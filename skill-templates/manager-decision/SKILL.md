---
name: manager-decision
description: Capture per-session manager decisions into a separate learning repo. Extract rulings, redact secrets, consult past decisions, and evolve the manager-AI sample behind a human review gate.
---

# Manager-Decision Skill

## Purpose

Turns each session's manager judgment into training data. Whenever the manager makes a trade-off, ruling, or system-design call, this skill extracts it (verbatim quote + structured decision), redacts secrets, and persists it append-only in the decision store (`.opencode/decisions/` of the current project — every project keeps its OWN manager notes — or any checkout pointed to by `DECISION_REPO_PATH`). Aggregated decisions evolve `samples/manager_profile.md` — the manager-AI sample — one reviewed promotion at a time, until micro-decisions no longer need the real manager.

## When to Invoke (Trigger)

- The manager states a preference, ruling, or architectural call in session ("use X over Y because…", "approved with…", "never do Z").
- A session closes with trade-offs worth preserving (scope cuts, quality-gate verdicts, release calls).
- An agent faces an architectural ambiguity the manager has ruled on before (consult first via `query_manager_decisions`).
- The sample looks stale: new decisions exist that the profile does not reflect (propose evolution).

Primary interface: the `manager_decisions` MCP server (5 tools). This skill is the universal wrapper so agents in ANY project invoke decision capture the same way.

## Extraction Workflow

1. **Source:** `extract_session_decisions(task_id)` reads `tasks/.sessions/{task_id}/transcript.jsonl` and returns candidate objects (verbatim quote + summary/category/rationale/alternatives/tradeoffs). Candidates are UNSCRUBBED — never persist them directly.
2. **Redact:** `record_manager_decision(decision)` runs `sanitize_text` on every free-text field and blocks the write when `verify_clean` fails. Required: API keys (`sk-…`, `ghp_…`, `AIzaSy…`), Bearer tokens, private IPs (`10/8`, `172.16/12`, `192.168/16`), credential assignments.
3. **Persist:** valid records land as `decisions/YYYY/MM/DEC-YYYYMMDD-NNN.json` + matching `.md`, and `decisions/INDEX.md` regenerates. The store is append-only — corrections are new records, never edits.
4. **Verbatim preservation:** the manager's original statement AND its English translation are stored word-for-word alongside the extracted summary. Summarizing away the source is forbidden.

## Consultation Workflow

- Before re-asking the manager, call `query_manager_decisions(query, category?)`. A hit (summary + verbatim quote + rationale) resolves the ambiguity without bothering the human.
- Inject `get_manager_profile()` output into agent reasoning when resolving architectural ambiguities (see cognitive-executor Context Bootstrapping).

## Sample-Evolution Loop (Review Gate Mandatory)

1. `propose_profile_evolution()` runs `scripts/compile_profile.py` and returns a `DRAFT_READY` draft (category distribution + recurring rationales). It NEVER writes to the sample.
2. Present the draft to the manager; on `APPROVED`, merge the reviewed text into `samples/manager_profile.md` baseline-adjacent generated section.
3. On `REJECTED`, record the rejection rationale as a decision (category `process`) so the next draft learns from it.
4. Identity updates without approval are forbidden — auto-promotion does not exist by design.

## Redaction Rules (Summary)

- Scrub before store, verify before write, attest via `redaction_verified: true`.
- Private IPs, provider keys, bearer tokens, and `password|secret|api_key = …` assignments are always redacted.
- A failed verification blocks persistence with a `ValueError` — surface it, do not bypass it.

## Invocation Example (per session)

```
# After the manager rules on the QA gate in session for task 167:
/manager-decision extract  →  extract_session_decisions(task_id=167)
                          →  record_manager_decision({...verbatim + category: "quality-gate"...})
                          →  "Recorded DEC-20260908-001"

# Weeks later, same ambiguity recurs:
query_manager_decisions("QA gate retry policy", category="quality-gate")
→  "### DEC-20260908-001 [quality-gate] … > <verbatim quote>"
→  decide without paging the manager.
```
