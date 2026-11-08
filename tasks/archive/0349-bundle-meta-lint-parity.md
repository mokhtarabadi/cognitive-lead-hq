# Task 0349: Bundle META output must satisfy the canonical task lint

**File:** `tasks/completed/0349-bundle-meta-lint-parity.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Make `bundle_tasks` emit a META file that passes `lint_task_file` on first write: a non-empty `## Supersedes` section, and every source section that carries provenance (original message, translation, refactored prompt, code context, analysis) preserved inside the META instead of being dropped.

## Manager's Notes

Reported after bundling `282` and `334` in the Apex project. The bundle itself was correct, but the produced META failed the real linter and silently lost the source's Telegram provenance sections. Manager asked for the graph to locate the defect first, then a task, then the fix in this repository.

## Graph findings (2026-10-25)

Graph built over `mcp-context-server` (96 nodes / 143 links). `_build_meta_content` at `bundle.py:23` is the single writer of the META body; `query_graph` also surfaced ADR-010 "Bundle Hardening (ID Retry, Rollback, Validation)" and `mcp-lint-server/server.py` as the validator.

Three defects, all between the writer and the validator:

- **D1 — missing section, not just metadata.** `bundle.py:142` writes `**Supersedes:** [ids]` as a metadata line only. `_check_bundle_meta_structure` (`mcp-lint-server/server.py:529`) requires a `## Supersedes` heading with a non-empty body. Every freshly bundled META therefore fails lint until edited by hand.
- **D2 — provenance sections dropped.** `_build_meta_content` extracts only Goal, Acceptance Criteria, Local TODOs, Risk & Rollback, Manager's Notes and Blueprint Reference (`bundle.py:41-53`). Sections such as `## Original Message (Persian)`, `## English Translation`, `## Refactored Prompt`, `## Relevant Code Context`, `## AI Analysis & Opinion` and `## Source Context` are not copied, so a telegram-sourced bundle loses them from the working file (they survive only in the archive).
- **D3 — the dry-run gate disagrees with the linter.** `server.py:1404-1419` claims "All required sections present" against a list that omits `## Supersedes` and `## Bundled Checklist`, so the preview passes while the real lint fails.

## Acceptance Criteria

- [x] `_build_meta_content` emits a non-empty `## Supersedes` section naming every source task id and title.
- [x] Any `## ` section present in a source task that the bundler does not already handle is copied verbatim into that source's block, in original order, with its heading preserved.
- [x] Structural sections are never duplicated into the source block: Goal, Acceptance Criteria, Local TODOs, Risk & Rollback, Manager's Notes, Blueprint Reference, Execution Log & Reasoning, Factual Git Diff.
- [x] The dry-run required-section list includes `## Supersedes` and `## Bundled Checklist`, so the preview can never pass a file the linter rejects.
- [x] A generated META passes `lint_task_file` with no manual edit (regression test).
- [x] Existing bundle tests stay green.

## Verification Evidence

- **Test command:** `rtk test uv run pytest tests/test_bundle_tasks.py -q`
- **Expected result:** all bundle tests pass, including the new META-lint-parity and provenance-preservation tests
- **Actual result:** `22 passed in 1.28s`. The parity test imports the live `mcp-lint-server` `_check_bundle_meta_structure` and asserts a generated META returns zero issues; against the pre-fix builder it fails on the missing `## Supersedes` section. `tests/test_mcp_servers.py` also run: `87 passed in 4.84s`.
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Copying every unrecognised section can duplicate a source's `## Factual Git Diff` or `## Execution Log` into the META, inflating the file and confusing the Hands. Mitigated by an explicit structural deny-list.
- **Rollback plan:** Revert the two file changes; bundling returns to its current behaviour, where the operator patches the META by hand.

## Local TODOs

- [x] Initial codebase exploration
- [x] Add the `## Supersedes` section writer and the extra-section extractor
- [x] Align the dry-run required-section list with the linter
- [x] Add regression tests (lint parity + provenance preservation)
- [x] Verify functionality

---

## Execution Log & Reasoning

**Autopilot lock:** the Manager said "auto lock … and fix it there"; the mode is locked for this task and no approval pauses were taken except hard blockers. None occurred.

**Graph-first discovery.** Graph over `mcp-context-server` (96 nodes / 143 links) plus two `query_graph` calls. The first query seeded on `_build_meta_content` and `_find_task_file`, which placed `bundle.py`, `gitops.py`, `server.py` and the `DECISIONS.md` ADRs in one neighbourhood — enough to see the writer/validator split before reading a line. The second query surfaced ADR-010 (Bundle Hardening), which is why the fix extends that ADR series rather than inventing a new subsystem.

**What changed and why.**

1. `bundle.py` — added `_STRUCTURAL_SECTIONS` and `_extract_preserved_sections`. The deny-list is explicit rather than "everything except what I copy", because `Definition of Done` and `Execution Log & Reasoning` are boilerplate that already exist at META level and duplicating them per source would double the file for zero information. `Verification Evidence` is deliberately NOT in the deny-list: bundled tasks carry different test commands, and dropping them loses the only place that records how each half is proven.
2. `bundle.py` — `_build_meta_content` now renders a real `## Supersedes` section (id + title per source, plus the all-or-nothing sentence). The `**Supersedes:**` metadata line stays: it is machine-readable for tooling, the section is what the linter and a human read.
3. `server.py` — dry-run `required` list gains `## Supersedes` and `## Bundled Checklist`, so the preview can no longer certify a file the linter rejects. This is the defect that made the original bug invisible: the preview printed "All required sections present" while `lint_task_file` failed on the same content.
4. Tests — four added. The parity test imports `mcp-lint-server/server.py` dynamically and runs its real `_check_bundle_meta_structure` over a generated META, so the two servers can never drift again without failing the suite.

**Trailing rule kept:** shell was read-only throughout; every file change went through the native edit tool. Task file was moved with filesystem `mv` because the new file was untracked (`git mv` refuses untracked paths).

**Verification.** `22 passed` for `tests/test_bundle_tasks.py`, `87 passed` for `tests/test_mcp_servers.py`, both exit 0. The parity test is the one that would have caught the original defect: it fails against the pre-fix builder and passes now.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `a9b71b1f90abba16456848bc34de60ea9c1563ba`
<!-- END_GIT_DIFF -->
