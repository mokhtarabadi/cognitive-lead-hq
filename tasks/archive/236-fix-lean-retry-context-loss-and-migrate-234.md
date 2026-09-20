# Task 236: Fix lean-retry context loss and migrate global 234 session folder

**File:** `tasks/completed/236-fix-lean-retry-context-loss-and-migrate-234.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Close the two session-context gaps proven in the 235 transcript audit: lean retries must carry state, and the 234 folder must move home.

## Manager's Notes

Manager order: "Can you fix gaps?" — "New task". Plan approved in concept (3 steps); implementation approval still needed before code changes. Gap G1: lean retry (`include_bundle=false`) drops the bundle, Brain judged a stale file version live in session 235 (turn 3, 179 chars, no bundle). Gap G2: task 234 transcript + fed_context live only in the global dir (`~/.config/opencode/brain-sessions/234`, 11 lines + fed file) because old server code was live during 234; 230-233 migrated, 235 writes per-project.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Add state note to lean-retry path in bridge server (task path + status + diff hash)
- [x] Add regression test: lean retry carries state note, no stale judgment possible
- [x] Migrate global 234 folder into tasks/.sessions/234, extend manifest, verify hashes
- [x] Full suite green + lint + stage per protocol

## Acceptance Criteria

- [x] A lean retry prompt always carries task path, status, and diff hash even with bundle off
- [x] New regression test proves the state note is present on the lean path
- [x] tasks/.sessions/234 exists with transcript + fed_context byte-identical to global copies
- [x] Manifest lists 234 with matching sha256 hashes

## Verification Evidence

- **Test command:** uv run --with pytest==8.3.4 --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec --with pyyaml pytest tests/ -q
- **Expected result:** all pass, exit code 0
- **Actual result:** bridge file 140 passed; full suite 357 passed in 3.41s
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** retry prompt grows; state note must stay tiny (3 lines max) or lean loses meaning
- **Rollback plan:** revert bridge edit; 234 global copies stay untouched as fallback

---

## Execution Log & Reasoning

Autopilot locked for Task 236 per Manager order "Start auto pilot".

G1: `_task_state_note()` (pure-adjacent, never raises) resolves the task file, reads `**Status:**`, hashes the Factual Git Diff block (sha8, "no-diff" when empty); `_empty_output_hint(task_id, state)` appends "Current state: path | status | diff=hash" while staying pure (caller does I/O); guard call site wires them; executor Step 5 notes the state note for cross-retry comparison. Honest AC check: AC1 demanded path+status+diff-hash on the lean path — first edit only added a freshness sentence, so the full state note was implemented before checking the box. G2: global 234 transcript (11 lines) + fed_context (6 lines) copied to tasks/.sessions/234/, sha256 match globals; manifest extended (task_ids 230-234). Tests: hint-contract extended (stale sentence, state line, unknown fallbacks); bridge file 140 passed; full suite 357 passed exit 0.

QA (same id, diff attached): QA_PASSED — state helper never raises, one-line status parse, pure hint, no shared state; notes F6-F8 are coverage observations only (no positive real-file test, no bridge-output integration test, G2 proof in log not diff). Review (same id, diff attached): technically approved, PO_REVIEW_PENDING. Strengths F1-F4 (never-raises helper, pure hint, backward-compat default arg, stale/state/unknown coverage). One fix applied: R1 changelog count corrected (1 assertion → 4 new assertions). R2/R3 noted (sessions ignored by design, proof in log; happy-path test only if bridge area reopens). Closure awaits the Manager approval word.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `1c50ba08db37ab77a5dc13a27f32c37f37a5b245`
<!-- END_GIT_DIFF -->
