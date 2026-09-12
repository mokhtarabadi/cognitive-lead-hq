# Task 205: Nine-Note Cleanup Run

**File:** `tasks/completed/205-nine-note-cleanup-run.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Resolve the manager's 9 cleanup notes in one autopilot run, each verified, then brain QA and reviewer.

## Manager's Notes

1. Remove 2026-09-09 pause/resume leftovers from agents files (confuses Hands); drop `(single MCP — replaces all archived automation)`.
2. Load audit-agents skill and audit the project (Mode 2).
3. Remove `./archive` folder.
4. Clean leftover docs like loop-engine; clean README.
5. RTK-ify `docs/opencode-shell-strategy.md` (must use RTK), update `LLM.txt` for RTK install, update global upgrade workflow to include RTK, install RTK for self; mirror denied commands from `opencode.json` into shell strategy.
6. Remove the 2026-09-09 paused date from `docs/setup.md`.
7. Unify `mcp-decision-server` + `mcp-brain-bridge` LLM setup: best options, most providers, OpenAI-compatible support; drop `muse-spark-1.3-contributor-free` default everywhere, default to OpenAI latest Astra model.
8. Disposition `scripts/qa-rules-gate/`: who calls it, when, by whom; repo-only → make it an MCP or delete if leftover.
9. Verify the `> **LIVE:**` line in `skill-templates/manager-decision/`.

## Local TODOs

- [x] Note 1: purge pause/resume leftovers
- [x] Note 2: audit-agents audit
- [x] Note 3: remove archive/
- [x] Note 4: loop-engine + README cleanup
- [x] Note 5: RTK everywhere + denied commands mirror
- [x] Note 6: setup.md date cleanup
- [x] Note 7: unify LLM setup on OpenAI
- [x] Note 8: qa-rules-gate disposition
- [x] Note 9: verify manager-decision LIVE line
- [x] Brain QA + reviewer, move to QA

## Acceptance Criteria

- [x] All 9 notes resolved with evidence
- [x] Suite green, lint clean, CHANGELOG updated

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with pathspec --with pyyaml --with mcp==1.30.0 python -m pytest tests/ -q` + `lint_task_file` + `lint_lint_system_prompt_sync`
- **Expected result:** exit 0
- **Actual result:** suite **237 passed** (264 − 27 deleted rules-gate tests = 237 exactly); sync check SYNC_OK; task lint clean (after this edit: pending re-lint)
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** doc-only run; archive/ removal is the only destructive step (git-restored if needed)
- **Rollback plan:** `git checkout` of removed paths (manager-owned git)

---

## Execution Log & Reasoning

Autopilot locked for the 9-note cleanup (goal active).

- **Note 1:** 6 edits — executor bridge quote/headings, setup.md pause sentence, README bridge + workflow sentences, LLM.txt parenthetical. Residual `2026-09-09` grep: zero hits in live docs.
- **Note 2:** audit-agents Mode 2 on AGENTS.md (132 lines) + conventions.md (181 lines) + .gitignore plugin state + deprecated-section scan: PASSED, no patches.
- **Note 3:** `archive/` held only the superseded RESTORE pointer; dead clause removed from conventions.md:77; dir deleted via rm.
- **Note 4:** loop-engine evidence table folded into shell-strategy §8, `docs/loop-engine/` deleted; README bridge/workflow/checklist aligned (one phantom fix logged, no such section on disk).
- **Note 5:** RTK 0.49.0 installed at `~/.local/bin/rtk` (corrected: earlier claim was wrong, binary lived in /tmp); shell-strategy §8 mandates `rtk test` + denied-commands mirror table; LLM.txt prerequisites + install subsection (`init -g` forbidden); upgrade-workflow memory step 4b. `rtk init -g` deliberately NOT run (rewrites global config — needs Manager word).
- **Note 6:** verified — zero `2026-09-09` hits across setup/agents/README/LLM.txt/shell-strategy/opencode.json.
- **Note 7:** 8-site swap to gpt-6-astra default (both servers, runtime .env pins, .env.example, brain-bridge docs, 4 test assertions); transport already OpenAI-compatible, no structural change.
- **Note 8:** zero live callers (only its own test + prose mentions) → leftover → DELETED script + tests; prose stripped from QA persona; version 9.29.0 → 9.30.0; prompt rebuilt (81684 bytes, sync OK).
- **Note 9:** LIVE line verified TRUE — `manager_decisions` connected in repo opencode.json (entry + allows) and global opencode.json:91 (+query allow:145). Two nuances, no file change: (a) Hands in-session path is indirect (tools never in session toolset — uv-run python workaround, proven all session); (b) LLM.txt §7 template JSON omits the server → fresh installs would NOT match the claim — proposed follow-up (install-behavior change, needs Manager word).
- **Brain QA (verbatim hunks H1–H6 pasted):** QA_PASSED with machine block (F1–F5: denied table matches ZAC, bridge fold clean, symmetric astra swap, gate strip prevents dangling ref, version bump synced; residuals R1 model probe / R2 link check).
- **Post-QA R2 closure:** live grep zero refs outside history/CHANGELOG/tasks; trimmed one self-describing removal pointer (shell-strategy:159); suite re-run 237 passed.
- **Reviewer:** APPROVED technically, PO_REVIEW_PENDING (F1–F5, I1–I2 Low: model probe + no full-diff round; coherent 9.30.0 release, no split/revert/block). No autoclosure per standing rule — awaiting Manager "Approved for closure". — `manager_decisions` connected in repo opencode.json (entry + allows) and global opencode.json:91 (+query allow:145). Two nuances, no file change: (a) Hands in-session path is indirect (tools never in session toolset — uv-run python workaround, proven all session); (b) LLM.txt §7 template JSON omits the server → fresh installs would NOT match the claim — proposed follow-up (install-behavior change, needs Manager word).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `7471aa6b1c25a57778108f87f13d626a438ab18f`
<!-- END_GIT_DIFF -->
