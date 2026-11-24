---
tags: [architecture, skills, portability]
---

Skill templates are project-agnostic; harness-specific names belong only in an optional profile or deployed-contract wording.

Rule: Skill template bodies must not hard-code harness identifiers (AGENTS.md, DESIGN.md, tasks/, system-prompt.md, custom_context_*) or HQ repository file paths (docs/brain-bridge.md, mcp-brain-bridge/README.md, prompts/stage-manifest.json). Platform concepts may be named; file locations are referenced only as the deployed runbook or deployed stage manifest. Enforced by tests/test_versioning_skill_portability.py and tests/test_brain_orchestration_skill.py. Registry prompt lines must never carry plugin literals.
