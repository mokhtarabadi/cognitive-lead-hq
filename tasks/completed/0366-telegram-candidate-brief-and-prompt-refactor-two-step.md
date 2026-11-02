# Task 0366: Telegram candidate brief and prompt-refactor two-step

**File:** `tasks/completed/0366-telegram-candidate-brief-and-prompt-refactor-two-step.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Submitted:** 2026-11-02T08:25:57Z
**Started:** 2026-11-02T08:06:13Z

## Goal

Enhance telegram candidate selection to show message briefs instead of bare IDs in the `question` tool, and enhance prompt-refactor skill into an explicit two-step Refactor-then-Execute workflow.

## Manager's Notes

Raw request (normalized): "Analyze telegram skill templates, learn them. The issue: when it shows me a list of candidate messages it shows me message IDs, but IDs are not visible in official Telegram apps so I don't understand which ID relates to which message. It is better it shows me the brief of each message instead of ID in `question` tool. Second: prompt-refactor when I load it — my prompt needs to pass two steps: first the agent enhances and fixes my prompt, then second executes the formatted XML prompt. Enhance it too. Task required. Autopilot lock."

Scope: `skill-templates/telegram-issue-sync/SKILL.md` Phase 2 approval UX plus `skill-templates/prompt-refactor/SKILL.md` workflow plus minimal mirror edits in prompt fragments. Autopilot locked.

## Local TODOs

- [x] Map telegram candidate selection UX and prompt-refactor current workflow
- [x] Implement brief-based candidate options (label/descriptions carry brief, ID stays machine value)
- [x] Implement prompt-refactor two-step Refactor-then-Execute workflow
- [x] Verify functionality

## Acceptance Criteria

- [x] Telegram candidate picker no longer asks Manager to provide bare message IDs; each option shows date/time sender plus first ~80 chars plus type/topic, ID kept as internal value only
- [x] Manual-mode fallback uses numbered brief list with server-side ID mapping
- [x] Prompt-refactor skill defines Step 1 enhance/fix and Step 2 execute formatted XML as live instruction with gate rules
- [x] Fragment callers mirror the two-step wording without scope creep

## Verification Evidence

- **Test command:** rtk test uvx pytest tests/test_prompt_sync.py -q
- **Expected result:** 22 shipped-prompt content gates pass, version in sync at 9.70.0
- **Actual result:** 22 passed in 0.22s; version 9.70.0 in fragment, test pin, and assembled prompt
- **Exit code:** 0

> Verification runner rule: `uvx pytest tests/test_prompt_sync.py -q` is the complete underlying test command. The first verification run used the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

Additional evidence: `python3 scripts/check_docs_sync.py` → `docs-sync: OK` (one warn-only pre-existing ORPHAN `scripts/release-9.66.0.sh`), exit 0. Risk greps (`auth|secret|migration|ledger|money|PII`, case-insensitive) hit only benign pre-existing mentions (skill registry entry, trigger-map pattern, prose examples); no high-risk surface. Bare-ID ask grep (`Provide the Message IDs|provide message IDs`) exits 1 (removed); `brief-first` 1 hit; `Two-Pass Refactor-then-Execute` 1 hit; `After Deliver, execute` hits in 05/executor/07/24 fragments. Stack skill skip: root `.`, marker scan list `go.mod, build.gradle.kts, Package.swift, pyproject.toml, package.json, nest-cli.json, vite.config, nuxt.config`, matched skills none, reason phrase no stack marker found for markdown task with python test gate only. lsp not applicable for markdown (reason phrase markdown only). `lint_task_file` runs in summary phase.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Low-medium. Skill wording changes only; risk is over-broad edits to unrelated fragments or breaking lint contract.
- **Rollback plan:** Revert skill-template edits via git worktree diff; task file remains as audit trail.

---

## Execution Log & Reasoning

**Input Corrections:** analyze, show, candidate, brief, need, enhance, formatted, execute. **Ambiguous terms:** None blocking. **Clarity Score:** 4/5.
Assumption A1: Telegram fix targets `skill-templates/telegram-issue-sync/SKILL.md` Phase 2 only; format/export skills display-only unless Brain plan says otherwise.
Assumption A2: Prompt-refactor Step 2 executes under existing gates (plan approval / ZAC / QA), no auto-bypass.
Mode: Autopilot locked for 0366.
Seat Check (pre-planning): domains are SOP wording + approval UX, no layout/dialog/theme/RTL/a11y trigger words in TITLE+BODY, no schema/contract/migration/quota/index/API-design trigger words, no flaky/race/deadlock/silent-fail/performance trigger words. UX-intent fallback does not fire (no user-visible surface named). Result: Architect seat minimum for SOP contract change; Designer/Programmer triggers miss stated explicitly.
Plan verdict (Brain planning turn, same task ID): REPORT plan received, no further discovery needed. Brainstorm: not required. Lite: not eligible, Tier T1 standard, full supervised autopilot with plan-approval pause. Seat routing: S1 Architect owns WHAT (this plan), S2 Senior Programmer owns HOW (implementation XML after approval), S3 QA adversarial on ID leakage/gate bypass, S4 Reviewer on lint/discipline/hygiene. Awaiting Manager approval (try 1 of 3) before requesting implementation XML.
Approval received: "Approved" (try 1 of 3, no edits). Requested Senior Programmer implementation XML via brain_turn (same task ID); XML_EXTRACTED received and Gatekeeper validation passed (no rule violations; allowlist respected, ZAC holds, no audit-agents touch).
Step 1 findings: anchors confirmed — F1 Phase 2 L92-98 verbatim `Provide the Message IDs` ask present; F2 L55-64 ends at Deliver with no Execute pass; F3 mirror anchor `05-user_input_processing.md:31` (Prompt Refactor Gate); F4 matrix row `agents/cognitive-executor.md:73` plus Direct Input section L80-87 plus Planning Gate L290; F5 registry `07-agent_skills_registry.md:16`; F6 `24-language_policy.md:11`. Memories applied: telegram-sync/message-formatting-contract, workflows/approval_gates_use_question_tool, project/fragment-edit-regenerate-workflow (edit fragment, bump 01-system_version.md, prettier, regenerate via assembler, verify version sync). Absent-File Policy: docs/architecture.md and docs/data_model.md do not exist, skipped.
⚠️ failure_report (Step 1 edge triggered, zero edits made): verifier `scripts/verify-templates.sh` is MISSING — `ls` confirms scripts/ holds only DECISIONS.md, README.md, check_docs_sync.py, prompt-build/, release-9.66.0.sh. `check_docs_sync.py` is not a valid substitute (it gates permission-denies vs docs table plus orphan scan, unrelated to template verification). Nearest candidate `tests/test_prompt_sync.py` gates shipped-prompt content but pins shipped version to 9.69.0, which collides with the mandatory version bump for fragment edits (memory workflow + AGENTS.md version rule) outside the XML allowlist F1-F8. Awaiting Brain adjudication on fallback verifier and version-bump scope before any edit.
D1 adjudication (Brain amended XML): halt was correct; allowlist extended to F9 `prompts/fragments/01-system_version.md` bump plus F10 `tests/test_prompt_sync.py` pinned-version-only update; fallback verifier `rtk test` on `tests/test_prompt_sync.py` plus `check_docs_sync.py` plus `lint_task_file` plus risk greps. D2: pin confirmed 9.69.0 at test line 47, bumped to 9.70.0 in fragment, test, and regenerated prompt (atomic, no other test logic touched). D3: `check_docs_sync.py` takes no args, exit 0 with one warn-only pre-existing ORPHAN line. D4: the amended XML bash commands dropped shell quotes around multi-word grep patterns; the corrected quoted forms were run instead (bare-ID removal proven exit 1, mirrors proven present). D5: no local `pytest` exists (no root pyproject), so the suite ran via `uvx pytest` under the `rtk test` prefix.
Implementation notes: Phase 2 now brief-first (label timestamp/sender/80 chars/type/topic, description full snippet plus audit ID, value numeric ID only, numbers-or-names-or-All closing, numbered manual fallback with same-turn server-side mapping, telegram-message-format contract cited). Prompt-refactor workflow is Two-Pass Refactor-then-Execute (Step 1 refactor keeps Step 0 corrections, enrichment, draft, refine; Step 2 executes under plan approval, ZAC, QA, closure gates, ambiguity halts to one question). One-line mirrors placed in 05 gate, executor matrix row plus Direct Input protocol, 07 registry, 24 execution binding. Prettier exit 0 (also normalized pre-existing indentation in 05/07 and the Phase 3 HTML example reflow in telegram-issue-sync; content unchanged). Assembler exit 0, 111596 bytes, version in sync. Sibling docs: ADR-004 (skill-templates), ADR-007 (fragments), executor delegation entry (agents). Diff stat shows only allowlisted files plus the three DECISIONS.md sync files plus generated system-prompt.md.
QA verdict (Brain QA Engineer turn, same task ID, diff attached): QA_PASSED. F1 ID transcription closed, F2 gate bypass closed, F3 version triple in sync (22 green, docs-sync OK), F4 prettier drift benign, F5 scope/hygiene clean. No additional unit test required. Ready for Code Reviewer.
Review verdict (Brain Code Reviewer turn, same task ID, diff attached): APPROVED technically, Status PO_REVIEW_PENDING. Strengths F1 brief-first picker, F2 two-pass bound to gates with no bypass, F3 version triple in sync, F4 scope/discipline clean, F5 shipped prompt rebuilt with changelog, no autonomous commit. No blocking issues, severity none. PO review of UX and business logic remains. Manager accept quote: "Approved for closure" (exact closure phrase, reply to relayed PO_REVIEW_PENDING question). Preconditions verified: file in tasks/qa, PO_REVIEW_PENDING in log. Requesting Senior Programmer closure XML via brain_turn (single issuance).
Closure 2026-11-02: moved tasks/qa → tasks/completed, Status closed, File header synced. QA_PASSED and reviewer APPROVED carried with zero rejections. Stack skill skip: root `.`, markers go.mod/build.gradle.kts/Package.swift/pyproject.toml/package.json/nest-cli.json/vite.config/nuxt.config, matched none, reason no stack marker found for markdown closure. lsp not applicable for markdown.

### Discovery-fed context

[fed-context]
- `skill-templates/telegram-issue-sync/SKILL.md` Phase 2 L92-98: candidate approval asks Manager to provide message IDs; per-candidate fields are Message ID + 200-char snippet + type + reply parent.
- Official Telegram apps never render internal numeric ID; Manager cannot join snippet to ID in-app, transcription error risks wrong sync anchor.
- `skill-templates/prompt-refactor/SKILL.md` L55-64: workflow ends at Deliver (output final prompt in code block); no Execute second pass exists in skill or callers (`05-user_input_processing.md:31`, executor matrix row).
- Memories applied: `telegram-sync/message-formatting-contract` (HTML formatting rules for any Telegram-facing text), `workflows/approval_gates_use_question_tool` (approval gates must use question tool).
- Absent-File Policy: `docs/architecture.md` and `docs/data_model.md` do not exist; skipped gracefully.
[/fed-context]

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 4070c5d..d906d87 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -34,6 +34,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Kanban gaps Phase 3: CFD + control chart (Task 0364):** Added `/api/cfd` and `/api/control-chart` endpoints (derived from task timestamps) and hand-rolled SVG views in the dashboard. CFD shows cumulative counts by lane; control chart shows cycle-time scatterplot with average and p50/p85/p95 lines.
 
+- **Brief-first Telegram candidate approval and two-pass prompt-refactor (Task 0366):** `telegram-issue-sync` Phase 2 no longer asks the Manager for bare numeric message IDs, which are invisible in official Telegram apps; each `question`-tool option now leads with a `[YYYY-MM-DD HH:MM] sender — first 80 chars (type/topic)` brief, the numeric ID stays the machine value only, and the manual fallback uses a numbered brief list with server-side number-to-ID mapping. The `prompt-refactor` skill is now an explicit two-pass workflow (Step 1 refactor, Step 2 execute the formatted prompt as the live instruction under plan approval, ZAC, QA, and closure gates), mirrored one-line in the input-processing gate, executor matrix and Direct Input protocol, skills registry, and language policy execution binding. `system-prompt.md` reassembled (`9.69.0` → `9.70.0`, test pin follows). The plan-referenced verifier `scripts/verify-templates.sh` does not exist; verification ran the adjudicated fallback (`test_prompt_sync.py` 22 green via `rtk test uvx pytest`, `check_docs_sync.py` OK). Docs: slice ADRs in `skill-templates`, `prompts/fragments`, and `agents`.
+
 ### Fixed
 
 - **Brain results are returned whole from Code Mode (Task 0354):** the executor's Code-mode output discipline told the Hands to return `{status, block_count: xml_blocks.length, model}`, a recipe meant to stop it printing a truncated prefix of a large XML block. The recipe instead licensed dropping the payload — turns returning only `output` lost `xml_blocks`, turns returning only `blocks` lost `output` — so the transcript and the agent's next turn held less than the server returned even though the executed instructions were complete. The rule now says a `brain_turn` result is evidence, not a preview: return `status`, `output`, `xml_blocks` and any diagnostic/`truncated` field exactly as received, never slice, map, summarize or field-shape it, and manage size before the call with `compact_context`, a leaner prompt or `include_bundle=false`. The runtime's `maxOutputBytes` remains the only acceptable cut and announces itself with `truncated: true`. Locked by a prompt-sync test that fails if the rule disappears or `block_count` returns; the live agent copy is byte-identical to the repo.
diff --git a/agents/DECISIONS.md b/agents/DECISIONS.md
index ce32165..91b15b8 100644
--- a/agents/DECISIONS.md
+++ b/agents/DECISIONS.md
@@ -83,3 +83,12 @@ Refs:
 - https://github.com/anomalyco/opencode/issues/54744
 - https://github.com/anomalyco/opencode/issues/52880
 - https://github.com/anomalyco/opencode/issues/49592
+
+## Prompt-refactor matrix row gains the execute pass
+
+Date: 2026-11-02
+Status: accepted
+Context: The Skill Auto-Loading Matrix bound prompt-refactor to validate-translate-expand-structure with no execute step, and the Direct Input pipeline ended at Plan & Halt, so a refactored prompt had no instruction carrying it into execution.
+Decision: Extend the matrix row to validate-translate-expand-structure-then-execute and add the After-Deliver execute sentence to the Direct Input protocol: the formatted prompt runs as the live instruction under plan approval, Zero-Autonomous-Commit, QA, and closure gates.
+Consequences: Refactor-then-execute is one bound pass; Step 2 cannot authorize commit or push.
+Rollback: Restore the prior matrix cell and drop the Direct Input sentence.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 4cc8d1b..04e1b95 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -70,7 +70,7 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 | Creating a new task file                                   | `task-generator`                                                                                                                             |
 | Closing or archiving a task                                | `archive-tasks`                                                                                                                              |
 | Complex bug, deadlock, silent failure                      | `debug-instrumentation`                                                                                                                      |
-| Implementation-producing input (any stack, any language)   | `prompt-refactor` (mandatory before planning: validate, translate, expand, then structure)                                                   |
+| Implementation-producing input (any stack, any language)   | `prompt-refactor` (mandatory before planning: validate, translate, expand, structure, then execute)                                          |
 | Java-8 Android Views, no Compose (XML layouts, Activities) | `android-kotlin` for Kotlin discipline plus tooling order only; Compose MVI Hilt SQLDelight coverage does not apply to Views (skip recorded) |
 | Plain Node CommonJS Cloud Code, no TS or hex ports         | `node-hexagonal-api` for layering intent where applicable, else no stack skill; no CommonJS Cloud Code skill exists (skip recorded)          |
 | Any Telegram MCP send, reply, edit, or file caption        | `telegram-message-format` (parse mode, escaping, length splitting, topic targeting, Persian text)                                            |
@@ -86,6 +86,7 @@ If the Manager sends you a direct message that is NOT an XML task block (e.g., "
 3. **Skill Loading:** Scan the request against the Skill Auto-Loading Matrix and load the relevant skills.
 4. **Plan & Halt:** Write a brief 3-step implementation plan and ask the Manager for explicit "Approved" before writing code.
 5. **ZAC Enforcement:** Remind the Manager that even for ad-hoc tasks, ZAC applies—you will not commit the changes.
+   After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
 
 ## Context Bootstrapping & Memory Protocol
 
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 9ed8492..1ecee0f 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.69.0</system_version>
\ No newline at end of file
+<system_version>9.70.0</system_version>
diff --git a/prompts/fragments/05-user_input_processing.md b/prompts/fragments/05-user_input_processing.md
index 880fe4c..44f4c04 100644
--- a/prompts/fragments/05-user_input_processing.md
+++ b/prompts/fragments/05-user_input_processing.md
@@ -2,15 +2,15 @@
 CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any action, you MUST execute this Automated Refactoring Pipeline internally:
 
 0. **Input Validation Gate:** Before ANY processing — including topic-shift detection — evaluate the raw input for:
-(a) Language detection — Is it English, non-English (any language), or mixed?
-(b) Typo/hallucination detection — Are there obvious misspellings or nonsensical words?
-(c) Clarity check — Can the core intent be identified with confidence?
-(d) Completeness check — Is there enough context to form a requirement?
+   (a) Language detection — Is it English, non-English (any language), or mixed?
+   (b) Typo/hallucination detection — Are there obvious misspellings or nonsensical words?
+   (c) Clarity check — Can the core intent be identified with confidence?
+   (d) Completeness check — Is there enough context to form a requirement?
 
-    If clarity check FAILS: HALT immediately. Output a clarification request in the per-message requested language. Do NOT proceed to any further processing.
-    If clarity check PASSES but typos detected: Note corrections in the reasoning_log, then proceed.
-    NEVER proceed to execution with an unvalidated input.
-    **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the per-message requested language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
+   If clarity check FAILS: HALT immediately. Output a clarification request in the per-message requested language. Do NOT proceed to any further processing.
+   If clarity check PASSES but typos detected: Note corrections in the reasoning_log, then proceed.
+   NEVER proceed to execution with an unvalidated input.
+   **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the per-message requested language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
 
 0.5. **Topic Shift Detection:** Only after the input passes the validation gate, compare the topic/domain of the current request against the active task context. If a shift is detected (e.g., from 'error localization' to 'deployment docs'), the Orchestrator MUST output a brief context-switch notice: 'Context Shift Detected: We are moving from [Topic A] to [Topic B]. The active task [XX] will be paused. Should I: (a) queue [Topic B] for after [Topic A] completes, or (b) start [Topic B] now and park [Topic A]?' This gives the Manager explicit control over context priority.
 
@@ -21,12 +21,13 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
 3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`. This trigger also runs on autopilot/XML planning turns, not only user-input processing.
 4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in the per-message requested language. See the language policy fragment for translation complexity gating (Brain-internal structured expansion for complex input, inline translation for short clear input; only Hands loads the prompt-refactor skill). **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Lite Mode Check:** Before proceeding to the full 9-step production line, evaluate the change request for complexity:
-    - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
-      (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
-      (b) Explicit Manager instruction to skip planning ("just do it", "quick fix", "no plan needed").
-      (c) Bug fixes where the root cause and fix are both obvious and verifiable within one file.
-    - **NOT eligible** (must use full workflow): Any change touching 2+ files, any new feature, any architectural change, any change with security/financial implications, or any ambiguous requirement.
-    - **If eligible:** Proceed directly to Step 5 (Implementation) of the `<execution_workflow>`. Document the Lite Mode justification in the task file.
-    - **If NOT eligible or uncertain:** Proceed to Step 1 (Smart Context Discovery).
-5.5. **Prompt Refactor Gate:** For any input that will result in an implementation task, the Orchestrator MUST apply its internal intent-shaping steps of validate, translate, expand, and structure. The Orchestrator (Brain) has no skill tool and never loads skills; only Hands (cognitive-executor) loads the full prompt-refactor skill via the skill tool when a task names it, per the Skill Auto-Loading Matrix which binds Hands only.
-</user_input_processing>
\ No newline at end of file
+   - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
+     (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
+     (b) Explicit Manager instruction to skip planning ("just do it", "quick fix", "no plan needed").
+     (c) Bug fixes where the root cause and fix are both obvious and verifiable within one file.
+   - **NOT eligible** (must use full workflow): Any change touching 2+ files, any new feature, any architectural change, any change with security/financial implications, or any ambiguous requirement.
+   - **If eligible:** Proceed directly to Step 5 (Implementation) of the `<execution_workflow>`. Document the Lite Mode justification in the task file.
+   - **If NOT eligible or uncertain:** Proceed to Step 1 (Smart Context Discovery).
+     5.5. **Prompt Refactor Gate:** For any input that will result in an implementation task, the Orchestrator MUST apply its internal intent-shaping steps of validate, translate, expand, and structure. The Orchestrator (Brain) has no skill tool and never loads skills; only Hands (cognitive-executor) loads the full prompt-refactor skill via the skill tool when a task names it, per the Skill Auto-Loading Matrix which binds Hands only.
+     After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
+     </user_input_processing>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index e95023d..134309d 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -13,7 +13,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **audit-agents**: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
 - **versioning-and-release**: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.
 - **debug-instrumentation**: Mandatory workflow for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
-- **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.
+- **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning. After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
 - **telegram-issue-sync**: Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.
 - **telegram-message-export**: Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.
 - **telegram-message-format**: Formats every outgoing Telegram MCP message so it renders cleanly in Telegram. Load before any send, reply, edit, or caption through the Telegram MCP — covers parse mode, HTML escaping, length splitting, forum-topic targeting, Persian text, and read-back verification.
@@ -42,5 +42,5 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-**Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
-</agent_skills_registry>
\ No newline at end of file
+  **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
+  </agent_skills_registry>
diff --git a/prompts/fragments/24-language_policy.md b/prompts/fragments/24-language_policy.md
index e16101c..fa47ac8 100644
--- a/prompts/fragments/24-language_policy.md
+++ b/prompts/fragments/24-language_policy.md
@@ -42,4 +42,5 @@ Plan gate accepts approved in any case through the question tool path. Closure a
 
 ## Execution Binding
 
-Translate first, then validate intent, expand requirements, check brainstorming, check clarification, check Lite Mode, and generate implementation tasks from the English version. Clarification questions use the per-message requested language. Implementation XML, tests, and evidence stay English.
\ No newline at end of file
+Translate first, then validate intent, expand requirements, check brainstorming, check clarification, check Lite Mode, and generate implementation tasks from the English version. Clarification questions use the per-message requested language. Implementation XML, tests, and evidence stay English.
+After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
diff --git a/prompts/fragments/DECISIONS.md b/prompts/fragments/DECISIONS.md
index 14eabdd..49d3eed 100644
--- a/prompts/fragments/DECISIONS.md
+++ b/prompts/fragments/DECISIONS.md
@@ -42,3 +42,10 @@
 - **Consequences:** Every tool the shipped prompt names resolves in the session. Version bumped with artifact regen.
 - **Rollback:** Revert the fragment wording and re-run the assembler.
 
+## [2026-11-02] ADR-007: Prompt-refactor becomes two-pass Refactor-then-Execute
+
+- **Context:** The prompt-refactor skill ended at Deliver (output the formatted prompt in a code block) with no Execute pass, so the refined prompt stalled as an artifact instead of running as the live instruction.
+- **Decision:** Retitle the workflow Two-Pass Refactor-then-Execute: Step 1 refactors (validate, translate, expand, structure), Step 2 executes the formatted prompt in the same session under the existing gates (plan approval, Zero-Autonomous-Commit, QA, closure). Mirror one-line execute clauses in the input-processing gate, the executor matrix and Direct Input protocol, the skills registry, and the language policy execution binding.
+- **Consequences:** Refined prompts execute instead of stalling; Step 2 cannot bypass gates, auto-commit, or push. Version bumped with artifact regen.
+- **Rollback:** Restore the four-step workflow wording, drop the mirror lines, and re-run the assembler.
+
diff --git a/skill-templates/DECISIONS.md b/skill-templates/DECISIONS.md
index f43cd27..3a75918 100644
--- a/skill-templates/DECISIONS.md
+++ b/skill-templates/DECISIONS.md
@@ -19,3 +19,10 @@
 - **Decision:** Remap to native tools: `write` creates the draft, `edit` makes every change, the `subagent` tool runs reader testing with a same-session fallback, and integrations resolve to MCP servers or pasted content. The three-stage workflow is unchanged.
 - **Consequences:** The skill now executes in OpenCode without translation. A registry test fails on any reintroduced Claude-centric term.
 - **Rollback:** Restore the prior SKILL.md from git history.
+
+## [2026-11-02] ADR-004: Brief-first candidate approval in telegram-issue-sync
+
+- **Context:** Phase 2 asked the Manager to reply with bare numeric message IDs, which are invisible in official Telegram apps, so the Manager could not join an ID to its message and risked syncing the wrong anchor.
+- **Decision:** Each `question`-tool option now leads with a brief ([YYYY-MM-DD HH:MM] sender — first 80 chars, type/topic); the numeric ID stays the machine value only, and the closing prompt asks for option numbers, names, or All, with a numbered-list manual fallback and server-side number-to-ID mapping.
+- **Consequences:** The Manager picks by visible brief instead of transcribing IDs; the sync registry still keys on numeric IDs.
+- **Rollback:** Restore the prior Phase 2 steps from git history.
diff --git a/skill-templates/prompt-refactor/SKILL.md b/skill-templates/prompt-refactor/SKILL.md
index 5a8278b..5313db8 100644
--- a/skill-templates/prompt-refactor/SKILL.md
+++ b/skill-templates/prompt-refactor/SKILL.md
@@ -48,20 +48,15 @@ Before translating or refactoring, scan the raw input for:
 3. **Ambiguity score** — Rate the input clarity from 1 to 5. If below 3, HALT and request clarification before proceeding.
 
 Output a brief correction note at the top of your response:
+
 > 📝 **Input Corrections:** [list of typos fixed, or "None"]
 > ⚠️ **Ambiguous terms:** [list of unclear words, or "None"]
 > 📊 **Clarity Score:** [1-5]
 
-## Workflow Execution
+## Workflow Execution (Two-Pass Refactor-then-Execute)
 
-1. **Bilingual Translation & Enrichment:** Read the Manager's raw prompt. If it is in a non-English language or informal English, seamlessly translate it into technical English. Identify the core goal, missing technical constraints, and desired outcome. Then ENRICH the translated intent:
-   - Add missing edge cases the Manager likely intended
-   - Add security implications if applicable
-   - Add architectural constraints if applicable
-   - Mark all enrichments as [INFERRED]
-2. **Draft:** Construct the prompt using the 5 XML blocks above.
-3. **Refine:** Ensure the language is highly authoritative, objective, and precise.
-4. **Deliver:** Output the final prompt inside a markdown code block.
+1. **Step 1 Refactor:** Validate the raw input, translate to technical English when needed, expand the intent, and structure the result into the constrained XML instruction using the 5 blocks above (role, system_context, agentic_reasoning, execution_rules/constraints, output_format). Keep the Step 0 correction note, the translate-then-enrich pass with [INFERRED] markings, and the draft and refine passes inside this step. Output the final prompt in a single code block, as Deliver does today.
+2. **Step 2 Execute:** Immediately execute the formatted prompt from Step 1 as the live instruction in the same session. Step 2 runs under the existing gates: plan approval via the `question` tool, Zero-Autonomous-Commit with no git add, commit, checkout, or push, QA and review loops, and closure only on the explicit approval phrase. Never bypass gates, never auto-commit, never push. If the Step 1 output is ambiguous, halt and ask one narrow question via the `question` tool before executing.
 
 ## Example Output Format
 
diff --git a/skill-templates/telegram-issue-sync/SKILL.md b/skill-templates/telegram-issue-sync/SKILL.md
index 5f90763..4aacfde 100644
--- a/skill-templates/telegram-issue-sync/SKILL.md
+++ b/skill-templates/telegram-issue-sync/SKILL.md
@@ -90,14 +90,9 @@ Every message this skill sends to Telegram MUST follow the `telegram-message-for
 ### Phase 2: Manager Approval
 
 1. Check the session capability manifest for the `question` tool first. If AVAILABLE, use it to present the identified candidates to the Manager. If UNAVAILABLE, do NOT silently skip this approval: relay the candidate list to the Manager as one message with the options inline and wait for the answer (manual mode), or record the replay-or-halt decision in the task file (autopilot mode).
-2. For each candidate, show:
-   - Message ID
-   - Snippet of the raw text (first 200 chars to identify it)
-   - Detected type (bug/feature/improve)
-   - Reply parent context (if any)
-3. Ask: _"Which of these candidates should be synced? (Provide the Message IDs, or state 'All')"_
-4. Also ask: _"Should GitHub issues be created for these? (yes/no)"_
-5. Only proceed with the approved candidates.
+2. Phase 2 Candidate approval with brief-first options. For each candidate capture timestamp, sender, first 200 characters of the raw text, detected type (bug/feature/improve), topic, reply parent context (if any), and the numeric message ID. Present one `question`-tool option per candidate. Each option label starts with the timestamp in YYYY-MM-DD HH:MM enclosed in square brackets, followed by the sender name, a dash, the first 80 characters single-line, plus type and topic in parentheses. Each option description holds the full 200-character snippet, the type, the reply parent, and the internal ID for audit. Each option machine value is the numeric ID only and the ID is never shown as primary text. Never ask the Manager for bare message IDs: the closing prompt asks the Manager to reply with option numbers, names, or All. Manual-mode fallback when the `question` tool is unavailable renders a numbered brief list with the same label text; the Manager replies with numbers and you map numbers to IDs server-side in the same turn via a lookup table built from the listed candidates. Re-read the table before syncing to prevent a wrong anchor. All Telegram-facing text obeys the `telegram-message-format` contract for HTML parse mode plus escaping plus no fences plus 4096 cap with splitting. Sync only approved IDs.
+3. Also ask: _"Should GitHub issues be created for these? (yes/no)"_
+4. Only proceed with the approved candidates. Log chosen IDs plus the mapping table in the task Execution Log.
 
 Store the Manager's GitHub preference in a variable `GH_ENABLED` (true/false).
 
@@ -294,9 +289,8 @@ Call `telegram_reply_to_message` with `parse_mode: "HTML"`, anchored to the **so
 ```html
 <b>Task synced</b>
 
-<b>File:</b> <code>tasks/backlog/{NEXT_ID}-title.md</code>
-<b>Issue:</b> <code>{GH_URL}</code>
-<b>Type:</b> {BUG|FEATURE|IMPROVE}
+<b>File:</b> <code>tasks/backlog/{NEXT_ID}-title.md</code> <b>Issue:</b>
+<code>{GH_URL}</code> <b>Type:</b> {BUG|FEATURE|IMPROVE}
 ```
 
 When the candidate is one of several in the same batch, add a leading line `<b>Task synced</b> (2 of 5)` so the Manager can match the reply to the message. If the payload would exceed ~3800 characters, split it into numbered parts, each a reply to the same parent id.
@@ -324,4 +318,4 @@ Task ready. Manager, please copy the contents of tasks/backlog/{NEXT_ID}-task.md
 | Codebase search misses context  | Three-pass search strategy (grep → glob → read) with fallback: if grep yields 0 results, broaden the search terms                                                                  |
 | State file has concurrent edits | Single-threaded Python updater script with atomic `json.dump` write                                                                                                                |
 | GitHub issue creation fails     | `GH_URL` gracefully defaults to `"Failed to create"`; the task file and Telegram reply still complete                                                                              |
-| Telegram reply renders broken   | The reply is sent with `parse_mode: "HTML"` and the `telegram-message-format` rules (escaping, no fences, no ZWNJ, length budget, topic anchoring)                             |
+| Telegram reply renders broken   | The reply is sent with `parse_mode: "HTML"` and the `telegram-message-format` rules (escaping, no fences, no ZWNJ, length budget, topic anchoring)                                 |
diff --git a/system-prompt.md b/system-prompt.md
index b6b2035..905d215 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.69.0</system_version>
+<system_version>9.70.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -21,15 +21,15 @@ The AI exists to maximize the successful, high-quality delivery of the current p
 CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any action, you MUST execute this Automated Refactoring Pipeline internally:
 
 0. **Input Validation Gate:** Before ANY processing — including topic-shift detection — evaluate the raw input for:
-(a) Language detection — Is it English, non-English (any language), or mixed?
-(b) Typo/hallucination detection — Are there obvious misspellings or nonsensical words?
-(c) Clarity check — Can the core intent be identified with confidence?
-(d) Completeness check — Is there enough context to form a requirement?
+   (a) Language detection — Is it English, non-English (any language), or mixed?
+   (b) Typo/hallucination detection — Are there obvious misspellings or nonsensical words?
+   (c) Clarity check — Can the core intent be identified with confidence?
+   (d) Completeness check — Is there enough context to form a requirement?
 
-    If clarity check FAILS: HALT immediately. Output a clarification request in the per-message requested language. Do NOT proceed to any further processing.
-    If clarity check PASSES but typos detected: Note corrections in the reasoning_log, then proceed.
-    NEVER proceed to execution with an unvalidated input.
-    **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the per-message requested language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
+   If clarity check FAILS: HALT immediately. Output a clarification request in the per-message requested language. Do NOT proceed to any further processing.
+   If clarity check PASSES but typos detected: Note corrections in the reasoning_log, then proceed.
+   NEVER proceed to execution with an unvalidated input.
+   **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the per-message requested language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
 
 0.5. **Topic Shift Detection:** Only after the input passes the validation gate, compare the topic/domain of the current request against the active task context. If a shift is detected (e.g., from 'error localization' to 'deployment docs'), the Orchestrator MUST output a brief context-switch notice: 'Context Shift Detected: We are moving from [Topic A] to [Topic B]. The active task [XX] will be paused. Should I: (a) queue [Topic B] for after [Topic A] completes, or (b) start [Topic B] now and park [Topic A]?' This gives the Manager explicit control over context priority.
 
@@ -40,14 +40,15 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
 3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`. This trigger also runs on autopilot/XML planning turns, not only user-input processing.
 4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in the per-message requested language. See the language policy fragment for translation complexity gating (Brain-internal structured expansion for complex input, inline translation for short clear input; only Hands loads the prompt-refactor skill). **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Lite Mode Check:** Before proceeding to the full 9-step production line, evaluate the change request for complexity:
-    - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
-      (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
-      (b) Explicit Manager instruction to skip planning ("just do it", "quick fix", "no plan needed").
-      (c) Bug fixes where the root cause and fix are both obvious and verifiable within one file.
-    - **NOT eligible** (must use full workflow): Any change touching 2+ files, any new feature, any architectural change, any change with security/financial implications, or any ambiguous requirement.
-    - **If eligible:** Proceed directly to Step 5 (Implementation) of the `<execution_workflow>`. Document the Lite Mode justification in the task file.
-    - **If NOT eligible or uncertain:** Proceed to Step 1 (Smart Context Discovery).
-5.5. **Prompt Refactor Gate:** For any input that will result in an implementation task, the Orchestrator MUST apply its internal intent-shaping steps of validate, translate, expand, and structure. The Orchestrator (Brain) has no skill tool and never loads skills; only Hands (cognitive-executor) loads the full prompt-refactor skill via the skill tool when a task names it, per the Skill Auto-Loading Matrix which binds Hands only.
+   - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
+     (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
+     (b) Explicit Manager instruction to skip planning ("just do it", "quick fix", "no plan needed").
+     (c) Bug fixes where the root cause and fix are both obvious and verifiable within one file.
+   - **NOT eligible** (must use full workflow): Any change touching 2+ files, any new feature, any architectural change, any change with security/financial implications, or any ambiguous requirement.
+   - **If eligible:** Proceed directly to Step 5 (Implementation) of the `<execution_workflow>`. Document the Lite Mode justification in the task file.
+   - **If NOT eligible or uncertain:** Proceed to Step 1 (Smart Context Discovery).
+     5.5. **Prompt Refactor Gate:** For any input that will result in an implementation task, the Orchestrator MUST apply its internal intent-shaping steps of validate, translate, expand, and structure. The Orchestrator (Brain) has no skill tool and never loads skills; only Hands (cognitive-executor) loads the full prompt-refactor skill via the skill tool when a task names it, per the Skill Auto-Loading Matrix which binds Hands only.
+     After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
 </user_input_processing>
 
 <personas>
@@ -130,7 +131,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **audit-agents**: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
 - **versioning-and-release**: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.
 - **debug-instrumentation**: Mandatory workflow for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
-- **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.
+- **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning. After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
 - **telegram-issue-sync**: Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.
 - **telegram-message-export**: Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.
 - **telegram-message-format**: Formats every outgoing Telegram MCP message so it renders cleanly in Telegram. Load before any send, reply, edit, or caption through the Telegram MCP — covers parse mode, HTML escaping, length splitting, forum-topic targeting, Persian text, and read-back verification.
@@ -159,7 +160,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-**Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
+  **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
 </agent_skills_registry>
 
 <agentic_reasoning>
@@ -827,3 +828,4 @@ Plan gate accepts approved in any case through the question tool path. Closure a
 ## Execution Binding
 
 Translate first, then validate intent, expand requirements, check brainstorming, check clarification, check Lite Mode, and generate implementation tasks from the English version. Clarification questions use the per-message requested language. Implementation XML, tests, and evidence stay English.
+After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index f1c1954..309f33a 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.69.0"
+    assert shipped == "9.70.0"
 
 
 def test_parallel_mandate_covers_implementation_triggers():
```
<!-- END_GIT_DIFF -->
