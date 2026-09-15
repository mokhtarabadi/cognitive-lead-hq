# Task 235: Review approval relay to Brain plus gitignore for session history

**File:** `tasks/completed/235-review-approval-relay-plus-gitignore-for-session-history.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Close the review-approval loop (reviewer approval → Hands tells Manager → Manager accepts → Hands tells Brain Programmer → Brain emits final XML) and gitignore Brain session history locally plus in the audit-agents skill for other projects.

## Manager's Notes

Original order (Persian, verbatim):

> خب الان خیلی خوب شد بهتر شد. فقط یه مورد دیگه اگر فکر می‌کنی باید رفع بشه رفعش کن و از برین هم بپرس. وقتی که من الان یک تسک کد ریویوئر تسک رو تأیید می‌کنم، می‌گه منتظر تأیید منیجره. تو به عنوان هندز باید به من بگی و من وقتی بهت می‌گم قبوله، تو به برین دوباره بگو به پروگرامر داخل برین بگو، بگو ادمین قبول کرد که اون تسک ایکس‌ام‌ال نهایی رو برات بزنه و تو انجامش بدی و مورد بعدی اینه که، دا ااا پوشه سشن‌هایی که الان آورد داریم انجام می‌دیم، هیستوری سشن‌ها که تو پوشه تسک داره قرار می‌گیره، این باید اگنور بشه. هم برای پروژه خودمون اگنورش کن هم آدیت ایجنت اسکیل رو ویرایش کن که وقتی اجراش کنم، دات اگنور بقیه پروژه‌ها رو هم آپدیت کنه برای این مورد. یه تسک برای اینم بزن.

English translation:

> Well, now it got very good, better. Just one more thing: if you think anything else needs fixing, fix it, and ask the Brain too. When I approve a task the Code Reviewer approved, it says it waits for the manager's approval. You as the Hands must tell me, and when I tell you it's accepted, you tell the Brain again — tell the Programmer inside the Brain — say the admin accepted, so it issues that final XML task for you and you execute it. And the next thing is: the session folders we are now bringing in, the session history that lands in the tasks folder, this must be ignored. Ignore it for our own project too, and edit the audit-agents skill so when I run it, it also updates the .gitignore of other projects for this case. Create a task for this too.

Breakdown:

1. B1 — Review-approval relay loop: today a technical approval ends at PO_REVIEW_PENDING and the loop stalls. Wanted flow: Hands notifies Manager of the technical approval → Manager says accepted → Hands calls the Brain again (Programmer seat) reporting admin acceptance → Brain emits the final XML → Hands executes it.
2. B2 — Gitignore session history: `tasks/.sessions/` history must be ignored. Already present in this repo's `.gitignore` (line 50, verified). Confirm it stays and is effective (untracked files check).
3. B3 — Audit-agents skill edit: the skill must update/ensure the session-history ignore rule in other projects' `.gitignore` when the Manager runs it.
4. Brain consult: ask the Brain about anything else worth fixing plus the design of B1/B3.

## Local TODOs

- [x] Ask the Brain (advisory): review-relay loop design, audit-skill gitignore design, any other fixes worth doing
- [x] Implement B1 relay rule in executor/Brain docs (Hands notifies Manager; on accept, re-call Brain Programmer for final XML)
- [x] Verify B2: tasks/.sessions/ ignored and untracked in this repo
- [x] Implement B3: audit-agents skill gains session-history gitignore rule for other projects
- [x] Full test suite passes, lint clean, stage, move to qa

## Acceptance Criteria

- [x] B1 relay loop documented and working: technical approval → Manager notice → accept → Brain Programmer final XML → Hands executes
- [x] B2 tasks/.sessions/ is gitignored with no tracked history files in this repo
- [x] B3 audit-agents skill updates other projects' .gitignore for session history
- [x] Brain consulted on relay design and any other fixes; answers logged

## Verification Evidence

- **Test command:** pytest tests/ -q (uv-pinned env) + git check-ignore -v tasks/.sessions/230/transcript.jsonl
- **Expected result:** suite exit 0; check-ignore returns the gitignore rule
- **Actual result:** 357 passed in 4.45s (second-hotfix re-run); check-ignore returns `.gitignore:50:tasks/.sessions/`; 0 tracked files; repo + global skill greps 2 hits each; lint_system_prompt_sync passes
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** relay rule could auto-close without real Manager approval; audit-skill edit could corrupt other projects' .gitignore
- **Rollback plan:** relay rule requires explicit accept word (never auto); .gitignore edit is append-only with duplicate-line guard, never rewrite

---

## Execution Log & Reasoning

Brain advisory (Architect seat, after one EMPTY_OUTPUT_RETRY + lean retry — the Task 232 guard working live): F1 relay rule in executor QA Review Phase + one-line Reviewer-contract mirror; F2 accept ONLY "Approved for closure"/"Close task" (reject "good"/"thanks"); F3 one exact Manager message before any final XML call, file stays in qa with PO_REVIEW_PENDING, call Brain Programmer once, log accept quote; F4 single `tasks/.sessions/` ignore line, verify via check-ignore + ls-files; F5 extend Plugin Runtime-State rule, only when tasks/ dir exists; F6 notice wording technical-vs-final split + single issuance + log advisory in task file.

Implementation: executor gains "Review-approval relay (manual mode)" subsection (verbatim relay, exact accept words, bare-"approved" counts only as direct answer to the closure question just asked, single issuance, autopilot runs relay as self but approval word still required) + Code Reviewer roster row relay line. Fragment 06-personas.md Reviewer contract now routes closure through a single relayed Programmer XML instead of emitting it directly (notice text unchanged). Shipped prompt regenerated via assembler (diff = exactly version 9.37.0 + reviewer line); lint_system_prompt_sync passes. Global audit-agents skill: Plugin Runtime-State rule extended with brain-session clause at both occurrences (replaceAll). B2 verified: `.gitignore:50:tasks/.sessions/` matches transcript path, 0 tracked files under tasks/.sessions/.

Hotfix after QA_REJECTED (re-QA judged the qa-path file with diff; first QA turn hit EMPTY_OUTPUT_RETRY, lean retry gave a STALE backlog-version verdict — lesson: lean retries drop the bundle, so re-QA ran with full bundle+diff). Correction: the repo template skill-templates/audit-agents/SKILL.md DOES exist (earlier no-repo-copy claim was wrong — verified via ls; rule at lines 39/392 without the clause). Applied the same brain-session clause there via replaceAll (both occurrences) — the B3 edit now lands in the repo diff (F1/M1 closed with grep proof: repo 2 hits, global 2 hits). Relay tightened in executor: bare-"approved" counts only as the next message directly answering the relayed closure question; explicit never-list (good/thanks/ok/okay/yes/done/fine/looks-good/emoji/silence); qa + PO_REVIEW_PENDING double-gate with halt-and-reverify; single issuance with failure-only re-call (logged transport/empty error, once lean, then escalate); autopilot self-decision NEVER satisfies the gate (F2/F3/F4/M3/M4 closed by construction). 06-personas.md Reviewer gains one approval-word sentence (self-made broken-sentence slip fixed immediately). Version bumped 9.37.0→9.37.1, prompt regenerated via assembler only (diff = exactly version line + reviewer sentence); lint_system_prompt_sync passes. Evidence: check-ignore matches .gitignore:50, ls-files 0 tracked, full suite 357 passed exit 0.

Second hotfix after second QA_REJECTED (contract-alignment deltas only, same qa file): 06-personas.md Reviewer sentence now mirrors the executor relay exactly — exact phrases "Approved for closure"/"Close task", bare-"approved" exception (next message answering the relayed question), full never-list (good/thanks/ok/okay/yes/done/fine/looks-good/emoji-only/silence), autopilot self-decision bar; notice text untouched. Audit clause (repo template both occurrences + global copy) gains the idempotency sentence (check first, add only if missing, never duplicate). Version 9.37.1→9.37.2, prompt regenerated via assembler only (diff = exactly version line + reviewer sentence); lint_system_prompt_sync passes. Evidence refreshed: 357 passed in 4.45s exit 0, check-ignore .gitignore:50, ls-files 0, skill greps 2+2.

Third QA (same id, diff attached): QA_PASSED — relay fail-closed, double gate holds, single issuance holds, no vulnerabilities, no missing tests. Final review (same id, diff attached): Code Reviewer technically approves, PO_REVIEW_PENDING. Strengths S1-S4 (exact-word gate, double gate, single issuance, idempotent audit). Two low notes, no code change needed: I1 reviewer text omits double-gate detail (executor stays normative), I2 prompt tail truncated in view (version head verified). Closure awaits the Manager approval word.

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `7cc2a7082b8825bc00c2346d219f7214bcce5c7a`
<!-- END_GIT_DIFF -->
