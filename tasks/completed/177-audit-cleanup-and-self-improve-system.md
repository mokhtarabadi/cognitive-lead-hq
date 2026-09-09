# Task 177: Comprehensive audit cleanup, MCP server hardening, and blowsh skill integration

**File:** `tasks/qa/177-audit-cleanup-and-self-improve-system.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Audit the repository, remove leftovers including stale docs, and self-improve skills, agents, system-prompt fragments, and MCP servers while preserving the automation-paused state. EXPANSION (Orchestrator re-open order): harden `mcp-context-server` against the two diagnosed wedging bugs (workspace confinement + runaway caps + report metrics), add regression tests, create the missing `blowsh` skill template + registry entry, bump system-prompt to 9.12.0, finish repo cleanup (`fat.md` — verified absent, no-op; archive superseded modularization doc; extend `.gitignore`), overhaul README (paused banner, blowsh tools, paused annotations) + CHANGELOG, verify + atomic QA transition.

## Manager's Notes

User order (verbatim): "now audit project and cleanup and remove left overs , all left overs include docs. and also self improve system all skills, agents, system prompts. mcps. you as a llm try to cleanup, improve, remove left overs. create a goal and continue until finished. a task required."

Constraints carried forward:
- Automation stays DISABLED (Tasks 175/176): persona + manager_decisions MCP servers stay stripped from repo + global opencode.json; executor/discovery automation sections stay commented; 9 commands stay archived under archive/automation-paused-2026-09-09/commands/ with RESTORE.md; brainstorm-swarm skill restored but inert.
- system-prompt.md is a GENERATED artifact: edit prompts/fragments/ + prompts/shared/ only, bump 01-system_version, regenerate via scripts/prompt-build/assemble_system_prompt.py, verify sync.
- Repo is source of truth for global sync; smoke expectation is 5 MCPs connected (persona/decisions absent by design).
- Do NOT delete archived automation implementation; remove only true leftovers (stale docs, dead refs, orphaned files) and document each removal.
- No autonomous git add/commit/push; use stage/inject MCP tool + git mv for Kanban only.

## Local TODOs

- [x] Discovery: map leftovers across docs, skills, agents, prompts, MCPs, root clutter
- [x] Triage each leftover as remove / archive / keep with reason
- [x] Self-improve skills, agents, fragments, MCPs (small, safe, tested edits only)
- [x] Regenerate system-prompt + version bump + sync verification
- [x] Verify functionality (tests, lint, MCP list)
- [x] Step 2: Harden mcp-context-server (workspace guard in get_directory_tree; max_depth=8 + max_entries=2000 + BANNED_DIRS={.git,.cache,__pycache__,node_modules,.venv,venv,proc,sys,dev} in generate_tree; max_files=1000 + BANNED_DIRS in collect_files; report metrics prepend in read_source_files)
- [x] Step 3: Regression tests in tests/test_mcp_servers.py (traversal reject, None input, depth/entry caps, banned-dirs skip) + pytest green
- [x] Step 4: Create skill-templates/blowsh/SKILL.md (5 tools, full params, docker ref, SSRF rules)
- [x] Step 5: Fragment 07 blowsh line + 01-system_version 9.12.0 + prettier + reassemble + byte-identity diff check
- [x] Step 6: Cleanup (fat.md rm — absent=no-op; git mv docs/system-prompt-modularization.md → archive/.../docs-superseded/; .gitignore += .uv/, .uv-cache/, .mypy_cache/, .coverage, htmlcov/; verify tasks/ not globally ignored)
- [x] Step 7: README overhaul (Manual Mode wording, paused banner, (paused) annotations, blowsh skill row + tool suite) + CHANGELOG Parse-Then-Append
- [x] Step 8: Verify (py_compile, full suite, lint_task_file, evidence) + atomic QA transition

## Acceptance Criteria

- [x] Repository audited: every leftover decision (remove/archive/keep) recorded in Execution Log
- [x] True leftovers removed including stale docs; archived automation implementation untouched
- [x] Skills, agents, system-prompt fragments, MCPs self-improved with evidence
- [x] system-prompt.md regenerated from fragments with version bump and sync check clean
- [x] Automation-paused state preserved (persona/decisions absent, manual workflow active)
- [x] get_directory_tree rejects traversal ("/", "..") + None defaults to workspace root
- [x] generate_tree capped (depth/entry limits) + BANNED_DIRS skipped; collect_files capped at 1000
- [x] read_source_files prepends metrics (files processed/skipped, size, duration)
- [x] blowsh skill exists with 5-tool docs; registry + system-prompt 9.12.0 in sync
- [x] Cleanup done (modularization doc archived, .gitignore extended, tasks/ not ignored)
- [x] README + CHANGELOG updated; full suite green; QA transition via custom_context_qa_transition

## Verification Evidence

- **Test command:** uv run --project mcp-persona-server --with pytest --with pathspec pytest tests/ -q
- **Expected result:** all tests pass
- **Actual result:** 145 passed, 8 warnings in 1.66s (post-expansion); re-run after `scripts/smoke_test_live.py` removal: 145 passed, 8 warnings in 1.43s
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** deleting something that is actually load-bearing (archived automation, referenced docs, live config)
- **Rollback plan:** removals limited to verified leftovers; git worktree + staged diff review before QA; `git log --follow` recovery for any file move

---

## Execution Log & Reasoning

Discovery (4 parallel cognitive-discovery subagents, read-only):
- D1 docs/root: `docs/loop-engine/` (5 files) stale — cite deleted `loop-engine/` + `deploy/` paths; `conventions.md:77` cites retired sentinel as live; `setup.md:50-58` lacks paused-state context; `docs/history/` is record (keep); root has no clutter; `context-reports/` gitignored runtime output; `/tmp` refs intentional.
- D2 skills: 32/32 in sync repo↔global, zero `loop-engine|deploy|dispatch` refs; `manager-decision` presents disabled server as live; `versioning-and-release:59` pins stale `V5.3.0`; `system-prompt.md` lacks just-added `brainstorm-swarm` line (stale artifact, version pins match at 9.10.0).
- D3 agents/prompts: executor automation inside PAUSED block, manual workflow active; executor L70 `manager-decision` matrix row live outside block (stale); fragments have zero live automation refs; archive holds 9/9 commands + RESTORE.md; RESTORE step 5 reads as live expectation.
- D4 MCPs/configs: 6 server dirs (persona/decision disabled-but-kept ✓); both opencode.json valid with persona/decisions absent ✓; `.env.example` PAUSED block ✓; caches (`tests/__pycache__/`, `.pytest_cache/`, `.ruff_cache/`) untracked leftovers; `.gitignore` lacks pytest/ruff cache entries; `deploy-prompt-composer.yml` live (`tools/prompt-composer/index.html` exists — kept).

Triage (remove/archive/keep):
- ARCHIVE (git mv, history preserved): `docs/loop-engine/` → `archive/automation-paused-2026-09-09/docs-loop-engine/`.
- REMOVE (untracked runtime only): `tests/__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, 3 probe-generated `context-reports/*.md`.
- KEEP: `docs/history/`, migration docs, `deploy-prompt-composer.yml` (live target exists), inert `brainstorm-swarm` skill, disabled-but-kept servers, `context-reports/` gitignore rule.
- IMPROVE (minimal edits): conventions sentinel line → historical; setup.md → paused banner; manager-decision SKILL → PAUSED banner; versioning SKILL → drop stale pin; executor L70 → PAUSED annotation; RESTORE step 5 → restore-time-only; `.gitignore` → pytest/ruff caches; fragment 01 → 9.11.0 (MINOR, additive registry entry).

Regeneration (fragment-edit workflow): prettier on 9 md files → `assemble_system_prompt.py` → 75,698 bytes; version 9.11.0 in fragment + artifact; `brainstorm-swarm` at system-prompt.md:133; `lint_system_prompt_sync` clean; `git status -- '*.py'` empty (zero out-of-scope changes); suite 138 passed exit 0. `opencode mcp list` re-verified at staging time (expect 5 connected, persona/decisions absent).

Expansion (Orchestrator re-open order, Steps 2–8):
- Hardening (`mcp-context-server/server.py`, py_compile clean): module guards `TREE_MAX_DEPTH=8`, `TREE_MAX_ENTRIES=2000`, `COLLECT_MAX_FILES=1000`, `BANNED_DIRS` (9 names) + `_is_banned_dir` (unstatable = unsafe); `get_directory_tree` mirrors the `create_tree_report` workspace confinement (non-string → root default, escapes → traversal error); `generate_tree` enforces depth/entry caps with `[Max depth reached]` / `[Truncated]` markers and skips banned dirs; `collect_files` prunes banned dirs in `dirs[:]` and caps at `max_files`; `read_source_files` prepends `📊 Report metrics` (processed/skipped/bytes/duration); `PermissionError` widened to `OSError` on unreadable dirs.
- Tests: 7 regression tests appended to `tests/test_mcp_servers.py` (same spec-load pattern): `/` + `..` traversal reject, `None`→root default, depth cap marker, entry cap + banned skip, collect cap + `.venv` exclusion, metrics line (`2 processed, 1 skipped`). New-test run 13 passed; full suite **145 passed** exit 0.
- Blowsh skill: `skill-templates/blowsh/SKILL.md` (5 tools with full params, Docker transport ref, cheapest-tool-first rules, SSRF rule); fragment 07 line added; `01-system_version` 9.11.0 → 9.12.0; prettier clean; reassembled 75,927 bytes, `blowsh` at system-prompt.md:134, `lint_system_prompt_sync` clean, reassembly byte-identical on rerun.
- Cleanup: `fat.md` verified absent (rm no-op); `docs/system-prompt-modularization.md` → `archive/automation-paused-2026-09-09/docs-superseded/` via `git mv`; `.gitignore` += `.uv/`, `.uv-cache/`, `.mypy_cache/`, `.coverage`, `htmlcov/`; only `tasks/.sessions/` scoped under `tasks/` (task files themselves not ignored — verified).
- README + CHANGELOG: Manual Mode heading marked ACTIVE/DEFAULT + paused banner; persona section + slash-commands bullet + manager-decision link marked (paused); loop-engine docs path corrected to the archive; blowsh skill row in registry table + 5-tool suite bullet (was "4 tools"); skill count 32 → 33. CHANGELOG Parse-Then-Append under `[Unreleased]`: Added blowsh bullet, Changed hardening + README bullets. Prettier `--check` clean on all touched md.
- Automation-paused state preserved throughout: persona/decisions still absent from both opencode.json files, commands still archived, manual workflow active; disabled servers' code untouched (only context-server hardened — an active server).
- Smoke test removal (Manager order): `git rm scripts/smoke_test_live.py` (live tester for paused persona/decision servers, no longer applicable while servers are disconnected); grep confirms zero lingering `smoke_test_live` refs in README.md/docs/scripts; CHANGELOG `[Unreleased]` → `### Removed` bullet appended.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.gitignore b/.gitignore
index 4a4043a..ad9e374 100644
--- a/.gitignore
+++ b/.gitignore
@@ -47,4 +47,14 @@ downloads/
 .opencode/worktree-sessions.json
 
 # Persona session transcripts (runtime audit trail, never committed)
-tasks/.sessions/
\ No newline at end of file
+tasks/.sessions/
+
+# Python/pytest runtime caches (never committed)
+.pytest_cache/
+.ruff_cache/
+.uv/
+.uv-cache/
+.mypy_cache/
+.coverage
+htmlcov/
+
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f816fbd..c53d7b0 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -17,6 +17,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Manager-decision learning repo + skill (Task 168):** New `packages/cognitive-lead-decisions/` (`schema/decision.schema.json` with verbatim-quote + linkage fields, `samples/manager_profile.md` baseline, `scripts/compile_profile.py` review-draft printer, `scripts/validate_decisions.py` dependency-free validator) and stdio FastMCP server `mcp-decision-server/` (`redactor.py` sanitize/verify engine, `server.py` with `extract_session_decisions`/`record_manager_decision`/`query_manager_decisions`/`get_manager_profile`/`propose_profile_evolution` — gated sample evolution, never auto-writes); universal `skill-templates/manager-decision/SKILL.md` (extraction/consultation/evolution workflows, per-session example); `opencode.json` `manager_decisions` entry + 5 tool permissions; executor matrix + bootstrapping consult past rulings; `tests/test_decision_server.py` **14 passed**, full suite **101 passed**.
 - **Missing persona slash commands (Task 174):** New `.opencode/commands/{architect,designer,programmer,planner,strategist}.md` dispatching the exact `06-personas.md` names (`Software Architect`, `UI/UX Designer`, `Senior Programmer`, `Project Planner`, `Sprint Strategist`) in the established `qa.md` Dual-Dispatch pattern (persona-specific REPORT guidance: Discovery-First, a11y/environmental checklist, Anti-Hack, Kanban source-of-truth, MoSCoW/WIP); `agents/cognitive-executor.md` command reference updated to all 9 commands. System prompt bumped to **9.10.0** (rebuilt from fragments, sync-check clean).
 - **Persona engine hardening, same task (Task 174 extension, manager order 2026-09-09):** (1) persona persistence — `SESSIONS_ROOT` pinned under the install root + per-task persona identity cards (`load/save_persona_card`, injected every turn), so personas survive across LiteLLM calls; (2) `<hands_context_request>` lane (`CONTEXT_REQUEST` with `scope`/`focus`) + planner/architect re-dispatch loops via MCP discovery tools; (3) bottlenecks fixed — split gate (`open_approval_gate`/`poll_approval_gate`, blocking gate kept as legacy), `slugify_stage()` keeps every `callback_data` under Telegram's 64-byte cap, `PERSONA_MAX_REPLAY_TURNS` (default 50) bounds replay; (4) lineage fallback chain (repo → cwd → global config) with stderr warnings, so every persona sees the full system prompt. Full suite **138 passed**.
+- **Blowsh web skill (Task 177 expansion):** new `skill-templates/blowsh/SKILL.md` documents all 5 blowsh MCP tools (`search_web` consensus engines + intent verticals, `fetch_web` JS-rendered + probe modes, `fetch_web_batch` 10 URLs, `crawl_web` sitemap-aware docs/API refs/wikis, `extract_links`) with the cheapest-tool-first rules; registry line added to fragment 07; `system-prompt.md` regenerated to **9.12.0** (sync-check clean, byte-identical reassembly).
 
 ### Changed
 
@@ -28,6 +29,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Ops follow-ups:** persona/decision server timeouts 120s → 600s (LLM reasoning turns need headroom); decision store moved `packages/cognitive-lead-decisions` → per-project `.opencode/decisions` with cwd-aware resolution (`DECISION_REPO_PATH` → `<cwd>/.opencode/decisions` → install-root fallback), so every repo keeps its own manager notes.
 - **QA round 2 fixes (Task 171 pipeline):** `DECISION_TEMPERATURE` env (default 1.0, clamped) replacing the hardcoded 0.2 in extraction; dotenv loader reads `utf-8-sig` (BOM-proof); `docs/conventions.md` codifies the blank-means-unset rule; parser/export/skip/docstring-guard tests added; dispatch no longer appends task bodies to transcripts (was causing 6MB transcripts → endpoint 400s). Full suite **120 passed**.
 - **Plugin install docs (Task 173):** `LLM.txt` §7.7 + README plugins section now carry both plugin install commands, cache-presence verification (`~/.cache/opencode/packages/`), and the restart requirement — closing the referenced-but-never-installed gap that hid `/dcp-compress`.
+- **Audit cleanup + self-improve pass (Task 177):** `system-prompt.md` regenerated to **9.11.0** (absorbs the restored `brainstorm-swarm` registry line in fragment 07; sync-check clean); `docs/setup.md` gains the automation-paused banner (persona/decision servers disabled, commands archived, global blowsh+telegram note); `skill-templates/manager-decision/SKILL.md` gains a PAUSED banner (skill inert until restore); `skill-templates/versioning-and-release/SKILL.md` drops the stale `V5.3.0` pin; executor skill matrix annotates the `manager-decision` row as paused; `RESTORE.md` step 5 marked restore-time-only; `.gitignore` gains `.pytest_cache/` + `.ruff_cache/`. Full suite **138 passed**, zero `.py` changes.
+- **Context-server wedging hardened + docs overhaul (Task 177 expansion):** `mcp-context-server/server.py` gains runaway-traversal guards — `get_directory_tree` mirrors the `create_tree_report` workspace confinement (escapes rejected, non-string targets default to root), `generate_tree` caps depth (8) + entries (2000) with truncation markers, `collect_files` caps at 1000 files, and `BANNED_DIRS` (`.git/.cache/__pycache__/node_modules/.venv/venv/proc/sys/dev`) is never descended into; `read_source_files` prepends report metrics (processed/skipped/bytes/duration). Fixes the diagnosed wedge where a `/` tree burned 7 CPU-minutes on the single-threaded server and starved all later calls. README overhauled (Manual Mode marked ACTIVE/DEFAULT, persona section + commands + manager-decision link marked paused, blowsh skill row + 5-tool suite, loop-engine docs path corrected, skill count 33); `docs/system-prompt-modularization.md` archived to `archive/automation-paused-2026-09-09/docs-superseded/`; `.gitignore` extended (`.uv/`, `.uv-cache/`, `.mypy_cache/`, `.coverage`, `htmlcov/`).
 
 ### Removed
 
@@ -35,6 +38,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **brainstorm-swarm skill removed, persona covers it (Task 174):** Deleted `skill-templates/brainstorm-swarm/SKILL.md` + global `~/.config/opencode/skills/brainstorm-swarm/` per Manager directive ("we have a persona, no skill needed") — the six-expert scheme and XML schema survive in `prompts/fragments/12-brainstorming_protocol.md`, injected into every `dispatch_session_turn` via `system-prompt.md`; `.opencode/commands/brainstorm.md` rewritten as a pure `Brainstorm Facilitator` persona turn (no skill preload); registry line dropped from fragment 07, `mcp-persona-server/server.py` docstring + executor reference updated, README skill tree pruned. Historical mentions (old CHANGELOG entries, `tasks/archive/*`, `.opencode/memory/*`, `docs/history/*`, `context-reports/*` snapshots) intentionally left untouched. Full suite **120 passed**.
 - **Automation system paused, manual workflow restored (Task 175):** Per Manager order (system not mature enough), the automation rules are neutralized but preserved: `agents/cognitive-executor.md` Persona Loop + Decision Learning Loop wrapped in `AUTOMATION-PAUSED-2026-09-09 ... AUTOMATION-RESUME` HTML comments with an active `## Manual Workflow` section (plan → execute → record → hand off, Manager-directed review, never auto-commit); all 9 automation slash commands moved via `git mv` to `archive/automation-paused-2026-09-09/commands/` (+ `RESTORE.md` with the 6-step restore procedure); `agents/cognitive-discovery.md` verified zero automation refs (untouched). Nothing deleted.
 - **Persona + decision MCP servers disabled repo + global (Task 176):** Per Manager order (disable both, delete nothing), removed the `persona` and `manager_decisions` blocks plus their 9 repo / 11 global tool permission lines from `opencode.json` (repo) and `~/.config/opencode/opencode.json` (JSON supports no comments — blocks removed, code untouched); commented out all active `PERSONA_*` / `DECISION_*` vars in `.env.example` (kept for future restore). Server implementations (`mcp-persona-server/`, `mcp-decision-server/`, skills, transcripts) fully preserved. Restore: re-add blocks from `archive/automation-paused-2026-09-09/RESTORE.md` step 5.
+- **Stale loop-engine docs archived + caches purged (Task 177):** `docs/loop-engine/` (5 files, cited already-deleted `loop-engine/` + `deploy/` paths) moved via `git mv` to `archive/automation-paused-2026-09-09/docs-loop-engine/` (history preserved, nothing deleted); removed runtime caches (`tests/__pycache__/`, `.pytest_cache/`, `.ruff_cache/`) + 3 probe-generated `context-reports/` files (dir stays gitignored). Kept deliberately: `docs/history/` (record), version-pinned migration docs, live `deploy-prompt-composer.yml` (`tools/prompt-composer/index.html` exists), inert `brainstorm-swarm` skill, disabled-but-kept MCP servers.
 
 ## [9.10.0] - 2026-09-04
 
diff --git a/README.md b/README.md
index 48db30c..4bae651 100644
--- a/README.md
+++ b/README.md
@@ -79,9 +79,11 @@ To leave feedback directly on the generated Markdown plans:
 
 The AI will process your inline feedback, generate a revised plan, and wait for your final "Approved" signal before writing code.
 
-## ⚡ Manual Mode Workflow (Pure-MCP Human-in-the-Loop)
+## ⚡ Manual Mode Workflow (Pure-MCP Human-in-the-Loop) — ACTIVE / DEFAULT
 
-For teams that prefer manual copy/paste over the Loop Engine daemon, this is the canonical pure-MCP cycle:
+> **Automation paused (2026-09-09, Tasks 175–176):** the persona/decision automation is disabled — servers stripped from configs, commands archived under `archive/automation-paused-2026-09-09/`. This manual cycle is the active default; see `archive/automation-paused-2026-09-09/RESTORE.md` for the restore path.
+
+This is the canonical pure-MCP cycle:
 
 1. **Manager inputs raw thought / Telegram message** — raw bilingual draft or structured task file in `tasks/backlog/`.
 2. **Orchestrator issues architectural blueprint & awaits approval** — Brain reviews context, proposes plan, and halts for explicit Manager `Approved`.
@@ -123,7 +125,9 @@ The repository includes a standalone web tool at `tools/prompt-composer/index.ht
 
 ---
 
-## 🤖 Persona Engine + Decision Learning
+## 🤖 Persona Engine + Decision Learning (PAUSED 2026-09-09)
+
+> **Disabled, not deleted (Tasks 175–176):** the system below is preserved for future development but not currently enabled. Manual Mode above is the active workflow.
 
 The **Persona Engine** (Tasks 167–168) replaced the retired loop-engine daemon with on-demand persona turns: OpenCode itself calls personas (`/qa`, `/reviewer`, `/manager`, `/brainstorm`) backed by a light LLM holding the full system prompt, with Telegram Approve/Reject hard gates. The **Decision Learning** side captures per-session manager rulings into a separate append-only repo that evolves the manager-AI sample behind human review.
 
@@ -151,7 +155,7 @@ cp .env.example .env
 
 ### Features
 
-- **Persona slash commands** — `/qa`, `/reviewer`, `/manager`, `/brainstorm`, each with Dual Dispatch classification (`XML_EXTRACTED` / `QUESTION` / `REPORT`)
+- **Persona slash commands (paused)** — `/qa`, `/reviewer`, `/manager`, `/brainstorm`, each with Dual Dispatch classification (`XML_EXTRACTED` / `QUESTION` / `REPORT`)
 - **Telegram approval gateway** — task/stage-scoped inline keyboard Approve/Reject with stale-press discard
 - **Auto-continue** — Goal Plugin handles idle detection and continuation
 - **Evidence-bound QA** — No evidence = no commit
@@ -160,10 +164,11 @@ cp .env.example .env
 
 ### Documentation
 
-- [Manager-Decision Skill](skill-templates/manager-decision/SKILL.md)
+- [Manager-Decision Skill](skill-templates/manager-decision/SKILL.md) (paused — server disabled in Task 176)
+- [Blowsh Web Skill](skill-templates/blowsh/SKILL.md) — live-web search/fetch/crawl via the blowsh MCP server
 - [Cognitive Executor Agent](agents/cognitive-executor.md) (Persona Loop section)
 - [Setup Guide](docs/setup.md)
-- Historical loop-engine docs remain under `docs/loop-engine/` for reference (daemon retired in Task 167).
+- Historical loop-engine docs archived under `archive/automation-paused-2026-09-09/docs-loop-engine/` (daemon retired in Task 167, docs moved in Task 177).
 
 ---
 
@@ -312,6 +317,7 @@ cp .env.example .env
 | `github`                  | GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.                                                                                                                                   |
 | `prompt-refactor`         | Meta-cognitive skill that refactors basic human prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.                                                                                          |
 | `bundle-tasks`            | Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Pure-MCP tool `bundle_tasks` (Task 110) — see `skill-templates/bundle-tasks/SKILL.md`. |
+| `blowsh`                  | Live-web research via the blowsh MCP server (Docker): `search_web`, `fetch_web`, `fetch_web_batch`, `crawl_web`, `extract_links` — rendered engines, JS rendering, sitemap-aware crawls. See `skill-templates/blowsh/SKILL.md`.            |
 | `task-generator`          | Automatically generates decentralized task files based on Manager instructions, with correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.                                                                                  |
 | `telegram-issue-sync`     | Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.                                                                                           |
 | `telegram-message-export` | Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.                                                                    |
@@ -405,7 +411,7 @@ Best if you want this codebase exploration tool available in _every_ terminal di
 
 _(Note: Replace `/Users/<YOUR_USER>` with your actual home directory path)._
 
-> Full HQ install (all 7 MCP servers — context, memory, lint, persona, decisions, blowsh, telegram — plus 32 skills and both agents) is documented in `LLM.txt` §4–§7 and the `global-install-upgrade` memory workflow, not here; the steps above cover only the standalone context server for third-party projects.
+> Full HQ install (all 7 MCP servers — context, memory, lint, persona, decisions, blowsh, telegram — plus 33 skills and both agents) is documented in `LLM.txt` §4–§7 and the `global-install-upgrade` memory workflow, not here; the steps above cover only the standalone context server for third-party projects.
 
 ### How It Works
 
@@ -428,7 +434,7 @@ _(Note: Replace `/Users/<YOUR_USER>` with your actual home directory path)._
 
 **Optional — auto-installed via `LLM.txt` Step 7.6:**
 
-- `blowsh` (Docker `ghcr.io/mokhtarabadi/blowsh-mcp:latest`, 4 tools) — **JS-capable browsing (retired browser MCP replacement).** `fetch_web` (plain/html/markdown/pdf + selector/max_chars/wait_ms), `search_web` (DuckDuckGo+Bing), `extract_links`, `fetch_web_batch` (10 URLs). SSRF guard, TTL cache. Timeout 120s. See https://github.com/mokhtarabadi/blowsh-mcp and `docs/telegram-setup.md` (setup maps to same global install).
+- `blowsh` (Docker `ghcr.io/mokhtarabadi/blowsh-mcp:latest`, 5 tools) — **JS-capable browsing (retired browser MCP replacement).** `fetch_web` (plain/html/markdown/pdf + selector/max_chars/wait_ms + focus/toc/must_contain/archive/stitch probes), `search_web` (DuckDuckGo+Bing+Brave+Mojeek consensus, intent verticals), `extract_links`, `fetch_web_batch` (10 URLs), `crawl_web` (sitemap-aware multi-page docs/API refs/wikis with focus/depth/char budgets). SSRF guard, TTL cache. Timeout 120s. See https://github.com/mokhtarabadi/blowsh-mcp, `skill-templates/blowsh/SKILL.md`, and `docs/telegram-setup.md` (setup maps to same global install).
 - `telegram` (Telethon, 80+ tools, `uv --directory $HOME/.config/opencode/mcp-telegram-server run main.py` over absolute path in opencode config dir) — Accounts (`list_accounts`, multi-account `account` param), chats/groups, messages (`send_message`/`reply_to_message` with `account="personal"`/`"work"`), contacts/aliases, media (`send_file`/`download_media`), events (`wait_for_settled_message`, `enable_incoming_feed`). File roots required for media tools (`/tmp/telegram-mcp` + `$HOME/.config/opencode/mcp-telegram-server/downloads`). Used by `skill-templates/telegram-issue-sync/SKILL.md` (supergroup → tasks) and `telegram-message-export/SKILL.md` (range → ZIP) — see `docs/telegram-setup.md` §6 for the full skill→tool→config table. Single vs work/personal setup documented there plus `LLM.txt` 7.6 (absolute paths, installed in `~/.config/opencode/`).
 
 ### Meta-Task Bundling — Pure MCP (No CLI Required)
@@ -520,13 +526,13 @@ OpenCode 1 reads `plugin` from **both** `opencode.json` (server/tools) and `tui.
 
 ## 📜 Release Milestones
 
-| Milestone | Key Architectural Evolutions |
-| --------- | ---------------------------- |
-| V5 | Decentralized `tasks/` architecture (retired `STATE.md`/`TODO.md`); Brain/Hands separation codified; `task-generator` + `audit-agents` skills introduced; Phase 0 UI/UX traversal for `DESIGN.md` generation. |
-| V6 | Kanban lifecycle (`backlog → in-progress → qa → completed → archive`); `commit_and_clean_task` MCP tool; `migrate-kanban` + `archive-tasks` skills; system prompt upgraded for Kanban state tracking. |
-| V6.7 | Manager profile and coaching fragments introduced (removed in V9.0.0; configuration moved to project-specific `AGENTS.md`). |
-| V7 | Multi-persona brainstorming protocol; Universal Datetime Rules (UTC-at-rest); SOLID programming mandate; Agent Skills Registry expanded to 31 skills. |
-| V8 | 9-step production line formalized; Immutable Financial Ledger mandate; Buffer Isolation validation phase; Defensive Shell Protocol. |
+| Milestone | Key Architectural Evolutions                                                                                                                                                                                  |
+| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
+| V5        | Decentralized `tasks/` architecture (retired `STATE.md`/`TODO.md`); Brain/Hands separation codified; `task-generator` + `audit-agents` skills introduced; Phase 0 UI/UX traversal for `DESIGN.md` generation. |
+| V6        | Kanban lifecycle (`backlog → in-progress → qa → completed → archive`); `commit_and_clean_task` MCP tool; `migrate-kanban` + `archive-tasks` skills; system prompt upgraded for Kanban state tracking.         |
+| V6.7      | Manager profile and coaching fragments introduced (removed in V9.0.0; configuration moved to project-specific `AGENTS.md`).                                                                                   |
+| V7        | Multi-persona brainstorming protocol; Universal Datetime Rules (UTC-at-rest); SOLID programming mandate; Agent Skills Registry expanded to 31 skills.                                                         |
+| V8        | 9-step production line formalized; Immutable Financial Ledger mandate; Buffer Isolation validation phase; Defensive Shell Protocol.                                                                           |
 
 ---
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 4540304..de99c57 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -51,23 +51,23 @@ You are the final gatekeeper of the Kanban task state. If the Orchestrator forge
 
 If the Orchestrator or Manager forgets to explicitly list a skill in the `<context_phase>`, you MUST scan the task context and auto-load the correct skill using the `skill` tool based on this matrix:
 
-| Detected Tech Stack / Context         | Mandatory Skill to Load         |
-| ------------------------------------- | ------------------------------- |
-| Jetpack Compose, Android, Kotlin      | `android-kotlin`                |
-| Flask, SQLAlchemy, Python             | `flask-python`                  |
-| Go, Gin, Hexagonal                    | `go-gin` or `go-hexagonal-grpc` |
-| SwiftUI, iOS                          | `ios-swiftui`                   |
-| NestJS, Prisma, TypeScript            | `nestjs-prisma-vertical`        |
-| Next.js, App Router, React            | `nextjs`                        |
-| FastAPI, Pydantic                     | `python-fastapi`                |
-| React Native, Expo                    | `react-native-expo`             |
-| React, Vite                           | `react-vite`                    |
-| Spring Boot, Java                     | `spring-boot`                   |
-| Vue, Nuxt                             | `vue-nuxt`                      |
-| Creating a new task file              | `task-generator`                |
-| Closing or archiving a task           | `archive-tasks`                 |
-| Complex bug, deadlock, silent failure | `debug-instrumentation`         |
-| Manager decision capture, ruling reuse | `manager-decision`             |
+| Detected Tech Stack / Context          | Mandatory Skill to Load                                                                                                                                                                      |
+| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
+| Jetpack Compose, Android, Kotlin       | `android-kotlin`                                                                                                                                                                             |
+| Flask, SQLAlchemy, Python              | `flask-python`                                                                                                                                                                               |
+| Go, Gin, Hexagonal                     | `go-gin` or `go-hexagonal-grpc`                                                                                                                                                              |
+| SwiftUI, iOS                           | `ios-swiftui`                                                                                                                                                                                |
+| NestJS, Prisma, TypeScript             | `nestjs-prisma-vertical`                                                                                                                                                                     |
+| Next.js, App Router, React             | `nextjs`                                                                                                                                                                                     |
+| FastAPI, Pydantic                      | `python-fastapi`                                                                                                                                                                             |
+| React Native, Expo                     | `react-native-expo`                                                                                                                                                                          |
+| React, Vite                            | `react-vite`                                                                                                                                                                                 |
+| Spring Boot, Java                      | `spring-boot`                                                                                                                                                                                |
+| Vue, Nuxt                              | `vue-nuxt`                                                                                                                                                                                   |
+| Creating a new task file               | `task-generator`                                                                                                                                                                             |
+| Closing or archiving a task            | `archive-tasks`                                                                                                                                                                              |
+| Complex bug, deadlock, silent failure  | `debug-instrumentation`                                                                                                                                                                      |
+| Manager decision capture, ruling reuse | `manager-decision` <!-- PAUSED-2026-09-09 (Task 177): manager_decisions server disabled in Task 176 — do NOT auto-load this skill until restore. Original row kept for future re-enable. --> |
 
 ## Direct Input (Ad-Hoc) Validation Protocol
 
diff --git a/archive/automation-paused-2026-09-09/RESTORE.md b/archive/automation-paused-2026-09-09/RESTORE.md
index acbd4bc..c8979b4 100644
--- a/archive/automation-paused-2026-09-09/RESTORE.md
+++ b/archive/automation-paused-2026-09-09/RESTORE.md
@@ -14,7 +14,7 @@ configs, and docs are preserved for future development.
   `git mv` from `.opencode/commands/`: `qa.md`, `reviewer.md`,
   `manager.md`, `brainstorm.md`, `architect.md`, `designer.md`,
   `programmer.md`, `planner.md`, `strategist.md`.
-- The automation *rules* stay in place but neutralized:
+- The automation _rules_ stay in place but neutralized:
   - `agents/cognitive-executor.md` — `## Persona Loop` +
     `### Decision Learning Loop` wrapped in
     `AUTOMATION-PAUSED-2026-09-09 ... AUTOMATION-RESUME` HTML comments;
@@ -48,7 +48,8 @@ replay cap, lineage fallback). See `tasks/completed/` for full records.
 4. Uncomment `PERSONA_*` / `DECISION_*` in `.env.example`; ensure live
    `.env` values exist.
 5. Re-run the global-install upgrade workflow, then `opencode mcp list`
-   must show persona + manager_decisions connected.
+   must show persona + manager_decisions connected. (Restore-time
+   expectation only — while paused, 5 connected by design.)
 6. Run the persona test suite green before re-enabling.
 
 ## Appendix A — exact removed JSON (Task 176, 2026-09-09)
diff --git a/docs/loop-engine/README.md b/archive/automation-paused-2026-09-09/docs-loop-engine/README.md
similarity index 100%
rename from docs/loop-engine/README.md
rename to archive/automation-paused-2026-09-09/docs-loop-engine/README.md
diff --git a/docs/loop-engine/configuration.md b/archive/automation-paused-2026-09-09/docs-loop-engine/configuration.md
similarity index 100%
rename from docs/loop-engine/configuration.md
rename to archive/automation-paused-2026-09-09/docs-loop-engine/configuration.md
diff --git a/docs/loop-engine/deployment.md b/archive/automation-paused-2026-09-09/docs-loop-engine/deployment.md
similarity index 100%
rename from docs/loop-engine/deployment.md
rename to archive/automation-paused-2026-09-09/docs-loop-engine/deployment.md
diff --git a/docs/loop-engine/multi-project.md b/archive/automation-paused-2026-09-09/docs-loop-engine/multi-project.md
similarity index 100%
rename from docs/loop-engine/multi-project.md
rename to archive/automation-paused-2026-09-09/docs-loop-engine/multi-project.md
diff --git a/docs/loop-engine/setup.md b/archive/automation-paused-2026-09-09/docs-loop-engine/setup.md
similarity index 100%
rename from docs/loop-engine/setup.md
rename to archive/automation-paused-2026-09-09/docs-loop-engine/setup.md
diff --git a/docs/system-prompt-modularization.md b/archive/automation-paused-2026-09-09/docs-superseded/system-prompt-modularization.md
similarity index 100%
rename from docs/system-prompt-modularization.md
rename to archive/automation-paused-2026-09-09/docs-superseded/system-prompt-modularization.md
diff --git a/docs/conventions.md b/docs/conventions.md
index e5a7952..03f0ba8 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -74,7 +74,7 @@ All projects in this ecosystem MUST treat source-of-truth contracts and shared s
 1. **No hand-authored duplicates** — Consumer applications (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) MUST NOT hand-author duplicate interface models, request/response DTOs, or data classes for types already governed by a contract.
 2. **Import or generate** — When a governed type is needed, either import it directly from the shared package (`@repo/shared-schema`, `packages/shared-schema`) or execute the stack's code-generation toolchain (`pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`).
 3. **SOLID reconciliation** — Single-source-of-truth prevents type drift (DRY/SRP) and does not conflict with YAGNI or the 3-Implementation Rule: extract or generate only when a contract or cross-service dependency already exists.
-4. **Deterministic enforcement** — `TypeDriftSentinel` (`loop-engine/sentinel.py`) scans task diffs during toolchain verification (pre-QA) and fails fast when a consumer path introduces a hand-written DTO while a governing contract pattern applies. Bypass with an explicit `drift-ignore` comment only when a justified exception exists.
+4. **Deterministic enforcement (historical — loop-engine retired):** the retired `loop-engine/sentinel.py` `TypeDriftSentinel` used to scan task diffs during toolchain verification (pre-QA). With the loop-engine daemon retired (Task 167; guides archived under `archive/automation-paused-2026-09-09/docs-loop-engine/`), enforcement is manual review until a replacement lands. Bypass with an explicit `drift-ignore` comment only when a justified exception exists.
 
 The single source of truth for the full mandate is `prompts/fragments/20-no_manual_dto_mandate.md` — this section is a summary only.
 
diff --git a/docs/setup.md b/docs/setup.md
index c270d7a..580f7c8 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -23,6 +23,7 @@ gh auth status
 ### Install (if missing)
 
 **Debian/Ubuntu:**
+
 ```bash
 (type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
 && sudo mkdir -p -m 755 /etc/apt/keyrings \
@@ -35,6 +36,7 @@ gh auth status
 ```
 
 **macOS:**
+
 ```bash
 brew install gh
 ```
@@ -49,14 +51,22 @@ gh auth login
 
 The project uses three FastMCP Python servers, all run via `uv`:
 
-| Server | Purpose | Start Command |
-|--------|---------|---------------|
+| Server               | Purpose                                           | Start Command                         |
+| -------------------- | ------------------------------------------------- | ------------------------------------- |
 | `mcp-context-server` | `.gitignore`-aware file reading, tree exploration | `uv run mcp-context-server/server.py` |
-| `mcp-lint-server` | Task file linting and Markdown validation | `uv run mcp-lint-server/server.py` |
-| `mcp-memory-server` | Persistent project memory bank | `uv run mcp-memory-server/server.py` |
+| `mcp-lint-server`    | Task file linting and Markdown validation         | `uv run mcp-lint-server/server.py`    |
+| `mcp-memory-server`  | Persistent project memory bank                    | `uv run mcp-memory-server/server.py`  |
 
 These are configured in `opencode.json` and auto-start with OpenCode.
 
+> **Automation-paused state (2026-09-09, Tasks 175/176):** the `persona`
+> and `manager_decisions` MCP servers are DISABLED (config blocks removed;
+> code kept under `mcp-persona-server/` + `mcp-decision-server/`), and the 9
+> automation slash commands are archived under
+> `archive/automation-paused-2026-09-09/commands/`. Global installs
+> additionally run `blowsh` + `telegram`. Restore path:
+> `archive/automation-paused-2026-09-09/RESTORE.md`.
+
 ## Development Tools
 
 ```bash
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index 591b0b9..2313ed0 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -223,24 +223,65 @@ def _extract_via_tree_sitter(file_path: Path) -> Optional[str]:
 
 # --- End tree-sitter ---
 
-def generate_tree(dir_path: Path, ignore_filter: GitIgnoreFilter) -> str:
+# Runaway-traversal guards (Task 177): a single wedged request (e.g. tree of
+# "/") used to burn minutes of CPU on the single-threaded stdio server and
+# starve every later tool call. These caps bound any single walk.
+TREE_MAX_DEPTH = 8
+TREE_MAX_ENTRIES = 2000
+COLLECT_MAX_FILES = 1000
+# Directory names never descended into, at any level. Supplements .gitignore
+# (which cannot cover absolute-path walks outside any repo).
+BANNED_DIRS = frozenset(
+    {".git", ".cache", "__pycache__", "node_modules", ".venv", "venv", "proc", "sys", "dev"}
+)
+
+def _is_banned_dir(entry: Path) -> bool:
+    """True when a directory entry must never be descended into."""
+    try:
+        return entry.is_dir() and entry.name in BANNED_DIRS
+    except OSError:
+        return True  # Unstatable entries are treated as unsafe to descend.
+
+def generate_tree(
+    dir_path: Path,
+    ignore_filter: GitIgnoreFilter,
+    max_depth: int = TREE_MAX_DEPTH,
+    max_entries: int = TREE_MAX_ENTRIES,
+) -> str:
     lines = ["```text", dir_path.name or str(dir_path)]
-    def _walk(current_path: Path, prefix: str) -> None:
+    state = {"count": 0, "truncated": False}
+    def _walk(current_path: Path, prefix: str, depth: int) -> None:
+        if state["truncated"]:
+            return
+        if depth > max_depth:
+            lines.append(f"{prefix}└── [Max depth reached ({max_depth})]")
+            return
         try:
             entries = list(current_path.iterdir())
-        except PermissionError:
-            lines.append(f"{prefix}└── [Permission Denied]")
+        except (PermissionError, OSError):
+            lines.append(f"{prefix}└── [Unreadable directory]")
             return
-        valid_entries = [e for e in entries if not ignore_filter.is_ignored(e)]
+        valid_entries = [
+            e
+            for e in entries
+            if not _is_banned_dir(e) and not ignore_filter.is_ignored(e)
+        ]
         sorted_entries = sorted(valid_entries, key=lambda e: (not e.is_dir(), e.name.lower()))
         for i, entry in enumerate(sorted_entries):
+            if state["count"] >= max_entries:
+                lines.append(
+                    f"{prefix}└── [Truncated: entry limit reached ({max_entries})]"
+                )
+                state["truncated"] = True
+                return
+            state["count"] += 1
             is_last = i == (len(sorted_entries) - 1)
             connector = "└── " if is_last else "├── "
             lines.append(f"{prefix}{connector}{entry.name}")
             if entry.is_dir():
                 extension = "    " if is_last else "│   "
-                _walk(entry, prefix + extension)
-    _walk(dir_path, "")
+                _walk(entry, prefix + extension, depth + 1)
+    _walk(dir_path, "", 0)
     lines.append("```")
     return "\n".join(lines)
 
@@ -285,7 +326,11 @@ def process_source_file(file_path: Path, max_size: int, line_numbers: bool) -> s
     lines.append("```\n")
     return "\n".join(lines)
 
-def collect_files(target: str, ignore_filter: GitIgnoreFilter) -> list[Path]:
+def collect_files(
+    target: str,
+    ignore_filter: GitIgnoreFilter,
+    max_files: int = COLLECT_MAX_FILES,
+) -> list[Path]:
     p = Path(target)
     if not p.exists() or ignore_filter.is_ignored(p):
         return []
@@ -294,8 +339,15 @@ def collect_files(target: str, ignore_filter: GitIgnoreFilter) -> list[Path]:
     collected = []
     for root, dirs, files in os.walk(p):
         root_path = Path(root)
-        dirs[:] = [d for d in dirs if not ignore_filter.is_ignored(root_path / d)]
+        dirs[:] = [
+            d
+            for d in dirs
+            if (root_path / d).name not in BANNED_DIRS
+            and not ignore_filter.is_ignored(root_path / d)
+        ]
         for f in files:
+            if len(collected) >= max_files:
+                return collected
             file_path = root_path / f
             if not ignore_filter.is_ignored(file_path):
                 collected.append(file_path)
@@ -322,6 +374,17 @@ mcp = FastMCP("CustomContext")
 @mcp.tool()
 def get_directory_tree(target_path: str = ".") -> str:
     """Generates an ASCII tree representation of the directory, respecting .gitignore. Use this to discover codebase structure."""
+    # Security: mirror create_tree_report — coerce bad types, resolve against
+    # the workspace root, reject escapes. Previously a bare "/" walked the
+    # whole filesystem and wedged the single-threaded server (Task 177).
+    if not isinstance(target_path, str):
+        target_path = "."
+    workspace_root = Path.cwd().resolve()
+    tree_path = Path(target_path).resolve()
+    try:
+        tree_path.relative_to(workspace_root)
+    except ValueError:
+        return "Error: Path traversal detected. target_path must be within the project workspace."
     ignore_filter = GitIgnoreFilter()
     tree_path = Path(target_path)
     if not tree_path.is_dir():
@@ -350,10 +413,21 @@ def read_source_files(paths: list[str], max_size: int = 1048576, no_line_numbers
     if not files_to_process:
         return "No files found or all files were ignored."
 
+    started = time.monotonic()
     output_lines = ["## Source Files\n"]
     include_line_numbers = not no_line_numbers
+    skipped = 0
+    total_bytes = 0
     for _, f in sorted(files_to_process.items(), key=lambda item: str(item[1]).lower()):
-        output_lines.append(process_source_file(f, max_size, include_line_numbers))
+        try:
+            total_bytes += f.stat().st_size
+        except OSError:
+            pass
+        rendered = process_source_file(f, max_size, include_line_numbers)
+        if "> Skipped:" in rendered:
+            skipped += 1
+        output_lines.append(rendered)
+    duration_s = time.monotonic() - started
 
     result_content = "\n".join(output_lines)
 
@@ -376,6 +450,9 @@ def read_source_files(paths: list[str], max_size: int = 1048576, no_line_numbers
 
     return (
         f"✅ Success: Compiled context for {len(files_to_process)} files.\n"
+        f"📊 Report metrics: {len(files_to_process) - skipped} processed, "
+        f"{skipped} skipped, {total_bytes} bytes read in {duration_s:.2f}s "
+        f"(tree depth cap {TREE_MAX_DEPTH}, collect cap {COLLECT_MAX_FILES}).\n"
         f"📁 Generated Report: `{report_file}`\n\n"
         f"Manager: You can now open `{report_file}` in your local editor to view the codebase context or copy/paste it directly for the AI."
     )
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 36a16cb..96aae70 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.10.0</system_version>
+<system_version>9.12.0</system_version>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index b70123b..877d22d 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -21,6 +21,8 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **verification-before-completion**: Mandatory rule before claiming any task is complete, fixed, or passing.
 - **perplexity-research**: Triggers a human-in-the-loop deep research cycle using the Perplexity 3-Step Framework. Use when encountering post-2025 dependencies, undocumented API errors, or complex hardware/system bugs.
 - **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
+- **brainstorm-swarm**: Orchestrates a multi-expert brainstorming session using six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) to resolve cross-disciplinary ambiguity. Outputs structured XML-tagged session reports.
+- **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
diff --git a/skill-templates/blowsh/SKILL.md b/skill-templates/blowsh/SKILL.md
new file mode 100644
index 0000000..561a58d
--- /dev/null
+++ b/skill-templates/blowsh/SKILL.md
@@ -0,0 +1,88 @@
+---
+name: blowsh
+description: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
+---
+
+# Blowsh Web Tooling
+
+All live-web work goes through the `blowsh` MCP server (Docker transport:
+`docker run --rm -i ghcr.io/mokhtarabadi/blowsh-mcp:latest`). Never shell
+out to `curl`/`wget` for page content — the server handles JS rendering,
+encoding, and SSRF guards.
+
+## The 5 Tools (pick the cheapest that answers the question)
+
+### 1. `blowsh_search_web` — discover pages
+
+Rendered search engines (DuckDuckGo, Bing, Brave, Mojeek) fused by
+cross-engine consensus. Returns ranked title/url/snippet results.
+
+- `query` (required), `max_results` (1–30, default 10), `page` (1–10)
+- `intent`: `auto` | `web` | `code` (adds GitHub vertical) | `paper`
+  (arXiv) | `news` (HN) | `entity` (Wikipedia)
+- `query_variants`: up to 2 alternate formulations, searched in parallel
+- `deadline_ms` (500–600000 hard budget), `enrich` (replace top-3
+  snippets with fetched markdown, best-effort)
+
+### 2. `blowsh_fetch_web` — read one page
+
+Full JS-rendered fetch as plain text, HTML, Markdown, or PDF-extracted
+text (`type: "pdf"` downloads directly, SSRF-guarded, 20MB cap).
+
+- `url` + `type` (required); `selector` (CSS, extract one element);
+  `max_chars` cap; `wait_ms` JS-settle polling budget
+- Token savers: `focus` (BM25 relevance filter, cuts 50–80%), `toc`
+  (heading outline only — then target with `section`), `links: false` /
+  `media: false` (~30% cheaper each)
+- `must_contain`: probe mode, returns MATCH/NO-MATCH + excerpts without
+  loading full content into context
+- `archive`: `auto` (Wayback resurrection on 404/paywall) | `only` |
+  `off`; `stitch`: follow `rel=next` (up to 6 parts, same-host)
+- `tier`: `auto` (HTTP first, escalates to browser) | `1` (HTTP only) |
+  `2` (browser directly); `offset`: resume from a prior `next_offset`
+- `deadline_ms` hard budget; `since_last`: one-line verdict when unchanged
+
+### 3. `blowsh_fetch_web_batch` — read up to 10 pages at once
+
+Same output shapes as fetch; reuses the render cache. One failing URL
+does not fail the batch.
+
+- `urls` (1–10, required); `type`, `max_chars`, `selector`, `wait_ms`
+  applied to each page
+
+### 4. `blowsh_crawl_web` — multi-page extraction (docs, API refs, wikis)
+
+Two-phase: sitemap discovery (cheap URL inventory) first, then
+focus-ranked fetching with adaptive per-host pacing.
+
+- `url` seed (required); `mode`: `full` (map + content, default) |
+  `map` (URL inventory only, very cheap) | `content` (BFS, no sitemap)
+- Budgets: `focus` (BM25 query — crawls only matching pages),
+  `max_pages` (cap 200), `max_total_chars` (4000–500000),
+  `deadline_s` (5–600); `resume` token continues across calls
+- `max_depth` (default 2, 0 = seed only), `per_page_max`,
+  `include_paths` / `exclude_paths` globs, `same_host` (default true),
+  `respect_robots` (default true), `since_last` (delta crawl)
+- Stop reasons: FrontierEmpty (done) | MaxPages | CharBudget |
+  DepthLimit | Deadline | ThrottledOut | Cancelled
+
+### 5. `blowsh_extract_links` — navigation without the DOM
+
+Returns hyperlinks (text + absolute URL) of a JS-rendered page. Use to
+follow site navigation without fetching full content.
+
+- `url` (required), `limit` (1–200, default 50)
+
+## Rules
+
+1. **Single page → `fetch_web`.** Finding sites → `search_web`.
+   Multi-page docs → `crawl_web` (`map` first when scoping). Link
+   following → `extract_links`.
+2. **Probe before guzzling:** `must_contain`, `toc`, or `map` mode
+   first; fetch full bodies only for pages that matter.
+3. **Batch independent fetches** (up to 10) in one `fetch_web_batch`
+   call instead of serial fetches.
+4. **Respect budgets:** set `deadline_ms`/`deadline_s` on every call in
+   agent loops; a `Deadline` stop is an honest signal, not a failure.
+5. **SSRF scope:** PDF fetch and crawling are server-guarded; never
+   route `file://` or internal-host URLs through these tools.
diff --git a/skill-templates/manager-decision/SKILL.md b/skill-templates/manager-decision/SKILL.md
index 8285894..93e5e4f 100644
--- a/skill-templates/manager-decision/SKILL.md
+++ b/skill-templates/manager-decision/SKILL.md
@@ -5,6 +5,8 @@ description: Capture per-session manager decisions into a separate learning repo
 
 # Manager-Decision Skill
 
+> **PAUSED-2026-09-09 (Tasks 175/176/177):** the `manager_decisions` MCP server is DISABLED (blocks removed from repo + global `opencode.json`). This skill is inert until restore — do not invoke its tools; re-ask the human manager directly. Restore path: `archive/automation-paused-2026-09-09/RESTORE.md`.
+
 ## Purpose
 
 Turns each session's manager judgment into training data. Whenever the manager makes a trade-off, ruling, or system-design call, this skill extracts it (verbatim quote + structured decision), redacts secrets, and persists it append-only in the decision store (`.opencode/decisions/` of the current project — every project keeps its OWN manager notes — or any checkout pointed to by `DECISION_REPO_PATH`). Aggregated decisions evolve `samples/manager_profile.md` — the manager-AI sample — one reviewed promotion at a time, until micro-decisions no longer need the real manager.
diff --git a/skill-templates/versioning-and-release/SKILL.md b/skill-templates/versioning-and-release/SKILL.md
index bd3f9b0..c476b9c 100644
--- a/skill-templates/versioning-and-release/SKILL.md
+++ b/skill-templates/versioning-and-release/SKILL.md
@@ -56,7 +56,7 @@ All git commit messages MUST use lowercase prefixes followed by a colon and a sp
 
 ### Phase 1: Pre-Commit Quality Checks
 
-1. Before completing any task, ensure the local test suite and type-checkers have passed successfully (maximum of 3 consecutive repair attempts as per V5.3.0 strict guardrails).
+1. Before completing any task, ensure the local test suite and type-checkers have passed successfully (maximum of 3 consecutive repair attempts per strict guardrails).
 2. Ensure `AGENTS.md` and `DESIGN.md` conventions are fully respected.
 3. **Pre-Commit Verification Gate (Environment Verification, DevOps/Infra tasks only):** If the task involves deployment, Docker, CI/CD, or infrastructure changes, run ALL environment-specific verification commands (e.g., `docker login`, token scope validation, registry access checks) BEFORE proceeding to staging. If ANY check fails, HALT and output a failure report. Do NOT stage partial work.
 
diff --git a/system-prompt.md b/system-prompt.md
index fa1094c..11bcde8 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.10.0</system_version>
+<system_version>9.12.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -130,6 +130,8 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **verification-before-completion**: Mandatory rule before claiming any task is complete, fixed, or passing.
 - **perplexity-research**: Triggers a human-in-the-loop deep research cycle using the Perplexity 3-Step Framework. Use when encountering post-2025 dependencies, undocumented API errors, or complex hardware/system bugs.
 - **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
+- **brainstorm-swarm**: Orchestrates a multi-expert brainstorming session using six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) to resolve cross-disciplinary ambiguity. Outputs structured XML-tagged session reports.
+- **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
diff --git a/tests/test_mcp_servers.py b/tests/test_mcp_servers.py
index 3762b43..b685986 100644
--- a/tests/test_mcp_servers.py
+++ b/tests/test_mcp_servers.py
@@ -2118,3 +2118,164 @@ def test_memory_server_rebuild_tool():
             assert "Alpha" in content
         finally:
             os.chdir(old_cwd)
+
+
+# --- Task 177: traversal-guard + runaway-cap regression tests ---
+
+def _load_context_server_hardening():
+    """Load mcp-context-server fresh for the hardening tests."""
+    import importlib
+    from pathlib import Path
+
+    repo_root = Path(__file__).parent.parent
+    server_path = repo_root / "mcp-context-server" / "server.py"
+    spec = importlib.util.spec_from_file_location(
+        "context_server_hardening", server_path
+    )
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+    return mod
+
+
+def test_tree_rejects_absolute_escape():
+    """get_directory_tree('/') must refuse instead of walking the filesystem."""
+    import os
+    import tempfile
+    from pathlib import Path
+
+    mod = _load_context_server_hardening()
+    with tempfile.TemporaryDirectory() as tmpdir:
+        old_cwd = os.getcwd()
+        os.chdir(tmpdir)
+        try:
+            result = mod.get_directory_tree("/")
+            assert result.startswith("Error: Path traversal detected"), result[:120]
+        finally:
+            os.chdir(old_cwd)
+
+
+def test_tree_rejects_parent_escape():
+    """get_directory_tree('..') escapes the workspace root and must be refused."""
+    import os
+    import tempfile
+
+    mod = _load_context_server_hardening()
+    with tempfile.TemporaryDirectory() as tmpdir:
+        old_cwd = os.getcwd()
+        os.chdir(tmpdir)
+        try:
+            result = mod.get_directory_tree("..")
+            assert result.startswith("Error: Path traversal detected"), result[:120]
+        finally:
+            os.chdir(old_cwd)
+
+
+def test_tree_none_defaults_to_workspace_root():
+    """Non-string target degrades gracefully to the whole-project default."""
+    import os
+    import tempfile
+    from pathlib import Path
+
+    mod = _load_context_server_hardening()
+    with tempfile.TemporaryDirectory() as tmpdir:
+        (Path(tmpdir) / "probe.txt").write_text("x", encoding="utf-8")
+        old_cwd = os.getcwd()
+        os.chdir(tmpdir)
+        try:
+            result = mod.get_directory_tree(None)
+            assert result.startswith("## Directory Tree:"), result[:120]
+            assert "probe.txt" in result
+        finally:
+            os.chdir(old_cwd)
+
+
+def test_tree_depth_cap():
+    """generate_tree stops descending past max_depth with a marker line."""
+    import tempfile
+    from pathlib import Path
+
+    mod = _load_context_server_hardening()
+    with tempfile.TemporaryDirectory() as tmpdir:
+        deep = Path(tmpdir)
+        for i in range(6):
+            deep = deep / f"lvl{i}"
+            deep.mkdir()
+        (deep / "bottom.txt").write_text("x", encoding="utf-8")
+        out = mod.generate_tree(
+            Path(tmpdir), mod.GitIgnoreFilter(), max_depth=3
+        )
+        assert "[Max depth reached (3)]" in out
+        assert "bottom.txt" not in out
+
+
+def test_tree_entry_cap_and_banned_dirs():
+    """Entry cap truncates; BANNED_DIRS never appear in tree output."""
+    import tempfile
+    from pathlib import Path
+
+    mod = _load_context_server_hardening()
+    with tempfile.TemporaryDirectory() as tmpdir:
+        root = Path(tmpdir)
+        for i in range(10):
+            (root / f"file{i:02d}.txt").write_text("x", encoding="utf-8")
+        banned = root / "__pycache__"
+        banned.mkdir()
+        (banned / "cached.pyc").write_text("x", encoding="utf-8")
+        modules = root / "node_modules"
+        modules.mkdir()
+        (modules / "dep.js").write_text("x", encoding="utf-8")
+        out = mod.generate_tree(
+            root, mod.GitIgnoreFilter(), max_entries=5
+        )
+        assert "[Truncated: entry limit reached (5)]" in out
+        assert "__pycache__" not in out
+        assert "node_modules" not in out
+        assert "cached.pyc" not in out
+
+
+def test_collect_files_cap_and_banned_dirs():
+    """collect_files caps at max_files and never descends into BANNED_DIRS."""
+    import tempfile
+    from pathlib import Path
+
+    mod = _load_context_server_hardening()
+    with tempfile.TemporaryDirectory() as tmpdir:
+        root = Path(tmpdir)
+        for i in range(5):
+            (root / f"f{i}.txt").write_text("x", encoding="utf-8")
+        venv = root / ".venv"
+        venv.mkdir()
+        (venv / "lib.py").write_text("x", encoding="utf-8")
+        got = mod.collect_files(str(root), mod.GitIgnoreFilter(), max_files=2)
+        assert len(got) == 2
+        full = mod.collect_files(str(root), mod.GitIgnoreFilter())
+        assert not any(".venv" in str(p) for p in full)
+        assert len(full) == 5
+
+
+def test_read_source_files_prepends_metrics():
+    """Report return carries processed/skipped/bytes/duration metrics."""
+    import os
+    import shutil
+    import tempfile
+    from pathlib import Path
+
+    mod = _load_context_server_hardening()
+    with tempfile.TemporaryDirectory() as tmpdir:
+        root = Path(tmpdir)
+        (root / "a.txt").write_text("hello", encoding="utf-8")
+        (root / "b.txt").write_text("world", encoding="utf-8")
+        (root / "big.txt").write_text("x" * 100, encoding="utf-8")
+        old_cwd = os.getcwd()
+        os.chdir(root)
+        try:
+            result = mod.read_source_files(
+                ["a.txt", "b.txt", "big.txt"], max_size=10
+            )
+            assert "📊 Report metrics:" in result, result[:300]
+            assert "2 processed" in result, result[:300]
+            assert "1 skipped" in result, result[:300]
+            assert "bytes read in" in result, result[:300]
+        finally:
+            os.chdir(old_cwd)
+            shutil.rmtree(root / "context-reports", ignore_errors=True)
```
<!-- END_GIT_DIFF -->
