# Task 120: Install opentmux and Update Project Docs

**File:** `tasks/in-progress/120-install-opentmux-and-update-docs.md`
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

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
