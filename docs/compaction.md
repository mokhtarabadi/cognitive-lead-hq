# Context Compaction

The platform keeps long sessions productive with three layers: OpenCode's native auto-compaction as the safety net, our own **Smart Compact** plugin as the high-fidelity manual layer, and that same plugin's awareness as the automatic layer that acts without an agent call. Durable working state lives in the task file and project memory, so any compaction stays recoverable.

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

`/goal` tracks one long-running objective per session in `.opencode/goals/<session-id>.json` with evidence in the matching `.evidence.json` sidecar (a legacy `.opencode/goal-state.json` stays a read fallback that migrates on first write, and the legacy `.opencode/goal-evidence.json` is read only until the session owns its own sidecar): `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal resume`, `/goal evidence <args>`, `/goal complete` (needs file citations plus tests that really pass — the plugin executes every recorded command and reads its real exit code; a test entry may carry an `env` map to pin the toolchain its command needs, and a blocked completion names the concrete failures instead of a generic hint), `/goal clear` — Manager lane. Every set starts a fresh empty evidence sidecar, so a new objective never inherits criteria from the goal before it and a finished goal's failing command cannot gate it; record evidence again for the new objective. Agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`; never write the state or evidence files with file tools; record evidence via `goal_evidence` before `goal_complete`; busy lease means retry next turn; corrupt state means report to the human. The agent opens the goal with `goal_set` when an objective is defined and resumes it with `goal_resume` after a block or interruption. Every slash mutation takes the state lease too, so a `set`, `block`, `resume`, or `clear` that lands while a completion is running answers `Goal is busy with another turn. Retry shortly.`; a completion holds that lease for the whole proof pass, which is why a slow `/goal complete` can make a concurrent change wait. The plugin reads its stop marker only at the projectDir `.opencode/STOP_GOAL` path (the project-root `STOP_GOAL` is never read); that marker is tracked in this repo, so the idle auto-continue is braked by a committed control rather than a local file, and it stops only the idle loop — never the five agent tools.

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

### Agent-callable tools

The agent compresses the session itself with the `compact_context` tool (never the `/magic-*` slash commands), which runs the same logic as `/magic-compact` (shared `src/actions.ts` in the plugin, so the paths cannot drift). Effect is async (stored now, prunes next request) — do not re-call to verify. In autopilot never ask the Manager to run slash commands:

The agent also compresses at the task boundary: when the previous task is fully finished and the Manager defines a new task in the same session, call `compact_context` with `keepTurns` 0 and `mode` `compact` before starting the new task, so the old turns do not crowd the new task's context. Recover the todo list with `todoread` after any compaction — never from a remembered transcript, because smart-compact replaces `todowrite` output with a short notice.

| Input | Effect |
| --- | --- |
| `keepTurns` (optional) | Most recent turns to keep unsummarized. Default `0` summarizes all. |
| `mode` (optional) | `compact` (default) summarizes and prunes; `trim` prunes tool output only. |

Invalid input returns a friendly message instead of failing. The slash commands remain available for the Manager.

The `compact_stats` tool reports what the compaction actually reclaimed: `prunedTokens`, `prunedParts`, `summarizedTurns`, cached omissions, memo-saved tokens, last run time, and whether the tokenizer backed the run. It takes no inputs, only reads the session state, and shares its formatter with `/magic-stats`, so the two lanes cannot report different numbers. Read it once when you need to choose between a trim and a full compaction — high `prunedParts` with `summarizedTurns` 0 means the bulk is tool output — never as a poll:

```json
{}
```

### Pruning rules

- Completed tool results over the configured limit (default 1024 chars / 128 words) are pruned to a notice; the original is cached.
- `read` output is always pruned (reloadable).
- `task` output uses a higher bar (default 4096 chars / 512 words).
- `question` output is never pruned (it captures an explicit user decision).
- `todowrite` output is replaced with a short notice and not cached (redundant). `skill` output is neither discarded nor pruned: a truncated skill body looks exactly like a broken `Load Skill`.
- Pending and errored calls are never pruned.

### Automatic strategies

- **Deduplication** — identical tool calls (same tool, same normalized arguments) keep only their most recent output; earlier ones are replaced with a notice.
- **Purge errors** — the arguments of errored tool calls are blanked after a configurable number of turns; error text is preserved.

### Configuration

JSONC, project over global: `.opencode/smart-compact.jsonc` over `~/.config/opencode/smart-compact.jsonc` over built-in defaults. On a fresh machine create the global file with this recommended content right after `opencode plugin add` (same snippet lives in `LLM.txt` §7.7, so an installer LLM writes it verbatim):

The platform runs `warnRatio 0.5` / `emergencyRatio 0.8` for window-relative firing; on a 1M-token window those lines sit at 500k and 800k, which is why the absolute `warnAtTokens` / `emergencyAtTokens` pair carries the reminder in practice. `autoTrimRatio 0.5` is the one automatic action and it is lossless: it queues a tool-output-only trim for the next request, summarizes nothing, and leaves every pruned original in the cache. A per-session latch means one sustained pressure period trims once; it re-arms only after the fill grows by `rearmStep` or drops below the line and rises again, so a long session above the threshold does not queue a trim on every request.

```jsonc
// Recommended global config for smart-compact.
{
  "enabled": true,
  "pruning": {
    "maxChars": 1024, "maxWords": 128, "taskMaxChars": 4096, "taskMaxWords": 512,
    "protectedTools": ["question", "skill"], "alwaysPruneTools": ["read"],
    "discardTools": {
      "todowrite": "Successfully updated todos."
    },
    "preserveRecentTurns": 2, "truncateToolsChars": 1024, "useTokens": true
  },
  "strategies": {
    "deduplication": { "enabled": true, "protectedTools": ["question"] },
    "purgeErrors": { "enabled": true, "turns": 4, "protectedTools": ["question"] },
    "stripReasoning": { "enabled": true, "thresholdChars": 500 }
  },
  "tokens": { "enabled": true, "emergencyBudgetTokens": 0, "emergencyBudgetRatio": 0.6 },
  "awareness": { "enabled": true, "warnRatio": 0.5, "emergencyRatio": 0.8, "rearmStep": 0.05, "autoTrimRatio": 0.55, "contextWindowTokens": 1000000, "warnAtTokens": 0, "emergencyAtTokens": 0 }
}
```

Four rules govern the numbers in that block.

- **The emergency budget follows the window.** A positive `emergencyBudgetTokens` pins an exact number and behaves exactly as before. `0` means *derive*: the budget becomes `emergencyBudgetRatio` (default `0.6`) of the resolved context window, so a large-window model no longer warns from the first few turns. To switch the warning off, set `emergencyBudgetRatio` to `0` — **not** `emergencyBudgetTokens`, because zero there now means derive. An unknown window keeps the warning silent rather than firing against a guessed denominator.
- **Awareness needs a denominator, and that number is a cap.** When the model registry entry carries no `limit.context`, set `awareness.contextWindowTokens` to the window size and the reminder states that the figure is configured rather than measured. With neither a registry limit nor a fallback, the advisory (and the lossless auto-trim that depends on the same ratio) stays inert — which is why the sample above carries an explicit `1000000` rather than the neutral `0`, and why a copied config with `0` here silently reproduces a plugin that never speaks. The same key is a hard ceiling: the plugin takes `min(registry limit, configured)`, so a project can lower the denominator below the model's real window and get a working budget instead of a percentage nobody ever reaches.
- **Set the absolute pair where work degrades, not where the window ends.** `warnAtTokens` / `emergencyAtTokens` fire on token counts (`0` disables either). The global file leaves them at `0` so no machine-wide budget is imposed; a project that wants one pins it in its own `.opencode/smart-compact.jsonc` — this repo uses 200k / 120k / 160k on a 1M-token model.
- **Auto-trim is armed by default.** `autoTrimRatio` defaults to `0.55`, so bulky completed tool results become notices without any manual call, one trim per sustained pressure period. Pruning is lossless — the original stays cached — so this is safe to leave on.

### Retrieving pruned content

Each omission notice carries a Content ID (e.g. `omitted-0001`). Prefer a cheap fresh run of the source tool; the agent calls `read_omitted_content` with that ID ONLY when the output cannot be reproduced cheaply, never speculatively — the lookup is scoped to the calling session, a single response is capped at 20 000 characters (a longer original returns a truncation notice rather than megabytes of text), and an original dropped by the store cap fails closed with a missing-original notice instead of returning stale content. On a cache miss, re-run the source tool once.

## Layer 3 — Awareness and automatic relief (no agent call)

The plugin watches fill by itself and can take two actions. Neither one summarizes a turn, touches a user message, or aborts a step.

Fill is measured against a **working budget**, not against the model ceiling. `awareness.contextWindowTokens` is a hard cap on the denominator — the plugin measures against `min(registry limit, configured)` — so a 1M-token model is still reported against the budget in which the work actually happens. That is the point: a ratio threshold on a 1M window is unreachable in practice. The shipped `warnRatio` 0.5 first speaks at 500k tokens, and a session's useful detail is long gone by then. This repo pins a 200k budget on a 1M window in `.opencode/smart-compact.jsonc` (warn at 120k, emergency at 160k).

| Action | Trigger | Effect | Lossy? |
| --- | --- | --- | --- |
| Advisory reminder | Fill crosses `awareness.warnAtTokens` (repo: 120k tokens) or `emergencyAtTokens` (160k); the ratio pair (`warnRatio` / `emergencyRatio`) stays as the window-relative path | One system part telling the agent how full the window is and what to call | No |
| Tool-output trim (`awareness.autoTrimRatio`) | Fill crosses the ratio (platform: `0.5`) | Queues a `trim` for the next request, reusing the manual trim pass. Once per sustained pressure period, not once per request | No — originals stay cached under a Content ID |

`0` disables either absolute threshold, and an unknown window keeps the reminder silent rather than firing against a guessed denominator. The plugin logs one console line each time it fires a reminder and each time it queues a trim, so a silent log means nothing fired — never assume the mechanism is broken, and check the fill the `compact_stats` line reports.

Summarization is not automatic on purpose: replacing turns with summaries needs the agent's own judgement about which detail still matters. The plugin never overwrites a pending compaction with a weaker trim, and the agent still compacts at the task boundary — see the task-boundary rule above.

Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.

## Integration in this platform

- **System prompt:** none — the prompt is plugin-blind on purpose (the retired `<compaction_protocol>` fragment sits in `prompts/archive/` and is never assembled), so the survival contract below and `agents/cognitive-executor.md` carry the whole rule set.
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
