# Task 171: post-sprint-workspace-bundle

**File:** `tasks/completed/171-post-sprint-workspace-bundle.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Supersedes:** [169, 170]
**Meta:** true
**Created:** 2026-09-08 22:28 UTC
**Bundled:** 2 tasks

## Goal

Unified execution of 2 related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks [169, 170] — "post-sprint-workspace-bundle" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.

> ⚠️ **Guardrail Warning:** Combined source size is 10984 LOC (> 400). Unified META diff may be large and hard to review. Consider splitting into two METAs.

**Source IDs:** [169, 170]
**Next ID:** 171 (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)
**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: 171-post-sprint-workspace-bundle` and remain reachable via `git log --follow` (never purged until META is completed).

## Manager's Notes

**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute 2 small related tasks together and speed up turnaround.

**Traceability:**
- Supersedes [169, 170] — see per-source verbatim blocks below
- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** 171-post-sprint-workspace-bundle` header + superseded footer
- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file

**Guardrails Applied:**
- Cap 6 per bundle — this bundle has 2 (✅ within cap)
- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)
- Diff-size check — combined 10984 LOC (⚠️ exceeds 400 — consider split)

## Source Bundles (Verbatim Preservation)

The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.

### Source Task 169: Track Post-Sprint Working Changes

**Original File:** `tasks/in-progress/169-track-post-sprint-working-changes.md` → `tasks/archive/169-track-post-sprint-working-changes.md` (after bundling)

**Title:** Track Post-Sprint Working Changes

#### Goal (verbatim)

Bring the uncommitted post-sprint working changes (temperature fix, global install, install-docs sync, live smoke script) under Kanban tracking for review, verification, and staged commit.

#### Manager's Notes (verbatim)

- Covers ad-hoc work done after Tasks 167/168 closed: PERSONA_TEMPERATURE 0.2→1.0, global install of new servers/skills/agents + `.env` backup, LLM.txt/README/memory doc sync, `scripts/smoke_test_live.py`.
- `.env` (live secrets) stays OUT of git scope — verify ignored + untracked, never stage.
- Work is already implemented and locally verified; this task exists to review, re-verify, and commit it through the normal pipeline.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

#### Acceptance Criteria (verbatim)

- [x] Every working change listed in Manager's Notes is accounted for in the diff
- [x] Full test suite passes with exit code 0
- [x] No secrets (`.env`, keys, tokens) staged or committed

#### Local TODOs (verbatim)

- [ ] Review unstaged diff (`git status`, `git diff`) for unintended content
- [ ] Re-run full test suite and record evidence
- [ ] Verify `.env` ignored and untracked; verify no secrets in staged files
- [ ] Stage via `custom_context_stage_and_inject_diff`, move to QA, await review

#### Risk & Rollback (verbatim)

- **Risk:** Accidentally staging `.env` or secret-bearing files; committing unrelated scratch content.
- **Rollback plan:** Unstage specific paths (`git reset -- <path>`); secrets committed by mistake require history rewrite + key rotation.

---

### Source Task 170: MCP Workspace Cleanup, Approval Notes, Split Models

**Original File:** `tasks/in-progress/170-mcp-workspace-approval-notes-split-models.md` → `tasks/archive/170-mcp-workspace-approval-notes-split-models.md` (after bundling)

**Title:** MCP Workspace Cleanup, Approval Notes, Split Models

#### Goal (verbatim)

Clean up the MCP server layout into locked uv projects with a shared common lib (D1), add optional manager notes to approval gates (D3), and split persona vs decision LLM models via env (D4).

#### Manager's Notes (verbatim)

- Approved scope from D1/D2/D3/D4 proposal: D1 full (per-server pyproject + uv.lock, shared `mcp-common`, `--project` launch commands), D3 (force-reply note, independent timeout, never blocks gate), D4 (`DECISION_MODEL` with `PERSONA_MODEL` fallback).
- After implementation: inject diff into this file, upgrade the global install, and hand off with a restart-and-test instruction.
- `.env` secrets stay out of git; lockfiles (`uv.lock`) ARE committed for reproducibility.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

#### Acceptance Criteria (verbatim)

- [x] Persona turns use PERSONA_MODEL, extraction uses DECISION_MODEL (fallback verified)
- [x] Approval gate can return an optional manager note without blocking on silence
- [x] Every server runs locked (`uv.lock`) via `--project`; shared loader lives in one place
- [x] Global install mirrors repo; post-restart smoke green

#### Local TODOs (verbatim)

- [x] D4: DECISION_MODEL env + fallback + tests + docs
- [x] D3: approval note flow + tests
- [x] D1: mcp-common lib + 5 pyprojects + locks + --project commands
- [x] Full suite green, task file injected, global upgraded

#### Risk & Rollback (verbatim)

- **Risk:** `--project` launch form behaves differently (cwd/env); workspace refactor breaks test import paths.
- **Rollback plan:** Keep server code untouched in shape (only loader import source changes); revert opencode.json commands to plain `uv run <path>`; per-server locks are additive files.

---


## Bundled Checklist (All-or-Nothing)

> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.

- [x] [169] Every working change listed in Manager's Notes is accounted for in the diff
- [x] [169] Full test suite passes with exit code 0
- [x] [169] No secrets (`.env`, keys, tokens) staged or committed
- [x] [170] Persona turns use PERSONA_MODEL, extraction uses DECISION_MODEL (fallback verified)
- [x] [170] Approval gate can return an optional manager note without blocking on silence
- [x] [170] Every server runs locked (`uv.lock`) via `--project`; shared loader lives in one place
- [x] [170] Global install mirrors repo; post-restart smoke green
- [x] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Local TODOs

- [x] Step 1: Validate META bundle — confirm all 2 source requirements are captured verbatim below
- [x] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)
- [x] [169] Review unstaged diff (`git status`, `git diff`) for unintended content
- [x] [169] Re-run full test suite and record evidence
- [x] [169] Verify `.env` ignored and untracked; verify no secrets in staged files
- [x] [169] Stage via `custom_context_stage_and_inject_diff`, move to QA, await review
- [x] [170] D4: DECISION_MODEL env + fallback + tests + docs
- [x] [170] D3: approval note flow + tests
- [x] [170] D1: mcp-common lib + 5 pyprojects + locks + --project commands
- [x] [170] Full suite green, task file injected, global upgraded
- [x] Step 11: Verify all bundled checklist items and run lint_task_file + verification-before-completion
- [x] Step 12: Update CHANGELOG.md and record Verification Evidence

## Acceptance Criteria

- [x] [169] Every working change listed in Manager's Notes is accounted for in the diff
- [x] [169] Full test suite passes with exit code 0
- [x] [169] No secrets (`.env`, keys, tokens) staged or committed
- [x] [170] Persona turns use PERSONA_MODEL, extraction uses DECISION_MODEL (fallback verified)
- [x] [170] Approval gate can return an optional manager note without blocking on silence
- [x] [170] Every server runs locked (`uv.lock`) via `--project`; shared loader lives in one place
- [x] [170] Global install mirrors repo; post-restart smoke green
- [x] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Verification Evidence

- **Test command:** full pytest suite (see source tasks) + `lint_task_file` on META + `git status` secret scan
- **Expected result:** 108 passed exit 0; META lint clean; both sources archived with superseded markers; no `.env`/keys staged
- **Actual result:** `108 passed, 8 warnings in 1.18s`; META lint clean (verified post-stage); `tasks/archive/169-*` + `tasks/archive/170-*` carry `Status: superseded` + `Superseded-By: 171` (traceability via `git log --follow` activates at META commit); secret scan clean
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.
- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.
- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.
- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded [169, 170], remove Superseded-By footer, delete or archive `tasks/backlog/171-post-sprint-workspace-bundle.md` as abandoned. No HQ code beyond bundler is affected.

---

## Execution Log & Reasoning

### Pipeline Stage 1 — QA Round 1 (DeepSeek, live)

QA returned **QA_REJECTED** with F1–F10. Disposition, each verified against code (not taken on authority):

- **Fixed F5 (temperature hardcode — fair catch):** `extract_session_decisions` had hardcoded `temperature=0.2`. Added `DECISION_TEMPERATURE` env (default 1.0, clamped to [0,2], never crashes); wired through `.env.example` + both opencode.json `environment` blocks + 4 tests.
- **Fixed F2-partial (BOM):** loader now reads `utf-8-sig` (one-word fix); added BOM/CRLF/literal-`#` tests. Inline `#` stays literal by design (values are tokens/paths — documented in test).
- **Fixed F8 (drift guard):** both suites now assert every tool docstring carries `WHEN TO CALL`.
- **Fixed F6-partial:** empty-string replies → None test added; /skip-vs-silence indistinguishability accepted and documented (note is garnish; decision is the gate).
- **Fixed F3-test:** fallback-chain test added (file-masquerading-as-dir forces OSError deterministically). Crash claim itself was wrong — the code already catches OSError per candidate.
- **Verified, no change:** F9 (each lock has its pyproject; locks new-by-construction; mcp-common referenced 4× in both locks); F10 (transcript-format regression test exists in the 112+6 suite); F4 (missing-script/absent-sample paths already return graceful ERROR/message dicts; stale `packages/` refs grepped — one live docstring fixed, rest is history); F7 (600s is the watchdog — opencode aborts the call at timeout; documented tradeoff, cancellation tokens out of scope).
- **Disputed F1 (blocker downgrade):** the demanded tristate (`KEY=` forces empty) contradicts our documented convention that blank means "use fallback" (`DECISION_MODEL=` relies on it). Standard dotenvinfers empty-override, but OUR contract (written in `.env.example`) is blank-means-unset — and the dangerous direction was always blank-process-env shadowing files, which is fixed and tested. Keeping current semantics deliberately.
- Suite now **118 passed**; global copies re-synced, drift clean.

### Pipeline Stage 2 — Code Review triage (DeepSeek, live)

Reviewer verdict: **FAIL** (B1–B10). Triaged against code evidence:

- **B1 re-litigates disputed F1** — rejected again (blank-means-unset is now codified in `docs/conventions.md`; tristate would break the `DECISION_MODEL=` fallback contract).
- **B2 valid** — CHANGELOG entry added above.
- **B3 valid** — loader precedence + blank convention now anchored in `docs/conventions.md` (the exact quirk-file for this).
- **B4 rejected with evidence** — DeepSeek's own default temperature IS 1.0; house policy (researched) is 1.0; `DECISION_TEMPERATURE` makes it configurable. No regression.
- **B5 factually wrong** — all staging via `custom_context_stage_and_inject_diff` (tool receipts in this log); only `git mv` used directly (explicitly allowed).
- **B6 verified** — porcelain shows only intended files; all 6 lock/pyproject pairs present, new-by-construction.
- **B7 closed** — export-prefix, spaced-equals, unclosed-quote tests added.
- **B8 verified** — repo-wide grep: zero live `packages/` refs (remaining hits are this file's own rename diff + history).
- **B9 closed** — explicit `/skip` test added; concurrent-gate race accepted as documented single-manager limitation.
- **B10 verified** — no pre-commit config exists; pytest IS the gate and both docstring guards run in it.
- Suite now **120 passed**.

### Pipeline Stage 3 — Admin Approval Gate (Telegram, live)

**APPROVED** (`decision: "approve"`, update 453030869; manager note: `"approve"`). Gate passed — proceeding to closure (Stage 4).

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `a37c3cb96c6f76498bf392b7914d4e910a201f72`
<!-- END_GIT_DIFF -->
