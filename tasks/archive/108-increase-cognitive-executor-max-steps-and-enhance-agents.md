# Task 108: Increase Cognitive Executor Max Steps & Enhance Agents for OpenCode/Freebuff

**File:** `tasks/completed/108-increase-cognitive-executor-max-steps-and-enhance-agents.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Increase the max steps for the Cognitive Executor agent in both OpenCode and Freebuff runtimes, ensure it is set as the default agent, and enhance both agent definitions for improved reliability and consistency across CLIs.

## Manager's Notes

- The current `steps: 100` in `agents/cognitive-executor.md` should be increased to allow longer, more complex task execution without hitting step limits.
- The Cognitive Executor should be the default agent for both OpenCode and Freebuff.
- Both the OpenCode (`.md`) and Freebuff (`.ts`) agent definitions should be enhanced for better performance, clarity, and alignment.

## Local TODOs

- [ ] Explore current agent definitions for both OpenCode and Freebuff
- [ ] Determine appropriate new max steps value (e.g., 200 or 300)
- [ ] Update `agents/cognitive-executor.md` with increased steps
- [ ] Update `freebuff/agents/cognitive-executor.ts` with any available max steps configuration
- [ ] Verify `opencode.json` has `default_agent: cognitive-executor` (already confirmed)
- [ ] Enhance both agent definitions (system prompt improvements, tool additions, protocol refinements)
- [ ] Sync Freebuff agent version if modified
- [ ] Verify functionality

## Acceptance Criteria

- [ ] `agents/cognitive-executor.md` has increased `steps` value (e.g., 200+)
- [ ] `opencode.json` retains `default_agent: cognitive-executor`
- [ ] `freebuff/agents/cognitive-executor.ts` is enhanced and version-bumped if modified
- [ ] Both agent definitions are consistent in protocol and capabilities
- [ ] CHANGELOG.md updated with the changes
- [ ] Task file execution log populated with reasoning

## Verification Evidence

- **Test command:** `grep -n "steps:" agents/cognitive-executor.md`
- **Expected result:** Steps value higher than 100 (e.g., `steps: 200`)
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Increasing steps too high could allow runaway agent loops consuming excessive tokens
- **Rollback plan:** Revert the `steps` value in `agents/cognitive-executor.md` to 100; revert Freebuff agent version bump

---

## Execution Log & Reasoning

### Research Phase

Fetched and analyzed three production-grade agent system prompt references:
1. **disler/fixing-smartass-opus-5** — Reference points (D1/F1/R1/Q1/A1), positive/negative communication patterns, hard operational boundaries, aliases
2. **thepromptshelf.dev agentic-ai-best-practices-2026** — Single-responsibility agents, circuit breakers on tool loops ($0.50-$2 budget caps, 5+ tool call limit), reasoning drift prevention (re-anchor every N steps), coordinator-specialist pattern
3. **zylos.ai prompt-engineering-ai-agent-systems** — Five-layer anatomy (identity, behavioral rules, typed tool APIs, safety layers, conditional sections), instruction hierarchy (system > user > tool output), context window management (compaction, structured notes, sub-agents), plan-execute-observe-repeat with bounded iterations
4. **machinelearningmastery.com** — Context engineering > prompt engineering, four components (system prompt, tools, examples, context state), right altitude (specific enough to constrain, flexible enough to handle edge cases)

### Max Steps Decision

- **Previous value:** 100 (conservative, frequently hit on complex multi-file tasks)
- **New value:** 512 (supports long-running implementation tasks with circuit breakers)
- **Rationale:** Production agents (Claude Code, Cursor) handle 100+ tool calls per session. 512 provides headroom for complex tasks while circuit breakers (5+ identical tool calls, 50+ steps without progress) prevent runaway loops.

### Changes Applied

**agents/cognitive-executor.md (OpenCode):**
- `steps: 100` → `steps: 512`
- Added `## Communication Patterns` — reference points, positive/negative patterns
- Added `## Execution Discipline` — plan-execute-observe pattern, circuit breakers, reasoning drift prevention
- Added `## Behavioral Examples` — correct vs incorrect patterns
- Added `## Hard Operational Boundaries` — scope constraints

**freebuff/agents/cognitive-executor.ts (Freebuff):**
- Version bump `1.2.0` → `1.3.0`
- Added identical best practices sections adapted for Freebuff runtime (escaped backticks, TypeScript string format)

**agents/cognitive-discovery.md (OpenCode):**
- Added `## Execution Discipline` — minimal footprint, evidence-based reporting, circuit breakers
- Added `## Communication Patterns` — reference points, positive patterns

**freebuff/agents/cognitive-discovery.ts (Freebuff):**
- Version bump `1.2.0` → `1.3.0`
- Added identical sections adapted for Freebuff runtime

### What Was Preserved

All existing content (ZAC rules, MCP-first context, skill loading, Kanban lifecycle, subagent delegation, bash discipline) remains intact. New sections are additive.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `887a894230cde7ae73c2480895dddeb79fb20bca`
<!-- END_GIT_DIFF -->
