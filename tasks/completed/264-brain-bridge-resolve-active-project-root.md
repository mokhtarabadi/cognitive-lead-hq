# Task 264: Brain Bridge resolves the active project root for the context bundle and file-pull tools

**File:** `tasks/qa/264-brain-bridge-resolve-active-project-root.md`
**Source:** manager
**Type:** bug
**Status:** open

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

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 3574e99..41e6d32 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -30,6 +30,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Brain Bridge resolves the active project root for the bundle and file-pull tools (Task 264, fixes GitHub issue 24):** the auto-attached context bundle (`kind: "bundle"`) and the Hand-facing file-pull tools always read from the bridge INSTALL directory unless `BRAIN_WORKSPACE_ROOT` was exported, so real project docs (`docs/conventions.md`, `docs/architecture.md`, `docs/data_model.md`, `DESIGN.md`) were marked `[missing]` on every `brain_turn` in any other project. `_build_context_bundle()` now takes an optional `root`; `_workspace_root()` no longer defaults to the install dir — it keeps the explicit `BRAIN_WORKSPACE_ROOT` override first, then auto-resolves the ACTIVE project root via `preflight.resolve_project_root` (`BRAIN_PROJECT_ROOT`, then a cwd `tasks/` walk-up), and only falls back to the install dir as a loud stderr-noted last resort. The bundle call site in `brain_turn` now passes the turn's already-resolved project root, and because `preflight` deliberately drops an explicit root on one-off (unbound) turns, the `brain_turn` boundary re-pins it for the bundle and file-pull attaches when it is an existing directory. A new `_explicit_root` helper threads the same root through `get_context_bundle`, `read_file`, and `grep_files`, which all gained an optional `project_root` argument; the single `_workspace_root()` change also corrects `_resolve_under_root`, `_paths_base`, and the workspace fallback in `_resolve_task_file`. 5 new regression tests (explicit root beats an env decoy, tool-level root pin, cwd walk-up, read+grep root pin, end-to-end one-off `brain_turn`). Full bridge suite: **243 passed**; all bridge-adjacent suites: **411 passed**.
+
 - **Decision server bounds the transcript prompt and fails loudly on a bad config value (Task 263):** the extraction call joined the whole session transcript into its prompt with no ceiling, so a long session produced an unbounded request — the same starvation class as issue 23 — and two config readers silently papered over a bad setting instead of reporting it. `extract_session_decisions()` now caps the joined transcript at `DECISION_TRANSCRIPT_MAX_CHARS` (default 131072 characters, blank-means-unset) BEFORE the prompt is built, keeping the first N characters and appending `[...truncated at <dropped> chars]` so the caller learns exactly how much was dropped; `transcript_bytes` stays the raw file content used by the cache key. `_get_decision_max_tokens()` (default 16384) and `_get_decision_temperature()` (default 1.0, range 0.0-2.0) now raise `ValueError` naming the variable and the bad value instead of falling back to 16384 or clamping to 1.0. The Responses request shape is unchanged (`model`, `input`, `max_output_tokens`, plus either `temperature` or nested `reasoning.effort`). 5 new tests. Full suite: **665 passed**.
 - **Brain Bridge sees the whole change set: configurable caps + one shared budget (Task 262, syncs GitHub issue 23):** the bridge appended every attachment against its own hard-coded constant, so a reviewer lost the hunks to boilerplate and every seat reported `[...truncated …]` mid-file. Four module defaults moved (`_TASK_ATTACH_CAP` 12000→60000, `_TASK_DIFF_CAP` 20000→200000, `_CTX_PATHS_PER_FILE` 20000→60000, `_CTX_PATHS_TOTAL` 40000→200000) and six caps gained blank-means-unset env overrides (`BRAIN_TASK_ATTACH_CAP`, `BRAIN_TASK_DIFF_CAP`, `BRAIN_CTX_PER_FILE_CAP`, `BRAIN_CTX_TOTAL_CAP`, `BRAIN_INPUT_BUDGET`, `BRAIN_MODEL_WINDOW_CHARS`) resolved at call time through the new `_env_positive_int`, which rejects malformed or non-positive values instead of clamping; `_INPUT_BUDGET` moves 100000→200000 because a live probe showed the assembled system prompt alone is ~87.6k chars, leaving the older ceiling only ~12k for the change set (200k chars is ~43k input tokens at the measured ~4.6 chars/token). The independent append sequence in `brain_turn` is replaced by one shared allocator that renders candidates against the chars actually left after the system prompt and the caller's prompt; `qa`/`review` turns rank context_paths → diff → task → fed context → bundle so explicit evidence outranks the small-file bundle, while history stays the last fallback and is deliberately excluded from the attachment budget (that keeps the static prompt-cache prefix stable across turns). Over-budget attachments chunk into numbered parts with an exact resume offset (`[ATTACHMENT kind=… part=1/3 …]` / `[NEXT_ATTACHMENT_PART … next_offset_chars=…]`) and the new `attachment_resume={"kind","path","offset_chars"}` argument continues them; a malformed resume is ignored with a stderr note. The result payload now splits the two failure modes: `history_turns_dropped` is canonical with `truncated_count` kept as the back-compat alias, and `attachments_truncated` (always a list; entries carry `kind`/`path`/`shown_chars`/`total_chars`/`dropped_chars`/`part`/`parts`) reports attachment loss alongside `attachment_parts`, `attachment_budget_chars`, `attachment_chars_used`, and `attachment_chars_remaining`; the capability-blocked early return carries the same field set. The three standalone builders keep their truncating behaviour for direct callers. `docs/brain-bridge.md` gains the new env-table rows and sections on the allocator, the priority order, the part/resume contract, and the two-truncation payload. The stored transcript no longer keeps the assembled prompt: each user turn is persisted with a compact `[stored-attachment kind=… path=… shown_chars=… total_chars=… part=a/b]` marker per segment instead of the attachment bodies, because every later turn replays the transcript — persisting the bodies made each turn re-pay the previous turn's attachment cost (one QA turn stored a 64,547-char user turn and every turn after it inherited it). The wire prompt is unchanged: attachments are re-derived from disk each turn, so only storage shrinks. The transcript file itself is append-only: every turn ever written stays on disk, and only the load VIEW is compacted in memory (one deterministic digest record plus the newest records), so a task keeps its full history while the send path stays bounded — the lossy rewrite helpers were removed. 27 new tests (cap readers, 60 KB file untruncated at both the builder and the turn level, part numbering + resume, priority order, separate reporting, chunk numbering, review-over-bundle precedence, compact transcript storage, append-only transcript storage) plus 2 regressions in `tests/test_brain_diff_attach.py` for the diff extractor (a `<!-- END_GIT_DIFF -->` marker inside a diff body no longer ends extraction, so a change set that edits the bridge's own marker constants is delivered whole), 3 loud-failure regressions proving a malformed or non-positive cap environment value fails the turn instead of being reported as an unavailable attachment, and 3 existing tests re-pinned to explicit caps. A malformed cap env value is now read outside the candidate guards so the configuration error propagates, and the part-marker reservation is measured from the lines actually emitted (`_marker_room`) instead of a fixed constant, so the running attachment total can no longer exceed the budget. The wrapper a rendered attachment emits (its open line, fence lines and separators, not just the part markers) is now priced against the room the allocator granted, so a block can never be longer than its budget, and the configured per-file cap bounds the CONTENT with the wrapper riding on top — a file that fits its cap exactly still arrives whole. Every `context_paths` file also shares one configured total budget (`BRAIN_CTX_TOTAL_CAP`), enforced across the whole group by the allocator with the overflow reported rather than silently sent, and a malformed or non-positive path cap fails the turn loudly like the task and diff caps do. Full suite: **660 passed**.
 
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index e427e12..bbc9178 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -108,12 +108,14 @@ try:
     from mcp_brain_bridge.preflight import (  # type: ignore[import-not-found]
         PreflightError,
         require_bare_task_id,
+        resolve_project_root as _resolve_project_root,
         validate_request as _validate_request,
     )
 except ImportError:
     from preflight import (  # type: ignore[import-not-found]
         PreflightError,
         require_bare_task_id,
+        resolve_project_root as _resolve_project_root,
         validate_request as _validate_request,
     )
 
@@ -291,11 +293,30 @@ _GREP_MAX_LINE_CHARS = 4000   # overlong lines are skipped, never searched
 
 
 def _workspace_root() -> Path:
-    """Repo root for context reads; override via ``BRAIN_WORKSPACE_ROOT``."""
+    """Repo root for context reads; override via ``BRAIN_WORKSPACE_ROOT``.
+
+    Resolution order (issue #24): an explicit ``BRAIN_WORKSPACE_ROOT``
+    override wins outright; otherwise auto-resolve the ACTIVE project root
+    (``BRAIN_PROJECT_ROOT``, then a cwd ``tasks/`` walk-up) so the bundle and
+    the file-pull tools read the project the turn actually runs in, never the
+    directory this bridge happens to be installed into. Only when both fail
+    does it fall back to the install dir, with a loud stderr note naming the
+    remedy.
+    """
     override = os.environ.get("BRAIN_WORKSPACE_ROOT", "").strip()
     if override:
         return Path(override).expanduser().resolve()
-    return Path(__file__).resolve().parent.parent
+    try:
+        return _resolve_project_root(None, env=os.environ, cwd=Path.cwd()).resolve()
+    except Exception as exc:  # defensive last resort: never break a read
+        install_root = Path(__file__).resolve().parent.parent
+        print(
+            "brain-bridge: could not resolve the active project root "
+            f"({exc}); falling back to the bridge install dir {install_root}. "
+            "Set BRAIN_PROJECT_ROOT (or BRAIN_WORKSPACE_ROOT) to silence this.",
+            file=sys.stderr,
+        )
+        return install_root
 
 
 def _resolve_under_root(rel: str, root: Optional[Path] = None) -> Path:
@@ -307,6 +328,18 @@ def _resolve_under_root(rel: str, root: Optional[Path] = None) -> Path:
     return candidate
 
 
+def _explicit_root(project_root: Optional[str]) -> Optional[Path]:
+    """Coerce an optional project-root string to a resolved Path.
+
+    ``None`` stays ``None`` so callers fall back to ``_workspace_root()``;
+    this is the shared coercion for the file-pull tools so an explicitly
+    passed root always beats ambient resolution (issue #24).
+    """
+    if project_root is None:
+        return None
+    return Path(project_root).expanduser().resolve()
+
+
 _TASK_DIFF_BEGIN = "<!-- BEGIN_GIT_DIFF -->"
 _TASK_DIFF_END = "<!-- END_GIT_DIFF -->"
 _TASK_FILE_MARKER = "[task-file:"
@@ -611,16 +644,23 @@ def _failsafe_qa_attach(
     return ""
 
 
-def _build_context_bundle() -> str:
+def _build_context_bundle(root: Optional[str] = None) -> str:
     """Assemble the labeled small-file bundle (never raises on Absent-File).
 
+    ``root`` pins the project the bundle is read from (issue #24): when the
+    caller already resolved the turn's project root it MUST pass it here, so
+    the bundle follows the active project instead of the bridge install dir.
+    ``None`` keeps the historical behaviour and falls back to
+    ``_workspace_root()``.
+
     The per-file cap applies first; the total cap applies across files so
     five full files can never stuff 300k into one turn. Files past the
     total budget are marked skipped, never silently dropped. The truncation
     suffix length is reserved before slicing, so the appended marker can
     never push the total past the cap (off-by-suffix overflow).
     """
-    root = _workspace_root()
+    _pinned = _explicit_root(root)
+    root = _pinned if _pinned is not None else _workspace_root()
     parts: list[str] = []
     missing = 0
     total = 0
@@ -659,12 +699,19 @@ def _build_context_bundle() -> str:
     return "\n\n".join(parts)
 
 
-def _read_file_impl(path: str, offset: int = 1, limit: int = 200) -> dict[str, Any]:
+def _read_file_impl(
+    path: str,
+    offset: int = 1,
+    limit: int = 200,
+    project_root: Optional[str] = None,
+) -> dict[str, Any]:
     """Numbered-line slice of a workspace text file (1-indexed offset).
 
     The ``limit`` clamps to ``_READ_MAX_LINES`` and files over
     ``_READ_MAX_BYTES`` are refused — pulls stay pull-sized and can
-    never drag a giant file into context.
+    never drag a giant file into context. ``project_root`` pins the tree
+    the path resolves against (issue #24); ``None`` falls back to
+    ``_workspace_root()``.
     """
     if not isinstance(path, str) or not path.strip():
         raise ValueError(f"bad path: {path!r}")
@@ -673,7 +720,7 @@ def _read_file_impl(path: str, offset: int = 1, limit: int = 200) -> dict[str, A
     if limit < 1:
         raise ValueError(f"bad limit: {limit!r}")
     limit = min(limit, _READ_MAX_LINES)
-    resolved = _resolve_under_root(path)
+    resolved = _resolve_under_root(path, _explicit_root(project_root))
     if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
         raise ValueError(f"unsupported extension: {path!r}")
     try:
@@ -697,7 +744,9 @@ def _read_file_impl(path: str, offset: int = 1, limit: int = 200) -> dict[str, A
     }
 
 
-def _grep_files_impl(pattern: str, subdir: str = ".") -> list[str]:
+def _grep_files_impl(
+    pattern: str, subdir: str = ".", project_root: Optional[str] = None
+) -> list[str]:
     """Python-regex search over workspace text files (max 30 hits).
 
     Hardening: the Brain-supplied pattern caps at ``_GREP_PATTERN_MAX``
@@ -705,7 +754,8 @@ def _grep_files_impl(pattern: str, subdir: str = ".") -> list[str]:
     line truncates at 200 chars, lines over ``_GREP_MAX_LINE_CHARS`` are
     skipped unsearched, and every candidate resolves against the root
     BEFORE it is read — a symlink escaping the workspace is skipped,
-    never opened.
+    never opened. ``project_root`` pins the tree searched (issue #24);
+    ``None`` falls back to ``_workspace_root()``.
     """
     if not isinstance(pattern, str) or not pattern:
         raise ValueError(f"bad regex: {pattern!r}")
@@ -716,7 +766,8 @@ def _grep_files_impl(pattern: str, subdir: str = ".") -> list[str]:
         rx = re.compile(pattern)
     except re.error as exc:
         raise ValueError(f"bad regex: {pattern!r} ({exc})") from exc
-    root = _workspace_root().resolve()
+    _pinned = _explicit_root(project_root)
+    root = (_pinned if _pinned is not None else _workspace_root()).resolve()
     base = _resolve_under_root(subdir, root)
     if not base.is_dir():
         return []
@@ -748,25 +799,43 @@ def _grep_files_impl(pattern: str, subdir: str = ".") -> list[str]:
 
 
 @mcp.tool()
-def get_context_bundle() -> str:
-    """Return the labeled small-file context bundle from the workspace root. The Hands call this for bundle proof or debugging; every brain_turn already injects it by default.
+def get_context_bundle(project_root: Optional[str] = None) -> str:
+    """Return the labeled small-file context bundle from the active project root. The Hands call this for bundle proof or debugging; every brain_turn already injects it by default.
 
+    ``project_root`` pins the project the bundle is read from (issue #24);
+    omit it to auto-resolve the active project root (``BRAIN_PROJECT_ROOT``,
+    then a cwd ``tasks/`` walk-up, then ``BRAIN_WORKSPACE_ROOT``).
     Missing files become ``[missing: path]`` marker lines (never raise);
     each file caps at 60000 chars with a ``[truncated]`` marker.
     """
-    return _build_context_bundle()
+    return _build_context_bundle(project_root)
 
 
 @mcp.tool()
-def read_file(path: str, offset: int = 1, limit: int = 200) -> dict[str, Any]:
-    """Read numbered lines from a workspace text file (1-indexed offset). The Hands call this after grep_files locates a hit; the Brain never calls it directly. Text extensions only (.md .txt .json .yaml .yml .toml); Python and other extensions are refused."""
-    return _read_file_impl(path, offset, limit)
+def read_file(
+    path: str,
+    offset: int = 1,
+    limit: int = 200,
+    project_root: Optional[str] = None,
+) -> dict[str, Any]:
+    """Read numbered lines from a workspace text file (1-indexed offset). The Hands call this after grep_files locates a hit; the Brain never calls it directly. Text extensions only (.md .txt .json .yaml .yml .toml); Python and other extensions are refused.
+
+    ``project_root`` pins the tree ``path`` resolves against (issue #24);
+    omit it to auto-resolve the active project root.
+    """
+    return _read_file_impl(path, offset, limit, project_root)
 
 
 @mcp.tool()
-def grep_files(pattern: str, subdir: str = ".") -> list[str]:
-    """Regex-search workspace text files; up to 30 ``path:line: excerpt`` hits. The Hands call this first to locate, then read only the ranges that fit the remaining budget."""
-    return _grep_files_impl(pattern, subdir)
+def grep_files(
+    pattern: str, subdir: str = ".", project_root: Optional[str] = None
+) -> list[str]:
+    """Regex-search workspace text files; up to 30 ``path:line: excerpt`` hits. The Hands call this first to locate, then read only the ranges that fit the remaining budget.
+
+    ``project_root`` pins the tree searched (issue #24); omit it to
+    auto-resolve the active project root.
+    """
+    return _grep_files_impl(pattern, subdir, project_root)
 
 # Prompt overrides must be real prompt files: .md only, resolved under
 # the repo root or ~/.config/opencode (the two legitimate homes).
@@ -2832,6 +2901,7 @@ def brain_turn(
     # session_id are mutually exclusive (exactly one binds history,
     # neither means a one-off turn). The resolved root feeds every
     # downstream resolver so attaches and history share one root.
+    _requested_root = project_root
     _pre = _validate_request(
         project_root=project_root, task_id=task_id, session_id=session_id,
         kanban_path=kanban_path, stage=stage,
@@ -2841,6 +2911,16 @@ def brain_turn(
     session_id = _pre.session_id
     project_root = (str(_pre.project_root)
                     if _pre.project_root is not None else None)
+    # One-off turns intentionally keep no project binding (they persist
+    # nothing), so preflight drops an explicit project_root. An explicitly
+    # passed root must still pin the BUNDLE and file-pull attaches to the
+    # caller's project (issue #24) — otherwise a one-off turn reads the
+    # bridge install dir. Existing-dir guard only: a bad root falls back
+    # to ambient resolution instead of silently reporting all-missing.
+    if project_root is None and _pre.binding == "one-off":
+        _pinned = _explicit_root(_requested_root)
+        if _pinned is not None and _pinned.is_dir():
+            project_root = str(_pinned)
     history_key = _pre.history_key
     _note_checkpoint("request_accepted", task_id=task_id,
                      session_id=session_id, project_root=project_root)
@@ -2914,13 +2994,16 @@ def brain_turn(
     # assume the whole window and starve the rest of the turn.
     candidates: list[dict] = []
     if include_bundle and _BUNDLE_MARKER not in user_prompt:
+        # Read the bundle from the SAME project root this turn resolved for
+        # the task file and context paths (issue #24): without the explicit
+        # root the bundle silently fell back to the bridge install dir.
         candidates.append({
             "kind": "bundle",
             "path": "small-file bundle",
             "slot": "bundle",
             "open_line": "",
             "fence_lang": None,
-            "text": _build_context_bundle(),
+            "text": _build_context_bundle(project_root),
         })
     if include_bundle and task_id:
         _ns = (
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 2d71dde..afd43d0 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -579,6 +579,113 @@ def test_bundle_truncates_large_file(tmp_path, monkeypatch):
     assert len(section) < len(big) + 5000
 
 
+# --- active-project-root resolution (issue #24) -----------------------
+# Regression guard: the bundle and the file-pull tools must read the
+# project the turn runs in, never the bridge install dir (the ambient
+# BRAIN_WORKSPACE_ROOT decoy below stands in for that install dir).
+
+def test_build_context_bundle_explicit_root_beats_env_decoy(
+        tmp_path, monkeypatch):
+    decoy = _mk_workspace(tmp_path, {
+        "agents/cognitive-executor.md": "DECOY_BUNDLE_CONTENT",
+    })
+    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(decoy))
+    project = tmp_path / "project"
+    (project / "agents").mkdir(parents=True)
+    (project / "agents" / "cognitive-executor.md").write_text(
+        "REAL_BUNDLE_CONTENT", encoding="utf-8")
+    (project / "docs").mkdir()
+    (project / "docs" / "conventions.md").write_text(
+        "real conventions", encoding="utf-8")
+
+    out = bridge._build_context_bundle(str(project))
+
+    assert "REAL_BUNDLE_CONTENT" in out
+    assert "real conventions" in out
+    assert "DECOY_BUNDLE_CONTENT" not in out
+    # genuinely absent files still get their markers; present ones do not
+    assert "[missing: docs/architecture.md]" in out
+    assert "[missing: DESIGN.md]" in out
+    assert "[missing: docs/conventions.md]" not in out
+
+
+def test_get_context_bundle_tool_honours_project_root(tmp_path, monkeypatch):
+    decoy = _mk_workspace(tmp_path, {
+        "agents/cognitive-executor.md": "DECOY_TOOL_CONTENT",
+    })
+    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(decoy))
+    project = tmp_path / "project"
+    (project / "agents").mkdir(parents=True)
+    (project / "agents" / "cognitive-executor.md").write_text(
+        "REAL_TOOL_CONTENT", encoding="utf-8")
+
+    out = _unwrap(bridge.get_context_bundle)(str(project))
+
+    assert "REAL_TOOL_CONTENT" in out
+    assert "DECOY_TOOL_CONTENT" not in out
+
+
+def test_workspace_root_follows_cwd_walkup(tmp_path, monkeypatch):
+    # With no env override the root must auto-resolve the ACTIVE project
+    # via the cwd ``tasks/`` walk-up instead of the install dir.
+    _clean_session_env(monkeypatch)
+    project = _mk_project(tmp_path, "walkup_project")
+    (project / "agents").mkdir()
+    (project / "agents" / "cognitive-executor.md").write_text(
+        "WALKUP_BUNDLE_CONTENT", encoding="utf-8")
+    nested = project / "a" / "b"
+    nested.mkdir(parents=True)
+    monkeypatch.chdir(nested)
+
+    assert bridge._workspace_root() == project.resolve()
+    assert "WALKUP_BUNDLE_CONTENT" in _unwrap(bridge.get_context_bundle)()
+
+
+def test_read_and_grep_honour_explicit_project_root(tmp_path, monkeypatch):
+    decoy = _mk_workspace(tmp_path, {"notes.md": "DECOY_NEEDLE\n"})
+    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(decoy))
+    project = tmp_path / "project"
+    project.mkdir()
+    (project / "notes.md").write_text(
+        "alpha\nREAL_NEEDLE beta\n", encoding="utf-8")
+
+    result = _unwrap(bridge.read_file)(
+        "notes.md", offset=2, limit=1, project_root=str(project))
+    assert result["lines"] == ["2: REAL_NEEDLE beta"]
+
+    hits = _unwrap(bridge.grep_files)(
+        "REAL_NEEDLE", project_root=str(project))
+    assert any("notes.md:2:" in h for h in hits)
+    assert not any("DECOY_NEEDLE" in h for h in hits)
+
+
+def test_brain_turn_bundle_follows_project_root(tmp_path, monkeypatch):
+    decoy = _mk_workspace(tmp_path, {
+        "agents/cognitive-executor.md": "DECOY_TURN_CONTENT",
+    })
+    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(decoy))
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    project = _mk_project(tmp_path, "turn_project")
+    (project / "agents").mkdir()
+    (project / "agents" / "cognitive-executor.md").write_text(
+        "REAL_TURN_CONTENT", encoding="utf-8")
+
+    holder = {}
+    _mk_bridge_client(
+        monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
+    target = _unwrap(bridge.brain_turn)
+    target("tiny question", project_root=str(project))
+
+    user_msgs = [t for t in holder["body"]["input"] if t.get("role") == "user"]
+    assert user_msgs
+    last = user_msgs[-1]["content"]
+    assert "REAL_TURN_CONTENT" in last
+    assert "DECOY_TURN_CONTENT" not in last
+
+
 def test_read_file_offset_limit(tmp_path, monkeypatch):
     ws = _mk_workspace(tmp_path, {"notes.md": "a\nb\nc\nd\ne\n"})
     monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
```
<!-- END_GIT_DIFF -->
