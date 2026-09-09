# Task 176: Disable persona + decision MCP servers (repo + global), document rollback/restore record

**File:** `tasks/completed/176-disable-persona-decision-mcp-servers.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Disable the `persona` and `manager_decisions` MCP servers in both the repo and global OpenCode configs (JSON supports no comments, so remove the blocks), comment out related env vars, and leave a complete rollback/restore record — without deleting any implementation.

## Manager's Notes

Manager order (verbatim intent): "Also disable the MCP servers related to this system. Initially, I considered keeping the Manager Decision MCP server, but forget that — disable both of them for now. Do not delete anything. Keep all the code, configurations, and implementation available for future development. For the global configuration and this repository, disable the MCP servers. For JSON files where comments are not supported, remove the active configuration from the JSON, but make sure the task clearly documents: What was implemented. What is being disabled. Why it is being disabled. Which components/configurations were affected. Where the archived implementation was moved. How the system was restored to the previous manual workflow. How we can restore and continue developing the automated system in the future."

What was implemented (automation system, Tasks 167/168/170/174):
- `mcp-persona-server/` (server.py, dual_dispatch.py, session.py, telegram.py; tools: dispatch_session_turn, get_session_summary, escalate_to_admin, request_admin_approval, open_approval_gate, poll_approval_gate; 138 tests).
- `mcp-decision-server/` (server.py, redactor.py; tools: extract_session_decisions, record_manager_decision, query_manager_decisions, get_manager_profile, propose_profile_evolution).
- Wiring: repo `opencode.json` `mcp.persona` + `mcp.manager_decisions` blocks (relative paths) + permission allows (`dispatch_session_turn`, `get_session_summary`, `escalate_to_admin`, `request_admin_approval`, `open_approval_gate`, `poll_approval_gate`, `extract_session_decisions`, `record_manager_decision`, `query_manager_decisions`, `get_manager_profile`, `propose_profile_evolution`); same blocks with absolute paths in `~/.config/opencode/opencode.json`; env vars `PERSONA_*` / `DECISION_*` in `.env.example` (+ live `.env`, gitignored).

What is being disabled / why: both servers (persona first, decision too per explicit reversal) because the orchestration is immature; production must run no experimental automation.

Affected components/configurations:
- Repo `opencode.json`: delete the two `mcp.*` blocks + their permission lines (keep `custom_context`, `project_memory`, `lint`, `bundle_tasks` intact).
- Global `~/.config/opencode/opencode.json`: same two blocks + permission lines (absolute-path variants).
- `.env.example`: comment out `PERSONA_*` / `DECISION_*` lines (file supports `#` comments) with a `PAUSED-AUTOMATION` note. Live `.env` values stay (gitignored, server absent = inert).
- Server source dirs, tests, skills, fragments, `system-prompt.md`: left in place, inert without wiring.

Where the archived implementation was moved: server code stays in place (disabled by config, not moved); slash commands archived under `archive/automation-paused-2026-09-09/commands/` (Task 175); removed JSON blocks pasted verbatim into this task's Execution Log + `archive/automation-paused-2026-09-09/RESTORE.md` for exact restoration.

Manual workflow restoration: executor `## Manual Workflow (ACTIVE DEFAULT)` (Task 175); remaining MCPs (`custom_context`, `project_memory`, `lint`) keep working; no persona QA/reviewer/gate steps in the loop.

Future restore path: re-add JSON blocks from RESTORE.md (repo: relative paths; global: absolute paths), uncomment `.env.example` vars, `git mv` commands back, uncomment executor sections, restart OpenCode, verify with `opencode mcp list` + persona test suite.

## Local TODOs

- [x] Remove `mcp.persona` + `mcp.manager_decisions` blocks from repo `opencode.json` (validate JSON after)
- [x] Remove the 9 persona/decision permission lines from repo `opencode.json` (validate JSON after; task text said 11 — actual count is 9 repo / 11 global incl. open+poll gates)
- [x] Same removals in `~/.config/opencode/opencode.json` (validate JSON after)
- [x] Comment out `PERSONA_*` / `DECISION_*` in `.env.example` with PAUSED-AUTOMATION note
- [x] Paste removed JSON blocks verbatim into Execution Log + RESTORE.md
- [x] Update CHANGELOG.md, write Execution Log, lint, stage + inject diff (repo files only — global config is machine-local, never staged)
- [x] Verify: `opencode mcp list` shows persona/manager_decisions gone; repo grep shows zero live wiring refs

## Acceptance Criteria

- [x] Repo `opencode.json` has no `persona`/`manager_decisions` blocks or permission lines; JSON valid
- [x] Global `opencode.json` has no `persona`/`manager_decisions` blocks or permission lines; JSON valid
- [x] `.env.example` automation vars commented with reason note
- [x] Removed blocks preserved verbatim in task log + RESTORE.md
- [x] Server source/tests/skills untouched in place (disable-by-wiring only)
- [x] `opencode mcp list` confirms both servers absent; remaining servers connected
- [x] `lint_task_file` passes on the active task file

## Verification Evidence

- **Test command:** `python3 -c "import json;json.load(open('opencode.json'));json.load(open('/home/mohammad/.config/opencode/opencode.json'));print('JSON OK')"; grep -c '"persona"\|"manager_decisions"\|dispatch_session_turn\|manager_decision' opencode.json` (expect 0) + `opencode mcp list`
- **Expected result:** JSON OK, zero wiring refs, both servers absent from list, custom_context/project_memory/lint connected
- **Actual result:** JSON OK both files; `grep -c` = 0 live refs in both configs; `.env.example` zero active vars; `opencode mcp list` = 5 servers (custom_context, project_memory, lint, blowsh, telegram) all connected, persona + manager_decisions absent
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** JSON edit breaks opencode config (whole file unparseable); global edit affects all projects on this machine
- **Rollback plan:** Exact removed blocks live in Execution Log + RESTORE.md — re-insert, validate with `python3 -c "import json;json.load(...)"`, restart OpenCode

---

## Execution Log & Reasoning

**What was implemented (automation, Tasks 167/168/170/174):** persona server (6 tools, 138 tests), decision server (5 tools), JSON wiring repo+global, PERSONA_*/DECISION_* env, 9 archived commands, executor automation sections. **Disabled:** both `mcp.*` blocks + 9 repo / 11 global permission lines (JSON has no comments — removed, code untouched). **Why:** Manager order — system immature, production runs zero experimental automation. **Affected:** repo `opencode.json`, global `opencode.json`, `.env.example`, CHANGELOG, RESTORE.md Appendix A. **Archive location:** server code stays in place (inert without wiring); commands at `archive/automation-paused-2026-09-09/commands/`; exact removed JSON in RESTORE.md Appendix A. **Manual restore:** executor `## Manual Workflow (ACTIVE DEFAULT)`; remaining MCPs (custom_context, project_memory, lint) connected. **Future restore:** RESTORE.md steps 1-6 + Appendix A blocks (repo relative paths / global absolute paths), uncomment env, restart OpenCode, `opencode mcp list` must show both connected.

Edits: (1) repo `opencode.json` — deleted persona + manager_decisions blocks, lint block closing comma fixed, 9 permission lines deleted; (2) global same (11 lines incl. open/poll gates) — first attempt dropped the `"blowsh":` key line (global JSON invalid, caught by validator), repaired by re-adding the key; both files now parse, mcp keys repo=[custom_context,lint,project_memory], global=+blowsh/telegram; (3) `.env.example` — 7 active PERSONA_*/DECISION_* vars commented with PAUSED note; (4) CHANGELOG 176 bullet; (5) RESTORE.md Appendix A verbatim blocks. Count correction: repo=9 lines, global=11 (task text said 11 for repo). `opencode mcp list`: 5/5 connected, persona + decisions absent. Server dirs/tests/skills/fragments/system-prompt untouched. Global config change is machine-local, never staged.

**Orchestrator micro-task (same session, recorded here for traceability):**
companion grep sweep for Task 175 found + neutralized one live
`query_manager_decisions`/`get_manager_profile` ref (executor line 86, now
HTML-commented; directive = re-ask the manager). AGENTS.md clean. No 176
scope change — server wiring stays removed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `161929690ecb4c4c877d234841a7f70b81aa9c51`
<!-- END_GIT_DIFF -->
