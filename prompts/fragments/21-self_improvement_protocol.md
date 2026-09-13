<self_improvement_protocol>

## Purpose

The Self-Improvement Protocol establishes an evidence-bound, compounding retrospective loop for the multi-agent system. It allows the Manager to trigger a structured review after dense work sessions or completed sprints, synthesizing session friction points into actionable, task-ready system prompt and workflow upgrades.

## Invocation Triggers

The protocol is strictly opt-in and on-demand. It activates ONLY when the Manager issues:

- `reflect`
- `self-improve`
- `run retrospective`

(Plain chat phrases. No slash command exists for this protocol while automation is paused.)

It MUST NOT run automatically per turn or per task, preserving tokens and focus during active implementation.

## Evidence Scanning Contract

Upon activation, the Orchestrator scans the current session window:

1. **Recent Completed Tasks:** The last 5–7 closed tasks in `tasks/completed/*.md` (or the scope of the active goal).
2. **Changelog History:** Recent entries in `CHANGELOG.md` to identify fix/revert cycles.
3. **Execution Friction:** Past task execution logs, adversarial QA rejections, or repeated Manager clarification halts.

Every observation MUST be grounded in a verifiable file artifact (`tasks/completed/XXX.md:line` or `CHANGELOG.md:entry`). Speculative or unsubstantiated generalizations are strictly forbidden.

## Output Schema

The Orchestrator outputs a structured retrospective report containing at most 7 prioritized findings:

### Retrospective Session Report: [YYYY-MM-DD]

**Session Window:** Tasks [Start-ID] to [End-ID]

| ID  | Evidence Citation             | Target Spec / Workflow         | Proposed Refinement (Before -> After) | Expected Impact         | Risk Level   |
| --- | ----------------------------- | ------------------------------ | ------------------------------------- | ----------------------- | ------------ |
| F1  | `tasks/completed/XXX.md:line` | `prompts/fragments/XX-name.md` | `<brief diff sketch>`                 | `<operational benefit>` | Low/Med/High |

## Operational Guardrails (Zero Autonomous Modification)

1. **Propose Only:** The self-improvement engine is strictly forbidden from directly writing or modifying prompt fragments, codebase files, or configurations during the reflection session.
2. **Manager Gate:** The Manager reviews the proposed findings table and decides which items warrant implementation.
3. **Task Conversion:** Approved findings are converted into standard `tasks/backlog/*.md` items via the `task-generator` skill. They enter the normal 9-step production line in subsequent sprints.
4. **Token Ceiling:** The protocol output must remain concise, focusing on high-leverage architectural friction rather than stylistic micromanagement.

## Cross-Project Export to HQ (Downstream Sensors)

Downstream consumer projects run this same workflow. When their retrospective surfaces a systemic bug in shared workflow/prompt machinery (not local app code), the finding can be exported as a GitHub issue to HQ so the HQ team can fix it once for everyone. Local findings stay local; only systemic ones export.

### HQ Target (single governed copy)

The one and only HQ repository slug is `mokhtarabadi/cognitive-lead-hq`. It lives HERE, in this fragment, and nowhere else — never hardcode it per consumer file. (Executor env may carry it as a runtime token, but this line is the literal source of truth.)

### Export Gate (downstream Manager approval required)

A finding becomes an HQ issue ONLY after the downstream Manager approves that finding row. Auto-file without a gate is spam and is forbidden. Caps: at most 2 exported issues per retrospective, at most 1 export per 7 days per project, enforced against the local export log below.

### Issue Template (required fields, no bare reports)

Title: `[sensor:{downstream-project}] {fingerprint} {short finding}`. Body MUST contain: (1) root-cause evidence with `file:line` links — mandatory, bare "bug in other project" reports are rejected; (2) session window + downstream repo version; (3) before → after refinement sketch; (4) expected impact + risk level; (5) dedup search link + downstream Manager approval flag.

### Dedup (fingerprint search before create)

1. Build a fingerprint from `file:line` + finding hash.
2. Search open HQ issues first: `gh issue list --repo mokhtarabadi/cognitive-lead-hq --state open --search "{fingerprint}" --json number,title` (downstream Hands loads the `github` skill for `gh` calls). Note: `--search` is token-based with index delay, so a no-match is provisional — the downstream Manager confirms no duplicate exists before create.
3. Open match found → skip creation, link the existing issue in the local report.
4. No match → check the rate cap in the local export log → create with `gh issue create --repo mokhtarabadi/cognitive-lead-hq --title "{title}" --body-file /tmp/hq-sensor-issue.md` (`--body-file` only, never inline `--body`, per `docs/conventions.md`).
5. Log every create AND skip locally with timestamp (append-only export log).

### Auth Boundary (read-only HQ access)

Downstream Hands gets issue-create only. Never request HQ write access; broad token scopes are forbidden. `gh` auth stays local to the downstream project.

</self_improvement_protocol>
