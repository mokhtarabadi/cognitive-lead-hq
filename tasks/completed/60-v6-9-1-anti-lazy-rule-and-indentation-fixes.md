# Task: V6.9.1 Anti-Lazy Rule and XML Indentation Fixes

**File:** `tasks/in-progress/60-v6-9-1-anti-lazy-rule-and-indentation-fixes.md`
**Type:** improvement
**Status:** closed

## Goal

Apply minor improvements to `system-prompt.md`:
1. Add **Deterministic Tool Orchestration (Anti-Lazy Rule)** to constraints — forces singular, deterministic MCP tool commands without "OR" fallback options
2. Add **Isolated Closure Mandate** to execution workflow step 8 — forbids bundling closure commands with other tasks
3. Add **Strict Tool Enforcement** wording to Code Reviewer behavior — forces `custom_context_commit_and_clean_task` without alternatives
4. Fix leading whitespace on closing XML tags (`</manager_profile>`, `</leadership_and_language_protocol>`, `</agent_skills_registry>`, `</user_input_processing>`, `</agentic_reasoning>`)
5. Bump `<system_version>` from 6.9.0 to 6.9.1

## Manager's Notes

- Changes already present in working tree — just needs CHANGELOG update, commit, and push

## Local TODOs

- [x] Codebase exploration — `git diff` read
- [x] Update `CHANGELOG.md` with `[6.9.1]` entry
- [x] Stage and commit changes
- [x] Push to remote
- [x] Move task to completed

## OpenCode Execution Log & Reasoning

### Architecture & Reasoning

**Changes applied manually by Manager then finalized by OpenCode:**

1. **Anti-Lazy Rule** (`system-prompt.md` `<constraints>` section): LLM agents optimize for path of least resistance. When given "OR" conditions (e.g., "use MCP tool OR stage manually"), they bypass the tool. This rule forces deterministic, single-path tool instructions.

2. **Isolated Closure Mandate** (`execution_workflow` step 8): Prevents the Orchestrator from bundling `git mv` to completed with unrelated documentation steps. Closure must be an isolated, explicitly authorized command.

3. **Strict Tool Enforcement** (Code Reviewer `<behavior>`): Adds "without alternative options" to the `custom_context_commit_and_clean_task` instruction — closing the OR-condition loophole.

4. **XML Indentation**: Fixed leading spaces on 5 closing tags to align with their opening tags, improving consistency.

5. **Version bumped** from 6.9.0 to 6.9.1.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `1d3c48085c84a0b1c7c3a774f11f32c3d49baac8`
<!-- END_GIT_DIFF -->
