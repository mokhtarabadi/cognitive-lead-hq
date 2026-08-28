# Task 127: Auto-Generate Memory Index via MCP Memory Server and Integrate into Agents

**File:** `tasks/completed/127-memory-index-auto-generation.md`
**Source:** telegram
**Type:** improvement
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `8f8c3ea8c21d14a698022a663144097fdc386d8d`
<!-- END_GIT_DIFF -->
