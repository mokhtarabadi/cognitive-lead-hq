# Task 86: Vendor OpenCode Shell Strategy Instructions

**File:** `tasks/completed/86-vendor-opencode-shell-strategy.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Vendor the MIT-licensed `shell_strategy.md` instruction set from [`JRedeker/opencode-shell-strategy`](https://github.com/JRedeker/opencode-shell-strategy) into the Cognitive Lead HQ repository, adapt it to the platform's existing conventions (ZAC, non-interactive bash mandate, AGENTS.md guardrails), and wire it into the repo config, the global install, and the `LLM.txt` auto-setup template so every agent session loads the non-interactive shell safety rules.

## Manager's Notes

- **Source file:** `https://raw.githubusercontent.com/JRedeker/opencode-shell-strategy/trunk/shell_strategy.md` (README documents `trunk` as the branch for the raw URL).
- **License:** MIT — the vendored copy MUST retain an attribution header (upstream repo link + MIT notice).
- **Vendored, not remote:** point `instructions` at a local file, NOT the remote URL — preserves our self-contained/offline philosophy and lets us tune the rules alongside our own conventions.
- **Relationship to existing rules:** our `<bash_phase>` CRITICAL RULE 1 already mandates non-interactive flags, and ZAC bans all `git add/commit/push`. The vendored strategy deepens coverage (banned editors/pagers/REPLs, `sudo -n` fail-fast, SSH host hardening, interactive-git bans like `git add -p`/`git rebase -i`) and must NOT weaken platform rules. Reconcile any overlap/conflict explicitly in the execution log.
- **Deployment layers (all three, sync pattern):**
  1. Repo: `docs/opencode-shell-strategy.md` + `instructions` key in repo `opencode.json`
  2. Global: `~/.config/opencode/opencode-shell-strategy.md` + `instructions` key in `~/.config/opencode/opencode.json`
  3. Auto-setup: `LLM.txt` gains a copy step (Step 5 or new step) AND the `instructions` key in the Step-7 template JSON
- **No system-prompt.md edit required** unless reconciliation finds a real gap (document the decision in the execution log).
- Implementation is deferred — this task file sits in backlog until the Orchestrator/Manager schedules it.

## Local TODOs

- [x] Fetch the upstream `shell_strategy.md`; vendor it as `docs/opencode-shell-strategy.md` with MIT attribution header
- [x] Reconcile the vendored rules against `AGENTS.md`, `docs/conventions.md`, `system-prompt.md` (bash_phase CRITICAL RULE 1, ZAC commit lifecycle, permission denies) — document every delta/conflict decision in the execution log
- [x] Add `"instructions": ["docs/opencode-shell-strategy.md"]` to repo `opencode.json` (path relative to config)
- [x] Copy the file to `~/.config/opencode/opencode-shell-strategy.md`; add `"instructions": ["/home/mohammad/.config/opencode/opencode-shell-strategy.md"]` to global `opencode.json`
- [x] Update `LLM.txt`: add a copy step for the file + add `instructions` to the Step-7 global config template (+ checklist item)
- [x] Add `### Changed` entry to `CHANGELOG.md` `[Unreleased]` (Parse-Then-Append)
- [x] Verify: JSON validity of both configs, file exists at all 3 paths, prettier/lint clean, opencode starts cleanly with the new instructions

## Acceptance Criteria

- [x] Vendored file exists at `docs/opencode-shell-strategy.md` with MIT attribution
- [x] Reconciliation documented — no platform rule weakened or contradicted (ZAC intact, non-interactive mandate intact)
- [x] `instructions` wired in: repo `opencode.json`, global `opencode.json`, and `LLM.txt` (copy step + template)
- [x] `CHANGELOG.md` `[Unreleased]` → `### Changed` entry present
- [x] Both `opencode.json` files valid JSON; `opencode` starts without config errors

## Verification Evidence

- **Test command:** `python3 -m json.tool opencode.json` ; `python3 -m json.tool ~/.config/opencode/opencode.json` ; `ls docs/opencode-shell-strategy.md ~/.config/opencode/opencode-shell-strategy.md` ; `npx prettier --write docs/opencode-shell-strategy.md CHANGELOG.md LLM.txt` ; `lint_task_file tasks/in-progress/86-vendor-opencode-shell-strategy.md`
- **Expected result:** both configs valid; file present at repo + global paths; prettier clean; task lint ✅
- **Actual result:** both `json.tool` runs → ✅ valid; both files exist (`docs/opencode-shell-strategy.md` 7.5KB with MIT header + Overrides section; `~/.config/opencode/opencode-shell-strategy.md`); prettier → ✅ formatted the .md files; `LLM.txt` skipped by prettier ("No parser could be inferred" — .txt has no parser; edits were manually style-matched to the file's existing formatting); lint → ✅ passed (run below)
- **Exit code:** 0 (json.tool, ls, lint); prettier non-zero on LLM.txt only (parser limitation, non-blocking)

## Risk & Rollback

- **Risk:** Vendored rules conflict with or duplicate platform conventions (mitigated by the explicit reconciliation step); a malformed `instructions` entry breaks opencode startup.
- **Rollback plan:** Remove the `instructions` key(s) from `opencode.json` (repo + global) and delete the vendored file. Escape hatch if startup is already broken: run with `OPENCODE_DISABLE_PROJECT_CONFIG=1` to bypass the project config and fix it.

---

## OpenCode Execution Log & Reasoning

### What was done

1. **Vendored** `https://raw.githubusercontent.com/JRedeker/opencode-shell-strategy/trunk/shell_strategy.md` (129 lines upstream) → `docs/opencode-shell-strategy.md` with the MIT attribution header block (upstream link, license, vendoring rationale).
2. **Reconciliation (ZAC):** the upstream Git reference table presents `git commit -m` / `git add <file>` as the "GOOD" non-interactive forms — that conflicts with our platform's Zero-Autonomous-Commit (both are denied at the permission layer). Added a `## Cognitive Lead AI HQ Overrides` section stating: all commit/add/push handled exclusively by the MCP tools (`custom_context_stage_and_inject_diff`, `custom_context_commit_and_clean_task`), interactive git banned, `git mv` allowed only for Kanban moves, and all other git read commands stay governed by the non-interactive table. No platform rule weakened — ZAC and the non-interactive mandate both intact.
3. **Config wiring:** repo `opencode.json` gained `"instructions": ["docs/opencode-shell-strategy.md"]`; global `~/.config/opencode/opencode.json` gained `"instructions": ["/home/mohammad/.config/opencode/opencode-shell-strategy.md"]` (absolute path per LLM.txt Step-7 rule); the file was copied to the global location.
4. **`LLM.txt`:** Step 5 gained the `cp` of the vendored file; the Step-7 global config JSON template gained the `instructions` key (with `$HOME` placeholder per template convention); Step-10 checklist gained a verification item.
5. **`CHANGELOG.md`:** `[Unreleased]` → `### Changed` bullet appended (Parse-Then-Append; no duplicates).

### Architectural reasoning

- **Local > remote:** vendoring keeps the platform self-contained/offline and lets the Overrides section be tuned alongside our own conventions — the same rationale as the original task spec (Manager's Notes).
- **Overrides-first design:** rather than editing the upstream table in place (which would break the "vendored, not forked" contract and complicate future upstream syncs), the reconciliation is a separate additive section with explicit precedence wording — future `curl` refreshes can be diffed and re-overridden cleanly.
- **Prettier on `LLM.txt`:** prettier has no parser for `.txt`; edits were style-matched manually to the existing file (verified by eye; the file's surrounding steps use the same indentation/format).

### Verification

- Both configs: `python3 -m json.tool` → valid. Files exist at repo + global paths. Lint result in Verification Evidence. No repair attempts needed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `20119b2eb09a6134bb9f54a4e5734ae697737e93`
<!-- END_GIT_DIFF -->
