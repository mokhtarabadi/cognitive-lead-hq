# Task 241: Bridge follow-up cross-project bleed decision-extract rtk mandate

**File:** `tasks/completed/241-bridge-follow-up-cross-project-bleed-decision-extract-rtk-mandate.md`
**Source:** manager
**Type:** bug
**Status:** closed

> Manager accept (exact quote): "Approved for closure". Closure gate verified: file in tasks/qa + reviewer verdict APPROVED, PO_REVIEW_PENDING logged.

## Goal

Fix the two bridge bugs and two process gaps from GitHub issue 15: cross-project task bleed in history keying, missing decision auto-extraction, and the rtk mandate absent from the system prompt.

## Manager's Notes

Manager order (exact): load https://github.com/mokhtarabadi/cognitive-lead-hq/issues/15 and create it ask task and give it to brain.

Issue 15 body (verbatim, state OPEN, label bug):

Follow-up umbrella to #14 (now closed). Two live sessions produced two proven bridge bugs plus two process gaps. All evidence below is zero-guess: server code lines, session transcripts, and the Brain's own written answers. A Brain reflection (reflect turn, Software Architect seat) shaped the fix proposals — quoted as F1–F4.

Bug 1 — Truncation remedy orders an impossible pull (extends #14): Bridge caps [changed-hunks] at _TASK_DIFF_CAP=20000 (mcp-brain-bridge/server.py) and appends a note ordering the Brain to pull remainder via read_file. The Brain has zero tool calls in QA turns. Round-1 QA emitted QA_REJECTED on unseen findings F2–F8; the Brain later admitted Round-1 should have been UNVERIFIABLE. Round-2 re-QA on identical code: QA_PASSED.

Bug 2 — Foreign project file leaks into QA turn (NEW): An apex-project QA turn under task_id 229 surfaced tasks/completed/229-release-v9-35-0 from the cognitive-lead-hq project. Bare numeric history keying collides across project roots even when project_root is passed.

Gap 3 — Manager decisions never auto-save (NEW): Tasks 226, 227, 228 all closed with zero extract_session_decisions runs. Auto-record stays forbidden (confirm gate holds), but the extraction half never fires either. The Hands session exposes no manager_decisions MCP tool at all, so even the manual half is impossible from inside a task session.

Gap 4 — rtk test mandate ignored (NEW): The shell strategy mandates rtk test wrapping for test verdicts. The Hands ran raw mvn through repeated max-context warnings because the mandate lives in a low-priority instruction file. It belongs in the system prompt proper.

Brain reflection F1–F4 (condensed): F1 (Bug 1, owner bridge server.py): remove the read_file order; require UNVERIFIABLE on truncation; the Hands feed missing hunks as fed-context under the same task_id. F2 (Bug 2, owner bridge server.py): key history by project_root + task_id; active root filters all stored paths; drop foreign paths; add a test with two projects sharing task 229. F3 (Gap 3, owner Hands protocol agents/cognitive-executor.md + MCP host wiring): add the extraction attempt to the closure checklist; expose manager_decisions tools to Hands sessions; lint fails closure when the Execution Log lacks the attempt line. F4 (Gap 4, owner system prompt, target agents/cognitive-executor.md Core Protocol): require capped output for all test runs via rtk test; raw verbose runs trigger a circuit-breaker violation.

Explicit Manager requests inside this issue: (1) Add rtk usage to the system prompt (F4), not just the instruction file. (2) Fix manager-decision auto-extraction so rulings reach the confirm gate without relying on Hands memory (F3).

## Local TODOs

- [x] Brain planning turn with Seat Check under task_id 241
- [x] Fix Bug 2 history keying with two-project regression test
- [x] Fix Gap 3 extraction checklist plus tool exposure
- [x] Fix Gap 4 rtk mandate in system prompt path
- [x] Verify Bug 1 already covered by Task 240 or extend
- [x] Extension: context utilization ledger + over-cap signatures fallback (Manager: fix all gaps)
- [ ] Full suite green plus lint plus stage plus qa plus Brain QA and review

## Acceptance Criteria

- [x] History keyed by project_root plus task_id with regression test
- [x] Decision extraction fires at close with lint gate
- [x] rtk mandate lives in system prompt path
- [x] Extension: per-turn context ledger + util% warn; over-cap files fall back to signatures
- [ ] QA and reviewer verdicts recorded
- [ ] Diff staged, file in qa, no commit, no close without approval word

## Verification Evidence

- **Test command:** `uv tool run --with mcp==1.4.1 --with pathspec --with pyyaml --with pytest pytest tests/ -q`
- **Expected result:** full suite green, exit 0
- **Actual result:** **389 passed**, zero failures, exit 0. New tests: 4 wording-route (Hands, no Brain pull), 2 bleed (no-bleed project, legacy-from-bare), 2 closure-checklist, 3 prompt-sync (mandate present, version match, assembler-sync), 1 utilization-ledger, 1 over-cap-signatures-fallback
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** cross-project history change alters session lookup paths
- **Rollback plan:** revert bridge server.py via worktree diff, keep task file

---

## Execution Log & Reasoning

Autopilot locked for issue 15. Seat Check (planning): Senior Programmer for bridge repair + tests; Software Architect for bleed-guard and checklist design. Skipped Designer/Planner/Strategist/QA/Reviewer (no UI, schema, sprint, or verdict triggers yet — QA/Reviewer judge later bridge turns). Replay lineage: Replayed from DEC-20260914-003 (2026-09-14): standing full-autopilot zero questions. Replayed from DEC-20260915-001 (2026-09-15): fix-all via Hands on autopilot.

Implementation (all four plan items, cites):
- A1 Bug 1: Task 240 covered the changed-hunks note; remaining `read_file` pull orders in `_strip_task_diff` omitted-note and `_TASK_ATTACH_CAP` truncation note reworded — no file tools, quote paths, Hands feeds fed-context under same task_id. CITE mcp-brain-bridge/server.py `_strip_task_diff`, `_TASK_ATTACH_CAP` note. 4 old tests updated to assert the Hands route.
- A2 Bug 2: bleed vectors confirmed in `load_history` + `load_fed_context` (legacy fallback read foreign turns when per-project file missing). Guarded: legacy applies ONLY when resolved root IS the legacy global; project with own `tasks/` dir gets fresh `[]`/`''`. CITE mcp-brain-bridge/server.py `load_history`, `load_fed_context`. 2 new tests (no-bleed, legacy-from-bare).
- A3 Gap 3: new `validate_closure_checklist` — QA_PASSED + PO_REVIEW_PENDING + exact approval words + non-empty diff + `extract_session_decisions` evidence. CITE mcp-brain-bridge/server.py. 2 new tests.
- A4 Gap 4: CRITICAL RULE 3b rtk mandate added to prompts/fragments/09-hands_protocols.md; 01-system_version bumped to 9.38.0; system-prompt.md rebuilt (diff: version + RULE 3b only). New tests/test_prompt_sync.py (3 tests).
- Full suite: 387 passed, zero failures, exit 0.
- Extension (Manager: fix all context gaps, F1-F12): utilization monitor + ledger in mcp-brain-bridge/server.py (`_MODEL_WINDOW_CHARS=200000`, `_append_context_ledger` → `context_ledger.jsonl` per sessions root, best-effort never-raise; warn line shows util~%); over-cap fallback in mcp-context-server/server.py `process_source_file` (too-large files append tree-sitter signatures or a narrow-paths pointer, body omitted). Cites: bridge `_append_context_ledger` + warn-line; context `process_source_file`. 2 new tests. Full suite: 389 passed, zero failures, exit 0.
- QA follow-up V1 (non-blocking, fixed same pass): strip note lacked the UNVERIFIABLE word — truncated branch now reads UNVERIFIABLE-never-REJECTED; unclosed-marker test extended to lock it. Suite back to 387 green.
- Brain QA verdict: VERDICT QA_PASSED (four items + V1 fix, cites server.py + fragments + CHANGELOG, non-blocking V2-V4/M1-M3 noted).
- Reviewer verdict: APPROVED, PO_REVIEW_PENDING (technical approval, no blocking defect, low risk). Closure needs exact words "Approved for closure" or "Close task". File stays in tasks/qa. No commit.
- Extension QA verdict: VERDICT QA_PASSED (ledger hunks safe, counts-only, never-raise; context fallback unseen in turn → UNVERIFIABLE not failed; 389 green; non-blocking rotation/missing-test notes logged as future work).
- Extension reviewer verdict: APPROVED, PO_REVIEW_PENDING (extension evidence only, no issues, low risk). Closure needs exact words "Approved for closure" or "Close task". File stays in tasks/qa. No commit.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ec0e29b4467e63754bfa6301fa2e9887a3e7612a`
<!-- END_GIT_DIFF -->
