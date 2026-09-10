# Task 178: Prompt optimization — brainstorm stub + clarity style

**File:** `tasks/completed/178-prompt-optimization-brainstorm-stub-and-clarity-style.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Optimize `system-prompt.md` / `prompts/fragments/` for token efficiency and manager-facing clarity: stub the duplicated brainstorming protocol (hybrid, not full delete) and add ASD-STE100-inspired clarity constraints scoped to the final response only.

## Manager's Notes

Approved after LLM-level analysis (2026-09-10): (1) Don't fully delete `prompts/fragments/12-brainstorming_protocol.md` — the Brain needs a trigger in the system prompt, skill alone only covers Hands. Hybrid = short stub (~12 lines) linking to `brainstorm-swarm` skill detail. Saves ~350 tokens. (2) ASD-STE100 paste is compatible if scoped to final Manager response only — deep reasoning thinking stays rich, only the externally visible output is simplified (short sentences ≤25 words, one idea per sentence, defined context before reference, active voice, compressed list codes). (3) Executor cognitive roles are healthy — minor matrix addition only.

Scope: `prompts/fragments/12-brainstorming_protocol.md` stub, `system-prompt.md` via prompt composer (never hand-edit directly), `agents/cognitive-executor.md` patterns update, `CHANGELOG.md`. Assembled `system-prompt.md` must stay byte-identical to `prompts/fragments/` + `prompts/shared/` (verify via `lint_system_prompt_sync`).

## Local TODOs

- [x] Stub `prompts/fragments/12-brainstorming_protocol.md` to hybrid trigger (keep Brain trigger, delegate detail to `brainstorm-swarm` skill)
- [x] Add clarity constraints for final Manager response (ASD-STE100-inspired, scoped — not deep reasoning)
- [x] Update `agents/cognitive-executor.md` Communication Patterns to reflect clarity style + add brainstorm-swarm matrix row
- [x] Re-assemble `system-prompt.md` via prompt composer and verify byte-identical (`lint_system_prompt_sync`)
- [x] Update `CHANGELOG.md` via Parse-Then-Append
- [x] Lint task file + verify, then stage and move to QA

## Acceptance Criteria

- [x] `prompts/fragments/12-brainstorming_protocol.md` is a short stub (not 52 lines) that still triggers Brain-side brainstorming and points to `brainstorm-swarm` skill for full session procedure
- [x] `system-prompt.md` contains clarity constraints scoped to final response only (does not suppress deep reasoning)
- [x] `agents/cognitive-executor.md` reflects clarity style in Positive/Negative Patterns and lists `brainstorm-swarm` in skill matrix if applicable
- [x] `lint_system_prompt_sync` passes (assembled file in sync)
- [x] `CHANGELOG.md` updated
- [x] `lint_task_file` passes on `tasks/in-progress/178-*.md` (post-move)

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py` + `lint_system_prompt_sync` + `lint_task_file tasks/in-progress/178-prompt-optimization-brainstorm-stub-and-clarity-style.md` + `wc -l prompts/fragments/12-brainstorming_protocol.md; grep -n brainstorm-swarm prompts/fragments/12-brainstorming_protocol.md` + `grep -n "Response Clarity" system-prompt.md prompts/fragments/13-constraints.md` + `grep -n brainstorm-swarm agents/cognitive-executor.md` + `grep -n 178 CHANGELOG.md | head`
- **Expected result:** stub is ~6 lines with skill reference; clarity clause present and scoped to final response; compose + sync in-sync; lint passes; CHANGELOG has 178 entry
- **Actual result:** assemble ok (638 lines, 74178 bytes, diff byte-identical SYNC OK); `lint_system_prompt_sync` ✅ in sync; `lint_task_file` ✅ passed; `wc -l` 6 with `brainstorm-swarm` ref (line 4); `Response Clarity — Final Manager Response Only` present in system-prompt.md and fragment 13; executor has `brainstorm-swarm` row; `CHANGELOG.md: Task 178` entry present
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Over-stubbing removes Brain trigger → brainstorming never fires. Over-scoping clarity style suppresses chain-of-thought reasoning.
- **Rollback plan:** `git diff prompts/fragments/12-brainstorming_protocol.md system-prompt.md agents/cognitive-executor.md` + `git restore` those three files + re-compose; task file stays in `tasks/in-progress/` until QA.

---

## Execution Log & Reasoning

**Scope (hybrid, not full delete):** Manager approved: stub keeps Brain trigger (task discovery), Hands delegates detail to skill. ASD-STE100 style scoped to final Manager response only — chain-of-thought stays rich.

**Edits (5 files):**
- `prompts/fragments/12-brainstorming_protocol.md` — replaced 53-line persona table + report schema with 6-line stub: trigger `cross-disciplinary ambiguity OR explicit \"brainstorm\"` → `Max one turn per Orchestrator request, load skill \"brainstorm-swarm\" for full persona matrix + report schema`. Saves ~350 tokens per session.
- `prompts/fragments/13-constraints.md` — added `Response Clarity — Final Manager Response Only` constraint: ≤25 words, one idea/sentence, define before reference, active voice, coded lists `F/D/R/Q/A`, does not apply to internal reasoning.
- `prompts/fragments/01-system_version.md` — `9.12.0` → `9.13.0`.
- `system-prompt.md` — regenerated via `python3 scripts/prompt-build/assemble_system_prompt.py` → 638 lines (from 684), 74178 bytes, byte-identical to fragments+shared (diff 0, SYNC OK). Not hand-edited.
- `agents/cognitive-executor.md` — Positive Patterns added scoped clarity bullet; Skill Auto-Loading Matrix added `brainstorm-swarm` row (`cross-disciplinary ambiguity`).
- `CHANGELOG.md` — Unreleased `Changed` entry for Task 178 via Parse-Then-Append.

**Verification:** `lint_system_prompt_sync` ✅, `lint_task_file` ✅, grep checks ok (stub 6 lines, Response Clarity hits, brainstorm-swarm in executor, 9.13.0, Task 178 in changelog).

**Closure (2026-09-10):** QA approved; Manager authorized closure via `<hands_implementation_task>`. Header updated (`**File:** tasks/completed/...`, `**Status:** closed`), file moved `tasks/qa/` → `tasks/completed/` via `git mv`. CHANGELOG Task 178 entry verified present on disk (line 36, no duplicate appended). Closed via `custom_context_commit_and_clean_task`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `2afdff8a98cb925bd2321bd3ebb282da503c91a2`
<!-- END_GIT_DIFF -->
