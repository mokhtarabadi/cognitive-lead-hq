# Task 199: Personas + fintech stack skills deep-research and improvement

**File:** `tasks/completed/199-personas-fintech-skills-deep-research.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Deep-research every persona in the system prompt and every fintech stack skill via the blowsh workflow, then improve personas (precision, boldness, zero hallucination) and stack skills where needed — new personas only when truly justified.

## Manager's Notes

Two-phase work, both via blowsh MCP + blowsh skill deep research. Phase 1 (personas): research each of the seven declared personas (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer) against industry best practice; add a new persona ONLY if research proves a real gap; improve current personas to be more precise, bolder, and fully hallucination-proof. Phase 2 — the more important part (manager's words): research EACH fintech stack skill one by one (android-kotlin, spring-boot, nestjs-prisma-vertical, nextjs, react-vite, react-native-expo, ios-swiftui, python-fastapi, flask-python, go-gin, go-hexagonal-grpc, vue-nuxt) and improve every skill that needs it. Standing authorization: full autopilot + autoclosure — execute without asking, QA + review via brain turns, close autonomously. Seven-seat contract stays in force unless research justifies an eighth seat with manager-visible reasoning.

## Local TODOs

- [x] Blowsh spider research per persona (7 sweeps, industry best practice)
- [x] Improve persona definitions (precision, boldness, anti-hallucination)
- [x] Blowsh spider research per fintech stack skill (12 sweeps)
- [x] Improve stack skills where research shows gaps
- [x] Rebuild + verify + stage + qa + autopilot QA/review + autoclose

## Acceptance Criteria

- [x] Every persona researched with cited sources; improvements traceable to findings
- [x] No new persona added without a written gap justification
- [x] Every fintech stack skill researched; improved skills list what changed and why
- [x] System prompt reassembled SYNC_OK; full suite green; lint passes

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check199.md && diff /tmp/check199.md system-prompt.md && echo SYNC_OK`
- **Expected result:** `SYNC_OK`, zero diff lines
- **Actual result:** SYNC_OK, zero diff lines (80462 bytes, v9.27.0); full suite 201 passed, exit 0
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Persona changes alter Brain behavior broadly; skill edits affect all downstream projects via audit-agents
- **Rollback plan:** Fragments + skills are git-tracked; revert to pre-task hashes, reassemble, re-verify sync

---

## Execution Log & Reasoning

Phase 1 (personas): blowsh sweeps hit Anthropic multi-agent research system (orchestrator-worker + programmatic tool calling validates our Kanban; parallel-workers pattern) + persona-collaboration surveys. Read true 06-personas.md (64 lines, SEVEN personas — no Dispatcher exists; auto_load is the dispatcher logic; my 196-line/8-persona memory was false, self-caught). Verdict: 6 verified-strong, Planner got ONE surgical edit (dependency-chain ordering, parallelizable lanes, per-phase verification gates, pushback on vague requirements). NO new persona (seven-seat contract; loop covered). Phase 2 (fintech skills): delegated assessment to fresh subagent — all 12 skills changed, 54 insertions, 9 deletions, zero task numbers in prose; web-verified (Next 15, Nuxt 4, golang/mock, Tailwind v4, React 19, Swift 6) + model-knowledge (cross-checked TRUE against my knowledge: Expo New Arch, Boot 3.x, Android 15 edge-to-edge, FastAPI lifespan, Flask 3.x, KSP/BOM, buf/protovalidate); risk probes via blowsh (React Compiler v1.0 stable TRUE; Nuxt 4.0 stable TRUE; v3-EOL unconfirmed → softened hard-EOL to legacy in vue-nuxt, verified). Bumped 9.26.0→9.27.0, reassembled SYNC_OK byte-identical (80462 bytes). Full suite 201 passed, exit 0. CHANGELOG entry added.

QA (brain 199-qc): QA_PASSED ([QA Engineer] + reasoning_log, REPORT). Verified Planner edit, CHANGELOG order, nuxt legacy + Compiler v1.0 + 11 skills, skill stat + zero task numbers, SYNC_OK + 201 green. No blockers. Reviewer: APPROVED → PO_REVIEW_PENDING ([Code Reviewer] + reasoning_log, REPORT). F1–F5 in pasted diff. R1 non-blocking Low. No postfix. Autoclosing under standing authorization.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `b402bfaeae50671de2956d8763916d49e18fa737`
<!-- END_GIT_DIFF -->
