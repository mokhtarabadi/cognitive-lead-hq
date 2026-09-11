# Task 185: Spider-web deep research workflow — broad, branch, synthesize

**File:** `tasks/qa/185-spider-web-deep-research-workflow.md`
**Source:** manager
**Type:** feature
**Status:** in-progress

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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 375ab22..43a00e8 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -10,6 +10,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Spider-search workflow for blowsh skill (Task 186):** `skill-templates/blowsh/SKILL.md` gains a `Spider-Search Workflow` deep-research mode — plan (4–6 sub-questions mapped to queries) → sweep wide (`query_variants` + `intent`) → probe cheap (`must_contain`/`toc`/`map`) → read deep (`fetch_web_batch` + `focus`) → follow chains (`extract_links`, default 2 iterations) → cite everything. Loop rules: visited-URL set, budgets on every call, stop signals as results, `respect_robots`/`same_host` defaults. Grounded in researched best practices (deep-research survey pipeline, Firecrawl search→scrape→analyze→repeat, DeepWideSearch breadth-depth balance, NVIDIA planner/researcher phases, classic best-first focused crawling). Synced to global skills.
 - **Dogfood round (Task 186, same task):** Ran the new workflow on its own topic — plan (4 sub-questions) → parallel sweeps → probe → focused fetch of the LangChain deep-research doc → iteration-2 chain fetch. Folded 5 genuine deltas back into the skill: parallel sub-question sweeps (step 2), assess-after-each-search question (step 5), one citation number per unique URL + Sources list + sub-question coverage check (step 6), search budget 2–3 simple / 5 per branch complex + scale-matching rule (loop rules). Synced to global skills.
+- **Synthesis + saturation upgrade (Task 185):** Extended the spider workflow with step 7 (ranked-options synthesis: evidence with citation numbers, trade-offs, strong/medium/weak confidence grades, exactly one recommended winner) and explicit saturation stop-conditions in the loop rules (under ~10% novel facts per round, semantically repeated queries, or all sub-questions answered — budget caps demoted to backstop). Corroboration rules added to step 6 (2+ independent sources to establish a claim, primary-over-secondary weighting, explicit contradiction flagging). Grounded in tianpan.co deep-research convergence analysis (information-gain thresholds, query saturation, coverage checklists, budget backstops, multi-source corroboration). Synced to global skills.
 
 ## [9.16.0] - 2026-09-11
 
diff --git a/skill-templates/blowsh/SKILL.md b/skill-templates/blowsh/SKILL.md
index 463c0c0..79b9d24 100644
--- a/skill-templates/blowsh/SKILL.md
+++ b/skill-templates/blowsh/SKILL.md
@@ -114,15 +114,30 @@ and never visit a URL twice.
 6. **Cite everything.** Every claim in the final answer carries its
    source URL. Give each unique URL one citation number across the
    whole answer and end with a Sources list. No claim without a read
-   source. Before finishing, verify every sub-question from step 1 is
-   addressed.
+   source. Corroborate: a claim counts as established only when 2+
+   independent sources agree. Weight primary sources (official docs,
+   papers, announcements) above secondary ones (blogs, forums). When
+   sources contradict, flag the conflict explicitly instead of
+   silently picking one side. Before finishing, verify every
+   sub-question from step 1 is addressed.
+7. **Synthesize ranked options.** When the question asks for a decision
+   or recommendation, close with ranked options: each option gets its
+   supporting evidence (with citation numbers), its trade-offs, and a
+   confidence note (strong = 2+ primary sources agree, medium = one
+   primary or 2+ secondary, weak = single secondary source). Recommend
+   exactly one winner and say why it beats the rest.
 
 Loop rules: keep a visited-URL set, never fetch the same URL twice.
 Set `deadline_ms`/`deadline_s` on every call. Search budget: simple
 fact-finding gets 2–3 search calls, complex questions up to 5 per
 branch — then stop and answer with what you have. Match the scale to
 the question: a quick fact needs one search, a deep question gets the
-full loop. Stop on FrontierEmpty,
-MaxPages, CharBudget, or Deadline — a stop is a result, not a failure.
+full loop. Stop on saturation, not just on budget. Saturation means
+any of: (a) a full round yields under ~10% novel facts versus what
+you already know, (b) new queries come out semantically similar to
+ones already executed, (c) every sub-question from step 1 is
+answered. Budget caps (FrontierEmpty,
+MaxPages, CharBudget, Deadline) are the backstop, never the primary
+stop reason — a stop is a result, not a failure.
 `respect_robots` stays true. `same_host` stays true unless the question
 demands crossing domains.
```
<!-- END_GIT_DIFF -->
