  <validation_phase>
    HANDS INSTRUCTION (MANDATORY FIRST STEP):
    1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
    3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
    4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
    5. If no violations are found, proceed to the {{NEXT_PHASE}} Phase.
  </validation_phase>