---
created_at: '2026-08-21T09:36:48.823393+00:00'
status: active
tags: []
updated_at: '2026-08-27T09:30:00.000000+00:00'
---

**Pattern (2026-08-21, updated 2026-08-27):** The `code-search` skill has two copies that must stay in sync: `skill-templates/code-search/SKILL.md` (source of truth) and `~/.config/opencode/skills/code-search/SKILL.md` (OpenCode global). After editing the template, always `cp` to the global location. Both were identical before this edit.
