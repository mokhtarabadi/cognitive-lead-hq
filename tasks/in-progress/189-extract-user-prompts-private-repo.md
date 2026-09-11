# Task 189: Extract personal user-prompts to a new private repo

**File:** `tasks/in-progress/189-extract-user-prompts-private-repo.md`
**Source:** manager
**Type:** feature
**Status:** in-progress

## Goal

Move all 10 personal files from `user-prompts/` out of cognitive-lead-hq into a new PRIVATE GitHub repo (created with `gh` in the parent projects dir), so no personal prompts remain in this HQ repo.

## Manager's Notes

- New repo MUST be private.
- Create it in the parent dir (`/home/mohammad/code-server/projects/` — the projects list), not inside this repo.
- Move (not copy): delete from here, push there.
- `git push` is ZAC-forbidden for agents — the Manager runs the push commands manually at the end.
- Files to move (10): agile-pm-state-manager.md, cold-start-context.md, daily-english-coach-chat.md, founder-coaching-chat.md, input-validation-test.md, multi-agent-brainstorming.md, perplexity-deep-research.md, persian-to-english-dictation.md, session-compactor.md, voice-to-text-enhancer.md.

## Local TODOs

- [ ] Verify `gh` auth + inventory `user-prompts/`
- [ ] Create private repo via `gh repo create` (parent dir)
- [ ] Move the 10 files, commit locally in new repo
- [ ] Remove `user-prompts/` from HQ repo via `git mv`/staged removal
- [ ] Verify no personal prompts remain + hand push commands to Manager

## Acceptance Criteria

- [x] New repo exists on GitHub, private, under the Manager's account
- [x] All 10 files present in the new repo (local commit ready, push by Manager)
- [x] Zero files remain under `user-prompts/` in cognitive-lead-hq
- [x] No other HQ files touched

## Verification Evidence

- **Test command:** `ls user-prompts/ 2>/dev/null || echo GONE; gh repo view <new-repo> --json visibility --jq .visibility`
- **Expected result:** `GONE` + `PRIVATE`
- **Actual result:** `HQ_DIR_GONE` + `PRIVATE` (`{"name":"user-prompts","visibility":"PRIVATE"}`); local commit `7e11998` in `/home/mohammad/code-server/projects/user-prompts/` with 10 files + README, `diff -r` COPIES_IDENTICAL before removal
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Files lost in transit between repos.
- **Rollback plan:** Nothing is deleted from HQ until the new repo's local commit is verified file-for-file (`diff -r`); `git log` in HQ retains history.

---

## Execution Log & Reasoning

Move-not-copy extraction per manager order. `gh repo create mokhtarabadi/user-prompts --private` (allowed: not in ZAC-denied list); visibility verified `PRIVATE` via `gh repo view`. Copied 10 files + new README to `/home/mohammad/code-server/projects/user-prompts/`, verified `diff -r COPIES_IDENTICAL`, then `git rm` from HQ and removed the empty dir. Local commit `7e11998` in the new repo with HQ git identity; remote `origin` set to SSH URL. Push deliberately NOT executed (ZAC: `git push` is Manager-owned — push commands handed to manager). No HQ files touched beyond the 10 deletions + CHANGELOG entry; history retained in HQ `git log`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
