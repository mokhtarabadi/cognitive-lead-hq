# Task 316: Brain dual-mode XML contract fix

**File:** `tasks/completed/316-brain-bare-xml-contract-fix.md`
**Source:** manager
**Type:** bug
**Status:** closed

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

Manager accept quote for closure: Approved for closure. Closure executed via single-issuance Senior Programmer XML, file moved to completed, status closed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `aefc42fe8461c08ad7c6285e244a9fcc5ff0a0ec`
<!-- END_GIT_DIFF -->
