# Task 307: Living Folder Docs — Conventions & Prompt System

**File:** `tasks/qa/307-living-folder-docs-conventions-prompts.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Implement Phase 1 of the Living Folder Docs system: add the standard to docs/conventions.md, update prompt fragments (13-constraints.md, 09-hands_protocols.md, 01-system_version.md to 9.54.0), rebuild system-prompt.md, mirror rules in agents/cognitive-executor.md, and update CHANGELOG.md.

## Manager's Notes

Phase 1 implementation from the approved Living Folder Docs roadmap (Task 306). Establishes conventions and prompt-level agent contracts before MCP tool changes in Phase 2.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Add Living Folder Docs standard to docs/conventions.md
- [x] Add mandate to prompts/fragments/13-constraints.md
- [x] Update hands protocols template in prompts/fragments/09-hands_protocols.md
- [x] Bump version to 9.54.0 in prompts/fragments/01-system_version.md and assemble system-prompt.md
- [x] Mirror rules in agents/cognitive-executor.md
- [x] Verify system-prompt.md sync and task file lint
- [x] Update skill-templates/audit-agents/SKILL.md with Living Docs criteria
- [x] Create skill-templates/init-folder-docs/SKILL.md and register in 07-agent_skills_registry.md

## Acceptance Criteria

- [x] AC1: docs/conventions.md defines the complete Living Folder Docs specification (file shapes, ADR schema, code pointer formats)
- [x] AC2: prompts/fragments/13-constraints.md and 09-hands_protocols.md mandate sibling doc reading and updates during execution
- [x] AC3: system_version incremented to 9.54.0, system-prompt.md assembled, and lint_system_prompt_sync passes cleanly
- [x] AC4: agents/cognitive-executor.md mirrors the Living Docs requirements
- [x] AC5: CHANGELOG.md records the v9.54.0 Living Docs update
- [x] AC6: skill-templates/audit-agents/SKILL.md audits Living Folder Docs conventions
- [x] AC7: skill-templates/init-folder-docs/SKILL.md created and registered in 07-agent_skills_registry.md

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-lint-server python /tmp/opencode/verify_307.py (runs `lint_system_prompt_sync()` plus `lint_task_file('tasks/in-progress/307-living-folder-docs-conventions-prompts.md')`; passes only when both report in-sync/pass)
- **Expected result:** lint_system_prompt_sync reports in sync, lint_task_file passes, exit code 0
- **Actual result:** `lint_system_prompt_sync` reports "in sync with prompts/"; `lint_task_file` reports "passed Task File linting" on the in-progress path — confirmed on the initial run and re-confirmed after the hotfix round (registry + skills changes)
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Prompt assembler drift or malformed fragment breaks prompt assembly
- **Rollback plan:** git checkout modified files to restore v9.53.0 state

---

## Execution Log & Reasoning

Phase 1 executed per the Orchestrator blueprint. Seat check: single-domain SOP/prompt change, no UI surface and no data contract change, so Designer and data-layer seats skipped with reason. Brainstorm: not required — approved plan execution, fully reversible via git checkout.

Steps performed: created the task file directly in `tasks/in-progress/` per instruction (no backlog move needed); appended the Living Folder Docs Standard to `docs/conventions.md`; added the mandate bullet before `<defensive_shell_protocol>` in `13-constraints.md`; added rule 5 (sync) to CRITICAL TOOL RULES and item 4 (sibling docs update) to the documentation phase in the implementation template of `09-hands_protocols.md`; bumped `01-system_version.md` to 9.54.0; added Core Protocol item 7 and the Boundaries bullet in `agents/cognitive-executor.md`; rebuilt `system-prompt.md` via the assembler (99489 bytes, version line confirmed, mandate content present); updated CHANGELOG `[Unreleased]` → `### Added` via Parse-Then-Append. Deviation D1 (logged, minimal): also bumped the `test_prompt_sync.py` version pin 9.53.0 → 9.54.0 — required to keep the suite green, matching prior version-bump precedent; the file is added to the staged `modified_files` so the QA diff is complete. Validation: no Orchestrator rule violations (assembler path used for the generated artifact, no git add/commit/push, task numbers only in filename/title/CHANGELOG). Absent files skipped per policy: DESIGN.md, docs/architecture.md, docs/data_model.md.

Hotfix round (Hands, 2026-10-06): moved the task back qa → in-progress via `git mv` (tracked file, exit 0) and re-synced the `**File:**` header. Added Living Folder Docs coverage to `skill-templates/audit-agents/SKILL.md` in five places: Mode 1 conventions-compliance bullet, new Sibling Inspection criterion, conventions template appendix, AGENTS.md template guardrails, and the Mode 2 audit criterion. Gatekeeper scope check: the additions reference only generic colocated docs (no HQ-only fragment paths, no task numbers in prose), so the skill stays project-agnostic and the earlier scope-leak fix holds. Created `skill-templates/init-folder-docs/SKILL.md` (slice discovery, scaffolding, pointer injection, verification summary) and registered it after `task-lint` in `07-agent_skills_registry.md`. Re-assembled `system-prompt.md` (99674 bytes, still 9.54.0, registry line present). CHANGELOG Task 307 entry extended per instruction. AC6–AC7 genuinely satisfied and checked; prior AC1–AC5 and DoD boxes remain valid.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index ac51ef2..e6ef3b0 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -16,6 +16,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - Defined Living Folder Docs architectural specification and implementation roadmap in docs/living-folder-docs-roadmap.md (Task 306).
 
+- **Living Folder Docs Standard & Prompt System (Task 307):** Added the Living Folder Docs standard to docs/conventions.md, enforcing colocated README.md and DECISIONS.md alongside code pointers across vertical slices. Extended prompt fragments (13-constraints.md, 09-hands_protocols.md) and agents/cognitive-executor.md with mandatory sibling doc inspection and ADR synchronization rules. Rebuilt system-prompt.md with version bump to v9.54.0; updated skill-templates/audit-agents to audit living docs, and created skill-templates/init-folder-docs for legacy project onboarding.
+
 ### Fixed
 
 - **Context MCP singleton report write path (Task 286):** after the singleton migration the context server runs from `~/.config/opencode/mcp-context-server`, but `create_tree_report`, `read_source_files`, and `extract_signatures` wrote their reports to `Path("context-reports")` — the process cwd — so generated maps landed in the global install dir and the project's `context-reports/` went stale (the newest repo tree report stayed at 2026-09-18, still listing the removed `stacks/` directory; found by the task 285 smoke test). All three writers now resolve `report_dir = workspace_root / "context-reports"` from the per-call `project_root` argument the caller supplies, and the `.gitignore` safeguard writes to `<project_root>/.gitignore` via a new `_ensure_context_reports_ignored(workspace_root)` parameter. `extract_signatures`'s regex fallback also reads the resolved `path` instead of the cwd-relative `file_path`. The project_root-omitted path is unchanged (cwd fallback, still surfaced client-visibly), and a new regression test proves a foreign cwd writes nothing outside `<project_root>/context-reports/`. Context-server suite: **70 passed** (69 pre-existing + 1 new).
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 233cb6d..b8fa333 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -32,6 +32,7 @@ You are the primary execution engine for the Cognitive Lead AI platform. You rec
    - **Staging:** When a task implementation is complete, you MUST call `lint_task_file`, then call `custom_context_stage_and_inject_diff` passing the task file path.
    - **Closure:** You are STRICTLY FORBIDDEN from using `git commit`. If the Manager explicitly authorizes closure ("Approved for closure" or "Close task"), you MUST use the `custom_context_commit_and_clean_task` MCP tool as the ONLY commit path.
    - Output the exact hand-off message instructed by the Orchestrator.
+7. **Living Folder Docs Inspection:** Whenever inspecting or editing source files inside a component or feature directory, you MUST read the sibling `README.md` and `DECISIONS.md` before modifying code, and update them when domain contracts or architectural decisions change.
 
 ## Task Lifecycle & Kanban State Enforcement
 
@@ -240,6 +241,7 @@ Claim: "Task complete. The code looks correct."
 - Do not widen work into cleanup, refactoring, documentation, or adjacent features.
 - Do not claim completion without evidence.
 - For completed work, concisely restate it but do not overload with response detail.
+- Do not silently alter slice architecture or domain invariants without updating the sibling `README.md` and appending a dated ADR to `DECISIONS.md`.
 
 ## Planning Gate (no implementation without a Brain plan)
 
diff --git a/docs/conventions.md b/docs/conventions.md
index f455232..45804c4 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -189,3 +189,15 @@ Task numbers are provenance for humans, not reasoning material for the model. A
 **Forbidden homes:** visible prose in prompt fragments, agent instruction files, skill instructions, registry lines, section headings, and any Markdown the Brain or Hands reads as operating instructions.
 
 **Authoring rule:** when writing or editing prompt-facing Markdown, strip task-number parentheticals. Record provenance in the task file and CHANGELOG instead — never in the prompt text itself.
+
+## Living Folder Docs Standard
+
+All vertical slices and component directories across projects in this ecosystem MUST maintain colocated documentation and decision records:
+
+1. **Folder Colocation** — Every domain component or vertical slice directory (e.g. `src/features/todos/`, `services/auth/`, `mcp-context-server/`) must contain:
+   - `README.md` — Explains the component's core duties, directory layout, owned files, and critical invariants/risks.
+   - `DECISIONS.md` — Chronological log of dated Architectural Decision Records (ADRs). Each entry must document Context, Decision, Consequences, and Rollback strategy.
+2. **One-Line Code Pointer Standard** — Primary source files within the component directory must include a top-line comment pointing directly to the sibling docs:
+   - JavaScript/TypeScript: `// Sibling Docs: <relative-path>/README.md | Decisions: <relative-path>/DECISIONS.md`
+   - Python/Shell: `# Sibling Docs: <relative-path>/README.md | Decisions: <relative-path>/DECISIONS.md`
+3. **Synchronization Invariant** — Whenever source code inside a component directory is added, refactored, or altered in behavior or data contract, the sibling `README.md` and `DECISIONS.md` MUST be inspected and updated within the same task. Silent overrides of existing architectural decisions are strictly forbidden.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 7ec98e9..6a3a21c 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.53.0</system_version>
+<system_version>9.54.0</system_version>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 6404437..6cc916c 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -6,6 +6,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **code-search**: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
 - **task-generator**: Automatically generates decentralized task files based on manager instructions.
 - **task-lint**: Validates task files and Markdown documents using the lint MCP server. Run after task creation and before task closure.
+- **init-folder-docs**: Scaffolds living folder docs (README.md, DECISIONS.md, and code pointers) across component directories and vertical slices in legacy or uninitialized codebases.
 - **bundle-tasks**: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as the `bundle_tasks` MCP tool.
 - **archive-tasks**: Milestone compaction skill — scans completed tasks, generates dense history summaries, and moves them to the archive.
 - **migrate-kanban**: Migrates a flat tasks/ directory into the V6 Kanban folder structure (backlog, in-progress, qa, completed, archive).
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index 5a897bd..34767c2 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -66,6 +66,7 @@
      2. If user feedback is required, first check the session capability manifest for your question/clarification tool. If the tool is AVAILABLE, utilize it with multi-option schemas. If it is UNAVAILABLE, do NOT silently skip the question: relay it to the Manager as one narrow question with the options inline, then wait for the answer (manual mode) or record the replay-or-halt decision in the task file (autopilot mode).
      3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.
      4. **Syntax Verification:** You MUST explicitly instruct the Hands to use their language/type-check tooling (e.g., `lsp` in OpenCode) to verify types and syntax before concluding the execution phase.
+     5. **Living Folder Docs Sync:** Before modifying code in a component or feature folder, inspect sibling README.md and DECISIONS.md. If your change alters domain responsibilities, interfaces, or invariants, you MUST update sibling README.md and append a dated ADR to DECISIONS.md.
 </execution_phase>
 
   <bash_phase>
@@ -86,7 +87,7 @@
 </bash_phase>
 
   <documentation_phase>
-    HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs. Task-number discipline: NEVER write task numbers into prompt-facing Markdown prose — section headings, skill instructions, registry lines, and Execution Logs stay number-free (the task file's own title already carries its number). Task-number references live ONLY in code comments, CHANGELOG entries, history archives, and HTML comments.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version.
+    HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs. Task-number discipline: NEVER write task numbers into prompt-facing Markdown prose — section headings, skill instructions, registry lines, and Execution Logs stay number-free (the task file's own title already carries its number). Task-number references live ONLY in code comments, CHANGELOG entries, history archives, and HTML comments.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version. 4) Update sibling folder documentation (`README.md`, `DECISIONS.md`) for any component or slice directory modified during this task.
 </documentation_phase>
 
   <summary_phase>
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index 3cc3bba..930a415 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -31,6 +31,7 @@
   6. **Address the reader.** Use "you". Define a specialist term in plain words the first time it appears. Keep words simple for a non-native reader. Always answer the Manager in English, no matter which language the Manager used. Think in English too: internal reasoning stays in English even when the input is not. Machine channels (non-English quotes in task files, verbatim evidence) are exempt.
   7. **Keep internals out of the prose.** Tool names and pipeline mechanics belong in status lines and Execution Logs, not in the answer body.
   8. **Reference codes stay mandatory** for 3 or more items (F1/D1/R1/Q1/A1), per the Reference Point System above.
+- **Living Folder Docs Mandate:** Whenever reading or editing source code inside a vertical slice or component directory, the Hands MUST read the sibling `README.md` and `DECISIONS.md` before making changes. When implementing changes that introduce or modify architectural boundaries, storage strategies, or domain invariants, the Hands MUST update sibling `README.md` and append a dated ADR to sibling `DECISIONS.md`. Omitting sibling doc updates when altering slice behavior is a strict rule violation.
 <defensive_shell_protocol>
 When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
 1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index ffe851a..ec63c7f 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -18,7 +18,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 
 - **Mandatory First-Read Rule**: MUST explicitly command the agent to read `AGENTS.md` first before any execution. Inside it, it must route the agent to read `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` first.
 - **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md` (if present, else note absent per Absent-File Policy), `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`). Only require `.opencode/skills/` when the project already contains `.opencode/` or `with_opencode: true` is set.
-- **conventions.md Compliance**: The project MUST have a `docs/conventions.md` file containing the Universal DateTime Standard (UTC at rest, Epoch/ISO-8601 with Offset at API boundaries, Clock injection, Dual-Representation for future events, TZ=UTC Infrastructure), SOLID Programming Guidelines (SRP, OCP, LSP, ISP, DIP, Pragmatic Guardrails), Universal Financial Ledger Standard (snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging), and Defensive Shell Protocol (DSP) (`set -euo pipefail`, banned error masking, sidecar isolation).
+- **conventions.md Compliance**: The project MUST have a `docs/conventions.md` file containing the Universal DateTime Standard (UTC at rest, Epoch/ISO-8601 with Offset at API boundaries, Clock injection, Dual-Representation for future events, TZ=UTC Infrastructure), SOLID Programming Guidelines (SRP, OCP, LSP, ISP, DIP, Pragmatic Guardrails), Universal Financial Ledger Standard (snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging), Defensive Shell Protocol (DSP) (`set -euo pipefail`, banned error masking, sidecar isolation), and Living Folder Docs Standard (colocated README.md and DECISIONS.md per feature slice/component, one-line code pointer standard, synchronization invariant).
 - **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`) as their single source of truth.
 - **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
 - **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator. **Exception:** `git mv` is permitted for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
@@ -38,6 +38,8 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
 - **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
 
+- **Living Folder Docs Sibling Inspection**: AGENTS.md MUST instruct agents to inspect sibling README.md and DECISIONS.md before editing code in any component or vertical slice directory, and update them when domain contracts or architectural decisions change.
+
 ---
 
 ## Core Document Templates
@@ -240,6 +242,18 @@ Task numbers are provenance for humans, not reasoning material for the model. A
 1. **Allowed Homes (only):** code comments (`#`, `//`), `CHANGELOG.md` entries, task files, history archives, and HTML-comment markers (`<!-- -->`).
 2. **Forbidden Homes:** visible prose in prompt fragments, agent instruction files, skill instructions, registry lines, section headings, and any Markdown the Brain or Hands reads as operating instructions.
 3. **Authoring Rule:** when writing or editing prompt-facing Markdown, strip task-number parentheticals. Record provenance in the task file and CHANGELOG instead — never in the prompt text itself.
+
+## Living Folder Docs Standard
+
+All vertical slices and component directories across projects in this ecosystem MUST maintain colocated documentation and decision records:
+
+1. **Folder Colocation** — Every domain component or vertical slice directory (e.g. `src/features/todos/`, `services/auth/`, `mcp-context-server/`) must contain:
+   - `README.md` — Explains the component's core duties, directory layout, owned files, and critical invariants/risks.
+   - `DECISIONS.md` — Chronological log of dated Architectural Decision Records (ADRs). Each entry must document Context, Decision, Consequences, and Rollback strategy.
+2. **One-Line Code Pointer Standard** — Primary source files within the component directory must include a top-line comment pointing directly to the sibling docs:
+   - JavaScript/TypeScript: `// Sibling Docs: <relative-path>/README.md | Decisions: <relative-path>/DECISIONS.md`
+   - Python/Shell: `# Sibling Docs: <relative-path>/README.md | Decisions: <relative-path>/DECISIONS.md`
+3. **Synchronization Invariant** — Whenever source code inside a component directory is added, refactored, or altered in behavior or data contract, the sibling `README.md` and `DECISIONS.md` MUST be inspected and updated within the same task. Silent overrides of existing architectural decisions are strictly forbidden.
 ```
 
 ---
@@ -304,6 +318,8 @@ Use this when a project has no `AGENTS.md` yet (new project onboarding).
   -> **Do** load the `prompt-refactor` skill to translate and expand the intent into an elite English spec first. (Note: If you receive a standard XML task block, skip this and execute normally).
 - **Don't** attempt to resolve cross-disciplinary ambiguity within a single persona.
   -> **Do** trigger the Multi-Agent Brainstorming Loop if the Manager explicitly requests brainstorming or a task exhibits cross-disciplinary ambiguity. Interpret the `<brainstorming_session>` results in backlog tasks as non-functional guidelines that govern execution.
+- **Don't** silently alter slice architecture or domain invariants without updating the sibling README.md and appending a dated ADR to DECISIONS.md.
+  -> **Do** inspect sibling README.md and DECISIONS.md before modifying code, and keep them in sync with implementation changes.
 
 ## Documentation Sync Rules
 
@@ -390,6 +406,7 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Execution Log & Reasoning` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
 - **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
 - **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
+- **Living Folder Docs Standard**: docs/conventions.md MUST contain a ## Living Folder Docs Standard section, and AGENTS.md must mandate sibling doc inspection before component edits.
 
 ### Resolution Protocol
 
diff --git a/skill-templates/init-folder-docs/SKILL.md b/skill-templates/init-folder-docs/SKILL.md
new file mode 100644
index 0000000..85f11d4
--- /dev/null
+++ b/skill-templates/init-folder-docs/SKILL.md
@@ -0,0 +1,48 @@
+---
+name: init-folder-docs
+description: Scaffolds living folder docs (README.md, DECISIONS.md, and code pointers) across component directories and vertical slices in legacy or uninitialized codebases.
+---
+
+# Skill: Living Folder Docs Initializer
+
+Use this skill to onboard existing projects to the Living Folder Docs standard by discovering component directories and scaffolding baseline documentation and code pointers.
+
+## Scope Confinement
+
+- Confine all file scans and generation strictly to `[PROJECT_ROOT]`.
+- Never touch vendor or build directories (`node_modules/`, `.git/`, `dist/`, `build/`, `.venv/`, `vendor/`, `target/`).
+
+## Workflow
+
+1. **Slice Discovery:**
+   - Search the repository for distinct vertical slices, modules, or domain component directories (e.g., `src/features/*`, `apps/*/src/modules/*`, `services/*`, `backend/src/*`).
+   - List all discovered directory paths.
+
+2. **Scaffold Missing Slice Docs:**
+   For each discovered directory `[DIR]`:
+   - **README.md:** If `[DIR]/README.md` does not exist, create it with:
+     - `# Slice: [DIR_NAME]`
+     - `## Duties` (Derived from contained file names and directory role)
+     - `## Files` (List of contained source files with brief 1-line description)
+     - `## Key Risks & Invariants` (Baseline invariants and known edge cases)
+   - **DECISIONS.md:** If `[DIR]/DECISIONS.md` does not exist, create it with:
+     - `# Architectural Decisions: [DIR_NAME]`
+     - `## [YYYY-MM-DD] ADR-001: Initial Slice Baseline`
+     - `- **Context:** Baseline documentation initialized via init-folder-docs.`
+     - `- **Decision:** Adopting Living Folder Docs standard for this component.`
+     - `- **Consequences:** All future structural or contract changes must be recorded here.`
+     - `- **Rollback:** N/A (baseline adoption).`
+
+3. **Inject Code Pointers:**
+   - In primary source files within `[DIR]` (e.g. main service, controller, model, or entry file), inspect the first 5 lines.
+   - If no sibling docs comment exists, inject the top-line comment pointer:
+     - JS/TS: `// Sibling Docs: [DIR]/README.md | Decisions: [DIR]/DECISIONS.md`
+     - Python/Shell: `# Sibling Docs: [DIR]/README.md | Decisions: [DIR]/DECISIONS.md`
+
+4. **Verification & Summary:**
+   - Run `git status` (read-only) to review generated files.
+   - Output a concise summary listing:
+     - Discovered Slices: count and paths
+     - Created `README.md` files
+     - Created `DECISIONS.md` files
+     - Injected code pointers count
diff --git a/system-prompt.md b/system-prompt.md
index 15b17d3..fe4d832 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.53.0</system_version>
+<system_version>9.54.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -123,6 +123,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **code-search**: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
 - **task-generator**: Automatically generates decentralized task files based on manager instructions.
 - **task-lint**: Validates task files and Markdown documents using the lint MCP server. Run after task creation and before task closure.
+- **init-folder-docs**: Scaffolds living folder docs (README.md, DECISIONS.md, and code pointers) across component directories and vertical slices in legacy or uninitialized codebases.
 - **bundle-tasks**: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as the `bundle_tasks` MCP tool.
 - **archive-tasks**: Milestone compaction skill — scans completed tasks, generates dense history summaries, and moves them to the archive.
 - **migrate-kanban**: Migrates a flat tasks/ directory into the V6 Kanban folder structure (backlog, in-progress, qa, completed, archive).
@@ -291,6 +292,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
      2. If user feedback is required, first check the session capability manifest for your question/clarification tool. If the tool is AVAILABLE, utilize it with multi-option schemas. If it is UNAVAILABLE, do NOT silently skip the question: relay it to the Manager as one narrow question with the options inline, then wait for the answer (manual mode) or record the replay-or-halt decision in the task file (autopilot mode).
      3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.
      4. **Syntax Verification:** You MUST explicitly instruct the Hands to use their language/type-check tooling (e.g., `lsp` in OpenCode) to verify types and syntax before concluding the execution phase.
+     5. **Living Folder Docs Sync:** Before modifying code in a component or feature folder, inspect sibling README.md and DECISIONS.md. If your change alters domain responsibilities, interfaces, or invariants, you MUST update sibling README.md and append a dated ADR to DECISIONS.md.
 </execution_phase>
 
   <bash_phase>
@@ -311,7 +313,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 </bash_phase>
 
   <documentation_phase>
-    HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs. Task-number discipline: NEVER write task numbers into prompt-facing Markdown prose — section headings, skill instructions, registry lines, and Execution Logs stay number-free (the task file's own title already carries its number). Task-number references live ONLY in code comments, CHANGELOG entries, history archives, and HTML comments.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version.
+    HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs. Task-number discipline: NEVER write task numbers into prompt-facing Markdown prose — section headings, skill instructions, registry lines, and Execution Logs stay number-free (the task file's own title already carries its number). Task-number references live ONLY in code comments, CHANGELOG entries, history archives, and HTML comments.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version. 4) Update sibling folder documentation (`README.md`, `DECISIONS.md`) for any component or slice directory modified during this task.
 </documentation_phase>
 
   <summary_phase>
@@ -509,6 +511,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
   6. **Address the reader.** Use "you". Define a specialist term in plain words the first time it appears. Keep words simple for a non-native reader. Always answer the Manager in English, no matter which language the Manager used. Think in English too: internal reasoning stays in English even when the input is not. Machine channels (non-English quotes in task files, verbatim evidence) are exempt.
   7. **Keep internals out of the prose.** Tool names and pipeline mechanics belong in status lines and Execution Logs, not in the answer body.
   8. **Reference codes stay mandatory** for 3 or more items (F1/D1/R1/Q1/A1), per the Reference Point System above.
+- **Living Folder Docs Mandate:** Whenever reading or editing source code inside a vertical slice or component directory, the Hands MUST read the sibling `README.md` and `DECISIONS.md` before making changes. When implementing changes that introduce or modify architectural boundaries, storage strategies, or domain invariants, the Hands MUST update sibling `README.md` and append a dated ADR to sibling `DECISIONS.md`. Omitting sibling doc updates when altering slice behavior is a strict rule violation.
 <defensive_shell_protocol>
 When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
 1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 9c26c29..45e939f 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -43,7 +43,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.53.0"
+    assert shipped == "9.54.0"
 
 
 def test_compaction_protocol_in_shipped_prompt():
```
<!-- END_GIT_DIFF -->
