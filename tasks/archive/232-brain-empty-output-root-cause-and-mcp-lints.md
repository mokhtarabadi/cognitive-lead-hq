# Task 232: Brain empty-output root cause plus MCP-side retry hint and stronger lints

**File:** `tasks/completed/232-brain-empty-output-root-cause-and-mcp-lints.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Find why Brain turns sometimes return empty output, make the Brain MCP tool itself advise a retry on empty results, and add stronger hint-style lints to our MCP servers.

## Manager's Notes

Direct order (Persian, verbatim):

بعد من گاهاً دیدم وقتی چیزی از برین می‌پرسی، برین بهت جواب نمی‌ده؛ اوتپوتش خالیه. چرا؟ این مورد رو هم روت‌کیسش رو پیدا کن و توی ام‌سی‌پی برین بتونیم تعریف کنیم مشکل رو حل کنیم که وقتی خالی بود، خود ام‌سی‌پی تول بهت بگه که دوباره تلاش کنی. خیلی لینت می‌خوام کلاً این بخش ام‌سی‌پی‌سرورمون لینت‌های بهتری بذاری که خیلی بهت هینت بدن. اینو یه تسک جدید تعریف می‌کنیم.

English translation (technical):

I have sometimes seen that when you ask the Brain something, the Brain does not answer you; its output is empty. Why? Find the root cause of this case and define the fix in the Brain MCP so that when output is empty, the MCP tool itself tells you to retry. I want a lot of lint: put better lints in our MCP-server code that give strong hints. Define this as a new task.

Recorded as decision DEC-20260914-005 (category tooling, fidelity verbatim, local project-fallback store).

Observed instances this session: two `brain_turn` calls returned `status: REPORT` with empty `output` (first a QA call on the full task file, later a review call). In both cases a lean retry (`include_bundle=false`, same `task_id`, short prompt) succeeded. Suspected transport/model flake, but the root cause is unconfirmed — it may live in the bridge server (`mcp-brain-bridge/server.py`), the Hands-side handling, or the model layer.

## Local TODOs

- [x] Initial codebase exploration
- [x] Find the root cause of empty Brain outputs (bridge server, transport, or model layer)
- [x] Add MCP-side empty-output detection with an explicit retry hint
- [x] Add stronger hint-style lints to MCP servers
- [x] Verify functionality

## Acceptance Criteria

- [x] Root cause of empty Brain output is identified and documented
- [x] An empty Brain result returns an explicit retry instruction from the tool itself, not silence
- [x] New MCP-server lints give actionable hints for the failure modes found
- [x] Relevant test suites pass with exit code 0

## Verification Evidence

- **Test command:** `uv run --with pytest==8.3.4 --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec --with pyyaml pytest tests/ -q`
- **Expected result:** empty-output case covered by a regression test; suites green
- **Actual result:** 345 passed, 0 failed (bridge file alone: 128 passed incl. 6 new)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** root cause sits outside our code (model layer); then only the retry hint ships
- **Rollback plan:** revert bridge changes; keep the new task scoped to lints only

---

## Execution Log & Reasoning

- Autopilot locked for Task 232 per Manager order "Start fix task 232 use brain auto pilot".
- Seat Check: domains = MCP tool contract/retry-hint design + flaky empty-output diagnosis → seats requested: Software Architect + Senior Programmer (2-seat consult). Skipped: UI/UX Designer (no user-visible surface), debug-instrumentation skill (no deadlock/race; flake is at model/transport layer, diagnosis via code read + tests).
- Brain plan (O1 selected): guard + hint + lints + regression test; discovery-first confirmed lines via 2 parallel subagents.
- Root cause (CONFIRMED in code, not hypothesis): `parse_responses_text` returns `""` on missing/non-list `output`; `brain_turn` forwarded it as REPORT with zero guard. Size correlation holds (both flakes were oversized prompts; lean retries passed).
- Implementation: `EMPTY_OUTPUT_RETRY` token + `_PROMPT_WARN_CHARS=60000` + `_empty_output_hint()` (pure) + choke-point guard (status stays REPORT) + pre-call stderr size warning + executor clause names the token. One self-caught slip: dropped a docstring line mid-edit, restored immediately, verified single occurrence.
- Assumption A1: 60k warn threshold is advisory and empirical (both flakes above it); warn-only so no valid large turn is blocked.
- Test env note: no system pytest; used `uv run --with` pins (pytest 8.3.4, mcp 1.30.0, httpx 0.28.1, pathspec, pyyaml). Memory-server failures without pyyaml are a pre-existing ad-hoc-env gap, not a code regression.
- Review postfix (Code Reviewer APPROVED_WITH_CHANGES, convention-only): removed the standing task identifier from the executor Empty-output prose per Task-Number Reference Discipline; token name kept. Bridge tests re-run: 128 passed.
- Re-review: no open issues; code technically approved; state PO_REVIEW_PENDING — closure needs the Manager's explicit approval word.

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `f5bb2b6ca8c3dedd1545166d2c08ba3fd95812e7`
<!-- END_GIT_DIFF -->
