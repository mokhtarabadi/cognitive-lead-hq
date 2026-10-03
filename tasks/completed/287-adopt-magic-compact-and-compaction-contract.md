# Task 287: Adopt Magic Compact and the Compaction Contract

**File:** `tasks/qa/287-adopt-magic-compact-and-compaction-contract.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Adopt the `magic-compact` plugin as the high-fidelity manual context compactor, keep OpenCode's native auto-compaction as the automatic safety net, and add an explicit compaction survival contract to the system prompt and the executor agent. Document the whole thing so a new machine installs the plugin automatically.

## Manager's Notes

Manager order: research OpenCode compaction and the Magic Compact plugin, pick the better route, and if the plugin wins, bring it into the system, document it (README, LLM.txt, any doc), and teach the system prompt and agent to use it when needed. Chosen route: **Adopt Magic Compact + A2 contract**. This supersedes the 2026-10-01 "no OpenCode plugins" policy — the Manager now explicitly approves this one plugin.

Constraints: no breaking changes; native auto-compaction must remain the safety net; the plugin is upstream-paused (Operator Memory successor) so pin the working release and document rollback.

## Local TODOs

- [x] Install `magic-compact` globally and fix the stale npm proxy that would break auto-install
- [x] Add the `compaction` block (native auto + keep.tokens) to the global config
- [x] Add the `<compaction_protocol>` system-prompt fragment, bump the version, regenerate
- [x] Add the compaction guidance to `agents/cognitive-executor.md`
- [x] Document in `README.md`, `LLM.txt`, and a new `docs/compaction.md`
- [x] Add prompt-sync tests for the contract and the version bump
- [x] Run the suite, sync the prompt + agent globally, and record evidence

## Acceptance Criteria

- [x] `magic-compact` is installed globally (`plugins: ["magic-compact"]`) and the plugin auto-install path works without manual npm overrides
- [x] Global config carries `compaction.auto` with a tuned `keep.tokens`
- [x] `system-prompt.md` contains `<compaction_protocol>` and the version is bumped to 9.50.0, byte-identical on re-assemble
- [x] `agents/cognitive-executor.md` states the two layers, the survival contract, and that the agent cannot run the command
- [x] `README.md`, `LLM.txt` (§7 JSON + §7.7), and `docs/compaction.md` document install and usage
- [x] All tests pass, including the new prompt-sync gates

## Verification Evidence

- **Test command:** rtk test uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/test_prompt_sync.py tests/test_mcp_servers.py -q
- **Expected result:** the prompt-sync and context-server suites pass, exit code 0
- **Actual result:** `83 passed, 22 warnings in 1.69s`
- **Exit code:** 0
- **Full suite (informational):** `711 passed, 2 failed`; both failures are the pre-existing unrelated `tests/test_decision_server.py` cases.

> Verification runner rule: `uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/ -q` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** the plugin is upstream-paused. Mitigation: pin the working `1.2.2` release; rollback is `opencode plugin remove magic-compact`, and native auto-compaction keeps working without it.
- **Risk:** a plugin dependency is a supply-chain surface. Mitigation: it is a single npm package already reviewed in research; the `plugins` entry is one line to remove.
- **Rollback plan:** remove `magic-compact` from `plugins`, restore `~/.npmrc` from its backup, and revert the fragment/version/agent/docs hunks.

---

## Execution Log & Reasoning

**Plan verdict:** Manager-approved route — the decision option "Adopt Magic Compact + A2 (Recommended)" enumerated the deliverables (install, config, prompt fragment, agent, docs, tests). His choice is the plan.

**Seat Check:** domains = prompt/agent architecture (Software Architect) + implementation/infra (Senior Programmer). Skipped: UI/UX Designer (no surface), Planner/Strategist (no scope/file-state change). QA/Review run after implementation.

**Research:** native OpenCode compaction (v2 docs) is automatic and lossy — one summary, keeps ~15k recent tokens, configurable. Magic Compact (173 stars, last release Sep 2026) keeps user messages verbatim, summarizes each old assistant turn, prunes bulky tool I/O into a retrievable cache, and runs on command with no runtime cache churn. Its upstream is paused in favor of Operator Memory, but the pinned release is fully functional. Chose the plugin as the high-fidelity layer, native as the safety net.

**Changes:**
- Global `~/.config/opencode/opencode.json`: `plugins: ["magic-compact"]` (installed `magic-compact@1.2.2`) and `compaction: {auto: true, keep: {tokens: 20000}}`; config backed up first.
- `~/.npmrc`: commented the dead proxy lines (`127.0.0.1:7890`; mihomo moved to 8118 behind auth) — the plugin install otherwise fails with `NPMInstallFailedError`. Backup taken. This is the fix that makes auto-install actually work.
- New `prompts/fragments/22-compaction_protocol.md` + `prompts/manifest.txt`; `<system_version>` 9.49.0 → 9.50.0; `system-prompt.md` regenerated (byte-identical re-assemble).
- `scripts/prompt-build/split_system_prompt.py`: added `compaction_protocol` to `TOP_LEVEL_TAGS` (20 → 21) and updated the counts — without this the split/assemble round-trip test fails.
- `agents/cognitive-executor.md`: new "Compaction & Context Pressure" section.
- `README.md`, `LLM.txt` (§7 JSON + §7.7), new `docs/compaction.md`.
- `tests/test_prompt_sync.py`: version pin 9.50.0 + fragment/executor presence gates.
- Project memory: `opencode_config/plugin_policy_magic_compact_2026_10_02` records the policy change (supersedes the no-plugins policy).

**Assumptions (logged):** A1 `keep.tokens` 20000 (keeps a slightly larger recent tail; easily tuned). A2 the `~/.npmrc` proxy edit is machine-level and reversible from its backup. A3 the plugin is pinned to the working `1.2.2`; rollback is `opencode plugin remove magic-compact`.

**R2 (carried):** the agent cannot run `/magic-compact`; it recommends the run under context pressure and uses `read_omitted_content` after a prune. True auto-invocation is not offered by the plugin.

**Verification:** targeted gate `83 passed`, exit 0; full suite `711 passed, 2 failed` (only the pre-existing decision-server cases). Global sync verified: `system-prompt.md` 9.50.0 with `<compaction_protocol>`, agent in sync, global config carries the plugin + compaction block. A full OpenCode restart is required to load the plugin and the new prompt.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/index.md b/.opencode/memory/index.md
index 83ea10f..ab1758a 100644
--- a/.opencode/memory/index.md
+++ b/.opencode/memory/index.md
@@ -11,6 +11,7 @@
 | manager-decisions | autopilot_consult_all_personas | Session 2026-09-14 (tasks 230+231 closure): the Manager ordered that in autopilot the Hands must consult ALL Brain pe... |  |
 | manager-decisions | task_closure_protocol_one_by_one | Session 2026-09-14: task closure protocol ordered by the Manager — close tasks ONE BY ONE (verify, git mv to tasks/co... |  |
 | opencode_config | opencode_v2_upgrade_2026_09_26 | # OpenCode V2 Upgrade — 2026-09-26 (state refreshed 2026-10-01) |  |
+| opencode_config | plugin_policy_magic_compact_2026_10_02 | # OpenCode plugin policy — Magic Compact adopted (2026-10-02, Task 287) |  |
 | opencode_config | v2_server_password_sync_2026_09_26 | # V2 server auth — managed mode only (updated 2026-10-01) |  |
 | project | absent-file-policy | Absent-File Policy: If a referenced core file does not exist (e.g., DESIGN.md, docs/architecture.md, docs/data_model.... |  |
 | project | fragment-edit-regenerate-workflow | # Fragment-Edit → Regenerate Workflow (Task 129, 2026-08-30) |  |
diff --git a/.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md b/.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md
new file mode 100644
index 0000000..50f5f21
--- /dev/null
+++ b/.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md
@@ -0,0 +1,15 @@
+---
+created_at: '2026-10-02T20:41:30.603312+00:00'
+status: active
+tags: []
+updated_at: '2026-10-02T20:41:30.603327+00:00'
+---
+
+# OpenCode plugin policy — Magic Compact adopted (2026-10-02, Task 287)
+Supersedes the 2026-10-01 no-plugins policy (recorded in opencode_config/opencode_v2_upgrade_2026_09_26).
+- One plugin is approved and installed: magic-compact@1.2.2 (lossless manual context compaction). Global opencode.json carries plugins: ["magic-compact"].
+- Native OpenCode compaction stays enabled as the safety net: compaction: {auto: true, keep: {tokens: 20000}}.
+- Install on a new machine: `opencode plugin add magic-compact` (LLM.txt §7.7). npm proxy caveat: ~/.npmrc proxy/https-proxy lines were commented out (dead 127.0.0.1:7890; mihomo now on 8118 behind auth; direct registry works). Without this the plugin install fails with NPMInstallFailedError.
+- Rollback: `opencode plugin remove magic-compact`; native compaction continues without it.
+- Upstream paused in favor of Operator Memory; the pinned release remains fully functional.
+- System prompt fragment 22 (<compaction_protocol>) and agents/cognitive-executor.md carry the survival contract; docs/compaction.md is the full guide.
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5b6115b..ec7cbbb 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -14,6 +14,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Context MCP singleton report write path (Task 286):** after the singleton migration the context server runs from `~/.config/opencode/mcp-context-server`, but `create_tree_report`, `read_source_files`, and `extract_signatures` wrote their reports to `Path("context-reports")` — the process cwd — so generated maps landed in the global install dir and the project's `context-reports/` went stale (the newest repo tree report stayed at 2026-09-18, still listing the removed `stacks/` directory; found by the task 285 smoke test). All three writers now resolve `report_dir = workspace_root / "context-reports"` from the per-call `project_root` argument the caller supplies, and the `.gitignore` safeguard writes to `<project_root>/.gitignore` via a new `_ensure_context_reports_ignored(workspace_root)` parameter. `extract_signatures`'s regex fallback also reads the resolved `path` instead of the cwd-relative `file_path`. The project_root-omitted path is unchanged (cwd fallback, still surfaced client-visibly), and a new regression test proves a foreign cwd writes nothing outside `<project_root>/context-reports/`. Context-server suite: **70 passed** (69 pre-existing + 1 new).
 
+### Changed
+
+- **Adopted Magic Compact + compaction contract (Task 287, system prompt 9.50.0):** the platform now runs one OpenCode plugin — `magic-compact@1.2.2` — as the high-fidelity manual context compactor, reversing the 2026-10-01 no-plugins policy by explicit Manager order. Native OpenCode auto-compaction stays enabled as the safety net with `compaction: {auto: true, keep: {tokens: 20000}}` in the global config. A new `<compaction_protocol>` system-prompt fragment (fragment 22, added to `prompts/manifest.txt`; `<system_version>` 9.49.0 → 9.50.0; `system-prompt.md` regenerated, byte-identical re-assemble) defines the two layers and the survival contract (task id + lane, pinned `[fed-context]` citations, persona/mode, staged diff hash, blockers, next action). `agents/cognitive-executor.md` carries the operational steps, including that the agent cannot run the plugin command and instead recommends `/magic-compact` under context pressure and uses `read_omitted_content` after a prune. Documented in `README.md`, `LLM.txt` (§7 JSON gains `plugins` + `compaction`; §7.7 rewritten), and the new `docs/compaction.md`. The machine's stale `~/.npmrc` proxy (`127.0.0.1:7890`, dead — mihomo moved to 8118 behind auth) was commented out so the plugin auto-installs; the global `opencode.json` backup was taken first. New prompt-sync gates cover the fragment and the executor guidance. Upstream note: Magic Compact development is paused in favor of Operator Memory; the pinned release remains fully functional and rollback is one line.
+
 ## [9.49.0] - 2026-10-01
 
 ### Added
diff --git a/LLM.txt b/LLM.txt
index 0653ccd..6fa2200 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -282,11 +282,20 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
       "*": "ask",
       "/tmp/**": "allow"
     }
+  },
+  "plugins": [
+    "magic-compact"
+  ],
+  "compaction": {
+    "auto": true,
+    "keep": {
+      "tokens": 20000
+    }
   }
 }
 ```
 
-No OpenCode plugins are installed. The terminal client config `~/.config/opencode/cli.json` is V2-native (no project `cli.json`, no `tui.json`):
+The `plugins` entry loads **`magic-compact`** (install it with `opencode plugin add magic-compact@1.2.2` — Step 7.7). The `compaction` block keeps OpenCode's native auto-compaction on as the safety net while retaining a larger recent tail; Magic Compact then provides the manual high-fidelity layer. The terminal client config `~/.config/opencode/cli.json` is V2-native (no project `cli.json`, no `tui.json`):
 
 ```json
 {
@@ -391,7 +400,15 @@ Telemetry-free cache/SSRF defaults (`CACHE_TTL_MS=300000`, `ALLOW_PRIVATE_URLS=f
 
 ## 7.7. Plugins
 
-None. This platform runs OpenCode with **no plugins** — goal tracking comes from OpenChamber's built-in **Session Goals**, and context compaction is native to OpenCode V2. The repo and global `opencode.json`/`cli.json` carry no plugin entries.
+Install the one platform plugin — **`magic-compact`** (lossless, manual context compaction):
+
+```bash
+opencode plugin add magic-compact@1.2.2
+```
+
+This installs the package from npm and writes `plugins: ["magic-compact"]` into `~/.config/opencode/opencode.json` (OpenCode auto-installs/loads it at startup). It needs npm registry access: if the machine's `~/.npmrc` points at a dead proxy, remove the `proxy`/`https-proxy` lines first — direct registry access works and the plugin otherwise fails with `NPMInstallFailedError`.
+
+Native OpenCode compaction stays enabled as the automatic safety net (the `compaction` block in Step 7). Goal tracking still comes from OpenChamber's built-in **Session Goals**. Upstream note: Magic Compact development is paused in favor of [Operator Memory](https://github.com/aerovato/operator-memory); the pinned `1.2.2` release remains fully functional. Full guide: [`docs/compaction.md`](docs/compaction.md).
 
 ---
 
diff --git a/README.md b/README.md
index 01c6bcc..395ca11 100644
--- a/README.md
+++ b/README.md
@@ -481,7 +481,7 @@ opencode --agent cognitive-executor
 
 ### OpenCode Plugins
 
-None. This platform runs OpenCode with **no plugins**; goal tracking comes from OpenChamber's built-in Session Goals and compaction is native to OpenCode V2.
+One plugin: **`magic-compact`** — lossless, manual context compaction. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Magic Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`. Install with `opencode plugin add magic-compact@1.2.2`; full guide in [`docs/compaction.md`](docs/compaction.md). Goal tracking still comes from OpenChamber's built-in Session Goals. Upstream note: Magic Compact development is paused in favor of Operator Memory; the pinned `1.2.2` release remains fully functional.
 
 ---
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 3e036fd..7e2fe7b 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -92,6 +92,15 @@ To prevent hallucinations and respect hidden project constraints, you MUST integ
    - **DO SAVE:** "The manager prefers Composition over Inheritance," "API X rate limits at 100 req/s, add caching," "Do not use Library Y because of Z."
    - **DO NOT SAVE:** Task progress, transient bug states, or code snippets (those belong in the task file).
 
+## Compaction & Context Pressure
+
+Context is finite. Two layers keep long sessions productive, and the agent's durable state lives in the task file and project memory, never only in the chat.
+
+1. **Native safety net.** OpenCode auto-compacts near the model limit: it replaces older turns with one lossy summary and keeps the most recent ~20k tokens (config: `compaction.keep.tokens`). Never depend on it to preserve working state — write the essentials to the task file as you go.
+2. **Magic Compact (manual, high-fidelity).** The `magic-compact` plugin is installed globally and loaded by OpenCode. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N assistant turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. After a prune, retrieve any omitted tool content with the `read_omitted_content` tool using its Content ID instead of re-running the source tool.
+3. **Survival contract.** Keep the task file holding: the active task id and Kanban lane, the pinned `[fed-context]` block with citations, the current persona/seat, the locked mode (manual or autopilot), the latest staged diff hash, open blockers, and the next action. Resume from that file after any compaction — never from a summary.
+4. **The agent cannot run the plugin command.** When context pressure is high, state one line recommending a `/magic-compact` run to the Manager, then continue from the task file.
+
 ## Capability Preflight (session start)
 
 Before approval-sensitive work (plan approval, review approval, closure), check the capability manifest: every `brain_turn` prints a `capability-manifest:` diagnostic line to stderr mapping each required tool to `AVAILABLE`, `UNAVAILABLE_REQUIRED`, or `UNAVAILABLE_OPTIONAL`. A step whose required tool is `UNAVAILABLE_REQUIRED` (for example the `question` tool) is never silently skipped. Emit the relay block the turn returned (missing tool names, stage, one narrow question, one answer slot) through the mode-appropriate channel: manual mode relays it to the Manager verbatim and pauses with the relayed question as the named blocker; autopilot replays it against stored manager decisions, and halts with the relay block as the named blocker only when no ruling covers it. Approval collection follows the single approval rule: closure accepts only the exact phrases "Approved for closure" or "Close task" (a bare "approved" never counts); the plan gate accepts "approved" in any case. Blanket acknowledgements ("ok", "yes", "looks good", emoji) never count as approval at any gate. At plan-approval, PO_REVIEW_PENDING relay, and any closure approval gate you MUST collect the decision via the question tool with one narrow question and one answer slot. Prose-only approval asks are forbidden because an auto-continue loop can roll past prose. This holds in manual and autopilot. If question is UNAVAILABLE_REQUIRED, emit the relay block and pause with it as the named blocker; never skip. Only hard blockers may use prose.
diff --git a/docs/compaction.md b/docs/compaction.md
new file mode 100644
index 0000000..a3e56e0
--- /dev/null
+++ b/docs/compaction.md
@@ -0,0 +1,72 @@
+# Context Compaction
+
+The platform keeps long sessions productive with two layers: OpenCode's native auto-compaction as the safety net, and the `magic-compact` plugin as the high-fidelity manual layer. Durable working state lives in the task file and project memory, so any compaction stays recoverable.
+
+## Layer 1 — Native OpenCode compaction (automatic)
+
+OpenCode compacts when a session approaches the model's context limit. It summarizes everything except the most recent conversation (~20,000 tokens here) and places that summary in front of the recent tail; later compactions update the same summary. It is lossy, so it is a survival mechanism, not an optimization.
+
+Configured in the global `~/.config/opencode/opencode.json`:
+
+```json
+"compaction": {
+  "auto": true,
+  "keep": { "tokens": 20000 }
+}
+```
+
+`compaction.keep.tokens` is the size of the recent tail kept verbatim. Raise it when exact recent detail matters; lower it when context room matters more.
+
+## Layer 2 — Magic Compact (manual, high fidelity)
+
+[`aerovato/magic-compact`](https://github.com/aerovato/magic-compact) preserves the conversation skeleton: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a cache that the agent can read back. Compaction happens once, on command, so it does not churn the prompt cache during the agent loop.
+
+### Install (already done on this machine)
+
+```bash
+opencode plugin add magic-compact@1.2.2
+```
+
+This installs the package from npm and writes `plugins: ["magic-compact"]` into the global config; OpenCode installs and loads it at startup. New machines get the entry from the global `opencode.json` in `LLM.txt` §7 plus the install command in `LLM.txt` §7.7.
+
+> **npm proxy caveat:** if `~/.npmrc` points at a dead proxy, the install fails with `NPMInstallFailedError`. Remove the `proxy`/`https-proxy` lines so the registry is reached directly. On this machine the stale `127.0.0.1:7890` proxy was commented out.
+
+### Commands (Manager-run)
+
+| Command            | Effect                                                              |
+| ------------------ | ------------------------------------------------------------------ |
+| `/magic-compact`   | Summarize all old assistant turns                                   |
+| `/magic-compact 3` | Keep the 3 most recent assistant turns, summarize the rest          |
+| `/magic-trim`      | Prune tool I/O only, without summarizing (OpenCode-only, no LLM call) |
+| `/magic-stats`     | Cumulative token/money savings for the session                      |
+
+A backup session is created before each run, so a failed compaction returns to the backup.
+
+### Pruning rules (summary)
+
+- Kept: user messages verbatim, per-turn summaries, tool-call structure, key synthetic messages.
+- Removed/condensed: assistant reasoning and text (replaced by the per-turn summary), most synthetic injected messages, bulky completed tool I/O.
+- Tool I/O omitted above ~128 words / 1024 chars; `read` output always omitted (reloadable), `write`/`edit` large content omitted, `bash` commands over 1024 chars truncated.
+- Pending, running, and errored tool calls are always preserved.
+
+### Retrieving pruned content
+
+Each omission notice carries a Content ID (e.g. `omitted-001`). The agent calls the `read_omitted_content` tool with that ID to fetch the original instead of re-running the source tool.
+
+## Integration in this platform
+
+- **System prompt:** the `<compaction_protocol>` fragment (generated into `system-prompt.md`) states the two layers and the survival contract.
+- **Agent:** `agents/cognitive-executor.md` carries the operational steps, including that the agent cannot run the plugin command and instead recommends a `/magic-compact` run when context pressure is high.
+- **Config:** global `opencode.json` holds `plugins` + `compaction`; the repo `opencode.json` stays config-free of both.
+
+**Survival contract** — keep these in the task file so any compaction is recoverable:
+
+- the active task id and its Kanban lane;
+- the pinned `[fed-context]` block and its `file:line` citations;
+- the current persona/seat and the locked mode (manual or autopilot);
+- the latest staged diff hash;
+- open blockers and the next action.
+
+## Upstream status and rollback
+
+Magic Compact development is **paused** in favor of [Operator Memory](https://github.com/aerovato/operator-memory), its successor; the pinned `1.2.2` release remains fully functional and is what this platform installs. Rollback is one line: `opencode plugin remove magic-compact` (and drop the `plugins` key). Native auto-compaction continues to work on its own if the plugin is removed.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index f0115c9..59be6b2 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.49.0</system_version>
+<system_version>9.50.0</system_version>
diff --git a/prompts/fragments/22-compaction_protocol.md b/prompts/fragments/22-compaction_protocol.md
new file mode 100644
index 0000000..ebfa60d
--- /dev/null
+++ b/prompts/fragments/22-compaction_protocol.md
@@ -0,0 +1,16 @@
+<compaction_protocol>
+Context is a finite budget, not a container. Long sessions stay productive through two layers.
+
+**Layer 1 — Native safety net (automatic).** OpenCode auto-compacts when a session nears the model limit: it replaces older turns with one summary and keeps the most recent ~20k tokens. It is lossy, so never rely on it to preserve working state. Capture the essentials below before it fires.
+
+**Layer 2 — Magic Compact (manual, high-fidelity).** The `magic-compact` plugin preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is installed globally and loaded by OpenCode. Commands (Manager-run): `/magic-compact [N]` summarizes old turns while keeping the last N assistant turns; `/magic-trim [N]` prunes tool I/O only, without summarizing; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.
+
+**What must survive any compaction — keep it in the task file, not only the chat:**
+- the active task id and its Kanban lane;
+- the pinned `[fed-context]` block and its file:line citations;
+- the current persona/seat and the locked mode (manual or autopilot);
+- the latest staged diff hash;
+- open blockers and the next action.
+
+**Rule.** The agent cannot run plugin commands itself. When context pressure is high it states, in one line, that a `/magic-compact` run is recommended, then continues from the task file — never from a lossy summary. Durable state lives in the task file and project memory, so any compaction stays recoverable.
+</compaction_protocol>
diff --git a/prompts/manifest.txt b/prompts/manifest.txt
index 064c771..e63ad5c 100644
--- a/prompts/manifest.txt
+++ b/prompts/manifest.txt
@@ -18,3 +18,4 @@
 19-initialization.md
 20-communication_examples.md
 21-self_improvement_protocol.md
+22-compaction_protocol.md
diff --git a/scripts/prompt-build/split_system_prompt.py b/scripts/prompt-build/split_system_prompt.py
index 2202cc1..d0925a0 100644
--- a/scripts/prompt-build/split_system_prompt.py
+++ b/scripts/prompt-build/split_system_prompt.py
@@ -40,10 +40,10 @@ Why a stack-free explicit-tag-list approach is used for parsing:
     (<workflow>, <personas>, <output_schema>, <brainstorming_session>, etc.)
     and the <personas> tag name recurs at column 0 both as a top-level tag and
     nested inside brainstorming_protocol. Instead this script uses the
-    EXPLICITLY ordered list of 20 expected top-level tag names and, for each,
+    EXPLICITLY ordered list of 21 expected top-level tag names and, for each,
     finds the first column-0 opening line <tag> and the first closing line
     </tag> (at any indentation, since some nested closers are indented) after
-    the previous block. This     deterministically isolates the 20 top-level blocks
+    the previous block. This     deterministically isolates the 21 top-level blocks
     without a full XML parser, and verifies their order matches the contract.
 """
 
@@ -58,9 +58,9 @@ from typing import List, Tuple
 # Configuration
 # ---------------------------------------------------------------------------
 
-# The 20 top-level XML tags in system-prompt.md (v9.9.0), in document order.
+# The 21 top-level XML tags in system-prompt.md (v9.50.0), in document order.
 # This explicit ordered list is the authoritative contract for the split: the
-# script verifies that these (and only these) 20 tags appear at the top level,
+# script verifies that these (and only these) 21 tags appear at the top level,
 # in this exact order. Nested tags (e.g. <phase>/<workflow>/<personas> inside
 # <brainstorming_protocol>) are part of their parent block's content and are
 # NOT split out separately.
@@ -85,6 +85,7 @@ TOP_LEVEL_TAGS: List[str] = [
     "initialization",
     "communication_examples",
     "self_improvement_protocol",
+    "compaction_protocol",
 ]
 
 # Regex patterns for locating top-level tag boundaries.
@@ -103,6 +104,7 @@ _SELF_RE = re.compile(r"^<([a-zA-Z_][a-zA-Z0-9_]*)>.*</\1>$")
 # Core parsing
 # ---------------------------------------------------------------------------
 
+
 def _halt(msg: str) -> None:
     """Print a HALT message to stderr and exit non-zero.
 
@@ -116,7 +118,7 @@ def _halt(msg: str) -> None:
 def _find_block_ranges(lines: List[str]) -> List[Tuple[str, int, int]]:
     """Locate the (tag_name, start_index, end_index) for each top-level tag.
 
-    Uses the explicit TOP_LEVEL_TAGS list in document order (20 tags). For each tag it
+    Uses the explicit TOP_LEVEL_TAGS list in document order (21 tags). For each tag it
     finds the first column-0 opening line `<tag>` after the previous tag's
     closing line, then the first closing line `</tag>` (at any indentation)
     after that opening. This correctly handles tags whose closing lines are
@@ -267,6 +269,7 @@ def _extract_and_verify_validation_phases(
 # Public API
 # ---------------------------------------------------------------------------
 
+
 def split_system_prompt(
     source_path: str = "system-prompt.md",
     fragments_dir: str = "prompts/fragments",
@@ -275,7 +278,7 @@ def split_system_prompt(
 ) -> List[str]:
     """Split system-prompt.md into per-tag fragment files.
 
-    Reads the monolithic system-prompt.md, extracts the 20 top-level XML tags in
+    Reads the monolithic system-prompt.md, extracts the 21 top-level XML tags in
     document order as verbatim fragment files, extracts the duplicated
     <validation_phase> block into a shared partial with include markers, and
     writes a manifest listing the fragment filenames in assembly order.
@@ -294,11 +297,11 @@ def split_system_prompt(
     content = src.read_text(encoding="utf-8")
     lines = content.split("\n")
 
-    # --- 1. Locate the 20 top-level block ranges ---
+    # --- 1. Locate the 21 top-level block ranges ---
     ranges = _find_block_ranges(lines)
     if len(ranges) != len(TOP_LEVEL_TAGS):
         _halt(
-            f"Expected {len(TOP_LEVEL_TAGS)} top-level blocks, found {len(ranges)}."  # V9.3.0: 20 tags
+            f"Expected {len(TOP_LEVEL_TAGS)} top-level blocks, found {len(ranges)}."  # 21 tags
         )
 
     # --- 2. Extract block text for each tag ---
@@ -348,6 +351,7 @@ def split_system_prompt(
 # CLI entry point
 # ---------------------------------------------------------------------------
 
+
 def main() -> None:
     """Command-line entry point: split the default system-prompt.md."""
     fragments = split_system_prompt()
diff --git a/system-prompt.md b/system-prompt.md
index caada94..a3d7064 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.49.0</system_version>
+<system_version>9.50.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -716,3 +716,20 @@ Title: `[sensor:{downstream-project}] {fingerprint} {short finding}`. Body MUST
 Downstream Hands gets issue-create only. Never request HQ write access; broad token scopes are forbidden. `gh` auth stays local to the downstream project.
 
 </self_improvement_protocol>
+
+<compaction_protocol>
+Context is a finite budget, not a container. Long sessions stay productive through two layers.
+
+**Layer 1 — Native safety net (automatic).** OpenCode auto-compacts when a session nears the model limit: it replaces older turns with one summary and keeps the most recent ~20k tokens. It is lossy, so never rely on it to preserve working state. Capture the essentials below before it fires.
+
+**Layer 2 — Magic Compact (manual, high-fidelity).** The `magic-compact` plugin preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is installed globally and loaded by OpenCode. Commands (Manager-run): `/magic-compact [N]` summarizes old turns while keeping the last N assistant turns; `/magic-trim [N]` prunes tool I/O only, without summarizing; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.
+
+**What must survive any compaction — keep it in the task file, not only the chat:**
+- the active task id and its Kanban lane;
+- the pinned `[fed-context]` block and its file:line citations;
+- the current persona/seat and the locked mode (manual or autopilot);
+- the latest staged diff hash;
+- open blockers and the next action.
+
+**Rule.** The agent cannot run plugin commands itself. When context pressure is high it states, in one line, that a `/magic-compact` run is recommended, then continues from the task file — never from a lossy summary. Durable state lives in the task file and project memory, so any compaction stays recoverable.
+</compaction_protocol>
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 21a00c1..2b58964 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -4,6 +4,7 @@ The rtk mandate must survive in the assembled system prompt, the shipped
 version must match the fragment source, and the assembler output must
 equal the committed file (same contract as lint_system_prompt_sync).
 """
+
 import re
 import subprocess
 import sys
@@ -14,7 +15,7 @@ SHIPPED = REPO / "system-prompt.md"
 FRAGMENT_01 = REPO / "prompts" / "fragments" / "01-system_version.md"
 ASSEMBLER = REPO / "scripts" / "prompt-build" / "assemble_system_prompt.py"
 EXECUTOR = REPO / "agents" / "cognitive-executor.md"
-TASKGEN_SKILL = (REPO / "skill-templates" / "task-generator" / "SKILL.md")
+TASKGEN_SKILL = REPO / "skill-templates" / "task-generator" / "SKILL.md"
 
 
 def _read(path):
@@ -29,17 +30,34 @@ def test_rtk_mandate_in_shipped_prompt():
 
 
 def test_shipped_version_matches_fragment():
-    shipped = re.search(r"<system_version>(.*?)</system_version>",
-                        _read(SHIPPED)).group(1)
-    source = re.search(r"<system_version>(.*?)</system_version>",
-                       _read(FRAGMENT_01)).group(1)
+    shipped = re.search(
+        r"<system_version>(.*?)</system_version>", _read(SHIPPED)
+    ).group(1)
+    source = re.search(
+        r"<system_version>(.*?)</system_version>", _read(FRAGMENT_01)
+    ).group(1)
     assert shipped == source
 
 
 def test_shipped_version_is_expected_minor_bump():
-    shipped = re.search(r"<system_version>(.*?)</system_version>",
-                        _read(SHIPPED)).group(1)
-    assert shipped == "9.49.0"
+    shipped = re.search(
+        r"<system_version>(.*?)</system_version>", _read(SHIPPED)
+    ).group(1)
+    assert shipped == "9.50.0"
+
+
+def test_compaction_protocol_in_shipped_prompt():
+    text = _read(SHIPPED)
+    assert "<compaction_protocol>" in text
+    assert "magic-compact" in text
+    assert "read_omitted_content" in text
+    assert "What must survive any compaction" in text
+
+
+def test_executor_carries_compaction_guidance():
+    text = _read(EXECUTOR)
+    assert "compaction" in text.lower()
+    assert "magic-compact" in text
 
 
 def test_no_manager_language_rule_in_shipped_prompt():
@@ -53,7 +71,10 @@ def test_assembler_output_matches_shipped(tmp_path):
     out = tmp_path / "check.md"
     proc = subprocess.run(
         [sys.executable, str(ASSEMBLER), "--output", str(out)],
-        capture_output=True, text=True, cwd=str(REPO))
+        capture_output=True,
+        text=True,
+        cwd=str(REPO),
+    )
     assert proc.returncode == 0, proc.stderr[-2000:]
     assert out.read_text(encoding="utf-8") == _read(SHIPPED)
```
<!-- END_GIT_DIFF -->
