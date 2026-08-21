---
created_at: '2026-08-21T09:32:41.877642+00:00'
status: active
tags: []
updated_at: '2026-08-21T09:32:41.877666+00:00'
---

**Bug Fixed (2026-08-21):** `extract_signatures` MCP tool in `mcp-context-server/server.py` was returning signature strings inline but never writing them to a markdown file under `context-reports/`. Fixed to mirror `read_source_files` and `create_tree_report` behavior: calls `_ensure_context_reports_ignored()`, writes to `context-reports/signatures_report_<ts>_<uuid>.md`, and returns the file path. All three context-producing tools now follow the same write-to-file pattern.