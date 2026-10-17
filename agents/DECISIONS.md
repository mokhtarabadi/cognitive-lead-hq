# Architectural Decisions: agents

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## Free-tier bash gate documented
Date: 2026-10-17
Status: accepted
Context: Upstream free-tier models discriminate by request-body tool list. Agents omitting bash receive 403 FreeTierError on free-tier models.
Decision: Document bash requirement in agent docs. Add free-tier smoke test to the review checklist. Make no permission changes.
Consequences: Agents intended for free-tier use keep bash. Hardening uses prompts and review, not tool removal.
Refs:
- https://github.com/anomalyco/opencode/issues/50627
- https://github.com/anomalyco/opencode/issues/53347
- https://github.com/anomalyco/opencode/issues/53885
- https://github.com/anomalyco/opencode/issues/54744
- https://github.com/anomalyco/opencode/issues/52880
- https://github.com/anomalyco/opencode/issues/49592
