# Task 411: Refresh stale global-install memory records

**File:** `tasks/completed/411-refresh-stale-memory-records.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-22T12:50:02Z
**Submitted:** 2026-11-22T12:45:58Z

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Update two stale memory shards discovered during the global-install drift audit so memory matches live machine state: the version record (OpenCode/OpenChamber) and the blowsh image/proxy policy record (Psiphon EgressRegion). No product code, no global-install file copies (those were done in the same session as a pure sync), no commit.

## Manager's Notes

- Manager asked to sync drifts and the global installation base using the project-memory workflow.
- Manager chose "Sync + fix memories now", accepting a task file for the memory-change portion per the refined no-task rule.
- Version memory key `opencode_config/opencode_openchamber_versions_2026_11_02` says OpenCode 2.3.0 / OpenChamber 2.7.1; live is 2.3.2 / 2.7.3 (verified this session).
- Blowsh policy memory key `opencode_config/blowsh_image_policy` says EgressRegion US / US exit IP; live is EgressRegion DE with a verified DE exit (verified this session, `loc=DE`, `ip=172.105.78.25`).

## Local TODOs

- [ ] Overwrite the version memory with live versions and a current verification date
- [ ] Overwrite the blowsh policy memory with EgressRegion DE and the verified DE exit
- [ ] Confirm the memory index reflects the updated summaries

## Acceptance Criteria

- [x] Both memory records carry current, verified facts
- [x] Supersession is logged inside each memory's content
- [x] The memory index is regenerated and shows the new summaries

## Verification Evidence

- **Test command:** rtk test python3 -m pytest tests/test_prompt_sync.py -q
- **Expected result:** suite passes; memory writes do not alter prompt artifacts
- **Actual result:** `44 passed in 0.43s`
- **Exit code:** `0`
- **Exact command run:** `rtk test /home/mohammad/hesab-ketab/.venv/bin/python -m pytest tests/test_prompt_sync.py -q`
- **Memory writes:** both `store_memory` calls succeeded; `rebuild_memory_index` reported 33 memories indexed; index row for the version key now reads `verified 2026-11-22`

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

## Risk & Rollback

- **Risk:** memory content is derived state; a wrong overwrite misleads future sessions. Mitigation: copy the old content into the supersession note.
- **Rollback plan:** restore the prior memory bodies via `store_memory` with the pre-change content.

---

## Execution Log & Reasoning

### Global-install sync (pure sync, no task file)

Audit via the `workflows/global-install-upgrade` memory found four drifted surfaces: `agents/cognitive-executor.md`, `system-prompt.md`, six `build/stage-prompts/system-prompt.*.md` artifacts, and a missing `mcp-lint-server/tests/test_deleted_skill_refs.py`. Copied each to its `~/.config/opencode/` target and re-audited: all now `OK`. The 24 skills, the other agent, shell strategy, all MCP sources, mcp-common and planner static were already clean. Agents dir holds exactly two files; no orphans. `opencode.json` was left untouched (repo relative vs global absolute).

### Memory refresh (this task)

- `opencode_config/opencode_openchamber_versions_2026_11_02`: OpenCode 2.3.0 → 2.3.2, OpenChamber 2.7.1 → 2.7.3, verification date 2026-11-13 → 2026-11-22. Full prior body preserved with a `Supersedes` note.
- `opencode_config/blowsh_image_policy`: EgressRegion US → DE, live exit updated to `172.105.78.25`/`loc=DE`/`colo=FRA`, tag `psiphon-proxy:de`, and the 2026-11-22 operator clarification recorded. Full prior body preserved with a `Supersedes` note.
- `rebuild_memory_index` regenerated `.opencode/memory/index.md` (33 rows); the version row now reads `verified 2026-11-22`.

### Assumptions

- A1: the missing `test_deleted_skill_refs.py` is a genuine sync target because the workflow says multi-module servers copy `*.py` (never `__pycache__/`).
- A2: memory shards are git-tracked (34 files), so overwriting them counts as repo work and justifies this task file under the refined no-task rule.

### User-visible outcome

The running agent and prompt artifacts now match the repo. The Manager must restart OpenCode and OpenChamber for the new global copies to load; the Hands never restart the editor or app.

### Review chain

- Code Reviewer: technically approved, `Status: PO_REVIEW_PENDING` — awaiting final Manager sign-off.
- Low-severity notes (no fix required): memory shards lack a trailing newline; the global re-audit clean claim has no pasted command output; `Status` remains `open` while the file is in `tasks/qa/`. All three are cosmetic or metadata and change no fact.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `e88064afde66d4f77a9bdc3ce429f2434b9f2500`
<!-- END_GIT_DIFF -->
