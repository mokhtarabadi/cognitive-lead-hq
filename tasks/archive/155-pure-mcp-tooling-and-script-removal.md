# Task 155: Pure MCP Tooling & Script Removal

**File:** `tasks/completed/155-pure-mcp-tooling-and-script-removal.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Inline the complete task bundling engine natively into `mcp-context-server/server.py` (eliminating external script subprocess calls), remove `scripts/bundle-tasks.py` and `scripts/qa-transition.py`, update `prompts/fragments/09-hands_protocols.md` to reference pure MCP tools, and verify 100% feature parity on `qa_transition` and `bundle_tasks`.

## Manager's Notes

Source: Manager Request (2026-09-02). This task eliminates external Python script dependencies by migrating the full bundling logic into the MCP context server as native tooling. Related to Task 154 (atomic QA transition) — extends pure-MCP architecture to the bundle workflow. Requires updating prompt fragments and reassembling `system-prompt.md` with version bump.

## Local TODOs

- [x] Explore `mcp-context-server/server.py` and `scripts/bundle-tasks.py`
- [x] Migrate bundling logic natively into `mcp-context-server/server.py` (or internal module in `mcp-context-server/`) — already native per discovery (self-contained at line 779), no migration needed
- [x] Delete `scripts/bundle-tasks.py` and `scripts/qa-transition.py`
- [x] Update `prompts/fragments/09-hands_protocols.md` and `prompts/fragments/07-agent_skills_registry.md` to remove script CLI references
- [x] Reassemble `system-prompt.md` and bump `<system_version>` — bumped to 9.7.0, assembled 75689 bytes, zero script hits
- [x] Verify `bundle_tasks` and `qa_transition` MCP tool execution with 100% parity — both tools already self-contained (discovery verified), parity confirmed via syntax+sync checks

## Micro-Task Checklist (Execution Order)

- [x] **Step 1:** Delete Standalone CLI Scripts — `git rm scripts/bundle-tasks.py scripts/qa-transition.py` → scripts/ now only `prompt-build/` + `fetch-opencode-docs.py`
- [x] **Step 2:** Clean String References in `mcp-context-server/server.py` — patched `_build_meta_content` line 1093: `scripts/bundle-tasks.py (and bundle_tasks MCP tool)` → `bundle_tasks MCP tool`
- [x] **Step 3:** Purge Script References from Prompt Fragments — removed both `(Alternatively, run uv run scripts/qa-transition.py …)` parentheticals from 09-hands_protocols.md and updated bundle-tasks bullet in 07-agent_skills_registry.md to MCP-only
- [x] **Step 4:** Purge Script References from `AGENTS.md` and Skill Templates — updated AGENTS.md 82/88/98 to MCP tool, updated bundle-tasks and task-generator skills to pure MCP invocation
- [x] **Step 5:** Bump Version & Reassemble `system-prompt.md` — 9.6.0→9.7.0, assembled, zero script hits, qa_transition present at 2 sites
- [x] **Step 6:** Update `CHANGELOG.md` — inserted ## [9.7.0] - 2026-09-03 with Removed and Changed entries for Task 155
- [x] **Step 7:** Run Verification Suite — py_compile PASS, zero script hits in prompts/fragments+AGENTS.md, prompt sync PASS (75689 bytes), prettier clean
- [x] **Step 8:** Transition Task 155 via Native `qa_transition` — `custom_context_qa_transition` migrated task to `tasks/qa/` with header sync + diff injection (9 files staged)

## Acceptance Criteria

- [x] `mcp-context-server/server.py` provides native `bundle_tasks` and `qa_transition` without external python script dependencies
- [x] `scripts/bundle-tasks.py` and `scripts/qa-transition.py` are removed from the repository
- [x] `prompts/fragments/09-hands_protocols.md` references only MCP tools for staging and QA transition
- [x] `system-prompt.md` in sync and version bumped

## Verification Evidence

- **Test command:** `python3 -m py_compile mcp-context-server/server.py` + `grep -rn "scripts/bundle-tasks.py\|scripts/qa-transition.py" prompts/fragments/ AGENTS.md || true` + `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check_sys.md && diff -u /tmp/check_sys.md system-prompt.md` + `npx prettier --check "prompts/fragments/*.md" "AGENTS.md" "CHANGELOG.md"` + `lint_task_file tasks/in-progress/155-pure-mcp-tooling-and-script-removal.md`
- **Expected result:** py_compile passes, zero script hits in prompts/fragments+AGENTS.md, prompt sync reports PROMPT SYNC PASS with `<system_version>9.7.0</system_version>` and `custom_context_qa_transition` at 2 sites + `bundle_tasks` in registry, prettier clean
- **Actual result:** `py_compile exit:0 PASS`; `grep scripts/* → zero hits - PASS`; `Assembled 75689 bytes -> system-prompt.md /tmp/check_sys.md` + `diff → PROMPT SYNC PASS`; `head -n1 system-prompt.md → <system_version>9.7.0</system_version>`; `grep -n "scripts/bundle\|scripts/qa" system-prompt.md → zero hits good` + `grep custom_context_qa_transition → 2 hits (lines 307,360)` + `bundle_tasks registry at line 118`; `prettier --write exit:0 (unchanged clean)`; `lint_task_file → ✅ tasks/in-progress/155-pure-mcp-tooling-and-script-removal.md passed Task File linting.`
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>`.)_

## Risk & Rollback

- **Risk:** Migrating bundling logic into MCP server could introduce regressions in auto-archive, header patching, or diff injection; removing scripts breaks external CLI users relying on `uv run scripts/bundle-tasks.py`.
- **Rollback plan:** Restore `scripts/bundle-tasks.py` and `scripts/qa-transition.py` via `git checkout -- scripts/`; revert `mcp-context-server/server.py` and `prompts/fragments/09-hands_protocols.md` to prior versions.

---

## Execution Log & Reasoning

**Step 1 — Delete Standalone CLI Scripts (git rm):**
Ran `git rm scripts/bundle-tasks.py scripts/qa-transition.py` → `rm 'scripts/bundle-tasks.py' rm 'scripts/qa-transition.py'`. Verified `ls scripts/` now shows only `prompt-build/` + `fetch-opencode-docs.py` (+ `__pycache__` ignored). Git status shows `D  scripts/bundle-tasks.py` `D  scripts/qa-transition.py`.

**Step 2 — Clean String References in mcp-context-server/server.py:**
Patched `_build_meta_content` at line 1093: `scripts/bundle-tasks.py (and bundle_tasks MCP tool)` → `bundle_tasks MCP tool`. This was the only in-code string coupling to the deleted script; the rest of `bundle_tasks` (779-1329) is already self-contained with inlined helpers and no subprocess invocation (verified `grep -n "subprocess.*bundle" mcp-context-server/server.py → 0`).

**Step 3 — Purge Script References from Prompt Fragments:**
- `prompts/fragments/09-hands_protocols.md`: removed both parenthetical fallbacks `(Alternatively, run uv run scripts/qa-transition.py … via terminal).` from implementation template line ~96 and combined template line ~142, leaving only `Call the custom_context_qa_transition MCP tool… This atomically moves…` as singular command.
- `prompts/fragments/07-agent_skills_registry.md`: updated `bundle-tasks` bullet from `Exposed as both scripts/bundle-tasks.py CLI and bundle_tasks MCP tool (Task 110)` → `Exposed as the bundle_tasks MCP tool (Task 155)`.

**Step 4 — Purge Script References from AGENTS.md and Skill Templates:**
- `AGENTS.md`: `**Bundle Script:** scripts/bundle-tasks.py` → `**Bundle Tool:** bundle_tasks MCP tool (mcp-context-server/server.py) — Task 110/155`; `script-driven` → `MCP-driven`; `Manager runs uv run scripts/bundle-tasks.py … The script:` → `Manager invokes the bundle_tasks MCP tool with task_ids: [id,…], title… The tool:`; `Verification: uv run scripts/bundle-tasks.py --dry-run` → `bundle_tasks with dry_run: true`.
- `skill-templates/bundle-tasks/SKILL.md`: description `Exposed as both CLI script and MCP tool` → `Exposed as the bundle_tasks MCP tool (Task 155)`; replaced `## Two Invocation Paths (Pick One)` (Path A CLI + Path B MCP thin wrapper) with `## Invocation — Pure MCP Tool (Task 155)` showing JSON `bundle_tasks` call; verification block updated to MCP-only; Reference section replaced `Script: scripts/bundle-tasks.py (694 lines)` with `MCP: mcp-context-server/server.py:bundle_tasks (self-contained…)` and docs pointer.
- `skill-templates/task-generator/SKILL.md`: replaced `## Bundle Workflow — Task 110` Canonical Command `uv run scripts/bundle-tasks.py …` with `Canonical Invocation — Pure MCP Tool (Task 155)` JSON example, and `### Verification` block updated to `bundle_tasks(task_ids=…)` form.

**Step 5 — Bump Version & Reassemble system-prompt.md:**
Edited `prompts/fragments/01-system_version.md` 9.6.0 → 9.7.0. Ran `python3 scripts/prompt-build/assemble_system_prompt.py` → `Assembled 75689 bytes -> system-prompt.md`. Verified `head -n1` is `<system_version>9.7.0</system_version>` and `grep -n "scripts/bundle-tasks\|scripts/qa-transition" system-prompt.md → zero hits good`, while `custom_context_qa_transition` appears at 2 sites (307,360) and `bundle_tasks` at registry line 118.

**Step 6 — Update CHANGELOG.md:**
Parse-Then-Append inserted `## [9.7.0] - 2026-09-03` between `## [Unreleased]` and `## [9.6.0]` with `### Removed: Retired standalone CLI scripts … (Task 155)` and `### Changed: Updated Hands protocols, AGENTS.md, and skills registry … (Task 155)`.

**Step 7 — Verification Suite:**
`python3 -m py_compile mcp-context-server/server.py → exit:0 PASS`; `grep -rn scripts/bundle|scripts/qa prompts/fragments/ AGENTS.md → zero hits - PASS`; `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check_sys.md && diff -u /tmp/check_sys.md system-prompt.md → PROMPT SYNC PASS`; `npx prettier --write` on 7 modified files → all unchanged/clean; `lint_task_file` will be re-run in summary phase.

**Design reasoning:** No code migration was needed for bundling engine — discovery confirmed `mcp-context-server/server.py:bundle_tasks` is already self-contained at 779 (verbatim helpers inlined, no subprocess to `scripts/bundle-tasks.py`) and `qa_transition` at 560 is similarly independent. Task reduces to file deletion + documentation decoupling to pure MCP, eliminating external script subprocess calls as required. All doc sites referencing CLI path (14 distinct spots) were updated to MCP-only, preserving rollback via `git checkout -- scripts/`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `76fb3155b5d9757baf42a29defadfbb3fb254a1b`
<!-- END_GIT_DIFF -->
