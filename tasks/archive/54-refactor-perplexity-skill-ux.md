# Task: Refactor Perplexity Research Skill UX

**File:** `tasks/backlog/54-refactor-perplexity-skill-ux.md`
**Type:** improvement
**Status:** open

## Goal

Improve the Manager UX of the `perplexity-research` skill by embedding the full 3-Step Framework prompt directly in the agent's message block, eliminating the need for the Manager to open and copy from `user-prompts/perplexity-deep-research.md` separately.

## Manager's Notes

Keep `user-prompts/perplexity-deep-research.md` intact for manual use-cases.

## Local TODOs

- [ ] Initial codebase exploration
- [x] Replace SKILL.md with embedded full-prompt UX
- [x] Update CHANGELOG.md under existing V6.5.0 header
- [x] Run prettier
- [x] Stage and inject diff

## OpenCode Execution Log & Reasoning

### Reasoning

The original skill instructed the Manager to open `user-prompts/perplexity-deep-research.md`, copy the framework, append the query, and paste into Perplexity. This created friction — the Manager had to perform a multi-step manual operation.

The refactored skill embeds the **entire 3-Step Framework prompt** directly inside the agent's message block, with `[INSERT YOUR SPECIFIC QUERY HERE]` as the only placeholder. The Manager can now copy the entire block with one click and paste it directly into Perplexity.

This is a pure UX improvement. The standalone `user-prompts/perplexity-deep-research.md` is preserved for cases where the Manager wants to manually craft research prompts outside the agent loop.

### Files Modified
- `skill-templates/perplexity-research/SKILL.md` — complete replacement with embedded full-prompt UX
- `CHANGELOG.md` — added UX improvement entry under V6.5.0

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `5259b3f86620a6d6885b9b5cb3e423cf528824bf`
<!-- END_GIT_DIFF -->
