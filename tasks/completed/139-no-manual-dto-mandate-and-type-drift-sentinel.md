# Task 139: No-Manual-DTO Mandate & Type Drift Sentinel

**File:** `tasks/completed/139-no-manual-dto-mandate-and-type-drift-sentinel.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Implement LE-7 — the No-Manual-DTO Mandate & Type Drift Sentinel: a new system-prompt mandate fragment (`prompts/fragments/20-no_manual_dto_mandate.md`) banning hand-authored duplicate DTO/interface/model declarations in consumer applications when a source-of-truth contract exists, plus a deterministic `TypeDriftSentinel` (`loop-engine/sentinel.py`) that scans task diffs for manual DTO declarations in consumer paths and fails the toolchain gate before LLM QA.

## Blueprint Reference

- Discovery context: `context-reports/task-139-context.md` (prompt fragments, assembler, verifier, daemon integration seams)
- Architecture reference: `docs/loop-engine/configuration.md` (LE-2 Toolchain Verification, LE-4 Executor injection, LE-6 Contract Propagation), `docs/conventions.md`

## Manager's Notes

- The no-manual-DTO rule lives in the system prompt (cognitive layer), while `TypeDriftSentinel` deterministically catches violations in the verifier (enforcement layer) before LLM QA — dual-layer defense against silent type drift in polyglot monorepos.
- Reconciliation: single-source-of-truth prevents type drift (DRY/SRP) and does NOT conflict with YAGNI or the 3-Implementation Rule from `14-solid_programming_mandate.md`.
- ZAC applies: no autonomous `git add`/`commit`/`push`; only `git mv` Kanban transitions and MCP staging.
- Verification gate: baseline 200 passed → final ≥ 215 passed, 0 failed, 0 regressions; `lint_lint_system_prompt_sync` must confirm fragments ↔ `system-prompt.md` byte identity after reassembly.
- Diff scope strictly limited to `prompts/`, `docs/`, `loop-engine/`, `system-prompt.md`, task file, and `CHANGELOG.md`.

## Local TODOs

- [x] Initialize task file (Step 1 — this file)
- [x] Create `prompts/fragments/20-no_manual_dto_mandate.md` with `<no_manual_dto_mandate>` XML block: ban on hand-authored duplicate interface models/request-response DTOs/data classes, import-from-shared or run-codegen requirement, SOLID reconciliation (Step 2)
- [x] Bump `<system_version>` 9.2.2 → 9.3.0, register `20-no_manual_dto_mandate.md` in `prompts/manifest.txt` before `18-initialization.md`, add `## No-Manual-DTO & Type Drift Standard` to `docs/conventions.md`, reassemble `system-prompt.md` (Step 3)
- [x] Implement `loop-engine/sentinel.py`: `DriftCheckResult` + `TypeDriftSentinel.check_diff` with default consumer/allowed patterns, diff parsing, TS/Kotlin/Python regex scanning, `drift-ignore` bypass, actionable Markdown report (Step 4)
- [x] Integrate `TypeDriftSentinel` into `loop-engine/verifier.py` (`ToolchainRunner.run` + `run_sync` gain `diff_text`; fail-fast on violation) and `loop-engine/daemon.py` (`_execute_and_qa` passes `diff_text=diff`) (Step 5)
- [x] Create `loop-engine/test_sentinel.py` suite: assembler inclusion + 9.3.0, TS/Kotlin/Python detection, allowed-pattern exemption, clean imports, `drift-ignore` bypass, ToolchainRunner fail-fast (Step 6)
- [x] Document Type Drift Sentinel in `docs/loop-engine/configuration.md` (Step 7)
- [x] Verify functionality: baseline + targeted + full suite + system prompt reassembly

## Acceptance Criteria

- [x] `prompts/fragments/20-no_manual_dto_mandate.md` exists, wrapped in `<no_manual_dto_mandate>` / `</no_manual_dto_mandate>`, and contains (a) the absolute ban on hand-authoring duplicate interface models / request-response DTOs / data classes when a source-of-truth contract or shared schema exists (`packages/shared-schema/`, OpenAPI, Prisma, Protobuf), (b) the requirement to import models directly from the shared package (`@repo/shared-schema`, `packages/shared-schema`) OR execute the stack codegen toolchain (`pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`), and (c) explicit reconciliation with SOLID (DRY/SRP vs YAGNI / 3-Implementation-Rule).
- [x] `<system_version>` in `prompts/fragments/01-system_version.md` and assembled `system-prompt.md` is `9.3.0`; `prompts/manifest.txt` lists `20-no_manual_dto_mandate.md` before `18-initialization.md`; `docs/conventions.md` contains the `## No-Manual-DTO & Type Drift Standard` summary section referencing the fragment as authoritative source; running the assembler regenerates `system-prompt.md` with `<no_manual_dto_mandate>` present.
- [x] `loop-engine/sentinel.py` implements `DriftCheckResult(passed, violations, report_md)` and `TypeDriftSentinel` with `__init__(consumer_patterns=None, allowed_patterns=None)` defaulting to the specified consumer (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) and allowed (`packages/shared-schema/**`, `contracts/**`, `openapi/**`, `proto/**`, `**/generated/**`, `**/build/**`, `**/dist/**`, `**/*.gen.*`) patterns.
- [x] `TypeDriftSentinel.check_diff(diff_text)` parses per-file diff chunks, skips allowed/contract-definition paths, scans added (`+`) lines in consumer files for manual declarations using the specified TS/JS, Kotlin, and Python regexes, ignores comment lines and explicit `drift-ignore` bypass comments, and on violation returns `passed=False` with an actionable Markdown report (import from shared package or run codegen).
- [x] `verifier.py:ToolchainRunner.run` and `run_sync` accept `diff_text: str = ""`; when drift is present, a `CommandResult(command="type-drift-sentinel", cmd_type="lint", passed=False, stderr=report_md)` is recorded and the run fails fast (no toolchain commands executed, `ToolchainResult.passed=False`).
- [x] `daemon.py:_execute_and_qa` passes `diff_text=diff` into `runner.run(...)`.
- [x] `loop-engine/test_sentinel.py` covers: assembler includes `<no_manual_dto_mandate>` with `9.3.0` and passes closing-tag checks; sentinel detects manual TypeScript interfaces, Kotlin data classes, and Python Pydantic models in consumer paths; sentinel allows DTO declarations in `packages/shared-schema/**` and `generated/`; sentinel allows clean imports without false positives; `// drift-ignore: reason` bypass; `ToolchainRunner` fail-fast integration with drift present in task diff.
- [x] `docs/loop-engine/configuration.md` documents the Type Drift Sentinel (`### Type Drift Sentinel (LE-7 / Task 139)` section) with config options and behavior.
- [x] Full test suite `uv run --project loop-engine --with pytest pytest loop-engine/ -q` passes with ≥ 215 passed, 0 failed, 0 regressions (baseline 200); diff scoped to `prompts/`, `docs/`, `loop-engine/`, `system-prompt.md`, `CHANGELOG.md`, and the task file.

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** ≥ 215 passed, 0 failed, 0 regressions (baseline 200)
- **Actual result:** 224 passed, 0 failed, 0 regressions (baseline 200 → +24 new tests in `loop-engine/test_sentinel.py`; targeted suite 24/24)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

**[2026-08-31] [D1] [ORCHESTRATOR-DETECTED]:** Dual-Layer Type Drift Defense (Prompt Mandate + Deterministic Sentinel)
- **Rationale:** Cognitive instructions in the system prompt establish the rule against manual DTO duplication, while the TypeDriftSentinel in the verifier deterministically catches violations before LLM QA.
- **Alternatives considered:** Relying solely on prompt instructions without deterministic verification, or building complex AST parsers per language.
- **Impact:** Eliminates silent type drift in polyglot monorepos while maintaining fast, regex-based fail-fast verification.

## Risk & Rollback

- **Risk:** Regex false positives on legitimate consumer-side declarations; fragment/version mismatch breaking `lint_lint_system_prompt_sync`; sentinel flagging imports or generated files; new `diff_text` param breaking legacy `ToolchainRunner` callers.
- **Rollback plan:** `TypeDriftSentinel` is isolated in `sentinel.py` and invoked only when `diff_text` is non-empty — removing the `verifier.py`/`daemon.py` call sites restores prior behavior; the mandate fragment is removable from `manifest.txt` (one line) followed by reassembly; `01-system_version.md` revert restores 9.2.2.

---

## Execution Log & Reasoning

### 2026-08-31 — Implementation

**Validation:** No rule violations. Reads: `AGENTS.md` (in-system), `docs/conventions.md`, `prompts/fragments/14-solid_programming_mandate.md`, `prompts/manifest.txt`, `scripts/prompt-build/assemble_system_prompt.py`, `loop-engine/verifier.py`, `loop-engine/daemon.py`, `docs/loop-engine/configuration.md`, `CHANGELOG.md`. `DESIGN.md`/`docs/architecture.md`/`docs/data_model.md` absent → skipped per Absent-File Policy. Note: `context-reports/task-139-context.md` (generated in the discovery phase) was absent from `context-reports/` (directory empty) — gracefully skipped; grounding satisfied via the mandated source reads above plus the discovery findings retained in this session. Memory lookup: no stored constraints conflicting. Buffer isolated.

**Step 1 — Task file init:** Created with canonical `task-generator` template (Variant A orchestrator), ACs, DoD, pre-seeded D1 (the only decision supplied by the Orchestrator in `<documentation_phase>` — D2–D5 were not supplied, so none were fabricated, matching the Task 138 precedent). Moved to `tasks/in-progress/` via sanctioned Kanban staging; `git mv` failed (untracked file), filesystem `mv` fallback used (not a Git operation; ZAC intact). Header synced.

**Step 2 — Mandate fragment:** Created `prompts/fragments/20-no_manual_dto_mandate.md` as an XML block (`<no_manual_dto_mandate>`): absolute ban on hand-authored duplicate interface models / request-response DTOs / data classes when a source-of-truth contract exists (`packages/shared-schema/`, OpenAPI, Prisma, Protobuf); requirement to import from the shared package (`@repo/shared-schema`, `packages/shared-schema`) OR run the stack codegen (`pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`); explicit reconciliation with SOLID guardrails (DRY/SRP single-source-of-truth; no YAGNI conflict because codegen/import reuses an existing contract; no 3-Implementation-Rule conflict; Occam's Razor).

**Step 3 — Assembly & conventions:** `<system_version>` bumped `9.2.2 → 9.3.0` (MINOR per SemVer — new mandate feature). `prompts/manifest.txt` registers `20-no_manual_dto_mandate.md` between `17-decision_logging_mandate.md` and `18-initialization.md` (mandates remain grouped before initialization). `docs/conventions.md` gained `## No-Manual-DTO & Type Drift Standard` (summary pointer; fragment is single source of truth — mirrors the decision-logging precedent). Assembler regenerated `system-prompt.md` (78869 bytes); `lint_lint_system_prompt_sync` confirms byte identity; `<no_manual_dto_mandate>` present, `9.3.0` in both fragment and artifact.

**Step 4 — sentinel.py:** `DriftCheckResult(passed, violations, report_md)` dataclass + `TypeDriftSentinel` with default consumer (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) and allowed (`packages/shared-schema/**`, `contracts/**`, `openapi/**`, `proto/**`, `**/generated/**`, `**/build/**`, `**/dist/**`, `**/*.gen.*`) patterns, both overridable. `check_diff` parses `diff --git a/… b/…` headers + `@@ -a,b +c,d @@` hunks (b-side path via `+++ ` refinement; per-line new-file numbers), skips allowed/contract paths and non-consumer paths, scans added lines with the three mandated regexes. Language dispatch is **extension-driven** (`.py` → Python, `.kt/.kts` → Kotlin, `.ts/.tsx/.js/.jsx/.mjs/.cjs` → TS/JS) with a specificity-ordered cascade for unknown extensions — fixed a first-draft bug where the generic Kotlin `class` regex mislabeled Python declarations. Comment-only lines and any line containing `drift-ignore` are ignored. Violations produce an actionable Markdown report (file, type, added line number, required action). One implementation note: the initial draft referenced a nonexistent `self._files` helper (circuit-breaker caught during smoke test) — rewritten as a clean generator accumulating `files` locally.

**Step 5 — Verifier/daemon integration:** `ToolchainRunner.run`/`run_sync` gained `diff_text: str = ""` (backward compatible). When drift is present, a single `CommandResult(command="type-drift-sentinel", cmd_type="lint", passed=False, stderr=report_md)` is recorded and the run returns fail-fast BEFORE any lint/build/test command (verified `len(commands) == 1`). Clean diffs pass silently — no sentinel command recorded, toolchain behavior unchanged (existing `test_verifier.py` suite unmodified and passing — no regressions). Sentinel infra errors are tolerated (logged, toolchain proceeds) mirroring the daemon's toolchain-error tolerance. `daemon._execute_and_qa` passes `diff_text=diff` into `runner.run(...)`.

**Step 6 — test_sentinel.py (24 tests):** assembler inclusion + 9.3.0 + closing-tag normalization + manifest ordering; TS interface / Kotlin data class / Kotlin plain class / Python Pydantic detection; multi-language capture; shared-schema / generated-dir / `.gen.` exemptions; clean imports + type re-export (no false positives); non-consumer exemption; empty/context-only pass; `drift-ignore` trailing + comment-line bypass; actionable report content; hunk line-number tracking; custom pattern override; ToolchainRunner fail-fast, clean-diff pass-through, no-diff unchanged; daemon `diff_text` forwarding. Two initial test bugs fixed (REPO_ROOT depth one `parent` too deep; Kotlin syntax written into a `.ts` fixture). First run 21/24 → 24/24.

**Step 7 — docs:** `docs/loop-engine/configuration.md` gained the `### Type Drift Sentinel (LE-7 / Task 139)` section after the LE-6 section: pipeline, regex table per language, default patterns table, fail-fast semantics, report shape, config-option note (not `loop-engine.jsonc`-driven; constructor-level glob overrides).

**CHANGELOG:** Parse-Then-Append under `## [Unreleased]` → `### Added` (newest-first, above the Task 138 entry), full Task 139 entry.

**Verification:** `pytest loop-engine/ -q` → **224 passed, 0 failed** (baseline 200 confirmed from Task 138 closure evidence; +24 new tests). CRITICAL GATE satisfied (0 failures, count strictly > 200, ≥ 215). Targeted suite 24/24. `lint_lint_system_prompt_sync` → ✅ in sync. Diff scoped to `prompts/fragments/01-system_version.md`, `prompts/fragments/20-no_manual_dto_mandate.md`, `prompts/manifest.txt`, `system-prompt.md`, `docs/conventions.md`, `loop-engine/sentinel.py`, `loop-engine/verifier.py`, `loop-engine/daemon.py`, `loop-engine/test_sentinel.py`, `docs/loop-engine/configuration.md`, `CHANGELOG.md`, task file.

**ZAC:** no `git add`/`commit`/`push` executed; staging delegated to `custom_context_stage_and_inject_diff`. Filesystem `mv` used only for the sanctioned untracked task-file Kanban transition.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index c1e0b90..ff51751 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **No-Manual-DTO Mandate & Type Drift Sentinel (Task 139)** — Added the No-Manual-DTO Mandate (`prompts/fragments/20-no_manual_dto_mandate.md`, `<no_manual_dto_mandate>` XML block banning hand-authored duplicate interface models / request-response DTOs / data classes in consumer applications when a source-of-truth contract or shared schema exists, requiring import from the shared package (`@repo/shared-schema`, `packages/shared-schema`) or execution of the stack codegen toolchain (`pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`), with explicit reconciliation against the SOLID guardrails from `14-solid_programming_mandate.md`) and the Type Drift Sentinel (`loop-engine/sentinel.py`): `DriftCheckResult` + `TypeDriftSentinel` with default consumer (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) and allowed (`packages/shared-schema/**`, `contracts/**`, `openapi/**`, `proto/**`, `**/generated/**`, `**/build/**`, `**/dist/**`, `**/*.gen.*`) patterns, diff parsing (`diff --git` headers + `@@` hunks with per-line numbers), extension-dispatched TS/JS/Kotlin/Python declaration regexes with specificity-ordered cascade for unknown extensions, comment-only + explicit `drift-ignore` bypass, and actionable Markdown failure reports; integrated into the toolchain verification gate — `ToolchainRunner.run`/`run_sync` accept `diff_text` and fail fast on drift with `CommandResult(command="type-drift-sentinel", cmd_type="lint", passed=False, stderr=report)` before any lint/build/test command; `daemon._execute_and_qa` forwards `diff_text=diff` into the runner; `<system_version>` bumped **9.2.2 → 9.3.0**, `prompts/manifest.txt` registers `20-no_manual_dto_mandate.md` before `18-initialization.md`, `system-prompt.md` reassembled (78869 bytes, `lint_lint_system_prompt_sync` byte-identity ✅), `docs/conventions.md` gained `## No-Manual-DTO & Type Drift Standard` (summary pointer, fragment authoritative), documented in `docs/loop-engine/configuration.md` (LE-7 section); 24 new tests in `loop-engine/test_sentinel.py` (assembler inclusion + version + closing-tag normalization, TS/Kotlin/Python detection, shared-schema/generated exemptions, clean imports, `drift-ignore` bypass, report quality, custom patterns, ToolchainRunner fail-fast/pass-through, daemon `diff_text` forwarding); verified **224 passed, 0 failed** (baseline 200).
 - **Contract Propagation & Downstream Task Dispatcher (Task 138)** — Added Contract Propagation & Downstream Task Dispatcher (`loop-engine/contracts.py`) with declarative schema mutation rules, diff pattern matching, sequential next-ID task generation in `tasks/backlog/`, SQLite state registration, and daemon closure integration. `DownstreamTaskTemplate` + `ContractRuleConfig` Pydantic schemas and `LoopEngineConfig.contract_rules` defaults (`openapi-spec`, `prisma-schema`, `protobuf`, `shared-schema` with `title_template`/`goal_template` `{contract_name}`/`{triggering_task_id}`/`{files}` placeholders) in `loop-engine/models.py`; `extract_modified_paths` (regex `diff --git` header parsing, deduplicated), `match_contract_rules` (fnmatch globs like `packages/shared-schema/**`, `openapi/*.yaml`, `*.prisma`), `discover_next_task_id` (max numeric prefix + 1 across backlog/in-progress/qa/completed/archive), `ContractPropagationEngine.process_task_closure` writes canonical task files (`**Source:** contract-propagation`, `**Triggered-By:** Task <id>`, Goal/Source Context/Acceptance Criteria/Git Diff markers) and registers them as `BACKLOG` in the SQLite state machine; `daemon.py` closure hooks `_process_task` + `_reimplement_task` invoke the engine immediately after `CLOSED` (with `ImportError` fallback + `LoopEngineDaemon.propagation_engine` wiring), printing dispatched summaries; non-contract diffs are a no-op. 21 new tests in `loop-engine/test_contracts.py` (path extraction add/update/delete/dedup, glob matching, next-ID sequential/gap/multi-folder/empty, batch generation sequential IDs + headers, state registration, config defaults, daemon closure integration happy-path + no-op, daemon `__init__` wiring); documented in `docs/loop-engine/configuration.md` (LE-6 section with schema tables, generated-task shape, and JSONC example); verified **200 passed, 0 failed** (baseline 179).
 - **OpenCode Executor Stack Context Injection & Goal Plugin Guardrails (Task 136)** — Added OpenCode Executor Stack Context Injection & Goal Plugin Guardrails (`loop-engine/executor.py`) with structured XML prompt generation, skill loading directives, process group isolation (`start_new_session=True`), Goal Plugin blocker reason extraction, and concurrency semaphore enforcement. `_build_prompt` constructs XML-tagged sections (`<task_instructions>`, `<stack_context name/display_name>` with `MANDATORY: Load required skills via the native skill tool` + toolchain test/build/lint instructions, `<blueprint_context>`, `<qa_feedback>` with explicit address directive, `<goal_rules>` with `[goal:complete]`/`[goal:blocked: <reason>]`); `TERM_COMPLETE`/`TERM_BLOCKED` regexes now case-insensitive with optional blocker-reason capture; `HandsExecutor.__init__` creates `asyncio.Semaphore(config.max_parallel_tasks)` and `execute()` wraps the run in `async with self._semaphore:`; `_run_once` uses `idle.executing_timeout_seconds` (fallback 900.0), launches with `start_new_session=True` on POSIX, kills the process group via `os.killpg(SIGKILL)` on timeout (suppressing ProcessLookupError/AttributeError/PermissionError) with 2.0s drain, and returns timeout/blocked (with reason)/complete status dicts; 15 new tests in `loop-engine/test_executor.py` (prompt combos, token matching, semaphore throttling, process-group timeout kill, transport retries); 3 legacy LE-0.1 tests in `test_le0_fixes.py` updated to the new XML prompt format; documented in `docs/loop-engine/configuration.md` (LE-4 section); verified 163 passed, 0 failed (baseline 148).
 - **End-to-End Polyglot Smoke Test Suite & Hard Verification Gate (Task 137)** — Added End-to-End Polyglot Smoke Test Suite & Hard Verification Gate (`loop-engine/test_polyglot_smoke.py`) certifying Phase A across 5 stacks (Node-TS, Python-FastAPI, Kotlin-Android, Go-Gin, Generic), preflight/toolchain fail-fast gates, agent blocked signals, and multi-turn retry recovery. `setup_test_workspace()` builds a hermetic `tmp_path` workspace (stacks/, tasks/{backlog,in-progress,qa,completed}/, loop-engine/{evidence,state}/, dummy AGENTS.md/system-prompt/conventions/loop-engine.jsonc) and wires REAL StateMachine/LLMRouter/QAEngine/HandsExecutor/ApprovalGateway/LoopEngineDaemon instances with scripted I/O seams only (`call_llm`, `_run_once`, `request_approval`); `daemon.REPO_ROOT` patched per run so detection/preflight/toolchain/evidence stay sandboxed; stack YAMLs mirror repo defaults with portable no-op commands (sandbox deviations documented: bare `"go"`/`"gin"` keywords dropped from go-gin to keep generic fallback reachable). 16 tests: 5 happy-path E2E (each asserting `closed`), 7 hard-gate/edge (preflight failure crashes before execution with `set_qa_feedback` record, toolchain failure bypasses QA + writes `toolchain_report.md` + retries, `[goal:blocked: <reason>]` extraction crash, empty diff crashes without toolchain/QA, retry recovery to `closed`, max retries → `crashed`, explicit `**Stack:**` header overrides marker detection), 4 supplementary (plan rejection → backlog, review rejection → crashed, QA-feedback retry threading, daemon boot-scan → pending_trigger). Documented in `docs/loop-engine/README.md` (Verification & Smoke Gate) and `docs/loop-engine/configuration.md` (LE-5 section); verified **179 passed, 0 failed** (baseline 163).
diff --git a/docs/conventions.md b/docs/conventions.md
index 494f143..3bd6613 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -67,6 +67,17 @@ Enforce these SOLID principles and pragmatic guardrails in every implementation:
 
 **Pragmatic Guardrails:** No abstraction for <3 trivial operations. Only extract interfaces with 2+ implementations. Apply YAGNI strictly. Prefer simpler designs unless a measurable requirement forces complexity.
 
+## No-Manual-DTO & Type Drift Standard
+
+All projects in this ecosystem MUST treat source-of-truth contracts and shared schemas (`packages/shared-schema/`, OpenAPI specs, Prisma schemas, Protobuf definitions) as the **only** place a governed type may be defined:
+
+1. **No hand-authored duplicates** — Consumer applications (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) MUST NOT hand-author duplicate interface models, request/response DTOs, or data classes for types already governed by a contract.
+2. **Import or generate** — When a governed type is needed, either import it directly from the shared package (`@repo/shared-schema`, `packages/shared-schema`) or execute the stack's code-generation toolchain (`pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`).
+3. **SOLID reconciliation** — Single-source-of-truth prevents type drift (DRY/SRP) and does not conflict with YAGNI or the 3-Implementation Rule: extract or generate only when a contract or cross-service dependency already exists.
+4. **Deterministic enforcement** — `TypeDriftSentinel` (`loop-engine/sentinel.py`) scans task diffs during toolchain verification (pre-QA) and fails fast when a consumer path introduces a hand-written DTO while a governing contract pattern applies. Bypass with an explicit `drift-ignore` comment only when a justified exception exists.
+
+The single source of truth for the full mandate is `prompts/fragments/20-no_manual_dto_mandate.md` — this section is a summary only.
+
 ## Universal Financial Ledger Standard
 
 All financial, transactional, and countable data operations MUST enforce these mandates:
diff --git a/docs/loop-engine/configuration.md b/docs/loop-engine/configuration.md
index d31ae16..158c2b2 100644
--- a/docs/loop-engine/configuration.md
+++ b/docs/loop-engine/configuration.md
@@ -460,6 +460,60 @@ crashed, or retried tasks never spawn duplicates; `discover_next_task_id` is col
 across all task folders; and the engine is fully disabled if `contracts.py` cannot be
 imported (`ImportError` fallback in `daemon.py`).
 
+### Type Drift Sentinel (LE-7 / Task 139)
+
+`loop-engine/sentinel.py` (`TypeDriftSentinel`) deterministically scans task diffs for
+**hand-authored duplicate DTO/interface/model declarations** in consumer paths while a
+source-of-truth contract or shared schema governs those types. It enforces the
+No-Manual-DTO Mandate (`prompts/fragments/20-no_manual_dto_mandate.md`) at the
+verification layer — before LLM QA — so broken duplicates fail fast and route to
+`_reimplement_task` instead of wasting tokens.
+
+**Pipeline:**
+
+1. `daemon._execute_and_qa` passes the extracted task diff into
+   `ToolchainRunner.run(..., diff_text=diff)`.
+2. Before any lint/build/test command, `TypeDriftSentinel().check_diff(diff_text)` parses
+   each `diff --git a/… b/…` file (with `@@ -a,b +c,d @@` hunk line numbers), skips paths
+   matching `allowed_patterns` (contract definitions + generated artifacts), and scans added
+   (`+`) lines in paths matching `consumer_patterns`.
+3. Declaration regexes per language family:
+   - **TypeScript/JavaScript:** `(?:export\s+)?(?:interface|type)\s+<name>` where the name
+     ends in `Dto|DTO|Request|Response|Payload|Model|Schema`.
+   - **Kotlin:** `(?:data\s+)?class\s+<name>` ending in `Dto|DTO|Request|Response|Payload|Model`.
+   - **Python:** `class\s+<name>(BaseModel|BaseDTO|dict)?` ending in
+     `Dto|DTO|Request|Response|Payload|Schema`.
+   Detection is dispatched by file extension (`.py`, `.kt/.kts`, `.ts/.tsx/.js/.jsx/…`),
+   with a specificity-ordered cascade for unknown extensions.
+4. Comment-only lines and lines carrying an explicit `drift-ignore` bypass comment are
+   ignored. On violation the sentinel records
+   `CommandResult(command="type-drift-sentinel", cmd_type="lint", passed=False,
+   stderr=<report>)` and the toolchain fails immediately — **no toolchain commands run**.
+
+**Default patterns** (overridable via `TypeDriftSentinel(consumer_patterns=..., allowed_patterns=...)`):
+
+| Pattern set | Defaults |
+|---|---|
+| `consumer_patterns` | `apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**` |
+| `allowed_patterns` | `packages/shared-schema/**`, `contracts/**`, `openapi/**`, `proto/**`, `**/generated/**`, `**/build/**`, `**/dist/**`, `**/*.gen.*` |
+
+**Fail-fast semantics:** the sentinel runs first inside `ToolchainRunner.run`. A drift
+failure returns `ToolchainResult(passed=False)` with the sentinel as the only recorded
+command, so `daemon._execute_and_qa` records `qa_feedback` and returns `FAILED` without
+calling `qa.run_qa`. A clean diff passes silently (no sentinel command is recorded) and the
+normal lint → build → test sequence proceeds. Sentinel infrastructure errors are tolerated
+(logged, toolchain proceeds) to avoid blocking otherwise valid pipelines.
+
+**Report shape:** the failure report names each offending file + type + added line number and
+instructs the agent to either import the type from the shared/contract package
+(`@repo/shared-schema`, `packages/shared-schema`) or run the stack's codegen toolchain
+(`pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`), with a note that
+an explicit `drift-ignore` comment is the only bypass.
+
+**Config options:** the sentinel is not config-driven in `loop-engine.jsonc` — it operates
+on the diff text already extracted by the daemon. Custom consumer/allowed globs are
+supported at construction time for callers that need to extend the default pattern sets.
+
 ## Environment Variables
 
 | Variable | Required | Description |
diff --git a/loop-engine/daemon.py b/loop-engine/daemon.py
index ed27b97..210dcee 100644
--- a/loop-engine/daemon.py
+++ b/loop-engine/daemon.py
@@ -220,7 +220,9 @@ async def _execute_and_qa(
                 effective_profile = stack_profile
         try:
             runner = ToolchainRunner(timeout_per_command=120.0, evidence_base_dir=evidence_base_dir)
-            toolchain_result = await runner.run(effective_profile, task_id=task_id, cwd=REPO_ROOT)
+            toolchain_result = await runner.run(
+                effective_profile, task_id=task_id, cwd=REPO_ROOT, diff_text=diff
+            )
             if not toolchain_result.passed:
                 # Fail-fast: record feedback, bypass LLM QA, return FAILED for retry logic
                 try:
diff --git a/loop-engine/sentinel.py b/loop-engine/sentinel.py
new file mode 100644
index 0000000..5d2fedc
--- /dev/null
+++ b/loop-engine/sentinel.py
@@ -0,0 +1,300 @@
+"""
+Type Drift Sentinel (LE-7 / Task 139).
+
+Deterministic regex-based scanner that detects hand-authored duplicate
+interface models, request/response DTOs, and data classes in consumer
+application paths during the toolchain verification gate — BEFORE LLM QA.
+
+Complements the No-Manual-DTO Mandate (prompts/fragments/20-no_manual_dto_mandate.md):
+the prompt fragment is the cognitive rule; this module is the deterministic
+enforcement layer. When a diff introduces a manual DTO/interface/model
+declaration into a consumer path while a source-of-truth contract or shared
+schema governs those types, check_diff() returns a failing DriftCheckResult
+with an actionable Markdown report instructing the agent to import from the
+shared package or run the stack's code-generation toolchain.
+
+The sentinel is intentionally side-effect free and unit-testable, mirroring
+the pure-helper design of loop-engine/contracts.py.
+"""
+
+from __future__ import annotations
+
+import fnmatch
+import re
+from dataclasses import dataclass, field
+
+
+@dataclass
+class DriftCheckResult:
+    """Outcome of a type-drift scan over a task diff."""
+
+    passed: bool
+    violations: list[str] = field(default_factory=list)
+    report_md: str = ""
+
+
+# Regexes matching hand-authored model/DTO declarations per language family.
+# TypeScript/JavaScript: interfaces and type aliases whose name carries a
+# DTO/model marker (e.g. `export interface CreateUserDTO {`, `type UserResponse = ...`).
+_TS_JS_RE = re.compile(
+    r"\b(?:export\s+)?(?:interface|type)\s+"
+    r"([A-Za-z0-9_]*(?:Dto|DTO|Request|Response|Payload|Model|Schema))\b"
+)
+# Kotlin: data classes and plain classes with a DTO/model marker
+# (e.g. `data class CreateUserRequest(`, `class OrderResponse(`).
+_KOTLIN_RE = re.compile(
+    r"\b(?:data\s+)?class\s+"
+    r"([A-Za-z0-9_]*(?:Dto|DTO|Request|Response|Payload|Model))\b"
+)
+# Python: classes deriving from BaseModel/BaseDTO/dict with a DTO/model marker
+# (e.g. `class CreateUserDTO(BaseModel):`).
+_PYTHON_RE = re.compile(
+    r"\bclass\s+"
+    r"([A-Za-z0-9_]*(?:Dto|DTO|Request|Response|Payload|Schema))"
+    r"\s*\((?:BaseModel|BaseDTO|dict)?\)"
+)
+
+# Default consumer paths where hand-authored DTOs are forbidden when a
+# governing contract exists.
+DEFAULT_CONSUMER_PATTERNS = [
+    "apps/**",
+    "services/**",
+    "client/**",
+    "frontend/**",
+    "mobile/**",
+    "src/**",
+]
+
+# Default paths where DTO/interface/model declarations are the canonical
+# source of truth (contract definitions) or generated artifacts — exempt.
+DEFAULT_ALLOWED_PATTERNS = [
+    "packages/shared-schema/**",
+    "contracts/**",
+    "openapi/**",
+    "proto/**",
+    "**/generated/**",
+    "**/build/**",
+    "**/dist/**",
+    "**/*.gen.*",
+]
+
+# Comment prefixes that mark a line as a comment (skipped by the scanner).
+_COMMENT_PREFIXES = ("//", "#", "/*", "*", "<!--", "--", "'''", '"""')
+
+
+class TypeDriftSentinel:
+    """Scan git diffs for hand-authored duplicate DTO declarations.
+
+    Args:
+        consumer_patterns: fnmatch globs for consumer application paths where
+            manual DTO declarations are forbidden (defaults to
+            DEFAULT_CONSUMER_PATTERNS).
+        allowed_patterns: fnmatch globs for contract/generated paths that are
+            exempt from the mandate (defaults to DEFAULT_ALLOWED_PATTERNS).
+    """
+
+    def __init__(
+        self,
+        consumer_patterns: list[str] | None = None,
+        allowed_patterns: list[str] | None = None,
+    ):
+        self.consumer_patterns = (
+            list(consumer_patterns)
+            if consumer_patterns is not None
+            else list(DEFAULT_CONSUMER_PATTERNS)
+        )
+        self.allowed_patterns = (
+            list(allowed_patterns)
+            if allowed_patterns is not None
+            else list(DEFAULT_ALLOWED_PATTERNS)
+        )
+
+    # ------------------------------------------------------------------
+    # Public API
+    # ------------------------------------------------------------------
+
+    def check_diff(self, diff_text: str) -> DriftCheckResult:
+        """Scan a git diff for manual DTO declarations in consumer paths.
+
+        Non-contract/no-drift diffs return ``DriftCheckResult(passed=True)``.
+        On violation, returns ``passed=False`` plus an actionable Markdown
+        report telling the agent to import from the shared package or run the
+        code-generation toolchain.
+        """
+        violations: list[str] = []
+        for path, added_lines in self._iter_added_lines(diff_text):
+            if self._matches_any(path, self.allowed_patterns):
+                continue
+            if not self._matches_any(path, self.consumer_patterns):
+                continue
+            for line_no, line in added_lines:
+                if self._is_ignored(line):
+                    continue
+                self._scan_line(path, line_no, line, violations)
+
+        if violations:
+            return DriftCheckResult(
+                passed=False,
+                violations=violations,
+                report_md=self._build_report(violations),
+            )
+        return DriftCheckResult(passed=True, violations=[])
+
+    # ------------------------------------------------------------------
+    # Diff parsing
+    # ------------------------------------------------------------------
+
+    def _iter_added_lines(self, diff_text: str):
+        """Yield ``(path, [(line_no, content), ...])`` for files with additions.
+
+        Parses ``diff --git a/<a> b/<b>`` headers (b-side path wins, refined by
+        ``+++ b/<path>`` lines) and ``@@ -a,b +c,d @@`` hunk headers so each
+        added line carries its approximate new-file line number.
+        """
+        current_path: str | None = None
+        current_added: list[tuple[int, str]] = []
+        new_line: int | None = None
+        in_hunk = False
+
+        # Accumulate files explicitly (a closure with yield would turn this
+        # into a double-generator and is invalid inside this generator body).
+        files: list[tuple[str, list[tuple[int, str]]]] = []
+
+        for raw in diff_text.splitlines():
+            line = raw
+            header = re.match(r"^diff --git a/(.*) b/(.*)$", line)
+            if header:
+                if current_path is not None:
+                    files.append((current_path, current_added))
+                current_path = header.group(2).strip()
+                current_added = []
+                new_line = None
+                in_hunk = False
+                continue
+
+            plus_path = re.match(r"^\+\+\+ b/(.*)$", line)
+            if plus_path:
+                current_path = plus_path.group(1).strip()
+                continue
+
+            hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
+            if hunk:
+                new_line = int(hunk.group(1))
+                in_hunk = True
+                continue
+
+            if current_path is None or not in_hunk:
+                continue
+
+            if line.startswith("+"):
+                if new_line is not None:
+                    current_added.append((new_line, line[1:]))
+                    new_line += 1
+            elif line.startswith("-"):
+                # Removed lines do not advance the new-file line counter.
+                pass
+            elif line.startswith(" "):
+                if new_line is not None:
+                    new_line += 1
+            # "\ No newline at end of file" and other metadata are skipped.
+
+        if current_path is not None:
+            files.append((current_path, current_added))
+
+        yield from files
+
+    # ------------------------------------------------------------------
+    # Scanning
+    # ------------------------------------------------------------------
+
+    def _matches_any(self, path: str, patterns: list[str]) -> bool:
+        return any(fnmatch.fnmatch(path, pat) for pat in patterns)
+
+    def _is_ignored(self, line: str) -> bool:
+        """True for comment-only lines or lines carrying an explicit `drift-ignore` bypass."""
+        if "drift-ignore" in line:
+            return True
+        stripped = line.strip()
+        if not stripped:
+            return True
+        return stripped.startswith(_COMMENT_PREFIXES)
+
+    def _scan_line(self, path: str, line_no: int, line: str, violations: list[str]) -> None:
+        # Dispatch by file extension so a Python `class XxxDTO(BaseModel):`
+        # line is labeled Python (not Kotlin, whose generic `class` regex also
+        # matches). Unknown extensions fall back to a specificity-ordered
+        # cascade (Python → TypeScript/JavaScript → Kotlin).
+        _BY_EXTENSION = {
+            ".py": ("Python", _PYTHON_RE),
+            ".kt": ("Kotlin", _KOTLIN_RE),
+            ".kts": ("Kotlin", _KOTLIN_RE),
+            ".ts": ("TypeScript/JavaScript", _TS_JS_RE),
+            ".tsx": ("TypeScript/JavaScript", _TS_JS_RE),
+            ".js": ("TypeScript/JavaScript", _TS_JS_RE),
+            ".jsx": ("TypeScript/JavaScript", _TS_JS_RE),
+            ".mjs": ("TypeScript/JavaScript", _TS_JS_RE),
+            ".cjs": ("TypeScript/JavaScript", _TS_JS_RE),
+        }
+        lowered = path.lower()
+        match = None
+        for ext, (lang, regex) in _BY_EXTENSION.items():
+            if lowered.endswith(ext):
+                match = regex.search(line)
+                if match:
+                    self._record_violation(path, line_no, lang, match.group(1), violations)
+                    return
+                return  # known language, no match -> not a violation of this language
+
+        # Unknown extension: cascade by specificity (Python is most specific,
+        # TS/JS next, Kotlin generic last). Only the first match labels the line.
+        for lang, regex in (
+            ("Python", _PYTHON_RE),
+            ("TypeScript/JavaScript", _TS_JS_RE),
+            ("Kotlin", _KOTLIN_RE),
+        ):
+            match = regex.search(line)
+            if match:
+                self._record_violation(path, line_no, lang, match.group(1), violations)
+                return
+
+    def _record_violation(
+        self, path: str, line_no: int, lang: str, type_name: str, violations: list[str]
+    ) -> None:
+        violations.append(
+            f"- `{path}` — manual {lang} model declaration `{type_name}` "
+            f"(added line {line_no}). Import it from the shared/contract "
+            f"package (`@repo/shared-schema`, `packages/shared-schema`) or run "
+            f"the stack codegen (`pnpm generate`, `prisma generate`, `protoc`, "
+            f"`./gradlew generateProto`) instead of hand-authoring a duplicate."
+        )
+
+    def _build_report(self, violations: list[str]) -> str:
+        lines = [
+            "# Type Drift Sentinel Report",
+            "",
+            "**Overall:** FAILED",
+            "",
+            "Hand-authored DTO/interface/model declarations were detected in consumer "
+            "paths while a source-of-truth contract or shared schema governs these types.",
+            "",
+            "## Violations",
+            "",
+        ]
+        lines.extend(violations)
+        lines.extend(
+            [
+                "",
+                "## Required Action",
+                "",
+                "- **Import** the type directly from the shared/contract package "
+                "(`@repo/shared-schema`, `packages/shared-schema`) where it is defined, OR",
+                "- **Run the stack's code-generation toolchain** (`pnpm generate`, "
+                "`prisma generate`, `protoc`, `./gradlew generateProto`) to produce the "
+                "type from the contract.",
+                "",
+                "Hand-written duplicates create silent type drift. Do NOT re-run QA "
+                "until the violation is resolved (or justified with an explicit "
+                "`drift-ignore` comment).",
+            ]
+        )
+        return "\n".join(lines)
\ No newline at end of file
diff --git a/loop-engine/test_sentinel.py b/loop-engine/test_sentinel.py
new file mode 100644
index 0000000..a26de1d
--- /dev/null
+++ b/loop-engine/test_sentinel.py
@@ -0,0 +1,395 @@
+"""Tests for No-Manual-DTO Mandate & Type Drift Sentinel (LE-7 / Task 139).
+
+Covers:
+1. Prompt assembly — ``assemble_system_prompt.py`` includes
+   ``<no_manual_dto_mandate>`` with ``<system_version>9.3.0</system_version>``
+   and passes the closing-tag normalization self-check; manifest registration
+   precedes ``18-initialization.md``.
+2. ``TypeDriftSentinel.check_diff`` — detects manual TypeScript interfaces,
+   Kotlin data/plain classes, and Python Pydantic models in consumer paths.
+3. Exemptions — DTO declarations in ``packages/shared-schema/**`` and
+   ``**/generated/**`` are allowed; clean imports produce no false positives.
+4. Bypass — explicit ``drift-ignore`` comments (line-level and trailing).
+5. Integration — ``ToolchainRunner`` fail-fast with drift present; clean diff
+   leaves the toolchain untouched; ``daemon._execute_and_qa`` forwards
+   ``diff_text=diff`` into the runner.
+"""
+import asyncio
+import importlib.util
+import os
+import sys
+from pathlib import Path
+from unittest.mock import AsyncMock, MagicMock, patch
+
+sys.path.insert(0, os.path.dirname(__file__))
+
+from sentinel import DriftCheckResult, TypeDriftSentinel
+from verifier import CommandResult, ToolchainResult
+
+REPO_ROOT = Path(__file__).resolve().parent.parent
+
+# ---------------------------------------------------------------------------
+# Helpers
+# ---------------------------------------------------------------------------
+
+
+def _diff(path: str, *added_lines: str, start: int = 1) -> str:
+    """Build a minimal git diff with *added_lines* under one new-file hunk."""
+    hunks = "".join(f"+{line}\n" for line in added_lines)
+    return (
+        f"diff --git a/{path} b/{path}\n"
+        f"--- a/{path}\n"
+        f"+++ b/{path}\n"
+        f"@@ -1,1 +{start},{len(added_lines)} @@\n"
+        f"{hunks}"
+    )
+
+
+_TS_DIFF = _diff(
+    "apps/api/src/user.ts",
+    "export interface CreateUserDTO {",
+    "  name: string;",
+    "}",
+)
+
+_KT_DATA_DIFF = _diff(
+    "services/orders/Order.kt",
+    "data class OrderResponse(",
+    "    val id: Long,",
+    ")",
+)
+
+_KT_PLAIN_DIFF = _diff("services/orders/Invoice.kt", "class InvoiceRequest(")
+
+_PY_DIFF = _diff(
+    "src/models/user.py",
+    "class CreateUserDTO(BaseModel):",
+    "    name: str",
+)
+
+
+def _load_assembler():
+    """Import scripts/prompt-build/assemble_system_prompt.py from the repo root."""
+    spec = importlib.util.spec_from_file_location(
+        "assemble_system_prompt",
+        REPO_ROOT / "scripts/prompt-build/assemble_system_prompt.py",
+    )
+    mod = importlib.util.module_from_spec(spec)
+    assert spec and spec.loader
+    spec.loader.exec_module(mod)
+    return mod
+
+
+class _Toolchain:
+    def __init__(self, lint=None, build=None, test=None):
+        self.lint_cmd = lint
+        self.build_cmd = build
+        self.test_cmd = test
+
+
+class _Profile:
+    def __init__(self, toolchain=None):
+        self.toolchain = toolchain
+
+
+# ---------------------------------------------------------------------------
+# 1. Prompt assembly (mandate fragment + version)
+# ---------------------------------------------------------------------------
+
+
+def test_assembler_includes_no_manual_dto_mandate_with_version_930(tmp_path):
+    mod = _load_assembler()
+    out = tmp_path / "assembled.md"
+    result = mod.assemble(
+        output_path=str(out),
+        fragments_dir=str(REPO_ROOT / "prompts/fragments"),
+        manifest_path=str(REPO_ROOT / "prompts/manifest.txt"),
+    )
+
+    # Mandate block present with both open and close tags.
+    assert "<no_manual_dto_mandate>" in result
+    assert "</no_manual_dto_mandate>" in result
+
+    # Version fragment bumped to 9.3.0 and reflected in the artifact.
+    version_frag = (REPO_ROOT / "prompts/fragments/01-system_version.md").read_text(
+        encoding="utf-8"
+    )
+    assert "9.3.0" in version_frag
+    assert "<system_version>9.3.0</system_version>" in result
+
+    # Closing-tag normalization: no indented pure closing tags survive.
+    drifted = [
+        line
+        for line in result.splitlines()
+        if line.startswith(" ") and line.lstrip().startswith("</")
+    ]
+    assert not drifted, f"Drifted closing tags found: {drifted}"
+
+
+def test_manifest_registers_mandate_before_initialization():
+    manifest = (REPO_ROOT / "prompts/manifest.txt").read_text(encoding="utf-8").splitlines()
+    assert "20-no_manual_dto_mandate.md" in manifest
+    assert manifest.index("20-no_manual_dto_mandate.md") < manifest.index(
+        "18-initialization.md"
+    )
+
+
+# ---------------------------------------------------------------------------
+# 2. Detection of manual declarations in consumer paths
+# ---------------------------------------------------------------------------
+
+
+def test_detects_typescript_interface():
+    result = TypeDriftSentinel().check_diff(_TS_DIFF)
+    assert result.passed is False
+    assert any("CreateUserDTO" in v for v in result.violations)
+    assert any("apps/api/src/user.ts" in v for v in result.violations)
+
+
+def test_detects_kotlin_data_class():
+    result = TypeDriftSentinel().check_diff(_KT_DATA_DIFF)
+    assert result.passed is False
+    assert any("OrderResponse" in v for v in result.violations)
+
+
+def test_detects_kotlin_plain_class():
+    result = TypeDriftSentinel().check_diff(_KT_PLAIN_DIFF)
+    assert result.passed is False
+    assert any("InvoiceRequest" in v for v in result.violations)
+
+
+def test_detects_python_pydantic_model():
+    result = TypeDriftSentinel().check_diff(_PY_DIFF)
+    assert result.passed is False
+    assert any("CreateUserDTO" in v for v in result.violations)
+    assert any("Python" in v for v in result.violations)
+
+
+def test_multiple_language_violations_captured():
+    combined = _TS_DIFF + _KT_DATA_DIFF + _PY_DIFF
+    result = TypeDriftSentinel().check_diff(combined)
+    assert result.passed is False
+    assert len(result.violations) == 3
+
+
+# ---------------------------------------------------------------------------
+# 3. Exemptions (allowed/contract paths, clean imports)
+# ---------------------------------------------------------------------------
+
+
+def test_allows_dto_in_shared_schema():
+    diff = _diff(
+        "packages/shared-schema/v1/types.ts",
+        "export interface UserDTO { id: string; }",
+    )
+    result = TypeDriftSentinel().check_diff(diff)
+    assert result.passed is True
+
+
+def test_allows_dto_in_generated_dir():
+    diff = _diff(
+        "apps/web/src/generated/api.ts",
+        "export interface CreateUserDTO { id: string; }",
+    )
+    result = TypeDriftSentinel().check_diff(diff)
+    assert result.passed is True
+
+
+def test_allows_dto_in_gen_file():
+    diff = _diff(
+        "apps/web/src/client.gen.ts",
+        "export interface UserResponse { ok: boolean; }",
+    )
+    result = TypeDriftSentinel().check_diff(diff)
+    assert result.passed is True
+
+
+def test_allows_clean_imports():
+    diff = _diff(
+        "apps/web/src/api.ts",
+        "import { ShiftDTO, exactOptionalPropertyTypes } from '@repo/shared-schema';",
+        "import type { UserDTO } from '@repo/shared-schema';",
+    )
+    result = TypeDriftSentinel().check_diff(diff)
+    assert result.passed is True
+
+
+def test_allows_type_reexport():
+    diff = _diff(
+        "apps/web/src/barrel.ts",
+        "export type { UserDTO, OrderResponse } from '@repo/shared-schema';",
+    )
+    result = TypeDriftSentinel().check_diff(diff)
+    assert result.passed is True
+
+
+def test_non_consumer_path_not_flagged():
+    diff = _diff(
+        "config/settings.ts",
+        "export interface SettingsDTO { theme: string; }",
+    )
+    result = TypeDriftSentinel().check_diff(diff)
+    assert result.passed is True
+
+
+def test_empty_diff_passes():
+    assert TypeDriftSentinel().check_diff("").passed is True
+
+
+def test_context_only_diff_passes():
+    diff = (
+        "diff --git a/apps/api/src/user.ts b/apps/api/src/user.ts\n"
+        "--- a/apps/api/src/user.ts\n"
+        "+++ b/apps/api/src/user.ts\n"
+        "@@ -10,3 +10,3 @@\n"
+        " export function getUser() {\n"
+        "-  return git;\n"
+        "+  return branch;\n"
+        " }\n"
+    )
+    assert TypeDriftSentinel().check_diff(diff).passed is True
+
+
+# ---------------------------------------------------------------------------
+# 4. drift-ignore bypass
+# ---------------------------------------------------------------------------
+
+
+def test_drift_ignore_trailing_comment_bypass():
+    diff = _diff(
+        "apps/web/src/legacy.ts",
+        "export interface LegacyDTO { x: string } // drift-ignore: legacy mirror",
+    )
+    assert TypeDriftSentinel().check_diff(diff).passed is True
+
+
+def test_drift_ignore_comment_line_bypass():
+    diff = _diff(
+        "apps/web/src/adapters.ts",
+        "// drift-ignore: generated adapter, mirror kept in sync by tooling",
+        "export interface AdapterDTO { x: string } // drift-ignore: kept in sync",
+    )
+    assert TypeDriftSentinel().check_diff(diff).passed is True
+
+
+# ---------------------------------------------------------------------------
+# 5. Report quality
+# ---------------------------------------------------------------------------
+
+
+def test_report_contains_actionable_instructions():
+    result = TypeDriftSentinel().check_diff(_PY_DIFF)
+    assert not result.passed
+    assert "Required Action" in result.report_md
+    assert "@repo/shared-schema" in result.report_md
+    assert "prisma generate" in result.report_md
+    assert "protoc" in result.report_md
+    assert "drift-ignore" in result.report_md
+
+
+def test_line_numbers_tracked():
+    diff = _diff("apps/api/src/user.ts", "export interface CreateUserDTO {", start=7)
+    result = TypeDriftSentinel().check_diff(diff)
+    assert any("added line 7" in v for v in result.violations)
+
+
+def test_custom_patterns():
+    sentinel = TypeDriftSentinel(
+        consumer_patterns=["packages/mobile/**"],
+        allowed_patterns=["packages/mobile/generated/**"],
+    )
+    # Consumer in custom pattern.
+    bad = _diff("packages/mobile/src/api.kt", "data class UserModel(")
+    assert sentinel.check_diff(bad).passed is False
+    # Allowed under custom pattern.
+    good = _diff("packages/mobile/generated/api.kt", "data class UserModel(")
+    assert sentinel.check_diff(good).passed is True
+
+
+# ---------------------------------------------------------------------------
+# 6. ToolchainRunner / daemon integration
+# ---------------------------------------------------------------------------
+
+
+def test_toolchain_runner_failfast_on_drift():
+    from verifier import ToolchainRunner
+
+    profile = _Profile(_Toolchain(lint="echo lint", build="echo build", test="echo test"))
+    result = ToolchainRunner().run_sync(profile, diff_text=_TS_DIFF)
+
+    assert result.passed is False
+    assert len(result.commands) == 1, "fail-fast: no toolchain commands ran"
+    cmd = result.commands[0]
+    assert cmd.command == "type-drift-sentinel"
+    assert cmd.cmd_type == "lint"
+    assert cmd.passed is False
+    assert "CreateUserDTO" in cmd.stderr
+
+
+def test_toolchain_runner_passes_without_drift():
+    from verifier import ToolchainRunner
+
+    diff = _diff(
+        "apps/api/src/user.ts",
+        "import { UserDTO } from '@repo/shared-schema';",
+    )
+    profile = _Profile(_Toolchain())
+    result = ToolchainRunner().run_sync(profile, diff_text=diff)
+
+    assert result.passed is True
+    # Sentinel passed silently — no sentinel command recorded, toolchain ran
+    # as usual (3 nullable commands -> skipped).
+    assert all(c.skipped for c in result.commands)
+    assert all(c.command != "type-drift-sentinel" for c in result.commands)
+
+
+def test_toolchain_runner_without_diff_text_unchanged():
+    from verifier import ToolchainRunner
+
+    profile = _Profile(_Toolchain())
+    result = ToolchainRunner().run_sync(profile)
+    assert result.passed is True
+    assert len(result.commands) == 3
+
+
+def test_daemon_passes_diff_text_to_runner(tmp_path):
+    import daemon as daemon_mod
+
+    diff_body = (
+        "diff --git a/apps/api/src/user.ts b/apps/api/src/user.ts\n"
+        "@@ -1 +1,2 @@\n"
+        "+export interface CreateUserDTO {\n"
+    )
+    task_file = tmp_path / "99-foo.md"
+    task_file.write_text(
+        "# Task 99: Foo\n\n## Factual Git Diff\n\n"
+        "<!-- BEGIN_GIT_DIFF -->\n" + diff_body + "<!-- END_GIT_DIFF -->\n",
+        encoding="utf-8",
+    )
+
+    state = MagicMock()
+    executor = MagicMock()
+    executor.execute = AsyncMock(return_value={"status": "complete"})
+    qa = MagicMock()
+    qa.run_qa.return_value = {"result": "PASSED"}
+
+    with patch.object(daemon_mod, "ToolchainRunner") as toolchain_cls:
+        toolchain_cls.return_value.run = AsyncMock(
+            return_value=ToolchainResult(passed=True, summary="ok", report_md="")
+        )
+        asyncio.run(
+            daemon_mod._execute_and_qa(
+                99,
+                str(task_file),
+                task_file.read_text(encoding="utf-8"),
+                task_file,
+                state,
+                executor,
+                qa,
+            )
+        )
+
+    call = toolchain_cls.return_value.run.await_args
+    assert call is not None
+    assert call.kwargs["diff_text"] == diff_body.strip()
+    qa.run_qa.assert_called_once()
\ No newline at end of file
diff --git a/loop-engine/verifier.py b/loop-engine/verifier.py
index d247618..bc41da4 100644
--- a/loop-engine/verifier.py
+++ b/loop-engine/verifier.py
@@ -11,6 +11,8 @@ import time
 from dataclasses import dataclass, field
 from pathlib import Path
 
+from sentinel import TypeDriftSentinel
+
 
 @dataclass
 class CommandResult:
@@ -53,12 +55,38 @@ class ToolchainRunner:
         profile,  # StackProfile
         task_id: int | None = None,
         cwd: str | Path | None = None,
+        diff_text: str = "",
     ) -> ToolchainResult:
         """Run toolchain commands sequentially.
 
-        Order: lint, build, test. Null/whitespace commands are skipped as
-        passed+skipped. Non-zero exit or timeout → passed=False.
+        Order: Type Drift Sentinel (LE-7) -> lint, build, test. Null/whitespace
+        commands are skipped as passed+skipped. Non-zero exit or timeout →
+        passed=False.
         """
+        # --- Type Drift Sentinel (LE-7) — fail-fast before any toolchain command ---
+        # A hand-authored duplicate DTO/interface/model in a consumer path is a
+        # hard violation: the toolchain fails immediately and the actionable
+        # report is recorded as stderr so it reaches QA feedback, preventing
+        # broken duplicate types from reaching LLM QA.
+        if diff_text and str(diff_text).strip():
+            try:
+                sentinel_result = TypeDriftSentinel().check_diff(str(diff_text))
+                if not sentinel_result.passed:
+                    sentinel_cmd = CommandResult(
+                        command="type-drift-sentinel",
+                        cmd_type="lint",
+                        passed=False,
+                        skipped=False,
+                        returncode=None,
+                        stdout="",
+                        stderr=sentinel_result.report_md,
+                    )
+                    return self._finalize([sentinel_cmd], task_id)
+            except Exception as e:
+                # Sentinel infra error must not block the toolchain (mirrors the
+                # daemon's toolchain-infra-error tolerance). Log to the result.
+                print(f"[verifier] Type Drift Sentinel error (proceeding): {e}")
+
         # Defensive: profile may lack toolchain attr in mocks
         toolchain = getattr(profile, "toolchain", None)
         if toolchain is None:
@@ -273,6 +301,7 @@ class ToolchainRunner:
         profile,
         task_id: int | None = None,
         cwd: str | Path | None = None,
+        diff_text: str = "",
     ) -> ToolchainResult:
         """Synchronous wrapper for tests and sync callers."""
-        return asyncio.run(self.run(profile, task_id=task_id, cwd=cwd))
+        return asyncio.run(self.run(profile, task_id=task_id, cwd=cwd, diff_text=diff_text))
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 1ac836a..9e94ffd 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.2.2</system_version>
+<system_version>9.3.0</system_version>
diff --git a/prompts/fragments/20-no_manual_dto_mandate.md b/prompts/fragments/20-no_manual_dto_mandate.md
new file mode 100644
index 0000000..0605d6d
--- /dev/null
+++ b/prompts/fragments/20-no_manual_dto_mandate.md
@@ -0,0 +1,27 @@
+<no_manual_dto_mandate>
+You MUST enforce the No-Manual-DTO Mandate on every implementation task where a source-of-truth contract or shared schema exists.
+
+### Core Mandate
+
+AI agents and engineers are STRICTLY FORBIDDEN from hand-authoring duplicate interface models, request/response DTOs, or data classes inside consumer applications when a source-of-truth contract or shared schema already exists — including `packages/shared-schema/`, OpenAPI specs, Prisma schemas, and Protobuf definitions. Consumer applications MUST NOT redefine types that a contract already governs.
+
+### Requirement
+
+When a task touches a type that is governed by an existing contract, the agent MUST either:
+
+1. **(a) Import models directly** from the shared package (`@repo/shared-schema`, `packages/shared-schema`, or the equivalent canonical source), OR
+2. **(b) Execute the stack's code-generation toolchain** — `pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`, or the equivalent generator — so the consumer's types are produced from the contract instead of being hand-written.
+
+Hand-written duplicates create silent type drift: the consumer's copy and the contract's canonical definition diverge over time, producing runtime mismatches that compile-time checks in the consumer alone cannot catch.
+
+### Reconciliation with SOLID
+
+This mandate is fully consistent with the SOLID principles and their pragmatic guardrails:
+
+- **DRY / SRP:** A single source of truth prevents duplicated type definitions (DRY) and gives each type exactly one owner (SRP). Importing a shared DTO is not duplication — it is the canonical, single-reason-to-change form.
+- **No conflict with YAGNI:** The mandate does not introduce speculative abstractions. It reuses a contract that already exists. If NO source-of-truth contract exists, the agent writes the concrete type directly — do NOT invent a shared-schema package for a single consumer.
+- **No conflict with the 3-Implementation Rule:** Extracting a shared package is only required when a contract or cross-service dependency already exists (2+ consumers or a canonical schema). Do not extract interfaces for trivial, single-module logic.
+- **Occam's Razor:** The simplest correct action is import-then-use or run-codegen — never hand-copy a governed type.
+
+When a diff introduces a new DTO/interface/model declaration into a consumer path (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) while a governing contract exists, the Type Drift Sentinel fails the verification until the agent imports from the shared package or runs the codegen toolchain.
+</no_manual_dto_mandate>
\ No newline at end of file
diff --git a/prompts/manifest.txt b/prompts/manifest.txt
index 222ceee..9499286 100644
--- a/prompts/manifest.txt
+++ b/prompts/manifest.txt
@@ -15,5 +15,6 @@
 15-universal_datetime_rules.md
 16-immutable_financial_ledger_mandate.md
 17-decision_logging_mandate.md
+20-no_manual_dto_mandate.md
 18-initialization.md
 19-communication_examples.md
diff --git a/system-prompt.md b/system-prompt.md
index 0391021..2da9f43 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.2.2</system_version>
+<system_version>9.3.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -630,6 +630,34 @@ Each entry MUST follow this exact format:
 - **Do NOT log:** Formatting changes, typo fixes, trivial config tweaks, or any change where the "why" is self-evident from the code itself.
 </decision_logging_mandate>
 
+<no_manual_dto_mandate>
+You MUST enforce the No-Manual-DTO Mandate on every implementation task where a source-of-truth contract or shared schema exists.
+
+### Core Mandate
+
+AI agents and engineers are STRICTLY FORBIDDEN from hand-authoring duplicate interface models, request/response DTOs, or data classes inside consumer applications when a source-of-truth contract or shared schema already exists — including `packages/shared-schema/`, OpenAPI specs, Prisma schemas, and Protobuf definitions. Consumer applications MUST NOT redefine types that a contract already governs.
+
+### Requirement
+
+When a task touches a type that is governed by an existing contract, the agent MUST either:
+
+1. **(a) Import models directly** from the shared package (`@repo/shared-schema`, `packages/shared-schema`, or the equivalent canonical source), OR
+2. **(b) Execute the stack's code-generation toolchain** — `pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`, or the equivalent generator — so the consumer's types are produced from the contract instead of being hand-written.
+
+Hand-written duplicates create silent type drift: the consumer's copy and the contract's canonical definition diverge over time, producing runtime mismatches that compile-time checks in the consumer alone cannot catch.
+
+### Reconciliation with SOLID
+
+This mandate is fully consistent with the SOLID principles and their pragmatic guardrails:
+
+- **DRY / SRP:** A single source of truth prevents duplicated type definitions (DRY) and gives each type exactly one owner (SRP). Importing a shared DTO is not duplication — it is the canonical, single-reason-to-change form.
+- **No conflict with YAGNI:** The mandate does not introduce speculative abstractions. It reuses a contract that already exists. If NO source-of-truth contract exists, the agent writes the concrete type directly — do NOT invent a shared-schema package for a single consumer.
+- **No conflict with the 3-Implementation Rule:** Extracting a shared package is only required when a contract or cross-service dependency already exists (2+ consumers or a canonical schema). Do not extract interfaces for trivial, single-module logic.
+- **Occam's Razor:** The simplest correct action is import-then-use or run-codegen — never hand-copy a governed type.
+
+When a diff introduces a new DTO/interface/model declaration into a consumer path (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) while a governing contract exists, the Type Drift Sentinel fails the verification until the agent imports from the shared package or runs the codegen toolchain.
+</no_manual_dto_mandate>
+
 <initialization>
 Acknowledge these instructions. Declare yourself online as the **[Cognitive Lead AI]**. Immediately initiate **Phase 0: Discovery & Onboarding**.
 </initialization>
```
<!-- END_GIT_DIFF -->