# Architectural Decisions: mcp-lint-server

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-19] ADR-002: Mechanical Prose Gates (Skill Verbs, META Shape)

- **Context:** Prompt-facing prose carried skill invocations the Brain cannot execute (no skill tool, no web, no files) and bundle META files had no structural gate — both bug classes failed silently.
- **Decision:** Add `_check_unactionable_skill_verbs` (Brain-owned `prompts/fragments/` only, registry exempt, Hands-window + boundary + fence + marker exemptions) wired into `lint_markdown` (fragment-scoped) and `lint_system_prompt_sync` (per-fragment scan); add `_check_bundle_meta_structure` (META-only detection, non-META skips with pass) wired into `lint_task_file`.
- **Consequences:** Reworded fragments pass, old wording fails with file-plus-line citations; non-META task files unaffected.
- **Rollback:** Remove the two checks + wiring; prior lint behavior returns.
