# Task 243: DECISION_* env support for decision server

**File:** `tasks/completed/243-decision-env-support.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Give the manager-decision server its own DECISION_API_BASE, DECISION_API_KEY, DECISION_MODEL, DECISION_REASONING_EFFORT envs (BRAIN_* fallback), and document them.

## Manager's Notes

Manager order, exact: "define and use following env too and update project docs and example and then continu your goal" with DECISION_API_BASE=https://openrouter.ai/api/v1, DECISION_API_KEY=<OpenRouter key, SECRET — never quote>, DECISION_MODEL=openai/gpt-5.6-luna, DECISION_REASONING_EFFORT=xhigh. Supersedes the earlier deepseek DECISION_MODEL value.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Wire DECISION_* reads with BRAIN_* fallback in mcp-decision-server/server.py
- [x] Set the 4 values in HQ .env (mode 600, gitignored, values never printed)
- [x] Extend .env.example DECISION section + fallback docs
- [x] Contract tests (precedence, blank-fallback, fail-closed); suite green

## Acceptance Criteria

- [x] Decision server reads all 4 DECISION_* envs, falls back to BRAIN_* when blank/unset
- [x] Missing both keys fails closed naming both env names
- [x] Docs + example updated; decision suite + full suite green

## Verification Evidence

- **Test command:** `uv tool run --with "mcp==1.4.1" --with pathspec --with pyyaml --with pytest pytest tests/ -q`
- **Expected result:** exit 0, all pass
- **Actual result:** 396 passed, zero failures (decision suite 108 incl. 3 new contract tests)
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** secret handling — key must never appear in chat, logs, diffs, or committed files
- **Rollback plan:** `git checkout -- mcp-decision-server/server.py`; unset the 4 DECISION_* lines (BRAIN_* fallback restores old behavior)

---

## Execution Log & Reasoning

Seat Check: Senior Programmer (server env wiring + contract tests). No UI/schema/sprint triggers; Designer/Planner/Strategist/QA/Reviewer skipped — small scoped wiring, judged via suites + lint. Autopilot: this task was executed under the manager's standing autopilot lock; replay lineage from stored rulings (fix-all on autopilot, zero-questions standing order).
Edits: `mcp-decision-server/server.py` — `_get_api_base()` helper (DECISION_API_BASE → BRAIN_API_BASE → default const), `_get_decision_effort()` reads DECISION_REASONING_EFFORT → BRAIN_REASONING_EFFORT, `_get_api_key()` reads DECISION_API_KEY → BRAIN_API_KEY (fail-closed names both), call site uses the helper. `DECISION_MODEL` was already read with blank-fallback (pre-existing). HQ `.env` holds all 4 values (key copied programmatically from the BRAIN key; values never printed; mode 600; gitignored). `.env.example` DECISION section extended. Tests: 3 new contract tests + 2 old tests fixed for env hermeticity. Decision suite 108 passed; full suite 396 passed, zero failures, exit 0.
- Live Brain QA verdict (gpt-5.6-luna, trunc 0): VERDICT QA_PASSED. Precedence, blank/whitespace fallback, fail-closed key, effort-only-without-temp all confirmed (CITE server.py:219,908,964; .env.example:23; tests :458). No vuln. M1/M2 = non-blocking coverage suggestions (all-four-env outbound test; whitespace BRAIN_API_BASE). Self-improvements S1 (task-scoped diff ownership) + S2 (auto env-matrix test) noted as future work.
- Manager accept (exact quote): "Approved for closure."
- Reviewer verdict (gpt-5.6-luna): PO_REVIEW_PENDING — technical approval, no blocking issues; precedence, blank fallback, fail-closed key, API-base helper, reasoning config, docs all match (CITE server.py:219,908,964 + .env.example:23); no secret in diff; closure only on exact phrases.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3f2398d2aeea275a7308b9dc9379031b43665b9a`
<!-- END_GIT_DIFF -->
