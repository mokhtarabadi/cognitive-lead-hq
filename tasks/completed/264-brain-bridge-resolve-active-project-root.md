# Task 264: Brain Bridge resolves the active project root for the context bundle and file-pull tools

**File:** `tasks/completed/264-brain-bridge-resolve-active-project-root.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Fix GitHub issue #24: the Brain Bridge auto-context-bundle and the Hand-facing file-pull tools must read from the ACTIVE project root, not from the bridge install directory. Root cause (issue): `_build_context_bundle()` takes no args and every read path resolves against `_workspace_root()`, which falls back to `Path(__file__).resolve().parent.parent` (the install dir) when `BRAIN_WORKSPACE_ROOT` is unset. The same `brain_turn` already resolves the correct project root for the task file and `context_paths`, but never passes it to the bundle builder; `brain_get_context_bundle`, `brain_read_file`, `brain_grep_files` share the same fallback.

Issue: https://github.com/mokhtarabadi/cognitive-lead-hq/issues/24

## Manager's Notes

- Requested by the Manager: "fix this issue ... full automatic".
- Fix lands in the vendored `mcp-brain-bridge/` source in this repo. The deployed copy at `~/.config/opencode/mcp-brain-bridge/` is the Manager's to deploy; this task does NOT touch it.
- Preserve `BRAIN_WORKSPACE_ROOT` semantics exactly (explicit override wins, no `tasks/` requirement).
- ZAC applies: no `git add`/`commit`/`push`.

## Local TODOs

- [x] Thread a resolved `root` argument through `_build_context_bundle`
- [x] Make `_workspace_root()` fall back to the active project root (cwd walk-up) instead of the install dir, install dir only as a loud last resort
- [x] Pass the resolved project root to the bundle candidate inside `brain_turn`
- [x] Add regression tests (bundle root follows explicit `project_root`; cwd walk-up; brain_turn end-to-end)
- [x] Verify with the bridge test suite

## Acceptance Criteria

- [x] With no `BRAIN_WORKSPACE_ROOT` set and a `project_root` passed to `brain_turn`, the bundle reads `agents/cognitive-executor.md` + `docs/*` + `DESIGN.md` from the passed project root, not the install dir.
- [x] On a project with no `docs/`, `[missing: ...]` markers appear only for genuinely absent files.
- [x] `brain_get_context_bundle`, `brain_read_file`, `brain_grep_files` resolve against the active project root.
- [x] A regression test asserts the bundle root follows `project_root`.
- [x] Existing test suite stays green (no behavior regression for `BRAIN_WORKSPACE_ROOT` overrides).

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_preflight.py -q`
- **Expected result:** all tests pass, including the new root-resolution regression tests
- **Actual result:** `tests/test_brain_bridge.py` **243 passed** (238 baseline + 5 new) in 1.33s; all bridge-adjacent suites (`test_brain_bridge.py test_brain_preflight.py test_brain_diff_attach.py test_brain_capability.py test_session_lifecycle.py test_authority_retrieval.py test_brain_transport_learning.py test_eval_harness.py test_golden_cases.py test_golden_replay.py test_loop_guard.py`) **411 passed** in 1.48s. `pytest tests/` (whole dir) still fails at COLLECTION on `tests/test_bundle_tasks.py` with `ModuleNotFoundError: No module named 'pathspec'` — pre-existing environment limitation (the context-server dep is not in the bridge venv), unrelated to this change.
- **Exit code:** 0 (both RTK runs)

> Verification runner rule: `uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_preflight.py -q` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Changing the `_workspace_root()` fallback could redirect reads for a caller that relied on the install-dir default. Mitigation: the explicit `BRAIN_WORKSPACE_ROOT` override still wins first; the install dir remains a loud last resort; the existing suite pins the override behavior.
- **Rollback plan:** revert the `mcp-brain-bridge/server.py` and `tests/test_brain_bridge.py` hunks.

---

## Execution Log & Reasoning

**Goal:** Fix GitHub issue #24 — the auto-context-bundle and Hand-facing file-pull tools must read the ACTIVE project root, not the bridge install dir.

### Changes

**`mcp-brain-bridge/server.py`**

1. **Imports** — added `resolve_project_root as _resolve_project_root` to both the packaged (`mcp_brain_bridge.preflight`) and fallback (`preflight`) import branches.
2. **`_workspace_root()`** — rewritten. Order is now: explicit `BRAIN_WORKSPACE_ROOT` override (wins outright, no `tasks/` requirement) → `preflight.resolve_project_root(None, env=os.environ, cwd=Path.cwd())` (honours `BRAIN_PROJECT_ROOT`, then a cwd `tasks/` walk-up) → install dir as a loud stderr-noted last resort. This one change corrects every downstream read path (`_resolve_under_root`, `_read_file_impl`, `_grep_files_impl`, `get_context_bundle`, `_paths_base`, and the workspace fallback in `_resolve_task_file`). The function is still replaced wholesale by tests that monkeypatch it, so existing tests keep working.
3. **`_explicit_root(project_root)`** — new helper that coerces an optional project-root string to a resolved `Path` (or `None`).
4. **`_build_context_bundle(root=None)`** — gained an optional `root`; when given it is pinned, otherwise `_workspace_root()` is used. All existing no-arg callers keep working.
5. **`_read_file_impl(..., project_root=None)`** and **`_grep_files_impl(..., project_root=None)`** — widened signatures; both pin the resolved explicit root when provided.
6. **Tools `get_context_bundle`, `read_file`, `grep_files`** — each gained `project_root: Optional[str] = None` and forwards it.
7. **`brain_turn` bundle candidate** — now calls `_build_context_bundle(project_root)` using the turn's already-resolved root, matching the task/path/diff candidates.

### Assumptions & Decisions

- **A1 — one-off turns re-pin the root (Edit 9).** `preflight.validate_request` deliberately sets `project_root = None` for one-off (unbound) turns. Discovered by the new end-to-end test: an explicit `project_root` on a one-off `brain_turn` was dropped, so the bundle fell back to the ambient decoy. Fixed at the `brain_turn` boundary — when the binding is one-off and the caller passed an existing directory, it is re-pinned for the bundle/file-pull attaches. Preflight was left untouched because one-off-has-no-binding is intentional and tested. Only new behavior is enabled; bound and rootless turns are unchanged.
- **A2 — no `opencode.json` env edit.** The issue's belt-and-braces suggestion (add `BRAIN_PROJECT_ROOT` to the `brain` server `environment` block) targets the deployed `~/.config/opencode/opencode.json`, which is outside this workspace; the repo `opencode.json` carries no `mcp` block by design (project-only contract). Deploy is the Manager's. The code fix is the fix.
- **A3 — install dir retained as a last resort.** Removing it entirely would break `test_no_tasks_dir_falls_back_to_legacy`; the loud stderr note names the remedy instead of changing behavior.

### TDD note

Tests were written alongside the edits; the end-to-end one-off test failed first (proving the drop), which drove Edit 9 — the fix then turned it green.

### Verification

- Baseline before changes: 238 passed.
- After: `tests/test_brain_bridge.py` → **243 passed** (5 new regression tests).
- All bridge-adjacent suites → **411 passed**.

### Autopilot Turn Log (Manager lock: "use brain auto pilot mode for this task")

- **brain_turn #1 — stage=qa, `include_diff=true` → verdict `QA_PASSED`.** Adversarial audit of the staged hunks found no reproducible defect. Confirmed: F1 explicit root beats the ambient `BRAIN_WORKSPACE_ROOT` decoy; F2 the one-off re-pin is correctly scoped and leaves bound/rootless turns untouched; F3 `_workspace_root()` cannot raise into a read path; F4 all 5 new tests assert observable behaviour; F5 no path-escape or allowlist regression (the suffix allowlist and `_resolve_under_root` confinement still apply). Non-blocking observations: O1 the re-pin couples to the `"one-off"` string literal; O2 no existence check on `project_root` for read/grep (degrades to empty/`[missing]`); O3 control-flow-via-exception in `_workspace_root()` with a stderr note per unresolvable call. Cited: `mcp-brain-bridge/server.py:295,331,647,2914`, `tests/test_brain_bridge.py:582`.

- **brain_turn #2 — stage=review, `include_diff=true` → verdict `APPROVED` (technical) → `PO_REVIEW_PENDING`.** The Code Reviewer found no issue requiring changes and no scope creep beyond issue 24. Confirmed: the bundle accepts and uses the explicit root; `brain_turn` passes the same resolved root; the one-off re-pin is limited to explicit existing roots; `_workspace_root()` keeps `BRAIN_WORKSPACE_ROOT` precedence with the install dir only as a logged last resort; the file-pull tools forward the root with extension checks and path confinement intact; the 5 regression tests assert observable behaviour; the CHANGELOG entry matches the diff and the recorded counts. Note: the issue text names the tools `brain_get_context_bundle` / `brain_read_file` / `brain_grep_files`, while the module exposes them as `get_context_bundle` / `read_file` / `grep_files` — the diff updates those actual consumers. Cited: `mcp-brain-bridge/server.py:293-315,647,720,766,799-840,2914,2994`, `tests/test_brain_bridge.py:586-691`, `CHANGELOG.md:33`.
- **Autopilot halt at the review-approval gate.** Autopilot does not satisfy the closure gate; the relay question was surfaced to the Manager verbatim and the task stays in `tasks/qa/`.
- **Manager acceptance (verbatim):** `Approved for clousre` — the Manager's direct reply to the relayed closure question. Read as the typo of the required phrase `Approved for closure`; a bare `approved` in this exact position already satisfies the gate, and this message carries both the approval word and the closure intent, so it is accepted as the closure authorization.
- **brain_turn #3 — stage=closure (Senior Programmer) → final closure XML.** Requested after acceptance, per the review-approval relay sequence. The Brain confirmed the gate preconditions (explicit approval word, file in `tasks/qa/`, log records `PO_REVIEW_PENDING`, `QA_PASSED` + technical `APPROVED`), normalised `clousre` → `closure`, and issued the closure XML once (D1 `git mv` qa→completed; D2 status `open`→`closed` + `**File:**` repointed; D3 feature commit `fix: resolve active project root for bridge bundle and file tools`, 66 chars, Conventional Commits; D4 commit only through `custom_context_commit_and_clean_task`). Executed that XML exactly once, unmodified.
- **Closure executed.** `git mv tasks/qa/... → tasks/completed/...`; `**Status:** closed`; `**File:**` header repointed to the completed path; `lint_task_file` re-run green; closure commit issued via the MCP tool only. ZAC held: no `git add` / `git commit` / `git push` by the Hands.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `2fdda043c8f90544cde88883b96dda0b863a113c`
<!-- END_GIT_DIFF -->
