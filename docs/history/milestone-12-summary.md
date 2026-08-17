# Milestone 12 Summary

**Date:** 2026-08-17
**Tasks Compacted:** 3

## Source Distribution

| Source       | Count |
| ------------ | ----- |
| orchestrator | 2     |
| telegram     | 0     |
| manager      | 1     |

## Architectural Changes

- **Runtime-agnostic system prompt + Freebuff full support (Task 98, v8.4.5):** the Orchestrator Brain (`system-prompt.md`) was made runtime-agnostic — the local execution agent is addressed as "the Hands" and all `<opencode_*_task>` block tags were renamed to `<hands_discovery_task>` / `<hands_implementation_task>` / `<hands_combined_task>`; the task-file section header was renamed `## OpenCode Execution Log & Reasoning` → `## Execution Log & Reasoning` end-to-end (system prompt, task-generator skill, lint server, tests); OpenCode-specific tool mentions generalized with Freebuff examples. Freebuff support completed: new in-repo artifacts `freebuff/agents/cognitive-executor.ts` + `freebuff/agents/cognitive-discovery.ts` (v1.2.0, `model` omitted for free-tier 403 fix) and `freebuff/AGENTS.global.md` (installed as `~/.AGENTS.md`); `docs/freebuff-support.md` rewritten to ✅ FULL (REPO-LEVEL); QA rounds 1-10 hardened non-breaking backward compatibility (both Execution Log headers accepted by lint), Kanban `tasks/qa/` transition rule, pre-diff-scoped heading checks, and ZAC/Kanban safeguard regression tests (31 tests total).
- **System prompt modularization (Task 99, v8.4.6):** `system-prompt.md` became a GENERATED build artifact. New `scripts/prompt-build/split_system_prompt.py` (disassembler — extracts the 20 top-level XML tags into `prompts/fragments/<seq>-<tag>.md`, extracts the 3 duplicated `<validation_phase>` blocks into `prompts/shared/validation-phase.md` with `{{NEXT_PHASE}}` placeholder + `<!--INCLUDE:...-->` markers, emits `prompts/manifest.txt`) and `scripts/prompt-build/assemble_system_prompt.py` (assembler — reads manifest, concatenates fragments, resolves include markers, writes `system-prompt.md`). New `lint_system_prompt_sync()` lint MCP tool verifies the generated file matches its source. QA fix rounds 1-4 hardened: existence guard, unresolved-placeholder ValueError, include-path traversal rejection (`_safe_include_path`), malformed include-marker rejection, manifest-path safety (`_safe_fragment_path`), assembler-load exception hardening, and broad diagnostic exception handling in the lint tool (45 tests total). Authoring moved to `prompts/` source tree (fragments + shared + manifest + README); version bumped 8.4.5 → 8.4.6 (byte-identical round-trip verified).
- **Release v8.4.6 preparation (Task 100):** consolidated the `[Unreleased]` docs hotfix into `[8.4.6]` `### Fixed` (Parse-Then-Append, no duplicates), left `[Unreleased]` header present but empty, added the release-preparation entry under `[8.4.6]` `### Changed`, and stored persistent release workflow memory at `release/release-workflow` (`.opencode/memory/release/release-workflow.md`) documenting SemVer rules, Keep a Changelog, prompt-source rules, verification gates, and ZAC-safe commit rules.

## Files Modified

| File         | Change      |
| ------------ | ----------- |
| system-prompt.md | v8.4.5 → v8.4.6; runtime-agnostic; generated artifact (Tasks 98-99) |
| AGENTS.md | Runtime-agnostic gatekeeper wording; Freebuff equivalents note; QA/closure Kanban rules (Task 98) |
| docs/freebuff-support.md | Rewritten to ✅ FULL (REPO-LEVEL) + free-tier limitation (Task 98) |
| docs/workflow-upgrade-v8.4.5.md | v8.4.5 migration guide (Task 98) |
| docs/system-prompt-modularization.md | Superseded status note pointing to Task 99 |
| prompts/fragments/*.md (20 files) | Per-tag fragment source of system-prompt.md (Task 99) |
| prompts/shared/validation-phase.md | Shared `<validation_phase>` partial with {{NEXT_PHASE}} (Task 99) |
| prompts/manifest.txt | Ordered fragment list (Task 99) |
| prompts/README.md | Authoring workflow + include/manifest safety notes (Tasks 99-100) |
| scripts/prompt-build/split_system_prompt.py | Disassembler (Task 99) |
| scripts/prompt-build/assemble_system_prompt.py | Assembler + safety guards (Tasks 99) |
| mcp-lint-server/server.py | lint_system_prompt_sync + exception hardening (Tasks 99) |
| tests/test_mcp_servers.py | 14 → 45 regression tests (Tasks 98-99) |
| freebuff/agents/*.ts (2 files) | Freebuff agent ports v1.2.0 (Task 98) |
| freebuff/AGENTS.global.md | Global rules source → ~/.AGENTS.md (Task 98) |
| CHANGELOG.md | v8.4.5 + v8.4.6 sections, QA fix rounds, release preparation (Tasks 98-100) |
| .opencode/memory/release/release-workflow.md | Persistent release workflow memory (Task 100) |
| .opencode/memory/project/system-prompt-build-process.md | Generated-artifact constraint (Task 99) |
| README.md | Repo structure tree + Freebuff matrix + prompt-build entries (Tasks 98-99) |

## Criteria Met

| Task | Acceptance Criteria | Status |
| ---- | ------------------- | ------ |
| 98   | Runtime-agnostic tags/headers; Freebuff ports schema-validated & model-free; legacy headers still lint; pytest 31/31 | ✅ Met |
| 99   | Assemble output byte-identical except version line; lint_system_prompt_sync clean + drift detection; full pytest 45/45; memory stored; docs updated | ✅ Met |
| 100  | Canonical task file; release memory stored & verified; Unreleased empty; release-prep entry added; gates verified (lint, sync, py_compile, pytest) | ✅ Met |

## Individual Task Summaries

### Task 98: System Prompt Runtime-Agnostic + Freebuff Full Support

- **Type:** improvement
- **Source:** manager
- **Reasoning:** renamed `<opencode_*_task>` → `<hands_*_task>` blocks and the task-file header to the runtime-agnostic `## Execution Log & Reasoning`; completed the Freebuff port (2 custom agent `.ts` files + global rules file) with the `model`-omission fix for the free-tier HTTP 403; documented the verified free-tier limitation (custom agents require paid tier); 10 QA rounds hardened backward compatibility, Kanban QA-transition, lint pre-diff heading scoping, and ZAC safeguards (14 → 31 tests).

### Task 99: Modularize System Prompt with Shared Validation Phase

- **Type:** refactor
- **Source:** orchestrator
- **Reasoning:** split the monolithic `system-prompt.md` into a generated build artifact: 20 per-tag fragments under `prompts/fragments/`, the 3 duplicated `<validation_phase>` blocks extracted to `prompts/shared/validation-phase.md` (byte-identical include resolution), plus split/assemble scripts and `lint_system_prompt_sync()`. Byte-identity verified by round-trip diff (zero differences pre-bump; only the version line after 8.4.5 → 8.4.6). Four QA fix rounds added include-path/manifest-path traversal rejection, malformed-marker and unresolved-placeholder guards, and broad diagnostic exception handling (31 → 45 tests).

### Task 100: Release v8.4.6 — Consolidate CHANGELOG and Store Release Workflow Memory

- **Type:** chore
- **Source:** orchestrator
- **Reasoning:** release preparation only — consolidated the `[Unreleased]` docs hotfix into `[8.4.6]` `### Fixed` (no duplication, `[Unreleased]` left empty per Keep a Changelog), added the release-preparation entry under `[8.4.6]` `### Changed`, stored the future release workflow as persistent memory (`release/release-workflow`, verified via `read_memory`), and verified all release gates (lint_markdown, lint_system_prompt_sync, py_compile, pytest 45/45). No tag/push performed by the Hands (ZAC) — publication is a separate manual Manager step.
