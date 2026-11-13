---
tags: [skills, opencode, openchamber]
---
# Skills load from ONE writable global root

OpenCode V2 / OpenChamber merge skills from several sources; V2 precedence runs built-ins -> Claude-compatible -> agent-compatible -> global OpenCode -> project -> explicit. On a clean V2 machine there is exactly **one writable global root**: `~/.config/opencode/skills`. The former `~/.agents/skills` root was a Freebuff-era artifact and was **removed 2026-11-13** (Task 399) together with the rest of the Freebuff footprint. Do not recreate it.

Roots to check after any skill change:
- `~/.config/opencode/skills` — the only global root to sync (24 skill dirs).
- `<project>/.opencode/skills` — overrides the global copies; clean it in the project itself.
- `~/.config/openchamber/run/instances/<id>/skills` — holds only `openchamber-extensions`; leave it alone.

Symptom of a stale second root: OpenChamber keeps listing retired skills no matter what is deleted globally. **Fix by deleting the extra root, not by syncing it** — two global roots is the drift itself.

**Fake-skill trap:** `cp -r skill-templates/*` also copies the root `DECISIONS.md` and `README.md`, which OpenChamber counts as fake skills. Always `rm -f ~/.config/opencode/skills/{DECISIONS.md,README.md}` after every copy, and keep the global count at exactly 24 skill DIRECTORIES with no stray `.md` at the skills root. The same trap exists for `~/.config/opencode/agents/`: only `cognitive-executor.md` and `cognitive-discovery.md` are global — the sibling `DECISIONS.md` / `README.md` are living-folder docs and must not be copied.
