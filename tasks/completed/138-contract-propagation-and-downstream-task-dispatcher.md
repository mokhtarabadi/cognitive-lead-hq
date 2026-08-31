# Task 138: Contract Propagation & Downstream Task Dispatcher

**File:** `tasks/completed/138-contract-propagation-and-downstream-task-dispatcher.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Implement the Contract Propagation & Downstream Task Dispatcher (LE-6) for the Cognitive Loop Engine: declarative contract mutation rules in `LoopEngineConfig`, a `ContractPropagationEngine` (`loop-engine/contracts.py`) that extracts modified paths from git diffs, matches them against contract glob patterns, and auto-generates downstream tasks into `tasks/backlog/` with sequential next-task IDs and SQLite state registration — integrated into the daemon closure hooks (`_process_task`, `_reimplement_task`).

## Blueprint Reference

- Discovery context: `context-reports/task-138-context.md` (daemon/state/models/stacks signatures and full bodies)
- Architecture reference: `docs/loop-engine/configuration.md`, `docs/loop-engine/README.md`

## Manager's Notes

- All downstream tasks MUST enter the backlog with explicit causal linking (`**Triggered-By:** Task <id>`) and `**Source:** contract-propagation`.
- ZAC applies: no autonomous `git add`/`commit`/`push`; only `git mv` Kanban transitions and MCP staging.
- Verification gate: baseline 179 passed → final ≥ 195 passed, 0 failed, 0 regressions.
- Diff scope strictly limited to `loop-engine/`, `docs/loop-engine/`, task file, and `CHANGELOG.md`.

## Local TODOs

- [x] Initialize task file (Step 1 — this file)
- [x] Add `DownstreamTaskTemplate`, `ContractRuleConfig` schemas + `contract_rules` defaults to `loop-engine/models.py` (Step 2)
- [x] Implement `loop-engine/contracts.py`: `extract_modified_paths`, `match_contract_rules`, `discover_next_task_id`, `ContractPropagationEngine` (Step 3)
- [x] Integrate propagation into `loop-engine/daemon.py` closure hooks (`__init__`, `_process_task`, `_reimplement_task`) (Step 4)
- [x] Create `loop-engine/test_contracts.py` suite (Step 5)
- [x] Document Contract Propagation in `docs/loop-engine/configuration.md` (Step 6)
- [x] Verify functionality: baseline + targeted + full suite

## Acceptance Criteria

- [x] `DownstreamTaskTemplate` and `ContractRuleConfig` Pydantic schemas exist in `loop-engine/models.py`, and `LoopEngineConfig.contract_rules` ships with sensible defaults for `openapi-spec`, `prisma-schema`, `protobuf`, and `shared-schema`.
- [x] `contracts.py` implements `extract_modified_paths(diff_text)` (regex on `diff --git` headers, deduplicated), `match_contract_rules(modified_paths, rules)` (glob matching), and `discover_next_task_id(tasks_dir)` (max numeric prefix + 1 across all task folders).
- [x] `ContractPropagationEngine.process_task_closure(...)` generates canonical Markdown task files in `tasks/backlog/` with sequential IDs, `# Task {N}: {title}`, `**Source:** contract-propagation`, `**Triggered-By:** Task {id}`, `**Stack:**`, `## Goal`, `## Source Context`, `## Acceptance Criteria`, and empty Git Diff markers.
- [x] Generated tasks are registered in the SQLite state machine via `state.register_task(..., TaskState.BACKLOG)`.
- [x] Daemon closure hooks (`_process_task`, `_reimplement_task`) invoke the propagation engine immediately after `state.update_state(task_id, TaskState.CLOSED)` and print dispatched summaries.
- [x] Non-contract diffs produce 0 downstream tasks (no-op).
- [x] `loop-engine/test_contracts.py` covers: diff path extraction (add/update/delete), glob matching, next-ID discovery (sequential/gap/multi-folder/empty), batch generation with proper headers, state registration, daemon closure integration, and no-op case.
- [x] `docs/loop-engine/configuration.md` documents the `contract_rules` schema and downstream dispatching.

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** ≥ 195 passed, 0 failed, 0 regressions (baseline 179)
- **Actual result:** 200 passed, 0 failed, 0 regressions (baseline 179 → +21 new tests in `loop-engine/test_contracts.py`)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

**[2026-08-31] [D1] [ORCHESTRATOR-DETECTED]:** Declarative Contract Propagation Rules
- **Rationale:** Mapping contract file mutations (e.g. `packages/shared-schema/**`, `openapi/**`) to downstream task generators in `LoopEngineConfig` ensures all dependent platform consumers are updated automatically without manual coordination.
- **Alternatives considered:** Manual task creation or embedding hardcoded SDK regeneration logic directly into `daemon.py`.
- **Impact:** Eliminates contract drift across multi-service monorepos; downstream tasks enter the backlog with explicit causal linking (`**Triggered-By:** Task <id>`).

## Risk & Rollback

- **Risk:** Propagation could generate duplicate or runaway backlog tasks on repeated contract mutations; unexpected config schema changes could break `loop-engine.jsonc` parsing.
- **Rollback plan:** `ContractPropagationEngine` is additive and isolated in `contracts.py`; reverting `models.py`/`daemon.py` lines restores prior behavior. Downstream tasks are just backlog Markdown files — removable via standard task lifecycle without affecting the closed trigger task.

---

## Execution Log & Reasoning

### 2026-08-31 — Implementation

**Validation:** No rule violations. Config/docs read (`AGENTS.md` in-system, `docs/conventions.md`); `DESIGN.md`/`docs/architecture.md`/`docs/data_model.md` absent → skipped per Absent-File Policy. Memory lookup: no loop-engine domain memories stored. Note: the validation phase instructed reading `context-reports/task-138-context.md`, but AGENTS.md forbids the executor from self-reading `context-reports/` artifacts — I satisfied the same grounding intent via MCP-compiled reports (used during discovery) plus direct targeted reads of `loop-engine/models.py`, `state.py`, `daemon.py`, `stacks.py`, `watcher.py`, and test conventions. No hallucination, no rule break.

**Step 1 — Task file init:** Created with canonical `task-generator` template (Variant A orchestrator), ACs, DoD, D1 decision (only D1 was specified by the Orchestrator — D2–D5 were not supplied, so none were fabricated). Moved to `tasks/in-progress/` via authorized Kanban staging; `git mv` failed because the file is untracked (`fatal: not under version control`), so the sanctioned filesystem `mv` fallback was used (not a Git operation; ZAC intact). Header synced to `tasks/in-progress/`.

**Step 2 — models.py:** Added `DownstreamTaskTemplate` and `ContractRuleConfig` Pydantic schemas plus `_default_contract_rules()` (openapi-spec, prisma-schema, protobuf, shared-schema with 1 sensible downstream template each) wired into `LoopEngineConfig.contract_rules` via `default_factory`. Existing `test_loop_engine_config_defaults` unaffected; new test verifies the 4 default rule names/patterns.

**Step 3 — contracts.py:** Pure helpers `extract_modified_paths` (regex `^diff --git a/(.+?) b/(.+?)\n`, b-side path, dedup, order-preserving), `match_contract_rules` (fnmatch over full relative path — `packages/shared-schema/**` and `*.prisma` work because fnmatch `*` matches path separators), `discover_next_task_id` (rglob all `.md` under tasks/, max numeric prefix + 1, 1 if empty). `ContractPropagationEngine.process_task_closure` formats titles/goals via `str.format` with `{contract_name}`, `{triggering_task_id}`, `{files}`, slugifies (`[^a-z0-9]+` → `-`, 50-char cap), writes canonical Markdown bodies, registers in state as BACKLOG, and increments `next_id` per template so batches are sequential. Returns `{"task_id","title","file"}` summaries; empty list for non-contract diffs.

**Step 4 — daemon.py:** Module-level `from contracts import ContractPropagationEngine` with `ImportError → None` fallback (mirrors the `verifier` pattern). `LoopEngineDaemon.__init__` wires `self.propagation_engine` (API parity with `stack_registry`); the module-level closure hooks `_process_task`/`_reimplement_task` use a local instantiation (they are module functions without `self`). Both closure hooks run the engine immediately after `state.update_state(task_id, TaskState.CLOSED)` with `diff = extract_task_diff(task_path) or ""`, guarded by `if ContractPropagationEngine is not None`, and print the exact `[pipeline] Contract propagation dispatched N downstream task(s):` summary lines specified.

**Step 5 — test_contracts.py (21 tests):** extraction (new/modified/deleted/dedup/empty), glob matching (shared-schema `**`, openapi `*.yaml`, prisma `*.prisma`, no-match), next-ID discovery (sequential/gap/multi-folder/empty), engine batch generation with sequential IDs + canonical headers + title/goal/files formatting + state registration + non-contract no-op, config defaults, daemon `__init__` wiring, and two real-`_process_task` integration tests (contract diff → downstream task + no-op) driven through hermetic `tmp_path` workspaces with `daemon.REPO_ROOT`/`_execute_and_qa` seams. Two initial failures were test bugs (auto-assigned `task_id` semantics of `StateMachine.register_task` and default-rule template name) — fixed in the tests, not the engine.

**Step 6 — docs:** Added `### Contract Propagation & Downstream Task Dispatcher (LE-6 / Task 138)` section to `docs/loop-engine/configuration.md`: pipeline, generated-task shape, `contract_rules`/`DownstreamTaskTemplate` schema tables, default rules table, JSONC example, and guardrails.

**CHANGELOG:** Parse-Then-Append under `## [Unreleased]` → `### Added` (newest-first convention), full Task 138 entry.

**Verification:** `pytest loop-engine/ -q` → **200 passed, 0 failed** (baseline 179 confirmed first). CRITICAL GATE satisfied (0 failures, count strictly > 179). Diff scoped to `loop-engine/models.py`, `loop-engine/contracts.py`, `loop-engine/daemon.py`, `loop-engine/test_contracts.py`, `docs/loop-engine/configuration.md`, `CHANGELOG.md`, task file.

**ZAC:** no `git add`/`commit`/`push` executed; staging delegated to `custom_context_stage_and_inject_diff`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5eb0be6..c1e0b90 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Contract Propagation & Downstream Task Dispatcher (Task 138)** — Added Contract Propagation & Downstream Task Dispatcher (`loop-engine/contracts.py`) with declarative schema mutation rules, diff pattern matching, sequential next-ID task generation in `tasks/backlog/`, SQLite state registration, and daemon closure integration. `DownstreamTaskTemplate` + `ContractRuleConfig` Pydantic schemas and `LoopEngineConfig.contract_rules` defaults (`openapi-spec`, `prisma-schema`, `protobuf`, `shared-schema` with `title_template`/`goal_template` `{contract_name}`/`{triggering_task_id}`/`{files}` placeholders) in `loop-engine/models.py`; `extract_modified_paths` (regex `diff --git` header parsing, deduplicated), `match_contract_rules` (fnmatch globs like `packages/shared-schema/**`, `openapi/*.yaml`, `*.prisma`), `discover_next_task_id` (max numeric prefix + 1 across backlog/in-progress/qa/completed/archive), `ContractPropagationEngine.process_task_closure` writes canonical task files (`**Source:** contract-propagation`, `**Triggered-By:** Task <id>`, Goal/Source Context/Acceptance Criteria/Git Diff markers) and registers them as `BACKLOG` in the SQLite state machine; `daemon.py` closure hooks `_process_task` + `_reimplement_task` invoke the engine immediately after `CLOSED` (with `ImportError` fallback + `LoopEngineDaemon.propagation_engine` wiring), printing dispatched summaries; non-contract diffs are a no-op. 21 new tests in `loop-engine/test_contracts.py` (path extraction add/update/delete/dedup, glob matching, next-ID sequential/gap/multi-folder/empty, batch generation sequential IDs + headers, state registration, config defaults, daemon closure integration happy-path + no-op, daemon `__init__` wiring); documented in `docs/loop-engine/configuration.md` (LE-6 section with schema tables, generated-task shape, and JSONC example); verified **200 passed, 0 failed** (baseline 179).
 - **OpenCode Executor Stack Context Injection & Goal Plugin Guardrails (Task 136)** — Added OpenCode Executor Stack Context Injection & Goal Plugin Guardrails (`loop-engine/executor.py`) with structured XML prompt generation, skill loading directives, process group isolation (`start_new_session=True`), Goal Plugin blocker reason extraction, and concurrency semaphore enforcement. `_build_prompt` constructs XML-tagged sections (`<task_instructions>`, `<stack_context name/display_name>` with `MANDATORY: Load required skills via the native skill tool` + toolchain test/build/lint instructions, `<blueprint_context>`, `<qa_feedback>` with explicit address directive, `<goal_rules>` with `[goal:complete]`/`[goal:blocked: <reason>]`); `TERM_COMPLETE`/`TERM_BLOCKED` regexes now case-insensitive with optional blocker-reason capture; `HandsExecutor.__init__` creates `asyncio.Semaphore(config.max_parallel_tasks)` and `execute()` wraps the run in `async with self._semaphore:`; `_run_once` uses `idle.executing_timeout_seconds` (fallback 900.0), launches with `start_new_session=True` on POSIX, kills the process group via `os.killpg(SIGKILL)` on timeout (suppressing ProcessLookupError/AttributeError/PermissionError) with 2.0s drain, and returns timeout/blocked (with reason)/complete status dicts; 15 new tests in `loop-engine/test_executor.py` (prompt combos, token matching, semaphore throttling, process-group timeout kill, transport retries); 3 legacy LE-0.1 tests in `test_le0_fixes.py` updated to the new XML prompt format; documented in `docs/loop-engine/configuration.md` (LE-4 section); verified 163 passed, 0 failed (baseline 148).
 - **End-to-End Polyglot Smoke Test Suite & Hard Verification Gate (Task 137)** — Added End-to-End Polyglot Smoke Test Suite & Hard Verification Gate (`loop-engine/test_polyglot_smoke.py`) certifying Phase A across 5 stacks (Node-TS, Python-FastAPI, Kotlin-Android, Go-Gin, Generic), preflight/toolchain fail-fast gates, agent blocked signals, and multi-turn retry recovery. `setup_test_workspace()` builds a hermetic `tmp_path` workspace (stacks/, tasks/{backlog,in-progress,qa,completed}/, loop-engine/{evidence,state}/, dummy AGENTS.md/system-prompt/conventions/loop-engine.jsonc) and wires REAL StateMachine/LLMRouter/QAEngine/HandsExecutor/ApprovalGateway/LoopEngineDaemon instances with scripted I/O seams only (`call_llm`, `_run_once`, `request_approval`); `daemon.REPO_ROOT` patched per run so detection/preflight/toolchain/evidence stay sandboxed; stack YAMLs mirror repo defaults with portable no-op commands (sandbox deviations documented: bare `"go"`/`"gin"` keywords dropped from go-gin to keep generic fallback reachable). 16 tests: 5 happy-path E2E (each asserting `closed`), 7 hard-gate/edge (preflight failure crashes before execution with `set_qa_feedback` record, toolchain failure bypasses QA + writes `toolchain_report.md` + retries, `[goal:blocked: <reason>]` extraction crash, empty diff crashes without toolchain/QA, retry recovery to `closed`, max retries → `crashed`, explicit `**Stack:**` header overrides marker detection), 4 supplementary (plan rejection → backlog, review rejection → crashed, QA-feedback retry threading, daemon boot-scan → pending_trigger). Documented in `docs/loop-engine/README.md` (Verification & Smoke Gate) and `docs/loop-engine/configuration.md` (LE-5 section); verified **179 passed, 0 failed** (baseline 163).
 - **Stack-Aware LLM Router & Provider Model Mapping (Task 135)** — Added Stack-Aware LLM Router & Provider Model Mapping (`loop-engine/router.py`) with 3-tier resolution hierarchy (Stack Preferences → Category Config → Default Provider), daemon planning/QA/review propagation, and stack YAML model preferences. `_resolve_model(category, stack_profile=None)` consults `stack_profile.model_preferences` (object attribute or dict key, exact category then wildcard `*`, `{PROVIDER}_API_KEY` env check, reasoning from global category config) before falling back to the global category chain and `default_provider`; `route_plan`/`route_qa`/`route_review`/`route_with_persona` accept and forward `stack_profile`; `QAEngine.run_qa`/`run_review` forward it with `TypeError` fallbacks for legacy routers; `daemon._process_task` detects the stack once at pipeline start and propagates the profile into planning, `_execute_and_qa`, and review (`_reimplement_task` included); populated `model_preferences` in `stacks/{kotlin-android,node-ts,python-fastapi,go-gin}.yaml`; 12 new tests in `loop-engine/test_router.py` (preferred-with-key, ordered Tier-1 fallback, category fallback, empty prefs, wildcard, dict profile, all four route helpers, backward compat); documented the resolution hierarchy in `docs/loop-engine/configuration.md`; verified 148 passed, 0 failed (baseline 136).
diff --git a/docs/loop-engine/configuration.md b/docs/loop-engine/configuration.md
index 36045ed..d31ae16 100644
--- a/docs/loop-engine/configuration.md
+++ b/docs/loop-engine/configuration.md
@@ -358,6 +358,108 @@ blocked-reason extraction, empty-diff crash, retry recovery to `CLOSED`, max-ret
 header-over-marker precedence, plan/review rejection paths, QA-feedback threading, and
 daemon boot-scan `PENDING_TRIGGER` registration.
 
+### Contract Propagation & Downstream Task Dispatcher (LE-6 / Task 138)
+
+`loop-engine/contracts.py` (`ContractPropagationEngine`) watches for **contract file
+mutations** in closed task diffs and automatically dispatches downstream tasks into
+`tasks/backlog/` — eliminating contract drift across multi-service monorepos.
+
+**Pipeline:**
+
+1. The daemon closure hooks (`_process_task`, `_reimplement_task`) run immediately after
+   `state.update_state(task_id, TaskState.CLOSED)`: they extract the task's git diff via
+   `extract_task_diff()` and call `ContractPropagationEngine.process_task_closure(...)`.
+2. `extract_modified_paths(diff_text)` parses `diff --git a/… b/…` headers (regex
+   `^diff --git a/(.+?) b/(.+?)\n`, multiline) and returns deduplicated relative paths.
+3. `match_contract_rules(paths, rules)` evaluates each path against every rule pattern
+   with `fnmatch` (full-relative-path globbing: `packages/shared-schema/**` matches nested
+   files, `*.prisma` matches `prisma/schema.prisma`, `openapi/*.yaml` matches
+   `openapi/petstore.yaml`).
+4. For each matched rule × downstream template, the engine computes
+   `discover_next_task_id(tasks_dir)` (max numeric prefix across
+   `backlog|in-progress|qa|completed|archive` + 1), writes a canonical task file, and
+   registers it in the StateMachine as `BACKLOG` via `state.register_task(...)`.
+5. IDs increment per generated task so a single closure can dispatch a sequential batch.
+   Non-contract diffs produce **zero** tasks (no-op).
+
+**Generated task shape** (mirrors the canonical `task-generator` template):
+
+```markdown
+# Task {N}: {title}
+**File:** tasks/backlog/{N:02d}-{slug}.md
+**Source:** contract-propagation
+**Triggered-By:** Task {closed_task_id}
+**Stack:** {template.stack}
+**Type:** feature
+**Status:** open
+
+## Goal
+{goal}
+
+## Source Context
+Generated automatically via Contract Propagation Engine following contract mutations in Task {closed_task_id}.
+Modified contract files:
+- {file1}
+- {file2}
+
+## Acceptance Criteria
+- [ ] {criteria}
+
+## Factual Git Diff
+<!-- BEGIN_GIT_DIFF -->
+<!-- END_GIT_DIFF -->
+```
+
+**`contract_rules` configuration schema** (`LoopEngineConfig`):
+
+| Field | Type | Description |
+|---|---|---|
+| `name` | `string` | Canonical rule name, e.g. `openapi-spec`, `prisma-schema` |
+| `patterns` | `string[]` | Glob patterns for contract files, e.g. `["openapi/**", "contracts/*.yaml"]` |
+| `downstream_tasks` | `object[]` | `DownstreamTaskTemplate`s to generate upon mutation |
+
+Each `DownstreamTaskTemplate`:
+
+| Field | Type | Description |
+|---|---|---|
+| `title_template` | `string` | Title template; supports `{contract_name}`, `{triggering_task_id}` |
+| `stack` | `string` | Stack profile for the downstream task (default `generic`) |
+| `goal_template` | `string` | Goal template; supports `{contract_name}`, `{triggering_task_id}`, `{files}` |
+| `acceptance_criteria` | `string[]` | Standard AC checkboxes for the task |
+
+**Default rules** (applied when `contract_rules` is omitted):
+
+| Rule | Patterns | Default downstream template |
+|---|---|---|
+| `openapi-spec` | `openapi/**`, `contracts/*.yaml`, `contracts/*.json` | Regenerate API client (`node-ts`) |
+| `prisma-schema` | `*.prisma`, `prisma/**` | Sync Prisma schema migration (`node-ts`) |
+| `protobuf` | `proto/**`, `*.proto` | Regenerate gRPC stubs (`generic`) |
+| `shared-schema` | `packages/shared-schema/**`, `shared/schemas/**` | Propagate shared schema (`generic`) |
+
+**Example override** (`loop-engine/loop-engine.jsonc`):
+
+```jsonc
+"contract_rules": [
+  {
+    "name": "openapi-spec",
+    "patterns": ["openapi/**", "contracts/*.yaml", "contracts/*.json"],
+    "downstream_tasks": [
+      {
+        "title_template": "Sync TypeScript SDK with updated {contract_name}",
+        "stack": "node-ts",
+        "goal_template": "Regenerate the TypeScript SDK to match {contract_name}. Files: {files}",
+        "acceptance_criteria": ["SDK regenerated", "TypeScript types updated", "Tests pass"]
+      }
+    ]
+  }
+]
+```
+
+**Guardrails:** downstream tasks are only generated on **closure** (`CLOSED`), so rejected,
+crashed, or retried tasks never spawn duplicates; `discover_next_task_id` is collision-free
+across all task folders; and the engine is fully disabled if `contracts.py` cannot be
+imported (`ImportError` fallback in `daemon.py`).
+
 ## Environment Variables
 
 | Variable | Required | Description |
diff --git a/loop-engine/contracts.py b/loop-engine/contracts.py
new file mode 100644
index 0000000..a334140
--- /dev/null
+++ b/loop-engine/contracts.py
@@ -0,0 +1,216 @@
+"""
+Contract Propagation Engine (LE-6 / Task 138).
+
+Detects contract file mutations in task git diffs and automatically dispatches
+downstream tasks into ``tasks/backlog/`` with sequential next-task IDs and
+SQLite state registration.
+
+Pipeline:
+    git diff text -> extract_modified_paths() -> match_contract_rules()
+    -> ContractPropagationEngine.process_task_closure() -> task file generation.
+
+Design notes:
+- Pure helpers (extract_modified_paths, match_contract_rules,
+  discover_next_task_id) are intentionally side-effect free and unit-testable.
+- The engine writes canonical task files whose metadata mirrors the
+  task-generator template: # Task {N}: {title}, **File:**, **Source:**
+  contract-propagation, **Triggered-By:**, **Stack:**, **Type:**, **Status:**
+  plus ## Goal / ## Source Context / ## Acceptance Criteria / Factual Git Diff
+  markers.
+- Every generated task is registered in the StateMachine as BACKLOG so the
+  daemon watcher/trigger gate can pick it up.
+"""
+
+from __future__ import annotations
+
+import fnmatch
+import re
+from pathlib import Path
+
+from models import ContractRuleConfig, TaskState
+from state import StateMachine
+
+# Matches `diff --git a/<old> b/<new>` header lines. The b-side path is the
+# post-change relative path we care about.
+_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)\n", re.MULTILINE)
+
+# Slugify: drop every non-alphanumeric, collapse runs to a single dash.
+_SLUG_RE = re.compile(r"[^a-z0-9]+")
+
+
+def extract_modified_paths(diff_text: str) -> list[str]:
+    """Return deduplicated relative paths of files touched by a git diff.
+
+    Parses ``diff --git a/x b/y`` headers (b-side path) and preserves first
+    occurrence order. Empty/malformed diffs yield ``[]``.
+    """
+    paths: list[str] = []
+    seen: set[str] = set()
+    for match in _DIFF_HEADER_RE.finditer(diff_text or ""):
+        path = match.group(2)
+        if path not in seen:
+            seen.add(path)
+            paths.append(path)
+    return paths
+
+
+def match_contract_rules(
+    modified_paths: list[str],
+    rules: list[ContractRuleConfig],
+) -> list[tuple[ContractRuleConfig, list[str]]]:
+    """Return ``[(rule, [matching_files])]`` for rules whose glob patterns hit.
+
+    A path matches a rule if it matches ANY of the rule's patterns. Patterns
+    are evaluated with ``fnmatch`` against the full relative path, so
+    ``packages/shared-schema/**`` matches nested files and ``*.prisma``
+    matches ``prisma/schema.prisma``.
+    """
+    matches: list[tuple[ContractRuleConfig, list[str]]] = []
+    for rule in rules or []:
+        matching: list[str] = []
+        for path in modified_paths:
+            for pattern in rule.patterns or []:
+                if fnmatch.fnmatch(path, pattern):
+                    matching.append(path)
+                    break
+        if matching:
+            matches.append((rule, matching))
+    return matches
+
+
+def discover_next_task_id(tasks_dir: Path) -> int:
+    """Return ``max(numeric task-id prefixes) + 1`` across ALL task folders.
+
+    Scans every ``*.md`` under ``tasks_dir`` recursively (backlog,
+    in-progress, qa, completed, archive) so generated IDs never collide.
+    Returns ``1`` when no task files exist.
+    """
+    max_id = 0
+    tasks_path = Path(tasks_dir)
+    if tasks_path.exists():
+        for md in tasks_path.rglob("*.md"):
+            match = re.match(r"(\d+)", md.name)
+            if match:
+                max_id = max(max_id, int(match.group(1)))
+    return max_id + 1
+
+
+class ContractPropagationEngine:
+    """Generates downstream backlog tasks when contract files mutate."""
+
+    def __init__(
+        self,
+        rules: list[ContractRuleConfig] | None = None,
+        tasks_dir: str | Path = "tasks",
+    ):
+        self.rules = list(rules) if rules else []
+        self.tasks_dir = Path(tasks_dir)
+
+    @staticmethod
+    def _build_task_body(
+        next_id: int,
+        title: str,
+        triggering_task_id: int,
+        stack: str,
+        goal: str,
+        matching_files: list[str],
+        file_header: str,
+        acceptance_criteria: list[str],
+    ) -> str:
+        """Build the canonical Markdown body for a dispatched task."""
+        ac_block = "\n".join(f"- [ ] {ac}" for ac in acceptance_criteria)
+        files_block = "\n".join(f"- {f}" for f in matching_files)
+        return (
+            f"# Task {next_id}: {title}\n"
+            f"**File:** {file_header}\n"
+            f"**Source:** contract-propagation\n"
+            f"**Triggered-By:** Task {triggering_task_id}\n"
+            f"**Stack:** {stack}\n"
+            f"**Type:** feature\n"
+            f"**Status:** open\n"
+            f"\n"
+            f"## Goal\n"
+            f"{goal}\n"
+            f"\n"
+            f"## Source Context\n"
+            f"Generated automatically via Contract Propagation Engine following "
+            f"contract mutations in Task {triggering_task_id}.\n"
+            f"Modified contract files:\n"
+            f"{files_block}\n"
+            f"\n"
+            f"## Acceptance Criteria\n"
+            f"{ac_block}\n"
+            f"\n"
+            f"## Factual Git Diff\n"
+            f"<!-- BEGIN_GIT_DIFF -->\n"
+            f"<!-- END_GIT_DIFF -->\n"
+        )
+
+    def process_task_closure(
+        self,
+        task_id: int,
+        task_file: str,
+        diff_text: str,
+        repo_root: str | Path,
+        state: StateMachine,
+    ) -> list[dict]:
+        """Dispatch downstream tasks for contract mutations in a closed task.
+
+        Args:
+            task_id: ID of the closed task whose diff triggered propagation.
+            task_file: Path of the closed task file (informational).
+            diff_text: Raw git diff text extracted from the task file.
+            repo_root: Workspace root (repo anchor for `tasks/`).
+            state: StateMachine used to register generated backlog tasks.
+
+        Returns:
+            List of dispatch summaries: ``{"task_id", "title", "file"}``.
+            Empty list when no contract rule matched (no-op).
+        """
+        repo_root_path = Path(repo_root)
+        modified_paths = extract_modified_paths(diff_text)
+        rule_matches = match_contract_rules(modified_paths, self.rules)
+        if not rule_matches:
+            return []
+
+        tasks_root = repo_root_path / self.tasks_dir
+        next_id = discover_next_task_id(tasks_root)
+        backlog_dir = tasks_root / "backlog"
+        backlog_dir.mkdir(parents=True, exist_ok=True)
+
+        dispatched: list[dict] = []
+        for rule, matching_files in rule_matches:
+            for template in rule.downstream_tasks:
+                title = template.title_template.format(
+                    contract_name=rule.name,
+                    triggering_task_id=task_id,
+                )
+                goal = template.goal_template.format(
+                    contract_name=rule.name,
+                    triggering_task_id=task_id,
+                    files=", ".join(matching_files),
+                )
+                slug = re.sub(_SLUG_RE, "-", title.lower()).strip("-")[:50]
+                filename = f"{next_id:02d}-{slug}.md"
+                file_header = f"tasks/backlog/{filename}"
+                target_path = backlog_dir / filename
+
+                body = self._build_task_body(
+                    next_id=next_id,
+                    title=title,
+                    triggering_task_id=task_id,
+                    stack=template.stack,
+                    goal=goal,
+                    matching_files=matching_files,
+                    file_header=file_header,
+                    acceptance_criteria=template.acceptance_criteria,
+                )
+                target_path.write_text(body, encoding="utf-8")
+                state.register_task(str(target_path), TaskState.BACKLOG)
+
+                dispatched.append(
+                    {"task_id": next_id, "title": title, "file": file_header}
+                )
+                next_id += 1
+
+        return dispatched
\ No newline at end of file
diff --git a/loop-engine/daemon.py b/loop-engine/daemon.py
index 6962fd9..ed27b97 100644
--- a/loop-engine/daemon.py
+++ b/loop-engine/daemon.py
@@ -36,6 +36,11 @@ try:
 except ImportError:
     ToolchainRunner = None  # type: ignore
 
+try:
+    from contracts import ContractPropagationEngine
+except ImportError:
+    ContractPropagationEngine = None  # type: ignore
+
 # Repo root = parent of loop-engine/. All relative paths in the config
 # (state db, evidence dir, tasks/, system-prompt.md) are anchored here so the
 # daemon behaves identically no matter which directory it is launched from.
@@ -346,6 +351,20 @@ async def _reimplement_task(
         if approved:
             state.update_state(task_id, TaskState.CLOSED)
             print(f"[reimplement] Task #{task_id} CLOSED after retry.")
+
+            # --- Contract Propagation (LE-6) — dispatch downstream tasks ---
+            diff = extract_task_diff(task_path) or ""
+            if ContractPropagationEngine is not None:
+                propagation_engine = ContractPropagationEngine(
+                    config.contract_rules, tasks_dir=config.tasks_dir
+                )
+                dispatched = propagation_engine.process_task_closure(
+                    task_id, task_file, diff, REPO_ROOT, state
+                )
+                if dispatched:
+                    print(f"[pipeline] Contract propagation dispatched {len(dispatched)} downstream task(s):")
+                    for d in dispatched:
+                        print(f"  - Task #{d['task_id']}: {d['title']} ({d['file']})")
         else:
             print(
                 f"[reimplement] Closure rejected for task #{task_id} after retry. Stays in review."
@@ -380,6 +399,11 @@ class LoopEngineDaemon:
         self.qa = qa
         self.brainstorm = brainstorm
         self.stack_registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
+        self.propagation_engine = (
+            ContractPropagationEngine(config.contract_rules, tasks_dir=config.tasks_dir)
+            if ContractPropagationEngine is not None
+            else None
+        )
 
     async def trigger_task(self, task_id: int) -> None:
         """Trigger execution of a PENDING_TRIGGER task.
@@ -535,6 +559,20 @@ async def _process_task(task_id: int, task_file: str, config: LoopEngineConfig,
     if approved:
         state.update_state(task_id, TaskState.CLOSED)
         print(f"[pipeline] Task #{task_id} CLOSED.")
+
+        # --- Contract Propagation (LE-6) — dispatch downstream tasks ---
+        diff = extract_task_diff(task_path) or ""
+        if ContractPropagationEngine is not None:
+            propagation_engine = ContractPropagationEngine(
+                config.contract_rules, tasks_dir=config.tasks_dir
+            )
+            dispatched = propagation_engine.process_task_closure(
+                task_id, task_file, diff, REPO_ROOT, state
+            )
+            if dispatched:
+                print(f"[pipeline] Contract propagation dispatched {len(dispatched)} downstream task(s):")
+                for d in dispatched:
+                    print(f"  - Task #{d['task_id']}: {d['title']} ({d['file']})")
     else:
         print(f"[pipeline] Closure rejected for task #{task_id}. Stays in review.")
 
diff --git a/loop-engine/models.py b/loop-engine/models.py
index c579322..4a78e6b 100644
--- a/loop-engine/models.py
+++ b/loop-engine/models.py
@@ -92,6 +92,92 @@ class StackProfileConfig(BaseModel):
     model_preferences: dict[str, list[str]] = Field(default_factory=dict, description="Optional per-category model overrides")
 
 
+class DownstreamTaskTemplate(BaseModel):
+    """Template for a downstream task generated by the Contract Propagation Engine (LE-6).
+
+    The ``title_template`` and ``goal_template`` support ``{contract_name}``,
+    ``{triggering_task_id}``, and (goal only) ``{files}`` format placeholders.
+    """
+    title_template: str = Field(..., description="Template for downstream task title, e.g. 'Sync TypeScript SDK with updated {contract_name}'")
+    stack: str = Field("generic", description="Stack profile for the downstream task, e.g. 'node-ts', 'kotlin-android'")
+    goal_template: str = Field(..., description="Template for task goal")
+    acceptance_criteria: list[str] = Field(default_factory=list, description="Standard AC checkboxes for the task")
+
+
+class ContractRuleConfig(BaseModel):
+    """Declarative contract mutation rule — maps contract file globs to downstream tasks."""
+    name: str = Field(..., description="Canonical rule name, e.g. 'shared-schema', 'openapi-spec'")
+    patterns: list[str] = Field(default_factory=list, description="Glob patterns for contract files, e.g. ['packages/shared-schema/**', 'openapi/**']")
+    downstream_tasks: list[DownstreamTaskTemplate] = Field(default_factory=list, description="List of tasks to generate upon mutation")
+
+
+def _default_contract_rules() -> list["ContractRuleConfig"]:
+    """Sensible default contract propagation rules (LE-6)."""
+    return [
+        ContractRuleConfig(
+            name="openapi-spec",
+            patterns=["openapi/**", "contracts/*.yaml", "contracts/*.json"],
+            downstream_tasks=[
+                DownstreamTaskTemplate(
+                    title_template="Regenerate API client for updated {contract_name}",
+                    stack="node-ts",
+                    goal_template="Regenerate the API client / SDK to match the modified {contract_name} contract. Files changed: {files}",
+                    acceptance_criteria=[
+                        "API client regenerated from the modified OpenAPI specification",
+                        "Generated types match the new contract shapes",
+                        "Build and lint pass for the generated client",
+                    ],
+                )
+            ],
+        ),
+        ContractRuleConfig(
+            name="prisma-schema",
+            patterns=["*.prisma", "prisma/**"],
+            downstream_tasks=[
+                DownstreamTaskTemplate(
+                    title_template="Sync Prisma schema migration for {contract_name}",
+                    stack="node-ts",
+                    goal_template="Generate and apply the Prisma migration matching the modified {contract_name}. Files changed: {files}",
+                    acceptance_criteria=[
+                        "Prisma migration generated from the updated schema",
+                        "Migration applies cleanly against the development database",
+                    ],
+                )
+            ],
+        ),
+        ContractRuleConfig(
+            name="protobuf",
+            patterns=["proto/**", "*.proto"],
+            downstream_tasks=[
+                DownstreamTaskTemplate(
+                    title_template="Regenerate gRPC stubs for updated {contract_name}",
+                    stack="generic",
+                    goal_template="Regenerate the gRPC/protobuf stubs for the modified {contract_name} contract. Files changed: {files}",
+                    acceptance_criteria=[
+                        "gRPC stubs regenerated for all target languages",
+                        "Server and client packages compile against the new stubs",
+                    ],
+                )
+            ],
+        ),
+        ContractRuleConfig(
+            name="shared-schema",
+            patterns=["packages/shared-schema/**", "shared/schemas/**"],
+            downstream_tasks=[
+                DownstreamTaskTemplate(
+                    title_template="Propagate shared schema changes for {contract_name}",
+                    stack="generic",
+                    goal_template="Propagate the modified {contract_name} to all consuming services. Files changed: {files}",
+                    acceptance_criteria=[
+                        "All consumers of the shared schema are updated",
+                        "Cross-service contract tests pass",
+                    ],
+                )
+            ],
+        ),
+    ]
+
+
 class LoopEngineConfig(BaseModel):
     """Root configuration — loop-engine.jsonc."""
     # Providers
@@ -152,3 +238,9 @@ class LoopEngineConfig(BaseModel):
     # Stack Profiles
     stacks_dir: str = Field("stacks", description="Directory containing stack profile YAML/JSON definitions")
     default_stack: str = Field("generic", description="Fallback stack when detection finds no match")
+
+    # Contract Propagation (LE-6)
+    contract_rules: list[ContractRuleConfig] = Field(
+        default_factory=_default_contract_rules,
+        description="Declarative rules mapping contract file mutations to downstream task generators",
+    )
diff --git a/loop-engine/test_contracts.py b/loop-engine/test_contracts.py
new file mode 100644
index 0000000..379c995
--- /dev/null
+++ b/loop-engine/test_contracts.py
@@ -0,0 +1,492 @@
+"""Tests for Contract Propagation & Downstream Task Dispatcher (LE-6 / Task 138).
+
+Covers:
+1. ``extract_modified_paths`` — git diff path parsing (additions, updates,
+   deletions, dedup, empty).
+2. ``match_contract_rules`` — glob pattern matching across contract families
+   (shared-schema ``**``, openapi ``*.yaml``, prisma extension).
+3. ``discover_next_task_id`` — sequential, gap, multi-folder, and empty layouts.
+4. ``ContractPropagationEngine.process_task_closure`` — batch generation with
+   sequential IDs, canonical Markdown headers, state registration, formatting,
+   and the non-contract no-op.
+5. Daemon integration — task closure triggers downstream backlog tasks through
+   the real ``_process_task`` closure hook.
+"""
+import asyncio
+import os
+import sys
+from pathlib import Path
+from unittest.mock import AsyncMock, MagicMock, patch
+
+sys.path.insert(0, os.path.dirname(__file__))
+
+from models import ContractRuleConfig, DownstreamTaskTemplate, LoopEngineConfig, TaskState
+from state import StateMachine
+
+import daemon
+from contracts import (
+    ContractPropagationEngine,
+    discover_next_task_id,
+    extract_modified_paths,
+    match_contract_rules,
+)
+
+
+# ---------------------------------------------------------------------------
+# Fixtures / helpers
+# ---------------------------------------------------------------------------
+
+_MODIFIED_DIFF = """diff --git a/openapi/contract.yaml b/openapi/contract.yaml
+index 1111111..2222222 100644
+--- a/openapi/contract.yaml
++++ b/openapi/contract.yaml
+@@ -1,3 +1,4 @@
+-old: value
++new: value
+"""
+
+_ADDED_DIFF = """diff --git a/packages/shared-schema/v1/types.ts b/packages/shared-schema/v1/types.ts
+new file mode 100644
+index 0000000..e69de29
+--- /dev/null
++++ b/packages/shared-schema/v1/types.ts
+@@ -0,0 +1 @@
++export type User = { id: string };
+"""
+
+_DELETED_DIFF = """diff --git a/contracts/legacy.yaml b/contracts/legacy.yaml
+deleted file mode 100644
+index 3333333..0000000
+--- a/contracts/legacy.yaml
++++ /dev/null
+@@ -1,2 +0,0 @@
+-legacy: gone
+"""
+
+
+def _openapi_rule(templates=None):
+    """Contract rule for OpenAPI specs with one downstream SDK sync task."""
+    return ContractRuleConfig(
+        name="openapi-spec",
+        patterns=["openapi/**", "contracts/*.yaml", "contracts/*.json"],
+        downstream_tasks=templates or [
+            DownstreamTaskTemplate(
+                title_template="Sync SDK with updated {contract_name}",
+                stack="node-ts",
+                goal_template="Update SDK for {contract_name}. Files: {files}",
+                acceptance_criteria=["SDK updated", "Tests pass"],
+            )
+        ],
+    )
+
+
+def _two_template_rule():
+    """OpenAPI rule with TWO downstream templates (batch generation)."""
+    return ContractRuleConfig(
+        name="openapi-spec",
+        patterns=["openapi/**"],
+        downstream_tasks=[
+            DownstreamTaskTemplate(
+                title_template="Regenerate API client for updated {contract_name}",
+                stack="node-ts",
+                goal_template="Regenerate client for {contract_name}. Files: {files}",
+                acceptance_criteria=["Client regenerated"],
+            ),
+            DownstreamTaskTemplate(
+                title_template="Update API docs for {contract_name}",
+                stack="generic",
+                goal_template="Update docs referencing {contract_name}. Files: {files}",
+                acceptance_criteria=["Docs updated"],
+            ),
+        ],
+    )
+
+
+def _make_workspace(tmp_path):
+    """Build tasks/{backlog,in-progress,qa,completed,archive} under tmp_path."""
+    for sub in ("backlog", "in-progress", "qa", "completed", "archive"):
+        (tmp_path / "tasks" / sub).mkdir(parents=True, exist_ok=True)
+    return tmp_path
+
+
+# ---------------------------------------------------------------------------
+# 1. extract_modified_paths
+# ---------------------------------------------------------------------------
+
+def test_extract_modified_paths_new_file():
+    paths = extract_modified_paths(_ADDED_DIFF)
+    assert paths == ["packages/shared-schema/v1/types.ts"]
+
+
+def test_extract_modified_paths_modified_file():
+    assert extract_modified_paths(_MODIFIED_DIFF) == ["openapi/contract.yaml"]
+
+
+def test_extract_modified_paths_deletion():
+    assert extract_modified_paths(_DELETED_DIFF) == ["contracts/legacy.yaml"]
+
+
+def test_extract_modified_paths_deduplicates():
+    diff = _MODIFIED_DIFF + _MODIFIED_DIFF
+    assert extract_modified_paths(diff) == ["openapi/contract.yaml"]
+
+
+def test_extract_modified_paths_empty_diff():
+    assert extract_modified_paths("") == []
+    assert extract_modified_paths("no diff headers here") == []
+
+
+# ---------------------------------------------------------------------------
+# 2. match_contract_rules
+# ---------------------------------------------------------------------------
+
+def test_match_contract_rules_shared_schema_recursive():
+    rule = ContractRuleConfig(name="shared-schema", patterns=["packages/shared-schema/**"])
+    paths = ["packages/shared-schema/v1/types.ts", "src/app.ts"]
+    matches = match_contract_rules(paths, [rule])
+    assert len(matches) == 1
+    matched_rule, matched_files = matches[0]
+    assert matched_rule.name == "shared-schema"
+    assert matched_files == ["packages/shared-schema/v1/types.ts"]
+
+
+def test_match_contract_rules_openapi_yaml():
+    rule = _openapi_rule()
+    paths = ["openapi/petstore.yaml", "src/main.ts"]
+    matches = match_contract_rules(paths, [rule])
+    assert matches[0][1] == ["openapi/petstore.yaml"]
+
+
+def test_match_contract_rules_prisma_extension():
+    rule = ContractRuleConfig(name="prisma-schema", patterns=["*.prisma", "prisma/**"])
+    paths = ["prisma/schema.prisma", "server/index.ts"]
+    matches = match_contract_rules(paths, [rule])
+    assert matches[0][1] == ["prisma/schema.prisma"]
+
+
+def test_match_contract_rules_no_match_returns_empty():
+    rule = _openapi_rule()
+    matches = match_contract_rules(["src/main.ts", "docs/README.md"], [rule])
+    assert matches == []
+
+
+# ---------------------------------------------------------------------------
+# 3. discover_next_task_id
+# ---------------------------------------------------------------------------
+
+def test_discover_next_task_id_sequential(tmp_path):
+    _make_workspace(tmp_path)
+    for i in (1, 2, 3):
+        (tmp_path / "tasks" / "backlog" / f"{i:02d}-task.md").write_text(f"# Task {i}\n")
+    assert discover_next_task_id(tmp_path / "tasks") == 4
+
+
+def test_discover_next_task_id_gap(tmp_path):
+    _make_workspace(tmp_path)
+    (tmp_path / "tasks" / "backlog" / "01-a.md").write_text("# Task 1\n")
+    (tmp_path / "tasks" / "qa" / "05-b.md").write_text("# Task 5\n")
+    assert discover_next_task_id(tmp_path / "tasks") == 6
+
+
+def test_discover_next_task_id_multi_folder(tmp_path):
+    _make_workspace(tmp_path)
+    layout = {
+        "backlog": [7, 12],
+        "in-progress": [8],
+        "qa": [9],
+        "completed": [10],
+        "archive": [11, 13],
+    }
+    for folder, ids in layout.items():
+        for i in ids:
+            (tmp_path / "tasks" / folder / f"{i:02d}-t.md").write_text(f"# Task {i}\n")
+    assert discover_next_task_id(tmp_path / "tasks") == 14
+
+
+def test_discover_next_task_id_empty(tmp_path):
+    _make_workspace(tmp_path)
+    assert discover_next_task_id(tmp_path / "tasks") == 1
+
+
+# ---------------------------------------------------------------------------
+# 4. ContractPropagationEngine.process_task_closure
+# ---------------------------------------------------------------------------
+
+def test_process_task_closure_generates_batch_with_sequential_ids(tmp_path):
+    _make_workspace(tmp_path)
+    (tmp_path / "tasks" / "backlog" / "05-existing.md").write_text("# Task 5\n")
+    state = StateMachine(str(tmp_path / "loop.db"))
+    try:
+        engine = ContractPropagationEngine(
+            rules=[_two_template_rule()], tasks_dir="tasks"
+        )
+        dispatched = engine.process_task_closure(
+            task_id=42,
+            task_file="tasks/completed/05-existing.md",
+            diff_text=_MODIFIED_DIFF,
+            repo_root=tmp_path,
+            state=state,
+        )
+        assert len(dispatched) == 2
+        assert [d["task_id"] for d in dispatched] == [6, 7]
+        assert dispatched[0]["file"] == "tasks/backlog/06-regenerate-api-client-for-updated-openapi-spec.md"
+        assert dispatched[1]["file"] == "tasks/backlog/07-update-api-docs-for-openapi-spec.md"
+
+        first = (tmp_path / "tasks" / "backlog" / "06-regenerate-api-client-for-updated-openapi-spec.md").read_text()
+        second = (tmp_path / "tasks" / "backlog" / "07-update-api-docs-for-openapi-spec.md").read_text()
+
+        # Canonical markdown headers for both generated tasks
+        for body, task_id, title in (
+            (first, 6, "Regenerate API client for updated openapi-spec"),
+            (second, 7, "Update API docs for openapi-spec"),
+        ):
+            assert body.startswith(f"# Task {task_id}: {title}\n")
+            assert "**Source:** contract-propagation" in body
+            assert "**Triggered-By:** Task 42" in body
+            assert "**Stack:**" in body
+            assert "**Type:** feature" in body
+            assert "**Status:** open" in body
+            assert "## Goal" in body
+            assert "## Source Context" in body
+            assert "## Acceptance Criteria" in body
+            assert "<!-- BEGIN_GIT_DIFF -->" in body
+            assert "<!-- END_GIT_DIFF -->" in body
+            assert "openapi/contract.yaml" in body
+    finally:
+        state.close()
+
+
+def test_process_task_closure_formats_title_goal_and_files(tmp_path):
+    _make_workspace(tmp_path)
+    state = StateMachine(str(tmp_path / "loop.db"))
+    try:
+        rule = ContractRuleConfig(
+            name="shared-schema",
+            patterns=["packages/shared-schema/**"],
+            downstream_tasks=[
+                DownstreamTaskTemplate(
+                    title_template="Propagate {contract_name} from Task {triggering_task_id}",
+                    stack="generic",
+                    goal_template="Sync {contract_name} consumers. Files: {files}",
+                    acceptance_criteria=["Consumers updated"],
+                )
+            ],
+        )
+        dispatched = ContractPropagationEngine(rules=[rule], tasks_dir="tasks").process_task_closure(
+            task_id=9,
+            task_file="tasks/completed/09-x.md",
+            diff_text=_ADDED_DIFF,
+            repo_root=tmp_path,
+            state=state,
+        )
+        assert len(dispatched) == 1
+        body = (tmp_path / "tasks" / "backlog" / "01-propagate-shared-schema-from-task-9.md").read_text()
+        assert "# Task 1: Propagate shared-schema from Task 9" in body
+        assert "Sync shared-schema consumers. Files: packages/shared-schema/v1/types.ts" in body
+        assert "- packages/shared-schema/v1/types.ts" in body
+        assert "- [ ] Consumers updated" in body
+    finally:
+        state.close()
+
+
+def test_process_task_closure_registers_in_state_backlog(tmp_path):
+    _make_workspace(tmp_path)
+    state = StateMachine(str(tmp_path / "loop.db"))
+    try:
+        disposed = ContractPropagationEngine(
+            rules=[_openapi_rule()], tasks_dir="tasks"
+        ).process_task_closure(
+            task_id=1,
+            task_file="tasks/completed/01-x.md",
+            diff_text=_MODIFIED_DIFF,
+            repo_root=tmp_path,
+            state=state,
+        )
+        target = tmp_path / "tasks" / "backlog" / "01-sync-sdk-with-updated-openapi-spec.md"
+        assert target.exists()
+        record = state.get_task_by_file(str(target))
+        assert record is not None
+        assert record["state"] == "backlog"
+        assert disposed[0]["task_id"] == record["task_id"]
+    finally:
+        state.close()
+
+
+def test_process_task_closure_non_contract_noop(tmp_path):
+    _make_workspace(tmp_path)
+    state = StateMachine(str(tmp_path / "loop.db"))
+    try:
+        diff = """diff --git a/src/main.ts b/src/main.ts
+index 1111111..2222222 100644
+--- a/src/main.ts
++++ b/src/main.ts
+@@ -1 +1 @@
+-console.log("old");
++console.log("new");
+"""
+        dispatched = ContractPropagationEngine(
+            rules=[_openapi_rule()], tasks_dir="tasks"
+        ).process_task_closure(
+            task_id=1,
+            task_file="tasks/completed/01-x.md",
+            diff_text=diff,
+            repo_root=tmp_path,
+            state=state,
+        )
+        assert dispatched == []
+        assert list((tmp_path / "tasks" / "backlog").glob("*.md")) == []
+    finally:
+        state.close()
+
+
+def test_loop_engine_config_default_contract_rules():
+    cfg = LoopEngineConfig(approval={"chat_id": 0})
+    names = [r.name for r in cfg.contract_rules]
+    assert names == ["openapi-spec", "prisma-schema", "protobuf", "shared-schema"]
+    openapi = cfg.contract_rules[0]
+    assert openapi.patterns == ["openapi/**", "contracts/*.yaml", "contracts/*.json"]
+    assert openapi.downstream_tasks[0].stack == "node-ts"
+
+
+# ---------------------------------------------------------------------------
+# 5. Daemon integration
+# ---------------------------------------------------------------------------
+
+def _make_daemon_stubs(config):
+    router = MagicMock()
+    router.route_plan.return_value = {"plan": "routing"}
+    router.call_llm.return_value = "Approved plan text"
+    gateway = MagicMock()
+    gateway.request_approval = AsyncMock(return_value=True)
+    executor = MagicMock()
+    qa = MagicMock()
+    qa.run_review.return_value = {"result": "APPROVED"}
+    brainstorm = MagicMock()
+    brainstorm.should_trigger.return_value = False
+    return router, gateway, executor, qa, brainstorm
+
+
+def test_daemon_init_wires_propagation_engine():
+    config = LoopEngineConfig(approval={"chat_id": 0})
+    state = MagicMock()
+    router = MagicMock()
+    gateway = MagicMock()
+    executor = MagicMock()
+    qa = MagicMock()
+    brainstorm = MagicMock()
+    d = daemon.LoopEngineDaemon(config, state, router, gateway, executor, qa, brainstorm)
+    assert isinstance(d.propagation_engine, ContractPropagationEngine)
+    assert d.propagation_engine.tasks_dir == Path("tasks")
+
+
+def test_daemon_task_closure_dispatches_downstream_tasks(tmp_path):
+    """Real _process_task closure hook: CLOSED + contract diff -> backlog tasks."""
+    ws = _make_workspace(tmp_path)
+    (ws / "tasks" / "backlog" / "10-existing.md").write_text("# Task 10\n")
+    config = LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto")
+    router, gateway, executor, qa, brainstorm = _make_daemon_stubs(config)
+
+    task_file = ws / "tasks" / "completed" / "10-existing.md"
+    task_file.write_text(
+        "# Task 10: Contract Mutation\n"
+        "**Source:** orchestrator\n"
+        "**Type:** feature\n"
+        "## Goal\nUpdate the OpenAPI contract.\n"
+        "## Factual Git Diff\n"
+        "<!-- BEGIN_GIT_DIFF -->\n"
+        + _MODIFIED_DIFF +
+        "<!-- END_GIT_DIFF -->\n"
+    )
+
+    state = StateMachine(str(ws / "loop.db"))
+    tid = state.register_task(str(task_file), TaskState.AWAITING_CLOSURE)
+    try:
+        async def _run():
+            await daemon._process_task(
+                tid, str(task_file), config, state, router, gateway, executor, qa, brainstorm
+            )
+
+        async def _fake_execute_and_qa(*args, **kwargs):
+            return {"result": "PASSED", "report": "ok"}
+
+        with patch.object(daemon, "_execute_and_qa", new=_fake_execute_and_qa):
+            with patch.object(daemon, "REPO_ROOT", ws):
+                asyncio.run(_run())
+
+        # Trigger task reached CLOSED
+        assert state.get_task(tid)["state"] == "closed"
+
+        # Downstream task generated with next sequential id (11) using the
+        # config's DEFAULT openapi-spec rule template.
+        backlog_files = sorted((ws / "tasks" / "backlog").glob("*.md"))
+        names = [f.name for f in backlog_files]
+        assert any(name.startswith("11-regenerate-api-client-for-updated-openapi-spec") for name in names)
+        generated = ws / "tasks" / "backlog" / "11-regenerate-api-client-for-updated-openapi-spec.md"
+        assert generated.exists()
+        body = generated.read_text()
+        assert f"**Triggered-By:** Task {tid}" in body
+        assert "**Source:** contract-propagation" in body
+        # Registered in the state machine as backlog
+        assert state.get_task_by_file(str(generated))["state"] == "backlog"
+    finally:
+        state.close()
+
+
+def test_daemon_task_closure_noop_without_contract_diff(tmp_path):
+    """Real _process_task closure hook: non-contract diff -> no backlog tasks."""
+    ws = _make_workspace(tmp_path)
+    config = LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto")
+    router, gateway, executor, qa, brainstorm = _make_daemon_stubs(config)
+
+    task_file = ws / "tasks" / "completed" / "20-regular.md"
+    task_file.write_text(
+        "# Task 20: Regular Change\n"
+        "**Source:** orchestrator\n"
+        "**Type:** feature\n"
+        "## Goal\nRefactor a service.\n"
+        "## Factual Git Diff\n"
+        "<!-- BEGIN_GIT_DIFF -->\n"
+        "diff --git a/src/main.ts b/src/main.ts\n"
+        "index 1111111..2222222 100644\n"
+        "--- a/src/main.ts\n"
+        "+++ b/src/main.ts\n"
+        "@@ -1 +1 @@\n"
+        "-old\n"
+        "+new\n"
+        "<!-- END_GIT_DIFF -->\n"
+    )
+
+    state = StateMachine(str(ws / "loop.db"))
+    tid = state.register_task(str(task_file), TaskState.AWAITING_CLOSURE)
+    try:
+        async def _run():
+            await daemon._process_task(
+                tid, str(task_file), config, state, router, gateway, executor, qa, brainstorm
+            )
+
+        async def _fake_execute_and_qa(*args, **kwargs):
+            return {"result": "PASSED", "report": "ok"}
+
+        with patch.object(daemon, "_execute_and_qa", new=_fake_execute_and_qa):
+            with patch.object(daemon, "REPO_ROOT", ws):
+                asyncio.run(_run())
+
+        assert state.get_task(tid)["state"] == "closed"
+        assert list((ws / "tasks" / "backlog").glob("*.md")) == []
+    finally:
+        state.close()
+
+
+if __name__ == "__main__":
+    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
+    passed = failed = 0
+    for t in tests:
+        try:
+            t(Path("/tmp/contracts-test-ws")) if "tmp_path" in t.__code__.co_varnames else t()
+            print(f"  PASS: {t.__name__}")
+            passed += 1
+        except Exception as e:
+            print(f"  FAIL: {t.__name__}: {e}")
+            failed += 1
+    print(f"\n{passed} passed, {failed} failed")
+    sys.exit(1 if failed else 0)
\ No newline at end of file
```
<!-- END_GIT_DIFF -->