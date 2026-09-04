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
**Factual Git Diff:** Stored in Commit Hash: `c61280a420f60cc8558b6739de4bce96c34a445a`
<!-- END_GIT_DIFF -->