# Task 78: Fix commit_and_clean_task orphaned hash bug

**File:** `tasks/completed/78-fix-commit-and-clean-task-orphaned-hash.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Fix the `commit_and_clean_task` MCP tool in `mcp-context-server/server.py` so the commit hash stored in the task file always references a commit reachable from HEAD. The tool previously captured the hash before `git commit --amend`, which orphaned the stored commit and broke `git show <hash>` audit trails.

## Manager's Notes

- The bug was reported with reflog evidence; the same pattern exists in this repo's own history (`df48833` referenced by Task 77 is unreachable; `aa72dc7` from Task 75 is orphaned).
- Preferred fix direction: eliminate the amend entirely (two-commit flow: feature commit + `chore: close task N` closure commit). The amend-based "capture hash after amend" alternative leaves the tree dirty and still orphans H1, so it was rejected.
- The system prompt already documents the ZAC lifecycle (CRITICAL RULE 2 in `<bash_phase>`), so no system-prompt change is required for the compliance gap — that was a Zen Router project issue, not this repo.
- Deployment note: `~/.config/opencode/mcp-context-server/server.py` (global copy for other projects) is NOT modified by this task; the local `opencode.json` already points at this repo's server via `uv run mcp-context-server/server.py`.

## Local TODOs

- [x] Rewrite `commit_and_clean_task` in `mcp-context-server/server.py` — remove amend, add closure commit + idempotency guard
- [x] Fix `stage_and_inject_diff` crash on ignored `context-reports/` (negative pathspec → `git add` + `git reset` defense)
- [x] Add regression tests for both fixes
- [x] Run full test suite and verify all criteria (reachability, no amend, idempotency, staging)
- [x] Update CHANGELOG.md and close this task

## Acceptance Criteria

- [x] The hash stored in the task file equals the feature commit hash and is reachable from HEAD after `commit_and_clean_task` returns (`git merge-base --is-ancestor <hash> HEAD` succeeds).
- [x] `git show <stored_hash>` returns the diff that includes the code changes.
- [x] No commit becomes orphaned after a normal task closure (no `commit (amend)` entries in reflog).
- [x] Calling `commit_and_clean_task` twice on the same task does not create a second commit (idempotency guard).

## Verification Evidence

- **Test command:** `uv run --with "mcp>=1.0,<2.0" --with pathspec --with pyyaml --with pytest pytest tests/test_mcp_servers.py -q`
- **Expected result:** 6 tests pass, including the new `test_commit_and_clean_task_stores_reachable_hash`
- **Actual result:** `6 passed in 1.85s`
- **Exit code:** 0

## Risk & Rollback

- **Risk:** The tool now produces two commits per closure (feature + close) instead of one amended commit; commit count per closure increases, but no orphans are created and the `chore: close task N` pattern already exists in this repo's history.
- **Rollback plan:** Revert `mcp-context-server/server.py` to the previous amend-based implementation; the idempotency guard and closure-commit behavior are self-contained in the one function.

---

## OpenCode Execution Log & Reasoning

### Execution Summary

**Root cause confirmed:** `commit_and_clean_task` captured `git rev-parse HEAD` (H1) *before* `git commit --amend --no-edit`. The amend replaced H1 with H2, leaving the stored H1 orphaned (reachable only via reflog, ~30 days). Repo evidence: reflog shows `df48833` (referenced in Task 77's log) and `aa72dc7` are unreachable from HEAD.

**Fix (architectural reasoning):** An amend-based flow cannot satisfy both "stored hash == HEAD" and "no orphans" — writing the hash into the file before amending stores a stale hash, while capturing it after amending leaves the file edit uncommitted (dirty tree) and still orphans H1. The only clean design is a **two-commit flow**:

1. `git commit -m <message>` → feature commit H1
2. `git rev-parse HEAD` → store H1
3. Clean task file diff block → `**Factual Git Diff:** Stored in Commit Hash: H1`
4. `git add -A tasks/` (keeps the Task 47 fix for kanban moves/deletions)
5. `git commit -m "chore: close <slug>"` → closure commit; H1 stays permanently reachable as its parent

Also added:
- **Idempotency guard** (checks for existing `Stored in Commit Hash:` before the empty-staged check) — prevents double-commit on repeated calls.
- **`_derive_task_slug`** helper — builds the `chore: close task NN - <slug>` message from the task filename, matching the repo's existing close-commit convention.
- **Removed the upstream-push amend warning** — no longer applicable since the tool never amends.
- The empty-staged safety check from Task 71 is retained.

**Files modified:**
- `mcp-context-server/server.py` — rewritten `commit_and_clean_task` + new `_derive_task_slug` helper; also fixed `stage_and_inject_diff` (see below)
- `tests/test_mcp_servers.py` — added regression tests covering reachability, no-amend history, `git show` of the stored hash, idempotency, and staging with an ignored `context-reports/` dir
- `CHANGELOG.md` — [Unreleased] Fixed entry

### Second bug found & fixed (same pipeline): `stage_and_inject_diff` crash on ignored `context-reports/`

While closing this task, the MCP `stage_and_inject_diff` tool failed with exit 1:
`The following paths are ignored by one of your .gitignore files: context-reports`.

**Root cause:** the tool ran `git add . :!*.env :!*.env.* :!*.key :!*.pem :!credentials* :!secrets* :!context-reports/ :!.opencode/cache/`. When any excluded path *actually exists on disk and is ignored* (the `context-reports/` directory had accumulated reports from earlier sessions), git treats the pathspec match against the ignored path as an error and exits 1 — even though nothing is staged. This blocked every subsequent closure until the reports were deleted. (Verified: plain `git add .` exits 0; adding `--ignore-errors` does NOT suppress this error.)

**Fix:** replace the negative-pathspec `git add` with plain `git add -A .` (which already respects .gitignore) followed by defense-in-depth unstaging of sensitive patterns via `git reset -q -- <pattern>` (`*.env`, `*.key`, `*.pem`, `credentials*`, `secrets*`, `context-reports/`, `.opencode/cache/`). Verified: exit 0, correct staging, no sensitive/ignored files staged.

### Third fix: idempotency guard false-positive (self-referential diff)

After the first restart, `stage_and_inject_diff` succeeded (staging fix confirmed live), but `commit_and_clean_task` returned "Task file already cleaned" without committing. Root cause: the guard's naive substring search (`if "Stored in Commit Hash:" in existing`) matched the task file's own injected raw diff — the diff contained the guard's source line (`if "Stored in Commit Hash:" in existing:`) and the CHANGELOG mention of the phrase. The guard saw its own code and blocked the closure.

**Fix:** the guard now matches only the exact cleaned-block structure (`<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `84efaae633ec5203d5bcc77d1b0920b5a010751e`
<!-- END_GIT_DIFF -->
