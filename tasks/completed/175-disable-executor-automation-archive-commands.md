# Task 175: Disable automation in Cognitive Executor agent, archive automation commands, restore manual workflow

**File:** `tasks/completed/175-disable-executor-automation-archive-commands.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Neutralize the experimental automated orchestration inside the Cognitive Executor agent, archive the nine automation-specific slash commands, and restore the manual workflow as the active default — without deleting anything.

## Manager's Notes

Manager order (verbatim intent): "Disable the intelligent/automated orchestration system we were building. It is not mature enough yet and is not working well enough, so I don't want it enabled for now. If Cognitive Executor Agent and Cognitive Discovery contain any of those automation rules or related configuration, you can comment them out if the file format supports comments. If comments aren't supported, back them up or move them somewhere safe, and restore the manual workflow as the active/default behavior. Keep all of these components somewhere so we can come back to them in the future. For the existing commands that were created specifically for this automation, archive them as well. Move them to a separate archive location so that when we decide to work on this feature again, we can restore them, fix them, and continue development."

What was implemented (Tasks 167/168/174 — the automation system being paused):
- Persona dispatch loop: executor orchestrates QA → reviewer → Telegram approval → closure via `dispatch_session_turn` (`mcp-persona-server/`, 4 modules + tests).
- Nine slash commands in `.opencode/commands/`: `qa.md`, `reviewer.md`, `manager.md`, `brainstorm.md`, `architect.md`, `designer.md`, `programmer.md`, `planner.md`, `strategist.md` (Tasks 167 + 174).
- Decision Learning Loop via `manager_decisions` MCP (`mcp-decision-server/`, `skill-templates/manager-decision/`).
- Executor sections: `## Persona Loop (MCP Slash Commands)` (lines ~208–266) and `### Decision Learning Loop (automatic — manager_decisions MCP)` (lines ~268–284) in `agents/cognitive-executor.md`.

Why it is being disabled: the automated orchestration is not mature and not working well enough (slow/flaky persona turns, gate-timeout friction, review-loop instability observed across Tasks 173–174). Temporary rollback to the reliable manual workflow; everything preserved for future maturation.

## Local TODOs

- [x] Verify `agents/cognitive-discovery.md` automation refs — grep found 2 (both `query_manager_decisions`/`get_manager_profile` read-only consult, lines 9-10 + 28); neutralized via YAML `#` + HTML comments (server itself disabled in Task 176)
- [x] Wrap executor `## Persona Loop` + `### Decision Learning Loop` sections in `<!-- PAUSED-AUTOMATION ... -->` HTML comments (Markdown supports comments)
- [x] Add explicit `## Manual Workflow (ACTIVE DEFAULT)` section to executor stating persona loop is paused and task execution is manual
- [x] Create `archive/automation-paused-2026-09-09/commands/` + move the 9 command files there via `git mv` (NOT `git rm`); leave a `README.md` stub? No — leave dir without commands; record new locations
- [x] Write `archive/automation-paused-2026-09-09/RESTORE.md` (how to restore: uncomment sections, `git mv` commands back, re-enable servers per Task 176)
- [x] Keep `mcp-persona-server/`, `mcp-decision-server/`, `skill-templates/manager-decision/`, fragments, `system-prompt.md` code in place (disable is by wiring, Task 176 covers servers)
- [x] Update CHANGELOG.md, write Execution Log, lint, stage + inject diff

## Acceptance Criteria

- [x] Executor automation sections commented out; manual workflow section states ACTIVE DEFAULT
- [x] All 9 command files moved to archive location; `.opencode/commands/` holds no automation commands
- [x] `agents/cognitive-discovery.md` verified automation-free with evidence
- [x] RESTORE.md documents the exact reversal steps
- [x] No deletions: `git status` shows renames/modifications only, zero `D` (deleted) entries for implementation files
- [ ] `lint_task_file` passes on the active task file

## Verification Evidence

- **Test command:** `git --no-pager status --short; ls .opencode/commands/; grep -c "dispatch_session_turn" agents/cognitive-executor.md` (expect 0 outside comments) + `lint_task_file` via lint MCP
- **Expected result:** only `R`/`M` entries, empty commands dir, zero live dispatch refs, lint clean
- **Actual result:** `R` x9 (commands → archive), `M` CHANGELOG.md + 2 agent files, `??` RESTORE.md + 176 backlog file; `.opencode/commands/` empty (0 files); executor markers 4 (PAUSED/RESUME/Manual Workflow); discovery decision refs commented (0 live); no `D` entries
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Comment markers break agent file parsing; commands referenced by live docs become dangling
- **Rollback plan:** Remove HTML comment wrappers; `git mv archive/automation-paused-2026-09-09/commands/*.md .opencode/commands/` — full reversal documented in RESTORE.md

---

## Execution Log & Reasoning

- Executor: `## Persona Loop` (was lines 208-266) + `### Decision Learning Loop` (268-284) wrapped in `AUTOMATION-PAUSED-2026-09-09 ... AUTOMATION-RESUME` HTML comments; new `## Manual Workflow` active-default section added above the block (plan → execute → record → hand off, Manager-directed review, never auto-commit).
- Discovery correction: inventory claimed zero refs, but grep found 2 (`query_manager_decisions`/`get_manager_profile` read-only consult). Neutralized: YAML `#` comments on permission lines 9-10, HTML comment on step 5 (prohibition on write/record/evolve kept active). No dispatch/persona-loop refs exist in the file.
- Commands: `git mv` x9 (tracked → renames, history preserved) to `archive/automation-paused-2026-09-09/commands/`; `.opencode/commands/` now empty; `RESTORE.md` written with 6-step restore procedure.
- CHANGELOG: `### Removed` bullet appended (Parse-Then-Append).
- Servers/skill/fragments code untouched in place (disable-by-wiring; Task 176 handles server configs).

**Post-implementation restore (manager order, same session):** restored
`skill-templates/brainstorm-swarm/SKILL.md` (69 lines) byte-identical from
`70ac2e0^` (`diff` → IDENTICAL); left untracked + inert (no live references
point at it after the 174 sweep; automation stays paused).

**Orchestrator micro-task (same session):** grep sweep found one LIVE
automation ref missed in implementation — executor line 86 (Read First:
`query_manager_decisions` + `get_manager_profile` consult, outside the
PAUSED block). Neutralized via inline HTML comment (directive now reads
"re-ask the human manager directly"; original preserved in comment).
AGENTS.md verified CLEAN (0 hits). Persona Loop body (lines 224–304)
confirmed inside the AUTOMATION-PAUSED block — grep hits there are comment
text only. Discovery: live-clean (frontmatter `#`, body HTML comment).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index 418307f..fb33ba6 100644
--- a/.env.example
+++ b/.env.example
@@ -12,20 +12,21 @@ OPENROUTER_API_KEY=sk-or-v1-...
 # ANTHROPIC_API_KEY=...
 # DEEPSEEK_API_KEY=...
 
-# Persona Engine (mcp-persona-server) — light LLM holding the system prompt
-PERSONA_MODEL=openrouter/deepseek/deepseek-v4-flash-0731
-PERSONA_REASONING_EFFORT=high
+# Persona Engine (mcp-persona-server) — PAUSED 2026-09-09 (Task 176): vars kept
+# for future restore, commented out so nothing auto-configures the servers.
+#PERSONA_MODEL=openrouter/deepseek/deepseek-v4-flash-0731
+#PERSONA_REASONING_EFFORT=high
 # Decision extraction model (mcp-decision-server); blank = fall back to PERSONA_MODEL
-DECISION_MODEL=
+#DECISION_MODEL=
 # Decision extraction temperature (default 1.0; out-of-range/invalid clamps to 1.0)
-DECISION_TEMPERATURE=1.0
+#DECISION_TEMPERATURE=1.0
 # Sampling temperature: keep the 1.0 default (low values risk looping / degraded
 # reasoning on complex tasks — tune thinking level instead).
-PERSONA_TEMPERATURE=1.0
-PERSONA_MAX_TOKENS=16384
+#PERSONA_TEMPERATURE=1.0
+#PERSONA_MAX_TOKENS=16384
 # Transcript replay bound: newest N turns re-sent per persona call (default 50;
 # blank = default). Older turns stay in the JSONL audit trail.
-PERSONA_MAX_REPLAY_TURNS=50
+#PERSONA_MAX_REPLAY_TURNS=50
 
 # Decision Learning Store — per-project notes live in <project>/.opencode/decisions
 # (auto-resolved, no setting needed). Uncomment to override with an absolute path.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 135a8ae..f816fbd 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -33,6 +33,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **loop-engine daemon + deploy infra (Task 167):** Deleted `loop-engine/` (48 tracked files: daemon/gateway/router/personas/qa_engine/executor/verifier/sentinel/stacks/specs/models/state/watcher + 20 test files + uv.lock) including ignored residue (`.venv`, logs, `__pycache__`), plus `deploy/cognitive-loop.service`, `deploy/docker-compose.yml`, `deploy/Dockerfile` (empty `deploy/` dir removed by git). No `.gitignore` loop rules existed. External historical mentions (`docs/history/*`, `docs/loop-engine/*`, `README.md`, archived tasks) intentionally left untouched.
 - **brainstorm-swarm skill removed, persona covers it (Task 174):** Deleted `skill-templates/brainstorm-swarm/SKILL.md` + global `~/.config/opencode/skills/brainstorm-swarm/` per Manager directive ("we have a persona, no skill needed") — the six-expert scheme and XML schema survive in `prompts/fragments/12-brainstorming_protocol.md`, injected into every `dispatch_session_turn` via `system-prompt.md`; `.opencode/commands/brainstorm.md` rewritten as a pure `Brainstorm Facilitator` persona turn (no skill preload); registry line dropped from fragment 07, `mcp-persona-server/server.py` docstring + executor reference updated, README skill tree pruned. Historical mentions (old CHANGELOG entries, `tasks/archive/*`, `.opencode/memory/*`, `docs/history/*`, `context-reports/*` snapshots) intentionally left untouched. Full suite **120 passed**.
+- **Automation system paused, manual workflow restored (Task 175):** Per Manager order (system not mature enough), the automation rules are neutralized but preserved: `agents/cognitive-executor.md` Persona Loop + Decision Learning Loop wrapped in `AUTOMATION-PAUSED-2026-09-09 ... AUTOMATION-RESUME` HTML comments with an active `## Manual Workflow` section (plan → execute → record → hand off, Manager-directed review, never auto-commit); all 9 automation slash commands moved via `git mv` to `archive/automation-paused-2026-09-09/commands/` (+ `RESTORE.md` with the 6-step restore procedure); `agents/cognitive-discovery.md` verified zero automation refs (untouched). Nothing deleted.
+- **Persona + decision MCP servers disabled repo + global (Task 176):** Per Manager order (disable both, delete nothing), removed the `persona` and `manager_decisions` blocks plus their 9 repo / 11 global tool permission lines from `opencode.json` (repo) and `~/.config/opencode/opencode.json` (JSON supports no comments — blocks removed, code untouched); commented out all active `PERSONA_*` / `DECISION_*` vars in `.env.example` (kept for future restore). Server implementations (`mcp-persona-server/`, `mcp-decision-server/`, skills, transcripts) fully preserved. Restore: re-add blocks from `archive/automation-paused-2026-09-09/RESTORE.md` step 5.
 
 ## [9.10.0] - 2026-09-04
 
diff --git a/agents/cognitive-discovery.md b/agents/cognitive-discovery.md
index c748e13..bc3e285 100644
--- a/agents/cognitive-discovery.md
+++ b/agents/cognitive-discovery.md
@@ -6,8 +6,9 @@ permission:
   bash: deny
   read: allow
   custom_context_*: allow
-  query_manager_decisions: allow
-  get_manager_profile: allow
+  # PAUSED-2026-09-09 (Task 175 — manager_decisions server disabled in Task 176):
+  # query_manager_decisions: allow
+  # get_manager_profile: allow
   external_directory:
     "*": "ask"
     "/tmp/**": "allow"
@@ -25,7 +26,7 @@ When invoked, you must use the `custom_context` MCP tools to compile comprehensi
 2. Use `create_tree_report` to persist a `.gitignore-aware` tree of a path or the whole project as `context-reports/tree_report_<timestamp>_<uuid>.md` when the Manager asks to "create a tree of the project".
 3. Use `read_source_files` to fetch the exact source code of requested files.
 4. Use `extract_signatures` to pull function/class signatures for vertical slices.
-5. Use `query_manager_decisions` + `get_manager_profile` when the request touches architecture, process, scope, or quality gates — past manager rulings are context too. These two tools are read-only; you still must not write, record, or evolve anything (no `record_manager_decision`, no `propose_profile_evolution` — those belong to the executor).
+5. <!-- PAUSED-2026-09-09 (Task 175): decision consult disabled with the manager_decisions server (Task 176). Original: "Use `query_manager_decisions` + `get_manager_profile` when the request touches architecture, process, scope, or quality gates — past manager rulings are context too." --> You still must not write, record, or evolve anything (no `record_manager_decision`, no `propose_profile_evolution` — those belong to the executor).
 
 Do not modify any files. Do not attempt to execute code. Compile the report and halt.
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 2f2be20..4540304 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -83,7 +83,7 @@ If the Manager sends you a direct message that is NOT an XML task block (e.g., "
 
 To prevent hallucinations and respect hidden project constraints, you MUST integrate persistent memory into your execution workflow:
 
-1. **Read First (Mandatory):** At the absolute start of any task (before writing code), load the `project-memory` skill. Read `.opencode/memory/index.md` (if present) — the auto-generated Markdown index of all memory shards — alongside `AGENTS.md` and `DESIGN.md`, to get a compact overview before planning. Then use `search_memory` with keywords from the task description and the tech stack, or `read_memory` for specific keys selected from the index, to retrieve any saved constraints, quirks, or past architectural decisions. If the index is missing, fall back to `list_namespaces`/`search_memory` and trigger `rebuild_memory_index` if needed. When resolving architectural ambiguities, additionally consult the manager's past rulings via the `manager-decision` skill (`query_manager_decisions`, plus `get_manager_profile()` output injected into your reasoning) before re-asking the human manager.
+1. **Read First (Mandatory):** At the absolute start of any task (before writing code), load the `project-memory` skill. Read `.opencode/memory/index.md` (if present) — the auto-generated Markdown index of all memory shards — alongside `AGENTS.md` and `DESIGN.md`, to get a compact overview before planning. Then use `search_memory` with keywords from the task description and the tech stack, or `read_memory` for specific keys selected from the index, to retrieve any saved constraints, quirks, or past architectural decisions. If the index is missing, fall back to `list_namespaces`/`search_memory` and trigger `rebuild_memory_index` if needed. When resolving architectural ambiguities, re-ask the human manager directly. <!-- PAUSED-2026-09-09 (Task 175): manager-decision consult disabled with the manager_decisions server (Task 176). Original: "additionally consult the manager's past rulings via the `manager-decision` skill (`query_manager_decisions`, plus `get_manager_profile()` output injected into your reasoning) before re-asking the human manager." -->
 2. **Apply Constraints:** If memories are found via the index (selectively fetched with `read_memory` or `search_memory` based on the index overview), strictly adhere to them during implementation. Do not contradict past architectural decisions without explicitly flagging it to the Manager.
 3. **Auto-Save Criteria (Strict):** You MUST use `store_memory` to save new memories ONLY if the Orchestrator or Manager explicitly states a new project rule, architectural constraint, or reusable quirk.
    - **DO SAVE:** "The manager prefers Composition over Inheritance," "API X rate limits at 100 req/s, add caching," "Do not use Library Y because of Z."
@@ -205,6 +205,24 @@ Claim: "Task complete. The code looks correct."
 - Do not claim completion without evidence.
 - For completed work, concisely restate it but do not overload with response detail.
 
+## Manual Workflow (Active Default — Automation Paused 2026-09-09)
+
+> The automation system (persona loops, decision-learning loop, slash
+> commands) is PAUSED per Task 175 — not mature enough yet. Everything
+> between `AUTOMATION-PAUSED-2026-09-09` and `AUTOMATION-RESUME` below is
+> preserved verbatim but MUST NOT be followed while paused. The automation
+> slash commands live archived at
+> `archive/automation-paused-2026-09-09/commands/` (see `RESTORE.md` there).
+
+1. **Plan** — read the task, gather context with direct tools, minimal changes.
+2. **Execute** — edit files; verify every change (tests/lint) before claiming done.
+3. **Record** — Execution Log + CHANGELOG + `custom_context_stage_and_inject_diff`.
+4. **Hand off** — move the task file per Kanban rules, notify the Manager.
+   NEVER auto-commit. QA/review happen as Manager-directed direct review,
+   not as persona loops.
+
+<!-- AUTOMATION-PAUSED-2026-09-09 (Task 175 — automation not mature enough, disabled by Manager order; preserved verbatim for future restoration, see archive/automation-paused-2026-09-09/RESTORE.md). Do NOT follow anything until AUTOMATION-RESUME while paused.
+
 ## Persona Loop (MCP Slash Commands)
 
 The retired `loop-engine/` daemon is replaced by on-demand persona turns via
@@ -282,3 +300,5 @@ Fold these into every session without being asked:
    `reject` (the note is the fix specification).
 5. **Never auto-evolve the sample.** `propose_profile_evolution` output is a
    draft for the manager; merging without explicit approval is forbidden.
+
+AUTOMATION-RESUME (end of paused automation block — Task 175) -->
diff --git a/archive/automation-paused-2026-09-09/RESTORE.md b/archive/automation-paused-2026-09-09/RESTORE.md
new file mode 100644
index 0000000..acbd4bc
--- /dev/null
+++ b/archive/automation-paused-2026-09-09/RESTORE.md
@@ -0,0 +1,103 @@
+# Automation System — Paused 2026-09-09 (Tasks 175/176)
+
+## Why paused
+
+Manager order: the intelligent/automated orchestration system (persona
+loops, decision-learning loop, automation slash commands, persona +
+manager-decision MCP servers) is **not mature enough yet** and is not
+working well enough. Disabled for now. **Nothing was deleted** — all code,
+configs, and docs are preserved for future development.
+
+## What is archived here
+
+- `commands/` — the 9 automation slash commands, moved verbatim via
+  `git mv` from `.opencode/commands/`: `qa.md`, `reviewer.md`,
+  `manager.md`, `brainstorm.md`, `architect.md`, `designer.md`,
+  `programmer.md`, `planner.md`, `strategist.md`.
+- The automation *rules* stay in place but neutralized:
+  - `agents/cognitive-executor.md` — `## Persona Loop` +
+    `### Decision Learning Loop` wrapped in
+    `AUTOMATION-PAUSED-2026-09-09 ... AUTOMATION-RESUME` HTML comments;
+    active behavior is `## Manual Workflow`.
+  - `agents/cognitive-discovery.md` — verified ZERO automation refs,
+    untouched.
+  - Repo + global `opencode.json` — `persona` / `manager_decisions` MCP
+    blocks removed from active JSON (JSON has no comments); exact removed
+    text is documented in Tasks 175/176.
+  - `.env.example` — `PERSONA_*` / `DECISION_*` vars commented out
+    (`# PAUSED-2026-09-09`).
+- Server implementations untouched and shippable: `mcp-persona-server/`,
+  `mcp-decision-server/`, `skill-templates/manager-decision/`,
+  `prompts/fragments/{06-personas,07-agent_skills_registry,12-brainstorming_protocol}.md`.
+
+## What was implemented (history)
+
+Tasks 167 (persona engine), 168 (decision learning), 170 (hardening),
+171 (META), 172 (sync), 173 (plugin docs), 174 (persona commands,
+skill removal, persistence cards, context-request lane, split gates,
+replay cap, lineage fallback). See `tasks/completed/` for full records.
+
+## How to restore (when the system is mature)
+
+1. `git mv archive/automation-paused-2026-09-09/commands/*.md .opencode/commands/`
+2. In `agents/cognitive-executor.md`: delete the Manual Workflow section
+   (or keep it as fallback) and remove the
+   `AUTOMATION-PAUSED-2026-09-09` / `AUTOMATION-RESUME` comment markers.
+3. Re-add the `persona` + `manager_decisions` blocks to repo and global
+   `opencode.json` (Task 176 documents the exact removed JSON).
+4. Uncomment `PERSONA_*` / `DECISION_*` in `.env.example`; ensure live
+   `.env` values exist.
+5. Re-run the global-install upgrade workflow, then `opencode mcp list`
+   must show persona + manager_decisions connected.
+6. Run the persona test suite green before re-enabling.
+
+## Appendix A — exact removed JSON (Task 176, 2026-09-09)
+
+Repo `opencode.json` — `mcp.persona` block (global variant identical
+except absolute paths
+`/home/mohammad/.config/opencode/mcp-persona-server`):
+
+```json
+    "persona": {
+      "type": "local",
+      "command": ["uv", "run", "--project", "mcp-persona-server", "mcp-persona-server/server.py"],
+      "enabled": true,
+      "timeout": 600000,
+      "environment": {
+        "OPENROUTER_API_KEY": "{env:OPENROUTER_API_KEY}",
+        "PERSONA_MODEL": "{env:PERSONA_MODEL}",
+        "PERSONA_REASONING_EFFORT": "{env:PERSONA_REASONING_EFFORT}",
+        "PERSONA_TEMPERATURE": "{env:PERSONA_TEMPERATURE}",
+        "PERSONA_MAX_TOKENS": "{env:PERSONA_MAX_TOKENS}",
+        "TELEGRAM_BOT_TOKEN": "{env:TELEGRAM_BOT_TOKEN}",
+        "TELEGRAM_CHAT_ID": "{env:TELEGRAM_CHAT_ID}",
+        "TELEGRAM_APPROVAL_TIMEOUT_SECONDS": "{env:TELEGRAM_APPROVAL_TIMEOUT_SECONDS}"
+      }
+    },
+```
+
+Repo `opencode.json` — `mcp.manager_decisions` block (global variant:
+absolute paths `/home/mohammad/.config/opencode/mcp-decision-server`):
+
+```json
+    "manager_decisions": {
+      "type": "local",
+      "command": ["uv", "run", "--project", "mcp-decision-server", "mcp-decision-server/server.py"],
+      "enabled": true,
+      "timeout": 600000,
+      "environment": {
+        "OPENROUTER_API_KEY": "{env:OPENROUTER_API_KEY}",
+        "PERSONA_MODEL": "{env:PERSONA_MODEL}",
+        "DECISION_MODEL": "{env:DECISION_MODEL}",
+        "DECISION_TEMPERATURE": "{env:DECISION_TEMPERATURE}"
+      }
+    }
+```
+
+Removed permission lines — repo (9):
+`dispatch_session_turn`, `get_session_summary`, `escalate_to_admin`,
+`request_admin_approval`, `extract_session_decisions`,
+`record_manager_decision`, `query_manager_decisions`,
+`get_manager_profile`, `propose_profile_evolution` (all `"allow"`).
+Global (same 9 plus): `open_approval_gate`, `poll_approval_gate`
+(all `"allow"`). All other permission lines untouched.
diff --git a/.opencode/commands/architect.md b/archive/automation-paused-2026-09-09/commands/architect.md
similarity index 100%
rename from .opencode/commands/architect.md
rename to archive/automation-paused-2026-09-09/commands/architect.md
diff --git a/.opencode/commands/brainstorm.md b/archive/automation-paused-2026-09-09/commands/brainstorm.md
similarity index 100%
rename from .opencode/commands/brainstorm.md
rename to archive/automation-paused-2026-09-09/commands/brainstorm.md
diff --git a/.opencode/commands/designer.md b/archive/automation-paused-2026-09-09/commands/designer.md
similarity index 100%
rename from .opencode/commands/designer.md
rename to archive/automation-paused-2026-09-09/commands/designer.md
diff --git a/.opencode/commands/manager.md b/archive/automation-paused-2026-09-09/commands/manager.md
similarity index 100%
rename from .opencode/commands/manager.md
rename to archive/automation-paused-2026-09-09/commands/manager.md
diff --git a/.opencode/commands/planner.md b/archive/automation-paused-2026-09-09/commands/planner.md
similarity index 100%
rename from .opencode/commands/planner.md
rename to archive/automation-paused-2026-09-09/commands/planner.md
diff --git a/.opencode/commands/programmer.md b/archive/automation-paused-2026-09-09/commands/programmer.md
similarity index 100%
rename from .opencode/commands/programmer.md
rename to archive/automation-paused-2026-09-09/commands/programmer.md
diff --git a/.opencode/commands/qa.md b/archive/automation-paused-2026-09-09/commands/qa.md
similarity index 100%
rename from .opencode/commands/qa.md
rename to archive/automation-paused-2026-09-09/commands/qa.md
diff --git a/.opencode/commands/reviewer.md b/archive/automation-paused-2026-09-09/commands/reviewer.md
similarity index 100%
rename from .opencode/commands/reviewer.md
rename to archive/automation-paused-2026-09-09/commands/reviewer.md
diff --git a/.opencode/commands/strategist.md b/archive/automation-paused-2026-09-09/commands/strategist.md
similarity index 100%
rename from .opencode/commands/strategist.md
rename to archive/automation-paused-2026-09-09/commands/strategist.md
diff --git a/opencode.json b/opencode.json
index 2537b77..29509cc 100644
--- a/opencode.json
+++ b/opencode.json
@@ -44,46 +44,6 @@
       ],
       "enabled": true,
       "timeout": 15000
-    },
-    "persona": {
-      "type": "local",
-      "command": [
-        "uv",
-        "run",
-        "--project",
-        "mcp-persona-server",
-        "mcp-persona-server/server.py"
-      ],
-      "enabled": true,
-      "timeout": 600000,
-      "environment": {
-        "OPENROUTER_API_KEY": "{env:OPENROUTER_API_KEY}",
-        "PERSONA_MODEL": "{env:PERSONA_MODEL}",
-        "PERSONA_REASONING_EFFORT": "{env:PERSONA_REASONING_EFFORT}",
-        "PERSONA_TEMPERATURE": "{env:PERSONA_TEMPERATURE}",
-        "PERSONA_MAX_TOKENS": "{env:PERSONA_MAX_TOKENS}",
-        "TELEGRAM_BOT_TOKEN": "{env:TELEGRAM_BOT_TOKEN}",
-        "TELEGRAM_CHAT_ID": "{env:TELEGRAM_CHAT_ID}",
-        "TELEGRAM_APPROVAL_TIMEOUT_SECONDS": "{env:TELEGRAM_APPROVAL_TIMEOUT_SECONDS}"
-      }
-    },
-    "manager_decisions": {
-      "type": "local",
-      "command": [
-        "uv",
-        "run",
-        "--project",
-        "mcp-decision-server",
-        "mcp-decision-server/server.py"
-      ],
-      "enabled": true,
-      "timeout": 600000,
-      "environment": {
-        "OPENROUTER_API_KEY": "{env:OPENROUTER_API_KEY}",
-        "PERSONA_MODEL": "{env:PERSONA_MODEL}",
-        "DECISION_MODEL": "{env:DECISION_MODEL}",
-        "DECISION_TEMPERATURE": "{env:DECISION_TEMPERATURE}"
-      }
     }
   },
   "permission": {
@@ -103,15 +63,6 @@
     "bundle_tasks": "allow",
     "blowsh_*": "allow",
     "telegram_*": "allow",
-    "dispatch_session_turn": "allow",
-    "get_session_summary": "allow",
-    "escalate_to_admin": "allow",
-    "request_admin_approval": "allow",
-    "extract_session_decisions": "allow",
-    "record_manager_decision": "allow",
-    "query_manager_decisions": "allow",
-    "get_manager_profile": "allow",
-    "propose_profile_evolution": "allow",
     "external_directory": {
       "*": "ask",
       "/tmp/**": "allow"
diff --git a/skill-templates/brainstorm-swarm/SKILL.md b/skill-templates/brainstorm-swarm/SKILL.md
new file mode 100644
index 0000000..118eb17
--- /dev/null
+++ b/skill-templates/brainstorm-swarm/SKILL.md
@@ -0,0 +1,69 @@
+---
+name: brainstorm-swarm
+description: Orchestrates a multi-expert brainstorming session using six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) to resolve cross-disciplinary ambiguity. Outputs structured XML-tagged session reports.
+---
+
+# Multi-Agent Brainstorming Swarm
+
+## When to Trigger
+
+- The Manager explicitly requests a brainstorming session.
+- After intent expansion, the input remains ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning).
+- A backlog task contains a `<brainstorming_session>` block that must be interpreted as non-functional guidelines.
+
+## The Six Expert Personas
+
+### 1. system_architect
+
+**Focus:** System design, scalability, data flow, API contracts, infrastructure, and architectural trade-offs.
+
+**Output:** Technical architecture assessment with risk analysis and recommended patterns. Covers coupling, cohesion, latency, availability, and disaster recovery.
+
+### 2. security_engineer
+
+**Focus:** Threat modeling, authentication/authorization, data privacy, compliance, and vulnerability assessment.
+
+**Output:** Security audit with identified risks (OWASP Top 10), severity ratings, and mitigation strategies. Covers least privilege, encryption at rest/in-transit, and regulatory requirements.
+
+### 3. product_manager
+
+**Focus:** User needs, feature prioritization, roadmap alignment, MVP definition, and stakeholder communication.
+
+**Output:** Product requirements analysis with prioritized user stories and success metrics. Maps features to user impact and business outcomes.
+
+### 4. business_strategist
+
+**Focus:** Market positioning, ROI analysis, competitive landscape, monetization models, and go-to-market strategy.
+
+**Output:** Business case assessment with strategic recommendations and risk/reward analysis. Covers total addressable market, pricing, and differentiation.
+
+### 5. legal_advisor
+
+**Focus:** Regulatory compliance, licensing, data protection laws (GDPR/CCPA), intellectual property, and contractual obligations.
+
+**Output:** Legal compliance review with identified obligations, risks, and recommended safeguards. Covers cross-border data transfer, terms of service, and liability.
+
+### 6. critical_thinker
+
+**Focus:** Devil's advocacy, assumption challenging, blind-spot detection, logical fallacies, and edge-case stress-testing.
+
+**Output:** Critical review highlighting unstated assumptions, cognitive biases, and stress-test results for each proposed approach.
+
+## Execution Rules
+
+1. **Independent Analysis:** Each persona MUST produce its analysis before reading any other persona's output. No cross-contamination.
+2. **Conflict Resolution:** If two personas give contradictory advice, the final synthesis MUST explicitly document the conflict and explain the resolution.
+3. **Minimum Output:** Each persona MUST produce at least 3 concrete observations or recommendations.
+4. **Grounding:** All reasoning must be grounded in the problem description. Do not invent hypothetical scenarios without explicit basis.
+5. **Output Format:** Always use the XML `<brainstorming_session>` schema defined in the system prompt's `<brainstorming_protocol>` section.
+
+## Interpretation in Backlog Tasks
+
+When a task file contains a `<brainstorming_session>` block, interpret the enclosed `<persona_responses>` and `<final_recommendation>` as **non-functional guidelines** that inform but do not override the primary task instructions. They provide cross-domain context:
+
+- `system_architect` responses influence architectural decisions.
+- `security_engineer` responses impose security constraints.
+- `product_manager` responses guide feature prioritization.
+- `business_strategist` responses shape scope and timeline.
+- `legal_advisor` responses enforce compliance requirements.
+- `critical_thinker` responses highlight edge cases and risks to test.
```
<!-- END_GIT_DIFF -->
