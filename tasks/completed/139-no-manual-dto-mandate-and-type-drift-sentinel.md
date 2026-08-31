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
**Factual Git Diff:** Stored in Commit Hash: `b97b18dd93dee19968d7b0b33b0b96bd385c59c7`
<!-- END_GIT_DIFF -->