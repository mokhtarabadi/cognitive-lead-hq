# Task 0355: Graph coverage honesty and search ergonomics

**File:** `tasks/completed/0355-graph-coverage-and-search-ergonomics.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-10-27T06:51:25Z
**Submitted:** 2026-10-27T06:35:02Z
**Estimate:** 3h
**Deadline:** 2026-10-28
**Started:** 2026-10-27T06:23:40Z

## Goal

Make the lite graph find things reliably: index recent work instead of truncating it silently, report coverage on every surface, accept the IDs it prints, rank exact symbols above prose, return signatures inline, and stop the code-search skill from describing tool contracts that do not exist.

## Manager's Notes

> now start smoke test our graph and $code-search skill, it comperhensive ? to easy find a things? or can make it even better? why?

> fix all in one task.

## Smoke-test evidence (2026-10-27)

- Build: 4.24s, 5000 nodes exactly (node cap), 7387 edges, 345 of 587 indexable files (59%).
- Missing 243 files: `tasks/` 190, `.opencode/memory` 31, `services/` 7. Recent task files 0352-0354 absent while archive 233 present, because docs are ordered by `(depth, path)` and truncated at 300.
- `explain_node` and `shortest_path` reject the `sym:...#...` IDs that `query_graph` prints; only bare labels work.
- `extract_signatures` returns only a report path (no inline text), has no directory mode, and returns nothing for Markdown/HTML, which is 521 of 609 tracked files. The skill simultaneously says to prefer signatures and never to read generated reports.
- `god_nodes` returns `output` and `system-prompt` from inline JS in `tools/prompt-composer/index.html`, plus three bare `main`s from different files.
- `query_graph` ranks prose sections over the actual symbol for natural queries; `get_directory_tree` dumps 28.6 KB at the repo root with no depth control.

## Local TODOs

- [x] Graph: caps, filters, recency ordering, coverage metadata, ID lookup, seed weighting
- [x] Tools: stats/query coverage lines, staleness, god-node hygiene, tree depth, inline signatures
- [x] Tests for each behaviour
- [x] Docs: context-server README + ADR, CHANGELOG, code-search skill (repo + global)
- [x] Suite and task lint

## Acceptance Criteria

- [x] `build_graph` orders task docs by lane and newest id first, takes `include`/`exclude` globs and cap overrides, and saves coverage metadata (scanned/indexed files and docs, caps, truncation reasons, build time).
- [x] Default caps index this repository fully (no silent 41% loss).
- [x] `graph_stats` prints coverage, caps, truncation reasons and a staleness verdict.
- [x] `query_graph` prints a one-line coverage caveat when the graph is truncated and scores symbols above files above sections on equal overlap.
- [x] `explain_node` and `shortest_path` resolve `sym:`/`file:`/`sec:` IDs exactly as printed.
- [x] `god_nodes` qualifies each label with its file, drops generic names, and never shows two identical bare labels.
- [x] `extract_signatures` accepts a file or a directory, returns the signatures inline (capped) alongside the report path, and says so for Markdown/HTML.
- [x] `get_directory_tree` and `create_tree_report` expose `max_depth` and `max_entries`.
- [x] `skill-templates/code-search/SKILL.md` and the global copy describe the real contracts and add a graph-first decision table and a coverage check.
- [x] Context-server README, DECISIONS ADR, CHANGELOG updated; suite and `lint_task_file` green.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/ -q`
- **Expected result:** full suite green including the new graph and signature tests
- **Actual result:** seven new tests pass (`test_graph_indexes_recent_tasks_and_reports_coverage`, `test_graph_resolves_printed_ids_and_qualifies_god_nodes`, `test_query_graph_prefers_symbols_over_sections`, `test_graph_stats_reports_stale_sources`, `test_graph_cap_overrides_and_include_filter`, `test_extract_signatures_inline_and_directory`, `test_directory_tree_depth_is_bounded`); full suite `745 passed in 53.07s`, exit 0. Live rebuild on this repo: `7581 nodes, 11741 links in 2.61s`, `Coverage: 49/49 files, 522/522 docs (complete)`; `explain_node("sym:mcp-lint-server/server.py#_resolve_task_reference")` resolves; the "never trim brain results" query seeds on the new test and `tasks/completed/0354-...`; `extract_signatures("mcp-brain-bridge")` returns 5 files inline with no `.venv` contamination.
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** raising caps increases build time and graph size; measured, and caps stay overridable.
- **Risk:** changing the tree default depth alters output for existing callers; documented, and depth stays a parameter.
- **Risk:** inline signatures enlarge tool results; capped by `max_chars`.
- **Rollback:** restore the previous constants, signatures and tool signatures; graphs rebuild from source.

---

## Execution Log & Reasoning

**What the smoke test proved.** Three failures, not one. Coverage was partial and silent (345/587 files, node cap exactly 5000), and the missing set held the three most recent task files because docs sorted `(depth, path)`; the printed `sym:`/`sec:` IDs were rejected by the two tools that take endpoints; and the signature tool returned only a report path while the code-search skill forbade opening generated reports, so its "prefer signatures" step was a dead end. The rest was ergonomics: prose outranked symbols, god nodes carried generic JS identifiers, and the root tree dumped 28 KB.

**Seat Check.** Domains: graph engine and tool contracts, plus a skill rewrite. Whole-word trigger `index` fired in the task body → Software Architect. UI/UX Designer skipped (no user-visible surface), QA/Reviewer later stages. Brainstorm: not required — one component plus one skill, reversible, and the smoke test already fixed the scope.

**Planning gate.** The Manager's own order is the plan: the smoke-test findings define the seven fixes and "fix all in one task" authorises them. No separate Brain planning round.

**Implementation.** Caps 300/300/5000 → 600/600/12000, every one overridable by `include`/`exclude`/`max_*`. Task docs now sort lane-first and newest-id-first, which is what keeps 0354 in the graph after a cap hit. The build stores `scanned`, `indexed`, `caps`, `truncated`, `built_at` and the indexed source list in the graph envelope, so `graph_stats` and `query_graph` can print one honest coverage line and name a source modified after the build as `STALE`. `_find_graph_nodes` tries the exact ID first, then the exact label, which makes the printed IDs round-trip. Seeds score `overlap × kind weight` (symbol 3, file 2, section 1) with +50 for an exact match. `god_nodes` uses confidence-weighted degree and qualified labels, and the noise set gained `output`, `system-prompt`, `role`, `wrapper`. `extract_signatures` now takes a directory through `collect_files` (so `.gitignore` keeps `.venv` out — the first rglob attempt returned 200 venv files), returns text inline up to `max_chars`, and reports Markdown/HTML as unsupported. Trees take `max_depth` (default 3) and `max_entries`. The skill was rewritten around the graph-first flow with a tool-choice table.

**Live numbers after the change.** Build 2.61-3.31s, 7,581 nodes, 11,741 edges, 49/49 code files and 522/522 docs. The symbol/noise/ID/ranking fixes are visible in the query output quoted in the evidence above.

**Deployment.** Global `mcp-context-server` copies (`server.py`, `graph.py`) and the global `code-search` skill were synced with native writes; `cmp` verifies both. The running `mcp-context` singleton keeps the old build until the Manager restarts it.

**Assumptions.** A1: caps 600/600/12000 (covers this repo with headroom, still bounded). A2: tree depth default 3 (files under `mcp-*/` remain visible while deep doc trees stop dominating). A3: 200-file cap and 12,000-char inline cap for signatures.

**QA cycle 1 (Brain).** `QA_REJECTED` with two blocking defects and three test gaps. F1: the doc-file loop and the rationale link cap still compared against `GRAPH_MAX_NODES`, so a `max_nodes` override leaked on the doc path. F2: `STALE` only stats indexed sources, so a newly added file is invisible. Fixed: both guards now use `cap_nodes`, and overrides are clamped (files/docs 1–5000, nodes 1–200000) so a trusted caller cannot wedge the single-threaded server; the `STALE` scope is documented in the README invariant and the ADR. New test `test_graph_cap_overrides_and_include_filter` builds with `max_nodes=6` (asserted bound) and with `include=["a.py"]` (asserted single source).

**QA cycle 2 (Brain).** `QA_PASSED`. F1 verified closed at `graph.py:691/717/734` with both link caps on `cap_nodes * 2`; F2 accepted as documented limitation (README invariant, ADR). Non-blocking residue: the one-second `built_at` truncation window and the absence of a test for the documented `STALE` miss.

**Review cycle 1 (Brain).** `APPROVED_WITH_CHANGES`: one factual defect — the CHANGELOG said six new tests where seven exist — plus a low note that the tree default has no README line (reviewer asked to defer it to the next edit of that file, not a new task). Count corrected to seven; `tests/test_mcp_servers.py` re-ran 96 passed, exit 0.

**Review cycle 2 (Brain).** `APPROVED` / `PO_REVIEW_PENDING`, severity Low: count closed, no engine or test change in the confirmation round.

**Deployment.** `mcp-context-server/server.py`, `mcp-context-server/graph.py` and `skill-templates/code-search/SKILL.md` were copied to the global install and `cmp` reports all three byte-identical. The running `mcp-context` singleton needs a restart to load the new build; restarting a singleton unit needs the Manager's order.

**Manager closure approval (2026-10-27):** "Approved for closure" via the question tool, answering the relayed PO_REVIEW_PENDING verdict. ZAC holds; closure runs only through `custom_context_commit_and_clean_task`.

**Closure:** preconditions verified, file moved with `git mv` to the completed lane, `**Status:** closed` and the `**File:**` header synced.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3654a426adcc4bb9961bffb9e407ce7187829e07`
<!-- END_GIT_DIFF -->
