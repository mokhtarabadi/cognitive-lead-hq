# Task 191: Deterministic decision extraction — temp-0, schema, fallback, cache

**File:** `tasks/completed/191-deterministic-decision-extraction.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Make decision extraction return identical candidates for identical transcripts: force temperature 0 on extraction calls, enforce a JSON schema, add a regex fallback parser, and cache results by input hash.

## Manager's Notes

From the Brain self-improvement review (Task 190, live `brain_turn`): identical runs currently return 1, 0, 1 candidates by model luck. Ranked R1 (temperature 0 + schema + regex fallback) and R6 (cache by input hash). Retry-on-empty stays as the caller-side companion, not the fix.

Round-2 delta (N1): validate the Brain output as strict JSON with evidence links, and auto-repair exactly once on validation fail (fix the JSON, re-validate, proceed) so the autopilot continues instead of stalling on free-text drift.

## Local TODOs

- [x] Pin extraction temperature to 0 (or `BRAIN_TEMPERATURE=0` default for the decision path)
- [x] Enforce candidate JSON schema on the model response
- [x] Add regex fallback when the model returns near-miss text
- [x] Cache extraction results keyed by transcript hash; reuse on exact repeats
- [x] Strict-JSON validation with evidence links + exactly one auto-repair on fail (N1)
- [x] Verify with repeated-runs test (same input 5x → identical output, zero extra tokens on cache hit)

## Acceptance Criteria

- [x] Same transcript 5 times in a row returns byte-identical candidates
- [x] Malformed model text still yields candidates via the regex fallback or a loud error, never silent drift
- [x] Cache hits cost zero tokens and are logged as hits
- [x] Invalid output triggers exactly one auto-repair; still-invalid output raises loudly

## Verification Evidence

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/test_decision_server.py -q`
- **Expected result:** all pass, including a new repeat-determinism test
- **Actual result:** 155 passed, 0 failed (145 + 7 Step-5 hotfix tests + 3 R1–R5 residual tests), reviewer verdict APPROVED
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Temperature 0 narrows creative variance the brainstorm path may rely on — scope the pin to the extraction call only, never the brainstorm call.
- **Rollback plan:** Revert the decision-server diff; previous nondeterministic behavior returns.

---

## Execution Log & Reasoning

Implemented via fresh subagent (decision server + tests only, no git/network/live): LRU cache keyed by sha256(transcript + model), cap 64, stderr hit logs, zero HTTP on hit; strict candidate schema validator; largest-JSON-span repair; exact-substring regex fallback; temperature pinned to 0 on the extraction call only (explicit `BRAIN_TEMPERATURE` wins, reasoning effort always dropped — brainstorm path untouched per Risk). 6 new mocked tests, full suite 145 passed, exit 0. Markers independently verified on disk. Executed under the standing autopilot+autoclosure authorization.

Review (DIRECT reviewer `brain_turn`, REPORT, no XML — APPROVED): 7 strengths with file:line cites (temp-aware cache key prevents cross-temperature poisoning; strip-don't-explode evidence handling; fenced prose fallback with NFC normalization; temp-0 enforcement with default-override-off; failure-mode tests reproducing reported issues; honest 40-vs-64 cap terminology fix; R1 false-alarm admission). 4/4 QA residuals resolved (R1 false alarm proven with `_HISTORY_LIMIT` vs `_EXTRACT_CACHE_MAX`; R2 NUL-join docstring; R3 whitespace behavioral + test; R4 loud-temp fix in BOTH servers symmetric + test; R5 `_LINE_CAP_CHARS` + skip-count + test). 3 claimed invariants (temp-aware locked LRU hit logging, at-most-once repair counting, fluctuation-tolerant largest-JSON) + full-suite-155 evidence. 5 non-blocking notes recorded as future work: N1 log only transcript hash prefix; N2 flock Unix-only (Windows needs portalocker/msvcrt); N3 document >64-char ID truncation; N4 document multi-temperature call cost; N5 constant-time cache compare (low priority). Autoclosed under the standing autopilot+autoclosure authorization.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `235f8c14948b9138e41f5f500ee2922b1ca8a420`
<!-- END_GIT_DIFF -->
