# Task 69: Add Project License

**File:** `tasks/backlog/69-add-project-license.md`
**Source:** manager
**Type:** feature
**Status:** completed

## Goal

Add a LICENSE file to the repository. The README already has a badge referencing `LICENSE` but no file exists. Determine the best license for this project and create the file.

## Manager's Notes

- This is a **documentation-only** repository: system prompts, MCP servers, Agent Skills (SKILL.md), and Markdown templates.
- The project is open-source on GitHub (mokhtarabadi/cognitive-lead-hq) and encourages community contributions (PRs welcome badge).
- No functional application code is shipped — only structured framework-specific SOPs and reusable Markdown templates.
- The best license should be **permissive** to maximize adoption while protecting against liability.

### Recommended License: MIT

**Rationale:**
- MIT is the most widely adopted permissive license for open-source documentation/framework projects.
- It allows unrestricted reuse, modification, and distribution — ideal for a template/SOP repository.
- It includes the standard liability and warranty disclaimer.
- It aligns with the project's "PRs welcome" and community-driven ethos.
- Alternatives considered:
  - **Apache 2.0**: Heavier, includes patent grant — overkill for a docs-only repo.
  - **BSD 2-Clause**: Nearly identical to MIT but less recognized.
  - **CC BY-SA 4.0**: Designed for creative works, not ideal for code-adjacent repositories.
  - **GPL**: Too restrictive for a framework/template repository.

## Local TODOs

- [ ] Create `LICENSE` file in project root with MIT license text
- [ ] Verify the copyright holder matches the GitHub owner (mokhtarabadi)
- [ ] Ensure README badge still resolves correctly

---

## OpenCode Execution Log & Reasoning

**Decision:** MIT License selected — the most widely adopted permissive license for open-source documentation and framework repositories. It permits unrestricted reuse, modification, and distribution, which aligns with the project's community-driven, PR-welcome posture.

**Files created:**
- `LICENSE` — Standard MIT license text with copyright holder `mokhtarabadi` (matching GitHub owner) and year 2026.

**Verification:**
- README badge on line 4 already references `LICENSE` — will resolve correctly now.
- No code is shipped, only documentation, prompts, and templates — MIT is appropriate without patent grant concerns.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
