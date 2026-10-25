# Milestone M02 — Planner cockpit, design system, and board hardening

**Opened:** 2026-10-24 · **Closed:** 2026-10-25 · **Released in:** v9.66.0

## Scope

The planner moved from a thin status board to a planning cockpit with a saved
weekly commitment, both Cognitive Lead surfaces adopted one design system, the
public board was hardened, and the Brain's XML/prompt pipeline was repaired.

## Delivered

| Task | What shipped |
| ---- | ------------ |
| 342 | Brain extraction exact for bare/3-backtick/4-backtick fences; prompt rebuild byte-identical |
| 340 | Planner protocol and daily pacing native in the system prompt (9.65.0) |
| 344 | Planner + Prompt Composer on vendored Bootstrap 5.3, `DESIGN.md` Graphite Desk, live board hardening (Secure cookie, HSTS, 400 on relative root), `jalaali-js` timeline |
| 345 | Day/week/month cockpit: `/api/plan`, capacity, 14-day chart, deadline rail, deep links |
| 347 | Saved weekly plan state with approval, admin-only save/clear, agenda commitment + deviations |
| 346 | Ownership field, Mine filter, NUDGE/OVERDUE signals |

## Verification

- Planner suite: 115 passed. Prompt/splitter: 103 passed. Full suite green at the last run.
- Live board `https://board.surfshield.org/`: 200 on `/`, `/api/plan` and all static assets; save/read/clear of the week plan verified with an admin session.
- Deployed copies under `~/.config/opencode/` verified byte-identical (`server.py`, `static/*`, `system-prompt.md`, `agents/cognitive-executor.md`).

## Known gaps carried forward

- `/mcp` answers `421` remotely instead of the documented `404`; the ingress fix belongs to Cloudflare (no `cloudflared` config on this host).
- The dashboard "done" count derives from the completed lane plus a deadline; task files store no closed timestamp (documented in `DESIGN.md`/ADR-008).
- Weekly plan writes are atomic but not locked; single-operator assumption is documented.
