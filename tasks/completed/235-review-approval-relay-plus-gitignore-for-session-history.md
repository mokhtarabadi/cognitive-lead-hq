# Task 235: Review approval relay to Brain plus gitignore for session history

**File:** `tasks/qa/235-review-approval-relay-plus-gitignore-for-session-history.md`
**Source:** manager
**Type:** improvement
**Status:** open

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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1892e25..5108261 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -12,7 +12,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Decision follow-up hardening H1/H2/H3 + B2 live proof (Task 231):** fingerprint path now tolerates a stray string `verbatim_quote`/`extracted_decision` (H1), skips tampered non-dict store files in both the duplicate scan and the index rewrite instead of crashing (H2), and treats explicit `None` optionals as unset so safe defaults still apply (H3). B2 live evidence: `extract_session_decisions(231)` fired at close handling and returned `[]` loudly (no session transcript in headless run — nothing queued, nothing written). 3 new regression tests. Full decision suite: **101 passed**.
 - **Brain empty-output retry hint + prompt-size warn (Task 232):** `mcp-brain-bridge/server.py` no longer returns a silent blank REPORT — root cause confirmed in code: `parse_responses_text` yields `""` on missing/non-list output and `brain_turn` forwarded it with no guard. A single choke-point guard now substitutes the machine-readable `EMPTY_OUTPUT_RETRY` hint (fixed token, lean-retry shape: same task_id, `include_bundle=false`, escalate if still empty; verdict content never invented, status stays REPORT so old callers keep working), plus a stderr advisory when the prompt exceeds 60k chars (oversized prompts correlated with both observed flakes). `agents/cognitive-executor.md` Empty-output clause now names the token. 6 new offline tests (hint contract, missing/None/whitespace payloads, normal passthrough, stderr warn). Full suite: **345 passed**.
 - **Supervised autopilot with plan approval and seat routing (Task 233):** `agents/cognitive-executor.md` gains a supervised plan-approval section (discovery feed → Brain plan → one approval pause → seat-routed implementation; Relay questions and hard blockers are the only other interrupts), a Seat Check trigger-citation line, a goal-pause carve-out for plan approval, and generous lock-word recognition. `mcp-brain-bridge/server.py` gains a 150 KB total bundle cap (truncate/skip with notes) and a text `validate_plan_verdict` checker (5 fields; cites need path:line shape). `docs/conventions.md` gains risk tiers T0/T1/T2 plus a 3-tries-then-escalate contract. `skill-templates/telegram-issue-sync/SKILL.md` folds the GitHub-preference data question into the planning turn (repo + global copies). Shipped prompt rebuilt to 9.36.0 with a Supervised Autopilot Contract bullet (authority stays in the executor file). 5 new offline bridge tests. Full suite: **350 passed**. Postfix: verdict checker uses word-bound field matching (stub text inside longer words no longer validates), bundle truncation reserves suffix length so the total never exceeds the cap, contract bullet reworded to a single plan-approval pause.
-- **Brain sessions per project, legacy global read-through (Task 234):** `mcp-brain-bridge/loop_guard.py` gains `project_sessions_root()` (explicit override → param/`BRAIN_PROJECT_ROOT`/`BRAIN_WORKSPACE_ROOT` → cwd walk-up to a `tasks/` dir → legacy global fallback) plus `legacy_sessions_root()`; `server.py` threads an optional `project_root` through `_sessions_root`, `_transcript_path`, `_fed_context_path`, `load_history`, `append_turn`, `save/load_fed_context`, and `brain_turn` — writes always land per project under `tasks/.sessions/<id>/`, while reads fall back to the legacy global dir with a loud stderr note when the per-project file is missing. HQ folders 230-233 migrated from the global store into `tasks/.sessions/` with a sha256 manifest (`/tmp/migrate-234-manifest.json`), globals kept as fallback. 4 new offline regression tests. Full suite: **354 passed**. Hotfix: no-global-write (fallback writes reroute to `cwd/tasks/.sessions` with stderr warn), package-then-plain sibling import, per-project loop-guard hashes with legacy read fallback, per-turn sessions-root stderr line, 3 more tests (T5-T7). Full suite: **357 passed**.
+ - **Brain sessions per project, legacy global read-through (Task 234):** `mcp-brain-bridge/loop_guard.py` gains `project_sessions_root()` (explicit override → param/`BRAIN_PROJECT_ROOT`/`BRAIN_WORKSPACE_ROOT` → cwd walk-up to a `tasks/` dir → legacy global fallback) plus `legacy_sessions_root()`; `server.py` threads an optional `project_root` through `_sessions_root`, `_transcript_path`, `_fed_context_path`, `load_history`, `append_turn`, `save/load_fed_context`, and `brain_turn` — writes always land per project under `tasks/.sessions/<id>/`, while reads fall back to the legacy global dir with a loud stderr note when the per-project file is missing. HQ folders 230-233 migrated from the global store into `tasks/.sessions/` with a sha256 manifest (`/tmp/migrate-234-manifest.json`), globals kept as fallback. 4 new offline regression tests. Full suite: **354 passed**. Hotfix: no-global-write (fallback writes reroute to `cwd/tasks/.sessions` with stderr warn), package-then-plain sibling import, per-project loop-guard hashes with legacy read fallback, per-turn sessions-root stderr line, 3 more tests (T5-T7). Full suite: **357 passed**.
+  - **Review-approval relay + session-history gitignore (Task 235):** `agents/cognitive-executor.md` gains a Review-approval relay rule (technical approval → verbatim relay, file stays in qa; only the exact words "Approved for closure"/"Close task" count; Hands re-calls Brain Programmer once for a single final-closure XML and executes it exactly once) plus a relay line in the Code Reviewer roster row. `prompts/fragments/06-personas.md` Code Reviewer contract now routes closure through the relayed Programmer XML instead of emitting it directly. Shipped prompt rebuilt to 9.37.0. Global `audit-agents` skill Plugin Runtime-State rule now covers Brain session history (`tasks/.sessions/` added only after confirming the dir exists). Hotfix: relay tightened (bare-approved counts only as the next message answering the relayed question; explicit never-list incl. yes/done/okay/looks-good/emoji/silence; qa + PO_REVIEW_PENDING double-gate; single issuance with failure-only re-call; autopilot self-decision never satisfies); repo `skill-templates/audit-agents/SKILL.md` template extended too (both occurrences) so the rule ships in-repo. Second hotfix: reviewer contract mirrors the executor relay exactly (bare-approved exception + full never-list incl. okay/done/fine/looks-good/emoji-only + autopilot bar), audit clause gains a duplicate-line guard (check first, add only if missing), shipped prompt rebuilt to 9.37.2.
 
 ## [9.35.0] - 2026-09-14
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 8a5ba6e..c232617 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -387,6 +387,27 @@ needs no extra machinery.
     `EMPTY_OUTPUT_RETRY` token in this case — treat that token exactly like an
     empty output and follow the same retry shape.
 
+### Review-approval relay (manual mode)
+
+When a review turn returns technical approval (`PO_REVIEW_PENDING` with the
+technical-vs-final notice), relay the verdict to the Manager verbatim and
+STOP — the file stays in `tasks/qa/`. Accept ONLY the exact phrases
+"Approved for closure" or "Close task" as the go-ahead (matching is
+case-insensitive on these two phrases and nothing else). A bare "approved"
+counts only when it is the Manager's next message directly answering the
+relayed closure question; a bare "approved" anywhere else never counts.
+These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine",
+"looks good", emoji-only replies, and silence. On accept: verify the
+file is still in `tasks/qa/` AND the log still records `PO_REVIEW_PENDING`
+(both required — otherwise halt and re-verify instead of closing), call
+`brain_turn` once as Senior Programmer for the final closure XML, log the
+Manager's accept quote in the Execution Log, and execute that XML exactly
+once (single issuance — a successful closure XML is never re-requested;
+one re-call is allowed only if the first call failed with a logged
+transport or empty-output error, retried once lean, then escalated).
+Even in autopilot, a replayed past ruling or self-decision NEVER satisfies
+this gate — halt and surface the verbatim relay question to the Manager.
+
 ### Autopilot mode (default OFF)
 
 When the Manager says "on autopilot do X": run the full state machine
@@ -468,7 +489,7 @@ table in the same commit.
 | Project Planner | Status checks, milestone planning, explicit Manager request | Kanban file state + milestones; never backlog priority |
 | Sprint Strategist | Sprint planning, backlog prioritization, sprint overfill | Capacity, MoSCoW, WIP ≤ 3; owns priority and sprint scope |
 | QA Engineer | Implementation complete, explicit test request | Adversarial testing; verdict `QA_PASSED` / `QA_REJECTED` |
-| Code Reviewer | Task summary pasted, PR submitted, review requested | Audit vs blueprint; verdict `APPROVED` / `APPROVED_WITH_CHANGES` / `REJECTED_NEEDS_FIXES` |
+| Code Reviewer | Task summary pasted, PR submitted, review requested | Audit vs blueprint; verdict `APPROVED` / `APPROVED_WITH_CHANGES` / `REJECTED_NEEDS_FIXES`; technical approval → `PO_REVIEW_PENDING` + notice, closure only via relayed Programmer XML after the exact approval word |
 
 **Load rules (mirror of `<auto_load>`):** Layer 1 — explicit mention wins
 (exact name or alias: QA, Reviewer, Architect, Strategist, Planner,
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 68fbbb3..11f4054 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.36.0</system_version>
+<system_version>9.37.2</system_version>
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index b0f0fc7..a3d8414 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -53,7 +53,7 @@
   <persona name="Code Reviewer">
     <trigger>Manager pastes the Hands' completed Task Summary, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." ONLY when the Manager explicitly uses the keyword "Approved for closure" or "Close task", generate the final closure task to `mkdir -p tasks/completed/`, use `git mv` to move the task file to `tasks/completed/`, and strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself.</behavior>
 </persona>
 
 <auto_load>
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index e5987cf..6eb70b6 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -36,7 +36,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Execution Log & Reasoning` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
 - **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
-- **Plugin Runtime-State gitignore**: If the project uses OpenCode plugins that write per-project state, `.gitignore` MUST cover plugin runtime-state paths (e.g. worktree checkouts, session/state JSON, goal-state dirs) while MUST NOT ignore deliberate config overrides checked in on purpose (e.g. a project-level plugin config pinning team-shared settings). Audit `.gitignore` read-only first; patch only paths belonging to plugins actually detected in the project's `opencode.json`/`tui.json` `plugin` arrays — never speculative entries.
+- **Plugin Runtime-State gitignore**: If the project uses OpenCode plugins that write per-project state, `.gitignore` MUST cover plugin runtime-state paths (e.g. worktree checkouts, session/state JSON, goal-state dirs) while MUST NOT ignore deliberate config overrides checked in on purpose (e.g. a project-level plugin config pinning team-shared settings). Audit `.gitignore` read-only first; patch only paths belonging to plugins actually detected in the project's `opencode.json`/`tui.json` `plugin` arrays — never speculative entries. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
 
 ---
 
@@ -389,7 +389,7 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 - **Task-Number Reference Discipline**: `AGENTS.md` MUST include a guardrail restricting task-number references to code comments, CHANGELOG entries, task files, history archives, and HTML comments — never in visible prompt prose, headings, or skill instructions. `docs/conventions.md` MUST contain a `## Task-Number Reference Discipline` section.
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Execution Log & Reasoning` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
 - **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
-- **Plugin Runtime-State gitignore**: If the project uses OpenCode plugins that write per-project state, `.gitignore` MUST cover plugin runtime-state paths (e.g. worktree checkouts, session/state JSON, goal-state dirs) while MUST NOT ignore deliberate config overrides checked in on purpose (e.g. a project-level plugin config pinning team-shared settings). Audit `.gitignore` read-only first; patch only paths belonging to plugins actually detected in the project's `opencode.json`/`tui.json` `plugin` arrays — never speculative entries.
+- **Plugin Runtime-State gitignore**: If the project uses OpenCode plugins that write per-project state, `.gitignore` MUST cover plugin runtime-state paths (e.g. worktree checkouts, session/state JSON, goal-state dirs) while MUST NOT ignore deliberate config overrides checked in on purpose (e.g. a project-level plugin config pinning team-shared settings). Audit `.gitignore` read-only first; patch only paths belonging to plugins actually detected in the project's `opencode.json`/`tui.json` `plugin` arrays — never speculative entries. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
 
 ### Resolution Protocol
 
diff --git a/system-prompt.md b/system-prompt.md
index 0a2b905..03361cc 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.36.0</system_version>
+<system_version>9.37.2</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -105,7 +105,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="Code Reviewer">
     <trigger>Manager pastes the Hands' completed Task Summary, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." ONLY when the Manager explicitly uses the keyword "Approved for closure" or "Close task", generate the final closure task to `mkdir -p tasks/completed/`, use `git mv` to move the task file to `tasks/completed/`, and strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself.</behavior>
 </persona>
 
 <auto_load>
```
<!-- END_GIT_DIFF -->
