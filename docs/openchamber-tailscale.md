# OpenChamber over Tailscale — Setup & Usage (this workstation)

> Live since 2026-09-08 (Task 165). Server: `vm15996266` (Tailscale IP `100.82.29.19`), port **3005**.
> Cloudflare Tunnel with a real domain is a LATER step — this doc covers Tailscale-only access.

## 1. What is running

- **OpenChamber 1.22.2** (global npm: `@openchamber/web`), daemon PID varies — check with `openchamber status`.
  - Web UI: `0.0.0.0:3005` (LAN mode, so Tailscale interfaces serve it too).
  - Managed OpenCode: auto-started by OpenChamber on a loopback-only port (e.g. `127.0.0.1:44133`, allocated dynamically) — never exposed directly.
  - UI password: enabled. Secret lives ONLY in `~/.secrets/openchamber-ui-password` (`chmod 600`). Never committed.
- **Default :3000 is NOT OpenChamber** — it is the pre-existing Next.js (fa/en) app. **:8080 is code-server.** Do not move OpenChamber onto either.
- **Plugins:** opencode `plugin` arrays (global `~/.config/opencode/opencode.json` + `tui.json`, repo `opencode.json` + `tui.json`) are **dcp-only** (`@tarquinen/opencode-dcp@latest`). Goal plugin removed (overlaps OpenChamber Session Goals); worktree loader `~/.config/opencode/plugins/worktree-plugin.js` renamed to `.disabled` (its `/init-worktree` etc. slash commands are dormant, not deleted). Re-enable: restore the goal line in the 4 JSONs; `mv worktree-plugin.js.disabled worktree-plugin.js`.

## 2. Daily commands (on the server, as `mohammad`)

```bash
openchamber status                        # running runtimes (expect: port 3005, password: yes)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3005/        # expect 200
curl -s -o /dev/null -w "%{http_code}\n" http://100.82.29.19:3005/     # expect 200 (Tailscale IP)
timeout 8 openchamber logs -p 3005 | head -n 30   # recent log (logs cmd follows; always wrap in timeout)
openchamber --lan --port 3005 --server http://100.82.29.19:3005   # (re)start daemon after a stop
export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"  # password via env, avoids ps exposure
openchamber stop --port 3005              # stop this instance
openchamber update                        # update OpenChamber later
```

## 3. Connect from a PC (mohammad-pc-1 / cando — Tailscale)

1. Join the same tailnet on the PC (`tailscale status` must show `vm15996266`).
2. Open `http://100.82.29.19:3005/` in the browser. Enter the UI password (ask the server owner; it is in `~/.secrets/` on the server only).
3. Recommended: pair properly instead of password-every-time —
   on the server run `openchamber connect-url --port 3005 --server http://100.82.29.19:3005 --qr`,
   then in OpenChamber Desktop use *Settings → Remote Instances → Direct Instances → Import Link* (or scan QR from mobile). Links are **single-use and expire** — generate a fresh one per device.
4. Desktop app can then switch between direct (Tailscale) and Relay transports; green dot = connected.

## 4. Connect from Android (redmi-note-13 / xiaomi-2312fpca6g — Tailscale)

1. Install Tailscale from Play Store, log in to the same tailnet, verify `tailscale status` on the server shows the phone.
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
| `curl` to :3005 hangs/refused | `openchamber status`; `ss -tlnp \| grep 3005`; restart per §2. |
| Tailscale IP unreachable from phone/PC | `tailscale status` both ends; `tailscale ping 100.82.29.19`; ensure Tailscale is up (not logged out). |
| Chat/notifications stall | Check `timeout 8 openchamber logs -p 3005`; managed OpenCode port (44133-ish) must stay loopback; restart instance. |
| High RAM (7.8GB host) | `free -h`; `docker stats`; stop idle OpenChamber sessions; blowsh MCP pulls a Docker image per use. |
| `/init-worktree` does nothing | Expected — worktree plugin is disabled (see §1). |

## 7. Security notes

- Tailscale tailnet = private irrespective of `--lan`; nothing here is on the public internet. Still: UI password stays ON, pairing links stay single-use, secrets never enter git/shell history (use the env-var form in §2).
- Next step (separate task): Cloudflare Tunnel `managed-remote` with your domain + account token for public URLs. Do NOT run a Quick tunnel with the real password for anything but a smoke test.
