# Task 230: Manager-decision improvements synced with issue 8

**File:** `tasks/completed/230-manager-decision-improvements-sync-with-issue-8.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Sync the local task with GitHub issue 8 and implement the manager-decision improvements: fixed save path, automatic capture on close, and a working manager profile.

## Manager's Notes

Direct order (Persian, verbatim, message 1):

ببین یک تسک داریم که تسکش اینه، می‌خوایم تصمیمات منیجر رو بهبود ببخشیم. یه ایشوی گیت‌هاب داره. یکی از دوستان اومده توی کامنت‌های ایشوی گیت‌هاب یه سری چیزها نوشته، اون‌ها رو برو بخون. بعد به فایل تسک خودمون اضافه‌ش کن. هر چیزی که هسته. فایل تسک دقیقاً سینک شده با ایشوی گیت‌هاب باشه. مورد بعدی اینه که خودم هم دو تا باگ دیدم. هر بار که اسکیل رو صدا می‌زنم، تصمیمات منیجر رو بنویسه، ازم مسیر می‌پرسه. این باید یک بار یه جا نوشته بشه واقعاً. وقتی توی نصب سیستم داره اتفاق می‌افته و توی اسکیله، باشه. نمی‌دونم یه جایی باشه که هر بار نپرسه. بعد ذخیره تصمیمات مدیر هیچ‌وقت خودکار نیست، یعنی بعد از اسپرینت بسته می‌شه، بعد از یک تسک بسته می‌شه. باید همیشه خودکار تصمیمات ذخیره بشه. مثلاً توی کاگنیتیو اگزکیوتر می‌تونه باشه یا توی خود سیستم پرامپت باشه که وقتی یه تسک بسته می‌شه با موفقیت، حالا تصمیمات اون تسک هم ذخیره بشه، یعنی سیستم همیشه کار کنه. و بخش پروفایل منیجر هنوز کامل نشده، رو اون هم باید کار کنیم که یه پروفایل دقیق از تصمیمات منیجر بسازیم که سیستم یه روزی بتونه واقعاً بدون حضور منیجر هم تسک بزنه. این چیزها که همه رو گفتم استپ به استپ انجام بده. فایل تسک رو کامل و کامل کن، گیت‌هاب فایل تسک سینک بشه و چیزهایی که بهت گفتم رو انجام بده. کاملاً.

Direct order (Persian, verbatim, message 2):

یعنی ما تسکی برای این ایشوی گیت‌هاب نداریم؟ اگر تسکی توی بک‌لاگ نداریم که روی این ایشوی گیت‌هاب باشه، یه تسک بساز، دقیقاً توی تلگرام سینک سینکش کن با ایشوی گیت‌هاب، تمام کامنت‌ها، هر چیزی که تو گیت‌هاب هست رو حواست باشه داخل تسک بنویسی، به‌اضافه تمام چیزهایی که من خودم جداگانه بالاتر گفتم، توی فایل تسک بنویس، به‌صورت کامنت هم توی گیت‌هابم اضافه کن که این دو تا دقیقاً سینک باشن با هم.

English translation (technical):

Improve the manager-decision system. There is a GitHub issue with review comments from a colleague. Read all comments and merge everything substantive into our task file so the task file stays exactly in sync with the GitHub issue. Additionally the Manager found two bugs: (B1) every skill call asks for the save path instead of using a once-configured location set at install time; (B2) decision saving is never automatic after a sprint or task closes — it must run automatically on every successful task close, e.g. via the cognitive executor or the system prompt. The manager profile is still incomplete — build an accurate decision profile so the system can one day handle tasks without the Manager present. Do everything step by step and keep the task file and the GitHub issue fully in sync both ways.

Assumption: "توی تلگرام سینک" is voice-to-text noise and means "fully synced". No Telegram sync is requested.

Manager-reported items (from message 1, to implement step by step):

- B1 — Fixed path: the skill must not ask for a path on every call. Configure the path once at install time / inside the skill config.
- B2 — Automatic capture: decision extraction and saving must run automatically whenever a task or sprint closes successfully. Candidate homes: cognitive executor shutdown path or system-prompt close rule.
- P1 — Manager profile: finish an accurate profile built from manager decisions so future tasks can proceed without the Manager present.

## GitHub Issue Sync (Evidence, verbatim)

Source: `gh issue view 8 --json title,body,comments` on 2026-09-14. Repo: `mokhtarabadi/cognitive-lead-hq`. Issue state at capture: OPEN.

Title: Manager-decision skill with separate learning repo (evolve manager-AI sample)

Body (verbatim):

## Original Message (Persian)

بعد یک بخش جدید هم میشه اضافه کرد بهش منیجر دیسیژن، یک اسکیل باشه، خب؟ هر وقت فراخوانی بشه توی اون جلسه، تصمیمهایی که مدیر گرفته صحبتهایی کرده سیستم دیزاینی که کرده، همه رو یاد بگیریم توی یک ریپوی جداگانه همیشه داشته باشیم تصمیمات مدیر رو که بعداً اون نمونهی هوش مصنوعی که از مدیر ساختیم روز به روز بتونه بهبود پیدا کنه و بهتر بشه. بعد یک جای دیگه کامل یه نمونه کامل باشه بعد تصمیمات جزء دیگه نیاز به منیجر واقعی نباشه و از همون نمونه ساخته شده ایآی که از تصمیمات منیجر شکل گرفته توی سشنها استفاده بشه، مثلاً این شکل باشه، این نحو باشه که توی سشنهای مختلف خود منیجر مثلاً اون اسکیل یا ام سی پی میتونه باشه یا اسکیل میتونه باشه یا یک پلاگین برای اوپن کد باشه. صدا بزنه بعد اون سشن تصمیماتی که مدیر گرفته، مدیر گرفته شده استخراج بشه و هویت بصری ایآی منیجر یا مدیر آپدیت بشه.

#remaining

## English Translation

Build a manager-decision skill that extracts per-session manager decisions into a separate repo to evolve a manager-AI sample until micro-decisions no longer need the real manager. Full translation + refactored prompt in local task file.

## AI Analysis

Learning half of msg 587's execution half: append-only decision records (verbatim quote + rationale + session linkage) with human review gate before sample/identity promotion. Privacy redaction required.

---
Migrated from Telegram (msg 588, topic 458 Cognitive Lead, continuation of 587). See local task file for details.

Comment 1 (owner, verbatim):

Status review (META 219 session): the capture mechanism is live and verified - manager-decision skill + MCP server (extract/record/query/profile/evolve), auto-trigger detector, consult-on-stuck protocol, migration skill, push protocol, 27 records in mokhtarabadi/manager-decisions. Remaining before close: the sample-evolution loop has never run end to end (profile aggregate still baseline; propose_profile_evolution never promoted). Keeping open until the first reviewed promotion lands.

Comment 2 (owner, brainstorm follow-up plan, verbatim):

Follow-up plan from team brainstorm (vision: stop asking the Manager for simple/medium questions; AI follows similar past rulings). Do later, in order: (1) Maturity levels L0-L3 with counts, coverage, override rate; human review gates promotion. (2) Consult-first rule: agent must query decisions and log top-3 hits before asking the Manager; auto-follow above threshold, else escalate with search proof. (3) Ranked retrieval to replace substring search (filtered full-text first, embeddings later, with tests). (4) First reviewed promotion from the 27 live records: ruling clusters + dissent notes + expiry dates. Deferred: full doppelganger runtime (unsafe at 27 records). Risks tracked: stale auto-apply, false matches, redaction leaks, promotion drift.

Comment 3 (owner, raw-capture quality findings apex session 2026-09-14, verbatim):

## Raw-capture quality findings (apex session, 2026-09-14)

Provenance: 11 raw records `DEC-20260914-003` to `013` in `mokhtarabadi/manager-decisions` (`decisions/2026/09/`), captured via the `record_manager_decision` code path directly (sanitize + verify + schema + index regen all green, `store_mode=personal`). A Brain self-improvement round plus Hands review found these problems in the **raw** material that will one day feed the promotion loop. Posting here so the fix project gets field evidence.

### Findings (Brain + Hands agree)

| # | Problem | Evidence this session | Proposed fix |
|---|---|---|---|
| F1 | Reconstructed quotes in verbatim fields | No transcript file existed, so 7 of 11 quotes were rebuilt from compressed summaries, flagged in-record | Add a `fidelity` field (`verbatim` vs `reconstructed`); require a verbatim paste before any record can be promoted |
| F2 | Autopilot rulings lose their type | Valid categories exclude `autopilot-cycle`; 003/012 stored as generic `process` | Extend the category set or add a `mode` field (`autopilot` vs `manual`) |
| F3 | Goal-session id in `session_id` | Stored `ses_f60dc35...` (a goal session), breaking the task-id lineage convention | Split into `session_id` + `goal_ref`, migrate old rows |
| F4 | Duplicate check is manual | Always-English duplicate caught by luck (already `DEC-20260914-001`) | Fingerprint hash + auto-search before save |
| F5 | Standing rules mixed with episode notes | 003/009/011 (standing) sit beside 006/010 (one-offs) with no signal | Tag `standing` vs `episode`, store apart; standing orders get owner + expiry |

### Hands-only extras (apex-specific)

- **M1 — Detector never ran.** With no `tasks/.sessions/*/transcript.jsonl`, `detect_decision_moments` had no input; extraction fell back to agent memory. Fix: persist session transcripts (or a compress-safe quote log) so extraction always has a source.
- **M2 — Confirm-gate timing is honor-system.** The store order arrived before the scrubbed quotes were shown; the agent proceeded on the explicit order. Fix: tool-side staging (prepare → show → approve → write) instead of relying on agent discipline.
- **M3 — Sync debt is silent.** 23 files sat unpushed with no reminder. Fix: surface pending-push count at session start so the Manager sees it.

None of this blocks the open item above (first reviewed promotion); it hardens what the promotion will consume.

Sync note: a sync-confirmation comment was posted on the issue pointing back to this task file, so both sides reference each other.

## Local TODOs

- [x] Verify issue 8 body plus all three comments are captured verbatim above
- [x] Fix B1: single configured decision-repo path set at install, never prompt per call
- [x] Fix B2: automatic decision capture on every successful task and sprint close
- [x] Deliver P1: first reviewed profile promotion from live records
- [x] Implement brainstorm follow-ups in order: maturity levels, consult-first, ranked retrieval, first promotion
- [x] Harden raw capture: fidelity field, mode field, session plus goal refs, duplicate fingerprint, standing vs episode tags, transcript persistence, staged confirm gate, visible sync debt
- [x] Verify functionality

## Acceptance Criteria

- [x] Task file holds the full issue body plus all comments verbatim with nothing dropped
- [x] Task file holds the Manager-reported B1, B2, and P1 items above
- [x] A sync comment exists on the issue pointing to this task file
- [x] Fixed-path behavior: no per-call path prompt in the skill path
- [x] Auto-capture runs on successful task close with evidence
- [x] First reviewed profile promotion lands with Manager approval

## Verification Evidence

- **Test command:** `uv run --with pytest --with "mcp[cli]==1.30.0" --with httpx [--with pathspec] [--with pyyaml] pytest tests/test_decision_server.py -q` plus adjacent suites
- **Expected result:** all green; `lint_task_file` passes on the task file
- **Actual result:** `tests/test_decision_server.py`: 98 passed (93 existing + 5 new hardening tests); `test_mcp_servers.py` + `test_bundle_tasks.py` + `test_skill_registry.py`: 90 passed (memory-server tests needed `pyyaml` in the ad-hoc env — pre-existing env gap, not a code failure). B2 close rule is wired in `agents/cognitive-executor.md` but has no live close-run evidence yet; P1 promotion needs Manager approval of a DRAFT_READY draft against the live personal repo, so both AC boxes stay open honestly.
- **Exit code:** 0 (both runs)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** issue comments change after this capture; the file goes stale
- **Rollback plan:** re-run `gh issue view 8 --json` and update the sync section; keep the sync comment thread as history

---

## Execution Log & Reasoning

- Creation: backlog was empty (completed holds one release file). NEXT_ID discovery gave 230 with no active duplicate and no backlog collision. Source set to manager per direct Manager orders.
- Prior state: earlier decision work is archived and its issue follow-ups were bundled before; this file is the fresh single home for the open issue plus B1, B2, P1.
- Implementation is NOT started; awaiting Orchestrator blueprint and Manager approval per lifecycle.
- Autopilot implementation (this turn): Architect single-seat (schema/contract/API trigger). B1 resolved per LLM.txt 503-508 (never pin DECISION_REPO_PATH in shared opencode.json — per-user resolution breaks); implemented as install-once via shell/.env + .env.example + SKILL section + server docstring. B2 resolved against the Task 213 confirm gate as auto-EXTRACT on close + gated record (auto-record stays forbidden). Fragments are git-ignored so no system-prompt rebuild was needed (B2 scoped to executor + SKILL + server).
- Assumption A1: verbatim Persian orders from the prior turn were preserved at creation; no re-fetch of issue 8 comments was needed since content was captured then and code changes do not alter it.
- Assumption A2: P1 first promotion stays open — merging a profile draft needs the Manager's explicit APPROVED on a DRAFT_READY run against the live personal repo, which only the Manager can do.
- Q1 for Manager: approve running `propose_profile_evolution` against the live personal repo and merging the first reviewed promotion?
- Brain QA round (same task_id, diff attached): QA Engineer voted QA_PASSED. Notes kept as non-blocking: V1 duplicate scan reads every file per save (fine at current size); V2 ranked query uses OR logic for multi-word queries (best first, broader than old phrase match); V3 standing scope stores only the tag, owner+expiry not enforced yet; T1 promotion fidelity gate test and T2 old-record migration test deferred to promotion work.
- Brain review round (4 seats): Project Planner APPROVED (qa/ state, header synced, AC honestly open on B2-live-proof + P1-promotion); UI/UX Designer APPROVED (no user-visible surface); Sprint Strategist APPROVED (scope inside issue 8 + B1/B2/P1, no widening); Senior Programmer APPROVED (schema defaults keep old callers valid; accepts OR logic D1 and owner+expiry deferral D2) with one action A1: remove duplicated sentence in SKILL.md Consultation Workflow — done (one line removed), decision suite re-run: 98 passed.
- Manager-side decision replay (Manager order: decide from his side via manager-decision): consulted baseline profile + local store. Evidence: DECISION_REPO_PATH unset (project-fallback mode), local `decisions/` holds zero records, `compile_profile.py --repo .opencode/decisions` prints "No decisions found" (exit 0). Decision D1: NO promotion merge now — the live 27+11 records sit in the personal repo which is unreachable from this session, and identity updates need explicit human approval per baseline ("Gate anything that learns or publishes on explicit human approval"). Replay basis: baseline profile behavioral guideline + heuristics #1 (hard gates stay hard); no local DEC record exists to cite. Still needs the real Manager: confirm the personal repo path and APPROVE a DRAFT_READY draft run against it. UPDATE: Manager approved ("Approve merge clean migrate"), path resolved to `projects/manager-decisions` (43 records). Clean check: quotes are dicts {original, english_translation} — all 43 full, zero empty, nothing excluded. Created `samples/manager_profile.md` in the personal repo (baseline verbatim + first promotion: distribution, 8 clusters, dissent notes). Uncommitted/unpushed per ZAC — Manager pushes. P1 AC checked.
- Final Brain loop (full current diff, Manager order): QA Engineer QA_PASSED twice (second pass covers A1 fix + log updates + P1 note; H1 nested-type, H2 non-dict tamper, H3 explicit-None logged as low-risk debt). Review round: Planner APPROVED_WITH_CHANGES, Designer APPROVED, Strategist APPROVED, Programmer APPROVED_WITH_CHANGES. Final: APPROVED_WITH_CHANGES.
- Reviewer actions closed: (1) P1 proof — approval verbatim "Approve merge clean migrate"; merge file `manager-decisions/samples/manager_profile.md` (63 lines, 4674 bytes, verified on disk 2026-09-14); no commit hash exists yet because publishing is Manager-owned (file + 11 raw record pairs pending in that repo). (2) Follow-up opened: Task 231 in `tasks/backlog/` (B2 live close-run proof + H1/H2/H3 regression tests).
- Closure update (2026-09-14, Manager order: close one by one per protocol): B2 live proof delivered by Task 231 (`extract_session_decisions(231)` fired on a real close path, returned `[]` loudly with nothing written — no silent pass). P1 promotion file created in the personal repo with Manager approval. Checking the two remaining boxes (TODO P1, AC auto-capture) on this evidence.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `68f7286d105e7426ae8481f344095c077e86f9b0`
<!-- END_GIT_DIFF -->
