# Architectural Decisions: prompts

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-11-23] ADR-002: Canonical Manager-Facing Concision Contract

- **Context:** The same answer-first rule and competing numeric length budgets existed in four shipped places, so agents optimized locally and produced verbose, inconsistent handoffs.
- **Decision:** One canonical Manager-Facing Concision Contract in the constraints fragment, mirrored verbatim into both cognitive agents; duplicate restatements retired; audited counts and vague modality corrected in the same pass; version bumped 9.93.0 → 9.94.0 and the artifact regenerated.
- **Consequences:** User-facing replies shorten to answer, reason, next action with a five-bullet ceiling; internal channels and verbatim pipeline strings are explicitly exempt.
- **Rollback:** Revert the fragment and the two agent files, decrement the version marker to 9.93.0, regenerate, and re-run both lints and the byte comparison.
