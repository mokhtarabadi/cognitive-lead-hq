## Unify Architecture to 100% Brain Turn and Permanently Eliminate Manual Mode

Date: 2026-11-08
Status: accepted
Context: Maintaining dual modes (manual courier copy-pasting vs autonomous brain_turn) introduced prompt bloat, mode confusion, and human friction.
Decision: Permanently eliminate manual mode across all prompts, agents, protocols, and documentation. The platform operates 100% autonomously via `mcp-brain-bridge` (`brain_turn`). The Manager is strictly executive supervisor, never a courier.
Consequences: Zero copy-paste prompt templates survive; all turns chain directly through brain_turn.
Rollback: Revert to 9.77.0 prompt fragments.

## Comprehensive Repository Audit: Purge Contradictions, Phantoms, and Cruft

Date: 2026-11-08
Status: accepted
Context: Over months of active evolution across 23 milestones, the repository accumulated historical drift, obsolete references, and redundant clauses across documentation and codebases.
Decision: Systematic audit across 5 domains (Prompts, Agents, Specifications, Skill Templates, FastMCP Servers). Fixed 25 findings: created missing docs (architecture.md, data_model.md), registered memory/web tools in capability.py, purged DSP violations, fixed broken citations, harmonized version references, updated permissions.
Consequences: Zero phantom references, all citations resolvable, system prompt reassembled cleanly at 9.77.0.
Rollback: Revert individual file changes per ADR.

## Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)

Date: 2026-11-08
Status: accepted
Context: Version 9.71.0 inadvertently conflated manual and automatic modes by stating the Hands calls brain_turn directly in both modes and the Manager never ferries task text. This broke the workflow for external web Brain interfaces where no MCP bridge exists.
Decision: Decouple the topologies cleanly: MODE: manual restores the human courier model (Hands emits fenced prompts/paths, Manager copies to external Brain, Brain emits fenced XML, Manager copies to Hands). MODE: automatic maintains the 100% headless MCP bridge via brain_turn where Manager never ferries text.
Consequences: External web Brains and local MCP agents can both operate without protocol collisions.
Rollback: Revert to 9.75.0 prompt fragments.

# Architectural Decisions: fragments

## [2026-10-28] ADR-006: Parallel Mandate Gains Implementation Triggers

- **Context:** The Parallel Agent Execution Mandate fired only on file scans, signature extractions, and decoupled module changes — discovery work. R&D questions and implementation splits had no trigger, no ownership rule, and no merge protocol, so parallel execution outside discovery was either guessed at or avoided.
- **Decision:** Append implementation & R&D triggers (disjoint files, independently verifiable lanes, independent research questions), a disjoint-ownership partition rule (overlap means stop-and-report), and a verify-and-merge protocol (Hands re-runs every lane gate, per-lane evidence, unverified lane blocks). Discovery wording untouched; single-file and coupled work stays single-threaded by rule.
- **Consequences:** Parallel splits outside discovery have an explicit contract instead of Manager reminders. Version bumped with artifact regen.
- **Rollback:** Revert the appended bullets and re-run the assembler.

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

## [2026-10-21] ADR-003: Plugin lanes become executable contract, not prose

- **Context:** The goal, todolist, and smart-compact plugin lanes were described in trailing prose outside every task template, so nothing ever triggered them. `goal_set` had no create trigger at all and the goal lane was unreachable; the todowrite rule fired only for implementation checklists; the task-boundary compaction trigger was missing; and several citations named code that does not exist at the stated lines.
- **Decision:** Each lane becomes an executable step inside the task templates it belongs to — Lane G (goal) in the implementation template, Lane T (todolist) in the implementation and combined templates, Lane C (smart-compact) in the compaction protocol — each carrying its exact tool names, parameters, WHEN trigger, error strings, and forbidden actions. The Brain states its tool-less boundary in the persona fragments and expresses intent through a `plugin_directives` sub-block carried inside the XML it already emits, so no bridge allowlist change is needed. Stale citations were replaced with the real ones: the idle gate at `src/loop.ts:458-492`, the handler at `src/loop.ts:552-853`, and the stop file read at `src/index.ts:284-296`.
- **Consequences:** The three lanes fire on a stated trigger instead of a Manager reminder, the Brain-to-Hands intent path is deterministic rather than prose, and the prompt text matches the plugin source. Version bumped and the artifact regenerated.
- **Rollback:** Revert the fragment and persona wording to the prior revision and re-run the assembler.

## [2026-10-21] ADR-004: The system prompt goes plugin-blind; the executor owns the lanes

- **Context:** Review of the lane design showed lanes inside the prompt still teach the Brain plugin machinery, which contradicts the Brain/Hands split. The Manager ordered the knowledge moved: the prompt emits only a plan and checklist, the executor maps them onto tools.
- **Decision:** Remove the plugin-directives schema, the lane blocks, and the trailing goal note from the Hands protocol fragment; rephrase both persona mandates to todo-list (micro-list) language with a single context-executor boundary sentence; archive the compaction fragment out of the manifest and the splitter tag list; expand the executor with the full lane surface (signatures, triggers, error strings, caps, parameter contract) instead.
- **Consequences:** The assembled prompt shrinks and carries zero tool names; the lane tests assert absence in the prompt and presence in the executor.
- **Rollback:** Restore the archived fragment to the manifest and tag list, revert the persona and protocol wording, and re-run the assembler.

## [2026-10-27] ADR-005: Prompt Names Only Tools That Exist

- **Context:** Fragments named a `nodejs-express` skill that was never created, `@explore`/`@general` subagents that exist in no roster, and `view_file`/`apply_patch` native tools outside the session toolset. The Hands cannot call what does not exist.
- **Decision:** Name `node-hexagonal-api`, the `cognitive-discovery` subagent, and the native `read`/`edit`/`write` tools. A prompt-sync test fails on any reintroduced phantom name.
- **Consequences:** Every tool the shipped prompt names resolves in the session. Version bumped with artifact regen.
- **Rollback:** Revert the fragment wording and re-run the assembler.

## [2026-11-02] ADR-007: Prompt-refactor becomes two-pass Refactor-then-Execute
- **Context:** The prompt-refactor skill ended at Deliver (output the formatted prompt in a code block) with no Execute pass, so the refined prompt stalled as an artifact instead of running as the live instruction.
- **Decision:** Retitle the workflow Two-Pass Refactor-then-Execute: Step 1 refactors (validate, translate, expand, structure), Step 2 executes the formatted prompt in the same session under the existing gates (plan approval, Zero-Autonomous-Commit, QA, closure). Mirror one-line execute clauses in the input-processing gate, the executor matrix and Direct Input protocol, the skills registry, and the language policy execution binding.
- **Consequences:** Refined prompts execute instead of stalling; Step 2 cannot bypass gates, auto-commit, or push. Version bumped with artifact regen.
- **Rollback:** Restore the four-step workflow wording, drop the mirror lines, and re-run the assembler.

## Hands-owned automatic review chaining

Date: 2026-11-06
Status: accepted
Context: The QA and Code Reviewer instructions assigned `brain_turn` chaining to the Brain while also assigning calls to the Hands. The Brain has no direct tool access.
Decision: In automatic mode, the Hands invokes the next QA, re-QA, or review `brain_turn` under the same `task_id`. The Manager does not ferry task text and retains the approval gates.
Consequences: Both review personas assign the next call to the actor that can execute it. Regression assertions pin the Hands-owned wording.
Rollback: Restore the Brain-owned automatic-mode overrides and remove the corresponding assertions.

## [2026-11-12] ADR-009: The Brain Prompt Carries Only the Personas of the Current Stage

- **Context:** Every `brain_turn` shipped all seven persona blocks, so a QA turn read the Sprint Strategist rules and a review turn read the QA rules. Measured on 2026-11-12, a connectivity ping consumed 20278 input tokens before the question was even seen, and the persona definitions competed for attention with the seat actually doing the work.
- **Decision:** Split the persona block into an always-shipping catalog (`06-personas-catalog.md`, holding the `<personas>` wrapper and the `<auto_load>` rules) and one verbatim slice per seat (`personas/<slug>.md`). Route by stage through `prompts/stage-manifest.json`, which is the single table read by both the assembler and the bridge. `plan` carries the five planning seats, `implement` and `closure` the Senior Programmer, `qa` the QA Engineer, `review` the Code Reviewer, `brainstorm` all seven, and an absent or unknown stage the full prompt. A known stage whose artifact is missing falls back to the full prompt, never to an empty prompt.
- **Consequences:** The QA prompt is 17% smaller, implement and review 16%, plan 7%, and brainstorm unchanged because it already carried every seat. The split is byte-identical for the full prompt: the assembler re-splices the slices and reproduces the committed artifact exactly. The `<panel>` sentence in `12-brainstorming_protocol.md` no longer says "seven personas" because the roster is now stage-scoped. Version bumped with artifact regen.
- **Rollback:** Restore `06-personas.md` from git, delete `prompts/fragments/personas/` and `prompts/stage-manifest.json`, drop the `stage` parameter from `load_system_prompt`, and re-run the assembler.

