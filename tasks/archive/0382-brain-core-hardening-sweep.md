# Task 0382: Brain core + tooling hardening sweep (minimal-change bug hunt)

**File:** `tasks/completed/0382-brain-core-hardening-sweep.md`
**Source:** manager (2026-11-06 — fa: با رفت‌وبرگشت‌های انجام‌شده، اگر نقص دیگری در ابزار Brain و core آن هست که hallucination را تشدید کند یا گپ/بهبودی وجود دارد، با مشورت seatهای داخل Brain انجامش بده؛ minimal change، بدون تغییرات بزرگ؛ فقط باگ واقعی پیدا و همین‌جا حل شود تا session بسته شود)
**Type:** bug-hunt + hardening
**Status:** closed
**Finished:** 2026-11-06T12:57:11Z
**Submitted:** 2026-11-06T12:49:45Z

## Goal

Find remaining REAL bugs/gaps in the Brain tooling and core that could amplify hallucination (or otherwise break the Brain↔Hands loop), fix them with minimal diffs, and close the session. No refactoring, no features, no large changes.

## Manager's Notes (translated)

- With the recent back-and-forths, consult the Brain seats: if there are other defects in the Brain tool or its core that could worsen hallucination, or any other improvement/gap, do it with the seats' consultation.
- Minimal change only — no big changes wanted; find real bugs and fix them here so we can close the session.
- Luna 6 is strong and follows the system prompt precisely but is slow. Finish the last hardening work with it, then switch to a faster model (e.g. Muse 1.3 X-High, which is fast but misses bugs).

## Method (binding)

1. Multi-seat Brain consultation (analysis only): Architect + Senior Programmer + QA Engineer survey the Brain core/tooling for hallucination-amplifying defects. Ranked candidates, each with a concrete failure scenario.
2. Triage each candidate against the repo: reproduce with evidence or refute with evidence. Only reproduced REAL bugs are fixed.
3. Fixes are minimal diffs with regression pins; full suite must stay green.
4. Anything unverified, speculative, or large is recorded as a parked follow-up — NOT implemented.

## Scope guard

- Allowed: `mcp-brain-bridge/`, `prompts/fragments/`, `agents/cognitive-executor.md`, `tests/`, `CHANGELOG.md`, generated `system-prompt.md`.
- Forbidden: new features, refactors, server rewrites, model-routing changes, unrelated docs.

## Local TODOs

- [x] Multi-seat consultation turn (Architect + Programmer + QA) under this task_id
- [x] Triage candidates with repo evidence (reproduce or refute)
- [x] Fix only verified real bugs (minimal diffs + regression tests)
- [x] Full suite green + `lint_task_file`; stage, QA + review via Brain
- [x] Relay verdict; close only on explicit approval; then close the session
- [2026-11-06] Exact closure answer value `Approved for closure` received through the immediately preceding question-tool result; QA_PASSED + PO_REVIEW_PENDING verified before close.

## Acceptance Criteria

- [x] Every implemented fix traces to a reproduced failure with cited evidence.
- [x] No speculative/unverified change merged; parked items listed with reasons.
- [x] Full HQ suite green; `lint_task_file` passes.
- [x] Diff is minimal (no refactors, no scope widening).

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q` → red `1 failed, 33 passed` then green `34 passed`; full `rtk test ... python -m pytest tests/ -q` → `802 passed, 24 warnings`; `python3 -m py_compile tests/test_prompt_sync.py` OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`
- **Expected result:** red-first on the ferry-phrase pin; green after the 2-phrase fix + 9.74.0 rebuild; assembler diff = 3 hunks only
- **Actual result:** green across all gates; `grep -c "where to paste it" system-prompt.md` → 0; version pins updated 9.73.0 → 9.74.0
- **Exit code:** 0
- Stack-gate skip: root=. markers=[go.mod, buf.yaml, build.gradle.kts, Package.swift, *.xcodeproj, pyproject.toml+Flask, pyproject.toml+FastAPI, package.json+next.config.*, package.json+src/ports/, package.json+apps/expo, vite.config.*, nuxt.config.*, nest-cli.json, prisma/schema.prisma] matched=[] reason=no matching stack marker found; python-fastapi loaded for Python discipline only

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** hardening sweeps invite scope creep. Bound: reproduce-or-park rule; max 3 fix rounds (same retry guard as QA loops), then escalate.
- **Rollback:** each fix is a small hunk; revert per-hunk via git.

---

## Execution Log & Reasoning

- Model lane: Luna 6 for the whole sweep (precision over speed, Manager order). Switch to Muse 1.3 X-High only after this task closes.
- [2026-11-06] Seat consult done (Architect + Programmer + QA, analysis-only): 3 discovery lanes returned 20+ candidates. Triage verdicts (reproduce-or-park):
  - CONFIRMED — prompt 06-personas:50/:56 "where to paste it" contradicts the pinned no-ferry invariant (Manager never ferries; Hands chains `brain_turn` directly). Minimal fix below. (F1/F2 prompt lane)
  - REFUTED with evidence — session_ledger F10 (verdict type is `Union[str,bool]`; str branch raises on bad input; no fail-open), F11 (writes go only to `ledger_dir / LEDGER_FILENAME`; session_id is a JSON string field, no traversal write), loop_guard F6 (corrupt lines skipped on read but tool only writes valid JSON; skipping cannot fake a stop), F7 (legacy fallback is documented migration with stderr notice), F8 oscillation (bounded by the 3-rejections-per-stage rule), capability F4/F5 (prefix families match real namespaced tools; phantom names fail loudly at call time; exact-allowlist would be a large change), preflight F1/F2/F3 (explicit bad root raises loudly, never substitutes silently; ambient/one-off semantics documented), prompt F3 (hotfix XMLs are post-plan-approval implementation, not new plans — no observed stall), F4 (no observed discovery ping-pong since 0378), F5 (MODE line tells the Brain the live mode), F6 (QA/Reviewer scope split is by design; no cycling evidence), F7 (rejecting a wrong-gate answer with re-ask is correct behavior), F8 (verdict block lives in the English machine channel, not the localized handoff), Q1 escape hatch (bounded: unparseable verdict → QA_REJECTED + prose fallback + Manager override; no re-emit loop), Q2 (Architect instructs, Hands loads — no collision), attach F1/F2/F4/F5/F8/F9/F10/F11/F12 (label-precision nits; TOCTOU affects only which label, not behavior; all parked).
  - PARKED (no evidence of a live failure) — capability exact-allowlist, loop_guard oscillation cap, ANSI-label distinction, discovery Brain-side wording. Reasons recorded; no action.
- Brainstorm: not required — <reason>diagnostic consult with minimal reversible fixes; full 7-seat ceremony reserved for hard-to-reverse design</reason>.
- Seat Check: contract wording (`contract` trigger) → Software Architect; silent-fail review → Senior Programmer; adversarial triage → QA Engineer. Designer/Strategist/Planner skipped (no UX/capacity/planning surface).
- [2026-11-06] Fix applied: "where to paste it" → "where the Hands applies it" in QA (:50) + Reviewer (:56) summary specs; ferry pin extended; version pins 9.73.0 → 9.74.0; rebuilt (3-hunk diff), CHANGELOG entry, all gates green. Lite justification: 2-phrase wording, no security/financial surface, reversible via git, gates decide.
- [2026-11-06] QA verdict: `QA_PASSED` (no vulns, no missing tests). Re-review verdict: `PO_REVIEW_PENDING` (technical verdict: `APPROVED`). F1 wording replaced in both personas + shipped; F2 pin + 9.74.0; F3 minimal diff, no unrelated changes. File remains in `tasks/qa/`; closure awaits Manager's explicit `Approved for closure` / `Close task`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `d63f46749a12e5bccf4dd0f3dc921ed0dc6225a5`
<!-- END_GIT_DIFF -->
