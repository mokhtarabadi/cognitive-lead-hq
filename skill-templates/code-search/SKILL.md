---
name: code-search
description: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
---

# Code Search & Discovery Strategy

You are the Executor. Your job is to extract codebase context so the Orchestrator can reason from it. In automatic mode you feed the Brain directly through `brain_turn`; in manual mode you hand the report path to the Manager.

**CRITICAL GUARDRAIL:** You MUST NOT read, analyze, or process generated report files (`context-reports/*.md`) yourself. Inline tool output — graph query results, signature text, tree output — is yours to use; the files those tools write are hand-off artifacts only.

## Runtime Surfaces (OpenCode v2)

The same tools are reachable two ways; use whichever surface the session exposes:

- **Direct tools** — `custom_context_get_directory_tree`, `custom_context_build_graph`, `custom_context_query_graph`, and the rest, when the server is not in Code Mode.
- **Code Mode (`execute`)** — MCP servers are namespaced: `tools.custom_context.query_graph({ question, project_root })`. Inside the script call `search("graph")` (synchronous) to get exact tool paths and signatures before calling; never guess a path. `execute` has no filesystem, no imports, and no timers — every read goes through a tool.
- If a namespace is absent, the server is either `codemode: false` (use direct tools) or down (fall back to native `grep`/`glob`/`read` and say so in the report).

## Discovery Workflow

0. **Memory before map.** Load the `project-memory` skill and check `.opencode/memory/index.md`, then `search_memory` for the domain. Standing constraints decide which files matter.

1. **Map the structure.** Call `custom_context_get_directory_tree` on the target (`.` for the repo). It defaults to depth 3 and 2000 entries; pass `max_depth`/`max_entries` when the area is deeper. Call `custom_context_create_tree_report` only when the Manager asks for a saved tree.

2. **Graph first.** For any question that names behaviour, a symbol, or "what connects to what", build once per session with `custom_context_build_graph` and then query it. Rebuild when the coverage line says `truncated` or `STALE`, and build a scoped graph for a slice:
   - `custom_context_query_graph` — natural words ("plan approval question tool", "staged diff injection").
   - `custom_context_explain_node` — one exact symbol, file, section, or any ID the graph printed (`sym:path#name`, `sec:path#slug`).
   - `custom_context_shortest_path` — how two concepts connect (`undirected=True` when direction is unknown).
   - `custom_context_god_nodes` — the hubs everything flows through.
   - `custom_context_graph_stats` — coverage and freshness before you trust a miss.

3. **Read the coverage line.** Every graph answer now prints one, e.g. `Coverage: 512/587 files, 480/521 docs; ... complete` or `truncated: docs — absence here is not proof of absence`. If it says truncated or `STALE`, rebuild (optionally `include=[...]`) before concluding a symbol does not exist.

4. **Verify every hit.** `explain_node` gives `source_file` + `source_location`; quote that file:line in your report. Read at most the 2–3 files the graph actually pointed at.

5. **Extract signatures only for structural breadth.** `custom_context_extract_signatures` accepts a file **or a directory** and returns the signature text **inline** (plus a saved report path). Use it when you need the shape of a module or folder; do not read the report it writes.

6. **Full reads last.** `custom_context_read_source_files` compiles narrowed files into a report and returns its path. Use it only after steps 2–5 have narrowed the set. Native `read` is bounded (2000 lines / 50 KiB per page), so page large files with `offset`/`limit`.

7. **Halt and hand over.**
   - **Automatic mode (autopilot):** call `brain_turn` under the active `task_id` with `context_paths: [<report path>]` so the Brain reads the report directly. Never ask the Manager to ferry a file, and never paste the report body.
   - **Manual mode:** output exactly:
     > "✅ Discovery complete. I have compiled the context report here: `[INSERT_FILE_PATH]`.
     > **Manager:** Please upload this file to the Orchestrator for review."

## Parallel Discovery

- Split independent scopes (e.g. one subagent per MCP server, one per feature slice) across up to four `task`/subagent calls.
- Inside one `execute` script, run independent tool calls concurrently (`Promise.allSettled`) and return the composed result once.
- Serial scanning of unrelated directories is a performance bug, not thoroughness.

## Definition of Done (discovery)

- Every cited file path exists and the graph coverage line is not truncated, or the report states why it is.
- Each claim that matters carries `file:line` from `explain_node` or a read.
- At most 2–3 file bodies were read; the rest came from the graph or signatures.
- The hand-off artifact exists (or the automatic-mode `context_paths` call returned).

## Choosing the Right Tool

| Question | Tool |
| --- | --- |
| Where is X defined / what does it touch? | `explain_node` (label or printed ID) |
| What does this behaviour live in? | `query_graph` with the domain words |
| How do these two connect? | `shortest_path` |
| What is the hub in this area? | `god_nodes` |
| What is the shape of this module/folder? | `extract_signatures` (file or dir, inline) |
| What is the folder layout? | `get_directory_tree` (depth-bounded) |
| Exact literal / regex match | native `grep` |
| Exact file body | `read` on the 2–3 narrowed files, or `read_source_files` for a report |

## Graph Contracts

- **IDs are round-trippable.** `sym:path#name`, `sec:path#slug`, `file:path` all work in `explain_node` and `shortest_path`. Bare labels still work but can be ambiguous (`main` exists in several scripts); prefer the printed ID.
- **Build options:** `include`/`exclude` take glob lists on repo-relative paths; `max_files`, `max_docs`, `max_nodes` override the caps (600/600/12000 by default).
- **Recency bias:** task documents are indexed lane-first (in-progress, qa, backlog, completed, archive) and newest id first, so a cap never hides the work you just did.
- **Ranking:** symbol nodes outweigh files, files outweigh prose sections on equal overlap; an exact label match always wins.
- **Freshness:** `graph_stats` names the first source modified after the build (`STALE: ...`). Rebuild rather than reusing a stale graph.
- **God nodes** are qualified as `name — path (weighted degree N)` and skip generic identifiers; two same-named functions in different files are distinguishable.

## Signature Contract

- One file or a directory (recursive, `.gitignore`-aware, up to 200 matching files).
- Returns the extracted text inline, capped by `max_chars` (default 12000), plus the report path.
- Tree-sitter AST for Python, JavaScript, TypeScript, Go, Java, Rust, Kotlin; regex fallback for others.
- Markdown, HTML and JSON have no structural signatures: the tool says so explicitly instead of returning an empty success.
- Captures declarations and parameter lists; never bodies, comments, imports, or multi-line decorators.

## Failure Modes

| Symptom | Cause | Move |
| --- | --- | --- |
| Tool absent from the catalog | server is `codemode: false` or down | call the direct tool, or fall back to native `grep`/`glob`/`read` |
| Query returns nothing | coverage truncated or graph stale | read the coverage line, rebuild with `include` |
| `Ambiguous 'main'` | duplicate symbol names | pass the printed ID (`sym:path#name`) |
| Signature tool says none | Markdown/HTML/JSON has no declarations | read the file or query its sections |
| Tool returned only a report path | `read_source_files` works that way | autopilot: `brain_turn(context_paths=[...])`; manual: hand the path over |

## Vertical Slicing Strategy

When the Orchestrator asks for one feature module (e.g. `packages/billing/`, `src/features/auth/`):

1. `get_directory_tree` on that directory only.
2. `build_graph` on that directory (scoped graph), or `query_graph` against the repo graph with the slice words, then `explain_node` for its entry points.
3. `extract_signatures` on the slice for the structural surface.
4. Trace local imports into shared packages and include their signatures.
5. Append `AGENTS.md`, `DESIGN.md`, and `docs/*.md` to the final report — mandatory core context.

## Why This Order Matters

Full-repo scans waste tokens and dilute signal. The graph answers "where" from an index that already carries file:line; signatures answer "what shape" without bodies; full reads answer "what exactly" for the few files that remain. Skipping straight to reads costs the most and grounds the Orchestrator least.
