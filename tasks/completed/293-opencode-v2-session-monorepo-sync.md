# Task 293: OpenCode V2 Session-First Monorepo Synchronization

**File:** `tasks/qa/293-opencode-v2-session-monorepo-sync.md`
**Source:** orchestrator
**Type:** feature
**Status:** in-progress

## Goal

Synchronize the monorepo to OpenCode V2 session-first semantics: ambient `OPENCODE_SESSION_ID` auto-detection in `mcp-brain-bridge` preflight, system prompt v9.53.0 with updated fragments, purged file-pull references from agent specs, aligned downstream skills, and synchronized docs/changelog.

## Micro-Task Checklist (Orchestrator blueprint)

- [x] **Step 1:** Scaffold and stage Task 293 in Kanban lanes.
- [x] **Step 2:** Ambient `OPENCODE_SESSION_ID` detection in `mcp-brain-bridge`.
- [x] **Step 3:** Update system prompt fragments and reassemble monolith to 9.53.0.
- [x] **Step 4:** Clean up agent specs in `agents/`.
- [x] **Step 5:** Synchronize downstream skills (`skill-templates/`).
- [x] **Step 6:** Update documentation, changelog, and verify.

## Local TODOs

- [x] Wire ambient session detection + unit test
- [x] Bump fragments + reassemble prompt + prompt-sync green
- [x] Clean agent specs + skill template
- [x] Docs + README + LLM.txt + CHANGELOG + RTK verification

## Acceptance Criteria

- [x] AC1: `preflight.validate_request` auto-detects ambient `OPENCODE_SESSION_ID` when `session_id` is omitted.
- [x] AC2: System prompt reassembled to v9.53.0 with fragments 01/09/22 updated and `test_prompt_sync` green.
- [x] AC3: `agents/cognitive-executor.md` file-pull section purged of deleted tools and documents ambient session detection.
- [x] AC4: `agents/cognitive-discovery.md` handoffs require whole-file reporting without multipart expectations.
- [x] AC5: `skill-templates/audit-agents/SKILL.md` template rules carry session-thread persistence.
- [x] AC6: Docs (`brain-bridge`, `services`), `README.md`, `LLM.txt`, `CHANGELOG.md` synchronized; RTK suite + doc-sync green.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_preflight.py tests/test_brain_capability.py tests/test_prompt_sync.py -q`
- **Expected result:** pass, exit code 0
- **Actual result:** `327 passed in 1.61s`, exit 0
- **Exit code:** 0
- **Doc sync:** `python3 scripts/check_docs_sync.py` → `docs-sync: OK`, exit 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** ambient env detection could bind an unintended session when callers expect one-off turns.
- **Rollback plan:** revert `preflight.py` ambient block; repin prompt version to 9.52.0 and reassemble.

---

## Execution Log & Reasoning

**Created (2026-10-04):** backlog file scaffolded via `task-generator` skill; NEXT_ID 293 (lanes max 292).

**Implementation (2026-10-04):**
- Wired ambient `OPENCODE_SESSION_ID` detection in `preflight.py` (`validate_request`: explicit `session_id` wins, else ambient env cleaned via `require_session_id`, else `None`; docstring updated). New test `test_preflight_uses_ambient_opencode_session_id`; binding tests hardened to clear the ambient var.
- Fix (verification-driven): first RTK run showed 7 failures in `test_brain_bridge.py` — ambient `OPENCODE_SESSION_ID=ses_ef82…` from the live shell hijacked task-keyed turns (the exact risk in Risk & Rollback). Added hermetic autouse fixtures (`_no_ambient_session`) to `test_brain_bridge.py` + `test_brain_capability.py`; suite now **327 passed**. Also updated `brain_turn` `session_id` docstring in `server.py` for ambient semantics.
- Updated prompt fragments `01` (9.52.0 → 9.53.0), `09` (2× automatic-mode chaining → active session thread), `22` (survival contract + session ID); reassembled `system-prompt.md` (98933 bytes, `assemble_system_prompt.py` exit 0); `test_prompt_sync` pin → 9.53.0.
- Excised deleted file-pull tools from `agents/cognitive-executor.md` (new `File context retrieval` section; state machine documents ambient detection). Verified `agents/cognitive-discovery.md` carries no multipart/chunk expectations (read-only check, no edit — kept out of staging list).
- Updated `skill-templates/audit-agents/SKILL.md` (2× Buffer Isolation + 2× End-Of-Task Sequence, project-agnostic session-thread wording; HQ-only rules untouched per AGENTS.md).
- Updated `docs/brain-bridge.md` (history section + Environment table), `docs/services.md` (mcp-brain singular-tool note), `README.md` + `LLM.txt` (session-thread summaries), `CHANGELOG.md` (`## [9.53.0] - 2026-10-04`, Added + Changed).
- Assumption A1: `qa_transition` `modified_files` extended beyond the Orchestrator list with `mcp-brain-bridge/server.py`, `tests/test_brain_bridge.py`, `tests/test_brain_capability.py`, `docs/services.md` — all four carry real hunks required for AC1/AC6 (ambient docstring, hermetic fixtures, singular-tool note); staging only the listed subset would leave changes unstaged and the injected diff incomplete.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e8eb838..0e8d76c 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -31,6 +31,16 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Lean session-first Brain bridge refactor (Task 292):** Removed dead tools `read_file`, `grep_files`, and `get_context_bundle` from `mcp-brain-bridge` (Hands use native OpenCode `read`/`grep`/`glob`; the five-file bundle still auto-attaches internally). Removed the multipart chunking allocator (`_allocate_attachments`, `_render_attachment`, `_marker_room`, `_open_overhead`, `_validate_attachment_resume`, `_attachment_priority`, priority tuples) and the `attachment_resume` turn parameter, plus the `history.pop(1)` middle-turn drop loop and the `_read_file_impl` / `_grep_files_impl` helpers with their grep/read guardrail constants.
 
+## [9.53.0] - 2026-10-04
+
+### Added
+
+- **Ambient session auto-detection (Task 293):** `mcp-brain-bridge` preflight now detects ambient `OPENCODE_SESSION_ID` from the process environment (set by OpenCode V2 for every session) when `session_id` is omitted — OpenCode turns automatically bind to the active session thread with zero caller flags. Explicit `session_id` always wins; blank/unset means no ambient binding. New unit test `test_preflight_uses_ambient_opencode_session_id` pins the behavior; existing binding tests hardened to clear the ambient variable for hermetic assertions.
+
+### Changed
+
+- **Bumped system prompt to 9.53.0 (Task 293):** updated prompt fragments (`01-system_version` 9.52.0 → 9.53.0; `09-hands_protocols` automatic-mode chaining now runs under the active session thread instead of the same `task_id`; `22-compaction_protocol` survival contract gains the active session ID), reassembled `system-prompt.md` (byte-verified via assembler), and updated the `test_prompt_sync` version pin. Docs synced: `docs/brain-bridge.md` (session-first history + Environment table document ambient auto-detection), `docs/services.md` (mcp-brain lists `brain_turn` as the singular exposed automation tool), `README.md` + `LLM.txt` (session-thread summaries). Purged deleted file-pull tools (`grep_files`, `read_file`) from `agents/cognitive-executor.md` (new `File context retrieval` section uses native `read`/`grep`/`glob` + `[fed-context]`) and documented ambient `OPENCODE_SESSION_ID` detection in the Brain Bridge state machine. Aligned downstream `skill-templates/audit-agents/SKILL.md` (Buffer Isolation + End-Of-Task Sequence now carry session-thread persistence, project-agnostic wording).
+
 ## [9.49.0] - 2026-10-01
 
 ### Added
diff --git a/LLM.txt b/LLM.txt
index 66356ff..fed7540 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -313,7 +313,7 @@ The `cli.json` `plugins` entry enables the todolist TUI sidebar strip.
 
 **Launch form + credentials:** no session spawns servers anymore — the 7 singletons run as supervised services on `127.0.0.1:8101-8107` (started in Step 7.5, full map in `docs/services.md`), and the config above only points at them via `type: "remote"`. The old per-session stdio storm (and its `mcp connect failed: Request timed out` failures, ~200/day before the 2026-09-29 singleton fix) is gone by construction. The brain/decision timeouts stay 600000ms (10 min) — LLM turns need it. Credentials (`BRAIN_*`, `DECISION_*`, `TELEGRAM_*`) are **not** in the OpenCode config: each server self-loads `.env` at import, in order `<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env`, never overriding real process env. For the global install that effective file is **`~/.config/opencode/.env`** (seeded in Step 5, `chmod 600`); for servers run straight from the repo it is the repo-root `.env`. The systemd/launchd/Windows units therefore need **no** `EnvironmentFile=` for these keys. Telegram prerequisites (clone + `uv sync` + `.env` + allowed-root dirs) are still installed per §7.6 — only the launch moved into the `mcp-telegram` service.
 
-**QA/review run through the bridge:** the Hands calls `brain_turn` with the instruction + task file (see the Bridge section in `agents/cognitive-executor.md`). No per-persona commands or learning stores.
+**QA/review run through the bridge:** the Hands calls `brain_turn` with the instruction + task file (see the Bridge section in `agents/cognitive-executor.md`); history continues under the active session thread (ambient `OPENCODE_SESSION_ID` auto-detection). No per-persona commands or learning stores.
 
 > **Project vs Global `opencode.json` (full V2, 2026-10-01):** The **repo's** `opencode.json` (committed) carries **no `mcp` section at all** — all 7 servers live in the **global** `~/.config/opencode/opencode.json` (created here) under `mcp.servers` as `type: "remote"` loopback URLs (`http://127.0.0.1:8101-8107/mcp`, identical for every user — no per-machine paths). New installations and `global-install-upgrade` (Step 5 in `.opencode/memory/workflows/global-install-upgrade.md`) must keep this split — `diff` of repo vs global `opencode.json` will always differ (repo has no `mcp`, global has 7 remote entries) by design; verify global shows 7 `127.0.0.1:810*/mcp` URLs.
 
diff --git a/README.md b/README.md
index fc48839..063bf3b 100644
--- a/README.md
+++ b/README.md
@@ -89,7 +89,7 @@ This is the canonical pure-MCP cycle:
 2. **Orchestrator issues architectural blueprint & awaits approval** — Brain reviews context, proposes plan, and halts for explicit Manager `Approved`.
 3. **Hands receives the implementation XML and runs locally with ZAC enforcement** — no pasting between chats; the Hands calls the Brain itself.
 4. **Hands executes code, runs tests, and invokes `custom_context_qa_transition`** — stages `modified_files`, injects factual diff, and moves task `tasks/in-progress/` → `tasks/qa/` via pure MCP.
-5. **Hands sends the QA task file to the Brain for QA Engineer adversarial testing and Code Reviewer architectural review via `brain_turn`** — no pasting; history continues under the same task id.
+5. **Hands sends the QA task file to the Brain for QA Engineer adversarial testing and Code Reviewer architectural review via `brain_turn`** — no pasting; history continues under the active session thread.
 6. **Manager approves closure and Hands commits atomically via `custom_context_commit_and_clean_task`** — commits staged diff, replaces raw diff with hash reference, and moves task to `tasks/completed/` — the only commit path.
 
 All transitions use pure FastMCP tools (`custom_context_qa_transition`, `bundle_tasks`, `custom_context_commit_and_clean_task`) — no `uv run scripts/...` CLI required.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index b7f89af..12bb656 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -403,7 +403,9 @@ needs no extra machinery.
    `session_id` alongside `task_id` (session-first): one thread spans
    the whole work session, while the task file and diff still resolve
    from `task_id`. A bare `task_id` with no `session_id` keeps the
-   legacy task-keyed transcript.
+   legacy task-keyed transcript. When `session_id` is omitted,
+   `brain_turn` automatically detects `OPENCODE_SESSION_ID` from the
+   environment, ensuring seamless session continuity across tasks.
 2. **Call** `brain_turn`. Read `status`:
    - `XML_EXTRACTED` — execute `xml_blocks` as the next instruction set,
      exactly like an Orchestrator XML block.
@@ -508,13 +510,9 @@ capability-blocked step (missing required tool) with no replayable
 ruling is a hard blocker: halt with the relay block as the named
 blocker instead of skipping it.
 
-### File pull for big tasks
+### File context retrieval
 
-The Brain cannot read your disk — it only sees what a `brain_turn`
-carries. For big task files, never paste the whole file: grep first via
-the bridge `grep_files`, then pull only the needed ranges with
-`read_file(path, offset, limit)`. The five-file bundle rides every call
-automatically; full files are pulled on demand, never stuffed.
+The Brain has no direct file-system access — it sees only what a `brain_turn` carries. For file inspection, use your own native OpenCode tools (`read`, `grep`, `glob`) to pull the needed code ranges and feed them into the next turn as `[fed-context]`. The five-file context bundle attaches automatically.
 
 ## Personas Roster (local seat resolution)
 
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index 7b8ca2a..66db0bb 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -31,9 +31,13 @@ The LLM is stateless, so the bridge keeps a JSONL transcript per
 (default `~/.config/opencode/brain-sessions`), capped at the last
 40 messages. Pass `session_id` (e.g. `sess-1`) alongside `task_id` and
 every call loads the full session conversation first, then appends both
-new turns. One session thread spans every task in the work session or
-sprint — planning, implementation, QA, and review all share the same
-context. A bare `task_id` with no `session_id` falls back to the
+new turns. When `session_id` is omitted, the bridge automatically
+detects ambient `OPENCODE_SESSION_ID` from the process environment (set
+by OpenCode V2 for every session) — explicit `session_id` always wins,
+and a blank/unset variable means no ambient binding. One session thread
+spans every task in the work session or sprint — planning,
+implementation, QA, and review all share the same context. A bare
+`task_id` with neither explicit nor ambient session id falls back to the
 task-keyed transcript for backward compatibility.
 
 The transcript is replayed on every later turn, so a stored turn
@@ -99,6 +103,7 @@ repo-root `.env`). Real process env wins; blank counts as unset. See
 | `BRAIN_MAX_TOKENS`  | `32768`                                              |
 | `BRAIN_SYSTEM_PROMPT` | `~/.config/opencode/system-prompt.md`              |
 | `BRAIN_SESSIONS_ROOT` | `~/.config/opencode/brain-sessions`                |
+| `OPENCODE_SESSION_ID` | _(ambient, set by OpenCode V2)_ — auto-binds the turn to the active session when `session_id` is omitted; explicit `session_id` always wins |
 | `DECISION_MODEL`    | _(falls back to `BRAIN_MODEL` default)_              |
 | `DECISION_TEMPERATURE` | `1.0`                                             |
 | `BRAIN_RISK_ROUTING_ENABLED` | `true` (routing ON; set a falsy value to disable) |
diff --git a/docs/services.md b/docs/services.md
index 20e5f65..c104de1 100644
--- a/docs/services.md
+++ b/docs/services.md
@@ -97,6 +97,11 @@ OpenCode connects via
 > existing stderr warning). Pass an absolute `project_root` on every
 > call.
 
+> **Brain tool surface:** `mcp-brain` exposes `brain_turn` as its singular
+> automation tool — the only path for planning, QA, and review turns.
+> File inspection uses the caller's native tools (`read`, `grep`, `glob`);
+> the former server-side file helpers were removed.
+
 ## Linux (systemd user units)
 
 Unit files live in `services/`. Install:
diff --git a/mcp-brain-bridge/preflight.py b/mcp-brain-bridge/preflight.py
index f30afcd..045e1d6 100644
--- a/mcp-brain-bridge/preflight.py
+++ b/mcp-brain-bridge/preflight.py
@@ -233,9 +233,17 @@ def validate_request(
     cwd: Optional[Path] = None,
 ) -> ValidatedRequest:
     """Validate a ``brain_turn`` request before any load, attach, or
-    transport. Raises PreflightError on the first malformed field."""
+    transport. Raises PreflightError on the first malformed field.
+    When ``session_id`` is omitted, ambient ``OPENCODE_SESSION_ID``
+    from the environment auto-binds the turn to the active session
+    (session-first) — explicit ``session_id`` always wins."""
+    environ = os.environ if env is None else env
     clean_task = require_bare_task_id(task_id) if task_id is not None else None
-    clean_session = require_session_id(session_id) if session_id is not None else None
+    if session_id is not None:
+        clean_session = require_session_id(session_id)
+    else:
+        _ambient = (environ.get("OPENCODE_SESSION_ID") or "").strip()
+        clean_session = require_session_id(_ambient) if _ambient else None
     binding = (
         "session"
         if clean_session is not None
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 9faf793..1ab3bca 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -2763,10 +2763,12 @@ def brain_turn(
         session_id: Optional session key (e.g. "cando-828") — the
             PRIMARY history key (session-first). Pass it alongside
             ``task_id`` so one thread spans every task in the work
-            session; pass it alone for taskless turns. When omitted and
-            only ``task_id`` is given, history falls back to the
+            session; pass it alone for taskless turns. When omitted, the
+            bridge auto-detects ambient ``OPENCODE_SESSION_ID`` from the
+            environment (explicit wins); with neither explicit nor
+            ambient session id, a lone ``task_id`` falls back to the
             task-keyed transcript for backward compatibility. Omit both
-            for one-off turns with no memory.
+            (and unset the env var) for one-off turns with no memory.
         stage: Optional turn stage, one of plan / implement / qa /
             review / closure. Unknown stages are rejected so a typo can
             never run as an unscoped turn.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index fe33327..7ec98e9 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.52.0</system_version>
+<system_version>9.53.0</system_version>
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index ad520d2..5a897bd 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -104,7 +104,7 @@
 
        "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
        "(If this task was purely documentation, CSS, or trivial, tell the Manager to copy/paste this:) **'[Code Reviewer], please perform the final review.'**"
-       In automatic mode, skip the copy/paste message above and chain the QA/review `brain_turn` yourself under the same `task_id`; the Manager never ferries task text.
+       In automatic mode, skip the copy/paste message above and chain the QA/review `brain_turn` yourself under the active session thread; the Manager never ferries task text.
 </summary_phase>
 </hands_implementation_task>
 ```
@@ -149,7 +149,7 @@
 
        "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
        "(If this task was purely documentation, CSS, or trivial, tell the Manager to copy/paste this:) **'[Code Reviewer], please perform the final review.'**"
-       In automatic mode, skip the copy/paste message above and chain the QA/review `brain_turn` yourself under the same `task_id`; the Manager never ferries task text.
+       In automatic mode, skip the copy/paste message above and chain the QA/review `brain_turn` yourself under the active session thread; the Manager never ferries task text.
 </summary_phase>
 </hands_combined_task>
 ```
diff --git a/prompts/fragments/22-compaction_protocol.md b/prompts/fragments/22-compaction_protocol.md
index 4244343..65586fc 100644
--- a/prompts/fragments/22-compaction_protocol.md
+++ b/prompts/fragments/22-compaction_protocol.md
@@ -9,6 +9,7 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 
 **What must survive any compaction — keep it in the task file, not only the chat:**
 - the active task id and its Kanban lane;
+- the active session ID (OPENCODE_SESSION_ID);
 - the pinned `[fed-context]` block and its file:line citations;
 - the current persona/seat and the locked mode (manual or autopilot);
 - the latest staged diff hash;
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 18c4d98..ffe851a 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -22,7 +22,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`) as their single source of truth.
 - **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
 - **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator. **Exception:** `git mv` is permitted for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
-- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 5-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool, then `git mv` the task to `tasks/qa/` (NO COMMITS ALLOWED). 4) Synchronize the task file's `**File:**` metadata to the new path and re-run lint + stage at the new path. 5) Notify the Manager.
+- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 5-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool, then `git mv` the task to `tasks/qa/` (NO COMMITS ALLOWED). 4) Synchronize the task file's `**File:**` metadata to the new path and re-run lint + stage at the new path. 5) Notify the Manager. When the project uses session-keyed conversation threads, the sequence MUST note that closing a task file does not close the session thread.
 - **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
 - **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load the `task-generator` skill before creating new task files.
 - **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load every available skill matching the project's tech stack before task implementation.
@@ -31,7 +31,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
 - **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
 - **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
-- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage.
+- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage. When the project uses session-keyed conversation threads, the rules MUST note that flushing covers working execution assumptions only — the conversation thread persists across tasks under the active session ID until sprint completion.
 - **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Execution Log & Reasoning` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
@@ -373,7 +373,7 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 - **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
 - **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
 - **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator. **Exception:** `git mv` is permitted for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
-- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 5-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool, then `git mv` the task to `tasks/qa/` (NO COMMITS ALLOWED). 4) Synchronize the task file's `**File:**` metadata to the new path and re-run lint + stage at the new path. 5) Notify the Manager.
+- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 5-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool, then `git mv` the task to `tasks/qa/` (NO COMMITS ALLOWED). 4) Synchronize the task file's `**File:**` metadata to the new path and re-run lint + stage at the new path. 5) Notify the Manager. When the project uses session-keyed conversation threads, the sequence MUST note that closing a task file does not close the session thread.
 - **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
 - **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load the `task-generator` skill before creating new task files.
 - **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load every available skill matching the project's tech stack before task implementation.
@@ -383,7 +383,7 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 - **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
 - **Bilingual Prompt Refactoring & Brainstorming Protocol**: Agents MUST be instructed not to execute raw, informal, or non-English prompts directly. The `prompt-refactor` skill must be loaded, or the Phase 1.5 Multi-Agent Brainstorming Protocol triggered, to translate and expand intent first. Standard XML task blocks are exempt.
 - **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
-- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage.
+- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage. When the project uses session-keyed conversation threads, the rules MUST note that flushing covers working execution assumptions only — the conversation thread persists across tasks under the active session ID until sprint completion.
 - **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
 - **Task-Number Reference Discipline**: `AGENTS.md` MUST include a guardrail restricting task-number references to code comments, CHANGELOG entries, task files, history archives, and HTML comments — never in visible prompt prose, headings, or skill instructions. `docs/conventions.md` MUST contain a `## Task-Number Reference Discipline` section.
diff --git a/system-prompt.md b/system-prompt.md
index ecf0c45..214ec65 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.52.0</system_version>
+<system_version>9.53.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -331,7 +331,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
        "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
        "(If this task was purely documentation, CSS, or trivial, tell the Manager to copy/paste this:) **'[Code Reviewer], please perform the final review.'**"
-       In automatic mode, skip the copy/paste message above and chain the QA/review `brain_turn` yourself under the same `task_id`; the Manager never ferries task text.
+       In automatic mode, skip the copy/paste message above and chain the QA/review `brain_turn` yourself under the active session thread; the Manager never ferries task text.
 </summary_phase>
 </hands_implementation_task>
 ```
@@ -384,7 +384,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
        "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
        "(If this task was purely documentation, CSS, or trivial, tell the Manager to copy/paste this:) **'[Code Reviewer], please perform the final review.'**"
-       In automatic mode, skip the copy/paste message above and chain the QA/review `brain_turn` yourself under the same `task_id`; the Manager never ferries task text.
+       In automatic mode, skip the copy/paste message above and chain the QA/review `brain_turn` yourself under the active session thread; the Manager never ferries task text.
 </summary_phase>
 </hands_combined_task>
 ```
@@ -728,6 +728,7 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 
 **What must survive any compaction — keep it in the task file, not only the chat:**
 - the active task id and its Kanban lane;
+- the active session ID (OPENCODE_SESSION_ID);
 - the pinned `[fed-context]` block and its file:line citations;
 - the current persona/seat and the locked mode (manual or autopilot);
 - the latest staged diff hash;
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 56f2ad6..0bd0914 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -17,6 +17,15 @@ sys.path.insert(0, str(BRIDGE_DIR))
 import server as bridge
 
 
+@pytest.fixture(autouse=True)
+def _no_ambient_session(monkeypatch):
+    """Hermetic default: ambient ``OPENCODE_SESSION_ID`` from the
+    developer's shell must never hijack task-keyed turns. Tests that
+    need ambient binding set it explicitly via ``monkeypatch.setenv``
+    in the test body (which runs after this fixture)."""
+    monkeypatch.delenv("OPENCODE_SESSION_ID", raising=False)
+
+
 def test_extract_single_implementation_block():
     out = 'Think <hands_implementation_task>{"a": 1}</hands_implementation_task> tail'
     blocks = bridge.extract_xml_blocks(out)
diff --git a/tests/test_brain_capability.py b/tests/test_brain_capability.py
index 234f3a1..1ad2dfb 100644
--- a/tests/test_brain_capability.py
+++ b/tests/test_brain_capability.py
@@ -23,18 +23,25 @@ import capability
 import server as bridge
 
 
+@pytest.fixture(autouse=True)
+def _no_ambient_session(monkeypatch):
+    """Hermetic default: ambient ``OPENCODE_SESSION_ID`` from the
+    developer's shell must never hijack task-keyed turns."""
+    monkeypatch.delenv("OPENCODE_SESSION_ID", raising=False)
+
+
 # --- manifest producer ---
 
+
 def test_all_available_tools_report_available():
     manifest = capability.build_manifest(
-        referenced=["lint_task_file", "brain_turn"], required=[])
-    assert manifest == {"lint_task_file": "AVAILABLE",
-                        "brain_turn": "AVAILABLE"}
+        referenced=["lint_task_file", "brain_turn"], required=[]
+    )
+    assert manifest == {"lint_task_file": "AVAILABLE", "brain_turn": "AVAILABLE"}
 
 
 def test_question_tool_is_available():
-    manifest = capability.build_manifest(
-        referenced=["question"], required=["question"])
+    manifest = capability.build_manifest(referenced=["question"], required=["question"])
     assert manifest == {"question": "AVAILABLE"}
 
 
@@ -44,27 +51,29 @@ def test_known_unavailable_registry_is_empty():
 
 def test_unknown_required_tool_fails_closed():
     manifest = capability.build_manifest(
-        referenced=["frobnicate"], required=["frobnicate"])
+        referenced=["frobnicate"], required=["frobnicate"]
+    )
     assert manifest == {"frobnicate": "UNAVAILABLE_REQUIRED"}
 
 
 def test_unknown_optional_tool_is_unavailable_optional():
-    manifest = capability.build_manifest(
-        referenced=["frobnicate"], required=[])
+    manifest = capability.build_manifest(referenced=["frobnicate"], required=[])
     assert manifest == {"frobnicate": "UNAVAILABLE_OPTIONAL"}
 
 
 def test_caller_available_override_wins():
     manifest = capability.build_manifest(
-        referenced=["frobnicate"], required=["frobnicate"],
-        available={"frobnicate"})
+        referenced=["frobnicate"], required=["frobnicate"], available={"frobnicate"}
+    )
     assert manifest == {"frobnicate": "AVAILABLE"}
 
 
 def test_caller_unavailable_override_marks_required():
     manifest = capability.build_manifest(
-        referenced=["lint_task_file"], required=["lint_task_file"],
-        unavailable={"lint_task_file"})
+        referenced=["lint_task_file"],
+        required=["lint_task_file"],
+        unavailable={"lint_task_file"},
+    )
     assert manifest == {"lint_task_file": "UNAVAILABLE_REQUIRED"}
 
 
@@ -75,25 +84,28 @@ def test_unavailable_override_demotes_granted_question_tool():
     for a registry-available name rather than an unknown one.
     """
     manifest = capability.build_manifest(
-        referenced=["question"], required=["question"],
-        unavailable={"question"})
+        referenced=["question"], required=["question"], unavailable={"question"}
+    )
     assert manifest == {"question": "UNAVAILABLE_REQUIRED"}
 
 
 def test_only_three_statuses_exist():
     assert capability.STATUSES == (
-        "AVAILABLE", "UNAVAILABLE_REQUIRED", "UNAVAILABLE_OPTIONAL")
+        "AVAILABLE",
+        "UNAVAILABLE_REQUIRED",
+        "UNAVAILABLE_OPTIONAL",
+    )
     manifest = capability.build_manifest(
-        referenced=["brain_turn", "question", "frobnicate"],
-        required=["frobnicate"])
+        referenced=["brain_turn", "question", "frobnicate"], required=["frobnicate"]
+    )
     assert set(manifest.values()) <= set(capability.STATUSES)
 
 
 def test_internal_registry_name_never_emitted_as_status():
     manifest = capability.build_manifest(
-        referenced=["brain_turn", "question", "frobnicate",
-                    "lint_task_file"],
-        required=["brain_turn", "frobnicate", "lint_task_file"])
+        referenced=["brain_turn", "question", "frobnicate", "lint_task_file"],
+        required=["brain_turn", "frobnicate", "lint_task_file"],
+    )
     assert "KNOWN_UNAVAILABLE" not in manifest.values()
     assert manifest["frobnicate"] == "UNAVAILABLE_REQUIRED"
     assert manifest["question"] == "AVAILABLE"
@@ -105,16 +117,18 @@ def test_empty_referenced_gives_empty_manifest():
 
 # --- gate ---
 
+
 def test_gate_passes_with_no_missing_required():
     manifest = capability.build_manifest(
-        referenced=["lint_task_file", "frobnicate"],
-        required=["lint_task_file"])
+        referenced=["lint_task_file", "frobnicate"], required=["lint_task_file"]
+    )
     assert capability.gate(manifest, stage="qa") is None
 
 
 def test_gate_raises_naming_missing_tools():
     manifest = capability.build_manifest(
-        referenced=["frobnicate"], required=["frobnicate"])
+        referenced=["frobnicate"], required=["frobnicate"]
+    )
     with pytest.raises(capability.CapabilityBlockedError) as exc:
         capability.gate(manifest, stage="review")
     assert "frobnicate" in str(exc.value)
@@ -123,7 +137,8 @@ def test_gate_raises_naming_missing_tools():
 
 def test_gate_error_carries_relay_block():
     manifest = capability.build_manifest(
-        referenced=["frobnicate"], required=["frobnicate"])
+        referenced=["frobnicate"], required=["frobnicate"]
+    )
     with pytest.raises(capability.CapabilityBlockedError) as exc:
         capability.gate(manifest, stage="review")
     block = capability.format_relay_block(exc.value)
@@ -133,6 +148,7 @@ def test_gate_error_carries_relay_block():
 
 # --- single approval rule ---
 
+
 def test_closure_approval_only_exact_phrases():
     assert capability.is_approval("Approved for closure", "closure") is True
     assert capability.is_approval("Close task", "closure") is True
@@ -155,26 +171,31 @@ def test_unknown_gate_never_approves():
 
 # --- stage-implied requirements ---
 
+
 def test_stage_implied_requirements_cover_key_gates():
     assert "lint_task_file" in capability.STAGE_REQUIRED_TOOLS["qa"]
-    assert ("custom_context_commit_and_clean_task"
-            in capability.STAGE_REQUIRED_TOOLS["closure"])
+    assert (
+        "custom_context_commit_and_clean_task"
+        in capability.STAGE_REQUIRED_TOOLS["closure"]
+    )
     assert "brain_turn" in capability.STAGE_REQUIRED_TOOLS["plan"]
 
 
 def test_stage_implied_missing_blocks_even_when_unlisted():
     manifest = capability.evaluate(
-        referenced=[], required=[], stage="qa",
-        unavailable={"lint_task_file"})
+        referenced=[], required=[], stage="qa", unavailable={"lint_task_file"}
+    )
     with pytest.raises(capability.CapabilityBlockedError):
         capability.gate(manifest, stage="qa")
 
 
 # --- brain_turn wiring ---
 
+
 class _FakeResp:
-    def __init__(self, status_code=200, text="", payload=None,
-                 ctype="application/json"):
+    def __init__(
+        self, status_code=200, text="", payload=None, ctype="application/json"
+    ):
         self.status_code = status_code
         self.text = text
         self._payload = payload
@@ -187,9 +208,11 @@ class _FakeResp:
 
 
 def _ok_payload(text="ok"):
-    return {"output": [{"type": "message",
-                        "content": [{"type": "output_text",
-                                     "text": text}]}]}
+    return {
+        "output": [
+            {"type": "message", "content": [{"type": "output_text", "text": text}]}
+        ]
+    }
 
 
 def _stub_httpx(monkeypatch, script, holder):
@@ -233,18 +256,29 @@ def _mk_env(tmp_path, monkeypatch):
 
 
 def test_brain_turn_missing_required_returns_non_verdict_report(
-        tmp_path, monkeypatch, capsys):
+    tmp_path, monkeypatch, capsys
+):
     proj = _mk_env(tmp_path, monkeypatch)
     holder = {}
     _stub_httpx(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
     call = bridge.brain_turn
     target = call.fn if hasattr(call, "fn") else call
-    result = target("review this", task_id="257", project_root=str(proj),
-                    stage="review", required_tools=["frobnicate"])
+    result = target(
+        "review this",
+        task_id="257",
+        project_root=str(proj),
+        stage="review",
+        required_tools=["frobnicate"],
+    )
     assert result["status"] == "REPORT"
     assert "frobnicate" in result["output"]
-    for verdict in ("QA_PASSED", "QA_REJECTED", "VERDICT:",
-                    "PO_REVIEW_PENDING", "APPROVED"):
+    for verdict in (
+        "QA_PASSED",
+        "QA_REJECTED",
+        "VERDICT:",
+        "PO_REVIEW_PENDING",
+        "APPROVED",
+    ):
         assert verdict not in result["output"]
     assert holder.get("calls", 0) == 0
     assert result["retry_count"] == 0
@@ -256,15 +290,21 @@ def test_brain_turn_all_available_reaches_transport(tmp_path, monkeypatch):
     _stub_httpx(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
     call = bridge.brain_turn
     target = call.fn if hasattr(call, "fn") else call
-    result = target("review this", task_id="257", project_root=str(proj),
-                    stage="review", required_tools=["brain_turn"])
+    result = target(
+        "review this",
+        task_id="257",
+        project_root=str(proj),
+        stage="review",
+        required_tools=["brain_turn"],
+    )
     assert result["status"] == "REPORT"
     assert result["output"] == "ok"
     assert holder.get("calls", 0) == 1
 
 
 def test_brain_turn_emits_session_start_manifest_diagnostic(
-        tmp_path, monkeypatch, capsys):
+    tmp_path, monkeypatch, capsys
+):
     proj = _mk_env(tmp_path, monkeypatch)
     holder = {}
     _stub_httpx(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
@@ -284,8 +324,9 @@ def test_brain_turn_persists_manifest_ledger_event(tmp_path, monkeypatch):
     target("hello", task_id="257", project_root=str(proj))
     ledger = proj / "tasks" / ".sessions" / "session_ledger.jsonl"
     assert ledger.is_file()
-    events = [json.loads(line) for line in
-              ledger.read_text(encoding="utf-8").splitlines()]
+    events = [
+        json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()
+    ]
     manifests = [e for e in events if e.get("event") == "capability_manifest"]
     assert len(manifests) == 1
     assert manifests[0]["task_id"] == "257"
diff --git a/tests/test_brain_preflight.py b/tests/test_brain_preflight.py
index fc185f3..0bda894 100644
--- a/tests/test_brain_preflight.py
+++ b/tests/test_brain_preflight.py
@@ -25,7 +25,7 @@ def _mk_project(tmp_path, name="proj"):
 
 
 def _clean_env(monkeypatch):
-    for key in ("BRAIN_PROJECT_ROOT", "BRAIN_WORKSPACE_ROOT"):
+    for key in ("BRAIN_PROJECT_ROOT", "BRAIN_WORKSPACE_ROOT", "OPENCODE_SESSION_ID"):
         monkeypatch.delenv(key, raising=False)
 
 
@@ -100,7 +100,8 @@ def test_nothing_resolves_raises_with_remedy(tmp_path, monkeypatch):
 # --- task / session binding ---
 
 
-def test_task_id_bare_digits_ok(tmp_path):
+def test_task_id_bare_digits_ok(tmp_path, monkeypatch):
+    monkeypatch.delenv("OPENCODE_SESSION_ID", raising=False)
     proj = _mk_project(tmp_path)
     req = preflight.validate_request(task_id="257", project_root=str(proj))
     assert req.binding == "task"
@@ -108,26 +109,30 @@ def test_task_id_bare_digits_ok(tmp_path):
     assert req.session_id is None
 
 
-def test_task_id_suffix_rejected(tmp_path):
+def test_task_id_suffix_rejected(tmp_path, monkeypatch):
+    monkeypatch.delenv("OPENCODE_SESSION_ID", raising=False)
     proj = _mk_project(tmp_path)
     with pytest.raises(preflight.PreflightError, match="task_id"):
         preflight.validate_request(task_id="215qa", project_root=str(proj))
 
 
-def test_session_id_ok(tmp_path):
+def test_session_id_ok(tmp_path, monkeypatch):
+    monkeypatch.delenv("OPENCODE_SESSION_ID", raising=False)
     proj = _mk_project(tmp_path)
     req = preflight.validate_request(session_id="cando-828", project_root=str(proj))
     assert req.binding == "session"
     assert req.session_id == "cando-828"
 
 
-def test_session_id_bad_chars_rejected(tmp_path):
+def test_session_id_bad_chars_rejected(tmp_path, monkeypatch):
+    monkeypatch.delenv("OPENCODE_SESSION_ID", raising=False)
     proj = _mk_project(tmp_path)
     with pytest.raises(preflight.PreflightError, match="session_id"):
         preflight.validate_request(session_id="a/b", project_root=str(proj))
 
 
-def test_both_ids_coexist_session_first(tmp_path):
+def test_both_ids_coexist_session_first(tmp_path, monkeypatch):
+    monkeypatch.delenv("OPENCODE_SESSION_ID", raising=False)
     proj = _mk_project(tmp_path)
     req = preflight.validate_request(
         task_id="257", session_id="s", project_root=str(proj)
@@ -138,13 +143,23 @@ def test_both_ids_coexist_session_first(tmp_path):
     assert req.history_key == "s"
 
 
-def test_session_only_binds_session(tmp_path):
+def test_session_only_binds_session(tmp_path, monkeypatch):
+    monkeypatch.delenv("OPENCODE_SESSION_ID", raising=False)
     proj = _mk_project(tmp_path)
     req = preflight.validate_request(session_id="s", project_root=str(proj))
     assert req.binding == "session"
     assert req.history_key == "s"
 
 
+def test_preflight_uses_ambient_opencode_session_id(tmp_path, monkeypatch):
+    proj = _mk_project(tmp_path)
+    monkeypatch.setenv("OPENCODE_SESSION_ID", "ses_test123")
+    req = preflight.validate_request(project_root=str(proj))
+    assert req.binding == "session"
+    assert req.session_id == "ses_test123"
+    assert req.history_key == "ses_test123"
+
+
 def test_neither_id_is_oneoff_without_root(tmp_path, monkeypatch):
     bare = tmp_path / "bare"
     bare.mkdir()
@@ -321,6 +336,7 @@ def test_brain_turn_task_and_session_coexist_under_session(tmp_path, monkeypatch
 
 
 def test_brain_turn_legacy_shape_still_works(tmp_path, monkeypatch):
+    monkeypatch.delenv("OPENCODE_SESSION_ID", raising=False)
     proj = _mk_project(tmp_path)
     _mk_sys_prompt(tmp_path, monkeypatch)
     monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 84fb7d1..9c26c29 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -43,7 +43,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.52.0"
+    assert shipped == "9.53.0"
 
 
 def test_compaction_protocol_in_shipped_prompt():
```
<!-- END_GIT_DIFF -->
