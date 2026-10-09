# Task 311: Full Stack Coverage — React Arrows, Prisma, ObjC, Config

**File:** `tasks/in-progress/311-stack-coverage-arrows-prisma-objc-config.md`
**Source:** manager
**Type:** feature
**Status:** in-progress

## Goal

Close the four proven extractor gaps so every skill-template stack resolves in the graph: React arrow components in JS/TS files, Prisma models/enums, Objective-C methods, and config/style assets (properties, CSS) — verified by probe-first tests plus a live deploy check.

## Manager's Notes

Manager probe 2026-10-09 proved: `const SignupForm = () =>` missed in TSX, ObjC methods missed, `.prisma`/`.properties`/`.css` invisible. Order: fix and test. QA lane holds 308/309/310 (at cap 3): this task stages in-progress and waits — 308 must close before the 311 QA transition. Builds cumulatively on staged work until prior tasks close.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Arrow components in all JS/TS suffixes plus correct interface/type/enum kinds
- [x] Prisma .prisma models/enums plus .m/.mm ObjC methods
- [x] Collect .properties/.css (.scss/.less) with key/selector nodes
- [x] Probe-backed tests for each gap and pass them
- [x] Deploy global, restart, live verify on the probe stack
- [x] Stage 311 and hold QA until 308 closes

## Acceptance Criteria

- [x] AC1: Arrow function components extract in .js/.jsx/.ts/.tsx
- [x] AC2: Prisma models/enums and ObjC methods extract with correct kinds
- [x] AC3: properties keys and CSS selectors become nodes; files are collected
- [x] AC4: Interface/type/alias nodes carry correct kinds, not func
- [x] AC5: lint_task_file passes, graph tests pass

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest pytest tests/test_mcp_servers.py -q -k graph
- **Expected result:** all 7 graph tests pass
- **Actual result:** 7 passed via RTK; live probe on deployed singleton finds SignupForm via natural words plus ObjC nodes; lint_task_file passes
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Looser patterns over-match (CSS braces, ObjC C functions) and add noise nodes
- **Rollback plan:** Revert new patterns; affected suffixes return to prior behavior

---

## Execution Log & Reasoning

Seat Check: backend Python regex patterns plus tests/docs → Architect kept (node taxonomy), Programmer kept, Designer skipped. Brainstorm: not required — reversible pattern change. QA lane at cap (308/309/310): implement + stage only, no fourth QA entry until 308 closes.

Deployed 2026-10-09 (global IN_SYNC, service active). Live probe on /tmp/opencode/stack-probe via deployed singleton: 16 nodes / 10 links; natural query signup form component seeds SignupForm plus ObjC doSignup; explain SignupForm resolves Component.tsx L5. Remaining gaps (logged, not fixed): Java records, CSS edge-less nodes, parallel-batch timeouts on singleton.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
