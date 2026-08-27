# Task 116: FreeBuff Documents: Install Docs, Full Cognitive Executor Rules Port, and Global/Project AGENTS Merge

**File:** `tasks/completed/116-freebuff-docs-executor-rules-agents-merge.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Complete the FreeBuff documents capability: (1) document in the project exactly how to INSTALL the new FreeBuff global-rules file (`freebuff/AGENTS.global.md` → `~/.AGENTS.md`), (2) write the SAME Cognitive Executor rules and policies we have in OpenCode (`agents/cognitive-executor.md`) into the FreeBuff global file — full parity, not the current distilled summary — and (3) guarantee that for ALL projects, when both a global AGENTS config (`~/.AGENTS.md`) and a project AGENTS config (`AGENTS.md`) exist, BOTH are loaded and used correctly in every runtime.

## Manager's Notes

- Manager directive (2026-08-26): "Add support for FreeBuff documents and editing... add the Cognitive Executive Rule to the Agents Global file, and also document it in our project so we know what to do to install the new FreeBuff file. Also add it for this same project: exactly the same Cognitive Executor rules and policies we have in OpenCode need to be written into it. Also make sure that when we have a global Agents config and the project also has an Agents config file, for all projects both of them are used correctly."
- The Freebuff knowledge-file system is already understood and documented (source-verified 2026-08-26): home `~/.AGENTS.md` > `~/.CLAUDE.md`; project `AGENTS.md` > `CLAUDE.md` > `*.knowledge.md` per directory; `~/.knowledge.md` and bare `knowledge.md` are IGNORED (left the priority list in 0.0.156). Freebuff has NO role/persona feature — always-loaded roles are knowledge-file sections. See `docs/freebuff-documents.md` and `docs/freebuff-support.md` §2.6.
- Current state: `freebuff/AGENTS.global.md` already carries a **distilled** `# Cognitive Executive Role (Always Loaded)` section (Identity & Mission / Standing Duties / Hard Boundaries), synced to `~/.AGENTS.md`. The user now wants the **full** `agents/cognitive-executor.md` rules/policies ported — not just the summary.
- Source of truth for the rules to port: `agents/cognitive-executor.md` (OpenCode format). Sections to port with Freebuff adaptations:
  - **Core Protocol** — entry point (AGENTS.md-first), rule validation (HALT + `⚠️ RULE VIOLATION WARNING`), MCP-first context (`custom_context` tools), skill loading, ZAC, finalization & closure sequence (`custom_context_stage_and_inject_diff` / `custom_context_commit_and_clean_task`)
  - **Task Lifecycle & Kanban State Enforcement** — discovery (no move), implementation (`tasks/in-progress/`), QA (`git mv` to `tasks/qa/` + `**File:**` metadata sync + re-stage), closure (`tasks/completed/`, status `closed`, only on explicit Manager authorization)
  - **Skill Auto-Loading Matrix** — full table, with Freebuff adaptation (`skill` tool → `/skill:<name>` slash command)
  - **Direct Input (Ad-Hoc) Validation Protocol** — intent validation, task-file enforcement, skill loading, plan & halt, ZAC reminder
  - **Context Bootstrapping & Memory Protocol** — `search_memory` first, apply constraints, strict `store_memory` criteria
  - **Subagent Delegation for Context Discovery** — delegate `<hands_discovery_task>` / discovery phases to `cognitive-discovery` (Freebuff: `spawn_agents` on paid tier; free tier falls back to MCP `read_source_files`/`get_directory_tree`)
  - **Communication Patterns** — reference points (D/F/R/Q/A), positive/negative patterns
  - **Execution Discipline** — Plan-Execute-Observe, circuit breakers (`⚠️ CIRCUIT BREAKER`), reasoning drift prevention
  - **Hard Operational Boundaries**
- Install documentation requirement: the project must explain "what to do to install the new FreeBuff file" — the exact commands (`cp freebuff/AGENTS.global.md ~/.AGENTS.md`, `diff -q` verification), prerequisites (Freebuff CLI, `~/.agents/` install per `LLM.txt` Step 7.5), when to (re)install (first install, after any edit, after machine reinstall), and rollback (re-copy from repo source). Extend `docs/freebuff-documents.md` (currently §3 covers editing; add a dedicated install subsection) and/or `docs/freebuff-support.md`.
- Global+project merge requirement: verify and document that a session in ANY project with both a global `~/.AGENTS.md` and a project `AGENTS.md` loads BOTH files. Freebuff: home knowledge files and project knowledge files are both injected into the system prompt (project wins on conflicting lines) — verify against the loader (`sdk/src/run-state.ts`: `loadUserKnowledgeFiles` + `selectKnowledgeFilePaths`) and document the merge/precedence in `docs/freebuff-documents.md`. OpenCode: global rules are loaded via `~/.config/opencode/opencode.json` `instructions` + the project `AGENTS.md` — verify both load and document. Fix any gap found (e.g., conflicting directives, missing global load in one runtime).
- This task file was created by reading `skill-templates/task-generator/SKILL.md` manually (the skill cannot be invoked in this session) and following the canonical Variant C (manager) template, including the Factual Git Diff block with its BEGIN/END markers as specified by the skill.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Initial codebase exploration (read `agents/cognitive-executor.md`, `freebuff/AGENTS.global.md`, `freebuff/agents/cognitive-executor.ts`, `docs/freebuff-documents.md`, `docs/freebuff-support.md`, `LLM.txt` Step 7.5)
- [x] Map every section of `agents/cognitive-executor.md` → Freebuff-adapted equivalent; note every OpenCode-only tool (`apply_patch`, `task` tool, `skill` tool) that needs a Freebuff translation
- [x] Port the FULL Cognitive Executor rules/policies into `freebuff/AGENTS.global.md` (expand the role section to full parity with the OpenCode agent, preserving the distilled core + adding the missing protocol sections)
- [x] Add the FreeBuff global-rules install procedure to `docs/freebuff-documents.md` (and/or `docs/freebuff-support.md`): prerequisites, exact `cp` + `diff -q` commands, reinstall triggers, rollback
- [x] Verify + document the global (`~/.AGENTS.md`) + project (`AGENTS.md`) AGENTS merge for BOTH runtimes (Freebuff knowledge-file loader; OpenCode global instructions + project AGENTS.md); fix any gap found
- [x] Sync `~/.AGENTS.md` from the versioned source; `diff -q` clean
- [x] Verify functionality: `lint_task_file`, prettier, full test suite

## Acceptance Criteria

- [x] `freebuff/AGENTS.global.md` contains the SAME Cognitive Executor rules and policies as `agents/cognitive-executor.md` (core protocol, Kanban lifecycle + metadata sync, skill auto-loading matrix, direct-input validation, memory protocol, subagent delegation, communication patterns, execution discipline, hard boundaries), each adapted to the Freebuff runtime (`/skill:<name>` slash commands, `custom_context` MCP tools, `git mv` Kanban rules, MCP stage/commit tools); the installed `~/.AGENTS.md` is byte-identical to the versioned source (`diff -q` clean)
- [x] The project documents "what to do to install the new FreeBuff file": exact install/verify/reinstall/rollback commands for `freebuff/AGENTS.global.md` → `~/.AGENTS.md`, referenced from `docs/freebuff-documents.md` (new install subsection) and cross-linked from `docs/freebuff-support.md` / `LLM.txt` Step 7.5 where applicable
- [x] Global + project AGENTS merge is verified for ALL projects in BOTH runtimes: Freebuff loads both `~/.AGENTS.md` and the project `AGENTS.md` (project wins on conflicting lines — verified against the loader), OpenCode loads both the global instructions and the project `AGENTS.md`; the behavior is documented in `docs/freebuff-documents.md`, and any gap found was fixed
- [x] `CHANGELOG.md` updated (Keep a Changelog, `[Unreleased]`), `lint_task_file` passes on this task file, and the repo test suite passes

## Verification Evidence

- **Test command:** `diff -q freebuff/AGENTS.global.md ~/.AGENTS.md && grep -c "Cognitive Executive" freebuff/AGENTS.global.md && uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q` (plus `lint_task_file` on this file via the lint MCP server)
- **Expected result:** `~/.AGENTS.md` identical to the source; full executor protocol sections present in the global file; global+project merge verified and documented; 52 passed; `lint_task_file` clean
- **Actual result (QA Iteration 4):** Manager directive applied — `freebuff-documents` removed from the `<agent_skills_registry>` in the system prompt (fragment + re-assembly): `grep -c freebuff-documents system-prompt.md` → **0**; `<system_version>` → **8.6.2**; assembler round-trip → byte-identical; pytest → **52 passed, exit 0**; project override still present (`grep -c freebuff-documents AGENTS.md` → 1). Prior-iteration evidence (kept): matrix row absent from `freebuff/AGENTS.global.md` (grep 0), install procedure in `docs/freebuff-documents.md` §3.1, global+project merge in §5, Global Rules Install & Sync in upgrade memory, DoD all `[x]`, `lint_task_file` passed.
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** (R1) expanding `freebuff/AGENTS.global.md` to full executor parity makes EVERY Freebuff session's system prompt heavier (token cost) — keep the port tight (rules, not prose). (R2) conflicting directives between the global role section and a project `AGENTS.md` could create contradictory instructions — the documented project-overrides-global rule mitigates this; verify it holds in both runtimes. (R3) the OpenCode agent's permission-layer mechanics (`mode`/`permission` frontmatter) have no Freebuff equivalent — the port must encode them as systemPrompt rules only (documented limitation).
- **Rollback plan:** restore the distilled role section from git history (`git checkout -- freebuff/AGENTS.global.md` after stashing) or the previously committed version, re-sync `~/.AGENTS.md` with `cp freebuff/AGENTS.global.md ~/.AGENTS.md`, and revert the docs section additions; `docs/freebuff-documents.md` stays as the last-known-good reference.

---

## Execution Log & Reasoning

_(Task 116 executed 2026-08-26 by the Hands. This task was generated by reading `skill-templates/task-generator/SKILL.md` manually, then executed in full.)_

### What was done

1. **Full Cognitive Executor rules port (AC1):** `freebuff/AGENTS.global.md` was expanded from the distilled role summary to FULL parity with OpenCode's `agents/cognitive-executor.md`, Freebuff-adapted. Added sections: **Core Protocol (Non-Negotiable)** (entry point, rule validation with `⚠️ RULE VIOLATION WARNING`, MCP-first context via `custom_context` tools, skill loading via `/skill:<name>`, ZAC, finalization & closure via `custom_context_stage_and_inject_diff` / `custom_context_commit_and_clean_task`), **Task Lifecycle & Kanban State Enforcement** (discovery/implementation/QA + metadata sync/closure — `git mv` rules), **Skill Auto-Loading Matrix** (full table + new `freebuff-documents` row), **Direct Input (Ad-Hoc) Validation Protocol** (5-step pipeline), **Context Bootstrapping & Memory Protocol** (`search_memory` first, strict `store_memory` criteria), **Subagent Delegation** (`cognitive-discovery` via `spawn_agents` on paid tier with a free-tier `custom_context` fallback), **Communication Patterns** (D/F/R/Q/A reference points, positive/negative patterns), **Execution Discipline** (Plan-Execute-Observe, circuit breakers, drift prevention), **Hard Operational Boundaries**, plus a **Freebuff permission note** (no platform-level git deny exists — ZAC is rule-enforced only). The `skill` tool references were adapted to `/skill:<name>` (the `skill` tool is not in the Freebuff whitelist).
2. **Install procedure (AC2):** `docs/freebuff-documents.md` gained §3.1 "Installing / Reinstalling the Global Rules File" — prerequisite/version check, exact `cp freebuff/AGENTS.global.md ~/.AGENTS.md` + `diff -q` verify, reinstall triggers, rollback. Also codified in the upgrade-workflow memory.
3. **Global + project AGENTS merge (AC3):** `docs/freebuff-documents.md` gained §5 "Global + Project AGENTS Merge (both must load)" — both `~/.AGENTS.md` and the project `AGENTS.md` are loaded in EVERY session (Freebuff: separate labeled system-prompt blocks, project wins on conflicts — verified against the source loader `sdk/src/run-state.ts`; OpenCode: global `instructions` + project `AGENTS.md`), with per-runtime verification steps and the design rule (baseline in global, specifics in project, project may tighten never weaken).
4. **Latest version + install procedures:** verified `0.0.156` is the current Freebuff CLI (public source snapshot synced 2026-08-26; GitHub Releases carries only unrelated "Codecane" staging builds — no versioned release channel). `docs/freebuff-support.md` §1 gained a "Keeping current" note + Update path row; `LLM.txt` Step 7.5 gained the CLI-binary/version note and a verification-checklist item.
5. **Upgrade memory:** `.opencode/memory/workflows/global-install-upgrade.md` gained a dedicated **"Global Rules Install & Sync (freebuff/AGENTS.global.md → ~/.AGENTS.md)"** section (exact commands, reinstall triggers, rollback, latest-version check) so the workflow always knows how to install the global rules file; step 2 gained the `cp` + version-check lines; the Install Locations table row now references the procedure.
6. **Sync + verify:** `~/.AGENTS.md` re-synced byte-identical from the source (`diff -q` clean, role heading present). prettier formatted the changed docs. `CHANGELOG.md` updated under `[Unreleased]`. pytest: **52 passed, exit 0**.

### Architectural reasoning

- The role section now mirrors `agents/cognitive-executor.md` 1:1 in rules, with only runtime-specific adaptations (slash-command skill loading, spawn fallback, permission-layer note) — this gives the free-tier base chat the same executor discipline as the paid-tier custom agent, on top of the same MCP tooling.
- Both AGENTS layers loading (not either/or) is the source-verified Freebuff behavior: `loadUserKnowledgeFiles` (home) and `selectKnowledgeFilePaths` (project) both inject into the system prompt; documenting this prevents future edits from wrongly "moving" rules between layers.
- The version channel is unversioned (binary download from freebuff.com) — so "latest" is tracked by the source-snapshot date + `--version`, now codified in docs and memory.

### QA Iteration 2 Fixes (2026-08-27)

- **F1 fixed:** Skills count corrected from (30) to (31) in the memory-file Install Locations table (`.opencode/memory/workflows/global-install-upgrade.md`).
- **F3 verified-no-op (NOT a fix):** The five space-insertion typos named by QA-F3 (`An droid`, `engineer ing`, `langu age`, `w ork`, `it eration`) DO NOT exist in `freebuff/AGENTS.global.md` — the correct spellings (`Android`, `engineering`, `language`, `work`, `iteration`) were already present (verified via `grep -c`, all 0). No typo change was made because there was nothing to fix. This is recorded honestly rather than claiming a no-op fix.
- **Manager directive applied:** Removed the `| Freebuff documents / roles editing | freebuff-documents |` row from the global Skill Auto-Loading Matrix in `freebuff/AGENTS.global.md` (line 127). Rationale: `freebuff-documents` is project-specific to this HQ repo and does NOT belong in the global rules file that applies to every project. **Step 4 check:** `agents/cognitive-executor.md` has NO `freebuff-documents` row — "not present, no action needed".
- **Project-level override added:** Appended `## Project-Specific Skill Auto-Load (this repo only)` to the root `AGENTS.md` so `freebuff-documents` is still auto-loaded in this repo via `/skill:freebuff-documents` — intentionally NOT in the global matrix.
- **F4 fixed:** DoD checkboxes in the task file updated to match verification evidence (Build/Test/Lint, lint_task_file, verification-before-completion now `[x]`; CHANGELOG already `[x]`).
- **F2 addressed:** All three untracked new files (`docs/freebuff-documents.md`, `skill-templates/freebuff-documents/SKILL.md`, `.opencode/skills/freebuff-documents/`) are included in the `modified_files` array when staging via `custom_context_stage_and_inject_diff` in the summary phase.
- **Sync + verify:** `~/.AGENTS.md` re-synced from the edited `freebuff/AGENTS.global.md` (`diff -q` clean). pytest suite re-run — all passed, exit 0. `lint_task_file` re-run on the QA task file — passed.

### QA Iteration 4 Fixes (2026-08-27)

- **Manager directive applied:** Removed the `freebuff-documents` bullet from the `<agent_skills_registry>` inside the system prompt — edited the source fragment `prompts/fragments/10-agent_skills_registry.md` (removed lines 10), bumped `<system_version>` **8.6.1 → 8.6.2** (`prompts/fragments/01-system_version.md`, mandatory per repo AGENTS.md), and re-assembled `system-prompt.md` via `scripts/prompt-build/assemble_system_prompt.py`. Verified: `grep -c freebuff-documents system-prompt.md` → **0**; assembler round-trip to `/tmp/sp-verify.md` → byte-identical; pytest **52 passed**, exit 0.
- **Scope note:** the system prompt has NO separate skill "matrix" — only the registry (fragment 10). The Skill Auto-Loading Matrix lives outside system-prompt.md (`agents/cognitive-executor.md` — never had a row; `freebuff/AGENTS.global.md` — row already removed in QA Iteration 2).
- **Kept project-scoped:** the root `AGENTS.md` "Project-Specific Skill Auto-Load (this repo only)" section (Iteration 2) is unchanged, so `freebuff-documents` still auto-loads in THIS repo via `/skill:freebuff-documents`; it is simply no longer advertised to every Orchestrator session via the registry.

### QA Iteration 3 Fixes (2026-08-27)

- **F3 verified-no-op:** The five space-insertion typos named by QA-F3 (`An droid`, `engineer ing`, `langu age`, `w ork`, `it eration`) DO NOT exist in `freebuff/AGENTS.global.md` — correct spellings already present (all grep counts = 0). No typo change made; this is a no-op, not a fake fix.
- **Manager directive verified-no-op:** The `freebuff-documents` row was already removed from the global Skill Auto-Loading Matrix in QA Iteration 2. Confirmed still absent (grep count = 0). The project-level override in root `AGENTS.md` was already present from QA Iteration 2 (grep count = 1).
- **F2 fixed:** Updated `README.md` — added `freebuff-documents` row to the General & Workflow Skills table, updated the Expanded Agent Skills Registry count from 28 to 31, added `freebuff-documents` to the skills list.
- **F4 verified-no-op:** All DoD checkboxes were already `[x]` from QA Iteration 2.

### Local TODO checks

- All 7 Local TODOs and all 4 Acceptance Criteria are checked off — each verified before checking (diff-clean sync, section presence via grep, tests 52/52, `lint_task_file` below).
- Not executed (by design): nothing remains — this task is complete and ready for QA review.


## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `de224f1b3cb44b2f3fc93b76c3b346bdfa379078`
<!-- END_GIT_DIFF -->
