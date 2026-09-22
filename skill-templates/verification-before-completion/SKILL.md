---
name: verification-before-completion
description: Mandatory rule before claiming any task is complete, fixed, or passing.
---

# Verification Before Completion

## The Iron Law

NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.
Claiming a task is complete without running tests/linters and seeing the output is a hallucination.

## The Gate Function (MANDATORY)

BEFORE claiming success or moving to the <summary_phase>:

1. IDENTIFY: What command proves this code works? (e.g., `npm test`, `cargo build`, `pytest`).
2. RUN: Execute the command in the terminal.
3. READ: Read the full output.
4. VERIFY: Does the output explicitly confirm success?
   - If NO: Fix the code and re-run.
   - If YES: You may now proceed.

## Strict Tooling Gate (MANDATORY — Forced Strict Mode)

Every completion claim must pass the active stack skill's **Strict Tooling Gate** before `lint_task_file` and before any QA transition. The gate is machine-enforced, not advisory.

1. LOAD the single stack skill from `<agent_skills_registry>` that matches the project's language and framework. If none matches, the gate is the repo's base `rtk test` suite plus `lint_task_file`.
2. EXECUTE that skill's **Strict Tooling Gate** section in fail-fast order: format → lint → typecheck → static analysis → security → test → build. Stop on the first non-zero exit.
3. RECORD the exact gate command, its output excerpt, and exit code `0` in `## Verification Evidence`. A completion claim without this evidence is a hallucination and is REJECTED at QA.
