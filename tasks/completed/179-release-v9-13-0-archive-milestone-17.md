# Task 179: Release v9.13.0 + archive completed tasks (milestone-17)

**File:** `tasks/qa/179-release-v9-13-0-archive-milestone-17.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Cut release **v9.13.0** (matches `system-prompt.md` 9.13.0): move all `[Unreleased]` CHANGELOG entries under a `## [9.13.0] - 2026-09-10` header, compact the 15 completed tasks (162–178, minus gaps) into `docs/history/milestone-17-summary.md` and move them to `tasks/archive/`, run all verification gates, and prepare the manual push script for Manager execution.

## Manager's Notes

Direct request (2026-09-10): "load skills about workflow about new release and make a release archive tasks. create a task for it. and create needed script for me too." Skills loaded: `versioning-and-release`, `archive-tasks`, `task-generator`; memory `release/release-workflow` retrieved and followed.

**Version rationale (Manager to confirm):** `system-prompt.md` is at 9.13.0 (Task 178); Unreleased holds Tasks 163–178 + external-opencode-server + goal-restore + OpenChamber changes — new capabilities, non-breaking → MINOR → **v9.13.0**. **Tag gap noted:** latest git tag is `v9.8.0`, but CHANGELOG already contains `9.9.0` and `9.10.0` sections (never tagged). Manager confirms whether to tag only v9.13.0 or backfill.

**Push script:** pre-created this turn at `/tmp/cognitive-lead-push-release.sh` (`VERSION="v9.13.0"`, `set -euo pipefail`, clean-tree + `gh auth status` checks, annotated tag if missing, push commits + tags, `gh release create`, verification printout). ZAC: Hands never execute it — Manager runs it manually after closure.

**Completed tasks to archive (15):** 162, 163, 164, 165, 166, 167, 168, 171, 172, 173, 174, 175, 176, 177, 178 (169/170 do not exist — no gaps to explain, IDs were never issued).

## Local TODOs

- [x] Confirm release version with Manager (proposed v9.13.0; resolve v9.9.0/v9.10.0 tag gap)
- [x] Move `[Unreleased]` entries under `## [9.13.0] - 2026-09-10` via Parse-Then-Append; leave `[Unreleased]` empty
- [x] Generate `docs/history/milestone-17-summary.md` (source distribution, architectural changes, files modified, criteria, per-task summaries)
- [x] Move 15 completed task files to `tasks/archive/` via `git mv`
- [x] Run verification gates: `lint_task_file`, `lint_markdown`, `lint_system_prompt_sync`, `py_compile`, full pytest suite
- [x] Stage via `custom_context_stage_and_inject_diff`, move task to `tasks/qa/`
- [x] Stale-memory audit report (no auto-delete without Manager approval)

## Acceptance Criteria

- [x] `CHANGELOG.md` has `## [9.13.0]` with all Unreleased entries moved; `[Unreleased]` section empty
- [x] `docs/history/milestone-17-summary.md` exists covering all 15 tasks
- [x] `tasks/completed/` is empty; all 15 files in `tasks/archive/` with history preserved
- [x] All verification gates pass (lint ×3, py_compile, pytest)
- [x] `/tmp/cognitive-lead-push-release.sh` exists, executable, `bash -n` clean, references v9.13.0
- [x] `lint_task_file` passes on the release task file

## Verification Evidence

- **Test command:** `grep -n "^\#\# \[" CHANGELOG.md | head -n 5` + `ls tasks/completed/ | wc -l` + `ls docs/history/milestone-17-summary.md` + `lint_system_prompt_sync` + `python3 -m pytest tests/ -q` + `bash -n /tmp/cognitive-lead-push-release.sh`
- **Expected result:** `## [9.13.0]` header present, `[Unreleased]` empty; `tasks/completed/` empty (0 files); milestone-17 summary exists; sync clean; pytest all pass; push script syntax ok
- **Actual result:** `## [9.13.0] - 2026-09-10` at CHANGELOG line 9, `[Unreleased]` empty (line 7); `tasks/completed/` 0 files, 15 files in `tasks/archive/`; `docs/history/milestone-17-summary.md` 158 lines (manager 13 / telegram 2 / orchestrator 0; 7 feature / 7 improvement / 1 bug); `lint_task_file` ✅, `lint_markdown` ✅ ×2 (CHANGELOG + summary), `lint_system_prompt_sync` ✅, `py_compile` OK, pytest **145 passed** (`uv run --project mcp-context-server --with pytest --with pyyaml pytest tests/ -q`; note: bare `pytest` and context-only env fail on missing `yaml` — env union required); `bash -n` on push script clean, `VERSION="v9.13.0"`, chmod +x
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Wrong version header or duplicate categories corrupt Keep-a-Changelog structure; archiving the wrong files loses Kanban history; tagging over the v9.8.0→v9.13.0 gap confuses release lineage.
- **Rollback plan:** `git restore CHANGELOG.md docs/history/` before staging; archived tasks recoverable via `git mv tasks/archive/<id>-*.md tasks/completed/`; never delete tags — if a wrong tag is pushed, Manager deletes it manually via `gh release delete` + `git push --delete origin <tag>`.

---

## Execution Log & Reasoning

**Version decision:** Manager approved v9.13.0, tag-only (no backfill of never-tagged 9.9.0/9.10.0). Matches `system-prompt.md` 9.13.0; Unreleased held new capabilities (persona/decision servers, OpenChamber, blowsh skill) → MINOR.

**Edits:**
- `CHANGELOG.md` — inserted `## [9.13.0] - 2026-09-10` directly below `## [Unreleased]` (single-line move, all Added/Changed/Removed entries now under release header; Unreleased left empty). No duplicate headers.
- `docs/history/milestone-17-summary.md` — new 158-line summary drafted via delegated subagent (matched milestone-16 structure): 15 tasks (162-168, 171-178; 169/170 never issued), source 13 manager / 2 telegram / 0 orchestrator, 7 feature / 7 improvement / 1 bug.
- 15 files `tasks/completed/` → `tasks/archive/` via `git mv` (single command, history preserved; `tasks/completed/` now empty).
- `/tmp/cognitive-lead-push-release.sh` — pre-created per `release/release-workflow` memory (`set -euo pipefail`, clean-tree + `gh auth status` gates, annotated tag if missing, push branch + tags, create-or-verify `gh release`, ls-remote + release URL verification). Manager runs it manually post-closure (ZAC).

**Stale-memory audit:** searched memory for archived-task topics — no stale or superseded entries found; all indexed memories are active workflow docs. No deletions proposed.

**Verification:** `lint_task_file` ✅, `lint_markdown` ✅ ×2, `lint_system_prompt_sync` ✅, `py_compile` OK, pytest **145 passed** (env note: suite needs `mcp` + `yaml` + `pathspec` union — `uv run --project mcp-context-server --with pytest --with pyyaml`).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 9f44dac..e053362 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.13.0] - 2026-09-10
+
 ### Added
 
 - **External OpenCode server for OpenChamber stability (2026-09-10):** New systemd user unit `opencode-server.service` (`~/.config/systemd/user/`, enabled at boot) running `opencode serve --hostname 127.0.0.1 --port 4096` loopback-only (`Restart=on-failure`); OpenChamber attaches via drop-in `openchamber.service.d/external-opencode.conf` (`OPENCODE_HOST=http://127.0.0.1:4096`, `OPENCODE_SKIP_START=true`, `After=` ordering). Replaces the supervised managed server, which stalled its event loop every few hours (all 5 MCPs `server unavailable` simultaneously, 3 watchdog restarts/24h; root-caused from `opencode.log` + journal, no OOM). Community-proven path (upstream #2258: 3 days stable). Verified: unit parses, `:4096` loopback-only, `/session` → 200. Runbook `docs/openchamber-tailscale.md` gains §2c (setup/verify/restart-order/rollback) + troubleshooting rows + §7 loopback note. **Follow-up fixes same day:** (1) cold `.venv` in global `mcp-{context,memory,lint}-server/` made every spawn sync-from-network past the 15 s MCP timeout (only Docker-based blowsh survived) — ran `uv sync --project` once per server; (2) systemd user units never read `~/.bashrc`, so the new service had no `uv` at all — pinned full interactive PATH manager-wide via `~/.config/environment.d/zz-shell-path.conf` (`zz-` prefix required: `/usr/lib/environment.d/99-*`/`990-*` reset PATH afterwards) + `set-environment` for the running manager; rejected `import-environment` (reboot-loss), `bash -lc` wrappers, `PAMName=login`. Doc §2c/§6 corrected to the two-cause version (PATH first, venv second).
diff --git a/docs/history/milestone-17-summary.md b/docs/history/milestone-17-summary.md
new file mode 100644
index 0000000..9c3e232
--- /dev/null
+++ b/docs/history/milestone-17-summary.md
@@ -0,0 +1,158 @@
+# Milestone 17 Summary
+
+**Date:** 2026-09-10
+**Tasks Compacted:** 15
+**Version:** 9.13.0
+
+## Source Distribution
+
+| Source       | Count |
+| ------------ | ----- |
+| orchestrator | 0     |
+| telegram     | 2     |
+| manager      | 13    |
+
+## Architectural Changes
+
+Milestone 17 spans release + plugin installs (162-164), OpenChamber multi-device (165-166), persona/decision automation build (167-168), workspace hardening META (171-172), docs follow-up (173), persona expansion + automation pause (174-176), and audit/hardening + prompt optimization (177-178).
+
+- **Release + plugins (162-164):** Archived 31 completed tasks into milestone-16, released v9.10.0 via Parse-Then-Append with push script, drift-audited and re-synced global install + Telegram fork (162); integrated `@tarquinen/opencode-dcp` mirroring the goal-plugin pattern across repo + global configs and LLM.txt (163); installed `@nano-step/opencode-worktree-plugin` globally via `owt-setup` with `.gitignore` guards + docs, deliberately NOT in plugin arrays (docs-only repo has no node_modules).
+- **OpenChamber (165-166):** Researched OpenChamber v1.22.2, installed globally via npm on alternate port 3005 (3000 taken by Next.js), Tailscale-only bind with UI password in `~/.secrets`, disabled goal + worktree plugins (DCP-only), Cloudflare Tunnel deferred; added optional-install LLM.txt guide with ask-user-first gate plus auto-start and pairing runbook.
+- **Automation build (167-168):** Retired the full `loop-engine/` daemon (48 files) + `deploy/`, replaced with `mcp-persona-server/` (Dual Dispatch, session transcripts, Telegram approval gates) and 4 slash commands; added `mcp-decision-server/` (redaction, decision repo schema, review-gated profile evolution) with `manager-decision` skill template and executor integration.
+- **Hardening META (171-172):** Bundled post-sprint fixes (DECISION_TEMPERATURE, BOM handling, docstring drift guards) with MCP workspace cleanup (shared `mcp-common`, per-server pyprojects + uv.lock, split PERSONA/DECISION models, approval notes); sync task re-staged 3 files whose fixes missed the closure commit.
+- **Pause + audit (174-178):** Added 5 missing persona commands and removed the `brainstorm-swarm` skill wrapper (scheme survives in fragment 12), then paused the whole automation (executor sections commented, 9 commands archived, both MCP servers unwired repo + global) back to manual workflow; hardened `mcp-context-server` (traversal rejection, depth/entry/file caps, banned dirs, report metrics), added `blowsh` skill, archived stale loop-engine docs, and stubbed the brainstorming protocol + scoped clarity style while bumping system-prompt 9.10.0 → 9.13.0.
+
+## Files Modified
+
+| File                                                   | Change                                                                                                        |
+| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
+| docs/history/milestone-16-summary.md                   | New 31-task archive (162)                                                                                     |
+| CHANGELOG.md                                           | 9.10.0 release + Unreleased entries for 163-178                                                               |
+| opencode.json + tui.json (repo + global)               | DCP added (163), dcp-only after goal removal (165), persona/decisions added (167-168) then removed (176)      |
+| LLM.txt                                                | DCP docs, owt section, OpenChamber optional guide, plugin install verification (163-166, 173)                  |
+| mcp-persona-server/                                    | New persona dispatch server + session/telegram modules + fixes (167, 171, 174)                                 |
+| mcp-decision-server/                                   | New decision learning server + redactor (168)                                                                 |
+| mcp-context-server/server.py                           | Workspace confinement + runaway caps + report metrics (177)                                                   |
+| mcp-common/ + per-server pyproject/uv.lock             | Locked workspace with shared loader (171)                                                                     |
+| .opencode/commands/                                    | 9 persona commands created (167, 174), then archived (175)                                                    |
+| agents/cognitive-executor.md + cognitive-discovery.md  | Persona/decision loops, manual workflow default, clarity style (167-168, 174-175, 178)                        |
+| prompts/fragments/* + system-prompt.md                 | Skills registry, brainstorm stub, clarity constraints, 9.10.0 → 9.13.0 (174, 177-178)                          |
+| skill-templates/                                       | manager-decision added (168), brainstorm-swarm removed/restored inert (174-175), blowsh added (177)            |
+| docs/openchamber-tailscale.md                          | New Tailscale pairing + ops runbook (165)                                                                     |
+| archive/automation-paused-2026-09-09/                  | Archived commands, loop-engine docs, RESTORE.md with verbatim JSON blocks (175-177)                            |
+| .env.example                                           | PERSONA_*/DECISION_* vars added then PAUSED-commented (167-168, 176)                                          |
+| packages/cognitive-lead-decisions/                     | Decision repo schema + validate/compile scripts (168)                                                         |
+| README.md + .gitignore                                 | Plugin blocks, paused banner, blowsh row; worktree + cache guards (164, 166, 173, 177)                         |
+| scripts/smoke_test_live.py                             | Added (171) then removed as inapplicable while servers paused (177)                                           |
+
+## Criteria Met
+
+| Task | Acceptance Criteria                                                        | Status |
+| ---- | -------------------------------------------------------------------------- | ------ |
+| 162  | Milestone-16 archived, 9.10.0 released, global + fork synced               | ✅ Met |
+| 163  | DCP in all 4 plugin arrays, docs + global install verified                 | ✅ Met |
+| 164  | owt installed globally, project guards + docs, tests green                 | ✅ Met |
+| 165  | OpenChamber on 3005 via Tailscale, dcp-only configs, runbook written       | ✅ Met |
+| 166  | LLM.txt optional OpenChamber guide + checklist, Tailscale-only verified    | ✅ Met |
+| 167  | Loop-engine removed, persona MCP spec + Telegram approval gate defined     | ✅ Met |
+| 168  | Decision schema + invocation contract + gated evolution loop               | ✅ Met |
+| 171  | META 169+170 bundled: split models, approval notes, locked workspace       | ✅ Met |
+| 172  | Stranded fixes re-staged, headers synced, suite green                      | ✅ Met |
+| 173  | Plugin install + cache-verify docs in LLM.txt and README                   | ✅ Met |
+| 174  | 5 persona commands added, brainstorm skill removed, prompt 9.10.0 in sync  | ✅ Met |
+| 175  | Executor automation commented, 9 commands archived, manual default active  | ✅ Met |
+| 176  | Both MCP servers unwired repo + global, restore record complete            | ✅ Met |
+| 177  | Audit cleanup, server hardening, blowsh skill, prompt 9.12.0 in sync      | ✅ Met |
+| 178  | Brainstorm stub + scoped clarity style, prompt 9.13.0 in sync             | ✅ Met |
+
+## Individual Task Summaries
+
+### Task 162: Archive Release Global Upgrade
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Archived 31 completed tasks to milestone-16, released v9.10.0 with push script, re-synced global install + Telegram fork; all suites green (55 + 309 + 446 passed).
+
+### Task 163: Integrate DCP Dynamic Context Pruning Like Goal Plugin
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Mirrored goal-plugin pattern for DCP across project + global configs with LLM.txt docs; official installer used globally, upstream-slowdown caveat documented.
+
+### Task 164: owt Worktree Plugin Integration (Project + Global)
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Chose `@nano-step/owt` over OCX-only/fork alternatives; gatekeeper deviation kept it out of plugin arrays (no node_modules in docs-only repo), global file-based install covers all sessions.
+
+### Task 165: OpenChamber Install + Multi-Device (Android/PC) + Internet Exposure via Cloudflare
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Installed OpenChamber 1.22.2 globally on port 3005 Tailscale-only with UI password; goal/worktree plugins disabled; Cloudflare Tunnel deferred per Manager directive.
+
+### Task 166: Update LLM.txt with optional OpenChamber install guide
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Added ask-first optional install section with Tailscale bind + auto-start + pairing steps; consolidated prior hardening docs in the same diff, no secrets staged.
+
+### Task 167: Replace Loop-Engine With Persona Skill-MCP Slash Commands
+
+- **Type:** improvement
+- **Source:** telegram
+- **Reasoning:** Decommissioned 48-file loop-engine daemon; built `mcp-persona-server` with Dual Dispatch + Telegram gates and slash commands; QA rounds fixed dispatch precision, gate scoping, and lineage dedupe (87 passed).
+
+### Task 168: Manager-Decision Skill With Separate Learning Repo
+
+- **Type:** feature
+- **Source:** telegram
+- **Reasoning:** Built decision repo schema with verbatim quotes + redaction, `mcp-decision-server` with 5 tools, skill template, and review-gated profile evolution (101 passed with persona suite).
+
+### Task 171: post-sprint-workspace-bundle
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** META bundling post-sprint fixes (temperature env, BOM, drift guards) with MCP workspace lockdown (mcp-common, uv.lock, split models, approval notes); survived QA_REJECTED + reviewer FAIL triage with evidence (120 passed).
+
+### Task 172: Sync Stranded Post-Closure Fixes
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Staging-only sync: re-staged 3 files whose working-tree fixes missed the Task 171 closure commit; no code changes, suite green on exact tree.
+
+### Task 173: Plugin Install Docs Follow-Up
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Documented the referenced-but-never-installed plugin outage (install commands + cache verification + restart) in LLM.txt and README; QA scope-creep nit fixed.
+
+### Task 174: Add missing persona slash commands and remove brainstorm-swarm skill
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Added 5 missing persona commands, removed skill wrapper (swarm scheme survives in fragment 12), rebuilt prompt to 9.10.0; manager-ordered extension fixed persona persistence, context lane, gate bottlenecks, and lineage fallback (138 passed).
+
+### Task 175: Disable automation in Cognitive Executor agent, archive automation commands, restore manual workflow
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Paused immature automation via HTML comments + `git mv` of 9 commands to archive with RESTORE.md; zero deletions, manual workflow restored as active default.
+
+### Task 176: Disable persona + decision MCP servers (repo + global), document rollback/restore record
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Removed both MCP blocks + permission lines from repo and global configs (JSON has no comments), preserved verbatim blocks in task log + RESTORE.md; 5 remaining servers verified connected.
+
+### Task 177: Comprehensive audit cleanup, MCP server hardening, and blowsh skill integration
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Archived stale loop-engine docs, hardened context server against wedging bugs with regression tests, added blowsh skill, overhauled README; paused state preserved throughout (145 passed).
+
+### Task 178: Prompt optimization — brainstorm stub + clarity style
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Stubbed 53-line brainstorming protocol to 6-line hybrid trigger (~350 tokens saved) and added final-response-only clarity constraints; prompt reassembled byte-identical at 9.13.0.
```
<!-- END_GIT_DIFF -->
