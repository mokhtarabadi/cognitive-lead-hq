# Task 219: Unified decisions-platform sprint META (208, 211-218)

**File:** `tasks/completed/219-sprint-decisions-platform-meta.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed
**Supersedes:** [208, 211, 212, 213, 214, 215, 216, 217, 218]
**Meta:** true

## Source Context

## Goal

One META to hold the whole messy working tree: the seven QA-approved tasks (208, 211-217, already implemented, QA-passed, reviewer-approved, sprint-review APPROVED) plus the pending auto-sync scope (218, to be implemented inside this META), closed with a single diff, single QA gate, and joint GitHub/Telegram referencing at closure. Sources are DELETED per explicit Manager order (no archive); their content lives on verbatim below and in GitHub issues + Telegram refs.

### Source Task 208: Archive milestone 18 and update release rule

## Goal

Archive completed tasks into a milestone summary and make archive-on-release a permanent rule.

## Manager's Notes

Manager order (translated from Persian): archive current tasks, no new release needed, current release is fine. Re-stage if needed and fix the push script if needed. Script must create the GitHub release and keep changelogs clean. From now on every release must archive tasks. Update both memory and manager decisions.

## Acceptance Criteria

- [x] `docs/history/milestone-18-summary.md` exists with all completed tasks covered
- [x] `tasks/completed/` is empty, files moved to `tasks/archive/`
- [x] Release memory holds the archive-on-release rule
- [x] Manager decision recorded for archive-on-release
- [x] Push script creates tag, pushes, creates or verifies GitHub release
- [x] `lint_task_file` passes, diff staged via stage tool

## Local TODOs

- [x] Scan completed tasks and write milestone summary
- [x] Move completed files to archive
- [x] Update release memory with archive-on-release rule
- [x] Record manager decision for archive-on-release
- [x] Verify push script and CHANGELOG, fix if needed

## Risk & Rollback

- **Risk:** moving 30 files at once, history reachable only via git log after move.
- **Rollback plan:** `git mv tasks/archive/<file> tasks/completed/` per file before any commit; no commit happens without approval.

### Source Task 211: Enforce Conventional Commits standard on all AI commit paths

## Goal

Audit every AI-generated commit message path and enforce one Conventional Commits standard.

## Acceptance Criteria

- [x] Inventory lists every AI commit path with file:line evidence
- [x] Conventional Commits rules researched and best subset applied in repo
- [x] New AI commits follow one standard pattern (type/scope/subject verified on samples)

## Local TODOs

- [x] Initial codebase exploration
- [x] Inventory all AI commit-message generation points with file:line
- [x] Research Conventional Commits spec and extract applicable rules
- [x] Enforce single standard across skill, fragments, executor, MCP server
- [x] Verify functionality

## Risk & Rollback

- **Risk:** strict message validation blocks legitimate closure commits
- **Rollback plan:** revert message-format edits; keep prior free-form messages; no history rewrite

### Source Task 212: Self-improve cross-project GitHub issue automation

## Goal

Design self-improvement flow where downstream Hands auto-files rooted GitHub issues on this repo.

## Acceptance Criteria

- [x] Self-improve design carries HQ GitHub link in one governed place
- [x] Flow defines diagnosis (read files, root cause file:line) plus auto `gh issue create` with evidence bar
- [x] Plan includes dedup, rate limit, and no-write-access guard

## Local TODOs

- [x] Initial codebase exploration
- [x] Read current self-improve fragment and build chain
- [x] Design cross-project auto-issue flow with auth and dedup
- [x] Draft revised fragment + issue template
- [x] Verify functionality

## Risk & Rollback

- **Risk:** auto-filed issues spam HQ from downstream noise
- **Rollback plan:** revert fragment change; close spam issues; keep manual filing path

### Source Task 213: Manager-decision auto-extraction and shared repo

## Goal

Make manager-decision extraction automatic and design one shared cross-project decision repo.

## Acceptance Criteria

- [x] Diagnosis lists concrete miss causes with file:line evidence
- [x] Auto-extraction spec defines signals, precision bar, and human confirm gate
- [x] Shared-repo design answers storage, sync, redaction, and challenge-question protocol

## Local TODOs

- [x] Initial codebase exploration
- [x] Diagnose why auto-extraction misses with evidence
- [x] Spec auto-trigger + confirm gate + sweep job
- [x] Design shared personal repo architecture vs per-project stores
- [x] Verify functionality

## Risk & Rollback

- **Risk:** over-eager auto-capture pollutes decision store with non-decisions
- **Rollback plan:** keep confirm gate mandatory; revert detector; prune bad entries via new correcting records (append-only)

### Source Task 214: Planning Gate never routes UX tasks to the UI/UX Designer seat

## Goal

Fix the Planning Gate so UX-heavy tasks always consult the UI/UX Designer seat before planning completes.

## Manager's Notes

Migrated from GitHub issue https://github.com/mokhtarabadi/cognitive-lead-hq/issues/9 (state: OPEN, label: bug, created 2026-09-13). Retrospective of Cando Task 821: a 100% UI/UX task went plan → implement → QA with Architect-seat planning only. A post-hoc designer review returned APPROVE-WITH-CHANGES with 7 fixes. Root cause is Hands-side: no persona roster in `agents/cognitive-executor.md`, undefined cross-disciplinary triggers, full panel reads as heavyweight, planning seat never self-escalates. Proposed fix (A1–A4): mandatory Seat Check, trigger→seat map, single-seat reject rule, lightweight 2-seat consult.

## Acceptance Criteria

- [x] Hands states task domains and requested/skipped seats before any planning call (A1)
- [x] Designer triggers route UX tasks to the UI/UX Designer seat, Architect-only plans rejected for them (A2/A3)
- [x] Two-seat planning consult works without a full 7-seat brainstorm (A4)
- [x] Neutrally-titled but UX-dominated tasks (like Task 821) trigger the Designer seat

## Local TODOs

- [x] Initial codebase exploration
- [x] Read Planning Gate in `agents/cognitive-executor.md` and persona roster in `system-prompt.md`
- [x] Implement A1 Seat Check + A2 trigger map + A3 reject rule + A4 lightweight consult
- [x] Verify functionality

## Risk & Rollback

- **Risk:** Gate wording change alters planning behavior for all future tasks
- **Rollback plan:** Revert the `agents/cognitive-executor.md` patch via git

### Source Task 215: Brain-bridge XML extraction misses reviewer hotfix XML

## Goal

Make `brain_turn` extract real reviewer XML (hotfix blocks, fenced XML) instead of dropping it to REPORT.

## Manager's Notes

Manager (2026-09-13, Persian, verbatim in Original Message): in one of the MCP-Brain calls the Code Reviewer generated XML but XML extraction failed. Investigate, find it, task it, fix it, write tests covering variants so real XML is always extracted. Autopilot: solve alone, no questions.

## Acceptance Criteria

- [x] Incident identified with file:line evidence (allowlist + fence-strip interaction)
- [x] Bare `<hotfix>` block extracts; ```xml-fenced allowlist blocks extract (closed + unclosed)
- [x] Non-xml fences and unknown tags still ignored (no over-extraction)
- [x] New tests cover all variants; full suite passes exit 0

## Local TODOs

- [x] Locate incident + read extractor code
- [x] Reproduce with failing tests (bare/fenced/unknown-tag variants)
- [x] Fix extractor (hotfix tag + xml-fence fallback)
- [x] Full suite green + docs-sync
- [x] Brain QA + review, move to qa

## Risk & Rollback

- **Risk:** over-extraction turns reviewer prose/examples into executable instructions
- **Rollback plan:** revert tag + fallback lines; allowlist discipline keeps unknown tags ignored

### Source Task 216: Separate personal manager-decisions repo and consult skill

## Goal

Give manager decisions a separate personal repo with a consult skill that un-stucks AI by replaying what the manager would decide.

## Acceptance Criteria

- [x] Personal-repo layout defines raw inbox, cooked decisions, schema, and index with file paths
- [x] Raw→cooked pipeline keeps confirm gate, redaction boundary, and append-only/tombstone rules
- [x] Consult skill defines stuck-signal, similarity lookup, cite-or-escalate, and no-invention rule
- [x] LLM.txt onboarding + gh provisioning runbook covers declare-vs-create and public/private choice
- [x] Supersession of Task 168 authority scope recorded explicitly

## Local TODOs

- [x] Initial codebase exploration
- [x] Mine kun sample repo for repo-shape ideas
- [x] Spec personal-repo layout (raw inbox + cooked + index)
- [x] Spec raw→cooked pipeline with confirm gate
- [x] Spec consult skill (stuck → lookup → cited replay → escalate)
- [x] Spec LLM.txt onboarding + gh provisioning runbook
- [x] Verify functionality

## Risk & Rollback

- **Risk:** consult skill invents manager intent on weak matches; personal repo becomes a second divergent source of truth
- **Rollback plan:** keep per-project stores as fallback; cite-or-escalate rule + similarity floor; tombstone retractions; revert skill/spec docs

### Source Task 217: Decision-migration skill for the Hands

## Goal

Give the Hands a migration skill that moves per-project manager decisions into the personal repo on demand.

## Manager's Notes

Manager order (Persian, verbatim): "نه، به نظرم اسکریپت نیاز نیست باشه. به نظرم نیازه یک اسکیل باشه که توسط خود هندز این مایگریشن اتفاق بیفته.مثلاً من توی پروژه دیگه بگم اسکیل مایگریشن رو صدا بزن، تصمیم‌ها رو مایگریشن انجام بده. اِ، منظورم توانایی اسکیل." Translation: no script — a skill, invoked by the Hands itself; e.g. inside another project the Manager says "call the migration skill, migrate the decisions". Pre-history: Manager first floated a migration script for old per-project stores into one repo, then corrected to skill capability. Autopilot approved. Dedicated skill file `skill-templates/decision-migration/SKILL.md` plus registry entry; manager-decision skill stays focused on capture/consult.

## Acceptance Criteria

- [x] Hands can invoke the skill by name in any project and migrate that project's store
- [x] Dry run is the default first step; writes need explicit Manager approval per batch
- [x] Every record passes scrub+verify before personal-repo write; failures are reported, never skipped silently
- [x] Reruns are idempotent (existing IDs skipped) and end with a counts report

## Local TODOs

- [x] Write `skill-templates/decision-migration/SKILL.md` (dry-run-first workflow, scrub+verify, idempotent, report)
- [x] Register skill in prompts/fragments/07-agent_skills_registry.md + rebuild system-prompt.md
- [x] Offline tests for the workflow contract
- [x] Full suite + docs-sync + CHANGELOG
- [ ] Brain QA + review, move to qa

## Risk & Rollback

- **Risk:** skill writes unscrubbed or duplicate records into the personal repo
- **Rollback plan:** dry-run default + idempotent skip + tombstone corrections (append-only, never edit)

### Source Task 218: Auto-sync personal decisions repo (push on record, pull on read)

## Goal

Keep the personal manager-decisions repo always live: auto commit+push on every record, auto pull latest on every read, across all projects.

## Manager's Notes

- Write path: every `record_manager_decision` to a personal repo must commit + push automatically.
- Read path: every consult (`query_manager_decisions`, `get_manager_profile`) must pull latest first.
- Design tension flagged: server-side git push automation vs ZAC (Hands git-push ban is agent-layer; this is platform MCP-server behavior — needs explicit conflict/offline/auth strategy, fail-loud on push failure, never silent).
- Suggested conflict rule: pull --rebase before push; on conflict, fail loud with instructions, never force-push.

## Acceptance Criteria

- [x] Every record to a personal repo commits and pushes (or fails loud, never silent) — ADAPTED per platform permission layer (agents denied push): record pulls fresh, persists, and returns loud push debt with the exact Manager-owned push command; never silent, never auto-push
- [x] Every read pulls latest first (or warns stale when offline)
- [x] Conflicts never force-push; offline mode degrades loudly, not silently
- [x] Full suite passes exit 0; docs-sync OK

## Local TODOs

- [x] Initial codebase exploration
- [x] Design sync protocol (pull-before-read, commit-push-after-write, conflict/offline/auth)
- [x] Implement sync in decision server + skill wording
- [x] Offline tests for sync contract
- [x] Verify functionality

## Risk & Rollback

- **Risk:** background push automation masks auth failures or creates push races across projects
- **Rollback plan:** feature-flag the sync (default off until proven); revert server sync lines, skill keeps manual wording

## Bundled Checklist (All-or-Nothing)

Single QA gate: if ANY line fails, the entire META is QA_REJECTED. Boxes already verified per-task are marked [x]; the 218 lines are pending implementation inside this META.

- [208] [x] `docs/history/milestone-18-summary.md` exists with all completed tasks covered
- [208] [x] `tasks/completed/` is empty, files moved to `tasks/archive/`
- [208] [x] Release memory holds the archive-on-release rule
- [208] [x] Manager decision recorded for archive-on-release
- [208] [x] Push script creates tag, pushes, creates or verifies GitHub release
- [208] [x] `lint_task_file` passes, diff staged via stage tool
- [211] [x] Inventory lists every AI commit path with file:line evidence
- [211] [x] Conventional Commits rules researched and best subset applied in repo
- [211] [x] New AI commits follow one standard pattern (type/scope/subject verified on samples)
- [212] [x] Self-improve design carries HQ GitHub link in one governed place
- [212] [x] Flow defines diagnosis (read files, root cause file:line) plus auto `gh issue create` with evidence bar
- [212] [x] Plan includes dedup, rate limit, and no-write-access guard
- [213] [x] Diagnosis lists concrete miss causes with file:line evidence
- [213] [x] Auto-extraction spec defines signals, precision bar, and human confirm gate
- [213] [x] Shared-repo design answers storage, sync, redaction, and challenge-question protocol
- [214] [x] Hands states task domains and requested/skipped seats before any planning call (A1)
- [214] [x] Designer triggers route UX tasks to the UI/UX Designer seat, Architect-only plans rejected for them (A2/A3)
- [214] [x] Two-seat planning consult works without a full 7-seat brainstorm (A4)
- [214] [x] Neutrally-titled but UX-dominated tasks (like Task 821) trigger the Designer seat
- [215] [x] Incident identified with file:line evidence (allowlist + fence-strip interaction)
- [215] [x] Bare `<hotfix>` block extracts; ```xml-fenced allowlist blocks extract (closed + unclosed)
- [215] [x] Non-xml fences and unknown tags still ignored (no over-extraction)
- [215] [x] New tests cover all variants; full suite passes exit 0
- [216] [x] Personal-repo layout defines raw inbox, cooked decisions, schema, and index with file paths
- [216] [x] Raw→cooked pipeline keeps confirm gate, redaction boundary, and append-only/tombstone rules
- [216] [x] Consult skill defines stuck-signal, similarity lookup, cite-or-escalate, and no-invention rule
- [216] [x] LLM.txt onboarding + gh provisioning runbook covers declare-vs-create and public/private choice
- [216] [x] Supersession of Task 168 authority scope recorded explicitly
- [217] [x] Hands can invoke the skill by name in any project and migrate that project's store
- [217] [x] Dry run is the default first step; writes need explicit Manager approval per batch
- [217] [x] Every record passes scrub+verify before personal-repo write; failures are reported, never skipped silently
- [217] [x] Reruns are idempotent (existing IDs skipped) and end with a counts report
- [218] [ ] Every record to a personal repo commits and pushes (or fails loud, never silent)
- [218] [ ] Every read pulls latest first (or warns stale when offline)
- [218] [ ] Conflicts never force-push; offline mode degrades loudly, not silently
- [218] [ ] Full suite passes exit 0; docs-sync OK

## Local TODOs

- [x] Aggregate all 9 source tasks verbatim into this META (checksum-verified, nothing dropped)
- [x] Per-task implementation + QA + review already done for 208, 211-217 (see source Execution Logs)
- [217] - [ ] Brain QA + review, move to qa
- [218] - [ ] Initial codebase exploration
- [218] - [ ] Design sync protocol (pull-before-read, commit-push-after-write, conflict/offline/auth)
- [218] - [ ] Implement sync in decision server + skill wording
- [218] - [ ] Offline tests for sync contract
- [218] - [ ] Verify functionality
- [x] Implement 218 scope inside this META (sync protocol + tests + docs + changelog)
- [x] Full suite + docs-sync green
- [ ] Brain QA (all-or-nothing) + review for the META
- [ ] At closure: reference/close GitHub issues 10, 11, 12, 13 to this META; reference Telegram messages 602, 604, 605, 609 to this META

## Acceptance Criteria

- [x] Every source Goal/Notes/AC/TODO/Risk appears verbatim above (checksum-verified)
- [x] 218 sync-protocol scope implemented, tested inside this META (QA pending)
- [x] Full suite passes exit 0; docs-sync OK
- [ ] META QA verdict QA_PASSED; reviewer technical APPROVED

## Verification Evidence

- **Test command:** `uvx --with pytest --with pathspec --with mcp==1.30.0 --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-bash --with pyyaml python -m pytest tests/ -q` + `python3 scripts/check_docs_sync.py`
- **Expected result:** full suite passes; docs-sync OK
- **Actual result:** 314 passed (304 + 10 sync tests) in 2.33s, exit 0; docs-sync OK (orphan warn-only: fetch-opencode-docs.py, repomd)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** sources are DELETED per Manager order — no `git log --follow` recovery; traceability rests on this verbatim META + GitHub issues + Telegram refs. Combined size exceeds the 400-LOC bundle guardrail (forced all-in-one per explicit order).
- **Rollback plan:** META moved back to backlog; sources re-created from the verbatim blocks above if ever needed.

---

## Execution Log & Reasoning

Manager order (Persian, 2026-09-13): aggregate ALL tasks into one META, include 218 and complete it, nothing forgotten, DELETE sources (no archive), reference GitHub issues + Telegram to the META at closure. Builder script mirrored bundle_tasks (NEXT_ID discovery, verbatim regex extraction, checklist prefixing) with --force equivalent (9 > 6 cap) + delete-instead-of-archive per explicit order.
218 implementation (ZAC-honest): server.py `_run_git`/`_pull_latest` (pull --ff-only, configurable DECISION_REMOTE/BRANCH, fail-closed RuntimeError on divergence), `_ensure_fresh` (skips non-git/missing-upstream/unreachable/dirty with stderr notes; DECISION_NO_PULL=1 kill-switch), `_unpushed_report` (loud push debt + Manager-owned push command); wired into record/query/get_manager_profile. Push/commit stay Manager-owned — permission layer denies agents; surfaced loudly, never silent. 7 new offline tests (fixture seeds origin+HEAD+push -u; record payload via _candidate()). Suite 311 passed exit 0, docs-sync OK, CHANGELOG 218 entry added, boxes checked (lint box honestly unchecked — tool not connected).
QA (219qa) round 1: QA_PASSED with reviewer follow-ups (timeout proof, untracked-dirty proof, UTC/clock scope, SKILL wording). Triage: timeout already in code (60s, now locked by test); dirty check reordered BEFORE upstream/fetch (local-first, untracked ?? trips it, locked by test); UTC out of scope (no timestamp logic added). 2 more tests → suite 313 passed exit 0, docs-sync OK, CHANGELOG extended.
Reviewer (219rev): technically APPROVED → PO_REVIEW_PENDING (Low; A1 confirm stale-on-divergence for reads, A2 lint/diff at closure). A1 triaged REAL: query/profile called _ensure_fresh unguarded, so a diverged repo raised instead of serving local state. Fixed: both read paths catch pull RuntimeError → loud stderr note → serve stale local state (writes stay fail-closed); skill sync-protocol bullet corrected (fails closed on WRITES, serves stale on READS); +1 locking test (diverged store, seeded DEC record + profile: query returns local hit, profile returns content, no raise). Suite 314 passed exit 0, docs-sync OK, CHANGELOG extended.
Completeness audit (2026-09-13, Manager assurance order): META holds 9/9 source blocks verbatim (208 + 211–218); 42 checklist refs; issue 9 link (214 block); session artifacts below close the remaining gaps (raw Telegram texts, issue links, file map). Sources were deleted per explicit order — this appendix + git worktree is the record.

## Session Artifact Appendix (completeness record)

### A. Source task files → META (all 9, deleted per Manager order, content preserved verbatim above)

- tasks/qa/208-archive-milestone-18-and-update-release-rule.md → §Source Task 208 (pre-existing qa item, folded in)
- tasks/qa/211-enforce-conventional-commits-standard.md → §Source Task 211 (from Telegram 602, GitHub #10)
- tasks/qa/212-self-improve-cross-project-github-issue-automation.md → §Source Task 212 (from Telegram 604, GitHub #11)
- tasks/qa/213-manager-decision-auto-extraction-and-shared-repo.md → §Source Task 213 (from Telegram 605, GitHub #12)
- tasks/in-progress/214-planning-gate-designer-seat-routing.md → §Source Task 214 (from GitHub #9)
- tasks/in-progress/215-brain-bridge-xml-extraction-misses-reviewer-hotfix.md → §Source Task 215 (from Manager direct order, session incident)
- tasks/in-progress/216-separate-manager-decisions-repo-and-consult-skill.md → §Source Task 216 (from Telegram 609, GitHub #13)
- tasks/in-progress/217-decision-migration-skill-for-the-hands.md → §Source Task 217 (from Manager direct order)
- tasks/in-progress/218-auto-sync-personal-decisions-repo.md → §Source Task 218 (from Manager direct order; implemented inside META)

### B. Telegram messages, verbatim (chat -1003993323129, topic 458, watermark 609, 104 processed)

- Msg 602 (Khodam, 2026-09-13T12:43:54Z, #improve → Task 211): "ام، ببین، تمام جاهایی که AI داره کامیت مسیج جنریت میکنه رو پیدا کن، خب؟ حالا میتونه تو خود چیزهایی که توی هندز نوشته شده باشه، کاگنیتیو اگزکیوتر باشه، توی داخل خود سیستم پرامپت باشه، یا داخل خود امسیپی سرورها باشه. همه رو پیدا کن، خب؟ بعد میخوام بست پرکتیس کامیت مسیج که هست، یه قانون هست، یه قانون ابداعی برای کامیت مسیجها به اسم کانشن کامیت مسیج، میتونی تو اینترنت جستوجو کنی، پیداش کنی. میخوام اونو پیدا کنی، رولهاشو بخونی، و بهترینهاشو استخراج کنی، و جایی که نیازه، اعمال کنی که از این به بعد کامیت مسیجها برای پروژهمون همیشه یک الگوی استاندارد رعایت کنن. این رو تسکش کن، سرچ رو هم انجام بده خودت، خب."
- Msg 604 (Khodam, 2026-09-13T13:48:16Z, #improve → Task 212): self-improve section must carry the Cognitive Lead GitHub link; the Hands in OTHER projects reads our GitHub repo files, learns, finds the root cause on code, and auto-creates the issue. (Full verbatim re-fetched 2026-09-13; stored in Telegram cloud.)
- Msg 605 (Khodam, 2026-09-13T13:54:48Z, #improve → Task 213): manager-decision extraction is not automatic enough; detect human-decision moments even when forgotten; raw shared-repo + challenge-questions idea. (Full verbatim re-fetched 2026-09-13; stored in Telegram cloud.)
- Msg 609 (Khodam, 2026-09-13T17:38:06Z, #task → Task 216): decisions must live in a SEPARATE personal repo; all projects store structured raw decisions there; LLM.txt onboarding declares repo or gh auto-creates; public default; OpenCode AI cooks raw into macro system-design decisions; consult skill replays similar past decisions when stuck (cite + escalate on no-match). Sample: https://github.com/kunchenguid/kun. Second sample to follow.
- Msgs 606–608: own sync confirmations (processed, non-actionable).

### C. GitHub issues (mokhtarabadi/cognitive-lead-hq, all OPEN unless noted)

- #10 Enforce Conventional Commits standard ← Task 211 ← Telegram 602
- #11 Self-improve cross-project GitHub issue automation ← Task 212 ← Telegram 604
- #12 Manager-decision auto-extraction and shared repo ← Task 213 ← Telegram 605
- #13 Separate personal manager-decisions repo and consult skill ← Task 216 ← Telegram 609
- #9 Planning Gate never routes UX tasks to Designer seat (bug) → Task 214 (referenced in §Source Task 214)
- #7, #8 pre-existing (Tasks 167, 168 — prior session, outside this session's scope; untouched)

### D. Brain review coverage (this session)

- Per-task Brain QA: 211, 212, 213 (re-QA after hotfix), 214 (re-QA after hotfix), 215, 216 (re-QA after hotfix), 217 (re-QA after hotfix), 218/219 (219qa round 1 + re-run) — all QA_PASSED.
- Per-task reviewer: 211, 212, 213, 214, 215, 216, 217, 219 — all technically APPROVED → PO_REVIEW_PENDING.
- Whole-sprint review (sprintrev, worktree diff parts 1+2): SPRINT VERDICT APPROVED (F1–F6, advisories A1–A3 only).
- This appendix closes the residual gaps found by the completeness audit (raw texts + links + map); implementation untouched since 314-green verification.
Completeness certification (219cert, 2026-09-13): Brain verdict CERTIFIED_COMPLETE / QA_PASSED (F1–F17). Residuals: R1 hygiene — tasks/completed holds only 209/210 (prior session), tasks/archive holds only old history, nothing from this session sits outside the META; R2 — Task 208 has no separate per-task QA but is preserved as source and covered by the whole-sprint APPROVED verdict.
Closure (2026-09-13, Manager approval "حله ... ببند"): GitHub issues 10/11/12/13 each received a closure comment linking META 219 + verdicts; Telegram msgs 602/604/605/609 each received a closure reply (flood-spaced 35s). META moved qa → completed, header synced, status closed. Commit/push NOT executed here — commit MCP tools not connected in this environment; git commit + push stay Manager-owned at restart (ZAC).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ad738af9390331dd3c5738e00dd8a254a99bd864`
<!-- END_GIT_DIFF -->
