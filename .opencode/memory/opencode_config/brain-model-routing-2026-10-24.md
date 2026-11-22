---
created_at: '2026-10-24T16:43:34.284845+00:00'
status: active
tags: []
updated_at: '2026-11-22T14:00:00.000000+00:00'
---

# Brain on zen-proxy chat mount with DeepSeek V4.1 Flash (Manager order 2026-11-22)

Every Brain tier runs on the zen-proxy Go chat mount with a single
model and max reasoning effort:

- BRAIN_API_BASE=http://127.0.0.1:8081/go/chat
- BRAIN_UPSTREAM_MODE=chat_completions
- BRAIN_MODEL=deepseek-v4.1-flash
- BRAIN_MODEL_LOW=deepseek-v4.1-flash
- BRAIN_MODEL_HIGH=deepseek-v4.1-flash
- BRAIN_REASONING_EFFORT=max
- BRAIN_RISK_ROUTING_ENABLED=true (routing stays on, all tiers identical)

Both copies stay in sync: global ~/.config/opencode/.env (read by
mcp-brain self-load and the zen-proxy unit). Repo has no .env.

Smoke test: brain_turn returned SMOKE_OK on deepseek-v4.1-flash via
chat_completions mode (status=completed).
