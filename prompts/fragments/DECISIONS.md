# Architectural Decisions: fragments

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-12] ADR-002: Dual-mode Brain XML emission rule

- **Context:** Manual mode needs forced ```xml fences for copy-paste; automatic mode needs bare XML for direct MCP execution.
- **Decision:** Programmer, QA hotfix, and Reviewer postfix personas carry the per-MODE emission rule; bridge extracts both shapes.
- **Consequences:** No re-emit loop in either mode; version bumped with artifact regen.
- **Rollback:** Revert persona wording to prior revision and re-run the assembler.

## [2026-10-21] ADR-003: Plugin lanes become executable contract, not prose

- **Context:** The goal, todolist, and smart-compact plugin lanes were described in trailing prose outside every task template, so nothing ever triggered them. `goal_set` had no create trigger at all and the goal lane was unreachable; the todowrite rule fired only for implementation checklists; the task-boundary compaction trigger was missing; and several citations named code that does not exist at the stated lines.
- **Decision:** Each lane becomes an executable step inside the task templates it belongs to — Lane G (goal) in the implementation template, Lane T (todolist) in the implementation and combined templates, Lane C (smart-compact) in the compaction protocol — each carrying its exact tool names, parameters, WHEN trigger, error strings, and forbidden actions. The Brain states its tool-less boundary in the persona fragments and expresses intent through a `plugin_directives` sub-block carried inside the XML it already emits, so no bridge allowlist change is needed. Stale citations were replaced with the real ones: the idle gate at `src/loop.ts:458-492`, the handler at `src/loop.ts:552-853`, and the stop file read at `src/index.ts:284-296`.
- **Consequences:** The three lanes fire on a stated trigger instead of a Manager reminder, the Brain-to-Hands intent path is deterministic rather than prose, and the prompt text matches the plugin source. Version bumped and the artifact regenerated.
- **Rollback:** Revert the fragment and persona wording to the prior revision and re-run the assembler.

## [2026-10-21] ADR-004: The system prompt goes plugin-blind; the executor owns the lanes

- **Context:** Review of the lane design showed lanes inside the prompt still teach the Brain plugin machinery, which contradicts the Brain/Hands split. The Manager ordered the knowledge moved: the prompt emits only a plan and checklist, the executor maps them onto tools.
- **Decision:** Remove the plugin-directives schema, the lane blocks, and the trailing goal note from the Hands protocol fragment; rephrase both persona mandates to todo-list (micro-list) language with a single context-executor boundary sentence; archive the compaction fragment out of the manifest and the splitter tag list; expand the executor with the full lane surface (signatures, triggers, error strings, caps, parameter contract) instead.
- **Consequences:** The assembled prompt shrinks and carries zero tool names; the lane tests assert absence in the prompt and presence in the executor.
- **Rollback:** Restore the archived fragment to the manifest and tag list, revert the persona and protocol wording, and re-run the assembler.

