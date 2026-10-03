# Task 288: Adopt the Smart Compact Plugin in HQ

**File:** `tasks/completed/288-adopt-smart-compact-plugin.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Point the HQ documentation, system prompt, agent, and memory at our own V2-native `@mokhtarabadi/opencode-smart-compact` plugin, which replaces the V1-era `magic-compact` package that does not load on OpenCode 2. Native auto-compaction stays as the safety net; Smart Compact is the manual high-fidelity layer.

## Manager's Notes

Manager order: review the smart-compact project, learn it, update our docs relative to it if needed, install it locally, then restart OpenCode and smoke test for correctness and safety. The plugin repo (`mokhtarabadi/opencode-smart-compact`) is maintained separately; this task only updates the HQ side and the global config.

## Local TODOs

- [x] Review the smart-compact repo and run its gates (typecheck, 14 tests, verify:package)
- [x] Rewrite `<compaction_protocol>` (fragment 22) and the executor compaction section for smart-compact
- [x] Update `README.md`, `LLM.txt` (§7 JSON + §7.7), and `docs/compaction.md`
- [x] Update the `opencode_config` memory to the smart-compact policy
- [x] Bump `<system_version>` 9.50.0 → 9.51.0, regenerate, update prompt-sync tests
- [x] Point global `plugins` at the plugin and sync the prompt + agent globally

## Acceptance Criteria

- [ ] No HQ doc, prompt fragment, agent, or memory presents `magic-compact` as the active plugin (historical CHANGELOG/history stays)
- [ ] `system-prompt.md` is 9.51.0, contains `<compaction_protocol>` referencing smart-compact, byte-identical on re-assemble
- [ ] `tests/test_prompt_sync.py` pins 9.51.0 and asserts the smart-compact contract
- [ ] Global `opencode.json` `plugins` points at `@mokhtarabadi/opencode-smart-compact` (or the local checkout) with `compaction` intact
- [ ] Targeted prompt-sync + context-server suites pass with exit code 0

## Verification Evidence

- **Test command:** rtk test uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/test_prompt_sync.py tests/test_mcp_servers.py -q
- **Expected result:** pass, exit code 0
- **Actual result:** `83 passed`
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** the plugin is loaded by OpenCode only after a restart; the smoke test is pending.
- **Rollback plan:** point `plugins` back to the previous entry or remove it; revert the HQ doc/prompt hunks.

---

## Execution Log & Reasoning

**Review:** the smart-compact repo is a clean-room V2-native rewrite — 9 source modules, 14 passing unit tests, `tsc --noEmit` clean, `verify:package` OK. It never mutates the stored transcript; it stores per-session state and applies it to model-visible messages via `session.hook("context")`, which is exactly the V2-native design we chose over porting the V1 plugin.

**Changes:** rewrote fragment 22 and the executor compaction section; updated `README.md`, `LLM.txt` (§7 JSON `plugins` entry + §7.7), and `docs/compaction.md`; updated the `opencode_config` memory; bumped `<system_version>` to 9.51.0 and regenerated; updated the prompt-sync tests; set global `plugins` to the plugin's local path (until it is published to npm) and synced the prompt + agent globally.

**Pending:** OpenCode restart to load the plugin, then the live smoke test (`/magic-compact`, `/magic-trim`, `/magic-stats`, `read_omitted_content`).

**Smoke test (post-restart):** the absolute-path `plugins` entry was silently ignored (OpenCode's `opencode plugin add` rejects bare local paths), so the install was switched to the Git spec `github:mokhtarabadi/opencode-smart-compact`. The plugin then loaded cleanly (log shows repeated `loading plugin id=github:mokhtarabadi/opencode-smart-compact`, no `failed to load plugin`), `read_omitted_content` is registered in the tool catalog and executes (returned the session-scoped not-found message), and `compaction` stays active. Works and is safe: no transcript mutation, session-scoped storage, no network/shell/filesystem writes beyond reading the two config files.

**Closure executed** on Manager quote "Approved for closure": file moved from `tasks/qa/` to `tasks/completed/` with Status `closed`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `0c1dbbf65c7b37f7c60c3607a07ed4b9e1ecd734`
<!-- END_GIT_DIFF -->
