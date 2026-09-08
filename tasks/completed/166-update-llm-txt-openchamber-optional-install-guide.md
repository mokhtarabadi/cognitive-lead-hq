# Task 166: Update LLM.txt with optional OpenChamber install guide

**File:** `tasks/qa/166-update-llm-txt-openchamber-optional-install-guide.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Add an optional OpenChamber install section to `LLM.txt` (ask user if needed) so new workstation setups can get multi-device remote access via Tailscale/Cloudflare Tunnel when they want it, without forcing it on everyone. Consolidate pending follow-up doc tweaks (Tailscale-only bind, auto-start, owt removal) that are currently unstaged.

## Manager's Notes

Manager 2026-09-08: "also update llm.txt to guide to install openchamber (optional) ask user if need." Prior follow-up 2026-09-08 already hardened OpenChamber to Tailscale-only `100.82.29.19:3005` (public refused), enabled auto-start (`systemctl --user enable` + `loginctl enable-linger`), fully removed `@nano-step/opencode-worktree-plugin` (`npm uninstall -g` + 7 command MDs) because OpenChamber native worktrees replace it. `LLM.txt` §7.8 already reflects owt removal. This task adds new §7.9 optional OpenChamber guide and stages the 5 currently-modified files.

## Local TODOs

- [x] Add `LLM.txt` §7.9 — optional OpenChamber install: ask user "Do you need multi-device remote access (phone/PC)?", prerequisites (Node≥22, OpenCode, Tailscale optional), `npm i -g @openchamber/web`, port choice (default 3000 occupied → 3005), Tailscale-only bind `--host 100.82.29.19`, UI password in `~/.secrets` (600) via env, verify (`status`, curl), auto-start (`startup enable` + linger), pairing (`connect-url --qr`), links to `docs/openchamber-tailscale.md`, Cloudflare deferred
- [x] Update verification checklist in `LLM.txt` §10 to reflect optional OpenChamber
- [x] Update `CHANGELOG.md` Unreleased (Parse-Then-Append)
- [x] Lint task file and Markdown
- [x] Stage all modified files via `custom_context_stage_and_inject_diff` and move to qa

## Acceptance Criteria

- [x] `LLM.txt` contains new §7.9 "Install OpenChamber (Optional — Multi-Device Remote Access)" that explicitly asks the user if they need it, lists prerequisites, install + Tailscale bind + password + auto-start + pairing steps, references `docs/openchamber-tailscale.md`, and notes Cloudflare Tunnel deferred
- [x] Verification checklist §10 has an optional OpenChamber check
- [x] Pending hardening docs are staged in same diff: `.gitignore`, `.opencode/memory/opencode_config/plugin_policy_dcp_only_2026_09_08.md`, `CHANGELOG.md`, `LLM.txt`, `docs/openchamber-tailscale.md` (no secrets in diff)
- [x] `lint_task_file` passes on this task file
- [x] `openchamber status` + `ss -tlnp` + curl checks still show Tailscale-only `100.82.29.19:3005` 200 / public 000 refused

## Verification Evidence

- **Test command:** `grep -n "Install OpenChamber" LLM.txt && grep -n "Do you need multi-device" LLM.txt && openchamber status; ss -tlnp | grep 3005; curl -s -o /dev/null -w "%{http_code}\n" http://100.82.29.19:3005/; curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://194.76.154.73:3005/ || echo "public refused"`
- **Expected result:** §7.9 heading + ask line present, status password:yes, LISTEN 100.82.29.19:3005, tailscale 200, public refused
- **Actual result:** `grep -n "7.9"` → 345: ## 7.9. (Optional) Install OpenChamber — Multi-Device Remote Access (Ask User First); `grep "Do you need multi-device"` → hit in §7.9 ask block; `openchamber status` → port 3005 PID 1684584 password:yes; `ss -tlnp` → 100.82.29.19:3005 LISTEN (not 0.0.0.0); `curl http://100.82.29.19:3005/` → 200; `curl http://194.76.154.73:3005/` → 000 / public refused (expected); loopback 000 refused expected when tailscale-bound; `grep -n "Task 166" CHANGELOG.md` → line 12 present
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Over-documenting OpenChamber could confuse fresh installs that don't need remote access; wrong port/host in guide could re-expose public 0.0.0.0
- **Rollback plan:** `git restore LLM.txt CHANGELOG.md` + re-run `lint_task_file`; re-add `owt` only if manager requests

---

## Execution Log & Reasoning

**2026-09-08 — Task 166 (follow-up to 165 hardening + owt removal):**

- Created `tasks/in-progress/166-update-llm-txt-openchamber-optional-install-guide.md` (NEXT_ID 166, dcp-only backlog→in-progress via mv, `**File:**` header updated)
- Edited `LLM.txt`: inserted new §7.9 “(Optional) Install OpenChamber — Multi-Device Remote Access (Ask User First)” after §7.8 — explicitly asks user “Do you need multi-device remote access (phone/PC)? … If yes I will install …; if not, skip” — covers prerequisites (Node≥22, OpenCode, Tailscale), port choice (3000 Next.js vs 3005 OpenChamber), `npm i -g @openchamber/web` 1.22.2, `~/.secrets/openchamber-ui-password` 600 via env, Tailscale-only bind `--host 100.82.29.19` (hardened from 0.0.0.0, public 194.76.154.73:3005 → refused), verify (`openchamber status`, `ss -tlnp`, curl 200/refused), auto-start (`startup enable` + `enable-linger`), pairing (`connect-url --qr`), link to `docs/openchamber-tailscale.md`, Cloudflare Tunnel deferred note; kept owt-removed context in §7.8
- Edited `LLM.txt` §10 verification checklist: added optional OpenChamber checkbox — if requested, checks `npm list -g`, `status password:yes`, `ss` 100.82.29.19:3005, tailscale 200/public refused, `startup status` enabled+active+lingering, runbook present; N/A if not requested
- Edited `CHANGELOG.md` Unreleased via Parse-Then-Append: appended bullet for Task 166 describing §7.9 ask, prerequisites, install, Tailscale bind, secrets, verify, auto-start, pairing, checklist, Cloudflare deferred
- Pending hardening docs remain unstaged from prior follow-up (Tailscale-only bind docs + owt removal): `.gitignore` (comment → owt removed), `.opencode/memory/opencode_config/plugin_policy_dcp_only_2026_09_08.md` (follow-up note), `CHANGELOG.md` (Task 165 hardened line), `LLM.txt` (owt-removed §7.8 + new §7.9), `docs/openchamber-tailscale.md` (§1-§2b, §6-§7 hardening) — all path-only, no secrets, will be staged together via this task's diff
- Verification: `grep -n "Install OpenChamber"` + `grep "Do you need multi-device"` hits, `openchamber status` password:yes PID1684584, `ss` 100.82.29.19:3005 LISTEN, curl tailscale 200 / public 000 refused / loopback 000 refused expected, CHANGELOG Task 166 present — evidence recorded above, exit 0
- Next: run `lint_task_file` on this task, `lint_markdown` on LLM.txt/CHANGELOG, then `custom_context_stage_and_inject_diff` with 5-file list and move to qa (ZAC, no git commit)

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.gitignore b/.gitignore
index af0c0a1..5178e68 100644
--- a/.gitignore
+++ b/.gitignore
@@ -42,6 +42,6 @@ downloads/
 # Goal plugin state (per-project)
 .opencode/goals/
 
-# owt worktree plugin state (per-project, Task 164)
+# worktree state (owt removed 2026-09-08 — keep guards if owt reinstalled; OpenChamber worktrees are SDK-managed)
 .opencode/worktrees/
 .opencode/worktree-sessions.json
\ No newline at end of file
diff --git a/.opencode/memory/opencode_config/plugin_policy_dcp_only_2026_09_08.md b/.opencode/memory/opencode_config/plugin_policy_dcp_only_2026_09_08.md
index ef1ac3f..559257d 100644
--- a/.opencode/memory/opencode_config/plugin_policy_dcp_only_2026_09_08.md
+++ b/.opencode/memory/opencode_config/plugin_policy_dcp_only_2026_09_08.md
@@ -2,7 +2,7 @@
 created_at: '2026-09-08T08:42:52.334419+00:00'
 status: active
 tags: []
-updated_at: '2026-09-08T08:42:52.334445+00:00'
+updated_at: '2026-09-08T11:15:00+00:00'
 ---
 
-2026-09-08 (Task 165): goal plugin (@prevalentware/opencode-goal-plugin) removed from all 4 opencode configs (global + repo opencode.json/tui.json → dcp-only) and worktree loader disabled (~/.config/opencode/plugins/worktree-plugin.js → .disabled). Reason: OpenChamber Session Goals replace goal-plugin; reduce proc/RAM sprawl. Re-enable: restore goal line in the 4 JSONs; mv .disabled back. Supersedes Task 126 (goal install) + Task 164 (owt install) until Manager says otherwise.
\ No newline at end of file
+2026-09-08 (Task 165): goal plugin (@prevalentware/opencode-goal-plugin) removed from all 4 opencode configs (global + repo opencode.json/tui.json → dcp-only) and worktree loader disabled (~/.config/opencode/plugins/worktree-plugin.js → .disabled). 2026-09-08 follow-up: owt fully removed (npm uninstall -g @nano-step/opencode-worktree-plugin + rm plugin + 7 command MDs) — verified OpenChamber 1.22.2 provides native worktrees (docs.openchamber.dev/worktrees + multi-run, UI dialog, isolate runs ≤5, Fusion). Reason: OpenChamber Session Goals + native worktrees replace both plugins; reduce proc/RAM. Re-enable owt only for CLI/headless without OpenChamber: npm install -g @nano-step/opencode-worktree-plugin && owt-setup install (see LLM.txt §7.8). Supersedes Task 126 + Task 164 until Manager says otherwise.
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index dd77287..ae12b65 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,7 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
-- **OpenChamber 1.22.2 over Tailscale on :3005 (Task 165):** Installed `@openchamber/web` globally (`npm i -g`, Node v24); daemon on `0.0.0.0:3005` in LAN mode (`:3000` Next.js app + `:8080` code-server untouched), UI password in `~/.secrets/openchamber-ui-password` (chmod 600, never committed), managed OpenCode on loopback (e.g. `127.0.0.1:44133`); loopback + Tailscale (`100.82.29.19:3005`) curls → 200, pairing links mint. Disabled goal plugin in all 4 opencode configs (global + repo `opencode.json`/`tui.json` now dcp-only — OpenChamber Session Goals replace it) and disabled worktree loader (`plugins/worktree-plugin.js` → `.disabled`; `/init-worktree` et al. dormant, Task 164 install reversed by Manager directive). New runbook `docs/openchamber-tailscale.md` (PC/Android pairing, QR discipline, revoke, troubleshooting). Cloudflare Tunnel deferred to follow-up task.
+- **OpenChamber 1.22.2 over Tailscale on :3005 (Task 165):** Installed `@openchamber/web` globally (`npm i -g`, Node v24); daemon on `100.82.29.19:3005` Tailscale-only bind `--host 100.82.29.19` (public `194.76.154.73:3005` refused — hardened from initial `0.0.0.0:3005` LAN bind; `:3000` Next.js app + `:8080` code-server untouched), UI password in `~/.secrets/openchamber-ui-password` (chmod 600, never committed) + `~/.config/openchamber/jwt-secret`/`startup.env` (600), managed OpenCode on loopback (e.g. `127.0.0.1:44133`); Tailscale `100.82.29.19:3005` → 200 (loopback/public both refused when tailscale-bound), pairing links mint. Auto-start at boot: `systemctl --user enable openchamber` + `loginctl enable-linger mohammad` (`enabled`/`Linger=yes`/`Restart=always`). Disabled goal plugin in all 4 opencode configs (global + repo `opencode.json`/`tui.json` now dcp-only — OpenChamber Session Goals replace it) and disabled worktree loader (`plugins/worktree-plugin.js` → `.disabled`; `/init-worktree` et al. dormant, Task 164 install reversed by Manager directive); **2026-09-08 follow-up: fully removed `owt` (`npm uninstall -g @nano-step/opencode-worktree-plugin` + `rm` plugin + 7 `command/*.md`) — OpenChamber native worktrees ([Worktree Sessions](https://docs.openchamber.dev/worktrees/) + [Multi-run](https://docs.openchamber.dev/multi-run/) via UI dialog, isolate runs ≤5, Fusion, Git view → Integrate) replace it; reinstall only for CLI/headless without OpenChamber (see `LLM.txt §7.8`)**. New runbook `docs/openchamber-tailscale.md` (§1-§7 + §2b auto-start, PC/Android pairing, QR discipline, revoke, troubleshooting, security notes). Cloudflare Tunnel deferred to follow-up task.
+- **LLM.txt optional OpenChamber guide (Task 166):** Added `LLM.txt` §7.9 “Install OpenChamber (Optional — Multi-Device Remote Access)” — asks user “Do you need multi-device remote access? …” before installing; prerequisites (Node≥22, OpenCode, Tailscale), `npm i -g @openchamber/web` 1.22.2, Tailscale-only `100.82.29.19:3005` bind (public `194.76.154.73:3005` refused), `~/.secrets` password (600) via env, verify (`status`, `curl`, `ss`), auto-start (`startup enable` + `enable-linger`), pairing (`connect-url --qr`), link to `docs/openchamber-tailscale.md`; Cloudflare Tunnel noted as deferred; updated §10 verification checklist with optional OpenChamber check.
 - **DCP dynamic context pruning like goal plugin (Task 163):** Added `@tarquinen/opencode-dcp` to `plugin` arrays in project `opencode.json` + `tui.json` (parity with global, mirrors `@prevalentware/opencode-goal-plugin` pattern from Task 126); extended `LLM.txt` §7 JSON example + TUI parity block + Option A note, new §7.7 DCP install/config/commands (`opencode plugin @tarquinen/opencode-dcp@latest --global`, `dcp.jsonc` global + `.opencode/dcp.jsonc` override, `/dcp` + `/dcp-compress`), verification checklist DCP checks. Installed globally + verified 4-way parity.
 - **owt worktree plugin (Task 164):** Installed `@nano-step/opencode-worktree-plugin` globally (`npm i -g` + `owt-setup install` → `~/.config/opencode/plugins/worktree-plugin.js` + 7 slash commands incl. `/init-worktree`, `/list-worktrees`, `/open-worktree`; file-based loading kept, `opencode.json`/`tui.json` untouched by design — npm spec resolves from project `node_modules` which this docs-only repo has none of, and owt is not a TUI panel plugin). Chose owt over `kdcokenny/opencode-worktree` (OCX-only, OCX not allowed) and `arturosdg/opencode-worktree` (standalone TUI). Project side: `.gitignore` guards (`.opencode/worktrees/`, `worktree-sessions.json`), new `LLM.txt` §7.8 install/commands/verify docs. Optional `owt hook --global` left disabled.
 
diff --git a/LLM.txt b/LLM.txt
index 99cba3e..d689db2 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -326,26 +326,88 @@ Defaults are applied automatically (enabled, autoUpdate, pruneNotification detai
 
 ---
 
-## 7.8. Install owt Worktree Plugin
+## 7.8. Worktree Support — OpenChamber Native (owt Removed 2026-09-08)
 
-owt (`@nano-step/opencode-worktree-plugin`, npm, MIT) manages git worktrees across parallel OpenCode sessions: plugin tools (`createworktree`/`deleteworktree`/`listworktrees` + system-prompt injection) + slash commands (`/init-worktree`, `/list-worktrees`, `/open-worktree`) + `owt` shell CLI (`status`/`diff`/`log`/`merge`/`commit`, terminal auto-detect, `node_modules` symlink). Chosen over `kdcokenny/opencode-worktree` (OCX-registry only — OCX is not allowed here) and `arturosdg/opencode-worktree` (standalone TUI, not a plugin).
+owt (`@nano-step/opencode-worktree-plugin`, npm, MIT) was installed in Task 164 (`npm install -g @nano-step/opencode-worktree-plugin` + `owt-setup install` → `~/.config/opencode/plugins/worktree-plugin.js` + 7 slash commands `/init-worktree` etc., `.gitignore` guards) and disabled in Task 165 (`.disabled`). **On 2026-09-08 it was fully removed** (`npm uninstall -g @nano-step/opencode-worktree-plugin` + `rm` plugin + 7 `command/*.md`) because **OpenChamber 1.22.2 provides first-class worktrees natively**: [Worktree Sessions](https://docs.openchamber.dev/worktrees/) (new-worktree dialog: new/existing branch, `OpenChamber makes the branch, sets up the folder, and starts a session in it`), [Multi-run](https://docs.openchamber.dev/multi-run/) (`isolate runs` → each run its own worktree/branch, up to 5 models), Fusion, and Git view → Integrate (merge worktree commits onto main). Use OpenChamber sidebar/dialogs for worktrees — owt is redundant when OpenChamber is running (confirmed via `packages/ui/src/lib/worktreeSessionCreator.ts`, `packages/docs/content/docs/worktrees.mdx`). No `openchamber --worktree` CLI flag exists — worktrees are GUI-driven.
+
+If you need CLI/headless worktrees **without** OpenChamber (SSH/CI), reinstall owt:
 
 ```bash
 npm install -g @nano-step/opencode-worktree-plugin
-owt-setup install
+owt-setup install  # restores plugin + 7 commands; restart OpenCode
+# optional: owt hook --global  # strips Co-authored-by via commit-msg hook (left disabled originally)
 ```
 
-`owt-setup install` copies the plugin to `~/.config/opencode/plugins/worktree-plugin.js` and slash commands to `~/.config/opencode/command/` (file-based loading — kept deliberately). The installer's config-based Option B (`"plugin": ["opencode-worktree-plugin"]` in `opencode.json`) is NOT adopted: it resolves from project `node_modules`, which this docs-only repo has none of, and the global file copy already covers every project session. `tui.json` is unchanged (owt is not a TUI panel plugin). Restart OpenCode after install (plugins + commands load at startup). Optional, not enabled: `owt hook --global` strips AI `Co-authored-by:` via a global `commit-msg` hook.
+Worktree state (owt, now removed): was under `.opencode/worktrees/` + `.opencode/worktree-sessions.json` (gitignored). OpenChamber worktrees are SDK-managed (probed via `git worktree list`, not that path).
+
+---
+
+## 7.9. (Optional) Install OpenChamber — Multi-Device Remote Access (Ask User First)
+
+OpenChamber (`@openchamber/web` 1.22.2, MIT, Node≥22) is the web/mobile/ desktop workspace that runs **on top of OpenCode** (this repo's agent harness). It gives you phone/PC remote access to the same OpenCode sessions via Tailscale, LAN, or Cloudflare Tunnel, plus native worktrees (see §7.8), Session Goals, Multi-run + Fusion, and GitHub integration. **You MUST ask the user before installing:**
+
+> "OpenChamber adds multi-device remote access (phone/PC) via Tailscale or Cloudflare Tunnel. Do you need remote access? If yes I will install it on a Tailscale-only port; if not, skip this section."
+
+Skip entirely if the user says no — the core OpenCode + MCP servers already work without it.
 
-Verify (project + global):
+### When to install
+
+- User wants to steer/review coding sessions from phone or a second PC (tailscale `100.x` or LAN IP).
+- User needs the OpenChamber UI (worktrees dialog, Multi-run ≤5, Fusion, walkthroughs) rather than bare `opencode` CLI.
+
+### Prerequisites (verify, do not assume)
+
+- `node --version` ≥22 (`lts/*`), `opencode --version` works, `tailscale status` shows peers if using Tailscale.
+- Default `:3000` is the Next.js (fa/en) app and `:8080` is code-server in this HQ setup — **do NOT use 3000** for OpenChamber; pick an alt port (recommended `:3005`).
+
+### Install + first run (Tailscale-only hardened)
 
 ```bash
-owt help && echo "owt CLI ✓"
-ls ~/.config/opencode/plugins/worktree-plugin.js && echo "global plugin ✓"
-ls ~/.config/opencode/command/init-worktree.md && echo "global commands ✓"
+# 1. Install globally (Node≥22 required)
+npm install -g @openchamber/web
+openchamber --version   # expect 1.22.2
+
+# 2. UI password — never commit, chmod 600, pass via env to avoid ps exposure
+mkdir -p ~/.secrets
+openssl rand -base64 24 > ~/.secrets/openchamber-ui-password
+chmod 600 ~/.secrets/openchamber-ui-password
+export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"
+
+# 3. Pick Tailscale IP and start daemon — bind ONLY to the tailnet (not 0.0.0.0)
+#    ss -tlnp must later show 100.82.29.19:3005, not 0.0.0.0:3005; public IP → refused is correct
+tailscale ip -4   # e.g. 100.82.29.19 — use this as --host
+openchamber status   # check nothing on :3005
+openchamber --lan --port 3005 --host 100.82.29.19 --server http://100.82.29.19:3005
+# alternative foreground form that startup uses:
+# openchamber serve --foreground --port 3005 --host 100.82.29.19 --ui-password "$OPENCHAMBER_UI_PASSWORD"
+
+# 4. Verify: Tailscale 200, public refused, loopback refused (when tailscale-bound)
+curl -s -o /dev/null -w "%{http_code}\n" http://100.82.29.19:3005/   # 200
+curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://194.76.154.73:3005/ && echo "PUBLIC OPEN" || echo "public refused (good)"
+curl -s -m 2 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3005/ || echo "loopback refused when tailscale-bound (expected)"
+openchamber status   # mode + password: yes
+ss -tlnp | grep 3005   # 100.82.29.19:3005 LISTEN
+
+# 5. Auto-start at boot (systemd user service, survives reboot/logout/crash)
+export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"
+openchamber startup enable --port 3005 --host 100.82.29.19
+sudo loginctl enable-linger $USER
+openchamber startup status   # startup enabled, service active, lingering enabled
+systemctl --user is-enabled openchamber   # enabled
+systemctl --user is-active openchamber    # active
+# restart test: openchamber stop --port 3005; sleep 6; systemctl --user is-active openchamber → active
+
+# 6. Pair a PC/phone (single-use expiring QR, revoke-able)
+openchamber connect-url --port 3005 --host 100.82.29.19 --qr   # or Settings → Remote Instances → Add device → Scope Anywhere/Home network only
+# PC on same tailnet: open http://100.82.29.19:3005 (Tailscale must show vm15996266)
+# Phone: Tailscale app joined to same tailnet, then open the same URL or scan QR in OpenChamber mobile/PWA
 ```
 
-Worktree state lives in the project (gitignored): worktrees under `.opencode/worktrees/`, session names in `.opencode/worktree-sessions.json`.
+Full runbook (daily commands, §2b auto-start, troubleshooting, security notes): `docs/openchamber-tailscale.md` — auto-generated after install and kept in repo.
+
+### Cloudflare Tunnel (deferred)
+
+Cloudflare Tunnel (`managed-remote` with your domain + account token) is the next step for public URLs without Tailscale. **Do NOT run a Quick tunnel with the real UI password for anything beyond a smoke test.** That step is intentionally deferred to a follow-up task — finish Tailscale first.
 
 ---
 
@@ -386,7 +448,8 @@ After completing all steps, verify:
 - [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 5 `mcp` entries (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`) + `blowsh_*`/`telegram_*` permissions, no former browser entry
 - [ ] `~/.config/opencode/opencode.json` + `tui.json` `plugin` arrays contain both `@prevalentware/opencode-goal-plugin` and `@tarquinen/opencode-dcp` (`grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/tui.json`); project `opencode.json` + `tui.json` match (`diff -q tui.json ~/.config/opencode/tui.json`)
 - [ ] DCP loads: `opencode plugin list` shows `@tarquinen/opencode-dcp`, `/dcp` panel opens, `~/.config/opencode/dcp.jsonc` created on first run (project `.opencode/dcp.jsonc` overrides if present)
-- [ ] owt loads: `owt help` prints usage, `~/.config/opencode/plugins/worktree-plugin.js` + `~/.config/opencode/command/init-worktree.md` exist, `/init-worktree` recognised after restart
+- [ ] worktrees: OpenChamber native via sidebar/dialog (`https://docs.openchamber.dev/worktrees/`) — no `owt` required; if owt reinstalled, `owt help` + `~/.config/opencode/plugins/worktree-plugin.js` + `/init-worktree` after restart
+- [ ] (optional) OpenChamber: if user requested multi-device, `npm list -g @openchamber/web` shows 1.22.2, `openchamber status` password:yes, `ss -tlnp | grep 3005` shows `100.82.29.19:3005` (not 0.0.0.0), `curl http://100.82.29.19:3005/ → 200` / public `194.76.154.73:3005 → refused`, `openchamber startup status` shows enabled+active+lingering, `docs/openchamber-tailscale.md` present; if not requested, this check is N/A
 - [ ] `~/.config/opencode/opencode.json` `blowsh` uses `docker run --rm -i ghcr.io/mokhtarabadi/blowsh-mcp:latest` (120s timeout) and `telegram` uses `uv --directory $HOME/.config/opencode/mcp-telegram-server run main.py` with allowed roots (`/tmp/telegram-mcp` + config dir downloads)
 - [ ] `~/.config/opencode/opencode-shell-strategy.md` exists (instructions file referenced by the `instructions` key)
 - [ ] `/tmp/cognitive-lead-hq` no longer exists
diff --git a/docs/openchamber-tailscale.md b/docs/openchamber-tailscale.md
index 2d604fe..3ba552e 100644
--- a/docs/openchamber-tailscale.md
+++ b/docs/openchamber-tailscale.md
@@ -6,25 +6,35 @@
 ## 1. What is running
 
 - **OpenChamber 1.22.2** (global npm: `@openchamber/web`), daemon PID varies — check with `openchamber status`.
-  - Web UI: `0.0.0.0:3005` (LAN mode, so Tailscale interfaces serve it too).
+  - Web UI: `100.82.29.19:3005` (Tailscale-only bind `--host 100.82.29.19`; public `194.76.154.73:3005` is **refused** — not `0.0.0.0`).
   - Managed OpenCode: auto-started by OpenChamber on a loopback-only port (e.g. `127.0.0.1:44133`, allocated dynamically) — never exposed directly.
   - UI password: enabled. Secret lives ONLY in `~/.secrets/openchamber-ui-password` (`chmod 600`). Never committed.
+  - Auto-start at boot: `systemctl --user is-enabled openchamber` → `enabled`, `loginctl show-user mohammad | grep Linger` → `Linger=yes`, `Restart=always` (`RestartSec=5`). Survives reboot & logout; crash → restart in 5s. Check with `openchamber startup status` + `systemctl --user is-active openchamber`.
 - **Default :3000 is NOT OpenChamber** — it is the pre-existing Next.js (fa/en) app. **:8080 is code-server.** Do not move OpenChamber onto either.
-- **Plugins:** opencode `plugin` arrays (global `~/.config/opencode/opencode.json` + `tui.json`, repo `opencode.json` + `tui.json`) are **dcp-only** (`@tarquinen/opencode-dcp@latest`). Goal plugin removed (overlaps OpenChamber Session Goals); worktree loader `~/.config/opencode/plugins/worktree-plugin.js` renamed to `.disabled` (its `/init-worktree` etc. slash commands are dormant, not deleted). Re-enable: restore the goal line in the 4 JSONs; `mv worktree-plugin.js.disabled worktree-plugin.js`.
+- **Plugins:** opencode `plugin` arrays (global `~/.config/opencode/opencode.json` + `tui.json`, repo `opencode.json` + `tui.json`) are **dcp-only** (`@tarquinen/opencode-dcp@latest`). Goal plugin removed (overlaps OpenChamber Session Goals); **worktree plugin `owt` (`@nano-step/opencode-worktree-plugin`) fully removed 2026-09-08** (`npm uninstall -g` + deleted `plugins/worktree-plugin.js` + 7 `command/*.md`; was `*.disabled` in Task 165). Reason: OpenChamber provides native worktrees (https://docs.openchamber.dev/worktrees/ + https://docs.openchamber.dev/multi-run/ — UI new-worktree dialog, isolate runs ≤5, Fusion, Git view → Integrate) — owt is redundant when OpenChamber is running. Reinstall only for CLI/headless without OpenChamber: `npm install -g @nano-step/opencode-worktree-plugin && owt-setup install` (see `LLM.txt §7.8`).
 
 ## 2. Daily commands (on the server, as `mohammad`)
 
 ```bash
 openchamber status                        # running runtimes (expect: port 3005, password: yes)
-curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3005/        # expect 200
-curl -s -o /dev/null -w "%{http_code}\n" http://100.82.29.19:3005/     # expect 200 (Tailscale IP)
+curl -s -o /dev/null -w "%{http_code}\n" http://100.82.29.19:3005/     # expect 200 (Tailscale IP; use this locally too)
+curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://194.76.154.73:3005/ && echo "PUBLIC STILL OPEN" || echo "public refused (good)"
+# note: http://127.0.0.1:3005/ is refused when bound to Tailscale IP — expected
 timeout 8 openchamber logs -p 3005 | head -n 30   # recent log (logs cmd follows; always wrap in timeout)
-openchamber --lan --port 3005 --server http://100.82.29.19:3005   # (re)start daemon after a stop
 export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"  # password via env, avoids ps exposure
-openchamber stop --port 3005              # stop this instance
+openchamber startup status                # startup enabled, service active, lingering enabled
+systemctl --user is-active openchamber   # should be active
+openchamber stop --port 3005              # stop this instance (systemd will restart in 5s due to Restart=always)
 openchamber update                        # update OpenChamber later
 ```
 
+### 2b. Auto-start at boot (systemd user service)
+
+- Enabled via `export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)" && openchamber startup enable --port 3005 --host 100.82.29.19` → writes `~/.config/systemd/user/openchamber.service` (`ExecStart=... serve --foreground --port 3005 --host 100.82.29.19`, `Restart=always`, `RestartSec=5`).
+- Lingering via `sudo loginctl enable-linger mohammad` → `loginctl show-user mohammad` shows `Linger=yes`, `State=active` — user manager starts at boot even without login.
+- Verification: `openchamber startup status` → `startup enabled`, `service active`, `user lingering enabled`; `systemctl --user is-enabled openchamber` → `enabled`; `systemctl --user is-active openchamber` → `active`; `ss -tlnp | grep 3005` → `100.82.29.19:3005` LISTEN; reboot → auto-starts, crash → restarts in 5s (`NRestarts` stays 0 when stable).
+- Re-enable after password change: repeat the `startup enable` command (it rewrites `startup.env` with the new password) — do **not** hand-edit `startup.env`/`jwt-secret` (both `600`).
+
 ## 3. Connect from a PC (mohammad-pc-1 / cando — Tailscale)
 
 1. Join the same tailnet on the PC (`tailscale status` must show `vm15996266`).
@@ -52,13 +62,17 @@ openchamber update                        # update OpenChamber later
 | Symptom | Check |
 |---|---|
 | Browser gets 307 → `/fa` on :3000 | You hit the Next.js app, not OpenChamber — use **:3005**. |
-| `curl` to :3005 hangs/refused | `openchamber status`; `ss -tlnp \| grep 3005`; restart per §2. |
+| `curl` to :3005 hangs/refused | `openchamber status`; `ss -tlnp \| grep 3005` should show `100.82.29.19:3005` LISTEN; `curl http://100.82.29.19:3005/` → 200; public IP → refused is expected. |
+| `curl http://127.0.0.1:3005/` refused | Expected — bound to Tailscale IP only, not `0.0.0.0`/`127.0.0.1`. Use `http://100.82.29.19:3005/` locally too. |
+| Startup not starting at boot | `systemctl --user is-enabled openchamber` → `enabled`; `loginctl show-user mohammad | grep Linger` → `yes`; `systemctl --user status openchamber`; `journalctl --user -u openchamber -n 30`. Re-enable: `export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)" && openchamber startup enable --port 3005 --host 100.82.29.19` + `sudo loginctl enable-linger mohammad`. |
 | Tailscale IP unreachable from phone/PC | `tailscale status` both ends; `tailscale ping 100.82.29.19`; ensure Tailscale is up (not logged out). |
 | Chat/notifications stall | Check `timeout 8 openchamber logs -p 3005`; managed OpenCode port (44133-ish) must stay loopback; restart instance. |
 | High RAM (7.8GB host) | `free -h`; `docker stats`; stop idle OpenChamber sessions; blowsh MCP pulls a Docker image per use. |
-| `/init-worktree` does nothing | Expected — worktree plugin is disabled (see §1). |
+| `/init-worktree` does nothing | Expected — worktree plugin `owt` was removed 2026-09-08 (OpenChamber native worktrees via UI; see §1 + `LLM.txt §7.8`). Reinstall only if you need CLI/headless without OpenChamber. |
 
 ## 7. Security notes
 
-- Tailscale tailnet = private irrespective of `--lan`; nothing here is on the public internet. Still: UI password stays ON, pairing links stay single-use, secrets never enter git/shell history (use the env-var form in §2).
+- Tailscale-only bind `--host 100.82.29.19`: `ss -tlnp` shows `100.82.29.19:3005` not `0.0.0.0:3005`; public IP `194.76.154.73:3005` → refused, loopback `127.0.0.1:3005` → refused — only tailnet peers (`mmokhtarabadi@gmail.com` tailnet, 5 peers) can reach it. Prior `0.0.0.0` bind was publicly reachable and has been hardened.
+- Secrets: `~/.secrets/openchamber-ui-password` (`600`), `~/.config/openchamber/jwt-secret` (`600`), `~/.config/openchamber/startup.env` (`600`, contains password for systemd — never committed). UI password stays ON, pairing links stay single-use and expire, passkeys clear on password change.
+- Auto-start: `openchamber.service` `enabled` + `Linger=yes` + `Restart=always` — survives reboot/logout/crash; verify with `openchamber startup status` and `systemctl --user is-active openchamber`.
 - Next step (separate task): Cloudflare Tunnel `managed-remote` with your domain + account token for public URLs. Do NOT run a Quick tunnel with the real password for anything but a smoke test.
```
<!-- END_GIT_DIFF -->
