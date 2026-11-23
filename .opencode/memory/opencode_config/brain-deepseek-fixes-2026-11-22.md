---
created_at: "2026-11-22T14:53:53.021502+00:00"
status: active
tags: []
updated_at: "2026-11-22T14:53:53.021543+00:00"
---

# Brain DeepSeek hardening (2026-11-22)

Verified via DeepSeek docs (api-docs.deepseek.com):

- reasoning_effort accepts none/low/high/max (minimal->low, medium/xhigh->high). 'max' is valid, so no clamp needed.
- temperature is IGNORED in thinking mode (no error). No suppression needed.
- max_tokens default: 8K non-thinking, 64K thinking, 128K with max effort. Max allowed 384K.
- usage reports prompt_cache_hit_tokens, prompt_cache_miss_tokens, completion_tokens_details.reasoning_tokens, prompt_tokens_details.cached_tokens.

Changes:

- .env: BRAIN_MAX_TOKENS=131072 (to match max-effort default).
- server.py: _convert_chat_completions_to_responses_data now passes through input_tokens_details (cached_tokens / prompt_cache_hit_tokens) and output_tokens_details (reasoning_tokens etc.).
- server.py: added warning branch for dropped input item types.
- server.py: _get_max_tokens default kept 32768 (safe fallback); deployed .env overrides to 131072.

F3 (empty choices -> failed) already handled: _responses_status_from_finish(None) returns incomplete/unknown_finish_reason.
F1 (max/xhigh 400) is not a real issue for DeepSeek (max valid, xhigh mapped to high).
F2 (temperature) is ignored, not error.
F8 (vocabulary check) exists.

Tests: 390 passed. Smoke test: XML_EXTRACTED, reasoning_tokens=9111 visible in usage.
