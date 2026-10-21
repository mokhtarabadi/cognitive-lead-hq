# Architectural Decisions: tests

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-21] ADR-002: Pin the plugin lanes, not just the compaction protocol

- **Context:** The prompt-sync suite pinned the compaction literals but no goal or todolist literal, so the two lanes that never fired were also the two lanes nothing guarded. A lane that can silently disappear from the assembled prompt is exactly the failure this task set out to remove.
- **Decision:** `test_shipped_prompt_is_plugin_blind` fails on any tool name, plugin name, state path, or channel tag leaking into the assembled artifact, and `test_executor_owns_all_three_plugin_lanes` pins the full lane surface (signatures, caps, stop-marker path, corrected line references) in the context executor; the obsolete compaction-protocol presence test is removed.
- **Consequences:** A regression that drops a lane trigger or restores a stale citation fails the blocking gate instead of shipping silently.
- **Rollback:** Remove the two test functions; no production code depends on them.
