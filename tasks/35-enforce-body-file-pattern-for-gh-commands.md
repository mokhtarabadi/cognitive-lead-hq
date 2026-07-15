# Task: Enforce --body-file pattern for all gh commands instead of inline --body

**File:** `tasks/35-enforce-body-file-pattern-for-gh-commands.md`
**Type:** improvement
**Status:** open

## Original GitHub Issue

**Issue #3** — Enforce `--body-file` pattern for all `gh` commands instead of inline `--body`

### Summary

Enforce a strict rule across all skills and docs: **`gh` commands that send body content MUST use `--body-file` with a temp Markdown file, never inline `--body`.** Inline bodies get corrupted by shell escaping, truncation, and formatting loss.

### Why

Inline `--body "..."` in `gh issue create` is fragile:

| Problem | Example |
|---------|---------|
| Shell escaping | Backticks, `$`, `"` inside the body break the command |
| Truncation | Long bodies get silently cut off |
| Markdown corruption | Newlines, `#`, `---` can break shell parsing |
| No preview | You can't verify what will actually be sent |

Using `--body-file /tmp/gh-issue-body.md` guarantees **precise, verbatim delivery** of the full Markdown content.

### Affected Files (must be fixed)

1. `skill-templates/telegram-issue-sync/SKILL.md` (line 203) — inline `--body`
2. `tasks/22-refactor-telegram-skill-templates.md` (line 170) — inline `--body`
3. `tasks/11-enforce-project-skill-loading.md` (line 165) — old pattern reference
4. `tasks/06-implement-telegram-issue-sync-skill.md` (line 122) — old pattern reference

---

## Refactored Prompt

```markdown
<role>
You are a Senior DevOps & Shell Scripting Architect specialized in GitHub CLI automation, Markdown pipeline integrity, and multi-platform shell escaping prevention.
</role>

<system_context>
You are operating inside the Cognitive Lead AI multi-agent system HQ repository (best-prompts). This repo contains system prompts, MCP servers, Agent Skills (SKILL.md), and task files in `tasks/`. The project uses `gh` (GitHub CLI) extensively for issue creation from automated pipelines, especially from the `telegram-issue-sync` skill. You have access to bash, file read/write, and git tools.
</system_context>

<agentic_reasoning>
Before executing any edit, you MUST output a <reasoning_log> that:
1. Identifies every file in the repo containing `gh issue create --body` (inline pattern) using grep.
2. Assesses risk: does the file currently rely on variable interpolation inside `--body` that would break if moved to `--body-file`?
3. Validates that `cat > /tmp/gh-issue-body.md << 'EOF'` with single-quoted EOF prevents all shell expansion.
4. Confirms the cleanup `rm -f /tmp/gh-issue-body.md` is present after every `--body-file` usage.
</agentic_reasoning>

<execution_rules>
- You MUST replace every instance of `gh issue create --body "..."` with the `--body-file` pattern using a heredoc with single-quoted EOF delimiter.
- You MUST NOT leave any inline `--body` pattern in skill templates or task files.
- You MUST ensure `rm -f /tmp/gh-issue-body.md` is called after each `gh issue create` that uses `--body-file`.
- You MUST NOT modify logic or variable references — only the delivery mechanism changes.
- You MUST treat `tasks/` files as living documentation and update them to reflect the new convention, not just the canonical skill template.
</execution_rules>

<output_format>
You MUST output a structured diff report listing each affected file, the exact old inline pattern found, and the replacement `--body-file` block. Use the format:

File: `<path>` (line <line_number>)
- OLD: `<inline body snippet>`
- NEW: `<body-file block>`
- STATUS: [PENDING | DONE | SKIPPED]
</output_format>
```

## Acceptance Criteria

- [ ] `skill-templates/telegram-issue-sync/SKILL.md` updated to use `--body-file`
- [ ] `tasks/22-refactor-telegram-skill-templates.md` updated
- [ ] All documentation references to `gh issue create --body "..."` replaced with the file-based pattern
- [ ] The pattern is documented as a convention in `docs/conventions.md` or `AGENTS.md`

## Local TODOs

- [ ] Initial codebase exploration — grep for all `gh issue create --body` occurrences
- [ ] Fix `skill-templates/telegram-issue-sync/SKILL.md`
- [ ] Fix `tasks/22-refactor-telegram-skill-templates.md`
- [ ] Fix `tasks/11-enforce-project-skill-loading.md`
- [ ] Fix `tasks/06-implement-telegram-issue-sync-skill.md`
- [ ] Document the `--body-file` convention in `docs/conventions.md`
- [ ] Verify no inline `--body` patterns remain

## OpenCode Execution Log & Reasoning

_(OpenCode: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
