---
status: active
tags: []
---

# OpenCode / OpenChamber versions — verified 2026-11-02

- OpenCode **v2.2.5** (binary at `~/.opencode/bin/opencode`; official endpoint `https://opencode.ai/update/api/latest/cli/npm` reports 2.2.5 as latest — already current, no reinstall needed).
- OpenChamber **2.6.0** (npm `latest` tag; upgraded from 2.5.3 via `npm install -g @openchamber/web@2.6.0` under mise node 24; binary reports 2.6.0).
- Install-source rules (unchanged): OpenCode V2 installs only from `https://opencode.ai/v2/install` (never the V1 URL on a V2 machine); OpenChamber installs as npm package `@openchamber/web` (global via mise node, `npm install -g @openchamber/web@<version>`).
- Global `cli.json` uses the native V2 shape (`$schema` https://opencode.ai/v2/cli.json, no plugin entries — the project uses no OpenCode plugins). Global and project `opencode.json` use V2 keys only. No V1 dual keys remain.
- Plugin policy: **no OpenCode plugins** (goal plugin and DCP/compress removed 2026-10-01 per Manager order).

Supersedes: opencode_config/opencode_v2_upgrade_2026_09_26 (recorded v2.0.21 / OpenChamber 2.1.0 — stale).
