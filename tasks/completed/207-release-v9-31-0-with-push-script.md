# Task 207: Release v9.31.0 with push script

**File:** `tasks/qa/207-release-v9-31-0-with-push-script.md`
**Source:** manager
**Type:** improvement
**Status:** open
**Mode:** autopilot-locked (manager said "use auto polit mode"; auto-closure approved)

## Goal

Cut release v9.31.0, move Unreleased entries under it, keep prompt in sync, and leave a ready push script.

## Manager's Notes

Manager asked to load memory, decisions, and release workflow, follow them, make the script ready, autopilot on, auto-closure fine. Autopilot locked. No-ferry rule applies. Past rulings used: QA-review autopilot cycle, no-ferry in autopilot, ZAC push-owned-by-manager, closure typos accepted.

## Local TODOs

- [x] Verify prompt sync, decide version, run full checks
- [x] Bump fragment version, rebuild prompt, move CHANGELOG
- [x] Write and chmod push script, lint and stage, run Brain QA and reviewer, close

## Acceptance Criteria

- [x] CHANGELOG has `## [9.31.0]` with moved Unreleased entries, Unreleased empty
- [x] Fragment version and system-prompt agree at 9.31.0, sync check passes
- [x] Full pytest suite passes with evidence recorded
- [x] `/tmp/cognitive-lead-push-release.sh` exists, executable, starts with `set -euo pipefail`, holds `VERSION="v9.31.0"`
- [x] `lint_task_file` passes, diff staged via stage tool

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with pyyaml --with mcp==1.30.0 python -m pytest tests/ -q`
- **Expected result:** all tests pass, exit 0
- **Actual result:** 237 passed, 8 warnings (baseline and post-release identical)
- **Exit code:** 0
- **Sync command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/sysprompt-check.md && diff -q /tmp/sysprompt-check.md system-prompt.md`
- **Sync result:** SYNC_OK, 81684 bytes, fragment and system-prompt agree at 9.31.0
- **Compile:** `python3 -m py_compile scripts/prompt-build/assemble_system_prompt.py mcp-lint-server/server.py` → COMPILE_OK
- **Script check:** `bash -n /tmp/cognitive-lead-push-release.sh` → SYNTAX_OK, executable bit set
- **Lint command:** `lint_task_file tasks/in-progress/207-release-v9-31-0-with-push-script.md`

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** branch is 57 commits ahead of origin, push may need rebase; CHANGELOG move may misplace categories.
- **Rollback plan:** reset CHANGELOG, prompt, and fragment files from git before staging; delete tag only if script created one locally.

---

## Execution Log & Reasoning

Autopilot locked per manager order. Plan: MINOR 9.31.0 since Unreleased holds Added workflow capabilities. Prompt behavior changes via prior tasks were deferred, so bump owed now. No assumptions yet.

Brain plan verdict (task_id 207, REPORT, no XML): Architect proposed MINOR 9.31.0, parse-then-append move, single fragment bump plus rebuild plus sync, ZAC no push or tag by Hands. Selected path recorded: conditional discovery first, then bump, rebuild, move, script, gates. Autopilot self-approval applied per no-ferry rule. Version source confirmed single file `prompts/fragments/01-system_version.md`. CHANGELOG duplicate Fixed merged into one. Baseline 237 passed, post-release 237 passed, sync OK, compile OK, script syntax OK.

QA verdict: QA_PASSED with cites on CHANGELOG, fragment, prompt, evidence. Reviewer round 1: APPROVED_WITH_CHANGES claiming missing Fixed header. Disputed with on-disk evidence: 9.31.0 block holds exactly one `### Fixed` at line 34, reviewer bullet at line 56 sits under it with no intervening header. Applying the hotfix would create a duplicate category, violating Parse-Then-Append. Fix rejected, re-review requested.

Reviewer round 2: technically approved, no blocking issue, keep file as is, PO review pending. Manager pre-approved auto-closure. Moving to qa, then closure.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 2faa908..92e60b6 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.31.0] - 2026-09-12
+
 ### Added
 
 - **Empty-output retry rule (Task 203):** executor bridge state machine gained step 5 — an empty-`output` REPORT is a transport flake, never a verdict: one lean retry (`include_bundle=false`, same task_id), then escalate. Lived during the self-judgment brainstorm round (2 empty REPORTs under history-bloat truncation). Executor doc is not a prompt-build input → no rebuild owed. Full suite: **264 passed**.
@@ -17,8 +19,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Token-optimization verified spike (Task 150):** Evaluated RTK 0.49.0 locally (musl binary, no global install): passing pytest suite collapses 1801 bytes / 21 lines → 44 bytes / 3 lines (**97.6% fewer bytes**, exit code preserved, 232 passed); small git outputs (±2%) not worth wrapping; `rtk diff` is a `/usr/bin/diff` wrapper (use `rtk git diff`); `rtk test` needs exact dep pins (`mcp==1.30.0` — `<` specs break as shell redirection). `headroom-ai` 0.37.0 (PyPI) and `@caveman-ai/cli` 1.3.3 (npm) registry-verified; proxy/pixel eval deferred (needs provider rewiring + manager approval). Claim scoped to passing suites — failing-suite trimming unmeasured. New `docs/loop-engine/configuration.md` holds the evidence table (with source column: local measurement vs tool self-report); `docs/opencode-shell-strategy.md` §8 holds the practices. Headroom/Caveman proxy integration and 10-task sprint measurement remain open follow-ups.
 - **Machine-readable QA verdicts + rules-first gate (Task 195):** QA persona (fragment 06) now ends every report with a machine verdict block (`VERDICT: QA_PASSED` / `QA_REJECTED` + `CITE: file:line` lines, single-regex parseable) with a documented escape hatch (unparseable → QA_REJECTED with reason, prose fallback, manager override). New `scripts/qa-rules-gate/rules_gate.py` runs verdict-parse, schema, budget, and allowlist checks before any LLM judge call — rule failures return QA_REJECTED without invoking the judge (Mock-asserted). 20 mocked tests (relative-path allowlist, exactly-one-verdict, whitespace tolerance, judge validation, nested schema, cite punctuation). System version 9.27.0 → 9.28.0, `system-prompt.md` rebuilt (sync-check byte-identical). Full suite: **239 passed**.
 
+- **Release push script (Task 207):** new ZAC-compliant `/tmp/cognitive-lead-push-release.sh` (`set -euo pipefail`, `VERSION="v9.31.0"`, clean-tree plus `gh auth status` checks, missing-tag creation, branch plus tag push, release create-or-verify, remote verification). Hands generate only, Manager runs it manually.
+
 ### Changed
 
+- **Prompt 9.30.0 → 9.31.0 (Task 207):** version fragment bumped, `system-prompt.md` reassembled (81684 bytes), sync check passed. Covers deferred bridge and executor capability changes.
+
 - **Systemd daemon env + docs (Task 206):** `opencode-server.service` (systemd user unit) gained `EnvironmentFile=-<hq>/.env` so the daemon-run OpenCode starts with keys + model pins — process env outranks every `.env` fallback and feeds `{env:}` forwarding, so all served projects share it. Verified via daemon-reload (`EnvironmentFiles` listed, service still running); restart deferred to Manager (kills live sessions). Documented in `docs/setup.md` (§Systemd user service env) and `LLM.txt` (§7.10, portable `%h` form for others).
 
 - **Cleanup sweep 9.30.0 (Task 205):** removed the dead 2026-09-09 pause narrative from live docs (executor bridge section, setup.md, README, LLM.txt) — the paused system was deleted during the bridge rebuild, never paused; deleted `archive/` (only a superseded RESTORE pointer) and its dead docs pointer; folded the loop-engine RTK evidence table into the shell strategy and removed `docs/loop-engine/`; README aligned to bridge reality; deleted the leftover `scripts/qa-rules-gate/` (zero live callers) and stripped its prose from the QA persona; shell strategy now mandates `rtk test` (binary installed) and mirrors the permission-layer git denies; LLM defaults to the latest OpenAI astra model on OpenAI-compatible transport. System version 9.29.0 → 9.30.0, prompt rebuilt (81684 bytes), sync check passed.
@@ -47,8 +53,6 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Guaranteed context bundle + autopilot saga rule (Task 190 overnight):** Executor autopilot gained Saga self-sufficiency — the Hands plays the manager role via manager-decision when an XML step says the manager copies, and hands results to the reviewer directly via `brain_turn` (ferrying through the human in autopilot is now a bug). Big-file-to-LLM research (blowsh spider workflow, Kokil 2026 long-context guide) concluded tool-use beats whole-file stuffing, so the bridge now auto-prepends a 5-file context bundle (`cognitive-executor.md`, `conventions.md`, `architecture.md`, `data_model.md`, `DESIGN.md`, 60k/file cap, `[missing]` markers) to every `brain_turn`, and exposes `read_file` (root-guarded, numbered lines) + `grep_files` (30-hit cap) for on-demand pulls of big files like full task files. Live bundle proof: HTTP 200, exact `BUNDLE_PROOF_OK`, all 5 files included-or-marked. Covered by 10 new mocked tests. Full suite: **139 passed**.
 
-### Fixed
-
 - **Reviewer hotfix on hunks path (Task 201):** QA/reviewer-like prompts now auto-attach the changed hunks even when the caller forgets `include_diff` (new pure `_failsafe_qa_attach` keyword gate + stderr warning; normal turns untouched); diff fence guard proven identical to the V1 task-attach guard; Modes docs now state prompt-level enforcement explicitly. Covered by 2 new tests (QA prompt attaches, normal prompt stays empty). Full suite: **264 passed**.
 
 ## [9.26.0] - 2026-09-11
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index e3b682f..2078c3c 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.30.0</system_version>
+<system_version>9.31.0</system_version>
diff --git a/system-prompt.md b/system-prompt.md
index 5380623..aea9c53 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.30.0</system_version>
+<system_version>9.31.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
```
<!-- END_GIT_DIFF -->
