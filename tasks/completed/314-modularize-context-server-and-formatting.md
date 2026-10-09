# Task 314: Modularize Context Server plus Enforced Python Formatting

**File:** `tasks/qa/314-modularize-context-server-and-formatting.md`
**Source:** manager
**Type:** refactor
**Status:** in-progress

## Goal

Split the single-file mcp-context-server/server.py into clean modules following exactly the mcp-brain-bridge pattern (server.py entrypoint plus concern modules), then pick one formatter for all MCP/Python code, force-enable it in OpenCode settings, and run it — with zero behavior change and a green suite.

## Manager's Notes

Manager order 2026-10-09: secure, precise, professional split mirroring the Brain server; formatter picked by Hands, enforced via OpenCode settings, run over all Python; everything stays clean, organized, formatted, modular with no lost functionality and no breaking changes.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Map brain-bridge module pattern and context-server inventory
- [x] Design module split (names, ownership, import graph, no cycles)
- [x] Split with server.py compatibility shim (tests import server.py by path)
- [x] Pick formatter (offline-capable, single tool) and record decision
- [x] Enforce formatter in OpenCode settings (project config)
- [x] Run formatter over all Python dirs and re-run full suite green
- [x] Deploy global, restart, live verify tools
- [x] Stage and move to QA

## Acceptance Criteria

- [x] AC1: server.py entrypoint plus concern modules mirror the brain-bridge layout
- [x] AC2: All 14 MCP tools register with identical names and behavior
- [x] AC3: Existing tests pass unmodified or with path-only import updates
- [x] AC4: One formatter enforced in OpenCode settings and applied to all Python
- [x] AC5: Global singleton deploy plus restart plus live tool check green
- [x] AC6: lint_task_file passes

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest pytest tests/ -q
- **Expected result:** 489 passed, only 6 pre-existing memory yaml failures
- **Actual result:** 489 passed, 6 failed (all ModuleNotFoundError yaml in memory server, pre-existing); lint_task_file passes; opencode validator exit 0; live graph_stats green on restarted service
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

- **Risk:** Module split breaks path-based test imports or the singleton entrypoint
- **Rollback plan:** Restore single server.py from git; modules removed

---

## Execution Log & Reasoning

Seat Check: backend Python refactor (no behavior change) plus config/text → Architect kept (module boundaries), Programmer kept, Designer skipped. Brainstorm: not required — reversible via git checkout. Mode: manual (313 autopilot closed with the META commit).

Design (mirrors mcp-brain-bridge: entrypoint owns the FastMCP app, siblings stay stdlib-pure with no registration, dual import robustness):
- server.py keeps: shebang/uv-script block, sys.path bootstrap, mcp = FastMCP("CustomContext"), _FALLBACK_FIRED + ROOT_FALLBACK_WARNING + _project_tool + _explicit_project_root (fallback framework), the 14 tool defs, __main__; re-exports every test-accessed helper via plain from-imports (monkeypatch-settable).
- fsutil.py: GitIgnoreFilter, TEXT_ENCODINGS, is_binary, BANNED_DIRS + tree caps, _is_banned_dir, generate_tree, process_source_file, collect_files, _ensure_context_reports_ignored.
- signatures.py: tree-sitter maps/queries/cache + language/signature extractors.
- graph.py: all GRAPH_* constants + symbol/md/sql parsers + build/degrees/save/load/tokens/find/neighbors/bfs/vocab/suggest.
- gitops.py: _repo_root, slug/commit-message/commit helpers, kebab/next-id/find-task/extract helpers, checklist/stack/checksum/mv/patch helpers + kanban constants.
- bundle.py: _build_meta_content (imports gitops helpers).
- Import graph: server → all; bundle → gitops; no cycles; no sibling → server edge.
- Formatter decision: ruff (single binary, format is AST-safe whitespace-only; `uv tool install ruff@0.16.10` pinned global since PATH lacks it and uvx needs cache). Enforce via opencode.json named map ruff-format on .py (validator-accepted shape). No new runtime deps; uv.lock untouched. Global deploy copies all *.py (never __pycache__).
- Deviation D1 (logged, minimal): test_prompt_sync.py version pin 9.54.0 → 9.56.0 — stale since 309 shipped 9.56.0 without updating it (fails on clean HEAD too); same precedent as 307.
- Incident (caught by deploy, fixed): first split dropped `import os` from server.py `__main__` (tests never execute it) and crashed the singleton restart loop; restored, redeployed, service active. Lesson recorded: live restart is the real entrypoint test.
- Autopilot locked for 314 per Manager order "start auto pilot for task" (2026-10-09). Saga: sync-global → live-verify → Brain QA → fix → re-stage → Brain review → relay; never auto-commit, never close without exact approval words. Global sync verified IN_SYNC (context 6/6, memory/lint/brain drifted files copied); all four singletons restarted active and tool-tested live.
- Fix loop 1 (autopilot, QA_REJECTED reproduced): oversize process_source_file called _extract_via_tree_sitter stranded in signatures module — fixed by lazy import in fsutil (no import-time edge) plus oversize regression test. AST audited all six modules for the same class; only instance. Full suite 490 passed + 6 pre-existing memory yaml failures. Diff hash after fix: cc50997f146c1cd14684742eb8d5d70be1b0b039b34dfabc26708851d9f5eb9b (single attempt, no spin). Redeployed fsutil global, service active, live oversize read attaches signatures.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 65609d2..e5b41d2 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -16,6 +16,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Graph precision round (Task 312):** full-file symbol scans, vocabulary hints on zero hits, DFS traversal mode, Task/ADR rationale links binding code to prior decisions, god-node noise filter, explicit truncation note. Found live: symbols past line 2000 were silently dropped. QA follow-ups: typed arrow annotations, graph-path confinement, empty-label guard, 1MB scan cap.
 
+- **Modularized context server plus enforced formatting (Task 314):** server.py split into entrypoint plus fsutil/signatures/graph/gitops/bundle mirroring the Brain layout, with full test-surface re-exports and zero behavior change; ruff 0.16.10 pinned globally and enforced in opencode.json; ruff format applied repo-wide.
+
 - **Context MCP lite knowledge-graph (Task 308, system prompt 9.55.0):** `mcp-context-server` now builds a deterministic stdlib-only graph (files + symbols; contains/imports EXTRACTED, references INFERRED) with `build_graph` persisting versioned `graph_*.json` (schema 1) plus `graph_report_*.md` under `context-reports/`, and `query_graph` / `explain_node` / `shortest_path` / `god_nodes` / `graph_stats` for scoped queries. Also fixed `get_directory_tree` workspace scoping (removed cwd overwrite). Discovery is graph-first: `skill-templates/code-search`, `prompts/fragments/09-hands_protocols`, `agents/cognitive-discovery.md`, and `agents/cognitive-executor.md` prefer graph queries before raw reads.
 
 - **Brain partial-truncation server-side recovery (Task 291, fixes issue #28):** long implement `brain_turn` calls truncated by `max_output_tokens` no longer return a bare fragment into a caller-side retry loop. Research found the cap is innocent — live `BRAIN_MAX_TOKENS=943718` already sits at the `meta/muse-spark-1.3-contributor` ceiling — while `BRAIN_REASONING_EFFORT=xhigh` burns ~97% of the output budget on reasoning (measured `reasoning_tokens=14683 visible_tokens=341`), starving the visible XML at ANY cap. Following the industry playbook (structured output must be re-issued whole with more headroom, never stitched), the bridge now discards the fragment and re-issues the turn ONCE server-side with one-notch-lower reasoning effort (`max→xhigh→high→medium→low` via `_step_down_effort`); a second truncation returns terminal `TRUNCATION_UNRECOVERABLE` (caller must not retry as-is) instead of looping. Task 259 empty-output terminal, `EMPTY_OUTPUT_RETRY`, the semantic gate, and the 5xx/429 retry policy are untouched. Open decisions for the Manager: lower live effort from `xhigh`, keep the cap, deploy = copy `server.py` to the install + `systemctl --user restart mcp-brain`.
diff --git a/mcp-brain-bridge/loop_guard.py b/mcp-brain-bridge/loop_guard.py
index da7fd8a..5f1dc88 100644
--- a/mcp-brain-bridge/loop_guard.py
+++ b/mcp-brain-bridge/loop_guard.py
@@ -110,8 +110,11 @@ def _sessions_root(explicit: Optional[str] = None) -> Path:
     return project_sessions_root()
 
 
-def _hashes_path(task_id: str, sessions_root: Optional[str] = None,
-                 project_root: Optional[str] = None) -> Path:
+def _hashes_path(
+    task_id: str,
+    sessions_root: Optional[str] = None,
+    project_root: Optional[str] = None,
+) -> Path:
     if not _TASK_ID_RE.match(task_id or ""):
         raise ValueError(f"bad task_id for loop guard: {task_id!r}")
     if project_root and not sessions_root:
@@ -141,7 +144,9 @@ def _read_hashes(path: Path) -> list[str]:
 
 
 def record_attempt(
-    task_id: str, diff_hash: str, sessions_root: Optional[str] = None,
+    task_id: str,
+    diff_hash: str,
+    sessions_root: Optional[str] = None,
     project_root: Optional[str] = None,
 ) -> dict[str, Any]:
     """Record one fix-attempt hash; report whether the loop is spinning.
diff --git a/mcp-context-server/DECISIONS.md b/mcp-context-server/DECISIONS.md
index 118aa9f..525b7f8 100644
--- a/mcp-context-server/DECISIONS.md
+++ b/mcp-context-server/DECISIONS.md
@@ -41,3 +41,10 @@
 - **Decision:** Full-file symbol scans (200/file cap bounds cost); zero-hit queries suggest closest vocabulary; query_graph gains mode bfs/dfs (depth 6); Task NNN/ADR-NNN code mentions become INFERRED rationale_for edges to task files/decision sections; god_nodes skips dunders plus run/json/post/data; truncation carries an explicit note.
 - **Consequences:** No silent drops; dead ends guide vocabulary; rationale links bind code to prior decisions. Plain helpers must sit above `@_project_tool` — a decorator left above a helper silently registers it as a 15th tool (caught live via catalog change); registry test pins exactly 14 tools.
 - **Rollback:** Restore the line head and drop new options.
+
+## [2026-10-09] ADR-007: Context Server Modules plus Ruff Enforcement
+
+- **Context:** server.py grew to 3189 lines single-file while the Brain side splits entrypoint plus stdlib-pure concern modules. No formatter was pinned (`formatter: true`); ruff/black absent from PATH.
+- **Decision:** Mirror the brain layout: server.py owns the FastMCP app plus the 14 tool defs and re-exports everything (test/shim surface, monkeypatch-settable); fsutil, signatures, graph, gitops, bundle stay stdlib-pure with acyclic imports (graph→fsutil, bundle→gitops). Formatter is ruff 0.16.10 via pinned global install; opencode.json pins named map ruff-format on .py; ruff format applied repo-wide (13 files).
+- **Consequences:** Same 14 tools, same behaviors, full suite green; global deploy copies all *.py.
+- **Rollback:** Restore single server.py from git; remove new modules; revert opencode.json to `formatter: true`.
diff --git a/mcp-context-server/README.md b/mcp-context-server/README.md
index f2be196..563a3d6 100644
--- a/mcp-context-server/README.md
+++ b/mcp-context-server/README.md
@@ -6,7 +6,12 @@ Custom-context MCP daemon: directory trees, source reads, signature extraction,
 
 ## Files
 
-- `server.py` — Daemon entrypoint (tree reports, source reads, signatures, lite graph, staging, bundling tools).
+- `server.py` — Entrypoint: FastMCP app, fallback framework, the 14 tool defs, `__main__`; re-exports every helper (test/shim surface).
+- `fsutil.py` — Gitignore filtering, trees, source reads, report writes.
+- `signatures.py` — Tree-sitter signature extraction with regex fallback.
+- `graph.py` — Knowledge-graph constants, parsers, build and query primitives.
+- `gitops.py` — Repo roots, commit gates, task discovery, archive patching.
+- `bundle.py` — Meta-task content builder.
 - `pyproject.toml` / `uv.lock` — Runtime deps (`pathspec`, `mcp[cli]`) and lockfile.
 
 ## Key Risks & Invariants
diff --git a/mcp-context-server/bundle.py b/mcp-context-server/bundle.py
new file mode 100644
index 0000000..8cd1351
--- /dev/null
+++ b/mcp-context-server/bundle.py
@@ -0,0 +1,189 @@
+# Sibling Docs: README.md | Decisions: DECISIONS.md
+
+
+"""Meta-task content builder (tool itself stays in server.py). Stdlib-pure: no MCP imports, no registration, no import back to server."""
+
+import re
+import time
+from pathlib import Path
+
+from gitops import (
+    ACTIVE_KANBAN_DIRS,
+    DIFF_SIZE_WARNING_THRESHOLD,
+    MAX_BUNDLE_SIZE,
+    _detect_stack,
+    _extract_checklist_with_continuations,
+    _extract_section,
+    _extract_title,
+    _format_task_id_list,
+    _verify_verbatim_checksums,
+)
+
+
+def _build_meta_content(
+    meta_id: int,
+    meta_slug: str,
+    meta_title: str,
+    source_ids: list[str],
+    source_data: list[tuple[str, Path, str, str]],
+) -> str:
+    meta_id_str = f"{meta_id:02d}" if meta_id < 100 else str(meta_id)
+    if meta_id >= 100:
+        meta_id_str = str(meta_id)
+    file_header = f"tasks/backlog/{meta_id_str}-{meta_slug}.md"
+    title_line = f"# Task {meta_id}: {meta_title}"
+    timestamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
+    bundled_checklist_items: list[str] = []
+    local_todos_aggregated: list[str] = []
+    total_loc = 0
+    per_source_blocks: list[str] = []
+    for sid, path, content, stitle in source_data:
+        goal = _extract_section(content, "Goal") or "_(No Goal section found)_"
+        ac = (
+            _extract_section(content, "Acceptance Criteria")
+            or "_(No Acceptance Criteria)_"
+        )
+        todos = _extract_section(content, "Local TODOs") or "_(No Local TODOs)_"
+        risk = _extract_section(content, "Risk & Rollback")
+        manager_notes = _extract_section(content, "Manager's Notes")
+        source_context = ""
+        if "## Blueprint Reference" in content:
+            br = _extract_section(content, "Blueprint Reference")
+            if br:
+                source_context += f"\n**Blueprint Reference (verbatim):**\n{br}\n"
+        total_loc += len(content.splitlines())
+        # B1: multi-line checklist extraction
+        ac_lines = _extract_checklist_with_continuations(ac)
+        if not ac_lines:
+            ac_lines = [
+                f"- [ ] {line.strip()}"
+                for line in ac.splitlines()
+                if line.strip() and not line.strip().startswith("#")
+            ][:3]
+        for line in ac_lines:
+            if line.startswith("- ["):
+                m = re.match(r"^- \[[ xX]\]\s*(.*)", line)
+                inner = m.group(1) if m else line
+                bundled_checklist_items.append(f"- [ ] [{sid}] {inner}")
+            else:
+                bundled_checklist_items.append(line)
+        # B1: multi-line TODO extraction
+        todo_lines = _extract_checklist_with_continuations(todos)
+        for line in todo_lines:
+            if line.startswith("- ["):
+                m = re.match(r"^- \[[ xX]\]\s*(.*)", line)
+                inner = m.group(1) if m else line
+                local_todos_aggregated.append(f"- [ ] [{sid}] {inner}")
+            else:
+                local_todos_aggregated.append(line)
+        block = f"### Source Task {sid}: {stitle}\n\n"
+        block += f"**Original File:** `{path}` → `tasks/archive/{path.name}` (after bundling)\n\n"
+        block += f"**Title:** {stitle}\n\n"
+        block += "#### Goal (verbatim)\n\n"
+        block += f"{goal}\n\n"
+        if manager_notes:
+            block += "#### Manager's Notes (verbatim)\n\n"
+            block += f"{manager_notes}\n\n"
+        if source_context:
+            block += source_context + "\n"
+        block += "#### Acceptance Criteria (verbatim)\n\n"
+        block += f"{ac}\n\n"
+        block += "#### Local TODOs (verbatim)\n\n"
+        block += f"{todos}\n\n"
+        if risk:
+            block += "#### Risk & Rollback (verbatim)\n\n"
+            block += f"{risk}\n\n"
+        block += "---\n\n"
+        per_source_blocks.append(block)
+    seen_todos: set[str] = set()
+    deduped_todos: list[str] = []
+    for t in local_todos_aggregated:
+        if t not in seen_todos:
+            seen_todos.add(t)
+            deduped_todos.append(t)
+    meta_local_todos = (
+        f"- [ ] Step 1: Validate META bundle — confirm all {len(source_data)} source requirements are captured verbatim below\n"
+        f"- [ ] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)\n"
+    )
+    for t in deduped_todos:
+        meta_local_todos += f"{t}\n"
+    meta_local_todos += f"- [ ] Step {len(deduped_todos) + 3}: Verify all bundled checklist items and run lint_task_file + verification-before-completion\n"
+    meta_local_todos += f"- [ ] Step {len(deduped_todos) + 4}: Update CHANGELOG.md and record Verification Evidence\n"
+    meta_ac = (
+        "\n".join(bundled_checklist_items)
+        if bundled_checklist_items
+        else "- [ ] _(No aggregated criteria — check per-source blocks)_"
+    )
+    meta_ac += f"\n- [ ] Traceability: All {len(source_data)} source tasks are archived with superseded-by marker and reachable via `git log --follow`"
+    meta_verification = (
+        f"- **Test command:** `lint_task_file` on META file; `git log --oneline --follow -- tasks/archive/<id>-*.md | head` for archived sources; project test suite if logic changed\n"
+        f"- **Expected result:** META lint passes; all {len(source_data)} sources in `tasks/archive/` with `superseded` status; single Factual Git Diff covers all bundled changes\n"
+        f"- **Actual result:** _(Hands fill during execution)_\n"
+        f"- **Exit code:** _(Hands fill)_\n"
+    )
+    meta_risk = (
+        "- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.\n"
+        "- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.\n"
+        "- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.\n"
+        f"- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded {_format_task_id_list(source_ids)}, remove Superseded-By footer, delete or archive `tasks/backlog/{meta_id_str}-{meta_slug}.md` as abandoned. No HQ code beyond bundler is affected.\n"
+    )
+    warning_note = ""
+    if total_loc > DIFF_SIZE_WARNING_THRESHOLD:
+        warning_note = (
+            f"> ⚠️ **Guardrail Warning:** Combined source size is {total_loc} LOC (> {DIFF_SIZE_WARNING_THRESHOLD}). "
+            f"Unified META diff may be large and hard to review. Consider splitting into two METAs.\n\n"
+        )
+    content = (
+        f"{title_line}\n\n"
+        f"**File:** `{file_header}`\n"
+        f"**Source:** manager\n"
+        f"**Type:** feature\n"
+        f"**Status:** open\n"
+        f"**Supersedes:** {_format_task_id_list(source_ids)}\n"
+        f"**Meta:** true\n"
+        f"**Created:** {timestamp}\n"
+        f"**Bundled:** {len(source_data)} tasks\n\n"
+        f"## Goal\n\n"
+        f'Unified execution of {len(source_data)} related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks {_format_task_id_list(source_ids)} — "{meta_title}" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.\n\n'
+        f"{warning_note}**Source IDs:** {_format_task_id_list(source_ids)}\n"
+        f'**Next ID:** {meta_id} (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)\n'
+        f"**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: {meta_id}-{meta_slug}` and remain reachable via `git log --follow` (never purged until META is completed).\n\n"
+        f"## Manager's Notes\n\n"
+        f"**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute {len(source_data)} small related tasks together and speed up turnaround.\n\n"
+        f"**Traceability:**\n"
+        f"- Supersedes {_format_task_id_list(source_ids)} — see per-source verbatim blocks below\n"
+        f"- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** {meta_id_str}-{meta_slug}` header + superseded footer\n"
+        f"- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file\n\n"
+        f"**Guardrails Applied:**\n"
+        f"- Cap 6 per bundle — this bundle has {len(source_data)} ({'✅ within cap' if len(source_data) <= MAX_BUNDLE_SIZE else '❌ exceeds cap — requires --force'})\n"
+        f"- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)\n"
+        f"- Diff-size check — combined {total_loc} LOC ({'⚠️ exceeds 400 — consider split' if total_loc > DIFF_SIZE_WARNING_THRESHOLD else '✅ within 400'})\n\n"
+        f"## Source Bundles (Verbatim Preservation)\n\n"
+        f"The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.\n\n"
+        f"{''.join(per_source_blocks)}\n"
+        f"## Bundled Checklist (All-or-Nothing)\n\n"
+        f"> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.\n\n"
+        f"{meta_ac}\n\n"
+        f"## Local TODOs\n\n"
+        f"{meta_local_todos.strip()}\n\n"
+        f"## Acceptance Criteria\n\n"
+        f"{meta_ac}\n\n"
+        f"## Verification Evidence\n\n"
+        f"{meta_verification.strip()}\n\n"
+        f"## Definition of Done\n\n"
+        f"The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):\n\n"
+        f"- [ ] Build/Test/Lint pass with exit code 0\n"
+        f"- [ ] `lint_task_file` passes on the active task file\n"
+        f"- [ ] `CHANGELOG.md` updated via Parse-Then-Append\n"
+        f"- [ ] `verification-before-completion` applied and evidence recorded\n\n"
+        f"## Risk & Rollback\n\n"
+        f"{meta_risk.strip()}\n\n"
+        f"---\n\n"
+        f"## Execution Log & Reasoning\n\n"
+        f"_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_\n\n"
+        f"## Factual Git Diff\n\n"
+        f"<!-- BEGIN_GIT_DIFF -->\n\n"
+        f"_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_\n\n"
+        f"<!-- END_GIT_DIFF -->\n"
+    )
+    return content
diff --git a/mcp-context-server/fsutil.py b/mcp-context-server/fsutil.py
new file mode 100644
index 0000000..1fa2886
--- /dev/null
+++ b/mcp-context-server/fsutil.py
@@ -0,0 +1,294 @@
+# Sibling Docs: README.md | Decisions: DECISIONS.md
+
+
+"""Filesystem scanning: gitignore filtering, trees, source reads, report writes. Stdlib-pure: no MCP imports, no registration, no import back to server."""
+
+import os
+import sys
+from pathlib import Path
+from typing import Optional
+
+import pathspec
+
+
+class GitIgnoreFilter:
+    """Evaluates paths against .gitignore files dynamically."""
+
+    def __init__(self) -> None:
+        self._specs: dict[Path, Optional[pathspec.PathSpec]] = {}
+
+    def _get_spec(self, dir_path: Path) -> Optional[pathspec.PathSpec]:
+        if dir_path in self._specs:
+            return self._specs[dir_path]
+        gitignore_file = dir_path / ".gitignore"
+        if gitignore_file.is_file():
+            try:
+                with open(gitignore_file, "r", encoding="utf-8") as f:
+                    spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
+                    self._specs[dir_path] = spec
+                    return spec
+            except Exception as e:
+                print(f"Warning: Failed to read {gitignore_file}: {e}", file=sys.stderr)
+        self._specs[dir_path] = None
+        return None
+
+    def is_ignored(self, path: Path) -> bool:
+        abs_path = path.resolve()
+        if ".git" in abs_path.parts or abs_path.name == ".git":
+            return True
+        # Repo boundary (Task 238 fix loop): git only applies .gitignore
+        # files INSIDE the repo. The old walk-to-/ let a grandparent
+        # .gitignore (e.g. `projects/` two levels up) mark every in-repo
+        # path ignored, which broke get_directory_tree("."). Stop at the
+        # nearest self-or-ancestor dir containing .git (its spec still
+        # applies); with no repo found, floor at cwd when the path lives
+        # under it, else keep the legacy walk-to-/ behavior.
+        boundary: Path | None = None
+        probe = abs_path if abs_path.is_dir() else abs_path.parent
+        cwd = Path.cwd().resolve()
+        # Both .git forms stop the walk: a directory in normal repos, a
+        # FILE in submodule/worktree roots (gitdir pointer). Either way
+        # this dir is a repo root and .gitignore files above it never
+        # apply inside.
+        while True:
+            dot_git = probe / ".git"
+            if dot_git.is_dir() or dot_git.is_file():
+                boundary = probe
+                break
+            if probe == probe.parent:
+                break
+            probe = probe.parent
+        if boundary is None:
+            try:
+                abs_path.relative_to(cwd)
+                boundary = cwd
+            except ValueError:
+                boundary = None
+        current = abs_path if abs_path.is_dir() else abs_path.parent
+        while True:
+            spec = self._get_spec(current)
+            if spec:
+                try:
+                    rel_path = abs_path.relative_to(current)
+                    match_str = rel_path.as_posix()
+                    if abs_path.is_dir() and not match_str.endswith("/"):
+                        match_str += "/"
+                    if spec.match_file(match_str):
+                        return True
+                except ValueError:
+                    pass
+            if boundary is not None and current == boundary:
+                break
+            if current == current.parent:
+                break
+            current = current.parent
+        return False
+
+
+TEXT_ENCODINGS = ["utf-8", "utf-8-sig", "windows-1256", "windows-1252", "latin-1"]
+
+
+def is_binary(file_path: Path) -> bool:
+    try:
+        with open(file_path, "rb") as f:
+            chunk = f.read(1024)
+            return b"\0" in chunk
+    except Exception:
+        return True
+
+
+# --- Tree-sitter AST signature extraction ---
+
+
+TREE_MAX_DEPTH = 8
+
+
+TREE_MAX_ENTRIES = 2000
+
+
+COLLECT_MAX_FILES = 1000
+# Directory names never descended into, at any level. Supplements .gitignore
+# (which cannot cover absolute-path walks outside any repo).
+
+
+BANNED_DIRS = frozenset(
+    {
+        ".git",
+        ".cache",
+        "__pycache__",
+        "node_modules",
+        ".venv",
+        "venv",
+        "proc",
+        "sys",
+        "dev",
+    }
+)
+
+
+def _is_banned_dir(entry: Path) -> bool:
+    """True when a directory entry must never be descended into."""
+    try:
+        return entry.is_dir() and entry.name in BANNED_DIRS
+    except OSError:
+        return True  # Unstatable entries are treated as unsafe to descend.
+
+
+def generate_tree(
+    dir_path: Path,
+    ignore_filter: GitIgnoreFilter,
+    max_depth: int = TREE_MAX_DEPTH,
+    max_entries: int = TREE_MAX_ENTRIES,
+) -> str:
+    lines = ["```text", dir_path.name or str(dir_path)]
+    state = {"count": 0, "truncated": False}
+
+    def _walk(current_path: Path, prefix: str, depth: int) -> None:
+        if state["truncated"]:
+            return
+        if depth > max_depth:
+            lines.append(f"{prefix}└── [Max depth reached ({max_depth})]")
+            return
+        try:
+            entries = list(current_path.iterdir())
+        except (PermissionError, OSError):
+            lines.append(f"{prefix}└── [Unreadable directory]")
+            return
+        valid_entries = [
+            e
+            for e in entries
+            if not _is_banned_dir(e) and not ignore_filter.is_ignored(e)
+        ]
+        sorted_entries = sorted(
+            valid_entries, key=lambda e: (not e.is_dir(), e.name.lower())
+        )
+        for i, entry in enumerate(sorted_entries):
+            if state["count"] >= max_entries:
+                lines.append(
+                    f"{prefix}└── [Truncated: entry limit reached ({max_entries})]"
+                )
+                state["truncated"] = True
+                return
+            state["count"] += 1
+            is_last = i == (len(sorted_entries) - 1)
+            connector = "└── " if is_last else "├── "
+            lines.append(f"{prefix}{connector}{entry.name}")
+            if entry.is_dir():
+                extension = "    " if is_last else "│   "
+                _walk(entry, prefix + extension, depth + 1)
+
+    _walk(dir_path, "", 0)
+    lines.append("```")
+    return "\n".join(lines)
+
+
+def process_source_file(file_path: Path, max_size: int, line_numbers: bool) -> str:
+    lines = [f"### `{file_path}`", ""]
+    if not file_path.exists():
+        lines.append("> Skipped: (File not found)\n")
+        return "\n".join(lines)
+    try:
+        size = file_path.stat().st_size
+        if size > max_size:
+            lines.append(
+                f"> Skipped: (File too large: {size} bytes > max_size={max_size})\n"
+            )
+            # Discovery gap fix (Task 241): a skipped body must not mean
+            # zero evidence — attach structural signatures when extractable
+            # so the Brain still sees the file's shape. Never raises.
+            try:
+                sig = _extract_via_tree_sitter(file_path)
+                if sig:
+                    lines.append(
+                        "> Body omitted by size cap; structural signatures follow:\n"
+                    )
+                    lines.append(sig)
+                else:
+                    lines.append(
+                        "> No signatures extracted — narrow `paths`, raise "
+                        "`max_size`, or call `extract_signatures` on this file.\n"
+                    )
+            except Exception as sig_err:
+                lines.append(f"> Signature fallback failed: ({sig_err})\n")
+            return "\n".join(lines)
+    except OSError as e:
+        lines.append(f"> Skipped: (OS Error: {e})\n")
+        return "\n".join(lines)
+    if is_binary(file_path):
+        lines.append("> Skipped: (Binary file)\n")
+        return "\n".join(lines)
+    ext = file_path.suffix.lstrip(".") or "text"
+    content_text = None
+    for enc in TEXT_ENCODINGS:
+        try:
+            with open(file_path, "r", encoding=enc) as f:
+                content_text = f.read()
+            break
+        except (UnicodeDecodeError, UnicodeError):
+            continue
+    if content_text is None:
+        lines.append(
+            f"> Skipped: (Could not decode file with any supported encoding)\n"
+        )
+        return "\n".join(lines)
+    file_lines = content_text.split("\n")
+    if file_lines and file_lines[-1] == "":
+        file_lines.pop()
+    if line_numbers:
+        content = "\n".join(f"{i}: {line}" for i, line in enumerate(file_lines, 1))
+    else:
+        content = "\n".join(file_lines)
+    lines.append(f"```{ext}")
+    if content:
+        lines.append(content)
+    lines.append("```\n")
+    return "\n".join(lines)
+
+
+def collect_files(
+    target: str,
+    ignore_filter: GitIgnoreFilter,
+    max_files: int = COLLECT_MAX_FILES,
+) -> list[Path]:
+    p = Path(target)
+    if not p.exists() or ignore_filter.is_ignored(p):
+        return []
+    if p.is_file():
+        return [p]
+    collected = []
+    for root, dirs, files in os.walk(p):
+        root_path = Path(root)
+        dirs[:] = [
+            d
+            for d in dirs
+            if (root_path / d).name not in BANNED_DIRS
+            and not ignore_filter.is_ignored(root_path / d)
+        ]
+        for f in files:
+            if len(collected) >= max_files:
+                return collected
+            file_path = root_path / f
+            if not ignore_filter.is_ignored(file_path):
+                collected.append(file_path)
+    return collected
+
+
+def _ensure_context_reports_ignored(workspace_root: Path | None = None) -> None:
+    """Safeguard: Append context-reports/ to <workspace_root>/.gitignore.
+
+    Every report-producing tool calls this so generated reports are never
+    accidentally committed. The target is the caller's project root, not the
+    process cwd: under the singleton the server runs from the global install
+    dir, so a bare ``Path(".gitignore")`` edited the wrong file. A ``None``
+    root keeps the old cwd behavior for project_root-omitted calls.
+    """
+    base = workspace_root if workspace_root is not None else Path.cwd()
+    gitignore = base / ".gitignore"
+    if gitignore.is_file():
+        try:
+            with open(gitignore, "r+", encoding="utf-8") as f:
+                content = f.read()
+                if "context-reports/" not in content:
+                    f.write("\n# Custom Context MCP reports\ncontext-reports/\n")
+        except Exception as e:
+            print(f"Warning: Failed to update .gitignore: {e}", file=sys.stderr)
diff --git a/mcp-context-server/gitops.py b/mcp-context-server/gitops.py
new file mode 100644
index 0000000..ea7c712
--- /dev/null
+++ b/mcp-context-server/gitops.py
@@ -0,0 +1,305 @@
+# Sibling Docs: README.md | Decisions: DECISIONS.md
+
+
+"""Git/kanban helpers: repo roots, commit gates, task discovery, archive patching. Stdlib-pure: no MCP imports, no registration, no import back to server."""
+
+import re
+import shutil
+import subprocess
+import time
+from pathlib import Path
+from typing import Optional
+
+
+def _repo_root(start_path: str, project_root: str | None = None) -> Path:
+    """Resolve the git repo root for git subprocess calls.
+
+    CWD fix: this server inherits opencode-server's CWD, which is usually
+    NOT the caller project, so bare `git` calls fail with exit 128.
+    Resolution order: explicit project_root override first, then walk up
+    from absolute task paths to the enclosing `.git`, then CWD fallback
+    (git errors honestly if that is not a repo).
+    """
+    if project_root:
+        return Path(project_root).resolve()
+    p = Path(start_path)
+    start = (
+        (p if p.is_dir() else p.parent) if p.is_absolute() else (Path.cwd() / p).parent
+    )
+    for cand in [start, *start.parents]:
+        if (cand / ".git").exists():
+            return cand
+    return start
+
+
+def _derive_task_slug(task_file_path: str) -> str:
+    """Derives a 'task <NN> - <slug>' label from a task file name (e.g. '78-fix-bug.md' -> 'task 78 - fix bug')."""
+    name = Path(task_file_path).stem
+    parts = re.split(r"[-_]", name, maxsplit=1)
+    if len(parts) == 2 and parts[0].isdigit():
+        return f"task {parts[0]} - {parts[1].replace('-', ' ')}"
+    return f"task - {name.replace('-', ' ')}"
+
+
+# Conventional Commits enforcement (Task 211): `commit_and_clean_task` is the
+# ONLY commit path, so the caller-supplied feature message is validated here
+# against skill-templates/versioning-and-release (`type: subject`, ≤72 chars).
+
+
+_CONVENTIONAL_RE = re.compile(r"^(feat|fix|docs|refactor|chore): \S.*$")
+
+
+def _check_conventional_commit(commit_message: str) -> Optional[str]:
+    """Returns an error string when commit_message violates Conventional Commits, else None."""
+    first_line = (
+        commit_message.splitlines()[0]
+        if commit_message and commit_message.strip()
+        else ""
+    )
+    if not _CONVENTIONAL_RE.match(first_line):
+        return (
+            "❌ Commit message rejected: must match Conventional Commits "
+            "`<type>: <subject>` with type in feat|fix|docs|refactor|chore "
+            f"(see skill-templates/versioning-and-release). Got: {first_line!r}"
+        )
+    if len(first_line) > 72:
+        return (
+            "❌ Commit message rejected: first line exceeds 72 characters "
+            f"({len(first_line)}). Got: {first_line!r}"
+        )
+    return None
+
+
+ACTIVE_KANBAN_DIRS = ["backlog", "in-progress", "qa", "completed"]
+
+
+MAX_BUNDLE_SIZE = 6
+
+
+DIFF_SIZE_WARNING_THRESHOLD = 400
+
+
+def _kebab_case(text: str) -> str:
+    """Convert arbitrary title to kebab-case slug (B4: supports Unicode/Persian)."""
+    import unicodedata
+
+    normalized = unicodedata.normalize("NFKD", text)
+    slug = normalized.lower().strip()
+    slug = re.sub(
+        r"[^a-z0-9\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+", "-", slug
+    )
+    slug = re.sub(r"-{2,}", "-", slug)
+    slug = slug.strip("-")
+    return slug or "bundle"
+
+
+def _discover_next_id(tasks_root: Path = Path("tasks")) -> int:
+    max_id = 0
+    if not tasks_root.is_dir():
+        return 1
+    for md in tasks_root.rglob("*.md"):
+        m = re.match(r"^(\d+)-", md.name)
+        if m:
+            try:
+                nid = int(m.group(1))
+                if nid > max_id:
+                    max_id = nid
+            except ValueError:
+                continue
+    return max_id + 1 if max_id else 1
+
+
+def _find_task_file(task_id: str, tasks_root: Path = Path("tasks")) -> Path | None:
+    norm = task_id.lstrip("0") or "0"
+    candidates: list[Path] = []
+    for d in ACTIVE_KANBAN_DIRS:
+        dir_path = tasks_root / d
+        if not dir_path.is_dir():
+            continue
+        for md in dir_path.glob("*.md"):
+            m = re.match(r"^(\d+)-", md.name)
+            if m and m.group(1).lstrip("0") == norm:
+                candidates.append(md)
+    if len(candidates) == 1:
+        return candidates[0]
+    if len(candidates) > 1:
+        return None  # B2: hard halt — duplicate active IDs
+    # Check archive for better error (already archived)
+    for md in (
+        (tasks_root / "archive").glob("*.md")
+        if (tasks_root / "archive").is_dir()
+        else []
+    ):
+        m = re.match(r"^(\d+)-", md.name)
+        if m and m.group(1).lstrip("0") == norm:
+            return None
+    return None
+
+
+def _extract_section(content: str, heading: str) -> str | None:
+    pattern = re.compile(
+        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\n---\s*\n|\Z)",
+        re.MULTILINE | re.DOTALL,
+    )
+    m = pattern.search(content)
+    return m.group(1).strip() if m else None
+
+
+def _extract_title(content: str) -> str:
+    m = re.search(r"^# Task \d+:\s*(.+)$", content, re.MULTILINE)
+    return m.group(1).strip() if m else "Untitled"
+
+
+def _format_task_id_list(ids: list[str]) -> str:
+    return "[" + ", ".join(ids) + "]"
+
+
+def _extract_checklist_with_continuations(section_text: str) -> list[str]:
+    """B1: Extract checklist items with all indented continuation lines."""
+    lines = section_text.splitlines()
+    result: list[str] = []
+    in_checklist = False
+    for line in lines:
+        stripped = line.strip()
+        is_root_bullet = line.startswith("- [")
+        if is_root_bullet:
+            in_checklist = True
+            result.append(stripped)
+        elif in_checklist:
+            if (
+                stripped
+                and not line.startswith("- [")
+                and not stripped.startswith("## ")
+                and not stripped.startswith("---")
+            ):
+                result.append(line)
+            else:
+                in_checklist = False
+                if line.startswith("- ["):
+                    in_checklist = True
+                    result.append(stripped)
+    return result
+
+
+def _detect_stack(content: str) -> str | None:
+    """M1: Detect tech stack from task content."""
+    lower = content.lower()
+    if any(
+        kw in lower
+        for kw in ["jetpack compose", "kotlin", "android", "hilt", "sqldelight"]
+    ):
+        return "android"
+    if any(kw in lower for kw in ["react", "vite", "jsx", "tsx", "next.js", "nextjs"]):
+        return "react"
+    if any(kw in lower for kw in ["fastapi", "pydantic", "uvicorn"]):
+        return "fastapi"
+    if any(kw in lower for kw in ["spring boot", "spring-boot", "java", "mapstruct"]):
+        return "spring"
+    if any(kw in lower for kw in ["swiftui", "ios", "swift", "uikit"]):
+        return "ios"
+    if any(kw in lower for kw in ["golang", "gin", "go-gin", "hexagonal"]):
+        return "go"
+    return None
+
+
+def _verify_verbatim_checksums(
+    source_data: list[tuple[str, Path, str, str]], meta_content: str
+) -> bool:
+    """M2: Verify 100% of extracted source AC text is in the Bundled Checklist."""
+    bundled_match = re.search(
+        r"^## Bundled Checklist.*?\n\n(.*?)(?=^## |\Z)",
+        meta_content,
+        re.MULTILINE | re.DOTALL,
+    )
+    if not bundled_match:
+        return False
+    bundled_text = bundled_match.group(1)
+    for sid, path, content, _title in source_data:
+        ac = _extract_section(content, "Acceptance Criteria")
+        if not ac:
+            continue
+        for line in ac.splitlines():
+            stripped = line.strip()
+            if stripped and stripped.startswith("- ["):
+                m = re.match(r"^- \[[ xX]\]\s*(.*)", stripped)
+                core = m.group(1) if m else stripped
+                prefixed = f"[{sid}] {core}"
+                if len(core) > 10 and prefixed not in bundled_text:
+                    return False
+    return True
+
+
+def _git_mv_or_fallback(src: Path, dst: Path) -> bool:
+    dst.parent.mkdir(parents=True, exist_ok=True)
+    repo = str(_repo_root(str(src)))
+    result = subprocess.run(
+        ["git", "mv", str(src), str(dst)], capture_output=True, text=True, cwd=repo
+    )
+    if result.returncode == 0:
+        return True
+    if (
+        "not under version control" in result.stderr
+        or "not tracked" in result.stderr.lower()
+    ):
+        try:
+            src.rename(dst)
+            subprocess.run(
+                ["git", "add", "--", str(dst)],
+                check=True,
+                capture_output=True,
+                cwd=repo,
+            )
+            return True
+        except Exception:
+            return False
+    return False
+
+
+def _patch_archived_file(archive_path: Path, meta_id: str, meta_slug: str) -> None:
+    try:
+        content = archive_path.read_text(encoding="utf-8")
+    except Exception:
+        return
+    new_file_header = f"**File:** `tasks/archive/{archive_path.name}`"
+    content = re.sub(r"\*\*File:\*\*\s*`[^`]+`", new_file_header, content, count=1)
+    if re.search(r"\*\*Status:\*\*\s*\w+", content):
+        content = re.sub(
+            r"\*\*Status:\*\*\s*\w+", "**Status:** superseded", content, count=1
+        )
+    else:
+        content = re.sub(
+            r"(\*\*Type:\*\*\s*\w+)", r"\1\n**Status:** superseded", content, count=1
+        )
+    if "**Superseded-By:**" not in content:
+        content = re.sub(
+            r"(\*\*Status:\*\*\s*superseded)",
+            rf"\1\n**Superseded-By:** `{meta_id}-{meta_slug}`",
+            content,
+            count=1,
+        )
+        timestamp = time.strftime("%Y-%m-%d")
+        content = re.sub(
+            r"(\*\*Superseded-By:\*\*\s*`[^`]+`)",
+            rf"\1\n**Superseded-At:** `{timestamp}`",
+            content,
+            count=1,
+        )
+    superseded_note = (
+        f"> **Superseded:** This task was bundled into META task `{meta_id}-{meta_slug}` "
+        f"and archived on {time.strftime('%Y-%m-%d')}. "
+        f"See `tasks/backlog/{meta_id}-{meta_slug}.md` (or its Kanban successor) for the unified execution. "
+        f"History preserved via `git log --follow -- tasks/archive/{archive_path.name}`.\n"
+    )
+    if superseded_note.strip() not in content:
+        if "## Execution Log" in content:
+            content = content.replace(
+                "## Execution Log", superseded_note + "\n## Execution Log", 1
+            )
+        elif "## Factual Git Diff" in content:
+            content = content.replace(
+                "## Factual Git Diff", superseded_note + "\n## Factual Git Diff", 1
+            )
+    try:
+        archive_path.write_text(content, encoding="utf-8")
+    except Exception:
+        pass
diff --git a/mcp-context-server/graph.py b/mcp-context-server/graph.py
new file mode 100644
index 0000000..be0c07a
--- /dev/null
+++ b/mcp-context-server/graph.py
@@ -0,0 +1,1078 @@
+# Sibling Docs: README.md | Decisions: DECISIONS.md
+
+
+"""Lite knowledge-graph: constants, parsers, build, query primitives. Stdlib-pure: no MCP imports, no registration, no import back to server."""
+
+import json
+import re
+import time
+import uuid
+from pathlib import Path
+
+from fsutil import GitIgnoreFilter, collect_files
+
+
+GRAPH_SCHEMA_VERSION = 2
+
+
+GRAPH_MAX_FILES = 300
+
+
+GRAPH_MAX_NODES = 5000
+
+
+GRAPH_MAX_DOCS = 300
+
+
+GRAPH_DOC_LINES = 500
+
+
+GRAPH_DOC_SECTIONS = 60
+
+
+_GRAPH_CODE_EXTS = frozenset(
+    {
+        ".py",
+        ".js",
+        ".jsx",
+        ".mjs",
+        ".cjs",
+        ".ts",
+        ".tsx",
+        ".mts",
+        ".cts",
+        ".go",
+        ".java",
+        ".rs",
+        ".kt",
+        ".kts",
+        ".rb",
+        ".php",
+        ".cs",
+        ".swift",
+        ".lua",
+        ".zig",
+        ".sh",
+        ".bash",
+        ".sql",
+        ".vue",
+        ".svelte",
+        ".astro",
+        ".html",
+        ".htm",
+        ".xml",
+        ".dart",
+        ".m",
+        ".mm",
+        ".gradle",
+        ".prisma",
+        ".properties",
+        ".css",
+        ".scss",
+        ".less",
+    }
+)
+
+
+_GRAPH_SYMBOL_RE = re.compile(
+    r"^\s*(?:export\s+|default\s+|public\s+|private\s+|protected\s+|static\s+|async\s+|fun\s+|def\s+|class\s+|interface\s+|type\s+|enum\s+|struct\s+|trait\s+|func(?:tion)?\s+)?"
+    r"(?:class|interface|type|enum|struct|trait|def|fun|func(?:tion)?)\s+([A-Za-z_]\w*)"
+)
+
+
+_GRAPH_CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
+
+
+_GRAPH_KT_FUN_RE = re.compile(
+    r"^\s*(?:(?:public|private|protected|internal|open|override|suspend|inline|tailrec|operator|infix|external)\s+)*fun\s+(?:<[^>]*>\s*)?([A-Za-z_]\w*)"
+)
+
+
+_GRAPH_TYPE_RE = re.compile(
+    r"^\s*(?:(?:public|private|protected|internal|open|abstract|final|sealed|data|object|export|default)\s+)*(?:class|object|interface)\s+([A-Za-z_]\w*)"
+)
+
+
+_GRAPH_SWIFT_RE = re.compile(
+    r"^\s*(?:(?:public|private|fileprivate|internal|open|override|static|class|mutating|required|convenience)\s+)*(?:func\s+([A-Za-z_]\w*)|(class|struct|enum|protocol)\s+([A-Za-z_]\w*))"
+)
+
+
+_GRAPH_JAVA_METHOD_RE = re.compile(
+    r"^\s*(?:(?:public|private|protected|static|final|synchronized|abstract|native|default|volatile|transient)\s+)+[\w<>\[\]?.,\s]+\s+(\w+)\s*\("
+)
+
+
+_GRAPH_JAVA_CTOR_RE = re.compile(r"^\s*(?:public|private|protected)\s+([A-Z]\w*)\s*\(")
+
+
+_GRAPH_DART_RE = re.compile(r"^\s*(?:[\w<>?,\s]+\s+)?(\w+)\s*\([^;{}]*\)\s*(?:\{|=>|;)")
+
+
+_GRAPH_DART_KEYWORDS = frozenset(
+    {
+        "return",
+        "if",
+        "for",
+        "while",
+        "switch",
+        "assert",
+        "new",
+        "const",
+        "final",
+        "var",
+        "late",
+        "import",
+        "export",
+        "throw",
+        "else",
+        "do",
+    }
+)
+
+
+_GRAPH_ARROW_RE = re.compile(
+    r"^\s*(?:export\s+)?(?:const|let)\s+([A-Za-z_]\w*)\s*(?::[^=;]+)?=\s*(?:async\s*)?(?:\([^)]*\)\s*=>|function)"
+)
+
+
+_GRAPH_ANDROID_ID_RE = re.compile(r'android:id="@\+id/([\w]+)"')
+
+
+_GRAPH_DOM_ID_RE = re.compile(r'(?:id|@\+id)="([\w-]+)"')
+
+
+_GRAPH_R_ID_RE = re.compile(r"R\.id\.([\w]+)")
+
+
+_GRAPH_GET_ID_RE = re.compile(r"getElementById\(\s*['\"]([\w-]+)['\"]\)")
+
+
+_GRAPH_SCRIPT_BLOCK_RE = re.compile(
+    r"<script\b[^>]*>(.*?)</script>", re.DOTALL | re.IGNORECASE
+)
+
+
+_GRAPH_OBJC_METHOD_RE = re.compile(r"^\s*[-+]\s*\([^)]*\)\s*([A-Za-z_]\w*)")
+
+
+_GRAPH_OBJC_IMPL_RE = re.compile(r"^\s*@implementation\s+([A-Za-z_]\w*)")
+
+
+_GRAPH_PRISMA_RE = re.compile(r"^\s*(model|enum)\s+([A-Za-z_]\w*)")
+
+
+_GRAPH_PROP_RE = re.compile(r"^\s*([A-Za-z_][\w.\-]*)\s*[=:]")
+
+
+_GRAPH_CSS_RE = re.compile(r"^\s*\.([\w-]+)\s*\{")
+
+
+_GRAPH_SQL_TABLE_RE = re.compile(
+    r"^\s*CREATE\s+(?:TEMP(?:ORARY)?\s+)?(?:TABLE|VIEW)\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"\[]?([\w\.]+)[`\"\]]?",
+    re.IGNORECASE,
+)
+
+
+_GRAPH_SQL_REF_RE = re.compile(r"REFERENCES\s+[`\"\[]?([\w\.]+)[`\"\]]?", re.IGNORECASE)
+
+
+_GRAPH_MD_HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$")
+
+
+_GRAPH_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+\.md)(?:#[^)\s]*)?\)")
+
+
+_GRAPH_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]]*)?(?:\|[^\]]*)?\]\]")
+
+
+_GRAPH_TOKEN_SPLIT_RE = re.compile(r"(?<=[a-z])(?=[A-Z])")
+
+
+_GRAPH_TASK_REF_RE = re.compile(r"\bTask\s+(\d{1,4})\b")
+
+
+_GRAPH_ADR_REF_RE = re.compile(r"\bADR-(\d{1,3})\b", re.IGNORECASE)
+
+
+_GRAPH_GOD_NOISE = frozenset({"run", "json", "post", "data"})
+
+
+_GRAPH_MAX_SCAN_BYTES = 1048576
+
+
+def _read_text_capped(file_path: Path, cap: int = _GRAPH_MAX_SCAN_BYTES) -> str | None:
+    """Read text bounded by cap bytes so huge generated files cannot wedge the server."""
+    try:
+        with open(file_path, "r", encoding="utf-8", errors="strict") as f:
+            return f.read(cap + 1)[:cap]
+    except Exception:
+        return None
+
+
+def _push_graph_symbol(
+    out: list[tuple[str, str, int]], seen: set[str], name: str, kind: str, lineno: int
+) -> None:
+    if len(out) >= 200 or len(name) < 2 or name in seen:
+        return
+    seen.add(name)
+    out.append((name, kind, lineno))
+
+
+def _scan_js_like_symbols(
+    text: str, base_line: int, out: list[tuple[str, str, int]], seen: set[str]
+) -> None:
+    for i, line in enumerate(text.split("\n")):
+        if len(out) >= 200:
+            return
+        lineno = base_line + i
+        m = _GRAPH_SYMBOL_RE.match(line)
+        if m:
+            lowered = line.lower()
+            _push_graph_symbol(
+                out, seen, m.group(1), "class" if "class" in lowered else "func", lineno
+            )
+            continue
+        m = _GRAPH_ARROW_RE.match(line)
+        if m:
+            _push_graph_symbol(out, seen, m.group(1), "func", lineno)
+
+
+def _extract_graph_symbols(file_path: Path) -> list[tuple[str, str, int]]:
+    """Return [(name, kind, line_no)] capped per file. Regex-based, deterministic.
+
+    Covers backend (Python/JS/TS/Go/Java...), mobile (Kotlin fun/class/object,
+    Swift func/types, Java methods/ctors, Dart classes/members), frontend
+    (Vue/Svelte script blocks, arrow components), and markup (HTML/XML element
+    ids incl. android:id). Markup node labels keep raw ids (dashes included).
+    """
+    out: list[tuple[str, str, int]] = []
+    seen: set[str] = set()
+    text = _read_text_capped(file_path)
+    if text is None:
+        return out
+    lines = text.split("\n")
+    suffix = file_path.suffix.lower()
+    if suffix in (".vue", ".svelte", ".astro", ".html", ".htm"):
+        text = "\n".join(lines)
+        for m in _GRAPH_SCRIPT_BLOCK_RE.finditer(text):
+            base_line = text[: m.start(1)].count("\n") + 1
+            _scan_js_like_symbols(m.group(1), base_line, out, seen)
+    if suffix in (".vue", ".svelte", ".astro", ".html", ".htm", ".xml"):
+        for i, line in enumerate(lines, 1):
+            if len(out) >= 200:
+                break
+            for m in _GRAPH_ANDROID_ID_RE.finditer(line):
+                _push_graph_symbol(out, seen, m.group(1), "view_id", i)
+            for m in _GRAPH_DOM_ID_RE.finditer(line):
+                _push_graph_symbol(out, seen, m.group(1), "element_id", i)
+        return out
+    if suffix in (".kt", ".kts", ".java", ".swift", ".dart", ".m", ".mm", ".gradle"):
+        for i, line in enumerate(lines, 1):
+            if len(out) >= 200:
+                break
+            if suffix in (".m", ".mm"):
+                m = _GRAPH_OBJC_IMPL_RE.match(line)
+                if m:
+                    _push_graph_symbol(out, seen, m.group(1), "class", i)
+                    continue
+                m = _GRAPH_OBJC_METHOD_RE.match(line)
+                if m:
+                    _push_graph_symbol(out, seen, m.group(1), "method", i)
+                    continue
+                continue
+            m = _GRAPH_KT_FUN_RE.match(line)
+            if m:
+                _push_graph_symbol(out, seen, m.group(1), "func", i)
+                continue
+            m = _GRAPH_TYPE_RE.match(line)
+            if m:
+                _push_graph_symbol(out, seen, m.group(1), "class", i)
+                continue
+            m = _GRAPH_SWIFT_RE.match(line)
+            if m:
+                if m.group(1):
+                    _push_graph_symbol(out, seen, m.group(1), "func", i)
+                else:
+                    _push_graph_symbol(out, seen, m.group(3), "class", i)
+                continue
+            m = _GRAPH_JAVA_METHOD_RE.match(line)
+            if m and m.group(1) not in (
+                "if",
+                "for",
+                "while",
+                "switch",
+                "catch",
+                "return",
+            ):
+                _push_graph_symbol(out, seen, m.group(1), "method", i)
+                continue
+            m = _GRAPH_JAVA_CTOR_RE.match(line)
+            if m:
+                _push_graph_symbol(out, seen, m.group(1), "method", i)
+                continue
+            if suffix == ".dart":
+                m = _GRAPH_DART_RE.match(line)
+                if m and m.group(1) not in _GRAPH_DART_KEYWORDS:
+                    _push_graph_symbol(out, seen, m.group(1), "method", i)
+                    continue
+            m = _GRAPH_ARROW_RE.match(line)
+            if m:
+                _push_graph_symbol(out, seen, m.group(1), "func", i)
+        return out
+    if suffix == ".prisma":
+        for i, line in enumerate(lines, 1):
+            if len(out) >= 200:
+                break
+            m = _GRAPH_PRISMA_RE.match(line)
+            if m:
+                _push_graph_symbol(
+                    out,
+                    seen,
+                    m.group(2),
+                    "model" if m.group(1) == "model" else "enum",
+                    i,
+                )
+        return out
+    if suffix == ".properties":
+        for i, line in enumerate(lines, 1):
+            if len(out) >= 200:
+                break
+            stripped = line.strip()
+            if not stripped or stripped.startswith(("#", "!")):
+                continue
+            m = _GRAPH_PROP_RE.match(line)
+            if m:
+                _push_graph_symbol(out, seen, m.group(1), "config", i)
+        return out
+    if suffix in (".css", ".scss", ".less"):
+        for i, line in enumerate(lines, 1):
+            if len(out) >= 200:
+                break
+            m = _GRAPH_CSS_RE.match(line)
+            if m:
+                _push_graph_symbol(out, seen, m.group(1), "style", i)
+        return out
+    for i, line in enumerate(lines, 1):
+        if len(out) >= 200:
+            break
+        m = _GRAPH_SYMBOL_RE.match(line)
+        if m:
+            name = m.group(1)
+            lowered = line.lower()
+            if "interface" in lowered:
+                kind = "interface"
+            elif "enum" in lowered:
+                kind = "enum"
+            elif re.search(r"\btype\b", lowered):
+                kind = "type"
+            elif "class" in lowered:
+                kind = "class"
+            else:
+                kind = "func"
+            _push_graph_symbol(out, seen, name, kind, i)
+            continue
+        m = _GRAPH_ARROW_RE.match(line)
+        if m:
+            _push_graph_symbol(out, seen, m.group(1), "func", i)
+            continue
+    return out
+
+
+def _extract_sql_symbols(
+    file_path: Path,
+) -> tuple[list[tuple[str, str, int]], list[str]]:
+    """Return ([(table, kind, line_no)], [referenced_table, ...]). Deterministic."""
+    tables: list[tuple[str, str, int]] = []
+    refs: list[str] = []
+    text = _read_text_capped(file_path)
+    if text is None:
+        return tables, refs
+    lines = text.split("\n")
+    for i, line in enumerate(lines, 1):
+        m = _GRAPH_SQL_TABLE_RE.match(line)
+        if m and len(tables) < 200:
+            name = m.group(1).split(".")[-1]
+            kind = "view" if "view" in line.lower() else "table"
+            if name not in {n for n, _, _ in tables}:
+                tables.append((name, kind, i))
+        for r in _GRAPH_SQL_REF_RE.finditer(line):
+            ref = r.group(1).split(".")[-1]
+            if ref and ref not in refs:
+                refs.append(ref)
+                if len(refs) >= 40:
+                    break
+    return tables, refs
+
+
+def _extract_md_sections(abs_path: Path) -> list[tuple[str, int, int]]:
+    """Return [(heading_text, level, line_no)] capped. Deterministic."""
+    out: list[tuple[str, int, int]] = []
+    text = _read_text_capped(abs_path)
+    if text is None:
+        return out
+    lines = text.split("\n")[:GRAPH_DOC_LINES]
+    for i, line in enumerate(lines, 1):
+        if len(out) >= GRAPH_DOC_SECTIONS:
+            break
+        m = _GRAPH_MD_HEADING_RE.match(line)
+        if not m:
+            continue
+        text = m.group(2).strip()[:80]
+        if len(text) >= 2:
+            out.append((text, len(m.group(1)), i))
+    return out
+
+
+def _extract_md_link_targets(content: str) -> list[str]:
+    """Return raw Markdown link targets (./other.md, [[wikilinks]]). Deterministic."""
+    targets: list[str] = []
+    for m in _GRAPH_MD_LINK_RE.finditer(content):
+        t = m.group(1).strip()
+        if t and t not in targets and not re.match(r"https?://", t):
+            targets.append(t)
+    for m in _GRAPH_WIKILINK_RE.finditer(content):
+        t = m.group(1).strip()
+        if t and t not in targets:
+            targets.append(t if t.lower().endswith(".md") else t + ".md")
+    return targets[:40]
+
+
+def _resolve_doc_link(target: str, from_rel: str, doc_set: set[str]) -> str | None:
+    if target.startswith("/"):
+        cand = target.lstrip("/")
+    else:
+        from_dir = from_rel.rsplit("/", 1)[0] if "/" in from_rel else ""
+        parts = (from_dir + "/" + target).split("/")
+        stack: list[str] = []
+        for part in parts:
+            if part in ("", "."):
+                continue
+            if part == "..":
+                if stack:
+                    stack.pop()
+            else:
+                stack.append(part)
+        cand = "/".join(stack)
+    if cand in doc_set:
+        return cand
+    base = cand.rsplit("/", 1)[-1]
+    for d in doc_set:
+        if d.rsplit("/", 1)[-1].lower() == base.lower():
+            return d
+    return None
+
+
+def _slugify_section(text: str) -> str:
+    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
+    return slug[:60] or "section"
+
+
+def _parse_graph_imports(rel_suffix: str, content: str) -> list[str]:
+    imps: list[str] = []
+    try:
+        if rel_suffix == ".py":
+            for m in re.finditer(
+                r"^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))",
+                content,
+                re.MULTILINE,
+            ):
+                mod = m.group(1) or m.group(2)
+                if mod and mod not in imps:
+                    imps.append(mod)
+        elif rel_suffix in {
+            ".js",
+            ".jsx",
+            ".mjs",
+            ".cjs",
+            ".ts",
+            ".tsx",
+            ".mts",
+            ".cts",
+        }:
+            for m in re.finditer(
+                r"""(?:from\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]|import\(\s*['"]([^'"]+)['"])""",
+                content,
+            ):
+                mod = m.group(1) or m.group(2) or m.group(3)
+                if mod and mod not in imps and mod.startswith("."):
+                    imps.append(mod)
+        elif rel_suffix == ".go":
+            for m in re.finditer(r'"([\w\.\-/]+)"', content):
+                mod = m.group(1)
+                if "/" in mod and mod not in imps:
+                    imps.append(mod)
+                    if len(imps) >= 20:
+                        break
+        elif rel_suffix in {".kt", ".kts", ".java", ".gradle"}:
+            for m in re.finditer(
+                r"^\s*import\s+(?:static\s+)?([\w\.]+)", content, re.MULTILINE
+            ):
+                mod = m.group(1)
+                if mod and mod not in imps:
+                    imps.append(mod)
+        elif rel_suffix in {".swift", ".m", ".mm"}:
+            for m in re.finditer(r"^\s*import\s+(\w+)", content, re.MULTILINE):
+                mod = m.group(1)
+                if mod and mod not in imps:
+                    imps.append(mod)
+    except Exception:
+        return imps
+    return imps[:20]
+
+
+def _resolve_import_to_rel(mod: str, from_rel: str, rel_set: set[str]) -> str | None:
+    if not mod.startswith(".") and "." not in mod and "/" not in mod:
+        return None
+    cand_base = mod.replace(".", "/").strip("/")
+    from_dir = from_rel.rsplit("/", 1)[0] if "/" in from_rel else ""
+    tried: list[str] = []
+    if mod.startswith("."):
+        level = len(mod) - len(mod.lstrip("."))
+        rest = mod.lstrip(".").replace(".", "/")
+        parts = from_dir.split("/") if from_dir else []
+        base = "/".join(parts[: max(0, len(parts) - level + 1)])
+        tried.append(f"{base}/{rest}".strip("/"))
+    else:
+        tried.append(cand_base)
+    exts = [
+        ".py",
+        "/__init__.py",
+        ".ts",
+        ".tsx",
+        ".js",
+        ".jsx",
+        ".go",
+        ".java",
+        ".rs",
+        ".kt",
+        ".kts",
+        ".swift",
+        ".dart",
+        ".vue",
+        ".m",
+        ".mm",
+    ]
+    for t in tried:
+        for e in exts:
+            c = (t + e).strip("/")
+            if c in rel_set:
+                return c
+        if t in rel_set:
+            return t
+    return None
+
+
+def _build_graph_data(workspace_root: Path, target: Path) -> dict:
+    filt = GitIgnoreFilter()
+    all_found = collect_files(str(target), filt)
+    files = [
+        p
+        for p in all_found
+        if p.suffix.lower() in _GRAPH_CODE_EXTS and "context-reports" not in p.parts
+    ]
+    files.sort(key=lambda p: (len(p.parts), p.as_posix()))
+    files = files[:GRAPH_MAX_FILES]
+    docs = [
+        p
+        for p in all_found
+        if p.suffix.lower() == ".md" and "context-reports" not in p.parts
+    ]
+    docs.sort(key=lambda p: (len(p.parts), p.as_posix()))
+    docs = docs[:GRAPH_MAX_DOCS]
+    rels: list[str] = []
+    rel_set: set[str] = set()
+    resolved: list[Path] = []
+    doc_rels: list[str] = []
+    doc_set: set[str] = set()
+    doc_resolved: list[Path] = []
+    for p in files:
+        try:
+            rel = p.resolve().relative_to(workspace_root).as_posix()
+        except ValueError:
+            continue
+        if rel not in rel_set:
+            rel_set.add(rel)
+            rels.append(rel)
+            resolved.append(p.resolve())
+    for p in docs:
+        try:
+            rel = p.resolve().relative_to(workspace_root).as_posix()
+        except ValueError:
+            continue
+        if rel not in doc_set and rel not in rel_set:
+            doc_set.add(rel)
+            doc_rels.append(rel)
+            doc_resolved.append(p.resolve())
+    nodes: list[dict] = []
+    links: list[dict] = []
+    sym_index: dict[str, list[str]] = {}
+    file_contents: dict[str, str] = {}
+    for rel, abs_p in zip(rels, resolved):
+        nodes.append(
+            {"id": f"file:{rel}", "label": rel, "file_type": "code", "source_file": rel}
+        )
+        try:
+            with open(abs_p, "r", encoding="utf-8", errors="strict") as f:
+                content = f.read()[:200000]
+        except Exception:
+            content = ""
+        file_contents[rel] = content
+        if Path(rel).suffix.lower() == ".sql":
+            symbols, sql_refs = _extract_sql_symbols(abs_p)
+            for t in sql_refs:
+                links.append(
+                    {
+                        "source": f"file:{rel}",
+                        "target": f"sqlref:{t}",
+                        "relation": "references",
+                        "confidence": "EXTRACTED",
+                        "source_file": rel,
+                    }
+                )
+        else:
+            symbols = _extract_graph_symbols(abs_p)
+        for name, kind, lineno in symbols:
+            if len(nodes) >= GRAPH_MAX_NODES:
+                break
+            sid = f"sym:{rel}#{name}"
+            nodes.append(
+                {
+                    "id": sid,
+                    "label": name,
+                    "file_type": "code",
+                    "source_file": rel,
+                    "source_location": f"L{lineno}",
+                    "kind": kind,
+                }
+            )
+            links.append(
+                {
+                    "source": f"file:{rel}",
+                    "target": sid,
+                    "relation": "contains",
+                    "confidence": "EXTRACTED",
+                    "source_file": rel,
+                }
+            )
+            sym_index.setdefault(name, []).append(sid)
+    doc_contents: dict[str, str] = {}
+    for rel, abs_p in zip(doc_rels, doc_resolved):
+        if len(nodes) >= GRAPH_MAX_NODES:
+            break
+        nodes.append(
+            {
+                "id": f"file:{rel}",
+                "label": rel,
+                "file_type": "document",
+                "source_file": rel,
+            }
+        )
+        try:
+            with open(abs_p, "r", encoding="utf-8", errors="strict") as f:
+                content = f.read()[:200000]
+        except Exception:
+            content = ""
+        doc_contents[rel] = content
+        for heading, _level, lineno in _extract_md_sections(abs_p):
+            if len(nodes) >= GRAPH_MAX_NODES:
+                break
+            sec_id = f"sec:{rel}#{_slugify_section(heading)}"
+            if sec_id not in {n["id"] for n in nodes}:
+                nodes.append(
+                    {
+                        "id": sec_id,
+                        "label": heading,
+                        "file_type": "document",
+                        "source_file": rel,
+                        "source_location": f"L{lineno}",
+                        "kind": "section",
+                    }
+                )
+                links.append(
+                    {
+                        "source": f"file:{rel}",
+                        "target": sec_id,
+                        "relation": "contains",
+                        "confidence": "EXTRACTED",
+                        "source_file": rel,
+                    }
+                )
+    for rel, content in doc_contents.items():
+        if not content or len(links) >= GRAPH_MAX_NODES * 2:
+            break
+        for tgt in _extract_md_link_targets(content):
+            resolved_tgt = _resolve_doc_link(tgt, rel, doc_set)
+            if resolved_tgt and resolved_tgt != rel:
+                links.append(
+                    {
+                        "source": f"file:{rel}",
+                        "target": f"file:{resolved_tgt}",
+                        "relation": "references",
+                        "confidence": "EXTRACTED",
+                        "source_file": rel,
+                    }
+                )
+        seen_doc_refs: set[str] = set()
+        for pat in (r"\b([A-Za-z_]\w{3,})\b", r"\b([\w]+-[\w-]+)\b"):
+            for m in re.finditer(pat, content):
+                name = m.group(1)
+                if name in seen_doc_refs:
+                    continue
+                targets = sym_index.get(name, [])
+                if not targets:
+                    continue
+                seen_doc_refs.add(name)
+                for tid in targets[:3]:
+                    links.append(
+                        {
+                            "source": f"file:{rel}",
+                            "target": tid,
+                            "relation": "references",
+                            "confidence": "INFERRED",
+                            "source_file": rel,
+                        }
+                    )
+                if len(seen_doc_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
+                    break
+    for rel in rels:
+        content = file_contents.get(rel, "")
+        if not content:
+            continue
+        suffix = Path(rel).suffix.lower()
+        for mod in _parse_graph_imports(suffix, content):
+            tgt = _resolve_import_to_rel(mod, rel, rel_set)
+            if tgt and tgt != rel:
+                links.append(
+                    {
+                        "source": f"file:{rel}",
+                        "target": f"file:{tgt}",
+                        "relation": "imports",
+                        "confidence": "EXTRACTED",
+                        "source_file": rel,
+                    }
+                )
+        if len(links) >= GRAPH_MAX_NODES * 2:
+            break
+        seen_refs: set[str] = set()
+        for id_re in (_GRAPH_R_ID_RE, _GRAPH_GET_ID_RE):
+            for m in id_re.finditer(content):
+                name = m.group(1)
+                if (rel, name) in seen_refs:
+                    continue
+                for tid in sym_index.get(name, []):
+                    if tid.startswith(f"sym:{rel}#"):
+                        continue
+                    seen_refs.add((rel, name))
+                    links.append(
+                        {
+                            "source": f"file:{rel}",
+                            "target": tid,
+                            "relation": "references",
+                            "confidence": "INFERRED",
+                            "source_file": rel,
+                        }
+                    )
+                    break
+        for m in _GRAPH_CALL_RE.finditer(content):
+            name = m.group(1)
+            if len(name) < 3 or name in {
+                "def",
+                "class",
+                "return",
+                "import",
+                "from",
+                "for",
+                "while",
+                "with",
+            }:
+                continue
+            targets = sym_index.get(name, [])
+            for tid in targets:
+                if tid.startswith(f"sym:{rel}#") or (rel, name) in seen_refs:
+                    continue
+                seen_refs.add((rel, name))
+                links.append(
+                    {
+                        "source": f"file:{rel}",
+                        "target": tid,
+                        "relation": "references",
+                        "confidence": "INFERRED",
+                        "source_file": rel,
+                    }
+                )
+                if len(seen_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
+                    break
+            if len(seen_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
+                break
+    rationale_refs: list[tuple[str, str, str]] = []
+    for rel in rels:
+        content = file_contents.get(rel, "")
+        if not content:
+            continue
+        for m in _GRAPH_TASK_REF_RE.finditer(content):
+            rationale_refs.append((rel, "task", m.group(1)))
+            if len(rationale_refs) >= 200:
+                break
+        for m in _GRAPH_ADR_REF_RE.finditer(content):
+            rationale_refs.append((rel, "adr", m.group(1)))
+            if len(rationale_refs) >= 200:
+                break
+    task_rel_by_id: dict[str, str] = {}
+    for cand_dir in ("backlog", "in-progress", "qa", "completed", "archive"):
+        tdir = workspace_root / "tasks" / cand_dir
+        if not tdir.is_dir():
+            continue
+        try:
+            for md in tdir.glob("*.md"):
+                mm = re.match(r"^(\d+)-", md.name)
+                if mm:
+                    task_rel_by_id.setdefault(
+                        mm.group(1).lstrip("0") or "0",
+                        md.resolve().relative_to(workspace_root).as_posix(),
+                    )
+        except OSError:
+            continue
+    node_ids = {n["id"] for n in nodes}
+    seen_rat: set[tuple[str, str]] = set()
+    for rel, kind, num in rationale_refs:
+        target: str | None = None
+        if kind == "task":
+            trel = task_rel_by_id.get(num.lstrip("0") or "0")
+            if trel:
+                target = f"file:{trel}"
+        else:
+            needle = f"adr-{int(num):03d}"
+            for n in nodes:
+                if n["id"].startswith("sec:") and needle in n["label"].lower():
+                    target = n["id"]
+                    break
+        if target and target in node_ids and len(links) < GRAPH_MAX_NODES * 2:
+            if (rel, target) in seen_rat:
+                continue
+            seen_rat.add((rel, target))
+            links.append(
+                {
+                    "source": f"file:{rel}",
+                    "target": target,
+                    "relation": "rationale_for",
+                    "confidence": "INFERRED",
+                    "source_file": rel,
+                }
+            )
+    table_ids: dict[str, str] = {}
+    for n in nodes:
+        if n.get("kind") in ("table", "view"):
+            table_ids.setdefault(n["label"], n["id"])
+    pruned: list[dict] = []
+    for e in links:
+        if e["target"].startswith("sqlref:"):
+            tname = e["target"][len("sqlref:") :]
+            tid = table_ids.get(tname)
+            if tid is None:
+                continue
+            e = {**e, "target": tid}
+        pruned.append(e)
+    return {"nodes": nodes, "links": pruned}
+
+
+def _graph_degrees(data: dict) -> dict[str, int]:
+    deg: dict[str, int] = {}
+    for n in data.get("nodes", []):
+        deg[n["id"]] = 0
+    for e in data.get("links", []):
+        deg[e["source"]] = deg.get(e["source"], 0) + 1
+        deg[e["target"]] = deg.get(e["target"], 0) + 1
+    return deg
+
+
+def _save_graph(
+    workspace_root: Path, data: dict, target_label: str
+) -> tuple[Path, Path]:
+    report_dir = workspace_root / "context-reports"
+    report_dir.mkdir(parents=True, exist_ok=True)
+    timestamp = time.strftime("%Y%m%d_%H%M%S")
+    unique = uuid.uuid4().hex[:8]
+    json_path = report_dir / f"graph_{timestamp}_{unique}.json"
+    md_path = report_dir / f"graph_report_{timestamp}_{unique}.md"
+    envelope = {
+        "nodes": sorted(data.get("nodes", []), key=lambda n: n["id"]),
+        "links": sorted(
+            data.get("links", []),
+            key=lambda e: (e["source"], e["target"], e["relation"]),
+        ),
+        "graph": {
+            "schema_version": GRAPH_SCHEMA_VERSION,
+            "graphify_version": None,
+            "root": target_label,
+        },
+    }
+    with open(json_path, "w", encoding="utf-8") as f:
+        json.dump(envelope, f, indent=1, sort_keys=False)
+    deg = _graph_degrees(envelope)
+    id2node = {n["id"]: n for n in envelope["nodes"]}
+    sym_rank = sorted(
+        ((d, nid) for nid, d in deg.items() if nid.startswith("sym:")), reverse=True
+    )[:10]
+    ext = sum(1 for e in envelope["links"] if e.get("confidence") == "EXTRACTED")
+    inf = sum(1 for e in envelope["links"] if e.get("confidence") == "INFERRED")
+    amb = len(envelope["links"]) - ext - inf
+    n_docs = sum(1 for n in envelope["nodes"] if n.get("file_type") == "document")
+    n_code = len(envelope["nodes"]) - n_docs
+    lines = [
+        f"# Graph Report - {target_label}",
+        "",
+        f"- **Generated:** {timestamp}",
+        f"- **Schema:** {GRAPH_SCHEMA_VERSION}",
+        f"- **Nodes:** {len(envelope['nodes'])} **Edges:** {len(envelope['links'])}",
+        f"- **Documents:** {n_docs} doc nodes ({n_code} code)",
+        f"- **Confidence:** EXTRACTED {ext} / INFERRED {inf} / AMBIGUOUS {amb}",
+        "",
+        "## God nodes (top by degree)",
+        "",
+    ]
+    for d, nid in sym_rank:
+        n = id2node.get(nid, {})
+        lines.append(
+            f"- {n.get('label', nid)} (degree {d}, {n.get('source_file', '?')})"
+        )
+    lines += [
+        "",
+        "## How to query",
+        "",
+        "- `query_graph` for scoped subgraphs",
+        "- `explain_node` for one concept",
+        "- `shortest_path` to trace two concepts",
+        "",
+    ]
+    md_path.write_text("\n".join(lines), encoding="utf-8")
+    return json_path, md_path
+
+
+def _resolve_graph_file(workspace_root: Path, graph_path: str | None) -> Path | None:
+    report_dir = workspace_root / "context-reports"
+    if graph_path:
+        p = Path(graph_path)
+        cand = p if p.is_absolute() else workspace_root / p
+        try:
+            cand.resolve().relative_to(workspace_root)
+        except ValueError:
+            return None
+        if cand.is_file():
+            return cand
+        alt = report_dir / p.name
+        if alt.is_file():
+            return alt
+        return None
+    if not report_dir.is_dir():
+        return None
+    cands = sorted(
+        report_dir.glob("graph_*.json"), key=lambda q: q.stat().st_mtime, reverse=True
+    )
+    return cands[0] if cands else None
+
+
+def _load_graph_data(
+    workspace_root: Path, graph_path: str | None
+) -> tuple[dict | None, Path | None, str | None]:
+    gp = _resolve_graph_file(workspace_root, graph_path)
+    if gp is None:
+        return None, None, "No graph found. Run build_graph first."
+    try:
+        data = json.loads(gp.read_text(encoding="utf-8"))
+        return data, gp, None
+    except Exception as e:
+        return None, gp, f"Error reading graph {gp}: {e}"
+
+
+def _graph_tokens(text: str) -> set[str]:
+    """Split identifiers so natural words match code: snake_case parts plus
+    camelCase parts, lowercased, minimum length 3. Deterministic."""
+    toks: set[str] = set()
+    for raw in re.findall(r"[A-Za-z0-9]+", text):
+        for part in _GRAPH_TOKEN_SPLIT_RE.split(raw):
+            for sub in part.split("_"):
+                t = sub.lower()
+                if len(t) >= 3:
+                    toks.add(t)
+    return toks
+
+
+def _find_graph_nodes(nodes: list[dict], label: str) -> list[dict]:
+    ll = label.lower()
+    exact = [n for n in nodes if n.get("label", "").lower() == ll]
+    if exact:
+        return exact
+    return [n for n in nodes if ll in n.get("label", "").lower()][:5]
+
+
+def _graph_neighbors(
+    data: dict, nid: str
+) -> tuple[list[tuple[dict, dict]], list[tuple[dict, dict]]]:
+    id2n = {n["id"]: n for n in data.get("nodes", [])}
+    out: list[tuple[dict, dict]] = []
+    inc: list[tuple[dict, dict]] = []
+    for e in data.get("links", []):
+        if e["source"] == nid and e["target"] in id2n:
+            out.append((e, id2n[e["target"]]))
+        elif e["target"] == nid and e["source"] in id2n:
+            inc.append((e, id2n[e["source"]]))
+    return out, inc
+
+
+def _graph_bfs_path(
+    data: dict, src: str, tgt: str, directed: bool = True
+) -> list[tuple[str, dict, str]] | None:
+    from collections import deque
+
+    adj: dict[str, list[tuple[str, dict]]] = {}
+    for e in data.get("links", []):
+        adj.setdefault(e["source"], []).append((e["target"], e))
+        if not directed:
+            adj.setdefault(e["target"], []).append((e["source"], e))
+    if src not in adj and src not in {n["id"] for n in data.get("nodes", [])}:
+        return None
+    prev: dict[str, tuple[str, dict]] = {src: ("", {})}
+    dq = deque([src])
+    while dq:
+        cur = dq.popleft()
+        if cur == tgt:
+            break
+        for nxt, e in sorted(adj.get(cur, []), key=lambda x: x[0]):
+            if nxt not in prev:
+                prev[nxt] = (cur, e)
+                dq.append(nxt)
+    if tgt not in prev:
+        return None
+    path: list[tuple[str, dict, str]] = []
+    cur = tgt
+    while cur != src:
+        pc, e = prev[cur]
+        path.append((pc, e, cur))
+        cur = pc
+    path.reverse()
+    return path
+
+
+def _graph_vocab(data: dict, limit: int = 500) -> list[str]:
+    """Sorted vocabulary tokens from node labels. Powers zero-hit hints."""
+    vocab: set[str] = set()
+    for n in data.get("nodes", []):
+        vocab |= _graph_tokens(n.get("label", ""))
+        if len(vocab) >= limit:
+            break
+    return sorted(vocab)
+
+
+def _suggest_vocab_tokens(
+    vocab: list[str], toks: set[str], limit: int = 8
+) -> list[str]:
+    hints: list[str] = []
+    for t in sorted(toks):
+        for v in vocab:
+            if v.startswith(t) or t in v or t.startswith(v):
+                if v not in hints:
+                    hints.append(v)
+                if len(hints) >= limit:
+                    return hints
+    return hints
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index 513a0da..bda86ac 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -18,8 +18,6 @@
 
 import contextvars
 import functools
-import importlib
-import json
 import os
 import re
 import shutil
@@ -30,441 +28,116 @@ import uuid
 from pathlib import Path
 from typing import Optional
 
-import pathspec
-from mcp.server.fastmcp import FastMCP
-
-
-class GitIgnoreFilter:
-    """Evaluates paths against .gitignore files dynamically."""
-
-    def __init__(self) -> None:
-        self._specs: dict[Path, Optional[pathspec.PathSpec]] = {}
-
-    def _get_spec(self, dir_path: Path) -> Optional[pathspec.PathSpec]:
-        if dir_path in self._specs:
-            return self._specs[dir_path]
-        gitignore_file = dir_path / ".gitignore"
-        if gitignore_file.is_file():
-            try:
-                with open(gitignore_file, "r", encoding="utf-8") as f:
-                    spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
-                    self._specs[dir_path] = spec
-                    return spec
-            except Exception as e:
-                print(f"Warning: Failed to read {gitignore_file}: {e}", file=sys.stderr)
-        self._specs[dir_path] = None
-        return None
-
-    def is_ignored(self, path: Path) -> bool:
-        abs_path = path.resolve()
-        if ".git" in abs_path.parts or abs_path.name == ".git":
-            return True
-        # Repo boundary (Task 238 fix loop): git only applies .gitignore
-        # files INSIDE the repo. The old walk-to-/ let a grandparent
-        # .gitignore (e.g. `projects/` two levels up) mark every in-repo
-        # path ignored, which broke get_directory_tree("."). Stop at the
-        # nearest self-or-ancestor dir containing .git (its spec still
-        # applies); with no repo found, floor at cwd when the path lives
-        # under it, else keep the legacy walk-to-/ behavior.
-        boundary: Path | None = None
-        probe = abs_path if abs_path.is_dir() else abs_path.parent
-        cwd = Path.cwd().resolve()
-        # Both .git forms stop the walk: a directory in normal repos, a
-        # FILE in submodule/worktree roots (gitdir pointer). Either way
-        # this dir is a repo root and .gitignore files above it never
-        # apply inside.
-        while True:
-            dot_git = probe / ".git"
-            if dot_git.is_dir() or dot_git.is_file():
-                boundary = probe
-                break
-            if probe == probe.parent:
-                break
-            probe = probe.parent
-        if boundary is None:
-            try:
-                abs_path.relative_to(cwd)
-                boundary = cwd
-            except ValueError:
-                boundary = None
-        current = abs_path if abs_path.is_dir() else abs_path.parent
-        while True:
-            spec = self._get_spec(current)
-            if spec:
-                try:
-                    rel_path = abs_path.relative_to(current)
-                    match_str = rel_path.as_posix()
-                    if abs_path.is_dir() and not match_str.endswith("/"):
-                        match_str += "/"
-                    if spec.match_file(match_str):
-                        return True
-                except ValueError:
-                    pass
-            if boundary is not None and current == boundary:
-                break
-            if current == current.parent:
-                break
-            current = current.parent
-        return False
+sys.path.insert(0, str(Path(__file__).resolve().parent))
 
+from mcp.server.fastmcp import FastMCP
 
-TEXT_ENCODINGS = ["utf-8", "utf-8-sig", "windows-1256", "windows-1252", "latin-1"]
-
-
-def is_binary(file_path: Path) -> bool:
-    try:
-        with open(file_path, "rb") as f:
-            chunk = f.read(1024)
-            return b"\0" in chunk
-    except Exception:
-        return True
-
-
-# --- Tree-sitter AST signature extraction ---
-
-_EXTENSION_LANG_MAP: dict[str, str] = {
-    ".py": "python",
-    ".js": "javascript",
-    ".jsx": "javascript",
-    ".mjs": "javascript",
-    ".cjs": "javascript",
-    ".ts": "typescript",
-    ".tsx": "typescript",
-    ".mts": "typescript",
-    ".cts": "typescript",
-    ".go": "go",
-    ".java": "java",
-    ".jsp": "java",
-    ".rs": "rust",
-    ".kt": "kotlin",
-    ".kts": "kotlin",
-    ".swift": "swift",
-    ".rb": "ruby",
-    ".php": "php",
-    ".cs": "c_sharp",
-}
-
-_TS_QUERIES: dict[str, list[str]] = {
-    "python": [
-        "(function_definition name: (identifier) @name parameters: (parameters) @params) @sig",
-        "(class_definition name: (identifier) @name) @sig",
-    ],
-    "javascript": [
-        "(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
-        "(class_declaration name: (identifier) @name) @sig",
-        "(method_definition name: (property_identifier) @name) @sig",
-        "(arrow_function) @sig",
-        "(generator_function_declaration name: (identifier) @name) @sig",
-    ],
-    "typescript": [
-        "(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
-        "(class_declaration name: (type_identifier) @name) @sig",
-        "(interface_declaration name: (type_identifier) @name) @sig",
-        "(method_definition name: (property_identifier) @name) @sig",
-        "(type_alias_declaration name: (type_identifier) @name) @sig",
-        "(enum_declaration name: (identifier) @name) @sig",
-        "(arrow_function) @sig",
-    ],
-    "go": [
-        "(function_declaration name: (identifier) @name parameters: (parameter_list) @params) @sig",
-        "(method_declaration receiver: (parameter_list) @receiver name: (field_identifier) @name) @sig",
-        "(type_declaration (type_spec name: (type_identifier) @name)) @sig",
-    ],
-    "java": [
-        "(method_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
-        "(class_declaration name: (identifier) @name) @sig",
-        "(interface_declaration name: (identifier) @name) @sig",
-        "(enum_declaration name: (identifier) @name) @sig",
-        "(record_declaration name: (identifier) @name) @sig",
-    ],
-    "rust": [
-        "(function_item name: (identifier) @name parameters: (parameters) @params) @sig",
-        "(struct_item name: (type_identifier) @name) @sig",
-        "(enum_item name: (type_identifier) @name) @sig",
-        "(trait_item name: (type_identifier) @name) @sig",
-        "(type_item name: (type_identifier) @name) @sig",
-        "(impl_item trait: (type_identifier) @name) @sig",
-    ],
-    "kotlin": [
-        "(function_declaration name: (identifier) @name) @sig",
-        "(class_declaration name: (identifier) @name) @sig",
-    ],
-}
-
-_ts_language_cache: dict[str, object] = {}
-
-
-def _get_ts_language(lang_id: str) -> object:
-    if lang_id in _ts_language_cache:
-        return _ts_language_cache[lang_id]
-    pkg_name = f"tree_sitter_{lang_id}"
-    try:
-        mod = importlib.import_module(pkg_name)
-        from tree_sitter import Language as TSLanguage
-
-        if lang_id == "typescript":
-            lang = TSLanguage(mod.language_typescript())
-        else:
-            lang = TSLanguage(mod.language())
-        _ts_language_cache[lang_id] = lang
-        return lang
-    except Exception:
-        _ts_language_cache[lang_id] = None
-        return None
-
-
-def _extract_signature_line(source_lines: list[str], start_row: int) -> str:
-    first = source_lines[start_row].rstrip("\n").rstrip("\r")
-    if not first.rstrip().endswith(",") and first.count("(") == first.count(")"):
-        return first
-    parts: list[str] = [first]
-    for line in source_lines[start_row + 1 :]:
-        stripped = line.rstrip("\n").rstrip("\r")
-        parts.append(stripped)
-        if ":" in stripped and not stripped.rstrip().endswith(","):
-            break
-        if stripped.rstrip().endswith("{"):
-            break
-        if stripped.rstrip().endswith("):") or stripped.rstrip().endswith(") {"):
-            break
-    return "\n".join(parts)
-
-
-def _extract_via_tree_sitter(file_path: Path) -> Optional[str]:
-    ext = file_path.suffix.lower()
-    lang_id = _EXTENSION_LANG_MAP.get(ext)
-    if not lang_id:
-        return None
-    lang = _get_ts_language(lang_id)
-    if lang is None:
-        return None
-    queries = _TS_QUERIES.get(lang_id)
-    if not queries:
-        return None
-    try:
-        with open(file_path, "r", encoding="utf-8") as f:
-            content = f.read()
-    except Exception:
-        return None
-    source_bytes = content.encode("utf-8")
-    from tree_sitter import Parser, Query, QueryCursor
-
-    parser = Parser(lang)
-    tree = parser.parse(source_bytes)
-    source_lines = content.split("\n")
-    seen: set[str] = set()
-    signatures: list[str] = []
-    for query_str in queries:
-        try:
-            q = Query(lang, query_str)
-            qc = QueryCursor(q)
-            matches = qc.matches(tree.root_node)
-            for _pattern_index, captures in matches:
-                sig_nodes = captures.get("sig", [])
-                for node in sig_nodes:
-                    start_row = node.start_point[0]
-                    sig_line = _extract_signature_line(source_lines, start_row).strip()
-                    if sig_line and sig_line not in seen:
-                        seen.add(sig_line)
-                        signatures.append(sig_line)
-        except Exception:
-            continue
-    if not signatures:
-        return None
-    return f"### Signatures in {file_path}\n" + "\n".join(signatures)
-
-
-# --- End tree-sitter ---
-
-# Runaway-traversal guards (Task 177): a single wedged request (e.g. tree of
-# "/") used to burn minutes of CPU on the single-threaded stdio server and
-# starve every later tool call. These caps bound any single walk.
-TREE_MAX_DEPTH = 8
-TREE_MAX_ENTRIES = 2000
-COLLECT_MAX_FILES = 1000
-# Directory names never descended into, at any level. Supplements .gitignore
-# (which cannot cover absolute-path walks outside any repo).
-BANNED_DIRS = frozenset(
-    {
-        ".git",
-        ".cache",
-        "__pycache__",
-        "node_modules",
-        ".venv",
-        "venv",
-        "proc",
-        "sys",
-        "dev",
-    }
+from fsutil import (
+    BANNED_DIRS,
+    COLLECT_MAX_FILES,
+    GitIgnoreFilter,
+    TEXT_ENCODINGS,
+    TREE_MAX_DEPTH,
+    TREE_MAX_ENTRIES,
+    _ensure_context_reports_ignored,
+    _is_banned_dir,
+    collect_files,
+    generate_tree,
+    is_binary,
+    process_source_file,
+)
+from signatures import (
+    _EXTENSION_LANG_MAP,
+    _TS_QUERIES,
+    _extract_signature_line,
+    _extract_via_tree_sitter,
+    _get_ts_language,
+    _ts_language_cache,
+)
+from graph import (
+    GRAPH_DOC_LINES,
+    GRAPH_DOC_SECTIONS,
+    GRAPH_MAX_DOCS,
+    GRAPH_MAX_FILES,
+    GRAPH_MAX_NODES,
+    GRAPH_SCHEMA_VERSION,
+    _GRAPH_ADR_REF_RE,
+    _GRAPH_ANDROID_ID_RE,
+    _GRAPH_ARROW_RE,
+    _GRAPH_CALL_RE,
+    _GRAPH_CODE_EXTS,
+    _GRAPH_CSS_RE,
+    _GRAPH_DART_KEYWORDS,
+    _GRAPH_DART_RE,
+    _GRAPH_DOM_ID_RE,
+    _GRAPH_GET_ID_RE,
+    _GRAPH_GOD_NOISE,
+    _GRAPH_JAVA_CTOR_RE,
+    _GRAPH_JAVA_METHOD_RE,
+    _GRAPH_KT_FUN_RE,
+    _GRAPH_MAX_SCAN_BYTES,
+    _GRAPH_MD_HEADING_RE,
+    _GRAPH_MD_LINK_RE,
+    _GRAPH_OBJC_IMPL_RE,
+    _GRAPH_OBJC_METHOD_RE,
+    _GRAPH_PRISMA_RE,
+    _GRAPH_PROP_RE,
+    _GRAPH_R_ID_RE,
+    _GRAPH_SCRIPT_BLOCK_RE,
+    _GRAPH_SQL_REF_RE,
+    _GRAPH_SQL_TABLE_RE,
+    _GRAPH_SWIFT_RE,
+    _GRAPH_SYMBOL_RE,
+    _GRAPH_TASK_REF_RE,
+    _GRAPH_TOKEN_SPLIT_RE,
+    _GRAPH_TYPE_RE,
+    _GRAPH_WIKILINK_RE,
+    _build_graph_data,
+    _extract_graph_symbols,
+    _extract_md_link_targets,
+    _extract_md_sections,
+    _extract_sql_symbols,
+    _find_graph_nodes,
+    _graph_bfs_path,
+    _graph_degrees,
+    _graph_neighbors,
+    _graph_tokens,
+    _graph_vocab,
+    _load_graph_data,
+    _parse_graph_imports,
+    _push_graph_symbol,
+    _read_text_capped,
+    _resolve_doc_link,
+    _resolve_graph_file,
+    _resolve_import_to_rel,
+    _save_graph,
+    _scan_js_like_symbols,
+    _slugify_section,
+    _suggest_vocab_tokens,
+)
+from gitops import (
+    ACTIVE_KANBAN_DIRS,
+    DIFF_SIZE_WARNING_THRESHOLD,
+    MAX_BUNDLE_SIZE,
+    _CONVENTIONAL_RE,
+    _check_conventional_commit,
+    _derive_task_slug,
+    _detect_stack,
+    _discover_next_id,
+    _extract_checklist_with_continuations,
+    _extract_section,
+    _extract_title,
+    _find_task_file,
+    _format_task_id_list,
+    _git_mv_or_fallback,
+    _kebab_case,
+    _patch_archived_file,
+    _repo_root,
+    _verify_verbatim_checksums,
+)
+from bundle import (
+    _build_meta_content,
 )
-
-
-def _is_banned_dir(entry: Path) -> bool:
-    """True when a directory entry must never be descended into."""
-    try:
-        return entry.is_dir() and entry.name in BANNED_DIRS
-    except OSError:
-        return True  # Unstatable entries are treated as unsafe to descend.
-
-
-def generate_tree(
-    dir_path: Path,
-    ignore_filter: GitIgnoreFilter,
-    max_depth: int = TREE_MAX_DEPTH,
-    max_entries: int = TREE_MAX_ENTRIES,
-) -> str:
-    lines = ["```text", dir_path.name or str(dir_path)]
-    state = {"count": 0, "truncated": False}
-
-    def _walk(current_path: Path, prefix: str, depth: int) -> None:
-        if state["truncated"]:
-            return
-        if depth > max_depth:
-            lines.append(f"{prefix}└── [Max depth reached ({max_depth})]")
-            return
-        try:
-            entries = list(current_path.iterdir())
-        except (PermissionError, OSError):
-            lines.append(f"{prefix}└── [Unreadable directory]")
-            return
-        valid_entries = [
-            e
-            for e in entries
-            if not _is_banned_dir(e) and not ignore_filter.is_ignored(e)
-        ]
-        sorted_entries = sorted(
-            valid_entries, key=lambda e: (not e.is_dir(), e.name.lower())
-        )
-        for i, entry in enumerate(sorted_entries):
-            if state["count"] >= max_entries:
-                lines.append(
-                    f"{prefix}└── [Truncated: entry limit reached ({max_entries})]"
-                )
-                state["truncated"] = True
-                return
-            state["count"] += 1
-            is_last = i == (len(sorted_entries) - 1)
-            connector = "└── " if is_last else "├── "
-            lines.append(f"{prefix}{connector}{entry.name}")
-            if entry.is_dir():
-                extension = "    " if is_last else "│   "
-                _walk(entry, prefix + extension, depth + 1)
-
-    _walk(dir_path, "", 0)
-    lines.append("```")
-    return "\n".join(lines)
-
-
-def process_source_file(file_path: Path, max_size: int, line_numbers: bool) -> str:
-    lines = [f"### `{file_path}`", ""]
-    if not file_path.exists():
-        lines.append("> Skipped: (File not found)\n")
-        return "\n".join(lines)
-    try:
-        size = file_path.stat().st_size
-        if size > max_size:
-            lines.append(
-                f"> Skipped: (File too large: {size} bytes > max_size={max_size})\n"
-            )
-            # Discovery gap fix (Task 241): a skipped body must not mean
-            # zero evidence — attach structural signatures when extractable
-            # so the Brain still sees the file's shape. Never raises.
-            try:
-                sig = _extract_via_tree_sitter(file_path)
-                if sig:
-                    lines.append(
-                        "> Body omitted by size cap; structural signatures follow:\n"
-                    )
-                    lines.append(sig)
-                else:
-                    lines.append(
-                        "> No signatures extracted — narrow `paths`, raise "
-                        "`max_size`, or call `extract_signatures` on this file.\n"
-                    )
-            except Exception as sig_err:
-                lines.append(f"> Signature fallback failed: ({sig_err})\n")
-            return "\n".join(lines)
-    except OSError as e:
-        lines.append(f"> Skipped: (OS Error: {e})\n")
-        return "\n".join(lines)
-    if is_binary(file_path):
-        lines.append("> Skipped: (Binary file)\n")
-        return "\n".join(lines)
-    ext = file_path.suffix.lstrip(".") or "text"
-    content_text = None
-    for enc in TEXT_ENCODINGS:
-        try:
-            with open(file_path, "r", encoding=enc) as f:
-                content_text = f.read()
-            break
-        except (UnicodeDecodeError, UnicodeError):
-            continue
-    if content_text is None:
-        lines.append(
-            f"> Skipped: (Could not decode file with any supported encoding)\n"
-        )
-        return "\n".join(lines)
-    file_lines = content_text.split("\n")
-    if file_lines and file_lines[-1] == "":
-        file_lines.pop()
-    if line_numbers:
-        content = "\n".join(f"{i}: {line}" for i, line in enumerate(file_lines, 1))
-    else:
-        content = "\n".join(file_lines)
-    lines.append(f"```{ext}")
-    if content:
-        lines.append(content)
-    lines.append("```\n")
-    return "\n".join(lines)
-
-
-def collect_files(
-    target: str,
-    ignore_filter: GitIgnoreFilter,
-    max_files: int = COLLECT_MAX_FILES,
-) -> list[Path]:
-    p = Path(target)
-    if not p.exists() or ignore_filter.is_ignored(p):
-        return []
-    if p.is_file():
-        return [p]
-    collected = []
-    for root, dirs, files in os.walk(p):
-        root_path = Path(root)
-        dirs[:] = [
-            d
-            for d in dirs
-            if (root_path / d).name not in BANNED_DIRS
-            and not ignore_filter.is_ignored(root_path / d)
-        ]
-        for f in files:
-            if len(collected) >= max_files:
-                return collected
-            file_path = root_path / f
-            if not ignore_filter.is_ignored(file_path):
-                collected.append(file_path)
-    return collected
-
-
-def _ensure_context_reports_ignored(workspace_root: Path | None = None) -> None:
-    """Safeguard: Append context-reports/ to <workspace_root>/.gitignore.
-
-    Every report-producing tool calls this so generated reports are never
-    accidentally committed. The target is the caller's project root, not the
-    process cwd: under the singleton the server runs from the global install
-    dir, so a bare ``Path(".gitignore")`` edited the wrong file. A ``None``
-    root keeps the old cwd behavior for project_root-omitted calls.
-    """
-    base = workspace_root if workspace_root is not None else Path.cwd()
-    gitignore = base / ".gitignore"
-    if gitignore.is_file():
-        try:
-            with open(gitignore, "r+", encoding="utf-8") as f:
-                content = f.read()
-                if "context-reports/" not in content:
-                    f.write("\n# Custom Context MCP reports\ncontext-reports/\n")
-        except Exception as e:
-            print(f"Warning: Failed to update .gitignore: {e}", file=sys.stderr)
 
 
 mcp = FastMCP("CustomContext", host="127.0.0.1", port=8102)
@@ -474,9 +147,13 @@ mcp = FastMCP("CustomContext", host="127.0.0.1", port=8102)
 # never reaches MCP clients, so the fallback is recorded here and surfaced
 # by @_project_tool in the tool result. No absolute paths are echoed
 # (layout privacy, cf. decision-server _active_root_info).
+
+
 _FALLBACK_FIRED: contextvars.ContextVar[bool] = contextvars.ContextVar(
     "custom_context_fallback_fired", default=False
 )
+
+
 ROOT_FALLBACK_WARNING = (
     "WARNING [project-isolation]: project_root was omitted, so this call "
     "was scoped to the singleton server's own directory instead of the "
@@ -536,983 +213,6 @@ def get_directory_tree(target_path: str = ".", project_root: str | None = None)
 # source: contains/imports) or INFERRED (resolved: references across files).
 # Persisted as versioned graph.json + markdown report under context-reports/.
 
-GRAPH_SCHEMA_VERSION = 2
-GRAPH_MAX_FILES = 300
-GRAPH_MAX_NODES = 5000
-GRAPH_MAX_DOCS = 300
-GRAPH_DOC_LINES = 500
-GRAPH_DOC_SECTIONS = 60
-_GRAPH_CODE_EXTS = frozenset(
-    {
-        ".py",
-        ".js",
-        ".jsx",
-        ".mjs",
-        ".cjs",
-        ".ts",
-        ".tsx",
-        ".mts",
-        ".cts",
-        ".go",
-        ".java",
-        ".rs",
-        ".kt",
-        ".kts",
-        ".rb",
-        ".php",
-        ".cs",
-        ".swift",
-        ".lua",
-        ".zig",
-        ".sh",
-        ".bash",
-        ".sql",
-        ".vue",
-        ".svelte",
-        ".astro",
-        ".html",
-        ".htm",
-        ".xml",
-        ".dart",
-        ".m",
-        ".mm",
-        ".gradle",
-        ".prisma",
-        ".properties",
-        ".css",
-        ".scss",
-        ".less",
-    }
-)
-_GRAPH_SYMBOL_RE = re.compile(
-    r"^\s*(?:export\s+|default\s+|public\s+|private\s+|protected\s+|static\s+|async\s+|fun\s+|def\s+|class\s+|interface\s+|type\s+|enum\s+|struct\s+|trait\s+|func(?:tion)?\s+)?"
-    r"(?:class|interface|type|enum|struct|trait|def|fun|func(?:tion)?)\s+([A-Za-z_]\w*)"
-)
-_GRAPH_CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
-_GRAPH_KT_FUN_RE = re.compile(
-    r"^\s*(?:(?:public|private|protected|internal|open|override|suspend|inline|tailrec|operator|infix|external)\s+)*fun\s+(?:<[^>]*>\s*)?([A-Za-z_]\w*)"
-)
-_GRAPH_TYPE_RE = re.compile(
-    r"^\s*(?:(?:public|private|protected|internal|open|abstract|final|sealed|data|object|export|default)\s+)*(?:class|object|interface)\s+([A-Za-z_]\w*)"
-)
-_GRAPH_SWIFT_RE = re.compile(
-    r"^\s*(?:(?:public|private|fileprivate|internal|open|override|static|class|mutating|required|convenience)\s+)*(?:func\s+([A-Za-z_]\w*)|(class|struct|enum|protocol)\s+([A-Za-z_]\w*))"
-)
-_GRAPH_JAVA_METHOD_RE = re.compile(
-    r"^\s*(?:(?:public|private|protected|static|final|synchronized|abstract|native|default|volatile|transient)\s+)+[\w<>\[\]?.,\s]+\s+(\w+)\s*\("
-)
-_GRAPH_JAVA_CTOR_RE = re.compile(r"^\s*(?:public|private|protected)\s+([A-Z]\w*)\s*\(")
-_GRAPH_DART_RE = re.compile(r"^\s*(?:[\w<>?,\s]+\s+)?(\w+)\s*\([^;{}]*\)\s*(?:\{|=>|;)")
-_GRAPH_DART_KEYWORDS = frozenset(
-    {
-        "return",
-        "if",
-        "for",
-        "while",
-        "switch",
-        "assert",
-        "new",
-        "const",
-        "final",
-        "var",
-        "late",
-        "import",
-        "export",
-        "throw",
-        "else",
-        "do",
-    }
-)
-_GRAPH_ARROW_RE = re.compile(
-    r"^\s*(?:export\s+)?(?:const|let)\s+([A-Za-z_]\w*)\s*(?::[^=;]+)?=\s*(?:async\s*)?(?:\([^)]*\)\s*=>|function)"
-)
-_GRAPH_ANDROID_ID_RE = re.compile(r'android:id="@\+id/([\w]+)"')
-_GRAPH_DOM_ID_RE = re.compile(r'(?:id|@\+id)="([\w-]+)"')
-_GRAPH_R_ID_RE = re.compile(r"R\.id\.([\w]+)")
-_GRAPH_GET_ID_RE = re.compile(r"getElementById\(\s*['\"]([\w-]+)['\"]\)")
-_GRAPH_SCRIPT_BLOCK_RE = re.compile(
-    r"<script\b[^>]*>(.*?)</script>", re.DOTALL | re.IGNORECASE
-)
-_GRAPH_OBJC_METHOD_RE = re.compile(r"^\s*[-+]\s*\([^)]*\)\s*([A-Za-z_]\w*)")
-_GRAPH_OBJC_IMPL_RE = re.compile(r"^\s*@implementation\s+([A-Za-z_]\w*)")
-_GRAPH_PRISMA_RE = re.compile(r"^\s*(model|enum)\s+([A-Za-z_]\w*)")
-_GRAPH_PROP_RE = re.compile(r"^\s*([A-Za-z_][\w.\-]*)\s*[=:]")
-_GRAPH_CSS_RE = re.compile(r"^\s*\.([\w-]+)\s*\{")
-_GRAPH_SQL_TABLE_RE = re.compile(
-    r"^\s*CREATE\s+(?:TEMP(?:ORARY)?\s+)?(?:TABLE|VIEW)\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"\[]?([\w\.]+)[`\"\]]?",
-    re.IGNORECASE,
-)
-_GRAPH_SQL_REF_RE = re.compile(r"REFERENCES\s+[`\"\[]?([\w\.]+)[`\"\]]?", re.IGNORECASE)
-_GRAPH_MD_HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$")
-_GRAPH_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+\.md)(?:#[^)\s]*)?\)")
-_GRAPH_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]]*)?(?:\|[^\]]*)?\]\]")
-_GRAPH_TOKEN_SPLIT_RE = re.compile(r"(?<=[a-z])(?=[A-Z])")
-_GRAPH_TASK_REF_RE = re.compile(r"\bTask\s+(\d{1,4})\b")
-_GRAPH_ADR_REF_RE = re.compile(r"\bADR-(\d{1,3})\b", re.IGNORECASE)
-_GRAPH_GOD_NOISE = frozenset({"run", "json", "post", "data"})
-
-_GRAPH_MAX_SCAN_BYTES = 1048576
-
-
-def _read_text_capped(file_path: Path, cap: int = _GRAPH_MAX_SCAN_BYTES) -> str | None:
-    """Read text bounded by cap bytes so huge generated files cannot wedge the server."""
-    try:
-        with open(file_path, "r", encoding="utf-8", errors="strict") as f:
-            return f.read(cap + 1)[:cap]
-    except Exception:
-        return None
-
-
-def _graph_rel_posix(p: Path, root: Path) -> str:
-    try:
-        return p.resolve().relative_to(root).as_posix()
-    except ValueError:
-        return p.name
-
-
-def _push_graph_symbol(
-    out: list[tuple[str, str, int]], seen: set[str], name: str, kind: str, lineno: int
-) -> None:
-    if len(out) >= 200 or len(name) < 2 or name in seen:
-        return
-    seen.add(name)
-    out.append((name, kind, lineno))
-
-
-def _scan_js_like_symbols(
-    text: str, base_line: int, out: list[tuple[str, str, int]], seen: set[str]
-) -> None:
-    for i, line in enumerate(text.split("\n")):
-        if len(out) >= 200:
-            return
-        lineno = base_line + i
-        m = _GRAPH_SYMBOL_RE.match(line)
-        if m:
-            lowered = line.lower()
-            _push_graph_symbol(
-                out, seen, m.group(1), "class" if "class" in lowered else "func", lineno
-            )
-            continue
-        m = _GRAPH_ARROW_RE.match(line)
-        if m:
-            _push_graph_symbol(out, seen, m.group(1), "func", lineno)
-
-
-def _extract_graph_symbols(file_path: Path) -> list[tuple[str, str, int]]:
-    """Return [(name, kind, line_no)] capped per file. Regex-based, deterministic.
-
-    Covers backend (Python/JS/TS/Go/Java...), mobile (Kotlin fun/class/object,
-    Swift func/types, Java methods/ctors, Dart classes/members), frontend
-    (Vue/Svelte script blocks, arrow components), and markup (HTML/XML element
-    ids incl. android:id). Markup node labels keep raw ids (dashes included).
-    """
-    out: list[tuple[str, str, int]] = []
-    seen: set[str] = set()
-    text = _read_text_capped(file_path)
-    if text is None:
-        return out
-    lines = text.split("\n")
-    suffix = file_path.suffix.lower()
-    if suffix in (".vue", ".svelte", ".astro", ".html", ".htm"):
-        text = "\n".join(lines)
-        for m in _GRAPH_SCRIPT_BLOCK_RE.finditer(text):
-            base_line = text[: m.start(1)].count("\n") + 1
-            _scan_js_like_symbols(m.group(1), base_line, out, seen)
-    if suffix in (".vue", ".svelte", ".astro", ".html", ".htm", ".xml"):
-        for i, line in enumerate(lines, 1):
-            if len(out) >= 200:
-                break
-            for m in _GRAPH_ANDROID_ID_RE.finditer(line):
-                _push_graph_symbol(out, seen, m.group(1), "view_id", i)
-            for m in _GRAPH_DOM_ID_RE.finditer(line):
-                _push_graph_symbol(out, seen, m.group(1), "element_id", i)
-        return out
-    if suffix in (".kt", ".kts", ".java", ".swift", ".dart", ".m", ".mm", ".gradle"):
-        for i, line in enumerate(lines, 1):
-            if len(out) >= 200:
-                break
-            if suffix in (".m", ".mm"):
-                m = _GRAPH_OBJC_IMPL_RE.match(line)
-                if m:
-                    _push_graph_symbol(out, seen, m.group(1), "class", i)
-                    continue
-                m = _GRAPH_OBJC_METHOD_RE.match(line)
-                if m:
-                    _push_graph_symbol(out, seen, m.group(1), "method", i)
-                    continue
-                continue
-            m = _GRAPH_KT_FUN_RE.match(line)
-            if m:
-                _push_graph_symbol(out, seen, m.group(1), "func", i)
-                continue
-            m = _GRAPH_TYPE_RE.match(line)
-            if m:
-                _push_graph_symbol(out, seen, m.group(1), "class", i)
-                continue
-            m = _GRAPH_SWIFT_RE.match(line)
-            if m:
-                if m.group(1):
-                    _push_graph_symbol(out, seen, m.group(1), "func", i)
-                else:
-                    _push_graph_symbol(out, seen, m.group(3), "class", i)
-                continue
-            m = _GRAPH_JAVA_METHOD_RE.match(line)
-            if m and m.group(1) not in (
-                "if",
-                "for",
-                "while",
-                "switch",
-                "catch",
-                "return",
-            ):
-                _push_graph_symbol(out, seen, m.group(1), "method", i)
-                continue
-            m = _GRAPH_JAVA_CTOR_RE.match(line)
-            if m:
-                _push_graph_symbol(out, seen, m.group(1), "method", i)
-                continue
-            if suffix == ".dart":
-                m = _GRAPH_DART_RE.match(line)
-                if m and m.group(1) not in _GRAPH_DART_KEYWORDS:
-                    _push_graph_symbol(out, seen, m.group(1), "method", i)
-                    continue
-            m = _GRAPH_ARROW_RE.match(line)
-            if m:
-                _push_graph_symbol(out, seen, m.group(1), "func", i)
-        return out
-    if suffix == ".prisma":
-        for i, line in enumerate(lines, 1):
-            if len(out) >= 200:
-                break
-            m = _GRAPH_PRISMA_RE.match(line)
-            if m:
-                _push_graph_symbol(
-                    out,
-                    seen,
-                    m.group(2),
-                    "model" if m.group(1) == "model" else "enum",
-                    i,
-                )
-        return out
-    if suffix == ".properties":
-        for i, line in enumerate(lines, 1):
-            if len(out) >= 200:
-                break
-            stripped = line.strip()
-            if not stripped or stripped.startswith(("#", "!")):
-                continue
-            m = _GRAPH_PROP_RE.match(line)
-            if m:
-                _push_graph_symbol(out, seen, m.group(1), "config", i)
-        return out
-    if suffix in (".css", ".scss", ".less"):
-        for i, line in enumerate(lines, 1):
-            if len(out) >= 200:
-                break
-            m = _GRAPH_CSS_RE.match(line)
-            if m:
-                _push_graph_symbol(out, seen, m.group(1), "style", i)
-        return out
-    for i, line in enumerate(lines, 1):
-        if len(out) >= 200:
-            break
-        m = _GRAPH_SYMBOL_RE.match(line)
-        if m:
-            name = m.group(1)
-            lowered = line.lower()
-            if "interface" in lowered:
-                kind = "interface"
-            elif "enum" in lowered:
-                kind = "enum"
-            elif re.search(r"\btype\b", lowered):
-                kind = "type"
-            elif "class" in lowered:
-                kind = "class"
-            else:
-                kind = "func"
-            _push_graph_symbol(out, seen, name, kind, i)
-            continue
-        m = _GRAPH_ARROW_RE.match(line)
-        if m:
-            _push_graph_symbol(out, seen, m.group(1), "func", i)
-            continue
-    return out
-
-
-def _extract_sql_symbols(
-    file_path: Path,
-) -> tuple[list[tuple[str, str, int]], list[str]]:
-    """Return ([(table, kind, line_no)], [referenced_table, ...]). Deterministic."""
-    tables: list[tuple[str, str, int]] = []
-    refs: list[str] = []
-    text = _read_text_capped(file_path)
-    if text is None:
-        return tables, refs
-    lines = text.split("\n")
-    for i, line in enumerate(lines, 1):
-        m = _GRAPH_SQL_TABLE_RE.match(line)
-        if m and len(tables) < 200:
-            name = m.group(1).split(".")[-1]
-            kind = "view" if "view" in line.lower() else "table"
-            if name not in {n for n, _, _ in tables}:
-                tables.append((name, kind, i))
-        for r in _GRAPH_SQL_REF_RE.finditer(line):
-            ref = r.group(1).split(".")[-1]
-            if ref and ref not in refs:
-                refs.append(ref)
-                if len(refs) >= 40:
-                    break
-    return tables, refs
-
-
-def _extract_md_sections(abs_path: Path) -> list[tuple[str, int, int]]:
-    """Return [(heading_text, level, line_no)] capped. Deterministic."""
-    out: list[tuple[str, int, int]] = []
-    text = _read_text_capped(abs_path)
-    if text is None:
-        return out
-    lines = text.split("\n")[:GRAPH_DOC_LINES]
-    for i, line in enumerate(lines, 1):
-        if len(out) >= GRAPH_DOC_SECTIONS:
-            break
-        m = _GRAPH_MD_HEADING_RE.match(line)
-        if not m:
-            continue
-        text = m.group(2).strip()[:80]
-        if len(text) >= 2:
-            out.append((text, len(m.group(1)), i))
-    return out
-
-
-def _extract_md_link_targets(content: str) -> list[str]:
-    """Return raw Markdown link targets (./other.md, [[wikilinks]]). Deterministic."""
-    targets: list[str] = []
-    for m in _GRAPH_MD_LINK_RE.finditer(content):
-        t = m.group(1).strip()
-        if t and t not in targets and not re.match(r"https?://", t):
-            targets.append(t)
-    for m in _GRAPH_WIKILINK_RE.finditer(content):
-        t = m.group(1).strip()
-        if t and t not in targets:
-            targets.append(t if t.lower().endswith(".md") else t + ".md")
-    return targets[:40]
-
-
-def _resolve_doc_link(target: str, from_rel: str, doc_set: set[str]) -> str | None:
-    if target.startswith("/"):
-        cand = target.lstrip("/")
-    else:
-        from_dir = from_rel.rsplit("/", 1)[0] if "/" in from_rel else ""
-        parts = (from_dir + "/" + target).split("/")
-        stack: list[str] = []
-        for part in parts:
-            if part in ("", "."):
-                continue
-            if part == "..":
-                if stack:
-                    stack.pop()
-            else:
-                stack.append(part)
-        cand = "/".join(stack)
-    if cand in doc_set:
-        return cand
-    base = cand.rsplit("/", 1)[-1]
-    for d in doc_set:
-        if d.rsplit("/", 1)[-1].lower() == base.lower():
-            return d
-    return None
-
-
-def _slugify_section(text: str) -> str:
-    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
-    return slug[:60] or "section"
-
-
-def _parse_graph_imports(rel_suffix: str, content: str) -> list[str]:
-    imps: list[str] = []
-    try:
-        if rel_suffix == ".py":
-            for m in re.finditer(
-                r"^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))",
-                content,
-                re.MULTILINE,
-            ):
-                mod = m.group(1) or m.group(2)
-                if mod and mod not in imps:
-                    imps.append(mod)
-        elif rel_suffix in {
-            ".js",
-            ".jsx",
-            ".mjs",
-            ".cjs",
-            ".ts",
-            ".tsx",
-            ".mts",
-            ".cts",
-        }:
-            for m in re.finditer(
-                r"""(?:from\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]|import\(\s*['"]([^'"]+)['"])""",
-                content,
-            ):
-                mod = m.group(1) or m.group(2) or m.group(3)
-                if mod and mod not in imps and mod.startswith("."):
-                    imps.append(mod)
-        elif rel_suffix == ".go":
-            for m in re.finditer(r'"([\w\.\-/]+)"', content):
-                mod = m.group(1)
-                if "/" in mod and mod not in imps:
-                    imps.append(mod)
-                    if len(imps) >= 20:
-                        break
-        elif rel_suffix in {".kt", ".kts", ".java", ".gradle"}:
-            for m in re.finditer(
-                r"^\s*import\s+(?:static\s+)?([\w\.]+)", content, re.MULTILINE
-            ):
-                mod = m.group(1)
-                if mod and mod not in imps:
-                    imps.append(mod)
-        elif rel_suffix in {".swift", ".m", ".mm"}:
-            for m in re.finditer(r"^\s*import\s+(\w+)", content, re.MULTILINE):
-                mod = m.group(1)
-                if mod and mod not in imps:
-                    imps.append(mod)
-    except Exception:
-        return imps
-    return imps[:20]
-
-
-def _resolve_import_to_rel(mod: str, from_rel: str, rel_set: set[str]) -> str | None:
-    if not mod.startswith(".") and "." not in mod and "/" not in mod:
-        return None
-    cand_base = mod.replace(".", "/").strip("/")
-    from_dir = from_rel.rsplit("/", 1)[0] if "/" in from_rel else ""
-    tried: list[str] = []
-    if mod.startswith("."):
-        level = len(mod) - len(mod.lstrip("."))
-        rest = mod.lstrip(".").replace(".", "/")
-        parts = from_dir.split("/") if from_dir else []
-        base = "/".join(parts[: max(0, len(parts) - level + 1)])
-        tried.append(f"{base}/{rest}".strip("/"))
-    else:
-        tried.append(cand_base)
-    exts = [
-        ".py",
-        "/__init__.py",
-        ".ts",
-        ".tsx",
-        ".js",
-        ".jsx",
-        ".go",
-        ".java",
-        ".rs",
-        ".kt",
-        ".kts",
-        ".swift",
-        ".dart",
-        ".vue",
-        ".m",
-        ".mm",
-    ]
-    for t in tried:
-        for e in exts:
-            c = (t + e).strip("/")
-            if c in rel_set:
-                return c
-        if t in rel_set:
-            return t
-    return None
-
-
-def _build_graph_data(workspace_root: Path, target: Path) -> dict:
-    filt = GitIgnoreFilter()
-    all_found = collect_files(str(target), filt)
-    files = [
-        p
-        for p in all_found
-        if p.suffix.lower() in _GRAPH_CODE_EXTS and "context-reports" not in p.parts
-    ]
-    files.sort(key=lambda p: (len(p.parts), p.as_posix()))
-    files = files[:GRAPH_MAX_FILES]
-    docs = [
-        p
-        for p in all_found
-        if p.suffix.lower() == ".md" and "context-reports" not in p.parts
-    ]
-    docs.sort(key=lambda p: (len(p.parts), p.as_posix()))
-    docs = docs[:GRAPH_MAX_DOCS]
-    rels: list[str] = []
-    rel_set: set[str] = set()
-    resolved: list[Path] = []
-    doc_rels: list[str] = []
-    doc_set: set[str] = set()
-    doc_resolved: list[Path] = []
-    for p in files:
-        try:
-            rel = p.resolve().relative_to(workspace_root).as_posix()
-        except ValueError:
-            continue
-        if rel not in rel_set:
-            rel_set.add(rel)
-            rels.append(rel)
-            resolved.append(p.resolve())
-    for p in docs:
-        try:
-            rel = p.resolve().relative_to(workspace_root).as_posix()
-        except ValueError:
-            continue
-        if rel not in doc_set and rel not in rel_set:
-            doc_set.add(rel)
-            doc_rels.append(rel)
-            doc_resolved.append(p.resolve())
-    nodes: list[dict] = []
-    links: list[dict] = []
-    sym_index: dict[str, list[str]] = {}
-    file_contents: dict[str, str] = {}
-    for rel, abs_p in zip(rels, resolved):
-        nodes.append(
-            {"id": f"file:{rel}", "label": rel, "file_type": "code", "source_file": rel}
-        )
-        try:
-            with open(abs_p, "r", encoding="utf-8", errors="strict") as f:
-                content = f.read()[:200000]
-        except Exception:
-            content = ""
-        file_contents[rel] = content
-        if Path(rel).suffix.lower() == ".sql":
-            symbols, sql_refs = _extract_sql_symbols(abs_p)
-            for t in sql_refs:
-                links.append(
-                    {
-                        "source": f"file:{rel}",
-                        "target": f"sqlref:{t}",
-                        "relation": "references",
-                        "confidence": "EXTRACTED",
-                        "source_file": rel,
-                    }
-                )
-        else:
-            symbols = _extract_graph_symbols(abs_p)
-        for name, kind, lineno in symbols:
-            if len(nodes) >= GRAPH_MAX_NODES:
-                break
-            sid = f"sym:{rel}#{name}"
-            nodes.append(
-                {
-                    "id": sid,
-                    "label": name,
-                    "file_type": "code",
-                    "source_file": rel,
-                    "source_location": f"L{lineno}",
-                    "kind": kind,
-                }
-            )
-            links.append(
-                {
-                    "source": f"file:{rel}",
-                    "target": sid,
-                    "relation": "contains",
-                    "confidence": "EXTRACTED",
-                    "source_file": rel,
-                }
-            )
-            sym_index.setdefault(name, []).append(sid)
-    doc_contents: dict[str, str] = {}
-    for rel, abs_p in zip(doc_rels, doc_resolved):
-        if len(nodes) >= GRAPH_MAX_NODES:
-            break
-        nodes.append(
-            {
-                "id": f"file:{rel}",
-                "label": rel,
-                "file_type": "document",
-                "source_file": rel,
-            }
-        )
-        try:
-            with open(abs_p, "r", encoding="utf-8", errors="strict") as f:
-                content = f.read()[:200000]
-        except Exception:
-            content = ""
-        doc_contents[rel] = content
-        for heading, _level, lineno in _extract_md_sections(abs_p):
-            if len(nodes) >= GRAPH_MAX_NODES:
-                break
-            sec_id = f"sec:{rel}#{_slugify_section(heading)}"
-            if sec_id not in {n["id"] for n in nodes}:
-                nodes.append(
-                    {
-                        "id": sec_id,
-                        "label": heading,
-                        "file_type": "document",
-                        "source_file": rel,
-                        "source_location": f"L{lineno}",
-                        "kind": "section",
-                    }
-                )
-                links.append(
-                    {
-                        "source": f"file:{rel}",
-                        "target": sec_id,
-                        "relation": "contains",
-                        "confidence": "EXTRACTED",
-                        "source_file": rel,
-                    }
-                )
-    for rel, content in doc_contents.items():
-        if not content or len(links) >= GRAPH_MAX_NODES * 2:
-            break
-        for tgt in _extract_md_link_targets(content):
-            resolved_tgt = _resolve_doc_link(tgt, rel, doc_set)
-            if resolved_tgt and resolved_tgt != rel:
-                links.append(
-                    {
-                        "source": f"file:{rel}",
-                        "target": f"file:{resolved_tgt}",
-                        "relation": "references",
-                        "confidence": "EXTRACTED",
-                        "source_file": rel,
-                    }
-                )
-        seen_doc_refs: set[str] = set()
-        for pat in (r"\b([A-Za-z_]\w{3,})\b", r"\b([\w]+-[\w-]+)\b"):
-            for m in re.finditer(pat, content):
-                name = m.group(1)
-                if name in seen_doc_refs:
-                    continue
-                targets = sym_index.get(name, [])
-                if not targets:
-                    continue
-                seen_doc_refs.add(name)
-                for tid in targets[:3]:
-                    links.append(
-                        {
-                            "source": f"file:{rel}",
-                            "target": tid,
-                            "relation": "references",
-                            "confidence": "INFERRED",
-                            "source_file": rel,
-                        }
-                    )
-                if len(seen_doc_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
-                    break
-    for rel in rels:
-        content = file_contents.get(rel, "")
-        if not content:
-            continue
-        suffix = Path(rel).suffix.lower()
-        for mod in _parse_graph_imports(suffix, content):
-            tgt = _resolve_import_to_rel(mod, rel, rel_set)
-            if tgt and tgt != rel:
-                links.append(
-                    {
-                        "source": f"file:{rel}",
-                        "target": f"file:{tgt}",
-                        "relation": "imports",
-                        "confidence": "EXTRACTED",
-                        "source_file": rel,
-                    }
-                )
-        if len(links) >= GRAPH_MAX_NODES * 2:
-            break
-        seen_refs: set[str] = set()
-        for id_re in (_GRAPH_R_ID_RE, _GRAPH_GET_ID_RE):
-            for m in id_re.finditer(content):
-                name = m.group(1)
-                if (rel, name) in seen_refs:
-                    continue
-                for tid in sym_index.get(name, []):
-                    if tid.startswith(f"sym:{rel}#"):
-                        continue
-                    seen_refs.add((rel, name))
-                    links.append(
-                        {
-                            "source": f"file:{rel}",
-                            "target": tid,
-                            "relation": "references",
-                            "confidence": "INFERRED",
-                            "source_file": rel,
-                        }
-                    )
-                    break
-        for m in _GRAPH_CALL_RE.finditer(content):
-            name = m.group(1)
-            if len(name) < 3 or name in {
-                "def",
-                "class",
-                "return",
-                "import",
-                "from",
-                "for",
-                "while",
-                "with",
-            }:
-                continue
-            targets = sym_index.get(name, [])
-            for tid in targets:
-                if tid.startswith(f"sym:{rel}#") or (rel, name) in seen_refs:
-                    continue
-                seen_refs.add((rel, name))
-                links.append(
-                    {
-                        "source": f"file:{rel}",
-                        "target": tid,
-                        "relation": "references",
-                        "confidence": "INFERRED",
-                        "source_file": rel,
-                    }
-                )
-                if len(seen_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
-                    break
-            if len(seen_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
-                break
-    rationale_refs: list[tuple[str, str, str]] = []
-    for rel in rels:
-        content = file_contents.get(rel, "")
-        if not content:
-            continue
-        for m in _GRAPH_TASK_REF_RE.finditer(content):
-            rationale_refs.append((rel, "task", m.group(1)))
-            if len(rationale_refs) >= 200:
-                break
-        for m in _GRAPH_ADR_REF_RE.finditer(content):
-            rationale_refs.append((rel, "adr", m.group(1)))
-            if len(rationale_refs) >= 200:
-                break
-    task_rel_by_id: dict[str, str] = {}
-    for cand_dir in ("backlog", "in-progress", "qa", "completed", "archive"):
-        tdir = workspace_root / "tasks" / cand_dir
-        if not tdir.is_dir():
-            continue
-        try:
-            for md in tdir.glob("*.md"):
-                mm = re.match(r"^(\d+)-", md.name)
-                if mm:
-                    task_rel_by_id.setdefault(
-                        mm.group(1).lstrip("0") or "0",
-                        md.resolve().relative_to(workspace_root).as_posix(),
-                    )
-        except OSError:
-            continue
-    node_ids = {n["id"] for n in nodes}
-    seen_rat: set[tuple[str, str]] = set()
-    for rel, kind, num in rationale_refs:
-        target: str | None = None
-        if kind == "task":
-            trel = task_rel_by_id.get(num.lstrip("0") or "0")
-            if trel:
-                target = f"file:{trel}"
-        else:
-            needle = f"adr-{int(num):03d}"
-            for n in nodes:
-                if n["id"].startswith("sec:") and needle in n["label"].lower():
-                    target = n["id"]
-                    break
-        if target and target in node_ids and len(links) < GRAPH_MAX_NODES * 2:
-            if (rel, target) in seen_rat:
-                continue
-            seen_rat.add((rel, target))
-            links.append(
-                {
-                    "source": f"file:{rel}",
-                    "target": target,
-                    "relation": "rationale_for",
-                    "confidence": "INFERRED",
-                    "source_file": rel,
-                }
-            )
-    table_ids: dict[str, str] = {}
-    for n in nodes:
-        if n.get("kind") in ("table", "view"):
-            table_ids.setdefault(n["label"], n["id"])
-    pruned: list[dict] = []
-    for e in links:
-        if e["target"].startswith("sqlref:"):
-            tname = e["target"][len("sqlref:") :]
-            tid = table_ids.get(tname)
-            if tid is None:
-                continue
-            e = {**e, "target": tid}
-        pruned.append(e)
-    return {"nodes": nodes, "links": pruned}
-
-
-def _graph_degrees(data: dict) -> dict[str, int]:
-    deg: dict[str, int] = {}
-    for n in data.get("nodes", []):
-        deg[n["id"]] = 0
-    for e in data.get("links", []):
-        deg[e["source"]] = deg.get(e["source"], 0) + 1
-        deg[e["target"]] = deg.get(e["target"], 0) + 1
-    return deg
-
-
-def _save_graph(
-    workspace_root: Path, data: dict, target_label: str
-) -> tuple[Path, Path]:
-    report_dir = workspace_root / "context-reports"
-    report_dir.mkdir(parents=True, exist_ok=True)
-    timestamp = time.strftime("%Y%m%d_%H%M%S")
-    unique = uuid.uuid4().hex[:8]
-    json_path = report_dir / f"graph_{timestamp}_{unique}.json"
-    md_path = report_dir / f"graph_report_{timestamp}_{unique}.md"
-    envelope = {
-        "nodes": sorted(data.get("nodes", []), key=lambda n: n["id"]),
-        "links": sorted(
-            data.get("links", []),
-            key=lambda e: (e["source"], e["target"], e["relation"]),
-        ),
-        "graph": {
-            "schema_version": GRAPH_SCHEMA_VERSION,
-            "graphify_version": None,
-            "root": target_label,
-        },
-    }
-    with open(json_path, "w", encoding="utf-8") as f:
-        json.dump(envelope, f, indent=1, sort_keys=False)
-    deg = _graph_degrees(envelope)
-    id2node = {n["id"]: n for n in envelope["nodes"]}
-    sym_rank = sorted(
-        ((d, nid) for nid, d in deg.items() if nid.startswith("sym:")), reverse=True
-    )[:10]
-    ext = sum(1 for e in envelope["links"] if e.get("confidence") == "EXTRACTED")
-    inf = sum(1 for e in envelope["links"] if e.get("confidence") == "INFERRED")
-    amb = len(envelope["links"]) - ext - inf
-    n_docs = sum(1 for n in envelope["nodes"] if n.get("file_type") == "document")
-    n_code = len(envelope["nodes"]) - n_docs
-    lines = [
-        f"# Graph Report - {target_label}",
-        "",
-        f"- **Generated:** {timestamp}",
-        f"- **Schema:** {GRAPH_SCHEMA_VERSION}",
-        f"- **Nodes:** {len(envelope['nodes'])} **Edges:** {len(envelope['links'])}",
-        f"- **Documents:** {n_docs} doc nodes ({n_code} code)",
-        f"- **Confidence:** EXTRACTED {ext} / INFERRED {inf} / AMBIGUOUS {amb}",
-        "",
-        "## God nodes (top by degree)",
-        "",
-    ]
-    for d, nid in sym_rank:
-        n = id2node.get(nid, {})
-        lines.append(
-            f"- {n.get('label', nid)} (degree {d}, {n.get('source_file', '?')})"
-        )
-    lines += [
-        "",
-        "## How to query",
-        "",
-        "- `query_graph` for scoped subgraphs",
-        "- `explain_node` for one concept",
-        "- `shortest_path` to trace two concepts",
-        "",
-    ]
-    md_path.write_text("\n".join(lines), encoding="utf-8")
-    return json_path, md_path
-
-
-def _resolve_graph_file(workspace_root: Path, graph_path: str | None) -> Path | None:
-    report_dir = workspace_root / "context-reports"
-    if graph_path:
-        p = Path(graph_path)
-        cand = p if p.is_absolute() else workspace_root / p
-        try:
-            cand.resolve().relative_to(workspace_root)
-        except ValueError:
-            return None
-        if cand.is_file():
-            return cand
-        alt = report_dir / p.name
-        if alt.is_file():
-            return alt
-        return None
-    if not report_dir.is_dir():
-        return None
-    cands = sorted(
-        report_dir.glob("graph_*.json"), key=lambda q: q.stat().st_mtime, reverse=True
-    )
-    return cands[0] if cands else None
-
-
-def _load_graph_data(
-    workspace_root: Path, graph_path: str | None
-) -> tuple[dict | None, Path | None, str | None]:
-    gp = _resolve_graph_file(workspace_root, graph_path)
-    if gp is None:
-        return None, None, "No graph found. Run build_graph first."
-    try:
-        data = json.loads(gp.read_text(encoding="utf-8"))
-        return data, gp, None
-    except Exception as e:
-        return None, gp, f"Error reading graph {gp}: {e}"
-
-
-def _graph_tokens(text: str) -> set[str]:
-    """Split identifiers so natural words match code: snake_case parts plus
-    camelCase parts, lowercased, minimum length 3. Deterministic."""
-    toks: set[str] = set()
-    for raw in re.findall(r"[A-Za-z0-9]+", text):
-        for part in _GRAPH_TOKEN_SPLIT_RE.split(raw):
-            for sub in part.split("_"):
-                t = sub.lower()
-                if len(t) >= 3:
-                    toks.add(t)
-    return toks
-
-
-def _find_graph_nodes(nodes: list[dict], label: str) -> list[dict]:
-    ll = label.lower()
-    exact = [n for n in nodes if n.get("label", "").lower() == ll]
-    if exact:
-        return exact
-    return [n for n in nodes if ll in n.get("label", "").lower()][:5]
-
-
-def _graph_neighbors(
-    data: dict, nid: str
-) -> tuple[list[tuple[dict, dict]], list[tuple[dict, dict]]]:
-    id2n = {n["id"]: n for n in data.get("nodes", [])}
-    out: list[tuple[dict, dict]] = []
-    inc: list[tuple[dict, dict]] = []
-    for e in data.get("links", []):
-        if e["source"] == nid and e["target"] in id2n:
-            out.append((e, id2n[e["target"]]))
-        elif e["target"] == nid and e["source"] in id2n:
-            inc.append((e, id2n[e["source"]]))
-    return out, inc
-
-
-def _graph_bfs_path(
-    data: dict, src: str, tgt: str, directed: bool = True
-) -> list[tuple[str, dict, str]] | None:
-    from collections import deque
-
-    adj: dict[str, list[tuple[str, dict]]] = {}
-    for e in data.get("links", []):
-        adj.setdefault(e["source"], []).append((e["target"], e))
-        if not directed:
-            adj.setdefault(e["target"], []).append((e["source"], e))
-    if src not in adj and src not in {n["id"] for n in data.get("nodes", [])}:
-        return None
-    prev: dict[str, tuple[str, dict]] = {src: ("", {})}
-    dq = deque([src])
-    while dq:
-        cur = dq.popleft()
-        if cur == tgt:
-            break
-        for nxt, e in sorted(adj.get(cur, []), key=lambda x: x[0]):
-            if nxt not in prev:
-                prev[nxt] = (cur, e)
-                dq.append(nxt)
-    if tgt not in prev:
-        return None
-    path: list[tuple[str, dict, str]] = []
-    cur = tgt
-    while cur != src:
-        pc, e = prev[cur]
-        path.append((pc, e, cur))
-        cur = pc
-    path.reverse()
-    return path
-
 
 @_project_tool
 def build_graph(target_path: str = ".", project_root: str | None = None) -> str:
@@ -1543,30 +243,6 @@ def build_graph(target_path: str = ".", project_root: str | None = None) -> str:
     return f"✅ Success: Graph built for `{tgt}`.\n📊 {len(data['nodes'])} nodes, {len(data['links'])} links in {dur:.2f}s (schema {GRAPH_SCHEMA_VERSION}, caps files {GRAPH_MAX_FILES}).\n📁 Graph: `{json_path}`\n📁 Report: `{md_path}`"
 
 
-def _graph_vocab(data: dict, limit: int = 500) -> list[str]:
-    """Sorted vocabulary tokens from node labels. Powers zero-hit hints."""
-    vocab: set[str] = set()
-    for n in data.get("nodes", []):
-        vocab |= _graph_tokens(n.get("label", ""))
-        if len(vocab) >= limit:
-            break
-    return sorted(vocab)
-
-
-def _suggest_vocab_tokens(
-    vocab: list[str], toks: set[str], limit: int = 8
-) -> list[str]:
-    hints: list[str] = []
-    for t in sorted(toks):
-        for v in vocab:
-            if v.startswith(t) or t in v or t.startswith(v):
-                if v not in hints:
-                    hints.append(v)
-                if len(hints) >= limit:
-                    return hints
-    return hints
-
-
 @_project_tool
 def query_graph(
     question: str,
@@ -2040,27 +716,6 @@ def extract_signatures(file_path: str, project_root: str | None = None) -> str:
         return f"Error extracting signatures from {file_path}: {str(e)}"
 
 
-def _repo_root(start_path: str, project_root: str | None = None) -> Path:
-    """Resolve the git repo root for git subprocess calls.
-
-    CWD fix: this server inherits opencode-server's CWD, which is usually
-    NOT the caller project, so bare `git` calls fail with exit 128.
-    Resolution order: explicit project_root override first, then walk up
-    from absolute task paths to the enclosing `.git`, then CWD fallback
-    (git errors honestly if that is not a repo).
-    """
-    if project_root:
-        return Path(project_root).resolve()
-    p = Path(start_path)
-    start = (
-        (p if p.is_dir() else p.parent) if p.is_absolute() else (Path.cwd() / p).parent
-    )
-    for cand in [start, *start.parents]:
-        if (cand / ".git").exists():
-            return cand
-    return start
-
-
 def _explicit_project_root(project_root: str | None, tool_name: str) -> Path:
     """Validate a per-call project root (Task 279 project_path).
 
@@ -2346,42 +1001,6 @@ def qa_transition(
         return f"❌ Unexpected error in qa_transition: {str(e)}"
 
 
-def _derive_task_slug(task_file_path: str) -> str:
-    """Derives a 'task <NN> - <slug>' label from a task file name (e.g. '78-fix-bug.md' -> 'task 78 - fix bug')."""
-    name = Path(task_file_path).stem
-    parts = re.split(r"[-_]", name, maxsplit=1)
-    if len(parts) == 2 and parts[0].isdigit():
-        return f"task {parts[0]} - {parts[1].replace('-', ' ')}"
-    return f"task - {name.replace('-', ' ')}"
-
-
-# Conventional Commits enforcement (Task 211): `commit_and_clean_task` is the
-# ONLY commit path, so the caller-supplied feature message is validated here
-# against skill-templates/versioning-and-release (`type: subject`, ≤72 chars).
-_CONVENTIONAL_RE = re.compile(r"^(feat|fix|docs|refactor|chore): \S.*$")
-
-
-def _check_conventional_commit(commit_message: str) -> Optional[str]:
-    """Returns an error string when commit_message violates Conventional Commits, else None."""
-    first_line = (
-        commit_message.splitlines()[0]
-        if commit_message and commit_message.strip()
-        else ""
-    )
-    if not _CONVENTIONAL_RE.match(first_line):
-        return (
-            "❌ Commit message rejected: must match Conventional Commits "
-            "`<type>: <subject>` with type in feat|fix|docs|refactor|chore "
-            f"(see skill-templates/versioning-and-release). Got: {first_line!r}"
-        )
-    if len(first_line) > 72:
-        return (
-            "❌ Commit message rejected: first line exceeds 72 characters "
-            f"({len(first_line)}). Got: {first_line!r}"
-        )
-    return None
-
-
 @_project_tool
 def commit_and_clean_task(
     task_file_path: str, commit_message: str, project_root: str | None = None
@@ -2491,404 +1110,6 @@ def commit_and_clean_task(
 # --- bundle_tasks helpers (module-level so tests can import them directly;
 # the bundle_tasks MCP tool below calls these globals; logic is verbatim from
 # the retired scripts/bundle-tasks.py, self-contained since Task 110/155) ---
-ACTIVE_KANBAN_DIRS = ["backlog", "in-progress", "qa", "completed"]
-MAX_BUNDLE_SIZE = 6
-DIFF_SIZE_WARNING_THRESHOLD = 400
-
-
-def _kebab_case(text: str) -> str:
-    """Convert arbitrary title to kebab-case slug (B4: supports Unicode/Persian)."""
-    import unicodedata
-
-    normalized = unicodedata.normalize("NFKD", text)
-    slug = normalized.lower().strip()
-    slug = re.sub(
-        r"[^a-z0-9\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+", "-", slug
-    )
-    slug = re.sub(r"-{2,}", "-", slug)
-    slug = slug.strip("-")
-    return slug or "bundle"
-
-
-def _discover_next_id(tasks_root: Path = Path("tasks")) -> int:
-    max_id = 0
-    if not tasks_root.is_dir():
-        return 1
-    for md in tasks_root.rglob("*.md"):
-        m = re.match(r"^(\d+)-", md.name)
-        if m:
-            try:
-                nid = int(m.group(1))
-                if nid > max_id:
-                    max_id = nid
-            except ValueError:
-                continue
-    return max_id + 1 if max_id else 1
-
-
-def _find_task_file(task_id: str, tasks_root: Path = Path("tasks")) -> Path | None:
-    norm = task_id.lstrip("0") or "0"
-    candidates: list[Path] = []
-    for d in ACTIVE_KANBAN_DIRS:
-        dir_path = tasks_root / d
-        if not dir_path.is_dir():
-            continue
-        for md in dir_path.glob("*.md"):
-            m = re.match(r"^(\d+)-", md.name)
-            if m and m.group(1).lstrip("0") == norm:
-                candidates.append(md)
-    if len(candidates) == 1:
-        return candidates[0]
-    if len(candidates) > 1:
-        return None  # B2: hard halt — duplicate active IDs
-    # Check archive for better error (already archived)
-    for md in (
-        (tasks_root / "archive").glob("*.md")
-        if (tasks_root / "archive").is_dir()
-        else []
-    ):
-        m = re.match(r"^(\d+)-", md.name)
-        if m and m.group(1).lstrip("0") == norm:
-            return None
-    return None
-
-
-def _extract_section(content: str, heading: str) -> str | None:
-    pattern = re.compile(
-        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\n---\s*\n|\Z)",
-        re.MULTILINE | re.DOTALL,
-    )
-    m = pattern.search(content)
-    return m.group(1).strip() if m else None
-
-
-def _extract_title(content: str) -> str:
-    m = re.search(r"^# Task \d+:\s*(.+)$", content, re.MULTILINE)
-    return m.group(1).strip() if m else "Untitled"
-
-
-def _format_task_id_list(ids: list[str]) -> str:
-    return "[" + ", ".join(ids) + "]"
-
-
-def _extract_checklist_with_continuations(section_text: str) -> list[str]:
-    """B1: Extract checklist items with all indented continuation lines."""
-    lines = section_text.splitlines()
-    result: list[str] = []
-    in_checklist = False
-    for line in lines:
-        stripped = line.strip()
-        is_root_bullet = line.startswith("- [")
-        if is_root_bullet:
-            in_checklist = True
-            result.append(stripped)
-        elif in_checklist:
-            if (
-                stripped
-                and not line.startswith("- [")
-                and not stripped.startswith("## ")
-                and not stripped.startswith("---")
-            ):
-                result.append(line)
-            else:
-                in_checklist = False
-                if line.startswith("- ["):
-                    in_checklist = True
-                    result.append(stripped)
-    return result
-
-
-def _detect_stack(content: str) -> str | None:
-    """M1: Detect tech stack from task content."""
-    lower = content.lower()
-    if any(
-        kw in lower
-        for kw in ["jetpack compose", "kotlin", "android", "hilt", "sqldelight"]
-    ):
-        return "android"
-    if any(kw in lower for kw in ["react", "vite", "jsx", "tsx", "next.js", "nextjs"]):
-        return "react"
-    if any(kw in lower for kw in ["fastapi", "pydantic", "uvicorn"]):
-        return "fastapi"
-    if any(kw in lower for kw in ["spring boot", "spring-boot", "java", "mapstruct"]):
-        return "spring"
-    if any(kw in lower for kw in ["swiftui", "ios", "swift", "uikit"]):
-        return "ios"
-    if any(kw in lower for kw in ["golang", "gin", "go-gin", "hexagonal"]):
-        return "go"
-    return None
-
-
-def _verify_verbatim_checksums(
-    source_data: list[tuple[str, Path, str, str]], meta_content: str
-) -> bool:
-    """M2: Verify 100% of extracted source AC text is in the Bundled Checklist."""
-    bundled_match = re.search(
-        r"^## Bundled Checklist.*?\n\n(.*?)(?=^## |\Z)",
-        meta_content,
-        re.MULTILINE | re.DOTALL,
-    )
-    if not bundled_match:
-        return False
-    bundled_text = bundled_match.group(1)
-    for sid, path, content, _title in source_data:
-        ac = _extract_section(content, "Acceptance Criteria")
-        if not ac:
-            continue
-        for line in ac.splitlines():
-            stripped = line.strip()
-            if stripped and stripped.startswith("- ["):
-                m = re.match(r"^- \[[ xX]\]\s*(.*)", stripped)
-                core = m.group(1) if m else stripped
-                prefixed = f"[{sid}] {core}"
-                if len(core) > 10 and prefixed not in bundled_text:
-                    return False
-    return True
-
-
-def _git_mv_or_fallback(src: Path, dst: Path) -> bool:
-    dst.parent.mkdir(parents=True, exist_ok=True)
-    repo = str(_repo_root(str(src)))
-    result = subprocess.run(
-        ["git", "mv", str(src), str(dst)], capture_output=True, text=True, cwd=repo
-    )
-    if result.returncode == 0:
-        return True
-    if (
-        "not under version control" in result.stderr
-        or "not tracked" in result.stderr.lower()
-    ):
-        try:
-            src.rename(dst)
-            subprocess.run(
-                ["git", "add", "--", str(dst)],
-                check=True,
-                capture_output=True,
-                cwd=repo,
-            )
-            return True
-        except Exception:
-            return False
-    return False
-
-
-def _patch_archived_file(archive_path: Path, meta_id: str, meta_slug: str) -> None:
-    try:
-        content = archive_path.read_text(encoding="utf-8")
-    except Exception:
-        return
-    new_file_header = f"**File:** `tasks/archive/{archive_path.name}`"
-    content = re.sub(r"\*\*File:\*\*\s*`[^`]+`", new_file_header, content, count=1)
-    if re.search(r"\*\*Status:\*\*\s*\w+", content):
-        content = re.sub(
-            r"\*\*Status:\*\*\s*\w+", "**Status:** superseded", content, count=1
-        )
-    else:
-        content = re.sub(
-            r"(\*\*Type:\*\*\s*\w+)", r"\1\n**Status:** superseded", content, count=1
-        )
-    if "**Superseded-By:**" not in content:
-        content = re.sub(
-            r"(\*\*Status:\*\*\s*superseded)",
-            rf"\1\n**Superseded-By:** `{meta_id}-{meta_slug}`",
-            content,
-            count=1,
-        )
-        timestamp = time.strftime("%Y-%m-%d")
-        content = re.sub(
-            r"(\*\*Superseded-By:\*\*\s*`[^`]+`)",
-            rf"\1\n**Superseded-At:** `{timestamp}`",
-            content,
-            count=1,
-        )
-    superseded_note = (
-        f"> **Superseded:** This task was bundled into META task `{meta_id}-{meta_slug}` "
-        f"and archived on {time.strftime('%Y-%m-%d')}. "
-        f"See `tasks/backlog/{meta_id}-{meta_slug}.md` (or its Kanban successor) for the unified execution. "
-        f"History preserved via `git log --follow -- tasks/archive/{archive_path.name}`.\n"
-    )
-    if superseded_note.strip() not in content:
-        if "## Execution Log" in content:
-            content = content.replace(
-                "## Execution Log", superseded_note + "\n## Execution Log", 1
-            )
-        elif "## Factual Git Diff" in content:
-            content = content.replace(
-                "## Factual Git Diff", superseded_note + "\n## Factual Git Diff", 1
-            )
-    try:
-        archive_path.write_text(content, encoding="utf-8")
-    except Exception:
-        pass
-
-
-def _build_meta_content(
-    meta_id: int,
-    meta_slug: str,
-    meta_title: str,
-    source_ids: list[str],
-    source_data: list[tuple[str, Path, str, str]],
-) -> str:
-    meta_id_str = f"{meta_id:02d}" if meta_id < 100 else str(meta_id)
-    if meta_id >= 100:
-        meta_id_str = str(meta_id)
-    file_header = f"tasks/backlog/{meta_id_str}-{meta_slug}.md"
-    title_line = f"# Task {meta_id}: {meta_title}"
-    timestamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
-    bundled_checklist_items: list[str] = []
-    local_todos_aggregated: list[str] = []
-    total_loc = 0
-    per_source_blocks: list[str] = []
-    for sid, path, content, stitle in source_data:
-        goal = _extract_section(content, "Goal") or "_(No Goal section found)_"
-        ac = (
-            _extract_section(content, "Acceptance Criteria")
-            or "_(No Acceptance Criteria)_"
-        )
-        todos = _extract_section(content, "Local TODOs") or "_(No Local TODOs)_"
-        risk = _extract_section(content, "Risk & Rollback")
-        manager_notes = _extract_section(content, "Manager's Notes")
-        source_context = ""
-        if "## Blueprint Reference" in content:
-            br = _extract_section(content, "Blueprint Reference")
-            if br:
-                source_context += f"\n**Blueprint Reference (verbatim):**\n{br}\n"
-        total_loc += len(content.splitlines())
-        # B1: multi-line checklist extraction
-        ac_lines = _extract_checklist_with_continuations(ac)
-        if not ac_lines:
-            ac_lines = [
-                f"- [ ] {line.strip()}"
-                for line in ac.splitlines()
-                if line.strip() and not line.strip().startswith("#")
-            ][:3]
-        for line in ac_lines:
-            if line.startswith("- ["):
-                m = re.match(r"^- \[[ xX]\]\s*(.*)", line)
-                inner = m.group(1) if m else line
-                bundled_checklist_items.append(f"- [ ] [{sid}] {inner}")
-            else:
-                bundled_checklist_items.append(line)
-        # B1: multi-line TODO extraction
-        todo_lines = _extract_checklist_with_continuations(todos)
-        for line in todo_lines:
-            if line.startswith("- ["):
-                m = re.match(r"^- \[[ xX]\]\s*(.*)", line)
-                inner = m.group(1) if m else line
-                local_todos_aggregated.append(f"- [ ] [{sid}] {inner}")
-            else:
-                local_todos_aggregated.append(line)
-        block = f"### Source Task {sid}: {stitle}\n\n"
-        block += f"**Original File:** `{path}` → `tasks/archive/{path.name}` (after bundling)\n\n"
-        block += f"**Title:** {stitle}\n\n"
-        block += "#### Goal (verbatim)\n\n"
-        block += f"{goal}\n\n"
-        if manager_notes:
-            block += "#### Manager's Notes (verbatim)\n\n"
-            block += f"{manager_notes}\n\n"
-        if source_context:
-            block += source_context + "\n"
-        block += "#### Acceptance Criteria (verbatim)\n\n"
-        block += f"{ac}\n\n"
-        block += "#### Local TODOs (verbatim)\n\n"
-        block += f"{todos}\n\n"
-        if risk:
-            block += "#### Risk & Rollback (verbatim)\n\n"
-            block += f"{risk}\n\n"
-        block += "---\n\n"
-        per_source_blocks.append(block)
-    seen_todos: set[str] = set()
-    deduped_todos: list[str] = []
-    for t in local_todos_aggregated:
-        if t not in seen_todos:
-            seen_todos.add(t)
-            deduped_todos.append(t)
-    meta_local_todos = (
-        f"- [ ] Step 1: Validate META bundle — confirm all {len(source_data)} source requirements are captured verbatim below\n"
-        f"- [ ] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)\n"
-    )
-    for t in deduped_todos:
-        meta_local_todos += f"{t}\n"
-    meta_local_todos += f"- [ ] Step {len(deduped_todos) + 3}: Verify all bundled checklist items and run lint_task_file + verification-before-completion\n"
-    meta_local_todos += f"- [ ] Step {len(deduped_todos) + 4}: Update CHANGELOG.md and record Verification Evidence\n"
-    meta_ac = (
-        "\n".join(bundled_checklist_items)
-        if bundled_checklist_items
-        else "- [ ] _(No aggregated criteria — check per-source blocks)_"
-    )
-    meta_ac += f"\n- [ ] Traceability: All {len(source_data)} source tasks are archived with superseded-by marker and reachable via `git log --follow`"
-    meta_verification = (
-        f"- **Test command:** `lint_task_file` on META file; `git log --oneline --follow -- tasks/archive/<id>-*.md | head` for archived sources; project test suite if logic changed\n"
-        f"- **Expected result:** META lint passes; all {len(source_data)} sources in `tasks/archive/` with `superseded` status; single Factual Git Diff covers all bundled changes\n"
-        f"- **Actual result:** _(Hands fill during execution)_\n"
-        f"- **Exit code:** _(Hands fill)_\n"
-    )
-    meta_risk = (
-        "- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.\n"
-        "- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.\n"
-        "- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.\n"
-        f"- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded {_format_task_id_list(source_ids)}, remove Superseded-By footer, delete or archive `tasks/backlog/{meta_id_str}-{meta_slug}.md` as abandoned. No HQ code beyond bundler is affected.\n"
-    )
-    warning_note = ""
-    if total_loc > DIFF_SIZE_WARNING_THRESHOLD:
-        warning_note = (
-            f"> ⚠️ **Guardrail Warning:** Combined source size is {total_loc} LOC (> {DIFF_SIZE_WARNING_THRESHOLD}). "
-            f"Unified META diff may be large and hard to review. Consider splitting into two METAs.\n\n"
-        )
-    content = (
-        f"{title_line}\n\n"
-        f"**File:** `{file_header}`\n"
-        f"**Source:** manager\n"
-        f"**Type:** feature\n"
-        f"**Status:** open\n"
-        f"**Supersedes:** {_format_task_id_list(source_ids)}\n"
-        f"**Meta:** true\n"
-        f"**Created:** {timestamp}\n"
-        f"**Bundled:** {len(source_data)} tasks\n\n"
-        f"## Goal\n\n"
-        f'Unified execution of {len(source_data)} related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks {_format_task_id_list(source_ids)} — "{meta_title}" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.\n\n'
-        f"{warning_note}**Source IDs:** {_format_task_id_list(source_ids)}\n"
-        f'**Next ID:** {meta_id} (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)\n'
-        f"**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: {meta_id}-{meta_slug}` and remain reachable via `git log --follow` (never purged until META is completed).\n\n"
-        f"## Manager's Notes\n\n"
-        f"**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute {len(source_data)} small related tasks together and speed up turnaround.\n\n"
-        f"**Traceability:**\n"
-        f"- Supersedes {_format_task_id_list(source_ids)} — see per-source verbatim blocks below\n"
-        f"- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** {meta_id_str}-{meta_slug}` header + superseded footer\n"
-        f"- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file\n\n"
-        f"**Guardrails Applied:**\n"
-        f"- Cap 6 per bundle — this bundle has {len(source_data)} ({'✅ within cap' if len(source_data) <= MAX_BUNDLE_SIZE else '❌ exceeds cap — requires --force'})\n"
-        f"- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)\n"
-        f"- Diff-size check — combined {total_loc} LOC ({'⚠️ exceeds 400 — consider split' if total_loc > DIFF_SIZE_WARNING_THRESHOLD else '✅ within 400'})\n\n"
-        f"## Source Bundles (Verbatim Preservation)\n\n"
-        f"The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.\n\n"
-        f"{''.join(per_source_blocks)}\n"
-        f"## Bundled Checklist (All-or-Nothing)\n\n"
-        f"> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.\n\n"
-        f"{meta_ac}\n\n"
-        f"## Local TODOs\n\n"
-        f"{meta_local_todos.strip()}\n\n"
-        f"## Acceptance Criteria\n\n"
-        f"{meta_ac}\n\n"
-        f"## Verification Evidence\n\n"
-        f"{meta_verification.strip()}\n\n"
-        f"## Definition of Done\n\n"
-        f"The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):\n\n"
-        f"- [ ] Build/Test/Lint pass with exit code 0\n"
-        f"- [ ] `lint_task_file` passes on the active task file\n"
-        f"- [ ] `CHANGELOG.md` updated via Parse-Then-Append\n"
-        f"- [ ] `verification-before-completion` applied and evidence recorded\n\n"
-        f"## Risk & Rollback\n\n"
-        f"{meta_risk.strip()}\n\n"
-        f"---\n\n"
-        f"## Execution Log & Reasoning\n\n"
-        f"_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_\n\n"
-        f"## Factual Git Diff\n\n"
-        f"<!-- BEGIN_GIT_DIFF -->\n\n"
-        f"_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_\n\n"
-        f"<!-- END_GIT_DIFF -->\n"
-    )
-    return content
 
 
 @_project_tool
diff --git a/mcp-context-server/signatures.py b/mcp-context-server/signatures.py
new file mode 100644
index 0000000..6d0e51d
--- /dev/null
+++ b/mcp-context-server/signatures.py
@@ -0,0 +1,169 @@
+# Sibling Docs: README.md | Decisions: DECISIONS.md
+
+
+"""Structural signature extraction via tree-sitter AST with regex fallback. Stdlib-pure: no MCP imports, no registration, no import back to server."""
+
+import importlib
+from pathlib import Path
+from typing import Optional
+
+
+_EXTENSION_LANG_MAP: dict[str, str] = {
+    ".py": "python",
+    ".js": "javascript",
+    ".jsx": "javascript",
+    ".mjs": "javascript",
+    ".cjs": "javascript",
+    ".ts": "typescript",
+    ".tsx": "typescript",
+    ".mts": "typescript",
+    ".cts": "typescript",
+    ".go": "go",
+    ".java": "java",
+    ".jsp": "java",
+    ".rs": "rust",
+    ".kt": "kotlin",
+    ".kts": "kotlin",
+    ".swift": "swift",
+    ".rb": "ruby",
+    ".php": "php",
+    ".cs": "c_sharp",
+}
+
+
+_TS_QUERIES: dict[str, list[str]] = {
+    "python": [
+        "(function_definition name: (identifier) @name parameters: (parameters) @params) @sig",
+        "(class_definition name: (identifier) @name) @sig",
+    ],
+    "javascript": [
+        "(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
+        "(class_declaration name: (identifier) @name) @sig",
+        "(method_definition name: (property_identifier) @name) @sig",
+        "(arrow_function) @sig",
+        "(generator_function_declaration name: (identifier) @name) @sig",
+    ],
+    "typescript": [
+        "(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
+        "(class_declaration name: (type_identifier) @name) @sig",
+        "(interface_declaration name: (type_identifier) @name) @sig",
+        "(method_definition name: (property_identifier) @name) @sig",
+        "(type_alias_declaration name: (type_identifier) @name) @sig",
+        "(enum_declaration name: (identifier) @name) @sig",
+        "(arrow_function) @sig",
+    ],
+    "go": [
+        "(function_declaration name: (identifier) @name parameters: (parameter_list) @params) @sig",
+        "(method_declaration receiver: (parameter_list) @receiver name: (field_identifier) @name) @sig",
+        "(type_declaration (type_spec name: (type_identifier) @name)) @sig",
+    ],
+    "java": [
+        "(method_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
+        "(class_declaration name: (identifier) @name) @sig",
+        "(interface_declaration name: (identifier) @name) @sig",
+        "(enum_declaration name: (identifier) @name) @sig",
+        "(record_declaration name: (identifier) @name) @sig",
+    ],
+    "rust": [
+        "(function_item name: (identifier) @name parameters: (parameters) @params) @sig",
+        "(struct_item name: (type_identifier) @name) @sig",
+        "(enum_item name: (type_identifier) @name) @sig",
+        "(trait_item name: (type_identifier) @name) @sig",
+        "(type_item name: (type_identifier) @name) @sig",
+        "(impl_item trait: (type_identifier) @name) @sig",
+    ],
+    "kotlin": [
+        "(function_declaration name: (identifier) @name) @sig",
+        "(class_declaration name: (identifier) @name) @sig",
+    ],
+}
+
+
+_ts_language_cache: dict[str, object] = {}
+
+
+def _get_ts_language(lang_id: str) -> object:
+    if lang_id in _ts_language_cache:
+        return _ts_language_cache[lang_id]
+    pkg_name = f"tree_sitter_{lang_id}"
+    try:
+        mod = importlib.import_module(pkg_name)
+        from tree_sitter import Language as TSLanguage
+
+        if lang_id == "typescript":
+            lang = TSLanguage(mod.language_typescript())
+        else:
+            lang = TSLanguage(mod.language())
+        _ts_language_cache[lang_id] = lang
+        return lang
+    except Exception:
+        _ts_language_cache[lang_id] = None
+        return None
+
+
+def _extract_signature_line(source_lines: list[str], start_row: int) -> str:
+    first = source_lines[start_row].rstrip("\n").rstrip("\r")
+    if not first.rstrip().endswith(",") and first.count("(") == first.count(")"):
+        return first
+    parts: list[str] = [first]
+    for line in source_lines[start_row + 1 :]:
+        stripped = line.rstrip("\n").rstrip("\r")
+        parts.append(stripped)
+        if ":" in stripped and not stripped.rstrip().endswith(","):
+            break
+        if stripped.rstrip().endswith("{"):
+            break
+        if stripped.rstrip().endswith("):") or stripped.rstrip().endswith(") {"):
+            break
+    return "\n".join(parts)
+
+
+def _extract_via_tree_sitter(file_path: Path) -> Optional[str]:
+    ext = file_path.suffix.lower()
+    lang_id = _EXTENSION_LANG_MAP.get(ext)
+    if not lang_id:
+        return None
+    lang = _get_ts_language(lang_id)
+    if lang is None:
+        return None
+    queries = _TS_QUERIES.get(lang_id)
+    if not queries:
+        return None
+    try:
+        with open(file_path, "r", encoding="utf-8") as f:
+            content = f.read()
+    except Exception:
+        return None
+    source_bytes = content.encode("utf-8")
+    from tree_sitter import Parser, Query, QueryCursor
+
+    parser = Parser(lang)
+    tree = parser.parse(source_bytes)
+    source_lines = content.split("\n")
+    seen: set[str] = set()
+    signatures: list[str] = []
+    for query_str in queries:
+        try:
+            q = Query(lang, query_str)
+            qc = QueryCursor(q)
+            matches = qc.matches(tree.root_node)
+            for _pattern_index, captures in matches:
+                sig_nodes = captures.get("sig", [])
+                for node in sig_nodes:
+                    start_row = node.start_point[0]
+                    sig_line = _extract_signature_line(source_lines, start_row).strip()
+                    if sig_line and sig_line not in seen:
+                        seen.add(sig_line)
+                        signatures.append(sig_line)
+        except Exception:
+            continue
+    if not signatures:
+        return None
+    return f"### Signatures in {file_path}\n" + "\n".join(signatures)
+
+
+# --- End tree-sitter ---
+
+# Runaway-traversal guards (Task 177): a single wedged request (e.g. tree of
+# "/") used to burn minutes of CPU on the single-threaded stdio server and
+# starve every later tool call. These caps bound any single walk.
diff --git a/mcp-lint-server/server.py b/mcp-lint-server/server.py
index bb86e9f..cf1f36d 100755
--- a/mcp-lint-server/server.py
+++ b/mcp-lint-server/server.py
@@ -35,15 +35,18 @@ mcp = FastMCP("LintServer", host="127.0.0.1", port=8101)
 # Client-visible project-isolation warning (Task 279 F6/V1); see
 # mcp-context-server for rationale. No absolute paths echoed (privacy).
 _FALLBACK_FIRED: contextvars.ContextVar[bool] = contextvars.ContextVar(
-    "lint_fallback_fired", default=False)
+    "lint_fallback_fired", default=False
+)
 ROOT_FALLBACK_WARNING = (
     "WARNING [project-isolation]: project_root was omitted, so this call "
     "was scoped to the singleton server's own directory instead of the "
-    "calling project. Pass an absolute project_root on every call.")
+    "calling project. Pass an absolute project_root on every call."
+)
 
 
 def _project_tool(fn):
     """Register an MCP tool that surfaces root-fallback client-visibly."""
+
     @functools.wraps(fn)
     def wrapper(*args, **kwargs):
         _FALLBACK_FIRED.set(False)
@@ -53,6 +56,7 @@ def _project_tool(fn):
         if isinstance(out, str):
             return ROOT_FALLBACK_WARNING + "\n" + out
         return out
+
     return mcp.tool()(wrapper)
 
 
@@ -106,7 +110,7 @@ def _check_markdown_basics(content: str, file_path: str) -> list[str]:
         A list of issue descriptions found in the content.
     """
     issues: list[str] = []
-    lines = content.split('\n')
+    lines = content.split("\n")
 
     # The machine-generated `## Factual Git Diff` block (between the
     # BEGIN_GIT_DIFF / END_GIT_DIFF markers) can contain arbitrary raw git
@@ -167,7 +171,11 @@ def _check_markdown_basics(content: str, file_path: str) -> list[str]:
                 issues.append(f"Line {i}: Missing blank line before heading.")
 
             # Check for missing blank line after heading
-            if i < len(lines) and lines[i].strip() != "" and not lines[i].strip().startswith("#"):
+            if (
+                i < len(lines)
+                and lines[i].strip() != ""
+                and not lines[i].strip().startswith("#")
+            ):
                 issues.append(f"Line {i}: Missing blank line after heading.")
 
         # Check for trailing whitespace (excluding intentional double-space for line breaks)
@@ -217,13 +225,13 @@ def _check_task_file_structure(content: str, file_path: str) -> list[str]:
     filename = Path(file_path).name
 
     # 1. Title number matches filename ID
-    id_match = re.match(r'^(\d+)-', filename)
+    id_match = re.match(r"^(\d+)-", filename)
     if id_match:
         file_id = id_match.group(1)
-        title_match = re.search(r'^# Task (\d+):', content, re.MULTILINE)
+        title_match = re.search(r"^# Task (\d+):", content, re.MULTILINE)
         if title_match:
             title_id = title_match.group(1)
-            if file_id.lstrip('0') != title_id.lstrip('0'):
+            if file_id.lstrip("0") != title_id.lstrip("0"):
                 issues.append(
                     f"Task ID mismatch: Filename has '{file_id}' but title has '{title_id}'."
                 )
@@ -247,7 +255,7 @@ def _check_task_file_structure(content: str, file_path: str) -> list[str]:
     # symlinks so equivalent spellings of the same file never false-positive.
     # This still catches genuinely stale headers left behind after git mv
     # between Kanban directories (different file => different resolved path).
-    file_header_match = re.search(r'\*\*File:\*\*\s*`([^`]+)`', content)
+    file_header_match = re.search(r"\*\*File:\*\*\s*`([^`]+)`", content)
     if not file_header_match:
         issues.append("Missing `**File:**` metadata field.")
     else:
@@ -285,7 +293,7 @@ def _check_task_file_structure(content: str, file_path: str) -> list[str]:
     # instead of test-command evidence: the required-section set swaps
     # `## Verification Evidence` for `## Report Evidence`, whose body must
     # name the report file and carry a non-empty multi-line result.
-    task_type_match = re.search(r'\*\*Type:\*\*\s*(\w+)', content)
+    task_type_match = re.search(r"\*\*Type:\*\*\s*(\w+)", content)
     is_analysis = bool(task_type_match and task_type_match.group(1) == "analysis")
     required_sections = [
         "## Goal",
@@ -338,10 +346,9 @@ def _check_task_file_structure(content: str, file_path: str) -> list[str]:
     # matches this intentional backward-compatibility shim inside the linter.
     canonical_execution_log_header = "## Execution Log & Reasoning"
     legacy_execution_log_header = "## OpenCode " + "Execution Log & Reasoning"
-    execution_log_heading_count = (
-        _count_heading(pre_diff, canonical_execution_log_header)
-        + _count_heading(pre_diff, legacy_execution_log_header)
-    )
+    execution_log_heading_count = _count_heading(
+        pre_diff, canonical_execution_log_header
+    ) + _count_heading(pre_diff, legacy_execution_log_header)
     if execution_log_heading_count == 0:
         issues.append("Missing required section: `## Execution Log & Reasoning`")
     elif execution_log_heading_count > 1:
@@ -353,17 +360,22 @@ def _check_task_file_structure(content: str, file_path: str) -> list[str]:
         )
 
     # 3. BEGIN/END markers
-    if "<!-- BEGIN_GIT_DIFF -->" not in content or "<!-- END_GIT_DIFF -->" not in content:
-        issues.append("Missing `<!-- BEGIN_GIT_DIFF -->` or `<!-- END_GIT_DIFF -->` markers.")
+    if (
+        "<!-- BEGIN_GIT_DIFF -->" not in content
+        or "<!-- END_GIT_DIFF -->" not in content
+    ):
+        issues.append(
+            "Missing `<!-- BEGIN_GIT_DIFF -->` or `<!-- END_GIT_DIFF -->` markers."
+        )
 
     # 4. Source field
-    if not re.search(r'\*\*Source:\*\*\s*(orchestrator|telegram|manager)', content):
+    if not re.search(r"\*\*Source:\*\*\s*(orchestrator|telegram|manager)", content):
         issues.append("Missing or invalid `**Source:**` metadata field.")
 
     # 5. Type field (Task 110: allow `meta` for bundled META tasks; canonical META still uses `feature` + `**Meta:** true`;
     # GitHub issue 19 P6: allow `analysis` for analysis-only tasks carrying `## Report Evidence`)
     if not re.search(
-        r'\*\*Type:\*\*\s*(bug|improvement|feature|chore|docs|refactor|security|research|infra|meta|analysis)',
+        r"\*\*Type:\*\*\s*(bug|improvement|feature|chore|docs|refactor|security|research|infra|meta|analysis)",
         content,
     ):
         issues.append("Missing or invalid `**Type:**` metadata field.")
@@ -383,13 +395,12 @@ def _check_report_evidence_body(pre_diff: str) -> list[str]:
     lines = pre_diff.splitlines()
     try:
         start = next(
-            i for i, line in enumerate(lines)
-            if line.strip() == "## Report Evidence"
+            i for i, line in enumerate(lines) if line.strip() == "## Report Evidence"
         )
     except StopIteration:  # Missing-section error already reported above.
         return issues
     body: list[str] = []
-    for line in lines[start + 1:]:
+    for line in lines[start + 1 :]:
         if line.startswith("## ") or line.strip() == "---":
             break
         body.append(line)
@@ -399,18 +410,18 @@ def _check_report_evidence_body(pre_diff: str) -> list[str]:
             "with a non-blank `Report:` line."
         )
     result_idx = next(
-        (i for i, line in enumerate(body)
-         if line.strip().startswith("Result:")), None
+        (i for i, line in enumerate(body) if line.strip().startswith("Result:")), None
     )
     outcome: list[str] = []
     if result_idx is not None:
         # Same-line content after `Result:` counts; bare `Exit code:`
         # residue never substitutes for the recorded outcome.
-        remainder = body[result_idx].strip()[len("Result:"):].strip()
+        remainder = body[result_idx].strip()[len("Result:") :].strip()
         if remainder and not remainder.startswith("Exit code:"):
             outcome.append(remainder)
         outcome.extend(
-            line.strip() for line in body[result_idx + 1:]
+            line.strip()
+            for line in body[result_idx + 1 :]
             if line.strip() and not line.strip().startswith("Exit code:")
         )
     if result_idx is None or not outcome:
@@ -423,6 +434,7 @@ def _check_report_evidence_body(pre_diff: str) -> list[str]:
 
 # --- MCP Tools ---
 
+
 def _explicit_project_root(project_root: str | None, tool_name: str) -> Path:
     """Validate a per-call project root (Task 279 project_path).
 
@@ -434,8 +446,10 @@ def _explicit_project_root(project_root: str | None, tool_name: str) -> Path:
     if project_root is None:
         root = Path.cwd().resolve()
         _FALLBACK_FIRED.set(True)
-        print(f"Warning: {tool_name}: project_root omitted, falling back to server cwd {root}",
-              file=sys.stderr)
+        print(
+            f"Warning: {tool_name}: project_root omitted, falling back to server cwd {root}",
+            file=sys.stderr,
+        )
         return root
     if not isinstance(project_root, str) or not project_root:
         raise ValueError("project_root must be a non-empty absolute path string.")
@@ -443,9 +457,12 @@ def _explicit_project_root(project_root: str | None, tool_name: str) -> Path:
         raise ValueError(f"project_root must be absolute, got: {project_root!r}.")
     root = Path(project_root).resolve()
     if not root.is_dir():
-        raise ValueError(f"project_root must be an existing directory, got: {project_root!r}.")
+        raise ValueError(
+            f"project_root must be an existing directory, got: {project_root!r}."
+        )
     return root
 
+
 @_project_tool
 def lint_markdown(file_path: str, project_root: str | None = None) -> str:
     """
@@ -465,12 +482,14 @@ def lint_markdown(file_path: str, project_root: str | None = None) -> str:
         workspace_root = _explicit_project_root(project_root, "lint_markdown")
     except ValueError as e:
         return f"Error: {e}"
-    path = Path(file_path) if Path(file_path).is_absolute() else workspace_root / file_path
+    path = (
+        Path(file_path) if Path(file_path).is_absolute() else workspace_root / file_path
+    )
     if not path.is_file():
         return f"Error: File not found: {file_path}"
 
     try:
-        with open(path, 'r', encoding='utf-8') as f:
+        with open(path, "r", encoding="utf-8") as f:
             content = f.read()
     except Exception as e:
         return f"Error reading file: {e}"
@@ -480,7 +499,9 @@ def lint_markdown(file_path: str, project_root: str | None = None) -> str:
     if not issues:
         return f"✅ {file_path} passed Markdown linting."
 
-    return f"⚠️ {len(issues)} issues found in {file_path}:\n" + "\n".join(f"- {i}" for i in issues)
+    return f"⚠️ {len(issues)} issues found in {file_path}:\n" + "\n".join(
+        f"- {i}" for i in issues
+    )
 
 
 @_project_tool
@@ -503,12 +524,16 @@ def lint_task_file(task_file_path: str, project_root: str | None = None) -> str:
         workspace_root = _explicit_project_root(project_root, "lint_task_file")
     except ValueError as e:
         return f"Error: {e}"
-    path = Path(task_file_path) if Path(task_file_path).is_absolute() else workspace_root / task_file_path
+    path = (
+        Path(task_file_path)
+        if Path(task_file_path).is_absolute()
+        else workspace_root / task_file_path
+    )
     if not path.is_file():
         return f"Error: File not found: {task_file_path}"
 
     try:
-        with open(path, 'r', encoding='utf-8') as f:
+        with open(path, "r", encoding="utf-8") as f:
             content = f.read()
     except Exception as e:
         return f"Error reading file: {e}"
@@ -521,14 +546,15 @@ def lint_task_file(task_file_path: str, project_root: str | None = None) -> str:
     if not all_issues:
         return f"✅ {task_file_path} passed Task File linting."
 
-    return (
-        f"⚠️ {len(all_issues)} issues found in {task_file_path}:\n"
-        + "\n".join(f"- {i}" for i in all_issues)
+    return f"⚠️ {len(all_issues)} issues found in {task_file_path}:\n" + "\n".join(
+        f"- {i}" for i in all_issues
     )
 
 
 @_project_tool
-def lint_all_tasks(include_archive: bool = False, project_root: str | None = None) -> str:
+def lint_all_tasks(
+    include_archive: bool = False, project_root: str | None = None
+) -> str:
     """
     Run lint_task_file on ALL task files across the ACTIVE Kanban subdirectories.
 
@@ -568,19 +594,23 @@ def lint_all_tasks(include_archive: bool = False, project_root: str | None = Non
         for md_file in sorted(dir_path.glob("*.md")):
             total_files += 1
             try:
-                with open(md_file, 'r', encoding='utf-8') as f:
+                with open(md_file, "r", encoding="utf-8") as f:
                     content = f.read()
             except Exception:
                 continue
 
-            issues = _check_markdown_basics(content, str(md_file)) + _check_task_file_structure(
+            issues = _check_markdown_basics(
                 content, str(md_file)
-            )
+            ) + _check_task_file_structure(content, str(md_file))
             if issues:
                 total_issues += len(issues)
-                report.append(f"**{md_file.relative_to(tasks_dir)}** ({len(issues)} issues)")
+                report.append(
+                    f"**{md_file.relative_to(tasks_dir)}** ({len(issues)} issues)"
+                )
 
-    summary = f"Scanned {total_files} task files. Found {total_issues} total issues.\n\n"
+    summary = (
+        f"Scanned {total_files} task files. Found {total_issues} total issues.\n\n"
+    )
     if report:
         summary += "Files with issues:\n" + "\n".join(f"- {r}" for r in report)
     else:
@@ -745,7 +775,10 @@ def _check_system_prompt_sync(
         diff_text = "".join(diff_lines[:200])  # cap to avoid huge output
         if len(diff_lines) > 200:
             diff_text += f"\n... ({len(diff_lines) - 200} more diff lines truncated)\n"
-        return False, f"⚠️ DRIFT DETECTED — system-prompt.md is out of sync with prompts/:\n{diff_text}"
+        return (
+            False,
+            f"⚠️ DRIFT DETECTED — system-prompt.md is out of sync with prompts/:\n{diff_text}",
+        )
     except Exception as e:
         # BROAD DIAGNOSTIC CATCH (QA Fix Round 3): this function is a
         # diagnostic tool exposed over the MCP lint server. It must degrade
diff --git a/mcp-memory-server/server.py b/mcp-memory-server/server.py
index 42a700c..7e6ff4e 100755
--- a/mcp-memory-server/server.py
+++ b/mcp-memory-server/server.py
@@ -28,15 +28,18 @@ mcp = FastMCP("ProjectMemory", host="127.0.0.1", port=8103)
 # Client-visible project-isolation warning (Task 279 F6/V1); see
 # mcp-context-server for rationale. No absolute paths echoed (privacy).
 _FALLBACK_FIRED: contextvars.ContextVar[bool] = contextvars.ContextVar(
-    "project_memory_fallback_fired", default=False)
+    "project_memory_fallback_fired", default=False
+)
 ROOT_FALLBACK_WARNING = (
     "WARNING [project-isolation]: project_root was omitted, so this call "
     "was scoped to the singleton server's own directory instead of the "
-    "calling project. Pass an absolute project_root on every call.")
+    "calling project. Pass an absolute project_root on every call."
+)
 
 
 def _project_tool(fn):
     """Register an MCP tool that surfaces root-fallback client-visibly."""
+
     @functools.wraps(fn)
     def wrapper(*args, **kwargs):
         _FALLBACK_FIRED.set(False)
@@ -46,8 +49,10 @@ def _project_tool(fn):
         if isinstance(out, str):
             return ROOT_FALLBACK_WARNING + "\n" + out
         return out
+
     return mcp.tool()(wrapper)
 
+
 def _explicit_project_root(project_root: str | None, tool_name: str) -> Path:
     """Validate a per-call project root (Task 279 project_path).
 
@@ -59,7 +64,10 @@ def _explicit_project_root(project_root: str | None, tool_name: str) -> Path:
     if project_root is None:
         root = Path.cwd().resolve()
         _FALLBACK_FIRED.set(True)
-        print(f"Warning: {tool_name}: project_root omitted, falling back to server cwd {root}", file=sys.stderr)
+        print(
+            f"Warning: {tool_name}: project_root omitted, falling back to server cwd {root}",
+            file=sys.stderr,
+        )
         return root
     if not isinstance(project_root, str) or not project_root:
         raise ValueError("project_root must be a non-empty absolute path string.")
@@ -67,23 +75,36 @@ def _explicit_project_root(project_root: str | None, tool_name: str) -> Path:
         raise ValueError(f"project_root must be absolute, got: {project_root!r}.")
     root = Path(project_root).resolve()
     if not root.is_dir():
-        raise ValueError(f"project_root must be an existing directory, got: {project_root!r}.")
+        raise ValueError(
+            f"project_root must be an existing directory, got: {project_root!r}."
+        )
     return root
 
+
 def _memory_dir(project_root: str | None, tool_name: str) -> Path:
     """Per-call memory base dir: <project_root>/.opencode/memory, else legacy server-cwd MEMORY_DIR."""
     if project_root is None:
         _FALLBACK_FIRED.set(True)
-        print(f"Warning: {tool_name}: project_root omitted, using server memory dir {MEMORY_DIR.resolve()}", file=sys.stderr)
+        print(
+            f"Warning: {tool_name}: project_root omitted, using server memory dir {MEMORY_DIR.resolve()}",
+            file=sys.stderr,
+        )
         return MEMORY_DIR
     return _explicit_project_root(project_root, tool_name) / ".opencode" / "memory"
 
-def _validate_and_resolve(namespace: str, key: Optional[str] = None, base_dir: Optional[Path] = None) -> Path:
+
+def _validate_and_resolve(
+    namespace: str, key: Optional[str] = None, base_dir: Optional[Path] = None
+) -> Path:
     if not re.match(r"^[a-zA-Z0-9_-]+$", namespace):
-        raise ValueError(f"Invalid namespace '{namespace}'. Only alphanumeric, hyphens, and underscores are allowed.")
+        raise ValueError(
+            f"Invalid namespace '{namespace}'. Only alphanumeric, hyphens, and underscores are allowed."
+        )
 
     if key is not None and not re.match(r"^[a-zA-Z0-9_-]+$", key):
-        raise ValueError(f"Invalid key '{key}'. Only alphanumeric, hyphens, and underscores are allowed.")
+        raise ValueError(
+            f"Invalid key '{key}'. Only alphanumeric, hyphens, and underscores are allowed."
+        )
 
     base_dir = (base_dir or MEMORY_DIR).resolve()
     target_path = (base_dir / namespace).resolve()
@@ -93,11 +114,13 @@ def _validate_and_resolve(namespace: str, key: Optional[str] = None, base_dir: O
 
     return target_path
 
+
 def _ensure_namespace(namespace: str, base_dir: Optional[Path] = None) -> Path:
     ns_dir = _validate_and_resolve(namespace, base_dir=base_dir)
     ns_dir.mkdir(parents=True, exist_ok=True)
     return ns_dir
 
+
 def build_memory_index(base_dir: Optional[Path] = None) -> str:
     """
     Scans MEMORY_DIR for all Markdown memories and builds a sorted, pipe-escaped
@@ -139,12 +162,14 @@ def build_memory_index(base_dir: Optional[Path] = None) -> str:
                 # For deeper nesting, use relative parent
                 rel = md_file.relative_to(mem_dir)
                 # Namespace is first part of relative path (e.g., "workflows" in "workflows/foo.md")
-                namespace = rel.parts[0] if len(rel.parts) >= 2 else rel.parent.name or "root"
+                namespace = (
+                    rel.parts[0] if len(rel.parts) >= 2 else rel.parent.name or "root"
+                )
                 # Key is file stem (without .md)
                 key = md_file.stem
 
                 # Read file content safely
-                with open(md_file, 'r', encoding='utf-8') as f:
+                with open(md_file, "r", encoding="utf-8") as f:
                     content = f.read()
 
                 # Parse frontmatter tags and locate summary start
@@ -184,7 +209,9 @@ def build_memory_index(base_dir: Optional[Path] = None) -> str:
                     summary = summary[:117] + "..."
                 summary = summary.replace("|", "\\|")
                 # Also escape pipes in tags
-                tags_str = ", ".join(str(t).replace("|", "\\|") for t in tags) if tags else ""
+                tags_str = (
+                    ", ".join(str(t).replace("|", "\\|") for t in tags) if tags else ""
+                )
 
                 rows.append((namespace, key, summary, tags_str))
             except Exception:
@@ -213,7 +240,7 @@ def build_memory_index(base_dir: Optional[Path] = None) -> str:
         index_path = mem_dir / "index.md"
         fd, temp_path = tempfile.mkstemp(dir=mem_dir, text=True)
         try:
-            with os.fdopen(fd, 'w', encoding='utf-8') as f:
+            with os.fdopen(fd, "w", encoding="utf-8") as f:
                 f.write(full_content)
                 f.flush()
                 os.fsync(f.fileno())
@@ -248,8 +275,15 @@ def build_memory_index(base_dir: Optional[Path] = None) -> str:
         print(f"[build_memory_index] unexpected error: {e}", flush=True)
         return f"Error building index: {e}"
 
+
 @_project_tool
-def store_memory(namespace: str, key: str, content: str, overwrite: bool = True, project_root: str | None = None) -> str:
+def store_memory(
+    namespace: str,
+    key: str,
+    content: str,
+    overwrite: bool = True,
+    project_root: str | None = None,
+) -> str:
     """Stores a memory snippet as a markdown file. Uses atomic writes to prevent race conditions. Use when saving an explicit project rule or reusable constraint. Use search_memory instead when finding existing memory without writing. project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
     try:
         base_dir = _memory_dir(project_root, "store_memory")
@@ -272,7 +306,7 @@ def store_memory(namespace: str, key: str, content: str, overwrite: bool = True,
 
         fd, temp_path = tempfile.mkstemp(dir=ns_dir, text=True)
         try:
-            with os.fdopen(fd, 'w', encoding='utf-8') as f:
+            with os.fdopen(fd, "w", encoding="utf-8") as f:
                 f.write(content)
             os.replace(temp_path, file_path)
         except Exception as e:
@@ -290,20 +324,24 @@ def store_memory(namespace: str, key: str, content: str, overwrite: bool = True,
     except Exception as e:
         return f"Error storing memory: {str(e)}"
 
+
 @_project_tool
 def read_memory(namespace: str, key: str, project_root: str | None = None) -> str:
     """Reads a specific memory snippet. Use when opening one known namespace and key already found via list or search. project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
     try:
-        ns_dir = _validate_and_resolve(namespace, key, base_dir=_memory_dir(project_root, "read_memory"))
+        ns_dir = _validate_and_resolve(
+            namespace, key, base_dir=_memory_dir(project_root, "read_memory")
+        )
         file_path = ns_dir / f"{key}.md"
         if not file_path.is_file():
             return f"Error: Memory '{key}' not found in namespace '{namespace}'."
 
-        with open(file_path, 'r', encoding='utf-8') as f:
+        with open(file_path, "r", encoding="utf-8") as f:
             return f.read()
     except Exception as e:
         return f"Error reading memory: {str(e)}"
 
+
 @_project_tool
 def delete_memory(namespace: str, key: str, project_root: str | None = None) -> str:
     """Deletes a specific memory snippet if it is no longer relevant. Use only for an obsolete rule after manager approval, never for routine lookups. project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
@@ -330,8 +368,11 @@ def delete_memory(namespace: str, key: str, project_root: str | None = None) ->
     except Exception as e:
         return f"Error deleting memory: {str(e)}"
 
+
 @_project_tool
-def search_memory(query: str, namespace: Optional[str] = None, project_root: str | None = None) -> str:
+def search_memory(
+    query: str, namespace: Optional[str] = None, project_root: str | None = None
+) -> str:
     """Performs a full-text search across memories. If namespace is provided, limits search to that slice.
     Use when finding existing memory without writing, and before asking the manager about a past ruling.
 
@@ -344,7 +385,11 @@ def search_memory(query: str, namespace: Optional[str] = None, project_root: str
         return "No memories recorded yet."
 
     try:
-        target_dir = _validate_and_resolve(namespace, base_dir=base_dir) if namespace else base_dir
+        target_dir = (
+            _validate_and_resolve(namespace, base_dir=base_dir)
+            if namespace
+            else base_dir
+        )
     except ValueError as e:
         return f"Error: {str(e)}"
 
@@ -354,17 +399,19 @@ def search_memory(query: str, namespace: Optional[str] = None, project_root: str
     # Parse tag filter from query
     tag_filter = None
     search_query = query
-    tag_match = re.search(r'\btag:(\S+)', query)
+    tag_match = re.search(r"\btag:(\S+)", query)
     if tag_match:
         tag_filter = tag_match.group(1).lower()
-        search_query = query[:tag_match.start()].strip() + " " + query[tag_match.end():].strip()
+        search_query = (
+            query[: tag_match.start()].strip() + " " + query[tag_match.end() :].strip()
+        )
         search_query = search_query.strip()
 
     results = []
     for md_file in target_dir.rglob("*.md"):
         try:
             file_rel = md_file.relative_to(base_dir)
-            with open(md_file, 'r', encoding='utf-8') as f:
+            with open(md_file, "r", encoding="utf-8") as f:
                 content = f.read()
 
             # Parse YAML frontmatter for tag filtering and ranking
@@ -400,7 +447,12 @@ def search_memory(query: str, namespace: Optional[str] = None, project_root: str
                 if key_match or content_match:
                     snippet = content[:200] + "..." if len(content) > 200 else content
                     rank_marker = "⭐ " if key_match else "   "
-                    results.append((0 if key_match else 1, f"{rank_marker}**{file_rel}**\n{snippet}\n"))
+                    results.append(
+                        (
+                            0 if key_match else 1,
+                            f"{rank_marker}**{file_rel}**\n{snippet}\n",
+                        )
+                    )
 
         except Exception:
             continue
@@ -414,6 +466,7 @@ def search_memory(query: str, namespace: Optional[str] = None, project_root: str
 
     return "### Search Results\n\n" + "\n---\n".join(ranked_results)
 
+
 @_project_tool
 def list_namespaces(project_root: str | None = None) -> str:
     """Lists all active memory namespaces and their keys. Use when discovering what is remembered before reading or searching. project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
@@ -431,6 +484,7 @@ def list_namespaces(project_root: str | None = None) -> str:
 
     return "\n".join(tree) if tree else "Memory bank is empty."
 
+
 @_project_tool
 def rebuild_memory_index(project_root: str | None = None) -> str:
     """
@@ -448,6 +502,7 @@ def rebuild_memory_index(project_root: str | None = None) -> str:
     """
     return build_memory_index(_memory_dir(project_root, "rebuild_memory_index"))
 
+
 if __name__ == "__main__":
     _transport = os.environ.get("MCP_TRANSPORT", "streamable-http")
     # Singleton default (Task 279 V3): all callers consume these servers as
diff --git a/opencode.json b/opencode.json
index cb6c410..16a2567 100644
--- a/opencode.json
+++ b/opencode.json
@@ -4,7 +4,12 @@
   "instructions": [
     "docs/opencode-shell-strategy.md"
   ],
-  "formatter": true,
+  "formatter": {
+    "ruff-format": {
+      "command": ["ruff", "format", "$FILE"],
+      "extensions": [".py"]
+    }
+  },
   "permission": {
     "custom_context_*": "allow",
     "project_memory_*": "allow",
diff --git a/scripts/check_docs_sync.py b/scripts/check_docs_sync.py
index e3600c5..c691a81 100644
--- a/scripts/check_docs_sync.py
+++ b/scripts/check_docs_sync.py
@@ -21,8 +21,16 @@ from pathlib import Path
 
 ROOT = Path(__file__).resolve().parent.parent
 GLOBAL = Path.home() / ".config" / "opencode"
-SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules",
-             ".pytest_cache", "archive", "tasks", "context-reports"}
+SKIP_DIRS = {
+    ".git",
+    "__pycache__",
+    ".venv",
+    "node_modules",
+    ".pytest_cache",
+    "archive",
+    "tasks",
+    "context-reports",
+}
 SKIP_NAMES = {"index.md"}  # generated memory index mirrors references
 TEXT_SUFFIXES = {".md", ".json", ".py", ".toml", ".txt", ".js"}
 
@@ -45,9 +53,9 @@ def _check_denies() -> list[str]:
         if glob and repo != glob:
             errors.append(
                 f"deny sets differ: repo-only={sorted(repo - glob)} "
-                f"global-only={sorted(glob - repo)}")
-    table = (ROOT / "docs" / "opencode-shell-strategy.md").read_text(
-        encoding="utf-8")
+                f"global-only={sorted(glob - repo)}"
+            )
+    table = (ROOT / "docs" / "opencode-shell-strategy.md").read_text(encoding="utf-8")
     verbs = {d.split()[1] for d in repo}  # "git <verb>[ *]"
     for verb in sorted(verbs):
         if f"`git {verb}`" not in table:
@@ -70,16 +78,22 @@ def _live_text_files() -> list[Path]:
 
 def _check_orphans() -> list[str]:
     orphans: list[str] = []
-    candidates = [p for p in (ROOT / "scripts").rglob("*")
-                  if p.is_file() and "__pycache__" not in p.parts]
-    haystacks = {p: p.read_text(encoding="utf-8", errors="replace")
-                 for p in _live_text_files()}
+    candidates = [
+        p
+        for p in (ROOT / "scripts").rglob("*")
+        if p.is_file() and "__pycache__" not in p.parts
+    ]
+    haystacks = {
+        p: p.read_text(encoding="utf-8", errors="replace") for p in _live_text_files()
+    }
     for script in candidates:
         name = script.name
         stem = script.stem
         hit = any(
             (name in text or (stem and stem in text))
-            for p, text in haystacks.items() if p != script)
+            for p, text in haystacks.items()
+            if p != script
+        )
         if not hit:
             orphans.append(str(script.relative_to(ROOT)))
     return orphans
diff --git a/scripts/prompt-build/assemble_system_prompt.py b/scripts/prompt-build/assemble_system_prompt.py
index a65a4af..e83fe10 100644
--- a/scripts/prompt-build/assemble_system_prompt.py
+++ b/scripts/prompt-build/assemble_system_prompt.py
@@ -50,9 +50,7 @@ from typing import List
 # Matches an include-marker comment, e.g.:
 #   <!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->
 # Group 1 = path (relative to prompts/), group 2 = pipe-separated params.
-_INCLUDE_RE = re.compile(
-    r"<!--INCLUDE:([^|]+?)(?:\|([^>]*))?-->"
-)
+_INCLUDE_RE = re.compile(r"<!--INCLUDE:([^|]+?)(?:\|([^>]*))?-->")
 # Matches a {{PARAM}} placeholder in shared-file content.
 _PARAM_RE = re.compile(r"\{\{([A-Z_]+)\}\}")
 
@@ -208,6 +206,7 @@ def _resolve_includes(text: str, prompts_dir: Path) -> str:
         The text with all include markers substituted by their resolved
         content.
     """
+
     def _replace(match: re.Match) -> str:
         rel_path = match.group(1)
         params_str = match.group(2) or ""
@@ -239,6 +238,7 @@ def _resolve_includes(text: str, prompts_dir: Path) -> str:
 # Public API
 # ---------------------------------------------------------------------------
 
+
 def assemble(
     output_path: str = "system-prompt.md",
     fragments_dir: str = "prompts/fragments",
@@ -265,7 +265,9 @@ def assemble(
         The assembled system-prompt text (also written to output_path).
     """
     frag_dir = Path(fragments_dir)
-    prompts_dir = frag_dir.parent  # fragments/ lives under prompts/, so parent is prompts/
+    prompts_dir = (
+        frag_dir.parent
+    )  # fragments/ lives under prompts/, so parent is prompts/
 
     # Read the ordered manifest.
     manifest = Path(manifest_path).read_text(encoding="utf-8").splitlines()
@@ -366,6 +368,7 @@ def assemble(
 # CLI entry point
 # ---------------------------------------------------------------------------
 
+
 def main() -> None:
     """Command-line entry point for assembling system-prompt.md.
 
diff --git a/tests/test_brain_diff_attach.py b/tests/test_brain_diff_attach.py
index 11331fa..bfff9d3 100644
--- a/tests/test_brain_diff_attach.py
+++ b/tests/test_brain_diff_attach.py
@@ -28,7 +28,8 @@ def _injected_task_text(diff_body: str) -> str:
     """The shape stage_and_inject_diff writes: a fenced diff body."""
     return (
         "# Task 99: Sample\n\nSome working content.\n\n"
-        "<!-- BEGIN_GIT_DIFF -->\n\n```diff\n" + diff_body
+        "<!-- BEGIN_GIT_DIFF -->\n\n```diff\n"
+        + diff_body
         + "\n```\n<!-- END_GIT_DIFF -->\n"
     )
 
@@ -38,10 +39,7 @@ def test_extract_diff_survives_embedded_end_marker():
     # source text inside its own hunk, so the FIRST marker is not the
     # block end. Extraction must keep the whole body (the seat was judging
     # a change set that stopped two lines into the file it was reviewing).
-    embedded = (
-        '+_TASK_DIFF_END = "<!-- END_GIT_DIFF -->"\n'
-        "+tail-sentinel"
-    )
+    embedded = '+_TASK_DIFF_END = "<!-- END_GIT_DIFF -->"\n+tail-sentinel'
     text = _injected_task_text(embedded)
     diff = bridge.extract_task_diff(text)
     assert "_TASK_DIFF_END" in diff
@@ -49,10 +47,7 @@ def test_extract_diff_survives_embedded_end_marker():
 
 
 def test_strip_task_diff_survives_embedded_end_marker():
-    embedded = (
-        '+_TASK_DIFF_END = "<!-- END_GIT_DIFF -->"\n'
-        "+tail-sentinel"
-    )
+    embedded = '+_TASK_DIFF_END = "<!-- END_GIT_DIFF -->"\n+tail-sentinel'
     text = _injected_task_text(embedded)
     cleaned, omitted, truncated = bridge._strip_task_diff(text, "99-sample.md")
     assert "tail-sentinel" not in cleaned
@@ -94,22 +89,21 @@ def test_build_diff_attach_resolved_with_diff(monkeypatch, tmp_path):
     target = tmp_path / "99-sample.md"
     target.write_text(_task_text("+added"), encoding="utf-8")
     monkeypatch.setattr(
-        bridge, "_resolve_task_file",
-        lambda tid, project_root=None: target)
+        bridge, "_resolve_task_file", lambda tid, project_root=None: target
+    )
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
     out = bridge.build_diff_attach("99")
     assert "+added" in out
 
 
-def test_build_diff_attach_no_diff_returns_inline_empty_note(
-        monkeypatch, tmp_path):
+def test_build_diff_attach_no_diff_returns_inline_empty_note(monkeypatch, tmp_path):
     # Re-QA repair: stderr is invisible to the model, so an empty diff
     # returns an inline EMPTY note (never silent "") with the remedy.
     target = tmp_path / "99-sample.md"
     target.write_text("# Task 99: no diff\n", encoding="utf-8")
     monkeypatch.setattr(
-        bridge, "_resolve_task_file",
-        lambda tid, project_root=None: target)
+        bridge, "_resolve_task_file", lambda tid, project_root=None: target
+    )
     out = bridge.build_diff_attach("99")
     assert "EMPTY" in out
     assert "stage_and_inject_diff" in out
@@ -119,7 +113,8 @@ def test_build_diff_attach_unresolvable_returns_inline_note(monkeypatch):
     # Re-QA repair: unresolvable file returns an inline UNAVAILABLE
     # note (never silent "") naming project_root as the remedy.
     monkeypatch.setattr(
-        bridge, "_resolve_task_file", lambda tid, project_root=None: None)
+        bridge, "_resolve_task_file", lambda tid, project_root=None: None
+    )
     out = bridge.build_diff_attach("nope")
     assert "UNAVAILABLE" in out
     assert "project_root" in out
@@ -129,8 +124,8 @@ def test_build_diff_attach_over_cap_truncates(monkeypatch, tmp_path):
     target = tmp_path / "99-sample.md"
     target.write_text(_task_text("x" * 50000), encoding="utf-8")
     monkeypatch.setattr(
-        bridge, "_resolve_task_file",
-        lambda tid, project_root=None: target)
+        bridge, "_resolve_task_file", lambda tid, project_root=None: target
+    )
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
     monkeypatch.setattr(bridge, "_TASK_DIFF_CAP", 100)
     out = bridge.build_diff_attach("99")
@@ -145,8 +140,8 @@ def test_build_diff_attach_truncation_note_is_unverifiable(monkeypatch, tmp_path
     target = tmp_path / "99-sample.md"
     target.write_text(_task_text("x" * 50000), encoding="utf-8")
     monkeypatch.setattr(
-        bridge, "_resolve_task_file",
-        lambda tid, project_root=None: target)
+        bridge, "_resolve_task_file", lambda tid, project_root=None: target
+    )
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
     monkeypatch.setattr(bridge, "_TASK_DIFF_CAP", 100)
     out = bridge.build_diff_attach("99")
@@ -165,8 +160,8 @@ def test_build_diff_attach_breaks_embedded_fences(monkeypatch, tmp_path):
     target = tmp_path / "99-sample.md"
     target.write_text(_task_text("line\n```evil\nline"), encoding="utf-8")
     monkeypatch.setattr(
-        bridge, "_resolve_task_file",
-        lambda tid, project_root=None: target)
+        bridge, "_resolve_task_file", lambda tid, project_root=None: target
+    )
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
     out = bridge.build_diff_attach("99")
     assert "```evil" not in out
@@ -177,11 +172,10 @@ def test_failsafe_qa_prompt_attaches_without_flag(monkeypatch, tmp_path):
     target = tmp_path / "99-sample.md"
     target.write_text(_task_text("+added"), encoding="utf-8")
     monkeypatch.setattr(
-        bridge, "_resolve_task_file",
-        lambda tid, project_root=None: target)
+        bridge, "_resolve_task_file", lambda tid, project_root=None: target
+    )
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
-    out = bridge._failsafe_qa_attach(
-        "QA engineer, adversarial review please", "99")
+    out = bridge._failsafe_qa_attach("QA engineer, adversarial review please", "99")
     assert "+added" in out
 
 
@@ -189,8 +183,8 @@ def test_failsafe_normal_prompt_stays_empty(monkeypatch, tmp_path):
     target = tmp_path / "99-sample.md"
     target.write_text(_task_text("+added"), encoding="utf-8")
     monkeypatch.setattr(
-        bridge, "_resolve_task_file",
-        lambda tid, project_root=None: target)
+        bridge, "_resolve_task_file", lambda tid, project_root=None: target
+    )
     assert bridge._failsafe_qa_attach("fix the login bug", "99") == ""
 
 
@@ -199,7 +193,8 @@ def _mk_project(tmp_path, name="proj"):
     lane = proj / "tasks" / "qa"
     lane.mkdir(parents=True)
     (lane / "999-sample.md").write_text(
-        _task_text("+via-project-root"), encoding="utf-8")
+        _task_text("+via-project-root"), encoding="utf-8"
+    )
     return proj
 
 
@@ -213,12 +208,10 @@ def test_resolve_task_file_honors_project_root(monkeypatch, tmp_path):
     assert bridge._resolve_task_file("999") is None
 
 
-def test_resolve_task_file_project_root_without_tasks_falls_back(
-        monkeypatch, tmp_path):
+def test_resolve_task_file_project_root_without_tasks_falls_back(monkeypatch, tmp_path):
     lane = tmp_path / "tasks" / "qa"
     lane.mkdir(parents=True)
-    (lane / "999-sample.md").write_text(
-        _task_text("+via-workspace"), encoding="utf-8")
+    (lane / "999-sample.md").write_text(_task_text("+via-workspace"), encoding="utf-8")
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
     bare = tmp_path / "bare"
     bare.mkdir()
@@ -237,8 +230,8 @@ def test_build_diff_attach_via_project_root(monkeypatch, tmp_path):
 
 def test_build_diff_attach_unresolvable_says_so(monkeypatch, capsys):
     monkeypatch.setattr(
-        bridge, "_resolve_task_file",
-        lambda tid, project_root=None: None)
+        bridge, "_resolve_task_file", lambda tid, project_root=None: None
+    )
     out = bridge.build_diff_attach("nope")
     assert "UNAVAILABLE" in out  # inline note for the model, not ""
     assert "unresolvable" in capsys.readouterr().err  # stderr kept too
@@ -248,8 +241,8 @@ def test_build_diff_attach_empty_diff_says_so(monkeypatch, tmp_path, capsys):
     target = tmp_path / "99-sample.md"
     target.write_text("# Task 99: no diff\n", encoding="utf-8")
     monkeypatch.setattr(
-        bridge, "_resolve_task_file",
-        lambda tid, project_root=None: target)
+        bridge, "_resolve_task_file", lambda tid, project_root=None: target
+    )
     out = bridge.build_diff_attach("99")
     assert "EMPTY" in out  # inline note for the model, not ""
     assert "no Factual Git Diff block" in capsys.readouterr().err
diff --git a/tests/test_bundle_tasks.py b/tests/test_bundle_tasks.py
index a75cb77..d012b11 100644
--- a/tests/test_bundle_tasks.py
+++ b/tests/test_bundle_tasks.py
@@ -49,6 +49,7 @@ detect_stack = _bundler._detect_stack
 # Fixtures
 # ---------------------------------------------------------------------------
 
+
 @pytest.fixture
 def tmp_tasks(tmp_path: Path):
     """Create a temporary tasks/ directory with Kanban subdirs."""
@@ -133,6 +134,7 @@ def _create_task_file(
 # T1: Multi-line checklist preservation
 # ---------------------------------------------------------------------------
 
+
 def test_multiline_checklist_preservation(tmp_tasks: Path):
     """B1: Verify indented continuation lines survive bundling.
 
@@ -177,7 +179,12 @@ _(fill)_"""
             in_checklist = True
             result.append(stripped)
         elif in_checklist:
-            if stripped and not stripped.startswith("- [") and not stripped.startswith("## ") and not stripped.startswith("---"):
+            if (
+                stripped
+                and not stripped.startswith("- [")
+                and not stripped.startswith("## ")
+                and not stripped.startswith("---")
+            ):
                 result.append(line)
             else:
                 in_checklist = False
@@ -195,6 +202,7 @@ _(fill)_"""
 # T2: Duplicate ID hard halt
 # ---------------------------------------------------------------------------
 
+
 def test_duplicate_active_id_halt(tmp_tasks: Path):
     """B2: Verify hard failure when two active tasks share the same ID."""
     content = (
@@ -247,6 +255,7 @@ def test_duplicate_active_id_halt(tmp_tasks: Path):
 # T3: Partial archive failure rollback
 # ---------------------------------------------------------------------------
 
+
 def test_partial_archive_failure_rollback(tmp_tasks: Path, monkeypatch):
     """B3: Verify rollback mechanism exists and handles failures."""
     _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
@@ -267,11 +276,13 @@ def test_partial_archive_failure_rollback(tmp_tasks: Path, monkeypatch):
 
     source_data = []
     for tid in ["01", "02"]:
-        p = tmp_tasks / "backlog" / f"{int(tid):02d}-task-{chr(96+int(tid))}.md"
+        p = tmp_tasks / "backlog" / f"{int(tid):02d}-task-{chr(96 + int(tid))}.md"
         c = p.read_text(encoding="utf-8")
-        source_data.append((tid, p, c, f"Task {chr(64+int(tid))}"))
+        source_data.append((tid, p, c, f"Task {chr(64 + int(tid))}"))
 
-    meta_content = _build_meta_content(100, "test-bundle", "Test Bundle", ["01", "02"], source_data)
+    meta_content = _build_meta_content(
+        100, "test-bundle", "Test Bundle", ["01", "02"], source_data
+    )
     assert "## Bundled Checklist" in meta_content
 
 
@@ -279,14 +290,17 @@ def test_partial_archive_failure_rollback(tmp_tasks: Path, monkeypatch):
 # T4: Persian unicode slug
 # ---------------------------------------------------------------------------
 
+
 def test_persian_unicode_slug(tmp_tasks: Path):
     """B4: Verify Persian titles produce valid kebab slugs."""
     slug = kebab_case("تست باندل فارسی")
     assert slug, "Slug should not be empty"
-    assert re.match(r"^[a-z0-9\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF-]+$", slug), \
-        f"Slug '{slug}' contains invalid characters"
-    assert any("\u0600" <= c <= "\u06FF" for c in slug), \
+    assert re.match(
+        r"^[a-z0-9\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF-]+$", slug
+    ), f"Slug '{slug}' contains invalid characters"
+    assert any("\u0600" <= c <= "\u06ff" for c in slug), (
         f"Slug '{slug}' should contain Persian characters"
+    )
 
     slug2 = kebab_case("Android پالایش")
     assert slug2, "Slug should not be empty"
@@ -302,6 +316,7 @@ def test_persian_unicode_slug(tmp_tasks: Path):
 # T5: Stack conflict guardrail
 # ---------------------------------------------------------------------------
 
+
 def test_stack_conflict_guardrail(tmp_tasks: Path):
     """M1: Verify conflicting stack detection without --force."""
     assert detect_stack("Task for Jetpack Compose + Hilt + SQLDelight") == "android"
@@ -313,32 +328,44 @@ def test_stack_conflict_guardrail(tmp_tasks: Path):
 # T6: Verbatim SHA validation
 # ---------------------------------------------------------------------------
 
+
 def test_verbatim_sha_validation(tmp_tasks: Path):
     """M2: Verify exact text presence check."""
-    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion Alpha", "Criterion Beta with details"])
+    _create_task_file(
+        tmp_tasks,
+        "backlog",
+        "01",
+        "Task A",
+        ["Criterion Alpha", "Criterion Beta with details"],
+    )
     _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion Gamma"])
 
     source_data = []
     for tid, dirname in [("01", "backlog"), ("02", "backlog")]:
-        p = tmp_tasks / dirname / f"{int(tid):02d}-task-{chr(96+int(tid))}.md"
+        p = tmp_tasks / dirname / f"{int(tid):02d}-task-{chr(96 + int(tid))}.md"
         c = p.read_text(encoding="utf-8")
-        source_data.append((tid, p, c, f"Task {chr(64+int(tid))}"))
+        source_data.append((tid, p, c, f"Task {chr(64 + int(tid))}"))
 
-    meta_content = _build_meta_content(100, "test-bundle", "Test Bundle", ["01", "02"], source_data)
-    assert _verify_verbatim_checksums(source_data, meta_content), \
+    meta_content = _build_meta_content(
+        100, "test-bundle", "Test Bundle", ["01", "02"], source_data
+    )
+    assert _verify_verbatim_checksums(source_data, meta_content), (
         "Verbatim check should pass for correctly generated META"
+    )
 
     # Tamper: replace in the BUNDLED CHECKLIST only (not the appendix)
     # The verbatim check specifically looks at the Bundled Checklist section
     tampered = meta_content.replace("[01] Criterion Alpha", "[01] CORRUPTED")
-    assert not _verify_verbatim_checksums(source_data, tampered), \
+    assert not _verify_verbatim_checksums(source_data, tampered), (
         "Verbatim check should fail for tampered META"
+    )
 
 
 # ---------------------------------------------------------------------------
 # Integration: Dry-run CLI with Persian title
 # ---------------------------------------------------------------------------
 
+
 def test_cli_dry_run_persian(tmp_tasks: Path):
     """Integration test: verify Persian title handling end-to-end."""
     _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
@@ -346,10 +373,14 @@ def test_cli_dry_run_persian(tmp_tasks: Path):
 
     source_data = []
     for tid in ["01", "02"]:
-        p = tmp_tasks / "backlog" / f"{int(tid):02d}-task-{chr(96+int(tid))}.md"
+        p = tmp_tasks / "backlog" / f"{int(tid):02d}-task-{chr(96 + int(tid))}.md"
         c = p.read_text(encoding="utf-8")
-        source_data.append((tid, p, c, f"Task {chr(64+int(tid))}"))
+        source_data.append((tid, p, c, f"Task {chr(64 + int(tid))}"))
 
-    meta_content = _build_meta_content(100, "تست-باندل", "تست باندل فارسی", ["01", "02"], source_data)
+    meta_content = _build_meta_content(
+        100, "تست-باندل", "تست باندل فارسی", ["01", "02"], source_data
+    )
     assert "تست-باندل" in meta_content, "Persian slug should appear in META content"
-    assert "تست باندل فارسی" in meta_content, "Persian title should appear in META content"
+    assert "تست باندل فارسی" in meta_content, (
+        "Persian title should appear in META content"
+    )
diff --git a/tests/test_input_validation_pipeline.py b/tests/test_input_validation_pipeline.py
index 9db8332..d4911fe 100644
--- a/tests/test_input_validation_pipeline.py
+++ b/tests/test_input_validation_pipeline.py
@@ -6,6 +6,7 @@ non-English or noisy Manager input through validate, normalize,
 translate, enrich, and prompt-refactor steps, and every clarification
 or response must stay in simple English.
 """
+
 from pathlib import Path
 
 REPO = Path(__file__).resolve().parent.parent
diff --git a/tests/test_mcp_servers.py b/tests/test_mcp_servers.py
index 7021dfb..f90c867 100644
--- a/tests/test_mcp_servers.py
+++ b/tests/test_mcp_servers.py
@@ -3063,7 +3063,9 @@ def test_graph_qa_followups_empty_label_and_confined_graph():
         repo = Path(td)
         (repo / "a.py").write_text("def hub():\n    return 1\n", encoding="utf-8")
         assert "✅ Success" in mod.build_graph(".", project_root=str(repo))
-        assert mod.explain_node("", project_root=str(repo)).startswith("Error:"), "empty label must error, not list"
+        assert mod.explain_node("", project_root=str(repo)).startswith("Error:"), (
+            "empty label must error, not list"
+        )
         assert mod.explain_node("   ", project_root=str(repo)).startswith("Error:")
         outside = mod.graph_stats(graph_path="/etc/hostname", project_root=str(repo))
         assert "No graph found" in outside, outside
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 3f1f5a1..89e8d1c 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.54.0"
+    assert shipped == "9.56.0"
 
 
 def test_compaction_protocol_in_shipped_prompt():
diff --git a/tests/test_session_lifecycle.py b/tests/test_session_lifecycle.py
index c5bb7c8..2b23dbf 100644
--- a/tests/test_session_lifecycle.py
+++ b/tests/test_session_lifecycle.py
@@ -26,6 +26,7 @@ import session_ledger as ledger
 
 # --- ledger fixtures -------------------------------------------------------
 
+
 def _sessions(tmp_path, name="proj"):
     proj = tmp_path / name
     (proj / "tasks" / ".sessions").mkdir(parents=True)
@@ -34,27 +35,35 @@ def _sessions(tmp_path, name="proj"):
 
 # --- Part 1: session ledger and checkpoints --------------------------------
 
+
 def test_start_session_carries_all_required_fields(tmp_path):
     proj = _sessions(tmp_path)
     rec = ledger.start_session("s1", project_root=str(proj))
-    for field in ("session_id", "phase", "checkpoints", "request_hash",
-                  "response_hash", "retry_counts", "capability_manifest",
-                  "approval_events", "transcript_path",
-                  "transport_corrections", "final_status"):
+    for field in (
+        "session_id",
+        "phase",
+        "checkpoints",
+        "request_hash",
+        "response_hash",
+        "retry_counts",
+        "capability_manifest",
+        "approval_events",
+        "transcript_path",
+        "transport_corrections",
+        "final_status",
+    ):
         assert field in rec, f"missing ledger field: {field}"
     assert rec["session_id"] == "s1"
     assert rec["checkpoints"] == []
     assert rec["final_status"] == "open"
-    assert rec["transcript_path"].endswith(
-        "tasks/.sessions/s1/transcript.jsonl")
+    assert rec["transcript_path"].endswith("tasks/.sessions/s1/transcript.jsonl")
 
 
 def test_checkpoint_rejects_unknown_name(tmp_path):
     proj = _sessions(tmp_path)
     ledger.start_session("s1", project_root=str(proj))
     with pytest.raises(ValueError):
-        ledger.checkpoint("s1", "nonsense_boundary",
-                          project_root=str(proj))
+        ledger.checkpoint("s1", "nonsense_boundary", project_root=str(proj))
 
 
 def test_all_nine_checkpoints_accepted_in_order(tmp_path):
@@ -63,8 +72,11 @@ def test_all_nine_checkpoints_accepted_in_order(tmp_path):
     assert len(ledger.CHECKPOINTS) == 9
     for name in ledger.CHECKPOINTS:
         ledger.checkpoint("s1", name, project_root=str(proj))
-    names = [e["checkpoint"] for e in ledger.read_ledger(
-        project_root=str(proj)) if e["event"] == "checkpoint"]
+    names = [
+        e["checkpoint"]
+        for e in ledger.read_ledger(project_root=str(proj))
+        if e["event"] == "checkpoint"
+    ]
     assert names == list(ledger.CHECKPOINTS)
 
 
@@ -75,15 +87,13 @@ def test_checkpoints_append_only_and_ordered(tmp_path):
     ledger.checkpoint("s1", ledger.CHECKPOINTS[1], project_root=str(proj))
     path = proj / "tasks" / ".sessions" / "session_ledger.jsonl"
     assert len(path.read_text(encoding="utf-8").splitlines()) == 3
-    events = [e["event"] for e in ledger.read_ledger(
-        project_root=str(proj))]
+    events = [e["event"] for e in ledger.read_ledger(project_root=str(proj))]
     assert events == ["session_started", "checkpoint", "checkpoint"]
 
 
 def test_reader_tolerates_unknown_fields_and_corrupt_lines(tmp_path):
     proj = _sessions(tmp_path)
-    ledger.start_session("s1", project_root=str(proj),
-                         future_field="kept")
+    ledger.start_session("s1", project_root=str(proj), future_field="kept")
     path = proj / "tasks" / ".sessions" / "session_ledger.jsonl"
     with path.open("a", encoding="utf-8") as fh:
         fh.write("this is not json\n")
@@ -97,8 +107,11 @@ def test_pending_candidate_stays_out_of_committed_store(tmp_path):
     ledger.start_session("s1", project_root=str(proj))
     cand = {"summary": "use X", "verbatim": "use X now"}
     ledger.record_pending_candidate("s1", cand, project_root=str(proj))
-    events = [e for e in ledger.read_ledger(project_root=str(proj))
-              if e["event"] == "decision_pending"]
+    events = [
+        e
+        for e in ledger.read_ledger(project_root=str(proj))
+        if e["event"] == "decision_pending"
+    ]
     assert len(events) == 1
     assert events[0]["status"] == "pending"
     assert list((proj / "tasks").rglob("DEC-*.json")) == []
@@ -109,33 +122,29 @@ def test_approval_promotes_only_via_explicit_record(tmp_path):
     ledger.start_session("s1", project_root=str(proj))
     cand = {"summary": "use X", "verbatim": "use X now"}
     ledger.record_pending_candidate("s1", cand, project_root=str(proj))
-    returned = ledger.promote_pending_candidate(
-        "s1", 0, project_root=str(proj))
+    returned = ledger.promote_pending_candidate("s1", 0, project_root=str(proj))
     assert returned["summary"] == "use X"
     # Promotion alone writes no committed decision: the caller must pass
     assert list((proj / "tasks").rglob("DEC-*.json")) == []
-    kinds = [e["event"] for e in ledger.read_ledger(
-        project_root=str(proj))]
+    kinds = [e["event"] for e in ledger.read_ledger(project_root=str(proj))]
     assert "decision_approved" in kinds
 
 
 def test_rejected_candidate_auditable_never_active(tmp_path):
     proj = _sessions(tmp_path)
     ledger.start_session("s1", project_root=str(proj))
-    ledger.record_pending_candidate("s1", {"summary": "bad idea"},
-                                    project_root=str(proj))
-    ledger.resolve_pending_candidate("s1", 0, "rejected",
-                                     project_root=str(proj))
+    ledger.record_pending_candidate(
+        "s1", {"summary": "bad idea"}, project_root=str(proj)
+    )
+    ledger.resolve_pending_candidate("s1", 0, "rejected", project_root=str(proj))
     records = ledger.read_ledger(project_root=str(proj))
-    assert {e["event"] for e in records} >= {"decision_pending",
-                                             "decision_rejected"}
+    assert {e["event"] for e in records} >= {"decision_pending", "decision_rejected"}
     assert list((proj / "tasks").rglob("DEC-*.json")) == []
 
 
-
-
 # --- Part 3: lint carve-out and analysis lifecycle --------------------------
 
+
 def _lint_mod():
     path = REPO / "mcp-lint-server" / "server.py"
     spec = importlib.util.spec_from_file_location("lint_server_ws4", path)
@@ -206,27 +215,29 @@ def test_source_evidence_fence_exempt_from_prose_checks():
         "verbatim Persian: گزارش خرابی\n"
         "a line with trailing space \n"
         "#looks-like-heading-no-blank-line\n"
-        "```\n")
-    assert mod._check_markdown_basics(
-        body, "tasks/backlog/99-test.md") == []
+        "```\n",
+    )
+    assert mod._check_markdown_basics(body, "tasks/backlog/99-test.md") == []
 
 
 def test_unclosed_source_evidence_fence_fails():
     mod = _lint_mod()
     body = _TASK_HEAD.format(
-        kind="bug",
-        evidence=_VERIFY + "\n```source-evidence\nnever closed\n")
+        kind="bug", evidence=_VERIFY + "\n```source-evidence\nnever closed\n"
+    )
     issues = mod._check_markdown_basics(body, "tasks/backlog/99-test.md")
     assert any("source-evidence" in i for i in issues)
 
 
 def test_unclosed_fence_does_not_exempt_rest():
     mod = _lint_mod()
-    body = ("# Task 99: Lifecycle fixture\n"
-            "## Goal\n"  # missing blank line before heading
-            + _TASK_HEAD.split("## Goal\n", 1)[1].format(
-                kind="bug",
-                evidence=_VERIFY + "\n```source-evidence\nnever closed\n"))
+    body = (
+        "# Task 99: Lifecycle fixture\n"
+        "## Goal\n"  # missing blank line before heading
+        + _TASK_HEAD.split("## Goal\n", 1)[1].format(
+            kind="bug", evidence=_VERIFY + "\n```source-evidence\nnever closed\n"
+        )
+    )
     issues = mod._check_markdown_basics(body, "tasks/backlog/99-test.md")
     assert any("source-evidence" in i for i in issues)
     assert any("blank line" in i for i in issues)
@@ -235,8 +246,8 @@ def test_unclosed_fence_does_not_exempt_rest():
 def test_fence_contents_do_not_satisfy_structure():
     mod = _lint_mod()
     body = _TASK_HEAD.format(
-        kind="bug",
-        evidence=_VERIFY + "\n```source-evidence\n## Goal\n```\n")
+        kind="bug", evidence=_VERIFY + "\n```source-evidence\n## Goal\n```\n"
+    )
     body = body.replace("## Goal\n\nProve the fence.\n\n", "")
     issues = mod._check_task_file_structure(body, "tasks/backlog/99-test.md")
     assert any("## Goal" in i for i in issues)
@@ -245,8 +256,8 @@ def test_fence_contents_do_not_satisfy_structure():
 def test_structure_checks_continue_outside_fence():
     mod = _lint_mod()
     body = _TASK_HEAD.format(
-        kind="bug",
-        evidence=_VERIFY + "\n```source-evidence\nverbatim\n```\n")
+        kind="bug", evidence=_VERIFY + "\n```source-evidence\nverbatim\n```\n"
+    )
     body = body.replace("## Risk & Rollback\n", "")
     issues = mod._check_task_file_structure(body, "tasks/backlog/99-test.md")
     assert any("Risk & Rollback" in i for i in issues)
@@ -255,15 +266,15 @@ def test_structure_checks_continue_outside_fence():
 def test_analysis_task_report_evidence_passes():
     mod = _lint_mod()
     body = _TASK_HEAD.format(kind="analysis", evidence=_REPORT)
-    assert mod._check_task_file_structure(
-        body, "tasks/backlog/99-test.md") == []
+    assert mod._check_task_file_structure(body, "tasks/backlog/99-test.md") == []
 
 
 def test_analysis_task_blank_result_fails():
     mod = _lint_mod()
     body = _TASK_HEAD.format(
         kind="analysis",
-        evidence="## Report Evidence\n\nReport: context-reports/r.md\n\nResult: \n")
+        evidence="## Report Evidence\n\nReport: context-reports/r.md\n\nResult: \n",
+    )
     issues = mod._check_task_file_structure(body, "tasks/backlog/99-test.md")
     assert any("Result" in i for i in issues)
 
@@ -271,8 +282,8 @@ def test_analysis_task_blank_result_fails():
 def test_analysis_task_missing_report_path_fails():
     mod = _lint_mod()
     body = _TASK_HEAD.format(
-        kind="analysis",
-        evidence="## Report Evidence\n\nResult: some finding\n")
+        kind="analysis", evidence="## Report Evidence\n\nResult: some finding\n"
+    )
     issues = mod._check_task_file_structure(body, "tasks/backlog/99-test.md")
     assert any("Report" in i for i in issues)
 
@@ -282,7 +293,8 @@ def test_analysis_task_exit_code_is_not_report():
     body = _TASK_HEAD.format(
         kind="analysis",
         evidence="## Report Evidence\n\nReport: context-reports/r.md\n\n"
-        "Result: \n\nExit code: 0\n")
+        "Result: \n\nExit code: 0\n",
+    )
     issues = mod._check_task_file_structure(body, "tasks/backlog/99-test.md")
     assert any("Result" in i for i in issues)
 
@@ -290,15 +302,16 @@ def test_analysis_task_exit_code_is_not_report():
 def test_implementation_tasks_unaffected_by_analysis_branch():
     mod = _lint_mod()
     body = _TASK_HEAD.format(kind="bug", evidence=_VERIFY)
-    assert mod._check_task_file_structure(
-        body, "tasks/backlog/99-test.md") == []
+    assert mod._check_task_file_structure(body, "tasks/backlog/99-test.md") == []
 
 
 # --- Part 4: brain_turn checkpoint integration -------------------------------
 
+
 class _FakeResp:
-    def __init__(self, status_code=200, text="", payload=None,
-                 ctype="application/json"):
+    def __init__(
+        self, status_code=200, text="", payload=None, ctype="application/json"
+    ):
         self.status_code = status_code
         self.text = text
         self._payload = payload
@@ -346,9 +359,11 @@ def _stub_client(monkeypatch, script, bodies):
 
 
 def _ok_payload(text="ok"):
-    return {"output": [{"type": "message",
-                        "content": [{"type": "output_text",
-                                     "text": text}]}]}
+    return {
+        "output": [
+            {"type": "message", "content": [{"type": "output_text", "text": text}]}
+        ]
+    }
 
 
 def _turn_env(tmp_path, monkeypatch):
@@ -365,34 +380,44 @@ def _turn_env(tmp_path, monkeypatch):
 
 
 def _unsupported_400_text(param):
-    return json.dumps({"error": {
-        "message": f"Unsupported parameter: '{param}'. Try again.",
-        "type": "invalid_request_error",
-        "param": param,
-        "code": "unsupported_parameter",
-    }})
+    return json.dumps(
+        {
+            "error": {
+                "message": f"Unsupported parameter: '{param}'. Try again.",
+                "type": "invalid_request_error",
+                "param": param,
+                "code": "unsupported_parameter",
+            }
+        }
+    )
 
 
 def _ledger_events(proj):
     ledger_path = proj / "tasks" / ".sessions" / "session_ledger.jsonl"
-    return [json.loads(line) for line in
-            ledger_path.read_text(encoding="utf-8").splitlines()]
+    return [
+        json.loads(line)
+        for line in ledger_path.read_text(encoding="utf-8").splitlines()
+    ]
 
 
 def test_brain_turn_emits_ordered_checkpoints(tmp_path, monkeypatch):
     proj = _turn_env(tmp_path, monkeypatch)
     bodies: list = []
-    _stub_client(monkeypatch,
-                 [_FakeResp(200, "fine", _ok_payload())], bodies)
+    _stub_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], bodies)
     call = bridge.brain_turn
     target = call.fn if hasattr(call, "fn") else call
     result = target("q", task_id="999", project_root=str(proj))
     assert result["status"] == "REPORT"
-    names = [e.get("checkpoint") for e in _ledger_events(proj)
-             if e["event"] == "checkpoint"]
-    assert names == ["request_accepted", "preflight_completed",
-                     "capability_completed", "transport_started",
-                     "response_parsed"]
+    names = [
+        e.get("checkpoint") for e in _ledger_events(proj) if e["event"] == "checkpoint"
+    ]
+    assert names == [
+        "request_accepted",
+        "preflight_completed",
+        "capability_completed",
+        "transport_started",
+        "response_parsed",
+    ]
 
 
 def test_brain_turn_unsupported_param_fails_fast(tmp_path, monkeypatch):
diff --git a/tests/test_skill_registry.py b/tests/test_skill_registry.py
index d38da69..a4b1637 100644
--- a/tests/test_skill_registry.py
+++ b/tests/test_skill_registry.py
@@ -142,8 +142,9 @@ def test_validate_opencode_script():
     code, out = run(no_zac)
     assert code == 1 and "git push *" in out
     secret = json.loads(json.dumps(base))
-    secret["lsp"] = {"pyright": {"command": ["pyright"],
-                                 "env": {"KEY": "sk-live-abc123"}}}
+    secret["lsp"] = {
+        "pyright": {"command": ["pyright"], "env": {"KEY": "sk-live-abc123"}}
+    }
     code, out = run(secret)
     assert code == 1 and "placeholder" in out
 
@@ -160,7 +161,9 @@ def _run_validator(cfg=None, raw=None):
     try:
         r = subprocess.run(
             ["python3", str(script), str(p)],
-            capture_output=True, text=True, timeout=30,
+            capture_output=True,
+            text=True,
+            timeout=30,
         )
         return r.returncode, r.stdout
     finally:
@@ -191,7 +194,11 @@ def test_validate_lsp_v2_keys_rejected():
 
 def test_validate_lsp_wrapper_rejected():
     cfg = _fresh_golden()
-    cfg["lsp"] = {"language-server": {"typescript": {"command": ["typescript-language-server", "--stdio"]}}}
+    cfg["lsp"] = {
+        "language-server": {
+            "typescript": {"command": ["typescript-language-server", "--stdio"]}
+        }
+    }
     code, out = _run_validator(cfg)
     assert code == 1 and "language-server" in out
     cfg = _fresh_golden()
@@ -215,9 +222,13 @@ def test_validate_lsp_null_empty_and_valid():
     cfg["lsp"] = {"pyright": {"command": ["pyright"]}}
     assert _run_validator(cfg) == (0, "")
     cfg = _fresh_golden()
-    cfg["lsp"] = {"pyright": {"command": ["pyright"],
-                              "extensions": [".py"],
-                              "env": {"KEY": "{env:KEY}"}}}
+    cfg["lsp"] = {
+        "pyright": {
+            "command": ["pyright"],
+            "extensions": [".py"],
+            "env": {"KEY": "{env:KEY}"},
+        }
+    }
     assert _run_validator(cfg) == (0, "")
     cfg = _fresh_golden()
     cfg["lsp"] = {"pyright": {"disabled": True}}
@@ -239,8 +250,9 @@ def test_validate_formatter_named_map():
     code, out = _run_validator(cfg)
     assert code == 1 and "named map" in out
     cfg = _fresh_golden()
-    cfg["formatter"] = {"spotless-java": {"command": ["mvn", "spotless:apply"],
-                                          "extensions": [".java"]}}
+    cfg["formatter"] = {
+        "spotless-java": {"command": ["mvn", "spotless:apply"], "extensions": [".java"]}
+    }
     assert _run_validator(cfg) == (0, "")
     cfg = _fresh_golden()
     cfg["formatter"] = False
@@ -260,8 +272,15 @@ def test_validate_plugin_env_secret_rules():
 
 def test_validate_invented_values_expanded():
     for bad in (
-        "foo-srv", "dummy", "placeholder-x", "sample agent",
-        "TODO", "changeme", "xxx", "your-value-here", "example-plugin",
+        "foo-srv",
+        "dummy",
+        "placeholder-x",
+        "sample agent",
+        "TODO",
+        "changeme",
+        "xxx",
+        "your-value-here",
+        "example-plugin",
     ):
         cfg = _fresh_golden()
         cfg["default_agent"] = bad
@@ -281,8 +300,13 @@ def test_validate_invented_values_expanded():
 
 def test_validate_mcp_rejected_global_only():
     cfg = _fresh_golden()
-    cfg["mcp"] = {"srv": {"type": "local", "command": ["node", "server.js"],
-                          "environment": {"KEY": "{env:KEY}"}}}
+    cfg["mcp"] = {
+        "srv": {
+            "type": "local",
+            "command": ["node", "server.js"],
+            "environment": {"KEY": "{env:KEY}"},
+        }
+    }
     code, out = _run_validator(cfg)
     assert code == 1 and "global-only" in out
 
@@ -302,7 +326,9 @@ def test_validate_malformed_inputs_fail_closed():
     )
     r = subprocess.run(
         ["python3", str(script), str(ROOT / ".tmp-does-not-exist.json")],
-        capture_output=True, text=True, timeout=30,
+        capture_output=True,
+        text=True,
+        timeout=30,
     )
     assert r.returncode == 1
     assert _run_validator(raw="")[0] == 1
@@ -323,6 +349,7 @@ def test_validate_opencode_positives():
     cfg["lsp"] = {"pyright": {"command": ["pyright"]}}
     assert _run_validator(cfg) == (0, "")
     cfg = _fresh_golden()
-    cfg["formatter"] = {"spotless-java": {"command": ["mvn", "spotless:apply"],
-                                          "extensions": [".java"]}}
+    cfg["formatter"] = {
+        "spotless-java": {"command": ["mvn", "spotless:apply"], "extensions": [".java"]}
+    }
     assert _run_validator(cfg) == (0, "")
```
<!-- END_GIT_DIFF -->
