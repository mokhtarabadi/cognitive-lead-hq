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

## Discovery Workflow (hybrid graph-vector, comment-aware, archive-aware)

0. **Memory before map.** Load the `project-memory` skill and check `.opencode/memory/index.md`, then `search_memory` for the domain. Standing constraints decide which files matter.

1. **Archive-aware graph build.** Build once per session with `custom_context_build_graph` (caps 600 files / 600 docs / 12000 nodes; task docs are lane-ordered so archive never hides active work). Rebuild when the coverage line says `truncated` or `STALE`; include `tasks/archive` explicitly when the question is about history. Archive is lane 4, not invisible.

2. **Map the structure.** `custom_context_get_directory_tree` on the target (`.` for repo, depth 3 / 2000 entries; pass `max_depth`/`max_entries` for deeper). `custom_context_create_tree_report` only when Manager asks for a saved tree.

3. **Graph-vector hybrid.** Deterministic `custom_context_query_graph` (`bfs` 2-hop for "what connects to X", `dfs` 6-chain for "how X reaches Y"; `graph_path` to pin a build) + tiny `mcp-context-server/vector.py` fastembed `BAAI/bge-small-en-v1.5` 384-d 512/50 Chroma `hq_docs_tasks_comments` (`_CHUNK_TOKENS` 512 plus `_CHUNK_OVERLAP` 50 plus `_MAX_CHUNKS_TOTAL` 2000) fused via RRF k=60 between `scored.sort` and `seeds` in `mcp-context-server/server.py` (`_VEC_MODEL` cached, 30 cap). Comment nodes in `mcp-context-server/graph.py` (`comment` kind, 80/50 caps, extension-gated) are graph nodes, not dropped text. Other graph tools: `explain_node` (ID or label), `shortest_path`, `god_nodes`, `graph_stats`.

4. **Verify every hit.** `explain_node` → `file:line`; quote it. Read at most the 2–3 files the graph pointed at.

5. **Extract signatures only for structural breadth.** `custom_context_extract_signatures` on a file or directory (inline, cap 12000, plus report path).

6. **Halt and hand over.** Autopilot: `brain_turn(context_paths:[<report path>])`. Manual: Manager hand-off. Full reads via `custom_context_read_source_files` only after steps 2–5; native `read` bounded 2000 lines / 50 KiB, page with `offset`/`limit`.

## Parallel Discovery

- Split independent scopes (e.g. one subagent per MCP server, one per feature slice) across up to four `subagent` calls.
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
- **Freshness:** `graph_stats` names the first source modified after the build (`STALE: ...`), plus node/edge counts, schema version, and the `EXTRACTED/INFERRED/AMBIGUOUS` edge split. Rebuild rather than reusing a stale graph. A grant restore that rewrites task files also makes the graph `STALE` — rebuild before trusting a miss.
- **God nodes** are qualified as `name — path (weighted degree N)` and skip generic identifiers; two same-named functions in different files are distinguishable.

## Signature Contract

- One file or a directory (recursive, `.gitignore`-aware, up to 200 matching files).
- Returns the extracted text inline, capped by `max_chars` (default 12000), plus the report path.
- Tree-sitter AST for Python, JavaScript, TypeScript, Go, Java, Rust, Kotlin; regex fallback for others. The graph indexes SQL table declarations and foreign-key `REFERENCES` relationships; SQL files are graph-searchable even when signature extraction is limited.
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
2. `build_graph` on that directory (scoped graph via `target_path`), or `query_graph` against the repo graph with the slice words, then `explain_node` for its entry points. Scoped graphs dedupe same-basename files across packages — prefer printed IDs over bare labels.
3. `extract_signatures` on the slice for the structural surface.
4. Trace local imports into shared packages and include their signatures.
5. Append `AGENTS.md`, `DESIGN.md`, and `docs/*.md` to the final report — mandatory core context.

## Why This Order Matters

Full-repo scans waste tokens and dilute signal. The graph answers "where" from an index that already carries file:line; signatures answer "what shape" without bodies; full reads answer "what exactly" for the few files that remain. Skipping straight to reads costs the most and grounds the Orchestrator least.
