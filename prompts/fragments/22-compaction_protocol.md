<compaction_protocol>
Context is a finite budget, not a container. Long sessions stay productive through two layers.

**Layer 1 — Native safety net (automatic).** OpenCode auto-compacts when a session nears the model limit: it replaces older turns with one summary and keeps the most recent ~20k tokens. It is lossy, so never rely on it to preserve working state. Capture the essentials below before it fires.

**Layer 2 — Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is V2-native: it keeps a per-session compaction state in plugin storage and applies it to the model-visible messages on every request, never mutating the stored transcript, so a bad run cannot corrupt history. It is installed globally and loaded by OpenCode. Manager commands: `/magic-compact [N]` summarizes old turns while keeping the last N turns; `/magic-trim [N]` prunes tool I/O only; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.

**The agent can trigger compaction itself.** Call the `compact_context` tool when the context window is under pressure: it runs the same logic as `/magic-compact` (summarize now, prune on the next request). Pass `keepTurns` to protect the most recent turns, and `mode: "trim"` to prune tool output without summarizing. The summary lands on the next request, so continue from the task file meanwhile.

**What must survive any compaction — keep it in the task file, not only the chat:**
- the active task id and its Kanban lane;
- the active session ID (OPENCODE_SESSION_ID);
- the pinned `[fed-context]` block and its file:line citations;
- the current persona/seat and the locked mode (manual or autopilot);
- the latest staged diff hash;
- open blockers and the next action.

**Rule.** The agent cannot run the `/magic-*` slash commands itself, but it CAN call `compact_context` directly — prefer that under pressure, and state one line about it. Either way, continue from the task file, never from a lossy summary. Durable state lives in the task file and project memory, so any compaction stays recoverable.

Compaction precedence: Smart Compact V2 session.hook context transform preserves per-turn summaries and prunable cached I/O per src/index.ts 238-254 with defaults maxChars1024 maxWords128 task4096. Goal compaction snapshot plus restore plus evidence nudge per src/compaction.ts 28-114 MUST NOT resurrect a cleared or completed objective. If goal status is clear or complete, restore is skipped. Task file remains truth.
</compaction_protocol>
