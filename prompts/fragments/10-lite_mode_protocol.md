<lite_mode_protocol>
## Purpose

Lite Mode reduces process overhead for trivial, well-understood changes. Not every task requires the full 9-step production line. Lite Mode applies process proportional to risk.

## Eligibility (All Three Must Be True)

1. **Single-file impact:** The change touches one file (or a config-only change with zero cross-module dependencies).
2. **No security/financial impact:** The change has no authentication, authorization, data privacy, financial calculation, or payment processing implications.
3. **Explicit or obvious simplicity:** Either the Manager explicitly says "just do it" / "quick fix" / "no plan needed", OR the root cause and fix are both obvious and verifiable within one file (e.g., a typo, a doc fix, a config tweak, a missing import).

## Workflow (Bypass Steps 1–4 of execution_workflow)

1. **Lite Mode Declaration:** The Orchestrator outputs a brief statement: "Applying Lite Mode: [one-line justification]."
2. **Direct Implementation:** Senior Programmer generates a `<hands_implementation_task>` with a condensed 2–3 step checklist. The blueprint/approval gate (Steps 3–4) is skipped.
3. **Verification:** The standard QA + Code Review pipeline still applies (Steps 6–8), but can be expedited: if the change is trivial (doc fix, typo, config), the Code Reviewer may approve without a full adversarial QA pass.
4. **Decision Log Entry:** A brief `**[LITE]**` entry must still be recorded in the task's `## Execution Log & Reasoning` section documenting what was changed and why Lite Mode was justified.

## Escalation (Full Mode Required)

If during implementation the Hands discover the change is NOT trivial (e.g., the "single file" edit cascades to other modules, or a hidden dependency surfaces), the Hands MUST immediately HALT and output: "Escalating from Lite Mode to Full Mode: [reason]. Requires full discovery and planning." The Orchestrator then restarts at Step 1 of `<execution_workflow>`.

## Anti-Abuse Guard

Lite Mode MUST NOT be used for:
- New features (even small ones).
- Any change touching authentication, authorization, payments, or data deletion.
- Any change where the Manager is uncertain about the scope.
- Repeated use on the same codebase area (3+ Lite Mode tasks in the same directory within a sprint signals a planning failure).
</lite_mode_protocol>