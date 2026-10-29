---
created_at: '2026-10-29T06:47:37.577473+00:00'
status: active
tags: []
updated_at: '2026-10-29T06:47:37.577501+00:00'
---

# Code Mode policy (OpenCode v2, 2026-10-29)

Per-server flag: `mcp.servers.<name>.codemode` (default true = tools behind `execute`).

Policy in force: EVERY server runs with `codemode: false` (native tools) except `telegram`. `custom_context` (16), `project_memory` (6), `lint` (4), `brain` (1), `planner` (11), `blowsh` (5) are direct calls — ~43 small tools total, all invoked per task, so the wrapper hop costs more than the schema saves. `telegram` (147 tools) stays in Code Mode: its schemas must not enter the system prompt.

Apply by editing `~/.config/opencode/opencode.json` after a timestamped backup, then validating with `python3 -c "import json;json.load(open(...))"`. The flag is host-level: the singleton services do not change, and an OpenCode/session restart applies it. Do NOT use this flag to hide individual tools — that is `permission` on the normalized `<server>_<tool>` name.

Docs: `docs/services.md` (policy table), `docs/setup.md`, `README.md` Option B, `LLM.txt` install block.