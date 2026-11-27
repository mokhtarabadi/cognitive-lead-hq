# Slice: tests

## Duties

Offline-only verification suite for the HQ platform: Brain Bridge turns, capability/preflight, diff attach, bundling, prompt sync, session lifecycle, skill registry, and MCP server contracts.

## Files

- `test_brain_bridge.py` — XML extractor, prompt loader, Responses-API parser, env fallbacks.
- `test_raw_output_recovery.py` — Raw-before-triage equality, truthful counts, compact reject transcript, deterministic helper, and partial-block non-executability.
- `test_brain_capability.py` / `test_brain_preflight.py` — Capability manifest and request preflight gates.
- `test_brain_diff_attach.py` — Diff attachment on QA/reviewer turns.
- `test_bundle_tasks.py` — META bundling, verbatim preservation, auto-archive moves.
- `test_prompt_sync.py` — Assembled prompt equals committed `system-prompt.md` (rtk mandate included).
- `test_versioning_skill_portability.py` — Rejects harness literals in the portable release core and preserves the optional profile.
- `test_executor_recovery_gate.py` — Pins mandatory recovery for omitted, truncated, and Brain-pointered output.
- `test_brain_orchestration_skill.py` — Pins Brain participants, seats, stages, gates, and portable authority wording.
- `test_stage_prompts.py` — Stage routing, runtime freshness fallback, assembler freshness gate, and release ordering.
- `test_session_lifecycle.py` / `test_loop_guard.py` — Session ledger lifecycle and spin-guard hashing.
- `test_mcp_servers.py` / `test_skill_registry.py` / `test_input_validation_pipeline.py` — Server contracts, registry, input pipeline.
- `test_litellm_double.py` — the shared offline LiteLLM double every Brain suite scripts through.
- `golden/` — Golden fixtures for deterministic comparisons.

## Test isolation & fixture re-anchoring

Offline tests must own every path they write. Use the pytest `tmp_path` fixture for scratch files instead of a repo-root fixed path (a shared `.tmp-validate-check.json` caused an in-suite-only race). Planner tests point `PLANNER_USERS_CONFIG` at a non-existent temp path for open local mode; deleting the env var falls back to the real home auth config and returns 401. Prompt-structure fixtures re-anchor to contract strings verified present in HEAD; when the assembled prompt's validation_phase blocks change, update the splitter's regex/count together with the byte-identity gate. See `DECISIONS.md` ADR-006.

## Key Risks & Invariants

- Offline only: live LLM HTTP paths are never touched in tests.
- Prompt-sync tests are blocking gates; a drifted `system-prompt.md` must fail.
- The OpenUI validity gate and the `openchamber_render` call envelope are pinned in both the executor agent and the hands-protocol fragment; removing either side fails the suite.
- Golden files are versioned truth; update them only with the behavior change that justifies the diff.
- The zen-bridge suite replaces the upstream with a fake response object, so it never spends gateway quota.
