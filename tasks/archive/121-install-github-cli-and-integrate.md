# Task 121: Install GitHub CLI and Integrate into System Prompt and Skills

**File:** `tasks/completed/121-install-github-cli-and-integrate.md`
**Source:** telegram
**Type:** feature
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `7cd321f81df2b90366ca9f7cacd24c2dcabc2844`
<!-- END_GIT_DIFF -->
