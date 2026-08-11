# Task 93: Fix Document Drift and Inconsistencies

**File:** `tasks/in-progress/93-fix-document-drift-and-inconsistencies.md`
**Source:** manager
**Type:** docs
**Status:** open

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Resolve all four F7 findings from Task 87: (F7a) sync the README structure tree with missing directories (`agents/`, `mcp-lint-server/`, `mcp-memory-server/`, `tests/`) and correct the stale "V7" system-prompt label; (F7b) add the default agent to the repo `opencode.json` (F7b's CHANGELOG 8.3.0 claim vs missing key); (F7c) clarify the `git mv` autonomy exception in `AGENTS.md`; (F7d) enforce the `tasks/qa/` transition in `agents/cognitive-executor.md`.

## Manager's Notes

- **F7b key decision (documented deviation):** the Orchestrator instructed adding `"agent": "cognitive-executor"`, but the authoritative opencode config docs (vendored `docs/opencode/config.md` line 365: "You can set the default agent using the **default_agent** option") and the working global config (`~/.config/opencode/opencode.json` — which made cognitive-executor the default in practice) both use **`default_agent`**. The repo config therefore gains `"default_agent": "cognitive-executor"` — this also matches the CHANGELOG 8.3.0 claim that F7b flagged as unfulfilled. Adding `"agent"` would be a no-op key and would NOT close F7b.
- **F7d:** the new rule makes `tasks/qa/` a mandatory transit state for every implemented task (implementation → `stage_and_inject_diff` → `git mv` to `tasks/qa/` → summary output). Closure instructions already support `tasks/qa/` → `completed/`.
- **Global sync:** the executor agent global copy (`~/.config/opencode/agents/cognitive-executor.md`) is re-synced after the edit (LLM.txt Step 6.5 pattern) so the next session enforces the qa transition.
- No system-prompt.md edit → no version bump required by AGENTS.md rules.

## Local TODOs

- [x] Step 1: Create this task file (ID discovery → 93), move to `tasks/in-progress/`
- [x] Step 2: Read target files (README tree, opencode.json, AGENTS.md, cognitive-executor.md, CHANGELOG) + verify the opencode default-agent schema key
- [x] Step 3: Fix F7a — README: `# V8 Multi-Agent System Prompt` + insert `agents/`, `mcp-lint-server/`, `mcp-memory-server/`, `tests/` into the tree
- [x] Step 4: Fix F7b — add `"default_agent": "cognitive-executor"` to repo `opencode.json` (deviation from Orchestrator's literal `"agent"` documented)
- [x] Step 5: Fix F7c — append the `git mv` Kanban exception to the `AGENTS.md` guardrail
- [x] Step 6: Fix F7d — replace the QA/Review Phase section in `agents/cognitive-executor.md` with the mandatory `tasks/qa/` transition rule
- [x] Step 7: Update `CHANGELOG.md` — `[Unreleased]` → `### Fixed`: F7 bullet
- [x] Step 8: Syntax verification (JSON validity + greps + lint) + re-sync global executor agent copy

## Acceptance Criteria

- [x] README line 95 says `# V8 Multi-Agent System Prompt` (1 match) and the tree lists `agents/`, `mcp-lint-server/`, `mcp-memory-server/`, `tests/`
- [x] `opencode.json` valid JSON containing `default_agent: cognitive-executor`
- [x] `AGENTS.md` guardrail carries the `git mv` Kanban exception
- [x] `agents/cognitive-executor.md` QA section mandates the `tasks/qa/` move before summary output
- [x] `CHANGELOG.md` `[Unreleased]` → `### Fixed` has the F7 entry, no duplicates
- [x] Task file passes `lint_task_file`

## Verification Evidence

- **Test command:** `python3 -m json.tool opencode.json` ; `grep -n "V8 Multi-Agent" README.md` ; `grep -n "default_agent" opencode.json` ; `grep -n "Exception.*git mv" AGENTS.md` ; `grep -n "tasks/qa/" agents/cognitive-executor.md` ; `lint_task_file tasks/in-progress/93-fix-document-drift-and-inconsistencies.md`
- **Expected result:** valid JSON; V8 label 1 match; `default_agent` 1 match; git mv exception 1 match; `tasks/qa/` 1 match in executor; lint ✅
- **Actual result:** `python3 -m json.tool` → ✅ valid; V8 label at README line 95 (1 match); `default_agent` at opencode.json line 3 (1 match); git mv exception at AGENTS.md line 39 (1 match); `tasks/qa/` in executor at line 44 (new rule) + line 47 (existing qa→completed closure path — now consistent); README tree shows agents/ (103), mcp-lint-server/ (112), mcp-memory-server/ (114), tests/ (116); global executor copy re-synced (byte-identical); CHANGELOG `### Fixed` now has both the pre-existing Security-hardening bullet AND the new F7 bullet (append, not replace — one edit slip was caught and corrected mid-task); lint → ✅ passed (run below)
- **Exit code:** 0 (all checks); 0 (lint)

## Risk & Rollback

- **Risk:** (1) Wrong default-agent key would silently no-op — mitigated by schema verification (vendored docs + working global config). (2) Mandatory qa/ transition could surprise the closure flow — closure tooling already supports qa → completed. (3) README tree cosmetic edits — low risk. (4) CHANGELOG duplicates — Parse-Then-Append.
- **Rollback plan:** revert the 5 file edits (README labels/tree, opencode.json key, AGENTS.md exception line, executor QA section, CHANGELOG bullet) and re-sync the global executor copy.

---

## OpenCode Execution Log & Reasoning

### What was done

1. **F7a — `README.md`:** line 95 label corrected `V7` → `V8 Multi-Agent System Prompt`; structure tree gained `agents/` (with both agent files), `mcp-lint-server/`, `mcp-memory-server/`, and `tests/` blocks in logical positions (agents before docs; the two MCP servers after mcp-context-server; tests before .opencode).
2. **F7b — `opencode.json`:** added `"default_agent": "cognitive-executor"` at root level. **Documented deviation:** the Orchestrator's literal instruction was `"agent": "cognitive-executor"`, but the vendored opencode config docs (`docs/opencode/config.md` line 365) state the default-agent option is `default_agent`, and the working global config (`~/.config/opencode/opencode.json`) uses `default_agent`. `"agent"` is used for other purposes (commands/agents definitions) — adding it at root would be a no-op and would not fulfill F7b. The chosen key matches the CHANGELOG 8.3.0 claim that F7b flagged as unfulfilled.
3. **F7c — `AGENTS.md`:** the `git mv` guardrail now carries the explicit exception: autonomous `git mv` is permitted for Kanban file moves (backlog/in-progress/qa/completed/archive) — aligning AGENTS.md wording with the executor protocol's actual behavior (Task 87 F7c).
4. **F7d — `agents/cognitive-executor.md`:** Section 3 (QA/Review Phase) replaced with the mandatory rule: after implementation + `stage_and_inject_diff`, the executor MUST `git mv` the task file to `tasks/qa/` before outputting the summary. The closure section's existing "(or `tasks/qa/` to `completed/`)" path makes the new transition fully consistent — the previously dead `tasks/qa/` directory becomes a real lifecycle state. Global copy at `~/.config/opencode/agents/cognitive-executor.md` re-synced (byte-identical).
5. **`CHANGELOG.md`:** the F7 bullet appended under `[Unreleased]` → `### Fixed`, alongside the pre-existing Security-hardening bullet (Parse-Then-Append). **Integrity note:** an initial edit accidentally REPLACED the pre-existing bullet; caught immediately and corrected to an append — final state verified (both bullets present, no duplicates).

### Architectural reasoning

- **F7b grounding over literalism:** the Orchestrator's `"agent"` key would have silently failed F7b's own goal (the repo config claims default-agent behavior). Following the authoritative vendored docs + proven global config is the grounded choice; the deviation is documented for the Reviewer rather than hidden.
- **F7d ripple effect:** every future implementation task now transits `tasks/qa/` before summary; the closure flow (qa → completed) already supported it. Discovery tasks remain unaffected (no file moves). This makes the QA gate physically visible in the Kanban state, matching the QA Engineer persona's role in the Brain.
- **No system-prompt edit → no version bump** (AGENTS.md rule satisfied).

### Verification

- All bash greps returned expected results (see Verification Evidence). JSON validated with `python3 -m json.tool`. No repair attempts needed (the single CHANGELOG slip was self-corrected during the task).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->