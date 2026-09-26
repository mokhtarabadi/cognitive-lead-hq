# OpenChamber over Tailscale — Setup & Usage (this workstation)

> Live since 2026-09-08. Server: `vm15996266` (loopback `127.0.0.1:3005` for Cloudflare Tunnel + Tailscale via `openchamber.surfshield.org`), port **3005**.
> Cloudflare Tunnel active 2026-09-19: `openchamber.surfshield.org` → `http://127.0.0.1:3005` via host-native `cloudflared` (system `cloudflared.service` v2026.9.1). Tailscale direct `100.82.29.19:3005` retired 2026-09-19 in favor of loopback for tunnel — see §7.

## 1. What is running

- **OpenChamber 2.0.2** (global npm: `@openchamber/web`, upgraded 2026-09-26 from 1.24.2), daemon PID varies — check with `openchamber status`.
  - Web UI: `127.0.0.1:3005` (loopback bind `--host 127.0.0.1`; Tailscale IP `100.82.29.19:3005` and public `194.76.154.73:3005` are **refused** — not `0.0.0.0`). Access locally via `http://127.0.0.1:3005`, remotely via Cloudflare `https://openchamber.surfshield.org` (tunnel → `127.0.0.1:3005`) — see §3-4. Legacy Tailscale `100.82.29.19:3005` retired 2026-09-19.
  - External OpenCode server (stability fix 2026-09-10): `opencode-server.service` (systemd user unit, `~/.config/systemd/user/opencode-server.service`) runs `/home/mohammad/.opencode/bin/opencode serve --hostname 127.0.0.1 --port 4096` — **loopback-only**, `Restart=on-failure`, enabled at boot. OpenChamber attaches via drop-in `~/.config/systemd/user/openchamber.service.d/external-opencode.conf` (`OPENCODE_HOST=http://127.0.0.1:4096`, `OPENCODE_SKIP_START=true`, `After=opencode-server.service`). Why: the OpenChamber-supervised managed server stalled its event loop every few hours (all 5 MCPs `server unavailable` simultaneously, watchdog restarts 3×/24h — see §2c). Community-proven path (upstream issue #2258: 3 days stable). Rollback: delete the drop-in, `daemon-reload`, restart openchamber → back to managed.
  - Managed OpenCode (OLD, pre-2026-09-10): auto-started by OpenChamber on a dynamic loopback port — replaced by the external server above.
  - UI password: enabled. Secret lives ONLY in `~/.secrets/openchamber-ui-password` (`chmod 600`). Never committed.
  - Auto-start at boot: `systemctl --user is-enabled openchamber` → `enabled`, `loginctl show-user mohammad | grep Linger` → `Linger=yes`, `Restart=always` (`RestartSec=5`). Survives reboot & logout; crash → restart in 5s. Check with `openchamber startup status` + `systemctl --user is-active openchamber`.
- **Default :3000 is NOT OpenChamber** — it is the pre-existing Next.js (fa/en) app. **:8080 is code-server.** Do not move OpenChamber onto either.
- **Plugins:** opencode plugin entries (global `~/.config/opencode/opencode.json` + global `cli.json` with V1 `tui.json` fallback, repo `opencode.json` with V1 `tui.json` fallback) are **goal + DCP** (`@prevalentware/opencode-goal-plugin` + `@tarquinen/opencode-dcp@latest`). Goal plugin **restored 2026-09-08** — it coexists with OpenChamber Session Goals (`/goal` in TUI/CLI + OpenChamber Goals in web UI complement each other, no conflict). Global `cli.json` mirrors `tui.json` for Opencode V2 compat. No project `cli.json` exists by design. (`permission.shell` mirrors `permission.bash` in `opencode.json`). **Worktree plugin `owt` (`@nano-step/opencode-worktree-plugin`) fully removed 2026-09-08** (`npm uninstall -g` + deleted `plugins/worktree-plugin.js` + 7 `command/*.md`; was `*.disabled` before removal). Reason: OpenChamber provides native worktrees (https://docs.openchamber.dev/worktrees/ + https://docs.openchamber.dev/multi-run/ — UI new-worktree dialog, isolate runs ≤5, Fusion, Git view → Integrate) — owt is redundant when OpenChamber is running. Reinstall only for CLI/headless without OpenChamber: `npm install -g @nano-step/opencode-worktree-plugin && owt-setup install` (see `LLM.txt §7.8`).

## 2. Daily commands (on the server, as `mohammad`)

```bash
openchamber status                        # running runtimes (expect: port 3005, password: yes)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3005/     # expect 200 (Tailscale IP; use this locally too)
curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://194.76.154.73:3005/ && echo "PUBLIC STILL OPEN" || echo "public refused (good)"
# note: http://100.82.29.19:3005/ is now refused when bound to loopback — expected (use 127.0.0.1)
timeout 8 openchamber logs -p 3005 | head -n 30   # recent log (logs cmd follows; always wrap in timeout)
export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"  # password via env, avoids ps exposure
openchamber startup status                # startup enabled, service active, lingering enabled
systemctl --user is-active openchamber   # should be active
systemctl --user is-active opencode-server # external OpenCode server (see §2c)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4096/session     # expect 200 (loopback only)
systemctl --user show-environment | tr ' ' '\n' | grep ^PATH=  # must contain mise shims, else uv MCPs can't spawn (see §2c)
openchamber stop --port 3005              # stop this instance (systemd will restart in 5s due to Restart=always)
openchamber update                        # update OpenChamber later
```

### 2b. Auto-start at boot (systemd user service)

- Enabled via `export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)" && openchamber startup enable --port 3005 --host 127.0.0.1` (was `--host 100.82.29.19` Tailscale-only until 2026-09-19; now loopback for Cloudflare Tunnel — see §7) → writes `~/.config/systemd/user/openchamber.service` (`ExecStart=... serve --foreground --port 3005 --host 127.0.0.1` (was `100.82.29.19` until 2026-09-19), `Restart=always`, `RestartSec=5`).
- Lingering via `sudo loginctl enable-linger mohammad` → `loginctl show-user mohammad` shows `Linger=yes`, `State=active` — user manager starts at boot even without login.
- Verification: `openchamber startup status` → `startup enabled`, `service active`, `user lingering enabled`; `systemctl --user is-enabled openchamber` → `enabled`; `systemctl --user is-active openchamber` → `active`; `ss -tlnp | grep 3005` → `127.0.0.1:3005` LISTEN; reboot → auto-starts, crash → restarts in 5s (`NRestarts` stays 0 when stable).
- Re-enable after password change: repeat the `startup enable` command (it rewrites `startup.env` with the new password) — do **not** hand-edit `startup.env`/`jwt-secret` (both `600`).

### 2c. External OpenCode server (stability fix 2026-09-10 — replaces managed server)

- **Why:** the OpenChamber-supervised managed `opencode serve` stalled its event loop every few hours of multi-session use — all 5 MCPs went `server unavailable` simultaneously (first wave `2026-09-10T00:00:25Z`, 5,550 retry lines over ~9h), no OOM/crash, watchdog (`Restarting OpenCode process...` + `TimeoutError`/WS `ECONNREFUSED`) fired 3× in 24h (Sep 9 14:01, 16:13; Sep 10 11:15). Failure is in opencode's MCP client layer, not the Python servers. Community-proven path: upstream issue [#2258](https://github.com/openchamber/openchamber/issues/2258) — external serve + `OPENCODE_SKIP_START` → 3 days stable. Related: [#3434](https://github.com/openchamber/openchamber/issues/3434) (reconnect flood, fix PR [#2783](https://github.com/openchamber/openchamber/pull/2783) unmerged) and [#1295](https://github.com/openchamber/openchamber/issues/1295) (old health-check false positives, already fixed).
- **Unit:** `~/.config/systemd/user/opencode-server.service` → `ExecStart=/home/mohammad/.opencode/bin/opencode serve --hostname 127.0.0.1 --port 4096`, `WorkingDirectory=/home/mohammad`, `Restart=on-failure`, `RestartSec=10`, enabled at boot (`WantedBy=default.target`). **Loopback-only by design** — OpenChamber reaches it locally; remote devices go through OpenChamber :3005, never to :4096 directly.
- **PATH (why services don't see `.bashrc`):** systemd user units never read `~/.bashrc` (non-interactive — no shell is ever spawned; upstream: https://wiki.archlinux.org/title/Systemd/User). So `~/.config/environment.d/zz-shell-path.conf` pins the full interactive-shell PATH manager-wide (mise shims, `~/.local/bin`, `~/.opencode/bin`, Android SDK, system). The `zz-` prefix is load-bearing: `/usr/lib/environment.d/99-*.conf` + `990-snapd.conf` reset PATH afterwards, so anything sorting earlier loses (verified via the `30-systemd-environment-d-generator` debug output). Rejected: `import-environment` (lost on reboot), `bash -lc` wrappers (fragile), `PAMName=login` (heavy). After PATH changes: `systemctl --user set-environment PATH=...` (running manager) + `daemon-reload`; verify with `systemctl --user show-environment | tr ' ' '\n' | grep ^PATH=`. Regenerate the pinned value with `bash -ic 'echo $PATH' 2>/dev/null`.
- **Wiring:** drop-in `~/.config/systemd/user/openchamber.service.d/external-opencode.conf` sets `OPENCODE_HOST=http://127.0.0.1:4096` + `OPENCODE_SKIP_START=true` + `After=opencode-server.service` (ordering only). Takes effect on next openchamber restart. Rollback: delete the drop-in file, `systemctl --user daemon-reload`, restart openchamber → managed server returns.
- **Verify:** `systemctl --user is-active opencode-server` → `active`; `ss -ltn | grep 4096` → `127.0.0.1:4096` ONLY (never `0.0.0.0`); authenticated info check → `200` (see §2c-password below — unauthenticated `/api/*` correctly returns `401` on V2); `journalctl --user -u opencode-server` shows `server listening on http://127.0.0.1:4096`.
- **Restart order (both):** `systemctl --user restart opencode-server` first, then `systemctl --user restart openchamber` (chamber re-attaches on boot via `After=`). During the switch window two opencode processes briefly coexist — telegram MCP shared-lock mode (upstream v3.2.33) covers the overlap.
- **Ownership note:** OpenChamber updates (`openchamber update`) no longer restart your OpenCode server; `opencode` binary updates via `~/.opencode/bin` as before, then `restart opencode-server`. OpenCode V2 itself upgrades via `curl -fsSL https://opencode.ai/v2/install | bash` (replaces the V1 binary in place).

### 2c-password. V2 server-password sync (401 fix 2026-09-26 — REQUIRED in external mode)

- **Why:** V2 `opencode serve` mints a random Basic-auth password every boot unless `OPENCODE_PASSWORD`/`OPENCODE_SERVER_PASSWORD` is set. OpenChamber authenticates with `OPENCODE_SERVER_PASSWORD` from its own env (`startup.env`). Any mismatch → `Startup failed / OpenCode info endpoint responded with status 401`, `PushWatcher disconnected / upstream_unavailable` floods, UI shows sessions but no OpenCode.
- **Fix (one stable password, both sides):** `~/.config/opencode/.server-password` (`chmod 600`, generated once) → pinned on the server via drop-in `~/.config/systemd/user/opencode-server.service.d/10-password.conf` (`Environment=OPENCODE_SERVER_PASSWORD=<value>`) → same value as the `OPENCODE_SERVER_PASSWORD="..."` line in `~/.config/openchamber/startup.env` (this line wins over drop-ins, so the startup.env edit is load-bearing, not the drop-in).
- **After ANY `openchamber startup enable`** (it rewrites `startup.env`): re-apply the password line from `~/.config/opencode/.server-password`, `daemon-reload`, restart both services (USER action). Never rotate the password file without re-syncing both sides.
- **Verify:** `journalctl --user -u openchamber -n 20 | grep -c 'status: 401'` → `0`; fresh logs show `[PushWatcher] connected`; authenticated `curl -u opencode:<password> http://127.0.0.1:4096/api/info` → `200`. Full steps: `LLM.txt §7.9` password-sync.

### 2d. Outbound proxy for opencode-server via mihomo-subs (2026-09-23)

- **Why:** route all outbound LLM API traffic through the `mihomo-subs` pool (`127.0.0.1:7890`, 53 free-pool nodes, 6h refresh) instead of direct egress.
- **How:** OpenCode respects standard proxy env vars (upstream: https://opencode.ai/docs/network). Set as `Environment=` lines in `~/.config/systemd/user/opencode-server.service` (NOT in `~/.config/opencode/.env` — that file is for secrets/keys; the proxy URL is non-secret loopback config):
  `HTTP_PROXY=http://127.0.0.1:7890`, `HTTPS_PROXY=http://127.0.0.1:7890` (plain `http://` scheme — 7890 is a mixed HTTP+SOCKS port, TLS to providers is tunnelled via CONNECT), `NO_PROXY=localhost,127.0.0.1,::1` **required** (server/TUI loopback `:4096` must bypass the proxy or you get a routing loop), plus lowercase twins (`http_proxy`/`https_proxy`/`no_proxy`) for the Bun/Node runtime.
- **Apply:** `systemctl --user daemon-reload && systemctl --user restart opencode-server.service`. Verify env on the live process: `tr '\0' '\n' < /proc/$(systemctl --user show -p MainPID --value opencode-server.service)/environ | grep -i proxy` (all six vars). Health: `curl http://127.0.0.1:4096/` still direct (NO_PROXY working); proxy itself: `curl -x http://127.0.0.1:7890 https://www.gstatic.com/generate_204` → `204`.
- **Rollback:** delete the six `Environment=` lines, `daemon-reload`, restart → direct egress returns.

## 3. Connect from a PC (mohammad-pc-1 / cando — Tailscale)

1. Join the same tailnet on the PC (`tailscale status` must show `vm15996266`).
2. Open `https://openchamber.surfshield.org/` (Cloudflare Tunnel → `127.0.0.1:3005`) in the browser, or `http://127.0.0.1:3005/` locally. Legacy `http://100.82.29.19:3005` is refused after 2026-09-19. Enter the UI password (ask the server owner; it is in `~/.secrets/` on the server only).
3. Recommended: pair properly instead of password-every-time —
   on the server run `openchamber connect-url --port 3005 --server https://openchamber.surfshield.org --qr` (was `http://100.82.29.19:3005` until 2026-09-19),
   then in OpenChamber Desktop use *Settings → Remote Instances → Direct Instances → Import Link* (or scan QR from mobile). Links are **single-use and expire** — generate a fresh one per device.
4. Desktop app can then switch between direct (Tailscale) and Relay transports; green dot = connected.

## 4. Connect from Android (redmi-note-13 / xiaomi-2312fpca6g — Tailscale)

1. Install Tailscale from Play Store, log in to the same tailnet, or just open `https://openchamber.surfshield.org` via Cloudflare (no Tailscale needed externally); verify `tailscale status` if using Tailscale link.
2. Option A (native): install the OpenChamber Android APK from `https://github.com/openchamber/openchamber/releases/latest`, open it, *Scan QR* from a fresh server-side `connect-url --qr` (Home-network scope is enough on Tailscale).
3. Option B (no install): in Chrome open `http://100.82.29.19:3005/`, log in with the UI password, then *Install app / Add to Home Screen* (PWA).
4. For away-from-home use, re-pair with **Anywhere** scope so the E2E Relay takes over when Tailscale direct is unreachable (server holds outbound to relay infra; no ports opened).

## 5. Pairing & revoke discipline

- One link per device; links expire after single use (~minutes). Never paste a link into chat/docs — it contains a secret.
- Revoke a lost device: OpenChamber *Settings → Remote Instances* → *Revoke* (then *Clear revoked*). Rotate the UI password afterwards if it may have leaked: write the new value to `~/.secrets/openchamber-ui-password` (`chmod 600`), then `openchamber restart --port 3005` (or stop + start per §2).
- Passkeys (*Settings → OpenChamber → Passkeys*) are optional hardening; note they clear on password change.

## 6. Troubleshooting

| Symptom | Check |
|---|---|
| Browser gets 307 → `/fa` on :3000 | You hit the Next.js app, not OpenChamber — use **:3005**. |
| `curl` to :3005 hangs/refused | `openchamber status`; `ss -tlnp \| grep 3005` should show `127.0.0.1:3005` LISTEN; `curl http://127.0.0.1:3005/` → 200; public IP → refused is expected. |
| `curl http://100.82.29.19:3005/` refused | Expected after 2026-09-19 — bound to loopback only (`127.0.0.1:3005`). Use `http://127.0.0.1:3005/` locally or `https://openchamber.surfshield.org` remotely. |
| Startup not starting at boot | `systemctl --user is-enabled openchamber` → `enabled`; `loginctl show-user mohammad | grep Linger` → `yes`; `systemctl --user status openchamber`; `journalctl --user -u openchamber -n 30`. Re-enable: `export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)" && openchamber startup enable --port 3005 --host 127.0.0.1` + `sudo loginctl enable-linger mohammad`. |
| Tailscale IP unreachable from phone/PC | `tailscale status` both ends; `tailscale ping 100.82.29.19`; ensure Tailscale is up (not logged out). |
| Chat/notifications stall | Check `timeout 8 openchamber logs -p 3005`; external OpenCode `:4096` must stay loopback (authenticated `/api/info` → 200, see §2c-password); restart order: `opencode-server` then `openchamber` (see §2c). |
| OpenChamber "Startup failed / status 401" | Server/client password mismatch (V2 randomizes per boot) — re-sync per §2c-password, restart both, expect `[PushWatcher] connected` and zero `status: 401` lines. |
| All MCP tools unavailable to AI at once | Known managed-server stall (pre-§2c): every session logs `server unavailable` ×5 every 30s. Check `systemctl --user is-active opencode-server` + `:4096` health; restart both per §2c. If it recurs on the external server, capture `journalctl --user -u opencode-server` + RSS trend (`ps -o pid,etime,%mem,rss -C opencode`) for an upstream issue. |
| High RAM (7.8GB host) | `free -h`; `docker stats`; stop idle OpenChamber sessions; blowsh MCP pulls a Docker image per use. |
| `/init-worktree` does nothing | Expected — worktree plugin `owt` was removed 2026-09-08 (OpenChamber native worktrees via UI; see §1 + `LLM.txt §7.8`). Reinstall only if you need CLI/headless without OpenChamber. |

## 7. Security notes

- Loopback bind `--host 127.0.0.1` (since 2026-09-19, was `--host 100.82.29.19` until 2026-09-19): `ss -tlnp` shows `127.0.0.1:3005` not `0.0.0.0:3005`; public IP `194.76.154.73:3005` → refused, Tailscale IP `100.82.29.19:3005` → refused — only loopback + Cloudflare Tunnel `openchamber.surfshield.org` can reach it (`mmokhtarabadi@gmail.com` tailnet, 5 peers) can reach it. Prior `0.0.0.0` bind was publicly reachable and has been hardened.
- Secrets: `~/.secrets/openchamber-ui-password` (`600`), `~/.config/openchamber/jwt-secret` (`600`), `~/.config/openchamber/startup.env` (`600`, contains password for systemd — never committed). UI password stays ON, pairing links stay single-use and expire, passkeys clear on password change.
- Auto-start: `openchamber.service` `enabled` + `Linger=yes` + `Restart=always` — survives reboot/logout/crash; verify with `openchamber startup status` and `systemctl --user is-active openchamber`.
- Cloudflare Tunnel active 2026-09-19: host-native `cloudflared` system service (`cloudflared.service` v2026.9.1, token `/etc/cloudflared/token`) proxies `https://openchamber.surfshield.org` → `http://127.0.0.1:3005` and `https://code.surfshield.org` → `http://127.0.0.1:8080`. See `docs/cloudflared.md`. Do NOT run a Quick tunnel with the real password for anything but a smoke test.
- External OpenCode `:4096` is loopback-only (`127.0.0.1:4096`, never `0.0.0.0`) — not reachable via Tailscale or public IP by design; remote devices always go through OpenChamber `:3005`.
