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
**Factual Git Diff:** Stored in Commit Hash: `c49daf6431ff2056967fd0b4452ba32cba1d4dd8`
<!-- END_GIT_DIFF -->