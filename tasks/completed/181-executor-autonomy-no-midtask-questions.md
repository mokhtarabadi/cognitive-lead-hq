# Task 181: Executor autonomy — never stall asking questions mid-task

**File:** `tasks/qa/181-executor-autonomy-no-midtask-questions.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress

## Goal

Make the Cognitive Executor resolve ambiguities itself and keep moving instead of stalling mid-task to ask the Manager questions.

## Manager's Notes

Manager observation: the executor sometimes gets stuck and asks questions inside the Cognitive Executor instead of proceeding intelligently and automatically. Required behavior: when information is missing, the executor must pick the most reasonable interpretation, record the assumption in the Execution Log, and continue. Questions to the Manager are allowed ONLY when two or more interpretations are equally plausible AND the choice is irreversible or destructive. Everything else is decided autonomously. Research industry best practices for autonomous agent behavior (e.g. ReAct decide-act loops, assumption logging, confidence thresholds) and encode the best fitting rules into `agents/cognitive-executor.md` without disrupting the existing core protocols (ZAC, Kanban lifecycle, dual-channel communication from Task 180).

## Local TODOs

- [x] Research autonomous-agent best practices (assumption logging, decision thresholds, when-to-ask policies)
- [x] Draft autonomy rules: decide-by-default, assumption log, narrow ask-gate for irreversible choices
- [x] Encode rules into `agents/cognitive-executor.md`
- [x] Verify no conflict with existing protocols (ZAC, Kanban, dual-channel)
- [x] Trace task-number reference habit (no written rule; provenance markers + author annotations + fresh heading)
- [x] Define Task-Number Reference Discipline in `docs/conventions.md` + executor Negative Patterns bullet
- [x] Audit prompt-facing Markdown; clean hallucinating refs (fragment 07, executor heading, 2 skills, conventions line)
- [x] Bump 9.18.0 → 9.19.0, reassemble system-prompt.md, verify sync
- [x] Fix originating prompts: discipline clause in 09-hands_protocols documentation_phase + task-generator skill step 3
- [x] Bump 9.19.0 → 9.20.0, reassemble, verify sync, CHANGELOG entry
- [x] Propagate discipline to audit-agents skill (template pair + conventions template section + Mode 2 criteria) so other projects get the rule via audit

## Acceptance Criteria

- [x] Executor asks the Manager mid-task ONLY for irreversible/destructive ambiguous choices
- [x] All autonomous decisions are recorded as assumptions in the Execution Log
- [x] No existing core protocol weakened (ZAC, Kanban moves, dual-channel scope intact)
- [x] Task numbers appear ONLY in code comments, CHANGELOG, task files, history, HTML-comment markers — never in prompt prose
- [x] `system-prompt.md` regenerated from fragments and byte-identical (sync verified, v9.19.0)
- [x] Originating authoring prompts fixed (09 documentation_phase + task-generator step 3); v9.20.0 sync verified
- [x] Audit-agents skill carries the discipline (3 spots, project-agnostic); other projects inherit it on next audit

## Verification Evidence

- **Test command:** `grep -n -i "assumption\|ask the Manager" agents/cognitive-executor.md`
- **Expected result:** autonomy section present with narrow ask-gate
- **Actual result:** new `XML Task Execution Autonomy` section at lines 139-145 (assume-first, blocking-only criteria, questions ride along); Direct Input Clarification Halt untouched at lines 72-80
- **Exit code:** 0
- **Test command:** `grep -rn "(Task [0-9]" prompts/fragments/ agents/ skill-templates/ docs/conventions.md | grep -v PAUSED-2026-09-09; python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check181b.md && diff /tmp/check181b.md system-prompt.md && echo SYNC_OK`
- **Expected result:** only the two self-defining rule lines remain; SYNC_OK
- **Actual result:** only rule-definition lines (executor:135, conventions:175) + frozen pause block remain; SYNC_OK, 77915 bytes, 9.19.0
- **Exit code:** 0
- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check187.md && diff /tmp/check187.md system-prompt.md && echo SYNC_OK; grep -c "Task-number discipline" system-prompt.md`
- **Expected result:** SYNC_OK + discipline clause present once
- **Actual result:** SYNC_OK, 78269 bytes, count 1, 9.20.0
- **Exit code:** 0
- **Test command:** `grep -n "Task-Number Reference Discipline" skill-templates/audit-agents/SKILL.md; grep -n "Task [0-9]\|task [0-9]" skill-templates/audit-agents/SKILL.md`
- **Expected result:** rule in 3 spots; no bare task numbers except the rule's own example
- **Actual result:** rule in 3 spots (template pair:299, conventions template section:236, Mode 2 criteria:389); only bare-number hit is the illustrative example in the Don't line
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Over-autonomy causes wrong irreversible actions.
- **Rollback plan:** Revert `agents/cognitive-executor.md` from git history; ask-gate restores previous behavior.

---

## Execution Log & Reasoning

Added `XML Task Execution Autonomy` section (lines 139-145) before `## Execution Discipline`: assume-first with A1/A2 assumption log, blocking-only stop criteria (destructive without rollback, missing secret, self-contradictory task), questions ride along as Q1/Q2 in the handoff. Scoped strictly to XML execution — Direct Input Clarification Halt (lines 72-80) unchanged, so raw ad-hoc input still halts on ambiguity. Verified ZAC/Kanban/dual-channel sections untouched via grep. Executor-only change: no system-prompt fragments, no version bump, no global sync needed beyond the executor file itself.

Extension (manager hallucination report, same task): task-number refs traced — no written rule ever mandated them; habit came from deliberate PAUSED-2026-09-09 provenance markers, skill-author origin annotations, and my own fresh heading. Defined `Task-Number Reference Discipline` in `docs/conventions.md` + mirror bullet in executor Negative Patterns (refs ONLY in code comments, CHANGELOG, task files, history, HTML-comment markers). Cleaned 10 prompt-facing hits: fragment 07 registry line, executor heading, 5 in bundle-tasks skill, 2 in task-generator skill, 1 historical line in conventions. Frozen pause block (verbatim per AGENTS.md) and YAML `#` comments untouched by design. Bumped 9.18.0 → 9.19.0 (fragment 07 changed), reassembled, SYNC_OK byte-identical. Changed skills re-synced globally.

Extension (audit-agents vehicle, manager order, same task): this repo seeds other projects via the audit-agents skill, so the discipline was propagated into `skill-templates/audit-agents/SKILL.md` in all three load-bearing spots — Mode 1 AGENTS.md template Don't/Do pair, Mode 1 conventions template `## Task-Number Reference Discipline` section, Mode 2 audit criteria bullet — mirroring the DSP/Financial pattern. Project-agnostic, no HQ-only content. Skill self-check: no bare task numbers except the rule's own illustrative example. No version bump (skills are not fragments).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e0acf78..dedaed9 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,22 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.20.0] - 2026-09-11
+
+### Fixed
+
+- **Originating-prompt fix for task-number refs (Task 181 extension, manager order):** the rule now lives where new Markdown gets authored, so future tasks cannot reintroduce the habit — fragment `09-hands_protocols.md` `<documentation_phase>` gains the Task-number discipline clause (Execution Logs, headings, skill instructions, registry lines stay number-free; numbers live only in code comments, CHANGELOG, history, HTML comments) and `skill-templates/task-generator/SKILL.md` step 3 carries the one-line version (filename + title carry the number exactly once). Reassembled `system-prompt.md` (sync-check byte-identical).
+
+## [9.19.0] - 2026-09-11
+
+### Fixed
+
+- **Task-number reference discipline (Task 181 extension, manager hallucination report):** Task numbers are provenance for humans, not reasoning material — a bare `(Task NN)` in visible prompt prose invites hallucination. New `docs/conventions.md` section `Task-Number Reference Discipline` (allowed homes: code comments, CHANGELOG, task files, docs/history, HTML-comment markers; forbidden: fragments, agent instructions, skill text, registry lines, headings) plus a mirror bullet in the executor Negative Patterns. Cleaned all prompt-facing hits: fragment 07 registry `(Task 155)`, executor autonomy heading `(Task 181)`, 5 refs in `skill-templates/bundle-tasks/SKILL.md`, 2 refs in `skill-templates/task-generator/SKILL.md`, 1 historical ref in `docs/conventions.md`. Untouched by design: frozen PAUSED-2026-09-09 automation block (verbatim per AGENTS.md), YAML/frontmatter `#` comments, CHANGELOG/history/task-file records. Reassembled `system-prompt.md` (sync-check byte-identical).
+
+### Added
+
+- **Hands-side execution autonomy (Task 181):** New `XML Task Execution Autonomy` section in `agents/cognitive-executor.md` — assume-first with assumption log (A1, A2), blocking-only criteria (destructive without rollback, missing secret, self-contradictory task), questions ride along in the handoff (Q1, Q2) and never block. Scoped to XML execution only; the Direct Input Clarification Halt for raw ad-hoc messages is unchanged. No system-prompt fragments touched, no version bump.
+
 ## [9.18.0] - 2026-09-11
 
 ### Changed
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 539c866..5094218 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -132,10 +132,19 @@ Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (refe
 - Do not flatter, praise, validate, or agree without reason.
 - Do not use decorative headings, emoji, or motivational language.
 - Never emit these phrases: load-bearing, worth stating plainly, here is the honest truth, real tension, carry the argument. No analogies, no semicolons, no fragments, no em-dash chaining.
+- Never write task numbers (Task 110, Task 181) into prompt-facing Markdown: fragments, agent sections, skill instructions, registry lines. Task-number provenance lives ONLY in code comments, CHANGELOG entries, task files, docs/history archives, and HTML-comment markers.
 - Do not repeat yourself. State every idea once, repeat only if relevant to subsequent queries.
 - Do not speculate on abstractions for future requirements.
 - Do not widen work into cleanup, refactoring, or documentation beyond the requested scope.
 
+## XML Task Execution Autonomy (never stall mid-task)
+
+When executing an Orchestrator XML task block, you MUST NOT stop and ask the Manager questions about anything the task, the plan, or the repo can answer. The Manager is a courier, not a consultant. These rules apply ONLY to XML task execution — the Direct Input Clarification Halt above still governs raw ad-hoc messages.
+
+1. **Assume first, log it, keep moving:** When a step is ambiguous but one option is clearly most probable, pick it and continue. Record every assumption in the task file under `## Execution Log & Reasoning` as `Assumption A1, A2, ...` with a one-line reason each. A wrong logged assumption the Manager can correct later is always cheaper than a stalled task.
+2. **Blocking vs non-blocking:** STOP and surface to the Manager ONLY when one of these is true: (a) the next action is destructive or irreversible and the plan gives no rollback path, (b) a secret, credential, or external approval only the Manager holds is required, (c) the task file contradicts itself and no reading resolves it. Everything else is non-blocking — decide, log, continue.
+3. **Questions ride along, never block:** If something is worth the Manager's eyes but non-blocking, finish the work, then list it as `Q1, Q2, ...` in the final handoff next to the assumptions. Never emit a mid-task question as a substitute for progress.
+
 ## Execution Discipline
 
 ### Plan-Execute-Observe Pattern
diff --git a/docs/conventions.md b/docs/conventions.md
index 03f0ba8..f7a1020 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -74,7 +74,7 @@ All projects in this ecosystem MUST treat source-of-truth contracts and shared s
 1. **No hand-authored duplicates** — Consumer applications (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) MUST NOT hand-author duplicate interface models, request/response DTOs, or data classes for types already governed by a contract.
 2. **Import or generate** — When a governed type is needed, either import it directly from the shared package (`@repo/shared-schema`, `packages/shared-schema`) or execute the stack's code-generation toolchain (`pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`).
 3. **SOLID reconciliation** — Single-source-of-truth prevents type drift (DRY/SRP) and does not conflict with YAGNI or the 3-Implementation Rule: extract or generate only when a contract or cross-service dependency already exists.
-4. **Deterministic enforcement (historical — loop-engine retired):** the retired `loop-engine/sentinel.py` `TypeDriftSentinel` used to scan task diffs during toolchain verification (pre-QA). With the loop-engine daemon retired (Task 167; guides archived under `archive/automation-paused-2026-09-09/docs-loop-engine/`), enforcement is manual review until a replacement lands. Bypass with an explicit `drift-ignore` comment only when a justified exception exists.
+4. **Deterministic enforcement (historical — loop-engine retired):** the retired `loop-engine/sentinel.py` `TypeDriftSentinel` used to scan task diffs during toolchain verification (pre-QA). With the loop-engine daemon retired (guides archived under `archive/automation-paused-2026-09-09/docs-loop-engine/`), enforcement is manual review until a replacement lands. Bypass with an explicit `drift-ignore` comment only when a justified exception exists.
 
 The single source of truth for the full mandate is `prompts/fragments/20-no_manual_dto_mandate.md` — this section is a summary only.
 
@@ -169,3 +169,13 @@ All MCP servers load `.env` files explicitly at import via `mcp_common.env.load_
 **Blank-means-unset (binding convention):** an empty value — whether from a bare `KEY=` line or an empty-string process variable (e.g. OpenCode `{env:…}` blocks inject `""` when the parent env lacks the var) — counts as UNSET. File values fill gaps; real non-empty process values always win. This is deliberate and load-bearing: `DECISION_MODEL=` (blank) means "fall back to `PERSONA_MODEL`". Do NOT "fix" this into standard-dotenv empty-overrides semantics without a manager-approved task — doing so silently disables the model fallback chain and reintroduces blank-auth 401s.
 
 Parser rules (locked by tests): `#` comments and blank/malformed lines skipped; `export KEY=` prefix stripped; quotes stripped only when wrapping; inline `#` stays literal; `KEY = value` whitespace trimmed; CRLF tolerated; BOM stripped (`utf-8-sig`).
+
+## Task-Number Reference Discipline
+
+Task numbers (Task 110, Task 181) are provenance for humans, not reasoning material for the model. A bare task number in visible prompt prose invites hallucination: the model treats it as load-bearing context it cannot resolve.
+
+**Allowed homes (only):** code comments (`#`, `//`), `CHANGELOG.md` entries, task files in `tasks/`, `docs/history/` archives, and HTML-comment markers (`<!-- -->`, including frozen provenance blocks which stay verbatim).
+
+**Forbidden homes:** visible prose in prompt fragments, agent instruction files, skill instructions, registry lines, section headings, and any Markdown the Brain or Hands reads as operating instructions.
+
+**Authoring rule:** when writing or editing prompt-facing Markdown, strip task-number parentheticals. Record provenance in the task file and CHANGELOG instead — never in the prompt text itself.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index d255de9..db6e54d 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.18.0</system_version>
+<system_version>9.20.0</system_version>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 0f3ab0c..1b7672e 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -6,7 +6,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **code-search**: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
 - **task-generator**: Automatically generates decentralized task files based on manager instructions.
 - **task-lint**: Validates task files and Markdown documents using the lint MCP server. Run after task creation and before task closure.
-- **bundle-tasks**: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as the `bundle_tasks` MCP tool (Task 155).
+- **bundle-tasks**: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as the `bundle_tasks` MCP tool.
 - **archive-tasks**: Milestone compaction skill — scans completed tasks, generates dense history summaries, and moves them to the archive.
 - **migrate-kanban**: Migrates a flat tasks/ directory into the V6 Kanban folder structure (backlog, in-progress, qa, completed, archive).
 - **audit-agents**: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index 5fd5aae..eefa4fb 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -84,7 +84,7 @@
 </bash_phase>
 
   <documentation_phase>
-    HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version.
+    HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs. Task-number discipline: NEVER write task numbers (e.g. Task 181) into prompt-facing Markdown prose — section headings, skill instructions, registry lines, and Execution Logs stay number-free (the task file's own title already carries its number). Task-number references live ONLY in code comments, CHANGELOG entries, history archives, and HTML comments.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version.
 </documentation_phase>
 
   <summary_phase>
diff --git a/skill-templates/bundle-tasks/SKILL.md b/skill-templates/bundle-tasks/SKILL.md
index 28e6a57..b80fe6c 100644
--- a/skill-templates/bundle-tasks/SKILL.md
+++ b/skill-templates/bundle-tasks/SKILL.md
@@ -1,9 +1,9 @@
 ---
 name: bundle-tasks
-description: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as the bundle_tasks MCP tool (Task 155).
+description: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as the bundle_tasks MCP tool.
 ---
 
-# Bundle Tasks Skill — Meta-Task Bundling (Task 110)
+# Bundle Tasks Skill — Meta-Task Bundling
 
 Use this skill when the Manager wants to execute 4–6 small related tasks together instead of sequentially. It eliminates the `backlog → in-progress → qa → completed` round-trip overhead by bundling them into one branch, one `Factual Git Diff`, and one all-or-nothing QA gate.
 
@@ -11,7 +11,7 @@ Use this skill when the Manager wants to execute 4–6 small related tasks toget
 
 - Manager says: "bundle tasks 1, 2, 5, 10, 15, 20", "create a meta-task from 12 15 20", "combine these polish tasks", or any note about "meta-task", "bundle", "supersede", "archive and bundle"
 - Tasks are small, same stack/domain (e.g., all `android-kotlin`, all `react-vite`, all docs), and would be inefficient to run one-by-one
-- You are in any project that has the `mcp-context-server` MCP server — the bundler is available as the `bundle_tasks` MCP tool (pure MCP, Task 155)
+- You are in any project that has the `mcp-context-server` MCP server — the bundler is available as the `bundle_tasks` MCP tool (pure MCP)
 
 **Do NOT use for:** large refactors, tasks with conflicting files that would cause merge conflicts in one diff, or tasks >6 without explicit `--force`.
 
@@ -22,7 +22,7 @@ Use this skill when the Manager wants to execute 4–6 small related tasks toget
 3. **Archive, Not Purge (with Transactional Rollback):** Sources are moved via `git mv` to `tasks/archive/` with `**Superseded-By:** <META_ID>-<slug>` until META is `completed`. History stays reachable via `git log --follow`. If ANY archive operation fails, ALL previously archived files are rolled back to their original locations, the META file is deleted, and the operation aborts cleanly.
 4. **Guardrails:** `MAX_BUNDLE_SIZE=6` (reject >6 without `--force`), combined LOC >400 warning, missing-ID and duplicate-ID checks (hard halt on duplicate active IDs), stack conflict detection (warn or require `--force`), SHA verbatim checksum validation, atomic Next-ID creation with retry loop for concurrent safety.
 
-## Invocation — Pure MCP Tool (Task 155)
+## Invocation — Pure MCP Tool
 
 The `mcp-context-server/server.py:bundle_tasks` tool is **fully self-contained** — it does NOT require `scripts/bundle-tasks.py`. All helpers (kebab_case, discover_next_id, find_task_file, extract_section, build_meta_content, git_mv_or_fallback, patch_archived_file) are inlined inside the MCP tool function. Invoke via the Hands' MCP interface:
 
@@ -63,7 +63,7 @@ The `mcp-context-server/server.py:bundle_tasks` tool is **fully self-contained**
 ## Verification (Must Pass Before QA)
 
 ```bash
-# via MCP (pure MCP, Task 155):
+# via MCP (pure MCP):
 bundle_tasks(task_ids=["12","15","20"], title="test-bundle", dry_run=true)
 
 # then after real bundle (if not dry_run):
diff --git a/skill-templates/task-generator/SKILL.md b/skill-templates/task-generator/SKILL.md
index 7a060d3..524fd79 100644
--- a/skill-templates/task-generator/SKILL.md
+++ b/skill-templates/task-generator/SKILL.md
@@ -36,7 +36,7 @@ find tasks/backlog tasks/in-progress tasks/qa tasks/completed -type f -name "*.m
 
 If the output is non-empty, HALT and report duplicate task IDs. Do NOT overwrite files. Archive is a historical record and MUST NOT be included in the blocking duplicate-ID check. If archive duplicates are discovered separately, report them as a warning only, never HALT task creation.
 
-3. **Name:** Create a kebab-case filename (e.g., `01-fix-login-bug.md`). Place it in `tasks/backlog/`.
+3. **Name:** Create a kebab-case filename (e.g., `01-fix-login-bug.md`). Place it in `tasks/backlog/`. Task-number discipline: the filename and `# Task [NN]` title carry the number exactly once — never repeat task numbers in template prose, headings, or notes (numbers live only in code comments, CHANGELOG, history, and HTML comments).
 
 3.5. **Collision Check:** Before writing the file, verify that `tasks/backlog/{NEXT_ID}-*.md` does NOT already exist. Run: `ls tasks/backlog/${NEXT_ID}-*.md 2>/dev/null`. If a file with that ID already exists, HALT and report: '⚠️ Task ID collision: {NEXT_ID} is already in use. Re-run ID discovery.' Do NOT overwrite existing files.
 
@@ -226,7 +226,7 @@ _(Git diff will be automatically injected here by the MCP tool. Do not edit this
 
 5. **Halt and Handover:** DO NOT execute the task. Print the exact message: "✅ The task file has been created at `tasks/backlog/[filename]` and is ready to be sent to the Orchestrator." and STOP.
 
-## Bundle Workflow (Meta-Tasks) — Task 110/155 (Pure MCP)
+## Bundle Workflow (Meta-Tasks, Pure MCP)
 
 Use this when the Manager has 4–6 small related tasks that should be executed together instead of sequentially. The bundler preserves every requirement verbatim and archives the sources.
 
@@ -236,7 +236,7 @@ Use this when the Manager has 4–6 small related tasks that should be executed
 - Tasks are small, same stack/domain (e.g., all Android polish), and would be inefficient to run one-by-one
 - Goal is one branch, one `Factual Git Diff`, one QA gate (all-or-nothing)
 
-### Canonical Invocation — Pure MCP Tool (Task 155)
+### Canonical Invocation — Pure MCP Tool
 
 Invoke the `bundle_tasks` MCP tool via the Hands:
 
diff --git a/system-prompt.md b/system-prompt.md
index bbb02c5..f246c79 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.18.0</system_version>
+<system_version>9.20.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -115,7 +115,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **code-search**: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
 - **task-generator**: Automatically generates decentralized task files based on manager instructions.
 - **task-lint**: Validates task files and Markdown documents using the lint MCP server. Run after task creation and before task closure.
-- **bundle-tasks**: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as the `bundle_tasks` MCP tool (Task 155).
+- **bundle-tasks**: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as the `bundle_tasks` MCP tool.
 - **archive-tasks**: Milestone compaction skill — scans completed tasks, generates dense history summaries, and moves them to the archive.
 - **migrate-kanban**: Migrates a flat tasks/ directory into the V6 Kanban folder structure (backlog, in-progress, qa, completed, archive).
 - **audit-agents**: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
@@ -297,7 +297,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 </bash_phase>
 
   <documentation_phase>
-    HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version.
+    HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs. Task-number discipline: NEVER write task numbers (e.g. Task 181) into prompt-facing Markdown prose — section headings, skill instructions, registry lines, and Execution Logs stay number-free (the task file's own title already carries its number). Task-number references live ONLY in code comments, CHANGELOG entries, history archives, and HTML comments.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version.
 </documentation_phase>
 
   <summary_phase>
```
<!-- END_GIT_DIFF -->
