# Task 274: Plugins full V2 status — verify latest, document, no duplicate upstream issues

**File:** `tasks/completed/274-plugins-full-v2-status-verify-latest-document-no-duplicate-upstream-issues.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Bring both OpenCode plugins to full V2 standing: verify latest V2-capable versions installed, file upstream issues only where none exist, update repo docs with exact V2 status.

## Manager's Notes

Manager order (Persian, 2026-09-26): do the needed work politely; be careful with any issue filing; update plugins that truly support V2 fully to V2; update docs as needed. Prior finding corrected during execution: goal-plugin 0.1.52 already contains full V2 adaptation (upstream PR #49 merged 2026-09-14, PR #58 merged/released 2026-09-26) — the earlier "V1-only" assessment was wrong (stale cache copy examined).

## Local TODOs

- [x] Verify installed versions via `opencode plugin list` (goal 0.1.52, dcp 3.2.0) vs npm latest
- [x] Check upstream goal-plugin repo: V2 adaptation already shipped (PR #49, #58); no issue to file
- [x] Check upstream DCP repo: V2-compat threads already open (#627, #628, #631, #632); no duplicate filing
- [x] Update README.md plugin section with exact V2 status per plugin
- [x] Update LLM.txt §7.7 with V2 status + ask-mode note + update procedure
- [x] CHANGELOG.md entry via Parse-Then-Append
- [x] Store memory `opencode_config/plugin_v2_status_2026_09_26`
- [x] Verify functionality

## Acceptance Criteria

- [x] Both plugins confirmed at latest stable with genuine V2 support (goal 0.1.52, dcp 3.2.0)
- [x] No duplicate upstream issues filed (verified existing threads first)
- [x] README.md + LLM.txt state exact V2 status, versions, and update procedure
- [x] `lint_task_file` passes on the active task file
- [x] `verification-before-completion` applied and evidence recorded

## Verification Evidence

- **Test command:** `rtk test opencode plugin list`
- **Expected result:** goal-plugin 0.1.52 + dcp 3.2.0 loaded, zero errors
- **Actual result:** `local.goal-mode.server 0.1.52` + `opencode-dcp 3.2.0` listed; npm view confirms both are latest stable (dcp betas are stale Mar/Apr experiments; goal 0.1.52 released 2026-09-26)
- **Exit code:** 0

> Verification runner rule: `opencode plugin list` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Docs overclaim V2 support if upstream regresses; mitigated by pinning exact versions + PR links
- **Rollback plan:** `git restore README.md LLM.txt CHANGELOG.md`; plugin versions untouched (no installs performed)

---

## Execution Log & Reasoning

Seat Check: single domain (docs + plugin audit) → Code Reviewer seat not needed; executor direct. `Brainstorm: not required — single-domain doc/audit task, no cross-disciplinary ambiguity`.

- Verified `opencode plugin list` → 0.1.52 + 3.2.0; npm confirms latest stable for both.
- Upstream goal-plugin: PR #49 (full V2 adaptation, beta-19425 contract, compaction context, restart recovery) merged 2026-09-14; PR #58 (V2 task recovery scoping) merged + released as 0.1.52 on 2026-09-26. No issue filed — nothing to ask.
- Upstream DCP (Opencode-DCP/opencode-dynamic-context-pruning): 20 open issues incl. active V2 threads #627 (v2 compat), #628 (/dcp-compress V2 palette), #631 (V2 setup), #632 (V2 compact tags). No duplicate filed — manager's compress flakiness matches known in-flight V2 work.
- Assumption A1: V2 host resolves npm packages at runtime (no extracted dist on disk; cache dirs metadata-only) — `plugin list` is source of truth. Reason: exhaustive find showed no dist/server.js for either plugin while list reports loaded versions.
- Docs updated: README.md plugin bullets + LLM.txt §7.7 V2 status/ask-mode/update procedure.
- Memory stored: `opencode_config/plugins_full_v2_status_2026_09_26` (no supersession — search found no prior plugin-status memory).
- Round 4 (post-verification edits): fixed `**File:**` header to in-progress path; README V2 paragraph now cites exact versions (goal 0.1.52 PR #49/#58, dcp 3.2.0, betas stale), `plugin list` as source of truth, and no-duplicate issue policy; LLM.txt §7.7 gained "Plugin V2 status" subsection; CHANGELOG [Unreleased] bullet added. Lint: task + README + LLM.txt + CHANGELOG all pass.
- Round 5 (Brain QA QA_PASSED + 2 nits fixed): added `### Added` under `[Unreleased]` (bullet no longer sits bare under the version header); README DCP bullet now reads `@latest (currently 3.2.0)` so it matches the pinned paragraph without misrepresenting the `@latest` config entry.
- Round 6 (Brain review + closure): Code Reviewer turn returned APPROVED with status PO_REVIEW_PENDING — "Code approved technically. PO, please review UX/Business logic. Reply Approved for closure to commit and finish." Relayed verbatim to Manager; Manager replied with the exact accept phrase "Approved for closure". File verified still in `tasks/qa/` before closure move.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 333e46a..904f324 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Added
+
+- **Plugin full-V2 status verification + docs (Task 274):** verified both plugins are at their latest stable V2-capable versions — `@prevalentware/opencode-goal-plugin@0.1.52` (released 2026-09-26; upstream V2 port PR #49 + PR #58) and `@tarquinen/opencode-dcp@3.2.0` (stable 2026-09-20 is newest; 3.2.1–3.2.8 betas are stale experiments; V2 `setup()` via `session` hooks; `compress.permission: ask` unsupported in V2 by DCP design, default `allow` stands). `opencode plugin list` is documented as the source of truth (`~/.cache/opencode/packages/` is metadata-only). Upstream-issue policy recorded in `README.md` and `LLM.txt` §7.7: search open threads first, never duplicate (DCP V2 threads #627/#628/#631/#632 already active) — no issues were filed.
+
 ## [9.46.0] - 2026-09-26
 
 ### Added
diff --git a/LLM.txt b/LLM.txt
index fd3329f..51f8314 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -384,6 +384,15 @@ Defaults are applied automatically (enabled, autoUpdate, pruneNotification detai
 
 > **Upstream note:** DCP development has slowed; new context-management work moved to `sleev` (`npm i -g sleev`). DCP remains available for OpenCode plugin users. If starting fresh and Sleev fits, prefer it; otherwise DCP stays supported here.
 
+### Plugin V2 status (verified 2026-09-26, opencode 2.0.18)
+
+Both plugins are at their latest stable versions and both are V2-capable upstream — no upgrade work remains:
+
+- **goal `@prevalentware/opencode-goal-plugin@0.1.52`** (released 2026-09-26; 0.1.50 Sep 21, 0.1.51 Sep 22): upstream V2 port merged via PR #49 (2026-09-14: beta-19425 contract, compaction context, restart transcript recovery, dual `[id, server, setup]` shape, V2 lifecycle smoke PASS) and PR #58 (merged + released same day: V2 task-recovery scoping). Open issue #54 is a V1-host registration bug whose body confirms `setupV2` targets V2 hosts.
+- **DCP `@tarquinen/opencode-dcp@3.2.0`** (stable, 2026-09-20): V2 `setup()` registers `session` hooks (`context`, `compaction`) — the documented V2 equivalents of V1 `experimental.chat.messages.transform`. The 3.2.1–3.2.8 betas are stale Mar/Apr experiments; stable 3.2.0 is newest. Known V2 gap, baked into DCP source: `compress.permission: ask` throws "not supported by OpenCode V2 public plugin API yet" — keep the default `allow`.
+- **Verification:** `opencode plugin list` must show `0.1.52` + `3.2.0` with zero errors — this is the source of truth (`~/.cache/opencode/packages/` holds metadata only, no `dist/`; the V2 host resolves npm at runtime).
+- **Upstream-issue policy:** search before filing, never duplicate. Goal repo: prevalentWare/opencode-goal-plugin. DCP repo: Opencode-DCP/opencode-dynamic-context-pruning (V2 threads #627 compat, #628 `/dcp-compress` palette, #631 V2 setup, #632 compact tags all active — file nothing there).
+
 ---
 
 ## 7.8. Worktree Support — OpenChamber Native (owt Removed 2026-09-08)
diff --git a/README.md b/README.md
index d01c387..8cd3d4d 100644
--- a/README.md
+++ b/README.md
@@ -478,9 +478,9 @@ opencode --agent cognitive-executor
 Both the repo (`opencode.json` + `tui.json`) and global (`~/.config/opencode/`) configs load two plugins:
 
 - **`@prevalentware/opencode-goal-plugin`** — `/goal` command with sidebar indicator, persistent state, idle continuation and plan-mode safety. Restored 2026-09-08 after the OpenChamber rollout; it coexists with OpenChamber Session Goals (TUI/CLI goals + web-UI Goals complement each other).
-- **`@tarquinen/opencode-dcp@latest`** — token saving via compress tool, deduplication and purge-errors.
+- **`@tarquinen/opencode-dcp@latest`** (currently 3.2.0) — token saving via compress tool, deduplication and purge-errors.
 
-Opencode V2 reads `plugins` from `opencode.json` (server/tools) and from the single global `~/.config/opencode/cli.json` (terminal client) — keep the entries identical. V1 fallbacks (`plugin` in `opencode.json` + `tui.json`) are kept alongside until V1 is fully retired. V2 prefers `permission.shell` over `permission.bash` (both kept). Full install/verify steps live in `LLM.txt` §7.
+Opencode V2 reads `plugins` from `opencode.json` (server/tools) and from the single global `~/.config/opencode/cli.json` (terminal client) — keep the entries identical. V1 fallbacks (`plugin` in `opencode.json` + `tui.json`) are kept alongside until V1 is fully retired. V2 prefers `permission.shell` over `permission.bash` (both kept). Both plugins are verified V2-capable at their latest stable versions: `@prevalentware/opencode-goal-plugin@0.1.52` (upstream V2 port: PR #49 dual runtime shape + PR #58 task-recovery scoping, 2026-09-26) and `@tarquinen/opencode-dcp@3.2.0` (V2 `setup()` via `session` hooks; stable 3.2.0 is newest — the 3.2.x betas are stale experiments). Verify with `opencode plugin list` (source of truth; cache dirs under `~/.cache/opencode/packages/` are metadata-only). Upstream-issue policy: search open threads first (goal: prevalentWare/opencode-goal-plugin; DCP: Opencode-DCP/opencode-dynamic-context-pruning — V2 threads #627/#628/#631/#632 already active) and never file duplicates. Full install/verify steps live in `LLM.txt` §7.
 
 > Install both plugins globally, then verify the packages actually landed (config references alone do not install them) and restart OpenCode before using `/goal` or `/dcp-compress`:
 >
```
<!-- END_GIT_DIFF -->
