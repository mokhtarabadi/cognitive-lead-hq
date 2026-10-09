# Task 312: Graph Precision Round from Graphify Re-read

**File:** `tasks/in-progress/312-graph-precision-from-graphify-reread.md`
**Source:** manager
**Type:** feature
**Status:** in-progress

## Goal

Raise context-graph precision with six Graphify learnings: full-file symbol scan (drop the silent 2000-line head), vocabulary hints on zero-hit queries, DFS traversal mode, rationale links from Task/ADR mentions in code, god-node noise filtering, and an explicit truncation note.

## Manager's Notes

Manager re-read order 2026-10-09 (Persian): re-check Graphify source for learnings, judge goal closeness. Live proof found `def qa_transition` (server.py:2025) missing from the graph — the `[:2000]` head cuts big files. Approved: implement as 312. QA lane holds 308/309/310 (at cap): stage in-progress, no fourth QA entry until 308 closes. Cumulative staging until priors close.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Scan full files for symbols (remove 2000-line head, keep per-file cap)
- [x] Suggest closest vocabulary tokens on zero-hit queries
- [x] Add DFS mode to query_graph alongside BFS
- [x] Link Task NNN and ADR-NNN code mentions to task files and decision sections
- [x] Filter noise (dunders, run/json/post/data) from god_nodes
- [x] Mark query output truncation explicitly
- [x] Tests plus live verify that qa_transition resolves
- [x] Keep helpers out of the MCP registry (decorator placement) plus test

## Acceptance Criteria

- [x] AC1: Symbols past line 2000 extract (qa_transition present with L2025)
- [x] AC2: Zero-hit query names closest vocabulary tokens instead of only Try wider
- [x] AC3: query_graph DFS mode traces chains up to depth 6
- [x] AC4: Task/ADR mentions in code become INFERRED rationale links
- [x] AC5: god_nodes hides dunder and trivial helper noise
- [x] AC6: lint_task_file passes, graph tests pass
- [x] AC7: Registry exposes exactly the 14 intended tools, no helpers

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest pytest tests/test_mcp_servers.py -q -k graph
- **Expected result:** all 9 graph tests pass
- **Actual result:** 9 passed via RTK; full file 73 passed + 6 pre-existing memory yaml failures; lint_task_file passes
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Full-file scans slow builds on huge generated files
- **Rollback plan:** Restore the 2000-line head and drop new query options

---

## Execution Log & Reasoning

Seat Check: backend Python graph precision plus tests/docs → Architect kept (edge taxonomy), Programmer kept, Designer skipped. Brainstorm: not required — reversible. QA at cap: stage only until 308 closes.

Live on deployed singleton (2026-10-09): whole-repo build 4479 nodes / 6230 links in 1.47s with 68 rationale_for edges binding code to task files. Explain qa_transition resolves the real node (L2143, degree 8: DECISIONS.md, milestone history, five archived tasks). Catalog incident: a stray decorator exposed _graph_vocab as a 15th tool — fixed by helper placement plus a registry test pinning 14 tools; live catalog confirms 14.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
