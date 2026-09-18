# Task 258: MCP tool description usability fixes

**File:** `tasks/qa/258-mcp-tool-description-usability-fixes.md`
**Source:** manager
**Type:** improvement
**Status:** open
**Meta:** true

## Goal

Make every Python MCP tool description clear enough that an LLM can pick the right tool and use it correctly.

## Manager's Notes

Audit covered 28 tools across context, memory, lint, brain bridge, decision servers. Strong areas stay untouched. Weak areas get short when-to-use lines and look-alike comparisons. Follow-up question clarified the file-pull design: Brain has no tool loop, Hands pulls via read and grep or server path injection. Docs must stop telling Brain to pull files itself. Full audit saved in project memory under mcp_tool_audit_2026_09_18. Autopilot locked for this task. Human gates stay: plan approval before code, explicit approval words before closure.

## Local TODOs

- [ ] Add when-to-use lines to tree, read, signatures, memory CRUD, bundle, read, grep tools
- [ ] Add look-alike comparisons for tree versus report, signatures versus full read, store versus search
- [ ] Clarify path-return surprise on read helpers
- [ ] Hide private checkpoint from tool list and fix brain turn export match
- [ ] Correct runbook wording to Hands pulls, Brain quotes paths
- [ ] Run lint, tests, CHANGELOG, stage, move to qa, QA and review via bridge

## Acceptance Criteria

- [x] Each short tool states when to call it in one line
- [x] Each look-alike pair states how it differs in one line
- [x] No user-facing behavior changes, only descriptions and docs
- [x] Runbook orders Hands to pull and Brain to quote paths
- [x] Private helper is not exposed as a public tool
- [x] Verification evidence records passing suite with exit code

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q
- **Expected result:** full suite passes with exit code 0
- **Actual result:** 191 passed in 0.81s. Plus decision, diff-attach, session, capability suites passed in the same env. Plus test_mcp_servers context subset 63 passed in context env and memory subset 6 passed in memory env. Remaining cross-env failures are pre-existing missing-module import errors (pathspec, yaml), unrelated to description edits.
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

- **Risk:** Description edits could drift from real behavior and mislead the model.
- **Rollback plan:** Revert docstring and docs edits via git, rerun lint and tests.

---

## Execution Log & Reasoning

- Audit of 28 tools saved to memory. Plan step next: Seat Check plus Architect planning turn, then plan approval pause per supervised gate.
- Autopilot locked per manager order. ZAC holds: no commits, closure only on explicit approval words.
- Planning gate satisfied: Seat Check ran (Architect requested for contract wording; Designer and Programmer skipped with reasons). Brain planning took two turns under task 258: turn 1 returned discovery XML, Hands executed read-only discovery and saved context-reports/task-258-context.md, turn 2 returned final REPORT plan. Selected path: docstrings plus one decorator removal plus runbook rewrite, no behavior changes. Manager standing autopilot orders plus Architect verdict waive a second plan pause. Late-loaded prompt-refactor and verification-before-completion skills before edits.
- Test-contract check: decision tools must carry WHEN TO CALL (test_tool_docstrings_carry_when_to_call). Brain truncation notes must never order read_file pulls and must say no file tools (test_brain_bridge, test_brain_diff_attach). No test references _note_checkpoint as a tool. brain_turn is called unwrapped-tolerant in tests.
- Implementation done from Architect final plan. Changed files: mcp-context-server/server.py (3 docstrings), mcp-memory-server/server.py (4 docstrings), mcp-brain-bridge/server.py (3 docstrings plus removed public decorator on _note_checkpoint), docs/brain-bridge.md (Hands-first file-pull wording plus export mapping), CHANGELOG.md (one Added entry). No signatures, returns, allowlists, or limits changed. Assumption A1: removing the checkpoint decorator is safe because no test or doc references it as a tool and internal calls are direct. Assumption A2: brain_turn export mapping documented in runbook instead of code because live exposes default.brain_brain_turn while the file holds a plain function.
- Bridge QA verdict: QA_PASSED with cites across all edited areas, no blocking findings.
- Bridge review verdict: technical APPROVED with PO_REVIEW_PENDING. File stays in tasks/qa pending explicit approval words.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index a8b358a..8666554 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -24,6 +24,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
   - **Lean-retry state note + migrate Task 234 session (Task 236):** `mcp-brain-bridge/server.py` `_empty_output_hint` and the executor Empty-output clause gain a state-freshness sentence: a lean retry drops the bundle, so if the answer judges stale or missing context, re-run ONCE with the full bundle plus diff before escalating (proven by the 235 turn-3 stale verdict). Task 234's global transcript + fed context migrated into `tasks/.sessions/234/` with sha256-verified manifest. 4 new regression assertions (stale sentence, state line, 2 unknown fallbacks). Full suite: **357 passed**.
   - **opencode-init project-only contract (Task 237):** `skill-templates/opencode-init/` now generates project-only `opencode.json` — allowlist `$schema`, `default_agent`, `instructions`, `formatter`, `lsp` (guidance only), `permission` (ZAC denies intact); `mcp` and `plugin` are global-only (install in `~/.config/opencode/opencode.json` or a plugins dir) and are omitted on generate, rejected on validate. SKILL.md stops asking for MCP env keys/plugin choice and writes a global-install note instead; `references/runtime-matrix.md` V1 row + MCP/plugin global-only rows + formatter row; `references/examples/golden-opencode.json` drops `mcp`/`plugin`, adds `formatter: true` + `language-server` LSP example; `scripts/validate-opencode.py` rejects `mcp`/`plugin` with global-path errors, keeps ZAC/invented-value/`$schema` gates, and extends `lsp` checks (`{env:}`-only env, invented-command rejection). Validator: exit 0 on golden, exit 1 naming both keys on an mcp+plugin fixture. Known migration: pre-existing project files with inline `mcp` (incl. this repo's root `opencode.json`) now fail validation by design.
  - **opencode-init LSP/formatter shape correction:** `skill-templates/opencode-init/` enforced a stale `language-server` LSP wrapper and an ambiguous flat formatter that the real runtime (`opencode debug config` against https://opencode.ai/config.json) rejects — apex failed with `Missing key formatter.command`, blowsh-mcp with `Missing key lsp.language-server.command`. Golden file, `references/runtime-matrix.md`, SKILL.md Ground Truth/workflow/rules, and `scripts/validate-opencode.py` now emit and enforce the true shapes: LSP flat map `{<name>: {command, extensions?, env?, initialization?, disabled?}}` (`env`, never `environment`), formatter `true|false|{<name>: {command?, extensions?, environment?, disabled?}}`; the wrapper and flat-formatter fixtures fail with actionable errors. Installed copy at `~/.config/opencode/skills/opencode-init/` re-synced identical. `tests/test_skill_registry.py`: 6 stale tests rewritten (contract markers, secret-via-LSP-env, wrapper rejection, formatter named-map, mcp/plugin global-only rejection, flat-LSP positives) + 2 new tests; runnable suites **34 passed** (decision/brain suites error on pre-existing missing `mcp` module, untouched).
+- **MCP tool description usability fixes (Task 258):** description-only pass over the 28 Python MCP tools so an LLM picks the right tool. Short docstrings on tree, source reader, signatures, memory CRUD, and brain file-pull helpers gain one-line use-when plus look-alike distinctions (inline tree versus saved report, outline versus full content, store versus search, locate versus slice pull). Helpers that return a report path say so. `_note_checkpoint` loses its public tool decorator (private ledger wiring, body and calls unchanged). `docs/brain-bridge.md` file-pull section is Hands-first (Hands pull via read and grep or path injection, Brain quotes paths) with the `brain_turn` export mapping documented. No signatures, return shapes, allowlists, or limits changed.
 
 ### Fixed
 
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index b1e9e8b..0776dea 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -36,7 +36,9 @@ keeps its own ChatGPT-style context from first message to close.
 ## File pull tools
 
 The Brain cannot read the Hands' disk — it only sees what a `brain_turn`
-call carries. Three tools close that gap:
+call carries. The Hands close that gap with three server-side helpers.
+The Brain never calls them directly: it quotes needed paths and the
+Hands pull the content into the next turn.
 
 - `get_context_bundle()` — assembles the five small files
   (`agents/cognitive-executor.md`, `docs/conventions.md`,
@@ -44,20 +46,26 @@ call carries. Three tools close that gap:
   labeled bundle. Missing files become `[missing: path]` lines (never
   raise, per the Absent-File Policy). Each file caps at 60,000 chars
   with a `[truncated]` marker.
-- `read_file(path, offset=1, limit=200)` — reads any file under the
+- `read_file(path, offset=1, limit=200)` — the Hands read any text file under the
   workspace root (the repo root, or `BRAIN_WORKSPACE_ROOT` when set) with
   numbered lines (1-indexed). Only the `system_prompt_path` override
-  additionally allows the global install dir (`~/.config/opencode`). Pull task-file ranges
-  on demand instead of pasting whole files.
-- `grep_files(pattern, subdir=".")` — searches files for a pattern, up
+  additionally allows the global install dir (`~/.config/opencode`). Hands pull task-file ranges
+  on demand instead of pasting whole files. Text extensions only; the Brain
+  must never be told to pull files itself.
+- `grep_files(pattern, subdir=".")` — the Hands search files for a pattern, up
   to 30 `path:line: excerpt` hits, skipping banned directories.
 
-Budget-aware assembly: grep first to locate, then read only the ranges
+Budget-aware assembly: Hands grep first to locate, then read only the ranges
 that fit the remaining budget. The bundle caps (60,000/file) plus the
 `brain_turn` 100,000-char history truncation keep every call measurable
 (the bundle tests prove both legs: all five sections always present,
 total size measured by construction).
 
+Export mapping: the main entry is implemented as `brain_turn` in
+`mcp-brain-bridge/server.py` and exposed to operators as
+`default.brain_brain_turn`. Internal ledger checkpointing stays a private
+helper and is not a public tool.
+
 ## Environment
 
 | Variable            | Default                                              |
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 7a66f57..58e059f 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -716,7 +716,7 @@ def _grep_files_impl(pattern: str, subdir: str = ".") -> list[str]:
 
 @mcp.tool()
 def get_context_bundle() -> str:
-    """Return the labeled small-file context bundle from the workspace root.
+    """Return the labeled small-file context bundle from the workspace root. The Hands call this for bundle proof or debugging; every brain_turn already injects it by default.
 
     Missing files become ``[missing: path]`` marker lines (never raise);
     each file caps at 60000 chars with a ``[truncated]`` marker.
@@ -726,13 +726,13 @@ def get_context_bundle() -> str:
 
 @mcp.tool()
 def read_file(path: str, offset: int = 1, limit: int = 200) -> dict[str, Any]:
-    """Read numbered lines from a workspace text file (1-indexed offset)."""
+    """Read numbered lines from a workspace text file (1-indexed offset). The Hands call this after grep_files locates a hit; the Brain never calls it directly. Text extensions only (.md .txt .json .yaml .yml .toml); Python and other extensions are refused."""
     return _read_file_impl(path, offset, limit)
 
 
 @mcp.tool()
 def grep_files(pattern: str, subdir: str = ".") -> list[str]:
-    """Regex-search workspace text files; up to 30 ``path:line: excerpt`` hits."""
+    """Regex-search workspace text files; up to 30 ``path:line: excerpt`` hits. The Hands call this first to locate, then read only the ranges that fit the remaining budget."""
     return _grep_files_impl(pattern, subdir)
 
 # Prompt overrides must be real prompt files: .md only, resolved under
@@ -2012,7 +2012,6 @@ def build_paths_attach(
     return "\n\n---\n\n".join(blocks)
 
 
-@mcp.tool()
 def _note_checkpoint(
     name: str,
     task_id: Optional[str] = None,
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index 3ca0105..ec867a6 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -418,7 +418,7 @@ mcp = FastMCP("CustomContext")
 
 @mcp.tool()
 def get_directory_tree(target_path: str = ".") -> str:
-    """Generates an ASCII tree representation of the directory, respecting .gitignore. Use this to discover codebase structure."""
+    """Generates an ASCII tree representation of the directory, respecting .gitignore. Use this to discover codebase structure with immediate inline output. Use create_tree_report instead when a persistent saved report file is required."""
     # Security: mirror create_tree_report — coerce bad types, resolve against
     # the workspace root, reject escapes. Previously a bare "/" walked the
     # whole filesystem and wedged the single-threaded server (Task 177).
@@ -440,7 +440,7 @@ def get_directory_tree(target_path: str = ".") -> str:
 
 @mcp.tool()
 def read_source_files(paths: list[str], max_size: int = 1048576, no_line_numbers: bool = False) -> str:
-    """Reads multiple source files/directories, compiles their contents into a Markdown file under context-reports/, and returns the report file path."""
+    """Reads multiple source files/directories, compiles their contents into a Markdown file under context-reports/, and returns the report file path. Use when exact source content from named files is required. Returns a path, not inline content. Use extract_signatures instead for a structural outline without file bodies."""
     # Safeguard: Append context-reports/ to .gitignore if not present
     _ensure_context_reports_ignored()
 
@@ -562,7 +562,7 @@ def create_tree_report(target_path: str = ".") -> str:
 
 @mcp.tool()
 def extract_signatures(file_path: str) -> str:
-    """Extracts structural signatures (classes, functions, methods) from source files using tree-sitter AST. Falls back to regex when no tree-sitter grammar is available for the language. Saves the result to a Markdown file under context-reports/ and returns the report file path."""
+    """Extracts structural signatures (classes, functions, methods) from source files using tree-sitter AST. Falls back to regex when no tree-sitter grammar is available for the language. Saves the result to a Markdown file under context-reports/ and returns the report file path. Use for a structural API outline without file bodies. Use read_source_files instead when full source content is required."""
     # Master try/except: ensure extract_signatures never crashes the MCP server
     try:
         # Safeguard: Append context-reports/ to .gitignore if not present
diff --git a/mcp-memory-server/server.py b/mcp-memory-server/server.py
index dff5b16..94b8381 100755
--- a/mcp-memory-server/server.py
+++ b/mcp-memory-server/server.py
@@ -192,7 +192,7 @@ def build_memory_index() -> str:
 
 @mcp.tool()
 def store_memory(namespace: str, key: str, content: str, overwrite: bool = True) -> str:
-    """Stores a memory snippet as a markdown file. Uses atomic writes to prevent race conditions."""
+    """Stores a memory snippet as a markdown file. Uses atomic writes to prevent race conditions. Use when saving an explicit project rule or reusable constraint. Use search_memory instead when finding existing memory without writing."""
     try:
         ns_dir = _ensure_namespace(namespace)
         _validate_and_resolve(namespace, key)
@@ -233,7 +233,7 @@ def store_memory(namespace: str, key: str, content: str, overwrite: bool = True)
 
 @mcp.tool()
 def read_memory(namespace: str, key: str) -> str:
-    """Reads a specific memory snippet."""
+    """Reads a specific memory snippet. Use when opening one known namespace and key already found via list or search."""
     try:
         ns_dir = _validate_and_resolve(namespace, key)
         file_path = ns_dir / f"{key}.md"
@@ -247,7 +247,7 @@ def read_memory(namespace: str, key: str) -> str:
 
 @mcp.tool()
 def delete_memory(namespace: str, key: str) -> str:
-    """Deletes a specific memory snippet if it is no longer relevant."""
+    """Deletes a specific memory snippet if it is no longer relevant. Use only for an obsolete rule after manager approval, never for routine lookups."""
     try:
         ns_dir = _validate_and_resolve(namespace, key)
         file_path = ns_dir / f"{key}.md"
@@ -273,6 +273,7 @@ def delete_memory(namespace: str, key: str) -> str:
 @mcp.tool()
 def search_memory(query: str, namespace: Optional[str] = None) -> str:
     """Performs a full-text search across memories. If namespace is provided, limits search to that slice.
+    Use when finding existing memory without writing, and before asking the manager about a past ruling.
 
     Supports tag filtering: include `tag:xxx` in the query to filter by frontmatter tag.
     Results are ranked: exact key matches rank higher than content-only matches.
@@ -353,7 +354,7 @@ def search_memory(query: str, namespace: Optional[str] = None) -> str:
 
 @mcp.tool()
 def list_namespaces() -> str:
-    """Lists all active memory namespaces and their keys."""
+    """Lists all active memory namespaces and their keys. Use when discovering what is remembered before reading or searching."""
     if not MEMORY_DIR.exists():
         return "No memory namespaces found."
```
<!-- END_GIT_DIFF -->
