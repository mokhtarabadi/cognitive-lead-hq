# rate-limit-rescue

OpenCode V2 plugin (`@opencode/plugin`, `Plugin.define` + `ctx.session.hook("retry")`).
Fires **only** on free-tier rate limits — every other error passes through untouched.

## What it does

On a free-tier 429-class failure it:

1. Runs the env-configured command (default `~/.local/bin/rr` — rotates the balancer node).
2. Appends one JSONL metrics line (default `~/.local/share/opencode/ratelimit-metrics.jsonl`), tagged `kind: "quota"` or `kind: "transport"`.
3. Overrides the wait to 2s (`event.decision = { retry: true, delay: 2_000 }`).

It also rescues transient transport faults (`ECONNRESET`, socket hang-up/closed,
`ETIMEDOUT`, `EPIPE`) the same way — these are proxy/node faults where `rr`
rotation is the fix.

## Detection ground truth

From `~/.local/share/opencode/log/opencode.log` (2026-09-26):

```text
AI.Error: Rate limit exceeded. Please try again later.
[cause]: AI.Error.QuotaExceeded: Rate limit exceeded. Please try again later.
```

No HTTP status, no free/tier words — so scope comes from the **model id**
(`*free*`, `*contributor*`), not the message. Gate: rate-ish
(`429|rate limit|quota|exceeded`) AND free-ish model/message.

## Env knobs

| Var | Default | Purpose |
| --- | ------- | ------- |
| `RATE_LIMIT_COMMAND` | `~/.local/bin/rr` | Command run on each hit |
| `RATE_LIMIT_METRICS` | `~/.local/share/opencode/ratelimit-metrics.jsonl` | Metrics sink (one JSON object per line) |

Plugin options (`command`, `metricsPath` in `opencode.json`) override env.

## Metrics vs OpenCode numbers

Each line carries `ts`, `sessionID`, provider/model, `status`,
`errorKeys`/`errorType`/`errorCode`, message head, `attempt`,
`proposedDelayMs` (what OpenCode wanted), command result, and the applied
`retryDelayMs`. Correlate by timestamp against:

- `rr` rotation timeline: `rotation_log (ts, node, delay_ms, reason)` SQLite DB in `v2ray-to-subs/`
- OpenCode's own log lines around the same `ts` (`Failed to drain Session`)

## Verify

```sh
node --check index.js
node --input-type=module -e "import('./index.js').then(async (m) => {
  const e = { error: { status: 429, message: 'Rate limit exceeded. Please try again later.' },
              attempt: 1, sessionID: 's', model: { providerID: 'opencode', id: 'muse-spark-1.3-contributor-free' } };
  console.log(await m.handleRetry(e, { command: 'echo ok', metricsPath: '/tmp/rl.jsonl' }), e.decision);
})"
```

## Install (global)

```sh
cp -r plugins/rate-limit-rescue ~/.config/opencode/plugins/rate-limit-rescue
# add "/home/mohammad/.config/opencode/plugins/rate-limit-rescue" to global opencode.json "plugins", restart sessions
```

Rollback: remove the entry + the directory.
