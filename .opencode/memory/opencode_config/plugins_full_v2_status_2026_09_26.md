---
created_at: '2026-09-26T17:45:00.423109+00:00'
status: active
tags: []
updated_at: '2026-09-26T17:45:00.423238+00:00'
---

# Plugins full-V2 status — verified 2026-09-26 (Task 274, opencode 2.0.18)

Both plugins at latest stable AND both V2-capable upstream. No upgrade work remains.

- goal `@prevalentware/opencode-goal-plugin@0.1.52` (released 2026-09-26; 0.1.50 Sep 21, 0.1.51 Sep 22). V2 port: PR #49 merged 2026-09-14 (beta-19425 contract, compaction context, restart transcript recovery, dual [id,server,setup] shape, V2 lifecycle smoke PASS) + PR #58 merged+released 2026-09-26 (V2 task-recovery scoping). Open issue #54 is a V1-host registration bug whose body confirms setupV2 targets V2 hosts.
- DCP `@tarquinen/opencode-dcp@3.2.0` (stable 2026-09-20). V2 setup() via session hooks (context, compaction). Betas 3.2.1-3.2.8-beta0 are stale Mar/Apr experiments — stable 3.2.0 is newest. Known gap by design: compress.permission ask throws in V2; keep default allow.
- Source of truth: `opencode plugin list` (shows 0.1.52 + 3.2.0, zero errors). `~/.cache/opencode/packages/*` is metadata-only (no dist/); V2 host resolves npm at runtime.
- Upstream-issue policy: search before filing, never duplicate. DCP repo Opencode-DCP/opencode-dynamic-context-pruning has active V2 threads #627/#628/#631/#632 — file nothing there. Goal repo prevalentWare/opencode-goal-plugin.
- Corrects the earlier (wrong) claim that the goal-plugin server is V1-only — that reading came from a stale cache copy.