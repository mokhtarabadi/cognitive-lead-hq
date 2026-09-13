---
name: testing-strategy
description: Enforce Test-Driven Development order and coverage gates so OpenCode writes tests before or alongside implementation code.
---

# Testing-Strategy Skill — TDD Enforcement

## Purpose

Turn "write tests too" from a wish into a gate. Every implementation task ships tests FIRST or WITH the code, never after. Research basis: TDD prompting alone raised regressions when agents lacked test context (TDAD, arXiv:2603.17973) — so this skill gives targeted test placement + coverage bars, not lectures. Half of agentic code PRs ship zero tests and error paths miss 81–86% coverage (arXiv:2607.18057) — so error-path tests are mandatory, not optional.

## Test-First Order (Red-Green-Refactor, Mandatory)

1. **RED:** write the failing test first, run it, watch it fail for the right reason. No implementation code exists yet.
2. **GREEN:** write the minimal implementation that turns the test green. Nothing more.
3. **REFACTOR:** clean up with tests green; re-run after every edit.
4. A task that changes behavior with no test change is REJECTED at QA — no exceptions except the Lite exemption below.

## Coverage Gates

- **Diff coverage:** every changed line of behavior code must be executed by at least one new or updated test. Untested changed lines block the task.
- **Error paths:** every new `raise` / error return / exception handler needs a test that triggers it. Happy-path-only suites fail the gate.
- **One assertion focus:** one behavior per test; name tests `test_<unit>_<condition>_<expectation>`. Multi-assertion mega-tests are a smell — split them.

## Test-Placement Map (No Guessing)

- Locate the project's existing test layout first (`tests/`, `test/`, `__tests__`, colocated `*.test.*`). New tests go where the project already puts them.
- Mirror the source path: `src/users/service.py` → `tests/users/test_service.py`. Never invent a parallel layout.
- If no test layout exists, create `tests/` at the repo root and record the choice in the task file.

## Lite-Mode Exemption

Trivial single-file changes with zero behavior delta (typo fixes, comment-only, pure renames proven by the suite) may skip NEW tests — but the existing suite must still run green. The exemption is logged in the task file with one line. Anything touching logic, money, auth, or migrations never qualifies.

## Verification Contract

- Run the project's test command BEFORE claiming done (see each stack's `toolchain.test_cmd`).
- Failing tests are fixed in code, never deleted or weakened to pass. A deleted failing test is a QA rejection.
