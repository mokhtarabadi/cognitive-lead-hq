---
name: kanban-lifecycle
description: Unified Kanban lifecycle — task generation, lint validation, META bundling, completion archiving, and flat-to-V6 migration in one meta skill.
---

# Kanban Lifecycle Meta Skill

Meta skill combining **task-generator** (create), **task-lint** (validate), **bundle-tasks** (META bundling), **archive-tasks** (milestone compaction), and **migrate-kanban** (flat migration). Load one skill for any `tasks/` work. Sections are verbatim from the source skills.

---

## Part 1: Task Generator Workflow (from `task-generator`)

# Task Generator Workflow

You are the Task Generator. Your job is to create structured task files for the Manager.

## Workflow

1. **Analyze:** Determine if the request is a `bug`, `improvement`, or `feature`.
2. **Index:** Search all Kanban subdirectories in `tasks/` for the highest existing task ID. Run:

```bash
NEXT_ID=$(find tasks/ -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ]; then NEXT_ID="01"; fi
printf "%02d\n" $NEXT_ID
```

Use the output as the zero-padded task number. If `tasks/` doesn't exist, create it along with the Kanban subdirectories and start at `01`.

Title consistency check (unified template `# Task [NN]: [Title]`): flag any duplicate title numbers:

```bash
grep -rhn "^# Task [0-9][0-9]*:" tasks/ | sort | uniq -d
```

The title number MUST match the filename ID. Any mismatch or duplicate must be resolved with the Collision Check below before writing the file.

Duplicate ID check — flag any duplicated numeric task IDs across the ACTIVE Kanban directories only:

```bash
find tasks/backlog tasks/in-progress tasks/qa tasks/completed -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort | uniq -d
```

If the output is non-empty, HALT and report duplicate task IDs. Do NOT overwrite files. Archive is a historical record and MUST NOT be included in the blocking duplicate-ID check. If archive duplicates are discovered separately, report them as a warning only, never HALT task creation.

3. **Name:** Create a kebab-case filename (e.g., `01-fix-login-bug.md`). Place it in `tasks/backlog/`. Task-number discipline: the filename and `# Task [NN]` title carry the number exactly once — never repeat task numbers in template prose, headings, or notes (numbers live only in code comments, CHANGELOG, history, and HTML comments).

3.5. **Collision Check:** Before writing the file, verify that `tasks/backlog/{NEXT_ID}-*.md` does NOT already exist. Run: `ls tasks/backlog/${NEXT_ID}-*.md`. If a file with that ID already exists, HALT and report: '⚠️ Task ID collision: {NEXT_ID} is already in use. Re-run ID discovery.' Do NOT overwrite existing files.

4. **Generate File:** Write the following unified canonical template to the new file. The `## Source Context` section is **polymorphic** — include ONLY the variant block matching the `**Source:**` value. `## Goal`, `## Local TODOs`, `## Acceptance Criteria`, `## Verification Evidence`, and `## Risk & Rollback` are MANDATORY and UNCONDITIONAL for ALL source types (lint contract):

   ```markdown
   # Task [NN]: [Title]

   **File:** `tasks/backlog/[filename]`
   **Source:** [orchestrator|telegram|manager]
   **Type:** [bug|improvement|feature]
   **Status:** open

   ## Source Context

   ### Variant A: Orchestrator (`**Source:** orchestrator`)

   ## Goal

   [Summary of the goal — MANDATORY]

   ## Blueprint Reference

   [Link or reference to the approved architectural blueprint]

   ## Manager's Notes

   [Any specific notes, requirements, or constraints]

   ### Variant B: Telegram (`**Source:** telegram`)

   ## Goal

   [MANDATORY — one-line goal derived from the RAW_TEXT]

   ## Original Message ([Language])

   {RAW_TEXT — verbatim, zero changes}

   ## English Translation

   {EN_TRANSLATION}

   ## Refactored Prompt

   {REFACTORED_PROMPT}

   ## Relevant Code Context

   {CODEBASE_CONTEXT}

   ## AI Analysis & Opinion

   {AI_OPINION}

   ### Variant C: Manager (`**Source:** manager`)

   ## Goal

   [Summary of the goal — MANDATORY]

   ## Manager's Notes

   [Any specific notes, requirements, or constraints]

   <!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

   ## Local TODOs

   - [ ] Initial codebase exploration
   - [ ] [Specific step 1]
   - [ ] Verify functionality

   ## Acceptance Criteria

   - [ ] [Criterion 1 — what must be true for this task to be considered done]
   - [ ] [Criterion 2]

    ## Verification Evidence

    - **Test command:** rtk test [exact command]
    - **Expected result:** [what success looks like]
    - **Actual result:** _(The Hands fill this during execution)_
    - **Exit code:** _(The Hands fill this during execution)_

    > Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

   ## Definition of Done

   The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

   - [ ] Build/Test/Lint pass with exit code 0
   - [ ] `lint_task_file` passes on the active task file
   - [ ] `CHANGELOG.md` updated via Parse-Then-Append
   - [ ] `testing-verification` applied and evidence recorded

   > **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

   ## Risk & Rollback

   - **Risk:** [what could go wrong]
   - **Rollback plan:** [how to undo if needed]

   ---

   ## Execution Log & Reasoning

   _(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

   ## Factual Git Diff

   <!-- BEGIN_GIT_DIFF -->

   _(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

   <!-- END_GIT_DIFF -->
   ```

## Multi-Phase Task Template

If the Orchestrator specifies `multi_phase: true`, generate a SINGLE task file with inline phase sections instead of separate files. Use this structure (same unified metadata header, `## Goal` mandatory):

```markdown
# Task [NN]: [Title]

**File:** `tasks/backlog/[filename]`
**Source:** [orchestrator|telegram|manager]
**Type:** [bug|improvement|feature]
**Status:** open

## Goal

[Summary of the goal]

## Acceptance Criteria

- [ ] [Criterion 1 — what must be true for this task to be considered done]
- [ ] [Criterion 2]

## Verification Evidence

- **Test command:** rtk test [exact command]
- **Expected result:** [what success looks like]
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every multi-phase task):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** [what could go wrong]
- **Rollback plan:** [how to undo if needed]

## Phase 1: [Name]

### Local TODOs

- [ ] [Phase 1 step 1]
- [ ] [Phase 1 step 2]

## Phase 2: [Name]

### Local TODOs

- [ ] [Phase 2 step 1]
- [ ] [Phase 2 step 2]

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
```

5. **Halt and Handover:** DO NOT execute the task. Keep the generated task in `tasks/backlog/`. Invoke `brain_turn` directly under the active session thread with the generated task ID and task-file context. The Manager must not copy, paste, or relay task contents. Continue only through the normal planning and approval gates.

## Bundle Workflow (Meta-Tasks, Pure MCP)

Use this when the Manager has 4–6 small related tasks that should be executed together instead of sequentially. The bundler preserves every requirement verbatim and archives the sources.

### When to Use

- Manager says: "bundle tasks 1, 2, 5, 10, 15, 20" or "create a meta-task from 12 15 20"
- Tasks are small, same stack/domain (e.g., all Android polish), and would be inefficient to run one-by-one
- Goal is one branch, one `Factual Git Diff`, one QA gate (all-or-nothing)

### Canonical Invocation — Pure MCP Tool

Invoke the `bundle_tasks` MCP tool via the Hands:

```json
{
  "tool": "bundle_tasks",
  "arguments": {
    "task_ids": ["12", "15", "20"],
    "title": "android-polish-bundle",
    "dry_run": false,
    "force": false
  }
}
```

Examples (MCP arguments):

- `task_ids: ["12","15","20"], title: "android-polish-bundle"`
- `task_ids: ["12","15","20"], title: "android-polish-bundle", dry_run: true`
- `task_ids: ["1","2","3","4","5","6","7"], title: "mega-bundle", force: true  // bypass 6-cap`

### What the Script Does (Deterministic, No LLM)

1. **Validate IDs:** searches `tasks/backlog/ tasks/in-progress/ tasks/qa/ tasks/completed/` (active only, archive excluded) for each `<id>-*.md`. HALT if any missing or if archive already contains the ID (already superseded). Rejects non-numeric IDs.
2. **Next-ID Discovery:** `find tasks -type f -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 +1` across ALL dirs (including archive) — guarantees no collision. Zero-padded (`02d` for <100, raw for >=100).
3. **Slug:** kebab-case the `--title` (`android Polish_Bundle` → `android-polish-bundle`). Output file: `tasks/backlog/<NEXT_ID>-<slug>.md`.
4. **Verbatim Extraction:** for each source, extracts `## Goal`, `## Manager's Notes`/`## Blueprint Reference`, `## Acceptance Criteria`, `## Local TODOs`, `## Risk & Rollback` verbatim (regex until next `## `). No summarization.
5. **Generate META File:** canonical template + extra metadata:
   - `**Supersedes:** [12, 15, 20]`
   - `**Meta:** true` (flag for tooling; `**Type:**` stays `feature` for lint compat, `meta` is also allowed)
   - Per-source appendix: `### Source Task XX: Title` with verbatim blocks
   - `## Bundled Checklist (All-or-Nothing)` — every source AC line prefixed `[XX]`, single QA gate
   - `## Local TODOs` aggregates all source TODOs prefixed `[XX]` plus bundle-specific steps
   - Guardrail notes: diff-size warning if combined LOC >400
6. **Auto-Archive:** unless `--dry-run`, runs `git mv <source> tasks/archive/<source>` (fallback to `mv` + `git add` for untracked) and patches the archived file:
   - `**File:**` → `tasks/archive/<file>`
   - `**Status:** superseded`
   - `**Superseded-By:** <META_ID>-<slug>` + `**Superseded-At:** YYYY-MM-DD`
   - Superseded footer before `## Execution Log` with `git log --follow` hint
     History remains reachable: `git log --oneline --follow -- tasks/archive/<file>`

### Guardrails

- **Cap:** `MAX_BUNDLE_SIZE=6` — rejects >6 without `--force` (mega-diff prevention)
- **Diff-size:** warns if combined source LOC >400 ("consider split")
- **Duplicate/Collision:** `ls tasks/backlog/<NEXT_ID>-*.md` check before write; HALT if exists. Duplicate active IDs HALT.
- **Archive-Only:** `git mv` to `tasks/archive/` — never `git rm` / purge until META reaches `tasks/completed/`; rollback is `git mv tasks/archive/<id>-*.md tasks/backlog/`

### QA & Completion

- META follows normal Kanban: `tasks/backlog/<META>` → `tasks/in-progress/<META>` → `tasks/qa/<META>` → `tasks/completed/<META>` with a single injected diff
- QA is all-or-nothing: if ANY bundled criterion fails, entire META is `QA_REJECTED`

### Verification

```bash
bundle_tasks(task_ids=["12","15","20"], title="test", dry_run=true)
lint_task_file tasks/backlog/<META_FILE>
git log --oneline --follow -- tasks/archive/12-*.md | head
```

---

## Part 2: Task Lint Skill (from `task-lint`)

# Task Lint Skill

## When to Run

1. **After Part 1 creates a new task file** — validate structure before handing to Orchestrator.
2. **Before closing a task** — validate the task file is complete and well-formed.
3. **During Part 4 archiving** — validate all tasks before compacting.

## Workflow

1. Call `lint_task_file` with the active task file path.
2. If issues found, report them and HALT.
3. If clean, proceed.

## For Markdown files (non-task)

1. Call `lint_markdown` with the file path.
2. Report issues.

---

## Part 3: Bundle Tasks Skill — Meta-Task Bundling (from `bundle-tasks`)

# Bundle Tasks Skill — Meta-Task Bundling

Use this skill when the Manager wants to execute 4–6 small related tasks together instead of sequentially. It eliminates the `backlog → in-progress → qa → completed` round-trip overhead by bundling them into one branch, one `Factual Git Diff`, and one all-or-nothing QA gate.

## When to Use

- Manager says: "bundle tasks 1, 2, 5, 10, 15, 20", "create a meta-task from 12 15 20", "combine these polish tasks", or any note about "meta-task", "bundle", "supersede", "archive and bundle"
- Tasks are small, same stack/domain (e.g., all `android-kotlin`, all `react-vite`, all docs), and would be inefficient to run one-by-one
- You are in any project that has the `mcp-context-server` MCP server — the bundler is available as the `bundle_tasks` MCP tool (pure MCP)

**Do NOT use for:** large refactors, tasks with conflicting files that would cause merge conflicts in one diff, or tasks >6 without explicit `--force`.

## Core Contract (Deterministic, No LLM, No Hallucination)

1. **Verbatim Preservation:** Every source `## Goal`, `## Manager's Notes` / `## Blueprint Reference`, `## Acceptance Criteria` (including multi-line continuations and indented sub-bullets), `## Local TODOs`, `## Risk & Rollback` is copied verbatim into `### Source Task XX` blocks. No summarization. The `## Bundled Checklist` is derived by prefixing each source AC root bullet with `[XX]` and preserving all indented continuation lines.
2. **Single QA Gate:** All bundled criteria are `all-or-nothing`. If any line fails QA, the entire META is `QA_REJECTED`.
3. **Archive, Not Purge (with Transactional Rollback):** Sources are moved via `git mv` to `tasks/archive/` with `**Superseded-By:** <META_ID>-<slug>` until META is `completed`. History stays reachable via `git log --follow`. If ANY archive operation fails, ALL previously archived files are rolled back to their original locations, the META file is deleted, and the operation aborts cleanly.
4. **Guardrails:** `MAX_BUNDLE_SIZE=6` (reject >6 without `--force`), combined LOC >400 warning, missing-ID and duplicate-ID checks (hard halt on duplicate active IDs), stack conflict detection (warn or require `--force`), SHA verbatim checksum validation, atomic Next-ID creation with retry loop for concurrent safety.

## Invocation — Pure MCP Tool

The `mcp-context-server/server.py:bundle_tasks` tool is **fully self-contained** — it does NOT require `scripts/bundle-tasks.py`. All helpers (kebab_case, discover_next_id, find_task_file, extract_section, build_meta_content, git_mv_or_fallback, patch_archived_file) are inlined inside the MCP tool function. Invoke via the Hands' MCP interface:

```json
{
  "tool": "bundle_tasks",
  "arguments": {
    "task_ids": ["12", "15", "20"],
    "title": "android-polish-bundle",
    "dry_run": true,
    "force": false
  }
}
```

**Tool name:** `bundle_tasks` on `mcp-context-server` (`custom_context` FastMCP server). It validates IDs, discovers NEXT_ID, slugifies title, generates META with verbatim preservation, and auto-archives sources. Dry-run prints preview without file creation. Pure MCP — no external script dependency.

## What Happens (Deterministic Steps)

1. **Validate IDs:** Search `tasks/backlog/ tasks/in-progress/ tasks/qa/ tasks/completed/` (active only, `tasks/archive/` excluded per `task-generator` duplicate-ID contract) for each `<id>-*.md`. HALT if any missing; note if found in archive (already superseded). Reject non-numeric IDs.
2. **Discover NEXT_ID:** `find tasks -type f -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}'` across **ALL** dirs including `archive` (no collision). Zero-padded `02d` for <100, raw for ≥100.
3. **Slugify Title:** `title` → kebab-case (`android Polish_Bundle` → `android-polish-bundle`). Output file: `tasks/backlog/<NEXT_ID>-<slug>.md`.
4. **Verbatim Extraction:** For each source, extract `## Goal`, `## Manager's Notes`/`## Blueprint Reference`, `## Acceptance Criteria`, `## Local TODOs`, `## Risk & Rollback` verbatim via regex `^## Heading$(.*?)(?=^## |\n---\s*\n|\Z)`. No summarization.
5. **Generate META File:** Canonical task template + `**Supersedes:** [12, 15, 20]` + `**Meta:** true` + `**Created:**` + per-source appendix `### Source Task XX: Title` + `## Source Bundles (Verbatim Preservation)` + `## Bundled Checklist (All-or-Nothing)` (every source AC line prefixed `[XX]`, single QA gate) + aggregated `## Local TODOs` (`[XX]`-prefixed) + guardrail notes (LOC warning if >400).
6. **Auto-Archive (unless dry_run):** `git mv <src> tasks/archive/<src>` (fallback to `mv` + `git add` for untracked) then patch archived file: `**File:**` → `tasks/archive/<file>`, `**Status:** superseded`, add `**Superseded-By:** <META_ID>-<slug>` + `**Superseded-At:** YYYY-MM-DD`, inject superseded footer before `## Execution Log`. History remains reachable: `git log --oneline --follow -- tasks/archive/<file>` — **never** `git rm` until META is `completed`.
7. **Kanban:** META follows normal `tasks/backlog/<META>` → `tasks/in-progress/<META>` → `tasks/qa/<META>` → `tasks/completed/<META>` with one injected `Factual Git Diff`. QA is all-or-nothing.

## Guardrails (Hard Stops & Warnings)

- **Cap:** `MAX_BUNDLE_SIZE=6` — rejects >6 without `--force` (mega-diff prevention). Use `--force` to override.
- **Floor:** bundles need 2-6 tasks — a single task or duplicate IDs in one request are rejected with an explicit error, never silently deduped.
- **Diff-size:** Warns if combined source LOC >400 (`> ⚠️ 400` in notes) — "consider split".
- **Missing / Duplicate / Collision:** Missing IDs → `❌ Missing tasks`; duplicate IDs across active Kanban dirs → distinct `❌ Duplicate task ID` error (never misreported as missing); same-ID-different-slug files for the allocated ID (either zero-padding) → `❌ Task ID collision`; allocation races rebuild the META body after the final ID and create-plus-write atomically, so no stale-ID or empty META file survives.
- **Stack Conflict (M1):** Auto-detects stack from content (android, react, fastapi, spring, ios, go). If tasks have conflicting stacks → requires `--force` to proceed.
- **Verbatim Checksum (M2):** After META generation, verifies every AC line from source tasks appears in the META. Fails if any text was dropped.
- **Archive-only:** Sources go to `tasks/archive/` via `git mv` only. Purge (`git rm`) is blocked until META is `completed`. On ANY archive failure: **transactional rollback** restores byte-identical originals to their recorded origin dirs (no header guessing, failures surfaced), deletes META, exits with clear error.
- **Unicode Slugs (B4):** `_kebab_case()` normalizes via NFKD and preserves non-English characters (\u0600-\u06FF). Non-English titles produce valid slugs like `تست-باندل` instead of losing all characters.

## Verification (Must Pass Before QA)

```bash
# via MCP (pure MCP):
bundle_tasks(task_ids=["12","15","20"], title="test-bundle", dry_run=true)

# then after real bundle (if not dry_run):
lint_task_file tasks/backlog/<NEXT_ID>-<slug>.md
lint_task_file tasks/archive/12-*.md
git log --oneline --follow -- tasks/archive/12-*.md | head
py_compile: python3 -m py_compile mcp-context-server/server.py
```

- META must contain `**Supersedes:**` + every source `### Source Task` block + `## Bundled Checklist` with `[XX]` prefixes.
- `lint_task_file` must pass on META (fixed `---` → `---\n\n` blank-line; `**Type:**` allows `feature` + `Meta:true` and also `meta`) and on both archived files (`**Status:** superseded` is allowed; `**File:**` matches archive path).
- `git log --follow` must show the source's history through the rename.

## Skill Loading

Load this skill when you handle bundling:

```bash
skill("kanban-lifecycle")
```

If you also need lint validation, use Part 2 of this skill; for context gathering before bundling, load `code-search` to ensure sources are in the expected Kanban dirs.

## Rollback

If META is abandoned or fails QA permanently:

```bash
git mv tasks/archive/12-*.md tasks/backlog/12-*.md
git mv tasks/archive/15-*.md tasks/backlog/15-*.md
git mv tasks/backlog/<NEXT_ID>-<slug>.md tasks/archive/<NEXT_ID>-<slug>.md  # mark abandoned and preserve history
```

No HQ code beyond the bundler is affected. If META already reached `tasks/completed/`, its archived sources stay in `tasks/archive/` permanently (they are superseded, not purged).

## Reference

- **MCP:** `mcp-context-server/server.py:bundle_tasks` (self-contained, verbatim helpers inlined, `task_ids: list[str], title: str, dry_run, force`, path-traversal safe, cap 6)
- **Docs:** `AGENTS.md` `## 🛑 META-TASK BUNDLE LIFECYCLE` + `**Bundle Tool:**`, `CHANGELOG.md` `[Unreleased]`
- **Lint:** `mcp-lint-server/server.py` Type regex now `...|meta`
- **Registry:** `prompts/fragments/07-agent_skills_registry.md` lists `kanban-lifecycle`

---

## Part 4: Archive Tasks Skill (from `archive-tasks`)

# Archive Tasks Skill

## Purpose

Prevents the `tasks/completed/` directory from accumulating hundreds of task files by periodically compacting completed tasks into dense, single-file milestone summaries in `docs/history/`.

## Workflow

1. **Scan completed tasks** for the current milestone:

```bash
ls tasks/completed/*.md
```

2. **Read each file** and extract:
   - Task number and title
   - Type (bug/improvement/feature)
   - Source (from the `**Source:**` metadata line)
   - Execution Log & Reasoning (architectural reasoning)
   - Key files modified

3. **Generate a milestone summary** at `docs/history/milestone-X-summary.md` with the following structure:

   ```markdown
   # Milestone X Summary

   **Date:** YYYY-MM-DD
   **Tasks Compacted:** N

   ## Source Distribution

   | Source       | Count |
   | ------------ | ----- |
   | orchestrator | N     |
   | telegram     | N     |
   | manager      | N     |

   ## Architectural Changes

   [Dense summary of all architectural changes across the milestone]

   ## Files Modified

   | File         | Change      |
   | ------------ | ----------- |
   | path/to/file | description |

   ## Criteria Met

   | Task | Acceptance Criteria | Status |
   | ---- | ------------------- | ------ |
   | XX   | [Extracted criteria from the completed task's `## Acceptance Criteria` section] | ✅ Met |

   ## Individual Task Summaries

   ### Task XX: Title

   - **Type:** bug|improvement|feature
   - **Source:** [orchestrator|telegram|manager]
   - **Reasoning:** [condensed execution log]
   ```

4. **Create the `docs/history/` directory** if it does not exist:

```bash
mkdir -p docs/history
```

5. **Move completed files to archive**:

```bash
git mv tasks/completed/*.md tasks/archive/
```

*Note: For untracked task files, use the supported native file-management operation to move them. Stage the moved files only through `custom_context_stage_and_inject_diff`; never run `git add` directly.*

6. **Memory Validation:** After compacting tasks, audit the project memory bank for stale or superseded entries:
   a. Call `list_namespaces` to enumerate all memory namespaces.
   b. For each namespace, call `search_memory` using keywords from the archived tasks.
   c. Identify memories that reference archived/completed task files or superseded workflows.
   d. Detect duplicates: if two memories in the same namespace cover the same topic and one references a newer date or task, flag the older one as superseded.
   e. Output a `## Stale Memory Report` listing all flagged memories with their namespace, key, and reason for flagging.
   f. Wait for Manager approval before calling `delete_memory` on any flagged entry. NEVER auto-delete memories without explicit Manager confirmation.

7. **Stage the new summary and moved files**:

Call `custom_context_stage_and_inject_diff` with the active task file and an explicit `modified_files` list containing the generated milestone summary and every moved task-file path. Do not run `git add` directly.

## When to Run

Run this skill at the end of each milestone or when `tasks/completed/` contains more than 20 files. The milestone number should be determined by reading the highest existing milestone in `docs/history/` and incrementing by one.

---

## Part 5: Migrate Kanban Skill (from `migrate-kanban`)

# Migrate Kanban Skill

## Purpose

Transforms a flat `tasks/` directory (e.g., `tasks/01-task.md`, `tasks/02-task.md`) into the state-based V6 Kanban lifecycle structure:

- `tasks/backlog/` — Open / unstarted tasks
- `tasks/in-progress/` — Currently being worked on
- `tasks/qa/` — Awaiting review / quality assurance
- `tasks/completed/` — Finished tasks
- `tasks/archive/` — Milestone-compacted historical tasks

## Workflow

1. **Create the 5 Kanban directories** if they do not already exist:

```bash
mkdir -p tasks/backlog tasks/in-progress tasks/qa tasks/completed tasks/archive
```

2. **Scan all `.md` files** in the flat `tasks/` root (excluding the Kanban subdirectories):

```bash
find tasks/ -maxdepth 1 -type f -name "*.md" | sort
```

3. **Classify each file** by reading its frontmatter or first line:

   - If the file contains `Status: open` (or `**Status:** open`), move it to `tasks/backlog/`.
   - If the file contains `Status: closed` (or `**Status:** closed`), move it to `tasks/completed/`.
   - If no status is found, default to `tasks/backlog/`.

4. **Move the files** using `git mv` to preserve history:

```bash
for f in tasks/*.md; do
  [ -e "$f" ] || continue
  [ "$f" = "tasks/README.md" ] && continue
  if grep -qi "Status: open" "$f"; then
    git mv "$f" tasks/backlog/
  elif grep -qi "Status: closed" "$f"; then
    git mv "$f" tasks/completed/
  else
    git mv "$f" tasks/backlog/
  fi
done
```

5. **Verify** the migration:

```bash
echo "=== Backlog ===" && ls tasks/backlog/
echo "=== Completed ===" && ls tasks/completed/
```

6. **Update AGENTS.md** to reference the Kanban directory structure in the "Core File Locations" and "Documentation Sync Rules" sections.

## Post-Migration

After running this skill, the flat `tasks/` directory should be empty (except for the 5 Kanban subdirectories). All existing task history is preserved via `git mv`.
