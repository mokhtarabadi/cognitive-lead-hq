# Task 0366: Telegram candidate brief and prompt-refactor two-step

**File:** `tasks/completed/0366-telegram-candidate-brief-and-prompt-refactor-two-step.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-02T08:32:55Z
**Submitted:** 2026-11-02T08:25:57Z
**Started:** 2026-11-02T08:06:13Z

## Goal

Enhance telegram candidate selection to show message briefs instead of bare IDs in the `question` tool, and enhance prompt-refactor skill into an explicit two-step Refactor-then-Execute workflow.

## Manager's Notes

Raw request (normalized): "Analyze telegram skill templates, learn them. The issue: when it shows me a list of candidate messages it shows me message IDs, but IDs are not visible in official Telegram apps so I don't understand which ID relates to which message. It is better it shows me the brief of each message instead of ID in `question` tool. Second: prompt-refactor when I load it — my prompt needs to pass two steps: first the agent enhances and fixes my prompt, then second executes the formatted XML prompt. Enhance it too. Task required. Autopilot lock."

Scope: `skill-templates/telegram-issue-sync/SKILL.md` Phase 2 approval UX plus `skill-templates/prompt-refactor/SKILL.md` workflow plus minimal mirror edits in prompt fragments. Autopilot locked.

## Local TODOs

- [x] Map telegram candidate selection UX and prompt-refactor current workflow
- [x] Implement brief-based candidate options (label/descriptions carry brief, ID stays machine value)
- [x] Implement prompt-refactor two-step Refactor-then-Execute workflow
- [x] Verify functionality

## Acceptance Criteria

- [x] Telegram candidate picker no longer asks Manager to provide bare message IDs; each option shows date/time sender plus first ~80 chars plus type/topic, ID kept as internal value only
- [x] Manual-mode fallback uses numbered brief list with server-side ID mapping
- [x] Prompt-refactor skill defines Step 1 enhance/fix and Step 2 execute formatted XML as live instruction with gate rules
- [x] Fragment callers mirror the two-step wording without scope creep

## Verification Evidence

- **Test command:** rtk test uvx pytest tests/test_prompt_sync.py -q
- **Expected result:** 22 shipped-prompt content gates pass, version in sync at 9.70.0
- **Actual result:** 22 passed in 0.22s; version 9.70.0 in fragment, test pin, and assembled prompt
- **Exit code:** 0

> Verification runner rule: `uvx pytest tests/test_prompt_sync.py -q` is the complete underlying test command. The first verification run used the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

Additional evidence: `python3 scripts/check_docs_sync.py` → `docs-sync: OK` (one warn-only pre-existing ORPHAN `scripts/release-9.66.0.sh`), exit 0. Risk greps (`auth|secret|migration|ledger|money|PII`, case-insensitive) hit only benign pre-existing mentions (skill registry entry, trigger-map pattern, prose examples); no high-risk surface. Bare-ID ask grep (`Provide the Message IDs|provide message IDs`) exits 1 (removed); `brief-first` 1 hit; `Two-Pass Refactor-then-Execute` 1 hit; `After Deliver, execute` hits in 05/executor/07/24 fragments. Stack skill skip: root `.`, marker scan list `go.mod, build.gradle.kts, Package.swift, pyproject.toml, package.json, nest-cli.json, vite.config, nuxt.config`, matched skills none, reason phrase no stack marker found for markdown task with python test gate only. lsp not applicable for markdown (reason phrase markdown only). `lint_task_file` runs in summary phase.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Low-medium. Skill wording changes only; risk is over-broad edits to unrelated fragments or breaking lint contract.
- **Rollback plan:** Revert skill-template edits via git worktree diff; task file remains as audit trail.

---

## Execution Log & Reasoning

**Input Corrections:** analyze, show, candidate, brief, need, enhance, formatted, execute. **Ambiguous terms:** None blocking. **Clarity Score:** 4/5.
Assumption A1: Telegram fix targets `skill-templates/telegram-issue-sync/SKILL.md` Phase 2 only; format/export skills display-only unless Brain plan says otherwise.
Assumption A2: Prompt-refactor Step 2 executes under existing gates (plan approval / ZAC / QA), no auto-bypass.
Mode: Autopilot locked for 0366.
Seat Check (pre-planning): domains are SOP wording + approval UX, no layout/dialog/theme/RTL/a11y trigger words in TITLE+BODY, no schema/contract/migration/quota/index/API-design trigger words, no flaky/race/deadlock/silent-fail/performance trigger words. UX-intent fallback does not fire (no user-visible surface named). Result: Architect seat minimum for SOP contract change; Designer/Programmer triggers miss stated explicitly.
Plan verdict (Brain planning turn, same task ID): REPORT plan received, no further discovery needed. Brainstorm: not required. Lite: not eligible, Tier T1 standard, full supervised autopilot with plan-approval pause. Seat routing: S1 Architect owns WHAT (this plan), S2 Senior Programmer owns HOW (implementation XML after approval), S3 QA adversarial on ID leakage/gate bypass, S4 Reviewer on lint/discipline/hygiene. Awaiting Manager approval (try 1 of 3) before requesting implementation XML.
Approval received: "Approved" (try 1 of 3, no edits). Requested Senior Programmer implementation XML via brain_turn (same task ID); XML_EXTRACTED received and Gatekeeper validation passed (no rule violations; allowlist respected, ZAC holds, no audit-agents touch).
Step 1 findings: anchors confirmed — F1 Phase 2 L92-98 verbatim `Provide the Message IDs` ask present; F2 L55-64 ends at Deliver with no Execute pass; F3 mirror anchor `05-user_input_processing.md:31` (Prompt Refactor Gate); F4 matrix row `agents/cognitive-executor.md:73` plus Direct Input section L80-87 plus Planning Gate L290; F5 registry `07-agent_skills_registry.md:16`; F6 `24-language_policy.md:11`. Memories applied: telegram-sync/message-formatting-contract, workflows/approval_gates_use_question_tool, project/fragment-edit-regenerate-workflow (edit fragment, bump 01-system_version.md, prettier, regenerate via assembler, verify version sync). Absent-File Policy: docs/architecture.md and docs/data_model.md do not exist, skipped.
⚠️ failure_report (Step 1 edge triggered, zero edits made): verifier `scripts/verify-templates.sh` is MISSING — `ls` confirms scripts/ holds only DECISIONS.md, README.md, check_docs_sync.py, prompt-build/, release-9.66.0.sh. `check_docs_sync.py` is not a valid substitute (it gates permission-denies vs docs table plus orphan scan, unrelated to template verification). Nearest candidate `tests/test_prompt_sync.py` gates shipped-prompt content but pins shipped version to 9.69.0, which collides with the mandatory version bump for fragment edits (memory workflow + AGENTS.md version rule) outside the XML allowlist F1-F8. Awaiting Brain adjudication on fallback verifier and version-bump scope before any edit.
D1 adjudication (Brain amended XML): halt was correct; allowlist extended to F9 `prompts/fragments/01-system_version.md` bump plus F10 `tests/test_prompt_sync.py` pinned-version-only update; fallback verifier `rtk test` on `tests/test_prompt_sync.py` plus `check_docs_sync.py` plus `lint_task_file` plus risk greps. D2: pin confirmed 9.69.0 at test line 47, bumped to 9.70.0 in fragment, test, and regenerated prompt (atomic, no other test logic touched). D3: `check_docs_sync.py` takes no args, exit 0 with one warn-only pre-existing ORPHAN line. D4: the amended XML bash commands dropped shell quotes around multi-word grep patterns; the corrected quoted forms were run instead (bare-ID removal proven exit 1, mirrors proven present). D5: no local `pytest` exists (no root pyproject), so the suite ran via `uvx pytest` under the `rtk test` prefix.
Implementation notes: Phase 2 now brief-first (label timestamp/sender/80 chars/type/topic, description full snippet plus audit ID, value numeric ID only, numbers-or-names-or-All closing, numbered manual fallback with same-turn server-side mapping, telegram-message-format contract cited). Prompt-refactor workflow is Two-Pass Refactor-then-Execute (Step 1 refactor keeps Step 0 corrections, enrichment, draft, refine; Step 2 executes under plan approval, ZAC, QA, closure gates, ambiguity halts to one question). One-line mirrors placed in 05 gate, executor matrix row plus Direct Input protocol, 07 registry, 24 execution binding. Prettier exit 0 (also normalized pre-existing indentation in 05/07 and the Phase 3 HTML example reflow in telegram-issue-sync; content unchanged). Assembler exit 0, 111596 bytes, version in sync. Sibling docs: ADR-004 (skill-templates), ADR-007 (fragments), executor delegation entry (agents). Diff stat shows only allowlisted files plus the three DECISIONS.md sync files plus generated system-prompt.md.
QA verdict (Brain QA Engineer turn, same task ID, diff attached): QA_PASSED. F1 ID transcription closed, F2 gate bypass closed, F3 version triple in sync (22 green, docs-sync OK), F4 prettier drift benign, F5 scope/hygiene clean. No additional unit test required. Ready for Code Reviewer.
Review verdict (Brain Code Reviewer turn, same task ID, diff attached): APPROVED technically, Status PO_REVIEW_PENDING. Strengths F1 brief-first picker, F2 two-pass bound to gates with no bypass, F3 version triple in sync, F4 scope/discipline clean, F5 shipped prompt rebuilt with changelog, no autonomous commit. No blocking issues, severity none. PO review of UX and business logic remains. Manager accept quote: "Approved for closure" (exact closure phrase, reply to relayed PO_REVIEW_PENDING question). Preconditions verified: file in tasks/qa, PO_REVIEW_PENDING in log. Requesting Senior Programmer closure XML via brain_turn (single issuance).
Closure 2026-11-02: moved tasks/qa → tasks/completed, Status closed, File header synced. QA_PASSED and reviewer APPROVED carried with zero rejections. Stack skill skip: root `.`, markers go.mod/build.gradle.kts/Package.swift/pyproject.toml/package.json/nest-cli.json/vite.config/nuxt.config, matched none, reason no stack marker found for markdown closure. lsp not applicable for markdown.

### Discovery-fed context

[fed-context]
- `skill-templates/telegram-issue-sync/SKILL.md` Phase 2 L92-98: candidate approval asks Manager to provide message IDs; per-candidate fields are Message ID + 200-char snippet + type + reply parent.
- Official Telegram apps never render internal numeric ID; Manager cannot join snippet to ID in-app, transcription error risks wrong sync anchor.
- `skill-templates/prompt-refactor/SKILL.md` L55-64: workflow ends at Deliver (output final prompt in code block); no Execute second pass exists in skill or callers (`05-user_input_processing.md:31`, executor matrix row).
- Memories applied: `telegram-sync/message-formatting-contract` (HTML formatting rules for any Telegram-facing text), `workflows/approval_gates_use_question_tool` (approval gates must use question tool).
- Absent-File Policy: `docs/architecture.md` and `docs/data_model.md` do not exist; skipped gracefully.
[/fed-context]

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `13de1b59a7738d5699020f52ae9afe6d896e1214`
<!-- END_GIT_DIFF -->
