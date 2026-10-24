---
name: sop-maintenance
description: Rules for modifying the Cognitive Lead AI SOP repository
---

# OpenCode Rules for This Repository

This file defines the rules that AI agents (OpenCode) must follow when modifying _this_ SOP repository.

## General Rules

1. **All documentation must be written in Markdown (`.md`).** No other formats are permitted.
2. **Every stack document must include the following four sections**, in this order:
   - **Project Structure** — Recommended directory layout and file organization.
   - **Naming Conventions** — File, class, function, variable, and route naming standards.
   - **Architectural Patterns** — The recommended architecture (e.g., layered, DDD, MVVM) and how to enforce it.
   - **Testing Strategies** — Unit, integration, and end-to-end test structure, frameworks, and naming.
3. **`CHANGELOG.md` must be updated** whenever the system prompt (`system-prompt.md`) or any stack rule document is modified. Follow the Keep a Changelog format.
4. **No code generation outside of documentation.** This repository contains SOPs only — do not generate application code.
5. **Keep language neutral where possible**, but include framework-specific examples when they clarify a rule.
6. **All files must be validated** to ensure markdown formatting is correct before marking a task complete.

## Documentation Sync Rules

When modifying this repository, you must keep these files synchronized:

1. **Active task file** in `tasks/` — agents must read the active task file for context and update it with final status, technical changes, and architectural reasoning upon completion.
2. **`DESIGN.md`** — if UI/UX changes are involved, consult and enforce the design spec. Include `DESIGN.md` updates in the documentation phase.
3. **`CHANGELOG.md`** — must be updated whenever `system-prompt.md` or any structural file is modified.
4. **No global state** — do not rely on legacy `STATE.md` or `TODO.md` files. All work tracking is decentralized to `tasks/`.
