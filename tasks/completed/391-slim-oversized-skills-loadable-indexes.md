# Task 391: Split oversized skills into loadable indexes

**File:** `tasks/completed/391-slim-oversized-skills-loadable-indexes.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Submitted:** 2026-11-09T07:42:52Z
**Finished:** 2026-11-09T08:42:18Z
**Estimate:** 2h
**Milestone:** M01

## Goal

Make every HQ skill loadable again: split the three oversized meta skills into a small index plus verbatim `templates/` parts, fold `opencode-init` into `governance`, and clear the stale references that change left behind.

## Manager's Notes

Root cause of the empty `Load Skill` result: `governance/SKILL.md` was 43,572 bytes and `kanban-lifecycle`/`telegram-suite` were 27,717/30,013 bytes. OpenCode advertises only ID/name/description and loads the body on demand; oversized bodies returned empty, and global smart-compact discards `skill` output to a notice, so the failure looked silent. Skills must stay small, with detail in sibling files read on demand.

## Local TODOs

- [x] Governance slimmed to an index; `audit.md`, `init.md` hold the verbatim bodies
- [x] `opencode-init` merged as `governance/templates/init.md` Part 3; standalone skill removed
- [x] Kanban + Telegram slimmed to indexes with part files
- [x] Registry, README, LLM.txt, and roadmap references match the 24-skill reality
- [x] Bundle CLI claim removed (script does not exist)
- [x] All 24 skills pass loader preconditions
- [x] Global install synced

## Acceptance Criteria

- [x] `governance`, `kanban-lifecycle`, `telegram-suite` `SKILL.md` are each under 3 KB and every body section survives verbatim in `templates/`
- [x] `skill-templates/opencode-init/` is gone; its validator, golden config, and runtime matrix live under `governance/templates/opencode-init/`
- [x] `07-agent_skills_registry.md` lists exactly the 24 on-disk skills and advertises `governance` for audit + slice docs + project `opencode.json`
- [x] Every skill has frontmatter `name` matching its directory and a non-empty description under 1024 chars
- [x] `LLM.txt` reports 24 skills, excludes `DECISIONS.md`/`README.md` from the global copy, and no longer offers a `bundle-tasks.py` CLI
- [x] `README.md` roadmap references `kanban-lifecycle` and `testing-verification`, not deleted skills
- [x] `test_prompt_sync.py` + `test_skill_registry.py` pass and `system-prompt.md` is in sync at 9.88.0
- [x] Global `~/.config/opencode/skills/` holds the same 24 skills plus the template parts

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest pytest tests/test_prompt_sync.py tests/test_skill_registry.py -q`
- **Expected result:** 65 passed, exit 0
- **Actual result:** 65 passed in 2.88s (SUMMARY)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by that evidence — do NOT defer box-checking to a closure task.

## Risk & Rollback

- **Risk:** A split can silently drop body text, or leave a test asserting a deleted path.
- **Rollback plan:** `git checkout -- skill-templates/ prompts/ LLM.txt README.md AGENTS.md tests/ system-prompt.md`; the global copy is rebuilt by re-running the sync step.

## Execution Log & Reasoning

**Implementation (this session, before the task file existed):** Merged the three metas into index + `templates/` split. `governance/SKILL.md` 43,572 → 2,114 bytes with `templates/audit.md` (40,735) and `templates/init.md` (2,335). Kanban 27,717 → 1,991 across five part files; Telegram 30,013 → 1,947 across three. Folded `opencode-init` into `governance/templates/init.md` Part 3 and moved `references/` + `scripts/validate-opencode.py` under `governance/templates/opencode-init/`, then deleted the standalone skill. Registry, version (9.87.0 → 9.88.0), and prompt were regenerated.

**Audit findings fixed:** `skill-templates/README.md` still advertised 25 templates and the old `opencode-init/` path; `README.md` roadmap pointed at `task-generator` and `testing-strategy`; `LLM.txt` offered a `bundle-tasks.py` CLI that does not exist. Test helpers were widened to read `SKILL.md` plus `templates/*.md` so the slim contracts still assert the same terms.

**Loader check:** all 24 skills have frontmatter, a `name` matching the directory, and a description under 1024 chars. The three formerly-oversized skills are now 2,263 / 1,991 / 1,947 bytes.

**Preservation proof (git HEAD vs new tree):** governance 43,221 → 47,332 bytes across index + `audit.md` + `init.md`, with `SCOPE CONFINEMENT`, `Target Audit Criteria`, `Deprecated Sections Resolution`, Mode 1, Mode 2, `Slice Discovery`, and `Inject Code Pointers` all still present. Kanban 27,574 → 29,032 with `NEXT_ID`, `Collision Check`, `Bundle Workflow`, `Archive Tasks`, `Migrate Kanban`, `Stale Memory Report` intact. Telegram 29,898 → 31,335 with `parse_mode`, `3800`, `U+200C`, `telegram_get_history`, `RAW_TEXT`, `sync_registry` intact. Totals grew because indexes were added on top of the verbatim bodies.

**Repo-wide audit closed:** `skill-templates/README.md` (25 → 24 templates, `opencode-init/` path corrected), `README.md` roadmap (`task-generator` → `kanban-lifecycle`, `testing-strategy` path → `testing-verification`), `LLM.txt` §6.1 (`bundle-tasks.py` CLI does not ship — MCP tool only). `docs/workflow-upgrade-v8.4.5.md` and the README version table stay as historical provenance.

**Root cause found (blind subagent tests, 3 fresh sessions):** the `skill` tool itself was returning a notice, not a body. `smart-compact` had `pruning.discardTools.skill = "Skill contents omitted after compaction..."`, so every skill load was replaced before the agent could read it; the agent then fell back to filesystem search, which is what produced "the skill loader returned empty". Fixed globally: `skill` removed from `discardTools` and added to `protectedTools` (`~/.config/opencode/smart-compact.jsonc`), documented in `LLM.txt` §7.7 and `docs/compaction.md` so new installs cannot reintroduce it. Requires an OpenCode restart to take effect.

**Second finding:** subagents had no `skill` tool in their toolset. `agents/cognitive-discovery.md` now carries `skill: allow` (verified: a fresh `cognitive-discovery` session reports the tool present), and `agents/cognitive-executor.md` §Subagent Delegation step 5 records that a delegated step must hand over the absolute skill file path, never the skill name alone.

**Index contract verified:** a blind agent given only the harness's `Base directory for this skill: <dir>` line resolved `templates/01-generate.md` and `templates/03-bundle.md` and read both headings correctly — the slim index is self-sufficient without absolute paths in the body.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `7c02a43b3a2a3f22fe1dd6f0f4946825df407481`
<!-- END_GIT_DIFF -->
