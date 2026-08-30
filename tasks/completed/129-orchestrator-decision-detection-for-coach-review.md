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
```diff
diff --git a/AGENTS.md b/AGENTS.md
index 7900fda..5c2d05e 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -52,7 +52,7 @@ This repository is the Headquarters for the Cognitive Lead AI multi-agent system
 - **Don't** apply the full 9-step production line for trivial, single-file changes.
   -> **Do** use the `<lite_mode_protocol>` for eligible changes (single-file, no security/financial impact, obvious simplicity). Escalate to Full Mode if implementation reveals hidden complexity. See `<lite_mode_protocol>` in the system prompt.
 - **Don't** make architectural or design decisions without recording the rationale.
-  -> **Do** log non-trivial decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>`. Lite Mode tasks must log a `[LITE]` justification entry.
+  -> **Do** log non-trivial decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>`, each entry tagged `[SOURCE]` (`ORCHESTRATOR-DETECTED` / `EXECUTOR-DETECTED` / `EXECUTION-DETECTED`). Lite Mode tasks must log a `[LITE]` justification entry.
 - **Don't** guess or assume intent from ambiguous, fragmented, or unclear Manager input.
   -> **Do** HALT immediately, output a clarification request in the Manager's language, and ask targeted questions to confirm the exact intent before proceeding. (Clarification Halt — V9.1.0)
 - **Don't** issue multi-step or large tasks without loading relevant skills and structuring work as a Goal.
@@ -121,4 +121,3 @@ When finishing a task, you MUST execute these exact steps in order:
 5. **Kanban Metadata Synchronization (mandatory after ANY authorized `git mv`):** After the move, you MUST update the task file's `**File:**` metadata header to the new path. If the move happened AFTER staging, you MUST also re-run `lint_task_file` and call `custom_context_stage_and_inject_diff` again using the NEW task path before notifying the Manager — the re-stage keeps the injected diff and the staging state in sync with the final path. Never notify the Manager with a stale `**File:**` header.
 6. **Closure (Manager-authorized only):** Move the task to `tasks/completed/` and update its status to `closed` ONLY after the Manager explicitly says "Approved for closure" or "Close task"; after that closure move, update the `**File:**` metadata to the new `tasks/completed/` path; then use `custom_context_commit_and_clean_task` as the ONLY commit path.
 7. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/qa/XX-task-name.md` and send it back to the Orchestrator Brain for review."
-
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 941fc38..e45da2e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -19,6 +19,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Remove opentmux and opencode-agent-tmux — keep tmux (Task 125)** — fully removed the OpenCode tmux wrapper layer per manager directive: uninstalled global npm packages `opentmux@1.5.7` and `opencode-agent-tmux@1.3.0` (`npm uninstall -g opentmux opencode-agent-tmux`), removed `"opentmux"` from `~/.config/opencode/opencode.json` plugin array (now `["@prevalentware/opencode-goal-plugin"]` after Task 126; was `["opencode-goal-plugin"]` before), deleted `README.md` `### Optional: opentmux` section, deleted `docs/setup.md` `## opentmux — Smart Tmux Integration` section (Installation/Verify/Usage/Features/Shell Configuration), and cleaned `LLM.txt` (Node.js prerequisite reworded without opentmux, deleted `### 6.2. Install opentmux Globally` section, removed `opentmux --version` verification checklist item). System `tmux` (`/usr/bin/tmux` 3.6, apt `3.6a-2ubuntu0.1`) is retained. Historical records preserved: `CHANGELOG.md` Task 120 entry, `docs/history/milestone-14-summary.md`, `tasks/archive/120-*.md`. Verified: `which tmux && tmux -V` → 3.6, `which opentmux` fails, `npm list -g` shows no tmux plugins, `grep -r opentmux` over active docs returns 0.
 
+## [9.2.0] - 2026-08-30
+
+### Added
+
+- **Orchestrator-Driven Manager Decision Detection for Coach Review (Task 129)** — extended `<decision_logging_mandate>` with a three-tier Decision Detection Responsibility: the **Orchestrator** pre-seeds Manager decisions/goals from chat conversations into the task file's `## Manager Decisions` (tagged `[ORCHESTRATOR-DETECTED]`), the **Cognitive Executor** detects decisions from direct Manager ↔ Hands/OpenCode conversations (tagged `[EXECUTOR-DETECTED]`), and the **Hands** log execution-time decisions (tagged `[EXECUTION-DETECTED]`). Log format updated to `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:**` with SOURCE enum. Updated `prompts/fragments/17-decision_logging_mandate.md` (new subsection + format), `prompts/fragments/09-hands_protocols.md` (preserve-and-append rule for Hands), `agents/cognitive-executor.md` (new Decision Detection Responsibility section), `docs/conventions.md` (three-tier summary + source-of-truth pointer), `skill-templates/task-generator/SKILL.md` (both `## Manager Decisions` templates show `[SOURCE]` format + Orchestrator pre-seed note), `skill-templates/audit-agents/SKILL.md` (both audit criteria extended with detection checks), `AGENTS.md` (guardrail `[SOURCE]` clause). `<system_version>` bumped **9.1.0 → 9.2.0** and `system-prompt.md` reassembled (75261 bytes, `## Decision Detection Responsibility` at line 600). Verified: prettier, assembler exit 0, version sync, zero out-of-scope changes.
+
 ## [9.1.0] - 2026-08-27
 
 ### Added
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 81892ec..ebf505f 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -88,6 +88,15 @@ To prevent hallucinations and respect hidden project constraints, you MUST integ
    - **DO SAVE:** "The manager prefers Composition over Inheritance," "API X rate limits at 100 req/s, add caching," "Do not use Library Y because of Z."
    - **DO NOT SAVE:** Task progress, transient bug states, or code snippets (those belong in the task file).
 
+## Decision Detection Responsibility (Direct Manager Conversations)
+
+When the Manager talks directly to you (the Hands/OpenCode agent) without going through the Orchestrator chat, you MUST perform the decision-detection role defined in `<decision_logging_mandate>`:
+
+1. **Detect:** During your conversation with the Manager, intelligently identify the Manager's goals and decisions — approvals, rejections, scope changes, chosen trade-offs, and stated objectives.
+2. **Log:** Write these into the active task file's `## Manager Decisions` section, tagged `[EXECUTOR-DETECTED]`, using the format `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>` with rationale, alternatives considered, and impact.
+3. **Preserve:** If the task file already contains pre-seeded `[ORCHESTRATOR-DETECTED]` entries, preserve them unmodified — you only APPEND new `[EXECUTOR-DETECTED]` entries, never overwrite or duplicate existing ones.
+4. **Coach-Readable:** Ensure the resulting log is precise and chronologically ordered so a weekly/monthly coach review can distinguish stated Manager intent (Orchestrator/Executor) from technical necessity (Hands).
+
 ## Subagent Delegation for Context Discovery
 
 To preserve your primary context window for implementation logic, you MUST delegate heavy context-gathering tasks to the `cognitive-discovery` subagent using your `task` tool:
@@ -104,6 +113,7 @@ Use these patterns to communicate with precision and engineering value.
 ### Reference Points
 
 When presenting three or more findings, decisions, options, risks, questions, or actions, assign every one a short code:
+
 - `D1`, `D2` for decisions
 - `F1`, `F2` for findings
 - `R1`, `R2` for risks
@@ -156,6 +166,7 @@ When a circuit breaker fires, output a `⚠️ CIRCUIT BREAKER` warning with the
 ### Reasoning Drift Prevention
 
 For tasks exceeding 100 steps, re-anchor to the original goal every 50 steps by answering:
+
 1. What was the original task goal?
 2. What have I completed so far?
 3. What remains?
diff --git a/docs/conventions.md b/docs/conventions.md
index c6f2c82..494f143 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -89,6 +89,8 @@ When writing or reviewing bash scripts, cron jobs, or container orchestration co
 
 Every non-trivial decision made during task execution MUST be logged in the active task file under `## Manager Decisions`. This creates an auditable trail of architectural, design, and strategic choices.
 
+Decision detection is a three-tier responsibility: the **Orchestrator** pre-seeds Manager decisions from chat conversations (tagged `[ORCHESTRATOR-DETECTED]`), the **Cognitive Executor** detects decisions from direct Manager ↔ Hands/OpenCode conversations (tagged `[EXECUTOR-DETECTED]`), and the **Hands** log execution-time decisions (tagged `[EXECUTION-DETECTED]`). Each entry carries a `[SOURCE]` tag so a weekly/monthly coach review can distinguish stated Manager intent from technical necessity. The single source of truth for the full mandate is `prompts/fragments/17-decision_logging_mandate.md` — this section is a summary only.
+
 ### When to Log
 
 - Architectural choices (framework, pattern, data store, API design).
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 5be7a70..4daa910 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.1.0</system_version>
\ No newline at end of file
+<system_version>9.2.0</system_version>
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index c438957..3bc1851 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -83,7 +83,7 @@
 
   <documentation_phase>
     HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version.
-    4) **Decision Logging:** If this task involved any architectural, design, or strategic decision (not purely mechanical), you MUST log it under `## Manager Decisions` in the task file using the format: `**[DATE] [DECISION_ID]:** <decision summary> — <rationale> — <alternatives considered>`. See `<decision_logging_mandate>` for the full standard.
+    4) **Decision Logging:** If this task involved any architectural, design, or strategic decision (not purely mechanical), you MUST log it under `## Manager Decisions` in the task file using the format: `**[DATE] [DECISION_ID] [SOURCE]:** <decision summary> — <rationale> — <alternatives considered>`. See `<decision_logging_mandate>` for the full standard. FIRST check the task file's `## Manager Decisions` section for any pre-seeded `[ORCHESTRATOR-DETECTED]` or `[EXECUTOR-DETECTED]` entries and preserve them unmodified — the Hands only APPENDS new `[EXECUTION-DETECTED]` entries, never overwrites or duplicates existing ones.
   </documentation_phase>
 
   <summary_phase>
@@ -144,4 +144,4 @@
 ```
 
 </hands_combined_task_template>
-</hands_protocols>
\ No newline at end of file
+</hands_protocols>
diff --git a/prompts/fragments/17-decision_logging_mandate.md b/prompts/fragments/17-decision_logging_mandate.md
index f24edef..8d204e5 100644
--- a/prompts/fragments/17-decision_logging_mandate.md
+++ b/prompts/fragments/17-decision_logging_mandate.md
@@ -1,4 +1,5 @@
 <decision_logging_mandate>
+
 ## Purpose
 
 Every non-trivial decision made during task execution MUST be logged in the active task file under `## Manager Decisions`. This creates an auditable trail of architectural, design, and strategic choices — preventing repeated debates and enabling future agents to understand WHY something was built a certain way.
@@ -6,28 +7,40 @@ Every non-trivial decision made during task execution MUST be logged in the acti
 ## When to Log
 
 Log a decision whenever any of the following occurs:
+
 - An architectural choice is made (framework, pattern, data store, API design).
 - A design trade-off is accepted (e.g., performance vs. readability, consistency vs. availability).
 - The Manager explicitly approves a plan that involves trade-offs.
 - A constraint or requirement drives a specific implementation approach.
 - Lite Mode is applied (log the justification).
 
+## Decision Detection Responsibility
+
+Logging a decision is not solely the Hands' job. Detection must happen at the layer closest to the Manager's actual words:
+
+- **Orchestrator (chat-based conversations):** When finalizing a task for handoff to the Hands/OpenCode, the Orchestrator MUST review the conversation that produced this task and explicitly identify any Manager decisions or goals — approvals, rejections, scope changes, chosen trade-offs. These MUST be pre-seeded into the generated task file's `## Manager Decisions` section, tagged `[ORCHESTRATOR-DETECTED]`, before the task is handed to the Hands.
+- **Cognitive Executor (direct Manager ↔ Hands/OpenCode conversations):** When the Manager talks directly to the Hands/OpenCode agent without going through the Orchestrator chat, the Cognitive Executor MUST perform the same detection role during its own conversation with the Manager, logging entries tagged `[EXECUTOR-DETECTED]`.
+- **Hands (execution-time):** Continues to log decisions made or discovered strictly during implementation (e.g., an unforeseen technical constraint forcing a trade-off), tagged `[EXECUTION-DETECTED]`.
+
+This produces one unified, chronologically ordered `## Manager Decisions` log per task. Each entry's `[SOURCE]` tag lets a weekly/monthly coach review distinguish stated Manager intent (Orchestrator/Executor) from technical necessity (Hands).
+
 ## Log Format
 
 Each entry MUST follow this exact format:
 
 ```
-**[YYYY-MM-DD] [DECISION_ID]:** <one-line decision summary>
+**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <one-line decision summary>
 - **Rationale:** <why this decision was made>
 - **Alternatives considered:** <what else was evaluated>
 - **Impact:** <what this affects or constrains>
 ```
 
 - **DECISION_ID** is a sequential identifier scoped to the task (e.g., D1, D2, D3).
+- **SOURCE** MUST be one of: ORCHESTRATOR-DETECTED, EXECUTOR-DETECTED, EXECUTION-DETECTED.
 - Decisions are appended in chronological order. Never reorder or delete entries.
 
 ## Scope
 
 - **Log:** Architectural patterns, technology choices, API contracts, data model decisions, security trade-offs, performance vs. readability trade-offs, scope changes, and Lite Mode justifications.
 - **Do NOT log:** Formatting changes, typo fixes, trivial config tweaks, or any change where the "why" is self-evident from the code itself.
-</decision_logging_mandate>
\ No newline at end of file
+  </decision_logging_mandate>
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 1aeff79..7bedfa3 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -28,7 +28,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Manager Decisions` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
-- **Decision Logging Mandate**: `AGENTS.md` MUST instruct the Hands to log non-trivial architectural, design, and strategic decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>` (sequential DECISION_ID, rationale, alternatives, impact). `docs/conventions.md` MUST contain a `## Decision Logging Standard` section.
+- **Decision Logging Mandate**: `AGENTS.md` MUST instruct the Hands to log non-trivial architectural, design, and strategic decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>` (sequential DECISION_ID, rationale, alternatives, impact). `docs/conventions.md` MUST contain a `## Decision Logging Standard` section. **Decision Detection Responsibility**: `prompts/fragments/17-decision_logging_mandate.md` MUST contain a `## Decision Detection Responsibility` section; `agents/cognitive-executor.md` MUST contain the executor detection role (tagged `[EXECUTOR-DETECTED]`); `skill-templates/task-generator/SKILL.md`'s `## Manager Decisions` template MUST show the `[SOURCE]` tag format (ORCHESTRATOR-DETECTED / EXECUTOR-DETECTED / EXECUTION-DETECTED).
 
 ---
 
@@ -369,7 +369,7 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 - **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Manager Decisions` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
-- **Decision Logging Mandate**: `AGENTS.md` MUST instruct the Hands to log non-trivial architectural, design, and strategic decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>` (sequential DECISION_ID, rationale, alternatives, impact). `docs/conventions.md` MUST contain a `## Decision Logging Standard` section.
+- **Decision Logging Mandate**: `AGENTS.md` MUST instruct the Hands to log non-trivial architectural, design, and strategic decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>` (sequential DECISION_ID, rationale, alternatives, impact). `docs/conventions.md` MUST contain a `## Decision Logging Standard` section. **Decision Detection Responsibility**: `prompts/fragments/17-decision_logging_mandate.md` MUST contain a `## Decision Detection Responsibility` section; `agents/cognitive-executor.md` MUST contain the executor detection role (tagged `[EXECUTOR-DETECTED]`); `skill-templates/task-generator/SKILL.md`'s `## Manager Decisions` template MUST show the `[SOURCE]` tag format (ORCHESTRATOR-DETECTED / EXECUTOR-DETECTED / EXECUTION-DETECTED).
 
 ### Resolution Protocol
 
diff --git a/skill-templates/task-generator/SKILL.md b/skill-templates/task-generator/SKILL.md
index 7a5b856..974f1e4 100644
--- a/skill-templates/task-generator/SKILL.md
+++ b/skill-templates/task-generator/SKILL.md
@@ -133,7 +133,7 @@ If the output is non-empty, HALT and report duplicate task IDs. Do NOT overwrite
 
    ## Manager Decisions
 
-   _(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`. For Lite Mode tasks, log a `[LITE]` justification entry.)_
+   _(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>` where SOURCE is ORCHESTRATOR-DETECTED, EXECUTOR-DETECTED, or EXECUTION-DETECTED. The Orchestrator is expected to pre-seed this section with `[ORCHESTRATOR-DETECTED]` entries during task generation when applicable. For Lite Mode tasks, log a `[LITE]` justification entry.)_
 
    ## Risk & Rollback
 
@@ -194,7 +194,7 @@ The task is NOT done unless ALL of the following are true (unconditional, applie
 
 ## Manager Decisions
 
-_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`. For Lite Mode tasks, log a `[LITE]` justification entry.)_
+_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>` where SOURCE is ORCHESTRATOR-DETECTED, EXECUTOR-DETECTED, or EXECUTION-DETECTED. The Orchestrator is expected to pre-seed this section with `[ORCHESTRATOR-DETECTED]` entries during task generation when applicable. For Lite Mode tasks, log a `[LITE]` justification entry.)_
 
 ## Risk & Rollback
 
@@ -272,7 +272,7 @@ uv run scripts/bundle-tasks.py 1 2 3 4 5 6 7 --title "mega-bundle" --force  # by
    - `**Status:** superseded`
    - `**Superseded-By:** <META_ID>-<slug>` + `**Superseded-At:** YYYY-MM-DD`
    - Superseded footer before `## Execution Log` with `git log --follow` hint
-   History remains reachable: `git log --oneline --follow -- tasks/archive/<file>`
+     History remains reachable: `git log --oneline --follow -- tasks/archive/<file>`
 
 ### Guardrails
 
diff --git a/system-prompt.md b/system-prompt.md
index ced3506..b806ad4 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.1.0</system_version>
+<system_version>9.2.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -296,7 +296,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
   <documentation_phase>
     HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version.
-    4) **Decision Logging:** If this task involved any architectural, design, or strategic decision (not purely mechanical), you MUST log it under `## Manager Decisions` in the task file using the format: `**[DATE] [DECISION_ID]:** <decision summary> — <rationale> — <alternatives considered>`. See `<decision_logging_mandate>` for the full standard.
+    4) **Decision Logging:** If this task involved any architectural, design, or strategic decision (not purely mechanical), you MUST log it under `## Manager Decisions` in the task file using the format: `**[DATE] [DECISION_ID] [SOURCE]:** <decision summary> — <rationale> — <alternatives considered>`. See `<decision_logging_mandate>` for the full standard. FIRST check the task file's `## Manager Decisions` section for any pre-seeded `[ORCHESTRATOR-DETECTED]` or `[EXECUTOR-DETECTED]` entries and preserve them unmodified — the Hands only APPENDS new `[EXECUTION-DETECTED]` entries, never overwrites or duplicates existing ones.
   </documentation_phase>
 
   <summary_phase>
@@ -582,6 +582,7 @@ To prevent silent data corruption and financial drift, you MUST enforce the Univ
 </immutable_financial_ledger_mandate>
 
 <decision_logging_mandate>
+
 ## Purpose
 
 Every non-trivial decision made during task execution MUST be logged in the active task file under `## Manager Decisions`. This creates an auditable trail of architectural, design, and strategic choices — preventing repeated debates and enabling future agents to understand WHY something was built a certain way.
@@ -589,31 +590,43 @@ Every non-trivial decision made during task execution MUST be logged in the acti
 ## When to Log
 
 Log a decision whenever any of the following occurs:
+
 - An architectural choice is made (framework, pattern, data store, API design).
 - A design trade-off is accepted (e.g., performance vs. readability, consistency vs. availability).
 - The Manager explicitly approves a plan that involves trade-offs.
 - A constraint or requirement drives a specific implementation approach.
 - Lite Mode is applied (log the justification).
 
+## Decision Detection Responsibility
+
+Logging a decision is not solely the Hands' job. Detection must happen at the layer closest to the Manager's actual words:
+
+- **Orchestrator (chat-based conversations):** When finalizing a task for handoff to the Hands/OpenCode, the Orchestrator MUST review the conversation that produced this task and explicitly identify any Manager decisions or goals — approvals, rejections, scope changes, chosen trade-offs. These MUST be pre-seeded into the generated task file's `## Manager Decisions` section, tagged `[ORCHESTRATOR-DETECTED]`, before the task is handed to the Hands.
+- **Cognitive Executor (direct Manager ↔ Hands/OpenCode conversations):** When the Manager talks directly to the Hands/OpenCode agent without going through the Orchestrator chat, the Cognitive Executor MUST perform the same detection role during its own conversation with the Manager, logging entries tagged `[EXECUTOR-DETECTED]`.
+- **Hands (execution-time):** Continues to log decisions made or discovered strictly during implementation (e.g., an unforeseen technical constraint forcing a trade-off), tagged `[EXECUTION-DETECTED]`.
+
+This produces one unified, chronologically ordered `## Manager Decisions` log per task. Each entry's `[SOURCE]` tag lets a weekly/monthly coach review distinguish stated Manager intent (Orchestrator/Executor) from technical necessity (Hands).
+
 ## Log Format
 
 Each entry MUST follow this exact format:
 
 ```
-**[YYYY-MM-DD] [DECISION_ID]:** <one-line decision summary>
+**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <one-line decision summary>
 - **Rationale:** <why this decision was made>
 - **Alternatives considered:** <what else was evaluated>
 - **Impact:** <what this affects or constrains>
 ```
 
 - **DECISION_ID** is a sequential identifier scoped to the task (e.g., D1, D2, D3).
+- **SOURCE** MUST be one of: ORCHESTRATOR-DETECTED, EXECUTOR-DETECTED, EXECUTION-DETECTED.
 - Decisions are appended in chronological order. Never reorder or delete entries.
 
 ## Scope
 
 - **Log:** Architectural patterns, technology choices, API contracts, data model decisions, security trade-offs, performance vs. readability trade-offs, scope changes, and Lite Mode justifications.
 - **Do NOT log:** Formatting changes, typo fixes, trivial config tweaks, or any change where the "why" is self-evident from the code itself.
-</decision_logging_mandate>
+  </decision_logging_mandate>
 
 <initialization>
 Acknowledge these instructions. Declare yourself online as the **[Cognitive Lead AI]**. Immediately initiate **Phase 0: Discovery & Onboarding**.
```
<!-- END_GIT_DIFF -->
