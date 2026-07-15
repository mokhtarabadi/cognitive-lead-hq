# Task: Enforce --body-file pattern for all gh commands instead of inline --body

**File:** `tasks/35-enforce-body-file-pattern-for-gh-commands.md`
**Type:** improvement
**Status:** closed

## Original GitHub Issue

**Issue #3** — Enforce `--body-file` pattern for all `gh` commands instead of inline `--body`

### Summary

Enforce a strict rule across all skills and docs: **`gh` commands that send body content MUST use `--body-file` with a temp Markdown file, never inline `--body`.** Inline bodies get corrupted by shell escaping, truncation, and formatting loss.

### Why

Inline `--body "..."` in `gh issue create` is fragile:

| Problem             | Example                                               |
| ------------------- | ----------------------------------------------------- |
| Shell escaping      | Backticks, `$`, `"` inside the body break the command |
| Truncation          | Long bodies get silently cut off                      |
| Markdown corruption | Newlines, `#`, `---` can break shell parsing          |
| No preview          | You can't verify what will actually be sent           |

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

- [x] Initial codebase exploration — grep for all `gh issue create --body` occurrences
- [x] Fix `skill-templates/telegram-issue-sync/SKILL.md`
- [x] Fix `tasks/22-refactor-telegram-skill-templates.md`
- [x] Fix `tasks/11-enforce-project-skill-loading.md`
- [x] Fix `tasks/06-implement-telegram-issue-sync-skill.md`
- [x] Document the `--body-file` convention in `docs/conventions.md`
- [x] Verify no inline `--body` patterns remain

## OpenCode Execution Log & Reasoning

### Files Modified

| File | Change |
|------|--------|
| `skill-templates/telegram-issue-sync/SKILL.md` | Replaced inline `--body` with `--body-file` heredoc + `rm -f` cleanup |
| `tasks/22-refactor-telegram-skill-templates.md` | Same conversion (diff-context file) |
| `tasks/11-enforce-project-skill-loading.md` | Changed `--body` flag to `--body-file` |
| `tasks/06-implement-telegram-issue-sync-skill.md` | Changed `--body` flag to `--body-file` |

### Files Created

| File | Purpose |
|------|---------|
| `docs/conventions.md` | Documents the `--body-file` convention with rationale, standard pattern, and rules |

### Architectural Reasoning

- **Single-quoted `'EOF'` heredoc**: Prevents any shell variable expansion (`$VAR`, backticks) inside the body template. This is critical because the template contains placeholders like `{RAW_TEXT}`, `{EN_TRANSLATION}` that LLMs will replace — with double-quoted EOF, shell would try to expand `${RAW_TEXT}` and silently produce empty strings.
- **`rm -f` cleanup after `gh issue create`**: Ensures no temp files leak in `/tmp/` across multiple sync cycles. The `-f` flag prevents errors if the file was already deleted.
- **Centralized in `docs/conventions.md`**: Rather than documenting the pattern ad-hoc in each file, one canonical doc serves as the single source of truth referenced by AGENTS.md.
- **Diff-context files preserved**: For `tasks/22-refactor-telegram-skill-templates.md` (which stores git diffs with `+`/`-` prefixes), the new code block maintains the exact same diff format so the patch remains semantically correct.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 22d1286..4930bfa 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Changed
+
+- **Enforced `--body-file` pattern for all `gh issue create` commands** across the codebase. Replaced inline `--body` in `skill-templates/telegram-issue-sync/SKILL.md`, `tasks/22-refactor-telegram-skill-templates.md`, `tasks/11-enforce-project-skill-loading.md`, and `tasks/06-implement-telegram-issue-sync-skill.md` with heredoc `--body-file` pattern using single-quoted `'EOF'` delimiter. Added `docs/conventions.md` documenting the convention.
+
 ## [5.18.0] — 2026-07-13
 
 ### Added
diff --git a/docs/conventions.md b/docs/conventions.md
new file mode 100644
index 0000000..b8a453f
--- /dev/null
+++ b/docs/conventions.md
@@ -0,0 +1,42 @@
+# Conventions
+
+This document defines syntax rules, naming conventions, file boundaries, and automation patterns for the Cognitive Lead AI multi-agent system HQ.
+
+## GitHub CLI Automation
+
+All `gh` commands that send body content MUST use `--body-file` with a temp Markdown file, never inline `--body`.
+
+### Rationale
+
+Inline `--body "..."` in `gh issue create` is fragile:
+
+| Problem             | Example                                               |
+| ------------------- | ----------------------------------------------------- |
+| Shell escaping      | Backticks, `$`, `"` inside the body break the command |
+| Truncation          | Long bodies get silently cut off                      |
+| Markdown corruption | Newlines, `#`, `---` can break shell parsing          |
+| No preview          | You can't verify what will actually be sent           |
+
+Using `--body-file /tmp/gh-issue-body.md` guarantees precise, verbatim delivery of the full Markdown content.
+
+### Standard Pattern
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
+  --label "some-label"
+
+rm -f /tmp/gh-issue-body.md
+```
+
+### Rules
+
+- Use single-quoted `'EOF'` delimiter to prevent shell variable expansion.
+- Always include `rm -f /tmp/gh-issue-body.md` cleanup after the `gh` command.
+- This applies to all files: SKILL.md templates, task files, and scripts.
diff --git a/skill-templates/telegram-issue-sync/SKILL.md b/skill-templates/telegram-issue-sync/SKILL.md
index 63654d6..5d131f5 100644
--- a/skill-templates/telegram-issue-sync/SKILL.md
+++ b/skill-templates/telegram-issue-sync/SKILL.md
@@ -200,10 +200,25 @@ _(Git diff will be automatically injected here by the MCP tool. Do not edit this
 Only if `GH_ENABLED` is true:
 
 ```bash
+cat > /tmp/gh-issue-body.md << 'EOF'
+## Original Message
+{RAW_TEXT}
+
+## English Translation
+{EN_TRANSLATION}
+
+## AI Analysis
+{AI_OPINION}
+
+---
+Migrated from Telegram. See local task file for details.
+EOF
+
 GH_URL=$(gh issue create \
   --title "{Task Title}" \
-  --body "## Original Message\n{RAW_TEXT}\n\n## English Translation\n{EN_TRANSLATION}\n\n## AI Analysis\n{AI_OPINION}\n\n---\nMigrated from Telegram. See local task file for details." \
+  --body-file /tmp/gh-issue-body.md \
   --label "telegram-sync")
+rm -f /tmp/gh-issue-body.md
 echo "GH_URL=$GH_URL"
 ```
```
<!-- END_GIT_DIFF -->
