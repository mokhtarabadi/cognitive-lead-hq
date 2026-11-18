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
