# Task: Global Auto-Setup — README Quick Install + LLM.txt Global Installation

**File:** `tasks/backlog/61-global-auto-setup-readme-llm-txt.md`
**Type:** improvement
**Status:** closed

## Goal

Fix three issues with the auto-setup flow:

1. **README Quick Install** — The quick install section forgot to include a direct reference to `LLM.txt`. Fix so users can copy a single complete instruction.
2. **LLM.txt Global Installation** — Rewrite `LLM.txt` to install OpenCode configuration **globally** (`~/.config/opencode/`) instead of project-locally (`./opencode/`). This includes both MCP servers and skills.
3. **MCP Server Global Setup** — LLM.txt must: check for `uv` (install if missing after confirmation), copy both MCP server scripts to `~/.config/opencode/mcp-*-server/`, and configure `~/.config/opencode/opencode.json` with **absolute paths** to the server scripts.

## Manager's Notes

- README lines 10-14: quick install box needs direct LLM.txt link
- LLM.txt needs major rewrite: global paths, uv installation logic, both MCP servers, absolute path resolution
- No changes needed to project-local `opencode.json` — it stays as-is for project-local overrides

## Local TODOs

- [x] Fix README quick install section
- [x] Rewrite LLM.txt with global installation flow
- [x] Update CHANGELOG.md
- [x] Run prettier and verify
- [x] Stage, commit, push, close

## OpenCode Execution Log & Reasoning

### Architecture & Reasoning

**Problem:** The auto-setup flow had three gaps:
1. README's quick install prompt didn't mention `LLM.txt` by name — AI agents wouldn't know which file to read.
2. `LLM.txt` installed everything project-locally (`.opencode/skills/`), but the user needed global installation.
3. `LLM.txt` only configured the `custom_context` MCP server, not `project_memory`. And both needed absolute paths in the global config.

**Changes:**

1. **README.md** (lines 10-14): Changed the quick install prompt from vague "read this address" to explicit "read the LLM.txt file in this project".

2. **LLM.txt** (full rewrite):
   - **Step 1:** Prerequisites — now includes uv installation logic with user confirmation.
   - **Step 2:** Home directory discovery — instructs AI to resolve `$HOME` for absolute paths.
   - **Step 3:** Global directories — creates `~/.config/opencode/mcp-*-server/` and copies both server scripts.
   - **Step 4:** Global `opencode.json` — configures BOTH `custom_context` AND `project_memory` MCP servers with absolute paths (critical for global config where working directory varies).
   - **Step 5:** Global skills — copies `skill-templates/*` to `~/.config/opencode/skills/`.
   - **Step 7:** Verification — checks both servers launch correctly.

3. **CHANGELOG.md** — Added `[6.10.0]` entry documenting the changes.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `e4f7a27df7d3a98050b0bddf35466f89770b76d4`
<!-- END_GIT_DIFF -->
