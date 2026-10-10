# Architectural Decisions: mcp-context-server

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-09] ADR-002: Lite Knowledge-Graph (Graphify-inspired, stdlib-only)

- **Context:** Context reports were file dumps (trees/signatures/reads) with no cross-file links. Graphify shows queryable graphs beat grep; full port (Leiden, graspologic, networkx, HTML viz) is too heavy for the singleton MCP server.
- **Decision:** Add lite graph to `server.py`: `build_graph` (files + regex symbols, contains/imports EXTRACTED, references INFERRED), `query_graph` (token seeds + 2-hop), `explain_node`, `shortest_path` (BFS directed default), `god_nodes` (symbol degree rank), `graph_stats`; versioned `graph.json` (schema 1) + `graph_report_*.md` under `context-reports/`; fix `get_directory_tree` workspace-scoping bug (removed `Path(target_path)` overwrite).
- **Consequences:** Discovery/consumers prefer graph queries before raw reads; no new deps; caps keep single-threaded server safe.
- **Rollback:** Revert `server.py` graph block + docs; existing tree/read/signature tools unchanged.

## [2026-10-09] ADR-003: Unified Graph over Code, SQL, Markdown, Docs

- **Context:** Code-only graph could not answer feature questions end-to-end (backend, clients, docs, skills, prompts). Markdown corpus is 459 files; repo has zero SQL files but SQL support is required for target projects.
- **Decision:** Schema 2 in the same stdlib engine: Markdown file + heading-section nodes, `[text](./other.md)`/`[[wikilinks]]` as EXTRACTED references, doc-to-symbol INFERRED links (capped 40/doc), SQL CREATE TABLE/VIEW nodes with REFERENCES edges (dangling refs pruned), tokenizer splits snake_case/camelCase so natural words match symbols, undirected path renders `<--` on reverse hops.
- **Consequences:** One `build_graph` covers the stack; query/explain/path work across code and docs; caps hold (docs 300, 500 lines each, 60 sections each).
- **Rollback:** Revert graph block to schema 1 code-only; drop schema-2 tests.

## [2026-10-09] ADR-004: Client and UI Coverage in the Unified Graph

- **Context:** Feature queries (e.g. signup/registration) must resolve across backend, docs, and every client: Android Kotlin plus XML layouts, iOS Swift, Vue/React script symbols, HTML ids, Dart. Regex method patterns risk over-matching in Java/Dart.
- **Decision:** Extend the extractor by suffix family: Kotlin fun/class/object, Swift func plus class/struct/enum/protocol, Java methods/ctors with modifier guard, Dart members with keyword guard, Vue/Svelte/Astro/HTML script-block scan plus arrow components, HTML/XML element ids incl. android:id as view_id/element_id nodes; JVM dotted imports and Swift imports feed existing resolver (extended with .kt/.swift/.dart/.vue); R.id/getElementById uses and doc id-mentions link INFERRED; markup stays file_type code.
- **Consequences:** One query spans backend, mobile, frontend, markup, and docs; Java record types and section-level doc links remain gaps.
- **Rollback:** Revert extractor patterns; client files fall back to file-only nodes.

## [2026-10-09] ADR-005: Full Stack Coverage (Arrows, Prisma, ObjC, Config)

- **Context:** Probe of every skill-template stack family proved four gaps: React arrow components missed in JS/TS files, ObjC methods missed, `.prisma`/`.properties`/`.css` never collected, interface nodes mislabeled func.
- **Decision:** Arrow pattern runs in the generic JS/TS path with keyword-derived kinds (interface/enum/type/class/func); `.prisma` models/enums, ObjC `@implementation`/method patterns, `.properties` keys (config), `.css/.scss/.less` selectors (style); five new collected suffixes.
- **Consequences:** All thirteen stack skills resolve symbols; CSS stay edge-less style nodes and Java records stay unmatched (logged gaps).
- **Rollback:** Revert new patterns and suffixes; prior behavior returns.

## [2026-10-09] ADR-006: Precision Round (Full Scan, Vocab Hints, DFS, Rationale)

- **Context:** Live evaluation proved `def qa_transition` (server.py:2025) missing — the 2000-line head cuts big files. Graphify query.md adds vocab-constrained expansion, DFS mode, rationale nodes, noise filtering, budget notes.
- **Decision:** Full-file symbol scans (200/file cap bounds cost); zero-hit queries suggest closest vocabulary; query_graph gains mode bfs/dfs (depth 6); Task NNN/ADR-NNN code mentions become INFERRED rationale_for edges to task files/decision sections; god_nodes skips dunders plus run/json/post/data; truncation carries an explicit note.
- **Consequences:** No silent drops; dead ends guide vocabulary; rationale links bind code to prior decisions. Plain helpers must sit above `@_project_tool` — a decorator left above a helper silently registers it as a 15th tool (caught live via catalog change); registry test pins exactly 14 tools.
- **Rollback:** Restore the line head and drop new options.

## [2026-10-09] ADR-007: Context Server Modules plus Ruff Enforcement

- **Context:** server.py grew to 3189 lines single-file while the Brain side splits entrypoint plus stdlib-pure concern modules. No formatter was pinned (`formatter: true`); ruff/black absent from PATH.
- **Decision:** Mirror the brain layout: server.py owns the FastMCP app plus the 14 tool defs and re-exports everything (test/shim surface, monkeypatch-settable); fsutil, signatures, graph, gitops, bundle stay stdlib-pure with acyclic imports (graph→fsutil, bundle→gitops). Formatter is ruff 0.16.10 via pinned global install; opencode.json pins named map ruff-format on .py; ruff format applied repo-wide (13 files).
- **Consequences:** Same 14 tools, same behaviors, full suite green; global deploy copies all *.py.
- **Rollback:** Restore single server.py from git; remove new modules; revert opencode.json to `formatter: true`.

## [2026-10-10] ADR-009: Agent-Managed Unstage for Parallel Sessions (`unstage_files`)

- **Context:** `skip_add` covers the stage side, but an agent discovering foreign hunks in its staged diff had no MCP path to remove them — shell `git reset` works but bypasses tool governance, and `git add`/`commit`/`checkout` stay forbidden. Parallel tasks sharing files need a full agent-managed index round-trip.
- **Decision:** Add `unstage_files(files, project_root)` using `git restore --staged -- <files>`: index-only, worktree never touched, empty list rejected, reports remaining staged state. Canonical flow: `unstage_files` → hunk surgery (`git apply --cached`) → `stage_and_inject_diff(skip_add=True)`. Registry grows 14 → 15 tools; no new deps; systemd units unchanged (same entrypoint).
- **Consequences:** Agents isolate their own files without involving foreign ones; commit/checkout/push remain forbidden by construction and permission layer.
- **Rollback:** Remove the tool + tests; registry returns to 14.

## [2026-10-10] ADR-008: Index-Safe Staging Mode (`skip_add`)

- **Context:** `stage_and_inject_diff` ran bare `git add -- <files>` on every call, staging whole-file blobs and silently discarding hunk-level index surgery (`git apply --cached`) a parallel session performed on shared files (CHANGELOG.md, slice DECISIONS.md) — the staged diff, Brain-review block, and closure commit then carried foreign hunks (live reproduction in the linked issue).
- **Decision:** Add opt-in `skip_add: bool = False` to `stage_and_inject_diff`: when true, skip the `git add` step entirely and only extract + inject (caller owns the whole index, task file included). On the default path, snapshot `git diff --cached --name-only` for the listed files before adding and append a warning naming files with pre-existing staged state. Document the whole-file contract in the tool docstring. `qa_transition` shares the pattern but its `git mv` interplay is out of scope (follow-up).
- **Consequences:** Index-safe flows sequence hunk surgery before the call with `skip_add=True`; default callers get a loud warning instead of silent overwrite. Signature change is trailing-optional, fully backwards compatible.
- **Rollback:** Revert `server.py` + tests; redeploy singleton.
