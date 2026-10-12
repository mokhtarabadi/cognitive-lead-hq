# Architectural Decisions: fragments

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-12] ADR-002: Dual-mode Brain XML emission rule

- **Context:** Manual mode needs forced ```xml fences for copy-paste; automatic mode needs bare XML for direct MCP execution.
- **Decision:** Programmer, QA hotfix, and Reviewer postfix personas carry the per-MODE emission rule; bridge extracts both shapes.
- **Consequences:** No re-emit loop in either mode; version bumped with artifact regen.
- **Rollback:** Revert persona wording to prior revision and re-run the assembler.
