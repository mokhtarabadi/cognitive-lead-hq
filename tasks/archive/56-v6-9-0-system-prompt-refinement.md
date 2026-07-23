# Task: V6.9.0 System Prompt Refinement

**File:** `tasks/in-progress/56-v6-9-0-system-prompt-refinement.md`
**Type:** improvement
**Status:** closed

## Goal

Upgrade system-prompt.md to V6.9.0 with:
1. Discovery-First Mandate for Architect and UI/UX personas
2. Environmental Checklist for UI/UX Designer
3. Anti-Hack / Clean Architecture Mandate for Senior Programmer
4. PO Approval Gate separating technical review from business closure

## Manager's Notes

- Bump `<system_version>` from 6.8.0 to 6.9.0
- Inject Discovery-First Mandate into Software Architect
- Inject Discovery-First Mandate + Environmental Checklist into UI/UX Designer
- Inject Anti-Hack Directive into Senior Programmer
- Separate Code Reviewer's technical approval from PO closure in execution workflow
- Update CHANGELOG.md with V6.9.0 entry

## Local TODOs

- [x] Step 1: Create task file
- [x] Step 2: Patch system version to 6.9.0
- [x] Step 3: Patch Software Architect persona
- [x] Step 4: Patch UI/UX Designer persona
- [x] Step 5: Patch Senior Programmer persona
- [x] Step 6: Patch Code Reviewer persona & execution_workflow
- [x] Step 7: Update CHANGELOG.md
- [x] Step 8: Run prettier and verify XML balance

## OpenCode Execution Log & Reasoning

### Architecture & Reasoning

**V6.9.0 Patches Applied:**

1. **Software Architect** — Injected **Discovery-First Mandate** at the top of `<behavior>`. Forbids blueprint generation without factual codebase context. Original text already said "If you lack sufficient codebase context, STOP" — the new mandate front-loads this as a hard rule before any other instruction.

2. **UI/UX Designer** — Injected **Discovery-First Mandate** (no hallucinated layouts) + **Environmental Checklist** (offline states, latency, Dark/Light mode, a11y). The checklist ensures designs consider non-happy-path conditions.

3. **Senior Programmer** — Injected **Anti-Hack Directive** as the first rule in `<behavior>`. Forces the persona to STOP and propose clean refactors when bugs tempt fragile fixes (arbitrary `setTimeout`, framework bypasses).

4. **Code Reviewer** — Changed post-approval behavior: now outputs `PO_REVIEW_PENDING` instead of immediately generating a commit task. Commits + closure only happen on Manager keywords "Approved for closure" or "Close task".

5. **Execution Workflow (Steps 5-8)** — Split old step 7 (Commit & Close) into three distinct steps:
   - Step 5: Code Review → APPROVED / APPROVED_WITH_CHANGES / REJECTED_NEEDS_FIXES. If technical approval → PO_REVIEW_PENDING.
   - Step 7: New **PO Acceptance** step — Manager validates UX/business logic.
   - Step 8: **Commit & Close** — Only fires on explicit Manager keywords.

6. **CHANGELOG.md** — Added `[6.9.0]` entry with all four additions documented.

7. **Version bumped** from 6.8.0 to 6.9.0 in `<system_version>`.

8. **Verification** — `prettier` confirmed no formatting issues; XML tag balance verified (all structural tags paired correctly).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3a938e76c2d63126cf211c7dd8024daf886bdb6f`
<!-- END_GIT_DIFF -->
