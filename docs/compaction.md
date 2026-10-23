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

### Goal plugin install

```bash
# Interim (works now, installs from the pushed repo):
opencode plugin add github:mokhtarabadi/opencode-goal-plugin
# Once published to npm:
opencode plugin add opencode-goal-plugin
```

`/goal` tracks one long-running objective per session in `.opencode/goals/<session-id>.json` with evidence in the matching `.evidence.json` sidecar (a legacy `.opencode/goal-state.json` stays a read fallback that migrates on first write): `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal resume`, `/goal evidence <args>`, `/goal complete` (needs file citations plus tests that really pass — the plugin executes every recorded command and reads its real exit code), `/goal clear` — Manager lane. Agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`; never write the state or evidence files with file tools; record evidence via `goal_evidence` before `goal_complete`; busy lease means retry next turn; corrupt state means report to the human. The agent opens the goal with `goal_set` when an objective is defined and resumes it with `goal_resume` after a block or interruption. Every slash mutation takes the state lease too, so a `set`, `block`, `resume`, or `clear` that lands while a completion is running answers `Goal is busy with another turn. Retry shortly.`; a completion holds that lease for the whole proof pass, which is why a slow `/goal complete` can make a concurrent change wait. The plugin reads its stop marker only at the projectDir `.opencode/STOP_GOAL` path (the project-root `STOP_GOAL` is never read); that marker is tracked in this repo, so the idle auto-continue is braked by a committed control rather than a local file, and it stops only the idle loop — never the five agent tools.

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

### Automatic at pressure (agent needs no action)

Two things happen without anyone asking:

| Layer | Trigger | Effect | Lossy? |
| --- | --- | --- | --- |
| Tool-output trim (`awareness.autoTrimRatio`) | Fill crosses the ratio (platform: `0.5`) | Queues a `trim` for the next request, reusing the manual trim pass. Once per sustained pressure period, not once per request | No — originals stay cached under a Content ID |
| Advisory reminder (`awareness.warnRatio`) | Fill crosses the ratio (platform: `0.5`, emergency `0.8`) | One system part telling the agent how full the window is and what to call | No |

Summarization is not automatic on purpose: replacing turns with summaries needs the agent's own judgement about which detail still matters. The plugin never overwrites a pending compaction with a weaker trim.

### Agent-callable tool

The agent compresses the session itself with the `compact_context` tool (never the `/magic-*` slash commands), which runs the same logic as `/magic-compact` (shared `src/actions.ts` in the plugin, so the paths cannot drift). Effect is async (stored now, prunes next request) — do not re-call to verify. In autopilot never ask the Manager to run slash commands:

The agent also compresses at the task boundary: when the previous task is fully finished and the Manager defines a new task in the same session, call `compact_context` with `keepTurns` 0 and `mode` `compact` before starting the new task, so the old turns do not crowd the new task's context. Recover the todo list with `todoread` after any compaction — never from a remembered transcript, because smart-compact replaces `todowrite` output with a short notice.

| Input | Effect |
| --- | --- |
| `keepTurns` (optional) | Most recent turns to keep unsummarized. Default `0` summarizes all. |
| `mode` (optional) | `compact` (default) summarizes and prunes; `trim` prunes tool output only. |

Invalid input returns a friendly message instead of failing. The slash commands remain available for the Manager.

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

JSONC, project over global: `.opencode/smart-compact.jsonc` over `~/.config/opencode/smart-compact.jsonc` over built-in defaults. On a fresh machine create the global file with this recommended content right after `opencode plugin add` (same snippet lives in `LLM.txt` §7.7, so an installer LLM writes it verbatim):

The platform runs `warnRatio 0.5` / `emergencyRatio 0.8` because a 1M-token window at the shipped `0.7` would only warn at ~734K tokens. `autoTrimRatio 0.5` is the one automatic action and it is lossless: it queues a tool-output-only trim for the next request, summarizes nothing, and leaves every pruned original in the cache. A per-session latch means one sustained pressure period trims once; it re-arms only after the fill grows by `rearmStep` or drops below the line and rises again, so a long session above the threshold does not queue a trim on every request.

```jsonc
// Recommended global config for smart-compact.
{
  "enabled": true,
  "pruning": {
    "maxChars": 1024, "maxWords": 128, "taskMaxChars": 4096, "taskMaxWords": 512,
    "protectedTools": ["question"], "alwaysPruneTools": ["read"],
    "discardTools": {
      "todowrite": "Successfully updated todos.",
      "skill": "Skill contents omitted after compaction; recall the skill if needed."
    },
    "preserveRecentTurns": 2, "truncateToolsChars": 1024, "useTokens": true
  },
  "strategies": {
    "deduplication": { "enabled": true, "protectedTools": ["question"] },
    "purgeErrors": { "enabled": true, "turns": 4, "protectedTools": ["question"] },
    "stripReasoning": { "enabled": true, "thresholdChars": 500 }
  },
  "tokens": { "enabled": true, "emergencyBudgetTokens": 50000 },
  "awareness": { "enabled": true, "warnRatio": 0.5, "emergencyRatio": 0.8, "rearmStep": 0.05, "autoTrimRatio": 0.5 }
}
```

### Retrieving pruned content

Each omission notice carries a Content ID (e.g. `omitted-0001`). Prefer a cheap fresh run of the source tool; the agent calls `read_omitted_content` with that ID ONLY when the output cannot be reproduced cheaply, never speculatively — the lookup is scoped to the calling session. On a cache miss, re-run the source tool once.

Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.

## Integration in this platform

- **System prompt:** the `<compaction_protocol>` fragment (generated into `system-prompt.md`) states the two layers and the survival contract.
- **Agent:** `agents/cognitive-executor.md` carries the operational steps: the agent calls `compact_context` itself under pressure (slash commands are Manager-only) and recommends `/magic-compact` only when a tool call is unavailable in manual mode.
- **Config:** global `opencode.json` holds `plugins` + `compaction`; the repo `opencode.json` stays config-free of both.
- **Global plugins:** Global plugins live in user config at tilde config opencode opencode dot json as github mokhtarabadi opencode-smart-compact plus github mokhtarabadi opencode-goal-plugin. Repo opencode dot json has no plugins key by intent. HQ task file stays truth. Use the goal plugin for long objectives (`/goal` set, status, block, complete with evidence, clear); its idle loop never fires past an approval gate.

Compaction precedence: Smart Compact V2 session.hook context transform preserves per-turn summaries and prunable cached I/O per src/index.ts 238-254 with defaults maxChars1024 maxWords128 task4096. Goal compaction snapshot plus restore plus evidence nudge per src/compaction.ts 28-114 MUST NOT resurrect a cleared or completed objective. If goal status is clear or complete, restore is skipped. Task file remains truth.

**Survival contract** — keep these in the task file so any compaction is recoverable:

- the active task id and its Kanban lane;
- the pinned `[fed-context]` block and its `file:line` citations;
- the current persona/seat and the locked mode (manual or autopilot);
- the latest staged diff hash;
- open blockers and the next action.

## Rollback

Smart Compact is our own plugin. Rollback is one line: `opencode plugin remove @mokhtarabadi/opencode-smart-compact` (and drop the `plugins` key). Native auto-compaction continues to work on its own if the plugin is removed.
