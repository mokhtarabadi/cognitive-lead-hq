---
name: manager-decision
description: Capture per-session manager decisions into a separate learning repo. Extract rulings, redact secrets, consult past decisions, and evolve the manager-AI sample behind a human review gate.
---

# Manager-Decision Skill

> **LIVE:** the `manager_decisions` MCP server is connected (repo + global `opencode.json`). Invoke its tools per the triggers below. Autopilot consults these stored rulings to decide as the manager would.

## Purpose

Turns each session's manager judgment into training data. Whenever the manager makes a trade-off, ruling, or system-design call, this skill extracts it (verbatim quote + structured decision), redacts secrets, and persists it append-only — since Task 216, to the manager's SEPARATE PERSONAL repo (pointed to by `DECISION_REPO_PATH`, onboarded via `LLM.txt` §7.11), which is the authoritative personality source across all projects. The per-project `.opencode/decisions/` store from Task 168 now serves only as write-through cache + offline fallback, never the personality source: the Task 213 mirror-never-authority rule below is SUPERSEDED for personality scope by explicit manager order (Task 216). Aggregated decisions evolve `samples/manager_profile.md` — the manager-AI sample — one reviewed promotion at a time, until micro-decisions no longer need the real manager.

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

## Auto-Trigger Spec (Task 213 — closes the never-called gap)

Extraction was callable but never called automatically. Two layers now feed it:

1. **Live detector** (`mcp-decision-server/detector.py`, pure function, no LLM):
   `detect_decision_moments(turns)` flags turns with 2+ signals (owner:manager +
   ruling-phrase + tradeoff-marker + scope-noun). Only candidates with
   `passes=True` (named owner + 2 content signals per `passes_precision_bar`)
   go to `extract_session_decisions`. Single-signal turns are dropped.
2. **End-of-sprint sweep**: scan `tasks/.sessions/*/transcript.jsonl` for
   sessions with no decision record; run detection + extraction; queue every
   candidate for confirm. Missing file → skip; empty file → keep loud error
   (never silently pass). Reuse the extraction LRU/repair path, never a fork.
3. **Mandatory confirm gate**: NOTHING persists without the Manager approving
   the scrubbed quote + source session + `verify_clean` result. Rejections drop
   silently (no write, no retry). Auto-record is forbidden — confirm is slower
   but preserves verbatim trust. The gate is enforced in the call path, not
   just prose: `detector.py` has no code path to the store, and agents MUST
   NOT call `record_manager_decision` on detector output without pasting the
   scrubbed quote back to the Manager and receiving explicit approval first.

## Personal Repo — Separate, Authoritative (Task 216 — SUPERSEDES Task 213 mirror rule)

- The manager's decisions live in ONE separate personal repo (public by
  default — cooler per manager order; private stays optional), pointed to by
  `DECISION_REPO_PATH` and onboarded via `LLM.txt` §7.11 (declare the repo or
  let `gh repo create` make it when pre-configured).
- It is the AUTHORITATIVE personality source across all projects — every
  project stores the manager's raw decisions there, structured, scrubbed, and
  append-only. Task 168's per-project authority is explicitly superseded for
  personality scope by manager order; per-project `.opencode/decisions/` is a
  write-through cache + offline fallback (used when the personal repo is
  unreachable; the agent logs which root every record landed in), not the
  personality source. Task 213's mirror-never-authority rule is superseded.
- Same `decisions/YYYY/MM/DEC-*.json` + `.md` + `INDEX.md` layout and the same
  `ENTRY.md` / `OPINIONS.md` / `VOICE.md` / `TOOLS.md` living-document shape;
  Task 191 determinism, Task 151 deletion, and the tombstone-only retraction
  rule all still hold.
- Cooking ownership: raw captures are written by the project-side agent, but
  ONLY OpenCode AI cooks raw into macro system-design decisions — project
  agents MUST NOT rewrite cooked records; cooking happens in the personal
  repo itself (see `policy/cook-review.md` there).
- Redaction boundary: `sanitize_text` then `verify_clean` must both pass
  before any personal-repo write. Records hold the scrubbed ruling +
  verbatim quote + date; secrets never land in the repo (public by default).
- Deletion rule: append-only. Retractions are new tombstone records pointing
  at the superseded id — never edit or delete history in place.
- Challenge-question sharpening: versioned, scored question sets may probe the
  repo to sharpen the profile — but profile writes still need the review gate
  above. Never free chat, never auto-promotion.
- Sync protocol (auto alive): the server pulls before every record and every
  read, so recall serves the latest version; a diverged store fails closed
  on WRITES (loud error, local state untouched) but READS still serve stale
  local state with a loud stderr note — consults never go offline.
  Commit + push stay
  Manager-owned under ZAC — agents MUST NOT push; every record answer ends
  with the visible sync-debt line telling the Manager exactly what to push.
  `DECISION_NO_PULL=1` skips the pull (tests / fully offline work only).

## Consult-on-Stuck Protocol (Task 216 — the replay skill)

When the agent is stuck and needs help, it calls the manager skill — the
skill replays what the manager would have decided:

1. **Invoke:** `query_manager_decisions("<stuck question>", category?)`
   against the personal repo, then `get_manager_profile()` for the cooked
   personality. Consult FIRST — before paging the human.
2. **Replay line:** every decision the agent takes from a replayed ruling MUST
   carry the replay line, so the manager can audit the lineage:
   `Replayed from <DEC-ID> (<date>): <verbatim quote, max 200 chars>`.
3. **No-match escalation:** if the query returns no usable ruling, the agent
   MUST escalate to the manager with the exact query it tried plus why the
   top results did not apply — never invent a ruling, never stay silent.
4. **Autopilot loop-pole:** in autopilot the consult verdict travels inside
   the agent's own turns (decide-from-record, log the replay line, continue);
   the human is paged only on no-match escalation. (Per stored
   autopilot-cycle ruling DEC-20260912-007.)
