# Task 393: Harness plugin contract sync (smart-compact 0.3.0 awareness)

**File:** `tasks/completed/393-harness-plugin-contract-sync.md`
**Source:** manager
**Type:** docs
**Status:** closed
**Finished:** 2026-11-10T11:53:22Z
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
**Factual Git Diff:** Stored in Commit Hash: `3f248799a3fad5684968beb893abee6da6e9b572`
<!-- END_GIT_DIFF -->
