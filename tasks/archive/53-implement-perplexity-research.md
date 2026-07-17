# Task: Implement Perplexity Deep Research Workflow

**File:** `tasks/completed/53-implement-perplexity-research.md`
**Type:** improvement
**Status:** closed

## Goal

Integrate the Perplexity Deep Research 3-Step Framework into the Cognitive Lead HQ repository as a reusable user prompt, an Agent Skill, and a system-prompt workflow step.

## Manager's Notes

This is a documentation-only and skill-templates addition. No application code is written.

## Local TODOs

- [x] Create `user-prompts/perplexity-deep-research.md` with the Manager's 3-Step Perplexity Framework
- [x] Create `skill-templates/perplexity-research/SKILL.md` with the deep research workflow
- [x] Update `system-prompt.md` to V6.5.0 — version bump, add skill to registry, insert Step 1.5 in execution workflow
- [x] Update `CHANGELOG.md` with V6.5.0 release entry
- [x] Stage and inject diff via MCP tool

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

The Perplexity Deep Research workflow addresses a fundamental limitation of static-knowledge-cutoff AI agents: they cannot know about post-2025 dependencies, undocumented API changes, or newly released architectural patterns. Rather than forcing the agent to hallucinate or rely on potentially stale training data, we introduce a formal human-in-the-loop bridge:

1. **`user-prompts/perplexity-deep-research.md`** — A copy-paste-ready template the Manager pastes directly into Perplexity. It encodes a 3-Step Search Framework (Broad → Refined → Precise) that forces Perplexity to iterate its `search_web` calls in an intelligent pyramid pattern rather than using its default flat search. The Final Answer Structure ensures the Manager gets back actionable, structured data the agent can consume.

2. **`skill-templates/perplexity-research/SKILL.md`** — The companion Agent Skill that teaches OpenCode _when_ to trigger this loop and _how_ to formulate the exact message block for the Manager. The halt-and-wait pattern prevents the agent from proceeding with incomplete or hallucinated information.

3. **System prompt V6.5.0 changes:**
   - Registered `perplexity-research` in the `<agent_skills_registry>` as a Global Workflow Skill, making the Orchestrator aware of its existence.
   - Inserted Step 1.5 ("Deep Research Loop") in `<execution_workflow>` immediately after input processing, ensuring the Orchestrator checks whether external research is needed before diving into implementation planning.

### Files Modified

- `system-prompt.md` — version bump, skill registry entry, new workflow step
- `CHANGELOG.md` — V6.5.0 release entry

### Files Created

- `user-prompts/perplexity-deep-research.md`
- `skill-templates/perplexity-research/SKILL.md`

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

**Factual Git Diff:** Stored in Commit Hash: `18130d77c3b6351b71ccdf501df90290469252c6`
<!-- END_GIT_DIFF -->
