---
created_at: '2026-10-24T16:43:34.284845+00:00'
status: active
tags: []
updated_at: '2026-10-24T16:43:34.284875+00:00'
---

# Brain on zen-proxy with one model (Manager order 2026-10-24)

Every Brain tier runs on the zen-proxy Go Responses mount with a single
model and effort:

- BRAIN_API_BASE=http://127.0.0.1:8081/go/resp
- BRAIN_MODEL=muse-spark-1.3-contributor
- BRAIN_MODEL_LOW=muse-spark-1.3-contributor
- BRAIN_MODEL_HIGH=muse-spark-1.3-contributor
- BRAIN_REASONING_EFFORT=xhigh
- BRAIN_RISK_ROUTING_ENABLED=true (routing stays on, all tiers identical)

Both copies must stay in sync: repo .env and the effective global
~/.config/opencode/.env (read by mcp-brain self-load and the zen-proxy unit).
This is the .env.example "Economy" preset; the balanced preset
(gpt-6-luna for BRAIN_MODEL/HIGH) is no longer the deployed setting.

Quota and credential status 2026-10-24: the old BRAIN_API_KEY belonged to a
Go workspace with the monthly limit exhausted (429 GoUsageLimitError), so
config-correct turns still failed. OpenCode's live credential is NOT
~/.local/share/opencode/auth.json (stale — 401 Invalid credential at the
gateway); it lives in ~/.local/share/opencode/opencode.db, table
`credential` where integration_id='opencode-go' and active=1, JSON value
carrying `key`. That key is now BRAIN_API_KEY in both env files and a
brain_turn smoke test returned SMOKE_OK on muse-spark-1.3-contributor.
/zen/resp (free models) lists empty upstream — no free fallback exists.