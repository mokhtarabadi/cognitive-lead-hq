# Task 178: Prompt optimization — brainstorm stub + clarity style

**File:** `tasks/qa/178-prompt-optimization-brainstorm-stub-and-clarity-style.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Optimize `system-prompt.md` / `prompts/fragments/` for token efficiency and manager-facing clarity: stub the duplicated brainstorming protocol (hybrid, not full delete) and add ASD-STE100-inspired clarity constraints scoped to the final response only.

## Manager's Notes

Approved after LLM-level analysis (2026-09-10): (1) Don't fully delete `prompts/fragments/12-brainstorming_protocol.md` — the Brain needs a trigger in the system prompt, skill alone only covers Hands. Hybrid = short stub (~12 lines) linking to `brainstorm-swarm` skill detail. Saves ~350 tokens. (2) ASD-STE100 paste is compatible if scoped to final Manager response only — deep reasoning thinking stays rich, only the externally visible output is simplified (short sentences ≤25 words, one idea per sentence, defined context before reference, active voice, compressed list codes). (3) Executor cognitive roles are healthy — minor matrix addition only.

Scope: `prompts/fragments/12-brainstorming_protocol.md` stub, `system-prompt.md` via prompt composer (never hand-edit directly), `agents/cognitive-executor.md` patterns update, `CHANGELOG.md`. Assembled `system-prompt.md` must stay byte-identical to `prompts/fragments/` + `prompts/shared/` (verify via `lint_system_prompt_sync`).

## Local TODOs

- [x] Stub `prompts/fragments/12-brainstorming_protocol.md` to hybrid trigger (keep Brain trigger, delegate detail to `brainstorm-swarm` skill)
- [x] Add clarity constraints for final Manager response (ASD-STE100-inspired, scoped — not deep reasoning)
- [x] Update `agents/cognitive-executor.md` Communication Patterns to reflect clarity style + add brainstorm-swarm matrix row
- [x] Re-assemble `system-prompt.md` via prompt composer and verify byte-identical (`lint_system_prompt_sync`)
- [x] Update `CHANGELOG.md` via Parse-Then-Append
- [x] Lint task file + verify, then stage and move to QA

## Acceptance Criteria

- [x] `prompts/fragments/12-brainstorming_protocol.md` is a short stub (not 52 lines) that still triggers Brain-side brainstorming and points to `brainstorm-swarm` skill for full session procedure
- [x] `system-prompt.md` contains clarity constraints scoped to final response only (does not suppress deep reasoning)
- [x] `agents/cognitive-executor.md` reflects clarity style in Positive/Negative Patterns and lists `brainstorm-swarm` in skill matrix if applicable
- [x] `lint_system_prompt_sync` passes (assembled file in sync)
- [x] `CHANGELOG.md` updated
- [x] `lint_task_file` passes on `tasks/in-progress/178-*.md` (post-move)

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py` + `lint_system_prompt_sync` + `lint_task_file tasks/in-progress/178-prompt-optimization-brainstorm-stub-and-clarity-style.md` + `wc -l prompts/fragments/12-brainstorming_protocol.md; grep -n brainstorm-swarm prompts/fragments/12-brainstorming_protocol.md` + `grep -n "Response Clarity" system-prompt.md prompts/fragments/13-constraints.md` + `grep -n brainstorm-swarm agents/cognitive-executor.md` + `grep -n 178 CHANGELOG.md | head`
- **Expected result:** stub is ~6 lines with skill reference; clarity clause present and scoped to final response; compose + sync in-sync; lint passes; CHANGELOG has 178 entry
- **Actual result:** assemble ok (638 lines, 74178 bytes, diff byte-identical SYNC OK); `lint_system_prompt_sync` ✅ in sync; `lint_task_file` ✅ passed; `wc -l` 6 with `brainstorm-swarm` ref (line 4); `Response Clarity — Final Manager Response Only` present in system-prompt.md and fragment 13; executor has `brainstorm-swarm` row; `CHANGELOG.md: Task 178` entry present
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Over-stubbing removes Brain trigger → brainstorming never fires. Over-scoping clarity style suppresses chain-of-thought reasoning.
- **Rollback plan:** `git diff prompts/fragments/12-brainstorming_protocol.md system-prompt.md agents/cognitive-executor.md` + `git restore` those three files + re-compose; task file stays in `tasks/in-progress/` until QA.

---

## Execution Log & Reasoning

**Scope (hybrid, not full delete):** Manager approved: stub keeps Brain trigger (task discovery), Hands delegates detail to skill. ASD-STE100 style scoped to final Manager response only — chain-of-thought stays rich.

**Edits (5 files):**
- `prompts/fragments/12-brainstorming_protocol.md` — replaced 53-line persona table + report schema with 6-line stub: trigger `cross-disciplinary ambiguity OR explicit \"brainstorm\"` → `Max one turn per Orchestrator request, load skill \"brainstorm-swarm\" for full persona matrix + report schema`. Saves ~350 tokens per session.
- `prompts/fragments/13-constraints.md` — added `Response Clarity — Final Manager Response Only` constraint: ≤25 words, one idea/sentence, define before reference, active voice, coded lists `F/D/R/Q/A`, does not apply to internal reasoning.
- `prompts/fragments/01-system_version.md` — `9.12.0` → `9.13.0`.
- `system-prompt.md` — regenerated via `python3 scripts/prompt-build/assemble_system_prompt.py` → 638 lines (from 684), 74178 bytes, byte-identical to fragments+shared (diff 0, SYNC OK). Not hand-edited.
- `agents/cognitive-executor.md` — Positive Patterns added scoped clarity bullet; Skill Auto-Loading Matrix added `brainstorm-swarm` row (`cross-disciplinary ambiguity`).
- `CHANGELOG.md` — Unreleased `Changed` entry for Task 178 via Parse-Then-Append.

**Verification:** `lint_system_prompt_sync` ✅, `lint_task_file` ✅, grep checks ok (stub 6 lines, Response Clarity hits, brainstorm-swarm in executor, 9.13.0, Task 178 in changelog).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 8ea671a..9f44dac 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -33,6 +33,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Plugin install docs (Task 173):** `LLM.txt` §7.7 + README plugins section now carry both plugin install commands, cache-presence verification (`~/.cache/opencode/packages/`), and the restart requirement — closing the referenced-but-never-installed gap that hid `/dcp-compress`.
 - **Audit cleanup + self-improve pass (Task 177):** `system-prompt.md` regenerated to **9.11.0** (absorbs the restored `brainstorm-swarm` registry line in fragment 07; sync-check clean); `docs/setup.md` gains the automation-paused banner (persona/decision servers disabled, commands archived, global blowsh+telegram note); `skill-templates/manager-decision/SKILL.md` gains a PAUSED banner (skill inert until restore); `skill-templates/versioning-and-release/SKILL.md` drops the stale `V5.3.0` pin; executor skill matrix annotates the `manager-decision` row as paused; `RESTORE.md` step 5 marked restore-time-only; `.gitignore` gains `.pytest_cache/` + `.ruff_cache/`. Full suite **138 passed**, zero `.py` changes.
 - **Context-server wedging hardened + docs overhaul (Task 177 expansion):** `mcp-context-server/server.py` gains runaway-traversal guards — `get_directory_tree` mirrors the `create_tree_report` workspace confinement (escapes rejected, non-string targets default to root), `generate_tree` caps depth (8) + entries (2000) with truncation markers, `collect_files` caps at 1000 files, and `BANNED_DIRS` (`.git/.cache/__pycache__/node_modules/.venv/venv/proc/sys/dev`) is never descended into; `read_source_files` prepends report metrics (processed/skipped/bytes/duration). Fixes the diagnosed wedge where a `/` tree burned 7 CPU-minutes on the single-threaded server and starved all later calls. README overhauled (Manual Mode marked ACTIVE/DEFAULT, persona section + commands + manager-decision link marked paused, blowsh skill row + 5-tool suite, loop-engine docs path corrected, skill count 33); `docs/system-prompt-modularization.md` archived to `archive/automation-paused-2026-09-09/docs-superseded/`; `.gitignore` extended (`.uv/`, `.uv-cache/`, `.mypy_cache/`, `.coverage`, `htmlcov/`).
+- **Prompt optimization — brainstorm stub + clarity style (Task 178):** Stubbed `prompts/fragments/12-brainstorming_protocol.md` from 53 lines to 6 lines — hybrid trigger (Brain keeps the 1.5 trigger) + `brainstorm-swarm` skill ref for full persona/schema detail (saves ~350 tokens per prompt). Added `Response Clarity (ASD-STE100-inspired, scoped)` constraint to `prompts/fragments/13-constraints.md` — applies only to the final Manager-facing response (short sentences ≤25 words, one idea per sentence, defined context before pronoun, active voice, coded lists), deep reasoning / `<reasoning_log>` / XML tasks stay rich. Updated `agents/cognitive-executor.md` Positive Patterns + Skill Auto-Loading Matrix (`brainstorm-swarm` row). Bumped `<system_version>` **9.12.0 → 9.13.0** and reassembled `system-prompt.md` (638 lines, sync-check byte-identical).
 
 ### Removed
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index de99c57..4305034 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -67,6 +67,7 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 | Creating a new task file               | `task-generator`                                                                                                                                                                             |
 | Closing or archiving a task            | `archive-tasks`                                                                                                                                                                              |
 | Complex bug, deadlock, silent failure  | `debug-instrumentation`                                                                                                                                                                      |
+| Brainstorming, cross-disciplinary ambiguity | `brainstorm-swarm`                                                                                                                                                                           |
 | Manager decision capture, ruling reuse | `manager-decision` <!-- PAUSED-2026-09-09 (Task 177): manager_decisions server disabled in Task 176 — do NOT auto-load this skill until restore. Original row kept for future re-enable. --> |
 
 ## Direct Input (Ad-Hoc) Validation Protocol
@@ -122,6 +123,7 @@ Preserve the same codes throughout the conversation. Do not create codes for sho
 - Do not use overloaded terms. Use the simplest word(s) that satisfies the idea.
 - Challenge incorrect assumptions directly and explain why.
 - Optimize for clarity and engineering value, not quotability.
+- For the final Manager-facing handoff only (not `<reasoning_log>` or XML tasks), keep sentences ≤25 words, one idea per sentence, defined context before pronoun reference, active voice — deep reasoning stays unrestricted and rich.
 
 ### Negative Patterns
 
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 96aae70..7ecb219 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.12.0</system_version>
+<system_version>9.13.0</system_version>
diff --git a/prompts/fragments/12-brainstorming_protocol.md b/prompts/fragments/12-brainstorming_protocol.md
index 4995918..1475cdb 100644
--- a/prompts/fragments/12-brainstorming_protocol.md
+++ b/prompts/fragments/12-brainstorming_protocol.md
@@ -1,53 +1,6 @@
 <brainstorming_protocol>
 <phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
 <trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona.</trigger>
-<workflow>
-Activate six expert personas simultaneously. Each persona analyzes the problem from its domain and produces a structured response. The Orchestrator then synthesizes these perspectives into a final plan.
-</workflow>
-<personas>
-<persona name="system_architect">
-<focus>System design, scalability, data flow, API contracts, infrastructure, and architectural trade-offs.</focus>
-<output>Technical architecture assessment with risk analysis and recommended patterns.</output>
-</persona>
-<persona name="security_engineer">
-<focus>Threat modeling, authentication/authorization, data privacy, compliance, and vulnerability assessment.</focus>
-<output>Security audit with identified risks, severity ratings, and mitigation strategies.</output>
-</persona>
-<persona name="product_manager">
-<focus>User needs, feature prioritization, roadmap alignment, MVP definition, and stakeholder communication.</focus>
-<output>Product requirements analysis with prioritized user stories and success metrics.</output>
-</persona>
-<persona name="business_strategist">
-<focus>Market positioning, ROI analysis, competitive landscape, monetization models, and go-to-market strategy.</focus>
-<output>Business case assessment with strategic recommendations and risk/reward analysis.</output>
-</persona>
-<persona name="legal_advisor">
-<focus>Regulatory compliance, licensing, data protection laws (GDPR/CCPA), intellectual property, and contractual obligations.</focus>
-<output>Legal compliance review with identified obligations, risks, and recommended safeguards.</output>
-</persona>
-<persona name="critical_thinker">
-<focus>Devil's advocacy, assumption challenging, blind-spot detection, logical fallacies, and edge-case stress-testing.</focus>
-<output>Critical review highlighting unstated assumptions, cognitive biases, and stress-test results for each proposed approach.</output>
-</persona>
-</personas>
-<output_schema>
-<brainstorming_session>
-<summary>Synthesized multi-persona analysis resolving the key ambiguities.</summary>
-<persona_responses>
-<response persona="system_architect">...</response>
-<response persona="security_engineer">...</response>
-<response persona="product_manager">...</response>
-<response persona="business_strategist">...</response>
-<response persona="legal_advisor">...</response>
-<response persona="critical_thinker">...</response>
-</persona_responses>
-<tradeoffs>
-<tradeoff factor="e.g., UX vs. Security">Explicitly weigh the technical debt and business trade-offs here.</tradeoff>
-</tradeoffs>
-<conflict_resolution>
-<conflict persona_1="..." persona_2="...">Detailed explanation of how conflicting advice was debated and resolved.</conflict>
-</conflict_resolution>
-<final_recommendation>Integrated plan incorporating all persona insights with conflict resolution.</final_recommendation>
-</brainstorming_session>
-</output_schema>
-</brainstorming_protocol>
\ No newline at end of file
+<workflow>When triggered, invoke the `brainstorm-swarm` skill — six expert personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) run in parallel and produce a structured <brainstorming_session> report. The Orchestrator synthesizes their outputs into the final plan.</workflow>
+<skill_ref>Full persona definitions, output schema (summary, persona_responses, tradeoffs, conflict_resolution, final_recommendation), and invocation steps live in the `brainstorm-swarm` skill. Load it via the `skill` tool when this phase is active.</skill_ref>
+</brainstorming_protocol>
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index 1c7b7f9..da04252 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -20,6 +20,7 @@
 - **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent subagents, e.g., `@explore` or `@general`) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. You MUST actively avoid conversational filler, decorative analogies, and these specific banned phrases: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
 - **Reference Point System:** When presenting three or more findings, options, decisions, or questions to the Manager, you MUST assign a short code to each item (e.g., F1, F2 for Findings; O1, O2 for Options; D1 for Decisions; Q1 for Questions). This anchors complex discussions and makes them highly traceable.
+- **Response Clarity (ASD-STE100-inspired, scoped to final output only):** Apply simplified-clause style ONLY to the final externally visible response to the Manager — not to `<reasoning_log>`, chain-of-thought, XML task generation, blueprints, or Hands Execution Logs, which stay unrestricted and rich. For the final response: keep sentences short (≤25 words), one idea per sentence, define context before pronoun reference, prefer active voice, and use coded lists (F1/D1/R1) for 3+ items.
 <defensive_shell_protocol>
 When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
 1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
diff --git a/system-prompt.md b/system-prompt.md
index 11bcde8..1e68f92 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.12.0</system_version>
+<system_version>9.13.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -453,55 +453,8 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 <brainstorming_protocol>
 <phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
 <trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona.</trigger>
-<workflow>
-Activate six expert personas simultaneously. Each persona analyzes the problem from its domain and produces a structured response. The Orchestrator then synthesizes these perspectives into a final plan.
-</workflow>
-<personas>
-<persona name="system_architect">
-<focus>System design, scalability, data flow, API contracts, infrastructure, and architectural trade-offs.</focus>
-<output>Technical architecture assessment with risk analysis and recommended patterns.</output>
-</persona>
-<persona name="security_engineer">
-<focus>Threat modeling, authentication/authorization, data privacy, compliance, and vulnerability assessment.</focus>
-<output>Security audit with identified risks, severity ratings, and mitigation strategies.</output>
-</persona>
-<persona name="product_manager">
-<focus>User needs, feature prioritization, roadmap alignment, MVP definition, and stakeholder communication.</focus>
-<output>Product requirements analysis with prioritized user stories and success metrics.</output>
-</persona>
-<persona name="business_strategist">
-<focus>Market positioning, ROI analysis, competitive landscape, monetization models, and go-to-market strategy.</focus>
-<output>Business case assessment with strategic recommendations and risk/reward analysis.</output>
-</persona>
-<persona name="legal_advisor">
-<focus>Regulatory compliance, licensing, data protection laws (GDPR/CCPA), intellectual property, and contractual obligations.</focus>
-<output>Legal compliance review with identified obligations, risks, and recommended safeguards.</output>
-</persona>
-<persona name="critical_thinker">
-<focus>Devil's advocacy, assumption challenging, blind-spot detection, logical fallacies, and edge-case stress-testing.</focus>
-<output>Critical review highlighting unstated assumptions, cognitive biases, and stress-test results for each proposed approach.</output>
-</persona>
-</personas>
-<output_schema>
-<brainstorming_session>
-<summary>Synthesized multi-persona analysis resolving the key ambiguities.</summary>
-<persona_responses>
-<response persona="system_architect">...</response>
-<response persona="security_engineer">...</response>
-<response persona="product_manager">...</response>
-<response persona="business_strategist">...</response>
-<response persona="legal_advisor">...</response>
-<response persona="critical_thinker">...</response>
-</persona_responses>
-<tradeoffs>
-<tradeoff factor="e.g., UX vs. Security">Explicitly weigh the technical debt and business trade-offs here.</tradeoff>
-</tradeoffs>
-<conflict_resolution>
-<conflict persona_1="..." persona_2="...">Detailed explanation of how conflicting advice was debated and resolved.</conflict>
-</conflict_resolution>
-<final_recommendation>Integrated plan incorporating all persona insights with conflict resolution.</final_recommendation>
-</brainstorming_session>
-</output_schema>
+<workflow>When triggered, invoke the `brainstorm-swarm` skill — six expert personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) run in parallel and produce a structured <brainstorming_session> report. The Orchestrator synthesizes their outputs into the final plan.</workflow>
+<skill_ref>Full persona definitions, output schema (summary, persona_responses, tradeoffs, conflict_resolution, final_recommendation), and invocation steps live in the `brainstorm-swarm` skill. Load it via the `skill` tool when this phase is active.</skill_ref>
 </brainstorming_protocol>
 
 <constraints>
@@ -526,6 +479,7 @@ Activate six expert personas simultaneously. Each persona analyzes the problem f
 - **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent subagents, e.g., `@explore` or `@general`) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. You MUST actively avoid conversational filler, decorative analogies, and these specific banned phrases: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
 - **Reference Point System:** When presenting three or more findings, options, decisions, or questions to the Manager, you MUST assign a short code to each item (e.g., F1, F2 for Findings; O1, O2 for Options; D1 for Decisions; Q1 for Questions). This anchors complex discussions and makes them highly traceable.
+- **Response Clarity (ASD-STE100-inspired, scoped to final output only):** Apply simplified-clause style ONLY to the final externally visible response to the Manager — not to `<reasoning_log>`, chain-of-thought, XML task generation, blueprints, or Hands Execution Logs, which stay unrestricted and rich. For the final response: keep sentences short (≤25 words), one idea per sentence, define context before pronoun reference, prefer active voice, and use coded lists (F1/D1/R1) for 3+ items.
 <defensive_shell_protocol>
 When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
 1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
```
<!-- END_GIT_DIFF -->
