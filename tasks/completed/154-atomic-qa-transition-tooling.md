# Task 154: Atomic QA Transition & Staging Tooling

**File:** `tasks/completed/154-atomic-qa-transition-tooling.md`
**Source:** manager — Retrospective Finding F4 (Sprint 2026-09-02)
**Type:** improvement
**Status:** closed

## Goal

Streamline the Kanban QA transition protocol in `prompts/fragments/09-hands_protocols.md` by introducing an atomic helper or tool that unifies file movement (`git mv tasks/in-progress/ tasks/qa/`), metadata header synchronization (`**File:**`), and diff injection (`custom_context_stage_and_inject_diff`) into a single deterministic operation, eliminating agent friction and two-pass staging errors.

## Manager's Notes

Origin: Retrospective Finding F4 (Sprint 2026-09-02) — agents repeatedly hit friction during QA transition due to the manual two-pass sequence (stage → `git mv` → header patch → re-stage). The fragmented flow causes stale `**File:**` headers and desynced diffs when the second staging is skipped. This task proposes a single atomic operation to unify movement, header sync, and diff injection.

Reference file: `prompts/fragments/09-hands_protocols.md` (summary phase / QA transition protocol). The fix must update that fragment and reassemble `system-prompt.md` via the prompt-build assembler.

## Local TODOs

- [x] Initial codebase exploration — read `prompts/fragments/09-hands_protocols.md`, `system-prompt.md`, `mcp-context-server/server.py` (stage_and_inject), and `docs/architecture.md` for Kanban lifecycle context
- [x] Design atomic QA transition mechanism — evaluate helper script (`scripts/qa-transition.sh` or `scripts/qa-transition.py`) vs MCP tool extension (`custom_context_stage_and_inject_diff` with move+sync or new `custom_context_qa_transition` tool)
- [x] Implement the chosen atomic mechanism with strict mode and path-drift guard
- [x] Update `prompts/fragments/09-hands_protocols.md` summary phase instructions to use the atomic transition flow (single command, no two-pass workaround)
- [x] Reassemble `system-prompt.md` from prompts/fragments and bump `<system_version>`
- [x] Verification test confirming single-pass QA migration with synced headers and diffs
- [x] Run `lint_task_file` and `lint_system_prompt_sync` to confirm no drift

## Micro-Task Checklist (Native MCP — Round 2)

- [x] **Step 1:** Add `qa_transition` Tool to `mcp-context-server/server.py`
- [x] **Step 2:** Update `prompts/fragments/09-hands_protocols.md` — specify `custom_context_qa_transition` MCP tool as primary with CLI alternative
- [x] **Step 3:** Reassemble `system-prompt.md` — confirm `custom_context_qa_transition` present and sync pass
- [x] **Step 4:** Update Documentation & CHANGELOG — `## [9.6.0]` `### Added` entry for MCP tool + CLI helper
- [x] **Step 5:** Verification & Re-staging — py_compile, dry-run test, re-stage QA file with updated diff

## Acceptance Criteria

- [x] Design/implement atomic QA transition mechanism (helper script or MCP tool integration)
- [x] Update `prompts/fragments/09-hands_protocols.md` summary phase instructions to use the atomic transition flow
- [x] Reassemble `system-prompt.md` and bump `<system_version>`
- [x] Verification test confirming single-pass QA migration with synced headers and diffs

## Verification Evidence

- **Test command:** `python3 -m py_compile scripts/qa-transition.py && uv run scripts/qa-transition.py --help` + `lint_task_file tasks/in-progress/154-atomic-qa-transition-tooling.md` + `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check_sys.md && diff -u /tmp/check_sys.md system-prompt.md` + sandbox `uv run scripts/qa-transition.py --task tasks/in-progress/test-fixture-qa.md --files scripts/qa-transition.py`
- **Expected result:** py_compile passes; help prints usage; lint passes; prompt sync reports `PROMPT SYNC PASS` with `<system_version>9.6.0</system_version>` and `qa-transition` command at two locations; sandbox moves fixture to `tasks/qa/` with synced `**File:**` header and injected diff containing `scripts/qa-transition.py` new file.
- **Actual result:** `py_compile PASS`; `usage: qa-transition.py ...`; `✅ tasks/in-progress/154-atomic-qa-transition-tooling.md passed Task File linting.`; `Assembled 75599 bytes -> /tmp/check_sys.md` + `PROMPT SYNC PASS`; `head -n1 system-prompt.md` → `<system_version>9.6.0</system_version>`; `grep qa-transition system-prompt.md` → 2 hits at lines 307, 358; sandbox `✅ QA transition complete: tasks/in-progress/test-fixture-qa.md → tasks/qa/test-fixture-qa.md` with header `**File:** \`tasks/qa/test-fixture-qa.md\`` and diff block containing `new file mode 100755` for `scripts/qa-transition.py`. Cleanup `rm -f tasks/qa/test-fixture-qa.md` done.
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>`.)_

## Risk & Rollback

- **Risk:** Atomic helper hides the underlying `git mv` + header sync semantics and could mask path-drift failures if the header patch is not validated; MCP tool change could break existing `custom_context_stage_and_inject_diff` callers.
- **Rollback plan:** Revert `prompts/fragments/09-hands_protocols.md` to the two-pass protocol and keep the helper as an optional wrapper (no breaking removal); `git checkout -- prompts/fragments/09-hands_protocols.md system-prompt.md` restores prior behavior.

---

## Execution Log & Reasoning

**Step 1 — Author `scripts/qa-transition.py` (268 lines, executable):**
Created `scripts/qa-transition.py` with `#!/usr/bin/env python3` + `/// script` front-matter. Implements `_git_mv_or_fallback` (git mv with `shutil.move` + `git add` fallback for untracked files, mirroring `scripts/bundle-tasks.py`), `_rewrite_file_header` (regex `**File:**` patch), `_inject_diff` (explicit `git add -- <files> <dest>` + `git diff --staged -- . ':!tasks/'` + greedy `BEGIN`/`END` replacement with sentinel `No code changes detected or staged.`), `_confirm_header` (resolved-path comparison as linter does). Arg parsing supports `--task` + `--files` and legacy positional fallback. Security: `Path.resolve().relative_to(workspace_root)` traversal guard, validates source inside `tasks/in-progress/`, checks `.md` extension and existence, `mkdir(parents=True)` for destination. Verified `chmod +x`, `python3 -m py_compile` → PASS, `--help` prints usage.

**Step 2 — Update `prompts/fragments/09-hands_protocols.md`:**
Replaced fragmented 2-pass QA transition (stage → `git mv` → header patch → re-stage) in both `<hands_implementation_task_template>` and `<hands_combined_task_template>` `<summary_phase>` with single atomic directive:
`uv run scripts/qa-transition.py --task tasks/in-progress/<task-name>.md --files <modified_file_1> <modified_file_2> ...` + description "atomically moves the task file to `tasks/qa/`, updates the `**File:**` header, stages your modified code, and injects the git diff in one operation." Renumbered subsequent steps (6→4, 7→5; 5→4 in combined). Preserved lint step (1,2) and final output step.

**Step 3 — Bump System Version & Reassemble:**
Edited `prompts/fragments/01-system_version.md` 9.5.0 → 9.6.0. Ran `python3 scripts/prompt-build/assemble_system_prompt.py` → `Assembled 75599 bytes -> system-prompt.md`. Verified `head -n1 system-prompt.md` → `<system_version>9.6.0</system_version>` and `grep qa-transition` → 2 hits (lines 307, 358). Ran prettier on fragments (unchanged, 66ms/3ms) and `assemble --output /tmp/check_sys.md && diff -u /tmp/check_sys.md system-prompt.md && echo PROMPT SYNC PASS` → PASS.

**Step 4 — Update `CHANGELOG.md`:**
Parse-Then-Append inserted `## [9.6.0] - 2026-09-02` `### Added` between `## [Unreleased]` and `## [9.5.0]` with entry:
`- **Atomic QA Transition Tooling:** Added \`scripts/qa-transition.py\` and updated Hands protocols in \`09-hands_protocols.md\` to unify Kanban file movement, header synchronization, and diff injection into a single deterministic operation (Task 154).`

**Step 5 — Verification Sandbox Test:**
Created `tasks/in-progress/test-fixture-qa.md` (minimal valid task with `**File:**` + `BEGIN`/`END` markers). Ran `uv run scripts/qa-transition.py --task tasks/in-progress/test-fixture-qa.md --files scripts/qa-transition.py` → `✅ QA transition complete: tasks/in-progress/test-fixture-qa.md → tasks/qa/test-fixture-qa.md` with staged files. Asserted `tasks/qa/test-fixture-qa.md` exists, header `**File:** \`tasks/qa/test-fixture-qa.md\``, diff block contains `new file mode 100755` and `scripts/qa-transition.py` content (verified via `grep -A5 BEGIN_GIT_DIFF`). Cleaned up via `git reset HEAD -- tasks/qa/test-fixture-qa.md; rm -f tasks/qa/test-fixture-qa.md`, restored stray `.opencode/skills/audit-agents/SKILL.md` via `git checkout`.

**Step 6 — Transition Task 154 via New Tool (pending summary phase):**
Will execute `uv run scripts/qa-transition.py --task tasks/in-progress/154-atomic-qa-transition-tooling.md --files scripts/qa-transition.py prompts/fragments/09-hands_protocols.md prompts/fragments/01-system_version.md system-prompt.md CHANGELOG.md` to atomically move task to `tasks/qa/`, sync header, stage code, inject diff. This replaces the manual two-pass sequence and validates the new deterministic path.

**Design decision:** Chose standalone `scripts/qa-transition.py` over MCP extension because it follows established `scripts/*.py` convention (like `bundle-tasks.py`), is `uv run`-able deterministically without MCP redeploy, has minimal blast radius, and can be wrapped later as an MCP tool if desired. Hybrid script-first design satisfies Task 154 AC "helper script or MCP tool integration" with lowest risk.

**Native MCP Integration (Round 2 — 2026-09-02):**
Added `qa_transition` as a native MCP tool in `mcp-context-server/server.py` (decorated with `@mcp.tool()`, 147 lines). Implemented with the same deterministic flow as `scripts/qa-transition.py`: `Path.resolve().relative_to(workspace_root)` traversal guard, `tasks/in-progress/` validation, `git mv` with `shutil.move` + `git add` fallback, regex `**File:**` header rewrite, explicit `git add -- <modified_files> <dest>` staging, `git diff --staged -- . ':!tasks/'` extraction, greedy `BEGIN`/`END` diff injection with sentinel, re-stage of QA file, and final header consistency check. Added `import shutil`. Updated `prompts/fragments/09-hands_protocols.md` both templates' step 3 to specify `custom_context_qa_transition` as primary with CLI alternative `(Alternatively, run \`uv run scripts/qa-transition.py ...\` via terminal)`. Reassembled `system-prompt.md` (75975 bytes) and verified `custom_context_qa_transition` present at 2 locations. Updated `CHANGELOG.md` `## [9.6.0]` entry to reflect both MCP tool and CLI helper. Verified `python3 -m py_compile mcp-context-server/server.py scripts/qa-transition.py` → PASS, prettier unchanged, prompt sync PASS. Tested `qa_transition` via `uv run python` dry-run dummy (`tasks/in-progress/test-qa-mcp-dummy2.md` → `tasks/qa/test-qa-mcp-dummy2.md`, header synced, diff injected, cleaned via `git reset` + unlink). Re-staged QA file via manual `git add` + diff injection (557 lines) to include MCP diff in `Factual Git Diff`.

**Edge-case handling (E1–E10):** Path traversal outside workspace → error; non-`tasks/in-progress/` source → error; missing file → error; non-`.md` extension → error; untracked file → fallback move; missing `**File:**` header → error; missing `BEGIN`/`END` markers → error; empty staged diff → sentinel; header mismatch after injection → error; re-stage failure → error.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `51d6c0ca595d7f84d0731de08e1d9d3bcbf3b149`
<!-- END_GIT_DIFF -->
