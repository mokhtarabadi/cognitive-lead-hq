# Task 326: Release v9.62.0 with milestone-23 archive

**File:** `tasks/qa/326-release-v9-62-0-with-milestone-23-archive.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Cut release v9.62.0 (MINOR: new lint gates, Technical-Terms behavior, bundle hardening) with milestone-23 archive of all completed tasks, per release/release-workflow memory.

## Manager's Notes

Direct order: "make a release, load everything from memory about new release, step by step follow them". Release memory retrieved and followed: skills loaded (versioning-and-release, project-memory, verification-before-completion, task-lint, archive-tasks, task-generator), SemVer confirmed MINOR (new workflow capabilities, non-breaking), archive-on-release enforced, CHANGELOG Parse-Then-Append with empty Unreleased after release, system-prompt bump plus reassemble, full verification gates, ZAC-safe push script at /tmp/cognitive-lead-push-release.sh for manual Manager execution.

Scope: bump `prompts/fragments/01-system_version.md` 9.61.1 to 9.62.0, update `tests/test_prompt_sync.py` version pin, reassemble `system-prompt.md`, move Unreleased entries under `## [9.62.0]`, archive 31 completed tasks (284-325) with `docs/history/milestone-23-summary.md` via archive-tasks skill, generate push script, run all gates.

## Local TODOs

- [x] Archive completed tasks with milestone-23 summary (archive-tasks skill)
- [x] Bump system version fragment and reassemble prompt
- [x] Move CHANGELOG Unreleased entries under 9.62.0 header
- [x] Update version pin in tests and run full verification gates
- [x] Generate push script at /tmp/cognitive-lead-push-release.sh
- [x] Verify functionality

## Acceptance Criteria

- [x] `tasks/completed/` empty after archive; `docs/history/milestone-23-summary.md` exists; sources in `tasks/archive/`
- [x] `system-prompt.md` carries 9.62.0, sync green, byte-identical rebuild
- [x] `CHANGELOG.md` has `## [9.62.0]` with all entries; `## [Unreleased]` empty
- [x] Push script exists at /tmp/cognitive-lead-push-release.sh, executable, starts with `set -euo pipefail`, never executed by Hands
- [x] All verification gates green (lint_task_file, lint_markdown, lint_system_prompt_sync, py_compile, full pytest, check_docs_sync.py)

## Verification Evidence

- **Test command:** rtk test uv run tests/test_prompt_sync.py -q
- **Expected result:** all prompt sync checks pass with version 9.62.0
- **Actual result:** exit 0, 14 checks pass, byte-identical rebuild confirmed
- **Exit code:** 0
- **Test command:** cd mcp-context-server && uv run --with pytest python -m pytest ../tests/test_bundle_tasks.py -q
- **Expected result:** 18 passed
- **Actual result:** exit 0, 18 passed
- **Exit code:** 0
- **Test command:** ls tasks/completed/ | wc -l; ls tasks/archive/ | wc -l; ls -l docs/history/milestone-23-summary.md
- **Expected result:** completed 0, archive grown by 31, summary exists
- **Actual result:** completed 0, archive 318 files, milestone-23-summary.md present (4763 bytes)
- **Exit code:** 0
- **Test command:** lint_task_file (task) + lint_markdown (01-system_version, CHANGELOG, milestone-23-summary) + lint_system_prompt_sync
- **Expected result:** all lint tools pass
- **Actual result:** all five lint calls pass
- **Exit code:** 0
- **Test command:** ls -l + head -2 + bash -n /tmp/cognitive-lead-push-release.sh (never executed)
- **Expected result:** executable, strict-mode header, syntax valid
- **Actual result:** -rwxrwxr-x, #!/usr/bin/env bash + set -euo pipefail, bash -n exit 0
- **Exit code:** 0
- **Test command:** python3 -m py_compile (6 files) + python3 scripts/check_docs_sync.py
- **Expected result:** both exit 0
- **Actual result:** PY_OK, docs-sync OK
- **Exit code:** 0
- **Test command:** full suite minus test_mcp_servers via context-server locked env
- **Expected result:** all green; test_mcp_servers excluded (53 environmental + 1 pre-existing split failure, also failing on pristine HEAD)
- **Actual result:** exit 0, 440 passed
- **Exit code:** 0
- **Stack-skill binding:** root=. markers=[package.json, go.mod, pyproject.toml server, build.gradle.kts] matched=[] reason=no app stack skill matches release plus MCP verification

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Archiving 31 tasks in one move; a missed file breaks traceability.
- **Rollback plan:** Revert via git (no commits until closure approval); re-run ID discovery if needed. Never purge archive until META/release reaches completed.

---

## Execution Log & Reasoning

Seat Check: release procedure, single domain, requested Software Architect; skipped Designer (no user-visible surface) and Senior Programmer (mechanical file ops spelled out in XML). Brainstorm: not required — procedure fully specified by release-workflow memory plus Manager order, reversible until closure.
Fed-context: `prompts/fragments/01-system_version.md:1` (9.61.1 → 9.62.0), `tests/test_prompt_sync.py:47` (pin updated), `system-prompt.md:1` (assembled 9.62.0), `CHANGELOG.md:7-9` (Unreleased empty, 9.62.0 header 2026-10-19), `docs/history/milestone-23-summary.md` (new, 31 tasks), `/tmp/cognitive-lead-push-release.sh` (executable, syntax valid, never executed).
Archive: 31 files git-moved tasks/completed/ → tasks/archive/, completed/ verified empty. Sibling docs inspected: prompts/fragments, tests, scripts, docs READMEs/DECISIONS carry no contract change for a version bump — logged no-change. test_mcp_servers excluded from blocking gates: 53 environmental failures (missing pathspec/yaml in lint env) plus 1 split round-trip failure, all reproduced on pristine HEAD worktree. Assumption A1: MINOR (not PATCH) because new lint gates plus Technical-Terms behavior plus bundle hardening are new workflow capabilities, non-breaking.
Hotfix (QA_REJECTED evidence gap): recorded archive counts (completed 0, archive 318), lint triple green via MCP tools, push script checks (executable, strict header, syntax valid, never executed), py_compile plus docs-sync green, full suite 440 green; DoD boxes checked against this evidence. No release logic redone.
Re-QA: QA_PASSED — archive proven, pins consistent, CHANGELOG correct, lint triple green, script plus docs gates green, 440 suite green with justified exclusion, DoD closed. Re-review: APPROVED with PO_REVIEW_PENDING, no blocking issues, no follow-ups.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index de8ac8f..69e8818 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,7 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.62.0] - 2026-10-19
+
 ### Added
+
 - **English technical terms in non-English handoffs (Task 325):** `prompts/fragments/24-language_policy.md` gains a Technical-Terms rule (file paths, tool names, XML tags, identifiers, Kanban lanes, verdict literals stay English in backticks, approval literals matched English-only); `agents/cognitive-executor.md` and `prompts/fragments/20-communication_examples.md` carry the same rule with a correct versus transliterated example; all Persian and Farsi mentions in operating instructions (fragments 05, 13, 20, 24, executor, `docs/conventions.md`, `AGENTS.md`, both Telegram and bundle skill templates, `README.md`, `mcp-context-server/gitops.py` docstring) generalized to non-English and requested language; `system-prompt.md` rebuilt.
 - **Unactionable skill references fixed (same task):** five Brain-owned fragment lines reworded with explicit Hands actors and Orchestrator no-tool boundaries (05 gate plus parenthetical, 24 gating, 11 Deep Research Loop routed to Hands, 21 task-generator actor); zero prompt growth.
 - **Lint mechanically catches the new bug classes (same task):** `_check_unactionable_skill_verbs` in `lint_markdown` (fragment-scoped) and `lint_system_prompt_sync`, plus `_check_bundle_meta_structure` (META-only) in `lint_task_file`.
diff --git a/docs/history/milestone-23-summary.md b/docs/history/milestone-23-summary.md
new file mode 100644
index 0000000..0fb26e6
--- /dev/null
+++ b/docs/history/milestone-23-summary.md
@@ -0,0 +1,53 @@
+# Milestone 23 Summary
+
+**Date:** 2026-10-19
+**Tasks Compacted:** 31
+
+## Source Distribution
+
+| Source       | Count |
+| ------------ | ----- |
+| orchestrator | 3     |
+| manager      | 28    |
+
+## Architectural Changes
+
+This milestone rebuilt the Brain bridge and the compaction stack, then hardened language, lint, and bundling on top. Tasks **285–293** made the bridge session-first and lean: a context-sufficiency pack on every planning turn (**285**), singleton report paths under the caller project root (**286**), Magic Compact adoption (**287**) replaced by our V2-native smart-compact plugin (**288**) with an agent-callable `compact_context` tool (**289**), the todolist plugin (**290**), truncated-XML server-side recovery (**291**), the lean session-first refactor (**292**), V2 session-monorepo sync (**293**), session-propagation fixes (**295**), retirement of manager-decision wiring (**296**) and goal-plugin wiring (**297**), the minimal-core simplification (**298**), and a full-brainstorm self-judgment (**299**). Task **12** added the night-mode workflow fragment from the overnight autopilot run.
+
+The META **305** shipped the anti-hallucination harness (bundling 300–304). Tasks **306–307** established Living Folder Docs (README + dated DECISIONS per slice, wired into conventions, fragments, and the executor). The META **313** shipped the unified code-plus-SQL-plus-Markdown knowledge graph (bundling 308–312). Task **314** modularized the context server and enforced ruff formatting. Task **315** made `stage_and_inject_diff` index-safe (`skip_add`, pre-staged warning, `unstage_files`). Tasks **316–317** fixed the Brain bare-XML contract and added the pre-send token budget guard. Task **318** integrated the goal and smart-compact plugins, **319** documented the free-tier bash gate, **321** ran the cognitive tune-up round, **322** set the English-inside language policy, **323** registered project-local skills in AGENTS.md, and **324** synced the goal-tools spec.
+
+The keystone META **325** generalized every Persian/Farsi mention to non-English/requested-language, fixed five unactionable skill references with explicit Hands actors at zero prompt growth, added mechanical lint gates (skill-verb + META-shape), and fixed ten bundle_tasks defects with red-proof tests. Task **284** was the v9.49.0 release ceremony archiving milestone-22.
+
+## Files Modified
+
+| File | Change |
+| ---- | ------ |
+| `docs/history/milestone-23-summary.md` | new: this 31-task compaction (284–325) |
+| `tasks/archive/284-*.md` … `tasks/archive/325-*.md` | released tasks moved to archive (326) |
+| `CHANGELOG.md` | 9.62.0 release block (326); [Unreleased] entries (321–325) |
+| `prompts/fragments/01-system_version.md` | 9.61.1 → 9.62.0 (326) |
+| `prompts/fragments/24-language_policy.md` | Technical-Terms rule (325); skill-actor reword (325) |
+| `prompts/fragments/20-communication_examples.md` | non-English handoff example (325) |
+| `prompts/fragments/05-user_input_processing.md` | Orchestrator-scoped no-tool boundary (325) |
+| `prompts/fragments/11-execution_workflow.md` | Deep Research Loop routed to Hands (325) |
+| `prompts/fragments/21-self_improvement_protocol.md` | Hands actor for task-generator (325) |
+| `prompts/fragments/13-constraints.md` | non-English wording (325) |
+| `agents/cognitive-executor.md` | Technical-Terms + no-tool boundary (325) |
+| `docs/conventions.md`, `AGENTS.md`, `README.md` | non-English generalization (325) |
+| `skill-templates/telegram-issue-sync/SKILL.md` | non-English wording (325) |
+| `skill-templates/bundle-tasks/SKILL.md` | non-English wording + 2-6 floor + duplicate errors (325) |
+| `mcp-context-server/gitops.py` | Unicode docstring + locate/collision/checksum/status fixes (325) |
+| `mcp-context-server/server.py` | atomic bundle write + rollback restore + validation (325) |
+| `mcp-lint-server/server.py` | skill-verb + META-shape gates (325) |
+| `mcp-brain-bridge/*` | session-first lean refactor + budget guard (285–298, 317) |
+| `mcp-context-server/*` | singleton paths, modularization, graph, index-safe staging (286, 313–315) |
+| `system-prompt.md` | regenerated each bump through 9.62.0 (326) |
+| `tests/test_bundle_tasks.py` | 11 red-proof tests, 18 green (325) |
+| `tests/test_prompt_sync.py` | version pin 9.62.0 (326) |
+
+## Test Evidence
+
+- `test_prompt_sync.py`: 14 checks green, byte-identical rebuild.
+- `test_bundle_tasks.py`: 18 passed (7 baseline + 11 new, 9-failed red proof recorded).
+- `test_mcp_servers.py`: 34 passed; 53 environmental failures (missing pathspec/yaml in lint env) + 1 split round-trip failure, all pre-existing on pristine HEAD — not gating.
+- Residual greps: zero Persian/Farsi and zero unactionable skill verbs in operating prose.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 58fc94d..be746d6 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.61.1</system_version>
+<system_version>9.62.0</system_version>
diff --git a/system-prompt.md b/system-prompt.md
index 04eeac2..9c914a8 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.61.1</system_version>
+<system_version>9.62.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 34c43f1..72b3bfc 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.61.1"
+    assert shipped == "9.62.0"
 
 
 def test_compaction_protocol_in_shipped_prompt():
```
<!-- END_GIT_DIFF -->
