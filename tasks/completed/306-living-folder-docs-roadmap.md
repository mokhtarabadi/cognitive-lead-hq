# Task 306: Living folder docs roadmap

**File:** `tasks/completed/306-living-folder-docs-roadmap.md`
**Source:** manager
**Type:** feature
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `accbcd54154e35641907e4f711d04bb61bf4fc6c`
<!-- END_GIT_DIFF -->
