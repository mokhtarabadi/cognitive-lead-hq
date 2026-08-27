# Task 119: System Prompt Hardening RFC Implementation

**File:** `tasks/completed/119-system-prompt-hardening-rfc-implementation.md`
**Source:** telegram
**Type:** improvement
**Status:** closed
**Created:** 2026-08-26

---

## Goal

Implement the 4 enhancements from RFC-001 (System Prompt Hardening, v8.7.0 → v8.8.0). The RFC addresses structural vulnerabilities exposed during the 4-task backend sprint (Tasks 734, 731, 729, 732).

### RFC Enhancements

1. **Enhancement A — Native 9-Step SOP:** Replace `<execution_workflow>` with a strict 9-step production line (Context Discovery → Brainstorming → Blueprint → Approval → TDD Implementation → QA Audit → Code Review → PO Acceptance → Next Task Transition).

2. **Enhancement B — Immutable Financial Ledger Mandate:** New `<immutable_financial_ledger_mandate>` block enforcing snapshot-on-write, `$ifNull` precedence, observability alerting, and deep config merging.

3. **Enhancement C — Output Isolation & Buffer Flush:** Add buffer isolation directives to `<hands_discovery_task_template>` and `<hands_implementation_task_template>` to prevent cross-task context leakage.

4. **Enhancement D — Defensive Shell Protocol (DSP):** New `<defensive_shell_protocol>` in `<constraints>` enforcing `set -euo pipefail`, banning `2>/dev/null` on data commands, and sidecar isolation for backups.

## Acceptance Criteria

- [x] Merge codified 9-Step SOP into `<execution_workflow>` in `prompts/fragments/`

- [x] Insert `<immutable_financial_ledger_mandate>` below `<universal_datetime_rules>`

- [x] Insert `<defensive_shell_protocol>` into `<constraints>`

- [x] Update task templates with Buffer Isolation directive

- [x] Reassemble `system-prompt.md` and verify byte-identical round-trip

- [x] Increment system version to 8.8.0

- [x] All existing tests pass (pytest — 49 passed, 1 pre-existing failure unrelated to Task 119)

- [x] CHANGELOG updated with all 4 enhancements

## Local TODOs

- [x] Bump version to 8.8.0 in `prompts/fragments/01-system_version.md`

- [x] Update `prompts/fragments/15-execution_workflow.md` with 9-Step SOP

- [x] Add Defensive Shell Protocol to `prompts/fragments/17-constraints.md`

- [x] Add Buffer Isolation to `prompts/shared/validation-phase.md`

- [x] Create `prompts/fragments/20-immutable_financial_ledger_mandate.md`

- [x] Renumber fragments 20→21/21→22 + update manifest + split script

- [x] Reassemble `system-prompt.md` (assembler round-trip identical)

- [x] Sync `docs/conventions.md`, `AGENTS.md`, `README.md`

- [x] Update `CHANGELOG.md`

## Risk & Rollback

- Modifying system prompt fragments affects all downstream agent behavior — changes must be backward-compatible with existing task workflows. The 9-Step SOP formalization may conflict with current ad-hoc sprint patterns.

- **Rollback:** Revert all fragment changes and reassemble. The old system-prompt.md is preserved in git history.

## Verification Evidence

- **Assembler round-trip:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/verify-prompt.md && diff /tmp/verify-prompt.md system-prompt.md` → IDENTICAL (77922 chars)
- **Round-trip test:** `pytest tests/test_mcp_servers.py::test_system_prompt_split_assemble_round_trip` → PASSED (split+reassemble produces byte-identical output)
- **Lint sync:** `pytest tests/test_mcp_servers.py::test_lint_system_prompt_sync_clean` → PASSED
- **Full test suite:** `pytest tests/ -q` → **49 passed**, 1 failed (`test_workflow_upgrade_guide_exists` — pre-existing, file removed in Task 117)
- **Version check:** `head -1 system-prompt.md` → `<system_version>8.8.0</system_version>`
- **Enhancement A (9-Step SOP):** `grep -c "Step 1:" system-prompt.md` → 1 (9 steps confirmed via regex: Step 1–9 present)
- **Enhancement B (Financial Ledger):** `grep -c "immutable_financial_ledger_mandate" system-prompt.md` → 2
- **Enhancement C (Buffer Isolation):** `grep -c "BUFFER ISOLATION" system-prompt.md` → 3
- **Enhancement D (DSP):** `grep -c "defensive_shell_protocol" system-prompt.md` → 2
- **Fragment count:** `ls prompts/fragments/*.md | wc -l` → 22
- **Manifest:** `wc -l prompts/manifest.txt` → 22 lines
- **Split script:** `TOP_LEVEL_TAGS` list contains 22 entries including `immutable_financial_ledger_mandate`
- **audit-agents sync:** `skill-templates/audit-agents/SKILL.md` updated with RFC-001 governance criteria (Financial Ledger, DSP, Buffer Isolation audit checks in both summary and Mode 2)

## Execution Log & Reasoning

### Step 1: Version Bump

Bumped `01-system_version.md` from 8.7.0 → 8.8.0. Single-line edit, no trailing newline.

### Step 2: 9-Step SOP Formalization

Replaced entire `<execution_workflow>` content with the 9-step production line from RFC-001. Preserved sub-rules (1.5 Task Number Validation, 2.5 Deep Research Loop, 2.7 Combined Discovery+Plan, 10 Distribution/Growth Signal). The old step names were ad-hoc; the new naming follows the persona-to-step mapping (Hands, Orchestrator, Manager, QA Engineer, Code Reviewer, Sprint Strategist).

### Step 3: Defensive Shell Protocol

Appended `<defensive_shell_protocol>` block inside `<constraints>`, before the closing `</constraints>` tag. Four rules: mandatory strict mode, banned error masking, no post-redirect status checks, sidecar isolation.

### Step 4: Buffer Isolation

Added a new directive to `prompts/shared/validation-phase.md` after step 5. The directive instructs Hands to flush prior context and treat every task as contextually independent. This is shared across all 3 task templates (discovery, combined, implementation) via include markers.

### Step 5: Immutable Financial Ledger Mandate

Created `prompts/fragments/20-immutable_financial_ledger_mandate.md` with 4 core mandates: snapshot-on-write, `$ifNull` precedence, observability alerting, deep config merging. Placed after `19-universal_datetime_rules.md`.

### Step 6: Fragment Renumbering + Build Scripts

Renamed `20-initialization.md` → `21-initialization.md`, `21-communication_examples.md` → `22-communication_examples.md`. Updated `prompts/manifest.txt` (22 entries). Updated `scripts/prompt-build/split_system_prompt.py` `TOP_LEVEL_TAGS` list (21→22 entries, added `immutable_financial_ledger_mandate`). Updated docstring counts.

### Step 7: Reassemble

Ran assembler → 77924 bytes. Diffed against old system-prompt.md → diffs are exactly the 4 intended enhancements (version bump, buffer isolation ×3, 9-step SOP, defensive shell protocol, immutable financial ledger mandate). Copied assembled file to `system-prompt.md`.

### Step 8: Doc Sync

- `docs/conventions.md`: Added "Universal Financial Ledger Standard" and "Defensive Shell Protocol (DSP)" sections.

- `AGENTS.md`: Added 3 new guardrails (DSP, Financial Ledger, Buffer Isolation) under Actionable Guardrails.

- `README.md`: Updated fragment count (01-20 → 01-22), added "Key V8 Changes" section documenting all 4 enhancements.

### Step 9: CHANGELOG

Added detailed entry under `## [Unreleased]` → `### Changed` documenting all file changes and verification evidence.

### Step 10: Verification

Pytest available via uv. Full test suite: 49 passed, 1 failed (`test_workflow_upgrade_guide_exists` — pre-existing, file removed in Task 117 Freebuff cleanup, unrelated to Task 119). Round-trip test passes. Lint sync test passes.

### Step 11: Assembler Round-Trip Fix (QA Iteration)

Fragment files written by the Write tool have trailing `\n` after closing tags, but the splitter extracts blocks WITHOUT trailing newlines. This caused the assembler's `\n\n` join to produce `\n\n\n` between fragments, breaking the round-trip test. Fixed by adding `.rstrip("\n")` to fragment reads in `assemble_system_prompt.py` before joining. Also removed the stale trailing blank line from `20-immutable_financial_ledger_mandate.md`. Verified: round-trip test now passes.

### Step 12: audit-agents Skill Update (QA Iteration)

Updated `skill-templates/audit-agents/SKILL.md` with RFC-001 governance criteria:
- conventions.md compliance: expanded with Financial Ledger Standard + Defensive Shell Protocol requirements
- Mode 2 (Conventions): added Buffer Isolation, DSP, and Financial Ledger audit criteria
- AGENTS.md template guardrails: added 3 new Don't/Do pairs (DSP, Financial Ledger, Buffer Isolation)
- conventions.md template: added Universal Financial Ledger Standard and Defensive Shell Protocol sections

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `611cdceabe10c4ceb758e9929f0cd542cfef6f1e`
<!-- END_GIT_DIFF -->
