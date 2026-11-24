---
name: versioning-and-release
description: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.
---

# Versioning, Changelog, and Release Management SOP

## Purpose

Enforces a strict, uniform workflow for versioning, tracking modifications, writing git history, and pushing code across all workspace projects. Every agent modifying any repository MUST strictly adhere to this protocol to prevent chaotic git history and untracked changes.

## Portability Contract

This skill is project-agnostic by contract. The sections below form the portable core and apply to every repository. Harness projects (workspaces shipping the Cognitive Lead platform agent files and Kanban task lanes) additionally apply the clearly labeled Harness Profile section at the end; nothing in the core depends on a specific platform's tools or file layout.

## Core Conventions

### 1. Semantic Versioning (SemVer)

Format: `MAJOR.MINOR.PATCH` (e.g., `5.3.0`)

- **PATCH (`0.0.1` increment):** bug fixes, documentation syncs, formatting, raw text cleanups, minor tool polishing.
- **MINOR (`0.1.0` increment):** new agent skills, new stack templates, new sub-components, non-breaking architectural upgrades.
- **MAJOR (`1.0.0` increment):** complete prompt/instruction rewrites, breaking contract changes, schema modifications.

### 2. Changelog Management (Keep a Changelog)

Every project MUST maintain a `CHANGELOG.md` at the root, newest release first below any `[Unreleased]` section, using exact categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.

### Parse-Then-Append Protocol

Before inserting any entry: read the whole file; find the target version header; find the target category under it; append if both exist; create the category in canonical order if only the header exists; create the header directly below `[Unreleased]` if the header is absent; NEVER duplicate a category header under one version.

### 3. Conventional Commits

All commit messages use lowercase prefixes plus colon and space, first line maximum 72 characters: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`.

## Detailed Workflow

### Phase 1: Pre-Commit Quality Checks

1. The local test suite and type-checkers pass before any completion claim (maximum 3 consecutive repair attempts; after that, halt with a failure report).
2. The project's documented conventions are respected wherever they live (agent instruction files, design guides, contribution rules).
3. DevOps/Infra tasks: run ALL environment-specific verification commands (registry authentication, token scope, network access) BEFORE staging. On any failure, HALT with a failure report; never stage partial work.

### Phase 2: Metadata Synchronization

1. If a version identifier is embedded in project documentation, prompts, or configuration and your change affects what it covers, bump it per SemVer.
2. Insert a formal `CHANGELOG.md` entry under the new version header via Parse-Then-Append, categorizing every modification correctly.
3. Log final reasoning and files modified in the project's active tracking artifact (task file, board card, or equivalent).
4. Metadata-only releases: the changelog entry MUST state the version marker is unchanged.
5. The `[Unreleased]` section MUST be empty after a release; all entries move under the new version header.

### Phase 3: Staging & Factual Diff

1. Stage exactly the files this task modified, through the project's approved staging mechanism, and make the factual diff available to the reviewer.
2. Never run raw `git add`, `git commit`, `git checkout`, or `git push`. Parallel sessions: if the shared working tree carries another session's changes to a file, stage only this task's hunks; never commit foreign content.

### Phase 4: Commit & Push Boundaries

1. Commit only through the project's approved commit mechanism, with a Conventional Commits message that the mechanism validates.
2. Pushing to a remote is owner-gated: the repository owner performs it after task closure, never an autonomous agent.

## Harness Profile (optional — Cognitive Lead harness projects only)

Apply this section only in workspaces that ship the platform agent files and Kanban lanes.

1. Read `AGENTS.md` as the entry point and respect `DESIGN.md` conventions in full.
2. The active task file lives in `tasks/`; record final reasoning under its "Execution Log & Reasoning" section.
3. If `system-prompt.md` was edited, verify `<system_version>` at the top is bumped per SemVer.
4. If a release changes system behavior, skills, MCP servers, task templates, or workflow rules, the `system-prompt.md` version MUST be bumped.
5. If the repository generates stage-scoped prompt artifacts, every release that changes prompt sources must regenerate the full prompt and every declared stage artifact, then pass the repository freshness gate before deployment. A release with a stale stage artifact is incomplete.
6. Stage via the `custom_context_stage_and_inject_diff` MCP tool with the active task file path; it stages the code and injects the factual diff. Parallel sessions: if the staged diff carries another task's hunks, call `custom_context_unstage_files` with exactly those files (index-only, worktree untouched), redo hunk-level staging, then re-run staging with `skip_add=True`. Never commit or checkout — both stay forbidden.
7. Closure commits go ONLY through the `custom_context_commit_and_clean_task` MCP tool (ZAC-compliant), with a message whose type is in `feat|fix|docs|refactor|chore` and first line at most 72 characters; the tool rejects free-form text — fix the message, never bypass.
8. Service restarts after a prompt deploy are owner-gated: the Manager performs them; an agent never restarts the running services.
