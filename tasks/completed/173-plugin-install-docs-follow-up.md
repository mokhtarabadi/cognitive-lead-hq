# Task 173: Plugin Install Docs Follow-Up

**File:** `tasks/completed/173-plugin-install-docs-follow-up.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Source Context

## Goal

Document the plugin install + verify steps that the /dcp-compress outage exposed (referenced-but-never-installed plugins).

## Manager's Notes

- Add explicit goal-plugin install command + cache-presence verification to LLM.txt §7.7 and README plugins section.
- Trigger: `@tarquinen/opencode-dcp` + `@prevalentware/opencode-goal-plugin` were referenced in all 4 configs but never installed; fixed globally during diagnosis.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Add install + verify docs to LLM.txt and README
- [x] Lint both files, stage, verify no secrets

## Acceptance Criteria

- [x] LLM.txt documents both plugin installs + cache verification + restart requirement
- [x] README mirrors the install/verify block
- [x] Both files lint clean

## Verification Evidence

- **Test command:** `lint_markdown` on LLM.txt + README.md
- **Expected result:** both pass
- **Actual result:** both passed
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Docs-only change; no code impact.
- **Rollback plan:** Revert the two hunks.

---

## Execution Log & Reasoning

Docs-only follow-up to the /dcp-compress outage: root cause was referenced-but-never-installed plugins (packages land in `~/.cache/opencode/packages/` only via `opencode plugin <mod> -g`, and slash commands appear after restart). LLM.txt §7.7 now carries both install commands + cache verification + restart warning; README plugins section mirrors it. CHANGELOG carries a Task 173 bullet under Changed; memory workflow carries the plugin-install lesson (Update 2026-09-09).

QA round 1 verdict: QA_REJECTED on C1 (LOW scope creep — one DECISION env-passthrough sentence from the 170/171 domain bundled in the 2026-09-08 memory entry). Fix applied: sentence removed from the memory file (2026-09-09 plugin-install lesson kept); `lint_markdown` re-passed. C2/C3/C4 passed.

Post-restart pipeline (manager order: QA → reviewer → auto-close, Telegram gate waived): QA rounds 2+ hit endpoint flakiness (empty REPORTs, one 69KB non-verdict ramble, one confabulating loop). Transcript reset twice (backups /tmp/transcript-173-backup.jsonl, /tmp/transcript-173-pre-reset.jsonl). Final QA with the literal 6473-char staged diff embedded returned QA_PASSED (C1-C4 PASS, grounded). Code Reviewer returned APPROVED (after 2 empty-report flakes, minimal-prompt retry). Deterministic tool verification (independent of persona lane): staged set = exactly the 4 docs + task file, all Markdown; secret regex CLEAN; zero 'decision' on '+' lines (13 hits all space-prefixed context); single 'token' hit is benign prose; lint_task_file + lint_markdown PASS. Telegram gate skipped per explicit manager waiver. Auto-closing.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/workflows/global-install-upgrade.md b/.opencode/memory/workflows/global-install-upgrade.md
index 281c62d..075b61d 100644
--- a/.opencode/memory/workflows/global-install-upgrade.md
+++ b/.opencode/memory/workflows/global-install-upgrade.md
@@ -110,5 +110,6 @@ The installed copy at `~/.config/opencode/mcp-telegram-server` is a git clone of
   - **Update 2026-09-05:** Telegram MCP fast-forwarded `3c37edb` → `7623e6b` (v3.2.31). Upstream PRs #206, #207, #210. PR #201 already in upstream — `merge --ff-only` + `push fork main`. Tests: 476 passed.
   - **Update 2026-09-08:** Per Manager directive, Telegram MCP switched from fork to **upstream chigwell/telegram-mcp directly** — `fork` remote removed (`git remote remove fork`), `origin` = https://github.com/chigwell/telegram-mcp.git only. Installed `main` now tracks `origin/main` at `c9460f8` (v3.2.32, PR #213 forward-routing). Fork patch already upstreamed (3c37edb ancestor of origin/main verified). Tests: 506 passed. No fork push needed.
   - **Update 2026-09-08 (Tasks 167/168):** persona + manager_decisions MCP servers installed globally (absolute paths, 600s timeouts since the slow-LLM fix); `manager-decision` skill synced (32 total); executor agent synced; project `.env` backed up to `~/.config/opencode/.env` (chmod 600). Decision store is per-project (`<project>/.opencode/decisions`, auto-created; global templates at `~/.config/opencode/.opencode/decisions/`).
+  - **Update 2026-09-09 (plugin install lesson):** config references ≠ installed — goal + DCP plugins were listed in all 4 configs but absent from `~/.cache/opencode/packages/` (that's why `/dcp-compress` didn't exist). Installing = `opencode plugin <mod> -g`, verifying = `ls -d ~/.cache/opencode/packages/<scope>/<pkg>@latest`, slash commands appear only after restart. NEVER run `opencode plugin list` — the CLI treats `list` as a package name and installs junk (`list@latest` + fake `.opencode/opencode.json`); verify via config greps + cache listing instead.
 
 Supersedes: workflows/global-install-upgrade (prior revision: 31 skills, 5 MCPs).
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5a97e99..135a8ae 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -27,6 +27,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **MCP uv-workspace cleanup + approval notes + split models (Task 170):** shared `mcp-common` lib (dotenv loader, single home); per-server `pyproject.toml` + committed `uv.lock` for all 5 servers; launch commands switched to locked `uv run --project <dir> <dir>/server.py` in repo + global configs; approval gates accept an optional manager note (force-reply, 300s independent timeout, silence/`/skip` → None, gate never blocks); `DECISION_MODEL` env splits extraction model from `PERSONA_MODEL` (blank = fallback); full suite **108 passed**.
 - **Ops follow-ups:** persona/decision server timeouts 120s → 600s (LLM reasoning turns need headroom); decision store moved `packages/cognitive-lead-decisions` → per-project `.opencode/decisions` with cwd-aware resolution (`DECISION_REPO_PATH` → `<cwd>/.opencode/decisions` → install-root fallback), so every repo keeps its own manager notes.
 - **QA round 2 fixes (Task 171 pipeline):** `DECISION_TEMPERATURE` env (default 1.0, clamped) replacing the hardcoded 0.2 in extraction; dotenv loader reads `utf-8-sig` (BOM-proof); `docs/conventions.md` codifies the blank-means-unset rule; parser/export/skip/docstring-guard tests added; dispatch no longer appends task bodies to transcripts (was causing 6MB transcripts → endpoint 400s). Full suite **120 passed**.
+- **Plugin install docs (Task 173):** `LLM.txt` §7.7 + README plugins section now carry both plugin install commands, cache-presence verification (`~/.cache/opencode/packages/`), and the restart requirement — closing the referenced-but-never-installed gap that hid `/dcp-compress`.
 
 ### Removed
 
diff --git a/LLM.txt b/LLM.txt
index 555f463..d117f09 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -348,9 +348,10 @@ DCP (`@tarquinen/opencode-dcp`, 4.2k stars, AGPL-3.0) reduces token usage via co
 
 ```bash
 opencode plugin @tarquinen/opencode-dcp@latest --global
+opencode plugin @prevalentware/opencode-goal-plugin --global
 ```
 
-This adds `@tarquinen/opencode-dcp` to `~/.config/opencode/opencode.json` + `tui.json`. Ensure the project files match (already committed in this repo):
+This adds both plugins to `~/.config/opencode/opencode.json` + `tui.json`. Ensure the project files match (already committed in this repo):
 
 ```bash
 grep -q "@tarquinen/opencode-dcp" opencode.json && echo "project opencode.json DCP ✓"
@@ -359,6 +360,14 @@ grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && echo "glob
 grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/tui.json && echo "global tui.json DCP ✓"
 ```
 
+> **References ≠ installed (learned 2026-09-09):** config entries alone do NOT install plugins — the packages must land in `~/.cache/opencode/packages/`, and slash commands (`/goal`, `/dcp`, `/dcp-compress`) only appear after an OpenCode **restart**. Always verify:
+>
+> ```bash
+> ls -d ~/.cache/opencode/packages/@tarquinen/opencode-dcp@latest ~/.cache/opencode/packages/@prevalentware/opencode-goal-plugin@latest && echo "plugins installed ✓"
+> ```
+>
+> Then restart OpenCode before testing `/goal` or `/dcp-compress`.
+
 ### DCP configuration (dcp.jsonc)
 
 DCP uses its own config file, searched in order (project overrides global). Restart OpenCode after changes:
diff --git a/README.md b/README.md
index e4549c8..48db30c 100644
--- a/README.md
+++ b/README.md
@@ -494,6 +494,14 @@ Both the repo (`opencode.json` + `tui.json`) and global (`~/.config/opencode/`)
 
 OpenCode 1 reads `plugin` from **both** `opencode.json` (server/tools) and `tui.json` (sidebar/palette) — keep the arrays identical. Full install/verify steps live in `LLM.txt` §7.
 
+> Install both plugins globally, then verify the packages actually landed (config references alone do not install them) and restart OpenCode before using `/goal` or `/dcp-compress`:
+>
+> ```bash
+> opencode plugin @prevalentware/opencode-goal-plugin --global
+> opencode plugin @tarquinen/opencode-dcp@latest --global
+> ls -d ~/.cache/opencode/packages/@tarquinen/opencode-dcp@latest ~/.cache/opencode/packages/@prevalentware/opencode-goal-plugin@latest && echo "plugins installed ✓"
+> ```
+
 ---
 
 ## Key V9 Changes
```
<!-- END_GIT_DIFF -->
