# Task: Integrate Multi-Agent Brainstorming Protocol

**File:** `tasks/completed/56-integrate-multi-agent-brainstorming-protocol.md`
**Type:** improvement
**Status:** closed

## Goal

Integrate the Multi-Agent Brainstorming Protocol into system-prompt.md, AGENTS.md, and create the standalone user prompt.

## Manager's Notes

- Version bump from 6.5.0 to 6.6.0 (current file is already at 6.6.0)
- Six expert personas: system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker
- XML-tagged output schema for brainstorming sessions

## Local TODOs

- [x] Step 1: Initialize the task file in tasks/in-progress/
- [x] Step 2: Update system-prompt.md — add brainstorm-swarm to registry, add brainstorming rule to user_input_processing, add brainstorming_protocol section
- [x] Step 3: Update AGENTS.md — add brainstorming guardrail directive
- [x] Step 4: Create user-prompts/multi-agent-brainstorming.md standalone prompt
- [x] Step 5: Update CHANGELOG.md for v6.6.0
- [x] Step 6: Run prettier formatting on all modified files
- [x] Step 7: Verify syntax and state
- [x] Step 8: Create skill-templates/brainstorm-swarm/SKILL.md
- [x] Step 9: Re-format system-prompt.md with clean XML indents
- [x] Step 10: Sync skill-templates/audit-agents/SKILL.md with brainstorming criteria

## OpenCode Execution Log & Reasoning

**Architectural reasoning:**
The Multi-Agent Brainstorming Protocol extends the system with a cross-disciplinary reasoning layer activated before the standard Plan & Review loop. The six personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) cover orthogonal domains to ensure no blind spots remain when the Manager presents ambiguous or multi-faceted problems. The protocol is modeled as a Phase 1.5 hook in the execution workflow — inserted between Input Processing (Phase 1) and Plan & Review (Phase 2) — so it fires exactly when ambiguity is detected but before architectural design begins.

**Files modified:**

1. `system-prompt.md` — Added `brainstorm-swarm` to `<agent_skills_registry>`, new Step 3 (Brainstorming Trigger) in `<user_input_processing>` (renumbering old step 3→4, 4→5), added full `<brainstorming_protocol>` section with 6 personas and XML output schema.
2. `AGENTS.md` — Added brainstorming guardrail directive in Actionable Guardrails section.
3. `user-prompts/multi-agent-brainstorming.md` — New standalone user prompt with full XML-tagged template, personas, constraints, output schema, and usage instructions.
4. `CHANGELOG.md` — Added `[6.6.0]` section with Added and Changed categories.
5. `tasks/in-progress/56-integrate-multi-agent-brainstorming-protocol.md` — This file, tracking the task.

**Corrective phase additions (Round 2):** 6. `skill-templates/brainstorm-swarm/SKILL.md` — New skill template defining the multi-expert swarm: 6 personas, execution rules, independent analysis protocol, conflict resolution, and backlog interpretation guidelines. 7. `system-prompt.md` — `<brainstorming_protocol>` block reformatted with clean 2-space nested indentation for all internal tags (`<phase>`, `<trigger>`, `<workflow>`, `<personas>`, `<persona>`, `<focus>`, `<output>`, `<output_schema>`). 8. `skill-templates/audit-agents/SKILL.md` — Updated both Target Audit Criteria sections (Mode 1 and Mode 2) with combined "Bilingual Prompt Refactoring & Brainstorming Protocol" criterion. Added brainstorming guardrail directive to the AGENTS.md template's Actionable Guardrails section.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `53c365798f8b168ab869f566b61e7a58b9d3fd51`
<!-- END_GIT_DIFF -->
