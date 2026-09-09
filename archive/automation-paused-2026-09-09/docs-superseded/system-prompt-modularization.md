# System Prompt Modularization Assessment

**Version:** V9.0.0 Proposal
**Date:** 2026-08-03
**Status:** Assessment Draft

> **Status (Task 99):** This assessment is being **superseded** by the
> modularization implementation in [`tasks/qa/99-modularize-system-prompt-shared-validation-phase.md`](../tasks/qa/99-modularize-system-prompt-shared-validation-phase.md).
> The `system-prompt.md` is now split into `prompts/fragments/` (20 per-tag
> fragment files) + `prompts/shared/validation-phase.md` (the shared
> `<validation_phase>` partial), assembled via
> `scripts/prompt-build/assemble_system_prompt.py`, with sync verification via
> `lint_system_prompt_sync()` in the lint MCP server. The token estimates in
> this document are outdated; a full rewrite with corrected figures is a
> separate follow-up docs task. See `prompts/README.md` for the current
> authoring workflow.

## Executive Summary

The current `system-prompt.md` (7.4.2) is a 479-line monolithic file containing 12 distinct functional sections. This document analyzes the current structure, identifies duplicated rules across files, proposes a modular directory architecture, and estimates the token savings and maintenance benefits of modularization.

---

## 1. Current Section Mapping

| #   | Section                              | Lines       | Purpose                                                                        | Token Est. |
| --- | ------------------------------------ | ----------- | ------------------------------------------------------------------------------ | ---------- |
| 1   | `<system_version>`                   | 1           | Version tracking                                                               | ~10        |
| 2   | `<role>`                             | 7           | Core identity and capabilities                                                 | ~80        |
| 3   | `<system_context>`                   | 3           | Knowledge cutoff, time awareness                                               | ~30        |
| 4   | `<manager_profile>`                  | 10          | User persona, background, coaching needs                                       | ~120       |
| 5   | `<leadership_and_language_protocol>` | 5           | English tutoring, vocabulary, sprint retrospectives                            | ~180       |
| 6   | `<agent_skills_registry>`            | 37          | Available skills listing (global + stack-specific)                             | ~400       |
| 7   | `<user_input_processing>`            | 22          | Farsi translation pipeline, validation, enrichment                             | ~250       |
| 8   | `<personas>`                         | 37          | 6 persona definitions (Architect, Designer, Programmer, Planner, QA, Reviewer) | ~800       |
| 9   | `<agentic_reasoning>`                | 47          | 10-step reasoning framework                                                    | ~500       |
| 10  | `<hands_protocols>`                  | 159         | 3 XML task templates (discovery, implementation, combined)                     | ~1800      |
| 11  | `<execution_workflow>`               | 18          | 9-step workflow phases                                                         | ~200       |
| 12  | `<brainstorming_protocol>`           | 53          | 6-persona brainstorming session schema                                         | ~600       |
| 13  | `<constraints>`                      | 14          | Global rules and guardrails                                                    | ~350       |
| 14  | `<solid_programming_mandate>`        | (truncated) | SOLID principles enforcement                                                   | ~200       |

**Estimated Total:** ~4,520 tokens

---

## 2. Duplicated Rules Analysis

### 2.1 Validation Phase Duplication

The `<validation_phase>` block appears **three times** identically in:

- `<hands_discovery_task_template>` (lines 190-197)
- `<hands_implementation_task_template>` (lines 230-237)
- `<hands_combined_task_template>` (lines 306-312)

**Impact:** ~80 tokens duplicated 3x = ~160 wasted tokens per prompt load.

**Recommendation:** Extract to a shared `prompts/shared/validation-phase.md` partial.

### 2.2 AGENTS.md ↔ system-prompt.md Overlap

| Rule                                               | AGENTS.md                       | system-prompt.md               | Status                                                                   |
| -------------------------------------------------- | ------------------------------- | ------------------------------ | ------------------------------------------------------------------------ |
| "Read AGENTS.md first"                             | Line 5-6 (Mandatory First-Read) | `<validation_phase>` step 1    | **Duplicated**                                                           |
| "Don't edit system-prompt.md without version bump" | Line 27-28                      | Not in system prompt           | **AGENTS.md only** (correct)                                             |
| "Don't execute git commands autonomously"          | Line 35-36                      | `<bash_phase>` CRITICAL RULE 2 | **Duplicated**                                                           |
| "Skill loading rules"                              | Line 66-71                      | `<agent_skills_registry>`      | **Complementary** (AGENTS.md has enforcement, system-prompt has listing) |
| "Context bootstrapping"                            | Line 73-75                      | `<context_phase>`              | **Duplicated**                                                           |

**Impact:** ~120 tokens of direct duplication.

**Recommendation:** system-prompt.md should reference AGENTS.md rules rather than restate them. Use `→ See AGENTS.md § Section Name` cross-references.

### 2.3 Skill ↔ Persona Behavior Overlap

The `Senior Programmer` persona (line 111-116) contains detailed instructions about:

- Loading AGENTS.md first
- Loading project-memory skill
- Anti-Hack Directive
- Multi-Phase Task Rule

Some of these are also covered in:

- `<agent_skills_registry>` (skill listing)
- `<constraints>` (workspace security, documentation rules)
- `<execution_workflow>` step 4

**Impact:** ~200 tokens of semantic overlap.

**Recommendation:** Persona `<behavior>` blocks should focus on **decision-making heuristics**, not operational mechanics. Move operational rules to `<constraints>` or `<execution_workflow>`.

---

## 3. Proposed Modular Directory Structure

```
prompts/
├── core/
│   ├── role.md                    # <role> + <system_context>
│   ├── constraints.md             # <constraints> + <solid_programming_mandate>
│   └── agentic-reasoning.md       # <agentic_reasoning>
├── personas/
│   ├── software-architect.md
│   ├── ui-ux-designer.md
│   ├── senior-programmer.md
│   ├── project-planner.md
│   ├── qa-engineer.md
│   └── code-reviewer.md
├── workflows/
│   ├── execution-workflow.md      # <execution_workflow>
│   ├── user-input-processing.md   # <user_input_processing>
│   ├── brainstorming-protocol.md  # <brainstorming_protocol>
│   └── leadership-protocol.md     # <leadership_and_language_protocol>
├── templates/
│   ├── opencode-discovery.md      # Discovery task XML template
│   ├── opencode-implementation.md # Implementation task XML template
│   ├── opencode-combined.md       # Combined task XML template
│   └── shared/
│       ├── validation-phase.md    # Shared validation phase block
│       └── summary-phase.md       # Shared summary phase block
├── registry/
│   ├── agent-skills.md            # <agent_skills_registry>
│   └── manager-profile.md         # <manager_profile>
└── system-prompt.md               # Root assembler (imports all partials)
```

### 3.1 Assembly Model

The root `system-prompt.md` becomes a thin orchestrator:

```markdown
<system_version>9.0.0</system_version>

<!-- CORE -->

{{> core/role.md}}
{{> core/constraints.md}}
{{> core/agentic-reasoning.md}}

<!-- REGISTRY -->

{{> registry/manager-profile.md}}
{{> registry/agent-skills.md}}

<!-- WORKFLOWS -->

{{> workflows/user-input-processing.md}}
{{> workflows/execution-workflow.md}}
{{> workflows/leadership-protocol.md}}
{{> workflows/brainstorming-protocol.md}}

<!-- PERSONAS (loaded dynamically by Orchestrator) -->

{{> personas/*}}

<!-- TEMPLATES (loaded on-demand by OpenCode) -->

{{> templates/*}}
```

**Key Design Decision:** Personas and templates are **not** loaded into every Orchestrator session. They are injected only when the relevant persona is activated. This is the single biggest token optimization.

---

## 4. Token Savings Estimate

### 4.1 Current State

| Component                            | Tokens     |
| ------------------------------------ | ---------- |
| Full system-prompt.md (Orchestrator) | ~4,520     |
| Full system-prompt.md (OpenCode)     | ~4,520     |
| Per-session overhead                 | **~9,040** |

### 4.2 Modularized State (Estimated)

| Component                             | Tokens     | Notes                         |
| ------------------------------------- | ---------- | ----------------------------- |
| Core (role + constraints + reasoning) | ~930       | Always loaded                 |
| Registry (skills + manager)           | ~520       | Always loaded                 |
| Active workflow (1 of 4)              | ~250       | Loaded per task type          |
| Active persona (1 of 6)               | ~150       | Loaded per persona activation |
| Active template (1 of 3)              | ~300       | Loaded per OpenCode task      |
| **Per-session total**                 | **~2,150** |                               |

### 4.3 Savings

| Metric                                  | Before | After  | Savings                |
| --------------------------------------- | ------ | ------ | ---------------------- |
| Tokens per Orchestrator session         | ~4,520 | ~1,600 | **65%**                |
| Tokens per OpenCode session             | ~4,520 | ~2,150 | **52%**                |
| Monthly token cost (est. 1000 sessions) | ~9M    | ~3.7M  | **~5.3M tokens/month** |

---

## 5. Maintenance Benefits

### 5.1 Single Responsibility

Each file owns one concern. Modifying persona behavior only touches `personas/*.md`. Adding a new constraint only touches `core/constraints.md`.

### 5.2 Parallel Editing

Multiple Orchestrator instances can modify different personas simultaneously without merge conflicts.

### 5.3 Version Granularity

Individual partials can be versioned independently. A persona tweak doesn't bump the system version.

### 5.4 Testing

Each partial can be lint-tested independently for structural validity.

### 5.5 Onboarding

New contributors can read one file at a time instead of a 500-line monolith.

---

## 6. Migration Risks

| Risk                              | Severity | Mitigation                                                                                                   |
| --------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| Partial loading failures          | High     | Root `system-prompt.md` includes fallback: if partial missing, log warning and continue with reduced context |
| Cross-reference breakage          | Medium   | Enforce `→ See <file> § <section>` convention; lint for broken refs                                          |
| Orchestrator prompt assembly bugs | High     | Implement `prompt-assembler` MCP tool that validates all partials resolve before injection                   |
| Token counting drift              | Low      | CI check: count tokens in assembled prompt, fail if >5000                                                    |

---

## 7. Recommended Implementation Order

1. **Phase 1:** Extract `<validation_phase>` and `<summary_phase>` as shared partials (immediate ~160 token savings, zero risk)
2. **Phase 2:** Extract `<personas>` into individual files (biggest token win — load only active persona)
3. **Phase 3:** Extract `<hands_protocols>` templates into separate files
4. **Phase 4:** Refactor root `system-prompt.md` into assembly model
5. **Phase 5:** Add `prompt-assembler` MCP tool with validation

---

## 8. Conclusion

The current monolithic `system-prompt.md` is functional but token-inefficient and maintenance-heavy. Modularization can reduce per-session token usage by 50-65% while improving maintainability. The migration can be phased to minimize risk, with immediate wins available from simply extracting shared template blocks.

The recommended target for V9.0.0 is to complete Phases 1-3, achieving ~40% token savings with minimal architectural change.
