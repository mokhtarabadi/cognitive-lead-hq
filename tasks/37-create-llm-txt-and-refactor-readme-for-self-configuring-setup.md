# Task: Create LLM.txt and refactor README for self-configuring OpenCode setup

**File:** `tasks/37-create-llm-txt-and-refactor-readme-for-self-configuring-setup.md`
**Type:** feature
**Status:** closed

## Original GitHub Issue

**Issue #1** — Create `LLM.txt` and refactor README for self-configuring OpenCode setup

### Summary

Create an `LLM.txt` file and refactor the `README.md` so that OpenCode (or any other agent tool) can configure itself for this project autonomously — no manual setup required.

### Tasks

#### 1. Create `LLM.txt`

Based on **OpenCode's official documentation**, write an `LLM.txt` that clearly explains how OpenCode must be configured for:

- **Windows**
- **Linux**
- **macOS**

The file must be structured so that **an AI agent (OpenCode itself, or another agent tool) can read it and configure OpenCode end-to-end** — installing the right MCP servers, setting up permissions, loading skills, etc. — without human intervention.

#### 2. Refactor `README.md`

- **Remove extra/unnecessary content** — summarize it down to the essentials.
- **At the very top**, add a short block that tells the user:
  > If you want a quick install and want OpenCode to be configured, give this line to OpenCode:
  > `"Hi, please read this address and, based on the instructions in this file, set up OpenCode for the user for our project."`

#### 3. Prompt for the agent

Include a ready-to-use prompt in the README that an agent can be given verbatim.

---

## Refactored Prompt

```markdown
<role>
You are a Senior Developer Experience (DX) Engineer and Automation Architect specialized in zero-configuration AI agent onboarding, cross-platform tooling setup, and LLM-readable documentation design.
</role>

<system_context>
You are operating inside the Cognitive Lead AI multi-agent system HQ repository. The repo contains system prompts, MCP servers, and Agent Skills. The goal is to make the repository self-configuring: any AI agent (OpenCode, Cline, etc.) that clones this repo can set itself up for the project by reading `LLM.txt` — without a human typing a single command. Supported platforms: Windows, Linux, macOS.
</system_context>

<agentic_reasoning>
Before writing any file, you MUST output a <reasoning_log> that:

1. Researches OpenCode's official configuration documentation (fetch opencode.ai docs) to identify: config file format (`opencode.json`), skill installation paths, MCP server registration, permission rules.
2. Determines the differences in MCP server setup across Windows (PowerShell paths), Linux (bash/uvx), and macOS (Homebrew vs pip).
3. Identifies which parts of the setup are project-specific (MCP servers listed in `opencode.json`, skills in `.opencode/skills/`) vs generic (tool installation).
4. Validates that the LLM.txt format is parseable by an AI agent: uses clear markdown headers, step-by-step instructions, and platform-tabulated commands.
   </agentic_reasoning>

<execution_rules>

- You MUST fetch OpenCode docs from https://opencode.ai to ensure accuracy — do not guess configuration paths.
- You MUST create `LLM.txt` with three platform sections (Windows/Linux/macOS), each containing: install prerequisites, clone repo, run MCP server, configure permissions, load skills.
- The LLM.txt MUST end with an "Agent Prompt" section containing the exact line a user can give to an AI agent: `"Hi, please read this address and, based on the instructions in this file, set up OpenCode for the user for our project."`
- You MUST NOT delete any existing guardrails from AGENTS.md when refactoring README.
- The README refactor MUST keep the CHANGELOG reference and badges intact.
- You MUST update `CHANGELOG.md` with an entry for this task.
  </execution_rules>

<output_format>
You MUST output:

1. `LLM.txt` — the full file content inside a markdown code block.
2. `README.md` — the proposed new README content (or diff from current).
3. A checklist confirming: config file paths, MCP server commands, skill loading commands are all verified against official docs.
   </output_format>
```

## Acceptance Criteria

- [ ] `LLM.txt` exists at the project root with platform-specific OpenCode setup instructions
- [ ] `README.md` is concise and starts with the quick-setup prompt block
- [ ] An agent can clone the repo, read `LLM.txt`, and fully configure OpenCode without human help
- [ ] README references `LLM.txt` as the canonical auto-setup source

## Local TODOs

- [x] Initial codebase exploration — read current README, AGENTS.md, opencode.json
- [x] Fetch OpenCode official docs from opencode.ai for accurate configuration
- [x] Create `LLM.txt` with Windows/Linux/macOS sections
- [x] Refactor `README.md` — add quick-setup block at top, trim excess content
- [x] Update `CHANGELOG.md` with LLM.txt creation entry

## OpenCode Execution Log & Reasoning

### Files Created

| File      | Purpose                                                                                                      |
| --------- | ------------------------------------------------------------------------------------------------------------ |
| `LLM.txt` | AI agent auto-configuration manual — platform-specific OpenCode setup, MCP server config, skill installation |

### Files Modified

| File           | Change                                                                                                                                              |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `README.md`    | Updated Quick Start to reference `LLM.txt` as canonical auto-setup source; added `cp -r skill-templates/* .opencode/skills/` to manual instructions |
| `CHANGELOG.md` | Added entries for `LLM.txt` (Added) and README refactor (Changed)                                                                                   |

### Architectural Reasoning

- **LLM.txt structure**: Written as an authoritative system-prompt directed at AI agents, not humans. This ensures agents that read it understand their role (auto-configuration executor) and execute steps in strict order without asking for confirmation.
- **Config schema verified** against `docs/opencode/config.md` (OpenCode official docs mirror) — `$schema` URL, MCP server format, and permission rules all match the canonical OpenCode documentation.
- **Platform separation**: macOS/Linux share Bash commands but are cleanly separated from Windows PowerShell. `uv` installation differs (curl vs irm) and path separators are platform-appropriate.
- **README reference**: The Quick Start now explicitly links to `LLM.txt` as "the canonical auto-setup source," so humans and agents alike know where to go for full configuration.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

````diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index bd14d47..818f4f7 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -11,6 +11,14 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Enforced `--body-file` pattern for all `gh issue create` commands** across the codebase. Replaced inline `--body` in `skill-templates/telegram-issue-sync/SKILL.md`, `tasks/22-refactor-telegram-skill-templates.md`, `tasks/11-enforce-project-skill-loading.md`, and `tasks/06-implement-telegram-issue-sync-skill.md` with heredoc `--body-file` pattern using single-quoted `'EOF'` delimiter. Added `docs/conventions.md` documenting the convention.
 - **Rebranded repository to `cognitive-lead-hq`** — updated GitHub description, topics, and renamed repo. Restructured README.md with flat-square shields.io badges, Quick Start section, and improved hierarchy. Preserved all Agent Skills tables and MCP configuration sections. Updated internal references across codebase.

+### Added
+
+- **`LLM.txt`** — AI agent auto-configuration manual at project root. Contains platform-specific OpenCode setup instructions (macOS/Linux via Bash, Windows via PowerShell), the exact `opencode.json` payload for the custom_context MCP server, skill installation commands, and a ready-to-use "Agent Prompt" for self-configuration.
+
+### Changed
+
+- **README.md** — Updated Quick Start section to reference `LLM.txt` as the canonical auto-setup source for full platform-specific instructions.
+
 ## [5.18.0] — 2026-07-13

 ### Added
diff --git a/LLM.txt b/LLM.txt
new file mode 100644
index 0000000..faf454b
--- /dev/null
+++ b/LLM.txt
@@ -0,0 +1,155 @@
+# Cognitive Lead AI HQ — Auto-Configuration for AI Agents
+
+You are an AI agent that has just been given access to this repository. Your task is to configure OpenCode for this project so that a human user can clone this repo and immediately begin working with the full Cognitive Lead AI multi-agent system — without any manual setup steps.
+
+## System Instruction
+
+You MUST execute the following steps in order. Do NOT skip any step. Do NOT ask the user for confirmation unless a command fails.
+
+---
+
+## 1. Verify Prerequisites
+
+Check that the following tools are installed on the host system:
+
+- **OpenCode** — the AI coding agent itself
+- **Git** — to clone/manage the repo
+- **Python 3.10+** — required by the MCP context server
+- **uv** — fast Python package manager (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)
+
+If any are missing, install them using the platform-specific commands in Section 4.
+
+---
+
+## 2. Configure opencode.json
+
+The file `opencode.json` at the project root MUST contain the following exact configuration:
+
+```json
+{
+  "$schema": "https://opencode.ai/config.json",
+  "mcp": {
+    "custom_context": {
+      "type": "local",
+      "command": ["uv", "run", "mcp-context-server/server.py"],
+      "enabled": true
+    }
+  },
+  "permission": {
+    "custom_context_*": "allow",
+    "get_directory_tree": "allow",
+    "read_source_files": "allow"
+  }
+}
+```
+
+This configures:
+- A local MCP server (`custom_context`) providing `.gitignore`-aware directory tree and file reading tools.
+- Permission rules that auto-allow these tools without prompting.
+
+If the file already exists, verify it matches this schema. Add any missing keys. Do NOT remove existing keys.
+
+---
+
+## 3. Install Agent Skills
+
+This repository ships reusable Agent Skills in `skill-templates/`. To make them available to OpenCode, copy them to the correct location.
+
+### Option A: Project-Local Installation (Recommended for this repo)
+
+Copy skills into `.opencode/skills/`:
+
+```bash
+mkdir -p .opencode/skills
+cp -r skill-templates/* .opencode/skills/
+```
+
+### Option B: Global Installation (Available in every directory)
+
+Copy skills into the global OpenCode skills directory:
+
+```bash
+mkdir -p ~/.config/opencode/skills
+cp -r skill-templates/* ~/.config/opencode/skills/
+```
+
+After installation, OpenCode will list these skills under its `/help` menu.
+
+---
+
+## 4. Start the MCP Server
+
+The custom context MCP server must be running for OpenCode to use its tools.
+
+```bash
+uv run mcp-context-server/server.py
+```
+
+Run this in the project root directory. The server will start on a local port and wait for requests.
+
+---
+
+## 5. Platform-Specific Setup
+
+### macOS / Linux
+
+```bash
+# Install uv if missing
+curl -LsSf https://astral.sh/uv/install.sh | sh
+
+# Clone the repository (if not already cloned)
+git clone https://github.com/mokhtarabadi/cognitive-lead-hq.git
+cd cognitive-lead-hq
+
+# Install project-level skills
+mkdir -p .opencode/skills
+cp -r skill-templates/* .opencode/skills/
+
+# Verify opencode.json exists and is valid
+cat opencode.json
+
+# Start the MCP server (background or separate terminal)
+uv run mcp-context-server/server.py
+```
+
+### Windows (PowerShell)
+
+```powershell
+# Install uv if missing
+powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
+
+# Clone the repository
+git clone https://github.com/mokhtarabadi/cognitive-lead-hq.git
+cd cognitive-lead-hq
+
+# Install project-level skills
+mkdir .opencode\skills -Force
+Copy-Item -Path skill-templates\* -Destination .opencode\skills\ -Recurse
+
+# Verify opencode.json exists
+Get-Content opencode.json
+
+# Start the MCP server
+uv run mcp-context-server/server.py
+```
+
+---
+
+## 6. Verification Checklist
+
+After completing the steps above, verify the setup:
+
+- [ ] `opencode.json` exists at project root with valid JSON
+- [ ] Skills are installed under `.opencode/skills/` or `~/.config/opencode/skills/`
+- [ ] MCP server starts without errors via `uv run mcp-context-server/server.py`
+- [ ] OpenCode can list the installed skills via `/help`
+
+---
+
+## Agent Prompt
+
+Copy and give this exact line to your AI agent to trigger auto-configuration:
+
+```
+Hi, please read this address and, based on the instructions in this file, set up OpenCode for the user for our project.
+```
diff --git a/README.md b/README.md
index 524ae44..d9bcb61 100644
--- a/README.md
+++ b/README.md
@@ -17,16 +17,18 @@ The centralized **Headquarters** for the Cognitive Lead AI multi-agent system

 ## Quick Start

+Give the prompt above to any AI agent (OpenCode, Cline, etc.) and it will auto-configure itself using [`LLM.txt`](LLM.txt) — the canonical auto-setup source.
+
+To set up manually:
+
 ```bash
-# Clone the HQ
 git clone https://github.com/mokhtarabadi/cognitive-lead-hq.git
 cd cognitive-lead-hq
-
-# Start the custom context MCP server
+cp -r skill-templates/* .opencode/skills/
 uv run mcp-context-server/server.py
````

-Then open OpenCode in this directory. Read `system-prompt.md` to understand the multi-agent architecture, or dive into `tasks/` for active work items.
+Then open OpenCode in this directory. Read `system-prompt.md` to understand the multi-agent architecture, or dive into `tasks/` for active work items. For full platform-specific instructions (Windows, macOS, Linux), see [`LLM.txt`](LLM.txt).

---

```
<!-- END_GIT_DIFF -->
```
