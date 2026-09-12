# Task 195: Machine-readable QA verdicts plus rules-first checks

**File:** `tasks/completed/195-machine-verdicts-rules-first.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Make autopilot fully hands-free: QA verdicts return a strict machine-readable `QA_PASSED` / `QA_REJECTED` with file-and-line cites the autopilot parses without copy-paste, and cheap deterministic rule checks (schema, budget, allowlist) run before the LLM judge.

## Manager's Notes

From the Brain self-improvement review (Task 190, live `brain_turn`), ranked R5 (strict verdicts with cites) and R7 (rules before judge). Fixed rules catch clear faults in milliseconds and spare judge tokens; strict verdicts let the hotfix step start automatically.

## Local TODOs

- [x] Define the strict verdict format (`QA_PASSED` / `QA_REJECTED` + `file:line` cites) in the QA persona behavior (fragment 06)
- [x] Add a rules-first gate: schema, budget, and allowlist checks run before any LLM judge call
- [x] Mocked unit tests for the rules gate
- [x] Rebuild system prompt from fragments if 06 changes; verify sync byte-identical

## Acceptance Criteria

- [x] A QA reply parses to a verdict + cites with a single regex
- [x] Schema/budget/allowlist violations are caught without any LLM call
- [x] Prompt sync verified byte-identical after any fragment edit

## Verification Evidence

- **Test command:** `uv run --with pytest --with "mcp==1.30.0" --with pathspec --with pyyaml python -m pytest -q` (repo root)
- **Expected result:** all tests pass, exit 0
- **Actual result:** **252 passed** (gate suite 27/27 incl. 7 round-2 residual tests; full suite, 8 pre-existing warnings), prompt round-trip `SYNC_OK` zero diff (recorded prior round, fragments untouched since)
- **Exit code:** `0`

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Over-strict verdict regex rejects valid human-worded verdicts — keep a documented escape hatch.
- **Rollback plan:** Revert the persona-behavior diff; verdicts return to prose.

---

## Execution Log & Reasoning

- Red-green: wrote `tests/test_rules_gate.py` first (13 tests), confirmed collection ERROR (`No module named 'rules_gate'`), then implemented `scripts/qa-rules-gate/rules_gate.py` → 13/13 green.
- Gate design: `parse_verdict` uses one compiled regex each for `VERDICT:` and `CITE:` lines; `run_gate` runs parse → schema → budget → allowlist and returns QA_REJECTED without touching `judge` on any violation (Mock asserted `assert_not_called`); clean payload calls judge exactly once, or returns the parsed verdict when no judge is given. Unparseable replies become QA_REJECTED with reason "unparseable verdict" (documented escape hatch: autopilot falls back to prose, manager may override).
- Fragment 06 QA persona gained the Machine-Readable Verdict Mandate + rules-first pointer + escape hatch; version bumped 9.27.0 → 9.28.0 per AGENTS.md (system-prompt.md is generated, so the version source is `01-system_version.md`).
- Rebuilt `system-prompt.md` via the assembler (81285 bytes), round-trip check `SYNC_OK` zero diff.
- Full suite `uv run --with pytest --with "mcp<2" --with pathspec --with pyyaml python -m pytest tests/` → **232 passed** (env note: system python has no pytest; `mcp` v2 removed FastMCP so suites need `mcp<2`; memory-server tests need pyyaml — all pre-existing env gaps, unrelated to this change).
- **State-machine QA round (fresh brain turn, this session): VERDICT QA_REJECTED.** First attempt hit transport 500, retry succeeded. Brain cites V1–V6: (V1) allowlist `Path(root) in Path(path).parents` fails on relative payload paths (tests only cover absolute `/repo/...`, production payloads are relative like the task's own cited paths) → false QA_REJECTED; (V2) multiple VERDICT lines silently pass on first match instead of failing closed; (V3) no leading-space tolerance (CRLF is fine — `\s*$` covers `\r`); (V4) `judge()` return used unvalidated (None/empty/malformed); (V5) schema check top-level only; (V6) loose cite pattern (disk check: trailing punctuation actually fails closed by dropping the cite rather than accepting it — minor). Hands disk-triage: V1–V5 hold, V3 partially, V6 overstated. Hotfix XML received, scoped to `scripts/qa-rules-gate/rules_gate.py` + `tests/test_rules_gate.py` (relative-path normalize, exactly-one-verdict, whitespace tolerance, judge validation, deeper schema, +7 tests). Per state-machine rule: rejection recorded, NO reviewer round, NO autoclosure — task stays in QA awaiting hotfix decision. Rejection count: 1 (no 3rd-rejection escalation).

- **Autopilot hotfix applied (this session, per QA V1–V6):** `scripts/qa-rules-gate/rules_gate.py` — (V1) `check_allowlist` normalizes both sides with `abspath` so relative payload paths judge correctly; (V2) `parse_verdict` requires exactly ONE VERDICT line (zero or multiple → `UnparseableVerdict`, fail-closed); (V3) VERDICT/CITE regexes tolerate leading spaces/tabs; (V4) `run_gate` validates the judge return against `QA_PASSED`/`QA_REJECTED` (garbage → QA_REJECTED + `judge_called=True`); (V5) `check_schema` supports dotted nested paths; (V6) CITE regex tolerates one trailing punctuation run, stripped from the path. `tests/test_rules_gate.py` +7 tests (relative inside/escape, two-verdicts raise, leading-space parse, judge-garbage rejected, nested-schema missing, cite trailing period). Gate file 20/20, full suite **239 passed** (232 + 7), exit 0. Pending: fresh QA + reviewer via `brain_turn`.

- **Rejection-2 QA round + round-2 fix (this session):** Brain re-run returned QA_REJECTED (rejection 2 of 3) with residual findings F1–F6 + hotfix XML — but the verdict was summary-based (no diff pasted; my summary said `startswith`, real code never used it). Hands disk-triage against ACTUAL code: F1 sibling-prefix FALSE (code used `Path.parents`, boundary-safe); F3 judge-enum FALSE (exact tuple membership, stricter than prescribed normalization — applying it would LOOSEN the gate, so Step 2 deliberately NOT applied); F4 split-regex FALSE (single `findall` for count+parse, zero/two raise tests pre-exist). F2 symlink TRUE (abspath leaves symlink escapes) → FIXED: `check_allowlist` now `realpath` + `commonpath` containment with fail-closed ValueError guard; unused `pathlib.Path` import removed. +7 residual tests (sibling-prefix, symlink escape, symlink-inside passes, indented second marker, judge-None, 3-level nested + non-dict mid, version + full punct tails); unused `import os` removed from test file. Gate **27/27**, full suite **252 passed**, exit 0. Code-grounded Brain re-review (actual code pasted): **QA_PASSED** — D1 FIXED, D2/D3 REFUTED in Hands' favor, no hotfix needed. **Reviewer round (this session): PO_REVIEW_PENDING — technically approved, NOT autoclosed.** Code Reviewer confirms AC/DoD honestly marked, no scope creep, CHANGELOG Parse-Then-Append kept, no task numbers in prompt prose. But status is explicitly PO_REVIEW_PENDING with two PO checks (A1 confirm diff block in file, A2 business need for strict verdict format) and asks the Manager to reply "Approved for closure". Per goal rule (close ONLY on explicit APPROVED) this is a deferral, not an approval — task STAYS in QA awaiting Manager's approval word.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `6d6691227e69b8976e0bf40091e8ab04e1b25795`
<!-- END_GIT_DIFF -->
