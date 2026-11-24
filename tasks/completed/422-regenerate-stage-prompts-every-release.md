# Task 422: Regenerate Stage Prompts Every Release and Repair Handoff Test

**File:** `tasks/completed/422-regenerate-stage-prompts-every-release.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Finished:** 2026-11-24T06:29:06Z
**Submitted:** 2026-11-24T05:38:43Z
**Estimate:** 5h
**Deadline:** 2026-11-25
**Started:** 2026-11-24T05:12:06Z

## Source Context

## Goal

Prevent releases from leaving stale stage prompts that bypass the full system prompt, and repair the handoff-language test regression found after task 421. Every prompt release must regenerate and verify both the full prompt and all stage prompts before global install.

## Manager's Notes

- Verbatim request: "this is important, always must be regenerate add this to our docs or our scripts in each release them generated too" and "fix both, a task required, that important for us".
- F1: `tests/test_input_validation_pipeline.py::test_executor_handoff_uses_requested_language` expects the retired exact phrase `regardless of the input language`. Task 421 kept the always-English behavior but changed the wording to `regardless of the user's input language`. The test must verify the behavior without pinning a brittle duplicate sentence.
- F2: `build/stage-prompts/system-prompt.*.md` remained at version 9.93.0 after task 421 regenerated only `system-prompt.md`. Brain Bridge prefers stage artifacts when present, so stage-scoped turns silently used the old 80–180-word and 2–5-sentence budgets.
- Standing rule saved to project memory: every release that changes prompt fragments must regenerate the full prompt and all stage prompts, and the release is incomplete while any stage artifact is stale.
- Stage artifacts are gitignored build/deploy outputs. The durable fix belongs in scripts, tests, and release documentation, not in committing generated stage files.

## Local TODOs

- [x] Inspect assembler `--stages`, stage manifest, Brain Bridge stage-artifact preference, and release docs
- [x] Write a failing regression test for stale stage-prompt detection before changing implementation
- [x] Implement an automated stage-prompt freshness check tied to the assembler/release workflow
- [x] Document mandatory full-prompt plus stage-prompt regeneration in release docs and skill copies
- [x] Repair F1 with a behavior-focused assertion, not a weaker test
- [x] Bump the system-prompt patch version and regenerate both full and stage prompts
- [x] Run stage generation twice and verify deterministic, fresh artifacts
- [x] Run the full test suite, prompt-sync checks, and task lint
- [x] Update CHANGELOG, decisions, and task evidence
- [x] Deploy regenerated full/stage prompts to the global install and verify versions

## Acceptance Criteria

- [x] F1 passes while still proving the executor requires user-facing output to remain technical English regardless of input language
- [x] A machine-enforced check fails when stage prompts are stale relative to the full prompt or current fragments
- [x] The release workflow invokes or requires that check before a release is accepted
- [x] `prompts/README.md` and both copies of the versioning skill document full-prompt plus stage-prompt regeneration
- [x] `system-prompt.md` and all eight stage prompts report the same new version
- [x] Every stage prompt contains the current fragment delta, including the Manager-Facing Concision Contract
- [x] The full test suite passes with exit code 0 and fresh evidence is recorded
- [x] Global install receives the regenerated full prompt and all stage prompts

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml pytest tests/ -q
- **Expected result:** all tests pass, including stale-stage detection and handoff-language behavior
- **Actual result:** 998 passed, 23 warnings. Includes F1 repair, stale-stage fallback, assembler freshness gate, orphan-stage rejection, explicit override priority, and release ordering.
- **Exit code:** 0
- **Additional gates:** docs sync exit 0; targeted suites 108 passed exit 0; full/stage regeneration exit 0; `--check` exit 0 with 8 current artifacts; version equality 9.94.1 across all 9 prompts; concision delta in all 8 stages; determinism diff exit 0; release script `bash -n` exit 0; global deploy comparisons exit 0; `build/` remains ignored.

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** A release guard that compares generated files incorrectly can block valid releases or miss stale stage subsets. A semantic handoff assertion could become too loose and stop catching regressions.
- **Rollback plan:** Revert the guard implementation and test changes, restore the prior release wording, decrement the version marker, regenerate the full prompt, and re-run the suite. Stage artifacts can be regenerated from current fragments at any time.

---

## Execution Log & Reasoning

Baseline F1: `rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml pytest tests/test_input_validation_pipeline.py::test_executor_handoff_uses_requested_language -q` → 1 failed, exit 1, before implementation.
Baseline stage tests: `rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml pytest tests/test_stage_prompts.py -q` → 22 passed, exit 0, before implementation.
Versioning skill byte equality: `cmp skill-templates/versioning-and-release/SKILL.md ~/.config/opencode/skills/versioning-and-release/SKILL.md` → exit 0.
Discovery loader finding: `mcp-brain-bridge/server.py#L1659-1682` accepts an existing stage artifact using only `path.is_file()` and `read_text`; no version, hash, timestamp, or content check. Repo artifacts precede global basenames. Missing artifacts fall back to the full prompt. Full-prompt sync tests do not cover stage freshness.
Discovery F1 finding: `tests/test_input_validation_pipeline.py#L74` pins the retired phrase `regardless of the input language`; `agents/cognitive-executor.md#L222` now says `regardless of the user's input language`. The behavior remains always-English technical output, so the test needs a section-scoped semantic assertion.

Approved plan: O1 runtime fallback plus assembler byte-freshness gate plus release ordering, version 9.94.1. Manager approved via question tool. No Hands restart; ADR provenance uses HTML comments only.
A1: Release deploy loop uses standalone `cmp` followed by `echo`, not `cmp && echo`, because `set -e` does not reliably exit on a failed left-hand command in an AND list. This preserves the intended hard gate.
Rule correction 1: the first implementation XML ordered a Hands restart; halted and reissued with Manager-owned restart only, per `.opencode/memory/workflows/global-install-upgrade.md:66`.
Rule correction 2: the first implementation XML put HQ-specific assembler flags into the redistributed versioning skill; halted and reissued with a conditional command-free rule, per `skill-templates/README.md:14`.
AC4 mapping: the generic rule in both byte-identical versioning-skill copies plus the HQ-specific commands in `prompts/README.md` and `scripts/README.md` satisfy the release-documentation criterion without leaking HQ scaffolding.
Phase 1 evidence: F1 module baseline 1 failed/5 passed exit 1; after semantic repair 6 passed exit 0. Runtime tests RED 24 passed/1 failed exit 1. Assembler/release tests RED 24 passed/5 failed exit 1.
Phase 2 evidence: bridge guard targeted tests 4 passed exit 0; assembler --check tests 3 passed exit 0; full stage module 29 passed exit 0; `bash -n scripts/release-9.66.0.sh` exit 0.
Phase 3 evidence: full assembler exit 0; stage assembler exit 0 for all 8 artifacts; `--check` exit 0 with `check: full prompt and 8 stage artifacts are current`. Distinct version output exactly `<system_version>9.94.1</system_version>`. Concision-contract file count 8. Retired-budget grep exit 1 (no matches). Two independent stage builds diff exit 0. `git status --short build/` empty. Stale `9.94.0` test literals grep exit 1 (none).
Phase 4 docs evidence: `prompts/README.md` has Stage Prompt Freshness; `scripts/README.md` has the release invariant; `mcp-brain-bridge/README.md` records stale fallback and override priority. Versioning skill copies `cmp` exit 0, conditional rule present, HQ-leak grep exit 1. ADR task-number hits are HTML-comment provenance only; visible-prose grep exit 1.
Edge hardening: explicit stage-path override RED 1 failed, then GREEN after tracking ungated override candidates; orphan stage-file check RED 1 failed, then GREEN after exact filename-set comparison. Targeted final 108 passed exit 0; full final 998 passed exit 0; post-doc freshness exit 0; `bash -n` exit 0.
Deploy evidence: copied full plus all 8 stage prompts to `~/.config/opencode/`; every `cmp -s` exit 0; deployed mtimes recorded at 2026-11-24 06:28:25 +0100. No `systemctl`, no singleton/OpenCode/OpenChamber restart.
restart owed to Manager: the running bridge still serves pre-deploy prompts and pre-change loader code until the Manager restarts OpenCode.
A2: The approved summary omitted `system-prompt.md` from `modified_files` even though Phase 3 regenerated it. The factual staged set must include it, so the repo-file count is 17 before the task file, not 16.
A3: `tests/README.md` and `tests/DECISIONS.md` were added to the changed set because test contracts changed and the Living Folder Docs Standard requires sibling synchronization.
A4: `.opencode/memory/release/stage-prompts-regenerate-every-release.md` and its auto-generated `.opencode/memory/index.md` were created at the Manager's explicit request immediately before this task. They are included in the factual changed set so the standing rule is committed with its enforcement; no duplicate memory write occurred during implementation.
Final lint: `lint_task_file` passed; QA budget 0/1. `lint_system_prompt_sync` reports `system-prompt.md is in sync` plus the two known false positives at `09-hands_protocols.md:150` and `DECISIONS.md:76`, previously verified and deferred; no new warning was introduced.
QA round 1 dispute: the requested CHANGELOG relocation does not reproduce. `grep -n '^## \[' CHANGELOG.md` returns `Unreleased` at line 7, `9.94.1` at line 43, then `9.90.0` at line 56. `grep -c '^## \[9\.94\.0\]' CHANGELOG.md` returns 0 with exit 1, so the cited destination header does not exist. The `9.94.1` section is already directly below Unreleased and above the next actual version header, which is the newest-first position. No CHANGELOG content or position was changed for this dispute. Pre-existing Unreleased debt is outside this task's scope.
QA round 2: QA_PASSED, recovered from the bridge artifact `tasks/.sessions/ses_df6723727ffeyqIEuj01fTgRgS_8777faaf/brain_outputs/chatcmpl_3c3f5c2c_d7bd_475b_8403_4452dc88ab184a5ebaa8c372e08cfd85.json` after two client-side timeouts. QA confirmed the original relocation finding was its error. Non-blocking observations for review: offender-count exit can exceed 1; stale stderr note can precede a fresh second-home fallback; pre-existing Unreleased debt remains out of scope.
Review blocker: the Code Mode catalog removed the `brain` namespace. `brain_turn` is unavailable and no replacement tool exists in the catalog search. The mandatory Code Reviewer turn cannot run, so technical approval and closure are blocked. Task remains in `tasks/qa/` with all changes staged; no commit or restart performed.
Review blocker re-check after Manager reported Brain restored: `tools.brain.brain_turn` still returns `Unknown tool 'brain.brain_turn'`; a fresh registry search for Brain review tools returns zero Brain entries. The service may be running, but this session has not reloaded the MCP tool registry. Task remains in `tasks/qa/`; parallel-session unstaged changes remain untouched.
Code review round 1: PO_REVIEW_PENDING — technically approved against the staged diff. Non-blocking recommendations R1-R4: reword --check help to non-zero on drift; make stderr note reflect the finally selected candidate; schedule release-cutoff cleanup for pre-existing Unreleased debt; consider stacked review slices for future releases over 400 lines.
Manager closure approval (question-tool answer value, verbatim): "Approved for closure".

### Closure checklist

- [x] Step 1: set task status to closed
- [x] Step 2: retarget File header to tasks/completed/422-regenerate-stage-prompts-every-release.md
- [x] Step 3: move task file from tasks/qa/ to tasks/completed/
- [ ] Step 4: run custom_context_commit_and_clean_task exactly once
- [ ] Step 5: verify commit ancestry, clean index, and cleared QA lane

## Implementation Progress

- [x] Step 1: claim task through planner
- [x] Step 2: schedule 5h estimate and 2026-11-25 deadline
- [x] Step 3: repair F1 semantic assertion; module green 6 passed, exit 0
- [x] Step 4: add runtime freshness tests; RED 24 passed, 1 failed, exit 1
- [x] Step 5: add assembler/release tests; RED 24 passed, 5 failed, exit 1
- [x] Step 6: add bridge version helpers
- [x] Step 7: wire stale-stage fallback
- [x] Step 8: add assembler --check
- [x] Step 9: gate release script generation/check/deploy
- [x] Step 10: bump version to 9.94.1
- [x] Step 11: re-anchor pinned test versions
- [x] Step 12: regenerate full and stage artifacts; run --check
- [x] Step 13: prove versions, delta, determinism, gitignore
- [x] Step 14: update normative READMEs
- [x] Step 15: update and mirror versioning skill
- [x] Step 16: CHANGELOG entry
- [x] Step 17: four ADRs with HTML-comment provenance
- [x] Step 18: deploy full and stage artifacts; no restart
- [x] Step 19: full green gate

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `0a95d97458f8ad5c9463380c5bf881a6a2641e73`
<!-- END_GIT_DIFF -->
