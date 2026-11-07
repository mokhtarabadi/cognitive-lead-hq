<hands_protocols>
<hands_discovery_task_template>

```xml
<hands_discovery_task>
<!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->

  <context_phase>
    HANDS INSTRUCTION: You are in DISCOVERY mode. Your goal is to gather context for the Orchestrator.
    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools.
    SKILL LOADING: Load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, node-hexagonal-api, python-fastapi). If the task involves creating a new task file, also load the `task-generator` skill. Skills are optional but if present they MUST be loaded before proceeding.
</context_phase>

  <execution_phase>
    HANDS INSTRUCTION: Execute the discovery protocol from `cognitive-executor` agent. Gather context using the `custom_context` MCP tools (directory tree, tree report, read source files, extract signatures, graph tools). Apply the Dependency Tracing Protocol. Compile the results into a single context report.

    Target Files to compile:
    [INSERT TARGET FILES HERE]
</execution_phase>

  <summary_phase>
    HANDS INSTRUCTION: Once the report is generated, STOP. Do not implement anything. Output the discovery findings along with the machine-readable manifest from the report, preserving its exact structure: `### Context Manifest`, then `Context-Paths:`, then one `- path/to/file.ext#Lstart-end` entry per path. If chaining to Brain planning, feed these paths directly via `brain_turn(context_paths=[...])` under the active session thread; the Manager never ferries context.
</summary_phase>
</hands_discovery_task>
```

</hands_discovery_task_template>

<hands_implementation_task_template>

```xml
<hands_implementation_task>
<!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->

  <context_phase>
    HANDS INSTRUCTION: Read the active task file in `tasks/`. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to your subagents: use the read-only `cognitive-discovery` subagent for fast mapping, or a research subagent for external docs/dependency research and complex multi-step research. Utilize any configured MCP servers if external context is required.
    **MANDATORY SKILL ORCHESTRATION:** Load the following skills:
    1. [Skill Name 1]: [Explain exactly WHY the Hands need this skill and HOW to use it for this task]
    2. [Skill Name 2]: [Explain exactly WHY and HOW...]
    Ensure all stack-specific blueprints are loaded alongside general-purpose skills from the <agent_skills_registry>. Load each skill via the `skill` tool.
</context_phase>

  <execution_phase>
    HANDS INSTRUCTION: Implement the following logic step-by-step.

    **ORCHESTRATOR AUTHORING RULE (comprehensive, executable XML):** Every `<hands_implementation_task>` MUST be a complete executable handoff. Each checklist step names the exact file path and the exact operation. Every file change carries the complete code sample or unified diff the Hands must apply. Every command is written out in full with exact flags and working directory. Every skill is named with one line saying why the Hands need it. Every step states its verification command and expected result, and acceptance criteria plus edge cases are explicit. Pre-make every decision the approved plan already contains and leave no step ambiguous. **PLACEHOLDER BAN:** No `[bracketed placeholder]` may survive in the emitted XML. The Hands may question the Manager ONLY for information that exists nowhere in the plan or repo. placeholder-only instructions are forbidden — every step MUST be concrete. omitted code are forbidden.

    **MICRO-TASK CHECKLIST:**
    You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step. When the checklist has 2 or more steps, you MUST also track them as a micro-list (todo list) alongside the task file.

    - [ ] **Step 1:** [Precise action]
    - [ ] **Step 2:** [Precise action]
    - [ ] **Step 3:** [Precise action]
    - [ ] **Step 4:** [Precise action]

    HANDS INSTRUCTION: Follow the critical tool rules, documentation rule, syntax verification, and living-folder-docs sync from `cognitive-executor` agent. The Hands owns the full rule text.
</execution_phase>

  <bash_phase>
    HANDS INSTRUCTION: Run necessary terminal commands to build, test, and verify. Follow the bash protocol, ZAC rules, evidence capture, and strict tooling gate from `cognitive-executor` agent.
    [List explicit bash commands here]
</bash_phase>

  <documentation_phase>
    HANDS INSTRUCTION: Update the local project documentation per the documentation rule and living-folder-docs sync in `cognitive-executor` agent.
</documentation_phase>

  <summary_phase>
    HANDS INSTRUCTION: Follow the finalization sequence in `cognitive-executor` agent. Output EXACTLY this message:
     1. Output EXACTLY this message to the Manager:
       "Task implemented, reasoning logged, Git diff injected, and QA/review chained via `brain_turn`."
</summary_phase>
</hands_implementation_task>
```

</hands_implementation_task_template>

<hands_combined_task_template>

```xml
<hands_combined_task>
<!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Discovery-->

  <discovery_phase>
    HANDS INSTRUCTION: You are in DISCOVERY mode. Gather context for the Orchestrator using the `custom_context` MCP server tools (directory tree, tree report, read source files, graph tools). Follow the discovery protocol in `cognitive-executor` agent. Do NOT use your native `read` tool to output file contents inline.
</discovery_phase>

  <conditional_implementation_phase>
    HANDS INSTRUCTION: IF the discovery context confirms the expected architecture and files listed below, THEN proceed with the implementation steps. OTHERWISE, HALT after discovery and invoke a revised-plan `brain_turn` yourself with the discovery manifest via `context_paths=[...]` for Orchestrator review.

    [EXPECTED FILES/ARCHITECTURE]

    [IMPLEMENTATION STEPS]

    HANDS INSTRUCTION: Follow the implementation protocol in `cognitive-executor` agent for tool calls, verification gates, and finalization.
</conditional_implementation_phase>

  <summary_phase>
    HANDS INSTRUCTION:
    1. If you HALTED after discovery (architecture mismatch): STOP. Do not implement anything. First invoke a revised-plan `brain_turn` yourself under the active session thread, feeding the discovery report manifest via `context_paths=[...]`; then output exactly:
       "Discovery complete but architecture mismatch detected. Revised-plan `brain_turn` chained with the discovery manifest."
    2. If implementation completed successfully: Follow the standard finalization sequence — before calling `lint_task_file`, review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why. Then call the `lint_task_file` MCP tool (from the `lint` server) on the active task file. If lint fails, fix the structural issues before proceeding.
     2b. Parallel check: inspect `git diff --cached --name-only` (read-only). If files outside your task are staged, call `custom_context_unstage_files` with exactly those files first — never stage or carry another task's files.
     3. Execute the atomic QA transition:
       Call the `custom_context_qa_transition` MCP tool with:
       - `task_file_path`: "tasks/in-progress/<task-name>.md"
       - `modified_files`: [<modified_file_1>, <modified_file_2>, ...]
       This atomically moves the task file to `tasks/qa/`, updates the `**File:**` header, stages your modified code, and injects the git diff in one operation.
     4. The Hands invokes the QA/review `brain_turn` itself in both manual and automatic modes under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text.
     5. Then output exactly:
       "Combined task complete: discovery verified, implementation applied, Git diff injected, and QA/review chained via `brain_turn`."
     6. After the QA/review `brain_turn` is invoked and the exact completion message is output, you are DONE.
</summary_phase>
</hands_combined_task>
```

</hands_combined_task_template>

</hands_protocols>