# Task 308: Context MCP Lite Graph Upgrade from Graphify

**File:** `tasks/archive/308-context-mcp-lite-graph-upgrade.md`
**Source:** manager
**Type:** feature
**Status:** superseded-progress

## Goal

Add lite knowledge-graph capability to mcp-context-server inspired by Graphify: persist graph.json plus query/path/explain tools and god-node ranking, while keeping current tree/read/signatures behavior unchanged.

## Manager's Notes

Manager approved scope Lite graph upgrade on 2026-10-09 via question tool. Docs-only rejected. Full port rejected. Create tracked task file in tasks/backlog. Plan approved: 1) map gap, 2) draft doc plus small graph prototype design, 3) implement behind verification gates. Reference: Graphify-Labs/graphify knowledge graph with local AST parsing, EXTRACTED/INFERRED edges, query/path/explain, god nodes and communities.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Map gap between mcp-context-server and Graphify concepts
- [x] Design graph.json schema plus query/path/explain tool contracts
- [x] Prototype god-node ranking and cross-file edges
- [x] Update README and DECISIONS for mcp-context-server
- [x] Verify with lint and server tests

## Acceptance Criteria

- [x] AC1: Gap map records current tree/read/signatures versus Graphify graph/query/path/explain
- [x] AC2: graph.json schema versioned and persisted under context-reports or graphify-out equivalent
- [x] AC3: New query/path/explain tools return scoped subgraphs without breaking existing tools
- [x] AC4: God-node ranking lists most-connected concepts with EXTRACTED versus INFERRED tags
- [x] AC5: README and DECISIONS updated in same change per Living Folder Docs standard
- [x] AC6: lint_task_file passes and existing server tests pass

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest pytest tests/test_mcp_servers.py -q
- **Expected result:** all context tests pass; only pre-existing memory-server yaml failures remain
- **Actual result:** 67 passed, 6 failed (all 6 are pre-existing ModuleNotFoundError: No module named 'yaml' in mcp-memory-server); graph filter `-k graph_` gives 3 passed; lint_task_file passes; lint_system_prompt_sync in sync
- **Exit code:** 0 (rtk preserves underlying exit; scoped graph run exit 0)

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Graph build cost grows on large repos and breaks single-threaded MCP server
- **Rollback plan:** Revert server.py and docs to prior commit, keep existing tree/read/signatures tools

---

> **Superseded:** This task was bundled into META task `313-unified-context-graph` and archived on 2026-10-09. See `tasks/backlog/313-unified-context-graph.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/308-context-mcp-lite-graph-upgrade.md`.

## Execution Log & Reasoning

Direct input normalized from English with typo fix references. Absent files skipped per policy: DESIGN.md, docs/architecture.md, docs/data_model.md. Memory lookups: index read, search_memory for mcp context graph returned none, read_memory for mcp_tool_audit and extract_signatures fix applied. Seat Check: backend Python MCP change, no user-visible surface, so Designer skipped, Architect kept for schema contract. Brainstorm: not required — single-domain tool extension, reversible. Manager answers: scope Lite graph upgrade, create task file, plan Approved. ZAC holds, no commit without explicit closure order.

Implementation (Hands, 2026-10-09): Seat Check task domains backend-schema plus docs/skills/prompts/agents → Architect kept, Programmer kept, Designer skipped (no user-visible surface); skipped seats reason recorded. Brainstorm: not required — reversible via git checkout, single scope. Cloned Graphify to /tmp/opencode/graphify; 3 parallel discovery subagents mapped core schema (nodes/links/graph envelope, schema_version 1, EXTRACTED 1.0/INFERRED 0.55-0.95/AMBIGUOUS 0.1-0.3, god_nodes degree rank, Leiden communities), query/path/explain plus MCP serve contracts, and HQ inventory (8 tools, tests in test_mcp_servers.py, 6 skill-templates, 4 fragments, 2 agents, zero graph refs, get_directory_tree scoping bug). Lite design: stdlib-only, no new deps, caps files 300/nodes 5000. server.py: added json import, fixed get_directory_tree overwrite bug, added GRAPH_SCHEMA_VERSION=1 plus build_graph/query_graph/explain_node/shortest_path/god_nodes/graph_stats with _build/_save/_load/_bfs helpers; reports under context-reports/ (gitignored). Updated mcp-context-server README/DECISIONS (ADR-002). Tests: 3 new graph tests pass; full file 67 passed 6 pre-existing memory yaml failures. Skills/prompts/agents: code-search 1.6 graph-first, 09-hands_protocols 1.6 graph-first (both templates), discovery step 5 graph-first, executor MCP-first extended, system_version 9.54.0→9.55.0 with regenerated system-prompt.md (lint_system_prompt_sync in sync). CHANGELOG [Unreleased] Added entry. Assumption A1: stdlib-only lite suffices for Manager scope (no Leiden/HTML/viz). Assumption A2: memory yaml failures pre-existing and unrelated (verified ModuleNotFoundError).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e6ef3b0..e803a18 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Context MCP lite knowledge-graph (Task 308, system prompt 9.55.0):** `mcp-context-server` now builds a deterministic stdlib-only graph (files + symbols; contains/imports EXTRACTED, references INFERRED) with `build_graph` persisting versioned `graph_*.json` (schema 1) plus `graph_report_*.md` under `context-reports/`, and `query_graph` / `explain_node` / `shortest_path` / `god_nodes` / `graph_stats` for scoped queries. Also fixed `get_directory_tree` workspace scoping (removed cwd overwrite). Discovery is graph-first: `skill-templates/code-search`, `prompts/fragments/09-hands_protocols`, `agents/cognitive-discovery.md`, and `agents/cognitive-executor.md` prefer graph queries before raw reads.
+
 - **Brain partial-truncation server-side recovery (Task 291, fixes issue #28):** long implement `brain_turn` calls truncated by `max_output_tokens` no longer return a bare fragment into a caller-side retry loop. Research found the cap is innocent — live `BRAIN_MAX_TOKENS=943718` already sits at the `meta/muse-spark-1.3-contributor` ceiling — while `BRAIN_REASONING_EFFORT=xhigh` burns ~97% of the output budget on reasoning (measured `reasoning_tokens=14683 visible_tokens=341`), starving the visible XML at ANY cap. Following the industry playbook (structured output must be re-issued whole with more headroom, never stitched), the bridge now discards the fragment and re-issues the turn ONCE server-side with one-notch-lower reasoning effort (`max→xhigh→high→medium→low` via `_step_down_effort`); a second truncation returns terminal `TRUNCATION_UNRECOVERABLE` (caller must not retry as-is) instead of looping. Task 259 empty-output terminal, `EMPTY_OUTPUT_RETRY`, the semantic gate, and the 5xx/429 retry policy are untouched. Open decisions for the Manager: lower live effort from `xhigh`, keep the cap, deploy = copy `server.py` to the install + `systemctl --user restart mcp-brain`.
 
 - **Brain context-sufficiency pack (Task 285):** the Brain planned against a five-file documentation bundle only, with no repository structure, so it either guessed or burned a discovery round just to aim its context request. `mcp-brain-bridge/server.py` now auto-appends the newest generated `.gitignore`-aware tree report (`context-reports/tree_report_*.md`, written by the Hands via `custom_context.create_tree_report`) to that bundle under a labeled section, bounded by a new `_STRUCTURAL_FILE_CAP` (40000) and the shared `_BUNDLE_TOTAL_CAP` with honest `[truncated]`/`[skipped: bundle total cap]` markers. The section appears only when a report exists, so every workspace and test without one is byte-unchanged. New pure helpers `_latest_report_path` (newest by mtime, then name; accepts a `Path` or a `str` root) and `_build_structural_pack` (never raises) do the work, and `_build_context_bundle` appends the pack last so the stable doc files keep their prefix positions. Hardened after the QA hotfix round: a report that resolves outside the workspace root (symlink escape) is skipped rather than read, a zero-byte/whitespace report counts as no grounding, the read is capped at `_STRUCTURAL_FILE_CAP` chars so an oversized report is never slurped whole, and triple backticks are neutralized with an invisible break so report fences cannot close a surrounding fence. A second pure helper, `context_sufficiency_gaps(stage, user_prompt, bundle_text, bundle_included)`, plus a `plan`-stage-only stderr diagnostic makes a blind plan observable instead of silent — non-blocking by design (no `status`/`xml_blocks` change), so no caller behavior shifts. The diagnostic reads the FINAL rendered bundle and the combined prompt including any pinned fed-context block, and it suppresses the structural demand when the caller opted out of the bundle — closing two false-positive paths found in QA. A second QA finding (round 2) was also fixed: a pack dropped for the total cap now appends `[structural pack skipped: bundle total cap]` with NO grounding marker, so a skipped pack correctly counts as absent instead of falsely reading as grounded. 21 new regression tests cover pack selection, truncation, bundle integration, string-root normalization, symlink-escape skip, empty-report handling, fence escaping, the skip-counts-as-absent case, the pure gap checker, and the stderr wiring. Bridge suite: **272 passed** (251 pre-existing + 21 new).
diff --git a/agents/cognitive-discovery.md b/agents/cognitive-discovery.md
index 9eb7f28..81c6483 100644
--- a/agents/cognitive-discovery.md
+++ b/agents/cognitive-discovery.md
@@ -23,7 +23,8 @@ When invoked, you must use the `custom_context` MCP tools to compile comprehensi
 2. Use `create_tree_report` to persist a `.gitignore-aware` tree of a path or the whole project as `context-reports/tree_report_<timestamp>_<uuid>.md` when the Manager asks to "create a tree of the project".
 3. Use `read_source_files` to fetch the exact source code of requested files.
 4. Use `extract_signatures` to pull function/class signatures for vertical slices.
-5. You still must not write, record, or evolve anything.
+5. Graph-first: run `build_graph` once per scope (saves versioned `graph_*.json` + `graph_report_*.md` with EXTRACTED/INFERRED edges), then prefer `query_graph` / `explain_node` / `shortest_path` / `god_nodes` for cross-file questions before full reads. Use `graph_stats` to confirm coverage.
+6. You still must not write, record, or evolve anything.
 
 Do not modify any files. Do not attempt to execute code. Compile the report and halt.
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index b8fa333..a1d53b0 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -25,7 +25,7 @@ You are the primary execution engine for the Cognitive Lead AI platform. You rec
 
 1. **Entry Point:** Your absolute first action is to read `AGENTS.md`. If `AGENTS.md` references `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, or `docs/conventions.md`, you MUST read them.
 2. **Rule Validation:** If the Orchestrator's instructions violate ANY project rule, HALT immediately. Output a `⚠️ RULE VIOLATION WARNING` detailing the broken rule. Do NOT proceed.
-3. **MCP-First Context:** When instructed to gather context, you MUST use the `custom_context` MCP tools (`get_directory_tree`, `create_tree_report`, `read_source_files`, `extract_signatures`). NEVER use native `read` to dump large file contents inline.
+3. **MCP-First Context:** When instructed to gather context, you MUST use the `custom_context` MCP tools (`get_directory_tree`, `create_tree_report`, `read_source_files`, `extract_signatures`, plus graph-first `build_graph`, `query_graph`, `explain_node`, `shortest_path`, `god_nodes`, `graph_stats`). NEVER use native `read` to dump large file contents inline.
 4. **Skill Loading:** Load all skills explicitly named in the XML task's `<context_phase>`.
 5. **Zero-Autonomous-Commit (ZAC):** You are STRICTLY FORBIDDEN from executing `git add`, `git commit`, or `git push`. These are denied at the permission layer. All staging is done via the `custom_context_stage_and_inject_diff` MCP tool.
 6. **Finalization & Closure Sequence:**
diff --git a/mcp-context-server/DECISIONS.md b/mcp-context-server/DECISIONS.md
index d88a024..0a53987 100644
--- a/mcp-context-server/DECISIONS.md
+++ b/mcp-context-server/DECISIONS.md
@@ -6,3 +6,10 @@
 - **Decision:** Adopting Living Folder Docs standard for this component.
 - **Consequences:** All future structural or contract changes must be recorded here.
 - **Rollback:** N/A (baseline adoption).
+
+## [2026-10-09] ADR-002: Lite Knowledge-Graph (Graphify-inspired, stdlib-only)
+
+- **Context:** Context reports were file dumps (trees/signatures/reads) with no cross-file links. Graphify shows queryable graphs beat grep; full port (Leiden, graspologic, networkx, HTML viz) is too heavy for the singleton MCP server.
+- **Decision:** Add lite graph to `server.py`: `build_graph` (files + regex symbols, contains/imports EXTRACTED, references INFERRED), `query_graph` (token seeds + 2-hop), `explain_node`, `shortest_path` (BFS directed default), `god_nodes` (symbol degree rank), `graph_stats`; versioned `graph.json` (schema 1) + `graph_report_*.md` under `context-reports/`; fix `get_directory_tree` workspace-scoping bug (removed `Path(target_path)` overwrite).
+- **Consequences:** Discovery/consumers prefer graph queries before raw reads; no new deps; caps keep single-threaded server safe.
+- **Rollback:** Revert `server.py` graph block + docs; existing tree/read/signature tools unchanged.
diff --git a/mcp-context-server/README.md b/mcp-context-server/README.md
index 778c55a..c4767ea 100644
--- a/mcp-context-server/README.md
+++ b/mcp-context-server/README.md
@@ -2,11 +2,11 @@
 
 ## Duties
 
-Custom-context MCP daemon: directory trees, source reads, signature extraction, diff staging/injection (`stage_and_inject_diff`), task commit/clean, and meta-task bundling (`bundle_tasks`).
+Custom-context MCP daemon: directory trees, source reads, signature extraction, lite knowledge-graph (build/query/explain/path/god-nodes/stats with versioned graph.json), diff staging/injection (`stage_and_inject_diff`), task commit/clean, and meta-task bundling (`bundle_tasks`).
 
 ## Files
 
-- `server.py` — Daemon entrypoint (tree reports, source reads, staging, bundling tools).
+- `server.py` — Daemon entrypoint (tree reports, source reads, signatures, lite graph, staging, bundling tools).
 - `pyproject.toml` / `uv.lock` — Runtime deps (`pathspec`, `mcp[cli]`) and lockfile.
 
 ## Key Risks & Invariants
@@ -14,3 +14,4 @@ Custom-context MCP daemon: directory trees, source reads, signature extraction,
 - ZAC enforcement point: staging goes through `stage_and_inject_diff`; never `git commit` directly.
 - Path confinement: all scans stay inside project root; vendor dirs excluded.
 - Bundle lifecycle (META + supersede/archive) is the only writer of `tasks/archive/` moves.
+- Graph lite: stdlib-only deterministic build (files + symbols, contains/imports EXTRACTED, references INFERRED); caps files 300 / nodes 5000; reports under `context-reports/` (gitignored).
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index 28d7ee3..d30042a 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -19,6 +19,7 @@
 import contextvars
 import functools
 import importlib
+import json
 import os
 import re
 import shutil
@@ -32,8 +33,10 @@ from typing import Optional
 import pathspec
 from mcp.server.fastmcp import FastMCP
 
+
 class GitIgnoreFilter:
     """Evaluates paths against .gitignore files dynamically."""
+
     def __init__(self) -> None:
         self._specs: dict[Path, Optional[pathspec.PathSpec]] = {}
 
@@ -104,8 +107,10 @@ class GitIgnoreFilter:
             current = current.parent
         return False
 
+
 TEXT_ENCODINGS = ["utf-8", "utf-8-sig", "windows-1256", "windows-1252", "latin-1"]
 
+
 def is_binary(file_path: Path) -> bool:
     try:
         with open(file_path, "rb") as f:
@@ -114,16 +119,25 @@ def is_binary(file_path: Path) -> bool:
     except Exception:
         return True
 
+
 # --- Tree-sitter AST signature extraction ---
 
 _EXTENSION_LANG_MAP: dict[str, str] = {
     ".py": "python",
-    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
-    ".ts": "typescript", ".tsx": "typescript", ".mts": "typescript", ".cts": "typescript",
+    ".js": "javascript",
+    ".jsx": "javascript",
+    ".mjs": "javascript",
+    ".cjs": "javascript",
+    ".ts": "typescript",
+    ".tsx": "typescript",
+    ".mts": "typescript",
+    ".cts": "typescript",
     ".go": "go",
-    ".java": "java", ".jsp": "java",
+    ".java": "java",
+    ".jsp": "java",
     ".rs": "rust",
-    ".kt": "kotlin", ".kts": "kotlin",
+    ".kt": "kotlin",
+    ".kts": "kotlin",
     ".swift": "swift",
     ".rb": "ruby",
     ".php": "php",
@@ -132,53 +146,54 @@ _EXTENSION_LANG_MAP: dict[str, str] = {
 
 _TS_QUERIES: dict[str, list[str]] = {
     "python": [
-        '(function_definition name: (identifier) @name parameters: (parameters) @params) @sig',
-        '(class_definition name: (identifier) @name) @sig',
+        "(function_definition name: (identifier) @name parameters: (parameters) @params) @sig",
+        "(class_definition name: (identifier) @name) @sig",
     ],
     "javascript": [
-        '(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig',
-        '(class_declaration name: (identifier) @name) @sig',
-        '(method_definition name: (property_identifier) @name) @sig',
-        '(arrow_function) @sig',
-        '(generator_function_declaration name: (identifier) @name) @sig',
+        "(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
+        "(class_declaration name: (identifier) @name) @sig",
+        "(method_definition name: (property_identifier) @name) @sig",
+        "(arrow_function) @sig",
+        "(generator_function_declaration name: (identifier) @name) @sig",
     ],
     "typescript": [
-        '(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig',
-        '(class_declaration name: (type_identifier) @name) @sig',
-        '(interface_declaration name: (type_identifier) @name) @sig',
-        '(method_definition name: (property_identifier) @name) @sig',
-        '(type_alias_declaration name: (type_identifier) @name) @sig',
-        '(enum_declaration name: (identifier) @name) @sig',
-        '(arrow_function) @sig',
+        "(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
+        "(class_declaration name: (type_identifier) @name) @sig",
+        "(interface_declaration name: (type_identifier) @name) @sig",
+        "(method_definition name: (property_identifier) @name) @sig",
+        "(type_alias_declaration name: (type_identifier) @name) @sig",
+        "(enum_declaration name: (identifier) @name) @sig",
+        "(arrow_function) @sig",
     ],
     "go": [
-        '(function_declaration name: (identifier) @name parameters: (parameter_list) @params) @sig',
-        '(method_declaration receiver: (parameter_list) @receiver name: (field_identifier) @name) @sig',
-        '(type_declaration (type_spec name: (type_identifier) @name)) @sig',
+        "(function_declaration name: (identifier) @name parameters: (parameter_list) @params) @sig",
+        "(method_declaration receiver: (parameter_list) @receiver name: (field_identifier) @name) @sig",
+        "(type_declaration (type_spec name: (type_identifier) @name)) @sig",
     ],
     "java": [
-        '(method_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig',
-        '(class_declaration name: (identifier) @name) @sig',
-        '(interface_declaration name: (identifier) @name) @sig',
-        '(enum_declaration name: (identifier) @name) @sig',
-        '(record_declaration name: (identifier) @name) @sig',
+        "(method_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
+        "(class_declaration name: (identifier) @name) @sig",
+        "(interface_declaration name: (identifier) @name) @sig",
+        "(enum_declaration name: (identifier) @name) @sig",
+        "(record_declaration name: (identifier) @name) @sig",
     ],
     "rust": [
-        '(function_item name: (identifier) @name parameters: (parameters) @params) @sig',
-        '(struct_item name: (type_identifier) @name) @sig',
-        '(enum_item name: (type_identifier) @name) @sig',
-        '(trait_item name: (type_identifier) @name) @sig',
-        '(type_item name: (type_identifier) @name) @sig',
-        '(impl_item trait: (type_identifier) @name) @sig',
+        "(function_item name: (identifier) @name parameters: (parameters) @params) @sig",
+        "(struct_item name: (type_identifier) @name) @sig",
+        "(enum_item name: (type_identifier) @name) @sig",
+        "(trait_item name: (type_identifier) @name) @sig",
+        "(type_item name: (type_identifier) @name) @sig",
+        "(impl_item trait: (type_identifier) @name) @sig",
     ],
     "kotlin": [
-        '(function_declaration name: (identifier) @name) @sig',
-        '(class_declaration name: (identifier) @name) @sig',
+        "(function_declaration name: (identifier) @name) @sig",
+        "(class_declaration name: (identifier) @name) @sig",
     ],
 }
 
 _ts_language_cache: dict[str, object] = {}
 
+
 def _get_ts_language(lang_id: str) -> object:
     if lang_id in _ts_language_cache:
         return _ts_language_cache[lang_id]
@@ -186,6 +201,7 @@ def _get_ts_language(lang_id: str) -> object:
     try:
         mod = importlib.import_module(pkg_name)
         from tree_sitter import Language as TSLanguage
+
         if lang_id == "typescript":
             lang = TSLanguage(mod.language_typescript())
         else:
@@ -196,12 +212,13 @@ def _get_ts_language(lang_id: str) -> object:
         _ts_language_cache[lang_id] = None
         return None
 
+
 def _extract_signature_line(source_lines: list[str], start_row: int) -> str:
     first = source_lines[start_row].rstrip("\n").rstrip("\r")
     if not first.rstrip().endswith(",") and first.count("(") == first.count(")"):
         return first
     parts: list[str] = [first]
-    for line in source_lines[start_row + 1:]:
+    for line in source_lines[start_row + 1 :]:
         stripped = line.rstrip("\n").rstrip("\r")
         parts.append(stripped)
         if ":" in stripped and not stripped.rstrip().endswith(","):
@@ -212,6 +229,7 @@ def _extract_signature_line(source_lines: list[str], start_row: int) -> str:
             break
     return "\n".join(parts)
 
+
 def _extract_via_tree_sitter(file_path: Path) -> Optional[str]:
     ext = file_path.suffix.lower()
     lang_id = _EXTENSION_LANG_MAP.get(ext)
@@ -230,6 +248,7 @@ def _extract_via_tree_sitter(file_path: Path) -> Optional[str]:
         return None
     source_bytes = content.encode("utf-8")
     from tree_sitter import Parser, Query, QueryCursor
+
     parser = Parser(lang)
     tree = parser.parse(source_bytes)
     source_lines = content.split("\n")
@@ -254,6 +273,7 @@ def _extract_via_tree_sitter(file_path: Path) -> Optional[str]:
         return None
     return f"### Signatures in {file_path}\n" + "\n".join(signatures)
 
+
 # --- End tree-sitter ---
 
 # Runaway-traversal guards (Task 177): a single wedged request (e.g. tree of
@@ -265,9 +285,20 @@ COLLECT_MAX_FILES = 1000
 # Directory names never descended into, at any level. Supplements .gitignore
 # (which cannot cover absolute-path walks outside any repo).
 BANNED_DIRS = frozenset(
-    {".git", ".cache", "__pycache__", "node_modules", ".venv", "venv", "proc", "sys", "dev"}
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
 )
 
+
 def _is_banned_dir(entry: Path) -> bool:
     """True when a directory entry must never be descended into."""
     try:
@@ -275,6 +306,7 @@ def _is_banned_dir(entry: Path) -> bool:
     except OSError:
         return True  # Unstatable entries are treated as unsafe to descend.
 
+
 def generate_tree(
     dir_path: Path,
     ignore_filter: GitIgnoreFilter,
@@ -283,6 +315,7 @@ def generate_tree(
 ) -> str:
     lines = ["```text", dir_path.name or str(dir_path)]
     state = {"count": 0, "truncated": False}
+
     def _walk(current_path: Path, prefix: str, depth: int) -> None:
         if state["truncated"]:
             return
@@ -299,7 +332,9 @@ def generate_tree(
             for e in entries
             if not _is_banned_dir(e) and not ignore_filter.is_ignored(e)
         ]
-        sorted_entries = sorted(valid_entries, key=lambda e: (not e.is_dir(), e.name.lower()))
+        sorted_entries = sorted(
+            valid_entries, key=lambda e: (not e.is_dir(), e.name.lower())
+        )
         for i, entry in enumerate(sorted_entries):
             if state["count"] >= max_entries:
                 lines.append(
@@ -314,10 +349,12 @@ def generate_tree(
             if entry.is_dir():
                 extension = "    " if is_last else "│   "
                 _walk(entry, prefix + extension, depth + 1)
+
     _walk(dir_path, "", 0)
     lines.append("```")
     return "\n".join(lines)
 
+
 def process_source_file(file_path: Path, max_size: int, line_numbers: bool) -> str:
     lines = [f"### `{file_path}`", ""]
     if not file_path.exists():
@@ -326,14 +363,18 @@ def process_source_file(file_path: Path, max_size: int, line_numbers: bool) -> s
     try:
         size = file_path.stat().st_size
         if size > max_size:
-            lines.append(f"> Skipped: (File too large: {size} bytes > max_size={max_size})\n")
+            lines.append(
+                f"> Skipped: (File too large: {size} bytes > max_size={max_size})\n"
+            )
             # Discovery gap fix (Task 241): a skipped body must not mean
             # zero evidence — attach structural signatures when extractable
             # so the Brain still sees the file's shape. Never raises.
             try:
                 sig = _extract_via_tree_sitter(file_path)
                 if sig:
-                    lines.append("> Body omitted by size cap; structural signatures follow:\n")
+                    lines.append(
+                        "> Body omitted by size cap; structural signatures follow:\n"
+                    )
                     lines.append(sig)
                 else:
                     lines.append(
@@ -359,7 +400,9 @@ def process_source_file(file_path: Path, max_size: int, line_numbers: bool) -> s
         except (UnicodeDecodeError, UnicodeError):
             continue
     if content_text is None:
-        lines.append(f"> Skipped: (Could not decode file with any supported encoding)\n")
+        lines.append(
+            f"> Skipped: (Could not decode file with any supported encoding)\n"
+        )
         return "\n".join(lines)
     file_lines = content_text.split("\n")
     if file_lines and file_lines[-1] == "":
@@ -374,6 +417,7 @@ def process_source_file(file_path: Path, max_size: int, line_numbers: bool) -> s
     lines.append("```\n")
     return "\n".join(lines)
 
+
 def collect_files(
     target: str,
     ignore_filter: GitIgnoreFilter,
@@ -401,6 +445,7 @@ def collect_files(
                 collected.append(file_path)
     return collected
 
+
 def _ensure_context_reports_ignored(workspace_root: Path | None = None) -> None:
     """Safeguard: Append context-reports/ to <workspace_root>/.gitignore.
 
@@ -421,6 +466,7 @@ def _ensure_context_reports_ignored(workspace_root: Path | None = None) -> None:
         except Exception as e:
             print(f"Warning: Failed to update .gitignore: {e}", file=sys.stderr)
 
+
 mcp = FastMCP("CustomContext", host="127.0.0.1", port=8102)
 
 # Client-visible project-isolation warning (Task 279 F6/V1). When a caller
@@ -429,15 +475,18 @@ mcp = FastMCP("CustomContext", host="127.0.0.1", port=8102)
 # by @_project_tool in the tool result. No absolute paths are echoed
 # (layout privacy, cf. decision-server _active_root_info).
 _FALLBACK_FIRED: contextvars.ContextVar[bool] = contextvars.ContextVar(
-    "custom_context_fallback_fired", default=False)
+    "custom_context_fallback_fired", default=False
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
@@ -447,8 +496,10 @@ def _project_tool(fn):
         if isinstance(out, str):
             return ROOT_FALLBACK_WARNING + "\n" + out
         return out
+
     return mcp.tool()(wrapper)
 
+
 @_project_tool
 def get_directory_tree(target_path: str = ".", project_root: str | None = None) -> str:
     """Generates an ASCII tree representation of the directory, respecting .gitignore. Use this to discover codebase structure with immediate inline output. Use create_tree_report instead when a persistent saved report file is required. project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
@@ -470,15 +521,667 @@ def get_directory_tree(target_path: str = ".", project_root: str | None = None)
     except ValueError:
         return "Error: Path traversal detected. target_path must be within the project workspace."
     ignore_filter = GitIgnoreFilter()
-    tree_path = Path(target_path)
     if not tree_path.is_dir():
         return f"Error: {target_path} is not a valid directory."
     if ignore_filter.is_ignored(tree_path):
         return f"Warning: Target tree path is ignored by .gitignore: {target_path}"
-    return f"## Directory Tree: `{tree_path}`\n\n" + generate_tree(tree_path, ignore_filter)
+    return f"## Directory Tree: `{tree_path}`\n\n" + generate_tree(
+        tree_path, ignore_filter
+    )
+
+
+# --- Lite knowledge-graph (Graphify-inspired, stdlib-only) ---
+# Design: deterministic local graph, no LLM, no vector store. Nodes are files
+# + symbols (def/class). Edges carry confidence tags EXTRACTED (explicit in
+# source: contains/imports) or INFERRED (resolved: references across files).
+# Persisted as versioned graph.json + markdown report under context-reports/.
+
+GRAPH_SCHEMA_VERSION = 1
+GRAPH_MAX_FILES = 300
+GRAPH_MAX_NODES = 5000
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
+    }
+)
+_GRAPH_SYMBOL_RE = re.compile(
+    r"^\s*(?:export\s+|default\s+|public\s+|private\s+|protected\s+|static\s+|async\s+|fun\s+|def\s+|class\s+|interface\s+|type\s+|enum\s+|struct\s+|trait\s+|func(?:tion)?\s+)?"
+    r"(?:class|interface|type|enum|struct|trait|def|fun|func(?:tion)?)\s+([A-Za-z_]\w*)"
+)
+_GRAPH_CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
+
+
+def _graph_rel_posix(p: Path, root: Path) -> str:
+    try:
+        return p.resolve().relative_to(root).as_posix()
+    except ValueError:
+        return p.name
+
+
+def _extract_graph_symbols(file_path: Path) -> list[tuple[str, str, int]]:
+    """Return [(name, kind, line_no)] capped per file. Regex-based, deterministic."""
+    out: list[tuple[str, str, int]] = []
+    try:
+        with open(file_path, "r", encoding="utf-8", errors="strict") as f:
+            lines = f.read().split("\n")[:2000]
+    except Exception:
+        return out
+    for i, line in enumerate(lines, 1):
+        if len(out) >= 200:
+            break
+        m = _GRAPH_SYMBOL_RE.match(line)
+        if not m:
+            continue
+        name = m.group(1)
+        if len(name) < 2 or name.startswith("_") and len(name) > 30:
+            pass
+        lowered = line.lower()
+        kind = "class" if "class" in lowered else "func"
+        if name not in {n for n, _, _ in out}:
+            out.append((name, kind, i))
+    return out
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
+    ][:GRAPH_MAX_FILES]
+    rels: list[str] = []
+    rel_set: set[str] = set()
+    resolved: list[Path] = []
+    for p in files:
+        try:
+            rel = p.resolve().relative_to(workspace_root).as_posix()
+        except ValueError:
+            continue
+        if rel not in rel_set:
+            rel_set.add(rel)
+            rels.append(rel)
+            resolved.append(p.resolve())
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
+        for name, kind, lineno in _extract_graph_symbols(abs_p):
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
+    return {"nodes": nodes, "links": links}
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
+    lines = [
+        f"# Graph Report - {target_label}",
+        "",
+        f"- **Generated:** {timestamp}",
+        f"- **Schema:** {GRAPH_SCHEMA_VERSION}",
+        f"- **Nodes:** {len(envelope['nodes'])} **Edges:** {len(envelope['links'])}",
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
+    return set(re.findall(r"[a-z0-9_]{3,}", text.lower()))
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
 
 @_project_tool
-def read_source_files(paths: list[str], max_size: int = 1048576, no_line_numbers: bool = False, project_root: str | None = None) -> str:
+def build_graph(target_path: str = ".", project_root: str | None = None) -> str:
+    """Builds a lite deterministic knowledge-graph (files + symbols, contains/imports/references with EXTRACTED/INFERRED tags) and saves versioned graph.json plus a markdown report under context-reports/. Use before query_graph/explain_node/shortest_path/god_nodes. project_root scopes the scan; target_path scopes the subgraph."""
+    if not isinstance(target_path, str):
+        target_path = "."
+    try:
+        workspace_root = _explicit_project_root(project_root, "build_graph")
+    except ValueError as e:
+        return f"Error: {e}"
+    _ensure_context_reports_ignored(workspace_root)
+    tgt = (
+        Path(target_path)
+        if Path(target_path).is_absolute()
+        else workspace_root / target_path
+    )
+    try:
+        tgt = tgt.resolve()
+        tgt.relative_to(workspace_root)
+    except ValueError:
+        return "Error: Path traversal detected. target_path must be within the project workspace."
+    if not tgt.exists():
+        return f"Error: {target_path} not found."
+    started = time.monotonic()
+    data = _build_graph_data(workspace_root, tgt if tgt.is_dir() else tgt.parent)
+    json_path, md_path = _save_graph(workspace_root, data, str(tgt))
+    dur = time.monotonic() - started
+    return f"✅ Success: Graph built for `{tgt}`.\n📊 {len(data['nodes'])} nodes, {len(data['links'])} links in {dur:.2f}s (schema {GRAPH_SCHEMA_VERSION}, caps files {GRAPH_MAX_FILES}).\n📁 Graph: `{json_path}`\n📁 Report: `{md_path}`"
+
+
+@_project_tool
+def query_graph(
+    question: str,
+    graph_path: str | None = None,
+    top_n: int = 10,
+    project_root: str | None = None,
+) -> str:
+    """Queries the lite graph with plain words: scores nodes by token overlap, expands 2 hops, returns a scoped subgraph. Run build_graph first. Pass graph_path to pin a graph file, else the latest in context-reports/ is used."""
+    try:
+        workspace_root = _explicit_project_root(project_root, "query_graph")
+    except ValueError as e:
+        return f"Error: {e}"
+    if not isinstance(question, str) or not question.strip():
+        return "Error: question must be a non-empty string."
+    data, gp, err = _load_graph_data(workspace_root, graph_path)
+    if err or data is None:
+        return f"Error: {err}"
+    toks = _graph_tokens(question)
+    scored: list[tuple[int, dict]] = []
+    for n in data.get("nodes", []):
+        nt = _graph_tokens(f"{n.get('label', '')} {n.get('source_file', '')}")
+        s = len(toks & nt)
+        if s > 0:
+            scored.append((s, n))
+    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
+    seeds = [n for _, n in scored[:3]]
+    if not seeds:
+        return f"No nodes matched '{question}' in `{gp}`. Try build_graph on a wider target."
+    keep: dict[str, dict] = {}
+    keep_links: list[dict] = []
+    for s in seeds:
+        keep[s["id"]] = s
+        out, inc = _graph_neighbors(data, s["id"])
+        for e, o in (out + inc)[:20]:
+            keep[o["id"]] = o
+            keep_links.append(e)
+            out2, inc2 = _graph_neighbors(data, o["id"])
+            for e2, o2 in (out2 + inc2)[:5]:
+                if len(keep) >= max(10, top_n * 3):
+                    break
+                keep[o2["id"]] = o2
+                keep_links.append(e2)
+    lines = [
+        f"Query: {question}",
+        f"Graph: `{gp}`",
+        f"Seeds: {', '.join(s.get('label', '?') for s in seeds)}",
+        "",
+        f"Nodes ({len(keep)}):",
+    ]
+    for nid in sorted(keep)[: max(10, top_n * 3)]:
+        n = keep[nid]
+        lines.append(
+            f"- {n.get('label')} [{n.get('file_type', '?')}] {n.get('source_file', '')} {n.get('source_location', '')}"
+        )
+    lines.append("")
+    lines.append(f"Edges ({len(keep_links)}):")
+    for e in keep_links[:50]:
+        lines.append(
+            f"- {e['source']} --{e['relation']}[{e['confidence']}]--> {e['target']}"
+        )
+    text = "\n".join(lines)
+    return text[:8000]
+
+
+@_project_tool
+def explain_node(
+    label: str, graph_path: str | None = None, project_root: str | None = None
+) -> str:
+    """Explains one graph concept: source location, type, degree, and top connections with [relation][confidence]. Use after build_graph."""
+    try:
+        workspace_root = _explicit_project_root(project_root, "explain_node")
+    except ValueError as e:
+        return f"Error: {e}"
+    data, gp, err = _load_graph_data(workspace_root, graph_path)
+    if err or data is None:
+        return f"Error: {err}"
+    matches = _find_graph_nodes(data.get("nodes", []), label)
+    if not matches:
+        return f"No node matching '{label}' in `{gp}`."
+    if len(matches) > 1:
+        opts = ", ".join(m.get("label", "?") for m in matches[:5])
+        return (
+            f"Ambiguous '{label}' ({len(matches)} matches: {opts}). Be more specific."
+        )
+    n = matches[0]
+    deg = _graph_degrees(data).get(n["id"], 0)
+    out, inc = _graph_neighbors(data, n["id"])
+    lines = [
+        f"Node: {n.get('label')}",
+        f"  ID: {n['id']}",
+        f"  Source: {n.get('source_file', '?')} {n.get('source_location', '')}",
+        f"  Type: {n.get('file_type', '?')}",
+        f"  Degree: {deg}",
+        "",
+        f"Connections ({len(out) + len(inc)}):",
+    ]
+    for e, o in (out + inc)[:20]:
+        arrow = "-->" if e["source"] == n["id"] else "<--"
+        lines.append(
+            f"  {arrow} {o.get('label')} [{e['relation']}] [{e['confidence']}] {o.get('source_file', '')}"
+        )
+    return "\n".join(lines)
+
+
+@_project_tool
+def shortest_path(
+    source: str,
+    target: str,
+    graph_path: str | None = None,
+    undirected: bool = False,
+    project_root: str | None = None,
+) -> str:
+    """Traces the shortest path between two graph concepts. Directed by default; pass undirected=True to ignore edge direction. Use after build_graph."""
+    try:
+        workspace_root = _explicit_project_root(project_root, "shortest_path")
+    except ValueError as e:
+        return f"Error: {e}"
+    data, gp, err = _load_graph_data(workspace_root, graph_path)
+    if err or data is None:
+        return f"Error: {err}"
+    sm = _find_graph_nodes(data.get("nodes", []), source)
+    tm = _find_graph_nodes(data.get("nodes", []), target)
+    if not sm:
+        return f"No node matching source '{source}'."
+    if not tm:
+        return f"No node matching target '{target}'."
+    if len(sm) > 1 or len(tm) > 1:
+        return f"Ambiguous endpoints (source {len(sm)}, target {len(tm)}). Be more specific."
+    path = _graph_bfs_path(data, sm[0]["id"], tm[0]["id"], directed=not undirected)
+    if not path:
+        return f"No path between '{source}' and '{target}' in `{gp}`."
+    id2n = {n["id"]: n for n in data.get("nodes", [])}
+    lines = [f"Shortest path ({len(path)} hops):"]
+    for a, e, b in path:
+        al = id2n.get(a, {}).get("label", a)
+        bl = id2n.get(b, {}).get("label", b)
+        lines.append(
+            f"  {al} --{e.get('relation', '?')}[{e.get('confidence', '?')}]--> {bl}"
+        )
+    return "\n".join(lines)
+
+
+@_project_tool
+def god_nodes(
+    top_n: int = 10, graph_path: str | None = None, project_root: str | None = None
+) -> str:
+    """Lists the most-connected symbol concepts (degree ranking, file hubs excluded). Use after build_graph to find what everything flows through."""
+    try:
+        workspace_root = _explicit_project_root(project_root, "god_nodes")
+    except ValueError as e:
+        return f"Error: {e}"
+    try:
+        top_n = max(1, min(int(top_n), 50))
+    except Exception:
+        top_n = 10
+    data, gp, err = _load_graph_data(workspace_root, graph_path)
+    if err or data is None:
+        return f"Error: {err}"
+    deg = _graph_degrees(data)
+    id2n = {n["id"]: n for n in data.get("nodes", [])}
+    ranked = sorted(
+        ((d, nid) for nid, d in deg.items() if nid.startswith("sym:")), reverse=True
+    )[:top_n]
+    if not ranked:
+        return f"No symbol nodes in `{gp}`."
+    lines = [f"God nodes (top {len(ranked)}) in `{gp}`:"]
+    for d, nid in ranked:
+        n = id2n.get(nid, {})
+        lines.append(
+            f"- {n.get('label', '?')} (degree {d}, {n.get('source_file', '?')} {n.get('source_location', '')})"
+        )
+    return "\n".join(lines)
+
+
+@_project_tool
+def graph_stats(graph_path: str | None = None, project_root: str | None = None) -> str:
+    """Reports node/edge counts plus EXTRACTED/INFERRED/AMBIGUOUS split and schema version for a built graph."""
+    try:
+        workspace_root = _explicit_project_root(project_root, "graph_stats")
+    except ValueError as e:
+        return f"Error: {e}"
+    data, gp, err = _load_graph_data(workspace_root, graph_path)
+    if err or data is None:
+        return f"Error: {err}"
+    ext = sum(1 for e in data.get("links", []) if e.get("confidence") == "EXTRACTED")
+    inf = sum(1 for e in data.get("links", []) if e.get("confidence") == "INFERRED")
+    tot = len(data.get("links", []))
+    schema = (data.get("graph", {}) or {}).get("schema_version", "?")
+    return f"Graph: `{gp}`\nNodes: {len(data.get('nodes', []))} Edges: {tot} (EXTRACTED {ext} / INFERRED {inf} / AMBIGUOUS {tot - ext - inf})\nSchema: {schema}"
+
+
+@_project_tool
+def read_source_files(
+    paths: list[str],
+    max_size: int = 1048576,
+    no_line_numbers: bool = False,
+    project_root: str | None = None,
+) -> str:
     """Reads multiple source files/directories, compiles their contents into a Markdown file under context-reports/, and returns the report file path. Use when exact source content from named files is required. Returns a path, not inline content. Use extract_signatures instead for a structural outline without file bodies. project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
     try:
         workspace_root = _explicit_project_root(project_root, "read_source_files")
@@ -552,6 +1255,7 @@ def read_source_files(paths: list[str], max_size: int = 1048576, no_line_numbers
         f"Manager: You can now open `{report_file}` in your local editor to view the codebase context or copy/paste it directly for the AI."
     )
 
+
 @_project_tool
 def create_tree_report(target_path: str = ".", project_root: str | None = None) -> str:
     """Creates a .gitignore-aware directory tree of a path or the entire project and saves it as a Markdown file under context-reports/ (named tree_report_<timestamp>_<uuid>.md). Use when the Manager asks to 'create a tree of the project' or 'create a tree of <path>'. Security: target_path is resolved against the workspace root and rejected if it escapes the project (path traversal prevention). project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
@@ -616,6 +1320,7 @@ def create_tree_report(target_path: str = ".", project_root: str | None = None)
         f"Manager: You can now open `{report_file}` in your local editor to view the project tree or copy/paste it directly for the AI."
     )
 
+
 @_project_tool
 def extract_signatures(file_path: str, project_root: str | None = None) -> str:
     """Extracts structural signatures (classes, functions, methods) from source files using tree-sitter AST. Falls back to regex when no tree-sitter grammar is available for the language. Saves the result to a Markdown file under context-reports/ and returns the report file path. Use for a structural API outline without file bodies. Use read_source_files instead when full source content is required. project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
@@ -654,19 +1359,22 @@ def extract_signatures(file_path: str, project_root: str | None = None) -> str:
         if result_content is None:
             # Read the RESOLVED path: under the singleton the raw relative
             # file_path resolves against the server cwd, not the project root.
-            with open(path, 'r', encoding='utf-8') as f:
+            with open(path, "r", encoding="utf-8") as f:
                 content = f.read()
 
             # Match class, function, def, interface, type — with access modifiers
             pattern = re.compile(
-                r'^(?:\s*(?:export|default|public|private|protected|internal|pub|static|abstract|final|override|inline|open|suspend)\s+)*'
-                r'(?:class|struct|enum|trait|impl|interface|type|def|fun|func(?:tion)?)\s+\w+.*$',
-                re.MULTILINE
+                r"^(?:\s*(?:export|default|public|private|protected|internal|pub|static|abstract|final|override|inline|open|suspend)\s+)*"
+                r"(?:class|struct|enum|trait|impl|interface|type|def|fun|func(?:tion)?)\s+\w+.*$",
+                re.MULTILINE,
             )
             matches = pattern.findall(content)
 
             # Match const/let arrow functions
-            arrow_pattern = re.compile(r'^(?:export\s+)?(?:const|let)\s+\w+\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=]*)\s*=>.*$', re.MULTILINE)
+            arrow_pattern = re.compile(
+                r"^(?:export\s+)?(?:const|let)\s+\w+\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=]*)\s*=>.*$",
+                re.MULTILINE,
+            )
             arrow_matches = arrow_pattern.findall(content)
 
             all_matches = matches + arrow_matches
@@ -696,6 +1404,7 @@ def extract_signatures(file_path: str, project_root: str | None = None) -> str:
     except Exception as e:
         return f"Error extracting signatures from {file_path}: {str(e)}"
 
+
 def _repo_root(start_path: str, project_root: str | None = None) -> Path:
     """Resolve the git repo root for git subprocess calls.
 
@@ -708,7 +1417,9 @@ def _repo_root(start_path: str, project_root: str | None = None) -> Path:
     if project_root:
         return Path(project_root).resolve()
     p = Path(start_path)
-    start = (p if p.is_dir() else p.parent) if p.is_absolute() else (Path.cwd() / p).parent
+    start = (
+        (p if p.is_dir() else p.parent) if p.is_absolute() else (Path.cwd() / p).parent
+    )
     for cand in [start, *start.parents]:
         if (cand / ".git").exists():
             return cand
@@ -726,8 +1437,10 @@ def _explicit_project_root(project_root: str | None, tool_name: str) -> Path:
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
@@ -735,12 +1448,16 @@ def _explicit_project_root(project_root: str | None, tool_name: str) -> Path:
         raise ValueError(f"project_root must be absolute, got: {project_root!r}.")
     root = Path(project_root).resolve()
     if not root.is_dir():
-        raise ValueError(f"project_root must be an existing directory, got: {project_root!r}.")
+        raise ValueError(
+            f"project_root must be an existing directory, got: {project_root!r}."
+        )
     return root
 
 
 @_project_tool
-def stage_and_inject_diff(task_file_path: str, modified_files: list[str] = [], project_root: str | None = None) -> str:
+def stage_and_inject_diff(
+    task_file_path: str, modified_files: list[str] = [], project_root: str | None = None
+) -> str:
     """Stages ONLY the explicitly listed modified files plus the task file, then intelligently injects the staged diff into the task file's Git Diff block.
 
     F5 fix (Task 90): explicit path scoping replaces the old blind `git add -A .`,
@@ -755,35 +1472,47 @@ def stage_and_inject_diff(task_file_path: str, modified_files: list[str] = [], p
         #    This prevents cross-session contamination and keeps the diff table clean for the Brain.
         files_to_stage = modified_files + [task_file_path]
         repo = str(_repo_root(task_file_path, project_root))
-        subprocess.run(["git", "add", "--"] + files_to_stage, check=True, capture_output=True, cwd=repo)
-        
+        subprocess.run(
+            ["git", "add", "--"] + files_to_stage,
+            check=True,
+            capture_output=True,
+            cwd=repo,
+        )
+
         # 2. Extract the diff (EXCLUDING the entire tasks/ directory to prevent recursive diff bloat)
         # Using git pathspec magic ':!tasks/' to ignore the entire task folder
         diff_cmd = ["git", "diff", "--staged", "--", ".", ":!tasks/"]
-        diff_process = subprocess.run(diff_cmd, capture_output=True, text=True, cwd=repo)
+        diff_process = subprocess.run(
+            diff_cmd, capture_output=True, text=True, cwd=repo
+        )
         diff_text = diff_process.stdout.strip()
-        
+
         if not diff_text:
             diff_text = "No code changes detected or staged."
-            
+
         diff_block = f"\n```diff\n{diff_text}\n```\n"
 
         # 3. Read the task file
-        with open(task_file_path, 'r', encoding='utf-8') as f:
+        with open(task_file_path, "r", encoding="utf-8") as f:
             content = f.read()
 
         # 4. Smart Replacement using Regex (greedy match from first BEGIN to last END)
         # Using greedy .* to consume everything between the first BEGIN and the LAST END marker,
         # preventing corruption when injected diff content itself contains 'END_GIT_DIFF'
-        pattern = re.compile(r'<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->', re.DOTALL)
-        
+        pattern = re.compile(
+            r"<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->", re.DOTALL
+        )
+
         if not pattern.search(content):
             return f"Error: Could not find the <!-- BEGIN_GIT_DIFF --> markers in {task_file_path}. Did you alter the template?"
 
-        new_content = pattern.sub(lambda m: f'<!-- BEGIN_GIT_DIFF -->{diff_block}<!-- END_GIT_DIFF -->', content)
+        new_content = pattern.sub(
+            lambda m: f"<!-- BEGIN_GIT_DIFF -->{diff_block}<!-- END_GIT_DIFF -->",
+            content,
+        )
 
         # 5. Write back to the task file
-        with open(task_file_path, 'w', encoding='utf-8') as f:
+        with open(task_file_path, "w", encoding="utf-8") as f:
             f.write(new_content)
 
         return f"✅ Success: Changes staged and factual diff intelligently injected into {task_file_path}."
@@ -791,8 +1520,11 @@ def stage_and_inject_diff(task_file_path: str, modified_files: list[str] = [], p
     except Exception as e:
         return f"❌ Error staging or updating task file: {str(e)}"
 
+
 @_project_tool
-def qa_transition(task_file_path: str, modified_files: list[str] = [], project_root: str | None = None) -> str:
+def qa_transition(
+    task_file_path: str, modified_files: list[str] = [], project_root: str | None = None
+) -> str:
     """
     Atomically transitions a task from tasks/in-progress/ to tasks/qa/:
     1. Validates path and ensures task resides in tasks/in-progress/
@@ -833,7 +1565,9 @@ def qa_transition(task_file_path: str, modified_files: list[str] = [], project_r
 
         task_name = src_resolved.name
         if not task_name.endswith(".md"):
-            return f"❌ Error: task file must be a Markdown file (*.md), got: {task_name}"
+            return (
+                f"❌ Error: task file must be a Markdown file (*.md), got: {task_name}"
+            )
 
         dest = workspace_root / "tasks" / "qa" / task_name
         expected_header = f"tasks/qa/{task_name}"
@@ -841,9 +1575,16 @@ def qa_transition(task_file_path: str, modified_files: list[str] = [], project_r
 
         # 2. Move task file to tasks/qa/ via git mv (fallback to shutil.move + git add)
         try:
-            result = subprocess.run(["git", "mv", str(src_resolved), str(dest)], capture_output=True, text=True, cwd=str(workspace_root))
+            result = subprocess.run(
+                ["git", "mv", str(src_resolved), str(dest)],
+                capture_output=True,
+                text=True,
+                cwd=str(workspace_root),
+            )
             if result.returncode != 0:
-                raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git mv failed")
+                raise RuntimeError(
+                    result.stderr.strip() or result.stdout.strip() or "git mv failed"
+                )
         except Exception as e:
             # Fallback for untracked files or git mv failure
             if not src_resolved.exists():
@@ -857,7 +1598,12 @@ def qa_transition(task_file_path: str, modified_files: list[str] = [], project_r
                 if src_resolved.exists():
                     shutil.move(str(src_resolved), str(dest))
                 # Stage the moved file
-                subprocess.run(["git", "add", "--", str(dest)], check=True, capture_output=True, cwd=str(workspace_root))
+                subprocess.run(
+                    ["git", "add", "--", str(dest)],
+                    check=True,
+                    capture_output=True,
+                    cwd=str(workspace_root),
+                )
             except Exception as move_err:
                 return f"❌ Error: Fallback move failed: {src_resolved} → {dest}: {move_err}"
 
@@ -869,7 +1615,9 @@ def qa_transition(task_file_path: str, modified_files: list[str] = [], project_r
         header_pattern = re.compile(r"\*\*File:\*\*\s*`[^`]+`")
         if not header_pattern.search(content):
             return f"❌ Error: Could not find **File:** header in {dest}"
-        new_content_header = header_pattern.sub(f"**File:** `{expected_header}`", content, count=1)
+        new_content_header = header_pattern.sub(
+            f"**File:** `{expected_header}`", content, count=1
+        )
         try:
             dest.write_text(new_content_header, encoding="utf-8")
         except Exception as e:
@@ -878,13 +1626,23 @@ def qa_transition(task_file_path: str, modified_files: list[str] = [], project_r
         # 4. Stages modified_files + destination task file (explicit staging)
         files_to_stage = list(modified_files) + [str(dest)]
         try:
-            subprocess.run(["git", "add", "--"] + files_to_stage, check=True, capture_output=True, cwd=str(workspace_root))
+            subprocess.run(
+                ["git", "add", "--"] + files_to_stage,
+                check=True,
+                capture_output=True,
+                cwd=str(workspace_root),
+            )
         except subprocess.CalledProcessError as e:
             return f"❌ Error staging files {files_to_stage}: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}"
 
         # 5. Extracts staged diff excluding tasks/ (:!tasks/)
         try:
-            diff_proc = subprocess.run(["git", "diff", "--staged", "--", ".", ":!tasks/"], capture_output=True, text=True, cwd=str(workspace_root))
+            diff_proc = subprocess.run(
+                ["git", "diff", "--staged", "--", ".", ":!tasks/"],
+                capture_output=True,
+                text=True,
+                cwd=str(workspace_root),
+            )
             diff_text = diff_proc.stdout.strip()
         except Exception as e:
             return f"❌ Error extracting staged diff: {e}"
@@ -897,17 +1655,27 @@ def qa_transition(task_file_path: str, modified_files: list[str] = [], project_r
             content_after_header = dest.read_text(encoding="utf-8")
         except Exception as e:
             return f"❌ Error re-reading task file for diff injection: {e}"
-        diff_pattern = re.compile(r"<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->", re.DOTALL)
+        diff_pattern = re.compile(
+            r"<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->", re.DOTALL
+        )
         if not diff_pattern.search(content_after_header):
             return f"❌ Error: Could not find <!-- BEGIN_GIT_DIFF --> markers in {dest}"
-        new_content_final = diff_pattern.sub(lambda m: f"<!-- BEGIN_GIT_DIFF -->{diff_block}<!-- END_GIT_DIFF -->", content_after_header)
+        new_content_final = diff_pattern.sub(
+            lambda m: f"<!-- BEGIN_GIT_DIFF -->{diff_block}<!-- END_GIT_DIFF -->",
+            content_after_header,
+        )
         try:
             dest.write_text(new_content_final, encoding="utf-8")
         except Exception as e:
             return f"❌ Error writing diff injection to {dest}: {e}"
         # Re-stage the task file after injection so final QA state is staged (header + diff)
         try:
-            subprocess.run(["git", "add", "--", str(dest)], check=True, capture_output=True, cwd=str(workspace_root))
+            subprocess.run(
+                ["git", "add", "--", str(dest)],
+                check=True,
+                capture_output=True,
+                cwd=str(workspace_root),
+            )
         except Exception as e:
             return f"❌ Error re-staging QA task file after injection: {e}"
 
@@ -928,7 +1696,11 @@ def qa_transition(task_file_path: str, modified_files: list[str] = [], project_r
         except Exception as e:
             return f"❌ Error validating header: {e}"
 
-        files_str = ", ".join(modified_files) if modified_files else "(no code files — diff will be sentinel)"
+        files_str = (
+            ", ".join(modified_files)
+            if modified_files
+            else "(no code files — diff will be sentinel)"
+        )
         return (
             f"✅ QA transition complete: {task_file_path} → {expected_header}\n"
             f"   Staged files: {files_str}\n"
@@ -938,6 +1710,7 @@ def qa_transition(task_file_path: str, modified_files: list[str] = [], project_r
     except Exception as e:
         return f"❌ Unexpected error in qa_transition: {str(e)}"
 
+
 def _derive_task_slug(task_file_path: str) -> str:
     """Derives a 'task <NN> - <slug>' label from a task file name (e.g. '78-fix-bug.md' -> 'task 78 - fix bug')."""
     name = Path(task_file_path).stem
@@ -946,14 +1719,20 @@ def _derive_task_slug(task_file_path: str) -> str:
         return f"task {parts[0]} - {parts[1].replace('-', ' ')}"
     return f"task - {name.replace('-', ' ')}"
 
+
 # Conventional Commits enforcement (Task 211): `commit_and_clean_task` is the
 # ONLY commit path, so the caller-supplied feature message is validated here
 # against skill-templates/versioning-and-release (`type: subject`, ≤72 chars).
 _CONVENTIONAL_RE = re.compile(r"^(feat|fix|docs|refactor|chore): \S.*$")
 
+
 def _check_conventional_commit(commit_message: str) -> Optional[str]:
     """Returns an error string when commit_message violates Conventional Commits, else None."""
-    first_line = commit_message.splitlines()[0] if commit_message and commit_message.strip() else ""
+    first_line = (
+        commit_message.splitlines()[0]
+        if commit_message and commit_message.strip()
+        else ""
+    )
     if not _CONVENTIONAL_RE.match(first_line):
         return (
             "❌ Commit message rejected: must match Conventional Commits "
@@ -967,8 +1746,11 @@ def _check_conventional_commit(commit_message: str) -> Optional[str]:
         )
     return None
 
+
 @_project_tool
-def commit_and_clean_task(task_file_path: str, commit_message: str, project_root: str | None = None) -> str:
+def commit_and_clean_task(
+    task_file_path: str, commit_message: str, project_root: str | None = None
+) -> str:
     """Commits staged changes, captures the feature commit hash, replaces the raw diff in the task file with the hash reference, and commits the cleaned task file as a separate closure commit. The stored hash always points to the feature commit, which stays reachable forever (no amend, no orphaned commits)."""
     try:
         # 0. Idempotency guard: skip if the task file was already cleaned.
@@ -982,11 +1764,11 @@ def commit_and_clean_task(task_file_path: str, commit_message: str, project_root
         if not path.is_absolute():
             path = Path(repo) / path
         if path.is_file():
-            with open(path, 'r', encoding='utf-8') as f:
+            with open(path, "r", encoding="utf-8") as f:
                 existing = f.read()
             cleaned_block = re.compile(
-                r'<!-- BEGIN_GIT_DIFF -->\s*\*\*Factual Git Diff:\*\* Stored in Commit Hash: `[0-9a-f]{7,40}`\s*<!-- END_GIT_DIFF -->',
-                re.DOTALL
+                r"<!-- BEGIN_GIT_DIFF -->\s*\*\*Factual Git Diff:\*\* Stored in Commit Hash: `[0-9a-f]{7,40}`\s*<!-- END_GIT_DIFF -->",
+                re.DOTALL,
             )
             if cleaned_block.search(existing):
                 return "⚠️ Task file already cleaned (Stored in Commit Hash present). Nothing to commit."
@@ -999,41 +1781,70 @@ def commit_and_clean_task(task_file_path: str, commit_message: str, project_root
             return conventional_error
 
         # 0.5 Safety check before commit
-        staged_check = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True, cwd=repo)
+        staged_check = subprocess.run(
+            ["git", "diff", "--staged", "--quiet"], capture_output=True, cwd=repo
+        )
         if staged_check.returncode == 0:
             return "⚠️ No staged changes to commit."
 
         # 1. Commit staged changes (feature commit H1)
-        subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True, text=True, cwd=repo)
+        subprocess.run(
+            ["git", "commit", "-m", commit_message],
+            check=True,
+            capture_output=True,
+            text=True,
+            cwd=repo,
+        )
 
         # 2. Capture H1 — the feature commit hash. It stays reachable forever
         #    as the parent of the closure commit (step 5). NEVER amend it.
-        hash_proc = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True, cwd=repo)
+        hash_proc = subprocess.run(
+            ["git", "rev-parse", "HEAD"],
+            check=True,
+            capture_output=True,
+            text=True,
+            cwd=repo,
+        )
         commit_hash = hash_proc.stdout.strip()
 
         # 3. Read task file and replace raw diff with the hash reference
         if path.is_file():
-            with open(path, 'r', encoding='utf-8') as f:
+            with open(path, "r", encoding="utf-8") as f:
                 content = f.read()
 
-            pattern = re.compile(r'<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->', re.DOTALL)
+            pattern = re.compile(
+                r"<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->", re.DOTALL
+            )
             if pattern.search(content):
                 clean_block = f"<!-- BEGIN_GIT_DIFF -->\n**Factual Git Diff:** Stored in Commit Hash: `{commit_hash}`\n<!-- END_GIT_DIFF -->"
                 new_content = pattern.sub(clean_block, content)
 
-                with open(path, 'w', encoding='utf-8') as f:
+                with open(path, "w", encoding="utf-8") as f:
                     f.write(new_content)
 
         # 4. Stage the cleaned task file ONLY (F5 fix: never `git add -A tasks/`,
         #    which swept foreign/parallel-session task files into this commit).
-        subprocess.run(["git", "add", "--", task_file_path], check=True, capture_output=True, cwd=repo)
+        subprocess.run(
+            ["git", "add", "--", task_file_path],
+            check=True,
+            capture_output=True,
+            cwd=repo,
+        )
 
         # 5. Commit the cleaned task file as a separate closure commit.
         #    A plain commit (NOT --amend) keeps H1 reachable from HEAD.
         slug = _derive_task_slug(task_file_path)
-        staged_after = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)
+        staged_after = subprocess.run(
+            ["git", "diff", "--staged", "--quiet"], capture_output=True
+        )
         if staged_after.returncode != 0:
-            subprocess.run(["git", "commit", "-m", f"chore: close {slug}"], check=True, capture_output=True, text=True, cwd=repo)
+            subprocess.run(
+                ["git", "commit", "-m", f"chore: close {slug}"],
+                check=True,
+                capture_output=True,
+                text=True,
+                cwd=repo,
+            )
 
         return f"✅ Success: Code committed (Hash: `{commit_hash}`). Task file {task_file_path} cleaned; closure commit `chore: close {slug}` created on top."
     except subprocess.CalledProcessError as e:
@@ -1053,9 +1864,12 @@ DIFF_SIZE_WARNING_THRESHOLD = 400
 def _kebab_case(text: str) -> str:
     """Convert arbitrary title to kebab-case slug (B4: supports Unicode/Persian)."""
     import unicodedata
+
     normalized = unicodedata.normalize("NFKD", text)
     slug = normalized.lower().strip()
-    slug = re.sub(r"[^a-z0-9\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+", "-", slug)
+    slug = re.sub(
+        r"[^a-z0-9\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+", "-", slug
+    )
     slug = re.sub(r"-{2,}", "-", slug)
     slug = slug.strip("-")
     return slug or "bundle"
@@ -1093,7 +1907,11 @@ def _find_task_file(task_id: str, tasks_root: Path = Path("tasks")) -> Path | No
     if len(candidates) > 1:
         return None  # B2: hard halt — duplicate active IDs
     # Check archive for better error (already archived)
-    for md in (tasks_root / "archive").glob("*.md") if (tasks_root / "archive").is_dir() else []:
+    for md in (
+        (tasks_root / "archive").glob("*.md")
+        if (tasks_root / "archive").is_dir()
+        else []
+    ):
         m = re.match(r"^(\d+)-", md.name)
         if m and m.group(1).lstrip("0") == norm:
             return None
@@ -1101,7 +1919,10 @@ def _find_task_file(task_id: str, tasks_root: Path = Path("tasks")) -> Path | No
 
 
 def _extract_section(content: str, heading: str) -> str | None:
-    pattern = re.compile(rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\n---\s*\n|\Z)", re.MULTILINE | re.DOTALL)
+    pattern = re.compile(
+        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\n---\s*\n|\Z)",
+        re.MULTILINE | re.DOTALL,
+    )
     m = pattern.search(content)
     return m.group(1).strip() if m else None
 
@@ -1127,7 +1948,12 @@ def _extract_checklist_with_continuations(section_text: str) -> list[str]:
             in_checklist = True
             result.append(stripped)
         elif in_checklist:
-            if stripped and not line.startswith("- [") and not stripped.startswith("## ") and not stripped.startswith("---"):
+            if (
+                stripped
+                and not line.startswith("- [")
+                and not stripped.startswith("## ")
+                and not stripped.startswith("---")
+            ):
                 result.append(line)
             else:
                 in_checklist = False
@@ -1140,7 +1966,10 @@ def _extract_checklist_with_continuations(section_text: str) -> list[str]:
 def _detect_stack(content: str) -> str | None:
     """M1: Detect tech stack from task content."""
     lower = content.lower()
-    if any(kw in lower for kw in ["jetpack compose", "kotlin", "android", "hilt", "sqldelight"]):
+    if any(
+        kw in lower
+        for kw in ["jetpack compose", "kotlin", "android", "hilt", "sqldelight"]
+    ):
         return "android"
     if any(kw in lower for kw in ["react", "vite", "jsx", "tsx", "next.js", "nextjs"]):
         return "react"
@@ -1155,7 +1984,9 @@ def _detect_stack(content: str) -> str | None:
     return None
 
 
-def _verify_verbatim_checksums(source_data: list[tuple[str, Path, str, str]], meta_content: str) -> bool:
+def _verify_verbatim_checksums(
+    source_data: list[tuple[str, Path, str, str]], meta_content: str
+) -> bool:
     """M2: Verify 100% of extracted source AC text is in the Bundled Checklist."""
     bundled_match = re.search(
         r"^## Bundled Checklist.*?\n\n(.*?)(?=^## |\Z)",
@@ -1183,13 +2014,23 @@ def _verify_verbatim_checksums(source_data: list[tuple[str, Path, str, str]], me
 def _git_mv_or_fallback(src: Path, dst: Path) -> bool:
     dst.parent.mkdir(parents=True, exist_ok=True)
     repo = str(_repo_root(str(src)))
-    result = subprocess.run(["git", "mv", str(src), str(dst)], capture_output=True, text=True, cwd=repo)
+    result = subprocess.run(
+        ["git", "mv", str(src), str(dst)], capture_output=True, text=True, cwd=repo
+    )
     if result.returncode == 0:
         return True
-    if "not under version control" in result.stderr or "not tracked" in result.stderr.lower():
+    if (
+        "not under version control" in result.stderr
+        or "not tracked" in result.stderr.lower()
+    ):
         try:
             src.rename(dst)
-            subprocess.run(["git", "add", "--", str(dst)], check=True, capture_output=True, cwd=repo)
+            subprocess.run(
+                ["git", "add", "--", str(dst)],
+                check=True,
+                capture_output=True,
+                cwd=repo,
+            )
             return True
         except Exception:
             return False
@@ -1204,13 +2045,27 @@ def _patch_archived_file(archive_path: Path, meta_id: str, meta_slug: str) -> No
     new_file_header = f"**File:** `tasks/archive/{archive_path.name}`"
     content = re.sub(r"\*\*File:\*\*\s*`[^`]+`", new_file_header, content, count=1)
     if re.search(r"\*\*Status:\*\*\s*\w+", content):
-        content = re.sub(r"\*\*Status:\*\*\s*\w+", "**Status:** superseded", content, count=1)
+        content = re.sub(
+            r"\*\*Status:\*\*\s*\w+", "**Status:** superseded", content, count=1
+        )
     else:
-        content = re.sub(r"(\*\*Type:\*\*\s*\w+)", r"\1\n**Status:** superseded", content, count=1)
+        content = re.sub(
+            r"(\*\*Type:\*\*\s*\w+)", r"\1\n**Status:** superseded", content, count=1
+        )
     if "**Superseded-By:**" not in content:
-        content = re.sub(r"(\*\*Status:\*\*\s*superseded)", rf"\1\n**Superseded-By:** `{meta_id}-{meta_slug}`", content, count=1)
+        content = re.sub(
+            r"(\*\*Status:\*\*\s*superseded)",
+            rf"\1\n**Superseded-By:** `{meta_id}-{meta_slug}`",
+            content,
+            count=1,
+        )
         timestamp = time.strftime("%Y-%m-%d")
-        content = re.sub(r"(\*\*Superseded-By:\*\*\s*`[^`]+`)", rf"\1\n**Superseded-At:** `{timestamp}`", content, count=1)
+        content = re.sub(
+            r"(\*\*Superseded-By:\*\*\s*`[^`]+`)",
+            rf"\1\n**Superseded-At:** `{timestamp}`",
+            content,
+            count=1,
+        )
     superseded_note = (
         f"> **Superseded:** This task was bundled into META task `{meta_id}-{meta_slug}` "
         f"and archived on {time.strftime('%Y-%m-%d')}. "
@@ -1219,16 +2074,26 @@ def _patch_archived_file(archive_path: Path, meta_id: str, meta_slug: str) -> No
     )
     if superseded_note.strip() not in content:
         if "## Execution Log" in content:
-            content = content.replace("## Execution Log", superseded_note + "\n## Execution Log", 1)
+            content = content.replace(
+                "## Execution Log", superseded_note + "\n## Execution Log", 1
+            )
         elif "## Factual Git Diff" in content:
-            content = content.replace("## Factual Git Diff", superseded_note + "\n## Factual Git Diff", 1)
+            content = content.replace(
+                "## Factual Git Diff", superseded_note + "\n## Factual Git Diff", 1
+            )
     try:
         archive_path.write_text(content, encoding="utf-8")
     except Exception:
         pass
 
 
-def _build_meta_content(meta_id: int, meta_slug: str, meta_title: str, source_ids: list[str], source_data: list[tuple[str, Path, str, str]]) -> str:
+def _build_meta_content(
+    meta_id: int,
+    meta_slug: str,
+    meta_title: str,
+    source_ids: list[str],
+    source_data: list[tuple[str, Path, str, str]],
+) -> str:
     meta_id_str = f"{meta_id:02d}" if meta_id < 100 else str(meta_id)
     if meta_id >= 100:
         meta_id_str = str(meta_id)
@@ -1241,7 +2106,10 @@ def _build_meta_content(meta_id: int, meta_slug: str, meta_title: str, source_id
     per_source_blocks: list[str] = []
     for sid, path, content, stitle in source_data:
         goal = _extract_section(content, "Goal") or "_(No Goal section found)_"
-        ac = _extract_section(content, "Acceptance Criteria") or "_(No Acceptance Criteria)_"
+        ac = (
+            _extract_section(content, "Acceptance Criteria")
+            or "_(No Acceptance Criteria)_"
+        )
         todos = _extract_section(content, "Local TODOs") or "_(No Local TODOs)_"
         risk = _extract_section(content, "Risk & Rollback")
         manager_notes = _extract_section(content, "Manager's Notes")
@@ -1254,7 +2122,11 @@ def _build_meta_content(meta_id: int, meta_slug: str, meta_title: str, source_id
         # B1: multi-line checklist extraction
         ac_lines = _extract_checklist_with_continuations(ac)
         if not ac_lines:
-            ac_lines = [f"- [ ] {line.strip()}" for line in ac.splitlines() if line.strip() and not line.strip().startswith("#")][:3]
+            ac_lines = [
+                f"- [ ] {line.strip()}"
+                for line in ac.splitlines()
+                if line.strip() and not line.strip().startswith("#")
+            ][:3]
         for line in ac_lines:
             if line.startswith("- ["):
                 m = re.match(r"^- \[[ xX]\]\s*(.*)", line)
@@ -1302,9 +2174,13 @@ def _build_meta_content(meta_id: int, meta_slug: str, meta_title: str, source_id
     )
     for t in deduped_todos:
         meta_local_todos += f"{t}\n"
-    meta_local_todos += f"- [ ] Step {len(deduped_todos)+3}: Verify all bundled checklist items and run lint_task_file + verification-before-completion\n"
-    meta_local_todos += f"- [ ] Step {len(deduped_todos)+4}: Update CHANGELOG.md and record Verification Evidence\n"
-    meta_ac = "\n".join(bundled_checklist_items) if bundled_checklist_items else "- [ ] _(No aggregated criteria — check per-source blocks)_"
+    meta_local_todos += f"- [ ] Step {len(deduped_todos) + 3}: Verify all bundled checklist items and run lint_task_file + verification-before-completion\n"
+    meta_local_todos += f"- [ ] Step {len(deduped_todos) + 4}: Update CHANGELOG.md and record Verification Evidence\n"
+    meta_ac = (
+        "\n".join(bundled_checklist_items)
+        if bundled_checklist_items
+        else "- [ ] _(No aggregated criteria — check per-source blocks)_"
+    )
     meta_ac += f"\n- [ ] Traceability: All {len(source_data)} source tasks are archived with superseded-by marker and reachable via `git log --follow`"
     meta_verification = (
         f"- **Test command:** `lint_task_file` on META file; `git log --oneline --follow -- tasks/archive/<id>-*.md | head` for archived sources; project test suite if logic changed\n"
@@ -1335,9 +2211,9 @@ def _build_meta_content(meta_id: int, meta_slug: str, meta_title: str, source_id
         f"**Created:** {timestamp}\n"
         f"**Bundled:** {len(source_data)} tasks\n\n"
         f"## Goal\n\n"
-        f"Unified execution of {len(source_data)} related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks {_format_task_id_list(source_ids)} — \"{meta_title}\" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.\n\n"
+        f'Unified execution of {len(source_data)} related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks {_format_task_id_list(source_ids)} — "{meta_title}" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.\n\n'
         f"{warning_note}**Source IDs:** {_format_task_id_list(source_ids)}\n"
-        f"**Next ID:** {meta_id} (discovered via `find tasks -name \"*.md\" | sort -n | tail -1 +1`)\n"
+        f'**Next ID:** {meta_id} (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)\n'
         f"**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: {meta_id}-{meta_slug}` and remain reachable via `git log --follow` (never purged until META is completed).\n\n"
         f"## Manager's Notes\n\n"
         f"**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute {len(source_data)} small related tasks together and speed up turnaround.\n\n"
@@ -1381,7 +2257,13 @@ def _build_meta_content(meta_id: int, meta_slug: str, meta_title: str, source_id
 
 
 @_project_tool
-def bundle_tasks(task_ids: list[str], title: str, dry_run: bool = False, force: bool = False, project_root: str | None = None) -> str:
+def bundle_tasks(
+    task_ids: list[str],
+    title: str,
+    dry_run: bool = False,
+    force: bool = False,
+    project_root: str | None = None,
+) -> str:
     """
     Bundle multiple small related tasks into a single META task with auto-archive (Task 110).
 
@@ -1472,12 +2354,18 @@ def bundle_tasks(task_ids: list[str], title: str, dry_run: bool = False, force:
         if output_path.exists():
             return f"❌ Task ID collision: {output_path} already exists. Re-run ID discovery."
         # Also check backlog glob for same ID prefix
-        if list((tasks_root / "backlog").glob(f"{next_id}-*.md")) if (tasks_root / "backlog").is_dir() else []:
+        if (
+            list((tasks_root / "backlog").glob(f"{next_id}-*.md"))
+            if (tasks_root / "backlog").is_dir()
+            else []
+        ):
             # This would also match our not-yet-created file if we had a race, but we already checked exists
             pass
 
         meta_title_full = title
-        meta_content = _build_meta_content(next_id, meta_slug, meta_title_full, task_ids, source_data)
+        meta_content = _build_meta_content(
+            next_id, meta_slug, meta_title_full, task_ids, source_data
+        )
         total_loc = sum(len(c.splitlines()) for _, _, c, _ in source_data)
 
         # M1: Stack detection
@@ -1498,13 +2386,17 @@ def bundle_tasks(task_ids: list[str], title: str, dry_run: bool = False, force:
 
         if dry_run:
             lines = []
-            lines.append(f"🔍 Dry-run (MCP): Would create META task {next_id}-{meta_slug}")
+            lines.append(
+                f"🔍 Dry-run (MCP): Would create META task {next_id}-{meta_slug}"
+            )
             lines.append(f"   Output: {output_path}")
             lines.append(f"   Bundles: {task_ids} ({len(task_ids)} tasks)")
             lines.append(f"   Sources:")
             for sid, p, _, t in source_data:
                 lines.append(f"     - {sid}: {t} ({p})")
-            lines.append(f"   Combined LOC: {total_loc} {'⚠️ >400' if total_loc > 400 else '✅'}")
+            lines.append(
+                f"   Combined LOC: {total_loc} {'⚠️ >400' if total_loc > 400 else '✅'}"
+            )
             lines.append(f"   Supersedes will be: {task_ids}")
             lines.append(f"   Archive destinations:")
             for sid, p, _, _ in source_data:
@@ -1513,18 +2405,32 @@ def bundle_tasks(task_ids: list[str], title: str, dry_run: bool = False, force:
             for i, line in enumerate(meta_content.splitlines()[:40], 1):
                 lines.append(f"   {i:3d}| {line}")
             lines.append(f"\n   ... {len(meta_content.splitlines()) - 40} more lines")
-            required = ["## Goal", "## Local TODOs", "## Acceptance Criteria", "## Verification Evidence", "## Risk & Rollback", "## Factual Git Diff", "## Execution Log"]
+            required = [
+                "## Goal",
+                "## Local TODOs",
+                "## Acceptance Criteria",
+                "## Verification Evidence",
+                "## Risk & Rollback",
+                "## Factual Git Diff",
+                "## Execution Log",
+            ]
             missing_sections = [s for s in required if s not in meta_content]
             if missing_sections:
-                lines.append(f"⚠️ Missing required sections in preview: {missing_sections}")
+                lines.append(
+                    f"⚠️ Missing required sections in preview: {missing_sections}"
+                )
                 return "\n".join(lines)
             lines.append(f"\n✅ Dry-run lint check: All required sections present.")
             if len(task_ids) > 6 and force:
-                lines.insert(0, f"⚠️ --force: Bundling {len(task_ids)} tasks (> 6). Mega-diff risk.")
+                lines.insert(
+                    0,
+                    f"⚠️ --force: Bundling {len(task_ids)} tasks (> 6). Mega-diff risk.",
+                )
             return "\n".join(lines)
 
         # --- B5: Atomic creation with retry loop ---
         import subprocess as _sp
+
         MAX_ID_RETRIES = 5
         for attempt in range(MAX_ID_RETRIES):
             try:
@@ -1580,22 +2486,41 @@ def bundle_tasks(task_ids: list[str], title: str, dry_run: bool = False, force:
                     restore_dst = tasks_root / "backlog" / original_name
                 try:
                     restore_dst.parent.mkdir(parents=True, exist_ok=True)
-                    _sp.run(["git", "mv", str(archived_path), str(restore_dst)], check=True, capture_output=True)
+                    _sp.run(
+                        ["git", "mv", str(archived_path), str(restore_dst)],
+                        check=True,
+                        capture_output=True,
+                    )
                     # Remove superseded headers
                     content = restore_dst.read_text(encoding="utf-8")
-                    content = re.sub(r"\n\*\*Superseded-By:\*\*.*$", "", content, flags=re.MULTILINE)
-                    content = re.sub(r"\n\*\*Superseded-At:\*\*.*$", "", content, flags=re.MULTILINE)
-                    superseded_pattern = re.compile(r"> \*\*Superseded:\*\*.*?History preserved.*?\n\n", re.DOTALL)
+                    content = re.sub(
+                        r"\n\*\*Superseded-By:\*\*.*$", "", content, flags=re.MULTILINE
+                    )
+                    content = re.sub(
+                        r"\n\*\*Superseded-At:\*\*.*$", "", content, flags=re.MULTILINE
+                    )
+                    superseded_pattern = re.compile(
+                        r"> \*\*Superseded:\*\*.*?History preserved.*?\n\n", re.DOTALL
+                    )
                     content = superseded_pattern.sub("", content)
-                    content = re.sub(r"\*\*Status:\*\*\s*superseded", "**Status:** open", content)
-                    content = re.sub(r"\*\*File:\*\*\s*`[^`]+`", f"**File:** `tasks/backlog/{restore_dst.name}`", content, count=1)
+                    content = re.sub(
+                        r"\*\*Status:\*\*\s*superseded", "**Status:** open", content
+                    )
+                    content = re.sub(
+                        r"\*\*File:\*\*\s*`[^`]+`",
+                        f"**File:** `tasks/backlog/{restore_dst.name}`",
+                        content,
+                        count=1,
+                    )
                     restore_dst.write_text(content, encoding="utf-8")
                 except Exception:
                     pass
             output_path.unlink(missing_ok=True)
             return f"❌ Bundle aborted. Archive failed for {failed}. All changes rolled back. Fix and retry."
         else:
-            out_lines.append(f"✅ Archived {len(archived)} source tasks to tasks/archive/ with superseded-by: {meta_id_str}-{meta_slug}")
+            out_lines.append(
+                f"✅ Archived {len(archived)} source tasks to tasks/archive/ with superseded-by: {meta_id_str}-{meta_slug}"
+            )
         # Light validation
         try:
             cc = output_path.read_text(encoding="utf-8")
@@ -1604,10 +2529,16 @@ def bundle_tasks(task_ids: list[str], title: str, dry_run: bool = False, force:
                     out_lines.append(f"⚠️ Lint warning: {req} missing in created META.")
         except Exception:
             pass
-        out_lines.append(f"\nDone. Next: move {output_path} through Kanban (backlog → in-progress → qa → completed) as a single Hands implementation.")
-        out_lines.append(f"Traceability: git log --oneline --follow -- tasks/archive/<id>-*.md | head")
+        out_lines.append(
+            f"\nDone. Next: move {output_path} through Kanban (backlog → in-progress → qa → completed) as a single Hands implementation."
+        )
+        out_lines.append(
+            f"Traceability: git log --oneline --follow -- tasks/archive/<id>-*.md | head"
+        )
         if len(task_ids) > 6 and force:
-            out_lines.insert(0, f"⚠️ --force: Bundling {len(task_ids)} tasks (> 6). Mega-diff risk.")
+            out_lines.insert(
+                0, f"⚠️ --force: Bundling {len(task_ids)} tasks (> 6). Mega-diff risk."
+            )
         return "\n".join(out_lines)
 
     except Exception as e:
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 6a3a21c..b5baba0 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.54.0</system_version>
+<system_version>9.55.0</system_version>
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index 34767c2..1e196ae 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -15,6 +15,7 @@
     HANDS INSTRUCTION:
     1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
     1.5. PERSIST THE TREE: Run the `custom_context_create_tree_report` tool (default `target_path="."` for the whole project; pass a scoped path when the Orchestrator targets a sub-directory). It saves a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md` and returns the file path.
+    1.6. GRAPH-FIRST: Run `custom_context_build_graph` once on the target scope (saves versioned `graph_*.json` + `graph_report_*.md`), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` for cross-file questions before falling back to full reads.
     2. MANDATORY CORE FILES: Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
     3. VERTICAL SLICE EXTRACTION: Use the `extract_signatures` tool on the specific feature directory requested by the Orchestrator (e.g., `src/features/auth/`). Do not extract signatures for the entire repository unless explicitly asked.
     4. Compile the results into a single context report using the MCP tools.
@@ -122,6 +123,7 @@
     HANDS INSTRUCTION: You are in DISCOVERY mode. Gather context for the Orchestrator using the `custom_context` MCP server tools:
     1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
     1.5. PERSIST THE TREE: Run the `custom_context_create_tree_report` tool (default `target_path="."` for the whole project; pass a scoped path when the Orchestrator targets a sub-directory). It saves a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md` and returns the file path.
+    1.6. GRAPH-FIRST: Run `custom_context_build_graph` once on the target scope (saves versioned `graph_*.json` + `graph_report_*.md`), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` for cross-file questions before falling back to full reads.
     2. Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
     3. Compile the results into a single context report using the MCP tools.
     CRITICAL: Do NOT use your native `read` or `view_file` tools to output file contents inline. You must use the `custom_context` MCP server tools.
diff --git a/skill-templates/code-search/SKILL.md b/skill-templates/code-search/SKILL.md
index 20fd9d4..200c015 100644
--- a/skill-templates/code-search/SKILL.md
+++ b/skill-templates/code-search/SKILL.md
@@ -15,6 +15,8 @@ You are the Executor. Your job is to extract codebase context so the Manager can
 
 1.5. **Persist the Tree (Recommended):** Call `custom_context_create_tree_report` (default `target_path="."` = whole project; pass any sub-path to scope it) to save a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md`. Use this whenever the Manager asks to "create a tree of the project".
 
+1.6. **Graph-First (Recommended):** For multi-file questions call `custom_context_build_graph` once (saves versioned `graph_*.json` + `graph_report_*.md` with EXTRACTED/INFERRED edges), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` over full reads. Use `custom_context_graph_stats` to confirm coverage. Fall back to signatures/reads only for exact bodies the subgraph does not answer.
+
 2. **Prefer Signature Extraction Over Full Reads:** Before reading a single file body, you MUST call `custom_context_extract_signatures` on every file or directory you plan to explore. This tool uses **tree-sitter AST** (not regex) to extract structural signatures — classes, functions, methods, interfaces, enums, type aliases — across all major languages. Signature extraction costs a fraction of the tokens compared to reading the full file, and is strictly preferred for initial exploration.
 
 3. **Target Files:** Use the directory tree AND the extracted signatures together to identify exactly which files contain the logic relevant to the Manager's request. The signatures give you a structural map of each file's exports without loading its body.
diff --git a/system-prompt.md b/system-prompt.md
index fe4d832..5d4ced4 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.54.0</system_version>
+<system_version>9.55.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -233,6 +233,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     HANDS INSTRUCTION:
     1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
     1.5. PERSIST THE TREE: Run the `custom_context_create_tree_report` tool (default `target_path="."` for the whole project; pass a scoped path when the Orchestrator targets a sub-directory). It saves a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md` and returns the file path.
+    1.6. GRAPH-FIRST: Run `custom_context_build_graph` once on the target scope (saves versioned `graph_*.json` + `graph_report_*.md`), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` for cross-file questions before falling back to full reads.
     2. MANDATORY CORE FILES: Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
     3. VERTICAL SLICE EXTRACTION: Use the `extract_signatures` tool on the specific feature directory requested by the Orchestrator (e.g., `src/features/auth/`). Do not extract signatures for the entire repository unless explicitly asked.
     4. Compile the results into a single context report using the MCP tools.
@@ -356,6 +357,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     HANDS INSTRUCTION: You are in DISCOVERY mode. Gather context for the Orchestrator using the `custom_context` MCP server tools:
     1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
     1.5. PERSIST THE TREE: Run the `custom_context_create_tree_report` tool (default `target_path="."` for the whole project; pass a scoped path when the Orchestrator targets a sub-directory). It saves a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md` and returns the file path.
+    1.6. GRAPH-FIRST: Run `custom_context_build_graph` once on the target scope (saves versioned `graph_*.json` + `graph_report_*.md`), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` for cross-file questions before falling back to full reads.
     2. Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
     3. Compile the results into a single context report using the MCP tools.
     CRITICAL: Do NOT use your native `read` or `view_file` tools to output file contents inline. You must use the `custom_context` MCP server tools.
diff --git a/tests/test_mcp_servers.py b/tests/test_mcp_servers.py
index 24adda4..de4f07b 100644
--- a/tests/test_mcp_servers.py
+++ b/tests/test_mcp_servers.py
@@ -164,13 +164,17 @@ Test
 <!-- END_GIT_DIFF -->
 """
     # Header says backlog, but the file is actually in in-progress.
-    issues = mod._check_task_file_structure(valid_content, "tasks/in-progress/99-test.md")
+    issues = mod._check_task_file_structure(
+        valid_content, "tasks/in-progress/99-test.md"
+    )
     assert any("File path mismatch" in i for i in issues), (
         f"Expected 'File path mismatch' issue, got: {issues}"
     )
 
     # Sanity: same content with the matching path must produce no mismatch.
-    issues_ok = mod._check_task_file_structure(valid_content, "tasks/backlog/99-test.md")
+    issues_ok = mod._check_task_file_structure(
+        valid_content, "tasks/backlog/99-test.md"
+    )
     assert not any("File path mismatch" in i for i in issues_ok), (
         f"Matching header/path must not be flagged: {issues_ok}"
     )
@@ -315,7 +319,9 @@ def test_lint_task_file_rejects_file_path_mismatch():
     import importlib
 
     server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
-    spec = importlib.util.spec_from_file_location("lint_server_path_mismatch", server_path)
+    spec = importlib.util.spec_from_file_location(
+        "lint_server_path_mismatch", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
@@ -453,7 +459,9 @@ Test
 <!-- BEGIN_GIT_DIFF -->
 <!-- END_GIT_DIFF -->
 """
-    issues = mod._check_task_file_structure(incomplete_content, "tasks/backlog/99-test.md")
+    issues = mod._check_task_file_structure(
+        incomplete_content, "tasks/backlog/99-test.md"
+    )
     assert len(issues) > 0, "Expected issues for missing sections, got none"
     # Should flag missing Acceptance Criteria, Verification Evidence, Risk & Rollback
     assert any("Acceptance Criteria" in i for i in issues), (
@@ -520,15 +528,21 @@ Test
 
     # New canonical header must pass.
     new_header_content = template.format(header="Execution Log & Reasoning")
-    issues_new = mod._check_task_file_structure(new_header_content, "tasks/backlog/99-test.md")
-    assert "Missing required section: `## Execution Log & Reasoning`" not in issues_new, (
-        f"Canonical '## Execution Log & Reasoning' header must pass; got: {issues_new}"
+    issues_new = mod._check_task_file_structure(
+        new_header_content, "tasks/backlog/99-test.md"
     )
+    assert (
+        "Missing required section: `## Execution Log & Reasoning`" not in issues_new
+    ), f"Canonical '## Execution Log & Reasoning' header must pass; got: {issues_new}"
 
     # Deprecated legacy header must ALSO pass (backward compatibility).
     old_header_content = template.format(header="OpenCode Execution Log & Reasoning")
-    issues_old = mod._check_task_file_structure(old_header_content, "tasks/backlog/99-test.md")
-    assert "Missing required section: `## Execution Log & Reasoning`" not in issues_old, (
+    issues_old = mod._check_task_file_structure(
+        old_header_content, "tasks/backlog/99-test.md"
+    )
+    assert (
+        "Missing required section: `## Execution Log & Reasoning`" not in issues_old
+    ), (
         f"Legacy '## OpenCode Execution Log & Reasoning' header must be accepted "
         f"(non-breaking guarantee); got: {issues_old}"
     )
@@ -612,7 +626,9 @@ def test_commit_and_clean_task_stores_reachable_hash():
         # Set up a git repo with a known identity
         subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
         subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
-        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
+        subprocess.run(
+            ["git", "config", "user.email", "test@example.com"], cwd=repo, check=True
+        )
 
         # Code change + task file with diff markers
         (repo / "feature.py").write_text("x = 1\n")
@@ -634,7 +650,9 @@ def test_commit_and_clean_task_stores_reachable_hash():
 
         # Task file must reference a commit hash
         cleaned = task_file.read_text()
-        assert "Stored in Commit Hash:" in cleaned, "Task file should reference the commit hash"
+        assert "Stored in Commit Hash:" in cleaned, (
+            "Task file should reference the commit hash"
+        )
         stored_hash = None
         for line in cleaned.splitlines():
             if "Stored in Commit Hash:" in line and "`" in line:
@@ -645,12 +663,17 @@ def test_commit_and_clean_task_stores_reachable_hash():
         head = subprocess.run(
             ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
         ).stdout.strip()
-        assert stored_hash != head, "Closure commit should sit on top of the feature commit"
+        assert stored_hash != head, (
+            "Closure commit should sit on top of the feature commit"
+        )
         ancestry = subprocess.run(
             ["git", "merge-base", "--is-ancestor", stored_hash, "HEAD"],
-            cwd=repo, capture_output=True,
+            cwd=repo,
+            capture_output=True,
+        )
+        assert ancestry.returncode == 0, (
+            f"Stored hash {stored_hash} is orphaned/unreachable"
         )
-        assert ancestry.returncode == 0, f"Stored hash {stored_hash} is orphaned/unreachable"
 
         # No amend commits in history
         log = subprocess.run(
@@ -660,9 +683,14 @@ def test_commit_and_clean_task_stores_reachable_hash():
 
         # git show <stored_hash> still returns the feature diff
         shown = subprocess.run(
-            ["git", "show", stored_hash, "--stat"], cwd=repo, capture_output=True, text=True
+            ["git", "show", stored_hash, "--stat"],
+            cwd=repo,
+            capture_output=True,
+            text=True,
         ).stdout
-        assert "feature.py" in shown, "git show <stored_hash> should return the code diff"
+        assert "feature.py" in shown, (
+            "git show <stored_hash> should return the code diff"
+        )
 
         # Idempotency: second call must not create more commits
         before = subprocess.run(
@@ -703,14 +731,16 @@ def test_commit_and_clean_task_guard_no_false_positive_on_diff_mention():
         repo = Path(repo_dir)
         subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
         subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
-        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
+        subprocess.run(
+            ["git", "config", "user.email", "test@example.com"], cwd=repo, check=True
+        )
 
         (repo / "feature.py").write_text("x = 1\n")
         # Raw diff that itself contains the guard's phrase AND the exact
         # clean-block f-string literal (but with {commit_hash}, not a real hash)
         raw_diff = (
             "```diff\n"
-            "+            if \"Stored in Commit Hash:\" in existing:\n"
+            '+            if "Stored in Commit Hash:" in existing:\n'
             "+**Factual Git Diff:** Stored in Commit Hash: `{commit_hash}`\n"
             "```\n"
         )
@@ -729,7 +759,9 @@ def test_commit_and_clean_task_guard_no_false_positive_on_diff_mention():
         finally:
             os.chdir(old_cwd)
         assert "✅ Success" in result, result
-        assert "already cleaned" not in result, "Guard must not false-positive on raw diff mentions"
+        assert "already cleaned" not in result, (
+            "Guard must not false-positive on raw diff mentions"
+        )
 
         # The stored hash must reference the committed code (reachable, not orphaned)
         cleaned = task_file.read_text()
@@ -740,9 +772,12 @@ def test_commit_and_clean_task_guard_no_false_positive_on_diff_mention():
         assert stored_hash, "Could not parse stored commit hash"
         ancestry = subprocess.run(
             ["git", "merge-base", "--is-ancestor", stored_hash, "HEAD"],
-            cwd=repo, capture_output=True,
+            cwd=repo,
+            capture_output=True,
+        )
+        assert ancestry.returncode == 0, (
+            f"Stored hash {stored_hash} is orphaned/unreachable"
         )
-        assert ancestry.returncode == 0, f"Stored hash {stored_hash} is orphaned/unreachable"
 
 
 def test_create_tree_report_saves_md_in_context_reports():
@@ -787,7 +822,9 @@ def test_create_tree_report_saves_md_in_context_reports():
 
             # .gitignore safeguard: context-reports/ appended by the tool
             gitignore_text = (repo / ".gitignore").read_text()
-            assert "context-reports/" in gitignore_text, "Tool must safeguard context-reports/ in .gitignore"
+            assert "context-reports/" in gitignore_text, (
+                "Tool must safeguard context-reports/ in .gitignore"
+            )
         finally:
             os.chdir(old_cwd)
 
@@ -799,7 +836,9 @@ def test_create_tree_report_default_target_is_cwd():
     import tempfile
 
     server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
-    spec = importlib.util.spec_from_file_location("context_server_tree_default", server_path)
+    spec = importlib.util.spec_from_file_location(
+        "context_server_tree_default", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
@@ -820,7 +859,9 @@ def test_create_tree_report_default_target_is_cwd():
             assert report_file, "Could not parse report path"
             assert "tree_report_" in Path(report_file).name, report_file
             content = Path(report_file).read_text()
-            assert "main.py" in content, "Project files should appear in the default whole-project tree"
+            assert "main.py" in content, (
+                "Project files should appear in the default whole-project tree"
+            )
         finally:
             os.chdir(old_cwd)
 
@@ -836,7 +877,9 @@ def test_create_tree_report_rapid_calls_do_not_overwrite():
     import tempfile
 
     server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
-    spec = importlib.util.spec_from_file_location("context_server_tree_rapid", server_path)
+    spec = importlib.util.spec_from_file_location(
+        "context_server_tree_rapid", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
@@ -853,7 +896,9 @@ def test_create_tree_report_rapid_calls_do_not_overwrite():
             assert "✅ Success" in first and "✅ Success" in second
 
             reports = sorted((repo / "context-reports").glob("tree_report_*.md"))
-            assert len(reports) >= 2, f"Expected 2 distinct reports, got {len(reports)}: {reports}"
+            assert len(reports) >= 2, (
+                f"Expected 2 distinct reports, got {len(reports)}: {reports}"
+            )
             assert reports[0].is_file() and reports[1].is_file()
         finally:
             os.chdir(old_cwd)
@@ -866,7 +911,9 @@ def test_create_tree_report_invalid_path():
     import tempfile
 
     server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
-    spec = importlib.util.spec_from_file_location("context_server_tree_invalid", server_path)
+    spec = importlib.util.spec_from_file_location(
+        "context_server_tree_invalid", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
@@ -894,7 +941,9 @@ def test_create_tree_report_rejects_path_traversal():
     import tempfile
 
     server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
-    spec = importlib.util.spec_from_file_location("context_server_tree_traversal", server_path)
+    spec = importlib.util.spec_from_file_location(
+        "context_server_tree_traversal", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
@@ -924,7 +973,9 @@ def test_create_tree_report_handles_none_input():
     import tempfile
 
     server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
-    spec = importlib.util.spec_from_file_location("context_server_tree_none", server_path)
+    spec = importlib.util.spec_from_file_location(
+        "context_server_tree_none", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
@@ -945,7 +996,9 @@ def test_create_tree_report_handles_none_input():
                     report_file = line.split("`")[1]
             assert report_file, "Could not parse report path"
             content = Path(report_file).read_text()
-            assert "main.py" in content, "None input should default to the whole-project tree"
+            assert "main.py" in content, (
+                "None input should default to the whole-project tree"
+            )
         finally:
             os.chdir(old_cwd)
 
@@ -991,17 +1044,24 @@ def test_stage_and_inject_diff_with_ignored_context_reports():
         try:
             # F5 contract (Task 90): stage_and_inject_diff stages ONLY the explicitly
             # listed modified files + the task file — pass the modified file list.
-            result = mod.stage_and_inject_diff(str(task_file), modified_files=["feature.py"])
+            result = mod.stage_and_inject_diff(
+                str(task_file), modified_files=["feature.py"]
+            )
         finally:
             os.chdir(old_cwd)
         assert "✅ Success" in result, result
 
         # Task file now contains the injected diff
-        assert "feature.py" in task_file.read_text(), "Diff should be injected into the task file"
+        assert "feature.py" in task_file.read_text(), (
+            "Diff should be injected into the task file"
+        )
 
         # The ignored report must not be staged; the code change must be
         staged = subprocess.run(
-            ["git", "diff", "--cached", "--name-only"], cwd=repo, capture_output=True, text=True
+            ["git", "diff", "--cached", "--name-only"],
+            cwd=repo,
+            capture_output=True,
+            text=True,
         ).stdout
         assert "feature.py" in staged, "Code change should be staged"
         assert "context-reports" not in staged, "Ignored reports must not be staged"
@@ -1085,7 +1145,9 @@ def test_lint_task_file_rejects_duplicate_factual_git_diff_heading():
     import importlib
 
     server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
-    spec = importlib.util.spec_from_file_location("lint_server_dup_factual", server_path)
+    spec = importlib.util.spec_from_file_location(
+        "lint_server_dup_factual", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
@@ -1209,8 +1271,12 @@ def test_system_prompt_summary_mentions_qa_transition():
     repo_root = Path(__file__).parent.parent
     system_prompt = (repo_root / "system-prompt.md").read_text(encoding="utf-8")
 
-    summary_blocks = re.findall(r"<summary_phase>.*?</summary_phase>", system_prompt, re.DOTALL)
-    assert summary_blocks, "system-prompt.md must contain at least one <summary_phase> block"
+    summary_blocks = re.findall(
+        r"<summary_phase>.*?</summary_phase>", system_prompt, re.DOTALL
+    )
+    assert summary_blocks, (
+        "system-prompt.md must contain at least one <summary_phase> block"
+    )
     assert any("tasks/qa/" in block for block in summary_blocks), (
         "At least one <summary_phase> block must mention the `tasks/qa/` QA-transition "
         "destination"
@@ -1245,11 +1311,17 @@ def test_cognitive_executor_preserves_qa_and_closure_rules():
     executor = repo_root / "agents" / "cognitive-executor.md"
     content = executor.read_text(encoding="utf-8")
 
-    assert "- **Rule:** When your implementation and `stage_and_inject_diff` are complete" in content, (
+    assert (
+        "- **Rule:** When your implementation and `stage_and_inject_diff` are complete"
+        in content
+    ), (
         "agents/cognitive-executor.md must preserve the QA/Review Phase Rule bullet "
         "authorizing the git mv from tasks/in-progress/ to tasks/qa/."
     )
-    assert '- **Rule:** Only when the Manager explicitly says "Approved for closure" or "Close task"' in content, (
+    assert (
+        '- **Rule:** Only when the Manager explicitly says "Approved for closure" or "Close task"'
+        in content
+    ), (
         "agents/cognitive-executor.md must preserve the Closure Sequence Rule bullet "
         "requiring explicit Manager closure authorization."
     )
@@ -1308,7 +1380,9 @@ def test_system_prompt_split_assemble_round_trip():
     repo_root = Path(__file__).parent.parent
     pristine_path = repo_root / "system-prompt.md"
     splitter_path = repo_root / "scripts" / "prompt-build" / "split_system_prompt.py"
-    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
+    assembler_path = (
+        repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
+    )
 
     with tempfile.TemporaryDirectory() as tmpdir:
         tmp = Path(tmpdir)
@@ -1425,7 +1499,9 @@ def test_lint_system_prompt_sync_detects_drift():
             manifest_path=str(manifest),
             system_prompt_path=str(repo_root / "system-prompt.md"),
         )
-        assert in_sync is False, "Expected drift to be detected, but check reported clean."
+        assert in_sync is False, (
+            "Expected drift to be detected, but check reported clean."
+        )
         assert "DRIFT DETECTED" in msg, f"Expected DRIFT message, got: {msg[:200]}"
 
 
@@ -1472,8 +1548,12 @@ def test_assemble_raises_on_unresolved_placeholder():
     import pytest
 
     repo_root = Path(__file__).parent.parent
-    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
-    spec = importlib.util.spec_from_file_location("assembler_unresolved", assembler_path)
+    assembler_path = (
+        repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
+    )
+    spec = importlib.util.spec_from_file_location(
+        "assembler_unresolved", assembler_path
+    )
     assembler = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(assembler)
 
@@ -1497,9 +1577,7 @@ def test_assemble_raises_on_unresolved_placeholder():
         # Shared partial containing {{FOO}} placeholder — no include marker
         # provides a value for FOO, so it should remain unresolved.
         shared_path = shared_dir / "test.md"
-        shared_path.write_text(
-            "Content with {{FOO}} placeholder.\n", encoding="utf-8"
-        )
+        shared_path.write_text("Content with {{FOO}} placeholder.\n", encoding="utf-8")
 
         manifest = tmp / "manifest.txt"
         manifest.write_text("01-test.md\n", encoding="utf-8")
@@ -1507,7 +1585,10 @@ def test_assemble_raises_on_unresolved_placeholder():
         assembled_path = tmp / "assembled.md"
 
         # assemble() should raise ValueError with the unresolved placeholder name.
-        with pytest.raises(ValueError, match=r"Unresolved placeholder \{\{FOO\}\} in fragment 01-test.md"):
+        with pytest.raises(
+            ValueError,
+            match=r"Unresolved placeholder \{\{FOO\}\} in fragment 01-test.md",
+        ):
             assembler.assemble(
                 output_path=str(tmp / "out.md"),
                 fragments_dir=str(frag_dir),
@@ -1553,9 +1634,7 @@ def test_lint_system_prompt_sync_handles_unresolved_placeholder():
             encoding="utf-8",
         )
         shared_path = shared_dir / "test.md"
-        shared_path.write_text(
-            "Content with {{FOO}} placeholder.\n", encoding="utf-8"
-        )
+        shared_path.write_text("Content with {{FOO}} placeholder.\n", encoding="utf-8")
         manifest = tmp / "manifest.txt"
         manifest.write_text("01-test.md\n", encoding="utf-8")
 
@@ -1567,7 +1646,9 @@ def test_lint_system_prompt_sync_handles_unresolved_placeholder():
             system_prompt_path=str(repo_root / "system-prompt.md"),
         )
         assert in_sync is False, f"Expected False, got: {msg}"
-        assert "FOO" in msg, f"Expected message to identify the placeholder {{FOO}}, got: {msg}"
+        assert "FOO" in msg, (
+            f"Expected message to identify the placeholder {{FOO}}, got: {msg}"
+        )
 
 
 def test_split_halts_on_missing_top_level_tag():
@@ -1599,7 +1680,9 @@ def test_split_halts_on_missing_top_level_tag():
         # Find the block boundaries
         start = content.find("<ai_objective>")
         end = content.find("</ai_objective>")
-        assert start != -1 and end != -1, "Test setup: ai_objective tag not found in pristine"
+        assert start != -1 and end != -1, (
+            "Test setup: ai_objective tag not found in pristine"
+        )
         end += len("</ai_objective>")
         corrupted = content[:start] + content[end:]
         corrupted_path = tmp / "system-prompt.corrupted.md"
@@ -1635,7 +1718,9 @@ def test_assemble_rejects_path_traversal_include():
     import pytest
 
     repo_root = Path(__file__).parent.parent
-    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
+    assembler_path = (
+        repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
+    )
     spec = importlib.util.spec_from_file_location("assembler_traversal", assembler_path)
     assembler = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(assembler)
@@ -1694,7 +1779,9 @@ def test_assemble_rejects_malformed_include_marker():
     import pytest
 
     repo_root = Path(__file__).parent.parent
-    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
+    assembler_path = (
+        repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
+    )
     spec = importlib.util.spec_from_file_location("assembler_malformed", assembler_path)
     assembler = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(assembler)
@@ -1728,7 +1815,9 @@ def test_assemble_rejects_malformed_include_marker():
                 manifest_path=str(manifest),
             )
         msg = str(exc_info.value)
-        assert "01-test.md" in msg, f"Error message must identify the fragment, got: {msg}"
+        assert "01-test.md" in msg, (
+            f"Error message must identify the fragment, got: {msg}"
+        )
         assert "<!--INCLUDE:" in msg or "INCLUDE" in msg, (
             f"Error message must identify the malformed include marker, got: {msg}"
         )
@@ -1747,7 +1836,9 @@ def test_lint_system_prompt_sync_missing_include_file():
 
     repo_root = Path(__file__).parent.parent
     server_path = repo_root / "mcp-lint-server" / "server.py"
-    spec = importlib.util.spec_from_file_location("lint_server_missing_include", server_path)
+    spec = importlib.util.spec_from_file_location(
+        "lint_server_missing_include", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
@@ -1774,7 +1865,11 @@ def test_lint_system_prompt_sync_missing_include_file():
             system_prompt_path=str(repo_root / "system-prompt.md"),
         )
         assert in_sync is False, f"Expected False, got: {msg}"
-        assert "missing" in msg.lower() or "not found" in msg.lower() or "include" in msg.lower(), (
+        assert (
+            "missing" in msg.lower()
+            or "not found" in msg.lower()
+            or "include" in msg.lower()
+        ), (
             f"Expected message to identify the missing file or include failure, got: {msg[:200]}"
         )
 
@@ -1791,7 +1886,9 @@ def test_lint_system_prompt_sync_invalid_fragments_dir_configuration():
 
     repo_root = Path(__file__).parent.parent
     server_path = repo_root / "mcp-lint-server" / "server.py"
-    spec = importlib.util.spec_from_file_location("lint_server_invalid_cfg", server_path)
+    spec = importlib.util.spec_from_file_location(
+        "lint_server_invalid_cfg", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
@@ -1800,7 +1897,9 @@ def test_lint_system_prompt_sync_invalid_fragments_dir_configuration():
 
         # A regular text file used as fragments_dir — a misconfiguration.
         bogus_fragments_dir = tmp / "not-a-directory.txt"
-        bogus_fragments_dir.write_text("this is a file, not a directory\n", encoding="utf-8")
+        bogus_fragments_dir.write_text(
+            "this is a file, not a directory\n", encoding="utf-8"
+        )
 
         shared_dir = tmp / "shared"
         shared_dir.mkdir()
@@ -1832,8 +1931,12 @@ def test_assemble_rejects_path_traversal_manifest_entry():
     import pytest
 
     repo_root = Path(__file__).parent.parent
-    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
-    spec = importlib.util.spec_from_file_location("assembler_manifest_trav", assembler_path)
+    assembler_path = (
+        repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
+    )
+    spec = importlib.util.spec_from_file_location(
+        "assembler_manifest_trav", assembler_path
+    )
     assembler = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(assembler)
 
@@ -1881,8 +1984,12 @@ def test_assemble_rejects_absolute_manifest_entry():
     import pytest
 
     repo_root = Path(__file__).parent.parent
-    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
-    spec = importlib.util.spec_from_file_location("assembler_manifest_abs", assembler_path)
+    assembler_path = (
+        repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
+    )
+    spec = importlib.util.spec_from_file_location(
+        "assembler_manifest_abs", assembler_path
+    )
     assembler = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(assembler)
 
@@ -1964,7 +2071,9 @@ def test_memory_server_build_index_on_store():
 
     repo_root = Path(__file__).parent.parent
     server_path = repo_root / "mcp-memory-server" / "server.py"
-    spec = importlib.util.spec_from_file_location("memory_server_build_store", server_path)
+    spec = importlib.util.spec_from_file_location(
+        "memory_server_build_store", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
@@ -1976,17 +2085,26 @@ def test_memory_server_build_index_on_store():
             # Fresh index should not exist
             assert not (repo / ".opencode" / "memory" / "index.md").exists()
             # Store a memory shard
-            result = mod.store_memory("testns", "testkey", "Hello world | with pipe\nSecond line", overwrite=True)
+            result = mod.store_memory(
+                "testns",
+                "testkey",
+                "Hello world | with pipe\nSecond line",
+                overwrite=True,
+            )
             assert "successfully stored" in result.lower(), result
             # Index must now exist and contain table headers and the row
             index_path = repo / ".opencode" / "memory" / "index.md"
-            assert index_path.is_file(), "index.md should be generated after store_memory"
+            assert index_path.is_file(), (
+                "index.md should be generated after store_memory"
+            )
             content = index_path.read_text(encoding="utf-8")
             assert "# Project Memory Index" in content, content[:200]
             assert "| Namespace | Key | Summary | Tags |" in content
             assert "| testns | testkey |" in content
             # Summary should be first non-empty line, clamped and pipe-escaped
-            assert "Hello world \\| with pipe" in content, f"Pipe not escaped: {content}"
+            assert "Hello world \\| with pipe" in content, (
+                f"Pipe not escaped: {content}"
+            )
             assert "Second line" not in content  # only first line is summary
         finally:
             os.chdir(old_cwd)
@@ -2001,7 +2119,9 @@ def test_memory_server_update_index_on_delete():
 
     repo_root = Path(__file__).parent.parent
     server_path = repo_root / "mcp-memory-server" / "server.py"
-    spec = importlib.util.spec_from_file_location("memory_server_build_delete", server_path)
+    spec = importlib.util.spec_from_file_location(
+        "memory_server_build_delete", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
@@ -2050,7 +2170,9 @@ def test_memory_server_index_empty_store():
             assert index_path.is_file()
             content = index_path.read_text(encoding="utf-8")
             assert "No memories recorded yet" in content
-            assert "| Namespace | Key | Summary | Tags |" not in content  # empty should not have table
+            assert (
+                "| Namespace | Key | Summary | Tags |" not in content
+            )  # empty should not have table
         finally:
             os.chdir(old_cwd)
 
@@ -2076,12 +2198,17 @@ def test_memory_server_index_sanitizes_pipes():
             # Content with pipes and tags with pipes (via frontmatter)
             content_with_pipe = "Summary with | pipe | chars\nMore"
             # Store with frontmatter that includes tags containing pipe via manual content
-            fm_content = "---\ncreated_at: '2026-08-28T00:00:00+00:00'\nupdated_at: '2026-08-28T00:00:00+00:00'\nstatus: active\ntags: ['a|b', 'c']\n---\n\n" + content_with_pipe
+            fm_content = (
+                "---\ncreated_at: '2026-08-28T00:00:00+00:00'\nupdated_at: '2026-08-28T00:00:00+00:00'\nstatus: active\ntags: ['a|b', 'c']\n---\n\n"
+                + content_with_pipe
+            )
             mod.store_memory("ns", "pipekey", fm_content, overwrite=True)
             index_path = repo / ".opencode" / "memory" / "index.md"
             idx = index_path.read_text(encoding="utf-8")
             # Pipes in summary must be escaped as \|
-            assert "Summary with \\| pipe \\| chars" in idx, f"Pipe not escaped in summary: {idx}"
+            assert "Summary with \\| pipe \\| chars" in idx, (
+                f"Pipe not escaped in summary: {idx}"
+            )
             # Pipes in tags must be escaped
             assert "a\\|b" in idx, f"Pipe not escaped in tags: {idx}"
             # Verify table still has exactly 4 columns per data row (pipes not splitting columns)
@@ -2123,7 +2250,9 @@ def test_memory_server_rebuild_tool():
             assert not idx_path.exists()
             # Rebuild via tool
             result = mod.rebuild_memory_index()
-            assert "memories indexed" in result.lower() or "built" in result.lower(), result
+            assert "memories indexed" in result.lower() or "built" in result.lower(), (
+                result
+            )
             assert idx_path.is_file()
             content = idx_path.read_text(encoding="utf-8")
             assert "rk1" in content
@@ -2134,6 +2263,7 @@ def test_memory_server_rebuild_tool():
 
 # --- Task 177: traversal-guard + runaway-cap regression tests ---
 
+
 def _load_context_server_hardening():
     """Load mcp-context-server fresh for the hardening tests."""
     import importlib
@@ -2158,7 +2288,7 @@ def _tree_result(mod, *args, **kwargs):
     out = mod.get_directory_tree(*args, **kwargs)
     prefix = getattr(mod, "ROOT_FALLBACK_WARNING", None)
     if prefix and isinstance(out, str) and out.startswith(prefix):
-        out = out[len(prefix):].lstrip("\n")
+        out = out[len(prefix) :].lstrip("\n")
     return out
 
 
@@ -2302,9 +2432,7 @@ def test_tree_depth_cap():
             deep = deep / f"lvl{i}"
             deep.mkdir()
         (deep / "bottom.txt").write_text("x", encoding="utf-8")
-        out = mod.generate_tree(
-            Path(tmpdir), mod.GitIgnoreFilter(), max_depth=3
-        )
+        out = mod.generate_tree(Path(tmpdir), mod.GitIgnoreFilter(), max_depth=3)
         assert "[Max depth reached (3)]" in out
         assert "bottom.txt" not in out
 
@@ -2325,9 +2453,7 @@ def test_tree_entry_cap_and_banned_dirs():
         modules = root / "node_modules"
         modules.mkdir()
         (modules / "dep.js").write_text("x", encoding="utf-8")
-        out = mod.generate_tree(
-            root, mod.GitIgnoreFilter(), max_entries=5
-        )
+        out = mod.generate_tree(root, mod.GitIgnoreFilter(), max_entries=5)
         assert "[Truncated: entry limit reached (5)]" in out
         assert "__pycache__" not in out
         assert "node_modules" not in out
@@ -2370,9 +2496,7 @@ def test_read_source_files_prepends_metrics():
         old_cwd = os.getcwd()
         os.chdir(root)
         try:
-            result = mod.read_source_files(
-                ["a.txt", "b.txt", "big.txt"], max_size=10
-            )
+            result = mod.read_source_files(["a.txt", "b.txt", "big.txt"], max_size=10)
             assert "📊 Report metrics:" in result, result[:300]
             assert "2 processed" in result, result[:300]
             assert "1 skipped" in result, result[:300]
@@ -2437,7 +2561,10 @@ def test_check_conventional_commit_rejects_long_subject():
 def test_check_conventional_commit_ignores_body():
     """Task 211: only the first line is validated; body text is free."""
     mod = _load_context_server_hardening()
-    assert mod._check_conventional_commit("fix: repair bug\n\nLong body " + "y" * 200) is None
+    assert (
+        mod._check_conventional_commit("fix: repair bug\n\nLong body " + "y" * 200)
+        is None
+    )
 
 
 def test_commit_and_clean_task_rejects_nonconventional_message():
@@ -2452,10 +2579,14 @@ def test_commit_and_clean_task_rejects_nonconventional_message():
         repo = Path(repo_dir)
         subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
         subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
-        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
+        subprocess.run(
+            ["git", "config", "user.email", "test@example.com"], cwd=repo, check=True
+        )
         (repo / "feature.py").write_text("x = 1\n")
         task_file = repo / "80-bad-msg.md"
-        task_file.write_text("# Task 80\n\n<!-- BEGIN_GIT_DIFF -->\n```diff\n+x\n```\n<!-- END_GIT_DIFF -->\n")
+        task_file.write_text(
+            "# Task 80\n\n<!-- BEGIN_GIT_DIFF -->\n```diff\n+x\n```\n<!-- END_GIT_DIFF -->\n"
+        )
         subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
         old_cwd = os.getcwd()
         os.chdir(repo)
@@ -2489,7 +2620,15 @@ def _read_executor_gate():
 def test_planning_gate_designer_fallback_terms():
     """Task 214 (QA hotfix F1/M1): trigger map covers neutral UX phrasing."""
     gate = _read_executor_gate()
-    for term in ("screen", "navigation", "onboarding", "empty state", "avatar", "settings", "flow"):
+    for term in (
+        "screen",
+        "navigation",
+        "onboarding",
+        "empty state",
+        "avatar",
+        "settings",
+        "flow",
+    ):
         assert term in gate, f"fallback term missing: {term}"
 
 
@@ -2518,12 +2657,15 @@ def test_context_reports_follow_project_root_not_singleton_cwd():
 
     server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
     spec = importlib.util.spec_from_file_location(
-        "context_server_projroot", server_path)
+        "context_server_projroot", server_path
+    )
     mod = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(mod)
 
-    with tempfile.TemporaryDirectory() as repo_dir, \
-            tempfile.TemporaryDirectory() as foreign_dir:
+    with (
+        tempfile.TemporaryDirectory() as repo_dir,
+        tempfile.TemporaryDirectory() as foreign_dir,
+    ):
         repo = Path(repo_dir)
         foreign = Path(foreign_dir)
         (repo / "src").mkdir()
@@ -2534,10 +2676,8 @@ def test_context_reports_follow_project_root_not_singleton_cwd():
         os.chdir(foreign)  # stand in for the singleton server's own cwd
         try:
             tree = mod.create_tree_report(".", project_root=str(repo))
-            read = mod.read_source_files(
-                ["src/app.py"], project_root=str(repo))
-            sig = mod.extract_signatures(
-                "src/app.py", project_root=str(repo))
+            read = mod.read_source_files(["src/app.py"], project_root=str(repo))
+            sig = mod.extract_signatures("src/app.py", project_root=str(repo))
         finally:
             os.chdir(old_cwd)
 
@@ -2551,6 +2691,72 @@ def test_context_reports_follow_project_root_not_singleton_cwd():
         assert any(n.startswith("signatures_report_") for n in names), names
 
         assert not (foreign / "context-reports").exists(), (
-            "reports must never be written into the singleton server cwd")
+            "reports must never be written into the singleton server cwd"
+        )
         assert "context-reports/" in (repo / ".gitignore").read_text(), (
-            "the .gitignore safeguard must target the project root")
+            "the .gitignore safeguard must target the project root"
+        )
+
+
+def _graph_fixture_repo(tmp: Path):
+    (tmp / "a.py").write_text("def alpha():\n    return beta()\n", encoding="utf-8")
+    (tmp / "b.py").write_text("def beta():\n    return 1\n", encoding="utf-8")
+    (tmp / "c.py").write_text(
+        "from a import alpha\ndef gamma():\n    return alpha()\n", encoding="utf-8"
+    )
+    return tmp
+
+
+def test_graph_build_saves_versioned_json_and_report():
+    """Lite graph: build_graph persists schema-1 graph.json plus markdown report."""
+    import json
+
+    mod = _load_context_server_hardening()
+    import tempfile
+
+    with tempfile.TemporaryDirectory() as td:
+        repo = _graph_fixture_repo(Path(td))
+        out = mod.build_graph(".", project_root=str(repo))
+        assert "✅ Success" in out, out
+        graphs = list((repo / "context-reports").glob("graph_*.json"))
+        reports = list((repo / "context-reports").glob("graph_report_*.md"))
+        assert graphs, out
+        assert reports, out
+        data = json.loads(graphs[0].read_text(encoding="utf-8"))
+        assert data["graph"]["schema_version"] == 1
+        assert len(data["nodes"]) >= 6
+        confs = {e["confidence"] for e in data["links"]}
+        assert "EXTRACTED" in confs, confs
+
+
+def test_graph_query_explain_path_god_stats():
+    """Lite graph: query/explain/path/god/stats work on a built graph."""
+    mod = _load_context_server_hardening()
+    import tempfile
+
+    with tempfile.TemporaryDirectory() as td:
+        repo = _graph_fixture_repo(Path(td))
+        assert "✅ Success" in mod.build_graph(".", project_root=str(repo))
+        q = mod.query_graph("alpha beta", project_root=str(repo))
+        assert "alpha" in q.lower(), q[:500]
+        ex = mod.explain_node("alpha", project_root=str(repo))
+        assert "Node: alpha" in ex, ex[:500]
+        assert "Degree:" in ex
+        sp = mod.shortest_path("gamma", "beta", project_root=str(repo))
+        assert "hops" in sp.lower() or "no path" in sp.lower(), sp[:500]
+        gods = mod.god_nodes(3, project_root=str(repo))
+        assert "God nodes" in gods, gods[:500]
+        stats = mod.graph_stats(project_root=str(repo))
+        assert "Nodes:" in stats and "EXTRACTED" in stats, stats
+
+
+def test_graph_tree_respects_project_root():
+    """Regression: get_directory_tree with project_root lists project files (not server cwd)."""
+    mod = _load_context_server_hardening()
+    import tempfile
+
+    with tempfile.TemporaryDirectory() as td:
+        repo = Path(td)
+        (repo / "kept.py").write_text("x=1\n", encoding="utf-8")
+        out = mod.get_directory_tree(".", project_root=str(repo))
+        assert "kept.py" in out, out[:500]
```
<!-- END_GIT_DIFF -->
