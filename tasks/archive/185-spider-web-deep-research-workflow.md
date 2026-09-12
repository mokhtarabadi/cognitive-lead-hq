# Task 185: Spider-web deep research workflow — broad, branch, synthesize

**File:** `tasks/completed/185-spider-web-deep-research-workflow.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Replace shallow single-search research with an advanced spider-web workflow: broad initial sweep, source reading, clue-chained branching, synthesis into a supported answer.

## Manager's Notes

Manager requirement: make Workflow Research more advanced by incorporating deep-web-research best practices. It must be a workflow, not a simple search. Example: asked "find the best backend framework for AI applications," it should first run a broad initial search (general landscape, major options, key concepts), then read the relevant articles and sources, then keep researching from the clues found — additional sources, step by step and branch by branch, spider-web style — until it can name the best options with a well-supported answer. Research industry best practices for deep research loops (query fan-out, source triangulation, clue-chaining, saturation stop-conditions, evidence-graded synthesis) and encode them as a reusable workflow: either a new skill (e.g. deep-research) or executor guidance, reusing the blowsh tool chain (search → fetch/batch → crawl) already in the system. Must not degrade existing core performance.

## Local TODOs

- [x] Research deep-research best practices (fan-out, triangulation, chaining, saturation, synthesis)
- [x] Design the staged workflow (broad sweep → read → branch → synthesize) with stop conditions
- [x] Encode as skill or executor guidance using blowsh tools
- [x] Verify no regression to existing research behavior or core performance

## Acceptance Criteria

- [x] Documented staged workflow exists (broad → read → branch → synthesize)
- [x] Clue-chaining and saturation stop-conditions defined (no endless crawling)
- [x] Synthesis outputs ranked options with supporting evidence
- [x] Built on blowsh chain; existing core behavior intact

## Verification Evidence

- **Test command:** `ls skill-templates/ | grep -i research; grep -rn -i "saturation\|fan-out\|fanout" skill-templates/ agents/cognitive-executor.md prompts/fragments/ | head`
- **Expected result:** workflow present with stages and stop-conditions
- **Actual result:** `saturation` hits in skill-templates/blowsh/SKILL.md (stop-conditions + coverage checklist); ranked-options synthesis step 7 present; global skill in sync (SYNC_OK)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Unbounded branching burns tokens/time on low-value sources.
- **Rollback plan:** Remove skill or revert guidance from git history; blowsh chain unchanged.

---

## Execution Log & Reasoning

Task 186 had already built the spider-search base (steps 1–6 + loop rules) on the blowsh chain, so 185 was implemented as an upgrade, not a new skill — zero new surface, zero regression risk.

Researched convergence + credibility patterns (tianpan.co deep-research convergence analysis, 2026-04-12: information-gain thresholds, query saturation, coverage checklists, budget backstops, multi-source corroboration, source-type weighting, contradiction flagging). Ran the workflow itself to find them (plan → parallel sweeps → focused fetch).

Changes to `skill-templates/blowsh/SKILL.md`:
1. Step 6 extended with corroboration rules (2+ independent sources to establish a claim, primary-over-secondary weighting, explicit contradiction flagging).
2. New step 7: ranked-options synthesis (evidence + citation numbers, trade-offs, strong/medium/weak confidence grades, exactly one recommended winner).
3. Loop rules: explicit saturation stop-conditions (under ~10% novel facts per round, semantically repeated queries, all sub-questions answered); budget caps demoted to backstop.

Synced to global skills (SYNC_OK). CHANGELOG Unreleased entry added. No `.py`, prompt, or executor changes — core behavior intact.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `4f5f3ead2bb73722ef6a1eefeef78f463f991157`
<!-- END_GIT_DIFF -->
