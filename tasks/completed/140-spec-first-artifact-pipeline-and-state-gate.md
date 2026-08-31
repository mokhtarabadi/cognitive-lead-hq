# Task 140: Spec-First Artifact Pipeline & State Gate

**File:** `tasks/completed/140-spec-first-artifact-pipeline-and-state-gate.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Goal

Implement a Spec-First Artifact Pipeline & State Gate (LE-8) in the Cognitive Loop Engine: tasks whose content or approved plan introduces architectural changes, API contracts, or database schema mutations must have verified spec artifacts (ADR, PRD, Contract, Data Model) present in the workspace or staged diff BEFORE code implementation begins. The daemon enforces this as a fail-fast state gate between Plan Approval and `IMPLEMENTING`, persisting verified artifact links in SQLite state (`spec_artifacts`), and the gate is fully configurable via `spec_gate` JSONC options with sensible default requirement rules.

## Blueprint Reference

Blueprint decisions D1–D5 for LE-8 are logged under `## Manager Decisions`. D1 (the core Spec-First State Gate principle) is pre-seeded by the Orchestrator; D2–D5 are recorded during execution as `[EXECUTION-DETECTED]` entries per decision-logging mandate.

## Manager's Notes

- Operator must follow the exact execution order in the implementation task: models → state → specs → daemon → tests → docs.
- Baseline gate: existing suite must stay green (224 passed) before changes; final suite must be ≥ 240 passed, 0 failed.
- ZAC applies: only the authorized `git mv` Kanban moves; no `git add`/`commit`/`push`.

## Local TODOs

- [x] Initial codebase exploration (models, state, daemon, contracts patterns)
- [x] Define Spec schemas in `loop-engine/models.py` (Step 2)
- [x] Extend SQLite StateMachine in `loop-engine/state.py` (Step 3)
- [x] Implement `loop-engine/specs.py` (Step 4)
- [x] Integrate gate into `loop-engine/daemon.py` (Step 5)
- [x] Create `loop-engine/test_specs.py` suite (Step 6)
- [x] Update `docs/loop-engine/configuration.md` (Step 7)
- [x] Verify functionality

## Acceptance Criteria

- [x] `SpecArtifactType` enum (`adr`/`prd`/`contract`/`data_model`), `SpecRequirementRule`, `SpecGateConfig`, and `_default_spec_rules()` with the three default rules (architecture-decision, api-contract, database-schema) exist in `models.py`; `LoopEngineConfig` gains `spec_gate: SpecGateConfig`.
- [x] `state.py` `tasks` table includes `spec_artifacts TEXT DEFAULT NULL`; `StateMachine.__init__` performs a safe `ALTER TABLE` migration for existing databases; `set_spec_artifacts`/`get_spec_artifacts` persist/retrieve JSON lists.
- [x] `loop-engine/specs.py` defines `SpecValidationResult` and `SpecGateEngine` with `evaluate_requirements` (keyword scan of task+plan) and `validate_artifacts` (fnmatch/`rglob` workspace scan + diff-path scan, Markdown report, `passed = len(errors)==0`).
- [x] `daemon._process_task` runs the gate immediately after Plan Approval and before `TaskState.IMPLEMENTING`: on failure → `CRASHED` + `set_qa_feedback(report_md)` + halts; on success → `set_spec_artifacts(found)` + proceeds.
- [x] `loop-engine/test_specs.py` covers rule evaluation, workspace/diff artifact validation (pass/fail), report content, state migration + accessors, and daemon integration (crash before IMPLEMENTING vs proceed).
- [x] `docs/loop-engine/configuration.md` documents Spec-First Governance and `spec_gate` options.
- [x] Full suite ≥ 240 passed, 0 failed, 0 regressions (baseline 224).

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** ≥ 240 passed, 0 failed (baseline 224)
- **Actual result:** 247 passed, 0 failed — baseline 224 + 23 new (`test_specs.py`); no regressions
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence`.

## Manager Decisions

`**[2026-08-31] [D1] [ORCHESTRATOR-DETECTED]:** Spec-First State Gate Preceding Implementation`
- **Rationale:** Enforcing that tasks introducing architectural changes or schema mutations must have verified spec artifacts (ADR, PRD, Contract, Data Model) before code implementation prevents architectural debt and ensures compliance.
- **Alternatives considered:** Relying solely on human review or prose guidelines without automated daemon enforcement.
- **Impact:** Automatically halts un-specified code generation; persists auditable spec artifact links in SQLite state.

`**[2026-08-31] [D2] [EXECUTION-DETECTED]:** Inert-by-default gate — `spec_gate.rules` defaults to `[]` with `_default_spec_rules()` as the opt-in wiring helper`
- **Rationale:** The LE-8 spec mandates `SpecGateConfig.rules = []` as the default; empty rules plus `validate_artifacts([]) → passed=True` guarantee zero behavioral change for existing engines/configs until a Manager explicitly configures rules, avoiding surprise crashes and breaking pre-existing tests.
- **Alternatives considered:** Having `rules` default to `_default_spec_rules()` — this would fire the gate on every architectural task out of the box (including this repo's own task files) without Manager opt-in.
- **Impact:** Existing pipelines stay green (247/247); adoption is opt-in via JSONC `spec_gate.rules` or explicit `SpecGateConfig(rules=_default_spec_rules())`.

`**[2026-08-31] [D3] [EXECUTION-DETECTED]:** Gate position is step 2.5 — after Plan Approval, before `IMPLEMENTING`/preflight`
- **Rationale:** Enforces spec-first ordering: the approved plan (which carries architectural/contract keywords) is available at that point, and crashing there prevents any executor/toolchain cost.
- **Alternatives considered:** Running the gate at Brainstorm/Planning entry (the plan may not exist yet) or after implementation (defeats the fail-fast purpose).
- **Impact:** Un-specified tasks never reach `IMPLEMENTING`; crash lands with `qa_feedback` report for audit.

`**[2026-08-31] [D4] [EXECUTION-DETECTED]:** ADR rule requires `adr` with `docs/adr/**` targets only`
- **Rationale:** Dropped the initial `PRD` artifact from the architecture-decision rule so the default rule strictly matches the LE-8 spec line (ADR), avoiding an unexpected second required artifact for architecture tasks.
- **Alternatives considered:** Keeping PRD as a co-requisite — over-broadens the default; PRD is not in the LE-8 rule line.
- **Impact:** Default rule-shape test asserts `[SpecArtifactType.ADR]`; architecture tasks need only an ADR/architecture doc.

`**[2026-08-31] [D5] [EXECUTION-DETECTED]:** Diff-scanning supported in `validate_artifacts` but the state-gate call passes `diff_text=""``
- **Rationale:** At gate time (pre-implementation) the staged diff does not yet exist; the workspace scan is the honest enforcement source. Diff-path scanning remains a deterministic capability for linters/tooling and future post-implementation spec checks.
- **Alternatives considered:** Calling the gate again post-execution with the real diff — out of scope and would defeat the fail-fast property.
- **Impact:** `validate_artifacts` is generic; the daemon passes an empty diff, so the gate only accepts artifacts already present in the workspace (e.g., pre-committed specs).

## Risk & Rollback

- **Risk:** The gate could crash legitimate tasks whose spec artifacts live outside `target_directories`, or default keyword rules could over-trigger.
- **Rollback plan:** Set `spec_gate.enabled = false` (or empty `rules`) in `loop-engine.jsonc` — the gate becomes a no-op; the SQLite `ALTER TABLE ... ADD COLUMN` migration is additive and non-destructive (existing DBs keep functioning; drop the column or recreate the DB to remove tracking).

---

## Execution Log & Reasoning

### Files Modified

- `loop-engine/models.py` — added `SpecArtifactType` enum, `SpecRequirementRule`, `SpecGateConfig`, `_default_spec_rules()`, and `LoopEngineConfig.spec_gate`.
- `loop-engine/state.py` — added `spec_artifacts TEXT DEFAULT NULL` to `_SCHEMA`, safe `ALTER TABLE` migration in `__init__`, and `set_spec_artifacts`/`get_spec_artifacts` JSON accessors.
- `loop-engine/specs.py` — new: `SpecValidationResult` dataclass + `SpecGateEngine` (evaluate_requirements/validate_artifacts) + pure helpers `_find_matching_files`, `_paths_in_diff`, `_build_report`.
- `loop-engine/daemon.py` — `SpecGateEngine` import with fallback; step 2.5 gate after Plan Approval, before `IMPLEMENTING`.
- `loop-engine/test_specs.py` — new: 23 tests.
- `docs/loop-engine/configuration.md` — LE-8 Spec-First Artifact Governance section.
- `CHANGELOG.md` — Task 140 entry under `### Added` (Parse-Then-Append).

### Architectural Reasoning

- **Inert-by-default gate:** `spec_gate.rules` defaults to `[]` (matching the literal LE-8 spec) and `validate_artifacts([])` returns `passed=True` — so zero existing tests/configs change behavior while the gate is fully activatable via `_default_spec_rules()`. This mirrors the LE-6 `contract_rules` default pattern.
- **Determinism:** `evaluate_requirements`/`validate_artifacts` are side-effect-free; the daemon owns all state transitions — same separation as LE-6 (`extract_modified_paths`/`match_contract_rules` pure, engine owns writes).
- **Diff staging support:** `validate_artifacts` accepts `diff_text` and parses `diff --git` b-side headers (reused pattern from `contracts.py`) so a task that stages its ADR/contract in the active diff satisfies the gate without an executor run. The daemon passes `diff_text=""` at gate time (the diff only exists AFTER implementation) — primarily workspace scan for the state gate, diff scanning available for tooling/linters.
- **Migration safety:** `ALTER TABLE ... ADD COLUMN` wrapped in try/except `sqlite3.OperationalError` — idempotent on new DBs (duplicate column), additive on legacy DBs. Verified by test on a hand-built legacy schema.
- **Report as feedback:** `report_md` written into `qa_feedback` gives the crash an auditable, actionable trail consistent with preflight/toolchain fail-fast behavior.

### Test Outcomes

- Baseline (pre-change): **224 passed** (`uv run --project loop-engine --with pytest pytest loop-engine/ -q`).
- Targeted new suite: `loop-engine/test_specs.py` → **23 passed** in 0.43s.
- Full suite post-implementation: **247 passed, 0 failed, 0 regressions** (224 + 23 = 247). Gate `>= 240` satisfied.
- `py_compile` clean on all 5 changed Python files.
- Diff scope verified: `git diff --stat` shows only `loop-engine/` (4 modified + 2 new) and `docs/loop-engine/configuration.md`; task file in `tasks/in-progress/`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index ff51751..875c811 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Spec-First Artifact Pipeline & State Gate (Task 140)** — Added Spec-First Artifact Pipeline & State Gate (`loop-engine/specs.py`) with requirement evaluation, workspace/diff artifact validation, SQLite `spec_artifacts` tracking in `state.py`, and fail-fast daemon state gate. `SpecArtifactType` enum (`adr`/`prd`/`contract`/`data_model`), `SpecRequirementRule`, `SpecGateConfig`, `_default_spec_rules()` (architecture-decision → `docs/adr/**`+`docs/architecture.md`; api-contract → `contracts/**`+`openapi/**`+`proto/**`; database-schema → `docs/data_model.md`+`prisma/**`+`migrations/**`), and `LoopEngineConfig.spec_gate` (default `enabled=true`, `rules=[]`) in `loop-engine/models.py`; `StateMachine` migration adding `spec_artifacts TEXT DEFAULT NULL` via safe `ALTER TABLE ... ADD COLUMN` (idempotent on new DBs, non-destructive on legacy DBs) plus `set_spec_artifacts`/`get_spec_artifacts` JSON accessors (`[]` on unset/corrupt) in `loop-engine/state.py`; `SpecValidationResult` dataclass + `SpecGateEngine` (`evaluate_requirements` lowercased keyword scan of task+plan, `validate_artifacts` `rglob`+`fnmatch` workspace scan and `diff --git` b-side diff-path scan with structured `# Spec-First Gate Report` Markdown, empty-rule immediate pass) in `loop-engine/specs.py`; `daemon._process_task` step 2.5 gate immediately after Plan Approval before `TaskState.IMPLEMENTING` — `ImportError` fallback, on failure `CRASHED` + `set_qa_feedback(report_md)` + halt before any code generation, on success `set_spec_artifacts(found)` + proceed; 23 new tests in `loop-engine/test_specs.py` (requirement evaluation, workspace/diff artifact validation pass/fail + report content, diff header parsing/dedup, state migration idempotency + accessors round-trip/corrupt fallback, daemon integration pass-proceeds/fail-crashes/disabled/routine-bypass, config defaults + rule shapes); documented in `docs/loop-engine/configuration.md` (LE-8 section with pipeline position, migration notes, schema tables, default rules, and JSONC example); verified **247 passed, 0 failed** (baseline 224, +23 new).
 - **No-Manual-DTO Mandate & Type Drift Sentinel (Task 139)** — Added the No-Manual-DTO Mandate (`prompts/fragments/20-no_manual_dto_mandate.md`, `<no_manual_dto_mandate>` XML block banning hand-authored duplicate interface models / request-response DTOs / data classes in consumer applications when a source-of-truth contract or shared schema exists, requiring import from the shared package (`@repo/shared-schema`, `packages/shared-schema`) or execution of the stack codegen toolchain (`pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`), with explicit reconciliation against the SOLID guardrails from `14-solid_programming_mandate.md`) and the Type Drift Sentinel (`loop-engine/sentinel.py`): `DriftCheckResult` + `TypeDriftSentinel` with default consumer (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) and allowed (`packages/shared-schema/**`, `contracts/**`, `openapi/**`, `proto/**`, `**/generated/**`, `**/build/**`, `**/dist/**`, `**/*.gen.*`) patterns, diff parsing (`diff --git` headers + `@@` hunks with per-line numbers), extension-dispatched TS/JS/Kotlin/Python declaration regexes with specificity-ordered cascade for unknown extensions, comment-only + explicit `drift-ignore` bypass, and actionable Markdown failure reports; integrated into the toolchain verification gate — `ToolchainRunner.run`/`run_sync` accept `diff_text` and fail fast on drift with `CommandResult(command="type-drift-sentinel", cmd_type="lint", passed=False, stderr=report)` before any lint/build/test command; `daemon._execute_and_qa` forwards `diff_text=diff` into the runner; `<system_version>` bumped **9.2.2 → 9.3.0**, `prompts/manifest.txt` registers `20-no_manual_dto_mandate.md` before `18-initialization.md`, `system-prompt.md` reassembled (78869 bytes, `lint_lint_system_prompt_sync` byte-identity ✅), `docs/conventions.md` gained `## No-Manual-DTO & Type Drift Standard` (summary pointer, fragment authoritative), documented in `docs/loop-engine/configuration.md` (LE-7 section); 24 new tests in `loop-engine/test_sentinel.py` (assembler inclusion + version + closing-tag normalization, TS/Kotlin/Python detection, shared-schema/generated exemptions, clean imports, `drift-ignore` bypass, report quality, custom patterns, ToolchainRunner fail-fast/pass-through, daemon `diff_text` forwarding); verified **224 passed, 0 failed** (baseline 200).
 - **Contract Propagation & Downstream Task Dispatcher (Task 138)** — Added Contract Propagation & Downstream Task Dispatcher (`loop-engine/contracts.py`) with declarative schema mutation rules, diff pattern matching, sequential next-ID task generation in `tasks/backlog/`, SQLite state registration, and daemon closure integration. `DownstreamTaskTemplate` + `ContractRuleConfig` Pydantic schemas and `LoopEngineConfig.contract_rules` defaults (`openapi-spec`, `prisma-schema`, `protobuf`, `shared-schema` with `title_template`/`goal_template` `{contract_name}`/`{triggering_task_id}`/`{files}` placeholders) in `loop-engine/models.py`; `extract_modified_paths` (regex `diff --git` header parsing, deduplicated), `match_contract_rules` (fnmatch globs like `packages/shared-schema/**`, `openapi/*.yaml`, `*.prisma`), `discover_next_task_id` (max numeric prefix + 1 across backlog/in-progress/qa/completed/archive), `ContractPropagationEngine.process_task_closure` writes canonical task files (`**Source:** contract-propagation`, `**Triggered-By:** Task <id>`, Goal/Source Context/Acceptance Criteria/Git Diff markers) and registers them as `BACKLOG` in the SQLite state machine; `daemon.py` closure hooks `_process_task` + `_reimplement_task` invoke the engine immediately after `CLOSED` (with `ImportError` fallback + `LoopEngineDaemon.propagation_engine` wiring), printing dispatched summaries; non-contract diffs are a no-op. 21 new tests in `loop-engine/test_contracts.py` (path extraction add/update/delete/dedup, glob matching, next-ID sequential/gap/multi-folder/empty, batch generation sequential IDs + headers, state registration, config defaults, daemon closure integration happy-path + no-op, daemon `__init__` wiring); documented in `docs/loop-engine/configuration.md` (LE-6 section with schema tables, generated-task shape, and JSONC example); verified **200 passed, 0 failed** (baseline 179).
 - **OpenCode Executor Stack Context Injection & Goal Plugin Guardrails (Task 136)** — Added OpenCode Executor Stack Context Injection & Goal Plugin Guardrails (`loop-engine/executor.py`) with structured XML prompt generation, skill loading directives, process group isolation (`start_new_session=True`), Goal Plugin blocker reason extraction, and concurrency semaphore enforcement. `_build_prompt` constructs XML-tagged sections (`<task_instructions>`, `<stack_context name/display_name>` with `MANDATORY: Load required skills via the native skill tool` + toolchain test/build/lint instructions, `<blueprint_context>`, `<qa_feedback>` with explicit address directive, `<goal_rules>` with `[goal:complete]`/`[goal:blocked: <reason>]`); `TERM_COMPLETE`/`TERM_BLOCKED` regexes now case-insensitive with optional blocker-reason capture; `HandsExecutor.__init__` creates `asyncio.Semaphore(config.max_parallel_tasks)` and `execute()` wraps the run in `async with self._semaphore:`; `_run_once` uses `idle.executing_timeout_seconds` (fallback 900.0), launches with `start_new_session=True` on POSIX, kills the process group via `os.killpg(SIGKILL)` on timeout (suppressing ProcessLookupError/AttributeError/PermissionError) with 2.0s drain, and returns timeout/blocked (with reason)/complete status dicts; 15 new tests in `loop-engine/test_executor.py` (prompt combos, token matching, semaphore throttling, process-group timeout kill, transport retries); 3 legacy LE-0.1 tests in `test_le0_fixes.py` updated to the new XML prompt format; documented in `docs/loop-engine/configuration.md` (LE-4 section); verified 163 passed, 0 failed (baseline 148).
diff --git a/docs/loop-engine/configuration.md b/docs/loop-engine/configuration.md
index 158c2b2..d25dd6c 100644
--- a/docs/loop-engine/configuration.md
+++ b/docs/loop-engine/configuration.md
@@ -514,6 +514,100 @@ an explicit `drift-ignore` comment is the only bypass.
 on the diff text already extracted by the daemon. Custom consumer/allowed globs are
 supported at construction time for callers that need to extend the default pattern sets.
 
+### Spec-First Artifact Governance (LE-8 / Task 140)
+
+`loop-engine/specs.py` (`SpecGateEngine`) enforces a **fail-fast spec-first state gate**:
+tasks whose content or approved plan introduces architectural changes, API contracts, or
+database schema mutations must have **verified spec artifacts** (ADR, PRD, Contract,
+Data Model) present in the workspace or the staged diff BEFORE code implementation begins.
+
+**Pipeline position:**
+
+1. `daemon._process_task` reads the task, plans via the router, and sends the plan to
+   `AWAITING_APPROVAL`.
+2. **Immediately after Plan Approval** and **before** `TaskState.IMPLEMENTING` (step 2.5),
+   the gate runs:
+   - `SpecGateEngine(config.spec_gate).evaluate_requirements(task_content, plan)` scans the
+     lowercased task+plan text for rule keywords → matched `SpecRequirementRule`s (empty for
+     routine tasks / bugfixes).
+   - For matched rules, `validate_artifacts(rules, REPO_ROOT, diff_text="")` scans the
+     workspace (`rglob` + `fnmatch` full-relative-path globs) and any staged diff paths
+     (`diff --git` b-side headers) for the rule's `target_directories` patterns.
+   - **Failure** → `TaskState.CRASHED` + `state.set_qa_feedback(report_md)` + early return:
+     no code is generated, no executor is launched.
+   - **Success** → `state.set_spec_artifacts(task_id, found_artifacts)` persists the verified
+     artifact paths as JSON in SQLite, and the pipeline proceeds to step 3.
+3. The gate is inert when `config.spec_gate.enabled` is `false` or no rules match.
+
+**Migration:** `StateMachine.__init__` adds `spec_artifacts TEXT DEFAULT NULL` to the
+`tasks` table via a safe `ALTER TABLE ... ADD COLUMN` (caught `sqlite3.OperationalError`
+when the column already exists) — existing databases upgrade non-destructively.
+`set_spec_artifacts`/`get_spec_artifacts` persist/retrieve the JSON array (`[]` on unset
+or corrupt JSON).
+
+**`spec_gate` configuration schema** (`LoopEngineConfig.spec_gate`):
+
+| Field | Type | Default | Description |
+|---|---|---|---|
+| `enabled` | `boolean` | `true` | Whether the spec-first gate is enforced |
+| `rules` | `SpecRequirementRule[]` | `[]` | Configured spec requirement rules (`_default_spec_rules()` provides the defaults below) |
+
+Each `SpecRequirementRule`:
+
+| Field | Type | Description |
+|---|---|---|
+| `name` | `string` | Rule name, e.g. `architecture-decision`, `api-contract` |
+| `keywords` | `string[]` | Substrings in task or plan that trigger this rule (lowercased) |
+| `required_artifacts` | `SpecArtifactType[]` | `adr` / `prd` / `contract` / `data_model` |
+| `target_directories` | `string[]` | Directory globs where artifacts are expected, e.g. `["docs/adr/**", "contracts/**"]` |
+
+**Default rules** (`models._default_spec_rules()` — wire them explicitly, since `rules`
+defaults to `[]`):
+
+| Rule | Trigger keywords | Required artifact | Target globs |
+|---|---|---|---|
+| `architecture-decision` | `architecture`, `architectural`, `redesign`, `adr` | `adr` | `docs/adr/**`, `docs/architecture.md` |
+| `api-contract` | `api contract`, `openapi`, `new endpoint`, `graphql schema`, `grpc proto` | `contract` | `contracts/**`, `openapi/**`, `proto/**` |
+| `database-schema` | `database schema`, `prisma migration`, `sql migration`, `new table`, `data model` | `data_model` | `docs/data_model.md`, `prisma/**`, `migrations/**` |
+
+**Example override** (`loop-engine/loop-engine.jsonc`):
+
+```jsonc
+"spec_gate": {
+  "enabled": true,
+  "rules": [
+    {
+      "name": "architecture-decision",
+      "keywords": ["architecture", "architectural", "redesign", "adr"],
+      "required_artifacts": ["adr"],
+      "target_directories": ["docs/adr/**", "docs/architecture.md"]
+    },
+    {
+      "name": "api-contract",
+      "keywords": ["api contract", "openapi", "new endpoint", "graphql schema", "grpc proto"],
+      "required_artifacts": ["contract"],
+      "target_directories": ["contracts/**", "openapi/**", "proto/**"]
+    },
+    {
+      "name": "database-schema",
+      "keywords": ["database schema", "prisma migration", "sql migration", "new table", "data model"],
+      "required_artifacts": ["data_model"],
+      "target_directories": ["docs/data_model.md", "prisma/**", "migrations/**"]
+    }
+  ]
+}
+```
+
+**Report shape:** `SpecValidationResult` carries `passed`, `required_artifacts`,
+`found_artifacts`, `errors`, and a structured `report_md` (`# Spec-First Gate Report` with
+`Verified Artifacts`, `Missing Spec Artifacts`, and `Resolution` sections). The daemon
+stores the report as `qa_feedback` on a crashed task so the failure is auditable.
+
+**Guardrails:** empty `rules` pass immediately; the engine is fully disabled if `specs.py`
+cannot be imported (`ImportError` fallback in `daemon.py`); routine tasks never trigger the
+gate; the gate runs **before** any executor/LLM call, so un-specified tasks never burn
+tokens.
+
 ## Environment Variables
 
 | Variable | Required | Description |
diff --git a/loop-engine/daemon.py b/loop-engine/daemon.py
index 210dcee..29308b4 100644
--- a/loop-engine/daemon.py
+++ b/loop-engine/daemon.py
@@ -41,6 +41,11 @@ try:
 except ImportError:
     ContractPropagationEngine = None  # type: ignore
 
+try:
+    from specs import SpecGateEngine
+except ImportError:
+    SpecGateEngine = None  # type: ignore
+
 # Repo root = parent of loop-engine/. All relative paths in the config
 # (state db, evidence dir, tasks/, system-prompt.md) are anchored here so the
 # daemon behaves identically no matter which directory it is launched from.
@@ -517,6 +522,32 @@ async def _process_task(task_id: int, task_file: str, config: LoopEngineConfig,
         print(f"[pipeline] Plan rejected for task #{task_id}. Back to backlog.")
         return
 
+    # 2.5 SPEC-FIRST GATE (LE-8) — after Plan Approval, before IMPLEMENTING.
+    # Architectural / contract / schema tasks must have verified spec artifacts
+    # (ADR, PRD, Contract, Data Model) in the workspace or staged diff, otherwise
+    # the task crashes BEFORE any code is generated.
+    if SpecGateEngine is not None and config.spec_gate.enabled:
+        spec_engine = SpecGateEngine(config.spec_gate)
+        rules = spec_engine.evaluate_requirements(task_content, plan)
+        if rules:
+            spec_res = spec_engine.validate_artifacts(rules, REPO_ROOT, diff_text="")
+            if not spec_res.passed:
+                state.update_state(task_id, TaskState.CRASHED)
+                try:
+                    state.set_qa_feedback(task_id, spec_res.report_md)
+                except Exception:
+                    pass
+                print(
+                    f"[pipeline] Spec Gate FAILED for task #{task_id}: "
+                    f"{'; '.join(spec_res.errors)} — crashing"
+                )
+                return
+            state.set_spec_artifacts(task_id, spec_res.found_artifacts)
+            print(
+                f"[pipeline] Spec Gate PASSED for task #{task_id}: verified "
+                f"{len(spec_res.found_artifacts)} artifact(s)"
+            )
+
     # 3. IMPLEMENTING — preflight (profile already detected at pipeline start)
     state.update_state(task_id, TaskState.IMPLEMENTING)
     print(f"[pipeline] Implementing task #{task_id}...")
diff --git a/loop-engine/models.py b/loop-engine/models.py
index 4a78e6b..384b40e 100644
--- a/loop-engine/models.py
+++ b/loop-engine/models.py
@@ -178,6 +178,63 @@ def _default_contract_rules() -> list["ContractRuleConfig"]:
     ]
 
 
+class SpecArtifactType(str, Enum):
+    """Spec artifact kinds governed by the Spec-First Gate (LE-8)."""
+    ADR = "adr"
+    PRD = "prd"
+    CONTRACT = "contract"
+    DATA_MODEL = "data_model"
+
+
+class SpecRequirementRule(BaseModel):
+    """Declarative spec requirement rule — maps triggering keywords to required artifacts.
+
+    A rule fires when any ``keywords`` substring appears in the (lowercased) task
+    content or approved plan. When fired, the Spec-First Gate (LE-8) requires at
+    least one matching artifact under ``target_directories`` to exist in the
+    workspace or staged diff before implementation may proceed.
+    """
+    name: str = Field(..., description="Rule name, e.g. 'architecture-decision', 'api-contract'")
+    keywords: list[str] = Field(default_factory=list, description="Keywords in task or plan triggering this spec requirement")
+    required_artifacts: list[SpecArtifactType] = Field(default_factory=list, description="Artifact types required by this rule")
+    target_directories: list[str] = Field(default_factory=list, description="Directory globs where artifacts are expected, e.g. ['docs/adr/**', 'contracts/**']")
+
+
+class SpecGateConfig(BaseModel):
+    """Spec-First Gate configuration (LE-8)."""
+    enabled: bool = Field(True, description="Whether the spec-first gate is enforced")
+    rules: list[SpecRequirementRule] = Field(default_factory=list, description="Configured spec requirement rules")
+
+
+def _default_spec_rules() -> list[SpecRequirementRule]:
+    """Sensible default spec requirement rules (LE-8).
+
+    Kept as a free function (mirroring ``_default_contract_rules``) so callers can
+    wire the defaults explicitly into ``SpecGateConfig.rules`` — the schema default
+    is an empty list so the gate is inert until configured.
+    """
+    return [
+        SpecRequirementRule(
+            name="architecture-decision",
+            keywords=["architecture", "architectural", "redesign", "adr"],
+            required_artifacts=[SpecArtifactType.ADR],
+            target_directories=["docs/adr/**", "docs/architecture.md"],
+        ),
+        SpecRequirementRule(
+            name="api-contract",
+            keywords=["api contract", "openapi", "new endpoint", "graphql schema", "grpc proto"],
+            required_artifacts=[SpecArtifactType.CONTRACT],
+            target_directories=["contracts/**", "openapi/**", "proto/**"],
+        ),
+        SpecRequirementRule(
+            name="database-schema",
+            keywords=["database schema", "prisma migration", "sql migration", "new table", "data model"],
+            required_artifacts=[SpecArtifactType.DATA_MODEL],
+            target_directories=["docs/data_model.md", "prisma/**", "migrations/**"],
+        ),
+    ]
+
+
 class LoopEngineConfig(BaseModel):
     """Root configuration — loop-engine.jsonc."""
     # Providers
@@ -244,3 +301,9 @@ class LoopEngineConfig(BaseModel):
         default_factory=_default_contract_rules,
         description="Declarative rules mapping contract file mutations to downstream task generators",
     )
+
+    # Spec-First Artifact Gate (LE-8)
+    spec_gate: SpecGateConfig = Field(
+        default_factory=SpecGateConfig,
+        description="Spec-first artifact governance: fail-fast gate requiring spec artifacts before implementation",
+    )
diff --git a/loop-engine/specs.py b/loop-engine/specs.py
new file mode 100644
index 0000000..9933e4e
--- /dev/null
+++ b/loop-engine/specs.py
@@ -0,0 +1,194 @@
+"""
+Spec-First Artifact Pipeline & State Gate (LE-8 / Task 140).
+
+Enforces that tasks introducing architectural changes, API contracts, or
+database schema mutations must have verified spec artifacts (ADR, PRD,
+Contract, Data Model) BEFORE code implementation begins.
+
+Pipeline:
+    task_content + plan_text -> evaluate_requirements() -> matched rules
+    -> validate_artifacts(workspace_root, diff_text) -> SpecValidationResult
+
+Design notes:
+- ``evaluate_requirements`` is a pure keyword scan (lowercased substring
+  match) and returns an empty list for routine tasks / bugfixes.
+- ``validate_artifacts`` scans the workspace with ``rglob`` + ``fnmatch``
+  (full-relative-path glob semantics, same as ``contracts.match_contract_rules``)
+  and also parses ``diff --git`` headers from the staged task diff so artifacts
+  staged in the active task satisfy the gate.
+- An empty rule set passes immediately (the gate is inert until configured).
+- The engine is deterministic and side-effect free; the daemon owns all state
+  transitions (CRASHED / spec_artifacts persistence).
+"""
+
+from __future__ import annotations
+
+import fnmatch
+import re
+from dataclasses import dataclass, field
+from pathlib import Path
+
+from models import SpecGateConfig, SpecRequirementRule
+
+# Matches `diff --git a/<old> b/<new>` header lines — the b-side path is the
+# post-change relative path that may stage spec artifacts (mirrors contracts.py).
+_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)\n", re.MULTILINE)
+
+
+@dataclass
+class SpecValidationResult:
+    """Outcome of a spec artifact validation run."""
+    passed: bool
+    required_artifacts: list[str] = field(default_factory=list)
+    found_artifacts: list[str] = field(default_factory=list)
+    errors: list[str] = field(default_factory=list)
+    report_md: str = ""
+
+
+class SpecGateEngine:
+    """Keyword-driven spec requirement evaluation + artifact validation."""
+
+    def __init__(self, config: SpecGateConfig | None = None):
+        self.config = config or SpecGateConfig()
+
+    # --- Requirement evaluation ---
+
+    def evaluate_requirements(self, task_content: str, plan_text: str = "") -> list[SpecRequirementRule]:
+        """Return the subset of configured rules triggered by task/plan keywords.
+
+        The task content and approved plan are combined and lowercased; a rule
+        fires when ANY of its ``keywords`` appears as a substring. Routine tasks
+        and bugfixes (no keyword hit) yield an empty list.
+        """
+        if not self.config.rules:
+            return []
+        haystack = f"{(task_content or '')}\n{(plan_text or '')}".lower()
+        matched: list[SpecRequirementRule] = []
+        for rule in self.config.rules:
+            if any(keyword.lower() in haystack for keyword in rule.keywords):
+                matched.append(rule)
+        return matched
+
+    # --- Artifact validation ---
+
+    def validate_artifacts(
+        self,
+        rules: list[SpecRequirementRule],
+        workspace_root: str | Path,
+        diff_text: str = "",
+    ) -> SpecValidationResult:
+        """Validate that required spec artifacts exist for each fired rule.
+
+        For every rule, each ``target_directories`` pattern is checked against
+        (1) files present under ``workspace_root`` (``rglob`` + ``fnmatch``) and
+        (2) paths staged in ``diff_text`` (parsed from ``diff --git`` headers).
+        A rule is satisfied when at least one of its patterns matches anywhere.
+        Missing rules produce diagnostic errors and a structured Markdown report.
+
+        An empty ``rules`` list passes immediately (``SpecValidationResult(passed=True)``).
+        """
+        if not rules:
+            return SpecValidationResult(passed=True)
+
+        root = Path(workspace_root)
+        diff_text = diff_text or ""
+        required: list[str] = []
+        found: list[str] = []
+        errors: list[str] = []
+
+        for rule in rules:
+            rule_required = [a.value for a in rule.required_artifacts]
+            rule_found: list[str] = []
+            for pattern in rule.target_directories or []:
+                if pattern not in required:
+                    required.append(pattern)
+                matches = _find_matching_files(root, pattern)
+                matches += _paths_in_diff_matching(diff_text, pattern)
+                for m in matches:
+                    if m not in rule_found:
+                        rule_found.append(m)
+                    if m not in found:
+                        found.append(m)
+            if not rule_found:
+                artifact_label = ", ".join(rule_required) if rule_required else "spec artifact"
+                errors.append(
+                    f"Rule '{rule.name}' requires {artifact_label} "
+                    f"but no matching file found under {', '.join(rule.target_directories or [])}"
+                )
+
+        report_md = _build_report(rules, required, found, errors)
+        return SpecValidationResult(
+            passed=len(errors) == 0,
+            required_artifacts=required,
+            found_artifacts=found,
+            errors=errors,
+            report_md=report_md,
+        )
+
+
+# --- Pure helpers (unit-testable, side-effect free) ---
+
+
+def _find_matching_files(root: Path, pattern: str) -> list[str]:
+    """Return relative paths of files under ``root`` matching a glob pattern.
+
+    Uses ``rglob`` + ``fnmatch`` over the full relative path so patterns like
+    ``docs/adr/**`` and ``docs/architecture.md`` behave consistently.
+    """
+    matches: list[str] = []
+    try:
+        for p in root.rglob("*"):
+            if p.is_file():
+                rel = p.relative_to(root).as_posix()
+                if fnmatch.fnmatch(rel, pattern):
+                    matches.append(rel)
+    except OSError:
+        return []
+    return sorted(matches)
+
+
+def _paths_in_diff(diff_text: str) -> list[str]:
+    """Return deduplicated relative paths of files touched by a git diff."""
+    paths: list[str] = []
+    seen: set[str] = set()
+    for match in _DIFF_HEADER_RE.finditer(diff_text):
+        path = match.group(2).strip()
+        if path and path not in seen:
+            seen.add(path)
+            paths.append(path)
+    return paths
+
+
+def _paths_in_diff_matching(diff_text: str, pattern: str) -> list[str]:
+    """Return staged diff paths (b-side) matching a glob pattern."""
+    return [p for p in _paths_in_diff(diff_text) if fnmatch.fnmatch(p, pattern)]
+
+
+def _build_report(
+    rules: list[SpecRequirementRule],
+    required: list[str],
+    found: list[str],
+    errors: list[str],
+) -> str:
+    """Build a structured Markdown report: verified vs missing spec artifacts."""
+    lines = ["# Spec-First Gate Report", ""]
+    lines.append(f"**Rules evaluated:** {len(rules)}")
+    lines.append(f"**Required artifact locations:** {len(required)}")
+    lines.append(f"**Verified artifacts:** {len(found)}")
+    lines.append(f"**Errors:** {len(errors)}")
+    lines.append("")
+    if found:
+        lines.append("## Verified Artifacts")
+        lines.extend(f"- {f}" for f in found)
+        lines.append("")
+    if errors:
+        lines.append("## Missing Spec Artifacts")
+        lines.extend(f"- {e}" for e in errors)
+        lines.append("")
+    lines.append("## Resolution")
+    lines.append(
+        "Add the required spec artifact (ADR / PRD / Contract / Data Model) under "
+        "the configured target directories, or include it in the task's staged diff "
+        "before implementation. See `docs/loop-engine/configuration.md` (LE-8)."
+    )
+    return "\n".join(lines)
\ No newline at end of file
diff --git a/loop-engine/state.py b/loop-engine/state.py
index 337265c..7dcca2e 100644
--- a/loop-engine/state.py
+++ b/loop-engine/state.py
@@ -29,6 +29,7 @@ CREATE TABLE IF NOT EXISTS tasks (
     qa_feedback TEXT DEFAULT NULL,
     qa_retry_count INTEGER DEFAULT 0,
     evidence_dir TEXT DEFAULT NULL,
+    spec_artifacts TEXT DEFAULT NULL,
     created_at REAL NOT NULL,
     updated_at REAL NOT NULL,
     closed_at REAL DEFAULT NULL
@@ -59,6 +60,15 @@ class StateMachine:
         self.conn.row_factory = sqlite3.Row
         self.conn.executescript(_SCHEMA)
         self.conn.commit()
+        # Safe column migration for databases created before the spec-first gate
+        # (LE-8): newer schemas already declare spec_artifacts, so the ALTER is a
+        # no-op that raises sqlite3.OperationalError("duplicate column name") and
+        # is deliberately swallowed. Additive + non-destructive.
+        try:
+            self.conn.execute("ALTER TABLE tasks ADD COLUMN spec_artifacts TEXT DEFAULT NULL")
+            self.conn.commit()
+        except sqlite3.OperationalError:
+            pass
 
     def close(self):
         self.conn.close()
@@ -124,6 +134,27 @@ class StateMachine:
                           (evidence_dir, time.time(), task_id))
         self.conn.commit()
 
+    # --- Spec-First Artifact Tracking (LE-8) ---
+
+    def set_spec_artifacts(self, task_id: int, artifacts: list[str]):
+        """Persist the verified spec artifact paths for a task as a JSON array."""
+        self.conn.execute(
+            "UPDATE tasks SET spec_artifacts = ?, updated_at = ? WHERE task_id = ?",
+            (json.dumps(artifacts), time.time(), task_id))
+        self.conn.commit()
+
+    def get_spec_artifacts(self, task_id: int) -> list[str]:
+        """Return the verified spec artifact paths for a task, or ``[]`` when unset/corrupt."""
+        row = self.conn.execute(
+            "SELECT spec_artifacts FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
+        if not row or not row[0]:
+            return []
+        try:
+            parsed = json.loads(str(row[0]))
+        except (ValueError, TypeError):
+            return []
+        return parsed if isinstance(parsed, list) else []
+
     def get_active_tasks(self) -> list[dict]:
         """Get all tasks not in terminal states."""
         rows = self.conn.execute(
diff --git a/loop-engine/test_specs.py b/loop-engine/test_specs.py
new file mode 100644
index 0000000..50794f6
--- /dev/null
+++ b/loop-engine/test_specs.py
@@ -0,0 +1,426 @@
+"""Tests for the Spec-First Artifact Pipeline & State Gate (LE-8 / Task 140).
+
+Covers:
+1. ``SpecGateEngine.evaluate_requirements`` — keyword matching for architectural
+   tasks vs routine/bugfix tasks (empty rules, no keyword hits).
+2. ``SpecGateEngine.validate_artifacts`` — workspace scan passes when an ADR /
+   contract exists; diff-text staging passes; failing with a diagnostic report
+   when a required artifact is absent; empty-rule immediate pass.
+3. State machine migration — ``spec_artifacts`` column on new and pre-migration
+   DBs, ``set_spec_artifacts``/``get_spec_artifacts`` round-trip, corrupt JSON
+   fallback.
+4. Daemon integration — spec gate crashes a task before ``IMPLEMENTING`` with
+   ``qa_feedback``; passing gate proceeds and persists verified artifacts.
+"""
+import asyncio
+import json
+import os
+import sqlite3
+import sys
+from pathlib import Path
+from unittest.mock import AsyncMock, MagicMock, patch
+
+sys.path.insert(0, os.path.dirname(__file__))
+
+from models import (
+    LoopEngineConfig,
+    SpecArtifactType,
+    SpecGateConfig,
+    SpecRequirementRule,
+    TaskState,
+)
+from state import StateMachine
+
+import daemon
+from specs import SpecGateEngine, SpecValidationResult, _paths_in_diff
+
+
+# ---------------------------------------------------------------------------
+# Fixtures / helpers
+# ---------------------------------------------------------------------------
+
+def _make_workspace(tmp_path):
+    """Build a minimal workspace with tasks/ + spec artifact directories."""
+    for sub in ("backlog", "in-progress", "qa", "completed", "archive"):
+        (tmp_path / "tasks" / sub).mkdir(parents=True, exist_ok=True)
+    (tmp_path / "docs" / "adr").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "contracts").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "migrations").mkdir(parents=True, exist_ok=True)
+    return tmp_path
+
+
+def _arch_rules():
+    """Default spec rules (architecture-decision, api-contract, database-schema)."""
+    from models import _default_spec_rules
+    return _default_spec_rules()
+
+
+def _engine(rules=None, enabled=True):
+    return SpecGateEngine(SpecGateConfig(enabled=enabled, rules=rules))
+
+
+_ARCH_TASK = (
+    "# Task 99: Redesign the payment architecture\n"
+    "## Goal\nRedesign the billing service architecture.\n"
+)
+
+_ROUTINE_TASK = (
+    "# Task 100: Fix typo\n"
+    "## Goal\nFix a typo in the README.\n"
+)
+
+_DIFF_WITH_ADR = """diff --git a/docs/adr/001-billing.md b/docs/adr/001-billing.md
+new file mode 100644
+index 0000000..e69de29
+--- /dev/null
++++ b/docs/adr/001-billing.md
+"""
+
+
+# ---------------------------------------------------------------------------
+# 1. evaluate_requirements
+# ---------------------------------------------------------------------------
+
+def test_evaluate_requirements_matches_architectural_keywords():
+    rules = _engine(_arch_rules())
+    matched = rules.evaluate_requirements(_ARCH_TASK)
+    assert len(matched) == 1
+    assert matched[0].name == "architecture-decision"
+
+
+def test_evaluate_requirements_no_match_for_routine_task():
+    rules = _engine(_arch_rules())
+    assert rules.evaluate_requirements(_ROUTINE_TASK) == []
+
+
+def test_evaluate_requirements_plan_text_also_triggered():
+    rules = _engine(_arch_rules())
+    # Keywords live in the approved plan, not the task content.
+    matched = rules.evaluate_requirements("simple task", "Introduce grpc proto contract")
+    assert len(matched) == 1
+    assert matched[0].name == "api-contract"
+
+
+def test_evaluate_requirements_empty_rules():
+    rules = _engine(rules=[])
+    assert rules.evaluate_requirements(_ARCH_TASK, "architecture") == []
+
+
+def test_evaluate_requirements_disabled_gate_still_evaluates():
+    # enabled=False only stops enforcement in the daemon; evaluation stays pure.
+    rules = _engine(_arch_rules(), enabled=False)
+    assert rules.evaluate_requirements(_ARCH_TASK) != []
+
+
+# ---------------------------------------------------------------------------
+# 2. validate_artifacts
+# ---------------------------------------------------------------------------
+
+def test_validate_artifacts_passes_when_adr_exists_in_workspace(tmp_path):
+    ws = _make_workspace(tmp_path)
+    (ws / "docs" / "adr" / "0001-billing.md").write_text("# ADR 1\n")
+    rules = _engine(_arch_rules())
+    res = rules.validate_artifacts(rules.evaluate_requirements(_ARCH_TASK), ws)
+    assert res.passed is True
+    assert res.errors == []
+    assert "docs/adr/0001-billing.md" in res.found_artifacts
+    assert "docs/adr/0001-billing.md" in res.report_md
+
+
+def test_validate_artifacts_passes_when_contract_in_workspace(tmp_path):
+    ws = _make_workspace(tmp_path)
+    (ws / "contracts" / "billing.yaml").write_text("openapi: 3.0.0\n")
+    rules = _engine(_arch_rules())
+    task = "# Task: Add new endpoint\n## Goal\nAdd openapi endpoint\n"
+    matched = rules.evaluate_requirements(task)
+    assert matched[0].name == "api-contract"
+    res = rules.validate_artifacts(matched, ws)
+    assert res.passed is True
+    assert "contracts/billing.yaml" in res.found_artifacts
+
+
+def test_validate_artifacts_passes_when_artifact_in_diff_text(tmp_path):
+    ws = _make_workspace(tmp_path)
+    rules = _engine(_arch_rules())
+    # No ADR on disk, but the staged diff adds one.
+    res = rules.validate_artifacts(rules.evaluate_requirements(_ARCH_TASK), ws, diff_text=_DIFF_WITH_ADR)
+    assert res.passed is True
+    assert "docs/adr/001-billing.md" in res.found_artifacts
+
+
+def test_validate_artifacts_fails_with_diagnostic_report_when_absent(tmp_path):
+    ws = _make_workspace(tmp_path)
+    rules = _engine(_arch_rules())
+    res = rules.validate_artifacts(rules.evaluate_requirements(_ARCH_TASK), ws)
+    assert res.passed is False
+    assert len(res.errors) == 1
+    assert "architecture-decision" in res.errors[0]
+    assert "docs/adr/**" in res.errors[0]
+    # Markdown report contains verified + missing sections
+    assert "# Spec-First Gate Report" in res.report_md
+    assert "Missing Spec Artifacts" in res.report_md
+    assert "architecture-decision" in res.report_md
+    assert "Verified Artifacts" not in res.report_md
+
+
+def test_validate_artifacts_empty_rules_passes_immediately(tmp_path):
+    ws = _make_workspace(tmp_path)
+    res = _engine(rules=[]).validate_artifacts([], ws)
+    assert res.passed is True
+    assert res.found_artifacts == []
+    assert res.errors == []
+
+
+def test_validate_artifacts_data_model_rule_matches_migration(tmp_path):
+    ws = _make_workspace(tmp_path)
+    (ws / "migrations" / "0001_users.sql").write_text("CREATE TABLE users;")
+    rules = _engine(_arch_rules())
+    task = "# Task: Add a new table\n## Goal\nCreate sql migration for users\n"
+    matched = rules.evaluate_requirements(task)
+    assert [r.name for r in matched] == ["database-schema"]
+    res = rules.validate_artifacts(matched, ws)
+    assert res.passed is True
+    assert "migrations/0001_users.sql" in res.found_artifacts
+
+
+# --- helper: _paths_in_diff ---
+
+def test_paths_in_diff_parses_headers():
+    assert _paths_in_diff(_DIFF_WITH_ADR) == ["docs/adr/001-billing.md"]
+    assert _paths_in_diff("") == []
+    assert _paths_in_diff("no headers") == []
+
+
+def test_paths_in_diff_deduplicates():
+    diff = _DIFF_WITH_ADR + _DIFF_WITH_ADR
+    assert _paths_in_diff(diff) == ["docs/adr/001-billing.md"]
+
+
+# ---------------------------------------------------------------------------
+# 3. State machine migration + accessors
+# ---------------------------------------------------------------------------
+
+def test_state_spec_artifacts_roundtrip(tmp_path):
+    sm = StateMachine(str(tmp_path / "loop.db"))
+    try:
+        tid = sm.register_task("tasks/backlog/140-spec.md")
+        sm.set_spec_artifacts(tid, ["docs/adr/001.md", "contracts/api.yaml"])
+        assert sm.get_task(tid)["spec_artifacts"] == json.dumps(
+            ["docs/adr/001.md", "contracts/api.yaml"]
+        )
+        assert sm.get_spec_artifacts(tid) == ["docs/adr/001.md", "contracts/api.yaml"]
+    finally:
+        sm.close()
+
+
+def test_state_spec_artifacts_empty_and_corrupt(tmp_path):
+    sm = StateMachine(str(tmp_path / "loop.db"))
+    try:
+        tid = sm.register_task("tasks/backlog/140b.md")
+        assert sm.get_spec_artifacts(tid) == []
+        sm.set_spec_artifacts(tid, [])
+        assert sm.get_spec_artifacts(tid) == []
+        # Corrupt persisted JSON -> [] fallback
+        sm.conn.execute("UPDATE tasks SET spec_artifacts = ? WHERE task_id = ?",
+                        ("{not-json", tid))
+        sm.conn.commit()
+        assert sm.get_spec_artifacts(tid) == []
+        # Non-list JSON -> [] fallback
+        sm.set_spec_artifacts(tid, ["a"])
+        sm.conn.execute("UPDATE tasks SET spec_artifacts = ? WHERE task_id = ?",
+                        ('"scalar"', tid))
+        sm.conn.commit()
+        assert sm.get_spec_artifacts(tid) == []
+    finally:
+        sm.close()
+
+
+def test_state_migration_adds_column_to_old_db(tmp_path):
+    """A DB created WITHOUT spec_artifacts gains the column via the safe ALTER."""
+    db_path = tmp_path / "legacy.db"
+    conn = sqlite3.connect(str(db_path))
+    conn.executescript(
+        """
+        CREATE TABLE tasks (
+            task_id INTEGER PRIMARY KEY,
+            task_file TEXT NOT NULL UNIQUE,
+            state TEXT NOT NULL DEFAULT 'backlog',
+            created_at REAL NOT NULL,
+            updated_at REAL NOT NULL
+        );
+        """
+    )
+    conn.execute(
+        "INSERT INTO tasks (task_file, created_at, updated_at) VALUES ('tasks/backlog/legacy.md', 1, 1)"
+    )
+    conn.commit()
+    conn.close()
+
+    sm = StateMachine(str(db_path))
+    try:
+        cols = [r[1] for r in sm.conn.execute("PRAGMA table_info(tasks)").fetchall()]
+        assert "spec_artifacts" in cols
+        row = sm.conn.execute(
+            "SELECT spec_artifacts FROM tasks WHERE task_file = 'tasks/backlog/legacy.md'"
+        ).fetchone()
+        assert row[0] is None
+    finally:
+        sm.close()
+
+
+def test_state_migration_idempotent_on_new_db(tmp_path):
+    """New DBs already declare the column; the ALTER no-ops without error."""
+    sm = StateMachine(str(tmp_path / "loop.db"))
+    try:
+        cols = [r[1] for r in sm.conn.execute("PRAGMA table_info(tasks)").fetchall()]
+        assert "spec_artifacts" in cols
+        tid = sm.register_task("tasks/backlog/140c.md")
+        assert sm.get_spec_artifacts(tid) == []
+    finally:
+        sm.close()
+
+
+# ---------------------------------------------------------------------------
+# 4. Daemon integration (real _process_task)
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
+def _write_task(ws, text):
+    task_file = ws / "tasks" / "in-progress" / "140-spec.md"
+    task_file.write_text(text)
+    return task_file
+
+
+def _run_pipeline(ws, task_file, config, executor_cls=None):
+    """Run the real _process_task with fake execute_and_qa that records the gate state."""
+    router, gateway, executor, qa, brainstorm = _make_daemon_stubs(config)
+    state = StateMachine(str(ws / "loop.db"))
+    tid = state.register_task(str(task_file), TaskState.AWAITING_APPROVAL)
+
+    captured = {}
+
+    async def _fake_execute_and_qa(*args, **kwargs):
+        captured["entered_executing"] = state.get_task(tid)["state"]
+        return {"result": "PASSED", "report": "ok"}
+
+    async def _run():
+        await daemon._process_task(
+            tid, str(task_file), config, state, router, gateway, executor, qa, brainstorm
+        )
+
+    with patch.object(daemon, "_execute_and_qa", new=_fake_execute_and_qa):
+        with patch.object(daemon, "REPO_ROOT", ws):
+            asyncio.run(_run())
+    return tid, state, captured
+
+
+def _spec_config(rules):
+    return LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto",
+                            spec_gate=SpecGateConfig(enabled=True, rules=rules))
+
+
+def test_daemon_spec_gate_passes_and_proceeds(tmp_path):
+    ws = _make_workspace(tmp_path)
+    (ws / "docs" / "adr" / "0001.md").write_text("# ADR 1\n")
+    task_file = _write_task(ws, _ARCH_TASK)
+    config = _spec_config(_arch_rules())
+
+    tid, state, captured = _run_pipeline(ws, task_file, config)
+    try:
+        # Gate passed -> execution entered, artifacts persisted
+        assert captured["entered_executing"] == "implementing"
+        assert state.get_spec_artifacts(tid) == ["docs/adr/0001.md"]
+    finally:
+        state.close()
+
+
+def test_daemon_spec_gate_failure_crashes_before_implementing(tmp_path):
+    ws = _make_workspace(tmp_path)  # no ADR anywhere
+    task_file = _write_task(ws, _ARCH_TASK)
+    config = _spec_config(_arch_rules())
+
+    tid, state, captured = _run_pipeline(ws, task_file, config)
+    try:
+        assert state.get_task(tid)["state"] == "crashed"
+        assert "entered_executing" not in captured  # never reached IMPLEMENTING
+        assert "architecture-decision" in (state.get_task(tid)["qa_feedback"] or "")
+        assert "# Spec-First Gate Report" in (state.get_task(tid)["qa_feedback"] or "")
+        assert state.get_spec_artifacts(tid) == []
+    finally:
+        state.close()
+
+
+def test_daemon_spec_gate_disabled_proceeds_without_gate(tmp_path):
+    ws = _make_workspace(tmp_path)  # no ADR
+    task_file = _write_task(ws, _ARCH_TASK)
+    config = LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto",
+                              spec_gate=SpecGateConfig(enabled=False, rules=_arch_rules()))
+
+    tid, state, captured = _run_pipeline(ws, task_file, config)
+    try:
+        assert captured["entered_executing"] == "implementing"
+        assert state.get_spec_artifacts(tid) == []
+    finally:
+        state.close()
+
+
+def test_daemon_spec_gate_routine_task_bypasses(tmp_path):
+    ws = _make_workspace(tmp_path)  # no artifacts
+    task_file = _write_task(ws, _ROUTINE_TASK)
+    config = _spec_config(_arch_rules())
+
+    tid, state, captured = _run_pipeline(ws, task_file, config)
+    try:
+        assert captured["entered_executing"] == "implementing"
+        assert state.get_spec_artifacts(tid) == []
+    finally:
+        state.close()
+
+
+def test_loop_engine_config_default_spec_gate():
+    cfg = LoopEngineConfig(approval={"chat_id": 0})
+    assert cfg.spec_gate.enabled is True
+    assert cfg.spec_gate.rules == []
+    assert isinstance(cfg.spec_gate, SpecGateConfig)
+
+
+def test_default_spec_rules_shapes():
+    rules = _arch_rules()
+    assert [r.name for r in rules] == [
+        "architecture-decision", "api-contract", "database-schema"
+    ]
+    arch, api, db = rules
+    assert arch.required_artifacts == [SpecArtifactType.ADR]
+    assert arch.target_directories == ["docs/adr/**", "docs/architecture.md"]
+    assert api.required_artifacts == [SpecArtifactType.CONTRACT]
+    assert api.target_directories == ["contracts/**", "openapi/**", "proto/**"]
+    assert db.required_artifacts == [SpecArtifactType.DATA_MODEL]
+    assert db.target_directories == ["docs/data_model.md", "prisma/**", "migrations/**"]
+
+
+if __name__ == "__main__":
+    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
+    passed = failed = 0
+    for t in tests:
+        try:
+            t(Path("/tmp/specs-test-ws")) if "tmp_path" in t.__code__.co_varnames else t()
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