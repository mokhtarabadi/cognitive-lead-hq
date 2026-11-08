# Task 0381: Closure approval via question tool loops instead of closing

**File:** `tasks/completed/0381-closure-approval-question-tool-loop.md`
**Source:** manager (2026-11-06 — ad-hoc fa, translated above)
**Type:** bugfix
**Status:** closed
**Finished:** 2026-11-06T12:42:08Z
**Submitted:** 2026-11-06T12:20:57Z
**Estimate:** 4h
**Deadline:** 2026-11-06

## Goal

End the closure-approval loop: when the Manager picks `Approved for closure` / `Close task` in the `question`-tool approval card, the Brain must accept it on the first relay — not reject it as "embedded in a larger message" turn after turn.

## Manager's Notes

Persian verbatim: "ببین، همین الان یه باگ دیگه پیدا شد، همین Approve for Closure. من یک بار زدم، چرا هی لوپ انداخت Brain؟ باگش رو پیدا کن، یک تسک جدید براش بساز و با کمک خود Brain این باگ Approve for Closure رو هم حل کن. اما دفعه اول که من توی ابزار Question، Approve for Closure رو انتخاب کردم، باید انجام می‌داد، نه هی لوپ بندازه."

Translation: a new bug was found in Approve-for-Closure. The Manager selected it once in the Question tool, but the Brain looped. Find the bug, create a new task, fix it with the Brain's help. The first selection must take effect — no looping.

## Root cause (verified, not hypothesized)

- Case: task 0380 closure. The Hands relayed `PO_REVIEW_PENDING` via the `question` tool (one narrow question, options `Approved for closure` / `Not yet`). The Manager picked `Approved for closure`. The tool result arrived as: `User has answered your questions: "Code Reviewer verdict ... Reply 'Approved for closure' to commit and finish."="Approved for closure"`.
- That tool result IS the Manager's next message directly answering the relayed closure question — contract-satisfying per `prompts/fragments/24-language_policy.md:41` ("A bare `approved` counts only as the next message directly answering the relayed closure question").
- But the Hands paraphrased the answer into a larger prompt (mode line + context), and the Brain's exact-literal closure gate (`prompts/fragments/06-personas.md:56` Reviewer behavior: "Only the exact phrases ... count", "nor does any autopilot self-decision") demands the phrase as the entire standalone message — structurally impossible for the Hands, which must always include the mode line and task context. Result: 3 consecutive closure rejects ("not exactly the required approval phrase" / "embedded in a larger message"), closed only by sending the bare phrase with the bundle switched off (losing task context).
- Asymmetry: the plan gate explicitly recognizes "through the question tool path" (`13-constraints.md:3`, `24-language_policy.md:41`); the closure gate has no question-tool-path recognition. That missing half is the bug.

## Fix direction (for the Brain plan to confirm)

1. Teach the Brain the question-tool answer envelope: a `User has answered your questions: "<header>"="<exact phrase>"` tool result quoting `Approved for closure` or `Close task` IS the Manager's exact answer — accept on first relay, never demand a standalone retype.
2. Teach the Hands to forward approval answers verbatim (quoted envelope, not paraphrase) — `agents/cognitive-executor.md` relay rule.
3. Touch points (confirm in plan): `prompts/fragments/06-personas.md` (Reviewer closure rule), `prompts/fragments/13-constraints.md` (Approval Literals Guard), `prompts/fragments/24-language_policy.md:41`, `agents/cognitive-executor.md` (relay/closure section), system-prompt rebuild with version bump, `tests/test_prompt_sync.py` regression pin, `CHANGELOG.md` entry. No `server.py` behavior change expected (prompt-level fix, same class as the plan-gate precedent) — plan must say so explicitly or justify a code change.

## Local TODOs

- [ ] Brain planning turn under this task_id (Seat Check + brainstorm evaluation on record)
- [ ] Implement the approved plan (prompt sentences + executor rule + rebuild + tests)
- [x] Full HQ suite green + `lint_task_file` on the active task file
- [x] Stage + inject diff, move to QA, Brain QA + review turns
- [x] Relay verdict to Manager; closure only on explicit `Approved for closure` / `Close task`
- [x] Verify the exact question-tool approval and QA/review prerequisites.
- [x] Move the task to `tasks/completed/` and update closure metadata.
- [x] Run `lint_task_file` and verify staged paths.
- [2026-11-06] Manager closure approval received through the question tool: User has answered your questions: "Code Reviewer verdict for task 0381 (tasks/qa/0381-closure-approval-question-tool-loop.md): PO_REVIEW_PENDING (technical verdict: APPROVED). F1 preflight+relay aligned on envelope acceptance; F2 regression pins both sections; F3 version 9.73.0/artifact/changelog consistent; no server.py change. QA_PASSED; full suite 802 passed, exit 0; lint clean; diff staged. Reply 'Approved for closure' to commit and finish."="Approved for closure". The answer value matched the immediately preceding closure question.

## Acceptance Criteria

- [x] A question-tool answer envelope quoting the exact closure phrase is accepted as the Manager's approval on first relay (pinned by a shipped-prompt regression test).
- [x] The Hands relay rule forbids paraphrasing approval answers (verbatim quoted envelope).
- [x] No other approval-gate semantics change: blanket acknowledgements still never count; bare `approved` still counts only as the next message answering the relayed question.
- [x] `test_prompt_sync.py` assembler-identity test still passes (rebuild is byte-clean except intended hunks).
- [x] Full HQ suite green.
- [x] `lint_task_file` passes on the active task file.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q` → `31 passed`; full `rtk test ... python -m pytest tests/ -q` → `799 passed, 24 warnings`; `python3 -m py_compile tests/test_prompt_sync.py` OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`
- **Expected result:** red-first 4 failed (3 new tests + version pin) before the fix, all green after; assembler diff = 4 intended hunks only
- **Actual result:** red confirmed `4 failed, 27 passed`; after fix `31 passed` prompt-sync, `799 passed` full; assembler output differs from old shipped file in exactly the 4 intended hunks (version + 3 contract sentences)
- **Exit code:** 0
- Stack-gate skip: root=. markers=[go.mod, buf.yaml, build.gradle.kts, Package.swift, *.xcodeproj, pyproject.toml+Flask, pyproject.toml+FastAPI, package.json+next.config.*, package.json+src/ports/, package.json+apps/expo, vite.config.*, nuxt.config.*, nest-cli.json, prisma/schema.prisma] matched=[] reason=no matching stack marker found; python-fastapi loaded for Python discipline only
- **QA hotfix (2026-11-06):** negative-case pin only.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q` → `32 passed` (incl. `test_closure_approval_keeps_existing_negative_cases`); full `rtk test ... python -m pytest tests/ -q` → `800 passed, 24 warnings`; `python3 -m py_compile tests/test_prompt_sync.py` OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`
  - **Expected result:** all green; Deviation D1 logged (removed pre-0381 sentence not pinned)
  - **Actual result:** green across all four gates
  - **Exit code:** 0
- **Reviewer hotfix (2026-11-06):** preflight alignment + pin.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q` → red `1 failed, 32 passed` then green `33 passed` (incl. `test_executor_capability_preflight_matches_closure_answer_contract`); full `rtk test ... python -m pytest tests/ -q` → `801 passed, 24 warnings`; `python3 -m py_compile tests/test_prompt_sync.py` OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`
  - **Expected result:** all green; no fragment/system-prompt/CHANGELOG/server change
  - **Actual result:** green across all four gates; Deviation D2 logged (EXECUTOR const fix)
  - **Exit code:** 0
- **Reviewer hotfix 2 (2026-11-06):** relay acceptance alignment + pin.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q` → red `1 failed, 33 passed` then green `34 passed` (incl. `test_executor_review_relay_accepts_closure_answer_envelope`); full `rtk test ... python -m pytest tests/ -q` → `802 passed, 24 warnings`; `python3 -m py_compile tests/test_prompt_sync.py` OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`
  - **Expected result:** all green; no fragment/system-prompt/CHANGELOG/server change
  - **Actual result:** green across all four gates
  - **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** loosening the literal gate could let paraphrased approvals through. Bound: only the verbatim `question`-tool envelope with the exact English literal counts; paraphrases and blanket acknowledgements still never count.
- **Rollback:** revert fragment/executor sentences; rebuild prompt to prior version.

---

## Execution Log & Reasoning

- (autopilot off — manual mode; Manager ferries nothing, Hands chains `brain_turn` calls directly)
- [2026-11-06] Seat Check: contract wording → Software Architect; brainstorm not required (single-domain reversible). Plan approved via question tool ("Approved").
- [2026-11-06] Assumption A1: skipped the 4-subagent fan-out — all four lanes' files were already read verbatim natively in-session (fragment lines, executor relay, tests, CHANGELOG); `grep -c "has answered" server.py` → 0 proves the envelope never passes through bridge code, so no runtime change is needed.
- [2026-11-06] Test-first: new envelope + forwarding + version tests failed red as expected (`4 failed, 27 passed`), then green after the fix. One repair: the verbatim-forwarding pin reads `agents/cognitive-executor.md` (not system-prompt.md) since the executor is not assembled into the shipped prompt — matches existing `test_executor_*` conventions.
- [2026-11-06] No `server.py` change (plan-confirmed): the envelope is produced by the question tool; the defect was prompt interpretation + Hands paraphrasing. Sibling docs read (fragments/agents/tests READMEs + DECISIONS); no doc changes required — wording change is contract-scoped, rollback via git + rebuild.
- Brainstorm: not required — <reason>single-domain prompt-contract fix with ledger-verified root cause, no cross-disciplinary ambiguity</reason>.
- [2026-11-06 QA hotfix] QA_REJECTED (test-only gap): new regression pinned positive envelope wording but not the preserved negative cases. Added `test_closure_approval_keeps_existing_negative_cases` (Deviation D1: QA-prescribed 4th string was the pre-0381 bare-approved sentence the approved plan replaced; pinning it would require a prompt change the hotfix forbids — test pins the three negative cases as actually shipped). No prompt/prod change. Prompt-sync `32 passed`; full `800 passed, 24 warnings`; py_compile OK; docs-sync OK.
- [2026-11-06 reviewer hotfix 1] REJECTED_NEEDS_FIXES was correct: Capability Preflight still said closure accepts only exact phrases with bare-approved-never-counts, contradicting the new relay rule. Test-first pin failed red alone, then green after aligning the paragraph (Deviation D2: prescribed `_read("...")` str arg fixed to existing EXECUTOR Path const). No fragment/system-prompt/CHANGELOG/server change.
- [2026-11-06 reviewer hotfix 2] REJECTED_NEEDS_FIXES was correct: the operational Review-approval relay still said "Accept ONLY the exact phrases", so the Hands could reject the envelope before relaying. Test-first (`1 failed, 33 passed` red on the new relay pin), then aligned the relay clause with preflight (one long line kept intact for the pin). No fragment/system-prompt/CHANGELOG/server change. Prompt-sync `34 passed`; full `802 passed, 24 warnings`; py_compile OK; docs-sync OK.
- [2026-11-06] Re-QA verdict: `QA_PASSED` (no vulnerabilities, no missing tests; no `server.py` change). Re-review verdict: `PO_REVIEW_PENDING` (technical verdict: `APPROVED`). F1 preflight+relay aligned; F2 regression pins both; F3 version/artifact/changelog consistent; no server.py change. File remains in `tasks/qa/`; closure awaits Manager's explicit `Approved for closure` / `Close task`.

### Reviewer Follow-up Checklist

- [x] Add preflight-alignment regression test (red-first)
- [x] Align Capability Preflight approval paragraph with envelope + direct-answer rules
- [x] Re-verify all gates, re-stage, chain re-review
- [x] Align Review-approval relay acceptance clause + pin test (reviewer hotfix 2); re-verify, re-stage, chain re-review

## QA Follow-up Checklist

- [x] Add negative-case regression test (test-only, no prompt change)
- [x] Re-run prompt-sync (32 passed) + full suite (800 passed) + py_compile + docs-sync
- [x] Record evidence, lint, re-stage, chain re-QA

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `4eae396c9fb6bed4712c585ae502f2467d71a821`
<!-- END_GIT_DIFF -->
