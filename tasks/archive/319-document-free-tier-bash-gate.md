# Task 319: Document free-tier bash gate in custom agents

**File:** `tasks/completed/319-document-free-tier-bash-gate.md`
**Source:** manager
**Type:** docs
**Status:** closed

## Goal

Document the upstream free-tier bash gate and guard custom agents against tool-restricted 403s.

## Manager's Notes

Goal accepted: "full implmment this issue https://github.com/mokhtarabadi/cognitive-lead-hq/issues/30 using our skills and brain full auto mode." Issue 30: upstream free-tier gating is triggered by request body tool list, not headers. Any agent omitting `bash` is classified as not from within OpenCode. Suggested actions: (1) document never ship custom agent without bash for free-tier models, (2) review checklist free-tier smoke test, (3) DECISIONS.md entry with upstream links.

## Local TODOs

- [x] Gather context (agents, opencode.json, docs)
- [x] Brain plan with Seat Check
- [x] Implement docs guard
- [x] Verify (lint, grep)
- [x] Stage and move to qa

## Acceptance Criteria

- [x] Agent docs state bash requirement for free-tier models
- [x] Review checklist includes free-tier smoke test
- [x] DECISIONS.md entry records upstream behavior with links
- [x] `lint_task_file` passes

## Verification Evidence

- **Test command:** docs-only, no suite — `lint_task_file` plus grep gates; tooling gate skip: root ., markers [package.json, requirements.txt, go.mod, Cargo.toml, pom.xml], matched none, reason no stack marker found
- **Expected result:** lint passes, greps match, no task-number leak
- **Actual result:**
  - `grep -n Free-tier bash gate agents/README.md` → line 18 match, exit 0
  - `grep -n Free-tier smoke test agents/README.md` → line 23 match, exit 0
  - `grep -n Free-tier bash gate documented agents/DECISIONS.md` → line 10 match, exit 0
  - `grep -c anomalyco/opencode agents/DECISIONS.md` → 6, exit 0
  - `grep -rn 5425 agents/README.md agents/DECISIONS.md` → empty, exit 1 handled (no leak)
  - `lint_task_file` → pending (summary phase)
- **Exit code:** 0 (greps)

## Code-guard extension (same task, autopilot)

- Upstream context round: all six upstream issues fetched via gh (50627 OPEN 14 comments with shell deny-all repro; 54744 triaging — restricted subagent fails even with bash allowed, so bash is necessary but not sufficient; 53347, 53885, 52880, 49592 closed). Brain implementation plan (Programmer, 4 steps) approved by Manager ("Approved", try 1); implementation XML issued bare unfenced, executed from it.
- New `tests/test_agent_tool_gate.py` (stdlib-only frontmatter parse, two tests: free-tier agents assert bash allow with discovery exempt, discovery asserts deny edit plus bash). Repair 1: glob caught slice docs without frontmatter — restricted `_agent_files` to frontmatter-carrying definitions.
- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_agent_tool_gate.py -q` (raw `pytest` unavailable — no binary in venvs, uv-run path used)
- **Expected result:** 2 passed, exit 0
- **Actual result:** first run 1 failed 1 passed (missing README.md plus DECISIONS.md from glob); after repair 2 passed in 0.02s, exit 0
- **Exit code:** 0
- Prose hygiene: `grep -rn 319` and `grep -rn 5425` on the test file → both empty (echo paths), no number leak; upstream numbers live only as URL refs.
- Tooling gate: docs-plus-test change, no stack blueprint applies; skip record — root ., markers [package.json, requirements.txt, go.mod, Cargo.toml, pom.xml], matched none, reason no stack marker found.
- Sibling docs: tests README plus DECISIONS describe suite generically (no per-file list to update); no slice change beyond the new test file itself.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append

## Risk & Rollback

- **Risk:** Future agent profile drops bash and hits misleading 403 on free-tier models.
- **Rollback plan:** Revert the two agents docs hunks via `git checkout --` on those paths only.

## Execution Log & Reasoning

Autopilot locked for issue 30 implementation.
Seat Check: agent docs plus permission guard → Software Architect requested; Designer, Programmer (planning), Planner, Strategist, QA, Reviewer skipped with single-domain docs reason. Trigger map explicit miss, no UI/schema/perf hits. Brainstorm: not required — docs-only reversible single-domain change.
Brain plan verdict (Architect, stage plan): 5-step docs-guard plan approved by Manager ("Approved", try 1). Selected path: README bash note plus checklist plus DECISIONS entry with six upstream links, no permission changes, ZAC holds.
Assumption A1: issue body quoted in task notes is verbatim from gh issue view. Reason: byte output captured via gh CLI.
Implementation notes: appended bash-gate section plus smoke-test checklist to agents/README.md (no permission edits); appended accepted DECISIONS entry with six upstream refs; CHANGELOG entry under Unreleased Added; sibling agents README plus DECISIONS inspected before edits per Living Folder Docs, no other slice change.
Autopilot pipeline (code guard): QA verdict QA_PASSED (no permission drift, frontmatter filter correct, discovery exemption explicit, fallback cannot hide dropped bash). Code Reviewer verdict: technically APPROVED, PO_REVIEW_PENDING (5 strengths, 1 low non-blocking: wildcard deny shape theoretical, follow-up R1). File stays in tasks/qa/ until the exact closure word. Autopilot never commits or closes.
Manager accept quote for closure: Approved for closure.
Closure 2026-10-17: file verified in tasks/qa/ with PO_REVIEW_PENDING in log; status closed, moved to completed via git mv; commits via commit_and_clean_task only. Feature hash 972286928ead6290b3562e2d277b332f0af86b11.
Task-number correction: file created as 5425 from a bad NEXT_ID scan (grep over full paths caught timestamp fragments); real Kanban max is 318, so renamed via git mv to 319, header updated, lint re-passed, diff re-injected. Brain history continues under the same session thread.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `972286928ead6290b3562e2d277b332f0af86b11`
<!-- END_GIT_DIFF -->
