# Milestone 19 Summary

**Date:** 2026-09-14
**Tasks Compacted:** 5 (209, 210, 219, 227, 228)

## Source Distribution

| Source       | Count |
| ------------ | ----- |
| orchestrator | 1     |
| manager      | 4     |

## Architectural Changes

- Brain planning loop gained discovery-fed context: discovery XML executes before the final plan, the plan cites fed context, and the fed block stays pinned in session history (209).
- Brain turns accept file-path context injection with caps and labels; small pulls inline, big artifacts by path (210).
- Decisions platform unified: Conventional Commits gate, self-improve cross-project issues, manager-decision auto-extraction + detector, Designer-seat planning gate, bridge hotfix-XML extraction, personal decisions repo with pull-on-read/push-on-write sync, migration skill (219 META covering 208 + 211-218).
- Current-work META: issue-8 follow-ups, README roadmap trio (testing-strategy, database-migration, hexagonal Py/TS), executor Personas Roster, numeric task_id gate (227 META covering 220 + 224 + 225 + 226).
- New `opencode-init` skill generates per-project opencode.json (V1-only, ask-gaps, ZAC denies, stdlib validator) (228).

## Files Modified

| File | Change |
| ---- | ------ |
| agents/cognitive-executor.md | Planning Gate, Personas Roster, Seat→Spec Map, goal pause rule |
| mcp-brain-bridge/server.py | hotfix allowlist, xml-fence fallback, numeric task_id gate |
| mcp-context-server/server.py | Conventional Commit gate |
| mcp-decision-server/server.py | provenance fields, pull-on-read/push-on-write sync |
| mcp-decision-server/detector.py | new decision-moment detector |
| skill-templates/manager-decision/SKILL.md | auto-trigger, personal repo, consult + push protocols |
| skill-templates/decision-migration/SKILL.md | new migration skill + smartenings |
| skill-templates/testing-strategy/SKILL.md | new skill (META 224) |
| skill-templates/database-migration/SKILL.md | new skill (META 224) |
| skill-templates/node-hexagonal-api/SKILL.md | new skill (META 224) |
| skill-templates/opencode-init/ | new skill + validator + golden (228) |
| prompts/fragments/ | version 9.35.0, registry, constraints, self-improve, personas |
| system-prompt.md | rebuilt through 9.35.0 |
| LLM.txt | decisions repo onboarding section |
| README.md | roadmap items struck done |
| tests/ | suite 255 → 331 green |

## Criteria Met

| Task | Acceptance Criteria | Status |
| ---- | ------------------- | ------ |
| 209 | Discovery executes before final plan; plan cites fed context; context pinned; no manual ferrying | ✅ Met |
| 210 | Brainstorm verdict recorded; design approved; small pulls inline; server caps injected files | ✅ Met |
| 219 | All 9 bundled criteria (208 + 211-218); suite 314 green; QA + reviewer approved | ✅ Met |
| 227 | All bundled criteria (220 + 224 + 225 + 226); suite 321 green; QA + reviewer approved | ✅ Met |
| 228 | Research complete; Brain-approved plan; skill writes valid opencode.json; suite 331 green | ✅ Met |

## Individual Task Summaries

### Task 209: Discovery-fed Brain planning with session-persistent context

- **Type:** feature
- **Source:** manager
- **Reasoning:** Autopilot under direct order; Brain blueprint first, then implementation from it.

### Task 210: File-path context injection for brain turns

- **Type:** feature
- **Source:** manager
- **Reasoning:** Brainstorm with file-fed context; optional capped path-pull parameter.

### Task 219: Unified decisions-platform sprint META (208, 211-218)

- **Type:** feature
- **Source:** orchestrator
- **Reasoning:** Bundled 9 sources verbatim; implemented 218 sync inside META; QA + reviewer approved; closed with commits.

### Task 227: Current-work META (220 + 224 + 225 + 226)

- **Type:** feature
- **Source:** manager
- **Reasoning:** Bundled 4 sources; QA + reviewer approved with bare numeric task_id; closed with commits.

### Task 228: OpenCode per-project config generator skill

- **Type:** feature
- **Source:** manager
- **Reasoning:** New standalone skill won over extending audit-agents; V1-only validator; two QA hotfix rounds; closed with commits.
