# Velocity Log

Throughput record for the Cognitive Lead AI HQ repo. One row per closed
task: suite size at close proves the harness keeps working while scope
grows. Counts come from each task's `## Verification Evidence` and its
`CHANGELOG.md` entry.

| Task | Scope | Tests passing at close |
| ---- | ----- | ---------------------- |
| 230 | Manager-decision hardening | 98 |
| 231 | Decision follow-up H1/H2/H3 | 101 |
| 232 | Brain EMPTY_OUTPUT_RETRY hint | 345 |
| 233 | Supervised autopilot plan-approval | 350 |
| 234 | Brain sessions per project (+hotfix) | 357 |
| 235 | Review-approval relay | n/a (release line, no suite delta claimed) |
| 236 | Lean-retry state note | 357 |
| 237 | opencode-init project-only contract | validator gates |
| 238 fix loop | XML tolerance, tree boundary, roster, queue cap | 155 + 15 (targeted suites) |

## Convention

On every task close, the Hands appends one row (task id, one-line scope,
suite count + exit code). No row, no close.
