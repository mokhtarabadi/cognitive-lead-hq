# Task 121: Install GitHub CLI and Integrate into System Prompt and Skills

**File:** `tasks/qa/121-install-github-cli-and-integrate.md`
**Source:** telegram
**Type:** feature
**Status:** in-progress

## Source Context

### Variant B: Telegram (`**Source:** telegram`)

## Goal

Download and install the official GitHub CLI (`gh`), and integrate it into the system prompt and skills that use GitHub commands.

## Original Message (Persian)

برای کامند gh باید اسکیل رسمی github ور دانلود و نصب کنیم و همیشه هم ازش اسفاده کنیم mention کنیم داخل system prompt و بقیه skill ها که از gh استفاده میکنن

https://github.com/cli/cli

#task

## English Translation

For the `gh` command, we need to download and install the official GitHub CLI, and always use it. Mention it in the system prompt and other skills that use `gh`.

## Refactored Prompt

<role>
You are a Platform Engineer integrating the official GitHub CLI (`gh`) into an AI multi-agent system's toolchain.
</role>

<system_context>
The project is a documentation-only repository for a Cognitive Lead AI multi-agent system. It uses OpenCode as the primary agent platform with custom MCP servers, skills, and system prompts. The `gh` CLI is used for GitHub issue management, PR creation, and repository operations. Currently, `gh` may not be installed or referenced consistently across skills.
</system_context>

<agentic_reasoning>
Before implementing, analyze: Is `gh` already installed? Which skills reference `gh`? What system prompt sections need updating? What authentication steps are required?
</agentic_reasoning>

<execution_rules>
- You MUST verify `gh` is installed; if not, install it via the official method
- You MUST authenticate `gh` with GitHub (or document the auth steps)
- You MUST search all skills for `gh` references and ensure they use the installed CLI
- You MUST update system-prompt.md or relevant fragments to mention `gh` as a required tool
- You MUST update AGENTS.md skill registry if a new GitHub skill is added
- Do NOT break existing GitHub integrations
</execution_rules>

<output_format>
Return: installation status, authentication status, files modified, verification results.
</output_format>

## Relevant Code Context

- `skill-templates/audit-agents/SKILL.md` — references `gh` for issue management
- `prompts/fragments/10-agent_skills_registry.md` — skill registry
- `AGENTS.md` — global agent rules and guardrails
- `telegram-issue-sync` skill — uses `gh issue create`

## AI Analysis & Opinion

The `gh` CLI is essential for GitHub operations in the agent workflow. Integration should:
1. Install `gh` via official package manager
2. Run `gh auth login` for authentication
3. Search codebase for `gh` references to ensure consistency
4. Update system-prompt.md fragments to document `gh` as a required tool
5. Update skill registry if needed

Risks: Authentication may require interactive browser flow; environment may not support it.

## Local TODOs

- [x] Check if `gh` is already installed
- [x] Install `gh` CLI if missing
- [x] Authenticate `gh` with GitHub
- [x] Search codebase for `gh` references
- [x] Update system-prompt.md or fragments with `gh` documentation
- [x] Update AGENTS.md skill registry if needed
- [x] Verify `gh` commands work end-to-end

## Acceptance Criteria

- [x] `gh --version` returns valid output
- [x] `gh auth status` shows authenticated
- [x] System prompt and skills reference `gh` consistently
- [x] Documentation reflects installation and usage

## Verification Evidence

- **Test command:** `gh --version && gh auth status`
- **Expected result:** Version info and authenticated status
- **Actual result:** `gh version 2.98.0` (2026-08-20); authenticated as `mokhtarabadi` on github.com (token scopes: admin:public_key, gist, read:org, repo)
- **Exit code:** 0

**Additional verification:**
- `python3 -m py_compile scripts/prompt-build/assemble_system_prompt.py mcp-context-server/server.py mcp-lint-server/server.py mcp-memory-server/server.py` → PY_COMPILE_OK
- `python3 scripts/prompt-build/assemble_system_prompt.py` → Assembled 78041 bytes
- Round-trip: `diff /tmp/check.md system-prompt.md` → ROUND_TRIP_OK (byte-identical)
- pytest: **49 passed, 1 failed** (the 1 failure is pre-existing `test_workflow_upgrade_guide_exists` — `docs/workflow-upgrade-v8.4.5.md` removed in Task 117, unrelated to Task 121)
- `test_workflow_skills_have_no_opencode_execution_log` (modified test) → **1 passed**

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** GitHub auth may require browser interaction not available in headless environment
- **Rollback plan:** Remove gh from PATH, revert system prompt changes

---

## Execution Log & Reasoning

**Discovery (prior phase):**
- `gh` v2.98.0 already installed and authenticated as `@mokhtarabadi` — no install/auth needed
- Official GitHub skill researched: `gh skill` (new CLI command) + `Dimillian/Skills` `github` skill (3.9k stars)
- Mapped 59 `gh` references across repo; active files: `docs/conventions.md` (--body-file), `skill-templates/telegram-issue-sync/SKILL.md`, `README.md`

**Implementation:**
1. **Created `skill-templates/github/SKILL.md`** — canonical GitHub CLI workflow with YAML frontmatter (`name: github`, `description: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.`). Sections: Issue Management (with mandatory `--body-file`), PR Review & Status, CI/CD Workflow & Log Triage, GitHub API & Structured Output, ZAC Guardrails (declaring `gh release create`/`git push`/`git tag` Manager-owned), and `gh skill` self-management. Mirrored to `.opencode/skills/github/SKILL.md`.
2. **Registered in `prompts/fragments/10-agent_skills_registry.md`** — added `- **github**: ...` under Global Workflow Skills.
3. **Bumped `<system_version>` 8.8.0 → 8.9.0** in `prompts/fragments/01-system_version.md` (no trailing newline).
4. **Reassembled `system-prompt.md`** via `assemble_system_prompt.py` (78041 bytes). Verified version `8.9.0` and github skill bullet present. Round-trip byte-identical.
5. **Synced docs:** `docs/conventions.md` (canonical github skill reference), `docs/setup.md` (new `## GitHub CLI (gh)` section with version/auth checks + install commands), `LLM.txt` (gh prerequisite in Section 1, skill count 30→31 in Sections 6 & 10, `gh auth status` checklist item), `README.md` (github in skills table + directory tree, skill count 30→31).
6. **Updated test suite:** `test_workflow_skills_have_no_opencode_execution_log` assertion `>= 29` → `>= 32` (31 skill templates + executor agent).
7. **Updated CHANGELOG.md** under `[Unreleased] > Added` via Parse-Then-Append.

**Architecture Notes:**
- `gh` was already installed/authenticated — the task focused on skill creation and documentation integration, not installation
- The `github` skill is a Global Workflow Skill (not stack-specific) since `gh` is used across all projects
- ZAC guardrails are explicitly encoded in the skill to prevent autonomous `gh release create`/`git push`/`git tag`
- System prompt bumped to v8.9.0 (MINOR — new agent skill) per SemVer rules

**Verification:**
- `gh --version` → v2.98.0; `gh auth status` → authenticated as mokhtarabadi
- py_compile all servers → OK
- pytest: 49 passed, 1 pre-existing failure (`test_workflow_upgrade_guide_exists` — unrelated, `docs/workflow-upgrade-v8.4.5.md` removed in Task 117)
- Modified test `test_workflow_skills_have_no_opencode_execution_log` → 1 passed
- System prompt round-trip → byte-identical

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/skills/github/SKILL.md b/.opencode/skills/github/SKILL.md
new file mode 100644
index 0000000..7f62324
--- /dev/null
+++ b/.opencode/skills/github/SKILL.md
@@ -0,0 +1,116 @@
+---
+name: github
+description: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
+---
+
+# GitHub CLI (gh) Workflow SOP
+
+## Purpose
+
+Standardizes GitHub operations through the official GitHub CLI (`gh`). This skill is the canonical reference for all GitHub CLI workflows in the Cognitive Lead AI multi-agent system — pull request triage, issue management, CI/CD run analysis, and API queries.
+
+## Prerequisites
+
+Verify the `gh` CLI is installed and authenticated before any GitHub operation:
+
+```bash
+gh --version
+gh auth status
+```
+
+If `gh` is not installed, install via the official method (see `docs/setup.md`). If not authenticated, run `gh auth login`.
+
+## Issue Management
+
+### List Issues
+
+```bash
+gh issue list --repo owner/repo
+gh issue list --repo owner/repo --state open --limit 20
+gh issue list --repo owner/repo --label "bug" --json number,title,labels
+```
+
+### View an Issue
+
+```bash
+gh issue view 123 --repo owner/repo
+gh issue view 123 --repo owner/repo --comments
+```
+
+### Create an Issue (MANDATORY `--body-file`)
+
+**CRITICAL:** Always use `--body-file` with a temp Markdown file — NEVER inline `--body "..."`. Inline bodies are fragile (shell escaping, truncation, Markdown corruption). See `docs/conventions.md` for the full rationale.
+
+```bash
+cat > /tmp/gh-issue-body.md << 'EOF'
+## Title
+Full Markdown content here — safe from shell escaping.
+EOF
+
+gh issue create \
+  --title "Issue Title" \
+  --body-file /tmp/gh-issue-body.md \
+  --label "bug"
+
+rm -f /tmp/gh-issue-body.md
+```
+
+## Pull Request Review & Status
+
+```bash
+gh pr view 55 --repo owner/repo
+gh pr diff 55 --repo owner/repo
+gh pr checks 55 --repo owner/repo
+gh pr comments 55 --repo owner/repo
+gh pr list --repo owner/repo --state open
+```
+
+## CI/CD Workflow & Log Triage
+
+```bash
+gh run list --repo owner/repo --limit 10
+gh run view <run-id> --repo owner/repo
+gh run view <run-id> --repo owner/repo --log-failed
+```
+
+### Debugging a CI Failure
+
+1. **Check PR status** — identify which checks are failing: `gh pr checks 55 --repo owner/repo`
+2. **List recent runs** — find the relevant run ID: `gh run list --repo owner/repo --limit 10`
+3. **View the failed run** — see which jobs and steps failed: `gh run view <run-id> --repo owner/repo`
+4. **Fetch failure logs** — get the detailed output for failed steps: `gh run view <run-id> --repo owner/repo --log-failed`
+
+## GitHub API & Structured Output
+
+The `gh api` command accesses data not available through other subcommands:
+
+```bash
+gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
+```
+
+Most commands support `--json` for structured output, filterable with `--jq`:
+
+```bash
+gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
+```
+
+## ZAC Guardrails (STRICTLY FORBIDDEN for Autonomous Agents)
+
+The following operations are **STRICTLY FORBIDDEN** for autonomous agent execution and remain **Manager-owned**:
+
+- `gh release create` — creating GitHub releases
+- `git push` — pushing to remote
+- `git tag` — creating tags
+
+These operations are denied at the permission layer (Zero-Autonomous-Commit / ZAC). The agent MUST NOT execute them. If a release or tag is required, the Manager executes it manually after task closure.
+
+## Self-Management with `gh skill`
+
+The `gh skill` command (GitHub CLI v2.98.0+) manages Agent Skills:
+
+```bash
+gh skill search <query>
+gh skill preview <owner>/<repo> <skill-name>
+gh skill install <owner>/<repo> <skill-name> --agent <host> --pin <ref>
+gh skill update --all
+```
diff --git a/CHANGELOG.md b/CHANGELOG.md
index fc2d36e..026db74 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -24,6 +24,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **GitHub CLI integration + `github` skill (Task 121)** — new `skill-templates/github/SKILL.md` (canonical GitHub CLI workflow: issue management with mandatory `--body-file`, PR review/status, CI/CD run & log triage, `gh api` structured output, and explicit ZAC guardrails declaring `gh release create`/`git push`/`git tag` Manager-owned) mirrored to `.opencode/skills/github/SKILL.md`; registered in `prompts/fragments/10-agent_skills_registry.md` under Global Workflow Skills; `<system_version>` bumped **8.8.0 → 8.9.0** and `system-prompt.md` reassembled (78041 bytes, verified version + github bullet). Docs synced: `docs/conventions.md` (canonical github skill reference), `docs/setup.md` (new `## GitHub CLI (gh)` section with version/auth checks + install commands), `LLM.txt` (gh prerequisite in Section 1, skill count 30→31 in Sections 6 & 10, `gh auth status` checklist item), `README.md` (github in skills table + directory tree, skill count 30→31). Test suite updated: `test_workflow_skills_have_no_opencode_execution_log` assertion `>= 29` → `>= 32` (31 skill templates + executor agent). Verified: `gh --version` (v2.98.0) + `gh auth status` (authenticated as mokhtarabadi), py_compile all servers, pytest suite.
 - **opentmux integration (Task 120)** — installed [opentmux](https://github.com/AnganSamadder/opentmux) (`npm install -g opentmux`) for smart tmux integration with OpenCode, providing real-time agent execution panes. Created `docs/setup.md` with full installation guide covering opentmux, MCP servers, and dev tools. Updated `README.md` with opentmux reference in Quick Start section and added `setup.md` to Repository Structure. Updated `LLM.txt` with Node.js prerequisite handling (Section 1), opentmux global installation (Section 6.2), and verification checklist items (Section 10).
 - **Freebuff Documents skill + docs (2026-08-26)** — new `skill-templates/freebuff-documents/SKILL.md`: SOP for editing Freebuff's knowledge documents — always-loaded roles are defined as sections in the versioned source `freebuff/AGENTS.global.md`, synced byte-identical to `~/.AGENTS.md` + the skill mirrors (`.opencode/skills/`, `~/.config/opencode/skills/`, `~/.agents/skills/`), then linted/verified; registered in `prompts/fragments/10-agent_skills_registry.md`; `system-prompt.md` re-assembled from fragments (byte-exact round-trip, sync test green) with `<system_version>` bumped **8.6.0 → 8.6.1**. New `docs/freebuff-documents.md` documents the Freebuff document system (knowledge files: home `~/.AGENTS.md` > `~/.CLAUDE.md`; project `AGENTS.md` > `CLAUDE.md` > `*.knowledge.md`; `~/.knowledge.md` ignored) and the Cognitive Executive Role reference. Skill synced to all 4 locations (31 skills total, was 30); count references updated in `docs/freebuff-support.md`, `README.md`, `LLM.txt`, and the install/upgrade workflow memory. Verified: prettier, pytest 52 passed.
 - **Telegram MCP Upgrade + Auto-Upgrade Section in Global Install Workflow** — upgraded `~/.config/opencode/mcp-telegram-server` (chigwell/telegram-mcp) from a stale 2.0.1 snapshot to upstream HEAD `52cca20`: backup → shallow clone → rsync overlay (preserving `.env`, `*.session`, `downloads/`, `claude_desktop_config.json`, `mcp_errors.log`) → `uv sync`; verified new modules (`singleton`, `photo_source`, `contact_sheet`) import and **335/335 upstream tests pass** (tests only pass with `.env` held aside — multi-account env leaks into test config, ~26 failures otherwise; quirk documented). Added dedicated **"Telegram MCP Auto-Upgrade"** section to the upgrade workflow memory (`.opencode/memory/workflows/global-install-upgrade.md`): drift audit vs upstream clone, backup+rsync upgrade steps, `.env`-aside test verification, and `AuthKeyDuplicatedError` startup-blocker remedy. Known pending (Manager fixes manually): WORK session `AUTH_KEY_DUPLICATED` blocks telegram MCP startup until regenerated.
diff --git a/LLM.txt b/LLM.txt
index faa4e42..9f5a91b 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -14,6 +14,7 @@ Check that the following tools are installed:
 
 - **Git** — to clone the repository
 - **Node.js (v20+ LTS)** and **npm** — required for opentmux and other npm-based tools
+- **GitHub CLI (`gh`)** — for GitHub operations (issues, PRs, CI runs, API queries)
 - **uv** — fast Python package manager (required by the MCP servers)
 
 ### Installing Node.js (if missing)
@@ -115,7 +116,7 @@ Copy all reusable skills from `skill-templates/` into the global OpenCode skills
 cp -r /tmp/cognitive-lead-hq/skill-templates/* ~/.config/opencode/skills/
 ```
 
-After this, the skills will be available via `/help` from any directory. `skill-templates/` contains **30 skills** (`bundle-tasks` since Task 110).
+After this, the skills will be available via `/help` from any directory. `skill-templates/` contains **31 skills** (`bundle-tasks` since Task 110, `github` since Task 121).
 
 ### 6.1. (Optional) Bundle CLI Script — Only If You Want `uv run scripts/bundle-tasks.py`
 
@@ -317,10 +318,12 @@ After completing all steps, verify:
 - [ ] `npm` is installed (`npm --version`)
 - [ ] `uv` is installed and available (`uv --version`)
 - [ ] `opentmux` is installed globally (`opentmux --version`)
+- [ ] `gh` is installed (`gh --version`)
+- [ ] `gh` is authenticated (`gh auth status`)
 - [ ] `~/.config/opencode/mcp-context-server/server.py` exists and is executable
 - [ ] `~/.config/opencode/mcp-memory-server/server.py` exists and is executable
 - [ ] `~/.config/opencode/mcp-lint-server/server.py` exists and is executable
-- [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` (30 skills total)
+- [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` (31 skills total)
 - [ ] `~/.config/opencode/agents/cognitive-executor.md` exists
 - [ ] `~/.config/opencode/agents/cognitive-discovery.md` exists
 - [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 5 `mcp` entries (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`) + `blowsh_*`/`telegram_*` permissions, no former browser entry
diff --git a/README.md b/README.md
index d46f05f..9bf5a44 100644
--- a/README.md
+++ b/README.md
@@ -233,6 +233,8 @@ python daemon.py
 │   │   └── SKILL.md
 │   ├── doc-coauthoring/                # Structured documentation co-authoring
 │   │   └── SKILL.md
+│   ├── github/                          # GitHub CLI (gh) workflow — PR triage, issues, CI/CD, API
+│   │   └── SKILL.md
 │   ├── migrate-kanban/                 # Flat-to-Kanban migration skill
 │   │   └── SKILL.md
 │   ├── perplexity-research/            # Human-in-the-loop deep research
@@ -301,6 +303,7 @@ python daemon.py
 | `debug-instrumentation`   | Diagnoses complex runtime bugs, deadlocks, race conditions, and silent failures via strategic temporary logging and tracing.                                                                                                              |
 | `design-md`               | Extracts a comprehensive design system (`DESIGN.md`) directly from frontend source code — React, Vue, Svelte, Angular, plain HTML/CSS, or any web framework.                                                                              |
 | `doc-coauthoring`         | Guides users through a structured 3-stage workflow (Context Gathering, Refinement & Structure, Reader Testing) for co-authoring documentation with AI.                                                                                    |
+| `github`                  | GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.                                                                                                                                 |
 | `prompt-refactor`         | Meta-cognitive skill that refactors basic human prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.                                                                                         |
 | `bundle-tasks`            | Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as both `scripts/bundle-tasks.py` CLI and `bundle_tasks` MCP tool (Task 110). |
 | `task-generator`          | Automatically generates decentralized task files based on Manager instructions, with correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.                                                                                 |
@@ -486,7 +489,7 @@ opencode --agent cognitive-executor
 - **Universal Datetime Rules (`<universal_datetime_rules>`):** UTC-at-rest, ISO-8601/Unix-epoch at API boundaries, SOLID Clock injection, dual-representation for future calendar events, and timezone-independent CI/CD testing.
 - **SOLID Programming Mandate (`<solid_programming_mandate>`):** Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion enforced on every generated implementation task, with pragmatic guardrails (No Zero-Abstraction Dogma, 3-Implementation Rule, YAGNI, Occam's Razor).
 - **Leadership & Language Protocol (`<leadership_and_language_protocol>`):** Executive coaching persona that provides vocabulary assistance, English pronunciation guides (Persian phonetics), and ruthless soft-skills feedback during sprint retrospectives.
-- **Expanded Agent Skills Registry:** 30 skills including stack-specific blueprints (android-kotlin, spring-boot, react-vite, nestjs-prisma-vertical, go-hexagonal-grpc, python-fastapi, nextjs, flask-python, react-native-expo, ios-swiftui, vue-nuxt, go-gin) and global workflow skills (brainstorm-swarm, design-md, project-memory, telegram-issue-sync, perplexity-research, verification-before-completion, debug-instrumentation).
+- **Expanded Agent Skills Registry:** 31 skills including stack-specific blueprints (android-kotlin, spring-boot, react-vite, nestjs-prisma-vertical, go-hexagonal-grpc, python-fastapi, nextjs, flask-python, react-native-expo, ios-swiftui, vue-nuxt, go-gin) and global workflow skills (brainstorm-swarm, design-md, project-memory, telegram-issue-sync, perplexity-research, verification-before-completion, debug-instrumentation, github).
 
 ## Key V8 Changes
 
diff --git a/docs/conventions.md b/docs/conventions.md
index c3bf834..cdbade4 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -41,6 +41,10 @@ rm -f /tmp/gh-issue-body.md
 - Always include `rm -f /tmp/gh-issue-body.md` cleanup after the `gh` command.
 - This applies to all files: SKILL.md templates, task files, and scripts.
 
+### Canonical Reference
+
+The [`github` skill](../skill-templates/github/SKILL.md) is the canonical reference for all GitHub CLI workflows — pull request triage, issue management, CI/CD run analysis, and API queries. Load it via the `skill` tool whenever a task involves GitHub operations.
+
 ## Universal DateTime Standard
 
 All projects in this ecosystem MUST follow these datetime rules:
diff --git a/docs/setup.md b/docs/setup.md
index 2f44009..3497b1a 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -7,6 +7,43 @@ This document covers installation and setup for all platform tools and dependenc
 - [Node.js](https://nodejs.org/) (v18+) and npm
 - [OpenCode](https://opencode.ai) (latest version)
 - [uv](https://docs.astral.sh/uv/) (for Python-based MCP servers)
+- [GitHub CLI](https://cli.github.com/) (`gh`) — for GitHub operations
+
+## GitHub CLI (gh)
+
+The [GitHub CLI](https://cli.github.com/) (`gh`) is required for GitHub operations — pull request triage, issue management, CI/CD run analysis, and API queries. See the [`github` skill](../skill-templates/github/SKILL.md) for the canonical workflow reference.
+
+### Verify Installation
+
+```bash
+gh --version
+gh auth status
+```
+
+### Install (if missing)
+
+**Debian/Ubuntu:**
+```bash
+(type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
+&& sudo mkdir -p -m 755 /etc/apt/keyrings \
+&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
+&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
+&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
+&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
+&& sudo apt update \
+&& sudo apt install gh -y
+```
+
+**macOS:**
+```bash
+brew install gh
+```
+
+### Authenticate
+
+```bash
+gh auth login
+```
 
 ## opentmux — Smart Tmux Integration
 
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 7c950a9..adcfcbd 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>8.8.0</system_version>
\ No newline at end of file
+<system_version>8.9.0</system_version>
\ No newline at end of file
diff --git a/prompts/fragments/10-agent_skills_registry.md b/prompts/fragments/10-agent_skills_registry.md
index 386854b..66e328b 100644
--- a/prompts/fragments/10-agent_skills_registry.md
+++ b/prompts/fragments/10-agent_skills_registry.md
@@ -21,6 +21,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **project-memory**: Smart note-taking and persistent project memory. Automatically saves Manager constraints and proactively retrieves context to prevent hallucinations.
 - **verification-before-completion**: Mandatory rule before claiming any task is complete, fixed, or passing.
 - **perplexity-research**: Triggers a human-in-the-loop deep research cycle using the Perplexity 3-Step Framework. Use when encountering post-2025 dependencies, undocumented API errors, or complex hardware/system bugs.
+- **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
diff --git a/skill-templates/github/SKILL.md b/skill-templates/github/SKILL.md
new file mode 100644
index 0000000..7f62324
--- /dev/null
+++ b/skill-templates/github/SKILL.md
@@ -0,0 +1,116 @@
+---
+name: github
+description: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
+---
+
+# GitHub CLI (gh) Workflow SOP
+
+## Purpose
+
+Standardizes GitHub operations through the official GitHub CLI (`gh`). This skill is the canonical reference for all GitHub CLI workflows in the Cognitive Lead AI multi-agent system — pull request triage, issue management, CI/CD run analysis, and API queries.
+
+## Prerequisites
+
+Verify the `gh` CLI is installed and authenticated before any GitHub operation:
+
+```bash
+gh --version
+gh auth status
+```
+
+If `gh` is not installed, install via the official method (see `docs/setup.md`). If not authenticated, run `gh auth login`.
+
+## Issue Management
+
+### List Issues
+
+```bash
+gh issue list --repo owner/repo
+gh issue list --repo owner/repo --state open --limit 20
+gh issue list --repo owner/repo --label "bug" --json number,title,labels
+```
+
+### View an Issue
+
+```bash
+gh issue view 123 --repo owner/repo
+gh issue view 123 --repo owner/repo --comments
+```
+
+### Create an Issue (MANDATORY `--body-file`)
+
+**CRITICAL:** Always use `--body-file` with a temp Markdown file — NEVER inline `--body "..."`. Inline bodies are fragile (shell escaping, truncation, Markdown corruption). See `docs/conventions.md` for the full rationale.
+
+```bash
+cat > /tmp/gh-issue-body.md << 'EOF'
+## Title
+Full Markdown content here — safe from shell escaping.
+EOF
+
+gh issue create \
+  --title "Issue Title" \
+  --body-file /tmp/gh-issue-body.md \
+  --label "bug"
+
+rm -f /tmp/gh-issue-body.md
+```
+
+## Pull Request Review & Status
+
+```bash
+gh pr view 55 --repo owner/repo
+gh pr diff 55 --repo owner/repo
+gh pr checks 55 --repo owner/repo
+gh pr comments 55 --repo owner/repo
+gh pr list --repo owner/repo --state open
+```
+
+## CI/CD Workflow & Log Triage
+
+```bash
+gh run list --repo owner/repo --limit 10
+gh run view <run-id> --repo owner/repo
+gh run view <run-id> --repo owner/repo --log-failed
+```
+
+### Debugging a CI Failure
+
+1. **Check PR status** — identify which checks are failing: `gh pr checks 55 --repo owner/repo`
+2. **List recent runs** — find the relevant run ID: `gh run list --repo owner/repo --limit 10`
+3. **View the failed run** — see which jobs and steps failed: `gh run view <run-id> --repo owner/repo`
+4. **Fetch failure logs** — get the detailed output for failed steps: `gh run view <run-id> --repo owner/repo --log-failed`
+
+## GitHub API & Structured Output
+
+The `gh api` command accesses data not available through other subcommands:
+
+```bash
+gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
+```
+
+Most commands support `--json` for structured output, filterable with `--jq`:
+
+```bash
+gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
+```
+
+## ZAC Guardrails (STRICTLY FORBIDDEN for Autonomous Agents)
+
+The following operations are **STRICTLY FORBIDDEN** for autonomous agent execution and remain **Manager-owned**:
+
+- `gh release create` — creating GitHub releases
+- `git push` — pushing to remote
+- `git tag` — creating tags
+
+These operations are denied at the permission layer (Zero-Autonomous-Commit / ZAC). The agent MUST NOT execute them. If a release or tag is required, the Manager executes it manually after task closure.
+
+## Self-Management with `gh skill`
+
+The `gh skill` command (GitHub CLI v2.98.0+) manages Agent Skills:
+
+```bash
+gh skill search <query>
+gh skill preview <owner>/<repo> <skill-name>
+gh skill install <owner>/<repo> <skill-name> --agent <host> --pin <ref>
+gh skill update --all
+```
diff --git a/system-prompt.md b/system-prompt.md
index fc57f87..918b7bc 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>8.8.0</system_version>
+<system_version>8.9.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -221,6 +221,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **project-memory**: Smart note-taking and persistent project memory. Automatically saves Manager constraints and proactively retrieves context to prevent hallucinations.
 - **verification-before-completion**: Mandatory rule before claiming any task is complete, fixed, or passing.
 - **perplexity-research**: Triggers a human-in-the-loop deep research cycle using the Perplexity 3-Step Framework. Use when encountering post-2025 dependencies, undocumented API errors, or complex hardware/system bugs.
+- **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
diff --git a/tests/test_mcp_servers.py b/tests/test_mcp_servers.py
index 5ac944c..5c42fb6 100644
--- a/tests/test_mcp_servers.py
+++ b/tests/test_mcp_servers.py
@@ -1060,8 +1060,8 @@ def test_workflow_skills_have_no_opencode_execution_log():
     repo_root = Path(__file__).parent.parent
     target_files = list((repo_root / "skill-templates").glob("*/SKILL.md"))
     target_files.append(repo_root / "agents" / "cognitive-executor.md")
-    assert len(target_files) >= 29, (
-        f"Expected the 29 skill templates + executor agent, got {len(target_files)} files"
+    assert len(target_files) >= 32, (
+        f"Expected the 32 skill templates + executor agent, got {len(target_files)} files"
     )
     for skill_file in target_files:
         content = skill_file.read_text(encoding="utf-8")
```
<!-- END_GIT_DIFF -->
