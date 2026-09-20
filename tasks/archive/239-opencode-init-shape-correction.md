# Task 239: opencode-init LSP formatter shape correction

**File:** `tasks/completed/239-opencode-init-shape-correction.md`
**Source:** manager
**Type:** improvement
**Status:** closed

Manager accept quote (closure gate): "Close task" — exact approval word received; file was in tasks/qa with PO_REVIEW_PENDING logged.

## Goal

Land the uncommitted opencode-init shape correction: flat LSP map, named formatter map, env-not-environment, stale language-server wrapper rejection.

## Manager's Notes

Autopilot locked for this order. Work the worktree changes, verify, stage, move to qa, Brain QA + review. Close only on explicit approval word.

Worktree truth: 6 unstaged modified files — CHANGELOG.md, skill-templates/opencode-init/SKILL.md, references/examples/golden-opencode.json, references/runtime-matrix.md, scripts/validate-opencode.py, tests/test_skill_registry.py. Evidence: real runtime rejections of the `language-server` wrapper shape from apex and blowsh-mcp. Blown fuses: L2-L6 in test_skill_registry (4 pre-existing fails) stay red until this lands.

## Local TODOs

- [x] Verify validator on golden + fixtures
- [x] Run registry suite, confirm red-to-green
- [x] CHANGELOG Parse-Then-Append check
- [x] lint_task_file, stage_and_inject_diff, git mv to qa

## Acceptance Criteria

- [x] Validator accepts corrected golden, rejects wrapper shape with global-path error
- [x] tests/test_skill_registry.py fully green
- [x] CHANGELOG entry present
- [x] Diff staged, file in qa, no commit, no close

## Verification Evidence

- **Test command:** uv tool run --with mcp==1.4.1 --with pathspec --with pytest pytest tests/test_skill_registry.py -q
- **Expected result:** all pass, exit 0
- **Actual result:** registry 20 passed exit 0; validator golden exit 0, wrapper fixture exit 1 with flat-map error; CHANGELOG bullet present in worktree diff
- **Exit code:** 0 (both)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** validator over-rejects valid project files
- **Rollback plan:** worktree diff revert, no commit yet

---

## Execution Log & Reasoning

Autopilot locked for Manager order (his word is the plan). Seat Check: Senior Programmer (validator + template + tests); no UI/schema/sprint triggers — Designer/Planner/Strategist skipped with reason; QA/Reviewer judge later turns. File landed in in-progress via git-mv-fallback path (untracked). Work was already in worktree (Manager-authored correction); Hands verified, did not author: registry 20 passed, golden exit 0, wrapper rejected with flat-map error. Replayed from DEC-20260914-003 (standing autopilot), DEC-20260915-001 (fix-all via Hands).

QA verdict: VERDICT QA_PASSED with cites (SKILL:18, golden:9, matrix:10, validator:168, CHANGELOG:19, task:32); residuals R1 validator tail truncated, R2 DoD build box unchecked — R2 fixed per box-checking mandate (registry 20 passed exit 0 + lint passed), restaged.

Reviewer verdict: PO_REVIEW_PENDING (technical approval, no blocking defect). Low notes: R1 CHANGELOG bullet omits task number; R2 acceptance text says global-path error, validator emits flat-map error; R3 test hunks truncated in reviewer view; R4 CHANGELOG mentions home-config sync path. Recommendations A1-A3 logged for a future docs pass; none block. Closure needs exact words "Approved for closure" or "Close task". File stays in tasks/qa. No commit.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c00bb87fa153fcf33f212ec4b40306f98e05cfd6`
<!-- END_GIT_DIFF -->
