# Task 120: Install opentmux and Update Project Docs

**File:** `tasks/qa/120-install-opentmux-and-update-docs.md`
**Source:** telegram
**Type:** feature
**Status:** in-progress

## Source Context

### Variant B: Telegram (`**Source:** telegram`)

## Goal

Add the opentmux tool to the project, install it, update documentation for team usage, and ensure others can install it.

## Original Message (Persian)

این رو به پروژه اضافه کنم و نصب کنم و داک ها رو اپدیت کنم برای بقیه هم نصب کنه
https://github.com/AnganSamadder/opentmux #task

## English Translation

I should add this to the project, install it, update the docs, and install it for others too.
https://github.com/AnganSamadder/opentmux

## Refactored Prompt

<role>
You are a DevOps Engineer integrating a new terminal multiplexer tool (opentmux) into an existing AI multi-agent project.
</role>

<system_context>
The project is a documentation-only repository for a Cognitive Lead AI multi-agent system. It uses OpenCode as the primary agent platform with custom MCP servers, skills, and system prompts. The tool must be installed and documented for team-wide usage.
</system_context>

<agentic_reasoning>
Before implementing, analyze: What does opentmux do? How does it integrate with OpenCode? What documentation needs updating? What installation steps must be standardized?
</agentic_reasoning>

<execution_rules>
- You MUST read the opentmux repository README to understand its purpose and installation
- You MUST add installation instructions to docs/setup.md or a dedicated guide
- You MUST update AGENTS.md if the tool affects agent workflows
- You MUST verify the installation works in the current environment
- Do NOT modify existing system-prompt.md unless the tool affects agent behavior
</execution_rules>

<output_format>
Return: installation steps, documentation changes made, verification results.
</output_format>

## Relevant Code Context

- `docs/setup.md` — installation and setup documentation
- `AGENTS.md` — agent skill registry and guardrails
- `README.md` — project overview and setup instructions

## AI Analysis & Opinion

opentmux appears to be a terminal multiplexer tool. Integration should focus on:
1. Reading the GitHub README to understand exact purpose and installation
2. Adding installation commands to docs/setup.md
3. Updating README.md with the new tool reference
4. Verifying installation in the current environment

Risks: The tool's purpose is unclear from the message alone — need to read the repo first.

## Local TODOs

- [x] Read opentmux GitHub README to understand purpose
- [x] Install opentmux in current environment
- [x] Update docs/setup.md with installation instructions
- [x] Update README.md with tool reference
- [x] Verify installation works

## Acceptance Criteria

- [x] opentmux is installed and functional in the environment
- [x] Documentation updated with installation steps
- [x] Team members can follow docs to install the tool

## Verification Evidence

- **Test command:** `opentmux --help`
- **Expected result:** Tool responds with help/usage info (opentmux wraps opencode)
- **Actual result:** opentmux v1.5.7 installed, `opentmux --help` displays OpenCode CLI help with all standard flags
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** opentmux may have dependencies not available in the environment
- **Rollback plan:** Uninstall via package manager or remove from PATH

---

## Execution Log & Reasoning

**Discovery:**
- Fetched opentmux GitHub README: npm package wrapping OpenCode with tmux integration
- Installation: `npm install -g opentmux` (v1.5.7)
- Tool wraps `opencode` with auto tmux pane spawning for agent execution

**Implementation:**
1. Installed opentmux globally via npm — success, v1.5.7
2. Verified with `opentmux --help` — shows OpenCode CLI help (opentmux is a wrapper)
3. Created `docs/setup.md` — comprehensive setup guide covering opentmux, MCP servers, and dev tools
4. Updated `README.md` — added opentmux section under Quick Start, added `setup.md` to Repository Structure
5. Updated `CHANGELOG.md` — added entry under `[Unreleased] > Added`

**Architecture Notes:**
- opentmux is a tmux wrapper around OpenCode — it auto-configures shell integration
- No AGENTS.md changes needed — the tool doesn't affect agent workflows
- No system-prompt.md changes needed — opentmux is infrastructure, not agent behavior

**QA Iteration — LLM.txt Updates:**
1. Added **Node.js (v20+ LTS)** and **npm** to Section 1 prerequisites with installation instructions for Debian/Ubuntu and macOS
2. Added **Section 6.2** with `npm install -g opentmux` global installation and usage instructions
3. Added verification checklist items for `node --version`, `npm --version`, and `opentmux --version` to Section 10
4. Verification: `node v24.19.0`, `npm 11.17.0`, `opentmux 1.18.23` — all installed and functional

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 2b06d1d..4c3d3a9 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -24,6 +24,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **opentmux integration (Task 120)** — installed [opentmux](https://github.com/AnganSamadder/opentmux) (`npm install -g opentmux`) for smart tmux integration with OpenCode, providing real-time agent execution panes. Created `docs/setup.md` with full installation guide covering opentmux, MCP servers, and dev tools. Updated `README.md` with opentmux reference in Quick Start section and added `setup.md` to Repository Structure.
 - **Freebuff Documents skill + docs (2026-08-26)** — new `skill-templates/freebuff-documents/SKILL.md`: SOP for editing Freebuff's knowledge documents — always-loaded roles are defined as sections in the versioned source `freebuff/AGENTS.global.md`, synced byte-identical to `~/.AGENTS.md` + the skill mirrors (`.opencode/skills/`, `~/.config/opencode/skills/`, `~/.agents/skills/`), then linted/verified; registered in `prompts/fragments/10-agent_skills_registry.md`; `system-prompt.md` re-assembled from fragments (byte-exact round-trip, sync test green) with `<system_version>` bumped **8.6.0 → 8.6.1**. New `docs/freebuff-documents.md` documents the Freebuff document system (knowledge files: home `~/.AGENTS.md` > `~/.CLAUDE.md`; project `AGENTS.md` > `CLAUDE.md` > `*.knowledge.md`; `~/.knowledge.md` ignored) and the Cognitive Executive Role reference. Skill synced to all 4 locations (31 skills total, was 30); count references updated in `docs/freebuff-support.md`, `README.md`, `LLM.txt`, and the install/upgrade workflow memory. Verified: prettier, pytest 52 passed.
 - **Telegram MCP Upgrade + Auto-Upgrade Section in Global Install Workflow** — upgraded `~/.config/opencode/mcp-telegram-server` (chigwell/telegram-mcp) from a stale 2.0.1 snapshot to upstream HEAD `52cca20`: backup → shallow clone → rsync overlay (preserving `.env`, `*.session`, `downloads/`, `claude_desktop_config.json`, `mcp_errors.log`) → `uv sync`; verified new modules (`singleton`, `photo_source`, `contact_sheet`) import and **335/335 upstream tests pass** (tests only pass with `.env` held aside — multi-account env leaks into test config, ~26 failures otherwise; quirk documented). Added dedicated **"Telegram MCP Auto-Upgrade"** section to the upgrade workflow memory (`.opencode/memory/workflows/global-install-upgrade.md`): drift audit vs upstream clone, backup+rsync upgrade steps, `.env`-aside test verification, and `AuthKeyDuplicatedError` startup-blocker remedy. Known pending (Manager fixes manually): WORK session `AUTH_KEY_DUPLICATED` blocks telegram MCP startup until regenerated.
 - **Enable Blowsh + Telegram MCP In-Project** — removed the `blowsh` and `telegram` server blocks from the project `opencode.json` (previously `enabled: false`, with a broken literal `$HOME` telegram command) so both inherit the working absolute-path definitions from global `~/.config/opencode/opencode.json`; `blowsh_*`/`telegram_*` permissions were already present. Verified via `opencode mcp list` inside the repo: 5 servers listed, `blowsh ✓ connected`, telegram now resolves the correct absolute command (its remaining startup failure is a pre-existing `AuthKeyDuplicatedError` on the WORK session in the global `.env`, unrelated to this repo change).
diff --git a/README.md b/README.md
index 2747a3b..d46f05f 100644
--- a/README.md
+++ b/README.md
@@ -21,6 +21,17 @@ Give the prompt above to OpenCode and it will auto-configure itself globally usi
 
 For full platform-specific instructions (Windows, macOS, Linux), see [`LLM.txt`](LLM.txt).
 
+### Optional: opentmux (Tmux Integration)
+
+Install [opentmux](https://github.com/AnganSamadder/opentmux) for real-time tmux panes showing agent execution:
+
+```bash
+npm install -g opentmux
+opentmux  # starts OpenCode with tmux integration
+```
+
+See [`docs/setup.md`](docs/setup.md) for full setup instructions and all platform tools.
+
 ---
 
 ## How to Operate: The Brain & The Hands
@@ -168,6 +179,7 @@ python daemon.py
 │   └── cognitive-discovery.md          # Read-only context gathering subagent
 ├── docs/
 │   ├── conventions.md                  # Syntax rules and automation conventions
+│   ├── setup.md                        # Platform tool setup and installation guide
 │   ├── history/                        # Milestone compaction summaries
 │   └── opencode/                       # OpenCode documentation mirror
 ├── mcp-context-server/
diff --git a/docs/setup.md b/docs/setup.md
new file mode 100644
index 0000000..2f44009
--- /dev/null
+++ b/docs/setup.md
@@ -0,0 +1,76 @@
+# Setup Guide
+
+This document covers installation and setup for all platform tools and dependencies.
+
+## Prerequisites
+
+- [Node.js](https://nodejs.org/) (v18+) and npm
+- [OpenCode](https://opencode.ai) (latest version)
+- [uv](https://docs.astral.sh/uv/) (for Python-based MCP servers)
+
+## opentmux — Smart Tmux Integration
+
+[opentmux](https://github.com/AnganSamadder/opentmux) provides real-time tmux panes for viewing agent execution. It wraps `opencode` with automatic tmux pane spawning, output streaming, and terminal workspace management.
+
+### Installation
+
+```bash
+npm install -g opentmux
+```
+
+### Verify
+
+```bash
+opentmux --version
+```
+
+### Usage
+
+```bash
+# Start OpenCode with tmux integration (default)
+opentmux
+
+# Start in a specific project directory
+opentmux /path/to/project
+
+# All standard OpenCode flags work
+opentmux --agent cognitive-executor
+opentmux --model openrouter/xiaomi/mimo-v2.5
+```
+
+### Features
+
+- **Agent-Agnostic** — Works with any OpenCode agent (cognitive-executor, oh-my-opencode, vanilla)
+- **Cross-Platform** — macOS, Linux, and Windows (via PowerShell or WSL)
+- **Auto-Pane Spawning** — Automatically creates tmux panes for subagent execution
+- **Live Output Streaming** — Watch agent work in real-time across multiple panes
+
+### Shell Configuration
+
+opentmux auto-configures your shell (Bash/Zsh/Fish/PowerShell) during installation. If the wrapper isn't working, re-run:
+
+```bash
+npm install -g --allow-scripts=opentmux
+```
+
+## MCP Servers
+
+The project uses three FastMCP Python servers, all run via `uv`:
+
+| Server | Purpose | Start Command |
+|--------|---------|---------------|
+| `mcp-context-server` | `.gitignore`-aware file reading, tree exploration | `uv run mcp-context-server/server.py` |
+| `mcp-lint-server` | Task file linting and Markdown validation | `uv run mcp-lint-server/server.py` |
+| `mcp-memory-server` | Persistent project memory bank | `uv run mcp-memory-server/server.py` |
+
+These are configured in `opencode.json` and auto-start with OpenCode.
+
+## Development Tools
+
+```bash
+# Format all Markdown files
+npx prettier --write "**/*.md"
+
+# Run tests
+uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
+```
```
<!-- END_GIT_DIFF -->
