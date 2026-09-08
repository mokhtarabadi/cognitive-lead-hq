# Task 166: Update LLM.txt with optional OpenChamber install guide

**File:** `tasks/completed/166-update-llm-txt-openchamber-optional-install-guide.md`
**Source:** manager
**Type:** improvement
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `2d91cbfe1b22a3628be88b6e3f2249a1dd6af9f1`
<!-- END_GIT_DIFF -->
