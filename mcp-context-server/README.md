# Slice: mcp-context-server

## Duties

Custom-context MCP daemon: directory trees, source reads, signature extraction, lite knowledge-graph (build/query/explain/path/god-nodes/stats with versioned graph.json), diff staging/injection (`stage_and_inject_diff`), task commit/clean, and meta-task bundling (`bundle_tasks`).

## Files

- `server.py` — Entrypoint: FastMCP app, fallback framework, the 14 tool defs, `__main__`; re-exports every helper (test/shim surface).
- `fsutil.py` — Gitignore filtering, trees, source reads, report writes.
- `signatures.py` — Tree-sitter signature extraction with regex fallback.
- `graph.py` — Knowledge-graph constants, parsers, build and query primitives.
- `gitops.py` — Repo roots, commit gates, task discovery, archive patching.
- `bundle.py` — Meta-task content builder.
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
- Staging index-safety: `stage_and_inject_diff` stages whole-file blobs; `skip_add=True` skips `git add` and only extracts + injects for self-managed hunk-level index surgery; default path warns naming files with pre-existing staged hunks.
- Parallel isolation: `unstage_files` removes listed files from the index without touching the worktree — the agent-managed unstage path for shared-file parallel sessions (no commit, no checkout, no push; ZAC holds).
