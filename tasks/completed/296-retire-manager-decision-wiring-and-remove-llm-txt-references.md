# Task 296: Retire manager-decision wiring and remove llm.txt references

**File:** `tasks/completed/296-retire-manager-decision-wiring-and-remove-llm-txt-references.md`
**Source:** manager
**Type:** chore
**Status:** closed
**Risk-Tier:** T2 destructive

## Goal

Remove every live manager-decision reference in cognitive-lead-hq except the external personal repo at /home/mohammad/Develop/Projects/manager-decisions. Purge the MCP decision component entirely with its service units. Keep LLM.txt and README setup references intact and remove only decision sections inside them. Delete fully with no placeholder notes.

## Manager's Notes

Direct Manager order: "Review the entire project and make sure you've found every place where Manager Decision appears: across the whole prompt system, fragments, agents, the README, and the MCP server itself. We want to fully retire it, but keep the Manager Decision repository that is the core repo. Everything else related to it should be cleaned up. Clean it up everywhere, including memory. Even within the memory store, remove anything related to it. My suggestion: archive it as well — archive its MCP component too. Then search for llm.txt everywhere, find all occurrences, and remove them. Also, don't leave notes like this was deleted. Delete the entire text/code sections related to Manager Decision wherever they exist. Remove them completely. Create a task for this and execute it end-to-end."

## Scope

In scope:
- prompts/fragments/07-agent_skills_registry.md, agents/cognitive-executor.md, system-prompt.md rebuild, opencode.json permissions
- README.md, docs/setup.md, docs/brain-bridge.md, docs/manager-decisions.md
- skill-templates/manager-decision/, skill-templates/decision-migration/, .opencode/skills/ manager copies
- mcp-decision-server/ archive, tests/test_decision_server.py and related asserts, .opencode/decisions/ scaffolding
- .opencode/memory/manager-decisions/*, manager/*, index.md entries, quirks/full_output_verification_rule.md mention
- All live llm.txt mentions in README, docs/compaction.md, docs/openchamber.md, docs/telegram-setup.md, services/mcp-telegram.service, CHANGELOG references left intact as history, LLM.txt file disposition

Out of scope:
- External personal repo /home/mohammad/Develop/Projects/manager-decisions is KEPT as-is
- docs/history/* and tasks/archive/* history is never rewritten
- No git add/commit/push by Hands (ZAC holds)

## Local TODOs

- [x] Inventory live hits with grep evidence
- [x] Remove prompt/agent wiring and rebuild system-prompt
- [x] Remove docs and README references, delete docs/manager-decisions.md
- [x] Archive mcp-decision-server, update tests and opencode.json
- [x] Clean .opencode/memory and .opencode/decisions scaffolding, rebuild index
- [x] Remove live llm.txt references and decide LLM.txt file fate
- [x] Purge archived MCP decision component per Manager correction
- [x] Run verification gates and stage diff

## Acceptance Criteria

- [x] AC1: grep for manager-decision, manager_decision, DECISION_REPO_PATH, mcp-decision-server returns zero live hits outside history and external repo path
- [x] AC2: mcp-decision-server is purged and no live config references its tools
- [x] AC3: memory index has no manager-decision namespaces and no decision tool mentions in live memory
- [x] AC4: LLM.txt kept as setup entry point with decision sections removed, README setup references intact
- [x] AC5: full test suite and lint gates pass with evidence recorded

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q
- **Expected result:** pass exit 0
- **Actual result:** 541 passed, 22 warnings in 4.32s (exit 0) with OPENCODE_SESSION_ID unset; hotfix re-verified after QA round 1
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** destructive delete removes needed wiring or breaks tests and prompt rebuild
- **Rollback plan:** worktree diff revert before staging, history reachable via git log --follow, external decisions repo untouched

---

## Execution Log & Reasoning

- Seat Check: domains are prompt contract plus MCP server removal plus docs and memory cleanup → Software Architect + Senior Programmer requested. UI/UX Designer skipped (no user-visible surface). QA, Reviewer, Planner, Strategist skipped at planning (verification comes later).
- Brainstorm: required — cross-disciplinary cleanup plus hard-to-reverse deletes.
- Prompt-refactor applied: validated English direct order, expanded scope from discovery subagents, structured as T2 chore with explicit keeps.
- Brain plan verdict 2026-10-05: Architect + Senior Programmer 2-seat consult APPROVED plan P0-P7. Keeps K1 external repo untouched, K2 history immutable, K3 ZAC. Selected path: inventory-first deletes, archive mcp-decision-server via git mv, rebuild system-prompt and memory index, llm.txt sweep with disposition record. Awaiting Manager plan approval before implementation XML.
- Manager plan approval 2026-10-05: "Approved" via question tool. Routed back through Brain for Senior Programmer implementation XML. Executed XML verbatim.
- Execution: Step1 inventory recorded live hits across prompts, agents, docs, skills, MCP, memory, tests. Steps 2-6 deleted full lines and sections with no placeholder notes, archived mcp-decision-server with git mv preserving git log follow, rebuilt system-prompt via assembler exit 0, rebuilt memory index to 21 entries with zero decision namespaces. LLM disposition: root LLM.txt deleted after zero live refs outside history. External personal repo untouched. History paths docs/history, tasks/archive, CHANGELOG history, telegram-sync left intact.
- Assumption A1: context-reports and tasks/.sessions transcripts count as generated history and were excluded from live zero-hit gates. Reason: they are not live config.
- Assumption A2: single transport-learning test failure under ambient OPENCODE_SESSION_ID is environmental, not caused by deletes. Reason: passes with session unset.
- Q1: prompts/archive/17-decision_logging_mandate.md left as history. Confirm history treatment stands.
- Correction 2026-10-05 per Manager: LLM.txt restored and kept as the setup entry point with only decision sections removed. README and docs setup references restored. Archive purged entirely with rm -rf per no-longer-needed order. LLM disposition: kept and cleaned.
- Hotfix Checklist (Brain QA round 1, QA_REJECTED F1-F4):
- [x] Step 1 docs/brain-bridge.md autopilot paragraph rewritten generic with zero decision refs
- [x] Step 2 quirks rule body restored generic without decision mention
- [x] Step 3 README HQ install pointer restored generic with zero decision refs
- [x] Step 4 upgrade workflow history note restored generic without live wiring
- [x] Step 5 memory index rebuilt to 21 entries, zero decision namespaces confirmed
- Hotfix Checklist round 2 (Brain QA round 2, second REJECTED):- [x] Step 1 docs/brain-bridge.md Questions relay bullet rewritten clean with zero decision refs
- [x] Step 2 .env.example orphan decision comment block deleted fully, BRAIN comments intact
- [x] Step 3 index quirks row restored via rebuild, generic description with zero decision refs
- [x] Step 4 rebuild preserved the description, index staged
- Brain QA round 3 verdict 2026-10-05: QA_PASSED. Scope confirmed safe and limited to decision wiring. S1 LLM kept, S2 README and setup docs intact, S3 server purged, S4 no unrelated behavior change. Tests 541 passed, lint pass, index 21 entries zero decision namespaces.
- Code Reviewer verdict 2026-10-05: APPROVED to PO_REVIEW_PENDING. Technically approved with no functional issues. I1 capability.py and I2 session_ledger.py style reflows accepted as is. Awaiting Manager explicit closure words.
- Closed: 2026-10-05 Approved for closure by Manager.
- Grep evidence: live-source mgr grep (excl .git/archive/.venv/__pycache__/context-reports/docs-history/tasks/CHANGELOG/telegram-sync/.pytest_cache/external) returns exit 1 with zero hits. llm live grep (same exclusions plus LLM.txt self) returns zero hits. index grep for manager-decision returns exit 1.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `013ff1424c2796ccb4588c13682bbc571ef3de5a`
<!-- END_GIT_DIFF -->
