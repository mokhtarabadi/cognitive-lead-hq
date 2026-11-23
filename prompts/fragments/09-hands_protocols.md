<hands_protocols>
<hands_discovery_task_template>

```xml
<hands_discovery_task>
<!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->

  <context_phase>
    HANDS INSTRUCTION: You are in DISCOVERY mode. Your goal is to gather context for the Orchestrator.
    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools. Skill loading is owned by the Hands per the executor; discovery subagents have no `skill` tool.
</context_phase>

  <execution_phase>
    HANDS INSTRUCTION: Execute the discovery protocol from `cognitive-executor` agent. Gather context using the `custom_context` MCP tools (directory tree, tree report, read source files, extract signatures, graph tools). Apply the Dependency Tracing Protocol. Compile the results into a single context report.

    Target Files to compile:
    [INSERT TARGET FILES HERE]
</execution_phase>

  <summary_phase>
    HANDS INSTRUCTION: Once the report is generated, STOP. Do not implement anything. Output the discovery findings along with the machine-readable manifest from the report, preserving its exact structure: `### Context Manifest`, a `Tree:` line naming the persisted tree report, then `Context-Paths:`, then one `- path/to/file.ext#Lstart-end` entry per path. The `Tree:` value is what fills the `tree=<path>` slot of this turn's audit line. Feed these paths directly via `brain_turn(context_paths=[...])` under the active session thread; the Manager never ferries context.
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
    Ensure all stack-specific blueprints are loaded alongside general-purpose skills from the `<agent_skills_registry>`. Load each skill via the `skill` tool.
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
    HANDS INSTRUCTION: Follow the finalization sequence in `cognitive-executor` agent.
    1. Review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why.
    2. Execute the atomic QA transition: move task file to `tasks/qa/` via `custom_context_qa_transition`.
    3. The Hands invokes the QA/review `brain_turn` itself under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text. In autopilot, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text.
    4. Output EXACTLY this message to the Manager:
       "Task implemented, reasoning logged, Git diff injected, and QA/review chained via `brain_turn`."
    5. After the QA/review `brain_turn` is invoked and the exact completion message is output, you are DONE.
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
     4. The Hands invokes the QA/review `brain_turn` itself under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text. In autopilot, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text.
     5. Then output exactly:
       "Combined task complete: discovery verified, implementation applied, Git diff injected, and QA/review chained via `brain_turn`."
     6. After the QA/review `brain_turn` is invoked and the exact completion message is output, you are DONE.
</summary_phase>
</hands_combined_task>
```

</hands_combined_task_template>

<worked_examples>

Both examples below are prompt text rather than emitted tasks, so their outer blocks are shown unwrapped. When you emit a task whose body itself carries a fenced code block, as the second example's body does, wrap the outer block in four backticks so the inner fence survives parsing.

Example A, a three-step documentation task, shown complete:

<hands_implementation_task>

<validation_phase>

HANDS INSTRUCTION (MANDATORY FIRST STEP):

1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.

2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.

3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.

4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.

5. If no violations are found, proceed to the Context Phase.

BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.

</validation_phase>

<context_phase>

HANDS INSTRUCTION: Load the `kanban-lifecycle` skill. This task edits documentation only. Skip record: repo root is the project root, marker scan list is `build.gradle.kts, pyproject.toml, package.json`, matched skills list is empty, reason phrase is documentation-only change with no stack marker.

</context_phase>

<execution_phase>

- [ ] **Step 1:** In `docs/setup.md` under `## Prerequisites`, add the bullet `- Node.js 20 or newer`. Verify `grep -n "Node.js 20 or newer" docs/setup.md` returns exactly one line.

- [ ] **Step 2:** In `docs/setup.md` under `## Install`, add the bullet `- Run pnpm install once after cloning.`. Verify `grep -n "pnpm install once" docs/setup.md` returns exactly one line.

- [ ] **Step 3:** Update `CHANGELOG.md` by Parse-Then-Append with one entry naming `docs/setup.md`. Verify `grep -c "docs/setup.md" CHANGELOG.md` returns 1 or more.

</execution_phase>

<summary_phase>

HANDS INSTRUCTION: Record all three grep commands with their exit codes in `## Verification Evidence`. Stage nothing until every one is green.

</summary_phase>

</hands_implementation_task>

Example B, a five-step code task, shown complete:

<hands_implementation_task>

<validation_phase>

HANDS INSTRUCTION (MANDATORY FIRST STEP):

1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.

2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.

3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.

4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.

5. If no violations are found, proceed to the Context Phase.

BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.

</validation_phase>

<context_phase>

HANDS INSTRUCTION: Load `testing-verification`. The change adds a regression test, and that skill owns the red-first ordering and the evidence gate.

</context_phase>

<execution_phase>

- [ ] **Step 1:** Add `test_notifier_rejects_empty_recipient` to `tests/test_notifier.py`. It asserts that an empty recipient raises `ValueError` naming the field. Run it first and confirm it fails for the missing guard with `rtk test python3 -m pytest tests/test_notifier.py -k test_notifier_rejects_empty_recipient`, expecting exit 1.

- [ ] **Step 2:** Add this guard at the top of the dispatch path, including its docstring explaining why the guard sits at the boundary:

```python
def require_recipient(recipient: str) -> None:
    """Reject an empty notification recipient.

    An empty recipient reaches the transport and fails there,
    which hides the real cause behind a network error. The
    guard fails loud at the boundary instead.
    """
    if not recipient or not recipient.strip():
        raise ValueError("recipient must not be empty")
```

Verify the guard exists with `grep -n "def require_recipient" src/notifications/dispatcher.py`.

- [ ] **Step 3:** Call `require_recipient(recipient)` as the first statement of `dispatch`. Verify the call sites with `grep -n "require_recipient(" src/notifications/dispatcher.py` and confirm two or more matches.

- [ ] **Step 4:** Run `rtk test python3 -m pytest tests/test_notifier.py -k test_notifier_rejects_empty_recipient` and record exit 0. Then run `rtk test python3 -m pytest tests/test_notifier.py` and record exit 0.

- [ ] **Step 5:** Update `src/notifications/README.md` with one line naming the `require_recipient` guard and append a dated ADR to `src/notifications/DECISIONS.md`. Verify `grep -c "require_recipient" src/notifications/README.md` returns 1 or more.

</execution_phase>

<bash_phase>

Run `rtk test python3 -m pytest tests/test_notifier.py` and record the exit code.

</bash_phase>

<summary_phase>

HANDS INSTRUCTION: Record every command with its exit code in `## Verification Evidence`. Stop at the QA chain.

</summary_phase>

</hands_implementation_task>

</worked_examples>

MANAGER-FACING RENDER CONTRACT: the Hands inherits the full rule from the `cognitive-executor` agent; the Brain must preserve it in every emitted task. Every Manager-facing handoff with 3+ parallel items uses a single `openchamber_render` `ui` program with a `Stack` root. Validate it before sending: exact positional signatures only (`Stack(children: Item[])`, `Table(columns: string[], rows: (string | number)[][])`, `Callout(markdown: string, tone?: string, title?: string)`, `Steps(items: {title: string, markdown?: string, status?: string}[], direction?: string)`), never wrap a `Table` cell in brackets, balance brackets and braces, use one statement per line, and never pass named arguments. Arity-style render diagnostics mean a source defect such as a stray bracket or nested cell, not a renderer bug; fix the source instead of retrying the same program. Build the `openchamber_render` call as `action: "render.page"` with `parameters` as a real object, never a JSON-encoded string: `parameters` starts with `{`, not `"{`, `ui` is one full program string, `html` is only for mockups, and exactly one payload is sent. A `parameters: Expected object` validation error means the envelope was stringified; rebuild the call with an object instead of retrying the same arguments.

CONTEXT MAP FOR 09 TURNS: every `brain_turn` chained from these templates carries one audit line beside the mode line.
Discovery summary (T1): Context-Map: full (tree=<path>, files=<n>).
Implementation summary step 3 (T2): Context-Map: diff-scoped (files=<n>).
Combined conditional phase (T3): Context-Map: full (tree=<path>, files=<n>).
Combined summary halt path (T4): Context-Map: full (tree=<path>, files=<n>).
Combined summary QA chain (T5): Context-Map: diff-scoped (files=<n>).

</hands_protocols>
