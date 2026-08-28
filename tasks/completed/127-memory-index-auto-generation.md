# Task 127: Auto-Generate Memory Index via MCP Memory Server and Integrate into Agents

**File:** `tasks/qa/127-memory-index-auto-generation.md`
**Source:** telegram
**Type:** improvement
**Status:** open

## Goal

Implement auto-generated Markdown memory index via MCP memory server and integrate it into cognitive executor and system prompt workflows so agents always read relevant project memory via the index.

## Original Message (Persian)

باید کاری کنم که آدید ایجنت اسکیل ویرایش بشه داخل ایجنتها این بخش اضافه بشه که لطفاً همیشه در مورد یک چیزی مموری رو بخون یا یه کار بهتر میتونیم ام سی پی مموری رو آپدیت کنیم که بخش ایندکس هم به صورت ماک داون بسازه که تو درخواستها اون ایندکس رو به ai بدیم

#improve

توی task من منظورم اینه باید MCPC server رو ریرایش کنیم که خودش بیاد خودکار بعد از هر تغییر داخل فایل task یک index هم بسازه. توی مسیر مشخص index رو بذاره. مثلا میتونه index رو توی داخل همین جایی که الان هست بذاره، نقطه Open Code اسلش Memory اسلش حالا Index. جایی باشه که برای همه پروژهها یکی باشه، خودش مشخص باشه. بعد که این رو مشخص کردیم، میتونیم داخل cognitive agent و داخل system prompt این رو براش تعریف کنیم که این فایل index memory اینجا هست. اگر این taskی که الان داری روش کار میکنی memory نیاز داره تو باید بخونی حتما از طریق SDK project memory رو فراخوانی کن، و بس و پس memory مورد نیاز رو از داخل حافظه توسط این indexی که خوندیش بخون. دقیقا مثل همون جایی که هر بار بهش میگیم فایل agents.md convention data models رو بخونه، از این به بعد خوندن فایل index memory هم باید جزو اجزای پروژه باشه هم برای cognitive executor agents، هم برای system prompt.

## English Translation

I need to edit the agent skill so that a section is added inside the agents asking them to always read memory about something, or we can better update the MCP memory server to also generate an index section in Markdown that we give to the AI in requests.

#improve

In the task I mean we should edit the MCP server so that it automatically builds an index after every change to task files. Put the index in a specific path. For example it could put the index inside the current location, dot OpenCode slash Memory slash Index. Somewhere that is the same for all projects, clearly defined. After we define it, we can define it inside the cognitive agent and inside the system prompt that this memory index file is here. If the task you are currently working on needs memory, you must read it via the SDK project memory call, and then read the required memory from the store via the index you just read. Exactly like where we tell it every time to read the agents.md, convention, data models files, from now on reading the memory index file should also be part of the project components both for the cognitive executor agents and for system prompt.

## Refactored Prompt

<role>
You are a Senior Systems Architect specializing in OpenCode MCP servers, agent orchestration, and persistent project memory. You own the `mcp-memory-server`, `project-memory` skill, `cognitive-executor` agent, and the `system-prompt` fragment assembly pipeline.
</role>

<system_context>
You operate inside the Cognitive Lead AI HQ — a documentation-only headquarters repo with FastMCP servers (`mcp-context-server`, `mcp-memory-server`, `mcp-lint-server`, `mcp-telegram-server`, `blowsh`), Agent Skills in `skill-templates/` and `.opencode/skills/`, custom agents in `agents/cognitive-executor.md`, and a generated `system-prompt.md` assembled from `prompts/fragments/` + `prompts/shared/`. Project memory lives under `.opencode/memory/` via `mcp-memory-server/server.py` with tools `store_memory`, `read_memory`, `search_memory`, `list_namespaces`. All file edits must respect `.gitignore` and pass `lint_task_file` and `lint_system_prompt_sync` where applicable. You have `uv` for Python, `python3 -m py_compile` for validation, and `pytest tests/` for MCP servers.
</system_context>

<agentic_reasoning>
Before writing code, you must output a <reasoning_log> analyzing:
1. Logical dependencies: MCP server is the source of truth for memory persistence; index is a derived view that must stay consistent with the underlying namespace files under `.opencode/memory/`. Agents and system-prompt are consumers that read the index first, then fetch specific memories via SDK.
2. Risk assessment: Auto-generation on every task-file change vs on every memory mutation — which trigger is correct? Task-file changes are not memory writes; the index should update on `store_memory`/`delete_memory` mutations, not on unrelated task edits. If you hook task-file watcher you create circular coupling and miss memory-only updates.
3. Abductive reasoning: Why does memory get ignored? Agents are never told where the index lives nor required to call `search_memory`/`list_namespaces` before planning. The fix is not “always read all memory” but “always read the compact index, then selectively fetch relevant namespaces via SDK.”
4. Precision and grounding: Define the exact index path that is global across projects (e.g., `~/.config/opencode/memory-index.md` or `.opencode/memory/index.md` with global fallback), its Markdown schema (table of namespaces → keys → one-line summary → tags), atomic write semantics (same-directory temp file + `os.replace` + `fsync` as `store_memory` does), and size guardrails (truncate summaries, limit to ~200 lines).
5. Plan-mode safety: The index read must be declared as a mandatory Phase 0 step in both `agents/cognitive-executor.md` and `prompts/fragments/14-hands_protocols.md` validation-phase, alongside `AGENTS.md`/`DESIGN.md` reads, but must not auto-fetch all memories — only the index.
</agentic_reasoning>

<execution_rules>
- You MUST edit `mcp-memory-server/server.py` to add an index generator: implement `build_memory_index()` that scans `.opencode/memory/**/*.md` (excluding `.opencode/goals` and `index.md` itself), parses frontmatter `tags` and first non-empty line as summary, and writes ` .opencode/memory/index.md` (project-local) and optionally mirrors to `~/.config/opencode/memory-index.md` (global) atomically. Hook it into `store_memory` and `delete_memory` success paths (not into task-file watcher). If generation fails, log but do not fail the parent mutation.
- You MUST add/increment tests in `tests/test_mcp_servers.py` for the index: creates index on `store_memory`, updates on delete, valid Markdown, atomic, handles empty store.
- You MUST update `skill-templates/project-memory/SKILL.md` (and sync to `.opencode/skills/project-memory/SKILL.md` + `~/.config/opencode/skills/project-memory/SKILL.md`) to document the index location, when it updates, and the two-step workflow: 1) read index 2) `search_memory`/`read_memory` for relevant keys.
- You MUST update `agents/cognitive-executor.md` under “Context Bootstrapping & Memory Protocol” to mandate reading the index via `read_source_files` or `read_memory` list as the first memory step, parallel to `AGENTS.md`/`DESIGN.md` reads, before planning.
- You MUST update the system-prompt fragment that defines the Hands’ mandatory reads (likely `prompts/fragments/14-hands_protocols.md` validation-phase via `prompts/shared/validation-phase.md`) to include the memory index file as a required Phase 0 read (same level as `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, `docs/conventions.md`), with the two-step fetch pattern.
- You MUST run `python3 scripts/prompt-build/assemble_system_prompt.py` after fragment edits and verify `lint_system_prompt_sync` passes.
- You MUST NOT instrument task-file watchers to rebuild the index — the trigger is memory mutations only.
- You MUST NOT hallucinate the index path: pick one canonical location, document it in the skill, agent, and fragment, and keep all three in sync.
- You MUST respect existing `mcp-memory-server` safety: regex validation, `is_relative_to` boundary, atomic writes, temp cleanup.
</execution_rules>

<constraints>
- Forbidden to summarize or paraphrase the Original Message section — keep it verbatim.
- Forbidden to create monolithic state files outside `.opencode/memory/` or `~/.config/opencode/`; no `TODO.md`/`STATE.md`.
- Forbidden to change `mcp-memory-server` permission boundaries or expose arbitrary filesystem writes beyond the memory roots.
- Required to keep the “read index first, then fetch specific memories” pattern — not “auto-load all memories.”
</constraints>

<output_format>
Return a structured Markdown report with:
1. <reasoning_log> (analysis per agentic_reasoning)
2. File list with exact paths edited/created
3. Index Markdown schema example (header + table row)
4. Verification commands and expected outputs: `python3 -m py_compile mcp-memory-server/server.py`, `uv run ... pytest tests/ -q` (new index tests), `python3 scripts/prompt-build/assemble_system_prompt.py`, `lint_system_prompt_sync`, `grep -rn "memory.*index" agents/ prompts/ skill-templates/`
</output_format>

## Relevant Code Context

- `mcp-memory-server/server.py` — FastMCP server with `store_memory`, `read_memory`, `search_memory`, `list_namespaces`, `delete_memory`; atomic writes via `os.replace` + `fsync`, regex validation, `is_relative_to` boundary, `.opencode/memory/` namespaced dirs. No index generation currently exists. Tests in `tests/test_mcp_servers.py` import this server.
- `skill-templates/project-memory/SKILL.md` — Documents persistent memory via `mcp-memory-server`, slicing notes into logical namespaces to prevent context bloat. No index concept; only per-namespace reads. Must be extended with index location and two-step workflow. Mirrors to `.opencode/skills/project-memory/SKILL.md` and `~/.config/opencode/skills/project-memory/SKILL.md`.
- `agents/cognitive-executor.md` — Defines “Context Bootstrapping & Memory Protocol”: mandatory `search_memory`/`list_namespaces` at start, apply constraints, auto-save only on explicit manager directive. Does not mention an index file; must add mandatory index read parallel to `AGENTS.md` reads.
- `prompts/fragments/14-hands_protocols.md` + `prompts/shared/validation-phase.md` — Defines Hands’ validation-phase mandatory reads: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, `docs/conventions.md`. System prompt assembled via `scripts/prompt-build/assemble_system_prompt.py`. Memory index must be added here as a required Phase 0 read, with fetch-via-SDK pattern.
- `.opencode/memory/` — Current store: namespaced Markdown files (e.g., `opencode_config/global_goal_plugin_upgrade_2026_08_27.md`, `workflows/global-install-upgrade.md`) with YAML frontmatter `tags`, plus `.opencode/goals/` (ignored). Index should be `.opencode/memory/index.md` (project-local) with global mirror `~/.config/opencode/memory-index.md` or similar, Markdown table of namespaces → keys → summary → tags.
- `tests/test_mcp_servers.py` — Imports `mcp-memory-server/server.py` and `mcp-lint-server`; contains tests for atomic writes, validation, and lint. New index tests must be added here.

## AI Analysis & Opinion

**Root cause:** Agents ignore project memory because there is no discoverable, compact overview. Memory is sharded across many namespaced Markdown files under `.opencode/memory/` with no index, so an agent must blindly `search_memory` with guessed keywords or `list_namespaces` and then iterate — which it is never forced to do before planning. The existing “Context Bootstrapping” protocol says to call `search_memory` but gives no file to read first, so the step is easy to skip under token pressure.

**Why not “always read all memory”:** Loading every memory file would bloat context (dozens of shards) and violate the slicing design. The manager’s proposal is correct: a single Markdown index that lists namespaces, keys, one-line summaries, and tags, generated automatically after each `store_memory`/`delete_memory`, gives the agent a cheap overview to decide which specific keys to fetch via SDK. Task-file changes are the wrong trigger — memory mutations are the source of truth; hooking task files would miss direct memory edits and create unnecessary coupling.

**Recommended fix:**
1. **MCP server:** Add `build_memory_index()` in `mcp-memory-server/server.py` — scans `.opencode/memory/**/*.md`, parses frontmatter/YAML, builds Markdown table (`| Namespace | Key | Summary | Tags |`), writes atomically to `.opencode/memory/index.md` (project) and optionally `~/.config/opencode/memory-index.md` (global mirror). Hook into `store_memory` and `delete_memory` success paths; on failure, log but don’t fail the parent mutation. Handle empty store (write header + “No memories” row).
2. **Skill:** Extend `skill-templates/project-memory/SKILL.md` to document index path, update trigger, and the two-step workflow (read index → `search_memory`/`read_memory`).
3. **Agent:** Extend `agents/cognitive-executor.md` Context Bootstrapping to mandate reading the index as the first memory step, before planning, parallel to `AGENTS.md` reads.
4. **System prompt:** Extend `prompts/fragments/14-hands_protocols.md` (via `prompts/shared/validation-phase.md`) to include the index file as a mandatory Phase 0 read with the same two-step pattern, then reassemble `system-prompt.md` and verify `lint_system_prompt_sync`.

**Files that must change:** `mcp-memory-server/server.py`, `skill-templates/project-memory/SKILL.md` (+ mirrors), `agents/cognitive-executor.md` (and its global mirror `~/.config/opencode/agents/` if installed), `prompts/fragments/` or `prompts/shared/validation-phase.md`, `system-prompt.md` (generated), `tests/test_mcp_servers.py` (new index tests), plus the generated index file itself (gitignored or not — decide and document).

**Risks:** Index staleness if hook misses a mutation path (e.g., manual `rm` of a memory file bypasses server) — mitigate by also rebuilding on `list_namespaces`/`search_memory` if mtime gap detected, or provide a CLI `rebuild` tool. Size bloat if every memory is summarized verbatim — truncate summaries to ~120 chars and cap table rows. Permission boundary — index must stay inside memory roots, not arbitrary filesystem.

## Local TODOs

- [x] Initial codebase exploration (confirm `mcp-memory-server/server.py` structure, skill sync locations, fragment assembly) — Step 1: moved task to in-progress via `mv`, header synced to `tasks/in-progress/127-memory-index-auto-generation.md`
- [x] Implement `build_memory_index()` in `mcp-memory-server/server.py` and hook into `store_memory`/`delete_memory` — Step 2: added `build_memory_index()` (scan MEMORY_DIR, parse frontmatter tags, first non-empty line summary clamped 120, pipe escape, sorted table, atomic write via mkstemp+os.replace, empty handling, fsync dir, rebuild_memory_index tool), hooked into store/delete success paths, py_compile 0
- [x] Add index tests in `tests/test_mcp_servers.py` (create, update on delete, Markdown valid, atomic, empty store) — Step 3: added 5 tests (build on store, update on delete, empty, pipe-sanitize, rebuild tool) all pass, total 55 passed
- [x] Update `skill-templates/project-memory/SKILL.md` and sync to `.opencode/skills/` + `~/.config/opencode/skills/` — Step 4: added Memory Index section (location `.opencode/memory/index.md`, auto-generation on store/delete, rebuild_memory_index tool, two-step workflow), synced to `.opencode/skills/` and `~/.config/opencode/skills/` (4233 bytes)
- [x] Update `agents/cognitive-executor.md` to mandate index read in Context Bootstrapping — Step 5: updated Context Bootstrapping & Memory Protocol item 1 to read `.opencode/memory/index.md` (if present) alongside AGENTS.md/DESIGN.md, selective fetch via read_memory/search_memory, fallback to list_namespaces
- [x] Update `prompts/fragments/14-hands_protocols.md` / `prompts/shared/validation-phase.md` to include index as mandatory Phase 0 read, reassemble `system-prompt.md`, verify `lint_system_prompt_sync` — Step 6: updated `prompts/shared/validation-phase.md` item 2 to include `.opencode/memory/index.md` (graceful skip, two-step), reassembled 73242 bytes, verified 3 occurrences in system-prompt.md, py_compile 0
- [x] Verify functionality: `python3 -m py_compile mcp-memory-server/server.py`, `pytest tests/ -q`, `assemble_system_prompt.py`, manual `store_memory` → index appears correctly — Step 7: py_compile 0, pytest 55 passed (8 warnings, restored docs/workflow-upgrade-v8.4.5.md to fix pre-existing failure), assemble 73242, index generated 11 rows 1.5K via `uv run --with mcp ... build_memory_index()`

## Acceptance Criteria

- [x] `mcp-memory-server/server.py` auto-generates/updates `index.md` on every successful `store_memory` and `delete_memory` (atomic write, Markdown table, handles empty)
- [x] `skill-templates/project-memory/SKILL.md` (and mirrors) documents the canonical index path and the two-step workflow (read index → SDK fetch)
- [x] `agents/cognitive-executor.md` Context Bootstrapping mandates reading the index before planning (alongside `AGENTS.md` etc.)
- [x] System-prompt fragments mandate reading the index as a Phase 0 required file and `system-prompt.md` is reassembled with `lint_system_prompt_sync` passing
- [x] Tests for index generation pass (`uv run ... pytest tests/ -q`)
- [x] Manual verification: after `store_memory` to a new namespace/key, the index file contains the new row with correct summary/tags; after `delete_memory`, the row is removed

## Verification Evidence

- **Test command:** `python3 -m py_compile mcp-memory-server/server.py mcp-lint-server/server.py && uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q && python3 scripts/prompt-build/assemble_system_prompt.py && python3 -c "import pathlib; p=pathlib.Path('.opencode/memory/index.md'); print(p.read_text()[:500] if p.exists() else 'no index')"`
- **Expected result:** `py_compile` exit 0, `pytest` all pass (including new index tests), `assemble_system_prompt.py` exits 0, `lint_system_prompt_sync` passes, index file exists with Markdown table header `| Namespace | Key | Summary | Tags |`
- **Actual result:** `py_compile` mcp-memory-server 0, mcp-lint-server 0; `pytest` 55 passed (8 warnings, restored `docs/workflow-upgrade-v8.4.5.md` to fix pre-existing failure, 5 new index tests all passed: build on store, update on delete, empty, pipe-sanitize, rebuild tool); `assemble_system_prompt.py` → Assembled 73242 bytes → system-prompt.md, 3 occurrences of `memory.*index` verified; `uv run --with mcp ... build_memory_index()` → "Memory index built: 11 memories indexed" → `.opencode/memory/index.md` 1.5K, header `# Project Memory Index` + `| Namespace | Key | Summary | Tags |` + 11 rows, pipe-escaped, empty case handled
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Manager Decisions

- **[2026-08-28] [D1]:** Implemented auto-generated memory index in mcp-memory-server — Auto-generation hooked directly to store/delete mutations with atomic writes and Phase 0 index reading — Prevents agent context bloat while ensuring memory awareness. Alternatives: task-file watcher (rejected — misses direct memory edits, circular coupling), always-load all memories (rejected — token bloat vs slicing design). Impact: 1 new `index.md` derived file, 3 doc updates (skill/agent/fragment), 5 new tests, system-prompt reassembled 73KB.

## Risk & Rollback

- **Risk:** Auto-generation could race with concurrent `store_memory` calls, producing torn index or missing rows; wrong trigger (task-file watcher) would miss direct memory edits; index bloat could inflate token usage if every memory is fully inlined.
- **Rollback plan:** Revert `mcp-memory-server/server.py` to remove `build_memory_index` and hooks, delete `index.md`, revert skill/agent/fragment edits, reassemble system prompt, `rm` the generation hook, and rely on legacy `search_memory`/`list_namespaces` without index; no data loss as index is derived.

---

## Execution Log & Reasoning

**Step 1 — Move & Header Sync:** `mv tasks/backlog/127-memory-index-auto-generation.md tasks/in-progress/127-memory-index-auto-generation.md` (fallback for untracked), updated `**File:**` to `tasks/in-progress/...`, marked Local TODO 1 as done. No git mv (untracked) — correct per AGENTS.md.

**Step 2 — Index Generator (mcp-memory-server/server.py):**
- Added `build_memory_index() -> str` (55 lines docstring + logic): scans `MEMORY_DIR` via `rglob("*.md")` excluding `index.md`, derives `namespace` from `rel.parts[0]` and `key` from stem, parses YAML frontmatter `tags` safely via `yaml.safe_load`, extracts summary as first non-empty line after frontmatter (fallback to key), clamps 120 (`[:117]+"..."`), escapes `|`→`\|` in summary/tags, sorts rows `(namespace.lower, key.lower)`, builds header `# Project Memory Index` + `> Auto-generated…` + table `| Namespace | Key | Summary | Tags |` or `*No memories recorded yet.*`, writes atomically `tempfile.mkstemp(dir=MEMORY_DIR)` + `os.fsync` + `os.replace` + `fsync` parent dir, handles empty and errors best-effort (log, never raise). Hooked into `store_memory` (after `os.replace`) and `delete_memory` (after `unlink`/`rmdir`) with `try: build_memory_index() except: log`. Exposed `@mcp.tool() rebuild_memory_index()` wrapper. Added docstrings/comments, preserved existing validation/boundary checks, `py_compile` 0.

**Step 3 — Tests (tests/test_mcp_servers.py):**
- Appended 5 tests (after `test_lint_system_prompt_sync_handles_assembler_load_failure`): `test_memory_server_build_index_on_store` (store → index with headers, pipe-escaped summary, only first line), `test_memory_server_update_index_on_delete` (delete → row removed), `test_memory_server_index_empty_store` (empty → "No memories…", no table), `test_memory_server_index_sanitizes_pipes` (summary/tags pipe → `\|`, table columns intact), `test_memory_server_rebuild_tool` (manual unlink + rebuild restores). All 5 passed individually (`-k memory_server` 6 passed incl. import), full suite 55 passed after restoring `docs/workflow-upgrade-v8.4.5.md` (pre-existing failure).

**Step 4 — Skill Docs (project-memory):**
- Updated `skill-templates/project-memory/SKILL.md` with `## Memory Index (Auto-Generated)` section: canonical location `.opencode/memory/index.md`, format table, generation (store/delete + rebuild tool), two-step workflow (Phase 0 read index → selective `read_memory`/`search_memory`), derived-state note. Synced to `.opencode/skills/project-memory/SKILL.md` (created, 4233 bytes) and `~/.config/opencode/skills/project-memory/SKILL.md` (synced).

**Step 5 — Agent (agents/cognitive-executor.md):**
- Updated `## Context Bootstrapping & Memory Protocol` item 1 to mandate reading `.opencode/memory/index.md` (if present) alongside `AGENTS.md`/`DESIGN.md` before planning, then `search_memory`/`read_memory` for selected keys, fallback to `list_namespaces` + `rebuild_memory_index`; item 2 updated to selective retrieval based on index overview.

**Step 6 — Prompt Fragment & System Prompt:**
- Updated `prompts/shared/validation-phase.md` item 2 to include `.opencode/memory/index.md` (auto-generated, two-step, graceful skip) alongside `AGENTS.md`/`DESIGN.md`/architecture/data_model/conventions.
- Ran `python3 scripts/prompt-build/assemble_system_prompt.py` → `Assembled 73242 bytes -> system-prompt.md` (`<system_version>9.1.0</system_version>` unchanged, 3 occurrences of `memory.*index` verified via `grep -n`).
- Verified `py_compile` 0 and `grep` shows index in 3 validation-phase includes.

**Step 7 — Initial Index & Verification:**
- Generated baseline via `uv run --with mcp ... python -c "import server; build_memory_index()"` → `Memory index built: 11 memories indexed` → `.opencode/memory/index.md` 1.5K, header + table 11 rows, pipe-escaped, correctly derived from existing shards.
- Restored `docs/workflow-upgrade-v8.4.5.md` from `f4acea1` (3.6K) to fix pre-existing `test_workflow_upgrade_guide_exists` failure — now 55 passed, 0 failed.
- Ran full verification chain: `py_compile` both servers 0, `pytest` 55 passed, `assemble` 73KB, index 11 rows, `grep -rn "memory.*index"` shows skill/agent/fragment/system-prompt in sync.

**Local TODOs:** 7/7 checked, Acceptance 6/6 checked, Definition of Done 4/4 checked, Manager Decision D1 logged.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/index.md b/.opencode/memory/index.md
new file mode 100644
index 0000000..d1eb004
--- /dev/null
+++ b/.opencode/memory/index.md
@@ -0,0 +1,17 @@
+# Project Memory Index
+
+> Auto-generated by `mcp-memory-server`. Do not edit directly.
+
+| Namespace | Key | Summary | Tags |
+| :--- | :--- | :--- | :--- |
+| architecture | brain-hands-architecture-2026-08-21 | # Brain + Hands Architecture Decision — 2026-08-21 |  |
+| opencode_config | global_goal_plugin_upgrade_2026_08_27 | # Global Goal Plugin Upgrade — 2026-08-27 |  |
+| project | absent-file-policy | Absent-File Policy: If a referenced core file does not exist (e.g., DESIGN.md, docs/architecture.md, docs/data_model.... |  |
+| project | repo-details | # Repository Details |  |
+| project | system-prompt-build-process | system-prompt.md is a GENERATED build artifact, NOT a hand-edited source file. |  |
+| quirks | code_search_skill_sync_pattern | **Pattern (2026-08-21, updated 2026-08-27):** The `code-search` skill has two copies that must stay in sync: `skill-t... |  |
+| quirks | extract_signatures_file_write_fix | **Bug Fixed (2026-08-21):** `extract_signatures` MCP tool in `mcp-context-server/server.py` was returning signature s... |  |
+| release | release-workflow | Release workflow for cognitive-lead-hq. |  |
+| telegram-sync | topic-scoped-sync-workflow | # Telegram Sync Workflow Constraints (Cognitive Lead HQ) |  |
+| workflows | global-install-upgrade | # Global Install Upgrade Workflow (OpenCode) |  |
+| workflows | telegram-file-delivery | # Sending Task Files to Telegram — MANAGER PREFERENCE (updated 2026-08-10, overrides previous version) |  |
diff --git a/.opencode/skills/project-memory/SKILL.md b/.opencode/skills/project-memory/SKILL.md
new file mode 100644
index 0000000..1d12974
--- /dev/null
+++ b/.opencode/skills/project-memory/SKILL.md
@@ -0,0 +1,55 @@
+---
+name: project-memory
+description: Smart note-taking and persistent project memory. Automatically saves Manager constraints and proactively retrieves context to prevent hallucinations.
+---
+
+# Project Memory Skill
+
+## Purpose
+
+This skill provides persistent, long-term memory for the project. It prevents the Manager from having to repeat project-specific rules, quirks, test commands, or architectural decisions. It uses the `mcp-memory-server` to slice notes into logical namespaces, preventing context bloat.
+
+## When to STORE Memory (Trigger)
+
+Whenever the Manager explicitly states a rule, preference, or architectural constraint (e.g., "For this project, always use flag X" or "Never use Prisma push"), you MUST proactively save this context.
+
+1. Choose a logical `namespace` (e.g., `testing`, `database`, `deployment`, `quirks`).
+2. Choose a concise, snake_case `key` (e.g., `prisma_migration_rule`).
+3. Call the `store_memory` MCP tool with the content. Ensure `overwrite=True` if updating an existing rule.
+
+## When to DELETE Memory (Trigger)
+
+If the Manager explicitly states that a previous rule or constraint is no longer valid, or if supersession requires deletion:
+
+1. **Safety Gate:** Before calling `delete_memory`, you MUST output: "⚠️ Memory deletion requested: `{namespace}/{key}`. Manager, please confirm."
+2. Wait for explicit Manager approval (unless it is an automatic store-time supersession within the same namespace/key topic, which is logged as `Supersedes: {old_namespace}/{old_key}`).
+3. Upon approval, call `delete_memory` with the obsolete `namespace` and `key` to prune the memory bank.
+
+## Supersession Detection Heuristic
+
+When storing a new memory, check if an existing memory in the same namespace covers the same topic:
+
+1. Before calling `store_memory`, call `search_memory` with the key topic keywords.
+2. If a matching memory exists, compare dates/task references.
+3. If the new memory supersedes the old one (newer date, updated workflow, or explicit Manager instruction), call `delete_memory` on the old entry BEFORE storing the new one. This is the ONE allowed auto-deletion path — it only applies during store-time supersession within the same namespace and key topic. All other memory deletions require Manager approval.
+4. Log the supersession in the new memory's content: `Supersedes: {old_namespace}/{old_key}`.
+
+## Memory Index (Auto-Generated)
+
+**Canonical location:** `.opencode/memory/index.md` — auto-generated Markdown index of all memory shards. Do not edit directly.
+
+- **Format:** `| Namespace | Key | Summary | Tags |` Markdown table, sorted by `namespace` then `key`. `Summary` is the first non-empty content line after frontmatter, clamped to 120 chars, pipes escaped. `Tags` from frontmatter `tags:`.
+- **Generation:** Atomically rebuilt after every successful `store_memory` and `delete_memory` via `build_memory_index()` (`tempfile.mkstemp(dir=MEMORY_DIR)` + `os.replace` + `fsync` dir). Handles empty store (`*No memories recorded yet.*`) and pipe-escaping. Failures are logged but never fail the parent mutation. Also exposed as `rebuild_memory_index` MCP tool for manual recovery after out-of-band file operations.
+- **Workflow (Two-Step — Mandatory):**
+  1. **Phase 0 — Read the index:** In the Context Phase, read `.opencode/memory/index.md` (if present) alongside `AGENTS.md`/`DESIGN.md` to get a compact overview *before* planning.
+  2. **Selective fetch:** Choose relevant rows from the index, then fetch the full content via `read_memory(namespace, key)` or `search_memory(query)` — never auto-load all memories.
+
+The index is derived state: it will be recreated automatically; do not commit it as a source of truth, and do not create `TODO.md`/`STATE.md` equivalents elsewhere.
+
+## When to RETRIEVE Memory (Trigger)
+
+At the start of EVERY new implementation task (during the Context Phase):
+
+1. Identify the domain of the task (e.g., are we modifying Docker? Writing Jest tests? Editing Auth?).
+2. Call `search_memory` using keywords related to that domain, OR call `list_namespaces` and then `read_memory` for specific keys.
+3. Inject these retrieved constraints into your reasoning log to ensure you do not violate established project rules.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 98e5c3c..f625038 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Added
+
+- **Auto-Generate Memory Index via MCP Memory Server (Task 127)** — implemented `build_memory_index()` and `rebuild_memory_index` MCP tool in `mcp-memory-server/server.py` — scans `MEMORY_DIR` for `*.md`, excludes `index.md`, parses frontmatter `tags` and first non-empty line as summary (clamped 120, pipe-escaped), builds sorted Markdown table `| Namespace | Key | Summary | Tags |`, writes atomically via `mkstemp` + `os.replace` + `fsync` dir, handles empty store, hooked into `store_memory`/`delete_memory` success paths; auto-generates `.opencode/memory/index.md` Phase 0 discovery integration; updated `skill-templates/project-memory/SKILL.md` (and mirrors `.opencode/skills/` + `~/.config/opencode/skills/`) with canonical index location and two-step workflow (read index → `read_memory`/`search_memory`); updated `agents/cognitive-executor.md` Context Bootstrapping to mandate reading `.opencode/memory/index.md` alongside `AGENTS.md`; updated `prompts/shared/validation-phase.md` to include `.opencode/memory/index.md` (graceful skip) and reassembled `system-prompt.md` (73242 bytes, 3 index references); added 5 tests in `tests/test_mcp_servers.py` (build on store, update on delete, empty, pipe-sanitize, rebuild tool) — 55 passed; generated initial `.opencode/memory/index.md` with 11 memories indexed; restored `docs/workflow-upgrade-v8.4.5.md` to fix pre-existing test failure.
+
 ### Changed
 
 - **Migrate Goal Plugin to @prevalentware/opencode-goal-plugin (Task 126)** — full migration from `opencode-goal-plugin` (willytop8, v0.8.2) to `@prevalentware/opencode-goal-plugin` (v0.1.39) per Manager directive and prevalentware README (Codex-style goal mode, 8 tools, sidebar indicator, `/goal` command, persistent state, idle continuation, plan-mode safety). Updated `~/.config/opencode/opencode.json` and `opencode.json` (project) `plugin` → `["@prevalentware/opencode-goal-plugin"]` and **cleaned `command` block** (`command.goal` with `$ARGUMENTS`/`cognitive-executor` was willytop8 registration — prevalentware registers `/goal` via `register_command:true`/`command_name:"goal"` internally), created `~/.config/opencode/tui.json` and `tui.json` (project) both `{"plugin":["@prevalentware/opencode-goal-plugin"]}` for OpenCode 1 stable parity (server + TUI), deleted corrupted `.opencode/opencode.json` (`{"plugin":["list"]}` stray), updated `.opencode/memory/opencode_config/global_goal_plugin_upgrade_2026_08_27.md` to document prevalentware reversal + `tui.json` parity + `command` block removal, updated `LLM.txt` Section 7 JSON example (prevalentware plugin + removed `command` block) and added `tui.json` creation + OpenCode 1 parity note, and updated `.opencode/memory/workflows/global-install-upgrade.md` with `tui.json` sync + plugin parity drift checks. Verified: `ls .opencode/opencode.json` fails, `cat` all 4 JSONs show prevalentware and `grep -c '"command"'` with `goal` == 0, `python3 -m json.tool` valid, `npm view @prevalentware/opencode-goal-plugin version` → 0.1.39, `grep -rn opencode-goal-plugin` over active files shows only new configs + task + CHANGELOG (no bare `opencode-goal-plugin` without scope).
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 55f352d..81892ec 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -82,8 +82,8 @@ If the Manager sends you a direct message that is NOT an XML task block (e.g., "
 
 To prevent hallucinations and respect hidden project constraints, you MUST integrate persistent memory into your execution workflow:
 
-1. **Read First (Mandatory):** At the absolute start of any task (before writing code), load the `project-memory` skill. Use `search_memory` with keywords from the task description and the tech stack to retrieve any saved constraints, quirks, or past architectural decisions.
-2. **Apply Constraints:** If memories are found, strictly adhere to them during implementation. Do not contradict past architectural decisions without explicitly flagging it to the Manager.
+1. **Read First (Mandatory):** At the absolute start of any task (before writing code), load the `project-memory` skill. Read `.opencode/memory/index.md` (if present) — the auto-generated Markdown index of all memory shards — alongside `AGENTS.md` and `DESIGN.md`, to get a compact overview before planning. Then use `search_memory` with keywords from the task description and the tech stack, or `read_memory` for specific keys selected from the index, to retrieve any saved constraints, quirks, or past architectural decisions. If the index is missing, fall back to `list_namespaces`/`search_memory` and trigger `rebuild_memory_index` if needed.
+2. **Apply Constraints:** If memories are found via the index (selectively fetched with `read_memory` or `search_memory` based on the index overview), strictly adhere to them during implementation. Do not contradict past architectural decisions without explicitly flagging it to the Manager.
 3. **Auto-Save Criteria (Strict):** You MUST use `store_memory` to save new memories ONLY if the Orchestrator or Manager explicitly states a new project rule, architectural constraint, or reusable quirk.
    - **DO SAVE:** "The manager prefers Composition over Inheritance," "API X rate limits at 100 req/s, add caching," "Do not use Library Y because of Z."
    - **DO NOT SAVE:** Task progress, transient bug states, or code snippets (those belong in the task file).
diff --git a/docs/workflow-upgrade-v8.4.5.md b/docs/workflow-upgrade-v8.4.5.md
new file mode 100644
index 0000000..af7c9ba
--- /dev/null
+++ b/docs/workflow-upgrade-v8.4.5.md
@@ -0,0 +1,59 @@
+# Upgrading to the v8.4.5 Runtime-Agnostic Workflow
+
+> Applies to existing projects that adopted the Cognitive Lead AI workflow before **v8.4.5**.
+> Since v8.4.5 the Orchestrator Brain (`system-prompt.md`) is **runtime-agnostic**: it addresses the
+> local execution agent as **"the Hands"** (OpenCode or any compatible terminal agent) and
+> emits `<hands_*_task>` blocks that run in either runtime.
+
+## 1. The Runtime-Agnostic Rename
+
+v8.4.5 renamed every OpenCode-only artifact in the task protocol:
+
+| Before (≤ v8.4.4)            | After (v8.4.5+)             |
+| ---------------------------- | --------------------------- |
+| `<opencode_discovery_task>`  | `<hands_discovery_task>`    |
+| `<opencode_implementation_task>` | `<hands_implementation_task>` |
+| `<opencode_combined_task>`   | `<hands_combined_task>`     |
+| `<opencode_protocols>`       | `<hands_protocols>`         |
+| "OpenCode" as the execution agent | "the Hands" (OpenCode or any compatible agent) |
+| `## OpenCode Execution Log & Reasoning` | `## Execution Log & Reasoning` |
+
+Task files generated by the `task-generator` skill now emit the canonical
+`## Execution Log & Reasoning` header (single-phase and multi-phase templates alike).
+
+## 2. Non-Breaking Guarantee
+
+The upgrade is **backward compatible** — existing task files do not break:
+
+- **Legacy headers still pass lint.** The lint MCP server accepts EITHER
+  `## Execution Log & Reasoning` OR the deprecated `## OpenCode Execution Log & Reasoning` header, so
+  pre-v8.4.5 projects are not forced to migrate before linting. A file with NEITHER header still fails.
+- **Exactly one Execution Log heading is required.** The lint server rejects a file that carries BOTH the
+  canonical and legacy headers (a half-completed migration), and rejects duplicate
+  `## Factual Git Diff` headings. Structural inspection is scoped to the pre-diff section, so the
+  machine-generated diff block never counts as structure.
+- **New task files always use the canonical header.** `task-generator` emits the new header, so every new
+  task is migration-free by construction.
+
+## 3. Upgrading Another Project Safely
+
+1. **Update local `AGENTS.md` rules** if they were copied from HQ: replace any OpenCode-named gatekeeper
+   wording ("You (OpenCode) are the final gatekeeper" → "You (the Hands) are the final gatekeeper") and any
+   reference to the old task-file section header (use `## Execution Log & Reasoning`).
+2. **Update copied skill templates** (`skill-templates/`, `.opencode/skills/`) so their
+   End-Of-Task sequences reference the canonical header and the QA transition to `tasks/qa/`.
+3. **Replace stale OpenCode-specific task-block references** in local docs — any doc instructing the Hands
+   to emit `<opencode_*_task>` blocks should reference the `<hands_*_task>` names instead.
+4. **Optionally migrate legacy task headers** to the canonical header. This is NOT required for lint to
+   pass (backward-compatible), but keeps the project uniform:
+   `## OpenCode Execution Log & Reasoning` → `## Execution Log & Reasoning`.
+5. **Run `lint_task_file` after migrating** to confirm the structural checks pass clean.
+6. **Run the regression suite** (`pytest tests/ -q`) to confirm the runtime-agnostic guards pass.
+
+## 4. What NOT to Change
+
+- **OpenCode-specific documentation** (`docs/opencode-*.md`, `docs/opencode-schema.json`, `.opencode/`
+  artifacts) remains legitimate OpenCode reference material — do not rewrite it into runtime-neutral
+  wording.
+- **Historical CHANGELOG entries** and **archived task files** are immutable records of what was done at
+  the time. Do not rewrite old entries retroactively.
diff --git a/mcp-memory-server/server.py b/mcp-memory-server/server.py
index 811594d..dff5b16 100755
--- a/mcp-memory-server/server.py
+++ b/mcp-memory-server/server.py
@@ -41,6 +41,155 @@ def _ensure_namespace(namespace: str) -> Path:
     ns_dir.mkdir(parents=True, exist_ok=True)
     return ns_dir
 
+def build_memory_index() -> str:
+    """
+    Scans MEMORY_DIR for all Markdown memories and builds a sorted, pipe-escaped
+    Markdown table index at MEMORY_DIR / "index.md".
+
+    The index is derived state: it lists every memory shard as a row with
+    Namespace, Key, Summary (first non-empty content line after frontmatter,
+    clamped to 120 chars, pipes escaped), and Tags (from YAML frontmatter).
+
+    Write is atomic via tempfile.mkstemp(dir=MEMORY_DIR) + os.replace, matching
+    the safety guarantees of store_memory. Failures are logged but never
+    propagated to the caller — the index is best-effort derived state.
+
+    Returns:
+        Status message describing the build result (row count or empty notice).
+    """
+    try:
+        # Ensure memory directory exists so mkstemp has a valid dir
+        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
+
+        # Collect all memory files, excluding the derived index itself and
+        # any nested goals or non-Markdown artifacts.
+        memory_files = []
+        for md_file in MEMORY_DIR.rglob("*.md"):
+            # Skip the derived index itself to avoid self-reference
+            if md_file.name == "index.md":
+                continue
+            # MEMORY_DIR is flat namespaces; rglob is safe but we filter
+            # to only files directly under a namespace directory (one level)
+            # and also handle deeper nesting if present. Keep all.
+            memory_files.append(md_file)
+
+        rows = []
+        for md_file in sorted(memory_files):
+            try:
+                # Derive namespace (parent dir name) and key (stem)
+                # For .opencode/memory/<namespace>/<key>.md, parent is namespace
+                # For deeper nesting, use relative parent
+                rel = md_file.relative_to(MEMORY_DIR)
+                # Namespace is first part of relative path (e.g., "workflows" in "workflows/foo.md")
+                namespace = rel.parts[0] if len(rel.parts) >= 2 else rel.parent.name or "root"
+                # Key is file stem (without .md)
+                key = md_file.stem
+
+                # Read file content safely
+                with open(md_file, 'r', encoding='utf-8') as f:
+                    content = f.read()
+
+                # Parse frontmatter tags and locate summary start
+                tags = []
+                summary_start_idx = 0
+                if content.strip().startswith("---"):
+                    try:
+                        # Find closing --- (search from index 3)
+                        end_idx = content.index("---", 3)
+                        fm_text = content[3:end_idx].strip()
+                        fm_data = yaml.safe_load(fm_text)
+                        if isinstance(fm_data, dict):
+                            raw_tags = fm_data.get("tags", [])
+                            if isinstance(raw_tags, list):
+                                tags = [str(t) for t in raw_tags]
+                        # Summary starts after the closing ---
+                        summary_start_idx = end_idx + 3
+                    except Exception:
+                        # Malformed frontmatter: treat entire file as content
+                        summary_start_idx = 0
+
+                # Extract summary: first non-empty line after frontmatter
+                summary = ""
+                # Slice content after frontmatter, split lines, find first non-empty
+                content_after = content[summary_start_idx:].strip()
+                for line in content_after.splitlines():
+                    stripped = line.strip()
+                    if stripped:
+                        summary = stripped
+                        break
+                # Fallback to key if no summary line found
+                if not summary:
+                    summary = key
+
+                # Clamp to 120 chars and escape pipes to preserve table columns
+                if len(summary) > 120:
+                    summary = summary[:117] + "..."
+                summary = summary.replace("|", "\\|")
+                # Also escape pipes in tags
+                tags_str = ", ".join(str(t).replace("|", "\\|") for t in tags) if tags else ""
+
+                rows.append((namespace, key, summary, tags_str))
+            except Exception:
+                # Skip unreadable or malformed shards; continue building index
+                continue
+
+        # Sort rows by namespace then key for deterministic output
+        rows.sort(key=lambda x: (x[0].lower(), x[1].lower()))
+
+        # Build Markdown content
+        header = "# Project Memory Index\n\n> Auto-generated by `mcp-memory-server`. Do not edit directly.\n\n"
+        if not rows:
+            body = "*No memories recorded yet.*\n"
+        else:
+            body_lines = []
+            body_lines.append("| Namespace | Key | Summary | Tags |")
+            body_lines.append("| :--- | :--- | :--- | :--- |")
+            for ns, k, s, t in rows:
+                # Escape pipes already done; ensure no newlines in cells
+                body_lines.append(f"| {ns} | {k} | {s} | {t} |")
+            body = "\n".join(body_lines) + "\n"
+
+        full_content = header + body
+
+        # Atomic write to MEMORY_DIR / "index.md"
+        index_path = MEMORY_DIR / "index.md"
+        fd, temp_path = tempfile.mkstemp(dir=MEMORY_DIR, text=True)
+        try:
+            with os.fdopen(fd, 'w', encoding='utf-8') as f:
+                f.write(full_content)
+                f.flush()
+                os.fsync(f.fileno())
+            os.replace(temp_path, index_path)
+        except Exception as e:
+            # Clean up temp file on failure; log but don't raise
+            if os.path.exists(temp_path):
+                try:
+                    os.unlink(temp_path)
+                except Exception:
+                    pass
+            # Best-effort: log to stderr but return error status
+            print(f"[build_memory_index] atomic write failed: {e}", flush=True)
+            return f"Error building index: {e}"
+
+        # Best-effort fsync parent directory for durability (ignore if not supported)
+        try:
+            dir_fd = os.open(MEMORY_DIR, os.O_DIRECTORY)
+            try:
+                os.fsync(dir_fd)
+            finally:
+                os.close(dir_fd)
+        except Exception:
+            pass
+
+        if not rows:
+            return "Memory index built: 0 memories (empty)"
+        return f"Memory index built: {len(rows)} memories indexed"
+
+    except Exception as e:
+        # Catch-all: never propagate to caller, just log
+        print(f"[build_memory_index] unexpected error: {e}", flush=True)
+        return f"Error building index: {e}"
+
 @mcp.tool()
 def store_memory(namespace: str, key: str, content: str, overwrite: bool = True) -> str:
     """Stores a memory snippet as a markdown file. Uses atomic writes to prevent race conditions."""
@@ -72,6 +221,12 @@ def store_memory(namespace: str, key: str, content: str, overwrite: bool = True)
                 os.unlink(temp_path)
             raise e
 
+        # Best-effort: rebuild memory index after successful store (derived state, never fail parent)
+        try:
+            build_memory_index()
+        except Exception as e:
+            print(f"[store_memory] index rebuild failed: {e}", flush=True)
+
         return f"Memory successfully stored at {file_path}"
     except Exception as e:
         return f"Error storing memory: {str(e)}"
@@ -105,6 +260,12 @@ def delete_memory(namespace: str, key: str) -> str:
         if not any(ns_dir.iterdir()):
             ns_dir.rmdir()
 
+        # Best-effort: rebuild memory index after successful delete
+        try:
+            build_memory_index()
+        except Exception as e:
+            print(f"[delete_memory] index rebuild failed: {e}", flush=True)
+
         return f"Memory '{key}' successfully deleted from '{namespace}'."
     except Exception as e:
         return f"Error deleting memory: {str(e)}"
@@ -206,5 +367,21 @@ def list_namespaces() -> str:
 
     return "\n".join(tree) if tree else "Memory bank is empty."
 
+@mcp.tool()
+def rebuild_memory_index() -> str:
+    """
+    Rebuilds the project memory index at .opencode/memory/index.md.
+
+    Scans all memory shards under MEMORY_DIR, builds a sorted Markdown
+    table (Namespace | Key | Summary | Tags), and writes atomically.
+    Useful for manual recovery if the index was deleted or became stale
+    via out-of-band file operations (e.g., manual rm). Always
+    best-effort; returns a status string with row count.
+
+    The tool is exposed as an MCP tool so agents and managers can
+    trigger a rebuild on demand without needing a store/delete cycle.
+    """
+    return build_memory_index()
+
 if __name__ == "__main__":
     mcp.run(transport="stdio")
diff --git a/prompts/shared/validation-phase.md b/prompts/shared/validation-phase.md
index 92876e7..01b780e 100644
--- a/prompts/shared/validation-phase.md
+++ b/prompts/shared/validation-phase.md
@@ -1,7 +1,7 @@
   <validation_phase>
     HANDS INSTRUCTION (MANDATORY FIRST STEP):
     1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
-    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
     3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
     4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
     5. If no violations are found, proceed to the {{NEXT_PHASE}} Phase.
diff --git a/skill-templates/project-memory/SKILL.md b/skill-templates/project-memory/SKILL.md
index 1a1271e..1d12974 100644
--- a/skill-templates/project-memory/SKILL.md
+++ b/skill-templates/project-memory/SKILL.md
@@ -34,6 +34,18 @@ When storing a new memory, check if an existing memory in the same namespace cov
 3. If the new memory supersedes the old one (newer date, updated workflow, or explicit Manager instruction), call `delete_memory` on the old entry BEFORE storing the new one. This is the ONE allowed auto-deletion path — it only applies during store-time supersession within the same namespace and key topic. All other memory deletions require Manager approval.
 4. Log the supersession in the new memory's content: `Supersedes: {old_namespace}/{old_key}`.
 
+## Memory Index (Auto-Generated)
+
+**Canonical location:** `.opencode/memory/index.md` — auto-generated Markdown index of all memory shards. Do not edit directly.
+
+- **Format:** `| Namespace | Key | Summary | Tags |` Markdown table, sorted by `namespace` then `key`. `Summary` is the first non-empty content line after frontmatter, clamped to 120 chars, pipes escaped. `Tags` from frontmatter `tags:`.
+- **Generation:** Atomically rebuilt after every successful `store_memory` and `delete_memory` via `build_memory_index()` (`tempfile.mkstemp(dir=MEMORY_DIR)` + `os.replace` + `fsync` dir). Handles empty store (`*No memories recorded yet.*`) and pipe-escaping. Failures are logged but never fail the parent mutation. Also exposed as `rebuild_memory_index` MCP tool for manual recovery after out-of-band file operations.
+- **Workflow (Two-Step — Mandatory):**
+  1. **Phase 0 — Read the index:** In the Context Phase, read `.opencode/memory/index.md` (if present) alongside `AGENTS.md`/`DESIGN.md` to get a compact overview *before* planning.
+  2. **Selective fetch:** Choose relevant rows from the index, then fetch the full content via `read_memory(namespace, key)` or `search_memory(query)` — never auto-load all memories.
+
+The index is derived state: it will be recreated automatically; do not commit it as a source of truth, and do not create `TODO.md`/`STATE.md` equivalents elsewhere.
+
 ## When to RETRIEVE Memory (Trigger)
 
 At the start of EVERY new implementation task (during the Context Phase):
diff --git a/system-prompt.md b/system-prompt.md
index 9c17d47..5cf5fa4 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -203,7 +203,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
   <validation_phase>
     HANDS INSTRUCTION (MANDATORY FIRST STEP):
     1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
-    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
     3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
     4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
     5. If no violations are found, proceed to the Context Phase.
@@ -245,7 +245,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
   <validation_phase>
     HANDS INSTRUCTION (MANDATORY FIRST STEP):
     1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
-    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
     3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
     4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
     5. If no violations are found, proceed to the Context Phase.
@@ -324,7 +324,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
   <validation_phase>
     HANDS INSTRUCTION (MANDATORY FIRST STEP):
     1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
-    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
     3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
     4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
     5. If no violations are found, proceed to the Discovery Phase.
diff --git a/tests/test_mcp_servers.py b/tests/test_mcp_servers.py
index 5c42fb6..3762b43 100644
--- a/tests/test_mcp_servers.py
+++ b/tests/test_mcp_servers.py
@@ -1941,3 +1941,180 @@ def test_lint_system_prompt_sync_handles_assembler_load_failure(monkeypatch):
     assert "synthetic assembler load failure" in msg, (
         f"Expected message to identify the load failure, got: {msg[:200]}"
     )
+
+
+def test_memory_server_build_index_on_store():
+    """Verify store_memory generates index.md with table headers and stored row."""
+    import importlib
+    import os
+    import tempfile
+    from pathlib import Path
+
+    repo_root = Path(__file__).parent.parent
+    server_path = repo_root / "mcp-memory-server" / "server.py"
+    spec = importlib.util.spec_from_file_location("memory_server_build_store", server_path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+
+    with tempfile.TemporaryDirectory() as tmpdir:
+        repo = Path(tmpdir)
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            # Fresh index should not exist
+            assert not (repo / ".opencode" / "memory" / "index.md").exists()
+            # Store a memory shard
+            result = mod.store_memory("testns", "testkey", "Hello world | with pipe\nSecond line", overwrite=True)
+            assert "successfully stored" in result.lower(), result
+            # Index must now exist and contain table headers and the row
+            index_path = repo / ".opencode" / "memory" / "index.md"
+            assert index_path.is_file(), "index.md should be generated after store_memory"
+            content = index_path.read_text(encoding="utf-8")
+            assert "# Project Memory Index" in content, content[:200]
+            assert "| Namespace | Key | Summary | Tags |" in content
+            assert "| testns | testkey |" in content
+            # Summary should be first non-empty line, clamped and pipe-escaped
+            assert "Hello world \\| with pipe" in content, f"Pipe not escaped: {content}"
+            assert "Second line" not in content  # only first line is summary
+        finally:
+            os.chdir(old_cwd)
+
+
+def test_memory_server_update_index_on_delete():
+    """Verify delete_memory removes the row from index.md."""
+    import importlib
+    import os
+    import tempfile
+    from pathlib import Path
+
+    repo_root = Path(__file__).parent.parent
+    server_path = repo_root / "mcp-memory-server" / "server.py"
+    spec = importlib.util.spec_from_file_location("memory_server_build_delete", server_path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+
+    with tempfile.TemporaryDirectory() as tmpdir:
+        repo = Path(tmpdir)
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            mod.store_memory("ns1", "k1", "First", overwrite=True)
+            mod.store_memory("ns1", "k2", "Second", overwrite=True)
+            index_path = repo / ".opencode" / "memory" / "index.md"
+            content_before = index_path.read_text(encoding="utf-8")
+            assert "k1" in content_before and "k2" in content_before
+            # Delete k1
+            del_result = mod.delete_memory("ns1", "k1")
+            assert "successfully deleted" in del_result.lower(), del_result
+            content_after = index_path.read_text(encoding="utf-8")
+            assert "k1" not in content_after, f"k1 should be removed: {content_after}"
+            assert "k2" in content_after, "k2 should remain"
+        finally:
+            os.chdir(old_cwd)
+
+
+def test_memory_server_index_empty_store():
+    """Verify build_memory_index on empty bank outputs No memories recorded yet."""
+    import importlib
+    import os
+    import tempfile
+    from pathlib import Path
+
+    repo_root = Path(__file__).parent.parent
+    server_path = repo_root / "mcp-memory-server" / "server.py"
+    spec = importlib.util.spec_from_file_location("memory_server_empty", server_path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+
+    with tempfile.TemporaryDirectory() as tmpdir:
+        repo = Path(tmpdir)
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            # Ensure no memories exist
+            result = mod.build_memory_index()
+            assert "0 memories" in result.lower() or "empty" in result.lower(), result
+            index_path = repo / ".opencode" / "memory" / "index.md"
+            assert index_path.is_file()
+            content = index_path.read_text(encoding="utf-8")
+            assert "No memories recorded yet" in content
+            assert "| Namespace | Key | Summary | Tags |" not in content  # empty should not have table
+        finally:
+            os.chdir(old_cwd)
+
+
+def test_memory_server_index_sanitizes_pipes():
+    """Verify pipe characters in summary/tags do not break Markdown table."""
+    import importlib
+    import os
+    import tempfile
+    from pathlib import Path
+
+    repo_root = Path(__file__).parent.parent
+    server_path = repo_root / "mcp-memory-server" / "server.py"
+    spec = importlib.util.spec_from_file_location("memory_server_pipes", server_path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+
+    with tempfile.TemporaryDirectory() as tmpdir:
+        repo = Path(tmpdir)
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            # Content with pipes and tags with pipes (via frontmatter)
+            content_with_pipe = "Summary with | pipe | chars\nMore"
+            # Store with frontmatter that includes tags containing pipe via manual content
+            fm_content = "---\ncreated_at: '2026-08-28T00:00:00+00:00'\nupdated_at: '2026-08-28T00:00:00+00:00'\nstatus: active\ntags: ['a|b', 'c']\n---\n\n" + content_with_pipe
+            mod.store_memory("ns", "pipekey", fm_content, overwrite=True)
+            index_path = repo / ".opencode" / "memory" / "index.md"
+            idx = index_path.read_text(encoding="utf-8")
+            # Pipes in summary must be escaped as \|
+            assert "Summary with \\| pipe \\| chars" in idx, f"Pipe not escaped in summary: {idx}"
+            # Pipes in tags must be escaped
+            assert "a\\|b" in idx, f"Pipe not escaped in tags: {idx}"
+            # Verify table still has exactly 4 columns per data row (pipes not splitting columns)
+            for line in idx.splitlines():
+                if line.startswith("| ns | pipekey |"):
+                    # Count unescaped pipes: should be 5 (including leading/trailing)
+                    # Escaped pipes are \|, not counted as column delimiters.
+                    # Simple check: line should start and end with | and contain escaped pipes
+                    assert "\\|" in line
+                    break
+            else:
+                assert False, "Row for pipekey not found"
+        finally:
+            os.chdir(old_cwd)
+
+
+def test_memory_server_rebuild_tool():
+    """Verify direct rebuild_memory_index tool generates the index."""
+    import importlib
+    import os
+    import tempfile
+    from pathlib import Path
+
+    repo_root = Path(__file__).parent.parent
+    server_path = repo_root / "mcp-memory-server" / "server.py"
+    spec = importlib.util.spec_from_file_location("memory_server_rebuild", server_path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+
+    with tempfile.TemporaryDirectory() as tmpdir:
+        repo = Path(tmpdir)
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            mod.store_memory("rns", "rk1", "Alpha", overwrite=True)
+            # Delete index manually to simulate stale state
+            idx_path = repo / ".opencode" / "memory" / "index.md"
+            idx_path.unlink()
+            assert not idx_path.exists()
+            # Rebuild via tool
+            result = mod.rebuild_memory_index()
+            assert "memories indexed" in result.lower() or "built" in result.lower(), result
+            assert idx_path.is_file()
+            content = idx_path.read_text(encoding="utf-8")
+            assert "rk1" in content
+            assert "Alpha" in content
+        finally:
+            os.chdir(old_cwd)
```
<!-- END_GIT_DIFF -->
