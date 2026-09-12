---
created_at: '2026-09-11T00:00:00+00:00'
status: active
tags: []
updated_at: '2026-09-11T00:00:00+00:00'
---

# Manual QA + Review Cycle (Hands role-plays both)

Trigger phrase: **"run the QA-review cycle from memory"** (or: چرخه QA و ریویو).

When a task implementation is complete and staged, the Hands manually play
both roles in sequence — no persona servers needed. Stay in the QA loop
until pass, then run review once.

## Step 1 — QA Engineer (loop until pass)

1. Read the changed code/docs from disk (never trust memory of the edit).
2. Adversarial checks: every workflow parameter exists in the tool
   definitions; repo/global copies in sync where required; template
   intact; Acceptance Criteria boxes honestly match recorded evidence;
   no contradictions with existing rules (N vs NOT-N scan).
3. Verdict `QA_PASSED` (list any low-severity notes) or `QA_REJECTED`
   with concrete findings.
4. On rejection: fix, re-verify, re-stage, and repeat Step 1 until pass.
   Never advance to review with open findings.

## Step 2 — Code Reviewer (one pass after QA passes)

1. Re-read the reviewer standards (AGENTS.md guardrails, conventions,
   loaded stack skills).
2. Standards audit: scope discipline (no creep), docs sync (CHANGELOG
   where required), lint green, staging via MCP tool, no forbidden
   operations.
3. Verdict `REVIEW_PASSED` (accept as-is or with noted nits) or
   `REVIEW_REJECTED` (sends back to implementation, then Step 1 again).

## Step 3 — Report to Manager

Short human-readable summary: QA verdict + review verdict + what was
checked. Then the standard task handoff line. Never claim completion
without the evidence above.
