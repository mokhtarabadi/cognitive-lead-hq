# Task 273: Release v9.46.0 with milestone-21 archive

**File:** `tasks/completed/273-release-v9-46-0-with-milestone-21-archive.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Cut release v9.46.0: archive completed tasks 266-272 into docs/history/milestone-21-summary.md, move CHANGELOG [Unreleased] under ## [9.46.0] - 2026-09-26, run all verification gates, generate the Manager-run push script.

## Manager's Notes

Direct Manager order: "load everything from memory and skills to make a new release." Follow memory release/release-workflow exactly: versioning-and-release + project-memory + verification-before-completion + task-lint skills loaded; archive-on-release mandatory; system-prompt.md already at 9.46.0 (tasks 268-271 bumped it, no hand-edit); [Unreleased] must be empty after release; ZAC holds (stage via MCP, commit via MCP after approval, tag/push/release via generated script run by Manager).

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Archive tasks 266-272 to docs/history/milestone-21-summary.md, git mv to tasks/archive/
- [x] Stale-memory audit report (flag only, no auto-delete)
- [x] Move CHANGELOG [Unreleased] entries under ## [9.46.0] - 2026-09-26, leave [Unreleased] empty
- [x] Run verification gates (lint_task_file, lint_markdown, lint_system_prompt_sync, py_compile, full pytest, check_docs_sync.py)
- [x] Generate /tmp/cognitive-lead-push-release.sh (VERSION=v9.46.0, chmod +x)
- [x] Stage via custom_context_stage_and_inject_diff, verify functionality

## Acceptance Criteria

- [x] AC1: docs/history/milestone-21-summary.md compacts tasks 266-272 and all 7 files are moved to tasks/archive/ (archive step mandatory per release memory)
- [x] AC2: CHANGELOG has ## [9.46.0] - 2026-09-26 with all prior [Unreleased] entries moved; [Unreleased] section empty; system-prompt.md version unchanged statement accurate (already built at 9.46.0)
- [x] AC3: all verification gates pass with exit code 0 and evidence recorded (pytest suite, lint_task_file, lint_markdown on edited files, lint_system_prompt_sync in sync, check_docs_sync.py OK)
- [x] AC4: /tmp/cognitive-lead-push-release.sh exists, executable, starts with set -euo pipefail, defines VERSION=v9.46.0, verifies clean tree + gh auth, creates annotated tag if missing, pushes commits + tags, creates or verifies GitHub release
- [x] AC5: stale-memory report produced and attached; no memory deleted without Manager approval

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q
- **Expected result:** full suite passes, exit code 0
- **Actual result:** 689 passed, 10 warnings in 5.02s; lint_task_file pass (273, post-move path); lint_markdown pass (milestone-21-summary.md, CHANGELOG.md); prompt re-assembly byte-identical (system-prompt.md untouched, in sync at 9.46.0); py_compile pass; check_docs_sync.py: docs-sync OK (2 warn-only orphans)
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** archive move or CHANGELOG rewrite loses task history or misattributes entries
- **Rollback plan:** history stays reachable via git log --follow on tasks/archive/; CHANGELOG edit is a single working-tree hunk revertible with git checkout before staging

---

## Execution Log & Reasoning

Release v9.46.0 executed per memory release/release-workflow (skills: versioning-and-release, project-memory, verification-before-completion, task-lint, archive-tasks, task-generator). Seat check: single-domain release ceremony → Code Reviewer at QA, no Brain planning round (release task follows the standing memory procedure, Brainstorm: not required — mechanical ceremony, fully reversible via git).
Milestone-21 draft delegated to a general subagent (7 files, 1054 lines) to preserve context; verified its claims by grep: sources 7x manager, types 1x feature + 6x improvement, AC boxes all checked, one wart found — task 271's Local TODO section left unchecked (8 boxes) while its AC went 6/6 checked; sealed file untouched, wart recorded honestly in the milestone Criteria Met row. Archive via `git mv` (tracked files, exit 0); completed/ verified empty. CHANGELOG: inserted `## [9.46.0] - 2026-09-26` + ceremony bullet between `[Unreleased]` and `### Added` (Parse-Then-Append, no dup headers; the `### Fixed` block below belongs to released 9.41.0, untouched). `lint_system_prompt_sync` MCP resolved the wrong root (global install) so sync was proven by direct re-assembly: byte-identical, zero diff. Push script written per memory spec (strict mode, VERSION=v9.46.0, clean-tree + gh auth preflight, tag-if-missing, push commits + tags, create-or-verify release), chmod +x, `bash -n` syntax OK.
Closure (2026-09-26): Manager ordered "close it" directly. No Brain review verdict was obtained for this task (review step skipped per explicit Manager order — recorded honestly, not backfilled). File moved tasks/qa/ → tasks/completed/ via git mv, header + Status synced, re-linted, re-staged, committed via commit_and_clean_task. Next: Manager re-runs /tmp/cognitive-lead-push-release.sh (it aborted earlier on dirty-tree preflight, which was correct), then tells me to restart OpenCode.

## Stale Memory Report

Searched project memory for task-number references (266-272), V1 leftovers (1.18/tui.json), and stacks/loop-engine: zero hits on all three queries. No stale or superseded entries flagged. No memory deleted (approval gate preserved).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 887d0c1..333e46a 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,8 +6,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.46.0] - 2026-09-26
+
 ### Added
 
+- **Release ceremony: milestone-21 archive + v9.46.0 push tooling (Task 273):** the 7 completed tasks (266-272) were compacted into `docs/history/milestone-21-summary.md` and moved to `tasks/archive/` **before** the release, the accumulated CHANGELOG `[Unreleased]` backlog was moved under `## [9.46.0] - 2026-09-26` leaving `[Unreleased]` empty, and an executable push script `/tmp/cognitive-lead-push-release.sh` was generated for Manager-run tagging, pushing and GitHub Release creation (strict mode, clean-tree and `gh auth` preflight, annotated tag created only if missing, release created or verified). `system-prompt.md` version unchanged — the shipped prompt was already built at 9.46.0.
+
 - **V2 401 fix + V2-major docs (Task 272 round 3):** fixed `Startup failed / OpenCode info endpoint responded with status 401` — V2 `opencode serve` randomizes its Basic-auth password every boot; synced one stable password (`~/.config/opencode/.server-password`, chmod 600) across `opencode-server.service.d/10-password.conf` and the `OPENCODE_SERVER_PASSWORD` line in `~/.config/openchamber/startup.env` (EnvironmentFile wins over drop-ins). Verified `/api/info` → 200 with auth, zero 401s, `[PushWatcher] connected`; stored as memory `opencode_config/v2_server_password_sync_2026_09_26`. Made the repo teach V2 to newcomers: `LLM.txt` gains an "Installing OpenCode V2" subsection plus V2 `plugins`/`cli.json`/`permission.shell` wording and a password-sync runbook (§7.9) with a `startup enable` re-apply warning; `README.md` plugins paragraph rewritten for V2; `docs/openchamber-tailscale.md` gains §2c-password, a corrected `:4096` health check (V2 needs auth), and a 401 troubleshooting row. All 1.22.2 pins → 2.x.
 
 - **Full-system V2 migration groundwork + OpenChamber 2.0.2 upgrade (Task 272):** audited every file referencing `tui.json` / `permission.bash` / `1.18.32` / `1.24.2` (AGENTS.md, README.md, skill-templates, docs/history, memories, archives). Mirrored `permission.bash` → `permission.shell` in both repo and global `opencode.json` (dual-key V1+V2 compat) and created global `~/.config/opencode/cli.json` mirror of `tui.json` (no project `cli.json` by design, V2 client config is global-only). Backed up `opencode.json`/`tui.json` (`.bak-272`) and `~/.config/opencode/` equivalents before changes. Round 1 verified `opencode --version` stayed 1.18.32 with V2-ready configs. Round 2 superseded this via `https://opencode.ai/v2/install` to 2.0.18, verified post-restart. Upgraded OpenChamber `1.24.2 → 2.0.2` via `openchamber update` (added 12, changed 191 packages, 25s), restarted `openchamber.service` (PID 1241698) and `opencode-server.service` (PID 179497) — both active, hot-reload + sessions intact. Updated `README.md` (Opencode V2 `cli.json`/`permission.shell` note) and `docs/openchamber-tailscale.md` (version bump + plugin-path note). Global npm proxy restored to `http://127.0.0.1:7890` after upgrade. Verification: `opencode --version` 2.0.18, `openchamber --version` 2.0.2 (see task 272).
diff --git a/docs/history/milestone-21-summary.md b/docs/history/milestone-21-summary.md
new file mode 100644
index 0000000..b43688d
--- /dev/null
+++ b/docs/history/milestone-21-summary.md
@@ -0,0 +1,102 @@
+# Milestone 21 Summary
+
+**Date:** 2026-09-26
+**Tasks Compacted:** 7 (266–272)
+
+## Source Distribution
+
+| Source       | Count |
+| ------------ | ----- |
+| manager      | 7     |
+| orchestrator | 0     |
+| telegram     | 0     |
+
+## Architectural Changes
+
+Prompt-contract milestone plus a full V2 platform migration. Tasks 268–271 each changed shipped-prompt behavior and bumped `<system_version>` 9.41.0 → 9.46.0: auditable brainstorm trigger with fragment-11 repair, a positive Manager-facing output-style contract, machine-enforced Strict Tooling Gates on all 13 stack skills with the dead `stacks/` folder removed, and a comprehensive executable-handoff contract for Programmer XML. Task 267 added the source-verified manager-decisions MCP contract doc. Task 272 migrated the live platform to Opencode 2.0.18 + OpenChamber 2.0.2 with dual-key V1/V2 configs and a stable server-password sync that fixed the V2 401. Task 266 was the previous release ceremony (v9.41.0 + milestone-20 archive).
+
+## Files Modified
+
+| File | Change |
+| ---- | ------ |
+| `docs/history/milestone-20-summary.md` | new: 33-task compaction (266) |
+| `docs/manager-decisions.md` | new: six-tool contract + drift table (267) |
+| `docs/setup.md` | cross-link to manager-decisions (267) |
+| `README.md` | doc links (267); V2 wording + plugins/cli.json (272) |
+| `docs/openchamber-tailscale.md` | V2 version + password-sync section + 401 rows (272) |
+| `LLM.txt` | V2 install subsection + password runbook (272) |
+| `prompts/fragments/01-system_version.md` | 9.41.0 → 9.42.0 (268) → 9.43.0 (269) → 9.44.0 → 9.45.0 (270) → 9.46.0 (271) |
+| `prompts/fragments/02-role.md` | answer-first after persona bracket (269) |
+| `prompts/fragments/07-agent_skills_registry.md` | strict-gate suffix on 13 stack lines (270) |
+| `prompts/fragments/09-hands_protocols.md` | strict tooling gate + fallback/skip schema (270); executable-handoff contract (271) |
+| `prompts/fragments/11-execution_workflow.md` | conditional brainstorm step, seven seats, blowsh pointer (268) |
+| `prompts/fragments/12-brainstorming_protocol.md` | `<auditability>` one-line rule (268) |
+| `prompts/fragments/13-constraints.md` | positive output-style contract + tell rules (269) |
+| `prompts/fragments/20-communication_examples.md` | prose good-versus-bad pairs (269) |
+| `system-prompt.md` | regenerated each bump 9.42.0 → 9.46.0 |
+| `agents/cognitive-executor.md` | brainstorm audit line (268); style mirror (269) |
+| `skill-templates/<13 stacks>/SKILL.md` | new Strict Tooling Gate sections (270) |
+| `skill-templates/testing-strategy/SKILL.md` | stacks pointer repointed to skill gate (270) |
+| `skill-templates/verification-before-completion/SKILL.md` | mandatory gate section (270) |
+| `stacks/` (5 YAMLs) | deleted, toolchain carried into skills (270) |
+| `opencode.json` (repo + global) | dual-key V1/V2 compat (272) |
+| `~/.config/opencode/cli.json` | new: V2 native global client config (272) |
+| `tests/test_prompt_sync.py` | version pins 9.42.0 → 9.46.0 + regression gates (268–271) |
+| `tests/test_skill_registry.py` | stacks read/assertion dropped (270) |
+| `CHANGELOG.md` | per-task Parse-Then-Append entries (all) |
+
+## Criteria Met
+
+| Task | Acceptance Criteria | Status |
+| ---- | ------------------- | ------ |
+| 266 | Archive first + completed/ empty; Unreleased empty under 9.41.0; suite + sync + prompt gates; task lint; push script strict + executable; MCP-staged, no commit; Manager handoff | ✅ Met (7/7) |
+| 267 | Six tools with signatures/effects/failures; file:line cites + BRAIN_MODEL correction; drift reported-not-fixed, zero source edits; enum/store/field contracts; README + setup links; Unreleased entry; suite + sync + lint green | ✅ Met (7/7) |
+| 268 | Fragment-11 seven seats + conditional; zero old-panel hits; user-prompts → blowsh; protocol audit line; executor mirror; 9.42.0 + byte-identical regen; Unreleased; suite + lint green | ✅ Met (8/8) |
+| 269 | Plan approved pre-edit; G1–G10 addressed/deferred; positive model; length budgets; structure rule; principle-based tells; open/close rules; C1 raised; 9.43.0 regen + pin; Unreleased | ✅ Met (10/10) |
+| 270 | 13 skills with exact strict sections; strict configs; completion gate; toolchain preserved; stacks/ deleted + test/pointer fixed; registry-consistent; framework enforcement; Unreleased; suite + lint; grep proofs | ✅ Met (10/10) |
+| 271 | Complete XML contract; placeholder/omission/vagueness bans; regression proof; prompt sync; targeted + lint green; CHANGELOG | ✅ Met (6/6 AC; Local TODO section left unchecked — sealed as-is) |
+| 272 | Opencode ≥ 2.0.15 (2.0.18); OpenChamber ≥ 2.0.0 (2.0.2) + sessions; no V1-only refs; 7/7 MCP + plugins load; lint + tests green; global install migrated | ✅ Met (6/6) |
+
+## Individual Task Summaries
+
+### Task 266: Release v9.41.0 with milestone-20 archive
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Cut release v9.41.0 by writing `docs/history/milestone-20-summary.md` covering 33 tasks (229–265) and moving them to `tasks/archive/` first, leaving `tasks/completed/` empty. Moved all `[Unreleased]` CHANGELOG entries under `## [9.41.0] - 2026-09-20`, leaving `[Unreleased]` empty with no duplicated headers. Verified with full 686-test suite, docs-sync, byte-identical prompt assembly, py_compile, and markdown/task lint; wrote executable `/tmp/cognitive-lead-push-release.sh` and closed on verbatim "Approved for closure" with tag `v9.41.0` public.
+
+### Task 267: docs: manager-decisions MCP tool schemas and usage contract for agents
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Wrote `docs/manager-decisions.md` (10 sections) as the source-verified contract for all six `manager_decisions` tools, every claim pinned by `file:line` citations at commit `0183433`. Corrected the issue body's false `DECISION_MODEL else BRAIN_MODEL` claim: only `DECISION_MODEL` overrides the default; `BRAIN_MODEL` is never read. Drift shipped as reported-not-fixed with zero server/skill edits; cross-linked README + setup; Brain QA + technical APPROVED; closes GitHub issue 25.
+
+### Task 268: Make the brainstorm trigger auditable and repair fragment 11
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Resolved the fragment 11 vs 12 contradiction (automatic step 2 vs conditional trigger) by making step 2 a conditional check naming the seven `<personas>` seats. Added the `<auditability>` rule: every plan states `Brainstorm: required | not required — reason`; cross-disciplinary plus hard-to-reverse work requires the full report, mirrored in the executor Planning Gate. Repaired the dead `user-prompts/` pointer to the `blowsh` skill; root cause was Task 180's snake_case-only grep missing display-form "Critical Thinker". Bumped 9.41.0 → 9.42.0, regenerated prompt, QA_PASSED + technical APPROVED.
+
+### Task 269: Make the Hands' output human-readable — output-style gap repair
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Ran four parallel research subagents plus a Manager-requested seven-seat brainstorm (O1 minimal style-contract patch selected), plan explicitly approved before edits. Closed gaps G1–G10 with a positive 8-rule output-style contract: answer-first after the persona bracket, length budgets (short 2–5 sentences; normal 80–180 words or ≤ 5 bullets), structure rule (prose 1–2, flat bullets 3–7, table only for repeated attributes), no preamble/recap, principle-based AI-tell rules replacing the 5-phrase ban. Kept English-only per stored ruling; bumped 9.42.0 → 9.43.0, QA_PASSED + APPROVED.
+
+### Task 270: Stack skill strict tooling gates and the stacks/ folder decision
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Proved `stacks/` had no live runtime consumer and deleted all 5 YAMLs after carrying every toolchain command into the owning skills. Researched all 13 stack skills and injected a uniform Strict Tooling Gate section into each (toolchain table, strict config + flags, fail-fast gate order, hallucination traps, evidence rows). Added framework enforcement in `09-hands_protocols.md` + verification skill; bumped to 9.44.0 then 9.45.0 across QA hotfixes; ended QA_PASSED + APPROVED with suite green.
+
+### Task 271: Generate Comprehensive Programmer XML Handoffs
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Root-caused generic handoffs to the template's code-block omission rule and replaced it with an executable-handoff contract (exact paths, complete code/diffs, full commands, named skills with reasons, per-step verification, AC + edge cases, placeholder ban). Brain plan approved by Manager; seat routing Architect + Programmer. Added 3 regression gates; targeted 268 passed, full 689 passed, QA_PASSED, review PO_REVIEW_PENDING, closed on approval.
+
+### Task 272: Full System Upgrade to Opencode V2 and OpenChamber V2
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Upgraded via the official V2 installer to Opencode 2.0.18 and OpenChamber 1.24.2 → 2.0.2 with dual-key compat configs (`permission.shell` alongside `bash`, `plugins` alongside `plugin`, global `cli.json` mirroring `tui.json`; no project `cli.json` by design). All 7 MCP servers load unchanged; fixed the round-3 V2 401 by syncing a stable `OPENCODE_SERVER_PASSWORD` across the service drop-in and OpenChamber `startup.env`. Taught the V2 path in `LLM.txt`, README, and tailscale docs; closed on "Approved for closure" after reviewer APPROVED relay.
```
<!-- END_GIT_DIFF -->
