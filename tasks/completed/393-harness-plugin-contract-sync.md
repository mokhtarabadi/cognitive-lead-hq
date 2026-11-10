# Task 393: Harness plugin contract sync (smart-compact 0.3.0 awareness)

**File:** `tasks/qa/393-harness-plugin-contract-sync.md`
**Source:** manager
**Type:** docs
**Status:** in-progress
**Submitted:** 2026-11-10T11:25:20Z
**Estimate:** 2h
**Milestone:** M01

## Goal

Bring the HQ harness in line with what the smart-compact plugin now actually does — a hard `awareness.contextWindowTokens` cap on the pressure denominator, absolute `warnAtTokens` / `emergencyAtTokens` thresholds, one log line per fired reminder and per queued trim, and a `compact_stats` line that reports the effective window and whether config capped it — and fix every live document that still tells the ratio-only story. Pin an HQ working budget in `.opencode/smart-compact.jsonc` so a 1M-token model is measured against the fill where this harness's work actually degrades, not against the ceiling.

## Manager's Notes

Scope is documentation and plugin config only. The plugin repositories (`../opencode-smart-compact`, `../opencode-goal-plugin`) are read-only for this task; MCP server code, agent logic outside the compaction section, and `tasks/archive/` plus `docs/history/` are untouchable. The global `~/.config/opencode/smart-compact.jsonc` is out of scope — the project file carries the override.

## Local TODOs

- [x] Read `AGENTS.md`, `README.md`, the agent compaction section, `docs/compaction.md`, `docs/README.md`, `.opencode/smart-compact.jsonc`
- [x] Grep the repo (excluding build artifacts) for `smart-compact`, `compact_context`, `autoTrimRatio`, `awareness`, `goal plugin`, `opencode-todolist`, `STOP_GOAL`
- [x] Rewrite the executor compaction items 2 and 4 for the cap, the absolute thresholds, the fire logging, and the "warn or dead context → call `compact_context` yourself" rule
- [x] Add Layer 3 to `docs/compaction.md` and correct its ratio-only configuration prose, sample block, and rules
- [x] Pin the working budget in `.opencode/smart-compact.jsonc` with the reason stated in-file
- [x] Sync the plugin lanes in `README.md` and `LLM.txt` §7.7 (installer snippet + the window-is-not-a-budget note)
- [x] Fix the two stale live claims found by the audit (skill-discard rule, retired `<compaction_protocol>` fragment)
- [x] Refresh the `opencode_config/plugin_policy_magic_compact_*` memory shard through `store_memory`
- [x] Verify with greps and the repo linters; record the `git diff --stat`

## Acceptance Criteria

- [x] `agents/cognitive-executor.md` compaction section states the cap (`min(registry, configured)`), both absolute thresholds with `0` = disabled, the per-fire log line, the `compact_stats` window/cap field, and the practical trigger rule; the rest of the prompt is untouched
- [x] `docs/compaction.md` describes three layers, explains why a 1M window needs a 200k working budget, and no longer presents ratio-only awareness as the mechanism
- [x] `.opencode/smart-compact.jsonc` pins `contextWindowTokens: 200000`, `warnAtTokens: 120000`, `emergencyAtTokens: 160000` with an inline WHY and the 0.3.0 version requirement
- [x] No live document still claims the plugin discards `skill` output, that the `<compaction_protocol>` fragment carries compaction rules, or that `autoTrimRatio` at `0.55` is the only pressure action
- [x] Memory policy shard carries the 0.3.0 semantics and marks the ratio-only threshold reading as superseded
- [x] `lint_task_file` and `lint_markdown` pass on every touched file; the prompt-sync suite stays green
- [x] No plugin feature is documented that the plugin patch does not implement

## Verification Evidence

- **Test command:** `grep -rn "shipped default arms it at" --include=*.md --include=*.txt --include=*.jsonc . | grep -v -E "^\./(tasks|context-reports)/|docs/history/"` — Expected: no match. Actual: no output, exit 1 (no stale "armed at 0.55" claim outside history).
- **Test command:** `grep -rn "two layers" --include=*.md agents docs README.md LLM.txt | grep -v docs/history` — Expected: no match. Actual: no output, exit 1.
- **Test command:** `grep -rn "todowrite\` and \`skill\`\|Skill contents omitted" --include=*.md agents docs README.md LLM.txt | grep -v -E "docs/history|CHANGELOG"` — Expected: no match. Actual: no output, exit 1 (the `skill` discard claim is gone).
- **Test command:** `grep -rn "compaction_protocol" --include=*.md agents docs README.md LLM.txt | grep -v -E "docs/history|prompts/archive"` — Expected: no match. Actual: no output, exit 1 (no live doc points at the retired fragment).
- **Test command:** `grep -rn "warnAtTokens" .opencode/smart-compact.jsonc docs/compaction.md agents/cognitive-executor.md README.md LLM.txt | wc -l` — Expected: > 0. Actual: 11 hits across the five files.
- **Test command:** `npx --no-install prettier --check /tmp/opencode/fmt/*.md` on the `HEAD` copies of the three Markdown files — Expected: shows whether formatting was already dirty. Actual: all three warn on `HEAD` too, exit 1, so no formatting regression was introduced and no reformat was applied.
- **Test command:** `uv run --no-project --with pytest pytest tests/test_prompt_sync.py -q` — Expected: the shipped-prompt content gates stay green. Actual: `42 passed in 0.31s`, exit 0 (the executor is parsed by `test_executor_carries_compaction_guidance`, which still finds `compaction` and `smart-compact`).
- **Test command:** `lint_task_file tasks/backlog/393-harness-plugin-contract-sync.md` — Expected: pass. Actual: `✅ tasks/backlog/393-harness-plugin-contract-sync.md passed Task File linting.`
- **Test command:** `lint_markdown` on `docs/compaction.md`, `agents/cognitive-executor.md`, `README.md`, `CHANGELOG.md` — Expected: pass. Actual: `✅` on all four.
- **Test command:** `lint_system_prompt_sync` — Expected: in sync (no fragment touched). Actual: `system-prompt.md is in sync`, with a pre-existing warning about an unactionable skill reference at `prompts/fragments/DECISIONS.md:73` that predates this task.
- **Test command:** `git --no-pager diff --cached --stat` — Expected: the harness files only (the `git diff --stat` equivalent once `qa_transition` staged the work). Actual: 9 files, 409 insertions, 36 deletions — 8 harness files plus this task file, and nothing outside this repository's docs, plugin config, and memory shard.
- **Test command:** `cd mcp-brain-bridge && python3 -c "import capability"` manifest assertion over the twelve plugin/native tool names — Expected: every name resolves `AVAILABLE`. Actual: `checked: 12 | non-AVAILABLE: {} | RESULT: OK`, exit 0. The bridge ships no test harness, so this import-level assertion is the verification; it would have printed `UNAVAILABLE_OPTIONAL` for all nine names before the fix.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0 (or a docs-only skip recorded with root plus marker scan plus matched skills plus reason)
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by that evidence.

## Risk & Rollback

- **Risk:** the three new `awareness` keys are ignored with an `Unknown config key` warning until plugin 0.3.0 loads, so on an older build the HQ project file pins a cap that does nothing and the reminder keeps firing on ratios. Detectable in `opencode.log`; it is a warning, not a failure.
- **Risk:** a 200k cap makes the advisory fire far earlier than before. That is intended, but a session that historically stayed quiet will now see reminders around 120k, and an operator may mistake them for a regression.
- **Rollback plan:** delete the `awareness` block from `.opencode/smart-compact.jsonc` to fall back to global defaults, and revert the four documents plus the memory shard. No plugin or MCP behaviour changes, so rollback is documentation-only.

## Execution Log & Reasoning

**Assumption A1:** the "plugin patch" described in the brief is the in-flight smart-compact 0.3.0 change; the plugin checkout at audit time (`../opencode-smart-compact`, HEAD `2804aa30`, version 0.2.2, clean worktree, no ref carrying the new keys) does not contain it yet. Reason: `git grep warnAtTokens` across all refs returned nothing, and `src/awareness.ts` still resolves the window as registry-first-with-config-fallback. The documented semantics therefore come from the change brief, and anything I could not confirm in source is listed as unverified below rather than asserted.

**Verified in plugin source (pre-patch, 0.2.2):** the ratio path (`getAwarenessLevel`, `shouldAutoTrim`, `autoTrimResetLine`), the shipped defaults (`warnRatio 0.5`, `emergencyRatio 0.8`, `autoTrimRatio 0.55`, `contextWindowTokens 0`), the auto-trim console line (`[smart-compact] N% of the window is in use; tool output will be trimmed on the next request.`), and `formatStats` already reporting `window <n> (<model> — configured)`. That last fact is why the doc says the stats line reports the effective window and whether config capped it, rather than calling the cap marker new.

**Not verifiable at audit time:** whether the absolute thresholds and the ratio pair are OR-ed or one replaces the other, and the exact wording of the new reminder log line. The documents avoid both claims: they say the absolute pair decides when the reminder fires in practice and that the ratio pair stays the window-relative path, without asserting precedence.

**Findings fixed (stale plugin claims):**

- `agents/cognitive-executor.md:108` — presented `awareness.autoTrimRatio` at the shipped `0.55` as the whole automatic story. Rewritten for the cap, the two absolute thresholds, the per-fire logging, and the stats window/cap field.
- `agents/cognitive-executor.md:105` — "Two layers" now names that the plugin's own awareness rides on the second, matching the guide's three-layer framing.
- `agents/cognitive-executor.md:112` — the trigger item now carries the practical rule (plugin warned, or a closed task's dead context) next to the existing pressure triggers.
- `docs/compaction.md:69-70` — the old ratio-only table gave `warnRatio` as the whole advisory trigger. Replaced by Layer 3, which is token-threshold based and explains the working budget.
- `docs/compaction.md:111` — claimed the ratio lowering existed because `0.7` warns at ~734K. Replaced with the absolute-threshold reality.
- `docs/compaction.md:120` — sample config now carries `warnAtTokens` / `emergencyAtTokens` at `0` (disabled globally, pinned per project).
- `docs/compaction.md:127-128` — `contextWindowTokens` described as a fallback only. Now stated as a hard cap, plus a rule for where to set the absolute pair.
- `docs/compaction.md:153` — claimed the `<compaction_protocol>` fragment states the layers. False: the fragment is retired to `prompts/archive/` and never assembled, and the prompt is plugin-blind. Rewritten.
- `docs/compaction.md:88` — claimed `skill` output is discarded with `todowrite`. False since plugin 0.2.2 removed `skill` from `discardTools` and added it to `protectedTools` (task 392); a discarded body reads as a broken `Load Skill`.
- `README.md:474` — plugin lane named only `autoTrimRatio`. Now names the cap, the absolute pair, the HQ budget, and the log line.
- `LLM.txt:502-503` — installer snippet carried `emergencyBudgetTokens: 50000` (a pinned absolute) and no cap/threshold keys, contradicting `docs/compaction.md`'s derive story. Aligned to `emergencyBudgetTokens: 0` + `emergencyBudgetRatio: 0.6` plus the three awareness keys and a note on 0.3.0.

**Memory:** `opencode_config/plugin_policy_magic_compact_2026_10_02` refreshed through `store_memory` (the sanctioned path, not a hand edit) with the 0.3.0 semantics and an explicit "supersedes the ratio-only reading" marker. The index row changed with it.

**Deliberately left alone:** `prompts/archive/22-compaction_protocol.md` and `docs/history/*` are provenance; `tasks/archive/*` is history; the dated snapshot shard `smart_compact_verified_2026_10_13.md` is a point-in-time verification record; the goal-plugin and todolist claims were checked against source (`idleParked`, per-session state plus `.evidence.json` sidecar, `STOP_GOAL` at the projectDir path) and none had drifted; the rate-limit plugin is archived and referenced by no config; no MCP server or Brain-bridge code depends on plugin internals — `compact_stats` is documented as read-only and the bridge never calls plugin tools.

**Lint:** no `package.json` exists, so the repo's own lint is the MCP linters (`lint_task_file`, `lint_markdown`, `lint_system_prompt_sync`) plus `tests/`. Prettier is available but `HEAD` copies of all three Markdown files already fail `--check`, so no reformat was applied (a reformat would bury this change in unrelated whitespace).

**Found while auditing the bridge, fixed in this task:** `mcp-brain-bridge/capability.py` `AVAILABLE_EXACT` listed `todowrite` but not `todoread`, and none of the plugin tools the executor's own protocol names — `compact_context`, `compact_stats`, `read_omitted_content`, `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`. `build_manifest` therefore reported a tool the agent is told to call as `UNAVAILABLE_OPTIONAL`, which is the quietest possible instruction to skip it; it may well have contributed to this session never calling `compact_context`. The nine names were added, the module docstring now records the date and the failure mode, and verification was an import-level assertion because the bridge ships no test harness: `python3 -c "import capability; [assert _is_available(n)]"` over all nine returns no unavailable names and `build_manifest(referenced=..., required=...)` maps them all to `AVAILABLE`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/index.md b/.opencode/memory/index.md
index 5662d6d..a9b6d48 100644
--- a/.opencode/memory/index.md
+++ b/.opencode/memory/index.md
@@ -11,7 +11,7 @@
 | opencode_config | brain-model-routing-2026-10-24 | # Brain on zen-proxy with one model (Manager order 2026-10-24) |  |
 | opencode_config | global-skills-copy-excludes-docs | # Global skills copy must exclude DECISIONS.md and README.md | skills, opencode |
 | opencode_config | opencode_openchamber_versions_2026_11_02 | # OpenCode / OpenChamber versions — verified 2026-11-02 |  |
-| opencode_config | plugin_policy_magic_compact_2026_10_02 | # OpenCode plugin policy — Smart Compact (updated 2026-10-24) |  |
+| opencode_config | plugin_policy_magic_compact_2026_10_02 | # OpenCode plugin policy — Smart Compact (updated 2026-11-10) |  |
 | opencode_config | skill-sources-multiple-roots | # Skills load from several roots, not just ~/.config/opencode/skills | skills, opencode, openchamber |
 | opencode_config | smart_compact_verified_2026_10_13 | # Smart Compact v0.2.1 verified live (2026-10-13, post-restart smoke test) |  |
 | opencode_config | v2_server_password_sync_2026_09_26 | # V2 server auth — managed mode only (updated 2026-10-01) |  |
diff --git a/.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md b/.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md
index abbf2d0..686913a 100644
--- a/.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md
+++ b/.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md
@@ -1,21 +1,22 @@
 ---
-created_at: '2026-10-24T16:29:23.842054+00:00'
+created_at: '2026-11-10T11:21:24.259383+00:00'
 status: active
 tags: []
-updated_at: '2026-10-24T16:29:23.842072+00:00'
+updated_at: '2026-11-10T11:21:24.259409+00:00'
 ---
 
-# OpenCode plugin policy — Smart Compact (updated 2026-10-24)
+# OpenCode plugin policy — Smart Compact (updated 2026-11-10)
 
 One plugin is approved and installed: `@mokhtarabadi/opencode-smart-compact` (V2-native context compaction, our own repo `mokhtarabadi/opencode-smart-compact`). It REPLACES the V1 `magic-compact` package, which fails to load on OpenCode 2 (`PluginModule.LoadError`).
 - Global opencode.json: `plugins: ["github:mokhtarabadi/opencode-smart-compact"]` (Git spec, tracks main). Once published to npm, `@mokhtarabadi/opencode-smart-compact` is preferred. `opencode plugin add` rejects bare local paths.
 - 2026-10-13 refresh: upstream HEAD `8dc42f9` = v0.2.1 (closes budget-guard deadlock); global npm cache still held v0.2.0, so `plugin remove` + `plugin add` re-registered the spec and the stale `~/.cache/opencode/npm/git-opencode-smart-compact-*/` dir was deleted to force a fresh git fetch on next session start. `opencode plugin list` / `check` / `update <github-spec>` do NOT see github-spec plugins (registry packages only; `update` errors `Plugin is not configured`) — remove+add is the refresh path. Restart required for new code to load.
-- Project reference: `.opencode/smart-compact.jsonc` (`enabled: true`, validated vs v0.2.1) overrides global defaults per-project; the audit-agents skill ignores it (never flag/patch/delete/gitignore).
+- Project reference: `.opencode/smart-compact.jsonc` overrides global defaults per-project and now carries the HQ working budget (200k cap, warn 120k, emergency 160k — needs plugin 0.3.0+); the audit-agents skill ignores it (never flag/patch/delete/gitignore).
 - Native OpenCode compaction stays on: `compaction: {auto: true, keep: {tokens: 20000}}`.
 - smart-compact is V2-native: per-session state in plugin storage applied to model-visible messages; never mutates the stored transcript.
 - Agent tools are three: `compact_context` (compress now; `keepTurns`, `mode`), `read_omitted_content` (retrieve one cached omission by session-scoped Content ID), and `compact_stats` (read-only, no inputs, returns the same savings line as `/magic-stats` through one shared `formatStats`). Manager commands stay `/magic-compact`, `/magic-trim`, `/magic-stats`.
 - Repo gates: `npm run typecheck`, `npm test`, `npm run verify:package`. CI publishes via npm OIDC trusted publishing once the package name exists on npm.
 - Rollback: `opencode plugin remove github:mokhtarabadi/opencode-smart-compact`; native compaction continues.
-- Docs: `docs/compaction.md` is the full guide. The live contract is `agents/cognitive-executor.md` (`<compaction_protocol>` section); `prompts/archive/22-compaction_protocol.md` is archived and no longer assembled.
-- 2026-10-22: upstream moved to `fa02c759` (v0.2.1). Platform thresholds are now `warnRatio 0.5` / `emergencyRatio 0.8` in the global `smart-compact.jsonc`, plus the incoming `autoTrimRatio 0.5` key that schedules a lossless tool-output trim without an agent call. Refresh path is unchanged: remove + add the github spec, restart.
-- 2026-10-24: `compact_stats` landed upstream in `2e702680` (closure `dd9e98a7`); installed cache dir `1792858905411` serves it. Smoke test on the live session returned `pruned ~130226 tokens across 213 tool results; summarized 0 turns; 13 cached omissions`, matching the plugin storage exactly. Auto-trim keeps doing the work in practice: a session can run to 365 messages with zero summarized turns and still be trimmed losslessly.
\ No newline at end of file
+- Docs: `docs/compaction.md` is the full guide; the live operational contract is the Compaction section of `agents/cognitive-executor.md`. The system prompt is plugin-blind, and `prompts/archive/22-compaction_protocol.md` is archived and never assembled.
+- 2026-10-22: upstream moved to `fa02c759` (v0.2.1). Ratio thresholds in the global `smart-compact.jsonc` moved to `warnRatio 0.5` / `emergencyRatio 0.8`, plus the incoming `autoTrimRatio 0.5` key that schedules a lossless tool-output trim without an agent call. Refresh path is unchanged: remove + add the github spec, restart.
+- 2026-10-24: `compact_stats` landed upstream in `2e702680` (closure `dd9e98a7`); installed cache dir `1792858905411` serves it. Smoke test on the live session returned `pruned ~130226 tokens across 213 tool results; summarized 0 turns; 13 cached omissions`, matching the plugin storage exactly. Auto-trim keeps doing the work in practice: a session can run to 365 messages with zero summarized turns and still be trimmed losslessly.
+- 2026-11-10 (0.3.0 semantics — supersedes the ratio-only reading above): awareness is token-threshold based. `awareness.contextWindowTokens` is a HARD CAP on the denominator (effective window = `min(registry limit, configured)`), not only a fallback for a silent registry. `awareness.warnAtTokens` and `awareness.emergencyAtTokens` are absolute token thresholds and 0 disables either, because a ratio on a 1M window only speaks at 500k/800k. The plugin logs one console line per fired reminder and per queued auto-trim, and `compact_stats` reports the effective window plus whether config capped it. Practical rule: when the plugin warns, or when a closed task's context is dead, call `compact_context` yourself.
\ No newline at end of file
diff --git a/.opencode/smart-compact.jsonc b/.opencode/smart-compact.jsonc
index de86a47..d4ba409 100644
--- a/.opencode/smart-compact.jsonc
+++ b/.opencode/smart-compact.jsonc
@@ -1,8 +1,24 @@
 {
-  // Project settings for @mokhtarabadi/opencode-smart-compact,
-  // validated against v0.2.1 (git main). Project settings override
-  // the global defaults; only override what is needed.
+  // Project settings for @mokhtarabadi/opencode-smart-compact.
+  // Project settings override the global defaults; only override what is needed.
   // NOTE: deliberate agent-managed config — the audit-agents skill
   // must ignore this file (never flag, patch, delete, or gitignore it).
-  "enabled": true
+  "enabled": true,
+
+  // Working budget for HQ sessions. Needs plugin 0.3.0 or newer: older builds
+  // log "Unknown config key: awareness.warnAtTokens" and ignore these keys.
+  // WHY a cap: contextWindowTokens is a hard ceiling on the denominator, so the
+  // plugin measures against min(registry limit, configured). The model window is
+  // 1M tokens, and 50% of that is 500k — a fill this harness never reaches while
+  // the work is still healthy, which makes ratio-only reminders useless. 200k is
+  // roughly one long audit session's working set, so fill is reported against the
+  // budget the work actually needs rather than the ceiling the window allows.
+  // WHY absolute thresholds: warnAtTokens / emergencyAtTokens fire on token
+  // counts, so the reminder arrives at 120k and the hard nudge at 160k no matter
+  // how large the model window is (0 disables either one).
+  "awareness": {
+    "contextWindowTokens": 200000,
+    "warnAtTokens": 120000,
+    "emergencyAtTokens": 160000
+  }
 }
diff --git a/CHANGELOG.md b/CHANGELOG.md
index ea3ffdb..ba56c8e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Changed
 
+- **Harness plugin contract synced to smart-compact 0.3.0 awareness (task 393):** the plugin's pressure model is now token-threshold based, so the harness stopped describing ratio-only compaction. `agents/cognitive-executor.md` documents the hard cap on the denominator (`min(registry limit, configured)`), the absolute `warnAtTokens` / `emergencyAtTokens` pair (`0` disables either), the per-fire log line, the `compact_stats` window/cap field, and the practical rule that a fired warning or a closed task's dead context is the cheapest thing to drop. `docs/compaction.md` gains Layer 3 (awareness and automatic relief) with the working-budget argument — a 1M-token window puts the shipped ratio lines at 500k/800k, so the budget, not the ceiling, keeps the reminder useful — and its sample config and rules now carry the absolute pair. `.opencode/smart-compact.jsonc` pins the HQ budget (200k cap, warn 120k, emergency 160k) with the reason and the 0.3.0 requirement in-file. The audit also fixed two false live claims: `docs/compaction.md` said `skill` output is discarded (untrue since plugin 0.2.2, task 392) and that the retired `<compaction_protocol>` fragment carries the compaction rules (the prompt is plugin-blind). `README.md` and `LLM.txt` §7.7 plugin lanes aligned, and the `opencode_config` memory shard refreshed through `store_memory`.
 - Permanently eliminated manual mode across the entire platform (Task 0386); unified 100% on autonomous `brain_turn` via `mcp-brain-bridge`.
 - Removed all manual courier instructions, dual-mode branching, and fenced prompt templates from system prompt fragments and agent definitions.
 - System prompt 9.77.0 → 9.78.0 via the assembler.
diff --git a/LLM.txt b/LLM.txt
index 56b41eb..ee7f207 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -499,11 +499,13 @@ Then create the recommended smart-compact global config at `~/.config/opencode/s
     "purgeErrors": { "enabled": true, "turns": 4, "protectedTools": ["question"] },
     "stripReasoning": { "enabled": true, "thresholdChars": 500 }
   },
-  "tokens": { "enabled": true, "emergencyBudgetTokens": 50000 },
-  "awareness": { "enabled": true, "warnRatio": 0.5, "emergencyRatio": 0.8, "rearmStep": 0.05, "autoTrimRatio": 0.5 }
+  "tokens": { "enabled": true, "emergencyBudgetTokens": 0, "emergencyBudgetRatio": 0.6 },
+  "awareness": { "enabled": true, "warnRatio": 0.5, "emergencyRatio": 0.8, "rearmStep": 0.05, "autoTrimRatio": 0.55, "contextWindowTokens": 1000000, "warnAtTokens": 0, "emergencyAtTokens": 0 }
 }
 ```
 
+> **The window is a denominator, not a budget.** `awareness.contextWindowTokens` is now a hard cap: the plugin measures against `min(registry limit, configured)`, and `warnAtTokens` / `emergencyAtTokens` decide when the reminder fires (`0` disables either). This global file names the real window and leaves the absolute pair disabled so no machine-wide budget is imposed; a project that wants a tighter working budget pins its own cap and thresholds in `.opencode/smart-compact.jsonc` — this repo uses 200k / 120k / 160k because 50% of a 1M-token window (500k) is a fill a session never reaches while the work is still healthy. Requires smart-compact 0.3.0 or newer; older builds log `Unknown config key` and ignore the pair.
+
 > **Do not add `skill` to `discardTools`.** Older recommended configs put a `"skill": "Skill contents omitted after compaction..."` entry there, which replaced every skill body with that notice — agents then fell back to filesystem search and `Load Skill` looked broken. `skill` must stay in `protectedTools` and out of `discardTools` (fixed in smart-compact 0.2.2).
 
 Enable the todolist sidebar strip via `~/.config/opencode/cli.json`:
diff --git a/README.md b/README.md
index d94b912..fa137ea 100644
--- a/README.md
+++ b/README.md
@@ -471,7 +471,7 @@ opencode --agent cognitive-executor
 
 ### OpenCode Plugins
 
-Three plugins: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) — lossless, V2-native context compaction, maintained in its own repo. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Smart Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. It never mutates the stored transcript — it stores a per-session compaction state and applies it to the model-visible messages per request. At `awareness.autoTrimRatio` it also trims tool output on its own, losslessly, without summarizing a turn. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`; the agent reads the same savings with the read-only `compact_stats` tool instead of asking for the command. Install with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` (the Git spec, until it is published to npm); full guide in [`docs/compaction.md`](docs/compaction.md). Plus **`goal`** (`opencode-goal-plugin`, maintained in its own repo) — tracks one long-running objective per session in `.opencode/goals/<session-id>.json` with evidence in the matching `.evidence.json` sidecar (a legacy `.opencode/goal-state.json` stays a read fallback that migrates on first write, and the legacy `.opencode/goal-evidence.json` is read only until the session owns its own sidecar, and another session in the same project never sees or continues this goal): `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal resume`, `/goal evidence <args>`, `/goal complete` (needs file citations plus tests that really pass — the plugin executes every recorded command and reads its real exit code; a test entry may carry an `env` map to pin the toolchain it needs, and a blocked completion quotes the failing reasons instead of a generic hint), `/goal clear` (Manager lane; agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`, never write the state files directly). Every set starts a fresh empty evidence sidecar, so a new objective never inherits criteria from the goal before it. The agent creates the goal with `goal_set` when an objective is defined, blocks with `goal_block`, records proof with `goal_evidence` before closing, and resumes with `goal_resume` after a block or interruption. Install with `opencode plugin add github:mokhtarabadi/opencode-goal-plugin` (the Git spec, `opencode-goal-plugin` once published to npm). Plus **`todolist`** (`opencode-todolist`) — restores the V1 session todo tools (`todowrite`/`todoread`) removed in V2, with a live TUI sidebar strip. Install with `opencode plugin add opencode-todolist` and enable the strip via `plugins` in `~/.config/opencode/cli.json`.
+Three plugins: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) — lossless, V2-native context compaction, maintained in its own repo. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Smart Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. It never mutates the stored transcript — it stores a per-session compaction state and applies it to the model-visible messages per request. At `awareness.autoTrimRatio` it also trims tool output on its own, losslessly, without summarizing a turn. Pressure is measured against a working budget rather than the model ceiling — `awareness.contextWindowTokens` is a hard cap on the denominator (`min(registry limit, configured)`), and the absolute `awareness.warnAtTokens` / `emergencyAtTokens` pair decides when the reminder actually fires, because a 1M-token window puts the ratio lines at 500k and 800k; this repo pins a 200k budget with warn at 120k and emergency at 160k in `.opencode/smart-compact.jsonc`, and the plugin logs a line whenever it fires. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`; the agent reads the same savings with the read-only `compact_stats` tool instead of asking for the command. Install with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` (the Git spec, until it is published to npm); full guide in [`docs/compaction.md`](docs/compaction.md). Plus **`goal`** (`opencode-goal-plugin`, maintained in its own repo) — tracks one long-running objective per session in `.opencode/goals/<session-id>.json` with evidence in the matching `.evidence.json` sidecar (a legacy `.opencode/goal-state.json` stays a read fallback that migrates on first write, and the legacy `.opencode/goal-evidence.json` is read only until the session owns its own sidecar, and another session in the same project never sees or continues this goal): `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal resume`, `/goal evidence <args>`, `/goal complete` (needs file citations plus tests that really pass — the plugin executes every recorded command and reads its real exit code; a test entry may carry an `env` map to pin the toolchain it needs, and a blocked completion quotes the failing reasons instead of a generic hint), `/goal clear` (Manager lane; agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`, never write the state files directly). Every set starts a fresh empty evidence sidecar, so a new objective never inherits criteria from the goal before it. The agent creates the goal with `goal_set` when an objective is defined, blocks with `goal_block`, records proof with `goal_evidence` before closing, and resumes with `goal_resume` after a block or interruption. Install with `opencode plugin add github:mokhtarabadi/opencode-goal-plugin` (the Git spec, `opencode-goal-plugin` once published to npm). Plus **`todolist`** (`opencode-todolist`) — restores the V1 session todo tools (`todowrite`/`todoread`) removed in V2, with a live TUI sidebar strip. Install with `opencode plugin add opencode-todolist` and enable the strip via `plugins` in `~/.config/opencode/cli.json`.
 
 ---
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index dea9ee0..45ce788 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -102,14 +102,14 @@ To prevent hallucinations and respect hidden project constraints, you MUST integ
 
 ## Compaction & Context Pressure
 
-Context is finite. Two layers keep long sessions productive, and the agent's durable state lives in the task file and project memory, never only in the chat.
+Context is finite. Two layers of tooling keep long sessions productive — the plugin's own awareness rides on the second — and the agent's durable state lives in the task file and project memory, never only in the chat.
 
 1. **Native safety net.** OpenCode auto-compacts near the model limit: it replaces older turns with one lossy summary and keeps the most recent ~20k tokens (config: `compaction.keep.tokens`). Never depend on it to preserve working state — write the essentials to the task file as you go.
-2. **Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) is installed globally and loaded by OpenCode. It is V2-native: it stores a per-session compaction state and applies it to the model-visible messages per request, so it never mutates the stored transcript. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. Above `awareness.autoTrimRatio` it trims tool output by itself between requests — the shipped default arms it at `0.55`, so expect a tool result to read as a notice even when you did not call `compact_context`; that is the plugin working as intended, and the original is one `read_omitted_content` call away. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. `compact_stats` is the agent's read-only copy of that report (no inputs, never writes), which you call when you need to know whether a compaction actually reclaimed anything: `prunedParts` high with `summarizedTurns` 0 means the bulk is tool output, so a trim is the cheaper move. The line now also reports the plugin version, the measurement path behind the numbers (`tokenizer` or `heuristic`) and a count of summary `fallbacks`, so a compaction that degraded to truncated prose is visible instead of looking normal. After a prune, prefer a cheap fresh run of the source tool; call `read_omitted_content` with its Content ID (`omitted-NNNN`) ONLY when the output cannot be reproduced cheaply, never speculatively. On a cache miss, re-run the source tool once.
+2. **Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) is installed globally and loaded by OpenCode. It is V2-native: it stores a per-session compaction state and applies it to the model-visible messages per request, so it never mutates the stored transcript. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. Pressure is measured against a budget, not against the model ceiling: `awareness.contextWindowTokens` is a hard cap on the denominator, so the fill is computed against `min(registry limit, configured)` instead of whichever figure happens to be larger. A 1M-token window makes the shipped ratios useless in practice — `warnRatio` 0.5 would only speak at 500k, long after your work has degraded — so the plugin also fires on absolute thresholds, `awareness.warnAtTokens` and `awareness.emergencyAtTokens` (`0` disables either), and this repo pins a 200k working budget with warn at 120k and emergency at 160k in `.opencode/smart-compact.jsonc`. Below the warn line, `awareness.autoTrimRatio` still trims tool output by itself between requests, so expect a tool result to read as a notice even when you did not call `compact_context`; that is the plugin working as intended, and the original is one `read_omitted_content` call away. The plugin logs one line each time it fires a reminder and each time it queues a trim, so a quiet log means nothing fired — not that the mechanism is broken. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. `compact_stats` is the agent's read-only copy of that report (no inputs, never writes), which you call when you need to know whether a compaction actually reclaimed anything: `prunedParts` high with `summarizedTurns` 0 means the bulk is tool output, so a trim is the cheaper move. The line also reports the plugin version, the effective window and whether your configured cap is what set it, the measurement path behind the numbers (`tokenizer` or `heuristic`) and a count of summary `fallbacks`, so a compaction that degraded to truncated prose is visible instead of looking normal. After a prune, prefer a cheap fresh run of the source tool; call `read_omitted_content` with its Content ID (`omitted-NNNN`) ONLY when the output cannot be reproduced cheaply, never speculatively. On a cache miss, re-run the source tool once.
    Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
 
 3. **Survival contract.** Keep the task file holding: the active task id and Kanban lane, the pinned `[fed-context]` block with citations, the current persona/seat, the locked mode (manual or autopilot), the latest staged diff hash, open blockers, and the next action. Resume from that file after any compaction — never from a summary.
-4. **Trigger it yourself, or hand off the command.** The agent cannot run the `/magic-*` slash commands, but it CAN call the `compact_context` tool directly — prefer that when context pressure is high (pass `keepTurns` to protect recent turns, `mode: "trim"` to prune tool output only), state one line about it, then continue from the task file. Contract: `keepTurns` is a non-negative integer defaulting to 0, `mode` is `compact` or `trim` defaulting to `compact`, neither is required; `read_omitted_content` takes a session-scoped Content ID such as `omitted-0001`; `compact_stats` takes no inputs, only reads state, and returns the same savings line as `/magic-stats`, so call it once when you need to know whether a compaction actually reclaimed anything and never as a poll. Effect is async (stored now, prunes next request) — do not re-call to verify. In autopilot never ask the Manager to run slash commands; call it yourself and chain the next turn. Fall back to recommending a `/magic-compact` run to the Manager only when a tool call is not available in manual mode. Do not edit compaction config files.
+4. **Trigger it yourself, or hand off the command.** The agent cannot run the `/magic-*` slash commands, but it CAN call the `compact_context` tool directly — prefer that when context pressure is high (pass `keepTurns` to protect recent turns, `mode: "trim"` to prune tool output only), state one line about it, then continue from the task file. Two triggers are yours to read without waiting for a number: when the plugin warns, and when a task is closed and its context is dead — a finished task's context is the cheapest thing to drop, so compact at that boundary instead of carrying it into the next one. Contract: `keepTurns` is a non-negative integer defaulting to 0, `mode` is `compact` or `trim` defaulting to `compact`, neither is required; `read_omitted_content` takes a session-scoped Content ID such as `omitted-0001`; `compact_stats` takes no inputs, only reads state, and returns the same savings line as `/magic-stats`, so call it once when you need to know whether a compaction actually reclaimed anything and never as a poll. Effect is async (stored now, prunes next request) — do not re-call to verify. In autopilot never ask the Manager to run slash commands; call it yourself and chain the next turn. Fall back to recommending a `/magic-compact` run to the Manager only when a tool call is not available in manual mode. Do not edit compaction config files.
 5. **Call it before heavy payloads, not after stalling.** Invoke `compact_context` yourself at these triggers: context pressure is high, 50+ steps ran without measurable progress, before a plan-approval handoff, before QA or review turns carry a large diff, plus the task-boundary trigger from the compaction protocol. Use `mode: "trim"` when only tool output is bulky and full `compact` when turns are stale. Never re-run a source tool for pruned output — retrieve it with `read_omitted_content` by Content ID. The Brain never names tools or plugins; it emits only a plan and checklist, and this executor maps them onto `compact_context`.
 
 ### Goal Plugin Boundary - global helper, not truth
diff --git a/docs/compaction.md b/docs/compaction.md
index 7084249..456c6e6 100644
--- a/docs/compaction.md
+++ b/docs/compaction.md
@@ -1,6 +1,6 @@
 # Context Compaction
 
-The platform keeps long sessions productive with two layers: OpenCode's native auto-compaction as the safety net, and our own **Smart Compact** plugin as the high-fidelity manual layer. Durable working state lives in the task file and project memory, so any compaction stays recoverable.
+The platform keeps long sessions productive with three layers: OpenCode's native auto-compaction as the safety net, our own **Smart Compact** plugin as the high-fidelity manual layer, and that same plugin's awareness as the automatic layer that acts without an agent call. Durable working state lives in the task file and project memory, so any compaction stays recoverable.
 
 ## Layer 1 — Native OpenCode compaction (automatic)
 
@@ -60,17 +60,6 @@ This writes the package (or path) into `plugins` in the global config; OpenCode
 
 Compaction is scheduled by the command and applied on the next model request; summaries are generated at command time with the session's own model.
 
-### Automatic at pressure (agent needs no action)
-
-Two things happen without anyone asking:
-
-| Layer | Trigger | Effect | Lossy? |
-| --- | --- | --- | --- |
-| Tool-output trim (`awareness.autoTrimRatio`) | Fill crosses the ratio (platform: `0.5`) | Queues a `trim` for the next request, reusing the manual trim pass. Once per sustained pressure period, not once per request | No — originals stay cached under a Content ID |
-| Advisory reminder (`awareness.warnRatio`) | Fill crosses the ratio (platform: `0.5`, emergency `0.8`) | One system part telling the agent how full the window is and what to call | No |
-
-Summarization is not automatic on purpose: replacing turns with summaries needs the agent's own judgement about which detail still matters. The plugin never overwrites a pending compaction with a weaker trim.
-
 ### Agent-callable tools
 
 The agent compresses the session itself with the `compact_context` tool (never the `/magic-*` slash commands), which runs the same logic as `/magic-compact` (shared `src/actions.ts` in the plugin, so the paths cannot drift). Effect is async (stored now, prunes next request) — do not re-call to verify. In autopilot never ask the Manager to run slash commands:
@@ -96,7 +85,7 @@ The `compact_stats` tool reports what the compaction actually reclaimed: `pruned
 - `read` output is always pruned (reloadable).
 - `task` output uses a higher bar (default 4096 chars / 512 words).
 - `question` output is never pruned (it captures an explicit user decision).
-- `todowrite` and `skill` output is replaced with a short notice and not cached (redundant or reloadable).
+- `todowrite` output is replaced with a short notice and not cached (redundant). `skill` output is neither discarded nor pruned: a truncated skill body looks exactly like a broken `Load Skill`.
 - Pending and errored calls are never pruned.
 
 ### Automatic strategies
@@ -108,7 +97,7 @@ The `compact_stats` tool reports what the compaction actually reclaimed: `pruned
 
 JSONC, project over global: `.opencode/smart-compact.jsonc` over `~/.config/opencode/smart-compact.jsonc` over built-in defaults. On a fresh machine create the global file with this recommended content right after `opencode plugin add` (same snippet lives in `LLM.txt` §7.7, so an installer LLM writes it verbatim):
 
-The platform runs `warnRatio 0.5` / `emergencyRatio 0.8` because a 1M-token window at the shipped `0.7` would only warn at ~734K tokens. `autoTrimRatio 0.5` is the one automatic action and it is lossless: it queues a tool-output-only trim for the next request, summarizes nothing, and leaves every pruned original in the cache. A per-session latch means one sustained pressure period trims once; it re-arms only after the fill grows by `rearmStep` or drops below the line and rises again, so a long session above the threshold does not queue a trim on every request.
+The platform runs `warnRatio 0.5` / `emergencyRatio 0.8` for window-relative firing; on a 1M-token window those lines sit at 500k and 800k, which is why the absolute `warnAtTokens` / `emergencyAtTokens` pair carries the reminder in practice. `autoTrimRatio 0.5` is the one automatic action and it is lossless: it queues a tool-output-only trim for the next request, summarizes nothing, and leaves every pruned original in the cache. A per-session latch means one sustained pressure period trims once; it re-arms only after the fill grows by `rearmStep` or drops below the line and rises again, so a long session above the threshold does not queue a trim on every request.
 
 ```jsonc
 // Recommended global config for smart-compact.
@@ -128,25 +117,41 @@ The platform runs `warnRatio 0.5` / `emergencyRatio 0.8` because a 1M-token wind
     "stripReasoning": { "enabled": true, "thresholdChars": 500 }
   },
   "tokens": { "enabled": true, "emergencyBudgetTokens": 0, "emergencyBudgetRatio": 0.6 },
-  "awareness": { "enabled": true, "warnRatio": 0.5, "emergencyRatio": 0.8, "rearmStep": 0.05, "autoTrimRatio": 0.55, "contextWindowTokens": 1000000 }
+  "awareness": { "enabled": true, "warnRatio": 0.5, "emergencyRatio": 0.8, "rearmStep": 0.05, "autoTrimRatio": 0.55, "contextWindowTokens": 1000000, "warnAtTokens": 0, "emergencyAtTokens": 0 }
 }
 ```
 
-Three rules govern the numbers in that block.
+Four rules govern the numbers in that block.
 
 - **The emergency budget follows the window.** A positive `emergencyBudgetTokens` pins an exact number and behaves exactly as before. `0` means *derive*: the budget becomes `emergencyBudgetRatio` (default `0.6`) of the resolved context window, so a large-window model no longer warns from the first few turns. To switch the warning off, set `emergencyBudgetRatio` to `0` — **not** `emergencyBudgetTokens`, because zero there now means derive. An unknown window keeps the warning silent rather than firing against a guessed denominator.
-- **Awareness needs a denominator.** When the model registry entry carries no `limit.context`, set `awareness.contextWindowTokens` to the window size and the reminder states that the figure is configured rather than measured. With neither a registry limit nor a fallback, the advisory (and the lossless auto-trim that depends on the same ratio) stays inert — which is why the sample above carries an explicit `1000000` rather than the neutral `0`, and why a copied config with `0` here silently reproduces a plugin that never speaks.
+- **Awareness needs a denominator, and that number is a cap.** When the model registry entry carries no `limit.context`, set `awareness.contextWindowTokens` to the window size and the reminder states that the figure is configured rather than measured. With neither a registry limit nor a fallback, the advisory (and the lossless auto-trim that depends on the same ratio) stays inert — which is why the sample above carries an explicit `1000000` rather than the neutral `0`, and why a copied config with `0` here silently reproduces a plugin that never speaks. The same key is a hard ceiling: the plugin takes `min(registry limit, configured)`, so a project can lower the denominator below the model's real window and get a working budget instead of a percentage nobody ever reaches.
+- **Set the absolute pair where work degrades, not where the window ends.** `warnAtTokens` / `emergencyAtTokens` fire on token counts (`0` disables either). The global file leaves them at `0` so no machine-wide budget is imposed; a project that wants one pins it in its own `.opencode/smart-compact.jsonc` — this repo uses 200k / 120k / 160k on a 1M-token model.
 - **Auto-trim is armed by default.** `autoTrimRatio` defaults to `0.55`, so bulky completed tool results become notices without any manual call, one trim per sustained pressure period. Pruning is lossless — the original stays cached — so this is safe to leave on.
 
 ### Retrieving pruned content
 
 Each omission notice carries a Content ID (e.g. `omitted-0001`). Prefer a cheap fresh run of the source tool; the agent calls `read_omitted_content` with that ID ONLY when the output cannot be reproduced cheaply, never speculatively — the lookup is scoped to the calling session, a single response is capped at 20 000 characters (a longer original returns a truncation notice rather than megabytes of text), and an original dropped by the store cap fails closed with a missing-original notice instead of returning stale content. On a cache miss, re-run the source tool once.
 
+## Layer 3 — Awareness and automatic relief (no agent call)
+
+The plugin watches fill by itself and can take two actions. Neither one summarizes a turn, touches a user message, or aborts a step.
+
+Fill is measured against a **working budget**, not against the model ceiling. `awareness.contextWindowTokens` is a hard cap on the denominator — the plugin measures against `min(registry limit, configured)` — so a 1M-token model is still reported against the budget in which the work actually happens. That is the point: a ratio threshold on a 1M window is unreachable in practice. The shipped `warnRatio` 0.5 first speaks at 500k tokens, and a session's useful detail is long gone by then. This repo pins a 200k budget on a 1M window in `.opencode/smart-compact.jsonc` (warn at 120k, emergency at 160k).
+
+| Action | Trigger | Effect | Lossy? |
+| --- | --- | --- | --- |
+| Advisory reminder | Fill crosses `awareness.warnAtTokens` (repo: 120k tokens) or `emergencyAtTokens` (160k); the ratio pair (`warnRatio` / `emergencyRatio`) stays as the window-relative path | One system part telling the agent how full the window is and what to call | No |
+| Tool-output trim (`awareness.autoTrimRatio`) | Fill crosses the ratio (platform: `0.5`) | Queues a `trim` for the next request, reusing the manual trim pass. Once per sustained pressure period, not once per request | No — originals stay cached under a Content ID |
+
+`0` disables either absolute threshold, and an unknown window keeps the reminder silent rather than firing against a guessed denominator. The plugin logs one console line each time it fires a reminder and each time it queues a trim, so a silent log means nothing fired — never assume the mechanism is broken, and check the fill the `compact_stats` line reports.
+
+Summarization is not automatic on purpose: replacing turns with summaries needs the agent's own judgement about which detail still matters. The plugin never overwrites a pending compaction with a weaker trim, and the agent still compacts at the task boundary — see the task-boundary rule above.
+
 Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
 
 ## Integration in this platform
 
-- **System prompt:** the `<compaction_protocol>` fragment (generated into `system-prompt.md`) states the two layers and the survival contract.
+- **System prompt:** none — the prompt is plugin-blind on purpose (the retired `<compaction_protocol>` fragment sits in `prompts/archive/` and is never assembled), so the survival contract below and `agents/cognitive-executor.md` carry the whole rule set.
 - **Agent:** `agents/cognitive-executor.md` carries the operational steps: the agent calls `compact_context` itself under pressure (slash commands are Manager-only) and recommends `/magic-compact` only when a tool call is unavailable in manual mode.
 - **Config:** global `opencode.json` holds `plugins` + `compaction`; the repo `opencode.json` stays config-free of both.
 - **Global plugins:** Global plugins live in user config at tilde config opencode opencode dot json as github mokhtarabadi opencode-smart-compact plus github mokhtarabadi opencode-goal-plugin. Repo opencode dot json has no plugins key by intent. HQ task file stays truth. Use the goal plugin for long objectives (`/goal` set, status, block, complete with evidence, clear); its idle loop never fires past an approval gate.
```
<!-- END_GIT_DIFF -->
