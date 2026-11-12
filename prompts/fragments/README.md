# Slice: fragments

## Duties

Authoritative system-prompt sources: one file per top-level XML tag in `system-prompt.md` (version, role, personas, skills registry, Hands protocols, execution workflow, brainstorming, constraints, mandates). Assembled in `manifest.txt` order.

## Files

- `01-system_version.md` — Version identifier (must bump on `system-prompt.md` edits).
- `02-role.md` — Executor role definition.
- `03-system_context.md` through `08-agentic_reasoning.md` — Context, objective, input processing, skills, reasoning.
- `06-personas-catalog.md` — The always-shipping part of the persona block: the `<personas>` wrapper plus the `<auto_load>` rules. The seven `<persona>` blocks live in `personas/` so a stage prompt can carry only the seats it needs.
- `personas/<slug>.md` — One verbatim persona slice per seat (`software-architect`, `ui-ux-designer`, `senior-programmer`, `project-planner`, `sprint-strategist`, `qa-engineer`, `code-reviewer`). Assembled in the order `prompts/stage-manifest.json` declares.
- `09-hands_protocols.md` — Hands protocols with `<!--INCLUDE:-->` markers (HQ-only AC/DoD rules live here).
- `11-execution_workflow.md` through `16-immutable_financial_ledger_mandate.md` — Workflow, brainstorming, constraints, SOLID/datetime/ledger mandates.
- `18-no_manual_dto_mandate.md` through `21-self_improvement_protocol.md`, plus `24-language_policy.md` — DTO ban, init, communication examples, self-improvement, language policy. The retired `22-compaction_protocol.md` lives in `prompts/archive/` and is never assembled: the system prompt carries no compaction or plugin knowledge.

## Key Risks & Invariants

- Never edit `system-prompt.md` directly; edit fragments then run the assembler.
- Fragment order is fixed by `prompts/manifest.txt`; renames break the build.
- A persona slice is copied VERBATIM from its seat. The assembler re-splices the slices to rebuild the full prompt, so one changed byte in a persona body changes the shipped prompt.
- `prompts/stage-manifest.json` is the single routing table for stage-to-persona mapping; the assembler and the bridge both read it. Never hard-code a stage mapping in either.
- A stage prompt carries only its declared personas. A stage artifact that leaks another seat breaks the scope contract the QA and review turns rely on.
- HQ-only fragments (`09-hands_protocols.md`) must not leak into project-agnostic audit templates.
- Automatic-mode QA and review `brain_turn` calls are invoked by the Hands under the same `task_id`; the Manager does not ferry task text.
