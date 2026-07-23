# Task: Refactor Global Auto-Installation Workflow

**File:** `tasks/completed/62-refactor-global-auto-installation.md`
**Type:** improvement
**Status:** closed

## Goal

Refactor `LLM.txt` to execute a standalone, global auto-installation that clones the repo to `/tmp/`, copies MCP servers and skills globally, configures `opencode.json` with absolute paths, and cleans up. Also simplify `README.md` Quick Start to a single copy-paste `webfetch` prompt. Update `CHANGELOG.md`.

## Manager's Notes

- LLM.txt must be self-contained — clone repo, install globally, remove clone.
- README Quick Start should instruct OpenCode to use `webfetch` on `https://raw.githubusercontent.com/mokhtarabadi/cognitive-lead-hq/main/LLM.txt`.
- CHANGELOG.md must follow Keep a Changelog format.

## Local TODOs

- [x] **Step 1:** Create `tasks/backlog/62-refactor-global-auto-installation.md` with goal, notes, local TODOs, execution log placeholder, and git diff markers.
- [x] **Step 2:** Refactor `LLM.txt` to execute a standalone, global auto-installation:
    - Add step to check for `git` and `uv`. If `uv` is missing, prompt user for confirmation and run `curl -LsSf https://astral.sh/uv/install.sh | sh`.
    - Add step to clone `https://github.com/mokhtarabadi/cognitive-lead-hq.git` to `/tmp/cognitive-lead-hq`.
    - Add step to discover `$HOME` absolute path.
    - Add step to create global directories (`~/.config/opencode/mcp-context-server/`, `~/.config/opencode/mcp-memory-server/`, `~/.config/opencode/skills/`).
    - Add step to copy server scripts (`mcp-context-server/server.py` and `mcp-memory-server/server.py`) and make them executable.
    - Add step to copy all skills from `skill-templates/*` into `~/.config/opencode/skills/`.
    - Add step to create or update `~/.config/opencode/opencode.json` using absolute paths for `uv run /ABSOLUTE_PATH/...`.
    - Add step to remove `/tmp/cognitive-lead-hq`.
    - Update verification checklist and agent prompt at the bottom of `LLM.txt`.
- [x] **Step 3:** Refactor `README.md` Quick Start section to give a single, direct copy-paste prompt instructing OpenCode to use `webfetch` on `https://raw.githubusercontent.com/mokhtarabadi/cognitive-lead-hq/main/LLM.txt`.
- [x] **Step 4:** Update `CHANGELOG.md` with a new entry logging the global installer overhaul.
- [x] **Step 5:** Move task to `tasks/in-progress/`, write execution log, stage and inject diff.

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

The prior `LLM.txt` assumed the user had already cloned the repo and was running from within it. This created a dependency on the current working directory, making true global installation unreliable. The refactored approach:

1. **Self-contained clone** — The AI clones the repo to `/tmp/cognitive-lead-hq` as the first step, so all subsequent file copies use deterministic absolute paths independent of the user's `cwd`.
2. **`git` prerequisite** — Added alongside `uv` since cloning is now the entry point.
3. **Temporary cleanup** — Step 8 removes the `/tmp/` clone, leaving no trace.
4. **README simplification** — The Quick Start now uses `webfetch` on the raw GitHub URL, which works regardless of whether the user has cloned the repo.
5. **CHANGELOG** — Logged under `[Unreleased]` with `### Changed` category per Keep a Changelog conventions.

### Files Modified

- `LLM.txt` — Full rewrite: standalone clone-based global installer (10 steps)
- `README.md` — Quick Start section simplified to single `webfetch` prompt
- `CHANGELOG.md` — Added `[Unreleased]` entry for global installer overhaul
- `tasks/backlog/62-refactor-global-auto-installation.md` → `tasks/in-progress/` (promoted)

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `556d3318789a137d4be97ac6ec9c5d469b1cef83`
<!-- END_GIT_DIFF -->
