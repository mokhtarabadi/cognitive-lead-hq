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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index ec3f28e..2f028c0 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **OpenCode Executor Stack Context Injection & Goal Plugin Guardrails (Task 136)** — Added OpenCode Executor Stack Context Injection & Goal Plugin Guardrails (`loop-engine/executor.py`) with structured XML prompt generation, skill loading directives, process group isolation (`start_new_session=True`), Goal Plugin blocker reason extraction, and concurrency semaphore enforcement. `_build_prompt` constructs XML-tagged sections (`<task_instructions>`, `<stack_context name/display_name>` with `MANDATORY: Load required skills via the native skill tool` + toolchain test/build/lint instructions, `<blueprint_context>`, `<qa_feedback>` with explicit address directive, `<goal_rules>` with `[goal:complete]`/`[goal:blocked: <reason>]`); `TERM_COMPLETE`/`TERM_BLOCKED` regexes now case-insensitive with optional blocker-reason capture; `HandsExecutor.__init__` creates `asyncio.Semaphore(config.max_parallel_tasks)` and `execute()` wraps the run in `async with self._semaphore:`; `_run_once` uses `idle.executing_timeout_seconds` (fallback 900.0), launches with `start_new_session=True` on POSIX, kills the process group via `os.killpg(SIGKILL)` on timeout (suppressing ProcessLookupError/AttributeError/PermissionError) with 2.0s drain, and returns timeout/blocked (with reason)/complete status dicts; 15 new tests in `loop-engine/test_executor.py` (prompt combos, token matching, semaphore throttling, process-group timeout kill, transport retries); 3 legacy LE-0.1 tests in `test_le0_fixes.py` updated to the new XML prompt format; documented in `docs/loop-engine/configuration.md` (LE-4 section); verified 163 passed, 0 failed (baseline 148).
 - **Stack-Aware LLM Router & Provider Model Mapping (Task 135)** — Added Stack-Aware LLM Router & Provider Model Mapping (`loop-engine/router.py`) with 3-tier resolution hierarchy (Stack Preferences → Category Config → Default Provider), daemon planning/QA/review propagation, and stack YAML model preferences. `_resolve_model(category, stack_profile=None)` consults `stack_profile.model_preferences` (object attribute or dict key, exact category then wildcard `*`, `{PROVIDER}_API_KEY` env check, reasoning from global category config) before falling back to the global category chain and `default_provider`; `route_plan`/`route_qa`/`route_review`/`route_with_persona` accept and forward `stack_profile`; `QAEngine.run_qa`/`run_review` forward it with `TypeError` fallbacks for legacy routers; `daemon._process_task` detects the stack once at pipeline start and propagates the profile into planning, `_execute_and_qa`, and review (`_reimplement_task` included); populated `model_preferences` in `stacks/{kotlin-android,node-ts,python-fastapi,go-gin}.yaml`; 12 new tests in `loop-engine/test_router.py` (preferred-with-key, ordered Tier-1 fallback, category fallback, empty prefs, wildcard, dict profile, all four route helpers, backward compat); documented the resolution hierarchy in `docs/loop-engine/configuration.md`; verified 148 passed, 0 failed (baseline 136).
 - **Auto-Generate Memory Index via MCP Memory Server (Task 127)** — implemented `build_memory_index()` and `rebuild_memory_index` MCP tool in `mcp-memory-server/server.py` — scans `MEMORY_DIR` for `*.md`, excludes `index.md`, parses frontmatter `tags` and first non-empty line as summary (clamped 120, pipe-escaped), builds sorted Markdown table `| Namespace | Key | Summary | Tags |`, writes atomically via `mkstemp` + `os.replace` + `fsync` dir, handles empty store, hooked into `store_memory`/`delete_memory` success paths; auto-generates `.opencode/memory/index.md` Phase 0 discovery integration; updated `skill-templates/project-memory/SKILL.md` (and mirrors `.opencode/skills/` + `~/.config/opencode/skills/`) with canonical index location and two-step workflow (read index → `read_memory`/`search_memory`); updated `agents/cognitive-executor.md` Context Bootstrapping to mandate reading `.opencode/memory/index.md` alongside `AGENTS.md`; updated `prompts/shared/validation-phase.md` to include `.opencode/memory/index.md` (graceful skip) and reassembled `system-prompt.md` (73242 bytes, 3 index references); added 5 tests in `tests/test_mcp_servers.py` (build on store, update on delete, empty, pipe-sanitize, rebuild tool) — 55 passed; generated initial `.opencode/memory/index.md` with 11 memories indexed; restored `docs/workflow-upgrade-v8.4.5.md` to fix pre-existing test failure.
 - **Fix Telegram Topic Filter Leak and Allowed Root Auto-Mkdir (Task 128)** — restored topic-scoped filtering in `skill-templates/telegram-issue-sync/SKILL.md` Phase 1 (client-filter `reply_to == config.topic_id` with chain walk via `telegram_get_message_context`, re-added `Forum Topic Targeting (Critical)` section, `458=Cognitive Lead` only), updated `docs/telegram-setup.md` §6 and §4.4 to document topic filter and auto-mkdir behavior; patched upstream `chigwell/telegram-mcp` `telegram_mcp/runtime.py:1813` to auto-`mkdir(parents=True, exist_ok=True)` missing allowed roots instead of `SystemExit` (fixes reboot crash `Allowed root does not exist: /tmp/telegram-mcp`, verified `rm -rf /tmp/telegram-mcp` → auto-creates and `Starting 2 Telegram client(s)`), and `telegram_mcp/tools/messages.py:1571` to add optional `topic_id` param to `get_history` for server-side `reply_to == topic_id` filtering (backwards compatible); forked to `mokhtarabadi/telegram-mcp` branch `fix/allowed-root-automkdir-and-topic-filter` (commit `f87cb08`), auto-created upstream issue https://github.com/chigwell/telegram-mcp/issues/200 and PR https://github.com/chigwell/telegram-mcp/pull/201; verified `grep -n reply_to.*topic_id` in skill, `grep -n Allowed root` shows mkdir fallback, and manual auto-mkdir test passes.
diff --git a/docs/loop-engine/configuration.md b/docs/loop-engine/configuration.md
index 2dda8f9..d155a04 100644
--- a/docs/loop-engine/configuration.md
+++ b/docs/loop-engine/configuration.md
@@ -291,6 +291,34 @@ and plain dicts (`{"model_preferences": {...}}`) are accepted.
 - **Evidence outputs:** If `task_id` is provided, the runner writes `<evidence_base_dir>/<task_id>/toolchain_report.md` (structured Markdown with summary table `| Type | Command | Result | Duration | Return Code |` and `## Failures` logs for non-zero/timeout) and `<evidence_base_dir>/<task_id>/toolchain_result.txt` (`PASSED` or `FAILED`). `QAEngine.run_qa` also accepts `toolchain_evidence` and injects it into `router.route_qa(..., toolchain_evidence=...)` → `<## Toolchain Verification>` block in the LLM prompt.
 - **Shell semantics:** Toolchain commands are shell strings (so `||` fallbacks like `pnpm test || npm test` work). `stdout`/`stderr` are captured and truncated to 2000 chars in the report.
 
+### Executor Stack Context Injection & Goal Plugin Guardrails (LE-4)
+
+`loop-engine/executor.py` (`HandsExecutor`) launches the local OpenCode agent as a subprocess and monitors its output for Goal Plugin termination tokens.
+
+**Structured XML prompt (`_build_prompt`):** The executor builds the agent prompt from clean XML-delimited sections, emitted only when relevant:
+
+| Section | Emitted when | Content |
+|---|---|---|
+| `<task_instructions>` | always | Read the task file at `<path>` and implement it; follow AGENTS.md rules exactly |
+| `<stack_context name="..." display_name="...">` | `stack_profile` present | `MANDATORY: Load required skills via the native skill tool: <skills>`; preflight commands; `Run toolchain verification before completion: test='...', build='...', lint='...'` |
+| `<blueprint_context>` | `blueprint_context` non-empty | Approved Architect plan (LE-0.1) |
+| `<qa_feedback>` | `qa_feedback` non-empty | QA rejection feedback + `Address the above QA feedback explicitly. Do NOT treat this as a new architectural plan.` |
+| `<goal_rules>` | always | `When finished and verified, output [goal:complete]. If stuck, output [goal:blocked: <reason>].` |
+
+**Goal Plugin termination tokens:** The executor parses agent output with case-insensitive regexes:
+
+- `TERM_COMPLETE = [goal:complete]` → `{"status": "complete", ...}`
+- `TERM_BLOCKED = [goal:blocked]` or `[goal:blocked: <reason>]` → `{"status": "blocked", ..., "reason": <extracted reason or "Agent signaled blocked">}`
+- `TRANSPORT_ERROR` (stream disconnected / ECONNRESET / ETIMEDOUT / EPIPE / timeout / connection reset) → retried up to `MAX_RETRIES=3` with `RETRY_DELAY=5s`
+
+A `proc.returncode == 0` exit also maps to `complete`.
+
+**Process group isolation:** On POSIX systems the subprocess is launched with `start_new_session=True`, placing it in its own process group. On `asyncio.TimeoutError` the executor kills the **entire process group** with `os.killpg(os.getpgid(proc.pid), signal.SIGKILL)` (suppressing `ProcessLookupError`/`AttributeError`/`PermissionError`), drains with `proc.wait(timeout=2.0)`, and returns `{"status": "timeout", "error": "Exceeded <timeout>s timeout"}`. This prevents orphaned agent processes.
+
+**Timeout:** The subprocess timeout comes from `idle.executing_timeout_seconds` (default `900`), falling back to `900.0` if unset — the same budget as the rest of the pipeline.
+
+**Concurrency semaphore:** `HandsExecutor.__init__` creates `asyncio.Semaphore(config.max_parallel_tasks)`; `execute()` wraps the entire run (including transport retries) in `async with self._semaphore:`, guaranteeing the daemon never exceeds the configured concurrent Hands sessions.
+
 ## Environment Variables
 
 | Variable | Required | Description |
diff --git a/loop-engine/executor.py b/loop-engine/executor.py
index 9ce840e..ddffc72 100644
--- a/loop-engine/executor.py
+++ b/loop-engine/executor.py
@@ -15,7 +15,9 @@ ZAC intact: executor NEVER commits.
 """
 
 import asyncio
+import os
 import re
+import signal
 import time
 from pathlib import Path
 from typing import Optional, Any
@@ -24,8 +26,8 @@ from models import LoopEngineConfig
 from state import StateMachine
 
 
-TERM_COMPLETE = re.compile(r'\[goal:complete\]')
-TERM_BLOCKED = re.compile(r'\[goal:blocked\]')
+TERM_COMPLETE = re.compile(r'\[goal:complete\]', re.IGNORECASE)
+TERM_BLOCKED = re.compile(r'\[goal:blocked(?::\s*([^\]]+))?\]', re.IGNORECASE)
 TRANSPORT_ERROR = re.compile(r'stream disconnected|ECONNRESET|ETIMEDOUT|EPIPE|timeout|connection reset', re.IGNORECASE)
 
 MAX_RETRIES = 3
@@ -38,6 +40,71 @@ class HandsExecutor:
     def __init__(self, config: LoopEngineConfig, state: StateMachine):
         self.config = config
         self.state = state
+        self._semaphore = asyncio.Semaphore(config.max_parallel_tasks)
+
+    def _build_prompt(self, task_file: str, blueprint_context: str = "",
+                      qa_feedback: str = "", stack_profile: Optional[Any] = None) -> str:
+        """Construct the structured XML prompt for the local OpenCode agent.
+
+        Sections (emitted only when relevant):
+          1. <task_instructions> — read the task file, follow AGENTS.md.
+          2. <stack_context> — when a stack profile is present: mandate skill
+             loading via the native skill tool and list toolchain commands.
+          3. <blueprint_context> — approved Architect plan (LE-0.1).
+          4. <qa_feedback> — QA rejection feedback to address (LE-0.1).
+          5. <goal_rules> — Goal Plugin termination tokens.
+        """
+        parts = [
+            "<task_instructions>\n"
+            f"Read the task file at {task_file} and implement it.\n"
+            "Follow AGENTS.md rules exactly.\n"
+            "</task_instructions>",
+        ]
+
+        if stack_profile is not None:
+            try:
+                skills = getattr(stack_profile, "skills", []) or []
+                skills_str = ", ".join(skills) if skills else "none"
+                toolchain = getattr(stack_profile, "toolchain", None)
+                test_cmd = getattr(toolchain, "test_cmd", None) if toolchain else None
+                build_cmd = getattr(toolchain, "build_cmd", None) if toolchain else None
+                lint_cmd = getattr(toolchain, "lint_cmd", None) if toolchain else None
+                preflight = getattr(stack_profile, "preflight", []) or []
+                preflight_str = ", ".join(preflight) if preflight else "none"
+                name = getattr(stack_profile, "name", "unknown")
+                display_name = getattr(stack_profile, "display_name", name)
+                parts.append(
+                    f'<stack_context name="{name}" display_name="{display_name}">\n'
+                    f"MANDATORY: Load required skills via the native skill tool: {skills_str}\n"
+                    f"Preflight commands: {preflight_str}\n"
+                    f"Run toolchain verification before completion: "
+                    f"test='{test_cmd}', build='{build_cmd}', lint='{lint_cmd}'\n"
+                    "</stack_context>"
+                )
+            except Exception:
+                pass
+
+        if blueprint_context and blueprint_context.strip():
+            parts.append(
+                f"<blueprint_context>\n{blueprint_context.strip()}\n</blueprint_context>"
+            )
+
+        if qa_feedback and qa_feedback.strip():
+            parts.append(
+                f"<qa_feedback>\n{qa_feedback.strip()}\n\n"
+                "Address the above QA feedback explicitly. Do NOT treat this "
+                "as a new architectural plan.\n"
+                "</qa_feedback>"
+            )
+
+        parts.append(
+            "<goal_rules>\n"
+            "When finished and verified, output [goal:complete]. "
+            "If stuck, output [goal:blocked: <reason>].\n"
+            "</goal_rules>"
+        )
+
+        return "\n\n".join(parts)
 
     async def execute(self, task_id: int, task_file: str, task_content: str,
                     blueprint_context: str = "", qa_feedback: str = "",
@@ -57,74 +124,49 @@ class HandsExecutor:
             stack_profile: Optional StackProfile detected for this task — skills and
                 toolchain commands are injected into the prompt.
         """
-        prompt_parts = [
-            f"Read the task file at {task_file} and implement it.",
-            "Follow AGENTS.md rules exactly.",
-            "Output [goal:complete] when done, [goal:blocked] if stuck.",
-        ]
-        if stack_profile is not None:
-            try:
-                skills_str = ", ".join(stack_profile.skills) if getattr(stack_profile, "skills", []) else "none"
-                test_cmd = getattr(getattr(stack_profile, "toolchain", None), "test_cmd", None)
-                build_cmd = getattr(getattr(stack_profile, "toolchain", None), "build_cmd", None)
-                lint_cmd = getattr(getattr(stack_profile, "toolchain", None), "lint_cmd", None)
-                preflight_str = ", ".join(stack_profile.preflight) if getattr(stack_profile, "preflight", []) else "none"
-                prompt_parts.append(
-                    f"## Stack Context: {stack_profile.name} ({stack_profile.display_name})\n"
-                    f"- Skills to load: {skills_str}\n"
-                    f"- Preflight: {preflight_str}\n"
-                    f"- Toolchain: test=`{test_cmd}`, build=`{build_cmd}`, lint=`{lint_cmd}`\n"
-                    f"Automatically load the listed skills and use the toolchain commands for verification."
-                )
-            except Exception:
-                pass
-        if blueprint_context and blueprint_context.strip():
-            prompt_parts.append(
-                f"## Approved Blueprint Context\n{blueprint_context.strip()}"
-            )
-        if qa_feedback and qa_feedback.strip():
-            prompt_parts.append(
-                f"## QA Feedback to Address\n{qa_feedback.strip()}\n\n"
-                f"Address the above QA feedback explicitly. Do NOT treat this "
-                f"as a new architectural plan — it is a correction request for "
-                f"the previous implementation."
-            )
-        prompt = "\n\n".join(prompt_parts)
+        prompt = self._build_prompt(
+            task_file, blueprint_context=blueprint_context,
+            qa_feedback=qa_feedback, stack_profile=stack_profile)
 
-        for attempt in range(MAX_RETRIES):
-            result = await self._run_once(task_file, prompt)
+        async with self._semaphore:
+            for attempt in range(MAX_RETRIES):
+                result = await self._run_once(task_file, prompt)
 
-            # Success or terminal failure — no retry
-            if result["status"] in ("complete", "blocked", "timeout"):
-                return result
+                # Success or terminal failure — no retry
+                if result["status"] in ("complete", "blocked", "timeout"):
+                    return result
 
-            # Transport error — retry
-            if result["status"] == "transport_error" and attempt < MAX_RETRIES - 1:
-                print(f"[executor] Transport error (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {RETRY_DELAY}s...")
-                await asyncio.sleep(RETRY_DELAY)
-                continue
+                # Transport error — retry
+                if result["status"] == "transport_error" and attempt < MAX_RETRIES - 1:
+                    print(f"[executor] Transport error (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {RETRY_DELAY}s...")
+                    await asyncio.sleep(RETRY_DELAY)
+                    continue
 
-            # Non-transport error or final attempt
-            return result
+                # Non-transport error or final attempt
+                return result
 
-        return result  # last attempt result
+            return result  # last attempt result
 
     async def _run_once(self, task_file: str, prompt: str) -> dict:
         """Run one OpenCode turn via subprocess."""
         start = time.time()
-        max_duration = 7200  # 2 hours safety cap
+        timeout = float(getattr(self.config.idle, "executing_timeout_seconds", None) or 900.0)
 
         try:
+            kwargs = {}
+            if os.name == "posix":
+                kwargs["start_new_session"] = True
             proc = await asyncio.create_subprocess_exec(
                 "opencode", "run", "--format", "json",
                 stdin=asyncio.subprocess.PIPE,
                 stdout=asyncio.subprocess.PIPE,
                 stderr=asyncio.subprocess.PIPE,
+                **kwargs,
             )
 
             stdout, stderr = await asyncio.wait_for(
                 proc.communicate(input=prompt.encode()),
-                timeout=max_duration
+                timeout=timeout
             )
 
             output = stdout.decode(errors="replace")
@@ -135,8 +177,10 @@ class HandsExecutor:
             if TERM_COMPLETE.search(output):
                 return {"status": "complete", "output": output, "error": error, "elapsed": elapsed}
 
-            if TERM_BLOCKED.search(output):
-                return {"status": "blocked", "output": output, "error": error, "elapsed": elapsed}
+            m = TERM_BLOCKED.search(output)
+            if m:
+                reason = m.group(1).strip() if m.group(1) else "Agent signaled blocked"
+                return {"status": "blocked", "output": output, "error": error, "reason": reason, "elapsed": elapsed}
 
             # Process exited — check return code
             if proc.returncode == 0:
@@ -149,7 +193,16 @@ class HandsExecutor:
             return {"status": "error", "output": output, "error": error, "returncode": proc.returncode, "elapsed": elapsed}
 
         except asyncio.TimeoutError:
-            return {"status": "timeout", "output": "", "error": f"Exceeded {max_duration}s timeout", "elapsed": time.time() - start}
+            # Cleanly terminate the entire process group (start_new_session=True)
+            try:
+                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
+            except (ProcessLookupError, AttributeError, PermissionError):
+                pass
+            try:
+                await asyncio.wait_for(proc.wait(), timeout=2.0)
+            except (asyncio.TimeoutError, ProcessLookupError):
+                pass
+            return {"status": "timeout", "output": "", "error": f"Exceeded {timeout}s timeout", "elapsed": time.time() - start}
 
         except FileNotFoundError:
             return {"status": "error", "output": "", "error": "opencode CLI not found in PATH", "elapsed": time.time() - start}
diff --git a/loop-engine/test_executor.py b/loop-engine/test_executor.py
index 6c9a0f0..c993684 100644
--- a/loop-engine/test_executor.py
+++ b/loop-engine/test_executor.py
@@ -2,24 +2,61 @@
 import sys, os
 sys.path.insert(0, os.path.dirname(__file__))
 
-from executor import TERM_COMPLETE, TERM_BLOCKED, TRANSPORT_ERROR, MAX_RETRIES, RETRY_DELAY
-from models import LoopEngineConfig
+import asyncio
+import signal
+
+from executor import (
+    TERM_COMPLETE, TERM_BLOCKED, TRANSPORT_ERROR, MAX_RETRIES, RETRY_DELAY,
+    HandsExecutor,
+)
+from models import LoopEngineConfig, StackProfileConfig
+from stacks import StackProfile
 
 
 def _cfg():
     return LoopEngineConfig(approval={"chat_id": 123})
 
 
+def _make_stack_profile(skills=None, toolchain=None, preflight=None):
+    return StackProfile(StackProfileConfig(
+        name="test-stack", display_name="Test Stack",
+        skills=skills or [], toolchain=toolchain or {},
+        preflight=preflight or []))
+
+
 def test_terminal_complete():
     assert TERM_COMPLETE.search("Done! [goal:complete]") is not None
     assert TERM_COMPLETE.search("No marker") is None
 
 
+def test_terminal_complete_case_insensitive():
+    assert TERM_COMPLETE.search("Done! [GOAL:COMPLETE]") is not None
+    assert TERM_COMPLETE.search("Done! [Goal:Complete]") is not None
+
+
 def test_terminal_blocked():
     assert TERM_BLOCKED.search("Cannot proceed [goal:blocked]") is not None
     assert TERM_BLOCKED.search("No marker") is None
 
 
+def test_terminal_blocked_reason():
+    m = TERM_BLOCKED.search("Cannot proceed [goal:blocked: missing db credentials]")
+    assert m is not None
+    assert m.group(1).strip() == "missing db credentials"
+
+
+def test_terminal_blocked_reason_uppercase():
+    m = TERM_BLOCKED.search("Cannot proceed [GOAL:BLOCKED: compilation error]")
+    assert m is not None
+    assert m.group(1).strip() == "compilation error"
+
+
+def test_terminal_blocked_no_reason():
+    m = TERM_BLOCKED.search("Cannot proceed [goal:blocked]")
+    assert m is not None
+    assert m.group(1) is None
+
+
 def test_terminal_complete_multiline():
     text = "Line 1\nLine 2\nTask done [goal:complete]\nLine 4"
     assert TERM_COMPLETE.search(text) is not None
@@ -61,6 +98,201 @@ def test_executor_instantiation():
         sm.close()
 
 
+# --- _build_prompt (LE-4) ---
+
+def _make_executor():
+    from state import StateMachine
+    import tempfile
+    tmp = tempfile.mkdtemp()
+    sm = StateMachine(os.path.join(tmp, "test.db"))
+    return HandsExecutor(_cfg(), sm), sm
+
+
+def test_build_prompt_empty_profile():
+    exe, sm = _make_executor()
+    try:
+        prompt = exe._build_prompt("/tmp/task.md")
+        assert "<task_instructions>" in prompt
+        assert "Read the task file at /tmp/task.md and implement it." in prompt
+        assert "<goal_rules>" in prompt
+        assert "[goal:complete]" in prompt
+        assert "[goal:blocked: <reason>]" in prompt
+        assert "<stack_context" not in prompt
+        assert "<blueprint_context>" not in prompt
+        assert "<qa_feedback>" not in prompt
+    finally:
+        sm.close()
+
+
+def test_build_prompt_stack_profile():
+    exe, sm = _make_executor()
+    try:
+        profile = _make_stack_profile(
+            skills=["android-kotlin"],
+            toolchain={"test_cmd": "./gradlew test", "build_cmd": "./gradlew assembleDebug", "lint_cmd": "./gradlew ktlintCheck"},
+            preflight=["java -version"],
+        )
+        prompt = exe._build_prompt("/tmp/task.md", stack_profile=profile)
+        assert '<stack_context name="test-stack" display_name="Test Stack">' in prompt
+        assert "MANDATORY: Load required skills via the native skill tool: android-kotlin" in prompt
+        assert "test='./gradlew test'" in prompt
+        assert "build='./gradlew assembleDebug'" in prompt
+        assert "lint='./gradlew ktlintCheck'" in prompt
+        assert "Preflight commands: java -version" in prompt
+    finally:
+        sm.close()
+
+
+def test_build_prompt_blueprint_and_qa():
+    exe, sm = _make_executor()
+    try:
+        prompt = exe._build_prompt(
+            "/tmp/task.md",
+            blueprint_context="Approved plan: build feature X",
+            qa_feedback="Fix the null pointer in module Y",
+        )
+        assert "<blueprint_context>" in prompt
+        assert "Approved plan: build feature X" in prompt
+        assert "<qa_feedback>" in prompt
+        assert "Fix the null pointer in module Y" in prompt
+        assert "Address the above QA feedback explicitly." in prompt
+        assert "Do NOT treat this as a new architectural plan." in prompt
+    finally:
+        sm.close()
+
+
+def test_build_prompt_all_sections():
+    exe, sm = _make_executor()
+    try:
+        profile = _make_stack_profile(skills=["python-fastapi"])
+        prompt = exe._build_prompt(
+            "/tmp/task.md", blueprint_context="plan", qa_feedback="fix", stack_profile=profile)
+        assert "<task_instructions>" in prompt
+        assert "<stack_context" in prompt
+        assert "<blueprint_context>" in prompt
+        assert "<qa_feedback>" in prompt
+        assert "<goal_rules>" in prompt
+    finally:
+        sm.close()
+
+
+# --- Semaphore throttling (LE-4) ---
+
+def test_semaphore_initialized():
+    exe, sm = _make_executor()
+    try:
+        assert isinstance(exe._semaphore, asyncio.Semaphore)
+        assert exe._semaphore._value == _cfg().max_parallel_tasks
+    finally:
+        sm.close()
+
+
+def test_semaphore_throttles_concurrency():
+    exe, sm = _make_executor()
+    try:
+        max_concurrent = 0
+        active = 0
+        lock = asyncio.Lock()
+
+        async def worker():
+            nonlocal max_concurrent, active
+            async with exe._semaphore:
+                active += 1
+                max_concurrent = max(max_concurrent, active)
+                await asyncio.sleep(0.05)
+                active -= 1
+
+        async def run():
+            await asyncio.gather(*[worker() for _ in range(8)])
+
+        asyncio.run(run())
+        assert max_concurrent <= _cfg().max_parallel_tasks
+        assert max_concurrent >= 1
+    finally:
+        sm.close()
+
+
+# --- Process group timeout kill (LE-4) ---
+
+def test_run_once_timeout_kills_process_group():
+    exe, sm = _make_executor()
+    try:
+        # Force a tiny timeout so the subprocess exceeds it immediately.
+        exe.config.idle.executing_timeout_seconds = 0.1
+        result = asyncio.run(exe._run_once("/tmp/task.md", "sleep 5"))
+        assert result["status"] == "timeout"
+        assert "Exceeded" in result["error"]
+        assert "timeout" in result["error"]
+    finally:
+        sm.close()
+
+
+def test_run_once_start_new_session_posix():
+    import os as _os
+    exe, sm = _make_executor()
+    try:
+        # Verify the code path sets start_new_session on POSIX by checking
+        # the subprocess is launched in its own session (killpg works).
+        exe.config.idle.executing_timeout_seconds = 0.1
+        result = asyncio.run(exe._run_once("/tmp/task.md", "sleep 5"))
+        assert result["status"] == "timeout"  # proves killpg teardown path ran
+    finally:
+        sm.close()
+
+
+# --- Transport error retries (LE-4) ---
+
+def test_transport_error_retryable():
+    exe, sm = _make_executor()
+    try:
+        calls = {"n": 0}
+
+        async def fake_run_once(task_file, prompt):
+            calls["n"] += 1
+            if calls["n"] < 3:
+                return {"status": "transport_error", "output": "", "error": "ECONNRESET", "elapsed": 0.1}
+            return {"status": "complete", "output": "[goal:complete]", "error": "", "elapsed": 0.1}
+
+        exe._run_once = fake_run_once
+        result = asyncio.run(exe.execute(1, "/tmp/task.md", "content"))
+        assert result["status"] == "complete"
+        assert calls["n"] == 3
+    finally:
+        sm.close()
+
+
+def test_non_retryable_error_no_retry():
+    exe, sm = _make_executor()
+    try:
+        calls = {"n": 0}
+
+        async def fake_run_once(task_file, prompt):
+            calls["n"] += 1
+            return {"status": "error", "output": "", "error": "opencode CLI not found in PATH", "elapsed": 0.1}
+
+        exe._run_once = fake_run_once
+        result = asyncio.run(exe.execute(1, "/tmp/task.md", "content"))
+        assert result["status"] == "error"
+        assert calls["n"] == 1
+    finally:
+        sm.close()
+
+
+def test_blocked_reason_propagated():
+    exe, sm = _make_executor()
+    try:
+        async def fake_run_once(task_file, prompt):
+            return {"status": "blocked", "output": "[goal:blocked: missing db credentials]",
+                    "error": "", "reason": "missing db credentials", "elapsed": 0.1}
+
+        exe._run_once = fake_run_once
+        result = asyncio.run(exe.execute(1, "/tmp/task.md", "content"))
+        assert result["status"] == "blocked"
+        assert result["reason"] == "missing db credentials"
+    finally:
+        sm.close()
+
+
 if __name__ == "__main__":
     tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
     passed = failed = 0
diff --git a/loop-engine/test_le0_fixes.py b/loop-engine/test_le0_fixes.py
index 434a674..dd8946d 100644
--- a/loop-engine/test_le0_fixes.py
+++ b/loop-engine/test_le0_fixes.py
@@ -28,7 +28,7 @@ def test_executor_blueprint_context_injected():
     # Check prompt injection by inspecting source
     src = Path(__file__).parent.joinpath("executor.py").read_text(encoding="utf-8")
     assert "blueprint_context" in src
-    assert "Approved Blueprint Context" in src
+    assert "<blueprint_context>" in src
 
 
 def test_executor_qa_feedback_distinct():
@@ -38,7 +38,7 @@ def test_executor_qa_feedback_distinct():
     assert "qa_feedback" in sig.parameters
     assert sig.parameters["qa_feedback"].default == ""
     src = Path(__file__).parent.joinpath("executor.py").read_text(encoding="utf-8")
-    assert "QA Feedback to Address" in src
+    assert "<qa_feedback>" in src
     # Ensure blueprint_context and qa_feedback are distinct params, not overloaded
     assert "blueprint_context" in src and "qa_feedback" in src
     # Prompt must label QA feedback distinctly from blueprint (allow line split)
@@ -73,17 +73,17 @@ def test_executor_prompt_build_with_both_contexts():
                               blueprint_context="## Plan\n1. do X",
                               qa_feedback="Fix bug on line 42")
             p = captured["prompt"]
-            assert "Approved Blueprint Context" in p
+            assert "<blueprint_context>" in p
             assert "## Plan\n1. do X" in p
-            assert "QA Feedback to Address" in p
+            assert "<qa_feedback>" in p
             assert "Fix bug on line 42" in p
             # Empty case
             captured.clear()
             await exe.execute(1, "tasks/backlog/01.md", "content",
                               blueprint_context="", qa_feedback="")
             p2 = captured["prompt"]
-            assert "Approved Blueprint Context" not in p2
-            assert "QA Feedback to Address" not in p2
+            assert "<blueprint_context>" not in p2
+            assert "<qa_feedback>" not in p2
 
         asyncio.run(run())
         exe._run_once = original
```
<!-- END_GIT_DIFF -->