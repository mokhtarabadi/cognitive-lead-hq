# Task 322: Language policy - English inside, requested language outside

**File:** `tasks/completed/322-language-policy.md`
**Source:** manager
**Type:** chore
**Status:** closed
**Project:** /home/mohammad/Develop/Projects/cognitive-lead-hq
**Priority:** High

## Goal

Translate-first pipeline with English-only internals and per-message requested-language handoff, wired through fragments, executor, conventions, and tests.

## Rule (owner-approved 2026-10-17)

Non-English input (Manager speaks Persian) is ALWAYS translated to technical
English first; execution runs on the English version only. The
`prompt-refactor` skill is invoked for complex/multi-intent messages; short
clear messages use lightweight inline translation. Voice-to-text normalization
stays step one (existing Direct Input rule).

Internal reasoning, task files, evidence, logs, and ALL Brain communication
stay English, no exceptions. Only the Manager-facing handoff may use the
requested language (detected per message, Persian default for this Manager).

## Hard guards (part of the rule, not optional)

1. Approval phrases (`Approved for closure`, `Close task`, plan-gate
   `approved`) match ONLY as English literals. Never translate-then-compare.
2. Skill gating by complexity: refactor skill for complex messages, inline
   translation for short clear ones. No blanket skill call per message.
3. Evidence/logs/task files English always — auditability over comfort.
4. Output language detected per message, not pinned to a session default.

## Deliverable

New prompt fragment (language policy) wired into `system-prompt.md` generation
+ executor boundary update + sync test update. Owner implements.

## Local TODOs

- [x] Steps 1-10: fragment 24, manifest, version, 05, 13, 20, executor, conventions, tests, rebuild

## Acceptance Criteria

- [x] Persian order executes on its English translation with identical gates.
- [x] Approval matching untouched by translation layer (test proves it).
- [x] Brain turns carry English only.
- [x] Manager handoff follows per-message requested language.

## Execution Log

- Created 2026-10-17 from Manager directive. Owner implements.

## Definition of Done

- [x] Assembler plus tests pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append

## Risk & Rollback

- **Risk:** Prompt plus executor plus conventions drift if the rebuild step is skipped; stale English-always phrases resurfacing.
- **Rollback plan:** Revert prompt and doc hunks via `git checkout --` on the touched paths only.

## Execution Log & Reasoning

- Seat Check: prompt-protocol domains, no trigger words fired (explicit miss on all seats), Architect minimum by domain, single-seat plan, brainstorm not required (doc-level, reversible). One discovery round used (fed-context: fragments 05/13/20, manifest, builder, tests); final grounded plan approved by Manager ("Approved").
- Implemented 10 steps: fragment 24 created; manifest appended; version 9.61.0; fragments 05/13/20, executor, and conventions updated to inside/outside with approval literals guard; both sync tests updated; system-prompt.md rebuilt (111187 bytes, byte-identical re-assemble).
- D1: split_system_prompt.py is destructive (rewrites fragments from the prompt, drops unassembled files) — recovered via git checkout and re-applied edits; round-trip verification uses assemble-twice diff, never split.
- Stack-skill skip record: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only prompt-text change".

## Verification Evidence

- `rtk test /home/mohammad/v2ray-to-subs/.venv/bin/pytest tests/test_prompt_sync.py tests/test_input_validation_pipeline.py -q` — expected all pass, actual 20 passed, exit 0. (Repo has no local pytest; foreign venv binary used as runner only.)
- Greps: `simple English` 0 hits in 05/conventions/executor; `per-message requested language` hits in 05, 13, conventions, executor; `Never answer the Manager in another language` 0 hits; `Approval Literals Guard` in shipped; `9.61.0` in 01/tests/shipped.
- Assembler: `python3 scripts/prompt-build/assemble_system_prompt.py --output system-prompt.md` exit 0, byte-identical re-assemble verified (111187 bytes, 9.61.0).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `786714b52ed2b7c7e12c047b0be12f4d71a2719f`
<!-- END_GIT_DIFF -->

- Rework try 2 (Reviewer REJECTED_NEEDS_FIXES, R1+R2): fragment 13 Cognitive Rule no longer lists clarification requests as English-only (handoff including clarification uses requested language); fragment 20 handoff line moved inside `</communication_examples>`. Rebuilt 9.61.0 (111226 bytes, byte-identical re-assemble), no version bump.
- Stack-skill skip record: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only wording fix".

- Rework try 3 (Reviewer 2nd rejection, duplicate close): fragment 20 tail fixed to single `</communication_examples>` as final line; rebuilt 9.61.0 (111199 bytes, byte-identical re-assemble), 20 tests pass. My earlier placement claim was wrong — verified against the diff this time.

- Review try 3: technical APPROVED, PO_REVIEW_PENDING. Awaiting Manager accept word for closure.

- Closure: Manager accept quote "Approved for closure" logged, closure executing exactly once. Stack-skill skip: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="closure-only lane move plus commit tool".
