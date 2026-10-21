---
created_at: '2026-10-21T19:11:37.699463+00:00'
status: active
tags: []
updated_at: '2026-10-21T19:11:37.699481+00:00'
---

# Responses API best-practice audit (2026-10-21) — Brain Bridge

Full record: task file `tasks/backlog/329-responses-api-best-practices-alignment.md` (all findings, official quotes, code citations, fixes).
Peer is a LOCAL GATEWAY, not api.openai.com: `BRAIN_API_BASE=http://127.0.0.1:8081/go/resp`, model `muse-spark-1.3-contributor`, effort `xhigh`, `max_output_tokens=131072`, window 1048576. The gateway was NOT probed during the audit — every parameter claim is 'documented by OpenAI', not 'verified live'. Probe before implementing.

Code audited: `mcp-brain-bridge/server.py` — exactly ONE provider call site (server.py:1536, raw httpx POST to `{BRAIN_API_BASE}/responses`). Nothing else in the repo calls a model.
Official sources: developers.openai.com (api/reference/resources/responses/methods/create.md, guides: conversation-state, reasoning, text, prompt-caching, error-codes, your-data, streaming-responses), Cookbook 'per-run spending controller', and openai-python 2.54.0 ResponseCreateParams (generated from the OpenAPI spec).

## The 10 findings

F1 (privacy) — `store` never sent, so responses are stored provider-side by default. Official: 'Responses are stored by default... set `store: false`'; ZDR forces store=false. We push system prompt + task file + diffs. Code: body at server.py:3195-3203. Fix: send `store: false`; pair with `include: [reasoning.encrypted_content]` for stateless reasoning replay.

F2 (quality) — reasoning items and assistant `phase` dropped every turn. Official: 'preserve every item in the response output array... keeps reasoning items and assistant phase values intact'; 'dropping phase can degrade performance'; 'verify your integration preserves the assistant message phase field correctly'. Code: server.py:3192-3194 rebuilds text-only role/content pairs; roles limited at :1956-1961; transcript stores text (:3415-3432). Fix: persist and replay provider output items.

F3 (robustness) — no `truncation` (default 'disabled' = 400 on overflow), no `context_management` compaction, and the guard estimates tokens as `chars // 4` against a 1M window. Official: truncation 'auto' drops oldest items; 'disabled (default)... the request will fail with a 400 error'; create.md documents context_management {type: compaction, compact_threshold}. Code: :1397-1403, :3091-3146, :3239-3252. Fix: truncation auto + calibrate tokens from the `usage.input_tokens` we already receive (or the official input-token count endpoint).

F4 (cost) — `prompt_cache_key` never sent although a cache-split descriptor is computed and deliberately kept off the wire. Official: 'Used by OpenAI to cache responses for similar requests to optimize your cache hit rates. Replaces the `user` field.' Code: descriptor at :1334-1372, kept sidecar-only at :3155-3156. Also `usage.input_tokens_details.cached_tokens` is never read, so cache hits are invisible. Fix: send a stable key from the existing prompt hash + surface cached_tokens.

F5 (correctness) — the response `model` is never read, so a silent model substitution is invisible. Official Cookbook: 'Use a fixed model ID that the API returns unchanged in response.model' and raises UncertainCharge on mismatch. Code: diagnostics read only status / incomplete_details / usage / error / output (:3625-3661); no data.get('model'). Fix: read response.model into debug.provider and compare.

F6 (errors) — every 429 is retried and `error.code` is never parsed. Official: billing/spend/quota 429s 'won't restore API access' — do not retry. Code: _RETRYABLE_STATUS at :1439 retries 429 unconditionally; error parser takes .message only (:3644-3659). Fix: parse error.code/error.type, make billing+spend+quota codes terminal with an actionable hint.

F7 (robustness) — a fatal 4xx escapes brain_turn as a raw RuntimeError instead of a REPORT with debug.provider. Official: each fatal status has its own remedy (400/401/403/404/422). Code: :1548-1553 raises; no try/except around the call in :2669-3460. Fix: catch inside the turn, return a diagnostic REPORT.

F8 (correctness) — effort ladder omits `minimal` and the unknown-value fallback RAISES effort to medium; the vocabulary is not validated. Official values: none/minimal/low/medium/high/xhigh/max, model-dependent; 'GPT-6 Astra does not support none... returns HTTP 400'. Code: ladder :3778-3784, fallback 'medium' at :3787-3793, regex-only validation :3479-3482. Fix: validate the vocabulary, add minimal, fall back to low/current.

F9 (hygiene) — _get_max_tokens silently falls back to 32768 on a bad BRAIN_MAX_TOKENS and passes negatives through (:1383-1386) while every other env reader fails loud; _FATAL_STATUS is dead (:1443); _send_with_learning is vestigial with unused kwargs (:1644-1662) and there is NO unsupported_parameter correction path in the code (only a comment at :3198-3200) although the CHANGELOG still claims one; stale __pycache__ for 8 deleted modules.

F10 (low) — system prompt is a `role: system` item inside `input` (:3192) instead of the top-level `instructions` field. Official: 'A system (or developer) message inserted into the model's context' and instructions 'take priority over a prompt in the input parameter'. Fix: use `instructions`, keep role form as gateway fallback.

## Verified correct (do not 'fix')
output[] is walked fully (both message/content/output_text and bare output_text) at :3850-3869 — official: 'not safe to assume output[0].content[0].text'. Triage order error -> refusal -> incomplete/max_output_tokens -> flake at :3336-3355, with the budget case deliberately not a flake. `reasoning.effort` nested not flat. temperature deletes reasoning. Retry-After + backoff + jitter + 500s deadline, 4xx fail fast. Diagnostics on every turn, parsers pure. Key never in error strings, https-only except loopback, fail-closed key. Pre-send budget guard and transcript bounding (40 turns, compaction at 30 msgs / 200KB, 1M char ceiling).

## Scopes (pick later)
D1 safe alignment, no protocol change: F1 F4 F5 F6 F8 F9 — request shape + observability, unit-testable offline.
D2 continuity and context: F2 F3 F10 — transcript format change (output items + phase), truncation auto, token calibration, instructions field. Needs its own design pass.
D3 record only: no behavior change; correct the CHANGELOG claims; keep this memory shard.

## Gateway probe checklist (prerequisite for any scope)
One small request per parameter: store:false, prompt_cache_key, truncation:auto, include:[reasoning.encrypted_content], instructions, context_management. Record which are accepted, whether the response echoes model and service_tier, and whether usage.input_tokens_details.cached_tokens is populated.