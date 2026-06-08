# Task 07: Implement Versioning & Release Management Skill

**Type:** feature
**Status:** completed

## Goal

Implement the global `versioning-and-release` skill template inside `skill-templates/` to standardize Semantic Versioning, Keep a Changelog formatting, Conventional Commits, and Safe Push Protocols across all repositories.

## Manager's Notes

- The skill must codify SemVer, Conventional Commits, Keep a Changelog, and pushing rules.
- Update CHANGELOG.md.

## Local TODOs

- [x] Create skill-templates/versioning-and-release/SKILL.md
- [x] Document SemVer increments rules (Major/Minor/Patch)
- [x] Document Conventional Commits prefixes (feat, fix, docs, refactor, chore)
- [x] Document Keep a Changelog categories
- [x] Document Safe Push Protocols
- [x] Update CHANGELOG.md

## OpenCode Execution Log & Reasoning

- Designed and implemented the comprehensive `versioning-and-release` SOP under templates.
- Standardized how SemVer is applied to prompts (Major), skills (Minor), and docs (Patch).
- Enforced Conventional Commit formats to keep git history pristine across all corporate repositories.
- Updated CHANGELOG.md to track this new release-standards template.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 0d65eee..f158df6 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -124,6 +124,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ### Added

+- **`skill-templates/versioning-and-release/SKILL.md`** — new global Agent Skill template for standardizing Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols.
+- **Task 07** — local task file tracking the release-standards skill implementation.
 - **`skill-templates/telegram-issue-sync/SKILL.md`** — new global, optional Agent Skill template for syncing Telegram group topics with local tasks and GitHub issues, featuring advanced non-tagged discussion thread crawling.
 - **Task 06** — local task file tracking the synchronization skill implementation.
 - **Mandatory Code Documentation constraint** in `system-prompt.md` — OpenCode is now required to write docstrings on all public functions/classes, inline comments on non-obvious logic, and README/header comments for new modules. Enforced via both `<constraints>` and the `<opencode_implementation_task_template>` execution phase.
diff --git a/skill-templates/versioning-and-release/SKILL.md b/skill-templates/versioning-and-release/SKILL.md
new file mode 100644
index 0000000..ade8744
--- /dev/null
+++ b/skill-templates/versioning-and-release/SKILL.md
@@ -0,0 +1,68 @@
+---
+name: versioning-and-release
+description: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.
+---
+
+# Versioning, Changelog, and Release Management SOP
+
+## Purpose
+
+Enforces a strict, uniform workflow for versioning, tracking modifications, writing git history, and pushing code across all workspace projects. Every agent modifying any repository MUST strictly adhere to this protocol to prevent chaotic git history and untracked changes.
+
+## Core Conventions
+
+### 1. Semantic Versioning (SemVer)
+
+Format: `MAJOR.MINOR.PATCH` (e.g., `5.3.0`)
+
+- **PATCH (`0.0.1` increment):** Used for bug fixes, documentation syncs, formatting, raw text cleanups, or minor tool polishing.
+- **MINOR (`0.1.0` increment):** Used for new agent skills, new stack templates, adding major sub-components, or non-breaking architectural upgrades.
+- **MAJOR (`1.0.0` increment):** Used for complete system prompt rewrites, breaking API contract changes, or protocol schema modifications.
+
+### 2. Changelog Management (Keep a Changelog)
+
+Every project MUST maintain a `CHANGELOG.md` file at the root. Modifications must be logged under the appropriate version header using these exact categories:
+
+- `Added` — for new features, skills, or blueprints.
+- `Changed` — for changes in existing functionality.
+- `Deprecated` — for soon-to-be-removed features.
+- `Removed` — for now-removed features.
+- `Fixed` — for any bug fixes.
+- `Security` — in case of vulnerabilities or security updates.
+
+### 3. Conventional Commits
+
+All git commit messages MUST use lowercase prefixes followed by a colon and a space, describing the change concisely (maximum 72 characters):
+
+- `feat: [description]` — for new features, skills, or blueprints.
+- `fix: [description]` — for bug fixes, syntax corrections, or logical repairs.
+- `docs: [description]` — for markdown, documentation, or README edits.
+- `refactor: [description]` — for restructuring code without changing behavior.
+- `chore: [description]` — for configurations, package updates, or tooling configs (e.g., `opencode.json`).
+
+## Detailed Workflow
+
+### Phase 1: Pre-Commit Quality Checks
+
+1. Before completing any task, ensure the local test suite and type-checkers have passed successfully (maximum of 3 consecutive repair attempts as per V5.3.0 strict guardrails).
+2. Ensure `AGENTS.md` and `DESIGN.md` conventions are fully respected.
+
+### Phase 2: Metadata Synchronization
+
+1. If `system-prompt.md` was edited, verify that `<system_version>` at the top is bumped according to SemVer rules.
+2. Open `CHANGELOG.md` and insert a formal release entry under the new version header, categorizing your modifications correctly.
+3. Open the active task file in `tasks/` and ensure your final reasoning and files modified are accurately logged under the "OpenCode Execution Log" section.
+
+### Phase 3: Staging & Factual Diff Injection
+
+1. Call the `custom_context_stage_and_inject_diff` MCP tool, providing the exact path to your active task file.
+2. This stages your modified codebase files and automatically injects the factual diff into your task file, ensuring the Code Reviewer has a grounded reference.
+
+### Phase 4: Git Commit & Secure Push Protocol
+
+1. Run the non-interactive commit command with a Conventional Commit message.
+   _Example:_ `git commit -m "docs: finalize versioning skill template"`
+2. Before pushing to the remote repository, check if the working tree is clean (`git status`).
+3. Run the secure, non-interactive push command:
+   `git push origin main` (or the active branch).
+4. If the push fails due to remote updates, run `git pull --rebase` first, verify tests pass again, and then push.
```

<!-- END_GIT_DIFF -->
