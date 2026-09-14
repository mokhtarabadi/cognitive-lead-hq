# Task 209: Discovery-fed Brain planning with session-persistent context

**File:** `tasks/completed/209-discovery-fed-brain-planning-with-session-persistent-context.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Mode:** autopilot-locked (manager ordered autopilot to the end with a goal; closure approval not yet given)

## Goal

Make Brain planning run on real discovery context: when Brain returns a discovery XML during planning, the Hands execute it and feed the context back before the final plan, and that context stays reachable until session end.

## Manager's Notes

Manager's verbatim message (Persian, preserved word-for-word):

> یه یچزی به ذهنم رسید تسک کن و بعدش روش کار میکنیم
> الان توی فاز یک وقتی میخواایم به brain بگیم برامون plan بزنه
> اگه برین task xml بده برای فاز discovery ایا تون اون رو احرا میکنی که و خروجی context رو بهش بدی برای رنامه ریزی؟
> که دقیقا از روی context نظر بده؟
> همینطور ایتن کانمست یا post context ها تا انهتای سشن براش قابل دسترس باشه؟
> کاری که من در حالت دستی انجام میدم

English translation: Something came to mind — file it as a task and we will work on it later. Now in phase one, when we ask the Brain to plan for us, if the Brain gives task XML for the discovery phase, do you execute it and give the context output back to it for planning, so it opines exactly from context? Likewise, do these contexts or post-contexts stay accessible to it until end of session? That is what I do manually.

Refactored intent: extend the planning gate into a discovery-fed loop (plan request → Brain discovery XML → Hands execute → context back to Brain → final plan grounded in context), with the fed context persisted in the task session transcript so it stays reachable through session end. Park for later, do not implement yet.

## Local TODOs

- [x] Initial codebase exploration
- [x] Map planning-gate and discovery paths in executor and bridge
- [x] Design discovery-fed loop and session persistence rule
- [x] Verify functionality

## Acceptance Criteria

- [x] Planning with a discovery step executes the discovery XML before the final plan
- [x] Final Brain plan cites the fed context, not assumptions
- [x] Fed context stays reachable in session history until session end
- [x] Manual manager ferrying of context stays unnecessary in autopilot

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with pyyaml --with mcp==1.30.0 python -m pytest tests/ -q`
- **Expected result:** all tests pass, exit 0
- **Actual result:** 245 passed (237 baseline plus 8 new fed-context tests), 8 warnings
- **Exit code:** 0
- **Probe:** planning turn returned discovery XML, 3 subagents executed, fed context returned grounded blueprint citing CTX-1..CTX-5; empty-output flake on 2 turns recovered via lean retry per standing rule

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** extra Brain turns per plan cost tokens and time; unbounded discovery loops.
- **Rollback plan:** keep the loop behind the existing planning gate with a guard (max one discovery round); revert to current gate behavior.

---

## Execution Log & Reasoning

Autopilot locked per manager order ("do the task, go to the end", goal created). Manager direct order counts as approval to implement from the Brain blueprint below.

Plan verdict (Brain Architect, task_id 209, REPORT, no XML): discovery-fed loop with max 1 discovery round and max 2 planning turns, same-task_id chaining, pinned fed_context.md exempt from compaction, grounding citations D10-D12, token guards G1-G5. Selected path O1 (pinned file plus transcript tag). Side finding CTX-5 (context MCP false gitignore) parked as separate follow-up.

Discovery executed first per Brain request: 3 parallel subagents (tree plus core files, bridge signatures plus history, planning fragments). Fed back as CTX-1..CTX-5, final plan grounded in it. Assumption A1: manager "go to the end" approves blueprint implementation; closure still needs explicit approval word.

Implementation (from approved blueprint, selected path O1): E1 added Discovery-fed planning subsection to executor Planning Gate (one discovery round, two planning turns max, same-id chaining, grounding citations, halt on second discovery). E2 added fed-context pinning to bridge (extract/save/load helpers, 20k cap, atomic write, prepend with pin header, exempt from compaction by separate-file design). 8 new offline tests (extract present/unclosed/absent, roundtrip, cap, clear, save-bad-id, load-bad-id). Full suite 245 passed. CHANGELOG Unreleased entry added (executor-only change, no prompt rebuild).

QA round 1: QA_PASSED with residuals. Honored F3 (load/bad-id doc mismatch): load now catches ValueError too, plus load-bad-id test. F2 (pid-only tmp collision) accepted as low risk: Hands use is sequential, same pattern as existing transcript writes. F4 (marker spoof) accepted: Hands control prompts. M1 (prepend wiring test) and M3 (double block) noted as follow-ups, non-blocking.

Reviewer round 1: APPROVED_WITH_CHANGES, all 3 findings reproduced and fixed (CHANGELOG 244→245, save/path docstrings now state ValueError). Suite still 245 passed. Re-review requested.

Reviewer round 2: technically approved, no blocking issue. One wording note honored (CHANGELOG now says gate plus pinning, not doc-only). Moved to qa. Closure needs explicit approval word; autopilot stops here per ZAC.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `88046734173402ddf6e0718a82a7b5959ed0fa68`
<!-- END_GIT_DIFF -->
