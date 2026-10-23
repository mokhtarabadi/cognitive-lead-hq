---
created_at: '2026-10-21T06:10:15.806342+00:00'
status: active
tags: []
updated_at: '2026-10-21T06:10:15.806361+00:00'
---

# Free-model context-window workflow (verified 2026-10-21)

Goal: raise OpenCode free-tier model context beyond the picker value, and set real
provider parameters. Truth: the **server** enforces the window, not the client. A
client-side limit override only decides when OpenCode compacts; it cannot make the
server accept more than its own cap.

## Where the numbers come from

- **Client catalog (picker value):** `https://models.opencode.ai/api.json` → `opencode.models[<id>].limit`
  (this is the "200,000" shown in the picker for several free SKUs).
- **Real paid-model params:** `https://openrouter.ai/api/v1/models` → match by
  stripping the `-free` suffix (e.g. `deepseek-v4.1-flash-free` →
  `deepseek/deepseek-v4.1-flash`), read `context_length` and
  `top_provider.max_completion_tokens`.
  **These are the PAID SKU's numbers. The free SKU is served with a smaller
  window — copying 1M into the free SKU's config does not grant 1M.**

## Where to apply it

`~/.config/opencode/opencode.json`:

```json
{
  "provider": {
    "opencode": {
      "models": {
        "<free-model-id>": { "limit": { "context": <server-verified tokens>, "output": <modest> } }
      }
    }
  }
}
```

Merge semantics (upstream source `packages/core/src/config/plugin/provider.ts`, model loop
near line 133): `model.limit = { ...model.limit, ...config.limit }` — the config
value wins, per model, keys are the model IDs from the picker. Provider key is
`opencode`. Same merge exists for the built-in provider plugin
(`packages/core/src/plugin/provider/opencode.ts:320`). No plugin needed.
Output must stay modest: the server checks **input + requested output** against
the window, so a huge `output` (e.g. OR's 943718) makes the client reserve
more than the window and every request fails.

## Verification method (no cost, free models)

```bash
# deterministic filler: 'the ' ~ 1 token per word
python3 -c "open('/tmp/cap.txt','w').write('the '*N + '\nReply with exactly: p-ok')" N
cat /tmp/cap.txt | opencode run --standalone --model opencode/<model-id>
```

- `p-ok` → accepted.
- `Your request resulted in more tokens than this model's maximum context length
  allows` → **server** rejected (raise N to find the ceiling; bisect).
- `The compaction request cannot be reduced further…` → **client**-side limit
  blocked it (raise the config `context` and retry).

Set the config `context` to `N + 120000` while probing, otherwise the client
compacts first and you cannot see the server's true cap.

## Measured server caps (2026-10-21, free tier)

| Model | Picker (feed) | Server accepts | Server rejects | Config now |
|---|---|---|---|---|
| `deepseek-v4.1-flash-free` | 200000 | **327680** | 360000 | context 327680, output 32000 |
| `glm-5.3-flash-free` | 200000 | **327680** | — | context 327680, output 32000 |
| `deepseek-v4-flash-free` | 200000 | < 327680 | 327680 | feed value (200000) |
| `mimo-v2.6-flash-free` | 200000 | < 700000 | 700000 | feed value (200000) |
| `longcat-2.5-preview-free` | 1000000 | 700000 (limit set) | — | feed value (1000000) |
| `muse-spark-1.3-contributor-free` | 1048576 | — | — | **removed from config**: deprecated upstream 2026-10-21 ("Model muse-spark-1.3-contributor-free has been deprecated") |

Consequences: the picker value is often **under** the server cap (200000 vs
327680) — overriding it is a real win, not a hack. It is never **over** the
server cap, so OpenRouter's 1M for the paid SKU is unreachable on the free SKU.

## Other hard limits found

- Free tier only works from inside the real OpenCode client. `curl`/python
  direct calls to `https://opencode.ai/zen/v1/chat/completions` get 403
  `FreeTierError` even with the `bash` tool in the body and a
  `ses_<hex12><base62-14>` session id, `x-opencode-client`, `x-opencode-request`,
  `User-Agent: opencode/<ver>` and `Authorization: Bearer public`.
  The provider-side gate is not reproducible from outside (upstream
  anomalyco/opencode#49433, #50627, #53347; r/opencode 1wkehdq;
  r/hermesagent 1w9x0on).
- Do not trust the OR "free" suffix mapping: OR has no `*-free` SKUs; several
  free SKUs have no OR counterpart at all (big-pickle, cat-jam-free,
  longcat-*, muse-spark-*, step-5-preview-free, space-bunny-free,
  nemotron-3-ultra-free, exo-free, beam-free, fledge-alpha-free, hy3*,
  ling-*, ring-2.6-1t-free, x-preview-f-free, north-mini-code-free,
  laguna-s-2.1-free, ll-alpha-free, trinity-large-preview-free,
  omen-alpha, mimo-v2-pro-free). For those, the feed value is the only source.

## Reusable recipe for a new free model

1. Feed value: `curl -s https://models.opencode.ai/api.json | jq '.opencode.models["<id>"].limit'`.
2. OR paid counterpart: strip `-free`, try prefixes `deepseek/ z-ai/ qwen/ xiaomi/
   meta/ moonshotai/ minimax/ nvidia/`.
3. Write the override with a generous probe `context` (`feed + 120000`) and
   `output: 32000`.
4. Probe with 'the ' filler, bisect between last-OK and first-reject.
5. Set final `context` = last-OK tokens, `output` = 32000 (or feed value if smaller).
6. Restart nothing — OpenCode re-reads config per session; use
   `opencode run --standalone` for a clean server, and `--print-logs` /
   `--log-level all` to see provider errors.
