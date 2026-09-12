# Milestone 18 Summary

**Date:** 2026-09-12
**Tasks Compacted:** 30

## Source Distribution

| Source       | Count |
| ------------ | ----- |
| orchestrator | 0     |
| telegram     | 0     |
| manager      | 30    |

## Architectural Changes

Milestone 18 spans the Brain-bridge era through release v9.31.0. Core work: unified Brain bridge MCP server with per-task history, context bundle, and file-pull tools; deterministic decision extraction plus alternatives search; transcript compaction with traceability; machine-readable QA verdicts; diff-hash loop guard; golden replay harness; retryable versus fatal transport taxonomy; full-task-file auto-attach; QA and reviewer hunks carriage; planning gate; XML execution autonomy; dual-channel communication; always-English output; voice-to-text normalization; goal lifecycle; spider-search research workflow; persona auto-load; prompt rebuilds from v9.13.0 to v9.31.0; milestone-17 archive; private user-prompts extraction; cleanup sweep deleting paused-automation leftovers; token-optimization spike; systemd unit env fix.

## Files Modified

| File         | Change      |
| ------------ | ----------- |
| CHANGELOG.md | release entries v9.13.0 through v9.31.0 |
| system-prompt.md | regenerated builds up to 9.31.0 |
| prompts/fragments/ | version bumps plus persona, protocol, and constraint edits |
| agents/cognitive-executor.md | autonomy, planning gate, goal lifecycle, bridge wiring |
| mcp-brain-bridge/ | new bridge server plus loop guard and replay harness |
| mcp-decision-server/ | deterministic extraction plus alternatives search |
| skill-templates/ | blowsh research workflow, fintech skill updates, deletions of superseded skills |
| docs/ | brain-bridge runbook, setup, shell strategy, history summaries |
| scripts/qa-rules-gate/ | created then removed as leftover |
| tests/ | bridge, decision, guard, replay, attach suites |
| user-prompts/ | moved out to private repo |
| opencode.json | bridge and decision wiring plus permission denies |
| LLM.txt | setup, plugin, and model-pin docs |
| README.md | bridge reality plus modes and skill counts |

## Criteria Met

| Task | Acceptance Criteria | Status |
| ---- | ------------------- | ------ |
| 150 | RTK practices documented with evidence | ✅ Met |
| 179 | v9.13.0 cut plus milestone-17 archived | ✅ Met |
| 180 | dual-channel plus brainstorm fixes | ✅ Met |
| 181 | execution autonomy plus number discipline | ✅ Met |
| 182 | self-driving QA and reviewer loops | ✅ Met |
| 183 | always-English output | ✅ Met |
| 184 | goal lifecycle | ✅ Met |
| 185 | spider synthesis plus saturation | ✅ Met |
| 186 | spider-search workflow | ✅ Met |
| 187 | persona auto-load | ✅ Met |
| 188 | voice-to-text normalization | ✅ Met |
| 189 | user-prompts extracted private | ✅ Met |
| 190 | unified Brain bridge live | ✅ Met |
| 191 | deterministic extraction | ✅ Met |
| 192 | alternatives search | ✅ Met |
| 193 | file-pull discoverability | ✅ Met |
| 194 | compaction plus traceability | ✅ Met |
| 195 | machine verdicts plus rules gate | ✅ Met |
| 196 | loop guard | ✅ Met |
| 197 | replay harness | ✅ Met |
| 198 | error taxonomy | ✅ Met |
| 199 | persona and fintech research | ✅ Met |
| 200 | full task-file attach | ✅ Met |
| 201 | QA hunks plus modes doc | ✅ Met |
| 202 | planning gate | ✅ Met |
| 203 | self-judgment run | ✅ Met |
| 204 | self-judgment fixes | ✅ Met |
| 205 | nine-note cleanup | ✅ Met |
| 206 | systemd unit env docs | ✅ Met |
| 207 | v9.31.0 plus push script | ✅ Met |

## Individual Task Summaries

### Task 150: Future token optimization research

- **Type:** research
- **Source:** manager
- **Reasoning:** Measured RTK trimming locally and documented practices with evidence tables.

### Task 179: Release v9.13.0 plus milestone-17 archive

- **Type:** feature
- **Source:** manager
- **Reasoning:** Cut v9.13.0 and archived milestone-17 tasks with a manual push script.

### Task 180: Dual-channel communication

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Split concise manager output from comprehensive machine blocks and fixed brainstorming contradictions.

### Task 181: Executor autonomy

- **Type:** feature
- **Source:** manager
- **Reasoning:** Added assume-first autonomy rules and the task-number reference discipline.

### Task 182: Self-driving QA and reviewer loops

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Rejections now auto-emit scoped hotfix XML on the same task file.

### Task 183: Always-English output

- **Type:** feature
- **Source:** manager
- **Reasoning:** Manager-facing text stays simple English regardless of input language.

### Task 184: Goal lifecycle

- **Type:** feature
- **Source:** manager
- **Reasoning:** Heavy tasks run under session goals closed only with evidence.

### Task 185: Spider synthesis upgrade

- **Type:** feature
- **Source:** manager
- **Reasoning:** Added corroboration, ranked synthesis, and saturation stops to the research workflow.

### Task 186: Spider-search workflow

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Encoded the plan, sweep, probe, read, chain, cite loop for the blowsh skill.

### Task 187: Persona auto-load

- **Type:** feature
- **Source:** manager
- **Reasoning:** Added confidence-threshold persona loading and generalized language wording.

### Task 188: Voice-to-text normalization

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Made input normalization an explicit written pipeline step.

### Task 189: User-prompts extraction

- **Type:** feature
- **Source:** manager
- **Reasoning:** Moved personal prompts to a private repo, verified identical before removal.

### Task 190: Unified Brain bridge

- **Type:** feature
- **Source:** manager
- **Reasoning:** Replaced paused automation with one stateful bridge tool plus history and bundle.

### Task 191: Deterministic extraction

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Pinned extraction to byte-identical output with schema checks and cache.

### Task 192: Alternatives search

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Decision queries now also hit the alternatives field.

### Task 193: File-pull discoverability

- **Type:** feature
- **Source:** manager
- **Reasoning:** Documented bundle plus read and grep tools for big task files.

### Task 194: Compaction plus traceability

- **Type:** feature
- **Source:** manager
- **Reasoning:** Long transcripts compact to a digest with per-record metadata.

### Task 195: Machine verdicts plus rules gate

- **Type:** feature
- **Source:** manager
- **Reasoning:** QA ends with a parseable verdict block checked before any judge call.

### Task 196: Loop guard

- **Type:** feature
- **Source:** manager
- **Reasoning:** Repeating identical diffs halt the loop instead of burning turns.

### Task 197: Replay harness

- **Type:** feature
- **Source:** manager
- **Reasoning:** Added hash-scored golden replay for prompt regression checks.

### Task 198: Error taxonomy

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Split retryable failures from fatal client errors on both servers.

### Task 199: Persona and fintech research

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Evidence-grounded surgical edits, no new persona added.

### Task 200: Full task-file attach

- **Type:** feature
- **Source:** manager
- **Reasoning:** Brain always sees whole task working content minus the diff block.

### Task 201: QA hunks plus modes doc

- **Type:** feature
- **Source:** manager
- **Reasoning:** QA and reviewer turns carry the actual diff plus manual versus autopilot docs.

### Task 202: Planning gate

- **Type:** feature
- **Source:** manager
- **Reasoning:** No implementation code without a recorded Brain plan.

### Task 203: Self-judgment run

- **Type:** improvement
- **Source:** manager
- **Reasoning:** System judged itself and fixed the empty-output flake live.

### Task 204: Self-judgment fixes

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Fixed persona overlap and trimmed redundant coverage.

### Task 205: Nine-note cleanup

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Purged pause leftovers and dead docs in one autopilot run.

### Task 206: Systemd unit env docs

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Daemon now reads the repo env file, documented for setup.

### Task 207: Release v9.31.0 with push script

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Cut MINOR 9.31.0 with sync proof and a ready manager-run push script.
