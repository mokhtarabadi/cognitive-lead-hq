# Task 341: Sync HQ plugin references with the two new plugin behaviors

**File:** `tasks/completed/0341-sync-plugin-references.md`
**Source:** manager
**Type:** docs
**Status:** closed

## Goal

Bring the living HQ documentation in line with what the two plugins now do, so the Hands reads an accurate tool list and an accurate goal-evidence contract.

## Manager's Notes

- Request: search this worktree with the context graph for every place the two plugins are mentioned, then update what genuinely needs updating.
- Graph run `context-reports/graph_20261024_182400_4ecbc4a9.json`: 4,766 nodes, 6,788 links.
- Scope is the HQ worktree only. No plugin code, no `~/.config/opencode/**`.

## Findings

- **F1.** `compact_stats` appears in zero living HQ files. `agents/cognitive-executor.md:105` and `docs/compaction.md:73-90` still list two agent tools, so the Hands cannot learn the third exists.
- **F2.** The goal plugin's two fixes are undocumented: `goal_set` now starts a clean evidence sidecar, and an existing scoped sidecar ends the legacy `.opencode/goal-evidence.json` fallback. `agents/cognitive-executor.md:115-120`, `docs/compaction.md:44-45` and `README.md:494` describe the sidecar without either rule, and stale evidence is exactly what blocked closure before.
- **F3.** All remaining hits are frozen history (`docs/history/`, `tasks/archive/`, `prompts/archive/`) or intentionally plugin-blind (`system-prompt.md`, `prompts/fragments/`), pinned by `tests/test_prompt_sync.py:56`.
- **F4.** `tests/test_prompt_sync.py:152` pins the executor's plugin literals but not `compact_stats`, so the doc could regress silently.

## Local TODOs

- [x] Step 1: Create task file and move it to `tasks/in-progress/`
- [x] Step 2: Update `agents/cognitive-executor.md` (tool list plus evidence-reset rule)
- [x] Step 3: Update `docs/compaction.md` (Tool C, goal evidence reset)
- [x] Step 4: Update `README.md` plugin description
- [x] Step 5: Pin `compact_stats` in `tests/test_prompt_sync.py`
- [x] Step 6: Refresh the smart-compact plugin-policy memory shard
- [x] Step 7: Append the `CHANGELOG.md` entry
- [x] Step 8: Verify, stage, QA transition, closure

## Acceptance Criteria

- [x] `agents/cognitive-executor.md` names `compact_stats` beside the two existing tools and states that `goal_set` starts with an empty evidence sidecar
- [x] `docs/compaction.md` documents `compact_stats` as read-only with no inputs, and states the evidence-reset rule in the goal plugin section
- [x] `README.md` plugin description mentions `compact_stats` and the evidence reset
- [x] `tests/test_prompt_sync.py` pins `compact_stats` in the executor literal list and still passes
- [x] The smart-compact policy memory shard lists the third tool
- [x] `CHANGELOG.md` carries one entry for the doc sync
- [x] `pytest tests/test_prompt_sync.py` exits 0, `lint_system_prompt_sync` is consistent, `lint_markdown` passes on every touched Markdown file

## Execution Log & Reasoning

**Graph first, then grep to read the lines.** `build_graph` on this worktree produced 4,766 nodes and 6,788 links. Queries for both plugin names returned file and section nodes, which gave the candidate set; the INFERRED edges were too noisy to act on (they linked unrelated modules through shared tokens), so every actual sentence was read with a targeted grep. Living files that name either plugin: `agents/cognitive-executor.md`, `docs/compaction.md`, `README.md`, `CHANGELOG.md`, the two `opencode_config` memory shards, `tests/test_prompt_sync.py`, `.opencode/smart-compact.jsonc`, and `prompts/archive/22-compaction_protocol.md`.

**What was actually stale.** `compact_stats` appeared in zero living files, and both goal-plugin fixes appeared nowhere. Everything else was either frozen history (`docs/history/`, `tasks/archive/`, `tasks/completed/`, `prompts/archive/`) or deliberately plugin-blind (`system-prompt.md` and `prompts/fragments/`, pinned by `test_shipped_prompt_is_plugin_blind`). Task 332 had already synced the per-session and observed-proof wording, so this pass only had to add the two newer behaviors rather than rewrite that section.

**Where each rule went.** The executor is the Hands' own instruction file, so both rules land there: the tool list gains `compact_stats`, and the goal boundary now states that a set starts a fresh sidecar and that the legacy evidence file is read only until the session owns one. The guide and README repeat both for the human reader. The test pin is what stops the executor from drifting back, which is cheaper than a review finding it later.

**Assumption A1.** Frozen history stays frozen. Reason: rewriting `docs/history/` or archived tasks would falsify what those records said at the time, and the repo treats them as audit trail.

**Assumption A2.** No `<system_version>` bump. Reason: the version pins the assembled Brain prompt, `system-prompt.md` and `prompts/fragments/` were not touched, and `lint_system_prompt_sync` confirms the assembly is unchanged.

**Assumption A3.** `prettier --check` is not a valid gate here. Reason: all four touched files were already non-conforming at `HEAD` (verified by running prettier against `git show HEAD:<file>`), so making them pass would mean reformatting whole long-form documents inside a docs-sync task. The reachable gate is `lint_markdown`, which passes on all five files.

**Assumption A3.** `prettier --check` is not a valid gate here. Reason: all four touched files were already non-conforming at `HEAD` (verified by running prettier against `git show HEAD:<file>`), so making them pass would mean reformatting whole long-form documents inside a docs-sync task. The reachable gate is `lint_markdown`, which passes on all five files.

**Memory shard.** Refreshed through `store_memory` with `overwrite`, which rewrote the frontmatter `created_at` to today; the original 2026-10-13 date survives in the body as the first refresh entry. One lint finding (missing blank line after the H1, inherited from the original) was fixed with the edit tool.

**Assumption A4.** The task id moved from 0339 to 0341. Reason: another session created `tasks/backlog/0339-planner-dashboard-ui-overhaul-and-task-modal.md` and `0340-system-prompt-planner-protocol-integration.md` while this task was being written, so 0339 was duplicated. This task was untracked and unshared, so it yielded and renumbered rather than editing another session's files.

## Verification Evidence

- Command: `rtk test uv run --project mcp-context-server --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q` | Expected: all pass | Actual: 16 passed in 0.16s | Exit: 0.
- Tool: `lint_system_prompt_sync` | Expected: assembly unchanged | Actual: `system-prompt.md is in sync with prompts/`.
- Tool: `lint_markdown` on `agents/cognitive-executor.md`, `docs/compaction.md`, `README.md`, `CHANGELOG.md`, and the memory shard | Expected: clean | Actual: all five pass.
- Check: `grep -c compact_stats` across living HQ files | Expected: executor, guide, README, test, memory | Actual: each of the five carries it.
- Check: `prettier --check` on the four touched Markdown files | Actual: dirty, but dirty at `HEAD` too for each one, so no regression was introduced.

## Risk & Rollback

- Risk: the executor prompt grows. Two short clauses, no restructuring.
- Risk: editing a shipped prompt by hand drifts from the fragment source. Not applicable here: `agents/*.md` is not assembled into `system-prompt.md`, and `test_shipped_prompt_is_plugin_blind` keeps plugin detail out of the Brain prompt.
- Rollback: revert the touched doc files; no code or config depends on the wording.

## Factual Git Diff

- Injected below via `custom_context_stage_and_inject_diff`.

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `1bc2c0858f90b66feaed2ce1c826aedc39d9b380`
<!-- END_GIT_DIFF -->
