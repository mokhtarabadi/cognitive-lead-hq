# Task 288: Adopt the Smart Compact Plugin in HQ

**File:** `tasks/qa/288-adopt-smart-compact-plugin.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Point the HQ documentation, system prompt, agent, and memory at our own V2-native `@mokhtarabadi/opencode-smart-compact` plugin, which replaces the V1-era `magic-compact` package that does not load on OpenCode 2. Native auto-compaction stays as the safety net; Smart Compact is the manual high-fidelity layer.

## Manager's Notes

Manager order: review the smart-compact project, learn it, update our docs relative to it if needed, install it locally, then restart OpenCode and smoke test for correctness and safety. The plugin repo (`mokhtarabadi/opencode-smart-compact`) is maintained separately; this task only updates the HQ side and the global config.

## Local TODOs

- [x] Review the smart-compact repo and run its gates (typecheck, 14 tests, verify:package)
- [x] Rewrite `<compaction_protocol>` (fragment 22) and the executor compaction section for smart-compact
- [x] Update `README.md`, `LLM.txt` (§7 JSON + §7.7), and `docs/compaction.md`
- [x] Update the `opencode_config` memory to the smart-compact policy
- [x] Bump `<system_version>` 9.50.0 → 9.51.0, regenerate, update prompt-sync tests
- [x] Point global `plugins` at the plugin and sync the prompt + agent globally

## Acceptance Criteria

- [ ] No HQ doc, prompt fragment, agent, or memory presents `magic-compact` as the active plugin (historical CHANGELOG/history stays)
- [ ] `system-prompt.md` is 9.51.0, contains `<compaction_protocol>` referencing smart-compact, byte-identical on re-assemble
- [ ] `tests/test_prompt_sync.py` pins 9.51.0 and asserts the smart-compact contract
- [ ] Global `opencode.json` `plugins` points at `@mokhtarabadi/opencode-smart-compact` (or the local checkout) with `compaction` intact
- [ ] Targeted prompt-sync + context-server suites pass with exit code 0

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

- **Risk:** the plugin is loaded by OpenCode only after a restart; the smoke test is pending.
- **Rollback plan:** point `plugins` back to the previous entry or remove it; revert the HQ doc/prompt hunks.

---

## Execution Log & Reasoning

**Review:** the smart-compact repo is a clean-room V2-native rewrite — 9 source modules, 14 passing unit tests, `tsc --noEmit` clean, `verify:package` OK. It never mutates the stored transcript; it stores per-session state and applies it to model-visible messages via `session.hook("context")`, which is exactly the V2-native design we chose over porting the V1 plugin.

**Changes:** rewrote fragment 22 and the executor compaction section; updated `README.md`, `LLM.txt` (§7 JSON `plugins` entry + §7.7), and `docs/compaction.md`; updated the `opencode_config` memory; bumped `<system_version>` to 9.51.0 and regenerated; updated the prompt-sync tests; set global `plugins` to the plugin's local path (until it is published to npm) and synced the prompt + agent globally.

**Pending:** OpenCode restart to load the plugin, then the live smoke test (`/magic-compact`, `/magic-trim`, `/magic-stats`, `read_omitted_content`).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/index.md b/.opencode/memory/index.md
index ab1758a..27bbaaf 100644
--- a/.opencode/memory/index.md
+++ b/.opencode/memory/index.md
@@ -11,7 +11,7 @@
 | manager-decisions | autopilot_consult_all_personas | Session 2026-09-14 (tasks 230+231 closure): the Manager ordered that in autopilot the Hands must consult ALL Brain pe... |  |
 | manager-decisions | task_closure_protocol_one_by_one | Session 2026-09-14: task closure protocol ordered by the Manager — close tasks ONE BY ONE (verify, git mv to tasks/co... |  |
 | opencode_config | opencode_v2_upgrade_2026_09_26 | # OpenCode V2 Upgrade — 2026-09-26 (state refreshed 2026-10-01) |  |
-| opencode_config | plugin_policy_magic_compact_2026_10_02 | # OpenCode plugin policy — Magic Compact adopted (2026-10-02, Task 287) |  |
+| opencode_config | plugin_policy_magic_compact_2026_10_02 | # OpenCode plugin policy — Smart Compact (updated 2026-10-03) |  |
 | opencode_config | v2_server_password_sync_2026_09_26 | # V2 server auth — managed mode only (updated 2026-10-01) |  |
 | project | absent-file-policy | Absent-File Policy: If a referenced core file does not exist (e.g., DESIGN.md, docs/architecture.md, docs/data_model.... |  |
 | project | fragment-edit-regenerate-workflow | # Fragment-Edit → Regenerate Workflow (Task 129, 2026-08-30) |  |
diff --git a/.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md b/.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md
index 9f23167..aec24cc 100644
--- a/.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md
+++ b/.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md
@@ -1,15 +1,16 @@
 ---
-created_at: '2026-10-02T20:41:30.603312+00:00'
+created_at: '2026-10-03T07:26:37.555606+00:00'
 status: active
 tags: []
-updated_at: '2026-10-02T20:41:30.603327+00:00'
+updated_at: '2026-10-03T07:26:37.555618+00:00'
 ---
 
-# OpenCode plugin policy — Magic Compact adopted (2026-10-02, Task 287)
-Supersedes the 2026-10-01 no-plugins policy (recorded in opencode_config/opencode_v2_upgrade_2026_09_26).
-- One plugin is approved and installed: magic-compact@1.2.2 (lossless manual context compaction). Global opencode.json carries plugins: ["magic-compact"].
-- Native OpenCode compaction stays enabled as the safety net: compaction: {auto: true, keep: {tokens: 20000}}.
-- Install on a new machine: `opencode plugin add magic-compact@1.2.2` (LLM.txt §7.7). npm proxy caveat: ~/.npmrc proxy/https-proxy lines were commented out (dead 127.0.0.1:7890; mihomo now on 8118 behind auth; direct registry works). Without this the plugin install fails with NPMInstallFailedError.
-- Rollback: `opencode plugin remove magic-compact`; native compaction continues without it.
-- Upstream paused in favor of Operator Memory; the pinned release remains fully functional.
-- System prompt fragment 22 (<compaction_protocol>) and agents/cognitive-executor.md carry the survival contract; docs/compaction.md is the full guide.
+# OpenCode plugin policy — Smart Compact (updated 2026-10-03)
+One plugin is approved and installed: `@mokhtarabadi/opencode-smart-compact` (V2-native context compaction, our own repo `mokhtarabadi/opencode-smart-compact`). It REPLACES the V1 `magic-compact` package, which fails to load on OpenCode 2 (`PluginModule.LoadError: Plugin must export a default definition with an id and an effect or setup function`).
+- Global opencode.json: `plugins: ["@mokhtarabadi/opencode-smart-compact"]` (or a local checkout path until the package is published to npm).
+- Native OpenCode compaction stays on: `compaction: {auto: true, keep: {tokens: 20000}}`.
+- smart-compact is V2-native: it stores per-session state in plugin storage and applies it to model-visible messages via `session.hook("context")`; it never mutates the stored transcript. Commands `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`; tool `read_omitted_content`.
+- Repo gates: `npm run typecheck`, `npm test` (14 tests), `npm run verify:package`. CI publishes via npm OIDC trusted publishing once the package name exists on npm.
+- Install on a new machine: `opencode plugin add @mokhtarabadi/opencode-smart-compact` (LLM.txt §7.7). npm proxy caveat: ~/.npmrc proxy lines were commented out (dead 127.0.0.1:7890; direct registry works).
+- Rollback: `opencode plugin remove @mokhtarabadi/opencode-smart-compact`; native compaction continues.
+- Docs: docs/compaction.md is the full guide; fragment 22 (<compaction_protocol>) and agents/cognitive-executor.md carry the contract.
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index ec7cbbb..6a2f63b 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -18,6 +18,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Adopted Magic Compact + compaction contract (Task 287, system prompt 9.50.0):** the platform now runs one OpenCode plugin — `magic-compact@1.2.2` — as the high-fidelity manual context compactor, reversing the 2026-10-01 no-plugins policy by explicit Manager order. Native OpenCode auto-compaction stays enabled as the safety net with `compaction: {auto: true, keep: {tokens: 20000}}` in the global config. A new `<compaction_protocol>` system-prompt fragment (fragment 22, added to `prompts/manifest.txt`; `<system_version>` 9.49.0 → 9.50.0; `system-prompt.md` regenerated, byte-identical re-assemble) defines the two layers and the survival contract (task id + lane, pinned `[fed-context]` citations, persona/mode, staged diff hash, blockers, next action). `agents/cognitive-executor.md` carries the operational steps, including that the agent cannot run the plugin command and instead recommends `/magic-compact` under context pressure and uses `read_omitted_content` after a prune. Documented in `README.md`, `LLM.txt` (§7 JSON gains `plugins` + `compaction`; §7.7 rewritten), and the new `docs/compaction.md`. The machine's stale `~/.npmrc` proxy (`127.0.0.1:7890`, dead — mihomo moved to 8118 behind auth) was commented out so the plugin auto-installs; the global `opencode.json` backup was taken first. New prompt-sync gates cover the fragment and the executor guidance. Upstream note: Magic Compact development is paused in favor of Operator Memory; the pinned release remains fully functional and rollback is one line.
 
+- **Adopted Smart Compact as the platform compaction plugin (Task 288, system prompt 9.51.0):** the V1-era `magic-compact` package fails to load on OpenCode 2 (`PluginModule.LoadError` — it exports the V1 plugin shape), so the platform now uses our own V2-native `@mokhtarabadi/opencode-smart-compact` instead. The plugin is a clean-room rewrite (separate repo, 14 passing tests, `tsc --noEmit` clean, `verify:package` OK): it keeps a per-session compaction state in plugin storage and applies it to model-visible messages via `session.hook("context")`, never mutating the stored transcript, with `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`, and the `read_omitted_content` tool. Updated `<compaction_protocol>` (fragment 22), `agents/cognitive-executor.md`, `README.md`, `LLM.txt` (§7 JSON + §7.7), `docs/compaction.md`, and the `opencode_config` memory; `<system_version>` 9.50.0 → 9.51.0 with a regenerated, byte-identical `system-prompt.md`; prompt-sync tests now pin 9.51.0 and assert the smart-compact contract. Native auto-compaction stays on as the safety net. Global `plugins` points at the plugin (local checkout path until it is published to npm). Targeted gate: **83 passed**, exit 0.
+
 ## [9.49.0] - 2026-10-01
 
 ### Added
diff --git a/LLM.txt b/LLM.txt
index 6fa2200..e3fa2d9 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -284,7 +284,7 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
     }
   },
   "plugins": [
-    "magic-compact"
+    "github:mokhtarabadi/opencode-smart-compact"
   ],
   "compaction": {
     "auto": true,
@@ -295,7 +295,7 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
 }
 ```
 
-The `plugins` entry loads **`magic-compact`** (install it with `opencode plugin add magic-compact@1.2.2` — Step 7.7). The `compaction` block keeps OpenCode's native auto-compaction on as the safety net while retaining a larger recent tail; Magic Compact then provides the manual high-fidelity layer. The terminal client config `~/.config/opencode/cli.json` is V2-native (no project `cli.json`, no `tui.json`):
+The `plugins` entry loads **`smart-compact`** (install it with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` — Step 7.7). The `compaction` block keeps OpenCode's native auto-compaction on as the safety net while retaining a larger recent tail; Smart Compact then provides the manual high-fidelity layer. The terminal client config `~/.config/opencode/cli.json` is V2-native (no project `cli.json`, no `tui.json`):
 
 ```json
 {
@@ -400,15 +400,20 @@ Telemetry-free cache/SSRF defaults (`CACHE_TTL_MS=300000`, `ALLOW_PRIVATE_URLS=f
 
 ## 7.7. Plugins
 
-Install the one platform plugin — **`magic-compact`** (lossless, manual context compaction):
+Install the one platform plugin — **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`, lossless V2-native context compaction, maintained in its own repo):
 
 ```bash
-opencode plugin add magic-compact@1.2.2
+# Interim (works now, installs from the pushed repo):
+opencode plugin add github:mokhtarabadi/opencode-smart-compact
+# Once published to npm:
+opencode plugin add @mokhtarabadi/opencode-smart-compact
 ```
 
-This installs the package from npm and writes `plugins: ["magic-compact"]` into `~/.config/opencode/opencode.json` (OpenCode auto-installs/loads it at startup). It needs npm registry access: if the machine's `~/.npmrc` points at a dead proxy, remove the `proxy`/`https-proxy` lines first — direct registry access works and the plugin otherwise fails with `NPMInstallFailedError`.
+This writes the spec into `plugins` in `~/.config/opencode/opencode.json`; OpenCode loads it at startup. `opencode plugin add` accepts npm registry packages or Git specs only — a bare local directory path is rejected, so use the Git spec (or list the directory in `plugins` and restart) while developing. It needs registry access: if the machine's `~/.npmrc` points at a dead proxy, remove the `proxy`/`https-proxy` lines first — direct registry access works and the install otherwise fails with `NPMInstallFailedError`.
 
-Native OpenCode compaction stays enabled as the automatic safety net (the `compaction` block in Step 7). Goal tracking still comes from OpenChamber's built-in **Session Goals**. Upstream note: Magic Compact development is paused in favor of [Operator Memory](https://github.com/aerovato/operator-memory); the pinned `1.2.2` release remains fully functional. Full guide: [`docs/compaction.md`](docs/compaction.md).
+The V1-era `magic-compact` package does not load on OpenCode V2 (it exports the V1 plugin shape); `smart-compact` is the V2-native replacement, so do not add `magic-compact` to `plugins`.
+
+Native OpenCode compaction stays enabled as the automatic safety net (the `compaction` block in Step 7). Goal tracking still comes from OpenChamber's built-in **Session Goals**. Full guide: [`docs/compaction.md`](docs/compaction.md).
 
 ---
 
diff --git a/README.md b/README.md
index 395ca11..16d8f9f 100644
--- a/README.md
+++ b/README.md
@@ -481,7 +481,7 @@ opencode --agent cognitive-executor
 
 ### OpenCode Plugins
 
-One plugin: **`magic-compact`** — lossless, manual context compaction. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Magic Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`. Install with `opencode plugin add magic-compact@1.2.2`; full guide in [`docs/compaction.md`](docs/compaction.md). Goal tracking still comes from OpenChamber's built-in Session Goals. Upstream note: Magic Compact development is paused in favor of Operator Memory; the pinned `1.2.2` release remains fully functional.
+One plugin: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) — lossless, V2-native context compaction, maintained in its own repo. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Smart Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. It never mutates the stored transcript — it stores a per-session compaction state and applies it to the model-visible messages per request. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`. Install with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` (the Git spec, until it is published to npm); full guide in [`docs/compaction.md`](docs/compaction.md). Goal tracking still comes from OpenChamber's built-in Session Goals.
 
 ---
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 7e2fe7b..051c9c3 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -97,7 +97,7 @@ To prevent hallucinations and respect hidden project constraints, you MUST integ
 Context is finite. Two layers keep long sessions productive, and the agent's durable state lives in the task file and project memory, never only in the chat.
 
 1. **Native safety net.** OpenCode auto-compacts near the model limit: it replaces older turns with one lossy summary and keeps the most recent ~20k tokens (config: `compaction.keep.tokens`). Never depend on it to preserve working state — write the essentials to the task file as you go.
-2. **Magic Compact (manual, high-fidelity).** The `magic-compact` plugin is installed globally and loaded by OpenCode. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N assistant turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. After a prune, retrieve any omitted tool content with the `read_omitted_content` tool using its Content ID instead of re-running the source tool.
+2. **Smart Compact (manual, high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) is installed globally and loaded by OpenCode. It is V2-native: it stores a per-session compaction state and applies it to the model-visible messages per request, so it never mutates the stored transcript. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. After a prune, retrieve any omitted tool content with the `read_omitted_content` tool using its Content ID instead of re-running the source tool.
 3. **Survival contract.** Keep the task file holding: the active task id and Kanban lane, the pinned `[fed-context]` block with citations, the current persona/seat, the locked mode (manual or autopilot), the latest staged diff hash, open blockers, and the next action. Resume from that file after any compaction — never from a summary.
 4. **The agent cannot run the plugin command.** When context pressure is high, state one line recommending a `/magic-compact` run to the Manager, then continue from the task file.
 
diff --git a/docs/compaction.md b/docs/compaction.md
index a3e56e0..f13167f 100644
--- a/docs/compaction.md
+++ b/docs/compaction.md
@@ -1,6 +1,6 @@
 # Context Compaction
 
-The platform keeps long sessions productive with two layers: OpenCode's native auto-compaction as the safety net, and the `magic-compact` plugin as the high-fidelity manual layer. Durable working state lives in the task file and project memory, so any compaction stays recoverable.
+The platform keeps long sessions productive with two layers: OpenCode's native auto-compaction as the safety net, and our own **Smart Compact** plugin as the high-fidelity manual layer. Durable working state lives in the task file and project memory, so any compaction stays recoverable.
 
 ## Layer 1 — Native OpenCode compaction (automatic)
 
@@ -17,41 +17,59 @@ Configured in the global `~/.config/opencode/opencode.json`:
 
 `compaction.keep.tokens` is the size of the recent tail kept verbatim. Raise it when exact recent detail matters; lower it when context room matters more.
 
-## Layer 2 — Magic Compact (manual, high fidelity)
+## Layer 2 — Smart Compact (manual, high fidelity)
 
-[`aerovato/magic-compact`](https://github.com/aerovato/magic-compact) preserves the conversation skeleton: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a cache that the agent can read back. Compaction happens once, on command, so it does not churn the prompt cache during the agent loop.
+`@mokhtarabadi/opencode-smart-compact` — maintained in its own repo `mokhtarabadi/opencode-smart-compact` — preserves the conversation skeleton: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a cache the agent can read back. It is a clean-room, **V2-native** rewrite of the idea behind the V1 `magic-compact`: the V1 plugin mutated the stored transcript, which OpenCode V2 no longer exposes, so Smart Compact keeps a per-session compaction state in plugin storage and applies it to the model-visible messages on every request through `session.hook("context")`. The transcript is never modified, so a bad run cannot corrupt history.
 
-### Install (already done on this machine)
+### Install
 
 ```bash
-opencode plugin add magic-compact@1.2.2
+# Interim (works now, installs from the pushed repo):
+opencode plugin add github:mokhtarabadi/opencode-smart-compact
+# Once published to npm:
+opencode plugin add @mokhtarabadi/opencode-smart-compact
 ```
 
-This installs the package from npm and writes `plugins: ["magic-compact"]` into the global config; OpenCode installs and loads it at startup. New machines get the entry from the global `opencode.json` in `LLM.txt` §7 plus the install command in `LLM.txt` §7.7.
+Note: `opencode plugin add` accepts npm registry packages or Git specs only — a bare local directory path is rejected, so use the Git spec (or list the directory in `plugins` and restart) while developing.
 
+This writes the package (or path) into `plugins` in the global config; OpenCode loads it at startup. New machines get the entry from the global `opencode.json` in `LLM.txt` §7 plus the install command in `LLM.txt` §7.7.
+
+> **Do not install `magic-compact`.** The V1-era npm package exports the V1 plugin shape and fails to load on OpenCode 2 with `PluginModule.LoadError`. Smart Compact is the V2-native replacement.
+>
 > **npm proxy caveat:** if `~/.npmrc` points at a dead proxy, the install fails with `NPMInstallFailedError`. Remove the `proxy`/`https-proxy` lines so the registry is reached directly. On this machine the stale `127.0.0.1:7890` proxy was commented out.
 
 ### Commands (Manager-run)
 
-| Command            | Effect                                                              |
-| ------------------ | ------------------------------------------------------------------ |
-| `/magic-compact`   | Summarize all old assistant turns                                   |
-| `/magic-compact 3` | Keep the 3 most recent assistant turns, summarize the rest          |
-| `/magic-trim`      | Prune tool I/O only, without summarizing (OpenCode-only, no LLM call) |
-| `/magic-stats`     | Cumulative token/money savings for the session                      |
+| Command            | Effect                                                         |
+| ------------------ | -------------------------------------------------------------- |
+| `/magic-compact`   | Summarize all old assistant turns; prune bulky tool output     |
+| `/magic-compact 3` | Keep the 3 most recent turns, summarize the rest               |
+| `/magic-trim`      | Prune tool I/O only, without summarizing (no LLM call)         |
+| `/magic-stats`     | Report cumulative savings for the session as a visible message |
+
+Compaction is scheduled by the command and applied on the next model request; summaries are generated at command time with the session's own model.
+
+### Pruning rules
+
+- Completed tool results over the configured limit (default 1024 chars / 128 words) are pruned to a notice; the original is cached.
+- `read` output is always pruned (reloadable).
+- `task` output uses a higher bar (default 4096 chars / 512 words).
+- `question` output is never pruned (it captures an explicit user decision).
+- `todowrite` and `skill` output is replaced with a short notice and not cached (redundant or reloadable).
+- Pending and errored calls are never pruned.
+
+### Automatic strategies
 
-A backup session is created before each run, so a failed compaction returns to the backup.
+- **Deduplication** — identical tool calls (same tool, same normalized arguments) keep only their most recent output; earlier ones are replaced with a notice.
+- **Purge errors** — the arguments of errored tool calls are blanked after a configurable number of turns; error text is preserved.
 
-### Pruning rules (summary)
+### Configuration
 
-- Kept: user messages verbatim, per-turn summaries, tool-call structure, key synthetic messages.
-- Removed/condensed: assistant reasoning and text (replaced by the per-turn summary), most synthetic injected messages, bulky completed tool I/O.
-- Tool I/O omitted above ~128 words / 1024 chars; `read` output always omitted (reloadable), `write`/`edit` large content omitted, `bash` commands over 1024 chars truncated.
-- Pending, running, and errored tool calls are always preserved.
+JSONC, project over global: `.opencode/smart-compact.jsonc` over `~/.config/opencode/smart-compact.jsonc` over built-in defaults. Only override what you need (`enabled`, `pruning.*`, `strategies.*`).
 
 ### Retrieving pruned content
 
-Each omission notice carries a Content ID (e.g. `omitted-001`). The agent calls the `read_omitted_content` tool with that ID to fetch the original instead of re-running the source tool.
+Each omission notice carries a Content ID (e.g. `omitted-0001`). The agent calls `read_omitted_content` with that ID to fetch the original — the lookup is scoped to the calling session — instead of re-running the source tool.
 
 ## Integration in this platform
 
@@ -67,6 +85,6 @@ Each omission notice carries a Content ID (e.g. `omitted-001`). The agent calls
 - the latest staged diff hash;
 - open blockers and the next action.
 
-## Upstream status and rollback
+## Rollback
 
-Magic Compact development is **paused** in favor of [Operator Memory](https://github.com/aerovato/operator-memory), its successor; the pinned `1.2.2` release remains fully functional and is what this platform installs. Rollback is one line: `opencode plugin remove magic-compact` (and drop the `plugins` key). Native auto-compaction continues to work on its own if the plugin is removed.
+Smart Compact is our own plugin. Rollback is one line: `opencode plugin remove @mokhtarabadi/opencode-smart-compact` (and drop the `plugins` key). Native auto-compaction continues to work on its own if the plugin is removed.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 59be6b2..1580bca 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.50.0</system_version>
+<system_version>9.51.0</system_version>
diff --git a/prompts/fragments/22-compaction_protocol.md b/prompts/fragments/22-compaction_protocol.md
index ebfa60d..a682e9c 100644
--- a/prompts/fragments/22-compaction_protocol.md
+++ b/prompts/fragments/22-compaction_protocol.md
@@ -3,7 +3,7 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 
 **Layer 1 — Native safety net (automatic).** OpenCode auto-compacts when a session nears the model limit: it replaces older turns with one summary and keeps the most recent ~20k tokens. It is lossy, so never rely on it to preserve working state. Capture the essentials below before it fires.
 
-**Layer 2 — Magic Compact (manual, high-fidelity).** The `magic-compact` plugin preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is installed globally and loaded by OpenCode. Commands (Manager-run): `/magic-compact [N]` summarizes old turns while keeping the last N assistant turns; `/magic-trim [N]` prunes tool I/O only, without summarizing; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.
+**Layer 2 — Smart Compact (manual, high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is V2-native: it keeps a per-session compaction state in plugin storage and applies it to the model-visible messages on every request, never mutating the stored transcript, so a bad run cannot corrupt history. It is installed globally and loaded by OpenCode. Commands (Manager-run): `/magic-compact [N]` summarizes old turns while keeping the last N turns; `/magic-trim [N]` prunes tool I/O only, without summarizing; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.
 
 **What must survive any compaction — keep it in the task file, not only the chat:**
 - the active task id and its Kanban lane;
diff --git a/system-prompt.md b/system-prompt.md
index a3d7064..cd3759c 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.50.0</system_version>
+<system_version>9.51.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -722,7 +722,7 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 
 **Layer 1 — Native safety net (automatic).** OpenCode auto-compacts when a session nears the model limit: it replaces older turns with one summary and keeps the most recent ~20k tokens. It is lossy, so never rely on it to preserve working state. Capture the essentials below before it fires.
 
-**Layer 2 — Magic Compact (manual, high-fidelity).** The `magic-compact` plugin preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is installed globally and loaded by OpenCode. Commands (Manager-run): `/magic-compact [N]` summarizes old turns while keeping the last N assistant turns; `/magic-trim [N]` prunes tool I/O only, without summarizing; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.
+**Layer 2 — Smart Compact (manual, high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is V2-native: it keeps a per-session compaction state in plugin storage and applies it to the model-visible messages on every request, never mutating the stored transcript, so a bad run cannot corrupt history. It is installed globally and loaded by OpenCode. Commands (Manager-run): `/magic-compact [N]` summarizes old turns while keeping the last N turns; `/magic-trim [N]` prunes tool I/O only, without summarizing; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID, retrieve the original with the `read_omitted_content` tool instead of re-running the source tool.
 
 **What must survive any compaction — keep it in the task file, not only the chat:**
 - the active task id and its Kanban lane;
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 2b58964..65712cb 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -43,13 +43,13 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.50.0"
+    assert shipped == "9.51.0"
 
 
 def test_compaction_protocol_in_shipped_prompt():
     text = _read(SHIPPED)
     assert "<compaction_protocol>" in text
-    assert "magic-compact" in text
+    assert "smart-compact" in text
     assert "read_omitted_content" in text
     assert "What must survive any compaction" in text
 
@@ -57,7 +57,7 @@ def test_compaction_protocol_in_shipped_prompt():
 def test_executor_carries_compaction_guidance():
     text = _read(EXECUTOR)
     assert "compaction" in text.lower()
-    assert "magic-compact" in text
+    assert "smart-compact" in text
 
 
 def test_no_manager_language_rule_in_shipped_prompt():
```
<!-- END_GIT_DIFF -->
