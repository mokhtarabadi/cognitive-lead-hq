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

<!-- provenance: tasks/in-progress/422-regenerate-stage-prompts-every-release.md -->

## [2026-11-24] ADR-003: Stage prompts are release artifacts, not optional copies

- **Context:** A version bump left every stage artifact on the previous release while the loader accepted any existing artifact. The full prompt looked current, but stage-scoped Brain turns silently used retired rules.
- **Decision:** Treat the full prompt and every declared stage artifact as one release set. Regenerate both, compare exact bytes with the freshness gate, and deploy both. Generated stage files remain ignored; the executable gate is the enforcement.
- **Consequences:** A release that skips stage regeneration now fails loudly. Stage scoping survives while artifacts are fresh, and a stale artifact can no longer override the current full prompt.
- **Rollback:** Revert the gate and release-script changes, decrement the version marker, and regenerate from the current fragments.
