# Task 0379: Cognitive Agents, Prompt, and Context-Gathering Overhaul

**File:** `tasks/completed/0379-cognitive-agents-prompt-and-context-gathering-overhaul.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-11-06T10:01:44Z
**Submitted:** 2026-11-06T08:29:44Z
**Mode:** automatic (autopilot locked)

## Goal

Refactor cognitive agents, system prompt fragments, and brain context gathering while closing the discovery-fed grounding gap (false-positive `no fed-context block` when `context_paths` injected server-side; `_combined_prompt` dropping `_rendered_paths`).

## Micro-Task Checklist

- [x] Step 1: Fix false-positive context grounding in `mcp-brain-bridge/server.py`
- [x] Step 2: Refactor cognitive discovery subagent in `agents/cognitive-discovery.md`
- [x] Step 3: Refactor cognitive executor in `agents/cognitive-executor.md`
- [x] Step 4: Align project root context hub in `AGENTS.md`
- [x] Step 5: Modernize system role in `prompts/fragments/02-role.md`
- [x] Step 6: Modernize hands protocols in `prompts/fragments/09-hands_protocols.md`
- [x] Step 7: Update execution workflow in `prompts/fragments/11-execution_workflow.md`
- [x] Step 8: Update constraints in `prompts/fragments/13-constraints.md`
- [x] Step 9: Bump version in `prompts/fragments/01-system_version.md` to `9.71.0`
- [x] Step 10: Reassemble system prompt
- [x] Step 11: Update regression tests in `tests/test_prompt_sync.py`

## Hotfix Checklist (QA_REJECTED round)

- [x] Hotfix Step 1: Spoof-vs-rendered grounding tests, verified red-first
- [x] Hotfix Step 2: Server-derived `has_server_paths` flag in sufficiency check
- [x] Hotfix Step 3: Canonical manifest format in discovery + `09` summary
- [x] Hotfix Step 4: Strengthened prompt-sync manifest structure test
- [x] Hotfix Step 5: Rebuilt prompt, CHANGELOG fix note, ADR updates
- [x] Hotfix Step 6: Evidence, full suite, lint, re-stage in `qa/`

## Hotfix Checklist 2 (QA_REJECTED round 2 — manual handoff)

- [x] Hotfix2 Step 1: Inspected 02/06/09 + `opencode.json` + codemode-policy memory; Code Mode confirmed host-level all-true, no wording change needed
- [x] Hotfix2 Step 2: Handoff regression test, verified red-first
- [x] Hotfix2 Step 3: Aligned manual instructions in 02/06/09 (+19 MODE declaration, same defect, scope extension logged)
- [x] Hotfix2 Step 4: Rebuilt prompt (still 9.71.0), CHANGELOG + agents ADR updated
- [x] Hotfix2 Step 5: Evidence, full suite, lint, re-stage in `qa/`

## Hotfix Checklist 3 (QA_REJECTED round 3 — O1 Manager-approved)

- [x] O1a: Extended handoff test (dedup + `AGENTS.md`), verified red-first
- [x] O1b: Distinct combined output line; `AGENTS.md` notify step aligned
- [x] O1c: Deduped overlapping 09 edits; rebuilt prompt; full suite green; re-staged

## Hotfix Checklist 4 (QA_REJECTED round 4 — manual mode line + active voice)

- [x] Round 4 Step 1: Executor manual mode line forbids task-ferrying relay text
- [x] Round 4 Step 2: Mode-line memory shard + bridge runbook mirrored
- [x] Round 4 Step 3: Mismatch branch converted to active voice
- [x] Round 4 Step 4: Prompt reassembled, version held at `9.71.0`
- [x] Round 4 Step 5: Handoff test extended (red-first, then green)
- [x] Round 4 Step 6: Task record, CHANGELOG clause, DECISIONS follow-up

## Hotfix Checklist 5 (QA_REJECTED round 5 — autopilot O1 self-authorized)

- [x] Round 5: Mismatch branch directs invocation (red-first, then green)
- [x] Round 5: Prompt rebuilt, CHANGELOG + ADR, task record updated

## Hotfix Checklist 6 (QA_REJECTED round 6 — autopilot O1 self-authorized)

- [x] Round 6: Conditional OTHERWISE reconciled with summary halt branch (red-first, then green)
- [x] Round 6: Prompt rebuilt, CHANGELOG + ADR, task record updated

## Hotfix Checklist 7 (QA_REJECTED round 7 — autopilot partial O1)

- [x] Round 7: DONE reordered after QA/review chain (red-first, then green)
- [x] Round 7: F1/F3 marker-provenance claim disputed with evidence (no behavior change)
- [x] Round 7: Prompt rebuilt, CHANGELOG + ADR, task record updated

## Review Hotfix Checklist (Code Review REJECTED_NEEDS_FIXES — autopilot)

- [x] Review Step 1: Extended handoff assertions (Brain-owned overrides, path token, changelog scope), red-first proven
- [x] Review Step 2: QA/Reviewer overrides replaced with Hands-owned chaining text
- [x] Review Step 3: `AGENTS.md` notify uses active `**File:**` path; CHANGELOG narrowed; fragment ADR + README rule added
- [x] Review Step 4: Prompt rebuilt at `9.71.0`, handoff green, prompt-sync green
- [x] Review Step 5: Task mode automatic, DoD count corrected, evidence recorded
- [x] Review Step 6: Lint clean, foreign-file check, staged via MCP tool
- [x] Review Step 7: Re-review chained under same task/session

## Review Hotfix Checklist 2 (manifest range consistency)

- [x] Step 1: Add and prove the prompt-sync regression assertion red-first.
- [x] Step 2: Require full-file line ranges for small discovery-manifest entries.
- [x] Step 3: Run targeted and full test suites and record exact evidence.
- [x] Step 4: Lint and restage the existing QA task, then chain Code Review.

## Local TODOs

- [x] Ground both `server.py` hunks against live code before editing
- [x] Preserve all `test_prompt_sync.py` regression literals while editing fragments
- [x] Rebuild prompt and prove byte-identical except intended hunks
- [x] Update living folder docs (`agents`, `mcp-brain-bridge`) in the same task
- [x] Record verification evidence with exact commands and exit codes

## Acceptance Criteria

- [x] Plan-turn sufficiency check treats server-side `[path-injected:` as grounding
- [x] Combined prompt folds rendered paths into the diagnostic text
- [x] Discovery reports end with a machine-readable `Context-Paths` manifest
- [x] Executor documents the Code Mode Tool Calling Protocol
- [x] System prompt rebuilt to `9.71.0`; all five suites green with zero regression
- [x] Spoofed `[path-injected:` marker in user text still reports the grounding gap
- [x] Server-rendered paths satisfy grounding via explicit caller-passed flag
- [x] Canonical manifest structure shared by discovery report and `09` summary
- [x] Manual summaries and personas no longer route task text through the Manager
- [x] Handoff regression test green; prompt still `9.71.0` with zero regression
- [x] One distinct exact-output line per 09 template; root notify step aligned
- [x] Manual mode line forbids task-ferrying relay text (executor + runbook + memory shard)
- [x] Mismatch branch in active voice; handoff test pins both plus root wording
- [x] Mismatch branch directs the invocation with the discovery manifest
- [x] Conditional and summary mismatch paths agree (invoke-with-manifest both)
- [x] DONE declared only after the QA/review chain runs
- [x] Hands-owned automatic chaining in both review personas; notify uses active path
- [x] Every discovery manifest path uses a concrete `#Lstart-end` range, with full-file ranges for small files.

## Verification Evidence

| # | Command | Expected | Actual | Exit |
|---|---------|----------|--------|------|
| 1 | `python3 scripts/prompt-build/assemble_system_prompt.py --output system-prompt.md` | assembles, only intended hunks | `Assembled 112691 bytes -> system-prompt.md`; diff touches only the 5 edited fragments + `system-prompt.md` | 0 |
| 2 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q` | all pass | 26 passed | 0 |
| 3 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q` | all pass | 307 passed | 0 |
| 4 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_agent_tool_gate.py -q` | all pass | 2 passed | 0 |
| 5 | `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml pytest tests/ -q` | zero regression | 786 passed, 24 warnings | 0 |
| 6 | `uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q -k sufficiency_gaps` (red-first, raw per failing-output rule) | 2 new tests fail pre-fix | 2 failed (spoof assertion + `has_server_paths` TypeError), 307 deselected | 1 |
| 7 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q -k sufficiency_gaps` | post-fix green | 7 passed, 302 deselected | 0 |
| 8 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q` | post-hotfix green | 26 passed | 0 |
| 9 | `uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q -k manual_handoff` (red-first, raw per failing-output rule) | new test fails pre-fix | 1 failed, 26 deselected | 1 |
| 10 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q` | post-hotfix2 green | 27 passed | 0 |
| 11 | `uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q -k manual_handoff` (red-first, raw per failing-output rule) | extended test fails pre-fix | 1 failed, 26 deselected | 1 |
| 12 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q` | post-O1 green | 27 passed | 0 |
| 13 | `uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q -k manual_handoff` (red-first, raw per failing-output rule) | extended round-4 assertions fail pre-fix | 1 failed, 26 deselected | 1 |
| 14 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q` | post-round-4 green | 27 passed | 0 |
| 15 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q` | no regression | 309 passed | 0 |
| 16 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_agent_tool_gate.py -q` | gate green | 2 passed | 0 |
| 17 | `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml pytest tests/ -q` | zero regression | 789 passed, 24 warnings | 0 |
| 18 | `uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q -k manual_handoff` (red-first, raw per failing-output rule) | directive assertion fails pre-fix | 1 failed, 26 deselected | 1 |
| 19 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q` | post-round-5 green | 27 passed | 0 |
| 20 | `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml pytest tests/ -q` | zero regression | 789 passed, 24 warnings | 0 |
| 21 | `uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q -k manual_handoff` (red-first, raw per failing-output rule) | reconciled-path assertions fail pre-fix | 1 failed, 26 deselected | 1 |
| 22 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q` | post-round-6 green | 27 passed | 0 |
| 23 | `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml pytest tests/ -q` | zero regression | 789 passed, 24 warnings | 0 |
| 24 | `uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q -k manual_handoff` (red-first, raw per failing-output rule) | order assertion fails pre-fix | 1 failed, 26 deselected | 1 |
| 25 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q` | post-round-7 green | 27 passed | 0 |
| 26 | `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml pytest tests/ -q` | zero regression | 789 passed, 24 warnings | 0 |
| 27 | `uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q -k manual_handoff` (red-first, raw per failing-output rule) | extended review assertions fail pre-fix | 1 failed, 26 deselected | 1 |
| 28 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q -k manual_handoff` | post-review-fix green | 1 passed, 26 deselected | 0 |
| 29 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q` | post-review-fix green | 27 passed | 0 |
| 30 | `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml pytest tests/ -q` | zero regression | 789 passed, 24 warnings | 0 |
| 31 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q -k discovery_defines_context_paths_manifest` (red-first) | range-policy assertion fails pre-fix | 1 failed, 26 deselected | 1 |
| 32 | `uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q -k discovery_defines_context_paths_manifest` (raw diagnostic) | same failure, full output | 1 failed, 26 deselected | 1 |
| 33 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q -k discovery_defines_context_paths_manifest` | post-fix green | 1 passed, 26 deselected | 0 |
| 34 | `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_prompt_sync.py -q` | post-fix green | 27 passed | 0 |
| 35 | `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml pytest tests/ -q` | zero regression | 789 passed, 24 warnings | 0 |
| 36 | `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml pytest tests/ -q` | README-sync verification green | 789 passed, 24 warnings | 0 |

Stack-skill scan: `root=. markers=[mcp-brain-bridge/pyproject.toml,pyproject.toml,package.json,go.mod,build.gradle.kts,Package.swift,vite.config.*,nuxt.config.*,nest-cli.json] matched=[] reason=no registered stack marker matches the observed plain Python MCP server`
- `python-fastapi` coverage: skipped (recorded) — the bridge is a plain stdlib-first Python MCP server, not a FastAPI application; Python testing discipline applied via pytest suites above.

## Definition of Done

- [x] All 11 implementation steps executed in order with evidence
- [x] Full test suite green (789 passed)
- [x] CHANGELOG, DECISIONS, and README docs updated
- [x] Task lint clean and QA transition executed

## Risk & Rollback

- **Risk:** fragment wording changes break prompt-sync gates. Mitigation: edits append rather than rewrite pinned sentences; suites run before docs.
- **Rollback:** revert the 14-file hunk via `git`, restore version fragment to `9.70.3`, rebuild the prompt, drop the two new tests.

## Execution Log & Reasoning

- Plan source: Orchestrator `<hands_implementation_task>` XML (approved blueprint, no separate Brain planning round needed).
- Task file did not exist in any Kanban lane; created directly in `tasks/in-progress/` before any code edit per implementation-task lifecycle rule.
- Absent-File Policy note: `docs/architecture.md` and `docs/data_model.md` do not exist; skipped gracefully. `DESIGN.md` exists (documentation-only repo, no UI surface touched). `docs/conventions.md` read.
- Assumption A1: `python` unavailable, used `python3` for the assembler (same interpreter family, exit 0).
- Assumption A2: fragment edits appended rather than rewrote pinned sentences, preserving all `test_prompt_sync.py` regression literals (verified by 26/26 green).
- Living Folder Docs: `agents/README.md` + `agents/DECISIONS.md` (new ADR) and `mcp-brain-bridge/DECISIONS.md` (ADR-011) updated in the same task as the contract changes.
- Brainstorm: not required — single-domain prompt/contract refactor from an approved blueprint with reversible git hunks.
- QA_REJECTED round (valid F1–F4): marker-string grounding was spoofable by user text; manifest had two formats. Fixed with caller-passed `has_server_paths`, canonical manifest in both surfaces, spoof-vs-rendered behavioral tests, and a strengthened structure test. Red-first proven (2 failed pre-fix), green post-fix. Task stays in `tasks/qa/` for re-review; QA not claimed.
- QA_REJECTED round 2 (valid F1–F2): manual summaries/personas still routed task text through the Manager. Fixed in 02/06/09 plus the 19 MODE declaration (same defect, logged scope extension); Code Mode claim verified against codemode-policy memory (all 7 servers true, host-level config; repo `opencode.json` carries no server block so no wording change). Handoff test red-first proven (1 failed pre-fix), 27 green post-fix, version held at 9.71.0. Residual: `AGENTS.md` end-of-task step 7 keeps the old copy-handoff line — flagged for follow-up, out of scope.
- QA_REJECTED round 3, O1 Manager-approved: F1 real — my overlapping 09 edits left the exact-output line duplicated inside each summary; removed the strays so each template emits one distinct line. F2 fixed — root notify step 7 now reports the `tasks/qa/` path with QA/review chained, approvals-only for the Manager. Handoff test extended (exact-line counts + root wording), red-first proven, 27 green. No version change.
- QA_REJECTED round 4 hotfix (remediation XML, test-first reorder logged): executor manual mode line, mode-line memory shard, and bridge runbook now forbid task-ferrying relay text; mismatch branch in active voice directing the Hands to chain the call. Skills `sop-maintenance`/`task-lint`/`verification-before-completion` carried over active from this session (no reload needed); stack scan unchanged (plain Python MCP server, no stack skill). Test-first reorder: Step 5 assertions written and proven red before Steps 1–3 wording changes, per testing-strategy discipline.
- QA_REJECTED round 5, autopilot O1 self-authorized (Manager locked auto mode; verdict offered O1/O2 with O1 recommended): mismatch summary claimed a chained replan turn without directing the call. Branch now orders invocation with the manifest via `context_paths` before the stop message; directive assertion red-first proven, 27 green post-rebuild. No version change.
- QA_REJECTED round 6, autopilot O1 self-authorized: conditional OTHERWISE path (halt-and-output-path) contradicted the summary halt branch (invoke-with-manifest). Both now direct invocation with the manifest; new assertions red-first proven, 27 green post-rebuild. No version change.
- QA_REJECTED round 7, autopilot partial O1: F2/F4 fixed (DONE reordered after the chain, order assertion red-first proven, 27 green). F1/F3 DISPUTED with evidence: inline `[fed-context]`/`[pinned-fed-context]` markers are the documented Hands fed channel — the executor's binding grounding rule (test-pinned) mandates verbatim fed retries, the bridge cannot distinguish Hands-pasted from user-typed text in one channel, and pre-existing tests pin fed-marker grounding (`plan_with_fed_context_only`, `fully_grounded_is_empty`, the `include_bundle=false` live-turn test). Round-1 scope covered server-rendered paths only. Validating provenance would break the grounded-retry contract, so no behavior change; existing tests already cover fed-marker behavior. If QA re-rejects on this point, escalate to the Manager as a spin signal.
- Code Review REJECTED_NEEDS_FIXES, autopilot review-fix (I1/I2/I3 all reproduced): QA/Reviewer automatic-mode overrides reassigned chaining to the Hands (Brain has no tool access); root notify step reads the active `**File:**` path instead of the literal token; CHANGELOG claim narrowed to the spoofed `[path-injected:]` marker. Review assertions red-first proven, green post-fix. Fragment ADR + README rule added. Skills carried over active from this session (`code-search`/`prompt-refactor` loaded earlier; stack scan unchanged).
- Code Review PO_REVIEW_PENDING (re-review): no issues in the staged diff; 789 green cited; inline fed-context behavior accepted within the Hands-fed contract. Awaiting the explicit closure word.
- Code Review PO_REVIEW_PENDING (README-sync re-review): README correction matches server behavior and ADR-011; no issues; 789 cited. Awaiting the explicit closure word.
- Closure: Manager authorization "Approved for closure" received as the explicit standalone approval (question-gate answer, twice confirmed); closure XML issued by the Senior Programmer after the lean bundle-off retry. Executing the completed-lane move and commit-and-clean path.
- Code Review follow-up: Resolved the mismatch between discovery instructions and the canonical manifest contract. Every entry now uses a concrete line range, with small files represented by their full-file range. No version bump or changelog entry was needed because this aligns the existing manifest contract.
- Sibling README sync (review follow-up, docs-only): `mcp-brain-bridge/README.md` gained the Plan-Turn Sufficiency Grounding section matching ADR-011; CHANGELOG `### Changed` records the documentation correction; no ADR change, no version change.
- Autopilot locked for task 0379 by Manager order ("lock auto brain mode for task"): Hands chains QA/review `brain_turn` turns directly under the same session thread; human gates are plan-approval (n/a — work complete) and closure approval word only. Brain-loop park order rescinded by the same message.
- QA_REJECTED round 4: F1 executor manual mode line keeps `copy-paste relay instructions expected`; F2 mismatch branch passive voice. No fix XML — Manager decision required. Manager ordered: stop the Brain loop, no more `brain_turn` calls, task parked in `tasks/qa/` staged; Manager ferries the task to an external Brain manually. Brain loop stopped; no further QA turns from this session.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `1f7badbdb2412bc54e6429aefc16a70184331905`
<!-- END_GIT_DIFF -->
