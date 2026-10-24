# Task 340: System prompt integration for Planner MCP and daily pacing protocol

**File:** `tasks/qa/0340-system-prompt-planner-protocol-integration.md`
**Source:** manager
**Type:** feature
**Status:** in-progress
**Estimate:** 1.5h
**Sprint:** S26-W43
**Milestone:** M01

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Integrate the Planner MCP singleton and the Daily Pacing Protocol into the core system prompt fragments (`prompts/fragments/`), reassemble `system-prompt.md`, bump `<system_version>`, and verify full prompt synchronization so that every Cognitive Lead AI session natively recognizes the planner tools and pacing rules.

## Manager's Notes

- Currently, the planner protocol is documented in `agents/cognitive-executor.md`, but the root system prompt should also natively recognize port 8108 and the daily pacing triggers.
- Must follow the prompt assembly pipeline: edit fragments in `prompts/fragments/`, update `manifest.txt` if needed, run `assemble_system_prompt.py`, bump `<system_version>`, and keep `tests/test_prompt_sync.py` and `scripts/check_docs_sync.py` 100% green.
- Language policy must be respected: internal prompt prose stays English-only, while supporting multi-lingual Manager triggers ("کار امروز رو شروع کنیم").

## Local TODOs

- [x] Identify the target fragment: `prompts/fragments/11-execution_workflow.md` (workflow prose, no new top-level tag, so the splitter manifest stays untouched); update `manifest.txt` only if the assembly script requires it
- [x] Add the planner singleton (`127.0.0.1:8108`), `sprint_daily_agenda`, `claim_next`, and `sprint_check_daily_quota` rules, plus the Daily Pacing Protocol triggers
- [x] Run `python3 scripts/prompt-build/assemble_system_prompt.py`
- [x] Bump `<system_version>` 9.64.1 → 9.65.0 and update the pin in `tests/test_prompt_sync.py`
- [x] Run `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_prompt_sync.py tests/test_mcp_servers.py -q`
- [x] Run the split→assemble round-trip assertion (`test_system_prompt_split_assemble_round_trip`) and `python3 scripts/check_docs_sync.py`
- [x] Update `CHANGELOG.md` under `### Added`

## Acceptance Criteria

- [x] Planner MCP and Daily Pacing Protocol are documented in `prompts/fragments/`
- [x] `system-prompt.md` is reassembled and carries `<system_version>9.65.0</system_version>`
- [x] `tests/test_prompt_sync.py` and the prompt/splitter tests pass with exit code 0
- [x] `test_system_prompt_split_assemble_round_trip` stays green (byte-identical)
- [x] `scripts/check_docs_sync.py` exits 0 with `docs-sync: OK`
- [x] No prompt split/assemble round-trip drift introduced

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest python -m pytest tests/test_prompt_sync.py -q`
- **Expected result:** All prompt sync tests pass
- **Actual result:** `103 passed` (prompt sync + MCP server suites, includes the split/assemble round trip); `docs-sync: OK`
- **Exit code:** 0
- **Round-trip:** `test_system_prompt_split_assemble_round_trip` must stay green and `scripts/check_docs_sync.py` must print `docs-sync: OK`
- **Version target:** `<system_version>9.65.0</system_version>` (pin updated in `tests/test_prompt_sync.py`)

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Editing prompt fragments can introduce assemble/split drift.
- **Mitigation:** Run `assemble_system_prompt.py` and `split_system_prompt.py` round-trip assertions to verify 100% fidelity.
- **Rollback plan:** Revert touched fragment files and `system-prompt.md`.

## Execution Log & Reasoning

Created by Project Planner / Senior Programmer per Manager directive.

**Seat consult (2026-10-24, Manager: "ask project planner and sprint strategist … handle task 340 tonight"):** [Project Planner] GO after four amendments — target fragment named, single test runner, version target pinned, CHANGELOG and round-trip added to the evidence; task is executable as written and depends only on 342, which is closed. [Sprint Strategist] GO tonight — capacity is zero in-progress plus zero QA with room for one review, the task is Must-Do for M01 because it closes the planner loop, and the only real risk is late-session prompt drift, mitigated by running assemble plus the split round-trip and halting on the first drift.

**Implementation:** the protocol landed in `prompts/fragments/11-execution_workflow.md` as a compact block after Step 9 (inside the existing `<execution_workflow>` tag, so `manifest.txt` and the splitter's tag list are untouched). It covers the singleton at `127.0.0.1:8108`, the Kanban-as-source-of-truth rule, `sprint_daily_agenda` on a start-the-day instruction in any language, `claim_next` instead of manual moves with refusals reported, `plan_status`/`qa_budget`, and `sprint_check_daily_quota` → `DAILY_QUOTA_REACHED` → `sprint_stats` then stop, plus the reachability fallback. `<system_version>` goes to 9.65.0 and the pin in `tests/test_prompt_sync.py` follows; `system-prompt.md` reassembled to 109,554 bytes and deployed byte-identical, `mcp-brain` restarted.

**Verification:** 103 passed (prompt sync + MCP servers), exit 0; `test_system_prompt_split_assemble_round_trip` green; `check_docs_sync.py` → `docs-sync: OK`; `grep -c "Planner MCP and daily pacing" system-prompt.md` = 1.

**Autopilot QA/review:** QA → `VERDICT: QA_PASSED` (placement inside the tag, version pin consistency, no protocol contradiction, language policy respected). Reviewer → APPROVED, `PO_REVIEW_PENDING`, no blocking issues.

**Autopilot QA/review:** QA → `VERDICT: QA_PASSED` (placement inside the tag, version pin consistency, no protocol contradiction, language policy respected). Reviewer → APPROVED, `PO_REVIEW_PENDING`, no blocking issues.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index d53ff99..6b7027d 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Planner MCP and daily pacing are native to the system prompt (Task 340):** `prompts/fragments/11-execution_workflow.md` now carries a *Planner MCP and daily pacing* block after Step 9 — the singleton at `127.0.0.1:8108`, `tasks/` Markdown as the single source of truth, `sprint_daily_agenda` on "start today's work" in any language (the Persian trigger is quoted), `claim_next` instead of hand-moving a task file with refusals reported not bypassed, `plan_status`/`qa_budget` for sizing the day (one unresolved review ceiling), and `sprint_check_daily_quota` with `DAILY_QUOTA_REACHED` → present `sprint_stats` and stop claiming. It sits inside the existing tag, so the splitter manifest needed no change. `<system_version>` bumps `9.64.1 → 9.65.0`, the pin in `tests/test_prompt_sync.py` follows, and `system-prompt.md` was reassembled (109,554 bytes). Verified: 103 prompt/splitter tests pass including `test_system_prompt_split_assemble_round_trip` (byte-identical), `check_docs_sync.py` prints `docs-sync: OK`; the prompt was deployed to `~/.config/opencode/system-prompt.md` byte-identical and `mcp-brain` restarted.
+
 - **`DESIGN.md` — Graphite Desk, one contract for both UIs:** the repo had no design system, so the Planner dashboard carried scattered slate/cyan tokens with mixed radii and the Prompt Composer was raw Tailwind defaults with six rainbow preset pills. The Manager reviewed four proposals and chose **A · Graphite Desk**: near-black slate surfaces (`#0b0e14` / `#141a23` / `#1b2430`), hairline borders `#263141`, one mint accent `#5eead4` with ink `#04211d`, four state colours, an 8px grid, a fixed 4/6/8/12 radius scale, Inter for UI and JetBrains Mono for ids/paths/diffs, and no shadows outside modals. The file also fixes component specs (buttons, lanes, tabs, inputs, preset chips, diff blocks, task modal), layout widths (1200 / 960), motion (120/180ms with reduced-motion honoured) and Stitch prompts. The Planner dashboard was re-skinned onto these tokens under task 339 — gradient gauge replaced, lane chips reduced to neutral plus semantic text, hard-coded greys removed — deployed byte-identical to `~/.config/opencode/mcp-planner-server/static/` and served live by `mcp-planner`. The Prompt Composer port is task 343 so it can drop the Tailwind CDN without touching this diff.
 
 - **Planner dashboard overhaul and a guarded task reader (Task 339):** the board is usable with 330+ tasks on it. `GET /api/task?id=<id>` / `?path=tasks/<lane>/<file>.md` returns `{id, path, lane, title, markdown}` so the new full-screen modal can render a task's whole body — todos, acceptance criteria, and `## Factual Git Diff` — with `id` winning when both params arrive. The route is deliberately not a file-read primitive: the new `_safe_task_path` accepts exactly three segments, a lane from `TASK_LANES`, a `.md` suffix, and no absolute prefix, drive colon, backslash, or `..`/`.`, then resolves and re-checks containment inside the project root; authorization reuses `AuthState.project_allowed` and the `_api_status` fallback to a session's first allowed root. Status mapping is explicit — 400 missing param, 401 no session, 403 outside grants *and* unsafe path (never 404, so the route cannot confirm whether a file exists), 404 unknown id, 500 unexpected; the `_api_status` blanket `except → 200 {"error": …}` pattern is not copied. `_task_brief` now carries `path` so cards can deep-link. The dashboard (`static/index.html`, still zero external URLs) caps each lane at `calc(100vh - 280px)` with inner scrolling and a sticky header, collapses the Archive lane behind an `Archive (N)` toggle remembered in `localStorage`, adds a client-only search input filtering by id/name/title, and opens the task modal through one delegated listener on the grid so the 30 s poll cannot drop the binding. The Markdown renderer is inline and self-contained: source is HTML-escaped first, then fences, headings, lists, task checkboxes, blockquotes, tables, and inline emphasis are added, diffs get `--success`/`--danger` line colouring, rendering stops at 2000 lines, and links are limited to same-origin or in-page targets. Docs: component `README.md` route table plus `DECISIONS.md` ADR-007. Verified: 97/97 planner tests pass (17 new: by id, by path, int-normalized id, 404, 400, eight traversal shapes at 403, route registration, 401, cross-project viewer 403, traversal over HTTP, open mode), `py_compile` and a JS parse of the inline script are clean, deployed `server.py`/`README.md`/`DECISIONS.md`/`static/index.html` are byte-identical to the repo copies, and the live unit on `127.0.0.1:8108` serves the new dashboard markup while `/api/task` answers 401 without a session and 400 with no param.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 42c1ed6..63ed0a1 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.64.1</system_version>
\ No newline at end of file
+<system_version>9.65.0</system_version>
\ No newline at end of file
diff --git a/prompts/fragments/11-execution_workflow.md b/prompts/fragments/11-execution_workflow.md
index d5de596..57b96e8 100644
--- a/prompts/fragments/11-execution_workflow.md
+++ b/prompts/fragments/11-execution_workflow.md
@@ -42,5 +42,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 9. **Step 9: Next Task Transition (Sprint Strategist)**
    - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
 
+**Planner MCP and daily pacing.** The Planner singleton runs at `127.0.0.1:8108` and reads `tasks/` Markdown as the single source of truth; it never replaces the Kanban files. Use it at five moments: when the Manager says start today's work — in any language, including "کار امروز رو شروع کنیم" — call `sprint_daily_agenda` before touching a task file; to take work, call `claim_next(project_root, task_id)` instead of moving the file by hand, and report a refusal with its stated reason instead of bypassing it; to size the day, `plan_status` and `qa_budget` (one unresolved review is the ceiling); to close work, `sprint_check_daily_quota`, and when it returns `DAILY_QUOTA_REACHED`, present `sprint_stats` and stop claiming for the day. If the server is unreachable, fall back to the Kanban workflow and say so plainly — never stall waiting for it.
+
 **Night mode override.** When the Manager hands over the night ("night mode", "100% autopilot until morning"), `<night_mode>` governs: the Step 6 QA gate, the Step 7 review gate, and the Step 8 closure approval are pre-authorized and played by the Hands, and the question tool is not used until he returns. Every other step in this pipeline is unchanged.
 </execution_workflow>
\ No newline at end of file
diff --git a/system-prompt.md b/system-prompt.md
index 49bed81..130c06f 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.64.1</system_version>
+<system_version>9.65.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -478,6 +478,8 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 9. **Step 9: Next Task Transition (Sprint Strategist)**
    - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
 
+**Planner MCP and daily pacing.** The Planner singleton runs at `127.0.0.1:8108` and reads `tasks/` Markdown as the single source of truth; it never replaces the Kanban files. Use it at five moments: when the Manager says start today's work — in any language, including "کار امروز رو شروع کنیم" — call `sprint_daily_agenda` before touching a task file; to take work, call `claim_next(project_root, task_id)` instead of moving the file by hand, and report a refusal with its stated reason instead of bypassing it; to size the day, `plan_status` and `qa_budget` (one unresolved review is the ceiling); to close work, `sprint_check_daily_quota`, and when it returns `DAILY_QUOTA_REACHED`, present `sprint_stats` and stop claiming for the day. If the server is unreachable, fall back to the Kanban workflow and say so plainly — never stall waiting for it.
+
 **Night mode override.** When the Manager hands over the night ("night mode", "100% autopilot until morning"), `<night_mode>` governs: the Step 6 QA gate, the Step 7 review gate, and the Step 8 closure approval are pre-authorized and played by the Hands, and the question tool is not used until he returns. Every other step in this pipeline is unchanged.
 </execution_workflow>
 
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 17cdb22..cb2896c 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.64.1"
+    assert shipped == "9.65.0"
 
 
 def test_executor_carries_compaction_guidance():
```
<!-- END_GIT_DIFF -->
