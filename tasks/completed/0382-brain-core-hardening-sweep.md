# Task 0382: Brain core + tooling hardening sweep (minimal-change bug hunt)

**File:** `tasks/qa/0382-brain-core-hardening-sweep.md`
**Source:** manager (2026-11-06 — fa: با رفت‌وبرگشت‌های انجام‌شده، اگر نقص دیگری در ابزار Brain و core آن هست که hallucination را تشدید کند یا گپ/بهبودی وجود دارد، با مشورت seatهای داخل Brain انجامش بده؛ minimal change، بدون تغییرات بزرگ؛ فقط باگ واقعی پیدا و همین‌جا حل شود تا session بسته شود)
**Type:** bug-hunt + hardening
**Status:** in-progress
**Submitted:** 2026-11-06T12:49:45Z

## Goal

Find remaining REAL bugs/gaps in the Brain tooling and core that could amplify hallucination (or otherwise break the Brain↔Hands loop), fix them with minimal diffs, and close the session. No refactoring, no features, no large changes.

## Manager's Notes (translated)

- With the recent back-and-forths, consult the Brain seats: if there are other defects in the Brain tool or its core that could worsen hallucination, or any other improvement/gap, do it with the seats' consultation.
- Minimal change only — no big changes wanted; find real bugs and fix them here so we can close the session.
- Luna 6 is strong and follows the system prompt precisely but is slow. Finish the last hardening work with it, then switch to a faster model (e.g. Muse 1.3 X-High, which is fast but misses bugs).

## Method (binding)

1. Multi-seat Brain consultation (analysis only): Architect + Senior Programmer + QA Engineer survey the Brain core/tooling for hallucination-amplifying defects. Ranked candidates, each with a concrete failure scenario.
2. Triage each candidate against the repo: reproduce with evidence or refute with evidence. Only reproduced REAL bugs are fixed.
3. Fixes are minimal diffs with regression pins; full suite must stay green.
4. Anything unverified, speculative, or large is recorded as a parked follow-up — NOT implemented.

## Scope guard

- Allowed: `mcp-brain-bridge/`, `prompts/fragments/`, `agents/cognitive-executor.md`, `tests/`, `CHANGELOG.md`, generated `system-prompt.md`.
- Forbidden: new features, refactors, server rewrites, model-routing changes, unrelated docs.

## Local TODOs

- [ ] Multi-seat consultation turn (Architect + Programmer + QA) under this task_id
- [ ] Triage candidates with repo evidence (reproduce or refute)
- [ ] Fix only verified real bugs (minimal diffs + regression tests)
- [ ] Full suite green + `lint_task_file`; stage, QA + review via Brain
- [ ] Relay verdict; close only on explicit approval; then close the session

## Acceptance Criteria

- [x] Every implemented fix traces to a reproduced failure with cited evidence.
- [x] No speculative/unverified change merged; parked items listed with reasons.
- [x] Full HQ suite green; `lint_task_file` passes.
- [x] Diff is minimal (no refactors, no scope widening).

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q` → red `1 failed, 33 passed` then green `34 passed`; full `rtk test ... python -m pytest tests/ -q` → `802 passed, 24 warnings`; `python3 -m py_compile tests/test_prompt_sync.py` OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`
- **Expected result:** red-first on the ferry-phrase pin; green after the 2-phrase fix + 9.74.0 rebuild; assembler diff = 3 hunks only
- **Actual result:** green across all gates; `grep -c "where to paste it" system-prompt.md` → 0; version pins updated 9.73.0 → 9.74.0
- **Exit code:** 0
- Stack-gate skip: root=. markers=[go.mod, buf.yaml, build.gradle.kts, Package.swift, *.xcodeproj, pyproject.toml+Flask, pyproject.toml+FastAPI, package.json+next.config.*, package.json+src/ports/, package.json+apps/expo, vite.config.*, nuxt.config.*, nest-cli.json, prisma/schema.prisma] matched=[] reason=no matching stack marker found; python-fastapi loaded for Python discipline only

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** hardening sweeps invite scope creep. Bound: reproduce-or-park rule; max 3 fix rounds (same retry guard as QA loops), then escalate.
- **Rollback:** each fix is a small hunk; revert per-hunk via git.

---

## Execution Log & Reasoning

- Model lane: Luna 6 for the whole sweep (precision over speed, Manager order). Switch to Muse 1.3 X-High only after this task closes.
- [2026-11-06] Seat consult done (Architect + Programmer + QA, analysis-only): 3 discovery lanes returned 20+ candidates. Triage verdicts (reproduce-or-park):
  - CONFIRMED — prompt 06-personas:50/:56 "where to paste it" contradicts the pinned no-ferry invariant (Manager never ferries; Hands chains `brain_turn` directly). Minimal fix below. (F1/F2 prompt lane)
  - REFUTED with evidence — session_ledger F10 (verdict type is `Union[str,bool]`; str branch raises on bad input; no fail-open), F11 (writes go only to `ledger_dir / LEDGER_FILENAME`; session_id is a JSON string field, no traversal write), loop_guard F6 (corrupt lines skipped on read but tool only writes valid JSON; skipping cannot fake a stop), F7 (legacy fallback is documented migration with stderr notice), F8 oscillation (bounded by the 3-rejections-per-stage rule), capability F4/F5 (prefix families match real namespaced tools; phantom names fail loudly at call time; exact-allowlist would be a large change), preflight F1/F2/F3 (explicit bad root raises loudly, never substitutes silently; ambient/one-off semantics documented), prompt F3 (hotfix XMLs are post-plan-approval implementation, not new plans — no observed stall), F4 (no observed discovery ping-pong since 0378), F5 (MODE line tells the Brain the live mode), F6 (QA/Reviewer scope split is by design; no cycling evidence), F7 (rejecting a wrong-gate answer with re-ask is correct behavior), F8 (verdict block lives in the English machine channel, not the localized handoff), Q1 escape hatch (bounded: unparseable verdict → QA_REJECTED + prose fallback + Manager override; no re-emit loop), Q2 (Architect instructs, Hands loads — no collision), attach F1/F2/F4/F5/F8/F9/F10/F11/F12 (label-precision nits; TOCTOU affects only which label, not behavior; all parked).
  - PARKED (no evidence of a live failure) — capability exact-allowlist, loop_guard oscillation cap, ANSI-label distinction, discovery Brain-side wording. Reasons recorded; no action.
- Brainstorm: not required — <reason>diagnostic consult with minimal reversible fixes; full 7-seat ceremony reserved for hard-to-reverse design</reason>.
- Seat Check: contract wording (`contract` trigger) → Software Architect; silent-fail review → Senior Programmer; adversarial triage → QA Engineer. Designer/Strategist/Planner skipped (no UX/capacity/planning surface).
- [2026-11-06] Fix applied: "where to paste it" → "where the Hands applies it" in QA (:50) + Reviewer (:56) summary specs; ferry pin extended; version pins 9.73.0 → 9.74.0; rebuilt (3-hunk diff), CHANGELOG entry, all gates green. Lite justification: 2-phrase wording, no security/financial surface, reversible via git, gates decide.
- [2026-11-06] QA verdict: `QA_PASSED` (no vulns, no missing tests). Re-review verdict: `PO_REVIEW_PENDING` (technical verdict: `APPROVED`). F1 wording replaced in both personas + shipped; F2 pin + 9.74.0; F3 minimal diff, no unrelated changes. File remains in `tasks/qa/`; closure awaits Manager's explicit `Approved for closure` / `Close task`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 27103b4..77682c2 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -9,6 +9,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 ### Fixed
 
 - Fix closure approval handling for question-tool answer envelopes and preserve approval answers verbatim.
+- **No-ferry wording in QA/Reviewer summaries:** the 3-line Manager summary spec said "where to paste it", implying the Manager ferries XML by hand — contradicting the pinned rule that the Hands chains `brain_turn` directly and the Manager only gates approvals. Both personas now say "where the Hands applies it"; the handoff pin covers the phrase. System prompt 9.73.0 → 9.74.0 via the assembler.
 - **Context-path injection for unlisted text files + no-repeat on unavailable paths:** `.env.example` (and any dotfile/extensionless text) resolved to zero chars twice while the model re-requested it — loop broken only by the Hands-side halt. Both attach paths now sniff unlisted suffixes (valid UTF-8 without NUL or disallowed Unicode control characters injects with a `sniffed text` label — tab/LF/CR/FF allowed; known binaries stay rejected), the allowlist gains the skill-sweep text suffixes (sqm, properties, plist, xcconfig, strings, mod, sum, ini, cfg, conf, mdx, csv, rst, fish, ejs), and the No-Hallucination contract states an `[unavailable: ...]` label means uninjectable — never re-request it. The sniff read is bounded at `_READ_MAX_BYTES + 1` (no stat/read race). System prompt 9.71.0 → 9.72.0 via the assembler.
 - **Service policy text now describes the uniform all-server Code Mode routing.**
 - **Prompt-sync regression test pins the binding fed-context contract:** assertions now require the mandatory verbatim-code-or-`context_paths` clause and its mirrored retrieval rule.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 6055978..880202d 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.73.0</system_version>
+<system_version>9.74.0</system_version>
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index 5bd3931..4062aa1 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -47,13 +47,13 @@
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-QA itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, the Hands chains the Code Reviewer itself; the Manager only gates approvals. **Automatic-mode override:** in automatic mode, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where the Hands applies it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-QA itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, the Hands chains the Code Reviewer itself; the Manager only gates approvals. **Automatic-mode override:** in automatic mode, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
 </persona>
 
   <persona name="Code Reviewer">
     <trigger>Hands completed-task summary ready, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact standalone phrases "Approved for closure" or "Close task" (case-insensitive) count, or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, silence, or any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** in automatic mode, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where the Hands applies it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact standalone phrases "Approved for closure" or "Close task" (case-insensitive) count, or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, silence, or any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** in automatic mode, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word.</behavior>
 </persona>
 
 <auto_load>
diff --git a/system-prompt.md b/system-prompt.md
index d8e4ed0..a0e9f13 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.73.0</system_version>
+<system_version>9.74.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -100,13 +100,13 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-QA itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, the Hands chains the Code Reviewer itself; the Manager only gates approvals. **Automatic-mode override:** in automatic mode, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where the Hands applies it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-QA itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, the Hands chains the Code Reviewer itself; the Manager only gates approvals. **Automatic-mode override:** in automatic mode, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
 </persona>
 
   <persona name="Code Reviewer">
     <trigger>Hands completed-task summary ready, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact standalone phrases "Approved for closure" or "Close task" (case-insensitive) count, or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, silence, or any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** in automatic mode, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where the Hands applies it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact standalone phrases "Approved for closure" or "Close task" (case-insensitive) count, or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, silence, or any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** in automatic mode, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word.</behavior>
 </persona>
 
 <auto_load>
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 910d924..1c9b08b 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -47,7 +47,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.73.0"
+    assert shipped == "9.74.0"
 
 
 def test_shipped_prompt_documents_context_path_line_ranges():
@@ -357,9 +357,9 @@ def test_closure_answer_verbatim_forwarding_is_pinned():
     )
 
 
-def test_shipped_prompt_version_is_9_73_0():
+def test_shipped_prompt_version_is_9_74_0():
     prompt = _read_shipped_prompt_for_approval_contract()
-    assert "9.73.0" in prompt
+    assert "9.74.0" in prompt
 
 
 def test_assembler_output_matches_shipped(tmp_path):
@@ -540,6 +540,7 @@ def test_manual_handoff_assigns_brain_turn_to_hands():
         "brings the result back",
         "paste the file tree and code context back",
         "pastes the Hands",
+        "where to paste it",
         "hand over to the Code Reviewer",
         "copy-paste relay instructions expected",
     ):
```
<!-- END_GIT_DIFF -->
