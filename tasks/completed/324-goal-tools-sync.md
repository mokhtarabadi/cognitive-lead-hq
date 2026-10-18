# Task 324: Goal plugin 5-tool specification and evidence workflow alignment

**File:** `tasks/qa/324-goal-tools-sync.md`
**Source:** manager
**Type:** chore
**Status:** in-progress
**Project:** /home/mohammad/Develop/Projects/cognitive-lead-hq
**Priority:** High

## Goal

Align goal plugin tool specification across prompt fragments, docs, and README with the shipped implementation: five agent tools with goal_evidence as sole evidence writer and goal_complete closed-empty.

## Local TODOs

- [x] Step 1: Create task file 324
- [x] Step 2: Bump system_version 9.61.0 to 9.61.1
- [x] Step 3: Update 09-hands_protocols.md to five tools
- [x] Step 4: Update docs/compaction.md agent lane
- [x] Step 5: Update README.md agent lane
- [x] Step 6: Update tests/test_prompt_sync.py version pin
- [x] Step 7: Reassemble system-prompt.md byte-identical
- [x] Step 8: Run pytest suites green
- [x] Step 9: Update CHANGELOG under Unreleased Fixed

## Acceptance Criteria

- [x] All five goal tools named in 09-hands_protocols, compaction.md, and README
- [x] goal_evidence documented as sole evidence writer, goal_complete closed-empty
- [x] system_version 9.61.1 everywhere with byte-identical re-assemble
- [x] All pytest suites pass with exit code 0

## Execution Log & Reasoning

- Validation: read AGENTS.md plus docs/conventions.md; DESIGN.md, docs/architecture.md, and docs/data_model.md absent (skipped per Absent-File Policy); memory index loaded. No rule violations found in Orchestrator instructions.
- Applied five exact edits: 01-system_version 9.61.0 to 9.61.1; 09-hands_protocols four tools to five tools with goal_evidence sole writer and goal_complete closed-empty; docs/compaction.md agent lane plus evidence-before-complete; README.md agent lane; test_prompt_sync.py pin to 9.61.1.
- Reassembled system-prompt.md (111312 bytes, byte-identical re-assemble verified via cmp).
- Stack-skill skip record: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only prompt-text change, no stack marker applies"

## Definition of Done

- [x] Assembler plus tests pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append

## Risk & Rollback

- **Risk:** Prompt plus docs drift if rebuild step is skipped.
- **Rollback plan:** Revert hunks via `git checkout --` on touched paths only.

## Verification Evidence

- `python3 scripts/prompt-build/assemble_system_prompt.py --output system-prompt.md` — Assembled 111312 bytes, exit 0; byte-identical re-assemble verified via cmp, exit 0.
- `rtk test /home/mohammad/v2ray-to-subs/.venv/bin/pytest tests/test_prompt_sync.py tests/test_skill_registry.py tests/test_input_validation_pipeline.py -q` — expected all pass, actual 39 passed, exit 0.
- Greps: `five tools` hits in 09-hands_protocols.md:165 and system-prompt.md:400; `goal_evidence` hits in README.md:481, docs/compaction.md:44, 09-hands_protocols.md:165, system-prompt.md:400; `9.61.1` hits in 01-system_version.md:1, system-prompt.md:1, test_prompt_sync.py:47.
- Stack-skill skip record: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only prompt-text change, no stack marker applies"

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
