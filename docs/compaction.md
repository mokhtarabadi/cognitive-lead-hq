# Context Compaction

The platform keeps long sessions productive with two layers: OpenCode's native auto-compaction as the safety net, and our own **Smart Compact** plugin as the high-fidelity manual layer. Durable working state lives in the task file and project memory, so any compaction stays recoverable.

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

## Layer 2 — Smart Compact (manual, high fidelity)

`@mokhtarabadi/opencode-smart-compact` — maintained in its own repo `mokhtarabadi/opencode-smart-compact` — preserves the conversation skeleton: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a cache the agent can read back. It is a clean-room, **V2-native** rewrite of the idea behind the V1 `magic-compact`: the V1 plugin mutated the stored transcript, which OpenCode V2 no longer exposes, so Smart Compact keeps a per-session compaction state in plugin storage and applies it to the model-visible messages on every request through `session.hook("context")`. The transcript is never modified, so a bad run cannot corrupt history.

### Install

```bash
# Interim (works now, installs from the pushed repo):
opencode plugin add github:mokhtarabadi/opencode-smart-compact
# Once published to npm:
opencode plugin add @mokhtarabadi/opencode-smart-compact
```

Note: `opencode plugin add` accepts npm registry packages or Git specs only — a bare local directory path is rejected, so use the Git spec (or list the directory in `plugins` and restart) while developing.

This writes the package (or path) into `plugins` in the global config; OpenCode loads it at startup. New machines get the entry from the global `opencode.json` in `LLM.txt` §7 plus the install command in `LLM.txt` §7.7.

> **Do not install `magic-compact`.** The V1-era npm package exports the V1 plugin shape and fails to load on OpenCode 2 with `PluginModule.LoadError`. Smart Compact is the V2-native replacement.
>
> **npm proxy caveat:** if `~/.npmrc` points at a dead proxy, the install fails with `NPMInstallFailedError`. Remove the `proxy`/`https-proxy` lines so the registry is reached directly. On this machine the stale `127.0.0.1:7890` proxy was commented out.

### Commands (Manager-run)

| Command            | Effect                                                         |
| ------------------ | -------------------------------------------------------------- |
| `/magic-compact`   | Summarize all old assistant turns; prune bulky tool output     |
| `/magic-compact 3` | Keep the 3 most recent turns, summarize the rest               |
| `/magic-trim`      | Prune tool I/O only, without summarizing (no LLM call)         |
| `/magic-stats`     | Report cumulative savings for the session as a visible message |

Compaction is scheduled by the command and applied on the next model request; summaries are generated at command time with the session's own model.

### Pruning rules

- Completed tool results over the configured limit (default 1024 chars / 128 words) are pruned to a notice; the original is cached.
- `read` output is always pruned (reloadable).
- `task` output uses a higher bar (default 4096 chars / 512 words).
- `question` output is never pruned (it captures an explicit user decision).
- `todowrite` and `skill` output is replaced with a short notice and not cached (redundant or reloadable).
- Pending and errored calls are never pruned.

### Automatic strategies

- **Deduplication** — identical tool calls (same tool, same normalized arguments) keep only their most recent output; earlier ones are replaced with a notice.
- **Purge errors** — the arguments of errored tool calls are blanked after a configurable number of turns; error text is preserved.

### Configuration

JSONC, project over global: `.opencode/smart-compact.jsonc` over `~/.config/opencode/smart-compact.jsonc` over built-in defaults. Only override what you need (`enabled`, `pruning.*`, `strategies.*`).

### Retrieving pruned content

Each omission notice carries a Content ID (e.g. `omitted-0001`). The agent calls `read_omitted_content` with that ID to fetch the original — the lookup is scoped to the calling session — instead of re-running the source tool.

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

## Rollback

Smart Compact is our own plugin. Rollback is one line: `opencode plugin remove @mokhtarabadi/opencode-smart-compact` (and drop the `plugins` key). Native auto-compaction continues to work on its own if the plugin is removed.
