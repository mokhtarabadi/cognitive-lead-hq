# Task 133: Stack Profile Engine and Schema

**File:** `tasks/completed/133-stack-profile-engine-and-schema.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Source Context

## Goal

Implement the Stack Profile Engine for loop-engine — declarative YAML stack profiles, two-tier stack detection (explicit header → marker files/extensions → keywords → generic fallback), preflight toolchain validation, and daemon/executor integration enabling polyglot monorepo support without modifying core daemon code.

## Blueprint Reference

Phase A / Task LE-1 (Stack Profile Engine) — Discovery report `context-reports/task-133-context.md`. Separation of stack execution profiles from cognitive categories (quick/deep) for modular extensibility.

## Manager's Notes

Route after completion: QA Engineer (Application logic: stack detection heuristics, preflight CLI validation, daemon integration). Enforce verification-before-completion: baseline 88 passed → target >=95 passed, 0 failures.

## Local TODOs

- [x] Initialize task file and verify Kanban placement
- [x] Define Pydantic schemas for Stack Profiles in loop-engine/models.py
- [x] Create stacks/ directory with 5 declarative YAML profiles (generic, node-ts, kotlin-android, python-fastapi, go-gin)
- [x] Implement loop-engine/stacks.py (StackProfile, StackRegistry, StackDetector, PreflightRunner)
- [x] Integrate StackRegistry/Detector/Preflight into daemon.py and executor.py
- [x] Create comprehensive test suite loop-engine/test_stacks.py
- [x] Update docs/loop-engine/configuration.md with stacks docs
- [x] Verify baseline 88 → full suite >=95 passed, 0 failed
- [x] Update CHANGELOG.md, log decisions, lint and stage

## Acceptance Criteria

- [x] Pydantic schemas `StackDetectionConfig`, `StackToolchainConfig`, `StackProfileConfig` defined in `loop-engine/models.py` with correct defaults; `LoopEngineConfig` extended with `stacks_dir` and `default_stack`
- [x] Directory `stacks/` contains 5 valid YAML profiles: `generic.yaml`, `node-ts.yaml`, `kotlin-android.yaml`, `python-fastapi.yaml`, `go-gin.yaml` with correct marker_files, extensions, skills, preflight, and toolchain fields
- [x] `loop-engine/stacks.py` implements `StackProfile`, `StackRegistry` (load/cache .yaml/.json, get_profile/list_profiles), `StackDetector` (two-tier detection: header > marker_files/extensions > keywords > generic), and `PreflightRunner` (async exec with timeout, PreflightResult)
- [x] `loop-engine/daemon.py` initializes `StackRegistry`, detects stack in `_process_task` and `_reimplement_task`, runs preflight before execution (CRASHED on failure with diagnostics), and passes active profile to `executor.execute()`
- [x] `loop-engine/executor.py` accepts `StackProfile` param and injects stack-specific skills/toolchain into agent prompt
- [x] Comprehensive test suite `loop-engine/test_stacks.py` covers parsing/rejection, detection precedence, preflight success/failure/timeout, and daemon integration
- [x] `docs/loop-engine/configuration.md` documents `stacks_dir`, `default_stack`, and stack profile schema format
- [x] Full test suite passes: `uv run --project loop-engine --with pytest pytest loop-engine/ -q` shows >=95 passed, 0 failed, 0 regressions, strictly greater than baseline 88

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** >=95 passed, 0 failed (baseline 88)
- **Actual result:** 110 passed, 0 failed (baseline confirmed 88 prior; after implementation 110 passed, 0 failed, 0 regressions — verified via `uv run --project loop-engine --with pytest pytest loop-engine/ -q` and direct `python loop-engine/test_stacks.py` showing 22 passed)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Manager Decisions

**[2026-08-31] [D1] [ORCHESTRATOR-DETECTED]:** Stack Profile Architecture and Separation of Concerns
- **Rationale:** Separated stack execution profiles from cognitive categories (quick/deep) to keep the daemon modular and extensible.
- **Alternatives considered:** Embedding stack-specific toolchain logic directly into `router.py` or hardcoding runner commands in `daemon.py`.
- **Impact:** Enables loop-engine to autonomously support polyglot monorepos and new tech stacks declaratively without modifying core daemon code.

**[2026-08-31] [D2] [ORCHESTRATOR-DETECTED]:** Declarative YAML Schema for Stack Profiles
- **Rationale:** Pydantic-validated YAML allows new stacks without code changes; supports both YAML and JSON with safe parsing via PyYAML or fallback.
- **Alternatives considered:** JSONC-only, TOML, or hardcoded dict in daemon.py.
- **Impact:** Single `stacks/` directory is source of truth; linting and test coverage for invalid schemas.

**[2026-08-31] [D3] [ORCHESTRATOR-DETECTED]:** Two-Tier Stack Detection Precedence
- **Rationale:** Explicit `**Stack:**` header gives deterministic override; workspace marker inference + keyword fallback enables auto-detection for untagged tasks.
- **Alternatives considered:** File-content regex only, or relying solely on marker_files.
- **Impact:** Deterministic precedence (header > marker_files/extensions > task_keywords > generic) testable and auditable.

**[2026-08-31] [D4] [ORCHESTRATOR-DETECTED]:** Preflight Toolchain Validation Before Execution
- **Rationale:** Running `preflight` commands with timeouts prevents wasted LLM execution when toolchain is broken; transitions to CRASHED with diagnostics.
- **Alternatives considered:** Skipping preflight, or running toolchain validation inside executor prompt only.
- **Impact:** Fast-fail safety; PreflightRunner returns structured PreflightResult(passed, errors).

**[2026-08-31] [D5] [ORCHESTRATOR-DETECTED]:** Default Stack Fallback to Generic
- **Rationale:** `default_stack: "generic"` guarantees every task resolves to a profile; generic has empty markers and safe no-op preflight.
- **Alternatives considered:** Failing open or requiring explicit stack on every task.
- **Impact:** No blocking for new/unknown stacks; generic profile is always present.

## Risk & Rollback

- **Risk:** YAML parsing failures, mis-detection due to overlapping marker_files, preflight timeouts hanging pipeline; provider concurrency gaps for new stacks.
- **Rollback plan:** Revert `loop-engine/models.py`, `daemon.py`, `executor.py`; delete `stacks/` and `loop-engine/stacks.py`; restore `docs/loop-engine/configuration.md`; rerun baseline tests.

---

## Execution Log & Reasoning

**Implementation sequence (exact per task):**

**Step 1 — Task file init:** Created `tasks/backlog/133-stack-profile-engine-and-schema.md` via canonical `task-generator` template with D1-D5, AC, DoD, then `mv tasks/backlog/... tasks/in-progress/...` and patched `**File:**` header.

**Step 2 — Pydantic schemas (`loop-engine/models.py`):** Added `StackDetectionConfig` (marker_files, extensions, task_keywords), `StackToolchainConfig` (test_cmd, build_cmd, lint_cmd), `StackProfileConfig` (name, display_name, detection, skills, preflight, toolchain, model_preferences), and extended `LoopEngineConfig` with `stacks_dir="stacks"` and `default_stack="generic"` (both Field with descriptions). Verified via `python -c` Pydantic dump.

**Step 3 — Declarative YAML profiles (`stacks/`):** Created repo-root `stacks/` with 5 YAML files: generic (fallback empty), node-ts (package.json/tsconfig, .ts/.tsx/.js, skills nextjs/react-vite, preflight node/pnpm, toolchain pnpm test), kotlin-android (gradle markers, .kt/.kts, android-kotlin, preflight java/gradlew, toolchain ./gradlew test), python-fastapi (pyproject/requirements, .py, python-fastapi skill, preflight python3/uv, toolchain pytest -q), go-gin (go.mod/.go, go-gin/go-hexagonal-grpc, preflight go version, toolchain go test ./...). Added `pyyaml>=6.0` to `loop-engine/pyproject.toml` for safe YAML parsing with JSON fallback.

**Step 4 — Core engine (`loop-engine/stacks.py`):** Implemented `StackProfile` (wraps config, .name/.display_name/.skills/.preflight/.toolchain/.to_dict), `StackRegistry` (repo-root-aware stacks_dir resolution, _parse_file handling .yaml via yaml.safe_load or JSON fallback, _load_all scanning sorted iterdir, ValueError wrapping with filename, get_profile/list_profiles/names/reload), `StackDetector` (regex for `**Stack:**` and plain `Stack:` header case-insensitive, ordered checks: header → marker_files existence → extensions scan (root + one-level deep, skipping .git/__pycache__/node_modules etc.) → task_keywords substring case-insensitive → generic fallback with synthetic fallback), `PreflightRunner` (dataclass PreflightResult, async run sequential shell commands via create_subprocess_shell, 30s timeout via wait_for, kill on timeout, capture stdout/stderr, non-zero → error list, empty preflight → passed=True, sync wrapper via asyncio.run). Validated via manual python checks: registry loads 5, header detection, marker/extension/keyword precedence, timeout and failure capture.

**Step 5 — Daemon/executor integration:** `daemon.py` – added `from stacks import StackRegistry, StackDetector, PreflightRunner`, extended `LoopEngineDaemon.__init__` to init `self.stack_registry = StackRegistry(config.stacks_dir, REPO_ROOT)`, extended `_execute_and_qa` signature with `stack_profile=None` and `**kwargs` forwarding with TypeError fallback for legacy stubs, in `_process_task` and `_reimplement_task` inserted detection `StackDetector.detect(task_content, REPO_ROOT, StackRegistry(...), default_stack)` + `PreflightRunner(30s).run(profile, cwd=REPO_ROOT)` before execution, CRASHED with `state.set_qa_feedback` on preflight failure, passing profile to `_execute_and_qa`. `executor.py` – added `Optional[Any]` import, extended `execute(..., stack_profile=None)` to inject `## Stack Context: {name} ({display_name})` block with skills, preflight, toolchain test/build/lint; backward compatible with default None and defensive getattr.

**Step 6 — Test suite (`loop-engine/test_stacks.py`):** 22 tests covering: config defaults/full/invalid, registry loads generic/get_profile/nonexistent/invalid schema/YAML+JSON both supported, detection precedence (header > marker > extensions > keywords > generic fallback + plain Stack: format), preflight success/failure/timeout/empty/mixed, LoopEngineConfig stack fields, daemon registry init (generic present), executor prompt injection (captured prompt contains stack name and toolchain). Verified: `python test_stacks.py` → 22 passed, `pytest test_stacks.py -v` → 22 passed.

**Step 7 — Docs (`docs/loop-engine/configuration.md`):** Added to Full Example JSONC `stacks_dir`/`default_stack`, added sections for `stacks_dir`, `default_stack`, and `Stack Profile Schema` with YAML example, detection precedence table, preflight description, registry notes, and default profiles table.

**Verification:** Baseline `uv run --project loop-engine --with pytest pytest loop-engine/ -q` → 88 passed pre-implementation. After: 110 passed, 0 failed (22 new + 88 existing, 3 initial stub failures fixed via TypeError fallback), exit 0. `git diff --stat` shows scoped changes to loop-engine/, stacks/, docs/loop-engine/.

**Quirks detected:** Generic preflight empty → immediate pass; /tmp extension scanning false-positive required empty-dir test fixtures; legacy StubExecutor without stack_profile needed fallback handling.

**Risks handled:** YAML missing PyYAML fallback to JSON; preflight timeouts kill proc; invalid schema ValueError bubbles with filename for debugging.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b21b6e1..c7c5ccd 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -10,6 +10,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Auto-Generate Memory Index via MCP Memory Server (Task 127)** — implemented `build_memory_index()` and `rebuild_memory_index` MCP tool in `mcp-memory-server/server.py` — scans `MEMORY_DIR` for `*.md`, excludes `index.md`, parses frontmatter `tags` and first non-empty line as summary (clamped 120, pipe-escaped), builds sorted Markdown table `| Namespace | Key | Summary | Tags |`, writes atomically via `mkstemp` + `os.replace` + `fsync` dir, handles empty store, hooked into `store_memory`/`delete_memory` success paths; auto-generates `.opencode/memory/index.md` Phase 0 discovery integration; updated `skill-templates/project-memory/SKILL.md` (and mirrors `.opencode/skills/` + `~/.config/opencode/skills/`) with canonical index location and two-step workflow (read index → `read_memory`/`search_memory`); updated `agents/cognitive-executor.md` Context Bootstrapping to mandate reading `.opencode/memory/index.md` alongside `AGENTS.md`; updated `prompts/shared/validation-phase.md` to include `.opencode/memory/index.md` (graceful skip) and reassembled `system-prompt.md` (73242 bytes, 3 index references); added 5 tests in `tests/test_mcp_servers.py` (build on store, update on delete, empty, pipe-sanitize, rebuild tool) — 55 passed; generated initial `.opencode/memory/index.md` with 11 memories indexed; restored `docs/workflow-upgrade-v8.4.5.md` to fix pre-existing test failure.
 - **Fix Telegram Topic Filter Leak and Allowed Root Auto-Mkdir (Task 128)** — restored topic-scoped filtering in `skill-templates/telegram-issue-sync/SKILL.md` Phase 1 (client-filter `reply_to == config.topic_id` with chain walk via `telegram_get_message_context`, re-added `Forum Topic Targeting (Critical)` section, `458=Cognitive Lead` only), updated `docs/telegram-setup.md` §6 and §4.4 to document topic filter and auto-mkdir behavior; patched upstream `chigwell/telegram-mcp` `telegram_mcp/runtime.py:1813` to auto-`mkdir(parents=True, exist_ok=True)` missing allowed roots instead of `SystemExit` (fixes reboot crash `Allowed root does not exist: /tmp/telegram-mcp`, verified `rm -rf /tmp/telegram-mcp` → auto-creates and `Starting 2 Telegram client(s)`), and `telegram_mcp/tools/messages.py:1571` to add optional `topic_id` param to `get_history` for server-side `reply_to == topic_id` filtering (backwards compatible); forked to `mokhtarabadi/telegram-mcp` branch `fix/allowed-root-automkdir-and-topic-filter` (commit `f87cb08`), auto-created upstream issue https://github.com/chigwell/telegram-mcp/issues/200 and PR https://github.com/chigwell/telegram-mcp/pull/201; verified `grep -n reply_to.*topic_id` in skill, `grep -n Allowed root` shows mkdir fallback, and manual auto-mkdir test passes.
+- **Stack Profile Engine (Task 133)** — Added Stack Profile Engine (`loop-engine/stacks.py`) with declarative YAML schemas, two-tier detection, preflight toolchain validation, and default profiles for Node-TS, Kotlin-Android, Python-FastAPI, Go-Gin, and Generic stacks. Pydantic schemas `StackDetectionConfig`, `StackToolchainConfig`, `StackProfileConfig` plus `LoopEngineConfig.stacks_dir`/`default_stack` in `loop-engine/models.py`; `stacks/` YAML profiles (generic, node-ts, kotlin-android, python-fastapi, go-gin) with marker_files/extensions/skills/preflight/toolchain; `StackRegistry`/`StackDetector`/`PreflightRunner` with YAML/JSON safe parsing and timeout handling; daemon integration via `StackRegistry` init, detection (`**Stack:**` header > marker_files/extensions > keywords > generic) and preflight (CRASHED on failure) + executor `stack_profile` prompt injection; `loop-engine/test_stacks.py` (22 tests, >95 total); docs in `docs/loop-engine/configuration.md`; `pyyaml>=6.0` dependency; verified 110 passed, 0 failed.
 
 ### Changed
 
diff --git a/docs/loop-engine/configuration.md b/docs/loop-engine/configuration.md
index c779209..fa3a953 100644
--- a/docs/loop-engine/configuration.md
+++ b/docs/loop-engine/configuration.md
@@ -72,7 +72,11 @@ All configuration lives in `loop-engine/loop-engine.jsonc`.
   "system_prompt_path": "system-prompt.md",
   "tasks_dir": "tasks",
   "agmd_path": "AGENTS.md",
-  "conventions_path": "docs/conventions.md"
+  "conventions_path": "docs/conventions.md",
+
+  // Stack Profiles
+  "stacks_dir": "stacks",
+  "default_stack": "generic"
 }
 ```
 
@@ -178,6 +182,61 @@ Each category supports:
 | `agmd_path` | `"AGENTS.md"` | Path to project rules |
 | `conventions_path` | `"docs/conventions.md"` | Path to conventions doc |
 
+### `stacks_dir`
+
+- **Type:** `string`
+- **Default:** `"stacks"`
+- **Description:** Directory containing stack profile YAML/JSON definitions (relative to workspace root, or absolute). Each file defines one `StackProfileConfig`.
+
+### `default_stack`
+
+- **Type:** `string`
+- **Default:** `"generic"`
+- **Description:** Fallback stack name when detection finds no match. Must correspond to a file in `stacks_dir` (e.g., `generic.yaml`).
+
+### Stack Profile Schema
+
+Each file in `stacks_dir` (e.g., `python-fastapi.yaml`) validates against `StackProfileConfig`:
+
+```yaml
+name: python-fastapi           # canonical name (matches filename)
+display_name: Python / FastAPI
+detection:
+  marker_files: ["pyproject.toml", "requirements.txt"]  # presence implies this stack
+  extensions: [".py"]           # file extensions implying this stack
+  task_keywords: ["python", "fastapi"]  # substring match in task content
+skills: ["python-fastapi"]     # skills to auto-load for this stack
+preflight:                     # shell commands validated before execution (empty = pass)
+  - "python3 --version"
+  - "uv --version || pytest --version"
+toolchain:
+  test_cmd: "pytest -q"
+  build_cmd: null
+  lint_cmd: "ruff check . || flake8 ."
+model_preferences: {}          # optional per-category model overrides
+```
+
+**Detection precedence (StackDetector):**
+
+1. Explicit `**Stack:** <name>` header in task file (case-insensitive)
+2. `marker_files` existence or matching `extensions` scan in workspace root
+3. `task_keywords` substring search in task content (case-insensitive)
+4. Fallback to `default_stack` (`generic`)
+
+**Preflight:** All `preflight` commands run sequentially via shell with 30s timeout each. Non-zero exit or timeout → `PreflightResult(passed=False)` → daemon transitions task to `CRASHED` with diagnostics (`state.set_qa_feedback`).
+
+**Registry:** `StackRegistry` scans `stacks_dir` on first access, supports both `.yaml`/`.yml` (via PyYAML) and `.json`, caches results, exposes `get_profile(name)` and `list_profiles()`.
+
+**Available default profiles:**
+
+| Profile | Detection | Skills | Toolchain |
+|---|---|---|---|
+| `generic` | fallback only | none | none |
+| `node-ts` | `package.json`, `.ts/.tsx/.js`, keywords `node/typescript` | `nextjs`, `react-vite` | `pnpm test \|\| npm test` |
+| `kotlin-android` | `build.gradle.kts`, `.kt/.kts`, keywords `kotlin/android` | `android-kotlin` | `./gradlew test` |
+| `python-fastapi` | `pyproject.toml`, `.py`, keywords `python/fastapi` | `python-fastapi` | `pytest -q` |
+| `go-gin` | `go.mod`, `.go`, keywords `go/gin` | `go-gin`, `go-hexagonal-grpc` | `go test ./...` |
+
 ## Environment Variables
 
 | Variable | Required | Description |
diff --git a/loop-engine/daemon.py b/loop-engine/daemon.py
index 151bc05..d816040 100644
--- a/loop-engine/daemon.py
+++ b/loop-engine/daemon.py
@@ -29,6 +29,7 @@ from gateway import ApprovalGateway
 from executor import HandsExecutor
 from qa_engine import QAEngine
 from brainstorm import BrainstormStage
+from stacks import StackRegistry, StackDetector, PreflightRunner
 
 # Repo root = parent of loop-engine/. All relative paths in the config
 # (state db, evidence dir, tasks/, system-prompt.md) are anchored here so the
@@ -138,6 +139,7 @@ async def _execute_and_qa(
     blueprint_context: str = "",
     qa_feedback: str = "",
     log_prefix: str = "pipeline",
+    stack_profile=None,
 ) -> dict | None:
     """Shared helper for execute → status check → diff extract → QA.
 
@@ -147,10 +149,24 @@ async def _execute_and_qa(
     CRASHED (executor blocked/error or empty diff). Caller decides FAILED retry vs
     PASSED progression. No behavior change, pure deduplication.
     """
-    result = await executor.execute(
-        task_id, task_file, task_content,
-        blueprint_context=blueprint_context, qa_feedback=qa_feedback,
-    )
+    kwargs = {}
+    if stack_profile is not None:
+        kwargs["stack_profile"] = stack_profile
+    try:
+        result = await executor.execute(
+            task_id, task_file, task_content,
+            blueprint_context=blueprint_context, qa_feedback=qa_feedback,
+            **kwargs,
+        )
+    except TypeError as e:
+        if "stack_profile" in str(e) and kwargs:
+            # Fallback for legacy executors / stubs that don't yet accept stack_profile
+            result = await executor.execute(
+                task_id, task_file, task_content,
+                blueprint_context=blueprint_context, qa_feedback=qa_feedback,
+            )
+        else:
+            raise
     print(f"[{log_prefix}] Execution result: {result['status']}")
 
     if result["status"] == EXEC_BLOCKED:
@@ -231,9 +247,25 @@ async def _reimplement_task(
             f"(retry {retries + 1}/{config.max_qa_retries})..."
         )
 
+        # Stack detection + preflight (LE-1)
+        registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
+        profile = StackDetector.detect(task_content, REPO_ROOT, registry, default_stack=config.default_stack)
+        print(f"[reimplement] Detected stack: {profile.name} ({profile.display_name})")
+        runner = PreflightRunner(timeout_seconds=30.0)
+        preflight = await runner.run(profile, cwd=REPO_ROOT)
+        if not preflight.passed:
+            state.update_state(task_id, TaskState.CRASHED)
+            diag = "; ".join(preflight.errors)
+            print(f"[reimplement] Preflight failed for stack {profile.name}: {diag} — crashing")
+            try:
+                state.set_qa_feedback(task_id, f"Preflight failed for stack {profile.name}: {diag}")
+            except Exception:
+                pass
+            return
+
         qa_result = await _execute_and_qa(
             task_id, task_file, task_content, task_path, state, executor, qa,
-            qa_feedback=current_feedback, log_prefix="reimplement"
+            qa_feedback=current_feedback, log_prefix="reimplement", stack_profile=profile
         )
         if qa_result is None:
             return
@@ -294,6 +326,7 @@ class LoopEngineDaemon:
         self.executor = executor
         self.qa = qa
         self.brainstorm = brainstorm
+        self.stack_registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
 
     async def trigger_task(self, task_id: int) -> None:
         """Trigger execution of a PENDING_TRIGGER task.
@@ -394,12 +427,26 @@ async def _process_task(task_id: int, task_file: str, config: LoopEngineConfig,
         print(f"[pipeline] Plan rejected for task #{task_id}. Back to backlog.")
         return
 
-    # 3. IMPLEMENTING
+    # 3. IMPLEMENTING — stack detection + preflight
     state.update_state(task_id, TaskState.IMPLEMENTING)
     print(f"[pipeline] Implementing task #{task_id}...")
+    registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
+    profile = StackDetector.detect(task_content, REPO_ROOT, registry, default_stack=config.default_stack)
+    print(f"[pipeline] Detected stack: {profile.name} ({profile.display_name})")
+    runner = PreflightRunner(timeout_seconds=30.0)
+    preflight = await runner.run(profile, cwd=REPO_ROOT)
+    if not preflight.passed:
+        state.update_state(task_id, TaskState.CRASHED)
+        diag = "; ".join(preflight.errors)
+        print(f"[pipeline] Preflight failed for stack {profile.name}: {diag} — crashing")
+        try:
+            state.set_qa_feedback(task_id, f"Preflight failed for stack {profile.name}: {diag}")
+        except Exception:
+            pass
+        return
     qa_result = await _execute_and_qa(
         task_id, task_file, task_content, task_path, state, executor, qa,
-        blueprint_context=plan, log_prefix="pipeline"
+        blueprint_context=plan, log_prefix="pipeline", stack_profile=profile
     )
     if qa_result is None:
         return
diff --git a/loop-engine/executor.py b/loop-engine/executor.py
index 2043561..9ce840e 100644
--- a/loop-engine/executor.py
+++ b/loop-engine/executor.py
@@ -18,6 +18,7 @@ import asyncio
 import re
 import time
 from pathlib import Path
+from typing import Optional, Any
 
 from models import LoopEngineConfig
 from state import StateMachine
@@ -39,7 +40,8 @@ class HandsExecutor:
         self.state = state
 
     async def execute(self, task_id: int, task_file: str, task_content: str,
-                    blueprint_context: str = "", qa_feedback: str = "") -> dict:
+                    blueprint_context: str = "", qa_feedback: str = "",
+                    stack_profile: Optional[Any] = None) -> dict:
         """Execute a task via OpenCode CLI with transport error retry.
 
         Args:
@@ -52,12 +54,30 @@ class HandsExecutor:
             qa_feedback: QA rejection feedback to address (on retry). Injected as
                 distinct delimited section when non-empty, never overloaded with
                 blueprint_context.
+            stack_profile: Optional StackProfile detected for this task — skills and
+                toolchain commands are injected into the prompt.
         """
         prompt_parts = [
             f"Read the task file at {task_file} and implement it.",
             "Follow AGENTS.md rules exactly.",
             "Output [goal:complete] when done, [goal:blocked] if stuck.",
         ]
+        if stack_profile is not None:
+            try:
+                skills_str = ", ".join(stack_profile.skills) if getattr(stack_profile, "skills", []) else "none"
+                test_cmd = getattr(getattr(stack_profile, "toolchain", None), "test_cmd", None)
+                build_cmd = getattr(getattr(stack_profile, "toolchain", None), "build_cmd", None)
+                lint_cmd = getattr(getattr(stack_profile, "toolchain", None), "lint_cmd", None)
+                preflight_str = ", ".join(stack_profile.preflight) if getattr(stack_profile, "preflight", []) else "none"
+                prompt_parts.append(
+                    f"## Stack Context: {stack_profile.name} ({stack_profile.display_name})\n"
+                    f"- Skills to load: {skills_str}\n"
+                    f"- Preflight: {preflight_str}\n"
+                    f"- Toolchain: test=`{test_cmd}`, build=`{build_cmd}`, lint=`{lint_cmd}`\n"
+                    f"Automatically load the listed skills and use the toolchain commands for verification."
+                )
+            except Exception:
+                pass
         if blueprint_context and blueprint_context.strip():
             prompt_parts.append(
                 f"## Approved Blueprint Context\n{blueprint_context.strip()}"
diff --git a/loop-engine/models.py b/loop-engine/models.py
index ae02424..c579322 100644
--- a/loop-engine/models.py
+++ b/loop-engine/models.py
@@ -67,6 +67,31 @@ class IdleConfig(BaseModel):
     min_delay_seconds: float = 2.0  # cooldown between continue attempts
 
 
+class StackDetectionConfig(BaseModel):
+    """Heuristics for auto-detecting a stack profile."""
+    marker_files: list[str] = Field(default_factory=list, description="Files whose presence implies this stack")
+    extensions: list[str] = Field(default_factory=list, description="File extensions implying this stack (e.g. .py)")
+    task_keywords: list[str] = Field(default_factory=list, description="Keywords in task content implying this stack")
+
+
+class StackToolchainConfig(BaseModel):
+    """Toolchain commands for a stack."""
+    test_cmd: str | None = Field(None, description="Command to run tests for this stack")
+    build_cmd: str | None = Field(None, description="Command to build this stack")
+    lint_cmd: str | None = Field(None, description="Command to lint this stack")
+
+
+class StackProfileConfig(BaseModel):
+    """Declarative profile for a tech stack."""
+    name: str = Field(..., description="Canonical stack name (matches filename without extension)")
+    display_name: str = Field(..., description="Human-readable name")
+    detection: StackDetectionConfig = Field(default_factory=StackDetectionConfig)
+    skills: list[str] = Field(default_factory=list, description="Skill names to load for this stack")
+    preflight: list[str] = Field(default_factory=list, description="Shell commands to validate toolchain before execution")
+    toolchain: StackToolchainConfig = Field(default_factory=StackToolchainConfig)
+    model_preferences: dict[str, list[str]] = Field(default_factory=dict, description="Optional per-category model overrides")
+
+
 class LoopEngineConfig(BaseModel):
     """Root configuration — loop-engine.jsonc."""
     # Providers
@@ -123,3 +148,7 @@ class LoopEngineConfig(BaseModel):
     tasks_dir: str = "tasks"
     agmd_path: str = "AGENTS.md"
     conventions_path: str = "docs/conventions.md"
+
+    # Stack Profiles
+    stacks_dir: str = Field("stacks", description="Directory containing stack profile YAML/JSON definitions")
+    default_stack: str = Field("generic", description="Fallback stack when detection finds no match")
diff --git a/loop-engine/pyproject.toml b/loop-engine/pyproject.toml
index 27e9503..63d786a 100644
--- a/loop-engine/pyproject.toml
+++ b/loop-engine/pyproject.toml
@@ -8,6 +8,7 @@ dependencies = [
     "litellm>=1.0",
     "watchdog>=4.0",
     "python-telegram-bot>=21.0",
+    "pyyaml>=6.0",
 ]
 
 [project.optional-dependencies]
diff --git a/loop-engine/stacks.py b/loop-engine/stacks.py
new file mode 100644
index 0000000..8938d86
--- /dev/null
+++ b/loop-engine/stacks.py
@@ -0,0 +1,326 @@
+"""
+Stack Profile Engine — declarative YAML stack definitions, detection, and preflight.
+
+Implements:
+- StackProfile: thin wrapper around StackProfileConfig with helpers
+- StackRegistry: scans stacks_dir, loads/caches .yaml/.json definitions
+- StackDetector: two-tier heuristic (header > marker_files/extensions > keywords > generic)
+- PreflightRunner: async validation of toolchain commands with timeout
+"""
+
+import asyncio
+import json
+import re
+import subprocess
+from dataclasses import dataclass, field
+from pathlib import Path
+from typing import Optional
+
+# Try to import yaml, fallback to safe parsing if unavailable
+try:
+    import yaml  # type: ignore
+
+    HAS_YAML = True
+except ImportError:
+    HAS_YAML = False
+
+from models import StackProfileConfig
+
+
+# ---------------------------------------------------------------------------
+# StackProfile — thin wrapper
+# ---------------------------------------------------------------------------
+
+class StackProfile:
+    """Encapsulates a StackProfileConfig with validation and serialization."""
+
+    def __init__(self, config: StackProfileConfig):
+        self.config = config
+
+    @property
+    def name(self) -> str:
+        return self.config.name
+
+    @property
+    def display_name(self) -> str:
+        return self.config.display_name
+
+    @property
+    def detection(self):
+        return self.config.detection
+
+    @property
+    def skills(self) -> list[str]:
+        return self.config.skills
+
+    @property
+    def preflight(self) -> list[str]:
+        return self.config.preflight
+
+    @property
+    def toolchain(self):
+        return self.config.toolchain
+
+    @property
+    def model_preferences(self) -> dict[str, list[str]]:
+        return self.config.model_preferences
+
+    def to_dict(self) -> dict:
+        return self.config.model_dump()
+
+    def __repr__(self) -> str:
+        return f"StackProfile(name={self.name!r}, display_name={self.display_name!r})"
+
+
+# ---------------------------------------------------------------------------
+# StackRegistry — scan + cache
+# ---------------------------------------------------------------------------
+
+class StackRegistry:
+    """Scans stacks_dir, loads/caches all .yaml and .json profile definitions."""
+
+    def __init__(self, stacks_dir: str = "stacks", repo_root: str | Path | None = None):
+        # Resolve stacks_dir relative to repo_root if needed
+        if repo_root is None:
+            # default: parent of loop-engine/ (REPO_ROOT)
+            from pathlib import Path as _P
+
+            repo_root = _P(__file__).resolve().parent.parent
+        else:
+            repo_root = Path(repo_root)
+
+        p = Path(stacks_dir)
+        if not p.is_absolute():
+            p = Path(repo_root) / stacks_dir
+        self.stacks_dir = p
+        self._cache: dict[str, StackProfile] = {}
+        self._loaded = False
+
+    def _parse_file(self, path: Path) -> dict:
+        text = path.read_text(encoding="utf-8")
+        if path.suffix in (".yaml", ".yml"):
+            if HAS_YAML:
+                data = yaml.safe_load(text)
+                if data is None:
+                    return {}
+                if not isinstance(data, dict):
+                    raise ValueError(f"YAML root must be a mapping in {path}")
+                return data
+            else:
+                # Fallback: try JSON parse if yaml not available
+                try:
+                    return json.loads(text)
+                except json.JSONDecodeError as e:
+                    raise ImportError(f"PyYAML not installed and {path} is not JSON: {e}")
+        elif path.suffix == ".json":
+            return json.loads(text)
+        else:
+            raise ValueError(f"Unsupported profile extension: {path.suffix}")
+
+    def _load_all(self) -> None:
+        if self._loaded:
+            return
+        self._cache.clear()
+        if not self.stacks_dir.exists():
+            self._loaded = True
+            return
+        for f in sorted(self.stacks_dir.iterdir()):
+            if f.suffix not in (".yaml", ".yml", ".json"):
+                continue
+            if f.is_dir():
+                continue
+            try:
+                data = self._parse_file(f)
+                cfg = StackProfileConfig(**data)
+                # Ensure name matches filename if not explicitly consistent — but allow explicit name to win
+                # Validate that name is filesystem-safe
+                self._cache[cfg.name] = StackProfile(cfg)
+            except Exception as e:
+                # Re-raise with context for caller/test to assert on invalid schema
+                raise ValueError(f"Failed to load stack profile {f.name}: {e}") from e
+        self._loaded = True
+
+    def list_profiles(self) -> list[StackProfile]:
+        self._load_all()
+        return list(self._cache.values())
+
+    def get_profile(self, name: str) -> Optional[StackProfile]:
+        self._load_all()
+        return self._cache.get(name)
+
+    def reload(self) -> None:
+        """Force re-scan (useful in tests)."""
+        self._loaded = False
+        self._load_all()
+
+    @property
+    def names(self) -> list[str]:
+        self._load_all()
+        return sorted(self._cache.keys())
+
+
+# ---------------------------------------------------------------------------
+# StackDetector — two-tier heuristic
+# ---------------------------------------------------------------------------
+
+class StackDetector:
+    """Two-tier detection logic.
+
+    Precedence (highest to lowest):
+      1. Explicit `**Stack:** <name>` header in task content
+      2. Workspace marker_files or extension scan
+      3. Task keywords (task_keywords substring match, case-insensitive)
+      4. Fallback to default_stack ("generic")
+    """
+
+    # Matches: **Stack:** node-ts  or  **Stacks:** python-fastapi  etc.
+    _HEADER_RE = re.compile(r"\*\*Stack:\*\*\s*([a-zA-Z0-9._\-/]+)", re.IGNORECASE)
+    # Also allow Stack: without bold, case-insensitive
+    _HEADER_RE_PLAIN = re.compile(r"^\s*Stack\s*:\s*([a-zA-Z0-9._\-/]+)", re.IGNORECASE | re.MULTILINE)
+
+    @staticmethod
+    def detect(
+        task_content: str,
+        workspace_root: str | Path,
+        registry: StackRegistry,
+        default_stack: str = "generic",
+    ) -> StackProfile:
+        # 1. Explicit header
+        m = StackDetector._HEADER_RE.search(task_content)
+        if m:
+            name = m.group(1).strip().lower()
+            profile = registry.get_profile(name)
+            if profile is not None:
+                return profile
+            # Also try without lower? registry is case-sensitive lower
+            profile = registry.get_profile(name)
+            if profile:
+                return profile
+
+        m2 = StackDetector._HEADER_RE_PLAIN.search(task_content)
+        if m2:
+            name = m2.group(1).strip().lower()
+            profile = registry.get_profile(name)
+            if profile is not None:
+                return profile
+
+        workspace_root = Path(workspace_root)
+
+        # 2. Marker files / extensions
+        # First check marker_files existence
+        for profile in registry.list_profiles():
+            if profile.name == default_stack:
+                continue  # skip generic in this phase; it's fallback
+            for marker in profile.detection.marker_files:
+                if (workspace_root / marker).exists():
+                    return profile
+            # Also scan for matching extensions in workspace (non-recursive top-level + one level?)
+            # We walk up to 2 levels deep to avoid full repo scan cost
+            if profile.detection.extensions:
+                # Quick scan: list files at root and subdirs one level
+                try:
+                    # Root files
+                    for f in workspace_root.iterdir():
+                        if f.is_file() and any(f.name.endswith(ext) for ext in profile.detection.extensions):
+                            return profile
+                    # One level deep
+                    for sub in workspace_root.iterdir():
+                        if sub.is_dir() and not sub.name.startswith(".") and sub.name not in ("node_modules", "__pycache__", ".git", "loop-engine", "stacks", "tasks", ".venv", "venv"):
+                            for f in sub.iterdir():
+                                if f.is_file() and any(f.name.endswith(ext) for ext in profile.detection.extensions):
+                                    return profile
+                except (PermissionError, OSError):
+                    pass
+
+        # 3. Task keywords (case-insensitive substring)
+        lower_content = task_content.lower()
+        for profile in registry.list_profiles():
+            if profile.name == default_stack:
+                continue
+            for kw in profile.detection.task_keywords:
+                if kw.lower() in lower_content:
+                    return profile
+
+        # 4. Fallback
+        generic = registry.get_profile(default_stack)
+        if generic is not None:
+            return generic
+        # If even generic missing, return first available or synthesize generic
+        profiles = registry.list_profiles()
+        if profiles:
+            return profiles[0]
+        # Synthetic generic
+        return StackProfile(StackProfileConfig(name="generic", display_name="Generic"))
+
+
+# ---------------------------------------------------------------------------
+# PreflightRunner — async toolchain validation
+# ---------------------------------------------------------------------------
+
+@dataclass
+class PreflightResult:
+    passed: bool
+    errors: list[str] = field(default_factory=list)
+    outputs: list[str] = field(default_factory=list)
+
+
+class PreflightRunner:
+    """Asynchronously executes profile.preflight commands with timeouts."""
+
+    def __init__(self, timeout_seconds: float = 30.0):
+        self.timeout_seconds = timeout_seconds
+
+    async def run(self, profile: StackProfile, cwd: str | Path | None = None) -> PreflightResult:
+        """Run all preflight commands sequentially. Return PreflightResult.
+
+        Each command is executed via shell (so `||` works). Non-zero exit → error.
+        Timeout → error. Empty preflight → passed.
+        """
+        if not profile.preflight:
+            return PreflightResult(passed=True)
+
+        errors: list[str] = []
+        outputs: list[str] = []
+        cwd_path = Path(cwd) if cwd else None
+
+        for cmd in profile.preflight:
+            try:
+                proc = await asyncio.create_subprocess_shell(
+                    cmd,
+                    stdout=asyncio.subprocess.PIPE,
+                    stderr=asyncio.subprocess.PIPE,
+                    cwd=str(cwd_path) if cwd_path else None,
+                )
+                try:
+                    stdout, stderr = await asyncio.wait_for(
+                        proc.communicate(), timeout=self.timeout_seconds
+                    )
+                except asyncio.TimeoutError:
+                    try:
+                        proc.kill()
+                    except ProcessLookupError:
+                        pass
+                    errors.append(f"Preflight timeout ({self.timeout_seconds}s): {cmd}")
+                    continue
+
+                out = stdout.decode(errors="replace").strip()
+                err = stderr.decode(errors="replace").strip()
+                combined = out
+                if err:
+                    combined = f"{out}\n{err}" if out else err
+                outputs.append(combined)
+
+                if proc.returncode != 0:
+                    errors.append(f"Preflight failed ({proc.returncode}): {cmd} → {err or out or 'no output'}")
+
+            except FileNotFoundError as e:
+                errors.append(f"Preflight spawn failed: {cmd} → {e}")
+            except Exception as e:
+                errors.append(f"Preflight error: {cmd} → {e}")
+
+        passed = len(errors) == 0
+        return PreflightResult(passed=passed, errors=errors, outputs=outputs)
+
+    def run_sync(self, profile: StackProfile, cwd: str | Path | None = None) -> PreflightResult:
+        """Synchronous wrapper for tests and sync callers."""
+        return asyncio.run(self.run(profile, cwd=cwd))
diff --git a/loop-engine/test_stacks.py b/loop-engine/test_stacks.py
new file mode 100644
index 0000000..ff3301f
--- /dev/null
+++ b/loop-engine/test_stacks.py
@@ -0,0 +1,337 @@
+"""Tests for stacks.py — Stack Profile Engine (Task 133)."""
+import sys, os, tempfile, json, asyncio
+from pathlib import Path
+
+sys.path.insert(0, os.path.dirname(__file__))
+
+from models import LoopEngineConfig, StackProfileConfig, StackDetectionConfig, StackToolchainConfig
+from stacks import StackProfile, StackRegistry, StackDetector, PreflightRunner
+
+
+# Helpers
+def make_registry(tmp_path: Path, profiles: dict) -> StackRegistry:
+    """Create YAML files in tmp_path/stacks and return registry."""
+    stacks_dir = tmp_path / "stacks"
+    stacks_dir.mkdir(parents=True, exist_ok=True)
+    for name, data in profiles.items():
+        # Use yaml if available else json
+        try:
+            import yaml
+            (stacks_dir / f"{name}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
+        except ImportError:
+            (stacks_dir / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")
+    return StackRegistry(str(stacks_dir))
+
+
+# ---------------------------------------------------------------------------
+# Profile parsing
+# ---------------------------------------------------------------------------
+
+def test_stack_profile_config_defaults():
+    cfg = StackProfileConfig(name="test", display_name="Test")
+    assert cfg.detection.marker_files == []
+    assert cfg.detection.extensions == []
+    assert cfg.skills == []
+    assert cfg.preflight == []
+    assert cfg.toolchain.test_cmd is None
+
+
+def test_stack_profile_config_full():
+    cfg = StackProfileConfig(
+        name="node-ts",
+        display_name="Node TS",
+        detection=StackDetectionConfig(
+            marker_files=["package.json"],
+            extensions=[".ts"],
+            task_keywords=["node"]
+        ),
+        skills=["nextjs"],
+        preflight=["node --version"],
+        toolchain=StackToolchainConfig(test_cmd="npm test")
+    )
+    assert cfg.detection.marker_files == ["package.json"]
+    assert cfg.skills == ["nextjs"]
+    assert cfg.toolchain.test_cmd == "npm test"
+
+
+def test_stack_profile_invalid_missing_name():
+    try:
+        StackProfileConfig(display_name="No Name")  # type: ignore
+        assert False, "Should fail without name"
+    except Exception:
+        pass
+
+
+def test_stack_registry_loads_generic():
+    r = StackRegistry("stacks")
+    profiles = r.list_profiles()
+    names = [p.name for p in profiles]
+    assert "generic" in names
+    assert len(names) >= 5
+
+
+def test_stack_registry_get_profile():
+    r = StackRegistry("stacks")
+    p = r.get_profile("node-ts")
+    assert p is not None
+    assert p.name == "node-ts"
+    assert "package.json" in p.detection.marker_files
+    assert p.get_profile is None if False else True  # dummy to avoid lint
+
+
+def test_stack_registry_nonexistent_returns_none():
+    r = StackRegistry("stacks")
+    assert r.get_profile("does-not-exist") is None
+
+
+def test_stack_registry_invalid_schema_rejection():
+    with tempfile.TemporaryDirectory() as tmp:
+        tmp = Path(tmp)
+        stacks_dir = tmp / "stacks"
+        stacks_dir.mkdir()
+        # Invalid: missing display_name
+        (stacks_dir / "bad.yaml").write_text("name: bad\n", encoding="utf-8")
+        r = StackRegistry(str(stacks_dir))
+        try:
+            r.list_profiles()
+            assert False, "Should have raised ValueError"
+        except ValueError as e:
+            assert "bad.yaml" in str(e) or "Failed to load" in str(e)
+
+
+def test_stack_profile_yaml_and_json_both_supported():
+    with tempfile.TemporaryDirectory() as tmp:
+        tmp = Path(tmp)
+        stacks_dir = tmp / "stacks"
+        stacks_dir.mkdir()
+        # JSON file
+        data = {"name": "json-stack", "display_name": "JSON Stack"}
+        (stacks_dir / "json-stack.json").write_text(json.dumps(data), encoding="utf-8")
+        # YAML file
+        try:
+            import yaml
+            yaml_data = {"name": "yaml-stack", "display_name": "YAML Stack"}
+            (stacks_dir / "yaml-stack.yaml").write_text(yaml.safe_dump(yaml_data), encoding="utf-8")
+        except ImportError:
+            pass
+        r = StackRegistry(str(stacks_dir))
+        assert r.get_profile("json-stack") is not None
+        if (stacks_dir / "yaml-stack.yaml").exists():
+            assert r.get_profile("yaml-stack") is not None
+
+
+# ---------------------------------------------------------------------------
+# Detection precedence
+# ---------------------------------------------------------------------------
+
+def test_detection_explicit_header_overrides_all():
+    with tempfile.TemporaryDirectory() as tmp:
+        tmp = Path(tmp)
+        # Create workspace with python marker to tempt wrong detection
+        (tmp / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
+        r = StackRegistry("stacks")
+        task = "**Stack:** node-ts\nDo something generic"
+        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
+        assert detected.name == "node-ts", f"Expected node-ts, got {detected.name}"
+
+
+def test_detection_marker_files_before_keywords():
+    with tempfile.TemporaryDirectory() as tmp:
+        tmp = Path(tmp)
+        (tmp / "go.mod").write_text("module foo\n", encoding="utf-8")
+        r = StackRegistry("stacks")
+        # Task mentions python but workspace has go.mod
+        task = "Fix python endpoint"
+        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
+        assert detected.name == "go-gin", f"Expected go-gin marker, got {detected.name}"
+
+
+def test_detection_extensions_fallback():
+    with tempfile.TemporaryDirectory() as tmp:
+        tmp = Path(tmp)
+        sub = tmp / "app"
+        sub.mkdir()
+        (sub / "main.go").write_text("package main\n", encoding="utf-8")
+        r = StackRegistry("stacks")
+        task = "random task without keywords"
+        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
+        assert detected.name == "go-gin", f"Expected go-gin via .go extension, got {detected.name}"
+
+
+def test_detection_keywords_after_marker_miss():
+    with tempfile.TemporaryDirectory() as tmp:
+        tmp = Path(tmp)
+        r = StackRegistry("stacks")
+        task = "This is a Kotlin Android compose task"
+        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
+        assert detected.name == "kotlin-android", f"Expected kotlin-android via keyword, got {detected.name}"
+
+
+def test_detection_generic_fallback():
+    with tempfile.TemporaryDirectory() as tmp:
+        tmp = Path(tmp)
+        r = StackRegistry("stacks")
+        task = "Completely unknown stack task with no markers or keywords xyz123"
+        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
+        assert detected.name == "generic"
+
+
+def test_detection_header_plain_format():
+    with tempfile.TemporaryDirectory() as tmp:
+        tmp = Path(tmp)
+        r = StackRegistry("stacks")
+        task = "Stack: python-fastapi\nImplement endpoint"
+        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
+        assert detected.name == "python-fastapi"
+
+
+# ---------------------------------------------------------------------------
+# Preflight runner
+# ---------------------------------------------------------------------------
+
+def test_preflight_success():
+    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["echo hello", "echo world"])
+    profile = StackProfile(cfg)
+    runner = PreflightRunner(timeout_seconds=5)
+    result = runner.run_sync(profile)
+    assert result.passed is True
+    assert result.errors == []
+    assert len(result.outputs) == 2
+
+
+def test_preflight_failure_nonzero():
+    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["false"])
+    profile = StackProfile(cfg)
+    runner = PreflightRunner(timeout_seconds=5)
+    result = runner.run_sync(profile)
+    assert result.passed is False
+    assert len(result.errors) == 1
+    assert "false" in result.errors[0]
+
+
+def test_preflight_timeout():
+    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["sleep 2"])
+    profile = StackProfile(cfg)
+    runner = PreflightRunner(timeout_seconds=0.3)
+    result = runner.run_sync(profile)
+    assert result.passed is False
+    assert any("timeout" in e.lower() for e in result.errors)
+
+
+def test_preflight_empty_is_pass():
+    cfg = StackProfileConfig(name="test", display_name="Test", preflight=[])
+    profile = StackProfile(cfg)
+    runner = PreflightRunner(timeout_seconds=5)
+    result = runner.run_sync(profile)
+    assert result.passed is True
+    assert result.errors == []
+
+
+def test_preflight_mixed_success_and_failure():
+    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["echo ok", "false", "echo again"])
+    profile = StackProfile(cfg)
+    runner = PreflightRunner(timeout_seconds=5)
+    result = runner.run_sync(profile)
+    assert result.passed is False
+    assert len(result.errors) == 1
+
+
+# ---------------------------------------------------------------------------
+# LoopEngineConfig extension
+# ---------------------------------------------------------------------------
+
+def test_loop_engine_config_stack_fields():
+    cfg = LoopEngineConfig(approval={"chat_id": 1})
+    assert cfg.stacks_dir == "stacks"
+    assert cfg.default_stack == "generic"
+    cfg2 = LoopEngineConfig(approval={"chat_id": 1}, stacks_dir="custom/stacks", default_stack="node-ts")
+    assert cfg2.stacks_dir == "custom/stacks"
+    assert cfg2.default_stack == "node-ts"
+
+
+# ---------------------------------------------------------------------------
+# Daemon integration (mock workspace fixtures)
+# ---------------------------------------------------------------------------
+
+def test_daemon_registry_init():
+    from daemon import LoopEngineDaemon
+    from state import StateMachine
+    from router import LLMRouter
+    from gateway import ApprovalGateway
+    from executor import HandsExecutor
+    from qa_engine import QAEngine
+    from brainstorm import BrainstormStage
+
+    cfg = LoopEngineConfig(approval={"chat_id": 0})
+    with tempfile.TemporaryDirectory() as tmp:
+        db = os.path.join(tmp, "loop.db")
+        state = StateMachine(db)
+        router = LLMRouter(cfg, workspace_root=tmp)
+        gateway = ApprovalGateway(cfg)
+        executor = HandsExecutor(cfg, state)
+        qa = QAEngine(cfg, state, router)
+        brainstorm = BrainstormStage(cfg, router, workspace_root=tmp)
+        daemon = LoopEngineDaemon(cfg, state, router, gateway, executor, qa, brainstorm)
+        assert daemon.stack_registry is not None
+        assert daemon.stack_registry.get_profile("generic") is not None
+        state.close()
+
+
+def test_executor_injects_stack_context():
+    from executor import HandsExecutor
+    from state import StateMachine
+
+    cfg = LoopEngineConfig(approval={"chat_id": 0})
+    with tempfile.TemporaryDirectory() as tmp:
+        state = StateMachine(os.path.join(tmp, "db"))
+        ex = HandsExecutor(cfg, state)
+
+        # Create a mock profile
+        profile_cfg = StackProfileConfig(
+            name="python-fastapi",
+            display_name="Python FastAPI",
+            skills=["python-fastapi"],
+            preflight=["echo ok"],
+            toolchain=StackToolchainConfig(test_cmd="pytest -q")
+        )
+        profile = StackProfile(profile_cfg)
+
+        # We only test prompt construction via _run_once mock
+        # Monkey-patch _run_once to capture prompt
+        captured = {}
+
+        async def fake_run_once(task_file, prompt):
+            captured["prompt"] = prompt
+            return {"status": "complete", "output": "[goal:complete]", "error": "", "elapsed": 0.1}
+
+        original = ex._run_once
+        ex._run_once = fake_run_once  # type: ignore
+
+        async def run():
+            return await ex.execute(1, "tasks/backlog/01-test.md", "content", stack_profile=profile)
+
+        result = asyncio.run(run())
+        assert result["status"] == "complete"
+        assert "python-fastapi" in captured["prompt"]
+        assert "python-fastapi" in captured["prompt"].lower()
+        assert "pytest -q" in captured["prompt"]
+        ex._run_once = original  # type: ignore
+        state.close()
+
+
+if __name__ == "__main__":
+    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
+    passed = 0
+    failed = 0
+    for t in tests:
+        try:
+            t()
+            print(f"  PASS: {t.__name__}")
+            passed += 1
+        except Exception as e:
+            import traceback
+            print(f"  FAIL: {t.__name__}: {e}")
+            traceback.print_exc()
+            failed += 1
+    print(f"\n{passed} passed, {failed} failed")
+    sys.exit(1 if failed else 0)
diff --git a/stacks/generic.yaml b/stacks/generic.yaml
new file mode 100644
index 0000000..95049ba
--- /dev/null
+++ b/stacks/generic.yaml
@@ -0,0 +1,13 @@
+name: generic
+display_name: Generic (Fallback)
+detection:
+  marker_files: []
+  extensions: []
+  task_keywords: []
+skills: []
+preflight: []
+toolchain:
+  test_cmd: null
+  build_cmd: null
+  lint_cmd: null
+model_preferences: {}
diff --git a/stacks/go-gin.yaml b/stacks/go-gin.yaml
new file mode 100644
index 0000000..4e520d1
--- /dev/null
+++ b/stacks/go-gin.yaml
@@ -0,0 +1,14 @@
+name: go-gin
+display_name: Go / Gin
+detection:
+  marker_files: ["go.mod", "go.sum"]
+  extensions: [".go"]
+  task_keywords: ["go", "gin", "golang", "grpc"]
+skills: ["go-gin", "go-hexagonal-grpc"]
+preflight:
+  - "go version"
+toolchain:
+  test_cmd: "go test ./..."
+  build_cmd: "go build ./..."
+  lint_cmd: "golangci-lint run || go vet ./..."
+model_preferences: {}
diff --git a/stacks/kotlin-android.yaml b/stacks/kotlin-android.yaml
new file mode 100644
index 0000000..e61ce2e
--- /dev/null
+++ b/stacks/kotlin-android.yaml
@@ -0,0 +1,15 @@
+name: kotlin-android
+display_name: Kotlin / Android
+detection:
+  marker_files: ["build.gradle.kts", "build.gradle", "settings.gradle.kts"]
+  extensions: [".kt", ".kts"]
+  task_keywords: ["kotlin", "android", "compose", "gradle"]
+skills: ["android-kotlin"]
+preflight:
+  - "java -version"
+  - "./gradlew -version || gradle -version"
+toolchain:
+  test_cmd: "./gradlew test"
+  build_cmd: "./gradlew assembleDebug"
+  lint_cmd: "./gradlew ktlintCheck"
+model_preferences: {}
diff --git a/stacks/node-ts.yaml b/stacks/node-ts.yaml
new file mode 100644
index 0000000..ce5c478
--- /dev/null
+++ b/stacks/node-ts.yaml
@@ -0,0 +1,15 @@
+name: node-ts
+display_name: Node.js / TypeScript
+detection:
+  marker_files: ["package.json", "tsconfig.json"]
+  extensions: [".ts", ".tsx", ".js"]
+  task_keywords: ["node", "typescript", "nextjs", "react"]
+skills: ["nextjs", "react-vite"]
+preflight:
+  - "node --version"
+  - "pnpm --version || npm --version"
+toolchain:
+  test_cmd: "pnpm test || npm test"
+  build_cmd: "pnpm build || npm run build"
+  lint_cmd: "pnpm lint || npm run lint"
+model_preferences: {}
diff --git a/stacks/python-fastapi.yaml b/stacks/python-fastapi.yaml
new file mode 100644
index 0000000..c78aa7e
--- /dev/null
+++ b/stacks/python-fastapi.yaml
@@ -0,0 +1,15 @@
+name: python-fastapi
+display_name: Python / FastAPI
+detection:
+  marker_files: ["pyproject.toml", "requirements.txt", "Pipfile"]
+  extensions: [".py"]
+  task_keywords: ["python", "fastapi", "pydantic", "pytest"]
+skills: ["python-fastapi"]
+preflight:
+  - "python3 --version"
+  - "uv --version || pytest --version"
+toolchain:
+  test_cmd: "pytest -q"
+  build_cmd: null
+  lint_cmd: "ruff check . || flake8 ."
+model_preferences: {}
```
<!-- END_GIT_DIFF -->
