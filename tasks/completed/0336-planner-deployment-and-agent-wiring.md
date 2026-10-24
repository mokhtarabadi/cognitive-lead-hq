# Task 336: Planner deployment and agent wiring

**File:** `tasks/qa/0336-planner-deployment-and-agent-wiring.md`
**Source:** manager
**Type:** feature
**Status:** in-progress

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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 892c5d5..2be084b 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Planner MCP deployed globally and wired into the executor protocol (Task 336):** the planner is now a live platform singleton rather than repo-local code. It installs to `~/.config/opencode/mcp-planner-server/` (source, committed `uv.lock`, and `static/` dashboard assets) with its venv built by `uv sync` from the lock, runs as `mcp-planner.service` on `127.0.0.1:8108` (enabled, active, loopback-only), and is registered in the global `opencode.json` as `mcp.servers.planner` (`type: remote`, `http://127.0.0.1:8108/mcp`, timeout 15000/30000). `agents/cognitive-executor.md` gains a *Planner MCP and Daily Pacing Protocol* section binding four moments to four tools: `sprint_daily_agenda` when the Manager starts the day, `claim_next` instead of hand-moving a task file (a block is reported, never bypassed), `sprint_check_daily_quota` when tasks close, and `plan_status`/`qa_budget` for status questions — with an explicit fallback to the Kanban workflow if the server is unreachable. `LLM.txt` provisions the whole thing (§4 directory, §5 copy block, §7 config entry, §7.5 venv-before-unit plus drop-in, verification checklist), `README.md` lists the component, and `docs/services.md` keeps the port map. Deployment adaptations forced by what actually ran: `uv pip install -e .` cannot work because the package declares no build backend, so the venv comes from `uv sync` against the committed lock; the committed unit stays machine-independent and the dashboard's project root is supplied by a `mcp-planner.service.d` drop-in (`PLANNER_PROJECT_ROOT`), since the unit's WorkingDirectory is the install dir which holds no `tasks/`; and `opencode mcp list` prints "No MCP servers configured" on v2.1.4 even for the six servers already in use, so registration is verified with `opencode debug config` (7 resolved `127.0.0.1:810*/mcp` entries) plus a live MCP handshake instead — the docs now say so. Verified: unit `active`/`enabled`, `/` and `/api/status` both 200 with 329 tasks for this repo, planner tools enumerable over `initialize`+`tools/list`, `scripts/check_docs_sync.py` exits 0, 31/31 planner tests pass, full suite 592 passed with the one pre-existing prompt round-trip failure.
+
 - **Planner MCP v1 and local dashboard (Task 335):** new `mcp-planner-server/` singleton on loopback `127.0.0.1:8108` that reads `tasks/` Markdown as the single source of truth and adds a capacity-aware, QA-gated planning layer over it. Tools: `plan_propose` (decompose a goal into estimated tasks + milestones, writes nothing), `plan_materialize` (writes task files only after approval), `claim_next` (guarded claim that refuses on unmet dependencies, a full WIP ceiling, or an exhausted QA budget), `plan_status`, `sprint_stats` (hours spent, progress, velocity), `qa_budget`, `milestone_status`, `sprint_lock`, `sprint_daily_agenda`, and `sprint_check_daily_quota` (`DAILY_QUOTA_REACHED`). The same process serves a zero-build dark-mode dashboard at `/` with a Jalali + Gregorian 14-day timeline, Kanban lanes, milestone tree, daily pacing gauge, and a working project switcher, plus `GET /api/status`. Two defects were fixed during verification rather than shipped: the transport is built with `mcp.streamable_http_app()` (mcp 1.30 has no `http_app()`) mounted at the root with an explicit `lifespan_context` enter, because Starlette never runs a `Mount`-ed sub-app's lifespan and the session manager stayed uninitialised; and `/api/status` now returns per-lane **task lists**, a `milestone_tree`, sorted `deadlines`, a `today` triple matching `sprint_check_daily_quota`, and a `projects` list, with the root resolved from `project_root` → `PLANNER_PROJECT_ROOT` → nearest ancestor holding `tasks/` → cwd. The previous count-per-lane shape made `items.map` throw inside `render()` and silently blanked the board, and the hard-coded `Path.cwd()` root reported an empty board under systemd. Also added `tasks/sprints/` and `tasks/milestones/`, `services/mcp-planner.service`, `uv.lock`, port 8108 in `docs/services.md`, and the unit in `services/README.md`. Verified: 30/30 planner tests pass, a live `initialize` on `/mcp` returns 200, `GET /` and `/api/status` return 200 against the real repo (328 tasks), and the dashboard `render()` was exercised headlessly against both the live and a synthetic milestone payload.
 
 - **Metadata bundle 334 — zen-proxy migration plus goal-plugin reference sync (META over tasks 333 + 332):** the two open items were merged into one all-or-nothing META with `bundle_tasks`, so they share one branch, one diff, and one QA gate. Sources are archived under `tasks/archive/` with a `Superseded-By: 334-...` header and stay reachable via `git log --follow`. The META also carries the remaining pending worktree changes the Manager asked to fold in: the Smart Compact automation/threshold sync, the layered provider-timeout tunables (`ZEN_PROXY_UPSTREAM_TIMEOUT` + `BRAIN_OVERALL_DEADLINE_S`), the two updated `opencode_config` memory shards, and the new free-model context-window workflow shard. Re-verified live: `zen-proxy` is `active` from `~/.config/opencode/zen-proxy/.venv/bin/python`, `/health` 200, `/go/resp` serves 13 models (the chat mounts read 23/3 — upstream churn, not a regression), `docs-sync: OK`, and 303 prompt-sync plus bridge tests pass.
diff --git a/LLM.txt b/LLM.txt
index 4cac8aa..7aa1bff 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -106,7 +106,7 @@ Store this value — you will use it to construct absolute paths in the global c
 Create the global OpenCode directories:
 
 ```bash
-for d in mcp-context-server mcp-memory-server mcp-lint-server mcp-brain-bridge mcp-common zen-proxy; do
+for d in mcp-context-server mcp-memory-server mcp-lint-server mcp-brain-bridge mcp-planner-server mcp-common zen-proxy; do
   mkdir -p ~/.config/opencode/$d
 done
 mkdir -p ~/.config/opencode/skills
@@ -133,6 +133,14 @@ done
 # nesting to mcp-common/mcp-common when the destination already exists).
 cp -a /tmp/cognitive-lead-hq/mcp-common/. ~/.config/opencode/mcp-common/
 
+# planner: source + committed lockfile + dashboard assets. Its venv is built in
+# §7.5 (`uv sync` installs from the lock); the dashboard needs `static/`.
+cp /tmp/cognitive-lead-hq/mcp-planner-server/{server.py,pyproject.toml,uv.lock,README.md,DECISIONS.md} \
+   ~/.config/opencode/mcp-planner-server/
+cp -r /tmp/cognitive-lead-hq/mcp-planner-server/static/. \
+   ~/.config/opencode/mcp-planner-server/static/
+chmod +x ~/.config/opencode/mcp-planner-server/server.py
+
 # zen-proxy: the gateway sidecar the Brain calls as its provider. Source only —
 # it is stdlib-only, so the venv has nothing to install (built in §7.5).
 cp /tmp/cognitive-lead-hq/zen-proxy/{proxy.py,pyproject.toml,README.md,DECISIONS.md} \
@@ -216,7 +224,7 @@ After this, the `cognitive-executor` will be available as a primary agent, enfor
 
 ## 7. Configure Global opencode.json (with Absolute Paths)
 
-Create or update `~/.config/opencode/opencode.json`. You MUST use **absolute paths** in the `command` array — resolve the `~` to the full home directory path discovered in Step 3. The project ships **6 MCP servers** (3 core + `brain` bridge + `blowsh` browsing + `telegram` account routing); the persona server and the previous browser automation MCP are retired — use `blowsh` for JS-heavy browsing.
+Create or update `~/.config/opencode/opencode.json`. You MUST use **absolute paths** in the `command` array — resolve the `~` to the full home directory path discovered in Step 3. The project ships **7 MCP servers** (3 core + `brain` bridge + `blowsh` browsing + `telegram` account routing + `planner` capacity/QA gating); the persona server and the previous browser automation MCP are retired — use `blowsh` for JS-heavy browsing.
 
 Write the following JSON (replace `$HOME` with the actual home directory path only where it still appears — the `mcp` entries are loopback URLs shared by every session and project, so they contain no paths at all). V2 structure per https://opencode.ai/v2/docs/mcp-servers/ (verified 2026-09-29): each MCP runs as **one supervised singleton** on `127.0.0.1` (see `docs/services.md` + Step 7.5), and OpenCode connects via `mcp.servers` entries with `type: "remote"` + `url` + `disabled: false` + `timeout: {catalog, execution}` (ours are raised above the 5000ms default — 15s standard, 30s telegram, 120s blowsh, 600s LLM bridges). No session ever spawns its own server processes: with 2+ sessions open the OS process count per server stays exactly one.
 
@@ -262,6 +270,12 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
         "url": "http://127.0.0.1:8106/mcp",
         "disabled": false,
         "timeout": { "catalog": 30000, "execution": 30000 }
+      },
+      "planner": {
+        "type": "remote",
+        "url": "http://127.0.0.1:8108/mcp",
+        "disabled": false,
+        "timeout": { "catalog": 15000, "execution": 30000 }
       }
     }
   },
@@ -317,11 +331,11 @@ The `cli.json` `plugins` entry enables the todolist TUI sidebar strip.
 
 **Important:** Replace `$HOME` with the actual absolute path resolved in Step 3 (e.g., `/home/alice` or `/Users/alice`). This is critical — MCP servers will NOT work with relative paths or `~` in the global config because OpenCode may be invoked from any working directory.
 
-**Launch form + credentials:** no session spawns servers anymore — the 7 singletons run as supervised services on `127.0.0.1:8101-8107` (started in Step 7.5, full map in `docs/services.md`), and the config above only points at them via `type: "remote"`. The old per-session stdio storm (and its `mcp connect failed: Request timed out` failures, ~200/day before the 2026-09-29 singleton fix) is gone by construction. The brain/decision timeouts stay 600000ms (10 min) — LLM turns need it. Credentials (`BRAIN_*`, `DECISION_*`, `TELEGRAM_*`) are **not** in the OpenCode config: each server self-loads `.env` at import, in order `<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env`, never overriding real process env. For the global install that effective file is **`~/.config/opencode/.env`** (seeded in Step 5, `chmod 600`); for servers run straight from the repo it is the repo-root `.env`. The systemd/launchd/Windows units therefore need **no** `EnvironmentFile=` for these keys. Telegram prerequisites (clone + `uv sync` + `.env` + allowed-root dirs) are still installed per §7.6 — only the launch moved into the `mcp-telegram` service.
+**Launch form + credentials:** no session spawns servers anymore — the 8 singletons run as supervised services on `127.0.0.1:8101-8108` (started in Step 7.5, full map in `docs/services.md`), and the config above only points at them via `type: "remote"`. The old per-session stdio storm (and its `mcp connect failed: Request timed out` failures, ~200/day before the 2026-09-29 singleton fix) is gone by construction. The brain/decision timeouts stay 600000ms (10 min) — LLM turns need it. Credentials (`BRAIN_*`, `DECISION_*`, `TELEGRAM_*`) are **not** in the OpenCode config: each server self-loads `.env` at import, in order `<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env`, never overriding real process env. For the global install that effective file is **`~/.config/opencode/.env`** (seeded in Step 5, `chmod 600`); for servers run straight from the repo it is the repo-root `.env`. The systemd/launchd/Windows units therefore need **no** `EnvironmentFile=` for these keys. Telegram prerequisites (clone + `uv sync` + `.env` + allowed-root dirs) are still installed per §7.6 — only the launch moved into the `mcp-telegram` service.
 
 **QA/review run through the bridge:** the Hands calls `brain_turn` with the instruction + task file (see the Bridge section in `agents/cognitive-executor.md`); history continues under the active session thread (ambient `OPENCODE_SESSION_ID` auto-detection). No per-persona commands or learning stores.
 
-> **Project vs Global `opencode.json` (full V2, 2026-10-01):** The **repo's** `opencode.json` (committed) carries **no `mcp` section at all** — all 7 servers live in the **global** `~/.config/opencode/opencode.json` (created here) under `mcp.servers` as `type: "remote"` loopback URLs (`http://127.0.0.1:8101-8107/mcp`, identical for every user — no per-machine paths). New installations and `global-install-upgrade` (Step 5 in `.opencode/memory/workflows/global-install-upgrade.md`) must keep this split — `diff` of repo vs global `opencode.json` will always differ (repo has no `mcp`, global has 7 remote entries) by design; verify global shows 7 `127.0.0.1:810*/mcp` URLs.
+> **Project vs Global `opencode.json` (full V2, 2026-10-01):** The **repo's** `opencode.json` (committed) carries **no `mcp` section at all** — all 7 MCP servers live in the **global** `~/.config/opencode/opencode.json` (created here) under `mcp.servers` as `type: "remote"` loopback URLs (identical for every user — no per-machine paths). New installations and `global-install-upgrade` (Step 5 in `.opencode/memory/workflows/global-install-upgrade.md`) must keep this split — `diff` of repo vs global `opencode.json` will always differ (repo has no `mcp`, global has 7 remote entries) by design; verify global shows 7 `127.0.0.1:810*/mcp` URLs (8101 lint, 8102 context, 8103 memory, 8105 brain, 8106 telegram, 8107 blowsh, 8108 planner — there is no 8104 entry, the decision server was retired).
 
 **Telegram is optional but auto-configured:** the entry above points at `~/.config/opencode/mcp-telegram-server` (installed in the opencode config dir per global-install-upgrade, absolute path required) with three allowed roots (`/tmp/telegram-mcp` for temp state + `~/.config/opencode/mcp-telegram-server/downloads` for exported media + `$HOME` so home files upload). If you cloned elsewhere, update the venv-python path, the `main.py` path and the trailing roots — keep them inside `$HOME` or `/tmp` and ensure `telegram_download_media` can write there. The server is installed in Step 7.6 even before you have API credentials; it stays idle (no `TELEGRAM_SESSION_STRING`) until you finish 7.6. For Docker blowsh no host binary is needed — `docker pull ghcr.io/mokhtarabadi/blowsh-mcp:latest` on first `fetch_web` run.
 
@@ -332,12 +346,23 @@ The `cli.json` `plugins` entry enables the todolist TUI sidebar strip.
 The config in Step 7 points at services — they must be running before OpenCode connects. Full reference: `docs/services.md`.
 
 ```bash
-# Python singletons (Linux): install + start the 6 systemd user units
+# Python singletons (Linux): install + start the 7 systemd user units
 # (run from your clone of this repo — services/ ships in the clone, no /tmp copy needed)
 mkdir -p ~/.config/systemd/user
 cp services/mcp-*.service services/zen-proxy.service ~/.config/systemd/user/
+
+# planner: build its venv from the committed lock BEFORE starting the unit
+# (ExecStart needs .venv/bin/python), and point the dashboard at the project
+# it should report on — the unit's WorkingDirectory is the install dir, which
+# holds no tasks/. A drop-in keeps the committed unit machine-independent.
+PLANNER_REPO="$PWD"
+(cd ~/.config/opencode/mcp-planner-server && uv sync)
+mkdir -p ~/.config/systemd/user/mcp-planner.service.d
+printf '[Service]\nEnvironment=PLANNER_PROJECT_ROOT=%s\n' "$PLANNER_REPO" \
+  > ~/.config/systemd/user/mcp-planner.service.d/override.conf
+
 systemctl --user daemon-reload
-for s in lint context memory decision brain telegram; do
+for s in lint context memory brain telegram planner; do
   systemctl --user enable --now mcp-$s
 done
 
@@ -361,7 +386,11 @@ macOS/Windows equivalents (launchd plist template, Task Scheduler/NSSM): `docs/s
 Verify before continuing:
 
 ```bash
-opencode mcp list                      # 7/7 connected
+# `opencode mcp list` prints "No MCP servers configured" on v2.1.4 even when the
+# entries are live, so read the resolved config instead:
+opencode debug config | grep -c '127.0.0.1:810'   # 7 MCP entries resolved
+systemctl --user is-active mcp-planner   # active
+curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8108/        # 200 — planner dashboard
 systemctl --user is-active zen-proxy    # active — the Brain's provider hop
 curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8081/health   # 200
 ```
@@ -583,12 +612,13 @@ After completing all steps, verify:
 - [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` (36 skills total)
 - [ ] `~/.config/opencode/agents/cognitive-executor.md` exists
 - [ ] `~/.config/opencode/agents/cognitive-discovery.md` exists
-- [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 6 `mcp` entries (`custom_context`, `project_memory`, `lint`, `brain`, `blowsh`, `telegram`) + `blowsh_*`/`telegram_*`/`brain_turn` permissions, no former browser entry
+- [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 7 `mcp` entries (`custom_context`, `project_memory`, `lint`, `brain`, `blowsh`, `telegram`, `planner`) + `blowsh_*`/`telegram_*`/`brain_turn` permissions, no former browser entry
+- [ ] `~/.config/opencode/mcp-planner-server/` holds `server.py`, `uv.lock`, and `static/index.html`; `systemctl --user is-active mcp-planner` reports `active`; `curl http://127.0.0.1:8108/api/status` returns a non-zero task count for this repo
 - [ ] `~/.config/opencode/opencode.json` `plugins` carries `smart-compact` plus `opencode-goal-plugin` plus `opencode-todolist`, and `~/.config/opencode/cli.json` `plugins` carries `opencode-todolist` for the sidebar strip
 - [ ] `opencode plugin list` shows smart-compact, goal, and todolist entries (after restart)
 - [ ] worktrees: OpenChamber native via sidebar/dialog (`https://docs.openchamber.dev/worktrees/`) — no plugin required
 - [ ] (optional) OpenChamber: if installed, `npm list -g @openchamber/web` shows 2.x, `openchamber status` password:yes, `openchamber startup status` shows enabled+active+lingering, `docs/openchamber.md` present; if not requested, this check is N/A
-- [ ] `~/.config/opencode/opencode.json` all 7 `mcp` entries are `type: "remote"` loopback URLs (8101 lint, 8102 context, 8103 memory, 8104 decisions, 8105 brain, 8106 telegram timeout 30000, 8107 blowsh timeout 120000) served by the supervised singletons — no stdio/`uv run` entries remain
+- [ ] `~/.config/opencode/opencode.json` all 7 `mcp` entries are `type: "remote"` loopback URLs (8101 lint, 8102 context, 8103 memory, 8105 brain, 8106 telegram timeout 30000, 8107 blowsh timeout 120000, 8108 planner timeout 30000) served by the supervised singletons — no stdio/`uv run` entries remain
 - [ ] `~/.config/opencode/opencode-shell-strategy.md` exists (instructions file referenced by the `instructions` key)
 - [ ] `/tmp/cognitive-lead-hq` no longer exists
 - [ ] `docker pull ghcr.io/mokhtarabadi/blowsh-mcp:latest` succeeds (or `docker` not installed → blowsh stays disabled, document it)
@@ -602,6 +632,7 @@ After completing all steps, verify:
   ~/.config/opencode/mcp-memory-server/.venv/bin/python ~/.config/opencode/mcp-memory-server/server.py &
   ~/.config/opencode/mcp-lint-server/.venv/bin/python ~/.config/opencode/mcp-lint-server/server.py &
   ~/.config/opencode/mcp-brain-bridge/.venv/bin/python ~/.config/opencode/mcp-brain-bridge/server.py &
+  ~/.config/opencode/mcp-planner-server/.venv/bin/python ~/.config/opencode/mcp-planner-server/server.py &
   ```
 
 ---
diff --git a/README.md b/README.md
index 3b288fc..1cd2c6b 100644
--- a/README.md
+++ b/README.md
@@ -199,6 +199,9 @@ cp .env.example .env
 │   └── server.py                       # FastMCP server for persistent project memory
 ├── mcp-brain-bridge/                  # Unified Brain bridge
 │   └── server.py                       # FastMCP `BrainBridge`: brain_turn (prompt loader + LLM + XML extract)
+├── mcp-planner-server/                 # Capacity-aware, QA-gated planning layer
+│   ├── server.py                       # FastMCP planning tools + dashboard/MCP on 127.0.0.1:8108
+│   └── static/index.html               # Standalone dashboard (Jalali + Gregorian timeline)
 ├── zen-proxy/                          # Loopback gateway sidecar (NOT an MCP server)
 │   ├── proxy.py                        # Zen/Go mount proxy: session minting, model filters, effort rewrite
 │   ├── pyproject.toml                  # Stdlib-only; exists so `uv venv` provisions the runtime
@@ -332,7 +335,7 @@ cp .env.example .env
 
 ## 🔌 Custom Code Context FastMCP
 
-> **Current path:** supervised remote singletons on `127.0.0.1:8101–8107` — see `docs/services.md`. What follows is the **legacy per-project stdio fallback** (kept for offline/air-gapped use, not the default).
+> **Current path:** supervised remote singletons on `127.0.0.1:8101–8108` — see `docs/services.md`. What follows is the **legacy per-project stdio fallback** (kept for offline/air-gapped use, not the default).
 
 This system uses a local **FastMCP** Python server (`mcp-context-server/server.py`) that runs via its persistent venv interpreter (`<dir>/.venv/bin/python <dir>/server.py`, never `uv run`) with locked dependency management. It provides deterministic, `.gitignore`-aware file reading and directory tree exploration, using far fewer tokens than raw `grep`/`glob` operations.
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 7612124..9584968 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -219,6 +219,17 @@ If you detect any of these failure modes, HALT immediately and surface to the Ma
 
 When a circuit breaker fires, output a `⚠️ CIRCUIT BREAKER` warning with the failure mode and your recommended next step.
 
+### Planner MCP and Daily Pacing Protocol
+
+`mcp-planner-server` is the loopback singleton on `127.0.0.1:8108` that owns daily workload and queue circuit-breaking. It reads `tasks/` Markdown as the source of truth and never replaces it. Pass an absolute `project_root` on every call.
+
+- **Starting the day.** When the Manager says "start today's work" — in whatever language the request arrives — call `sprint_daily_agenda(project_root)` before touching any task file. It lists what is already in progress plus any QA-pending task that has to be resolved first.
+- **Taking a task.** Call `claim_next(project_root, task_id)` instead of hand-moving the file. It performs the backlog to in-progress transition only when dependencies are satisfied, the WIP ceiling allows it, and the QA budget is not spent. A block is an answer, not an obstacle: report the stated reason to the Manager and never bypass it by moving the file manually.
+- **Ending the day.** Once tasks are closed, call `sprint_check_daily_quota(project_root)`. When it returns `DAILY_QUOTA_REACHED`, present `sprint_stats(project_root)` and announce that the day's work is finished; do not claim another task in that turn.
+- **Status questions.** `plan_status(project_root)` covers lanes, capacity against estimate, milestones, and blockers. `qa_budget(project_root)` answers whether another review can be opened without breaching the one-unresolved-review ceiling.
+
+The planner is additive tooling. If the server is unreachable, fall back to the existing Kanban workflow and say so plainly — never stall work waiting for it.
+
 ### Reasoning Drift Prevention
 
 For tasks exceeding 100 steps, re-anchor to the original goal every 50 steps by answering:
```
<!-- END_GIT_DIFF -->
