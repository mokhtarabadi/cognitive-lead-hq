# Task 426: Evaluate migrating Brain to LiteLLM

**File:** `tasks/in-progress/426-evaluate-litellm-migration-for-brain.md`
**Source:** manager
**Type:** research
**Status:** in-progress
**Started:** 2026-11-27T07:40:49Z

## Goal

Evaluate whether to migrate the Brain from its current Python proxy +
opencode-v2 identity implementation to LiteLLM. Determine how much custom code
would be removed (LiteLLM handles identity/routing natively), what breaks, and
whether the migration is worth it. Produce a recommendation with evidence.

## Manager's Notes (verbatim intent)

"برای خود برین رو نگاه کنی بعد ببینی آیا ارزشش داره مایگریت کنی بری سمت لایت ال ال ام یا همین چیزی که هست رو نگه داریم؛ چون بریم سمت لایت ال ال ام یه بخش خیلی خوبی از کدهایی که نوشتیم پاک میشه، دیگه نیاز نیست ما هندل کنیم، خود اون لایت ال ال ام هندل میکنه، بخش عظیمی از کدها پاک میشه."

## Local TODOs

- [x] Inspect current Brain MCP bridge request construction
- [x] Research LiteLLM support for OpenCode Go / custom headers / proxy CONNECT
- [x] Estimate code removed vs added
- [x] Produce recommendation

## Acceptance Criteria

- [x] Evidence-based recommendation with file citations
- [x] List of code that LiteLLM would replace
- [x] Migration risk notes

## LiteLLM Evaluation

Options:
- O1 (migrate now): Replace `_post_with_retry`, `_make_client`, `_upstream_mode/_upstream_url`, and conversion helpers with LiteLLM. Risk: custom model registration for muse-spark-1.3-contributor, identity header hook, re-test all retry/error/timeout behavior.
- O2 (adapter-gated pilot): Add `BRAIN_UPSTREAM_MODE=litellm` behind a feature flag; keep current path as default. Lower risk, reversible.
- O3 (no migration): Keep current verified stack.

Scope touched by any migration: mcp-brain-bridge/server.py transport/conversion, zen-proxy identity headers (may reduce), docs/config.

Interface delta: Brain uses OpenAI Responses API; LiteLLM supports `/responses` and translates to chat completions when needed. OpenCode Go models use `opencode_go/` prefix; muse-spark-1.3-contributor not in published catalog (needs custom registration).

Risk: retry semantics, 429 terminal handling, timeout mapping, identity headers, quota behavior, streaming XML extraction.

Cost/latency/observability: LiteLLM adds cost tracking and fallbacks; current stack has no cost dashboard but is verified and simple.

Rollback: revert env + dependency; no code change needed for O3.

## Recommendation

Winner: O3 (no migration) for now. The current stack is verified (health, models, chat, responses, CONNECT all 200, brain_turn works). Migrating to LiteLLM is only justified for multi-provider fallback, cost dashboards, or model routing across providers — none is a current requirement. If pursued later, use O2 behind `BRAIN_UPSTREAM_MODE=litellm` as a reversible experiment; do not replace the current path outright.

No implementation performed in this discovery task.

## Risk & Rollback

- **Risk:** migration would add LiteLLM dependency and reintroduce custom hooks; muse-spark-1.3-contributor not in catalog.
- **Rollback:** keep current stack; no code changes performed.

## Verification Evidence

Commands and citations:
- grep -n "BRAIN_API_BASE\|/responses\|_post_with_retry\|_make_client" mcp-brain-bridge/server.py (lines 2844, 2833, 2986, 5383, 5385, 4998)
- docs.litellm.ai/docs/providers/opencode_go fetched 2026-11-27 (session headers, model prefix, custom headers)
- docs.litellm.ai/docs/response_api fetched 2026-11-27 (/responses support)
- gist.github.com/CL0SeY/e174c5fa1f58487122b0b7e767dee0dd (session hook pattern)
- grep -n "muse-spark-1.3-contributor" models.litellm.ai/providers/opencode_go -> not present in catalog

## Definition of Done

- [x] Findings recorded; task remains in backlog for Manager review

## Execution Log & Reasoning

Discovery (2026-11-27):
- Brain MCP server is a single Python file (mcp-brain-bridge/server.py, 6458 lines) using httpx directly over OpenAI Responses API (`{BRAIN_API_BASE}/responses`), with built-in retry/backoff, 429 terminal handling, responses<->chat-completions conversion, and stage-tier routing. It sends only `Authorization: Bearer <key>`; all OpenCode identity headers are injected by `zen-proxy/proxy.py`.
- zen-proxy is now a dependency-free Python proxy (17 KB) doing cached identity generation, CONNECT tunneling, endpoint mapping, header injection, and upstream proxy support.
- LiteLLM (docs fetched 2026-11-27) natively supports the OpenAI Responses API (`/responses`), OpenCode Go models via `opencode_go/` prefix, session headers via `litellm_session_id` / `x-litellm-session-id` (forwarded as `x-opencode-session`), cost tracking, retries, fallbacks, and load balancing. It also supports custom headers via `extra_headers` in litellm_params and `forward_client_headers_to_llm_api`.
- However, `muse-spark-1.3-contributor` (the Brain's current model) is not in LiteLLM's published OpenCode Go catalog (30 models listed; muse-spark not among them). It would need custom model registration or an openai-compatible override with `supported_endpoints`.
- LiteLLM does NOT automatically inject the OpenCode free-tier identity bundle (preamble, tool manifest, client/project headers); for OpenCode Go it forwards `x-opencode-session` only when supplied. For our paid Go mount the identity headers are still required upstream; LiteLLM can carry them via `extra_headers` or a pre-call hook, but that reintroduces custom code.
- Migration estimate: replacing `_post_with_retry`, `_make_client`, `_upstream_mode/_upstream_url`, and the conversion helpers would remove ~400-600 lines of Brain transport code, but requires adding LiteLLM as a dependency, a custom pre-call hook for identity headers, custom model registration for muse-spark-1.3-contributor, and re-testing all retry/error/timeout behavior. The Brain's XML extraction and reporting logic is unaffected.
- Recommendation: KEEP the current stack for now. The custom proxy + httpx path is already verified (63 tests, CONNECT, all endpoints 200, brain_turn works). Migrating to LiteLLM is only justified if we need multi-provider fallback, cost dashboards, or model routing across providers — none is a current requirement. If pursued, do it as a separate, reversible experiment behind a feature flag (`BRAIN_UPSTREAM_MODE=litellm`), not a replacement.
- LiteLLM would NOT remove the need for zen-proxy unless we also stop injecting identity headers; OpenCode Go still requires them. So the proxy (or an equivalent hook) stays either way.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
"""