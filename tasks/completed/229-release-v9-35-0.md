# Task 229: Release v9.35.0 with milestone-19 archive

**File:** `tasks/completed/229-release-v9-35-0.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Cut release v9.35.0: archive tasks/completed/ into milestone-19 first, move CHANGELOG Unreleased under the release header, verify gates, stage, and hand the Manager tag/push/release commands plus the push script.

## Manager's Notes

- Memory `release/release-workflow` governs: archive-on-release standing rule (archive-tasks skill BEFORE release), [Unreleased] MUST be empty after release, Hands never run git add/commit/push/tag or gh release create, stage only via the MCP tool, public tag/release is a manual Manager step, and an executable push script MUST be created at `/tmp/cognitive-lead-push-release.sh`.
- Release version 9.35.0 matches the current `<system_version>` (no fragment edit needed; prompt already rebuilt).
- Completed pile: 209, 210, 219, 227, 228 → `docs/history/milestone-19-summary.md`, then `git mv` to `tasks/archive/`.

## Local TODOs

- [ ] Archive completed tasks (milestone-19 summary + git mv to archive)
- [ ] Move CHANGELOG [Unreleased] under ## [9.35.0] - 2026-09-14
- [ ] Run full test suite + docs-sync + prompt-sync check
- [ ] Stage via MCP stage_and_inject_diff (no commit — ZAC)
- [ ] Write /tmp/cognitive-lead-push-release.sh (executable, documented below)
- [ ] Stale-memory audit report (read-only, no deletes without approval)

## Acceptance Criteria

- [ ] Archive step done FIRST: milestone-19 summary exists, completed/ empty, files in archive/
- [ ] CHANGELOG [Unreleased] section empty; all entries under [9.35.0]
- [ ] Full suite passes exit 0; docs-sync OK; system-prompt byte-identical to assembled fragments
- [ ] Diff staged via MCP tool and injected into this task file (no commit by Hands)
- [ ] Push script exists at /tmp/cognitive-lead-push-release.sh, chmod +x, strict mode, tag+push+release flow
- [ ] Manager receives exact commit/tag/push/release commands

## Verification Evidence

- **Test command:** `uvx --with pytest --with pathspec --with mcp==1.30.0 --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-bash --with pyyaml python -m pytest tests/ -q` + `python3 scripts/check_docs_sync.py` + prompt-sync assemble diff
- **Expected result:** suite green exit 0; docs-sync OK; prompt in sync at 9.35.0
- **Actual result:** _(fill during execution)_
- **Exit code:** _(fill during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** release commit/tag by the wrong party breaks ZAC; archive loses task history
- **Rollback plan:** archive uses `git mv` (history preserved via --follow); release tag created only if missing; no force operations anywhere

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## QA Verdict Note

Brain QA (bare 229): QA_PASSED — release mechanics only (summary accuracy F1, archive moves F2, milestone number F3, CHANGELOG move F4, version F5); 331 passed exit 0, docs-sync OK, prompt-sync via suite lint test; lint gap + diff placeholder noted as non-blockers. Code Reviewer (bare 229, pasted evidence): technically APPROVED → PO_REVIEW_PENDING, Low severity, no hotfix XML (F1-F5 strengths; I1 lint unchecked + I2 placeholder diff deferred to closure as R1/R2; R3 archive/CHANGELOG confirm before commit).
Stage (2026-09-14): drove sanctioned MCP path over stdio JSON-RPC (uv run mcp-context-server): stage_and_inject_diff staged 9 release paths + injected diff — returned ok. Commit NOT run (Manager-owned closure word pending).
Push script (2026-09-14): wrote executable /tmp/cognitive-lead-push-release.sh per memory spec (strict mode, VERSION var default 9.35.0, clean-tree gate, annotated tag if missing, push commits+tag, gh release create if missing, ls-remote verification). bash -n syntax OK. LEFT UNRUN (tag/push/release-create are Manager-owned).
Stale-memory report (2026-09-14): grepped .opencode/memory for completed/209|210|219|227|228, 213-mirror/authoritative, milestone-18, 9.3x — 4 hits, all benign (old quirk note, old plugin history, standing archive rule, upgrade credential note). NO deletions proposed; nothing awaits approval.

Closure (2026-09-14, 'Approved for closure'): moved qa→completed, header synced, status closed. Commit via sanctioned MCP path.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `933488e759e7deab4f5c9e10357193151493ed17`
<!-- END_GIT_DIFF -->
