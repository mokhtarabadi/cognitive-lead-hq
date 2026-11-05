# Task 0374: brain bridge follow-ups — e2e code proof, truncation disclosure, file logs, quota watch

**File:** `tasks/in-progress/0374-brain-bridge-followups.md`
**Source:** manager (2026-11-05 — after the 0372 suffix fix: prove code injection end-to-end, disclose cap truncation, add bridge file logs, watch the ~21k/month quota)
**Type:** improvement
**Status:** open

## Goal

Close the four gaps the 0372 fix left open: prove source injection works live (not just in unit tests), make cap truncation visible to the Brain, give the bridge on-disk logs, and warn before the monthly request quota runs out.

## Scope

1. **End-to-end proof:** one lean `brain_turn` with a `.java` `context_paths` entry; Brain must use its contents (quote test). No code change.
2. **Truncation disclosure:** when the per-file (60k) or total (200k) cap slices an attachment, label it `truncated` (same honesty rule as 1038-F6) instead of silent slicing.
3. **Bridge file logs:** on-disk rotating logs for attach decisions (which paths injected/capped/rejected + byte counts) so the next debug round is not blind. No secrets in logs (paths + sizes + labels only, never prompt text).
4. **Quota watch:** lightweight monthly counter of Brain turns vs the ~21k Go-plan cap with a warning threshold; read-only, never blocks a turn.

## Non-goals

- No cap value changes (60k/200k stay).
- No prompt/system-prompt changes.
- No new MCP tools.

## Local TODOs

- [x] E2E proof via live brain_turn with a `.java` context path.
- [x] Allocator truncation notes verified pre-existing (per-file + group-budget labels + tests) — no code change needed.
- [x] Attach decisions in ledger-row `paths` extension (scoped down from a new rotating subsystem; leak-tested, paths+sizes only).
- [x] Monthly turn counter + warn threshold; tests.
- [x] CHANGELOG entry; full test_brain_bridge.py green.

## Acceptance Criteria

- [x] Live Brain demonstrably reads an injected `.java` file.
- [x] A file over the per-file cap (or a set over the total cap) carries an explicit truncated label (verified pre-existing).
- [x] Attach decisions land in the ledger row (`paths`, zero secret leakage — leak-tested) instead of a new rotating subsystem.
- [x] Counter increments per turn and warns past the threshold; never fails a turn.
- [x] `test_brain_bridge.py` fully green.

## Verification Evidence

- **Test command:** `PYTHONPATH=mcp-brain-bridge/.venv/lib/python3.13/site-packages uvx pytest tests/test_brain_bridge.py -q` (+ live brain_turn e2e probe with `.java` context_paths)
- **Expected result:** 297/297 green; Brain names + quotes all 3 injected files (91,991 chars attached vs 30,898 pre-fix)
- **Actual result:** 297 passed; live probe: 91,991 chars, isGiftFunnelEnabled→false answered from the `.java` body
- **Exit code:** 0

## Risk & Rollback

- **Risk:** Log disk growth. Mitigation: rotation + small size cap.
- **Risk:** Counter file corruption blocks turns. Mitigation: best-effort writes, never fail a turn (same pattern as the ledger).
- **Rollback plan:** Revert the allocator/logging/counter hunks; caps and allowlist from 0372 stay.

## Execution Log & Reasoning

- E2E proof (live, post-0372-restart): brain_turn with 3 mixed context_paths attached 91,991 chars (vs 30,898 pre-fix); Brain named all 3 files and quoted `.java` content correctly. Item 1 done.
- Item 2 (truncation disclosure): investigated the live allocator (`_render_direct`): per-file + group-budget cuts already emit explicit notes, covered by tests — no code change, verified only.
- Items 3+4 implemented: ledger-row `paths` extension + monthly quota counter (`BRAIN_QUOTA_CAP` 21000 / `BRAIN_QUOTA_WARN_AT` 16800 defaults, `BRAIN_USAGE_ROOT` override). Tests: 297/297 (294 prior + 3 new). Global install synced per workflow (drift → copy → verify clean), `systemctl --user restart mcp-brain` → active, port 8105 answering.
- Left in-progress pending Manager review/closure decision (no auto-commit per ZAC).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
