# Task 208: Archive milestone 18 and update release rule

**File:** `tasks/qa/208-archive-milestone-18-and-update-release-rule.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Archive completed tasks into a milestone summary and make archive-on-release a permanent rule.

## Manager's Notes

Manager order (translated from Persian): archive current tasks, no new release needed, current release is fine. Re-stage if needed and fix the push script if needed. Script must create the GitHub release and keep changelogs clean. From now on every release must archive tasks. Update both memory and manager decisions.

## Local TODOs

- [x] Scan completed tasks and write milestone summary
- [x] Move completed files to archive
- [x] Update release memory with archive-on-release rule
- [x] Record manager decision for archive-on-release
- [x] Verify push script and CHANGELOG, fix if needed

## Acceptance Criteria

- [x] `docs/history/milestone-18-summary.md` exists with all completed tasks covered
- [x] `tasks/completed/` is empty, files moved to `tasks/archive/`
- [x] Release memory holds the archive-on-release rule
- [x] Manager decision recorded for archive-on-release
- [x] Push script creates tag, pushes, creates or verifies GitHub release
- [x] `lint_task_file` passes, diff staged via stage tool

## Verification Evidence

- **Test command:** `ls tasks/completed/; ls tasks/archive/ | wc -l; ls docs/history/milestone-18-summary.md`
- **Expected result:** completed empty, archive grew, summary exists
- **Actual result:** completed empty, archive 183 → 213, milestone-18 summary exists, memory stored, DEC-20260912-013 recorded, script SYNTAX_OK
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `verification-before-completion` applied and evidence recorded
- [ ] `CHANGELOG.md` updated via Parse-Then-Append (N/A: 9.31.0 section already clean, no new release cut)
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** moving 30 files at once, history reachable only via git log after move.
- **Rollback plan:** `git mv tasks/archive/<file> tasks/completed/` per file before any commit; no commit happens without approval.

---

## Execution Log & Reasoning

Scanned 30 completed files via a read-only subagent (all manager source: 16 feature, 13 improvement, 1 research). Wrote milestone-18 summary covering every task. Moved all 30 files to archive with git mv (completed now empty, archive 183 → 213). Stored the archive-on-release rule in release memory (overwrite). Recorded the manager ruling as DEC-20260912-013 with verbatim Persian quote plus English translation. Script fixes: added `git fetch --tags`, replaced `--web` view (browser opener, unsafe headless) with plain view, verify step now fails loudly when remote tag or release is missing. CHANGELOG verified clean (Unreleased empty, single Added/Changed/Fixed under 9.31.0) so no edit needed. No commit: closure approval not given for this task.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/decisions/decisions/2026/09/DEC-20260912-013.json b/.opencode/decisions/decisions/2026/09/DEC-20260912-013.json
new file mode 100644
index 0000000..6ccd151
--- /dev/null
+++ b/.opencode/decisions/decisions/2026/09/DEC-20260912-013.json
@@ -0,0 +1,20 @@
+{
+  "extracted_decision": {
+    "alternatives": [
+      "Archive tasks only at milestones"
+    ],
+    "category": "process",
+    "rationale": "Manager wants completed tasks compacted on every release instead of piling up, and the release script must cover tag, push, and GitHub release with a clean changelog.",
+    "summary": "Every future release must archive tasks/completed/ via the archive-tasks skill as part of the release",
+    "tradeoffs": "Archive step adds release time but keeps the board clean and history reachable"
+  },
+  "project_name": "cognitive-lead-hq",
+  "session_id": "208",
+  "verbatim_quote": {
+    "english_translation": "Please archive the current tasks too. No need to build a new release, the release you made is fine, just archive the current tasks too. From now on whenever we want to release, the tasks must be archived.",
+    "original": "لطفاً تسک‌های فعلی رو هم آرکایو کن. نیاز نیست ریلیز جدید بسازی، همین ریلیزی که انجام دادی همه‌چی اوکیه، فقط تسک‌های فعلی رو هم آرکایو کن. از این به بعد هر موقع خواستیم ریلیز بزنیم باید تسک‌ها آرکایو بشن."
+  },
+  "redaction_verified": true,
+  "decision_id": "DEC-20260912-013",
+  "timestamp": "2026-09-12T12:19:50.188868+00:00"
+}
diff --git a/.opencode/decisions/decisions/2026/09/DEC-20260912-013.md b/.opencode/decisions/decisions/2026/09/DEC-20260912-013.md
new file mode 100644
index 0000000..a646f78
--- /dev/null
+++ b/.opencode/decisions/decisions/2026/09/DEC-20260912-013.md
@@ -0,0 +1,17 @@
+# DEC-20260912-013 — Every future release must archive tasks/completed/ via the archive-tasks skill as part of the release
+
+- Category: process
+- Session: 208
+- Project: cognitive-lead-hq
+
+## Verbatim (original)
+
+> لطفاً تسک‌های فعلی رو هم آرکایو کن. نیاز نیست ریلیز جدید بسازی، همین ریلیزی که انجام دادی همه‌چی اوکیه، فقط تسک‌های فعلی رو هم آرکایو کن. از این به بعد هر موقع خواستیم ریلیز بزنیم باید تسک‌ها آرکایو بشن.
+
+## Verbatim (English)
+
+> Please archive the current tasks too. No need to build a new release, the release you made is fine, just archive the current tasks too. From now on whenever we want to release, the tasks must be archived.
+
+## Rationale
+
+Manager wants completed tasks compacted on every release instead of piling up, and the release script must cover tag, push, and GitHub release with a clean changelog.
diff --git a/.opencode/decisions/decisions/INDEX.md b/.opencode/decisions/decisions/INDEX.md
index 9346ae1..13f60ff 100644
--- a/.opencode/decisions/decisions/INDEX.md
+++ b/.opencode/decisions/decisions/INDEX.md
@@ -16,3 +16,4 @@
 | DEC-20260912-010 | process | Manager orders recurring-style self-judgment runs: fresh task, Brain Architect planning + brainstorm | `decisions/2026/09/DEC-20260912-010.json` |
 | DEC-20260912-011 | process | In-flight findings go to a side note (/tmp) during the run, not into the task file; only final verdi | `decisions/2026/09/DEC-20260912-011.json` |
 | DEC-20260912-012 | tooling | Mechanical permission-layer lock: executor agents can never run git add/checkout/commit/push via bas | `decisions/2026/09/DEC-20260912-012.json` |
+| DEC-20260912-013 | process | Every future release must archive tasks/completed/ via the archive-tasks skill as part of the releas | `decisions/2026/09/DEC-20260912-013.json` |
diff --git a/.opencode/memory/release/release-workflow.md b/.opencode/memory/release/release-workflow.md
index ca17376..f868720 100644
--- a/.opencode/memory/release/release-workflow.md
+++ b/.opencode/memory/release/release-workflow.md
@@ -1,8 +1,8 @@
 ---
-created_at: '2026-08-17T09:55:12.993426+00:00'
+created_at: '2026-09-12T12:19:12.494958+00:00'
 status: active
 tags: []
-updated_at: '2026-09-03T08:15:00.000000+00:00'
+updated_at: '2026-09-12T12:19:12.494983+00:00'
 ---
 
 Release workflow for cognitive-lead-hq.
@@ -17,6 +17,8 @@ Before every release:
   - MINOR: new skills, new workflow capabilities, non-breaking architectural upgrades.
   - MAJOR: breaking workflow changes or full system prompt protocol rewrites.
 
+Archive-on-release (standing manager rule, 2026-09-12): every release must archive tasks/completed/ first via the archive-tasks skill (milestone summary in docs/history/, git mv to tasks/archive/). Never cut a release while completed tasks pile up; the release task's Acceptance Criteria must include the archive step.
+
 CHANGELOG rules:
 - Use Keep a Changelog format.
 - Use Parse-Then-Append: never create duplicate version headers or duplicate category headers.
@@ -51,4 +53,4 @@ Push-script generation (since v9.8.0 — Task 157):
 
 Memory rule:
 - This memory lives at release/release-workflow.
-- Future release tasks must retrieve and follow this memory before making release decisions.
+- Future release tasks must retrieve and follow this memory before making release decisions.
\ No newline at end of file
diff --git a/docs/history/milestone-18-summary.md b/docs/history/milestone-18-summary.md
new file mode 100644
index 0000000..62021ef
--- /dev/null
+++ b/docs/history/milestone-18-summary.md
@@ -0,0 +1,252 @@
+# Milestone 18 Summary
+
+**Date:** 2026-09-12
+**Tasks Compacted:** 30
+
+## Source Distribution
+
+| Source       | Count |
+| ------------ | ----- |
+| orchestrator | 0     |
+| telegram     | 0     |
+| manager      | 30    |
+
+## Architectural Changes
+
+Milestone 18 spans the Brain-bridge era through release v9.31.0. Core work: unified Brain bridge MCP server with per-task history, context bundle, and file-pull tools; deterministic decision extraction plus alternatives search; transcript compaction with traceability; machine-readable QA verdicts; diff-hash loop guard; golden replay harness; retryable versus fatal transport taxonomy; full-task-file auto-attach; QA and reviewer hunks carriage; planning gate; XML execution autonomy; dual-channel communication; always-English output; voice-to-text normalization; goal lifecycle; spider-search research workflow; persona auto-load; prompt rebuilds from v9.13.0 to v9.31.0; milestone-17 archive; private user-prompts extraction; cleanup sweep deleting paused-automation leftovers; token-optimization spike; systemd unit env fix.
+
+## Files Modified
+
+| File         | Change      |
+| ------------ | ----------- |
+| CHANGELOG.md | release entries v9.13.0 through v9.31.0 |
+| system-prompt.md | regenerated builds up to 9.31.0 |
+| prompts/fragments/ | version bumps plus persona, protocol, and constraint edits |
+| agents/cognitive-executor.md | autonomy, planning gate, goal lifecycle, bridge wiring |
+| mcp-brain-bridge/ | new bridge server plus loop guard and replay harness |
+| mcp-decision-server/ | deterministic extraction plus alternatives search |
+| skill-templates/ | blowsh research workflow, fintech skill updates, deletions of superseded skills |
+| docs/ | brain-bridge runbook, setup, shell strategy, history summaries |
+| scripts/qa-rules-gate/ | created then removed as leftover |
+| tests/ | bridge, decision, guard, replay, attach suites |
+| user-prompts/ | moved out to private repo |
+| opencode.json | bridge and decision wiring plus permission denies |
+| LLM.txt | setup, plugin, and model-pin docs |
+| README.md | bridge reality plus modes and skill counts |
+
+## Criteria Met
+
+| Task | Acceptance Criteria | Status |
+| ---- | ------------------- | ------ |
+| 150 | RTK practices documented with evidence | ✅ Met |
+| 179 | v9.13.0 cut plus milestone-17 archived | ✅ Met |
+| 180 | dual-channel plus brainstorm fixes | ✅ Met |
+| 181 | execution autonomy plus number discipline | ✅ Met |
+| 182 | self-driving QA and reviewer loops | ✅ Met |
+| 183 | always-English output | ✅ Met |
+| 184 | goal lifecycle | ✅ Met |
+| 185 | spider synthesis plus saturation | ✅ Met |
+| 186 | spider-search workflow | ✅ Met |
+| 187 | persona auto-load | ✅ Met |
+| 188 | voice-to-text normalization | ✅ Met |
+| 189 | user-prompts extracted private | ✅ Met |
+| 190 | unified Brain bridge live | ✅ Met |
+| 191 | deterministic extraction | ✅ Met |
+| 192 | alternatives search | ✅ Met |
+| 193 | file-pull discoverability | ✅ Met |
+| 194 | compaction plus traceability | ✅ Met |
+| 195 | machine verdicts plus rules gate | ✅ Met |
+| 196 | loop guard | ✅ Met |
+| 197 | replay harness | ✅ Met |
+| 198 | error taxonomy | ✅ Met |
+| 199 | persona and fintech research | ✅ Met |
+| 200 | full task-file attach | ✅ Met |
+| 201 | QA hunks plus modes doc | ✅ Met |
+| 202 | planning gate | ✅ Met |
+| 203 | self-judgment run | ✅ Met |
+| 204 | self-judgment fixes | ✅ Met |
+| 205 | nine-note cleanup | ✅ Met |
+| 206 | systemd unit env docs | ✅ Met |
+| 207 | v9.31.0 plus push script | ✅ Met |
+
+## Individual Task Summaries
+
+### Task 150: Future token optimization research
+
+- **Type:** research
+- **Source:** manager
+- **Reasoning:** Measured RTK trimming locally and documented practices with evidence tables.
+
+### Task 179: Release v9.13.0 plus milestone-17 archive
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Cut v9.13.0 and archived milestone-17 tasks with a manual push script.
+
+### Task 180: Dual-channel communication
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Split concise manager output from comprehensive machine blocks and fixed brainstorming contradictions.
+
+### Task 181: Executor autonomy
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Added assume-first autonomy rules and the task-number reference discipline.
+
+### Task 182: Self-driving QA and reviewer loops
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Rejections now auto-emit scoped hotfix XML on the same task file.
+
+### Task 183: Always-English output
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Manager-facing text stays simple English regardless of input language.
+
+### Task 184: Goal lifecycle
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Heavy tasks run under session goals closed only with evidence.
+
+### Task 185: Spider synthesis upgrade
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Added corroboration, ranked synthesis, and saturation stops to the research workflow.
+
+### Task 186: Spider-search workflow
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Encoded the plan, sweep, probe, read, chain, cite loop for the blowsh skill.
+
+### Task 187: Persona auto-load
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Added confidence-threshold persona loading and generalized language wording.
+
+### Task 188: Voice-to-text normalization
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Made input normalization an explicit written pipeline step.
+
+### Task 189: User-prompts extraction
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Moved personal prompts to a private repo, verified identical before removal.
+
+### Task 190: Unified Brain bridge
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Replaced paused automation with one stateful bridge tool plus history and bundle.
+
+### Task 191: Deterministic extraction
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Pinned extraction to byte-identical output with schema checks and cache.
+
+### Task 192: Alternatives search
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Decision queries now also hit the alternatives field.
+
+### Task 193: File-pull discoverability
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Documented bundle plus read and grep tools for big task files.
+
+### Task 194: Compaction plus traceability
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Long transcripts compact to a digest with per-record metadata.
+
+### Task 195: Machine verdicts plus rules gate
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** QA ends with a parseable verdict block checked before any judge call.
+
+### Task 196: Loop guard
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Repeating identical diffs halt the loop instead of burning turns.
+
+### Task 197: Replay harness
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Added hash-scored golden replay for prompt regression checks.
+
+### Task 198: Error taxonomy
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Split retryable failures from fatal client errors on both servers.
+
+### Task 199: Persona and fintech research
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Evidence-grounded surgical edits, no new persona added.
+
+### Task 200: Full task-file attach
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Brain always sees whole task working content minus the diff block.
+
+### Task 201: QA hunks plus modes doc
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** QA and reviewer turns carry the actual diff plus manual versus autopilot docs.
+
+### Task 202: Planning gate
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** No implementation code without a recorded Brain plan.
+
+### Task 203: Self-judgment run
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** System judged itself and fixed the empty-output flake live.
+
+### Task 204: Self-judgment fixes
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Fixed persona overlap and trimmed redundant coverage.
+
+### Task 205: Nine-note cleanup
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Purged pause leftovers and dead docs in one autopilot run.
+
+### Task 206: Systemd unit env docs
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Daemon now reads the repo env file, documented for setup.
+
+### Task 207: Release v9.31.0 with push script
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Cut MINOR 9.31.0 with sync proof and a ready manager-run push script.
```
<!-- END_GIT_DIFF -->
