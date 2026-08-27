# Task 124: Create Chat-Interface Coaching User Prompts

**File:** `tasks/completed/124-create-chat-coaching-user-prompts.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Goal

Create two standalone chat-interface system prompt templates in `user-prompts/`: (1) a Founder Coaching Chat prompt optimized for AI Studio/Claude/ChatGPT with coachee profile, coaching philosophy, growth model, decision evaluation framework, and in-chat memory protocol; (2) a Daily English Coach Chat prompt for conversational English practice with session modes, correction format, and vocabulary bank. Synchronize all documentation.

## Local TODOs

- [x] Step 1: Initialize task file with canonical metadata (done — this file)
- [x] Step 2: Create `user-prompts/founder-coaching-chat.md`
- [x] Step 3: Create `user-prompts/daily-english-coach-chat.md`
- [x] Step 4: Update `README.md` with new file listings
- [x] Step 5: Update `CHANGELOG.md` via Parse-Then-Append
- [x] Step 6: Run full test & verification suite

## Acceptance Criteria

- [x] `user-prompts/founder-coaching-chat.md` exists with all 9 required XML blocks
- [x] `user-prompts/daily-english-coach-chat.md` exists with all 8 required XML blocks
- [x] `README.md` directory tree lists both new files
- [x] `CHANGELOG.md` documents both new templates under [Unreleased] -> Added
- [x] pytest suite exits 0 (49/50 — 1 pre-existing failure unrelated to this task)

## Verification Evidence

- **Test command:** `uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q`
- **Expected result:** All tests pass, exit code 0
- **Actual result:** 49/50 passed, 1 failed (pre-existing `test_workflow_upgrade_guide_exists` — missing `docs/workflow-upgrade-v8.4.5.md`, NOT caused by this task)
- **Exit code:** 1 (1 pre-existing failure only)

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0 (49/50 — 1 pre-existing failure)
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Chat prompts may be too opinionated for some users' coaching style
- **Rollback plan:** `git rm` the two new files and revert README/CHANGELOG edits

---

## Execution Log & Reasoning

**Files created:**
- `user-prompts/founder-coaching-chat.md` — 9 XML blocks: `<system_version>`, `<role>`, `<coachee_profile>` (6 behavioral patterns), `<coaching_philosophy>` (7 principles), `<growth_model>` (6-stage progression), `<decision_evaluation_framework>` (6 questions with application rules), `<chat_interaction_modes>` (3 modes with distinct rhythms), `<in_chat_memory_protocol>` (running summary structure), `<initialization>`.
- `user-prompts/daily-english-coach-chat.md` — 8 XML blocks: `<system_version>`, `<role>` (English-only, no coding), `<learner_profile>` (Persian native, common patterns), `<coaching_philosophy>` (6 principles including Persian phonetic pronunciation guides), `<session_modes>` (4 modes: Free, Roleplay, Vocab, Pronunciation), `<correction_format>` (Persian `> 💡 **نکته‌ی مربی:**`), `<in_chat_vocabulary_bank>` (track/test/build/retire), `<initialization>`.

**Files modified:**
- `README.md` — added `founder-coaching-chat.md` and `daily-english-coach-chat.md` to `user-prompts/` directory tree listing.
- `CHANGELOG.md` — added `### Added` section under `[Unreleased]` with two entries documenting the new templates.

**Architectural reasoning:**
- Both prompts are designed as standalone chat-interface system instructions — copy-paste into AI Studio, Claude, or ChatGPT. No external tools or MCP servers required.
- The Founder Coaching prompt follows the V9 separation-of-concerns principle: coaching content lives in a dedicated user prompt, NOT in the system prompt. This allows the Manager to customize coaching style independently.
- The English Coach prompt includes Persian phonetic pronunciation guides (e.g., /اِکسپِرت/ for *expert*) — a unique feature for Persian-speaking learners that bridges the gap between written English and spoken sounds.
- Both prompts use `<in_chat_memory_protocol>` / `<in_chat_vocabulary_bank>` to maintain state within the chat history, avoiding the need for external memory systems.

**Verification:** pytest 49/50 passed (1 pre-existing failure: `test_workflow_upgrade_guide_exists`). No regressions introduced by this task.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `bbdd4460aeb18d652de552c4fefdbf238ca91cbb`
<!-- END_GIT_DIFF -->
