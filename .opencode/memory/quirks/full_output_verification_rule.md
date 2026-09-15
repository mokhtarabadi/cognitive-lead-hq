---
created_at: '2026-09-15T20:11:19.990199+00:00'
status: active
tags: []
updated_at: '2026-09-15T20:11:19.990288+00:00'
---

Never trust truncated command output: `head`/`tail` cuts hid `manager_decisions` from `opencode mcp list` and caused a false dead-server alarm on 2026-09-15. Always re-run with full output (grep for status lines, not head) before claiming a server, test, or check result.