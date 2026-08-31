# Task 136: OpenCode Executor Stack Context Injection & Goal Plugin Guardrails

**File:** `tasks/completed/136-opencode-executor-stack-context-and-goal-plugin-guardrails.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Implement structured prompt building, Goal Plugin termination token extraction, process group isolation, and concurrency semaphore enforcement in `loop-engine/executor.py`, expand the executor test suite, and document the new executor behavior in `docs/loop-engine/configuration.md`.

## Blueprint Reference

Phase A / Task LE-4 — OpenCode Executor Stack Context Injection & Goal Plugin Guardrails. Blueprint decisions D1–D5 recorded under `## Manager Decisions`.

## Manager's Notes

- Termination token regexes: `TERM_COMPLETE`, `TERM_BLOCKED` (with optional reason capture), `TRANSPORT_ERROR`.
- `HandsExecutor.__init__` gains `self._semaphore = asyncio.Semaphore(config.max_parallel_tasks)`.
- New `_build_prompt` method constructs clean XML-tagged sections (`<task_instructions>`, `<stack_context>`, `<blueprint_context>`, `<qa_feedback>`, `<goal_rules>`).
- `execute()` wraps execution in `async with self._semaphore:` and uses `_build_prompt`.
- `_run_once` uses `config.idle.executing_timeout_seconds` (fallback 900.0), `start_new_session=True` on POSIX, `os.killpg` SIGKILL on timeout, Goal Plugin blocker reason extraction, and terminal-marker/returncode handling.
- Test suite must grow from 148 to >= 160 passing tests with 0 failures.

## Local TODOs

- [x] Initial codebase exploration
- [x] Initialize task file with canonical template (D1–D5, AC, DoD)
- [x] Update regex definitions in executor.py
- [x] Add semaphore to HandsExecutor.__init__
- [x] Implement _build_prompt XML construction
- [x] Update execute() to use semaphore + _build_prompt
- [x] Update _run_once with timeout/process-group/killpg/blocked-reason handling
- [x] Expand test_executor.py (prompt combos, tokens, semaphore, timeout kill, transport retries)
- [x] Document executor behavior in docs/loop-engine/configuration.md
- [x] Verify functionality (baseline 148 → >= 160 passed, 0 failed)

## Acceptance Criteria

- [x] `TERM_COMPLETE` matches `[goal:complete]` case-insensitively; `TERM_BLOCKED` matches `[goal:blocked]` and `[goal:blocked: <reason>]` extracting the reason; `TRANSPORT_ERROR` matches the specified transport error patterns
- [x] `HandsExecutor.__init__` initializes `self._semaphore = asyncio.Semaphore(config.max_parallel_tasks)`
- [x] `_build_prompt` produces XML-tagged sections: `<task_instructions>`, `<stack_context>` (with MANDATORY skill loading directive + toolchain instructions), `<blueprint_context>`, `<qa_feedback>`, `<goal_rules>`
- [x] `execute()` wraps execution in `async with self._semaphore:` and generates the prompt via `_build_prompt`
- [x] `_run_once` uses `config.idle.executing_timeout_seconds` (fallback 900.0), passes `start_new_session=True` on POSIX, kills the process group with `os.killpg(..., SIGKILL)` on timeout (suppressing ProcessLookupError/AttributeError/PermissionError), drains with `proc.wait(timeout=2.0)`, and returns timeout/blocked/complete status dicts
- [x] `_run_once` extracts blocker reason from `TERM_BLOCKED` match and returns it in the blocked status dict
- [x] `test_executor.py` covers: `_build_prompt` combinations, TERM_COMPLETE case-insensitive multiline, TERM_BLOCKED reason extraction (3 variants), semaphore throttling, process group timeout kill + `start_new_session`, transport error retries vs non-retryable
- [x] Full suite passes with >= 160 tests, 0 failures
- [x] `docs/loop-engine/configuration.md` documents executor stack context injection, process group isolation, and Goal Plugin termination tokens

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** >= 160 passed, 0 failed
- **Actual result:** 163 passed, 0 failed (baseline 148 → +15 new tests in `test_executor.py`)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

**[2026-08-31] [D1] [ORCHESTRATOR-DETECTED]:** Structured XML Prompt Construction and Skill Directives
- **Rationale:** XML-delimited prompt blocks (`<task_instructions>`, `<stack_context>`, `<goal_rules>`) provide unambiguous instruction boundaries for local autonomous agents, preventing prompt confusion.
- **Alternatives considered:** Plain unformatted markdown or comma-separated string appending.
- **Impact:** Local OpenCode agents reliably load declared skills and execute verification toolchains prior to goal completion.

**[2026-08-31] [D2] [ORCHESTRATOR-DETECTED]:** Goal Plugin Termination Token Extraction
- **Rationale:** Parsing `[goal:complete]` / `[goal:blocked: <reason>]` from agent output lets the executor map agent signals to pipeline states deterministically, with blocker reasons propagated for QA feedback.
- **Alternatives considered:** Inferring completion purely from subprocess exit code; free-text blocked parsing.
- **Impact:** Deterministic terminal-state detection; blocked reasons flow into retry/feedback logic.

**[2026-08-31] [D3] [ORCHESTRATOR-DETECTED]:** Process Group Isolation via `start_new_session=True`
- **Rationale:** Launching the OpenCode subprocess in its own process group lets the executor kill the entire tree on timeout with `os.killpg(SIGKILL)`, preventing orphaned agent processes.
- **Alternatives considered:** Killing only the direct child PID.
- **Impact:** Clean timeout teardown; no leaked subprocesses or hung sessions.

**[2026-08-31] [D4] [ORCHESTRATOR-DETECTED]:** Concurrency Semaphore Enforcement
- **Rationale:** `asyncio.Semaphore(config.max_parallel_tasks)` in the executor guarantees the daemon never exceeds the configured concurrent Hands sessions, even under retry or multi-task bursts.
- **Alternatives considered:** Relying solely on daemon-level scheduling.
- **Impact:** Deterministic concurrency cap at the execution boundary; matches `config.max_parallel_tasks` (1–4).

**[2026-08-31] [D5] [ORCHESTRATOR-DETECTED]:** Configurable Executor Timeout from `idle.executing_timeout_seconds`
- **Rationale:** Using the existing idle config as the subprocess timeout (fallback 900.0) keeps a single source of truth for execution duration and aligns with the Goal Plugin's idle semantics.
- **Alternatives considered:** A hardcoded 7200s safety cap.
- **Impact:** Executor honors the same timeout budget as the rest of the pipeline; no new config surface.

## Risk & Rollback

- **Risk:** `os.killpg` on a non-POSIX platform or already-exited group could raise; legacy executors/stubs calling `execute()` with the old signature must keep working.
- **Rollback plan:** Revert `executor.py`, `test_executor.py` to pre-task state (git history); doc changes are additive; tests are non-destructive.

---

## Execution Log & Reasoning

**Implementation (2026-08-31):**

1. **`loop-engine/executor.py`** — LE-4 executor hardening:
   - **Regexes:** `TERM_COMPLETE = re.compile(r'\[goal:complete\]', re.IGNORECASE)`; `TERM_BLOCKED = re.compile(r'\[goal:blocked(?::\s*([^\]]+))?\]', re.IGNORECASE)` (captures optional reason); `TRANSPORT_ERROR` unchanged (already IGNORECASE with the specified patterns).
   - **Semaphore:** `HandsExecutor.__init__` now creates `self._semaphore = asyncio.Semaphore(config.max_parallel_tasks)`; `execute()` wraps the entire run (including transport retries) in `async with self._semaphore:`.
   - **`_build_prompt`:** New method constructing clean XML-tagged sections — `<task_instructions>` (always), `<stack_context name="..." display_name="...">` (when profile present: `MANDATORY: Load required skills via the native skill tool: <skills>`, preflight commands, `Run toolchain verification before completion: test='...', build='...', lint='...'`), `<blueprint_context>` (when non-empty), `<qa_feedback>` (when non-empty, with "Address the above QA feedback explicitly. Do NOT treat this as a new architectural plan."), `<goal_rules>` (always: `[goal:complete]` / `[goal:blocked: <reason>]`).
   - **`_run_once`:** timeout now `float(config.idle.executing_timeout_seconds)` with 900.0 fallback (replaces hardcoded 7200s cap); `start_new_session=True` passed on POSIX (`os.name == "posix"`); on `asyncio.TimeoutError` the process group is killed via `os.killpg(os.getpgid(proc.pid), signal.SIGKILL)` with `(ProcessLookupError, AttributeError, PermissionError)` suppression, drained via `proc.wait(timeout=2.0)`, returning `{"status": "timeout", "error": f"Exceeded {timeout}s timeout"}`; `TERM_BLOCKED` match extracts `reason = m.group(1).strip() if m.group(1) else "Agent signaled blocked"` and returns it in the blocked dict; `TERM_COMPLETE` or `returncode == 0` → complete.
2. **`loop-engine/test_executor.py`** — 15 new tests (8 → 23 collected): case-insensitive TERM_COMPLETE; TERM_BLOCKED reason extraction (lowercase, uppercase, no-reason); `_build_prompt` combinations (empty, stack profile with skills/toolchain/preflight, blueprint+QA, all sections); semaphore initialization + throttling (8 workers, max concurrent <= `max_parallel_tasks`); process-group timeout kill (tiny 0.1s timeout → `sleep 5` subprocess killed via killpg); `start_new_session` POSIX path; transport-error retry (3 attempts then complete); non-retryable error (1 attempt); blocked reason propagation through `execute()`.
3. **`loop-engine/test_le0_fixes.py`** — 3 legacy LE-0.1 tests updated: assertions changed from the old markdown headers (`## Approved Blueprint Context`, `## QA Feedback to Address`) to the new XML tags (`<blueprint_context>`, `<qa_feedback>`) — the prompt format was intentionally redesigned by this task (D1).
4. **`docs/loop-engine/configuration.md`** — new "Executor Stack Context Injection & Goal Plugin Guardrails (LE-4)" section documenting the XML prompt sections table, termination token regexes, process group isolation (`start_new_session=True` + `os.killpg(SIGKILL)`), timeout source (`idle.executing_timeout_seconds`, fallback 900.0), and concurrency semaphore.

**Verification:** baseline 148 passed → targeted `test_executor.py` 23 passed → full suite **163 passed, 0 failed** (exit 0). Three regressions were caught and fixed during the run: legacy LE-0.1 tests asserted the old markdown prompt format; updated to the new XML format (within `loop-engine/` scope). `git diff --stat` confirms changes are strictly scoped to `loop-engine/`, `docs/loop-engine/`, and the task file.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `d368b911c851ec32dd19efd12ce544d4c37debf7`
<!-- END_GIT_DIFF -->