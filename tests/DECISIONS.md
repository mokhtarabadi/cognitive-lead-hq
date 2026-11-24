# Architectural Decisions: tests

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-21] ADR-002: Pin the plugin lanes, not just the compaction protocol

- **Context:** The prompt-sync suite pinned the compaction literals but no goal or todolist literal, so the two lanes that never fired were also the two lanes nothing guarded. A lane that can silently disappear from the assembled prompt is exactly the failure this task set out to remove.
- **Decision:** `test_shipped_prompt_is_plugin_blind` fails on any tool name, plugin name, state path, or channel tag leaking into the assembled artifact, and `test_executor_owns_all_three_plugin_lanes` pins the full lane surface (signatures, caps, stop-marker path, corrected line references) in the context executor; the obsolete compaction-protocol presence test is removed.
- **Consequences:** A regression that drops a lane trigger or restores a stale citation fails the blocking gate instead of shipping silently.
- **Rollback:** Remove the two test functions; no production code depends on them.

## [2026-11-13] ADR-003: The zen-proxy slice gets its own suite, offline

- **Context:** The zen-proxy slice is the live path for every brain turn, yet it had no tests at all. The gap was already on record in the archived migration task, and the 2026-11-13 hardening work added four behaviours (an explicit failure contract, a bounded body read, terminal-event detection and a structured request log) that a reviewer cannot check by reading alone.
- **Decision:** Add `test_zen_proxy.py` as a slice-local suite. It loads `zen-proxy/proxy.py` by path (never by import of the installed copy) and replaces the upstream with a fake response object, so no case spends gateway quota or touches the live gateway. Every case is named after the defect it prevents, so a regression names itself.
- **Consequences:** The failure contract, the body cap, the chunked decoder, the truncated-stream rule, the fail-loud environment parsing, the credential-free log line and the allowlist merge rules are now regression-guarded. The slice can no longer be changed without a test that runs offline in under ten seconds.
- **Rollback:** Delete `tests/test_zen_proxy.py` and the two lines in `tests/README.md`; no production code depends on the suite.

## [2026-11-18] ADR-004: Pin the OpenUI validity gate on both prompt surfaces

- **Context:** A malformed `openui-lang` `Table` program shipped to `openchamber_render` and was rejected because one cell was an array instead of a plain value. The agent contract had no signature table and no pre-render self-check, and the Brain prompt had no mirror.
- **Decision:** Add `test_openui_validity_gate_in_executor_and_fragment` to `test_prompt_sync.py`, asserting the signature, plain-cell, named-argument, and diagnostic rules in both `agents/cognitive-executor.md` and `prompts/fragments/09-hands_protocols.md`. Update the two version pins to `9.90.0`.
- **Consequences:** Removing either copy of the contract breaks the shipped-prompt gate, so prompt and agent drift cannot pass silently.
- **Rollback:** Delete the test function and restore the version pins; no runtime code depends on them.

## [2026-11-22] ADR-005: Pin the render call envelope on both prompt surfaces

- **Context:** A real `openchamber_render` call was rejected with `parameters: Expected object`. The existing test pinned the `openui-lang` program gate only, so the envelope defect had no regression guard.
- **Decision:** Add `test_render_call_envelope_in_executor_and_fragment`, asserting the `action`/`parameters` object shape, the object-not-string rule, one-payload rule, and rebuild-on-error directive in both `agents/cognitive-executor.md` and `prompts/fragments/09-hands_protocols.md`. Update both version pins to 9.90.1.
- **Consequences:** Removing either copy of the envelope contract breaks the shipped-prompt gate, the same as the program gate.
- **Rollback:** Delete the test function and restore the version pins; no runtime code depends on them.

## [2026-11-23] ADR-006: Re-anchor stale fixtures, isolate shared paths, keep the guard floor

- **Context:** After the task-419 prompt reword and a prompt-lane regeneration, 17 tests failed: three stale prose/structure fixtures in `test_mcp_servers.py`, five planner tests whose fixture deleted `PLANNER_USERS_CONFIG` (falling back to the real home auth config → 401 instead of 400/404/200/500), and a shared-path race in `test_skill_registry.py` (`.tmp-validate-check.json`, green alone, red in-suite).
- **Decision:** (1) Re-anchor the executor guard to the ZAC deny-resource surface and the drift-guard mutation to a phrase verified present in HEAD; change the splitter's stale VP regex/count (`2-space indent`, `== 3`) to the real column-0, five-block structure so the byte-identity round trip is lossless — no shipped prompt edits. (2) Fix planner auth isolation at the test fixture: point `PLANNER_USERS_CONFIG` at a non-existent temp path so `_load_user_config` falls back to open local mode (fail-open on missing config — the documented no-auth behavior, not a security guard). The server's 401 is correct RFC 9110 behavior; no production change. (3) Fix the skill-registry race by per-test `tmp_path` isolation, not retry/sleep masking. (4) No test deleted to reach green; guard floor held at 960 test functions and 4 pre-existing skip/xfails.
- **Consequences:** A future prompt regeneration that changes the VP block count or indentation requires a matching splitter update; the byte-identity gate catches any mismatch. Auth-enabled planner deployments still require real credentials; only the offline tests run open mode.
- **Rollback:** Revert the three test files (`test_mcp_servers.py`, `test_planner_409_regression.py`, `test_skill_registry.py`) plus `scripts/prompt-build/split_system_prompt.py`; no runtime auth or server code was changed.

<!-- provenance: tasks/in-progress/422-regenerate-stage-prompts-every-release.md -->

## [2026-11-24] ADR-007: Pin stage freshness and release ordering offline

- **Context:** Existing stage tests skipped missing artifacts and checked content shape, not freshness. A stale stage set could therefore pass while overriding the current full prompt.
- **Decision:** Add hermetic tests that generate into temporary directories, mutate one artifact, and require the freshness gate to fail. Pin runtime fallback, fresh-artifact serving, explicit override priority, and release-script ordering.
- **Consequences:** A clean clone needs no prebuilt `build/` tree to prove the gate. Stale full prompts, stale stage prompts, and deploy-before-check regressions all fail offline.
- **Rollback:** Remove the added tests and helpers; no production behavior depends on the tests.
