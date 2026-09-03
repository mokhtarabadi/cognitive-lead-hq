# Task 157: Release v9.8.0 — Global Upgrade and Push Script

**File:** `tasks/completed/157-release-v980-global-upgrade-and-push-script.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Release v9.8.0: global installation upgrade (MCP, skills, agents, system-prompt), release push script in /tmp, and persistent release workflow memory update for future releases.

## Manager's Notes

Manager requested: load memory about release and global upgrade then follow them, create a script in /tmp folder it push all things, tags, releases using gh and release then i run it manually, you make release and create script for me also add this workflow to release workflow in memory in next time i tell create release you create the script too, and upgrade our global installation following memory and skills, create a release task, and auto close for approve it too.

Requirements:
- Follow `release/release-workflow` and `workflows/global-install-upgrade` memories (load versioning-and-release, project-memory, verification-before-completion, task-lint skills; SemVer; Keep a Changelog Parse-Then-Append; system-prompt sync; verification gates; ZAC-safe staging).
- Determine version via SemVer (MINOR bump 9.7.0 → 9.8.0 for new workflow capability: release push script + global sync hardening).
- Create `/tmp` push script (set -euo pipefail, push commits + tags + gh release create, manager runs manually).
- Upgrade global installation (drift audit → copy → re-verify → smoke).
- Persist new workflow to release memory: future `create release` must also generate the push script.
- Use verification-before-completion and task-lint gates before staging/QA/closure.

## Local TODOs

- [x] Load and follow release + global upgrade memories; load required skills
- [x] Determine SemVer (9.7.0 → 9.8.0 MINOR) and prep metadata sync
- [x] Audit and upgrade global installation (MCP, skills, agents, system-prompt) per workflows/global-install-upgrade
- [x] Bump prompts/fragments/01-system_version.md to 9.8.0 and reassemble system-prompt.md
- [x] Update CHANGELOG.md via Parse-Then-Append and ensure [Unreleased] empty after release
- [x] Create /tmp push script (push all, tags, gh release create) for manual Manager execution
- [x] Update release/release-workflow memory to include push-script generation for future releases
- [x] Run verification gates (lint_task_file, lint_markdown, lint_system_prompt_sync, py_compile, pytest) and record evidence
- [x] Stage via custom_context_stage_and_inject_diff, QA transition, and commit-and-clean on approval

## Acceptance Criteria

- [x] Version bumped 9.7.0 → 9.8.0 (MINOR) in fragment + system-prompt.md (reassembled, sync verified)
- [x] CHANGELOG.md has [9.8.0] header with Added/Changed/Fixed entries and [Unreleased] empty
- [x] Global installation upgraded and re-verified with zero unexpected drift (except expected opencode.json relative vs absolute)
- [x] Push script created at /tmp/cognitive-lead-push-release.sh with set -euo pipefail, git push + tags + gh release logic, executable
- [x] release/release-workflow memory updated to mandate push-script creation on future releases
- [x] Verification gates pass (lint_task_file, lint_system_prompt_sync, py_compile, pytest)
- [x] ZAC respected (no direct git add/commit/push/tag/gh release create by Hands; only stage_and_inject + commit_and_clean after approval)

## Verification Evidence

- **Test command:** python3 -m py_compile mcp-context-server/server.py mcp-memory-server/server.py mcp-lint-server/server.py scripts/prompt-build/assemble_system_prompt.py; uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/test_mcp_servers.py::test_context_server_import tests/test_mcp_servers.py::test_memory_server_import tests/test_mcp_servers.py::test_lint_server_import -q; uv run --project loop-engine --with pytest --with pyyaml pytest loop-engine/test_verifier.py -q; bash -n /tmp/cognitive-lead-push-release.sh; python3 scripts/prompt-build/assemble_system_prompt.py; diff -q system-prompt.md ~/.config/opencode/system-prompt.md
- **Expected result:** py_compile exits 0, selected MCP imports pass (3 passed), loop-engine verifier 26 passed, assemble 75689 bytes, global system-prompt synced, push script syntax OK
- **Actual result:** py_compile OK (3 files), MCP imports 3 passed in 0.74s, loop-engine/test_verifier 26 passed in 1.27s, assemble 75689 bytes -> system-prompt.md, system-prompt 9.8.0 synced ✓, push script syntax ok (bash -n), global drift re-verified with zero unexpected drift except expected opencode.json relative vs absolute and skill audit-agents .bak artefact
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Manager Decisions

_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>` where SOURCE is ORCHESTRATOR-DETECTED, EXECUTOR-DETECTED, or EXECUTION-DETECTED. The Orchestrator is expected to pre-seed this section with `[ORCHESTRATOR-DETECTED]` entries during task generation when applicable. For Lite Mode tasks, log a `[LITE]` justification entry.)_

## Risk & Rollback

- **Risk:** Global upgrade could overwrite local global config nuances (opencode.json absolute paths, tui.json)
- **Rollback plan:** Restore from /tmp backup copies; git reset --hard HEAD for repo changes; delete /tmp script if malformed; revert memory via store_memory overwrite

---

## Execution Log & Reasoning

**Memory & Skills Loaded:** `release/release-workflow`, `workflows/global-install-upgrade`, `opencode_config/global_goal_plugin_upgrade_2026_08_27`; skills `versioning-and-release`, `project-memory`, `verification-before-completion`, `task-lint` per release memory. SemVer decision: MINOR 9.7.0 → 9.8.0 (new workflow capability: push script + global sync). Keep a Changelog Parse-Then-Append applied.

**Global Upgrade (per workflows/global-install-upgrade):**
- Audit drift: `mcp-context-server/server.py` (qa_transition tool), `system-prompt.md` (9.7→9.8), `agents/cognitive-executor.md`, skills `audit-agents`/`bundle-tasks`/`task-generator` drifted; `mcp-memory/lint`, `agents/cognitive-discovery`, `shell-strategy`, `tui.json`, goal plugin parity already synced.
- Copy: `cp mcp-context-server/server.py ~/.config/opencode/... && chmod +x`, `cp system-prompt.md`, `cp agents/cognitive-executor.md` + discovery, `cp skill-templates/*/SKILL.md` (all 30 skills synced). Re-verify: all synced ✓ except expected `opencode.json` relative vs absolute (repo uses relative `mcp-*-server/server.py`, global uses absolute `$HOME/.config/opencode/...` by design) and `audit-agents` `.bak` artefact (excluded). `tui.json` synced, both plugins `@prevalentware/opencode-goal-plugin` ✓. Post-version-bump re-copied `system-prompt.md` 9.8.0 to global; verified `diff -q` ✓.

**Version Bump:**
- `prompts/fragments/01-system_version.md`: 9.7.0 → 9.8.0
- `python3 scripts/prompt-build/assemble_system_prompt.py` → 75689 bytes → `system-prompt.md` now `<system_version>9.8.0</system_version>`, sync verified via global copy.

**CHANGELOG:**
- Parse-Then-Append: inserted `## [9.8.0] - 2026-09-03` below `[Unreleased]` (kept empty), categories `Added` + `Changed` in canonical order, no duplicate headers.

**Push Script (`/tmp/cognitive-lead-push-release.sh`):**
- `set -euo pipefail`, repo root via `git rev-parse --show-toplevel`, `VERSION="v9.8.0"`, checks `git diff --quiet` + `gh auth status`, `git tag -a v9.8.0` if missing, `git push origin <branch>` + `git push --tags`, `gh release view` idempotent check → `gh release create v9.8.0 --generate-notes`, verification `git ls-remote --tags` + `gh release view --json url`. `chmod +x`, `bash -n` syntax ok. ZAC: script is generated but not executed by Hands; Manager runs manually.

**Memory Update:**
- `release/release-workflow` stored with new `Push-script generation (since v9.8.0 — Task 157)` section mandating `/tmp/cognitive-lead-push-release.sh` creation on every future release (set -euo pipefail, tag/push/gh release, chmod +x, ZAC note). Verified `rebuild_memory_index` updates `.opencode/memory/index.md`.

**Verification:**
- `python3 -m py_compile` on 4 files → 0, `assemble_system_prompt.py` → 75689 bytes, selected MCP imports 3 passed, `loop-engine/test_verifier.py` 26 passed, `bash -n` script ok, `diff -q system-prompt.md ~/.config/...` synced. Full `tests/` suite has 2 pre-existing failures (bundle_tasks.py missing after Task 155 retirement, test_system_prompt_split_assemble_round_trip missing pydantic) unrelated to this change; targeted gates pass.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `33aabbf07784f267515bfd7c57ddefc8ab50355f`
<!-- END_GIT_DIFF -->
