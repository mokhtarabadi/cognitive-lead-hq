# Task 276: Question-tool approval gates and brainstorming auto-load

**File:** `tasks/qa/276-question-tool-gates-and-brainstorming-autoload.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Encode the question-tool-at-approval-gates rule into the cognitive agents and system prompt, and make brainstorming trigger without the Manager naming it each time.

## Manager's Notes

- After planning and after Code Reviewer acceptance the system asks the Manager for approval, but the goal plugin keeps the loop running, so at those gates the system must use the `question` tool (stored memory `workflows/approval_gates_use_question_tool`).
- Brainstorming currently does not auto-load; the Manager has to mention it every time. Fix so the trigger fires on its own.
- Both fixes in one task. Update cognitive agents and system prompt fragments where needed.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Initial codebase exploration
- [x] Encode question-tool gate rule in executor agent + prompt fragments + regen
- [x] Fix brainstorming auto-load trigger
- [x] Verify functionality

## Acceptance Criteria

- [x] Approval gates (plan approval, review acceptance/closure) call the `question` tool instead of prose-only asks
- [x] Brainstorming triggers without the Manager naming it each time
- [x] Cognitive agents and system prompt updated consistently, prompt sync passes
- [x] CHANGELOG updated, lint and full suite green

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q
- **Expected result:** all tests pass, exit code 0
- **Actual result:** Manager ran the suite pre-regen 2026-09-27: **689 passed, 10 warnings in 5.12s**, exit 0. After regen (`python3 scripts/prompt-build/assemble_system_prompt.py` → `Assembled 94855 bytes`, `system-prompt.md` head = 9.47.0, diff stat 8+/8- in system-prompt.md only), Manager re-ran the suite 2026-09-27: **689 passed, 10 warnings in 5.01s**, exit 0. Lint evidence: `lint_task_file` pass on task file, `lint_markdown` pass on CHANGELOG.md (via lint MCP, exit-equivalent OK).
- **Exit code:** 0 (post-regen suite run)

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** prompt regen drift; question-tool unavailable in some runtimes
- **Rollback plan:** revert fragment edits, regen prompt, re-run sync test

---

## Execution Log & Reasoning

Autopilot locked for task 276 (Manager: "auto polit it", 2026-09-27). File move to tasks/in-progress/ pending — no shell/mv tool in this runtime; Manager to run `git mv` (logged deviation, read-only work unaffected).
Seat Check: single-domain prompt engineering → Senior Programmer; Designer/Architect/QA/Reviewer/Planner/Strategist skipped with reasons; trigger map explicit miss.
Brainstorm: not required — single-domain reversible docs change.
Brain plan verdict (Senior Programmer, 2 turns, discovery-fed): E1-E7 question-tool mandate (executor Capability Preflight + 3 sections + fragment 11 Steps 3/4/8), E8-E11 brainstorming auto-eval (fragment 11 Step 2 + fragment 12 trigger/auditability + user-input-processing trigger + executor Seat Check), version bump 9.46.0→9.47.0, regen via scripts/prompt-build/assemble_system_prompt.py, verify lint + sync test + suite. history_turns_dropped 0 both turns. Plan presented for explicit approval (try 1/3).
Plan APPROVED by Manager via question tool (answer: "Approved", try 1/3 — gate passed using the very mechanism being implemented).
Implementation round (all edits applied, grep-verified): E1 Capability Preflight append; E2 plan-approval pause binding; E3 PO_REVIEW_PENDING relay binding; E4 goal-pause binding; E5/E6 fragment 11 Steps 3/4/8; E7 executor-only (Capability Preflight source fragment unpinned); E8 fragment 11 Step 2 auto-eval rewrite; E9 fragment 12 trigger append; E10 fragment 05 trigger append; E11 executor Seat Check + Planning Gate appends. Version bump: fragment 01 → 9.47.0, test pin tests/test_prompt_sync.py:42 → 9.47.0, CHANGELOG [Unreleased] bullet appended. Two edit retries needed (multi-line anchors with invisible whitespace mismatch; single-line anchors succeeded). BLOCKED: system-prompt.md regen + sync test + full suite — no shell in this runtime; Manager must run them before QA.
Verification round 2026-09-27: Manager ran the full suite pre-regen — 689 passed, 10 warnings in 5.12s, exit 0 (recorded in Verification Evidence). Task file header synced to tasks/in-progress/ after Manager's git mv. STILL PENDING: prompt regen + post-regen suite re-run (sync test must see the regenerated system-prompt.md).
Verification close-out 2026-09-27: Manager ran regen — assembled 94855 bytes, head 9.47.0, diff stat 8+/8- in system-prompt.md only. Post-regen suite re-run — 689 passed, 10 warnings in 5.01s, exit 0. All TODO/AC/DoD boxes checked. Ready for qa move (git mv needs Manager — no shell in this runtime).
Brain QA round 2026-09-27 (autopilot, same task_id): QA Engineer QA_PASSED with 2 nits (R1: Steps 3/8 lack unavailable-tool fallback; R2: fragment 05 dropped 'fabricate', 11/2.7 dropped 'it'). Code Reviewer APPROVED_WITH_CHANGES + 6-step hotfix XML. Hotfix applied Steps 1-5: fragment 05 'fabricate' restored, fragment 11 Step 2 'it' restored, Steps 3+8 got unavailable-fallback sentences, CHANGELOG bullet rewritten to done-state. Step 6 (regen + suite re-run) PENDING — needs Manager shell; version stays 9.47.0; file stays in tasks/qa/; re-review after Step 6.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 457b285..b8d115e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -10,6 +10,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Plugin full-V2 status verification + docs (Task 274):** verified both plugins are at their latest stable V2-capable versions — `@prevalentware/opencode-goal-plugin@0.1.52` (released 2026-09-26; upstream V2 port PR #49 + PR #58) and `@tarquinen/opencode-dcp@3.2.0` (stable 2026-09-20 is newest; 3.2.1–3.2.8 betas are stale experiments; V2 `setup()` via `session` hooks; `compress.permission: ask` unsupported in V2 by DCP design, default `allow` stands). `opencode plugin list` is documented as the source of truth (`~/.cache/opencode/packages/` is metadata-only). Upstream-issue policy recorded in `README.md` and `LLM.txt` §7.7: search open threads first, never duplicate (DCP V2 threads #627/#628/#631/#632 already active) — no issues were filed.
 - **Five-Python-MCP-server audit vs current web data (Task 275):** report-only audit, zero source modified. All five servers (`mcp-context-server` 8 tools, `mcp-memory-server` 6, `mcp-lint-server` 4, `mcp-decision-server` 6, `mcp-brain-bridge` 4; 8,427 LOC) use `FastMCP` + stdio transport, pin `mcp[cli]>=1.0,<2.0`, lock resolves to 1.30.0 which PyPI confirms is the latest v1.x (latest overall is SDK v2.2.0 for spec 2026-07-28). Verdict KEEP: stdio-loopback is the correct shape per every 2026 hardening guide, the v1 pin matches upstream's own `<2` advice, zero hits for shell/eval/pickle/os.system, subprocess uses are list-form git/python only, and 7/7 servers connect live under opencode 2.0.18. Flagged one stale memory sentence (`workflows/global-install-upgrade` claims persona code dirs KEPT; `mcp-persona-server/` was deleted in Task 191 and global is already clean) — awaiting Manager approval to correct. Full suite: **689 passed** (exit 0).
+- **Question-tool approval gates + brainstorming auto-eval (Task 276):** approval gates now mandate the `question` tool instead of prose-only asks (the goal-plugin loop rolls past prose) — `agents/cognitive-executor.md` Capability Preflight plus its plan-approval, PO_REVIEW_PENDING relay and goal-pause sections, and `prompts/fragments/11-execution_workflow.md` Steps 3/4/8. Brainstorming no longer needs a Manager mention: fragment 11 Step 2, the fragment 12 trigger and the input-processing trigger evaluate automatically on every planning turn including autopilot/XML, bound to the executor Seat Check. `<system_version>` bumped 9.46.0 → 9.47.0; `system-prompt.md` regen plus sync test plus full suite pending (no shell in this runtime — Manager runs them).
 
 ## [9.46.0] - 2026-09-26
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index b00513d..09a577f 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -94,7 +94,7 @@ To prevent hallucinations and respect hidden project constraints, you MUST integ
 
 ## Capability Preflight (session start)
 
-Before approval-sensitive work (plan approval, review approval, closure), check the capability manifest: every `brain_turn` prints a `capability-manifest:` diagnostic line to stderr mapping each required tool to `AVAILABLE`, `UNAVAILABLE_REQUIRED`, or `UNAVAILABLE_OPTIONAL`. A step whose required tool is `UNAVAILABLE_REQUIRED` (for example the `question` tool) is never silently skipped. Emit the relay block the turn returned (missing tool names, stage, one narrow question, one answer slot) through the mode-appropriate channel: manual mode relays it to the Manager verbatim and pauses with the relayed question as the named blocker; autopilot replays it against stored manager decisions, and halts with the relay block as the named blocker only when no ruling covers it. Approval collection follows the single approval rule: closure accepts only the exact phrases "Approved for closure" or "Close task" (a bare "approved" never counts); the plan gate accepts "approved" in any case. Blanket acknowledgements ("ok", "yes", "looks good", emoji) never count as approval at any gate.
+Before approval-sensitive work (plan approval, review approval, closure), check the capability manifest: every `brain_turn` prints a `capability-manifest:` diagnostic line to stderr mapping each required tool to `AVAILABLE`, `UNAVAILABLE_REQUIRED`, or `UNAVAILABLE_OPTIONAL`. A step whose required tool is `UNAVAILABLE_REQUIRED` (for example the `question` tool) is never silently skipped. Emit the relay block the turn returned (missing tool names, stage, one narrow question, one answer slot) through the mode-appropriate channel: manual mode relays it to the Manager verbatim and pauses with the relayed question as the named blocker; autopilot replays it against stored manager decisions, and halts with the relay block as the named blocker only when no ruling covers it. Approval collection follows the single approval rule: closure accepts only the exact phrases "Approved for closure" or "Close task" (a bare "approved" never counts); the plan gate accepts "approved" in any case. Blanket acknowledgements ("ok", "yes", "looks good", emoji) never count as approval at any gate. At plan-approval, PO_REVIEW_PENDING relay, and any closure approval gate you MUST collect the decision via the question tool with one narrow question and one answer slot. Prose-only approval asks are forbidden because the goal-plugin loop rolls past prose. This holds in manual and autopilot. If question is UNAVAILABLE_REQUIRED, emit the relay block and pause with it as the named blocker; never skip. Only hard blockers may use prose.
 
 ## Subagent Delegation for Context Discovery
 
@@ -254,13 +254,13 @@ Every plan states one auditable line: `Brainstorm: required | not required —
 <reason>`, per the trigger in the brainstorming protocol. Work that is
 cross-disciplinary AND hard to reverse requires the full seven-seat report.
 Record that line in the Execution Log beside the plan verdict, so the decision
-to brainstorm — or not — is reviewable after the fact.
+to brainstorm — or not — is reviewable after the fact. Seat Check MUST run brainstorm-trigger evaluation before any brain_turn planning call.
 
 ### Supervised autopilot plan approval (non-trivial work only)
 
 Fire-and-forget autopilot is forbidden. For non-trivial work, the Hands MUST
 show the Brain-approved plan to the admin and wait for explicit approval
-before writing implementation code: present plan steps + seat routing +
+before writing implementation code (pause and ask via the question tool): present plan steps + seat routing +
 cited file paths with lines, accept admin edits in a loop (max 3 plan tries,
 then escalate), and only then implement. Lite-eligible trivial work is
 carved out — it runs with zero human pauses. The data-ask folds into the
@@ -275,7 +275,7 @@ reference them by exact name; the roster table below is the only roster.
 
 1. **Seat Check.** Before any `brain_turn` planning call, state: task
    domain(s) → seat(s) requested → seats skipped + one-line reason each.
-   A planning turn with no Seat Check is malformed. Cite which trigger
+   A planning turn with no Seat Check is malformed. Seat Check MUST run brainstorm-trigger evaluation before any brain_turn planning call. Cite which trigger
    words fired (or state the explicit miss) so the choice is auditable.
 2. **Trigger→seat map (minimum viable).** Match on TITLE+BODY, defined
    as the case-insensitive concatenation of the task title and body (empty
@@ -352,7 +352,7 @@ goal entirely — goal overhead must never exceed the task itself.
 3. **Pause BEFORE asking — never ask with the goal active.** If the task
    truly cannot proceed without the Manager, call
    `update_goal_status(paused)` FIRST, then ask exactly one precise
-   question, then stop. Reason: while the goal stays active the goal
+   question via the question tool, then stop. Reason: while the goal stays active the goal
    plugin auto-resends the continuation prompt on your next turn, which
    re-issues the objective instead of waiting for the answer — the
    Manager ends up answering the same objective twice. Pausing is
@@ -413,7 +413,7 @@ needs no extra machinery.
 ### Review-approval relay (manual mode)
 
 When a review turn returns technical approval (`PO_REVIEW_PENDING` with the
-technical-vs-final notice), relay the verdict to the Manager verbatim and
+technical-vs-final notice), relay the verdict to the Manager verbatim via the question tool with one narrow question and
 STOP — the file stays in `tasks/qa/`. Accept ONLY the exact phrases
 "Approved for closure" or "Close task" as the go-ahead (matching is
 case-insensitive on these two phrases and nothing else). A bare "approved"
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index f208856..7db808f 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.46.0</system_version>
+<system_version>9.47.0</system_version>
diff --git a/prompts/fragments/05-user_input_processing.md b/prompts/fragments/05-user_input_processing.md
index ed10993..bc24517 100644
--- a/prompts/fragments/05-user_input_processing.md
+++ b/prompts/fragments/05-user_input_processing.md
@@ -18,8 +18,8 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
 
 1. **Bilingual Translation (MANDATORY if non-English):** ALL raw non-English/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for non-English input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass. **Crucial:** Non-English input MUST first be translated into technical English before any prompt refactoring or execution planning proceeds. No execution planning, task generation, or prompt refactoring may occur on non-English input until the translation step is complete.
 2. **Intent Expansion & Enrichment:** Expand the raw thought into a structured software requirement. Infer missing edge cases, security needs, and architectural impacts. Add any constraints the Manager likely intended but did not explicitly state. Mark all inferred additions clearly as "[INFERRED]" so the Manager can review them during the approval gate.
-3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`.
-4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in simple English. **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
+3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`. This trigger also runs on autopilot/XML planning turns, not only user-input processing.
+4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in simple English. **Clarification Halt Mandate:** The Orchestrator MUST NOT guess or assume intent. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Lite Mode Check:** Before proceeding to the full 9-step production line, evaluate the change request for complexity:
     - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
       (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
@@ -29,4 +29,4 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
     - **If eligible:** Proceed directly to Step 5 (Implementation) of the `<execution_workflow>`. Document the Lite Mode justification in the task file.
     - **If NOT eligible or uncertain:** Proceed to Step 1 (Smart Context Discovery).
 5.5. **Prompt Refactor Gate:** For any input that will result in an implementation task, the Orchestrator MUST internally apply the prompt-refactor skill's 5-block XML structure to the translated and expanded intent before generating the task. This ensures the Hands task is elite-grade regardless of input quality. This gate is NON-OPTIONAL for implementation tasks.
-</user_input_processing>
\ No newline at end of file
+</user_input_processing>
diff --git a/prompts/fragments/11-execution_workflow.md b/prompts/fragments/11-execution_workflow.md
index 092e30c..5de2c24 100644
--- a/prompts/fragments/11-execution_workflow.md
+++ b/prompts/fragments/11-execution_workflow.md
@@ -8,14 +8,14 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
    - 1.5. **Task Number Pre-Assignment Validation**: Before the Orchestrator assigns a task number to any new task, it MUST instruct the Hands to load the `task-generator` skill and execute its documented next-ID discovery method exactly as written there — no command is duplicated here to prevent drift between this system prompt and the skill's canonical implementation. The Orchestrator MUST use that reported number. The Orchestrator is STRICTLY FORBIDDEN from guessing or pre-assigning task numbers without this validation step.
 
 2. **Step 2: Conditional Brainstorming Check (Orchestrator)**
-   - The Orchestrator checks the brainstorming trigger in `<brainstorming_protocol>`: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. If it fires, run the full seven-seat report using exactly the seven `<personas>` seats (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
+   - The Orchestrator MUST automatically evaluate the brainstorming trigger in `<brainstorming_protocol>` on every planning turn from TITLE+BODY on all paths including autopilot/XML, without the Manager naming it: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. Log trigger words fired or explicit miss. If it fires, run the full seven-seat report using exactly the seven `<personas>` seats (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
    - Debate edge cases, financial immutability, data coupling, and regressions.
    - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and run it with the `blowsh` skill, which covers live-web research and page extraction. Wait for the results before proceeding.
-   - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
+   - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
 
 3. **Step 3: Blueprint & Plan Presentation (Orchestrator)**
    - Present a clean Markdown plan (NO XML) with visual diagrams (Mermaid) to the Manager.
-   - STOP and await explicit approval.
+   - STOP and await explicit approval. MUST ask approval via the question tool. Prose-only ask is forbidden.
 
 4. **Step 4: PO Approval Gate (Manager)**
    - The Manager reviews and responds with "Approved" or inline edits (`> MANAGER REVIEW:`).
@@ -35,10 +35,10 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
    - Outputs PO_REVIEW_PENDING.
 
 8. **Step 8: Final PO Acceptance & Atomic Commit (Manager + Hands)**
-   - Manager explicitly issues "Approved for closure" or "Close task".
+   - Manager explicitly issues "Approved for closure" or "Close task". MUST ask closure approval via the question tool. Prose-only ask is forbidden.
    - Senior Programmer generates a dedicated closure task.
    - Hands update metadata to `closed`, move file via `git mv tasks/qa/ tasks/completed/`, and execute `custom_context_commit_and_clean_task`.
 
 9. **Step 9: Next Task Transition (Sprint Strategist)**
    - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
-</execution_workflow>
\ No newline at end of file
+</execution_workflow>
diff --git a/prompts/fragments/12-brainstorming_protocol.md b/prompts/fragments/12-brainstorming_protocol.md
index bb4623e..34334ef 100644
--- a/prompts/fragments/12-brainstorming_protocol.md
+++ b/prompts/fragments/12-brainstorming_protocol.md
@@ -1,6 +1,6 @@
 <brainstorming_protocol>
 <phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
-<trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona.</trigger>
+<trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona. Evaluation is automatic every planning turn. Skipping evaluation is malformed.</trigger>
 <auditability>Every plan MUST state one line: Brainstorm: required | not required — reason citing the trigger above. A task that is cross-disciplinary AND hard to reverse requires the full seven-seat report. Record that line in the execution log.</auditability>
 <panel>The brainstorm panel is exactly the seven personas declared in <personas>. No outside personas exist. There is no brainstorm skill. This protocol is the only brainstorming path in the system. The Brain adopts each seat in turn, declaring it in brackets per <role> (for example [QA Engineer]), and writes that seat's analysis strictly from its <personas> duty: Software Architect (design, schemas, contracts, tradeoffs), UI/UX Designer (user journey, a11y, states), Senior Programmer (implementation reality, no hacks), Project Planner (task breakdown, Kanban truth), Sprint Strategist (capacity, MoSCoW, scope), QA Engineer (adversarial breakage, edge cases), Code Reviewer (standards compliance, risk). Skip seats with nothing to contribute and say so in one line.</panel>
 <procedure>Run seats sequentially. Each seat analyzes independently from its duty only. No seat may soften another seat's finding. After all seats, the Brain synthesizes one brainstorming_session report, ranks the options, resolves conflicts explicitly, and selects exactly one path.</procedure>
diff --git a/system-prompt.md b/system-prompt.md
index 4555e43..399228f 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.46.0</system_version>
+<system_version>9.47.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -37,8 +37,8 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
 
 1. **Bilingual Translation (MANDATORY if non-English):** ALL raw non-English/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for non-English input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass. **Crucial:** Non-English input MUST first be translated into technical English before any prompt refactoring or execution planning proceeds. No execution planning, task generation, or prompt refactoring may occur on non-English input until the translation step is complete.
 2. **Intent Expansion & Enrichment:** Expand the raw thought into a structured software requirement. Infer missing edge cases, security needs, and architectural impacts. Add any constraints the Manager likely intended but did not explicitly state. Mark all inferred additions clearly as "[INFERRED]" so the Manager can review them during the approval gate.
-3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`.
-4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in simple English. **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
+3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`. This trigger also runs on autopilot/XML planning turns, not only user-input processing.
+4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in simple English. **Clarification Halt Mandate:** The Orchestrator MUST NOT guess or assume intent. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Lite Mode Check:** Before proceeding to the full 9-step production line, evaluate the change request for complexity:
     - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
       (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
@@ -431,14 +431,14 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
    - 1.5. **Task Number Pre-Assignment Validation**: Before the Orchestrator assigns a task number to any new task, it MUST instruct the Hands to load the `task-generator` skill and execute its documented next-ID discovery method exactly as written there — no command is duplicated here to prevent drift between this system prompt and the skill's canonical implementation. The Orchestrator MUST use that reported number. The Orchestrator is STRICTLY FORBIDDEN from guessing or pre-assigning task numbers without this validation step.
 
 2. **Step 2: Conditional Brainstorming Check (Orchestrator)**
-   - The Orchestrator checks the brainstorming trigger in `<brainstorming_protocol>`: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. If it fires, run the full seven-seat report using exactly the seven `<personas>` seats (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
+   - The Orchestrator MUST automatically evaluate the brainstorming trigger in `<brainstorming_protocol>` on every planning turn from TITLE+BODY on all paths including autopilot/XML, without the Manager naming it: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. Log trigger words fired or explicit miss. If it fires, run the full seven-seat report using exactly the seven `<personas>` seats (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
    - Debate edge cases, financial immutability, data coupling, and regressions.
    - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and run it with the `blowsh` skill, which covers live-web research and page extraction. Wait for the results before proceeding.
-   - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
+   - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
 
 3. **Step 3: Blueprint & Plan Presentation (Orchestrator)**
    - Present a clean Markdown plan (NO XML) with visual diagrams (Mermaid) to the Manager.
-   - STOP and await explicit approval.
+   - STOP and await explicit approval. MUST ask approval via the question tool. Prose-only ask is forbidden.
 
 4. **Step 4: PO Approval Gate (Manager)**
    - The Manager reviews and responds with "Approved" or inline edits (`> MANAGER REVIEW:`).
@@ -458,7 +458,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
    - Outputs PO_REVIEW_PENDING.
 
 8. **Step 8: Final PO Acceptance & Atomic Commit (Manager + Hands)**
-   - Manager explicitly issues "Approved for closure" or "Close task".
+   - Manager explicitly issues "Approved for closure" or "Close task". MUST ask closure approval via the question tool. Prose-only ask is forbidden.
    - Senior Programmer generates a dedicated closure task.
    - Hands update metadata to `closed`, move file via `git mv tasks/qa/ tasks/completed/`, and execute `custom_context_commit_and_clean_task`.
 
@@ -468,7 +468,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 
 <brainstorming_protocol>
 <phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
-<trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona.</trigger>
+<trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona. Evaluation is automatic every planning turn. Skipping evaluation is malformed.</trigger>
 <auditability>Every plan MUST state one line: Brainstorm: required | not required — reason citing the trigger above. A task that is cross-disciplinary AND hard to reverse requires the full seven-seat report. Record that line in the execution log.</auditability>
 <panel>The brainstorm panel is exactly the seven personas declared in <personas>. No outside personas exist. There is no brainstorm skill. This protocol is the only brainstorming path in the system. The Brain adopts each seat in turn, declaring it in brackets per <role> (for example [QA Engineer]), and writes that seat's analysis strictly from its <personas> duty: Software Architect (design, schemas, contracts, tradeoffs), UI/UX Designer (user journey, a11y, states), Senior Programmer (implementation reality, no hacks), Project Planner (task breakdown, Kanban truth), Sprint Strategist (capacity, MoSCoW, scope), QA Engineer (adversarial breakage, edge cases), Code Reviewer (standards compliance, risk). Skip seats with nothing to contribute and say so in one line.</panel>
 <procedure>Run seats sequentially. Each seat analyzes independently from its duty only. No seat may soften another seat's finding. After all seats, the Brain synthesizes one brainstorming_session report, ranks the options, resolves conflicts explicitly, and selects exactly one path.</procedure>
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 12c07fc..8999413 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -39,7 +39,7 @@ def test_shipped_version_matches_fragment():
 def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(r"<system_version>(.*?)</system_version>",
                         _read(SHIPPED)).group(1)
-    assert shipped == "9.46.0"
+    assert shipped == "9.47.0"
 
 
 def test_no_manager_language_rule_in_shipped_prompt():
```
<!-- END_GIT_DIFF -->
