---
created_at: '2026-09-19T11:50:23.064487+00:00'
status: active
tags: []
updated_at: '2026-09-19T11:50:23.064502+00:00'
---

# Responses-API servers must surface provider diagnostics

**Rule (Manager order, Task 259, 2026-09-19):** every MCP server in this repo that calls the OpenAI Responses API MUST parse and log the provider diagnostics on every turn and MUST NOT collapse a provider-side failure into a generic blank/empty error.

Applies to both servers today:

- `mcp-brain-bridge/server.py` — `parse_responses_diagnostics`, `_log_provider_diagnostics`, `_provider_error_hint`, `_provider_refusal_hint`, `_output_budget_hint`, `_maybe_warn_reasoning_budget`.
- `mcp-decision-server/server.py` — `_responses_diagnostics`, `_log_responses_diagnostics`, `_provider_failure_message`.

Required diagnostics shape (stable keys, null when absent):
`status`, `incomplete_reason`, `usage{input_tokens,output_tokens,reasoning_tokens,total_tokens}`, `error`, `refusal`.

Required empty-output branch order: top-level `error` → `refusal` → `status=="incomplete"` with `incomplete_details.reason=="max_output_tokens"` → generic flake (`EMPTY_OUTPUT_RETRY`).

Critical invariants:

- Reasoning tokens count against `max_output_tokens`, so a reasoning-heavy turn can return `status=incomplete` with zero visible text. That is `OUTPUT_BUDGET_EXHAUSTED`, a TERMINAL diagnosis — never `EMPTY_OUTPUT_RETRY`, never a lean retry, never counted as a flake retry. Remediation: lower `BRAIN_REASONING_EFFORT`/`DECISION_REASONING_EFFORT` or raise `BRAIN_MAX_TOKENS` (32768+).
- `debug.provider` attaches on EVERY brain_turn response, including successes with null fields.
- Error and refusal text surface verbatim.
- The parsers are pure and must never raise on malformed payloads (non-list nested `content`, non-finite usage numbers, malformed `error` objects).
- The 16384 default cap is unchanged; the high/xhigh reasoning budget warning is non-breaking.

Rationale: a generic "transport flake" or "non-JSON" error hides the real cause and sends callers into retry loops that can never succeed.

Supersedes: none.