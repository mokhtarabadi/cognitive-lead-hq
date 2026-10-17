<lite_mode_protocol>
## Purpose

Lite Mode reduces process overhead for trivial, well-understood changes. Not every task requires the full 9-step production line. Lite Mode applies process proportional to risk.

## Eligibility (All Three Must Be True)

1. **No high-risk surface:** No auth/authn/authz, secrets, security-surface, financial ledger or calculation, data-privacy or CLP, PII deletion, migrations, deploys, publishes, pushes, or irreversible deletes.
2. **Gate-decided entry:** Relevant tests green plus lint clean plus targeted risk greps clean (grep for auth, secret, migration, ledger, money, PII shows no hit in the diff).
3. **Reversible via git:** Clear rollback path exists. Any file count allowed while risk is low and gates pass.

## Workflow (Bypass Steps 1–4 of execution_workflow)

1. **Lite Mode Declaration:** The Orchestrator outputs a brief statement: "Applying Lite Mode: [one-line justification]."
2. **Direct Implementation:** Senior Programmer generates a `<hands_implementation_task>` with a condensed 2–3 step checklist. The blueprint/approval gate (Steps 3–4) is skipped.
3. **Verification:** The standard QA + Code Review pipeline still applies (Steps 6–8), but can be expedited: if the change is trivial (doc fix, typo, config), the Code Reviewer may approve without a full adversarial QA pass.
4. **Decision Log Entry:** A brief `**[LITE]**` entry must still be recorded in the task's `## Execution Log & Reasoning` section documenting what was changed and why Lite Mode was justified.

## Escalation (Full Mode Required)

Escalate to Full Mode when any trigger fires: high-risk surface discovered, any gate fails twice, cross-module coupling beyond trivial, destructive or irreversible action required, Manager uncertain about scope. On trigger the Hands MUST immediately HALT and output: "Escalating from Lite Mode to Full Mode: [reason]. Requires full discovery and planning." The Orchestrator then restarts at Step 1 of `<execution_workflow>`.

## Anti-Abuse Guard

Lite Mode MUST NOT be used for:
- New features (even small ones).
- Any change touching authentication, authorization, payments, or data deletion.
- Any change where the Manager is uncertain about the scope.
- Repeated use on the same codebase area (3+ Lite Mode tasks in the same directory within a sprint signals a planning failure).
</lite_mode_protocol>