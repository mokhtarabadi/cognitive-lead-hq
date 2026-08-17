# Task 100: Release v8.4.6 — Consolidate CHANGELOG and Store Release Workflow Memory

**File:** `tasks/archive/100-release-v846-consolidate-changelog-and-store-release-workflow-memory.md`
**Source:** orchestrator
**Type:** chore
**Status:** closed

## Goal

Prepare release v8.4.6: consolidate the pending `[Unreleased]` CHANGELOG entry into the existing `[8.4.6]` section, store the future release workflow as persistent project memory (`release/release-workflow`), verify all release gates (lint, prompt sync, compile, tests), and leave `[Unreleased]` present but empty. Release publication (tag/push/GitHub release) is a separate manual Manager step after closure — the Hands perform NO tag/push/release commands. Note: the Orchestrator suggested `Type: release/maintenance`; the lint contract only accepts `bug|improvement|feature|chore|docs|refactor|security|research|infra`, so `Type: chore` is used instead (documented substitution).

## Local TODOs

- [x] **Step 1:** Discover the next task ID via the task-generator ID discovery rule and create this task file in `tasks/backlog/` using the canonical template.
- [x] **Step 2:** Move the task file to `tasks/in-progress/` via the authorized `git mv` (filesystem `mv` if untracked); update the `**File:**` header to the new path.
- [x] **Step 3:** Store the future release workflow memory — search memory for release/versioning/changelog/semver keywords, then `store_memory` namespace `release`, key `release-workflow`, `overwrite: true` with the canonical memory content.
- [x] **Step 4:** Verify the stored memory via `read_memory` (namespace `release`, key `release-workflow`); record the actual memory file path in the Execution Log.
- [x] **Step 5:** Consolidate `CHANGELOG.md` for release v8.4.6 — move the `[Unreleased]` Fixed entry (Freebuff free-tier spawn status docs hotfix) into `[8.4.6]` `### Fixed` via Parse-Then-Append (no duplicate, no wording deletion); leave `[Unreleased]` header present but empty.
- [x] **Step 6:** Add the release-preparation entry under `[8.4.6]` `### Changed` (create the category in canonical order if absent) with the specified wording.
- [x] **Step 7:** Verify CHANGELOG formatting via `lint_markdown`; fix Markdown structure and re-run if lint fails.
- [x] **Step 8:** Update the active task file with release decisions, memory storage result, CHANGELOG consolidation result, and all verification evidence (English).

## Acceptance Criteria

- [x] (a) Task file created with canonical template, correct ID 100, valid lint metadata (`Type: chore`), BEGIN/END_GIT_DIFF markers.
- [x] (b) Release workflow memory stored at namespace `release` / key `release-workflow` (file `.opencode/memory/release/release-workflow.md` or actual server path) with the exact canonical content; verified via `read_memory`.
- [x] (c) CHANGELOG `[Unreleased]` Fixed entry moved (not duplicated) into `[8.4.6]` `### Fixed`; `[Unreleased]` header present but empty; no historical wording deleted.
- [x] (d) Release-preparation entry added under `[8.4.6]` `### Changed` with the exact specified wording.
- [x] (e) `lint_markdown` passes on CHANGELOG.md; `lint_system_prompt_sync` reports in sync; py_compile exit 0; full pytest suite passes.
- [x] (f) No tag/push/GitHub release performed by the Hands (ZAC); release publication left as a separate manual Manager step.

## Verification Evidence

- **Test command:** `python3 -m py_compile scripts/prompt-build/split_system_prompt.py scripts/prompt-build/assemble_system_prompt.py mcp-lint-server/server.py` then `uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q`
- **Expected result:** py_compile exit 0; pytest all pass (exit 0); `lint_system_prompt_sync` reports `✅ system-prompt.md is in sync with prompts/`; `lint_markdown` passes on CHANGELOG.md.
- **Actual result:**
  - Task ID discovery: `find tasks/ -type f -name '*.md'` → highest ID 99 (completed/), next ID **100**; no collision in backlog/.
  - Memory storage: `store_memory(namespace=release, key=release-workflow, overwrite=true)` → stored at `.opencode/memory/release/release-workflow.md`; verified via `read_memory` (content matches canonical text exactly).
  - CHANGELOG consolidation: Freebuff free-tier spawn status docs hotfix moved from `[Unreleased]` `### Fixed` into `[8.4.6]` `### Fixed` — `grep -c "Freebuff free-tier spawn status verified and corrected"` = **1** (moved, not duplicated); `[Unreleased]` header present but empty.
  - Release-preparation entry added under `[8.4.6]` `### Changed` with the exact specified wording.
  - `lint_markdown` on CHANGELOG.md: ✅ passed.
  - `python3 -m py_compile scripts/prompt-build/split_system_prompt.py scripts/prompt-build/assemble_system_prompt.py mcp-lint-server/server.py` → exit code **0**.
  - Full pytest suite: **45 passed, 9 warnings**, exit code **0**.
  - `lint_system_prompt_sync`: `✅ system-prompt.md is in sync with prompts/`.
  - ZAC-safe release note: NO `git tag`, `git push`, or `gh release create` performed by the Hands — release publication is a separate manual Manager step after closure.
- **Exit code:** 0 (pytest)

## Risk & Rollback

- **Risk:** CHANGELOG consolidation could accidentally duplicate or delete historical wording, or leave `[Unreleased]` non-empty (release-gate violation). Mitigation: Parse-Then-Append with explicit no-duplicate check; `lint_markdown` gate on CHANGELOG.md; the `[Unreleased]` header is left present but empty per Keep a Changelog. Rollback: revert the CHANGELOG edits (working tree is uncommitted until Manager closure approval); memory file can be overwritten/deleted via the memory MCP server if needed.

---

## Execution Log & Reasoning

### Release v8.4.6 Preparation (Task 100)

**Discovered task ID:** 100 (highest existing ID was 99 in `tasks/completed/`; no collision in `tasks/backlog/` — verified via the task-generator ID discovery rule).

**Type metadata substitution (documented):** the Orchestrator suggested `Type: release/maintenance`, but the lint contract (`_check_task_file_structure` in `mcp-lint-server/server.py`) only accepts `bug|improvement|feature|chore|docs|refactor|security|research|infra`. Used `Type: chore` instead (consistent with the CHANGELOG's own `chore: close task N` convention) so the task file passes `lint_task_file`. No other metadata changed.

**Release workflow memory stored:** namespace `release`, key `release-workflow`, `overwrite=true`. Actual memory file path: `.opencode/memory/release/release-workflow.md` (confirmed by the project_memory MCP server on store and verified via `read_memory` — content matches the canonical text byte-for-byte, including frontmatter `status: active`). No prior release-workflow memory existed (search returned no matches), so no supersession was required. The memory captures: SemVer decision rules, Keep a Changelog / Parse-Then-Append rules, the empty-`[Unreleased]` rule, prompt-source rules (generated `system-prompt.md`, never hand-edit, sync verification), verification gates, ZAC-safe commit rules (no tag/push by Hands; publication is a separate manual Manager step), and the memory-rule pointer (`release/release-workflow`).

**CHANGELOG consolidation actions:**
1. Moved the `[Unreleased]` `### Fixed` bullet (Freebuff free-tier spawn status docs hotfix, 2026-08-13) into the existing `[8.4.6] - 2026-08-16` section under `### Fixed`, appending it after the QA Fix Round 4 bullet. Verified via `grep -c` that the entry appears exactly once (moved, NOT duplicated) and no historical wording was deleted.
2. Left `## [Unreleased]` header present but empty (Keep a Changelog rule: `[Unreleased]` MUST be empty after a release — this is now satisfied).
3. Added the release-preparation entry under `[8.4.6]` `### Changed` (category already existed — appended, no duplicate category header): "Release v8.4.6 preparation — consolidated the [Unreleased] docs hotfix under [8.4.6], stored persistent release workflow memory at release/release-workflow, and verified release gates. system-prompt.md version unchanged." (The `system-prompt.md version unchanged` statement is correct: this task edited no prompt source, and `lint_system_prompt_sync` confirms the generated file is in sync at 8.4.6.)

**Release verification results:**
- `lint_markdown` on CHANGELOG.md: ✅ passed.
- `python3 -m py_compile` (splitter, assembler, lint server): exit 0.
- Full pytest suite: 45 passed, exit 0.
- `lint_system_prompt_sync`: `✅ system-prompt.md is in sync with prompts/`.

**ZAC-safe release publication note:** the Hands performed NO `git tag`, `git push`, or `gh release create` in this task. Public tag/release publication (e.g. `git tag v8.4.6` + push + GitHub release) is a separate manual Manager step after task closure, per the stored release workflow memory and the Orchestrator's explicit instruction.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/release/release-workflow.md b/.opencode/memory/release/release-workflow.md
new file mode 100644
index 0000000..9abca80
--- /dev/null
+++ b/.opencode/memory/release/release-workflow.md
@@ -0,0 +1,48 @@
+---
+created_at: '2026-08-17T09:55:12.993426+00:00'
+status: active
+tags: []
+updated_at: '2026-08-17T09:55:12.993444+00:00'
+---
+
+Release workflow for cognitive-lead-hq.
+
+Purpose: standardize future releases and prevent forgotten release gates.
+
+Before every release:
+- Load these skills: versioning-and-release, project-memory, verification-before-completion, task-lint.
+- Search project memory for release constraints and prior release decisions.
+- Confirm the release version against SemVer:
+  - PATCH: bug fixes, docs sync, formatting, metadata-only changes.
+  - MINOR: new skills, new workflow capabilities, non-breaking architectural upgrades.
+  - MAJOR: breaking workflow changes or full system prompt protocol rewrites.
+
+CHANGELOG rules:
+- Use Keep a Changelog format.
+- Use Parse-Then-Append: never create duplicate version headers or duplicate category headers.
+- Categories: Added, Changed, Deprecated, Removed, Fixed, Security.
+- The [Unreleased] section MUST be empty after a release. Move all entries under the release version header before closing the release task.
+- If system-prompt.md behavior changes, bump prompts/fragments/01-system_version.md and reassemble via scripts/prompt-build/assemble_system_prompt.py.
+- If the release is metadata/docs-only, the CHANGELOG entry MUST explicitly state: system-prompt.md version unchanged.
+
+Prompt source rules:
+- system-prompt.md is generated from prompts/fragments/ and prompts/shared/.
+- Never hand-edit system-prompt.md.
+- Before release staging, verify sync with lint_system_prompt_sync or by assembling to a temp path and diffing against system-prompt.md.
+
+Verification gates before staging:
+- lint_task_file passes for the active release task.
+- lint_markdown passes for edited Markdown files.
+- lint_system_prompt_sync reports in sync.
+- python3 -m py_compile passes for prompt-build scripts and lint server.
+- full pytest suite passes.
+
+ZAC-safe commit rules:
+- Hands MUST NOT run git add, git commit, git push, git tag, or gh release create.
+- Hands stage only via custom_context_stage_and_inject_diff.
+- Hands commit only via custom_context_commit_and_clean_task after explicit Manager closure approval.
+- Public tag/release publication is a separate manual Manager step after closure.
+
+Memory rule:
+- This memory lives at release/release-workflow.
+- Future release tasks must retrieve and follow this memory before making release decisions.
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5355ed1..1d25b99 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,22 +6,6 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
-### Fixed
-
-- **Freebuff free-tier spawn status verified and corrected (docs hotfix, 2026-08-13)** — the "manual
-  verification item" status for the custom agents' live free-tier spawn is **closed**: binary analysis of the
-  Freebuff CLI `0.0.149` plus a live `@Cognitive Executor say hello` session proved the free tier CANNOT spawn
-  custom local `.agents/*.ts` agents. Root cause: the default free agent (`base3-free-deepseek-flash`) has no
-  `spawn_agents` tool in its whitelist, and the free-tier orchestrator (`base2-free-*`) only whitelists
-  built-in Codebuff subagents — the client-side spawn validation rejects anything else with `Agent "..." is
-not available to spawn` (the earlier `model`-omission fix was necessary but not sufficient). Docs updated:
-  `docs/freebuff-support.md` (header status, §3.3 verification evidence, §4 matrix, §5 rewrite, §6 step 4,
-  §7 step 6, §8 drift note), `README.md` Freebuff matrix + guide link, and `LLM.txt` Step 7.5 note. Corrected
-  guidance: on the free tier paste `<hands_*_task>` blocks into the base chat (all MCP tools + skills +
-  `~/.AGENTS.md` loaded) or switch to a `base2-free-*` "Free Orchestrator" agent to spawn Freebuff's built-in
-  subagents; custom agents require a credits/paid tier. `system-prompt.md` version unchanged (metadata/docs-only).
-  Verified: `lint_markdown` on all edited docs ✅, prettier ✅.
-
 ## [8.4.6] - 2026-08-16
 
 ### Added
@@ -37,6 +21,7 @@ not available to spawn` (the earlier `model`-omission fix was necessary but not
 ### Changed
 
 - **`system-prompt.md` is now generated, not hand-edited** — edits go in `prompts/fragments/` or `prompts/shared/`, then regenerate via `python3 scripts/prompt-build/assemble_system_prompt.py`. The "Customizing for Yourself" section of `README.md` was updated to point to `prompts/fragments/04-manager_profile.md` instead of `system-prompt.md` directly. Version bumped 8.4.5 → **8.4.6** (the ONLY byte difference from the pre-task monolithic file; verified by round-trip diff: zero differences pre-bump, only the `<system_version>` line post-bump). `README.md` repository structure tree updated to include the `prompts/` and `scripts/prompt-build/` entries. `docs/system-prompt-modularization.md` given a status note pointing to Task 99.
+- **Release v8.4.6 preparation** — consolidated the [Unreleased] docs hotfix under [8.4.6], stored persistent release workflow memory at release/release-workflow, and verified release gates. system-prompt.md version unchanged.
 
 ### Fixed
 
@@ -48,6 +33,19 @@ not available to spawn` (the earlier `model`-omission fix was necessary but not
   - **QA Fix Round 2 (ValueError catch composition gap)** — `_check_system_prompt_sync()` in `mcp-lint-server/server.py` only caught `FileNotFoundError` around `assembler.assemble(...)`, so if a fragment tree contained an unresolved `{{PLACEHOLDER}}`, the `ValueError` raised by `assemble()` (round-1 V2 behavior, intentional for CLI callers) would propagate out and crash the lint diagnostic tool. Widened the exception handling to also catch `ValueError`, returning a clean `(False, f"Error: {e}")` tuple (message still identifies the fragment + placeholder); the `FileNotFoundError` branch wording is unchanged. Added regression test `test_lint_system_prompt_sync_handles_unresolved_placeholder` (reuses the round-1 `{{FOO}}` fixture shape but drives `_check_system_prompt_sync()`, asserting a clean `(False, <message>)` without raising). Total regression tests: 37 → **38** (all passing).
   - **QA Fix Round 3 (include-path safety + lint diagnostic hardening)** — (1) **Include-path traversal rejection**: `scripts/prompt-build/assemble_system_prompt.py` gained a `_safe_include_path(rel_path, prompts_dir)` helper that rejects absolute include paths and resolves every include path against the `prompts/` boundary (raising `ValueError` for `..` traversal or any resolution outside `prompts/`), closing a hole where a marker like `<!--INCLUDE:../outside.md-->` could read an arbitrary file outside the prompt source tree. (2) **Malformed/unresolved include-marker rejection**: after include resolution, each fragment is scanned for any remaining literal `<!--INCLUDE:` substring (e.g. a marker with a broken `--!>` closing); if found, `ValueError` names the fragment — malformed markers never leak into the generated `system-prompt.md`. This guard runs BEFORE the unresolved-placeholder check. (3) **Lint diagnostic exception hardening**: `_check_system_prompt_sync()` now wraps the post-guard region (assembler load, assembly, temp/committed file reads, diff generation) in a broad `except Exception` handler (NOT catching `SystemExit`/`KeyboardInterrupt`) returning `(False, f"Error: {e}")`, with `finally` temp cleanup preserved — a misconfigured `fragments_dir` (e.g. a regular file), a missing include file, or any unexpected exception degrades to an error string instead of crashing the MCP lint server; `assemble()` itself still fails loudly for CLI callers. `prompts/README.md` documents the include-path safety contract. Four regression tests added (38 → **42**): `test_assemble_rejects_path_traversal_include`, `test_assemble_rejects_malformed_include_marker`, `test_lint_system_prompt_sync_missing_include_file`, `test_lint_system_prompt_sync_invalid_fragments_dir_configuration`. Reference audit (read-only): `AGENTS.md`/`LLM.txt` do not yet describe the generated-artifact workflow — documented gap for a separate follow-up docs task. Verified: py_compile exit 0, pytest 42/42 exit 0, fresh assembler diff exit 0 (byte-identical), `lint_system_prompt_sync` ✅ in sync.
   - **QA Fix Round 4 (manifest-path safety + assembler-load hardening)** — (1) **Manifest-entry path-traversal rejection**: `scripts/prompt-build/assemble_system_prompt.py` gained a `_safe_fragment_path(filename, fragments_dir)` helper treating the manifest (`prompts/manifest.txt`) as an untrusted input surface — empty manifest entries are rejected, absolute entries are rejected, and every entry is resolved via `Path.resolve()` and must remain inside `prompts/fragments/` (raising `ValueError` naming the unsafe entry for `..` traversal or any escape of `fragments/`), closing the same traversal hole as round 3 but on the fragment-read path. (2) **Absolute manifest-entry rejection**: absolute paths in the manifest are rejected outright — only filenames relative to `fragments/` are part of the manifest API. (3) **Assembler-load exception hardening**: `_check_system_prompt_sync()` in `mcp-lint-server/server.py` keeps the specific `FileNotFoundError` handler for `_load_assembler()` and adds a generic `except Exception` handler returning `(False, f"Error: {e}")` — `_load_assembler()` dynamically executes Python source via importlib and can raise `SyntaxError`/`ImportError` if the script is corrupted, so the MCP diagnostic tool degrades gracefully instead of crashing (`SystemExit`/`KeyboardInterrupt` deliberately not caught). Three regression tests added (42 → **45**): `test_assemble_rejects_path_traversal_manifest_entry`, `test_assemble_rejects_absolute_manifest_entry`, `test_lint_system_prompt_sync_handles_assembler_load_failure` (monkeypatched `SyntaxError` load failure). TDD flow honored (tests confirmed failing pre-fix, passing post-fix); a `NameError` regression introduced mid-round (accidentally swallowed `def _resolve_includes`) was caught by the verification gate and repaired — full suite 45/45. `prompts/README.md` documents the manifest-entry safety contract. Verified: py_compile exit 0, pytest 45/45 exit 0, fresh assembler diff exit 0 (byte-identical), `lint_system_prompt_sync` ✅ in sync.
+  - **Freebuff free-tier spawn status verified and corrected (docs hotfix, 2026-08-13)** — the "manual
+  verification item" status for the custom agents' live free-tier spawn is **closed**: binary analysis of the
+  Freebuff CLI `0.0.149` plus a live `@Cognitive Executor say hello` session proved the free tier CANNOT spawn
+  custom local `.agents/*.ts` agents. Root cause: the default free agent (`base3-free-deepseek-flash`) has no
+  `spawn_agents` tool in its whitelist, and the free-tier orchestrator (`base2-free-*`) only whitelists
+  built-in Codebuff subagents — the client-side spawn validation rejects anything else with `Agent "..." is
+not available to spawn` (the earlier `model`-omission fix was necessary but not sufficient). Docs updated:
+  `docs/freebuff-support.md` (header status, §3.3 verification evidence, §4 matrix, §5 rewrite, §6 step 4,
+  §7 step 6, §8 drift note), `README.md` Freebuff matrix + guide link, and `LLM.txt` Step 7.5 note. Corrected
+  guidance: on the free tier paste `<hands_*_task>` blocks into the base chat (all MCP tools + skills +
+  `~/.AGENTS.md` loaded) or switch to a `base2-free-*` "Free Orchestrator" agent to spawn Freebuff's built-in
+  subagents; custom agents require a credits/paid tier. `system-prompt.md` version unchanged (metadata/docs-only).
+  Verified: `lint_markdown` on all edited docs ✅, prettier ✅.
 
 ## [8.4.5] - 2026-08-13
```
<!-- END_GIT_DIFF -->
