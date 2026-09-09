---
description: Open the Telegram manager approval gate on the active task
---

# /manager — manager approval gate

Invoke `request_admin_approval` (persona MCP server) with:

- `task_id`: the active task number
- `stage`: the gate name (e.g. `QA`, `review`, `closure`)
- `summary`: what was implemented, verified, and what approval unlocks
- `task_file_path`: the active task file path

This posts an inline **Approve / Reject** keyboard to the manager via
Telegram and blocks until the manager decides (or the
`TELEGRAM_APPROVAL_TIMEOUT_SECONDS` window elapses).

Hard-gate rule: on `approve`, continue the pipeline. On `reject`, timeout,
or transport failure — STOP, record the outcome in the task file, and do
NOT auto-continue.
