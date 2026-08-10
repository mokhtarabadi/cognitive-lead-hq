# Task 86: Vendor OpenCode Shell Strategy Instructions

**File:** `tasks/backlog/86-vendor-opencode-shell-strategy.md`
**Source:** manager
**Type:** improvement
**Status:** open

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

- [ ] Fetch the upstream `shell_strategy.md`; vendor it as `docs/opencode-shell-strategy.md` with MIT attribution header
- [ ] Reconcile the vendored rules against `AGENTS.md`, `docs/conventions.md`, `system-prompt.md` (bash_phase CRITICAL RULE 1, ZAC commit lifecycle, permission denies) — document every delta/conflict decision in the execution log
- [ ] Add `"instructions": ["docs/opencode-shell-strategy.md"]` to repo `opencode.json` (path relative to config)
- [ ] Copy the file to `~/.config/opencode/opencode-shell-strategy.md`; add `"instructions": ["/home/mohammad/.config/opencode/opencode-shell-strategy.md"]` to global `opencode.json`
- [ ] Update `LLM.txt`: add a copy step for the file + add `instructions` to the Step-7 global config template
- [ ] Add `### Changed` entry to `CHANGELOG.md` `[Unreleased]` (Parse-Then-Append)
- [ ] Verify: JSON validity of both configs, file exists at all 3 paths, prettier/lint clean, opencode starts cleanly with the new instructions

## Acceptance Criteria

- [ ] Vendored file exists at `docs/opencode-shell-strategy.md` with MIT attribution
- [ ] Reconciliation documented — no platform rule weakened or contradicted (ZAC intact, non-interactive mandate intact)
- [ ] `instructions` wired in: repo `opencode.json`, global `opencode.json`, and `LLM.txt` (copy step + template)
- [ ] `CHANGELOG.md` `[Unreleased]` → `### Changed` entry present
- [ ] Both `opencode.json` files valid JSON; `opencode` starts without config errors

## Verification Evidence

- **Test command:** `python3 -m json.tool opencode.json` ; `python3 -m json.tool ~/.config/opencode/opencode.json` ; `ls docs/opencode-shell-strategy.md ~/.config/opencode/opencode-shell-strategy.md` ; `npx prettier --write docs/opencode-shell-strategy.md CHANGELOG.md LLM.txt` ; `opencode run "..."` (or `opencode --version`) for a clean-start smoke test
- **Expected result:** both configs valid; file present at repo + global paths; prettier clean; opencode starts without `ConfigInvalidError`
- **Actual result:** _(OpenCode fills this during execution)_
- **Exit code:** _(OpenCode fills this during execution)_

## Risk & Rollback

- **Risk:** Vendored rules conflict with or duplicate platform conventions (mitigated by the explicit reconciliation step); a malformed `instructions` entry breaks opencode startup.
- **Rollback plan:** Remove the `instructions` key(s) from `opencode.json` (repo + global) and delete the vendored file. Escape hatch if startup is already broken: run with `OPENCODE_DISABLE_PROJECT_CONFIG=1` to bypass the project config and fix it.

---

## OpenCode Execution Log & Reasoning

_(OpenCode: Manually log the vendoring, reconciliation decisions, config wiring, and verification evidence here BEFORE calling the MCP tool.)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
