# Task 289: Document the agent-callable compact_context tool

**File:** `tasks/qa/289-docs-compact-context-tool.md`
**Source:** manager
**Type:** docs
**Status:** open

## Goal

Update the HQ system prompt, executor agent, and compaction guide to reflect that the agent can now trigger compaction itself via the `compact_context` tool (added to the smart-compact plugin, pushed and smoke-tested live). The old text said the agent cannot run the plugin command, which the new tool makes false.

## Manager's Notes

Manager pushed the plugin and restarted; the live smoke test passed (`compact_context` returned the correct trim and compact messages; plugin loaded 25 times, 0 failures). This task only updates the HQ side so the prompt and docs match the shipped tool.

## Local TODOs

- [x] Update fragment 22 (`<compaction_protocol>`) with the `compact_context` tool and the corrected rule
- [x] Update the executor compaction section
- [x] Add the tool to `docs/compaction.md`
- [x] Bump `<system_version>` 9.51.0 → 9.52.0, regenerate, update the prompt-sync test
- [x] Sync the prompt + agent globally and update the `opencode_config` memory
- [x] Run the gate and record evidence

## Acceptance Criteria

- [ ] Fragment 22 and the executor no longer claim the agent cannot trigger compaction; both name `compact_context`
- [ ] `docs/compaction.md` documents the tool and its inputs
- [ ] `system-prompt.md` is 9.52.0 with `compact_context`, byte-identical on re-assemble
- [ ] `tests/test_prompt_sync.py` pins 9.52.0 and asserts `compact_context`
- [ ] Targeted gate passes with exit code 0

## Verification Evidence

- **Test command:** rtk test uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/test_prompt_sync.py tests/test_mcp_servers.py -q
- **Expected result:** pass, exit code 0
- **Actual result:** `83 passed`
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** none material — docs/prompt text only; the tool already ships.
- **Rollback plan:** revert the fragment/agent/docs hunks and the version bump.

---

## Execution Log & Reasoning

**Plan verdict:** continuation of the Manager-approved "Add it" work — the tool is live, so the docs must match. **Brainstorm:** not required (docs-only). **Seat Check:** domain = prompt/docs (Architect) → requested: Software Architect; skipped: UI/UX Designer (no surface), Planner/Strategist (no scope change).

**Changes:** fragment 22 now states the agent CAN call `compact_context` (with `keepTurns` and `mode`), and the "Rule" was corrected; the executor item 4 mirrors it; `docs/compaction.md` gains an "Agent-callable tool" section; `<system_version>` 9.51.0 → 9.52.0 with a regenerated, byte-identical prompt; the prompt-sync test pins 9.52.0 and asserts `compact_context`.

**Live evidence (plugin side):** `compact_context({mode:"trim"})` → "[smart-compact] tool output will be trimmed on the next request."; `compact_context({keepTurns:9999})` → "[smart-compact] summarized 0 turn(s); …". Plugin loaded 25 times, 0 failures.

**Verification:** targeted gate `83 passed`, exit 0.

**Gate (autopilot):** Code Reviewer `PO_REVIEW_PENDING` — technically approved, Low only. Applied R2 (executor item 2 no longer says "manual", matching fragment 22) and R3 (prompt-sync test also asserts `keepTurns`). Left R1 (changelog ordering) as-is — newest-first is intentional. Re-synced the prompt + agent globally and re-ran the gate: `83 passed`, exit 0. Closure awaits the Manager's exact word.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6a2f63b..966808f 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -18,6 +18,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Adopted Magic Compact + compaction contract (Task 287, system prompt 9.50.0):** the platform now runs one OpenCode plugin — `magic-compact@1.2.2` — as the high-fidelity manual context compactor, reversing the 2026-10-01 no-plugins policy by explicit Manager order. Native OpenCode auto-compaction stays enabled as the safety net with `compaction: {auto: true, keep: {tokens: 20000}}` in the global config. A new `<compaction_protocol>` system-prompt fragment (fragment 22, added to `prompts/manifest.txt`; `<system_version>` 9.49.0 → 9.50.0; `system-prompt.md` regenerated, byte-identical re-assemble) defines the two layers and the survival contract (task id + lane, pinned `[fed-context]` citations, persona/mode, staged diff hash, blockers, next action). `agents/cognitive-executor.md` carries the operational steps, including that the agent cannot run the plugin command and instead recommends `/magic-compact` under context pressure and uses `read_omitted_content` after a prune. Documented in `README.md`, `LLM.txt` (§7 JSON gains `plugins` + `compaction`; §7.7 rewritten), and the new `docs/compaction.md`. The machine's stale `~/.npmrc` proxy (`127.0.0.1:7890`, dead — mihomo moved to 8118 behind auth) was commented out so the plugin auto-installs; the global `opencode.json` backup was taken first. New prompt-sync gates cover the fragment and the executor guidance. Upstream note: Magic Compact development is paused in favor of Operator Memory; the pinned release remains fully functional and rollback is one line.
 
+- **Documented the agent-callable `compact_context` tool (Task 289, system prompt 9.52.0):** the smart-compact plugin gained a `compact_context` tool so the agent can compress the session itself instead of waiting for a Manager slash command; the HQ text that said the agent cannot trigger compaction is now corrected. Fragment 22 (`<compaction_protocol>`) states the agent can call `compact_context` (`keepTurns`, `mode`), the executor item 4 mirrors it, and `docs/compaction.md` gains an "Agent-callable tool" section. `<system_version>` 9.51.0 → 9.52.0, regenerated byte-identical; the prompt-sync test pins 9.52.0 and asserts `compact_context`. Live smoke: `compact_context` returned the correct trim and compact messages; plugin loaded 25 times, 0 failures. Targeted gate: **83 passed**, exit 0.
 - **Adopted Smart Compact as the platform compaction plugin (Task 288, system prompt 9.51.0):** the V1-era `magic-compact` package fails to load on OpenCode 2 (`PluginModule.LoadError` — it exports the V1 plugin shape), so the platform now uses our own V2-native `@mokhtarabadi/opencode-smart-compact` instead. The plugin is a clean-room rewrite (separate repo, 14 passing tests, `tsc --noEmit` clean, `verify:package` OK): it keeps a per-session compaction state in plugin storage and applies it to model-visible messages via `session.hook("context")`, never mutating the stored transcript, with `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`, and the `read_omitted_content` tool. Updated `<compaction_protocol>` (fragment 22), `agents/cognitive-executor.md`, `README.md`, `LLM.txt` (§7 JSON + §7.7), `docs/compaction.md`, and the `opencode_config` memory; `<system_version>` 9.50.0 → 9.51.0 with a regenerated, byte-identical `system-prompt.md`; prompt-sync tests now pin 9.51.0 and assert the smart-compact contract. Native auto-compaction stays on as the safety net. Global `plugins` points at the plugin (local checkout path until it is published to npm). Targeted gate: **83 passed**, exit 0.
 
 ## [9.49.0] - 2026-10-01
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 051c9c3..e6870aa 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -99,7 +99,7 @@ Context is finite. Two layers keep long sessions productive, and the agent's dur
 1. **Native safety net.** OpenCode auto-compacts near the model limit: it replaces older turns with one lossy summary and keeps the most recent ~20k tokens (config: `compaction.keep.tokens`). Never depend on it to preserve working state — write the essentials to the task file as you go.
 2. **Smart Compact (manual, high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) is installed globally and loaded by OpenCode. It is V2-native: it stores a per-session compaction state and applies it to the model-visible messages per request, so it never mutates the stored transcript. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. After a prune, retrieve any omitted tool content with the `read_omitted_content` tool using its Content ID instead of re-running the source tool.
 3. **Survival contract.** Keep the task file holding: the active task id and Kanban lane, the pinned `[fed-context]` block with citations, the current persona/seat, the locked mode (manual or autopilot), the latest staged diff hash, open blockers, and the next action. Resume from that file after any compaction — never from a summary.
-4. **The agent cannot run the plugin command.** When context pressure is high, state one line recommending a `/magic-compact` run to the Manager, then continue from the task file.
+4. **Trigger it yourself, or hand off the command.** The agent cannot run the `/magic-*` slash commands, but it CAN call the `compact_context` tool directly — prefer that when context pressure is high (pass `keepTurns` to protect recent turns, `mode: "trim"` to prune tool output only), state one line about it, then continue from the task file. Fall back to recommending a `/magic-compact` run to the Manager when a tool call is not available.
 
 ## Capability Preflight (session start)
 
diff --git a/docs/compaction.md b/docs/compaction.md
index f13167f..d3c6ca1 100644
--- a/docs/compaction.md
+++ b/docs/compaction.md
@@ -49,6 +49,17 @@ This writes the package (or path) into `plugins` in the global config; OpenCode
 
 Compaction is scheduled by the command and applied on the next model request; summaries are generated at command time with the session's own model.
 
+### Agent-callable tool
+
+The agent can compress the session itself with the `compact_context` tool, which runs the same logic as `/magic-compact` (shared `src/actions.ts` in the plugin, so the paths cannot drift):
+
+| Input | Effect |
+| --- | --- |
+| `keepTurns` (optional) | Most recent turns to keep unsummarized. Default `0` summarizes all. |
+| `mode` (optional) | `compact` (default) summarizes and prunes; `trim` prunes tool output only. |
+
+Invalid input returns a friendly message instead of failing. The slash commands remain available for the Manager.
+
 ### Pruning rules
 
 - Completed tool results over the configured limit (default 1024 chars / 128 words) are pruned to a notice; the original is cached.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 1580bca..fe33327 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.51.0</system_version>
+<system_version>9.52.0</system_version>
diff --git a/prompts/fragments/22-compaction_protocol.md b/prompts/fragments/22-compaction_protocol.md
index a682e9c..4244343 100644
--- a/prompts/fragments/22-compaction_protocol.md
+++ b/prompts/fragments/22-compaction_protocol.md
@@ -3,7 +3,9 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 
 **Layer 1 — Native safety net (automatic).** OpenCode auto-compacts when a session nears the model limit: it replaces older turns with one summary and keeps the most recent ~20k tokens. It is lossy, so never rely on it to preserve working state. Capture the essentials below before it fires.
 
-**Layer 2 — Smart Compact (manual, high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is V2-native: it keeps a per-session compaction state in plugin storage and applies it to the model-visible messages on every request, never mutating the stored transcript, so a bad run cannot corrupt history. It is installed globally and loaded by OpenCode. Commands (Manager-run): `/magic-compact [N]` summarizes old turns while keeping the last N turns; `/magic-trim [N]` prunes tool I/O only, without summarizing; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.
+**Layer 2 — Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is V2-native: it keeps a per-session compaction state in plugin storage and applies it to the model-visible messages on every request, never mutating the stored transcript, so a bad run cannot corrupt history. It is installed globally and loaded by OpenCode. Manager commands: `/magic-compact [N]` summarizes old turns while keeping the last N turns; `/magic-trim [N]` prunes tool I/O only; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.
+
+**The agent can trigger compaction itself.** Call the `compact_context` tool when the context window is under pressure: it runs the same logic as `/magic-compact` (summarize now, prune on the next request). Pass `keepTurns` to protect the most recent turns, and `mode: "trim"` to prune tool output without summarizing. The summary lands on the next request, so continue from the task file meanwhile.
 
 **What must survive any compaction — keep it in the task file, not only the chat:**
 - the active task id and its Kanban lane;
@@ -12,5 +14,5 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 - the latest staged diff hash;
 - open blockers and the next action.
 
-**Rule.** The agent cannot run plugin commands itself. When context pressure is high it states, in one line, that a `/magic-compact` run is recommended, then continues from the task file — never from a lossy summary. Durable state lives in the task file and project memory, so any compaction stays recoverable.
+**Rule.** The agent cannot run the `/magic-*` slash commands itself, but it CAN call `compact_context` directly — prefer that under pressure, and state one line about it. Either way, continue from the task file, never from a lossy summary. Durable state lives in the task file and project memory, so any compaction stays recoverable.
 </compaction_protocol>
diff --git a/system-prompt.md b/system-prompt.md
index cd3759c..ecf0c45 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.51.0</system_version>
+<system_version>9.52.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -722,7 +722,9 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 
 **Layer 1 — Native safety net (automatic).** OpenCode auto-compacts when a session nears the model limit: it replaces older turns with one summary and keeps the most recent ~20k tokens. It is lossy, so never rely on it to preserve working state. Capture the essentials below before it fires.
 
-**Layer 2 — Smart Compact (manual, high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is V2-native: it keeps a per-session compaction state in plugin storage and applies it to the model-visible messages on every request, never mutating the stored transcript, so a bad run cannot corrupt history. It is installed globally and loaded by OpenCode. Commands (Manager-run): `/magic-compact [N]` summarizes old turns while keeping the last N turns; `/magic-trim [N]` prunes tool I/O only, without summarizing; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.
+**Layer 2 — Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is V2-native: it keeps a per-session compaction state in plugin storage and applies it to the model-visible messages on every request, never mutating the stored transcript, so a bad run cannot corrupt history. It is installed globally and loaded by OpenCode. Manager commands: `/magic-compact [N]` summarizes old turns while keeping the last N turns; `/magic-trim [N]` prunes tool I/O only; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.
+
+**The agent can trigger compaction itself.** Call the `compact_context` tool when the context window is under pressure: it runs the same logic as `/magic-compact` (summarize now, prune on the next request). Pass `keepTurns` to protect the most recent turns, and `mode: "trim"` to prune tool output without summarizing. The summary lands on the next request, so continue from the task file meanwhile.
 
 **What must survive any compaction — keep it in the task file, not only the chat:**
 - the active task id and its Kanban lane;
@@ -731,5 +733,5 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 - the latest staged diff hash;
 - open blockers and the next action.
 
-**Rule.** The agent cannot run plugin commands itself. When context pressure is high it states, in one line, that a `/magic-compact` run is recommended, then continues from the task file — never from a lossy summary. Durable state lives in the task file and project memory, so any compaction stays recoverable.
+**Rule.** The agent cannot run the `/magic-*` slash commands itself, but it CAN call `compact_context` directly — prefer that under pressure, and state one line about it. Either way, continue from the task file, never from a lossy summary. Durable state lives in the task file and project memory, so any compaction stays recoverable.
 </compaction_protocol>
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 65712cb..674e3dc 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -43,13 +43,14 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.51.0"
+    assert shipped == "9.52.0"
 
 
 def test_compaction_protocol_in_shipped_prompt():
     text = _read(SHIPPED)
     assert "<compaction_protocol>" in text
     assert "smart-compact" in text
+    assert "compact_context" in text
     assert "read_omitted_content" in text
     assert "What must survive any compaction" in text
```
<!-- END_GIT_DIFF -->
