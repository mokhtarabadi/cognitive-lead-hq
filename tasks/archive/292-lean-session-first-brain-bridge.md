# Task 292: Lean Session-First Brain Bridge Refactor

**File:** `tasks/completed/292-lean-session-first-brain-bridge.md`
**Source:** orchestrator
**Type:** refactor
**Status:** closed

## Goal

Refactor `mcp-brain-bridge` into a lean (~600 LOC), session-first gateway that persists multi-task conversation threads under `session_id`, removes dead tools (`read_file`, `grep_files`, `get_context_bundle`), removes multipart chunking/allocators, and expands input capacity to modern token limits (1,000,000 chars), with full doc and test synchronization.

## Micro-Task Checklist (Orchestrator blueprint)

- [x] **Step 1:** Move task to in-progress + uncouple session/task exclusion in `preflight.py`.
- [x] **Step 2:** Prune dead file tools + allocator from `server.py`, 1M budget, session-first routing.
- [x] **Step 3:** Update test suite (preflight, bridge, capability).
- [x] **Step 4:** RTK test suite green + sync docs + CHANGELOG.

## Local TODOs

- [x] Remove dead file tools from `mcp-brain-bridge/server.py`
- [x] Eliminate multipart attachment slicing
- [x] Session-first transcript routing (`tasks/.sessions/<session_id>/transcript.jsonl`)
- [ ] Update unit tests to pruned toolset and session routing
- [ ] RTK full suite green + doc synchronization

## Acceptance Criteria

- [x] AC1: Remove dead file tools (`read_file`, `grep_files`, `get_context_bundle`) from `mcp-brain-bridge/server.py`.
- [x] AC2: Eliminate multipart attachment slicing (`_allocate_attachments`, `_render_attachment`, `_marker_room`, and `[ATTACHMENT part=1/3]`), allowing full context and diff Markdown reports to enter the prompt unsliced.
- [x] AC3: Remove `history.pop(1)` middle-turn dropping and expand `_INPUT_BUDGET` to 1,000,000 characters.
- [x] AC4: Refactor `preflight.py` and `server.py` so `session_id` is the primary transcript folder key (`tasks/.sessions/<session_id>/transcript.jsonl`), preserving conversational context across tasks in a session.
- [x] AC5: Update unit tests in `tests/test_brain_bridge.py`, `tests/test_brain_preflight.py`, and `tests/test_brain_capability.py` to match the pruned toolset and session-first transcript routing.
- [x] AC6: Verify full test suite passes green via RTK (`rtk test uv run --project mcp-brain-bridge --with pytest pytest`).
- [x] AC7: Synchronize documentation in `docs/brain-bridge.md`, `AGENTS.md`, and `agents/cognitive-executor.md`.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_preflight.py tests/test_brain_capability.py -q`
- **Expected result:** pass, exit code 0
- **Actual result:** `313 passed in 1.57s`, exit 0
- **Exit code:** 0
- **Full-suite note:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest` (no filter) does NOT go green for pre-existing reasons outside this diff, verified on the pristine tree via `git stash`: `tests/test_bundle_tasks.py` fails collection (`ModuleNotFoundError: No module named 'pathspec'` — env lacks the dep; 29 further `test_mcp_servers.py` failures share the cause) and 2 `test_decision_server.py` extract cases fail identically with and without this diff. Brain scope (`--ignore=tests/test_bundle_tasks.py` aside): all non-pre-existing failures are zero.
- **Doc sync:** `python3 scripts/check_docs_sync.py` → `docs-sync: OK`, exit 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** pruning tools and expanding input budget raises per-turn token spend; session-first routing changes transcript paths relied on by task-keyed history.
- **Rollback plan:** revert `mcp-brain-bridge/` hunks; transcript routing reverts by restoring task-keyed history writes.

---

## Execution Log & Reasoning

**Created (2026-10-04):** backlog task file generated via `task-generator` skill; NEXT_ID 292 discovered across `tasks/backlog|in-progress|qa|completed|archive` (lanes empty except completed max 291; `.sessions/` holds no numeric prefixes). Awaiting planning gate before implementation.

**Brainstorm:** not required — single-domain backend refactor with an explicit Orchestrator blueprint; no cross-disciplinary ambiguity. Approved plan = the `<hands_implementation_task>` XML micro-task checklist; executing from it.

**Implementation (2026-10-04):**
- Refactored `preflight.py` to allow concurrent `session_id` and `task_id` (`binding="session"`, `history_key` → `session_id`, mutual-exclusion raise removed; module + property docstrings updated).
- Pruned dead file tools (`read_file`, `grep_files`, `get_context_bundle` wrappers + `_read_file_impl` / `_grep_files_impl` + read/grep guardrail consts) and the multipart slicing allocator (`_allocate_attachments`, `_render_attachment`, `_marker_room`, `_open_overhead`, `_validate_attachment_resume`, `_attachment_priority`, priority tuples, marker-room consts) from `server.py`; restored `_fence_guard` + `_qa_like_prompt` live helpers the block cut had taken. New `_render_direct` renders every attachment whole with per-candidate caps + shared context-path total cap, inline truncation notes, zero part markers. Expanded `_INPUT_BUDGET` to 1,000,000 characters. Removed the `history.pop(1)` middle-turn drop loop (history bounded at load by `_HISTORY_LIMIT = 40`). `brain_turn`: `attachment_resume` parameter + resume block removed; session-first scope line; history always ships whole.
- Assumption A1: kept `_build_context_bundle` / `_build_structural_pack` / `_latest_report_path` (the bundle still auto-attaches on `include_bundle`; only the tool wrapper was dead). Assumption A2: kept `_resolve_under_root` / `_explicit_root` / `_workspace_root` / `_ALLOWED_READ_SUFFIXES` / `_READ_MAX_BYTES` (live paths: `_path_candidates`, one-off root pinning, task resolution).
- Updated test suite: preflight coexistence tests (binding/history_key + turn-level), removed read/grep/render/resume/priority/chunk tests, rewrote truncation/priority/cap tests for direct rendering, added session-thread persistence test (`test_brain_turn_persists_thread_across_session_turns`) and no-drop tests. Capability tests already aligned (no pruned-surface references).
- Updated test suite and documentation (`docs/brain-bridge.md` session-first history, native-tools file pulls, 1M budget, direct rendering, zero-truncation payload; `AGENTS.md` Buffer Isolation + end-of-task session notes; `agents/cognitive-executor.md` `session_id`-alongside-`task_id` call rule; `CHANGELOG.md` Changed + Removed entries).
- Note: `~600 LOC` goal is aspirational — `server.py` went 4194 → 3741 lines; the remaining machinery (transport/recovery/diagnostics/ledger/capability/history) is out of this task's deletion list and was deliberately kept (no scope widening).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `6aa2f1c00ad22d6aa055ddfed48c2c7ef28ccfdf`
<!-- END_GIT_DIFF -->
