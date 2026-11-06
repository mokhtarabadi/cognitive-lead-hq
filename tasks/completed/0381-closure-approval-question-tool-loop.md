# Task 0381: Closure approval via question tool loops instead of closing

**File:** `tasks/qa/0381-closure-approval-question-tool-loop.md`
**Source:** manager (2026-11-06 — ad-hoc fa, translated above)
**Type:** bugfix
**Status:** in-progress
**Submitted:** 2026-11-06T12:20:57Z
**Estimate:** 4h
**Deadline:** 2026-11-06

## Goal

End the closure-approval loop: when the Manager picks `Approved for closure` / `Close task` in the `question`-tool approval card, the Brain must accept it on the first relay — not reject it as "embedded in a larger message" turn after turn.

## Manager's Notes

Persian verbatim: "ببین، همین الان یه باگ دیگه پیدا شد، همین Approve for Closure. من یک بار زدم، چرا هی لوپ انداخت Brain؟ باگش رو پیدا کن، یک تسک جدید براش بساز و با کمک خود Brain این باگ Approve for Closure رو هم حل کن. اما دفعه اول که من توی ابزار Question، Approve for Closure رو انتخاب کردم، باید انجام می‌داد، نه هی لوپ بندازه."

Translation: a new bug was found in Approve-for-Closure. The Manager selected it once in the Question tool, but the Brain looped. Find the bug, create a new task, fix it with the Brain's help. The first selection must take effect — no looping.

## Root cause (verified, not hypothesized)

- Case: task 0380 closure. The Hands relayed `PO_REVIEW_PENDING` via the `question` tool (one narrow question, options `Approved for closure` / `Not yet`). The Manager picked `Approved for closure`. The tool result arrived as: `User has answered your questions: "Code Reviewer verdict ... Reply 'Approved for closure' to commit and finish."="Approved for closure"`.
- That tool result IS the Manager's next message directly answering the relayed closure question — contract-satisfying per `prompts/fragments/24-language_policy.md:41` ("A bare `approved` counts only as the next message directly answering the relayed closure question").
- But the Hands paraphrased the answer into a larger prompt (mode line + context), and the Brain's exact-literal closure gate (`prompts/fragments/06-personas.md:56` Reviewer behavior: "Only the exact phrases ... count", "nor does any autopilot self-decision") demands the phrase as the entire standalone message — structurally impossible for the Hands, which must always include the mode line and task context. Result: 3 consecutive closure rejects ("not exactly the required approval phrase" / "embedded in a larger message"), closed only by sending the bare phrase with the bundle switched off (losing task context).
- Asymmetry: the plan gate explicitly recognizes "through the question tool path" (`13-constraints.md:3`, `24-language_policy.md:41`); the closure gate has no question-tool-path recognition. That missing half is the bug.

## Fix direction (for the Brain plan to confirm)

1. Teach the Brain the question-tool answer envelope: a `User has answered your questions: "<header>"="<exact phrase>"` tool result quoting `Approved for closure` or `Close task` IS the Manager's exact answer — accept on first relay, never demand a standalone retype.
2. Teach the Hands to forward approval answers verbatim (quoted envelope, not paraphrase) — `agents/cognitive-executor.md` relay rule.
3. Touch points (confirm in plan): `prompts/fragments/06-personas.md` (Reviewer closure rule), `prompts/fragments/13-constraints.md` (Approval Literals Guard), `prompts/fragments/24-language_policy.md:41`, `agents/cognitive-executor.md` (relay/closure section), system-prompt rebuild with version bump, `tests/test_prompt_sync.py` regression pin, `CHANGELOG.md` entry. No `server.py` behavior change expected (prompt-level fix, same class as the plan-gate precedent) — plan must say so explicitly or justify a code change.

## Local TODOs

- [ ] Brain planning turn under this task_id (Seat Check + brainstorm evaluation on record)
- [ ] Implement the approved plan (prompt sentences + executor rule + rebuild + tests)
- [x] Full HQ suite green + `lint_task_file` on the active task file
- [x] Stage + inject diff, move to QA, Brain QA + review turns
- [ ] Relay verdict to Manager; closure only on explicit `Approved for closure` / `Close task`

## Acceptance Criteria

- [x] A question-tool answer envelope quoting the exact closure phrase is accepted as the Manager's approval on first relay (pinned by a shipped-prompt regression test).
- [x] The Hands relay rule forbids paraphrasing approval answers (verbatim quoted envelope).
- [x] No other approval-gate semantics change: blanket acknowledgements still never count; bare `approved` still counts only as the next message answering the relayed question.
- [x] `test_prompt_sync.py` assembler-identity test still passes (rebuild is byte-clean except intended hunks).
- [x] Full HQ suite green.
- [x] `lint_task_file` passes on the active task file.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q` → `31 passed`; full `rtk test ... python -m pytest tests/ -q` → `799 passed, 24 warnings`; `python3 -m py_compile tests/test_prompt_sync.py` OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`
- **Expected result:** red-first 4 failed (3 new tests + version pin) before the fix, all green after; assembler diff = 4 intended hunks only
- **Actual result:** red confirmed `4 failed, 27 passed`; after fix `31 passed` prompt-sync, `799 passed` full; assembler output differs from old shipped file in exactly the 4 intended hunks (version + 3 contract sentences)
- **Exit code:** 0
- Stack-gate skip: root=. markers=[go.mod, buf.yaml, build.gradle.kts, Package.swift, *.xcodeproj, pyproject.toml+Flask, pyproject.toml+FastAPI, package.json+next.config.*, package.json+src/ports/, package.json+apps/expo, vite.config.*, nuxt.config.*, nest-cli.json, prisma/schema.prisma] matched=[] reason=no matching stack marker found; python-fastapi loaded for Python discipline only
- **QA hotfix (2026-11-06):** negative-case pin only.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q` → `32 passed` (incl. `test_closure_approval_keeps_existing_negative_cases`); full `rtk test ... python -m pytest tests/ -q` → `800 passed, 24 warnings`; `python3 -m py_compile tests/test_prompt_sync.py` OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`
  - **Expected result:** all green; Deviation D1 logged (removed pre-0381 sentence not pinned)
  - **Actual result:** green across all four gates
  - **Exit code:** 0
- **Reviewer hotfix (2026-11-06):** preflight alignment + pin.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q` → red `1 failed, 32 passed` then green `33 passed` (incl. `test_executor_capability_preflight_matches_closure_answer_contract`); full `rtk test ... python -m pytest tests/ -q` → `801 passed, 24 warnings`; `python3 -m py_compile tests/test_prompt_sync.py` OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`
  - **Expected result:** all green; no fragment/system-prompt/CHANGELOG/server change
  - **Actual result:** green across all four gates; Deviation D2 logged (EXECUTOR const fix)
  - **Exit code:** 0
- **Reviewer hotfix 2 (2026-11-06):** relay acceptance alignment + pin.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q` → red `1 failed, 33 passed` then green `34 passed` (incl. `test_executor_review_relay_accepts_closure_answer_envelope`); full `rtk test ... python -m pytest tests/ -q` → `802 passed, 24 warnings`; `python3 -m py_compile tests/test_prompt_sync.py` OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`
  - **Expected result:** all green; no fragment/system-prompt/CHANGELOG/server change
  - **Actual result:** green across all four gates
  - **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** loosening the literal gate could let paraphrased approvals through. Bound: only the verbatim `question`-tool envelope with the exact English literal counts; paraphrases and blanket acknowledgements still never count.
- **Rollback:** revert fragment/executor sentences; rebuild prompt to prior version.

---

## Execution Log & Reasoning

- (autopilot off — manual mode; Manager ferries nothing, Hands chains `brain_turn` calls directly)
- [2026-11-06] Seat Check: contract wording → Software Architect; brainstorm not required (single-domain reversible). Plan approved via question tool ("Approved").
- [2026-11-06] Assumption A1: skipped the 4-subagent fan-out — all four lanes' files were already read verbatim natively in-session (fragment lines, executor relay, tests, CHANGELOG); `grep -c "has answered" server.py` → 0 proves the envelope never passes through bridge code, so no runtime change is needed.
- [2026-11-06] Test-first: new envelope + forwarding + version tests failed red as expected (`4 failed, 27 passed`), then green after the fix. One repair: the verbatim-forwarding pin reads `agents/cognitive-executor.md` (not system-prompt.md) since the executor is not assembled into the shipped prompt — matches existing `test_executor_*` conventions.
- [2026-11-06] No `server.py` change (plan-confirmed): the envelope is produced by the question tool; the defect was prompt interpretation + Hands paraphrasing. Sibling docs read (fragments/agents/tests READMEs + DECISIONS); no doc changes required — wording change is contract-scoped, rollback via git + rebuild.
- Brainstorm: not required — <reason>single-domain prompt-contract fix with ledger-verified root cause, no cross-disciplinary ambiguity</reason>.
- [2026-11-06 QA hotfix] QA_REJECTED (test-only gap): new regression pinned positive envelope wording but not the preserved negative cases. Added `test_closure_approval_keeps_existing_negative_cases` (Deviation D1: QA-prescribed 4th string was the pre-0381 bare-approved sentence the approved plan replaced; pinning it would require a prompt change the hotfix forbids — test pins the three negative cases as actually shipped). No prompt/prod change. Prompt-sync `32 passed`; full `800 passed, 24 warnings`; py_compile OK; docs-sync OK.
- [2026-11-06 reviewer hotfix 1] REJECTED_NEEDS_FIXES was correct: Capability Preflight still said closure accepts only exact phrases with bare-approved-never-counts, contradicting the new relay rule. Test-first pin failed red alone, then green after aligning the paragraph (Deviation D2: prescribed `_read("...")` str arg fixed to existing EXECUTOR Path const). No fragment/system-prompt/CHANGELOG/server change.
- [2026-11-06 reviewer hotfix 2] REJECTED_NEEDS_FIXES was correct: the operational Review-approval relay still said "Accept ONLY the exact phrases", so the Hands could reject the envelope before relaying. Test-first (`1 failed, 33 passed` red on the new relay pin), then aligned the relay clause with preflight (one long line kept intact for the pin). No fragment/system-prompt/CHANGELOG/server change. Prompt-sync `34 passed`; full `802 passed, 24 warnings`; py_compile OK; docs-sync OK.
- [2026-11-06] Re-review verdict: `PO_REVIEW_PENDING` (technical verdict: `APPROVED`). F1 preflight+relay aligned; F2 regression pins both; F3 version/artifact/changelog consistent; no server.py change. File remains in `tasks/qa/`; closure awaits Manager's explicit `Approved for closure` / `Close task`.

### Reviewer Follow-up Checklist

- [x] Add preflight-alignment regression test (red-first)
- [x] Align Capability Preflight approval paragraph with envelope + direct-answer rules
- [x] Re-verify all gates, re-stage, chain re-review
- [x] Align Review-approval relay acceptance clause + pin test (reviewer hotfix 2); re-verify, re-stage, chain re-review

## QA Follow-up Checklist

- [x] Add negative-case regression test (test-only, no prompt change)
- [x] Re-run prompt-sync (32 passed) + full suite (800 passed) + py_compile + docs-sync
- [x] Record evidence, lint, re-stage, chain re-QA

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index c002e82..27103b4 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- Fix closure approval handling for question-tool answer envelopes and preserve approval answers verbatim.
 - **Context-path injection for unlisted text files + no-repeat on unavailable paths:** `.env.example` (and any dotfile/extensionless text) resolved to zero chars twice while the model re-requested it — loop broken only by the Hands-side halt. Both attach paths now sniff unlisted suffixes (valid UTF-8 without NUL or disallowed Unicode control characters injects with a `sniffed text` label — tab/LF/CR/FF allowed; known binaries stay rejected), the allowlist gains the skill-sweep text suffixes (sqm, properties, plist, xcconfig, strings, mod, sum, ini, cfg, conf, mdx, csv, rst, fish, ejs), and the No-Hallucination contract states an `[unavailable: ...]` label means uninjectable — never re-request it. The sniff read is bounded at `_READ_MAX_BYTES + 1` (no stat/read race). System prompt 9.71.0 → 9.72.0 via the assembler.
 - **Service policy text now describes the uniform all-server Code Mode routing.**
 - **Prompt-sync regression test pins the binding fed-context contract:** assertions now require the mandatory verbatim-code-or-`context_paths` clause and its mirrored retrieval rule.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 6590c25..3eece49 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -124,7 +124,7 @@ Context is finite. Two layers keep long sessions productive, and the agent's dur
 
 ## Capability Preflight (session start)
 
-Before approval-sensitive work (plan approval, review approval, closure), check the capability manifest: every `brain_turn` prints a `capability-manifest:` diagnostic line to stderr mapping each required tool to `AVAILABLE`, `UNAVAILABLE_REQUIRED`, or `UNAVAILABLE_OPTIONAL`. A step whose required tool is `UNAVAILABLE_REQUIRED` (for example the `question` tool) is never silently skipped. Emit the relay block the turn returned (missing tool names, stage, one narrow question, one answer slot) through the mode-appropriate channel: manual mode relays it to the Manager verbatim and pauses with the relayed question as the named blocker; autopilot halts with the relay block as the named blocker. Approval collection follows the single approval rule: closure accepts only the exact phrases "Approved for closure" or "Close task" (a bare "approved" never counts); the plan gate accepts "approved" in any case. Blanket acknowledgements ("ok", "yes", "looks good", emoji) never count as approval at any gate. At plan-approval you MUST collect the decision via the question tool whose body carries the full plan text (see the Plan presentation contract), with one answer slot; at the PO_REVIEW_PENDING relay and any closure approval gate, one narrow question and one answer slot. Prose-only approval asks are forbidden because an auto-continue loop can roll past prose. This holds in manual and autopilot. If question is UNAVAILABLE_REQUIRED, emit the relay block and pause with it as the named blocker; never skip. Only hard blockers may use prose.
+Before approval-sensitive work (plan approval, review approval, closure), check the capability manifest: every `brain_turn` prints a `capability-manifest:` diagnostic line to stderr mapping each required tool to `AVAILABLE`, `UNAVAILABLE_REQUIRED`, or `UNAVAILABLE_OPTIONAL`. A step whose required tool is `UNAVAILABLE_REQUIRED` (for example the `question` tool) is never silently skipped. Emit the relay block the turn returned (missing tool names, stage, one narrow question, one answer slot) through the mode-appropriate channel: manual mode relays it to the Manager verbatim and pauses with the relayed question as the named blocker; autopilot halts with the relay block as the named blocker. Approval collection follows the single approval rule. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. The plan gate accepts "approved" in any case. Blanket acknowledgements ("ok", "yes", "looks good", emoji) never count as approval at any gate. At plan-approval you MUST collect the decision via the question tool whose body carries the full plan text (see the Plan presentation contract), with one answer slot; at the PO_REVIEW_PENDING relay and any closure approval gate, one narrow question and one answer slot. Prose-only approval asks are forbidden because an auto-continue loop can roll past prose. This holds in manual and autopilot. If question is UNAVAILABLE_REQUIRED, emit the relay block and pause with it as the named blocker; never skip. Only hard blockers may use prose.
 
 ## Subagent Delegation for Context Discovery
 
@@ -492,12 +492,7 @@ its own fenced code); do NOT emit copy-paste task ferrying instructions — the
 
 When a review turn returns technical approval (`PO_REVIEW_PENDING` with the
 technical-vs-final notice), relay the verdict to the Manager verbatim via the question tool with one narrow question and
-STOP — the file stays in `tasks/qa/`. Accept ONLY the exact phrases
-"Approved for closure" or "Close task" as the go-ahead (matching is
-case-insensitive on these two phrases and nothing else). A bare "approved"
-counts only when it is the Manager's next message directly answering the
-relayed closure question; a bare "approved" anywhere else never counts.
-These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine",
+STOP — the file stays in `tasks/qa/`. When the Manager answers through the question tool, the next `brain_turn` must carry the complete result envelope verbatim in a clearly labeled `Question-tool answer (verbatim)` block. Do not paraphrase, summarize, normalize, truncate, or strip the envelope. Keep the required mode line, full active task context, and the Brain instruction outside the unchanged block. The surrounding mode line, task context, and instruction do not invalidate the answer envelope. Accept ONLY the exact standalone Manager answers "Approved for closure" or "Close task" (case-insensitive on these two phrases), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine",
 "looks good", emoji-only replies, and silence. On accept: verify the
 file is still in `tasks/qa/` AND the log still records `PO_REVIEW_PENDING`
 (both required — otherwise halt and re-verify instead of closing), call
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index d75719f..6055978 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.72.0</system_version>
+<system_version>9.73.0</system_version>
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index fe1a587..5bd3931 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -53,7 +53,7 @@
   <persona name="Code Reviewer">
     <trigger>Hands completed-task summary ready, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** in automatic mode, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact standalone phrases "Approved for closure" or "Close task" (case-insensitive) count, or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, silence, or any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** in automatic mode, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word.</behavior>
 </persona>
 
 <auto_load>
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index e2df92b..7e1d8fd 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -1,6 +1,6 @@
 <constraints>
 - **Cognitive Language Rule:** English inside, requested language outside. All internal reasoning, architectural blueprints, XML task generation, Hands execution logs, and Brain turns MUST always be written in English. Only the final Manager-facing handoff — including clarification requests — may use the per-message requested language. Non-English text is permitted ONLY as explicitly delimited quoted source material (verbatim evidence, original-message quotes). This rule takes precedence over any localized-language instruction elsewhere.
-- **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path; closure accepts only the exact phrases `Approved for closure` or `Close task`. Blanket acknowledgements never count at any gate.
+- **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need. For file slices, use `path#Lstart-end` for inclusive 1-based line ranges or `path#Lstart-` for the tail through end-of-file. An `[unavailable: ...]` label (unsupported extension, outside workspace, unreadable, bad range — anything that is NOT a truncation note) means that path cannot be injected: never re-request the same path. Either proceed without it, ask the Hands for an inline paste of the exact lines needed, or escalate.
diff --git a/prompts/fragments/24-language_policy.md b/prompts/fragments/24-language_policy.md
index 85914a3..a612bca 100644
--- a/prompts/fragments/24-language_policy.md
+++ b/prompts/fragments/24-language_policy.md
@@ -38,7 +38,7 @@ The final Manager-facing handoff follows the per-message requested language. For
 
 Approval phrases match ONLY as English literals. Never translate-then-compare.
 
-Plan gate accepts approved in any case through the question tool path. Closure accepts only the exact phrases Approved for closure or Close task. A bare approved counts only as the next message directly answering the relayed closure question. Good, thanks, ok, yes, done, fine, looks good, emoji-only replies, and silence never count.
+Plan gate accepts `approved` in any case through the question tool path. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. Blanket acknowledgements never count at any gate.
 
 ## Execution Binding
 
diff --git a/system-prompt.md b/system-prompt.md
index 2718577..d8e4ed0 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.72.0</system_version>
+<system_version>9.73.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -106,7 +106,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="Code Reviewer">
     <trigger>Hands completed-task summary ready, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** in automatic mode, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact standalone phrases "Approved for closure" or "Close task" (case-insensitive) count, or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, silence, or any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** in automatic mode, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word.</behavior>
 </persona>
 
 <auto_load>
@@ -491,7 +491,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 
 <constraints>
 - **Cognitive Language Rule:** English inside, requested language outside. All internal reasoning, architectural blueprints, XML task generation, Hands execution logs, and Brain turns MUST always be written in English. Only the final Manager-facing handoff — including clarification requests — may use the per-message requested language. Non-English text is permitted ONLY as explicitly delimited quoted source material (verbatim evidence, original-message quotes). This rule takes precedence over any localized-language instruction elsewhere.
-- **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path; closure accepts only the exact phrases `Approved for closure` or `Close task`. Blanket acknowledgements never count at any gate.
+- **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need. For file slices, use `path#Lstart-end` for inclusive 1-based line ranges or `path#Lstart-` for the tail through end-of-file. An `[unavailable: ...]` label (unsupported extension, outside workspace, unreadable, bad range — anything that is NOT a truncation note) means that path cannot be injected: never re-request the same path. Either proceed without it, ask the Hands for an inline paste of the exact lines needed, or escalate.
@@ -818,7 +818,7 @@ The final Manager-facing handoff follows the per-message requested language. For
 
 Approval phrases match ONLY as English literals. Never translate-then-compare.
 
-Plan gate accepts approved in any case through the question tool path. Closure accepts only the exact phrases Approved for closure or Close task. A bare approved counts only as the next message directly answering the relayed closure question. Good, thanks, ok, yes, done, fine, looks good, emoji-only replies, and silence never count.
+Plan gate accepts `approved` in any case through the question tool path. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. Blanket acknowledgements never count at any gate.
 
 ## Execution Binding
 
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index a8e9323..910d924 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -47,7 +47,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.72.0"
+    assert shipped == "9.73.0"
 
 
 def test_shipped_prompt_documents_context_path_line_ranges():
@@ -224,6 +224,144 @@ def test_approval_literals_match_english_only():
     assert "Approval Literals Guard" in text
 
 
+def _read_shipped_prompt_for_approval_contract() -> str:
+    """Read the generated prompt that defines the runtime approval contract."""
+    from pathlib import Path
+
+    project_root = Path(__file__).resolve().parents[1]
+    return (project_root / "system-prompt.md").read_text(encoding="utf-8")
+
+
+def test_closure_question_tool_envelope_acceptance_is_pinned():
+    prompt = _read_shipped_prompt_for_approval_contract()
+
+    assert (
+        "either exact phrase as the answer value in an unmodified question-tool result"
+        in prompt
+    )
+    assert 'User has answered your questions: "<question>"="<answer>"' in prompt
+    assert "immediately preceding relayed closure-approval question" in prompt
+    assert "Compare only the answer value, not the quoted question/header" in prompt
+    assert "do not require the approval phrase to be the entire Hands message" in prompt
+    assert 'The existing bare "approved" exception remains limited' in prompt
+
+
+def test_closure_approval_keeps_existing_negative_cases():
+    """Prevent envelope support from broadening unrelated closure approvals.
+
+    Deviation D1 from the QA-prescribed test: the QA hotfix listed the
+    pre-0381 sentence 'A bare "approved" counts only when ... anywhere else
+    never counts', but the approved plan replaced that sentence with the
+    'remains limited' formulation (direct answer + question-tool answer
+    value), already pinned above. Re-adding the removed sentence would be a
+    prompt change, which the hotfix forbids — so this pins the negative
+    cases exactly as shipped.
+    """
+    prompt = _read_shipped_prompt_for_approval_contract()
+
+    preserved_contract = (
+        'These never count: "good", "thanks", "ok", "okay", "yes", "done", '
+        '"fine", "looks good", emoji-only replies, silence, or any autopilot self-decision.',
+        "Blanket acknowledgements never count at any gate.",
+        (
+            'The existing bare "approved" exception remains limited to the '
+            "Manager's direct answer to that immediately preceding "
+            "closure-approval question, including the exact answer value "
+            '"approved" in its question-tool result.'
+        ),
+    )
+
+    for contract in preserved_contract:
+        assert contract in prompt
+
+
+def test_executor_capability_preflight_matches_closure_answer_contract():
+    """Keep startup approval guidance aligned with the operational closure relay.
+
+    Deviation D2 from the reviewer-prescribed test: it called
+    `_read("agents/cognitive-executor.md")` with a str, but `_read` needs a
+    Path — so this uses the existing EXECUTOR constant instead. Same
+    assertions otherwise.
+    """
+    executor = _read(EXECUTOR)
+    capability_preflight = executor.split("## Capability Preflight (session start)", 1)[
+        1
+    ].split("## Subagent Delegation for Context Discovery", 1)[0]
+
+    assert (
+        "either exact phrase as the answer value in an unmodified question-tool result"
+        in capability_preflight
+    )
+    assert (
+        "Compare only the answer value, not the quoted question/header"
+        in capability_preflight
+    )
+    assert (
+        'The existing bare "approved" exception remains limited to the Manager\'s direct answer'
+        in capability_preflight
+    )
+    assert (
+        'including the exact answer value "approved" in its question-tool result'
+        in capability_preflight
+    )
+    assert 'a bare "approved" never counts' not in capability_preflight
+
+
+def test_executor_review_relay_accepts_closure_answer_envelope():
+    """Keep the operational review relay aligned with closure approval rules."""
+    executor = _read(EXECUTOR)
+    review_relay = executor.split("### Review-approval relay (manual mode)", 1)[
+        1
+    ].split("### Autopilot mode", 1)[0]
+
+    assert (
+        'Accept ONLY the exact standalone Manager answers "Approved for closure" or "Close task"'
+        in review_relay
+    )
+    assert (
+        "or either exact phrase as the answer value in an unmodified question-tool result"
+        in review_relay
+    )
+    assert '`User has answered your questions: "<question>"="<answer>"`' in review_relay
+    assert (
+        "when that result answers the immediately preceding relayed closure-approval question"
+        in review_relay
+    )
+    assert (
+        "Compare only the answer value, not the quoted question/header" in review_relay
+    )
+    assert (
+        "do not require the approval phrase to be the entire Hands message"
+        in review_relay
+    )
+    assert (
+        'The existing bare "approved" exception remains limited to the Manager\'s direct answer'
+        in review_relay
+    )
+
+
+def test_closure_answer_verbatim_forwarding_is_pinned():
+    executor = (REPO / "agents" / "cognitive-executor.md").read_text(encoding="utf-8")
+
+    assert (
+        "complete result envelope verbatim in a clearly labeled "
+        "`Question-tool answer (verbatim)` block" in executor
+    )
+    assert (
+        "Do not paraphrase, summarize, normalize, truncate, or strip the envelope"
+        in executor
+    )
+    assert (
+        "Keep the required mode line, full active task context, and the Brain "
+        "instruction outside the unchanged block" in executor
+    )
+
+
+def test_shipped_prompt_version_is_9_73_0():
+    prompt = _read_shipped_prompt_for_approval_contract()
+    assert "9.73.0" in prompt
+
+
 def test_assembler_output_matches_shipped(tmp_path):
     out = tmp_path / "check.md"
     proc = subprocess.run(
```
<!-- END_GIT_DIFF -->
