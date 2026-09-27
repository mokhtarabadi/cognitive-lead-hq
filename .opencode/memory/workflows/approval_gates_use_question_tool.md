---
created_at: '2026-09-27T05:57:38.146788+00:00'
status: active
tags: []
updated_at: '2026-09-27T05:57:38.148311+00:00'
---

# Approval gates must use the question tool (Manager standing rule 2026-09-27)

Whenever the cognitive executor needs Manager approval — after presenting a plan, after the Code Reviewer accepts code (PO_REVIEW_PENDING relay), or at any other approval gate — it MUST ask through the `question` tool (blocking options), never through plain prose. Reason: the goal plugin keeps the auto-continue loop running, so a prose question gets rolled past instead of answered. This holds in manual and autopilot modes; only hard blockers (missing credentials, Clarification Halt) may use prose. Blanket acknowledgements (ok/yes/looks good/emoji) never count as approval at any gate.