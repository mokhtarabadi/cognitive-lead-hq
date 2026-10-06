# Slice: skill-templates

## Duties

Project-agnostic skill template catalog: source of truth copied into `.opencode/skills/` workspaces and third-party projects. Covers stacks (Android, Spring, Next.js, FastAPI, etc.), workflows (task-generator, archive-tasks, bundle-tasks, testing-strategy), and platform bridges (Telegram, GitHub, Blowsh).

## Files

- `*/SKILL.md` — One directory per skill (35 templates: `android-kotlin`, `audit-agents`, `bundle-tasks`, `task-generator`, `prompt-refactor`, `verification-before-completion`, `init-folder-docs`, and others).
- `opencode-init/references/` and `opencode-init/scripts/` — Init scaffolding references and helpers.

## Key Risks & Invariants

- HQ-only scaffolding (`09-hands_protocols.md` rules, prompt fragments) must never leak into project-agnostic templates.
- Task-number references live only in code comments, CHANGELOG, task files, and HTML comments; never in prompt prose.
- Template edits propagate to all downstream projects; keep them project-agnostic.
