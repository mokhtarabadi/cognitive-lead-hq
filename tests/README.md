# Slice: tests

## Duties

Offline-only verification suite for the HQ platform: Brain Bridge turns, capability/preflight, diff attach, bundling, prompt sync, session lifecycle, skill registry, and MCP server contracts.

## Files

- `test_brain_bridge.py` — XML extractor, prompt loader, Responses-API parser, env fallbacks.
- `test_brain_capability.py` / `test_brain_preflight.py` — Capability manifest and request preflight gates.
- `test_brain_diff_attach.py` — Diff attachment on QA/reviewer turns.
- `test_bundle_tasks.py` — META bundling, verbatim preservation, auto-archive moves.
- `test_prompt_sync.py` — Assembled prompt equals committed `system-prompt.md` (rtk mandate included).
- `test_session_lifecycle.py` / `test_loop_guard.py` — Session ledger lifecycle and spin-guard hashing.
- `test_mcp_servers.py` / `test_skill_registry.py` / `test_input_validation_pipeline.py` — Server contracts, registry, input pipeline.
- `golden/` — Golden fixtures for deterministic comparisons.

## Key Risks & Invariants

- Offline only: live LLM HTTP paths are never touched in tests.
- Prompt-sync tests are blocking gates; a drifted `system-prompt.md` must fail.
- Golden files are versioned truth; update them only with the behavior change that justifies the diff.
