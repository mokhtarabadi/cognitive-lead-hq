# Slice: docs

## Duties

Human-readable spec hub for conventions, architecture-adjacent guides, service topology, and milestone history. Bound spec files (`conventions.md`, `brain-bridge.md`) govern Hands behavior.

## Files

- `conventions.md` — Syntax, naming, file boundaries, and automation patterns (bound spec).
- `brain-bridge.md` — Brain Bridge protocol reference for QA/review turns.
- `compaction.md` — Context compaction and smart-compact usage.
- `openchamber.md` — OpenChamber session linking guide.
- `opencode-shell-strategy.md` — Shell execution strategy.
- `services.md` — Service topology for MCP daemons.
- `setup.md` — Environment setup guide.
- `telegram-setup.md` — Telegram sync setup.
- `living-folder-docs-roadmap.md` — Rollout roadmap for Living Folder Docs.
- `workflow-upgrade-v8.4.5.md` — Workflow upgrade notes.
- `history/` — Per-milestone summaries (milestone-1 through milestone-22).

## Key Risks & Invariants

- `conventions.md` is a bound spec for QA/Reviewer seats; edits change quality gates.
- History summaries are append-only; never rewrite past milestones.
- New cross-cutting rules must also land in `AGENTS.md` and the active skill templates.
