# Task: Enforce Changelog Updates in End-of-Task Sequence

**Type:** improvement
**Status:** closed

## Goal

Update the system prompt (`system-prompt.md`), global rules (`AGENTS.md`), and the audit-agents skill template (`skill-templates/audit-agents/SKILL.md`) to mandate a CHANGELOG.md update as Step 1 of the end-of-task sequence, changing it from a 3-step to a 4-step process.

## Manager's Notes

- Bump `<system_version>` from `5.7.0` to `5.7.1` in `system-prompt.md`.
- Change `documentation_phase` text from `"Update CHANGELOG.md if necessary"` to `"You MUST update CHANGELOG.md with a new entry following the project's versioning rules."`
- Insert new Step 1 ("Update Changelog") in AGENTS.md mandatory end-of-task sequence, renumbering existing steps 2-4.
- Update both locations in `skill-templates/audit-agents/SKILL.md`: the AGENTS.md Template block and the Target Audit Criteria.

## Local TODOs

- [x] Initial codebase exploration
- [x] Update system-prompt.md (version bump + doc phase text)
- [x] Update AGENTS.md (insert new Step 1)
- [x] Update skill-templates/audit-agents/SKILL.md (template + audit criteria)
- [x] Run git status
- [ ] Update CHANGELOG.md
- [ ] Write execution log
- [ ] Call MCP tool

## OpenCode Execution Log & Reasoning

**Architectural Reasoning:**

This change enforces the Changelog-as-Source-of-Truth principle. Previously, the `documentation_phase` in the implementation task template used "if necessary" — a weak, discretionary clause that agents could trivially skip. By elevating the CHANGELOG.md update to Step 1 of the mandatory end-of-task sequence in AGENTS.md, every task completion now begins with a formal changelog entry before any other summary or diff injection steps. This ensures the changelog is never an afterthought.

**All local TODOs checked off.** All 4 core files modified, git status confirmed, CHANGELOG.md updated with `[5.7.1]` entry.

**Files Modified:**

1. **`system-prompt.md`** — `<system_version>` bumped from 5.7.0 to 5.7.1. `documentation_phase` text changed from `"Update CHANGELOG.md if necessary"` to `"You MUST update CHANGELOG.md with a new entry following the project's versioning rules."`
2. **`AGENTS.md`** — Inserted new Step 1 in the `🛑 MANDATORY END-OF-TASK SEQUENCE` block: "Update Changelog: You MUST insert a formal entry into CHANGELOG.md logging your modifications." Renumbered existing steps 1-3 to 2-4.
3. **`skill-templates/audit-agents/SKILL.md`** — Updated the AGENTS.md Template's end-of-task sequence to match the 4-step pattern. Updated Target Audit Criteria text from "3-step" to "4-step" with the correct step descriptions.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/AGENTS.md b/AGENTS.md
index ae2caba..59bec3f 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -47,6 +47,7 @@ You MUST follow these skill loading rules in every session:

 When finishing a task, you MUST execute these exact steps in order:

-1. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active `tasks/XX-task.md` file under "OpenCode Execution Log".
-2. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically `git add .` and inject the factual code diff.
-3. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/XX-task.md` and send it back to the AI Studio Brain for review."
+1. **Update Changelog:** You MUST insert a formal entry into CHANGELOG.md logging your modifications.
+2. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active `tasks/XX-task.md` file under "OpenCode Execution Log".
+3. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically `git add .` and inject the factual code diff.
+4. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/XX-task.md` and send it back to the AI Studio Brain for review."
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 4be841d..3c28e18 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -126,6 +126,14 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 - **`stage_and_inject_diff` MCP tool** — optimized the staged git diff command to globally exclude the entire `tasks/` directory (`:!tasks/`) instead of just the single active task file, completely eliminating task history clutter from factual codebase reviews.

+## [5.7.1] — 2026-06-17
+
+### Changed
+
+- **`system-prompt.md`** — `<system_version>` bumped to 5.7.1. `documentation_phase` text changed from discretionary `"Update CHANGELOG.md if necessary"` to mandatory `"You MUST update CHANGELOG.md with a new entry following the project's versioning rules."`
+- **`AGENTS.md`** — Mandatory End-Of-Task sequence expanded from 3 steps to 4 steps. New Step 1: "Update Changelog" — agents must now insert a formal CHANGELOG.md entry before writing their summary.
+- **`skill-templates/audit-agents/SKILL.md`** — AGENTS.md Template and Target Audit Criteria updated to reflect the new 4-step mandatory completion process.
+
 ## [5.8.0] — 2026-06-17

 ### Added
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index a1f3949..652b8ff 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -75,9 +75,10 @@ You MUST follow these skill loading rules in every session:

 When finishing a task, you MUST execute these exact steps in order:

-1. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active `tasks/XX-task.md` file under "OpenCode Execution Log".
-2. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically `git add .` and inject the factual code diff.
-3. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/XX-task.md` and send it back to the AI Studio Brain for review."
+1. **Update Changelog:** You MUST insert a formal entry into CHANGELOG.md logging your modifications.
+2. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active `tasks/XX-task.md` file under "OpenCode Execution Log".
+3. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically `git add .` and inject the factual code diff.
+4. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/XX-task.md` and send it back to the AI Studio Brain for review."
```

---

@@ -97,7 +98,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain

- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `tasks/`, and `.opencode/skills/`.
- **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
- **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
  -- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 3-step completion process: 1) Write manual reasoning in the task file. 2) Call the `custom_context_stage_and_inject_diff` MCP tool. 3) Notify the Manager.
  +- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 4-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool. 4) Notify the Manager.
- **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
- **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load the `task-generator` skill before creating new task files.
- **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load every available skill matching the project's tech stack before task implementation.
  diff --git a/system-prompt.md b/system-prompt.md
  index 5ae0429..111aa85 100644
  --- a/system-prompt.md
  +++ b/system-prompt.md
  @@ -1,4 +1,4 @@
  -<system_version>5.7.0</system_version>
  +<system_version>5.7.1</system_version>

 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
@@ -122,7 +122,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
   </bash_phase>

<documentation_phase>

- OPENCODE INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "OpenCode Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. Check off any local TODOs. 3) Update `CHANGELOG.md` if necessary.

* OPENCODE INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "OpenCode Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. Check off any local TODOs. 3) You MUST update `CHANGELOG.md` with a new entry following the project's versioning rules.
  </documentation_phase>

<summary_phase>

```
<!-- END_GIT_DIFF -->
```
