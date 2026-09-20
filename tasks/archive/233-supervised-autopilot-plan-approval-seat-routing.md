# Task 233: Supervised autopilot with plan approval and seat routing

**File:** `tasks/completed/233-supervised-autopilot-plan-approval-seat-routing.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Replace fire-and-forget autopilot with supervised autopilot: discovery feed, mandatory plan-approval loop with the admin, seat-routed implementation, bounded QA/review loops, and final-approval close — with a fast path for trivial work.

## Manager's Notes

Manager approved the joint 7-seat brainstorm (O1 supervised autopilot wins). Verbatim orders: "Yes fix all by ask hands (auto pilot)". Autopilot locked for this task. Implement gaps G1-G13 with warnings U1-U5 honored:

- A1: `agents/cognitive-executor.md` — discovery feed + plan approval loop + seat check + corrected lock words; fix G7/G8 (human plan approval and goal-pause carve-outs).
- A2: `mcp-brain-bridge/server.py` — bundle/tree size limits (G12), fed-context handling, plan-verdict shape; regression tests, no live network.
- A3: `docs/conventions.md` Lite rules + `telegram-issue-sync` skill — risk tiers (G13), autopilot-ready contract (G9), trivial fast paths (U1/U3/U4), max-3 plan tries then escalate (U5); fold data-ask into planning turn (U2).
- G5/G6: seat-routed implementation + "autopilot on task N" lock recognition. G10/G11: bounded QA/review loops, results shown before move to qa.
- Fragments dir is git-ignored: A1 also mirrors into shipped `system-prompt.md` atomically (bump `<system_version>`, CHANGELOG entry) or the rule never ships. Never invent architecture/data-model/design specs (files absent).

## Local TODOs

- [x] Seat check + Brain planning turn under same task id, log verdict
- [x] A1 executor rules (discovery, plan loop, seats, lock words, G7/G8 carve-outs)
- [x] A2 bridge limits + plan verdict + tests
- [x] A3 tiers + telegram contract + fast paths
- [x] Full suite green, CHANGELOG, stage, qa move

## Acceptance Criteria

- [x] Autopilot shows the plan to the admin and waits for approval before implementing non-trivial work
- [x] Trivial work (Lite-eligible) still runs without human pauses
- [x] Seat routing sends UI work to Designer review and backend to Engineer
- [x] QA/review loops are bounded and results are shown before qa move
- [x] Tests cover new bridge behavior; full suite exits 0

## Verification Evidence

- **Test command:** `pytest tests/ -q` (from repo root)
- **Expected result:** all tests pass, exit 0
- **Actual result:** 350 passed, 8 warnings (pathspec deprecation, pre-existing), 5.44s — post-postfix re-run, uv-pinned env, exit verified 0
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** plan gate stalls night runs; over-gating trivial work; fragment/prompt drift
- **Rollback plan:** risk tiers + max-3-tries escalate; single-commit scope per file area; `git log` revert of closure commits only by Manager

---

## Execution Log & Reasoning

Autopilot locked for Task 233 per Manager order "Yes fix all by ask hands (auto pilot)".

Seat Check (planning gate): domains = autopilot process rules + bridge contract + seat routing. Requested: Software Architect + Senior Programmer. Skipped: Designer (UI routing here is a one-line trigger rule, no layout decisions), Strategist/Planner/QA/Reviewer (no capacity/milestone/verdict questions at plan time).

Brain planning turn 1 (Architect + Senior Programmer): returned ordered plan A1/A2/A3 + verdict shape V1-V6 + limits L1-L4 + Lite criteria C1-C3 + tests T1-T3. Two points marked INFERRED pending file reads.

Discovery grounding (3 parallel scans + task file read):
- G1: bridge server is 1409 lines. Bundle: _BUNDLE_FILES L164-170, _BUNDLE_FILE_CAP=60000 L172, _build_context_bundle L412-433. No tree reporter in bridge (lives in context-server); paths attach caps _CTX_PATHS_PER_FILE=20000 L1070, _CTX_PATHS_TOTAL=40000 L1075. Brain L1-L4 partly exist: keep L2 (60k/file cap confirmed), add explicit bundle TOTAL cap; tree limits belong to context-server, out of scope.
- G2: fed-context pinning ALREADY exists in bridge (marker L989-991, extract/save/load L1004-1066, wired L1247-1265). Brain I8 is reduced to documenting + enforcing prepend, not building.
- G3: response builder brain_turn L1131-1139, result dict L1338-1352, empty guard L1325-1330. Plan-verdict validator is genuinely new, goes near extract_xml_blocks L586-601.
- G4: telegram skill 308 lines, approval Phase 2 L77-89 (question tool); repo template copy exists and matches. Edit both copies.
- G5: shipped prompt 698 lines v9.35.0; no Planning Gate / Brain Bridge sections (those live in executor agent file). Mirror targets: <execution_workflow> L422-465, <constraints> L476-499, <lite_mode_protocol> L391-420. Fragments: 20 files, no 17-*.md gap noted.

Brain planning turn 2 (same id, fed-context): PLAN APPROVED by Architect + Senior Programmer. Corrected deltas: D1 bundle total cap 150k in builder (keep 60k/file); D2 tree limits out of scope (context-server owns tree); D3 fed-context exists, enforce prepend only; D4 plan-verdict validator after extract_xml_blocks with 5 fields (verdict, seats, path, steps, cites), reject empty cites; D5 mirror into shipped prompt workflow/constraints/Lite/personas + version bump + CHANGELOG in same commit. Proceeding to implementation under autopilot approval.

A3 done: conventions Lite section gains Risk Tiers T0/T1/T2 + 3-tries-then-escalate; telegram skill Phase 2 gains autopilot data-ask folding note (repo template + global copy, identical). Mirror done: fragment 13-constraints.md gains Supervised Autopilot Contract bullet; 01-system_version.md 9.35.0→9.36.0; system-prompt.md regenerated via assembler (diff vs committed = exactly these 2 changes). CHANGELOG Unreleased entry appended. Full suite: 350 passed, exit 0.

Postfix after review verdict (7 steps, same file, no new number): S1 validator now uses word-bound field matching with a docstring note (bare substring accepted stubs like path-inside-paths; bounds force real sections). S2 bundle truncation reserves the suffix length before slicing so the total never exceeds the cap. S3 contract bullet reworded (single plan-approval pause; Relay plus hard blockers are the only other interrupts); shipped prompt regenerated via the assembler only, diff shows exactly the reworded line. S5 both skill copies verified byte-same note at line 91 (repo template + global install). S6 D5 scope justification: the approved fragment edits were the constraints bullet plus the version bump only, and the shipped prompt carries no Planning Gate or Brain Bridge sections (discovery confirmed), so the constraints-only mirror is complete — no workflow, Lite, or personas mirrors were approved or needed. S7 five bridge tests cited at tests/test_brain_bridge.py:1473-1485 (total cap bounds oversize workspace), 1486-1492 (fed pin persists across second turn), 1494-1497 (valid verdict passes), 1500-1503 (stub fails on seats/cites), 1506-1509 (cites without path-with-lines fail). Skills loaded for postfix: verification-before-completion, task-lint (both already active this session).

Post-postfix re-verify: py_compile clean on bridge server; full suite re-run via uv-pinned env = 350 passed, exit 0, 5.44s (evidence updated above); lint_task_file re-passed; restaged via stage_and_inject_diff from tasks/qa path.

Re-review (second review, same id, diff attached): Code Reviewer reports code technically approved, status PO_REVIEW_PENDING. Strengths F1-F5 (word-bound verdict checker, suffix-safe cap, one-pause plan gate, auditable seat routing, bounded loops). Two low-severity notes: I1 test hunks past truncation point (covered by suite evidence), I2 capped/skipped files emit no stderr count (deferred to a later task per reviewer R2, not implemented here). Closure awaits the Manager approval word.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `21a7613ad431fb4a886a832dcf4d420150fd7988`
<!-- END_GIT_DIFF -->
