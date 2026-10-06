# Slice: fragments

## Duties

Authoritative system-prompt sources: one file per top-level XML tag in `system-prompt.md` (version, role, personas, skills registry, Hands protocols, lite mode, execution workflow, brainstorming, constraints, mandates). Assembled in `manifest.txt` order.

## Files

- `01-system_version.md` — Version identifier (must bump on `system-prompt.md` edits).
- `02-role.md` — Executor role definition.
- `03-system_context.md` through `08-agentic_reasoning.md` — Context, objective, input processing, personas, skills, reasoning.
- `09-hands_protocols.md` — Hands protocols with `<!--INCLUDE:-->` markers (HQ-only AC/DoD rules live here).
- `10-lite_mode_protocol.md` through `16-immutable_financial_ledger_mandate.md` — Lite mode, workflow, brainstorming, constraints, SOLID/datetime/ledger mandates.
- `18-no_manual_dto_mandate.md` through `22-compaction_protocol.md` — DTO ban, init, communication examples, self-improvement, compaction.

## Key Risks & Invariants

- Never edit `system-prompt.md` directly; edit fragments then run the assembler.
- Fragment order is fixed by `prompts/manifest.txt`; renames break the build.
- HQ-only fragments (`09-hands_protocols.md`) must not leak into project-agnostic audit templates.
