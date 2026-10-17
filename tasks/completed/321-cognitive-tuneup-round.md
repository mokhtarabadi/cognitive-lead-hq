# Task 321: Cognitive tune-up round (Lite, goal sync, skills, compaction)

**File:** `tasks/qa/321-cognitive-tuneup-round.md`
**Source:** manager
**Type:** chore
**Status:** in-progress
**Project:** /home/mohammad/Develop/Projects/cognitive-lead-hq
**Priority:** High

## Goal

Risk-based Lite entry, executor goal-sync rule, skill fallback rule, and single compaction authority across HQ prompts and docs.

## Scope (owner-approved 2026-10-17)

Four workstreams. Explicitly OUT: ferrying reduction — task 320 stays
as-is per owner decision (full task-file copy-paste each turn is kept
for full context; do not pursue 320 in this round).

## 1. Lite Mode redefinition (risk-based, not file-count)

Today Lite dies on the second touched file. Redefine eligibility by risk:
any file count allowed while the change touches no security / financial /
CLP / auth / migration surface. The decision moves from file count to
automatic gates (tests green + lint clean + §17-style greps). Update the
Lite protocol + escalation triggers. Owner fixes.

## 2. Goal sync rule (from goal-plugin deliberation, 3 conditions)

Hands writes goal status at `block` and at closure via the `goal_evidence`
tool (2 writes per goal, no background reads). Kanban stays single truth;
goal files are scratch resume pointers; on conflict Kanban wins. Plugin
needs no change — this is executor behavior. Write it into
`agents/cognitive-executor.md` (Goal Plugin Boundary section).

## 3. Skill matrix vs real stacks

`android-kotlin` does not cover Java-8 Android Views; nothing covers plain
Node CommonJS Cloud Code. Either add precise skills or define a binding
fallback rule (closest skill + explicit skip record with reason). Update
the Skill Auto-Loading Matrix.

## 4. Single-source compaction

Native auto-compact + Smart Compact write async side by side and can
diverge from task-file truth. Make the task file the sole reference:
one writer owns pruning, the other is disabled or slaved to it. Update
the Compaction section.

## Local TODOs

- [x] Steps 1-6 prompt and doc edits
- [x] Step 7 rebuild plus CHANGELOG plus tests

## Acceptance Criteria

- [x] Lite eligibility is risk-based with gate-decided entry.
- [x] Goal sync rule written; plugin untouched.
- [x] Every real stack has a covering skill or a defined fallback.
- [x] One compaction authority; task file is the reconcile target.
- [x] 320 explicitly left alone.

## Definition of Done

- [x] Assembler plus tests pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append

## Risk & Rollback

- **Risk:** Fragment plus executor plus conventions drift apart if the rebuild step is skipped.
- **Rollback plan:** Revert prompt and doc hunks via `git checkout --` on the touched paths only.

## Execution Log

- Created 2026-10-17 after 2-round Brain deliberation (Architect +
  Programmer, converged ship-with-changes). Owner implements.

## Execution Log & Reasoning

- Seat Check: executor-protocol domains, trigger word "migration" fired Architect, single-seat plan, brainstorm not required (doc-level, reversible). Brain plan approved by Manager ("Approved").
- Implemented 7 steps: fragment 10 risk-based Lite (no high-risk surface, gate-decided entry, reversible, any file count; escalation triggers); conventions.md mirror with T0 wording; executor Planning Gate Lite line; executor Goal Boundary two-writes rule (block + closure, Kanban wins, plugin untouched); registry + matrix Binding Fallback Rule with Java-8 Views and plain Node CommonJS rows, no new skills; sole-reconcile-target authority line in fragment 22, docs/compaction.md, executor; rebuilt system-prompt.md 9.60.0.
- D1: fallback rule instead of new skills (token bloat). D2: prompt-text refinements only, no sibling ADR changes (inspected prompts/fragments, agents, docs READMEs/DECISIONS.md, no domain contract change).
- Stack-skill skip record: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only prompt-text change, no stack marker applies".

## Verification Evidence

- `python3 scripts/prompt-build/assemble_system_prompt.py` expected exit 0 (recorded below).
- Stack-skill skip: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only prompt-text change".

- Verification run 1: `rtk test /home/mohammad/v2ray-to-subs/.venv/bin/pytest tests/test_prompt_sync.py tests/test_skill_registry.py -q` — expected all pass, actual 29 passed, exit 0. (Repo has no local pytest; foreign venv binary used as runner only. RTK wrapper preserved exit code with 3-line summary.)
- Greps: `Any file count allowed` 3 hits (fragment 10, conventions, executor); `sole reconcile target` 3 hits (fragment 22, docs/compaction, executor); `Binding Fallback Rule` 2 hits (registry, executor); `Goal sync rule` 1 hit (executor).
- Assembler: `python3 scripts/prompt-build/assemble_system_prompt.py --output system-prompt.md` exit 0, byte-identical re-assemble verified (108083 bytes, 9.60.0).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f9bc879..4705886 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -7,6 +7,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 ## [Unreleased]
 
 ### Added
+- **Goal sync wording fix (Task 321 rework):** closure is now first `goal_evidence` (file citations plus passing tests) then `goal_complete`, since `goal_complete` takes no arguments. Bumped `<system_version>` 9.60.0 to 9.60.1 with byte-identical re-assemble.
+
+- **Cognitive tune-up round (Task 321):** Lite eligibility is now risk-based (no high-risk surface, gate-decided entry with tests plus lint plus risk greps green, reversible via git, any file count) with matching escalation triggers in `prompts/fragments/10-lite_mode_protocol.md`, `docs/conventions.md` (T0 wording), and `agents/cognitive-executor.md`; executor Goal Boundary gains the two-writes sync rule (block plus closure, Kanban wins, plugin untouched); skill registry plus executor matrix gain the Binding Fallback Rule with Java-8 Views and plain Node CommonJS rows, no new skills; sole-reconcile-target compaction authority in fragment 22, `docs/compaction.md`, and the executor. Bumped `<system_version>` 9.59.4 to 9.60.0 with byte-identical re-assemble.
+
 - **Audit against plugin AGENT-TOOLS (compact + goal).** Aligned `prompts/fragments/22-compaction_protocol.md`, `prompts/fragments/09-hands_protocols.md`, `agents/cognitive-executor.md`, `docs/compaction.md`, and `README.md` with the shipped plugin manuals: `compact_context` async effect with no re-call to verify, `read_omitted_content` only on `omitted-NNNN` when a cheap fresh run cannot reproduce (single re-run on cache miss, never speculative), autopilot never asks the Manager for slash commands, no compaction config edits; goal lane split (Manager slash vs agent tools `goal_set`/`goal_block`/`goal_complete`/`goal_resume`, exact schemas, literal titles, never write state files, busy-retry and corrupt-report rules, evidence gate). Bumped `<system_version>` 9.59.3 to 9.59.4 with byte-identical re-assemble.
 
 - **Free-tier bash gate documented in agent docs.** `agents/README.md` now states custom agents must keep bash in the tool allowlist for free-tier models (upstream classifies by request-body tool list, 403 otherwise) plus a free-tier smoke-test checklist item; `agents/DECISIONS.md` records the accepted decision with six upstream issue refs. No permission changes.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 3198ddd..14f50ee 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -71,6 +71,10 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 | Closing or archiving a task                              | `archive-tasks`                                                                            |
 | Complex bug, deadlock, silent failure                    | `debug-instrumentation`                                                                    |
 | Implementation-producing input (any stack, any language) | `prompt-refactor` (mandatory before planning: validate, translate, expand, then structure) |
+| Java-8 Android Views, no Compose (XML layouts, Activities) | `android-kotlin` for Kotlin discipline plus tooling order only; Compose MVI Hilt SQLDelight coverage does not apply to Views (skip recorded) |
+| Plain Node CommonJS Cloud Code, no TS or hex ports      | `node-hexagonal-api` for layering intent where applicable, else no stack skill; no CommonJS Cloud Code skill exists (skip recorded) |
+
+**Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
 
 ## Direct Input (Ad-Hoc) Validation Protocol
 
@@ -98,6 +102,8 @@ Context is finite. Two layers keep long sessions productive, and the agent's dur
 
 1. **Native safety net.** OpenCode auto-compacts near the model limit: it replaces older turns with one lossy summary and keeps the most recent ~20k tokens (config: `compaction.keep.tokens`). Never depend on it to preserve working state — write the essentials to the task file as you go.
 2. **Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) is installed globally and loaded by OpenCode. It is V2-native: it stores a per-session compaction state and applies it to the model-visible messages per request, so it never mutates the stored transcript. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. After a prune, prefer a cheap fresh run of the source tool; call `read_omitted_content` with its Content ID (`omitted-NNNN`) ONLY when the output cannot be reproduced cheaply, never speculatively. On a cache miss, re-run the source tool once.
+Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
+
 3. **Survival contract.** Keep the task file holding: the active task id and Kanban lane, the pinned `[fed-context]` block with citations, the current persona/seat, the locked mode (manual or autopilot), the latest staged diff hash, open blockers, and the next action. Resume from that file after any compaction — never from a summary.
 4. **Trigger it yourself, or hand off the command.** The agent cannot run the `/magic-*` slash commands, but it CAN call the `compact_context` tool directly — prefer that when context pressure is high (pass `keepTurns` to protect recent turns, `mode: "trim"` to prune tool output only), state one line about it, then continue from the task file. Effect is async (stored now, prunes next request) — do not re-call to verify. In autopilot never ask the Manager to run slash commands; call it yourself and chain the next turn. Fall back to recommending a `/magic-compact` run to the Manager only when a tool call is not available in manual mode. Do not edit compaction config files.
 5. **Call it before heavy payloads, not after stalling.** Invoke `compact_context` yourself at these triggers: context pressure is high, 50+ steps ran without measurable progress, before a plan-approval handoff, and before QA or review turns carry a large diff. Use `mode: "trim"` when only tool output is bulky and full `compact` when turns are stale. Never re-run a source tool for pruned output — retrieve it with `read_omitted_content` by Content ID. The Brain bridge needs no change: the executor already holds direct `compact_context` access, so no Brain mention is added.
@@ -109,6 +115,7 @@ Context is finite. Two layers keep long sessions productive, and the agent's dur
 - Goal idle handler src/loop.ts 205-437 MUST NOT auto-send inside HQ sessions. Brain Bridge remains sole automation path with ZAC plus WIP3 plus approval gates per lines 24-52. If STOP_GOAL file exists at root or .opencode/STOP_GOAL, loop MUST stop immediately per src/limits.ts 25-26.
 - Goal slash inputs are exact-only: status plus clear plus complete accept no extras, parser rejects slash goalie extras per src/goal.ts 28-101. Transitions setObjective plus blockGoal plus completeGoal plus clearGoal run active-only per src/goal.ts 153-223. Agent lane is tools-only (`goal_set`, `goal_block`, `goal_complete`, `goal_resume`, exact schemas, no extra properties, titles and reasons are literal data). Never write `.opencode/goal-state.json` or `.opencode/goal-evidence.json` with file tools. Busy lease means retry the same call next turn, never work around it. Corrupt state means report to the human, never invent.
 - Goal evidence plus verifier gate is optional external check. HQ QA plus Code Reviewer gates stay authoritative per src/evidence.ts 12-47 and src/verifier.ts 18-128.
+- Goal sync rule (executor behavior, plugin untouched): Hands performs exactly two goal writes per goal: at block via `goal_block`, and at closure first `goal_evidence` (file citations plus passing tests) then `goal_complete` (`goal_complete` takes no arguments — evidence goes only through `goal_evidence`). No background reads or polling of goal state files. Kanban task files remain single source of truth; goal files are scratch resume pointers only. On any conflict Kanban wins. Never write `.opencode/goal-state.json` or `.opencode/goal-evidence.json` with file tools; use goal tools only with exact schemas; on busy-lease retry the same call next turn; on corrupt state report to the human.
 - Smart Compact operations in lines 95-104 remain unchanged.
 
 ## Capability Preflight (session start)
@@ -270,9 +277,7 @@ is governed by the Seat Check, trigger map, and reject rule below —
 "Architect seat minimum" alone is never sufficient when a trigger matches.
 Record the Brain's plan verdict plus the selected path in the task Execution
 Log (or the session/goal record when no task file exists) and execute from
-it — never from your own invention. Lite-eligible changes (single file, no
-cross-module impact, obvious fix, never login/auth, money, or security-surface
-changes) pass with a one-line justification in the file.
+it — never from your own invention. Lite-eligible changes (no security/financial/CLP/auth/migration surface, gate-decided entry with tests green plus lint clean plus risk greps clean, reversible via git. Any file count allowed while risk is low and gates pass) pass with a one-line justification in the file.
 
 Every plan states one auditable line: `Brainstorm: required | not required —
 <reason>`, per the trigger in the brainstorming protocol. Work that is
diff --git a/docs/compaction.md b/docs/compaction.md
index 5d7f2ca..ef47c4b 100644
--- a/docs/compaction.md
+++ b/docs/compaction.md
@@ -93,6 +93,8 @@ JSONC, project over global: `.opencode/smart-compact.jsonc` over `~/.config/open
 
 Each omission notice carries a Content ID (e.g. `omitted-0001`). Prefer a cheap fresh run of the source tool; the agent calls `read_omitted_content` with that ID ONLY when the output cannot be reproduced cheaply, never speculatively — the lookup is scoped to the calling session. On a cache miss, re-run the source tool once.
 
+Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
+
 ## Integration in this platform
 
 - **System prompt:** the `<compaction_protocol>` fragment (generated into `system-prompt.md`) states the two layers and the survival contract.
diff --git a/docs/conventions.md b/docs/conventions.md
index 45804c4..433e2c5 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -102,9 +102,9 @@ Process is scaled to risk. Not every task requires the full 9-step production li
 
 ### Eligibility (All Three Must Be True)
 
-1. **Single-file impact:** Change touches one file (or config-only, zero cross-module dependencies).
-2. **No security/financial impact:** No authentication, authorization, data privacy, financial calculation, or payment implications.
-3. **Explicit or obvious simplicity:** Manager says "just do it" / "quick fix" / "no plan needed", OR root cause and fix are both obvious and verifiable within one file.
+1. **No high-risk surface:** No auth/authn/authz, secrets, security-surface, financial ledger or calculation, data-privacy or CLP, PII deletion, migrations, deploys, publishes, pushes, or irreversible deletes.
+2. **Gate-decided entry:** Relevant tests green plus lint clean plus targeted risk greps clean (grep for auth, secret, migration, ledger, money, PII shows no hit in the diff).
+3. **Reversible via git:** Clear rollback path exists. Any file count allowed while risk is low and gates pass.
 
 ### Workflow
 
@@ -112,13 +112,13 @@ Bypasses Steps 1–4 of `<execution_workflow>` (Discovery, Brainstorming, Bluepr
 
 ### Escalation
 
-If implementation reveals the change is NOT trivial, the Hands MUST HALT and output: "Escalating from Lite Mode to Full Mode: [reason]." The full workflow restarts at Step 1.
+Escalate to Full Mode when any trigger fires: high-risk surface discovered, any gate fails twice, cross-module coupling beyond trivial, destructive or irreversible action required, Manager uncertain about scope. On trigger the Hands MUST HALT and output: "Escalating from Lite Mode to Full Mode: [reason]." The full workflow restarts at Step 1.
 
 ### Risk Tiers (Autopilot-Ready Contract)
 
 Every task runs at one tier. The tier sets how many human pauses apply.
 
-- **T0 trivial:** meets all three Lite eligibility criteria above. Lite fast path applies. No human pauses except QA and review verdicts.
+- **T0 trivial:** meets all Lite eligibility above (no high-risk surface, gates green, reversible). Lite fast path applies. No human pauses except QA and review verdicts.
 - **T1 standard:** multi-file changes or new behavior. Full supervised autopilot applies with a plan-approval pause plus Relay questions.
 - **T2 destructive or irreversible:** migrations, deletes, publishes, pushes, or secret handling. Each action needs explicit Manager approval. Autopilot MUST halt and never self-approve.
 
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 8ba524d..5a47730 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.59.4</system_version>
+<system_version>9.60.1</system_version>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 6cc916c..0ef04a6 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -41,4 +41,5 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+**Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
   </agent_skills_registry>
diff --git a/prompts/fragments/10-lite_mode_protocol.md b/prompts/fragments/10-lite_mode_protocol.md
index 91ebc9a..943c085 100644
--- a/prompts/fragments/10-lite_mode_protocol.md
+++ b/prompts/fragments/10-lite_mode_protocol.md
@@ -5,9 +5,9 @@ Lite Mode reduces process overhead for trivial, well-understood changes. Not eve
 
 ## Eligibility (All Three Must Be True)
 
-1. **Single-file impact:** The change touches one file (or a config-only change with zero cross-module dependencies).
-2. **No security/financial impact:** The change has no authentication, authorization, data privacy, financial calculation, or payment processing implications.
-3. **Explicit or obvious simplicity:** Either the Manager explicitly says "just do it" / "quick fix" / "no plan needed", OR the root cause and fix are both obvious and verifiable within one file (e.g., a typo, a doc fix, a config tweak, a missing import).
+1. **No high-risk surface:** No auth/authn/authz, secrets, security-surface, financial ledger or calculation, data-privacy or CLP, PII deletion, migrations, deploys, publishes, pushes, or irreversible deletes.
+2. **Gate-decided entry:** Relevant tests green plus lint clean plus targeted risk greps clean (grep for auth, secret, migration, ledger, money, PII shows no hit in the diff).
+3. **Reversible via git:** Clear rollback path exists. Any file count allowed while risk is low and gates pass.
 
 ## Workflow (Bypass Steps 1–4 of execution_workflow)
 
@@ -18,7 +18,7 @@ Lite Mode reduces process overhead for trivial, well-understood changes. Not eve
 
 ## Escalation (Full Mode Required)
 
-If during implementation the Hands discover the change is NOT trivial (e.g., the "single file" edit cascades to other modules, or a hidden dependency surfaces), the Hands MUST immediately HALT and output: "Escalating from Lite Mode to Full Mode: [reason]. Requires full discovery and planning." The Orchestrator then restarts at Step 1 of `<execution_workflow>`.
+Escalate to Full Mode when any trigger fires: high-risk surface discovered, any gate fails twice, cross-module coupling beyond trivial, destructive or irreversible action required, Manager uncertain about scope. On trigger the Hands MUST immediately HALT and output: "Escalating from Lite Mode to Full Mode: [reason]. Requires full discovery and planning." The Orchestrator then restarts at Step 1 of `<execution_workflow>`.
 
 ## Anti-Abuse Guard
 
diff --git a/prompts/fragments/22-compaction_protocol.md b/prompts/fragments/22-compaction_protocol.md
index b9ae7eb..41ef9a6 100644
--- a/prompts/fragments/22-compaction_protocol.md
+++ b/prompts/fragments/22-compaction_protocol.md
@@ -17,5 +17,7 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 
 **Rule.** The agent cannot run the `/magic-*` slash commands itself, but it CAN call `compact_context` directly — prefer that under pressure, and state one line about it. Either way, continue from the task file, never from a lossy summary. In autopilot never ask the Manager to run slash commands; call `compact_context` yourself and chain the next turn. Over-budget input still compacts with a warning. Do not edit compaction config files; human slash tools are out of scope for the agent. Durable state lives in the task file and project memory, so any compaction stays recoverable.
 
+Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
+
 Compaction precedence: Smart Compact V2 session.hook context transform preserves per-turn summaries and prunable cached I/O per src/index.ts 238-254 with defaults maxChars1024 maxWords128 task4096. Goal compaction snapshot plus restore plus evidence nudge per src/compaction.ts 28-114 MUST NOT resurrect a cleared or completed objective. If goal status is clear or complete, restore is skipped. Task file remains truth.
 </compaction_protocol>
diff --git a/system-prompt.md b/system-prompt.md
index cd16cc6..ad2c8ee 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.59.4</system_version>
+<system_version>9.60.1</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -158,6 +158,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+**Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
 </agent_skills_registry>
 
 <agentic_reasoning>
@@ -407,9 +408,9 @@ Lite Mode reduces process overhead for trivial, well-understood changes. Not eve
 
 ## Eligibility (All Three Must Be True)
 
-1. **Single-file impact:** The change touches one file (or a config-only change with zero cross-module dependencies).
-2. **No security/financial impact:** The change has no authentication, authorization, data privacy, financial calculation, or payment processing implications.
-3. **Explicit or obvious simplicity:** Either the Manager explicitly says "just do it" / "quick fix" / "no plan needed", OR the root cause and fix are both obvious and verifiable within one file (e.g., a typo, a doc fix, a config tweak, a missing import).
+1. **No high-risk surface:** No auth/authn/authz, secrets, security-surface, financial ledger or calculation, data-privacy or CLP, PII deletion, migrations, deploys, publishes, pushes, or irreversible deletes.
+2. **Gate-decided entry:** Relevant tests green plus lint clean plus targeted risk greps clean (grep for auth, secret, migration, ledger, money, PII shows no hit in the diff).
+3. **Reversible via git:** Clear rollback path exists. Any file count allowed while risk is low and gates pass.
 
 ## Workflow (Bypass Steps 1–4 of execution_workflow)
 
@@ -420,7 +421,7 @@ Lite Mode reduces process overhead for trivial, well-understood changes. Not eve
 
 ## Escalation (Full Mode Required)
 
-If during implementation the Hands discover the change is NOT trivial (e.g., the "single file" edit cascades to other modules, or a hidden dependency surfaces), the Hands MUST immediately HALT and output: "Escalating from Lite Mode to Full Mode: [reason]. Requires full discovery and planning." The Orchestrator then restarts at Step 1 of `<execution_workflow>`.
+Escalate to Full Mode when any trigger fires: high-risk surface discovered, any gate fails twice, cross-module coupling beyond trivial, destructive or irreversible action required, Manager uncertain about scope. On trigger the Hands MUST immediately HALT and output: "Escalating from Lite Mode to Full Mode: [reason]. Requires full discovery and planning." The Orchestrator then restarts at Step 1 of `<execution_workflow>`.
 
 ## Anti-Abuse Guard
 
@@ -747,6 +748,8 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 
 **Rule.** The agent cannot run the `/magic-*` slash commands itself, but it CAN call `compact_context` directly — prefer that under pressure, and state one line about it. Either way, continue from the task file, never from a lossy summary. In autopilot never ask the Manager to run slash commands; call `compact_context` yourself and chain the next turn. Over-budget input still compacts with a warning. Do not edit compaction config files; human slash tools are out of scope for the agent. Durable state lives in the task file and project memory, so any compaction stays recoverable.
 
+Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
+
 Compaction precedence: Smart Compact V2 session.hook context transform preserves per-turn summaries and prunable cached I/O per src/index.ts 238-254 with defaults maxChars1024 maxWords128 task4096. Goal compaction snapshot plus restore plus evidence nudge per src/compaction.ts 28-114 MUST NOT resurrect a cleared or completed objective. If goal status is clear or complete, restore is skipped. Task file remains truth.
 </compaction_protocol>
 
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 1894355..0498fba 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.58.0"
+    assert shipped == "9.60.1"
 
 
 def test_compaction_protocol_in_shipped_prompt():
```
<!-- END_GIT_DIFF -->

- QA: QA_PASSED (all 4 workstreams verified, 29 tests, 320 untouched). Review: technical APPROVED, PO_REVIEW_PENDING. Awaiting Manager accept word for closure.

- Rework per Manager (try 2): goal sync closure wording fixed — first `goal_evidence` then `goal_complete`; `goal_complete` takes no arguments. Version 9.60.1.

- Rework try 3 (Reviewer R1, APPROVED_WITH_CHANGES): Agent lane tools-only list now includes `goal_evidence` for consistency with the sync rule. No version bump (executor is not assembled into system-prompt). D3: one-token consistency fix, no CHANGELOG entry, sibling docs inspected with no change.
- Verification run 3: `rtk test /home/mohammad/v2ray-to-subs/.venv/bin/pytest tests/test_prompt_sync.py tests/test_skill_registry.py -q` — expected all pass, actual 29 passed, exit 0. Greps: Agent lane line shows `goal_evidence`; Goal sync rule shows block plus `goal_evidence` then `goal_complete`.
- Stack-skill skip: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only executor prose fix".
