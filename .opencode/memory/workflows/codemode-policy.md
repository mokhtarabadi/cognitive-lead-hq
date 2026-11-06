---
created_at: '2026-10-29T06:47:37.577473+00:00'
status: active
tags: []
updated_at: '2026-10-29T06:47:37.577501+00:00'
---

# Code Mode policy (OpenCode v2, 2026-10-29)

Per-server flag: `mcp.servers.<name>.codemode` (default true = tools behind `execute`).

Policy in force (2026-11-06): EVERY server runs in Code Mode (`codemode: true`, the default). `custom_context`, `project_memory`, `lint`, `brain`, `planner`, `blowsh` and `telegram` are all `execute` wrappers — no MCP tool schemas enter the system prompt. Cost accepted by explicit Manager order: one `execute` hop per call.

Apply by editing `~/.config/opencode/opencode.json` after a timestamped backup, then validating with `python3 -c "import json;json.load(open(...))"`. The flag is host-level: the singleton services do not change, and an OpenCode/session restart applies it. Do NOT use this flag to hide individual tools — that is `permission` on the normalized `<server>_<tool>` name.

Docs: `docs/services.md` (policy table), `docs/setup.md`, `README.md` Option B, `LLM.txt` install block.