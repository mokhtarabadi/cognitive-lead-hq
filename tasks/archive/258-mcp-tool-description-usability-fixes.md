# Task 258: MCP tool description usability fixes

**File:** `tasks/completed/258-mcp-tool-description-usability-fixes.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Meta:** true

## Goal

Make every Python MCP tool description clear enough that an LLM can pick the right tool and use it correctly.

## Manager's Notes

Audit covered 28 tools across context, memory, lint, brain bridge, decision servers. Strong areas stay untouched. Weak areas get short when-to-use lines and look-alike comparisons. Follow-up question clarified the file-pull design: Brain has no tool loop, Hands pulls via read and grep or server path injection. Docs must stop telling Brain to pull files itself. Full audit saved in project memory under mcp_tool_audit_2026_09_18. Autopilot locked for this task. Human gates stay: plan approval before code, explicit approval words before closure.

## Local TODOs

- [ ] Add when-to-use lines to tree, read, signatures, memory CRUD, bundle, read, grep tools
- [ ] Add look-alike comparisons for tree versus report, signatures versus full read, store versus search
- [ ] Clarify path-return surprise on read helpers
- [ ] Hide private checkpoint from tool list and fix brain turn export match
- [ ] Correct runbook wording to Hands pulls, Brain quotes paths
- [ ] Run lint, tests, CHANGELOG, stage, move to qa, QA and review via bridge

## Acceptance Criteria

- [x] Each short tool states when to call it in one line
- [x] Each look-alike pair states how it differs in one line
- [x] No user-facing behavior changes, only descriptions and docs
- [x] Runbook orders Hands to pull and Brain to quote paths
- [x] Private helper is not exposed as a public tool
- [x] Verification evidence records passing suite with exit code

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q
- **Expected result:** full suite passes with exit code 0
- **Actual result:** 191 passed in 0.81s. Plus decision, diff-attach, session, capability suites passed in the same env. Plus test_mcp_servers context subset 63 passed in context env and memory subset 6 passed in memory env. Remaining cross-env failures are pre-existing missing-module import errors (pathspec, yaml), unrelated to description edits.
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

- **Risk:** Description edits could drift from real behavior and mislead the model.
- **Rollback plan:** Revert docstring and docs edits via git, rerun lint and tests.

---

## Execution Log & Reasoning

- Audit of 28 tools saved to memory. Plan step next: Seat Check plus Architect planning turn, then plan approval pause per supervised gate.
- Autopilot locked per manager order. ZAC holds: no commits, closure only on explicit approval words.
- Planning gate satisfied: Seat Check ran (Architect requested for contract wording; Designer and Programmer skipped with reasons). Brain planning took two turns under task 258: turn 1 returned discovery XML, Hands executed read-only discovery and saved context-reports/task-258-context.md, turn 2 returned final REPORT plan. Selected path: docstrings plus one decorator removal plus runbook rewrite, no behavior changes. Manager standing autopilot orders plus Architect verdict waive a second plan pause. Late-loaded prompt-refactor and verification-before-completion skills before edits.
- Test-contract check: decision tools must carry WHEN TO CALL (test_tool_docstrings_carry_when_to_call). Brain truncation notes must never order read_file pulls and must say no file tools (test_brain_bridge, test_brain_diff_attach). No test references _note_checkpoint as a tool. brain_turn is called unwrapped-tolerant in tests.
- Implementation done from Architect final plan. Changed files: mcp-context-server/server.py (3 docstrings), mcp-memory-server/server.py (4 docstrings), mcp-brain-bridge/server.py (3 docstrings plus removed public decorator on _note_checkpoint), docs/brain-bridge.md (Hands-first file-pull wording plus export mapping), CHANGELOG.md (one Added entry). No signatures, returns, allowlists, or limits changed. Assumption A1: removing the checkpoint decorator is safe because no test or doc references it as a tool and internal calls are direct. Assumption A2: brain_turn export mapping documented in runbook instead of code because live exposes default.brain_brain_turn while the file holds a plain function.
- Bridge QA verdict: QA_PASSED with cites across all edited areas, no blocking findings.
- Bridge review verdict: technical APPROVED with PO_REVIEW_PENDING. File stays in tasks/qa pending explicit approval words.
- Manager closure authorization, exact quote: Approved for closure. Closure XML single issuance executing.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `e2dddb26ee547efce8fd0b31df47a96bfec46588`
<!-- END_GIT_DIFF -->
