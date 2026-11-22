# Task 412: DeepSeek Chat Completions Hardening

**File:** `tasks/completed/412-deepseek-chatcompletions-hardening.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-22T15:22:57Z
**Submitted:** 2026-11-22T14:55:01Z

## Goal

Harden the brain bridge (mcp-brain-bridge) for DeepSeek V4.1 Flash running over the OpenAI-compatible chat completions API with reasoning effort `max`. Work covers: output token enhancement (BRAIN_MAX_TOKENS=131072), usage-details passthrough (cache hits + reasoning tokens) in the response converter, and a warning branch for dropped input item types. Verified against DeepSeek's official API docs.

## Manager's Notes

Switched BRAIN to DeepSeek V4.1 Flash 1017 over /go/chat (chat completions) with reasoning_effort=max. Audited converter against DeepSeek docs; only real issues were usage-details passthrough and output-token sizing. Temperature and `max` effort validated as non-issues.

## Local TODOs

- [x] Switch .env to DeepSeek chat mount + max effort
- [x] Enhance output token size (BRAIN_MAX_TOKENS=131072)
- [x] Pass through usage details (F6)
- [x] Add warning branch for dropped input items (F4)
- [x] Run lint_task_file
- [x] Stage via custom_context_stage_and_inject_diff
- [x] QA transition

## Acceptance Criteria

- [x] `uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_responses_alignment.py` exits 0
- [x] `lint_task_file` passes on this task file
- [x] Smoke brain_turn returns XML_EXTRACTED with reasoning_tokens visible in usage
- [x] CHANGELOG.md updated

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_responses_alignment.py -q
- **Expected result:** All tests pass
- **Actual result:** 390 passed in 2.88s
- **Exit code:** 0

### Post-fix verification (QA rejection round 2)

- **Syntax check:** `uv run --project mcp-brain-bridge python -c "import ast,pathlib; [ast.parse(pathlib.Path(p).read_text()) for p in ['mcp-brain-bridge/server.py','tests/test_brain_bridge.py','tests/test_brain_responses_alignment.py']]"` — exit 0.
- **Declared tooling:** `grep -n "ruff|mypy|black|isort" mcp-brain-bridge/pyproject.toml` — no match; skip (no lint tool declared).
- **V1 advisory gate:** `grep -n "usage\\[" mcp-brain-bridge/server.py` + `grep -n "sum(\\|\\.values()" mcp-brain-bridge/server.py | grep -i usage` — no numeric consumers over usage; verdict "usage type widening has no numeric consumers". Readers use `.get`.
- **Full suite (RTK):** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_responses_alignment.py -q` — exit 0, 396 passed in 4.47s.
- **Smoke:** live brain_turn under task 412 — status REPORT, usage reasoning_tokens=6115.
- **Lint:** `lint_task_file` on `tasks/qa/412-deepseek-chatcompletions-hardening.md` — pass.
- **Closure suite (RTK):** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_responses_alignment.py -q` — `396 passed in 4.48s` — exit 0
- **Tooling skip record (four fields):** root=`mcp-brain-bridge`; marker scan=`mcp-brain-bridge/pyproject.toml` + repo-root `pyproject.toml`; matched skills=none (no ruff/mypy/black/isort declared; plain stdlib server); reason=no lint/type tool declared for this component.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

## Risk & Rollback

- **Risk:** Output token default raised; larger bills if max effort overused. Mitigated by .env override (code default stays 32768).
- **Rollback plan:** Revert .env BRAIN_MAX_TOKENS to 32768; revert server.py usage-details edit.

---

## Execution Log & Reasoning

Implementation completed 2026-11-22. Changes:
- .env: BRAIN_API_BASE=/go/chat, BRAIN_UPSTREAM_MODE=chat_completions, BRAIN_MODEL=deepseek-v4.1-flash (all tiers), BRAIN_REASONING_EFFORT=max, BRAIN_MAX_TOKENS=131072.
- mcp-brain-bridge/server.py: _convert_chat_completions_to_responses_data now passes through input_tokens_details (cached_tokens/prompt_cache_hit_tokens) and output_tokens_details (reasoning_tokens etc.); added warning branch for dropped input item types.
- Memory updated: brain-model-routing + brain-deepseek-fixes.
- Tests: 390 passed. Smoke: XML_EXTRACTED, reasoning_tokens=9111.

### QA rejection round 1 fixes

- Added 6 regression tests: T1 OpenAI nested details passthrough, T2 DeepSeek top-level folding, T3 nested-over-top-level precedence, T4 malformed/absent details (no leak), T5 unsupported input item dropped with exactly one warning, T6 non-dict item reported without crashing.
- CHANGELOG.md: appended Fixed entry under [Unreleased] for usage-details passthrough + dropped-item warning.
- V1-V3 advisory gate: grep for sum()/.values() over usage returned no matches; readers use .get; verdict "usage type widening has no numeric consumers". V4 (bool isinstance) remains advisory, pre-existing.
- Smoke evidence: reasoning_tokens=6115 from live brain_turn under task 412.
- DECISIONS.md: appended dated ADR for chat-completions usage details passthrough.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `97c70975866874d0d04d6096d5ea3f6323665bca`
<!-- END_GIT_DIFF -->
