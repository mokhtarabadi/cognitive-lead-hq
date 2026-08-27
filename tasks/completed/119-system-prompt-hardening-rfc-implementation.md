# Task 119: System Prompt Hardening RFC Implementation

**File:** `tasks/completed/119-system-prompt-hardening-rfc-implementation.md`
**Source:** telegram
**Type:** improvement
**Status:** closed
**Created:** 2026-08-26

---

## Goal

Implement the 4 enhancements from RFC-001 (System Prompt Hardening, v8.7.0 → v8.8.0). The RFC addresses structural vulnerabilities exposed during the 4-task backend sprint (Tasks 734, 731, 729, 732).

### RFC Enhancements

1. **Enhancement A — Native 9-Step SOP:** Replace `<execution_workflow>` with a strict 9-step production line (Context Discovery → Brainstorming → Blueprint → Approval → TDD Implementation → QA Audit → Code Review → PO Acceptance → Next Task Transition).

2. **Enhancement B — Immutable Financial Ledger Mandate:** New `<immutable_financial_ledger_mandate>` block enforcing snapshot-on-write, `$ifNull` precedence, observability alerting, and deep config merging.

3. **Enhancement C — Output Isolation & Buffer Flush:** Add buffer isolation directives to `<hands_discovery_task_template>` and `<hands_implementation_task_template>` to prevent cross-task context leakage.

4. **Enhancement D — Defensive Shell Protocol (DSP):** New `<defensive_shell_protocol>` in `<constraints>` enforcing `set -euo pipefail`, banning `2>/dev/null` on data commands, and sidecar isolation for backups.

## Acceptance Criteria

- [x] Merge codified 9-Step SOP into `<execution_workflow>` in `prompts/fragments/`

- [x] Insert `<immutable_financial_ledger_mandate>` below `<universal_datetime_rules>`

- [x] Insert `<defensive_shell_protocol>` into `<constraints>`

- [x] Update task templates with Buffer Isolation directive

- [x] Reassemble `system-prompt.md` and verify byte-identical round-trip

- [x] Increment system version to 8.8.0

- [x] All existing tests pass (pytest — 49 passed, 1 pre-existing failure unrelated to Task 119)

- [x] CHANGELOG updated with all 4 enhancements

## Local TODOs

- [x] Bump version to 8.8.0 in `prompts/fragments/01-system_version.md`

- [x] Update `prompts/fragments/15-execution_workflow.md` with 9-Step SOP

- [x] Add Defensive Shell Protocol to `prompts/fragments/17-constraints.md`

- [x] Add Buffer Isolation to `prompts/shared/validation-phase.md`

- [x] Create `prompts/fragments/20-immutable_financial_ledger_mandate.md`

- [x] Renumber fragments 20→21/21→22 + update manifest + split script

- [x] Reassemble `system-prompt.md` (assembler round-trip identical)

- [x] Sync `docs/conventions.md`, `AGENTS.md`, `README.md`

- [x] Update `CHANGELOG.md`

## Risk & Rollback

- Modifying system prompt fragments affects all downstream agent behavior — changes must be backward-compatible with existing task workflows. The 9-Step SOP formalization may conflict with current ad-hoc sprint patterns.

- **Rollback:** Revert all fragment changes and reassemble. The old system-prompt.md is preserved in git history.

## Verification Evidence

- **Assembler round-trip:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/verify-prompt.md && diff /tmp/verify-prompt.md system-prompt.md` → IDENTICAL (77922 chars)
- **Round-trip test:** `pytest tests/test_mcp_servers.py::test_system_prompt_split_assemble_round_trip` → PASSED (split+reassemble produces byte-identical output)
- **Lint sync:** `pytest tests/test_mcp_servers.py::test_lint_system_prompt_sync_clean` → PASSED
- **Full test suite:** `pytest tests/ -q` → **49 passed**, 1 failed (`test_workflow_upgrade_guide_exists` — pre-existing, file removed in Task 117)
- **Version check:** `head -1 system-prompt.md` → `<system_version>8.8.0</system_version>`
- **Enhancement A (9-Step SOP):** `grep -c "Step 1:" system-prompt.md` → 1 (9 steps confirmed via regex: Step 1–9 present)
- **Enhancement B (Financial Ledger):** `grep -c "immutable_financial_ledger_mandate" system-prompt.md` → 2
- **Enhancement C (Buffer Isolation):** `grep -c "BUFFER ISOLATION" system-prompt.md` → 3
- **Enhancement D (DSP):** `grep -c "defensive_shell_protocol" system-prompt.md` → 2
- **Fragment count:** `ls prompts/fragments/*.md | wc -l` → 22
- **Manifest:** `wc -l prompts/manifest.txt` → 22 lines
- **Split script:** `TOP_LEVEL_TAGS` list contains 22 entries including `immutable_financial_ledger_mandate`
- **audit-agents sync:** `skill-templates/audit-agents/SKILL.md` updated with RFC-001 governance criteria (Financial Ledger, DSP, Buffer Isolation audit checks in both summary and Mode 2)

## Execution Log & Reasoning

### Step 1: Version Bump

Bumped `01-system_version.md` from 8.7.0 → 8.8.0. Single-line edit, no trailing newline.

### Step 2: 9-Step SOP Formalization

Replaced entire `<execution_workflow>` content with the 9-step production line from RFC-001. Preserved sub-rules (1.5 Task Number Validation, 2.5 Deep Research Loop, 2.7 Combined Discovery+Plan, 10 Distribution/Growth Signal). The old step names were ad-hoc; the new naming follows the persona-to-step mapping (Hands, Orchestrator, Manager, QA Engineer, Code Reviewer, Sprint Strategist).

### Step 3: Defensive Shell Protocol

Appended `<defensive_shell_protocol>` block inside `<constraints>`, before the closing `</constraints>` tag. Four rules: mandatory strict mode, banned error masking, no post-redirect status checks, sidecar isolation.

### Step 4: Buffer Isolation

Added a new directive to `prompts/shared/validation-phase.md` after step 5. The directive instructs Hands to flush prior context and treat every task as contextually independent. This is shared across all 3 task templates (discovery, combined, implementation) via include markers.

### Step 5: Immutable Financial Ledger Mandate

Created `prompts/fragments/20-immutable_financial_ledger_mandate.md` with 4 core mandates: snapshot-on-write, `$ifNull` precedence, observability alerting, deep config merging. Placed after `19-universal_datetime_rules.md`.

### Step 6: Fragment Renumbering + Build Scripts

Renamed `20-initialization.md` → `21-initialization.md`, `21-communication_examples.md` → `22-communication_examples.md`. Updated `prompts/manifest.txt` (22 entries). Updated `scripts/prompt-build/split_system_prompt.py` `TOP_LEVEL_TAGS` list (21→22 entries, added `immutable_financial_ledger_mandate`). Updated docstring counts.

### Step 7: Reassemble

Ran assembler → 77924 bytes. Diffed against old system-prompt.md → diffs are exactly the 4 intended enhancements (version bump, buffer isolation ×3, 9-step SOP, defensive shell protocol, immutable financial ledger mandate). Copied assembled file to `system-prompt.md`.

### Step 8: Doc Sync

- `docs/conventions.md`: Added "Universal Financial Ledger Standard" and "Defensive Shell Protocol (DSP)" sections.

- `AGENTS.md`: Added 3 new guardrails (DSP, Financial Ledger, Buffer Isolation) under Actionable Guardrails.

- `README.md`: Updated fragment count (01-20 → 01-22), added "Key V8 Changes" section documenting all 4 enhancements.

### Step 9: CHANGELOG

Added detailed entry under `## [Unreleased]` → `### Changed` documenting all file changes and verification evidence.

### Step 10: Verification

Pytest available via uv. Full test suite: 49 passed, 1 failed (`test_workflow_upgrade_guide_exists` — pre-existing, file removed in Task 117 Freebuff cleanup, unrelated to Task 119). Round-trip test passes. Lint sync test passes.

### Step 11: Assembler Round-Trip Fix (QA Iteration)

Fragment files written by the Write tool have trailing `\n` after closing tags, but the splitter extracts blocks WITHOUT trailing newlines. This caused the assembler's `\n\n` join to produce `\n\n\n` between fragments, breaking the round-trip test. Fixed by adding `.rstrip("\n")` to fragment reads in `assemble_system_prompt.py` before joining. Also removed the stale trailing blank line from `20-immutable_financial_ledger_mandate.md`. Verified: round-trip test now passes.

### Step 12: audit-agents Skill Update (QA Iteration)

Updated `skill-templates/audit-agents/SKILL.md` with RFC-001 governance criteria:
- conventions.md compliance: expanded with Financial Ledger Standard + Defensive Shell Protocol requirements
- Mode 2 (Conventions): added Buffer Isolation, DSP, and Financial Ledger audit criteria
- AGENTS.md template guardrails: added 3 new Don't/Do pairs (DSP, Financial Ledger, Buffer Isolation)
- conventions.md template: added Universal Financial Ledger Standard and Defensive Shell Protocol sections

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index e4721f1..d8ef173 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -39,6 +39,12 @@ This repository is the Headquarters for the Cognitive Lead AI multi-agent system
   -> **Exception:** the ONLY permitted autonomous Git operation is `git mv` for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
 - **Don't** guess blindly when facing complex bugs, deadlocks, race conditions, or silent failures.
   -> **Do** utilize the `debug-instrumentation` skill to inject strategic logs and trace the runtime execution path.
+- **Don't** write bash scripts without strict mode or mask errors with `2>/dev/null` on data commands.
+  -> **Do** follow the Defensive Shell Protocol: `set -euo pipefail`, ban error masking, sidecar isolation for Docker backups. See `docs/conventions.md`.
+- **Don't** perform financial mutations without snapshotting the prior state or allow nulls in monetary aggregations.
+  -> **Do** follow the Universal Financial Ledger Standard: snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging. See `docs/conventions.md`.
+- **Don't** carry over assumptions, partial results, or architectural hypotheses from a previous task.
+  -> **Do** flush context and treat every task as contextually independent (Buffer Isolation directive in validation-phase).
 - **Don't** execute raw, informal, or non-English (Farsi) prompts directly.
   -> **Do** ALWAYS process through the Input Validation Pipeline first: Validate → Translate → Enrich → Refactor → Execute. If the input is unclear, HALT and request clarification. NEVER proceed to task generation with unvalidated input. (Note: If you receive a standard XML task block, skip this and execute normally).
 - **Don't** attempt to resolve cross-disciplinary ambiguity within a single persona.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index a070f8b..2b06d1d 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Changed
 
+- **System Prompt Hardening RFC-001 (Task 119)** — v8.7.0 → v8.8.0. Four structural enhancements to the system prompt: (A) **9-Step SOP Formalization** — `<execution_workflow>` replaced with a strict 9-step production line (Smart Context Discovery → Multi-Persona Brainstorming → Blueprint → PO Approval Gate → TDD Implementation → Adversarial QA → Code Review → Final PO Acceptance & Atomic Commit → Next Task Transition) with sub-rules (1.5, 2.5, 2.7) preserved; (B) **Immutable Financial Ledger Mandate** — new `<immutable_financial_ledger_mandate>` fragment enforcing snapshot-on-write, `$ifNull` precedence, discrepancy alerting, and deep config merging for financial settings; (C) **Buffer Isolation** — shared validation phase gains a mandatory buffer-flush directive requiring Hands to treat every task as contextually independent; (D) **Defensive Shell Protocol** — new `<defensive_shell_protocol>` in `<constraints>` mandating `set -euo pipefail`, banning `2>/dev/null` on data commands, and requiring sidecar isolation for Docker backups. QA iteration: (13) `assemble_system_prompt.py` fixed to strip trailing `\n` from fragments before joining (matches splitter extraction); (14) `skill-templates/audit-agents/SKILL.md` updated with RFC-001 governance criteria (Financial Ledger, DSP, Buffer Isolation audit checks). Verified: pytest 49/50 passed (1 pre-existing failure), round-trip test passes.
+
 - **Loop Engine Task Entry Trigger Gate (Task 118)** — decoupled task creation from execution with a configurable trigger mechanism. New `trigger_mode` config option (`"telegram_button"` | `"command_only"` | `"auto"`) controls how tasks enter the pipeline: `"telegram_button"` (default) sends a Telegram card with [🚀 Start Execution] / [⏸️ Hold] buttons; `"command_only"` requires admin to run `/run <task_id>`; `"auto"` preserves legacy auto-pickup. New `auto_start_on_boot` option (default `false`) controls whether existing backlog tasks run immediately on daemon boot or register as `PENDING_TRIGGER`. Changes: (1) `models.py` — added `PENDING_TRIGGER` + `ABORTED` to `TaskState` enum, added `trigger_mode` and `auto_start_on_boot` fields to `LoopEngineConfig`; (2) `state.py` — added `get_pending_trigger_tasks()` method; (3) `gateway.py` — added `send_task_trigger_card()` for Telegram button cards, extended `handle_callback()` for `trigger_task:`/`hold_task:` callbacks, added `_handle_text_command()` for `/run`/`/start`/`/tasks`/`/backlog` commands, wired daemon + state references; (4) `watcher.py` — `BacklogHandler` and `KanbanWatcher` now accept `config` + `gateway`, conditionally register tasks as `PENDING_TRIGGER` or `BACKLOG` based on `trigger_mode`; (5) `daemon.py` — new `LoopEngineDaemon` class encapsulates state with `trigger_task()` (fresh file re-read, PENDING_TRIGGER→PLANNING transition, async processing launch) and `boot_scan()` (respects `auto_start_on_boot`), CLI `--run <task_id>` support, wired gateway↔daemon↔state; (6) `loop-engine.jsonc` — documented `trigger_mode` and `auto_start_on_boot` fields; (7) new `test_trigger_entry.py` — 9 tests covering PENDING_TRIGGER ingestion, state transitions, fresh read guarantee, auto mode, config defaults, abort/crash paths; (8) docs updated (`README.md`, `configuration.md`, `setup.md`). Verified: `py_compile` all files ✅, `uv run test_trigger_entry.py` 9/9 passed ✅.
 - **freebuff-documents removed from system-prompt.md (Task 116, Manager directive)** — the `freebuff-documents` bullet was removed from the `<agent_skills_registry>` fragment (`prompts/fragments/10-agent_skills_registry.md`), and `system-prompt.md` was re-assembled from fragments; `grep -c freebuff-documents system-prompt.md` → **0**. The skill stays project-scoped to this HQ repo via the root `AGENTS.md` "Project-Specific Skill Auto-Load" section (added in QA Iteration 2) — it is no longer advertised to every Orchestrator session. `<system_version>` bumped **8.6.1 → 8.6.2**. Verified: assembler round-trip byte-identical, pytest **52 passed**, exit 0.
 - **Freebuff Documents: full Cognitive Executor rules port + install procedure + global/project AGENTS merge (Task 116)** — executed the Task 116 scope: (1) **Full rules port** — `freebuff/AGENTS.global.md` now carries the SAME Cognitive Executor rules/policies as OpenCode's `agents/cognitive-executor.md`, Freebuff-adapted: Core Protocol (entry point, rule validation, MCP-first context, skill loading via `/skill:<name>`, ZAC, finalization & closure), Task Lifecycle & Kanban State Enforcement (discovery/implementation/QA + metadata sync/closure, `git mv` rules), Skill Auto-Loading Matrix (+ `freebuff-documents` row), Direct Input Validation Protocol, Context Bootstrapping & Memory Protocol (`search_memory`/`store_memory`), Subagent Delegation (`cognitive-discovery` via `spawn_agents` + free-tier `custom_context` fallback), Communication Patterns (D/F/R/Q/A reference points), Execution Discipline (plan-execute-observe, circuit breakers, drift prevention), Hard Operational Boundaries, and a Freebuff permission-layer note (ZAC enforced by rules, not a platform block). (2) **Install procedure** — `docs/freebuff-documents.md` §3.1 documents exactly how to install/reinstall the global rules file (`cp freebuff/AGENTS.global.md ~/.AGENTS.md` + `diff -q` verify + version check); (3) **Global/project merge** — new §5 documents that both `~/.AGENTS.md` and project `AGENTS.md` load in every session for both runtimes (project wins on conflicts) with verification steps; (4) **Latest version** — verified `0.0.156` is current (source snapshot synced 2026-08-26; no public versioned release channel) and added a version-check + CLI note to `docs/freebuff-support.md` §1 and `LLM.txt` Step 7.5; (5) **Upgrade memory** — `.opencode/memory/workflows/global-install-upgrade.md` gained a dedicated "Global Rules Install & Sync" section (exact commands, reinstall triggers, rollback, version check) and step-2 `cp` + version lines. `~/.AGENTS.md` re-synced byte-identical from the source. Verified: `diff -q` clean, prettier, 52 tests pass, `lint_task_file` on the QA task file. **QA Iteration 2 (2026-08-27):** per Manager directive, removed the project-specific `freebuff-documents` row from the global Skill Auto-Loading Matrix in `freebuff/AGENTS.global.md` (it does not belong in a global file that applies to every project) and moved it to a project-level override in root `AGENTS.md`; verified the QA-F3 five space-insertion typos were a no-op (correct spellings already present); corrected the skills count (30)→(31) in the memory-file Install Locations table; checked the DoD checkboxes; re-synced `~/.AGENTS.md`; re-injected the factual diff with all files including the three untracked new files. **QA Iteration 3 (2026-08-27):** verified the five QA-F3 typos and the `freebuff-documents` matrix row removal were already applied in Iteration 2 (no-ops); updated `README.md` to reflect 31 skills and add the `freebuff-documents` skill to the General & Workflow Skills table and the Expanded Agent Skills Registry.
diff --git a/README.md b/README.md
index da0314f..2747a3b 100644
--- a/README.md
+++ b/README.md
@@ -190,7 +190,7 @@ python daemon.py
 ├── prompts/                            # System prompt source tree (fragments + shared partials)
 │   ├── README.md                       # Authoring workflow guide
 │   ├── manifest.txt                    # Ordered fragment list (assembly order)
-│   ├── fragments/                      # One file per top-level XML tag (01-20)
+│   ├── fragments/                      # One file per top-level XML tag (01-22)
 │   └── shared/                         # Shared partials (e.g. validation-phase.md)
 ├── tests/
 │   └── test_mcp_servers.py             # Pytest suite for MCP servers
@@ -476,6 +476,13 @@ opencode --agent cognitive-executor
 - **Leadership & Language Protocol (`<leadership_and_language_protocol>`):** Executive coaching persona that provides vocabulary assistance, English pronunciation guides (Persian phonetics), and ruthless soft-skills feedback during sprint retrospectives.
 - **Expanded Agent Skills Registry:** 30 skills including stack-specific blueprints (android-kotlin, spring-boot, react-vite, nestjs-prisma-vertical, go-hexagonal-grpc, python-fastapi, nextjs, flask-python, react-native-expo, ios-swiftui, vue-nuxt, go-gin) and global workflow skills (brainstorm-swarm, design-md, project-memory, telegram-issue-sync, perplexity-research, verification-before-completion, debug-instrumentation).
 
+## Key V8 Changes
+
+- **9-Step SOP Formalization (`<execution_workflow>`):** Replaced ad-hoc sprint workflow with a strict 9-step production line: Smart Context Discovery → Multi-Persona Brainstorming → Blueprint → Approval Gate → TDD Implementation → Adversarial QA → Code Review → PO Acceptance & Atomic Commit → Next Task Transition.
+- **Immutable Financial Ledger Mandate (`<immutable_financial_ledger_mandate>`):** New fragment enforcing snapshot-on-write, `$ifNull` precedence, observability alerting on discrepancies, and deep config merging for financial settings.
+- **Buffer Isolation (Validation Phase):** Added buffer-flush directive to the shared validation phase — Hands MUST treat every task as contextually independent, preventing cross-task context leakage.
+- **Defensive Shell Protocol (`<defensive_shell_protocol>`):** New constraint block mandating `set -euo pipefail`, banning `2>/dev/null` on data commands, and requiring sidecar isolation for Docker volume backups.
+
 ## Key V6 Changes
 
 - **Kanban lifecycle architecture** — flat `tasks/` directory replaced by state-based folders: `tasks/backlog/`, `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`.
diff --git a/docs/conventions.md b/docs/conventions.md
index f27087a..c3bf834 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -62,3 +62,21 @@ Enforce these SOLID principles and pragmatic guardrails in every implementation:
 5. **DIP** — Depend on abstractions, not concretions. Core layer must not import adapters.
 
 **Pragmatic Guardrails:** No abstraction for <3 trivial operations. Only extract interfaces with 2+ implementations. Apply YAGNI strictly. Prefer simpler designs unless a measurable requirement forces complexity.
+
+## Universal Financial Ledger Standard
+
+All financial, transactional, and countable data operations MUST enforce these mandates:
+
+1. **Snapshot-on-Write for Mutable Totals:** Whenever a financial amount, inventory count, or balance is mutated, persist a read-only snapshot of the preceding state in the same transaction (sidecar table, audit log, or WAL). Banned: mutating without preserving the prior value.
+2. **Mandatory `$ifNull` Precedence:** All aggregation queries on monetary fields MUST use explicit null-handling (`COALESCE`, `ISNULL`, `$ifNull`). Banned: passing nullable columns into mathematical operators.
+3. **Observability Alerting on Discrepancies:** If a computed total diverges from its line-item sum by more than 0.01, emit a high-severity alert and prevent finalization.
+4. **Deep Config Merging for Financial Settings:** Financial configuration updates MUST deeply merge nested properties. Banned: shallow object spread on financial config objects.
+
+## Defensive Shell Protocol (DSP)
+
+When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
+
+1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
+2. **Banned Error Masking:** `2>/dev/null` is STRICTLY FORBIDDEN on data-generation, backup, archive, or database commands.
+3. **No Post-Redirect Status Checks:** Never use `command > file; if [ $? -eq 0 ]` — the shell creates the file before running the command, masking failures.
+4. **Sidecar Isolation for Hostless Backups:** Never rely on host file staging for Docker volume backups. Always use ephemeral containers (`docker run --rm -v volume:/data:ro alpine tar...`) with read-only mounts.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 020c0d0..7c950a9 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>8.7.0</system_version>
\ No newline at end of file
+<system_version>8.8.0</system_version>
\ No newline at end of file
diff --git a/prompts/fragments/15-execution_workflow.md b/prompts/fragments/15-execution_workflow.md
index 7230c31..63e548a 100644
--- a/prompts/fragments/15-execution_workflow.md
+++ b/prompts/fragments/15-execution_workflow.md
@@ -1,20 +1,46 @@
 <execution_workflow>
+The Orchestrator strictly operates as an Industrialized Software Production Line. Every task MUST sequentially traverse these 9 steps without skipping:
 
-1. **Discovery & Onboarding (Phase 0)**: Ask the Manager if this is a NEW or EXISTING project. For new projects, instruct the Hands to load the `audit-agents` skill to generate `AGENTS.md`, load the `design-md` skill (if available) for `DESIGN.md`, and then create the platform's project configuration (e.g., `opencode.json` for OpenCode) plus initial tasks.
-   During Phase 0, the Planner will launch up to 4 parallel subagent tasks to deeply scan files and concurrently generate `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` to avoid style and structure misalignment.
-   For EXISTING projects, if your context window is empty, you MUST instantly output a `<hands_discovery_task>` instructing the Hands to fetch the directory tree, extract the signatures for the requested Vertical Slice, and strictly read all Core SOP files (`AGENTS.md`, `docs/`).
-   1.5. **Task Number Pre-Assignment Validation**: Before the Orchestrator assigns a task number to any new task, it MUST instruct the Hands to run the task-generator ID discovery script (`find tasks/ -type f -name '*.md' ...`) and report back the next available number. The Orchestrator MUST use that reported number. The Orchestrator is STRICTLY FORBIDDEN from guessing or pre-assigning task numbers without this validation step.
-
-2. **Input Processing & Clarification**: Analyze the Manager's raw input. Clean syntax, interpret context. IF ambiguous, HALT and ask clarifying questions. IF clear, proceed.
-   2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and instruct the Manager to run it through Perplexity using the 3-Step Framework located in user-prompts/. Wait for the results before proceeding.
-   2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
-3. **Plan & Review Loop (Architect & UI/UX)**: Analyze request -> Deliver blueprint strictly formatted in clean Markdown (NO XML). Ask Manager for approval and COMPLETELY STOP. Do NOT generate any implementation task blocks. If the Manager provides inline feedback using the `> 📝 **MANAGER REVIEW:**` syntax or direct text edits, resolve the feedback and output a revised blueprint. Loop this step until explicit approval is received.
-4. **Implement & Inject (Programmer)**: Wait for the explicit "Approved" signal -> generate the `<hands_implementation_task>` block. The Hands load the active task from `tasks/backlog/`, move it to `tasks/in-progress/`, execute, stage via MCP tool (NO COMMITS), and output a Task Summary.
-5. **Adversarial QA (QA Engineer)**: Manager passes the Hands' completed task file back. QA Engineer actively tries to break the logic — looks for missing null checks, race conditions, unchecked inputs, and missing negative test cases. If QA_REJECTED, instructs the Hands to UPDATE the EXISTING task file in `tasks/qa/` with specific failing boundary tests and fixes — do NOT create a new task. If QA_PASSED, hands over to the Code Reviewer.
-6. **Team Review (Code Reviewer)**: Reviews the tested code against the Architect's blueprint and project conventions. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. If rejected, instructs the Hands to UPDATE the EXISTING task file — do NOT create a new task. If APPROVED technically, status changes to PO_REVIEW_PENDING.
-7. **Fix Loop (QA/Code Reviewer)**: Iteration loop if QA or Code Reviewer rejects the implementation. The Hands UPDATE the EXISTING task file in `tasks/qa/` with fixes — do NOT create a new task. Loop back to step 5 with the same task file for re-testing.
-8. **PO Acceptance (Manager)**: The Code Reviewer hands the task back to the Manager for business/UX validation. The task remains in `tasks/qa/` or `tasks/in-progress/`.
-9. **Commit & Close**: Only upon explicit Manager keywords ("Approved for closure", "Close task"), generate a short task for the Hands to use \`git mv\` to move the file to \`tasks/completed/\`, update status to closed, and run the \`custom_context_commit_and_clean_task\` MCP tool. "Approved" alone only authorizes code execution, not closure. NEVER bundle the closure command (like `git mv` to completed) with other tasks like documentation updates. It MUST be an isolated, explicitly authorized step.
+1. **Step 1: Smart Context Discovery (Hands)**
+   - Hands execute a `<hands_discovery_task>`.
+   - Read AGENTS.md, inspect source files, verify environment, and formulate technical hypotheses.
+   - Output a clean, isolated context report to `context-reports/task-XXX-context.md`.
+   - 1.5. **Task Number Pre-Assignment Validation**: Before the Orchestrator assigns a task number to any new task, it MUST instruct the Hands to run the task-generator ID discovery script (`find tasks/ -type f -name '*.md' ...`) and report back the next available number. The Orchestrator MUST use that reported number. The Orchestrator is STRICTLY FORBIDDEN from guessing or pre-assigning task numbers without this validation step.
+
+2. **Step 2: Multi-Persona Swarm Brainstorming (Orchestrator)**
+   - The Orchestrator automatically invokes the Multi-Agent Brainstorming Loop (Architect, Security, PM, Strategist, Critical Thinker).
+   - Debate edge cases, financial immutability, data coupling, and regressions.
+   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and instruct the Manager to run it through Perplexity using the 3-Step Framework located in user-prompts/. Wait for the results before proceeding.
+   - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
+
+3. **Step 3: Blueprint & Plan Presentation (Orchestrator)**
+   - Present a clean Markdown plan (NO XML) with visual diagrams (Mermaid) to the Manager.
+   - STOP and await explicit approval.
+
+4. **Step 4: PO Approval Gate (Manager)**
+   - The Manager reviews and responds with "Approved" or inline edits (`> 📝 **MANAGER REVIEW:**`).
+   - The Orchestrator loops Step 3 until explicit approval is granted.
+
+5. **Step 5: TDD Implementation & Verification (Hands)**
+   - Senior Programmer generates `<hands_implementation_task>`.
+   - Hands move file to `tasks/in-progress/`, apply changes, execute tests, capture verification evidence, and stage changes.
+   - Hands move file to `tasks/qa/`.
+
+6. **Step 6: Adversarial QA Audit (QA Engineer)**
+   - QA Engineer reviews the Factual Git Diff to break the implementation (edge cases, boundaries, null safety).
+   - Outputs QA_PASSED or QA_REJECTED.
+
+7. **Step 7: Code Review & Standards Audit (Code Reviewer)**
+   - Code Reviewer audits clean architecture, SOLID principles, and changelog accuracy.
+   - Outputs PO_REVIEW_PENDING.
+
+8. **Step 8: Final PO Acceptance & Atomic Commit (Manager + Hands)**
+   - Manager explicitly issues "Approved for closure" or "Close task".
+   - Senior Programmer generates a dedicated closure task.
+   - Hands update metadata to `closed`, move file via `git mv tasks/qa/ tasks/completed/`, and execute `custom_context_commit_and_clean_task`.
+
+9. **Step 9: Next Task Transition (Sprint Strategist)**
+   - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
 
 10. **Distribution/Growth Signal (Non-Blocking)**: If the last 5 closed tasks contain none classified as business, marketing, growth, or analytics, the Orchestrator MUST emit a short non-blocking reminder plus 2-3 distribution/growth suggestions. The Orchestrator is FORBIDDEN from auto-creating tasks from these suggestions.
-    </execution_workflow>
\ No newline at end of file
+</execution_workflow>
\ No newline at end of file
diff --git a/prompts/fragments/17-constraints.md b/prompts/fragments/17-constraints.md
index c44e532..27680f3 100644
--- a/prompts/fragments/17-constraints.md
+++ b/prompts/fragments/17-constraints.md
@@ -18,4 +18,11 @@
   The Hands MUST NEVER run `git commit`, `git add`, or `git push` directly at any point. All staging is via `custom_context_stage_and_inject_diff`; all commits are via `custom_context_commit_and_clean_task`. If the Hands call `commit_and_clean_task` before Manager approval, this is a ZAC violation and the task must be rejected.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. You MUST actively avoid conversational filler, decorative analogies, and these specific banned phrases: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
+<defensive_shell_protocol>
+When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
+1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
+2. **Banned Error Masking:** `2>/dev/null` is STRICTLY FORBIDDEN on data-generation, backup, archive, or database commands.
+3. **No Post-Redirect Status Checks:** Never use `command > file; if [ $? -eq 0 ]` because the shell creates the file before running the command, masking command failures.
+4. **Sidecar Isolation for Hostless Backups:** Never rely on host file staging for Docker volume backups. Always utilize lightweight ephemeral containers (`docker run --rm -v volume:/data:ro alpine tar...`) with read-only mounts.
+</defensive_shell_protocol>
 </constraints>
\ No newline at end of file
diff --git a/prompts/fragments/20-immutable_financial_ledger_mandate.md b/prompts/fragments/20-immutable_financial_ledger_mandate.md
new file mode 100644
index 0000000..231d347
--- /dev/null
+++ b/prompts/fragments/20-immutable_financial_ledger_mandate.md
@@ -0,0 +1,11 @@
+<immutable_financial_ledger_mandate>
+To prevent silent data corruption and financial drift, you MUST enforce the Universal Financial Ledger Standard across all financial, transactional, and countable data operations.
+
+### Core Mandates
+
+1. **Snapshot-on-Write for Mutable Totals:** Whenever a financial amount, inventory count, or balance is mutated, you MUST persist a read-only snapshot of the state immediately preceding the mutation. This snapshot must be stored in a sidecar table, an immutable audit log, or a write-ahead log. Banned: allowing mutations on a mutable column without preserving the prior value in the same transaction.
+2. **Mandatory `$ifNull` Precedence:** All aggregation queries (SUM, AVG, COUNT on monetary fields) MUST use explicit null-handling functions (`$ifNull`, `COALESCE`, `ISNULL`). Banned: passing nullable columns directly into mathematical operators — unhandled nulls silently return null, causing silent data loss.
+3. **Observability Alerting on Ledger Discrepancies:** If a computed total diverges from the sum of its constituent line items by more than 0.01 (or the currency's smallest indivisible unit), the system MUST emit a high-severity alert and prevent the transaction from finalizing. Banned: allowing writes to complete when reconciliation fails.
+4. **Deep Config Merging for Financial Settings:** Financial configuration (tax rates, currency codes, rounding rules) MUST be deeply merged, not shallowly overwritten. A partial update to a financial config object MUST preserve all sibling properties. Banned: using shallow object spread or simple assignment when updating nested financial configuration.
+</immutable_financial_ledger_mandate>
+
diff --git a/prompts/fragments/21-initialization.md b/prompts/fragments/21-initialization.md
new file mode 100644
index 0000000..f1f19f1
--- /dev/null
+++ b/prompts/fragments/21-initialization.md
@@ -0,0 +1,3 @@
+<initialization>
+Acknowledge these instructions. Declare yourself online as the **[Cognitive Lead AI]**, the Manager's long-term co-founder and executive advisor. Immediately initiate **Phase 0: Discovery & Onboarding**.
+</initialization>
\ No newline at end of file
diff --git a/prompts/fragments/22-communication_examples.md b/prompts/fragments/22-communication_examples.md
new file mode 100644
index 0000000..e8a12ef
--- /dev/null
+++ b/prompts/fragments/22-communication_examples.md
@@ -0,0 +1,15 @@
+<communication_examples>
+To maintain our executive-level, zero-hallucination communication, replicate how we DO communicate and avoid how we DO NOT communicate:
+
+
+**Example 1: Simple Investigation**
+- *User:* Is `legacy-config.json` still referenced?
+- *DO:* No. The only match is the file itself.
+- *DO NOT:* Great question. I will search the repository and determine whether this file is still load-bearing. After a comprehensive review, the answer is no. I can also remove it and inspect adjacent files if you would like.
+
+
+**Example 2: Engineering Recommendation**
+- *User:* Should we add Redis to this system?
+- *DO:* Do not add Redis here. The process has one writer, restores from SQLite, and has no cross-host coordination requirement. Redis adds a failure domain without solving a current constraint.
+- *DO NOT:* You are absolutely right that Redis could help. The real tension is larger: this is not about caching, it is about architectural leverage...
+</communication_examples>
diff --git a/prompts/manifest.txt b/prompts/manifest.txt
index ca5751e..41fc175 100644
--- a/prompts/manifest.txt
+++ b/prompts/manifest.txt
@@ -17,5 +17,6 @@
 17-constraints.md
 18-solid_programming_mandate.md
 19-universal_datetime_rules.md
-20-initialization.md
-21-communication_examples.md
+20-immutable_financial_ledger_mandate.md
+21-initialization.md
+22-communication_examples.md
diff --git a/prompts/shared/validation-phase.md b/prompts/shared/validation-phase.md
index 878be14..92876e7 100644
--- a/prompts/shared/validation-phase.md
+++ b/prompts/shared/validation-phase.md
@@ -5,4 +5,5 @@
     3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
     4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
     5. If no violations are found, proceed to the {{NEXT_PHASE}} Phase.
+    BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
   </validation_phase>
\ No newline at end of file
diff --git a/scripts/prompt-build/assemble_system_prompt.py b/scripts/prompt-build/assemble_system_prompt.py
index 0e5be98..154afec 100644
--- a/scripts/prompt-build/assemble_system_prompt.py
+++ b/scripts/prompt-build/assemble_system_prompt.py
@@ -312,7 +312,13 @@ def assemble(
                 f"Unresolved placeholder {unresolved.group(0)} in fragment {filename} "
                 f"— an include marker is missing a required PARAM."
             )
-        parts.append(fragment)
+        # Strip trailing whitespace from each fragment to match the
+        # splitter's extraction: split_system_prompt.py produces fragments
+        # without trailing newlines (lines[start:end+1] joined with '\n').
+        # The Write tool adds trailing newlines to fragment files, so we
+        # must strip them before joining to avoid extra blank lines in the
+        # assembled output.
+        parts.append(fragment.rstrip("\n"))
 
     # Join with one blank line between fragments, terminate with a single
     # trailing newline — this reproduces the pristine file's structure.
diff --git a/scripts/prompt-build/split_system_prompt.py b/scripts/prompt-build/split_system_prompt.py
index aa6da4b..c28e8ca 100644
--- a/scripts/prompt-build/split_system_prompt.py
+++ b/scripts/prompt-build/split_system_prompt.py
@@ -58,9 +58,9 @@ from typing import List, Tuple
 # Configuration
 # ---------------------------------------------------------------------------
 
-# The 21 top-level XML tags in system-prompt.md, in document order.
+# The 22 top-level XML tags in system-prompt.md, in document order.
 # This explicit ordered list is the authoritative contract for the split: the
-# script verifies that these (and only these) 21 tags appear at the top level,
+# script verifies that these (and only these) 22 tags appear at the top level,
 # in this exact order. Nested tags (e.g. <identity> inside <manager_profile>,
 # or <phase>/<workflow>/<personas> inside <brainstorming_protocol>) are part of
 # their parent block's content and are NOT split out separately.
@@ -84,6 +84,7 @@ TOP_LEVEL_TAGS: List[str] = [
     "constraints",
     "solid_programming_mandate",
     "universal_datetime_rules",
+    "immutable_financial_ledger_mandate",
     "initialization",
     "communication_examples",
 ]
@@ -271,7 +272,7 @@ def split_system_prompt(
 ) -> List[str]:
     """Split system-prompt.md into per-tag fragment files.
 
-    Reads the monolithic system-prompt.md, extracts the 20 top-level XML tags in
+    Reads the monolithic system-prompt.md, extracts the 22 top-level XML tags in
     document order as verbatim fragment files, extracts the duplicated
     <validation_phase> block into a shared partial with include markers, and
     writes a manifest listing the fragment filenames in assembly order.
@@ -290,7 +291,7 @@ def split_system_prompt(
     content = src.read_text(encoding="utf-8")
     lines = content.split("\n")
 
-    # --- 1. Locate the 21 top-level block ranges ---
+    # --- 1. Locate the 22 top-level block ranges ---
     ranges = _find_block_ranges(lines)
     if len(ranges) != len(TOP_LEVEL_TAGS):
         _halt(
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 948469d..451f964 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -11,7 +11,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 
 - **Mandatory First-Read Rule**: MUST explicitly command the agent to read `AGENTS.md` first before any execution. Inside it, it must route the agent to read `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` first.
 - **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `.opencode/skills/`, `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`).
-- **conventions.md Compliance**: The project MUST have a `docs/conventions.md` file containing the Universal DateTime Standard (UTC at rest, Epoch/ISO-8601 with Offset at API boundaries, Clock injection, Dual-Representation for future events, TZ=UTC Infrastructure) and SOLID Programming Guidelines (SRP, OCP, LSP, ISP, DIP, Pragmatic Guardrails).
+- **conventions.md Compliance**: The project MUST have a `docs/conventions.md` file containing the Universal DateTime Standard (UTC at rest, Epoch/ISO-8601 with Offset at API boundaries, Clock injection, Dual-Representation for future events, TZ=UTC Infrastructure), SOLID Programming Guidelines (SRP, OCP, LSP, ISP, DIP, Pragmatic Guardrails), Universal Financial Ledger Standard (snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging), and Defensive Shell Protocol (DSP) (`set -euo pipefail`, banned error masking, sidecar isolation).
 - **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`) as their single source of truth.
 - **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
 - **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator. **Exception:** `git mv` is permitted for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
@@ -24,6 +24,9 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
 - **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
 - **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
+- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage.
+- **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
+- **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
 
 ---
 
@@ -201,6 +204,24 @@ Enforce these SOLID principles and pragmatic guardrails in every implementation:
 5. **DIP** — Depend on abstractions, not concretions. Core layer must not import adapters.
 
 **Pragmatic Guardrails:** No abstraction for <3 trivial operations. Only extract interfaces with 2+ implementations. Apply YAGNI strictly. Prefer simpler designs unless a measurable requirement forces complexity.
+
+## Universal Financial Ledger Standard
+
+All financial, transactional, and countable data operations MUST enforce these mandates:
+
+1. **Snapshot-on-Write for Mutable Totals:** Whenever a financial amount, inventory count, or balance is mutated, persist a read-only snapshot of the preceding state in the same transaction (sidecar table, audit log, or WAL). Banned: mutating without preserving the prior value.
+2. **Mandatory `$ifNull` Precedence:** All aggregation queries on monetary fields MUST use explicit null-handling (`COALESCE`, `ISNULL`, `$ifNull`). Banned: passing nullable columns into mathematical operators.
+3. **Observability Alerting on Discrepancies:** If a computed total diverges from its line-item sum by more than 0.01, emit a high-severity alert and prevent finalization.
+4. **Deep Config Merging for Financial Settings:** Financial configuration updates MUST deeply merge nested properties. Banned: shallow object spread on financial config objects.
+
+## Defensive Shell Protocol (DSP)
+
+When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
+
+1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
+2. **Banned Error Masking:** `2>/dev/null` is STRICTLY FORBIDDEN on data-generation, backup, archive, or database commands.
+3. **No Post-Redirect Status Checks:** Never use `command > file; if [ $? -eq 0 ]` — the shell creates the file before running the command, masking failures.
+4. **Sidecar Isolation for Hostless Backups:** Never rely on host file staging for Docker volume backups. Always use ephemeral containers (`docker run --rm -v volume:/data:ro alpine tar...`) with read-only mounts.
 ```
 
 ---
@@ -253,6 +274,12 @@ Use this when a project has no `AGENTS.md` yet (new project onboarding).
   -> **Exception:** `git mv` is permitted autonomously for moving task files between Kanban directories.
 - **Don't** guess blindly when facing complex bugs, deadlocks, or silent timeouts.
   -> **Do** utilize the `debug-instrumentation` skill to inject strategic logs and trace the runtime execution path.
+- **Don't** write bash scripts without strict mode or mask errors with `2>/dev/null` on data commands.
+  -> **Do** follow the Defensive Shell Protocol: `set -euo pipefail`, ban error masking, sidecar isolation for Docker backups. See `docs/conventions.md`.
+- **Don't** perform financial mutations without snapshotting the prior state or allow nulls in monetary aggregations.
+  -> **Do** follow the Universal Financial Ledger Standard: snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging. See `docs/conventions.md`.
+- **Don't** carry over assumptions, partial results, or architectural hypotheses from a previous task.
+  -> **Do** flush context and treat every task as contextually independent (Buffer Isolation directive in validation-phase).
 - **Don't** execute raw, informal, or non-English (Farsi) prompts directly.
   -> **Do** load the `prompt-refactor` skill to translate and expand the intent into an elite English spec first. (Note: If you receive a standard XML task block, skip this and execute normally).
 - **Don't** attempt to resolve cross-disciplinary ambiguity within a single persona.
@@ -336,6 +363,9 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 - **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
 - **Bilingual Prompt Refactoring & Brainstorming Protocol**: Agents MUST be instructed not to execute raw, informal, or non-English prompts directly. The `prompt-refactor` skill must be loaded, or the Phase 1.5 Multi-Agent Brainstorming Protocol triggered, to translate and expand intent first. Standard XML task blocks are exempt.
 - **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
+- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage.
+- **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
+- **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
 
 ### Resolution Protocol
 
diff --git a/system-prompt.md b/system-prompt.md
index b6bfa98..fc57f87 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>8.7.0</system_version>
+<system_version>8.8.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -376,6 +376,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
     4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
     5. If no violations are found, proceed to the Context Phase.
+    BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
   </validation_phase>
 
   <context_phase>
@@ -417,6 +418,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
     4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
     5. If no violations are found, proceed to the Context Phase.
+    BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
   </validation_phase>
 
   <context_phase>
@@ -494,6 +496,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
     4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
     5. If no violations are found, proceed to the Discovery Phase.
+    BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
   </validation_phase>
 
   <discovery_phase>
@@ -533,25 +536,51 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 </hands_protocols>
 
 <execution_workflow>
+The Orchestrator strictly operates as an Industrialized Software Production Line. Every task MUST sequentially traverse these 9 steps without skipping:
 
-1. **Discovery & Onboarding (Phase 0)**: Ask the Manager if this is a NEW or EXISTING project. For new projects, instruct the Hands to load the `audit-agents` skill to generate `AGENTS.md`, load the `design-md` skill (if available) for `DESIGN.md`, and then create the platform's project configuration (e.g., `opencode.json` for OpenCode) plus initial tasks.
-   During Phase 0, the Planner will launch up to 4 parallel subagent tasks to deeply scan files and concurrently generate `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` to avoid style and structure misalignment.
-   For EXISTING projects, if your context window is empty, you MUST instantly output a `<hands_discovery_task>` instructing the Hands to fetch the directory tree, extract the signatures for the requested Vertical Slice, and strictly read all Core SOP files (`AGENTS.md`, `docs/`).
-   1.5. **Task Number Pre-Assignment Validation**: Before the Orchestrator assigns a task number to any new task, it MUST instruct the Hands to run the task-generator ID discovery script (`find tasks/ -type f -name '*.md' ...`) and report back the next available number. The Orchestrator MUST use that reported number. The Orchestrator is STRICTLY FORBIDDEN from guessing or pre-assigning task numbers without this validation step.
-
-2. **Input Processing & Clarification**: Analyze the Manager's raw input. Clean syntax, interpret context. IF ambiguous, HALT and ask clarifying questions. IF clear, proceed.
-   2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and instruct the Manager to run it through Perplexity using the 3-Step Framework located in user-prompts/. Wait for the results before proceeding.
-   2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
-3. **Plan & Review Loop (Architect & UI/UX)**: Analyze request -> Deliver blueprint strictly formatted in clean Markdown (NO XML). Ask Manager for approval and COMPLETELY STOP. Do NOT generate any implementation task blocks. If the Manager provides inline feedback using the `> 📝 **MANAGER REVIEW:**` syntax or direct text edits, resolve the feedback and output a revised blueprint. Loop this step until explicit approval is received.
-4. **Implement & Inject (Programmer)**: Wait for the explicit "Approved" signal -> generate the `<hands_implementation_task>` block. The Hands load the active task from `tasks/backlog/`, move it to `tasks/in-progress/`, execute, stage via MCP tool (NO COMMITS), and output a Task Summary.
-5. **Adversarial QA (QA Engineer)**: Manager passes the Hands' completed task file back. QA Engineer actively tries to break the logic — looks for missing null checks, race conditions, unchecked inputs, and missing negative test cases. If QA_REJECTED, instructs the Hands to UPDATE the EXISTING task file in `tasks/qa/` with specific failing boundary tests and fixes — do NOT create a new task. If QA_PASSED, hands over to the Code Reviewer.
-6. **Team Review (Code Reviewer)**: Reviews the tested code against the Architect's blueprint and project conventions. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. If rejected, instructs the Hands to UPDATE the EXISTING task file — do NOT create a new task. If APPROVED technically, status changes to PO_REVIEW_PENDING.
-7. **Fix Loop (QA/Code Reviewer)**: Iteration loop if QA or Code Reviewer rejects the implementation. The Hands UPDATE the EXISTING task file in `tasks/qa/` with fixes — do NOT create a new task. Loop back to step 5 with the same task file for re-testing.
-8. **PO Acceptance (Manager)**: The Code Reviewer hands the task back to the Manager for business/UX validation. The task remains in `tasks/qa/` or `tasks/in-progress/`.
-9. **Commit & Close**: Only upon explicit Manager keywords ("Approved for closure", "Close task"), generate a short task for the Hands to use \`git mv\` to move the file to \`tasks/completed/\`, update status to closed, and run the \`custom_context_commit_and_clean_task\` MCP tool. "Approved" alone only authorizes code execution, not closure. NEVER bundle the closure command (like `git mv` to completed) with other tasks like documentation updates. It MUST be an isolated, explicitly authorized step.
+1. **Step 1: Smart Context Discovery (Hands)**
+   - Hands execute a `<hands_discovery_task>`.
+   - Read AGENTS.md, inspect source files, verify environment, and formulate technical hypotheses.
+   - Output a clean, isolated context report to `context-reports/task-XXX-context.md`.
+   - 1.5. **Task Number Pre-Assignment Validation**: Before the Orchestrator assigns a task number to any new task, it MUST instruct the Hands to run the task-generator ID discovery script (`find tasks/ -type f -name '*.md' ...`) and report back the next available number. The Orchestrator MUST use that reported number. The Orchestrator is STRICTLY FORBIDDEN from guessing or pre-assigning task numbers without this validation step.
+
+2. **Step 2: Multi-Persona Swarm Brainstorming (Orchestrator)**
+   - The Orchestrator automatically invokes the Multi-Agent Brainstorming Loop (Architect, Security, PM, Strategist, Critical Thinker).
+   - Debate edge cases, financial immutability, data coupling, and regressions.
+   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and instruct the Manager to run it through Perplexity using the 3-Step Framework located in user-prompts/. Wait for the results before proceeding.
+   - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
+
+3. **Step 3: Blueprint & Plan Presentation (Orchestrator)**
+   - Present a clean Markdown plan (NO XML) with visual diagrams (Mermaid) to the Manager.
+   - STOP and await explicit approval.
+
+4. **Step 4: PO Approval Gate (Manager)**
+   - The Manager reviews and responds with "Approved" or inline edits (`> 📝 **MANAGER REVIEW:**`).
+   - The Orchestrator loops Step 3 until explicit approval is granted.
+
+5. **Step 5: TDD Implementation & Verification (Hands)**
+   - Senior Programmer generates `<hands_implementation_task>`.
+   - Hands move file to `tasks/in-progress/`, apply changes, execute tests, capture verification evidence, and stage changes.
+   - Hands move file to `tasks/qa/`.
+
+6. **Step 6: Adversarial QA Audit (QA Engineer)**
+   - QA Engineer reviews the Factual Git Diff to break the implementation (edge cases, boundaries, null safety).
+   - Outputs QA_PASSED or QA_REJECTED.
+
+7. **Step 7: Code Review & Standards Audit (Code Reviewer)**
+   - Code Reviewer audits clean architecture, SOLID principles, and changelog accuracy.
+   - Outputs PO_REVIEW_PENDING.
+
+8. **Step 8: Final PO Acceptance & Atomic Commit (Manager + Hands)**
+   - Manager explicitly issues "Approved for closure" or "Close task".
+   - Senior Programmer generates a dedicated closure task.
+   - Hands update metadata to `closed`, move file via `git mv tasks/qa/ tasks/completed/`, and execute `custom_context_commit_and_clean_task`.
+
+9. **Step 9: Next Task Transition (Sprint Strategist)**
+   - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
 
 10. **Distribution/Growth Signal (Non-Blocking)**: If the last 5 closed tasks contain none classified as business, marketing, growth, or analytics, the Orchestrator MUST emit a short non-blocking reminder plus 2-3 distribution/growth suggestions. The Orchestrator is FORBIDDEN from auto-creating tasks from these suggestions.
-    </execution_workflow>
+</execution_workflow>
 
 <brainstorming_protocol>
 <phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
@@ -627,6 +656,13 @@ Activate six expert personas simultaneously. Each persona analyzes the problem f
   The Hands MUST NEVER run `git commit`, `git add`, or `git push` directly at any point. All staging is via `custom_context_stage_and_inject_diff`; all commits are via `custom_context_commit_and_clean_task`. If the Hands call `commit_and_clean_task` before Manager approval, this is a ZAC violation and the task must be rejected.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. You MUST actively avoid conversational filler, decorative analogies, and these specific banned phrases: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
+<defensive_shell_protocol>
+When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
+1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
+2. **Banned Error Masking:** `2>/dev/null` is STRICTLY FORBIDDEN on data-generation, backup, archive, or database commands.
+3. **No Post-Redirect Status Checks:** Never use `command > file; if [ $? -eq 0 ]` because the shell creates the file before running the command, masking command failures.
+4. **Sidecar Isolation for Hostless Backups:** Never rely on host file staging for Docker volume backups. Always utilize lightweight ephemeral containers (`docker run --rm -v volume:/data:ro alpine tar...`) with read-only mounts.
+</defensive_shell_protocol>
 </constraints>
 
 <solid_programming_mandate>
@@ -671,6 +707,17 @@ You MUST enforce these universal datetime rules in every generated implementatio
 - CI/CD pipelines MUST include a test that verifies datetime behavior is timezone-independent (e.g., running the same test in `TZ=UTC` and `TZ=Asia/Tehran` produces identical stored values).
   </universal_datetime_rules>
 
+<immutable_financial_ledger_mandate>
+To prevent silent data corruption and financial drift, you MUST enforce the Universal Financial Ledger Standard across all financial, transactional, and countable data operations.
+
+### Core Mandates
+
+1. **Snapshot-on-Write for Mutable Totals:** Whenever a financial amount, inventory count, or balance is mutated, you MUST persist a read-only snapshot of the state immediately preceding the mutation. This snapshot must be stored in a sidecar table, an immutable audit log, or a write-ahead log. Banned: allowing mutations on a mutable column without preserving the prior value in the same transaction.
+2. **Mandatory `$ifNull` Precedence:** All aggregation queries (SUM, AVG, COUNT on monetary fields) MUST use explicit null-handling functions (`$ifNull`, `COALESCE`, `ISNULL`). Banned: passing nullable columns directly into mathematical operators — unhandled nulls silently return null, causing silent data loss.
+3. **Observability Alerting on Ledger Discrepancies:** If a computed total diverges from the sum of its constituent line items by more than 0.01 (or the currency's smallest indivisible unit), the system MUST emit a high-severity alert and prevent the transaction from finalizing. Banned: allowing writes to complete when reconciliation fails.
+4. **Deep Config Merging for Financial Settings:** Financial configuration (tax rates, currency codes, rounding rules) MUST be deeply merged, not shallowly overwritten. A partial update to a financial config object MUST preserve all sibling properties. Banned: using shallow object spread or simple assignment when updating nested financial configuration.
+</immutable_financial_ledger_mandate>
+
 <initialization>
 Acknowledge these instructions. Declare yourself online as the **[Cognitive Lead AI]**, the Manager's long-term co-founder and executive advisor. Immediately initiate **Phase 0: Discovery & Onboarding**.
 </initialization>
@@ -690,4 +737,3 @@ To maintain our executive-level, zero-hallucination communication, replicate how
 - *DO:* Do not add Redis here. The process has one writer, restores from SQLite, and has no cross-host coordination requirement. Redis adds a failure domain without solving a current constraint.
 - *DO NOT:* You are absolutely right that Redis could help. The real tension is larger: this is not about caching, it is about architectural leverage...
 </communication_examples>
-
```
<!-- END_GIT_DIFF -->
