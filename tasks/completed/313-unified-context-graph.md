# Task 313: unified context graph

**File:** `tasks/completed/313-unified-context-graph.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Supersedes:** [308, 309, 310, 311, 312]
**Meta:** true
**Created:** 2026-10-09 09:11 UTC
**Bundled:** 5 tasks

## Goal

Unified execution of 5 related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks [308, 309, 310, 311, 312] — "unified context graph" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.

> ⚠️ **Guardrail Warning:** Combined source size is 17151 LOC (> 400). Unified META diff may be large and hard to review. Consider splitting into two METAs.

**Source IDs:** [308, 309, 310, 311, 312]
**Next ID:** 313 (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)
**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: 313-unified-context-graph` and remain reachable via `git log --follow` (never purged until META is completed).

## Manager's Notes

**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute 5 small related tasks together and speed up turnaround.

**Traceability:**
- Supersedes [308, 309, 310, 311, 312] — see per-source verbatim blocks below
- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** 313-unified-context-graph` header + superseded footer
- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file

**Guardrails Applied:**
- Cap 6 per bundle — this bundle has 5 (✅ within cap)
- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)
- Diff-size check — combined 17151 LOC (⚠️ exceeds 400 — consider split)

## Source Bundles (Verbatim Preservation)

The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.

### Source Task 308: Context MCP Lite Graph Upgrade from Graphify

**Original File:** `/home/mohammad/Develop/Projects/cognitive-lead-hq/tasks/qa/308-context-mcp-lite-graph-upgrade.md` → `tasks/archive/308-context-mcp-lite-graph-upgrade.md` (after bundling)

**Title:** Context MCP Lite Graph Upgrade from Graphify

#### Goal (verbatim)

Add lite knowledge-graph capability to mcp-context-server inspired by Graphify: persist graph.json plus query/path/explain tools and god-node ranking, while keeping current tree/read/signatures behavior unchanged.

#### Manager's Notes (verbatim)

Manager approved scope Lite graph upgrade on 2026-10-09 via question tool. Docs-only rejected. Full port rejected. Create tracked task file in tasks/backlog. Plan approved: 1) map gap, 2) draft doc plus small graph prototype design, 3) implement behind verification gates. Reference: Graphify-Labs/graphify knowledge graph with local AST parsing, EXTRACTED/INFERRED edges, query/path/explain, god nodes and communities.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

#### Acceptance Criteria (verbatim)

- [x] AC1: Gap map records current tree/read/signatures versus Graphify graph/query/path/explain
- [x] AC2: graph.json schema versioned and persisted under context-reports or graphify-out equivalent
- [x] AC3: New query/path/explain tools return scoped subgraphs without breaking existing tools
- [x] AC4: God-node ranking lists most-connected concepts with EXTRACTED versus INFERRED tags
- [x] AC5: README and DECISIONS updated in same change per Living Folder Docs standard
- [x] AC6: lint_task_file passes and existing server tests pass

#### Local TODOs (verbatim)

- [x] Map gap between mcp-context-server and Graphify concepts
- [x] Design graph.json schema plus query/path/explain tool contracts
- [x] Prototype god-node ranking and cross-file edges
- [x] Update README and DECISIONS for mcp-context-server
- [x] Verify with lint and server tests

#### Risk & Rollback (verbatim)

- **Risk:** Graph build cost grows on large repos and breaks single-threaded MCP server
- **Rollback plan:** Revert server.py and docs to prior commit, keep existing tree/read/signatures tools

---

### Source Task 309: Unified Graph over Code, SQL, Markdown, and Docs

**Original File:** `/home/mohammad/Develop/Projects/cognitive-lead-hq/tasks/qa/309-unified-graph-code-sql-markdown-docs.md` → `tasks/archive/309-unified-graph-code-sql-markdown-docs.md` (after bundling)

**Title:** Unified Graph over Code, SQL, Markdown, and Docs

#### Goal (verbatim)

Extend the lite knowledge-graph to one unified graph covering all code (including SQL), Markdown files, and living docs (README, DECISIONS): doc file + section nodes, doc-to-doc reference edges, doc-to-symbol and symbol visibility links, SQL table nodes, and a tokenizer that matches natural words to snake_case/camelCase symbols — so one query traces any feature end-to-end across backend, clients, docs, skills, prompts, and MCP servers.

#### Manager's Notes (verbatim)

Manager goal expansion 2026-10-09: single unified graph over everything. Example flow: ask about a feature and the graph shows backend implementation, sub-features, client mapping, and doc mapping. Concrete acceptance: define/modify a decision entry and the graph reveals every related component (Markdown assets, prompt system, skills, MCP servers); verify with tests; deploy global, restart service, test live. Builds on the staged task 308 code graph (still in QA); this task carries only the incremental diff but stages cumulatively until 308 closes.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

#### Acceptance Criteria (verbatim)

- [x] AC1: build_graph over repo root yields document nodes and section nodes alongside code nodes
- [x] AC2: Markdown links ([text](./other.md), [[wikilinks]]) become references edges between docs
- [x] AC3: Doc files link to code symbols they mention (INFERRED) and SQL tables are extracted
- [x] AC4: Natural-word query (e.g. stage diff workflow) matches snake_case symbols
- [x] AC5: graph_stats reports schema 2 with document counts and new relations
- [x] AC6: Decision demo: editing a DECISIONS entry surfaces it plus related components via query/explain/path
- [x] AC7: lint_task_file passes, graph tests pass, prompt sync in sync

#### Local TODOs (verbatim)

- [x] Index Markdown: file + heading-section nodes, md-link references edges
- [x] Link docs to code symbols (references INFERRED) both directions where cheap
- [x] Index SQL: CREATE TABLE/VIEW nodes plus REFERENCES edges
- [x] Fix tokenizer: split snake_case and camelCase for natural-word queries
- [x] Bump graph schema to 2 and update report counts
- [x] Extend tests with md/sql fixtures and pass them
- [x] Update README/DECISIONS/skills/prompts/agents plus system prompt rebuild
- [x] Deploy global, restart service, run end-to-end decision demo live

#### Risk & Rollback (verbatim)

- **Risk:** 459 Markdown files bloat the graph past node caps and slow single-threaded builds
- **Rollback plan:** Revert server.py graph block to schema 1 code-only; docs drop out, code graph unchanged

---

### Source Task 310: Client and UI Coverage in the Unified Graph

**Original File:** `/home/mohammad/Develop/Projects/cognitive-lead-hq/tasks/qa/310-client-ui-graph-coverage.md` → `tasks/archive/310-client-ui-graph-coverage.md` (after bundling)

**Title:** Client and UI Coverage in the Unified Graph

#### Goal (verbatim)

Extend the unified graph to client-side and UI code so one feature query (e.g. signup/registration) resolves end-to-end: decision logic, Markdown docs, backend code, and every client — HTML, Vue, React, Android (Kotlin plus XML layouts), iOS (Swift), Dart, and other XML — with all of it inferable from the graph.

#### Manager's Notes (verbatim)

Manager order 2026-10-09: for a feature such as registration the graph must show where its decision logic lives, where its docs and descriptions are, where backend code is, and where each client and frontend implementation is. Implement, test, deploy global, restart, live-demo. Builds on staged tasks 308 and 309 (both in QA); this task stages cumulatively until they close.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

#### Acceptance Criteria (verbatim)

- [x] AC1: Kotlin fun/class/object, Swift func/class/struct, Java methods, Dart classes become symbol nodes
- [x] AC2: Vue script functions, HTML/XML element ids (incl. android:id) become nodes
- [x] AC3: Kotlin/Java/Swift imports resolve to imports edges like Python/JS/Go
- [x] AC4: Natural query signup matches backend fun, Android Activity, XML ids, Vue component, Swift func, and docs
- [x] AC5: explain_node on a client id shows its file plus cross-stack connections
- [x] AC6: lint_task_file passes, graph tests pass

#### Local TODOs (verbatim)

- [x] Extract Kotlin/Swift/Java/Dart symbols (fun/func/class/object/struct/protocol)
- [x] Extract Vue/Svelte/HTML/XML nodes (script symbols, element/android ids)
- [x] Parse Kotlin/Java/Swift imports into imports edges
- [x] Cover lookup so element ids and components resolve in references
- [x] Extend tests with client fixtures and pass them
- [x] Update README/DECISIONS plus CHANGELOG
- [x] Deploy global, restart, live signup-style demo on a /tmp fixture stack
- [x] Verify discovery flow prefers graph before raw reads (no prompt change needed)

#### Risk & Rollback (verbatim)

- **Risk:** Regex method extraction in Java/Dart over-matches (loops, calls) and pollutes the graph
- **Rollback plan:** Revert extractor patterns to schema-2 set; client files fall back to file-only nodes

---

### Source Task 311: Full Stack Coverage — React Arrows, Prisma, ObjC, Config

**Original File:** `/home/mohammad/Develop/Projects/cognitive-lead-hq/tasks/in-progress/311-stack-coverage-arrows-prisma-objc-config.md` → `tasks/archive/311-stack-coverage-arrows-prisma-objc-config.md` (after bundling)

**Title:** Full Stack Coverage — React Arrows, Prisma, ObjC, Config

#### Goal (verbatim)

Close the four proven extractor gaps so every skill-template stack resolves in the graph: React arrow components in JS/TS files, Prisma models/enums, Objective-C methods, and config/style assets (properties, CSS) — verified by probe-first tests plus a live deploy check.

#### Manager's Notes (verbatim)

Manager probe 2026-10-09 proved: `const SignupForm = () =>` missed in TSX, ObjC methods missed, `.prisma`/`.properties`/`.css` invisible. Order: fix and test. QA lane holds 308/309/310 (at cap 3): this task stages in-progress and waits — 308 must close before the 311 QA transition. Builds cumulatively on staged work until prior tasks close.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

#### Acceptance Criteria (verbatim)

- [x] AC1: Arrow function components extract in .js/.jsx/.ts/.tsx
- [x] AC2: Prisma models/enums and ObjC methods extract with correct kinds
- [x] AC3: properties keys and CSS selectors become nodes; files are collected
- [x] AC4: Interface/type/alias nodes carry correct kinds, not func
- [x] AC5: lint_task_file passes, graph tests pass

#### Local TODOs (verbatim)

- [x] Arrow components in all JS/TS suffixes plus correct interface/type/enum kinds
- [x] Prisma .prisma models/enums plus .m/.mm ObjC methods
- [x] Collect .properties/.css (.scss/.less) with key/selector nodes
- [x] Probe-backed tests for each gap and pass them
- [x] Deploy global, restart, live verify on the probe stack
- [x] Stage 311 and hold QA until 308 closes

#### Risk & Rollback (verbatim)

- **Risk:** Looser patterns over-match (CSS braces, ObjC C functions) and add noise nodes
- **Rollback plan:** Revert new patterns; affected suffixes return to prior behavior

---

### Source Task 312: Graph Precision Round from Graphify Re-read

**Original File:** `/home/mohammad/Develop/Projects/cognitive-lead-hq/tasks/in-progress/312-graph-precision-from-graphify-reread.md` → `tasks/archive/312-graph-precision-from-graphify-reread.md` (after bundling)

**Title:** Graph Precision Round from Graphify Re-read

#### Goal (verbatim)

Raise context-graph precision with six Graphify learnings: full-file symbol scan (drop the silent 2000-line head), vocabulary hints on zero-hit queries, DFS traversal mode, rationale links from Task/ADR mentions in code, god-node noise filtering, and an explicit truncation note.

#### Manager's Notes (verbatim)

Manager re-read order 2026-10-09 (Persian): re-check Graphify source for learnings, judge goal closeness. Live proof found `def qa_transition` (server.py:2025) missing from the graph — the `[:2000]` head cuts big files. Approved: implement as 312. QA lane holds 308/309/310 (at cap): stage in-progress, no fourth QA entry until 308 closes. Cumulative staging until priors close.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

#### Acceptance Criteria (verbatim)

- [x] AC1: Symbols past line 2000 extract (qa_transition present with L2025)
- [x] AC2: Zero-hit query names closest vocabulary tokens instead of only Try wider
- [x] AC3: query_graph DFS mode traces chains up to depth 6
- [x] AC4: Task/ADR mentions in code become INFERRED rationale links
- [x] AC5: god_nodes hides dunder and trivial helper noise
- [x] AC6: lint_task_file passes, graph tests pass
- [x] AC7: Registry exposes exactly the 14 intended tools, no helpers

#### Local TODOs (verbatim)

- [x] Scan full files for symbols (remove 2000-line head, keep per-file cap)
- [x] Suggest closest vocabulary tokens on zero-hit queries
- [x] Add DFS mode to query_graph alongside BFS
- [x] Link Task NNN and ADR-NNN code mentions to task files and decision sections
- [x] Filter noise (dunders, run/json/post/data) from god_nodes
- [x] Mark query output truncation explicitly
- [x] Tests plus live verify that qa_transition resolves
- [x] Keep helpers out of the MCP registry (decorator placement) plus test

#### Risk & Rollback (verbatim)

- **Risk:** Full-file scans slow builds on huge generated files
- **Rollback plan:** Restore the 2000-line head and drop new query options

---


## Bundled Checklist (All-or-Nothing)

> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.

- [ ] [308] AC1: Gap map records current tree/read/signatures versus Graphify graph/query/path/explain
- [ ] [308] AC2: graph.json schema versioned and persisted under context-reports or graphify-out equivalent
- [ ] [308] AC3: New query/path/explain tools return scoped subgraphs without breaking existing tools
- [ ] [308] AC4: God-node ranking lists most-connected concepts with EXTRACTED versus INFERRED tags
- [ ] [308] AC5: README and DECISIONS updated in same change per Living Folder Docs standard
- [ ] [308] AC6: lint_task_file passes and existing server tests pass
- [ ] [309] AC1: build_graph over repo root yields document nodes and section nodes alongside code nodes
- [ ] [309] AC2: Markdown links ([text](./other.md), [[wikilinks]]) become references edges between docs
- [ ] [309] AC3: Doc files link to code symbols they mention (INFERRED) and SQL tables are extracted
- [ ] [309] AC4: Natural-word query (e.g. stage diff workflow) matches snake_case symbols
- [ ] [309] AC5: graph_stats reports schema 2 with document counts and new relations
- [ ] [309] AC6: Decision demo: editing a DECISIONS entry surfaces it plus related components via query/explain/path
- [ ] [309] AC7: lint_task_file passes, graph tests pass, prompt sync in sync
- [ ] [310] AC1: Kotlin fun/class/object, Swift func/class/struct, Java methods, Dart classes become symbol nodes
- [ ] [310] AC2: Vue script functions, HTML/XML element ids (incl. android:id) become nodes
- [ ] [310] AC3: Kotlin/Java/Swift imports resolve to imports edges like Python/JS/Go
- [ ] [310] AC4: Natural query signup matches backend fun, Android Activity, XML ids, Vue component, Swift func, and docs
- [ ] [310] AC5: explain_node on a client id shows its file plus cross-stack connections
- [ ] [310] AC6: lint_task_file passes, graph tests pass
- [ ] [311] AC1: Arrow function components extract in .js/.jsx/.ts/.tsx
- [ ] [311] AC2: Prisma models/enums and ObjC methods extract with correct kinds
- [ ] [311] AC3: properties keys and CSS selectors become nodes; files are collected
- [ ] [311] AC4: Interface/type/alias nodes carry correct kinds, not func
- [ ] [311] AC5: lint_task_file passes, graph tests pass
- [ ] [312] AC1: Symbols past line 2000 extract (qa_transition present with L2025)
- [ ] [312] AC2: Zero-hit query names closest vocabulary tokens instead of only Try wider
- [ ] [312] AC3: query_graph DFS mode traces chains up to depth 6
- [ ] [312] AC4: Task/ADR mentions in code become INFERRED rationale links
- [ ] [312] AC5: god_nodes hides dunder and trivial helper noise
- [ ] [312] AC6: lint_task_file passes, graph tests pass
- [ ] [312] AC7: Registry exposes exactly the 14 intended tools, no helpers
- [ ] Traceability: All 5 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Local TODOs

- [ ] Step 1: Validate META bundle — confirm all 5 source requirements are captured verbatim below
- [ ] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)
- [ ] [308] Map gap between mcp-context-server and Graphify concepts
- [ ] [308] Design graph.json schema plus query/path/explain tool contracts
- [ ] [308] Prototype god-node ranking and cross-file edges
- [ ] [308] Update README and DECISIONS for mcp-context-server
- [ ] [308] Verify with lint and server tests
- [ ] [309] Index Markdown: file + heading-section nodes, md-link references edges
- [ ] [309] Link docs to code symbols (references INFERRED) both directions where cheap
- [ ] [309] Index SQL: CREATE TABLE/VIEW nodes plus REFERENCES edges
- [ ] [309] Fix tokenizer: split snake_case and camelCase for natural-word queries
- [ ] [309] Bump graph schema to 2 and update report counts
- [ ] [309] Extend tests with md/sql fixtures and pass them
- [ ] [309] Update README/DECISIONS/skills/prompts/agents plus system prompt rebuild
- [ ] [309] Deploy global, restart service, run end-to-end decision demo live
- [ ] [310] Extract Kotlin/Swift/Java/Dart symbols (fun/func/class/object/struct/protocol)
- [ ] [310] Extract Vue/Svelte/HTML/XML nodes (script symbols, element/android ids)
- [ ] [310] Parse Kotlin/Java/Swift imports into imports edges
- [ ] [310] Cover lookup so element ids and components resolve in references
- [ ] [310] Extend tests with client fixtures and pass them
- [ ] [310] Update README/DECISIONS plus CHANGELOG
- [ ] [310] Deploy global, restart, live signup-style demo on a /tmp fixture stack
- [ ] [310] Verify discovery flow prefers graph before raw reads (no prompt change needed)
- [ ] [311] Arrow components in all JS/TS suffixes plus correct interface/type/enum kinds
- [ ] [311] Prisma .prisma models/enums plus .m/.mm ObjC methods
- [ ] [311] Collect .properties/.css (.scss/.less) with key/selector nodes
- [ ] [311] Probe-backed tests for each gap and pass them
- [ ] [311] Deploy global, restart, live verify on the probe stack
- [ ] [311] Stage 311 and hold QA until 308 closes
- [ ] [312] Scan full files for symbols (remove 2000-line head, keep per-file cap)
- [ ] [312] Suggest closest vocabulary tokens on zero-hit queries
- [ ] [312] Add DFS mode to query_graph alongside BFS
- [ ] [312] Link Task NNN and ADR-NNN code mentions to task files and decision sections
- [ ] [312] Filter noise (dunders, run/json/post/data) from god_nodes
- [ ] [312] Mark query output truncation explicitly
- [ ] [312] Tests plus live verify that qa_transition resolves
- [ ] [312] Keep helpers out of the MCP registry (decorator placement) plus test
- [ ] Step 38: Verify all bundled checklist items and run lint_task_file + verification-before-completion
- [ ] Step 39: Update CHANGELOG.md and record Verification Evidence

## Acceptance Criteria

- [ ] [308] AC1: Gap map records current tree/read/signatures versus Graphify graph/query/path/explain
- [ ] [308] AC2: graph.json schema versioned and persisted under context-reports or graphify-out equivalent
- [ ] [308] AC3: New query/path/explain tools return scoped subgraphs without breaking existing tools
- [ ] [308] AC4: God-node ranking lists most-connected concepts with EXTRACTED versus INFERRED tags
- [ ] [308] AC5: README and DECISIONS updated in same change per Living Folder Docs standard
- [ ] [308] AC6: lint_task_file passes and existing server tests pass
- [ ] [309] AC1: build_graph over repo root yields document nodes and section nodes alongside code nodes
- [ ] [309] AC2: Markdown links ([text](./other.md), [[wikilinks]]) become references edges between docs
- [ ] [309] AC3: Doc files link to code symbols they mention (INFERRED) and SQL tables are extracted
- [ ] [309] AC4: Natural-word query (e.g. stage diff workflow) matches snake_case symbols
- [ ] [309] AC5: graph_stats reports schema 2 with document counts and new relations
- [ ] [309] AC6: Decision demo: editing a DECISIONS entry surfaces it plus related components via query/explain/path
- [ ] [309] AC7: lint_task_file passes, graph tests pass, prompt sync in sync
- [ ] [310] AC1: Kotlin fun/class/object, Swift func/class/struct, Java methods, Dart classes become symbol nodes
- [ ] [310] AC2: Vue script functions, HTML/XML element ids (incl. android:id) become nodes
- [ ] [310] AC3: Kotlin/Java/Swift imports resolve to imports edges like Python/JS/Go
- [ ] [310] AC4: Natural query signup matches backend fun, Android Activity, XML ids, Vue component, Swift func, and docs
- [ ] [310] AC5: explain_node on a client id shows its file plus cross-stack connections
- [ ] [310] AC6: lint_task_file passes, graph tests pass
- [ ] [311] AC1: Arrow function components extract in .js/.jsx/.ts/.tsx
- [ ] [311] AC2: Prisma models/enums and ObjC methods extract with correct kinds
- [ ] [311] AC3: properties keys and CSS selectors become nodes; files are collected
- [ ] [311] AC4: Interface/type/alias nodes carry correct kinds, not func
- [ ] [311] AC5: lint_task_file passes, graph tests pass
- [ ] [312] AC1: Symbols past line 2000 extract (qa_transition present with L2025)
- [ ] [312] AC2: Zero-hit query names closest vocabulary tokens instead of only Try wider
- [ ] [312] AC3: query_graph DFS mode traces chains up to depth 6
- [ ] [312] AC4: Task/ADR mentions in code become INFERRED rationale links
- [ ] [312] AC5: god_nodes hides dunder and trivial helper noise
- [ ] [312] AC6: lint_task_file passes, graph tests pass
- [ ] [312] AC7: Registry exposes exactly the 14 intended tools, no helpers
- [ ] Traceability: All 5 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Verification Evidence

- **Test command:** `lint_task_file` on META file; `git log --oneline --follow -- tasks/archive/<id>-*.md | head` for archived sources; project test suite if logic changed
- **Expected result:** META lint passes; all 5 sources in `tasks/archive/` with `superseded` status; single Factual Git Diff covers all bundled changes
- **Actual result:** _(Hands fill during execution)_
- **Exit code:** _(Hands fill)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.
- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.
- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.
- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded [308, 309, 310, 311, 312], remove Superseded-By footer, delete or archive `tasks/backlog/313-unified-context-graph.md` as abandoned. No HQ code beyond bundler is affected.

---

## Execution Log & Reasoning

Autopilot locked for META 313 per Manager order "start auto pilot for it" (2026-10-09). Mode: autopilot. Assumption A1: "8,9,10,11,12" means active tasks 308–312 (literal 8–12 live only in archive, rejected by bundler; dry-run validated the reading). Seat Check: backend Python graph work plus docs/skills/prompts — Architect kept (schema/taxonomy), Programmer kept, Designer skipped (no user surface). Brainstorm: not required — work complete, verification-only from here. Saga: build→bundle→stage→qa→Brain QA→fix→Brain review→stage→qa; never auto-commit, never close without exact approval words. Relay questions go to Manager verbatim; everything else decided from task file and Brain context.

Fix loop 1 (autopilot, QA_PASSED with follow-ups F1–F4, all reproduced): typed arrow annotations, graph-path workspace confinement, empty-label guard, 1MB scan cap, plus tests for each. Worktree diff hash after fix: 10497247f8658ee7948962880fbafcbaf2e42af555186a62e3c170b7dffa89fd (single attempt, no spin). Full suite: 74 passed + 6 pre-existing memory yaml failures.

PO_REVIEW_PENDING (autopilot relay, 2026-10-09): Brain Code Reviewer returned technical approval — all 32 bundled AC plus traceability map to code/docs/tests; 4 minor follow-ups logged (CSS id selectors, dead _graph_rel_posix helper, dual read caps, Java package-private methods) for a future task. File stays in tasks/qa/ awaiting the exact approval words.

Closure (2026-10-09): Approved for closure received verbatim via relay question; PO_REVIEW_PENDING on record; file verified in tasks/qa/; closure-only move to tasks/completed/ with Status closed. No code changes.

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3d5db016e31bc7660abff99de6a27d70cb316213`
<!-- END_GIT_DIFF -->
