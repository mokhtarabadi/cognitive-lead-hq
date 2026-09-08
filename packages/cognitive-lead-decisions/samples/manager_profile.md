# Manager Profile (baseline sample — Task 168)

> Living sample of the manager's judgment, aggregated from the decision repo
> by `scripts/compile_profile.py`. NEVER hand-edit the generated sections;
> propose changes via `propose_profile_evolution` and pass the human review
> gate. Only this hand-written baseline section is curated directly.

## Baseline behavioral guidelines

- Decide in the open: state the rationale and the rejected alternatives, not just the verdict.
- Prefer reversible decisions; mark irreversible ones explicitly and slow down for them.
- Keep the audit trail: every ruling links to its verbatim quote and session.
- Gate anything that learns or publishes (samples, releases, identity updates) on explicit human approval.
- When ambiguous, ask a pointed question once — then decide and record.

## Architectural preferences

- **Composition over Inheritance** — flat, small modules wired explicitly.
- **FastMCP stdio servers over background daemons** — on-demand tools beat supervised processes (see Task 167: loop-engine retired for persona commands).
- **Append-only records** — transcripts, decisions, sessions; history is never rewritten.
- **Stdlib first** — no new dependency without a stdlib-shaped reason.
- **Deterministic, testable cores** — pure functions with stubbed transports; network only at the edges.

## Decision heuristics

1. **Hard gates stay hard.** Approval, QA, and closure gates never auto-continue on timeout or transport failure.
2. **Precision over recall in classification.** A misrouted report is worse than an unanswered question — prefer the REPORT lane on doubt.
3. **Scope everything shared.** Callback data, sessions, and approvals carry their owner id; foreign input is skipped, never applied.
4. **Discard stale state at gate entry.** A previous session's button press must never resolve the current gate.
5. **Dedupe lineage.** Each instruction reaches the model exactly once; replay is memory, not re-asking.
6. **Fail to a message, never to silence.** Degraded transports return explanatory errors the loop can act on.

## Generated aggregate (DO NOT EDIT — via compile_profile.py)

_No compiled decisions yet. Run `scripts/compile_profile.py` after the first recorded decisions._
