# Milestone 23 Summary

**Date:** 2026-10-19
**Tasks Compacted:** 31

## Source Distribution

| Source       | Count |
| ------------ | ----- |
| orchestrator | 3     |
| manager      | 28    |

## Architectural Changes

This milestone rebuilt the Brain bridge and the compaction stack, then hardened language, lint, and bundling on top. Tasks **285–293** made the bridge session-first and lean: a context-sufficiency pack on every planning turn (**285**), singleton report paths under the caller project root (**286**), Magic Compact adoption (**287**) replaced by our V2-native smart-compact plugin (**288**) with an agent-callable `compact_context` tool (**289**), the todolist plugin (**290**), truncated-XML server-side recovery (**291**), the lean session-first refactor (**292**), V2 session-monorepo sync (**293**), session-propagation fixes (**295**), retirement of manager-decision wiring (**296**) and goal-plugin wiring (**297**), the minimal-core simplification (**298**), and a full-brainstorm self-judgment (**299**). Task **12** added the night-mode workflow fragment from the overnight autopilot run.

The META **305** shipped the anti-hallucination harness (bundling 300–304). Tasks **306–307** established Living Folder Docs (README + dated DECISIONS per slice, wired into conventions, fragments, and the executor). The META **313** shipped the unified code-plus-SQL-plus-Markdown knowledge graph (bundling 308–312). Task **314** modularized the context server and enforced ruff formatting. Task **315** made `stage_and_inject_diff` index-safe (`skip_add`, pre-staged warning, `unstage_files`). Tasks **316–317** fixed the Brain bare-XML contract and added the pre-send token budget guard. Task **318** integrated the goal and smart-compact plugins, **319** documented the free-tier bash gate, **321** ran the cognitive tune-up round, **322** set the English-inside language policy, **323** registered project-local skills in AGENTS.md, and **324** synced the goal-tools spec.

The keystone META **325** generalized every Persian/Farsi mention to non-English/requested-language, fixed five unactionable skill references with explicit Hands actors at zero prompt growth, added mechanical lint gates (skill-verb + META-shape), and fixed ten bundle_tasks defects with red-proof tests. Task **284** was the v9.49.0 release ceremony archiving milestone-22.

## Files Modified

| File | Change |
| ---- | ------ |
| `docs/history/milestone-23-summary.md` | new: this 31-task compaction (284–325) |
| `tasks/archive/284-*.md` … `tasks/archive/325-*.md` | released tasks moved to archive (326) |
| `CHANGELOG.md` | 9.62.0 release block (326); [Unreleased] entries (321–325) |
| `prompts/fragments/01-system_version.md` | 9.61.1 → 9.62.0 (326) |
| `prompts/fragments/24-language_policy.md` | Technical-Terms rule (325); skill-actor reword (325) |
| `prompts/fragments/20-communication_examples.md` | non-English handoff example (325) |
| `prompts/fragments/05-user_input_processing.md` | Orchestrator-scoped no-tool boundary (325) |
| `prompts/fragments/11-execution_workflow.md` | Deep Research Loop routed to Hands (325) |
| `prompts/fragments/21-self_improvement_protocol.md` | Hands actor for task-generator (325) |
| `prompts/fragments/13-constraints.md` | non-English wording (325) |
| `agents/cognitive-executor.md` | Technical-Terms + no-tool boundary (325) |
| `docs/conventions.md`, `AGENTS.md`, `README.md` | non-English generalization (325) |
| `skill-templates/telegram-issue-sync/SKILL.md` | non-English wording (325) |
| `skill-templates/bundle-tasks/SKILL.md` | non-English wording + 2-6 floor + duplicate errors (325) |
| `mcp-context-server/gitops.py` | Unicode docstring + locate/collision/checksum/status fixes (325) |
| `mcp-context-server/server.py` | atomic bundle write + rollback restore + validation (325) |
| `mcp-lint-server/server.py` | skill-verb + META-shape gates (325) |
| `mcp-brain-bridge/*` | session-first lean refactor + budget guard (285–298, 317) |
| `mcp-context-server/*` | singleton paths, modularization, graph, index-safe staging (286, 313–315) |
| `system-prompt.md` | regenerated each bump through 9.62.0 (326) |
| `tests/test_bundle_tasks.py` | 11 red-proof tests, 18 green (325) |
| `tests/test_prompt_sync.py` | version pin 9.62.0 (326) |

## Test Evidence

- `test_prompt_sync.py`: 14 checks green, byte-identical rebuild.
- `test_bundle_tasks.py`: 18 passed (7 baseline + 11 new, 9-failed red proof recorded).
- `test_mcp_servers.py`: 34 passed; 53 environmental failures (missing pathspec/yaml in lint env) + 1 split round-trip failure, all pre-existing on pristine HEAD — not gating.
- Residual greps: zero Persian/Farsi and zero unactionable skill verbs in operating prose.
