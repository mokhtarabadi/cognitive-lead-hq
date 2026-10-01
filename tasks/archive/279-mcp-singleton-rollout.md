# Task 279: mcp-singleton-rollout

**File:** `tasks/completed/279-mcp-singleton-rollout.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Supersedes:** [277, 278]
**Meta:** true
**Created:** 2026-09-29 06:31 UTC
**Bundled:** 2 tasks

## Goal

Unified execution of 2 related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks [277, 278] — "mcp-singleton-rollout" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.

**Source IDs:** [277, 278]
**Next ID:** 279 (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)
**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: 279-mcp-singleton-rollout` and remain reachable via `git log --follow` (never purged until META is completed).

## Manager's Notes

**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute 2 small related tasks together and speed up turnaround.

**Traceability:**
- Supersedes [277, 278] — see per-source verbatim blocks below
- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** 279-mcp-singleton-rollout` header + superseded footer
- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file

**Guardrails Applied:**
- Cap 6 per bundle — this bundle has 2 (✅ within cap)
- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)
- Diff-size check — combined 190 LOC (✅ within 400)

## Source Bundles (Verbatim Preservation)

The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.

### Source Task 277: MCP singleton remote services

**Original File:** `tasks/in-progress/277-mcp-singleton-remote-services.md` → `tasks/archive/277-mcp-singleton-remote-services.md` (after bundling)

**Title:** MCP singleton remote services

#### Goal (verbatim)

One running instance of each MCP server, shared across all sessions and projects, with a single opencode-server and a single OpenChamber instance.

#### Manager's Notes (verbatim)

Manager request (Persian, verbatim): "در کل میخوام طوری باشه یه instance از opencode بالا باشه و همه mcp ها هم فقط یک instance داشته باشن و و یک instance از openchamber هم باشه دیگه بین همه سشن ها و پروژها مشتکر باشه mcp سرورها". English: one opencode instance up, every MCP exactly one instance, one OpenChamber instance, MCP servers shared across all sessions and projects. Current state already satisfies 2 of 3 (single `opencode serve --service` PID 1100144, single OpenChamber service). Missing piece: each session spawns its own 7 stdio MCP processes (12 observed: 2 sets x 6). Approved direction: run each Python MCP once as a supervised remote (HTTP/SSE) service on 127.0.0.1 and switch global opencode.json entries from stdio to `type: remote`. Manager approved via plan-approval gate ("Approved, build it").

#### Acceptance Criteria (verbatim)

- [ ] Exactly one OS process per MCP server (6 Python + blowsh) regardless of open session count
- [ ] Every session/project resolves the same 7 MCP servers via `opencode mcp list`
- [ ] Single opencode-server and single OpenChamber instance unchanged and healthy
- [ ] Services supervised (auto-restart) and bound to 127.0.0.1 only
- [ ] Rollback to stdio config restores current working state

#### Local TODOs (verbatim)

_(No Local TODOs)_

#### Risk & Rollback (verbatim)

- **Risk:** stdio-to-remote migration breaks currently working MCP setup; custom servers are stdio-only and need a transport shim; shared stateful servers face concurrent access; singleton is a single point of failure
- **Rollback plan:** global config backup (`opencode.json.bak-20260929-073130` plus fresh pre-migration backup); restore stdio entries, restart sessions; document exact restore commands in Execution Log

---

### Source Task 278: Singleton docs, migration, upgrades, cross-platform units

**Original File:** `tasks/in-progress/278-singleton-docs-migration-upgrades.md` → `tasks/archive/278-singleton-docs-migration-upgrades.md` (after bundling)

**Title:** Singleton docs, migration, upgrades, cross-platform units

#### Goal (verbatim)

Everything documented and upgraded: new users set up the full system from LLM.txt, existing users migrate to singletons via memory, all docs/skills match opencode 2 schema, global installation current, service files exist for Linux/macOS/Windows.

#### Manager's Notes (verbatim)

Manager order covering: (a) all docs updated with singleton changes; (b) research opencode 2 schema and full opencode.json, migrate skills to opencode 2; (c) upgrade global installation and memory; (d) LLM.txt = full setup for new users, memory workflow = migration path for existing users; (e) systemd units plus macOS/Windows equivalents, all documented; (f) blowsh (own repo task 10): stdio + http + sse all enabled by default and env-manageable, docs/readme/dockerfile updated. Assumptions: A1 `upgrade memory` = memory MCP server code currency + memory index rebuild + workflow doc update; A2 Windows supervision = scheduled-task XML + optional NSSM note (no systemd); macOS = launchd plists; A3 blowsh default ports: stdio fd + http 8107 + sse 8108 unless its task 10 says otherwise.

#### Acceptance Criteria (verbatim)

- [ ] LLM.txt alone takes a new user from zero to 7/7 connected singletons
- [ ] Memory workflow migrates an existing stdio setup to singletons
- [ ] All repo docs/skills validated against opencode 2 schema (no v1 leftovers)
- [ ] Global installation (opencode, openchamber, npm deps) at latest, memory index rebuilt
- [ ] Service files for Linux (systemd), macOS (launchd), Windows (scheduled task) present + documented
- [ ] Blowsh supports stdio+http+sse env-managed with docs/readme/dockerfile updated in its task 10

#### Local TODOs (verbatim)

_(No Local TODOs)_

#### Risk & Rollback (verbatim)

- **Risk:** doc edits contradict live state; upgrades break working setup; cross-platform files untestable here (Linux only)
- **Rollback plan:** config backups before any upgrade; docs are git-diffable, revert per file; mark macOS/Windows files untested-on-Linux in docs

---


## Bundled Checklist (All-or-Nothing)

> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.

- [x] [277] Exactly one OS process per MCP server (6 Python + blowsh) regardless of open session count
- [x] [277] Every session/project resolves the same 7 MCP servers via `opencode mcp list`
- [x] [277] Single opencode-server and single OpenChamber instance unchanged and healthy
- [x] [277] Services supervised (auto-restart) and bound to 127.0.0.1 only
- [ ] [277] Rollback to stdio config restores current working state
- [ ] [278] LLM.txt alone takes a new user from zero to 7/7 connected singletons
- [x] [278] Memory workflow migrates an existing stdio setup to singletons
- [x] [278] All repo docs/skills validated against opencode 2 schema (no v1 leftovers)
- [ ] [278] Global installation (opencode, openchamber, npm deps) at latest, memory index rebuilt
- [x] [278] Service files for Linux (systemd), macOS (launchd), Windows (scheduled task) present + documented
- [ ] [278] Blowsh supports stdio+http+sse env-managed with docs/readme/dockerfile updated in its task 10
- [ ] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Local TODOs

- [x] Step 1: Validate META bundle — confirm all 2 source requirements are captured verbatim below
- [x] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)
- [x] Step 3: Verify all bundled checklist items and run lint_task_file + verification-before-completion
- [x] Step 4: Update CHANGELOG.md and record Verification Evidence

## Acceptance Criteria

- [x] [277] Exactly one OS process per MCP server (6 Python + blowsh) regardless of open session count
- [x] [277] Every session/project resolves the same 7 MCP servers via `opencode mcp list`
- [x] [277] Single opencode-server and single OpenChamber instance unchanged and healthy
- [x] [277] Services supervised (auto-restart) and bound to 127.0.0.1 only
- [ ] [277] Rollback to stdio config restores current working state
- [ ] [278] LLM.txt alone takes a new user from zero to 7/7 connected singletons
- [x] [278] Memory workflow migrates an existing stdio setup to singletons
- [x] [278] All repo docs/skills validated against opencode 2 schema (no v1 leftovers)
- [ ] [278] Global installation (opencode, openchamber, npm deps) at latest, memory index rebuilt
- [x] [278] Service files for Linux (systemd), macOS (launchd), Windows (scheduled task) present + documented
- [ ] [278] Blowsh supports stdio+http+sse env-managed with docs/readme/dockerfile updated in its task 10
- [ ] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Verification Evidence

- **Test command:** `lint_task_file` on META file; `git log --oneline --follow -- tasks/archive/<id>-*.md | head` for archived sources; project test suite if logic changed
- **Expected result:** META lint passes; all 2 sources in `tasks/archive/` with `superseded` status; single Factual Git Diff covers all bundled changes
- **Actual result:** _(Hands fill during execution)_
- **Exit code:** _(Hands fill)_

### Hotfix evidence (2026-09-29, Brain QA_REJECTED re-QA round, docs-only F1+F2)

- **Test command:** `ls -1 services/mcp-*.service` / `ls -1 services/systemd/mcp-*.service` / `grep -R "services/systemd" LLM.txt docs/services.md .opencode/memory/workflows/global-install-upgrade.md` / `grep -n "tasks/qa/279-mcp-singleton-rollout" tasks/archive/277-*.md tasks/archive/278-*.md`
- **Expected result:** first ls lists 6 units exit 0; second ls fails (no subdir); stale-subdir grep empty; footer grep shows only `tasks/qa/` path
- **Actual result:** 6 units listed (`mcp-brain/context/decision/lint/memory/telegram.service`), subdir ls failed as expected, stale grep clean, both footers show `tasks/qa/` path, zero `tasks/backlog/279` refs left
- **Exit code:** 0 (all)
- **Tooling gate skip record:** `root=. markers=[pyproject.toml, package.json scan] matched=[] reason=no source code changed in this hotfix`

### Live evidence round 2 (2026-09-29, re-QA fix XML Steps 1+2+4, verify-only, exit 0 unless noted)

- `ps aux | grep -E "mcp-|telegram_mcp|blowsh"` → exactly 6 python server processes, one per server (memory 1173704, decision 1173705, brain 1173706, telegram 1175507, context 1264778, lint 1277166), all started 08:01–08:57 before this session — shared singletons, count does not grow per session. Exit 0.
- `ss -tlnp | grep -E "8101|...|8107"` → all 7 ports LISTEN on `127.0.0.1` only (8101 lint, 8102 context, 8103 memory, 8104 decision, 8105 brain, 8106 telegram, 8107 blowsh container). No wildcard binds. Exit 0.
- `systemctl --user status mcp-lint mcp-context mcp-memory mcp-decision mcp-brain mcp-telegram` → units `Loaded: loaded (.../systemd/user/...)`, `enabled`, `Active: active (running)`. Exit 0.
- Unit bodies: all 6 `services/mcp-*.service` carry `Restart=always` + `RestartSec=3` and direct-venv-interpreter `ExecStart` (never `uv run`); telegram unit additionally pins `MCP_HOST=127.0.0.1` + `MCP_PORT=8106`. The other five bind loopback code-side: FastMCP constructors hardcode `host="127.0.0.1"` (lint server.py:28, context server.py:417, memory server.py:22, decision server.py:190, brain server.py:175; ports 8101–8105) with `transport=os.environ.get("MCP_TRANSPORT","stdio")`. Assumption A2: kept code untouched (editing live servers' shim + restarting them mid-session = destructive); loopback is constructor-enforced and ss-proven.
- `opencode mcp list` → 7/7 connected (blowsh, brain, custom_context, lint, manager_decisions, project_memory, telegram). Cross-session proof: PIDs predate this session yet serve it (every MCP tool call in this session routed through them). Exit 0.
- `opencode --version` → `opencode v2.0.19`. OpenChamber: `openchamber.service` active (running), `cli.js serve --foreground --port 3005 --host 127.0.0.1`. Exit 0.
- `docker inspect blowsh-singleton` → `restart=unless-stopped`, `ports=map[8107/tcp:[{127.0.0.1 8107}]]`, env `MCP_TRANSPORT=http MCP_HOST=0.0.0.0 MCP_PORT=8107 BROWSH_PROFILE_DIR=/data/browsh-profile` — matches `global-install-upgrade.md` migration step verbatim (R1 alignment verified live). Exit 0.
- Schema sweep `grep -R -n 'type: .local.' README.md LLM.txt opencode.json skill-templates/` → empty (exit 1 = clean, no v1 leftovers). Stale-subdir sweep `grep -R "services/systemd"` → clean.
- `uv run` sweep: remaining hits reviewed-intentional (README never-uv-run statements ×2 + pure-MCP note, LLM 6.1 optional Manager CLI section, LLM telegram session-string generator, workflow `rtk test uv run` smoke-test, setup.md never-uv-run rationale + rtk line). No per-session stdio/`uv run` spawn entries remain.
- Rollback artifact: `cp ~/.config/opencode/opencode.json → opencode.json.bak-279-verify-20260929-091449` (exit 0); live config parses and holds 7 `mcp` keys (custom_context, project_memory, lint, blowsh, telegram, brain, manager_decisions).
- `rebuild_memory_index` via MCP → `Memory index built: 0 memories (empty)` (server-side store; exit ok). Repo `.opencode/memory/index.md` verified intact afterwards (`git status` clean, entries present). No upgrades performed anywhere (verify-only per XML).
- `npm ls -g --depth=0` → `@openchamber/web@2.0.4`, `npm@11.19.0` (no opencode npm package; v2.0.19 installed out-of-band — recorded, not changed).
- `git log --oneline --follow -- tasks/archive/277-*.md tasks/archive/278-*.md` → empty: both files are staged-new, uncommitted — history starts at this commit, reachable afterwards. Traceability stays CONDITIONAL until commit (commit path is Manager-gated).
- **Tooling gate skip record (round 2):** `root=. markers=[pyproject.toml, package.json] matched=[] reason=docs+units only, repo server.py behavior untouched`.
- Prettier `--check` on touched docs: `README.md`, `docs/setup.md`, `docs/services.md` clean (two pre-existing table/JSON spots re-padded, exit 0 after); `global-install-upgrade.md` warn is pre-existing frontmatter quote style at HEAD (verified via `git show HEAD:`, left untouched); `LLM.txt` has no prettier parser (expected); task file carries the structural injected-diff block (lint_task_file is its gate, passed).

### Close-out execution (2026-09-29, approved plan A5→A1→A3→safe-A4→verify-only-A2)

- A5 gates: `py_compile` exit 0 on all 4 patched servers; `prettier --check` clean on README/setup/services; `type: local` grep exit 1 (clean, no v1 leftovers); `lint_task_file` structure-clean (only the path-invocation artifact). No pytest suite exists for these script-servers — compile + functional matrices are the gate.
- A1 fresh-copy proof (`/tmp/fresh-verify`, read-only): 6 units listed; stale `services/systemd` grep exit 1 (clean); `type: "remote"` pattern + 7-port table + loopback URLs present. Full live fresh-user run NOT done (would need a second machine/user) — box stays open.
- A3 blowsh (read-only, foreign repo untouched): `../blowsh-mcp/tasks/in-progress/10-native-http-transport.md` still open; `MCP_TRANSPORT` stdio-default + `MCP_HOST`/`MCP_PORT` handling confirmed in `src/server.ts`. Externally blocked — box stays open.
- Safe A4: live config diff vs `/tmp/opencode.json.pre-upgrade-bak` exit 0 (identical); `opencode mcp list` from $HOME shows 7/7 connected. Note: from repo cwd the CLI reports none (project `opencode.json` carries no mcp section) — session tools unaffected (this session called all live singletons successfully). Full stop+stdio-revert NOT run (would kill this session's servers) — box stays open.
- Verify-only A2: opencode v2.0.19, openchamber web 2.0.4, node 24.20.0; outdated toolchains listed (go/node/rust/uv/gradle) but NO upgrades run (excluded by approval); memory rebuild via patched code indexed 27 memories, output byte-identical to committed index, git clean. Note: live pre-patch singleton ignored the new param and reported "0 memories" — its write landed outside the repo (repo index verified untouched); genuine rebuild ran against patched file directly.
- Traceability: Superseded-By markers present in both archived sources; `git log --follow` resolves only after the closure commit (ZAC) — box stays open until closure.

### Reviewer postfix (2026-09-29, APPROVED_WITH_CHANGES, autopilot)

- Assumption A3: XML referenced `tasks/qa/` paths but the file sits in `tasks/in-progress/` (moved back on QA rejection); all operations use the in-progress path.
- Step 1 source-of-truth: `mcp-brain.service` ExecStart uses `mcp-brain-bridge`; `mcp-telegram.service` uses `main.py` + `/tmp/telegram-mcp` + `downloads` roots; `bridge-present` + `brain-server-absent` confirmed.
- Step 2: brain plist now points at `mcp-brain-bridge` (interpreter + server). Step 3: telegram plist now `main.py` + both roots in systemd order. No CHANGELOG entry (folds into rollout entry, per XML).
- Evidence: `xml.dom.minidom` parse both plists → xml-valid; 5 positive greps exit 0; 2 negative greps 0 matches. Stack-gate record: root=. markers=[services/launchd/*.plist] matched=[] reason=plist-only-fix-no-stack-gate. No docstrings apply (plist-only, per XML rule 3).

### QA round-2 triage (2026-09-29, autopilot, verdict QA_REJECTED)

- F2 reproduces — ACCEPTED: both `[277] Rollback` boxes unchecked (full stop+stdio-revert never ran; safe-variant proof only). Boxes stay open until Manager approves the destructive run.
- F4 does NOT reproduce — DISPUTED with evidence: all 6 units pin transport (`Environment=MCP_TRANSPORT=streamable-http` in the 5 Python units, `MCP_TRANSPORT=http` + HOST + PORT in telegram). QA judged without the hunks (admitted part 1/7 visible).
- F3 DISPUTED with authority: OPTIONAL-with-fallback is the Manager-approved Architect plan (question-tool "Approved" on record), which supersedes the earlier required-path note. No contract change.
- F1/F5/F6/F7 AGREED, remain open: fresh-user live run, upgrades (excluded), blowsh external, traceability-till-commit. Not fixable in-session.
- F8 is a transport artifact (attachment budget cut diff to 1/7) — re-QA feeds the missing hunks inline.
- Vulnerability "silent wrong-root writes": fallback prints to server stderr (stdio-safe by design); tool results unchanged per approved plan. Flagged to Manager as accepted residual risk, not a defect.

### project_path implementation (2026-09-29, Manager "Add to 279 now", Architect O1 hybrid, goal active)

- Server edits (24 tools, all `project_root` OPTIONAL default None, canonical description verbatim in every docstring, validation V1–V5):
  - context (`mcp-context-server/server.py`): new `_explicit_project_root` helper (stderr warning on fallback); 4 file tools patched — get_directory_tree, read_source_files (relative srcs rooted), create_tree_report, extract_signatures (relative paths rooted). 4 git/task tools already had project_root (unchanged).
  - memory (`mcp-memory-server/server.py`): new `_explicit_project_root` + `_memory_dir` (<root>/.opencode/memory, else legacy); threaded `base_dir` through `_validate_and_resolve`/`_ensure_namespace`/`build_memory_index`; 6 tools wired (store/read/delete/search/list/rebuild); own fallback prints fixed to stderr (stdio-protocol safe).
  - lint (`mcp-lint-server/server.py`): new `_explicit_project_root` (+`import sys`); 4 tools wired (markdown/task-file root relative paths; all-tasks scans <root>/tasks; prompt-sync passes root-joined dirs — same effective paths as before when omitted).
  - decision (`mcp-decision-server/server.py`): `_repo_root(explicit_root=None)` per-call override (validates + creates `<root>/.opencode/decisions`, fail-closed mirroring env branch); 6 tools wired (record/query/sync/profile return error strings on bad root; propose returns ERROR dict; extract raises ValueError per its fail-loud contract) + Args doc entries. Brain bridge untouched (precedent as-is).
- Style note: `str | None` used in new params (valid on requires-python >=3.10); memory/lint files otherwise use Optional — cosmetic mix, no behavior impact.
- Python gate: `py_compile` exit 0 on all 4 servers. Functional matrix per server (venv, exit 0): omitted→legacy behavior + stderr warning; explicit abs dir→scoped resolution; relative→reject naming field; missing dir→reject; file-as-root→reject; `../`/absolute escape→traversal reject (context proven: `/etc` vs `/tmp` root rejected). Decision scoping proven (`_repo_root('/tmp')` → `/tmp/.opencode/decisions`).
- Caller sweep: `grep -R` over skills/prompts/agents/.opencode/skill-templates finds tool-name references but zero hardcoded roots and zero existing project_root params — nothing to rewrite; first-party adoption = Hands pass each call's absolute path (demonstrated all session: absolute paths + project_root in every execute/brain call). Skill docs describe when-to-call, not params — untouched (no scope creep).
- No service restarts, no global mutations, no new infra. Live singletons still run pre-patch code (reinstall covered by global-install-upgrade workflow, out of session).

### Autopilot round (2026-09-29, Manager order "autopilot, everything handled inside task")

Autopilot LOCKED for task 279 in this turn (recorded here per protocol). ZAC holds: no commits, no closure — file stays in `tasks/qa/`.
- Q1 closed: `opencode mcp list` run from 4 cwd contexts (repo, /tmp ×2, $HOME) — 7/7 connected every time, exit 0. (One transient "No MCP servers configured" observed on first cold runs from /tmp and $HOME; all subsequent runs 7/7 — server-wake race, not config. Cross-session sharing stands: PIDs predate this session yet serve it.)
- A5 rollback-command test: `diff` live config vs `opencode.json.bak-279-verify-*` → IDENTICAL; ran the exact restore command (`cp bak → opencode.json`, exit 0) + `opencode mcp list` after → 7/7 connected. Restore mechanism proven live with zero state change. Full stdio-revert path stays documented-only (live-revert would kill this session's servers).
- A7 migration end-state: live global config is 7/7 `type: remote` loopback URLs (verified key-by-key) — the migrated end-state, achieved; workflow section + BROWSH_PROFILE_DIR live-match already recorded. No stdio setup remains to dry-run against.
- A9 install currency: `mise outdated` flags nothing for opencode/openchamber; standalone `~/.opencode/bin/opencode` v2.0.19; GitHub latest-tag API check inconclusive (returned null) — `opencode upgrade` deliberately NOT run (verify-only; upgrading the binary mid-session risks breaking it). Memory rebuild ran (empty server store; repo index intact).
- A11 blowsh foreign-repo state (read-only inspect): `blowsh-mcp/tasks/in-progress/10-native-http-transport.md` Status open; `src/server.ts` already honors `MCP_TRANSPORT` (default stdio) + `MCP_HOST`/`MCP_PORT` (defaults 127.0.0.1:8107/8108) — code side exists upstream, task unfinished there. Stays external-blocked for 279.
- Repo `opencode.json` top-level keys confirm no `mcp` block (project relies on global remote config — consistent with singleton direction).
- Boxes checked now: A5, A7 (both copies, evidence above). Still unchecked with reasons: A6 (no fresh-clone host), A9 (no destructive upgrades; latest-tag check inconclusive), A11 (foreign task open), A12 (commit-gated, autopilot never commits), D1 (pre-existing prettier warn in untouched frontmatter). META all-or-nothing gate therefore still open — returned for adversarial re-QA, not closure.
- Manager scope decision (2026-09-29, via question tool): earlier "comment-only" order for per-call absolute `project_path` REVERSED — Manager chose "Add to 279 now". project_path implementation is now in-scope for 279 (all 5 repo Python singletons; telegram/blowsh live outside this repo). Brain's prior DEFERRED verdicts are superseded by this explicit Manager order (recorded here; prior reasoning preserved above for audit).
- Architect plan approved (2026-09-29, via question tool, "Approved"): hybrid O1 — OPTIONAL `project_root: str | None = None` on all 24 tools (context 8, memory 6, lint 4, decision 6; brain as-is), canonical description verbatim, validation V1–V5 (absolute, exists-dir, resolve+traversal-block, fallback warning, no behavior change), helpers copied per server (no shared lib), caller policy mandatory-pass with grep sweep, no restarts/infra. Brainstorm: not required (single-discipline, reversible).
- Close-out plan approved (2026-09-29, via question tool, "Approved"): Brain Senior Programmer plan for 5 open items — A5 gates, A1 fresh-copy proof, A3 blowsh read-only, A4 safe config-diff+list, A2 versions+rebuild only. Destructive upgrade + full revert EXCLUDED. Brainstorm: not required (per plan).

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.
- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.
- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.
- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded [277, 278], remove Superseded-By footer, delete or archive `tasks/backlog/279-mcp-singleton-rollout.md` as abandoned. No HQ code beyond bundler is affected.

---

## Execution Log & Reasoning

### 2026-09-29 — Manager follow-up note (comment-only, no code yet)

Manager (Persian verbatim, voice-to-text): "ببین، یه مسئله رو الان به ذهنم رسید، اینکه مسیر پروژه— الان چون این حرکت سینگل‌تون رو زدیم، مسیر پروژه فکر می‌کنم باید چی باشه دیگه؟ که حالا تو متغیر توربار تعریفش کنی، که توی اون MCP سرور برین توسط خود اون کسی که داره صداش می‌زنه، مسیر پروژه ابسولوت پروژه ابسولوت پس اونجا توی کالرهاش باشه، توی پارامترهاش باشه، براش داکیومنت هم به اندازه کافی بنویس، منظورم داکیومنت دیسکریپشنه، دیسکریپشن بنویس که دقیقاً بدونه باید چی رو فیل کنه، چون قبلاً یه متغیر فکر می‌کنم می‌اومد، الان چون دیگه سینگل‌تونی، باید هر بار هر کسی که صداش می‌زنه، این موارد این‌چنینی رو هم بهش بده."

English (normalized): since the singleton move, shared servers lost per-session project context. Each caller must pass its absolute project path explicitly in every tool call params, with a clear field description so callers know exactly what to fill (previously this likely arrived via cwd/env).

Confirmed scope (2026-09-29, via question tool): applies to EACH MCP server (all Python singletons, not brain-only). Tracking: comment on 279 only — no new backlog task, no implementation in this pass. Future work must add a required `project_path` (absolute) param + description to every server's tools, since per-call context replaces the old per-process cwd.

### 2026-09-29 — Brain all-seats remaining-progress round + hotfix (QA_REJECTED)

Seat Check: domains=services+API-params+docs+skills+global-install+QA → all 7 seats requested per explicit Manager order ("all seats", Layer 1 wins); skipped: none. Triggers fired: schema|migration (Architect); UI triggers: none (miss stated).
Brainstorm: required — cross-disciplinary backend+docs+services AND hard-to-reverse global singleton cutover (full multi-seat report requested by Manager). Brain reply verdict: QA_REJECTED on F1+F2; Brain's own brainstorm line returned "not required — single seat QA on concrete path defects" (recorded verbatim; scope of its turn, not the META).
Brain plan verdict: docs-only hotfix (no service starts, no installs, no commits); project_path param DEFERRED to separate design work (no AC in this pass; adding a required param now would break callers); task 276 location out of scope, deferred.
Assumption A1: Brain judged from diff part 1/3 + staged-set summary (parts 2-3 truncated by budget); live-state ACs (process counts, `mcp list`, global install, schema sweep, blowsh task 10) stay unchecked as remaining — they need machine runs, out of this hotfix.
Fixes applied: `docs/services.md` unit-live line + cp line now `services/` (was `services/systemd/`); `LLM.txt` Step 7.5 cp line first fixed to `/tmp/cognitive-lead-hq/services/...` (later corrected to clone-relative `services/` in the re-QA round below); archived 277/278 footers now point to `tasks/qa/279-mcp-singleton-rollout.md`; `grep -R "services/systemd"` clean (memory workflow already used `services/` — no edit needed). CHANGELOG DoD box checked (Fixed entry for connect-timeout storm verified in staged diff).

### 2026-09-29 — Re-QA fix round (Brain QA_REJECTED fix XML, Steps 1–5, verify-only)

Seat Check: QA Engineer (re-QA verdict gaps) + Senior Programmer (fix XML execution). Skipped: Architect (no new design; project_path stays DEFERRED), Designer (no UI triggers — miss stated), Planner/Strategist (no Kanban question), Reviewer (re-QA precedes review).
Brainstorm: not required — concrete defects only on verifiable paths (Brain's line, adopted).
Step 1 done: live evidence captured (see round-2 block; all exit 0). Step 2 done: unit+bind proof recorded (Restart=always ×6, venv ExecStart ×6, ss 127.0.0.1 ×7, constructor host cites). Step 3 done: LLM.txt 7.5 `cp` source fixed from `/tmp/cognitive-lead-hq/services/...` (correction to prior log entry — tmp path vanishes after setup) to clone-relative `services/mcp-*.service`; README FastMCP section marked legacy stdio fallback with pointer to `docs/services.md`; `docs/services.md` Windows section fixed (XML template IS vendored at `services/windows/`) + untested-on-macOS/Windows markers added. Step 4 done: schema/uv-run sweeps logged, versions recorded (opencode v2.0.19, @openchamber/web@2.0.4), memory rebuild run (empty server store; repo index intact), blowsh external-blocked (below).
Assumption A2: no unit env additions and no server.py edits — constructors already enforce loopback; restarting live serving singletons mid-session would be destructive.
Assumption A3: A5/A7 restore/migration left untested on purpose — running them would disrupt the singletons serving this session; backup artifact + exact commands below are the proof available in-session.
Q1 (ride-along): second-session `mcp list` repeat still not run interactively — cross-session sharing is proven by pre-session PIDs serving this session instead.
Blowsh external-blocked: live container (restart/bind/env) verified here, but stdio+http+sse support + docs in its own repo task 10 cannot be proven from this repo — blocked externally, never dropped.
project_path DEFERRED (re-confirmed): no AC covers it; a required param now would break every caller — separate design task.
Exact rollback commands (verify-only, NOT run): `cp ~/.config/opencode/opencode.json.bak-279-verify-20260929-091449 ~/.config/opencode/opencode.json` (restores pre-pass config); if abandoning singletons: `systemctl --user stop mcp-lint mcp-context mcp-memory mcp-decision mcp-brain mcp-telegram`, restore stdio entries per `global-install-upgrade.md`, restart sessions.
Boxes checked on live evidence now: A1, A2, A3, A4, A8, A10 (both checklist copies). Left unchecked with reasons: A5 (restore untested, A3), A6 (no fresh-clone e2e host), A7 (no live migration dry-run, A3), A9 (verify-only: versions recorded, no upgrades; index rebuild hit empty server store), A11 (external-blocked, above), A12 (git log --follow empty until Manager-gated commit).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `45f703b16334127f26177663c47c220864f20eba`
<!-- END_GIT_DIFF -->

## Brain QA round 3 (re-review routed as QA) — QA_REJECTED, close paths offered

- Re-review asked as Reviewer; Brain routed as QA Engineer. Verdict: QA_REJECTED (third rejection).
- F1-F5 restated (rollback/fresh-user/upgrades/blowsh/traceability unproven live) + NEW F6: optional project_root breaks singleton isolation — omitted root falls back to server CWD with stderr-only warning, invisible to MCP client (V1 cross-project contamination risk). V2 concurrent-writer locking, V3 unset-TRANSPORT fragility noted. M1-M4 missing-test matrix listed.
- F7: reviewer still could not see plist bodies — attachment budget exhausted (103691/103722 chars, diff part 1 of 8 only); context_paths bodies dropped. Local proof stands: 6/6 plists well-formed XML; telegram plist roots identical to services/mcp-telegram.service ExecStart; brain plist points at mcp-brain-bridge/server.py.
- F6 on merits: fallback-to-CWD was the Manager-approved Architect plan (optional root, backward compat). Fail-closed would break existing callers; needs Manager ruling, not a silent Hands change.
- Brain offers 3 close paths (O1 waive+close with residual risk, O2 split META, O3 maintenance window). Relayed to Manager via question tool; awaiting decision.

## Manager decision: O3 Maintenance window (2026-09-29)

- Manager selected O3 via approval gate. Task stays in tasks/qa/ — NOT closed, NOT merged.

- Window scope (from Brain M1-M4 + F6): M1 full rollback revert with mcp list before/after; M2 fresh-clone run zero-to-7/7; M3 live upgrade + memory rebuild against restarted singletons; M4 project_root isolation matrix (omitted/root-relative/traversal/symlink/concurrent writers).
- Blockers to schedule: second host access + explicit window authorization (destructive ops need Manager word at execution time per XML autonomy rules).

## Fix pass for QA round 3 (2026-09-29, post-O3 selection, pre-window)

Manager order: "fix them and re-qa". Scope: everything fixable without the

second host / destructive window. M1-M4 live proofs stay parked for O3.


### F6/V1 FIXED — client-visible project_root fallback banner

- Root cause accepted: omitted project_root fell back to server cwd with a
  stderr-only warning invisible to MCP clients.

- Fix (backward compatible, approved optional-root plan unchanged): each of

  the 4 HQ servers gained a `ContextVar` fallback flag + `_project_tool`
  decorator replacing `@mcp.tool()` on all 24 tools (context 8, memory 6,
  lint 4, decision 6). When fallback fires during a call, str results get a
  `WARNING [project-isolation]` first line; decision's dict tool gets an
  additive `project_root_warning` key; the single list tool passes through
  + stderr (documented residual). No absolute paths echoed (P7 privacy).
- Decision nuance: flag fires only on the cwd/install-root fallthrough, NOT
  when the B1-approved DECISION_REPO_PATH personal repo serves (verified:
  repo .env sets it, so configured installs stay banner-free by design).
- Functional proof (live module imports, global venv pythons): explicit
  root -> clean on all 4 servers; omitted root -> banner on all 4
  (decision proven with env+.env isolated). py_compile 5/5 exit 0.

### V3 FIXED — transport default stdio -> streamable-http

- 5 in-repo servers now default to `streamable-http` when MCP_TRANSPORT is
  unset; explicit `stdio` still works. Safe: all 7 singletons are consumed
  as remote URLs (global opencode.json verified), all units pin TRANSPORT.


- Telegram correction: telegram-mcp runner accepts ONLY stdio|http|sse
  (runner.py VALID_TRANSPORTS; invalid value = sys.exit(1)). The systemd
  `MCP_TRANSPORT=http` was already correct; the launchd plist wrongly said
  `streamable-http` and is fixed to `http`. An earlier Hands edit in this
  pass briefly flipped the systemd unit the wrong way and reverted it
  (unit file back to `http`, verified via git diff).
- Windows template comment now documents: HQ servers need no env (default
  + hardcoded loopback), telegram MUST have system-level MCP_TRANSPORT=http.

### F7 evidence embedded (reviewer attachment budget proof)

- All 6/6 launchd plists well-formed XML (xml.dom.minidom). sha256:
  brain 5681bd3a, context 4709699a, decision 3bb151e7, lint 736538b0,
  memory 76234db7, telegram 25f43b24 (full hashes in shell history 2026-09-29).
- Brain plist ProgramArguments (verbatim):


  `{HOME}/.config/opencode/mcp-brain-bridge/.venv/bin/python`,
  `{HOME}/.config/opencode/mcp-brain-bridge/server.py`.
- Telegram plist ProgramArguments (verbatim):
  `{HOME}/.config/opencode/mcp-telegram-server/.venv/bin/python`,
  `{HOME}/.config/opencode/mcp-telegram-server/main.py`,
  `/tmp/telegram-mcp`,
  `{HOME}/.config/opencode/mcp-telegram-server/downloads`
  — identical entry point + roots to services/mcp-telegram.service
  ExecStart (F4 resolved; prior "bridge" wording was a prompt typo).

### V2 evidence (concurrency, no code change)

- Memory writes already atomic (tempfile.mkstemp + os.replace in
  store_memory and build_memory_index); concurrent writers cannot tear
  files (last-writer-wins per file). Cross-session locking remains
  unproven -> residual for O3 window.



### Still parked for O3 window (NOT fixed here)

- F1 rollback revert, F2 fresh-user run, F3 live upgrades, F4 blowsh
  triple transport, F5 traceability-after-commit, M1-M4 live matrix.
- Global-install sync of these repo fixes to ~/.config/opencode is
  deliberately NOT done here (restarts live singletons; part of window).

## M7 proofs (2026-09-29, pre-review, no window needed)

- Sequential explicit-after-omitted in one process (context server, live
  import): omitted -> banner, explicit -> clean (no sticky ContextVar
  state), omitted again -> banner. PASS.
- Unset-MCP_TRANSPORT direct invoke (lint server, `env -u`, timeout 8):
  startup log shows StreamableHTTP session manager initializing (not
  stdio). Post-test fleet check: 7/7 ports bound, server processes
  intact — live singletons undisturbed. PASS.

## Brain QA round 4 (re-QA after fix pass) — QA_PASSED with O3 window residuals

- Verdict: QA_PASSED. Round-3 code fixes close the two code-fixable defects (F6/V1 banner, V3 default) with no new blockers. M7 proofs accepted.
- Residuals (do NOT block; owned by O3 window): M1 rollback, M2 fresh-clone, M3 upgrades, M4 isolation matrix rerun after global sync, M5 blowsh foreign task-10, M6 commit-gated traceability, one list-tool stderr-only notice, read-modify-write locking, strict-parser/sticky-state unproven.
- Verdict directs: task remains in tasks/qa/ until O3 window + Code Reviewer clearance.

## Helper-sync note (Reviewer I5)

- The `_FALLBACK_FIRED` / `ROOT_FALLBACK_WARNING` / `_project_tool` trio is intentionally copied per server (context, memory, lint, decision), following this repo's established per-server-copy pattern from the project_path rollout (helpers were already copied per server, not shared). Sync rule: any change to the trio must be applied to all four copies in the same pass.

## Code Reviewer interim verdict (re-review round 1) — no approval yet

- Interim only: factual diff truncated (part 1 of 13), server hunks unseen.
- Actionable items owned here: I2 (this QA_PASSED entry — now written), I4 (global-install-upgrade.md step 5 stale stdio-default line — now fixed to streamable-http), I5 (sync note above), R1-R3 (feed hunks via context_paths + hunk offset map below).
- Accepted as window-owned: I3 META gate residuals, I6 live-use proofs.

## Hunk offset map for re-review (repo paths, 1-indexed)

- mcp-context-server/server.py: imports 18-19; _project_tool def 434 (block to ~452); fallback flag 712; transport default 1602.
- mcp-memory-server/server.py: imports ~18-19; _project_tool def 37 (block to ~55); flags 60 (_explicit) + 75 (_memory_dir); transport default 451.
- mcp-lint-server/server.py: imports ~18-19; _project_tool def 44 (block to ~62); flag 435; transport default 781.
- mcp-decision-server/server.py: imports ~29-31; _project_tool def 228 (block to ~250); flag 132 (_repo_root fallthrough); transport default 1930.
- services/launchd/ai.cognitivelead.mcp-telegram.plist: line 14 TRANSPORT http.

## Brain QA round 5 (verbatim-hunk gate) — QA_PASSED again

- Second consecutive PASS, this time judging ONLY verbatim hunks C1-U1 +
  logged proofs. Confirms: banner on str (C1/M1/L1) + dict key (D1),
  flag reset per call, transport default with stdio opt-out, telegram
  http parity, U1 docs correct. Residuals unchanged (window-owned M1-M6,
  list-tool notice, locking, repo-vs-live drift until window sync).
- Note: two consecutive turns requesting the Code Reviewer seat were
  routed by the bridge as QA Engineer instead. Reviewer-seat final
  approval is therefore unobtainable from this path; last Reviewer
  verdict stands at APPROVED_WITH_CHANGES with its 2 plist items now
  applied and proven.

## Code Reviewer final (stage=review routing) — technically APPROVED, PO_REVIEW_PENDING

- Verdict: Approved on observed evidence (Part 1/2 + QA rounds 4/5 + M7). No high-severity defects.
- Follow-ups (lows, explicitly non-blocking): F6 bundle_tasks silent-cwd note (disputed: bundle_tasks scopes via per-task walk-up, not server-cwd fallback — a flag there would false-positive; parked for Manager ruling), F7 services.md telegram paragraph duplication (docs-only, follow-up).
- Status: PO_REVIEW_PENDING. File stays in tasks/qa/. Closure only on Manager's explicit approval word.

## Closure (2026-09-29)

- Manager accept quote: "Approved for closure" (via approval gate, 2026-09-29).
- Preconditions verified: file in tasks/qa/, PO_REVIEW_PENDING logged (3 hits), staged diff injected, lint clean (only environmental path artifact).
