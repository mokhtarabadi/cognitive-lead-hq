---
status: active
tags: []
---

# OpenCode / OpenChamber versions — verified 2026-11-13

- OpenCode **v2.3.0** (binary at `~/.opencode/bin/opencode`; `opencode2` is a thin `exec` shim next to it). This is the ACTIVE binary — `~/.opencode/` is the OpenCode install, not a Freebuff artifact, and must be kept.
- OpenChamber **2.7.1** (npm `@openchamber/web`, global under mise node 24; binary reports 2.7.1).
- Install-source rules: OpenCode V2 installs only from `https://opencode.ai/v2/install` (never the V1 URL on a V2 machine); OpenChamber installs as the npm package `@openchamber/web` via `npm install -g @openchamber/web@<version>` (not `openchamber update`, which does not exist as a package-level upgrade path — verify with `openchamber --version` after install).
- Global `cli.json` uses the native V2 shape (`$schema` https://opencode.ai/v2/cli.json, `plugins: ["opencode-todolist"]` for the TUI sidebar strip). Global and project `opencode.json` use V2 keys only. No V1 dual keys remain.
- **Plugin policy (updated 2026-11-13):** three plugins are installed and approved — `github:mokhtarabadi/opencode-smart-compact` (V2-native context compaction), `github:mokhtarabadi/opencode-goal-plugin` (one long-running objective per session), and `opencode-todolist` (V1 `todowrite`/`todoread` + sidebar strip). The earlier "no OpenCode plugins" note was stale after the goal plugin and todolist were adopted.
- Git-spec plugins do NOT refresh via `opencode plugin update` (it errors "Plugin is not configured") — the refresh path is `plugin remove` + `plugin add`, plus deleting the stale `~/.cache/opencode/npm/git-opencode-<plugin>-*/` directory so the next start re-fetches from GitHub. Both plugin repos are pushed, so a cache purge + reinstall picks up the newest commit.
- **A binary upgrade is not an install upgrade.** The OpenCode binary, the OpenChamber package, and the global install targets (`~/.config/opencode/` servers, skills, agents, prompts, plugins) are independent copies. Upgrading only the binary leaves the harness on old code — run the full chain in `.opencode/memory/workflows/global-install-upgrade.md` and `LLM.txt` §1 "Upgrading OpenCode / OpenChamber".
- The Manager restarts OpenCode and OpenChamber; the Hands prepares the install and says so.

Supersedes: opencode_config/opencode_v2_upgrade_2026_09_26 (v2.0.21 / OpenChamber 2.1.0) and the 2026-11-02 snapshot (v2.2.5 / OpenChamber 2.6.0 — stale, and its "no plugins" claim no longer holds).
