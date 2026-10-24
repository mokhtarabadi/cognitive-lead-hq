---
created_at: '2026-10-24T06:46:30.231400+00:00'
status: active
tags: []
updated_at: '2026-10-24T06:46:30.231422+00:00'
---

# MCP tool audit (2026-09-18) — HISTORICAL SNAPSHOT

**Status: historical.** This audit pre-dates the singleton migration (2026-09-29), the retirement of the manager-decisions MCP, and the addition of the planner. Read it as a dated observation, never as current state. Re-audit before acting on any follow-up listed here.

Snapshot: 28 tools across 5 servers.

Strong: lint-server (4 clear); context power tools `stage`/`qa`/`commit`/`bundle`.

Weak: basic context tree/read/signatures; memory CRUD store/read/delete/list (one-line, no when-to-use, confusing look-alikes, path-return surprise); brain file-pull `bundle`/`read`/`grep` (one-line, workflow only in docs).

Issues found then: `brain_turn` had a rich docstring but was missing the `@mcp.tool` decorator in the file (exposed as `default.brain_brain_turn`); private `_note_checkpoint` exposed a public tool.

Follow-ups recorded then: add when-to-use + compare lines, hide the private tool, fix the export match.

`DESIGN.md` / `docs/architecture.md` / `docs/data_model.md` were absent at the time and skipped per the Absent-File Policy.

Void findings: the decision-server portion of the original audit is dead — that server no longer exists (no directory, no unit, no config entry, port 8104 unused). Do not resurrect its findings.
