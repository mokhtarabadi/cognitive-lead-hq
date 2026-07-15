# Task: Create LLM.txt and refactor README for self-configuring OpenCode setup

**File:** `tasks/37-create-llm-txt-and-refactor-readme-for-self-configuring-setup.md`
**Type:** feature
**Status:** open

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

- [ ] Initial codebase exploration — read current README, AGENTS.md, opencode.json
- [ ] Fetch OpenCode official docs from opencode.ai for accurate configuration
- [ ] Create `LLM.txt` with Windows/Linux/macOS sections
- [ ] Refactor `README.md` — add quick-setup block at top, trim excess content
- [ ] Update `CHANGELOG.md` with LLM.txt creation entry

## OpenCode Execution Log & Reasoning

_(OpenCode: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
