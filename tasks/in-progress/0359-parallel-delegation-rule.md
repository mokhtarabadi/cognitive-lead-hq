# Task 0359: Parallel-delegation decision rule (discovery-only mandate → R&D + implementation lanes)

**File:** `tasks/in-progress/0359-parallel-delegation-rule.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Give the Hands an explicit decision rule for parallel subagent use beyond discovery: triggers for parallel R&D/implementation, disjoint file-ownership partitioning, and a verify-and-merge protocol — plus fix the stale "`task`/subagent" reference in the code-search skill.

## Manager's Notes

Manager observed single-threaded execution outside discovery and asked whether the system prompt / executor need multi-agent knowledge, then ordered a small autopilot task limited to what the Hands endorses.

## Scope (endorsed only)

1. `13-constraints.md` mandate: add R&D/implementation triggers + ownership/merge protocol (discovery wording untouched).
2. Executor: add an implementation-delegation lane under Subagent Delegation (read-only discovery lane untouched).
3. `code-search/SKILL.md`: "`task`/subagent calls" → "`subagent` calls".
4. Version bump + prompt regen + pin test update + 1–2 regression asserts + CHANGELOG + global sync.

Out of scope (not endorsed): inventing a new write-capable agent; blessing runtime `explore`/`general` with contracts; touching lane caps or QA gates.

## Local TODOs

- [x] Brain plan turn under this task_id
- [x] Edit mandate + delegation lane + skill reference
- [x] Bump version, regen prompt, update pin test, add asserts
- [x] CHANGELOG + global sync + cmp verify
- [x] Run planner/prompt test subset + verify

## Acceptance Criteria

- [x] Mandate names implementation/R&D triggers distinct from discovery triggers
- [x] Delegation lane requires disjoint file ownership + Hands verification of each lane
- [x] No "`task` tool" reference remains in executor or code-search skill
- [x] Shipped prompt regenerates byte-clean; pin test updated; new asserts green
- [x] Global copies cmp-identical to repo

## Verification Evidence

- **Test command:** rtk test [exact command]
- **Expected result:** prompt-sync + skill-registry subsets green
- **Actual result:** _(filled during execution)_
- **Exit code:** _(filled during execution)_

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** broader mandate could push subagents into coupled edits; mitigated by disjoint-ownership requirement.
- **Rollback:** revert fragment/executor/skill wording, regen prompt, drop asserts.

---

## Execution Log & Reasoning

**Mode:** Autopilot LOCKED per Manager order ("خودکار با Autopilot برین انجامش بدین"). No pauses except hard blockers.

**Seat Check:** domains = prompt-contract wording + regression asserts → Architect + Senior Programmer; skipped Designer (no UI surface), QA/Reviewer (later), Planner/Strategist (single task). Trigger map TITLE+BODY: explicit miss on all three sets; 2-seat consult by duty. Brainstorm: not required — reversible wording change.

**Brain plan verdict (REPORT):** tighten without widening — triggers + ownership + merge protocol; one executor lane; skill fix; bump + regen + pin + asserts; CHANGELOG; global sync with cmp. Selected path: executed verbatim; out-of-scope guardrails held (no new agents, no runtime blessings, no cap/QA changes).

**Implementation notes:** mandate appended (discovery wording intact), executor lane added beside discovery, skill one-word fix. Version `9.68.0` → `9.69.0`; regen deterministic (double-run byte-identical) and shipped byte-clean; executor sections confirmed absent from shipped prompt both before and after (plugin-blind split holds). Pin updated; 3 new asserts (mandate triggers, executor lane + no "`task` tool", skill reference). ADRs in fragments + agents DECISIONS; CHANGELOG entry. Global sync: executor, code-search skill, system-prompt (9.69.0 live) — all `cmp` identical.

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_prompt_sync.py tests/test_skill_registry.py -q
- **Expected result:** prompt-sync + skill-registry subsets green
- **Actual result:** `45 passed` (22 prompt-sync incl. 3 new asserts, 23 skill-registry); grep confirms zero "`task` tool" in executor and skill
- **Exit code:** 0

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
