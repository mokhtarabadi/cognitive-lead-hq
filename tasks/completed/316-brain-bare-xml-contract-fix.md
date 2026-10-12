# Task 316: Brain dual-mode XML contract fix

**File:** `tasks/qa/316-brain-bare-xml-contract-fix.md`
**Source:** manager
**Type:** bug
**Status:** open

## Goal

Fix fenced-XML reject loop with a dual-mode contract: fenced XML forced in manual copy-paste mode, bare unfenced XML in automatic mode, with the bridge extracting both cleanly.

## Manager's Notes

Manager order (translated): define a task and handle it automatically without Brain planning. Simplify Brain handling. We know which XML may be created in the system prompt. Extract XML cleanly. Fix the reported bug with minimal simple changes. Build the task, fix it, inject changes and explanations into the task file, prepare for QA. Plan approval: Manager words are the plan. Brainstorm: not required — single-domain prompt/bridge contract fix, fully reversible via versioned fragments.

Revision order (translated): rejected the bare-only change. Manual mode needs the fence, forced, for easy copy-paste. Automatic mode (OpenCode via MCP brain server) must have fencing disabled. Revise the task per these notes. Graph: mcp-brain-bridge 152 nodes, 155 links; MODE declared in 19-initialization (manual ferries, automatic chains brain_turn); bridge extraction currently mode-blind.

## Local TODOs

- [x] Dual-mode prompt contract (manual fenced, automatic bare)
- [x] Bridge extracts both bare and fenced allowlisted XML
- [x] Bump version, regenerate artifact, sync docs and tests
- [x] Verify with RTK tests and lint gates

## Acceptance Criteria

- [x] Manual mode forces fenced XML for one-click copy-paste
- [x] Automatic mode emits bare unfenced XML with no fences
- [x] Bridge extracts both shapes; no re-emit loop in either mode
- [x] Version bumped, artifact regenerated in sync, runbook accurate

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q
- **Expected result:** all tests pass, exit 0, fence-fallback extraction covered
- **Actual result:** 277 passed; lint_system_prompt_sync in sync; lint_task_file passed pre-staging
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Fragment edit breaks prompt assembly or version sync check.
- **Rollback plan:** Revert fragments plus regenerated artifact to prior version header via git checkout of those paths only, re-run assembler.

---

## Execution Log & Reasoning

Root cause: Senior Programmer persona instructed fenced ```xml output for human copy-paste while the bridge fail-closed strict gate (Task 305 C1) strips fences then rejects fenced allowlisted XML with XML_STRICT_REJECT_FENCE_FALLBACK, returning REPORT with empty xml_blocks. First review turn showed debug fenced_blocks 1, so OpenCode had nothing to execute; the lean bare re-emit succeeded as XML_EXTRACTED. Bridge behavior is intentional safety (never execute documentation examples); the bug is the contradictory prompt plus stale runbook lenient-fence text. Fix keeps the bridge unchanged (zero test churn across 277 tests) and corrects the contract at the source: bare unfenced raw XML in Programmer, QA hotfix, and Reviewer postfix personas, version 9.58.0 to 9.58.1 with regenerated artifact, runbook corrected to fail-closed. Graph: 152 nodes, 155 links, seeds _strict_reject, format_relay_block, require_bare_task_id. Brainstorm: not required — single-domain reversible prompt fix. Seat check: no brain_turn per Manager order, so no seat routing needed. DESIGN.md and docs/architecture.md absent, skipped per Absent-File Policy. verification-before-completion applied: RTK green plus lint sync gates green before staging. Modified: prompts/fragments/06-personas.md, prompts/fragments/01-system_version.md, system-prompt.md, docs/brain-bridge.md, CHANGELOG.md.

Assumption A1: prompt-only fix is sufficient and no lenient bridge fallback is wanted, because Manager asked for minimal simple changes and strict tests pin fail-closed.

Revision 2 (dual-mode per Manager rejection): bare-only rejected. MODE is declared in 19-initialization (manual ferries by copy-paste, automatic chains brain_turn; default manual) while the bridge was mode-blind, so one shape could not serve both. New contract: manual MODE fences ```xml forced, automatic MODE bare with no fences; bridge extracts bare first then complete ```xml-fenced blocks, other fences stay docs, bare unclosed and truncated fences still strict-reject (broken XML never executes). Tests updated from strict-reject to extraction pins (8 cases); truncated-in-fence case keeps rejecting. Version 9.58.2, artifact regenerated and sync-verified. Living docs: ADRs appended in mcp-brain-bridge and fragments DECISIONS. verification-before-completion applied on the revision run: RTK 277 passed plus lint sync gates green before staging. Modified this round: prompts/fragments/06-personas.md, prompts/fragments/01-system_version.md, system-prompt.md, mcp-brain-bridge/server.py, tests/test_brain_bridge.py, docs/brain-bridge.md, CHANGELOG.md, mcp-brain-bridge/DECISIONS.md, prompts/fragments/DECISIONS.md.

Autopilot locked for 316 at Manager order on 2026-10-12. Bridge check: brain_turn absent from Code Mode catalog (turn, brain_turn, and brain searches return no bridge path), so autopilot QA and review chaining is capability-blocked. File stays in tasks/qa/ with mode recorded here; next action needs the bridge path restored or a manual QA decision.

Autopilot retry: bridge restored with tools.brain.brain_turn; Manager chose Retry. QA chained under same task and session: VERDICT QA_PASSED with cites mcp-brain-bridge/server.py:891, prompts/fragments/06-personas.md:17, tests/test_brain_bridge.py:2069, docs/brain-bridge.md:20 (F1 bare confusion, F2 fenced-docs tradeoff per Manager order, F3 broken XML still rejects, F4 unfenced-wins preserved). Review chained under same task and session: technical APPROVED, PO_REVIEW_PENDING, no blocking issues, file stays in tasks/qa/ until the exact closure word. Autopilot never commits or closes.

Manager accept quote: "Approved for closure" (answered the relayed closure question). Closure attempt 1 as Senior Programmer under same task and session returned REPORT with XML_STRICT_REJECT_FENCE_FALLBACK: the emitted closure XML was fenced (4 fenced blocks) and the live bridge still runs the old strict code, so xml_blocks came back empty. One lean retry asking for bare unfenced re-emit returned a manual-mode refusal with no XML. Two failed closure calls, no usable closure XML issued; per single-issuance plus one-recall rule no further Brain closure calls will be made. Escalation: file stays in tasks/qa/; closure needs either the updated bridge deployed (copy server.py to the install plus restart) followed by one fresh closure turn, or a Manager-directed manual close.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index d0db038..6ee6a3a 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -38,6 +38,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Brain dual-mode XML contract (Task 316, system prompt 9.58.2):** manual copy-paste mode forces fenced ```xml output while automatic mode emits bare unfenced XML, and the bridge extracts both shapes (bare first, ```xml-fence fallback second; other fences stay documentation-only, bare unclosed tails still strict-reject). This supersedes the bare-only 9.58.1 attempt the Manager rejected: the Senior Programmer, QA hotfix, and Reviewer postfix personas now carry the per-MODE rule, the runbook describes dual-mode extraction, and the fence-fallback tests pin extraction instead of rejection.
+
 - **Context MCP singleton report write path (Task 286):** after the singleton migration the context server runs from `~/.config/opencode/mcp-context-server`, but `create_tree_report`, `read_source_files`, and `extract_signatures` wrote their reports to `Path("context-reports")` — the process cwd — so generated maps landed in the global install dir and the project's `context-reports/` went stale (the newest repo tree report stayed at 2026-09-18, still listing the removed `stacks/` directory; found by the task 285 smoke test). All three writers now resolve `report_dir = workspace_root / "context-reports"` from the per-call `project_root` argument the caller supplies, and the `.gitignore` safeguard writes to `<project_root>/.gitignore` via a new `_ensure_context_reports_ignored(workspace_root)` parameter. `extract_signatures`'s regex fallback also reads the resolved `path` instead of the cwd-relative `file_path`. The project_root-omitted path is unchanged (cwd fallback, still surfaced client-visibly), and a new regression test proves a foreign cwd writes nothing outside `<project_root>/context-reports/`. Context-server suite: **70 passed** (69 pre-existing + 1 new).
 
 ### Changed
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index 6fcacff..08f787f 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -17,9 +17,9 @@ retired persona engine. The Hands calls it for every Brain turn
    (`<hands_implementation_task>`, `<hands_discovery_task>`,
    `<hands_combined_task>`, `<failure_report>`, `<hotfix>`), the bridge returns
    `XML_EXTRACTED` with the block; otherwise `REPORT` with the text.
-   Explicit ```xml fences count as real XML: when the unfenced scan finds
-   nothing, allowlist tags inside ```xml bodies still extract (other
-   fences stay documentation-only).
+   Bare unfenced XML extracts first (automatic mode); when none exists,
+   allowlisted blocks inside explicit ```xml fences extract (manual
+   copy-paste mode). Other fences stay documentation-only.
 4. **Questions relay to the Manager.** A `QUESTION` verdict pauses
    the Hands until the Manager answers.
 
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 0596228..d8c06cc 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -6,3 +6,10 @@
 - **Decision:** Adopting Living Folder Docs standard for this component.
 - **Consequences:** All future structural or contract changes must be recorded here.
 - **Rollback:** N/A (baseline adoption).
+
+## [2026-10-12] ADR-002: Dual-mode XML extraction (bare + fenced fallback)
+
+- **Context:** Manual copy-paste mode needs forced ```xml fences; automatic MCP mode needs bare XML. The strict fence reject forced a wasted re-emit turn.
+- **Decision:** Bare unfenced blocks extract first; explicit ```xml fences extract second; other fences stay documentation-only; bare unclosed tails still strict-reject.
+- **Consequences:** Both modes extract without re-emit; fence-fallback tests pin extraction.
+- **Rollback:** Revert extract_xml_blocks fallback hunk and fence tests to strict-reject form.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 940b2a2..912690e 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -871,9 +871,11 @@ def _extract_unclosed_tail(text: str) -> str | None:
     return None
 
 
-#: Strict XML reject codes (Task 305 C1). Lenient fallback paths were
-#: deleted: unclosed trailing blocks and xml-fenced blocks now raise
-#: instead of extracting. The Brain must emit bare unfenced XML.
+#: Strict XML reject codes. Bare unclosed trailing blocks and truncated
+#: ```xml fences (no closed block inside) raise instead of extracting.
+#: Non-string input raises the contract code. Explicit ```xml fences
+#: holding complete allowlisted blocks extract via the fallback below
+#: (manual copy-paste mode); other fences stay documentation-only.
 STRICT_XML_FENCE_FALLBACK_CODE = "XML_STRICT_REJECT_FENCE_FALLBACK"
 STRICT_XML_UNCLOSED_CODE = "XML_STRICT_REJECT_UNCLOSED_TAIL"
 STRICT_XML_CONTRACT_CODE = "XML_STRICT_REJECT_CONTRACT"
@@ -889,14 +891,14 @@ def _strict_reject(code: str, msg: str) -> None:
 
 
 def extract_xml_blocks(output: str) -> list[str]:
-    """Return verbatim XML control blocks in document order. Only bare
-    unfenced blocks extract: fenced code blocks are documentation, and
-    unclosed trailing openers are rejected, never repaired. Fenced or
-    unclosed allowlisted input raises ``ValueError`` with a strict code
-    (Task 305 C1) instead of extracting. Empty list means plain
-    conversation — the Hands takes the whole output. Input contract is
-    ``str``: non-string input raises ``ValueError`` with a strict code
-    instead of a bare ``TypeError``."""
+    """Return verbatim XML control blocks in document order. Bare
+    unfenced blocks extract first (automatic mode); when none exist,
+    allowlisted blocks inside explicit ```xml fences extract as the
+    manual copy-paste fallback (other fences stay documentation-only).
+    Bare unclosed trailing openers are rejected, never repaired.
+    Empty list means plain conversation — the Hands takes the whole
+    output. Input contract is ``str``: non-string input raises
+    ``ValueError`` with a strict code instead of a bare ``TypeError``."""
     if not isinstance(output, str):
         _strict_reject(
             STRICT_XML_CONTRACT_CODE,
@@ -912,9 +914,14 @@ def extract_xml_blocks(output: str) -> list[str]:
             STRICT_XML_UNCLOSED_CODE,
             "unclosed trailing block: re-emit bare unfenced XML",
         )
+    fence_blocks: list[str] = []
     for body in _XML_FENCE_RE.finditer(output):
         content = body.group(1)
-        if _XML_RE.search(content) or _extract_unclosed_tail(content):
+        fence_blocks.extend(m.group(0) for m in _XML_RE.finditer(content))
+    if fence_blocks:
+        return fence_blocks
+    for body in _XML_FENCE_RE.finditer(output):
+        if _extract_unclosed_tail(body.group(1)):
             _strict_reject(
                 STRICT_XML_FENCE_FALLBACK_CODE,
                 "xml-fenced block: re-emit bare unfenced XML",
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index ee9d2d6..b869417 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.58.0</system_version>
+<system_version>9.58.2</system_version>
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index 7c75df1..bfd171d 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -14,7 +14,7 @@
   <persona name="Senior Programmer">
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "Hands Whisperer" (chief orchestrator of the local execution agent).</duty>
-    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. Wrap the task in a Markdown code block starting with ```xml and ending with ``` so the Manager can copy it with a single click. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
+    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. In manual MODE wrap the task in a ```xml fenced block for one-click copy-paste (fence forced); in automatic MODE emit it as bare unfenced raw XML with no fences. The bridge extracts both shapes. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
     You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. Ownership boundary: the Architect owns the WHAT (blueprint plus which skills it needs) — you own the HOW (task XML, step checklists, orchestration). **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit Goal units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
 </persona>
 
@@ -47,13 +47,13 @@
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. In manual mode the Manager ferries task files between the Hands and the Brain by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer. **Automatic-mode override:** when MODE is automatic, chain the next `brain_turn` yourself under the same `task_id` (re-QA after fixes, then Reviewer) and never ask the Manager to ferry files or emit copy/paste handoffs. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. In manual mode the Manager ferries task files between the Hands and the Brain by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points — fenced ```xml in manual MODE (fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer. **Automatic-mode override:** when MODE is automatic, chain the next `brain_turn` yourself under the same `task_id` (re-QA after fixes, then Reviewer) and never ask the Manager to ferry files or emit copy/paste handoffs. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
 </persona>
 
   <persona name="Code Reviewer">
     <trigger>Manager pastes the Hands' completed Task Summary, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** when MODE is automatic, chain the fix/review `brain_turn` calls yourself and never ask the Manager to ferry files; the technical approval still relays to the Manager for the explicit closure word.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** when MODE is automatic, chain the fix/review `brain_turn` calls yourself and never ask the Manager to ferry files; the technical approval still relays to the Manager for the explicit closure word.</behavior>
 </persona>
 
 <auto_load>
@@ -61,4 +61,4 @@ Layer 1 — explicit mention wins. If the Manager names a persona (exact name or
 Layer 2 — threshold inference. If nobody is named, infer from the Manager's message plus conversation history and current machine state. High confidence means the message maps to exactly one persona's trigger or duty with no rival. Then load it, declare it in the existing bracket label, and proceed. The label makes the choice visible and correctable. Low confidence means two or more personas fit, or none fits clearly. Then do NOT guess. Stop and ask the Manager which persona to load. Guessing an identity is a hallucination risk. One question costs less than a wrong persona.
 No new label. The bracket declaration in 02-role stays the single speaker display. Never add a second Speaking-as line.
 </auto_load>
-</personas>
\ No newline at end of file
+</personas>
diff --git a/prompts/fragments/DECISIONS.md b/prompts/fragments/DECISIONS.md
index 2bb1001..be4ae3a 100644
--- a/prompts/fragments/DECISIONS.md
+++ b/prompts/fragments/DECISIONS.md
@@ -6,3 +6,10 @@
 - **Decision:** Adopting Living Folder Docs standard for this component.
 - **Consequences:** All future structural or contract changes must be recorded here.
 - **Rollback:** N/A (baseline adoption).
+
+## [2026-10-12] ADR-002: Dual-mode Brain XML emission rule
+
+- **Context:** Manual mode needs forced ```xml fences for copy-paste; automatic mode needs bare XML for direct MCP execution.
+- **Decision:** Programmer, QA hotfix, and Reviewer postfix personas carry the per-MODE emission rule; bridge extracts both shapes.
+- **Consequences:** No re-emit loop in either mode; version bumped with artifact regen.
+- **Rollback:** Revert persona wording to prior revision and re-run the assembler.
diff --git a/system-prompt.md b/system-prompt.md
index a966254..2b8e96a 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.58.0</system_version>
+<system_version>9.58.2</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -66,7 +66,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="Senior Programmer">
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "Hands Whisperer" (chief orchestrator of the local execution agent).</duty>
-    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. Wrap the task in a Markdown code block starting with ```xml and ending with ``` so the Manager can copy it with a single click. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
+    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. In manual MODE wrap the task in a ```xml fenced block for one-click copy-paste (fence forced); in automatic MODE emit it as bare unfenced raw XML with no fences. The bridge extracts both shapes. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
     You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. Ownership boundary: the Architect owns the WHAT (blueprint plus which skills it needs) — you own the HOW (task XML, step checklists, orchestration). **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit Goal units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
 </persona>
 
@@ -99,13 +99,13 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. In manual mode the Manager ferries task files between the Hands and the Brain by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer. **Automatic-mode override:** when MODE is automatic, chain the next `brain_turn` yourself under the same `task_id` (re-QA after fixes, then Reviewer) and never ask the Manager to ferry files or emit copy/paste handoffs. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. In manual mode the Manager ferries task files between the Hands and the Brain by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points — fenced ```xml in manual MODE (fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer. **Automatic-mode override:** when MODE is automatic, chain the next `brain_turn` yourself under the same `task_id` (re-QA after fixes, then Reviewer) and never ask the Manager to ferry files or emit copy/paste handoffs. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
 </persona>
 
   <persona name="Code Reviewer">
     <trigger>Manager pastes the Hands' completed Task Summary, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** when MODE is automatic, chain the fix/review `brain_turn` calls yourself and never ask the Manager to ferry files; the technical approval still relays to the Manager for the explicit closure word.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** when MODE is automatic, chain the fix/review `brain_turn` calls yourself and never ask the Manager to ferry files; the technical approval still relays to the Manager for the explicit closure word.</behavior>
 </persona>
 
 <auto_load>
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 172c1c6..b0ae0b5 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -574,7 +574,7 @@ def test_brain_turn_none_output_reports_without_crash(tmp_path, monkeypatch):
 
 
 def test_brain_turn_consecutive_fenced_both_report_code(tmp_path, monkeypatch):
-    # Task 305 C1 loop: two fenced turns both REPORT with strict code.
+    # Dual-mode: two fenced turns both extract at turn level.
     monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
     _mk_sys_prompt(tmp_path, monkeypatch)
     monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
@@ -591,14 +591,13 @@ def test_brain_turn_consecutive_fenced_both_report_code(tmp_path, monkeypatch):
     target = call.fn if hasattr(call, "fn") else call
     first = target("q", task_id="219")
     second = target("q2", task_id="219")
-    assert first["status"] == "REPORT" and second["status"] == "REPORT"
-    assert "XML_STRICT_REJECT_FENCE_FALLBACK" in first["output"]
-    assert "XML_STRICT_REJECT_FENCE_FALLBACK" in second["output"]
+    assert first["status"] == "XML_EXTRACTED" and second["status"] == "XML_EXTRACTED"
+    assert len(first["xml_blocks"]) == 1 and len(second["xml_blocks"]) == 1
 
 
 def test_brain_turn_strict_reject_reports_code(tmp_path, monkeypatch):
-    # Task 305 C1: fenced operative XML never extracts at turn level.
-    # The tool stays stable and reports with the explicit strict code.
+    # Dual-mode: fenced operative XML extracts at turn level.
+    # The tool stays stable and returns the block.
     monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
     _mk_sys_prompt(tmp_path, monkeypatch)
     monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
@@ -608,8 +607,8 @@ def test_brain_turn_strict_reject_reports_code(tmp_path, monkeypatch):
     call = bridge.brain_turn
     target = call.fn if hasattr(call, "fn") else call
     result = target("q", task_id="217")
-    assert result["status"] == "REPORT"
-    assert "XML_STRICT_REJECT_FENCE_FALLBACK" in result["output"]
+    assert result["status"] == "XML_EXTRACTED"
+    assert len(result["xml_blocks"]) == 1
 
 
 def test_brain_turn_budget_return_fields(tmp_path, monkeypatch):
@@ -2067,23 +2066,26 @@ def test_extract_hotfix_bare_block():
 
 
 def test_extract_known_tag_inside_xml_fence():
-    # Task 305 C1 strict: lenient fallback raises with code.
-    with pytest.raises(ValueError, match="XML_STRICT_REJECT_FENCE_FALLBACK"):
-        bridge.extract_xml_blocks(
-            "notes\n```xml\n<failure_report>root cause</failure_report>\n```\ntail"
-        )
+    # Dual-mode fallback: manual copy-paste ```xml fences extract.
+    blocks = bridge.extract_xml_blocks(
+        "notes\n```xml\n<failure_report>root cause</failure_report>\n```\ntail"
+    )
+    assert len(blocks) == 1
+    assert blocks[0].startswith("<failure_report>")
 
 
 def test_extract_hotfix_inside_xml_fence():
-    # Task 305 C1 strict: lenient fallback raises with code.
-    with pytest.raises(ValueError, match="XML_STRICT_REJECT_FENCE_FALLBACK"):
-        bridge.extract_xml_blocks("```xml\n<hotfix>apply A1-A8</hotfix>\n```")
+    # Dual-mode fallback: manual copy-paste ```xml fences extract.
+    blocks = bridge.extract_xml_blocks("```xml\n<hotfix>apply A1-A8</hotfix>\n```")
+    assert len(blocks) == 1
+    assert blocks[0].startswith("<hotfix>")
 
 
 def test_extract_unclosed_xml_fence_to_eof():
-    # Task 305 C1 strict: lenient fallback raises with code.
-    with pytest.raises(ValueError, match="XML_STRICT_REJECT_FENCE_FALLBACK"):
-        bridge.extract_xml_blocks("notes\n```xml\n<hotfix>apply A1</hotfix>\n")
+    # Dual-mode fallback: unclosed ```xml fence still yields to EOF.
+    blocks = bridge.extract_xml_blocks("notes\n```xml\n<hotfix>apply A1</hotfix>\n")
+    assert len(blocks) == 1
+    assert blocks[0].startswith("<hotfix>")
 
 
 def test_extract_ignores_hotfix_in_non_xml_fences():
@@ -2117,17 +2119,20 @@ def test_extract_unfenced_wins_over_fenced_xml():
 
 
 def test_extract_multiple_xml_fences_in_order():
-    # Task 305 C1 strict: lenient fallback raises with code.
-    with pytest.raises(ValueError, match="XML_STRICT_REJECT_FENCE_FALLBACK"):
-        bridge.extract_xml_blocks(
-            "```xml\n<hotfix>first</hotfix>\n```\ntext\n```xml\n<failure_report>second</failure_report>\n```"
-        )
+    # Dual-mode fallback: multiple ```xml fences extract in order.
+    blocks = bridge.extract_xml_blocks(
+        "```xml\n<hotfix>first</hotfix>\n```\ntext\n```xml\n<failure_report>second</failure_report>\n```"
+    )
+    assert len(blocks) == 2
+    assert blocks[0].startswith("<hotfix>")
+    assert blocks[1].startswith("<failure_report>")
 
 
 def test_extract_uppercase_fence_lowercase_tag():
-    # Task 305 C1 strict: lenient fallback raises with code.
-    with pytest.raises(ValueError, match="XML_STRICT_REJECT_FENCE_FALLBACK"):
-        bridge.extract_xml_blocks("```XML\n<hotfix>loud fence</hotfix>\n```")
+    # Dual-mode fallback: case-insensitive ```XML fence extracts.
+    blocks = bridge.extract_xml_blocks("```XML\n<hotfix>loud fence</hotfix>\n```")
+    assert len(blocks) == 1
+    assert blocks[0].startswith("<hotfix>")
 
 
 def test_extract_uppercase_tag_tolerated():
@@ -2135,9 +2140,9 @@ def test_extract_uppercase_tag_tolerated():
     # varies in case; an operative tag in any case still extracts.
     blocks = bridge.extract_xml_blocks("<HOTFIX>x</HOTFIX>")
     assert len(blocks) == 1
-    # Task 305 C1 strict: the fenced twin raises with code.
-    with pytest.raises(ValueError, match="XML_STRICT_REJECT_FENCE_FALLBACK"):
-        bridge.extract_xml_blocks("```xml\n<HOTFIX>x</HOTFIX>\n```")
+    # Dual-mode fallback: the fenced twin extracts as well.
+    blocks = bridge.extract_xml_blocks("```xml\n<HOTFIX>x</HOTFIX>\n```")
+    assert len(blocks) == 1
 
 
 def test_extract_fence_without_newline_ignored():
```
<!-- END_GIT_DIFF -->
