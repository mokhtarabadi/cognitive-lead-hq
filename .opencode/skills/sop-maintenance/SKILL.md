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
