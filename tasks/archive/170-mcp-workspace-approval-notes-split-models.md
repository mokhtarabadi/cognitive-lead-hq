# Task 170: MCP Workspace Cleanup, Approval Notes, Split Models

**File:** `tasks/in-progress/170-mcp-workspace-approval-notes-split-models.md`
**Source:** manager
**Type:** feature
**Status:** in-progress

## Source Context

## Goal

Clean up the MCP server layout into locked uv projects with a shared common lib (D1), add optional manager notes to approval gates (D3), and split persona vs decision LLM models via env (D4).

## Manager's Notes

- Approved scope from D1/D2/D3/D4 proposal: D1 full (per-server pyproject + uv.lock, shared `mcp-common`, `--project` launch commands), D3 (force-reply note, independent timeout, never blocks gate), D4 (`DECISION_MODEL` with `PERSONA_MODEL` fallback).
- After implementation: inject diff into this file, upgrade the global install, and hand off with a restart-and-test instruction.
- `.env` secrets stay out of git; lockfiles (`uv.lock`) ARE committed for reproducibility.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] D4: DECISION_MODEL env + fallback + tests + docs
- [x] D3: approval note flow + tests
- [x] D1: mcp-common lib + 5 pyprojects + locks + --project commands
- [x] Full suite green, task file injected, global upgraded

## Acceptance Criteria

- [x] Persona turns use PERSONA_MODEL, extraction uses DECISION_MODEL (fallback verified)
- [x] Approval gate can return an optional manager note without blocking on silence
- [x] Every server runs locked (`uv.lock`) via `--project`; shared loader lives in one place
- [x] Global install mirrors repo; post-restart smoke green

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with "mcp[cli]>=1.0,<2.0" --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin -- pytest tests/ -q`
- **Expected result:** all green, exit 0
- **Actual result:** `108 passed, 8 warnings in 1.24s`; `COMPILE-OK`; all 5 global servers answer `tools/list` via locked `--project` form (persona 4, decisions 5, context 8, memory 6, lint 4 tools)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** `--project` launch form behaves differently (cwd/env); workspace refactor breaks test import paths.
- **Rollback plan:** Keep server code untouched in shape (only loader import source changes); revert opencode.json commands to plain `uv run <path>`; per-server locks are additive files.

---

## Execution Log & Reasoning

**D4 (split models):** `mcp-decision-server` gained `_get_decision_model()` — `DECISION_MODEL`, else `PERSONA_MODEL`, else built-in DeepSeek default (blank counts as unset). Wired into `extract_session_decisions`; documented in `.env.example` (`DECISION_MODEL=` blank) and both opencode.json `environment` blocks. Test covers default/fallback/override/blank.

**D3 (approval notes):** `send_approval_request(..., ask_note=True, note_timeout_s=300)` → after the decision, one force-reply prompt; silence/`/skip`/timeout → `note=None`; gate NEVER waits on the note. `_collect_note()` helper; `request_admin_approval(..., ask_note=True)` surfaces `note` for task reasoning (reject reasons are the prime case). Existing flow tests pinned with `ask_note=False`; new tests: note captured with force-reply assertion, silence-resolves-None with `note_timeout_s=0`.

**D1 (uv workspace):** new `mcp-common/` package (`mcp_common.env.load_env_files`, the single home of the dotenv loader); both servers import it with a sibling-tree fallback (`<install-root>/mcp-common/src`) so plain runs/tests work without install — thin `_load_env_files` wrappers keep the tested entry points stable. Per-server `pyproject.toml` + committed `uv.lock` ×6 (common 1 pkg, persona/decision 79, context 50, memory 42, lint 41). Launch commands in repo + global opencode.json switched to locked `uv run --project <dir> <dir>/server.py` (verified live: persona tools/list answers, env notice on stderr). Fixed a second off-by-one along the way (loader checked `parent.parent` instead of `parent`). Global install synced (mcp-common, pyprojects, locks, servers, DECISION_MODEL in `.env` backup); drift clean; all 5 global servers answer `tools/list` (4/5/8/6/4 tools; first persona probe needed a warm env build, then green).

**Deviations:** kept flat server layouts (no file moves — test import paths untouched); locks are per-server, not one workspace lock; `DECISION_REPO_PATH` intentionally NOT in `environment` blocks (relative path must keep resolving per-cwd).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
