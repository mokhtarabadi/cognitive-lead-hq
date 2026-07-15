# Task: Rebrand project with solid name, metadata, polished README, and SEO

**File:** `tasks/36-rebrand-project-metadata-readme-seo.md`
**Type:** improvement
**Status:** open

## Original GitHub Issue

**Issue #2** — Rebrand project: solid name, metadata, polished README, and SEO

### Summary

Rebrand the project with a solid name, complete metadata, polished README, and SEO optimizations to improve discoverability.

### Tasks

#### 1. Choose a Solid Project Name
The current name `best-prompts` is generic and doesn't reflect the project's identity as the Cognitive Lead AI multi-agent system HQ. Rename to something that matches the internal branding.

#### 2. Complete Repository Description
Add a clear, keyword-rich description to the GitHub repo.

#### 3. Add Repository Topics/Tags
Add relevant GitHub topics for discoverability (e.g., `opencode`, `ai-agent`, `multi-agent-system`, `system-prompt`, `mcp-server`, `agent-skills`, `cognitive-ai`).

#### 4. Polish the README
- Modern layout with badges, clearer sections, visual hierarchy
- SEO-friendly metadata and introductions
- Consistent tone and branding

#### 5. SEO & Discoverability
- Ensure the README includes relevant keywords naturally
- Add social preview / OpenGraph image
- Optimize for "opencode setup", "multi-agent system prompt", "AI agent skills" searches

---

## Refactored Prompt

```markdown
<role>
You are a Senior Open-Source Brand Strategist and Technical README Architect with expertise in GitHub SEO, repository discoverability, and developer-first branding.
</role>

<system_context>
You are operating inside the Cognitive Lead AI multi-agent system HQ repository. The repo is currently named `best-prompts` but functions as a centralized hub for system prompts, MCP server configurations, and Agent Skill templates. The target audience is AI engineers, OpenCode users, and multi-agent system builders. The branding must reflect authority, structure, and cognitive AI specialization.
</system_context>

<agentic_reasoning>
Before executing any change, you MUST output a <reasoning_log> that:
1. Analyzes the current repo name `best-prompts` against the actual repo content (system prompts, MCP servers, skills) — does the name cause a discoverability mismatch?
2. Evaluates 3-5 candidate names for: memorability, keyword relevance, alignment with "Cognitive Lead AI" branding, and GitHub search ranking potential.
3. Checks the existing README structure against Top 20 most-starred AI agent repos on GitHub to identify missing sections (badges, quickstart, architecture diagram, etc.).
4. Assesses whether GitHub topics can be set via `gh repo edit` and which 8-10 topics maximize cross-listing with related projects.
</agentic_reasoning>

<execution_rules>
- You MUST NOT rename the repo without verifying that all internal references (AGENTS.md, docs/, git remote URLs) are updated atomically.
- You MUST preserve the existing `CHANGELOG.md` format and add a formal entry for the rebranding.
- You MUST ensure README badges use shields.io with flat-square style for consistency.
- You MUST include a `## Quick Start` section that takes <30 seconds to read.
- You MUST NOT remove or weaken the existing `AGENTS.md` guardrails — the rebrand is additive, not destructive.
- You MUST update the repo description via `gh repo edit --description "..."` as part of this task.
</execution_rules>

<output_format>
Provide a report structured as:
1. **Proposed Name**: with rationale and SEO scoring
2. **Description**: exact string to set via `gh repo edit`
3. **Topics**: comma-separated list
4. **README Sections**: ordered list of sections in the new README
5. **Diff Summary**: files changed and the nature of each change
</output_format>
```

## Acceptance Criteria

- [ ] Repo name finalized and updated
- [ ] Description written and set on GitHub
- [ ] GitHub topics/tags added
- [ ] README polished with badges and clean structure
- [ ] SEO basics covered (description, topics, OpenGraph if possible)

## Local TODOs

- [ ] Initial codebase exploration — read current README, AGENTS.md, CHANGELOG.md
- [ ] Research and propose new repo name
- [ ] Update repo name via `gh repo rename`
- [ ] Write and set repo description via `gh repo edit --description "..."`
- [ ] Add GitHub topics via `gh repo edit --add-topic "..."`
- [ ] Polish README with badges, quickstart, architecture overview
- [ ] Update CHANGELOG.md with rebranding entry
- [ ] Update all internal references to old repo name

## OpenCode Execution Log & Reasoning

_(OpenCode: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
