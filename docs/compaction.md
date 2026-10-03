# Context Compaction

The platform keeps long sessions productive with two layers: OpenCode's native auto-compaction as the safety net, and the `magic-compact` plugin as the high-fidelity manual layer. Durable working state lives in the task file and project memory, so any compaction stays recoverable.

## Layer 1 — Native OpenCode compaction (automatic)

OpenCode compacts when a session approaches the model's context limit. It summarizes everything except the most recent conversation (~20,000 tokens here) and places that summary in front of the recent tail; later compactions update the same summary. It is lossy, so it is a survival mechanism, not an optimization.

Configured in the global `~/.config/opencode/opencode.json`:

```json
"compaction": {
  "auto": true,
  "keep": { "tokens": 20000 }
}
```

`compaction.keep.tokens` is the size of the recent tail kept verbatim. Raise it when exact recent detail matters; lower it when context room matters more.

## Layer 2 — Magic Compact (manual, high fidelity)

[`aerovato/magic-compact`](https://github.com/aerovato/magic-compact) preserves the conversation skeleton: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a cache that the agent can read back. Compaction happens once, on command, so it does not churn the prompt cache during the agent loop.

### Install (already done on this machine)

```bash
opencode plugin add magic-compact@1.2.2
```

This installs the package from npm and writes `plugins: ["magic-compact"]` into the global config; OpenCode installs and loads it at startup. New machines get the entry from the global `opencode.json` in `LLM.txt` §7 plus the install command in `LLM.txt` §7.7.

> **npm proxy caveat:** if `~/.npmrc` points at a dead proxy, the install fails with `NPMInstallFailedError`. Remove the `proxy`/`https-proxy` lines so the registry is reached directly. On this machine the stale `127.0.0.1:7890` proxy was commented out.

### Commands (Manager-run)

| Command            | Effect                                                              |
| ------------------ | ------------------------------------------------------------------ |
| `/magic-compact`   | Summarize all old assistant turns                                   |
| `/magic-compact 3` | Keep the 3 most recent assistant turns, summarize the rest          |
| `/magic-trim`      | Prune tool I/O only, without summarizing (OpenCode-only, no LLM call) |
| `/magic-stats`     | Cumulative token/money savings for the session                      |

A backup session is created before each run, so a failed compaction returns to the backup.

### Pruning rules (summary)

- Kept: user messages verbatim, per-turn summaries, tool-call structure, key synthetic messages.
- Removed/condensed: assistant reasoning and text (replaced by the per-turn summary), most synthetic injected messages, bulky completed tool I/O.
- Tool I/O omitted above ~128 words / 1024 chars; `read` output always omitted (reloadable), `write`/`edit` large content omitted, `bash` commands over 1024 chars truncated.
- Pending, running, and errored tool calls are always preserved.

### Retrieving pruned content

Each omission notice carries a Content ID (e.g. `omitted-001`). The agent calls the `read_omitted_content` tool with that ID to fetch the original instead of re-running the source tool.

## Integration in this platform

- **System prompt:** the `<compaction_protocol>` fragment (generated into `system-prompt.md`) states the two layers and the survival contract.
- **Agent:** `agents/cognitive-executor.md` carries the operational steps, including that the agent cannot run the plugin command and instead recommends a `/magic-compact` run when context pressure is high.
- **Config:** global `opencode.json` holds `plugins` + `compaction`; the repo `opencode.json` stays config-free of both.

**Survival contract** — keep these in the task file so any compaction is recoverable:

- the active task id and its Kanban lane;
- the pinned `[fed-context]` block and its `file:line` citations;
- the current persona/seat and the locked mode (manual or autopilot);
- the latest staged diff hash;
- open blockers and the next action.

## Upstream status and rollback

Magic Compact development is **paused** in favor of [Operator Memory](https://github.com/aerovato/operator-memory), its successor; the pinned `1.2.2` release remains fully functional and is what this platform installs. Rollback is one line: `opencode plugin remove magic-compact` (and drop the `plugins` key). Native auto-compaction continues to work on its own if the plugin is removed.
