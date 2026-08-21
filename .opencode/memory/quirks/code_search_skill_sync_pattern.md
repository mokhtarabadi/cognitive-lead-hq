---
created_at: '2026-08-21T09:36:48.823393+00:00'
status: active
tags: []
updated_at: '2026-08-21T09:36:48.823409+00:00'
---

**Pattern (2026-08-21):** The `code-search` skill has three copies that must stay in sync: `skill-templates/code-search/SKILL.md` (source of truth), `~/.config/opencode/skills/code-search/SKILL.md` (OpenCode global), `~/.agents/skills/code-search/SKILL.md` (Freebuff global). After editing the template, always `cp` to both global locations. All three were identical before this edit.