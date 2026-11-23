# Task 418: Agent-facing context MCP tool outputs

**File:** `tasks/qa/418-agent-facing-context-mcp-tool-outputs.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress
**Submitted:** 2026-11-23T08:54:51Z
**Started:** 2026-11-23T08:40:03Z

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Remove human/Manager-facing wording from Python MCP tool output strings so that tool output consumed by the agents and the cognitive executor is addressed to the agent, not to a person who copies and pastes files.

## Manager's Notes

- Manager request (voice-dictated, normalized): "Search and find all places we used keywords like `Manager: You can now open` in the tool output and input now used by agents and cognitive executor, so drop `Manager` from all of them — the tools, Python MCP. Make the system more comfortable for yourself. A task is required. Brain seats required. Skill loading and code search required. Auto mode lock."
- Correction note (prompt-refactor): `serach`→`search`, `cogntive exectotor`→`cognitive executor`, `comortable`→`comfortable`, `brain setas`→`brain seats`, `auto mode lock`→`autopilot locked`. Clarity 3/5; scope resolved by code search before planning.
- Autopilot locked for this task from the Manager's "auto mode lock" order. ZAC holds — no `git add`, `git commit`, `git checkout`, `git push`. Plan-approval and closure-approval gates still apply.
- Skills loaded: `prompt-refactor`, `code-search`, `project-memory`, `sop-maintenance`, `kanban-lifecycle`. `testing-verification` to be applied before the verification gate.
- Code-search finding: only two tool-output strings match the pattern, both in `mcp-context-server/server.py` (`build_context` and `create_tree_report` return blocks). A deployed copy exists at `~/.config/opencode/mcp-context-server/server.py` and is a separate deployment concern, not repo source.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Input validation, typo correction, and skill loading
- [x] Code search: locate every `Manager:` tool output/input string in the Python MCP servers
- [x] Create this task file
- [x] Seat-routed Brain plan, then Manager plan approval
- [x] Update the two tool-output strings in `mcp-context-server/server.py` to agent-facing wording
- [x] Add or update a regression test asserting no `Manager:` token in those tool outputs
- [x] Update sibling `README.md`/`DECISIONS.md` if the tool-output contract changes, and `CHANGELOG.md`
- [x] Run the verification gate and record evidence here
- [ ] QA transition via `custom_context_qa_transition` and chain QA/review via `brain_turn`

## Acceptance Criteria

- [x] A repo-wide grep of `mcp-*/**/*.py` for the literal `Manager:` returns no tool output/input strings (documentation and historical task files are out of scope)
- [x] `read_source_files` and `create_tree_report` return messages addressed to the calling agent, with no `Manager:` prefix and no "copy/paste it for the AI" instruction
- [x] A regression test fails on the old wording and passes on the new wording
- [x] `CHANGELOG.md` updated via Parse-Then-Append; sibling living-folder docs inspected
- [ ] Verification evidence recorded with an exact `rtk test`-prefixed command and exit code 0 (recorded command exits 1 due to 8 pre-existing/environmental failures; the two new tests exit 0 — see `## Verification Evidence`)

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec==0.12.1 --with pyyaml==6.0.2 python -m pytest tests/ -q`
- **Expected result:** all tests pass, exit code 0
- **Actual result:** Scoped red/green: `tests/test_agent_facing_tool_outputs.py` → 2 failed (exit 1) then 2 passed (exit 0). Full suite: `8 failed, 969 passed, 1 warning in 81.20s`. The 8 failures are pre-existing and unrelated to this change: 3 in `tests/test_mcp_servers.py` (system-prompt sync drift fixture stale — mutation target missing from `03-system_context.md`; `cognitive-executor.md` missing the QA/closure Rule bullet from a prior task) and 5 in `tests/test_planner_409_regression.py` (401 Unauthorized — auth token not present in this environment). None touches the files changed by this task. ruff format --check: exit 0 on both changed files. ruff check: exit 0 on the new test file; on `server.py` reports 115 pre-existing findings, none on the edited lines 766-767, 842-843, or 778. Typecheck and security stages: no config in `mcp-context-server/pyproject.toml` — skip records below.
- **Exit code:** 1 (full suite, pre-existing failures). The two new regression tests exit 0.

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0 (full suite exits 1 on 8 pre-existing/environmental failures; the two new tests and ruff format/check on the new test exit 0 — see `## Verification Evidence`)
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** The deployed singleton at `~/.config/opencode/mcp-context-server/server.py` keeps the old wording until a separate redeploy; agents would still see `Manager:` at runtime even after this repo change.
- **Rollback plan:** Revert the two string literals (and the regression test) in `mcp-context-server/server.py`; no data or schema change. Deployment copy is untouched by this task.

---

## Execution Log & Reasoning

_Planning phase. Autopilot locked per Manager order. Code search located exactly two matching tool-output strings in `mcp-context-server/server.py` (lines 766 and 841). Context-Map produced: graph `context-reports/graph_20261123_092849_e9b7c41d.json`, tree report `context-reports/tree_report_20261123_092850_08a392f2.md`, verified manifest `mcp-context-server/server.py#L760-767` and `#L838-842`. Sibling living-folder docs read before editing. No code changed yet._

- Plan: approved by Manager via question tool ("Approved"), option O1. `Brainstorm: not required — single-domain, fully reversible string contract change`. Seats [Software Architect] + [Senior Programmer]; Brain issued the implementation XML.
- Lane claim: `claim_next(task_id=418)` succeeded; moved to `tasks/in-progress/`, `**Started:** 2026-11-23T08:40:03Z` stamped by the transition. `**File:**` header synced to the in-progress path by hand because the transition did not rewrite it.
- Tooling fallback record: repo root `/home/mohammad/cognitive-lead-hq`; marker scan list — `mcp-context-server/pyproject.toml`, `mcp-context-server/server.py` (FastMCP app, no Flask/FastAPI/Pydantic); matched skills list — `python-fastapi` (closest, discipline only for gate order); reason phrase — "no MCP or FastMCP stack skill exists in the agent skills registry".
- Skill load record: `prompt-refactor`, `code-search`, `project-memory`, `sop-maintenance`, `kanban-lifecycle`, `testing-verification`, `python-fastapi` all loaded. Skips — `code-search` already executed in planning; no new task file to lint; no version bump or release in scope.
- Red proof: `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec==0.12.1 --with pyyaml==6.0.2 python -m pytest tests/test_agent_facing_tool_outputs.py -q` → `2 failed`, exit 1. Intended TDD red proof — old wording still present at `server.py:766` and `:841`. Syntax gate on the test file passed (exit 0).
- **Correction C1 (grounded):** the Brain plan named the codebase-context tool `build_context`, but the actual top-level function returning that text is `read_source_files` (`mcp-context-server/server.py#L690`). The first green attempt failed `test_context_tool_outputs_are_agent_addressed` with `build_context: definition not found`; the test mapping and the task AC were corrected to the real symbol. No tool behavior changed.
- Green proof: identical scoped command after the correction → `2 passed`, exit 0. Red-to-green pair closes Acceptance Criterion 3.
- Two return blocks rewritten with O1 wording: `read_source_files` at `server.py#L766-767` now `Context report written to … / Read it with your file tools to review the compiled codebase context.`; `create_tree_report` at `server.py#L842-843` now `Tree report written to … / Read it with your file tools to review the project tree.` Emoji prefixes, metrics line, `Generated Report` line, and `\\n\\n` separator untouched. Repo-wide grep for both retired sentinels in `mcp-*/**/*.py` prints nothing (exit 1 = PASS).
- Audit of other tools and parts (Manager request): grep of `mcp-*` source (excluding `.venv`) for `Manager:`, `copy/paste`, `local editor`, `for the AI`, `please copy`, `please upload`, `send it back to the AI Studio` returned no tool output strings beyond the two already fixed. Only other hit was a `create_tree_report` docstring ("Use when the Manager asks to..."), updated to "Use when the caller asks to...". No other human-facing tool strings found; scope stayed minimal.
- Tooling gate (fail-fast): (1) `uvx ruff format` write mode — exit 0, no changes. (2) `uvx ruff format --check` — exit 0 on both changed files. (3) `uvx ruff check` on `tests/test_agent_facing_tool_outputs.py` — exit 0. On `mcp-context-server/server.py` — 115 pre-existing findings (unused re-exported imports, blind exceptions, mutable defaults, etc.), none on the edited lines 766-767, 842-843, or 778; skip record: config path checked `mcp-context-server/pyproject.toml` (no `[tool.ruff]` section), reason "pre-existing findings not introduced by this change; ruff config absent; cleanup is a separate task". (4) Typecheck: `pyproject.toml` configures no typechecker (basedpyright/mypy/ty absent) — skip record: configuration path read, "no typechecker configured for this slice". (5) Security: no bandit/semgrep/pip-audit configured — skip record: configuration path checked, "no security scanner configured for this slice".
- Assumption log: A1 — ADR-015 placed newest-first before the existing ADR-014 entries (matching the file's 2026-11-02 top entry), not renumbering history. A2 — new test placed at repo-root `tests/` because that directory exists and `mcp-context-server/tests/` does not. A3 — the Brain plan's `build_context` name corrected to the real symbol `read_source_files` (`server.py#L690`); task AC and test mapping updated accordingly. A4 — 8 full-suite failures are pre-existing/environmental and unrelated to this change; the `exit code 0` AC/DoD boxes are left unchecked with this recorded reason.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index be8393b..f037a01 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Changed
 
+- `mcp-context-server`: `read_source_files` and `create_tree_report` now address the calling agent in their return text instead of a human Manager, and drop the copy/paste-for-the-AI instruction; both behaviours are pinned by a regression test.
 - **META 417 reopened: DeepSeek Flash cutoff fix + forced code/docs formatting:** corrected `prompts/fragments/03-system_context.md` to drop the stale Meta/Muse-Spark cutoff wording and name the DeepSeek Flash model line, with no hardcoded year (avoids cache-breaking mutable state, audit A3). Bumped `01-system_version.md` 9.92.0 → 9.93.0; regenerated `system-prompt.md` via the assembler. Configured OpenCode V2 `formatter` in project `opencode.json` (per the official V2 config/formatters docs): `scripts/format-guard.sh` dispatches prettier (docs/JSON/YAML), ruff (Python), shfmt (shell) on `write`/`edit`/`patch`, while skipping byte-sensitive artifacts — `prompts/fragments/*`, `prompts/shared/*`, `system-prompt.md`, `build/stage-prompts/*` and `tasks/*` — so Prettier cannot re-break the V25 pinned closing tags or the injected diff blocks. The previous `ruff-format` entry referenced a `ruff` binary absent from PATH (silently failing); ruff now runs via `uvx`. Updated `scripts/README.md`. Prompt-sync suite green, with the collected count recorded in the task file's Verification Evidence. No commit.
 
 - **Global install drifts synced and stale memories refreshed:** audited every global-install target against the repo using the project-memory workflow. Copied four drifted surfaces to `~/.config/opencode/`: `agents/cognitive-executor.md`, `system-prompt.md`, six `build/stage-prompts/system-prompt.*.md` stage artifacts, and the missing `mcp-lint-server/tests/test_deleted_skill_refs.py`. Re-audit clean; skills (24 dirs, no stray `.md`), the other agent, shell strategy, MCP sources, mcp-common and planner static were already in sync. Refreshed two stale memory records under task 411: the version record now reads OpenCode 2.3.2 / OpenChamber 2.7.3 verified 2026-11-22, and the blowsh policy record now reads EgressRegion DE with the verified DE exit. Both supersession notes preserved the prior bodies; `rebuild_memory_index` regenerated the index (33 rows). Prompt-sync suite 44 passed. No commit.
diff --git a/mcp-context-server/DECISIONS.md b/mcp-context-server/DECISIONS.md
index 945e8ed..0e51503 100644
--- a/mcp-context-server/DECISIONS.md
+++ b/mcp-context-server/DECISIONS.md
@@ -1,5 +1,12 @@
 # Architectural Decisions: mcp-context-server
 
+## [2026-11-23] ADR-015: Agent-addressed return text for the report tools
+
+- **Context:** `read_source_files` and `create_tree_report` ended their success text with "Manager: You can now open ... or copy/paste it directly for the AI". Both consumers are autonomous agents that read the generated report with their own file tools; there is no human in the loop and no clipboard step. The wording misdescribed the real contract and instructed the consumer to do something it cannot do.
+- **Decision:** Replace only the trailing paragraph with an agent-addressed pointer: `Context report written to <report>. Read it with your file tools to review the compiled codebase context.` and `Tree report written to <report>. Read it with your file tools to review the project tree.` Emoji prefixes, the metrics line, the report paths, the `\n\n` separator, and the tool signatures are unchanged. No shared helper is extracted: two call sites with different nouns do not satisfy the three-implementation rule, and a helper would exist only for the test's convenience.
+- **Consequences:** Tool output now matches its real consumer, and the two retired sentinels are pinned repo-wide by `tests/test_agent_facing_tool_outputs.py` alongside a per-function pointer assertion. The deployed singleton keeps the old wording until a separate redeploy, which is out of scope here.
+- **Rollback:** Restore the two trailing f-string lines in `server.py` and delete `tests/test_agent_facing_tool_outputs.py`; no data or schema change.
+
 ## [2026-11-02] ADR-014: Shared Regex Signature Fallback for Tree-sitter-less Envs
 
 - **Context:** The oversize `read_source_files` path called `_extract_via_tree_sitter` only, so minimal installs carrying just the pinned runtime deps (no tree-sitter grammar packages) produced "No signatures extracted" instead of structural evidence. The module docstring already promised "regex fallback", and an equivalent fallback lived inline in `server._signature_block` where the oversize path could not reach it (server imports fsutil, not vice versa).
diff --git a/mcp-context-server/README.md b/mcp-context-server/README.md
index 39f8021..3f861cc 100644
--- a/mcp-context-server/README.md
+++ b/mcp-context-server/README.md
@@ -31,3 +31,4 @@ Custom-context MCP daemon: directory trees, source reads, signature extraction,
 - Staging index-safety: `stage_and_inject_diff` stages whole-file blobs; `skip_add=True` skips `git add` and only extracts + injects for self-managed hunk-level index surgery; default path warns naming files with pre-existing staged hunks.
 - Parallel isolation: `unstage_files` removes listed files from the index without touching the worktree — the agent-managed unstage path for shared-file parallel sessions (no commit, no checkout, no push; ZAC holds).
 - Task timing: `sync_task_times` stamps a missing `Started` (in `in-progress`) or `Submitted` (in `qa`) for tasks already sitting in a lane, which is what a hand-moved task needs. It refuses the `completed` lane on purpose — stamping `Finished` at call time on an old closed task would fabricate a duration. The start comes from git history then the file mtime, never from an invented "now"; when neither can answer the file is reported as skipped.
+- Tool-output contract: `read_source_files` and `create_tree_report` address the calling agent, never a human Manager. Their return text points at the generated report and carries no copy/paste-for-the-AI instruction; both properties are pinned by `tests/test_agent_facing_tool_outputs.py`.
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index d56700c..74a067f 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -763,7 +763,8 @@ def read_source_files(
         f"{skipped} skipped, {total_bytes} bytes read in {duration_s:.2f}s "
         f"(tree depth cap {TREE_MAX_DEPTH}, collect cap {COLLECT_MAX_FILES}).\n"
         f"📁 Generated Report: `{report_file}`\n\n"
-        f"Manager: You can now open `{report_file}` in your local editor to view the codebase context or copy/paste it directly for the AI."
+        f"Context report written to `{report_file}`. "
+        f"Read it with your file tools to review the compiled codebase context."
     )
 
 
@@ -774,7 +775,7 @@ def create_tree_report(
     max_depth: int = 3,
     max_entries: int = TREE_MAX_ENTRIES,
 ) -> str:
-    """Creates a .gitignore-aware directory tree of a path or the entire project and saves it as a Markdown file under context-reports/ (named tree_report_<timestamp>_<uuid>.md). Use when the Manager asks to 'create a tree of the project' or 'create a tree of <path>'. Security: target_path is resolved against the workspace root and rejected if it escapes the project (path traversal prevention). project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
+    """Creates a .gitignore-aware directory tree of a path or the entire project and saves it as a Markdown file under context-reports/ (named tree_report_<timestamp>_<uuid>.md). Use when the caller asks to 'create a tree of the project' or 'create a tree of <path>'. Security: target_path is resolved against the workspace root and rejected if it escapes the project (path traversal prevention). project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
     # Security: Coerce None or invalid types back to the whole-project default
     # so a malformed tool invocation degrades gracefully instead of crashing.
     if not isinstance(target_path, str):
@@ -838,7 +839,8 @@ def create_tree_report(
     return (
         f"✅ Success: Directory tree saved for `{tree_path}`.\n"
         f"📁 Generated Report: `{report_file}`\n\n"
-        f"Manager: You can now open `{report_file}` in your local editor to view the project tree or copy/paste it directly for the AI."
+        f"Tree report written to `{report_file}`. "
+        f"Read it with your file tools to review the project tree."
     )
 
 
diff --git a/tests/test_agent_facing_tool_outputs.py b/tests/test_agent_facing_tool_outputs.py
new file mode 100644
index 0000000..b156323
--- /dev/null
+++ b/tests/test_agent_facing_tool_outputs.py
@@ -0,0 +1,90 @@
+"""Regression test: MCP tool output addresses the calling agent, not a human.
+
+Sibling Docs: mcp-context-server/README.md | Decisions: mcp-context-server/DECISIONS.md
+
+Contract under test: the success text returned by `read_source_files` and
+`create_tree_report` is consumed by autonomous agents that read files with their
+own tools. The text therefore points the agent at the generated report and never
+carries the retired human-facing prefix or the copy/paste-for-the-AI instruction.
+
+Design notes:
+- Source-level assertions only. Importing `server.py` would pull the FastMCP
+  runtime and its dependency set, which the test environment does not install.
+- The repository root is discovered by walking up from this file, so the test
+  works from any working directory.
+- This file lives outside `mcp-*`, so its own sentinel literals are not scanned
+  by the repo-wide check below.
+"""
+
+import ast
+from pathlib import Path
+
+# Retired human-facing wording that must vanish from every MCP server source.
+BANNED_SENTINELS = (
+    "Manager: You can now open",
+    "copy/paste it directly for the AI",
+)
+
+# Agent-addressed pointer sentence expected inside each report tool function.
+EXPECTED_POINTERS = {
+    "read_source_files": "Context report written to",
+    "create_tree_report": "Tree report written to",
+}
+
+# Directory name that identifies the repository root.
+ROOT_MARKER = "mcp-context-server"
+
+
+def _repo_root():
+    """Return the repository root by walking up until the marker directory exists."""
+    for parent in Path(__file__).resolve().parents:
+        if (parent / ROOT_MARKER).is_dir():
+            return parent
+    raise AssertionError("repository root not found")
+
+
+def _mcp_sources(root):
+    """Yield every Python file that belongs to an MCP server directory."""
+    for server_dir in sorted(root.glob("mcp-*")):
+        if not server_dir.is_dir():
+            continue
+        yield from sorted(server_dir.rglob("*.py"))
+
+
+def _function_source(source, function_name):
+    """Return the exact source segment of a top-level function, or fail loudly."""
+    tree = ast.parse(source)
+    for node in tree.body:
+        if isinstance(node, ast.FunctionDef) and node.name == function_name:
+            segment = ast.get_source_segment(source, node)
+            if segment is None:
+                raise AssertionError(function_name + ": source segment unavailable")
+            return segment
+    raise AssertionError(function_name + ": definition not found")
+
+
+def test_no_human_addressed_sentinels_in_mcp_sources():
+    """No MCP server source may keep the retired human-facing wording."""
+    root = _repo_root()
+    offenders = []
+    for path in _mcp_sources(root):
+        text = path.read_text(encoding="utf-8")
+        for sentinel in BANNED_SENTINELS:
+            if sentinel in text:
+                offenders.append(str(path.relative_to(root)) + " -> " + sentinel)
+    if offenders:
+        details = "; ".join(offenders)
+        raise AssertionError("retired sentinel survived in: " + details)
+
+
+def test_context_tool_outputs_are_agent_addressed():
+    """Both report tools point the agent at the report and keep no human wording."""
+    root = _repo_root()
+    source = (root / ROOT_MARKER / "server.py").read_text(encoding="utf-8")
+    for function_name, pointer in EXPECTED_POINTERS.items():
+        segment = _function_source(source, function_name)
+        for sentinel in BANNED_SENTINELS:
+            if sentinel in segment:
+                raise AssertionError(function_name + " still returns " + sentinel)
+        if pointer not in segment:
+            raise AssertionError(function_name + " is missing " + pointer)
```
<!-- END_GIT_DIFF -->
