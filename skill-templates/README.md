# Slice: skill-templates

## Duties

Project-agnostic skill template catalog: source of truth copied into `.opencode/skills/` workspaces and third-party projects. Covers stacks (Android, Spring, Next.js, FastAPI, etc.), workflows (kanban-lifecycle, testing-verification, prompt-refactor), platform bridges (Brain orchestration, Telegram, GitHub, Blowsh).

## Files

- `*/SKILL.md` — One directory per skill (25 templates: `android-kotlin`, `brain-orchestration`, `governance`, `kanban-lifecycle`, `prompt-refactor`, `testing-verification`, `telegram-suite`, and others).
- `governance/templates/opencode-init/references/` and `governance/templates/opencode-init/scripts/` — Init scaffolding references and helpers.

## Key Risks & Invariants

- HQ-only scaffolding (`09-hands_protocols.md` rules, prompt fragments) must never leak into project-agnostic templates.
- Task-number references live only in code comments, CHANGELOG, task files, and HTML comments; never in prompt prose.
- Template edits propagate to all downstream projects; keep them project-agnostic.
- Portable-core split is test-enforced for versioning and Brain orchestration: harness identifiers and HQ repository paths belong only in the labeled optional profile or deployed-contract wording.
