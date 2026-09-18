---
created_at: '2026-09-18T20:01:36.408335+00:00'
status: active
tags: []
updated_at: '2026-09-18T20:01:36.408360+00:00'
---

MCP tool audit 2026-09-18: 28 tools across 5 servers. Strong: decision-server (WHEN TO CALL on all 6), lint-server (4 clear), context power tools stage/qa/commit/bundle. Weak: basic context tree/read/signatures + memory CRUD store/read/delete/list (one-line, no when-to-use, confusing look-alikes, path-return surprise) + brain file-pull bundle/read/grep (one-line, workflow only in docs). Issues: brain_turn rich doc but missing @mcp.tool in file (exposed as default.brain_brain_turn); private _note_checkpoint exposes public tool. Follow-ups: add when-to-use + compare lines, hide private tool, fix export match. DESIGN/architecture/data_model absent, skipped per policy.