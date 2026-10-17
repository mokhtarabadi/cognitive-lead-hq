# Task 321: Cognitive tune-up round (Lite, goal sync, skills, compaction)

**File:** `tasks/completed/321-cognitive-tuneup-round.md`
**Source:** manager
**Type:** chore
**Status:** closed
**Project:** /home/mohammad/Develop/Projects/cognitive-lead-hq
**Priority:** High

## Goal

Risk-based Lite entry, executor goal-sync rule, skill fallback rule, and single compaction authority across HQ prompts and docs.

## Scope (owner-approved 2026-10-17)

Four workstreams. Explicitly OUT: ferrying reduction — task 320 stays
as-is per owner decision (full task-file copy-paste each turn is kept
for full context; do not pursue 320 in this round).

## 1. Lite Mode redefinition (risk-based, not file-count)

Today Lite dies on the second touched file. Redefine eligibility by risk:
any file count allowed while the change touches no security / financial /
CLP / auth / migration surface. The decision moves from file count to
automatic gates (tests green + lint clean + §17-style greps). Update the
Lite protocol + escalation triggers. Owner fixes.

## 2. Goal sync rule (from goal-plugin deliberation, 3 conditions)

Hands writes goal status at `block` and at closure via the `goal_evidence`
tool (2 writes per goal, no background reads). Kanban stays single truth;
goal files are scratch resume pointers; on conflict Kanban wins. Plugin
needs no change — this is executor behavior. Write it into
`agents/cognitive-executor.md` (Goal Plugin Boundary section).

## 3. Skill matrix vs real stacks

`android-kotlin` does not cover Java-8 Android Views; nothing covers plain
Node CommonJS Cloud Code. Either add precise skills or define a binding
fallback rule (closest skill + explicit skip record with reason). Update
the Skill Auto-Loading Matrix.

## 4. Single-source compaction

Native auto-compact + Smart Compact write async side by side and can
diverge from task-file truth. Make the task file the sole reference:
one writer owns pruning, the other is disabled or slaved to it. Update
the Compaction section.

## Local TODOs

- [x] Steps 1-6 prompt and doc edits
- [x] Step 7 rebuild plus CHANGELOG plus tests

## Acceptance Criteria

- [x] Lite eligibility is risk-based with gate-decided entry.
- [x] Goal sync rule written; plugin untouched.
- [x] Every real stack has a covering skill or a defined fallback.
- [x] One compaction authority; task file is the reconcile target.
- [x] 320 explicitly left alone.

## Definition of Done

- [x] Assembler plus tests pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append

## Risk & Rollback

- **Risk:** Fragment plus executor plus conventions drift apart if the rebuild step is skipped.
- **Rollback plan:** Revert prompt and doc hunks via `git checkout --` on the touched paths only.

## Execution Log

- Created 2026-10-17 after 2-round Brain deliberation (Architect +
  Programmer, converged ship-with-changes). Owner implements.

## Execution Log & Reasoning

- Seat Check: executor-protocol domains, trigger word "migration" fired Architect, single-seat plan, brainstorm not required (doc-level, reversible). Brain plan approved by Manager ("Approved").
- Implemented 7 steps: fragment 10 risk-based Lite (no high-risk surface, gate-decided entry, reversible, any file count; escalation triggers); conventions.md mirror with T0 wording; executor Planning Gate Lite line; executor Goal Boundary two-writes rule (block + closure, Kanban wins, plugin untouched); registry + matrix Binding Fallback Rule with Java-8 Views and plain Node CommonJS rows, no new skills; sole-reconcile-target authority line in fragment 22, docs/compaction.md, executor; rebuilt system-prompt.md 9.60.0.
- D1: fallback rule instead of new skills (token bloat). D2: prompt-text refinements only, no sibling ADR changes (inspected prompts/fragments, agents, docs READMEs/DECISIONS.md, no domain contract change).
- Stack-skill skip record: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only prompt-text change, no stack marker applies".

## Verification Evidence

- `python3 scripts/prompt-build/assemble_system_prompt.py` expected exit 0 (recorded below).
- Stack-skill skip: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only prompt-text change".

- Verification run 1: `rtk test /home/mohammad/v2ray-to-subs/.venv/bin/pytest tests/test_prompt_sync.py tests/test_skill_registry.py -q` — expected all pass, actual 29 passed, exit 0. (Repo has no local pytest; foreign venv binary used as runner only. RTK wrapper preserved exit code with 3-line summary.)
- Greps: `Any file count allowed` 3 hits (fragment 10, conventions, executor); `sole reconcile target` 3 hits (fragment 22, docs/compaction, executor); `Binding Fallback Rule` 2 hits (registry, executor); `Goal sync rule` 1 hit (executor).
- Assembler: `python3 scripts/prompt-build/assemble_system_prompt.py --output system-prompt.md` exit 0, byte-identical re-assemble verified (108083 bytes, 9.60.0).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `bfbbe476f642aadc374463b667fb9791470de70a`
<!-- END_GIT_DIFF -->

- QA: QA_PASSED (all 4 workstreams verified, 29 tests, 320 untouched). Review: technical APPROVED, PO_REVIEW_PENDING. Awaiting Manager accept word for closure.

- Rework per Manager (try 2): goal sync closure wording fixed — first `goal_evidence` then `goal_complete`; `goal_complete` takes no arguments. Version 9.60.1.

- Rework try 3 (Reviewer R1, APPROVED_WITH_CHANGES): Agent lane tools-only list now includes `goal_evidence` for consistency with the sync rule. No version bump (executor is not assembled into system-prompt). D3: one-token consistency fix, no CHANGELOG entry, sibling docs inspected with no change.
- Verification run 3: `rtk test /home/mohammad/v2ray-to-subs/.venv/bin/pytest tests/test_prompt_sync.py tests/test_skill_registry.py -q` — expected all pass, actual 29 passed, exit 0. Greps: Agent lane line shows `goal_evidence`; Goal sync rule shows block plus `goal_evidence` then `goal_complete`.
- Stack-skill skip: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only executor prose fix".

- QA try 3: QA_PASSED. Review try 3: technical APPROVED, PO_REVIEW_PENDING. Awaiting Manager accept word for closure.

- Closure: Manager accept quote "Approved for closure" recorded; closure executed; version 9.60.1; 29 tests pass; 320 untouched. Stack-skill skip: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="closure-only file move plus commit tool".
