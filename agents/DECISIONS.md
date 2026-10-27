# Architectural Decisions: agents

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
