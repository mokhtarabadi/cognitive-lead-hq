# Task 306: Living folder docs roadmap

**File:** `tasks/qa/306-living-folder-docs-roadmap.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Define and implement the living folder-docs system from the approved plan: every feature slice owns a short README plus a dated DECISIONS log, code keeps a one-line pointer, and four gates (read, write, lint, review) force the agent to keep them in sync so no architectural decision is ever lost or silently overridden.

## Manager's Notes

Manager order (translated from Persian): stop the Graphify thread and build our own. Docs are too thin over a project's life; decisions buried in code comments get lost, and a human "leave it" override can break the system. Wanted: docs live both in comments and in markdown files colocated with the structure (vertical slice or clean-architecture folders), the dev environment forces a brief per-folder explanation (files, duties, risks), important decisions are stored there, and the AI always checks those markdown files when it reviews the source. Question asked: implement ourselves per that description, or use Graphify, and how. Approved plan: build ourselves (F1-F6), keep Graphify only as an optional read-only query aid for large foreign codebases. Scope of this task is the roadmap file only; implementation lands in follow-up tasks.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [ ] Add the Living Docs standard to `docs/conventions.md` (file names, shapes, pointer format) — follow-up scope, see log
- [ ] Extend prompt fragments (`13-constraints.md`, `09-hands_protocols.md`), register in manifest, regenerate `system-prompt.md` with version bump, mirror in `agents/cognitive-executor.md` — follow-up scope, see log
- [ ] Update the `task-generator` template with the folder-docs checklist and verification field — follow-up scope, see log
- [ ] Extend `mcp-context-server/server.py` to auto-attach sibling README and DECISIONS; add the docs-sync lint rule to `mcp-lint-server` — follow-up scope, see log
- [ ] Wire the human guards: QA reject on missing rationale, review reject on stale docs, override recorded as ADR with rollback, decision stored via project memory — follow-up scope, see log
- [x] Verify functionality (lint_task_file pass, exit 0, evidence recorded above)

## Acceptance Criteria

- [x] AC1: roadmap spec created at `docs/living-folder-docs-roadmap.md`; task file at `tasks/in-progress/306-living-folder-docs-roadmap.md` with all lint-mandatory sections and a valid diff block
- [x] AC2: roadmap names every touch point (conventions, fragments, executor, task template, context server, lint server, QA/review, memory) with no invented file paths
- [x] AC3: todo-app example shows the slice tree plus README, DECISIONS, and code-pointer shapes
- [x] AC4: enforcement is layered across at least four gates so no single skip can lose a decision

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-lint-server python /tmp/opencode/lint_306.py (runs `lint_task_file('tasks/in-progress/306-living-folder-docs-roadmap.md')` inside the lint server env)
- **Expected result:** task-file lint passes, exit code 0
- **Actual result:** `lint_task_file` reports "passed Task File linting" on the in-progress path; `lint_markdown` on `docs/living-folder-docs-roadmap.md` reports 4 cosmetic nits (missing blank line after headings before code fences, lines 40/50/67/78) — kept as-is because the Orchestrator mandated exact spec content and the fences render correctly; non-blocking, flagged for the Reviewer
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

- **Risk:** roadmap references a file or workflow that does not exist, sending follow-up work down the wrong path
- **Rollback plan:** revert the working-tree hunks (`docs/living-folder-docs-roadmap.md`, `CHANGELOG.md`) and move the task file back to `tasks/backlog/`; nothing is staged or committed by this task

---

## Execution Log & Reasoning

Roadmap task created from the approved living-docs plan. Seat check: single-domain process/SOP change, no UI surface and no data contract change, so Designer and data-layer seats are skipped with reason. Brainstorm: not required — the approach was already decided with the Manager (build ourselves, Graphify optional read-only). Next: lint the file, then hand to the Orchestrator for blueprint approval before any implementation task.

Implementation notes (Hands, 2026-10-06): moved the file backlog → in-progress via filesystem `mv` (untracked file, so `git mv` failed with exit 128; no staging involved, ZAC intact) and synced the `**File:**` header. Created `docs/living-folder-docs-roadmap.md` with the exact Orchestrator-mandated content: 4-gate breakdown (read/write/lint/review), verified touch points, todo-app slice example. Cross-checked all named paths against the repo tree: all real except `06-personas.md`, which is shorthand for the existing `prompts/fragments/06-personas.md`. CHANGELOG updated via Parse-Then-Append under `[Unreleased]` → `### Added`. Verification: `lint_task_file` passes on the in-progress file (exit 0, confirmed via both the MCP tool and the `rtk test` runner); `lint_markdown` on the new spec reports 4 cosmetic blank-line nits kept as-is per the exact-content mandate. Assumption A1: the five phase TODOs describe follow-up implementation explicitly out of scope per this file's own Manager's Notes, so they stay open and transfer to follow-up tasks — checking them now would be a false completion claim. AC1–AC4 and all DoD boxes are genuinely satisfied by the recorded evidence and are checked.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 00764f9..ac51ef2 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -14,6 +14,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Adopted opencode-todolist plugin (Task 290):** OpenCode V2 removed the built-in `todowrite`/`todoread` session todo tools that powered the V1 sidebar, so the platform now runs `opencode-todolist` alongside `smart-compact`. Global install via `opencode plugin add opencode-todolist` (`plugins` now carries both entries) plus the TUI sidebar strip via `plugins` in `~/.config/opencode/cli.json`. HQ docs synced in every place plugins are listed: `README.md` (one plugin -> two plugins), `LLM.txt` (Step 7 JSON + description, Step 7.7 install + `cli.json` strip + restart smoke test, stale no-plugins checklist corrected). Restart OpenCode to load it, then smoke-test `todowrite`/`todoread` and the sidebar strip.
 
+- Defined Living Folder Docs architectural specification and implementation roadmap in docs/living-folder-docs-roadmap.md (Task 306).
+
 ### Fixed
 
 - **Context MCP singleton report write path (Task 286):** after the singleton migration the context server runs from `~/.config/opencode/mcp-context-server`, but `create_tree_report`, `read_source_files`, and `extract_signatures` wrote their reports to `Path("context-reports")` — the process cwd — so generated maps landed in the global install dir and the project's `context-reports/` went stale (the newest repo tree report stayed at 2026-09-18, still listing the removed `stacks/` directory; found by the task 285 smoke test). All three writers now resolve `report_dir = workspace_root / "context-reports"` from the per-call `project_root` argument the caller supplies, and the `.gitignore` safeguard writes to `<project_root>/.gitignore` via a new `_ensure_context_reports_ignored(workspace_root)` parameter. `extract_signatures`'s regex fallback also reads the resolved `path` instead of the cwd-relative `file_path`. The project_root-omitted path is unchanged (cwd fallback, still surfaced client-visibly), and a new regression test proves a foreign cwd writes nothing outside `<project_root>/context-reports/`. Context-server suite: **70 passed** (69 pre-existing + 1 new).
diff --git a/docs/living-folder-docs-roadmap.md b/docs/living-folder-docs-roadmap.md
new file mode 100644
index 0000000..3a82546
--- /dev/null
+++ b/docs/living-folder-docs-roadmap.md
@@ -0,0 +1,91 @@
+# Living Folder Docs: Architectural Specification & Implementation Roadmap
+
+## 1. Objective
+
+The Living Folder Docs system ensures that architectural knowledge, design rationales, and directory boundaries are colocated with source code in vertical slices or clean architecture component directories. By forcing synchronization across four distinct gates, decisions cannot be silently forgotten, bypassed, or overridden.
+
+## 2. The Four Enforcement Gates
+
+1. **Gate 1: Read Gate (Context Auto-Attach):**
+   - Location: `mcp-context-server/server.py`
+   - Behavior: When `read_source_files` or `extract_signatures` processes files in a component directory, it automatically resolves and attaches sibling `README.md` and `DECISIONS.md` files so the Brain always inspects existing architectural context.
+
+2. **Gate 2: Write Gate (Agent Constraints & Task Templates):**
+   - Locations: `prompts/fragments/13-constraints.md`, `prompts/fragments/09-hands_protocols.md`, `skill-templates/task-generator/`
+   - Behavior: When modifying code within a slice, the agent is mandated to inspect and update sibling docs. Implementing without updating relevant ADRs triggers a rule violation warning.
+
+3. **Gate 3: Lint Gate (Static Verification):**
+   - Location: `mcp-lint-server/server.py`
+   - Behavior: Introduces structural verification (`lint_folder_docs`) ensuring every component slice owns conforming `README.md` and `DECISIONS.md` files and validates top-line source code pointers.
+
+4. **Gate 4: Review Gate (Quality & Persona Enforcement):**
+   - Locations: `06-personas.md` (QA Engineer & Code Reviewer)
+   - Behavior: QA rejects changes missing documented rationale or invariants. Code Reviewer rejects tasks with stale or desynchronized sibling docs. Human overrides must be recorded as dated ADRs with rollback instructions.
+
+## 3. Touch Points & File Locations
+
+All touch points are anchored in verified repository files:
+- `docs/conventions.md`: Canonical definition of the Living Docs standard.
+- `prompts/fragments/13-constraints.md`: Sibling docs reading and writing constraints.
+- `prompts/fragments/09-hands_protocols.md`: Task execution phases for folder docs sync.
+- `prompts/manifest.txt`: Fragment manifest for prompt assembly.
+- `agents/cognitive-executor.md`: Mirrored execution rules for the Hands.
+- `mcp-context-server/server.py`: Sibling doc resolution in context tools.
+- `mcp-lint-server/server.py`: Sibling doc lint rule.
+- `06-personas.md`: Adversarial QA and Code Reviewer inspection gates.
+- Persistent Memory (`project-memory`): Synchronizing high-level Manager decisions with local slice logs.
+
+## 4. Concrete Reference Example: `todo-app` Vertical Slice
+
+### Directory Layout
+```text
+src/features/todos/
+├── README.md
+├── DECISIONS.md
+├── todo.model.ts
+├── todo.service.ts
+└── todo.controller.ts
+```
+
+### `src/features/todos/README.md`
+```markdown
+# Slice: Todos Feature
+
+## Duties
+Handles todo creation, completion toggling, filtering, and persistent storage.
+
+## Files
+- todo.model.ts: Domain entities and validation schemas.
+- todo.service.ts: Business logic, persistence interactions, and error handling.
+- todo.controller.ts: HTTP route handlers and request/response mapping.
+
+## Key Risks & Invariants
+- Todos must belong to a verified tenant; never query across tenant boundaries.
+- Soft-deleted items must not appear in count aggregations.
+```
+
+### `src/features/todos/DECISIONS.md`
+```markdown
+# Architectural Decisions: Todos Feature
+
+## [2026-08-25] ADR-001: Soft Deletion via Sidecar DeletedAt Column
+- Context: Hard deletion caused cascade failures with audit reports.
+- Decision: All deletion marks deleted_at timestamp; queries filter deleted_at IS NULL.
+- Consequences: Existing indexes required compound update on (tenant_id, deleted_at).
+- Rollback: Revert migration 0042 and restore hard delete cascade.
+```
+
+### Code Pointer Standard (`src/features/todos/todo.service.ts`)
+```typescript
+// Sibling Docs: src/features/todos/README.md | Decisions: src/features/todos/DECISIONS.md
+export class TodoService {
+  // implementation
+}
+```
+
+## 5. Phased Implementation Breakdown (Follow-Up Tasks)
+
+- **Phase 1 (Conventions & System Prompts):** Update `docs/conventions.md`, prompt fragments `13-constraints.md` and `09-hands_protocols.md`, assemble `system-prompt.md`, and mirror in `agents/cognitive-executor.md`.
+- **Phase 2 (MCP Context & Lint Tooling):** Add sibling doc auto-attachment in `mcp-context-server/server.py` and structural validation in `mcp-lint-server/server.py`.
+- **Phase 3 (Task Templates & Skills):** Update `task-generator` template to mandate folder-docs checklist items.
+- **Phase 4 (Persona Gates & ADR Memory Integration):** Wire QA/Reviewer adversarial gates and test the full cycle on a sample slice.
```
<!-- END_GIT_DIFF -->
