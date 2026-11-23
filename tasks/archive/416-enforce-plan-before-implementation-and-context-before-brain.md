# Task 416: Enforce plan-before-implementation and context-before-brain on direct Manager input

**File:** `tasks/archive/416-enforce-plan-before-implementation-and-context-before-brain.md`
**Source:** manager
**Type:** improvement
**Status:** superseded
**Superseded-By:** `417-comprehensive-prompt-and-workflow-hardening-across-fragments-agents-and-brain-context`
**Superseded-At:** `2026-11-22 20:56 UTC`

## Goal

When the Manager talks directly to the cognitive agent (Hands) — i.e., ad-hoc input that is NOT an XML task block — the Hands sometimes implements immediately without asking the Brain for a plan first, and the Brain sometimes does not ask the Hands for context before planning. This breaks the mandatory workflow: **plan before implementation** (Planning Gate in `agents/cognitive-executor.md`) and **context before brain** (MCP-First Context + Context Map from Task 415). The fix is to make both gates non-skippable on direct Manager input, with a hard halt if either is missing.

## Manager's Notes

- **Symptom:** Manager says something like "fix the login bug" directly to the Hands. The Hands skips the Planning Gate (no `brain_turn` planning call), implements immediately, and never feeds context to the Brain. The Brain, in turn, never asks for context (no `missing_context` or discovery task), producing plans from assumptions.
- **Root cause (Hands side):** `agents/cognitive-executor.md` §"Direct Input (Ad-Hoc) Validation Protocol" says "Write a brief 3-step implementation plan and ask the Manager for explicit 'Approved' before writing code." But it does NOT mandate a `brain_turn` planning call. The Hands can self-approve a 3-step plan and implement without ever calling the Brain. The Planning Gate ("no implementation without an approved plan") is stated but the direct-input path bypasses it by letting the Hands write its own plan.
- **Root cause (Brain side):** The Brain's system prompt (assembled from fragments) does not enforce a "context before plan" rule. When the Hands sends a `brain_turn` with a task description but no `context_paths`, the Brain may plan from assumptions instead of returning a `missing_context` or discovery task. The Discovery-fed planning section exists but is not triggered by direct Manager input because the Hands never calls `brain_turn` in the first place.
- **The two gates that must be non-skippable:**
  1. **Plan gate (Hands → Brain):** On direct Manager input, the Hands MUST call `brain_turn` for planning BEFORE writing any code. The Hands' own 3-step plan is a draft for the Manager, not a substitute for a Brain plan. The Brain's plan (or a discovery task) must arrive before implementation.
  2. **Context gate (Brain → Hands):** When the Brain receives a `brain_turn` with no `context_paths` (or insufficient context), it MUST return a `missing_context` or a discovery task, NOT a plan. The Hands must feed the context back before a plan can arrive.
- **This is the same class of defect as Task 415** (context map before brain calls) but on the direct-input path instead of the XML-task path. Task 415 covers `brain_turn` sites in the executor and 09 templates; this task covers the Direct Input Validation Protocol and the Brain's context-before-plan rule.
- **HQ-only:** Changes to `agents/cognitive-executor.md` (Direct Input section), `agents/cognitive-discovery.md`, and `prompts/fragments/` (05-user_input_processing, 08-agentic_reasoning, 09-hands_protocols if needed). Must not leak into project-agnostic governance scaffolding unless the rule is project-agnostic.
- **Related:** Task 414 (enhance fragments/agents), Task 415 (context map before brain calls), research report `context-reports/agent-harness-system-prompts-research.md`.

## Local TODOs

- [ ] Audit the Direct Input Validation Protocol in `agents/cognitive-executor.md` — identify where the Hands can self-approve a plan and skip `brain_turn`
- [ ] Add a hard gate: on direct Manager input, the Hands MUST call `brain_turn` for planning before writing code; the Hands' 3-step plan is a draft, not a substitute
- [ ] Add a hard gate: the Brain MUST NOT produce a plan without `context_paths` (or a discovery task); return `missing_context` or discovery task instead
- [ ] Update `prompts/fragments/05-user_input_processing.md` (Input Validation Pipeline) to route direct Manager input through `brain_turn` planning, not self-approved plans
- [ ] Update `prompts/fragments/08-agentic_reasoning.md` to include "context before plan" as a mandatory reasoning step
- [ ] Update `agents/cognitive-discovery.md` to ensure the discovery subagent is invoked when the Brain needs context (not skipped)
- [ ] Add a verification gate: grep for the new mandatory `brain_turn` planning call in the Direct Input section
- [ ] Update sibling `README.md` and append dated ADR to `DECISIONS.md` where domain contracts changed
- [ ] Update CHANGELOG.md via Parse-Then-Append

## Acceptance Criteria

- [ ] The Direct Input Validation Protocol in `agents/cognitive-executor.md` mandates a `brain_turn` planning call before implementation on ad-hoc Manager input
- [ ] The Hands' 3-step plan is explicitly labeled as a draft for Manager approval, not a substitute for a Brain plan
- [ ] The Brain (via fragments) returns `missing_context` or a discovery task when `context_paths` is absent, rather than producing a plan from assumptions
- [ ] `prompts/fragments/05-user_input_processing.md` routes direct Manager input through `brain_turn` planning
- [ ] `prompts/fragments/08-agentic_reasoning.md` includes "context before plan" as a mandatory reasoning step
- [ ] `lint_task_file` passes on this task file
- [ ] `npx prettier --write "**/*.md"` applied to changed Markdown
- [ ] Sibling `README.md` and `DECISIONS.md` updated where domain contracts changed
- [ ] CHANGELOG.md updated via Parse-Then-Append

## Verification Evidence

- **Test command:** rtk test npx prettier --check "**/*.md"
- **Expected result:** exit 0, no formatting errors
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Making the plan gate non-skippable on direct input adds latency to simple requests ("fix a typo"). Mitigation: define a "trivial change" exemption where the Manager's words are already the plan AND the change is single-file with known paths — but even then, the Hands must still feed context (file path + line range) to the Brain via `brain_turn` before implementing.
- **Risk:** The Brain's context-before-plan rule must not break existing XML task flows where context is already fed. The rule should only trigger when `context_paths` is absent or empty.
- **Risk:** HQ-only changes (agents/, prompts/fragments/) must not leak into project-agnostic governance scaffolding unless the rule is project-agnostic (it is, since it applies to all projects using the harness).
- **Rollback plan:** Git revert of changed agent/fragment files. No data migration involved.

> **Superseded:** This task was bundled into META task `417-comprehensive-prompt-and-workflow-hardening-across-fragments-agents-and-brain-context` and archived on 2026-11-22 20:56 UTC. See `tasks/backlog/417-comprehensive-prompt-and-workflow-hardening-across-fragments-agents-and-brain-context.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/416-enforce-plan-before-implementation-and-context-before-brain.md`.

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
