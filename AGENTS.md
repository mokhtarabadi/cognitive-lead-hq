# Cognitive Lead AI HQ — Project Context Hub

## 🛑 MANDATORY FIRST-READ RULE

The very first file the agent MUST read before performing any task is `AGENTS.md`.
This file acts as the primary router. You MUST load and read the following documents first before executing any code changes to guarantee 100% structural and stylistic alignment:

1. `DESIGN.md` — Enforces colors, typography, layout scale, component styling, and RTL Persian configurations.
2. `docs/architecture.md` — Defines project structure, layer boundaries, and key data flow policies.
3. `docs/data_model.md` — Defines database entities, schemas, pointers, and object relationships.
4. `docs/conventions.md` — Defines syntax rules, naming conventions, file boundaries, and localization paths.

> **Absent-File Policy:** If a referenced core file (e.g., `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`) does NOT exist in the repository, SKIP it gracefully with an explicit internal note. DO NOT HALT. DO NOT HALLUCINATE its contents. Proceed to the next step. This policy applies to all validation phases, discovery tasks, and implementation tasks.

## Project Overview

This repository is the Headquarters for the Cognitive Lead AI multi-agent system. It is a **documentation-only** repository containing system prompts, MCP servers, and Agent Skills (`SKILL.md`).

## Setup & Dev Commands

- Run custom context MCP: `uv run mcp-context-server/server.py`
- Format Markdown: `npx prettier --write "**/*.md"`

## Actionable Guardrails (Do's & Don'ts)

- **Don't** generate target application code (product features, user-facing apps) in this repository.
  -> **Do** write structured framework-specific SOPs and reusable Markdown templates.
  -> **Exception:** MCP servers (`mcp-context-server/`, `mcp-memory-server/`, `mcp-lint-server/`), maintenance scripts (`scripts/`), and tooling required for the Cognitive Lead AI platform itself ARE permitted.
- **Don't** edit `system-prompt.md` without updating the version identifier.
  -> **Do** increment the version inside `<system_version>` at the very top of `system-prompt.md`, update the active task file in `tasks/`, and log a formal entry in `CHANGELOG.md`.
- **Don't** read `context-reports/` markdown files yourself.
  -> **Do** generate them using the MCP server — context reports via `custom_context_read_source_files`, tree reports via `custom_context_create_tree_report` ("create a tree of the project") — and hand the file path to the Manager.
- **Don't** create monolithic state files like `TODO.md` or `STATE.md`.
  -> **Do** use the decentralized `tasks/` directory with individual task files as the single source of truth.
- **Don't** make UI/UX changes without consulting `DESIGN.md`.
  -> **Do** enforce the color palette, typography, spacing, and component styling defined in `DESIGN.md`.
- **Don't** execute `git add`, `git commit`, or `git push` autonomously or try to guess when to stage code — these commands are STRICTLY FORBIDDEN.
  -> **Do** execute Git commands ONLY when explicitly instructed by an Orchestrator task block. Otherwise, rely on the `custom_context_stage_and_inject_diff` MCP tool.
  -> **Exception:** the ONLY permitted autonomous Git operation is `git mv` for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
- **Don't** guess blindly when facing complex bugs, deadlocks, race conditions, or silent failures.
  -> **Do** utilize the `debug-instrumentation` skill to inject strategic logs and trace the runtime execution path.
- **Don't** write bash scripts without strict mode or mask errors with `2>/dev/null` on data commands.
  -> **Do** follow the Defensive Shell Protocol: `set -euo pipefail`, ban error masking, sidecar isolation for Docker backups. See `docs/conventions.md`.
- **Don't** perform financial mutations without snapshotting the prior state or allow nulls in monetary aggregations.
  -> **Do** follow the Universal Financial Ledger Standard: snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging. See `docs/conventions.md`.
- **Don't** carry over assumptions, partial results, or architectural hypotheses from a previous task.
  -> **Do** flush context and treat every task as contextually independent (Buffer Isolation directive in validation-phase).
- **Don't** execute raw, informal, or non-English (Farsi) prompts directly.
  -> **Do** ALWAYS process through the Input Validation Pipeline first: Validate → Translate → Enrich → Refactor → Execute. If the input is unclear, HALT and request clarification. NEVER proceed to task generation with unvalidated input. (Note: If you receive a standard XML task block, skip this and execute normally).
- **Don't** attempt to resolve cross-disciplinary ambiguity within a single persona.
  -> **Do** trigger the Multi-Agent Brainstorming Loop if the Manager explicitly requests brainstorming or a task exhibits cross-disciplinary ambiguity. Interpret the `<brainstorming_session>` results in backlog tasks as non-functional guidelines that govern execution.
- **Don't** apply the full 9-step production line for trivial, single-file changes.
  -> **Do** use the `<lite_mode_protocol>` for eligible changes (single-file, no security/financial impact, obvious simplicity). Escalate to Full Mode if implementation reveals hidden complexity. See `<lite_mode_protocol>` in the system prompt.
- **Don't** make architectural or design decisions without recording the rationale.
  -> **Do** log non-trivial decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>`. Lite Mode tasks must log a `[LITE]` justification entry.

## Documentation Sync Rules

When modifying this repository, you must keep these files synchronized:

1. Active task file in `tasks/` (single source of truth for current work items)
2. `CHANGELOG.md` (Keep a Changelog format)
3. `DESIGN.md` (UI/UX design system, if modified)
4. Relevant `SKILL.md` files (if structural patterns were altered)

## 🛑 GATEKEEPER VALIDATION (HALT PROTOCOL)

You (the Hands) are the final gatekeeper. Before executing any implementation task, you MUST evaluate the Orchestrator's instructions against this file and any referenced specs (`DESIGN.md`, `architecture.md`, etc.). If the instructions violate project rules, ignore them. HALT immediately and output a `⚠️ RULE VIOLATION WARNING` back to the Manager explaining exactly what the Orchestrator got wrong, forcing it to self-correct.

## 🛑 CORE FILE LOCATIONS

You MUST strictly adhere to these exact paths. Do not create duplicates elsewhere:

- **Global Rules:** `AGENTS.md` (Root)
- **UI/UX Specs:** `DESIGN.md` (Root)
- **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace)
- **Active Tasks:** `tasks/backlog/<task-number>-<name>.md` (backlog), `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`
- **Bundle Script:** `scripts/bundle-tasks.py` — deterministic meta-task bundler for `task-generator` (Task 110)

## 🛑 META-TASK BUNDLE LIFECYCLE (Task 110)

A meta-task bundles 2–6 small related tasks into one META for unified execution. This is a **fully automatic, script-driven** workflow (never manual copy-paste).

1. **Creation:** Manager runs `uv run scripts/bundle-tasks.py <id> <id> ... --title "<title>" [--dry-run]`. The script:
   - discovers `NEXT_ID` via `find tasks -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 +1` (ALL dirs including archive, no collision)
   - validates each ID exists in `tasks/backlog|in-progress|qa|completed` (active only, archive excluded), rejects >6 without `--force`, warns if combined LOC >400
   - slugifies `--title` to kebab-case, writes `tasks/backlog/<NEXT_ID>-<slug>.md` with canonical template + `**Supersedes:** [ids]` + `**Meta:** true` + per-source verbatim appendices (`### Source Task XX: Title` with Goal/AC/TODO/Risk copied verbatim, zero omission)
   - generates `## Bundled Checklist (All-or-Nothing)` — every source AC line prefixed `[XX]`, single QA gate
2. **Auto-Archive:** unless `--dry-run`, each source file is moved via `git mv <src> tasks/archive/<src>` (fallback to filesystem `mv` + `git add` for untracked) and patched:
   - `**File:**` → `tasks/archive/<file>`, `**Status:** superseded`, `**Superseded-By:** <META_ID>-<slug>`, `**Superseded-At:** YYYY-MM-DD`, superseded footer before `## Execution Log`
   - History stays reachable: `git log --oneline --follow -- tasks/archive/<file>` — never `git rm` until META reaches `tasks/completed/`
   - Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META
3. **Kanban:** META follows the normal lifecycle `tasks/backlog/<META>` → `tasks/in-progress/<META>` → `tasks/qa/<META>` → `tasks/completed/<META>` with one injected `Factual Git Diff`. QA is all-or-nothing: if ANY bundled criterion fails, the entire META is `QA_REJECTED`.
4. **Verification:** `uv run scripts/bundle-tasks.py --dry-run` for preview, `lint_task_file` on META, `git log --follow` on archived sources

## 🛑 SKILL LOADING RULES

You MUST follow these skill loading rules in every session:

- **Task-Generator Skill:** Before creating any new task file, you MUST load the `task-generator` skill using the `skill` tool to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
- **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `android-kotlin`, `spring-boot`, `react-vite`, `nodejs-express`, `python-fastapi`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.

## 🛑 CONTEXT BOOTSTRAPPING

At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing.

## 🛑 MANDATORY END-OF-TASK SEQUENCE

When finishing a task, you MUST execute these exact steps in order:

1. **Update Changelog:** You MUST insert a formal entry into CHANGELOG.md logging your modifications.
2. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active task file under "Execution Log & Reasoning".
3. **Call MCP Tool (Staging):** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path AND the `modified_files` array (list of all code files you changed) to automatically stage ONLY those files and inject the factual code diff. DO NOT execute any `git commit` commands afterward.
4. **QA Transition (implementation tasks only):** After successful staging, move the implementation task file from `tasks/in-progress/` to `tasks/qa/` via the explicitly authorized `git mv` — the ONLY autonomous Git operation, reserved for Kanban transitions. Discovery tasks stay in place. Do NOT move the task to `tasks/completed/` at this stage.
5. **Kanban Metadata Synchronization (mandatory after ANY authorized `git mv`):** After the move, you MUST update the task file's `**File:**` metadata header to the new path. If the move happened AFTER staging, you MUST also re-run `lint_task_file` and call `custom_context_stage_and_inject_diff` again using the NEW task path before notifying the Manager — the re-stage keeps the injected diff and the staging state in sync with the final path. Never notify the Manager with a stale `**File:**` header.
6. **Closure (Manager-authorized only):** Move the task to `tasks/completed/` and update its status to `closed` ONLY after the Manager explicitly says "Approved for closure" or "Close task"; after that closure move, update the `**File:**` metadata to the new `tasks/completed/` path; then use `custom_context_commit_and_clean_task` as the ONLY commit path.
7. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/qa/XX-task-name.md` and send it back to the Orchestrator Brain for review."

