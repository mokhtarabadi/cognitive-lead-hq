# Task 135: Stack-Aware LLM Router & Provider Model Mapping

**File:** `tasks/completed/135-stack-aware-llm-router-and-model-mapping.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Implement a stack-aware LLM router in `loop-engine/router.py` that resolves models through a 3-tier hierarchy (Stack-Preferred Models → Global Category Models → Global Default), propagate the detected stack profile through the daemon planning/QA/review pipeline, populate `model_preferences` in the four stack YAML profiles, extend the router test suite, and document the resolution hierarchy in `docs/loop-engine/configuration.md`.

## Blueprint Reference

Phase A / Task LE-3 — Stack-Aware LLM Router & Provider Model Mapping. Blueprint decisions D1–D5 recorded under `## Manager Decisions`.

## Manager's Notes

- Tier 1 (Stack-Preferred Models): consult `stack_profile.model_preferences` (or dict `.get("model_preferences")`), match `category` then wildcard `*`, verify `{PROVIDER}_API_KEY` env presence, return `(model, category.reasoning)`.
- Tier 2 (Global Category Models): existing category iteration fallback.
- Tier 3 (Global Default): `(default_provider, None)`.
- All routing helpers (`route_plan`, `route_qa`, `route_review`, `route_with_persona`) accept `stack_profile: Optional[Any] = None` and forward it.
- Daemon detects the stack once at the start of `_process_task` and propagates the profile into planning, QA, and review.
- Test suite must grow from 136 to >= 148 passing tests with 0 failures.

## Local TODOs

- [x] Initial codebase exploration
- [x] Initialize task file with canonical template (D1–D5, AC, DoD)
- [x] Implement 3-tier `_resolve_model` + stack_profile forwarding in `router.py`
- [x] Forward stack_profile in `qa_engine.py` run_qa/run_review
- [x] Move stack detection to start of `_process_task` and propagate profile in `daemon.py`
- [x] Populate `model_preferences` in 4 stack YAML profiles
- [x] Extend `test_router.py` with stack-aware routing tests
- [x] Document stack-aware routing in `docs/loop-engine/configuration.md`
- [x] Verify functionality (baseline 136 → >= 148 passed, 0 failed)

## Acceptance Criteria

- [x] `_resolve_model(category, stack_profile=None)` implements Tier 1 (stack-preferred models with env-key check), Tier 2 (category config fallback), Tier 3 (default provider)
- [x] `route_plan`, `route_qa`, `route_review`, `route_with_persona` accept and forward `stack_profile`
- [x] `QAEngine.run_qa` and `QAEngine.run_review` forward `stack_profile` to the router
- [x] `daemon._process_task` detects the stack before planning and propagates the profile into `route_plan`, `_execute_and_qa`, and `qa.run_review`; `_reimplement_task` forwards it to `qa.run_review`
- [x] `stacks/{kotlin-android,node-ts,python-fastapi,go-gin}.yaml` declare `model_preferences` per spec
- [x] `test_router.py` covers: preferred model with key, fallback when key missing, empty preferences, wildcard `*`, object and dict profiles, backward compatibility with `stack_profile=None`
- [x] Full suite passes with >= 148 tests, 0 failures
- [x] `docs/loop-engine/configuration.md` documents the stack-aware routing hierarchy

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** >= 148 passed, 0 failed
- **Actual result:** 148 passed, 0 failed (baseline 136 → +12 new tests in `test_router.py`)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

**[2026-08-31] [D1] [ORCHESTRATOR-DETECTED]:** Two-Tier Stack Model Resolution Hierarchy
- **Rationale:** Enabling stack profiles to declare preferred models per category allows specialized LLMs (e.g. Kotlin AST specialists vs TypeScript specialists) while maintaining transparent fallback to global category models when keys are absent.
- **Alternatives considered:** Hardcoding stack-to-model mappings inside `router.py`, or replacing category routing entirely with stack routing.
- **Impact:** Clean composition of stack context with cognitive categories; full backward compatibility when stack preferences are empty or unkeyed.

**[2026-08-31] [D2] [ORCHESTRATOR-DETECTED]:** Three-Tier Fallback Chain (Stack Preferences → Category Config → Default Provider)
- **Rationale:** Guarantees a model is always resolvable: stack-preferred models win when their provider key is present, otherwise the global category chain applies, and `default_provider` is the terminal fallback.
- **Alternatives considered:** Hard-failing when no stack key exists; single-tier routing that ignores stack context.
- **Impact:** Deterministic resolution in every environment state; no new failure modes for unkeyed providers.

**[2026-08-31] [D3] [ORCHESTRATOR-DETECTED]:** Single Stack Detection at Pipeline Start
- **Rationale:** Detecting the stack once at the beginning of `_process_task` (before planning) ensures planning, QA, and review all share one consistent profile for model routing, avoiding per-stage re-detection drift.
- **Alternatives considered:** Re-detecting the stack independently at each pipeline stage.
- **Impact:** One detection point, one preflight gate; profile propagates through `route_plan`, `_execute_and_qa`, and `qa.run_review`.

**[2026-08-31] [D4] [ORCHESTRATOR-DETECTED]:** Declarative `model_preferences` in Stack YAML
- **Rationale:** Stack-specific model choice is configuration, not code — new stacks declare preferred models per category without touching `router.py`.
- **Alternatives considered:** Hardcoding stack-to-model mappings inside `router.py`.
- **Impact:** Extensible stack catalog; `StackProfileConfig.model_preferences` already exists in `models.py` and is exposed via `StackProfile.model_preferences`.

**[2026-08-31] [D5] [ORCHESTRATOR-DETECTED]:** Backward-Compatible Optional `stack_profile` Parameter
- **Rationale:** All routing helpers and QA entry points accept `stack_profile: Optional[Any] = None`, so legacy routers, stubs, and existing callers keep working unchanged.
- **Alternatives considered:** Making `stack_profile` a required parameter.
- **Impact:** Zero breaking changes; TypeError fallback chains in `qa_engine.py` and `daemon.py` preserve compatibility with legacy signatures.

## Risk & Rollback

- **Risk:** Env-key collisions between stack-preferred and category models could route to an unexpected provider; daemon signature changes could break legacy callers.
- **Rollback plan:** Revert `router.py`, `qa_engine.py`, `daemon.py` to the pre-task state (git history); stack YAML `model_preferences` can be emptied back to `{}` without code changes; tests are additive and non-destructive.

---

## Execution Log & Reasoning

**Implementation (2026-08-31):**

1. **`loop-engine/router.py`** — `_resolve_model` upgraded to the 3-tier hierarchy:
   - **Tier 1 (Stack-Preferred):** accepts `stack_profile: Optional[Any] = None`; extracts `model_preferences` safely from either a `StackProfile` object (`getattr`) or a plain dict (`.get("model_preferences")`); matches exact `category` then wildcard `"*"`; iterates candidates in order, checking `os.environ["{PROVIDER}_API_KEY"]`; reasoning level sourced from the global category config (`categories[category].reasoning`, defaulting to `unspecified` then `None`).
   - **Tier 2 (Global Category):** unchanged existing fallback chain.
   - **Tier 3 (Global Default):** `(default_provider, None)`.
   - `route_plan`, `route_qa`, `route_review`, `route_with_persona` all accept `stack_profile: Optional[Any] = None` and forward it into `_resolve_model`. Added `Any` to typing imports.
2. **`loop-engine/qa_engine.py`** — `run_qa` and `run_review` accept `stack_profile: Optional[Any] = None` and forward it to `route_qa`/`route_review`; nested `TypeError` fallbacks preserve compatibility with legacy routers lacking `stack_profile` (and, for `run_qa`, lacking `toolchain_evidence`).
3. **`loop-engine/daemon.py`** — stack detection (`StackRegistry` + `StackDetector.detect`) moved to the start of `_process_task` (after reading `task_content`, before brainstorming/planning); the profile is forwarded into `route_plan(..., stack_profile=profile)` (with `TypeError` fallback for legacy routers/stubs), `_execute_and_qa(..., stack_profile=profile)` (already present), and `qa.run_review(..., stack_profile=profile)`; duplicate detection removed from the IMPLEMENTING section (preflight retained). `_reimplement_task` forwards `stack_profile=profile` into `qa.run_review`.
4. **`stacks/*.yaml`** — populated `model_preferences` for `kotlin-android`, `node-ts`, `python-fastapi`, `go-gin` per spec (deep/quick lists).
5. **`loop-engine/test_router.py`** — 12 new tests (9 → 21 collected): preferred model with env key; ordered Tier-1 fallback (first unkeyed → second keyed wins); Tier-2 category fallback when preferred key missing; empty `model_preferences`; wildcard `*`; dict-profile resolution; `route_plan`/`route_qa`/`route_review`/`route_with_persona` with stack profile objects; backward compatibility with `stack_profile=None` for `route_plan` and `route_qa`.
6. **`docs/loop-engine/configuration.md`** — new "Stack-Aware Model Routing (LE-3)" section documenting the 3-tier resolution hierarchy, daemon propagation, backward compatibility, and the default stack preferences table; schema example updated to show populated `model_preferences`.

**Verification:** baseline 136 passed → targeted `test_router.py` 21 passed → full suite **148 passed, 0 failed** (exit 0). One regression was caught and fixed during the run: `test_le0_fixes.py::test_daemon_empty_diff_crashes` failed because a legacy `StubRouter` lacks the `stack_profile` param — resolved with a `TypeError` fallback in `_process_task` (consistent with the existing `_execute_and_qa`/`qa_engine` pattern and D5). `git diff --stat` confirms changes are strictly scoped to `loop-engine/`, `stacks/`, `docs/loop-engine/`, and the task file.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 3ea0e96..ec3f28e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Stack-Aware LLM Router & Provider Model Mapping (Task 135)** — Added Stack-Aware LLM Router & Provider Model Mapping (`loop-engine/router.py`) with 3-tier resolution hierarchy (Stack Preferences → Category Config → Default Provider), daemon planning/QA/review propagation, and stack YAML model preferences. `_resolve_model(category, stack_profile=None)` consults `stack_profile.model_preferences` (object attribute or dict key, exact category then wildcard `*`, `{PROVIDER}_API_KEY` env check, reasoning from global category config) before falling back to the global category chain and `default_provider`; `route_plan`/`route_qa`/`route_review`/`route_with_persona` accept and forward `stack_profile`; `QAEngine.run_qa`/`run_review` forward it with `TypeError` fallbacks for legacy routers; `daemon._process_task` detects the stack once at pipeline start and propagates the profile into planning, `_execute_and_qa`, and review (`_reimplement_task` included); populated `model_preferences` in `stacks/{kotlin-android,node-ts,python-fastapi,go-gin}.yaml`; 12 new tests in `loop-engine/test_router.py` (preferred-with-key, ordered Tier-1 fallback, category fallback, empty prefs, wildcard, dict profile, all four route helpers, backward compat); documented the resolution hierarchy in `docs/loop-engine/configuration.md`; verified 148 passed, 0 failed (baseline 136).
 - **Auto-Generate Memory Index via MCP Memory Server (Task 127)** — implemented `build_memory_index()` and `rebuild_memory_index` MCP tool in `mcp-memory-server/server.py` — scans `MEMORY_DIR` for `*.md`, excludes `index.md`, parses frontmatter `tags` and first non-empty line as summary (clamped 120, pipe-escaped), builds sorted Markdown table `| Namespace | Key | Summary | Tags |`, writes atomically via `mkstemp` + `os.replace` + `fsync` dir, handles empty store, hooked into `store_memory`/`delete_memory` success paths; auto-generates `.opencode/memory/index.md` Phase 0 discovery integration; updated `skill-templates/project-memory/SKILL.md` (and mirrors `.opencode/skills/` + `~/.config/opencode/skills/`) with canonical index location and two-step workflow (read index → `read_memory`/`search_memory`); updated `agents/cognitive-executor.md` Context Bootstrapping to mandate reading `.opencode/memory/index.md` alongside `AGENTS.md`; updated `prompts/shared/validation-phase.md` to include `.opencode/memory/index.md` (graceful skip) and reassembled `system-prompt.md` (73242 bytes, 3 index references); added 5 tests in `tests/test_mcp_servers.py` (build on store, update on delete, empty, pipe-sanitize, rebuild tool) — 55 passed; generated initial `.opencode/memory/index.md` with 11 memories indexed; restored `docs/workflow-upgrade-v8.4.5.md` to fix pre-existing test failure.
 - **Fix Telegram Topic Filter Leak and Allowed Root Auto-Mkdir (Task 128)** — restored topic-scoped filtering in `skill-templates/telegram-issue-sync/SKILL.md` Phase 1 (client-filter `reply_to == config.topic_id` with chain walk via `telegram_get_message_context`, re-added `Forum Topic Targeting (Critical)` section, `458=Cognitive Lead` only), updated `docs/telegram-setup.md` §6 and §4.4 to document topic filter and auto-mkdir behavior; patched upstream `chigwell/telegram-mcp` `telegram_mcp/runtime.py:1813` to auto-`mkdir(parents=True, exist_ok=True)` missing allowed roots instead of `SystemExit` (fixes reboot crash `Allowed root does not exist: /tmp/telegram-mcp`, verified `rm -rf /tmp/telegram-mcp` → auto-creates and `Starting 2 Telegram client(s)`), and `telegram_mcp/tools/messages.py:1571` to add optional `topic_id` param to `get_history` for server-side `reply_to == topic_id` filtering (backwards compatible); forked to `mokhtarabadi/telegram-mcp` branch `fix/allowed-root-automkdir-and-topic-filter` (commit `f87cb08`), auto-created upstream issue https://github.com/chigwell/telegram-mcp/issues/200 and PR https://github.com/chigwell/telegram-mcp/pull/201; verified `grep -n reply_to.*topic_id` in skill, `grep -n Allowed root` shows mkdir fallback, and manual auto-mkdir test passes.
 - **Stack Profile Engine (Task 133)** — Added Stack Profile Engine (`loop-engine/stacks.py`) with declarative YAML schemas, two-tier detection, preflight toolchain validation, and default profiles for Node-TS, Kotlin-Android, Python-FastAPI, Go-Gin, and Generic stacks. Pydantic schemas `StackDetectionConfig`, `StackToolchainConfig`, `StackProfileConfig` plus `LoopEngineConfig.stacks_dir`/`default_stack` in `loop-engine/models.py`; `stacks/` YAML profiles (generic, node-ts, kotlin-android, python-fastapi, go-gin) with marker_files/extensions/skills/preflight/toolchain; `StackRegistry`/`StackDetector`/`PreflightRunner` with YAML/JSON safe parsing and timeout handling; daemon integration via `StackRegistry` init, detection (`**Stack:**` header > marker_files/extensions > keywords > generic) and preflight (CRASHED on failure) + executor `stack_profile` prompt injection; `loop-engine/test_stacks.py` (22 tests, >95 total); docs in `docs/loop-engine/configuration.md`; `pyyaml>=6.0` dependency; verified 110 passed, 0 failed.
diff --git a/docs/loop-engine/configuration.md b/docs/loop-engine/configuration.md
index ac4a958..2dda8f9 100644
--- a/docs/loop-engine/configuration.md
+++ b/docs/loop-engine/configuration.md
@@ -213,7 +213,9 @@ toolchain:
   test_cmd: "pytest -q"
   build_cmd: null
   lint_cmd: "ruff check . || flake8 ."
-model_preferences: {}          # optional per-category model overrides
+model_preferences:          # optional per-category model overrides (LE-3)
+  deep: ["openai/gpt-5.6-sol", "gemini/gemini-2.5-pro"]
+  quick: ["gemini/gemini-2.5-flash"]
 ```
 
 **Detection precedence (StackDetector):**
@@ -237,6 +239,47 @@ model_preferences: {}          # optional per-category model overrides
 | `python-fastapi` | `pyproject.toml`, `.py`, keywords `python/fastapi` | `python-fastapi` | `pytest -q` |
 | `go-gin` | `go.mod`, `.go`, keywords `go/gin` | `go-gin`, `go-hexagonal-grpc` | `go test ./...` |
 
+### Stack-Aware Model Routing (LE-3)
+
+`LLMRouter._resolve_model(category, stack_profile=None)` resolves the model for a
+call through a **3-tier hierarchy** — stack preferences win when their provider
+key is present, otherwise the global category chain applies, and
+`default_provider` is the terminal fallback:
+
+1. **Tier 1 — Stack-Preferred Models:** If a `stack_profile` is provided, its
+   `model_preferences` dict is consulted. The exact `category` key is matched
+   first, then the wildcard `"*"` key. For each candidate `provider/model` in
+   order, the router checks `os.environ["{PROVIDER}_API_KEY"]`; the first model
+   whose key is present wins. The reasoning level comes from the global category
+   config (`categories[category].reasoning`), not the stack.
+2. **Tier 2 — Global Category Models:** If no stack-preferred model is keyed
+   (empty preferences, no category/wildcard match, or no provider key), the
+   existing `categories[category].models` fallback chain is used.
+3. **Tier 3 — Global Default:** If no category model is keyed either, the router
+   returns `(default_provider, None)`.
+
+**Propagation:** The daemon detects the stack **once** at the start of
+`_process_task` (before planning) and forwards the resulting `StackProfile` into
+`router.route_plan(..., stack_profile=profile)`, `_execute_and_qa(...,
+stack_profile=profile)`, and `qa.run_review(..., stack_profile=profile)`.
+`_reimplement_task` forwards it into `qa.run_review` as well. `QAEngine.run_qa`
+and `QAEngine.run_review` accept `stack_profile` and forward it to the router
+(with `TypeError` fallbacks for legacy router signatures).
+
+**Backward compatibility:** `stack_profile` is optional everywhere
+(`Optional[Any] = None`). When omitted, resolution behaves exactly as before
+(Tier 2 → Tier 3). Both `StackProfile` objects (`.model_preferences` attribute)
+and plain dicts (`{"model_preferences": {...}}`) are accepted.
+
+**Default stack preferences:**
+
+| Stack | `deep` | `quick` |
+|---|---|---|
+| `kotlin-android` | `anthropic/claude-3-7-sonnet`, `openai/gpt-5.6-sol` | `gemini/gemini-2.5-flash` |
+| `node-ts` | `openai/gpt-5.6-sol`, `anthropic/claude-3-7-sonnet` | `kimi/kimi-k3` |
+| `python-fastapi` | `openai/gpt-5.6-sol`, `gemini/gemini-2.5-pro` | `gemini/gemini-2.5-flash` |
+| `go-gin` | `openai/gpt-5.6-sol`, `anthropic/claude-3-7-sonnet` | `gemini/gemini-2.5-flash` |
+
 ### Toolchain Verification (LE-2)
 
 `loop-engine/verifier.py` executes each profile's `toolchain` deterministically **after** Hands produce a git diff and **before** LLM QA, providing fail-fast short-circuiting and factual evidence.
diff --git a/loop-engine/daemon.py b/loop-engine/daemon.py
index b7adb60..6962fd9 100644
--- a/loop-engine/daemon.py
+++ b/loop-engine/daemon.py
@@ -331,7 +331,8 @@ async def _reimplement_task(
 
         # QA PASSED — proceed to REVIEW and CLOSURE (mirrors main pipeline steps 5-6)
         state.update_state(task_id, TaskState.REVIEW)
-        review = qa.run_review(task_id, task_content, qa_result.get("report", ""))
+        review = qa.run_review(task_id, task_content, qa_result.get("report", ""),
+                               stack_profile=profile)
         print(f"[reimplement] Review result: {review['result']}")
 
         if review["result"] == "REJECTED":
@@ -448,6 +449,12 @@ async def _process_task(task_id: int, task_file: str, config: LoopEngineConfig,
     task_path = Path(task_file)
     task_content = task_path.read_text(encoding="utf-8")
 
+    # Stack detection (LE-1) — detect once at the start so planning, QA, and
+    # review all share the same profile for stack-aware model routing (LE-3).
+    registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
+    profile = StackDetector.detect(task_content, REPO_ROOT, registry, default_stack=config.default_stack)
+    print(f"[pipeline] Detected stack: {profile.name} ({profile.display_name})")
+
     # 0. BRAINSTORMING (Phase 1.5) — optional pre-planning stage
     extra_context = ""
     if brainstorm.should_trigger(task_content):
@@ -467,7 +474,12 @@ async def _process_task(task_id: int, task_file: str, config: LoopEngineConfig,
     # 1. PLANNING
     state.update_state(task_id, TaskState.PLANNING)
     print(f"[pipeline] Planning task #{task_id}...")
-    routing = router.route_plan(task_content, extra_context=extra_context)
+    try:
+        routing = router.route_plan(task_content, extra_context=extra_context,
+                                    stack_profile=profile)
+    except TypeError:
+        # Fallback for legacy routers/stubs without stack_profile param
+        routing = router.route_plan(task_content, extra_context=extra_context)
     plan = router.call_llm(routing)
     state.set_plan(task_id, plan)
 
@@ -479,12 +491,9 @@ async def _process_task(task_id: int, task_file: str, config: LoopEngineConfig,
         print(f"[pipeline] Plan rejected for task #{task_id}. Back to backlog.")
         return
 
-    # 3. IMPLEMENTING — stack detection + preflight
+    # 3. IMPLEMENTING — preflight (profile already detected at pipeline start)
     state.update_state(task_id, TaskState.IMPLEMENTING)
     print(f"[pipeline] Implementing task #{task_id}...")
-    registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
-    profile = StackDetector.detect(task_content, REPO_ROOT, registry, default_stack=config.default_stack)
-    print(f"[pipeline] Detected stack: {profile.name} ({profile.display_name})")
     runner = PreflightRunner(timeout_seconds=30.0)
     preflight = await runner.run(profile, cwd=REPO_ROOT)
     if not preflight.passed:
@@ -511,7 +520,8 @@ async def _process_task(task_id: int, task_file: str, config: LoopEngineConfig,
 
     # 5. REVIEW
     state.update_state(task_id, TaskState.REVIEW)
-    review = qa.run_review(task_id, task_content, qa_result.get("report", ""))
+    review = qa.run_review(task_id, task_content, qa_result.get("report", ""),
+                           stack_profile=profile)
     print(f"[pipeline] Review result: {review['result']}")
 
     if review["result"] == "REJECTED":
diff --git a/loop-engine/qa_engine.py b/loop-engine/qa_engine.py
index 7d92490..971fde6 100644
--- a/loop-engine/qa_engine.py
+++ b/loop-engine/qa_engine.py
@@ -8,6 +8,7 @@ Writes to loop-engine/evidence/<task-id>/.
 import re
 import time
 from pathlib import Path
+from typing import Any, Optional
 
 from models import LoopEngineConfig, TaskState
 from state import StateMachine
@@ -45,17 +46,26 @@ class QAEngine:
         self.router = router
         self.evidence_dir = Path(config.evidence_dir)
 
-    def run_qa(self, task_id: int, task_content: str, diff: str = "", toolchain_evidence: str = "") -> dict:
+    def run_qa(self, task_id: int, task_content: str, diff: str = "",
+               toolchain_evidence: str = "",
+               stack_profile: Optional[Any] = None) -> dict:
         """Run QA Engineer review. Returns PASSED or FAILED."""
         self.evidence_dir.mkdir(parents=True, exist_ok=True)
         evidence_path = self.evidence_dir / f"{task_id}"
         evidence_path.mkdir(exist_ok=True)
 
         try:
-            routing = self.router.route_qa(task_content, diff, toolchain_evidence=toolchain_evidence)
+            routing = self.router.route_qa(
+                task_content, diff, toolchain_evidence=toolchain_evidence,
+                stack_profile=stack_profile)
         except TypeError:
-            # Fallback for legacy routers/stubs without toolchain_evidence param
-            routing = self.router.route_qa(task_content, diff)
+            # Fallback for legacy routers/stubs without stack_profile param
+            try:
+                routing = self.router.route_qa(
+                    task_content, diff, toolchain_evidence=toolchain_evidence)
+            except TypeError:
+                # Fallback for legacy routers/stubs without toolchain_evidence param
+                routing = self.router.route_qa(task_content, diff)
         qa_report = self.router.call_llm(routing)
 
         # Write evidence
@@ -71,12 +81,18 @@ class QAEngine:
         (evidence_path / "result.txt").write_text(result, encoding="utf-8")
         return {"result": result, "report": qa_report, "evidence_dir": str(evidence_path)}
 
-    def run_review(self, task_id: int, task_content: str, qa_report: str = "") -> dict:
+    def run_review(self, task_id: int, task_content: str, qa_report: str = "",
+                   stack_profile: Optional[Any] = None) -> dict:
         """Run Code Reviewer. Returns APPROVED or REJECTED."""
         evidence_path = self.evidence_dir / f"{task_id}"
         evidence_path.mkdir(parents=True, exist_ok=True)
 
-        routing = self.router.route_review(task_content, qa_report)
+        try:
+            routing = self.router.route_review(
+                task_content, qa_report, stack_profile=stack_profile)
+        except TypeError:
+            # Fallback for legacy routers/stubs without stack_profile param
+            routing = self.router.route_review(task_content, qa_report)
         review = self.router.call_llm(routing)
 
         (evidence_path / "review.md").write_text(review, encoding="utf-8")
diff --git a/loop-engine/router.py b/loop-engine/router.py
index 63f8dcb..f37dacd 100644
--- a/loop-engine/router.py
+++ b/loop-engine/router.py
@@ -12,7 +12,7 @@ Reads system-prompt.md + AGENTS.md + docs/conventions.md on every invocation.
 
 import os
 from pathlib import Path
-from typing import Optional
+from typing import Any, Optional
 
 from models import LoopEngineConfig
 from personas import load_personas
@@ -57,7 +57,37 @@ class LLMRouter:
         # All 7 operational personas from prompts/fragments/06-personas.md
         self.personas = load_personas(str(self.workspace_root))
 
-    def _resolve_model(self, category: str) -> tuple[str, Optional[str]]:
+    def _resolve_model(self, category: str,
+                       stack_profile: Optional[Any] = None) -> tuple[str, Optional[str]]:
+        """Resolve a model for a category via the 3-tier hierarchy (LE-3).
+
+        Tier 1 — Stack-Preferred Models: consult ``stack_profile.model_preferences``
+        (or a dict's ``"model_preferences"`` key). Match the exact category first,
+        then the wildcard ``"*"``. The first model whose ``{PROVIDER}_API_KEY`` env
+        var is present wins; reasoning level comes from the global category config.
+        Tier 2 — Global Category Models: existing category fallback chain.
+        Tier 3 — Global Default: ``(default_provider, None)``.
+        """
+        # Tier 1: Stack-Preferred Models
+        prefs: dict = {}
+        if stack_profile is not None:
+            if isinstance(stack_profile, dict):
+                prefs = stack_profile.get("model_preferences", {}) or {}
+            else:
+                prefs = getattr(stack_profile, "model_preferences", {}) or {}
+        if prefs:
+            candidate_models = prefs.get(category) or prefs.get("*") or []
+            for model in candidate_models:
+                provider = model.split("/")[0]
+                env_key = f"{provider.upper()}_API_KEY"
+                if os.environ.get(env_key):
+                    cat_config = self.config.categories.get(category)
+                    if not cat_config:
+                        cat_config = self.config.categories.get("unspecified")
+                    reasoning = cat_config.reasoning if cat_config else None
+                    return model, reasoning
+
+        # Tier 2: Global Category Models
         cat_config = self.config.categories.get(category)
         if not cat_config:
             cat_config = self.config.categories.get("unspecified")
@@ -66,6 +96,8 @@ class LLMRouter:
             env_key = f"{provider.upper()}_API_KEY"
             if os.environ.get(env_key):
                 return model, cat_config.reasoning
+
+        # Tier 3: Global Default
         return self.config.default_provider, None
 
     def _load_memory_context(self) -> str:
@@ -151,9 +183,10 @@ class LLMRouter:
 
     def route_with_persona(self, persona_name: str, user_content: str,
                            temperature: float = 0.3,
-                           category: str = "deep") -> dict:
+                           category: str = "deep",
+                           stack_profile: Optional[Any] = None) -> dict:
         """Route a call as ANY Manager-defined persona (all 7 invocable)."""
-        model, reasoning = self._resolve_model(category)
+        model, reasoning = self._resolve_model(category, stack_profile=stack_profile)
         return {
             "model": model, "reasoning": reasoning,
             "system": self._build_system_context(persona_name),
@@ -162,11 +195,12 @@ class LLMRouter:
         }
 
     def route_plan(self, task_content: str, category: str = "unspecified",
-                   extra_context: str = "") -> dict:
+                   extra_context: str = "",
+                   stack_profile: Optional[Any] = None) -> dict:
         user = f"Generate implementation blueprint:\n\n{task_content}"
         if extra_context:
             user += f"\n\nIncorporate this brainstorming session output:\n\n{extra_context}"
-        model, reasoning = self._resolve_model(category)
+        model, reasoning = self._resolve_model(category, stack_profile=stack_profile)
         return {
             "model": model, "reasoning": reasoning,
             "system": self._build_system_context("architect"),
@@ -174,8 +208,9 @@ class LLMRouter:
             "temperature": 0.3,
         }
 
-    def route_qa(self, task_content: str, diff: str = "", toolchain_evidence: str = "") -> dict:
-        model, reasoning = self._resolve_model("deep")
+    def route_qa(self, task_content: str, diff: str = "", toolchain_evidence: str = "",
+                 stack_profile: Optional[Any] = None) -> dict:
+        model, reasoning = self._resolve_model("deep", stack_profile=stack_profile)
         user = f"Review this task and changes:\n\n{task_content}\n\n## Diff\n\n{diff}"
         if toolchain_evidence:
             user += f"\n\n## Toolchain Verification\n\n{toolchain_evidence}"
@@ -186,8 +221,9 @@ class LLMRouter:
             "temperature": 0.1,
         }
 
-    def route_review(self, task_content: str, qa_report: str = "") -> dict:
-        model, reasoning = self._resolve_model("deep")
+    def route_review(self, task_content: str, qa_report: str = "",
+                     stack_profile: Optional[Any] = None) -> dict:
+        model, reasoning = self._resolve_model("deep", stack_profile=stack_profile)
         return {
             "model": model, "reasoning": reasoning,
             "system": self._build_system_context("code_reviewer"),
diff --git a/loop-engine/test_router.py b/loop-engine/test_router.py
index c8e0856..add4fe6 100644
--- a/loop-engine/test_router.py
+++ b/loop-engine/test_router.py
@@ -3,13 +3,19 @@ import sys, os
 sys.path.insert(0, os.path.dirname(__file__))
 
 from router import LLMRouter, _load_file_if_exists
-from models import LoopEngineConfig
+from models import LoopEngineConfig, StackProfileConfig
+from stacks import StackProfile
 
 
 def _make_config():
     return LoopEngineConfig(approval={"chat_id": 123})
 
 
+def _make_stack_profile(prefs):
+    return StackProfile(StackProfileConfig(
+        name="test-stack", display_name="Test Stack", model_preferences=prefs))
+
+
 def test_load_file_exists():
     p = os.path.join(os.path.dirname(__file__), "models.py")
     content = _load_file_if_exists(p)
@@ -78,6 +84,136 @@ def test_route_review():
     assert routing["temperature"] == 0.2
 
 
+# --- Stack-Aware Model Routing (LE-3) ---
+
+def test_resolve_model_stack_preferred_with_env():
+    os.environ["ANTHROPIC_API_KEY"] = "test-key"
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet", "openai/gpt-5.6-sol"]})
+    model, reasoning = router._resolve_model("deep", stack_profile=profile)
+    assert model == "anthropic/claude-3-7-sonnet"
+    assert reasoning == "medium"  # deep category reasoning
+    del os.environ["ANTHROPIC_API_KEY"]
+
+
+def test_resolve_model_stack_preferred_second_model_when_first_unkeyed():
+    for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "KIMI_API_KEY"]:
+        os.environ.pop(key, None)
+    os.environ["OPENAI_API_KEY"] = "test-key"
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet", "openai/gpt-5.6-sol"]})
+    model, reasoning = router._resolve_model("deep", stack_profile=profile)
+    assert model == "openai/gpt-5.6-sol"  # first unkeyed, second keyed wins
+    assert reasoning == "medium"
+    del os.environ["OPENAI_API_KEY"]
+
+
+def test_resolve_model_stack_fallback_category_when_key_missing():
+    for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "KIMI_API_KEY"]:
+        os.environ.pop(key, None)
+    os.environ["OPENAI_API_KEY"] = "test-key"
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
+    model, reasoning = router._resolve_model("deep", stack_profile=profile)
+    assert model == "openai/gpt-5.6-sol"  # Tier 2 category fallback
+    assert reasoning == "medium"
+    del os.environ["OPENAI_API_KEY"]
+
+
+def test_resolve_model_stack_empty_preferences():
+    for key in ["KIMI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
+        os.environ.pop(key, None)
+    os.environ["KIMI_API_KEY"] = "test-key"
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    profile = _make_stack_profile({})
+    model, reasoning = router._resolve_model("quick", stack_profile=profile)
+    assert model == "kimi/kimi-k3"
+    del os.environ["KIMI_API_KEY"]
+
+
+def test_resolve_model_stack_wildcard():
+    os.environ["GEMINI_API_KEY"] = "test-key"
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    profile = _make_stack_profile({"*": ["gemini/gemini-2.5-flash"]})
+    model, reasoning = router._resolve_model("quick", stack_profile=profile)
+    assert model == "gemini/gemini-2.5-flash"
+    del os.environ["GEMINI_API_KEY"]
+
+
+def test_resolve_model_stack_dict_profile():
+    os.environ["KIMI_API_KEY"] = "test-key"
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    profile = {"model_preferences": {"quick": ["kimi/kimi-k3"]}}
+    model, reasoning = router._resolve_model("quick", stack_profile=profile)
+    assert model == "kimi/kimi-k3"
+    del os.environ["KIMI_API_KEY"]
+
+
+def test_route_plan_with_stack_profile():
+    os.environ["ANTHROPIC_API_KEY"] = "test-key"
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
+    routing = router.route_plan("## Goal\nBuild a feature", "deep", stack_profile=profile)
+    assert routing["model"] == "anthropic/claude-3-7-sonnet"
+    del os.environ["ANTHROPIC_API_KEY"]
+
+
+def test_route_qa_with_stack_profile():
+    os.environ["ANTHROPIC_API_KEY"] = "test-key"
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
+    routing = router.route_qa("Task content", "diff here", stack_profile=profile)
+    assert routing["model"] == "anthropic/claude-3-7-sonnet"
+    del os.environ["ANTHROPIC_API_KEY"]
+
+
+def test_route_review_with_stack_profile():
+    os.environ["ANTHROPIC_API_KEY"] = "test-key"
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
+    routing = router.route_review("Task", "QA passed", stack_profile=profile)
+    assert routing["model"] == "anthropic/claude-3-7-sonnet"
+    del os.environ["ANTHROPIC_API_KEY"]
+
+
+def test_route_with_persona_stack_profile():
+    os.environ["ANTHROPIC_API_KEY"] = "test-key"
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
+    routing = router.route_with_persona("architect", "content", category="deep",
+                                        stack_profile=profile)
+    assert routing["model"] == "anthropic/claude-3-7-sonnet"
+    del os.environ["ANTHROPIC_API_KEY"]
+
+
+def test_route_plan_backward_compat_no_stack_profile():
+    for key in ["KIMI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
+        os.environ.pop(key, None)
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    routing = router.route_plan("## Goal\nBuild a feature", "quick")
+    assert routing["model"] == cfg.default_provider
+
+
+def test_route_qa_backward_compat_no_stack_profile():
+    for key in ["KIMI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
+        os.environ.pop(key, None)
+    cfg = _make_config()
+    router = LLMRouter(cfg)
+    routing = router.route_qa("Task content", "diff here")
+    assert routing["model"] == cfg.default_provider
+
+
 if __name__ == "__main__":
     tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
     passed = failed = 0
diff --git a/stacks/go-gin.yaml b/stacks/go-gin.yaml
index 4e520d1..aee4d8d 100644
--- a/stacks/go-gin.yaml
+++ b/stacks/go-gin.yaml
@@ -11,4 +11,6 @@ toolchain:
   test_cmd: "go test ./..."
   build_cmd: "go build ./..."
   lint_cmd: "golangci-lint run || go vet ./..."
-model_preferences: {}
+model_preferences:
+  deep: ["openai/gpt-5.6-sol", "anthropic/claude-3-7-sonnet"]
+  quick: ["gemini/gemini-2.5-flash"]
diff --git a/stacks/kotlin-android.yaml b/stacks/kotlin-android.yaml
index e61ce2e..695927e 100644
--- a/stacks/kotlin-android.yaml
+++ b/stacks/kotlin-android.yaml
@@ -12,4 +12,6 @@ toolchain:
   test_cmd: "./gradlew test"
   build_cmd: "./gradlew assembleDebug"
   lint_cmd: "./gradlew ktlintCheck"
-model_preferences: {}
+model_preferences:
+  deep: ["anthropic/claude-3-7-sonnet", "openai/gpt-5.6-sol"]
+  quick: ["gemini/gemini-2.5-flash"]
diff --git a/stacks/node-ts.yaml b/stacks/node-ts.yaml
index ce5c478..c76ab59 100644
--- a/stacks/node-ts.yaml
+++ b/stacks/node-ts.yaml
@@ -12,4 +12,6 @@ toolchain:
   test_cmd: "pnpm test || npm test"
   build_cmd: "pnpm build || npm run build"
   lint_cmd: "pnpm lint || npm run lint"
-model_preferences: {}
+model_preferences:
+  deep: ["openai/gpt-5.6-sol", "anthropic/claude-3-7-sonnet"]
+  quick: ["kimi/kimi-k3"]
diff --git a/stacks/python-fastapi.yaml b/stacks/python-fastapi.yaml
index c78aa7e..f6a3a31 100644
--- a/stacks/python-fastapi.yaml
+++ b/stacks/python-fastapi.yaml
@@ -12,4 +12,6 @@ toolchain:
   test_cmd: "pytest -q"
   build_cmd: null
   lint_cmd: "ruff check . || flake8 ."
-model_preferences: {}
+model_preferences:
+  deep: ["openai/gpt-5.6-sol", "gemini/gemini-2.5-pro"]
+  quick: ["gemini/gemini-2.5-flash"]
```
<!-- END_GIT_DIFF -->