# Task 293: OpenCode V2 Session-First Monorepo Synchronization

**File:** `tasks/completed/293-opencode-v2-session-monorepo-sync.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Goal

Synchronize the monorepo to OpenCode V2 session-first semantics: ambient `OPENCODE_SESSION_ID` auto-detection in `mcp-brain-bridge` preflight, system prompt v9.53.0 with updated fragments, purged file-pull references from agent specs, aligned downstream skills, and synchronized docs/changelog.

## Micro-Task Checklist (Orchestrator blueprint)

- [x] **Step 1:** Scaffold and stage Task 293 in Kanban lanes.
- [x] **Step 2:** Ambient `OPENCODE_SESSION_ID` detection in `mcp-brain-bridge`.
- [x] **Step 3:** Update system prompt fragments and reassemble monolith to 9.53.0.
- [x] **Step 4:** Clean up agent specs in `agents/`.
- [x] **Step 5:** Synchronize downstream skills (`skill-templates/`).
- [x] **Step 6:** Update documentation, changelog, and verify.

## Local TODOs

- [x] Wire ambient session detection + unit test
- [x] Bump fragments + reassemble prompt + prompt-sync green
- [x] Clean agent specs + skill template
- [x] Docs + README + LLM.txt + CHANGELOG + RTK verification

## Acceptance Criteria

- [x] AC1: `preflight.validate_request` auto-detects ambient `OPENCODE_SESSION_ID` when `session_id` is omitted.
- [x] AC2: System prompt reassembled to v9.53.0 with fragments 01/09/22 updated and `test_prompt_sync` green.
- [x] AC3: `agents/cognitive-executor.md` file-pull section purged of deleted tools and documents ambient session detection.
- [x] AC4: `agents/cognitive-discovery.md` handoffs require whole-file reporting without multipart expectations.
- [x] AC5: `skill-templates/audit-agents/SKILL.md` template rules carry session-thread persistence.
- [x] AC6: Docs (`brain-bridge`, `services`), `README.md`, `LLM.txt`, `CHANGELOG.md` synchronized; RTK suite + doc-sync green.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_preflight.py tests/test_brain_capability.py tests/test_prompt_sync.py -q`
- **Expected result:** pass, exit code 0
- **Actual result:** `327 passed in 1.61s`, exit 0
- **Exit code:** 0
- **Doc sync:** `python3 scripts/check_docs_sync.py` → `docs-sync: OK`, exit 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** ambient env detection could bind an unintended session when callers expect one-off turns.
- **Rollback plan:** revert `preflight.py` ambient block; repin prompt version to 9.52.0 and reassemble.

---

## Execution Log & Reasoning

**Created (2026-10-04):** backlog file scaffolded via `task-generator` skill; NEXT_ID 293 (lanes max 292).

**Implementation (2026-10-04):**
- Wired ambient `OPENCODE_SESSION_ID` detection in `preflight.py` (`validate_request`: explicit `session_id` wins, else ambient env cleaned via `require_session_id`, else `None`; docstring updated). New test `test_preflight_uses_ambient_opencode_session_id`; binding tests hardened to clear the ambient var.
- Fix (verification-driven): first RTK run showed 7 failures in `test_brain_bridge.py` — ambient `OPENCODE_SESSION_ID=ses_ef82…` from the live shell hijacked task-keyed turns (the exact risk in Risk & Rollback). Added hermetic autouse fixtures (`_no_ambient_session`) to `test_brain_bridge.py` + `test_brain_capability.py`; suite now **327 passed**. Also updated `brain_turn` `session_id` docstring in `server.py` for ambient semantics.
- Updated prompt fragments `01` (9.52.0 → 9.53.0), `09` (2× automatic-mode chaining → active session thread), `22` (survival contract + session ID); reassembled `system-prompt.md` (98933 bytes, `assemble_system_prompt.py` exit 0); `test_prompt_sync` pin → 9.53.0.
- Excised deleted file-pull tools from `agents/cognitive-executor.md` (new `File context retrieval` section; state machine documents ambient detection). Verified `agents/cognitive-discovery.md` carries no multipart/chunk expectations (read-only check, no edit — kept out of staging list).
- Updated `skill-templates/audit-agents/SKILL.md` (2× Buffer Isolation + 2× End-Of-Task Sequence, project-agnostic session-thread wording; HQ-only rules untouched per AGENTS.md).
- Updated `docs/brain-bridge.md` (history section + Environment table), `docs/services.md` (mcp-brain singular-tool note), `README.md` + `LLM.txt` (session-thread summaries), `CHANGELOG.md` (`## [9.53.0] - 2026-10-04`, Added + Changed).
- Assumption A1: `qa_transition` `modified_files` extended beyond the Orchestrator list with `mcp-brain-bridge/server.py`, `tests/test_brain_bridge.py`, `tests/test_brain_capability.py`, `docs/services.md` — all four carry real hunks required for AC1/AC6 (ambient docstring, hermetic fixtures, singular-tool note); staging only the listed subset would leave changes unstaged and the injected diff incomplete.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `e3c76f0dbd14120764cdba2bc8a76c92d8b39ecd`
<!-- END_GIT_DIFF -->
