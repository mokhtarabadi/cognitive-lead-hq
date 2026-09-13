# Task 210: File-path context injection for brain turns

**File:** `tasks/completed/210-file-path-context-injection-for-brain-turns.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Let the Brain receive context by file path instead of pasted lines: new `brain_turn` input carries markdown paths, the server reads and injects them capped and labeled.

## Manager's Notes

Manager proposal (translated from Persian): when the Brain wants context or code, it should name file paths (signature reports, context reports, trees, custom markdown). The Hands build those files with the context MCP server. The Brain server reads them from disk and injects them into the turn. Small pulls stay inline, big artifacts go by path. Goal: least hallucination with most precise context. Manager ordered a brainstorm with file-fed context before deciding.

## Local TODOs

- [x] Brainstorm with file-fed context
- [x] Decide design from brainstorm result
- [x] Implement on approval
- [x] Verify functionality

## Acceptance Criteria

- [x] Brainstorm verdict on the proposal recorded
- [x] Final design approved before code
- [x] Small pulls stay inline, big artifacts go by path
- [x] Server caps and labels each injected file

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with pyyaml --with mcp==1.30.0 python -m pytest tests/ -q`
- **Expected result:** all tests pass, exit 0
- **Actual result:** 255 passed (245 baseline plus 10 new path-injection tests), 8 warnings
- **Exit code:** 0
- **Live proof:** `brain_turn` signature carries `context_paths`; `build_paths_attach(['docs/conventions.md'])` returns labeled injection from disk

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** path traversal and budget overflow if caps are wrong.
- **Rollback plan:** keep inline slices working; new parameter optional, default off.

---

## Execution Log & Reasoning

Task filed per manager order. Brainstorm with file-fed context runs under this task id next.

Brainstorm done (2 rounds, file-fed). Verdict: proposal GOOD and DOABLE. Selected path O1: optional context_paths field on brain_turn, server-side read with root check plus suffix allowlist, per-file cap plus total budget, labeled injection. Small pulls stay inline. Key evidence: bridge read_file refuses .py (suffix allowlist), context tools return paths only (ferry-shaped), fed-context pin helpers reusable. Brain asks for approval before blueprint and code. No code written.

Manager approved. Implementation O1: new optional context_paths param (default off), build_paths_attach helper (resolve under root, allowlist, per-file 20k cap, total 40k budget, explicit unavailable labels), wired after task attach so it counts toward input budget. One self-caught docstring slip repaired (dropped task_id line, restored verbatim). 10 new offline tests. Full suite 255 passed. Live proof via signature plus real-file injection.

QA round 1: QA_PASSED. Honored 2 cheap follow-ups (too-large branch test, absolute-path escape test). Symlink escape accepted: shared resolver uses realpath. Wiring test stays a follow-up: helpers plus signature proof cover it.

Reviewer: technically APPROVED, no blocking issues. Follow-up kept: max file count cap for a future release. Moved to qa. Closure needs explicit approval word.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `a6e0d8f8d163c948b80212d87cadea6d0e5d6e57`
<!-- END_GIT_DIFF -->
