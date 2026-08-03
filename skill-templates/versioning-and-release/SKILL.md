---
name: versioning-and-release
description: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.
---

# Versioning, Changelog, and Release Management SOP

## Purpose

Enforces a strict, uniform workflow for versioning, tracking modifications, writing git history, and pushing code across all workspace projects. Every agent modifying any repository MUST strictly adhere to this protocol to prevent chaotic git history and untracked changes.

## Core Conventions

### 1. Semantic Versioning (SemVer)

Format: `MAJOR.MINOR.PATCH` (e.g., `5.3.0`)

- **PATCH (`0.0.1` increment):** Used for bug fixes, documentation syncs, formatting, raw text cleanups, or minor tool polishing.
- **MINOR (`0.1.0` increment):** Used for new agent skills, new stack templates, adding major sub-components, or non-breaking architectural upgrades.
- **MAJOR (`1.0.0` increment):** Used for complete system prompt rewrites, breaking API contract changes, or protocol schema modifications.

### 2. Changelog Management (Keep a Changelog)

Every project MUST maintain a `CHANGELOG.md` file at the root. Modifications must be logged under the appropriate version header using these exact categories:

- `Added` — for new features, skills, or blueprints.
- `Changed` — for changes in existing functionality.
- `Deprecated` — for soon-to-be-removed features.
- `Removed` — for now-removed features.
- `Fixed` — for any bug fixes.
- `Security` — in case of vulnerabilities or security updates.

### Parse-Then-Append Protocol

Before inserting any entry into CHANGELOG.md:

1. Read the entire file.
2. Search for the target version header (e.g., `## [7.1.0]`).
3. If the version header exists, search for the target category (e.g., `### Changed`) under it.
4. If the category exists, append the new entry as a bullet under it.
5. If the category does NOT exist, create it under the version header in the canonical order: Added, Changed, Deprecated, Removed, Fixed, Security.
6. If the version header does NOT exist, create it at the top (below `## [Unreleased]` if present) with the required category.
7. NEVER create a duplicate category header under the same version.

### 3. Conventional Commits

All git commit messages MUST use lowercase prefixes followed by a colon and a space, describing the change concisely (maximum 72 characters):

- `feat: [description]` — for new features, skills, or blueprints.
- `fix: [description]` — for bug fixes, syntax corrections, or logical repairs.
- `docs: [description]` — for markdown, documentation, or README edits.
- `refactor: [description]` — for restructuring code without changing behavior.
- `chore: [description]` — for configurations, package updates, or tooling configs (e.g., `opencode.json`).

## Detailed Workflow

### Phase 1: Pre-Commit Quality Checks

1. Before completing any task, ensure the local test suite and type-checkers have passed successfully (maximum of 3 consecutive repair attempts as per V5.3.0 strict guardrails).
2. Ensure `AGENTS.md` and `DESIGN.md` conventions are fully respected.
3. **Pre-Commit Verification Gate (Environment Verification, DevOps/Infra tasks only):** If the task involves deployment, Docker, CI/CD, or infrastructure changes, run ALL environment-specific verification commands (e.g., `docker login`, token scope validation, registry access checks) BEFORE proceeding to staging. If ANY check fails, HALT and output a failure report. Do NOT stage partial work.

### Phase 2: Metadata Synchronization

1. If `system-prompt.md` was edited, verify that `<system_version>` at the top is bumped according to SemVer rules.
2. Open `CHANGELOG.md` and insert a formal release entry under the new version header, categorizing your modifications correctly.
3. Open the active task file in `tasks/` and ensure your final reasoning and files modified are accurately logged under the "OpenCode Execution Log" section.
4. If a release includes changes to system behavior, skills, MCP servers, task templates, or workflow rules, `system-prompt.md` version MUST be bumped.
5. If a release is metadata-only (e.g., LICENSE addition), the CHANGELOG MUST explicitly state: "system-prompt.md version unchanged."
6. The `[Unreleased]` section MUST be empty after a release. All entries MUST be moved under the new version header.

### Phase 3: Staging & Factual Diff Injection

1. Call the `custom_context_stage_and_inject_diff` MCP tool, providing the exact path to your active task file.
2. This stages your modified codebase files and automatically injects the factual diff into your task file, ensuring the Code Reviewer has a grounded reference.

### Phase 4: Git Commit & Secure Push Protocol

1. Run the non-interactive commit command with a Conventional Commit message.
   _Example:_ `git commit -m "docs: finalize versioning skill template"`
2. Before pushing to the remote repository, check if the working tree is clean (`git status`).
3. Run the secure, non-interactive push command:
   `git push origin main` (or the active branch).
4. If the push fails due to remote updates, run `git pull --rebase` first, verify tests pass again, and then push.
