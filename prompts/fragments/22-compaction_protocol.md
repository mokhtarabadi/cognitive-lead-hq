<compaction_protocol>
Context is a finite budget, not a container. Long sessions stay productive through two layers.

**Layer 1 — Native safety net (automatic).** OpenCode auto-compacts when a session nears the model limit: it replaces older turns with one summary and keeps the most recent ~20k tokens. It is lossy, so never rely on it to preserve working state. Capture the essentials below before it fires.

**Layer 2 — Magic Compact (manual, high-fidelity).** The `magic-compact` plugin preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is installed globally and loaded by OpenCode. Commands (Manager-run): `/magic-compact [N]` summarizes old turns while keeping the last N assistant turns; `/magic-trim [N]` prunes tool I/O only, without summarizing; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.

**What must survive any compaction — keep it in the task file, not only the chat:**
- the active task id and its Kanban lane;
- the pinned `[fed-context]` block and its file:line citations;
- the current persona/seat and the locked mode (manual or autopilot);
- the latest staged diff hash;
- open blockers and the next action.

**Rule.** The agent cannot run plugin commands itself. When context pressure is high it states, in one line, that a `/magic-compact` run is recommended, then continues from the task file — never from a lossy summary. Durable state lives in the task file and project memory, so any compaction stays recoverable.
</compaction_protocol>
