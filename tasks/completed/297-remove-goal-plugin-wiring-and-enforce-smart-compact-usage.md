# Task 297: Remove goal-plugin wiring and enforce smart-compact usage

**File:** `tasks/qa/297-remove-goal-plugin-wiring-and-enforce-smart-compact-usage.md`
**Source:** manager
**Type:** chore
**Status:** open
**Risk-Tier:** T1 standard

## Goal

Remove every live goal-plugin and Session Goals reference in cognitive-lead-hq since the goal plugin is no longer used. Learn the opencode-smart-compact plugin from its own repo, then strengthen the cognitive-executor guidance (and the Brain bridge only if truly needed) so the executor intelligently calls compaction and keeps a small clean context.

## Manager's Notes

Direct Manager order (translated from Persian): "Define a new task in the current open sprint and run it through planning, implementation, QA, code review, then report to me. Goal: look through the project and delete every reference to the goal plugin or goals wherever referenced. We no longer use the goal plugin. We have a plugin that compresses the session with features like magic-compact. First learn it by reading its repository, then mention it in the cognitive executor and, only if really needed, in the Brain, and force it so the cognitive executor intelligently always calls it to keep a clean small washed context. All of this lands in one task."

## Scope

In scope:
- Goal-plugin and Session Goals wiring: agents/cognitive-executor.md Goal Lifecycle section, prompts fragments mirroring it, README.md and LLM.txt Session Goals lines, .opencode/memory Session Goals lines, opencode.json goal entries if any, docs mentions
- Generic English word goal meaning objective (task Goal headings, alignment prose) stays untouched
- docs/history, tasks/archive, CHANGELOG history lines stay immutable
- opencode-smart-compact repo (../opencode-smart-compact): README, package.json, src hooks and tools (compact_context, read_omitted_content, slash commands)
- Strengthened executor compaction guidance with intelligent call triggers plus Brain mention only if proven needed
- system-prompt.md rebuilt from fragments, never hand-edited

Out of scope:
- External repos stay untouched, changes land only in cognitive-lead-hq
- No git add/commit/push by Hands (ZAC holds)

## Local TODOs

- [x] Inventory goal-plugin and Session Goals hits with grep evidence
- [x] Learn smart-compact repo (README, tools, triggers)
- [x] Remove goal-plugin wiring, keep generic goal prose
- [x] Strengthen executor compaction enforcement
- [x] Rebuild system-prompt and run verification gates

## Acceptance Criteria

- [x] AC1: targeted grep for goal-plugin, Session Goals, get_goal, create_goal, update_goal returns zero live hits outside history
- [x] AC2: generic task Goal prose still intact
- [x] AC3: executor documents smart-compact triggers and calls compact_context under pressure
- [x] AC4: system-prompt in sync with fragments, full suite passes with evidence

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q
- **Expected result:** pass exit 0
- **Actual result:** 541 passed, 22 warnings in 4.46s (exit 0) with OPENCODE_SESSION_ID unset; AC1 grep exit 1 zero hits; AC2 prose intact; json valid; index zero Session Goals
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** over-deletion removes generic goal prose or breaks goal-tool tests
- **Rollback plan:** worktree diff revert before staging, history reachable via git log --follow

---

## Execution Log & Reasoning

- Seat Check: domains are prompt contract plus docs and memory cleanup plus plugin guidance → Software Architect + Senior Programmer requested. Trigger sets all explicit miss, no user-visible surface. UI/UX Designer, QA, Reviewer, Planner, Strategist skipped at planning.
- Brainstorm: not required — single-domain reversible docs and config cleanup.
- Prompt-refactor applied: translated Persian direct order to technical English, expanded scope from targeted grep and compact repo read, structured as T1 chore with explicit keeps.
- Brain plan verdict 2026-10-06: Architect 2-seat consult APPROVED plan P0-P4. Keeps: generic goal prose untouched, history immutable, external repos untouched, ZAC. Selected path: inventory plus compact learn first, targeted goal-wiring deletes, executor trim enforcement, prompt and memory rebuild, verify plus stage. Awaiting Manager plan approval before implementation XML.
- Manager plan approval 2026-10-06: "Approved" via question tool. Routed back through Brain for Senior Programmer implementation XML. Executed XML verbatim.
- Execution: Step1 inventory found executor Goal Lifecycle 350-384, README 481, LLM 431, memory opencode_config 17-18; no prompts mirror, no opencode.json goal entries, no docs hits. Compact repo learned: compact_context tool with keepTurns and trim mode, read_omitted_content by Content ID, slash commands magic-compact, magic-trim, magic-stats. Step2 deleted Goal Lifecycle section plus three Session Goals sentences plus memory line. Step3 added trigger item 5 to executor Compaction section. Brain mention skipped: executor already holds direct compact_context access (AGENTS.md equivalent guidance in place). Step4 system-prompt rebuild verified in sync with zero fragment edits needed. Memory index rebuilt to 21 entries with zero Session Goals namespaces and no index content change required.
- Autopilot locked 2026-10-06 per Manager order for end-to-end completion of this task.
- Brain QA verdict autopilot round: QA_PASSED with zero live goal wiring and intact setup flow.
- Code Reviewer verdict autopilot round: APPROVED to PO_REVIEW_PENDING with no functional defects. R2 confirmations recorded in Verification Evidence. Awaiting Manager explicit closure words.
- Assumption A1: OpenChamber built-in Session Goals references count as goal-plugin wiring per Manager order and were removed. Reason: Manager ordered every goal reference deleted except generic prose.
- Assumption A2: goal lifecycle tool calls (get_goal, create_goal, update_goal) have no live callers left after section delete. Reason: targeted grep returns zero hits outside history.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/opencode_config/opencode_v2_upgrade_2026_09_26.md b/.opencode/memory/opencode_config/opencode_v2_upgrade_2026_09_26.md
index c711586..5418c3e 100644
--- a/.opencode/memory/opencode_config/opencode_v2_upgrade_2026_09_26.md
+++ b/.opencode/memory/opencode_config/opencode_v2_upgrade_2026_09_26.md
@@ -14,5 +14,5 @@ updated_at: '2026-10-01T00:00:00.000000+00:00'
 - MCP block uses native V2 `mcp.servers` with `disabled:false` + `timeout:{catalog,execution}`.
 - V1→V2 DB migration key `migration.v1-v2` reached phase `completed`.
 - OpenChamber **2.1.0** active (latest on npm).
-- Plugin policy: **no OpenCode plugins** — the goal plugin and DCP/compress plugin were removed 2026-10-01 per Manager order. OpenChamber's built-in Session Goals replace the goal plugin.
+- Plugin policy: **no OpenCode plugins** — the goal plugin and DCP/compress plugin were removed 2026-10-01 per Manager order.
 - Supersedes: opencode_config/global_goal_plugin_upgrade_2026_08_27 (deleted), plugin_policy_dcp_only_2026_09_08 (deleted), plugins_full_v2_status_2026_09_26 (deleted).
diff --git a/CHANGELOG.md b/CHANGELOG.md
index fb55262..a3f1045 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -29,6 +29,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Removed
 
+- **Removed goal-plugin and Session Goals wiring, enforced smart-compact:** deleted the Goal Lifecycle section from the executor agent, removed Session Goals sentences from README, LLM.txt, and the V2 upgrade memory, and documented intelligent `compact_context` triggers in the executor Compaction section. Generic task Goal prose left intact. External repos untouched.
 - **Retired manager-decision wiring, kept LLM.txt as setup entry point:** removed prompt registry lines, executor consult blocks, docs contract file, skill templates, MCP decision server purged entirely with its service units, decision tests removed or stripped, memory namespaces deleted with index rebuild. Live `LLM.txt` references in README and docs kept intact; decision sections inside `LLM.txt` itself removed. External personal decisions repo kept untouched. History paths unchanged.
 - **Lean session-first Brain bridge refactor (Task 292):** Removed dead tools `read_file`, `grep_files`, and `get_context_bundle` from `mcp-brain-bridge` (Hands use native OpenCode `read`/`grep`/`glob`; the five-file bundle still auto-attaches internally). Removed the multipart chunking allocator (`_allocate_attachments`, `_render_attachment`, `_marker_room`, `_open_overhead`, `_validate_attachment_resume`, `_attachment_priority`, priority tuples) and the `attachment_resume` turn parameter, plus the `history.pop(1)` middle-turn drop loop and the `_read_file_impl` / `_grep_files_impl` helpers with their grep/read guardrail constants.
 
diff --git a/LLM.txt b/LLM.txt
index d7b4bbe..3498b55 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -428,7 +428,7 @@ This writes the spec into `plugins` in `~/.config/opencode/opencode.json`; OpenC
 
 The V1-era `magic-compact` package does not load on OpenCode V2 (it exports the V1 plugin shape); `smart-compact` is the V2-native replacement, so do not add `magic-compact` to `plugins`.
 
-Native OpenCode compaction stays enabled as the automatic safety net (the `compaction` block in Step 7). Goal tracking still comes from OpenChamber's built-in **Session Goals**. Full guide: [`docs/compaction.md`](docs/compaction.md).
+Native OpenCode compaction stays enabled as the automatic safety net (the `compaction` block in Step 7). Full guide: [`docs/compaction.md`](docs/compaction.md).
 
 ---
 
diff --git a/README.md b/README.md
index 53a63b0..c956022 100644
--- a/README.md
+++ b/README.md
@@ -478,7 +478,7 @@ opencode --agent cognitive-executor
 
 ### OpenCode Plugins
 
-Two plugins: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) — lossless, V2-native context compaction, maintained in its own repo. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Smart Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. It never mutates the stored transcript — it stores a per-session compaction state and applies it to the model-visible messages per request. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`. Install with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` (the Git spec, until it is published to npm); full guide in [`docs/compaction.md`](docs/compaction.md). Plus **`todolist`** (`opencode-todolist`) — restores the V1 session todo tools (`todowrite`/`todoread`) removed in V2, with a live TUI sidebar strip. Install with `opencode plugin add opencode-todolist` and enable the strip via `plugins` in `~/.config/opencode/cli.json`. Goal tracking still comes from OpenChamber's built-in Session Goals.
+Two plugins: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) — lossless, V2-native context compaction, maintained in its own repo. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Smart Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. It never mutates the stored transcript — it stores a per-session compaction state and applies it to the model-visible messages per request. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`. Install with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` (the Git spec, until it is published to npm); full guide in [`docs/compaction.md`](docs/compaction.md). Plus **`todolist`** (`opencode-todolist`) — restores the V1 session todo tools (`todowrite`/`todoread`) removed in V2, with a live TUI sidebar strip. Install with `opencode plugin add opencode-todolist` and enable the strip via `plugins` in `~/.config/opencode/cli.json`.
 
 ---
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 819f65c..233cb6d 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -99,6 +99,7 @@ Context is finite. Two layers keep long sessions productive, and the agent's dur
 2. **Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) is installed globally and loaded by OpenCode. It is V2-native: it stores a per-session compaction state and applies it to the model-visible messages per request, so it never mutates the stored transcript. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. After a prune, retrieve any omitted tool content with the `read_omitted_content` tool using its Content ID instead of re-running the source tool.
 3. **Survival contract.** Keep the task file holding: the active task id and Kanban lane, the pinned `[fed-context]` block with citations, the current persona/seat, the locked mode (manual or autopilot), the latest staged diff hash, open blockers, and the next action. Resume from that file after any compaction — never from a summary.
 4. **Trigger it yourself, or hand off the command.** The agent cannot run the `/magic-*` slash commands, but it CAN call the `compact_context` tool directly — prefer that when context pressure is high (pass `keepTurns` to protect recent turns, `mode: "trim"` to prune tool output only), state one line about it, then continue from the task file. Fall back to recommending a `/magic-compact` run to the Manager when a tool call is not available.
+5. **Call it before heavy payloads, not after stalling.** Invoke `compact_context` yourself at these triggers: context pressure is high, 50+ steps ran without measurable progress, before a plan-approval handoff, and before QA or review turns carry a large diff. Use `mode: "trim"` when only tool output is bulky and full `compact` when turns are stale. Never re-run a source tool for pruned output — retrieve it with `read_omitted_content` by Content ID. The Brain bridge needs no change: the executor already holds direct `compact_context` access, so no Brain mention is added.
 
 ## Capability Preflight (session start)
 
@@ -345,45 +346,6 @@ than invent.
    NEVER auto-commit. QA/review run through the Brain Bridge below, or as
    Manager-directed direct review.
 
-## Goal Lifecycle (heavy implementation tasks only)
-
-The Hands run inside OpenCode, which provides session-scoped goal tools
-(`get_goal`, `create_goal`, `update_goal`, plus pause/resume status).
-The system prompt also carries the goal mode policy. Use them as follows.
-Light tasks (single-file edits, docs-only changes, quick fixes) skip the
-goal entirely — goal overhead must never exceed the task itself.
-
-1. **Create on receipt.** When a heavy implementation task arrives
-   (multi-file, multi-phase, or explicitly ordered as a Goal), call
-   `get_goal` first. If a matching non-closed goal exists, continue under
-   it. Otherwise `create_goal` once, with the task objective and its
-   Acceptance Criteria as success criteria.
-2. **Work under the goal.** Every implementation step serves the goal
-   objective. If new instructions arrive mid-task, capture them against
-   the goal before acting.
-3. **Pause BEFORE asking — never ask with the goal active.** If the task
-   truly cannot proceed without the Manager, call
-   `update_goal_status(paused)` FIRST, then ask exactly one precise
-   question via the question tool, then stop. Reason: while the goal stays active the goal
-   plugin auto-resends the continuation prompt on your next turn, which
-   re-issues the objective instead of waiting for the answer — the
-   Manager ends up answering the same objective twice. Pausing is
-   permitted ONLY for the narrow cases where asking is allowed — never
-   as a substitute for permitted autonomous action. No orphaned pauses:
-   every pause names the blocker. Carve-out: the supervised plan-approval
-   pause and Relay questions are allowed pauses — they carry the plan or
-   the relayed question as the named blocker.
-4. **Resume WITH the answer.** When the Manager answers, call
-   `update_goal_status(active)` and continue from the recorded state,
-   carrying the Manager's answer forward as the deciding input. Never
-   resume without the answer in hand. Do not restart completed steps.
-5. **Close with evidence.** Close the goal only when the task's
-   Acceptance Criteria are verified against real artifacts (tests,
-   diffs, command output). The closure evidence mirrors the task's
-   Verification Evidence. Goal closure and Kanban closure stay aligned:
-   no goal left open behind a closed task, no task closed with its goal
-   unmet.
-
 ## Brain Bridge
 
 The `brain` MCP server (`mcp-brain-bridge/server.py`, one tool:
```
<!-- END_GIT_DIFF -->
