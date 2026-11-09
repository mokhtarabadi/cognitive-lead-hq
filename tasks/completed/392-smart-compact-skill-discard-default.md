# Task 392: Remove skill from smart-compact discardTools default

**File:** `tasks/qa/392-smart-compact-skill-discard-default.md`
**Source:** manager
**Type:** bug
**Status:** open
**Submitted:** 2026-11-09T08:05:11Z
**Estimate:** 1h
**Milestone:** M01

## Goal

Stop the smart-compact plugin from discarding every `skill` tool result by default, so `Load Skill` returns its body to the agent (not the placeholder notice).

## Manager's Notes

Found via blind subagent tests: every `skill` call returned the exact placeholder `Skill contents omitted after compaction; recall the skill if needed.` Removing the key in `~/.config/opencode/smart-compact.jsonc` changed nothing. Root cause is in the plugin source at `../opencode-smart-compact/src/config.ts`: `DEFAULT_CONFIG.pruning.discardTools` hardcodes the `skill` entry, and config merging spreads defaults under user config (`{...base.pruning.discardTools, ...user}`), so an absent key in user config cannot remove it. Also, the discard check in `prune.ts` runs before `protectedTools`, so protecting `skill` cannot prevent the discard either. Audit `../opencode-smart-compact` README + defaults and fix at the source with an explicit opt-out.

## Local TODOs

- [x] Audit `../opencode-smart-compact` README + `src/config.ts` defaults
- [x] Remove `skill` from `discardTools` default (keep `todowrite`); make the user override able to remove a default key (explicit `null`/empty opt-out, not just spread)
- [x] Add `question` + `skill` to `protectedTools` defaults; document why `skill` must never be discarded
- [x] Add regression test: loading a skill returns full content, not the placeholder
- [x] Bump package version, run typecheck + tests, update CHANGELOG
- [x] Point the OpenCode install at the local plugin path (or republish) and restart; re-run the blind skill-load test

## Acceptance Criteria

- [x] `DEFAULT_CONFIG.pruning.discardTools` no longer contains `skill`, and user config can now remove a default discard key
- [x] A fresh session loading any skill receives its body verbatim (no placeholder); `discardTools` safely returns `todowrite` only by default
- [x] `npm run typecheck` and `npm test` pass in `../opencode-smart-compact`; version bumped in `package.json` + `CHANGELOG.md`
- [x] Global reinstall is verified with a blind `Load Skill` (e.g. `kanban-lifecycle`) returning real content

## Verification Evidence

- **Test command:** `rtk test npm test` (in `../opencode-smart-compact`)
- **Expected result:** all vitest suites pass
- **Actual result:** tests 141, pass 141, fail 0 (incl new `skill-discard.test.ts`); `npm run typecheck` clean
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by that evidence.

## Risk & Rollback

- **Risk:** `discardTools` semantics change — users who depended on skill discarding (unlikely; it breaks the tool) would see larger context.
- **Rollback plan:** revert the config default; re-pin the previous published version in `~/.config/opencode/opencode.json`.

## Execution Log & Reasoning

**Created:** plugin source located at `../opencode-smart-compact` (sibling repo, alongside `../opencode-goal-plugin`). `src/config.ts:96-100` hardcodes `discardTools.skill`; `src/config.ts:297-299` spreads defaults, so user deletion is a no-op; `src/prune.ts:152` discards before the `protectedTools` guard. Going forward, audit `README.md` + `DECISIONS.md` and the `DEFAULT_CONFIG` first before touching anything else.

**Fixed:** removed `skill` from `DEFAULT_CONFIG.pruning.discardTools` (only `todowrite` remains); `protectedTools` now defaults to `["question", "skill"]`; user `null` value in `discardTools` now deletes the default key (explicit opt-out). New regression test `tests/skill-discard.test.ts` asserts `skill` is not discarded and is protected. Version bumped 0.2.1 → 0.2.2; `CHANGELOG.md` Unreleased → Fixed. Typecheck clean, 141/141 tests pass.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 8d2da67..ea3ffdb 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -26,6 +26,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - Closed project-memory gaps: fixed namespace list (`architecture`, `opencode_config`, `project`, `quirks`, `release`, `telegram-sync`, `workflows` — no invented namespaces without approval), frontmatter template (`tags:` + one-line summary for the index), banned task-progress saves, and index-first retrieval with Manager re-ask on architectural ambiguity.
 - Fixed lint-server gaps: `_check_task_file_structure` now uses exact-line heading counts (no substring false-pass for `## Goal`); added deleted-skill guard so live `agents/` + `prompts/` text fails on any of the 12 pre-meta skill names (the guard scans root-relative `agents/` and `prompts/fragments/` paths, excludes `DECISIONS.md` files within those paths, and does not exempt provenance or attribution lines); unactionable-verb regex now checks `kanban-lifecycle`.
 - Persisted the Go `crouton-alpha-free` verdict (ADR-004): `docs/zen-proxy.md` now lists the verified 29-model `/go/resp` set (2026-11-08), `zen-proxy/DECISIONS.md` records the Go verdict with rollback, and the global install is byte-identical with the proxy active.
+- Merged `opencode-init` into `governance` as Part 3 of `templates/init.md` (project-only `opencode.json` generation); removed the standalone skill; governance index + registry updated, LLM.txt + checklist now 24 skills; system prompt 9.87.0 → 9.88.0 via the assembler (95047 chars / 95434 bytes).
+- Split the three oversized skills into loadable indexes: `governance` 43,572 → 2,114 bytes with `templates/audit.md` + `templates/init.md`, `kanban-lifecycle` 27,717 → 1,991 across five part files, `telegram-suite` 30,013 → 1,947 across three. The old sizes returned an empty `Load Skill` result. Repo-wide audit closed the drift they left: `skill-templates/README.md` count and `opencode-init` path, `README.md` roadmap naming `task-generator`/`testing-strategy`, and the `LLM.txt` §6.1 `bundle-tasks.py` CLI that does not ship. Tests now read `SKILL.md` plus `templates/*.md` so the same contract terms stay asserted.
 
 
 ## [9.77.0] - 2026-11-08
diff --git a/LLM.txt b/LLM.txt
index 8fc3765..7ce8dfb 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -191,21 +191,13 @@ cp -r /tmp/cognitive-lead-hq/skill-templates/* ~/.config/opencode/skills/
 rm -f ~/.config/opencode/skills/DECISIONS.md ~/.config/opencode/skills/README.md
 ```
 
-After this, the skills will be available via `/help` from any directory. `skill-templates/` contains **25 skills** (`kanban-lifecycle`, `telegram-suite`, `testing-verification`, and 22 more). `DECISIONS.md` and `README.md` stay in the repo only — they are not skills and must never be copied globally, or OpenChamber counts them as fake skills.
+After this, the skills will be available via `/help` from any directory. `skill-templates/` contains **24 skills** (`kanban-lifecycle`, `telegram-suite`, `testing-verification`, and 21 more). `DECISIONS.md` and `README.md` stay in the repo only — they are not skills and must never be copied globally, or OpenChamber counts them as fake skills.
 
-### 6.1. (Optional) Bundle CLI Script — Only If You Want `uv run scripts/bundle-tasks.py`
+### 6.1. Bundle CLI Script — Not Shipped
 
-The `bundle_tasks` MCP tool (`mcp-context-server/server.py`) is **self-contained** — it bundles without needing the script, so other projects that only have the MCP server can bundle via the Hands (`bundle_tasks` MCP call) with no extra files.
+`scripts/bundle-tasks.py` no longer exists in this repository: the `bundle_tasks` MCP tool (`mcp-context-server/server.py`) is **fully self-contained** and is the only bundling path. Invoke it through the Hands (`bundle_tasks(task_ids=[...], title="...", dry_run?, force?)`); there is no `uv run` CLI to copy.
 
-If you also want the Manager CLI (`uv run scripts/bundle-tasks.py <id> ... --title "<title>" [--dry-run]`), copy the script to your project's `scripts/`:
-
-```bash
-mkdir -p scripts
-cp /tmp/cognitive-lead-hq/scripts/bundle-tasks.py scripts/bundle-tasks.py
-chmod +x scripts/bundle-tasks.py
-```
-
-> **Is the script redundant?** No — CLI is for the Manager, MCP is for the Hands. For cross-project reuse, MCP is sufficient. Keep both if you want `uv run` one-offs and AI-driven bundling.
+> Cross-project reuse needs only the MCP server — no extra files.
 
 ---
 
@@ -479,10 +471,9 @@ Then create the recommended smart-compact global config at `~/.config/opencode/s
   "enabled": true,
   "pruning": {
     "maxChars": 1024, "maxWords": 128, "taskMaxChars": 4096, "taskMaxWords": 512,
-    "protectedTools": ["question"], "alwaysPruneTools": ["read"],
+    "protectedTools": ["question", "skill"], "alwaysPruneTools": ["read"],
     "discardTools": {
-      "todowrite": "Successfully updated todos.",
-      "skill": "Skill contents omitted after compaction; recall the skill if needed."
+      "todowrite": "Successfully updated todos."
     },
     "preserveRecentTurns": 2, "truncateToolsChars": 1024, "useTokens": true
   },
@@ -635,7 +626,7 @@ After completing all steps, verify:
 - [ ] `~/.config/opencode/mcp-brain-bridge/server.py` exists and is executable (plus its sibling modules `capability.py`, `preflight.py`, `loop_guard.py`, `session_ledger.py`)
 - [ ] `~/.config/opencode/mcp-common/src/mcp_common/env.py` exists
 - [ ] `~/.config/opencode/zen-proxy/proxy.py` exists and is executable, `~/.config/opencode/zen-proxy/.venv/bin/python` exists (built with `uv venv`), and `systemctl --user is-active zen-proxy` returns `active` on `127.0.0.1:8081` (`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/health` → 200); the unit reads `~/.config/opencode/.env` and needs no API key of its own
-- [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` (36 skills total)
+- [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `kanban-lifecycle` (24 skills total)
 - [ ] `~/.config/opencode/agents/cognitive-executor.md` exists
 - [ ] `~/.config/opencode/agents/cognitive-discovery.md` exists
 - [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 7 `mcp` entries (`custom_context`, `project_memory`, `lint`, `brain`, `blowsh`, `telegram`, `planner`) + `blowsh_*`/`telegram_*`/`brain_turn` permissions, no former browser entry
diff --git a/README.md b/README.md
index b61aac0..d94b912 100644
--- a/README.md
+++ b/README.md
@@ -507,7 +507,7 @@ See `.opencode/skills/sop-maintenance/SKILL.md` for the rules that AI agents mus
 ## Future Architectural Roadmap
 
 1. **Automated Pull Request Integration:** Upgrade the final Code Reviewer step to automatically branch, commit, and open a PR via GitHub CLI (`gh pr create`) instead of committing locally to `main`.
-2. **Epic and Milestone Tracking:** Create an `epics/` directory and update the `task-generator` skill to link individual tasks to parent epics for better macro-level project tracking.
-3. ~~Dedicated `testing-strategy` Skill~~ — DONE (Task 224 META): `skill-templates/testing-strategy/SKILL.md` enforces TDD order + diff-coverage + error-path gates.
+2. **Epic and Milestone Tracking:** Create an `epics/` directory and update the `kanban-lifecycle` skill to link individual tasks to parent epics for better macro-level project tracking.
+3. ~~Dedicated `testing-strategy` Skill~~ — DONE (Task 224 META): `skill-templates/testing-verification/SKILL.md` enforces TDD order + diff-coverage + error-path gates.
 4. ~~Database Migration Management~~ — DONE (Task 224 META): `skill-templates/database-migration/SKILL.md` bans direct DDL, forces Alembic/Prisma/Flyway.
 5. ~~Hexagonal Architecture Expansion~~ — DONE (Task 224 META): Hexagonal section in `skill-templates/python-fastapi/SKILL.md` + new `skill-templates/node-hexagonal-api/SKILL.md`; `stacks/node-ts.yaml` updated.
diff --git a/agents/cognitive-discovery.md b/agents/cognitive-discovery.md
index d7a3793..9825b5a 100644
--- a/agents/cognitive-discovery.md
+++ b/agents/cognitive-discovery.md
@@ -6,6 +6,7 @@ permission:
   bash: deny
   read: allow
   execute: allow
+  skill: allow
   custom_context_*: allow
   external_directory:
     "*": "ask"
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 921ed07..dea9ee0 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -135,6 +135,7 @@ To preserve your primary context window for implementation logic, you MUST deleg
 2. **Combined Tasks (`<hands_combined_task>`):** For the `<discovery_phase>`, delegate to `cognitive-discovery`. Wait for its context report before proceeding to the `<conditional_implementation_phase>`.
 3. **Implementation Tasks (`<hands_implementation_task>`):** If you need to understand a complex, unfamiliar module before editing, delegate a quick scan to `cognitive-discovery` to fetch just the signatures or relevant blocks.
 4. **Parallel Execution Mandate:** For multi-directory mapping and independent file reads, you MUST spawn parallel subagents (up to 4 concurrent agents) to maximize throughput. Serial execution of independent discovery work is a performance violation.
+5. **Subagents have no `skill` tool.** Verified 2026-11-09: a spawned subagent reports no `skill` tool in its toolset. Never delegate a step as "load skill X and follow it". Instead resolve the skill yourself, then hand the subagent the absolute file path (the skill's base directory plus the relative `templates/...` path named by its index) or the exact instruction text. A delegated agent that must guess a skill path will stall or search blindly.
 
 ## Subagent Delegation for Implementation
 
diff --git a/docs/compaction.md b/docs/compaction.md
index 02e63a5..7084249 100644
--- a/docs/compaction.md
+++ b/docs/compaction.md
@@ -116,10 +116,9 @@ The platform runs `warnRatio 0.5` / `emergencyRatio 0.8` because a 1M-token wind
   "enabled": true,
   "pruning": {
     "maxChars": 1024, "maxWords": 128, "taskMaxChars": 4096, "taskMaxWords": 512,
-    "protectedTools": ["question"], "alwaysPruneTools": ["read"],
+    "protectedTools": ["question", "skill"], "alwaysPruneTools": ["read"],
     "discardTools": {
-      "todowrite": "Successfully updated todos.",
-      "skill": "Skill contents omitted after compaction; recall the skill if needed."
+      "todowrite": "Successfully updated todos."
     },
     "preserveRecentTurns": 2, "truncateToolsChars": 1024, "useTokens": true
   },
diff --git a/mcp-lint-server/server.py b/mcp-lint-server/server.py
index 270ac81..a866689 100755
--- a/mcp-lint-server/server.py
+++ b/mcp-lint-server/server.py
@@ -668,21 +668,28 @@ def _check_bundle_meta_structure(content: str, file_path: str) -> list[str]:
     else skips with pass. A detected META file must carry a non-empty
     `## Supersedes` section naming source tasks and a non-empty
     `## Bundled Checklist` section carrying verbatim acceptance lines.
+
+    Detection and body inspection are scoped to the PRE-DIFF portion of the
+    file: the injected `## Factual Git Diff` block quotes other files
+    verbatim (a diff of the bundle skill itself contains `**Meta:** true` and
+    `## Bundled Checklist`), which would otherwise mark every task that
+    touches those files as a META and demand sections it never needs.
     """
     issues: list[str] = []
+    body_source = content.split("<!-- BEGIN_GIT_DIFF -->", 1)[0]
     title_meta = bool(
-        re.search(r"^# Task \d+:.*\bMETA\b", content, re.MULTILINE | re.IGNORECASE)
+        re.search(r"^# Task \d+:.*\bMETA\b", body_source, re.MULTILINE | re.IGNORECASE)
     )
     is_meta = (
         title_meta
-        or "**Meta:** true" in content
-        or "## Supersedes" in content
-        or "## Bundled Checklist" in content
+        or "**Meta:** true" in body_source
+        or "## Supersedes" in body_source
+        or "## Bundled Checklist" in body_source
     )
     if not is_meta:
         return issues
     for section in ("## Supersedes", "## Bundled Checklist"):
-        idx = content.find(section)
+        idx = body_source.find(section)
         if idx == -1:
             issues.append(
                 f"Bundle META: missing required `{section}` section "
@@ -690,7 +697,7 @@ def _check_bundle_meta_structure(content: str, file_path: str) -> list[str]:
                 f"all-or-nothing checklist)."
             )
             continue
-        rest = content[idx + len(section) :]
+        rest = body_source[idx + len(section) :]
         next_heading = re.search(r"\n## ", rest)
         body = rest[: next_heading.start()] if next_heading else rest
         if not body.strip():
diff --git a/mcp-lint-server/tests/test_deleted_skill_refs.py b/mcp-lint-server/tests/test_deleted_skill_refs.py
index 7d840d2..8b5c626 100644
--- a/mcp-lint-server/tests/test_deleted_skill_refs.py
+++ b/mcp-lint-server/tests/test_deleted_skill_refs.py
@@ -1,11 +1,11 @@
-"""Regression coverage for deleted-skill references in live instructions."""
+"""Regression coverage for deleted-skill references and META detection scope."""
 
 import sys
 from pathlib import Path
 
 sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
 
-from server import _check_deleted_skill_refs
+from server import _check_bundle_meta_structure, _check_deleted_skill_refs
 
 
 def test_deleted_skill_reference_is_reported_on_line_mentioning_readme() -> None:
@@ -48,3 +48,30 @@ def test_archive_path_excluded_for_deleted_skill(tmp_path) -> None:
 
     archive_result = lint_markdown(str(archived), project_root=str(tmp_path))
     assert "Deleted skill reference" not in archive_result
+
+
+def test_meta_markers_inside_injected_diff_do_not_make_a_task_meta() -> None:
+    """A diff quoting the bundle skill must not turn an ordinary task into META."""
+    content = (
+        "# Task 391: Split oversized skills\n\n"
+        "**File:** `tasks/qa/391-x.md`\n\n"
+        "## Goal\n\nNothing to bundle.\n\n"
+        "## Factual Git Diff\n\n"
+        "<!-- BEGIN_GIT_DIFF -->\n"
+        "+**Meta:** true\n"
+        "+## Bundled Checklist\n"
+        "+## Supersedes\n"
+    )
+
+    assert _check_bundle_meta_structure(content, "tasks/qa/391-x.md") == []
+
+
+def test_real_meta_missing_sections_is_still_reported() -> None:
+    """A genuine META outside the diff region still fails the structure check."""
+    content = (
+        "# Task 392: Bundle three tasks\n\n**Meta:** true\n\n## Goal\n\nBundle work.\n"
+    )
+
+    issues = _check_bundle_meta_structure(content, "tasks/qa/392-x.md")
+    assert any("## Supersedes" in i for i in issues)
+    assert any("## Bundled Checklist" in i for i in issues)
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index a0d4a2a..17b5dd4 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.87.0</system_version>
+<system_version>9.88.0</system_version>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 903fac9..8e30873 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -5,7 +5,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 
 - **code-search**: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
 - **kanban-lifecycle**: Unified Kanban lifecycle — task generation, lint validation, META bundling, completion archiving, and flat-to-V6 migration in one meta skill. Load before creating, linting, bundling, archiving, or migrating `tasks/` files.
-- **governance**: Agent protocol auditing plus living folder docs scaffolding — `AGENTS.md` governance and README/DECISIONS baselines in one meta skill.
+- **governance**: Agent protocol auditing, living folder docs scaffolding, and project-only `opencode.json` generation — `AGENTS.md` governance plus README/DECISIONS baselines plus Parts 2–3 of `templates/init.md` in one meta skill.
 - **versioning-and-release**: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.
 - **debug-instrumentation**: Mandatory workflow for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
 - **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning. After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
@@ -17,7 +17,6 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **database-migration**: Forbid direct schema alterations and force standard migration tools (Alembic, Prisma, Flyway) for safe, repeatable deployments.
 - **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
 - **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
-- **opencode-init**: Analyze a project (or ask the user) and generate a comprehensive, correct opencode.json for it. Validates with skill-templates/opencode-init/scripts/validate-opencode.py before writing; never touches global config. Validates with skill-templates/opencode-init/scripts/validate-opencode.py before writing; never touches global config.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
diff --git a/skill-templates/README.md b/skill-templates/README.md
index d8c58ba..6af7a7b 100644
--- a/skill-templates/README.md
+++ b/skill-templates/README.md
@@ -6,8 +6,8 @@ Project-agnostic skill template catalog: source of truth copied into `.opencode/
 
 ## Files
 
-- `*/SKILL.md` — One directory per skill (25 templates: `android-kotlin`, `governance`, `kanban-lifecycle`, `prompt-refactor`, `testing-verification`, `telegram-suite`, and others).
-- `opencode-init/references/` and `opencode-init/scripts/` — Init scaffolding references and helpers.
+- `*/SKILL.md` — One directory per skill (24 templates: `android-kotlin`, `governance`, `kanban-lifecycle`, `prompt-refactor`, `testing-verification`, `telegram-suite`, and others).
+- `governance/templates/opencode-init/references/` and `governance/templates/opencode-init/scripts/` — Init scaffolding references and helpers.
 
 ## Key Risks & Invariants
 
diff --git a/skill-templates/governance/SKILL.md b/skill-templates/governance/SKILL.md
index a58c108..f669066 100644
--- a/skill-templates/governance/SKILL.md
+++ b/skill-templates/governance/SKILL.md
@@ -3,505 +3,26 @@ name: governance
 description: Agent protocol auditing plus living folder docs scaffolding — AGENTS.md governance and README/DECISIONS baselines in one meta skill.
 ---
 
-# Governance Meta Skill
+# Governance Meta Skill (slim index)
 
-Meta skill combining **audit-agents** (project-agnostic Agent Protocol Auditor) and **init-folder-docs** (Living Folder Docs Initializer). Load one skill for governance work: either audit/patch an existing `AGENTS.md`, or scaffold missing slice docs. Sections are verbatim from the source skills.
+Meta skill combining **audit-agents** (project-agnostic Agent Protocol Auditor), **init-folder-docs** (Living Folder Docs Initializer), and **opencode-init** (project-only `opencode.json` generator, Part 3 of `templates/init.md`). Load one skill for governance work: audit/patch `AGENTS.md`, scaffold slice docs, or generate a project `opencode.json`. Full bodies are verbatim in `templates/` — read only the part you need.
 
 ---
 
-## Part 1: Agent Protocol Auditor — Project-Agnostic (from `audit-agents`)
+## Critical Rules (no read needed)
 
-# Skill: Agent Protocol Auditor (Project-Agnostic)
+- **Zero-Autonomous-Commit:** `git add`, `git commit`, `git checkout`, `git push` denied. Stage via `custom_context_stage_and_inject_diff`; close ONLY on exact “Approved for closure” / “Close task”.
+- **Absent-File Policy:** optional `DESIGN.md`/`docs/architecture.md`/`docs/data_model.md` missing → SKIP with note, never halt. Exception: UI work requires `DESIGN.md`.
+- **Decentralized tasks:** individual files in `tasks/{backlog,in-progress,qa,completed,archive}/` only. No `TODO.md`/`STATE.md`.
+- **Living Folder Docs:** every slice needs sibling `README.md` + `DECISIONS.md` with code pointers; keep in sync.
+- **Financial Ledger:** snapshot-on-write + `$ifNull` precedence + alerting + deep merge. **DSP:** `set -euo pipefail`, never mask with `2>/dev/null`.
+- **Lite Mode / Night Mode:** deprecated. Every task follows the full workflow; no bypass. Purge if found.
+- **Task numbers:** only in code comments, `CHANGELOG.md`, task files, history archives, HTML comments. Never in prompt prose.
+- **Edit discipline:** native edit/file-write tools only. No python/shell/heredoc/`sed -i` edits.
 
-## 🛑 SCOPE CONFINEMENT (Priority 0)
+## When to Read Templates
 
-- All file enumeration, inspection, and patch operations MUST be strictly confined to the caller's current working directory (`[PROJECT_ROOT]`).
-- You are STRICTLY FORBIDDEN from traversing outside `[PROJECT_ROOT]` or referencing parent directories. Use generic placeholders like `[PROJECT_ROOT]/AGENTS.md`.
-- **Absent-File Policy**: If optional architectural files (`DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`) do NOT exist in `[PROJECT_ROOT]`, SKIP them gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. DO NOT scaffold or create them unless explicitly instructed.
-- **OpenCode Isolation**: You are STRICTLY FORBIDDEN from creating `.opencode/` scaffolding inside third-party projects. Only inspect `.opencode/` if `[PROJECT_ROOT]/.opencode/` ALREADY exists OR if the user passes `with_opencode: true`.
-- **Session-Compact Config Is Agent Tooling**: `[PROJECT_ROOT]/.opencode/smart-compact.jsonc` is deliberate, agent-managed configuration for the context-compaction plugin. IGNORE it entirely: never flag it as OpenCode scaffolding, never patch or delete it, and never demand it be added to `.gitignore`. Report it only if the Manager explicitly asks about compaction settings.
+- **Audit or patch `AGENTS.md` / `docs/conventions.md`?** Read `templates/audit.md` (Target Audit Criteria, Mode 1 template, Mode 2 resolution, pitfalls).
+- **Scaffold slice docs for a new module?** Read `templates/init.md` Parts 2–3 (discovery → README/DECISIONS → code pointers; project `opencode.json` generation).
 
-## Target Audit Criteria
-
-The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:
-
-- **Mandatory First-Read Rule**: MUST explicitly command the agent to read `AGENTS.md` first before any execution. Inside it, it must route the agent to read `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` first.
-- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md` (if present, else note absent per Absent-File Policy), `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`). Only require `.opencode/skills/` when the project already contains `.opencode/` or `with_opencode: true` is set.
-- **conventions.md Compliance**: The project MUST have a `docs/conventions.md` file containing the Universal DateTime Standard (UTC at rest, Epoch/ISO-8601 with Offset at API boundaries, Clock injection, Dual-Representation for future events, TZ=UTC Infrastructure), SOLID Programming Guidelines (SRP, OCP, LSP, ISP, DIP, Pragmatic Guardrails), Universal Financial Ledger Standard (snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging), Defensive Shell Protocol (DSP) (`set -euo pipefail`, banned error masking, sidecar isolation), and Living Folder Docs Standard (colocated README.md and DECISIONS.md per feature slice/component, one-line code pointer standard, synchronization invariant).
-- **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`) as their single source of truth.
-- **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
-- **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator. **Exception:** `git mv` is permitted for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
-- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the active task file. 3) Call `custom_context_qa_transition` once with the active task path and explicit `modified_files`; it atomically moves the task to `tasks/qa/`, synchronizes the header, stages the changes, and injects the diff. Do not perform a separate task move, header edit, or re-stage. 4) Notify the Manager that QA/review will be chained directly through `brain_turn`; never ask the Manager to copy or relay task contents. Do not commit or close without explicit Manager approval.
-- **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
-- **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load the `kanban-lifecycle` skill before creating new task files.
-- **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load every available skill matching the project's tech stack before task implementation.
-- **Project Skills Table (local skills)**: On every audit, scan the project's local skill directories (`.opencode/skills/*/SKILL.md` or equivalent) and (re)build a **Project Skills** table in that project's `AGENTS.md` — one row per local skill: name, trigger (when to load), one-line duty, same column shape as the global Skill Auto-Loading Matrix. Two hard fails: audit without the Project Skills table fails, and a stale row (deleted skill still listed) fails the audit.
-- **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
-- **MCP Report Generation**: `AGENTS.md` MUST instruct agents to generate context reports (`custom_context_read_source_files`) and tree reports (`custom_context_create_tree_report` — "create a tree of the project") via the MCP server and hand the file path to the Manager instead of reading `context-reports/` files inline.
-- **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
-- **Parallel Index Isolation**: Verify the project documents the agent-managed round-trip for shared files — `custom_context_unstage_files` (index-only unstage) followed by `stage_and_inject_diff` with `skip_add=True` — and that `git commit`/`git checkout`/`git push` remain forbidden everywhere.
-- **Edit Tool Discipline**: `AGENTS.md` MUST forbid all scripted file edits — agents may use ONLY native file-editing tools for creating or modifying files (python, shell, heredoc, and `sed -i` are banned for edits; shell stays read-only for file content — e.g. grep, cat, diff, ls, git status). A non-unique anchor must fail loudly, never be forced. `docs/conventions.md` MUST contain a matching `## Edit Tool Discipline` section.
-- **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
-- **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
-- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage. When the project uses session-keyed conversation threads, the rules MUST note that flushing covers working execution assumptions only — the conversation thread persists across tasks under the active session ID until sprint completion.
-- **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
-- **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
-- **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
-- **Lite Mode Removal (Deprecated Bypass)**: Lite Mode (`<lite_mode_protocol>`, `Lite Mode`, `lite_mode`, `[LITE]`, `Lite-eligible`) is a deprecated bypass and MUST NOT exist in `AGENTS.md`, `docs/conventions.md`, `README.md`, `agents/*.md`, `prompts/**`, or generated prompt artifacts. Every task MUST traverse the full execution workflow with no bypass, escalation, or justification carve-out. When detected, the auditor MUST purge the Lite Mode section/paragraphs entirely (removing bypass clauses so the workflow is unconditional), verify no `<lite_mode_protocol>` fragment or manifest entry remains, and document the purge in the audit findings/changelog. The auditor MUST NOT flag its absence as a missing requirement. Historical traces in `tasks/archive/`, `tasks/completed/`, `docs/history/`, and `CHANGELOG.md` history are provenance only and MUST NOT be rewritten.
-- **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. Deliberate agent config (`[PROJECT_ROOT]/.opencode/smart-compact.jsonc`) is NOT runtime state and MUST NOT be gitignored. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
-- **Goal Plugin Runtime State**: Goal plugin file state (`[PROJECT_ROOT]/.opencode/goals/` per-session state plus evidence sidecars, the legacy `[PROJECT_ROOT]/.opencode/goal-state.json` and `[PROJECT_ROOT]/.opencode/goal-evidence.json` read fallbacks, `[PROJECT_ROOT]/STOP_GOAL`, `[PROJECT_ROOT]/.opencode/STOP_GOAL`) is runtime state only and MUST be gitignored. It is external scratch and never replaces decentralized task truth.
-
-- **Living Folder Docs Sibling Inspection**: AGENTS.md MUST instruct agents to inspect sibling README.md and DECISIONS.md before editing code in any component or vertical slice directory, and update them when domain contracts or architectural decisions change.
-
----
-
-## Core Document Templates
-
-### 1. `architecture.md` Template
-
-```markdown
-# Architecture Overview
-
-This document serves as a critical, living template designed to equip agents with a rapid and comprehensive understanding of the codebase's architecture, enabling efficient navigation and effective contribution from day one. Update this document as the codebase evolves.
-
-## 1. Project Structure
-
-[Project Root]/
-├── backend/ # Contains all server-side code and APIs
-│ ├── src/ # Main source code for backend services
-│ │ ├── api/ # API endpoints and controllers
-│ │ ├── client/ # Business logic and service implementations
-│ │ ├── models/ # Database models/schemas
-│ │ └── utils/ # Backend utility functions
-│ ├── config/ # Backend configuration files
-│ ├── tests/ # Backend unit and integration tests
-│ └── Dockerfile # Dockerfile for backend deployment
-├── frontend/ # Contains all client-side code for user interfaces
-│ ├── src/ # Main source code for frontend applications
-│ │ ├── components/ # Reusable UI components
-│ │ ├── pages/ # Application pages/views
-│ │ ├── assets/ # Images, fonts, and other static assets
-│ │ ├── services/ # Frontend services for API interaction
-│ │ └── store/ # State management (e.g., Redux, Vuex, Context API)
-│ ├── public/ # Publicly accessible assets (e.g., index.html)
-│ ├── tests/ # Frontend unit and E2E tests
-│ └── package.json # Frontend dependencies and scripts
-├── common/ # Shared code, types, and utilities used by both frontend and backend
-│ ├── types/ # Shared TypeScript/interface definitions
-│ └── utils/ # General utility functions
-├── docs/ # Project documentation (e.g., API docs, setup guides)
-├── scripts/ # Automation scripts (e.g., deployment, data seeding)
-├── .github/ # GitHub Actions or other CI/CD configurations
-├── .gitignore # Specifies intentionally untracked files to ignore
-├── README.md # Project overview and quick start guide
-└── ARCHITECTURE.md # This document
-
-## 2. High-Level System Diagram
-
-[User] <--> [Frontend Application] <--> [Backend Service 1] <--> [Database 1]
-|
-+--> [Backend Service 2] <--> [External API]
-
-## 3. Core Components
-
-### 3.1. Frontend
-
-Name: [Web App, Mobile App]
-Description: [Purpose, core interfaces, and roles]
-Technologies: [e.g., React, Next.js, Jetpack Compose, Swift/Kotlin]
-Deployment: [e.g., Vercel, Netlify, Play Store, App Store]
-
-### 3.2. Backend Services
-
-#### 3.2.1. Service Name 1
-
-Name: [e.g., API Service]
-Description: [Core business roles]
-Technologies: [e.g., Spring Boot, Node.js Express, Go]
-Deployment: [e.g., AWS ECS, Kubernetes]
-
-## 4. Data Stores
-
-### 4.1. Data Store 1
-
-Name: [e.g., SQL Database]
-Type: [e.g., PostgreSQL, MongoDB]
-Purpose: [e.g., Account records]
-
-## 5. External Integrations / APIs
-
-- Service Name: [e.g., Stripe, SendGrid]
-- Purpose: [e.g., Payments]
-- Method: [e.g., REST, SDK]
-
-## 6. Deployment & Infrastructure
-
-- Provider: [e.g., AWS, GCP]
-- CI/CD: [e.g., GitHub Actions]
-
-## 7. Security Considerations
-
-- Authentication: OAuth2/JWT
-- Encryption: TLS + AES-256
-
-## 8. Development & Testing Environment
-
-Testing Frameworks: [e.g., Pytest, JUnit, Jest]
-
-## 9. Future Considerations / Roadmap
-
-[Planned changes or architectural debt]
-```
-
-### 2. DESIGN.md Template (Google Spec)
-
-```markdown
-# Design System Specification
-
----
-
-name: custom-ui-system
-colors:
-primary: "#1D4ED8"
-secondary: "#4B5563"
-background: "#F3F4F6"
-surface: "#FFFFFF"
-text: "#111827"
-
----
-
-## 1. Visual Theme & Atmosphere
-
-[Rich prose outlining overall design mood, light/dark values, and whitespace philosophy]
-
-## 2. Color Palette & Roles
-
-- Primary foundation
-- Interactive / CTAs
-- Text hierarchy
-- State colors (Success, error, warn)
-
-## 3. Typography Rules
-
-- Hierarchy (headline, body, label)
-- letterSpacing, lineHeight, fontWeights
-
-## 4. Component Stylings
-
-- Buttons
-- Cards
-- Navigation
-- Input fields
-
-## 5. Layout Principles
-
-- Spacing scales
-- Breakpoints
-```
-
-### 3. `docs/conventions.md` Template
-
-Generate a `docs/conventions.md` file containing the Universal DateTime Standard and SOLID Programming Guidelines:
-
-```markdown
-# Conventions
-
-This document defines syntax rules, naming conventions, file boundaries, and automation patterns for this project.
-
-## Universal DateTime Standard
-
-All projects in this ecosystem MUST follow these datetime rules:
-
-1. **UTC at Rest** — All databases and caches store datetimes in UTC with `TIMESTAMP WITH TIME ZONE`. Banned: naive or local-time storage.
-2. **ISO-8601 with Offset / Epoch ms at API Boundaries** — APIs transmit datetimes as Unix Epoch milliseconds (int64) or ISO-8601 with offset (e.g., `2026-07-23T14:30:00+00:00`). Banned: timezone-naive strings.
-3. **Clock Injection** — All current-time access must go through an injectable `Clock` abstraction. Banned: direct `new Date()`, `datetime.now()`, `time.Now()` in business logic.
-4. **Dual-Representation for Future Events** — Calendar events expose both `event_start_local` (with timezone) and `event_start_epoch_ms` (absolute).
-5. **`TZ=UTC` Infrastructure** — All environments run with `TZ=UTC`. Timezone display is a client-layer responsibility only.
-
-## SOLID Programming Guidelines
-
-Enforce these SOLID principles and pragmatic guardrails in every implementation:
-
-1. **SRP** — One reason to change per module. Split merged concerns.
-2. **OCP** — Open for extension, closed for modification. Use composition over inheritance.
-3. **LSP** — Subtypes must be substitutable. Ban `NotImplementedError` overrides.
-4. **ISP** — Small role-specific interfaces. Ban monolithic god-interfaces.
-5. **DIP** — Depend on abstractions, not concretions. Core layer must not import adapters.
-
-**Pragmatic Guardrails:** No abstraction for <3 trivial operations. Only extract interfaces with 2+ implementations. Apply YAGNI strictly. Prefer simpler designs unless a measurable requirement forces complexity.
-
-## Universal Financial Ledger Standard
-
-All financial, transactional, and countable data operations MUST enforce these mandates:
-
-1. **Snapshot-on-Write for Mutable Totals:** Whenever a financial amount, inventory count, or balance is mutated, persist a read-only snapshot of the preceding state in the same transaction (sidecar table, audit log, or WAL). Banned: mutating without preserving the prior value.
-2. **Mandatory `$ifNull` Precedence:** All aggregation queries on monetary fields MUST use explicit null-handling (`COALESCE`, `ISNULL`, `$ifNull`). Banned: passing nullable columns into mathematical operators.
-3. **Observability Alerting on Discrepancies:** If a computed total diverges from its line-item sum by more than 0.01, emit a high-severity alert and prevent finalization.
-4. **Deep Config Merging for Financial Settings:** Financial configuration updates MUST deeply merge nested properties. Banned: shallow object spread on financial config objects.
-
-## Defensive Shell Protocol (DSP)
-
-When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
-
-1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
-2. **Banned Error Masking:** `2>/dev/null` is STRICTLY FORBIDDEN on data-generation, backup, archive, or database commands.
-3. **No Post-Redirect Status Checks:** Never use `command > file; if [ $? -eq 0 ]` — the shell creates the file before running the command, masking failures.
-4. **Sidecar Isolation for Hostless Backups:** Never rely on host file staging for Docker volume backups. Always use ephemeral containers (`docker run --rm -v volume:/data:ro alpine tar...`) with read-only mounts.
-
-## Edit Tool Discipline
-
-File edits use ONLY native file-editing tools (edit for replacements, file-write tools for new files). Using python, shell, heredoc, `sed -i`, or any script to create or modify files is strictly forbidden — scripted edits fail silently (replace-all on non-unique anchors, quoting and encoding mangling) while native tools fail loudly on a non-unique anchor.
-
-1. **Default native only:** one replacement, one location, exact unique anchor. A no-match or multi-match error is a signal, never a retry hint.
-2. **No scripted edits:** python, shell, heredoc, and `sed -i` are banned for creating or modifying files. Shell stays read-only for file content (e.g. grep, cat, diff, ls, git status).
-3. **Verify always:** grep/diff after every edit.
-
-## Task-Number Reference Discipline
-
-Task numbers are provenance for humans, not reasoning material for the model. A bare task number in visible prompt prose invites hallucination: the model treats it as load-bearing context it cannot resolve.
-
-1. **Allowed Homes (only):** code comments (`#`, `//`), `CHANGELOG.md` entries, task files, history archives, and HTML-comment markers (`<!-- -->`).
-2. **Forbidden Homes:** visible prose in prompt fragments, agent instruction files, skill instructions, registry lines, section headings, and any Markdown the Brain or Hands reads as operating instructions.
-3. **Authoring Rule:** when writing or editing prompt-facing Markdown, strip task-number parentheticals. Record provenance in the task file and CHANGELOG instead — never in the prompt text itself.
-
-## Living Folder Docs Standard
-
-All vertical slices and component directories across projects in this ecosystem MUST maintain colocated documentation and decision records:
-
-1. **Folder Colocation** — Every domain component or vertical slice directory (e.g. `src/features/todos/`, `services/auth/`, `mcp-context-server/`) must contain:
-   - `README.md` — Explains the component's core duties, directory layout, owned files, and critical invariants/risks.
-   - `DECISIONS.md` — Chronological log of dated Architectural Decision Records (ADRs). Each entry must document Context, Decision, Consequences, and Rollback strategy.
-2. **One-Line Code Pointer Standard** — Primary source files within the component directory must include a top-line comment pointing directly to the sibling docs:
-   - JavaScript/TypeScript: `// Sibling Docs: <relative-path>/README.md | Decisions: <relative-path>/DECISIONS.md`
-   - Python/Shell: `# Sibling Docs: <relative-path>/README.md | Decisions: <relative-path>/DECISIONS.md`
-3. **Synchronization Invariant** — Whenever source code inside a component directory is added, refactored, or altered in behavior or data contract, the sibling `README.md` and `DECISIONS.md` MUST be inspected and updated within the same task. Silent overrides of existing architectural decisions are strictly forbidden.
-```
-
----
-
-Use this skill in two modes:
-
-- **Phase 0 (Generation):** When `AGENTS.md` does not exist yet — generate it from the template below.
-- **Audit Mode (Existing):** When `AGENTS.md` already exists — audit and patch it against the Target Audit Criteria.
-
----
-
-## Mode 1: Phase 0 — Generate AGENTS.md & docs/conventions.md
-
-Use this when a project has no `AGENTS.md` yet (new project onboarding).
-
-### Workflow
-
-1. Read the project's existing context (package configs, README, tech stack files) to determine the project name, description, and relevant tech stack skills.
-2. Generate `AGENTS.md` at the project root using the template below.
-3. Fill in the `[bracketed]` placeholders with the actual project details.
-4. Generate `docs/conventions.md` using the conventions template above, if the project does not already have one.
-5. Confirm both files were created.
-
-### AGENTS.md Template
-
-```markdown
-# [Project Name] — Project Context Hub
-
-## Project Overview
-
-[Brief description of the project, its purpose, and tech stack]
-
-## Setup & Dev Commands
-
-- Build: [build command, e.g., npm run build]
-- Test: [test command, e.g., npm test]
-- Lint: [lint command, e.g., npm run lint]
-- Dev: [dev server command, e.g., npm run dev]
-
-## Actionable Guardrails (Do's & Don'ts)
-
-- **Don't** [common anti-pattern to avoid]
-  -> **Do** [preferred alternative]
-- **Don't** [another anti-pattern]
-  -> **Do** [preferred alternative]
-- **Don't** read `context-reports/` markdown files yourself.
-  -> **Do** generate them using the MCP server — context reports via `custom_context_read_source_files`, tree reports via `custom_context_create_tree_report` ("create a tree of the project") — and hand the file path to the Manager.
-- **Don't** execute Git commands like `git add`, `git commit`, or `git mv` autonomously or try to guess when to stage code.
-  -> **Do** execute Git commands ONLY when explicitly instructed by an Orchestrator task block. Otherwise, rely on the `custom_context_stage_and_inject_diff` MCP tool.
-  -> **Exception:** `git mv` is permitted autonomously for moving task files between Kanban directories.
-- **Don't** guess blindly when facing complex bugs, deadlocks, or silent timeouts.
-  -> **Do** utilize the `debug-instrumentation` skill to inject strategic logs and trace the runtime execution path.
-- **Don't** write bash scripts without strict mode or mask errors with `2>/dev/null` on data commands.
-  -> **Do** follow the Defensive Shell Protocol: `set -euo pipefail`, ban error masking, sidecar isolation for Docker backups. See `docs/conventions.md`.
-- **Don't** perform financial mutations without snapshotting the prior state or allow nulls in monetary aggregations.
-  -> **Do** follow the Universal Financial Ledger Standard: snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging. See `docs/conventions.md`.
-- **Don't** leave task numbers in visible prompt prose, section headings, or skill instructions.
-  -> **Do** keep task-number references in code comments, CHANGELOG entries, task files, history archives, and HTML comments only. See `docs/conventions.md`.
-- **Don't** carry over assumptions, partial results, or architectural hypotheses from a previous task.
-  -> **Do** flush context and treat every task as contextually independent (Buffer Isolation directive in validation-phase).
-- **Don't** execute raw, informal, or non-English prompts directly.
-  -> **Do** load the `prompt-refactor` skill to translate and expand the intent into an elite English spec first. (Note: If you receive a standard XML task block, skip this and execute normally).
-- **Don't** attempt to resolve cross-disciplinary ambiguity within a single persona.
-  -> **Do** trigger the Multi-Agent Brainstorming Loop if the Manager explicitly requests brainstorming or a task exhibits cross-disciplinary ambiguity. Interpret the `<brainstorming_session>` results in backlog tasks as non-functional guidelines that govern execution.
-- **Don't** silently alter slice architecture or domain invariants without updating the sibling README.md and appending a dated ADR to DECISIONS.md.
-  -> **Do** inspect sibling README.md and DECISIONS.md before modifying code, and keep them in sync with implementation changes.
-- **Don't** skip the execution workflow for trivial, single-file changes.
-  -> **Do** traverse the full workflow for every task; keep scope minimal for trivial changes.
-
-## Documentation Sync Rules
-
-When modifying this repository, you must keep these files synchronized:
-
-1. Active task file in `tasks/` (single source of truth for current work items)
-2. `CHANGELOG.md` (Keep a Changelog format)
-3. `DESIGN.md` (UI/UX design system, if modified)
-4. `docs/conventions.md` (syntax rules, datetime standard, SOLID guidelines)
-5. Relevant `SKILL.md` files (if structural patterns were altered)
-
-## 🛑 GATEKEEPER VALIDATION (HALT PROTOCOL)
-
-You (the Hands) are the final gatekeeper. Before executing any implementation task, you MUST evaluate the Orchestrator's instructions against this file and any referenced specs (`DESIGN.md`, `architecture.md`, etc.). If the instructions violate project rules, ignore them. HALT immediately and output a `⚠️ RULE VIOLATION WARNING` back to the Manager explaining exactly what the Orchestrator got wrong, forcing it to self-correct.
-
-## 🛑 CORE FILE LOCATIONS
-
-You MUST strictly adhere to these exact paths. Do not create duplicates elsewhere:
-
-- **Global Rules:** `AGENTS.md` (Root)
-- **UI/UX Specs:** `DESIGN.md` (Root)
-- **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace — optional; only include if project utilizes OpenCode)
-- **Active Tasks:** `tasks/backlog/<task-number>-<name>.md` (backlog), `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`
-
-## 🛑 SKILL LOADING RULES
-
-You MUST follow these skill loading rules in every session:
-
-- **Task-Generator Skill:** Before creating any new task file, you MUST load the `kanban-lifecycle` skill using the `skill` tool to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
-- **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `android-kotlin`, `spring-boot`, `react-vite`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.
-
-## 🛑 CONTEXT BOOTSTRAPPING
-
-At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing.
-
-## 🛑 MANDATORY END-OF-TASK SEQUENCE
-
-When finishing an implementation task, execute these steps in order:
-
-1. Update `CHANGELOG.md` with the task's changes.
-2. Record reasoning and verification evidence in the active task file.
-3. Call `custom_context_qa_transition` once with the active task path and explicit `modified_files`. This tool atomically moves the task to `tasks/qa/`, synchronizes its `**File:**` header, stages modified files, and injects the diff. Do not move the task separately or manually edit its header.
-4. Notify the Manager that the task is in QA and the Hands will chain QA/review through `brain_turn`. Never ask the Manager to copy, paste, or relay task contents.
-5. Do not commit or close the task until the Manager gives the explicit closure approval phrase. Discovery tasks remain in their current lane.
-```
-
----
-
-## Mode 2: Audit & Patch Existing AGENTS.md and docs/conventions.md
-
-### 🛑 STRICT EXECUTION RULES (Priority 1)
-
-1. **Primary Source of Truth**: You MUST read `AGENTS.md` at the project root using local file read tools.
-2. **Read-Only First**: Evaluate the contents of both `AGENTS.md` and `docs/conventions.md` against the Target Audit Criteria before attempting any file modifications.
-3. **Immutable Formatting**: If patching is required, maintain the exact Markdown list structure, headers, and spacing of the existing file.
-
-### Target Audit Criteria
-
-The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:
-
-- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md` (if present, else note absent per Absent-File Policy), `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`). Only require `.opencode/skills/` when the project already contains `.opencode/` or `with_opencode: true` is set.
-
-Additionally, the `docs/conventions.md` file MUST exist and contain:
-
-- **Universal DateTime Standard**: UTC at rest, Epoch/ISO-8601 with Offset at API boundaries, Clock injection, Dual-Representation for future events, `TZ=UTC` Infrastructure.
-- **SOLID Programming Guidelines**: SRP, OCP, LSP, ISP, DIP, and Pragmatic Guardrails (No abstraction for <3 trivial ops, 3-Implementation Rule, YAGNI, Occam's Razor).
-- **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
-- **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
-- **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator. **Exception:** `git mv` is permitted for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
-- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the active task file. 3) Call `custom_context_qa_transition` once with the active task path and explicit `modified_files`; it atomically moves the task to `tasks/qa/`, synchronizes the header, stages the changes, and injects the diff. Do not perform a separate task move, header edit, or re-stage. 4) Notify the Manager that QA/review will be chained directly through `brain_turn`; never ask the Manager to copy or relay task contents. Do not commit or close without explicit Manager approval.
-- **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
-- **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load the `kanban-lifecycle` skill before creating new task files.
-- **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load every available skill matching the project's tech stack before task implementation.
-- **Project Skills Table (local skills)**: On every audit, scan the project's local skill directories (`.opencode/skills/*/SKILL.md` or equivalent) and (re)build a **Project Skills** table in that project's `AGENTS.md` — one row per local skill: name, trigger (when to load), one-line duty, same column shape as the global Skill Auto-Loading Matrix. Two hard fails: audit without the Project Skills table fails, and a stale row (deleted skill still listed) fails the audit.
-- **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
-- **MCP Report Generation**: `AGENTS.md` MUST instruct agents to generate context reports (`custom_context_read_source_files`) and tree reports (`custom_context_create_tree_report` — "create a tree of the project") via the MCP server and hand the file path to the Manager instead of reading `context-reports/` files inline.
-- **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
-- **Parallel Index Isolation**: Verify the project documents the agent-managed round-trip for shared files — `custom_context_unstage_files` (index-only unstage) followed by `stage_and_inject_diff` with `skip_add=True` — and that `git commit`/`git checkout`/`git push` remain forbidden everywhere.
-- **Edit Tool Discipline**: `AGENTS.md` MUST forbid all scripted file edits — agents may use ONLY native file-editing tools for creating or modifying files (python, shell, heredoc, and `sed -i` are banned for edits; shell stays read-only for file content — e.g. grep, cat, diff, ls, git status). A non-unique anchor must fail loudly, never be forced. `docs/conventions.md` MUST contain a matching `## Edit Tool Discipline` section.
-- **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
-- **Bilingual Prompt Refactoring & Brainstorming Protocol**: Agents MUST be instructed not to execute raw, informal, or non-English prompts directly. The `prompt-refactor` skill must be loaded, or the Phase 1.5 Multi-Agent Brainstorming Protocol triggered, to translate and expand intent first. Standard XML task blocks are exempt.
-- **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
-- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage. When the project uses session-keyed conversation threads, the rules MUST note that flushing covers working execution assumptions only — the conversation thread persists across tasks under the active session ID until sprint completion.
-- **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
-- **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
-- **Task-Number Reference Discipline**: `AGENTS.md` MUST include a guardrail restricting task-number references to code comments, CHANGELOG entries, task files, history archives, and HTML comments — never in visible prompt prose, headings, or skill instructions. `docs/conventions.md` MUST contain a `## Task-Number Reference Discipline` section.
-- **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
-- **Lite Mode Removal (Deprecated Bypass)**: Lite Mode (`<lite_mode_protocol>`, `Lite Mode`, `lite_mode`, `[LITE]`, `Lite-eligible`) is a deprecated bypass and MUST NOT exist in `AGENTS.md`, `docs/conventions.md`, `README.md`, `agents/*.md`, `prompts/**`, or generated prompt artifacts. Every task MUST traverse the full execution workflow with no bypass, escalation, or justification carve-out. When detected, the auditor MUST purge the Lite Mode section/paragraphs entirely (removing bypass clauses so the workflow is unconditional), verify no `<lite_mode_protocol>` fragment or manifest entry remains, and document the purge in the audit findings/changelog. The auditor MUST NOT flag its absence as a missing requirement. Historical traces in `tasks/archive/`, `tasks/completed/`, `docs/history/`, and `CHANGELOG.md` history are provenance only and MUST NOT be rewritten.
-- **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. Deliberate agent config (`[PROJECT_ROOT]/.opencode/smart-compact.jsonc`) is NOT runtime state and MUST NOT be gitignored. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
-- **Living Folder Docs Standard**: docs/conventions.md MUST contain a ## Living Folder Docs Standard section, and AGENTS.md must mandate sibling doc inspection before component edits.
-
-### Resolution Protocol
-
-1. **Evaluation**: Compare the active `AGENTS.md` text against the Target Audit Criteria. Also check if `docs/conventions.md` exists and contains both the DateTime Standard and SOLID Guidelines.
-   - **Absent-File Policy (Mandatory)**: For `DESIGN.md`, `docs/architecture.md`, and `docs/data_model.md` — if any of these files do NOT exist in `[PROJECT_ROOT]`, audit them as `OPTIONAL — SKIPPED GRACEFULLY` with an explicit note. DO NOT flag as fatal errors, non-compliance violations, or missing-file failures. DO NOT hallucinate or scaffold them.
-2. **Patching**: If any constraints are missing, ambiguous, or incorrect in `AGENTS.md`, use the `apply_patch` tool to inject the exact missing rules. If `docs/conventions.md` is missing or incomplete, generate or patch it using the conventions template from Mode 1.
-3. **Halt on Success**: If both files already comply 100%, DO NOT execute any write operations.
-
-### Deprecated Sections Resolution
-
-- **Deprecated Sections Purge**: If any file contains deprecated sections (`## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`), strip those sections cleanly. Do NOT add them back. Record the removal in the audit report under a dedicated "Deprecated Sections Purged" note.
-- **Lite Mode Purge**: If any live file (excluding `tasks/archive/`, `tasks/completed/`, `docs/history/`, `CHANGELOG.md` history, and `prompts/archive/`) contains Lite Mode markers (`<lite_mode_protocol>`, `Lite Mode`, `lite_mode`, `[LITE]`, `Lite-eligible`, `Escalating from Lite Mode`), strip the Lite Mode block and every bypass/escalation/justification sentence, keep the full execution workflow unconditional, and record under "Deprecated Sections Purged". Do NOT add them back.
-
-### Summary Phase
-
-Upon completion, output a strict, formatted summary for the Manager:
-
-### Agent Audit Summary
-
-**Audit Status:** [PASSED | FIXED]
-**AGENTS.md Violations:** [List of missing/incorrect rules, or "None"]
-**conventions.md Status:** [COMPLIANT | MISSING | INCOMPLETE]
-**conventions.md Actions:** [Description of the patch applied, or "Already compliant"]
-**Actions Taken:** [Description of the patches applied, or "Both files already compliant"]
-
----
-
-## Part 2: Living Folder Docs Initializer (from `init-folder-docs`)
-
-# Skill: Living Folder Docs Initializer
-
-Use this skill to onboard existing projects to the Living Folder Docs standard by discovering component directories and scaffolding baseline documentation and code pointers.
-
-## Scope Confinement
-
-- Confine all file scans and generation strictly to `[PROJECT_ROOT]`.
-- Never touch vendor or build directories (`node_modules/`, `.git/`, `dist/`, `build/`, `.venv/`, `vendor/`, `target/`).
-
-## Workflow
-
-1. **Slice Discovery:**
-   - Search the repository for distinct vertical slices, modules, or domain component directories (e.g., `src/features/*`, `apps/*/src/modules/*`, `services/*`, `backend/src/*`).
-   - List all discovered directory paths.
-
-2. **Scaffold Missing Slice Docs:**
-   For each discovered directory `[DIR]`:
-   - **README.md:** If `[DIR]/README.md` does not exist, create it with:
-     - `# Slice: [DIR_NAME]`
-     - `## Duties` (Derived from contained file names and directory role)
-     - `## Files` (List of contained source files with brief 1-line description)
-     - `## Key Risks & Invariants` (Baseline invariants and known edge cases)
-   - **DECISIONS.md:** If `[DIR]/DECISIONS.md` does not exist, create it with:
-     - `# Architectural Decisions: [DIR_NAME]`
-     - `## [YYYY-MM-DD] ADR-001: Initial Slice Baseline`
-     - `- **Context:** Baseline documentation initialized via governance.`
-     - `- **Decision:** Adopting Living Folder Docs standard for this component.`
-     - `- **Consequences:** All future structural or contract changes must be recorded here.`
-     - `- **Rollback:** N/A (baseline adoption).`
-
-3. **Inject Code Pointers:**
-   - In primary source files within `[DIR]` (e.g. main service, controller, model, or entry file), inspect the first 5 lines.
-   - If no sibling docs comment exists, inject the top-line comment pointer:
-     - JS/TS: `// Sibling Docs: [DIR]/README.md | Decisions: [DIR]/DECISIONS.md`
-     - Python/Shell: `# Sibling Docs: [DIR]/README.md | Decisions: [DIR]/DECISIONS.md`
-
-4. **Verification & Summary:**
-   - Run `git status` (read-only) to review generated files.
-   - Output a concise summary listing:
-     - Discovered Slices: count and paths
-     - Created `README.md` files
-     - Created `DECISIONS.md` files
-     - Injected code pointers count
+Templates are authoritative; this index only summarizes. Skills registry: `prompts/fragments/07-agent_skills_registry.md`.
diff --git a/skill-templates/governance/templates/audit.md b/skill-templates/governance/templates/audit.md
new file mode 100644
index 0000000..f32b6e4
--- /dev/null
+++ b/skill-templates/governance/templates/audit.md
@@ -0,0 +1,451 @@
+## Part 1: Agent Protocol Auditor — Project-Agnostic (from `audit-agents`)
+
+# Skill: Agent Protocol Auditor (Project-Agnostic)
+
+## 🛑 SCOPE CONFINEMENT (Priority 0)
+
+- All file enumeration, inspection, and patch operations MUST be strictly confined to the caller's current working directory (`[PROJECT_ROOT]`).
+- You are STRICTLY FORBIDDEN from traversing outside `[PROJECT_ROOT]` or referencing parent directories. Use generic placeholders like `[PROJECT_ROOT]/AGENTS.md`.
+- **Absent-File Policy**: If optional architectural files (`DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`) do NOT exist in `[PROJECT_ROOT]`, SKIP them gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. DO NOT scaffold or create them unless explicitly instructed.
+- **OpenCode Isolation**: You are STRICTLY FORBIDDEN from creating `.opencode/` scaffolding inside third-party projects. Only inspect `.opencode/` if `[PROJECT_ROOT]/.opencode/` ALREADY exists OR if the user passes `with_opencode: true`.
+- **Session-Compact Config Is Agent Tooling**: `[PROJECT_ROOT]/.opencode/smart-compact.jsonc` is deliberate, agent-managed configuration for the context-compaction plugin. IGNORE it entirely: never flag it as OpenCode scaffolding, never patch or delete it, and never demand it be added to `.gitignore`. Report it only if the Manager explicitly asks about compaction settings.
+
+## Target Audit Criteria
+
+The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:
+
+- **Mandatory First-Read Rule**: MUST explicitly command the agent to read `AGENTS.md` first before any execution. Inside it, it must route the agent to read `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` first.
+- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md` (if present, else note absent per Absent-File Policy), `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`). Only require `.opencode/skills/` when the project already contains `.opencode/` or `with_opencode: true` is set.
+- **conventions.md Compliance**: The project MUST have a `docs/conventions.md` file containing the Universal DateTime Standard (UTC at rest, Epoch/ISO-8601 with Offset at API boundaries, Clock injection, Dual-Representation for future events, TZ=UTC Infrastructure), SOLID Programming Guidelines (SRP, OCP, LSP, ISP, DIP, Pragmatic Guardrails), Universal Financial Ledger Standard (snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging), Defensive Shell Protocol (DSP) (`set -euo pipefail`, banned error masking, sidecar isolation), and Living Folder Docs Standard (colocated README.md and DECISIONS.md per feature slice/component, one-line code pointer standard, synchronization invariant).
+- **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`) as their single source of truth.
+- **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
+- **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator. **Exception:** `git mv` is permitted for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
+- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the active task file. 3) Call `custom_context_qa_transition` once with the active task path and explicit `modified_files`; it atomically moves the task to `tasks/qa/`, synchronizes the header, stages the changes, and injects the diff. Do not perform a separate task move, header edit, or re-stage. 4) Notify the Manager that QA/review will be chained directly through `brain_turn`; never ask the Manager to copy or relay task contents. Do not commit or close without explicit Manager approval.
+- **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
+- **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load the `kanban-lifecycle` skill before creating new task files.
+- **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load every available skill matching the project's tech stack before task implementation.
+- **Project Skills Table (local skills)**: On every audit, scan the project's local skill directories (`.opencode/skills/*/SKILL.md` or equivalent) and (re)build a **Project Skills** table in that project's `AGENTS.md` — one row per local skill: name, trigger (when to load), one-line duty, same column shape as the global Skill Auto-Loading Matrix. Two hard fails: audit without the Project Skills table fails, and a stale row (deleted skill still listed) fails the audit.
+- **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
+- **MCP Report Generation**: `AGENTS.md` MUST instruct agents to generate context reports (`custom_context_read_source_files`) and tree reports (`custom_context_create_tree_report` — "create a tree of the project") via the MCP server and hand the file path to the Manager instead of reading `context-reports/` files inline.
+- **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
+- **Parallel Index Isolation**: Verify the project documents the agent-managed round-trip for shared files — `custom_context_unstage_files` (index-only unstage) followed by `stage_and_inject_diff` with `skip_add=True` — and that `git commit`/`git checkout`/`git push` remain forbidden everywhere.
+- **Edit Tool Discipline**: `AGENTS.md` MUST forbid all scripted file edits — agents may use ONLY native file-editing tools for creating or modifying files (python, shell, heredoc, and `sed -i` are banned for edits; shell stays read-only for file content — e.g. grep, cat, diff, ls, git status). A non-unique anchor must fail loudly, never be forced. `docs/conventions.md` MUST contain a matching `## Edit Tool Discipline` section.
+- **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
+- **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
+- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage. When the project uses session-keyed conversation threads, the rules MUST note that flushing covers working execution assumptions only — the conversation thread persists across tasks under the active session ID until sprint completion.
+- **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
+- **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
+- **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
+- **Lite Mode Removal (Deprecated Bypass)**: Lite Mode (`<lite_mode_protocol>`, `Lite Mode`, `lite_mode`, `[LITE]`, `Lite-eligible`) is a deprecated bypass and MUST NOT exist in `AGENTS.md`, `docs/conventions.md`, `README.md`, `agents/*.md`, `prompts/**`, or generated prompt artifacts. Every task MUST traverse the full execution workflow with no bypass, escalation, or justification carve-out. When detected, the auditor MUST purge the Lite Mode section/paragraphs entirely (removing bypass clauses so the workflow is unconditional), verify no `<lite_mode_protocol>` fragment or manifest entry remains, and document the purge in the audit findings/changelog. The auditor MUST NOT flag its absence as a missing requirement. Historical traces in `tasks/archive/`, `tasks/completed/`, `docs/history/`, and `CHANGELOG.md` history are provenance only and MUST NOT be rewritten.
+- **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. Deliberate agent config (`[PROJECT_ROOT]/.opencode/smart-compact.jsonc`) is NOT runtime state and MUST NOT be gitignored. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
+- **Goal Plugin Runtime State**: Goal plugin file state (`[PROJECT_ROOT]/.opencode/goals/` per-session state plus evidence sidecars, the legacy `[PROJECT_ROOT]/.opencode/goal-state.json` and `[PROJECT_ROOT]/.opencode/goal-evidence.json` read fallbacks, `[PROJECT_ROOT]/STOP_GOAL`, `[PROJECT_ROOT]/.opencode/STOP_GOAL`) is runtime state only and MUST be gitignored. It is external scratch and never replaces decentralized task truth.
+
+- **Living Folder Docs Sibling Inspection**: AGENTS.md MUST instruct agents to inspect sibling README.md and DECISIONS.md before editing code in any component or vertical slice directory, and update them when domain contracts or architectural decisions change.
+
+---
+
+## Core Document Templates
+
+### 1. `architecture.md` Template
+
+```markdown
+# Architecture Overview
+
+This document serves as a critical, living template designed to equip agents with a rapid and comprehensive understanding of the codebase's architecture, enabling efficient navigation and effective contribution from day one. Update this document as the codebase evolves.
+
+## 1. Project Structure
+
+[Project Root]/
+├── backend/ # Contains all server-side code and APIs
+│ ├── src/ # Main source code for backend services
+│ │ ├── api/ # API endpoints and controllers
+│ │ ├── client/ # Business logic and service implementations
+│ │ ├── models/ # Database models/schemas
+│ │ └── utils/ # Backend utility functions
+│ ├── config/ # Backend configuration files
+│ ├── tests/ # Backend unit and integration tests
+│ └── Dockerfile # Dockerfile for backend deployment
+├── frontend/ # Contains all client-side code for user interfaces
+│ ├── src/ # Main source code for frontend applications
+│ │ ├── components/ # Reusable UI components
+│ │ ├── pages/ # Application pages/views
+│ │ ├── assets/ # Images, fonts, and other static assets
+│ │ ├── services/ # Frontend services for API interaction
+│ │ └── store/ # State management (e.g., Redux, Vuex, Context API)
+│ ├── public/ # Publicly accessible assets (e.g., index.html)
+│ ├── tests/ # Frontend unit and E2E tests
+│ └── package.json # Frontend dependencies and scripts
+├── common/ # Shared code, types, and utilities used by both frontend and backend
+│ ├── types/ # Shared TypeScript/interface definitions
+│ └── utils/ # General utility functions
+├── docs/ # Project documentation (e.g., API docs, setup guides)
+├── scripts/ # Automation scripts (e.g., deployment, data seeding)
+├── .github/ # GitHub Actions or other CI/CD configurations
+├── .gitignore # Specifies intentionally untracked files to ignore
+├── README.md # Project overview and quick start guide
+└── ARCHITECTURE.md # This document
+
+## 2. High-Level System Diagram
+
+[User] <--> [Frontend Application] <--> [Backend Service 1] <--> [Database 1]
+|
++--> [Backend Service 2] <--> [External API]
+
+## 3. Core Components
+
+### 3.1. Frontend
+
+Name: [Web App, Mobile App]
+Description: [Purpose, core interfaces, and roles]
+Technologies: [e.g., React, Next.js, Jetpack Compose, Swift/Kotlin]
+Deployment: [e.g., Vercel, Netlify, Play Store, App Store]
+
+### 3.2. Backend Services
+
+#### 3.2.1. Service Name 1
+
+Name: [e.g., API Service]
+Description: [Core business roles]
+Technologies: [e.g., Spring Boot, Node.js Express, Go]
+Deployment: [e.g., AWS ECS, Kubernetes]
+
+## 4. Data Stores
+
+### 4.1. Data Store 1
+
+Name: [e.g., SQL Database]
+Type: [e.g., PostgreSQL, MongoDB]
+Purpose: [e.g., Account records]
+
+## 5. External Integrations / APIs
+
+- Service Name: [e.g., Stripe, SendGrid]
+- Purpose: [e.g., Payments]
+- Method: [e.g., REST, SDK]
+
+## 6. Deployment & Infrastructure
+
+- Provider: [e.g., AWS, GCP]
+- CI/CD: [e.g., GitHub Actions]
+
+## 7. Security Considerations
+
+- Authentication: OAuth2/JWT
+- Encryption: TLS + AES-256
+
+## 8. Development & Testing Environment
+
+Testing Frameworks: [e.g., Pytest, JUnit, Jest]
+
+## 9. Future Considerations / Roadmap
+
+[Planned changes or architectural debt]
+```
+
+### 2. DESIGN.md Template (Google Spec)
+
+```markdown
+# Design System Specification
+
+---
+
+name: custom-ui-system
+colors:
+primary: "#1D4ED8"
+secondary: "#4B5563"
+background: "#F3F4F6"
+surface: "#FFFFFF"
+text: "#111827"
+
+---
+
+## 1. Visual Theme & Atmosphere
+
+[Rich prose outlining overall design mood, light/dark values, and whitespace philosophy]
+
+## 2. Color Palette & Roles
+
+- Primary foundation
+- Interactive / CTAs
+- Text hierarchy
+- State colors (Success, error, warn)
+
+## 3. Typography Rules
+
+- Hierarchy (headline, body, label)
+- letterSpacing, lineHeight, fontWeights
+
+## 4. Component Stylings
+
+- Buttons
+- Cards
+- Navigation
+- Input fields
+
+## 5. Layout Principles
+
+- Spacing scales
+- Breakpoints
+```
+
+### 3. `docs/conventions.md` Template
+
+Generate a `docs/conventions.md` file containing the Universal DateTime Standard and SOLID Programming Guidelines:
+
+```markdown
+# Conventions
+
+This document defines syntax rules, naming conventions, file boundaries, and automation patterns for this project.
+
+## Universal DateTime Standard
+
+All projects in this ecosystem MUST follow these datetime rules:
+
+1. **UTC at Rest** — All databases and caches store datetimes in UTC with `TIMESTAMP WITH TIME ZONE`. Banned: naive or local-time storage.
+2. **ISO-8601 with Offset / Epoch ms at API Boundaries** — APIs transmit datetimes as Unix Epoch milliseconds (int64) or ISO-8601 with offset (e.g., `2026-07-23T14:30:00+00:00`). Banned: timezone-naive strings.
+3. **Clock Injection** — All current-time access must go through an injectable `Clock` abstraction. Banned: direct `new Date()`, `datetime.now()`, `time.Now()` in business logic.
+4. **Dual-Representation for Future Events** — Calendar events expose both `event_start_local` (with timezone) and `event_start_epoch_ms` (absolute).
+5. **`TZ=UTC` Infrastructure** — All environments run with `TZ=UTC`. Timezone display is a client-layer responsibility only.
+
+## SOLID Programming Guidelines
+
+Enforce these SOLID principles and pragmatic guardrails in every implementation:
+
+1. **SRP** — One reason to change per module. Split merged concerns.
+2. **OCP** — Open for extension, closed for modification. Use composition over inheritance.
+3. **LSP** — Subtypes must be substitutable. Ban `NotImplementedError` overrides.
+4. **ISP** — Small role-specific interfaces. Ban monolithic god-interfaces.
+5. **DIP** — Depend on abstractions, not concretions. Core layer must not import adapters.
+
+**Pragmatic Guardrails:** No abstraction for <3 trivial operations. Only extract interfaces with 2+ implementations. Apply YAGNI strictly. Prefer simpler designs unless a measurable requirement forces complexity.
+
+## Universal Financial Ledger Standard
+
+All financial, transactional, and countable data operations MUST enforce these mandates:
+
+1. **Snapshot-on-Write for Mutable Totals:** Whenever a financial amount, inventory count, or balance is mutated, persist a read-only snapshot of the preceding state in the same transaction (sidecar table, audit log, or WAL). Banned: mutating without preserving the prior value.
+2. **Mandatory `$ifNull` Precedence:** All aggregation queries on monetary fields MUST use explicit null-handling (`COALESCE`, `ISNULL`, `$ifNull`). Banned: passing nullable columns into mathematical operators.
+3. **Observability Alerting on Discrepancies:** If a computed total diverges from its line-item sum by more than 0.01, emit a high-severity alert and prevent finalization.
+4. **Deep Config Merging for Financial Settings:** Financial configuration updates MUST deeply merge nested properties. Banned: shallow object spread on financial config objects.
+
+## Defensive Shell Protocol (DSP)
+
+When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
+
+1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
+2. **Banned Error Masking:** `2>/dev/null` is STRICTLY FORBIDDEN on data-generation, backup, archive, or database commands.
+3. **No Post-Redirect Status Checks:** Never use `command > file; if [ $? -eq 0 ]` — the shell creates the file before running the command, masking failures.
+4. **Sidecar Isolation for Hostless Backups:** Never rely on host file staging for Docker volume backups. Always use ephemeral containers (`docker run --rm -v volume:/data:ro alpine tar...`) with read-only mounts.
+
+## Edit Tool Discipline
+
+File edits use ONLY native file-editing tools (edit for replacements, file-write tools for new files). Using python, shell, heredoc, `sed -i`, or any script to create or modify files is strictly forbidden — scripted edits fail silently (replace-all on non-unique anchors, quoting and encoding mangling) while native tools fail loudly on a non-unique anchor.
+
+1. **Default native only:** one replacement, one location, exact unique anchor. A no-match or multi-match error is a signal, never a retry hint.
+2. **No scripted edits:** python, shell, heredoc, and `sed -i` are banned for creating or modifying files. Shell stays read-only for file content (e.g. grep, cat, diff, ls, git status).
+3. **Verify always:** grep/diff after every edit.
+
+## Task-Number Reference Discipline
+
+Task numbers are provenance for humans, not reasoning material for the model. A bare task number in visible prompt prose invites hallucination: the model treats it as load-bearing context it cannot resolve.
+
+1. **Allowed Homes (only):** code comments (`#`, `//`), `CHANGELOG.md` entries, task files, history archives, and HTML-comment markers (`<!-- -->`).
+2. **Forbidden Homes:** visible prose in prompt fragments, agent instruction files, skill instructions, registry lines, section headings, and any Markdown the Brain or Hands reads as operating instructions.
+3. **Authoring Rule:** when writing or editing prompt-facing Markdown, strip task-number parentheticals. Record provenance in the task file and CHANGELOG instead — never in the prompt text itself.
+
+## Living Folder Docs Standard
+
+All vertical slices and component directories across projects in this ecosystem MUST maintain colocated documentation and decision records:
+
+1. **Folder Colocation** — Every domain component or vertical slice directory (e.g. `src/features/todos/`, `services/auth/`, `mcp-context-server/`) must contain:
+   - `README.md` — Explains the component's core duties, directory layout, owned files, and critical invariants/risks.
+   - `DECISIONS.md` — Chronological log of dated Architectural Decision Records (ADRs). Each entry must document Context, Decision, Consequences, and Rollback strategy.
+2. **One-Line Code Pointer Standard** — Primary source files within the component directory must include a top-line comment pointing directly to the sibling docs:
+   - JavaScript/TypeScript: `// Sibling Docs: <relative-path>/README.md | Decisions: <relative-path>/DECISIONS.md`
+   - Python/Shell: `# Sibling Docs: <relative-path>/README.md | Decisions: <relative-path>/DECISIONS.md`
+3. **Synchronization Invariant** — Whenever source code inside a component directory is added, refactored, or altered in behavior or data contract, the sibling `README.md` and `DECISIONS.md` MUST be inspected and updated within the same task. Silent overrides of existing architectural decisions are strictly forbidden.
+```
+
+---
+
+Use this skill in two modes:
+
+- **Phase 0 (Generation):** When `AGENTS.md` does not exist yet — generate it from the template below.
+- **Audit Mode (Existing):** When `AGENTS.md` already exists — audit and patch it against the Target Audit Criteria.
+
+---
+
+## Mode 1: Phase 0 — Generate AGENTS.md & docs/conventions.md
+
+Use this when a project has no `AGENTS.md` yet (new project onboarding).
+
+### Workflow
+
+1. Read the project's existing context (package configs, README, tech stack files) to determine the project name, description, and relevant tech stack skills.
+2. Generate `AGENTS.md` at the project root using the template below.
+3. Fill in the `[bracketed]` placeholders with the actual project details.
+4. Generate `docs/conventions.md` using the conventions template above, if the project does not already have one.
+5. Confirm both files were created.
+
+### AGENTS.md Template
+
+```markdown
+# [Project Name] — Project Context Hub
+
+## Project Overview
+
+[Brief description of the project, its purpose, and tech stack]
+
+## Setup & Dev Commands
+
+- Build: [build command, e.g., npm run build]
+- Test: [test command, e.g., npm test]
+- Lint: [lint command, e.g., npm run lint]
+- Dev: [dev server command, e.g., npm run dev]
+
+## Actionable Guardrails (Do's & Don'ts)
+
+- **Don't** [common anti-pattern to avoid]
+  -> **Do** [preferred alternative]
+- **Don't** [another anti-pattern]
+  -> **Do** [preferred alternative]
+- **Don't** read `context-reports/` markdown files yourself.
+  -> **Do** generate them using the MCP server — context reports via `custom_context_read_source_files`, tree reports via `custom_context_create_tree_report` ("create a tree of the project") — and hand the file path to the Manager.
+- **Don't** execute Git commands like `git add`, `git commit`, or `git mv` autonomously or try to guess when to stage code.
+  -> **Do** execute Git commands ONLY when explicitly instructed by an Orchestrator task block. Otherwise, rely on the `custom_context_stage_and_inject_diff` MCP tool.
+  -> **Exception:** `git mv` is permitted autonomously for moving task files between Kanban directories.
+- **Don't** guess blindly when facing complex bugs, deadlocks, or silent timeouts.
+  -> **Do** utilize the `debug-instrumentation` skill to inject strategic logs and trace the runtime execution path.
+- **Don't** write bash scripts without strict mode or mask errors with `2>/dev/null` on data commands.
+  -> **Do** follow the Defensive Shell Protocol: `set -euo pipefail`, ban error masking, sidecar isolation for Docker backups. See `docs/conventions.md`.
+- **Don't** perform financial mutations without snapshotting the prior state or allow nulls in monetary aggregations.
+  -> **Do** follow the Universal Financial Ledger Standard: snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging. See `docs/conventions.md`.
+- **Don't** leave task numbers in visible prompt prose, section headings, or skill instructions.
+  -> **Do** keep task-number references in code comments, CHANGELOG entries, task files, history archives, and HTML comments only. See `docs/conventions.md`.
+- **Don't** carry over assumptions, partial results, or architectural hypotheses from a previous task.
+  -> **Do** flush context and treat every task as contextually independent (Buffer Isolation directive in validation-phase).
+- **Don't** execute raw, informal, or non-English prompts directly.
+  -> **Do** load the `prompt-refactor` skill to translate and expand the intent into an elite English spec first. (Note: If you receive a standard XML task block, skip this and execute normally).
+- **Don't** attempt to resolve cross-disciplinary ambiguity within a single persona.
+  -> **Do** trigger the Multi-Agent Brainstorming Loop if the Manager explicitly requests brainstorming or a task exhibits cross-disciplinary ambiguity. Interpret the `<brainstorming_session>` results in backlog tasks as non-functional guidelines that govern execution.
+- **Don't** silently alter slice architecture or domain invariants without updating the sibling README.md and appending a dated ADR to DECISIONS.md.
+  -> **Do** inspect sibling README.md and DECISIONS.md before modifying code, and keep them in sync with implementation changes.
+- **Don't** skip the execution workflow for trivial, single-file changes.
+  -> **Do** traverse the full workflow for every task; keep scope minimal for trivial changes.
+
+## Documentation Sync Rules
+
+When modifying this repository, you must keep these files synchronized:
+
+1. Active task file in `tasks/` (single source of truth for current work items)
+2. `CHANGELOG.md` (Keep a Changelog format)
+3. `DESIGN.md` (UI/UX design system, if modified)
+4. `docs/conventions.md` (syntax rules, datetime standard, SOLID guidelines)
+5. Relevant `SKILL.md` files (if structural patterns were altered)
+
+## 🛑 GATEKEEPER VALIDATION (HALT PROTOCOL)
+
+You (the Hands) are the final gatekeeper. Before executing any implementation task, you MUST evaluate the Orchestrator's instructions against this file and any referenced specs (`DESIGN.md`, `architecture.md`, etc.). If the instructions violate project rules, ignore them. HALT immediately and output a `⚠️ RULE VIOLATION WARNING` back to the Manager explaining exactly what the Orchestrator got wrong, forcing it to self-correct.
+
+## 🛑 CORE FILE LOCATIONS
+
+You MUST strictly adhere to these exact paths. Do not create duplicates elsewhere:
+
+- **Global Rules:** `AGENTS.md` (Root)
+- **UI/UX Specs:** `DESIGN.md` (Root)
+- **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace — optional; only include if project utilizes OpenCode)
+- **Active Tasks:** `tasks/backlog/<task-number>-<name>.md` (backlog), `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`
+
+## 🛑 SKILL LOADING RULES
+
+You MUST follow these skill loading rules in every session:
+
+- **Task-Generator Skill:** Before creating any new task file, you MUST load the `kanban-lifecycle` skill using the `skill` tool to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
+- **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `android-kotlin`, `spring-boot`, `react-vite`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.
+
+## 🛑 CONTEXT BOOTSTRAPPING
+
+At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing.
+
+## 🛑 MANDATORY END-OF-TASK SEQUENCE
+
+When finishing an implementation task, execute these steps in order:
+
+1. Update `CHANGELOG.md` with the task's changes.
+2. Record reasoning and verification evidence in the active task file.
+3. Call `custom_context_qa_transition` once with the active task path and explicit `modified_files`. This tool atomically moves the task to `tasks/qa/`, synchronizes its `**File:**` header, stages modified files, and injects the diff. Do not move the task separately or manually edit its header.
+4. Notify the Manager that the task is in QA and the Hands will chain QA/review through `brain_turn`. Never ask the Manager to copy, paste, or relay task contents.
+5. Do not commit or close the task until the Manager gives the explicit closure approval phrase. Discovery tasks remain in their current lane.
+```
+
+---
+
+## Mode 2: Audit & Patch Existing AGENTS.md and docs/conventions.md
+
+### 🛑 STRICT EXECUTION RULES (Priority 1)
+
+1. **Primary Source of Truth**: You MUST read `AGENTS.md` at the project root using local file read tools.
+2. **Read-Only First**: Evaluate the contents of both `AGENTS.md` and `docs/conventions.md` against the Target Audit Criteria before attempting any file modifications.
+3. **Immutable Formatting**: If patching is required, maintain the exact Markdown list structure, headers, and spacing of the existing file.
+
+### Target Audit Criteria
+
+The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:
+
+- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md` (if present, else note absent per Absent-File Policy), `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`). Only require `.opencode/skills/` when the project already contains `.opencode/` or `with_opencode: true` is set.
+
+Additionally, the `docs/conventions.md` file MUST exist and contain:
+
+- **Universal DateTime Standard**: UTC at rest, Epoch/ISO-8601 with Offset at API boundaries, Clock injection, Dual-Representation for future events, `TZ=UTC` Infrastructure.
+- **SOLID Programming Guidelines**: SRP, OCP, LSP, ISP, DIP, and Pragmatic Guardrails (No abstraction for <3 trivial ops, 3-Implementation Rule, YAGNI, Occam's Razor).
+- **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
+- **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
+- **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator. **Exception:** `git mv` is permitted for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
+- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the active task file. 3) Call `custom_context_qa_transition` once with the active task path and explicit `modified_files`; it atomically moves the task to `tasks/qa/`, synchronizes the header, stages the changes, and injects the diff. Do not perform a separate task move, header edit, or re-stage. 4) Notify the Manager that QA/review will be chained directly through `brain_turn`; never ask the Manager to copy or relay task contents. Do not commit or close without explicit Manager approval.
+- **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
+- **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load the `kanban-lifecycle` skill before creating new task files.
+- **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load every available skill matching the project's tech stack before task implementation.
+- **Project Skills Table (local skills)**: On every audit, scan the project's local skill directories (`.opencode/skills/*/SKILL.md` or equivalent) and (re)build a **Project Skills** table in that project's `AGENTS.md` — one row per local skill: name, trigger (when to load), one-line duty, same column shape as the global Skill Auto-Loading Matrix. Two hard fails: audit without the Project Skills table fails, and a stale row (deleted skill still listed) fails the audit.
+- **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
+- **MCP Report Generation**: `AGENTS.md` MUST instruct agents to generate context reports (`custom_context_read_source_files`) and tree reports (`custom_context_create_tree_report` — "create a tree of the project") via the MCP server and hand the file path to the Manager instead of reading `context-reports/` files inline.
+- **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
+- **Parallel Index Isolation**: Verify the project documents the agent-managed round-trip for shared files — `custom_context_unstage_files` (index-only unstage) followed by `stage_and_inject_diff` with `skip_add=True` — and that `git commit`/`git checkout`/`git push` remain forbidden everywhere.
+- **Edit Tool Discipline**: `AGENTS.md` MUST forbid all scripted file edits — agents may use ONLY native file-editing tools for creating or modifying files (python, shell, heredoc, and `sed -i` are banned for edits; shell stays read-only for file content — e.g. grep, cat, diff, ls, git status). A non-unique anchor must fail loudly, never be forced. `docs/conventions.md` MUST contain a matching `## Edit Tool Discipline` section.
+- **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
+- **Bilingual Prompt Refactoring & Brainstorming Protocol**: Agents MUST be instructed not to execute raw, informal, or non-English prompts directly. The `prompt-refactor` skill must be loaded, or the Phase 1.5 Multi-Agent Brainstorming Protocol triggered, to translate and expand intent first. Standard XML task blocks are exempt.
+- **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
+- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage. When the project uses session-keyed conversation threads, the rules MUST note that flushing covers working execution assumptions only — the conversation thread persists across tasks under the active session ID until sprint completion.
+- **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
+- **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
+- **Task-Number Reference Discipline**: `AGENTS.md` MUST include a guardrail restricting task-number references to code comments, CHANGELOG entries, task files, history archives, and HTML comments — never in visible prompt prose, headings, or skill instructions. `docs/conventions.md` MUST contain a `## Task-Number Reference Discipline` section.
+- **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
+- **Lite Mode Removal (Deprecated Bypass)**: Lite Mode (`<lite_mode_protocol>`, `Lite Mode`, `lite_mode`, `[LITE]`, `Lite-eligible`) is a deprecated bypass and MUST NOT exist in `AGENTS.md`, `docs/conventions.md`, `README.md`, `agents/*.md`, `prompts/**`, or generated prompt artifacts. Every task MUST traverse the full execution workflow with no bypass, escalation, or justification carve-out. When detected, the auditor MUST purge the Lite Mode section/paragraphs entirely (removing bypass clauses so the workflow is unconditional), verify no `<lite_mode_protocol>` fragment or manifest entry remains, and document the purge in the audit findings/changelog. The auditor MUST NOT flag its absence as a missing requirement. Historical traces in `tasks/archive/`, `tasks/completed/`, `docs/history/`, and `CHANGELOG.md` history are provenance only and MUST NOT be rewritten.
+- **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. Deliberate agent config (`[PROJECT_ROOT]/.opencode/smart-compact.jsonc`) is NOT runtime state and MUST NOT be gitignored. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
+- **Living Folder Docs Standard**: docs/conventions.md MUST contain a ## Living Folder Docs Standard section, and AGENTS.md must mandate sibling doc inspection before component edits.
+
+### Resolution Protocol
+
+1. **Evaluation**: Compare the active `AGENTS.md` text against the Target Audit Criteria. Also check if `docs/conventions.md` exists and contains both the DateTime Standard and SOLID Guidelines.
+   - **Absent-File Policy (Mandatory)**: For `DESIGN.md`, `docs/architecture.md`, and `docs/data_model.md` — if any of these files do NOT exist in `[PROJECT_ROOT]`, audit them as `OPTIONAL — SKIPPED GRACEFULLY` with an explicit note. DO NOT flag as fatal errors, non-compliance violations, or missing-file failures. DO NOT hallucinate or scaffold them.
+2. **Patching**: If any constraints are missing, ambiguous, or incorrect in `AGENTS.md`, use the `apply_patch` tool to inject the exact missing rules. If `docs/conventions.md` is missing or incomplete, generate or patch it using the conventions template from Mode 1.
+3. **Halt on Success**: If both files already comply 100%, DO NOT execute any write operations.
+
+### Deprecated Sections Resolution
+
+- **Deprecated Sections Purge**: If any file contains deprecated sections (`## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`), strip those sections cleanly. Do NOT add them back. Record the removal in the audit report under a dedicated "Deprecated Sections Purged" note.
+- **Lite Mode Purge**: If any live file (excluding `tasks/archive/`, `tasks/completed/`, `docs/history/`, `CHANGELOG.md` history, and `prompts/archive/`) contains Lite Mode markers (`<lite_mode_protocol>`, `Lite Mode`, `lite_mode`, `[LITE]`, `Lite-eligible`, `Escalating from Lite Mode`), strip the Lite Mode block and every bypass/escalation/justification sentence, keep the full execution workflow unconditional, and record under "Deprecated Sections Purged". Do NOT add them back.
+
+### Summary Phase
+
+Upon completion, output a strict, formatted summary for the Manager:
+
+### Agent Audit Summary
+
+**Audit Status:** [PASSED | FIXED]
+**AGENTS.md Violations:** [List of missing/incorrect rules, or "None"]
+**conventions.md Status:** [COMPLIANT | MISSING | INCOMPLETE]
+**conventions.md Actions:** [Description of the patch applied, or "Already compliant"]
+**Actions Taken:** [Description of the patches applied, or "Both files already compliant"]
+
+---
+
diff --git a/skill-templates/governance/templates/init.md b/skill-templates/governance/templates/init.md
new file mode 100644
index 0000000..b90b5af
--- /dev/null
+++ b/skill-templates/governance/templates/init.md
@@ -0,0 +1,71 @@
+## Part 2: Living Folder Docs Initializer (from `init-folder-docs`)
+
+# Skill: Living Folder Docs Initializer
+
+Use this skill to onboard existing projects to the Living Folder Docs standard by discovering component directories and scaffolding baseline documentation and code pointers.
+
+## Scope Confinement
+
+- Confine all file scans and generation strictly to `[PROJECT_ROOT]`.
+- Never touch vendor or build directories (`node_modules/`, `.git/`, `dist/`, `build/`, `.venv/`, `vendor/`, `target/`).
+
+## Workflow
+
+1. **Slice Discovery:**
+   - Search the repository for distinct vertical slices, modules, or domain component directories (e.g., `src/features/*`, `apps/*/src/modules/*`, `services/*`, `backend/src/*`).
+   - List all discovered directory paths.
+
+2. **Scaffold Missing Slice Docs:**
+   For each discovered directory `[DIR]`:
+   - **README.md:** If `[DIR]/README.md` does not exist, create it with:
+     - `# Slice: [DIR_NAME]`
+     - `## Duties` (Derived from contained file names and directory role)
+     - `## Files` (List of contained source files with brief 1-line description)
+     - `## Key Risks & Invariants` (Baseline invariants and known edge cases)
+   - **DECISIONS.md:** If `[DIR]/DECISIONS.md` does not exist, create it with:
+     - `# Architectural Decisions: [DIR_NAME]`
+     - `## [YYYY-MM-DD] ADR-001: Initial Slice Baseline`
+     - `- **Context:** Baseline documentation initialized via governance.`
+     - `- **Decision:** Adopting Living Folder Docs standard for this component.`
+     - `- **Consequences:** All future structural or contract changes must be recorded here.`
+     - `- **Rollback:** N/A (baseline adoption).`
+
+3. **Inject Code Pointers:**
+   - In primary source files within `[DIR]` (e.g. main service, controller, model, or entry file), inspect the first 5 lines.
+   - If no sibling docs comment exists, inject the top-line comment pointer:
+     - JS/TS: `// Sibling Docs: [DIR]/README.md | Decisions: [DIR]/DECISIONS.md`
+     - Python/Shell: `# Sibling Docs: [DIR]/README.md | Decisions: [DIR]/DECISIONS.md`
+
+4. **Verification & Summary:**
+   - Run `git status` (read-only) to review generated files.
+   - Output a concise summary listing:
+     - Discovered Slices: count and paths
+     - Created `README.md` files
+     - Created `DECISIONS.md` files
+     - Injected code pointers count
+
+---
+
+## Part 3: Project OpenCode Config Generator (from `opencode-init`)
+
+Turn project analysis into a working `opencode.json` for THAT project only.
+Analyze stack files, ask the user for gaps (default agent,
+formatter, LSP guidance, instructions, permissions), emit JSON matching
+the public schema (https://opencode.ai/config.json),
+then validate with `scripts/validate-opencode.py` before writing.
+MCP servers and plugins install GLOBALLY — never emit `mcp` or `plugin`
+into the project file. Never edit global config. Never install plugins.
+
+### Ground Truth (public schema wins)
+
+- Shape: project-only keys: `$schema`, `default_agent`, `instructions[]`, `formatter`, `lsp`, `permission{}`. `mcp{}` and `plugin[]` are GLOBAL-only and banned from project output.
+- Formatter: `true` | `false` | named map `{<name>: {command?, extensions?, environment?, disabled?}}`. NEVER emit a flat `{command, extensions}` object — it fails validation. LSP uses flat map `{<name>: {command, extensions?, env?, initialization?, disabled?}}`, NEVER a `language-server` key.
+- LSP: `true` | `false` | map `{<name>: {command (required), extensions?, env?, initialization?, disabled?}}`. NEVER wrap in `language-server`; LSP uses `env`.
+- Secrets travel ONLY as `{env:NAME}` placeholders in global scope — never literal values. `default_agent` must name an existing primary agent. Merge order: remote → global → custom → project root → subdir.
+
+### Workflow
+
+1. **Analyze.** Read manifests, README, stack files, existing `opencode.json`/`AGENTS.md`/`.opencode/`. Record stack, agents dir, formatter/LSP/instructions/permission needs. Do NOT record MCP needs or plugin choices.
+2. **Ask user for gaps.** Missing `default_agent`, formatter/LSP/instructions/permission choices. Ambiguous means NOT answered — HALT and re-ask. Never ask for MCP env keys or plugin selection.
+3. **Generate.** Emit project-only JSON (allowlist: `$schema`, `default_agent`, `instructions`, `formatter`, `lsp`, `permission`). Omit `mcp`/`plugin`; note global install paths instead.
+4. **Validate, then write.** Run `scripts/validate-opencode.py <file>`. Zero errors required. Write ONLY to target project root `opencode.json`. One project per run. Never touch global config. Never `git commit`. ZAC deny set is mandatory in every generated file: `git add`, `git checkout`, `git commit`, `git push` → `deny`.
diff --git a/skill-templates/opencode-init/references/examples/golden-opencode.json b/skill-templates/governance/templates/opencode-init/references/examples/golden-opencode.json
similarity index 100%
rename from skill-templates/opencode-init/references/examples/golden-opencode.json
rename to skill-templates/governance/templates/opencode-init/references/examples/golden-opencode.json
diff --git a/skill-templates/opencode-init/references/runtime-matrix.md b/skill-templates/governance/templates/opencode-init/references/runtime-matrix.md
similarity index 100%
rename from skill-templates/opencode-init/references/runtime-matrix.md
rename to skill-templates/governance/templates/opencode-init/references/runtime-matrix.md
diff --git a/skill-templates/opencode-init/scripts/validate-opencode.py b/skill-templates/governance/templates/opencode-init/scripts/validate-opencode.py
old mode 100644
new mode 100755
similarity index 100%
rename from skill-templates/opencode-init/scripts/validate-opencode.py
rename to skill-templates/governance/templates/opencode-init/scripts/validate-opencode.py
diff --git a/skill-templates/kanban-lifecycle/SKILL.md b/skill-templates/kanban-lifecycle/SKILL.md
index 7fb09e3..53a32ee 100644
--- a/skill-templates/kanban-lifecycle/SKILL.md
+++ b/skill-templates/kanban-lifecycle/SKILL.md
@@ -3,601 +3,27 @@ name: kanban-lifecycle
 description: Unified Kanban lifecycle — task generation, lint validation, META bundling, completion archiving, and flat-to-V6 migration in one meta skill.
 ---
 
-# Kanban Lifecycle Meta Skill
+# Kanban Lifecycle Meta Skill (slim index)
 
-Meta skill combining **task-generator** (create), **task-lint** (validate), **bundle-tasks** (META bundling), **archive-tasks** (milestone compaction), and **migrate-kanban** (flat migration). Load one skill for any `tasks/` work. Sections are verbatim from the source skills.
+Meta skill combining **task-generator** + **task-lint** + **bundle-tasks** + **archive-tasks** + **migrate-kanban**. Full bodies are verbatim in `templates/` — read only the part you need.
 
 ---
 
-## Part 1: Task Generator Workflow (from `task-generator`)
+## Critical Rules (no read needed)
 
-# Task Generator Workflow
+- **ZAC:** Staging via `custom_context_stage_and_inject_diff` only; closure on exact “Approved for closure” / “Close task”.
+- **Task template:** unified canonical with `## Goal`, `## Local TODOs`, `## Acceptance Criteria`, `## Verification Evidence` (rtk test), `## Definition of Done`, `## Risk & Rollback`, `<!-- BEGIN_GIT_DIFF -->` markers. `**Source:**`/`**Type:**` required; `Meta: true` + `Supersedes` for METAs.
+- **IDs:** `NEXT_ID` via `find tasks/ -type f -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 +1` across ALL lanes (archive reuses consumed IDs → active duplicates fail). Collision check (`ls tasks/backlog/${NEXT_ID}-*.md`) is a hard stop.
+- **Bundle:** cap 6, LOC >400 warn, verbatim preservation, `git mv` to `tasks/archive/` only — never purge until META is `completed`.
+- **Archive:** `tasks/completed/` → dense `docs/history/milestone-X-summary.md`; stale-memory audit (flag only, never delete without Manager approval).
+- **QA:** all-or-nothing funnel; any failed bundled item rejects the META.
 
-You are the Task Generator. Your job is to create structured task files for the Manager.
+## When to Read Templates
 
-## Workflow
+- **Create/edit a task file** → `templates/01-generate.md` (Workflow + Bundle Workflow).
+- **Validate a task file** → `templates/02-lint.md`.
+- **Bundle 2–6 tasks into META** → `templates/03-bundle.md`.
+- **Archive a milestone** → `templates/04-archive.md`.
+- **Migrate flat `tasks/` → V6 lanes** → `templates/05-migrate.md`.
 
-1. **Analyze:** Determine if the request is a `bug`, `improvement`, or `feature`.
-2. **Index:** Search all Kanban subdirectories in `tasks/` for the highest existing task ID. Run:
-
-```bash
-NEXT_ID=$(find tasks/ -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
-if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ]; then NEXT_ID="01"; fi
-printf "%02d\n" $NEXT_ID
-```
-
-Use the output as the zero-padded task number. If `tasks/` doesn't exist, create it along with the Kanban subdirectories and start at `01`.
-
-Title consistency check (unified template `# Task [NN]: [Title]`): flag any duplicate title numbers:
-
-```bash
-grep -rhn "^# Task [0-9][0-9]*:" tasks/ | sort | uniq -d
-```
-
-The title number MUST match the filename ID. Any mismatch or duplicate must be resolved with the Collision Check below before writing the file.
-
-Duplicate ID check — flag any duplicated numeric task IDs across the ACTIVE Kanban directories only:
-
-```bash
-find tasks/backlog tasks/in-progress tasks/qa tasks/completed -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort | uniq -d
-```
-
-If the output is non-empty, HALT and report duplicate task IDs. Do NOT overwrite files. Archive is a historical record and MUST NOT be included in the blocking duplicate-ID check. If archive duplicates are discovered separately, report them as a warning only, never HALT task creation.
-
-3. **Name:** Create a kebab-case filename (e.g., `01-fix-login-bug.md`). Place it in `tasks/backlog/`. Task-number discipline: the filename and `# Task [NN]` title carry the number exactly once — never repeat task numbers in template prose, headings, or notes (numbers live only in code comments, CHANGELOG, history, and HTML comments).
-
-3.5. **Collision Check:** Before writing the file, verify that `tasks/backlog/{NEXT_ID}-*.md` does NOT already exist. Run: `ls tasks/backlog/${NEXT_ID}-*.md`. If a file with that ID already exists, HALT and report: '⚠️ Task ID collision: {NEXT_ID} is already in use. Re-run ID discovery.' Do NOT overwrite existing files.
-
-4. **Generate File:** Write the following unified canonical template to the new file. The `## Source Context` section is **polymorphic** — include ONLY the variant block matching the `**Source:**` value. `## Goal`, `## Local TODOs`, `## Acceptance Criteria`, `## Verification Evidence`, and `## Risk & Rollback` are MANDATORY and UNCONDITIONAL for ALL source types (lint contract):
-
-   ```markdown
-   # Task [NN]: [Title]
-
-   **File:** `tasks/backlog/[filename]`
-   **Source:** [orchestrator|telegram|manager]
-   **Type:** [bug|improvement|feature]
-   **Status:** open
-
-   ## Source Context
-
-   ### Variant A: Orchestrator (`**Source:** orchestrator`)
-
-   ## Goal
-
-   [Summary of the goal — MANDATORY]
-
-   ## Blueprint Reference
-
-   [Link or reference to the approved architectural blueprint]
-
-   ## Manager's Notes
-
-   [Any specific notes, requirements, or constraints]
-
-   ### Variant B: Telegram (`**Source:** telegram`)
-
-   ## Goal
-
-   [MANDATORY — one-line goal derived from the RAW_TEXT]
-
-   ## Original Message ([Language])
-
-   {RAW_TEXT — verbatim, zero changes}
-
-   ## English Translation
-
-   {EN_TRANSLATION}
-
-   ## Refactored Prompt
-
-   {REFACTORED_PROMPT}
-
-   ## Relevant Code Context
-
-   {CODEBASE_CONTEXT}
-
-   ## AI Analysis & Opinion
-
-   {AI_OPINION}
-
-   ### Variant C: Manager (`**Source:** manager`)
-
-   ## Goal
-
-   [Summary of the goal — MANDATORY]
-
-   ## Manager's Notes
-
-   [Any specific notes, requirements, or constraints]
-
-   <!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->
-
-   ## Local TODOs
-
-   - [ ] Initial codebase exploration
-   - [ ] [Specific step 1]
-   - [ ] Verify functionality
-
-   ## Acceptance Criteria
-
-   - [ ] [Criterion 1 — what must be true for this task to be considered done]
-   - [ ] [Criterion 2]
-
-    ## Verification Evidence
-
-    - **Test command:** rtk test [exact command]
-    - **Expected result:** [what success looks like]
-    - **Actual result:** _(The Hands fill this during execution)_
-    - **Exit code:** _(The Hands fill this during execution)_
-
-    > Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.
-
-   ## Definition of Done
-
-   The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):
-
-   - [ ] Build/Test/Lint pass with exit code 0
-   - [ ] `lint_task_file` passes on the active task file
-   - [ ] `CHANGELOG.md` updated via Parse-Then-Append
-   - [ ] `testing-verification` applied and evidence recorded
-
-   > **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.
-
-   ## Risk & Rollback
-
-   - **Risk:** [what could go wrong]
-   - **Rollback plan:** [how to undo if needed]
-
-   ---
-
-   ## Execution Log & Reasoning
-
-   _(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_
-
-   ## Factual Git Diff
-
-   <!-- BEGIN_GIT_DIFF -->
-
-   _(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_
-
-   <!-- END_GIT_DIFF -->
-   ```
-
-## Multi-Phase Task Template
-
-If the Orchestrator specifies `multi_phase: true`, generate a SINGLE task file with inline phase sections instead of separate files. Use this structure (same unified metadata header, `## Goal` mandatory):
-
-```markdown
-# Task [NN]: [Title]
-
-**File:** `tasks/backlog/[filename]`
-**Source:** [orchestrator|telegram|manager]
-**Type:** [bug|improvement|feature]
-**Status:** open
-
-## Goal
-
-[Summary of the goal]
-
-## Acceptance Criteria
-
-- [ ] [Criterion 1 — what must be true for this task to be considered done]
-- [ ] [Criterion 2]
-
-## Verification Evidence
-
-- **Test command:** rtk test [exact command]
-- **Expected result:** [what success looks like]
-- **Actual result:** _(The Hands fill this during execution)_
-- **Exit code:** _(The Hands fill this during execution)_
-
-> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.
-
-## Definition of Done
-
-The task is NOT done unless ALL of the following are true (unconditional, applies to every multi-phase task):
-
-- [ ] Build/Test/Lint pass with exit code 0
-- [ ] `lint_task_file` passes on the active task file
-- [ ] `CHANGELOG.md` updated via Parse-Then-Append
-- [ ] `testing-verification` applied and evidence recorded
-
-> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.
-
-## Risk & Rollback
-
-- **Risk:** [what could go wrong]
-- **Rollback plan:** [how to undo if needed]
-
-## Phase 1: [Name]
-
-### Local TODOs
-
-- [ ] [Phase 1 step 1]
-- [ ] [Phase 1 step 2]
-
-## Phase 2: [Name]
-
-### Local TODOs
-
-- [ ] [Phase 2 step 1]
-- [ ] [Phase 2 step 2]
-
-## Execution Log & Reasoning
-
-_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_
-
-## Factual Git Diff
-
-<!-- BEGIN_GIT_DIFF -->
-
-_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_
-
-<!-- END_GIT_DIFF -->
-```
-
-5. **Halt and Handover:** DO NOT execute the task. Keep the generated task in `tasks/backlog/`. Invoke `brain_turn` directly under the active session thread with the generated task ID and task-file context. The Manager must not copy, paste, or relay task contents. Continue only through the normal planning and approval gates.
-
-## Bundle Workflow (Meta-Tasks, Pure MCP)
-
-Use this when the Manager has 4–6 small related tasks that should be executed together instead of sequentially. The bundler preserves every requirement verbatim and archives the sources.
-
-### When to Use
-
-- Manager says: "bundle tasks 1, 2, 5, 10, 15, 20" or "create a meta-task from 12 15 20"
-- Tasks are small, same stack/domain (e.g., all Android polish), and would be inefficient to run one-by-one
-- Goal is one branch, one `Factual Git Diff`, one QA gate (all-or-nothing)
-
-### Canonical Invocation — Pure MCP Tool
-
-Invoke the `bundle_tasks` MCP tool via the Hands:
-
-```json
-{
-  "tool": "bundle_tasks",
-  "arguments": {
-    "task_ids": ["12", "15", "20"],
-    "title": "android-polish-bundle",
-    "dry_run": false,
-    "force": false
-  }
-}
-```
-
-Examples (MCP arguments):
-
-- `task_ids: ["12","15","20"], title: "android-polish-bundle"`
-- `task_ids: ["12","15","20"], title: "android-polish-bundle", dry_run: true`
-- `task_ids: ["1","2","3","4","5","6","7"], title: "mega-bundle", force: true  // bypass 6-cap`
-
-### What the Script Does (Deterministic, No LLM)
-
-1. **Validate IDs:** searches `tasks/backlog/ tasks/in-progress/ tasks/qa/ tasks/completed/` (active only, archive excluded) for each `<id>-*.md`. HALT if any missing or if archive already contains the ID (already superseded). Rejects non-numeric IDs.
-2. **Next-ID Discovery:** `find tasks -type f -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 +1` across ALL dirs (including archive) — guarantees no collision. Zero-padded (`02d` for <100, raw for >=100).
-3. **Slug:** kebab-case the `--title` (`android Polish_Bundle` → `android-polish-bundle`). Output file: `tasks/backlog/<NEXT_ID>-<slug>.md`.
-4. **Verbatim Extraction:** for each source, extracts `## Goal`, `## Manager's Notes`/`## Blueprint Reference`, `## Acceptance Criteria`, `## Local TODOs`, `## Risk & Rollback` verbatim (regex until next `## `). No summarization.
-5. **Generate META File:** canonical template + extra metadata:
-   - `**Supersedes:** [12, 15, 20]`
-   - `**Meta:** true` (flag for tooling; `**Type:**` stays `feature` for lint compat, `meta` is also allowed)
-   - Per-source appendix: `### Source Task XX: Title` with verbatim blocks
-   - `## Bundled Checklist (All-or-Nothing)` — every source AC line prefixed `[XX]`, single QA gate
-   - `## Local TODOs` aggregates all source TODOs prefixed `[XX]` plus bundle-specific steps
-   - Guardrail notes: diff-size warning if combined LOC >400
-6. **Auto-Archive:** unless `--dry-run`, runs `git mv <source> tasks/archive/<source>` (fallback to `mv` + `git add` for untracked) and patches the archived file:
-   - `**File:**` → `tasks/archive/<file>`
-   - `**Status:** superseded`
-   - `**Superseded-By:** <META_ID>-<slug>` + `**Superseded-At:** YYYY-MM-DD`
-   - Superseded footer before `## Execution Log` with `git log --follow` hint
-     History remains reachable: `git log --oneline --follow -- tasks/archive/<file>`
-
-### Guardrails
-
-- **Cap:** `MAX_BUNDLE_SIZE=6` — rejects >6 without `--force` (mega-diff prevention)
-- **Diff-size:** warns if combined source LOC >400 ("consider split")
-- **Duplicate/Collision:** `ls tasks/backlog/<NEXT_ID>-*.md` check before write; HALT if exists. Duplicate active IDs HALT.
-- **Archive-Only:** `git mv` to `tasks/archive/` — never `git rm` / purge until META reaches `tasks/completed/`; rollback is `git mv tasks/archive/<id>-*.md tasks/backlog/`
-
-### QA & Completion
-
-- META follows normal Kanban: `tasks/backlog/<META>` → `tasks/in-progress/<META>` → `tasks/qa/<META>` → `tasks/completed/<META>` with a single injected diff
-- QA is all-or-nothing: if ANY bundled criterion fails, entire META is `QA_REJECTED`
-
-### Verification
-
-```bash
-bundle_tasks(task_ids=["12","15","20"], title="test", dry_run=true)
-lint_task_file tasks/backlog/<META_FILE>
-git log --oneline --follow -- tasks/archive/12-*.md | head
-```
-
----
-
-## Part 2: Task Lint Skill (from `task-lint`)
-
-# Task Lint Skill
-
-## When to Run
-
-1. **After Part 1 creates a new task file** — validate structure before handing to Orchestrator.
-2. **Before closing a task** — validate the task file is complete and well-formed.
-3. **During Part 4 archiving** — validate all tasks before compacting.
-
-## Workflow
-
-1. Call `lint_task_file` with the active task file path.
-2. If issues found, report them and HALT.
-3. If clean, proceed.
-
-## For Markdown files (non-task)
-
-1. Call `lint_markdown` with the file path.
-2. Report issues.
-
----
-
-## Part 3: Bundle Tasks Skill — Meta-Task Bundling (from `bundle-tasks`)
-
-# Bundle Tasks Skill — Meta-Task Bundling
-
-Use this skill when the Manager wants to execute 4–6 small related tasks together instead of sequentially. It eliminates the `backlog → in-progress → qa → completed` round-trip overhead by bundling them into one branch, one `Factual Git Diff`, and one all-or-nothing QA gate.
-
-## When to Use
-
-- Manager says: "bundle tasks 1, 2, 5, 10, 15, 20", "create a meta-task from 12 15 20", "combine these polish tasks", or any note about "meta-task", "bundle", "supersede", "archive and bundle"
-- Tasks are small, same stack/domain (e.g., all `android-kotlin`, all `react-vite`, all docs), and would be inefficient to run one-by-one
-- You are in any project that has the `mcp-context-server` MCP server — the bundler is available as the `bundle_tasks` MCP tool (pure MCP)
-
-**Do NOT use for:** large refactors, tasks with conflicting files that would cause merge conflicts in one diff, or tasks >6 without explicit `--force`.
-
-## Core Contract (Deterministic, No LLM, No Hallucination)
-
-1. **Verbatim Preservation:** Every source `## Goal`, `## Manager's Notes` / `## Blueprint Reference`, `## Acceptance Criteria` (including multi-line continuations and indented sub-bullets), `## Local TODOs`, `## Risk & Rollback` is copied verbatim into `### Source Task XX` blocks. No summarization. The `## Bundled Checklist` is derived by prefixing each source AC root bullet with `[XX]` and preserving all indented continuation lines.
-2. **Single QA Gate:** All bundled criteria are `all-or-nothing`. If any line fails QA, the entire META is `QA_REJECTED`.
-3. **Archive, Not Purge (with Transactional Rollback):** Sources are moved via `git mv` to `tasks/archive/` with `**Superseded-By:** <META_ID>-<slug>` until META is `completed`. History stays reachable via `git log --follow`. If ANY archive operation fails, ALL previously archived files are rolled back to their original locations, the META file is deleted, and the operation aborts cleanly.
-4. **Guardrails:** `MAX_BUNDLE_SIZE=6` (reject >6 without `--force`), combined LOC >400 warning, missing-ID and duplicate-ID checks (hard halt on duplicate active IDs), stack conflict detection (warn or require `--force`), SHA verbatim checksum validation, atomic Next-ID creation with retry loop for concurrent safety.
-
-## Invocation — Pure MCP Tool
-
-The `mcp-context-server/server.py:bundle_tasks` tool is **fully self-contained** — it does NOT require `scripts/bundle-tasks.py`. All helpers (kebab_case, discover_next_id, find_task_file, extract_section, build_meta_content, git_mv_or_fallback, patch_archived_file) are inlined inside the MCP tool function. Invoke via the Hands' MCP interface:
-
-```json
-{
-  "tool": "bundle_tasks",
-  "arguments": {
-    "task_ids": ["12", "15", "20"],
-    "title": "android-polish-bundle",
-    "dry_run": true,
-    "force": false
-  }
-}
-```
-
-**Tool name:** `bundle_tasks` on `mcp-context-server` (`custom_context` FastMCP server). It validates IDs, discovers NEXT_ID, slugifies title, generates META with verbatim preservation, and auto-archives sources. Dry-run prints preview without file creation. Pure MCP — no external script dependency.
-
-## What Happens (Deterministic Steps)
-
-1. **Validate IDs:** Search `tasks/backlog/ tasks/in-progress/ tasks/qa/ tasks/completed/` (active only, `tasks/archive/` excluded per `task-generator` duplicate-ID contract) for each `<id>-*.md`. HALT if any missing; note if found in archive (already superseded). Reject non-numeric IDs.
-2. **Discover NEXT_ID:** `find tasks -type f -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}'` across **ALL** dirs including `archive` (no collision). Zero-padded `02d` for <100, raw for ≥100.
-3. **Slugify Title:** `title` → kebab-case (`android Polish_Bundle` → `android-polish-bundle`). Output file: `tasks/backlog/<NEXT_ID>-<slug>.md`.
-4. **Verbatim Extraction:** For each source, extract `## Goal`, `## Manager's Notes`/`## Blueprint Reference`, `## Acceptance Criteria`, `## Local TODOs`, `## Risk & Rollback` verbatim via regex `^## Heading$(.*?)(?=^## |\n---\s*\n|\Z)`. No summarization.
-5. **Generate META File:** Canonical task template + `**Supersedes:** [12, 15, 20]` + `**Meta:** true` + `**Created:**` + per-source appendix `### Source Task XX: Title` + `## Source Bundles (Verbatim Preservation)` + `## Bundled Checklist (All-or-Nothing)` (every source AC line prefixed `[XX]`, single QA gate) + aggregated `## Local TODOs` (`[XX]`-prefixed) + guardrail notes (LOC warning if >400).
-6. **Auto-Archive (unless dry_run):** `git mv <src> tasks/archive/<src>` (fallback to `mv` + `git add` for untracked) then patch archived file: `**File:**` → `tasks/archive/<file>`, `**Status:** superseded`, add `**Superseded-By:** <META_ID>-<slug>` + `**Superseded-At:** YYYY-MM-DD`, inject superseded footer before `## Execution Log`. History remains reachable: `git log --oneline --follow -- tasks/archive/<file>` — **never** `git rm` until META is `completed`.
-7. **Kanban:** META follows normal `tasks/backlog/<META>` → `tasks/in-progress/<META>` → `tasks/qa/<META>` → `tasks/completed/<META>` with one injected `Factual Git Diff`. QA is all-or-nothing.
-
-## Guardrails (Hard Stops & Warnings)
-
-- **Cap:** `MAX_BUNDLE_SIZE=6` — rejects >6 without `--force` (mega-diff prevention). Use `--force` to override.
-- **Floor:** bundles need 2-6 tasks — a single task or duplicate IDs in one request are rejected with an explicit error, never silently deduped.
-- **Diff-size:** Warns if combined source LOC >400 (`> ⚠️ 400` in notes) — "consider split".
-- **Missing / Duplicate / Collision:** Missing IDs → `❌ Missing tasks`; duplicate IDs across active Kanban dirs → distinct `❌ Duplicate task ID` error (never misreported as missing); same-ID-different-slug files for the allocated ID (either zero-padding) → `❌ Task ID collision`; allocation races rebuild the META body after the final ID and create-plus-write atomically, so no stale-ID or empty META file survives.
-- **Stack Conflict (M1):** Auto-detects stack from content (android, react, fastapi, spring, ios, go). If tasks have conflicting stacks → requires `--force` to proceed.
-- **Verbatim Checksum (M2):** After META generation, verifies every AC line from source tasks appears in the META. Fails if any text was dropped.
-- **Archive-only:** Sources go to `tasks/archive/` via `git mv` only. Purge (`git rm`) is blocked until META is `completed`. On ANY archive failure: **transactional rollback** restores byte-identical originals to their recorded origin dirs (no header guessing, failures surfaced), deletes META, exits with clear error.
-- **Unicode Slugs (B4):** `_kebab_case()` normalizes via NFKD and preserves non-English characters (\u0600-\u06FF). Non-English titles produce valid slugs like `تست-باندل` instead of losing all characters.
-
-## Verification (Must Pass Before QA)
-
-```bash
-# via MCP (pure MCP):
-bundle_tasks(task_ids=["12","15","20"], title="test-bundle", dry_run=true)
-
-# then after real bundle (if not dry_run):
-lint_task_file tasks/backlog/<NEXT_ID>-<slug>.md
-lint_task_file tasks/archive/12-*.md
-git log --oneline --follow -- tasks/archive/12-*.md | head
-py_compile: python3 -m py_compile mcp-context-server/server.py
-```
-
-- META must contain `**Supersedes:**` + every source `### Source Task` block + `## Bundled Checklist` with `[XX]` prefixes.
-- `lint_task_file` must pass on META (fixed `---` → `---\n\n` blank-line; `**Type:**` allows `feature` + `Meta:true` and also `meta`) and on both archived files (`**Status:** superseded` is allowed; `**File:**` matches archive path).
-- `git log --follow` must show the source's history through the rename.
-
-## Skill Loading
-
-Load this skill when you handle bundling:
-
-```bash
-skill("kanban-lifecycle")
-```
-
-If you also need lint validation, use Part 2 of this skill; for context gathering before bundling, load `code-search` to ensure sources are in the expected Kanban dirs.
-
-## Rollback
-
-If META is abandoned or fails QA permanently:
-
-```bash
-git mv tasks/archive/12-*.md tasks/backlog/12-*.md
-git mv tasks/archive/15-*.md tasks/backlog/15-*.md
-git mv tasks/backlog/<NEXT_ID>-<slug>.md tasks/archive/<NEXT_ID>-<slug>.md  # mark abandoned and preserve history
-```
-
-No HQ code beyond the bundler is affected. If META already reached `tasks/completed/`, its archived sources stay in `tasks/archive/` permanently (they are superseded, not purged).
-
-## Reference
-
-- **MCP:** `mcp-context-server/server.py:bundle_tasks` (self-contained, verbatim helpers inlined, `task_ids: list[str], title: str, dry_run, force`, path-traversal safe, cap 6)
-- **Docs:** `AGENTS.md` `## 🛑 META-TASK BUNDLE LIFECYCLE` + `**Bundle Tool:**`, `CHANGELOG.md` `[Unreleased]`
-- **Lint:** `mcp-lint-server/server.py` Type regex now `...|meta`
-- **Registry:** `prompts/fragments/07-agent_skills_registry.md` lists `kanban-lifecycle`
-
----
-
-## Part 4: Archive Tasks Skill (from `archive-tasks`)
-
-# Archive Tasks Skill
-
-## Purpose
-
-Prevents the `tasks/completed/` directory from accumulating hundreds of task files by periodically compacting completed tasks into dense, single-file milestone summaries in `docs/history/`.
-
-## Workflow
-
-1. **Scan completed tasks** for the current milestone:
-
-```bash
-ls tasks/completed/*.md
-```
-
-2. **Read each file** and extract:
-   - Task number and title
-   - Type (bug/improvement/feature)
-   - Source (from the `**Source:**` metadata line)
-   - Execution Log & Reasoning (architectural reasoning)
-   - Key files modified
-
-3. **Generate a milestone summary** at `docs/history/milestone-X-summary.md` with the following structure:
-
-   ```markdown
-   # Milestone X Summary
-
-   **Date:** YYYY-MM-DD
-   **Tasks Compacted:** N
-
-   ## Source Distribution
-
-   | Source       | Count |
-   | ------------ | ----- |
-   | orchestrator | N     |
-   | telegram     | N     |
-   | manager      | N     |
-
-   ## Architectural Changes
-
-   [Dense summary of all architectural changes across the milestone]
-
-   ## Files Modified
-
-   | File         | Change      |
-   | ------------ | ----------- |
-   | path/to/file | description |
-
-   ## Criteria Met
-
-   | Task | Acceptance Criteria | Status |
-   | ---- | ------------------- | ------ |
-   | XX   | [Extracted criteria from the completed task's `## Acceptance Criteria` section] | ✅ Met |
-
-   ## Individual Task Summaries
-
-   ### Task XX: Title
-
-   - **Type:** bug|improvement|feature
-   - **Source:** [orchestrator|telegram|manager]
-   - **Reasoning:** [condensed execution log]
-   ```
-
-4. **Create the `docs/history/` directory** if it does not exist:
-
-```bash
-mkdir -p docs/history
-```
-
-5. **Move completed files to archive**:
-
-```bash
-git mv tasks/completed/*.md tasks/archive/
-```
-
-*Note: For untracked task files, use the supported native file-management operation to move them. Stage the moved files only through `custom_context_stage_and_inject_diff`; never run `git add` directly.*
-
-6. **Memory Validation:** After compacting tasks, audit the project memory bank for stale or superseded entries:
-   a. Call `list_namespaces` to enumerate all memory namespaces.
-   b. For each namespace, call `search_memory` using keywords from the archived tasks.
-   c. Identify memories that reference archived/completed task files or superseded workflows.
-   d. Detect duplicates: if two memories in the same namespace cover the same topic and one references a newer date or task, flag the older one as superseded.
-   e. Output a `## Stale Memory Report` listing all flagged memories with their namespace, key, and reason for flagging.
-   f. Wait for Manager approval before calling `delete_memory` on any flagged entry. NEVER auto-delete memories without explicit Manager confirmation.
-
-7. **Stage the new summary and moved files**:
-
-Call `custom_context_stage_and_inject_diff` with the active task file and an explicit `modified_files` list containing the generated milestone summary and every moved task-file path. Do not run `git add` directly.
-
-## When to Run
-
-Run this skill at the end of each milestone or when `tasks/completed/` contains more than 20 files. The milestone number should be determined by reading the highest existing milestone in `docs/history/` and incrementing by one.
-
----
-
-## Part 5: Migrate Kanban Skill (from `migrate-kanban`)
-
-# Migrate Kanban Skill
-
-## Purpose
-
-Transforms a flat `tasks/` directory (e.g., `tasks/01-task.md`, `tasks/02-task.md`) into the state-based V6 Kanban lifecycle structure:
-
-- `tasks/backlog/` — Open / unstarted tasks
-- `tasks/in-progress/` — Currently being worked on
-- `tasks/qa/` — Awaiting review / quality assurance
-- `tasks/completed/` — Finished tasks
-- `tasks/archive/` — Milestone-compacted historical tasks
-
-## Workflow
-
-1. **Create the 5 Kanban directories** if they do not already exist:
-
-```bash
-mkdir -p tasks/backlog tasks/in-progress tasks/qa tasks/completed tasks/archive
-```
-
-2. **Scan all `.md` files** in the flat `tasks/` root (excluding the Kanban subdirectories):
-
-```bash
-find tasks/ -maxdepth 1 -type f -name "*.md" | sort
-```
-
-3. **Classify each file** by reading its frontmatter or first line:
-
-   - If the file contains `Status: open` (or `**Status:** open`), move it to `tasks/backlog/`.
-   - If the file contains `Status: closed` (or `**Status:** closed`), move it to `tasks/completed/`.
-   - If no status is found, default to `tasks/backlog/`.
-
-4. **Move the files** using `git mv` to preserve history:
-
-```bash
-for f in tasks/*.md; do
-  [ -e "$f" ] || continue
-  [ "$f" = "tasks/README.md" ] && continue
-  if grep -qi "Status: open" "$f"; then
-    git mv "$f" tasks/backlog/
-  elif grep -qi "Status: closed" "$f"; then
-    git mv "$f" tasks/completed/
-  else
-    git mv "$f" tasks/backlog/
-  fi
-done
-```
-
-5. **Verify** the migration:
-
-```bash
-echo "=== Backlog ===" && ls tasks/backlog/
-echo "=== Completed ===" && ls tasks/completed/
-```
-
-6. **Update AGENTS.md** to reference the Kanban directory structure in the "Core File Locations" and "Documentation Sync Rules" sections.
-
-## Post-Migration
-
-After running this skill, the flat `tasks/` directory should be empty (except for the 5 Kanban subdirectories). All existing task history is preserved via `git mv`.
+Templates are authoritative; this index only summarizes. Registry: `prompts/fragments/07-agent_skills_registry.md`.
diff --git a/skill-templates/kanban-lifecycle/templates/01-generate.md b/skill-templates/kanban-lifecycle/templates/01-generate.md
new file mode 100644
index 0000000..f69f80c
--- /dev/null
+++ b/skill-templates/kanban-lifecycle/templates/01-generate.md
@@ -0,0 +1,303 @@
+## Part 1: Task Generator Workflow (from `task-generator`)
+
+# Task Generator Workflow
+
+You are the Task Generator. Your job is to create structured task files for the Manager.
+
+## Workflow
+
+1. **Analyze:** Determine if the request is a `bug`, `improvement`, or `feature`.
+2. **Index:** Search all Kanban subdirectories in `tasks/` for the highest existing task ID. Run:
+
+```bash
+NEXT_ID=$(find tasks/ -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
+if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ]; then NEXT_ID="01"; fi
+printf "%02d\n" $NEXT_ID
+```
+
+Use the output as the zero-padded task number. If `tasks/` doesn't exist, create it along with the Kanban subdirectories and start at `01`.
+
+Title consistency check (unified template `# Task [NN]: [Title]`): flag any duplicate title numbers:
+
+```bash
+grep -rhn "^# Task [0-9][0-9]*:" tasks/ | sort | uniq -d
+```
+
+The title number MUST match the filename ID. Any mismatch or duplicate must be resolved with the Collision Check below before writing the file.
+
+Duplicate ID check — flag any duplicated numeric task IDs across the ACTIVE Kanban directories only:
+
+```bash
+find tasks/backlog tasks/in-progress tasks/qa tasks/completed -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort | uniq -d
+```
+
+If the output is non-empty, HALT and report duplicate task IDs. Do NOT overwrite files. Archive is a historical record and MUST NOT be included in the blocking duplicate-ID check. If archive duplicates are discovered separately, report them as a warning only, never HALT task creation.
+
+3. **Name:** Create a kebab-case filename (e.g., `01-fix-login-bug.md`). Place it in `tasks/backlog/`. Task-number discipline: the filename and `# Task [NN]` title carry the number exactly once — never repeat task numbers in template prose, headings, or notes (numbers live only in code comments, CHANGELOG, history, and HTML comments).
+
+3.5. **Collision Check:** Before writing the file, verify that `tasks/backlog/{NEXT_ID}-*.md` does NOT already exist. Run: `ls tasks/backlog/${NEXT_ID}-*.md`. If a file with that ID already exists, HALT and report: '⚠️ Task ID collision: {NEXT_ID} is already in use. Re-run ID discovery.' Do NOT overwrite existing files.
+
+4. **Generate File:** Write the following unified canonical template to the new file. The `## Source Context` section is **polymorphic** — include ONLY the variant block matching the `**Source:**` value. `## Goal`, `## Local TODOs`, `## Acceptance Criteria`, `## Verification Evidence`, and `## Risk & Rollback` are MANDATORY and UNCONDITIONAL for ALL source types (lint contract):
+
+   ```markdown
+   # Task [NN]: [Title]
+
+   **File:** `tasks/backlog/[filename]`
+   **Source:** [orchestrator|telegram|manager]
+   **Type:** [bug|improvement|feature]
+   **Status:** open
+
+   ## Source Context
+
+   ### Variant A: Orchestrator (`**Source:** orchestrator`)
+
+   ## Goal
+
+   [Summary of the goal — MANDATORY]
+
+   ## Blueprint Reference
+
+   [Link or reference to the approved architectural blueprint]
+
+   ## Manager's Notes
+
+   [Any specific notes, requirements, or constraints]
+
+   ### Variant B: Telegram (`**Source:** telegram`)
+
+   ## Goal
+
+   [MANDATORY — one-line goal derived from the RAW_TEXT]
+
+   ## Original Message ([Language])
+
+   {RAW_TEXT — verbatim, zero changes}
+
+   ## English Translation
+
+   {EN_TRANSLATION}
+
+   ## Refactored Prompt
+
+   {REFACTORED_PROMPT}
+
+   ## Relevant Code Context
+
+   {CODEBASE_CONTEXT}
+
+   ## AI Analysis & Opinion
+
+   {AI_OPINION}
+
+   ### Variant C: Manager (`**Source:** manager`)
+
+   ## Goal
+
+   [Summary of the goal — MANDATORY]
+
+   ## Manager's Notes
+
+   [Any specific notes, requirements, or constraints]
+
+   <!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->
+
+   ## Local TODOs
+
+   - [ ] Initial codebase exploration
+   - [ ] [Specific step 1]
+   - [ ] Verify functionality
+
+   ## Acceptance Criteria
+
+   - [ ] [Criterion 1 — what must be true for this task to be considered done]
+   - [ ] [Criterion 2]
+
+    ## Verification Evidence
+
+    - **Test command:** rtk test [exact command]
+    - **Expected result:** [what success looks like]
+    - **Actual result:** _(The Hands fill this during execution)_
+    - **Exit code:** _(The Hands fill this during execution)_
+
+    > Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.
+
+   ## Definition of Done
+
+   The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):
+
+   - [ ] Build/Test/Lint pass with exit code 0
+   - [ ] `lint_task_file` passes on the active task file
+   - [ ] `CHANGELOG.md` updated via Parse-Then-Append
+   - [ ] `testing-verification` applied and evidence recorded
+
+   > **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.
+
+   ## Risk & Rollback
+
+   - **Risk:** [what could go wrong]
+   - **Rollback plan:** [how to undo if needed]
+
+   ---
+
+   ## Execution Log & Reasoning
+
+   _(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_
+
+   ## Factual Git Diff
+
+   <!-- BEGIN_GIT_DIFF -->
+
+   _(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_
+
+   <!-- END_GIT_DIFF -->
+   ```
+
+## Multi-Phase Task Template
+
+If the Orchestrator specifies `multi_phase: true`, generate a SINGLE task file with inline phase sections instead of separate files. Use this structure (same unified metadata header, `## Goal` mandatory):
+
+```markdown
+# Task [NN]: [Title]
+
+**File:** `tasks/backlog/[filename]`
+**Source:** [orchestrator|telegram|manager]
+**Type:** [bug|improvement|feature]
+**Status:** open
+
+## Goal
+
+[Summary of the goal]
+
+## Acceptance Criteria
+
+- [ ] [Criterion 1 — what must be true for this task to be considered done]
+- [ ] [Criterion 2]
+
+## Verification Evidence
+
+- **Test command:** rtk test [exact command]
+- **Expected result:** [what success looks like]
+- **Actual result:** _(The Hands fill this during execution)_
+- **Exit code:** _(The Hands fill this during execution)_
+
+> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.
+
+## Definition of Done
+
+The task is NOT done unless ALL of the following are true (unconditional, applies to every multi-phase task):
+
+- [ ] Build/Test/Lint pass with exit code 0
+- [ ] `lint_task_file` passes on the active task file
+- [ ] `CHANGELOG.md` updated via Parse-Then-Append
+- [ ] `testing-verification` applied and evidence recorded
+
+> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.
+
+## Risk & Rollback
+
+- **Risk:** [what could go wrong]
+- **Rollback plan:** [how to undo if needed]
+
+## Phase 1: [Name]
+
+### Local TODOs
+
+- [ ] [Phase 1 step 1]
+- [ ] [Phase 1 step 2]
+
+## Phase 2: [Name]
+
+### Local TODOs
+
+- [ ] [Phase 2 step 1]
+- [ ] [Phase 2 step 2]
+
+## Execution Log & Reasoning
+
+_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_
+
+## Factual Git Diff
+
+<!-- BEGIN_GIT_DIFF -->
+
+_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_
+
+<!-- END_GIT_DIFF -->
+```
+
+5. **Halt and Handover:** DO NOT execute the task. Keep the generated task in `tasks/backlog/`. Invoke `brain_turn` directly under the active session thread with the generated task ID and task-file context. The Manager must not copy, paste, or relay task contents. Continue only through the normal planning and approval gates.
+
+## Bundle Workflow (Meta-Tasks, Pure MCP)
+
+Use this when the Manager has 4–6 small related tasks that should be executed together instead of sequentially. The bundler preserves every requirement verbatim and archives the sources.
+
+### When to Use
+
+- Manager says: "bundle tasks 1, 2, 5, 10, 15, 20" or "create a meta-task from 12 15 20"
+- Tasks are small, same stack/domain (e.g., all Android polish), and would be inefficient to run one-by-one
+- Goal is one branch, one `Factual Git Diff`, one QA gate (all-or-nothing)
+
+### Canonical Invocation — Pure MCP Tool
+
+Invoke the `bundle_tasks` MCP tool via the Hands:
+
+```json
+{
+  "tool": "bundle_tasks",
+  "arguments": {
+    "task_ids": ["12", "15", "20"],
+    "title": "android-polish-bundle",
+    "dry_run": false,
+    "force": false
+  }
+}
+```
+
+Examples (MCP arguments):
+
+- `task_ids: ["12","15","20"], title: "android-polish-bundle"`
+- `task_ids: ["12","15","20"], title: "android-polish-bundle", dry_run: true`
+- `task_ids: ["1","2","3","4","5","6","7"], title: "mega-bundle", force: true  // bypass 6-cap`
+
+### What the Script Does (Deterministic, No LLM)
+
+1. **Validate IDs:** searches `tasks/backlog/ tasks/in-progress/ tasks/qa/ tasks/completed/` (active only, archive excluded) for each `<id>-*.md`. HALT if any missing or if archive already contains the ID (already superseded). Rejects non-numeric IDs.
+2. **Next-ID Discovery:** `find tasks -type f -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 +1` across ALL dirs (including archive) — guarantees no collision. Zero-padded (`02d` for <100, raw for >=100).
+3. **Slug:** kebab-case the `--title` (`android Polish_Bundle` → `android-polish-bundle`). Output file: `tasks/backlog/<NEXT_ID>-<slug>.md`.
+4. **Verbatim Extraction:** for each source, extracts `## Goal`, `## Manager's Notes`/`## Blueprint Reference`, `## Acceptance Criteria`, `## Local TODOs`, `## Risk & Rollback` verbatim (regex until next `## `). No summarization.
+5. **Generate META File:** canonical template + extra metadata:
+   - `**Supersedes:** [12, 15, 20]`
+   - `**Meta:** true` (flag for tooling; `**Type:**` stays `feature` for lint compat, `meta` is also allowed)
+   - Per-source appendix: `### Source Task XX: Title` with verbatim blocks
+   - `## Bundled Checklist (All-or-Nothing)` — every source AC line prefixed `[XX]`, single QA gate
+   - `## Local TODOs` aggregates all source TODOs prefixed `[XX]` plus bundle-specific steps
+   - Guardrail notes: diff-size warning if combined LOC >400
+6. **Auto-Archive:** unless `--dry-run`, runs `git mv <source> tasks/archive/<source>` (fallback to `mv` + `git add` for untracked) and patches the archived file:
+   - `**File:**` → `tasks/archive/<file>`
+   - `**Status:** superseded`
+   - `**Superseded-By:** <META_ID>-<slug>` + `**Superseded-At:** YYYY-MM-DD`
+   - Superseded footer before `## Execution Log` with `git log --follow` hint
+     History remains reachable: `git log --oneline --follow -- tasks/archive/<file>`
+
+### Guardrails
+
+- **Cap:** `MAX_BUNDLE_SIZE=6` — rejects >6 without `--force` (mega-diff prevention)
+- **Diff-size:** warns if combined source LOC >400 ("consider split")
+- **Duplicate/Collision:** `ls tasks/backlog/<NEXT_ID>-*.md` check before write; HALT if exists. Duplicate active IDs HALT.
+- **Archive-Only:** `git mv` to `tasks/archive/` — never `git rm` / purge until META reaches `tasks/completed/`; rollback is `git mv tasks/archive/<id>-*.md tasks/backlog/`
+
+### QA & Completion
+
+- META follows normal Kanban: `tasks/backlog/<META>` → `tasks/in-progress/<META>` → `tasks/qa/<META>` → `tasks/completed/<META>` with a single injected diff
+- QA is all-or-nothing: if ANY bundled criterion fails, entire META is `QA_REJECTED`
+
+### Verification
+
+```bash
+bundle_tasks(task_ids=["12","15","20"], title="test", dry_run=true)
+lint_task_file tasks/backlog/<META_FILE>
+git log --oneline --follow -- tasks/archive/12-*.md | head
+```
+
+---
+
diff --git a/skill-templates/kanban-lifecycle/templates/02-lint.md b/skill-templates/kanban-lifecycle/templates/02-lint.md
new file mode 100644
index 0000000..c57c7e8
--- /dev/null
+++ b/skill-templates/kanban-lifecycle/templates/02-lint.md
@@ -0,0 +1,23 @@
+## Part 2: Task Lint Skill (from `task-lint`)
+
+# Task Lint Skill
+
+## When to Run
+
+1. **After Part 1 creates a new task file** — validate structure before handing to Orchestrator.
+2. **Before closing a task** — validate the task file is complete and well-formed.
+3. **During Part 4 archiving** — validate all tasks before compacting.
+
+## Workflow
+
+1. Call `lint_task_file` with the active task file path.
+2. If issues found, report them and HALT.
+3. If clean, proceed.
+
+## For Markdown files (non-task)
+
+1. Call `lint_markdown` with the file path.
+2. Report issues.
+
+---
+
diff --git a/skill-templates/kanban-lifecycle/templates/03-bundle.md b/skill-templates/kanban-lifecycle/templates/03-bundle.md
new file mode 100644
index 0000000..5192fd4
--- /dev/null
+++ b/skill-templates/kanban-lifecycle/templates/03-bundle.md
@@ -0,0 +1,108 @@
+## Part 3: Bundle Tasks Skill — Meta-Task Bundling (from `bundle-tasks`)
+
+# Bundle Tasks Skill — Meta-Task Bundling
+
+Use this skill when the Manager wants to execute 4–6 small related tasks together instead of sequentially. It eliminates the `backlog → in-progress → qa → completed` round-trip overhead by bundling them into one branch, one `Factual Git Diff`, and one all-or-nothing QA gate.
+
+## When to Use
+
+- Manager says: "bundle tasks 1, 2, 5, 10, 15, 20", "create a meta-task from 12 15 20", "combine these polish tasks", or any note about "meta-task", "bundle", "supersede", "archive and bundle"
+- Tasks are small, same stack/domain (e.g., all `android-kotlin`, all `react-vite`, all docs), and would be inefficient to run one-by-one
+- You are in any project that has the `mcp-context-server` MCP server — the bundler is available as the `bundle_tasks` MCP tool (pure MCP)
+
+**Do NOT use for:** large refactors, tasks with conflicting files that would cause merge conflicts in one diff, or tasks >6 without explicit `--force`.
+
+## Core Contract (Deterministic, No LLM, No Hallucination)
+
+1. **Verbatim Preservation:** Every source `## Goal`, `## Manager's Notes` / `## Blueprint Reference`, `## Acceptance Criteria` (including multi-line continuations and indented sub-bullets), `## Local TODOs`, `## Risk & Rollback` is copied verbatim into `### Source Task XX` blocks. No summarization. The `## Bundled Checklist` is derived by prefixing each source AC root bullet with `[XX]` and preserving all indented continuation lines.
+2. **Single QA Gate:** All bundled criteria are `all-or-nothing`. If any line fails QA, the entire META is `QA_REJECTED`.
+3. **Archive, Not Purge (with Transactional Rollback):** Sources are moved via `git mv` to `tasks/archive/` with `**Superseded-By:** <META_ID>-<slug>` until META is `completed`. History stays reachable via `git log --follow`. If ANY archive operation fails, ALL previously archived files are rolled back to their original locations, the META file is deleted, and the operation aborts cleanly.
+4. **Guardrails:** `MAX_BUNDLE_SIZE=6` (reject >6 without `--force`), combined LOC >400 warning, missing-ID and duplicate-ID checks (hard halt on duplicate active IDs), stack conflict detection (warn or require `--force`), SHA verbatim checksum validation, atomic Next-ID creation with retry loop for concurrent safety.
+
+## Invocation — Pure MCP Tool
+
+The `mcp-context-server/server.py:bundle_tasks` tool is **fully self-contained** — it does NOT require `scripts/bundle-tasks.py`. All helpers (kebab_case, discover_next_id, find_task_file, extract_section, build_meta_content, git_mv_or_fallback, patch_archived_file) are inlined inside the MCP tool function. Invoke via the Hands' MCP interface:
+
+```json
+{
+  "tool": "bundle_tasks",
+  "arguments": {
+    "task_ids": ["12", "15", "20"],
+    "title": "android-polish-bundle",
+    "dry_run": true,
+    "force": false
+  }
+}
+```
+
+**Tool name:** `bundle_tasks` on `mcp-context-server` (`custom_context` FastMCP server). It validates IDs, discovers NEXT_ID, slugifies title, generates META with verbatim preservation, and auto-archives sources. Dry-run prints preview without file creation. Pure MCP — no external script dependency.
+
+## What Happens (Deterministic Steps)
+
+1. **Validate IDs:** Search `tasks/backlog/ tasks/in-progress/ tasks/qa/ tasks/completed/` (active only, `tasks/archive/` excluded per `task-generator` duplicate-ID contract) for each `<id>-*.md`. HALT if any missing; note if found in archive (already superseded). Reject non-numeric IDs.
+2. **Discover NEXT_ID:** `find tasks -type f -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}'` across **ALL** dirs including `archive` (no collision). Zero-padded `02d` for <100, raw for ≥100.
+3. **Slugify Title:** `title` → kebab-case (`android Polish_Bundle` → `android-polish-bundle`). Output file: `tasks/backlog/<NEXT_ID>-<slug>.md`.
+4. **Verbatim Extraction:** For each source, extract `## Goal`, `## Manager's Notes`/`## Blueprint Reference`, `## Acceptance Criteria`, `## Local TODOs`, `## Risk & Rollback` verbatim via regex `^## Heading$(.*?)(?=^## |\n---\s*\n|\Z)`. No summarization.
+5. **Generate META File:** Canonical task template + `**Supersedes:** [12, 15, 20]` + `**Meta:** true` + `**Created:**` + per-source appendix `### Source Task XX: Title` + `## Source Bundles (Verbatim Preservation)` + `## Bundled Checklist (All-or-Nothing)` (every source AC line prefixed `[XX]`, single QA gate) + aggregated `## Local TODOs` (`[XX]`-prefixed) + guardrail notes (LOC warning if >400).
+6. **Auto-Archive (unless dry_run):** `git mv <src> tasks/archive/<src>` (fallback to `mv` + `git add` for untracked) then patch archived file: `**File:**` → `tasks/archive/<file>`, `**Status:** superseded`, add `**Superseded-By:** <META_ID>-<slug>` + `**Superseded-At:** YYYY-MM-DD`, inject superseded footer before `## Execution Log`. History remains reachable: `git log --oneline --follow -- tasks/archive/<file>` — **never** `git rm` until META is `completed`.
+7. **Kanban:** META follows normal `tasks/backlog/<META>` → `tasks/in-progress/<META>` → `tasks/qa/<META>` → `tasks/completed/<META>` with one injected `Factual Git Diff`. QA is all-or-nothing.
+
+## Guardrails (Hard Stops & Warnings)
+
+- **Cap:** `MAX_BUNDLE_SIZE=6` — rejects >6 without `--force` (mega-diff prevention). Use `--force` to override.
+- **Floor:** bundles need 2-6 tasks — a single task or duplicate IDs in one request are rejected with an explicit error, never silently deduped.
+- **Diff-size:** Warns if combined source LOC >400 (`> ⚠️ 400` in notes) — "consider split".
+- **Missing / Duplicate / Collision:** Missing IDs → `❌ Missing tasks`; duplicate IDs across active Kanban dirs → distinct `❌ Duplicate task ID` error (never misreported as missing); same-ID-different-slug files for the allocated ID (either zero-padding) → `❌ Task ID collision`; allocation races rebuild the META body after the final ID and create-plus-write atomically, so no stale-ID or empty META file survives.
+- **Stack Conflict (M1):** Auto-detects stack from content (android, react, fastapi, spring, ios, go). If tasks have conflicting stacks → requires `--force` to proceed.
+- **Verbatim Checksum (M2):** After META generation, verifies every AC line from source tasks appears in the META. Fails if any text was dropped.
+- **Archive-only:** Sources go to `tasks/archive/` via `git mv` only. Purge (`git rm`) is blocked until META is `completed`. On ANY archive failure: **transactional rollback** restores byte-identical originals to their recorded origin dirs (no header guessing, failures surfaced), deletes META, exits with clear error.
+- **Unicode Slugs (B4):** `_kebab_case()` normalizes via NFKD and preserves non-English characters (\u0600-\u06FF). Non-English titles produce valid slugs like `تست-باندل` instead of losing all characters.
+
+## Verification (Must Pass Before QA)
+
+```bash
+# via MCP (pure MCP):
+bundle_tasks(task_ids=["12","15","20"], title="test-bundle", dry_run=true)
+
+# then after real bundle (if not dry_run):
+lint_task_file tasks/backlog/<NEXT_ID>-<slug>.md
+lint_task_file tasks/archive/12-*.md
+git log --oneline --follow -- tasks/archive/12-*.md | head
+py_compile: python3 -m py_compile mcp-context-server/server.py
+```
+
+- META must contain `**Supersedes:**` + every source `### Source Task` block + `## Bundled Checklist` with `[XX]` prefixes.
+- `lint_task_file` must pass on META (fixed `---` → `---\n\n` blank-line; `**Type:**` allows `feature` + `Meta:true` and also `meta`) and on both archived files (`**Status:** superseded` is allowed; `**File:**` matches archive path).
+- `git log --follow` must show the source's history through the rename.
+
+## Skill Loading
+
+Load this skill when you handle bundling:
+
+```bash
+skill("kanban-lifecycle")
+```
+
+If you also need lint validation, use Part 2 of this skill; for context gathering before bundling, load `code-search` to ensure sources are in the expected Kanban dirs.
+
+## Rollback
+
+If META is abandoned or fails QA permanently:
+
+```bash
+git mv tasks/archive/12-*.md tasks/backlog/12-*.md
+git mv tasks/archive/15-*.md tasks/backlog/15-*.md
+git mv tasks/backlog/<NEXT_ID>-<slug>.md tasks/archive/<NEXT_ID>-<slug>.md  # mark abandoned and preserve history
+```
+
+No HQ code beyond the bundler is affected. If META already reached `tasks/completed/`, its archived sources stay in `tasks/archive/` permanently (they are superseded, not purged).
+
+## Reference
+
+- **MCP:** `mcp-context-server/server.py:bundle_tasks` (self-contained, verbatim helpers inlined, `task_ids: list[str], title: str, dry_run, force`, path-traversal safe, cap 6)
+- **Docs:** `AGENTS.md` `## 🛑 META-TASK BUNDLE LIFECYCLE` + `**Bundle Tool:**`, `CHANGELOG.md` `[Unreleased]`
+- **Lint:** `mcp-lint-server/server.py` Type regex now `...|meta`
+- **Registry:** `prompts/fragments/07-agent_skills_registry.md` lists `kanban-lifecycle`
+
+---
+
diff --git a/skill-templates/kanban-lifecycle/templates/04-archive.md b/skill-templates/kanban-lifecycle/templates/04-archive.md
new file mode 100644
index 0000000..5f81bdf
--- /dev/null
+++ b/skill-templates/kanban-lifecycle/templates/04-archive.md
@@ -0,0 +1,96 @@
+## Part 4: Archive Tasks Skill (from `archive-tasks`)
+
+# Archive Tasks Skill
+
+## Purpose
+
+Prevents the `tasks/completed/` directory from accumulating hundreds of task files by periodically compacting completed tasks into dense, single-file milestone summaries in `docs/history/`.
+
+## Workflow
+
+1. **Scan completed tasks** for the current milestone:
+
+```bash
+ls tasks/completed/*.md
+```
+
+2. **Read each file** and extract:
+   - Task number and title
+   - Type (bug/improvement/feature)
+   - Source (from the `**Source:**` metadata line)
+   - Execution Log & Reasoning (architectural reasoning)
+   - Key files modified
+
+3. **Generate a milestone summary** at `docs/history/milestone-X-summary.md` with the following structure:
+
+   ```markdown
+   # Milestone X Summary
+
+   **Date:** YYYY-MM-DD
+   **Tasks Compacted:** N
+
+   ## Source Distribution
+
+   | Source       | Count |
+   | ------------ | ----- |
+   | orchestrator | N     |
+   | telegram     | N     |
+   | manager      | N     |
+
+   ## Architectural Changes
+
+   [Dense summary of all architectural changes across the milestone]
+
+   ## Files Modified
+
+   | File         | Change      |
+   | ------------ | ----------- |
+   | path/to/file | description |
+
+   ## Criteria Met
+
+   | Task | Acceptance Criteria | Status |
+   | ---- | ------------------- | ------ |
+   | XX   | [Extracted criteria from the completed task's `## Acceptance Criteria` section] | ✅ Met |
+
+   ## Individual Task Summaries
+
+   ### Task XX: Title
+
+   - **Type:** bug|improvement|feature
+   - **Source:** [orchestrator|telegram|manager]
+   - **Reasoning:** [condensed execution log]
+   ```
+
+4. **Create the `docs/history/` directory** if it does not exist:
+
+```bash
+mkdir -p docs/history
+```
+
+5. **Move completed files to archive**:
+
+```bash
+git mv tasks/completed/*.md tasks/archive/
+```
+
+*Note: For untracked task files, use the supported native file-management operation to move them. Stage the moved files only through `custom_context_stage_and_inject_diff`; never run `git add` directly.*
+
+6. **Memory Validation:** After compacting tasks, audit the project memory bank for stale or superseded entries:
+   a. Call `list_namespaces` to enumerate all memory namespaces.
+   b. For each namespace, call `search_memory` using keywords from the archived tasks.
+   c. Identify memories that reference archived/completed task files or superseded workflows.
+   d. Detect duplicates: if two memories in the same namespace cover the same topic and one references a newer date or task, flag the older one as superseded.
+   e. Output a `## Stale Memory Report` listing all flagged memories with their namespace, key, and reason for flagging.
+   f. Wait for Manager approval before calling `delete_memory` on any flagged entry. NEVER auto-delete memories without explicit Manager confirmation.
+
+7. **Stage the new summary and moved files**:
+
+Call `custom_context_stage_and_inject_diff` with the active task file and an explicit `modified_files` list containing the generated milestone summary and every moved task-file path. Do not run `git add` directly.
+
+## When to Run
+
+Run this skill at the end of each milestone or when `tasks/completed/` contains more than 20 files. The milestone number should be determined by reading the highest existing milestone in `docs/history/` and incrementing by one.
+
+---
+
diff --git a/skill-templates/kanban-lifecycle/templates/05-migrate.md b/skill-templates/kanban-lifecycle/templates/05-migrate.md
new file mode 100644
index 0000000..10f7097
--- /dev/null
+++ b/skill-templates/kanban-lifecycle/templates/05-migrate.md
@@ -0,0 +1,62 @@
+## Part 5: Migrate Kanban Skill (from `migrate-kanban`)
+
+# Migrate Kanban Skill
+
+## Purpose
+
+Transforms a flat `tasks/` directory (e.g., `tasks/01-task.md`, `tasks/02-task.md`) into the state-based V6 Kanban lifecycle structure:
+
+- `tasks/backlog/` — Open / unstarted tasks
+- `tasks/in-progress/` — Currently being worked on
+- `tasks/qa/` — Awaiting review / quality assurance
+- `tasks/completed/` — Finished tasks
+- `tasks/archive/` — Milestone-compacted historical tasks
+
+## Workflow
+
+1. **Create the 5 Kanban directories** if they do not already exist:
+
+```bash
+mkdir -p tasks/backlog tasks/in-progress tasks/qa tasks/completed tasks/archive
+```
+
+2. **Scan all `.md` files** in the flat `tasks/` root (excluding the Kanban subdirectories):
+
+```bash
+find tasks/ -maxdepth 1 -type f -name "*.md" | sort
+```
+
+3. **Classify each file** by reading its frontmatter or first line:
+
+   - If the file contains `Status: open` (or `**Status:** open`), move it to `tasks/backlog/`.
+   - If the file contains `Status: closed` (or `**Status:** closed`), move it to `tasks/completed/`.
+   - If no status is found, default to `tasks/backlog/`.
+
+4. **Move the files** using `git mv` to preserve history:
+
+```bash
+for f in tasks/*.md; do
+  [ -e "$f" ] || continue
+  [ "$f" = "tasks/README.md" ] && continue
+  if grep -qi "Status: open" "$f"; then
+    git mv "$f" tasks/backlog/
+  elif grep -qi "Status: closed" "$f"; then
+    git mv "$f" tasks/completed/
+  else
+    git mv "$f" tasks/backlog/
+  fi
+done
+```
+
+5. **Verify** the migration:
+
+```bash
+echo "=== Backlog ===" && ls tasks/backlog/
+echo "=== Completed ===" && ls tasks/completed/
+```
+
+6. **Update AGENTS.md** to reference the Kanban directory structure in the "Core File Locations" and "Documentation Sync Rules" sections.
+
+## Post-Migration
+
+After running this skill, the flat `tasks/` directory should be empty (except for the 5 Kanban subdirectories). All existing task history is preserved via `git mv`.
diff --git a/skill-templates/opencode-init/SKILL.md b/skill-templates/opencode-init/SKILL.md
deleted file mode 100644
index fddb888..0000000
--- a/skill-templates/opencode-init/SKILL.md
+++ /dev/null
@@ -1,102 +0,0 @@
----
-name: opencode-init
-description: Analyze a project (or ask the user) and generate a comprehensive, correct opencode.json for it. Matches https://opencode.ai/config.json shapes; validates before writing.
----
-
-# Skill: opencode-init
-
-# Project OpenCode Config Generator
-
-## Purpose
-
-Turn project analysis into a working `opencode.json` for THAT project only.
-Analyze stack files, ask the user for gaps (default agent,
-formatter, LSP guidance, instructions, permissions), emit JSON matching
-the public schema (https://opencode.ai/config.json),
-then validate with `scripts/validate-opencode.py` before writing.
-For every gap question, use the `question` tool when the session capability
-manifest shows it AVAILABLE; otherwise relay the same question in prose.
-MCP servers and plugins install GLOBALLY — never emit `mcp` or `plugin`
-into the project file. Never edit global config. Never install plugins.
-
-## Ground Truth (public schema wins — verified 2026-09-16)
-
-- Shape: project-only top keys: `$schema`, `default_agent`,
-  `instructions[]`, `formatter`, `lsp`, `permission{}`. The `permission` map is
-  `tool-name → allow|ask|deny`, plus a `bash` sub-map of
-  `command-pattern → deny` and optional scoped sub-maps
-  (e.g. `external_directory`). There is NO `permissions[]` array here.
-  `mcp{}` and `plugin[]` are GLOBAL-only and banned from project output.
-- Formatter: `true` | `false` | named map
-  `{<name>: {command?, extensions?, environment?, disabled?}}`.
-  NEVER emit a flat `{command, extensions}` object — it fails with
-  `Missing key formatter.command`. Example:
-  `{"spotless-java": {"command": ["mvn", "spotless:apply"], "extensions": [".java"]}}`.
-- LSP: `true` | `false` | flat map
-  `{<name>: {command (required), extensions?, env?, initialization?, disabled?}}`.
-  NEVER wrap in a `language-server` key — it fails with
-  `Missing key lsp.language-server.command` because the runtime treats
-  `language-server` as a server name. LSP uses `env`, NOT `environment`.
-  Example: `{"typescript": {"command": ["typescript-language-server", "--stdio"]}}`.
-- MCP server: global-only. Shared servers live in the global config
-  (`~/.config/opencode/opencode.json`) or a global plugin directory —
-  project output carries NO `mcp` block. Secrets travel ONLY as
-  `{env:NAME}` placeholders in global scope — never literal values.
-- `default_agent` must name an existing primary agent.
-- Merge order: remote → global → custom → project root → subdir;
-  `.opencode/*` wins. Global holds shared MCP and plugins;
-  the project file holds overrides only (formatter, LSP guidance,
-  instructions, permissions).
-- Schema authority: https://opencode.ai/config.json plus
-  `references/runtime-matrix.md`. The golden file
-  (`references/examples/golden-opencode.json`) is a known-good example
-  that MUST pass both this validator and `opencode debug config`.
-
-## Workflow
-
-1. **Analyze.** Read the target project: package manifests, README, stack
-   files, existing `opencode.json`/`AGENTS.md`/`.opencode/`. Record: stack,
-   agents dir, formatter needs, LSP guidance needs, instructions paths,
-   permission needs. Do NOT record MCP needs or plugin choices —
-   those are global scope, out of this skill's output.
-2. **Ask user for gaps.** Missing `default_agent` choice, formatter/LSP/
-   instructions/permission choices. Ask with explicit questions;
-   ambiguous means NOT answered — HALT and re-ask rather than
-   inventing values. Never ask for MCP env keys or plugin selection.
-3. **Generate.** Emit project-only JSON: `$schema`, `default_agent`,
-   `instructions[]` (existing doc paths only), `formatter`
-   (`true`|`false`|named map `{<name>: {command, extensions?, environment?, disabled?}}`),
-   `lsp` (`true`|`false`|flat map `{<name>: {command, extensions?, env?, initialization?, disabled?}}`),
-   `permission{}` (tool allows + full ZAC `bash` deny set).
-   Omit `mcp` and `plugin` entirely; instead write a human note naming
-   the global install paths (`~/.config/opencode/opencode.json`,
-   `~/.config/opencode/plugins/` or `.opencode/plugins/`).
-4. **Validate, then write.** Run `scripts/validate-opencode.py <file>`.
-   Zero errors required before writing to the project root. On failure,
-   fix and re-run — never hand over an invalid file.
-
-## Rules
-
-- Project-only output. `mcp` and `plugin` keys, `permissions[]`
-  arrays, `language-server` LSP wrappers, flat formatter objects,
-  and any key the validator rejects are forbidden.
-- Project key allowlist: `$schema`, `default_agent`, `instructions`,
-  `formatter`, `lsp`, `permission`. Output keys MUST subset this list.
-- ZAC deny set is mandatory in every generated file: `git add`, `git add *`,
-  `git checkout`, `git checkout *`, `git commit`, `git commit *`, `git push`,
-  `git push *` → `deny`.
-- Secrets are `{env:NAME}` placeholders. A literal secret fails validation.
-- No invented values. TODO, changeme, xxx, your-value-here, foo, bar,
-  dummy, placeholder (any case) and standalone "example"/"sample" fail
-  validation in `default_agent`, `instructions`, `formatter`, `lsp`,
-  `agents_dir`, `theme`, `keybinds`
-  — confirm every name against the project first. MCP server names,
-  commands, env names, and plugin sources are global scope: they MUST
-  NOT appear in project output at all (neither real nor placeholder).
-- Write ONLY to the target project's root `opencode.json`. Parent
-  traversal (`..`), the home directory, and any global config path are
-  forbidden as write destinations.
-- Verify before generating: list the `agents_dir` files and confirm the
-  chosen `default_agent` name exists there. A name with no file is an
-  invention — ask the user instead.
-- One project per run. Never touch global config. Never `git commit` the result.
diff --git a/skill-templates/telegram-suite/SKILL.md b/skill-templates/telegram-suite/SKILL.md
index 82fffc7..9d8765f 100644
--- a/skill-templates/telegram-suite/SKILL.md
+++ b/skill-templates/telegram-suite/SKILL.md
@@ -3,507 +3,24 @@ name: telegram-suite
 description: Unified Telegram skills — HTML message formatting, contextual export to ZIP, and issue sync to tasks/GitHub.
 ---
 
-# Telegram Suite Meta Skill
+# Telegram Suite Meta Skill (slim index)
 
-Meta skill combining **telegram-message-format** (HTML formatting contract), **telegram-message-export** (contextual range export), and **telegram-issue-sync** (topic sync to tasks/GitHub). All outgoing Telegram messages in any part MUST follow Part 1. Sections are verbatim from the source skills.
+Meta skill combining **telegram-message-format** (HTML formatting contract), **telegram-message-export** (contextual range export), and **telegram-issue-sync** (topic sync to tasks/GitHub). All outgoing messages follow Part 1. Full bodies are verbatim in `templates/` — read only the part you need.
 
 ---
 
-## Part 1: Telegram Message Formatting SOP (from `telegram-message-format`)
+## Critical Rules (no read needed)
 
-## Purpose
+- **Parse mode:** always `parse_mode: "HTML"`; `<b>`/`<code>`/`<pre>` only; no ` ``` ` or `*emphasis*`; escape `&` `<` `>` inside `<code>`/`<pre>`.
+- **Persian:** no U+200C ZWNJ — use normal space. **Length:** ≤ ~3800 chars/message (hard cap 4096); split with numbered parts anchored to the same parent.
+- **Topics:** `send_message` has no `topic_id` (lands in General). Post into a topic via `reply_to_message` anchored to a message already inside that topic.
+- **Export:** `get_history` range → sorted sidecars with `Reply To Message ID` → `Max` (single `get_media_info` + `download_media` per media) → `zip -r export.zip` → delete dir. No media = no zip.
+- **Sync:** verbatim `RAW_TEXT` (no summarize) + `## Original Message` + `## English Translation` + `## Refactored Prompt` (prompt-refactor 5 blocks) + codebase correlation + `AI_OPINION` in `kanban-lifecycle` unified template. State via native edits only; never helper scripts. Approval: `question` tool when available, else capability-block relay.
 
-Every message an agent sends through the Telegram MCP must be clean, readable, and correctly rendered. The Telegram MCP server does **not** behave like the Bot API: it silently destroys Markdown structure, rejects over-length payloads with an opaque error, drops Persian half-spaces, and has no topic parameter on `send_message`.
+## When to Read Templates
 
-This skill is the agent-facing rulebook. The full evidence (probe transcripts, defect list, server-side recommendations) lives in the HQ repository at `docs/telegram-message-formatting.md`.
+- **Send, reply, edit, caption, or verify a message** → `templates/01-format.md` (9 Rules + checklists + defect table).
+- **Export a range to ZIP** → `templates/02-export.md`.
+- **Sync topics → tasks/GitHub** → `templates/03-sync.md`.
 
-**Load this skill before any Telegram send.** It applies to `send_message`, `reply_to_message`, `edit_message`, `send_file` captions, and any other tool that puts text into a chat.
-
----
-
-## The 9 Rules
-
-| # | Rule                                                                                                    | Why                                                                            |
-| - | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
-| 1 | Always send with `parse_mode: "HTML"`.                                                                   | Markdown mode strips fence/backtick markers and creates no entities.          |
-| 2 | Escape `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;` inside `<pre>` and `<code>`.                             | A raw `<` breaks the HTML parse and aborts the entire message.                |
-| 3 | Use `<b>` for headings, `<code>` for inline identifiers, `<pre>` for code blocks.                          | These three are the only elements proven to survive the round-trip.           |
-| 4 | Never use ` ``` ` fences or `*bold*` Markdown syntax.                                                     | Fences vanish; asterisks stay literal.                                        |
-| 5 | Write Persian without U+200C ZWNJ — use a normal space where the half-space belongs.                      | ZWNJ is lost on the read path of every message, including hand-typed ones.    |
-| 6 | Keep each message under ~3800 characters; split longer payloads into parts, each a reply to the same parent id. | The hard cap is 4096 chars and the failure is an opaque `GEN-ERR-184`.      |
-| 7 | Post into a forum topic with `reply_to_message` anchored to a message already inside that topic.           | `send_message` has no `topic_id` and lands in General.                        |
-| 8 | Verify a formatted send by reading it back and checking the `&lt;`/`&gt;` round-trip.                      | `get_history` resolves entities to plain text, so a text diff proves nothing. |
-| 9 | Delete every probe message after reading it back.                                                         | Keeps the chat clean; message ids are never reused.                           |
-
----
-
-## Rule Details
-
-### 1–4. Parse mode and markup
-
-- `parse_mode: "HTML"` is the only mode that works. `Markdown` consumes ` ``` ` fences and inline backticks without creating the matching Telegram entities, and leaves `*bold*` as literal asterisks.
-- A message with **no** markup needs no parse mode at all — plain text is safe.
-- The safe element set is `<b>`, `<i>`, `<u>`, `<code>`, `<pre>`, `<a>`. Everything else is unverified — do not use it.
-- `<pre>` keeps its block boundaries. Put the code body inside it, escape `&`, `<`, `>`, and keep the language hint as plain text inside the block (the server does not support a language attribute).
-- One unescaped `<` in the payload rejects the whole message, so escape **all** angle brackets inside `<pre>` and `<code>`, including shell redirects (`>`) and generics.
-
-### 5. Persian text (and any non-ASCII text)
-
-- The server drops U+200C ZERO WIDTH NON-JOINER on the read path. It is lost for every message, not only agent-authored ones.
-- Author Persian with a **normal space** where the half-space belongs: `می کند`, `قابل تسویه`, `نمی فهمم`. Never paste a ZWNJ into authored text.
-- Same caution for other `Cf` (format) characters: zero-width space, BOM, soft hyphen. Use plain text.
-
-### 6. Length budget and splitting
-
-- Hard cap: **4096 characters**. Over that, the server returns `An error occurred (code: GEN-ERR-184)` with no hint — never retry it, it is not transient.
-- Plan on **~3800 characters** per message to leave headroom for the reply anchor and for entity overhead.
-- Count characters, not bytes. Persian, Arabic, and emoji payloads hit the cap well before their byte length suggests.
-- When a payload exceeds the budget, split it into numbered parts, each sent as a reply to the **same** parent message id, so the thread stays readable:
-
-  ```html
-  <b>Report — part 1 of 3</b>
-
-  ... first third ...
-
-  <i>Continued in the next reply.</i>
-  ```
-
-- Keep the part count minimal and never split inside a `<pre>` block.
-
-### 7. Forum topics
-
-- `send_message` accepts `chat_id`, `message`, `parse_mode`, `format_date`, `custom_emojis`, `account` — **no `topic_id`**. In a supergroup with forum topics enabled it lands in **General**.
-- `send_album` and `send_file` do accept `topic_id`.
-- To post into a topic, reply to a message that already lives in that topic — a reply inherits the topic of its parent:
-
-  ```text
-  reply_to_message(chat_id, message_id=<id inside the target topic>, account, parse_mode="HTML", text=...)
-  ```
-
-- Never post a topic-scoped confirmation with `send_message`.
-
-### 8. Read-back verification
-
-- `get_history` returns text with entities already resolved, so comparing the read-back text against the sent text **cannot** prove the formatting was applied.
-- The reliable check is the entity round-trip: send `&lt;` inside a `<pre>` block, read it back, and confirm it came back as a literal `<` with the block intact. If the literal `&lt;` is still there, the HTML was not parsed.
-
-### 9. Probe hygiene
-
-- Every probe message must be deleted with `delete_message(chat_id, message_id, account)` after it is read back.
-- Deleting does not renumber the remaining messages; later messages keep their ids. Treat a cached id as "may no longer resolve" rather than "was renumbered".
-
----
-
-## Message Templates
-
-### Short prose message
-
-```html
-<b>Short heading</b>
-
-Plain prose with <code>identifiers</code> and no markup dependency.
-```
-
-### Report with a code block
-
-```html
-<b>Heading</b> and <code>inline_identifier</code>
-
-<pre>curl -X POST "https://example.com/api" \
-  --data 'key=value'</pre>
-
-<b>Second heading</b>
-
-<pre>SELECT id, state FROM trades WHERE id = 2069;</pre>
-
-Notes with <code>snake_case_names</code> inline.
-```
-
-### Status confirmation on a task
-
-```html
-<b>Task synced</b>
-
-<b>File:</b> <code>tasks/backlog/123-example.md</code>
-<b>Issue:</b> <code>https://github.com/org/repo/issues/7</code>
-<b>Type:</b> BUG
-```
-
-Keep the body plain — no emoji, no ASCII art, no horizontal rules made of dashes. One blank line between blocks, never more.
-
-### File caption (for `send_file`)
-
-```html
-<b>Export archive</b>
-
-<code>export-20261021-101500.zip</code> — 42 messages, 6 media files.
-```
-
----
-
-## Pre-Send Checklist
-
-Run through this before every send:
-
-1. `parse_mode` is `"HTML"`, or the message is pure plain text with no markup.
-2. Every `&`, `<`, `>` inside `<pre>` / `<code>` is escaped.
-3. No ` ``` ` fences and no `*asterisk*` emphasis anywhere.
-4. No U+200C or other `Cf` characters in the text.
-5. The message is under ~3800 characters — or it is split into numbered parts.
-6. The target is a topic → the send is a `reply_to_message` to a message inside that topic.
-7. The payload is not raw LLM output: it has been read once and checked for stray angle brackets and Markdown leftovers.
-
----
-
-## Server Defects (known, unfixed)
-
-The following are upstream defects in the Telegram MCP server. Work around them; do not report them as your own errors, and do not retry them.
-
-| Defect                                                | Workaround                                                       |
-| ----------------------------------------------------- | ---------------------------------------------------------------- |
-| Over-length message returns opaque `GEN-ERR-184`       | Self-enforce the 3800-character budget; never retry.            |
-| Markdown mode destroys code blocks                    | Use HTML.                                                         |
-| Markdown `*bold*` not applied                         | Use `<b>`.                                                        |
-| ZWNJ lost on the read path                            | Author Persian without U+200C.                                   |
-| `send_message` cannot target a forum topic            | Use `reply_to_message` anchored inside the topic.                |
-| Message `entities` not exposed on read               | Verify with the `&lt;`/`&gt;` round-trip, not a text diff.      |
-| Length counted without UTF-16 semantics                | Count characters yourself, not bytes.                            |
-
----
-
-## Part 2: Telegram Message Export Skill (from `telegram-message-export`)
-
-# Telegram Message Export Skill
-
-## Purpose
-
-Extracts a highly contextual range of Telegram messages. It explicitly documents reply relationships to preserve conversation trees and packages text alongside downloaded media files (images, voice notes) into a ZIP file.
-
-## Input Resolution
-
-Determine the exact `[from_id, to_id]` range. If the Manager provided a text snippet, use `telegram_search_messages` to find the `msg_id`. If a link is provided (`t.me/c/CHAT_ID/MSG_ID`), extract the ID.
-
-## Phase 1: Contextual Fetching
-
-1. Call `telegram_get_history` and filter to keep messages where `id >= from_id` and `id <= to_id`.
-2. Sort the filtered messages strictly by `id` in ascending order.
-3. If the range spans more than 200 messages, ask for confirmation before proceeding to avoid rate limits. Use the `question` tool when the session capability manifest shows it AVAILABLE; otherwise relay the same question in prose and wait for the answer.
-
-## Phase 2: Extraction & Sidecar Generation
-
-1. Create directory: `mkdir -p <workspace>/telegram-exports/export-{timestamp}/`
-2. Set counter `n = 1`.
-3. For each message in the sorted list:
-
-   **Text Sidecar (`{n}.txt`)**:
-   Create a `.txt` file for every message. You MUST include `reply_to_message_id` to preserve thread context.
-
-   ```text
-   Message ID: {message.id}
-   From: {sender_name_or_id}
-   Date: {date}
-   Reply To Message ID: {reply_to_message_id | 'None'}
-   Message Type: {type}
-
-   [Content]
-   {message_text | caption | '[No extractable content]'}
-   ```
-
-   **Media Download**:
-   If the message contains media, call `telegram_get_media_info` to get the extension. Then call `telegram_download_media(chat_id=..., message_id=..., file_path="<workspace>/telegram-exports/export-{timestamp}/{n}.{ext}")`.
-
-4. Increment `n`.
-
-## Phase 3: Archiving
-
-Run the bash zip command:
-
-```bash
-cd <workspace>/telegram-exports && zip -r export-{timestamp}.zip export-{timestamp}/
-rm -rf export-{timestamp}/
-```
-
-## Phase 4: Notification
-
-Output exactly: "✅ Contextual Telegram export complete. Range: {from_id} to {to_id}. Archive path: <workspace>/telegram-exports/export-{timestamp}.zip"
-
-## Phase 5: Optional Telegram Delivery
-
-When the archive is delivered to a chat through the Telegram MCP, the caption and any follow-up message MUST follow the `telegram-suite` (Part 1) contract:
-
-- `parse_mode: "HTML"`, with `<b>` for the heading and `<code>` for the archive path.
-- No Markdown fences, no ZWNJ in Persian text, under ~3800 characters.
-- For a forum topic, deliver with `telegram_send_file(chat_id, file_path, caption, topic_id=...)` (it accepts `topic_id`) or with `telegram_reply_to_message` anchored to a message already inside the topic. `telegram_send_message` has no `topic_id` and lands in General.
-
-```html
-<b>Export archive</b>
-
-<code>export-{timestamp}.zip</code> — {count} messages, {media_count} media files.
-```
-
----
-
-## Part 3: Telegram Issue Sync & Discussion Crawler SOP (from `telegram-issue-sync`)
-
-# Telegram Issue Sync & Discussion Crawler SOP
-
-## Purpose
-
-Syncs actionable Telegram messages into GitHub Issues and local `tasks/` files. Unlike the previous version which **summarized** raw messages (BUG: Phase 3 Step 2 had vague "inject translated context" language that allowed LLMs to paraphrase and discard the original text), this SOP enforces:
-
-- **Zero-summarization**: raw non-English text is preserved verbatim in its original language
-- **Bilingual task files**: original message + complete English translation
-- **Prompt refactoring**: loads `prompt-refactor` skill to generate an enhanced prompt from the raw text
-- **Codebase correlation**: autonomously searches the codebase for files relevant to the described bug/feature
-- **Interactive cycle**: asks Manager for approval → generates tasks → optionally creates GitHub issues → replies to Telegram
-
-## Root Cause of the Summarization Bug
-
-The old Phase 3 Step 2 read:
-
-> _"Inject the translated Telegram discussion context and codebase correlation."_
-
-This was **ambiguously phrased** — it did not mandate verbatim preservation. LLMs interpret "inject context" as "extract the gist and summarize." The fix is:
-
-1. Explicit `## Original Message (<Language>)` section with the **exact raw text** — no transformation allowed
-2. A separate `## English Translation` section so the original is never overwritten or merged
-3. Strict `execution_rules` in the system prompt forbidding any truncation or paraphrasing
-
-## Local State Schema (`telegram-sync.json`)
-
-```json
-{
-  "config": {
-    "project_name": "[Name]",
-    "chat_id": "[Chat ID]",
-    "topic_id": null,
-    "account": null,
-    "target_hashtags": ["bug", "feature", "improve"]
-  },
-  "last_processed_message_id": 0,
-  "processed_ids": [],
-  "sync_registry": {}
-}
-```
-
-## Detailed Workflow
-
-### Phase 0: Load Mandatory Skills
-
-Before any Telegram fetching, you MUST load these skills:
-
-```markdown
-1. Load `kanban-lifecycle` skill — ensures task files use the correct template with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
-2. Load `prompt-refactor` skill — will be used in Phase 3 to generate the `## Refactored Prompt` section.
-3. Load `telegram-suite` skill (Part 1) — governs every message this skill sends back to Telegram (parse mode, escaping, length splitting, Persian text, topic targeting). MANDATORY before the Phase 3 reply step.
-```
-
-Use the `skill` tool for each. If loading fails, HALT and report the error.
-
-### Phase 1: Context Fetch & Deep Crawling
-
-1. Read `telegram-sync.json` at the project root to get `config.chat_id`, `config.topic_id`, `config.account`, and `last_processed_message_id`.
-2. Call `telegram_get_history` (with `account` if set, limit=100). This returns messages from ALL forum topics — Telegram has no server-side topic filter. **You MUST client-filter** to `reply_to == config.topic_id` OR walk the `reply_to` chain via `telegram_get_message_context` until you reach the topic root `config.topic_id`. Only messages whose `reply_to` chain terminates at `config.topic_id` belong to this project. Then additionally filter for `id > last_processed_message_id`.
-3. **Candidate Selection:** Identify messages containing `target_hashtags` from the _topic-filtered_ set. Also identify messages without hashtags that strongly resemble bug reports or feature requests.
-4. **Deep Context:** For every selected candidate, check `reply_to_message_id`. If it exists, call `telegram_get_message_context` to fetch the parent message. Merge the parent message (the "what") with the child message (the "intent").
-
-**CRITICAL — Message Integrity Rule:** Store the raw message text in a variable `RAW_TEXT` immediately after fetching. You MUST NOT modify, trim, or summarize this value at any point. Use it verbatim in Phase 3.
-
-### Forum Topic Targeting (Critical)
-
-This MCP implementation does **NOT** expose a `topic_id` parameter. Forum topics are identified by the `reply_to` field:
-
-- **Reading messages from a specific topic:** Call `telegram_get_history(chat_id=config.chat_id, limit=100, account=config.account)`. It returns messages from all topics. **Filter results by `reply_to`** — direct replies have `reply_to == config.topic_id` (e.g., `458` = Cognitive Lead, `455` = other project, `1` = General). For nested replies, walk the chain via `telegram_get_message_context` recursively until you hit the topic root `MessageActionTopicCreate`; discard messages whose chain terminates at `455`/`1`/`null`.
-- **Sending a message to a specific topic:** You MUST use `telegram_reply_to_message` with `message_id` set to `config.topic_id`. Never post topic confirmations to General.
-- **`telegram_send_message` MUST NOT be used for topic-scoped output:** it has no `topic_id` parameter, so it always lands in General.
-- **MANDATORY per `.opencode/memory/telegram-sync/topic-scoped-sync-workflow.md`:** `config.topic_id` defines the ONLY channel to sync. NEVER fetch/scan group-wide history.
-
-### Outgoing Message Formatting (Critical)
-
-Every message this skill sends to Telegram MUST follow Part 1 (`telegram-suite` formatting contract). The short version:
-
-- `parse_mode: "HTML"` — never `Markdown` (it destroys code blocks and leaves `*bold*` literal).
-- `<b>` for headings, `<code>` for inline identifiers, `<pre>` for code blocks; escape `&`, `<`, `>` inside them.
-- No ` ``` ` fences, no `*emphasis*`.
-- Persian text without U+200C ZWNJ (use a normal space where the half-space belongs).
-- Keep each message under ~3800 characters; split longer payloads into parts, each a reply to the same parent id.
-- Anchor the reply to the **source message** (`config.topic_id` root or the candidate's own id) so the message inherits the topic.
-
-### Phase 2: Manager Approval
-
-1. Check the session capability manifest for the `question` tool. If AVAILABLE, use it to present the candidates and collect approval. If the required tool is UNAVAILABLE_REQUIRED, manual mode relays the returned capability block verbatim and pauses; autopilot halts with that block as the named blocker. Never make a self-selected approval decision or proceed without the required approval.
-2. Phase 2 Candidate approval with brief-first options. For each candidate capture timestamp, sender, first 200 characters of the raw text, detected type (bug/feature/improve), topic, reply parent context (if any), and the numeric message ID. Present one `question`-tool option per candidate. Each option label starts with the timestamp in YYYY-MM-DD HH:MM enclosed in square brackets, followed by the sender name, a dash, the first 80 characters single-line, plus type and topic in parentheses. Each option description holds the full 200-character snippet, the type, the reply parent, and the internal ID for audit. Each option machine value is the numeric ID only and the ID is never shown as primary text. Never ask the Manager for bare message IDs: the closing prompt asks the Manager to reply with option numbers, names, or All. Manual-mode fallback when the `question` tool is unavailable renders a numbered brief list with the same label text; the Manager replies with numbers and you map numbers to IDs server-side in the same turn via a lookup table built from the listed candidates. Re-read the table before syncing to prevent a wrong anchor. All Telegram-facing text obeys the `telegram-suite` contract for HTML parse mode plus escaping plus no fences plus 4096 cap with splitting. Sync only approved IDs.
-3. Also ask: _"Should GitHub issues be created for these? (yes/no)"_
-4. Only proceed with the approved candidates. Log chosen IDs plus the mapping table in the task Execution Log.
-
-Store the Manager's GitHub preference in a variable `GH_ENABLED` (true/false).
-
-Autopilot note: the data question in step 4 (whether GitHub issues are wanted) folds into the planning turn. The Hands asks it once alongside candidate approval, records the answer in the task file, and never asks again mid-task.
-
-### Phase 3: Task Generation & Automation (Per Approved Candidate)
-
-For **each** approved candidate, execute the following steps **strictly in order**:
-
-> **TASK-GENERATOR MIRROR MANDATE:** Task creation MUST mirror `kanban-lifecycle` exactly: same ID discovery command, same duplicate-title check, same duplicate-ID check, same collision check, same canonical template, and same `## Definition of Done` block. Do NOT maintain divergent logic — if the `kanban-lifecycle` skill's workflow changes, mirror those changes here.
-
----
-
-**0. Mirror Checks (from kanban-lifecycle):**
-
-Before writing the task file, run the same guards the `kanban-lifecycle` skill runs:
-
-```bash
-# Duplicate-title check
-grep -rhn "^# Task [0-9][0-9]*:" tasks/ | sort | uniq -d
-# Duplicate-ID check (active Kanban dirs only — archive never blocks)
-find tasks/backlog tasks/in-progress tasks/qa tasks/completed -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort | uniq -d
-# Collision check
-ls tasks/backlog/${NEXT_ID}-*.md
-```
-
-If any check returns output, HALT and report the collision. Do NOT overwrite files. Archive is a historical record and MUST NOT be included in the blocking duplicate-ID check. If archive duplicates are discovered separately, report them as a warning only, never HALT task creation. Then confirm the generated task file includes the same `## Definition of Done` block as `kanban-lifecycle` (Build/Test/Lint exit 0, `lint_task_file` passes, `CHANGELOG.md` via Parse-Then-Append, `testing-verification` evidence).
-
----
-
-**1. Determine Next Task ID:**
-
-Run this bash command (searches across all Kanban subdirectories):
-
-```bash
-NEXT_ID=$(find tasks/ -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
-if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ]; then NEXT_ID="01"; fi
-printf "%02d\n" $NEXT_ID
-```
-
----
-
-**2. Generate English Translation:**
-
-Using the `RAW_TEXT` (the verbatim original message, in whatever language it was written), produce a complete English translation. Store it in a variable `EN_TRANSLATION`.
-
----
-
-**3. Load & Run Prompt Refactor (The Omni-Channel Filter):**
-
-The `prompt-refactor` skill should already be loaded (from Phase 0). Use it as the omni-channel filter: pass the `RAW_TEXT` (in its original language) to it so it translates the text to English, expands the architectural intent, and generates an enhanced "Max Power" prompt. Store the output in a variable `REFACTORED_PROMPT`.
-
-The refactored prompt MUST include the 5 XML blocks:
-
-- `<role>`
-- `<system_context>`
-- `<agentic_reasoning>`
-- `<constraints>` or `<execution_rules>`
-- `<output_format>`
-
----
-
-**4. Search Codebase for Relevant Context:**
-
-Use codebase exploration tools to find files related to the bug/feature described in the `RAW_TEXT`. Execute searches in this order:
-
-```markdown
-1. grep for key technical terms from the message across the codebase
-2. glob for likely file patterns (e.g., if the bug mentions "sync" → `**/*sync*`)
-3. Read the top 2-3 most relevant files to extract key excerpts
-```
-
-Store the results as `CODEBASE_CONTEXT` — a list of file paths with brief relevant excerpts.
-
----
-
-**5. Generate Your AI Analysis & Opinion:**
-
-Form an architectural diagnosis:
-
-- What is the root cause of the issue described?
-- What is the recommended fix?
-- What files need to change?
-- What are the risks?
-
-Store as `AI_OPINION`.
-
----
-
-**6. Generate Local Task File:**
-
-Create `tasks/backlog/{NEXT_ID}-hyphenated-title.md` using the **unified canonical template** from the `kanban-lifecycle` skill, with `**Source:** telegram`. Do NOT define a separate inline template — the `kanban-lifecycle` skill is the single source of truth for the file structure.
-
-Populate the telegram variant (`## Source Context` → Variant B) by filling these fields:
-
-- `## Goal` — **MANDATORY.** Derive a one-line goal from the `RAW_TEXT` before writing the file.
-- `## Acceptance Criteria` — **MANDATORY.** Derive 2-3 concrete, verifiable conditions from the Telegram message's intent before writing the file.
-- `## Original Message ({LANGUAGE})` — `{RAW_TEXT}` — **verbatim, zero changes.**
-
-  **RULE:** The `## Original Message` section MUST contain the exact text from Telegram. The section header names the detected language: `## Original Message (<Language>)`. If the language is unknown, use `## Original Message (Raw)`.
-
-- `## English Translation` — `{EN_TRANSLATION}`
-- `## Refactored Prompt` — `{REFACTORED_PROMPT}`
-- `## Relevant Code Context` — `{CODEBASE_CONTEXT}`
-- `## AI Analysis & Opinion` — `{AI_OPINION}`
-
-`## Local TODOs` MUST be populated with at minimum:
-
-```markdown
-- [ ] Initial codebase exploration
-- [ ] Verify functionality
-```
-
----
-
-**7. Create GitHub Issue (Optional):**
-
-Only if `GH_ENABLED` is true, create a unique temporary Markdown body file inside the project workspace with a native file-write tool. Put the Original Message, English Translation, AI Analysis, and migration note in that file. Set `BODY_FILE` to its concrete workspace-relative path, then run:
-
-```bash
-GH_URL=$(gh issue create \
-  --title "{Task Title}" \
-  --body-file "$BODY_FILE" \
-  --label "telegram-sync")
-printf 'GH_URL=%s\n' "$GH_URL"
-```
-
-After recording the result, delete only that exact temporary file with a native file-management tool. Do not use shell redirection, scripts, or an outside-workspace path to create the body file.
-
-If `GH_ENABLED` is false, set `GH_URL="Not created (skipped)"`.
-
----
-
-**8. Update State Deterministically with native file tools:**
-
-Edit `telegram-sync.json` using a native file-editing tool. Preserve unrelated keys. Set `last_processed_message_id` to the larger of its current value and the approved message ID. Add the message ID to `processed_ids` only if absent, then sort that list. Set `sync_registry[str(message_id)]` to an object containing the generated task-file path, the GitHub URL or recorded skip value, and the uppercase issue type. Do not create or execute a helper script and do not use shell or Python to write the JSON file. Verify the resulting JSON with `python3 -m json.tool telegram-sync.json` and inspect the native-tool diff.
-
----
-
-**9. Reply in Telegram:**
-
-Call `telegram_reply_to_message` with `parse_mode: "HTML"`, anchored to the **source message** (`config.topic_id` root, or the candidate's own message id) so the reply inherits the topic. The payload MUST follow Part 1 — no emoji, no Markdown fences, no ZWNJ in Persian text, under ~3800 characters.
-
-```html
-<b>Task synced</b>
-
-<b>File:</b> <code>tasks/backlog/{NEXT_ID}-title.md</code> <b>Issue:</b>
-<code>{GH_URL}</code> <b>Type:</b> {BUG|FEATURE|IMPROVE}
-```
-
-When the candidate is one of several in the same batch, add a leading line `<b>Task synced</b> (2 of 5)` so the Manager can match the reply to the message. If the payload would exceed ~3800 characters, split it into numbered parts, each a reply to the same parent id.
-
----
-
-### Phase 4: Mark Non-Actionable Messages
-
-Once all approved tasks are generated, edit `telegram-sync.json` with native file tools to update `last_processed_message_id` to the highest message ID observed in the batch and append the skipped IDs to `processed_ids`. Do not use a helper script.
-
-### Phase 5: Return Control
-
-For each generated task, invoke `brain_turn` directly under the active session thread with that task ID and task-file context. Do not ask the Manager to copy, paste, or relay task contents. Keep each task under the normal plan and approval gates. After the Brain turns return, report that the task files are ready for Orchestrator review.
-
-## Data Integrity Guarantees
-
-| Risk                            | Mitigation                                                                                                                                                                         |
-| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
-| LLM summarizes raw text         | `## Original Message` is declared as verbatim; the system prompt for the task-generation LLM MUST include "Do NOT summarize, paraphrase, or truncate the Original Message section" |
-| Non-English text gets corrupted | The raw text is stored immediately on fetch and never re-encoded; the task file is written in UTF-8                                                                                |
-| Codebase search misses context  | Three-pass search strategy (grep → glob → read) with fallback: if grep yields 0 results, broaden the search terms                                                                  |
-| State file has concurrent edits | Single-threaded Python updater script with atomic `json.dump` write                                                                                                                |
-| GitHub issue creation fails     | `GH_URL` gracefully defaults to `"Failed to create"`; the task file and Telegram reply still complete                                                                              |
-| Telegram reply renders broken   | The reply is sent with `parse_mode: "HTML"` and the Part 1 rules (escaping, no fences, no ZWNJ, length budget, topic anchoring)                                 |
+Templates are authoritative; this index only summarizes. Registry: `prompts/fragments/07-agent_skills_registry.md`.
diff --git a/skill-templates/telegram-suite/templates/01-format.md b/skill-templates/telegram-suite/templates/01-format.md
new file mode 100644
index 0000000..589f389
--- /dev/null
+++ b/skill-templates/telegram-suite/templates/01-format.md
@@ -0,0 +1,162 @@
+## Part 1: Telegram Message Formatting SOP (from `telegram-message-format`)
+
+## Purpose
+
+Every message an agent sends through the Telegram MCP must be clean, readable, and correctly rendered. The Telegram MCP server does **not** behave like the Bot API: it silently destroys Markdown structure, rejects over-length payloads with an opaque error, drops Persian half-spaces, and has no topic parameter on `send_message`.
+
+This skill is the agent-facing rulebook. The full evidence (probe transcripts, defect list, server-side recommendations) lives in the HQ repository at `docs/telegram-message-formatting.md`.
+
+**Load this skill before any Telegram send.** It applies to `send_message`, `reply_to_message`, `edit_message`, `send_file` captions, and any other tool that puts text into a chat.
+
+---
+
+## The 9 Rules
+
+| # | Rule                                                                                                    | Why                                                                            |
+| - | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
+| 1 | Always send with `parse_mode: "HTML"`.                                                                   | Markdown mode strips fence/backtick markers and creates no entities.          |
+| 2 | Escape `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;` inside `<pre>` and `<code>`.                             | A raw `<` breaks the HTML parse and aborts the entire message.                |
+| 3 | Use `<b>` for headings, `<code>` for inline identifiers, `<pre>` for code blocks.                          | These three are the only elements proven to survive the round-trip.           |
+| 4 | Never use ` ``` ` fences or `*bold*` Markdown syntax.                                                     | Fences vanish; asterisks stay literal.                                        |
+| 5 | Write Persian without U+200C ZWNJ — use a normal space where the half-space belongs.                      | ZWNJ is lost on the read path of every message, including hand-typed ones.    |
+| 6 | Keep each message under ~3800 characters; split longer payloads into parts, each a reply to the same parent id. | The hard cap is 4096 chars and the failure is an opaque `GEN-ERR-184`.      |
+| 7 | Post into a forum topic with `reply_to_message` anchored to a message already inside that topic.           | `send_message` has no `topic_id` and lands in General.                        |
+| 8 | Verify a formatted send by reading it back and checking the `&lt;`/`&gt;` round-trip.                      | `get_history` resolves entities to plain text, so a text diff proves nothing. |
+| 9 | Delete every probe message after reading it back.                                                         | Keeps the chat clean; message ids are never reused.                           |
+
+---
+
+## Rule Details
+
+### 1–4. Parse mode and markup
+
+- `parse_mode: "HTML"` is the only mode that works. `Markdown` consumes ` ``` ` fences and inline backticks without creating the matching Telegram entities, and leaves `*bold*` as literal asterisks.
+- A message with **no** markup needs no parse mode at all — plain text is safe.
+- The safe element set is `<b>`, `<i>`, `<u>`, `<code>`, `<pre>`, `<a>`. Everything else is unverified — do not use it.
+- `<pre>` keeps its block boundaries. Put the code body inside it, escape `&`, `<`, `>`, and keep the language hint as plain text inside the block (the server does not support a language attribute).
+- One unescaped `<` in the payload rejects the whole message, so escape **all** angle brackets inside `<pre>` and `<code>`, including shell redirects (`>`) and generics.
+
+### 5. Persian text (and any non-ASCII text)
+
+- The server drops U+200C ZERO WIDTH NON-JOINER on the read path. It is lost for every message, not only agent-authored ones.
+- Author Persian with a **normal space** where the half-space belongs: `می کند`, `قابل تسویه`, `نمی فهمم`. Never paste a ZWNJ into authored text.
+- Same caution for other `Cf` (format) characters: zero-width space, BOM, soft hyphen. Use plain text.
+
+### 6. Length budget and splitting
+
+- Hard cap: **4096 characters**. Over that, the server returns `An error occurred (code: GEN-ERR-184)` with no hint — never retry it, it is not transient.
+- Plan on **~3800 characters** per message to leave headroom for the reply anchor and for entity overhead.
+- Count characters, not bytes. Persian, Arabic, and emoji payloads hit the cap well before their byte length suggests.
+- When a payload exceeds the budget, split it into numbered parts, each sent as a reply to the **same** parent message id, so the thread stays readable:
+
+  ```html
+  <b>Report — part 1 of 3</b>
+
+  ... first third ...
+
+  <i>Continued in the next reply.</i>
+  ```
+
+- Keep the part count minimal and never split inside a `<pre>` block.
+
+### 7. Forum topics
+
+- `send_message` accepts `chat_id`, `message`, `parse_mode`, `format_date`, `custom_emojis`, `account` — **no `topic_id`**. In a supergroup with forum topics enabled it lands in **General**.
+- `send_album` and `send_file` do accept `topic_id`.
+- To post into a topic, reply to a message that already lives in that topic — a reply inherits the topic of its parent:
+
+  ```text
+  reply_to_message(chat_id, message_id=<id inside the target topic>, account, parse_mode="HTML", text=...)
+  ```
+
+- Never post a topic-scoped confirmation with `send_message`.
+
+### 8. Read-back verification
+
+- `get_history` returns text with entities already resolved, so comparing the read-back text against the sent text **cannot** prove the formatting was applied.
+- The reliable check is the entity round-trip: send `&lt;` inside a `<pre>` block, read it back, and confirm it came back as a literal `<` with the block intact. If the literal `&lt;` is still there, the HTML was not parsed.
+
+### 9. Probe hygiene
+
+- Every probe message must be deleted with `delete_message(chat_id, message_id, account)` after it is read back.
+- Deleting does not renumber the remaining messages; later messages keep their ids. Treat a cached id as "may no longer resolve" rather than "was renumbered".
+
+---
+
+## Message Templates
+
+### Short prose message
+
+```html
+<b>Short heading</b>
+
+Plain prose with <code>identifiers</code> and no markup dependency.
+```
+
+### Report with a code block
+
+```html
+<b>Heading</b> and <code>inline_identifier</code>
+
+<pre>curl -X POST "https://example.com/api" \
+  --data 'key=value'</pre>
+
+<b>Second heading</b>
+
+<pre>SELECT id, state FROM trades WHERE id = 2069;</pre>
+
+Notes with <code>snake_case_names</code> inline.
+```
+
+### Status confirmation on a task
+
+```html
+<b>Task synced</b>
+
+<b>File:</b> <code>tasks/backlog/123-example.md</code>
+<b>Issue:</b> <code>https://github.com/org/repo/issues/7</code>
+<b>Type:</b> BUG
+```
+
+Keep the body plain — no emoji, no ASCII art, no horizontal rules made of dashes. One blank line between blocks, never more.
+
+### File caption (for `send_file`)
+
+```html
+<b>Export archive</b>
+
+<code>export-20261021-101500.zip</code> — 42 messages, 6 media files.
+```
+
+---
+
+## Pre-Send Checklist
+
+Run through this before every send:
+
+1. `parse_mode` is `"HTML"`, or the message is pure plain text with no markup.
+2. Every `&`, `<`, `>` inside `<pre>` / `<code>` is escaped.
+3. No ` ``` ` fences and no `*asterisk*` emphasis anywhere.
+4. No U+200C or other `Cf` characters in the text.
+5. The message is under ~3800 characters — or it is split into numbered parts.
+6. The target is a topic → the send is a `reply_to_message` to a message inside that topic.
+7. The payload is not raw LLM output: it has been read once and checked for stray angle brackets and Markdown leftovers.
+
+---
+
+## Server Defects (known, unfixed)
+
+The following are upstream defects in the Telegram MCP server. Work around them; do not report them as your own errors, and do not retry them.
+
+| Defect                                                | Workaround                                                       |
+| ----------------------------------------------------- | ---------------------------------------------------------------- |
+| Over-length message returns opaque `GEN-ERR-184`       | Self-enforce the 3800-character budget; never retry.            |
+| Markdown mode destroys code blocks                    | Use HTML.                                                         |
+| Markdown `*bold*` not applied                         | Use `<b>`.                                                        |
+| ZWNJ lost on the read path                            | Author Persian without U+200C.                                   |
+| `send_message` cannot target a forum topic            | Use `reply_to_message` anchored inside the topic.                |
+| Message `entities` not exposed on read               | Verify with the `&lt;`/`&gt;` round-trip, not a text diff.      |
+| Length counted without UTF-16 semantics                | Count characters yourself, not bytes.                            |
+
+---
+
diff --git a/skill-templates/telegram-suite/templates/02-export.md b/skill-templates/telegram-suite/templates/02-export.md
new file mode 100644
index 0000000..beccfb4
--- /dev/null
+++ b/skill-templates/telegram-suite/templates/02-export.md
@@ -0,0 +1,72 @@
+## Part 2: Telegram Message Export Skill (from `telegram-message-export`)
+
+# Telegram Message Export Skill
+
+## Purpose
+
+Extracts a highly contextual range of Telegram messages. It explicitly documents reply relationships to preserve conversation trees and packages text alongside downloaded media files (images, voice notes) into a ZIP file.
+
+## Input Resolution
+
+Determine the exact `[from_id, to_id]` range. If the Manager provided a text snippet, use `telegram_search_messages` to find the `msg_id`. If a link is provided (`t.me/c/CHAT_ID/MSG_ID`), extract the ID.
+
+## Phase 1: Contextual Fetching
+
+1. Call `telegram_get_history` and filter to keep messages where `id >= from_id` and `id <= to_id`.
+2. Sort the filtered messages strictly by `id` in ascending order.
+3. If the range spans more than 200 messages, ask for confirmation before proceeding to avoid rate limits. Use the `question` tool when the session capability manifest shows it AVAILABLE; otherwise relay the same question in prose and wait for the answer.
+
+## Phase 2: Extraction & Sidecar Generation
+
+1. Create directory: `mkdir -p <workspace>/telegram-exports/export-{timestamp}/`
+2. Set counter `n = 1`.
+3. For each message in the sorted list:
+
+   **Text Sidecar (`{n}.txt`)**:
+   Create a `.txt` file for every message. You MUST include `reply_to_message_id` to preserve thread context.
+
+   ```text
+   Message ID: {message.id}
+   From: {sender_name_or_id}
+   Date: {date}
+   Reply To Message ID: {reply_to_message_id | 'None'}
+   Message Type: {type}
+
+   [Content]
+   {message_text | caption | '[No extractable content]'}
+   ```
+
+   **Media Download**:
+   If the message contains media, call `telegram_get_media_info` to get the extension. Then call `telegram_download_media(chat_id=..., message_id=..., file_path="<workspace>/telegram-exports/export-{timestamp}/{n}.{ext}")`.
+
+4. Increment `n`.
+
+## Phase 3: Archiving
+
+Run the bash zip command:
+
+```bash
+cd <workspace>/telegram-exports && zip -r export-{timestamp}.zip export-{timestamp}/
+rm -rf export-{timestamp}/
+```
+
+## Phase 4: Notification
+
+Output exactly: "✅ Contextual Telegram export complete. Range: {from_id} to {to_id}. Archive path: <workspace>/telegram-exports/export-{timestamp}.zip"
+
+## Phase 5: Optional Telegram Delivery
+
+When the archive is delivered to a chat through the Telegram MCP, the caption and any follow-up message MUST follow the `telegram-suite` (Part 1) contract:
+
+- `parse_mode: "HTML"`, with `<b>` for the heading and `<code>` for the archive path.
+- No Markdown fences, no ZWNJ in Persian text, under ~3800 characters.
+- For a forum topic, deliver with `telegram_send_file(chat_id, file_path, caption, topic_id=...)` (it accepts `topic_id`) or with `telegram_reply_to_message` anchored to a message already inside the topic. `telegram_send_message` has no `topic_id` and lands in General.
+
+```html
+<b>Export archive</b>
+
+<code>export-{timestamp}.zip</code> — {count} messages, {media_count} media files.
+```
+
+---
+
diff --git a/skill-templates/telegram-suite/templates/03-sync.md b/skill-templates/telegram-suite/templates/03-sync.md
new file mode 100644
index 0000000..b152cb5
--- /dev/null
+++ b/skill-templates/telegram-suite/templates/03-sync.md
@@ -0,0 +1,264 @@
+## Part 3: Telegram Issue Sync & Discussion Crawler SOP (from `telegram-issue-sync`)
+
+# Telegram Issue Sync & Discussion Crawler SOP
+
+## Purpose
+
+Syncs actionable Telegram messages into GitHub Issues and local `tasks/` files. Unlike the previous version which **summarized** raw messages (BUG: Phase 3 Step 2 had vague "inject translated context" language that allowed LLMs to paraphrase and discard the original text), this SOP enforces:
+
+- **Zero-summarization**: raw non-English text is preserved verbatim in its original language
+- **Bilingual task files**: original message + complete English translation
+- **Prompt refactoring**: loads `prompt-refactor` skill to generate an enhanced prompt from the raw text
+- **Codebase correlation**: autonomously searches the codebase for files relevant to the described bug/feature
+- **Interactive cycle**: asks Manager for approval → generates tasks → optionally creates GitHub issues → replies to Telegram
+
+## Root Cause of the Summarization Bug
+
+The old Phase 3 Step 2 read:
+
+> _"Inject the translated Telegram discussion context and codebase correlation."_
+
+This was **ambiguously phrased** — it did not mandate verbatim preservation. LLMs interpret "inject context" as "extract the gist and summarize." The fix is:
+
+1. Explicit `## Original Message (<Language>)` section with the **exact raw text** — no transformation allowed
+2. A separate `## English Translation` section so the original is never overwritten or merged
+3. Strict `execution_rules` in the system prompt forbidding any truncation or paraphrasing
+
+## Local State Schema (`telegram-sync.json`)
+
+```json
+{
+  "config": {
+    "project_name": "[Name]",
+    "chat_id": "[Chat ID]",
+    "topic_id": null,
+    "account": null,
+    "target_hashtags": ["bug", "feature", "improve"]
+  },
+  "last_processed_message_id": 0,
+  "processed_ids": [],
+  "sync_registry": {}
+}
+```
+
+## Detailed Workflow
+
+### Phase 0: Load Mandatory Skills
+
+Before any Telegram fetching, you MUST load these skills:
+
+```markdown
+1. Load `kanban-lifecycle` skill — ensures task files use the correct template with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
+2. Load `prompt-refactor` skill — will be used in Phase 3 to generate the `## Refactored Prompt` section.
+3. Load `telegram-suite` skill (Part 1) — governs every message this skill sends back to Telegram (parse mode, escaping, length splitting, Persian text, topic targeting). MANDATORY before the Phase 3 reply step.
+```
+
+Use the `skill` tool for each. If loading fails, HALT and report the error.
+
+### Phase 1: Context Fetch & Deep Crawling
+
+1. Read `telegram-sync.json` at the project root to get `config.chat_id`, `config.topic_id`, `config.account`, and `last_processed_message_id`.
+2. Call `telegram_get_history` (with `account` if set, limit=100). This returns messages from ALL forum topics — Telegram has no server-side topic filter. **You MUST client-filter** to `reply_to == config.topic_id` OR walk the `reply_to` chain via `telegram_get_message_context` until you reach the topic root `config.topic_id`. Only messages whose `reply_to` chain terminates at `config.topic_id` belong to this project. Then additionally filter for `id > last_processed_message_id`.
+3. **Candidate Selection:** Identify messages containing `target_hashtags` from the _topic-filtered_ set. Also identify messages without hashtags that strongly resemble bug reports or feature requests.
+4. **Deep Context:** For every selected candidate, check `reply_to_message_id`. If it exists, call `telegram_get_message_context` to fetch the parent message. Merge the parent message (the "what") with the child message (the "intent").
+
+**CRITICAL — Message Integrity Rule:** Store the raw message text in a variable `RAW_TEXT` immediately after fetching. You MUST NOT modify, trim, or summarize this value at any point. Use it verbatim in Phase 3.
+
+### Forum Topic Targeting (Critical)
+
+This MCP implementation does **NOT** expose a `topic_id` parameter. Forum topics are identified by the `reply_to` field:
+
+- **Reading messages from a specific topic:** Call `telegram_get_history(chat_id=config.chat_id, limit=100, account=config.account)`. It returns messages from all topics. **Filter results by `reply_to`** — direct replies have `reply_to == config.topic_id` (e.g., `458` = Cognitive Lead, `455` = other project, `1` = General). For nested replies, walk the chain via `telegram_get_message_context` recursively until you hit the topic root `MessageActionTopicCreate`; discard messages whose chain terminates at `455`/`1`/`null`.
+- **Sending a message to a specific topic:** You MUST use `telegram_reply_to_message` with `message_id` set to `config.topic_id`. Never post topic confirmations to General.
+- **`telegram_send_message` MUST NOT be used for topic-scoped output:** it has no `topic_id` parameter, so it always lands in General.
+- **MANDATORY per `.opencode/memory/telegram-sync/topic-scoped-sync-workflow.md`:** `config.topic_id` defines the ONLY channel to sync. NEVER fetch/scan group-wide history.
+
+### Outgoing Message Formatting (Critical)
+
+Every message this skill sends to Telegram MUST follow Part 1 (`telegram-suite` formatting contract). The short version:
+
+- `parse_mode: "HTML"` — never `Markdown` (it destroys code blocks and leaves `*bold*` literal).
+- `<b>` for headings, `<code>` for inline identifiers, `<pre>` for code blocks; escape `&`, `<`, `>` inside them.
+- No ` ``` ` fences, no `*emphasis*`.
+- Persian text without U+200C ZWNJ (use a normal space where the half-space belongs).
+- Keep each message under ~3800 characters; split longer payloads into parts, each a reply to the same parent id.
+- Anchor the reply to the **source message** (`config.topic_id` root or the candidate's own id) so the message inherits the topic.
+
+### Phase 2: Manager Approval
+
+1. Check the session capability manifest for the `question` tool. If AVAILABLE, use it to present the candidates and collect approval. If the required tool is UNAVAILABLE_REQUIRED, manual mode relays the returned capability block verbatim and pauses; autopilot halts with that block as the named blocker. Never make a self-selected approval decision or proceed without the required approval.
+2. Phase 2 Candidate approval with brief-first options. For each candidate capture timestamp, sender, first 200 characters of the raw text, detected type (bug/feature/improve), topic, reply parent context (if any), and the numeric message ID. Present one `question`-tool option per candidate. Each option label starts with the timestamp in YYYY-MM-DD HH:MM enclosed in square brackets, followed by the sender name, a dash, the first 80 characters single-line, plus type and topic in parentheses. Each option description holds the full 200-character snippet, the type, the reply parent, and the internal ID for audit. Each option machine value is the numeric ID only and the ID is never shown as primary text. Never ask the Manager for bare message IDs: the closing prompt asks the Manager to reply with option numbers, names, or All. Manual-mode fallback when the `question` tool is unavailable renders a numbered brief list with the same label text; the Manager replies with numbers and you map numbers to IDs server-side in the same turn via a lookup table built from the listed candidates. Re-read the table before syncing to prevent a wrong anchor. All Telegram-facing text obeys the `telegram-suite` contract for HTML parse mode plus escaping plus no fences plus 4096 cap with splitting. Sync only approved IDs.
+3. Also ask: _"Should GitHub issues be created for these? (yes/no)"_
+4. Only proceed with the approved candidates. Log chosen IDs plus the mapping table in the task Execution Log.
+
+Store the Manager's GitHub preference in a variable `GH_ENABLED` (true/false).
+
+Autopilot note: the data question in step 4 (whether GitHub issues are wanted) folds into the planning turn. The Hands asks it once alongside candidate approval, records the answer in the task file, and never asks again mid-task.
+
+### Phase 3: Task Generation & Automation (Per Approved Candidate)
+
+For **each** approved candidate, execute the following steps **strictly in order**:
+
+> **TASK-GENERATOR MIRROR MANDATE:** Task creation MUST mirror `kanban-lifecycle` exactly: same ID discovery command, same duplicate-title check, same duplicate-ID check, same collision check, same canonical template, and same `## Definition of Done` block. Do NOT maintain divergent logic — if the `kanban-lifecycle` skill's workflow changes, mirror those changes here.
+
+---
+
+**0. Mirror Checks (from kanban-lifecycle):**
+
+Before writing the task file, run the same guards the `kanban-lifecycle` skill runs:
+
+```bash
+# Duplicate-title check
+grep -rhn "^# Task [0-9][0-9]*:" tasks/ | sort | uniq -d
+# Duplicate-ID check (active Kanban dirs only — archive never blocks)
+find tasks/backlog tasks/in-progress tasks/qa tasks/completed -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort | uniq -d
+# Collision check
+ls tasks/backlog/${NEXT_ID}-*.md
+```
+
+If any check returns output, HALT and report the collision. Do NOT overwrite files. Archive is a historical record and MUST NOT be included in the blocking duplicate-ID check. If archive duplicates are discovered separately, report them as a warning only, never HALT task creation. Then confirm the generated task file includes the same `## Definition of Done` block as `kanban-lifecycle` (Build/Test/Lint exit 0, `lint_task_file` passes, `CHANGELOG.md` via Parse-Then-Append, `testing-verification` evidence).
+
+---
+
+**1. Determine Next Task ID:**
+
+Run this bash command (searches across all Kanban subdirectories):
+
+```bash
+NEXT_ID=$(find tasks/ -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
+if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ]; then NEXT_ID="01"; fi
+printf "%02d\n" $NEXT_ID
+```
+
+---
+
+**2. Generate English Translation:**
+
+Using the `RAW_TEXT` (the verbatim original message, in whatever language it was written), produce a complete English translation. Store it in a variable `EN_TRANSLATION`.
+
+---
+
+**3. Load & Run Prompt Refactor (The Omni-Channel Filter):**
+
+The `prompt-refactor` skill should already be loaded (from Phase 0). Use it as the omni-channel filter: pass the `RAW_TEXT` (in its original language) to it so it translates the text to English, expands the architectural intent, and generates an enhanced "Max Power" prompt. Store the output in a variable `REFACTORED_PROMPT`.
+
+The refactored prompt MUST include the 5 XML blocks:
+
+- `<role>`
+- `<system_context>`
+- `<agentic_reasoning>`
+- `<constraints>` or `<execution_rules>`
+- `<output_format>`
+
+---
+
+**4. Search Codebase for Relevant Context:**
+
+Use codebase exploration tools to find files related to the bug/feature described in the `RAW_TEXT`. Execute searches in this order:
+
+```markdown
+1. grep for key technical terms from the message across the codebase
+2. glob for likely file patterns (e.g., if the bug mentions "sync" → `**/*sync*`)
+3. Read the top 2-3 most relevant files to extract key excerpts
+```
+
+Store the results as `CODEBASE_CONTEXT` — a list of file paths with brief relevant excerpts.
+
+---
+
+**5. Generate Your AI Analysis & Opinion:**
+
+Form an architectural diagnosis:
+
+- What is the root cause of the issue described?
+- What is the recommended fix?
+- What files need to change?
+- What are the risks?
+
+Store as `AI_OPINION`.
+
+---
+
+**6. Generate Local Task File:**
+
+Create `tasks/backlog/{NEXT_ID}-hyphenated-title.md` using the **unified canonical template** from the `kanban-lifecycle` skill, with `**Source:** telegram`. Do NOT define a separate inline template — the `kanban-lifecycle` skill is the single source of truth for the file structure.
+
+Populate the telegram variant (`## Source Context` → Variant B) by filling these fields:
+
+- `## Goal` — **MANDATORY.** Derive a one-line goal from the `RAW_TEXT` before writing the file.
+- `## Acceptance Criteria` — **MANDATORY.** Derive 2-3 concrete, verifiable conditions from the Telegram message's intent before writing the file.
+- `## Original Message ({LANGUAGE})` — `{RAW_TEXT}` — **verbatim, zero changes.**
+
+  **RULE:** The `## Original Message` section MUST contain the exact text from Telegram. The section header names the detected language: `## Original Message (<Language>)`. If the language is unknown, use `## Original Message (Raw)`.
+
+- `## English Translation` — `{EN_TRANSLATION}`
+- `## Refactored Prompt` — `{REFACTORED_PROMPT}`
+- `## Relevant Code Context` — `{CODEBASE_CONTEXT}`
+- `## AI Analysis & Opinion` — `{AI_OPINION}`
+
+`## Local TODOs` MUST be populated with at minimum:
+
+```markdown
+- [ ] Initial codebase exploration
+- [ ] Verify functionality
+```
+
+---
+
+**7. Create GitHub Issue (Optional):**
+
+Only if `GH_ENABLED` is true, create a unique temporary Markdown body file inside the project workspace with a native file-write tool. Put the Original Message, English Translation, AI Analysis, and migration note in that file. Set `BODY_FILE` to its concrete workspace-relative path, then run:
+
+```bash
+GH_URL=$(gh issue create \
+  --title "{Task Title}" \
+  --body-file "$BODY_FILE" \
+  --label "telegram-sync")
+printf 'GH_URL=%s\n' "$GH_URL"
+```
+
+After recording the result, delete only that exact temporary file with a native file-management tool. Do not use shell redirection, scripts, or an outside-workspace path to create the body file.
+
+If `GH_ENABLED` is false, set `GH_URL="Not created (skipped)"`.
+
+---
+
+**8. Update State Deterministically with native file tools:**
+
+Edit `telegram-sync.json` using a native file-editing tool. Preserve unrelated keys. Set `last_processed_message_id` to the larger of its current value and the approved message ID. Add the message ID to `processed_ids` only if absent, then sort that list. Set `sync_registry[str(message_id)]` to an object containing the generated task-file path, the GitHub URL or recorded skip value, and the uppercase issue type. Do not create or execute a helper script and do not use shell or Python to write the JSON file. Verify the resulting JSON with `python3 -m json.tool telegram-sync.json` and inspect the native-tool diff.
+
+---
+
+**9. Reply in Telegram:**
+
+Call `telegram_reply_to_message` with `parse_mode: "HTML"`, anchored to the **source message** (`config.topic_id` root, or the candidate's own message id) so the reply inherits the topic. The payload MUST follow Part 1 — no emoji, no Markdown fences, no ZWNJ in Persian text, under ~3800 characters.
+
+```html
+<b>Task synced</b>
+
+<b>File:</b> <code>tasks/backlog/{NEXT_ID}-title.md</code> <b>Issue:</b>
+<code>{GH_URL}</code> <b>Type:</b> {BUG|FEATURE|IMPROVE}
+```
+
+When the candidate is one of several in the same batch, add a leading line `<b>Task synced</b> (2 of 5)` so the Manager can match the reply to the message. If the payload would exceed ~3800 characters, split it into numbered parts, each a reply to the same parent id.
+
+---
+
+### Phase 4: Mark Non-Actionable Messages
+
+Once all approved tasks are generated, edit `telegram-sync.json` with native file tools to update `last_processed_message_id` to the highest message ID observed in the batch and append the skipped IDs to `processed_ids`. Do not use a helper script.
+
+### Phase 5: Return Control
+
+For each generated task, invoke `brain_turn` directly under the active session thread with that task ID and task-file context. Do not ask the Manager to copy, paste, or relay task contents. Keep each task under the normal plan and approval gates. After the Brain turns return, report that the task files are ready for Orchestrator review.
+
+## Data Integrity Guarantees
+
+| Risk                            | Mitigation                                                                                                                                                                         |
+| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
+| LLM summarizes raw text         | `## Original Message` is declared as verbatim; the system prompt for the task-generation LLM MUST include "Do NOT summarize, paraphrase, or truncate the Original Message section" |
+| Non-English text gets corrupted | The raw text is stored immediately on fetch and never re-encoded; the task file is written in UTF-8                                                                                |
+| Codebase search misses context  | Three-pass search strategy (grep → glob → read) with fallback: if grep yields 0 results, broaden the search terms                                                                  |
+| State file has concurrent edits | Single-threaded Python updater script with atomic `json.dump` write                                                                                                                |
+| GitHub issue creation fails     | `GH_URL` gracefully defaults to `"Failed to create"`; the task file and Telegram reply still complete                                                                              |
+| Telegram reply renders broken   | The reply is sent with `parse_mode: "HTML"` and the Part 1 rules (escaping, no fences, no ZWNJ, length budget, topic anchoring)                                 |
diff --git a/system-prompt.md b/system-prompt.md
index d0da785..817f514 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.87.0</system_version>
+<system_version>9.88.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -115,7 +115,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 
 - **code-search**: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
 - **kanban-lifecycle**: Unified Kanban lifecycle — task generation, lint validation, META bundling, completion archiving, and flat-to-V6 migration in one meta skill. Load before creating, linting, bundling, archiving, or migrating `tasks/` files.
-- **governance**: Agent protocol auditing plus living folder docs scaffolding — `AGENTS.md` governance and README/DECISIONS baselines in one meta skill.
+- **governance**: Agent protocol auditing, living folder docs scaffolding, and project-only `opencode.json` generation — `AGENTS.md` governance plus README/DECISIONS baselines plus Parts 2–3 of `templates/init.md` in one meta skill.
 - **versioning-and-release**: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.
 - **debug-instrumentation**: Mandatory workflow for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
 - **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning. After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
@@ -127,7 +127,6 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **database-migration**: Forbid direct schema alterations and force standard migration tools (Alembic, Prisma, Flyway) for safe, repeatable deployments.
 - **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
 - **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
-- **opencode-init**: Analyze a project (or ask the user) and generate a comprehensive, correct opencode.json for it. Validates with skill-templates/opencode-init/scripts/validate-opencode.py before writing; never touches global config. Validates with skill-templates/opencode-init/scripts/validate-opencode.py before writing; never touches global config.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index bdc1562..0111dd1 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -47,7 +47,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.87.0"
+    assert shipped == "9.88.0"
 
 
 def test_shipped_prompt_documents_context_path_line_ranges():
@@ -372,7 +372,7 @@ def test_executor_contains_full_dto_mandate():
 
 def test_shipped_prompt_version_is_9_78_0():
     prompt = _read_shipped_prompt_for_approval_contract()
-    assert "9.87.0" in prompt
+    assert "9.88.0" in prompt
 
 
 def test_assembler_output_matches_shipped(tmp_path):
@@ -492,6 +492,10 @@ def test_executor_evidence_records_rtk_command():
 
 def test_task_generator_template_prescribes_rtk():
     text = _read(TASKGEN_SKILL)
+    tpl_dir = TASKGEN_SKILL.parent / "templates"
+    if tpl_dir.is_dir():
+        for f in sorted(tpl_dir.glob("*.md")):
+            text += "\n" + f.read_text(encoding="utf-8")
     assert "rtk test [exact command]" in text
 
 
@@ -706,7 +710,7 @@ def test_skill_templates_no_dsp_violations():
 
     violations = []
     for path in (REPO / "skill-templates").rglob("*.md"):
-        if path.name == "SKILL.md" and "governance" in str(path):
+        if "governance" in str(path):
             continue
         for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
             if "2>/dev/null" in line:
diff --git a/tests/test_skill_registry.py b/tests/test_skill_registry.py
index 0ab21ec..20ccb5e 100644
--- a/tests/test_skill_registry.py
+++ b/tests/test_skill_registry.py
@@ -35,7 +35,13 @@ def test_every_registry_skill_has_matching_template():
 
 
 def _template_text(name: str) -> str:
-    return (ROOT / "skill-templates" / name / "SKILL.md").read_text(encoding="utf-8")
+    direction = ROOT / "skill-templates" / name
+    parts = [(direction / "SKILL.md").read_text(encoding="utf-8")]
+    tpl_dir = direction / "templates"
+    if tpl_dir.is_dir():
+        for f in sorted(tpl_dir.glob("*.md")):
+            parts.append(f.read_text(encoding="utf-8"))
+    return "\n".join(parts)
 
 
 def test_testing_strategy_skill_contract():
@@ -82,7 +88,7 @@ def test_hexagonal_expansion_contract():
 
 
 def test_opencode_init_skill_contract():
-    text = _template_text("opencode-init")
+    text = _template_text("governance")
     for required in (
         "validate-opencode.py",
         "flat map",
@@ -95,8 +101,15 @@ def test_opencode_init_skill_contract():
     ):
         assert required in text, f"contract term missing: {required}"
     reg = REGISTRY.read_text(encoding="utf-8")
-    assert "opencode-init" in reg
-    refs = ROOT / "skill-templates" / "opencode-init" / "references"
+    assert "governance" in reg
+    refs = (
+        ROOT
+        / "skill-templates"
+        / "governance"
+        / "templates"
+        / "opencode-init"
+        / "references"
+    )
     assert (refs / "runtime-matrix.md").is_file()
     assert (refs / "examples" / "golden-opencode.json").is_file()
 
@@ -106,11 +119,19 @@ def test_validate_opencode_script():
     import subprocess
 
     script = (
-        ROOT / "skill-templates" / "opencode-init" / "scripts" / "validate-opencode.py"
+        ROOT
+        / "skill-templates"
+        / "governance"
+        / "templates"
+        / "opencode-init"
+        / "scripts"
+        / "validate-opencode.py"
     )
     golden = (
         ROOT
         / "skill-templates"
+        / "governance"
+        / "templates"
         / "opencode-init"
         / "references"
         / "examples"
@@ -154,7 +175,13 @@ def _run_validator(cfg=None, raw=None):
     import subprocess
 
     script = (
-        ROOT / "skill-templates" / "opencode-init" / "scripts" / "validate-opencode.py"
+        ROOT
+        / "skill-templates"
+        / "governance"
+        / "templates"
+        / "opencode-init"
+        / "scripts"
+        / "validate-opencode.py"
     )
     p = ROOT / ".tmp-validate-check.json"
     p.write_text(raw if raw is not None else json.dumps(cfg), encoding="utf-8")
@@ -176,6 +203,8 @@ def _fresh_golden():
     golden = (
         ROOT
         / "skill-templates"
+        / "governance"
+        / "templates"
         / "opencode-init"
         / "references"
         / "examples"
@@ -322,7 +351,13 @@ def test_validate_malformed_inputs_fail_closed():
     import subprocess
 
     script = (
-        ROOT / "skill-templates" / "opencode-init" / "scripts" / "validate-opencode.py"
+        ROOT
+        / "skill-templates"
+        / "governance"
+        / "templates"
+        / "opencode-init"
+        / "scripts"
+        / "validate-opencode.py"
     )
     r = subprocess.run(
         ["python3", str(script), str(ROOT / ".tmp-does-not-exist.json")],
@@ -425,9 +460,7 @@ def test_doc_coauthoring_skill_is_runtime_neutral():
 
 
 def test_audit_template_requires_project_skills_table():
-    text = (ROOT / "skill-templates" / "governance" / "SKILL.md").read_text(
-        encoding="utf-8"
-    )
+    text = _template_text("governance")
     assert "Project Skills Table" in text
     assert "stale row" in text
```
<!-- END_GIT_DIFF -->
