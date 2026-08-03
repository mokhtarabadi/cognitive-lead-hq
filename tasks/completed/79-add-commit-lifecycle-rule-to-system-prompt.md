# Task 79: Add commit_lifecycle_rule to system prompt constraints

**File:** `tasks/completed/79-add-commit-lifecycle-rule-to-system-prompt.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Add a `<commit_lifecycle_rule>` bullet point to the `<constraints>` section of `system-prompt.md` that documents the two MCP commit tools (`stage_and_inject_diff` for development-time, `commit_and_clean_task` for closure-time), their distinct lifecycle semantics, and the ZAC enforcement rule. This makes the ZAC intent globally visible rather than buried only in the `<bash_phase>` implementation templates.

## Manager's Notes

- The Architect recommended this after reviewing the Zen Router incident (Task 13) where OpenCode invoked `commit_and_clean_task` during implementation. The ZAC rule exists in `<bash_phase>` CRITICAL RULE 2 but is invisible in top-level `<constraints>`.
- Follow existing `<constraints>` bullet-point style (`- **Bold:**` with numbered sub-items).
- System-prompt edits require: version bump in `<system_version>`, active task file in `tasks/`, CHANGELOG entry.

## Local TODOs

- [x] Create task file
- [x] Add `<commit_lifecycle_rule>` to `<constraints>` in system-prompt.md
- [x] Bump `<system_version>` from 8.0.0 to 8.0.1 (PATCH)
- [x] Update CHANGELOG.md [Unreleased] with Changed entry
- [x] Move to completed, lint, stage via MCP tool

## Acceptance Criteria

- [ ] `<constraints>` section in system-prompt.md contains the commit lifecycle rule with both MCP tools documented
- [ ] `<system_version>` bumped to 8.0.1
- [ ] CHANGELOG.md updated with formal entry
- [ ] Task file lint passes

## Verification Evidence

- **Test command:** `grep -A 10 "Commit Lifecycle Rule" system-prompt.md`
- **Expected result:** Rule text present in `<constraints>` section
- **Actual result:** _(OpenCode fills during execution)_
- **Exit code:** _(OpenCode fills during execution)_

## Risk & Rollback

- **Risk:** Adding a constraint to the system prompt increases token count slightly (~150 tokens).
- **Rollback plan:** Remove the `<commit_lifecycle_rule>` bullet from `<constraints>` and revert `<system_version>`.

---

## OpenCode Execution Log & Reasoning

### Execution Summary

**Files modified:**
- `system-prompt.md` — `<system_version>` bumped from `8.0.0` to `8.0.1` (PATCH); new `<commit_lifecycle_rule>` bullet added to `<constraints>` section
- `CHANGELOG.md` — new `### Changed` entry under `[Unreleased]`

### What Was Done

1. **`<constraints>` enhancement:** Added a `<commit_lifecycle_rule>` bullet point (lines 433–439 of `system-prompt.md`) documenting:
   - The two commit-producing MCP tools and their lifecycle semantics
   - `stage_and_inject_diff` = development-time (stages + injects diff, no commit)
   - `commit_and_clean_task` = closure-time (two-commit flow: feature + `chore: close task N`)
   - ZAC enforcement: OpenCode must never run `git add`/`git commit`/`git push` directly
   - Enforcement hook: calling `commit_and_clean_task` before Manager approval = ZAC violation

2. **Version bump:** `<system_version>` 8.0.0 → 8.0.1 (PATCH per SemVer — non-breaking addition of a constraint rule)

3. **CHANGELOG:** New `### Changed` section in `[Unreleased]` with formal entry

### Architectural Reasoning

The ZAC rule was previously documented only in `<bash_phase>` CRITICAL RULE 2, which is only visible during implementation task generation. LLM agents operating in non-implementation contexts (discovery, review, planning) had no visibility into the two-tool lifecycle. The Zen Router incident (Task 13) demonstrated this gap: OpenCode invoked `commit_and_clean_task` during iteration 1 because the constraint was invisible in the top-level rules.

The new rule follows the existing `<constraints>` bullet-point style (`- **Bold:**` with numbered sub-items), keeping the prompt structurally consistent. The rule is placed after `Strict Grounding` (the last existing bullet) and before `</constraints>`, making it the final global constraint — appropriate since it governs a cross-cutting operational concern.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `490cc601e4be2d35fcfad6b93fb718199e93bca1`
<!-- END_GIT_DIFF -->
