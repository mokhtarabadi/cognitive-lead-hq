# Task 129: Orchestrator-Driven Manager Decision Detection for Coach Review

**File:** `tasks/completed/129-orchestrator-decision-detection-for-coach-review.md`
**Source:** telegram
**Type:** improvement
**Status:** closed

## Source Context

### Variant B: Telegram (`**Source:** telegram`)

## Goal

Make Manager decision logging proactive and precise by having the Orchestrator and Cognitive Executor intelligently detect and capture the Manager's goals and decisions from conversation context into task files, so they can be handed weekly/monthly to a coach for evaluation.

## Original Message (Persian)

ببین، بخش هشت که تصمیمات مدیر باید توی تسکها نوشته باشه که ماهانه یا هفتگی بدیم به کوچ بررسی کنه، مدیر رو ارزیابی کنه، الان دقیق نیست. تصمیمها باید توسط Orchestrator تشخیص داده بشه، چون بیشتر صحبتهای من با Orchestratorه. اون باید تشخیص بده که صحبت چی بوده وقتی میخواست تسک رو نهایی کنه، توی مرحلهی به Hands یا حالا OpenCode، ابزار Agent، دستش بوده که این تصمیمات توسط Admin گرفته شده، Manager گرفته شده، اینها رو داخل تسک بنویسه. یا اگر من خودم مستقیم مثلاً صحبت کردم با دستهای OpenCode یا Hands، حالا اسمش هرچی هست، اون خودش هم باید هوشمندانه توی اون Cognitive Executorمون این رول باشه که بتونه هوشمندانه تشخیص بده تصمیمات من چی بوده، اونجا توی تسک بنویسه که تصمیمهای دقیقی از من گرفته بشه، هدفها، تصمیمها، که بتونم هفتگی به کوچ بدم که ارزیابی انجام بده.

## English Translation

Look, section 8 — that Manager decisions must be written in the tasks so that we can give them monthly or weekly to the coach to review and evaluate the Manager — is currently not precise. The decisions must be detected by the Orchestrator, because most of my conversations are with the Orchestrator. It must detect what the conversation was about when it wanted to finalize the task, at the stage where it hands off to Hands or now OpenCode, the Agent tool, it had the ability to write into the task that these decisions were made by Admin, made by Manager. Or if I myself directly, for example, talked with the Hands of OpenCode — whatever it's called — it itself must also intelligently have this role in our Cognitive Executor, so that it can intelligently detect what my decisions were, write them in the task so that precise decisions are captured from me — the goals, the decisions — so that I can give them weekly to the coach to perform an evaluation.

## Refactored Prompt

```markdown
<role>
You are a Cognitive Architect and Systems Engineer for the Cognitive Lead AI multi-agent platform. You own the decision-capture pipeline that turns Manager conversations into auditable, coach-reviewable task records.
</role>

<system_context>
You operate inside the Cognitive Lead AI HQ repository (documentation-only: system prompts, MCP servers, Agent Skills). The decision trail lives in task files under `## Manager Decisions`, governed by `<decision_logging_mandate>` (source fragment: `prompts/fragments/17-decision_logging_mandate.md`). The Orchestrator and the Cognitive Executor agent (`agents/cognitive-executor.md`) are the two layers that interact with the Manager and must detect decisions.
</system_context>

<agentic_reasoning>
Before proposing any change, output a <reasoning_log> that evaluates:
1. Logical dependencies — which files reference the decision-logging mandate (system-prompt.md, fragments, conventions, skill templates, audit checks).
2. Risk assessment — version-bump requirement on system-prompt.md, scope creep into unrelated prompt sections, and the "do NOT log trivial changes" boundary.
3. Abductive reasoning — why the current mandate fails to capture Orchestrator-conversation decisions (it is reactive and Hands-centric, logging only execution-time decisions).
4. Precision and grounding — every proposed edit must map to a concrete file and a concrete acceptance criterion.
</agentic_reasoning>

<execution_rules>
- You MUST extend the decision-logging mandate so that decision DETECTION is a first-class responsibility of the Orchestrator and the Cognitive Executor, not just the Hands.
- You MUST preserve the existing `## Manager Decisions` log format (DECISION_ID, rationale, alternatives, impact) — do not break the audit trail.
- You MUST keep the raw Persian message verbatim in the task file's `## Original Message (Persian)` section; zero summarization.
- You MUST NOT log trivial changes (formatting, typos, config tweaks) — the existing Scope boundary stays.
- You MUST bump the `<system_version>` in system-prompt.md and log a CHANGELOG.md entry if system-prompt.md is modified.
- You MUST update `skill-templates/audit-agents/SKILL.md` audit checks to verify the new detection responsibility exists.
- You MUST NOT widen scope into unrelated prompt sections or adjacent features.
</execution_rules>

<output_format>
Deliver a structured implementation plan with:
- Root-cause diagnosis (why current logging is imprecise)
- Exact file-by-file change list with rationale
- Updated mandate text (fragment + system prompt + conventions)
- Updated agent role text (Orchestrator + Cognitive Executor)
- Updated skill templates and audit checks
- Acceptance criteria mapped to each change
- Risk & rollback plan
</output_format>
```

## Relevant Code Context

- `prompts/fragments/17-decision_logging_mandate.md` — the source fragment defining `<decision_logging_mandate>` (Purpose, When to Log, Log Format, Scope). Currently reactive and Hands-centric: "Every non-trivial decision made during task execution MUST be logged..." — no Orchestrator/Executor detection role.
- `system-prompt.md` (lines 584–616) — the mandate embedded in the system prompt; line 299 — "Decision Logging" step in the end-of-task sequence where the Hands logs decisions. Modifying this file requires a `<system_version>` bump.
- `prompts/fragments/09-hands_protocols.md` (line 86) — the Decision Logging step in the Hands protocols.
- `agents/cognitive-executor.md` (203 lines) — the Cognitive Executor agent; the layer that must gain the intelligent decision-detection role for direct Manager↔Hands/OpenCode conversations.
- `docs/conventions.md` (line 90) — the `## Decision Logging Standard` section.
- `skill-templates/task-generator/SKILL.md` — the `## Manager Decisions` section in the canonical task template.
- `skill-templates/audit-agents/SKILL.md` (lines 31, 372) — the Decision Logging Mandate audit checks that must verify the new detection responsibility.
- `AGENTS.md` (line 55) — the decision-logging guardrail ("Do log non-trivial decisions under `## Manager Decisions`...").

## AI Analysis & Opinion

**Root cause:** The current `<decision_logging_mandate>` is reactive and Hands-centric. It only logs decisions "made during task execution" and relies on the Hands to self-report after the fact. It does NOT capture the Manager's goals and decisions that occur during Orchestrator conversations (the majority of interactions) or during direct Manager↔Hands/OpenCode exchanges. As a result, the `## Manager Decisions` trail is incomplete and imprecise, which defeats the weekly/monthly coach-evaluation use case.

**Recommended fix:**
1. Extend `<decision_logging_mandate>` (fragment 17 + `system-prompt.md` + `docs/conventions.md`) to add a **Decision Detection** responsibility: the Orchestrator and Cognitive Executor MUST proactively detect and log Manager decisions/goals from conversation context during task finalization — not only execution-time decisions.
2. Add the decision-detection role to `agents/cognitive-executor.md` (and the Orchestrator agent) so direct Manager↔agent conversations are captured.
3. Update `skill-templates/task-generator/SKILL.md` and `skill-templates/audit-agents/SKILL.md` to reflect the new detection responsibility and audit checks.
4. Optionally add a structured "Coach Review" format so weekly/monthly evaluation is mechanical.

**Files to change:** `prompts/fragments/17-decision_logging_mandate.md`, `system-prompt.md` (version bump), `prompts/fragments/09-hands_protocols.md`, `agents/cognitive-executor.md`, `docs/conventions.md`, `skill-templates/task-generator/SKILL.md`, `skill-templates/audit-agents/SKILL.md`, `AGENTS.md`, `CHANGELOG.md`.

**Risks:** scope creep (touches system prompt + agents + skills); mandatory `<system_version>` bump; risk of violating the "do NOT log trivial changes" boundary if detection becomes over-eager.

## Local TODOs

- [x] Initial codebase exploration
- [x] Extend `<decision_logging_mandate>` with Decision Detection responsibility (fragment + system prompt + conventions)
- [x] Add decision-detection role to Cognitive Executor / Orchestrator agent
- [x] Update skill templates and audit checks
- [x] Bump `<system_version>` and update CHANGELOG.md
- [x] Verify functionality

## Acceptance Criteria

- [x] `<decision_logging_mandate>` explicitly assigns decision DETECTION to the Orchestrator and Cognitive Executor, not only the Hands, in `prompts/fragments/17-decision_logging_mandate.md`, `system-prompt.md`, and `docs/conventions.md`.
- [x] `agents/cognitive-executor.md` (and the Orchestrator agent) contains an explicit role instruction to intelligently detect and log the Manager's goals and decisions from conversation context into the task file.
- [x] `skill-templates/audit-agents/SKILL.md` audit checks verify the new detection responsibility; `skill-templates/task-generator/SKILL.md` reflects it.
- [x] `system-prompt.md` `<system_version>` is bumped and a formal `CHANGELOG.md` entry is added.
- [x] The raw Persian message is preserved verbatim in `## Original Message (Persian)` with zero summarization.

## Verification Evidence

- **Test command:** `npx prettier --write "prompts/fragments/17-decision_logging_mandate.md" "prompts/fragments/09-hands_protocols.md" "prompts/fragments/01-system_version.md" "docs/conventions.md" "agents/cognitive-executor.md" "skill-templates/task-generator/SKILL.md" "skill-templates/audit-agents/SKILL.md" "AGENTS.md" "CHANGELOG.md"` then `python3 scripts/prompt-build/assemble_system_prompt.py` then `grep -n "Decision Detection Responsibility" system-prompt.md` and `grep -n "<system_version>" prompts/fragments/01-system_version.md system-prompt.md` and `git diff --stat -- 'loop-engine/' '*.py'`
- **Expected result:** All modified Markdown files formatted; assembler regenerates system-prompt.md; `Decision Detection Responsibility` present in system-prompt.md; both version files show `9.2.0`; zero out-of-scope changes.
- **Actual result:** Prettier formatted all listed files (3 unchanged); assembler regenerated `system-prompt.md` (75261 bytes, exit 0); `grep` found `## Decision Detection Responsibility` at system-prompt.md:600; both `01-system_version.md` and `system-prompt.md` show `<system_version>9.2.0</system_version>`; `git diff --stat -- 'loop-engine/' '*.py'` returned empty (zero out-of-scope changes).
- **Exit code:** 0 (all commands)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Manager Decisions

**[2026-08-30] [D1] [EXECUTION-DETECTED]:** Adopted a three-tier `[SOURCE]` tag system (`ORCHESTRATOR-DETECTED` / `EXECUTOR-DETECTED` / `EXECUTION-DETECTED`) for the `## Manager Decisions` log.
- **Rationale:** The Manager's Telegram message (msg 536) requires distinguishing decisions captured from Orchestrator chat conversations, direct Manager↔Hands/OpenCode conversations, and execution-time technical necessity — so a weekly/monthly coach review can separate stated Manager intent from technical necessity.
- **Alternatives considered:** A single untagged shared log (rejected — cannot distinguish intent source, defeats the coach-evaluation use case); a two-tier system without the Hands tier (rejected — execution-time technical trade-offs would be misattributed to Manager intent).
- **Impact:** Every task file's `## Manager Decisions` section now carries source-tagged entries; the mandate, Hands protocols, Cognitive Executor agent, conventions, task-generator template, audit checks, and AGENTS.md guardrail all reference the tag system; `<system_version>` bumped 9.1.0 → 9.2.0.

## Risk & Rollback

- **Risk:** Scope creep into unrelated prompt sections; mandatory `<system_version>` bump; over-eager detection violating the "do NOT log trivial changes" boundary.
- **Rollback plan:** Revert the fragment and system-prompt edits via the injected Git diff; restore the previous `<system_version>`; the task file diff is the single rollback reference.

---

## Execution Log & Reasoning

**Files edited (9 + regenerated artifact):**

1. `prompts/fragments/17-decision_logging_mandate.md` — added `## Decision Detection Responsibility` subsection after `## When to Log` / before `## Log Format` (three-tier detection: Orchestrator `[ORCHESTRATOR-DETECTED]`, Cognitive Executor `[EXECUTOR-DETECTED]`, Hands `[EXECUTION-DETECTED]`); updated `## Log Format` entry line to `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:**` and added the SOURCE enum sentence.
2. `prompts/fragments/09-hands_protocols.md` — extended the Decision Logging step (line 86, inside `<documentation_phase>` of the implementation-task template) with the preserve-and-append rule: Hands FIRST check for pre-seeded `[ORCHORESTRATOR-DETECTED]`/`[EXECUTOR-DETECTED]` entries, preserve them unmodified, only APPEND `[EXECUTION-DETECTED]`.
3. `prompts/fragments/01-system_version.md` — bumped `<system_version>` 9.1.0 → 9.2.0 (MINOR: additive, non-breaking mandate extension).
4. `agents/cognitive-executor.md` — added new `## Decision Detection Responsibility (Direct Manager Conversations)` section after `Context Bootstrapping & Memory Protocol` (detect → log `[EXECUTOR-DETECTED]` → preserve pre-seeded entries → coach-readable).
5. `docs/conventions.md` — extended `## Decision Logging Standard` intro with the three-tier detection summary + `[SOURCE]` tag requirement + pointer to `prompts/fragments/17-decision_logging_mandate.md` as single source of truth.
6. `skill-templates/task-generator/SKILL.md` — updated BOTH `## Manager Decisions` template sections (single-phase + multi-phase) to show the `[SOURCE]`-tagged format and the Orchestrator pre-seed expectation.
7. `skill-templates/audit-agents/SKILL.md` — extended BOTH Decision Logging Mandate audit criteria (Target Audit Criteria + Mode 2) with the Decision Detection Responsibility checks (fragment 17 section, executor role, `[SOURCE]` tag format in task-generator template).
8. `AGENTS.md` — appended the `[SOURCE]` tag clause to the decision-logging guardrail (line 55).
9. `CHANGELOG.md` — added Task 129 entry under `## [9.2.0]` → `### Added` (Parse-Then-Append).
10. `system-prompt.md` — regenerated via `python3 scripts/prompt-build/assemble_system_prompt.py` (75261 bytes) from the updated fragments; confirmed `## Decision Detection Responsibility` present (line 600) and `<system_version>9.2.0</system_version>` in sync.

**Build regeneration confirmation:** The assembler picked up all fragment edits — `grep -n "Decision Detection Responsibility" system-prompt.md` → line 600; `grep -n "<system_version>" prompts/fragments/01-system_version.md system-prompt.md` → both `9.2.0`. Prettier ran before regeneration (per bash phase order), so the assembled artifact reflects the formatted fragments. Out-of-scope check: `git diff --stat -- 'loop-engine/' '*.py'` → empty (zero changes).

**Anchor points used:** fragment 17 (after `## When to Log` list, before `## Log Format`); fragment 09 (Decision Logging step 4 in `<documentation_phase>`); cognitive-executor (after Context Bootstrapping section, before Subagent Delegation); conventions (Decision Logging Standard intro); task-generator (both `## Manager Decisions` blocks); audit-agents (both Decision Logging Mandate bullets); AGENTS.md (guardrail line 55).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `6c7a41c7f4736ef909b09c86f0f920eac830e33d`
<!-- END_GIT_DIFF -->
