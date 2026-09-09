# Task 177: Comprehensive audit cleanup, MCP server hardening, and blowsh skill integration

**File:** `tasks/completed/177-audit-cleanup-and-self-improve-system.md`
**Source:** manager
**Type:** improvement
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `cce1d5ec9394f1acf6ccf696aca2466650c3cf5f`
<!-- END_GIT_DIFF -->
