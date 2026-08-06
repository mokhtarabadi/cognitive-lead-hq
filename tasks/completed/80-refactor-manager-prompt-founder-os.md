# Task 80: Refactor Manager Prompt into a Founder Operating System

**File:** `tasks/completed/80-refactor-manager-prompt-founder-os.md`
**Source:** orchestrator
**Type:** improvement
**Status:** closed

## Goal

Refactor the `<manager_profile>` and `<leadership_and_language_protocol>` blocks of `system-prompt.md` so every AI persona models the Manager as an AI-native Founder building an AI-first software company — not as an elite software engineer. The refactor must preserve all existing functionality (English coaching, terminology assistance, executive communication coaching, leadership feedback) while adding a structured identity layer (Identity, Current Role, Long-term Mission, Entrepreneurial History, Technical Context, Leadership Objectives, Behavioral Patterns, Cognitive Biases, Decision Framework, Product Philosophy, Company Vision, AI Collaboration Philosophy, Coaching Preferences) and upgrading coaching behavior (co-founder / executive advisor / product strategist / systems architect / leadership coach roles; active bias defense; implicit decision-framework reasoning).

## Blueprint Reference

Orchestrator `<implementation_task>`: "Refactor Manager System Prompt into a Founder Operating System" (architecture-refactor, high priority). Scope: manager identity layer and closely related coaching behavior only. Do NOT redesign unrelated prompt architecture.

## Manager's Notes

- This is a refactor, NOT a rewrite. Maintain backward compatibility. Do not simplify existing architecture, remove protocols, or break persona interactions.
- Preserve the existing 3 coaching features verbatim in intent: Vocabulary & Keyword Assistant, English Language Corrections (`> 💡 **Coach's Note:**` with Persian phonetics), and Ruthless Soft-Skills Feedback (sprint retrospectives).
- Bias documentation is insufficient — biases must actively influence AI reasoning (bias defense).
- The Decision Framework questions must become implicit reasoning rules for every persona.
- Success criterion: the prompt must no longer primarily represent a senior engineer. Programming is one tool for building companies, not the manager's identity.
- System-prompt edits require: version bump in `<system_version>`, active task file in `tasks/`, CHANGELOG entry.

## Local TODOs

- [ ] Create task file
- [ ] Refactor `<manager_profile>` into structured Founder Operating System (13 sections)
- [ ] Upgrade `<leadership_and_language_protocol>` with founder coaching roles, bias defense, and founder-first coaching mode
- [ ] Propagate founder mission in `<role>` and `<initialization>` (one sentence each)
- [ ] Bump `<system_version>` from 8.0.2 to 8.1.0 (MINOR)
- [ ] Sync README.md (Manager Profile & AI Coaching section) and LLM.txt (Section 9 wording)
- [ ] Update CHANGELOG.md [Unreleased] with Changed entry
- [ ] Run prettier on modified markdown files
- [ ] Lint task file, stage via MCP tool

## Acceptance Criteria

- [ ] `<manager_profile>` contains all 13 required identity sections in structured, modular form
- [ ] `<leadership_and_language_protocol>` retains vocabulary assistance, English corrections, and sprint retrospective feedback; adds co-founder/executive coaching roles, bias defense, and decision-framework enforcement
- [ ] Every persona-facing entry point (`<role>`, `<manager_profile>`, `<initialization>`) communicates the founder mission
- [ ] `<system_version>` bumped to 8.1.0
- [ ] README.md and LLM.txt manager profile sections updated
- [ ] CHANGELOG.md updated with formal entry under [Unreleased]
- [ ] Task file lint passes

## Verification Evidence

- **Test command:** `grep -c "<long_term_mission>\|<cognitive_biases>\|<decision_framework>" system-prompt.md` and `grep -n "8.1.0" system-prompt.md CHANGELOG.md`
- **Expected result:** 3 identity section tags present; 8.1.0 found in `<system_version>` and CHANGELOG
- **Actual result:** _(OpenCode fills during execution)_
- **Exit code:** _(OpenCode fills during execution)_

## Risk & Rollback

- **Risk:** The expanded identity layer (~+250 tokens) increases prompt size slightly; overly verbose coaching could interrupt technical workflows.
- **Rollback plan:** Revert `system-prompt.md` `<manager_profile>`/`<leadership_and_language_protocol>` blocks to the 8.0.2 versions and restore `<system_version>` 8.0.2.

---

## OpenCode Execution Log & Reasoning

### Migration Notes (deliverable 3 — every meaningful change)

1. **`<system_version>` 8.0.2 → 8.1.0 (MINOR)** — new identity architecture, per SemVer.
2. **`<manager_profile>` rewritten as a Founder Operating System** — flat bullet list replaced with 13 nested XML sections: `<identity>`, `<current_role>`, `<long_term_mission>`, `<entrepreneurial_history>`, `<technical_context>`, `<leadership_objectives>`, `<behavioral_patterns>`, `<cognitive_biases>`, `<decision_framework>`, `<product_philosophy>`, `<company_vision>`, `<ai_collaboration_philosophy>`, `<coaching_preferences>`. All facts from the old profile preserved (name, birth year, self-taught background, technical expertise, work style, language needs) and enriched with the Orchestrator's background/mission data (Nokia Series 40 origins, 15+ years, millions of users, unofficial Persian Telegram client, success + failure arc, founder transition).
3. **`<leadership_and_language_protocol>` upgraded (0-based list)** — existing items 1–3 preserved verbatim in intent (Vocabulary Assistant, English Corrections with Persian phonetics, Ruthless Sprint Retrospective); item 3 extended to judge founder skills (delegation, vision clarity, team motivation). Two new items added: **0. Founder-First Coaching Mode** (evaluate every request against mission/decision framework/company vision; be comfortable disagreeing) and **4. Bias Defense** (actively weigh documented cognitive biases against the decision framework and surface conflicts). Renamed the block's intro from "Executive Coach and English Tutor" to co-founder/executive advisor/product strategist/systems architect/leadership coach.
4. **`<role>`** — added one propagation sentence: every persona embodies the Founder Operating System; the Manager's objective is building a company, not writing code.
5. **`<initialization>`** — AI now declares itself online as "the Manager's long-term co-founder and executive advisor".
6. **README.md** — "Manager Profile & AI Coaching" section rewritten to describe the Founder Operating System, Founder-First Coaching, and bias defense; customization instructions kept.
7. **LLM.txt Section 9** — wording updated to describe the `<manager_profile>` as a Founder Operating System (identity, mission, behavioral patterns, biases, decision framework, coaching preferences).
8. **CHANGELOG.md** — `### Changed` entry under `[Unreleased]` following the Parse-Then-Append Protocol.

### Rationale (deliverable 4 — why each change improves long-term AI behavior)

- **Structured XML sections over a flat bullet list** — the profile is now addressable: the leadership protocol, personas, and future modules can reference `<long_term_mission>`, `<cognitive_biases>`, and `<decision_framework>` by tag (as item 0 and item 4 of the protocol now do), making the identity layer modular and maintainable instead of a prose blob.
- **Mission placed inside `<manager_profile>` AND propagated via `<role>`/`<initialization>`** — the mission is the first thing the model sees in three independent places, so it survives context truncation and token dilution during long sessions. Every persona inherits founder-first framing without touching persona definitions (backward compatibility preserved).
- **Bias defense as an active rule, not documentation** — `<cognitive_biases>` alone would be descriptive; pairing it with protocol item 4 (surface conflict + counter-recommendation) converts it into a behavioral constraint the model must execute during reasoning. This directly implements the Orchestrator's "use them during reasoning" requirement.
- **Decision Framework as implicit reasoning rules** — encoded as 8 ordered questions inside the profile and cross-referenced from the protocol, so the model evaluates new work against company outcomes (recurring revenue, leverage, complexity, 5-year horizon) before recommending it. Counteracts the documented opportunity-optimism and post-failure-pivoting biases.
- **Coaching preferences honor the behavioral pattern "reacts defensively first, evaluates rationally later"** — instructs personas to state reasoning once, calmly, and let the Manager process it, which prevents the AI from backing off or escalating when the first reaction is defensive.
- **Success criteria check** — the prompt now leads with "AI-native Founder", "objective is building a company, not writing code", "programming is one tool, not his identity", and every persona-facing entry point carries the mission. The senior-engineer framing ("Elite skills in Cybersecurity...") is retained only as `<technical_context>` — supporting evidence for a technical founder, no longer the primary identity.
- **No unrelated architecture touched** — personas, protocols, templates, constraints, SOLID/datetime mandates, and the skills registry are byte-identical to 8.0.2.

### ZAC note

The Orchestrator's task block contained no `<bash_phase>` `git mv tasks/backlog/80... tasks/in-progress/80...` command, so per Zero-Autonomous-Commit the task file remains in `tasks/backlog/`. The Orchestrator must include that `git mv` as the first bash command of the follow-up closure task (or instruct it explicitly).

### Iteration 2 (Manager / Code Reviewer feedback — "همه موارد گفته شده رو اضافه کن")

The Code Reviewer scored the 8.1.0 refactor 9.8/10 architecture, 9.5/10 prompt engineering, 10/10 backward compatibility, 8.5/10 maintainability and requested 5 additional sections before merge. All incorporated (version bumped 8.1.0 → 8.1.1, PATCH):

1. **`<growth_model>`** (added inside `<manager_profile>`) — addresses "the Manager is continuously evolving": stages Solo Builder → Founder → Product Leader → Engineering Leader → CEO → Executive, with coaching style explicitly evolving per stage (early: execution/technical verification; later: delegation, vision, hiring, organizational leverage).
2. **`<ai_objective>`** (new top-level block after `<manager_profile>`) — the AI's own purpose: maximize the Manager's long-term success, NOT agreement, code quality, or conversation quality. On conflict, prefer long-term company success. The first top-level block that defines the AI's goal rather than the Manager's.
3. **`<operating_principles>`** (new top-level block) — 8 company operating rules (leverage over effort, systems over heroics, recurring revenue over one-time wins, optimization before exploration, evidence over intuition, reusable infrastructure, compounding assets, people over individual output), applied whenever recommending work, evaluating decisions, or coaching.
4. **`<delegation_strategy>`** (new top-level block) — codifies "من دیگر نمی‌خواهم خودم کد بزنم" as a rule: the default solution is NEVER "the Manager writes more code" — improve systems/AI/workflows/delegation/documentation/hiring first; direct implementation only when no better leverage exists.
5. **`<challenge_policy>`** (new top-level block) — the AI MUST explicitly challenge excitement-driven decisions, may recommend delay/evidence-collection/experiments; agreement is optional, honest disagreement is encouraged.
6. **Decision Framework question 9** — "Does this create a compounding advantage? If not, the work is probably not worth doing."
7. **Protocol binding** — `<leadership_and_language_protocol>` item 0 now references `<ai_objective>` and `<operating_principles>` alongside the existing mission/framework/vision references, so the new rules are actively enforced in every coaching response.
8. **Docs sync** — README.md (Founder OS description + Delegation Strategy bullet), LLM.txt Section 9 (growth model + new rules listed), CHANGELOG.md new 8.1.1 Changed entry (Parse-Then-Append, no duplicate headers).

**Rationale:** these five sections are what the Reviewer called "قوانین سیستم عامل شرکت" (the company OS rules) — they are persona-agnostic system constraints that outlive the Manager's personal profile. Placing the four company-level rules as top-level blocks (not nested inside `<manager_profile>`) makes them addressable by every persona and future modules, exactly like `<constraints>`; `<growth_model>` stays inside the profile because it models the Manager's trajectory. Question 9 in the Decision Framework adds the compounding filter the Reviewer flagged as the strongest single heuristic ("if the answer is no, the project is probably not worth doing").

**Correction (iteration 2 diff re-injection):** Verified 8.1.1 changes on disk, re-ran stage_and_inject_diff. Diff now reflects complete 8.1.1 state.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `cc74494881b312ea3ca27ef1ac82e9ef6fa704ef`
<!-- END_GIT_DIFF -->
