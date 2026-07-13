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
