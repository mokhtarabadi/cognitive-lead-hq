# Task 336: Planner deployment and agent wiring

**File:** `tasks/completed/0336-planner-deployment-and-agent-wiring.md`
**Source:** manager
**Type:** feature
**Status:** completed

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Take the Planner MCP server from repo-local code to a live part of the platform: install it as a global singleton under `~/.config/opencode/mcp-planner-server/`, run it as a supervised systemd user unit on `127.0.0.1:8108`, register it in the global `opencode.json` so every session can call its tools, and wire the daily-pacing workflow into the executor protocol plus the provisioning docs.

## Manager's Notes

- The server itself shipped previously; this task is deployment, registration, and agent wiring only. No changes to the planning tool surface.
- Provisioning must stay reproducible: every deployment step taken by hand here belongs in `LLM.txt` so a fresh machine lands in the same state.
- The executor section must describe *when* to call each planner tool, not restate its implementation.
- `Claim next` is the circuit breaker: it is what stops unattended work from piling up behind an unresolved QA queue.

## Local TODOs

- [x] Create this task file with the canonical Kanban template
- [x] Deploy `mcp-planner-server` to `~/.config/opencode/mcp-planner-server/` (source, lockfile, static assets) and build its venv
- [x] Install and enable `mcp-planner.service`; confirm the unit is active and the port answers
- [x] Register the `planner` remote entry in the global `opencode.json` and confirm enumeration
- [x] Add the Planner MCP and Daily Pacing Protocol section to `agents/cognitive-executor.md`
- [x] Update `LLM.txt`: directory loop, copy block, config snippet, services loop, verification checklist
- [x] Update the `README.md` component tree and `CHANGELOG.md`
- [x] Run the verification suite and record evidence

## Acceptance Criteria

- [x] `~/.config/opencode/mcp-planner-server/` holds `server.py`, `pyproject.toml`, `uv.lock`, `README.md`, `DECISIONS.md`, and `static/index.html`, with a working `.venv`
- [x] `systemctl --user is-active mcp-planner` reports `active` and survives `daemon-reload`
- [x] `GET /` and `GET /api/status` on `127.0.0.1:8108` both return HTTP 200, and `/api/status` reports a non-zero task count for this repo (329)
- [x] The global `opencode.json` carries a `planner` entry under `mcp.servers` pointing at `http://127.0.0.1:8108/mcp`. Verified via `opencode debug config` (7 resolved `127.0.0.1:810*/mcp` entries) plus a live MCP handshake at that URL. `opencode mcp list` cannot confirm it: on v2.1.4 it prints "No MCP servers configured" for **every** entry, including the six servers this session is actively using, so it is a pre-existing CLI defect rather than a planner problem
- [x] `agents/cognitive-executor.md` documents `sprint_daily_agenda`, `claim_next`, and `sprint_check_daily_quota` with the conditions that trigger each call
- [x] `LLM.txt` provisions the planner in §4, §5, §7 and §7.5, and its verification checklist covers the new port
- [x] `README.md` lists `mcp-planner-server/` among the components
- [x] `python3 scripts/check_docs_sync.py` exits 0
- [x] `tests/test_planner_server.py` passes in full

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q`
- **Expected result:** all planner tests pass, `check_docs_sync.py` prints `docs-sync: OK` with exit code 0, the unit is `active`, and both HTTP probes return `200`
- **Actual result:** `31 passed` for the planner suite. `python3 scripts/check_docs_sync.py` prints `docs-sync: OK`. `systemctl --user is-active mcp-planner` prints `active` (and `is-enabled` prints `enabled`). `GET /` prints `200` and `GET /api/status` prints `200` with `total_tasks: 329`, `in_progress: 1`, `qa_pending: 0` for this repo. `opencode debug config` resolves 7 `127.0.0.1:810*/mcp` entries including `planner`.
- **Exit code:** 0 (docs-sync 0, pytest 0, all probes 200)

> Verification runner rule: the first verification run MUST use the `rtk test` prefix; a raw rerun is allowed only after a failed RTK run for diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task.

## Risk & Rollback

- **Risk:** A global install can shadow or break the existing singletons if the unit or the config entry is malformed; a bad `opencode.json` edit disconnects every MCP server for every session, not just the planner.
- **Rollback plan:** `systemctl --user disable --now mcp-planner`, remove `planner` from `mcp.servers`, and restore the backed-up `opencode.json` (a timestamped `.bak-*` is taken before editing). The install directory is additive and can be deleted without touching any other server. Task Markdown remains readable throughout, so planning degrades to the existing Kanban workflow.

---

## Execution Log & Reasoning

### What changed

The planner moved from repo-local code to a live platform singleton, and the
executor learned when to call it.

- **Global install** at `~/.config/opencode/mcp-planner-server/`: `server.py`,
  `pyproject.toml`, `uv.lock`, `README.md`, `DECISIONS.md`, and `static/`. The
  venv is built by `uv sync` from the committed lock (37 packages resolved).
- **Service**: `services/mcp-planner.service` copied into
  `~/.config/systemd/user/`, `daemon-reload`, `enable --now`. Unit is `active`
  and `enabled`, bound to `127.0.0.1:8108` only.
- **Registration**: `mcp.servers.planner` in the global `opencode.json`
  (`type: remote`, `http://127.0.0.1:8108/mcp`, timeout 15000/30000).
  Config was backed up first to `opencode.json.bak-20261024-0629-planner`;
  the file still parses and all six pre-existing entries are untouched.
- **Executor**: new *Planner MCP and Daily Pacing Protocol* section under
  Execution Discipline, next to the circuit breakers, because it is the same
  concern (workload control). It binds start-of-day, task-claim, end-of-day,
  and status questions to `sprint_daily_agenda`, `claim_next`,
  `sprint_check_daily_quota`, and `plan_status`/`qa_budget`, and states that a
  `claim_next` block is reported rather than bypassed.
- **Docs**: `LLM.txt` (§4 directory loop, §5 copy block, §7 config entry and
  counts, §7.5 venv-before-unit plus drop-in, verification block, checklist),
  `README.md` component tree, `CHANGELOG.md`.

### Assumptions and deviations

- **A1 — `uv sync`, not `uv pip install -e .`.** The requested editable install
  cannot work: `pyproject.toml` declares no `[build-system]` and no package, so
  there is nothing to install as a project. `uv sync` against the committed
  `uv.lock` produces the same interpreter the unit needs and stays reproducible.
- **A2 — `PLANNER_PROJECT_ROOT` via a systemd drop-in.** The committed unit runs
  with `WorkingDirectory` set to the install directory, which holds no `tasks/`,
  so the dashboard would resolve to an empty board — the exact defect fixed in
  the previous task, now reappearing at deployment. The unit file is left
  machine-independent (no hardcoded repo path committed);
  `mcp-planner.service.d/override.conf` supplies the absolute path locally, and
  `LLM.txt` reproduces that step for any machine.
- **A3 — the day-start trigger is written in English.** The request quoted a
  literal phrase in another language. Operating instructions in this repo are
  English-only by policy, and an earlier language-policy task deliberately
  generalised non-English literals out of the executor. The section therefore
  says "start today's work — in whatever language the request arrives", which
  keeps the recognition behaviour without reintroducing a literal. Verified:
  no non-ASCII-script characters exist in the file.
- **A4 — the installed executor was synced.** `agents/cognitive-executor.md` in
  the repo is not what the running agent reads; the global
  `~/.config/opencode/agents/cognitive-executor.md` is a separate regular file.
  Without syncing, the wiring would be documented but inert. Diffed first — the
  new section was the only difference — then copied and confirmed
  byte-identical with `cmp`.
- **A5 — `opencode mcp list` is unusable for verification.** It prints "No MCP
  servers configured" for every entry on v2.1.4, including the six servers this
  session is using right now. Registration was therefore verified two other
  ways: `opencode debug config` shows the `planner` entry resolved, and the
  registered URL answers a real MCP `initialize` + `tools/list`. The stale
  `opencode mcp list` instruction in `LLM.txt` was replaced with the working
  command and a note explaining why.

### Findings worth flagging

- **F1 — `LLM.txt` carried a retired server.** Its checklist claimed a 8104
  "decisions" MCP entry and simultaneously said "6 entries" and "all 7 `mcp`
  entries". There is no 8104 entry in the global config. The lines touched for
  the planner are now accurate (7 entries: 8101, 8102, 8103, 8105, 8106, 8107,
  8108); other stale 8104 references elsewhere in the docs were left alone.
- **F2 — `opencode debug config` is the reliable registration probe** on this
  build and is now documented as such.

### Verification notes

- Probes were run against the deployed unit, not a hand-started process, so they
  prove the systemd path (`ExecStart` → venv interpreter → server) rather than
  the developer path.
- `docs-sync` compares the repo and global `permission.shell` deny sets; the
  `planner` entry touches only `mcp.servers`, so the gate stays green.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c665c9deab786210fa5b7a300464cbb769d31b69`
<!-- END_GIT_DIFF -->
