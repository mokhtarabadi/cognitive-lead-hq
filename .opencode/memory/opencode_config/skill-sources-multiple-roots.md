---
tags: [skills, opencode, openchamber]
---
# Skills load from several roots, not just ~/.config/opencode/skills

OpenCode V2 / OpenChamber merge skills from multiple sources; V2 precedence runs built-ins -> Claude-compatible -> agent-compatible -> global OpenCode -> project -> explicit. In this machine the stale ones lived in `~/.agents/skills` (36 entries, all retired names) while `~/.config/opencode/skills` was already correct (24). Symptom: OpenChamber showed old skills no matter what was deleted globally. Fix: sync EVERY root to the canonical 24 and drop non-skill DECISIONS.md/README.md. Roots to check after any skill change: `~/.config/opencode/skills`, `~/.agents/skills`, `<project>/.opencode/skills`, `~/.config/openchamber/run/instances/<id>/skills` (only openchamber-extensions there). Deleting from one root is not enough.