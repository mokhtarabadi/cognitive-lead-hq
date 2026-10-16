---
created_at: '2026-10-16T20:22:33.519163+00:00'
status: active
tags: []
updated_at: '2026-10-16T20:22:33.519174+00:00'
---

# Brain calls MUST carry a mode line (Manager order 2026-10-16)

Every brain_turn user prompt MUST open with one line stating the live mode, because the Brain's system prompt carries both emission shapes and cannot know which is live:

- Autopilot: MODE: AUTOMATIC (autopilot locked) — emit bare unfenced XML only, never xml-fenced blocks; do NOT emit copy-paste relay instructions ("Manager: please copy...") — the Hands chain QA/review turns directly.
- Manual: MODE: MANUAL — xml-fenced blocks expected; copy-paste relay instructions expected.

Without the line the Brain fence-strict-rejects in autopilot (re-emit loop) and keeps emitting admin copy-paste text in a silent pipeline.

Encoded in agents/cognitive-executor.md (Brain Bridge Build step + autopilot section) and docs/brain-bridge.md; synced globally 2026-10-16.