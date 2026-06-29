# Task 18: Cognitive Language Rules & Future Roadmap

**Type:** improvement
**Status:** closed

## Goal

Enforce English-only cognitive reasoning and execution logging across both AI Studio and OpenCode, and append the future architectural TODOs to README.md.

## Manager's Notes

- Bump system version to 5.11.0 in system-prompt.md.
- Add "MUST be written in English" to the visible reasoning step 10.
- Add "All technical reasoning and logs MUST be written in English" to the documentation_phase template.
- Add a new "Cognitive Language Rule" constraint in `<constraints>`.
- Append 4 roadmap items to README.md.

## Local TODOs

- [x] Create Task 18 file
- [x] Bump system-prompt.md version to 5.11.0
- [x] Update visible reasoning step 10 to require English
- [x] Update documentation_phase template to require English
- [x] Add Cognitive Language Rule constraint
- [x] Append Architectural Roadmap to README.md
- [x] Update CHANGELOG.md
- [ ] Call custom_context_stage_and_inject_diff MCP tool

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

This task introduces a formal **Cognitive Language Rule** that enforces English as the sole language for all internal reasoning, blueprints, task generation, and execution logs. This prevents multilingual fragmentation in agentic workflows where different parts of the system might inadvertently mix languages, creating parsing issues and context confusion.

### Execution Notes

- Edited `system-prompt.md` — bumped to 5.11.0, updated step 10 and documentation_phase, added Cognitive Language Rule constraint.
- Appended 4 Future Architectural Roadmap items to `README.md`.
- Updated `CHANGELOG.md` with a new [Unreleased] entry.
- Created `tasks/18-cognitive-language-and-roadmap.md` as the active task file.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e3082d3..490f488 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -128,6 +128,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Reviewer-Driven Commit Cycle:** Code Reviewer persona now generates commit tasks on `APPROVED` status and fix-loop implementation tasks on `REJECTED_NEEDS_FIXES` status, completing the review loop.
 - **6-Step Execution Workflow:** Replaced the old linear 5-step workflow with a loop: Implement & Inject → Team Review → Fix Loop → Commit & Close.
 - **Audit-Agents ZAC Propagation:** Updated `skill-templates/audit-agents/SKILL.md` to enforce the Zero-Autonomous-Commit (ZAC) workflow in newly scaffolded or audited projects — ZAC criterion added to both Target Audit Criteria blocks, Git guardrails added to the AGENTS.md template, and End-Of-Task Sequence updated.
+- **Cognitive Language Rule:** Enforced English-only cognitive reasoning and execution logging across both AI Studio (reasoning_log, blueprints, task generation) and OpenCode (execution logs). Appended future architectural TODOs to README.md.

 ### Changed

diff --git a/README.md b/README.md
index 92fef56..9babf10 100644
--- a/README.md
+++ b/README.md
@@ -202,3 +202,10 @@ To make the `code-search` skill (or any other reusable skill) available in _ever
 ## Contributing

 See `.opencode/skills/sop-maintenance/SKILL.md` for the rules that AI agents must follow when modifying this repository.
+
+## Future Architectural Roadmap (TODOs)
+
+1. **Automated Pull Request Integration:** Upgrade the final Code Reviewer step to automatically branch, commit, and open a PR via GitHub CLI (`gh pr create`) instead of committing locally to `main`.
+2. **Epic and Milestone Tracking:** Create an `epics/` directory and update the `task-generator` skill to link individual tasks to parent epics for better macro-level project tracking.
+3. **Dedicated `testing-strategy` Skill:** Create a template enforcing Test-Driven Development (TDD) or strict coverage thresholds, ensuring OpenCode writes tests before or alongside implementation code.
+4. **Database Migration Management:** Create a `database-migration` skill to strictly forbid direct schema alterations, forcing the use of standard migration tools (Prisma, Alembic, Flyway) for safe, repeatable deployments.
diff --git a/system-prompt.md b/system-prompt.md
index 42a68a8..ce04117 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>5.10.0</system_version>
+<system_version>5.11.0</system_version>

 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
@@ -65,7 +65,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
 7. Completeness: Ensure all requirements, constraints, and options are exhaustively incorporated into your plan.
 8. Persistence and patience: Do not give up unless all reasoning is exhausted.
 9. Inhibit your response: Only output your final architectural plan or task block AFTER all the above reasoning is completed internally.
-10. Visible reasoning (Critical): Since you rely on token generation to reason effectively, you MUST NOT keep these 9 steps hidden. Before outputting any template or final response, you MUST output a <reasoning_log> block where you write down your analysis for steps 1–9. ONLY AFTER closing the </reasoning_log> tag are you allowed to output the task blocks or talk to the Manager.
+10. Visible reasoning (Critical): Since you rely on token generation to reason effectively, you MUST NOT keep these 9 steps hidden. Before outputting any template or final response, you MUST output a <reasoning_log> block where you write down your analysis for steps 1–9. This entire reasoning log MUST strictly be written in English. ONLY AFTER closing the </reasoning_log> tag are you allowed to output the task blocks or talk to the Manager.
     </agentic_reasoning>

 <opencode_protocols>
@@ -124,7 +124,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
   </bash_phase>

   <documentation_phase>
-    OPENCODE INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "OpenCode Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. Check off any local TODOs.     3) You MUST update `CHANGELOG.md` with a new entry following the project's versioning rules.
+    OPENCODE INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "OpenCode Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs.     3) You MUST update `CHANGELOG.md` with a new entry following the project's versioning rules.
   </documentation_phase>

   <summary_phase>
@@ -152,6 +152,7 @@ During Phase 0, the Planner will launch up to 4 parallel subagent tasks to deepl
    </execution_workflow>

 <constraints>
+- **Cognitive Language Rule:** All internal reasoning, architectural blueprints, XML task generation, and OpenCode execution logs MUST always be written in English. You may only use a localized language for direct conversational responses to the Manager if explicitly requested.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<OpenCode: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
 - **Tone and Demeanor**: Keep your responses highly professional, objective, and analytical. Do not use superlatives.
```

<!-- END_GIT_DIFF -->
