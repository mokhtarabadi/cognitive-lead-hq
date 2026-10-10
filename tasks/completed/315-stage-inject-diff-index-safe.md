# Task 315: stage_and_inject_diff index-safe mode for shared-file sessions

**File:** `tasks/completed/315-stage-inject-diff-index-safe.md`
**Source:** manager
**Type:** bugfix
**Status:** closed

## Goal

Fix `stage_and_inject_diff` clobbering selective index staging: add an opt-in `skip_add` mode that skips the `git add` step and only extracts + injects the staged diff, plus a pre-existing-staged-state warning on the default path. Resolves mokhtarabadi/cognitive-lead-hq#29.

## Manager's Notes

Manager order 2026-10-10: fix https://github.com/mokhtarabadi/cognitive-lead-hq/issues/29 — create a task and link and full autopilot mode fix it and close issue with comment. Session linked via `session.link` as issue #29. Autopilot LOCKED for this task. Issue body (verified via `gh issue view 29`): bare `git add -- <files>` discards hunk-level index surgery (`git apply --cached`) in shared files (CHANGELOG.md, DECISIONS.md); the F5 fix solved cross-file contamination but not same-file hunk overwrite. Suggested fix adopted: opt-in flag + warning + whole-file documentation. Scope: `stage_and_inject_diff` only; `qa_transition` shares the pattern but its `git mv` interplay is out of scope (logged as follow-up, no change).

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Add `skip_add` param to `stage_and_inject_diff` (skip step 1, extract + inject only)
- [x] Detect pre-existing staged hunks in listed files on default path and warn in return string
- [x] Document whole-file staging semantics + `skip_add` usage in tool docstring
- [x] Add regression tests (preserve / warn / default-unchanged)
- [x] Update sibling README.md + DECISIONS.md (Living Folder Docs) + CHANGELOG.md
- [x] Deploy to global singleton, restart unit, live-verify via MCP tools
- [x] Stage, QA-transition, Brain QA + review, close GitHub issue with comment

## Acceptance Criteria

- [x] AC1: `skip_add=True` skips `git add` entirely; staged index is byte-identical before/after; diff still extracted + injected
- [x] AC2: Default path (`skip_add=False`) with pre-existing staged hunks in listed files returns a warning naming those files
- [x] AC3: Tool docstring documents whole-file staging + `skip_add` contract
- [x] AC4: New regression tests pass; full `test_mcp_servers.py` shows no new failures
- [x] AC5: README.md + DECISIONS.md + CHANGELOG.md updated; `lint_task_file` passes
- [x] AC6: Global singleton redeployed + restarted; live `stage_and_inject_diff` smoke test green

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest pytest tests/test_mcp_servers.py -q -k stage
- **Expected result:** all 4 stage tests pass (1 existing + 3 new)
- **Actual result:** 4 passed via RTK; full file 78 passed + 6 pre-existing memory yaml failures (ModuleNotFoundError, unrelated baseline)
- **Exit code:** 0 (RTK run); full-file raw rerun exit 1 solely from the 6 known failures
- **Self-review round (Brain bridge unavailable this session — capability-blocked, substituted with adversarial diff review, logged):** re-read staged hunks; found + fixed warning noise (tool-managed task file named on repeat calls → filtered via path-identity set, covered by extended warn test); audited `None`/non-repo/exception edges (all preserve prior error-string behavior); registry unchanged (no new tool). Re-run: 4 stage tests pass, full file still 78+6 baseline. Live re-verify on restarted singleton: refined warning names only `shared.py`.

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest pytest tests/test_mcp_servers.py -q -k stage
- **Expected result:** all stage-related tests pass (new + existing)
- **Actual result:** TBD
- **Exit code:** TBD

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Signature change breaks existing callers/tests passing positional args (mitigated: trailing optional param, default False, fully backwards compatible)
- **Rollback plan:** `git checkout -- mcp-context-server/server.py tests/test_mcp_servers.py`; redeploy global singleton from HEAD

---

## Execution Log & Reasoning

Seat Check: backend Python MCP fix, no user-visible surface → Designer skipped; Architect kept (index-state contract touches Brain-review dataflow). Brainstorm: not required — single-domain fix, fully reversible, fix shape pre-approved by issue reporter. Autopilot LOCKED per Manager order 2026-10-10 ("full auto pilot mode"). Mode note: plan-approval pause skipped — fix shape is the issue's own suggested option verbatim (opt-in flag preferred), logged here as Assumption A1. ZAC holds; no commits without exact approval words (GitHub issue close explicitly authorized: "close issue with comment"). Absent files skipped per policy: DESIGN.md, docs/architecture.md, docs/data_model.md. Memory: index read; search_memory for staging found no prior ruling.

Live verification on redeployed singleton (2026-10-10, /tmp/opencode/stage-verify2): pre-existing staged v1 blob + dirty worktree v2. `skip_add=True` → index sha256 identical before/after, injected block contains staged v1 only, zero foreign worktree content. Default path → warning names shared.py. Assumption A2: shell `git commit`/`git add` ZAC-denied, so the live fixture used `git apply --cached` new-file staging (no HEAD) — equivalent index state for the test.

GitHub issue closed 2026-10-10: comment posted via `--body-file` (fix summary + usage), `gh issue close 29 --reason completed`, session re-linked as closed. Note: first comment attempt hit transient GraphQL EOF; retry succeeded. Task file remains in `tasks/qa/` — task closure needs the exact approval words.

Autopilot smoke round 2 (Manager order 2026-10-10, all 5 MCP units restarted, 8s settle): drift audit per memory workflow = zero drift everywhere (servers, agents, prompt, strategy, skills, no orphans); all units active. Live tool calls on restarted singleton: graph_stats schema 2 (4495 nodes), stage default path warns naming shared.py, `unstage_files` via real tool call unstaged shared.py with worktree intact (verified on disk), `skip_add` round-trip leaves index untouched, lint_task_file passes. Session catalog refreshed mid-run (15 tools incl. unstage_files). Issue #29 state verified CLOSED.

Closure 2026-10-10: "Approved for closure" received verbatim via relay question after green smoke on the new server code; file moved to tasks/completed/ with Status closed.

Follow-up extension (Manager order 2026-10-10, Persian; reused this task per Manager choice — no new task file): full parallel-session isolation round-trip. Added `unstage_files(files, project_root)` MCP tool (`git reset -q -- <files>` — first tried `git restore --staged`, which fails without HEAD; reset works with or without HEAD). Registry 14 → 15 tools (pin test updated). New tests: index-only unstage + empty-list rejection. Graph rebuilt (4495 nodes) and queried to confirm the related set; edited: 09-hands_protocols (RULE 2b + 2b parallel check in both summary phases), 13-constraints (ZAC now also bans `git checkout`), AGENTS.md staging step, executor ZAC, versioning-and-release Phase 3, audit-agents (2× new criterion), shell-strategy overrides, slice README/DECISIONS (ADR-009), system prompt 9.57.0 → 9.58.0 + pin + CHANGELOG. Discovery agent untouched (read-only, stages nothing). Services verified unchanged (same entrypoint). ZAC intact: commit/checkout/push forbidden everywhere; opencode.json untouched (custom_context_* wildcard already covers the new tool).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `7c63eedf4234f14101605a585380b1dccc37a585`
<!-- END_GIT_DIFF -->
