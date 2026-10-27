---
name: code-search
description: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
---

# Code Search & Discovery Strategy

You are the Executor. Your job is to extract codebase context so the Manager can upload it to the Orchestrator.

**CRITICAL GUARDRAIL:** You MUST NOT read, analyze, or process generated report files (`context-reports/*.md`) yourself. Inline tool output — graph query results, signature text, tree output — is yours to use; the files those tools write are hand-off artifacts only.

## Discovery Workflow

1. **Map the structure.** Call `custom_context_get_directory_tree` on the target (`.` for the repo). It defaults to depth 3 and 2000 entries; pass `max_depth`/`max_entries` when the area is deeper. Call `custom_context_create_tree_report` only when the Manager asks for a saved tree.

2. **Graph first.** For any question that names behaviour, a symbol, or "what connects to what", build once per session with `custom_context_build_graph` and then query it:
   - `custom_context_query_graph` — natural words ("plan approval question tool", "staged diff injection").
   - `custom_context_explain_node` — one exact symbol, file, section, or any ID the graph printed (`sym:path#name`, `sec:path#slug`).
   - `custom_context_shortest_path` — how two concepts connect (`undirected=True` when direction is unknown).
   - `custom_context_god_nodes` — the hubs everything flows through.
   - `custom_context_graph_stats` — coverage and freshness before you trust a miss.

3. **Read the coverage line.** Every graph answer now prints one, e.g. `Coverage: 512/587 files, 480/521 docs; ... complete` or `truncated: docs — absence here is not proof of absence`. If it says truncated or `STALE`, rebuild (optionally `include=[...]`) before concluding a symbol does not exist.

4. **Verify every hit.** `explain_node` gives `source_file` + `source_location`; quote that file:line in your report. Read at most the 2–3 files the graph actually pointed at.

5. **Extract signatures only for structural breadth.** `custom_context_extract_signatures` accepts a file **or a directory** and returns the signature text **inline** (plus a saved report path). Use it when you need the shape of a module or folder; do not read the report it writes.

6. **Full reads last.** `custom_context_read_source_files` compiles narrowed files into a report and returns its path. Use it only after steps 2–5 have narrowed the set.

7. **Halt and hand over.** Output exactly:
   > "✅ Discovery complete. I have compiled the context report here: `[INSERT_FILE_PATH]`.
   > **Manager:** Please upload this file to the Orchestrator for review."

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

## Vertical Slicing Strategy

When the Orchestrator asks for one feature module (e.g. `packages/billing/`, `src/features/auth/`):

1. `get_directory_tree` on that directory only.
2. `build_graph` on that directory (or `query_graph` against the repo graph with the slice words), then `explain_node` for its entry points.
3. `extract_signatures` on the slice for the structural surface.
4. Trace local imports into shared packages and include their signatures.
5. Append `AGENTS.md`, `DESIGN.md`, and `docs/*.md` to the final report — mandatory core context.

## Why This Order Matters

Full-repo scans waste tokens and dilute signal. The graph answers "where" from an index that already carries file:line; signatures answer "what shape" without bodies; full reads answer "what exactly" for the few files that remain. Skipping straight to reads costs the most and grounds the Orchestrator least.
