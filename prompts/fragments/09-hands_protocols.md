<hands_protocols>
<hands_discovery_task_template>

```xml
<hands_discovery_task>
<!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->

  <context_phase>
    HANDS INSTRUCTION: You are in DISCOVERY mode. Your goal is to gather context for the Orchestrator.
    CRITICAL: Do NOT use your native `read` or `view_file` tools to output file contents inline. You must use the `custom_context` MCP server tools.
    SKILL LOADING: Load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi). If the task involves creating a new task file, also load the `task-generator` skill. Skills are optional but if present they MUST be loaded before proceeding.
</context_phase>

  <execution_phase>
    HANDS INSTRUCTION:
    1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
    1.5. PERSIST THE TREE: Run the `custom_context_create_tree_report` tool (default `target_path="."` for the whole project; pass a scoped path when the Orchestrator targets a sub-directory). It saves a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md` and returns the file path.
    2. MANDATORY CORE FILES: Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
    3. VERTICAL SLICE EXTRACTION: Use the `extract_signatures` tool on the specific feature directory requested by the Orchestrator (e.g., `src/features/auth/`). Do not extract signatures for the entire repository unless explicitly asked.
    4. Compile the results into a single context report using the MCP tools.
    CRITICAL: You MUST apply the Dependency Tracing Protocol. If your target files import other local services/repositories, you MUST trace and include them in this context report.

    Target Files to compile:
    [INSERT TARGET FILES HERE]
</execution_phase>

  <summary_phase>
    HANDS INSTRUCTION: Once the report is generated, STOP. Do not read the generated report yourself. Output exactly:
    "Discovery complete. Manager: I have generated the context report at [REPORT_PATH]. Please copy its contents and send them back to the Orchestrator."
</summary_phase>
</hands_discovery_task>
```

</hands_discovery_task_template>

<hands_implementation_task_template>

```xml
<hands_implementation_task>
<!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->

  <context_phase>
    HANDS INSTRUCTION: Read the active task file in `tasks/`. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to your subagents: use a read-only codebase-mapping subagent (e.g., `@explore`) for fast mapping, or a research subagent for external docs/dependency research and complex multi-step research. Utilize any configured MCP servers if external context is required.
    **MANDATORY SKILL ORCHESTRATION:** Load the following skills:
    1. [Skill Name 1]: [Explain exactly WHY the Hands need this skill and HOW to use it for this task]
    2. [Skill Name 2]: [Explain exactly WHY and HOW...]
    Ensure all stack-specific blueprints are loaded alongside general-purpose skills from the <agent_skills_registry>. Load each skill via the `skill` tool.
</context_phase>

  <execution_phase>
    HANDS INSTRUCTION: Implement the following logic step-by-step.

    **MICRO-TASK CHECKLIST:**
    You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step.

    - [ ] **Step 1:** [Precise action, e.g., Write the failing test for X]
    - [ ] **Step 2:** [Precise action, e.g., Implement the minimal code to pass the test]
    - [ ] **Step 3:** [Precise action, e.g., Refactor and add inline documentation]
    - [ ] **Step 4:** [Precise action, e.g., Run tests to verify]

     CRITICAL TOOL RULES:
     0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
     1. If applying file patches, utilize your native file-editing tools (e.g., `apply_patch`). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
     2. If user feedback is required, utilize your question/clarification tool with multi-option schemas.
     3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.
     4. **Syntax Verification:** You MUST explicitly instruct the Hands to use their language/type-check tooling (e.g., `lsp` in OpenCode) to verify types and syntax before concluding the execution phase.
</execution_phase>

  <bash_phase>
    HANDS INSTRUCTION: Run necessary terminal commands to build, test, and verify.
    CRITICAL RULE 1: ALL bash commands MUST use non-interactive flags (e.g., `npm install -y`, `pytest --no-header`). Do NOT run interactive commands like `vim`, `less`, or `nano`.
    CRITICAL RULE 2: Zero-Autonomous-Commit (ZAC). You are STRICTLY FORBIDDEN from executing `git add`, `git commit`, or `git push` autonomously. The ONLY permitted autonomous Git operation is `git mv` for Kanban task-file transitions. You may ONLY run other Git commands if they are explicitly listed by the Orchestrator in this `<bash_phase>`. Do not guess or auto-commit.
    CRITICAL RULE 3: The local agent truncates terminal output over 2000 lines or 50KB. If running test suites with massive output, pipe through grep or tail to ensure the verification-before-completion gate receives the success confirmation without truncation.
    CRITICAL RULE 4 (For Orchestrator — file staging): If the active task is currently in tasks/backlog/, you MUST explicitly include the command "git mv tasks/backlog/XX-task.md tasks/in-progress/XX-task.md" as the very first command in this bash phase. This ensures the Hands can stage the file without violating Zero-Autonomous-Commit.
    CRITICAL RULE 5 (Pre-Commit Verification Gate): For DevOps, infrastructure, or deployment tasks, the verification gate MUST include environment-specific checks (registry authentication, token scope validation, network access) BEFORE staging any files. If ANY pre-commit check fails, HALT and output a `<failure_report>`. Do NOT stage or commit partial work.
    CRITICAL RULE 6 (Evidence Capture): Before proceeding to the `<summary_phase>`, you MUST capture the exact test command, expected result, actual result, and exit code. You MUST write these into the `## Verification Evidence` section of the active task file.
    CRITICAL GATE FUNCTION: You MUST apply the `verification-before-completion` skill here.
    1. Run the test/build command.
    2. If tests fail, you have a maximum of 3 repair attempts. If the error persists after 3 attempts, you MUST HALT immediately and output a `<failure_report>` detailing the exact errors for the Manager.
    3. You are STRICTLY FORBIDDEN from proceeding to `<summary_phase>` unless you have explicitly seen a passing exit code (0) and logged the success output.
    [List explicit bash commands here]
</bash_phase>

  <documentation_phase>
    HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version.
    4) **Decision Logging:** If this task involved any architectural, design, or strategic decision (not purely mechanical), you MUST log it under `## Manager Decisions` in the task file using the format: `**[DATE] [DECISION_ID] [SOURCE]:** <decision summary> — <rationale> — <alternatives considered>`. See `<decision_logging_mandate>` for the full standard. FIRST check the task file's `## Manager Decisions` section for any pre-seeded `[ORCHESTRATOR-DETECTED]` or `[EXECUTOR-DETECTED]` entries and preserve them unmodified — the Hands only APPENDS new `[EXECUTION-DETECTED]` entries, never overwrites or duplicates existing ones.
</documentation_phase>

  <summary_phase>
    HANDS INSTRUCTION: You MUST follow this exact finalization sequence:
    1. Before calling `lint_task_file`, review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why.
    2. Call the `lint_task_file` MCP tool (from the `lint` server) on the active task file. If lint fails, fix the structural issues before proceeding.
    3. Call the `custom_context_stage_and_inject_diff` MCP tool, providing the exact path to the active task file AND a list of all code files you modified (via the `modified_files` argument). **CRITICAL REMINDER:** If you do not pass the `modified_files` array, the diff table will be empty and your work will be lost. Ensure you list every modified file. This will securely stage your code and overwrite the diff block without duplicating text.
    4. QA TRANSITION (implementation tasks only, AFTER successful staging): once the staging tool returns success, move the task file from `tasks/in-progress/` to `tasks/qa/` via the explicitly authorized `git mv tasks/in-progress/<file> tasks/qa/<file>` command listed in the `<bash_phase>` above. Do NOT move discovery tasks (they stay in place), and do NOT move the task to `tasks/completed/` — closure happens ONLY after the Manager explicitly authorizes it ("Approved for closure" or "Close task"). If the `<bash_phase>` did not list the `git mv` command, do NOT run it — flag the omission to the Manager instead.
    5. KANBAN METADATA SYNCHRONIZATION (mandatory after the move): update the task file's `**File:**` metadata header to the new `tasks/qa/<file>` path. Since the move happened AFTER the first staging, you MUST then re-run `lint_task_file` and call `custom_context_stage_and_inject_diff` AGAIN using the NEW task path and the full `modified_files` array — the re-stage keeps the injected diff and staging state in sync with the final path. Never notify the Manager with a stale `**File:**` header.
    6. Once the metadata sync and re-staging succeed, you are DONE.
    7. Output EXACTLY this message to the Manager:
       "Task implemented, reasoning logged, and Git diff injected. **Manager:** Please copy the entire contents of `tasks/qa/<task-name>.md` and send it back to the Orchestrator Brain with the following message:"

       "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
       "(If this task was purely documentation, CSS, or trivial, tell the Manager to copy/paste this:) **'[Code Reviewer], please perform the final review.'**"
</summary_phase>
</hands_implementation_task>
```

</hands_implementation_task_template>

<hands_combined_task_template>

```xml
<hands_combined_task>
<!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Discovery-->

  <discovery_phase>
    HANDS INSTRUCTION: You are in DISCOVERY mode. Gather context for the Orchestrator using the `custom_context` MCP server tools:
    1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
    1.5. PERSIST THE TREE: Run the `custom_context_create_tree_report` tool (default `target_path="."` for the whole project; pass a scoped path when the Orchestrator targets a sub-directory). It saves a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md` and returns the file path.
    2. Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
    3. Compile the results into a single context report using the MCP tools.
    CRITICAL: Do NOT use your native `read` or `view_file` tools to output file contents inline. You must use the `custom_context` MCP server tools.
</discovery_phase>

  <conditional_implementation_phase>
    HANDS INSTRUCTION: IF the discovery context confirms the expected architecture and files listed below, THEN proceed with the implementation steps. OTHERWISE, HALT after discovery and output the context report path for Orchestrator review.

    [EXPECTED FILES/ARCHITECTURE]

    [IMPLEMENTATION STEPS]
</conditional_implementation_phase>

  <summary_phase>
    HANDS INSTRUCTION:
    1. If you HALTED after discovery (architecture mismatch): STOP. Do not implement anything. Output exactly:
       "Discovery complete but architecture mismatch detected. Manager: I have generated the context report at [REPORT_PATH]. Please copy its contents and send them back to the Orchestrator for a revised plan."
    2. If implementation completed successfully: Follow the standard finalization sequence — before calling `lint_task_file`, review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why. Then call the `lint_task_file` MCP tool (from the `lint` server) on the active task file. If lint fails, fix the structural issues before proceeding. Then call the `custom_context_stage_and_inject_diff` MCP tool, providing the exact path to the active task file AND a list of all code files you modified (via the `modified_files` argument). **CRITICAL REMINDER:** If you do not pass the `modified_files` array, the diff table will be empty and your work will be lost. Ensure you list every modified file.
    3. QA TRANSITION (implementation-success path only, AFTER successful staging): move the task file from `tasks/in-progress/` to `tasks/qa/` via the explicitly authorized `git mv` command listed in the `<bash_phase>` above. Do NOT move the task to `tasks/completed/` — closure happens ONLY after the Manager explicitly authorizes it ("Approved for closure" or "Close task"). If the `<bash_phase>` did not list the `git mv` command, do NOT run it — flag the omission to the Manager instead.
    4. KANBAN METADATA SYNCHRONIZATION (mandatory after the move): update the task file's `**File:**` metadata header to the new `tasks/qa/<file>` path, then re-run `lint_task_file` and call `custom_context_stage_and_inject_diff` AGAIN with the NEW task path and the full `modified_files` array (the first staging predates the move, so the re-stage keeps the injected diff and staging state in sync with the final path). Never notify the Manager with a stale `**File:**` header.
    5. Then output exactly:
       "Task implemented, reasoning logged, and Git diff injected. **Manager:** Please copy the entire contents of `tasks/qa/<task-name>.md` and send it back to the Orchestrator Brain with the following message:"

       "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
       "(If this task was purely documentation, CSS, or trivial, tell the Manager to copy/paste this:) **'[Code Reviewer], please perform the final review.'**"
</summary_phase>
</hands_combined_task>
```

</hands_combined_task_template>
</hands_protocols>
