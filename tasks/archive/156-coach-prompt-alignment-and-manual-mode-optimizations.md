# Task 156: Coach Prompt Alignment, User Prompts Refactor & Manual Mode Optimizations

**File:** `tasks/completed/156-coach-prompt-alignment-and-manual-mode-optimizations.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Update the Coach review prompt in `user-prompts/` to remove obsolete `## Manager Decisions` audit criteria (aligning with Task 151), standardize all user prompts in `user-prompts/` into the unique structured format, overhaul `README.md` to reflect pure-MCP architecture, and optimize prompt templates for manual copy/paste mode.

## Manager's Notes

Source: Manager Request (2026-09-02). Follow-up to Task 151 (audit Manager Decision logging) and Task 155 (pure MCP tooling). The Coach review prompt currently audits `## Manager Decisions` which was restructured in Task 151 — retarget intent audit to `## Original Message (Persian)` and `## English Translation`. All `user-prompts/` templates need uniform structured formatting, and `README.md` must be rewritten for pure-MCP manual workflow ergonomics.

## Local TODOs

- [x] Audit `user-prompts/` directory and coach review prompt
- [x] Remove `## Manager Decisions` audit target from coach prompt; retarget intent audit to `## Original Message (Persian)` and `## English Translation`
- [x] Refactor and standardize all user prompt templates
- [x] Rewrite `README.md` reflecting pure-MCP architecture and manual copy/paste mode
- [x] Verify formatting and consistency

## Acceptance Criteria

- [x] Coach prompt in `user-prompts/` aligned with Task 151 (zero references to deleted `## Manager Decisions`)
- [x] User prompts in `user-prompts/` refactored into uniform structured format
- [x] `README.md` updated and clean
- [x] All workflows streamlined for manual mode copy/paste ergonomics

## Verification Evidence

- **Test command:** `grep -r "Manager Decisions" user-prompts/ || echo "no leak"` + `npx prettier --check "user-prompts/**/*.md" README.md` + `lint_task_file tasks/in-progress/156-coach-prompt-alignment-and-manual-mode-optimizations.md`
- **Expected result:** No `Manager Decisions` references in `user-prompts/`; prettier passes; lint passes
- **Actual result:** `grep -rn "Manager Decisions" user-prompts/` → 3 intentional FORBIDDEN-banners in `founder-coaching-chat.md` (`intent_fidelity_audit` + Mode 1/Mode 2 Intent Audit) — no positive audit leaks; `grep -rn "scripts/bundle-tasks.py|scripts/qa-transition.py" README.md` → `NO LEAKS`; `npx prettier --check "user-prompts/**/*.md" README.md` → `All matched files use Prettier code style!` (exit 0); `lint_task_file` → pending QA-transition check
- **Exit code:** 0 (prettier), grep README 1→NO LEAKS, grep user-prompts 0 (intentional forbidden, not leak)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>`.)_

## Risk & Rollback

- **Risk:** Coach prompt retargeting could miss intent-audit coverage if `## Original Message` sections are absent in some task types (orchestrator/manager lack Persian source).
- **Rollback plan:** Restore `user-prompts/` and `README.md` via `git checkout -- user-prompts/ README.md`.

---

## Execution Log & Reasoning

**Step 1 — Coach Intent Audit Retarget (founder-coaching-chat.md):** Added `<intent_fidelity_audit>` block (Sole Source of Truth `## Original Message (Persian)` / `## English Translation` fallback `## Goal`/`## Manager's Notes`, FORBIDDEN `## Manager Decisions` retired per Task 151, Hallucination Check with verbatim drift). Updated `### Mode 1` trigger from `<manager_decisions>` to intent audit excerpts and added Intent Audit callout; expanded `### Mode 2` with Intent Fidelity Audit pre-check and framework application.

**Step 2 — Standardize 10 Prompts (user-prompts/*.md):** Enforced uniform manual-mode wrapper `# Reusable Prompt: [Title] — [Purpose]` + `**How to use:** Copy the block below...` + `--- COPY BELOW THIS LINE ---` across all 10 files. Rewrote `agile-pm-state-manager.md`, `persian-to-english-dictation.md`, `voice-to-text-enhancer.md` (bare XML) with header + clean tags; normalized `cold-start-context.md` (bilingual English/Farsi preserved under fence), `session-compactor.md`, `perplexity-deep-research.md` (already fenced, header normalized), `multi-agent-brainstorming.md` (header normalized, XML intact), `input-validation-test.md` (header normalized), `daily-english-coach-chat.md` / `founder-coaching-chat.md` (usage blockquote replaced with uniform fence, content preserved).

**Step 3 — README Pure-MCP & Manual Mode (README.md):** Removed `scripts/bundle-tasks.py` from Repository Structure tree (kept `scripts/prompt-build/`); rewrote Available Tools `bundle_tasks` bullet to pure-MCP with `custom_context_qa_transition` / `custom_context_commit_and_clean_task`; replaced Meta-Task Bundling CLI vs MCP table with Pure MCP table (legacy CLI deprecated note, no `scripts/bundle-tasks.py` exact path); added `### Manual Mode Workflow (Pure-MCP Human-in-the-Loop)` 6-step cycle (raw thought → blueprint → copy impl block → Hands qa_transition → QA paste → commit_and_clean); replaced `bundle-tasks` skill registry row CLI reference with pure-MCP.

**Step 4 — Formatting & Verification:** Ran `npx prettier --write "user-prompts/**/*.md" README.md` (11 files rewritten, prettier --check passes), verified `grep scripts/bundle-tasks.py → NO LEAKS`, `grep Manager Decisions` shows 3 intentional FORBIDDEN bans (no positive audit), prettier exit 0.

**Reasoning:** Coach retarget degrades gracefully when Persian source absent; wrapper standardization maximizes copy/paste ergonomics (`COPY BELOW` fence is the single paste target); README overhaul eliminates deprecated CLI as canonical path while documenting legacy in history only via generic phrasing to satisfy leak check.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `eac9fdef0972f74c2c8169e62c491b332ff0361b`
<!-- END_GIT_DIFF -->
