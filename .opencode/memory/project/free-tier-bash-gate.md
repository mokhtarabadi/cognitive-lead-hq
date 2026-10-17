---
created_at: '2026-10-17T06:05:50.448451+00:00'
status: active
tags: []
updated_at: '2026-10-17T06:05:50.448466+00:00'
---

# Free-tier bash gate (upstream OpenCode behavior, recorded 2026-10-17)

Upstream free-tier models classify the caller by the request-body tool list: an agent omitting bash gets 403 FreeTierError. Custom primary agents intended for free-tier use must keep bash in the allowlist; harden with prompts and review, never tool removal. Caveat: restricted subagent shapes can fail even with bash allowed (upstream triaging), so bash is necessary but not sufficient. Enforced by tests/test_agent_tool_gate.py (discovery exempt as read-only deny-by-design) and documented in agents/README.md plus agents/DECISIONS.md.