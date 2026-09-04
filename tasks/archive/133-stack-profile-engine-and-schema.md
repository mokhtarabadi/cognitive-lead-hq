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
**Factual Git Diff:** Stored in Commit Hash: `8371cf5ba0131c7db94a0e1fca6c38613cd32a4d`
<!-- END_GIT_DIFF -->
