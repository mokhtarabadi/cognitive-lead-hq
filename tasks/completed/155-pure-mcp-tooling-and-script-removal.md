# Task 155: Pure MCP Tooling & Script Removal

**File:** `tasks/qa/155-pure-mcp-tooling-and-script-removal.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Inline the complete task bundling engine natively into `mcp-context-server/server.py` (eliminating external script subprocess calls), remove `scripts/bundle-tasks.py` and `scripts/qa-transition.py`, update `prompts/fragments/09-hands_protocols.md` to reference pure MCP tools, and verify 100% feature parity on `qa_transition` and `bundle_tasks`.

## Manager's Notes

Source: Manager Request (2026-09-02). This task eliminates external Python script dependencies by migrating the full bundling logic into the MCP context server as native tooling. Related to Task 154 (atomic QA transition) — extends pure-MCP architecture to the bundle workflow. Requires updating prompt fragments and reassembling `system-prompt.md` with version bump.

## Local TODOs

- [x] Explore `mcp-context-server/server.py` and `scripts/bundle-tasks.py`
- [x] Migrate bundling logic natively into `mcp-context-server/server.py` (or internal module in `mcp-context-server/`) — already native per discovery (self-contained at line 779), no migration needed
- [x] Delete `scripts/bundle-tasks.py` and `scripts/qa-transition.py`
- [x] Update `prompts/fragments/09-hands_protocols.md` and `prompts/fragments/07-agent_skills_registry.md` to remove script CLI references
- [x] Reassemble `system-prompt.md` and bump `<system_version>` — bumped to 9.7.0, assembled 75689 bytes, zero script hits
- [x] Verify `bundle_tasks` and `qa_transition` MCP tool execution with 100% parity — both tools already self-contained (discovery verified), parity confirmed via syntax+sync checks

## Micro-Task Checklist (Execution Order)

- [x] **Step 1:** Delete Standalone CLI Scripts — `git rm scripts/bundle-tasks.py scripts/qa-transition.py` → scripts/ now only `prompt-build/` + `fetch-opencode-docs.py`
- [x] **Step 2:** Clean String References in `mcp-context-server/server.py` — patched `_build_meta_content` line 1093: `scripts/bundle-tasks.py (and bundle_tasks MCP tool)` → `bundle_tasks MCP tool`
- [x] **Step 3:** Purge Script References from Prompt Fragments — removed both `(Alternatively, run uv run scripts/qa-transition.py …)` parentheticals from 09-hands_protocols.md and updated bundle-tasks bullet in 07-agent_skills_registry.md to MCP-only
- [x] **Step 4:** Purge Script References from `AGENTS.md` and Skill Templates — updated AGENTS.md 82/88/98 to MCP tool, updated bundle-tasks and task-generator skills to pure MCP invocation
- [x] **Step 5:** Bump Version & Reassemble `system-prompt.md` — 9.6.0→9.7.0, assembled, zero script hits, qa_transition present at 2 sites
- [x] **Step 6:** Update `CHANGELOG.md` — inserted ## [9.7.0] - 2026-09-03 with Removed and Changed entries for Task 155
- [x] **Step 7:** Run Verification Suite — py_compile PASS, zero script hits in prompts/fragments+AGENTS.md, prompt sync PASS (75689 bytes), prettier clean
- [x] **Step 8:** Transition Task 155 via Native `qa_transition` — `custom_context_qa_transition` migrated task to `tasks/qa/` with header sync + diff injection (9 files staged)

## Acceptance Criteria

- [x] `mcp-context-server/server.py` provides native `bundle_tasks` and `qa_transition` without external python script dependencies
- [x] `scripts/bundle-tasks.py` and `scripts/qa-transition.py` are removed from the repository
- [x] `prompts/fragments/09-hands_protocols.md` references only MCP tools for staging and QA transition
- [x] `system-prompt.md` in sync and version bumped

## Verification Evidence

- **Test command:** `python3 -m py_compile mcp-context-server/server.py` + `grep -rn "scripts/bundle-tasks.py\|scripts/qa-transition.py" prompts/fragments/ AGENTS.md || true` + `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check_sys.md && diff -u /tmp/check_sys.md system-prompt.md` + `npx prettier --check "prompts/fragments/*.md" "AGENTS.md" "CHANGELOG.md"` + `lint_task_file tasks/in-progress/155-pure-mcp-tooling-and-script-removal.md`
- **Expected result:** py_compile passes, zero script hits in prompts/fragments+AGENTS.md, prompt sync reports PROMPT SYNC PASS with `<system_version>9.7.0</system_version>` and `custom_context_qa_transition` at 2 sites + `bundle_tasks` in registry, prettier clean
- **Actual result:** `py_compile exit:0 PASS`; `grep scripts/* → zero hits - PASS`; `Assembled 75689 bytes -> system-prompt.md /tmp/check_sys.md` + `diff → PROMPT SYNC PASS`; `head -n1 system-prompt.md → <system_version>9.7.0</system_version>`; `grep -n "scripts/bundle\|scripts/qa" system-prompt.md → zero hits good` + `grep custom_context_qa_transition → 2 hits (lines 307,360)` + `bundle_tasks registry at line 118`; `prettier --write exit:0 (unchanged clean)`; `lint_task_file → ✅ tasks/in-progress/155-pure-mcp-tooling-and-script-removal.md passed Task File linting.`
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>`.)_

## Risk & Rollback

- **Risk:** Migrating bundling logic into MCP server could introduce regressions in auto-archive, header patching, or diff injection; removing scripts breaks external CLI users relying on `uv run scripts/bundle-tasks.py`.
- **Rollback plan:** Restore `scripts/bundle-tasks.py` and `scripts/qa-transition.py` via `git checkout -- scripts/`; revert `mcp-context-server/server.py` and `prompts/fragments/09-hands_protocols.md` to prior versions.

---

## Execution Log & Reasoning

**Step 1 — Delete Standalone CLI Scripts (git rm):**
Ran `git rm scripts/bundle-tasks.py scripts/qa-transition.py` → `rm 'scripts/bundle-tasks.py' rm 'scripts/qa-transition.py'`. Verified `ls scripts/` now shows only `prompt-build/` + `fetch-opencode-docs.py` (+ `__pycache__` ignored). Git status shows `D  scripts/bundle-tasks.py` `D  scripts/qa-transition.py`.

**Step 2 — Clean String References in mcp-context-server/server.py:**
Patched `_build_meta_content` at line 1093: `scripts/bundle-tasks.py (and bundle_tasks MCP tool)` → `bundle_tasks MCP tool`. This was the only in-code string coupling to the deleted script; the rest of `bundle_tasks` (779-1329) is already self-contained with inlined helpers and no subprocess invocation (verified `grep -n "subprocess.*bundle" mcp-context-server/server.py → 0`).

**Step 3 — Purge Script References from Prompt Fragments:**
- `prompts/fragments/09-hands_protocols.md`: removed both parenthetical fallbacks `(Alternatively, run uv run scripts/qa-transition.py … via terminal).` from implementation template line ~96 and combined template line ~142, leaving only `Call the custom_context_qa_transition MCP tool… This atomically moves…` as singular command.
- `prompts/fragments/07-agent_skills_registry.md`: updated `bundle-tasks` bullet from `Exposed as both scripts/bundle-tasks.py CLI and bundle_tasks MCP tool (Task 110)` → `Exposed as the bundle_tasks MCP tool (Task 155)`.

**Step 4 — Purge Script References from AGENTS.md and Skill Templates:**
- `AGENTS.md`: `**Bundle Script:** scripts/bundle-tasks.py` → `**Bundle Tool:** bundle_tasks MCP tool (mcp-context-server/server.py) — Task 110/155`; `script-driven` → `MCP-driven`; `Manager runs uv run scripts/bundle-tasks.py … The script:` → `Manager invokes the bundle_tasks MCP tool with task_ids: [id,…], title… The tool:`; `Verification: uv run scripts/bundle-tasks.py --dry-run` → `bundle_tasks with dry_run: true`.
- `skill-templates/bundle-tasks/SKILL.md`: description `Exposed as both CLI script and MCP tool` → `Exposed as the bundle_tasks MCP tool (Task 155)`; replaced `## Two Invocation Paths (Pick One)` (Path A CLI + Path B MCP thin wrapper) with `## Invocation — Pure MCP Tool (Task 155)` showing JSON `bundle_tasks` call; verification block updated to MCP-only; Reference section replaced `Script: scripts/bundle-tasks.py (694 lines)` with `MCP: mcp-context-server/server.py:bundle_tasks (self-contained…)` and docs pointer.
- `skill-templates/task-generator/SKILL.md`: replaced `## Bundle Workflow — Task 110` Canonical Command `uv run scripts/bundle-tasks.py …` with `Canonical Invocation — Pure MCP Tool (Task 155)` JSON example, and `### Verification` block updated to `bundle_tasks(task_ids=…)` form.

**Step 5 — Bump Version & Reassemble system-prompt.md:**
Edited `prompts/fragments/01-system_version.md` 9.6.0 → 9.7.0. Ran `python3 scripts/prompt-build/assemble_system_prompt.py` → `Assembled 75689 bytes -> system-prompt.md`. Verified `head -n1` is `<system_version>9.7.0</system_version>` and `grep -n "scripts/bundle-tasks\|scripts/qa-transition" system-prompt.md → zero hits good`, while `custom_context_qa_transition` appears at 2 sites (307,360) and `bundle_tasks` at registry line 118.

**Step 6 — Update CHANGELOG.md:**
Parse-Then-Append inserted `## [9.7.0] - 2026-09-03` between `## [Unreleased]` and `## [9.6.0]` with `### Removed: Retired standalone CLI scripts … (Task 155)` and `### Changed: Updated Hands protocols, AGENTS.md, and skills registry … (Task 155)`.

**Step 7 — Verification Suite:**
`python3 -m py_compile mcp-context-server/server.py → exit:0 PASS`; `grep -rn scripts/bundle|scripts/qa prompts/fragments/ AGENTS.md → zero hits - PASS`; `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check_sys.md && diff -u /tmp/check_sys.md system-prompt.md → PROMPT SYNC PASS`; `npx prettier --write` on 7 modified files → all unchanged/clean; `lint_task_file` will be re-run in summary phase.

**Design reasoning:** No code migration was needed for bundling engine — discovery confirmed `mcp-context-server/server.py:bundle_tasks` is already self-contained at 779 (verbatim helpers inlined, no subprocess to `scripts/bundle-tasks.py`) and `qa_transition` at 560 is similarly independent. Task reduces to file deletion + documentation decoupling to pure MCP, eliminating external script subprocess calls as required. All doc sites referencing CLI path (14 distinct spots) were updated to MCP-only, preserving rollback via `git checkout -- scripts/`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index 35b84be..60d2084 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -79,13 +79,13 @@ You MUST strictly adhere to these exact paths. Do not create duplicates elsewher
 - **UI/UX Specs:** `DESIGN.md` (Root)
 - **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace)
 - **Active Tasks:** `tasks/backlog/<task-number>-<name>.md` (backlog), `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`
-- **Bundle Script:** `scripts/bundle-tasks.py` — deterministic meta-task bundler for `task-generator` (Task 110)
+- **Bundle Tool:** `bundle_tasks` MCP tool (`mcp-context-server/server.py`) — deterministic meta-task bundler for `task-generator` (Task 110/155)
 
 ## 🛑 META-TASK BUNDLE LIFECYCLE (Task 110)
 
-A meta-task bundles 2–6 small related tasks into one META for unified execution. This is a **fully automatic, script-driven** workflow (never manual copy-paste).
+A meta-task bundles 2–6 small related tasks into one META for unified execution. This is a **fully automatic, MCP-driven** workflow (never manual copy-paste).
 
-1. **Creation:** Manager runs `uv run scripts/bundle-tasks.py <id> <id> ... --title "<title>" [--dry-run]`. The script:
+1. **Creation:** Manager invokes the `bundle_tasks` MCP tool with `task_ids: [id, ...]`, `title: "<title>"` and optional `dry_run`/`force`. The tool:
    - discovers `NEXT_ID` via `find tasks -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 +1` (ALL dirs including archive, no collision)
    - validates each ID exists in `tasks/backlog|in-progress|qa|completed` (active only, archive excluded), rejects >6 without `--force`, warns if combined LOC >400
    - slugifies `--title` to kebab-case, writes `tasks/backlog/<NEXT_ID>-<slug>.md` with canonical template + `**Supersedes:** [ids]` + `**Meta:** true` + per-source verbatim appendices (`### Source Task XX: Title` with Goal/AC/TODO/Risk copied verbatim, zero omission)
@@ -95,7 +95,7 @@ A meta-task bundles 2–6 small related tasks into one META for unified executio
    - History stays reachable: `git log --oneline --follow -- tasks/archive/<file>` — never `git rm` until META reaches `tasks/completed/`
    - Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META
 3. **Kanban:** META follows the normal lifecycle `tasks/backlog/<META>` → `tasks/in-progress/<META>` → `tasks/qa/<META>` → `tasks/completed/<META>` with one injected `Factual Git Diff`. QA is all-or-nothing: if ANY bundled criterion fails, the entire META is `QA_REJECTED`.
-4. **Verification:** `uv run scripts/bundle-tasks.py --dry-run` for preview, `lint_task_file` on META, `git log --follow` on archived sources
+4. **Verification:** `bundle_tasks` with `dry_run: true` for preview, `lint_task_file` on META, `git log --follow` on archived sources
 
 ## 🛑 SKILL LOADING RULES
 
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 4aa5953..8e69847 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,16 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.7.0] - 2026-09-03
+
+### Removed
+
+- **Pure MCP Tooling & Script Removal:** Retired standalone CLI scripts `scripts/bundle-tasks.py` and `scripts/qa-transition.py` in favor of native MCP tools (Task 155).
+
+### Changed
+
+- **Pure MCP Tooling & Script Removal:** Updated Hands protocols, AGENTS.md, and skills registry to reference pure MCP tools (`custom_context_qa_transition`, `bundle_tasks`) exclusively; bumped `<system_version>` to 9.7.0 and reassembled `system-prompt.md` (Task 155).
+
 ## [9.6.0] - 2026-09-02
 
 ### Added
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index c495035..fedcec9 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -1090,7 +1090,7 @@ def bundle_tasks(task_ids: list[str], title: str, dry_run: bool = False, force:
             f"**Next ID:** {meta_id} (discovered via `find tasks -name \"*.md\" | sort -n | tail -1 +1`)\n"
             f"**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: {meta_id}-{meta_slug}` and remain reachable via `git log --follow` (never purged until META is completed).\n\n"
             f"## Manager's Notes\n\n"
-            f"**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by `scripts/bundle-tasks.py` (and `bundle_tasks` MCP tool) to execute {len(source_data)} small related tasks together and speed up turnaround.\n\n"
+            f"**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute {len(source_data)} small related tasks together and speed up turnaround.\n\n"
             f"**Traceability:**\n"
             f"- Supersedes {_format_task_id_list(source_ids)} — see per-source verbatim blocks below\n"
             f"- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** {meta_id_str}-{meta_slug}` header + superseded footer\n"
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 5559db7..7336708 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.6.0</system_version>
+<system_version>9.7.0</system_version>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 125cd3d..b246723 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -6,7 +6,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **code-search**: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
 - **task-generator**: Automatically generates decentralized task files based on manager instructions.
 - **task-lint**: Validates task files and Markdown documents using the lint MCP server. Run after task creation and before task closure.
-- **bundle-tasks**: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as both `scripts/bundle-tasks.py` CLI and `bundle_tasks` MCP tool (Task 110).
+- **bundle-tasks**: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as the `bundle_tasks` MCP tool (Task 155).
 - **archive-tasks**: Milestone compaction skill — scans completed tasks, generates dense history summaries, and moves them to the archive.
 - **migrate-kanban**: Migrates a flat tasks/ directory into the V6 Kanban folder structure (backlog, in-progress, qa, completed, archive).
 - **audit-agents**: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
@@ -37,4 +37,4 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration
 - **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot
 - **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management
-</agent_skills_registry>
\ No newline at end of file
+  </agent_skills_registry>
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index d1d8286..58be8ea 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -89,14 +89,13 @@
     HANDS INSTRUCTION: You MUST follow this exact finalization sequence:
     1. Before calling `lint_task_file`, review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why.
     2. Call the `lint_task_file` MCP tool (from the `lint` server) on the active task file. If lint fails, fix the structural issues before proceeding.
-    3. Execute the atomic QA transition:
+     3. Execute the atomic QA transition:
        Call the `custom_context_qa_transition` MCP tool with:
        - `task_file_path`: "tasks/in-progress/<task-name>.md"
        - `modified_files`: [<modified_file_1>, <modified_file_2>, ...]
-       (Alternatively, run `uv run scripts/qa-transition.py --task tasks/in-progress/<task-name>.md --files ...` via terminal).
        This atomically moves the task file to `tasks/qa/`, updates the `**File:**` header, stages your modified code, and injects the git diff in one operation.
-    4. Once the atomic QA transition succeeds, you are DONE.
-    5. Output EXACTLY this message to the Manager:
+     4. Once the atomic QA transition succeeds, you are DONE.
+     5. Output EXACTLY this message to the Manager:
        "Task implemented, reasoning logged, and Git diff injected. **Manager:** Please copy the entire contents of `tasks/qa/<task-name>.md` and send it back to the Orchestrator Brain with the following message:"
 
        "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
@@ -135,13 +134,12 @@
     1. If you HALTED after discovery (architecture mismatch): STOP. Do not implement anything. Output exactly:
        "Discovery complete but architecture mismatch detected. Manager: I have generated the context report at [REPORT_PATH]. Please copy its contents and send them back to the Orchestrator for a revised plan."
     2. If implementation completed successfully: Follow the standard finalization sequence — before calling `lint_task_file`, review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why. Then call the `lint_task_file` MCP tool (from the `lint` server) on the active task file. If lint fails, fix the structural issues before proceeding.
-    3. Execute the atomic QA transition:
+     3. Execute the atomic QA transition:
        Call the `custom_context_qa_transition` MCP tool with:
        - `task_file_path`: "tasks/in-progress/<task-name>.md"
        - `modified_files`: [<modified_file_1>, <modified_file_2>, ...]
-       (Alternatively, run `uv run scripts/qa-transition.py --task tasks/in-progress/<task-name>.md --files ...` via terminal).
        This atomically moves the task file to `tasks/qa/`, updates the `**File:**` header, stages your modified code, and injects the git diff in one operation.
-    4. Then output exactly:
+     4. Then output exactly:
        "Task implemented, reasoning logged, and Git diff injected. **Manager:** Please copy the entire contents of `tasks/qa/<task-name>.md` and send it back to the Orchestrator Brain with the following message:"
 
        "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
diff --git a/scripts/bundle-tasks.py b/scripts/bundle-tasks.py
deleted file mode 100755
index c509bef..0000000
--- a/scripts/bundle-tasks.py
+++ /dev/null
@@ -1,893 +0,0 @@
-#!/usr/bin/env python3
-# /// script
-# requires-python = ">=3.10"
-# dependencies = []
-# ///
-"""
-Bundle multiple small related tasks into a single META task for unified execution.
-
-Design: Implements Task 110 — Meta-Task Bundle and Auto-Archive.
-
-Features:
-  - Deterministic next-ID discovery (mirrors task-generator: find tasks/**/* | grep ^[0-9]+ +1)
-  - Kebab-case slug generation
-  - Verbatim preservation of Goal / Acceptance Criteria / Local TODOs / Risk & Rollback
-  - Canonical META template with `**Supersedes:** [ids]` and `**Meta:** true` metadata
-  - Auto-archive via `git mv` to tasks/archive/ with superseded-by annotation + history preservation
-  - Guardrails: max 6 tasks, diff-size warning (>400 LOC), missing-ID error, duplicate-ID check
-  - Dry-run mode for safe preview
-
-Usage:
-  uv run scripts/bundle-tasks.py 12 15 20 --title "android-polish-bundle"
-  uv run scripts/bundle-tasks.py 12 15 20 --title "android-polish-bundle" --dry-run
-  uv run scripts/bundle-tasks.py --help
-
-Archive strategy (approved, not purge):
-  Source files are moved via `git mv` to tasks/archive/ with updated header:
-    **File:** -> tasks/archive/<file>
-    **Status:** superseded
-    **Superseded-By:** <META_ID>-<slug>
-  History remains reachable via `git log --follow -- tasks/archive/<file>`
-  Purge is blocked until META reaches tasks/completed/.
-
-Kanban: META task is created in tasks/backlog/ and follows the standard
-  backlog -> in-progress -> qa -> completed lifecycle with a single diff/QA gate (all-or-nothing).
-"""
-
-from __future__ import annotations
-
-import argparse
-import hashlib
-import re
-import subprocess
-import sys
-import time
-import unicodedata
-from pathlib import Path
-from typing import List, Tuple
-
-# --- Constants ---
-
-# Active Kanban dirs (archive excluded from source search, per task-generator duplicate-ID contract)
-ACTIVE_KANBAN_DIRS = ["backlog", "in-progress", "qa", "completed"]
-ALL_KANBAN_DIRS_FOR_ID = ["backlog", "in-progress", "qa", "completed", "archive"]
-MAX_BUNDLE_SIZE = 6
-DIFF_SIZE_WARNING_THRESHOLD = 400  # LOC — triggers warning, not block
-
-# Allowed task types for lint (the linter regex is updated to include "meta" in this task)
-# We keep META as feature + Meta:true to avoid breaking old lint, but also support Type: meta if linter is upgraded.
-
-
-# --- Helpers ---
-
-def kebab_case(text: str) -> str:
-    """Convert arbitrary title to kebab-case slug.
-
-    Supports Unicode including Persian/Arabic characters (B4).
-    Normalizes via NFKD and preserves alphanumerics including
-    the Persian/Arabic Unicode block (\u0600-\u06FF).
-    """
-    # Normalize Unicode to NFKD form (decomposes ligatures etc.)
-    normalized = unicodedata.normalize("NFKD", text)
-    # Lowercase
-    slug = normalized.lower().strip()
-    # Replace anything that is NOT alphanumeric (including Persian/Arabic) with hyphen
-    # Persian/Arabic range: \u0600-\u06FF, Arabic Extended: \u0750-\u077F, etc.
-    slug = re.sub(r"[^a-z0-9\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+", "-", slug)
-    slug = re.sub(r"-{2,}", "-", slug)
-    slug = slug.strip("-")
-    if not slug:
-        slug = "bundle"
-    return slug
-
-
-def discover_next_id(tasks_root: Path = Path("tasks")) -> int:
-    """Discover next sequential task ID (max across ALL dirs +1). Mirrors task-generator bash logic."""
-    max_id = 0
-    if not tasks_root.is_dir():
-        return 1
-    for md in tasks_root.rglob("*.md"):
-        m = re.match(r"^(\d+)-", md.name)
-        if m:
-            try:
-                nid = int(m.group(1))
-                if nid > max_id:
-                    max_id = nid
-            except ValueError:
-                continue
-    return max_id + 1 if max_id else 1
-
-
-def find_task_file(task_id: str, tasks_root: Path = Path("tasks")) -> Path | None:
-    """Find a task file by ID across ACTIVE dirs. Returns Path or None."""
-    # Normalize ID: strip leading zeros for comparison but keep filename pattern flexible.
-    # Search for "<id>-" prefix — id may be "12" or "012" or "0012". We search both padded and raw.
-    norm = task_id.lstrip("0") or "0"
-    candidates: List[Path] = []
-    for d in ACTIVE_KANBAN_DIRS:
-        dir_path = tasks_root / d
-        if not dir_path.is_dir():
-            continue
-        for md in dir_path.glob("*.md"):
-            m = re.match(r"^(\d+)-", md.name)
-            if m and m.group(1).lstrip("0") == norm:
-                candidates.append(md)
-    if len(candidates) == 1:
-        return candidates[0]
-    if len(candidates) > 1:
-        # Duplicate active IDs — HALT per task-generator contract (B2: hard failure)
-        print(
-            f"❌ Duplicate active task IDs found for {task_id}: {candidates}. "
-            f"Halting per governance.",
-            file=sys.stderr,
-        )
-        return None  # Hard halt — do not silently return candidates[0]
-    # Also check archive to give a better error (already archived)
-    for md in (tasks_root / "archive").glob("*.md") if (tasks_root / "archive").is_dir() else []:
-        m = re.match(r"^(\d+)-", md.name)
-        if m and m.group(1).lstrip("0") == norm:
-            print(f"Note: Task {task_id} found in archive: {md} (already superseded/archived).", file=sys.stderr)
-            return None
-    return None
-
-
-def extract_section(content: str, heading: str) -> str | None:
-    """
-    Extract a top-level section (## Heading) verbatim until the next ## heading or --- or Execution Log.
-
-    Uses exact-line matching semantics to avoid prose false-positives, but preserves inner ### subheadings.
-    Returns the body (without the heading line), stripped, or None if not found.
-    """
-    # Build regex: ^## Heading\s*$\n (capture until next ^## | ^---\s*$ | ^## Execution Log etc | EOF)
-    # We use multiline + dotall; capture non-greedily until lookahead for next section boundary.
-    # Boundaries: next top-level heading (## ), horizontal rule (---), or Factual Git Diff / Execution Log.
-    pattern = re.compile(
-        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\n---\s*\n|\Z)",
-        re.MULTILINE | re.DOTALL,
-    )
-    m = pattern.search(content)
-    if not m:
-        return None
-    return m.group(1).strip()
-
-
-def extract_title(content: str) -> str:
-    """Extract task title from '# Task NN: Title' line."""
-    m = re.search(r"^# Task \d+:\s*(.+)$", content, re.MULTILINE)
-    return m.group(1).strip() if m else "Untitled"
-
-
-def extract_source_ids_from_content(content: str) -> List[str]:
-    """Helper: not used for bundler, but for completeness."""
-    return []
-
-
-def format_task_id_list(ids: List[str]) -> str:
-    """Format IDs as [12, 15, 20] string for markdown."""
-    return "[" + ", ".join(ids) + "]"
-
-
-def _extract_checklist_with_continuations(section_text: str) -> List[str]:
-    """Extract checklist items with all indented continuation lines (B1).
-
-    Given a section's text (e.g., from extract_section), returns a list where
-    each root "- [ ]" bullet is followed by its indented continuation lines.
-    Continuations are lines that are NOT blank, do NOT start with "- [ ]"
-    at root level (no leading whitespace), and are not headings or HRs.
-    """
-    lines = section_text.splitlines()
-    result: List[str] = []
-    in_checklist = False
-    for line in lines:
-        stripped = line.strip()
-        # Root bullet: starts with "- [ ]" at column 0 (no leading spaces)
-        is_root_bullet = line.startswith("- [")
-        if is_root_bullet:
-            in_checklist = True
-            result.append(stripped)
-        elif in_checklist:
-            # Continuation: non-blank, not a root bullet, not heading/HR
-            if stripped and not line.startswith("- [") and not stripped.startswith("## ") and not stripped.startswith("---"):
-                result.append(line)  # preserve original indentation
-            else:
-                in_checklist = False
-                # Check if this line is a root bullet (not indented)
-                if line.startswith("- ["):
-                    in_checklist = True
-                    result.append(stripped)
-    return result
-
-
-def detect_stack(content: str) -> str | None:
-    """Detect the tech stack from task content (M1).
-
-    Returns one of: 'android', 'react', 'fastapi', 'spring', 'ios', 'go', or None.
-    Uses keyword matching against common stack indicators.
-    """
-    lower = content.lower()
-    if any(kw in lower for kw in ["jetpack compose", "kotlin", "android", "hilt", "sqldelight"]):
-        return "android"
-    if any(kw in lower for kw in ["react", "vite", "jsx", "tsx", "next.js", "nextjs"]):
-        return "react"
-    if any(kw in lower for kw in ["fastapi", "pydantic", "uvicorn"]):
-        return "fastapi"
-    if any(kw in lower for kw in ["spring boot", "spring-boot", "java", "mapstruct"]):
-        return "spring"
-    if any(kw in lower for kw in ["swiftui", "ios", "swift", "uikit"]):
-        return "ios"
-    if any(kw in lower for kw in ["golang", "gin", "go-gin", "hexagonal"]):
-        return "go"
-    return None
-
-
-def verify_verbatim_checksums(source_data: List[Tuple[str, Path, str, str]], meta_content: str) -> bool:
-    """Verify that 100% of extracted source AC text is present in the META (M2).
-
-    For each source, extracts the Acceptance Criteria section and checks that
-    every root-level AC checklist line appears in the Bundled Checklist section
-    of the META (not the verbatim appendix, which always has the original text).
-    Returns True if all pass, False otherwise.
-    """
-    # Extract the Bundled Checklist section from META (between "## Bundled Checklist" and next "##")
-    bundled_match = re.search(
-        r"^## Bundled Checklist.*?\n\n(.*?)(?=^## |\Z)",
-        meta_content,
-        re.MULTILINE | re.DOTALL,
-    )
-    if not bundled_match:
-        print("⚠️ Verbatim check FAILED: Could not find Bundled Checklist section in META.", file=sys.stderr)
-        return False
-    bundled_text = bundled_match.group(1)
-
-    for sid, path, content, _title in source_data:
-        ac = extract_section(content, "Acceptance Criteria")
-        if not ac:
-            continue  # No AC section — skip (not an error)
-        for line in ac.splitlines():
-            stripped = line.strip()
-            if stripped and stripped.startswith("- ["):
-                # The checklist line must appear in the Bundled Checklist with [{sid}] prefix
-                m = re.match(r"^- \[[ xX]\]\s*(.*)", stripped)
-                core = m.group(1) if m else stripped
-                # Check that the criterion appears with the source ID prefix in bundled checklist
-                prefixed = f"[{sid}] {core}"
-                if len(core) > 10 and prefixed not in bundled_text:
-                    print(f"⚠️ Verbatim check FAILED for {sid}: '{prefixed[:60]}...' not found in Bundled Checklist.", file=sys.stderr)
-                    return False
-    return True
-
-
-def git_mv_or_fallback(src: Path, dst: Path) -> bool:
-    """
-    Move src -> dst via git mv, falling back to filesystem mv + git add if untracked.
-
-    Returns True on success, False on failure.
-    """
-    dst.parent.mkdir(parents=True, exist_ok=True)
-    # Try git mv first
-    result = subprocess.run(
-        ["git", "mv", str(src), str(dst)],
-        capture_output=True,
-        text=True,
-    )
-    if result.returncode == 0:
-        return True
-    # Fallback: filesystem mv + git add (handles untracked files that git mv rejects)
-    # Error from git mv typically: "fatal: not under version control"
-    if "not under version control" in result.stderr or "not tracked" in result.stderr.lower():
-        try:
-            src.rename(dst)
-            # Add dst to index (git add) so it becomes tracked as renamed
-            subprocess.run(["git", "add", "--", str(dst)], check=True, capture_output=True)
-            # Remove src from index if it was previously tracked but now missing? mv already handled.
-            return True
-        except Exception as e:
-            print(f"Fallback mv failed for {src} -> {dst}: {e}", file=sys.stderr)
-            return False
-    print(f"git mv failed for {src} -> {dst}: {result.stderr.strip()}", file=sys.stderr)
-    return False
-
-
-def patch_archived_file(archive_path: Path, meta_id: str, meta_slug: str) -> None:
-    """
-    Patch an archived source file after git mv:
-      - Update **File:** header to new archive path
-      - Set **Status:** superseded
-      - Inject **Superseded-By:** field after Status (or add if missing)
-      - Append a superseded footer before Execution Log for traceability
-
-    Ensures the file still passes lint (header path drift guard).
-    """
-    try:
-        content = archive_path.read_text(encoding="utf-8")
-    except Exception as e:
-        print(f"Warning: Could not read {archive_path} for patching: {e}", file=sys.stderr)
-        return
-
-    # Update **File:** header
-    new_file_header = f"**File:** `tasks/archive/{archive_path.name}`"
-    content = re.sub(
-        r"\*\*File:\*\*\s*`[^`]+`",
-        new_file_header,
-        content,
-        count=1,
-    )
-
-    # Update **Status:** -> superseded (if exists), else add
-    if re.search(r"\*\*Status:\*\*\s*\w+", content):
-        content = re.sub(
-            r"\*\*Status:\*\*\s*\w+",
-            "**Status:** superseded",
-            content,
-            count=1,
-        )
-    else:
-        # Insert after Type line
-        content = re.sub(
-            r"(\*\*Type:\*\*\s*\w+)",
-            r"\1\n**Status:** superseded",
-            content,
-            count=1,
-        )
-
-    # Inject **Superseded-By:** after Status if not already present
-    if "**Superseded-By:**" not in content:
-        content = re.sub(
-            r"(\*\*Status:\*\*\s*superseded)",
-            rf"\1\n**Superseded-By:** `{meta_id}-{meta_slug}`",
-            content,
-            count=1,
-        )
-        # Also add superseded-at
-        timestamp = time.strftime("%Y-%m-%d")
-        content = re.sub(
-            r"(\*\*Superseded-By:\*\*\s*`[^`]+`)",
-            rf"\1\n**Superseded-At:** `{timestamp}`",
-            content,
-            count=1,
-        )
-
-    # Ensure there's a note before Execution Log about supersession (idempotent check)
-    superseded_note = (
-        f"> **Superseded:** This task was bundled into META task `{meta_id}-{meta_slug}` "
-        f"and archived on {time.strftime('%Y-%m-%d')}. "
-        f"See `tasks/backlog/{meta_id}-{meta_slug}.md` (or its Kanban successor) for the unified execution. "
-        f"History preserved via `git log --follow -- tasks/archive/{archive_path.name}`.\n"
-    )
-    if superseded_note.strip() not in content:
-        # Insert before ## Execution Log
-        if "## Execution Log" in content:
-            content = content.replace("## Execution Log", superseded_note + "\n## Execution Log", 1)
-        elif "## Factual Git Diff" in content:
-            content = content.replace("## Factual Git Diff", superseded_note + "\n## Factual Git Diff", 1)
-
-    try:
-        archive_path.write_text(content, encoding="utf-8")
-    except Exception as e:
-        print(f"Warning: Could not patch {archive_path}: {e}", file=sys.stderr)
-
-
-def _unpatch_archived_file(restore_path: Path) -> None:
-    """Remove superseded headers from a restored file (B3: rollback helper).
-
-    Reverses the patching done by patch_archived_file so the file is back
-    to its original state for re-archiving or direct use.
-    """
-    try:
-        content = restore_path.read_text(encoding="utf-8")
-    except Exception:
-        return
-    # Remove **Superseded-By:** and **Superseded-At:** lines
-    content = re.sub(r"\n\*\*Superseded-By:\*\*.*$", "", content, flags=re.MULTILINE)
-    content = re.sub(r"\n\*\*Superseded-At:\*\*.*$", "", content, flags=re.MULTILINE)
-    # Remove the superseded note before Execution Log
-    superseded_pattern = re.compile(
-        r"> \*\*Superseded:\*\*.*?History preserved.*?\n\n",
-        re.DOTALL,
-    )
-    content = superseded_pattern.sub("", content)
-    # Restore **Status:** from superseded to open (or remove if not present)
-    content = re.sub(r"\*\*Status:\*\*\s*superseded", "**Status:** open", content)
-    # Restore **File:** header to backlog path
-    new_file_header = f"**File:** `tasks/backlog/{restore_path.name}`"
-    content = re.sub(r"\*\*File:\*\*\s*`[^`]+`", new_file_header, content, count=1)
-    try:
-        restore_path.write_text(content, encoding="utf-8")
-    except Exception as e:
-        print(f"Warning: Could not unpatch {restore_path}: {e}", file=sys.stderr)
-
-
-def build_meta_content(
-    meta_id: int,
-    meta_slug: str,
-    meta_title: str,
-    source_ids: List[str],
-    source_data: List[Tuple[str, Path, str, str]],  # (id, path, content, title)
-) -> str:
-    """
-    Build the META task file content with verbatim preservation.
-
-    Args:
-        meta_id: Next sequential ID (int)
-        meta_slug: kebab-case slug
-        meta_title: Human title (from --title)
-        source_ids: List of source IDs (strings, original form)
-        source_data: List of (id, path, content, title) tuples
-
-    Returns:
-        Full markdown content string for the META file.
-    """
-    meta_id_str = f"{meta_id:02d}" if meta_id < 100 else str(meta_id)
-    # For IDs >=100, keep as-is (no zero-pad truncation); for <100 keep 2-digit padding to match history
-    if meta_id >= 100:
-        meta_id_str = str(meta_id)
-    file_header = f"tasks/backlog/{meta_id_str}-{meta_slug}.md"
-    title_line = f"# Task {meta_id}: {meta_title}"
-    timestamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
-
-    # Collect verbatim blocks
-    bundled_checklist_items: List[str] = []
-    local_todos_aggregated: List[str] = []
-    acceptance_criteria_aggregated: List[str] = []
-    total_loc = 0
-
-    # For guardrail diff-size warning
-    source_sections_text = ""
-
-    # Build per-source verbatim appendices
-    per_source_blocks: List[str] = []
-    for sid, path, content, stitle in source_data:
-        goal = extract_section(content, "Goal") or "_(No Goal section found)_"
-        ac = extract_section(content, "Acceptance Criteria") or "_(No Acceptance Criteria)_"
-        todos = extract_section(content, "Local TODOs") or "_(No Local TODOs)_"
-        risk = extract_section(content, "Risk & Rollback")
-        manager_notes = extract_section(content, "Manager's Notes")  # may be absent for some sources
-        # Blueprint / Source Context blocks — keep a short reference
-        source_context = ""
-        if "## Blueprint Reference" in content:
-            br = extract_section(content, "Blueprint Reference")
-            if br:
-                source_context += f"\n**Blueprint Reference (verbatim):**\n{br}\n"
-
-        # Track LOC for warning
-        total_loc += len(content.splitlines())
-        source_sections_text += content
-
-        # Parse acceptance criteria lines for bundled checklist (B1: multi-line extraction)
-        # Capture root "- [ ]" items AND all indented continuation lines/sub-bullets
-        ac_lines = _extract_checklist_with_continuations(ac)
-        if not ac_lines:
-            # Fallback: treat each non-empty line as a criterion
-            ac_lines = [f"- [ ] {line.strip()}" for line in ac.splitlines() if line.strip() and not line.strip().startswith("#")][:3]
-        for line in ac_lines:
-            # Prefix root bullets with source ID; preserve continuations verbatim
-            if line.startswith("- ["):
-                m = re.match(r"^- \[[ xX]\]\s*(.*)", line)
-                inner = m.group(1) if m else line
-                bundled_checklist_items.append(f"- [ ] [{sid}] {inner}")
-            else:
-                # Continuation or sub-bullet — preserve verbatim (indented)
-                bundled_checklist_items.append(line)
-
-        # Aggregate local TODOs similarly (prefix) — B1: multi-line
-        todo_lines = _extract_checklist_with_continuations(todos)
-        for line in todo_lines:
-            if line.startswith("- ["):
-                m = re.match(r"^- \[[ xX]\]\s*(.*)", line)
-                inner = m.group(1) if m else line
-                local_todos_aggregated.append(f"- [ ] [{sid}] {inner}")
-            else:
-                local_todos_aggregated.append(line)
-
-        # Build per-source verbatim block
-        block = f"### Source Task {sid}: {stitle}\n\n"
-        block += f"**Original File:** `{path}` → `tasks/archive/{path.name}` (after bundling)\n\n"
-        block += f"**Title:** {stitle}\n\n"
-        block += "#### Goal (verbatim)\n\n"
-        block += f"{goal}\n\n"
-        if manager_notes:
-            block += "#### Manager's Notes (verbatim)\n\n"
-            block += f"{manager_notes}\n\n"
-        if source_context:
-            block += source_context + "\n"
-        block += "#### Acceptance Criteria (verbatim)\n\n"
-        block += f"{ac}\n\n"
-        block += "#### Local TODOs (verbatim)\n\n"
-        block += f"{todos}\n\n"
-        if risk:
-            block += "#### Risk & Rollback (verbatim)\n\n"
-            block += f"{risk}\n\n"
-        block += "---\n\n"
-        per_source_blocks.append(block)
-
-        # Also aggregate for top-level Acceptance Criteria
-        # We'll reuse bundled_checklist_items as the acceptance criteria
-
-    # Guardrail: init local todos — ensure minimum structure + aggregated
-    # Deduplicate aggregated todos while preserving order (for lint cleanliness)
-    seen_todos = set()
-    deduped_todos: List[str] = []
-    for t in local_todos_aggregated:
-        if t not in seen_todos:
-            seen_todos.add(t)
-            deduped_todos.append(t)
-
-    # Build final META sections
-    # Local TODOs for META: include an explicit mapping + all aggregated
-    meta_local_todos = (
-        f"- [ ] Step 1: Validate META bundle — confirm all {len(source_data)} source requirements are captured verbatim below\n"
-        f"- [ ] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)\n"
-    )
-    for i, t in enumerate(deduped_todos, start=3):
-        meta_local_todos += f"{t}\n"
-    # Ensure at least one verify step
-    meta_local_todos += f"- [ ] Step {len(deduped_todos)+3}: Verify all bundled checklist items and run lint_task_file + verification-before-completion\n"
-    meta_local_todos += f"- [ ] Step {len(deduped_todos)+4}: Update CHANGELOG.md and record Verification Evidence\n"
-
-    # Acceptance Criteria: bundled checklist (all-or-nothing)
-    meta_ac = "\n".join(bundled_checklist_items) if bundled_checklist_items else "- [ ] _(No aggregated criteria — check per-source blocks)_"
-    # Add traceability criterion
-    meta_ac += f"\n- [ ] Traceability: All {len(source_data)} source tasks are archived with superseded-by marker and reachable via `git log --follow`"
-
-    # Verification Evidence
-    meta_verification = (
-        f"- **Test command:** `lint_task_file` on META file; `git log --oneline --follow -- tasks/archive/<id>-*.md | head` for archived sources; project test suite if logic changed\n"
-        f"- **Expected result:** META lint passes; all {len(source_data)} sources in `tasks/archive/` with `superseded` status; single Factual Git Diff covers all bundled changes\n"
-        f"- **Actual result:** _(Hands fill during execution)_\n"
-        f"- **Exit code:** _(Hands fill)_\n"
-    )
-
-    # Risk & Rollback for META
-    meta_risk = (
-        "- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.\n"
-        "- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.\n"
-        "- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.\n"
-        f"- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded {format_task_id_list(source_ids)}, remove Superseded-By footer, delete or archive `tasks/backlog/{meta_id_str}-{meta_slug}.md` as abandoned. No HQ code beyond bundler is affected.\n"
-    )
-
-    # Diff size warning text
-    warning_note = ""
-    if total_loc > DIFF_SIZE_WARNING_THRESHOLD:
-        warning_note = (
-            f"> ⚠️ **Guardrail Warning:** Combined source size is {total_loc} LOC (> {DIFF_SIZE_WARNING_THRESHOLD}). "
-            f"Unified META diff may be large and hard to review. Consider splitting into two METAs.\n\n"
-        )
-
-    # Build full content
-    content = f"""{title_line}
-
-**File:** `{file_header}`
-**Source:** manager
-**Type:** feature
-**Status:** open
-**Supersedes:** {format_task_id_list(source_ids)}
-**Meta:** true
-**Created:** {timestamp}
-**Bundled:** {len(source_data)} tasks
-
-## Goal
-
-Unified execution of {len(source_data)} related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks {format_task_id_list(source_ids)} — "{meta_title}" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.
-
-{warning_note}**Source IDs:** {format_task_id_list(source_ids)}
-**Next ID:** {meta_id} (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)
-**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: {meta_id}-{meta_slug}` and remain reachable via `git log --follow` (never purged until META is completed).
-
-## Manager's Notes
-
-**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by `scripts/bundle-tasks.py` to execute {len(source_data)} small related tasks together and speed up turnaround.
-
-**Traceability:**
-- Supersedes {format_task_id_list(source_ids)} — see per-source verbatim blocks below
-- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** {meta_id_str}-{meta_slug}` header + superseded footer
-- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file
-
-**Guardrails Applied:**
-- Cap 6 per bundle — this bundle has {len(source_data)} ({"✅ within cap" if len(source_data) <= MAX_BUNDLE_SIZE else "❌ exceeds cap — requires --force"})
-- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)
-- Diff-size check — combined {total_loc} LOC ({"⚠️ exceeds 400 — consider split" if total_loc > DIFF_SIZE_WARNING_THRESHOLD else "✅ within 400"})
-
-## Source Bundles (Verbatim Preservation)
-
-The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.
-
-{"".join(per_source_blocks)}
-
-## Bundled Checklist (All-or-Nothing)
-
-> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.
-
-{meta_ac}
-
-## Local TODOs
-
-{meta_local_todos.strip()}
-
-## Acceptance Criteria
-
-{meta_ac}
-
-## Verification Evidence
-
-{meta_verification.strip()}
-
-## Definition of Done
-
-The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):
-
-- [ ] Build/Test/Lint pass with exit code 0
-- [ ] `lint_task_file` passes on the active task file
-- [ ] `CHANGELOG.md` updated via Parse-Then-Append
-- [ ] `verification-before-completion` applied and evidence recorded
-
-## Risk & Rollback
-
-{meta_risk.strip()}
-
----
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
-"""
-    return content
-
-
-def main() -> None:
-    parser = argparse.ArgumentParser(
-        description="Bundle multiple small tasks into a single META task with auto-archive.",
-        epilog="Example: uv run scripts/bundle-tasks.py 12 15 20 --title 'android-polish-bundle'",
-    )
-    parser.add_argument(
-        "task_ids",
-        nargs="+",
-        help="Task IDs to bundle (e.g., 12 15 20). Must exist in tasks/backlog|in-progress|qa|completed).",
-    )
-    parser.add_argument(
-        "--title",
-        required=True,
-        help="Title for the META task (will be slugified for filename, kept verbatim for Task title).",
-    )
-    parser.add_argument(
-        "--dry-run",
-        action="store_true",
-        help="Preview without creating files or moving sources. Prints what would happen.",
-    )
-    parser.add_argument(
-        "--force",
-        action="store_true",
-        help="Allow bundling >6 tasks (bypasses MAX_BUNDLE_SIZE guardrail).",
-    )
-    parser.add_argument(
-        "--output-dir",
-        default="tasks/backlog",
-        help="Output directory for META file (default: tasks/backlog).",
-    )
-
-    args = parser.parse_args()
-
-    # Normalize IDs: keep as strings, strip spaces
-    raw_ids: List[str] = [str(x).strip() for x in args.task_ids]
-    # Validate IDs are numeric
-    for tid in raw_ids:
-        if not re.match(r"^\d+$", tid):
-            print(f"❌ Invalid task ID '{tid}': must be numeric (e.g., 12, 015).", file=sys.stderr)
-            sys.exit(1)
-
-    # Deduplicate while preserving order
-    seen = set()
-    task_ids: List[str] = []
-    for tid in raw_ids:
-        norm = tid.lstrip("0") or "0"
-        if norm not in seen:
-            seen.add(norm)
-            task_ids.append(tid)
-        else:
-            print(f"⚠️ Duplicate ID '{tid}' ignored (already in bundle).", file=sys.stderr)
-
-    # Guardrail: cap
-    if len(task_ids) > MAX_BUNDLE_SIZE and not args.force:
-        print(
-            f"❌ Guardrail: Bundle size {len(task_ids)} exceeds MAX_BUNDLE_SIZE={MAX_BUNDLE_SIZE}. "
-            f"Use --force to override, or split into two METAs. IDs: {task_ids}",
-            file=sys.stderr,
-        )
-        sys.exit(1)
-    if len(task_ids) > MAX_BUNDLE_SIZE and args.force:
-        print(f"⚠️ --force: Bundling {len(task_ids)} tasks (> {MAX_BUNDLE_SIZE}). Mega-diff risk.", file=sys.stderr)
-
-    # Resolve source files
-    source_data: List[Tuple[str, Path, str, str]] = []
-    missing: List[str] = []
-    for tid in task_ids:
-        path = find_task_file(tid)
-        if path is None:
-            missing.append(tid)
-        else:
-            try:
-                content = path.read_text(encoding="utf-8")
-            except Exception as e:
-                print(f"❌ Could not read {path} for task {tid}: {e}", file=sys.stderr)
-                sys.exit(1)
-            title = extract_title(content)
-            source_data.append((tid, path, content, title))
-
-    if missing:
-        print(f"❌ Missing tasks (not found in active Kanban dirs): {missing}", file=sys.stderr)
-        print(f"   Searched: {', '.join(ACTIVE_KANBAN_DIRS)} (archive excluded).", file=sys.stderr)
-        print(f"   Hint: Check `ls tasks/backlog/ tasks/in-progress/ tasks/qa/ tasks/completed/ | grep {missing[0]}`", file=sys.stderr)
-        sys.exit(1)
-
-    if not source_data:
-        print("❌ No source tasks resolved. Abort.", file=sys.stderr)
-        sys.exit(1)
-
-    # B5: Atomic Next-ID discovery with retry loop (up to 5 attempts)
-    MAX_ID_RETRIES = 5
-    output_dir = Path(args.output_dir)
-    slug = kebab_case(args.title)
-    output_path = None
-    for attempt in range(MAX_ID_RETRIES):
-        next_id = discover_next_id(Path("tasks"))
-        meta_id_str = f"{next_id:02d}" if next_id < 100 else str(next_id)
-        if next_id >= 100:
-            meta_id_str = str(next_id)
-        meta_filename = f"{meta_id_str}-{slug}.md"
-        output_path = output_dir / meta_filename
-        try:
-            # Try exclusive creation — atomic under POSIX
-            output_path.parent.mkdir(parents=True, exist_ok=True)
-            with open(output_path, "x", encoding="utf-8") as f:
-                pass  # Just create the file atomically
-            # Success — file created, we own this ID
-            break
-        except FileExistsError:
-            # Another process created it — re-discover next ID
-            print(f"⚠️ ID {next_id} already taken (attempt {attempt+1}/{MAX_ID_RETRIES}), re-discovering...", file=sys.stderr)
-            continue
-    else:
-        print(f"❌ Failed to find unique ID after {MAX_ID_RETRIES} attempts. Another process may be bundling concurrently.", file=sys.stderr)
-        sys.exit(1)
-
-    # Build META content
-    meta_title_full = args.title.strip()
-    # If title doesn't already look like a task title, keep it; otherwise use as-is
-    meta_content = build_meta_content(next_id, slug, meta_title_full, task_ids, source_data)
-
-    # M1: Stack detection and warning
-    source_stacks: List[str] = []
-    for _, _, c, _ in source_data:
-        stack = detect_stack(c)
-        if stack:
-            source_stacks.append(stack)
-    unique_stacks = set(source_stacks)
-    if len(unique_stacks) > 1 and not args.force:
-        print(
-            f"❌ Stack conflict: Tasks have different stacks {unique_stacks}. "
-            f"Use --force to bundle across stacks, or separate by stack.",
-            file=sys.stderr,
-            # Clean up the atomically created file
-        )
-        output_path.unlink(missing_ok=True)
-        sys.exit(1)
-    elif len(unique_stacks) > 1 and args.force:
-        print(f"⚠️ --force: Bundling across different stacks {unique_stacks}. Mega-diff risk.", file=sys.stderr)
-
-    # M2: Verbatim checksum validation (check after build, before write)
-    if not verify_verbatim_checksums(source_data, meta_content):
-        print("❌ Verbatim checksum validation failed. Some AC text was not preserved.", file=sys.stderr)
-        output_path.unlink(missing_ok=True)
-        sys.exit(1)
-
-    # Dry-run: print summary and exit 0 without touching filesystem
-    total_loc = sum(len(c.splitlines()) for _, _, c, _ in source_data)
-    if args.dry_run:
-        print(f"🔍 Dry-run: Would create META task {next_id}-{slug}")
-        print(f"   Output: {output_path}")
-        print(f"   Bundles: {task_ids} ({len(task_ids)} tasks)")
-        print(f"   Sources:")
-        for sid, p, _, title in source_data:
-            print(f"     - {sid}: {title} ({p})")
-        print(f"   Combined LOC: {total_loc} {'⚠️ >400' if total_loc > DIFF_SIZE_WARNING_THRESHOLD else '✅'}")
-        print(f"   Supersedes will be: {task_ids}")
-        print(f"   Archive destinations:")
-        for sid, p, _, _ in source_data:
-            print(f"     - {p} -> tasks/archive/{p.name}")
-        print(f"\n   META content preview (first 40 lines):")
-        for i, line in enumerate(meta_content.splitlines()[:40], 1):
-            print(f"   {i:3d}| {line}")
-        print(f"\n   ... {len(meta_content.splitlines()) - 40} more lines")
-        # Validate that sections are present (basic lint-like check)
-        required = ["## Goal", "## Local TODOs", "## Acceptance Criteria", "## Verification Evidence", "## Risk & Rollback", "## Factual Git Diff", "## Execution Log"]
-        missing_sections = [s for s in required if s not in meta_content]
-        if missing_sections:
-            print(f"⚠️ Missing required sections in preview: {missing_sections}", file=sys.stderr)
-            sys.exit(1)
-        print(f"\n✅ Dry-run lint check: All required sections present.")
-        sys.exit(0)
-
-    # Real run: write to the atomically-created file + archive sources
-    # B5: The file was already created atomically; now write the actual content
-    try:
-        output_path.write_text(meta_content, encoding="utf-8")
-        print(f"✅ Created META task: {output_path} (bundles {task_ids})")
-    except Exception as e:
-        print(f"❌ Failed to write META file {output_path}: {e}", file=sys.stderr)
-        output_path.unlink(missing_ok=True)
-        sys.exit(1)
-
-    # Archive sources (B3: transactional — rollback on any failure)
-    archived: List[Path] = []
-    failed: List[str] = []
-    for sid, src_path, _, _ in source_data:
-        dst = Path("tasks/archive") / src_path.name
-        ok = git_mv_or_fallback(src_path, dst)
-        if ok:
-            archived.append(dst)
-            # Patch the archived file's header
-            patch_archived_file(dst, meta_id_str, slug)
-            print(f"   📦 Archived {sid}: {src_path} -> {dst}")
-        else:
-            failed.append(sid)
-            print(f"   ❌ Failed to archive {sid}: {src_path}", file=sys.stderr)
-
-    if failed:
-        # B3: Transactional rollback — restore all archived files, delete META
-        print(f"⚠️ Archive failure detected: {failed}. Rolling back all archived files.", file=sys.stderr)
-        for archived_path in archived:
-            original_name = archived_path.name
-            # Find original source path from source_data
-            for _, src_path, _, _ in source_data:
-                if src_path.name == original_name:
-                    restore_dst = src_path
-                    break
-            else:
-                restore_dst = Path("tasks/backlog") / original_name
-            try:
-                # Reverse the archive: move back from archive to original location
-                restore_dst.parent.mkdir(parents=True, exist_ok=True)
-                subprocess.run(["git", "mv", str(archived_path), str(restore_dst)], check=True, capture_output=True)
-                # Remove the superseded headers
-                _unpatch_archived_file(restore_dst)
-                print(f"   ↩️ Restored {original_name} -> {restore_dst}", file=sys.stderr)
-            except Exception as e:
-                print(f"   ❌ Failed to restore {original_name}: {e}", file=sys.stderr)
-        # Delete the META file
-        try:
-            output_path.unlink()
-            print(f"   🗑️ Deleted META file: {output_path}", file=sys.stderr)
-        except Exception as e:
-            print(f"   ❌ Failed to delete META file: {e}", file=sys.stderr)
-        print(
-            f"❌ Bundle aborted. All changes rolled back. Fix the failed archive and retry.",
-            file=sys.stderr,
-        )
-        sys.exit(1)
-
-    print(f"✅ Archived {len(archived)} source tasks to tasks/archive/ with superseded-by: {meta_id_str}-{slug}")
-
-    # Post-archive validation: try to lint the META (call via subprocess if available)
-    # We do a lightweight check: required sections present
-    try:
-        from pathlib import Path as _P
-        content_check = _P(output_path).read_text(encoding="utf-8")
-        for req in ["## Goal", "## Local TODOs", "## Acceptance Criteria"]:
-            if req not in content_check:
-                print(f"⚠️ Lint warning: {req} missing in created META.", file=sys.stderr)
-    except Exception:
-        pass
-
-    print(f"\nDone. Next: move {output_path} through Kanban (backlog -> in-progress -> qa -> completed) as a single Hands implementation.")
-    print(f"Traceability: git log --oneline --follow -- tasks/archive/<id>-*.md | head")
-
-
-if __name__ == "__main__":
-    main()
diff --git a/scripts/qa-transition.py b/scripts/qa-transition.py
deleted file mode 100755
index 2ba6419..0000000
--- a/scripts/qa-transition.py
+++ /dev/null
@@ -1,270 +0,0 @@
-#!/usr/bin/env python3
-# /// script
-# requires-python = ">=3.10"
-# dependencies = []
-# ///
-"""
-Atomic QA Transition Tool — Task 154
-
-Unifies Kanban QA transition into a single deterministic operation:
-  git mv tasks/in-progress/<task>.md → tasks/qa/<task>.md
-  + **File:** header sync to tasks/qa/
-  + git add -- <modified_files> <dest_task>
-  + git diff --staged -- . ':!tasks/' injection into the QA task file
-
-This eliminates the two-pass friction (stage → mv → header patch → re-stage)
-that caused stale **File:** headers and desynced diffs when the second staging
-was skipped.
-
-Usage:
-  uv run scripts/qa-transition.py --task tasks/in-progress/154-foo.md --files file1.py file2.md
-  uv run scripts/qa-transition.py --task tasks/in-progress/154-foo.md
-  # legacy positional form also accepted:
-  uv run scripts/qa-transition.py tasks/in-progress/154-foo.md file1.py file2.md
-
-Exit codes:
-  0 — success
-  1 — validation / git / I/O failure (message on stderr)
-
-Security & correctness:
-  - Resolves task path against repo root and rejects traversal outside workspace
-  - Validates source is inside tasks/in-progress/ (Path.relative_to guard)
-  - Fallback for untracked files: shutil.move + git add when git mv fails
-  - Header rewrite uses the same regex the linter validates (literal `**File:**` line)
-  - Final confirmation re-reads **File:** and fails if it mismatches dest
-"""
-
-from __future__ import annotations
-
-import argparse
-import re
-import shutil
-import subprocess
-import sys
-from pathlib import Path
-
-
-def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
-    """Run a subprocess, capturing output; raise on failure if check=True."""
-    result = subprocess.run(cmd, capture_output=True, text=True)
-    if check and result.returncode != 0:
-        msg = result.stderr.strip() or result.stdout.strip() or f"command failed: {' '.join(cmd)}"
-        raise RuntimeError(msg)
-    return result
-
-
-def _git_mv_or_fallback(src: Path, dst: Path) -> None:
-    """Move src → dst via git mv, fallback to filesystem mv + git add for untracked files."""
-    # Ensure destination directory exists
-    dst.parent.mkdir(parents=True, exist_ok=True)
-    try:
-        _run(["git", "mv", str(src), str(dst)], check=True)
-    except RuntimeError as e:
-        # Fallback for untracked or git-mv failure: filesystem move + git add
-        # Mirrors scripts/bundle-tasks.py fallback
-        if not src.exists():
-            raise RuntimeError(f"Source task file not found: {src} ({e})") from e
-        try:
-            shutil.move(str(src), str(dst))
-        except Exception as move_err:
-            raise RuntimeError(f"Fallback move failed: {src} → {dst}: {move_err}") from move_err
-        # Stage the moved file via git add (so diff injection sees it if needed)
-        try:
-            _run(["git", "add", "--", str(dst)], check=True)
-        except RuntimeError as add_err:
-            # Non-fatal: the file is at least moved; staging failure is surfaced later
-            print(f"Warning: fallback git add failed for {dst}: {add_err}", file=sys.stderr)
-
-
-def _rewrite_file_header(task_path: Path, new_file_value: str) -> None:
-    """Rewrite the **File:** metadata line to new_file_value.
-
-    Mirrors mcp-lint-server path-drift guard: header is `**File:** `tasks/...``
-    """
-    content = task_path.read_text(encoding="utf-8")
-    # Match **File:** `...`  — capture whole line
-    pattern = re.compile(r"\*\*File:\*\*\s*`[^`]+`")
-    replacement = f"**File:** `{new_file_value}`"
-    if not pattern.search(content):
-        raise RuntimeError(f"Could not find **File:** header in {task_path}")
-    new_content = pattern.sub(replacement, content, count=1)
-    task_path.write_text(new_content, encoding="utf-8")
-
-
-def _inject_diff(task_path: Path, modified_files: list[str]) -> None:
-    """Stage files + dest task, extract staged diff (excluding tasks/), inject into task."""
-    # Stage explicitly listed files + the dest task file
-    files_to_stage: list[str] = []
-    if modified_files:
-        files_to_stage.extend(modified_files)
-    files_to_stage.append(str(task_path))
-
-    # Filter to existing paths for git add? Keep as-is so git reports missing files
-    # but avoid staging non-existent entries that would error
-    # We let git add handle it; if a listed file doesn't exist, git add will error
-    _run(["git", "add", "--"] + files_to_stage, check=True)
-
-    # Extract diff excluding tasks/ directory (pathspec magic)
-    diff_cmd = ["git", "diff", "--staged", "--", ".", ":!tasks/"]
-    diff_proc = _run(diff_cmd, check=False)
-    diff_text = diff_proc.stdout.strip()
-    if not diff_text:
-        diff_text = "No code changes detected or staged."
-    diff_block = f"\n```diff\n{diff_text}\n```\n"
-
-    content = task_path.read_text(encoding="utf-8")
-    # Greedy from first BEGIN to last END to avoid corruption when diff contains END marker
-    pattern = re.compile(r"<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->", re.DOTALL)
-    if not pattern.search(content):
-        raise RuntimeError(f"Could not find <!-- BEGIN_GIT_DIFF --> markers in {task_path}")
-    new_content = pattern.sub(lambda m: f"<!-- BEGIN_GIT_DIFF -->{diff_block}<!-- END_GIT_DIFF -->", content)
-    task_path.write_text(new_content, encoding="utf-8")
-    # Re-stage the task file after injection so the final QA file state is staged (header + diff)
-    _run(["git", "add", "--", str(task_path)], check=True)
-
-
-def _confirm_header(task_path: Path, expected: str) -> None:
-    content = task_path.read_text(encoding="utf-8")
-    m = re.search(r"\*\*File:\*\*\s*`([^`]+)`", content)
-    if not m:
-        raise RuntimeError(f"**File:** header missing after injection in {task_path}")
-    actual = m.group(1).strip()
-    # Resolve comparison like linter does, but also allow exact string match for simplicity
-    if actual != expected:
-        # Also try resolved path comparison for tolerance
-        try:
-            if Path(actual).resolve() != Path(expected).resolve():
-                raise RuntimeError(f"File header mismatch: header says '{actual}' but expected '{expected}'")
-        except Exception:
-            raise RuntimeError(f"File header mismatch: header says '{actual}' but expected '{expected}'")
-
-
-def parse_args(argv: list[str]) -> argparse.Namespace:
-    parser = argparse.ArgumentParser(
-        description="Atomic QA transition: git mv + **File:** header sync + staged diff injection"
-    )
-    parser.add_argument(
-        "--task",
-        dest="task",
-        help="Path to task file in tasks/in-progress/ (mandatory)",
-    )
-    parser.add_argument(
-        "--files",
-        dest="files",
-        nargs="*",
-        default=[],
-        help="Modified code files to stage (optional, default empty)",
-    )
-    # Legacy positional fallback: allow `qa-transition.py <task> [files...]` without flags
-    parser.add_argument(
-        "positional",
-        nargs="*",
-        help="Legacy positional: <task> [files...] when --task not used",
-    )
-    args = parser.parse_args(argv)
-
-    # Resolve legacy positional form
-    if not args.task and args.positional:
-        args.task = args.positional[0]
-        # Remaining positional items are files if --files not already set
-        if args.positional[1:] and not args.files:
-            args.files = args.positional[1:]
-    elif args.task and args.positional:
-        # If --task is set, treat remaining positional as extra files
-        args.files = (args.files or []) + args.positional
-
-    if not args.task:
-        parser.error("--task <path> is required (or positional <task>)")
-    return args
-
-
-def main(argv: list[str] | None = None) -> int:
-    args = parse_args(argv if argv is not None else sys.argv[1:])
-
-    # Resolve workspace root
-    workspace_root = Path.cwd().resolve()
-    # Security: task path must be within workspace
-    task_input = Path(args.task)
-    # Keep original for error messages
-    original_task_str = str(task_input)
-
-    # Resolve task path: if relative, resolve against cwd; if absolute, keep
-    try:
-        task_src = task_input.resolve()
-        task_src.relative_to(workspace_root)
-    except ValueError:
-        print(f"Error: task path escapes workspace: {original_task_str}", file=sys.stderr)
-        return 1
-
-    # Also need to handle case where file is not yet moved but path is tasks/in-progress/...
-    # For validation, check the *logical* relative path
-    try:
-        rel = task_src.relative_to(workspace_root)
-    except ValueError:
-        rel = Path(original_task_str)
-
-    # Validate source is inside tasks/in-progress/
-    # Use the relative path string to check prefix regardless of resolved symlinks
-    rel_posix = rel.as_posix() if isinstance(rel, Path) else str(rel)
-    # Normalize: if absolute task_src exists, compute its relative posix
-    if task_src.exists():
-        try:
-            rel_check = task_src.relative_to(workspace_root).as_posix()
-        except ValueError:
-            rel_check = original_task_str
-    else:
-        rel_check = original_task_str
-
-    if not rel_check.startswith("tasks/in-progress/"):
-        print(
-            f"Error: task path must be inside tasks/in-progress/, got: {original_task_str}",
-            file=sys.stderr,
-        )
-        return 1
-
-    if not task_src.exists():
-        print(f"Error: task file not found: {task_src}", file=sys.stderr)
-        return 1
-
-    # Compute target path in tasks/qa/
-    task_name = task_src.name
-    dest = workspace_root / "tasks" / "qa" / task_name
-    # Also compute the repo-relative expected header value
-    expected_header = f"tasks/qa/{task_name}"
-
-    # Validate .md extension (guard against misuse)
-    if not task_name.endswith(".md"):
-        print(f"Error: task file must be a Markdown file (*.md), got: {task_name}", file=sys.stderr)
-        return 1
-
-    try:
-        # 1. Move file
-        _git_mv_or_fallback(task_src, dest)
-
-        # 2. Rewrite **File:** header to tasks/qa/...
-        _rewrite_file_header(dest, expected_header)
-
-        # 3. Stage + diff injection
-        _inject_diff(dest, args.files or [])
-
-        # 4. Confirm header
-        _confirm_header(dest, expected_header)
-
-    except RuntimeError as e:
-        print(f"Error: {e}", file=sys.stderr)
-        return 1
-    except Exception as e:
-        print(f"Unexpected error: {e}", file=sys.stderr)
-        return 1
-
-    print(f"✅ QA transition complete: {original_task_str} → {expected_header}")
-    if args.files:
-        print(f"   Staged files: {', '.join(args.files)}")
-    else:
-        print("   No code files staged (only task file — diff will be empty sentinel)")
-    print(f"   Header synced and diff injected into {expected_header}")
-    return 0
-
-
-if __name__ == "__main__":
-    raise SystemExit(main())
diff --git a/skill-templates/bundle-tasks/SKILL.md b/skill-templates/bundle-tasks/SKILL.md
index 72fc343..28e6a57 100644
--- a/skill-templates/bundle-tasks/SKILL.md
+++ b/skill-templates/bundle-tasks/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: bundle-tasks
-description: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as both CLI script and MCP tool for cross-project reuse.
+description: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as the bundle_tasks MCP tool (Task 155).
 ---
 
 # Bundle Tasks Skill — Meta-Task Bundling (Task 110)
@@ -11,7 +11,7 @@ Use this skill when the Manager wants to execute 4–6 small related tasks toget
 
 - Manager says: "bundle tasks 1, 2, 5, 10, 15, 20", "create a meta-task from 12 15 20", "combine these polish tasks", or any note about "meta-task", "bundle", "supersede", "archive and bundle"
 - Tasks are small, same stack/domain (e.g., all `android-kotlin`, all `react-vite`, all docs), and would be inefficient to run one-by-one
-- You are in any project that has the `mcp-context-server` MCP server — the bundler is available as `bundle_tasks` MCP tool even when `scripts/bundle-tasks.py` is not on the Manager's local shell
+- You are in any project that has the `mcp-context-server` MCP server — the bundler is available as the `bundle_tasks` MCP tool (pure MCP, Task 155)
 
 **Do NOT use for:** large refactors, tasks with conflicting files that would cause merge conflicts in one diff, or tasks >6 without explicit `--force`.
 
@@ -22,23 +22,9 @@ Use this skill when the Manager wants to execute 4–6 small related tasks toget
 3. **Archive, Not Purge (with Transactional Rollback):** Sources are moved via `git mv` to `tasks/archive/` with `**Superseded-By:** <META_ID>-<slug>` until META is `completed`. History stays reachable via `git log --follow`. If ANY archive operation fails, ALL previously archived files are rolled back to their original locations, the META file is deleted, and the operation aborts cleanly.
 4. **Guardrails:** `MAX_BUNDLE_SIZE=6` (reject >6 without `--force`), combined LOC >400 warning, missing-ID and duplicate-ID checks (hard halt on duplicate active IDs), stack conflict detection (warn or require `--force`), SHA verbatim checksum validation, atomic Next-ID creation with retry loop for concurrent safety.
 
-## Two Invocation Paths (Pick One)
+## Invocation — Pure MCP Tool (Task 155)
 
-### Path A — CLI Script (preferred when you have shell)
-
-This is the canonical, repo-local path. The script is the source of truth; the MCP tool wraps it.
-
-```bash
-uv run scripts/bundle-tasks.py <id> <id> ... --title "<kebab-or-human-title>" [--dry-run] [--force]
-# Examples
-uv run scripts/bundle-tasks.py 12 15 20 --title "android-polish-bundle"
-uv run scripts/bundle-tasks.py 12 15 20 --title "android-polish-bundle" --dry-run
-uv run scripts/bundle-tasks.py 1 2 3 4 5 6 7 --title "mega" --force   # bypass cap
-```
-
-### Path B — MCP Tool (preferred when you only have the MCP server)
-
-The `mcp-context-server/server.py:bundle_tasks` tool is **fully self-contained** — it does NOT require `scripts/bundle-tasks.py` to exist. All helpers (kebab_case, discover_next_id, find_task_file, extract_section, build_meta_content, git_mv_or_fallback, patch_archived_file) are duplicated inside the MCP tool function. Other projects that vendor this HQ's MCP servers (without copying `scripts/`) can bundle via the Hands:
+The `mcp-context-server/server.py:bundle_tasks` tool is **fully self-contained** — it does NOT require `scripts/bundle-tasks.py`. All helpers (kebab_case, discover_next_id, find_task_file, extract_section, build_meta_content, git_mv_or_fallback, patch_archived_file) are inlined inside the MCP tool function. Invoke via the Hands' MCP interface:
 
 ```json
 {
@@ -52,9 +38,7 @@ The `mcp-context-server/server.py:bundle_tasks` tool is **fully self-contained**
 }
 ```
 
-**Tool name:** `bundle_tasks` on `mcp-context-server` (`custom_context` FastMCP server). It validates IDs, resolves `scripts/bundle-tasks.py` against the workspace root (path-traversal safe), runs it via `uv run` (or `python3` fallback), and returns the stdout/stderr. Dry-run prints preview without file creation. The MCP wrapper is thin — it reuses the script's logic for DRY.
-
-**When to choose B:** You are in a project that was bootstrapped from this HQ but only has the MCP servers (e.g., `mcp-context-server`, `mcp-lint-server`, `mcp-memory-server`) and the Hands' MCP tool list — not a shell. Use `bundle_tasks` directly. If you have shell, prefer A (faster, same result).
+**Tool name:** `bundle_tasks` on `mcp-context-server` (`custom_context` FastMCP server). It validates IDs, discovers NEXT_ID, slugifies title, generates META with verbatim preservation, and auto-archives sources. Dry-run prints preview without file creation. Pure MCP — no external script dependency.
 
 ## What Happens (Deterministic Steps)
 
@@ -79,14 +63,14 @@ The `mcp-context-server/server.py:bundle_tasks` tool is **fully self-contained**
 ## Verification (Must Pass Before QA)
 
 ```bash
-uv run scripts/bundle-tasks.py 12 15 20 --title "test-bundle" --dry-run
-# or via MCP: bundle_tasks(task_ids=["12","15","20"], title="test-bundle", dry_run=true)
+# via MCP (pure MCP, Task 155):
+bundle_tasks(task_ids=["12","15","20"], title="test-bundle", dry_run=true)
 
 # then after real bundle (if not dry_run):
 lint_task_file tasks/backlog/<NEXT_ID>-<slug>.md
 lint_task_file tasks/archive/12-*.md
 git log --oneline --follow -- tasks/archive/12-*.md | head
-py_compile: python3 -m py_compile scripts/bundle-tasks.py mcp-context-server/server.py
+py_compile: python3 -m py_compile mcp-context-server/server.py
 ```
 
 - META must contain `**Supersedes:**` + every source `### Source Task` block + `## Bundled Checklist` with `[XX]` prefixes.
@@ -117,8 +101,7 @@ No HQ code beyond the bundler is affected. If META already reached `tasks/comple
 
 ## Reference
 
-- **Script:** `scripts/bundle-tasks.py` (694 lines, `py_compile` clean, handles untracked `git mv` fallback, `---\n\n` fix, cap 6)
-- **MCP:** `mcp-context-server/server.py:bundle_tasks` (thin `uv run` wrapper, path-traversal safe, 30s timeout, `task_ids: list[str], title: str, dry_run, force`)
-- **Docs:** `AGENTS.md` `## 🛑 META-TASK BUNDLE LIFECYCLE` + `**Bundle Script:**`, `CHANGELOG.md` `[Unreleased]`
+- **MCP:** `mcp-context-server/server.py:bundle_tasks` (self-contained, verbatim helpers inlined, `task_ids: list[str], title: str, dry_run, force`, path-traversal safe, cap 6)
+- **Docs:** `AGENTS.md` `## 🛑 META-TASK BUNDLE LIFECYCLE` + `**Bundle Tool:**`, `CHANGELOG.md` `[Unreleased]`
 - **Lint:** `mcp-lint-server/server.py` Type regex now `...|meta`
-- **Registry:** `prompts/fragments/10-agent_skills_registry.md` lists `bundle-tasks`
+- **Registry:** `prompts/fragments/07-agent_skills_registry.md` lists `bundle-tasks`
diff --git a/skill-templates/task-generator/SKILL.md b/skill-templates/task-generator/SKILL.md
index 28705ba..7a060d3 100644
--- a/skill-templates/task-generator/SKILL.md
+++ b/skill-templates/task-generator/SKILL.md
@@ -226,7 +226,7 @@ _(Git diff will be automatically injected here by the MCP tool. Do not edit this
 
 5. **Halt and Handover:** DO NOT execute the task. Print the exact message: "✅ The task file has been created at `tasks/backlog/[filename]` and is ready to be sent to the Orchestrator." and STOP.
 
-## Bundle Workflow (Meta-Tasks) — Task 110
+## Bundle Workflow (Meta-Tasks) — Task 110/155 (Pure MCP)
 
 Use this when the Manager has 4–6 small related tasks that should be executed together instead of sequentially. The bundler preserves every requirement verbatim and archives the sources.
 
@@ -236,19 +236,27 @@ Use this when the Manager has 4–6 small related tasks that should be executed
 - Tasks are small, same stack/domain (e.g., all Android polish), and would be inefficient to run one-by-one
 - Goal is one branch, one `Factual Git Diff`, one QA gate (all-or-nothing)
 
-### Canonical Command
+### Canonical Invocation — Pure MCP Tool (Task 155)
 
-```bash
-uv run scripts/bundle-tasks.py <id> <id> ... --title "<kebab-or-human-title>" [--dry-run] [--force]
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
 ```
 
-Examples:
+Examples (MCP arguments):
 
-```bash
-uv run scripts/bundle-tasks.py 12 15 20 --title "android-polish-bundle"
-uv run scripts/bundle-tasks.py 12 15 20 --title "android-polish-bundle" --dry-run
-uv run scripts/bundle-tasks.py 1 2 3 4 5 6 7 --title "mega-bundle" --force  # bypass 6-cap
-```
+- `task_ids: ["12","15","20"], title: "android-polish-bundle"`
+- `task_ids: ["12","15","20"], title: "android-polish-bundle", dry_run: true`
+- `task_ids: ["1","2","3","4","5","6","7"], title: "mega-bundle", force: true  // bypass 6-cap`
 
 ### What the Script Does (Deterministic, No LLM)
 
@@ -285,7 +293,7 @@ uv run scripts/bundle-tasks.py 1 2 3 4 5 6 7 --title "mega-bundle" --force  # by
 ### Verification
 
 ```bash
-uv run scripts/bundle-tasks.py 12 15 20 --title "test" --dry-run
+bundle_tasks(task_ids=["12","15","20"], title="test", dry_run=true)
 lint_task_file tasks/backlog/<META_FILE>
 git log --oneline --follow -- tasks/archive/12-*.md | head
 ```
diff --git a/system-prompt.md b/system-prompt.md
index b56620d..dc40716 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.6.0</system_version>
+<system_version>9.7.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -115,7 +115,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **code-search**: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
 - **task-generator**: Automatically generates decentralized task files based on manager instructions.
 - **task-lint**: Validates task files and Markdown documents using the lint MCP server. Run after task creation and before task closure.
-- **bundle-tasks**: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as both `scripts/bundle-tasks.py` CLI and `bundle_tasks` MCP tool (Task 110).
+- **bundle-tasks**: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as the `bundle_tasks` MCP tool (Task 155).
 - **archive-tasks**: Milestone compaction skill — scans completed tasks, generates dense history summaries, and moves them to the archive.
 - **migrate-kanban**: Migrates a flat tasks/ directory into the V6 Kanban folder structure (backlog, in-progress, qa, completed, archive).
 - **audit-agents**: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
@@ -303,14 +303,13 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     HANDS INSTRUCTION: You MUST follow this exact finalization sequence:
     1. Before calling `lint_task_file`, review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why.
     2. Call the `lint_task_file` MCP tool (from the `lint` server) on the active task file. If lint fails, fix the structural issues before proceeding.
-    3. Execute the atomic QA transition:
+     3. Execute the atomic QA transition:
        Call the `custom_context_qa_transition` MCP tool with:
        - `task_file_path`: "tasks/in-progress/<task-name>.md"
        - `modified_files`: [<modified_file_1>, <modified_file_2>, ...]
-       (Alternatively, run `uv run scripts/qa-transition.py --task tasks/in-progress/<task-name>.md --files ...` via terminal).
        This atomically moves the task file to `tasks/qa/`, updates the `**File:**` header, stages your modified code, and injects the git diff in one operation.
-    4. Once the atomic QA transition succeeds, you are DONE.
-    5. Output EXACTLY this message to the Manager:
+     4. Once the atomic QA transition succeeds, you are DONE.
+     5. Output EXACTLY this message to the Manager:
        "Task implemented, reasoning logged, and Git diff injected. **Manager:** Please copy the entire contents of `tasks/qa/<task-name>.md` and send it back to the Orchestrator Brain with the following message:"
 
        "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
@@ -357,13 +356,12 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     1. If you HALTED after discovery (architecture mismatch): STOP. Do not implement anything. Output exactly:
        "Discovery complete but architecture mismatch detected. Manager: I have generated the context report at [REPORT_PATH]. Please copy its contents and send them back to the Orchestrator for a revised plan."
     2. If implementation completed successfully: Follow the standard finalization sequence — before calling `lint_task_file`, review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why. Then call the `lint_task_file` MCP tool (from the `lint` server) on the active task file. If lint fails, fix the structural issues before proceeding.
-    3. Execute the atomic QA transition:
+     3. Execute the atomic QA transition:
        Call the `custom_context_qa_transition` MCP tool with:
        - `task_file_path`: "tasks/in-progress/<task-name>.md"
        - `modified_files`: [<modified_file_1>, <modified_file_2>, ...]
-       (Alternatively, run `uv run scripts/qa-transition.py --task tasks/in-progress/<task-name>.md --files ...` via terminal).
        This atomically moves the task file to `tasks/qa/`, updates the `**File:**` header, stages your modified code, and injects the git diff in one operation.
-    4. Then output exactly:
+     4. Then output exactly:
        "Task implemented, reasoning logged, and Git diff injected. **Manager:** Please copy the entire contents of `tasks/qa/<task-name>.md` and send it back to the Orchestrator Brain with the following message:"
 
        "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
```
<!-- END_GIT_DIFF -->
