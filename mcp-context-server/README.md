# Slice: mcp-context-server

## Duties

Custom-context MCP daemon: directory trees, source reads, signature extraction, lite knowledge-graph (build/query/explain/path/god-nodes/stats with versioned graph.json), diff staging/injection (`stage_and_inject_diff`), task commit/clean, and meta-task bundling (`bundle_tasks`).

## Files

- `server.py` — Daemon entrypoint (tree reports, source reads, signatures, lite graph, staging, bundling tools).
- `pyproject.toml` / `uv.lock` — Runtime deps (`pathspec`, `mcp[cli]`) and lockfile.

## Key Risks & Invariants

- ZAC enforcement point: staging goes through `stage_and_inject_diff`; never `git commit` directly.
- Path confinement: all scans stay inside project root; vendor dirs excluded.
- Bundle lifecycle (META + supersede/archive) is the only writer of `tasks/archive/` moves.
- Graph lite: stdlib-only deterministic build (files + symbols, contains/imports EXTRACTED, references INFERRED); caps files 300 / nodes 5000; reports under `context-reports/` (gitignored).
- Graph unified (schema 2): same engine plus Markdown docs (file + heading-section nodes, md-link/[[wiki]] references edges, doc-to-symbol INFERRED links), SQL tables/views with REFERENCES edges, natural-word tokenizer (snake_case/camelCase split); caps docs 300.
- Graph clients (310): Kotlin fun/class/object, Swift func/types, Java methods/ctors, Dart members, Vue/Svelte script symbols, HTML/XML element ids incl. android:id; JVM/Swift imports; R.id/getElementById and doc id-mention links.
- Graph stacks (311): arrow components in all JS/TS suffixes, Prisma models/enums, ObjC methods, properties keys, CSS selectors; correct interface/type/enum kinds.
- Graph precision (312): full-file scans, vocab hints, DFS mode, Task/ADR rationale links, god-node noise filter, truncation note.
