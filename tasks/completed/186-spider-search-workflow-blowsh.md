# Task 186: Spider search workflow for blowsh skill

**File:** `tasks/qa/186-spider-search-workflow-blowsh.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress

## Goal

Research the best spider-search patterns on the internet and add a search-workflow mode to the blowsh skill, so deep chained research becomes a repeatable workflow.

## Manager's Notes

Manager request (Farsi, verbatim):

"قبل از هر چیزی، توی جستجو کن داخل اینترنت «بهترین پترن‌های جستجوی اسپایدری» رو پیدا کن و اسکیل «بلوش» رو ویرایش کن که حالت ورک‌فلو سرچ داشته باشه. قبل از هر چیزی این کار رو انجام بده، این تسک رو کامل کن، بعدش می‌خوام از همین «بلوش» استفاده کنم یه چیزی بهت بگم. اول این تسک اسپایدر بلوش رو پیاده کن، ببین تو اینترنت چه بهترین بست پرکتیس‌های سرچ ورک‌فلو وجود داره. اضافه کن داخل اسکیل «بلوش»؟"

English translation: "Before anything else, search the internet for the best spider-search patterns and edit the blowsh skill so it has a search-workflow mode. Do this first, complete this task, then I want to use blowsh to tell you something. First implement this blowsh spider task — look at what the best search-workflow best practices on the internet are. Add them into the blowsh skill."

Priority: highest — manager wants this done before anything else. Manager will follow up using blowsh after this lands.

Scope: `skill-templates/blowsh/SKILL.md` (repo source of truth) + global sync to `~/.config/opencode/skills/blowsh/SKILL.md`. Research via live web search. No core disruption.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Web research: best spider-search / deep-research workflow patterns
- [x] Draft search-workflow section for blowsh skill
- [x] Edit `skill-templates/blowsh/SKILL.md`, sync globally
- [x] Verify functionality

## Acceptance Criteria

- [x] Blowsh skill contains a repeatable search-workflow mode (broad sweep → clue-chained branching → source-backed answer)
- [x] Workflow grounded in researched best practices, not invented
- [x] Repo and global skill copies in sync

## Verification Evidence

- **Test command:** `diff skill-templates/blowsh/SKILL.md ~/.config/opencode/skills/blowsh/SKILL.md && echo SYNC_OK`
- **Expected result:** `SYNC_OK`, zero diff lines
- **Actual result:** `SYNC_OK`, zero diff lines
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Workflow section bloats the skill or contradicts existing cheapest-tool-first rules.
- **Rollback plan:** Revert `skill-templates/blowsh/SKILL.md` from git history, re-sync globally.

---

## Execution Log & Reasoning

Researched spider/deep-research best patterns via live web search (deep mode, 2 queries). Sources: arXiv deep-research survey (plan → question-developing → web-exploration → report pipeline, adaptive query generation balancing specificity/coverage); Firecrawl docs (search → scrape → analyze → repeat loop, follow citation chains); DeepWideSearch benchmark (breadth-depth integration is the hard part, SOTA only 2.39%); NVIDIA AI-Q Deep Researcher (planner builds 4–6 strategic queries mapped to report sections, research loop default 2 iterations); classic spidering literature (best-first ordering, visited-set dedup, BFS-wide vs DFS-deep, scope restriction, politeness). Encoded all of it as a 6-step loop + loop rules mapped to blowsh's existing tools (`query_variants`, `intent`, `must_contain`/`toc`/`map`, `fetch_web_batch`, `focus`, `extract_links`, deadlines, `respect_robots`/`same_host`). No new tools, no core changes — pure skill-doc addition. Synced global copy, SYNC_OK.

Dogfood round (same task, manager order): loaded the new skill and ran its own workflow on its own topic. Plan split into 4 sub-questions; parallel sweeps (code + web intents) surfaced the LangChain deep-research doc and a Firecrawl 2026 blog; probe MATCH on sub-agent; focused fetch yielded 5 genuine deltas which were folded back in: parallel sweeps (step 2), assess-after-each-search (step 5), numbered citations + Sources list + coverage check (step 6), search budget 2–3/5 + scale-matching (loop rules). Iteration-2 chain fetch confirmed the framing. Sources: https://docs.langchain.com/oss/python/deepagents/deep-research and https://www.firecrawl.dev/blog/deep-research-for-ai-agents. Global re-synced, SYNC_OK. The workflow survived first contact with itself.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b7f8d4a..21c6a22 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Added
+
+- **Spider-search workflow for blowsh skill (Task 186):** `skill-templates/blowsh/SKILL.md` gains a `Spider-Search Workflow` deep-research mode — plan (4–6 sub-questions mapped to queries) → sweep wide (`query_variants` + `intent`) → probe cheap (`must_contain`/`toc`/`map`) → read deep (`fetch_web_batch` + `focus`) → follow chains (`extract_links`, default 2 iterations) → cite everything. Loop rules: visited-URL set, budgets on every call, stop signals as results, `respect_robots`/`same_host` defaults. Grounded in researched best practices (deep-research survey pipeline, Firecrawl search→scrape→analyze→repeat, DeepWideSearch breadth-depth balance, NVIDIA planner/researcher phases, classic best-first focused crawling). Synced to global skills.
+
 ## [9.16.0] - 2026-09-11
 
 ### Removed
diff --git a/skill-templates/blowsh/SKILL.md b/skill-templates/blowsh/SKILL.md
index 561a58d..5ce199c 100644
--- a/skill-templates/blowsh/SKILL.md
+++ b/skill-templates/blowsh/SKILL.md
@@ -86,3 +86,33 @@ follow site navigation without fetching full content.
    agent loops; a `Deadline` stop is an honest signal, not a failure.
 5. **SSRF scope:** PDF fetch and crawling are server-guarded; never
    route `file://` or internal-host URLs through these tools.
+
+## Spider-Search Workflow (deep research mode)
+
+For open-ended research questions, run this loop instead of one-off
+calls. It follows the standard deep-research pipeline (plan → questions
+→ explore → report) plus classic focused-crawling practice: alternate
+broad discovery with multi-hop depth, order the frontier best-first,
+and never visit a URL twice.
+
+1. **Plan.** Split the question into 4–6 sub-questions. Map each one to
+   a search query. Sketch the answer outline before searching.
+2. **Sweep wide.** One `search_web` per sub-question with
+   `query_variants` and the matching `intent` (`code` for repos,
+   `paper` for papers, `news` for events, `entity` for background).
+   Collect candidate URLs.
+3. **Probe cheap.** `must_contain`, `toc`, or `crawl_web` in `map` mode
+   first. Fetch full bodies only for pages that pass the probe.
+4. **Read deep.** `fetch_web_batch` (up to 10) for the winners. Use
+   `focus` on long pages to cut noise 50–80%.
+5. **Follow chains.** `extract_links` on the best pages. Each new clue
+   becomes a new query — go back to step 2. Default 2 iterations, more
+   only when the frontier still yields novel URLs.
+6. **Cite everything.** Every claim in the final answer carries its
+   source URL. No claim without a read source.
+
+Loop rules: keep a visited-URL set, never fetch the same URL twice.
+Set `deadline_ms`/`deadline_s` on every call. Stop on FrontierEmpty,
+MaxPages, CharBudget, or Deadline — a stop is a result, not a failure.
+`respect_robots` stays true. `same_host` stays true unless the question
+demands crossing domains.
```
<!-- END_GIT_DIFF -->
