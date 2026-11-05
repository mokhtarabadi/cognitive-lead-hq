# Task 0372: brain_turn context_paths rejects source files — extend suffix allowlist

**File:** `tasks/completed/0372-brain-context-paths-source-suffixes.md`
**Source:** manager (2026-11-05 — brain_turn implementation planning starved: `context_paths` with `.java`/`.js`/`.tsx` all returned `[unavailable: unsupported extension]`, only `AGENTS.md` attached (~29.5k of ~87k requested); Brain looped on missing_context and finally refused)
**Type:** bug
**Status:** closed

## Goal

Let `brain_turn(context_paths=[...])` inject source-code files (not just docs/reports) so implementation planning and review turns can see the code they judge — while keeping traversal, size, and budget guards intact.

## Scope

1. Extend `_ALLOWED_READ_SUFFIXES` in `mcp-brain-bridge/server.py` with source-text suffixes (Java/Kotlin, JS/TS/JSX/TSX, Python, Go, Swift, C/C++, C#, Ruby, PHP, XML/Gradle/CSS/HTML, SQL, shell, etc.); binaries stay rejected.
2. Update `test_paths_attach_bad_suffix_labelled` to pin a still-rejected binary suffix; add positive coverage that `.java`/`.tsx`/`.py` inject.
3. Run the brain-bridge test file green; no other MCP behavior changes.

## Non-goals

- No change to caps (`_CTX_PATHS_PER_FILE` 60k, total 200k), traversal guard, max-bytes guard, or empty-file handling.
- No change to the tool description contract (still "read suffix allowlist").
- No new MCP tool or schema change.

## Local TODOs

- [x] Extend the suffix set with a comment citing this task.
- [x] Update/extend tests (binary still rejected; source files inject).
- [x] Run `test_brain_bridge.py` green.
- [x] CHANGELOG entry (HQ repo).

## Acceptance Criteria

- [x] `build_paths_attach(["a.java"])` injects text; `["a.exe"]` (or similar binary) still labels unsupported.
- [x] Full `test_brain_bridge.py` passes.
- [x] The exact 2026-11-05 failure (AGENTS.md-only attach for a mixed code+docs request) now attaches the code files within caps.

## Verification Evidence

- **Test command:** `PYTHONPATH=mcp-brain-bridge/.venv/lib/python3.13/site-packages uvx pytest tests/test_brain_bridge.py -q` (+ functional `build_paths_attach` check via bridge venv python)
- **Expected result:** all green; `.java`/`.tsx`/`.py` inject, `.exe` rejected, traversal blocked
- **Actual result:** 294 passed; functional check True/True/True/True
- **Exit code:** 0
- Ruff: 116 pre-existing errors before and after (stdin check on HEAD vs worktree); zero on changed lines — no new lint introduced.

## Risk & Rollback

- **Risk:** Over-broad suffix lets a binary blob into the prompt. Mitigation: text-only programming/markup suffixes; 2 MB hard cap + per-file/total caps unchanged; `errors="replace"` decode already in place.
- **Rollback plan:** Revert the one-line suffix set + test change.

## Execution Log & Reasoning

- Byte-exact proof: request `["AGENTS.md" (29,500 B), "AnalyticsRepository.java" (38,614 B), "analytics.test.js" (18,686 B)]` attached 30,898 chars = AGENTS.md + label overhead only. Diagnosis: `_ALLOWED_READ_SUFFIXES` (server.py:471, since 2026-09-12) predates the task-210 `context_paths` feature (2026-09-13) and was never extended beyond docs/reports — silent by-design veto, not a transient failure.
- Fix applied 2026-11-05: suffix set extended (docs + source-text languages, binaries still out), `test_paths_attach_bad_suffix_labelled` now pins `.exe` rejection, new `test_paths_attach_source_suffixes_inject` covers `.java`/`.tsx`/`.py`. Functional check via bridge venv (inject/injest/reject/block traversal all True); `test_brain_bridge.py` 294 passed; ruff delta zero on changed lines. Task stays in-progress pending review/closure decision — no commit (ZAC).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
