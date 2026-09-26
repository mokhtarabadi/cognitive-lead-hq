# Task 266: Release v9.41.0 with milestone-20 archive

**File:** `tasks/completed/266-release-v9-41-0-with-milestone-20-archive.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Cut release v9.41.0. Archive the 33 completed tasks (229-265) into `docs/history/milestone-20-summary.md` and move them to `tasks/archive/` FIRST, then move the CHANGELOG `[Unreleased]` entries under a `## [9.41.0]` header leaving `[Unreleased]` empty, run every release verification gate (task lint, markdown lint, prompt-fragment sync, py_compile, docs-sync, full pytest suite), generate the executable push script at `/tmp/cognitive-lead-push-release.sh`, stage via the MCP tool, and hand the Manager the review hand-off.

## Manager's Notes

- Release version **9.41.0** matches the current `<system_version>` (system-prompt.md and prompts/fragments/01_system_version.md both read 9.41.0), so no fragment edit or prompt rebuild is needed — the prompt was already rebuilt during the 9.36.0-9.41.0 work. This follows the Task 229 precedent.
- Memory `release/release-workflow` governs this task: archive-on-release is a standing rule (archive BEFORE the release), `[Unreleased]` MUST be empty after the release, and an executable push script at `/tmp/cognitive-lead-push-release.sh` MUST be created with strict mode, tag creation, push, and GitHub Release steps.
- ZAC: the Hands never run `git add`, `git commit`, `git push`, `git tag`, or `gh release create`. Only `git mv` for Kanban moves. Staging is MCP-only; the commit goes through `custom_context_commit_and_clean_task` after the Manager's exact closure words.
- The public tag and GitHub Release publication are a manual Manager step.

## Local TODOs

- [x] Create the release task file and move it to `tasks/in-progress/`
- [x] Archive step FIRST: write `docs/history/milestone-20-summary.md` covering tasks 229-265, then `git mv tasks/completed/*.md tasks/archive/`
- [x] CHANGELOG Parse-Then-Append: move every `[Unreleased]` entry under `## [9.41.0] - 2026-09-20`, leaving `[Unreleased]` empty
- [x] Run all release verification gates (task lint, markdown lint, prompt sync, py_compile, docs-sync, full pytest)
- [x] Write the executable push script at `/tmp/cognitive-lead-push-release.sh`
- [x] Stage via `custom_context_stage_and_inject_diff` and move the task to `tasks/qa/`
- [x] Stale-memory audit report (read-only; no deletes without Manager approval)

## Acceptance Criteria

- [x] Archive step done FIRST: `docs/history/milestone-20-summary.md` exists with the milestone structure, `tasks/completed/` is empty, and all 33 files are in `tasks/archive/`
- [x] CHANGELOG `[Unreleased]` section is empty; every former entry sits under `## [9.41.0] - 2026-09-20` with no duplicate version or category headers
- [x] Full test suite passes exit 0; `scripts/check_docs_sync.py` passes; prompt-fragment sync verified byte-identical; `python3 -m py_compile` passes for the prompt-build scripts and the lint server
- [x] `lint_task_file` passes on the active release task file
- [x] `/tmp/cognitive-lead-push-release.sh` exists, is `chmod +x`, starts with `set -euo pipefail`, detects the repo root, defines `VERSION="v9.41.0"`, verifies a clean tree and `gh auth status`, creates the annotated tag only if missing, pushes commits and tags, then creates or verifies the GitHub Release
- [x] Diff staged via the MCP tool and injected into this task file; no commit by the Hands
- [x] Manager receives the exact tag/push/release commands for manual execution

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** full suite green exit 0; `scripts/check_docs_sync.py` OK; `lint_system_prompt_sync` in sync at 9.41.0; py_compile clean; `lint_task_file` clean
- **Actual result:** `rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q` → `686 passed, 10 warnings in 5.56s`. Other gates: `lint_markdown CHANGELOG.md` PASS; `lint_markdown docs/history/milestone-20-summary.md` PASS; prompt sync verified byte-identical via `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/opencode/system-prompt-check-266.md` + `diff -q system-prompt.md` → PROMPT_SYNC_OK; `python3 -m py_compile scripts/prompt-build/assemble_system_prompt.py scripts/prompt-build/split_system_prompt.py scripts/check_docs_sync.py mcp-lint-server/server.py` → PY_COMPILE_OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`; `bash -n /tmp/cognitive-lead-push-release.sh` → BASH_SYNTAX_OK. Archive: `git mv tasks/completed/*.md tasks/archive/` → 33 renames, `tasks/completed/` empty, `tasks/archive/` grew 225 → 258.
- **Exit code:** 0 (pytest), 0 (check_docs_sync.py)

> Verification runner rule: the command above is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** archiving loses task history, or the release is cut with a non-empty `[Unreleased]` section and a wrong version header; a stray commit by the Hands would break ZAC.
- **Rollback plan:** archival uses `git mv` so history stays reachable via `git log --follow -- tasks/archive/<file>`; the CHANGELOG edit is a pure section move, revertible from git; no `git add`/`commit`/`push`/`tag` is ever run by the Hands; the tag is created only if missing and never force-moved.

---

## Execution Log & Reasoning

### Skills and memory loaded (release-workflow SOP)

Loaded `archive-tasks`, `versioning-and-release`, `project-memory`, `verification-before-completion`, `task-lint`. Read memory `release/release-workflow` (the governing SOP) plus `workflows/no_task_for_global_upgrade` and `workflows/global-install-upgrade`.

### Assumptions

- **A1 — "milestone skill" = `archive-tasks`.** No skill named `milestone` exists in the 36-skill global set; `archive-tasks` is described as the milestone-compaction skill, so it is the one the Manager named.
- **A2 — Release version = 9.41.0.** `system-prompt.md` line 1 and `prompts/fragments/01_system_version.md` line 1 both read `9.41.0`, and no prompt change ships in this release. Following the Task 229 precedent, the release version matches the already-built `<system_version>`, so no fragment edit and no prompt rebuild are needed; the CHANGELOG simply catches up from its last header (9.35.0) to 9.41.0. This is a MINOR-class release body (new skills/workflow capabilities accumulated across 9.36.0-9.41.0) recorded under the 9.41.0 header.
- **A3 — prompt sync verified by the repo assembler, not the MCP tool.** `lint_system_prompt_sync` resolved the assembler against the GLOBAL lint-server install dir (`/home/mohammad/.config/opencode/scripts/prompt-build/assemble_system_prompt.py`) and errored with `Errno 2` because the global install ships only the server code, not `scripts/`. Equivalent verification was therefore run in-repo: assemble to a temp path and `diff -q` against `system-prompt.md` → byte-identical. The gate intent (no prompt/fragment drift) is satisfied.

### Changes

1. **Task file** `tasks/in-progress/266-release-v9-41-0-with-milestone-20-archive.md` created from the canonical template (Source: manager, Type: feature) and moved out of `tasks/backlog/`.
2. **Archive step done FIRST** (standing Manager rule 2026-09-12): `docs/history/milestone-20-summary.md` written covering all 33 completed tasks (229-252, 257-265); `git mv tasks/completed/*.md tasks/archive/` moved all 33 files (staged as renames `R`), leaving `tasks/completed/` empty and `tasks/archive/` at 258 files. History stays reachable via `git log --follow -- tasks/archive/<file>`.
3. **CHANGELOG Parse-Then-Append**: inserted `## [9.41.0] - 2026-09-20` between `## [Unreleased]` and the existing `### Added` block. No version or category header was duplicated; the existing `### Added` and `### Fixed` blocks now sit under 9.41.0 and `[Unreleased]` is empty. `## [9.35.0] - 2026-09-14` and older headers are untouched.
4. **Push script** `/tmp/cognitive-lead-push-release.sh` written and `chmod +x` (mode 755), syntax-checked with `bash -n`. It starts with `set -euo pipefail`, resolves the repo root, sets `VERSION="v9.41.0"`, refuses a dirty tree, requires `gh auth status`, pushes the branch, creates the annotated tag only if missing, pushes tags, then creates or verifies the GitHub Release and prints the remote tag and release URL.
5. **Stale Memory Report (read-only — nothing deleted, Manager approval required):**

   | Namespace / Key | Reason flagged | Evidence |
   | --------------- | -------------- | -------- |
   | `opencode_config/plugin_policy_dcp_only_2026_09_08` | Claims the goal plugin was removed from all four configs (dcp-only). Live config contradicts it. | `tui.json` (repo and global) carries `plugin: ["@prevalentware/opencode-goal-plugin", "@tarquinen/opencode-dcp@latest"]`, and the goal plugin is active in this session. |
   | `workflows/global-install-upgrade` (embedded 2026-09-09 claim) | One embedded claim says the persona and manager_decisions MCP servers were DISABLED in repo and global `opencode.json`. | The global config currently enables 7 servers including `manager_decisions` and `brain`; `opencode mcp list` reports 7/7 connected. The rest of this workflow memory is current and was used as-is. |
   | `opencode_config/global_goal_plugin_upgrade_2026_08_27` | Overlaps `plugin_policy_dcp_only_2026_09_08` on the same topic (goal plugin presence) with conflicting conclusions. | Both cover the goal plugin; the 2026-08-27 entry matches live config, the 2026-09-08 entry does not. Flagged as a duplicate-topic pair, not individually stale. |

   No memory was deleted or edited. All three require explicit Manager approval before any `delete_memory` call.

### Verification

- Full suite (RTK-prefixed, first run): **686 passed, 10 warnings in 5.56s**, exit 0.
- `lint_markdown` CHANGELOG.md → PASS; `lint_markdown` docs/history/milestone-20-summary.md → PASS.
- Prompt sync → byte-identical (see A3). `python3 -m py_compile` on the two prompt-build scripts, `check_docs_sync.py` and `mcp-lint-server/server.py` → clean. `scripts/check_docs_sync.py` → `docs-sync: OK`, exit 0 (two warn-only orphans: `scripts/fetch-opencode-docs.py`, `scripts/repomd`).
- `lint_task_file` on the active task file → PASS (the initial run flagged only the stale `tasks/backlog/...` `**File:**` header, corrected to the in-progress path).
- Milestone summary completeness: 33 `### Task` sections, all IDs 229-252 and 257-265 present in both the `## Criteria Met` table and `## Individual Task Summaries`; sources all `manager`; types 12 bug / 13 improvement / 8 feature.

### ZAC

No `git add`, `git commit`, `git push`, `git tag`, or `gh release create` was run. `git mv` was used only for the Kanban archive move. Staging goes through `custom_context_stage_and_inject_diff` only, and the tag/release publication is left to the Manager via the generated script. Closure still requires the Manager's exact words "Approved for closure" or "Close task".

### Closure

- **Manager approval (verbatim):** "Approved for closure"
- **Release state at closure (verified read-only):** remote annotated tag `v9.41.0` → commit `d40c2c0`; GitHub Release public and not a draft (`https://github.com/mokhtarabadi/cognitive-lead-hq/releases/tag/v9.41.0`); `main` level with `origin/main`; working tree clean.
- **Kanban move:** `tasks/qa/266-release-v9-41-0-with-milestone-20-archive.md` → `tasks/completed/266-release-v9-41-0-with-milestone-20-archive.md` via `git mv`; `**File:**` header updated and `**Status:**` set to `closed`.
- **Commit:** closure committed through `custom_context_commit_and_clean_task`. The release body itself was committed and pushed by the Manager as `d40c2c0`; the Hands ran no `git add`/`commit`/`push`/`tag`.
- **Still open:** the three stale-memory flags recorded above await the Manager's decision. Nothing was deleted.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `99077554e8c1d9aec99391d28f2dc3d76b21468e`
<!-- END_GIT_DIFF -->
