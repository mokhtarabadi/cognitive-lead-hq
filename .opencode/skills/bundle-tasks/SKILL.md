---
name: bundle-tasks
description: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as both CLI script and MCP tool for cross-project reuse.
---

# Bundle Tasks Skill — Meta-Task Bundling (Task 110)

Use this skill when the Manager wants to execute 4–6 small related tasks together instead of sequentially. It eliminates the `backlog → in-progress → qa → completed` round-trip overhead by bundling them into one branch, one `Factual Git Diff`, and one all-or-nothing QA gate.

## When to Use

- Manager says: "bundle tasks 1, 2, 5, 10, 15, 20", "create a meta-task from 12 15 20", "combine these polish tasks", or any note about "meta-task", "bundle", "supersede", "archive and bundle"
- Tasks are small, same stack/domain (e.g., all `android-kotlin`, all `react-vite`, all docs), and would be inefficient to run one-by-one
- You are in any project that has the `mcp-context-server` MCP server — the bundler is available as `bundle_tasks` MCP tool even when `scripts/bundle-tasks.py` is not on the Manager's local shell

**Do NOT use for:** large refactors, tasks with conflicting files that would cause merge conflicts in one diff, or tasks >6 without explicit `--force`.

## Core Contract (Deterministic, No LLM, No Hallucination)

1. **Verbatim Preservation:** Every source `## Goal`, `## Manager's Notes` / `## Blueprint Reference`, `## Acceptance Criteria` (including multi-line continuations and indented sub-bullets), `## Local TODOs`, `## Risk & Rollback` is copied verbatim into `### Source Task XX` blocks. No summarization. The `## Bundled Checklist` is derived by prefixing each source AC root bullet with `[XX]` and preserving all indented continuation lines.
2. **Single QA Gate:** All bundled criteria are `all-or-nothing`. If any line fails QA, the entire META is `QA_REJECTED`.
3. **Archive, Not Purge (with Transactional Rollback):** Sources are moved via `git mv` to `tasks/archive/` with `**Superseded-By:** <META_ID>-<slug>` until META is `completed`. History stays reachable via `git log --follow`. If ANY archive operation fails, ALL previously archived files are rolled back to their original locations, the META file is deleted, and the operation aborts cleanly.
4. **Guardrails:** `MAX_BUNDLE_SIZE=6` (reject >6 without `--force`), combined LOC >400 warning, missing-ID and duplicate-ID checks (hard halt on duplicate active IDs), stack conflict detection (warn or require `--force`), SHA verbatim checksum validation, atomic Next-ID creation with retry loop for concurrent safety.

## Two Invocation Paths (Pick One)

### Path A — CLI Script (preferred when you have shell)

This is the canonical, repo-local path. The script is the source of truth; the MCP tool wraps it.

```bash
uv run scripts/bundle-tasks.py <id> <id> ... --title "<kebab-or-human-title>" [--dry-run] [--force]
# Examples
uv run scripts/bundle-tasks.py 12 15 20 --title "android-polish-bundle"
uv run scripts/bundle-tasks.py 12 15 20 --title "android-polish-bundle" --dry-run
uv run scripts/bundle-tasks.py 1 2 3 4 5 6 7 --title "mega" --force   # bypass cap
```

### Path B — MCP Tool (preferred when you only have the MCP server)

The `mcp-context-server/server.py:bundle_tasks` tool is **fully self-contained** — it does NOT require `scripts/bundle-tasks.py` to exist. All helpers (kebab_case, discover_next_id, find_task_file, extract_section, build_meta_content, git_mv_or_fallback, patch_archived_file) are duplicated inside the MCP tool function. Other projects that vendor this HQ's MCP servers (without copying `scripts/`) can bundle via the Hands:

```json
{
  "tool": "bundle_tasks",
  "arguments": {
    "task_ids": ["12", "15", "20"],
    "title": "android-polish-bundle",
    "dry_run": true,
    "force": false
  }
}
```

**Tool name:** `bundle_tasks` on `mcp-context-server` (`custom_context` FastMCP server). It validates IDs, resolves `scripts/bundle-tasks.py` against the workspace root (path-traversal safe), runs it via `uv run` (or `python3` fallback), and returns the stdout/stderr. Dry-run prints preview without file creation. The MCP wrapper is thin — it reuses the script's logic for DRY.

**When to choose B:** You are in a project that was bootstrapped from this HQ but only has the MCP servers (e.g., `mcp-context-server`, `mcp-lint-server`, `mcp-memory-server`) and the Hands' MCP tool list — not a shell. Use `bundle_tasks` directly. If you have shell, prefer A (faster, same result).

## What Happens (Deterministic Steps)

1. **Validate IDs:** Search `tasks/backlog/ tasks/in-progress/ tasks/qa/ tasks/completed/` (active only, `tasks/archive/` excluded per `task-generator` duplicate-ID contract) for each `<id>-*.md`. HALT if any missing; note if found in archive (already superseded). Reject non-numeric IDs.
2. **Discover NEXT_ID:** `find tasks -type f -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}'` across **ALL** dirs including `archive` (no collision). Zero-padded `02d` for <100, raw for ≥100.
3. **Slugify Title:** `title` → kebab-case (`android Polish_Bundle` → `android-polish-bundle`). Output file: `tasks/backlog/<NEXT_ID>-<slug>.md`.
4. **Verbatim Extraction:** For each source, extract `## Goal`, `## Manager's Notes`/`## Blueprint Reference`, `## Acceptance Criteria`, `## Local TODOs`, `## Risk & Rollback` verbatim via regex `^## Heading$(.*?)(?=^## |\n---\s*\n|\Z)`. No summarization.
5. **Generate META File:** Canonical task template + `**Supersedes:** [12, 15, 20]` + `**Meta:** true` + `**Created:**` + per-source appendix `### Source Task XX: Title` + `## Source Bundles (Verbatim Preservation)` + `## Bundled Checklist (All-or-Nothing)` (every source AC line prefixed `[XX]`, single QA gate) + aggregated `## Local TODOs` (`[XX]`-prefixed) + guardrail notes (LOC warning if >400).
6. **Auto-Archive (unless dry_run):** `git mv <src> tasks/archive/<src>` (fallback to `mv` + `git add` for untracked) then patch archived file: `**File:**` → `tasks/archive/<file>`, `**Status:** superseded`, add `**Superseded-By:** <META_ID>-<slug>` + `**Superseded-At:** YYYY-MM-DD`, inject superseded footer before `## Execution Log`. History remains reachable: `git log --oneline --follow -- tasks/archive/<file>` — **never** `git rm` until META is `completed`.
7. **Kanban:** META follows normal `tasks/backlog/<META>` → `tasks/in-progress/<META>` → `tasks/qa/<META>` → `tasks/completed/<META>` with one injected `Factual Git Diff`. QA is all-or-nothing.

## Guardrails (Hard Stops & Warnings)

- **Cap:** `MAX_BUNDLE_SIZE=6` — rejects >6 without `--force` (mega-diff prevention). Use `--force` to override.
- **Diff-size:** Warns if combined source LOC >400 (`> ⚠️ 400` in notes) — "consider split".
- **Missing / Duplicate / Collision:** Missing IDs → `❌ Missing tasks`; duplicate active IDs → **hard halt** (returns None, exits with error); `NEXT_ID` collision → atomic creation with retry loop (up to 5 re-discoveries).
- **Stack Conflict (M1):** Auto-detects stack from content (android, react, fastapi, spring, ios, go). If tasks have conflicting stacks → requires `--force` to proceed.
- **Verbatim Checksum (M2):** After META generation, verifies every AC line from source tasks appears in the META. Fails if any text was dropped.
- **Archive-only:** Sources go to `tasks/archive/` via `git mv` only. Purge (`git rm`) is blocked until META is `completed`. On ANY archive failure: **transactional rollback** restores all archived files to original locations, deletes META, exits with clear error.
- **Unicode/Persian Slugs (B4):** `_kebab_case()` normalizes via NFKD and preserves Persian/Arabic characters (\u0600-\u06FF). Persian titles produce valid slugs like `تست-باندل` instead of losing all characters.

## Verification (Must Pass Before QA)

```bash
uv run scripts/bundle-tasks.py 12 15 20 --title "test-bundle" --dry-run
# or via MCP: bundle_tasks(task_ids=["12","15","20"], title="test-bundle", dry_run=true)

# then after real bundle (if not dry_run):
lint_task_file tasks/backlog/<NEXT_ID>-<slug>.md
lint_task_file tasks/archive/12-*.md
git log --oneline --follow -- tasks/archive/12-*.md | head
py_compile: python3 -m py_compile scripts/bundle-tasks.py mcp-context-server/server.py
```

- META must contain `**Supersedes:**` + every source `### Source Task` block + `## Bundled Checklist` with `[XX]` prefixes.
- `lint_task_file` must pass on META (fixed `---` → `---\n\n` blank-line; `**Type:**` allows `feature` + `Meta:true` and also `meta`) and on both archived files (`**Status:** superseded` is allowed; `**File:**` matches archive path).
- `git log --follow` must show the source's history through the rename.

## Skill Loading

Load this skill when you handle bundling:

```bash
skill("bundle-tasks")
```

If you also need ID discovery or template generation, also load `task-generator` (this skill complements it, not replaces it). For lint, load `task-lint`; for context gathering before bundling, load `code-search` to ensure sources are in the expected Kanban dirs.

## Rollback

If META is abandoned or fails QA permanently:

```bash
git mv tasks/archive/12-*.md tasks/backlog/12-*.md
git mv tasks/archive/15-*.md tasks/backlog/15-*.md
rm tasks/backlog/<NEXT_ID>-<slug>.md        # or: git mv tasks/backlog/<NEXT_ID>-<slug>.md tasks/archive/<NEXT_ID>-<slug>.md # mark abandoned
```

No HQ code beyond the bundler is affected. If META already reached `tasks/completed/`, its archived sources stay in `tasks/archive/` permanently (they are superseded, not purged).

## Reference

- **Script:** `scripts/bundle-tasks.py` (694 lines, `py_compile` clean, handles untracked `git mv` fallback, `---\n\n` fix, cap 6)
- **MCP:** `mcp-context-server/server.py:bundle_tasks` (thin `uv run` wrapper, path-traversal safe, 30s timeout, `task_ids: list[str], title: str, dry_run, force`)
- **Docs:** `AGENTS.md` `## 🛑 META-TASK BUNDLE LIFECYCLE` + `**Bundle Script:**`, `CHANGELOG.md` `[Unreleased]`
- **Lint:** `mcp-lint-server/server.py` Type regex now `...|meta`
- **Registry:** `prompts/fragments/10-agent_skills_registry.md` lists `bundle-tasks`
