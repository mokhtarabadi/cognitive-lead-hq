---
name: testing-verification
description: TDD test ordering with coverage gates plus mandatory fresh verification evidence before any completion claim.
---

# Testing & Verification Meta Skill

Meta skill combining **testing-strategy** (TDD order, coverage gates, placement) and **verification-before-completion** (fresh-evidence gate). Load one skill for both: write tests with the code, then prove it with the gate. Sections are verbatim from the source skills.

---

## Part 1: Testing-Strategy Skill — TDD Enforcement (from `testing-strategy`)

## Purpose

Turn "write tests too" from a wish into a gate. Every implementation task ships tests FIRST or WITH the code, never after. Research basis: TDD prompting alone raised regressions when agents lacked test context (TDAD, arXiv:2603.17973) — so this skill gives targeted test placement + coverage bars, not lectures. Half of agentic code PRs ship zero tests and error paths miss 81–86% coverage (arXiv:2607.18057) — so error-path tests are mandatory, not optional.

## Test-First Order (Red-Green-Refactor, Mandatory)

1. **RED:** write the failing test first, run it, watch it fail for the right reason. No implementation code exists yet.
2. **GREEN:** write the minimal implementation that turns the test green. Nothing more.
3. **REFACTOR:** clean up with tests green; re-run after every edit.
4. A task that changes behavior with no test change is REJECTED at QA — no exceptions except the trivial-change exemption below.

## Coverage Gates

- **Diff coverage:** every changed line of behavior code must be executed by at least one new or updated test. Untested changed lines block the task.
- **Error paths:** every new `raise` / error return / exception handler needs a test that triggers it. Happy-path-only suites fail the gate.
- **One assertion focus:** one behavior per test; name tests `test_<unit>_<condition>_<expectation>`. Multi-assertion mega-tests are a smell — split them.

## Test-Placement Map (No Guessing)

- Locate the project's existing test layout first (`tests/`, `test/`, `__tests__`, colocated `*.test.*`). New tests go where the project already puts them.
- Mirror the source path: `src/users/service.py` → `tests/users/test_service.py`. Never invent a parallel layout.
- If no test layout exists, create `tests/` at the repo root and record the choice in the task file.

## Trivial-Change Exemption

Trivial single-file changes with zero behavior delta (typo fixes, comment-only, pure renames proven by the suite) may skip NEW tests — but the existing suite must still run green. The exemption is logged in the task file with one line. Anything touching logic, money, auth, or migrations never qualifies.

## Verification Contract

- Run the project's test command BEFORE claiming done — see the active stack skill's **Strict Tooling Gate** section for the exact `test` step and its prerequisites (format, lint, typecheck, and security must pass first).
- Failing tests are fixed in code, never deleted or weakened to pass. A deleted failing test is a QA rejection.

---

## Part 2: Verification Before Completion (from `verification-before-completion`)

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
