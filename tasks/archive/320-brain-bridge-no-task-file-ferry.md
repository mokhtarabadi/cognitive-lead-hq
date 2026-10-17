# Task 320 — Brain bridge without full task-file ferrying

**File:** tasks/archive/320-brain-bridge-no-task-file-ferry.md
**Status:** archived
**Project:** /home/mohammad/Develop/Projects/cognitive-lead-hq
**Priority:** High

## Problem

Every `brain_turn` (plan, QA, review) currently carries the entire task file
plus full diff, copied by hand between Hands and Brain. On large tasks this
burns tokens, hits truncation (2000 lines / 50KB), and slows every loop —
while the Brain only needs the decision inputs.

## Goal

Redefine the bridge payload: the Brain receives `diff` hunks + `Execution Log`
+ verdict question only. Full task-file copy is forbidden. The task file stays
where it is; the Hands sends pointers (task id + lane), never the body.

## Scope

- `mcp-brain-bridge` payload builder + `system-prompt.md` bridge section.
- Plan / QA / review turn templates (what each must carry at minimum).
- Fallback rule: when the Brain judges the hunk pack insufficient, it requests
  named ranges (file + line spans), never the whole file.

## Acceptance

- [ ] No turn requires pasting a full task file.
- [ ] Each turn type has a documented minimum payload.
- [ ] Truncation path degrades to range-requests, not silent cuts.
- [ ] Existing gates (plan approval, QA, review, closure wording) unchanged.

## Execution Log

- Task created 2026-10-17 from Manager direction (proposal 2 of cognitive tune-up). Owner implements.

---
Archived 2026-10-17 per Manager order. Left as-is per task 321 scope (owner keeps full task-file ferrying; 320 not pursued).
