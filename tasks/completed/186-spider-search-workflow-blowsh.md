# Task 186: Spider search workflow for blowsh skill

**File:** `tasks/completed/186-spider-search-workflow-blowsh.md`
**Source:** manager
**Type:** improvement
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `ea224cd52468ee1632febd5dc965c6d75abd0f48`
<!-- END_GIT_DIFF -->
