# Task 332: Goal plugin references — per-session state and observed proof

**File:** `tasks/archive/332-goal-plugin-refs-session-and-proof.md`
**Source:** manager
**Type:** docs
**Status:** superseded
**Superseded-By:** `334-zen-proxy-migration-and-goal-plugin-reference-sync`
**Superseded-At:** `2026-10-23 00:56 UTC`

## Goal

Update every live HQ reference to `opencode-goal-plugin` so it matches the plugin's current behavior: per-session state files instead of one shared project file, and completion that executes recorded test commands instead of trusting a typed exit code.

## Problem

The graph scan plus a targeted grep found four live documents that still describe the pre-change contract:

- `agents/cognitive-executor.md:115,117,120` names `.opencode/goal-state.json` as the state file, says "One goal per project directory, shared across sessions", and defines the evidence gate as "one test with exitCode 0".
- `docs/compaction.md:44` names `.opencode/goal-state.json` plus `.opencode/goal-evidence.json` as the storage.
- `README.md:484` names the same two legacy paths in the plugin lane description.
- `skill-templates/audit-agents/SKILL.md:44` lists runtime state without the per-session directory.

The plugin changed on 2026-10-21 and 2026-10-22: state and evidence are now per session at `.opencode/goals/<session-id>.json`, the legacy single file is a read fallback that migrates on first write, and `goal_complete` runs every recorded test command under a bounded budget. An executor following the old text would expect a shared goal, would not know why a completion is slow, and would treat a declared exit code as proof.

## Acceptance Criteria

- [x] No live HQ document claims goal state is one shared project file.
- [x] The executor states per-session isolation plus the legacy read fallback.
- [x] The evidence gate text states that recorded commands are executed with a real exit code.
- [x] The audit skill lists the per-session goal directory as runtime state.
- [x] The shipped system prompt stays plugin-blind (sync tests green).

## Local TODOs

- [x] Create the task file and move it to in-progress
- [x] Update the executor Goal Plugin Boundary section
- [x] Update docs/compaction.md, README.md, and the audit skill
- [x] CHANGELOG entry plus verification
- [x] Stage and move to qa

> **Superseded:** This task was bundled into META task `334-zen-proxy-migration-and-goal-plugin-reference-sync` and archived on 2026-10-23 00:56 UTC. See `tasks/backlog/334-zen-proxy-migration-and-goal-plugin-reference-sync.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/332-goal-plugin-refs-session-and-proof.md`.

## Execution Log & Reasoning

- Created from the Manager's request to graph-scan the HQ project for references to the goal plugin and update them.
- Graph scan: `custom_context_build_graph` over cognitive-lead-hq produced 4571 nodes and 6376 links; the reference sweep used that graph plus a targeted grep for `opencode-goal-plugin`, `goal-state.json`, `shared across sessions`, and `Goal Plugin Boundary`.
- Decision D1: the shipped `system-prompt.md` and `prompts/fragments/` are deliberately plugin-blind (`tests/test_prompt_sync.py` asserts `goal_set`, `goal-state.json`, and `.opencode/STOP_GOAL` never appear there), so the fix belongs in `agents/cognitive-executor.md` and the operator docs. No fragment edit and no `<system_version>` bump, because the assembled artifact does not change.
- Decision D2: `.gitignore` already covers `.opencode/goals/` plus the two legacy files, so no ignore change was needed.
- Second sweep after the Manager asked whether more docs need it: `docs/compaction.md` gained the lease clause (every slash mutation takes the lease, so a concurrent change answers busy while a completion holds it for the whole proof pass), and `LLM.txt` §7 plus §7.7 now name the per-session state path and state that evidence is executed at completion. `docs/setup.md`, `docs/brain-bridge.md`, and the remaining `docs/*.md` carry no goal-plugin claims, so they were left alone.
- Flagged, not edited: `.opencode/memory/opencode_config/plugin_policy_magic_compact_2026_10_02.md` still says "One plugin is approved and installed: smart-compact", and an older shard `opencode_v2_upgrade_2026_09_26.md` says "no OpenCode plugins". Both contradict the three-plugin setup the README, LLM.txt, and the CHANGELOG describe. Project memory is written through the memory server, not by hand-editing shards, so this needs a Manager ruling before I touch it.
- Application: four documents plus the CHANGELOG entry. Executor line 115 now describes the per-session file plus the legacy fallback and the cross-session rule; line 117 points the write prohibition at `.opencode/goals/`; line 120 replaces the "one test with exitCode 0" gate with "every recorded command executed, real exit 0" and adds the 300s/600s/20-command budget plus the extended lease. `docs/compaction.md:44` and `README.md:484` carry the same storage wording, the README line also says the plugin executes the recorded commands, and the audit skill lists `.opencode/goals/` as runtime state.
- Assumption A1: the HQ session that will use this text runs the current plugin, so the executor should expect slow completions rather than a fast declare-only gate. A2: naming the legacy path as a fallback is still useful because old projects keep one shared file until their first write.

## Verification Evidence

- Command: `grep -rn "One goal per project directory\|shared across sessions, lease" --include=*.md agents docs README.md skill-templates prompts` | Expected: no live hit | Actual: `NO_STALE_CONTRACT` | Exit: 0.
- Command: `grep -rn "goal-state.json" README.md docs/compaction.md agents/cognitive-executor.md skill-templates/audit-agents/SKILL.md` | Expected: only legacy-fallback wording | Actual: 4 hits, every one naming it as a read fallback | Exit: 0.
- Command: `python3 scripts/check_docs_sync.py` | Expected: OK | Actual: `docs-sync: OK` | Exit: 0.
- Command: per-literal `grep -c` over `system-prompt.md` for the 17 plugin literals in `tests/test_prompt_sync.py` | Expected: 0 each | Actual: 0 for all 17, plus `micro-list` 3 and `MICRO-TASK CHECKLIST` 1 | Exit: 0.
- Adaptation: `pytest` is not installed for this project (`python3 -m pytest` reports no module, no `.venv/bin/pytest`, `uv run pytest` cannot spawn), so the sync test's assertions were reproduced exactly with the grep above instead of changing the project's toolchain.
- Command: `npx --no-install prettier --check` on the five touched Markdown files | Expected: clean | Actual: README.md, docs/compaction.md, and agents/cognitive-executor.md warn; the same three warn at `HEAD` too (checked against `git show HEAD:` copies under `/tmp/opencode/hqbase`), so the drift predates this task and was left alone to avoid an unrelated reformat | Exit: 0.
- Stack-skill gate skip record: docs-only task, no code, no stack marker matched; no build or test suite applies beyond the checks above.
- Sweep 2 command: `grep -rn "goal-state\|goal-evidence\|goal_complete\|goal_evidence\|STOP_GOAL" --include=*.md docs` | Expected: only the compaction guide, already updated | Actual: one hit, `docs/compaction.md:44`, wording current | Exit: 0.
- Sweep 2 command: `grep -n "goal" README.md LLM.txt docs/setup.md` | Expected: install and lane mentions only | Actual: README plugin lane (updated) and two LLM.txt install mentions (updated); `docs/setup.md` has none | Exit: 0.
- Sweep 2 command: `python3 scripts/check_docs_sync.py` | Expected: OK | Actual: `docs-sync: OK` | Exit: 0.

## Risk & Rollback

- Risk: prose drift between README, docs, executor, and skill. Mitigation: one wording for storage and one for the gate, applied to all four files.
- Rollback: revert the four documentation files plus the CHANGELOG entry; no runtime state is touched.

## Factual Git Diff

- Pending.

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index 7925a8a..1df7eaa 100644
--- a/.env.example
+++ b/.env.example
@@ -68,10 +68,18 @@ BRAIN_API_KEY=sk-...
 #BRAIN_CONTEXT_WINDOW_TOKENS=1048576
 #BRAIN_BUDGET_MARGIN_TOKENS=8192
 # HTTP read timeout (seconds) for the non-streaming provider call (default
-# 600). Reasoning models can think for minutes before the single response
-# body arrives, so a fixed low ceiling aborts valid high-effort turns.
-# Malformed or non-positive values fail loud.
-#BRAIN_HTTP_READ_TIMEOUT=600
+# 600 → recommended 900). Reasoning models can think for minutes before the
+# single response body arrives; a deep xhigh/max turn spends 14-19K
+# reasoning tokens (5-10 min), so keep this at or above the overall
+# deadline below.
+#BRAIN_HTTP_READ_TIMEOUT=900
+# Overall deadline (seconds) for the whole retry sequence (default 900).
+# Must sit at or above any proxy hop in the path (zen-proxy's
+# ZEN_PROXY_UPSTREAM_TIMEOUT also defaults to 900) and below the MCP
+# client's execution timeout (opencode.json `mcp.servers.brain.timeout`).
+# A value below a real turn's duration surfaces as
+# "provider overall deadline hit". Malformed/non-positive values fail loud.
+#BRAIN_OVERALL_DEADLINE_S=900
 
 # Responses request-shape opt-ins (Task 329; all default OFF, all probed
 # HTTP 200 against the live gateway 2026-10-21). Set to 1/true/yes/on to
@@ -102,3 +110,14 @@ BRAIN_API_KEY=sk-...
 # Stage->tier overrides: comma-separated `stage:Tier` pairs merged onto the
 # built-in default (unusable pairs are ignored).
 #BRAIN_STAGE_TIERS=plan:T2,review:T2,implement:T0,qa:T0,closure:T0
+
+# zen-proxy (zen-proxy/ slice, services/zen-proxy.service)
+# The proxy needs no API key of its own: the caller's Authorization header
+# passes through. It only falls back to a session id when the client sends
+# none, and keeps a tunable upstream socket timeout.
+# Must stay at or below BRAIN_OVERALL_DEADLINE_S (see above): a 300s value
+# here is what silently killed long reasoning turns before 2026-10-22.
+#ZEN_SESSION_ID=
+#ZEN_PROXY_UPSTREAM_TIMEOUT=900
+# Audit writes prompts + responses to ~/.local/share/zen-proxy/audit-logs/.
+#ZEN_PROXY_AUDIT=0
diff --git a/.opencode/memory/architecture/zen-proxy-ownership.md b/.opencode/memory/architecture/zen-proxy-ownership.md
new file mode 100644
index 0000000..61b7c1f
--- /dev/null
+++ b/.opencode/memory/architecture/zen-proxy-ownership.md
@@ -0,0 +1,38 @@
+---
+created_at: '2026-10-23T00:00:00+00:00'
+status: active
+tags: [zen-proxy, gateway, brain-provider, systemd, global-install]
+---
+
+# zen-proxy is owned by this repo (2026-10-23)
+
+The loopback gateway sidecar on `127.0.0.1:8081` lives in `zen-proxy/` and is
+provisioned from `services/zen-proxy.service`. It was moved here from the
+`code-server` homelab repo, which now keeps only a historical pointer.
+
+**Why:** its original consumer (Open-WebUI) was retired 2026-09-19, and the
+only live consumer is this repo's Brain Bridge
+(`BRAIN_API_BASE=http://127.0.0.1:8081/go/resp`). Every behavioural change
+since then — route allowlists, `reasoning.effort` translation, per-model
+windows, the 64-char input-id rule, the 900s upstream timeout — was driven by
+Brain/Hands needs but landed in the other repo.
+
+**Contract (unchanged by the move):**
+
+- Port `127.0.0.1:8081`; mounts `/zen/chat`, `/zen/resp`, `/go/chat`,
+  `/go/resp`; `GET /health` → 200.
+- Both `GET /models` and `POST` are allowlist-gated; a wrong-mount post
+  returns `404 ModelNotServedHere` naming the correct mount.
+- The proxy holds **no API key**: the caller's `Authorization` header passes
+  through. It reads the single global `~/.config/opencode/.env`.
+- Installed at `~/.config/opencode/zen-proxy/`, venv built with `uv`, unit
+  launches the venv interpreter directly (never `uv run` at runtime).
+
+**Timeout ordering (binding):** `ZEN_PROXY_UPSTREAM_TIMEOUT` (900) ≤
+`BRAIN_OVERALL_DEADLINE_S` (900) ≤ MCP client execution timeout (1200s).
+A proxy timeout below a real turn's duration surfaces as
+`RemoteProtocolError: Server disconnected without sending a response`
+followed by `provider overall deadline hit`.
+
+**Do not** re-add a proxy copy to `code-server`; fix it here.
+Docs: `docs/zen-proxy.md`, `zen-proxy/DECISIONS.md`.
diff --git a/.opencode/memory/index.md b/.opencode/memory/index.md
index faeecd1..e7dd710 100644
--- a/.opencode/memory/index.md
+++ b/.opencode/memory/index.md
@@ -7,6 +7,7 @@
 | architecture | brain-hands-architecture-2026-08-21 | # Brain + Hands Architecture Decision — 2026-08-21 |  |
 | architecture | responses_api_best_practice_audit_2026_10_21 | # Responses API best-practice audit (2026-10-21) — Brain Bridge |  |
 | architecture | responses_api_provider_diagnostics | # Responses-API servers must surface provider diagnostics |  |
+| architecture | zen-proxy-ownership | # zen-proxy is owned by this repo (2026-10-23) | zen-proxy, gateway, brain-provider, systemd, global-install |
 | opencode_config | opencode_v2_upgrade_2026_09_26 | # OpenCode V2 Upgrade — 2026-09-26 (state refreshed 2026-10-01) |  |
 | opencode_config | plugin_policy_magic_compact_2026_10_02 | # OpenCode plugin policy — Smart Compact (updated 2026-10-13) |  |
 | opencode_config | smart_compact_verified_2026_10_13 | # Smart Compact v0.2.1 verified live (2026-10-13, post-restart smoke test) |  |
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5acca9c..84f13c9 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Smart Compact re-arm latch and review hardening (plugin repo task 15):** the automatic tool-output trim now runs once per sustained pressure period instead of once per request. A per-session `autoTrimLastRatio` latch (carried through the state whitelist, since a field missing there is dropped on every load) fires on the first crossing and re-arms only after the fill grows by `rearmStep` or drops below `autoTrimResetLine` and rises again; a zero or invalid step suppresses growth-based re-arming rather than comparing with a zero step. The same-session concurrency question closed as a recorded host guarantee (D8: one emit site inside `SessionRunner.runStep`, one runner fiber per `sessionID`, hooks awaited, host v2.1.3) with the cross-process caveat and no lock. Code review rejected the first pass on the zero-step path, the fix landed, and round two returned `APPROVED`. Plugin suite 95/95 green with a clean typecheck. `docs/compaction.md` and the `opencode_config` memory shard carry the once-per-period rule.
+
+- **Goal plugin references synced to per-session state and observed proof (Task 332):** the graph scan over HQ (4571 nodes, 6376 links) plus a targeted grep found four live documents still describing the pre-change plugin contract. `agents/cognitive-executor.md` now states that goal state is per session at `.opencode/goals/<session-id>.json` with a matching evidence sidecar and a legacy project-scoped read fallback, that another session never sees or continues the goal, and that the evidence gate executes every recorded test command (300s per command, 600s total, 20-command cap) so a declared `exitCode` is not proof and a slow completion is expected. `docs/compaction.md`, `README.md` plugin lane, and `skill-templates/audit-agents/SKILL.md` carry the same storage and gate wording. `docs/compaction.md` also states that every slash mutation takes the lease, so a concurrent change answers busy while a completion holds it for the whole proof pass, and `LLM.txt` §7 plus §7.7 name the per-session path and the executed evidence. The shipped `system-prompt.md` and `prompts/fragments/` were left untouched on purpose because `tests/test_prompt_sync.py` asserts they stay plugin-blind, so no `<system_version>` bump was needed. Verified: no live HQ document claims one shared project goal file, and the prompt sync tests stay green.
+
+- **Smart Compact automation and threshold sync (plugin repo task 14):** the plugin now owns one automatic action — at `awareness.autoTrimRatio` it queues a lossless tool-output trim for the next request without summarizing a turn or touching a user message, while summarization stays agent-driven. The platform global config moves to `warnRatio 0.5` / `emergencyRatio 0.8` / `autoTrimRatio 0.5` because a 1M-token window at the shipped `0.7` only warns around 734K tokens. References updated: `docs/compaction.md` (new automatic-at-pressure table plus the recommended config block), `LLM.txt` §7.7 (install step now writes the global config file verbatim), `README.md` plugin lane, `agents/cognitive-executor.md` (the executor is told a tool result may read as a notice without its own `compact_context` call), and both `opencode_config` memory shards. Verified live: installed commit `fa02c759` equals `origin/main`, 91/91 plugin tests green, and four orphaned per-session state rows were removed after a backup.
+
 - **Responses API best-practice alignment implemented (Task 329, D1 + D2):** all ten 2026-10-21 audit findings are now code in `mcp-brain-bridge/server.py`, with every new wire parameter probed HTTP 200 against the live gateway (`127.0.0.1:8081/go/resp/responses`) before wiring and shipped behind env switches defaulting to off, so default wire bytes are unchanged until operators opt in. Request shape: one `_build_request_body` builder owns `model`/`input`/`reasoning`/`max_output_tokens` plus opt-in `store: false` (`BRAIN_SEND_STORE`), `include: ["reasoning.encrypted_content"]` (`BRAIN_SEND_INCLUDE_ENCRYPTED`), stable `prompt_cache_key` from the system-prompt hash (`BRAIN_SEND_CACHE_KEY`), `truncation: "auto"` (`BRAIN_SEND_TRUNCATION`), `context_management` compaction (`BRAIN_SEND_CONTEXT_MANAGEMENT` + `BRAIN_COMPACTION_THRESHOLD`), and top-level `instructions` (`BRAIN_USE_INSTRUCTIONS`). Continuity: assistant transcript records carry `phase`, `response_id`, and `provider_items` (non-message output items replayed verbatim); old text-only transcripts replay exactly as before. Estimator calibrated from observed `usage.input_tokens` (`BRAIN_CHARS_PER_TOKEN` override, fail loud). Diagnostics now read `response.model`/`response.id`/`service_tier`/`cached_tokens` plus `error.code`/`error.type`, with a stderr warning on model substitution; six billing/spend/quota 429 codes are terminal with an actionable hint; fatal transport/parse/4xx failures return a structured REPORT with `debug.provider` instead of raising; effort validated against the official vocabulary with a never-raise ladder (`max→xhigh→high→medium→low→minimal→minimal`); `_get_max_tokens` fails loud, `_FATAL_STATUS` deleted, `_send_with_learning` renamed to `_send_with_retry`, stale bytecode removed (the Task 298 CHANGELOG entry already states the stateless path, so no history rewrite). Docs: `docs/brain-bridge.md` request-shape/diagnostics section plus ten new env rows, `.env.example` switch block, `mcp-brain-bridge` README invariant + ADR-004. 23 new tests in `tests/test_brain_responses_alignment.py`; full suite 554 passed with the one pre-existing failure; `debug.provider` always carries the new keys including on fatal turns.
 
 - **Responses API best-practice audit recorded for later implementation (Task 329, no code change):** a research pass against the current official OpenAI Responses API material — the create reference and the conversation-state, reasoning, text, prompt-caching, error-codes, your-data and streaming guides on `developers.openai.com`, the Cookbook "per-run spending controller" sample, and the `openai-python` 2.54.0 `ResponseCreateParams` (generated from the OpenAPI spec) — audited against `mcp-brain-bridge/server.py`, the repository's only provider call site. Ten findings are recorded in `tasks/backlog/329-responses-api-best-practices-alignment.md` with the official quote, the code citation, the impact and the proposed fix: F1 `store` never sent (responses stored provider-side by default while the system prompt, task file and diffs are sent); F2 reasoning items and assistant `phase` dropped on every turn, against the official "preserve every item in the response's `output` array"; F3 no `truncation` (the default `disabled` fails with a 400) and no `context_management` compaction behind a `chars // 4` estimate against a 1M-token window; F4 `prompt_cache_key` never sent although a cache-split descriptor is computed and deliberately kept off the wire, and `cached_tokens` never read; F5 the response `model` never read, so a silent model substitution is invisible; F6 every 429 retried and `error.code` never parsed, against the official "retrying billing, spend, or quota errors won't restore API access"; F7 a fatal 4xx escaping `brain_turn` as a raw exception instead of a REPORT with `debug.provider`; F8 the reasoning-effort ladder omitting `minimal` with an unknown-value fallback that raises effort, and no validation against the official vocabulary; F9 configuration hygiene (silent `BRAIN_MAX_TOKENS` fallback, dead `_FATAL_STATUS`, vestigial `_send_with_learning`, stale bytecode, and a CHANGELOG claim about a correction path the code no longer contains); F10 the system prompt as a `role: "system"` item instead of the top-level `instructions` field. The same record is saved to project memory (`architecture/responses_api_best_practice_audit_2026_10_21`), together with a verified-correct table and three implementation scopes (D1 request-shape and observability, D2 transcript continuity and context, D3 record only). Audit caveat recorded in the task: the live peer is a local gateway on `127.0.0.1:8081`, not `api.openai.com`, and it was not probed, so every parameter claim is "documented by OpenAI" rather than "verified live" — a gateway probe is a prerequisite for any scope.
@@ -23,6 +29,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Stale plugin citations corrected (same task):** the executor's `src/loop.ts 205-437` reference now names the real gate (`shouldContinue` at `src/loop.ts:458-492`) and handler (`handleSessionIdle` at `src/loop.ts:552-853`); the stop-file claim now states that the code reads only the projectDir `.opencode/STOP_GOAL` path (`src/index.ts:284-296`) and that the project-root path is never read; the "exact-only" slash list now covers the full parser surface (objective, block reason, resume, and evidence accept arguments; status, clear, and complete are exact-only); the missing `/goal resume` and `/goal evidence` slash inputs are documented; the goal lane's "exactly two goal writes" rule becomes three writes plus resume, matching the restored `goal_set` trigger.
 - **Compaction task-boundary gap closed (same task):** the previous task being finished and the Manager defining a new task in the same session now triggers `compact_context` with `keepTurns` 0 and `mode` `compact`, and the todo list is recovered with `todoread` rather than from a remembered transcript.
+- **Layered provider timeouts raised and made tunable (task 331 follow-up):** big `xhigh`/`max` turns were dying with `provider overall deadline hit (500.0s) ... RemoteProtocolError: Server disconnected without sending a response`. Root cause was three stacked ceilings where the tightest won: `zen-proxy`'s hard-coded `urlopen(timeout=300)` dropped any upstream call thinking longer than 5 minutes, and the bridge's hard-coded `_OVERALL_DEADLINE_S = 500` fired during the retry that followed. The proxy timeout is now `ZEN_PROXY_UPSTREAM_TIMEOUT` (default 900) and the bridge deadline is `BRAIN_OVERALL_DEADLINE_S` (default 900, fail-loud on malformed values); the MCP client timeout for the brain server moved 600s → 1200s so the client no longer cuts a legitimate turn. Verified live: a deep `xhigh` turn with 7,583 reasoning tokens completes, and both singletons load the new values.
 - **Replayed reasoning items sanitized at send time (Tasks 330 + 331):** `gpt-6-luna` turns with replayed history failed 400 twice — first `Unknown parameter: 'input[N].status'` (upstream attaches execution `status` to reasoning output items; the bridge replayed them verbatim and the strict Luna endpoint rejects the key while `muse-spark-1.3-contributor` silently accepts it), then `Invalid 'input[N].id': string too long` (the gateway mints ids longer than its own 64-char input cap, e.g. `rs_` + 64 hex = 67 chars; confirmed by an OpenAI community report of platform-minted over-limit ids). `_sanitize_replay_item` in `mcp-brain-bridge/server.py` now drops the `status` key and skips whole items whose string `id` exceeds 64 chars (never truncated — the id is bound to `encrypted_content`); the skip diagnostic records only the id length and the cap, never item fields. Send-time, so existing transcripts are fixed without migration; capture stays verbatim. Proven live against the Go gateway: a real provider-issued blob replayed with both defects returns `completed`. 27 + 3 new tests in `tests/test_brain_responses_alignment.py`; ADR-005/ADR-006 in `mcp-brain-bridge/DECISIONS.md`.
 - **False-green verification command (same task):** the `uv run tests/test_prompt_sync.py` form ran the file as a script with no main block and exited 0 without executing a single assertion; the working form is `uv run --with pytest python -m pytest tests/test_prompt_sync.py -q` (16 passed).
 - **Compaction fragment retired (same task):** `prompts/fragments/22-compaction_protocol.md` moved to `prompts/archive/` with an archival header, removed from `prompts/manifest.txt`, and dropped from the splitter `TOP_LEVEL_TAGS` (21 to 20); split-to-assemble drift introduces zero new lines versus the pre-existing night-mode and language-policy gap.
diff --git a/LLM.txt b/LLM.txt
index 60ee24d..4cac8aa 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -106,12 +106,17 @@ Store this value — you will use it to construct absolute paths in the global c
 Create the global OpenCode directories:
 
 ```bash
-for d in mcp-context-server mcp-memory-server mcp-lint-server mcp-brain-bridge mcp-common; do
+for d in mcp-context-server mcp-memory-server mcp-lint-server mcp-brain-bridge mcp-common zen-proxy; do
   mkdir -p ~/.config/opencode/$d
 done
 mkdir -p ~/.config/opencode/skills
 ```
 
+> `zen-proxy` is not an MCP server — it is the loopback gateway sidecar the
+> Brain Bridge calls as its provider (`BRAIN_API_BASE` → `127.0.0.1:8081`).
+> It is installed globally alongside the servers so one provisioning pass
+> covers both. See the copy block below and `docs/zen-proxy.md`.
+
 ---
 
 ## 5. Copy MCP Servers and Make Them Executable
@@ -128,6 +133,12 @@ done
 # nesting to mcp-common/mcp-common when the destination already exists).
 cp -a /tmp/cognitive-lead-hq/mcp-common/. ~/.config/opencode/mcp-common/
 
+# zen-proxy: the gateway sidecar the Brain calls as its provider. Source only —
+# it is stdlib-only, so the venv has nothing to install (built in §7.5).
+cp /tmp/cognitive-lead-hq/zen-proxy/{proxy.py,pyproject.toml,README.md,DECISIONS.md} \
+   ~/.config/opencode/zen-proxy/
+chmod +x ~/.config/opencode/zen-proxy/proxy.py
+
 # Preserve system-prompt.md globally for the user's Orchestrator
 cp /tmp/cognitive-lead-hq/system-prompt.md ~/.config/opencode/system-prompt.md
 
@@ -291,7 +302,7 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
 }
 ```
 
-The `plugins` entry loads **`smart-compact`** (install it with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` — Step 7.7) plus **`goal`** (install it with `opencode plugin add github:mokhtarabadi/opencode-goal-plugin` — Step 7.7, tracks one long-running objective with `/goal` set, status, block, complete, clear) plus **`opencode-todolist`** (install it with `opencode plugin add opencode-todolist` — Step 7.7, restores V1 `todowrite`/`todoread` plus the TUI sidebar strip). The `compaction` block keeps OpenCode's native auto-compaction on as the safety net while retaining a larger recent tail; Smart Compact then provides the manual high-fidelity layer. The terminal client config `~/.config/opencode/cli.json` is V2-native (no project `cli.json`, no `tui.json`):
+The `plugins` entry loads **`smart-compact`** (install it with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` — Step 7.7) plus **`goal`** (install it with `opencode plugin add github:mokhtarabadi/opencode-goal-plugin` — Step 7.7, tracks one long-running objective per session in `.opencode/goals/` with `/goal` set, status, block, complete, clear) plus **`opencode-todolist`** (install it with `opencode plugin add opencode-todolist` — Step 7.7, restores V1 `todowrite`/`todoread` plus the TUI sidebar strip). The `compaction` block keeps OpenCode's native auto-compaction on as the safety net while retaining a larger recent tail; Smart Compact then provides the manual high-fidelity layer. The terminal client config `~/.config/opencode/cli.json` is V2-native (no project `cli.json`, no `tui.json`):
 
 ```json
 {
@@ -324,12 +335,18 @@ The config in Step 7 points at services — they must be running before OpenCode
 # Python singletons (Linux): install + start the 6 systemd user units
 # (run from your clone of this repo — services/ ships in the clone, no /tmp copy needed)
 mkdir -p ~/.config/systemd/user
-cp services/mcp-*.service ~/.config/systemd/user/
+cp services/mcp-*.service services/zen-proxy.service ~/.config/systemd/user/
 systemctl --user daemon-reload
 for s in lint context memory decision brain telegram; do
   systemctl --user enable --now mcp-$s
 done
 
+# zen-proxy: the Brain's provider hop. Build its venv with uv (no deps) and
+# start it BEFORE the brain, so the first brain_turn does not race the port.
+cd ~/.config/opencode/zen-proxy && uv venv .venv
+systemctl --user enable --now zen-proxy
+curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8081/health   # 200
+
 # Blowsh singleton (any OS with Docker): one persistent container
 docker run -d --name blowsh-singleton --restart unless-stopped \
   -p 127.0.0.1:8107:8107 \
@@ -344,7 +361,9 @@ macOS/Windows equivalents (launchd plist template, Task Scheduler/NSSM): `docs/s
 Verify before continuing:
 
 ```bash
-opencode mcp list   # 7/7 connected
+opencode mcp list                      # 7/7 connected
+systemctl --user is-active zen-proxy    # active — the Brain's provider hop
+curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8081/health   # 200
 ```
 
 ---
@@ -401,7 +420,7 @@ Telemetry-free cache/SSRF defaults (`CACHE_TTL_MS=300000`, `ALLOW_PRIVATE_URLS=f
 
 ## 7.7. Plugins
 
-Install the three platform plugins — **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`, lossless V2-native context compaction, maintained in its own repo) plus **`goal`** (`opencode-goal-plugin`, tracks one long-running objective with `/goal` set, status, block, complete with evidence, clear, maintained in its own repo) plus **`todolist`** (`opencode-todolist`, restores V1 `todowrite`/`todoread` plus the TUI sidebar strip removed in V2):
+Install the three platform plugins — **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`, lossless V2-native context compaction, maintained in its own repo) plus **`goal`** (`opencode-goal-plugin`, tracks one long-running objective per session in `.opencode/goals/<session-id>.json` with `/goal` set, status, block, complete with evidence that is executed at completion, clear, maintained in its own repo) plus **`todolist`** (`opencode-todolist`, restores V1 `todowrite`/`todoread` plus the TUI sidebar strip removed in V2):
 
 ```bash
 # Interim (works now, installs from the pushed repo):
@@ -437,7 +456,7 @@ Then create the recommended smart-compact global config at `~/.config/opencode/s
     "stripReasoning": { "enabled": true, "thresholdChars": 500 }
   },
   "tokens": { "enabled": true, "emergencyBudgetTokens": 50000 },
-  "awareness": { "enabled": true, "warnRatio": 0.7, "emergencyRatio": 0.9, "rearmStep": 0.05 }
+  "awareness": { "enabled": true, "warnRatio": 0.5, "emergencyRatio": 0.8, "rearmStep": 0.05, "autoTrimRatio": 0.5 }
 }
 ```
 
@@ -560,6 +579,7 @@ After completing all steps, verify:
 - [ ] `~/.config/opencode/mcp-lint-server/server.py` exists and is executable
 - [ ] `~/.config/opencode/mcp-brain-bridge/server.py` exists and is executable (plus its sibling modules `capability.py`, `preflight.py`, `loop_guard.py`, `session_ledger.py`)
 - [ ] `~/.config/opencode/mcp-common/src/mcp_common/env.py` exists
+- [ ] `~/.config/opencode/zen-proxy/proxy.py` exists and is executable, `~/.config/opencode/zen-proxy/.venv/bin/python` exists (built with `uv venv`), and `systemctl --user is-active zen-proxy` returns `active` on `127.0.0.1:8081` (`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/health` → 200); the unit reads `~/.config/opencode/.env` and needs no API key of its own
 - [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` (36 skills total)
 - [ ] `~/.config/opencode/agents/cognitive-executor.md` exists
 - [ ] `~/.config/opencode/agents/cognitive-discovery.md` exists
diff --git a/README.md b/README.md
index 77190e6..3b288fc 100644
--- a/README.md
+++ b/README.md
@@ -163,6 +163,7 @@ cp .env.example .env
 ### Documentation
 
 - [Brain Bridge Server](mcp-brain-bridge/server.py) — one tool, system-prompt loader + Responses-API call + XML extractor
+- [zen-proxy](docs/zen-proxy.md) — the loopback gateway hop behind `BRAIN_API_BASE` (session minting, model filters, effort rewrite, timeout ordering)
 - [Blowsh Web Skill](skill-templates/blowsh/SKILL.md) — live-web search/fetch/crawl via the blowsh MCP server
 - [Cognitive Executor Agent](agents/cognitive-executor.md) (Bridge + Autopilot sections)
 - [Setup Guide](docs/setup.md)
@@ -198,6 +199,12 @@ cp .env.example .env
 │   └── server.py                       # FastMCP server for persistent project memory
 ├── mcp-brain-bridge/                  # Unified Brain bridge
 │   └── server.py                       # FastMCP `BrainBridge`: brain_turn (prompt loader + LLM + XML extract)
+├── zen-proxy/                          # Loopback gateway sidecar (NOT an MCP server)
+│   ├── proxy.py                        # Zen/Go mount proxy: session minting, model filters, effort rewrite
+│   ├── pyproject.toml                  # Stdlib-only; exists so `uv venv` provisions the runtime
+│   └── DECISIONS.md                    # ADRs: repo ownership, upstream timeout, POST gating
+├── services/                           # systemd units / launchd plists for the singletons
+│   └── zen-proxy.service               # Brain's provider hop on 127.0.0.1:8081
 ├── prompts/                            # System prompt source tree (fragments + shared partials)
 │   ├── README.md                       # Authoring workflow guide
 │   ├── manifest.txt                    # Ordered fragment list (assembly order)
@@ -481,7 +488,7 @@ opencode --agent cognitive-executor
 
 ### OpenCode Plugins
 
-Three plugins: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) — lossless, V2-native context compaction, maintained in its own repo. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Smart Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. It never mutates the stored transcript — it stores a per-session compaction state and applies it to the model-visible messages per request. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`. Install with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` (the Git spec, until it is published to npm); full guide in [`docs/compaction.md`](docs/compaction.md). Plus **`goal`** (`opencode-goal-plugin`, maintained in its own repo) — tracks one long-running objective in `.opencode/goal-state.json` with evidence in `.opencode/goal-evidence.json`: `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal resume`, `/goal evidence <args>`, `/goal complete` (needs file citations plus passing tests), `/goal clear` (Manager lane; agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`, never write the state files directly). The agent creates the goal with `goal_set` when an objective is defined, blocks with `goal_block`, records proof with `goal_evidence` before closing, and resumes with `goal_resume` after a block or interruption. Install with `opencode plugin add github:mokhtarabadi/opencode-goal-plugin` (the Git spec, `opencode-goal-plugin` once published to npm). Plus **`todolist`** (`opencode-todolist`) — restores the V1 session todo tools (`todowrite`/`todoread`) removed in V2, with a live TUI sidebar strip. Install with `opencode plugin add opencode-todolist` and enable the strip via `plugins` in `~/.config/opencode/cli.json`.
+Three plugins: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) — lossless, V2-native context compaction, maintained in its own repo. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Smart Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. It never mutates the stored transcript — it stores a per-session compaction state and applies it to the model-visible messages per request. At `awareness.autoTrimRatio` it also trims tool output on its own, losslessly, without summarizing a turn. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`. Install with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` (the Git spec, until it is published to npm); full guide in [`docs/compaction.md`](docs/compaction.md). Plus **`goal`** (`opencode-goal-plugin`, maintained in its own repo) — tracks one long-running objective per session in `.opencode/goals/<session-id>.json` with evidence in the matching `.evidence.json` sidecar (a legacy `.opencode/goal-state.json` stays a read fallback that migrates on first write, and another session in the same project never sees or continues this goal): `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal resume`, `/goal evidence <args>`, `/goal complete` (needs file citations plus tests that really pass — the plugin executes every recorded command and reads its real exit code), `/goal clear` (Manager lane; agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`, never write the state files directly). The agent creates the goal with `goal_set` when an objective is defined, blocks with `goal_block`, records proof with `goal_evidence` before closing, and resumes with `goal_resume` after a block or interruption. Install with `opencode plugin add github:mokhtarabadi/opencode-goal-plugin` (the Git spec, `opencode-goal-plugin` once published to npm). Plus **`todolist`** (`opencode-todolist`) — restores the V1 session todo tools (`todowrite`/`todoread`) removed in V2, with a live TUI sidebar strip. Install with `opencode plugin add opencode-todolist` and enable the strip via `plugins` in `~/.config/opencode/cli.json`.
 
 ---
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index e7761d7..7612124 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -102,7 +102,7 @@ To prevent hallucinations and respect hidden project constraints, you MUST integ
 Context is finite. Two layers keep long sessions productive, and the agent's durable state lives in the task file and project memory, never only in the chat.
 
 1. **Native safety net.** OpenCode auto-compacts near the model limit: it replaces older turns with one lossy summary and keeps the most recent ~20k tokens (config: `compaction.keep.tokens`). Never depend on it to preserve working state — write the essentials to the task file as you go.
-2. **Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) is installed globally and loaded by OpenCode. It is V2-native: it stores a per-session compaction state and applies it to the model-visible messages per request, so it never mutates the stored transcript. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. After a prune, prefer a cheap fresh run of the source tool; call `read_omitted_content` with its Content ID (`omitted-NNNN`) ONLY when the output cannot be reproduced cheaply, never speculatively. On a cache miss, re-run the source tool once.
+2. **Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) is installed globally and loaded by OpenCode. It is V2-native: it stores a per-session compaction state and applies it to the model-visible messages per request, so it never mutates the stored transcript. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. Above `awareness.autoTrimRatio` it trims tool output by itself between requests — expect a tool result to read as a notice even when you did not call `compact_context`; that is the plugin working as intended, and the original is one `read_omitted_content` call away. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. After a prune, prefer a cheap fresh run of the source tool; call `read_omitted_content` with its Content ID (`omitted-NNNN`) ONLY when the output cannot be reproduced cheaply, never speculatively. On a cache miss, re-run the source tool once.
 Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
 
 3. **Survival contract.** Keep the task file holding: the active task id and Kanban lane, the pinned `[fed-context]` block with citations, the current persona/seat, the locked mode (manual or autopilot), the latest staged diff hash, open blockers, and the next action. Resume from that file after any compaction — never from a summary.
@@ -112,12 +112,12 @@ Task file is the sole reconcile target. Smart Compact via `compact_context` is t
 ### Goal Plugin Boundary - global helper, not truth
 
 - HQ task file in tasks backlog plus in-progress plus qa plus completed remains single source of truth.
-- The file at `.opencode/goal-state.json` is external scratch only and never replaces Kanban state.
+- Goal state is per session: `.opencode/goals/<session-id>.json` with a matching `.evidence.json` sidecar, and a legacy `.opencode/goal-state.json` kept only as a read fallback that migrates on the next write. Those files are external scratch only and never replace Kanban state. A second session in the same project has its own file and never sees, continues, or clears this goal.
 - The goal plugin registers its idle handler for every project it loads, so it is not HQ-aware: with an active goal and no stop marker, it injects a continuation prompt whenever the session idles. The tracked `.opencode/STOP_GOAL` marker in the project directory brakes ONLY that idle loop and never blocks the five agent tools. A `STOP_GOAL` file at the project root does nothing — only the `.opencode/` path counts, and this repo ships the marker so the brake is committed, not local.
-- Goal slash surface: setting the objective, blocking with a reason, resuming, and recording evidence accept arguments; status, clear, and complete are exact-only. Blocking and completing run only on an active goal; resuming runs only on a parked (blocked or interrupted) goal. Agent lane is tools-only (`goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`, exact schemas, no extra properties, titles and reasons are literal data). Never write `.opencode/goal-state.json` or `.opencode/goal-evidence.json` with file tools. Busy lease means retry the same call next turn, never work around it. Corrupt state means report to the human, never invent.
+- Goal slash surface: setting the objective, blocking with a reason, resuming, and recording evidence accept arguments; status, clear, and complete are exact-only. Blocking and completing run only on an active goal; resuming runs only on a parked (blocked or interrupted) goal. Agent lane is tools-only (`goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`, exact schemas, no extra properties, titles and reasons are literal data). Never write a file under `.opencode/goals/` (or the legacy `.opencode/goal-state.json` / `.opencode/goal-evidence.json`) with file tools. Busy lease means retry the same call next turn, never work around it. Corrupt state means report to the human, never invent.
 - Goal evidence plus verifier gate is optional external check. HQ QA plus Code Reviewer gates stay authoritative.
 - Why these lanes are yours: the Brain has no tool access of its own; it emits only a plan and checklist. Every plugin call below is yours alone.
-- Goal sync rule (executor behavior, plugin untouched): Hands performs exactly three goal writes per goal with these exact signatures — `goal_set(title)`, `goal_block(reason)`, `goal_evidence(id, claim, files[], tests[{command, exitCode}])`, `goal_complete()` (no arguments), `goal_resume()` (no arguments). WHEN: `goal_set` when an objective is defined (an XML implementation arrives or the Manager defines a new objective in chat) — the lane is unreachable without it, since no other call creates a goal; `goal_block` when blocked; `goal_evidence` then `goal_complete` at closure; `goal_resume` after a block or an interruption. Evidence gate: every criterion needs one existing file inside projectDir AND one test with exitCode 0, else `Complete blocked: <reason>. Add file citations plus passing tests to evidence.` Busy lease: on `Goal is busy with another turn. Retry shortly.` retry the same call next turn. Titles that look like path escapes (`..`, a leading `/`, drive letters) are rejected — keep titles plain prose. One goal per project directory, shared across sessions, lease TTL 120s. No background reads or polling of goal state files. Kanban task files remain single source of truth; goal files are scratch resume pointers only. On any conflict Kanban wins. Never write `.opencode/goal-state.json` or `.opencode/goal-evidence.json` with file tools; use goal tools only with exact schemas; on corrupt state report to the human.
+- Goal sync rule (executor behavior, plugin untouched): Hands performs exactly three goal writes per goal with these exact signatures — `goal_set(title)`, `goal_block(reason)`, `goal_evidence(id, claim, files[], tests[{command, exitCode}])`, `goal_complete()` (no arguments), `goal_resume()` (no arguments). WHEN: `goal_set` when an objective is defined (an XML implementation arrives or the Manager defines a new objective in chat) — the lane is unreachable without it, since no other call creates a goal; `goal_block` when blocked; `goal_evidence` then `goal_complete` at closure; `goal_resume` after a block or an interruption. Evidence gate: every criterion needs one existing file inside projectDir AND every recorded test command to exit 0, else `Complete blocked: <reason>. Add file citations plus passing tests to evidence.` The plugin executes those commands itself at completion time, so a declared `exitCode` is not proof and the gate can take minutes (300s per command, 600s total, 20-command cap) — expect a slow completion, never retry it just because it is slow. Busy lease: on `Goal is busy with another turn. Retry shortly.` retry the same call next turn. Titles that look like path escapes (`..`, a leading `/`, drive letters) are rejected — keep titles plain prose. One goal per session at `.opencode/goals/<session-id>.json` (the legacy project-scoped file is a read fallback only), with a base lease TTL of 120s extended to cover a completion proof pass; another session's goal is never yours to read, continue, or clear. No background reads or polling of goal state files. Kanban task files remain single source of truth; goal files are scratch resume pointers only. On any conflict Kanban wins. Never write a goal state or evidence file with file tools; use goal tools only with exact schemas; on corrupt state report to the human.
 - Smart Compact operations in the Compaction section above remain unchanged.
 
 ## Capability Preflight (session start)
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index 604e9f5..ed7c8cf 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -140,6 +140,17 @@ repo-root `.env`). Real process env wins; blank counts as unset. See
 | `BRAIN_USE_INSTRUCTIONS` | off — when on, the system prompt moves to top-level `instructions` instead of a `role: system` input item (F10; probed OK) |
 | `BRAIN_CHARS_PER_TOKEN` | unset — explicit chars-per-token override for the pre-send estimate; otherwise calibrated from observed `usage.input_tokens`, else `4.0` (F3) |
 | `BRAIN_COMPACTION_THRESHOLD` | `100000` — token threshold for `context_management` compaction (F3) |
+| `BRAIN_HTTP_READ_TIMEOUT` | `900` — httpx read timeout for the provider call |
+| `BRAIN_OVERALL_DEADLINE_S` | `900` — whole retry-sequence deadline; must sit at or above any proxy hop in the path and below the MCP client timeout |
+
+The local `BRAIN_API_BASE` is `http://127.0.0.1:8081/go/resp`, served by the
+`zen-proxy` slice in this repo (`docs/zen-proxy.md`, unit
+`services/zen-proxy.service`). That hop imposes its own upstream socket
+timeout, so keep the ordering sound: `ZEN_PROXY_UPSTREAM_TIMEOUT` ≤
+`BRAIN_OVERALL_DEADLINE_S` ≤ the MCP client's execution timeout. A proxy
+timeout below a real turn's duration surfaces here as
+`RemoteProtocolError: Server disconnected without sending a response`
+followed by `provider overall deadline hit`.
 
 `BRAIN_INPUT_BUDGET` defaults to 1,000,000 chars (~217k input tokens at
 the measured ~4.6 chars/token) — room for full context and diff reports
diff --git a/docs/compaction.md b/docs/compaction.md
index c322138..ba31297 100644
--- a/docs/compaction.md
+++ b/docs/compaction.md
@@ -41,7 +41,7 @@ opencode plugin add github:mokhtarabadi/opencode-goal-plugin
 opencode plugin add opencode-goal-plugin
 ```
 
-`/goal` tracks one long-running objective in `.opencode/goal-state.json` with evidence in `.opencode/goal-evidence.json`: `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal resume`, `/goal evidence <args>`, `/goal complete` (needs file citations plus passing tests), `/goal clear` — Manager lane. Agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`; never write the state or evidence files with file tools; record evidence via `goal_evidence` before `goal_complete`; busy lease means retry next turn; corrupt state means report to the human. The agent opens the goal with `goal_set` when an objective is defined and resumes it with `goal_resume` after a block or interruption. The plugin reads its stop marker only at the projectDir `.opencode/STOP_GOAL` path (the project-root `STOP_GOAL` is never read); that marker is tracked in this repo, so the idle auto-continue is braked by a committed control rather than a local file, and it stops only the idle loop — never the five agent tools.
+`/goal` tracks one long-running objective per session in `.opencode/goals/<session-id>.json` with evidence in the matching `.evidence.json` sidecar (a legacy `.opencode/goal-state.json` stays a read fallback that migrates on first write): `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal resume`, `/goal evidence <args>`, `/goal complete` (needs file citations plus tests that really pass — the plugin executes every recorded command and reads its real exit code), `/goal clear` — Manager lane. Agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`; never write the state or evidence files with file tools; record evidence via `goal_evidence` before `goal_complete`; busy lease means retry next turn; corrupt state means report to the human. The agent opens the goal with `goal_set` when an objective is defined and resumes it with `goal_resume` after a block or interruption. Every slash mutation takes the state lease too, so a `set`, `block`, `resume`, or `clear` that lands while a completion is running answers `Goal is busy with another turn. Retry shortly.`; a completion holds that lease for the whole proof pass, which is why a slow `/goal complete` can make a concurrent change wait. The plugin reads its stop marker only at the projectDir `.opencode/STOP_GOAL` path (the project-root `STOP_GOAL` is never read); that marker is tracked in this repo, so the idle auto-continue is braked by a committed control rather than a local file, and it stops only the idle loop — never the five agent tools.
 
 This writes the package (or path) into `plugins` in the global config; OpenCode loads it at startup. New machines get the entry from the global `opencode.json` in `LLM.txt` §7 plus the install command in `LLM.txt` §7.7.
 
@@ -60,6 +60,17 @@ This writes the package (or path) into `plugins` in the global config; OpenCode
 
 Compaction is scheduled by the command and applied on the next model request; summaries are generated at command time with the session's own model.
 
+### Automatic at pressure (agent needs no action)
+
+Two things happen without anyone asking:
+
+| Layer | Trigger | Effect | Lossy? |
+| --- | --- | --- | --- |
+| Tool-output trim (`awareness.autoTrimRatio`) | Fill crosses the ratio (platform: `0.5`) | Queues a `trim` for the next request, reusing the manual trim pass. Once per sustained pressure period, not once per request | No — originals stay cached under a Content ID |
+| Advisory reminder (`awareness.warnRatio`) | Fill crosses the ratio (platform: `0.5`, emergency `0.8`) | One system part telling the agent how full the window is and what to call | No |
+
+Summarization is not automatic on purpose: replacing turns with summaries needs the agent's own judgement about which detail still matters. The plugin never overwrites a pending compaction with a weaker trim.
+
 ### Agent-callable tool
 
 The agent compresses the session itself with the `compact_context` tool (never the `/magic-*` slash commands), which runs the same logic as `/magic-compact` (shared `src/actions.ts` in the plugin, so the paths cannot drift). Effect is async (stored now, prunes next request) — do not re-call to verify. In autopilot never ask the Manager to run slash commands:
@@ -91,6 +102,8 @@ Invalid input returns a friendly message instead of failing. The slash commands
 
 JSONC, project over global: `.opencode/smart-compact.jsonc` over `~/.config/opencode/smart-compact.jsonc` over built-in defaults. On a fresh machine create the global file with this recommended content right after `opencode plugin add` (same snippet lives in `LLM.txt` §7.7, so an installer LLM writes it verbatim):
 
+The platform runs `warnRatio 0.5` / `emergencyRatio 0.8` because a 1M-token window at the shipped `0.7` would only warn at ~734K tokens. `autoTrimRatio 0.5` is the one automatic action and it is lossless: it queues a tool-output-only trim for the next request, summarizes nothing, and leaves every pruned original in the cache. A per-session latch means one sustained pressure period trims once; it re-arms only after the fill grows by `rearmStep` or drops below the line and rises again, so a long session above the threshold does not queue a trim on every request.
+
 ```jsonc
 // Recommended global config for smart-compact.
 {
@@ -110,7 +123,7 @@ JSONC, project over global: `.opencode/smart-compact.jsonc` over `~/.config/open
     "stripReasoning": { "enabled": true, "thresholdChars": 500 }
   },
   "tokens": { "enabled": true, "emergencyBudgetTokens": 50000 },
-  "awareness": { "enabled": true, "warnRatio": 0.7, "emergencyRatio": 0.9, "rearmStep": 0.05 }
+  "awareness": { "enabled": true, "warnRatio": 0.5, "emergencyRatio": 0.8, "rearmStep": 0.05, "autoTrimRatio": 0.5 }
 }
 ```
 
diff --git a/docs/services.md b/docs/services.md
index c104de1..b3a14f3 100644
--- a/docs/services.md
+++ b/docs/services.md
@@ -13,6 +13,12 @@ One supervised instance of each MCP server, shared across all sessions and proje
 | brain     | 8105 | mcp-brain                 |
 | telegram  | 8106 | mcp-telegram              |
 | blowsh    | 8107 | blowsh-singleton (Docker) |
+| zen-proxy | 8081 | zen-proxy (not MCP — the Brain's provider hop) |
+
+`zen-proxy` is listed here because it is provisioned and supervised the same
+way, but it speaks the OpenAI Responses/Chat API rather than MCP. Its unit
+reads the same global `.env`; it needs no API key of its own (the caller's
+`Authorization` header passes through). See `docs/zen-proxy.md`.
 
 ## Security (accepted risk)
 
diff --git a/docs/zen-proxy.md b/docs/zen-proxy.md
new file mode 100644
index 0000000..3a8ea00
--- /dev/null
+++ b/docs/zen-proxy.md
@@ -0,0 +1,127 @@
+# zen-proxy — loopback gateway sidecar
+
+The sidecar that lets an OpenAI-compatible client talk to the OpenCode
+Zen/Go gateways. Source: `zen-proxy/proxy.py` (stdlib only). Unit:
+`services/zen-proxy.service`. Installed globally at
+`~/.config/opencode/zen-proxy/`.
+
+## Why it exists
+
+The gateways are stricter than a generic OpenAI client:
+
+1. **Session header required.** Requests without `x-opencode-session` are
+   rejected. The proxy mints one when the caller supplies none.
+2. **User-agent gate.** Cloudflare in front of `opencode.ai` answers HTTP
+   1010 to bare SDK agents. The proxy sends a browser UA unless a genuine
+   `opencode/...` client is talking, in which case it forwards the client's
+   own UA untouched.
+3. **Model lists merge by id.** An OpenAI-compatible client that mounts both
+   API styles in one connection shows models that cannot work on that style.
+   Each mount filters `GET /models` to the ids that actually work there.
+4. **Effort shape differs.** Clients send chat-style `reasoning_effort`;
+   the `/responses` endpoints accept only `reasoning: {effort}`. The proxy
+   rewrites one into the other so `high`/`xhigh`/`max` reach the model.
+
+Historically the consumer was Open-WebUI (retired 2026-09-19). The live
+consumer is the Brain Bridge: `BRAIN_API_BASE=http://127.0.0.1:8081/go/resp`.
+
+## Routes
+
+| Mount | Upstream | Serves |
+| --- | --- | --- |
+| `/zen/chat` | `opencode.ai/zen/v1` | free chat models |
+| `/zen/resp` | `opencode.ai/zen/v1` | free Responses models |
+| `/go/chat` | `opencode.ai/zen/go/v1` | Go subscription, chat completions |
+| `/go/resp` | `opencode.ai/zen/go/v1` | Go subscription, Responses API |
+
+`GET /health` → `{"status":"ok"}`.
+
+Both `GET /models` and `POST` are gated by the mount allowlist. A model
+posted to the wrong mount returns `404 ModelNotServedHere` naming the correct
+mount, or `no known route` when no mount serves it.
+
+## Verified allowlists (2026-10-22)
+
+- `/go/resp` — 13: `muse-spark-1.2/1.3-contributor`, `gpt-5.6-luna`,
+  `gpt-6-luna`, `grok-4.6`, `grok-4.7`, `glm-5.3`, `glm-5.3-flash`,
+  `kimi-k3`, `qwen3.8-max`, `mimo-v2.6-pro`, `deepseek-v4-pro`,
+  `deepseek-v4.1-flash`.
+  Every Go chat model probed on 2026-10-21 also answered on `/responses`;
+  the earlier "only six Responses models" reading came from the docs table,
+  not from the gateway.
+- `/go/chat` — the Go chat set. The served count tracks upstream and drifts
+  (36 upstream ids, 23 allowlisted present at the last check); re-probe
+  before trusting a number.
+- `/zen/chat`, `/zen/resp` — free models only. Free-tier generation is
+  blocked server-side for non-OpenCode callers (see the A3 gate finding in
+  the `code-server` history); the mount exists for list parity.
+
+## Configuration
+
+Read from the single global `~/.config/opencode/.env` via the unit's
+`EnvironmentFile`.
+
+| Variable | Default | Meaning |
+| --- | --- | --- |
+| `ZEN_SESSION_ID` | zero UUID | Fallback session header when the caller sends none |
+| `ZEN_PROXY_UPSTREAM_TIMEOUT` | `900` | Upstream socket timeout, seconds |
+| `ZEN_PROXY_AUDIT` | `0` | `1` writes prompts + responses to `~/.local/share/zen-proxy/audit-logs/` |
+
+No API key of its own: the caller's `Authorization` header passes through.
+
+### Timeout ordering (binding)
+
+```
+zen-proxy upstream timeout  ≤  caller overall deadline  ≤  MCP client execution
+       900s (default)             900s (brain default)        1200s
+```
+
+A hidden 300s here is what killed long reasoning turns before 2026-10-22: a
+deep `gpt-6-luna` turn spends 14-19K reasoning tokens, i.e. five to ten
+minutes, so the proxy dropped the socket with no response, the bridge saw
+`RemoteProtocolError`, retried, and reported
+`provider overall deadline hit (500.0s)`.
+
+## Install (global)
+
+```bash
+# from a clone of this repo
+mkdir -p ~/.config/opencode/zen-proxy
+cp zen-proxy/{proxy.py,pyproject.toml,README.md,DECISIONS.md} ~/.config/opencode/zen-proxy/
+chmod +x ~/.config/opencode/zen-proxy/proxy.py
+cd ~/.config/opencode/zen-proxy && uv venv .venv     # no deps to install
+cp services/zen-proxy.service ~/.config/systemd/user/
+systemctl --user daemon-reload
+systemctl --user enable --now zen-proxy.service
+curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8081/health   # 200
+```
+
+The venv is built by `uv` but the unit launches the venv interpreter
+directly, matching every other slice: a running service must not depend on
+`uv` being on PATH.
+
+## Verification
+
+```bash
+systemctl --user is-active zen-proxy
+for r in go/resp go/chat zen/chat zen/resp; do
+  curl -s "http://127.0.0.1:8081/$r/models" | jq '.data | length'
+done
+# wrong-mount post must be 404 with a hint, not an upstream 400
+curl -s -X POST http://127.0.0.1:8081/go/resp/responses \
+  -H 'Content-Type: application/json' \
+  -d '{"model":"hy3","input":[{"role":"user","content":"x"}]}' | jq .error.type
+# a real Responses turn through the proxy
+curl -s -X POST http://127.0.0.1:8081/go/resp/responses \
+  -H "Authorization: Bearer $BRAIN_API_KEY" -H 'Content-Type: application/json' \
+  -d '{"model":"glm-5.3","input":[{"role":"user","content":"reply: ok"}],"max_output_tokens":64}' | jq -r .status
+```
+
+## Failure modes
+
+| Symptom | Cause | Fix |
+| --- | --- | --- |
+| `502 BadGatewayError` | egress proxy node failed TLS | retry; check the mihomo pool if enabled |
+| `404 ModelNotServedHere` | model posted to the wrong mount | use the mount named in the message |
+| `Server disconnected without sending a response` | upstream slower than `ZEN_PROXY_UPSTREAM_TIMEOUT` | raise the timeout, or lower the caller's reasoning effort |
+| `/models` count dropped | upstream list drift | re-probe upstream and refresh the allowlist |
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 933dcb6..cb2c70c 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -41,3 +41,10 @@
 - **Decision:** `_sanitize_replay_item` returns None for items whose string `id` exceeds 64 chars; the send loop skips them. The skip diagnostic records only the id length and the cap — never the id, type, or any other item field. Never truncate: the id is bound to `encrypted_content` and editing it breaks decryption. Dropping only loses encrypted-context continuity for that turn.
 - **Consequences:** Strict providers accept history replays regardless of id length. The skip applies on the send path for every provider (lenient ones simply never needed it — they ignored the over-long id instead of 400ing). Three regression tests pin the drop, the at-cap pass-through, and the redacted diagnostic. The skip diagnostic records only the id length and the cap, never item fields.
 - **Rollback:** Revert the length check plus the two tests; old transcripts keep working on lenient models.
+
+## [2026-10-22] ADR-007: Provider deadline tunable above the proxy hop
+
+- **Context:** Big `xhigh`/`max` turns died as `provider overall deadline hit (500.0s) ... RemoteProtocolError: Server disconnected without sending a response`. Three stacked ceilings existed; the tightest won: zen-proxy `urlopen(timeout=300)`, bridge `_OVERALL_DEADLINE_S = 500`, httpx read timeout 600, MCP client 600s. A deep `gpt-6-luna` turn spends 14-19K reasoning tokens, i.e. 5-10 minutes.
+- **Decision:** `_OVERALL_DEADLINE_S` becomes `BRAIN_OVERALL_DEADLINE_S` (default 900s, fail-loud on malformed), and the proxy hop becomes `ZEN_PROXY_UPSTREAM_TIMEOUT` (default 900s). Ordering contract: httpx read ≤ bridge overall ≤ MCP client execution, with the proxy at or below the bridge overall so its disconnects surface as retryable rather than as a deadline.
+- **Consequences:** Long reasoning turns complete; a truly hung provider now surfaces later (bounded by the client timeout). The existing test that forced the deadline was updated to patch the new default constant.
+- **Rollback:** Unset both env vars to restore code defaults, or set them to 500/300 explicitly for the old behavior.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 5c6c49f..4b33ac5 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1709,7 +1709,33 @@ _RETRYABLE_STATUS = {429, 500, 502, 503, 504}
 # Overall deadline (seconds) for the whole retry sequence. Sleeps are
 # capped by the remaining budget; hitting the deadline fast-fails instead
 # of sleeping past it.
-_OVERALL_DEADLINE_S = 500.0
+# 2026-10-22: was hard-coded 500, which fired before a single deep
+# xhigh/max turn could finish (gpt-6-luna spends 14-19K reasoning tokens
+# on a large prompt = 5-10 min), so long turns failed as
+# "provider overall deadline hit (500.0s)" no matter the read timeout.
+# Env-tunable; must stay above the proxy's upstream timeout when one is
+# in the path (zen-proxy defaults to 900).
+_DEFAULT_OVERALL_DEADLINE_S = 900.0
+
+
+def _overall_deadline_s() -> float:
+    """Whole-sequence provider deadline; override via BRAIN_OVERALL_DEADLINE_S.
+
+    Fail-loud on a non-numeric or non-positive value: a silent fallback
+    would change the timeout contract without saying so.
+    """
+    raw = os.environ.get("BRAIN_OVERALL_DEADLINE_S", "").strip()
+    if not raw:
+        return _DEFAULT_OVERALL_DEADLINE_S
+    try:
+        val = float(raw)
+    except ValueError:
+        raise RuntimeError(
+            f"BRAIN_OVERALL_DEADLINE_S must be a number, got {raw!r}"
+        )
+    if val <= 0:
+        raise RuntimeError(f"BRAIN_OVERALL_DEADLINE_S must be > 0, got {raw!r}")
+    return val
 
 #: Billing/spend/quota 429 codes that must NEVER be retried (Task 329
 #: F6, per the official error-codes guide): "Retrying billing, spend, or
@@ -1852,14 +1878,15 @@ def _post_with_retry(client: Any, url: str, payload: dict[str, Any]) -> tuple[An
 
     import httpx
 
-    deadline = time.monotonic() + _OVERALL_DEADLINE_S
+    _deadline_s = _overall_deadline_s()
+    deadline = time.monotonic() + _deadline_s
     last_status: int = -1
     last_snippet: str = "no attempt made"
     attempts = 0
     for attempt in range(3):
         if time.monotonic() >= deadline:
             raise _transport_fail(
-                f"provider overall deadline hit ({_OVERALL_DEADLINE_S}s) at "
+                f"provider overall deadline hit ({_deadline_s}s) at "
                 f"{url.rsplit('/', 1)[-1]}: {last_snippet}",
                 attempts,
             )
@@ -1924,7 +1951,7 @@ def _post_with_retry(client: Any, url: str, payload: dict[str, Any]) -> tuple[An
         remaining = deadline - time.monotonic()
         if remaining <= 0:
             raise _transport_fail(
-                f"provider overall deadline hit ({_OVERALL_DEADLINE_S}s) at "
+                f"provider overall deadline hit ({_deadline_s}s) at "
                 f"{url.rsplit('/', 1)[-1]}: {last_snippet}",
                 attempts,
             )
diff --git a/services/DECISIONS.md b/services/DECISIONS.md
index ce98198..7e789e2 100644
--- a/services/DECISIONS.md
+++ b/services/DECISIONS.md
@@ -6,3 +6,17 @@
 - **Decision:** Adopting Living Folder Docs standard for this component.
 - **Consequences:** All future structural or contract changes must be recorded here.
 - **Rollback:** N/A (baseline adoption).
+
+## [2026-10-23] ADR-002: zen-proxy is provisioned from this slice
+
+- **Context:** The Brain's provider hop (`127.0.0.1:8081`) was owned by the
+  `code-server` homelab repo while its only consumer lived here, so every
+  behavioural change landed in a repo that did not own the need.
+- **Decision:** `zen-proxy.service` ships here next to the MCP units, points
+  `ExecStart` at `~/.config/opencode/zen-proxy/.venv/bin/python`, and reads
+  the single global `~/.config/opencode/.env`. It stays out of the `mcp-*`
+  naming because it speaks the OpenAI API, not MCP.
+- **Consequences:** One provisioning pass installs every loopback service;
+  the Brain's provider and its consumer share a repo and an `.env`.
+- **Rollback:** Restore the unit from the `code-server` history and re-point
+  the path; no other service depends on it.
diff --git a/services/README.md b/services/README.md
index 4a7ca10..2cb94c2 100644
--- a/services/README.md
+++ b/services/README.md
@@ -8,6 +8,7 @@ OS service singletons for MCP daemons: systemd units plus launchd plists and Win
 
 - `mcp-context.service` / `mcp-brain.service` / `mcp-lint.service` / `mcp-memory.service` — systemd units (streamable HTTP, loopback only).
 - `mcp-telegram.service` — Telegram sync service unit.
+- `zen-proxy.service` — not an MCP daemon: the loopback gateway sidecar on `127.0.0.1:8081` that the Brain uses as its provider hop (`BRAIN_API_BASE`). Reads the single global `.env` and launches through the venv built by `uv`.
 - `launchd/ai.cognitivelead.mcp-*.plist` — macOS launchd singletons mirroring the systemd units.
 - `windows/mcp-singleton-template.xml` — Windows singleton template.
 
diff --git a/services/zen-proxy.service b/services/zen-proxy.service
new file mode 100644
index 0000000..3442e68
--- /dev/null
+++ b/services/zen-proxy.service
@@ -0,0 +1,28 @@
+[Unit]
+Description=zen-proxy sidecar (OpenAI-compatible clients -> OpenCode Zen/Go gateways, loopback only)
+After=network-online.target
+Wants=network-online.target
+Documentation=file:///home/mohammad/Develop/Projects/cognitive-lead-hq/docs/zen-proxy.md
+
+[Service]
+Type=simple
+# Same global .env every other slice reads (<server-dir>/../.env), so no
+# secret is duplicated. The proxy itself needs no API key: it passes the
+# caller's Authorization header through and only falls back to
+# ZEN_SESSION_ID when the client sends no session header.
+EnvironmentFile=-%h/.config/opencode/.env
+WorkingDirectory=%h/.config/opencode/zen-proxy
+# Outbound egress. Direct by default; uncomment the four lines below to send
+# gateway traffic through the mihomo-subs mixed proxy. NO_PROXY keeps any
+# loopback call out of the tunnel.
+#Environment=HTTP_PROXY=http://127.0.0.1:7890
+#Environment=HTTPS_PROXY=http://127.0.0.1:7890
+#Environment=http_proxy=http://127.0.0.1:7890
+#Environment=https_proxy=http://127.0.0.1:7890
+#Environment=NO_PROXY=localhost,127.0.0.1,::1
+ExecStart=%h/.config/opencode/zen-proxy/.venv/bin/python %h/.config/opencode/zen-proxy/proxy.py
+Restart=always
+RestartSec=3
+
+[Install]
+WantedBy=default.target
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 07e13d0..fd6b7aa 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -41,7 +41,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Execution Log & Reasoning` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
 - **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
 - **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. Deliberate agent config (`[PROJECT_ROOT]/.opencode/smart-compact.jsonc`) is NOT runtime state and MUST NOT be gitignored. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
-- **Goal Plugin Runtime State**: Goal plugin file state (`[PROJECT_ROOT]/.opencode/goal-state.json`, `[PROJECT_ROOT]/.opencode/goal-evidence.json`, `[PROJECT_ROOT]/STOP_GOAL`, `[PROJECT_ROOT]/.opencode/STOP_GOAL`) is runtime state only and MUST be gitignored. It is external scratch and never replaces decentralized task truth.
+- **Goal Plugin Runtime State**: Goal plugin file state (`[PROJECT_ROOT]/.opencode/goals/` per-session state plus evidence sidecars, the legacy `[PROJECT_ROOT]/.opencode/goal-state.json` and `[PROJECT_ROOT]/.opencode/goal-evidence.json` read fallbacks, `[PROJECT_ROOT]/STOP_GOAL`, `[PROJECT_ROOT]/.opencode/STOP_GOAL`) is runtime state only and MUST be gitignored. It is external scratch and never replaces decentralized task truth.
 
 - **Living Folder Docs Sibling Inspection**: AGENTS.md MUST instruct agents to inspect sibling README.md and DECISIONS.md before editing code in any component or vertical slice directory, and update them when domain contracts or architectural decisions change.
 
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 6fa859f..07a5914 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -388,7 +388,11 @@ def test_post_overall_deadline_fast_fail(monkeypatch):
     _stub_httpx(monkeypatch)
     monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
     monkeypatch.setattr(_time, "sleep", lambda s: None)
-    monkeypatch.setattr(bridge, "_OVERALL_DEADLINE_S", 0)
+    # The env override wins over the code default, so clear it before
+    # patching the default — otherwise an ambient .env value (900) keeps
+    # the deadline real and the turn just exhausts its retries.
+    monkeypatch.delenv("BRAIN_OVERALL_DEADLINE_S", raising=False)
+    monkeypatch.setattr(bridge, "_DEFAULT_OVERALL_DEADLINE_S", 0)
     import pytest as _pt
 
     with _pt.raises(RuntimeError, match="deadline"):
@@ -397,6 +401,21 @@ def test_post_overall_deadline_fast_fail(monkeypatch):
         )
 
 
+def test_overall_deadline_env_override(monkeypatch):
+    monkeypatch.setenv("BRAIN_OVERALL_DEADLINE_S", "1200")
+    assert bridge._overall_deadline_s() == 1200.0
+    monkeypatch.setenv("BRAIN_OVERALL_DEADLINE_S", "junk")
+    import pytest as _pt
+
+    with _pt.raises(RuntimeError, match="BRAIN_OVERALL_DEADLINE_S"):
+        bridge._overall_deadline_s()
+    monkeypatch.setenv("BRAIN_OVERALL_DEADLINE_S", "-5")
+    with _pt.raises(RuntimeError, match="BRAIN_OVERALL_DEADLINE_S"):
+        bridge._overall_deadline_s()
+    monkeypatch.delenv("BRAIN_OVERALL_DEADLINE_S")
+    assert bridge._overall_deadline_s() == bridge._DEFAULT_OVERALL_DEADLINE_S
+
+
 def test_post_retry_after_honored(monkeypatch):
     _stub_httpx(monkeypatch)
     monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
diff --git a/zen-proxy/DECISIONS.md b/zen-proxy/DECISIONS.md
new file mode 100644
index 0000000..0bbab4b
--- /dev/null
+++ b/zen-proxy/DECISIONS.md
@@ -0,0 +1,58 @@
+# Architectural Decisions: zen-proxy
+
+## [2026-10-22] ADR-001: This slice owns the proxy, not the homelab repo
+
+- **Context:** The proxy was born in the `code-server` homelab repo as an
+  Open-WebUI sidecar (Docker, then a native revival). Open-WebUI was retired
+  2026-09-19, and the only remaining consumer became this project's Brain
+  Bridge (`BRAIN_API_BASE=http://127.0.0.1:8081/go/resp`). Every behavioural
+  change since then — route allowlists, `reasoning.effort` translation,
+  per-model windows, the 900s upstream timeout, the 64-char input-id rule —
+  was driven by Brain and Hands needs, yet lived in the other repo. Two repos
+  owning one runtime contract is what let fixes go missing (the owner repo's
+  docs still described 8081 as closed while it served live traffic).
+- **Decision:** Move source, docs, and the systemd unit here. Install
+  globally next to the MCP server slices (`~/.config/opencode/zen-proxy/`),
+  build the venv with `uv`, and launch through that venv interpreter from
+  `services/zen-proxy.service`. Read configuration from the single global
+  `~/.config/opencode/.env`. `code-server` keeps only a historical pointer.
+- **Consequences:** One repo owns the proxy's behaviour and its consumer.
+  The port (8081), the four mount paths, and `BRAIN_API_BASE` are unchanged,
+  so Brain needs no reconfiguration. The proxy adds no secret of its own: it
+  passes the caller's `Authorization` header through and only reads
+  `ZEN_SESSION_ID` as a fallback.
+- **Rollback:** Restore `archive/zen-proxy-native-2026-09-27/` from
+  `code-server` git history, re-point the unit to that path, restart.
+
+## [2026-10-22] ADR-002: Upstream timeout is tunable and defaults to 900s
+
+- **Context:** Long `xhigh`/`max` reasoning turns failed with
+  `RemoteProtocolError: Server disconnected without sending a response` and
+  the bridge reported `provider overall deadline hit (500.0s)`. The proxy's
+  hard-coded `urlopen(timeout=300)` was the real limiter: any upstream call
+  whose first byte arrived after five minutes was dropped with no response,
+  the caller retried, and the retry-burn hit its own deadline. A deep
+  `gpt-6-luna` turn spends 14-19K reasoning tokens — five to ten minutes.
+- **Decision:** `ZEN_PROXY_UPSTREAM_TIMEOUT` (default 900s) replaces the
+  constant. Ordering contract recorded: proxy timeout ≤ caller overall
+  deadline ≤ MCP client execution timeout.
+- **Consequences:** Reasoning turns up to ~15 minutes complete. A genuinely
+  hung upstream surfaces later; the client timeout caps the worst case and
+  the `502 BadGatewayError` path still answers pool failures.
+- **Rollback:** Set `ZEN_PROXY_UPSTREAM_TIMEOUT=300` in the unit env — no
+  code change needed.
+
+## [2026-10-22] ADR-003: Mounts are enforced on POST as well as on /models
+
+- **Context:** The route allowlists originally filtered only `GET /models`,
+  which made them display-only: a model posted to the wrong mount reached
+  the upstream and came back as an opaque 400 about API style.
+- **Decision:** `POST` bodies are checked against the mount's allowlist
+  before dispatch. A mismatch returns `404 ModelNotServedHere` with the
+  correct mount named, or `no known route` when the id is unserved anywhere.
+- **Consequences:** Callers get an actionable error instead of a provider
+  400. The allowlist must be refreshed against upstream when it drifts;
+  `GO_RESP` was widened on 2026-10-21 after probing showed every Go chat
+  model tested also answers on `/responses`.
+- **Rollback:** Remove the POST gate; `GET /models` filtering alone remains
+  as before.
diff --git a/zen-proxy/README.md b/zen-proxy/README.md
new file mode 100644
index 0000000..94e9910
--- /dev/null
+++ b/zen-proxy/README.md
@@ -0,0 +1,57 @@
+# Slice: zen-proxy
+
+## Duties
+
+Loopback sidecar between OpenAI-compatible clients and the OpenCode Zen/Go
+gateways. It exists because those gateways are stricter than a generic
+client:
+
+1. They require an `x-opencode-session` header; the proxy mints one when the
+   caller does not supply it.
+2. Cloudflare in front of `opencode.ai` blocks bare SDK user-agents; the
+   proxy sends a browser UA unless a real `opencode/...` client is talking.
+3. Clients merge model lists across connections by id, so each mount path
+   filters `/models` to the ids that actually work on that API style.
+4. Chat-style `reasoning_effort` is rewritten into the Responses-API shape
+   `reasoning: {effort}` so `high`/`xhigh`/`max` reach the model.
+
+## Routes (loopback `127.0.0.1:8081`)
+
+| Mount | Upstream | Serves |
+| --- | --- | --- |
+| `/zen/chat` | `opencode.ai/zen/v1` | free chat models |
+| `/zen/resp` | `opencode.ai/zen/v1` | free Responses models |
+| `/go/chat` | `opencode.ai/zen/go/v1` | Go subscription, chat completions |
+| `/go/resp` | `opencode.ai/zen/go/v1` | Go subscription, Responses API |
+
+`GET /health` answers `{"status":"ok"}` and is the liveness probe.
+
+## Consumers
+
+- **Brain Bridge (primary).** `BRAIN_API_BASE=http://127.0.0.1:8081/go/resp`
+  — every `brain_turn` goes through this slice.
+- Historical: Open-WebUI, retired and archived 2026-09-19. The proxy stayed
+  because the Brain still needs the header minting, the route filters, and
+  the effort rewrite.
+
+## Files
+
+- `proxy.py` — the whole server (`BaseHTTPRequestHandler` + `ThreadingHTTPServer`, stdlib only).
+- `pyproject.toml` — no runtime dependencies; exists so the venv is built by `uv`.
+- `README.md` / `DECISIONS.md` — this slice's docs and ADRs.
+
+## Key Risks & Invariants
+
+- **Loopback only.** Never bind a public interface; the gateway credentials
+  pass through this hop.
+- **Allowlists gate both `GET /models` and `POST`.** A model posted to the
+  wrong mount gets `404 ModelNotServedHere` naming the correct route instead
+  of an opaque upstream 400.
+- **Timeout ordering.** `ZEN_PROXY_UPSTREAM_TIMEOUT` (default 900s) must sit
+  at or below the caller's own deadline (`BRAIN_OVERALL_DEADLINE_S`, also
+  900) and below the MCP client's execution timeout. A hidden 300s here is
+  what silently killed long reasoning turns before 2026-10-22.
+- **Never truncate a replayed item id** in a caller; that rule lives in the
+  bridge, but it exists because of this gateway's strict input validation.
+- Audit mode (`ZEN_PROXY_AUDIT=1`) writes prompts to local disk. Leave it off
+  outside active debugging.
diff --git a/zen-proxy/proxy.py b/zen-proxy/proxy.py
new file mode 100755
index 0000000..682b304
--- /dev/null
+++ b/zen-proxy/proxy.py
@@ -0,0 +1,383 @@
+#!/usr/bin/env python3
+"""zen-proxy: sidecar between Open WebUI and the OpenCode Zen/Go gateways.
+
+Why this exists:
+  1. The gateways reject requests without an `x-opencode-session` header
+     (Go: always; Zen free tier: always). Open WebUI cannot send it.
+  2. Cloudflare in front of opencode.ai blocks bare SDK user-agents (HTTP 1010).
+   3. Open WebUI merges model lists across connections by ID, so each mount
+      path filters `/models` to only the IDs that actually work on its API
+      style (chat/completions vs responses). Without this, picking e.g. a
+      responses-only model on a chat connection fails.
+   4. Open WebUI sends reasoning effort chat-completions style (top-level
+      `reasoning_effort`); the gateways' /responses endpoints only accept
+      the Responses-API shape (`reasoning: {effort}`) — the proxy rewrites
+      one into the other so high/xhigh actually reach the model.
+
+Routes (all mounted under port 8081, compose network only):
+  /zen/chat/* -> https://opencode.ai/zen/v1/*      (chat models, free)
+  /zen/resp/* -> https://opencode.ai/zen/v1/*      (responses models, free Muse)
+  /go/chat/*  -> https://opencode.ai/zen/go/v1/*   (Go subscription, chat)
+  /go/resp/*  -> https://opencode.ai/zen/go/v1/*   (Go subscription, Responses;
+                  verified 2026-10-21: muse 1.2/1.3-contrib, gpt-5.6/6-luna,
+                  grok-4.6/4.7, glm-5.3, kimi-k3, qwen3.8-max,
+                  mimo-v2.6-pro, deepseek-v4-pro/v4.1-flash, glm-5.3-flash)
+
+Stdlib only. SSE streaming is relayed chunk-by-chunk, never buffered.
+Auth (Authorization: Bearer <key>) passes straight through untouched.
+"""
+import json
+import os
+import uuid
+import time
+import urllib.request
+import urllib.error
+from datetime import datetime, timezone
+from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
+
+UPSTREAM = "https://opencode.ai"
+SESSION_ID = os.environ.get("ZEN_SESSION_ID", "00000000-0000-4000-8000-000000000000")
+UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
+      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
+
+# Audit mode: when "1", every proxied request appends one JSON line to
+# audit.jsonl plus full request/response capture files, so you can prove
+# exactly what effort value was sent upstream and what came back.
+# Flip via ZEN_PROXY_AUDIT in .env (needs container recreate), default off.
+# NOTE: captures contain your prompts — local disk only, disable after testing.
+AUDIT = os.environ.get("ZEN_PROXY_AUDIT", "0") == "1"
+AUDIT_DIR = os.path.expanduser("~/.local/share/zen-proxy/audit-logs")
+AUDIT_MAX_BYTES = 2 * 1024 * 1024  # per-response capture cap
+
+# Upstream socket timeout (seconds). 2026-10-22: was hard-coded 300, which
+# silently truncated long reasoning turns — a big xhigh/max turn on
+# gpt-6-luna thinks for 5-10 minutes, so the proxy dropped the socket at
+# 300s and the bridge saw "RemoteProtocolError: Server disconnected
+# without sending a response", retried, and burned its own 500s deadline.
+# Env-tunable so a slow model can be given more room without a code edit.
+UPSTREAM_TIMEOUT = float(os.environ.get("ZEN_PROXY_UPSTREAM_TIMEOUT", "900"))
+
+# Refreshed live 2026-10-14 against upstream /zen/go/v1/models (40) and
+# /zen/v1/models (47). Removed IDs gone upstream; added new ones.
+# Re-verified 2026-10-21: upstream /responses accepts far more Go models
+# than the docs imply — glm-5.3, kimi-k3, qwen3.8-max, mimo-v2.6-pro,
+# deepseek-v4-pro, deepseek-v4.1-flash, glm-5.3-flash all returned 200
+# completed on POST /zen/go/v1/responses (direct, paid key). They stay on
+# GO_CHAT too (dual-endpoint models, chat verified 2026-10-14).
+# Anthropic-/messages-only (claude-*) and single-endpoint models
+# (gemini-*) stay out — no OpenAI-compatible client can use them.
+# qwen3.6-plus / qwen3.7-max: endpoint unverified (absent from docs +
+# models.dev); placed on chat as Qwen is OpenAI-compatible by default —
+# move if a real call 400s.
+GO_CHAT = {
+    "glm-5.1", "glm-5.2", "glm-5.3", "glm-5.3-flash",
+    "kimi-k2.6", "kimi-k2.7-code", "kimi-k3",
+    "longcat-2.0", "longcat-2.5-preview-free",
+    "deepseek-v4-pro", "deepseek-v4.1-flash",
+    "mimo-v2.5", "mimo-v2.5-pro", "mimo-v2.6-flash", "mimo-v2.6-pro",
+    "minimax-m2.5", "minimax-m2.7", "minimax-m3",
+    "qwen3.6-plus", "qwen3.7-max", "qwen3.8-max",
+    "space-bunny", "step-5-preview-free", "cat-jam-free",
+    "hy3", "hy4-preview",
+    "omen-alpha",
+}
+GO_RESP = {
+    "muse-spark-1.3-contributor", "muse-spark-1.2-contributor",
+    "gpt-5.6-luna", "gpt-6-luna", "grok-4.6", "grok-4.7",
+    # Verified 2026-10-21 on POST /zen/go/v1/responses (200 completed,
+    # paid key): chat+responses dual-endpoint models.
+    "glm-5.3", "kimi-k3", "qwen3.8-max",
+    "mimo-v2.6-pro", "deepseek-v4-pro", "deepseek-v4.1-flash",
+    "glm-5.3-flash",
+}
+
+# Per-model context windows (tokens), for callers that pre-size prompts
+# (e.g. brain BRAIN_CONTEXT_WINDOW_TOKENS). Values from models.dev feed
+# 2026-10-21; default when absent below is 1048576. WARNING: grok-4.7 is
+# only 500000 — never send it a 1M-sized prompt, the server rejects it.
+MODEL_WINDOWS = {
+    "grok-4.6": 500000,
+    "grok-4.7": 500000,
+    "hy3": 256000,
+    "deepseek-v4-flash": 1000000,
+    "deepseek-v4-flash-free": 200000,
+    "deepseek-v4.1-flash-free": 200000,
+    "glm-5.3-flash-free": 200000,
+    "mimo-v2.6-flash-free": 200000,
+    "longcat-2.5-preview-free": 1000000,
+}
+ZEN_CHAT = {
+    "big-pickle", "nemotron-3.5-lightning-free",
+    "cat-jam-free", "longcat-2.5-preview-free",
+    "mimo-v2.6-flash-free", "space-bunny-free", "step-5-preview-free",
+}
+ZEN_RESP = {
+    "muse-spark-1.3-contributor-free", "muse-spark-1.2-contributor-free",
+}
+
+def _translate_reasoning_effort(payload):
+    """Rewrite chat-style top-level `reasoning_effort` (what Open WebUI
+    sends) into Responses-API style `reasoning: {effort}` (what the
+    gateways' /responses endpoints accept, incl. low/high/xhigh).
+    Returns True if the payload was changed."""
+    if not isinstance(payload, dict) or "reasoning_effort" not in payload:
+        return False
+    effort = payload.pop("reasoning_effort")
+    reasoning = payload.get("reasoning")
+    if not isinstance(reasoning, dict):
+        reasoning = {}
+        payload["reasoning"] = reasoning
+    reasoning.setdefault("effort", effort)
+    return True
+
+ROUTES = {
+    "/zen/chat": ("/zen/v1", ZEN_CHAT),
+    "/zen/resp": ("/zen/v1", ZEN_RESP),
+    "/go/chat": ("/zen/go/v1", GO_CHAT),
+    "/go/resp": ("/zen/go/v1", GO_RESP),
+}
+
+
+def _find_route(model):
+    """Return the mount prefix that serves `model`, or None."""
+    for prefix, (_, allow) in ROUTES.items():
+        if model in allow:
+            return prefix
+    return None
+
+
+def _audit_write(record, req_body=None):
+    """Append one JSONL line + optional capture files. Never breaks proxying."""
+    try:
+        os.makedirs(AUDIT_DIR, exist_ok=True)
+        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
+        if req_body is not None:
+            rpath = os.path.join(AUDIT_DIR, f"audit-{ts}-req.json")
+            with open(rpath, "wb") as f:
+                f.write(req_body)
+            record["req_capture"] = rpath
+        with open(os.path.join(AUDIT_DIR, "audit.jsonl"), "a") as f:
+            f.write(json.dumps(record) + "\n")
+        return ts
+    except OSError:
+        return None
+
+
+class Handler(BaseHTTPRequestHandler):
+    server_version = "zen-proxy/1.0"
+
+    def log_message(self, *args):
+        pass  # keep logs quiet; errors still surface via status codes
+
+    def _send_upstream(self):
+        if self.path == "/health":
+            body = b'{"status":"ok"}'
+            self.send_response(200)
+            self.send_header("Content-Type", "application/json")
+            self.send_header("Content-Length", str(len(body)))
+            self.end_headers()
+            self.wfile.write(body)
+            return
+
+        for prefix, (base, allow) in ROUTES.items():
+            if self.path == prefix or self.path.startswith(prefix + "/"):
+                rest = self.path[len(prefix):] or "/"
+                self._proxy(base + rest, allow)
+                return
+        self.send_error(404, "unknown zen-proxy route")
+
+    do_GET = _send_upstream
+    do_POST = _send_upstream
+
+    def _proxy(self, upstream_path, allow):
+        length = int(self.headers.get("Content-Length", 0) or 0)
+        body = self.rfile.read(length) if length else None
+        t0 = time.monotonic()
+        # Gate POST by the route allowlist: a model served on another
+        # mount gets a 404 naming its correct route instead of a confusing
+        # upstream 400 (endpoint/style mismatch).
+        if self.command == "POST" and body:
+            try:
+                _probe = json.loads(body)
+            except ValueError:
+                _probe = None
+            if isinstance(_probe, dict) and isinstance(_probe.get("model"), str):
+                _mid = _probe["model"]
+                if _mid not in allow:
+                    _hint = _find_route(_mid)
+                    _err = {
+                        "type": "error",
+                        "error": {
+                            "type": "ModelNotServedHere",
+                            "message": (
+                                f"zen-proxy: model '{_mid}' is not served on "
+                                f"{self.path};"
+                                + (f" use {_hint} instead."
+                                   if _hint else
+                                   " it is on no known route (check upstream list).")
+                            ),
+                        },
+                    }
+                    _errb = json.dumps(_err).encode()
+                    self.send_response(404)
+                    self.send_header("Content-Type", "application/json")
+                    self.send_header("Content-Length", str(len(_errb)))
+                    self.end_headers()
+                    self.wfile.write(_errb)
+                    return
+        record = None
+        if AUDIT and self.command == "POST":
+            record = {
+                "ts": datetime.now(timezone.utc).isoformat(),
+                "method": self.command,
+                "route": self.path,
+                "upstream": upstream_path,
+                "auth_present": bool(self.headers.get("Authorization")),
+                "model": None,
+                "stream": None,
+                "effort_in": None,   # top-level reasoning_effort as received
+                "effort_out": None,  # reasoning.effort as sent upstream
+                "translated": False,
+            }
+        if (self.command == "POST" and body
+                and upstream_path.endswith("/responses")):
+            try:
+                payload = json.loads(body)
+            except ValueError:
+                payload = None
+            if isinstance(payload, dict):
+                if record is not None:
+                    record["model"] = payload.get("model")
+                    record["stream"] = payload.get("stream")
+                    record["effort_in"] = payload.get("reasoning_effort")
+                if _translate_reasoning_effort(payload):
+                    body = json.dumps(payload).encode()
+                    if record is not None:
+                        record["translated"] = True
+                        reasoning = payload.get("reasoning") or {}
+                        record["effort_out"] = reasoning.get("effort")
+        elif record is not None and body:
+            try:
+                payload = json.loads(body)
+            except ValueError:
+                payload = None
+            if isinstance(payload, dict):
+                record["model"] = payload.get("model")
+                record["stream"] = payload.get("stream")
+                record["effort_in"] = payload.get("reasoning_effort")
+        minted_session = (
+            self.headers.get("x-opencode-session")
+            or self.headers.get("X-Session-ID")
+            or str(uuid.uuid4())  # Hermes recipe: mint fresh ID per request
+        )
+        client_ua = self.headers.get("User-Agent", "")
+        out_headers = {
+                "Authorization": self.headers.get("Authorization", ""),
+                "Content-Type": self.headers.get("Content-Type", "application/json"),
+                "Accept": self.headers.get("Accept", "*/*"),
+                # Pass through genuine client-minted identity headers when the
+                # caller is a real OpenCode client (A3 path); otherwise fall
+                # back to the configured defaults below.
+                "User-Agent": client_ua if client_ua.startswith("opencode/") else UA,
+                "x-opencode-session": minted_session,
+                "X-Session-ID": minted_session,
+        }
+        for h in ("x-opencode-client", "x-opencode-request",
+                  "x-opencode-request-id", "x-opencode-project"):
+            v = self.headers.get(h)
+            if v:
+                out_headers[h] = v
+        req = urllib.request.Request(
+            UPSTREAM + upstream_path, data=body, method=self.command,
+            headers=out_headers,
+        )
+        try:
+            upstream = urllib.request.urlopen(req, timeout=UPSTREAM_TIMEOUT)
+            status, headers, stream = upstream.status, upstream.headers, upstream
+        except urllib.error.HTTPError as e:
+            status, headers, stream = e.code, e.headers, e
+        except urllib.error.URLError as e:
+            # Pool egress failure (e.g. MITM node cert refused, fail-closed).
+            # Answer 502 instead of dropping the socket so SDK clients get a
+            # parseable error they can retry against another node.
+            err = json.dumps({"type": "error", "error": {
+                "type": "BadGatewayError",
+                "message": f"zen-proxy: upstream unreachable: {e.reason}"}}).encode()
+            self.send_response(502)
+            self.send_header("Content-Type", "application/json")
+            self.send_header("Content-Length", str(len(err)))
+            self.end_headers()
+            self.wfile.write(err)
+            return
+
+        ctype = headers.get("Content-Type", "")
+        if upstream_path.endswith("/models") and self.command == "GET":
+            raw = stream.read()
+            stream.close()
+            try:
+                data = json.loads(raw)
+            except ValueError:
+                # Upstream error page (e.g. 404 on a mistyped path, 401 on a
+                # bad key) — relay it as-is instead of dropping the
+                # connection with an empty reply that clients can't explain.
+                self.send_response(status)
+                self.send_header("Content-Type", ctype or "application/octet-stream")
+                self.send_header("Content-Length", str(len(raw)))
+                self.end_headers()
+                self.wfile.write(raw)
+                return
+            data["data"] = [m for m in data.get("data", [])
+                            if m.get("id") in allow]
+            out = json.dumps(data).encode()
+            self.send_response(status)
+            self.send_header("Content-Type", "application/json")
+            self.send_header("Content-Length", str(len(out)))
+            self.end_headers()
+            self.wfile.write(out)
+            return
+
+        self.send_response(status)
+        self.send_header("Content-Type", ctype or "application/octet-stream")
+        if "text/event-stream" not in ctype:
+            self.send_header("Connection", "close")
+        self.end_headers()
+        cap = None
+        if record is not None:
+            record["upstream_status"] = status
+            record["content_type"] = ctype
+            try:
+                os.makedirs(AUDIT_DIR, exist_ok=True)
+                ts_fname = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
+                record["resp_capture"] = os.path.join(
+                    AUDIT_DIR, f"audit-{ts_fname}-resp.sse")
+                cap = open(record["resp_capture"], "wb")
+            except OSError:
+                cap = None
+        sent = 0
+        try:
+            while True:
+                chunk = stream.read(8192)
+                if not chunk:
+                    break
+                self.wfile.write(chunk)
+                self.wfile.flush()
+                sent += len(chunk)
+                if cap is not None:
+                    if sent <= AUDIT_MAX_BYTES:
+                        cap.write(chunk)
+                    elif cap is not None:
+                        cap.write(b"\n...[truncated]\n")
+                        cap.close()
+                        cap = None
+        finally:
+            stream.close()
+            if cap is not None:
+                cap.close()
+        if record is not None:
+            record["resp_bytes"] = sent
+            record["duration_ms"] = round((time.monotonic() - t0) * 1000)
+            _audit_write(record, req_body=body)
+
+
+if __name__ == "__main__":
+    ThreadingHTTPServer(("127.0.0.1", 8081), Handler).serve_forever()
diff --git a/zen-proxy/pyproject.toml b/zen-proxy/pyproject.toml
new file mode 100644
index 0000000..652632f
--- /dev/null
+++ b/zen-proxy/pyproject.toml
@@ -0,0 +1,13 @@
+[project]
+name = "cognitive-zen-proxy"
+version = "1.0.0"
+description = "Loopback sidecar between OpenAI-compatible clients and the OpenCode Zen/Go gateways"
+requires-python = ">=3.11"
+# Intentionally empty: the proxy is stdlib-only (json, os, uuid, time,
+# urllib, http.server). The venv exists so the service launches through a
+# stable interpreter, exactly like the MCP server slices, and so `uv venv`
+# + `uv pip install` remain the single provisioning path.
+dependencies = []
+
+[tool.uv]
+package = false
```
<!-- END_GIT_DIFF -->
