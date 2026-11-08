# Task 0352: Plan approval must show the plan before asking

**File:** `tasks/completed/0352-plan-approval-shows-plan-first.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Finished:** 2026-10-26T19:43:55Z
**Submitted:** 2026-10-26T19:34:50Z
**Estimate:** 1h
**Deadline:** 2026-10-26
**Started:** 2026-10-26T19:28:32Z

## Goal

Make every plan-approval gate present the approved plan to the Manager before the approval question appears. Today the Hands calls the `question` tool with a bare approval ask while the plan stays inside the Brain's `output`, which the Manager never sees.

## Manager's Notes

> system has a bug, it ask me for approve plan , but never show me the plan first, find it and fix automaticlly within a task and brain mode auto lock

Autopilot is LOCKED for this task: find the cause and fix it without a separate plan pause or implementation pause. ZAC holds; closure still needs the exact approval word.

## Root cause (verified in the prompt corpus)

- `agents/cognitive-executor.md` "Autopilot mode" states "In autopilot the Manager sees only Relay questions and the final verdict report", which reads as an instruction to suppress the plan body.
- The "Supervised autopilot plan approval" section says "show the Brain-approved plan to the admin" but never says where or in what order, and never says the `question` payload must carry the plan.
- "Capability Preflight" says the plan gate collects the decision "via the question tool with one narrow question and one answer slot", which pushes toward a short, plan-free question.
- The Brain Bridge state machine treats a plan `REPORT` as "triage like a review verdict"; no step says the plan text reaches the Manager.
- Net effect: the Hands emits an approval card whose body is only "Approve the plan?" and the plan lives and dies in the tool result.

## Local TODOs

- [x] Add a Plan presentation contract to the executor (chat-first, full plan, question payload carries it, bare ask forbidden)
- [x] Fix the autopilot "sees only Relay questions" sentence
- [x] Bind the plan gate wording in Capability Preflight to the plan body
- [x] Add a regression test on the executor contract in `tests/test_prompt_sync.py`
- [x] Sync the live global agent copy at `~/.config/opencode/agents/cognitive-executor.md`
- [x] Living docs: `agents/DECISIONS.md` ADR + `agents/README.md` invariant
- [x] CHANGELOG entry
- [x] Run the suite and `lint_task_file`

## Acceptance Criteria

- [x] `agents/cognitive-executor.md` carries an explicit Plan presentation contract: the plan body is written into the chat in the same turn, in full, before the `question` tool call; the question payload repeats the plan; a bare "Approve the plan?" ask is a protocol violation.
- [x] The autopilot sentence no longer claims the Manager sees only Relay questions; it names the plan as visible.
- [x] The Capability Preflight plan-gate sentence requires the full plan in the question payload instead of a bare narrow question.
- [x] A regression test in `tests/test_prompt_sync.py` asserts the contract text exists and the old suppressing sentence is absent.
- [x] The live agent copy at `~/.config/opencode/agents/cognitive-executor.md` matches the repo file byte for byte.
- [x] `agents/DECISIONS.md`, `agents/README.md`, and `CHANGELOG.md` record the change.
- [x] Full suite green and `lint_task_file` green.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/ -q`
- **Expected result:** full HQ suite green including the new prompt-contract test
- **Actual result:** `735 passed, 24 warnings in 59.33s`; new `test_executor_shows_plan_before_asking_for_approval` verified red first (`AssertionError: assert 'Plan presentation contract' in ...`) then green; `diff` of the live agent copy against the repo file exits 0. QA round 1 returned `QA_PASSED` with two hardening notes, both applied and re-verified (`735 passed in 61.17s`, exit 0): the prompt gate now also asserts the question-payload sentence, the preflight binding, the REPORT-surfacing rule and the positive autopilot sentence, so a partial deletion cannot pass; the planner week test now derives the expected week from `date.today().isocalendar()` instead of the implementation helper.
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** the plan body duplicated in chat and in the question card looks redundant; accepted, because a client may render only one of the two surfaces.
- **Risk:** a very long plan makes the question card unwieldy; mitigated by requiring the chat message as the primary surface and the question body as the same text.
- **Rollback:** revert the executor paragraphs and the regression test; the previous (buggy) behaviour returns.

---

## Execution Log & Reasoning

**Mode.** Autopilot LOCKED per the Manager's order ("fix automaticlly within a task and brain mode auto lock"). Standing order `manager/full_automatic_mode` (2026-09-17) plus this order authorize plan-then-implement without a separate pause. Because the bug being fixed is an approval card with no plan, this task also applies the new contract to itself: the Brain plan was reproduced in the chat before any approval step.

**Seat Check.** Domains: agent prompt contract (approval-gate ordering) plus the user-facing approval surface. Seats requested: Software Architect (whole-word trigger `contract` in the task body), UI/UX Designer (UX-intent fallback: the broken surface is the approval card; no layout keyword fired). Skipped: Senior Programmer (no runtime code change), QA/Reviewer (later stages), Planner/Strategist (no scheduling decision). Brainstorm: not required — single-file prompt-contract fix, reversible, no cross-disciplinary irreversibility.

**Brain plan verdict.** `REPORT` on the first planning turn, model `muse-spark-1.3-contributor`. Selected path: plan presentation contract in the executor, fix the suppressing autopilot sentence, bind the preflight plan gate, regression test, live sync, living docs. The Brain explicitly rejected a code-level guard in `mcp-brain-bridge` as overkill and confirmed the bridge already returns the full plan in `output`.

**Root cause (F1-F3).** F1: `agents/cognitive-executor.md:471-486` told the Hands that in autopilot "the Manager sees only Relay questions and the final verdict report" — read as a ban on showing the plan. F2: `:125` asked for "one narrow question and one answer slot" at the plan gate, with no payload requirement. F3: `:308-322` said "show the plan" with no order or surface, and `:415-419` triaged a plan `REPORT` as a verdict to file. The plan itself was never missing: `mcp-brain-bridge/server.py:4055` returns it verbatim in `output`; it was dropped at presentation time. The `question` card is rendered independently of the assistant message, so a card-only ask leaves the Manager nothing to approve.

**Fix.** Added a four-rule Plan presentation contract under Supervised autopilot plan approval (chat first in full, question repeats the plan, bare ask is a protocol bug, revision rounds print the revised plan). Reworded the autopilot sentence to name the plan as visible. Bound the Capability Preflight plan gate to the contract. Marked a plan `REPORT` as a plan to surface. Fixed nothing in the bridge on purpose: the fault was policy, not transport.

**Verification shape.** TDD: the new prompt-sync test was written first and failed on the missing contract string, which proves it guards the behaviour rather than the wording of a pre-existing paragraph. After the edit the full suite passed. The live agent copy was edited with native tools (four mirrored edits) and `diff` against the repo exits 0, so the running system carries the fix, not just the checkout.

**Adjacent defect found by the green run.** `tests/test_planner_server.py::test_plan_api_admin_only_and_persists` hardcoded the plan week as `2026-W43` while `GET /api/plan?window=week` resolves the current ISO week. It passed until the W43 to W44 rollover on 2026-10-26 and then failed with `'NoneType' object is not subscriptable`. Retargeted to `planner._plan_week_key()` so the test tracks the clock instead of a calendar guess; unrelated to this task's code path, recorded here and in the CHANGELOG because the suite could not be green otherwise.

**Assumption A1.** `Estimate: 1h` and a same-day deadline were chosen by the Hands, since the Brain plan carried no estimate and the Manager gave no size; `schedule_tasks` owns those header lines rather than a hand edit.

**QA cycle 1 (Brain).** `QA_PASSED` with four vulnerability checks (both-mode binding, transport not at fault, live sync, legitimacy of the skipped pause) and two hardening notes: the prompt gate was too narrow to catch a partial deletion, and the week repair proved itself from the implementation helper. Both were fixed before the next round, which is why the gate now asserts eight strings including the revision rule, and the week now comes from `date.today().isocalendar()`.

**QA cycle 2 (Brain).** `QA_PASSED` again, with two cosmetic notes: the revision-round rule was still unasserted and the CHANGELOG still named the helper as the week source. Both closed (ninth assertion, CHANGELOG sentence corrected) and the full suite re-ran green.

**Code Reviewer (Brain).** Technically approved, `PO_REVIEW_PENDING`, severity Low. One note only: the `__import__("datetime")` inline import in the planner test differs from the file's top-level import style; the reviewer recommended leaving it for this task and moving it on the next edit of that file. No blocking defect. The reviewer confirmed no fragment edit and no `<system_version>` bump were due, because the Brain side already required present-then-ask and only the Hands side dropped the plan.

**Final gate state:** QA_PASSED and PO_REVIEW_PENDING recorded. Closure waits for the Manager's exact word.

**Manager closure approval (2026-10-26):** "Approved for closure" via the question tool, answering the relayed PO_REVIEW_PENDING verdict. ZAC holds throughout: no `git add`, no `git commit`, no `git push`; closure runs only through `custom_context_commit_and_clean_task`.

**Closure:** preconditions verified (QA_PASSED, PO_REVIEW_PENDING, exact approval quote, injected diff), file moved with `git mv` to the completed lane, `**Status:** closed` and the `**File:**` header synced.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ad4cf1252ad4b317403d5ee9b81c56d59ca13db4`
<!-- END_GIT_DIFF -->
