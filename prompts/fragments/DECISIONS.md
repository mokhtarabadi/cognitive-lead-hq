## Unify Architecture to 100% Brain Turn and Permanently Eliminate Manual Mode

Date: 2026-11-08
Status: superseded by "Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)"
Context: Maintaining dual modes (manual courier copy-pasting vs autonomous brain_turn) introduced prompt bloat, mode confusion, and human friction.
Decision: Permanently eliminate manual mode across all prompts, agents, protocols, and documentation. The platform operates 100% autonomously via `mcp-brain-bridge` (`brain_turn`). The Manager is strictly executive supervisor, never a courier.
Consequences: Zero copy-paste prompt templates survive; all turns chain directly through brain_turn.
Rollback: Revert to 9.77.0 prompt fragments.
Superseded-By: "Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)" (2026-11-08)
Superseded-Reason: The decouple ADR restored manual mode as a first-class topology; this ADR's "permanent elimination" claim was reverted but never marked superseded, creating a contradiction in the decision log.

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

## [2026-11-06] ADR-008: Hands-owned automatic review chaining

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

## [2026-11-18] ADR-010: Mirror the OpenUI validity gate into the Brain prompt

- **Context:** The executor agent learned an OpenUI pre-render check, but the Brain that emits hands tasks had no matching rule, so an emitted task could still request a malformed `Table` program. A nested array cell in a real render call produced an arity-style diagnostic that pointed at the wrong layer.
- **Decision:** Add a `MANAGER-FACING RENDER CONTRACT` paragraph to `09-hands_protocols.md` carrying the same signatures, plain-cell rule, bracket balance, named-argument ban, and diagnostic interpretation as the executor's gate. Bump the version fragment `9.89.0` → `9.90.0` and regenerate both `system-prompt.md` and the stage artifacts with the assembler.
- **Consequences:** Brain and Hands read the same validity contract. A drift in either surface is caught by `test_openui_validity_gate_in_executor_and_fragment` and the assembler byte-identity gate.
- **Rollback:** Remove the paragraph, restore the version fragment, regenerate the artifacts, and drop the regression assertions.

## [2026-11-22] ADR-011: Pin the render call envelope in the Brain prompt

- **Context:** A render call failed before the program was ever parsed because `parameters` was sent as a JSON string. The Brain prompt mirrored the program gate but had no envelope rule, so an emitted task could still request a malformed call.
- **Decision:** Extend the `MANAGER-FACING RENDER CONTRACT` with the `action: "render.page"` / `parameters`-object shape, the object-not-string rule, one-payload rule, and the rebuild-on-`Expected object` directive. Bump `01-system_version.md` 9.90.0 to 9.90.1 and regenerate `system-prompt.md` and the stage artifacts.
- **Consequences:** Brain and Hands read the same envelope contract. A drift in either surface fails `test_render_call_envelope_in_executor_and_fragment` and the assembler byte-identity gate.
- **Rollback:** Remove the added sentences, restore the version fragment, regenerate the artifacts, and drop the regression test.

## [2026-11-22] ADR-012: META 417 context map, plan gate, and topology reconciliation

- **Context:** The 67-finding audit (24 HIGH) showed the Brain plans from assumed context when no map is attached, the Hands can self-approve a plan on direct input, and five surfaces assert different topologies.
- **Decision:** Context Map contract in fragments (turn classes, audit line, 09 per-turn classes, worked examples for the placeholder ban); direct-input plan gate in `05` and Brain context-before-plan rule in `08`; topology reconciliation (superseded-note, single finalization sequence, Personas Roster rebind); approval-literal consolidation with `13-constraints.md` canonical; fragment scope note (20 ship, 10/17/22/23 absent). Version fragment 9.92.0, prompt regenerated, 14 new regression assertions.
- **Consequences:** Fragments carry the map, the gate, one topology and one approval home. Dedupe recorded per finding; persona full-compression and executor playbook-split deferred with rationale (no Brain playbook loader; unique rules single-homed).
- **Rollback:** Revert the fragment edits, restore the version fragment, regenerate the artifacts, and drop the 14 new regression assertions.

## [2026-11-22] ADR-013: Second QA round — closure correction and four assertions

- **Context:** Second QA rejected on the closure step ordering `qa_transition` at closure, the roster pointer naming unreadable paths, and the ADR-012 count line. The fix also added tag-balance, fragment-path, closure-scope and count-agreement assertions.
- **Decision:** Closure step orders commit only; roster seats are inline with no path pointers; ADR-012 keeps 14/14 while the suite total moves to 62 with the 4 QA-round assertions.
- **Consequences:** `test_qa_transition_absent_from_closure_step`, `test_assembled_prompt_has_no_fragment_paths`, `test_validation_blocks_not_collapsed` and `test_adr_test_counts_agree` pin the second-round defects.
- **Rollback:** Revert the closure bullet, restore the roster pointer, restore the version fragment, drop the 4 QA-round assertions, and regenerate.
- **Forward reference:** The suite total moved to 66 in the O1 round, recorded in ADR-014.

## [2026-11-22] ADR-014: O1 scoped round — four assertions and the final suite total (superseded by ADR-015)

- **Context:** ADR-013 recorded 62 after the second QA round. The Manager-authorized O1 round added four assertions (example-presence, closing-tag column, approval single-home, staging-tool role) and corrected the ADR-012 version anchor. The fragments log carried no entry for that round, so its total predated the shipped suite.
- **Decision:** Record the O1 round here. The suite total is 66 assertions: 44 pre-existing plus 14 plan-round plus 4 second-round plus 4 O1-round. ADR-013's 62 is a true round snapshot and stays as written.
- **Total superseded:** The O1 round closed at 66 assertions. The reopen round added four more, so 66 is not the current total; ADR-015 records the delta and the task file's `## Verification Evidence` records the collected count.
- **Consequences:** The fragments log and `agents/DECISIONS.md` now state the same current total. The O1 round changed fragments `09`, `05`, `07`, `08`, `20` and the reviewer persona plus ADR-012's version anchor, so the assembled prompt was regenerated; the count is what this entry reconciles.
- **Rollback:** Delete this entry and restore the previous suite total in any surface that cites 66.
- **Follow-up:** Example B now models the exact-command rule that Example A already modelled (postfix round two).

## [2026-11-23] ADR-015: Reopen round - model-line policy and forced formatting

- **Context:** The shipped `03-system_context.md` carried a Meta/Muse-Spark cutoff claim, a dated verification anchor and a hardcoded current year, all mutable state inside the cached system prefix (audit A3). Separately the project formatter covered only Python and referenced a binary absent from PATH, so no code or doc was reliably auto-formatted.
- **Decision:** Rewrite `03-system_context.md` to name the active model line and drop the Meta/Muse reference, the dated anchor and every year literal, leaving current-source verification as the path. Route all formatting through `scripts/format-guard.sh` from `opencode.json`, with `.prettierignore` as the shared exclusion source. Bump the version fragment to 9.93.0 and regenerate the prompt.
- **Suite total:** ADR-014's 66 plus four reopen-round assertions: ignore-file scope against the guard, guard arms against the ignore file, extension parity against `opencode.json`, and sibling `Decisions:` path resolution for `scripts/*.sh`. The collected count lives in the task file's `## Verification Evidence`.
- **Consequences:** The system prefix carries no current-date or cutoff-year claim, so it does not expire on a fixed boundary. Prompt fragments, the assembled prompt, stage artifacts and task files are excluded from both the formatter and the format gate.
- **Rollback:** Restore the prior `03-system_context.md`, restore the `ruff-format` formatter entry, delete `.prettierignore` and the guard, restore 9.92.0, and regenerate.

## [2026-11-23] ADR-016: Discovery manifest shape aligned across four surfaces

- **Context:** The reopen round moved three surfaces onto a discovery manifest whose first content line is a persisted tree report path: the discovery agent's Context Manifest block, its How to Work step 2 and the `agents/README.md` invariant, with `skill-templates/code-search/SKILL.md` already agreeing. The discovery summary phase in the protocols fragment still prescribed a two-line shape with no tree line, and the audit line's `tree=<path>` slot depends on exactly that value, which the executor treats as mandatory beside the mode line.
- **Decision:** Align the discovery summary phase to the four-surface shape, naming the `Tree:` line and its role as the source of the audit line's tree slot. Add one sentence to the worked-examples preamble stating that the examples are prompt text, so their unwrapped outer blocks are not a contradiction of the four-backtick emission rule. Hold the version at 9.93.0, because a bump is owed per shipped change rather than per rebuild inside one unreleased change.
- **Consequences:** All four manifest surfaces state one shape, and the tree path has a named home for the audit line. The worked examples stay authoritative for the placeholder ban without modelling a forbidden emission. Four residuals (I33-I36) plus one audit-line observation (I37) remain open as documentation debt.
- **Rollback:** Restore the prior discovery summary sentence, drop the preamble paragraph, restore version 9.92.0 and regenerate.

<!-- provenance: tasks/in-progress/423-portable-release-omitted-output-brain-skill.md -->
## [2026-11-24] ADR-017: Brain orchestration becomes a portable skill

- **Context:** Brain's participants, seats, stages, modes, gates, and output-recovery paths were spread across runbooks and prompt fragments, making correct use dependent on memorizing internal files.
- **Decision:** Register a Brain orchestration skill that distills the deployed contract. Its authority wording names the deployed runbook and stage manifest rather than HQ repository paths after the portability rule check.
- **Consequences:** Agents and downstream projects can load one skill to plan, implement, brainstorm, test, review, and close work without inventing tools or bypassing approval gates.
- **Rollback:** Remove the registry row and template, decrement the version marker, regenerate prompts, and re-run the registry and portability tests.
