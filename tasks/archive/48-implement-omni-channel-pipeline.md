# Task 48: Implement Omni-Channel Bilingual Prompt Pipeline

**File:** `tasks/in-progress/48-implement-omni-channel-pipeline.md`
**Type:** feature
**Status:** closed

## Goal

Upgrade to V6.2.0 by embedding the Automated Prompt Refactoring Pipeline as an omni-channel bilingual (Farsi-to-English) translation and expansion layer across AI Studio (system-prompt.md), OpenCode (AGENTS.md + prompt-refactor skill), and Telegram syncs.

## Manager's Notes

- Replace the `<user_input_processing>` block in system-prompt.md with a 4-step Bilingual Translation & Intent Expansion protocol.
- Add bilingual guardrails to AGENTS.md and the audit-agents template and audit criteria.
- Update the prompt-refactor skill with translation as a first step.
- Update telegram-issue-sync Phase 3 Step 3 to use prompt-refactor as the omni-channel filter.
- Strike roadmap item #5 as implemented.

## Local TODOs

- [x] Step 1: Scaffold task file
- [x] Step 2: Update `system-prompt.md` — bump version to 6.2.0 + replace `<user_input_processing>`
- [x] Step 3: Update `prompt-refactor` skill — add bilingual translation as Step 1
- [x] Step 4: Update `AGENTS.md` + `audit-agents` skill — add Farsi guardrail
- [x] Step 5: Update `telegram-issue-sync` skill — omni-channel filter in Phase 3 Step 3
- [x] Step 6: Strike roadmap item #5 in `README.md`
- [x] Step 7: Update `CHANGELOG.md` for [6.2.0]
- [x] Run `npx prettier --write "**/*.md"`

## OpenCode Execution Log & Reasoning

**Architectural Reasoning:** This upgrade embeds the Automated Prompt Refactoring Pipeline as an omni-channel bilingual layer across the entire system. The key architectural insight is that the Manager frequently inputs raw Farsi text, which the AI Studio Brain previously processed with basic spell-checking. By replacing `<user_input_processing>` with a formal 4-step Bilingual Translation → Intent Expansion → Clarification → Seamless Routing protocol, the Brain can now autonomously handle Farsi inputs with professional-grade translation. The pipeline is reinforced at every layer: (1) the prompt-refactor skill was given bilingual translation as its first workflow step, (2) AGENTS.md and the audit-agents skill now enforce a Farsi guardrail, (3) the Telegram sync skill explicitly documents its Phase 3 Step 3 as the omni-channel filter for translating RAW_TEXT through prompt-refactor.

**Files Modified:**

1. **`system-prompt.md`** — `<system_version>` bumped to 6.2.0. `<user_input_processing>` replaced with 4-step Automated Refactoring Pipeline.
2. **`skill-templates/prompt-refactor/SKILL.md`** — Workflow Step 1 changed to "Bilingual Translation & Analysis".
3. **`AGENTS.md`** — New guardrail: don't execute raw/Farsi prompts directly; load `prompt-refactor` skill first.
4. **`skill-templates/audit-agents/SKILL.md`** — New guardrail in template + new audit criterion for Bilingual Prompt Refactoring.
5. **`skill-templates/telegram-issue-sync/SKILL.md`** — Phase 3 Step 3 updated to "Omni-Channel Filter" with explicit Farsi translation mention.
6. **`README.md`** — Roadmap item #5 struck through and marked implemented in V6.2.0.
7. **`CHANGELOG.md`** — [6.2.0] release notes added.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

**Factual Git Diff:** Stored in Commit Hash: `e400c001c03159af0867fed08a95aff9cbfd73ea`
<!-- END_GIT_DIFF -->
