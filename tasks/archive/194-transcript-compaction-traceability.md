# Task 194: Transcript lifecycle — compaction plus traceability logging

**File:** `tasks/completed/194-transcript-compaction-traceability.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Bound transcript growth (compact after 30 messages into a 4k summary, keep the last 10 intact) and log model name, prompt hash, and truncation actions in each JSONL record for minute-level debugging.

## Manager's Notes

From the Brain self-improvement review (Task 190, live `brain_turn`), ranked R4 (compaction) and R8 (traceability). Transcripts today grow append-only; later turns slow down and old context loses focus. Each record should carry enough metadata to trace any run without replaying it.

## Local TODOs

- [x] Compaction: after 30 messages, summarize into ≤4k chars, keep last 10 intact
- [x] Per-record metadata: model name, prompt hash, truncation counts
- [x] Mocked unit tests (compaction trigger, metadata presence, last-10 preservation)
- [x] Verify full bridge suite still green

## Acceptance Criteria

- [x] A 50-message transcript compacts to summary + last 10 on next load
- [x] Every JSONL record carries model, prompt hash, and truncation info
- [x] No live calls in tests; full suite green

## Verification Evidence

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q`
- **Expected result:** all pass, including compaction tests
- **Actual result:** 165 passed (160 + 5 hotfix tests), 0 failed. Live QA_REJECTED round 1 on 194 honored in full: V1 prior-summary merge, V2 atomic temp+rename write, V3 full-lock re-read, V4 byte-size trigger; payload purity verified on disk (chat already strips to role/content). Round-2 DIRECT QA re-run: QA_PASSED (REPORT, no XML — correct on pass; accepted on substance despite format drift: no [QA Engineer] bracket, no reasoning_log — drift noted honestly, strict format demanded on reviewer turn; cited specifics: merge 35+35=70, atomic temp+rename, full-lock re-read, byte-trigger, 5 tests, 165 green; R1–R3 kept as reviewer notes). CORRECTION: round-2 QA ran WITHOUT task_id (no history loaded — specifics came from the pasted prompt, not history continuity). Reviewer re-run WITH task_id 194-qa: APPROVED ([Code Reviewer] + reasoning_log, REPORT no XML; verbatim on disk in 194-qa/transcript.jsonl, now 4 turns: 'F1: Merge preserves prior counts across cycles.', 'F2: Atomic write uses temp file plus fsync plus rename.', 'No diff text was pasted in this call'). A1–A3 pre-closure checks confirmed on disk (bridge 182-line + tests 172-line diffs; CHANGELOG 194 entry at line 11; all 4 helper docstrings). Rejections stay at 1 — no escalation.
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Compaction summarizes via the model (extra call, extra cost) or via rules (lossy) — decide explicitly during implementation.
- **Rollback plan:** Disable the compaction trigger; transcripts grow append-only again.

---

## Execution Log & Reasoning

Implemented in `mcp-brain-bridge/server.py` under standing autopilot+autoclosure (manager asleep, zero questions). Risk decision: NO model call for compaction — deterministic extractive digest record (turn count, per-role counts, ts range, models seen, truncated total, ≤4k chars) + last 10 records kept; offline-testable, zero cost. `append_turn` gained optional metadata params (model/prompt_hash/truncated, defaults None/None/0); `brain_turn` passes model + sha256(effective_prompt) + truncated_count. Chat payload strips metadata to role/content (provider-safe). Compact-on-load inside `load_history` (idempotent, LOCK_EX rewrite); compaction supersedes the 40-cap in normal flow (40-cap stays as backstop). Tests T1–T5 (50→summary+10, bounded+idempotent, metadata keys, defaults-compat, brain_turn metadata via mocked HTTP). Green round: fixed 3 exact-equality assertions + fake-home prompt pattern; rewrote caps test to summary+last-10. Full suite: **160 passed**, exit 0.

Hotfix (live QA_REJECTED round 1 on 194, all findings TRUE gaps, honored in full): `_parse_turns` helper extracted (shared parse rules for `load_history` and locked compaction); `_build_compacted` pure merge (prior summaries detected via `compacted` flag, counts accumulate into `compacted_count`, models union, truncated sums, prior digest tails chained, 4k clamp, last 10 kept); `_atomic_write_turns` (temp+pid, fsync, os.replace); `_compact_locked` (LOCK_EX across re-read+build+replace — concurrent appends queue, never lost); `load_history` uses `_parse_turns` + triggers on count>30 OR file>200KB (`_COMPACT_FILE_BYTES`); `compacted_count` added to `_META_KEYS`; old `_compact_transcript_file` removed (no callers). Step-4 verified already true on disk (chat strips to role/content; `append_turn` defaults). Tests: monster-lines test rewritten for byte-trigger behavior; 5 new mocked tests (merge 35+35=70 — my own arithmetic in the test fixed during authoring; corrupt-skip; payload-purity; old-compat; large-turn byte trigger). Full suite: **165 passed**, exit 0. Round-2 QA_PASSED (accepted on substance, format drift noted honestly; strict format demanded on reviewer turn — drift fixed: reviewer came back with [Code Reviewer] + reasoning_log). History-continuity CORRECTION: the round-2 QA call ran without task_id (no history loaded/appended — verdict real but prompt-grounded); the reviewer re-run carried task_id 194-qa and its APPROVED verdict persists verbatim on disk (4-turn transcript). A1–A3 confirmed (code diffs, CHANGELOG entry, docstrings). Reviewer APPROVED → proceeding to autoclose under standing autopilot+autoclosure.

Round-3 QA re-request (model back, task_id 194-qa, full verbatim pack): QA_PASSED ([QA Engineer] + reasoning_log, REPORT no XML — correct on pass). Grounds: code excerpts across turns, suite green, HOLD closed via forensics, reviewer APPROVED already on disk (turn 4/4). CORRECTION (honest): QA claimed highest count 183 — fresh suite proves 181 passed EXIT:0; 183 hallucinated (off by 2, non-blocking). No re-review needed (Hands to NO ONE). Autoclosing under standing authorization.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `af40e7e0e73db54dcda8f19c00915253ee59bf14`
<!-- END_GIT_DIFF -->
