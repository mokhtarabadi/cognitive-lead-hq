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

# Architectural Decisions: agents

## Discovery-fed retries must ground with bodies, not prose

Date: 2026-11-06
Status: accepted
Context: A planning loop stalled with two consecutive `missing_context` answers. The Hands had fed citation-style prose (file paths with lines, no bodies) per the Discovery-fed wording, but prose-about-code cannot satisfy the Brain's No-Hallucination + Strict Grounding rules, so the second request was contractually correct and the loop hit its stop signal. The bridge's `context_paths` reader (server-side bodies, caps, `#L` slices) sat unused on the retry turn.
Decision: The executor's Discovery-fed planning section now binds the retry to verbatim code (capped ranges pasted inline) and/or `context_paths=[paths]`; a prose-only `[fed-context]` is a protocol violation that predicts its own second `missing_context`. The File context retrieval line mirrors the rule. A prompt-sync regression test fails if the sentences disappear.
Consequences: Fed retries arrive verifiable, so planning turns ground instead of re-requesting. Retry prompts grow by the quoted ranges; the existing caps and slices bound that cost.
Rollback: Revert the two paragraphs and the regression test; the stall behavior returns.

## Implementation Delegation Lane Beside Discovery

Date: 2026-10-28
Status: accepted
Context: Subagent Delegation covered read-only context discovery only. Implementation splits across subagents had no lane: no ownership rule, no verification duty, no stop condition on overlap.
Decision: Add "Subagent Delegation for Implementation" under the discovery section, unchanged otherwise: disjoint per-lane file lists, shared-nothing lanes, Hands verifies every lane gate after merging with per-lane evidence, overlap stops and reports. Single-file, coupled, and sequential work stays with the Hands by rule.
Consequences: The executor owns the full delegation contract; the shipped prompt stays free of lane machinery per the plugin-blind split.
Rollback: Delete the lane section; discovery delegation is unaffected.

## Brain results are returned whole, never field-shaped

Date: 2026-10-27
Status: accepted
Context: The Brain Bridge's Code-mode output discipline told the Hands to "return `{status, block_count: xml_blocks.length, model}` and keep the block whole instead of printing a prefix". The intent was to stop the model printing a truncated prefix of a large XML block, but the recipe licensed dropping the payload: a turn returning only `output` lost `xml_blocks`, and a turn returning only `blocks` lost `output`. The executed instructions were complete, yet the transcript and the agent's next turn held less than the server returned, so an audit could no longer see what the Brain actually said.
Decision: Replace the paragraph with a return-the-payload-whole rule: always return `status`, `output`, `xml_blocks` and any diagnostic/`truncated` field exactly as received, never slice, map, summarize or field-shape a `brain_turn` result, and manage size before the call with `compact_context`, a leaner prompt or `include_bundle=false`. The only acceptable cut is the runtime's own `maxOutputBytes`, which announces itself with `truncated: true` and requires re-reading the exact range. A prompt-sync test fails if the rule disappears or `block_count` returns.
Consequences: Every plan, verdict and XML block stays verbatim in the transcript, so a later turn or a reviewer can re-read it. The cost is a larger tool result per Brain turn; the pre-call tools absorb that, and the rule keeps the echo out of chat, where the plan presentation contract governs what the Manager sees.
Rollback: Restore the previous paragraph and drop the test; the trimmed-return behaviour returns.

## Plan approval shows the plan, not just the question

Date: 2026-10-26
Status: accepted
Context: The Manager received approval cards with nothing to approve. The executor told the Hands that in autopilot the Manager "sees only Relay questions and the final verdict report", the preflight asked for "one narrow question", and no paragraph required the plan body — which the Brain already returns in `output` — to reach either the chat or the question payload. The plan was available and got dropped at presentation time.
Decision: Add a Plan presentation contract to the executor: the full plan text goes into the assistant message before the `question` call, the question body repeats it, a bare ask is a protocol bug, and a revision round prints the revised plan in full before asking again. Fix the autopilot sentence so it names the plan as visible, and treat a plan that arrives as `REPORT` as a plan to surface rather than a verdict to file. Bind the preflight plan-gate sentence to the same contract. A regression test in `tests/test_prompt_sync.py` fails if the contract disappears or the suppressing sentence returns.
Consequences: A plan-approval card can no longer arrive without the plan. The plan text is duplicated on purpose — chat plus card — because a client may render only one of the two surfaces. No bridge code change: the bridge already delivers the plan in `output`, and a code validator over UI wording would add coupling without safety.
Rollback: Revert the executor paragraphs and the regression test; the previous behaviour returns.

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## Plugin lane contract and the tracked idle-loop brake

Date: 2026-10-21
Status: accepted
Context: The context executor is the agent's own instruction file, so it is where the Hands learns which plugins it owns. Its goal boundary named only two goal writes and never `goal_set`, cited a `src/loop.ts` range that holds neither the gate nor the handler, claimed the stop file is read at the project root when the code reads only the projectDir `.opencode/STOP_GOAL` path, and asserted a rule the plugin does not enforce anywhere. Because the goal plugin registers its idle handler for every project it loads, opening a goal inside HQ could let the plugin inject continuation prompts that fight the Brain Bridge.
Decision: Correct the citations to the real ones, replace the prompt-enforced idle ban with the honest description of what the plugin does, add the missing `goal_set` create trigger and the task-boundary compaction trigger, and ship a tracked `.opencode/STOP_GOAL` marker so the brake is a committed control rather than a local accident. The marker brakes only the idle loop and never blocks the five agent tools.
Consequences: The executor's goal lifecycle is three writes plus resume, the compaction lane covers the task boundary, and the idle loop stays silent in HQ by an actual mechanism instead of a promise. The root `STOP_GOAL` stays git-ignored; the `.opencode/STOP_GOAL` path is negated in `.gitignore` so the marker is tracked.
Rollback: Revert the executor wording and the `.gitignore` negation, delete the tracked marker, and re-run the assembler.

## Lanes consolidated in the executor, prompt goes blind

Date: 2026-10-21
Status: accepted
Context: The lane surface first landed split across the prompt fragments and the executor, which still taught the Brain plugin machinery. The Manager ordered full separation: the prompt emits only a plan and checklist, the executor owns every lane.
Decision: Move the remaining lane knowledge (exact tool signatures, WHEN triggers, evidence-gate and busy-lease strings, todolist caps, compact parameter contract, the Brain-has-no-tools WHY) into the executor's Goal Boundary, Micro-Task Tracking, and Compaction sections, and strip the same knowledge from the prompt fragments.
Consequences: The executor is the single file the Hands needs for which plugins it owns, how to call each, why, and when. The prompt carries zero tool names.
Rollback: Revert the executor sections and restore the fragment wording, then re-run the assembler.

## Prompts are for the LLM, not the auditor

Date: 2026-10-21
Status: accepted
Context: The executor carried file and line citations into the Goal Boundary. Those pointers serve human audits, but the executor is read by the agent every turn — for the LLM they are unverifiable noise.
Decision: Strip every code reference (source files, line ranges, server paths) from the executor, keeping all tool names, signatures, triggers, caps, and error strings. History records (DECISIONS, CHANGELOG, task files) keep their citations; the lane tests now assert the absence of code references in the executor.
Consequences: The executor reads as behavior only. A regression that re-adds a pointer fails the prompt-sync gate.
Rollback: Restore the citations from git history.

## Free-tier bash gate documented

## Subagent Delegation Names the Session Tool

Date: 2026-10-27
Status: accepted
Context: The executor told the Hands to delegate discovery "using your `task` tool". No tool by that name exists in the session; delegation runs through the `subagent` tool. The sentence was inherited from another runtime's vocabulary.
Decision: Name the `subagent` tool explicitly. One-word-class fix; delegation targets and the 4-agent cap are unchanged.
Consequences: The delegation instruction resolves to a real tool. No behavior change beyond the name.
Rollback: Restore the prior sentence from git history.
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

## Prompt-refactor matrix row gains the execute pass

Date: 2026-11-02
Status: accepted
Context: The Skill Auto-Loading Matrix bound prompt-refactor to validate-translate-expand-structure with no execute step, and the Direct Input pipeline ended at Plan & Halt, so a refactored prompt had no instruction carrying it into execution.
Decision: Extend the matrix row to validate-translate-expand-structure-then-execute and add the After-Deliver execute sentence to the Direct Input protocol: the formatted prompt runs as the live instruction under plan approval, Zero-Autonomous-Commit, QA, and closure gates.
Consequences: Refactor-then-execute is one bound pass; Step 2 cannot authorize commit or push.
Rollback: Restore the prior matrix cell and drop the Direct Input sentence.

## Unified Context Manifest and Code Mode Tool Execution Protocol

Date: 2026-11-06
Status: accepted
Context: Discovery returned prose summaries, the Hands fed prose `[fed-context]`, and the Brain correctly re-emitted `missing_context` — a grounding deadlock. Separately the bridge accepted `context_paths` but the sufficiency check ignored server-side `[path-injected:` bodies and the combined prompt dropped the rendered paths block, so grounded turns were falsely warned.
Decision: Discovery ends every report with one canonical machine-readable `### Context Manifest` (`Context-Paths:` with one `- path/to/file.ext#Lstart-end` entry per path, no bracketed inline-list alternative); the executor extracts it into `brain_turn(context_paths=[...])`, documents the Code Mode Tool Calling Protocol (`tools.<server>.<tool>` via `execute`), and normalizes non-English input to technical English before planning. The bridge folds rendered paths into the diagnostic prompt and grounds on an explicit server-derived flag, so a user-typed marker cannot spoof it. Fragments, system role, and `AGENTS.md` drop the Manager-as-courier model; prompt rebuilt to `9.71.0`.
Consequences: Fed retries arrive verifiable; sufficiency warnings fire only on truly ungrounded plan turns. Prompt-sync tests pin the canonical manifest structure, the discovery-summary parity, and the Code Mode section; bridge behavioral tests pin spoof-vs-rendered grounding.
Rollback: Revert the agent/fragment/bridge hunks, restore the version fragment, rebuild the prompt, and drop the new tests.

## Hands-driven QA/review chaining in both modes (QA round 2)

Date: 2026-11-06
Status: accepted
Context: The courier-model cleanup left manual-mode instructions telling the Manager to copy task files and QA/review prompts between the Hands and the Brain (both 09 summaries, the QA/Reviewer/Architect personas, the 02 role delivery line, and the 19 MODE declaration), while the executor already assigns `brain_turn` invocation to the Hands in both modes with the Manager gating approvals only.
Decision: The Hands invokes QA/review turns itself in manual mode too; the Manager only gates approvals and Relay questions. Fence expectations for manual XML delivery stay. A prompt-sync test fails on any Manager-ferries-task-text wording in the shipped prompt. No version change (still 9.71.0).
Consequences: One handoff contract across modes; manual turns no longer stall on human ferrying. Follow-up done under O1: the root notify step now reports the staged `tasks/qa/` path with QA/review chained.
Rollback: Restore the Manager-copy sentences from git history and drop the handoff test.

## Manual mode line + mismatch active voice (QA round 4 follow-up)

Date: 2026-11-06
Status: accepted
Context: The manual `brain_turn` mode line still ordered copy-paste relay output, and the combined mismatch summary used passive voice ("is chained") without directing the Hands to call.
Decision: Manual mode line forbids task-ferrying relay text and names Hands-direct QA/review invocation with approvals-only Manager role, mirrored in the mode-line memory shard and the bridge runbook. Mismatch summary converted to active voice. Handoff test extended to forbid the old mode-line phrase and pin the active-voice sentence. No version change.
Consequences: Emission contract matches the handoff contract in both modes.
Rollback: Restore the prior mode-line sentences and the passive mismatch line; drop the added assertions.

## Mismatch branch directs the invocation (QA round 5, autopilot O1)

Date: 2026-11-06
Status: accepted
Context: The combined mismatch summary output a sentence claiming a revised-plan turn was chained, without directing the Hands to invoke `brain_turn` with the discovery manifest first.
Decision: The branch now orders the Hands to invoke the revised-plan turn with the manifest via `context_paths` before stopping with the status message. The handoff test pins the directive sentence. No version change.
Consequences: A halted combined task always produces a grounded replan turn instead of an ungrounded claim.
Rollback: Restore the claim-only sentence and drop the directive assertion.

## Conditional/summary mismatch paths reconciled (QA round 6, autopilot O1)

Date: 2026-11-06
Status: accepted
Context: The conditional OTHERWISE path ordered halt-and-output-path while the summary halt branch ordered invoke-with-manifest — two incompatible next actions for the same mismatch.
Decision: Both paths direct the Hands to invoke the revised-plan turn with the discovery manifest via `context_paths`. The handoff test pins both sentences and forbids the old output-path wording. No version change.
Consequences: One unambiguous mismatch behavior across the combined template.
Rollback: Restore the output-path sentence and drop the new assertions.

## DONE follows the QA/review chain (QA round 7, autopilot partial O1)

Date: 2026-11-06
Status: accepted
Context: The implementation summary declared DONE right after the QA transition while the chaining step came after, permitting an early halt before QA/review.
Decision: Step 4 now marks implementation complete with an explicit continue; a final step declares DONE only after the QA/review turn is invoked. The handoff test pins the order. The round-7 marker-provenance claim (inline `[fed-context]` spoofing) is disputed — see the task log for evidence — with no behavior change. No version change.
Consequences: The summary sequence cannot terminate before the chain runs.
Rollback: Restore the early DONE sentence and drop the order assertion.
