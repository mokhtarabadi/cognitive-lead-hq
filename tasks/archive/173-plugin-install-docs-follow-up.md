# Task 173: Plugin Install Docs Follow-Up

**File:** `tasks/completed/173-plugin-install-docs-follow-up.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Source Context

## Goal

Document the plugin install + verify steps that the /dcp-compress outage exposed (referenced-but-never-installed plugins).

## Manager's Notes

- Add explicit goal-plugin install command + cache-presence verification to LLM.txt §7.7 and README plugins section.
- Trigger: `@tarquinen/opencode-dcp` + `@prevalentware/opencode-goal-plugin` were referenced in all 4 configs but never installed; fixed globally during diagnosis.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Add install + verify docs to LLM.txt and README
- [x] Lint both files, stage, verify no secrets

## Acceptance Criteria

- [x] LLM.txt documents both plugin installs + cache verification + restart requirement
- [x] README mirrors the install/verify block
- [x] Both files lint clean

## Verification Evidence

- **Test command:** `lint_markdown` on LLM.txt + README.md
- **Expected result:** both pass
- **Actual result:** both passed
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Docs-only change; no code impact.
- **Rollback plan:** Revert the two hunks.

---

## Execution Log & Reasoning

Docs-only follow-up to the /dcp-compress outage: root cause was referenced-but-never-installed plugins (packages land in `~/.cache/opencode/packages/` only via `opencode plugin <mod> -g`, and slash commands appear after restart). LLM.txt §7.7 now carries both install commands + cache verification + restart warning; README plugins section mirrors it. CHANGELOG carries a Task 173 bullet under Changed; memory workflow carries the plugin-install lesson (Update 2026-09-09).

QA round 1 verdict: QA_REJECTED on C1 (LOW scope creep — one DECISION env-passthrough sentence from the 170/171 domain bundled in the 2026-09-08 memory entry). Fix applied: sentence removed from the memory file (2026-09-09 plugin-install lesson kept); `lint_markdown` re-passed. C2/C3/C4 passed.

Post-restart pipeline (manager order: QA → reviewer → auto-close, Telegram gate waived): QA rounds 2+ hit endpoint flakiness (empty REPORTs, one 69KB non-verdict ramble, one confabulating loop). Transcript reset twice (backups /tmp/transcript-173-backup.jsonl, /tmp/transcript-173-pre-reset.jsonl). Final QA with the literal 6473-char staged diff embedded returned QA_PASSED (C1-C4 PASS, grounded). Code Reviewer returned APPROVED (after 2 empty-report flakes, minimal-prompt retry). Deterministic tool verification (independent of persona lane): staged set = exactly the 4 docs + task file, all Markdown; secret regex CLEAN; zero 'decision' on '+' lines (13 hits all space-prefixed context); single 'token' hit is benign prose; lint_task_file + lint_markdown PASS. Telegram gate skipped per explicit manager waiver. Auto-closing.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `121768a07a89c997df182f4aa756e356df7c5acd`
<!-- END_GIT_DIFF -->
