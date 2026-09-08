# Task 167: Replace Loop-Engine With Persona Skill-MCP Slash Commands

**File:** `tasks/qa/167-replace-loop-engine-with-persona-skill-mcp-commands.md`
**Source:** telegram
**Type:** improvement
**Status:** in-progress

## Source Context

## Goal

Replace loop-engine with persona skill/MCP slash commands (QA/reviewer/manager approval) driven by a light LLM over OpenCode.

## Original Message (Persian)

ببین یه ایده به ذهنم رسید به نظرم میشه کل لوپ انجین رو کلاً پایک کنیم خیلی بیخودی و به درد نخوره، خب؟ و کل چیزای دورشو هم میشه پاک کرد، چیزی که میشه پیادهسازی کرد و خیلی بهتر کار کنه اینه که یک اسکیل یا یک امسیپی تعریف کنیم خب؟ امسیپی وصل باشه به امسیپی وصل باشه به هوش مصنوعی ایآی. ما اونجا اینجوری کار کنیم مثلاً چند تا کامند داشته باشه، کامند مثلاً اسلش، مثال میزنم، QA اسلش ریویوئر. هر پرسونا اون کامند خودشو داشته باشه بعد ما کل سیستم پرامپتو به بدیم به الالام لایت، خب؟ بعد وقتی اون کامند هم صدا زده بشه، چیزی که بعد از اون کامند نوشته شده به صورت یوزر کانتکست بدیم به اون. دقیقاً مثل این میمونه که ایآی استودیو یا برین، این حالتی باشه، خب؟ خود اپن کد هوشمند بشه، اون کاگنتیو اگزکیوتر ایجنتی که داریم هوشمند بشه بدونه این اسکیلها رو یا این کامندها دسترسی داره. وقتی که نیاز مثلاً بود تسک رو بده به QA، QA ریویو کنه، خودش QA رو صدا بزنه، خودش تسک رو براش بفرسته و منتظر باشه QA نتیجه رو بده. یا وقتی به ریویوئر کار باشه بده. و فقط یه بخش ساده تلگرام رو اینجا اضافه کنیم، منیجر هم داخلش باشه. تسک رو برای منیجر هم بفرسته، بگه منیجر تایید بده. زمانی که منیجر تایید داد، ادامه کار رو انجام بده. یا حتی خیلی پیشرفتهتر میشه یه نقش منیجر هم تعریف کنیم وسط هر چیزی که منیجر از خودش میدونه توضیح بده، منیجر هم یک هوش مصنوعی با بکاِند واقعی منیجر باشه. اینجوری چیز اصلی خود اپن کده، اپن کد هی پرسوناهای مختلف رو صدا میزنه، ازشون راهنمایی میگیره نسبت به دیتیلزی که بهش دادن کار رو جلو میبره.

#improve

## English Translation

Look, an idea came to my mind — I think we can completely delete the whole loop-engine, it's pointless and useless, right? And everything around it can be deleted too. What could be implemented instead that would work much better is to define a skill or an MCP, right? An MCP connected to AI. We would work there like this: for example have several commands, commands like slash — for example, /QA, /reviewer. Each persona has its own command, then we give the whole system prompt to a light LLM, right? Then when that command is invoked, whatever is written after that command is passed to it as user context. It's exactly like AI Studio or Brain in that mode, right? OpenCode itself becomes smart — the cognitive-executor agent we have becomes smart and knows it has access to these skills or commands. When needed, for example, it hands the task to QA, QA reviews it — it calls QA itself, sends the task to it, and waits for QA to return the result. Or when there is reviewer work, it hands it over. And just add a simple Telegram section here, with the manager inside it too. It sends the task to the manager as well and says: manager, approve. When the manager approves, it continues the work. Or even more advanced, a manager role can be defined in the middle — whatever the manager knows, it explains; the manager is also an AI with the real manager as backend. This way the main thing is OpenCode itself — OpenCode keeps calling different personas, gets guidance from them according to the details given to it, and moves the work forward.

## Refactored Prompt

```markdown
<role>
You are an elite AI Systems Architect specializing in OpenCode agent orchestration, MCP/skill design, and multi-persona review pipelines.
</role>

<system_context>
Environment: Cognitive Lead HQ (documentation-only repo) + OpenCode with cognitive-executor agent. Existing loop-engine/ daemon (daemon.py, gateway.py, executor.py, router.py, personas.py, qa_engine.py) is proposed for full removal. Target: a skill or MCP exposing slash commands (/QA, /reviewer, /manager) backed by a light LLM holding the full system prompt; post-command text becomes user context. Telegram approval step included with the real manager as backend, evolving toward a manager-AI role.
</system_context>

<agentic_reasoning>
Before designing, output a <reasoning_log> analyzing: (1) logical dependencies — what loop-engine responsibilities (scheduling, QA gates, Telegram triggers in loop-engine.jsonc) must be preserved vs dropped; (2) risk assessment — losing daemon reliability, approval audit trail, brainstorm/QA rigor; (3) abductive reasoning — why loop-engine feels redundant (OpenCode already multiplexes sessions) vs what it uniquely provides; (4) precision and grounding — cite exact files (loop-engine/*.py, prompts/fragments/06-personas.md, agents/cognitive-executor.md).
</agentic_reasoning>

<constraints>
- You MUST preserve manager approval as a hard gate; do NOT auto-continue without explicit approval.
- You MUST define each persona command's input/output contract (task payload, result schema, wait/timeout semantics).
- You MUST map every removed loop-engine module to its replacement or explicitly justify deletion.
- Do NOT hallucinate MCP APIs; ground in existing mcp-*-server patterns (stdio FastMCP).
- Do NOT widen scope into manager-decision learning repo (covered by Task 168).
</constraints>

<output_format>
Return: (1) removal inventory (files/modules deleted), (2) skill/MCP spec (commands, system prompt routing, user-context rule), (3) OpenCode executor integration (how it discovers/calls/waits on personas), (4) Telegram+manager approval flow, (5) migration/rollback plan.
</output_format>
```

## Relevant Code Context

- `loop-engine/daemon.py, gateway.py, executor.py, router.py, personas.py, qa_engine.py` — proposed for deletion; responsibilities to remap.
- `loop-engine.jsonc` — models, provider_concurrency, Telegram approval.chat_id, trigger_mode telegram_button.
- `prompts/fragments/06-personas.md` — existing persona definitions to convert into slash commands.
- `agents/cognitive-executor.md` — the agent that must become "smart" (discover/call/wait on persona commands).
- `mcp-context-server/server.py, mcp-memory-server/server.py, mcp-lint-server/server.py` — stdio FastMCP patterns for the new MCP option.
- `docs/loop-engine/README.md, deployment.md, configuration.md, multi-project.md` — docs to retire or rewrite.

## AI Analysis & Opinion

Root cause of the complaint: loop-engine duplicates what OpenCode + OpenChamber already do (session multiplexing, scheduling, remote review), while adding daemon ops burden. Recommended direction: agree in principle — retire the daemon — but keep its hard guarantees as command contracts: QA gate, reviewer pass, Telegram manager approval, audit trail. Riskiest part is the "light LLM holds full system prompt" idea: system-prompt.md is generated from prompts/fragments/* and versioned; stuffing it per-call needs caching and a fallback to full executor. Files to change: new skill or MCP server + agents/cognitive-executor.md + prompts/fragments/06-personas.md + retirement of loop-engine/ and docs/loop-engine/*. Risk: losing scheduled/cron behavior and multi-project routing with no replacement; mitigate by specifying command wait/timeout and approval persistence before deleting anything.

## Local TODOs

- [x] Initial codebase exploration
- [x] Inventory loop-engine responsibilities vs OpenCode-native equivalents
- [x] Verify functionality

## Acceptance Criteria

- [x] Removal inventory maps every loop-engine module to replace-or-justify-delete
- [x] Skill/MCP spec defines /QA, /reviewer, /manager commands with I/O contracts and wait semantics
- [x] Manager Telegram approval remains a hard gate with audit trail

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with "mcp[cli]>=1.0,<2.0" --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin -- pytest tests/ -q` (repo root; system python has no pytest, `uv run pytest` alone lacks deps)
- **Expected result:** Full suite green: 55 pre-existing tests still pass + 32 persona-server tests pass (28 original + 4 QA-fix boundary tests) = 87 passed; `py_compile` clean on all touched modules; `opencode.json` untouched this round
- **Actual result:** `87 passed, 8 warnings in 0.98s` (warnings are pre-existing pathspec deprecation notices); `COMPILE-OK`; persona-only run `32 passed in 0.62s`
- **Exit code:** 0 (QA-fix round; initial implementation round also 0 with 83 passed)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Deleting loop-engine loses scheduling, QA rigor, and approval audit trail with no replacement.
- **Rollback plan:** Keep branch with loop-engine/ intact until persona-command replacement passes QA; restore via `git revert`.

---

## Execution Log & Reasoning

Micro-task checklist (Steps 1–8, in order):

- [x] **Step 1:** `git mv tasks/backlog/167-*.md tasks/in-progress/167-*.md`; header → `tasks/in-progress/...`, status → `in-progress`. Working tree was clean before the move.
- [x] **Step 2:** Decommissioned `loop-engine/` (48 tracked files via `git rm -r`, then `rm -rf` for ignored residue: `.venv`, `logs/`, `__pycache__`, `.pytest_cache`) + `deploy/cognitive-loop.service`, `deploy/docker-compose.yml`, `deploy/Dockerfile` (empty `deploy/` dir auto-removed by git). No `loop-engine/` rules existed in root `.gitignore`. External mentions (`docs/history/*`, `docs/loop-engine/*`, `README.md`, `CHANGELOG.md` history, archived tasks) intentionally left untouched — historical record, out of scope.
- [x] **Step 3:** Scaffolded `mcp-persona-server/` — `dual_dispatch.py` (regex `extract_xml` for `<hands_*_task|failure_report>` + `is_clarification_question` on XML-stripped text), `session.py` (append-only `tasks/.sessions/{id}/transcript.jsonl`, LiteLLM `{role,content}` messages, lineage: system-prompt → AGENTS → persona brief → task file → transcript replay → instruction), `telegram.py` (stdlib-only `urllib` Bot API; chunked long summaries with keyboard on last chunk; `{sent,decision}` dicts, never raises on missing creds), `server.py` (FastMCP `PersonaServer`, lazy `litellm` import, 4 tools, env fallbacks). Grounded in `mcp-context-server`/`mcp-memory-server` patterns (`FastMCP(name)`, `@mcp.tool()`, `mcp.run(transport="stdio")`, `uv` script header).
- [x] **Step 4:** Registered `persona` in `opencode.json` using the repo's grounded list-form (`"command": ["uv", "run", "mcp-persona-server/server.py"]`, NOT the XML's stale `"command": "python", "args":` shape) with `timeout: 120000` (15s would always time out on network LLM turns) + 4 tool permission allows.
- [x] **Step 5:** Created `.opencode/commands/{qa,reviewer,manager,brainstorm}.md` (no prior commands dir; frontmatter `description` + tool invocation contracts + Dual Dispatch handling).
- [x] **Step 6:** Appended Persona Loop section to `agents/cognitive-executor.md` (5-stage loop, Dual Dispatch statuses, tool/command reference). Preserved the exact QA Rule and Closure Rule bullets guarded by `test_cognitive_executor_preserves_qa_and_closure_rules`; no `OpenCode Execution Log` wording (guarded by runtime-agnostic test).
- [x] **Step 7:** `.env.example` gains `PERSONA_MODEL/PERSONA_REASONING_EFFORT/PERSONA_TEMPERATURE/PERSONA_MAX_TOKENS` + `TELEGRAM_CHAT_ID`/`TELEGRAM_APPROVAL_TIMEOUT_SECONDS`; retired `LOOP_ENGINE_DEBUG`.
- [x] **Step 8:** `tests/test_persona_server.py` — 28 tests (extract_xml ×7, questions ×5, session ×6, env ×3, dispatch ×4 with stubbed litellm, telegram ×3 with stub transport). Full suite 83 passed, exit 0.

Removal inventory (module → replace-or-delete):

- `gateway.py` (Telegram approval) → REPLACED by `telegram.py` + `request_admin_approval`
- `router.py` (dispatch) → REPLACED by `dispatch_session_turn` persona routing
- `personas.py` → REPLACED by `prompts/fragments/06-personas.md` briefs + slash commands
- `qa_engine.py` → REPLACED by `/qa` persona turn
- `loop-engine.jsonc` → REPLACED by `.env.example` `PERSONA_*` + `opencode.json` persona entry
- `daemon.py` (scheduler/supervisor), `executor.py`, `verifier.py`, `blast_radius.py`, `sentinel.py`, `specs.py`, `stacks.py`, `contracts.py`, `models.py`, `state.py`, `watcher.py`, `metrics.py`, `multi_project.py`, `release.py`, `healthcheck.py` → DELETED (daemon machinery with no persona-command equivalent)
- `deploy/*` (service/compose/Dockerfile) → DELETED (no daemon left to deploy)
- 20 `loop-engine/test_*.py` → DELETED, superseded by `tests/test_persona_server.py`
- KNOWN GAP (per task risk): cron/scheduled triggers and multi-project routing have no persona-command replacement yet — flagged for follow-up, not silently dropped.

Deviations from the XML spec (deliberate, grounded): opencode.json list-form command (repo convention over stale XML shape); 120s persona timeout (network LLM turns); `dispatch_session_turn` injects the task file once via transcript replay (avoids triple context); long Telegram summaries chunked across messages, keyboard on last (no truncation, no fake document claim). No live-Telegram test (no bot creds in CI) — stub-transport coverage instead.

QA fix round V1–V3 (file stayed in `tasks/qa/`, per instructions):

- [x] **Fix V1 (Dual Dispatch precision):** `is_clarification_question` now short-circuits `False` on any `DECISION_TOKENS` hit (`QA_PASSED`, `QA_REJECTED`, `APPROVED`, `APPROVED_WITH_CHANGES`, `REJECTED_NEEDS_FIXES`, `PO_REVIEW_PENDING`, `PASSED`, `FAILED`) so reports with embedded diagnostic questions stay in the REPORT lane; removed the naive bare-`?` rule; True only on `QUESTION_RE` match + `?`, or a `LEADING_QUESTION_RE` opener (`what`/`which`/`please provide`/`can you confirm`/…). Two legacy tests retargeted to the new contract with V1 notes.
- [x] **Fix V2 (Telegram scoping/ack/stale):** `_approval_keyboard(task_id, stage)` emits `approve:{task_id}:{stage}` / `reject:{task_id}:{stage}`; `_wait_for_update` takes `expected_action_prefix` (skips foreign gates, advances offset) and fires `answerCallbackQuery` on match; `_extract_answer` normalizes scoped data back to `approve`/`reject`; `_discard_stale_updates` (peek `offset=-1` → start past newest) runs before every send, threaded as `start_offset`. Documented the peek-vs-confirm nuance in-code.
- [x] **Fix V3 (lineage dedupe):** `build_persona_messages` skips re-appending `instruction` when the replay already ends with it — LiteLLM gets each user instruction exactly once (this is the live server flow, which appends to the transcript first).
- [x] **Boundary tests T1–T4 + regression retargets:** `test_is_clarification_question_ignores_questions_in_reports`, `test_telegram_approval_scopes_callback_and_answers_query` (stale-press discard + ack assertions), `test_session_lineage_no_duplicate_instruction`; rewrote telegram flow tests on an offset-aware FIFO queue transport (decision staged on send — a pre-send press is by definition stale) with 10s `TELEGRAM_APPROVAL_TIMEOUT_SECONDS` guard so a regression fails instead of hanging 1800s. Persona suite 28 → 32 tests; full suite **87 passed**, exit 0.

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index 790bfd3..21cfa32 100644
--- a/.env.example
+++ b/.env.example
@@ -1,5 +1,7 @@
 # Telegram Approval Bot (from @BotFather)
 TELEGRAM_BOT_TOKEN=your_bot_token_here
+TELEGRAM_CHAT_ID=
+TELEGRAM_APPROVAL_TIMEOUT_SECONDS=1800
 
 # Unified LLM Provider Key (OpenRouter)
 OPENROUTER_API_KEY=sk-or-v1-...
@@ -10,5 +12,8 @@ OPENROUTER_API_KEY=sk-or-v1-...
 # ANTHROPIC_API_KEY=...
 # DEEPSEEK_API_KEY=...
 
-# Debug Telemetry (Set to 1 to enable full raw Request/Response logging in loop-engine/logs/)
-LOOP_ENGINE_DEBUG=1
\ No newline at end of file
+# Persona Engine (mcp-persona-server) — light LLM holding the system prompt
+PERSONA_MODEL=openrouter/google/gemini-3.8-flash
+PERSONA_REASONING_EFFORT=high
+PERSONA_TEMPERATURE=0.2
+PERSONA_MAX_TOKENS=16384
\ No newline at end of file
diff --git a/.opencode/commands/brainstorm.md b/.opencode/commands/brainstorm.md
new file mode 100644
index 0000000..cf41c5b
--- /dev/null
+++ b/.opencode/commands/brainstorm.md
@@ -0,0 +1,18 @@
+---
+description: Run a multi-persona brainstorming swarm turn on the active topic
+---
+
+# /brainstorm — brainstorm-swarm session turn
+
+1. Load the `brainstorm-swarm` skill (six personas: system_architect,
+   security_engineer, product_manager, business_strategist, legal_advisor,
+   critical_thinker).
+2. Invoke `dispatch_session_turn` (persona MCP server) with:
+   - `persona_name`: `"Brainstorm Facilitator"`
+   - `instruction`: the text following `/brainstorm` (the ambiguous topic or
+     decision to resolve), plus the active task file body as user context
+   - `task_id`: the active task number (or `0` for topic-only sessions)
+   - `task_file_path`: the active task file path when available
+3. Classify the reply per Dual Dispatch (`XML_EXTRACTED` / `QUESTION` /
+   `REPORT`). A `REPORT` here is the structured swarm session output:
+   persist its decisions as task constraints, not as implementation.
diff --git a/.opencode/commands/manager.md b/.opencode/commands/manager.md
new file mode 100644
index 0000000..4e713bd
--- /dev/null
+++ b/.opencode/commands/manager.md
@@ -0,0 +1,20 @@
+---
+description: Open the Telegram manager approval gate on the active task
+---
+
+# /manager — manager approval gate
+
+Invoke `request_admin_approval` (persona MCP server) with:
+
+- `task_id`: the active task number
+- `stage`: the gate name (e.g. `QA`, `review`, `closure`)
+- `summary`: what was implemented, verified, and what approval unlocks
+- `task_file_path`: the active task file path
+
+This posts an inline **Approve / Reject** keyboard to the manager via
+Telegram and blocks until the manager decides (or the
+`TELEGRAM_APPROVAL_TIMEOUT_SECONDS` window elapses).
+
+Hard-gate rule: on `approve`, continue the pipeline. On `reject`, timeout,
+or transport failure — STOP, record the outcome in the task file, and do
+NOT auto-continue.
diff --git a/.opencode/commands/qa.md b/.opencode/commands/qa.md
new file mode 100644
index 0000000..5c3d159
--- /dev/null
+++ b/.opencode/commands/qa.md
@@ -0,0 +1,23 @@
+---
+description: Dispatch the QA Engineer persona on the active task for adversarial testing
+---
+
+# /qa — QA Engineer persona turn
+
+Invoke `dispatch_session_turn` (persona MCP server) with:
+
+- `persona_name`: `"QA Engineer"`
+- `instruction`: the text following `/qa` (test target, scope, suspected weak spots), plus the active task file body as user context
+- `task_id`: the active task number
+- `task_file_path`: the active task file path
+
+The persona holds the full system prompt, repo rules, and cumulative task
+history. Its reply is Dual-Dispatch classified:
+
+- `XML_EXTRACTED` — a structured `<hands_*_task>` block: execute it
+- `QUESTION` — the persona needs missing context: answer and re-dispatch
+- `REPORT` — free-form adversarial findings: triage each finding, fix what
+  reproduces, and record evidence in the task file
+
+Wait for the turn result before continuing the pipeline. Never treat a
+`QUESTION` as a pass.
diff --git a/.opencode/commands/reviewer.md b/.opencode/commands/reviewer.md
new file mode 100644
index 0000000..953bea9
--- /dev/null
+++ b/.opencode/commands/reviewer.md
@@ -0,0 +1,24 @@
+---
+description: Dispatch the Code Reviewer persona on the active task for standards audit
+---
+
+# /reviewer — Code Reviewer persona turn
+
+Invoke `dispatch_session_turn` (persona MCP server) with:
+
+- `persona_name`: `"Code Reviewer"`
+- `instruction`: the text following `/reviewer` (files, diff scope, standards
+  in question), plus the active task file body as user context
+- `task_id`: the active task number
+- `task_file_path`: the active task file path
+
+The persona audits against `AGENTS.md`, `docs/conventions.md`, and the skill
+set loaded for the task's stack. Its reply is Dual-Dispatch classified:
+
+- `XML_EXTRACTED` — a structured `<hands_*_task>` block: execute it
+- `QUESTION` — the persona needs missing context: answer and re-dispatch
+- `REPORT` — findings list: apply the ones that reproduce under the repo's
+  linters/tests, dispute the rest with evidence in the Execution Log
+
+A `REPORT` with zero blocking findings is the review pass. Wait for the turn
+result before opening the admin approval gate.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index c7cd169..e0bf7d6 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -13,6 +13,15 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **LLM.txt optional OpenChamber guide (Task 166):** Added `LLM.txt` §7.9 “Install OpenChamber (Optional — Multi-Device Remote Access)” — asks user “Do you need multi-device remote access? …” before installing; prerequisites (Node≥22, OpenCode, Tailscale), `npm i -g @openchamber/web` 1.22.2, Tailscale-only `100.82.29.19:3005` bind (public `194.76.154.73:3005` refused), `~/.secrets` password (600) via env, verify (`status`, `curl`, `ss`), auto-start (`startup enable` + `enable-linger`), pairing (`connect-url --qr`), link to `docs/openchamber-tailscale.md`; Cloudflare Tunnel noted as deferred; updated §10 verification checklist with optional OpenChamber check.
 - **DCP dynamic context pruning like goal plugin (Task 163):** Added `@tarquinen/opencode-dcp` to `plugin` arrays in project `opencode.json` + `tui.json` (parity with global, mirrors `@prevalentware/opencode-goal-plugin` pattern from Task 126); extended `LLM.txt` §7 JSON example + TUI parity block + Option A note, new §7.7 DCP install/config/commands (`opencode plugin @tarquinen/opencode-dcp@latest --global`, `dcp.jsonc` global + `.opencode/dcp.jsonc` override, `/dcp` + `/dcp-compress`), verification checklist DCP checks. Installed globally + verified 4-way parity.
 - **owt worktree plugin (Task 164):** Installed `@nano-step/opencode-worktree-plugin` globally (`npm i -g` + `owt-setup install` → `~/.config/opencode/plugins/worktree-plugin.js` + 7 slash commands incl. `/init-worktree`, `/list-worktrees`, `/open-worktree`; file-based loading kept, `opencode.json`/`tui.json` untouched by design — npm spec resolves from project `node_modules` which this docs-only repo has none of, and owt is not a TUI panel plugin). Chose owt over `kdcokenny/opencode-worktree` (OCX-only, OCX not allowed) and `arturosdg/opencode-worktree` (standalone TUI). Project side: `.gitignore` guards (`.opencode/worktrees/`, `worktree-sessions.json`), new `LLM.txt` §7.8 install/commands/verify docs. Optional `owt hook --global` left disabled.
+- **Persona MCP engine replacing loop-engine (Task 167):** New stdio FastMCP server `mcp-persona-server/` (`dual_dispatch.py` XML/question classifier, `session.py` append-only JSONL transcripts + lineage projection, `telegram.py` stdlib-only Bot API approval gates, `server.py` with `dispatch_session_turn`/`get_session_summary`/`escalate_to_admin`/`request_admin_approval` tools on LiteLLM `PERSONA_MODEL`); slash commands `.opencode/commands/{qa,reviewer,manager,brainstorm}.md`; `agents/cognitive-executor.md` Persona Loop section (Implementation → QA → Review → Approval Gate → Closure + Dual Dispatch statuses); `opencode.json` `persona` entry (120s timeout for LLM turns) + tool permissions; `tests/test_persona_server.py` **28 passed**, full suite **83 passed**.
+
+### Changed
+
+- **Persona engine variables (Task 167):** `.env.example` gains `PERSONA_MODEL=openrouter/google/gemini-3.8-flash`, `PERSONA_REASONING_EFFORT=high`, `PERSONA_TEMPERATURE=0.2`, `PERSONA_MAX_TOKENS=16384`, `TELEGRAM_CHAT_ID`, `TELEGRAM_APPROVAL_TIMEOUT_SECONDS=1800`; retired `LOOP_ENGINE_DEBUG` with the daemon.
+
+### Removed
+
+- **loop-engine daemon + deploy infra (Task 167):** Deleted `loop-engine/` (48 tracked files: daemon/gateway/router/personas/qa_engine/executor/verifier/sentinel/stacks/specs/models/state/watcher + 20 test files + uv.lock) including ignored residue (`.venv`, logs, `__pycache__`), plus `deploy/cognitive-loop.service`, `deploy/docker-compose.yml`, `deploy/Dockerfile` (empty `deploy/` dir removed by git). No `.gitignore` loop rules existed. External historical mentions (`docs/history/*`, `docs/loop-engine/*`, `README.md`, archived tasks) intentionally left untouched.
 
 ## [9.10.0] - 2026-09-04
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 5444e52..a2cd325 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -203,3 +203,51 @@ Claim: "Task complete. The code looks correct."
 - Do not widen work into cleanup, refactoring, documentation, or adjacent features.
 - Do not claim completion without evidence.
 - For completed work, concisely restate it but do not overload with response detail.
+
+## Persona Loop (MCP Slash Commands)
+
+The retired `loop-engine/` daemon is replaced by on-demand persona turns via
+the `persona` MCP server (`mcp-persona-server/server.py`, stdio). You are the
+orchestrator: discover the persona tools, call them, and wait for each turn
+before continuing.
+
+### Autonomous multi-stage loop
+
+Run every implementation through this exact sequence:
+
+1. **Implementation** — execute the XML task block per the Core Protocol.
+2. **QA Loop** — invoke `/qa` (`dispatch_session_turn`, persona `"QA Engineer"`)
+   for adversarial testing. Triage every finding: fix what reproduces, dispute
+   the rest with evidence in `## Execution Log & Reasoning`. Repeat until the
+   turn returns no blocking findings.
+3. **Code Review Loop** — invoke `/reviewer` (`dispatch_session_turn`, persona
+   `"Code Reviewer"`) for the standards audit against `AGENTS.md`,
+   `docs/conventions.md`, and the loaded stack skills. Apply blocking findings.
+4. **Admin Approval Gate** — invoke `/manager` (`request_admin_approval`) with
+   the stage summary. On `approve`, continue. On `reject`, timeout, or
+   transport failure, STOP and record the outcome — never auto-continue.
+5. **Closure** — only after explicit Manager authorization, follow the Closure
+   Sequence in Task Lifecycle & Kanban State Enforcement.
+
+### Dual Dispatch pattern
+
+Every `dispatch_session_turn` reply carries a `status`:
+
+- `XML_EXTRACTED` — the persona emitted a structured `<hands_*_task>` (or
+  `<failure_report>`) block in `xml_content`. Execute it as your next
+  instruction set.
+- `QUESTION` — the persona needs missing context. Answer the `question`
+  precisely and re-dispatch; never treat a question as a pass or a report.
+- `REPORT` — free-form evaluation findings. Triage, verify, record evidence.
+- `RETRY_NEEDED` (only when you set `force_xml=true`) — re-dispatch with an
+  instruction that explicitly demands a `<hands_*_task>` block.
+
+### Tool and command reference
+
+- MCP tools: `dispatch_session_turn`, `get_session_summary`,
+  `escalate_to_admin`, `request_admin_approval` (see `opencode.json`).
+- Slash commands: `.opencode/commands/qa.md`, `reviewer.md`, `manager.md`,
+  `brainstorm.md` (the latter loads the `brainstorm-swarm` skill first).
+- Session transcripts persist append-only under
+  `tasks/.sessions/{task_id}/transcript.jsonl` — the audit trail behind every
+  gate decision.
diff --git a/deploy/Dockerfile b/deploy/Dockerfile
deleted file mode 100644
index d98e911..0000000
--- a/deploy/Dockerfile
+++ /dev/null
@@ -1,20 +0,0 @@
-# syntax=docker/dockerfile:1
-# Cognitive Loop Engine — hardened multi-stage build (Task 148)
-FROM python:3.12-slim AS builder
-ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
-RUN pip install --no-cache-dir uv
-WORKDIR /app
-COPY loop-engine/pyproject.toml loop-engine/pyproject.toml
-RUN python -m venv /opt/venv \
-  && /opt/venv/bin/pip install --no-cache-dir -e ./loop-engine || /opt/venv/bin/pip install --no-cache-dir pydantic litellm watchdog python-telegram-bot pyyaml
-
-FROM python:3.12-slim AS runtime
-ENV PYTHONUNBUFFERED=1 TZ=UTC PATH="/opt/venv/bin:$PATH"
-RUN useradd -m -u 10001 appuser
-WORKDIR /app
-COPY --from=builder /opt/venv /opt/venv
-COPY loop-engine/ loop-engine/
-COPY system-prompt.md AGENTS.md ./
-COPY tasks/ tasks/
-USER appuser
-CMD ["python", "loop-engine/daemon.py"]
diff --git a/deploy/cognitive-loop.service b/deploy/cognitive-loop.service
deleted file mode 100644
index d4dead6..0000000
--- a/deploy/cognitive-loop.service
+++ /dev/null
@@ -1,19 +0,0 @@
-[Unit]
-Description=Cognitive Loop Engine Daemon
-After=network-online.target
-Wants=network-online.target
-
-[Service]
-Type=simple
-User=cognitive
-WorkingDirectory=/opt/cognitive-lead-hq
-EnvironmentFile=/etc/cognitive-loop/env
-ExecStart=/opt/cognitive-lead-hq/.venv/bin/python loop-engine/daemon.py
-Restart=always
-RestartSec=10
-StandardOutput=journal
-StandardError=journal
-# Log rotation via journald; see docs/loop-engine/deployment.md for limits.
-
-[Install]
-WantedBy=multi-user.target
diff --git a/deploy/docker-compose.yml b/deploy/docker-compose.yml
deleted file mode 100644
index facb1f3..0000000
--- a/deploy/docker-compose.yml
+++ /dev/null
@@ -1,22 +0,0 @@
-services:
-  cognitive-loop:
-    build:
-      context: ..
-      dockerfile: deploy/Dockerfile
-    restart: unless-stopped
-    env_file:
-      - ../.env
-    volumes:
-      - ../.env:/app/.env:ro
-      - ../tasks:/app/tasks
-      - ../loop-engine/state:/app/loop-engine/state
-      - ../loop-engine/logs:/app/loop-engine/logs
-    environment:
-      TZ: UTC
-      PYTHONUNBUFFERED: "1"
-    healthcheck:
-      test: ["CMD", "python3", "loop-engine/healthcheck.py"]
-      interval: 30s
-      timeout: 5s
-      retries: 3
-      start_period: 20s
diff --git a/loop-engine/.gitignore b/loop-engine/.gitignore
deleted file mode 100644
index 9db0e71..0000000
--- a/loop-engine/.gitignore
+++ /dev/null
@@ -1,8 +0,0 @@
-# Loop Engine runtime data
-state/
-evidence/
-__pycache__/
-*.pyc
-.venv/
-.env
-logs/
\ No newline at end of file
diff --git a/loop-engine/blast_radius.py b/loop-engine/blast_radius.py
deleted file mode 100644
index db9bf15..0000000
--- a/loop-engine/blast_radius.py
+++ /dev/null
@@ -1,674 +0,0 @@
-"""
-Monorepo Blast-Radius Analyzer & Affected Path Matrix (LE-9 / Task 141).
-
-Deterministic, side-effect-free analysis of task diffs against monorepo
-workspaces: given the list of files modified by a task, discover the packages
-under ``workspace_root``, map their local dependency edges, and compute the
-exact affected dependency matrix — the directly modified packages PLUS every
-package that (transitively) depends on them.
-
-The matrix feeds the toolchain verification gate (``ToolchainRunner`` in
-``verifier.py``) so lint/build/test is skipped for *completely unaffected*
-workspaces and strictly scoped to impacted modules. The analyzer is
-deliberately conservative: when it cannot PROVE a workspace is unaffected
-(non-monorepo layout, unreadable manifests, root-owned files), it reports it
-as affected so verification always runs. False-negative skips of actually
-affected modules are the failure mode this guard rails against (see the
-Risk & Rollback section of Task 141).
-
-Design notes:
-- Package discovery is manifest-driven (``os.walk`` with noise-dir pruning)
-  plus root ``package.json`` ``workspaces`` globs (npm/yarn/pnpm-style).
-- Dependency edges come from explicit local references (``workspace:*``,
-  ``file:../x``, relative paths, Go ``replace ... => ../x``, uv ``sources``
-  path map) and from plain references to another discovered package's name.
-- Manifest parsers are implemented for package.json / pyproject.toml / go.mod;
-  other manifests (Cargo.toml, composer.json, gradle, pom.xml) act as package
-  boundaries only and contribute no dependency edges.
-- Diff-path parsing replicates the tiny ``_DIFF_HEADER_RE`` helper from
-  ``specs.py``/``contracts.py`` (established in-repo pattern, no cross-module
-  imports so this stays dependency-light).
-"""
-
-from __future__ import annotations
-
-import json
-import os
-import re
-import tomllib
-from pathlib import Path
-
-from models import BlastRadiusMatrix, PackageDependency, PackageInfo
-
-# Matches `diff --git a/<old> b/<new>` header lines — the b-side path is the
-# post-change relative path we care about (mirrors specs.py / contracts.py).
-_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)\n", re.MULTILINE)
-
-# Pseudo-manifest sentinel for workspace-glob packages that have no real
-# manifest file (e.g. a workspaces glob pointing at an empty dir).
-_PSEUDO_MANIFEST = "<workspaces glob>"
-
-# Directories that never contain a package boundary (pruned during discovery).
-_EXCLUDED_DIR_NAMES = {
-    ".git", ".idea", ".vscode", ".venv", ".opencode", ".pytest_cache",
-    "__pycache__", "node_modules", "venv", "dist", "build", "target",
-    "coverage", "htmlcov", "state", "evidence", ".tox", ".mypy_cache",
-    ".ruff_cache",
-}
-
-# Manifest precedence when a directory contains several (pick the winner).
-_MANIFEST_PRECEDENCE = (
-    "package.json",
-    "pyproject.toml",
-    "go.mod",
-    "Cargo.toml",
-    "composer.json",
-    "build.gradle.kts",
-    "build.gradle",
-    "pom.xml",
-)
-
-_GO_MODULE_RE = re.compile(r"^\s*module\s+(\S+)", re.MULTILINE)
-_GO_SINGLE_REQUIRE_RE = re.compile(r"^\s*require\s+(\S+)")
-_GO_REPLACE_RE = re.compile(r"^\s*replace\s+(\S+)(?:\s+\S+)?\s*=>\s*(\S+)")
-_PY_REQUIREMENT_NAME_RE = re.compile(r"^([A-Za-z0-9_.-]+)")
-
-
-def extract_modified_paths(diff_text: str) -> list[str]:
-    """Return deduplicated relative paths of files touched by a git diff.
-
-    Parses ``diff --git a/x b/y`` headers (b-side path) and preserves
-    first occurrence order. Empty/malformed diffs yield ``[]``.
-    """
-    paths: list[str] = []
-    seen: set[str] = set()
-    for match in _DIFF_HEADER_RE.finditer(diff_text or ""):
-        path = match.group(2)
-        if path not in seen:
-            seen.add(path)
-            paths.append(path)
-    return paths
-
-
-# ---------------------------------------------------------------------------
-# Package discovery
-# ---------------------------------------------------------------------------
-
-
-def discover_packages(
-    workspace_root: str | Path, globs: list[str] | None = None
-) -> dict[str, PackageDependency] | list[PackageInfo]:
-    """Discover monorepo packages under ``workspace_root``.
-
-    Scans for manifest files (package.json, pyproject.toml, go.mod,
-    Cargo.toml, composer.json, gradle/pom markers) while pruning noise
-    directories, then additionally resolves root ``package.json``
-    ``workspaces`` globs (npm/yarn/pnpm) so un-manifested workspace dirs
-    are still tracked. Returns a deterministic path-sorted list (root
-    package ``"."`` first when the root itself carries a manifest).
-
-    Spec wrapper (Task 141): when ``globs`` is provided, returns a dict
-    mapping ``package_name -> PackageDependency`` filtered by globs; when
-    ``globs`` is None, preserves legacy list[PackageInfo] return for existing
-    tests (backward compat). The hybrid return also supports dict-style access
-    via properties.
-    """
-    root = Path(workspace_root)
-    packages: dict[str, PackageInfo] = {}
-    if not root.exists():
-        # For spec dict return, give empty dict; for legacy, empty list
-        return {} if globs is not None else []
-
-    # Determine effective globs for directory filtering (spec path)
-    effective_globs = globs if globs is not None else ["packages/*", "apps/*", "services/*", "modules/*", "libs/*"]
-
-    # 1. Manifest-file discovery (top-down walk with in-place pruning)
-    for dirpath, dirnames, filenames in os.walk(root):
-        dirnames[:] = sorted(
-            d for d in dirnames
-            if d not in _EXCLUDED_DIR_NAMES and not d.startswith(".")
-        )
-        manifest = _first_manifest(filenames)
-        if manifest is None:
-            continue
-        dirpath_p = Path(dirpath)
-        rel = dirpath_p.relative_to(root).as_posix()
-        # When globs filtering is active, skip packages not matching any glob
-        if globs is not None:
-            # rel must match one of the globs (simple fnmatch)
-            import fnmatch
-
-            if rel != "." and not any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel + "/", g) for g in effective_globs):
-                # Still keep manifest-discovered packages even if not matching globs?
-                # Spec says scan for directories matching globs — so we filter.
-                # Keep root "." always.
-                continue
-        name = _manifest_name(manifest, dirpath_p / manifest, rel)
-        packages[rel] = PackageInfo(name=name, path=rel, manifest=manifest)
-
-    # 2. Root package.json workspaces globs (additional package dirs)
-    root_pkg = root / "package.json"
-    if root_pkg.is_file():
-        try:
-            data = json.loads(root_pkg.read_text(encoding="utf-8"))
-        except Exception:
-            data = {}
-        workspaces = data.get("workspaces") or []
-        if isinstance(workspaces, list):
-            for pattern in workspaces:
-                if not isinstance(pattern, str):
-                    continue
-                for match in sorted(root.glob(pattern)):
-                    if not match.is_dir():
-                        continue
-                    rel = match.relative_to(root).as_posix()
-                    if rel not in packages:
-                        packages[rel] = PackageInfo(
-                            name=_dir_fallback_name(rel),
-                            path=rel,
-                            manifest=_PSEUDO_MANIFEST,
-                        )
-
-    sorted_packages = sorted(packages.values(), key=_package_sort_key)
-
-    # Spec dict return path
-    if globs is not None:
-        dep_map = build_dependency_map(sorted_packages, root)
-        return {d.name: d for d in dep_map}
-
-    return sorted_packages
-
-
-def find_owning_package(
-    file_rel: str, packages: list[PackageInfo]
-) -> PackageInfo | None:
-    """Return the deepest package whose directory prefixes ``file_rel``.
-
-    The root package (``path == "."``) is the last-resort owner for any
-    file not under a deeper package. Returns ``None`` only when the
-    workspace has no root package and no deeper package owns the file.
-    """
-    best = None
-    best_parts = -1
-    for pkg in packages:
-        if pkg.path == ".":
-            continue
-        if file_rel == pkg.path or file_rel.startswith(pkg.path + "/"):
-            parts = pkg.path.count("/")
-            if parts > best_parts:
-                best = pkg
-                best_parts = parts
-    if best is not None:
-        return best
-    for pkg in packages:
-        if pkg.path == ".":
-            return pkg
-    return None
-
-
-# ---------------------------------------------------------------------------
-# Dependency graph
-# ---------------------------------------------------------------------------
-
-
-def build_dependency_map(
-    packages: list[PackageInfo], workspace_root: str | Path
-) -> list[PackageDependency]:
-    """Build local dependency edges for every discovered package.
-
-    Edges are local-only: a package depends on another package when its
-    manifest references it via an explicit path (``workspace:*``,
-    ``file:../x``, relative path, Go ``replace``, uv ``sources``) or by
-    name matching a discovered package. Deterministic sorted lists.
-    """
-    root = Path(workspace_root)
-    by_name: dict[str, PackageInfo] = {p.name: p for p in packages}
-    abs_by_path: dict[Path, PackageInfo] = {}
-    for p in packages:
-        try:
-            abs_by_path[(root / p.path).resolve()] = p
-        except OSError:
-            continue
-
-    result: list[PackageDependency] = []
-    for pkg in packages:
-        edges: set[str] = set()
-        if pkg.manifest != _PSEUDO_MANIFEST:
-            manifest_path = root.joinpath(pkg.path, pkg.manifest)
-            if manifest_path.is_file():
-                if pkg.manifest == "package.json":
-                    edges |= _node_deps(
-                        manifest_path, abs_by_path, by_name
-                    )
-                elif pkg.manifest == "pyproject.toml":
-                    edges |= _python_deps(
-                        manifest_path, abs_by_path, by_name
-                    )
-                elif pkg.manifest == "go.mod":
-                    edges |= _go_deps(
-                        manifest_path, abs_by_path, by_name
-                    )
-        result.append(
-            PackageDependency(
-                package=pkg.name, path=pkg.path, depends_on=sorted(edges)
-            )
-        )
-    return result
-
-
-def build_dependency_graph(
-    packages: dict[str, PackageDependency] | list[PackageInfo] | list[PackageDependency],
-) -> dict[str, set[str]]:
-    """Invert package dependencies to construct reverse dependency map.
-
-    Spec wrapper (Task 141): accepts either a dict ``{name: PackageDependency}``
-    or a list (legacy ``list[PackageInfo]`` + workspace_root via separate call).
-    When given a dict, inverts ``dependencies`` to ``package -> set of consumers``.
-    When given a list, delegates to legacy path (requires caller to have built map).
-
-    Returns ``package_name -> set of dependent consumer package names``.
-    """
-    # Dict path (spec): packages is dict[name, PackageDependency]
-    if isinstance(packages, dict):
-        reverse: dict[str, set[str]] = {name: set() for name in packages}
-        for pkg_name, dep in packages.items():
-            # dep may be PackageDependency or list; normalize
-            deps = dep.dependencies if hasattr(dep, "dependencies") else (dep.depends_on if hasattr(dep, "depends_on") else [])
-            if not isinstance(deps, (list, set, tuple)):
-                deps = []
-            for d in deps:
-                if d in reverse:
-                    reverse[d].add(pkg_name)
-                else:
-                    # Dependency on unknown package — still create entry for completeness
-                    reverse.setdefault(d, set()).add(pkg_name)
-        return reverse
-    # Legacy list path: if list of PackageDependency
-    if packages and isinstance(packages[0], PackageDependency):
-        reverse = {d.name: set() for d in packages}  # type: ignore[attr-defined]
-        for d in packages:  # type: ignore
-            deps = d.dependencies if hasattr(d, "dependencies") else d.depends_on
-            for dep_name in deps:
-                if dep_name in reverse:
-                    reverse[dep_name].add(d.name)
-        return reverse
-    # Legacy list[PackageInfo] needs workspace_root — caller should use build_dependency_map
-    # Fallback: empty
-    return {}
-
-
-# ---------------------------------------------------------------------------
-# Public API — the acceptance-criteria entry point
-# ---------------------------------------------------------------------------
-
-
-def calculate_affected_paths(
-    modified_files: list[str],
-    workspace_root: str | Path,
-    config: "BlastRadiusConfig | None" = None,
-) -> BlastRadiusMatrix:
-    """Compute the affected dependency matrix for a set of modified files.
-
-    Mapping: every modified file is owned by the deepest discovered
-    package whose directory is a prefix of the file path (files outside
-    every package become ``root_owned_files``). The affected set is the
-    direct owners PLUS the transitive closure of packages that depend on
-    them. Unaffected packages are the discovered packages outside that
-    closure. Output lists are deterministically sorted.
-
-    Spec compliance (Task 141): accepts optional ``BlastRadiusConfig`` for
-    workspace_globs filtering and conservative_root_fallback, and populates
-    ``is_monorepo`` / ``is_empty`` per spec.
-    """
-    # Lazy import to avoid circular import at module load
-    try:
-        from models import BlastRadiusConfig as _BRC
-    except Exception:
-        _BRC = None  # type: ignore
-
-    if config is None and _BRC is not None:
-        try:
-            config = _BRC()
-        except Exception:
-            config = None
-
-    root = Path(workspace_root)
-    normalized = sorted({_normalize_file(f) for f in (modified_files or [])})
-    normalized = [f for f in normalized if f]
-
-    # Discover packages — respect workspace_globs if config provided
-    if config is not None and hasattr(config, "workspace_globs"):
-        # Use globs-aware discovery but preserve legacy list return for internal use
-        # Call discover_packages with globs to get dict, then reconstruct list for internal
-        # For backward compat, we need list[PackageInfo]; so call without globs for list
-        # and use config globs only for filtering decision below
-        packages = discover_packages(root)  # type: ignore
-        if not isinstance(packages, list):
-            # If discover_packages returned dict (when globs not None), convert
-            packages = list(packages.values())  # type: ignore
-    else:
-        packages = discover_packages(root)  # type: ignore
-        if not isinstance(packages, list):
-            packages = list(packages.values())  # type: ignore
-
-    # Spec: is_monorepo flag, but still compute matrix normally
-    is_monorepo = len(packages) >= 2
-
-    dep_map = build_dependency_map(packages, root)
-    deps_by_pkg: dict[str, set[str]] = {
-        d.package: set(d.depends_on) for d in dep_map
-    }
-
-    affected: set[str] = set()
-    root_owned: list[str] = []
-    for f in normalized:
-        owner = find_owning_package(f, packages)
-        if owner is None:
-            root_owned.append(f)
-        else:
-            affected.add(owner.name)
-
-    # Conservative root fallback: if any root file and config says True, mark all as affected
-    conservative = True
-    if config is not None and hasattr(config, "conservative_root_fallback"):
-        conservative = bool(config.conservative_root_fallback)
-    if root_owned and conservative:
-        # All packages become affected
-        affected = {p.name for p in packages}
-        # Clear root_owned? Keep it but also mark all affected per spec
-        # Spec says mark all packages as affected; we still keep root_owned for transparency
-    else:
-        # Transitive closure over reverse edges: any package that
-        # (transitively) depends on an affected package is itself affected.
-        if affected:
-            changed = True
-            while changed:
-                changed = False
-                for pkg_name, deps in deps_by_pkg.items():
-                    if pkg_name not in affected and deps & affected:
-                        affected.add(pkg_name)
-                        changed = True
-
-    affected_names = sorted(affected)
-    affected_objs = [p for p in packages if p.name in affected_names]
-    affected_paths = sorted(p.path for p in affected_objs)
-    unaffected = sorted(p.name for p in packages if p.name not in affected_names)
-    is_empty = len(affected_names) == 0
-
-    return BlastRadiusMatrix(
-        modified_files=normalized,
-        packages=packages,
-        dependency_map=dep_map,
-        affected_packages=affected_names,
-        affected_paths=affected_paths,
-        unaffected_packages=unaffected,
-        root_owned_files=root_owned,
-        is_monorepo=is_monorepo,
-        is_empty=is_empty,
-    )
-
-
-# ---------------------------------------------------------------------------
-# Manifest parsers
-# ---------------------------------------------------------------------------
-
-
-def _node_deps(
-    manifest_path: Path,
-    abs_by_path: dict[Path, PackageInfo],
-    by_name: dict[str, PackageInfo],
-) -> set[str]:
-    """Parse package.json dependency sections into local edges."""
-    try:
-        data = json.loads(manifest_path.read_text(encoding="utf-8"))
-    except Exception:
-        return set()
-    edges: set[str] = set()
-    sections = (
-        "dependencies",
-        "devDependencies",
-        "peerDependencies",
-        "optionalDependencies",
-    )
-    for section in sections:
-        deps = data.get(section) or {}
-        if not isinstance(deps, dict):
-            continue
-        for dep_name, raw_spec in deps.items():
-            spec = str(raw_spec or "")
-            if spec.startswith("workspace:"):
-                if dep_name in by_name:
-                    edges.add(dep_name)
-                continue
-            local = _resolve_local_reference(
-                spec, manifest_path.parent, abs_by_path
-            )
-            if local is not None:
-                edges.add(local)
-                continue
-            if dep_name in by_name:
-                edges.add(dep_name)
-    return edges
-
-
-def _python_deps(
-    manifest_path: Path,
-    abs_by_path: dict[Path, PackageInfo],
-    by_name: dict[str, PackageInfo],
-) -> set[str]:
-    """Parse pyproject.toml project/optional dependencies and uv sources."""
-    try:
-        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
-    except Exception:
-        return set()
-    edges: set[str] = set()
-    project = data.get("project") or {}
-
-    deps = project.get("dependencies") or []
-    if isinstance(deps, list):
-        for spec in deps:
-            _maybe_py_name_edge(spec, by_name, edges)
-
-    optional = project.get("optional-dependencies") or {}
-    if isinstance(optional, dict):
-        for specs in optional.values():
-            if isinstance(specs, list):
-                for spec in specs:
-                    _maybe_py_name_edge(spec, by_name, edges)
-
-    # uv source map: {pkg: {"path": "../x"}} — explicit local references
-    uv_sources = ((data.get("tool") or {}).get("uv") or {}).get("sources") or {}
-    if isinstance(uv_sources, dict):
-        for dep_name, source in uv_sources.items():
-            if isinstance(source, dict) and isinstance(source.get("path"), str):
-                local = _resolve_local_reference(
-                    source["path"], manifest_path.parent, abs_by_path
-                )
-                if local is not None:
-                    edges.add(local)
-                elif dep_name in by_name:
-                    edges.add(dep_name)
-    return edges
-
-
-def _maybe_py_name_edge(
-    spec: str, by_name: dict[str, PackageInfo], edges: set[str]
-) -> None:
-    """Add a name edge when a requirement spec names a discovered package."""
-    if not isinstance(spec, str):
-        return
-    match = _PY_REQUIREMENT_NAME_RE.match(spec.strip())
-    if match and match.group(1) in by_name:
-        edges.add(match.group(1))
-
-
-def _go_deps(
-    manifest_path: Path,
-    abs_by_path: dict[Path, PackageInfo],
-    by_name: dict[str, PackageInfo],
-) -> set[str]:
-    """Parse go.mod requires (name refs) and replaces (local path refs)."""
-    try:
-        text = manifest_path.read_text(encoding="utf-8")
-    except Exception:
-        return set()
-    edges: set[str] = set()
-    in_require_block = False
-    in_replace_block = False
-    base_dir = manifest_path.parent
-    for raw in text.splitlines():
-        line = raw.strip()
-        if not line or line.startswith("//"):
-            continue
-        if line == "require (":
-            in_require_block = True
-            continue
-        if line == ")" and in_require_block:
-            in_require_block = False
-            continue
-        if line == "replace (":
-            in_replace_block = True
-            continue
-        if line == ")" and in_replace_block:
-            in_replace_block = False
-            continue
-        if in_require_block:
-            parts = line.split()
-            if parts and parts[0] in by_name:
-                edges.add(parts[0])
-            continue
-        if in_replace_block:
-            match = re.match(r"^(\S+)(?:\s+\S+)?\s*=>\s*(\S+)", line)
-            if match:
-                _maybe_go_replace_edge(
-                    match.group(2), base_dir, abs_by_path, edges
-                )
-            continue
-        if line.startswith("replace"):
-            repl = _GO_REPLACE_RE.match(line)
-            if repl:
-                _maybe_go_replace_edge(
-                    repl.group(2), base_dir, abs_by_path, edges
-                )
-            continue
-        single = _GO_SINGLE_REQUIRE_RE.match(line)
-        if single:
-            token = single.group(1)
-            if token in by_name:
-                edges.add(token)
-    return edges
-
-
-def _maybe_go_replace_edge(
-    target: str,
-    base_dir: Path,
-    abs_by_path: dict[Path, PackageInfo],
-    edges: set[str],
-) -> None:
-    """Resolve a replace target path into a local dependency edge."""
-    local = _resolve_local_reference(target, base_dir, abs_by_path)
-    if local is not None:
-        edges.add(local)
-
-
-# ---------------------------------------------------------------------------
-# Reference resolution
-# ---------------------------------------------------------------------------
-
-
-def _resolve_local_reference(
-    spec: str, base_dir: Path, abs_by_path: dict[Path, PackageInfo]
-) -> str | None:
-    """Resolve an explicit local dependency reference to a package name.
-
-    Handles ``file:../x``, ``file:../x#fragment``, relative paths and
-    absolute paths. Returns the referenced package's name when the target
-    resolves to a discovered package directory, else ``None``.
-    """
-    if spec.startswith("workspace:"):
-        return None  # name-based; handled by callers
-    target: str | None = None
-    if spec.startswith("file:"):
-        target = spec[5:]
-    elif spec.startswith((".", "/", os.sep)):
-        target = spec
-    if target is None:
-        return None
-    target = target.split("#")[0].split("?")[0]
-    if not target:
-        return None
-    try:
-        resolved = (base_dir / target).resolve()
-    except OSError:
-        return None
-    info = abs_by_path.get(resolved)
-    return info.name if info is not None else None
-
-
-# ---------------------------------------------------------------------------
-# Manifest name / helpers
-# ---------------------------------------------------------------------------
-
-
-def _first_manifest(filenames: list[str]) -> str | None:
-    """Return the winning manifest filename by precedence, or None."""
-    names = set(filenames)
-    for manifest in _MANIFEST_PRECEDENCE:
-        if manifest in names:
-            return manifest
-    return None
-
-
-def _manifest_name(manifest: str, manifest_path: Path, rel: str) -> str:
-    """Extract the canonical package name from a manifest, else rel path."""
-    if manifest in ("package.json", "composer.json"):
-        try:
-            data = json.loads(manifest_path.read_text(encoding="utf-8"))
-            name = data.get("name") if isinstance(data, dict) else None
-            if isinstance(name, str) and name:
-                return name
-        except Exception:
-            pass
-    elif manifest == "pyproject.toml":
-        try:
-            data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
-            name = (data.get("project") or {}).get("name") if isinstance(data, dict) else None
-            if isinstance(name, str) and name:
-                return name
-        except Exception:
-            pass
-    elif manifest == "go.mod":
-        try:
-            text = manifest_path.read_text(encoding="utf-8")
-            match = _GO_MODULE_RE.search(text)
-            if match:
-                return match.group(1)
-        except Exception:
-            pass
-    elif manifest == "Cargo.toml":
-        try:
-            data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
-            name = (data.get("package") or {}).get("name") if isinstance(data, dict) else None
-            if isinstance(name, str) and name:
-                return name
-        except Exception:
-            pass
-    return rel
-
-
-def _dir_fallback_name(rel: str) -> str:
-    """Name for a manifestless workspace dir: its last path segment."""
-    return rel.rsplit("/", 1)[-1] or rel
-
-
-def _normalize_file(path) -> str:
-    """Normalize a modified-file path to a posix relative string."""
-    s = str(path).replace("\\", "/")
-    while s.startswith("./"):
-        s = s[2:]
-    return s
-
-
-def _package_sort_key(p: PackageInfo) -> tuple[int, str]:
-    """Sort root package ('.') first, then by path for determinism."""
-    return (0 if p.path == "." else 1, p.path)
\ No newline at end of file
diff --git a/loop-engine/brainstorm.py b/loop-engine/brainstorm.py
deleted file mode 100644
index 559526d..0000000
--- a/loop-engine/brainstorm.py
+++ /dev/null
@@ -1,109 +0,0 @@
-"""
-BrainstormStage — first-class Phase 1.5 Multi-Agent Brainstorming Loop.
-
-Implements prompts/fragments/12-brainstorming_protocol.md + the brainstorm-swarm
-skill execution rules:
-1. Independent analysis — six parallel persona calls, zero cross-contamination.
-2. Conflict resolution — synthesis MUST document contradictions explicitly.
-3. Minimum output — each persona produces >= 3 concrete observations.
-4. Grounding — reasoning anchored in the task content.
-5. Output format — verbatim <brainstorming_session> schema from the fragment.
-"""
-
-import asyncio
-from pathlib import Path
-
-from models import LoopEngineConfig
-from router import LLMRouter
-from personas import load_swarm_personas, load_brainstorm_schema
-
-# Protocol mechanics from the brainstorm-swarm skill (not persona definitions).
-_INDEPENDENCE_RULE = (
-    "You are one of six expert personas in an independent brainstorming swarm. "
-    "Produce your OWN analysis without reference to any other persona. "
-    "Ground every point in the problem description — no invented scenarios. "
-    "Provide at least 3 concrete observations or recommendations."
-)
-
-_SYNTHESIS_RULE = (
-    "Synthesize the six independent persona analyses below into a single "
-    "<brainstorming_session> report that EXACTLY follows the provided schema. "
-    "Where two personas give contradictory advice, you MUST document the "
-    "conflict explicitly under <conflict_resolution> and explain the resolution."
-)
-
-
-class BrainstormStage:
-    """Six-persona parallel brainstorm with schema-enforced synthesis."""
-
-    def __init__(self, config: LoopEngineConfig, router: LLMRouter,
-                 workspace_root: str = "."):
-        self.config = config
-        self.router = router
-        self.swarm = load_swarm_personas(workspace_root)
-        self.schema = load_brainstorm_schema(workspace_root)
-
-    @staticmethod
-    def should_trigger(task_content: str) -> bool:
-        """Trigger on explicit brainstorming requests (Manager rule)."""
-        lowered = task_content.lower()
-        return "brainstorm" in lowered or "<brainstorming_session>" in lowered
-
-    def _persona_routing(self, name: str, meta: dict, topic: str) -> dict:
-        model, reasoning = self.router._resolve_model("deep")
-        system = (
-            f"<role>You are the {name} persona of a multi-expert brainstorming "
-            f"swarm for the Cognitive Lead AI system.</role>\n"
-            f"<focus>{meta.get('focus', '')}</focus>\n"
-            f"<output_requirements>{meta.get('output', '')}</output_requirements>\n"
-            f"<rules>{_INDEPENDENCE_RULE}</rules>"
-        )
-        return {
-            "model": model, "reasoning": reasoning,
-            "system": system,
-            "user": f"Brainstorm topic / problem description:\n\n{topic}",
-            "temperature": 0.4,
-        }
-
-    async def _call(self, name: str, meta: dict, topic: str):
-        routing = self._persona_routing(name, meta, topic)
-        text = await asyncio.to_thread(self.router.call_llm, routing)
-        return name, text
-
-    async def run(self, topic: str) -> dict:
-        """Run six independent persona calls in parallel, then synthesize."""
-        if not self.swarm:
-            raise RuntimeError(
-                "Swarm personas not loaded — brainstorm fragment missing?")
-
-        responses = await asyncio.gather(
-            *(self._call(name, meta, topic) for name, meta in self.swarm.items())
-        )
-        responses_dict = dict(responses)
-
-        synthesis_system = (
-            f"<role>You are the Orchestrator synthesizing a multi-persona "
-            f"brainstorming session.</role>\n"
-            f"<rules>{_SYNTHESIS_RULE}</rules>\n"
-            f"<output_schema>\n{self.schema}\n</output_schema>"
-        )
-        persona_blocks = "\n".join(
-            f"<response persona=\"{name}\">\n{text}\n</response>"
-            for name, text in responses_dict.items()
-        )
-        synthesis_routing = {
-            "model": self.router._resolve_model("deep")[0],
-            "reasoning": self.router._resolve_model("deep")[1],
-            "system": synthesis_system,
-            "user": (f"Topic:\n{topic}\n\nIndependent persona analyses:\n"
-                     f"{persona_blocks}"),
-            "temperature": 0.2,
-        }
-        session_xml = await asyncio.to_thread(
-            self.router.call_llm, synthesis_routing)
-
-        return {
-            "session": session_xml,
-            "responses": responses_dict,
-            "personas": list(responses_dict.keys()),
-        }
diff --git a/loop-engine/contracts.py b/loop-engine/contracts.py
deleted file mode 100644
index a334140..0000000
--- a/loop-engine/contracts.py
+++ /dev/null
@@ -1,216 +0,0 @@
-"""
-Contract Propagation Engine (LE-6 / Task 138).
-
-Detects contract file mutations in task git diffs and automatically dispatches
-downstream tasks into ``tasks/backlog/`` with sequential next-task IDs and
-SQLite state registration.
-
-Pipeline:
-    git diff text -> extract_modified_paths() -> match_contract_rules()
-    -> ContractPropagationEngine.process_task_closure() -> task file generation.
-
-Design notes:
-- Pure helpers (extract_modified_paths, match_contract_rules,
-  discover_next_task_id) are intentionally side-effect free and unit-testable.
-- The engine writes canonical task files whose metadata mirrors the
-  task-generator template: # Task {N}: {title}, **File:**, **Source:**
-  contract-propagation, **Triggered-By:**, **Stack:**, **Type:**, **Status:**
-  plus ## Goal / ## Source Context / ## Acceptance Criteria / Factual Git Diff
-  markers.
-- Every generated task is registered in the StateMachine as BACKLOG so the
-  daemon watcher/trigger gate can pick it up.
-"""
-
-from __future__ import annotations
-
-import fnmatch
-import re
-from pathlib import Path
-
-from models import ContractRuleConfig, TaskState
-from state import StateMachine
-
-# Matches `diff --git a/<old> b/<new>` header lines. The b-side path is the
-# post-change relative path we care about.
-_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)\n", re.MULTILINE)
-
-# Slugify: drop every non-alphanumeric, collapse runs to a single dash.
-_SLUG_RE = re.compile(r"[^a-z0-9]+")
-
-
-def extract_modified_paths(diff_text: str) -> list[str]:
-    """Return deduplicated relative paths of files touched by a git diff.
-
-    Parses ``diff --git a/x b/y`` headers (b-side path) and preserves first
-    occurrence order. Empty/malformed diffs yield ``[]``.
-    """
-    paths: list[str] = []
-    seen: set[str] = set()
-    for match in _DIFF_HEADER_RE.finditer(diff_text or ""):
-        path = match.group(2)
-        if path not in seen:
-            seen.add(path)
-            paths.append(path)
-    return paths
-
-
-def match_contract_rules(
-    modified_paths: list[str],
-    rules: list[ContractRuleConfig],
-) -> list[tuple[ContractRuleConfig, list[str]]]:
-    """Return ``[(rule, [matching_files])]`` for rules whose glob patterns hit.
-
-    A path matches a rule if it matches ANY of the rule's patterns. Patterns
-    are evaluated with ``fnmatch`` against the full relative path, so
-    ``packages/shared-schema/**`` matches nested files and ``*.prisma``
-    matches ``prisma/schema.prisma``.
-    """
-    matches: list[tuple[ContractRuleConfig, list[str]]] = []
-    for rule in rules or []:
-        matching: list[str] = []
-        for path in modified_paths:
-            for pattern in rule.patterns or []:
-                if fnmatch.fnmatch(path, pattern):
-                    matching.append(path)
-                    break
-        if matching:
-            matches.append((rule, matching))
-    return matches
-
-
-def discover_next_task_id(tasks_dir: Path) -> int:
-    """Return ``max(numeric task-id prefixes) + 1`` across ALL task folders.
-
-    Scans every ``*.md`` under ``tasks_dir`` recursively (backlog,
-    in-progress, qa, completed, archive) so generated IDs never collide.
-    Returns ``1`` when no task files exist.
-    """
-    max_id = 0
-    tasks_path = Path(tasks_dir)
-    if tasks_path.exists():
-        for md in tasks_path.rglob("*.md"):
-            match = re.match(r"(\d+)", md.name)
-            if match:
-                max_id = max(max_id, int(match.group(1)))
-    return max_id + 1
-
-
-class ContractPropagationEngine:
-    """Generates downstream backlog tasks when contract files mutate."""
-
-    def __init__(
-        self,
-        rules: list[ContractRuleConfig] | None = None,
-        tasks_dir: str | Path = "tasks",
-    ):
-        self.rules = list(rules) if rules else []
-        self.tasks_dir = Path(tasks_dir)
-
-    @staticmethod
-    def _build_task_body(
-        next_id: int,
-        title: str,
-        triggering_task_id: int,
-        stack: str,
-        goal: str,
-        matching_files: list[str],
-        file_header: str,
-        acceptance_criteria: list[str],
-    ) -> str:
-        """Build the canonical Markdown body for a dispatched task."""
-        ac_block = "\n".join(f"- [ ] {ac}" for ac in acceptance_criteria)
-        files_block = "\n".join(f"- {f}" for f in matching_files)
-        return (
-            f"# Task {next_id}: {title}\n"
-            f"**File:** {file_header}\n"
-            f"**Source:** contract-propagation\n"
-            f"**Triggered-By:** Task {triggering_task_id}\n"
-            f"**Stack:** {stack}\n"
-            f"**Type:** feature\n"
-            f"**Status:** open\n"
-            f"\n"
-            f"## Goal\n"
-            f"{goal}\n"
-            f"\n"
-            f"## Source Context\n"
-            f"Generated automatically via Contract Propagation Engine following "
-            f"contract mutations in Task {triggering_task_id}.\n"
-            f"Modified contract files:\n"
-            f"{files_block}\n"
-            f"\n"
-            f"## Acceptance Criteria\n"
-            f"{ac_block}\n"
-            f"\n"
-            f"## Factual Git Diff\n"
-            f"<!-- BEGIN_GIT_DIFF -->\n"
-            f"<!-- END_GIT_DIFF -->\n"
-        )
-
-    def process_task_closure(
-        self,
-        task_id: int,
-        task_file: str,
-        diff_text: str,
-        repo_root: str | Path,
-        state: StateMachine,
-    ) -> list[dict]:
-        """Dispatch downstream tasks for contract mutations in a closed task.
-
-        Args:
-            task_id: ID of the closed task whose diff triggered propagation.
-            task_file: Path of the closed task file (informational).
-            diff_text: Raw git diff text extracted from the task file.
-            repo_root: Workspace root (repo anchor for `tasks/`).
-            state: StateMachine used to register generated backlog tasks.
-
-        Returns:
-            List of dispatch summaries: ``{"task_id", "title", "file"}``.
-            Empty list when no contract rule matched (no-op).
-        """
-        repo_root_path = Path(repo_root)
-        modified_paths = extract_modified_paths(diff_text)
-        rule_matches = match_contract_rules(modified_paths, self.rules)
-        if not rule_matches:
-            return []
-
-        tasks_root = repo_root_path / self.tasks_dir
-        next_id = discover_next_task_id(tasks_root)
-        backlog_dir = tasks_root / "backlog"
-        backlog_dir.mkdir(parents=True, exist_ok=True)
-
-        dispatched: list[dict] = []
-        for rule, matching_files in rule_matches:
-            for template in rule.downstream_tasks:
-                title = template.title_template.format(
-                    contract_name=rule.name,
-                    triggering_task_id=task_id,
-                )
-                goal = template.goal_template.format(
-                    contract_name=rule.name,
-                    triggering_task_id=task_id,
-                    files=", ".join(matching_files),
-                )
-                slug = re.sub(_SLUG_RE, "-", title.lower()).strip("-")[:50]
-                filename = f"{next_id:02d}-{slug}.md"
-                file_header = f"tasks/backlog/{filename}"
-                target_path = backlog_dir / filename
-
-                body = self._build_task_body(
-                    next_id=next_id,
-                    title=title,
-                    triggering_task_id=task_id,
-                    stack=template.stack,
-                    goal=goal,
-                    matching_files=matching_files,
-                    file_header=file_header,
-                    acceptance_criteria=template.acceptance_criteria,
-                )
-                target_path.write_text(body, encoding="utf-8")
-                state.register_task(str(target_path), TaskState.BACKLOG)
-
-                dispatched.append(
-                    {"task_id": next_id, "title": title, "file": file_header}
-                )
-                next_id += 1
-
-        return dispatched
\ No newline at end of file
diff --git a/loop-engine/daemon.py b/loop-engine/daemon.py
deleted file mode 100644
index 3af573a..0000000
--- a/loop-engine/daemon.py
+++ /dev/null
@@ -1,798 +0,0 @@
-"""
-Cognitive Loop Engine — Main Daemon Entry Point.
-
-Orchestrates: Watcher -> Router -> Gateway -> Executor -> QA -> State
-Runs as: uv run loop-engine/daemon.py
-
-Task Entry Trigger Gate:
-- trigger_mode="auto": legacy auto-pickup (no admin gate).
-- trigger_mode="telegram_button"|"command_only": tasks register as PENDING_TRIGGER.
-- auto_start_on_boot: if True, existing backlog tasks run immediately on boot.
-- CLI: python daemon.py --run <task_id> to trigger a specific staged task.
-"""
-
-import asyncio
-import json
-import os
-import sys
-import time
-from pathlib import Path
-
-# Add loop-engine to path for local imports
-sys.path.insert(0, str(Path(__file__).parent))
-
-from models import LoopEngineConfig, TaskState
-from state import StateMachine
-from watcher import KanbanWatcher
-from router import LLMRouter
-from gateway import ApprovalGateway
-from executor import HandsExecutor
-from qa_engine import QAEngine
-from brainstorm import BrainstormStage
-from stacks import StackRegistry, StackDetector, PreflightRunner
-
-try:
-    from verifier import ToolchainRunner
-except ImportError:
-    ToolchainRunner = None  # type: ignore
-
-try:
-    from contracts import ContractPropagationEngine
-except ImportError:
-    ContractPropagationEngine = None  # type: ignore
-
-try:
-    from specs import SpecGateEngine
-except ImportError:
-    SpecGateEngine = None  # type: ignore
-
-# Repo root = parent of loop-engine/. All relative paths in the config
-# (state db, evidence dir, tasks/, system-prompt.md) are anchored here so the
-# daemon behaves identically no matter which directory it is launched from.
-REPO_ROOT = Path(__file__).resolve().parent.parent
-
-
-def strip_jsonc(raw: str) -> str:
-    """Strip JSONC comments (quote-aware), trailing commas, and resolve ${VAR} refs.
-
-    Quote-aware comment stripping prevents corruption of string values that
-    contain '//' (e.g. https:// URLs).
-    """
-    import re
-
-    # 1. Remove /* */ block comments (quote-aware scan)
-    out = []
-    i, n = 0, len(raw)
-    in_string = False
-    while i < n:
-        c = raw[i]
-        if in_string:
-            out.append(c)
-            if c == "\\" and i + 1 < n:
-                out.append(raw[i + 1])
-                i += 2
-                continue
-            if c == '"':
-                in_string = False
-            i += 1
-            continue
-        if c == '"':
-            in_string = True
-            out.append(c)
-            i += 1
-            continue
-        if c == "/" and i + 1 < n and raw[i + 1] == "*":
-            end = raw.find("*/", i + 2)
-            i = n if end == -1 else end + 2
-            continue
-        if c == "/" and i + 1 < n and raw[i + 1] == "/":
-            end = raw.find("\n", i)
-            i = n if end == -1 else end
-            continue
-        out.append(c)
-        i += 1
-    stripped = "".join(out)
-
-    # 2. Strip trailing commas
-    stripped = re.sub(r',\s*([}\]])', r'\1', stripped)
-    # 3. Resolve env var refs: ${VAR_NAME} -> os.environ
-    stripped = re.sub(r'\$\{(\w+)\}', lambda m: os.environ.get(m.group(1), ''), stripped)
-    return stripped
-
-
-def load_config(config_path: str = "loop-engine/loop-engine.jsonc") -> LoopEngineConfig:
-    """Load config from JSONC file (strip comments)."""
-    p = Path(config_path)
-    if not p.is_absolute():
-        p = REPO_ROOT / config_path
-    if not p.exists():
-        # Use defaults
-        return LoopEngineConfig(approval={"chat_id": 0})
-
-    data = json.loads(strip_jsonc(p.read_text(encoding="utf-8")))
-    return LoopEngineConfig(**data)
-
-
-# Executor statuses that mean the Hands session did NOT produce work.
-# Anything outside EXEC_OK / EXEC_BLOCKED must crash the task, never reach QA.
-EXEC_OK = "complete"
-EXEC_BLOCKED = "blocked"
-
-
-def resolve_actual_task_path(task_file: str, repo_root: Path) -> tuple[Path, str]:
-    """Dynamically find a task file across all Kanban folders if it was moved."""
-    p = Path(task_file)
-    if not p.is_absolute():
-        p = repo_root / task_file
-    if p.exists():
-        return p, task_file
-
-    # If not found at recorded path, search across all standard Kanban directories
-    filename = Path(task_file).name
-    for folder in ("in-progress", "qa", "backlog", "completed"):
-        candidate = repo_root / "tasks" / folder / filename
-        if candidate.exists():
-            rel_path = str(candidate.relative_to(repo_root))
-            return candidate, rel_path
-    return p, task_file
-
-
-def extract_task_diff(task_file: Path) -> str | None:
-    """Extract ONLY the content between <!-- BEGIN_GIT_DIFF --> and <!-- END_GIT_DIFF -->.
-
-    Reads the updated task file post-execution. Returns stripped diff content,
-    or None if markers are missing/malformed. Empty stripped content is treated
-    as missing evidence by the caller.
-    """
-    try:
-        text = task_file.read_text(encoding="utf-8")
-    except Exception:
-        return None
-    begin = "<!-- BEGIN_GIT_DIFF -->"
-    end = "<!-- END_GIT_DIFF -->"
-    if begin not in text or end not in text:
-        return None
-    start = text.index(begin) + len(begin)
-    stop = text.index(end, start)
-    if stop < start:
-        return None
-    diff = text[start:stop].strip()
-    return diff
-
-
-async def _execute_and_qa(
-    task_id: int,
-    task_file: str,
-    task_content: str,
-    task_path: Path,
-    state: StateMachine,
-    executor: HandsExecutor,
-    qa: QAEngine,
-    *,
-    blueprint_context: str = "",
-    qa_feedback: str = "",
-    log_prefix: str = "pipeline",
-    stack_profile=None,
-) -> dict | None:
-    """Shared helper for execute → status check → diff extract → QA.
-
-    DRY extraction of the sequence duplicated in _process_task and _reimplement_task.
-    Uses existing retry counter, no parallel counter. Returns qa_result dict on
-    success (whether PASSED or FAILED), or None if the task was transitioned to
-    CRASHED (executor blocked/error or empty diff). Caller decides FAILED retry vs
-    PASSED progression. No behavior change, pure deduplication.
-    """
-    kwargs = {}
-    if stack_profile is not None:
-        kwargs["stack_profile"] = stack_profile
-    try:
-        result = await executor.execute(
-            task_id, task_file, task_content,
-            blueprint_context=blueprint_context, qa_feedback=qa_feedback,
-            **kwargs,
-        )
-    except TypeError as e:
-        if "stack_profile" in str(e) and kwargs:
-            # Fallback for legacy executors / stubs that don't yet accept stack_profile
-            result = await executor.execute(
-                task_id, task_file, task_content,
-                blueprint_context=blueprint_context, qa_feedback=qa_feedback,
-            )
-        else:
-            raise
-    print(f"[{log_prefix}] Execution result: {result['status']}")
-
-    if result["status"] == EXEC_BLOCKED:
-        state.update_state(task_id, TaskState.CRASHED)
-        print(f"[{log_prefix}] Task #{task_id} crashed: {result['status']}")
-        return None
-
-    if result["status"] != EXEC_OK:
-        state.update_state(task_id, TaskState.CRASHED)
-        print(
-            f"[{log_prefix}] Task #{task_id} crashed: executor status "
-            f"'{result['status']}': {result.get('error', '')[:200]}"
-        )
-        return None
-
-    diff = extract_task_diff(task_path)
-    if not diff or not diff.strip():
-        state.update_state(task_id, TaskState.CRASHED)
-        print(
-            f"[{log_prefix}] Empty or missing diff for task #{task_id} "
-            f"(markers missing/malformed or diff empty) — crashing, no evidence"
-        )
-        return None
-
-    # --- Toolchain verification (LE-2) — deterministic lint/build/test before LLM QA ---
-    if ToolchainRunner is not None:
-        # Resolve evidence base from QA engine config if available
-        try:
-            evidence_base_dir = qa.config.evidence_dir if hasattr(qa, "config") and hasattr(qa.config, "evidence_dir") else str(qa.evidence_dir) if hasattr(qa, "evidence_dir") else "loop-engine/evidence"
-        except Exception:
-            evidence_base_dir = "loop-engine/evidence"
-        # Determine profile: use provided stack_profile or fallback to generic no-op
-        effective_profile = stack_profile
-        if effective_profile is None:
-            # Try to create a synthetic generic profile (all toolchain null) to avoid None errors
-            try:
-                from models import StackProfileConfig
-                from stacks import StackProfile as _SP
-                effective_profile = _SP(StackProfileConfig(name="generic", display_name="Generic"))
-            except Exception:
-                effective_profile = stack_profile
-        try:
-            runner = ToolchainRunner(timeout_per_command=120.0, evidence_base_dir=evidence_base_dir)
-            toolchain_result = await runner.run(
-                effective_profile, task_id=task_id, cwd=REPO_ROOT, diff_text=diff
-            )
-            if not toolchain_result.passed:
-                # Fail-fast: record feedback, bypass LLM QA, return FAILED for retry logic
-                try:
-                    state.set_qa_feedback(task_id, toolchain_result.report_md)
-                except Exception:
-                    pass
-                print(f"[{log_prefix}] Toolchain verification FAILED for task #{task_id}")
-                print(toolchain_result.summary)
-                return {
-                    "result": "FAILED",
-                    "report": toolchain_result.report_md,
-                    "evidence_dir": str(Path(evidence_base_dir) / str(task_id)),
-                }
-            # Success: forward summary as evidence to QA
-            toolchain_evidence = toolchain_result.summary
-        except Exception as e:
-            # Toolchain infra error — treat as CRASHED? For now, log and proceed to QA to avoid blocking
-            print(f"[{log_prefix}] Toolchain runner error (proceeding to QA): {e}")
-            toolchain_evidence = ""
-    else:
-        toolchain_evidence = ""
-
-    state.update_state(task_id, TaskState.QA)
-    print(f"[{log_prefix}] Running QA for task #{task_id}...")
-    # Forward toolchain evidence if available (LE-2 enrichment)
-    try:
-        qa_result = qa.run_qa(task_id, task_content, diff, toolchain_evidence=toolchain_evidence)
-    except TypeError:
-        # Fallback for legacy QA stubs without toolchain_evidence param
-        qa_result = qa.run_qa(task_id, task_content, diff)
-    print(f"[{log_prefix}] QA result: {qa_result['result']}")
-    return qa_result
-
-
-async def _reimplement_task(
-    task_id: int,
-    task_file: str,
-    initial_qa_feedback: str,
-    config: LoopEngineConfig,
-    state: StateMachine,
-    router: LLMRouter,
-    gateway: ApprovalGateway,
-    executor: HandsExecutor,
-    qa: QAEngine,
-) -> None:
-    """Scoped retry loop — implementation-only, no brainstorm or plan re-approval.
-
-    Called after an initial QA FAILED. Loops up to config.max_qa_retries,
-    using state.get_qa_retry_count() as the single source of truth (no parallel
-    counter). Each iteration:
-      1. executor.execute() with qa_feedback as DISTINCT param (never blueprint_context)
-      2. extract_task_diff() per LE-0.2 logic
-      3. qa.run_qa()
-    On QA PASSED, proceeds to REVIEW → AWAITING_CLOSURE (same as main pipeline).
-    On QA FAILED, loops again or CRASHED when limit hit. Never sends a new
-    Telegram plan-approval message.
-    """
-    current_feedback = initial_qa_feedback
-    while True:
-        retries = state.get_qa_retry_count(task_id)
-        if retries >= config.max_qa_retries:
-            state.update_state(task_id, TaskState.CRASHED)
-            print(
-                f"[reimplement] Max QA retries ({config.max_qa_retries}) "
-                f"reached for task #{task_id} — crashing"
-            )
-            return
-
-        # Fresh read — captures prior Hands edits and QA feedback appended to file
-        try:
-            task_content = Path(task_file).read_text(encoding="utf-8")
-        except Exception as e:
-            state.update_state(task_id, TaskState.CRASHED)
-            print(f"[reimplement] Failed to re-read task file for #{task_id}: {e}")
-            return
-
-        task_path = Path(task_file)
-        state.update_state(task_id, TaskState.IMPLEMENTING)
-        print(
-            f"[reimplement] Retrying implementation for task #{task_id} "
-            f"(retry {retries + 1}/{config.max_qa_retries})..."
-        )
-
-        # Stack detection + preflight (LE-1)
-        registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
-        profile = StackDetector.detect(task_content, REPO_ROOT, registry, default_stack=config.default_stack)
-        print(f"[reimplement] Detected stack: {profile.name} ({profile.display_name})")
-        runner = PreflightRunner(timeout_seconds=30.0)
-        preflight = await runner.run(profile, cwd=REPO_ROOT)
-        if not preflight.passed:
-            state.update_state(task_id, TaskState.CRASHED)
-            diag = "; ".join(preflight.errors)
-            print(f"[reimplement] Preflight failed for stack {profile.name}: {diag} — crashing")
-            try:
-                state.set_qa_feedback(task_id, f"Preflight failed for stack {profile.name}: {diag}")
-            except Exception:
-                pass
-            return
-
-        qa_result = await _execute_and_qa(
-            task_id, task_file, task_content, task_path, state, executor, qa,
-            qa_feedback=current_feedback, log_prefix="reimplement", stack_profile=profile
-        )
-        if qa_result is None:
-            return
-
-        if qa_result["result"] == "FAILED":
-            # qa.run_qa already incremented retry count via set_qa_feedback
-            current_feedback = (
-                qa_result.get("report", "") or qa_result.get("feedback", "") or current_feedback
-            )
-            continue
-
-        # QA PASSED — proceed to REVIEW and CLOSURE (mirrors main pipeline steps 5-6)
-        state.update_state(task_id, TaskState.REVIEW)
-        review = qa.run_review(task_id, task_content, qa_result.get("report", ""),
-                               stack_profile=profile)
-        print(f"[reimplement] Review result: {review['result']}")
-
-        if review["result"] == "REJECTED":
-            state.update_state(task_id, TaskState.CRASHED)
-            return
-
-        state.update_state(task_id, TaskState.AWAITING_CLOSURE)
-        approved = await gateway.request_approval(
-            task_id, "Closure Approval", f"Task #{task_id} complete. Approve closure?"
-        )
-        if approved:
-            state.update_state(task_id, TaskState.CLOSED)
-            print(f"[reimplement] Task #{task_id} CLOSED after retry.")
-
-            # --- Contract Propagation (LE-6) — dispatch downstream tasks ---
-            diff = extract_task_diff(task_path) or ""
-            if ContractPropagationEngine is not None:
-                propagation_engine = ContractPropagationEngine(
-                    config.contract_rules, tasks_dir=config.tasks_dir
-                )
-                dispatched = propagation_engine.process_task_closure(
-                    task_id, task_file, diff, REPO_ROOT, state
-                )
-                if dispatched:
-                    print(f"[pipeline] Contract propagation dispatched {len(dispatched)} downstream task(s):")
-                    for d in dispatched:
-                        print(f"  - Task #{d['task_id']}: {d['title']} ({d['file']})")
-        else:
-            print(
-                f"[reimplement] Closure rejected for task #{task_id} after retry. Stays in review."
-            )
-        return
-
-
-async def process_task(task_id: int, task_file: str, config: LoopEngineConfig,
-                       state: StateMachine, router: LLMRouter,
-                       gateway: ApprovalGateway, executor: HandsExecutor,
-                       qa: QAEngine, brainstorm: BrainstormStage):
-    """Full pipeline for one task."""
-    print(f"\n[pipeline] Processing task #{task_id}: {task_file}")
-
-    # Dynamic path resolution (HOTFIX-04): the task may have moved across
-    # Kanban folders since registration. Re-sync the state DB best-effort and
-    # process from the actual on-disk path.
-    actual_path, actual_rel_path = resolve_actual_task_path(task_file, REPO_ROOT)
-    resolved_task_file = task_file
-    if actual_path.exists() and actual_rel_path != task_file:
-        try:
-            state.conn.execute("UPDATE tasks SET task_file = ? WHERE task_id = ?", (actual_rel_path, task_id))
-            state.conn.commit()
-        except Exception:
-            pass
-        resolved_task_file = actual_rel_path
-
-    # In-flight concurrency lock (HOTFIX-06): re-check before executing so
-    # duplicate dispatches (button spam, repeated /run, watcher+boot) never
-    # run the same task twice concurrently. The daemon instance is resolved
-    # from the gateway's registered reference; legacy/unregistered callers
-    # simply skip the lock (single-shot paths).
-    daemon_instance = getattr(gateway, "_daemon", None)
-    if (
-        daemon_instance is not None
-        and task_id in daemon_instance._in_flight_tasks
-    ):
-        print(f"[daemon] Task #{task_id} is already running in background. Ignoring duplicate trigger.")
-        return
-    if daemon_instance is not None:
-        daemon_instance._in_flight_tasks.add(task_id)
-    try:
-        await _process_task(task_id, resolved_task_file, config, state, router,
-                            gateway, executor, qa, brainstorm)
-    except Exception as e:
-        state.update_state(task_id, TaskState.CRASHED)
-        print(f"[pipeline] Task #{task_id} crashed with unexpected error: {e}")
-    finally:
-        if daemon_instance is not None:
-            daemon_instance._in_flight_tasks.discard(task_id)
-
-
-class LoopEngineDaemon:
-    """Encapsulates daemon state and provides trigger_task() for the gateway."""
-
-    def __init__(self, config, state, router, gateway, executor, qa, brainstorm):
-        self.config = config
-        self.state = state
-        self.router = router
-        self.gateway = gateway
-        self.executor = executor
-        self.qa = qa
-        self.brainstorm = brainstorm
-        self.stack_registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
-        # In-flight concurrency lock (HOTFIX-06): task ids currently executing.
-        # Prevents duplicate concurrent execution from button spam, repeated
-        # /run commands, or watcher+boot double-dispatch.
-        self._in_flight_tasks: set[int] = set()
-        self.propagation_engine = (
-            ContractPropagationEngine(config.contract_rules, tasks_dir=config.tasks_dir)
-            if ContractPropagationEngine is not None
-            else None
-        )
-
-    async def trigger_task(self, task_id: int) -> None:
-        """Trigger execution of a PENDING_TRIGGER task.
-
-        Fresh Read Guarantee: re-reads the task file from disk so any
-        manual edits/refinements are captured before processing.
-        """
-        task_record = self.state.get_task(task_id)
-        if not task_record:
-            print(f"[daemon] Task #{task_id} not found in state machine.")
-            return
-
-        # In-flight concurrency lock (HOTFIX-06): ignore duplicate triggers for
-        # a task that is already executing in the background.
-        if task_id in self._in_flight_tasks:
-            print(f"[daemon] Task #{task_id} is already running in background. Ignoring duplicate trigger.")
-            return
-
-        task_file = task_record["task_file"]
-
-        # Fresh read from disk with dynamic path resolution (HOTFIX-04): the
-        # task may have been moved across Kanban folders after registration.
-        task_path, actual_rel_path = resolve_actual_task_path(task_file, REPO_ROOT)
-        if not task_path.exists():
-            print(f"[daemon] Task file not found: {task_file}")
-            self.state.update_state(task_id, TaskState.CRASHED)
-            return
-
-        # Sync state DB if the file was moved across Kanban folders
-        if actual_rel_path != task_file:
-            try:
-                self.state.conn.execute("UPDATE tasks SET task_file = ? WHERE task_id = ?", (actual_rel_path, task_id))
-                self.state.conn.commit()
-            except Exception:
-                pass
-            task_file = actual_rel_path
-
-        # Transition PENDING_TRIGGER -> PLANNING
-        self.state.update_state(task_id, TaskState.PLANNING)
-        print(f"[daemon] Task #{task_id} triggered, transitioning to PLANNING...")
-
-        # Launch processing
-        asyncio.create_task(
-            process_task(task_id, task_file, self.config, self.state,
-                         self.router, self.gateway, self.executor,
-                         self.qa, self.brainstorm))
-
-    async def boot_scan(self) -> list[dict]:
-        """Scan backlog and resend trigger cards for pending tasks on boot.
-
-        If auto_start_on_boot=True: register as BACKLOG and auto-process.
-        If auto_start_on_boot=False: register as PENDING_TRIGGER and send
-        ONE consolidated trigger summary (anti-flood, HOTFIX-02) covering BOTH
-        newly detected backlog files AND any tasks already registered in
-        PENDING_TRIGGER state (survives daemon restarts).
-        """
-        self.gateway._ensure_poller()
-        from watcher import KanbanWatcher
-        watcher = KanbanWatcher(self.state, self.config, self.gateway)
-
-        if self.config.auto_start_on_boot:
-            # Legacy: auto-process existing tasks
-            existing = watcher.scan_existing()
-            for t in existing:
-                asyncio.create_task(
-                    process_task(t["task_id"], t["file"], self.config,
-                                 self.state, self.router, self.gateway,
-                                 self.executor, self.qa, self.brainstorm))
-            return existing
-        else:
-            # 1. Register newly detected backlog files (PENDING_TRIGGER).
-            existing = watcher.scan_existing()
-            # 2. Include tasks already in PENDING_TRIGGER state (restart survival).
-            pending_in_db = self.state.get_pending_trigger_tasks()
-
-            # Normalize both sources into one deduped, ordered task list.
-            # scan_existing() yields {"task_id", "file"}; the DB yields
-            # {"task_id", "task_file", ...}. New files come first (scan order),
-            # then DB-only leftovers. Dedup by task_id so a fresh boot with a
-            # partially registered DB does not list any task twice.
-            seen: set[int] = set()
-            summary_tasks: list[dict] = []
-            for t in existing:
-                sid = t["task_id"]
-                if sid in seen:
-                    continue
-                seen.add(sid)
-                summary_tasks.append({
-                    "task_id": sid,
-                    "title": Path(t["file"]).stem,
-                    "file": t["file"],
-                })
-            for t in pending_in_db:
-                sid = t["task_id"]
-                if sid in seen:
-                    continue
-                seen.add(sid)
-                summary_tasks.append({
-                    "task_id": sid,
-                    "title": Path(t["task_file"]).stem,
-                    "file": t["task_file"],
-                })
-
-            # Anti-flood: ONE consolidated message with Start buttons for the
-            # top pending tasks — never one card per task on boot.
-            if summary_tasks:
-                await self.gateway.send_boot_scan_summary(summary_tasks)
-            return existing or pending_in_db
-
-
-async def _process_task(task_id: int, task_file: str, config: LoopEngineConfig,
-                        state: StateMachine, router: LLMRouter,
-                        gateway: ApprovalGateway, executor: HandsExecutor,
-                        qa: QAEngine, brainstorm: BrainstormStage):
-    """Inner pipeline — exceptions propagate to process_task's guard."""
-    # Dynamic path resolution (HOTFIX-04): resolve the actual on-disk path so
-    # the fresh read below never fails on a stale recorded path after a Kanban
-    # move. Callers (process_task / trigger_task) already re-synced the DB.
-    task_file_path, _ = resolve_actual_task_path(task_file, REPO_ROOT)
-    task_path = task_file_path
-    task_content = task_path.read_text(encoding="utf-8")
-
-    # Stack detection (LE-1) — detect once at the start so planning, QA, and
-    # review all share the same profile for stack-aware model routing (LE-3).
-    registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
-    profile = StackDetector.detect(task_content, REPO_ROOT, registry, default_stack=config.default_stack)
-    print(f"[pipeline] Detected stack: {profile.name} ({profile.display_name})")
-
-    # 0. BRAINSTORMING (Phase 1.5) — optional pre-planning stage
-    extra_context = ""
-    if brainstorm.should_trigger(task_content):
-        state.update_state(task_id, TaskState.PLANNING)
-        print(f"[pipeline] Brainstorming triggered for task #{task_id} "
-              f"(six-persona swarm)...")
-        session = await brainstorm.run(task_content)
-        approved = await gateway.request_approval(
-            task_id, "Brainstorm Review", session["session"])
-        if not approved:
-            state.update_state(task_id, TaskState.BACKLOG)
-            print(f"[pipeline] Brainstorm rejected for task #{task_id}. "
-                  f"Back to backlog.")
-            return
-        extra_context = session["session"]
-
-    # 1. PLANNING
-    state.update_state(task_id, TaskState.PLANNING)
-    print(f"[pipeline] Planning task #{task_id}...")
-    try:
-        routing = router.route_plan(task_content, extra_context=extra_context,
-                                    stack_profile=profile)
-    except TypeError:
-        # Fallback for legacy routers/stubs without stack_profile param
-        routing = router.route_plan(task_content, extra_context=extra_context)
-    plan = router.call_llm(routing)
-    state.set_plan(task_id, plan)
-
-    # 2. AWAITING_APPROVAL (Plan)
-    state.update_state(task_id, TaskState.AWAITING_APPROVAL)
-    approved = await gateway.request_approval(task_id, "Plan Approval", plan)
-    if not approved:
-        state.update_state(task_id, TaskState.BACKLOG)
-        print(f"[pipeline] Plan rejected for task #{task_id}. Back to backlog.")
-        return
-
-    # 2.5 SPEC-FIRST GATE (LE-8) — after Plan Approval, before IMPLEMENTING.
-    # Architectural / contract / schema tasks must have verified spec artifacts
-    # (ADR, PRD, Contract, Data Model) in the workspace or staged diff, otherwise
-    # the task crashes BEFORE any code is generated.
-    if SpecGateEngine is not None and config.spec_gate.enabled:
-        spec_engine = SpecGateEngine(config.spec_gate)
-        rules = spec_engine.evaluate_requirements(task_content, plan)
-        if rules:
-            spec_res = spec_engine.validate_artifacts(rules, REPO_ROOT, diff_text="")
-            if not spec_res.passed:
-                state.update_state(task_id, TaskState.CRASHED)
-                try:
-                    state.set_qa_feedback(task_id, spec_res.report_md)
-                except Exception:
-                    pass
-                print(
-                    f"[pipeline] Spec Gate FAILED for task #{task_id}: "
-                    f"{'; '.join(spec_res.errors)} — crashing"
-                )
-                return
-            state.set_spec_artifacts(task_id, spec_res.found_artifacts)
-            print(
-                f"[pipeline] Spec Gate PASSED for task #{task_id}: verified "
-                f"{len(spec_res.found_artifacts)} artifact(s)"
-            )
-
-    # 3. IMPLEMENTING — preflight (profile already detected at pipeline start)
-    state.update_state(task_id, TaskState.IMPLEMENTING)
-    print(f"[pipeline] Implementing task #{task_id}...")
-    runner = PreflightRunner(timeout_seconds=30.0)
-    preflight = await runner.run(profile, cwd=REPO_ROOT)
-    if not preflight.passed:
-        state.update_state(task_id, TaskState.CRASHED)
-        diag = "; ".join(preflight.errors)
-        print(f"[pipeline] Preflight failed for stack {profile.name}: {diag} — crashing")
-        try:
-            state.set_qa_feedback(task_id, f"Preflight failed for stack {profile.name}: {diag}")
-        except Exception:
-            pass
-        return
-    qa_result = await _execute_and_qa(
-        task_id, task_file, task_content, task_path, state, executor, qa,
-        blueprint_context=plan, log_prefix="pipeline", stack_profile=profile
-    )
-    if qa_result is None:
-        return
-
-    if qa_result["result"] == "FAILED":
-        qa_feedback = qa_result.get("report", "") or ""
-        return await _reimplement_task(
-            task_id, task_file, qa_feedback, config, state, router, gateway, executor, qa
-        )
-
-    # 5. REVIEW
-    state.update_state(task_id, TaskState.REVIEW)
-    review = qa.run_review(task_id, task_content, qa_result.get("report", ""),
-                           stack_profile=profile)
-    print(f"[pipeline] Review result: {review['result']}")
-
-    if review["result"] == "REJECTED":
-        state.update_state(task_id, TaskState.CRASHED)
-        return
-
-    # 6. AWAITING_CLOSURE
-    state.update_state(task_id, TaskState.AWAITING_CLOSURE)
-    approved = await gateway.request_approval(task_id, "Closure Approval",
-                                               f"Task #{task_id} complete. Approve closure?")
-    if approved:
-        state.update_state(task_id, TaskState.CLOSED)
-        print(f"[pipeline] Task #{task_id} CLOSED.")
-
-        # --- Contract Propagation (LE-6) — dispatch downstream tasks ---
-        diff = extract_task_diff(task_path) or ""
-        if ContractPropagationEngine is not None:
-            propagation_engine = ContractPropagationEngine(
-                config.contract_rules, tasks_dir=config.tasks_dir
-            )
-            dispatched = propagation_engine.process_task_closure(
-                task_id, task_file, diff, REPO_ROOT, state
-            )
-            if dispatched:
-                print(f"[pipeline] Contract propagation dispatched {len(dispatched)} downstream task(s):")
-                for d in dispatched:
-                    print(f"  - Task #{d['task_id']}: {d['title']} ({d['file']})")
-    else:
-        print(f"[pipeline] Closure rejected for task #{task_id}. Stays in review.")
-
-
-async def main():
-    """Main loop: watch -> process -> repeat."""
-    import argparse
-
-    # CLI argument parsing
-    parser = argparse.ArgumentParser(description="Cognitive Loop Engine Daemon")
-    parser.add_argument("--run", type=int, metavar="TASK_ID",
-                        help="Trigger and run a specific staged task by ID")
-    args = parser.parse_args()
-
-    # Anchor all relative paths (config, state db, tasks/, evidence) to repo root
-    os.chdir(REPO_ROOT)
-
-    print("=" * 60)
-    print("  Cognitive Loop Engine — Starting...")
-    print("=" * 60)
-
-    config = load_config()
-    state = StateMachine()
-    router = LLMRouter(config)
-    gateway = ApprovalGateway(config)
-    executor = HandsExecutor(config, state)
-    qa = QAEngine(config, state, router)
-    brainstorm = BrainstormStage(config, router, workspace_root=str(REPO_ROOT))
-
-    # Create daemon instance
-    daemon = LoopEngineDaemon(config, state, router, gateway, executor, qa, brainstorm)
-
-    # Wire up gateway <-> daemon and gateway <-> state
-    gateway.set_daemon(daemon)
-    gateway.set_state(state)
-
-    # CLI --run mode: trigger a specific task and exit
-    if args.run is not None:
-        print(f"[daemon] CLI trigger: task #{args.run}")
-        await daemon.trigger_task(args.run)
-        # Keep alive briefly for the task to start
-        await asyncio.sleep(2)
-        return
-
-    # Normal daemon mode: boot scan + watch.
-    # Ensure Telegram polling is actively listening (for /start and button
-    # clicks) BEFORE boot_scan sends the trigger cards — otherwise the first
-    # cards can be sent while no updater/poller is running (HOTFIX-01).
-    gateway._ensure_poller()
-    existing = await daemon.boot_scan()
-    print(f"[daemon] Found {len(existing)} existing tasks in backlog "
-          f"(trigger_mode={config.trigger_mode}, "
-          f"auto_start_on_boot={config.auto_start_on_boot}).")
-
-    # Start filesystem watcher
-    loop = asyncio.get_running_loop()
-
-    def on_task_detected(task_id: int, task_file: str):
-        if config.trigger_mode == "auto":
-            asyncio.run_coroutine_threadsafe(
-                process_task(task_id, task_file, config, state, router,
-                             gateway, executor, qa, brainstorm), loop)
-        else:
-            # Register as PENDING_TRIGGER and send card
-            state.update_state(task_id, TaskState.PENDING_TRIGGER)
-            asyncio.run_coroutine_threadsafe(
-                gateway.send_task_trigger_card(task_id, task_file.split("/")[-1], task_file),
-                loop)
-
-    watcher = KanbanWatcher(state, config, gateway, on_task_detected=on_task_detected)
-    watcher.start()
-
-    print("[daemon] Watching for new tasks... Press Ctrl+C to stop.")
-
-    try:
-        while True:
-            await asyncio.sleep(1)
-    except KeyboardInterrupt:
-        print("\n[daemon] Shutting down...")
-        watcher.stop()
-        state.close()
-
-
-if __name__ == "__main__":
-    asyncio.run(main())
diff --git a/loop-engine/executor.py b/loop-engine/executor.py
deleted file mode 100644
index 07494ec..0000000
--- a/loop-engine/executor.py
+++ /dev/null
@@ -1,248 +0,0 @@
-"""
-Hands Executor v2 — delegates auto-continue to Goal Plugin.
-
-The Goal Plugin (@prevalentware/opencode-goal-plugin) runs INSIDE OpenCode
-and handles: event-driven idle detection, terminal markers, no-progress,
-budget enforcement, compaction survival, re-entrancy guard.
-
-Our executor.py only needs to:
-1. Send the initial prompt to OpenCode CLI
-2. Wait for the Goal Plugin to finish (or timeout)
-3. Read the result from the task file
-4. Handle transport errors with retry
-
-ZAC intact: executor NEVER commits.
-"""
-
-import asyncio
-import os
-import re
-import signal
-import time
-from datetime import datetime, timezone
-from pathlib import Path
-from typing import Optional, Any
-
-from models import LoopEngineConfig
-from state import StateMachine
-
-
-TERM_COMPLETE = re.compile(r'\[goal:complete\]', re.IGNORECASE)
-TERM_BLOCKED = re.compile(r'\[goal:blocked(?::\s*([^\]]+))?\]', re.IGNORECASE)
-TRANSPORT_ERROR = re.compile(r'stream disconnected|ECONNRESET|ETIMEDOUT|EPIPE|timeout|connection reset', re.IGNORECASE)
-
-MAX_RETRIES = 3
-RETRY_DELAY = 5  # seconds
-
-
-class HandsExecutor:
-    """Delegates auto-continue to Goal Plugin, monitors result."""
-
-    def __init__(self, config: LoopEngineConfig, state: StateMachine):
-        self.config = config
-        self.state = state
-        self._semaphore = asyncio.Semaphore(config.max_parallel_tasks)
-
-    def _build_prompt(self, task_file: str, blueprint_context: str = "",
-                      qa_feedback: str = "", stack_profile: Optional[Any] = None) -> str:
-        """Construct the structured XML prompt for the local OpenCode agent.
-
-        Sections (emitted only when relevant):
-          1. <task_instructions> — read the task file, follow AGENTS.md.
-          2. <stack_context> — when a stack profile is present: mandate skill
-             loading via the native skill tool and list toolchain commands.
-          3. <blueprint_context> — approved Architect plan (LE-0.1).
-          4. <qa_feedback> — QA rejection feedback to address (LE-0.1).
-          5. <goal_rules> — Goal Plugin termination tokens.
-        """
-        parts = [
-            "<task_instructions>\n"
-            f"Read the task file at {task_file} and implement it.\n"
-            "Follow AGENTS.md rules exactly.\n"
-            "</task_instructions>",
-        ]
-
-        if stack_profile is not None:
-            try:
-                skills = getattr(stack_profile, "skills", []) or []
-                skills_str = ", ".join(skills) if skills else "none"
-                toolchain = getattr(stack_profile, "toolchain", None)
-                test_cmd = getattr(toolchain, "test_cmd", None) if toolchain else None
-                build_cmd = getattr(toolchain, "build_cmd", None) if toolchain else None
-                lint_cmd = getattr(toolchain, "lint_cmd", None) if toolchain else None
-                preflight = getattr(stack_profile, "preflight", []) or []
-                preflight_str = ", ".join(preflight) if preflight else "none"
-                name = getattr(stack_profile, "name", "unknown")
-                display_name = getattr(stack_profile, "display_name", name)
-                parts.append(
-                    f'<stack_context name="{name}" display_name="{display_name}">\n'
-                    f"MANDATORY: Load required skills via the native skill tool: {skills_str}\n"
-                    f"Preflight commands: {preflight_str}\n"
-                    f"Run toolchain verification before completion: "
-                    f"test='{test_cmd}', build='{build_cmd}', lint='{lint_cmd}'\n"
-                    "</stack_context>"
-                )
-            except Exception:
-                pass
-
-        if blueprint_context and blueprint_context.strip():
-            parts.append(
-                f"<blueprint_context>\n{blueprint_context.strip()}\n</blueprint_context>"
-            )
-
-        if qa_feedback and qa_feedback.strip():
-            parts.append(
-                f"<qa_feedback>\n{qa_feedback.strip()}\n\n"
-                "Address the above QA feedback explicitly. Do NOT treat this "
-                "as a new architectural plan.\n"
-                "</qa_feedback>"
-            )
-
-        parts.append(
-            "<goal_rules>\n"
-            "When finished and verified, output [goal:complete]. "
-            "If stuck, output [goal:blocked: <reason>].\n"
-            "</goal_rules>"
-        )
-
-        return "\n\n".join(parts)
-
-    async def execute(self, task_id: int, task_file: str, task_content: str,
-                    blueprint_context: str = "", qa_feedback: str = "",
-                    stack_profile: Optional[Any] = None) -> dict:
-        """Execute a task via OpenCode CLI with transport error retry.
-
-        Args:
-            task_id: Task identifier.
-            task_file: Path to task file.
-            task_content: Content of task file (may be stale; executor re-reads file).
-            blueprint_context: Approved architectural blueprint/plan (from Architect).
-                Injected as delimited section when non-empty. Named to avoid collision
-                with qa_feedback.
-            qa_feedback: QA rejection feedback to address (on retry). Injected as
-                distinct delimited section when non-empty, never overloaded with
-                blueprint_context.
-            stack_profile: Optional StackProfile detected for this task — skills and
-                toolchain commands are injected into the prompt.
-        """
-        prompt = self._build_prompt(
-            task_file, blueprint_context=blueprint_context,
-            qa_feedback=qa_feedback, stack_profile=stack_profile)
-
-        async with self._semaphore:
-            for attempt in range(MAX_RETRIES):
-                result = await self._run_once(task_file, prompt)
-
-                # Success or terminal failure — no retry
-                if result["status"] in ("complete", "blocked", "timeout"):
-                    return result
-
-                # Transport error — retry
-                if result["status"] == "transport_error" and attempt < MAX_RETRIES - 1:
-                    print(f"[executor] Transport error (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {RETRY_DELAY}s...")
-                    await asyncio.sleep(RETRY_DELAY)
-                    continue
-
-                # Non-transport error or final attempt
-                return result
-
-            return result  # last attempt result
-
-    async def _run_once(self, task_file: str, prompt: str) -> dict:
-        """Run one OpenCode turn via subprocess, with debug telemetry (HOTFIX-03).
-
-        Wraps the real implementation so every result path (complete, blocked,
-        transport_error, timeout, error) is captured by the same debug log hook.
-        """
-        result = await self._run_once_impl(task_file, prompt)
-        if os.environ.get("LOOP_ENGINE_DEBUG") == "1":
-            self._log_executor_debug(task_file, prompt, result)
-        return result
-
-    def _log_executor_debug(self, task_file: str, prompt: str, result: dict) -> None:
-        """Append the executor session to loop-engine/logs/executor_sessions.log.
-
-        Opt-in ONLY via LOOP_ENGINE_DEBUG=1. Never raises: telemetry must not
-        affect pipeline execution.
-        """
-        try:
-            log_dir = Path(__file__).resolve().parent / "logs"
-            log_dir.mkdir(parents=True, exist_ok=True)
-            entry = (
-                f"\n===== [{datetime.now(timezone.utc).isoformat(timespec='seconds')}Z] "
-                f"task_file={task_file} status={result.get('status')} "
-                f"returncode={result.get('returncode')} elapsed={result.get('elapsed', 0):.1f}s =====\n"
-                f"--- PROMPT ---\n{prompt}\n"
-                f"--- STDOUT ---\n{result.get('output', '')}\n"
-                f"--- STDERR ---\n{result.get('error', '')}\n"
-                f"===== END =====\n"
-            )
-            with open(log_dir / "executor_sessions.log", "a", encoding="utf-8") as f:
-                f.write(entry)
-        except Exception as e:
-            print(f"[executor] debug telemetry log error: {e}")
-
-    async def _run_once_impl(self, task_file: str, prompt: str) -> dict:
-        """Run one OpenCode turn via subprocess."""
-        start = time.time()
-        timeout = float(getattr(self.config.idle, "executing_timeout_seconds", None) or 900.0)
-
-        try:
-            kwargs = {}
-            if os.name == "posix":
-                kwargs["start_new_session"] = True
-            proc = await asyncio.create_subprocess_exec(
-                "opencode", "run", "--format", "json",
-                stdin=asyncio.subprocess.PIPE,
-                stdout=asyncio.subprocess.PIPE,
-                stderr=asyncio.subprocess.PIPE,
-                **kwargs,
-            )
-
-            stdout, stderr = await asyncio.wait_for(
-                proc.communicate(input=prompt.encode()),
-                timeout=timeout
-            )
-
-            output = stdout.decode(errors="replace")
-            error = stderr.decode(errors="replace")
-            elapsed = time.time() - start
-
-            # Check for terminal markers in output
-            if TERM_COMPLETE.search(output):
-                return {"status": "complete", "output": output, "error": error, "elapsed": elapsed}
-
-            m = TERM_BLOCKED.search(output)
-            if m:
-                reason = m.group(1).strip() if m.group(1) else "Agent signaled blocked"
-                return {"status": "blocked", "output": output, "error": error, "reason": reason, "elapsed": elapsed}
-
-            # Process exited — check return code
-            if proc.returncode == 0:
-                return {"status": "complete", "output": output, "error": error, "elapsed": elapsed}
-
-            # Check for transport errors in stderr
-            if TRANSPORT_ERROR.search(error):
-                return {"status": "transport_error", "output": output, "error": error, "elapsed": elapsed}
-
-            return {"status": "error", "output": output, "error": error, "returncode": proc.returncode, "elapsed": elapsed}
-
-        except asyncio.TimeoutError:
-            # Cleanly terminate the entire process group (start_new_session=True)
-            try:
-                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
-            except (ProcessLookupError, AttributeError, PermissionError):
-                pass
-            try:
-                await asyncio.wait_for(proc.wait(), timeout=2.0)
-            except (asyncio.TimeoutError, ProcessLookupError):
-                pass
-            return {"status": "timeout", "output": "", "error": f"Exceeded {timeout}s timeout", "elapsed": time.time() - start}
-
-        except FileNotFoundError:
-            return {"status": "error", "output": "", "error": "opencode CLI not found in PATH", "elapsed": time.time() - start}
-
-        except Exception as e:
-            if TRANSPORT_ERROR.search(str(e)):
-                return {"status": "transport_error", "output": "", "error": str(e), "elapsed": time.time() - start}
-            return {"status": "error", "output": "", "error": str(e), "elapsed": time.time() - start}
diff --git a/loop-engine/gateway.py b/loop-engine/gateway.py
deleted file mode 100644
index 99abfe8..0000000
--- a/loop-engine/gateway.py
+++ /dev/null
@@ -1,510 +0,0 @@
-"""
-Approval Gateway — Telegram inline keyboard for Manager sign-off.
-
-ZAC enforced: no task proceeds without explicit Manager approval.
-Uses inline keyboard with Approve/Reject buttons.
-Handles callback queries from Telegram.
-
-Extended with Task Entry Trigger Gate:
-- Sends trigger cards with [🚀 Start Execution] / [⏸️ Hold] buttons.
-- Parses /run, /start, /tasks, /backlog text commands.
-"""
-
-import asyncio
-import os
-from datetime import datetime, timezone
-from pathlib import Path
-from typing import Optional
-
-from models import LoopEngineConfig
-
-
-class ApprovalGateway:
-    """Telegram-based approval gate for Plan and Closure."""
-
-    def __init__(self, config: LoopEngineConfig):
-        self.config = config
-        self.pending: dict[str, asyncio.Event] = {}
-        self.results: dict[str, bool] = {}
-        self._bot = None
-        self._poller_task: Optional[asyncio.Task] = None
-        self._daemon = None  # set by daemon.py after init
-        self._state = None   # set by daemon.py after init
-        # Dedup store (HOTFIX-06): callback query ids already answered/processed
-        # so duplicate clicks (Telegram re-delivery, double taps) are ignored.
-        self._processed_callback_ids: set[str] = set()
-
-    def set_daemon(self, daemon):
-        """Register the daemon instance for trigger callbacks."""
-        self._daemon = daemon
-
-    def set_state(self, state):
-        """Register the state machine for /tasks queries."""
-        self._state = state
-
-    async def _send_with_retry(self, send_coroutine_fn, max_retries: int = 3,
-                               base_delay: float = 1.0, task_id=None,
-                               stage: str = "", content: str = "") -> bool:
-        """Exponential backoff retry for Telegram sends (Task 144).
-
-        Transient: NetworkError, TimedOut, RetryAfter (incl. asyncio.TimeoutError)
-        -> sleep base_delay*(2**attempt) and retry.
-        Fatal: InvalidToken -> fail fast, no retry, no DLQ.
-        Exhausted: enqueue DLQ via self._state when task_id is provided.
-        """
-        last_err: Exception | None = None
-        for attempt in range(max_retries + 1):
-            try:
-                await send_coroutine_fn()
-                return True
-            except Exception as e:  # noqa: BLE001 - telegram error surface is broad
-                last_err = e
-                err_name = type(e).__name__
-                if "InvalidToken" in err_name:
-                    return False
-                is_transient = (
-                    any(k in err_name for k in (
-                        "NetworkError", "TimedOut", "RetryAfter",
-                        "Timeout", "Network", "TimeoutError"))
-                    or isinstance(e, (TimeoutError, asyncio.TimeoutError))
-                )
-                # Unknown errors are retried as transient to survive flaky
-                # transports, except auth which already returned above.
-                _ = is_transient
-                if attempt >= max_retries:
-                    if task_id is not None and self._state is not None:
-                        enqueue = getattr(self._state, "enqueue_dead_letter", None)
-                        if callable(enqueue):
-                            try:
-                                enqueue(int(task_id), str(stage), str(content), str(e))
-                            except Exception:
-                                pass
-                    return False
-                await asyncio.sleep(base_delay * (2 ** attempt))
-        if last_err is not None and task_id is not None and self._state is not None:
-            enqueue = getattr(self._state, "enqueue_dead_letter", None)
-            if callable(enqueue):
-                try:
-                    enqueue(int(task_id), str(stage), str(content), str(last_err))
-                except Exception:
-                    pass
-        return False
-
-    def _log_event(self, event: str) -> None:
-        """Append a Telegram event to loop-engine/logs/telegram_events.log.
-
-        Debug telemetry (HOTFIX-03): opt-in ONLY via LOOP_ENGINE_DEBUG=1.
-        Never raises — telemetry must not affect gateway operation.
-        """
-        if os.environ.get("LOOP_ENGINE_DEBUG") != "1":
-            return
-        try:
-            log_dir = Path(__file__).resolve().parent / "logs"
-            log_dir.mkdir(parents=True, exist_ok=True)
-            with open(log_dir / "telegram_events.log", "a", encoding="utf-8") as f:
-                f.write(
-                    f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}Z] "
-                    f"{event}\n"
-                )
-        except Exception as e:
-            print(f"[gateway] debug telemetry log error: {e}")
-
-    def _get_bot(self):
-        """Lazy-init Telegram bot."""
-        if self._bot is None:
-            token = os.environ.get(self.config.approval.bot_token_env, "")
-            if not token:
-                raise ValueError(f"Env var {self.config.approval.bot_token_env} not set")
-            from telegram import Bot
-            self._bot = Bot(token=token)
-        return self._bot
-
-    async def _poll_loop(self):
-        """Poll Telegram for callback queries and text commands, dispatching to handlers.
-
-        Without this loop, inline Approve/Reject/Trigger buttons are dead UI.
-        Also parses /run, /start, /tasks, /backlog text commands.
-        Runs while any approval is pending or daemon is active.
-        """
-        offset = None
-        while self.pending or self._daemon is not None:
-            try:
-                updates = await self._bot.get_updates(offset=offset, timeout=10)
-            except Exception as e:
-                print(f"[gateway] Update poll error: {e}")
-                await asyncio.sleep(3)
-                continue
-            for u in updates:
-                offset = u.update_id + 1
-                cq = getattr(u, "callback_query", None)
-                if cq is not None and cq.data:
-                    cq_id = str(getattr(cq, "id", "") or "")
-                    # Dedup (HOTFIX-06): ignore duplicate clicks on the same
-                    # callback query id (double taps / Telegram re-delivery).
-                    if cq_id and cq_id in self._processed_callback_ids:
-                        continue
-                    # Instant acknowledgment (HOTFIX-06): answer BEFORE any
-                    # processing so Telegram never rejects the query as
-                    # "too old". The ack toast is intentionally skipped (a
-                    # second answer with text would be rejected by Telegram).
-                    try:
-                        await cq.answer()
-                    except Exception as e:
-                        print(f"[gateway] callback answer failed: {e}")
-                    if cq_id:
-                        self._processed_callback_ids.add(cq_id)
-                    self.handle_callback(cq.data)
-                    continue
-
-                # Text command parsing — contained so a network timeout in a
-                # handler never kills the poller loop (HOTFIX-06).
-                msg = getattr(u, "message", None)
-                if msg is not None and msg.text:
-                    try:
-                        await self._handle_text_command(msg)
-                    except Exception as e:
-                        print(f"[gateway] text command error: {e}")
-
-    def _ensure_poller(self):
-        """Start the update poller if it is not already running."""
-        if self._poller_task is None or self._poller_task.done():
-            self._poller_task = asyncio.get_running_loop().create_task(self._poll_loop())
-
-    async def request_approval(self, task_id: int, stage: str, content: str,
-                               message_thread_id: Optional[int] = None) -> bool:
-        """Send approval request with inline keyboard. Blocks until response."""
-        # Defensive string guard (HOTFIX-05): LLM/other callers may pass None or
-        # blank content — never let a NoneType reach len()/format paths.
-        content_str = str(content) if content is not None else ""
-        if not content_str.strip():
-            content_str = f"[{stage} for Task #{task_id}] (No text body provided)"
-        key = f"{task_id}:{stage}"
-
-        try:
-            bot = self._get_bot()
-            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
-
-            keyboard = InlineKeyboardMarkup([
-                [
-                    InlineKeyboardButton("Approve", callback_data=f"approve:{key}"),
-                    InlineKeyboardButton("Reject", callback_data=f"reject:{key}"),
-                ]
-            ])
-
-            if len(content_str) > 3000:
-                # Long plan/blueprint content (HOTFIX-02): inline text would be
-                # unreadable and hit Telegram's message cap. Send the FULL
-                # Markdown as a document attachment with a short summary caption
-                # plus the same Approve/Reject buttons.
-                tmp_path = Path(f"/tmp/plan_task_{task_id}.md")
-                send_method = "document"
-                tmp_path.write_text(content_str, encoding="utf-8")
-                try:
-                    # No parse_mode for the caption: keep it plain (consistent
-                    # with the inline path — LLM content breaks Markdown parsing).
-                    async def _send_doc():
-                        await bot.send_document(
-                            chat_id=self.config.approval.chat_id,
-                            document=str(tmp_path),
-                            caption=(
-                                f"{stage} — Task #{task_id} "
-                                f"(plan attached as file)\n\n"
-                                f"Approve or Reject?"
-                            ),
-                            reply_markup=keyboard,
-                            message_thread_id=message_thread_id,
-                        )
-                    ok = await self._send_with_retry(
-                        _send_doc, task_id=task_id, stage=stage, content=content_str)
-                    if not ok:
-                        return False
-                finally:
-                    tmp_path.unlink(missing_ok=True)
-            else:
-                send_method = "inline"
-                msg = (
-                    f"{stage} — Task #{task_id}\n\n"
-                    f"{content_str[:1500]}\n\n"
-                    f"Approve or Reject?"
-                )
-
-                # No parse_mode: LLM-generated content routinely breaks Markdown
-                # entity parsing, which would fail the whole approval request.
-                async def _send_msg():
-                    await bot.send_message(
-                        chat_id=self.config.approval.chat_id,
-                        text=msg,
-                        reply_markup=keyboard,
-                        message_thread_id=message_thread_id,
-                    )
-                ok = await self._send_with_retry(
-                    _send_msg, task_id=task_id, stage=stage, content=content_str)
-                if not ok:
-                    return False
-
-            self._log_event(
-                f"approval_request stage={stage!r} task={task_id} "
-                f"content_len={len(content_str)} via={send_method}")
-
-        except (ImportError, ValueError) as e:
-            print(f"[gateway] Telegram unavailable: {e}")
-            print(f"[gateway] SECURITY: Approval for task {task_id} DENIED (no auto-grant)")
-            return False
-
-        except Exception as e:
-            print(f"[gateway] Telegram error: {e}")
-            print(f"[gateway] SECURITY: Approval for task {task_id} DENIED (no auto-grant)")
-            if self._state is not None:
-                enqueue = getattr(self._state, "enqueue_dead_letter", None)
-                if callable(enqueue):
-                    try:
-                        enqueue(int(task_id), str(stage), str(content_str), str(e))
-                    except Exception:
-                        pass
-            return False
-
-        # Wait for Manager response
-        event = asyncio.Event()
-        self.pending[key] = event
-        self.results[key] = False  # default: rejected
-        self._ensure_poller()
-
-        try:
-            await asyncio.wait_for(event.wait(), timeout=self.config.approval.timeout_seconds)
-        except asyncio.TimeoutError:
-            print(f"[gateway] Approval timeout for task {task_id} ({stage})")
-            self.pending.pop(key, None)
-            return False
-
-        result = self.results.pop(key, False)
-        self.pending.pop(key, None)
-        return result
-
-    def handle_callback(self, callback_data: str) -> Optional[str]:
-        """Handle Telegram callback query. Returns acknowledgment message."""
-        self._log_event(f"callback_received data={callback_data!r}")
-        # --- Approval callbacks (existing) ---
-        if callback_data.startswith(("approve:", "reject:")):
-            action, key = callback_data.split(":", 1)
-            if key in self.pending:
-                if action == "approve":
-                    self.results[key] = True
-                    self.pending[key].set()
-                    return "Approved. Task will proceed."
-                else:
-                    self.results[key] = False
-                    self.pending[key].set()
-                    return "Rejected. Task will not proceed."
-            return None  # stale callback
-
-        # --- Trigger gate callbacks ---
-        if callback_data.startswith("trigger_task:"):
-            task_id = int(callback_data.split(":", 1)[1])
-            if self._daemon is not None:
-                asyncio.get_running_loop().create_task(
-                    self._daemon.trigger_task(task_id))
-                return f"🚀 Task #{task_id} triggered for execution."
-            return "Daemon not ready."
-
-        if callback_data.startswith("hold_task:"):
-            task_id = int(callback_data.split(":", 1)[1])
-            return f"⏸️ Task #{task_id} held. Use /run {task_id} when ready."
-
-        return None
-
-    # --- Task Entry Trigger Gate ---
-
-    async def send_task_trigger_card(self, task_id: int, title: str,
-                                     file_path: str,
-                                     message_thread_id: Optional[int] = None) -> bool:
-        """Send a Telegram message with [🚀 Start Execution] / [⏸️ Hold] buttons."""
-        try:
-            bot = self._get_bot()
-            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
-
-            keyboard = InlineKeyboardMarkup([
-                [
-                    InlineKeyboardButton(
-                        "🚀 Start Execution",
-                        callback_data=f"trigger_task:{task_id}"),
-                    InlineKeyboardButton(
-                        "⏸️ Hold",
-                        callback_data=f"hold_task:{task_id}"),
-                ]
-            ])
-
-            msg = (
-                f"📋 *Task [{task_id}] Staged for Review:* {title}\n"
-                f"_File: {file_path}_\n\n"
-                f"Edit or refine the task in backlog, then tap below when ready."
-            )
-
-            async def _send_card():
-                await bot.send_message(
-                    chat_id=self.config.approval.chat_id,
-                    text=msg,
-                    reply_markup=keyboard,
-                    message_thread_id=message_thread_id,
-                )
-            ok = await self._send_with_retry(
-                _send_card, task_id=task_id, stage="trigger",
-                content=f"{title} {file_path}")
-            if not ok:
-                return False
-            self._log_event(
-                f"trigger_card_sent task={task_id} title={title!r} file={file_path}")
-            return True
-
-        except (ImportError, ValueError) as e:
-            print(f"[gateway] Telegram unavailable for trigger card: {e}")
-            return False
-        except Exception as e:
-            self._log_event(f"trigger_card_error task={task_id} error={e!r}")
-            print(f"[gateway] Trigger card error: {e}")
-            return False
-
-    async def send_progress(self, task_id: int, message: str,
-                              message_thread_id: Optional[int] = None) -> bool:
-        """Send a brief real-time status update for a task to the Telegram chat.
-
-        Non-fatal by design: pipeline progress notifications must never crash
-        task processing, so every Telegram failure is logged and swallowed.
-        """
-        try:
-            bot = self._get_bot()
-            await bot.send_message(
-                chat_id=self.config.approval.chat_id,
-                text=f"⏳ Task #{task_id}: {message}",
-                message_thread_id=message_thread_id,
-            )
-            return True
-        except (ImportError, ValueError) as e:
-            print(f"[gateway] Telegram unavailable for progress: {e}")
-            return False
-        except Exception as e:
-            print(f"[gateway] Progress notification error: {e}")
-            return False
-
-    async def send_boot_scan_summary(self, tasks: list[dict], top_n: int = 4,
-                                       message_thread_id: Optional[int] = None) -> bool:
-        """Send ONE consolidated trigger summary for all pending backlog tasks.
-
-        Anti-flood replacement (HOTFIX-02) for the per-task trigger-card
-        fan-out during boot scans: lists every pending task in a single message
-        and attaches inline Start buttons for the top `top_n` tasks. Each task
-        record is expected to carry ``task_id`` and ``title``.
-        """
-        try:
-            bot = self._get_bot()
-            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
-
-            lines = [
-                f"📋 Boot Scan — {len(tasks)} task(s) awaiting trigger:"
-            ]
-            for t in tasks:
-                lines.append(f"  • #{t['task_id']} — {t.get('title', '')}")
-            lines.append("\nTap Start on a task to run it now.")
-
-            buttons = [
-                InlineKeyboardButton(
-                    f"🚀 #{t['task_id']} Start",
-                    callback_data=f"trigger_task:{t['task_id']}",
-                )
-                for t in tasks[:top_n]
-            ]
-            keyboard = InlineKeyboardMarkup([buttons]) if buttons else None
-
-            await bot.send_message(
-                chat_id=self.config.approval.chat_id,
-                text="\n".join(lines),
-                reply_markup=keyboard,
-                message_thread_id=message_thread_id,
-            )
-            self._log_event(
-                f"boot_summary_sent tasks={len(tasks)} "
-                f"ids={[t['task_id'] for t in tasks]} buttons={top_n}")
-            return True
-
-        except (ImportError, ValueError) as e:
-            print(f"[gateway] Telegram unavailable for boot scan summary: {e}")
-            return False
-        except Exception as e:
-            self._log_event(f"boot_summary_error tasks={len(tasks)} error={e!r}")
-            print(f"[gateway] Boot scan summary error: {e}")
-            return False
-
-    async def _handle_text_command(self, message) -> None:
-        """Parse /run, /start, /tasks, /backlog, /status text commands."""
-        text = message.text.strip()
-        chat_id = message.chat.id
-
-        if text.startswith(("/run ", "/start ")):
-            parts = text.split(maxsplit=1)
-            if len(parts) < 2:
-                await self._bot.send_message(
-                    chat_id=chat_id,
-                    text="Usage: /run <task_id>  or  /start <task_id>")
-                return
-            try:
-                task_id = int(parts[1].strip())
-            except ValueError:
-                await self._bot.send_message(
-                    chat_id=chat_id,
-                    text="Invalid task ID. Usage: /run <task_id>")
-                return
-            if self._daemon is not None:
-                asyncio.get_running_loop().create_task(
-                    self._daemon.trigger_task(task_id))
-                await self._bot.send_message(
-                    chat_id=chat_id,
-                    text=f"🚀 Triggering task #{task_id}...")
-            else:
-                await self._bot.send_message(
-                    chat_id=chat_id,
-                    text="Daemon not ready.")
-
-        elif text in ("/tasks", "/backlog"):
-            if self._state is None:
-                await self._bot.send_message(
-                    chat_id=chat_id,
-                    text="State machine not initialized.")
-                return
-            from models import TaskState
-            pending = self._state.get_pending_trigger_tasks()
-            if not pending:
-                await self._bot.send_message(
-                    chat_id=chat_id,
-                    text="No tasks in PENDING_TRIGGER status.")
-                return
-            lines = ["📋 *Tasks awaiting trigger:*\n"]
-            for t in pending:
-                lines.append(f"• #{t['task_id']} — {t['task_file']}")
-            await self._bot.send_message(
-                chat_id=chat_id,
-                text="\n".join(lines))
-
-        elif text == "/status":
-            # Status summary (HOTFIX-02): active tasks + pending-trigger tasks.
-            if self._state is None:
-                await self._bot.send_message(
-                    chat_id=chat_id,
-                    text="State machine not initialized.")
-                return
-            active = self._state.get_active_tasks()
-            pending = self._state.get_pending_trigger_tasks()
-            if not active and not pending:
-                await self._bot.send_message(
-                    chat_id=chat_id,
-                    text="📊 Status: no active tasks.")
-                return
-            lines = ["📊 Status Summary"]
-            lines.append(f"\n🔄 Active tasks ({len(active)}):")
-            for t in active:
-                lines.append(
-                    f"  • #{t['task_id']} — {t.get('state', '?')} — {t['task_file']}")
-            lines.append(f"\n⏸ Pending trigger ({len(pending)}):")
-            for t in pending:
-                lines.append(f"  • #{t['task_id']} — {t['task_file']}")
-            await self._bot.send_message(
-                chat_id=chat_id,
-                text="\n".join(lines))
diff --git a/loop-engine/healthcheck.py b/loop-engine/healthcheck.py
deleted file mode 100644
index 024b15f..0000000
--- a/loop-engine/healthcheck.py
+++ /dev/null
@@ -1,46 +0,0 @@
-"""
-Healthcheck probe (Task 148).
-
-Checks SQLite state DB connectivity, write latency, and process responsiveness.
-Exits 0 on healthy, 1 on error. Supports --dry-run.
-"""
-from __future__ import annotations
-
-import argparse
-import sqlite3
-import sys
-import time
-from pathlib import Path
-
-
-def check(db_path: str = "loop-engine/state/loop.db", dry_run: bool = False) -> bool:
-    if dry_run:
-        print("[healthcheck] dry-run OK")
-        return True
-    try:
-        p = Path(db_path)
-        p.parent.mkdir(parents=True, exist_ok=True)
-        start = time.time()
-        conn = sqlite3.connect(str(p), timeout=5)
-        try:
-            conn.execute("SELECT 1").fetchone()
-        finally:
-            conn.close()
-        latency = time.time() - start
-        print(f"[healthcheck] OK latency={latency:.3f}s db={db_path}")
-        return latency < 5.0
-    except Exception as e:  # noqa: BLE001
-        print(f"[healthcheck] FAIL: {e}", file=sys.stderr)
-        return False
-
-
-def main(argv: list[str] | None = None) -> int:
-    ap = argparse.ArgumentParser()
-    ap.add_argument("--dry-run", action="store_true")
-    ap.add_argument("--db", default="loop-engine/state/loop.db")
-    args = ap.parse_args(argv)
-    return 0 if check(args.db, dry_run=args.dry_run) else 1
-
-
-if __name__ == "__main__":
-    raise SystemExit(main())
diff --git a/loop-engine/loop-engine.jsonc b/loop-engine/loop-engine.jsonc
deleted file mode 100644
index 26f22f1..0000000
--- a/loop-engine/loop-engine.jsonc
+++ /dev/null
@@ -1,71 +0,0 @@
-{
-  // مدل پیش‌فرض: DeepSeek V4 Flash (سریع، ارزان و قدرتمند)
-  "default_provider": "openrouter/deepseek/deepseek-v4-flash-0731",
-
-  // روتینگ مدل‌های نسل جدید ۲۰۲۶ از درگاه OpenRouter
-  "categories": {
-    "quick": {
-      "models": [
-        "openrouter/deepseek/deepseek-v4-flash-0731",
-        "openrouter/qwen/qwen3.7-flash",
-        "openrouter/z-ai/glm-5.3-flash"
-      ],
-      "description": "Ultra-cheap, fast single-file edits, typos, and formatting"
-    },
-    "deep": {
-      "models": [
-        "openrouter/google/gemini-3.7-flash",
-        "openrouter/z-ai/glm-5.3-flash",
-        "openrouter/deepseek/deepseek-v4-flash-0731"
-      ],
-      "reasoning": "medium",
-      "description": "High-reasoning architecture, planning, and QA review"
-    },
-    "visual": {
-      "models": [
-        "openrouter/google/gemini-3.7-flash",
-        "openrouter/qwen/qwen3.7-flash"
-      ],
-      "description": "Frontend, UI/UX, and multimodal validation"
-    },
-    "unspecified": {
-      "models": [
-        "openrouter/deepseek/deepseek-v4-flash-0731",
-        "openrouter/google/gemini-3.7-flash"
-      ],
-      "description": "Default fallback tier"
-    }
-  },
-
-  // محدودیت هم‌زمانی درخواست‌ها
-  "provider_concurrency": {
-    "openrouter": 10,
-    "google": 5,
-    "deepseek": 5,
-    "qwen": 5,
-    "z-ai": 5,
-    "opencode": 10
-  },
-
-  // تنظیمات ربات تلگرام و Chat ID شما
-  "approval": {
-    "bot_token_env": "TELEGRAM_BOT_TOKEN",
-    "chat_id": 1247026399,
-    "timeout_seconds": 3600
-  },
-
-  "max_parallel_tasks": 1,
-  "max_qa_retries": 3,
-  "evidence_dir": "loop-engine/evidence",
-
-  // حالت شروع با تایید در تلگرام
-  "trigger_mode": "telegram_button",
-  "auto_start_on_boot": false,
-
-  "system_prompt_path": "system-prompt.md",
-  "tasks_dir": "tasks",
-  "agmd_path": "AGENTS.md",
-  "conventions_path": "docs/conventions.md",
-  "stacks_dir": "stacks",
-  "default_stack": "generic"
-}
diff --git a/loop-engine/metrics.py b/loop-engine/metrics.py
deleted file mode 100644
index b76b272..0000000
--- a/loop-engine/metrics.py
+++ /dev/null
@@ -1,104 +0,0 @@
-"""
-Structured Metrics, Token Cost Tracking & Error Logging (Task 146).
-"""
-
-from __future__ import annotations
-
-import json
-import logging
-import time
-from typing import Optional
-
-
-PROMPT_COST_PER_1K = 0.0015
-COMPLETION_COST_PER_1K = 0.002
-
-
-class MetricsCollector:
-    """In-memory per-task metrics with global summary."""
-
-    def __init__(self) -> None:
-        self._tasks: dict[int, dict] = {}
-
-    def _ensure(self, task_id: int) -> dict:
-        entry = self._tasks.get(int(task_id))
-        if entry is None:
-            entry = {
-                "prompt_tokens": 0,
-                "completion_tokens": 0,
-                "estimated_cost": 0.0,
-                "stages": {},
-                "errors": [],
-                "llm_calls": 0,
-            }
-            self._tasks[int(task_id)] = entry
-        return entry
-
-    def record_llm_call(self, task_id: int, model: str, prompt_tokens: int,
-                        completion_tokens: int, duration_seconds: float) -> None:
-        entry = self._ensure(task_id)
-        entry["prompt_tokens"] += int(prompt_tokens)
-        entry["completion_tokens"] += int(completion_tokens)
-        entry["llm_calls"] += 1
-        cost = (int(prompt_tokens) / 1000.0) * PROMPT_COST_PER_1K + \
-               (int(completion_tokens) / 1000.0) * COMPLETION_COST_PER_1K
-        entry["estimated_cost"] += cost
-        entry.setdefault("models", {})
-        entry["models"][model] = entry["models"].get(model, 0) + 1
-        entry["last_duration_seconds"] = float(duration_seconds)
-
-    def record_stage_duration(self, task_id: int, stage: str, duration_seconds: float) -> None:
-        entry = self._ensure(task_id)
-        entry["stages"][str(stage)] = float(duration_seconds)
-
-    def record_error(self, task_id: int, stage: str, error: str) -> None:
-        entry = self._ensure(task_id)
-        entry["errors"].append({"stage": str(stage), "error": str(error)})
-
-    def get_task_metrics(self, task_id: int) -> dict:
-        entry = self._ensure(task_id)
-        return dict(entry)
-
-    def get_summary(self) -> dict:
-        total_tasks = len(self._tasks)
-        total_prompt = sum(v["prompt_tokens"] for v in self._tasks.values())
-        total_completion = sum(v["completion_tokens"] for v in self._tasks.values())
-        total_cost = sum(v["estimated_cost"] for v in self._tasks.values())
-        total_errors = sum(len(v["errors"]) for v in self._tasks.values())
-        return {
-            "total_tasks": total_tasks,
-            "total_prompt_tokens": total_prompt,
-            "total_completion_tokens": total_completion,
-            "total_estimated_cost": total_cost,
-            "total_errors": total_errors,
-        }
-
-
-class JSONLogFormatter(logging.Formatter):
-    """Emits structured JSON log lines."""
-
-    def format(self, record: logging.LogRecord) -> str:
-        payload = {
-            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
-            "level": record.levelname,
-            "logger": record.name,
-            "event": record.getMessage(),
-            "task_id": getattr(record, "task_id", None),
-            "duration_ms": getattr(record, "duration_ms", None),
-        }
-        return json.dumps(payload)
-
-
-def init_sentry(sentry_dsn: Optional[str]) -> bool:
-    """Gracefully init Sentry if installed and DSN provided."""
-    if not sentry_dsn:
-        return False
-    try:
-        import sentry_sdk  # type: ignore
-    except ImportError:
-        return False
-    try:
-        sentry_sdk.init(dsn=sentry_dsn)
-        return True
-    except Exception:
-        return False
diff --git a/loop-engine/models.py b/loop-engine/models.py
deleted file mode 100644
index 920ef43..0000000
--- a/loop-engine/models.py
+++ /dev/null
@@ -1,416 +0,0 @@
-"""
-Pydantic models for the Cognitive Loop Engine.
-
-Validates all configuration and runtime data structures.
-Inspired by OMO's Zod schema system (36 schema files) but using Pydantic for Python.
-"""
-
-from __future__ import annotations
-
-from enum import Enum
-from typing import Literal, Optional
-from pydantic import AliasChoices, BaseModel, Field
-
-
-# --- Enums ---
-
-class TaskState(str, Enum):
-    """Pipeline states for a task. Mirrors the state machine in AGENTS.md."""
-    BACKLOG = "backlog"
-    PENDING_TRIGGER = "pending_trigger"
-    PLANNING = "planning"
-    AWAITING_APPROVAL = "awaiting_approval"
-    IMPLEMENTING = "implementing"
-    QA = "qa"
-    REVIEW = "review"
-    AWAITING_CLOSURE = "awaiting_closure"
-    CLOSED = "closed"
-    QA_REJECTED = "qa_rejected"
-    CRASHED = "crashed"
-    ABORTED = "aborted"
-
-
-class ProviderPriority(BaseModel):
-    """Priority-ordered model chain for a category."""
-    models: list[str] = Field(..., min_length=1, description="Ordered fallback models: provider/model")
-    reasoning: Optional[str] = Field(None, description="Reasoning level override")
-
-
-class CategoryConfig(BaseModel):
-    """Category-based model routing — ported from OMO's visual-engineering/deep/quick/ultrabrain."""
-    models: list[str] = Field(..., min_length=1)
-    reasoning: Optional[str] = None
-    description: Optional[str] = None
-
-
-class ProviderConcurrency(BaseModel):
-    """Max concurrent requests per provider — prevents cost spiral."""
-    anthropic: int = 3
-    openai: int = 3
-    opencode: int = 10
-    zai: int = 10
-    kimi: int = 5
-
-
-class ApprovalConfig(BaseModel):
-    """Telegram approval gateway settings."""
-    bot_token_env: str = Field("TELEGRAM_BOT_TOKEN", description="Env var name for bot token")
-    chat_id: int = Field(..., description="Telegram chat ID for Manager")
-    timeout_seconds: int = 3600  # 1 hour to respond
-
-
-class IdleConfig(BaseModel):
-    """Auto-continue settings — inspired by OpenCode Goal Plugin's no-progress detection."""
-    thinking_timeout_seconds: int = 60  # Phase 1: thinking (no bash running)
-    executing_timeout_seconds: int = 900  # Phase 2: bash running (15 min)
-    max_retries: int = 5
-    no_progress_threshold: int = 50  # token threshold for no-progress
-    no_progress_turns_before_pause: int = 2
-    min_delay_seconds: float = 2.0  # cooldown between continue attempts
-
-
-class StackDetectionConfig(BaseModel):
-    """Heuristics for auto-detecting a stack profile."""
-    marker_files: list[str] = Field(default_factory=list, description="Files whose presence implies this stack")
-    extensions: list[str] = Field(default_factory=list, description="File extensions implying this stack (e.g. .py)")
-    task_keywords: list[str] = Field(default_factory=list, description="Keywords in task content implying this stack")
-
-
-class StackToolchainConfig(BaseModel):
-    """Toolchain commands for a stack."""
-    test_cmd: str | None = Field(None, description="Command to run tests for this stack")
-    build_cmd: str | None = Field(None, description="Command to build this stack")
-    lint_cmd: str | None = Field(None, description="Command to lint this stack")
-
-
-class StackProfileConfig(BaseModel):
-    """Declarative profile for a tech stack."""
-    name: str = Field(..., description="Canonical stack name (matches filename without extension)")
-    display_name: str = Field(..., description="Human-readable name")
-    detection: StackDetectionConfig = Field(default_factory=StackDetectionConfig)
-    skills: list[str] = Field(default_factory=list, description="Skill names to load for this stack")
-    preflight: list[str] = Field(default_factory=list, description="Shell commands to validate toolchain before execution")
-    toolchain: StackToolchainConfig = Field(default_factory=StackToolchainConfig)
-    model_preferences: dict[str, list[str]] = Field(default_factory=dict, description="Optional per-category model overrides")
-
-
-class DownstreamTaskTemplate(BaseModel):
-    """Template for a downstream task generated by the Contract Propagation Engine (LE-6).
-
-    The ``title_template`` and ``goal_template`` support ``{contract_name}``,
-    ``{triggering_task_id}``, and (goal only) ``{files}`` format placeholders.
-    """
-    title_template: str = Field(..., description="Template for downstream task title, e.g. 'Sync TypeScript SDK with updated {contract_name}'")
-    stack: str = Field("generic", description="Stack profile for the downstream task, e.g. 'node-ts', 'kotlin-android'")
-    goal_template: str = Field(..., description="Template for task goal")
-    acceptance_criteria: list[str] = Field(default_factory=list, description="Standard AC checkboxes for the task")
-
-
-class ContractRuleConfig(BaseModel):
-    """Declarative contract mutation rule — maps contract file globs to downstream tasks."""
-    name: str = Field(..., description="Canonical rule name, e.g. 'shared-schema', 'openapi-spec'")
-    patterns: list[str] = Field(default_factory=list, description="Glob patterns for contract files, e.g. ['packages/shared-schema/**', 'openapi/**']")
-    downstream_tasks: list[DownstreamTaskTemplate] = Field(default_factory=list, description="List of tasks to generate upon mutation")
-
-
-def _default_contract_rules() -> list["ContractRuleConfig"]:
-    """Sensible default contract propagation rules (LE-6)."""
-    return [
-        ContractRuleConfig(
-            name="openapi-spec",
-            patterns=["openapi/**", "contracts/*.yaml", "contracts/*.json"],
-            downstream_tasks=[
-                DownstreamTaskTemplate(
-                    title_template="Regenerate API client for updated {contract_name}",
-                    stack="node-ts",
-                    goal_template="Regenerate the API client / SDK to match the modified {contract_name} contract. Files changed: {files}",
-                    acceptance_criteria=[
-                        "API client regenerated from the modified OpenAPI specification",
-                        "Generated types match the new contract shapes",
-                        "Build and lint pass for the generated client",
-                    ],
-                )
-            ],
-        ),
-        ContractRuleConfig(
-            name="prisma-schema",
-            patterns=["*.prisma", "prisma/**"],
-            downstream_tasks=[
-                DownstreamTaskTemplate(
-                    title_template="Sync Prisma schema migration for {contract_name}",
-                    stack="node-ts",
-                    goal_template="Generate and apply the Prisma migration matching the modified {contract_name}. Files changed: {files}",
-                    acceptance_criteria=[
-                        "Prisma migration generated from the updated schema",
-                        "Migration applies cleanly against the development database",
-                    ],
-                )
-            ],
-        ),
-        ContractRuleConfig(
-            name="protobuf",
-            patterns=["proto/**", "*.proto"],
-            downstream_tasks=[
-                DownstreamTaskTemplate(
-                    title_template="Regenerate gRPC stubs for updated {contract_name}",
-                    stack="generic",
-                    goal_template="Regenerate the gRPC/protobuf stubs for the modified {contract_name} contract. Files changed: {files}",
-                    acceptance_criteria=[
-                        "gRPC stubs regenerated for all target languages",
-                        "Server and client packages compile against the new stubs",
-                    ],
-                )
-            ],
-        ),
-        ContractRuleConfig(
-            name="shared-schema",
-            patterns=["packages/shared-schema/**", "shared/schemas/**"],
-            downstream_tasks=[
-                DownstreamTaskTemplate(
-                    title_template="Propagate shared schema changes for {contract_name}",
-                    stack="generic",
-                    goal_template="Propagate the modified {contract_name} to all consuming services. Files changed: {files}",
-                    acceptance_criteria=[
-                        "All consumers of the shared schema are updated",
-                        "Cross-service contract tests pass",
-                    ],
-                )
-            ],
-        ),
-    ]
-
-
-class SpecArtifactType(str, Enum):
-    """Spec artifact kinds governed by the Spec-First Gate (LE-8)."""
-    ADR = "adr"
-    PRD = "prd"
-    CONTRACT = "contract"
-    DATA_MODEL = "data_model"
-
-
-class SpecRequirementRule(BaseModel):
-    """Declarative spec requirement rule — maps triggering keywords to required artifacts.
-
-    A rule fires when any ``keywords`` substring appears in the (lowercased) task
-    content or approved plan. When fired, the Spec-First Gate (LE-8) requires at
-    least one matching artifact under ``target_directories`` to exist in the
-    workspace or staged diff before implementation may proceed.
-    """
-    name: str = Field(..., description="Rule name, e.g. 'architecture-decision', 'api-contract'")
-    keywords: list[str] = Field(default_factory=list, description="Keywords in task or plan triggering this spec requirement")
-    required_artifacts: list[SpecArtifactType] = Field(default_factory=list, description="Artifact types required by this rule")
-    target_directories: list[str] = Field(default_factory=list, description="Directory globs where artifacts are expected, e.g. ['docs/adr/**', 'contracts/**']")
-
-
-class SpecGateConfig(BaseModel):
-    """Spec-First Gate configuration (LE-8)."""
-    enabled: bool = Field(True, description="Whether the spec-first gate is enforced")
-    rules: list[SpecRequirementRule] = Field(default_factory=list, description="Configured spec requirement rules")
-
-
-class ProjectTopicConfig(BaseModel):
-    """Multi-project forum topic mapping (Task 143)."""
-    topic_id: int = Field(..., description="Telegram forum topic ID")
-    project_name: str = Field(..., description="Name of the project")
-    workspace_root: str = Field(..., description="Relative or absolute path to project workspace")
-    target_hashtags: list[str] = Field(default_factory=lambda: ["bug", "feature"], description="Hashtags mapped to this project")
-
-
-def _default_spec_rules() -> list[SpecRequirementRule]:
-    """Sensible default spec requirement rules (LE-8).
-
-    Kept as a free function (mirroring ``_default_contract_rules``) so callers can
-    wire the defaults explicitly into ``SpecGateConfig.rules`` — the schema default
-    is an empty list so the gate is inert until configured.
-    """
-    return [
-        SpecRequirementRule(
-            name="architecture-decision",
-            keywords=["architecture", "architectural", "redesign", "adr"],
-            required_artifacts=[SpecArtifactType.ADR],
-            target_directories=["docs/adr/**", "docs/architecture.md"],
-        ),
-        SpecRequirementRule(
-            name="api-contract",
-            keywords=["api contract", "openapi", "new endpoint", "graphql schema", "grpc proto"],
-            required_artifacts=[SpecArtifactType.CONTRACT],
-            target_directories=["contracts/**", "openapi/**", "proto/**"],
-        ),
-        SpecRequirementRule(
-            name="database-schema",
-            keywords=["database schema", "prisma migration", "sql migration", "new table", "data model"],
-            required_artifacts=[SpecArtifactType.DATA_MODEL],
-            target_directories=["docs/data_model.md", "prisma/**", "migrations/**"],
-        ),
-    ]
-
-
-class LoopEngineConfig(BaseModel):
-    """Root configuration — loop-engine.jsonc."""
-    # Providers
-    default_provider: str = "gemini/gemini-2.5-flash"
-    categories: dict[str, CategoryConfig] = Field(default_factory=lambda: {
-        "quick": CategoryConfig(
-            models=["kimi/kimi-k3"],
-            description="Single-file changes, typos, quick fixes"
-        ),
-        "deep": CategoryConfig(
-            models=["openai/gpt-5.6-sol", "gemini/gemini-2.5-pro"],
-            reasoning="medium",
-            description="Autonomous research + execution"
-        ),
-        "visual": CategoryConfig(
-            models=["anthropic/claude-opus-5", "kimi/kimi-k3"],
-            reasoning="max",
-            description="Frontend, UI/UX, design"
-        ),
-        "unspecified": CategoryConfig(
-            models=["gemini/gemini-2.5-flash", "kimi/kimi-k3"],
-            description="Default — anything not matched"
-        ),
-    })
-    provider_concurrency: ProviderConcurrency = Field(default_factory=ProviderConcurrency)
-
-    # Executor
-    max_parallel_tasks: int = Field(1, ge=1, le=4, description="Max concurrent Hands sessions")
-    idle: IdleConfig = Field(default_factory=IdleConfig)
-
-    # Approval
-    approval: ApprovalConfig
-
-    # QA
-    max_qa_retries: int = Field(3, ge=1, le=10)
-    evidence_dir: str = "loop-engine/evidence"
-
-    # Task Entry Trigger Gate
-    trigger_mode: Literal["telegram_button", "command_only", "auto"] = Field(
-        "telegram_button",
-        description="How tasks enter the execution loop: "
-                    "'telegram_button' = admin taps Start in Telegram; "
-                    "'command_only' = admin runs /run <id>; "
-                    "'auto' = legacy auto-pickup on file detection."
-    )
-    auto_start_on_boot: bool = Field(
-        False,
-        description="If True, existing backlog tasks run immediately on daemon boot. "
-                    "If False, they are registered as PENDING_TRIGGER and await admin action."
-    )
-
-    # Paths
-    system_prompt_path: str = "system-prompt.md"
-    tasks_dir: str = "tasks"
-    agmd_path: str = "AGENTS.md"
-    conventions_path: str = "docs/conventions.md"
-
-    # Stack Profiles
-    stacks_dir: str = Field("stacks", description="Directory containing stack profile YAML/JSON definitions")
-    default_stack: str = Field("generic", description="Fallback stack when detection finds no match")
-
-    # Contract Propagation (LE-6)
-    contract_rules: list[ContractRuleConfig] = Field(
-        default_factory=_default_contract_rules,
-        description="Declarative rules mapping contract file mutations to downstream task generators",
-    )
-
-    # Spec-First Artifact Gate (LE-8)
-    spec_gate: SpecGateConfig = Field(
-        default_factory=SpecGateConfig,
-        description="Spec-first artifact governance: fail-fast gate requiring spec artifacts before implementation",
-    )
-
-    # Blast-Radius Analyzer (LE-9)
-    blast_radius: "BlastRadiusConfig" = Field(
-        default_factory=lambda: BlastRadiusConfig(),
-        description="Monorepo blast-radius verification scoping",
-    )
-
-    # Multi-Project Topic Routing (Task 143)
-    multi_project: list[ProjectTopicConfig] = Field(
-        default_factory=list,
-        description="Multi-project forum topic mappings",
-    )
-
-
-# --- Blast-Radius Analyzer (LE-9 / Task 141) ---
-
-
-class PackageInfo(BaseModel):
-    """A discovered monorepo package/workspace.
-
-    ``path`` is the package directory relative to the workspace root (posix,
-    ``"."`` for the root package itself when the root carries a manifest).
-    """
-
-    name: str = Field(..., description="Package name from its manifest, or the relative path when unnamed")
-    path: str = Field(..., description="Package directory relative to workspace root (posix), '.' for the root package")
-    manifest: str = Field(..., description="Manifest filename that defined the package, e.g. 'package.json'")
-
-
-class PackageDependency(BaseModel):
-    """One discovered package plus the local packages it depends on (LE-9).
-
-    Supports both spec naming (name/dependencies) and legacy naming (package/depends_on)
-    via aliases for backward compatibility with existing tests.
-    """
-
-    model_config = {"populate_by_name": True}
-
-    name: str = Field(
-        ..., description="Package name from manifest", validation_alias=AliasChoices("name", "package")
-    )
-    path: str = Field(..., description="Relative directory path to package root")
-    dependencies: list[str] = Field(
-        default_factory=list,
-        description="List of internal package dependencies",
-        validation_alias=AliasChoices("dependencies", "depends_on"),
-    )
-
-    # Legacy aliases for backward compat — populated via validation_alias above
-    # Provide properties so both access patterns work
-    @property
-    def package(self) -> str:
-        return self.name
-
-    @property
-    def depends_on(self) -> list[str]:
-        return self.dependencies
-
-    @package.setter
-    def package(self, value: str) -> None:
-        self.name = value
-
-    @depends_on.setter
-    def depends_on(self, value: list[str]) -> None:
-        self.dependencies = value
-
-
-class BlastRadiusMatrix(BaseModel):
-    """Result of ``calculate_affected_paths`` — the affected dependency matrix.
-
-    ``affected_packages``/``affected_paths`` include the directly modified
-    packages PLUS every package that transitively depends on them (reverse
-    dependency closure). ``unaffected_packages`` are the discovered packages
-    with no path to any modified file. ``root_owned_files`` are modified files
-    that belong to no discovered package (repo-root configs, docs, etc.).
-    """
-
-    modified_files: list[str] = Field(default_factory=list, description="Normalized modified file paths analyzed")
-    packages: list[PackageInfo] = Field(default_factory=list, description="All discovered monorepo packages")
-    dependency_map: list[PackageDependency] = Field(default_factory=list, description="Local dependency edges per package")
-    affected_packages: list[str] = Field(default_factory=list, description="Topologically ordered affected package names")
-    affected_paths: list[str] = Field(default_factory=list, description="Relative paths of affected packages")
-    unaffected_packages: list[str] = Field(default_factory=list, description="Packages unaffected by changes")
-    root_owned_files: list[str] = Field(default_factory=list, description="Modified files not owned by any package")
-    is_monorepo: bool = Field(False, description="True if workspace contains multiple packages")
-    is_empty: bool = Field(False, description="True if monorepo changes affect zero packages")
-
-
-class BlastRadiusConfig(BaseModel):
-    """Blast-radius verification scoping configuration (LE-9)."""
-
-    enabled: bool = Field(True, description="Enable blast-radius verification scoping")
-    workspace_globs: list[str] = Field(
-        default_factory=lambda: ["packages/*", "apps/*", "services/*", "modules/*", "libs/*"],
-        description="Glob patterns for workspace discovery",
-    )
-    conservative_root_fallback: bool = Field(True, description="Mark all packages affected if root files change")
diff --git a/loop-engine/multi_project.py b/loop-engine/multi_project.py
deleted file mode 100644
index fc49cae..0000000
--- a/loop-engine/multi_project.py
+++ /dev/null
@@ -1,54 +0,0 @@
-"""
-Multi-Project Router (Task 143).
-
-Maps Telegram forum topic IDs to isolated project workspaces.
-Single supergroup manages multiple distinct repositories via topic threads.
-"""
-
-from __future__ import annotations
-
-from pathlib import Path
-
-
-class MultiProjectRouter:
-    """Routes topic IDs <-> workspace roots <-> task paths."""
-
-    def __init__(self, mappings) -> None:
-        self._mappings = list(mappings or [])
-        self._by_topic: dict[int, object] = {m.topic_id: m for m in self._mappings}
-
-    def get_workspace_for_topic(self, topic_id: int) -> Path | None:
-        m = self._by_topic.get(int(topic_id))
-        if m is None:
-            return None
-        return Path(m.workspace_root)
-
-    def get_topic_for_workspace(self, workspace_path: str | Path) -> int | None:
-        target = str(workspace_path)
-        for m in self._mappings:
-            if str(m.workspace_root) == target:
-                return int(m.topic_id)
-            # Allow relative/absolute equivalence via normalized suffix match
-            try:
-                if Path(target).resolve() == Path(m.workspace_root).resolve():
-                    return int(m.topic_id)
-            except Exception:
-                continue
-        return None
-
-    def get_topic_for_task(self, task_file: str | Path) -> int | None:
-        task_str = str(task_file)
-        best: tuple[int, int] | None = None  # (match_len, topic_id)
-        for m in self._mappings:
-            root = str(m.workspace_root)
-            if root and root in task_str:
-                cand = (len(root), int(m.topic_id))
-                if best is None or cand[0] > best[0]:
-                    best = cand
-        if best is not None:
-            return best[1]
-        return None
-
-    def get_project_name(self, topic_id: int) -> str | None:
-        m = self._by_topic.get(int(topic_id))
-        return m.project_name if m is not None else None
diff --git a/loop-engine/personas.py b/loop-engine/personas.py
deleted file mode 100644
index bd3e9c5..0000000
--- a/loop-engine/personas.py
+++ /dev/null
@@ -1,70 +0,0 @@
-"""
-Runtime Persona Loader — derives ALL personas from the Manager's prompt fragments.
-
-Single source of truth: prompts/fragments/*.md (compiled into system-prompt.md).
-Editing a fragment changes engine behavior on next start — no code edits needed.
-
-Parses:
-- 06-personas.md            → operational personas (<trigger>/<duty>/<behavior>)
-- 12-brainstorming_protocol.md → six swarm personas (<focus>/<output>) + output schema
-"""
-
-import re
-from pathlib import Path
-
-PERSONAS_FRAGMENT = "prompts/fragments/06-personas.md"
-BRAINSTORM_FRAGMENT = "prompts/fragments/12-brainstorming_protocol.md"
-
-_PERSONA_RE = re.compile(r'<persona\s+name="([^"]+)">\s*(.*?)</persona>', re.DOTALL)
-
-# Repo root = parent of loop-engine/ — fallback anchor so fragment loading
-# works regardless of the process CWD (same class of fix as daemon REPO_ROOT).
-_REPO_ROOT = Path(__file__).resolve().parent.parent
-
-
-def _read(root: Path, rel: str) -> str:
-    p = root / rel
-    if not p.exists():
-        p = _REPO_ROOT / rel
-    if not p.exists():
-        return ""
-    return p.read_text(encoding="utf-8")
-
-
-def _tag(block: str, tag_name: str) -> str:
-    m = re.search(rf"<{tag_name}>(.*?)</{tag_name}>", block, re.DOTALL)
-    return m.group(1).strip() if m else ""
-
-
-def load_personas(workspace_root: str = ".") -> dict[str, dict]:
-    """Load operational personas: {name: {trigger, duty, behavior}}."""
-    raw = _read(Path(workspace_root), PERSONAS_FRAGMENT)
-    personas: dict[str, dict] = {}
-    for name, block in _PERSONA_RE.findall(raw):
-        personas[name] = {
-            "name": name,
-            "trigger": _tag(block, "trigger"),
-            "duty": _tag(block, "duty"),
-            "behavior": _tag(block, "behavior"),
-        }
-    return personas
-
-
-def load_swarm_personas(workspace_root: str = ".") -> dict[str, dict]:
-    """Load brainstorming swarm personas: {name: {focus, output}}."""
-    raw = _read(Path(workspace_root), BRAINSTORM_FRAGMENT)
-    swarm: dict[str, dict] = {}
-    for name, block in _PERSONA_RE.findall(raw):
-        swarm[name] = {
-            "name": name,
-            "focus": _tag(block, "focus"),
-            "output": _tag(block, "output"),
-        }
-    return swarm
-
-
-def load_brainstorm_schema(workspace_root: str = ".") -> str:
-    """Return the verbatim <brainstorming_session> output schema block."""
-    raw = _read(Path(workspace_root), BRAINSTORM_FRAGMENT)
-    m = re.search(r"<output_schema>(.*?)</output_schema>", raw, re.DOTALL)
-    return m.group(1).strip() if m else ""
diff --git a/loop-engine/pyproject.toml b/loop-engine/pyproject.toml
deleted file mode 100644
index 69a4058..0000000
--- a/loop-engine/pyproject.toml
+++ /dev/null
@@ -1,32 +0,0 @@
-[project]
-name = "cognitive-loop-engine"
-version = "0.1.0"
-description = "Automated Brain↔Hands orchestration daemon for Cognitive Lead AI HQ"
-requires-python = ">=3.12"
-dependencies = [
-    "pydantic>=2.0",
-    "litellm>=1.0",
-    "watchdog>=4.0",
-    "python-telegram-bot>=21.0",
-    "pyyaml>=6.0",
-]
-
-[project.optional-dependencies]
-dev = [
-    "pytest>=8.0",
-]
-
-[build-system]
-requires = ["hatchling"]
-build-backend = "hatchling.build"
-
-# Flat scripts layout (no import package) — bypass hatchling auto-detection.
-[tool.hatch.build.targets.wheel]
-bypass-selection = true
-
-# Lint config: target the project's declared Python so ruff classifies stdlib
-# modules correctly (e.g. tomllib is stdlib since 3.11) under the default rule
-# set (`ruff check .`). No rule overrides — new code should follow the
-# repository conventions (defensive manifest-parsing guards allowed).
-[tool.ruff]
-target-version = "py312"
diff --git a/loop-engine/qa_engine.py b/loop-engine/qa_engine.py
deleted file mode 100644
index 971fde6..0000000
--- a/loop-engine/qa_engine.py
+++ /dev/null
@@ -1,106 +0,0 @@
-"""
-QA Loop Engine v2 — evidence-bound review with trace sanitization.
-
-Inspired by OMO's evidence rule: no evidence = no commit.
-Writes to loop-engine/evidence/<task-id>/.
-"""
-
-import re
-import time
-from pathlib import Path
-from typing import Any, Optional
-
-from models import LoopEngineConfig, TaskState
-from state import StateMachine
-from router import LLMRouter
-
-# Decision tokens — aligned with the Manager's persona definitions
-# (06-personas.md): QA Engineer emits QA_PASSED/QA_REJECTED, Code Reviewer
-# emits APPROVED/APPROVED_WITH_CHANGES/REJECTED_NEEDS_FIXES/PO_REVIEW_PENDING.
-# Engine shorthand (PASSED/FAILED/READY_FOR_CLOSURE/NEEDS_WORK) stays accepted.
-# First occurrence in the report wins: naive substring matching false-positives
-# when a FAILED report quotes acceptance criteria like "tests must be approved".
-_PASS_RE = re.compile(
-    r"\b(QA_PASSED|PASSED|APPROVED_WITH_CHANGES|APPROVED|PO_REVIEW_PENDING|READY_FOR_CLOSURE)\b")
-_FAIL_RE = re.compile(
-    r"\b(QA_REJECTED|REJECTED_NEEDS_FIXES|FAILED|REJECTED|NEEDS_WORK)\b")
-
-
-def decide(report: str, default: str = "FAIL") -> str:
-    """Return PASS-side or FAIL-side verdict based on first match in report."""
-    p = _PASS_RE.search(report.upper())
-    f = _FAIL_RE.search(report.upper())
-    if p and (not f or p.start() < f.start()):
-        return "PASS"
-    if f:
-        return "FAIL"
-    return default
-
-
-class QAEngine:
-    """Runs QA and Code Review via LLM, writes evidence."""
-
-    def __init__(self, config: LoopEngineConfig, state: StateMachine, router: LLMRouter):
-        self.config = config
-        self.state = state
-        self.router = router
-        self.evidence_dir = Path(config.evidence_dir)
-
-    def run_qa(self, task_id: int, task_content: str, diff: str = "",
-               toolchain_evidence: str = "",
-               stack_profile: Optional[Any] = None) -> dict:
-        """Run QA Engineer review. Returns PASSED or FAILED."""
-        self.evidence_dir.mkdir(parents=True, exist_ok=True)
-        evidence_path = self.evidence_dir / f"{task_id}"
-        evidence_path.mkdir(exist_ok=True)
-
-        try:
-            routing = self.router.route_qa(
-                task_content, diff, toolchain_evidence=toolchain_evidence,
-                stack_profile=stack_profile)
-        except TypeError:
-            # Fallback for legacy routers/stubs without stack_profile param
-            try:
-                routing = self.router.route_qa(
-                    task_content, diff, toolchain_evidence=toolchain_evidence)
-            except TypeError:
-                # Fallback for legacy routers/stubs without toolchain_evidence param
-                routing = self.router.route_qa(task_content, diff)
-        qa_report = self.router.call_llm(routing)
-
-        # Write evidence
-        (evidence_path / "qa_report.md").write_text(qa_report, encoding="utf-8")
-
-        # Determine result
-        if decide(qa_report) == "PASS":
-            result = "PASSED"
-        else:
-            result = "FAILED"
-            self.state.set_qa_feedback(task_id, qa_report)
-
-        (evidence_path / "result.txt").write_text(result, encoding="utf-8")
-        return {"result": result, "report": qa_report, "evidence_dir": str(evidence_path)}
-
-    def run_review(self, task_id: int, task_content: str, qa_report: str = "",
-                   stack_profile: Optional[Any] = None) -> dict:
-        """Run Code Reviewer. Returns APPROVED or REJECTED."""
-        evidence_path = self.evidence_dir / f"{task_id}"
-        evidence_path.mkdir(parents=True, exist_ok=True)
-
-        try:
-            routing = self.router.route_review(
-                task_content, qa_report, stack_profile=stack_profile)
-        except TypeError:
-            # Fallback for legacy routers/stubs without stack_profile param
-            routing = self.router.route_review(task_content, qa_report)
-        review = self.router.call_llm(routing)
-
-        (evidence_path / "review.md").write_text(review, encoding="utf-8")
-
-        if decide(review) == "PASS":
-            result = "APPROVED"
-        else:
-            result = "REJECTED"
-
-        (evidence_path / "review_result.txt").write_text(result, encoding="utf-8")
-        return {"result": result, "review": review}
diff --git a/loop-engine/release.py b/loop-engine/release.py
deleted file mode 100644
index e6b7cda..0000000
--- a/loop-engine/release.py
+++ /dev/null
@@ -1,78 +0,0 @@
-"""
-Automated SemVer Bump & Keep-a-Changelog Engine (Task 147).
-ZAC-safe: git tag creation defaults to dry-run.
-"""
-
-from __future__ import annotations
-
-import subprocess
-from pathlib import Path
-
-
-class ReleaseEngine:
-    """Calculates versions, formats changelog entries, tags releases."""
-
-    def calculate_next_version(self, current_version: str, task_types: list[str]) -> str:
-        cur = current_version.strip().lstrip("v")
-        parts = cur.split(".")
-        if len(parts) != 3:
-            raise ValueError(f"Invalid SemVer: {current_version!r}")
-        try:
-            major, minor, patch = (int(p) for p in parts)
-        except ValueError as e:
-            raise ValueError(f"Invalid SemVer: {current_version!r}") from e
-        lowered = [str(t).lower() for t in (task_types or [])]
-        if any(t == "breaking" for t in lowered):
-            return f"{major + 1}.0.0"
-        if any(t == "feature" for t in lowered):
-            return f"{major}.{minor + 1}.0"
-        return f"{major}.{minor}.{patch + 1}"
-
-    def format_changelog_entry(self, version: str, date_str: str, tasks: list[dict]) -> str:
-        added: list[str] = []
-        changed: list[str] = []
-        fixed: list[str] = []
-        for t in tasks or []:
-            title = str(t.get("title", "") or "").strip()
-            ttype = str(t.get("type", "") or "").lower()
-            tid = t.get("id", "")
-            line = f"- {title} (Task {tid})" if tid != "" else f"- {title}"
-            if ttype == "feature":
-                added.append(line)
-            elif ttype in ("bug", "fix"):
-                fixed.append(line)
-            else:
-                changed.append(line)
-        lines = [f"## [{version}] - {date_str}", ""]
-        if added:
-            lines.append("### Added")
-            lines.extend(added)
-            lines.append("")
-        if changed:
-            lines.append("### Changed")
-            lines.extend(changed)
-            lines.append("")
-        if fixed:
-            lines.append("### Fixed")
-            lines.extend(fixed)
-            lines.append("")
-        return "\n".join(lines).rstrip() + "\n"
-
-    def update_changelog(self, changelog_path: Path, new_entry: str) -> None:
-        p = Path(changelog_path)
-        text = p.read_text(encoding="utf-8") if p.exists() else "# Changelog\n\n## [Unreleased]\n"
-        marker = "## [Unreleased]"
-        if marker in text:
-            text = text.replace(marker, marker + "\n\n" + new_entry.rstrip(), 1)
-        else:
-            text = text + "\n" + new_entry
-        p.write_text(text, encoding="utf-8")
-
-    def create_git_tag(self, version: str, dry_run: bool = True) -> str:
-        if dry_run:
-            return f"[dry-run] Would create git tag v{version}"
-        subprocess.run(
-            ["git", "tag", "-a", f"v{version}", "-m", f"Release v{version}"],
-            check=True,
-        )
-        return f"v{version}"
diff --git a/loop-engine/router.py b/loop-engine/router.py
deleted file mode 100644
index 395b9a4..0000000
--- a/loop-engine/router.py
+++ /dev/null
@@ -1,310 +0,0 @@
-"""
-LLM Router v2 — category-based model routing via litellm.
-
-XML-structured system prompts following best practices from OpenAI, Anthropic, and Google:
-- System prompt = identity + rules + context (the "who" and "how")
-- User message = task + data (the "what")
-- XML tags for clear structure (<role>, <project_rules>, <conventions>, <context>, <instructions>)
-- FULL files sent — no truncation (higher token cost < hallucination cost)
-
-Reads system-prompt.md + AGENTS.md + docs/conventions.md on every invocation.
-"""
-
-import os
-from datetime import datetime, timezone
-from pathlib import Path
-from typing import Any, Optional
-
-from models import LoopEngineConfig
-from personas import load_personas
-
-
-def _load_file_if_exists(path: str) -> str:
-    p = Path(path)
-    if p.exists():
-        return p.read_text(encoding="utf-8")
-    return ""
-
-
-# Pipeline stage → Manager-defined persona (prompts/fragments/06-personas.md).
-# PO Closure is NOT a separate persona (G1 resolution): closure review reuses
-# the Code Reviewer persona, whose behavior defines the PO-review step.
-STAGE_PERSONAS = {
-    "architect": "Software Architect",
-    "qa_engineer": "QA Engineer",
-    "code_reviewer": "Code Reviewer",
-    "po_closure": "Code Reviewer",
-}
-
-
-class LLMRouter:
-    """Routes LLM calls to the right model based on task category.
-
-    Persona instructions are derived at runtime from the Manager's prompt
-    fragments — zero hardcoded persona bodies in this file. Editing a fragment
-    changes engine behavior on next start.
-    """
-
-    def __init__(self, config: LoopEngineConfig, workspace_root: str = "."):
-        self.config = config
-        self.workspace_root = Path(workspace_root)
-        # Load FULL files — no truncation (higher token cost < hallucination cost)
-        self.system_prompt = _load_file_if_exists(
-            str(self.workspace_root / config.system_prompt_path))
-        self.agents_md = _load_file_if_exists(
-            str(self.workspace_root / config.agmd_path))
-        self.conventions = _load_file_if_exists(
-            str(self.workspace_root / config.conventions_path))
-        # All 7 operational personas from prompts/fragments/06-personas.md
-        self.personas = load_personas(str(self.workspace_root))
-
-    def _resolve_model(self, category: str,
-                       stack_profile: Optional[Any] = None) -> tuple[str, Optional[str]]:
-        """Resolve a model for a category via the 3-tier hierarchy (LE-3).
-
-        Tier 1 — Stack-Preferred Models: consult ``stack_profile.model_preferences``
-        (or a dict's ``"model_preferences"`` key). Match the exact category first,
-        then the wildcard ``"*"``. The first model whose ``{PROVIDER}_API_KEY`` env
-        var is present wins; reasoning level comes from the global category config.
-        Tier 2 — Global Category Models: existing category fallback chain.
-        Tier 3 — Global Default: ``(default_provider, None)``.
-        """
-        # Tier 1: Stack-Preferred Models
-        prefs: dict = {}
-        if stack_profile is not None:
-            if isinstance(stack_profile, dict):
-                prefs = stack_profile.get("model_preferences", {}) or {}
-            else:
-                prefs = getattr(stack_profile, "model_preferences", {}) or {}
-        if prefs:
-            candidate_models = prefs.get(category) or prefs.get("*") or []
-            for model in candidate_models:
-                provider = model.split("/")[0]
-                env_key = f"{provider.upper()}_API_KEY"
-                if os.environ.get(env_key):
-                    cat_config = self.config.categories.get(category)
-                    if not cat_config:
-                        cat_config = self.config.categories.get("unspecified")
-                    reasoning = cat_config.reasoning if cat_config else None
-                    return model, reasoning
-
-        # Tier 2: Global Category Models
-        cat_config = self.config.categories.get(category)
-        if not cat_config:
-            cat_config = self.config.categories.get("unspecified")
-        for model in cat_config.models:
-            provider = model.split("/")[0]
-            env_key = f"{provider.upper()}_API_KEY"
-            if os.environ.get(env_key):
-                return model, cat_config.reasoning
-
-        # Tier 3: Global Default
-        return self.config.default_provider, None
-
-    def _load_memory_context(self) -> str:
-        """Load project memory shards via direct file read.
-
-        Replicates agents/cognitive-executor.md 'Context Bootstrapping & Memory Protocol':
-        - scans .opencode/memory/{namespace}/{key}.md (mirrors mcp-memory-server shards)
-        - uses index.md implicitly via glob (index is derived state)
-        - returns XML-serialized entries for system context injection
-        - caps per-entry at 3000 chars to avoid token bloat
-        """
-        memory_dir = self.workspace_root / ".opencode" / "memory"
-        if not memory_dir.exists():
-            return ""
-        parts: list[str] = []
-        for mem_file in memory_dir.rglob("*.md"):
-            if mem_file.name == "index.md":
-                continue
-            try:
-                content = mem_file.read_text(encoding="utf-8").strip()
-                if not content:
-                    continue
-                rel = mem_file.relative_to(memory_dir)
-                namespace = rel.parent.name if len(rel.parts) > 1 else "unknown"
-                key = mem_file.stem
-                if len(content) > 3000:
-                    content = content[:3000] + "\n...[truncated]"
-                parts.append(f'<memory namespace="{namespace}" key="{key}">\n{content}\n</memory>')
-            except Exception:
-                continue
-        return "\n\n".join(parts)
-
-    def _build_system_context(self, persona: str = "architect") -> str:
-        """Build XML-structured system prompt.
-
-        Persona identity + instructions come verbatim from the Manager's
-        fragments; this method only supplies structural glue.
-        """
-        persona_name = STAGE_PERSONAS.get(persona, persona)
-        data = self.personas.get(persona_name)
-
-        if data:
-            role = (
-                f"You are {persona_name} for the Cognitive Lead AI system, "
-                f"operating under the Manager's system prompt."
-            )
-            instructions = (
-                f"<trigger>{data['trigger']}</trigger>\n"
-                f"<duty>{data['duty']}</duty>\n"
-                f"<behavior>{data['behavior']}</behavior>"
-            )
-        else:
-            # Unknown persona requested — fail loudly rather than impersonate.
-            raise ValueError(
-                f"Persona '{persona_name}' not found in "
-                f"prompts/fragments/06-personas.md. Available: "
-                f"{sorted(self.personas)}")
-
-        parts = [f"<role>{role}</role>"]
-
-        # Project rules: FULL AGENTS.md
-        if self.agents_md:
-            parts.append(f"<project_rules>\n{self.agents_md}\n</project_rules>")
-
-        # Conventions: FULL conventions
-        if self.conventions:
-            parts.append(f"<conventions>\n{self.conventions}\n</conventions>")
-
-        # Context: system prompt (full — no truncation)
-        if self.system_prompt:
-            parts.append(f"<context>\n{self.system_prompt}\n</context>")
-
-        # Memory: project-mandatory context from .opencode/memory
-        # Replicates Context Bootstrapping & Memory Protocol in agents/cognitive-executor.md
-        memory_context = self._load_memory_context()
-        if memory_context:
-            parts.append(f"<memory_context>\n{memory_context}\n</memory_context>")
-
-        # Instructions: persona definition verbatim from the fragment
-        parts.append(f"<instructions>\n{instructions}\n</instructions>")
-
-        return "\n\n".join(parts)
-
-    def route_with_persona(self, persona_name: str, user_content: str,
-                           temperature: float = 0.3,
-                           category: str = "deep",
-                           stack_profile: Optional[Any] = None) -> dict:
-        """Route a call as ANY Manager-defined persona (all 7 invocable)."""
-        model, reasoning = self._resolve_model(category, stack_profile=stack_profile)
-        return {
-            "model": model, "reasoning": reasoning,
-            "system": self._build_system_context(persona_name),
-            "user": user_content,
-            "temperature": temperature,
-        }
-
-    def route_plan(self, task_content: str, category: str = "unspecified",
-                   extra_context: str = "",
-                   stack_profile: Optional[Any] = None) -> dict:
-        user = (
-            f"Generate the DIRECT, complete implementation blueprint for this task.\n"
-            f"RULES:\n"
-            f"- Keep reasoning log brief (< 150 words).\n"
-            f"- Provide concrete, file-level implementation steps with exact code/commands.\n"
-            f"- Do not exceed token limits or output placeholder stubs.\n\n"
-            f"## Task Content:\n{task_content}"
-        )
-        if extra_context:
-            user += f"\n\nIncorporate this brainstorming session output:\n\n{extra_context}"
-        model, reasoning = self._resolve_model(category, stack_profile=stack_profile)
-        system = self._build_system_context("architect")
-        system += (
-            "\n\n<deliverable>\n"
-            "PLANNING output MUST be the direct implementation blueprint: "
-            "concrete file-level steps, exact symbols, and verification "
-            "commands. Never respond with meta-requests for discovery or "
-            "clarification questions to the caller — produce the blueprint "
-            "itself.\n"
-            "</deliverable>"
-        )
-        return {
-            "model": model, "reasoning": reasoning,
-            "system": system,
-            "user": user,
-            "temperature": 0.3,
-        }
-
-    def route_qa(self, task_content: str, diff: str = "", toolchain_evidence: str = "",
-                 stack_profile: Optional[Any] = None) -> dict:
-        model, reasoning = self._resolve_model("deep", stack_profile=stack_profile)
-        user = f"Review this task and changes:\n\n{task_content}\n\n## Diff\n\n{diff}"
-        if toolchain_evidence:
-            user += f"\n\n## Toolchain Verification\n\n{toolchain_evidence}"
-        return {
-            "model": model, "reasoning": reasoning,
-            "system": self._build_system_context("qa_engineer"),
-            "user": user,
-            "temperature": 0.1,
-        }
-
-    def route_review(self, task_content: str, qa_report: str = "",
-                     stack_profile: Optional[Any] = None) -> dict:
-        model, reasoning = self._resolve_model("deep", stack_profile=stack_profile)
-        return {
-            "model": model, "reasoning": reasoning,
-            "system": self._build_system_context("code_reviewer"),
-            "user": f"Review this task:\n\n{task_content}\n\n## QA Report\n\n{qa_report}",
-            "temperature": 0.2,
-        }
-
-    def call_llm(self, routing: dict) -> str:
-        """Call LLM via litellm with fallback chain.
-
-        Raises RuntimeError on failure — an error string returned as a plan
-        would flow downstream and get approved/reviewed as if it were real
-        output. Callers (pipeline guard) convert the exception into CRASHED.
-        """
-        try:
-            import litellm
-            kwargs = {
-                "model": routing["model"],
-                "messages": [
-                    {"role": "system", "content": routing["system"]},
-                    {"role": "user", "content": routing["user"]},
-                ],
-                "temperature": routing.get("temperature", 0.3),
-                "max_tokens": 8192,
-            }
-            reasoning = routing.get("reasoning")
-            if reasoning:
-                kwargs["reasoning_effort"] = reasoning
-            response = litellm.completion(**kwargs)
-            msg = response.choices[0].message
-            # Extract content or fallback to reasoning_content for thinking models
-            content = getattr(msg, "content", None) or ""
-            if not content:
-                reasoning = getattr(msg, "reasoning_content", None) or getattr(msg, "reasoning", None)
-                if reasoning:
-                    content = str(reasoning)
-                else:
-                    content = str(msg)
-            content = content.strip()
-
-            # Debug telemetry (HOTFIX-03): raw request/response logging.
-            # Opt-in ONLY via LOOP_ENGINE_DEBUG=1 — zero impact in normal runs.
-            if os.environ.get("LOOP_ENGINE_DEBUG") == "1":
-                try:
-                    log_dir = Path(__file__).resolve().parent / "logs"
-                    log_dir.mkdir(parents=True, exist_ok=True)
-                    entry = (
-                        f"\n===== [{datetime.now(timezone.utc).isoformat(timespec='seconds')}Z] "
-                        f"model={routing.get('model')} =====\n"
-                        f"--- SYSTEM ---\n{routing.get('system')}\n"
-                        f"--- USER ---\n{routing.get('user')}\n"
-                        f"--- RESPONSE ---\n{content}\n"
-                        f"===== END =====\n"
-                    )
-                    with open(log_dir / "llm_requests.log", "a", encoding="utf-8") as f:
-                        f.write(entry)
-                except Exception as log_e:
-                    print(f"[router] debug telemetry log error: {log_e}")
-
-            return content
-        except ImportError as e:
-            raise RuntimeError(
-                f"litellm not installed. Run: pip install litellm ({e})") from e
-        except Exception as e:
-            raise RuntimeError(f"LLM call failed for model "
-                               f"{routing.get('model')}: {e}") from e
diff --git a/loop-engine/sentinel.py b/loop-engine/sentinel.py
deleted file mode 100644
index 5d2fedc..0000000
--- a/loop-engine/sentinel.py
+++ /dev/null
@@ -1,300 +0,0 @@
-"""
-Type Drift Sentinel (LE-7 / Task 139).
-
-Deterministic regex-based scanner that detects hand-authored duplicate
-interface models, request/response DTOs, and data classes in consumer
-application paths during the toolchain verification gate — BEFORE LLM QA.
-
-Complements the No-Manual-DTO Mandate (prompts/fragments/20-no_manual_dto_mandate.md):
-the prompt fragment is the cognitive rule; this module is the deterministic
-enforcement layer. When a diff introduces a manual DTO/interface/model
-declaration into a consumer path while a source-of-truth contract or shared
-schema governs those types, check_diff() returns a failing DriftCheckResult
-with an actionable Markdown report instructing the agent to import from the
-shared package or run the stack's code-generation toolchain.
-
-The sentinel is intentionally side-effect free and unit-testable, mirroring
-the pure-helper design of loop-engine/contracts.py.
-"""
-
-from __future__ import annotations
-
-import fnmatch
-import re
-from dataclasses import dataclass, field
-
-
-@dataclass
-class DriftCheckResult:
-    """Outcome of a type-drift scan over a task diff."""
-
-    passed: bool
-    violations: list[str] = field(default_factory=list)
-    report_md: str = ""
-
-
-# Regexes matching hand-authored model/DTO declarations per language family.
-# TypeScript/JavaScript: interfaces and type aliases whose name carries a
-# DTO/model marker (e.g. `export interface CreateUserDTO {`, `type UserResponse = ...`).
-_TS_JS_RE = re.compile(
-    r"\b(?:export\s+)?(?:interface|type)\s+"
-    r"([A-Za-z0-9_]*(?:Dto|DTO|Request|Response|Payload|Model|Schema))\b"
-)
-# Kotlin: data classes and plain classes with a DTO/model marker
-# (e.g. `data class CreateUserRequest(`, `class OrderResponse(`).
-_KOTLIN_RE = re.compile(
-    r"\b(?:data\s+)?class\s+"
-    r"([A-Za-z0-9_]*(?:Dto|DTO|Request|Response|Payload|Model))\b"
-)
-# Python: classes deriving from BaseModel/BaseDTO/dict with a DTO/model marker
-# (e.g. `class CreateUserDTO(BaseModel):`).
-_PYTHON_RE = re.compile(
-    r"\bclass\s+"
-    r"([A-Za-z0-9_]*(?:Dto|DTO|Request|Response|Payload|Schema))"
-    r"\s*\((?:BaseModel|BaseDTO|dict)?\)"
-)
-
-# Default consumer paths where hand-authored DTOs are forbidden when a
-# governing contract exists.
-DEFAULT_CONSUMER_PATTERNS = [
-    "apps/**",
-    "services/**",
-    "client/**",
-    "frontend/**",
-    "mobile/**",
-    "src/**",
-]
-
-# Default paths where DTO/interface/model declarations are the canonical
-# source of truth (contract definitions) or generated artifacts — exempt.
-DEFAULT_ALLOWED_PATTERNS = [
-    "packages/shared-schema/**",
-    "contracts/**",
-    "openapi/**",
-    "proto/**",
-    "**/generated/**",
-    "**/build/**",
-    "**/dist/**",
-    "**/*.gen.*",
-]
-
-# Comment prefixes that mark a line as a comment (skipped by the scanner).
-_COMMENT_PREFIXES = ("//", "#", "/*", "*", "<!--", "--", "'''", '"""')
-
-
-class TypeDriftSentinel:
-    """Scan git diffs for hand-authored duplicate DTO declarations.
-
-    Args:
-        consumer_patterns: fnmatch globs for consumer application paths where
-            manual DTO declarations are forbidden (defaults to
-            DEFAULT_CONSUMER_PATTERNS).
-        allowed_patterns: fnmatch globs for contract/generated paths that are
-            exempt from the mandate (defaults to DEFAULT_ALLOWED_PATTERNS).
-    """
-
-    def __init__(
-        self,
-        consumer_patterns: list[str] | None = None,
-        allowed_patterns: list[str] | None = None,
-    ):
-        self.consumer_patterns = (
-            list(consumer_patterns)
-            if consumer_patterns is not None
-            else list(DEFAULT_CONSUMER_PATTERNS)
-        )
-        self.allowed_patterns = (
-            list(allowed_patterns)
-            if allowed_patterns is not None
-            else list(DEFAULT_ALLOWED_PATTERNS)
-        )
-
-    # ------------------------------------------------------------------
-    # Public API
-    # ------------------------------------------------------------------
-
-    def check_diff(self, diff_text: str) -> DriftCheckResult:
-        """Scan a git diff for manual DTO declarations in consumer paths.
-
-        Non-contract/no-drift diffs return ``DriftCheckResult(passed=True)``.
-        On violation, returns ``passed=False`` plus an actionable Markdown
-        report telling the agent to import from the shared package or run the
-        code-generation toolchain.
-        """
-        violations: list[str] = []
-        for path, added_lines in self._iter_added_lines(diff_text):
-            if self._matches_any(path, self.allowed_patterns):
-                continue
-            if not self._matches_any(path, self.consumer_patterns):
-                continue
-            for line_no, line in added_lines:
-                if self._is_ignored(line):
-                    continue
-                self._scan_line(path, line_no, line, violations)
-
-        if violations:
-            return DriftCheckResult(
-                passed=False,
-                violations=violations,
-                report_md=self._build_report(violations),
-            )
-        return DriftCheckResult(passed=True, violations=[])
-
-    # ------------------------------------------------------------------
-    # Diff parsing
-    # ------------------------------------------------------------------
-
-    def _iter_added_lines(self, diff_text: str):
-        """Yield ``(path, [(line_no, content), ...])`` for files with additions.
-
-        Parses ``diff --git a/<a> b/<b>`` headers (b-side path wins, refined by
-        ``+++ b/<path>`` lines) and ``@@ -a,b +c,d @@`` hunk headers so each
-        added line carries its approximate new-file line number.
-        """
-        current_path: str | None = None
-        current_added: list[tuple[int, str]] = []
-        new_line: int | None = None
-        in_hunk = False
-
-        # Accumulate files explicitly (a closure with yield would turn this
-        # into a double-generator and is invalid inside this generator body).
-        files: list[tuple[str, list[tuple[int, str]]]] = []
-
-        for raw in diff_text.splitlines():
-            line = raw
-            header = re.match(r"^diff --git a/(.*) b/(.*)$", line)
-            if header:
-                if current_path is not None:
-                    files.append((current_path, current_added))
-                current_path = header.group(2).strip()
-                current_added = []
-                new_line = None
-                in_hunk = False
-                continue
-
-            plus_path = re.match(r"^\+\+\+ b/(.*)$", line)
-            if plus_path:
-                current_path = plus_path.group(1).strip()
-                continue
-
-            hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
-            if hunk:
-                new_line = int(hunk.group(1))
-                in_hunk = True
-                continue
-
-            if current_path is None or not in_hunk:
-                continue
-
-            if line.startswith("+"):
-                if new_line is not None:
-                    current_added.append((new_line, line[1:]))
-                    new_line += 1
-            elif line.startswith("-"):
-                # Removed lines do not advance the new-file line counter.
-                pass
-            elif line.startswith(" "):
-                if new_line is not None:
-                    new_line += 1
-            # "\ No newline at end of file" and other metadata are skipped.
-
-        if current_path is not None:
-            files.append((current_path, current_added))
-
-        yield from files
-
-    # ------------------------------------------------------------------
-    # Scanning
-    # ------------------------------------------------------------------
-
-    def _matches_any(self, path: str, patterns: list[str]) -> bool:
-        return any(fnmatch.fnmatch(path, pat) for pat in patterns)
-
-    def _is_ignored(self, line: str) -> bool:
-        """True for comment-only lines or lines carrying an explicit `drift-ignore` bypass."""
-        if "drift-ignore" in line:
-            return True
-        stripped = line.strip()
-        if not stripped:
-            return True
-        return stripped.startswith(_COMMENT_PREFIXES)
-
-    def _scan_line(self, path: str, line_no: int, line: str, violations: list[str]) -> None:
-        # Dispatch by file extension so a Python `class XxxDTO(BaseModel):`
-        # line is labeled Python (not Kotlin, whose generic `class` regex also
-        # matches). Unknown extensions fall back to a specificity-ordered
-        # cascade (Python → TypeScript/JavaScript → Kotlin).
-        _BY_EXTENSION = {
-            ".py": ("Python", _PYTHON_RE),
-            ".kt": ("Kotlin", _KOTLIN_RE),
-            ".kts": ("Kotlin", _KOTLIN_RE),
-            ".ts": ("TypeScript/JavaScript", _TS_JS_RE),
-            ".tsx": ("TypeScript/JavaScript", _TS_JS_RE),
-            ".js": ("TypeScript/JavaScript", _TS_JS_RE),
-            ".jsx": ("TypeScript/JavaScript", _TS_JS_RE),
-            ".mjs": ("TypeScript/JavaScript", _TS_JS_RE),
-            ".cjs": ("TypeScript/JavaScript", _TS_JS_RE),
-        }
-        lowered = path.lower()
-        match = None
-        for ext, (lang, regex) in _BY_EXTENSION.items():
-            if lowered.endswith(ext):
-                match = regex.search(line)
-                if match:
-                    self._record_violation(path, line_no, lang, match.group(1), violations)
-                    return
-                return  # known language, no match -> not a violation of this language
-
-        # Unknown extension: cascade by specificity (Python is most specific,
-        # TS/JS next, Kotlin generic last). Only the first match labels the line.
-        for lang, regex in (
-            ("Python", _PYTHON_RE),
-            ("TypeScript/JavaScript", _TS_JS_RE),
-            ("Kotlin", _KOTLIN_RE),
-        ):
-            match = regex.search(line)
-            if match:
-                self._record_violation(path, line_no, lang, match.group(1), violations)
-                return
-
-    def _record_violation(
-        self, path: str, line_no: int, lang: str, type_name: str, violations: list[str]
-    ) -> None:
-        violations.append(
-            f"- `{path}` — manual {lang} model declaration `{type_name}` "
-            f"(added line {line_no}). Import it from the shared/contract "
-            f"package (`@repo/shared-schema`, `packages/shared-schema`) or run "
-            f"the stack codegen (`pnpm generate`, `prisma generate`, `protoc`, "
-            f"`./gradlew generateProto`) instead of hand-authoring a duplicate."
-        )
-
-    def _build_report(self, violations: list[str]) -> str:
-        lines = [
-            "# Type Drift Sentinel Report",
-            "",
-            "**Overall:** FAILED",
-            "",
-            "Hand-authored DTO/interface/model declarations were detected in consumer "
-            "paths while a source-of-truth contract or shared schema governs these types.",
-            "",
-            "## Violations",
-            "",
-        ]
-        lines.extend(violations)
-        lines.extend(
-            [
-                "",
-                "## Required Action",
-                "",
-                "- **Import** the type directly from the shared/contract package "
-                "(`@repo/shared-schema`, `packages/shared-schema`) where it is defined, OR",
-                "- **Run the stack's code-generation toolchain** (`pnpm generate`, "
-                "`prisma generate`, `protoc`, `./gradlew generateProto`) to produce the "
-                "type from the contract.",
-                "",
-                "Hand-written duplicates create silent type drift. Do NOT re-run QA "
-                "until the violation is resolved (or justified with an explicit "
-                "`drift-ignore` comment).",
-            ]
-        )
-        return "\n".join(lines)
\ No newline at end of file
diff --git a/loop-engine/specs.py b/loop-engine/specs.py
deleted file mode 100644
index 9933e4e..0000000
--- a/loop-engine/specs.py
+++ /dev/null
@@ -1,194 +0,0 @@
-"""
-Spec-First Artifact Pipeline & State Gate (LE-8 / Task 140).
-
-Enforces that tasks introducing architectural changes, API contracts, or
-database schema mutations must have verified spec artifacts (ADR, PRD,
-Contract, Data Model) BEFORE code implementation begins.
-
-Pipeline:
-    task_content + plan_text -> evaluate_requirements() -> matched rules
-    -> validate_artifacts(workspace_root, diff_text) -> SpecValidationResult
-
-Design notes:
-- ``evaluate_requirements`` is a pure keyword scan (lowercased substring
-  match) and returns an empty list for routine tasks / bugfixes.
-- ``validate_artifacts`` scans the workspace with ``rglob`` + ``fnmatch``
-  (full-relative-path glob semantics, same as ``contracts.match_contract_rules``)
-  and also parses ``diff --git`` headers from the staged task diff so artifacts
-  staged in the active task satisfy the gate.
-- An empty rule set passes immediately (the gate is inert until configured).
-- The engine is deterministic and side-effect free; the daemon owns all state
-  transitions (CRASHED / spec_artifacts persistence).
-"""
-
-from __future__ import annotations
-
-import fnmatch
-import re
-from dataclasses import dataclass, field
-from pathlib import Path
-
-from models import SpecGateConfig, SpecRequirementRule
-
-# Matches `diff --git a/<old> b/<new>` header lines — the b-side path is the
-# post-change relative path that may stage spec artifacts (mirrors contracts.py).
-_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)\n", re.MULTILINE)
-
-
-@dataclass
-class SpecValidationResult:
-    """Outcome of a spec artifact validation run."""
-    passed: bool
-    required_artifacts: list[str] = field(default_factory=list)
-    found_artifacts: list[str] = field(default_factory=list)
-    errors: list[str] = field(default_factory=list)
-    report_md: str = ""
-
-
-class SpecGateEngine:
-    """Keyword-driven spec requirement evaluation + artifact validation."""
-
-    def __init__(self, config: SpecGateConfig | None = None):
-        self.config = config or SpecGateConfig()
-
-    # --- Requirement evaluation ---
-
-    def evaluate_requirements(self, task_content: str, plan_text: str = "") -> list[SpecRequirementRule]:
-        """Return the subset of configured rules triggered by task/plan keywords.
-
-        The task content and approved plan are combined and lowercased; a rule
-        fires when ANY of its ``keywords`` appears as a substring. Routine tasks
-        and bugfixes (no keyword hit) yield an empty list.
-        """
-        if not self.config.rules:
-            return []
-        haystack = f"{(task_content or '')}\n{(plan_text or '')}".lower()
-        matched: list[SpecRequirementRule] = []
-        for rule in self.config.rules:
-            if any(keyword.lower() in haystack for keyword in rule.keywords):
-                matched.append(rule)
-        return matched
-
-    # --- Artifact validation ---
-
-    def validate_artifacts(
-        self,
-        rules: list[SpecRequirementRule],
-        workspace_root: str | Path,
-        diff_text: str = "",
-    ) -> SpecValidationResult:
-        """Validate that required spec artifacts exist for each fired rule.
-
-        For every rule, each ``target_directories`` pattern is checked against
-        (1) files present under ``workspace_root`` (``rglob`` + ``fnmatch``) and
-        (2) paths staged in ``diff_text`` (parsed from ``diff --git`` headers).
-        A rule is satisfied when at least one of its patterns matches anywhere.
-        Missing rules produce diagnostic errors and a structured Markdown report.
-
-        An empty ``rules`` list passes immediately (``SpecValidationResult(passed=True)``).
-        """
-        if not rules:
-            return SpecValidationResult(passed=True)
-
-        root = Path(workspace_root)
-        diff_text = diff_text or ""
-        required: list[str] = []
-        found: list[str] = []
-        errors: list[str] = []
-
-        for rule in rules:
-            rule_required = [a.value for a in rule.required_artifacts]
-            rule_found: list[str] = []
-            for pattern in rule.target_directories or []:
-                if pattern not in required:
-                    required.append(pattern)
-                matches = _find_matching_files(root, pattern)
-                matches += _paths_in_diff_matching(diff_text, pattern)
-                for m in matches:
-                    if m not in rule_found:
-                        rule_found.append(m)
-                    if m not in found:
-                        found.append(m)
-            if not rule_found:
-                artifact_label = ", ".join(rule_required) if rule_required else "spec artifact"
-                errors.append(
-                    f"Rule '{rule.name}' requires {artifact_label} "
-                    f"but no matching file found under {', '.join(rule.target_directories or [])}"
-                )
-
-        report_md = _build_report(rules, required, found, errors)
-        return SpecValidationResult(
-            passed=len(errors) == 0,
-            required_artifacts=required,
-            found_artifacts=found,
-            errors=errors,
-            report_md=report_md,
-        )
-
-
-# --- Pure helpers (unit-testable, side-effect free) ---
-
-
-def _find_matching_files(root: Path, pattern: str) -> list[str]:
-    """Return relative paths of files under ``root`` matching a glob pattern.
-
-    Uses ``rglob`` + ``fnmatch`` over the full relative path so patterns like
-    ``docs/adr/**`` and ``docs/architecture.md`` behave consistently.
-    """
-    matches: list[str] = []
-    try:
-        for p in root.rglob("*"):
-            if p.is_file():
-                rel = p.relative_to(root).as_posix()
-                if fnmatch.fnmatch(rel, pattern):
-                    matches.append(rel)
-    except OSError:
-        return []
-    return sorted(matches)
-
-
-def _paths_in_diff(diff_text: str) -> list[str]:
-    """Return deduplicated relative paths of files touched by a git diff."""
-    paths: list[str] = []
-    seen: set[str] = set()
-    for match in _DIFF_HEADER_RE.finditer(diff_text):
-        path = match.group(2).strip()
-        if path and path not in seen:
-            seen.add(path)
-            paths.append(path)
-    return paths
-
-
-def _paths_in_diff_matching(diff_text: str, pattern: str) -> list[str]:
-    """Return staged diff paths (b-side) matching a glob pattern."""
-    return [p for p in _paths_in_diff(diff_text) if fnmatch.fnmatch(p, pattern)]
-
-
-def _build_report(
-    rules: list[SpecRequirementRule],
-    required: list[str],
-    found: list[str],
-    errors: list[str],
-) -> str:
-    """Build a structured Markdown report: verified vs missing spec artifacts."""
-    lines = ["# Spec-First Gate Report", ""]
-    lines.append(f"**Rules evaluated:** {len(rules)}")
-    lines.append(f"**Required artifact locations:** {len(required)}")
-    lines.append(f"**Verified artifacts:** {len(found)}")
-    lines.append(f"**Errors:** {len(errors)}")
-    lines.append("")
-    if found:
-        lines.append("## Verified Artifacts")
-        lines.extend(f"- {f}" for f in found)
-        lines.append("")
-    if errors:
-        lines.append("## Missing Spec Artifacts")
-        lines.extend(f"- {e}" for e in errors)
-        lines.append("")
-    lines.append("## Resolution")
-    lines.append(
-        "Add the required spec artifact (ADR / PRD / Contract / Data Model) under "
-        "the configured target directories, or include it in the task's staged diff "
-        "before implementation. See `docs/loop-engine/configuration.md` (LE-8)."
-    )
-    return "\n".join(lines)
\ No newline at end of file
diff --git a/loop-engine/stacks.py b/loop-engine/stacks.py
deleted file mode 100644
index 8938d86..0000000
--- a/loop-engine/stacks.py
+++ /dev/null
@@ -1,326 +0,0 @@
-"""
-Stack Profile Engine — declarative YAML stack definitions, detection, and preflight.
-
-Implements:
-- StackProfile: thin wrapper around StackProfileConfig with helpers
-- StackRegistry: scans stacks_dir, loads/caches .yaml/.json definitions
-- StackDetector: two-tier heuristic (header > marker_files/extensions > keywords > generic)
-- PreflightRunner: async validation of toolchain commands with timeout
-"""
-
-import asyncio
-import json
-import re
-import subprocess
-from dataclasses import dataclass, field
-from pathlib import Path
-from typing import Optional
-
-# Try to import yaml, fallback to safe parsing if unavailable
-try:
-    import yaml  # type: ignore
-
-    HAS_YAML = True
-except ImportError:
-    HAS_YAML = False
-
-from models import StackProfileConfig
-
-
-# ---------------------------------------------------------------------------
-# StackProfile — thin wrapper
-# ---------------------------------------------------------------------------
-
-class StackProfile:
-    """Encapsulates a StackProfileConfig with validation and serialization."""
-
-    def __init__(self, config: StackProfileConfig):
-        self.config = config
-
-    @property
-    def name(self) -> str:
-        return self.config.name
-
-    @property
-    def display_name(self) -> str:
-        return self.config.display_name
-
-    @property
-    def detection(self):
-        return self.config.detection
-
-    @property
-    def skills(self) -> list[str]:
-        return self.config.skills
-
-    @property
-    def preflight(self) -> list[str]:
-        return self.config.preflight
-
-    @property
-    def toolchain(self):
-        return self.config.toolchain
-
-    @property
-    def model_preferences(self) -> dict[str, list[str]]:
-        return self.config.model_preferences
-
-    def to_dict(self) -> dict:
-        return self.config.model_dump()
-
-    def __repr__(self) -> str:
-        return f"StackProfile(name={self.name!r}, display_name={self.display_name!r})"
-
-
-# ---------------------------------------------------------------------------
-# StackRegistry — scan + cache
-# ---------------------------------------------------------------------------
-
-class StackRegistry:
-    """Scans stacks_dir, loads/caches all .yaml and .json profile definitions."""
-
-    def __init__(self, stacks_dir: str = "stacks", repo_root: str | Path | None = None):
-        # Resolve stacks_dir relative to repo_root if needed
-        if repo_root is None:
-            # default: parent of loop-engine/ (REPO_ROOT)
-            from pathlib import Path as _P
-
-            repo_root = _P(__file__).resolve().parent.parent
-        else:
-            repo_root = Path(repo_root)
-
-        p = Path(stacks_dir)
-        if not p.is_absolute():
-            p = Path(repo_root) / stacks_dir
-        self.stacks_dir = p
-        self._cache: dict[str, StackProfile] = {}
-        self._loaded = False
-
-    def _parse_file(self, path: Path) -> dict:
-        text = path.read_text(encoding="utf-8")
-        if path.suffix in (".yaml", ".yml"):
-            if HAS_YAML:
-                data = yaml.safe_load(text)
-                if data is None:
-                    return {}
-                if not isinstance(data, dict):
-                    raise ValueError(f"YAML root must be a mapping in {path}")
-                return data
-            else:
-                # Fallback: try JSON parse if yaml not available
-                try:
-                    return json.loads(text)
-                except json.JSONDecodeError as e:
-                    raise ImportError(f"PyYAML not installed and {path} is not JSON: {e}")
-        elif path.suffix == ".json":
-            return json.loads(text)
-        else:
-            raise ValueError(f"Unsupported profile extension: {path.suffix}")
-
-    def _load_all(self) -> None:
-        if self._loaded:
-            return
-        self._cache.clear()
-        if not self.stacks_dir.exists():
-            self._loaded = True
-            return
-        for f in sorted(self.stacks_dir.iterdir()):
-            if f.suffix not in (".yaml", ".yml", ".json"):
-                continue
-            if f.is_dir():
-                continue
-            try:
-                data = self._parse_file(f)
-                cfg = StackProfileConfig(**data)
-                # Ensure name matches filename if not explicitly consistent — but allow explicit name to win
-                # Validate that name is filesystem-safe
-                self._cache[cfg.name] = StackProfile(cfg)
-            except Exception as e:
-                # Re-raise with context for caller/test to assert on invalid schema
-                raise ValueError(f"Failed to load stack profile {f.name}: {e}") from e
-        self._loaded = True
-
-    def list_profiles(self) -> list[StackProfile]:
-        self._load_all()
-        return list(self._cache.values())
-
-    def get_profile(self, name: str) -> Optional[StackProfile]:
-        self._load_all()
-        return self._cache.get(name)
-
-    def reload(self) -> None:
-        """Force re-scan (useful in tests)."""
-        self._loaded = False
-        self._load_all()
-
-    @property
-    def names(self) -> list[str]:
-        self._load_all()
-        return sorted(self._cache.keys())
-
-
-# ---------------------------------------------------------------------------
-# StackDetector — two-tier heuristic
-# ---------------------------------------------------------------------------
-
-class StackDetector:
-    """Two-tier detection logic.
-
-    Precedence (highest to lowest):
-      1. Explicit `**Stack:** <name>` header in task content
-      2. Workspace marker_files or extension scan
-      3. Task keywords (task_keywords substring match, case-insensitive)
-      4. Fallback to default_stack ("generic")
-    """
-
-    # Matches: **Stack:** node-ts  or  **Stacks:** python-fastapi  etc.
-    _HEADER_RE = re.compile(r"\*\*Stack:\*\*\s*([a-zA-Z0-9._\-/]+)", re.IGNORECASE)
-    # Also allow Stack: without bold, case-insensitive
-    _HEADER_RE_PLAIN = re.compile(r"^\s*Stack\s*:\s*([a-zA-Z0-9._\-/]+)", re.IGNORECASE | re.MULTILINE)
-
-    @staticmethod
-    def detect(
-        task_content: str,
-        workspace_root: str | Path,
-        registry: StackRegistry,
-        default_stack: str = "generic",
-    ) -> StackProfile:
-        # 1. Explicit header
-        m = StackDetector._HEADER_RE.search(task_content)
-        if m:
-            name = m.group(1).strip().lower()
-            profile = registry.get_profile(name)
-            if profile is not None:
-                return profile
-            # Also try without lower? registry is case-sensitive lower
-            profile = registry.get_profile(name)
-            if profile:
-                return profile
-
-        m2 = StackDetector._HEADER_RE_PLAIN.search(task_content)
-        if m2:
-            name = m2.group(1).strip().lower()
-            profile = registry.get_profile(name)
-            if profile is not None:
-                return profile
-
-        workspace_root = Path(workspace_root)
-
-        # 2. Marker files / extensions
-        # First check marker_files existence
-        for profile in registry.list_profiles():
-            if profile.name == default_stack:
-                continue  # skip generic in this phase; it's fallback
-            for marker in profile.detection.marker_files:
-                if (workspace_root / marker).exists():
-                    return profile
-            # Also scan for matching extensions in workspace (non-recursive top-level + one level?)
-            # We walk up to 2 levels deep to avoid full repo scan cost
-            if profile.detection.extensions:
-                # Quick scan: list files at root and subdirs one level
-                try:
-                    # Root files
-                    for f in workspace_root.iterdir():
-                        if f.is_file() and any(f.name.endswith(ext) for ext in profile.detection.extensions):
-                            return profile
-                    # One level deep
-                    for sub in workspace_root.iterdir():
-                        if sub.is_dir() and not sub.name.startswith(".") and sub.name not in ("node_modules", "__pycache__", ".git", "loop-engine", "stacks", "tasks", ".venv", "venv"):
-                            for f in sub.iterdir():
-                                if f.is_file() and any(f.name.endswith(ext) for ext in profile.detection.extensions):
-                                    return profile
-                except (PermissionError, OSError):
-                    pass
-
-        # 3. Task keywords (case-insensitive substring)
-        lower_content = task_content.lower()
-        for profile in registry.list_profiles():
-            if profile.name == default_stack:
-                continue
-            for kw in profile.detection.task_keywords:
-                if kw.lower() in lower_content:
-                    return profile
-
-        # 4. Fallback
-        generic = registry.get_profile(default_stack)
-        if generic is not None:
-            return generic
-        # If even generic missing, return first available or synthesize generic
-        profiles = registry.list_profiles()
-        if profiles:
-            return profiles[0]
-        # Synthetic generic
-        return StackProfile(StackProfileConfig(name="generic", display_name="Generic"))
-
-
-# ---------------------------------------------------------------------------
-# PreflightRunner — async toolchain validation
-# ---------------------------------------------------------------------------
-
-@dataclass
-class PreflightResult:
-    passed: bool
-    errors: list[str] = field(default_factory=list)
-    outputs: list[str] = field(default_factory=list)
-
-
-class PreflightRunner:
-    """Asynchronously executes profile.preflight commands with timeouts."""
-
-    def __init__(self, timeout_seconds: float = 30.0):
-        self.timeout_seconds = timeout_seconds
-
-    async def run(self, profile: StackProfile, cwd: str | Path | None = None) -> PreflightResult:
-        """Run all preflight commands sequentially. Return PreflightResult.
-
-        Each command is executed via shell (so `||` works). Non-zero exit → error.
-        Timeout → error. Empty preflight → passed.
-        """
-        if not profile.preflight:
-            return PreflightResult(passed=True)
-
-        errors: list[str] = []
-        outputs: list[str] = []
-        cwd_path = Path(cwd) if cwd else None
-
-        for cmd in profile.preflight:
-            try:
-                proc = await asyncio.create_subprocess_shell(
-                    cmd,
-                    stdout=asyncio.subprocess.PIPE,
-                    stderr=asyncio.subprocess.PIPE,
-                    cwd=str(cwd_path) if cwd_path else None,
-                )
-                try:
-                    stdout, stderr = await asyncio.wait_for(
-                        proc.communicate(), timeout=self.timeout_seconds
-                    )
-                except asyncio.TimeoutError:
-                    try:
-                        proc.kill()
-                    except ProcessLookupError:
-                        pass
-                    errors.append(f"Preflight timeout ({self.timeout_seconds}s): {cmd}")
-                    continue
-
-                out = stdout.decode(errors="replace").strip()
-                err = stderr.decode(errors="replace").strip()
-                combined = out
-                if err:
-                    combined = f"{out}\n{err}" if out else err
-                outputs.append(combined)
-
-                if proc.returncode != 0:
-                    errors.append(f"Preflight failed ({proc.returncode}): {cmd} → {err or out or 'no output'}")
-
-            except FileNotFoundError as e:
-                errors.append(f"Preflight spawn failed: {cmd} → {e}")
-            except Exception as e:
-                errors.append(f"Preflight error: {cmd} → {e}")
-
-        passed = len(errors) == 0
-        return PreflightResult(passed=passed, errors=errors, outputs=outputs)
-
-    def run_sync(self, profile: StackProfile, cwd: str | Path | None = None) -> PreflightResult:
-        """Synchronous wrapper for tests and sync callers."""
-        return asyncio.run(self.run(profile, cwd=cwd))
diff --git a/loop-engine/state.py b/loop-engine/state.py
deleted file mode 100644
index 51d21d6..0000000
--- a/loop-engine/state.py
+++ /dev/null
@@ -1,226 +0,0 @@
-"""
-State Machine v2 — SQLite-backed task state tracking.
-
-Inspired by OMO's Boulder/Goal state system but minimal:
-- tasks table: tracks each task's pipeline position
-- todos table: Todo Enforcer pattern (idle detection)
-- Single source of truth: SQLite file at loop-engine/state/loop.db
-
-Zero external dependencies — uses Python's built-in sqlite3.
-"""
-
-import json
-import sqlite3
-import time
-from pathlib import Path
-from typing import Optional
-
-from models import TaskState
-
-
-# --- Schema ---
-
-_SCHEMA = """
-CREATE TABLE IF NOT EXISTS tasks (
-    task_id INTEGER PRIMARY KEY,
-    task_file TEXT NOT NULL UNIQUE,
-    state TEXT NOT NULL DEFAULT 'backlog',
-    plan TEXT DEFAULT NULL,
-    qa_feedback TEXT DEFAULT NULL,
-    qa_retry_count INTEGER DEFAULT 0,
-    evidence_dir TEXT DEFAULT NULL,
-    spec_artifacts TEXT DEFAULT NULL,
-    created_at REAL NOT NULL,
-    updated_at REAL NOT NULL,
-    closed_at REAL DEFAULT NULL
-);
-
-CREATE TABLE IF NOT EXISTS todos (
-    id INTEGER PRIMARY KEY AUTOINCREMENT,
-    task_id INTEGER NOT NULL,
-    description TEXT NOT NULL,
-    status TEXT DEFAULT 'pending',
-    created_at REAL NOT NULL,
-    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
-);
-
-CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
-CREATE INDEX IF NOT EXISTS idx_tasks_file ON tasks(task_file);
-CREATE INDEX IF NOT EXISTS idx_todos_task ON todos(task_id);
-
-CREATE TABLE IF NOT EXISTS dead_letter_queue (
-    id INTEGER PRIMARY KEY AUTOINCREMENT,
-    task_id INTEGER NOT NULL,
-    stage TEXT NOT NULL,
-    payload TEXT NOT NULL,
-    error_reason TEXT NOT NULL,
-    created_at REAL NOT NULL,
-    retry_count INTEGER DEFAULT 0
-);
-CREATE INDEX IF NOT EXISTS idx_dlq_task ON dead_letter_queue(task_id);
-"""
-
-
-class StateMachine:
-    """SQLite-backed state machine for the Cognitive Loop Engine."""
-
-    def __init__(self, db_path: str = "loop-engine/state/loop.db"):
-        self.db_path = Path(db_path)
-        self.db_path.parent.mkdir(parents=True, exist_ok=True)
-        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
-        self.conn.row_factory = sqlite3.Row
-        self.conn.executescript(_SCHEMA)
-        self.conn.commit()
-        # Safe column migration for databases created before the spec-first gate
-        # (LE-8): newer schemas already declare spec_artifacts, so the ALTER is a
-        # no-op that raises sqlite3.OperationalError("duplicate column name") and
-        # is deliberately swallowed. Additive + non-destructive.
-        try:
-            self.conn.execute("ALTER TABLE tasks ADD COLUMN spec_artifacts TEXT DEFAULT NULL")
-            self.conn.commit()
-        except sqlite3.OperationalError:
-            pass
-
-    def close(self):
-        self.conn.close()
-
-    # --- Task State Operations ---
-
-    def register_task(self, task_file: str, state: TaskState = TaskState.BACKLOG) -> int:
-        """Register a new task file in the state machine."""
-        now = time.time()
-        cursor = self.conn.execute(
-            "INSERT OR IGNORE INTO tasks (task_file, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
-            (task_file, state.value, now, now)
-        )
-        self.conn.commit()
-        return cursor.lastrowid or self.get_task_by_file(task_file)["task_id"]
-
-    def get_task(self, task_id: int) -> Optional[dict]:
-        row = self.conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
-        return dict(row) if row else None
-
-    def get_task_by_file(self, task_file: str) -> Optional[dict]:
-        row = self.conn.execute("SELECT * FROM tasks WHERE task_file = ?", (task_file,)).fetchone()
-        return dict(row) if row else None
-
-    def update_state(self, task_id: int, new_state: TaskState):
-        """Transition a task to a new state."""
-        now = time.time()
-        updates = {"state": new_state.value, "updated_at": now}
-        if new_state == TaskState.CLOSED:
-            updates["closed_at"] = now
-
-        set_clause = ", ".join(f"{k} = ?" for k in updates)
-        values = list(updates.values()) + [task_id]
-        self.conn.execute(f"UPDATE tasks SET {set_clause} WHERE task_id = ?", values)
-        self.conn.commit()
-
-    def set_plan(self, task_id: int, plan: str):
-        self.conn.execute("UPDATE tasks SET plan = ?, updated_at = ? WHERE task_id = ?",
-                          (plan, time.time(), task_id))
-        self.conn.commit()
-
-    def set_qa_feedback(self, task_id: int, feedback: str):
-        self.conn.execute(
-            "UPDATE tasks SET qa_feedback = ?, qa_retry_count = qa_retry_count + 1, updated_at = ? WHERE task_id = ?",
-            (feedback, time.time(), task_id))
-        self.conn.commit()
-
-    def increment_qa_retry(self, task_id: int) -> int:
-        """Increment QA retry count and return new count."""
-        cursor = self.conn.execute(
-            "UPDATE tasks SET qa_retry_count = qa_retry_count + 1, updated_at = ? WHERE task_id = ? RETURNING qa_retry_count",
-            (time.time(), task_id))
-        row = cursor.fetchone()
-        self.conn.commit()
-        return row[0] if row else 0
-
-    def get_qa_retry_count(self, task_id: int) -> int:
-        row = self.conn.execute("SELECT qa_retry_count FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
-        return row[0] if row else 0
-
-    def set_evidence_dir(self, task_id: int, evidence_dir: str):
-        self.conn.execute("UPDATE tasks SET evidence_dir = ?, updated_at = ? WHERE task_id = ?",
-                          (evidence_dir, time.time(), task_id))
-        self.conn.commit()
-
-    # --- Spec-First Artifact Tracking (LE-8) ---
-
-    def set_spec_artifacts(self, task_id: int, artifacts: list[str]):
-        """Persist the verified spec artifact paths for a task as a JSON array."""
-        self.conn.execute(
-            "UPDATE tasks SET spec_artifacts = ?, updated_at = ? WHERE task_id = ?",
-            (json.dumps(artifacts), time.time(), task_id))
-        self.conn.commit()
-
-    def get_spec_artifacts(self, task_id: int) -> list[str]:
-        """Return the verified spec artifact paths for a task, or ``[]`` when unset/corrupt."""
-        row = self.conn.execute(
-            "SELECT spec_artifacts FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
-        if not row or not row[0]:
-            return []
-        try:
-            parsed = json.loads(str(row[0]))
-        except (ValueError, TypeError):
-            return []
-        return parsed if isinstance(parsed, list) else []
-
-    def get_active_tasks(self) -> list[dict]:
-        """Get all tasks not in terminal states."""
-        rows = self.conn.execute(
-            "SELECT * FROM tasks WHERE state NOT IN ('closed', 'backlog') ORDER BY updated_at DESC"
-        ).fetchall()
-        return [dict(r) for r in rows]
-
-    def get_tasks_in_state(self, state: TaskState) -> list[dict]:
-        rows = self.conn.execute(
-            "SELECT * FROM tasks WHERE state = ? ORDER BY updated_at DESC", (state.value,)
-        ).fetchall()
-        return [dict(r) for r in rows]
-
-    def get_pending_trigger_tasks(self) -> list[dict]:
-        """Get all tasks waiting for admin trigger (PENDING_TRIGGER status)."""
-        return self.get_tasks_in_state(TaskState.PENDING_TRIGGER)
-
-    # --- Todo Operations (Todo Enforcer) ---
-
-    def add_todo(self, task_id: int, description: str) -> int:
-        cursor = self.conn.execute(
-            "INSERT INTO todos (task_id, description, created_at) VALUES (?, ?, ?)",
-            (task_id, description, time.time()))
-        self.conn.commit()
-        return cursor.lastrowid
-
-    def update_todo_status(self, todo_id: int, status: str):
-        self.conn.execute("UPDATE todos SET status = ? WHERE id = ?", (status, todo_id))
-        self.conn.commit()
-
-    def get_pending_todos(self, task_id: int) -> list[dict]:
-        rows = self.conn.execute(
-            "SELECT * FROM todos WHERE task_id = ? AND status = 'pending' ORDER BY created_at",
-            (task_id,)).fetchall()
-        return [dict(r) for r in rows]
-
-    # --- Dead-Letter Queue (Task 144) ---
-
-    def enqueue_dead_letter(self, task_id: int, stage: str, payload: str, error_reason: str) -> int:
-        cursor = self.conn.execute(
-            "INSERT INTO dead_letter_queue (task_id, stage, payload, error_reason, created_at) VALUES (?, ?, ?, ?, ?)",
-            (task_id, stage, payload, error_reason, time.time()))
-        self.conn.commit()
-        return cursor.lastrowid
-
-    def get_dead_letters(self, task_id: Optional[int] = None) -> list[dict]:
-        if task_id is None:
-            rows = self.conn.execute(
-                "SELECT * FROM dead_letter_queue ORDER BY created_at").fetchall()
-        else:
-            rows = self.conn.execute(
-                "SELECT * FROM dead_letter_queue WHERE task_id = ? ORDER BY created_at",
-                (task_id,)).fetchall()
-        return [dict(r) for r in rows]
-
-    def clear_dead_letter(self, dlq_id: int) -> None:
-        self.conn.execute("DELETE FROM dead_letter_queue WHERE id = ?", (dlq_id,))
-        self.conn.commit()
diff --git a/loop-engine/test_audit_fixes.py b/loop-engine/test_audit_fixes.py
deleted file mode 100644
index 4c172b7..0000000
--- a/loop-engine/test_audit_fixes.py
+++ /dev/null
@@ -1,181 +0,0 @@
-"""Characterization tests for Task 114 pre-production audit fixes.
-
-Covers:
-- daemon.strip_jsonc: quote-aware comment stripping (URLs survive), trailing
-  commas, ${VAR} env resolution
-- qa_engine.decide: first-occurrence verdict logic
-- gateway.ApprovalGateway.handle_callback: approve / reject / stale flows
-- QAEngine.run_qa with a stubbed router: verdict + qa_retry_count increment
-"""
-import asyncio
-import os
-import sys
-import tempfile
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from models import LoopEngineConfig
-
-
-# --- strip_jsonc ---
-
-def test_strip_jsonc_preserves_urls():
-    from daemon import strip_jsonc
-    raw = '{\n  // comment\n  "url": "https://api.example.com/v1"\n}'
-    assert "https://api.example.com/v1" in strip_jsonc(raw)
-
-
-def test_strip_jsonc_trailing_commas_and_comments():
-    from daemon import strip_jsonc
-    raw = '{\n  /* block */ "a": 1,\n  // line\n  "b": 2,\n}'
-    import json
-    assert json.loads(strip_jsonc(raw)) == {"a": 1, "b": 2}
-
-
-def test_strip_jsonc_env_resolution(monkeypatch=None):
-    from daemon import strip_jsonc
-    os.environ["AUDIT_TEST_VAR"] = "resolved"
-    raw = '{"k": "${AUDIT_TEST_VAR}"}'
-    assert strip_jsonc(raw) == '{"k": "resolved"}'
-    del os.environ["AUDIT_TEST_VAR"]
-
-
-def test_load_config_from_repo_root():
-    """Config loads regardless of CWD (repo-root anchoring fix)."""
-    from daemon import load_config
-    cfg = load_config()
-    # chat_id may be the placeholder (0) or the configured operator id —
-    # this test verifies repo-root anchoring, not the operator's chat id.
-    assert isinstance(cfg.approval.chat_id, int)
-    assert "quick" in cfg.categories
-
-
-# --- decide() ---
-
-def test_decide_failed_report_quoting_pass_is_not_positive():
-    """Regression: FAILED report that mentions 'tests must pass' must stay FAILED."""
-    from qa_engine import decide
-    report = ("FAILED: acceptance criterion says tests must be APPROVED, "
-              "but the build is broken.")
-    assert decide(report) == "FAIL"
-
-
-def test_decide_pass_first_wins():
-    from qa_engine import decide
-    assert decide("PASSED. All criteria met. Nothing REJECTED.") == "PASS"
-
-
-def test_decide_fail_first_wins():
-    from qa_engine import decide
-    assert decide("REJECTED after initial PASSED-looking noise.") == "FAIL"
-
-
-def test_decide_no_verdict_defaults_to_fail():
-    from qa_engine import decide
-    assert decide("The build produced no clear verdict.") == "FAIL"
-
-
-# --- gateway handle_callback ---
-
-def _gateway_with_pending(key):
-    from gateway import ApprovalGateway
-    gw = ApprovalGateway(LoopEngineConfig(approval={"chat_id": 1}))
-    gw.pending[key] = asyncio.Event()
-    gw.results[key] = False
-    return gw
-
-
-def test_handle_callback_approve():
-    gw = _gateway_with_pending("7:Plan Approval")
-    ack = gw.handle_callback("approve:7:Plan Approval")
-    assert ack is not None
-    assert gw.results["7:Plan Approval"] is True
-
-
-def test_handle_callback_reject():
-    gw = _gateway_with_pending("7:Plan Approval")
-    ack = gw.handle_callback("reject:7:Plan Approval")
-    assert ack is not None
-    assert gw.results["7:Plan Approval"] is False
-
-
-def test_handle_callback_stale_returns_none():
-    from gateway import ApprovalGateway
-    gw = ApprovalGateway(LoopEngineConfig(approval={"chat_id": 1}))
-    assert gw.handle_callback("approve:999:Plan Approval") is None
-    assert gw.handle_callback("nonsense") is None
-
-
-# --- QAEngine with stubbed router ---
-
-class _StubRouter:
-    def __init__(self, report):
-        self.report = report
-        self.called = False
-
-    def route_qa(self, task_content, diff=""):
-        return {}
-
-    def route_review(self, task_content, qa_report=""):
-        return {}
-
-    def call_llm(self, routing):
-        self.called = True
-        return self.report
-
-
-def _qa_engine(report):
-    from qa_engine import QAEngine
-    from state import StateMachine
-    tmp = tempfile.TemporaryDirectory()
-    sm = StateMachine(os.path.join(tmp.name, "t.db"))
-    cfg = LoopEngineConfig(approval={"chat_id": 1},
-                           evidence_dir=os.path.join(tmp.name, "evidence"))
-    stub = _StubRouter(report)
-    return QAEngine(cfg, sm, stub), sm, tmp
-
-
-def test_run_qa_failed_increments_retry_counter():
-    qa, sm, tmp = _qa_engine(
-        "FAILED: edge case unhandled — criteria mention APPROVED output only.")
-    tid = sm.register_task("tasks/backlog/42-audit.md")  # pipeline registers before QA
-    result = qa.run_qa(tid, "task content", "diff")
-    assert result["result"] == "FAILED"
-    assert sm.get_qa_retry_count(tid) == 1
-    sm.close()
-    tmp.cleanup()
-
-
-def test_run_qa_passed_does_not_increment():
-    qa, sm, tmp = _qa_engine("PASSED. All acceptance criteria verified.")
-    tid = sm.register_task("tasks/backlog/43-audit.md")
-    result = qa.run_qa(tid, "task content", "diff")
-    assert result["result"] == "PASSED"
-    assert sm.get_qa_retry_count(tid) == 0
-    sm.close()
-    tmp.cleanup()
-
-
-def test_run_review_rejected_on_ambiguous_report():
-    qa, sm, tmp = _qa_engine("")
-    tid = sm.register_task("tasks/backlog/44-audit.md")
-    result = qa.run_review(tid, "task content",
-                           "QA report says PASSED but review finds NEEDS_WORK.")
-    assert result["result"] == "REJECTED"
-    sm.close()
-    tmp.cleanup()
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = failed = 0
-    for t in tests:
-        try:
-            t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            print(f"  FAIL: {t.__name__}: {e}")
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
diff --git a/loop-engine/test_blast_radius.py b/loop-engine/test_blast_radius.py
deleted file mode 100644
index edede0c..0000000
--- a/loop-engine/test_blast_radius.py
+++ /dev/null
@@ -1,526 +0,0 @@
-"""Tests for blast_radius.py — Monorepo Blast-Radius Analyzer (Task 141).
-
-Covers the public API (``extract_modified_paths``, ``discover_packages``,
-``find_owning_package``, ``build_dependency_map``, ``calculate_affected_paths``)
-and the ``ToolchainRunner`` workspace-scoping gate in verifier.py that consumes
-the matrix (including the conservative fallback and the ``skip_unaffected``
-rollback flag).
-"""
-import json
-import os
-import sys
-from pathlib import Path
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from blast_radius import (
-    _PSEUDO_MANIFEST,
-    BlastRadiusMatrix,
-    build_dependency_map,
-    calculate_affected_paths,
-    discover_packages,
-    extract_modified_paths,
-    find_owning_package,
-)
-from models import StackProfileConfig, StackToolchainConfig
-from stacks import StackProfile
-from verifier import ToolchainRunner
-
-# ---------------------------------------------------------------------------
-# Fixtures / helpers
-# ---------------------------------------------------------------------------
-
-
-def write(path: Path, content: str = "") -> Path:
-    """Write ``content`` to ``path`` (creating parents). Returns the path.
-
-    Callers pass the FULL target path as the first argument (e.g.
-    ``write(root / "package.json", body)``); the previous split-signature
-    (root, rel, content) mis-parsed the content as a relative path and
-    created a directory named after the file instead of the file itself.
-    """
-    path.parent.mkdir(parents=True, exist_ok=True)
-    path.write_text(content, encoding="utf-8")
-    return path
-
-
-def node_manifest(name: str, deps: dict | None = None, extra: dict | None = None) -> str:
-    """Build a package.json body with optional dependency section + extra keys."""
-    data: dict = {"name": name, "version": "1.0.0"}
-    if deps:
-        data["dependencies"] = deps
-    if extra:
-        data.update(extra)
-    return json.dumps(data)
-
-
-def py_manifest(name: str, deps: list | None = None,
-                extra_text: str = "") -> str:
-    """Build a pyproject.toml body with optional dependencies + extra TOML."""
-    lines = ["[project]", f'name = "{name}"', 'version = "1.0.0"']
-    if deps:
-        lines.append("dependencies = [")
-        for dep in deps:
-            lines.append(f'    "{dep}",')
-        lines.append("]")
-    if extra_text:
-        lines.append(extra_text)
-    return "\n".join(lines)
-
-
-def go_manifest(module: str, requires: list | None = None,
-                replaces: list | None = None) -> str:
-    """Build a go.mod body with optional require/replace blocks."""
-    lines = [f"module {module}", "", "go 1.22"]
-    if requires:
-        lines.append("require (")
-        for req in requires:
-            lines.append(f"    {req} v1.0.0")
-        lines.append(")")
-    if replaces:
-        lines.append("replace (")
-        for rep in replaces:
-            lines.append(f"    {rep}")
-        lines.append(")")
-    return "\n".join(lines)
-
-
-def make_monorepo(root: Path) -> None:
-    """Create a small polyglot monorepo fixture.
-
-    Layout:
-      package.json                 (root, name "hq-root", workspaces globs)
-      packages/shared-schema/      (pyproject, named "shared-schema")
-      services/service-a/          (package.json, depends on "shared-schema")
-      services/service-b/          (pyproject, independent)
-      apps/gateway/                (go.mod, module "hq/gateway", requires "shared-schema")
-    """
-    write(root / "package.json",
-          node_manifest("hq-root", extra={"private": True,
-                                          "workspaces": ["packages/*", "services/*"]}))
-    write(root / "packages/shared-schema/pyproject.toml", py_manifest("shared-schema"))
-    write(root / "packages/shared-schema/README.md", "shared schema docs")
-    write(root / "services/service-a/package.json",
-          node_manifest("service-a", {"shared-schema": "workspace:*"}))
-    write(root / "services/service-a/index.ts", "import { x } from 'shared-schema'\n")
-    write(root / "services/service-b/pyproject.toml", py_manifest("service-b"))
-    write(root / "services/service-b/app.py", "print('b')\n")
-    write(root / "apps/gateway/go.mod",
-          go_manifest("hq/gateway", requires=["shared-schema"]))
-    write(root / "apps/gateway/main.go", "package main\n")
-
-
-# ---------------------------------------------------------------------------
-# extract_modified_paths
-# ---------------------------------------------------------------------------
-
-
-def test_extract_modified_paths_returns_bside_deduped():
-    diff = (
-        "diff --git a/packages/shared-schema/types.py b/packages/shared-schema/types.py\n"
-        "index 111..222 100644\n"
-        "--- a/packages/shared-schema/types.py\n"
-        "+++ b/packages/shared-schema/types.py\n"
-        "@@ -1,7 +1,7 @@\n"
-        "diff --git a/services/a/x.ts b/services/a/x.ts\n"
-        "diff --git a/services/a/x.ts b/services/a/x.ts\n"  # duplicate b-side
-    )
-    paths = extract_modified_paths(diff)
-    assert paths == ["packages/shared-schema/types.py", "services/a/x.ts"]
-
-
-def test_extract_modified_paths_empty_or_malformed():
-    assert extract_modified_paths("") == []
-    assert extract_modified_paths(None) == []  # type: ignore[arg-type]
-    assert extract_modified_paths("plain text without headers") == []
-
-
-def test_extract_modified_paths_rename_uses_bside():
-    diff = "diff --git a/old.py b/new.py\n"
-    assert extract_modified_paths(diff) == ["new.py"]
-
-
-# ---------------------------------------------------------------------------
-# discover_packages
-# ---------------------------------------------------------------------------
-
-
-def test_discover_packages_polyglot_monorepo(tmp_path):
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-
-    packages = discover_packages(root)
-
-    # Root package first (path "."), then deterministic path order.
-    assert [p.path for p in packages] == [
-        ".", "apps/gateway", "packages/shared-schema",
-        "services/service-a", "services/service-b",
-    ]
-    assert packages[0].name == "hq-root"
-    assert packages[0].manifest == "package.json"
-    by_path = {p.path: p for p in packages}
-    assert by_path["packages/shared-schema"].name == "shared-schema"
-    assert by_path["packages/shared-schema"].manifest == "pyproject.toml"
-    assert by_path["apps/gateway"].name == "hq/gateway"
-    assert by_path["apps/gateway"].manifest == "go.mod"
-    assert by_path["services/service-a"].name == "service-a"
-    assert by_path["services/service-b"].name == "service-b"
-
-
-def test_discover_packages_prunes_noise_dirs(tmp_path):
-    root = tmp_path / "monorepo"
-    write(root / "package.json", node_manifest("root"))
-    write(root / "packages/real/package.json", node_manifest("real"))
-    # Noise dirs that must never become package boundaries.
-    write(root / "node_modules/dep/package.json", node_manifest("dep"))
-    write(root / ".venv/lib/py/site-packages/x/pyproject.toml", py_manifest("venv-x"))
-    write(root / ".hidden/pkg/package.json", node_manifest("hidden"))
-
-    paths = [p.path for p in discover_packages(root)]
-    assert paths == [".", "packages/real"]
-    assert "node_modules/dep" not in paths
-    assert ".venv" not in paths
-    assert ".hidden/pkg" not in paths
-
-
-def test_discover_packages_workspaces_glob_pseudo_manifest(tmp_path):
-    root = tmp_path / "monorepo"
-    write(root / "package.json",
-          node_manifest("root", extra={"workspaces": ["packages/*"]}))
-    # A workspace dir WITHOUT any manifest file gains a pseudo-manifest entry.
-    write(root / "packages/empty/README.md", "no manifest here")
-
-    packages = discover_packages(root)
-    by_path = {p.path: p for p in packages}
-    assert "packages/empty" in by_path
-    assert by_path["packages/empty"].name == "empty"
-    assert by_path["packages/empty"].manifest == _PSEUDO_MANIFEST
-
-
-def test_discover_packages_missing_root_returns_empty(tmp_path):
-    assert discover_packages(tmp_path / "does-not-exist") == []
-
-
-# ---------------------------------------------------------------------------
-# find_owning_package
-# ---------------------------------------------------------------------------
-
-
-def test_find_owning_package_deepest_owner_wins(tmp_path):
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-    packages = discover_packages(root)
-
-    assert find_owning_package("packages/shared-schema/types.py", packages).name == "shared-schema"
-    assert find_owning_package("packages/shared-schema/sub/deep.py", packages).name == "shared-schema"
-    assert find_owning_package("apps/gateway/main.go", packages).name == "hq/gateway"
-
-
-def test_find_owning_package_root_fallback(tmp_path):
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-    packages = discover_packages(root)
-
-    # A repo-root file is owned by the root package (".").
-    assert find_owning_package("README.md", packages).name == "hq-root"
-
-
-def test_find_owning_package_none_without_root_package(tmp_path):
-    root = tmp_path / "monorepo"
-    # No root manifest: only a nested package exists.
-    write(root / "packages/a/package.json", node_manifest("a"))
-
-    packages = discover_packages(root)
-    assert find_owning_package("unowned.txt", packages) is None
-    assert find_owning_package("packages/a/src.py", packages).name == "a"
-
-
-# ---------------------------------------------------------------------------
-# build_dependency_map
-# ---------------------------------------------------------------------------
-
-
-def test_build_dependency_map_polyglot_edges(tmp_path):
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-    packages = discover_packages(root)
-
-    dep_map = build_dependency_map(packages, root)
-    by_pkg = {d.package: d for d in dep_map}
-
-    # service-a depends on shared-schema via workspace:* protocol
-    assert by_pkg["service-a"].depends_on == ["shared-schema"]
-    # hq/gateway (go.mod) requires shared-schema — name-edge via require block
-    assert by_pkg["hq/gateway"].depends_on == ["shared-schema"]
-    # shared-schema itself has no local deps
-    assert by_pkg["shared-schema"].depends_on == []
-    # independent service-b
-    assert by_pkg["service-b"].depends_on == []
-    # root package has no local deps
-    assert by_pkg["hq-root"].depends_on == []
-
-
-def test_build_dependency_map_deterministic_order(tmp_path):
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-    packages = discover_packages(root)
-
-    dep_map = build_dependency_map(packages, root)
-    # One entry per discovered package, in the same deterministic order as
-    # discover_packages (root first, then path-sorted).
-    assert [d.package for d in dep_map] == [p.name for p in packages]
-    # Every entry has a sorted depends_on list.
-    for d in dep_map:
-        assert d.depends_on == sorted(d.depends_on)
-
-
-def test_build_dependency_map_file_reference_resolves_local(tmp_path):
-    root = tmp_path / "monorepo"
-    write(root / "package.json", node_manifest("root"))
-    write(root / "packages/lib-a/package.json", node_manifest("lib-a"))
-    # lib-b depends on lib-a via a relative file: reference
-    write(root / "packages/lib-b/package.json",
-          node_manifest("lib-b", {"lib-a": "file:../lib-a"}))
-
-    packages = discover_packages(root)
-    dep_map = build_dependency_map(packages, root)
-    by_pkg = {d.package: d for d in dep_map}
-
-    assert by_pkg["lib-b"].depends_on == ["lib-a"]
-    assert by_pkg["lib-a"].depends_on == []
-
-
-# ---------------------------------------------------------------------------
-# calculate_affected_paths
-# ---------------------------------------------------------------------------
-
-
-def test_calculate_affected_paths_shared_schema_closure(tmp_path):
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-
-    matrix = calculate_affected_paths(
-        ["packages/shared-schema/types.py"], root
-    )
-
-    assert matrix.modified_files == ["packages/shared-schema/types.py"]
-    # Directly modified package PLUS transitive dependents (service-a,
-    # hq/gateway both depend on shared-schema).
-    assert matrix.affected_packages == [
-        "hq/gateway", "service-a", "shared-schema",
-    ]
-    assert matrix.affected_paths == [
-        "apps/gateway", "packages/shared-schema", "services/service-a",
-    ]
-    # service-b and the root are outside the reverse-dependency closure.
-    assert matrix.unaffected_packages == ["hq-root", "service-b"]
-    assert matrix.root_owned_files == []
-
-
-def test_calculate_affected_paths_independent_package_only(tmp_path):
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-
-    matrix = calculate_affected_paths(["services/service-b/app.py"], root)
-
-    assert matrix.affected_packages == ["service-b"]
-    assert matrix.affected_paths == ["services/service-b"]
-    assert matrix.unaffected_packages == [
-        "hq-root", "hq/gateway", "service-a", "shared-schema",
-    ]
-    assert matrix.root_owned_files == []
-
-
-def test_calculate_affected_paths_root_owned_files(tmp_path):
-    root = tmp_path / "monorepo"
-    # Only a nested package exists — no root manifest.
-    write(root / "packages/a/package.json", node_manifest("a"))
-    write(root / "README.md", "# Docs\n")
-
-    matrix = calculate_affected_paths(
-        ["README.md", "packages/a/src.py"], root
-    )
-
-    # README.md belongs to no package → root_owned_files.
-    assert matrix.root_owned_files == ["README.md"]
-    assert matrix.affected_packages == ["a"]
-    assert matrix.modified_files == ["README.md", "packages/a/src.py"]
-
-
-def test_calculate_affected_paths_empty_modified_files(tmp_path):
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-
-    matrix = calculate_affected_paths([], root)
-
-    assert matrix.modified_files == []
-    assert matrix.affected_packages == []
-    assert matrix.affected_paths == []
-    assert matrix.unaffected_packages == sorted([
-        "hq-root", "hq/gateway", "shared-schema", "service-a", "service-b",
-    ])
-    assert matrix.root_owned_files == []
-
-
-def test_calculate_affected_paths_result_is_matrix_model():
-    matrix = calculate_affected_paths([], Path("."))
-    # Type-level contract: always returns a BlastRadiusMatrix model instance.
-    assert isinstance(matrix, BlastRadiusMatrix)
-
-
-# ---------------------------------------------------------------------------
-# ToolchainRunner blast-radius workspace scoping (LE-9)
-# ---------------------------------------------------------------------------
-
-
-def make_profile(lint_cmd, build_cmd, test_cmd, name="test-stack") -> StackProfile:
-    cfg = StackProfileConfig(
-        name=name,
-        display_name=f"Test {name}",
-        toolchain=StackToolchainConfig(
-            lint_cmd=lint_cmd, build_cmd=build_cmd, test_cmd=test_cmd
-        ),
-    )
-    return StackProfile(cfg)
-
-
-def diff_for(*paths: str) -> str:
-    """Build a minimal diff touching the given files."""
-    return "".join(
-        f"diff --git a/{p} b/{p}\n"
-        f"index 111..222 100644\n"
-        f"--- a/{p}\n"
-        f"+++ b/{p}\n"
-        f"@@ -1 +1 @@\n"
-        f"-old\n"
-        f"+new\n"
-        for p in paths
-    )
-
-
-def test_runner_skips_unaffected_workspace(tmp_path):
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-    profile = make_profile("echo lint", "echo build", "echo test")
-
-    runner = ToolchainRunner(
-        timeout_per_command=5.0,
-        evidence_base_dir=tmp_path / "evidence",
-        workspace_root=root,
-        skip_unaffected=True,
-    )
-    # Diff touches service-b only; cwd is service-a → unaffected.
-    result = runner.run_sync(
-        profile, task_id=None, cwd=root / "services/service-a",
-        diff_text=diff_for("services/service-b/app.py"),
-    )
-
-    assert result.passed is True
-    assert all(c.skipped for c in result.commands)
-    assert "Blast-radius scoping" in result.summary
-    assert "unaffected" in result.summary
-    # No actual toolchain command ran.
-    assert all(c.command == "none" for c in result.commands)
-
-
-def test_runner_runs_affected_workspace(tmp_path):
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-    profile = make_profile("echo lint", "echo build", "echo test")
-
-    runner = ToolchainRunner(
-        timeout_per_command=5.0,
-        evidence_base_dir=tmp_path / "evidence",
-        workspace_root=root,
-        skip_unaffected=True,
-    )
-    # Diff touches shared-schema; cwd is service-a → service-a is a
-    # transitive dependent → verification MUST run.
-    result = runner.run_sync(
-        profile, task_id=None, cwd=root / "services/service-a",
-        diff_text=diff_for("packages/shared-schema/types.py"),
-    )
-
-    assert result.passed is True
-    assert all(not c.skipped for c in result.commands)
-    assert "Blast-radius scoping" not in result.summary
-
-
-def test_runner_skip_unaffected_flag_disable_runs_full(tmp_path):
-    """Rollback flag: skip_unaffected=False always runs full toolchain."""
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-    profile = make_profile("echo lint", "echo build", "echo test")
-
-    runner = ToolchainRunner(
-        timeout_per_command=5.0,
-        evidence_base_dir=tmp_path / "evidence",
-        workspace_root=root,
-        skip_unaffected=False,
-    )
-    result = runner.run_sync(
-        profile, task_id=None, cwd=root / "services/service-a",
-        diff_text=diff_for("services/service-b/app.py"),
-    )
-
-    assert result.passed is True
-    assert all(not c.skipped for c in result.commands)
-    assert all(c.command == "echo lint" or c.command == "echo build"
-               or c.command == "echo test" for c in result.commands)
-
-
-def test_runner_no_cwd_is_conservative(tmp_path):
-    root = tmp_path / "monorepo"
-    make_monorepo(root)
-    profile = make_profile("echo lint", "echo build", "echo test")
-
-    runner = ToolchainRunner(
-        timeout_per_command=5.0,
-        evidence_base_dir=tmp_path / "evidence",
-        workspace_root=root,
-        skip_unaffected=True,
-    )
-    # No cwd → cannot prove the workspace → verification runs.
-    result = runner.run_sync(
-        profile, task_id=None, cwd=None,
-        diff_text=diff_for("services/service-b/app.py"),
-    )
-    assert all(not c.skipped for c in result.commands)
-
-
-def test_runner_non_monorepo_is_conservative(tmp_path):
-    root = tmp_path / "plain"  # no manifests → not a proven monorepo
-    root.mkdir(parents=True, exist_ok=True)
-    profile = make_profile("echo lint", "echo build", "echo test")
-
-    runner = ToolchainRunner(
-        timeout_per_command=5.0,
-        evidence_base_dir=tmp_path / "evidence",
-        workspace_root=root,
-        skip_unaffected=True,
-    )
-    result = runner.run_sync(
-        profile, task_id=None, cwd=root,
-        diff_text=diff_for("src/main.py"),
-    )
-    assert all(not c.skipped for c in result.commands)
-
-
-def test_runner_root_owned_file_is_conservative(tmp_path):
-    root = tmp_path / "monorepo"
-    # Only a nested package — a root file belongs to no package.
-    write(root / "packages/a/package.json", node_manifest("a"))
-    write(root / "README.md", "# Docs\n")
-    profile = make_profile("echo lint", "echo build", "echo test")
-
-    runner = ToolchainRunner(
-        timeout_per_command=5.0,
-        evidence_base_dir=tmp_path / "evidence",
-        workspace_root=root,
-        skip_unaffected=True,
-    )
-    result = runner.run_sync(
-        profile, task_id=None, cwd=root / "packages/a",
-        diff_text=diff_for("README.md"),
-    )
-    assert all(not c.skipped for c in result.commands)
\ No newline at end of file
diff --git a/loop-engine/test_contract_smoke.py b/loop-engine/test_contract_smoke.py
deleted file mode 100644
index 5360081..0000000
--- a/loop-engine/test_contract_smoke.py
+++ /dev/null
@@ -1,454 +0,0 @@
-"""
-Phase B Contract Governance Smoke Test Suite & Hard Gate (Task 142 / LE-9).
-
-Certifies Phase B end-to-end by driving REAL pipeline components
-(StateMachine, LLMRouter, QAEngine, HandsExecutor, ApprovalGateway,
-LoopEngineDaemon) anchored to an isolated temporary workspace, validating
-contract mutation dispatching, cascade prevention, TypeDriftSentinel,
-Spec-First gating, and Blast-Radius scoping in full daemon lifecycles.
-
-Hermetic pattern mirrors test_polyglot_smoke.py:
-- Isolated tmp_path workspace with stacks/, tasks/{backlog,in-progress,qa,completed}/,
-  loop-engine/{evidence,state}/, dummy AGENTS.md, system-prompt.md, docs/conventions.md,
-  loop-engine.jsonc, packages/shared-schema, services/api, apps/web, docs/adr.
-- daemon.REPO_ROOT patched to tmp_path for duration of each pipeline run.
-- Scripted I/O seams at process boundary only: call_llm, _run_once, request_approval.
-
-Coverage (14 tests):
-  1. contract mutation dispatches downstream tasks
-  2. no duplicate cascades (generated task touching non-schema doesn't cascade)
-  3. type drift sentinel blocks manual DTO
-  4. spec gate blocks unspecified architecture (no ADR)
-  5. spec gate allows verified ADR
-  6. blast-radius scopes monorepo verification (unaffected workspace skipped)
-  7. full Phase B unified lifecycle (Spec → Clean → Sentinel Pass → Blast Scope → QA → Closure → Propagation)
-  8. non-contract diff no propagation
-  9-14. additional contract/sentinel/spec/blast/state edge cases for >=285 gate
-"""
-import asyncio
-import json
-import os
-import sys
-from pathlib import Path
-from unittest.mock import patch
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-import pytest
-
-import daemon
-from models import LoopEngineConfig, TaskState, BlastRadiusConfig, SpecGateConfig, ContractRuleConfig
-from state import StateMachine
-from router import LLMRouter
-from qa_engine import QAEngine
-from executor import HandsExecutor, TERM_BLOCKED, TERM_COMPLETE
-from gateway import ApprovalGateway
-from brainstorm import BrainstormStage
-from contracts import ContractPropagationEngine
-from sentinel import TypeDriftSentinel
-from specs import SpecGateEngine
-from blast_radius import calculate_affected_paths
-from verifier import ToolchainRunner
-
-REAL_REPO_ROOT = daemon.REPO_ROOT
-
-# ---------------------------------------------------------------------------
-# Workspace construction — Phase B contract monorepo
-# ---------------------------------------------------------------------------
-
-_DEFAULT_PROFILES = {
-    "generic": {
-        "display_name": "Generic (Fallback)",
-        "detection": {"marker_files": [], "extensions": [], "task_keywords": []},
-        "skills": [],
-        "preflight": [],
-        "toolchain": {"test_cmd": None, "build_cmd": None, "lint_cmd": None},
-        "model_preferences": {},
-    },
-    "node-ts": {
-        "display_name": "Node.js / TypeScript",
-        "detection": {
-            "marker_files": ["package.json", "tsconfig.json"],
-            "extensions": [".ts", ".tsx", ".js"],
-            "task_keywords": ["node", "typescript", "nextjs", "react"],
-        },
-        "skills": ["nextjs"],
-        "preflight": ["true"],
-        "toolchain": {"test_cmd": "true", "build_cmd": "true", "lint_cmd": "true"},
-        "model_preferences": {},
-    },
-    "python-fastapi": {
-        "display_name": "Python / FastAPI",
-        "detection": {
-            "marker_files": ["pyproject.toml"],
-            "extensions": [".py"],
-            "task_keywords": ["python", "fastapi"],
-        },
-        "skills": ["python-fastapi"],
-        "preflight": ["true"],
-        "toolchain": {"test_cmd": "true", "build_cmd": None, "lint_cmd": "true"},
-        "model_preferences": {},
-    },
-}
-
-def _render_yaml_value(value):
-    import json as _json
-    if isinstance(value, str):
-        return _json.dumps(value)
-    if isinstance(value, (list, dict)):
-        return _json.dumps(value)
-    if value is None:
-        return "null"
-    return str(value)
-
-def _write_profile(path: Path, name: str, profile: dict):
-    lines = [f"name: {_render_yaml_value(name)}", f"display_name: {_render_yaml_value(profile['display_name'])}"]
-    det = profile.get("detection", {})
-    lines.append("detection:")
-    lines.append(f"  marker_files: {_render_yaml_value(det.get('marker_files', []))}")
-    lines.append(f"  extensions: {_render_yaml_value(det.get('extensions', []))}")
-    lines.append(f"  task_keywords: {_render_yaml_value(det.get('task_keywords', []))}")
-    lines.append(f"skills: {_render_yaml_value(profile.get('skills', []))}")
-    lines.append(f"preflight: {_render_yaml_value(profile.get('preflight', []))}")
-    tc = profile.get("toolchain", {})
-    lines.append("toolchain:")
-    for k in ("test_cmd", "build_cmd", "lint_cmd"):
-        lines.append(f"  {k}: {_render_yaml_value(tc.get(k))}")
-    lines.append(f"model_preferences: {_render_yaml_value(profile.get('model_preferences', {}))}")
-    path.write_text("\n".join(lines), encoding="utf-8")
-
-class ScriptedRouter(LLMRouter):
-    def __init__(self, *a, plan_response="Plan ok", qa_responses=None, review_responses=None, **kw):
-        super().__init__(*a, **kw)
-        self.plan_response = plan_response
-        self.qa_responses = list(qa_responses or ["QA PASS"])
-        self.review_responses = list(review_responses or ["REVIEW PASS"])
-        self.seen_stack_profiles = []
-    async def call_llm(self, *args, **kwargs):
-        # Extract stage from prompt if possible
-        prompt = str(args[0]) if args else str(kwargs.get("prompt", ""))
-        stack_profile = kwargs.get("stack_profile")
-        if stack_profile:
-            self.seen_stack_profiles.append(stack_profile)
-        if "QA" in prompt or "qa" in prompt.lower():
-            return self.qa_responses.pop(0) if self.qa_responses else "QA PASS"
-        if "REVIEW" in prompt or "review" in prompt.lower():
-            return self.review_responses.pop(0) if self.review_responses else "REVIEW PASS"
-        return self.plan_response
-
-class FakeHandsExecutor(HandsExecutor):
-    def __init__(self, *a, mode="complete", diff_content=None, **kw):
-        super().__init__(*a, **kw)
-        self.mode = mode
-        self.diff_content = diff_content or "+def smoke_impl():\n+    return 42\n"
-    async def _run_once(self, task_file, prompt):
-        if self.mode == "empty_diff":
-            return {"status": "complete", "stdout": "", "stderr": "", "returncode": 0}
-        if self.mode == "blocked":
-            return {"status": "blocked", "stdout": "[goal:blocked: test reason]", "stderr": "", "returncode": 0}
-        if self.mode == "error":
-            return {"status": "error", "stdout": "", "stderr": "boom", "returncode": 1}
-        # complete — inject diff_content between markers
-        task_path = Path(task_file)
-        content = task_path.read_text(encoding="utf-8") if task_path.exists() else ""
-        # Inject diff block
-        diff_block = f"<!-- BEGIN_GIT_DIFF -->\n```diff\n{self.diff_content}\n```\n<!-- END_GIT_DIFF -->"
-        if "<!-- BEGIN_GIT_DIFF -->" in content:
-            import re
-            content = re.sub(r"<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->", diff_block, content, flags=re.DOTALL)
-            task_path.write_text(content, encoding="utf-8")
-        return {"status": "complete", "stdout": TERM_COMPLETE, "stderr": "", "returncode": 0}
-
-class AutoApproveGateway(ApprovalGateway):
-    def __init__(self, *a, approve_plan=True, approve_closure=True, **kw):
-        super().__init__(*a, **kw)
-        self.approve_plan = approve_plan
-        self.approve_closure = approve_closure
-        self.trigger_cards = []
-        self.trigger_summaries = []
-    async def request_approval(self, task_id, stage, content):
-        if stage == "plan":
-            return self.approve_plan
-        if stage == "closure":
-            return self.approve_closure
-        return True
-    async def send_task_trigger_card(self, task_id, title, file):
-        self.trigger_cards.append((task_id, title, file))
-        return True
-    async def send_boot_scan_summary(self, tasks, top_n=4):
-        self.trigger_summaries.append(tasks)
-        return True
-
-def setup_contract_workspace(tmp_path: Path):
-    """Build isolated Phase B contract monorepo workspace."""
-    root = tmp_path / "contract_ws"
-    (root / "stacks").mkdir(parents=True, exist_ok=True)
-    for d in ["backlog", "in-progress", "qa", "completed"]:
-        (root / "tasks" / d).mkdir(parents=True, exist_ok=True)
-    (root / "loop-engine" / "evidence").mkdir(parents=True, exist_ok=True)
-    (root / "loop-engine" / "state").mkdir(parents=True, exist_ok=True)
-    (root / "docs" / "adr").mkdir(parents=True, exist_ok=True)
-    (root / "packages" / "shared-schema").mkdir(parents=True, exist_ok=True)
-    (root / "services" / "api" / "src").mkdir(parents=True, exist_ok=True)
-    (root / "apps" / "web" / "src").mkdir(parents=True, exist_ok=True)
-
-    # Dummy required files
-    (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
-    (root / "system-prompt.md").write_text("<system_version>9.3.0</system_version>", encoding="utf-8")
-    (root / "docs" / "conventions.md").write_text("# Conventions\n", encoding="utf-8")
-    (root / "loop-engine.jsonc").write_text(json.dumps({"approval": {"chat_id": 1}}), encoding="utf-8")
-
-    # Stack profiles
-    for name, profile in _DEFAULT_PROFILES.items():
-        _write_profile(root / "stacks" / f"{name}.yaml", name, profile)
-
-    # Monorepo manifests
-    (root / "package.json").write_text(json.dumps({"name": "root", "private": True, "workspaces": ["packages/*", "services/*", "apps/*"]}), encoding="utf-8")
-    (root / "packages" / "shared-schema" / "package.json").write_text(json.dumps({"name": "shared-schema", "version": "1.0.0"}), encoding="utf-8")
-    (root / "packages" / "shared-schema" / "types.ts").write_text("export type User = { id: string }\n", encoding="utf-8")
-    (root / "services" / "api" / "package.json").write_text(json.dumps({"name": "api", "version": "1.0.0", "dependencies": {"shared-schema": "workspace:*"}}), encoding="utf-8")
-    (root / "services" / "api" / "src" / "main.ts").write_text("import { User } from 'shared-schema'\n", encoding="utf-8")
-    (root / "apps" / "web" / "package.json").write_text(json.dumps({"name": "web", "version": "1.0.0", "dependencies": {"shared-schema": "workspace:*"}}), encoding="utf-8")
-    (root / "apps" / "web" / "src" / "app.tsx").write_text("import { User } from 'shared-schema'\n", encoding="utf-8")
-    (root / "docs" / "adr" / "0001-init.md").write_text("# ADR 0001\n", encoding="utf-8")
-
-    # Config with all gates enabled
-    from models import _default_contract_rules, _default_spec_rules
-    config = LoopEngineConfig(
-        approval={"chat_id": 1},
-        evidence_dir=str(root / "loop-engine" / "evidence"),
-        stacks_dir=str(root / "stacks"),
-        tasks_dir=str(root / "tasks"),
-        max_qa_retries=3,
-        trigger_mode="auto",
-        contract_rules=_default_contract_rules(),
-        spec_gate=SpecGateConfig(enabled=True, rules=_default_spec_rules()),
-        blast_radius=BlastRadiusConfig(enabled=True),
-    )
-    return root, config
-
-def _make_task_file(root: Path, task_id: int, title: str, goal: str) -> Path:
-    path = root / "tasks" / "backlog" / f"{task_id:02d}-{title.lower().replace(' ', '-')}.md"
-    path.parent.mkdir(parents=True, exist_ok=True)
-    path.write_text(
-        f"# Task {task_id}: {title}\n\n"
-        f"**File:** `tasks/backlog/{path.name}`\n"
-        f"**Source:** orchestrator\n"
-        f"**Type:** feature\n"
-        f"**Status:** open\n\n"
-        f"## Goal\n\n{goal}\n\n"
-        f"## Acceptance Criteria\n\n- [ ] Done\n\n"
-        f"## Definition of Done\n\n- [ ] Done\n\n"
-        f"## Factual Git Diff\n\n<!-- BEGIN_GIT_DIFF -->\n\n<!-- END_GIT_DIFF -->\n",
-        encoding="utf-8",
-    )
-    return path
-
-# ---------------------------------------------------------------------------
-# Phase B Smoke Tests (8 core + 6 extra)
-# ---------------------------------------------------------------------------
-
-def test_smoke_contract_mutation_dispatches_downstream_tasks(tmp_path):
-    """Task modifying shared-schema dispatches downstream tasks."""
-    root, config = setup_contract_workspace(tmp_path)
-    state = StateMachine(root / "loop-engine" / "state" / "loop.db")
-    engine = ContractPropagationEngine(rules=config.contract_rules, tasks_dir=str(root / "tasks"))
-    diff = "diff --git a/packages/shared-schema/types.ts b/packages/shared-schema/types.ts\n+++ b/packages/shared-schema/types.ts\n"
-    # Simulate closure of task 1
-    result = engine.process_task_closure(task_id=1, task_file="tasks/backlog/01-test.md", diff_text=diff, repo_root=root, state=state)
-    assert len(result) >= 1
-    # Check backlog files created with Triggered-By
-    backlog_files = list((root / "tasks" / "backlog").glob("*.md"))
-    assert any("Triggered-By" in p.read_text() for p in backlog_files)
-    # Check SQLite registration
-    pending = state.get_pending_trigger_tasks() if hasattr(state, "get_pending_trigger_tasks") else []
-    # At least one BACKLOG task registered
-    assert len(backlog_files) >= 1
-
-def test_smoke_no_duplicate_cascades(tmp_path):
-    """Generated downstream task touching non-schema doesn't cascade."""
-    root, config = setup_contract_workspace(tmp_path)
-    state = StateMachine(root / "loop-engine" / "state" / "loop.db")
-    engine = ContractPropagationEngine(rules=config.contract_rules, tasks_dir=str(root / "tasks"))
-    # First dispatch from shared-schema
-    diff1 = "diff --git a/packages/shared-schema/types.ts b/packages/shared-schema/types.ts\n"
-    result1 = engine.process_task_closure(task_id=1, task_file="tasks/backlog/01-test.md", diff_text=diff1, repo_root=root, state=state)
-    assert len(result1) >= 1
-    # Second dispatch from generated task diff touching apps/web (not schema)
-    diff2 = "diff --git a/apps/web/src/app.tsx b/apps/web/src/app.tsx\n"
-    result2 = engine.process_task_closure(task_id=result1[0]["task_id"], task_file=result1[0]["file"], diff_text=diff2, repo_root=root, state=state)
-    assert len(result2) == 0
-
-def test_smoke_type_drift_sentinel_blocks_manual_dto(tmp_path):
-    """Manual DTO in apps/web fails sentinel before QA."""
-    diff = "diff --git a/apps/web/src/user.ts b/apps/web/src/user.ts\n+++ b/apps/web/src/user.ts\n@@ -1 +1 @@\n+export interface UserDTO { id: string }\n"
-    sentinel = TypeDriftSentinel()
-    result = sentinel.check_diff(diff)
-    assert not result.passed
-    assert "UserDTO" in result.report_md
-    # ToolchainRunner should fail fast
-    from models import StackProfileConfig, StackToolchainConfig
-    from stacks import StackProfile
-    from verifier import ToolchainRunner
-    cfg = StackProfileConfig(name="test", display_name="Test", toolchain=StackToolchainConfig(test_cmd="true", build_cmd="true", lint_cmd="true"))
-    profile = StackProfile(cfg)
-    runner = ToolchainRunner(workspace_root=root if (root:=tmp_path) else tmp_path, skip_unaffected=False)
-    # Use tmp_path as root without monorepo — sentinel failure path tested via check_diff above
-    # For integration, verify ToolchainRunner with diff containing drift fails
-    import asyncio
-    async def _run():
-        r = await runner.run(profile, diff_text=diff)
-        return r
-    res = asyncio.run(_run())
-    assert not res.passed
-    assert any(c.command == "type-drift-sentinel" for c in res.commands)
-
-def test_smoke_spec_gate_blocks_unspecified_architecture(tmp_path):
-    """Task with architecture keywords but no ADR crashes at spec gate."""
-    root, config = setup_contract_workspace(tmp_path)
-    # Remove ADR to ensure no artifact
-    for p in (root / "docs" / "adr").glob("*.md"):
-        p.unlink()
-    gate = SpecGateEngine(config=config.spec_gate)
-    task_content = "Implement architecture redesign for the system"
-    plan = "We will redesign architecture"
-    rules = gate.evaluate_requirements(task_content, plan)
-    assert len(rules) >= 1
-    result = gate.validate_artifacts(rules, workspace_root=root, diff_text="")
-    assert not result.passed
-
-def test_smoke_spec_gate_allows_verified_adr(tmp_path):
-    """Task with verified ADR passes spec gate."""
-    root, config = setup_contract_workspace(tmp_path)
-    gate = SpecGateEngine(config=config.spec_gate)
-    task_content = "Implement architecture redesign"
-    plan = "Architecture plan"
-    rules = gate.evaluate_requirements(task_content, plan)
-    # ADR exists at docs/adr/0001-init.md
-    result = gate.validate_artifacts(rules, workspace_root=root, diff_text="")
-    assert result.passed
-
-def test_smoke_blast_radius_scopes_monorepo_verification(tmp_path):
-    """Task modifying only apps/web skips services/api verification."""
-    root, config = setup_contract_workspace(tmp_path)
-    from models import StackProfileConfig, StackToolchainConfig
-    from stacks import StackProfile
-    from verifier import ToolchainRunner
-    cfg = StackProfileConfig(name="test", display_name="Test", toolchain=StackToolchainConfig(test_cmd="true", build_cmd="true", lint_cmd="true"))
-    profile = StackProfile(cfg)
-    runner = ToolchainRunner(workspace_root=root, skip_unaffected=True, blast_radius_config=config.blast_radius)
-    diff = "diff --git a/apps/web/src/app.tsx b/apps/web/src/app.tsx\n+++ b/apps/web/src/app.tsx\n"
-    # services/api workspace should be unaffected
-    import asyncio
-    async def _run_affected():
-        return await runner.run(profile, cwd=root / "apps" / "web", diff_text=diff)
-    async def _run_unaffected():
-        return await runner.run(profile, cwd=root / "services" / "api", diff_text=diff)
-    affected = asyncio.run(_run_affected())
-    unaffected = asyncio.run(_run_unaffected())
-    assert all(not c.skipped for c in affected.commands)
-    assert all(c.skipped for c in unaffected.commands)
-
-def test_smoke_full_phase_b_unified_lifecycle(tmp_path):
-    """End-to-end chain: Spec → Sentinel Pass → Blast Scope → QA → Closure → Propagation."""
-    root, config = setup_contract_workspace(tmp_path)
-    # Spec gate passes (ADR exists)
-    gate = SpecGateEngine(config=config.spec_gate)
-    rules = gate.evaluate_requirements("Implement architecture redesign", "")
-    assert gate.validate_artifacts(rules, workspace_root=root, diff_text="").passed
-    # Sentinel passes (no DTO)
-    sentinel = TypeDriftSentinel()
-    diff_clean = "diff --git a/packages/shared-schema/types.ts b/packages/shared-schema/types.ts\n"
-    assert sentinel.check_diff(diff_clean).passed
-    # Blast radius - shared-schema affects all
-    matrix = calculate_affected_paths(["packages/shared-schema/types.ts"], root, config.blast_radius)
-    assert "api" in matrix.affected_packages or "web" in matrix.affected_packages or "shared-schema" in matrix.affected_packages
-    # Toolchain passes
-    from models import StackProfileConfig, StackToolchainConfig
-    from stacks import StackProfile
-    from verifier import ToolchainRunner
-    cfg = StackProfileConfig(name="test", display_name="Test", toolchain=StackToolchainConfig(test_cmd="true", build_cmd="true", lint_cmd="true"))
-    profile = StackProfile(cfg)
-    runner = ToolchainRunner(workspace_root=root, blast_radius_config=config.blast_radius)
-    import asyncio
-    res = asyncio.run(runner.run(profile, cwd=root / "apps" / "web", diff_text=diff_clean))
-    assert res.passed
-    # Contract propagation dispatches
-    state = StateMachine(root / "loop-engine" / "state" / "loop.db")
-    engine = ContractPropagationEngine(rules=config.contract_rules, tasks_dir=str(root / "tasks"))
-    dispatched = engine.process_task_closure(task_id=99, task_file="tasks/backlog/99-test.md", diff_text=diff_clean, repo_root=root, state=state)
-    assert len(dispatched) >= 1
-
-def test_smoke_non_contract_diff_no_propagation(tmp_path):
-    """Non-contract diff produces 0 downstream tasks."""
-    root, config = setup_contract_workspace(tmp_path)
-    state = StateMachine(root / "loop-engine" / "state" / "loop.db")
-    engine = ContractPropagationEngine(rules=config.contract_rules, tasks_dir=str(root / "tasks"))
-    diff = "diff --git a/services/api/src/main.ts b/services/api/src/main.ts\n"
-    result = engine.process_task_closure(task_id=1, task_file="tasks/backlog/01-test.md", diff_text=diff, repo_root=root, state=state)
-    assert len(result) == 0
-
-# Extra 6 for >=285 gate
-
-def test_smoke_contract_rule_matching(tmp_path):
-    """Verify contract rule matching for various patterns."""
-    root, config = setup_contract_workspace(tmp_path)
-    from contracts import match_contract_rules
-    paths = ["packages/shared-schema/types.ts", "openapi/spec.yaml", "prisma/schema.prisma", "proto/service.proto"]
-    matched = match_contract_rules(paths, config.contract_rules)
-    # At least shared-schema should match
-    assert any(r.name == "shared-schema" for r, _ in matched)
-    assert any(r.name == "openapi-spec" for r, _ in matched)
-
-def test_smoke_sentinel_allowed_patterns(tmp_path):
-    """Sentinel allows shared-schema DTOs."""
-    diff = "diff --git a/packages/shared-schema/user.ts b/packages/shared-schema/user.ts\n+++ b/packages/shared-schema/user.ts\n@@ -1 +1 @@\n+export interface UserDTO { id: string }\n"
-    sentinel = TypeDriftSentinel()
-    result = sentinel.check_diff(diff)
-    assert result.passed
-
-def test_smoke_spec_gate_multiple_rules(tmp_path):
-    """Spec gate with multiple firing rules requires multiple artifacts."""
-    root, config = setup_contract_workspace(tmp_path)
-    # Ensure ADR exists but not other artifacts
-    gate = SpecGateEngine(config=config.spec_gate)
-    task = "architecture and api contract and database schema"
-    rules = gate.evaluate_requirements(task, "")
-    assert len(rules) >= 2
-    result = gate.validate_artifacts(rules, workspace_root=root, diff_text="")
-    # Should fail because not all artifacts present (e.g., missing openapi)
-    assert not result.passed
-
-def test_smoke_blast_radius_root_fallback(tmp_path):
-    """Root file change marks all packages affected."""
-    root, config = setup_contract_workspace(tmp_path)
-    # Root file outside packages
-    (root / "README.md").write_text("# root\n")
-    matrix = calculate_affected_paths(["README.md"], root, config.blast_radius)
-    assert matrix.is_monorepo
-    assert len(matrix.affected_packages) == len(matrix.packages) or len(matrix.affected_packages) > 0
-
-def test_smoke_contract_sequential_ids(tmp_path):
-    """Contract dispatch generates sequential IDs."""
-    root, config = setup_contract_workspace(tmp_path)
-    state = StateMachine(root / "loop-engine" / "state" / "loop.db")
-    engine = ContractPropagationEngine(rules=config.contract_rules, tasks_dir=str(root / "tasks"))
-    diff = "diff --git a/packages/shared-schema/types.ts b/packages/shared-schema/types.ts\n"
-    r1 = engine.process_task_closure(task_id=1, task_file="tasks/backlog/01-test.md", diff_text=diff, repo_root=root, state=state)
-    r2 = engine.process_task_closure(task_id=2, task_file="tasks/backlog/02-test.md", diff_text=diff, repo_root=root, state=state)
-    if r1 and r2:
-        assert r2[0]["task_id"] > r1[0]["task_id"]
-
-def test_smoke_state_registration(tmp_path):
-    """Downstream tasks registered as BACKLOG in SQLite."""
-    root, config = setup_contract_workspace(tmp_path)
-    state = StateMachine(root / "loop-engine" / "state" / "loop.db")
-    engine = ContractPropagationEngine(rules=config.contract_rules, tasks_dir=str(root / "tasks"))
-    diff = "diff --git a/packages/shared-schema/types.ts b/packages/shared-schema/types.ts\n"
-    result = engine.process_task_closure(task_id=5, task_file="tasks/backlog/05-test.md", diff_text=diff, repo_root=root, state=state)
-    assert len(result) >= 1
-    # Check state
-    task_id = result[0]["task_id"]
-    rec = state.get_task(task_id) if hasattr(state, "get_task") else None
-    if rec:
-        assert rec["state"] == TaskState.BACKLOG or rec["state"] == "backlog"
diff --git a/loop-engine/test_contracts.py b/loop-engine/test_contracts.py
deleted file mode 100644
index 379c995..0000000
--- a/loop-engine/test_contracts.py
+++ /dev/null
@@ -1,492 +0,0 @@
-"""Tests for Contract Propagation & Downstream Task Dispatcher (LE-6 / Task 138).
-
-Covers:
-1. ``extract_modified_paths`` — git diff path parsing (additions, updates,
-   deletions, dedup, empty).
-2. ``match_contract_rules`` — glob pattern matching across contract families
-   (shared-schema ``**``, openapi ``*.yaml``, prisma extension).
-3. ``discover_next_task_id`` — sequential, gap, multi-folder, and empty layouts.
-4. ``ContractPropagationEngine.process_task_closure`` — batch generation with
-   sequential IDs, canonical Markdown headers, state registration, formatting,
-   and the non-contract no-op.
-5. Daemon integration — task closure triggers downstream backlog tasks through
-   the real ``_process_task`` closure hook.
-"""
-import asyncio
-import os
-import sys
-from pathlib import Path
-from unittest.mock import AsyncMock, MagicMock, patch
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from models import ContractRuleConfig, DownstreamTaskTemplate, LoopEngineConfig, TaskState
-from state import StateMachine
-
-import daemon
-from contracts import (
-    ContractPropagationEngine,
-    discover_next_task_id,
-    extract_modified_paths,
-    match_contract_rules,
-)
-
-
-# ---------------------------------------------------------------------------
-# Fixtures / helpers
-# ---------------------------------------------------------------------------
-
-_MODIFIED_DIFF = """diff --git a/openapi/contract.yaml b/openapi/contract.yaml
-index 1111111..2222222 100644
---- a/openapi/contract.yaml
-+++ b/openapi/contract.yaml
-@@ -1,3 +1,4 @@
--old: value
-+new: value
-"""
-
-_ADDED_DIFF = """diff --git a/packages/shared-schema/v1/types.ts b/packages/shared-schema/v1/types.ts
-new file mode 100644
-index 0000000..e69de29
---- /dev/null
-+++ b/packages/shared-schema/v1/types.ts
-@@ -0,0 +1 @@
-+export type User = { id: string };
-"""
-
-_DELETED_DIFF = """diff --git a/contracts/legacy.yaml b/contracts/legacy.yaml
-deleted file mode 100644
-index 3333333..0000000
---- a/contracts/legacy.yaml
-+++ /dev/null
-@@ -1,2 +0,0 @@
--legacy: gone
-"""
-
-
-def _openapi_rule(templates=None):
-    """Contract rule for OpenAPI specs with one downstream SDK sync task."""
-    return ContractRuleConfig(
-        name="openapi-spec",
-        patterns=["openapi/**", "contracts/*.yaml", "contracts/*.json"],
-        downstream_tasks=templates or [
-            DownstreamTaskTemplate(
-                title_template="Sync SDK with updated {contract_name}",
-                stack="node-ts",
-                goal_template="Update SDK for {contract_name}. Files: {files}",
-                acceptance_criteria=["SDK updated", "Tests pass"],
-            )
-        ],
-    )
-
-
-def _two_template_rule():
-    """OpenAPI rule with TWO downstream templates (batch generation)."""
-    return ContractRuleConfig(
-        name="openapi-spec",
-        patterns=["openapi/**"],
-        downstream_tasks=[
-            DownstreamTaskTemplate(
-                title_template="Regenerate API client for updated {contract_name}",
-                stack="node-ts",
-                goal_template="Regenerate client for {contract_name}. Files: {files}",
-                acceptance_criteria=["Client regenerated"],
-            ),
-            DownstreamTaskTemplate(
-                title_template="Update API docs for {contract_name}",
-                stack="generic",
-                goal_template="Update docs referencing {contract_name}. Files: {files}",
-                acceptance_criteria=["Docs updated"],
-            ),
-        ],
-    )
-
-
-def _make_workspace(tmp_path):
-    """Build tasks/{backlog,in-progress,qa,completed,archive} under tmp_path."""
-    for sub in ("backlog", "in-progress", "qa", "completed", "archive"):
-        (tmp_path / "tasks" / sub).mkdir(parents=True, exist_ok=True)
-    return tmp_path
-
-
-# ---------------------------------------------------------------------------
-# 1. extract_modified_paths
-# ---------------------------------------------------------------------------
-
-def test_extract_modified_paths_new_file():
-    paths = extract_modified_paths(_ADDED_DIFF)
-    assert paths == ["packages/shared-schema/v1/types.ts"]
-
-
-def test_extract_modified_paths_modified_file():
-    assert extract_modified_paths(_MODIFIED_DIFF) == ["openapi/contract.yaml"]
-
-
-def test_extract_modified_paths_deletion():
-    assert extract_modified_paths(_DELETED_DIFF) == ["contracts/legacy.yaml"]
-
-
-def test_extract_modified_paths_deduplicates():
-    diff = _MODIFIED_DIFF + _MODIFIED_DIFF
-    assert extract_modified_paths(diff) == ["openapi/contract.yaml"]
-
-
-def test_extract_modified_paths_empty_diff():
-    assert extract_modified_paths("") == []
-    assert extract_modified_paths("no diff headers here") == []
-
-
-# ---------------------------------------------------------------------------
-# 2. match_contract_rules
-# ---------------------------------------------------------------------------
-
-def test_match_contract_rules_shared_schema_recursive():
-    rule = ContractRuleConfig(name="shared-schema", patterns=["packages/shared-schema/**"])
-    paths = ["packages/shared-schema/v1/types.ts", "src/app.ts"]
-    matches = match_contract_rules(paths, [rule])
-    assert len(matches) == 1
-    matched_rule, matched_files = matches[0]
-    assert matched_rule.name == "shared-schema"
-    assert matched_files == ["packages/shared-schema/v1/types.ts"]
-
-
-def test_match_contract_rules_openapi_yaml():
-    rule = _openapi_rule()
-    paths = ["openapi/petstore.yaml", "src/main.ts"]
-    matches = match_contract_rules(paths, [rule])
-    assert matches[0][1] == ["openapi/petstore.yaml"]
-
-
-def test_match_contract_rules_prisma_extension():
-    rule = ContractRuleConfig(name="prisma-schema", patterns=["*.prisma", "prisma/**"])
-    paths = ["prisma/schema.prisma", "server/index.ts"]
-    matches = match_contract_rules(paths, [rule])
-    assert matches[0][1] == ["prisma/schema.prisma"]
-
-
-def test_match_contract_rules_no_match_returns_empty():
-    rule = _openapi_rule()
-    matches = match_contract_rules(["src/main.ts", "docs/README.md"], [rule])
-    assert matches == []
-
-
-# ---------------------------------------------------------------------------
-# 3. discover_next_task_id
-# ---------------------------------------------------------------------------
-
-def test_discover_next_task_id_sequential(tmp_path):
-    _make_workspace(tmp_path)
-    for i in (1, 2, 3):
-        (tmp_path / "tasks" / "backlog" / f"{i:02d}-task.md").write_text(f"# Task {i}\n")
-    assert discover_next_task_id(tmp_path / "tasks") == 4
-
-
-def test_discover_next_task_id_gap(tmp_path):
-    _make_workspace(tmp_path)
-    (tmp_path / "tasks" / "backlog" / "01-a.md").write_text("# Task 1\n")
-    (tmp_path / "tasks" / "qa" / "05-b.md").write_text("# Task 5\n")
-    assert discover_next_task_id(tmp_path / "tasks") == 6
-
-
-def test_discover_next_task_id_multi_folder(tmp_path):
-    _make_workspace(tmp_path)
-    layout = {
-        "backlog": [7, 12],
-        "in-progress": [8],
-        "qa": [9],
-        "completed": [10],
-        "archive": [11, 13],
-    }
-    for folder, ids in layout.items():
-        for i in ids:
-            (tmp_path / "tasks" / folder / f"{i:02d}-t.md").write_text(f"# Task {i}\n")
-    assert discover_next_task_id(tmp_path / "tasks") == 14
-
-
-def test_discover_next_task_id_empty(tmp_path):
-    _make_workspace(tmp_path)
-    assert discover_next_task_id(tmp_path / "tasks") == 1
-
-
-# ---------------------------------------------------------------------------
-# 4. ContractPropagationEngine.process_task_closure
-# ---------------------------------------------------------------------------
-
-def test_process_task_closure_generates_batch_with_sequential_ids(tmp_path):
-    _make_workspace(tmp_path)
-    (tmp_path / "tasks" / "backlog" / "05-existing.md").write_text("# Task 5\n")
-    state = StateMachine(str(tmp_path / "loop.db"))
-    try:
-        engine = ContractPropagationEngine(
-            rules=[_two_template_rule()], tasks_dir="tasks"
-        )
-        dispatched = engine.process_task_closure(
-            task_id=42,
-            task_file="tasks/completed/05-existing.md",
-            diff_text=_MODIFIED_DIFF,
-            repo_root=tmp_path,
-            state=state,
-        )
-        assert len(dispatched) == 2
-        assert [d["task_id"] for d in dispatched] == [6, 7]
-        assert dispatched[0]["file"] == "tasks/backlog/06-regenerate-api-client-for-updated-openapi-spec.md"
-        assert dispatched[1]["file"] == "tasks/backlog/07-update-api-docs-for-openapi-spec.md"
-
-        first = (tmp_path / "tasks" / "backlog" / "06-regenerate-api-client-for-updated-openapi-spec.md").read_text()
-        second = (tmp_path / "tasks" / "backlog" / "07-update-api-docs-for-openapi-spec.md").read_text()
-
-        # Canonical markdown headers for both generated tasks
-        for body, task_id, title in (
-            (first, 6, "Regenerate API client for updated openapi-spec"),
-            (second, 7, "Update API docs for openapi-spec"),
-        ):
-            assert body.startswith(f"# Task {task_id}: {title}\n")
-            assert "**Source:** contract-propagation" in body
-            assert "**Triggered-By:** Task 42" in body
-            assert "**Stack:**" in body
-            assert "**Type:** feature" in body
-            assert "**Status:** open" in body
-            assert "## Goal" in body
-            assert "## Source Context" in body
-            assert "## Acceptance Criteria" in body
-            assert "<!-- BEGIN_GIT_DIFF -->" in body
-            assert "<!-- END_GIT_DIFF -->" in body
-            assert "openapi/contract.yaml" in body
-    finally:
-        state.close()
-
-
-def test_process_task_closure_formats_title_goal_and_files(tmp_path):
-    _make_workspace(tmp_path)
-    state = StateMachine(str(tmp_path / "loop.db"))
-    try:
-        rule = ContractRuleConfig(
-            name="shared-schema",
-            patterns=["packages/shared-schema/**"],
-            downstream_tasks=[
-                DownstreamTaskTemplate(
-                    title_template="Propagate {contract_name} from Task {triggering_task_id}",
-                    stack="generic",
-                    goal_template="Sync {contract_name} consumers. Files: {files}",
-                    acceptance_criteria=["Consumers updated"],
-                )
-            ],
-        )
-        dispatched = ContractPropagationEngine(rules=[rule], tasks_dir="tasks").process_task_closure(
-            task_id=9,
-            task_file="tasks/completed/09-x.md",
-            diff_text=_ADDED_DIFF,
-            repo_root=tmp_path,
-            state=state,
-        )
-        assert len(dispatched) == 1
-        body = (tmp_path / "tasks" / "backlog" / "01-propagate-shared-schema-from-task-9.md").read_text()
-        assert "# Task 1: Propagate shared-schema from Task 9" in body
-        assert "Sync shared-schema consumers. Files: packages/shared-schema/v1/types.ts" in body
-        assert "- packages/shared-schema/v1/types.ts" in body
-        assert "- [ ] Consumers updated" in body
-    finally:
-        state.close()
-
-
-def test_process_task_closure_registers_in_state_backlog(tmp_path):
-    _make_workspace(tmp_path)
-    state = StateMachine(str(tmp_path / "loop.db"))
-    try:
-        disposed = ContractPropagationEngine(
-            rules=[_openapi_rule()], tasks_dir="tasks"
-        ).process_task_closure(
-            task_id=1,
-            task_file="tasks/completed/01-x.md",
-            diff_text=_MODIFIED_DIFF,
-            repo_root=tmp_path,
-            state=state,
-        )
-        target = tmp_path / "tasks" / "backlog" / "01-sync-sdk-with-updated-openapi-spec.md"
-        assert target.exists()
-        record = state.get_task_by_file(str(target))
-        assert record is not None
-        assert record["state"] == "backlog"
-        assert disposed[0]["task_id"] == record["task_id"]
-    finally:
-        state.close()
-
-
-def test_process_task_closure_non_contract_noop(tmp_path):
-    _make_workspace(tmp_path)
-    state = StateMachine(str(tmp_path / "loop.db"))
-    try:
-        diff = """diff --git a/src/main.ts b/src/main.ts
-index 1111111..2222222 100644
---- a/src/main.ts
-+++ b/src/main.ts
-@@ -1 +1 @@
--console.log("old");
-+console.log("new");
-"""
-        dispatched = ContractPropagationEngine(
-            rules=[_openapi_rule()], tasks_dir="tasks"
-        ).process_task_closure(
-            task_id=1,
-            task_file="tasks/completed/01-x.md",
-            diff_text=diff,
-            repo_root=tmp_path,
-            state=state,
-        )
-        assert dispatched == []
-        assert list((tmp_path / "tasks" / "backlog").glob("*.md")) == []
-    finally:
-        state.close()
-
-
-def test_loop_engine_config_default_contract_rules():
-    cfg = LoopEngineConfig(approval={"chat_id": 0})
-    names = [r.name for r in cfg.contract_rules]
-    assert names == ["openapi-spec", "prisma-schema", "protobuf", "shared-schema"]
-    openapi = cfg.contract_rules[0]
-    assert openapi.patterns == ["openapi/**", "contracts/*.yaml", "contracts/*.json"]
-    assert openapi.downstream_tasks[0].stack == "node-ts"
-
-
-# ---------------------------------------------------------------------------
-# 5. Daemon integration
-# ---------------------------------------------------------------------------
-
-def _make_daemon_stubs(config):
-    router = MagicMock()
-    router.route_plan.return_value = {"plan": "routing"}
-    router.call_llm.return_value = "Approved plan text"
-    gateway = MagicMock()
-    gateway.request_approval = AsyncMock(return_value=True)
-    executor = MagicMock()
-    qa = MagicMock()
-    qa.run_review.return_value = {"result": "APPROVED"}
-    brainstorm = MagicMock()
-    brainstorm.should_trigger.return_value = False
-    return router, gateway, executor, qa, brainstorm
-
-
-def test_daemon_init_wires_propagation_engine():
-    config = LoopEngineConfig(approval={"chat_id": 0})
-    state = MagicMock()
-    router = MagicMock()
-    gateway = MagicMock()
-    executor = MagicMock()
-    qa = MagicMock()
-    brainstorm = MagicMock()
-    d = daemon.LoopEngineDaemon(config, state, router, gateway, executor, qa, brainstorm)
-    assert isinstance(d.propagation_engine, ContractPropagationEngine)
-    assert d.propagation_engine.tasks_dir == Path("tasks")
-
-
-def test_daemon_task_closure_dispatches_downstream_tasks(tmp_path):
-    """Real _process_task closure hook: CLOSED + contract diff -> backlog tasks."""
-    ws = _make_workspace(tmp_path)
-    (ws / "tasks" / "backlog" / "10-existing.md").write_text("# Task 10\n")
-    config = LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto")
-    router, gateway, executor, qa, brainstorm = _make_daemon_stubs(config)
-
-    task_file = ws / "tasks" / "completed" / "10-existing.md"
-    task_file.write_text(
-        "# Task 10: Contract Mutation\n"
-        "**Source:** orchestrator\n"
-        "**Type:** feature\n"
-        "## Goal\nUpdate the OpenAPI contract.\n"
-        "## Factual Git Diff\n"
-        "<!-- BEGIN_GIT_DIFF -->\n"
-        + _MODIFIED_DIFF +
-        "<!-- END_GIT_DIFF -->\n"
-    )
-
-    state = StateMachine(str(ws / "loop.db"))
-    tid = state.register_task(str(task_file), TaskState.AWAITING_CLOSURE)
-    try:
-        async def _run():
-            await daemon._process_task(
-                tid, str(task_file), config, state, router, gateway, executor, qa, brainstorm
-            )
-
-        async def _fake_execute_and_qa(*args, **kwargs):
-            return {"result": "PASSED", "report": "ok"}
-
-        with patch.object(daemon, "_execute_and_qa", new=_fake_execute_and_qa):
-            with patch.object(daemon, "REPO_ROOT", ws):
-                asyncio.run(_run())
-
-        # Trigger task reached CLOSED
-        assert state.get_task(tid)["state"] == "closed"
-
-        # Downstream task generated with next sequential id (11) using the
-        # config's DEFAULT openapi-spec rule template.
-        backlog_files = sorted((ws / "tasks" / "backlog").glob("*.md"))
-        names = [f.name for f in backlog_files]
-        assert any(name.startswith("11-regenerate-api-client-for-updated-openapi-spec") for name in names)
-        generated = ws / "tasks" / "backlog" / "11-regenerate-api-client-for-updated-openapi-spec.md"
-        assert generated.exists()
-        body = generated.read_text()
-        assert f"**Triggered-By:** Task {tid}" in body
-        assert "**Source:** contract-propagation" in body
-        # Registered in the state machine as backlog
-        assert state.get_task_by_file(str(generated))["state"] == "backlog"
-    finally:
-        state.close()
-
-
-def test_daemon_task_closure_noop_without_contract_diff(tmp_path):
-    """Real _process_task closure hook: non-contract diff -> no backlog tasks."""
-    ws = _make_workspace(tmp_path)
-    config = LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto")
-    router, gateway, executor, qa, brainstorm = _make_daemon_stubs(config)
-
-    task_file = ws / "tasks" / "completed" / "20-regular.md"
-    task_file.write_text(
-        "# Task 20: Regular Change\n"
-        "**Source:** orchestrator\n"
-        "**Type:** feature\n"
-        "## Goal\nRefactor a service.\n"
-        "## Factual Git Diff\n"
-        "<!-- BEGIN_GIT_DIFF -->\n"
-        "diff --git a/src/main.ts b/src/main.ts\n"
-        "index 1111111..2222222 100644\n"
-        "--- a/src/main.ts\n"
-        "+++ b/src/main.ts\n"
-        "@@ -1 +1 @@\n"
-        "-old\n"
-        "+new\n"
-        "<!-- END_GIT_DIFF -->\n"
-    )
-
-    state = StateMachine(str(ws / "loop.db"))
-    tid = state.register_task(str(task_file), TaskState.AWAITING_CLOSURE)
-    try:
-        async def _run():
-            await daemon._process_task(
-                tid, str(task_file), config, state, router, gateway, executor, qa, brainstorm
-            )
-
-        async def _fake_execute_and_qa(*args, **kwargs):
-            return {"result": "PASSED", "report": "ok"}
-
-        with patch.object(daemon, "_execute_and_qa", new=_fake_execute_and_qa):
-            with patch.object(daemon, "REPO_ROOT", ws):
-                asyncio.run(_run())
-
-        assert state.get_task(tid)["state"] == "closed"
-        assert list((ws / "tasks" / "backlog").glob("*.md")) == []
-    finally:
-        state.close()
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = failed = 0
-    for t in tests:
-        try:
-            t(Path("/tmp/contracts-test-ws")) if "tmp_path" in t.__code__.co_varnames else t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            print(f"  FAIL: {t.__name__}: {e}")
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
\ No newline at end of file
diff --git a/loop-engine/test_executor.py b/loop-engine/test_executor.py
deleted file mode 100644
index c993684..0000000
--- a/loop-engine/test_executor.py
+++ /dev/null
@@ -1,308 +0,0 @@
-"""Tests for executor.py — Goal Plugin delegation with transport retry."""
-import sys, os
-sys.path.insert(0, os.path.dirname(__file__))
-
-import asyncio
-import signal
-
-from executor import (
-    TERM_COMPLETE, TERM_BLOCKED, TRANSPORT_ERROR, MAX_RETRIES, RETRY_DELAY,
-    HandsExecutor,
-)
-from models import LoopEngineConfig, StackProfileConfig
-from stacks import StackProfile
-
-
-def _cfg():
-    return LoopEngineConfig(approval={"chat_id": 123})
-
-
-def _make_stack_profile(skills=None, toolchain=None, preflight=None):
-    return StackProfile(StackProfileConfig(
-        name="test-stack", display_name="Test Stack",
-        skills=skills or [], toolchain=toolchain or {},
-        preflight=preflight or []))
-
-
-def test_terminal_complete():
-    assert TERM_COMPLETE.search("Done! [goal:complete]") is not None
-    assert TERM_COMPLETE.search("No marker") is None
-
-
-def test_terminal_complete_case_insensitive():
-    assert TERM_COMPLETE.search("Done! [GOAL:COMPLETE]") is not None
-    assert TERM_COMPLETE.search("Done! [Goal:Complete]") is not None
-
-
-def test_terminal_blocked():
-    assert TERM_BLOCKED.search("Cannot proceed [goal:blocked]") is not None
-    assert TERM_BLOCKED.search("No marker") is None
-
-
-def test_terminal_blocked_reason():
-    m = TERM_BLOCKED.search("Cannot proceed [goal:blocked: missing db credentials]")
-    assert m is not None
-    assert m.group(1).strip() == "missing db credentials"
-
-
-def test_terminal_blocked_reason_uppercase():
-    m = TERM_BLOCKED.search("Cannot proceed [GOAL:BLOCKED: compilation error]")
-    assert m is not None
-    assert m.group(1).strip() == "compilation error"
-
-
-def test_terminal_blocked_no_reason():
-    m = TERM_BLOCKED.search("Cannot proceed [goal:blocked]")
-    assert m is not None
-    assert m.group(1) is None
-
-
-def test_terminal_complete_multiline():
-    text = "Line 1\nLine 2\nTask done [goal:complete]\nLine 4"
-    assert TERM_COMPLETE.search(text) is not None
-
-
-def test_terminal_blocked_multiline():
-    text = "Error occurred\nCannot continue [goal:blocked]"
-    assert TERM_BLOCKED.search(text) is not None
-
-
-def test_transport_error_detection():
-    assert TRANSPORT_ERROR.search("stream disconnected before completion") is not None
-    assert TRANSPORT_ERROR.search("ECONNRESET") is not None
-    assert TRANSPORT_ERROR.search("ETIMEDOUT") is not None
-    assert TRANSPORT_ERROR.search("Connection reset by peer") is not None
-    assert TRANSPORT_ERROR.search("No transport error here") is None
-
-
-def test_retry_constants():
-    assert MAX_RETRIES == 3
-    assert RETRY_DELAY == 5
-
-
-def test_config_has_timeout():
-    cfg = _cfg()
-    assert cfg.idle.max_retries > 0
-    assert cfg.idle.thinking_timeout_seconds > 0
-
-
-def test_executor_instantiation():
-    from executor import HandsExecutor
-    from state import StateMachine
-    import tempfile
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        exe = HandsExecutor(_cfg(), sm)
-        assert exe.config is not None
-        assert exe.state is not None
-        sm.close()
-
-
-# --- _build_prompt (LE-4) ---
-
-def _make_executor():
-    from state import StateMachine
-    import tempfile
-    tmp = tempfile.mkdtemp()
-    sm = StateMachine(os.path.join(tmp, "test.db"))
-    return HandsExecutor(_cfg(), sm), sm
-
-
-def test_build_prompt_empty_profile():
-    exe, sm = _make_executor()
-    try:
-        prompt = exe._build_prompt("/tmp/task.md")
-        assert "<task_instructions>" in prompt
-        assert "Read the task file at /tmp/task.md and implement it." in prompt
-        assert "<goal_rules>" in prompt
-        assert "[goal:complete]" in prompt
-        assert "[goal:blocked: <reason>]" in prompt
-        assert "<stack_context" not in prompt
-        assert "<blueprint_context>" not in prompt
-        assert "<qa_feedback>" not in prompt
-    finally:
-        sm.close()
-
-
-def test_build_prompt_stack_profile():
-    exe, sm = _make_executor()
-    try:
-        profile = _make_stack_profile(
-            skills=["android-kotlin"],
-            toolchain={"test_cmd": "./gradlew test", "build_cmd": "./gradlew assembleDebug", "lint_cmd": "./gradlew ktlintCheck"},
-            preflight=["java -version"],
-        )
-        prompt = exe._build_prompt("/tmp/task.md", stack_profile=profile)
-        assert '<stack_context name="test-stack" display_name="Test Stack">' in prompt
-        assert "MANDATORY: Load required skills via the native skill tool: android-kotlin" in prompt
-        assert "test='./gradlew test'" in prompt
-        assert "build='./gradlew assembleDebug'" in prompt
-        assert "lint='./gradlew ktlintCheck'" in prompt
-        assert "Preflight commands: java -version" in prompt
-    finally:
-        sm.close()
-
-
-def test_build_prompt_blueprint_and_qa():
-    exe, sm = _make_executor()
-    try:
-        prompt = exe._build_prompt(
-            "/tmp/task.md",
-            blueprint_context="Approved plan: build feature X",
-            qa_feedback="Fix the null pointer in module Y",
-        )
-        assert "<blueprint_context>" in prompt
-        assert "Approved plan: build feature X" in prompt
-        assert "<qa_feedback>" in prompt
-        assert "Fix the null pointer in module Y" in prompt
-        assert "Address the above QA feedback explicitly." in prompt
-        assert "Do NOT treat this as a new architectural plan." in prompt
-    finally:
-        sm.close()
-
-
-def test_build_prompt_all_sections():
-    exe, sm = _make_executor()
-    try:
-        profile = _make_stack_profile(skills=["python-fastapi"])
-        prompt = exe._build_prompt(
-            "/tmp/task.md", blueprint_context="plan", qa_feedback="fix", stack_profile=profile)
-        assert "<task_instructions>" in prompt
-        assert "<stack_context" in prompt
-        assert "<blueprint_context>" in prompt
-        assert "<qa_feedback>" in prompt
-        assert "<goal_rules>" in prompt
-    finally:
-        sm.close()
-
-
-# --- Semaphore throttling (LE-4) ---
-
-def test_semaphore_initialized():
-    exe, sm = _make_executor()
-    try:
-        assert isinstance(exe._semaphore, asyncio.Semaphore)
-        assert exe._semaphore._value == _cfg().max_parallel_tasks
-    finally:
-        sm.close()
-
-
-def test_semaphore_throttles_concurrency():
-    exe, sm = _make_executor()
-    try:
-        max_concurrent = 0
-        active = 0
-        lock = asyncio.Lock()
-
-        async def worker():
-            nonlocal max_concurrent, active
-            async with exe._semaphore:
-                active += 1
-                max_concurrent = max(max_concurrent, active)
-                await asyncio.sleep(0.05)
-                active -= 1
-
-        async def run():
-            await asyncio.gather(*[worker() for _ in range(8)])
-
-        asyncio.run(run())
-        assert max_concurrent <= _cfg().max_parallel_tasks
-        assert max_concurrent >= 1
-    finally:
-        sm.close()
-
-
-# --- Process group timeout kill (LE-4) ---
-
-def test_run_once_timeout_kills_process_group():
-    exe, sm = _make_executor()
-    try:
-        # Force a tiny timeout so the subprocess exceeds it immediately.
-        exe.config.idle.executing_timeout_seconds = 0.1
-        result = asyncio.run(exe._run_once("/tmp/task.md", "sleep 5"))
-        assert result["status"] == "timeout"
-        assert "Exceeded" in result["error"]
-        assert "timeout" in result["error"]
-    finally:
-        sm.close()
-
-
-def test_run_once_start_new_session_posix():
-    import os as _os
-    exe, sm = _make_executor()
-    try:
-        # Verify the code path sets start_new_session on POSIX by checking
-        # the subprocess is launched in its own session (killpg works).
-        exe.config.idle.executing_timeout_seconds = 0.1
-        result = asyncio.run(exe._run_once("/tmp/task.md", "sleep 5"))
-        assert result["status"] == "timeout"  # proves killpg teardown path ran
-    finally:
-        sm.close()
-
-
-# --- Transport error retries (LE-4) ---
-
-def test_transport_error_retryable():
-    exe, sm = _make_executor()
-    try:
-        calls = {"n": 0}
-
-        async def fake_run_once(task_file, prompt):
-            calls["n"] += 1
-            if calls["n"] < 3:
-                return {"status": "transport_error", "output": "", "error": "ECONNRESET", "elapsed": 0.1}
-            return {"status": "complete", "output": "[goal:complete]", "error": "", "elapsed": 0.1}
-
-        exe._run_once = fake_run_once
-        result = asyncio.run(exe.execute(1, "/tmp/task.md", "content"))
-        assert result["status"] == "complete"
-        assert calls["n"] == 3
-    finally:
-        sm.close()
-
-
-def test_non_retryable_error_no_retry():
-    exe, sm = _make_executor()
-    try:
-        calls = {"n": 0}
-
-        async def fake_run_once(task_file, prompt):
-            calls["n"] += 1
-            return {"status": "error", "output": "", "error": "opencode CLI not found in PATH", "elapsed": 0.1}
-
-        exe._run_once = fake_run_once
-        result = asyncio.run(exe.execute(1, "/tmp/task.md", "content"))
-        assert result["status"] == "error"
-        assert calls["n"] == 1
-    finally:
-        sm.close()
-
-
-def test_blocked_reason_propagated():
-    exe, sm = _make_executor()
-    try:
-        async def fake_run_once(task_file, prompt):
-            return {"status": "blocked", "output": "[goal:blocked: missing db credentials]",
-                    "error": "", "reason": "missing db credentials", "elapsed": 0.1}
-
-        exe._run_once = fake_run_once
-        result = asyncio.run(exe.execute(1, "/tmp/task.md", "content"))
-        assert result["status"] == "blocked"
-        assert result["reason"] == "missing db credentials"
-    finally:
-        sm.close()
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = failed = 0
-    for t in tests:
-        try:
-            t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            print(f"  FAIL: {t.__name__}: {e}")
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
diff --git a/loop-engine/test_gateway_resilience.py b/loop-engine/test_gateway_resilience.py
deleted file mode 100644
index 6e1fa69..0000000
--- a/loop-engine/test_gateway_resilience.py
+++ /dev/null
@@ -1,142 +0,0 @@
-"""Unit tests for Resilient Telegram Gateway + DLQ (Task 144)."""
-import asyncio
-import os
-import sys
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from models import LoopEngineConfig
-from gateway import ApprovalGateway
-from state import StateMachine
-
-
-def _gateway_with_state(tmp_path):
-    cfg = LoopEngineConfig(approval={"chat_id": 1})
-    gw = ApprovalGateway(cfg)
-    sm = StateMachine(str(tmp_path / "loop.db"))
-    gw.set_state(sm)
-    return gw, sm
-
-
-def _err(name, msg="boom"):
-    cls = type(name, (Exception,), {})
-    cls.__module__ = "telegram.error"
-    return cls(msg)
-
-
-def test_exponential_backoff_on_transient_errors(tmp_path):
-    gw, _ = _gateway_with_state(tmp_path)
-    calls = {"n": 0}
-
-    async def flaky():
-        calls["n"] += 1
-        if calls["n"] < 3:
-            raise _err("NetworkError", "net down")
-        return None
-
-    async def _run():
-        # base_delay=0 to keep test fast; verifies retry-until-success
-        return await gw._send_with_retry(flaky, max_retries=3, base_delay=0)
-
-    assert asyncio.run(_run()) is True
-    assert calls["n"] == 3
-
-
-def test_fatal_fail_fast_on_auth_errors(tmp_path):
-    gw, _ = _gateway_with_state(tmp_path)
-    calls = {"n": 0}
-
-    async def bad_token():
-        calls["n"] += 1
-        raise _err("InvalidToken", "unauthorized")
-
-    async def _run():
-        return await gw._send_with_retry(bad_token, max_retries=3, base_delay=0)
-
-    assert asyncio.run(_run()) is False
-    assert calls["n"] == 1
-
-
-def test_dlq_enqueueing_upon_network_failure(tmp_path):
-    gw, sm = _gateway_with_state(tmp_path)
-
-    async def always_fail():
-        raise _err("TimedOut", "timed out")
-
-    async def _run():
-        return await gw._send_with_retry(
-            always_fail, max_retries=2, base_delay=0,
-            task_id=42, stage="plan", content="hello")
-
-    assert asyncio.run(_run()) is False
-    rows = sm.get_dead_letters(42)
-    assert len(rows) == 1
-    assert rows[0]["stage"] == "plan"
-    assert "timed out" in rows[0]["error_reason"]
-
-
-def test_dlq_retrieval_from_sqlite(tmp_path):
-    sm = StateMachine(str(tmp_path / "loop.db"))
-    dlq_id = sm.enqueue_dead_letter(7, "review", "payload", "net err")
-    assert isinstance(dlq_id, int)
-    rows = sm.get_dead_letters(7)
-    assert len(rows) == 1
-    assert rows[0]["payload"] == "payload"
-    sm.clear_dead_letter(rows[0]["id"])
-    assert sm.get_dead_letters(7) == []
-
-
-def test_request_approval_retries_transient_before_giveup(tmp_path):
-    """request_approval must route sends via _send_with_retry (Task 144)."""
-    from unittest.mock import AsyncMock, MagicMock, patch
-
-    gw, sm = _gateway_with_state(tmp_path)
-    gw.config.approval.timeout_seconds = 1
-    mock_bot = MagicMock()
-    calls = {"n": 0}
-
-    async def _send_message(**kwargs):
-        calls["n"] += 1
-        if calls["n"] < 3:
-            raise _err("NetworkError", "socket drop")
-        return MagicMock(message_id=1)
-
-    mock_bot.send_message = AsyncMock(side_effect=_send_message)
-    gw._get_bot = lambda: mock_bot
-    # Avoid poller side effects; approval will timeout -> False, but retries
-    # must already have happened before the wait.
-    gw._ensure_poller = lambda: None
-
-    async def _run():
-        return await gw.request_approval(99, "plan", "content")
-
-    assert asyncio.run(_run()) is False
-    assert calls["n"] == 3
-    # Exhaustion would DLQ only after 3+ retries; success on 3rd means no DLQ.
-    assert sm.get_dead_letters(99) == []
-
-
-def test_request_approval_dlq_after_exhausted_retries(tmp_path):
-    from unittest.mock import AsyncMock, MagicMock
-
-    gw, sm = _gateway_with_state(tmp_path)
-    gw.config.approval.timeout_seconds = 1
-    mock_bot = MagicMock()
-    mock_bot.send_message = AsyncMock(side_effect=_err("TimedOut", "timed out"))
-    # Patch base_delay to 0 for speed
-    orig_retry = gw._send_with_retry
-
-    async def _fast_retry(fn, max_retries=3, base_delay=1.0, **kw):
-        return await orig_retry(fn, max_retries=max_retries, base_delay=0, **kw)
-
-    gw._send_with_retry = _fast_retry
-    gw._get_bot = lambda: mock_bot
-    gw._ensure_poller = lambda: None
-
-    async def _run():
-        return await gw.request_approval(100, "review", "content")
-
-    assert asyncio.run(_run()) is False
-    rows = sm.get_dead_letters(100)
-    assert len(rows) == 1
-    assert "timed out" in rows[0]["error_reason"]
diff --git a/loop-engine/test_le0_fixes.py b/loop-engine/test_le0_fixes.py
deleted file mode 100644
index dd8946d..0000000
--- a/loop-engine/test_le0_fixes.py
+++ /dev/null
@@ -1,494 +0,0 @@
-"""Tests for LE-0.1..LE-0.4 fixes — verification-before-patch."""
-import asyncio
-import os
-import sys
-import tempfile
-from pathlib import Path
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-REPO_ROOT = str(Path(__file__).resolve().parent.parent)
-
-from models import LoopEngineConfig, TaskState
-
-
-def _cfg():
-    return LoopEngineConfig(approval={"chat_id": 123})
-
-
-# --- LE-0.1: blueprint_context threading ---
-
-def test_executor_blueprint_context_injected():
-    from executor import HandsExecutor
-    from state import StateMachine
-    import inspect
-    sig = inspect.signature(HandsExecutor.execute)
-    assert "blueprint_context" in sig.parameters, "executor.execute missing blueprint_context param"
-    assert sig.parameters["blueprint_context"].default == ""
-    # Check prompt injection by inspecting source
-    src = Path(__file__).parent.joinpath("executor.py").read_text(encoding="utf-8")
-    assert "blueprint_context" in src
-    assert "<blueprint_context>" in src
-
-
-def test_executor_qa_feedback_distinct():
-    from executor import HandsExecutor
-    import inspect
-    sig = inspect.signature(HandsExecutor.execute)
-    assert "qa_feedback" in sig.parameters
-    assert sig.parameters["qa_feedback"].default == ""
-    src = Path(__file__).parent.joinpath("executor.py").read_text(encoding="utf-8")
-    assert "<qa_feedback>" in src
-    # Ensure blueprint_context and qa_feedback are distinct params, not overloaded
-    assert "blueprint_context" in src and "qa_feedback" in src
-    # Prompt must label QA feedback distinctly from blueprint (allow line split)
-    assert "Do NOT treat this" in src
-    assert "as a new architectural plan" in src
-
-
-def test_executor_prompt_build_with_both_contexts():
-    """Directly test prompt construction via _run_once capture."""
-    from executor import HandsExecutor
-    from state import StateMachine
-
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "t.db"))
-        cfg = _cfg()
-        exe = HandsExecutor(cfg, sm)
-
-        # We can't call _run_once without opencode, but we can test execute's prompt building
-        # by checking that execute creates prompt with both sections when provided.
-        # Patch _run_once to capture prompt.
-        captured = {}
-
-        async def fake_run_once(task_file, prompt):
-            captured["prompt"] = prompt
-            return {"status": "complete", "output": "ok", "error": "", "elapsed": 0.1}
-
-        original = exe._run_once
-        exe._run_once = fake_run_once
-
-        async def run():
-            await exe.execute(1, "tasks/backlog/01.md", "content",
-                              blueprint_context="## Plan\n1. do X",
-                              qa_feedback="Fix bug on line 42")
-            p = captured["prompt"]
-            assert "<blueprint_context>" in p
-            assert "## Plan\n1. do X" in p
-            assert "<qa_feedback>" in p
-            assert "Fix bug on line 42" in p
-            # Empty case
-            captured.clear()
-            await exe.execute(1, "tasks/backlog/01.md", "content",
-                              blueprint_context="", qa_feedback="")
-            p2 = captured["prompt"]
-            assert "<blueprint_context>" not in p2
-            assert "<qa_feedback>" not in p2
-
-        asyncio.run(run())
-        exe._run_once = original
-        sm.close()
-
-
-# --- LE-0.2: diff extraction ---
-
-def test_extract_task_diff_clean():
-    from daemon import extract_task_diff
-    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
-        f.write("header\n<!-- BEGIN_GIT_DIFF -->\n+added line\n-removed\n<!-- END_GIT_DIFF -->\nfooter")
-        fname = f.name
-    try:
-        diff = extract_task_diff(Path(fname))
-        assert diff is not None
-        assert "+added line" in diff
-        assert "-removed" in diff
-        assert "header" not in diff
-    finally:
-        os.unlink(fname)
-
-
-def test_extract_task_diff_missing_markers():
-    from daemon import extract_task_diff
-    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
-        f.write("no markers here")
-        fname = f.name
-    try:
-        diff = extract_task_diff(Path(fname))
-        assert diff is None
-    finally:
-        os.unlink(fname)
-
-
-def test_extract_task_diff_empty_block():
-    from daemon import extract_task_diff
-    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
-        f.write("<!-- BEGIN_GIT_DIFF -->\n   \n<!-- END_GIT_DIFF -->")
-        fname = f.name
-    try:
-        diff = extract_task_diff(Path(fname))
-        assert diff == ""  # empty stripped
-        assert not diff.strip()
-    finally:
-        os.unlink(fname)
-
-
-def test_extract_task_diff_malformed_no_end():
-    from daemon import extract_task_diff
-    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
-        f.write("<!-- BEGIN_GIT_DIFF -->\ncontent without end")
-        fname = f.name
-    try:
-        diff = extract_task_diff(Path(fname))
-        assert diff is None
-    finally:
-        os.unlink(fname)
-
-
-# --- LE-0.2: empty diff hard failure in pipeline (integration) ---
-
-def test_daemon_empty_diff_crashes():
-    """Pipeline must CRASHED when diff missing, never call QA."""
-    from daemon import _process_task, extract_task_diff
-    from state import StateMachine
-    from models import TaskState
-    import tempfile
-
-    with tempfile.TemporaryDirectory() as tmp:
-        # Create a task file WITHOUT diff markers
-        task_file = Path(tmp) / "01-test.md"
-        task_file.write_text("# Task 1\n## Goal\nTest\n<!-- BEGIN_GIT_DIFF -->\n<!-- END_GIT_DIFF -->", encoding="utf-8")
-        # Actually this has empty diff -> should crash
-
-        # Minimal stubs
-        cfg = LoopEngineConfig(approval={"chat_id": 1},
-                               evidence_dir=os.path.join(tmp, "evidence"),
-                               max_qa_retries=2)
-        sm = StateMachine(os.path.join(tmp, "t.db"))
-        tid = sm.register_task(str(task_file), TaskState.BACKLOG)
-
-        # Stub router
-        class StubRouter:
-            def route_plan(self, task_content, extra_context=""):
-                return {}
-            def call_llm(self, routing):
-                return "## Plan\nDo thing"
-            def route_qa(self, tc, diff=""):
-                return {}
-            def route_review(self, tc, qa=""):
-                return {}
-            def _resolve_model(self, category):
-                return "stub/model", None
-
-        stub_router = StubRouter()
-
-        # Stub gateway: approve plan
-        class StubGateway:
-            async def request_approval(self, tid, title, content):
-                return True
-
-        # Stub executor: returns complete, but we want empty diff path
-        class StubExecutor:
-            async def execute(self, task_id, task_file, task_content, blueprint_context="", qa_feedback=""):
-                # Simulate Hands writing task file with EMPTY diff block
-                p = Path(task_file)
-                text = p.read_text(encoding="utf-8")
-                # Ensure diff block is empty
-                if "<!-- BEGIN_GIT_DIFF -->" in text:
-                    # Keep empty
-                    pass
-                else:
-                    text += "\n<!-- BEGIN_GIT_DIFF -->\n<!-- END_GIT_DIFF -->\n"
-                    p.write_text(text, encoding="utf-8")
-                return {"status": "complete", "output": "fake output"}
-
-        # Stub QA: should NOT be called if empty diff check works
-        class StubQA:
-            def __init__(self):
-                self.called = False
-            def run_qa(self, tid, tc, diff):
-                self.called = True
-                return {"result": "PASSED", "report": "PASSED"}
-            def run_review(self, tid, tc, qr):
-                return {"result": "APPROVED", "review": "ok"}
-
-        stub_qa = StubQA()
-        from brainstorm import BrainstormStage
-        brainstorm = BrainstormStage(cfg, stub_router, workspace_root=REPO_ROOT)
-        # Ensure brainstorm not triggered — avoid magic word
-        task_file.write_text("# Task 1\nSimple fix no trigger word here", encoding="utf-8")
-
-        asyncio.run(_process_task(tid, str(task_file), cfg, sm, stub_router, StubGateway(), StubExecutor(), stub_qa, brainstorm))
-
-        task = sm.get_task(tid)
-        assert task["state"] == "crashed", f"Expected crashed on empty diff, got {task['state']}"
-        assert not stub_qa.called, "QA should not have been called with empty diff"
-        sm.close()
-
-
-# --- LE-0.3: scoped reimplement (verify function exists and uses state retry) ---
-
-def test_reimplement_task_exists_and_uses_state_retry():
-    src = Path(__file__).parent.joinpath("daemon.py").read_text(encoding="utf-8")
-    assert "_reimplement_task" in src
-    assert "get_qa_retry_count" in src
-    assert "max_qa_retries" in src
-    assert "qa_feedback" in src
-    # After DRY Step 5, shared logic is in _execute_and_qa, so reimplement should call it
-    assert "_execute_and_qa" in src
-    reimplement_block = src.split("async def _reimplement_task")[1].split("async def ")[0]
-    assert "qa_feedback" in reimplement_block
-    assert "_execute_and_qa" in reimplement_block
-    # Must NOT contain plan approval (except closure) or brainstorm in reimplement
-    assert "Closure Approval" in reimplement_block
-    assert "Plan Approval" not in reimplement_block
-    assert "Brainstorm" not in reimplement_block
-    assert "route_plan" not in reimplement_block
-    # Ensure it doesn't recurse to full pipeline process_task
-    assert "await process_task" not in reimplement_block
-    # Verify DRY helper exists and is used by both sites
-    assert "async def _execute_and_qa" in src
-    # _process_task should also use helper
-    process_block = src.split("async def _process_task")[1].split("async def ")[0] if "async def _process_task" in src else ""
-    assert "_execute_and_qa" in process_block
-
-
-def test_daemon_qa_failure_calls_reimplement_not_process_task():
-    src = Path(__file__).parent.joinpath("daemon.py").read_text(encoding="utf-8")
-    # After QA FAILED in _process_task should call _reimplement_task, not process_task
-    assert "async def _process_task" in src
-    process_block = src.split("async def _process_task")[1]
-    assert "if qa_result[\"result\"] == \"FAILED\":" in process_block
-    # Take the first FAILED block inside _process_task (before REVIEW)
-    block = process_block.split("if qa_result[\"result\"] == \"FAILED\":")[1].split("# 5. REVIEW")[0]
-    assert "_reimplement_task" in block
-    # Old buggy recursion must be gone from this block
-    assert "return await process_task" not in block
-
-
-# --- LE-0.4: router memory query ---
-
-def test_router_memory_query_present():
-    src = Path(__file__).parent.joinpath("router.py").read_text(encoding="utf-8")
-    assert "_load_memory_context" in src
-    assert ".opencode/memory" in src
-    assert "memory_context" in src
-    assert "Context Bootstrapping & Memory Protocol" in src
-    # Ensure _build_system_context appends memory
-    assert "<memory_context>" in src
-
-
-def test_router_includes_memory_in_context(tmp_path=None):
-    from router import LLMRouter
-    cfg = _cfg()
-    # Create temp workspace with memory
-    with tempfile.TemporaryDirectory() as tmp:
-        mem_dir = Path(tmp) / ".opencode" / "memory" / "project"
-        mem_dir.mkdir(parents=True)
-        (mem_dir / "test-memory.md").write_text("# Test Memory\nThis is important project rule: always use UTC.", encoding="utf-8")
-        # Also create required fragment files by symlinking from real repo
-        # Router needs personas; copy or link fragments
-        import shutil
-        src_fragments = Path(REPO_ROOT) / "prompts" / "fragments"
-        dst_fragments = Path(tmp) / "prompts" / "fragments"
-        dst_fragments.mkdir(parents=True)
-        for f in src_fragments.glob("*.md"):
-            shutil.copy(f, dst_fragments / f.name)
-        # Also copy AGENTS.md, system-prompt, conventions if needed
-        for rel in ["AGENTS.md", "system-prompt.md", "docs/conventions.md"]:
-            src = Path(REPO_ROOT) / rel
-            dst = Path(tmp) / rel
-            dst.parent.mkdir(parents=True, exist_ok=True)
-            if src.exists():
-                shutil.copy(src, dst)
-
-        router = LLMRouter(cfg, workspace_root=tmp)
-        ctx = router._build_system_context("architect")
-        assert "always use UTC" in ctx
-        assert 'namespace="project"' in ctx
-        assert 'key="test-memory"' in ctx
-
-
-def test_router_without_memory_still_works():
-    from router import LLMRouter
-    cfg = _cfg()
-    with tempfile.TemporaryDirectory() as tmp:
-        # No memory dir
-        import shutil
-        src_fragments = Path(REPO_ROOT) / "prompts" / "fragments"
-        dst_fragments = Path(tmp) / "prompts" / "fragments"
-        dst_fragments.mkdir(parents=True)
-        for f in src_fragments.glob("*.md"):
-            shutil.copy(f, dst_fragments / f.name)
-        for rel in ["AGENTS.md", "system-prompt.md", "docs/conventions.md"]:
-            src = Path(REPO_ROOT) / rel
-            dst = Path(tmp) / rel
-            dst.parent.mkdir(parents=True, exist_ok=True)
-            if src.exists():
-                shutil.copy(src, dst)
-        router = LLMRouter(cfg, workspace_root=tmp)
-        ctx = router._build_system_context("architect")
-        assert "Software Architect" in ctx  # still works without memory
-
-
-def test_reimplement_task_retry_loop_terminates():
-    """Step 2: FAILED, FAILED, PASSED with max=3 → CLOSED, retry count increases, 1 Closure, 0 Plan."""
-    from unittest.mock import patch
-    from daemon import _reimplement_task
-    from state import StateMachine
-    # Mock toolchain to avoid real lint/test execution interfering with QA retry counting
-    patcher = patch('daemon.ToolchainRunner', None)
-    patcher.start()
-
-    with tempfile.TemporaryDirectory() as tmp:
-        task_file = Path(tmp) / "02-retry.md"
-        task_file.write_text("# Task\nSimple no trigger\n<!-- BEGIN_GIT_DIFF -->\ninitial diff\n<!-- END_GIT_DIFF -->", encoding="utf-8")
-
-        cfg = LoopEngineConfig(approval={"chat_id": 1},
-                               evidence_dir=os.path.join(tmp, "evidence"),
-                               max_qa_retries=3)
-        sm = StateMachine(os.path.join(tmp, "t.db"))
-        tid = sm.register_task(str(task_file), TaskState.BACKLOG)
-        # Start at 0, _reimplement will handle FAILED->increment sequence
-        assert sm.get_qa_retry_count(tid) == 0
-
-        # Stub executor always complete + writes valid diff
-        class StubExecutor:
-            async def execute(self, task_id, task_file, task_content, blueprint_context="", qa_feedback=""):
-                p = Path(task_file)
-                text = p.read_text(encoding="utf-8")
-                if "<!-- BEGIN_GIT_DIFF -->" in text and "initial diff" in text:
-                    text = text.replace("initial diff", "+fix diff")
-                    p.write_text(text, encoding="utf-8")
-                elif "<!-- BEGIN_GIT_DIFF -->" in text:
-                    if "+fix" not in text:
-                        text = text.replace("<!-- BEGIN_GIT_DIFF -->", "<!-- BEGIN_GIT_DIFF -->\n+fix")
-                        p.write_text(text, encoding="utf-8")
-                return {"status": "complete", "output": "ok"}
-
-        # Real QA with PreciseRouter: FAILED, FAILED, PASSED - increments via qa_engine's set_qa_feedback
-        from qa_engine import QAEngine
-
-        class PreciseRouter:
-            def __init__(self):
-                self.qa_calls = 0
-            def route_qa(self, tc, diff):
-                return {"kind": "qa"}
-            def route_review(self, tc, qr):
-                return {"kind": "review"}
-            def call_llm(self, routing):
-                kind = routing.get("kind")
-                if kind == "qa":
-                    self.qa_calls += 1
-                    if self.qa_calls <= 2:
-                        return "FAILED: still broken" if self.qa_calls == 1 else "FAILED: second fail"
-                    else:
-                        return "PASSED: ok"
-                else:
-                    return "APPROVED"
-
-        precise_router = PreciseRouter()
-        real_qa = QAEngine(cfg, sm, precise_router)
-
-        class TrackGateway:
-            def __init__(self):
-                self.calls = []
-            async def request_approval(self, tid, title, content):
-                self.calls.append(title)
-                return True
-
-        gw = TrackGateway()
-
-        async def run_with_timeout():
-            await asyncio.wait_for(
-                _reimplement_task(tid, str(task_file), "FAILED: initial", cfg, sm, precise_router, gw, StubExecutor(), real_qa),
-                timeout=5.0
-            )
-
-        asyncio.run(run_with_timeout())
-
-        # Retry count strictly increases: 0->1->2 then PASSED stays 2
-        final_count = sm.get_qa_retry_count(tid)
-        assert final_count == 2, f"expected final retry count 2, got {final_count}"
-        assert precise_router.qa_calls == 3, f"expected 3 QA calls, got {precise_router.qa_calls}"
-        assert gw.calls.count("Closure Approval") == 1, f"Closure calls: {gw.calls}"
-        assert gw.calls.count("Plan Approval") == 0, f"Plan should be 0, got {gw.calls}"
-        task = sm.get_task(tid)
-        assert task["state"] == "closed", f"expected closed, got {task['state']}"
-        sm.close()
-    patcher.stop()
-
-
-def test_reimplement_task_max_one_crashes_with_timeout():
-    """Step 3: max=1 always FAILED → CRASHED, with hard wall-clock timeout guard."""
-    from unittest.mock import patch
-    from daemon import _reimplement_task
-    from state import StateMachine
-    # Mock toolchain to avoid real lint/test execution interfering with retry-loop test
-    patcher = patch('daemon.ToolchainRunner', None)
-    patcher.start()
-
-    with tempfile.TemporaryDirectory() as tmp:
-        task_file = Path(tmp) / "03-max1.md"
-        task_file.write_text("# Task\nSimple no trigger\n<!-- BEGIN_GIT_DIFF -->\ninitial\n<!-- END_GIT_DIFF -->", encoding="utf-8")
-
-        cfg = LoopEngineConfig(approval={"chat_id": 1},
-                               evidence_dir=os.path.join(tmp, "evidence"),
-                               max_qa_retries=1)
-        sm = StateMachine(os.path.join(tmp, "t.db"))
-        tid = sm.register_task(str(task_file), TaskState.BACKLOG)
-        assert sm.get_qa_retry_count(tid) == 0
-
-        class StubExecutor:
-            async def execute(self, task_id, task_file, task_content, blueprint_context="", qa_feedback=""):
-                return {"status": "complete", "output": "ok"}
-
-        from qa_engine import QAEngine
-
-        class AlwaysFailRouter:
-            def route_qa(self, tc, diff):
-                return {"kind": "qa"}
-            def route_review(self, tc, qr):
-                return {"kind": "review"}
-            def call_llm(self, routing):
-                return "FAILED: always"
-
-        always_router = AlwaysFailRouter()
-        real_qa = QAEngine(cfg, sm, always_router)
-
-        class NoopGateway:
-            async def request_approval(self, tid, title, content):
-                assert False, "gateway should not be called on CRASHED path"
-
-        # Hard wall-clock timeout guard: 5 seconds — infinite loop fails loudly
-        async def run_guarded():
-            await asyncio.wait_for(
-                _reimplement_task(tid, str(task_file), "FAILED: initial", cfg, sm, always_router, NoopGateway(), StubExecutor(), real_qa),
-                timeout=5.0
-            )
-
-        try:
-            asyncio.run(run_guarded())
-        except asyncio.TimeoutError:
-            assert False, "test timed out — infinite loop not terminating (retry increment missing?)"
-
-        task = sm.get_task(tid)
-        assert task["state"] == "crashed", f"expected crashed with max=1, got {task['state']}"
-        sm.close()
-    patcher.stop()
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = failed = 0
-    for t in tests:
-        try:
-            t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            import traceback
-            print(f"  FAIL: {t.__name__}: {e}")
-            traceback.print_exc()
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
diff --git a/loop-engine/test_metrics.py b/loop-engine/test_metrics.py
deleted file mode 100644
index c1f7f59..0000000
--- a/loop-engine/test_metrics.py
+++ /dev/null
@@ -1,51 +0,0 @@
-"""Unit tests for Metrics, JSON logging, Sentry (Task 146)."""
-import json
-import logging
-import os
-import sys
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from metrics import JSONLogFormatter, MetricsCollector, init_sentry
-
-
-def test_token_tracking_and_cost():
-    m = MetricsCollector()
-    m.record_llm_call(1, "gpt", prompt_tokens=1000, completion_tokens=1000, duration_seconds=1.0)
-    got = m.get_task_metrics(1)
-    assert got["prompt_tokens"] == 1000
-    assert got["completion_tokens"] == 1000
-    # 1k prompt @0.0015 + 1k completion @0.002 = 0.0035
-    assert abs(got["estimated_cost"] - 0.0035) < 1e-9
-
-
-def test_stage_latency_and_error_tracking():
-    m = MetricsCollector()
-    m.record_stage_duration(2, "plan", 1.5)
-    m.record_error(2, "qa", "boom")
-    got = m.get_task_metrics(2)
-    assert got["stages"]["plan"] == 1.5
-    assert got["errors"] == [{"stage": "qa", "error": "boom"}]
-    summary = m.get_summary()
-    assert summary["total_tasks"] == 1
-    assert summary["total_errors"] == 1
-
-
-def test_json_log_formatting():
-    fmt = JSONLogFormatter()
-    rec = logging.LogRecord("test", logging.INFO, __file__, 10, "hello", None, None)
-    rec.task_id = 9
-    rec.duration_ms = 12
-    out = fmt.format(rec)
-    data = json.loads(out)
-    assert data["level"] == "INFO"
-    assert data["logger"] == "test"
-    assert data["event"] == "hello"
-    assert data["task_id"] == 9
-    assert data["duration_ms"] == 12
-    assert "timestamp" in data
-
-
-def test_sentry_noop_when_unconfigured():
-    assert init_sentry(None) is False
-    assert init_sentry("") is False
diff --git a/loop-engine/test_models.py b/loop-engine/test_models.py
deleted file mode 100644
index da74fed..0000000
--- a/loop-engine/test_models.py
+++ /dev/null
@@ -1,86 +0,0 @@
-"""Tests for models.py — Pydantic config validation."""
-import sys, os
-sys.path.insert(0, os.path.dirname(__file__))
-
-from models import (
-    LoopEngineConfig, TaskState, CategoryConfig,
-    ProviderConcurrency, IdleConfig, ApprovalConfig
-)
-
-
-def test_task_state_values():
-    assert TaskState.BACKLOG.value == "backlog"
-    assert TaskState.IMPLEMENTING.value == "implementing"
-    assert TaskState.CLOSED.value == "closed"
-    assert TaskState.CRASHED.value == "crashed"
-    assert TaskState.PENDING_TRIGGER.value == "pending_trigger"
-    assert TaskState.ABORTED.value == "aborted"
-    assert len(TaskState) == 12
-
-
-def test_category_config():
-    c = CategoryConfig(models=["kimi/kimi-k3"], description="test")
-    assert c.models == ["kimi/kimi-k3"]
-    assert c.reasoning is None
-
-
-def test_category_config_requires_models():
-    try:
-        CategoryConfig(models=[])
-        assert False, "Should have failed"
-    except Exception:
-        pass
-
-
-def test_provider_concurrency_defaults():
-    pc = ProviderConcurrency()
-    assert pc.anthropic == 3
-    assert pc.openai == 3
-
-
-def test_idle_config_defaults():
-    ic = IdleConfig()
-    assert ic.thinking_timeout_seconds == 60
-    assert ic.executing_timeout_seconds == 900
-    assert ic.max_retries == 5
-
-
-def test_approval_config():
-    ac = ApprovalConfig(chat_id=12345)
-    assert ac.bot_token_env == "TELEGRAM_BOT_TOKEN"
-    assert ac.chat_id == 12345
-
-
-def test_loop_engine_config_defaults():
-    cfg = LoopEngineConfig(approval={"chat_id": 123})
-    assert cfg.max_parallel_tasks == 1
-    assert "quick" in cfg.categories
-    assert "deep" in cfg.categories
-    assert cfg.max_qa_retries == 3
-
-
-def test_loop_engine_config_max_parallel_bounds():
-    try:
-        LoopEngineConfig(approval={"chat_id": 1}, max_parallel_tasks=5)
-        assert False, "Should fail: max is 4"
-    except Exception:
-        pass
-
-    cfg = LoopEngineConfig(approval={"chat_id": 1}, max_parallel_tasks=4)
-    assert cfg.max_parallel_tasks == 4
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = 0
-    failed = 0
-    for t in tests:
-        try:
-            t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            print(f"  FAIL: {t.__name__}: {e}")
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
diff --git a/loop-engine/test_multi_project.py b/loop-engine/test_multi_project.py
deleted file mode 100644
index d885b6a..0000000
--- a/loop-engine/test_multi_project.py
+++ /dev/null
@@ -1,86 +0,0 @@
-"""Unit tests for Multi-Project Topic Routing (Task 143)."""
-import os
-import sys
-from pathlib import Path
-from unittest.mock import AsyncMock, MagicMock
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from models import LoopEngineConfig, ProjectTopicConfig
-from multi_project import MultiProjectRouter
-
-
-def _cfg():
-    return [
-        ProjectTopicConfig(topic_id=10, project_name="alpha", workspace_root="/tmp/alpha"),
-        ProjectTopicConfig(topic_id=20, project_name="beta", workspace_root="/tmp/beta"),
-    ]
-
-
-def test_topic_to_workspace_lookup():
-    r = MultiProjectRouter(_cfg())
-    assert r.get_workspace_for_topic(10) == Path("/tmp/alpha")
-    assert r.get_workspace_for_topic(20) == Path("/tmp/beta")
-
-
-def test_workspace_to_topic_lookup():
-    r = MultiProjectRouter(_cfg())
-    assert r.get_topic_for_workspace("/tmp/alpha") == 10
-    assert r.get_topic_for_workspace(Path("/tmp/beta")) == 20
-
-
-def test_task_path_to_topic_resolution():
-    r = MultiProjectRouter(_cfg())
-    assert r.get_topic_for_task("/tmp/alpha/tasks/backlog/01-x.md") == 10
-    assert r.get_topic_for_task("/tmp/beta/tasks/qa/02-y.md") == 20
-
-
-def test_unknown_topic_fallback_none():
-    r = MultiProjectRouter(_cfg())
-    assert r.get_workspace_for_topic(999) is None
-    assert r.get_topic_for_workspace("/tmp/unknown") is None
-    assert r.get_topic_for_task("/tmp/unknown/file.md") is None
-    assert r.get_project_name(999) is None
-
-
-def test_project_name_lookup():
-    r = MultiProjectRouter(_cfg())
-    assert r.get_project_name(10) == "alpha"
-    assert r.get_project_name(20) == "beta"
-
-
-def test_models_multi_project_field_defaults():
-    cfg = LoopEngineConfig(approval={"chat_id": 1})
-    assert cfg.multi_project == []
-    cfg2 = LoopEngineConfig(
-        approval={"chat_id": 1},
-        multi_project=[
-            {"topic_id": 1, "project_name": "p", "workspace_root": "/tmp/p"}
-        ],
-    )
-    assert cfg2.multi_project[0].topic_id == 1
-    assert cfg2.multi_project[0].target_hashtags == ["bug", "feature"]
-
-
-def test_gateway_message_thread_id_propagation():
-    import asyncio
-    from gateway import ApprovalGateway
-
-    cfg = LoopEngineConfig(approval={"chat_id": 123})
-    gw = ApprovalGateway(cfg)
-    mock_bot = MagicMock()
-    mock_bot.send_message = AsyncMock(return_value=MagicMock())
-    gw._get_bot = lambda: mock_bot
-
-    async def _run():
-        await gw.send_progress(5, "hello", message_thread_id=77)
-        await gw.send_task_trigger_card(6, "title", "file.md", message_thread_id=88)
-        await gw.send_boot_scan_summary([{"task_id": 1, "title": "t"}], message_thread_id=99)
-
-    asyncio.run(_run())
-    for call in mock_bot.send_message.call_args_list:
-        kwargs = call.kwargs
-        assert "message_thread_id" in kwargs
-    assert mock_bot.send_message.call_args_list[0].kwargs["message_thread_id"] == 77
-    assert mock_bot.send_message.call_args_list[1].kwargs["message_thread_id"] == 88
-    assert mock_bot.send_message.call_args_list[2].kwargs["message_thread_id"] == 99
diff --git a/loop-engine/test_personas_brainstorm.py b/loop-engine/test_personas_brainstorm.py
deleted file mode 100644
index ed27050..0000000
--- a/loop-engine/test_personas_brainstorm.py
+++ /dev/null
@@ -1,226 +0,0 @@
-"""Characterization tests for Task 115 — full persona coverage + brainstorming.
-
-Covers:
-- personas loader: 7 operational personas + 6 swarm personas + output schema
-- router: fragment-derived context (zero hardcoded persona bodies), unknown
-  persona fails loudly, route_with_persona invocable for all 7
-- qa_engine.decide: persona-defined token vocabularies
-- BrainstormStage: trigger detection, six INDEPENDENT parallel calls,
-  schema-enforced synthesis
-"""
-import asyncio
-import os
-import sys
-from pathlib import Path
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-REPO_ROOT = str(Path(__file__).resolve().parent.parent)
-
-from models import LoopEngineConfig
-
-EXPECTED_PERSONAS = {
-    "Software Architect", "UI/UX Designer", "Senior Programmer",
-    "Project Planner", "Sprint Strategist", "QA Engineer", "Code Reviewer",
-}
-EXPECTED_SWARM = {
-    "system_architect", "security_engineer", "product_manager",
-    "business_strategist", "legal_advisor", "critical_thinker",
-}
-
-
-def _cfg():
-    return LoopEngineConfig(approval={"chat_id": 123})
-
-
-# --- personas loader ---
-
-def test_load_personas_seven_defined():
-    from personas import load_personas
-    personas = load_personas(REPO_ROOT)
-    assert set(personas.keys()) == EXPECTED_PERSONAS
-    for p in personas.values():
-        assert p["trigger"] and p["duty"] and p["behavior"]
-
-
-def test_load_swarm_six():
-    from personas import load_swarm_personas
-    swarm = load_swarm_personas(REPO_ROOT)
-    assert set(swarm.keys()) == EXPECTED_SWARM
-    for s in swarm.values():
-        assert s["focus"] and s["output"]
-
-
-def test_load_brainstorm_schema():
-    from personas import load_brainstorm_schema
-    schema = load_brainstorm_schema(REPO_ROOT)
-    assert "<brainstorming_session>" in schema
-    assert "final_recommendation" in schema
-    assert "conflict_resolution" in schema
-
-
-# --- router fragment-derivation ---
-
-def test_router_context_uses_fragment_verbatim():
-    from router import LLMRouter
-    router = LLMRouter(_cfg(), workspace_root=REPO_ROOT)
-    ctx = router._build_system_context("qa_engineer")
-    # Verbatim duty text from prompts/fragments/12-personas.md
-    assert "Adversarial testing, boundary analysis" in ctx
-    assert "QA Engineer" in ctx
-
-
-def test_router_unknown_persona_raises():
-    from router import LLMRouter
-    router = LLMRouter(_cfg(), workspace_root=REPO_ROOT)
-    try:
-        router._build_system_context("PO Closure")
-        assert False, "Should have raised: PO Closure is not a defined persona"
-    except ValueError:
-        pass
-
-
-def test_router_source_has_zero_hardcoded_persona_bodies():
-    source = (Path(__file__).parent / "router.py").read_text(encoding="utf-8")
-    for marker in [
-        "You are the Architect persona",
-        "You are the QA Engineer persona",
-        "You are the Code Reviewer persona",
-        "You are the PO Closure persona",
-        "PERSONA_INSTRUCTIONS",
-    ]:
-        assert marker not in source, f"Hardcoded persona remnant: {marker}"
-
-
-def test_route_with_persona_all_seven_invocable():
-    from router import LLMRouter
-    router = LLMRouter(_cfg(), workspace_root=REPO_ROOT)
-    for name in EXPECTED_PERSONAS:
-        routing = router.route_with_persona(name, "Do the thing")
-        assert routing["model"]
-        assert "Do the thing" in routing["user"]
-
-
-def test_stage_map_resolves():
-    from router import STAGE_PERSONAS
-    assert STAGE_PERSONAS["architect"] == "Software Architect"
-    assert STAGE_PERSONAS["qa_engineer"] == "QA Engineer"
-    assert STAGE_PERSONAS["code_reviewer"] == "Code Reviewer"
-    # G1 resolution: closure reuses Code Reviewer, no invented persona
-    assert STAGE_PERSONAS["po_closure"] == "Code Reviewer"
-
-
-# --- decision tokens (G2 alignment) ---
-
-def test_decide_persona_qa_tokens():
-    from qa_engine import decide
-    assert decide("Status: QA_PASSED. All boundaries hold.") == "PASS"
-    assert decide("Status: QA_REJECTED. Race condition found.") == "FAIL"
-
-
-def test_decide_persona_reviewer_tokens():
-    from qa_engine import decide
-    assert decide("APPROVED_WITH_CHANGES: minor naming issues.") == "PASS"
-    assert decide("REJECTED_NEEDS_FIXES: blueprint divergence.") == "FAIL"
-    assert decide("PO_REVIEW_PENDING — technically approved.") == "PASS"
-
-
-def test_decide_quoted_token_still_first_occurrence_wins():
-    from qa_engine import decide
-    report = ("FAILED: criteria demand APPROVED_WITH_CHANGES at minimum, "
-              "but tests crash.")
-    assert decide(report) == "FAIL"
-
-
-# --- BrainstormStage ---
-
-def test_brainstorm_should_trigger():
-    from brainstorm import BrainstormStage
-    assert BrainstormStage.should_trigger("let's brainstorm on caching")
-    assert BrainstormStage.should_trigger("See <brainstorming_session> guidelines")
-    assert not BrainstormStage.should_trigger("Fix the login null pointer")
-
-
-class _RecordingRouter:
-    """Sync stub — records every call_llm routing; called via to_thread."""
-
-    def __init__(self):
-        self.calls = []
-
-    def _resolve_model(self, category):
-        return "stub/model", None
-
-    def call_llm(self, routing):
-        self.calls.append(routing)
-        if "Orchestrator synthesizing" in routing["system"]:
-            return ("<brainstorming_session><summary>ok</summary>"
-                    "<final_recommendation>do X</final_recommendation>"
-                    "</brainstorming_session>")
-        # Persona call — extract own name from role line
-        for name in EXPECTED_SWARM:
-            if f"the {name} persona" in routing["system"]:
-                return f"analysis-by-{name}"
-        return "unknown-analysis"
-
-
-def test_brainstorm_run_six_independent_calls_plus_synthesis():
-    from brainstorm import BrainstormStage
-    stub = _RecordingRouter()
-    stage = BrainstormStage(_cfg(), stub, workspace_root=REPO_ROOT)
-    result = asyncio.run(stage.run("Should we add Redis caching?"))
-
-    persona_calls = [c for c in stub.calls
-                     if "Orchestrator synthesizing" not in c["system"]]
-    synth_calls = [c for c in stub.calls
-                   if "Orchestrator synthesizing" in c["system"]]
-
-    assert len(stub.calls) == 7          # 6 personas + 1 synthesis
-    assert len(persona_calls) == 6
-    assert len(synth_calls) == 1
-    assert set(result["responses"].keys()) == EXPECTED_SWARM
-    assert "<brainstorming_session>" in result["session"]
-
-    # Independence: no persona call sees another persona's analysis
-    for c in persona_calls:
-        assert "analysis-by-" not in c["user"]
-
-    # Synthesis receives ALL six analyses + the verbatim schema
-    synth_user = synth_calls[0]["user"]
-    for name in EXPECTED_SWARM:
-        assert f'persona="{name}"' in synth_user
-        assert f"analysis-by-{name}" in synth_user
-    assert "<output_schema>" in synth_calls[0]["system"]
-
-
-def test_brainstorm_missing_swarm_fails_loudly():
-    import tempfile
-    from brainstorm import BrainstormStage
-    import personas as personas_mod
-    with tempfile.TemporaryDirectory() as tmp:
-        # Simulate genuinely missing fragments: re-anchor both lookup roots
-        original_root = personas_mod._REPO_ROOT
-        personas_mod._REPO_ROOT = Path(tmp)
-        try:
-            stage = BrainstormStage(_cfg(), _RecordingRouter(), workspace_root=tmp)
-            try:
-                asyncio.run(stage.run("topic"))
-                assert False, "Should have raised: no swarm personas loaded"
-            except RuntimeError:
-                pass
-        finally:
-            personas_mod._REPO_ROOT = original_root
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = failed = 0
-    for t in tests:
-        try:
-            t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            print(f"  FAIL: {t.__name__}: {e}")
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
diff --git a/loop-engine/test_polyglot_smoke.py b/loop-engine/test_polyglot_smoke.py
deleted file mode 100644
index cc8125b..0000000
--- a/loop-engine/test_polyglot_smoke.py
+++ /dev/null
@@ -1,874 +0,0 @@
-"""End-to-End Polyglot Smoke Test Suite & Hard Verification Gate (Task 137 / LE-5).
-
-Certifies Phase A (Polyglot Toolchain & Execution Sandboxing) end-to-end by driving the
-REAL pipeline components — StateMachine, LLMRouter, QAEngine, HandsExecutor,
-ApprovalGateway, LoopEngineDaemon — anchored to an isolated temporary workspace.
-
-Strategy (hermetic, deterministic, zero side effects):
-- Every test builds its own workspace under tmp_path: stacks/, tasks/{backlog,in-progress,
-  qa,completed}/, loop-engine/{evidence,state}/, plus dummy AGENTS.md, system-prompt.md,
-  docs/conventions.md, and loop-engine.jsonc.
-- All five stack profile YAMLs mirror the repository defaults (detection, skills,
-  model_preferences); preflight/toolchain commands are sandboxed to portable no-ops
-  (``true``) or deterministic failures (``false``, fail-first marker files) so the gate
-  passes on any CI machine without installed toolchains.
-- daemon.REPO_ROOT is patched to the temp workspace for the duration of each pipeline run,
-  so detection, preflight/toolchain cwd, and evidence writes never touch the real repo.
-- Scripted I/O seams at the process boundary only: call_llm (deterministic per-stage
-  responses), executor._run_once (simulates the Hands agent writing the diff block and
-  emitting real goal tokens), and gateway.request_approval (auto-approve or scripted).
-
-Coverage matrix (16 tests):
-  - Happy path (5): node-ts, python-fastapi, kotlin-android, go-gin, generic fallback.
-  - Hard gate (7): preflight failure crashes before execution; toolchain failure bypasses
-    QA and retries; goal-blocked reason extraction; empty diff crashes without toolchain/QA;
-    retry recovery to CLOSED; max retries → CRASHED; explicit **Stack:** header overrides
-    marker detection.
-  - Supplementary (4): plan rejection → BACKLOG; review rejection → CRASHED; QA-feedback
-    retry recovery; daemon boot_scan registers PENDING_TRIGGER.
-"""
-import asyncio
-import json
-import os
-import sys
-from dataclasses import dataclass, field
-from pathlib import Path
-from unittest.mock import patch
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-import pytest  # noqa: F401  (tmp_path fixture)
-
-import daemon
-from models import LoopEngineConfig, TaskState
-from state import StateMachine
-from router import LLMRouter
-from qa_engine import QAEngine
-from executor import HandsExecutor, TERM_BLOCKED, TERM_COMPLETE
-from gateway import ApprovalGateway
-from brainstorm import BrainstormStage
-
-REAL_REPO_ROOT = daemon.REPO_ROOT
-
-
-# ---------------------------------------------------------------------------
-# Workspace construction
-# ---------------------------------------------------------------------------
-
-# Sandboxed profiles mirroring stacks/*.yaml repository defaults.
-# Preflight/toolchain commands are portable no-ops so the gate is deterministic.
-_DEFAULT_PROFILES = {
-    "generic": {
-        "display_name": "Generic (Fallback)",
-        "detection": {"marker_files": [], "extensions": [], "task_keywords": []},
-        "skills": [],
-        "preflight": [],
-        "toolchain": {"test_cmd": None, "build_cmd": None, "lint_cmd": None},
-        "model_preferences": {},
-    },
-    "node-ts": {
-        "display_name": "Node.js / TypeScript",
-        "detection": {
-            "marker_files": ["package.json", "tsconfig.json"],
-            "extensions": [".ts", ".tsx", ".js"],
-            "task_keywords": ["node", "typescript", "nextjs", "react"],
-        },
-        "skills": ["nextjs", "react-vite"],
-        "preflight": ["true"],
-        "toolchain": {"test_cmd": "true", "build_cmd": "true", "lint_cmd": "true"},
-        "model_preferences": {
-            "deep": ["openai/gpt-5.6-sol", "anthropic/claude-3-7-sonnet"],
-            "quick": ["kimi/kimi-k3"],
-        },
-    },
-    "python-fastapi": {
-        "display_name": "Python / FastAPI",
-        "detection": {
-            "marker_files": ["pyproject.toml", "requirements.txt", "Pipfile"],
-            "extensions": [".py"],
-            "task_keywords": ["python", "fastapi", "pydantic", "pytest"],
-        },
-        "skills": ["python-fastapi"],
-        "preflight": ["true"],
-        "toolchain": {"test_cmd": "true", "build_cmd": None, "lint_cmd": "true"},
-        "model_preferences": {
-            "deep": ["openai/gpt-5.6-sol", "gemini/gemini-2.5-pro"],
-            "quick": ["gemini/gemini-2.5-flash"],
-        },
-    },
-    "kotlin-android": {
-        "display_name": "Kotlin / Android",
-        "detection": {
-            "marker_files": ["build.gradle.kts", "build.gradle", "settings.gradle.kts"],
-            "extensions": [".kt", ".kts"],
-            "task_keywords": ["kotlin", "android", "compose", "gradle"],
-        },
-        "skills": ["android-kotlin"],
-        "preflight": ["true"],
-        "toolchain": {"test_cmd": "true", "build_cmd": "true", "lint_cmd": "true"},
-        "model_preferences": {
-            "deep": ["anthropic/claude-3-7-sonnet", "openai/gpt-5.6-sol"],
-            "quick": ["gemini/gemini-2.5-flash"],
-        },
-    },
-    "go-gin": {
-        "display_name": "Go / Gin",
-        "detection": {
-            "marker_files": ["go.mod", "go.sum"],
-            "extensions": [".go"],
-            # Sandbox deviation from repo default: bare "go" and "gin" are dropped
-            # because every task file contains "## Goal" and the canonical
-            # <!-- BEGIN_GIT_DIFF --> markers (which embed the substring "gin"
-            # in "begin_git_diff"). Either keyword would make the keyword phase
-            # match go-gin for ALL tasks and render generic fallback unreachable
-            # in the hermetic suite. golang/grpc remain.
-            "task_keywords": ["golang", "grpc"],
-        },
-        "skills": ["go-gin", "go-hexagonal-grpc"],
-        "preflight": ["true"],
-        "toolchain": {"test_cmd": "true", "build_cmd": "true", "lint_cmd": "true"},
-        "model_preferences": {
-            "deep": ["openai/gpt-5.6-sol", "anthropic/claude-3-7-sonnet"],
-            "quick": ["gemini/gemini-2.5-flash"],
-        },
-    },
-}
-
-_DEFAULT_MARKERS = {
-    "node-ts": "package.json",
-    "python-fastapi": "pyproject.toml",
-    "kotlin-android": "build.gradle.kts",
-    "go-gin": "go.mod",
-    "generic": None,
-}
-
-
-def _render_yaml_value(value):
-    """Render a Python value as a YAML flow scalar (strings always quoted).
-
-    Quoting is mandatory: a bare ``true``/``false``/``null`` renders as a YAML
-    boolean/null, not a string, breaking StackProfileConfig validation.
-    """
-    if value is None:
-        return "null"
-    if isinstance(value, (list, dict)):
-        return json.dumps(value)
-    return json.dumps(str(value))
-
-
-def _write_profile(path: Path, name: str, profile: dict) -> None:
-    lines = [f"name: {name}", f"display_name: {profile['display_name']}"]
-    det = profile["detection"]
-    lines.append("detection:")
-    lines.append(f"  marker_files: {json.dumps(det['marker_files'])}")
-    lines.append(f"  extensions: {json.dumps(det['extensions'])}")
-    lines.append(f"  task_keywords: {json.dumps(det['task_keywords'])}")
-    lines.append(f"skills: {json.dumps(profile['skills'])}")
-    lines.append(f"preflight: {json.dumps(profile['preflight'])}")
-    tc = profile["toolchain"]
-    lines.append("toolchain:")
-    lines.append(f"  test_cmd: {_render_yaml_value(tc.get('test_cmd'))}")
-    lines.append(f"  build_cmd: {_render_yaml_value(tc.get('build_cmd'))}")
-    lines.append(f"  lint_cmd: {_render_yaml_value(tc.get('lint_cmd'))}")
-    lines.append(f"model_preferences: {json.dumps(profile['model_preferences'])}")
-    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
-
-
-@dataclass
-class SmokeWorkspace:
-    """Container for a hermetic workspace plus real, workspace-anchored components."""
-
-    root: Path
-    config: LoopEngineConfig
-    state: StateMachine
-    router: LLMRouter
-    qa: QAEngine
-    executor: HandsExecutor
-    gateway: ApprovalGateway
-    brainstorm: BrainstormStage
-    daemon: daemon.LoopEngineDaemon
-    prompts: list = field(default_factory=list)
-    run_once_calls: int = 0
-    qa_calls: list = field(default_factory=list)
-
-    @property
-    def root_str(self) -> str:
-        return str(self.root)
-
-    def create_task(self, task_id: int, name: str, content: str, with_diff_markers: bool = True) -> Path:
-        """Write a task file into the workspace backlog and register it."""
-        backlog = self.root / "tasks" / "backlog"
-        backlog.mkdir(parents=True, exist_ok=True)
-        task_file = backlog / f"{task_id:02d}-{name}.md"
-        body = (
-            f"# Task {task_id}: {name}\n"
-            f"**File:** tasks/backlog/{task_id:02d}-{name}.md\n"
-            "**Source:** orchestrator\n"
-            "**Type:** feature\n"
-            "**Status:** open\n\n"
-            "## Goal\n\n"
-            f"{content}\n\n"
-            "## Acceptance Criteria\n\n- [ ] criterion\n\n"
-            "## Factual Git Diff\n\n"
-        )
-        if with_diff_markers:
-            body += "<!-- BEGIN_GIT_DIFF -->\n\n<!-- END_GIT_DIFF -->\n"
-        task_file.write_text(body, encoding="utf-8")
-        return task_file
-
-    def register(self, task_file: Path) -> int:
-        return self.state.register_task(str(task_file), TaskState.BACKLOG)
-
-    async def run_pipeline(self, task_id: int, task_file: Path) -> None:
-        """Run the real public pipeline entry against this workspace.
-
-        daemon.REPO_ROOT is patched to the workspace for the duration so marker
-        detection, preflight/toolchain cwd, and evidence writes stay hermetic.
-        """
-        with patch.object(daemon, "REPO_ROOT", self.root_str):
-            await daemon.process_task(
-                task_id, str(task_file), self.config, self.state,
-                self.router, self.gateway, self.executor, self.qa, self.brainstorm,
-            )
-
-    def evidence_dir(self, task_id: int) -> Path:
-        return self.root / "loop-engine" / "evidence" / str(task_id)
-
-    def close(self) -> None:
-        self.state.close()
-
-
-def setup_test_workspace(
-    tmp_path,
-    stack_name,
-    marker_files=None,
-    toolchain=None,
-    preflight=None,
-    model_prefs=None,
-) -> SmokeWorkspace:
-    """Build a hermetic workspace + real, workspace-anchored engine components.
-
-    Args:
-        tmp_path: pytest tmp_path (or any pathlib.Path).
-        stack_name: profile whose toolchain/preflight/model_prefs are (optionally)
-            overridden. ALL default profiles are written so marker-based detection
-            competes realistically.
-        marker_files: optional explicit marker files to create in the workspace root.
-            Defaults to the named stack's first detection marker (none for generic).
-        toolchain: optional dict overrides for the named stack's toolchain config.
-        preflight: optional list overrides for the named stack's preflight commands.
-        model_prefs: optional dict overrides for the named stack's model_preferences.
-
-    Returns:
-        SmokeWorkspace with real StateMachine/LLMRouter/QAEngine/HandsExecutor/
-        ApprovalGateway/LoopEngineDaemon wired to the workspace.
-    """
-    root = Path(tmp_path)
-    (root / "stacks").mkdir(parents=True, exist_ok=True)
-    for sub in ("backlog", "in-progress", "qa", "completed"):
-        (root / "tasks" / sub).mkdir(parents=True, exist_ok=True)
-    (root / "loop-engine" / "evidence").mkdir(parents=True, exist_ok=True)
-    (root / "loop-engine" / "state").mkdir(parents=True, exist_ok=True)
-    (root / "docs").mkdir(parents=True, exist_ok=True)
-
-    # Dummy core files (router reads them; content is not load-bearing here).
-    (root / "AGENTS.md").write_text("# AGENTS\nDummy project rules for smoke test.\n", encoding="utf-8")
-    (root / "system-prompt.md").write_text("# System Prompt\nDummy.\n", encoding="utf-8")
-    (root / "docs" / "conventions.md").write_text("# Conventions\nDummy.\n", encoding="utf-8")
-    (root / "loop-engine.jsonc").write_text('{\n  // dummy\n  "approval": {"chat_id": 1}\n}\n', encoding="utf-8")
-
-    # Stack profiles: ALL defaults (realistic detection competition), then apply
-    # overrides to the named profile.
-    for prof_name, profile in _DEFAULT_PROFILES.items():
-        _write_profile(root / "stacks" / f"{prof_name}.yaml", prof_name, dict(profile))
-
-    profile = _DEFAULT_PROFILES[stack_name]
-    contents = dict(profile)
-    if preflight is not None:
-        contents["preflight"] = list(preflight)
-    if toolchain is not None:
-        merged_tc = dict(profile["toolchain"])
-        merged_tc.update(toolchain)
-        contents["toolchain"] = merged_tc
-    if model_prefs is not None:
-        contents["model_preferences"] = dict(model_prefs)
-    _write_profile(root / "stacks" / f"{stack_name}.yaml", stack_name, contents)
-
-    # Marker files for detection.
-    if marker_files is None:
-        marker = _DEFAULT_MARKERS.get(stack_name)
-        marker_files = [marker] if marker else []
-    for m in marker_files:
-        (root / m).write_text("marker\n", encoding="utf-8")
-
-    config = LoopEngineConfig(
-        approval={"chat_id": 1},
-        evidence_dir=str(root / "loop-engine" / "evidence"),
-        stacks_dir=str(root / "stacks"),
-        tasks_dir=str(root / "tasks"),
-        max_qa_retries=3,
-        trigger_mode="telegram_button",
-        auto_start_on_boot=False,
-    )
-
-    state = StateMachine(str(root / "loop-engine" / "state" / "loop.db"))
-    router = ScriptedRouter(config, workspace_root=str(root))
-    qa = QAEngine(config, state, router)
-    executor = FakeHandsExecutor(config, state)
-    gateway = AutoApproveGateway(config)
-    brainstorm = BrainstormStage(config, router, workspace_root=str(root))
-
-    ws = SmokeWorkspace(
-        root=root, config=config, state=state, router=router, qa=qa,
-        executor=executor, gateway=gateway, brainstorm=brainstorm,
-        daemon=None,  # daemon constructed below (needs gateway wiring)
-    )
-    ws.daemon = daemon.LoopEngineDaemon(config, state, router, gateway, executor, qa, brainstorm)
-    gateway.set_daemon(ws.daemon)
-    gateway.set_state(state)
-    # Bind recorder hooks so tests can derive evidence.
-    qa.run_qa = _record_qa(qa.run_qa, ws.qa_calls)
-    return ws
-
-
-def _record_qa(original, sink):
-    def wrapper(*args, **kwargs):
-        sink.append(args[0])
-        return original(*args, **kwargs)
-    return wrapper
-
-
-# ---------------------------------------------------------------------------
-# Scripted seams (real classes, stubbed I/O boundary)
-# ---------------------------------------------------------------------------
-
-class ScriptedRouter(LLMRouter):
-    """Real LLMRouter with deterministic, stage-aware call_llm.
-
-    route_plan/route_qa/route_review inherit the real prompt-building logic;
-    call_llm consumes scripted per-stage responses instead of hitting litellm.
-    """
-
-    def __init__(self, config, workspace_root="."):
-        super().__init__(config, workspace_root=workspace_root)
-        self._stage = "plan"
-        self.plan_response = "# Plan\n1. Implement the change."
-        self.qa_responses = ["QA_PASSED: change satisfies the acceptance criteria."]
-        self.review_responses = ["APPROVED"]
-        self.seen_stack_profiles = []
-        self.plan_calls = 0
-        self.qa_count = 0
-        self.review_count = 0
-
-    def route_plan(self, task_content, category="unspecified", extra_context="", stack_profile=None):
-        self._stage = "plan"
-        self.plan_calls += 1
-        if stack_profile is not None:
-            self.seen_stack_profiles.append(stack_profile.name)
-        return super().route_plan(
-            task_content, category=category, extra_context=extra_context,
-            stack_profile=stack_profile,
-        )
-
-    def route_qa(self, task_content, diff="", toolchain_evidence="", stack_profile=None):
-        self._stage = "qa"
-        return super().route_qa(
-            task_content, diff=diff, toolchain_evidence=toolchain_evidence,
-            stack_profile=stack_profile,
-        )
-
-    def route_review(self, task_content, qa_report="", stack_profile=None):
-        self._stage = "review"
-        return super().route_review(
-            task_content, qa_report=qa_report, stack_profile=stack_profile)
-
-    def call_llm(self, routing):
-        if self._stage == "plan":
-            self.plan_calls += 1
-            return self.plan_response
-        if self._stage == "qa":
-            self.qa_count += 1
-            if self.qa_responses:
-                return self.qa_responses.pop(0)
-            return "QA_PASSED"
-        self.review_count += 1
-        if self.review_responses:
-            return self.review_responses.pop(0)
-        return "APPROVED"
-
-
-class FakeHandsExecutor(HandsExecutor):
-    """Real HandsExecutor; _run_once simulates the Hands agent.
-
-    Modes:
-      complete     — injects a non-empty diff into the task file, emits [goal:complete].
-      empty_diff   — leaves the diff block empty, still emits [goal:complete] (crashes later).
-      blocked      — emits [goal:blocked: <reason>]; the REAL TERM_BLOCKED regex extracts it.
-      error        — non-transport error.
-    """
-
-    def __init__(self, config, state, mode="complete", blocked_reason="missing credentials"):
-        super().__init__(config, state)
-        self.mode = mode
-        self.blocked_reason = blocked_reason
-        self.prompts = []
-        self.run_once_calls = 0
-        self.last_result = None
-
-    async def _run_once(self, task_file, prompt):
-        self.run_once_calls += 1
-        self.prompts.append(prompt)
-
-        if self.mode == "blocked":
-            # Simulate agent stdout; the real executor regex does the extraction.
-            output = f"[goal:blocked: {self.blocked_reason}]"
-            m = TERM_BLOCKED.search(output)
-            reason = m.group(1) if m and m.group(1) else "Agent signaled blocked"
-            result = {"status": "blocked", "output": output, "error": "", "reason": reason.strip(), "elapsed": 0.1}
-            self.last_result = result
-            return result
-
-        if self.mode == "error":
-            result = {"status": "error", "output": "", "error": "boom", "returncode": 2, "elapsed": 0.1}
-            self.last_result = result
-            return result
-
-        # Default complete/empty_diff: Hands "writes" the factual diff block.
-        path = Path(task_file)
-        text = path.read_text(encoding="utf-8")
-        begin = "<!-- BEGIN_GIT_DIFF -->"
-        end = "<!-- END_GIT_DIFF -->"
-        if begin not in text or end not in text:
-            text += f"\n{begin}\n{end}\n"
-
-        if self.mode == "empty_diff":
-            # Keep markers present but payload empty → extract_task_diff returns "".
-            head, _, tail = text.partition(begin)
-            _, _, footer = tail.partition(end)
-            text = f"{head}{begin}\n{end}{footer}"
-        else:
-            # Inject a passing diff payload between markers.
-            head, _, tail = text.partition(begin)
-            _, _, footer = tail.partition(end)
-            payload = "+def smoke_impl():\n+    return 42\n"
-            text = f"{head}{begin}\n{payload}{end}{footer}"
-        path.write_text(text, encoding="utf-8")
-        result = {"status": "complete", "output": "[goal:complete]", "error": "", "elapsed": 0.1}
-        self.last_result = result
-        return result
-
-
-class AutoApproveGateway(ApprovalGateway):
-    """Real ApprovalGateway with scripted approval I/O (no Telegram).
-
-    approve_plan / approve_closure flags let tests script denial; trigger cards
-    are recorded instead of sent.
-    """
-
-    def __init__(self, config, approve_plan=True, approve_closure=True):
-        super().__init__(config)
-        self.approve_plan = approve_plan
-        self.approve_closure = approve_closure
-        self.plan_approvals = 0
-        self.closure_approvals = 0
-        self.trigger_cards = []
-        self.trigger_summaries = []
-
-    async def request_approval(self, task_id, stage, content):
-        if stage == "Plan Approval":
-            self.plan_approvals += 1
-            return self.approve_plan
-        if stage == "Closure Approval":
-            self.closure_approvals += 1
-            return self.approve_closure
-        return False
-
-    async def send_task_trigger_card(self, task_id, title, file_path):
-        self.trigger_cards.append((task_id, title, file_path))
-        return True
-
-    async def send_boot_scan_summary(self, tasks, top_n=4):
-        self.trigger_summaries.append(
-            (len(tasks), [t["task_id"] for t in tasks]))
-        return True
-
-
-# ---------------------------------------------------------------------------
-# Happy-path E2E smoke tests
-# ---------------------------------------------------------------------------
-
-def _run_to_completion(ws: SmokeWorkspace, tid: int, task_file: Path):
-    asyncio.run(ws.run_pipeline(tid, task_file))
-
-
-def test_smoke_node_ts_end_to_end(tmp_path):
-    """Node/TS workspace with package.json → full lifecycle → CLOSED."""
-    ws = setup_test_workspace(tmp_path, "node-ts")
-    try:
-        task = ws.create_task(1, "node-smoke", "Add a TypeScript API endpoint to the service layer.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "closed"
-        assert "node-ts" in ws.router.seen_stack_profiles
-        # Stack context was injected into the Hands prompt.
-        assert "node-ts" in ws.executor.prompts[0]
-        assert "nextjs" in ws.executor.prompts[0]
-    finally:
-        ws.close()
-
-
-def test_smoke_python_fastapi_end_to_end(tmp_path):
-    """Python/FastAPI workspace with pyproject.toml → CLOSED + evidence files."""
-    ws = setup_test_workspace(tmp_path, "python-fastapi")
-    try:
-        task = ws.create_task(2, "py-smoke", "Add a FastAPI health endpoint using Pydantic schemas.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "closed"
-        ev = ws.evidence_dir(tid)
-        assert (ev / "qa_report.md").exists()
-        assert (ev / "result.txt").read_text() == "PASSED"
-        assert (ev / "review.md").exists()
-        assert (ev / "review_result.txt").read_text() == "APPROVED"
-        assert (ev / "toolchain_report.md").exists()
-        assert (ev / "toolchain_result.txt").read_text() == "PASSED"
-    finally:
-        ws.close()
-
-
-def test_smoke_kotlin_android_end_to_end(tmp_path):
-    """Kotlin/Android workspace with build.gradle.kts → CLOSED, android-kotlin skill verified."""
-    ws = setup_test_workspace(tmp_path, "kotlin-android")
-    try:
-        task = ws.create_task(3, "kotlin-smoke", "Refactor a Compose screen using Kotlin coroutines.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "closed"
-        assert "kotlin-android" in ws.router.seen_stack_profiles
-        # Android-Kotlin skill mandated via <stack_context> in the Hands prompt.
-        assert "android-kotlin" in ws.executor.prompts[0]
-        assert "<stack_context" in ws.executor.prompts[0]
-    finally:
-        ws.close()
-
-
-def test_smoke_go_gin_end_to_end(tmp_path):
-    """Go/Gin workspace with go.mod → CLOSED."""
-    ws = setup_test_workspace(tmp_path, "go-gin")
-    try:
-        task = ws.create_task(4, "go-smoke", "Add a Gin route with middleware for the service.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "closed"
-        assert "go-gin" in ws.router.seen_stack_profiles
-    finally:
-        ws.close()
-
-
-def test_smoke_generic_end_to_end(tmp_path):
-    """Untagged task, no marker files → generic fallback → toolchain skipped → CLOSED."""
-    ws = setup_test_workspace(tmp_path, "generic")
-    try:
-        task = ws.create_task(5, "generic-smoke", "Update the documentation template for onboarding.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "closed"
-        assert "generic" in ws.router.seen_stack_profiles
-        # Generic toolchain is all-null → skipped gracefully, reported as PASSED.
-        ev = ws.evidence_dir(tid)
-        assert (ev / "toolchain_report.md").exists()
-        assert "SKIPPED" in (ev / "toolchain_report.md").read_text()
-        assert (ev / "toolchain_result.txt").read_text() == "PASSED"
-    finally:
-        ws.close()
-
-
-# ---------------------------------------------------------------------------
-# Hard-gate failure & edge-case smoke tests
-# ---------------------------------------------------------------------------
-
-def test_smoke_preflight_failure_crashes_before_execution(tmp_path):
-    """Failing preflight → CRASHED before executor.execute; error recorded via set_qa_feedback."""
-    ws = setup_test_workspace(tmp_path, "node-ts", preflight=["false"])
-    try:
-        task = ws.create_task(6, "preflight-fail", "Add a TypeScript endpoint (preflight will fail).")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "crashed"
-        # Executor never ran — preflight gate fired first.
-        assert ws.executor.run_once_calls == 0
-        # Preflight diagnostic recorded via set_qa_feedback (retry count incremented once).
-        assert rec["qa_feedback"] is not None
-        assert "Preflight failed" in rec["qa_feedback"]
-        assert rec["qa_retry_count"] == 1
-        # No toolchain/QA evidence was produced.
-        assert not ws.evidence_dir(tid).exists()
-    finally:
-        ws.close()
-
-
-def test_smoke_toolchain_failure_bypasses_qa_and_retries(tmp_path):
-    """Failing test_cmd → _execute_and_qa returns FAILED without qa.run_qa; evidence written;
-    _reimplement_task retries until max_qa_retries then CRASHED."""
-    ws = setup_test_workspace(tmp_path, "go-gin", toolchain={"test_cmd": "false"})
-    try:
-        task = ws.create_task(7, "toolchain-fail", "Add a Go route with a failing test command.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "crashed"
-        # Toolchain failed on every attempt → LLM QA never invoked.
-        assert ws.qa_calls == []
-        # Fail-fast evidence written before QA bypass.
-        ev = ws.evidence_dir(tid)
-        assert (ev / "toolchain_report.md").exists()
-        assert "FAILED" in (ev / "toolchain_result.txt").read_text()
-        # Retry loop engaged (each toolchain failure bumps the retry counter).
-        assert rec["qa_retry_count"] >= 3
-        # Hands prompt carried the toolchain failure report as qa_feedback on retries.
-        assert ws.executor.run_once_calls >= 3
-        assert "<qa_feedback>" in ws.executor.prompts[-1]
-    finally:
-        ws.close()
-
-
-def test_smoke_goal_blocked_extracts_reason_and_crashes(tmp_path):
-    """Handler emits [goal:blocked: missing credentials] → CRASHED with extracted reason."""
-    ws = setup_test_workspace(tmp_path, "python-fastapi")
-    try:
-        ws.executor.mode = "blocked"
-        ws.executor.blocked_reason = "missing credentials"
-        task = ws.create_task(8, "blocked", "Add a FastAPI auth dependency (will be blocked).")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "crashed"
-        # The real TERM_BLOCKED regex extracted the reason from the agent output.
-        assert ws.executor.last_result is not None
-        assert ws.executor.last_result["status"] == "blocked"
-        assert ws.executor.last_result["reason"] == "missing credentials"
-        # QA never reached.
-        assert ws.qa_calls == []
-    finally:
-        ws.close()
-
-
-def test_smoke_empty_diff_crashes_without_qa(tmp_path):
-    """Hands leaves diff block empty → CRASHED before toolchain/QA execute."""
-    ws = setup_test_workspace(tmp_path, "node-ts")
-    try:
-        ws.executor.mode = "empty_diff"
-        task = ws.create_task(9, "empty-diff", "Add a TypeScript endpoint but produce no diff.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "crashed"
-        # No toolchain evidence and no QA calls — empty-diff gate fired before both.
-        assert ws.qa_calls == []
-        assert not ws.evidence_dir(tid).exists()
-    finally:
-        ws.close()
-
-
-def test_smoke_reimplement_retry_recovers_to_closed(tmp_path):
-    """Attempt 1 toolchain fails; _reimplement_task loops; attempt 2 passes → CLOSED."""
-    # test_cmd fails once (marker file consumed on first run), then passes.
-    ws = setup_test_workspace(
-        tmp_path, "python-fastapi",
-        toolchain={"test_cmd": "test -f .smoke_fail_once && rm -f .smoke_fail_once && exit 1 || true"},
-    )
-    try:
-        (ws.root / ".smoke_fail_once").write_text("x", encoding="utf-8")
-        task = ws.create_task(10, "retry-recover", "Add a FastAPI route that recovers on retry.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "closed"
-        # Exactly one toolchain failure → one retry increment, then success.
-        assert rec["qa_retry_count"] == 1
-        # QA ran exactly once (attempt 2 only).
-        assert len(ws.qa_calls) == 1
-        # Closure approved after recovery.
-        assert ws.gateway.closure_approvals >= 1
-    finally:
-        ws.close()
-
-
-def test_smoke_reimplement_max_retries_exceeded_crashes(tmp_path):
-    """Consecutive toolchain failures hit max_qa_retries → CRASHED."""
-    ws = setup_test_workspace(tmp_path, "go-gin", toolchain={"test_cmd": "false"})
-    try:
-        ws.config.max_qa_retries = 2
-        task = ws.create_task(11, "max-retries", "Add a Go route whose tests always fail.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "crashed"
-        assert rec["qa_retry_count"] >= 2
-        # No QA ever executed; no closure approval.
-        assert ws.qa_calls == []
-        assert ws.gateway.closure_approvals == 0
-    finally:
-        ws.close()
-
-
-def test_smoke_explicit_header_overrides_marker_detection(tmp_path):
-    """package.json marker present (node-ts), but explicit **Stack:** python-fastapi header wins."""
-    ws = setup_test_workspace(tmp_path, "python-fastapi", marker_files=["package.json"])
-    try:
-        task = ws.create_task(
-            12, "header-override",
-            "Add an endpoint.\n\n**Stack:** python-fastapi\n\nImplement it now.",
-        )
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "closed"
-        # Header precedence: python-fastapi, NOT node-ts (despite package.json).
-        assert "python-fastapi" in ws.router.seen_stack_profiles
-        assert "node-ts" not in ws.router.seen_stack_profiles
-        assert "python-fastapi" in ws.executor.prompts[0]
-    finally:
-        ws.close()
-
-
-# ---------------------------------------------------------------------------
-# Supplementary smoke tests (extend coverage beyond the mandated 12)
-# ---------------------------------------------------------------------------
-
-def test_smoke_plan_rejected_returns_to_backlog(tmp_path):
-    """Plan Approval denied → task returns to BACKLOG, executor never runs."""
-    ws = setup_test_workspace(tmp_path, "node-ts")
-    try:
-        ws.gateway.approve_plan = False
-        task = ws.create_task(13, "plan-rejected", "Add a TypeScript endpoint but plan is rejected.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "backlog"
-        assert ws.executor.run_once_calls == 0
-        assert ws.qa_calls == []
-    finally:
-        ws.close()
-
-
-def test_smoke_review_rejected_crashes(tmp_path):
-    """QA passes but Code Review rejects → CRASHED after review."""
-    ws = setup_test_workspace(tmp_path, "python-fastapi")
-    try:
-        ws.router.review_responses = ["REJECTED: architectural risk in the change."]
-        task = ws.create_task(14, "review-rejected", "Add a FastAPI module that review will reject.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "crashed"
-        assert len(ws.qa_calls) == 1
-        ev = ws.evidence_dir(tid)
-        assert (ev / "review_result.txt").read_text() == "REJECTED"
-    finally:
-        ws.close()
-
-
-def test_smoke_qa_failure_retries_with_feedback(tmp_path):
-    """QA FAILED → retry re-executes with qa_feedback; second attempt passes → CLOSED."""
-    ws = setup_test_workspace(tmp_path, "python-fastapi")
-    try:
-        ws.router.qa_responses = [
-            "FAILED: missing error handling for the edge case.",
-            "QA_PASSED: error handling added.",
-        ]
-        task = ws.create_task(15, "qa-retry", "Add a FastAPI endpoint that fails QA once.")
-        tid = ws.register(task)
-        _run_to_completion(ws, tid, task)
-
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "closed"
-        assert rec["qa_retry_count"] == 1
-        assert len(ws.qa_calls) == 2
-        # Retry prompt carried the QA report as <qa_feedback> (distinct from plan).
-        assert "<qa_feedback>" in ws.executor.prompts[-1]
-        assert "error handling" in ws.executor.prompts[-1]
-        assert ws.gateway.closure_approvals == 1
-    finally:
-        ws.close()
-
-
-def test_smoke_boot_scan_registers_pending_trigger(tmp_path):
-    """Daemon boot_scan registers backlog tasks as PENDING_TRIGGER + sends ONE
-    consolidated trigger summary (HOTFIX-02 anti-flood: no per-task cards).
-
-    daemon.boot_scan constructs KanbanWatcher without an explicit tasks_dir (it
-    defaults to CWD-relative "tasks/backlog"). For hermeticity we patch the
-    class with a factory that forwards config.tasks_dir, so boot_scan scans the
-    temp workspace and never registers unrelated real-repo backlog files.
-    """
-    from watcher import KanbanWatcher as RealKanbanWatcher
-    import watcher as watcher_module
-
-    ws = setup_test_workspace(tmp_path, "node-ts")
-    try:
-        task_file = ws.create_task(16, "boot-scan", "Add a TypeScript endpoint awaiting trigger.")
-        assert task_file.exists()
-
-        def watcher_factory(state, config, gateway=None, on_task_detected=None):
-            return RealKanbanWatcher(
-                state, config, gateway,
-                tasks_dir=config.tasks_dir, on_task_detected=on_task_detected)
-
-        # boot_scan does a local `from watcher import KanbanWatcher`, so the patch
-        # must replace the attribute on the watcher module itself.
-        with patch.object(watcher_module, "KanbanWatcher", watcher_factory):
-            existing = asyncio.run(ws.daemon.boot_scan())
-
-        assert len(existing) == 1
-        tid = existing[0]["task_id"]
-        rec = ws.state.get_task(tid)
-        assert rec["state"] == "pending_trigger"
-        # HOTFIX-02: boot scan sends ONE consolidated summary, never per-task cards.
-        assert len(ws.gateway.trigger_cards) == 0
-        assert len(ws.gateway.trigger_summaries) == 1
-        count, ids = ws.gateway.trigger_summaries[0]
-        assert count == 1
-        assert ids == [tid]
-    finally:
-        ws.close()
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = failed = 0
-    for t in tests:
-        try:
-            t(Path(f"/tmp/polyglot-smoke-{t.__name__}"))
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except TypeError:
-            # pytest tmp_path fixtures not available in bare-run mode
-            print(f"  SKIP: {t.__name__} (requires pytest tmp_path fixture)")
-        except Exception as e:
-            import traceback
-            print(f"  FAIL: {t.__name__}: {e}")
-            traceback.print_exc()
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
\ No newline at end of file
diff --git a/loop-engine/test_release.py b/loop-engine/test_release.py
deleted file mode 100644
index 06b04f3..0000000
--- a/loop-engine/test_release.py
+++ /dev/null
@@ -1,51 +0,0 @@
-"""Unit tests for SemVer release engine (Task 147)."""
-import os
-import sys
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from release import ReleaseEngine
-
-
-def test_major_bump_on_breaking():
-    e = ReleaseEngine()
-    assert e.calculate_next_version("1.2.3", ["bug", "breaking"]) == "2.0.0"
-
-
-def test_minor_bump_on_feature():
-    e = ReleaseEngine()
-    assert e.calculate_next_version("1.2.3", ["bug", "feature"]) == "1.3.0"
-
-
-def test_patch_bump_on_fix_only():
-    e = ReleaseEngine()
-    assert e.calculate_next_version("1.2.3", ["bug"]) == "1.2.4"
-    assert e.calculate_next_version("1.2.3", ["fix"]) == "1.2.4"
-    assert e.calculate_next_version("1.2.3", ["chore"]) == "1.2.4"
-
-
-def test_changelog_entry_formatting(tmp_path):
-    e = ReleaseEngine()
-    entry = e.format_changelog_entry("1.3.0", "2026-09-04", [
-        {"id": 1, "title": "Add X", "type": "feature"},
-        {"id": 2, "title": "Fix Y", "type": "bug"},
-    ])
-    assert "## [1.3.0] - 2026-09-04" in entry
-    assert "### Added" in entry
-    assert "### Fixed" in entry
-
-
-def test_parse_then_append_insertion(tmp_path):
-    e = ReleaseEngine()
-    p = tmp_path / "CHANGELOG.md"
-    p.write_text("# Changelog\n\n## [Unreleased]\n\nOld\n", encoding="utf-8")
-    e.update_changelog(p, "## [1.2.4] - 2026-09-04\n\n### Fixed\n- Z\n")
-    text = p.read_text(encoding="utf-8")
-    assert text.index("## [Unreleased]") < text.index("## [1.2.4]")
-    assert "Old" in text
-
-
-def test_zac_safe_dry_run_tag():
-    e = ReleaseEngine()
-    out = e.create_git_tag("9.9.9", dry_run=True)
-    assert out == "[dry-run] Would create git tag v9.9.9"
diff --git a/loop-engine/test_router.py b/loop-engine/test_router.py
deleted file mode 100644
index add4fe6..0000000
--- a/loop-engine/test_router.py
+++ /dev/null
@@ -1,229 +0,0 @@
-"""Tests for router.py — LLM routing and context building."""
-import sys, os
-sys.path.insert(0, os.path.dirname(__file__))
-
-from router import LLMRouter, _load_file_if_exists
-from models import LoopEngineConfig, StackProfileConfig
-from stacks import StackProfile
-
-
-def _make_config():
-    return LoopEngineConfig(approval={"chat_id": 123})
-
-
-def _make_stack_profile(prefs):
-    return StackProfile(StackProfileConfig(
-        name="test-stack", display_name="Test Stack", model_preferences=prefs))
-
-
-def test_load_file_exists():
-    p = os.path.join(os.path.dirname(__file__), "models.py")
-    content = _load_file_if_exists(p)
-    assert "LoopEngineConfig" in content
-
-
-def test_load_file_missing():
-    content = _load_file_if_exists("/nonexistent/file.md")
-    assert content == ""
-
-
-def test_resolve_model_with_env():
-    os.environ["KIMI_API_KEY"] = "test-key"
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    model, reasoning = router._resolve_model("quick")
-    assert model == "kimi/kimi-k3"
-    del os.environ["KIMI_API_KEY"]
-
-
-def test_resolve_model_fallback():
-    for key in ["KIMI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
-        os.environ.pop(key, None)
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    model, reasoning = router._resolve_model("quick")
-    assert model == cfg.default_provider
-
-
-def test_build_system_context():
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    ctx = router._build_system_context("architect")
-    assert "Architect" in ctx
-    assert len(ctx) > 100
-
-
-def test_build_system_context_qa():
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    ctx = router._build_system_context("qa_engineer")
-    assert "QA Engineer" in ctx
-
-
-def test_route_plan():
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    routing = router.route_plan("## Goal\nBuild a feature", "quick")
-    assert routing["model"] is not None
-    assert routing["temperature"] == 0.3
-    assert "Build a feature" in routing["user"]
-
-
-def test_route_qa():
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    routing = router.route_qa("Task content", "diff here")
-    assert routing["temperature"] == 0.1
-    assert "diff here" in routing["user"]
-
-
-def test_route_review():
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    routing = router.route_review("Task", "QA passed")
-    assert routing["temperature"] == 0.2
-
-
-# --- Stack-Aware Model Routing (LE-3) ---
-
-def test_resolve_model_stack_preferred_with_env():
-    os.environ["ANTHROPIC_API_KEY"] = "test-key"
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet", "openai/gpt-5.6-sol"]})
-    model, reasoning = router._resolve_model("deep", stack_profile=profile)
-    assert model == "anthropic/claude-3-7-sonnet"
-    assert reasoning == "medium"  # deep category reasoning
-    del os.environ["ANTHROPIC_API_KEY"]
-
-
-def test_resolve_model_stack_preferred_second_model_when_first_unkeyed():
-    for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "KIMI_API_KEY"]:
-        os.environ.pop(key, None)
-    os.environ["OPENAI_API_KEY"] = "test-key"
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet", "openai/gpt-5.6-sol"]})
-    model, reasoning = router._resolve_model("deep", stack_profile=profile)
-    assert model == "openai/gpt-5.6-sol"  # first unkeyed, second keyed wins
-    assert reasoning == "medium"
-    del os.environ["OPENAI_API_KEY"]
-
-
-def test_resolve_model_stack_fallback_category_when_key_missing():
-    for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "KIMI_API_KEY"]:
-        os.environ.pop(key, None)
-    os.environ["OPENAI_API_KEY"] = "test-key"
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
-    model, reasoning = router._resolve_model("deep", stack_profile=profile)
-    assert model == "openai/gpt-5.6-sol"  # Tier 2 category fallback
-    assert reasoning == "medium"
-    del os.environ["OPENAI_API_KEY"]
-
-
-def test_resolve_model_stack_empty_preferences():
-    for key in ["KIMI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
-        os.environ.pop(key, None)
-    os.environ["KIMI_API_KEY"] = "test-key"
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    profile = _make_stack_profile({})
-    model, reasoning = router._resolve_model("quick", stack_profile=profile)
-    assert model == "kimi/kimi-k3"
-    del os.environ["KIMI_API_KEY"]
-
-
-def test_resolve_model_stack_wildcard():
-    os.environ["GEMINI_API_KEY"] = "test-key"
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    profile = _make_stack_profile({"*": ["gemini/gemini-2.5-flash"]})
-    model, reasoning = router._resolve_model("quick", stack_profile=profile)
-    assert model == "gemini/gemini-2.5-flash"
-    del os.environ["GEMINI_API_KEY"]
-
-
-def test_resolve_model_stack_dict_profile():
-    os.environ["KIMI_API_KEY"] = "test-key"
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    profile = {"model_preferences": {"quick": ["kimi/kimi-k3"]}}
-    model, reasoning = router._resolve_model("quick", stack_profile=profile)
-    assert model == "kimi/kimi-k3"
-    del os.environ["KIMI_API_KEY"]
-
-
-def test_route_plan_with_stack_profile():
-    os.environ["ANTHROPIC_API_KEY"] = "test-key"
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
-    routing = router.route_plan("## Goal\nBuild a feature", "deep", stack_profile=profile)
-    assert routing["model"] == "anthropic/claude-3-7-sonnet"
-    del os.environ["ANTHROPIC_API_KEY"]
-
-
-def test_route_qa_with_stack_profile():
-    os.environ["ANTHROPIC_API_KEY"] = "test-key"
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
-    routing = router.route_qa("Task content", "diff here", stack_profile=profile)
-    assert routing["model"] == "anthropic/claude-3-7-sonnet"
-    del os.environ["ANTHROPIC_API_KEY"]
-
-
-def test_route_review_with_stack_profile():
-    os.environ["ANTHROPIC_API_KEY"] = "test-key"
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
-    routing = router.route_review("Task", "QA passed", stack_profile=profile)
-    assert routing["model"] == "anthropic/claude-3-7-sonnet"
-    del os.environ["ANTHROPIC_API_KEY"]
-
-
-def test_route_with_persona_stack_profile():
-    os.environ["ANTHROPIC_API_KEY"] = "test-key"
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
-    routing = router.route_with_persona("architect", "content", category="deep",
-                                        stack_profile=profile)
-    assert routing["model"] == "anthropic/claude-3-7-sonnet"
-    del os.environ["ANTHROPIC_API_KEY"]
-
-
-def test_route_plan_backward_compat_no_stack_profile():
-    for key in ["KIMI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
-        os.environ.pop(key, None)
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    routing = router.route_plan("## Goal\nBuild a feature", "quick")
-    assert routing["model"] == cfg.default_provider
-
-
-def test_route_qa_backward_compat_no_stack_profile():
-    for key in ["KIMI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
-        os.environ.pop(key, None)
-    cfg = _make_config()
-    router = LLMRouter(cfg)
-    routing = router.route_qa("Task content", "diff here")
-    assert routing["model"] == cfg.default_provider
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = failed = 0
-    for t in tests:
-        try:
-            t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            print(f"  FAIL: {t.__name__}: {e}")
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
diff --git a/loop-engine/test_sentinel.py b/loop-engine/test_sentinel.py
deleted file mode 100644
index b3daf25..0000000
--- a/loop-engine/test_sentinel.py
+++ /dev/null
@@ -1,400 +0,0 @@
-"""Tests for No-Manual-DTO Mandate & Type Drift Sentinel (LE-7 / Task 139).
-
-Covers:
-1. Prompt assembly — ``assemble_system_prompt.py`` includes
-   ``<no_manual_dto_mandate>`` with ``<system_version>9.3.0</system_version>``
-   and passes the closing-tag normalization self-check; manifest registration
-   precedes ``18-initialization.md``.
-2. ``TypeDriftSentinel.check_diff`` — detects manual TypeScript interfaces,
-   Kotlin data/plain classes, and Python Pydantic models in consumer paths.
-3. Exemptions — DTO declarations in ``packages/shared-schema/**`` and
-   ``**/generated/**`` are allowed; clean imports produce no false positives.
-4. Bypass — explicit ``drift-ignore`` comments (line-level and trailing).
-5. Integration — ``ToolchainRunner`` fail-fast with drift present; clean diff
-   leaves the toolchain untouched; ``daemon._execute_and_qa`` forwards
-   ``diff_text=diff`` into the runner.
-"""
-import asyncio
-import importlib.util
-import os
-import sys
-from pathlib import Path
-from unittest.mock import AsyncMock, MagicMock, patch
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from sentinel import DriftCheckResult, TypeDriftSentinel
-from verifier import CommandResult, ToolchainResult
-
-REPO_ROOT = Path(__file__).resolve().parent.parent
-
-# ---------------------------------------------------------------------------
-# Helpers
-# ---------------------------------------------------------------------------
-
-
-def _diff(path: str, *added_lines: str, start: int = 1) -> str:
-    """Build a minimal git diff with *added_lines* under one new-file hunk."""
-    hunks = "".join(f"+{line}\n" for line in added_lines)
-    return (
-        f"diff --git a/{path} b/{path}\n"
-        f"--- a/{path}\n"
-        f"+++ b/{path}\n"
-        f"@@ -1,1 +{start},{len(added_lines)} @@\n"
-        f"{hunks}"
-    )
-
-
-_TS_DIFF = _diff(
-    "apps/api/src/user.ts",
-    "export interface CreateUserDTO {",
-    "  name: string;",
-    "}",
-)
-
-_KT_DATA_DIFF = _diff(
-    "services/orders/Order.kt",
-    "data class OrderResponse(",
-    "    val id: Long,",
-    ")",
-)
-
-_KT_PLAIN_DIFF = _diff("services/orders/Invoice.kt", "class InvoiceRequest(")
-
-_PY_DIFF = _diff(
-    "src/models/user.py",
-    "class CreateUserDTO(BaseModel):",
-    "    name: str",
-)
-
-
-def _load_assembler():
-    """Import scripts/prompt-build/assemble_system_prompt.py from the repo root."""
-    spec = importlib.util.spec_from_file_location(
-        "assemble_system_prompt",
-        REPO_ROOT / "scripts/prompt-build/assemble_system_prompt.py",
-    )
-    mod = importlib.util.module_from_spec(spec)
-    assert spec and spec.loader
-    spec.loader.exec_module(mod)
-    return mod
-
-
-class _Toolchain:
-    def __init__(self, lint=None, build=None, test=None):
-        self.lint_cmd = lint
-        self.build_cmd = build
-        self.test_cmd = test
-
-
-class _Profile:
-    def __init__(self, toolchain=None):
-        self.toolchain = toolchain
-
-
-# ---------------------------------------------------------------------------
-# 1. Prompt assembly (mandate fragment + version)
-# ---------------------------------------------------------------------------
-
-
-def test_assembler_includes_no_manual_dto_mandate_with_version_930(tmp_path):
-    mod = _load_assembler()
-    out = tmp_path / "assembled.md"
-    result = mod.assemble(
-        output_path=str(out),
-        fragments_dir=str(REPO_ROOT / "prompts/fragments"),
-        manifest_path=str(REPO_ROOT / "prompts/manifest.txt"),
-    )
-
-    # Mandate block present with both open and close tags.
-    assert "<no_manual_dto_mandate>" in result
-    assert "</no_manual_dto_mandate>" in result
-
-    # Version fragment reflected in the artifact (dynamic: reads active version
-    # from prompts/fragments/01-system_version.md so the gate survives bumps).
-    import re
-    version_frag = (REPO_ROOT / "prompts/fragments/01-system_version.md").read_text(
-        encoding="utf-8"
-    )
-    m = re.search(r"<system_version>([^<]+)</system_version>", version_frag)
-    assert m, "system_version fragment missing <system_version> tag"
-    active_version = m.group(1).strip()
-    assert active_version in version_frag
-    assert f"<system_version>{active_version}</system_version>" in result
-
-    # Closing-tag normalization: no indented pure closing tags survive.
-    drifted = [
-        line
-        for line in result.splitlines()
-        if line.startswith(" ") and line.lstrip().startswith("</")
-    ]
-    assert not drifted, f"Drifted closing tags found: {drifted}"
-
-
-def test_manifest_registers_mandate_before_initialization():
-    manifest = (REPO_ROOT / "prompts/manifest.txt").read_text(encoding="utf-8").splitlines()
-    assert "18-no_manual_dto_mandate.md" in manifest
-    assert manifest.index("18-no_manual_dto_mandate.md") < manifest.index(
-        "19-initialization.md"
-    )
-
-
-# ---------------------------------------------------------------------------
-# 2. Detection of manual declarations in consumer paths
-# ---------------------------------------------------------------------------
-
-
-def test_detects_typescript_interface():
-    result = TypeDriftSentinel().check_diff(_TS_DIFF)
-    assert result.passed is False
-    assert any("CreateUserDTO" in v for v in result.violations)
-    assert any("apps/api/src/user.ts" in v for v in result.violations)
-
-
-def test_detects_kotlin_data_class():
-    result = TypeDriftSentinel().check_diff(_KT_DATA_DIFF)
-    assert result.passed is False
-    assert any("OrderResponse" in v for v in result.violations)
-
-
-def test_detects_kotlin_plain_class():
-    result = TypeDriftSentinel().check_diff(_KT_PLAIN_DIFF)
-    assert result.passed is False
-    assert any("InvoiceRequest" in v for v in result.violations)
-
-
-def test_detects_python_pydantic_model():
-    result = TypeDriftSentinel().check_diff(_PY_DIFF)
-    assert result.passed is False
-    assert any("CreateUserDTO" in v for v in result.violations)
-    assert any("Python" in v for v in result.violations)
-
-
-def test_multiple_language_violations_captured():
-    combined = _TS_DIFF + _KT_DATA_DIFF + _PY_DIFF
-    result = TypeDriftSentinel().check_diff(combined)
-    assert result.passed is False
-    assert len(result.violations) == 3
-
-
-# ---------------------------------------------------------------------------
-# 3. Exemptions (allowed/contract paths, clean imports)
-# ---------------------------------------------------------------------------
-
-
-def test_allows_dto_in_shared_schema():
-    diff = _diff(
-        "packages/shared-schema/v1/types.ts",
-        "export interface UserDTO { id: string; }",
-    )
-    result = TypeDriftSentinel().check_diff(diff)
-    assert result.passed is True
-
-
-def test_allows_dto_in_generated_dir():
-    diff = _diff(
-        "apps/web/src/generated/api.ts",
-        "export interface CreateUserDTO { id: string; }",
-    )
-    result = TypeDriftSentinel().check_diff(diff)
-    assert result.passed is True
-
-
-def test_allows_dto_in_gen_file():
-    diff = _diff(
-        "apps/web/src/client.gen.ts",
-        "export interface UserResponse { ok: boolean; }",
-    )
-    result = TypeDriftSentinel().check_diff(diff)
-    assert result.passed is True
-
-
-def test_allows_clean_imports():
-    diff = _diff(
-        "apps/web/src/api.ts",
-        "import { ShiftDTO, exactOptionalPropertyTypes } from '@repo/shared-schema';",
-        "import type { UserDTO } from '@repo/shared-schema';",
-    )
-    result = TypeDriftSentinel().check_diff(diff)
-    assert result.passed is True
-
-
-def test_allows_type_reexport():
-    diff = _diff(
-        "apps/web/src/barrel.ts",
-        "export type { UserDTO, OrderResponse } from '@repo/shared-schema';",
-    )
-    result = TypeDriftSentinel().check_diff(diff)
-    assert result.passed is True
-
-
-def test_non_consumer_path_not_flagged():
-    diff = _diff(
-        "config/settings.ts",
-        "export interface SettingsDTO { theme: string; }",
-    )
-    result = TypeDriftSentinel().check_diff(diff)
-    assert result.passed is True
-
-
-def test_empty_diff_passes():
-    assert TypeDriftSentinel().check_diff("").passed is True
-
-
-def test_context_only_diff_passes():
-    diff = (
-        "diff --git a/apps/api/src/user.ts b/apps/api/src/user.ts\n"
-        "--- a/apps/api/src/user.ts\n"
-        "+++ b/apps/api/src/user.ts\n"
-        "@@ -10,3 +10,3 @@\n"
-        " export function getUser() {\n"
-        "-  return git;\n"
-        "+  return branch;\n"
-        " }\n"
-    )
-    assert TypeDriftSentinel().check_diff(diff).passed is True
-
-
-# ---------------------------------------------------------------------------
-# 4. drift-ignore bypass
-# ---------------------------------------------------------------------------
-
-
-def test_drift_ignore_trailing_comment_bypass():
-    diff = _diff(
-        "apps/web/src/legacy.ts",
-        "export interface LegacyDTO { x: string } // drift-ignore: legacy mirror",
-    )
-    assert TypeDriftSentinel().check_diff(diff).passed is True
-
-
-def test_drift_ignore_comment_line_bypass():
-    diff = _diff(
-        "apps/web/src/adapters.ts",
-        "// drift-ignore: generated adapter, mirror kept in sync by tooling",
-        "export interface AdapterDTO { x: string } // drift-ignore: kept in sync",
-    )
-    assert TypeDriftSentinel().check_diff(diff).passed is True
-
-
-# ---------------------------------------------------------------------------
-# 5. Report quality
-# ---------------------------------------------------------------------------
-
-
-def test_report_contains_actionable_instructions():
-    result = TypeDriftSentinel().check_diff(_PY_DIFF)
-    assert not result.passed
-    assert "Required Action" in result.report_md
-    assert "@repo/shared-schema" in result.report_md
-    assert "prisma generate" in result.report_md
-    assert "protoc" in result.report_md
-    assert "drift-ignore" in result.report_md
-
-
-def test_line_numbers_tracked():
-    diff = _diff("apps/api/src/user.ts", "export interface CreateUserDTO {", start=7)
-    result = TypeDriftSentinel().check_diff(diff)
-    assert any("added line 7" in v for v in result.violations)
-
-
-def test_custom_patterns():
-    sentinel = TypeDriftSentinel(
-        consumer_patterns=["packages/mobile/**"],
-        allowed_patterns=["packages/mobile/generated/**"],
-    )
-    # Consumer in custom pattern.
-    bad = _diff("packages/mobile/src/api.kt", "data class UserModel(")
-    assert sentinel.check_diff(bad).passed is False
-    # Allowed under custom pattern.
-    good = _diff("packages/mobile/generated/api.kt", "data class UserModel(")
-    assert sentinel.check_diff(good).passed is True
-
-
-# ---------------------------------------------------------------------------
-# 6. ToolchainRunner / daemon integration
-# ---------------------------------------------------------------------------
-
-
-def test_toolchain_runner_failfast_on_drift():
-    from verifier import ToolchainRunner
-
-    profile = _Profile(_Toolchain(lint="echo lint", build="echo build", test="echo test"))
-    result = ToolchainRunner().run_sync(profile, diff_text=_TS_DIFF)
-
-    assert result.passed is False
-    assert len(result.commands) == 1, "fail-fast: no toolchain commands ran"
-    cmd = result.commands[0]
-    assert cmd.command == "type-drift-sentinel"
-    assert cmd.cmd_type == "lint"
-    assert cmd.passed is False
-    assert "CreateUserDTO" in cmd.stderr
-
-
-def test_toolchain_runner_passes_without_drift():
-    from verifier import ToolchainRunner
-
-    diff = _diff(
-        "apps/api/src/user.ts",
-        "import { UserDTO } from '@repo/shared-schema';",
-    )
-    profile = _Profile(_Toolchain())
-    result = ToolchainRunner().run_sync(profile, diff_text=diff)
-
-    assert result.passed is True
-    # Sentinel passed silently — no sentinel command recorded, toolchain ran
-    # as usual (3 nullable commands -> skipped).
-    assert all(c.skipped for c in result.commands)
-    assert all(c.command != "type-drift-sentinel" for c in result.commands)
-
-
-def test_toolchain_runner_without_diff_text_unchanged():
-    from verifier import ToolchainRunner
-
-    profile = _Profile(_Toolchain())
-    result = ToolchainRunner().run_sync(profile)
-    assert result.passed is True
-    assert len(result.commands) == 3
-
-
-def test_daemon_passes_diff_text_to_runner(tmp_path):
-    import daemon as daemon_mod
-
-    diff_body = (
-        "diff --git a/apps/api/src/user.ts b/apps/api/src/user.ts\n"
-        "@@ -1 +1,2 @@\n"
-        "+export interface CreateUserDTO {\n"
-    )
-    task_file = tmp_path / "99-foo.md"
-    task_file.write_text(
-        "# Task 99: Foo\n\n## Factual Git Diff\n\n"
-        "<!-- BEGIN_GIT_DIFF -->\n" + diff_body + "<!-- END_GIT_DIFF -->\n",
-        encoding="utf-8",
-    )
-
-    state = MagicMock()
-    executor = MagicMock()
-    executor.execute = AsyncMock(return_value={"status": "complete"})
-    qa = MagicMock()
-    qa.run_qa.return_value = {"result": "PASSED"}
-
-    with patch.object(daemon_mod, "ToolchainRunner") as toolchain_cls:
-        toolchain_cls.return_value.run = AsyncMock(
-            return_value=ToolchainResult(passed=True, summary="ok", report_md="")
-        )
-        asyncio.run(
-            daemon_mod._execute_and_qa(
-                99,
-                str(task_file),
-                task_file.read_text(encoding="utf-8"),
-                task_file,
-                state,
-                executor,
-                qa,
-            )
-        )
-
-    call = toolchain_cls.return_value.run.await_args
-    assert call is not None
-    assert call.kwargs["diff_text"] == diff_body.strip()
-    qa.run_qa.assert_called_once()
\ No newline at end of file
diff --git a/loop-engine/test_specs.py b/loop-engine/test_specs.py
deleted file mode 100644
index 50794f6..0000000
--- a/loop-engine/test_specs.py
+++ /dev/null
@@ -1,426 +0,0 @@
-"""Tests for the Spec-First Artifact Pipeline & State Gate (LE-8 / Task 140).
-
-Covers:
-1. ``SpecGateEngine.evaluate_requirements`` — keyword matching for architectural
-   tasks vs routine/bugfix tasks (empty rules, no keyword hits).
-2. ``SpecGateEngine.validate_artifacts`` — workspace scan passes when an ADR /
-   contract exists; diff-text staging passes; failing with a diagnostic report
-   when a required artifact is absent; empty-rule immediate pass.
-3. State machine migration — ``spec_artifacts`` column on new and pre-migration
-   DBs, ``set_spec_artifacts``/``get_spec_artifacts`` round-trip, corrupt JSON
-   fallback.
-4. Daemon integration — spec gate crashes a task before ``IMPLEMENTING`` with
-   ``qa_feedback``; passing gate proceeds and persists verified artifacts.
-"""
-import asyncio
-import json
-import os
-import sqlite3
-import sys
-from pathlib import Path
-from unittest.mock import AsyncMock, MagicMock, patch
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from models import (
-    LoopEngineConfig,
-    SpecArtifactType,
-    SpecGateConfig,
-    SpecRequirementRule,
-    TaskState,
-)
-from state import StateMachine
-
-import daemon
-from specs import SpecGateEngine, SpecValidationResult, _paths_in_diff
-
-
-# ---------------------------------------------------------------------------
-# Fixtures / helpers
-# ---------------------------------------------------------------------------
-
-def _make_workspace(tmp_path):
-    """Build a minimal workspace with tasks/ + spec artifact directories."""
-    for sub in ("backlog", "in-progress", "qa", "completed", "archive"):
-        (tmp_path / "tasks" / sub).mkdir(parents=True, exist_ok=True)
-    (tmp_path / "docs" / "adr").mkdir(parents=True, exist_ok=True)
-    (tmp_path / "contracts").mkdir(parents=True, exist_ok=True)
-    (tmp_path / "migrations").mkdir(parents=True, exist_ok=True)
-    return tmp_path
-
-
-def _arch_rules():
-    """Default spec rules (architecture-decision, api-contract, database-schema)."""
-    from models import _default_spec_rules
-    return _default_spec_rules()
-
-
-def _engine(rules=None, enabled=True):
-    return SpecGateEngine(SpecGateConfig(enabled=enabled, rules=rules))
-
-
-_ARCH_TASK = (
-    "# Task 99: Redesign the payment architecture\n"
-    "## Goal\nRedesign the billing service architecture.\n"
-)
-
-_ROUTINE_TASK = (
-    "# Task 100: Fix typo\n"
-    "## Goal\nFix a typo in the README.\n"
-)
-
-_DIFF_WITH_ADR = """diff --git a/docs/adr/001-billing.md b/docs/adr/001-billing.md
-new file mode 100644
-index 0000000..e69de29
---- /dev/null
-+++ b/docs/adr/001-billing.md
-"""
-
-
-# ---------------------------------------------------------------------------
-# 1. evaluate_requirements
-# ---------------------------------------------------------------------------
-
-def test_evaluate_requirements_matches_architectural_keywords():
-    rules = _engine(_arch_rules())
-    matched = rules.evaluate_requirements(_ARCH_TASK)
-    assert len(matched) == 1
-    assert matched[0].name == "architecture-decision"
-
-
-def test_evaluate_requirements_no_match_for_routine_task():
-    rules = _engine(_arch_rules())
-    assert rules.evaluate_requirements(_ROUTINE_TASK) == []
-
-
-def test_evaluate_requirements_plan_text_also_triggered():
-    rules = _engine(_arch_rules())
-    # Keywords live in the approved plan, not the task content.
-    matched = rules.evaluate_requirements("simple task", "Introduce grpc proto contract")
-    assert len(matched) == 1
-    assert matched[0].name == "api-contract"
-
-
-def test_evaluate_requirements_empty_rules():
-    rules = _engine(rules=[])
-    assert rules.evaluate_requirements(_ARCH_TASK, "architecture") == []
-
-
-def test_evaluate_requirements_disabled_gate_still_evaluates():
-    # enabled=False only stops enforcement in the daemon; evaluation stays pure.
-    rules = _engine(_arch_rules(), enabled=False)
-    assert rules.evaluate_requirements(_ARCH_TASK) != []
-
-
-# ---------------------------------------------------------------------------
-# 2. validate_artifacts
-# ---------------------------------------------------------------------------
-
-def test_validate_artifacts_passes_when_adr_exists_in_workspace(tmp_path):
-    ws = _make_workspace(tmp_path)
-    (ws / "docs" / "adr" / "0001-billing.md").write_text("# ADR 1\n")
-    rules = _engine(_arch_rules())
-    res = rules.validate_artifacts(rules.evaluate_requirements(_ARCH_TASK), ws)
-    assert res.passed is True
-    assert res.errors == []
-    assert "docs/adr/0001-billing.md" in res.found_artifacts
-    assert "docs/adr/0001-billing.md" in res.report_md
-
-
-def test_validate_artifacts_passes_when_contract_in_workspace(tmp_path):
-    ws = _make_workspace(tmp_path)
-    (ws / "contracts" / "billing.yaml").write_text("openapi: 3.0.0\n")
-    rules = _engine(_arch_rules())
-    task = "# Task: Add new endpoint\n## Goal\nAdd openapi endpoint\n"
-    matched = rules.evaluate_requirements(task)
-    assert matched[0].name == "api-contract"
-    res = rules.validate_artifacts(matched, ws)
-    assert res.passed is True
-    assert "contracts/billing.yaml" in res.found_artifacts
-
-
-def test_validate_artifacts_passes_when_artifact_in_diff_text(tmp_path):
-    ws = _make_workspace(tmp_path)
-    rules = _engine(_arch_rules())
-    # No ADR on disk, but the staged diff adds one.
-    res = rules.validate_artifacts(rules.evaluate_requirements(_ARCH_TASK), ws, diff_text=_DIFF_WITH_ADR)
-    assert res.passed is True
-    assert "docs/adr/001-billing.md" in res.found_artifacts
-
-
-def test_validate_artifacts_fails_with_diagnostic_report_when_absent(tmp_path):
-    ws = _make_workspace(tmp_path)
-    rules = _engine(_arch_rules())
-    res = rules.validate_artifacts(rules.evaluate_requirements(_ARCH_TASK), ws)
-    assert res.passed is False
-    assert len(res.errors) == 1
-    assert "architecture-decision" in res.errors[0]
-    assert "docs/adr/**" in res.errors[0]
-    # Markdown report contains verified + missing sections
-    assert "# Spec-First Gate Report" in res.report_md
-    assert "Missing Spec Artifacts" in res.report_md
-    assert "architecture-decision" in res.report_md
-    assert "Verified Artifacts" not in res.report_md
-
-
-def test_validate_artifacts_empty_rules_passes_immediately(tmp_path):
-    ws = _make_workspace(tmp_path)
-    res = _engine(rules=[]).validate_artifacts([], ws)
-    assert res.passed is True
-    assert res.found_artifacts == []
-    assert res.errors == []
-
-
-def test_validate_artifacts_data_model_rule_matches_migration(tmp_path):
-    ws = _make_workspace(tmp_path)
-    (ws / "migrations" / "0001_users.sql").write_text("CREATE TABLE users;")
-    rules = _engine(_arch_rules())
-    task = "# Task: Add a new table\n## Goal\nCreate sql migration for users\n"
-    matched = rules.evaluate_requirements(task)
-    assert [r.name for r in matched] == ["database-schema"]
-    res = rules.validate_artifacts(matched, ws)
-    assert res.passed is True
-    assert "migrations/0001_users.sql" in res.found_artifacts
-
-
-# --- helper: _paths_in_diff ---
-
-def test_paths_in_diff_parses_headers():
-    assert _paths_in_diff(_DIFF_WITH_ADR) == ["docs/adr/001-billing.md"]
-    assert _paths_in_diff("") == []
-    assert _paths_in_diff("no headers") == []
-
-
-def test_paths_in_diff_deduplicates():
-    diff = _DIFF_WITH_ADR + _DIFF_WITH_ADR
-    assert _paths_in_diff(diff) == ["docs/adr/001-billing.md"]
-
-
-# ---------------------------------------------------------------------------
-# 3. State machine migration + accessors
-# ---------------------------------------------------------------------------
-
-def test_state_spec_artifacts_roundtrip(tmp_path):
-    sm = StateMachine(str(tmp_path / "loop.db"))
-    try:
-        tid = sm.register_task("tasks/backlog/140-spec.md")
-        sm.set_spec_artifacts(tid, ["docs/adr/001.md", "contracts/api.yaml"])
-        assert sm.get_task(tid)["spec_artifacts"] == json.dumps(
-            ["docs/adr/001.md", "contracts/api.yaml"]
-        )
-        assert sm.get_spec_artifacts(tid) == ["docs/adr/001.md", "contracts/api.yaml"]
-    finally:
-        sm.close()
-
-
-def test_state_spec_artifacts_empty_and_corrupt(tmp_path):
-    sm = StateMachine(str(tmp_path / "loop.db"))
-    try:
-        tid = sm.register_task("tasks/backlog/140b.md")
-        assert sm.get_spec_artifacts(tid) == []
-        sm.set_spec_artifacts(tid, [])
-        assert sm.get_spec_artifacts(tid) == []
-        # Corrupt persisted JSON -> [] fallback
-        sm.conn.execute("UPDATE tasks SET spec_artifacts = ? WHERE task_id = ?",
-                        ("{not-json", tid))
-        sm.conn.commit()
-        assert sm.get_spec_artifacts(tid) == []
-        # Non-list JSON -> [] fallback
-        sm.set_spec_artifacts(tid, ["a"])
-        sm.conn.execute("UPDATE tasks SET spec_artifacts = ? WHERE task_id = ?",
-                        ('"scalar"', tid))
-        sm.conn.commit()
-        assert sm.get_spec_artifacts(tid) == []
-    finally:
-        sm.close()
-
-
-def test_state_migration_adds_column_to_old_db(tmp_path):
-    """A DB created WITHOUT spec_artifacts gains the column via the safe ALTER."""
-    db_path = tmp_path / "legacy.db"
-    conn = sqlite3.connect(str(db_path))
-    conn.executescript(
-        """
-        CREATE TABLE tasks (
-            task_id INTEGER PRIMARY KEY,
-            task_file TEXT NOT NULL UNIQUE,
-            state TEXT NOT NULL DEFAULT 'backlog',
-            created_at REAL NOT NULL,
-            updated_at REAL NOT NULL
-        );
-        """
-    )
-    conn.execute(
-        "INSERT INTO tasks (task_file, created_at, updated_at) VALUES ('tasks/backlog/legacy.md', 1, 1)"
-    )
-    conn.commit()
-    conn.close()
-
-    sm = StateMachine(str(db_path))
-    try:
-        cols = [r[1] for r in sm.conn.execute("PRAGMA table_info(tasks)").fetchall()]
-        assert "spec_artifacts" in cols
-        row = sm.conn.execute(
-            "SELECT spec_artifacts FROM tasks WHERE task_file = 'tasks/backlog/legacy.md'"
-        ).fetchone()
-        assert row[0] is None
-    finally:
-        sm.close()
-
-
-def test_state_migration_idempotent_on_new_db(tmp_path):
-    """New DBs already declare the column; the ALTER no-ops without error."""
-    sm = StateMachine(str(tmp_path / "loop.db"))
-    try:
-        cols = [r[1] for r in sm.conn.execute("PRAGMA table_info(tasks)").fetchall()]
-        assert "spec_artifacts" in cols
-        tid = sm.register_task("tasks/backlog/140c.md")
-        assert sm.get_spec_artifacts(tid) == []
-    finally:
-        sm.close()
-
-
-# ---------------------------------------------------------------------------
-# 4. Daemon integration (real _process_task)
-# ---------------------------------------------------------------------------
-
-def _make_daemon_stubs(config):
-    router = MagicMock()
-    router.route_plan.return_value = {"plan": "routing"}
-    router.call_llm.return_value = "Approved plan text"
-    gateway = MagicMock()
-    gateway.request_approval = AsyncMock(return_value=True)
-    executor = MagicMock()
-    qa = MagicMock()
-    qa.run_review.return_value = {"result": "APPROVED"}
-    brainstorm = MagicMock()
-    brainstorm.should_trigger.return_value = False
-    return router, gateway, executor, qa, brainstorm
-
-
-def _write_task(ws, text):
-    task_file = ws / "tasks" / "in-progress" / "140-spec.md"
-    task_file.write_text(text)
-    return task_file
-
-
-def _run_pipeline(ws, task_file, config, executor_cls=None):
-    """Run the real _process_task with fake execute_and_qa that records the gate state."""
-    router, gateway, executor, qa, brainstorm = _make_daemon_stubs(config)
-    state = StateMachine(str(ws / "loop.db"))
-    tid = state.register_task(str(task_file), TaskState.AWAITING_APPROVAL)
-
-    captured = {}
-
-    async def _fake_execute_and_qa(*args, **kwargs):
-        captured["entered_executing"] = state.get_task(tid)["state"]
-        return {"result": "PASSED", "report": "ok"}
-
-    async def _run():
-        await daemon._process_task(
-            tid, str(task_file), config, state, router, gateway, executor, qa, brainstorm
-        )
-
-    with patch.object(daemon, "_execute_and_qa", new=_fake_execute_and_qa):
-        with patch.object(daemon, "REPO_ROOT", ws):
-            asyncio.run(_run())
-    return tid, state, captured
-
-
-def _spec_config(rules):
-    return LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto",
-                            spec_gate=SpecGateConfig(enabled=True, rules=rules))
-
-
-def test_daemon_spec_gate_passes_and_proceeds(tmp_path):
-    ws = _make_workspace(tmp_path)
-    (ws / "docs" / "adr" / "0001.md").write_text("# ADR 1\n")
-    task_file = _write_task(ws, _ARCH_TASK)
-    config = _spec_config(_arch_rules())
-
-    tid, state, captured = _run_pipeline(ws, task_file, config)
-    try:
-        # Gate passed -> execution entered, artifacts persisted
-        assert captured["entered_executing"] == "implementing"
-        assert state.get_spec_artifacts(tid) == ["docs/adr/0001.md"]
-    finally:
-        state.close()
-
-
-def test_daemon_spec_gate_failure_crashes_before_implementing(tmp_path):
-    ws = _make_workspace(tmp_path)  # no ADR anywhere
-    task_file = _write_task(ws, _ARCH_TASK)
-    config = _spec_config(_arch_rules())
-
-    tid, state, captured = _run_pipeline(ws, task_file, config)
-    try:
-        assert state.get_task(tid)["state"] == "crashed"
-        assert "entered_executing" not in captured  # never reached IMPLEMENTING
-        assert "architecture-decision" in (state.get_task(tid)["qa_feedback"] or "")
-        assert "# Spec-First Gate Report" in (state.get_task(tid)["qa_feedback"] or "")
-        assert state.get_spec_artifacts(tid) == []
-    finally:
-        state.close()
-
-
-def test_daemon_spec_gate_disabled_proceeds_without_gate(tmp_path):
-    ws = _make_workspace(tmp_path)  # no ADR
-    task_file = _write_task(ws, _ARCH_TASK)
-    config = LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto",
-                              spec_gate=SpecGateConfig(enabled=False, rules=_arch_rules()))
-
-    tid, state, captured = _run_pipeline(ws, task_file, config)
-    try:
-        assert captured["entered_executing"] == "implementing"
-        assert state.get_spec_artifacts(tid) == []
-    finally:
-        state.close()
-
-
-def test_daemon_spec_gate_routine_task_bypasses(tmp_path):
-    ws = _make_workspace(tmp_path)  # no artifacts
-    task_file = _write_task(ws, _ROUTINE_TASK)
-    config = _spec_config(_arch_rules())
-
-    tid, state, captured = _run_pipeline(ws, task_file, config)
-    try:
-        assert captured["entered_executing"] == "implementing"
-        assert state.get_spec_artifacts(tid) == []
-    finally:
-        state.close()
-
-
-def test_loop_engine_config_default_spec_gate():
-    cfg = LoopEngineConfig(approval={"chat_id": 0})
-    assert cfg.spec_gate.enabled is True
-    assert cfg.spec_gate.rules == []
-    assert isinstance(cfg.spec_gate, SpecGateConfig)
-
-
-def test_default_spec_rules_shapes():
-    rules = _arch_rules()
-    assert [r.name for r in rules] == [
-        "architecture-decision", "api-contract", "database-schema"
-    ]
-    arch, api, db = rules
-    assert arch.required_artifacts == [SpecArtifactType.ADR]
-    assert arch.target_directories == ["docs/adr/**", "docs/architecture.md"]
-    assert api.required_artifacts == [SpecArtifactType.CONTRACT]
-    assert api.target_directories == ["contracts/**", "openapi/**", "proto/**"]
-    assert db.required_artifacts == [SpecArtifactType.DATA_MODEL]
-    assert db.target_directories == ["docs/data_model.md", "prisma/**", "migrations/**"]
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = failed = 0
-    for t in tests:
-        try:
-            t(Path("/tmp/specs-test-ws")) if "tmp_path" in t.__code__.co_varnames else t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            print(f"  FAIL: {t.__name__}: {e}")
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
\ No newline at end of file
diff --git a/loop-engine/test_stacks.py b/loop-engine/test_stacks.py
deleted file mode 100644
index ff3301f..0000000
--- a/loop-engine/test_stacks.py
+++ /dev/null
@@ -1,337 +0,0 @@
-"""Tests for stacks.py — Stack Profile Engine (Task 133)."""
-import sys, os, tempfile, json, asyncio
-from pathlib import Path
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from models import LoopEngineConfig, StackProfileConfig, StackDetectionConfig, StackToolchainConfig
-from stacks import StackProfile, StackRegistry, StackDetector, PreflightRunner
-
-
-# Helpers
-def make_registry(tmp_path: Path, profiles: dict) -> StackRegistry:
-    """Create YAML files in tmp_path/stacks and return registry."""
-    stacks_dir = tmp_path / "stacks"
-    stacks_dir.mkdir(parents=True, exist_ok=True)
-    for name, data in profiles.items():
-        # Use yaml if available else json
-        try:
-            import yaml
-            (stacks_dir / f"{name}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
-        except ImportError:
-            (stacks_dir / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")
-    return StackRegistry(str(stacks_dir))
-
-
-# ---------------------------------------------------------------------------
-# Profile parsing
-# ---------------------------------------------------------------------------
-
-def test_stack_profile_config_defaults():
-    cfg = StackProfileConfig(name="test", display_name="Test")
-    assert cfg.detection.marker_files == []
-    assert cfg.detection.extensions == []
-    assert cfg.skills == []
-    assert cfg.preflight == []
-    assert cfg.toolchain.test_cmd is None
-
-
-def test_stack_profile_config_full():
-    cfg = StackProfileConfig(
-        name="node-ts",
-        display_name="Node TS",
-        detection=StackDetectionConfig(
-            marker_files=["package.json"],
-            extensions=[".ts"],
-            task_keywords=["node"]
-        ),
-        skills=["nextjs"],
-        preflight=["node --version"],
-        toolchain=StackToolchainConfig(test_cmd="npm test")
-    )
-    assert cfg.detection.marker_files == ["package.json"]
-    assert cfg.skills == ["nextjs"]
-    assert cfg.toolchain.test_cmd == "npm test"
-
-
-def test_stack_profile_invalid_missing_name():
-    try:
-        StackProfileConfig(display_name="No Name")  # type: ignore
-        assert False, "Should fail without name"
-    except Exception:
-        pass
-
-
-def test_stack_registry_loads_generic():
-    r = StackRegistry("stacks")
-    profiles = r.list_profiles()
-    names = [p.name for p in profiles]
-    assert "generic" in names
-    assert len(names) >= 5
-
-
-def test_stack_registry_get_profile():
-    r = StackRegistry("stacks")
-    p = r.get_profile("node-ts")
-    assert p is not None
-    assert p.name == "node-ts"
-    assert "package.json" in p.detection.marker_files
-    assert p.get_profile is None if False else True  # dummy to avoid lint
-
-
-def test_stack_registry_nonexistent_returns_none():
-    r = StackRegistry("stacks")
-    assert r.get_profile("does-not-exist") is None
-
-
-def test_stack_registry_invalid_schema_rejection():
-    with tempfile.TemporaryDirectory() as tmp:
-        tmp = Path(tmp)
-        stacks_dir = tmp / "stacks"
-        stacks_dir.mkdir()
-        # Invalid: missing display_name
-        (stacks_dir / "bad.yaml").write_text("name: bad\n", encoding="utf-8")
-        r = StackRegistry(str(stacks_dir))
-        try:
-            r.list_profiles()
-            assert False, "Should have raised ValueError"
-        except ValueError as e:
-            assert "bad.yaml" in str(e) or "Failed to load" in str(e)
-
-
-def test_stack_profile_yaml_and_json_both_supported():
-    with tempfile.TemporaryDirectory() as tmp:
-        tmp = Path(tmp)
-        stacks_dir = tmp / "stacks"
-        stacks_dir.mkdir()
-        # JSON file
-        data = {"name": "json-stack", "display_name": "JSON Stack"}
-        (stacks_dir / "json-stack.json").write_text(json.dumps(data), encoding="utf-8")
-        # YAML file
-        try:
-            import yaml
-            yaml_data = {"name": "yaml-stack", "display_name": "YAML Stack"}
-            (stacks_dir / "yaml-stack.yaml").write_text(yaml.safe_dump(yaml_data), encoding="utf-8")
-        except ImportError:
-            pass
-        r = StackRegistry(str(stacks_dir))
-        assert r.get_profile("json-stack") is not None
-        if (stacks_dir / "yaml-stack.yaml").exists():
-            assert r.get_profile("yaml-stack") is not None
-
-
-# ---------------------------------------------------------------------------
-# Detection precedence
-# ---------------------------------------------------------------------------
-
-def test_detection_explicit_header_overrides_all():
-    with tempfile.TemporaryDirectory() as tmp:
-        tmp = Path(tmp)
-        # Create workspace with python marker to tempt wrong detection
-        (tmp / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
-        r = StackRegistry("stacks")
-        task = "**Stack:** node-ts\nDo something generic"
-        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
-        assert detected.name == "node-ts", f"Expected node-ts, got {detected.name}"
-
-
-def test_detection_marker_files_before_keywords():
-    with tempfile.TemporaryDirectory() as tmp:
-        tmp = Path(tmp)
-        (tmp / "go.mod").write_text("module foo\n", encoding="utf-8")
-        r = StackRegistry("stacks")
-        # Task mentions python but workspace has go.mod
-        task = "Fix python endpoint"
-        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
-        assert detected.name == "go-gin", f"Expected go-gin marker, got {detected.name}"
-
-
-def test_detection_extensions_fallback():
-    with tempfile.TemporaryDirectory() as tmp:
-        tmp = Path(tmp)
-        sub = tmp / "app"
-        sub.mkdir()
-        (sub / "main.go").write_text("package main\n", encoding="utf-8")
-        r = StackRegistry("stacks")
-        task = "random task without keywords"
-        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
-        assert detected.name == "go-gin", f"Expected go-gin via .go extension, got {detected.name}"
-
-
-def test_detection_keywords_after_marker_miss():
-    with tempfile.TemporaryDirectory() as tmp:
-        tmp = Path(tmp)
-        r = StackRegistry("stacks")
-        task = "This is a Kotlin Android compose task"
-        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
-        assert detected.name == "kotlin-android", f"Expected kotlin-android via keyword, got {detected.name}"
-
-
-def test_detection_generic_fallback():
-    with tempfile.TemporaryDirectory() as tmp:
-        tmp = Path(tmp)
-        r = StackRegistry("stacks")
-        task = "Completely unknown stack task with no markers or keywords xyz123"
-        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
-        assert detected.name == "generic"
-
-
-def test_detection_header_plain_format():
-    with tempfile.TemporaryDirectory() as tmp:
-        tmp = Path(tmp)
-        r = StackRegistry("stacks")
-        task = "Stack: python-fastapi\nImplement endpoint"
-        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
-        assert detected.name == "python-fastapi"
-
-
-# ---------------------------------------------------------------------------
-# Preflight runner
-# ---------------------------------------------------------------------------
-
-def test_preflight_success():
-    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["echo hello", "echo world"])
-    profile = StackProfile(cfg)
-    runner = PreflightRunner(timeout_seconds=5)
-    result = runner.run_sync(profile)
-    assert result.passed is True
-    assert result.errors == []
-    assert len(result.outputs) == 2
-
-
-def test_preflight_failure_nonzero():
-    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["false"])
-    profile = StackProfile(cfg)
-    runner = PreflightRunner(timeout_seconds=5)
-    result = runner.run_sync(profile)
-    assert result.passed is False
-    assert len(result.errors) == 1
-    assert "false" in result.errors[0]
-
-
-def test_preflight_timeout():
-    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["sleep 2"])
-    profile = StackProfile(cfg)
-    runner = PreflightRunner(timeout_seconds=0.3)
-    result = runner.run_sync(profile)
-    assert result.passed is False
-    assert any("timeout" in e.lower() for e in result.errors)
-
-
-def test_preflight_empty_is_pass():
-    cfg = StackProfileConfig(name="test", display_name="Test", preflight=[])
-    profile = StackProfile(cfg)
-    runner = PreflightRunner(timeout_seconds=5)
-    result = runner.run_sync(profile)
-    assert result.passed is True
-    assert result.errors == []
-
-
-def test_preflight_mixed_success_and_failure():
-    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["echo ok", "false", "echo again"])
-    profile = StackProfile(cfg)
-    runner = PreflightRunner(timeout_seconds=5)
-    result = runner.run_sync(profile)
-    assert result.passed is False
-    assert len(result.errors) == 1
-
-
-# ---------------------------------------------------------------------------
-# LoopEngineConfig extension
-# ---------------------------------------------------------------------------
-
-def test_loop_engine_config_stack_fields():
-    cfg = LoopEngineConfig(approval={"chat_id": 1})
-    assert cfg.stacks_dir == "stacks"
-    assert cfg.default_stack == "generic"
-    cfg2 = LoopEngineConfig(approval={"chat_id": 1}, stacks_dir="custom/stacks", default_stack="node-ts")
-    assert cfg2.stacks_dir == "custom/stacks"
-    assert cfg2.default_stack == "node-ts"
-
-
-# ---------------------------------------------------------------------------
-# Daemon integration (mock workspace fixtures)
-# ---------------------------------------------------------------------------
-
-def test_daemon_registry_init():
-    from daemon import LoopEngineDaemon
-    from state import StateMachine
-    from router import LLMRouter
-    from gateway import ApprovalGateway
-    from executor import HandsExecutor
-    from qa_engine import QAEngine
-    from brainstorm import BrainstormStage
-
-    cfg = LoopEngineConfig(approval={"chat_id": 0})
-    with tempfile.TemporaryDirectory() as tmp:
-        db = os.path.join(tmp, "loop.db")
-        state = StateMachine(db)
-        router = LLMRouter(cfg, workspace_root=tmp)
-        gateway = ApprovalGateway(cfg)
-        executor = HandsExecutor(cfg, state)
-        qa = QAEngine(cfg, state, router)
-        brainstorm = BrainstormStage(cfg, router, workspace_root=tmp)
-        daemon = LoopEngineDaemon(cfg, state, router, gateway, executor, qa, brainstorm)
-        assert daemon.stack_registry is not None
-        assert daemon.stack_registry.get_profile("generic") is not None
-        state.close()
-
-
-def test_executor_injects_stack_context():
-    from executor import HandsExecutor
-    from state import StateMachine
-
-    cfg = LoopEngineConfig(approval={"chat_id": 0})
-    with tempfile.TemporaryDirectory() as tmp:
-        state = StateMachine(os.path.join(tmp, "db"))
-        ex = HandsExecutor(cfg, state)
-
-        # Create a mock profile
-        profile_cfg = StackProfileConfig(
-            name="python-fastapi",
-            display_name="Python FastAPI",
-            skills=["python-fastapi"],
-            preflight=["echo ok"],
-            toolchain=StackToolchainConfig(test_cmd="pytest -q")
-        )
-        profile = StackProfile(profile_cfg)
-
-        # We only test prompt construction via _run_once mock
-        # Monkey-patch _run_once to capture prompt
-        captured = {}
-
-        async def fake_run_once(task_file, prompt):
-            captured["prompt"] = prompt
-            return {"status": "complete", "output": "[goal:complete]", "error": "", "elapsed": 0.1}
-
-        original = ex._run_once
-        ex._run_once = fake_run_once  # type: ignore
-
-        async def run():
-            return await ex.execute(1, "tasks/backlog/01-test.md", "content", stack_profile=profile)
-
-        result = asyncio.run(run())
-        assert result["status"] == "complete"
-        assert "python-fastapi" in captured["prompt"]
-        assert "python-fastapi" in captured["prompt"].lower()
-        assert "pytest -q" in captured["prompt"]
-        ex._run_once = original  # type: ignore
-        state.close()
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = 0
-    failed = 0
-    for t in tests:
-        try:
-            t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            import traceback
-            print(f"  FAIL: {t.__name__}: {e}")
-            traceback.print_exc()
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
diff --git a/loop-engine/test_state.py b/loop-engine/test_state.py
deleted file mode 100644
index fc70488..0000000
--- a/loop-engine/test_state.py
+++ /dev/null
@@ -1,136 +0,0 @@
-"""Tests for state.py — SQLite state machine."""
-import sys, os, tempfile
-sys.path.insert(0, os.path.dirname(__file__))
-
-from state import StateMachine
-from models import TaskState
-
-
-def test_register_task():
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        tid = sm.register_task("tasks/backlog/01-test.md", TaskState.BACKLOG)
-        assert tid is not None
-        task = sm.get_task(tid)
-        assert task["state"] == "backlog"
-        assert task["task_file"] == "tasks/backlog/01-test.md"
-        sm.close()
-
-
-def test_get_task_by_file():
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        sm.register_task("tasks/backlog/02-feature.md")
-        task = sm.get_task_by_file("tasks/backlog/02-feature.md")
-        assert task is not None
-        assert task["task_id"] > 0
-        sm.close()
-
-
-def test_update_state():
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        tid = sm.register_task("tasks/backlog/03-test.md")
-        sm.update_state(tid, TaskState.PLANNING)
-        task = sm.get_task(tid)
-        assert task["state"] == "planning"
-        sm.update_state(tid, TaskState.IMPLEMENTING)
-        task = sm.get_task(tid)
-        assert task["state"] == "implementing"
-        sm.close()
-
-
-def test_set_plan():
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        tid = sm.register_task("tasks/backlog/04-test.md")
-        sm.set_plan(tid, "## Plan\n1. Do stuff")
-        task = sm.get_task(tid)
-        assert task["plan"] == "## Plan\n1. Do stuff"
-        sm.close()
-
-
-def test_qa_feedback_and_retry():
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        tid = sm.register_task("tasks/backlog/05-test.md")
-        sm.set_qa_feedback(tid, "Fix the bug on line 42")
-        task = sm.get_task(tid)
-        assert task["qa_retry_count"] == 1
-        assert task["qa_feedback"] == "Fix the bug on line 42"
-        count = sm.increment_qa_retry(tid)
-        assert count == 2
-        sm.close()
-
-
-def test_closed_at_timestamp():
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        tid = sm.register_task("tasks/backlog/06-test.md")
-        sm.update_state(tid, TaskState.CLOSED)
-        task = sm.get_task(tid)
-        assert task["closed_at"] is not None
-        assert task["closed_at"] > 0
-        sm.close()
-
-
-def test_get_active_tasks():
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        sm.register_task("tasks/backlog/07a.md")
-        tid2 = sm.register_task("tasks/backlog/07b.md")
-        sm.update_state(tid2, TaskState.IMPLEMENTING)
-        active = sm.get_active_tasks()
-        assert len(active) == 1
-        assert active[0]["task_file"] == "tasks/backlog/07b.md"
-        sm.close()
-
-
-def test_get_tasks_in_state():
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        t1 = sm.register_task("tasks/backlog/08a.md")
-        t2 = sm.register_task("tasks/backlog/08b.md")
-        sm.update_state(t1, TaskState.QA)
-        sm.update_state(t2, TaskState.QA)
-        qa_tasks = sm.get_tasks_in_state(TaskState.QA)
-        assert len(qa_tasks) == 2
-        sm.close()
-
-
-def test_todos():
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        tid = sm.register_task("tasks/backlog/09-test.md")
-        todo_id = sm.add_todo(tid, "Write tests")
-        assert todo_id > 0
-        pending = sm.get_pending_todos(tid)
-        assert len(pending) == 1
-        sm.update_todo_status(todo_id, "done")
-        pending = sm.get_pending_todos(tid)
-        assert len(pending) == 0
-        sm.close()
-
-
-def test_register_task_idempotent():
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        t1 = sm.register_task("tasks/backlog/10-test.md")
-        t2 = sm.register_task("tasks/backlog/10-test.md")
-        assert t1 == t2  # same file = same task
-        sm.close()
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = failed = 0
-    for t in tests:
-        try:
-            t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            print(f"  FAIL: {t.__name__}: {e}")
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
diff --git a/loop-engine/test_trigger_entry.py b/loop-engine/test_trigger_entry.py
deleted file mode 100644
index f076f3a..0000000
--- a/loop-engine/test_trigger_entry.py
+++ /dev/null
@@ -1,240 +0,0 @@
-"""Tests for Task Entry Trigger Gate — decoupled intake mechanism.
-
-Verifies:
-1. New task ingestion under trigger_mode="telegram_button" sets PENDING_TRIGGER.
-2. trigger_task() transitions to PLANNING and starts processing.
-3. Fresh file re-read captures edits after initial ingestion.
-4. Telegram /run command triggers task.
-5. Legacy trigger_mode="auto" immediately starts processing.
-6. CLI --run argument triggers targeted task.
-"""
-import asyncio
-import os
-import sys
-import tempfile
-from pathlib import Path
-from unittest.mock import AsyncMock, MagicMock, patch
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from models import LoopEngineConfig, TaskState
-from state import StateMachine
-from watcher import BacklogHandler
-
-
-def _make_config(**overrides) -> LoopEngineConfig:
-    """Create a LoopEngineConfig with test defaults."""
-    defaults = {
-        "approval": {"chat_id": -100123456},
-        "trigger_mode": "telegram_button",
-        "auto_start_on_boot": False,
-    }
-    defaults.update(overrides)
-    return LoopEngineConfig(**defaults)
-
-
-# --- Test 1: New task ingestion under telegram_button sets PENDING_TRIGGER ---
-
-def test_trigger_mode_telegram_button_sets_pending():
-    """New task detected with trigger_mode='telegram_button' → PENDING_TRIGGER."""
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        config = _make_config(trigger_mode="telegram_button")
-
-        # Simulate watcher registering a task
-        tid = sm.register_task("tasks/backlog/99-test-trigger.md", TaskState.PENDING_TRIGGER)
-        task = sm.get_task(tid)
-
-        assert task["state"] == "pending_trigger"
-        assert task["task_file"] == "tasks/backlog/99-test-trigger.md"
-        sm.close()
-
-
-# --- Test 2: trigger_task() transitions PENDING_TRIGGER → PLANNING ---
-
-def test_trigger_task_transitions_to_planning():
-    """Invoking trigger_task(id) transitions PENDING_TRIGGER → PLANNING."""
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        tid = sm.register_task("tasks/backlog/99-test-trigger.md", TaskState.PENDING_TRIGGER)
-
-        # Simulate trigger_task transition (without launching process_task)
-        sm.update_state(tid, TaskState.PLANNING)
-        task = sm.get_task(tid)
-
-        assert task["state"] == "planning"
-        sm.close()
-
-
-# --- Test 3: Fresh file re-read captures edits ---
-
-def test_fresh_read_captures_edits():
-    """After ingestion, re-reading the file captures manual edits."""
-    with tempfile.TemporaryDirectory() as tmp:
-        task_file = Path(tmp) / "99-test-trigger.md"
-        task_file.write_text("# Original content\n")
-
-        # Initial read
-        content_v1 = task_file.read_text()
-        assert "Original" in content_v1
-
-        # Simulate admin edit
-        task_file.write_text("# Updated content\n**Status:** refined\n")
-
-        # Fresh read captures changes
-        content_v2 = task_file.read_text()
-        assert "Updated" in content_v2
-        assert "refined" in content_v2
-        assert "Original" not in content_v2
-
-
-# --- Test 4: get_pending_trigger_tasks returns correct tasks ---
-
-def test_get_pending_trigger_tasks():
-    """get_pending_trigger_tasks() returns only PENDING_TRIGGER tasks."""
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        t1 = sm.register_task("tasks/backlog/01-a.md", TaskState.PENDING_TRIGGER)
-        t2 = sm.register_task("tasks/backlog/02-b.md", TaskState.BACKLOG)
-        t3 = sm.register_task("tasks/backlog/03-c.md", TaskState.PENDING_TRIGGER)
-
-        pending = sm.get_pending_trigger_tasks()
-        assert len(pending) == 2
-        states = {t["task_id"] for t in pending}
-        assert t1 in states
-        assert t3 in states
-        assert t2 not in states
-        sm.close()
-
-
-# --- Test 5: Legacy trigger_mode="auto" registers as BACKLOG ---
-
-def test_trigger_mode_auto_registers_backlog():
-    """With trigger_mode='auto', tasks register as BACKLOG (legacy behavior)."""
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        config = _make_config(trigger_mode="auto")
-
-        # Simulate auto mode registration
-        tid = sm.register_task("tasks/backlog/99-test-auto.md", TaskState.BACKLOG)
-        task = sm.get_task(tid)
-
-        assert task["state"] == "backlog"
-        # auto mode should NOT have pending_trigger tasks
-        pending = sm.get_pending_trigger_tasks()
-        assert len(pending) == 0
-        sm.close()
-
-
-# --- Test 6: Config defaults ---
-
-def test_config_defaults():
-    """LoopEngineConfig defaults: trigger_mode='telegram_button', auto_start_on_boot=False."""
-    config = _make_config()
-    assert config.trigger_mode == "telegram_button"
-    assert config.auto_start_on_boot is False
-
-
-def test_config_auto_mode():
-    """LoopEngineConfig auto mode: trigger_mode='auto', auto_start_on_boot=True."""
-    config = _make_config(trigger_mode="auto", auto_start_on_boot=True)
-    assert config.trigger_mode == "auto"
-    assert config.auto_start_on_boot is True
-
-
-# --- Test 7: State transitions PENDING_TRIGGER → CRASHED/ABORTED ---
-
-def test_pending_trigger_can_crash():
-    """PENDING_TRIGGER → CRASHED transition works."""
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        tid = sm.register_task("tasks/backlog/99-crash.md", TaskState.PENDING_TRIGGER)
-        sm.update_state(tid, TaskState.CRASHED)
-        task = sm.get_task(tid)
-        assert task["state"] == "crashed"
-        sm.close()
-
-
-def test_pending_trigger_can_abort():
-    """PENDING_TRIGGER → ABORTED transition works."""
-    with tempfile.TemporaryDirectory() as tmp:
-        sm = StateMachine(os.path.join(tmp, "test.db"))
-        tid = sm.register_task("tasks/backlog/99-abort.md", TaskState.PENDING_TRIGGER)
-        sm.update_state(tid, TaskState.ABORTED)
-        task = sm.get_task(tid)
-        assert task["state"] == "aborted"
-        sm.close()
-
-
-# --- Test 10: Thread-safe dispatch from watchdog background thread ---
-
-def test_watcher_thread_safe_dispatch():
-    """BacklogHandler.on_created runs from a background thread without RuntimeError.
-
-    Regression test: the original code called asyncio.get_event_loop().create_task()
-    from watchdog's background thread, which has no running event loop and would
-    raise RuntimeError. The fix removes that call and always dispatches via the
-    on_task_detected callback, letting the daemon handle async scheduling.
-
-    Note: SQLite connections are thread-bound, so StateMachine must be created
-    inside the same thread that calls on_created.
-    """
-    import threading
-    from unittest.mock import MagicMock
-    from watchdog.events import FileCreatedEvent
-
-    with tempfile.TemporaryDirectory() as tmp:
-        config = _make_config(trigger_mode="telegram_button")
-
-        # Create a tasks/backlog dir and a task file inside it
-        backlog_dir = Path(tmp) / "tasks" / "backlog"
-        backlog_dir.mkdir(parents=True)
-        task_file = backlog_dir / "01-thread-test.md"
-        task_file.write_text("# Task 1: Thread Test\n**Source:** telegram\n**Type:** improvement\n")
-
-        # Track callback invocations and errors from background thread
-        callback_invocations = []
-        errors = []
-
-        def on_task_detected(task_id, task_file_path):
-            callback_invocations.append((task_id, task_file_path))
-
-        def run_in_thread():
-            try:
-                # StateMachine must be created in the same thread (SQLite thread-bound)
-                sm = StateMachine(os.path.join(tmp, "test.db"))
-                gateway_mock = MagicMock()
-                handler = BacklogHandler(sm, config, gateway_mock, on_task_detected)
-
-                # Create a FileCreatedEvent for the task file
-                event = FileCreatedEvent(str(task_file))
-                handler.on_created(event)
-                sm.close()
-            except Exception as e:
-                errors.append(e)
-
-        thread = threading.Thread(target=run_in_thread)
-        thread.start()
-        thread.join(timeout=5)
-
-        # Verify: no RuntimeError, callback was invoked
-        assert len(errors) == 0, f"Background thread raised: {errors}"
-        assert len(callback_invocations) == 1, \
-            f"Expected 1 callback, got {len(callback_invocations)}"
-        assert callback_invocations[0][0] == 1  # task_id
-        assert "thread-test" in callback_invocations[0][1]
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = failed = 0
-    for t in tests:
-        try:
-            t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            print(f"  FAIL: {t.__name__}: {e}")
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
diff --git a/loop-engine/test_verifier.py b/loop-engine/test_verifier.py
deleted file mode 100644
index 810de01..0000000
--- a/loop-engine/test_verifier.py
+++ /dev/null
@@ -1,501 +0,0 @@
-"""Tests for verifier.py — Polyglot Verification & Multi-Toolchain Runner (Task 134)."""
-import os
-import sys
-import tempfile
-import asyncio
-from pathlib import Path
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-from models import StackProfileConfig, StackToolchainConfig
-from stacks import StackProfile
-from verifier import CommandResult, ToolchainResult, ToolchainRunner
-
-
-# ---------------------------------------------------------------------------
-# Helpers
-# ---------------------------------------------------------------------------
-
-def make_profile(lint_cmd, build_cmd, test_cmd, name="test-stack") -> StackProfile:
-    cfg = StackProfileConfig(
-        name=name,
-        display_name=f"Test {name}",
-        toolchain=StackToolchainConfig(
-            lint_cmd=lint_cmd, build_cmd=build_cmd, test_cmd=test_cmd
-        ),
-    )
-    return StackProfile(cfg)
-
-
-# ---------------------------------------------------------------------------
-# Dataclass contracts
-# ---------------------------------------------------------------------------
-
-def test_command_result_defaults():
-    r = CommandResult(command="echo hi", cmd_type="lint", passed=True)
-    assert r.command == "echo hi"
-    assert r.cmd_type == "lint"
-    assert r.passed is True
-    assert r.skipped is False
-    assert r.returncode is None
-    assert r.stdout == ""
-    assert r.stderr == ""
-    assert r.duration_seconds == 0.0
-
-
-def test_toolchain_result_defaults():
-    r = ToolchainResult(passed=True)
-    assert r.passed is True
-    assert r.commands == []
-    assert r.summary == ""
-    assert r.report_md == ""
-
-
-def test_toolchain_runner_init_defaults():
-    runner = ToolchainRunner()
-    assert runner.timeout_per_command == 120.0
-    assert str(runner.evidence_base_dir) == "loop-engine/evidence"
-
-
-def test_toolchain_runner_custom_init():
-    runner = ToolchainRunner(timeout_per_command=30.0, evidence_base_dir="/tmp/ev")
-    assert runner.timeout_per_command == 30.0
-    assert runner.evidence_base_dir == Path("/tmp/ev")
-
-
-# ---------------------------------------------------------------------------
-# Full toolchain success
-# ---------------------------------------------------------------------------
-
-def test_toolchain_full_success():
-    profile = make_profile("echo lint", "echo build", "echo test")
-    runner = ToolchainRunner(timeout_per_command=5.0)
-    # Use temp evidence dir to avoid polluting repo
-    with tempfile.TemporaryDirectory() as tmp:
-        runner.evidence_base_dir = Path(tmp)
-        result = runner.run_sync(profile, task_id=999)
-        assert result.passed is True
-        assert len(result.commands) == 3
-        # Order lint, build, test
-        assert result.commands[0].cmd_type == "lint"
-        assert result.commands[1].cmd_type == "build"
-        assert result.commands[2].cmd_type == "test"
-        for c in result.commands:
-            assert c.passed is True
-            assert c.skipped is False
-            assert c.returncode == 0
-        assert "PASSED" in result.summary
-        assert "lint: PASSED" in result.summary
-        assert "build: PASSED" in result.summary
-        assert "test: PASSED" in result.summary
-        assert "PASSED" in result.report_md
-        # Evidence files
-        assert (Path(tmp) / "999" / "toolchain_report.md").exists()
-        assert (Path(tmp) / "999" / "toolchain_result.txt").read_text() == "PASSED"
-
-
-def test_toolchain_success_no_task_id_no_evidence():
-    profile = make_profile("echo lint", None, "echo test")
-    with tempfile.TemporaryDirectory() as tmp:
-        runner = ToolchainRunner(timeout_per_command=5.0, evidence_base_dir=tmp)
-        result = runner.run_sync(profile, task_id=None)
-        assert result.passed is True
-        # No task_id → no evidence dir created for task
-        assert not (Path(tmp) / "toolchain_report.md").exists()
-
-
-# ---------------------------------------------------------------------------
-# Failure cases — lint / build / test non-zero
-# ---------------------------------------------------------------------------
-
-def test_toolchain_failure_on_lint():
-    profile = make_profile("false", "echo build", "echo test")
-    runner = ToolchainRunner(timeout_per_command=5.0)
-    with tempfile.TemporaryDirectory() as tmp:
-        runner.evidence_base_dir = Path(tmp)
-        result = runner.run_sync(profile, task_id=1)
-        assert result.passed is False
-        # lint failed
-        lint_res = [c for c in result.commands if c.cmd_type == "lint"][0]
-        assert lint_res.passed is False
-        assert lint_res.returncode != 0
-        # build and test still executed? Runner is sequential; all run even if one fails (collect all)
-        assert len(result.commands) == 3
-        assert "FAILED" in result.summary
-        assert "lint: FAILED" in result.summary
-        # Report contains failure section
-        assert "Failures" in result.report_md
-        assert "FAILED" in (Path(tmp) / "1" / "toolchain_result.txt").read_text()
-
-
-def test_toolchain_failure_on_build():
-    profile = make_profile("echo lint", "false", "echo test")
-    runner = ToolchainRunner(timeout_per_command=5.0)
-    with tempfile.TemporaryDirectory() as tmp:
-        runner.evidence_base_dir = Path(tmp)
-        result = runner.run_sync(profile)
-        assert result.passed is False
-        build_res = [c for c in result.commands if c.cmd_type == "build"][0]
-        assert build_res.passed is False
-
-
-def test_toolchain_failure_on_test():
-    profile = make_profile("echo lint", "echo build", "false")
-    runner = ToolchainRunner(timeout_per_command=5.0)
-    result = runner.run_sync(profile)
-    assert result.passed is False
-    test_res = [c for c in result.commands if c.cmd_type == "test"][0]
-    assert test_res.passed is False
-
-
-def test_toolchain_failure_captures_stdout_stderr():
-    # Use sh that writes to stderr and exits 1
-    profile = make_profile("sh -c 'echo out_msg; echo err_msg >&2; exit 1'", None, None)
-    runner = ToolchainRunner(timeout_per_command=5.0)
-    result = runner.run_sync(profile)
-    lint_res = [c for c in result.commands if c.cmd_type == "lint"][0]
-    assert lint_res.passed is False
-    assert "err_msg" in lint_res.stderr or "err_msg" in lint_res.stdout or "err_msg" in result.report_md
-    assert "out_msg" in lint_res.stdout or "out_msg" in result.report_md
-
-
-# ---------------------------------------------------------------------------
-# Timeout and kill handling
-# ---------------------------------------------------------------------------
-
-def test_toolchain_timeout():
-    profile = make_profile("sleep 2", None, None)
-    # Very short timeout to trigger kill
-    runner = ToolchainRunner(timeout_per_command=0.3)
-    with tempfile.TemporaryDirectory() as tmp:
-        runner.evidence_base_dir = Path(tmp)
-        result = runner.run_sync(profile, task_id=2)
-        assert result.passed is False
-        lint_res = [c for c in result.commands if c.cmd_type == "lint"][0]
-        assert lint_res.passed is False
-        assert "timeout" in lint_res.stderr.lower()
-        assert lint_res.duration_seconds >= 0.2
-        assert "FAILED" in result.report_md
-
-
-def test_toolchain_timeout_then_success_subsequent():
-    # First command times out, second is skipped? Actually second is None so skipped pass, but third should still run
-    profile = make_profile("sleep 2", None, "echo test")
-    runner = ToolchainRunner(timeout_per_command=0.3)
-    result = runner.run_sync(profile)
-    assert result.passed is False
-    # lint failed due timeout
-    assert result.commands[0].passed is False
-    # build skipped (None)
-    assert result.commands[1].skipped is True
-    # test should still be executed and pass
-    assert result.commands[2].passed is True
-
-
-# ---------------------------------------------------------------------------
-# Null / empty skip (generic.yaml)
-# ---------------------------------------------------------------------------
-
-def test_generic_null_toolchain_all_skipped():
-    cfg = StackProfileConfig(name="generic", display_name="Generic")
-    profile = StackProfile(cfg)
-    runner = ToolchainRunner(timeout_per_command=5.0)
-    result = runner.run_sync(profile)
-    assert result.passed is True
-    assert len(result.commands) == 3
-    for c in result.commands:
-        assert c.skipped is True
-        assert c.passed is True
-        assert c.command == "none"
-    assert "SKIPPED" in result.summary
-    assert "PASSED" in result.summary  # overall PASSED
-
-
-def test_whitespace_only_skipped():
-    profile = make_profile("   ", "  \t ", None)
-    runner = ToolchainRunner(timeout_per_command=5.0)
-    result = runner.run_sync(profile)
-    assert result.passed is True
-    assert result.commands[0].skipped is True
-    assert result.commands[1].skipped is True
-    assert result.commands[2].skipped is True
-
-
-def test_mixed_null_and_real():
-    profile = make_profile(None, "echo build", None)
-    runner = ToolchainRunner(timeout_per_command=5.0)
-    result = runner.run_sync(profile)
-    assert result.passed is True
-    assert result.commands[0].skipped is True
-    assert result.commands[1].passed is True and not result.commands[1].skipped
-    assert result.commands[2].skipped is True
-
-
-# ---------------------------------------------------------------------------
-# Markdown report and evidence persistence
-# ---------------------------------------------------------------------------
-
-def test_report_contains_table_and_summary():
-    profile = make_profile("echo lint", "echo build", "echo test")
-    runner = ToolchainRunner(timeout_per_command=5.0)
-    result = runner.run_sync(profile)
-    # Table header
-    assert "| Type | Command | Result | Duration | Return Code |" in result.report_md
-    assert "lint" in result.report_md
-    assert "build" in result.report_md
-    assert "test" in result.report_md
-    assert "# Toolchain Verification Report" in result.report_md
-    assert "Toolchain PASSED" in result.report_md
-
-
-def test_report_failure_details():
-    profile = make_profile("false", None, None)
-    runner = ToolchainRunner(timeout_per_command=5.0)
-    result = runner.run_sync(profile)
-    assert "## Failures" in result.report_md
-    assert "false" in result.report_md
-
-
-def test_evidence_persistence_files():
-    profile = make_profile("echo lint", "echo build", "echo test")
-    with tempfile.TemporaryDirectory() as tmp:
-        runner = ToolchainRunner(timeout_per_command=5.0, evidence_base_dir=tmp)
-        result = runner.run_sync(profile, task_id=42)
-        report_path = Path(tmp) / "42" / "toolchain_report.md"
-        result_path = Path(tmp) / "42" / "toolchain_result.txt"
-        assert report_path.exists()
-        assert result_path.exists()
-        assert report_path.read_text() == result.report_md
-        assert result_path.read_text() == "PASSED"
-        # Failure case writes FAILED
-        profile_fail = make_profile("false", None, None)
-        result2 = runner.run_sync(profile_fail, task_id=43)
-        assert (Path(tmp) / "43" / "toolchain_result.txt").read_text() == "FAILED"
-
-
-def test_evidence_dir_created_even_if_missing():
-    with tempfile.TemporaryDirectory() as tmp:
-        # Use nested non-existing dir
-        nested = Path(tmp) / "a" / "b" / "evidence"
-        runner = ToolchainRunner(evidence_base_dir=str(nested))
-        profile = make_profile("echo hi", None, None)
-        result = runner.run_sync(profile, task_id=7)
-        assert (nested / "7" / "toolchain_report.md").exists()
-
-
-# ---------------------------------------------------------------------------
-# Async run direct (not via run_sync)
-# ---------------------------------------------------------------------------
-
-def test_async_run_direct():
-    async def _inner():
-        profile = make_profile("echo lint", None, "echo test")
-        runner = ToolchainRunner(timeout_per_command=5.0)
-        result = await runner.run(profile)
-        assert result.passed is True
-        assert len(result.commands) == 3
-    asyncio.run(_inner())
-
-
-def test_profile_without_toolchain_attr():
-    class FakeProfile:
-        pass
-    runner = ToolchainRunner(timeout_per_command=5.0)
-    result = runner.run_sync(FakeProfile())  # type: ignore
-    assert result.passed is True
-    # Should treat as generic → all skipped
-    for c in result.commands:
-        assert c.skipped is True
-
-
-# ---------------------------------------------------------------------------
-# Daemon fail-fast integration
-# ---------------------------------------------------------------------------
-
-def test_daemon_fail_fast_bypasses_qa_on_toolchain_failure():
-    # Mock state, qa, executor to test _execute_and_qa integration
-    import daemon
-    from unittest.mock import MagicMock, AsyncMock
-
-    # Create a failing toolchain profile
-    profile = make_profile("false", None, None)
-
-    # Mock state
-    mock_state = MagicMock()
-    mock_state.set_qa_feedback = MagicMock()
-    mock_state.update_state = MagicMock()
-
-    # Mock QA that should NOT be called on failure
-    mock_qa = MagicMock()
-    mock_qa.config = MagicMock()
-    mock_qa.config.evidence_dir = tempfile.mkdtemp()
-    mock_qa.evidence_dir = Path(mock_qa.config.evidence_dir)
-    mock_qa.run_qa = MagicMock(return_value={"result": "PASSED", "report": "QA_PASSED"})
-
-    # Mock executor returning complete with dummy diff file
-    mock_executor = MagicMock()
-    async def fake_execute(*args, **kwargs):
-        return {"status": "complete"}
-    mock_executor.execute = fake_execute
-
-    # Create temp task file with diff markers
-    with tempfile.TemporaryDirectory() as tmp:
-        task_file = Path(tmp) / "task.md"
-        task_file.write_text("content\n<!-- BEGIN_GIT_DIFF -->\ndiff content\n<!-- END_GIT_DIFF -->", encoding="utf-8")
-        # Need to monkeypatch daemon.ToolchainRunner to use our failing profile? Instead directly test via daemon._execute_and_qa with stack_profile
-        async def run_test():
-            result = await daemon._execute_and_qa(
-                task_id=99,
-                task_file=str(task_file),
-                task_content="task content",
-                task_path=task_file,
-                state=mock_state,
-                executor=mock_executor,
-                qa=mock_qa,
-                stack_profile=profile,
-            )
-            return result
-
-        result = asyncio.run(run_test())
-        # Should be FAILED due to toolchain, not PASSED
-        assert result is not None
-        assert result["result"] == "FAILED"
-        assert "toolchain" in result["report"].lower() or "FAILED" in result["report"]
-        # qa.run_qa should NOT have been called
-        mock_qa.run_qa.assert_not_called()
-        # state.set_qa_feedback should have been called with report_md
-        mock_state.set_qa_feedback.assert_called_once()
-        # evidence dir file should exist
-        assert (Path(mock_qa.config.evidence_dir) / "99" / "toolchain_report.md").exists()
-
-
-def test_daemon_success_forwards_to_qa():
-    import daemon
-    from unittest.mock import MagicMock
-
-    profile = make_profile("echo lint", "echo build", "echo test")
-    mock_state = MagicMock()
-    mock_state.set_qa_feedback = MagicMock()
-    mock_state.update_state = MagicMock()
-    mock_qa = MagicMock()
-    mock_qa.config = MagicMock()
-    mock_qa.config.evidence_dir = tempfile.mkdtemp()
-    mock_qa.evidence_dir = Path(mock_qa.config.evidence_dir)
-    # Capture toolchain_evidence param
-    captured = {}
-    def fake_run_qa(task_id, task_content, diff, toolchain_evidence=""):
-        captured["toolchain_evidence"] = toolchain_evidence
-        return {"result": "PASSED", "report": "QA_PASSED", "evidence_dir": str(mock_qa.evidence_dir / str(task_id))}
-    mock_qa.run_qa = fake_run_qa
-
-    mock_executor = MagicMock()
-    async def fake_execute(*args, **kwargs):
-        return {"status": "complete"}
-    mock_executor.execute = fake_execute
-
-    with tempfile.TemporaryDirectory() as tmp:
-        task_file = Path(tmp) / "task.md"
-        task_file.write_text("x\n<!-- BEGIN_GIT_DIFF -->\ndiff\n<!-- END_GIT_DIFF -->", encoding="utf-8")
-        async def run_test():
-            return await daemon._execute_and_qa(
-                task_id=100,
-                task_file=str(task_file),
-                task_content="task",
-                task_path=task_file,
-                state=mock_state,
-                executor=mock_executor,
-                qa=mock_qa,
-                stack_profile=profile,
-            )
-        result = asyncio.run(run_test())
-        assert result["result"] == "PASSED"
-        # toolchain_evidence should have been forwarded
-        assert "toolchain" in captured["toolchain_evidence"].lower() or "PASSED" in captured["toolchain_evidence"]
-        # set_qa_feedback should NOT be called on success
-        mock_state.set_qa_feedback.assert_not_called()
-
-
-def test_daemon_generic_skips_and_passes_to_qa():
-    import daemon
-    from unittest.mock import MagicMock
-    cfg = StackProfileConfig(name="generic", display_name="Generic")
-    profile = StackProfile(cfg)
-    mock_state = MagicMock()
-    mock_state.set_qa_feedback = MagicMock()
-    mock_state.update_state = MagicMock()
-    mock_qa = MagicMock()
-    mock_qa.config = MagicMock()
-    mock_qa.config.evidence_dir = tempfile.mkdtemp()
-    mock_qa.evidence_dir = Path(mock_qa.config.evidence_dir)
-    mock_qa.run_qa = MagicMock(return_value={"result": "PASSED", "report": "QA_PASSED", "evidence_dir": "ev"})
-    mock_executor = MagicMock()
-    async def fake_execute(*args, **kwargs):
-        return {"status": "complete"}
-    mock_executor.execute = fake_execute
-    with tempfile.TemporaryDirectory() as tmp:
-        task_file = Path(tmp) / "t.md"
-        task_file.write_text("c\n<!-- BEGIN_GIT_DIFF -->\ndiff\n<!-- END_GIT_DIFF -->")
-        async def run_test():
-            return await daemon._execute_and_qa(101, str(task_file), "c", task_file, mock_state, mock_executor, mock_qa, stack_profile=profile)
-        result = asyncio.run(run_test())
-        assert result["result"] == "PASSED"
-        mock_qa.run_qa.assert_called_once()
-
-
-def test_router_includes_toolchain_evidence():
-    from models import LoopEngineConfig
-    from router import LLMRouter
-    cfg = LoopEngineConfig(approval={"chat_id": 0})
-    router = LLMRouter(cfg, workspace_root=".")
-    routing = router.route_qa("task content", "diff content", toolchain_evidence="Toolchain PASSED | lint: SKIPPED")
-    assert "Toolchain PASSED" in routing["user"]
-    assert "diff content" in routing["user"]
-    # Without evidence, not included
-    routing2 = router.route_qa("task", "diff")
-    assert "Toolchain" not in routing2["user"]
-
-
-def test_qa_engine_forwards_toolchain_evidence():
-    from models import LoopEngineConfig
-    from state import StateMachine
-    from router import LLMRouter
-    from qa_engine import QAEngine
-    cfg = LoopEngineConfig(approval={"chat_id": 0}, evidence_dir=tempfile.mkdtemp())
-    state = StateMachine(db_path=os.path.join(tempfile.mkdtemp(), "db"))
-    router = LLMRouter(cfg, workspace_root=".")
-
-    # Patch router.call_llm to capture routing and return PASSED
-    captured = {}
-    orig_call = router.call_llm
-    def fake_call(routing):
-        captured["user"] = routing["user"]
-        return "QA_PASSED everything ok"
-    router.call_llm = fake_call
-
-    qa = QAEngine(cfg, state, router)
-    result = qa.run_qa(1, "task", "diff", toolchain_evidence="Toolchain PASSED | lint: PASSED")
-    assert result["result"] == "PASSED"
-    assert "Toolchain PASSED" in captured["user"]
-    # Also test empty evidence still works
-    result2 = qa.run_qa(2, "task", "diff")
-    assert result2["result"] == "PASSED"
-    router.call_llm = orig_call
-    state.close()
-
-
-if __name__ == "__main__":
-    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
-    passed = 0
-    failed = 0
-    for t in tests:
-        try:
-            t()
-            print(f"  PASS: {t.__name__}")
-            passed += 1
-        except Exception as e:
-            import traceback
-            print(f"  FAIL: {t.__name__}: {e}")
-            traceback.print_exc()
-            failed += 1
-    print(f"\n{passed} passed, {failed} failed")
-    sys.exit(1 if failed else 0)
diff --git a/loop-engine/test_vertical_slice.py b/loop-engine/test_vertical_slice.py
deleted file mode 100644
index 6535dd7..0000000
--- a/loop-engine/test_vertical_slice.py
+++ /dev/null
@@ -1,74 +0,0 @@
-"""Phase C Capstone: Monorepo Multi-Platform Vertical Slice (Task 145).
-
-Hermetic E2E following test_polyglot_smoke.py:
-isolated monorepo under tmp_path with TypeScript contract, React web,
-Kotlin Android client, and node-ts + kotlin-android stack definitions.
-Simulates contract update -> propagation -> dual toolchain verification
--> simulated QA -> closure in one unified pipeline run.
-"""
-import json
-import os
-import subprocess
-import sys
-from pathlib import Path
-
-sys.path.insert(0, os.path.dirname(__file__))
-
-
-def _write(path: Path, text: str) -> None:
-    path.parent.mkdir(parents=True, exist_ok=True)
-    path.write_text(text, encoding="utf-8")
-
-
-def _run(cmd: list[str], cwd: Path) -> None:
-    subprocess.run(cmd, cwd=str(cwd), check=True, capture_output=True)
-
-
-def test_vertical_slice_multi_platform_e2e(tmp_path):
-    root = tmp_path / "monorepo"
-    # 1. Contract: shared TypeScript schema
-    _write(root / "packages/shared-schema/index.ts",
-           "export interface User { id: string; name: string }\n")
-    _write(root / "packages/shared-schema/package.json",
-           json.dumps({"name": "@repo/shared-schema", "version": "0.1.0"}))
-    # 2. Web Admin (React/TS)
-    _write(root / "apps/web/package.json",
-           json.dumps({"name": "web", "dependencies": {"@repo/shared-schema": "*"}}))
-    _write(root / "apps/web/src/App.tsx",
-           "import { User } from '@repo/shared-schema';\nexport const App = (_: User) => null;\n")
-    # 3. Mobile Android (Kotlin)
-    _write(root / "apps/mobile/build.gradle.kts",
-           'plugins { id("com.android.application") }\nandroid { namespace = "com.example.app" }\n')
-    _write(root / "apps/mobile/src/Main.kt",
-           "data class User(val id: String, val name: String)\n")
-    # 4. Stack definitions
-    stacks = {
-        "node-ts": {"test_cmd": "true", "build_cmd": "true"},
-        "kotlin-android": {"test_cmd": "true", "build_cmd": "true"},
-    }
-    _write(root / "stacks.json", json.dumps(stacks))
-
-    # 5. Contract update -> propagation (simulated: bump schema, sync consumers)
-    _write(root / "packages/shared-schema/index.ts",
-           "export interface User { id: string; name: string; email: string }\n")
-    web_app = (root / "apps/web/src/App.tsx").read_text(encoding="utf-8")
-    assert "User" in web_app
-    mobile = (root / "apps/mobile/src/Main.kt").read_text(encoding="utf-8")
-    assert "User" in mobile
-
-    # 6. Dual toolchain verification (portable no-ops, hermetic)
-    for stack in ("node-ts", "kotlin-android"):
-        assert stacks[stack]["build_cmd"] == "true"
-        assert stacks[stack]["test_cmd"] == "true"
-        _run(["true"], cwd=root)
-
-    # 7. Simulated QA + closure markers
-    _write(root / "QA_APPROVED", "qa:pass\n")
-    _write(root / "CLOSED", "closed\n")
-    assert (root / "QA_APPROVED").exists()
-    assert (root / "CLOSED").exists()
-
-    # 8. Prove simultaneous TS + Kotlin artifacts present in one run
-    assert (root / "packages/shared-schema/index.ts").exists()
-    assert (root / "apps/web/package.json").exists()
-    assert (root / "apps/mobile/build.gradle.kts").exists()
diff --git a/loop-engine/uv.lock b/loop-engine/uv.lock
deleted file mode 100644
index f6b9129..0000000
--- a/loop-engine/uv.lock
+++ /dev/null
@@ -1,1775 +0,0 @@
-version = 1
-revision = 3
-requires-python = ">=3.12"
-resolution-markers = [
-    "python_full_version >= '3.14'",
-    "python_full_version < '3.14'",
-]
-
-[[package]]
-name = "aiohappyeyeballs"
-version = "2.7.1"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/ce/f4/eec0465c2f67b2664688d0240b3212d5196fd89e741df67ddb81f8d35658/aiohappyeyeballs-2.7.1.tar.gz", hash = "sha256:065665c041c42a5938ed220bdcd7230f22527fbec085e1853d2402c8a3615d9d", size = 24757, upload-time = "2026-07-01T17:11:55.501Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/71/43/1947f06babed6b3f1d7f38b0c767f52df66bfb2bc10b468c4a7de9eceff2/aiohappyeyeballs-2.7.1-py3-none-any.whl", hash = "sha256:9243213661e29250eb41368e5daa826fc017156c3b8a11440826b2e3ed376472", size = 15038, upload-time = "2026-07-01T17:11:54.055Z" },
-]
-
-[[package]]
-name = "aiohttp"
-version = "3.14.3"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "aiohappyeyeballs" },
-    { name = "aiosignal" },
-    { name = "attrs" },
-    { name = "frozenlist" },
-    { name = "multidict" },
-    { name = "propcache" },
-    { name = "typing-extensions", marker = "python_full_version < '3.13'" },
-    { name = "yarl" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/58/d9/22ce5786ac0c1653ae8b6c23bded02c1686d11f0dbb45b31ce128e0df985/aiohttp-3.14.3.tar.gz", hash = "sha256:9491196535a88924a60afd5b5f434b5b203b6cc616250878dbdb223a8f7844bc", size = 7971213, upload-time = "2026-07-23T01:57:27.037Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/18/d4/eb96299230e20acf2efae207cb8d69051f1f68e357e5ea5e479bf6fb097a/aiohttp-3.14.3-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:39aded8c7f3b935b54aab1d8d73c70ec0ee2d3ec3b943e0e86611bc150ba47f5", size = 754690, upload-time = "2026-07-23T01:53:47.332Z" },
-    { url = "https://files.pythonhosted.org/packages/88/11/e7a70a209eb9a067c0d3212b518a0134e3484f5178c7533878b6b514d469/aiohttp-3.14.3-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:5bcb6ff3fdab1258a192679ff1a05d44f59626430aa05cd1a9d2447423599228", size = 509484, upload-time = "2026-07-23T01:53:51.159Z" },
-    { url = "https://files.pythonhosted.org/packages/30/07/4bbc222cc8dbe31d4c3e8a5baad2286e4d42026ac0c570027b89afce6344/aiohttp-3.14.3-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:617105e2c3018ee38d0c8ce5ee3c84f621a6d8b9f723202aacaff28449ca91ee", size = 511949, upload-time = "2026-07-23T01:53:55.083Z" },
-    { url = "https://files.pythonhosted.org/packages/54/b9/42e74c46b7b7c794b995bbc1f573fb48950c38b19d8600c62a6804ee2d67/aiohttp-3.14.3-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:f631fe87a6f30df5fbe6d79640b25e4cffb38c31c7fb6f10871517b84b0f8c1a", size = 1765282, upload-time = "2026-07-23T01:53:59.662Z" },
-    { url = "https://files.pythonhosted.org/packages/6b/ed/62bc4d74363ad346d518e0720363a949f63e2e23439a79eb5813d4d29bb3/aiohttp-3.14.3-cp312-cp312-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:a94dbaae5ae27bd849c93570669bff91e0510f33a80805738e3de72a7be0447b", size = 1741511, upload-time = "2026-07-23T01:54:04.063Z" },
-    { url = "https://files.pythonhosted.org/packages/d0/9f/181e8a8bc79e47d13c7fc4540bd7a3b729d9505609c61f392a8dd2fbfe55/aiohttp-3.14.3-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:8f2f1c4c032c7cedd7d8da6f54c97b70266c6570c3108d3fdffee7188bb70529", size = 1810680, upload-time = "2026-07-23T01:54:09.882Z" },
-    { url = "https://files.pythonhosted.org/packages/5c/9a/dec94d6ad694552fe3424e3f1928d7a606a5d9d9433a04e7ecdd9d38ae7f/aiohttp-3.14.3-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:ea05e1f97ceea523942d9b2a7d7c0359d781d683d6b043f5943a602b14da4787", size = 1905646, upload-time = "2026-07-23T01:54:13.475Z" },
-    { url = "https://files.pythonhosted.org/packages/52/b7/7cd31f29d6055bd711ae6e669367fba6f5ae9de463910a793e30556a8db7/aiohttp-3.14.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:543906c127fb1d929b95076db19b83fa2d46751006ff1e23b093aa5ac4d8db42", size = 1792122, upload-time = "2026-07-23T01:54:15.752Z" },
-    { url = "https://files.pythonhosted.org/packages/66/73/10b1ef93afa61f4963c746257b70ced619cf31a4798671de5fdb2608501d/aiohttp-3.14.3-cp312-cp312-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:0a5ff2dfbb9ce645fa5b8ef3e02c6c0b9cc3f6030ff863d0c51fffc50cb5541b", size = 1591127, upload-time = "2026-07-23T01:54:19.489Z" },
-    { url = "https://files.pythonhosted.org/packages/49/ed/3b203fa6de1b338c14acdc06bf6ca9b043b7944f005966958c2ced932cde/aiohttp-3.14.3-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:041badb8f84396357c4d3ad26de6afd7a32b112f43d3c63045c0c8278cfd2043", size = 1725210, upload-time = "2026-07-23T01:54:24.129Z" },
-    { url = "https://files.pythonhosted.org/packages/28/b7/1c2aab8c706436dcc28598452488ac9cd7c409da815237c28c27d58993e6/aiohttp-3.14.3-cp312-cp312-musllinux_1_2_armv7l.whl", hash = "sha256:530125ee1163c4219af35dc3aa1206e541e7b31b6efc1a3f93b70a136f65d427", size = 1764848, upload-time = "2026-07-23T01:54:27.973Z" },
-    { url = "https://files.pythonhosted.org/packages/54/50/94c28f08b131c4bf10984ea2c7a536c9920608bb2d6e7f95642c30cc87b7/aiohttp-3.14.3-cp312-cp312-musllinux_1_2_ppc64le.whl", hash = "sha256:c8653fd547c93a61aadc612007790f5555cdd18946fa48cf45e26d8ea4ea473d", size = 1777102, upload-time = "2026-07-23T01:54:31.775Z" },
-    { url = "https://files.pythonhosted.org/packages/13/d4/e7d09ba7d345fb2d74440fd2fa033c5e079fac05552927705986f41a364f/aiohttp-3.14.3-cp312-cp312-musllinux_1_2_riscv64.whl", hash = "sha256:89176250f686cb9853c0fb7ead90e639e915b84a6f43eedc2a4e7ec21f1037f0", size = 1580205, upload-time = "2026-07-23T01:54:34.518Z" },
-    { url = "https://files.pythonhosted.org/packages/a3/84/072a91d68e1e1eb587985b54baab94221277f877e8ef274fc213a0ceae28/aiohttp-3.14.3-cp312-cp312-musllinux_1_2_s390x.whl", hash = "sha256:3a26434dafe408229ff3403458ca58de24fb51936504decac49ce6755f77e59d", size = 1797219, upload-time = "2026-07-23T01:54:36.995Z" },
-    { url = "https://files.pythonhosted.org/packages/e0/eb/aad34e897e668424d6e995da5dff8a4a09af93363d3392488772957a63aa/aiohttp-3.14.3-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:d1558173930a5a8d3069cee5c92fc91c87c4dbcb099debbb3622053717145a19", size = 1768629, upload-time = "2026-07-23T01:54:40.103Z" },
-    { url = "https://files.pythonhosted.org/packages/b6/2b/6bb88ddba0fecd9122aa3ebcad25996cf6c083a4a7040dbb3a4f97972af6/aiohttp-3.14.3-cp312-cp312-win32.whl", hash = "sha256:16100ad3ab8d649fdfbee87602d9d2dcdca9df0b9eda8a1b5fdc0d41f96da559", size = 451481, upload-time = "2026-07-23T01:54:42.547Z" },
-    { url = "https://files.pythonhosted.org/packages/76/9b/f2f8f108da17ecef2cc3efc424e8b7ad3782b1a8360f7b8eae8ced84f6ea/aiohttp-3.14.3-cp312-cp312-win_amd64.whl", hash = "sha256:33a2d7c28d33797a2e99923dffa63f83d908a19b6bf26cfe80fa790aa5e1a75a", size = 476845, upload-time = "2026-07-23T01:54:44.853Z" },
-    { url = "https://files.pythonhosted.org/packages/3e/44/28dac80a8941b604f4da10ce21097614ca1bf905ce93dca28d8d7de9c1e7/aiohttp-3.14.3-cp312-cp312-win_arm64.whl", hash = "sha256:362a3fd481769cac1a824514bcd86fda51c65e8fe6e051099e008fddde6db17c", size = 448050, upload-time = "2026-07-23T01:54:47.087Z" },
-    { url = "https://files.pythonhosted.org/packages/57/be/5afd201cc0ab139029aadb75392efe85a293403d9dd3a3226161c21ce00c/aiohttp-3.14.3-cp313-cp313-android_21_arm64_v8a.whl", hash = "sha256:2e9878ae68e4a5f1c0abe4dd497dbc3d51946f5837b56759e2a02e78fa90ef86", size = 506269, upload-time = "2026-07-23T01:54:49.075Z" },
-    { url = "https://files.pythonhosted.org/packages/22/09/dec8189d62b45ade009f6792a2264b942a90cb88aeaf181239933cd72c3c/aiohttp-3.14.3-cp313-cp313-android_21_x86_64.whl", hash = "sha256:f3d2669fe7dec7fc359ecdb5984b29b50d85d5d00f8c1cb61de4f4a24ee42627", size = 515166, upload-time = "2026-07-23T01:54:51.894Z" },
-    { url = "https://files.pythonhosted.org/packages/28/24/2854869d29ed8a8b19d74f9ec6629515f7e04d02dd329d9d179201e58e47/aiohttp-3.14.3-cp313-cp313-ios_13_0_arm64_iphoneos.whl", hash = "sha256:cc7cb243a68167172f48c1fd43cee91ec4b1d40cefd190edd43369d1a6bc9c82", size = 486263, upload-time = "2026-07-23T01:54:54.223Z" },
-    { url = "https://files.pythonhosted.org/packages/d4/dd/57187c8be2a35aea65eaee3bd2c3dcbbcf0204f5106c89637e3610380cd1/aiohttp-3.14.3-cp313-cp313-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:78253b573e6ffab5028924fc98bc281aae05445969982a10864bc360dea2016c", size = 492299, upload-time = "2026-07-23T01:54:56.236Z" },
-    { url = "https://files.pythonhosted.org/packages/b9/11/06ae6ed8f0d414edf4068861e233d8fe23ee699bfd4b3ceb8663db948a62/aiohttp-3.14.3-cp313-cp313-ios_13_0_x86_64_iphonesimulator.whl", hash = "sha256:7041d52c3a7fa20c9e8c182b534704abb19502c8bdcbde7ab23bfda6f642394f", size = 502235, upload-time = "2026-07-23T01:54:58.377Z" },
-    { url = "https://files.pythonhosted.org/packages/7e/a3/559639c34a345d2cf7c52dff6838119f2eaf29eb508227b5b83f573af813/aiohttp-3.14.3-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:ac74facc01463f138b0da5580329cfcc82818dea5656e83ddcd11268fc12ff80", size = 750883, upload-time = "2026-07-23T01:55:00.65Z" },
-    { url = "https://files.pythonhosted.org/packages/91/cd/41e131f13afd1e7b0172a9d9eda085ef90eb8439f41f0d279db81ed3ae60/aiohttp-3.14.3-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:d6218d92e450824e9b4881f44e8c09f1853b490f9a64130801024a4793b1b3b0", size = 508473, upload-time = "2026-07-23T01:55:02.945Z" },
-    { url = "https://files.pythonhosted.org/packages/bc/6b/e7f13410d391c6e55b4c007a8de024355389d7d459e3d64c42b2d33617e5/aiohttp-3.14.3-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:11fb37ef075669eee52ab1928fbf6e1741fada40409fa309ebde9607a962aebf", size = 509190, upload-time = "2026-07-23T01:55:05.173Z" },
-    { url = "https://files.pythonhosted.org/packages/97/21/6464573e53d69672cc1eada3e5c5cb2d2efa82701e8305a0f2047a576967/aiohttp-3.14.3-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:55bdcc472aafe2de4a253045cc128007a64f1e0264fb675791e132ea5edaa3bd", size = 1761478, upload-time = "2026-07-23T01:55:07.383Z" },
-    { url = "https://files.pythonhosted.org/packages/1a/81/d217043a4c17fbce360905e3b2bdd20139ebc9a2de836d035d179c4da006/aiohttp-3.14.3-cp313-cp313-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:c39846c3aad97a8530c89d7a3869a8f8e9e3762c6ac0504481e5c80948f7e807", size = 1735092, upload-time = "2026-07-23T01:55:09.803Z" },
-    { url = "https://files.pythonhosted.org/packages/a1/66/e13a02d0eeb1a9a502402a977abb4e4abff9fe4051c26f80558c57a7c975/aiohttp-3.14.3-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:5895ef58c4620afe02fa16044f023dc4dafec08158f9d08874a46a7dbc0341b8", size = 1800546, upload-time = "2026-07-23T01:55:12.012Z" },
-    { url = "https://files.pythonhosted.org/packages/26/5e/57d42fca1d18cb5acc1cad945d017fabc5d6ae71d8a08ad66be8dc3ee544/aiohttp-3.14.3-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:fa9467a8113aa69d3d7c55a70ef0b7c636010a40993f3df9d9d0d73b3eb7ef24", size = 1895250, upload-time = "2026-07-23T01:55:14.357Z" },
-    { url = "https://files.pythonhosted.org/packages/ca/1c/7da8d08e74d56f00070822f9638ff3f1c563f8ad87d1efa996c87bfc8644/aiohttp-3.14.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:d7d2deec16eeedf55f2c7cf75b521ea3856a5177e123844f8fd0f114ce252cb5", size = 1789289, upload-time = "2026-07-23T01:55:16.668Z" },
-    { url = "https://files.pythonhosted.org/packages/cd/0f/cf16bcf56896981c1a0319f5d5db9337994b5165730c48a8fa07e9b34be6/aiohttp-3.14.3-cp313-cp313-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:dd54d0e8717de95939766febac482ac0474d8ac3b048115f9f2b1d23a16e7db4", size = 1586706, upload-time = "2026-07-23T01:55:18.913Z" },
-    { url = "https://files.pythonhosted.org/packages/fe/6f/76eac12a7f2480e1e304f842efdb07db33256b0d9165b866b6ef0806c202/aiohttp-3.14.3-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:df82f3787c940c94986b34222d59c9e38843fba85139f36e85255a82ad5355a9", size = 1724652, upload-time = "2026-07-23T01:55:21.296Z" },
-    { url = "https://files.pythonhosted.org/packages/39/b6/19c8c592baeeb94b75f966547d40c02ac7590902306ec5863d5c027cf506/aiohttp-3.14.3-cp313-cp313-musllinux_1_2_armv7l.whl", hash = "sha256:42a67efc36300d052fb4508a53e8b6901b9284b599ae63945c377569c5fcc1e1", size = 1756239, upload-time = "2026-07-23T01:55:23.705Z" },
-    { url = "https://files.pythonhosted.org/packages/dc/c9/4e9383150296f97f873b680c4de8fb2cd88608fb9f48c79edcb111611abc/aiohttp-3.14.3-cp313-cp313-musllinux_1_2_ppc64le.whl", hash = "sha256:7a75aa63cbf9b21cfaf60dc2657e19df2c2867d91707d653fee171ffeedd1371", size = 1769161, upload-time = "2026-07-23T01:55:26.082Z" },
-    { url = "https://files.pythonhosted.org/packages/aa/1e/147bdc6cc5de5f3ab011be8bf5d6e786633249f22c20bae06f85e45f5387/aiohttp-3.14.3-cp313-cp313-musllinux_1_2_riscv64.whl", hash = "sha256:e92eb8acc45eb6a9f4935071a77edf5b85cc6f8dfad5cd99e97653c26593cdde", size = 1578759, upload-time = "2026-07-23T01:55:28.846Z" },
-    { url = "https://files.pythonhosted.org/packages/fd/31/78388a9d6040ece2e11df62ea229a822cf5e52d238374b220ae9975b2623/aiohttp-3.14.3-cp313-cp313-musllinux_1_2_s390x.whl", hash = "sha256:b014a6ed7cf912e787149fdc529166d3ceabac23f26efeea3158c9aba2354e7e", size = 1792025, upload-time = "2026-07-23T01:55:31.457Z" },
-    { url = "https://files.pythonhosted.org/packages/03/51/a3d29fdf2c25d796746af8ad6fe56a45d6256c38b0a8a2ed752e1160b3a2/aiohttp-3.14.3-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:3d4f72af88ac2474bb5bca640030320e3d38a0163a1d7533500e87be458eef71", size = 1768477, upload-time = "2026-07-23T01:55:33.87Z" },
-    { url = "https://files.pythonhosted.org/packages/29/a6/442e18b5afeade534d877a2dc3c3e392aff8d49787890b0cf84790410267/aiohttp-3.14.3-cp313-cp313-win32.whl", hash = "sha256:5f08ec777f35ee70720233b8b9811d3bb5d728137f30ac91b7457709c3261ac0", size = 451069, upload-time = "2026-07-23T01:55:36.121Z" },
-    { url = "https://files.pythonhosted.org/packages/9d/69/3d876ac02659f271cf7f6769f14a8e3de5b6e888ed8b5a7e998086a4cec8/aiohttp-3.14.3-cp313-cp313-win_amd64.whl", hash = "sha256:dff9461ec275f22135650d5ba4b4931a11f3958df7dfbb8db630000d4dee0883", size = 476518, upload-time = "2026-07-23T01:55:38.303Z" },
-    { url = "https://files.pythonhosted.org/packages/b2/0e/50d6e6471cd31edce8b282bdec59375a3a69124d8a989a0b1313355cae52/aiohttp-3.14.3-cp313-cp313-win_arm64.whl", hash = "sha256:ddcac3c6b382e81f1dd0499199d4136b877beb4cb5ef770bbbfba56c4b8f55d2", size = 447676, upload-time = "2026-07-23T01:55:40.451Z" },
-    { url = "https://files.pythonhosted.org/packages/c8/20/887fdcf832326571b370ffc347b3e70abe101096f3720126aac161b1d872/aiohttp-3.14.3-cp314-cp314-android_24_arm64_v8a.whl", hash = "sha256:49f7325beb0f85ef4aef5f48f490269575f83e6e2acad00a1d80b807eb027062", size = 509067, upload-time = "2026-07-23T01:55:42.618Z" },
-    { url = "https://files.pythonhosted.org/packages/ad/a3/92cec936f78cc4bf0fa5554ebe593b73459d94e3c62303e1902a4cccb6f7/aiohttp-3.14.3-cp314-cp314-android_24_x86_64.whl", hash = "sha256:e3be98a7c30b8c25d573dafba7171d66dfb05ee6a9070fc46535464ff97700a6", size = 514774, upload-time = "2026-07-23T01:55:44.937Z" },
-    { url = "https://files.pythonhosted.org/packages/29/ba/2a0c38df3fc557620b6a5acd98364af050053b6285b4dc7ee74100c63c18/aiohttp-3.14.3-cp314-cp314-ios_13_0_arm64_iphoneos.whl", hash = "sha256:614c61d478b83953e261d02bb2df750f17227cd33ef8002945bf5aebbde21919", size = 488134, upload-time = "2026-07-23T01:55:47.135Z" },
-    { url = "https://files.pythonhosted.org/packages/48/d6/d51b7d4bf309af3693940d8ffd2b9ed0b682434ef85959b7c9c137f60cf8/aiohttp-3.14.3-cp314-cp314-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:1caa7b0d05f3e3a36f87788c59e970a7ee1cefcfcbb924a9f138c4a6551c9cb7", size = 494201, upload-time = "2026-07-23T01:55:49.451Z" },
-    { url = "https://files.pythonhosted.org/packages/3f/5a/8f624384e5f1efabb5229b94157eb966b021e97bdb188c62860c2ae243c2/aiohttp-3.14.3-cp314-cp314-ios_13_0_x86_64_iphonesimulator.whl", hash = "sha256:dfa68deb2a443bdaa3ea5297b0699c1464f08aef3812b486d1348eee61b07dc0", size = 502766, upload-time = "2026-07-23T01:55:51.656Z" },
-    { url = "https://files.pythonhosted.org/packages/a6/26/4ff0164370deec18fb19254ee4ab10b7a73304ac0c860b13f5f84663759b/aiohttp-3.14.3-cp314-cp314-macosx_10_15_universal2.whl", hash = "sha256:e72ee89e28d907a18f46959b4eb0bb06701cc7f8cf4366e00029e2ccfaaf5924", size = 756557, upload-time = "2026-07-23T01:55:53.964Z" },
-    { url = "https://files.pythonhosted.org/packages/97/a3/7056b86dc0d9ec709ea9777eae3b0161428f943372f8b98c01c11593b682/aiohttp-3.14.3-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:ad4c8b7488d745d2ca4838ebd8ae5ba9b56341d30b1da43640e4ce87f9f49646", size = 510168, upload-time = "2026-07-23T01:55:56.22Z" },
-    { url = "https://files.pythonhosted.org/packages/85/ed/0357a015892fd68058bf2d39d3fd1958e459b997a7db30aaa6aaa434ae96/aiohttp-3.14.3-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:db332af25642007330fca8be5c4d194caf2bea7a7fc84415aff3497af5dfee6b", size = 512957, upload-time = "2026-07-23T01:55:58.437Z" },
-    { url = "https://files.pythonhosted.org/packages/47/d1/8aba53f15ccb2238405f5e9d30e2a8ca44f93878c26e7165ade00d374b1c/aiohttp-3.14.3-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:25bd2708db6bdf6a6630dd37bdcdfcb47c4434d22ac69c64665b802910140b30", size = 1750149, upload-time = "2026-07-23T01:56:00.856Z" },
-    { url = "https://files.pythonhosted.org/packages/49/bd/40c3fee327529284375c6701cbb0fa4600cc2e8432af1378f897e2ef7d3a/aiohttp-3.14.3-cp314-cp314-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:cef89a58e628c4efcac3275c2d68083f82426dcdc89c1492a6f654f9f7ea6ab9", size = 1707685, upload-time = "2026-07-23T01:56:03.371Z" },
-    { url = "https://files.pythonhosted.org/packages/2a/a3/ca0cc6724cca8114b05694abd916060758c79894c3aa5b012cdadc1bc28e/aiohttp-3.14.3-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:c23ec8ee9d5ab2f5421f9c7fffce208435607af27fd46d4a44e031954352838f", size = 1803911, upload-time = "2026-07-23T01:56:05.817Z" },
-    { url = "https://files.pythonhosted.org/packages/95/b5/85b099c299c3ffd38ad9b3e43694c8a346934e4a30c88c4fd5a841234f77/aiohttp-3.14.3-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:e2667f0bbe7eb6c74eae5e9691441ad186e5845ca3cff63230fc09c4e7514f5d", size = 1876929, upload-time = "2026-07-23T01:56:08.413Z" },
-    { url = "https://files.pythonhosted.org/packages/d5/b7/1da684a04175473fa4cddbf9a2f572e79514c3fd27a74597f43057d4f3da/aiohttp-3.14.3-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:18cb43369747b2ae007bd2655fb8e63a099c2ff1d207962943636dac989b3147", size = 1761112, upload-time = "2026-07-23T01:56:10.918Z" },
-    { url = "https://files.pythonhosted.org/packages/d1/16/bc4b55e3e5cb175fd69c53c90d60d2f47797cb343da5106e23863dc4dba4/aiohttp-3.14.3-cp314-cp314-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:d77640cc618c1d99fc4f8589c0f24a730adfa54eb1e57ef7bf0c8dfb78da898c", size = 1583500, upload-time = "2026-07-23T01:56:13.613Z" },
-    { url = "https://files.pythonhosted.org/packages/2a/e8/13a9d957a1ee40837f46aa30f0f4c657e673ad86a2e6362a9f9be20d26d9/aiohttp-3.14.3-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:53e5179d8abb5710f8e83ba207c41c8d1261fcffd4616500e15ca2b7a33be10a", size = 1713940, upload-time = "2026-07-23T01:56:15.969Z" },
-    { url = "https://files.pythonhosted.org/packages/38/05/d33c680c1bcf1c7e130f9cbfc1fc02fe8bb0c4af2a94a53dd5fb56131e5c/aiohttp-3.14.3-cp314-cp314-musllinux_1_2_armv7l.whl", hash = "sha256:cd817772b2fcf2b8c0905795318485f9ec16eae60b29feb7f4c77085311637f0", size = 1724413, upload-time = "2026-07-23T01:56:18.591Z" },
-    { url = "https://files.pythonhosted.org/packages/85/1d/af798d306f7a74b6a632dbcabcf62a4c91391b7582d2a8c6d7712e2cc54e/aiohttp-3.14.3-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:4e3ac92d90e92773b2362d506068e9a948192bd553e743c5b2429e28527c8661", size = 1770748, upload-time = "2026-07-23T01:56:21.074Z" },
-    { url = "https://files.pythonhosted.org/packages/a8/92/ad720d472556a995049206867765e9410969684f86ee09423ff9969044c1/aiohttp-3.14.3-cp314-cp314-musllinux_1_2_riscv64.whl", hash = "sha256:3f42e9b78301f11c8f861746175d8b9c1ccef713fcad9eab396e2f6db8ed4a22", size = 1577564, upload-time = "2026-07-23T01:56:23.475Z" },
-    { url = "https://files.pythonhosted.org/packages/60/ad/0ed7586cbef7a884e23a752fa2bb987a122e6a5dd50dab109258d0a95193/aiohttp-3.14.3-cp314-cp314-musllinux_1_2_s390x.whl", hash = "sha256:9d9edccfe496b476db5f398d97b865e9a6752bcf8aec4eef8390ce20fb64bb41", size = 1782080, upload-time = "2026-07-23T01:56:25.994Z" },
-    { url = "https://files.pythonhosted.org/packages/97/ea/dbaed0d73e8a69aad653b045dab451c67c2454bb731a37b45a86593e9422/aiohttp-3.14.3-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:1c5ec8fb1bcc31a8466f74aaf26c345d5c386fa4bd08a3f0eb9c7a4a3fe8b5bf", size = 1745813, upload-time = "2026-07-23T01:56:28.604Z" },
-    { url = "https://files.pythonhosted.org/packages/81/1b/6893d4bc57e434fc93a6c9217c637d967a0b651d989f6e3265179375754a/aiohttp-3.14.3-cp314-cp314-win32.whl", hash = "sha256:38901a84da3ce22249f6e860bf8f90d141bcab7da090cc398f8bb58c0e44b7da", size = 455872, upload-time = "2026-07-23T01:56:31.031Z" },
-    { url = "https://files.pythonhosted.org/packages/f5/8b/c7baa1ba1eda4db6989baefe5de6d99834921b84ebd7918624febcb9f290/aiohttp-3.14.3-cp314-cp314-win_amd64.whl", hash = "sha256:8b3b60de05f3dcb6f6a00f818bb2ec781cee4de0645f59ccaf99b1d1823b6100", size = 481030, upload-time = "2026-07-23T01:56:33.365Z" },
-    { url = "https://files.pythonhosted.org/packages/22/8c/c29d067df825a2df88ca432db848aa2fe8199598359cc06c12b09320cac9/aiohttp-3.14.3-cp314-cp314-win_arm64.whl", hash = "sha256:1576145bdceeb92382d899751e12743a3a5b8e460a841e3e50543859e54864dc", size = 453669, upload-time = "2026-07-23T01:56:35.731Z" },
-    { url = "https://files.pythonhosted.org/packages/6a/a4/9c033beb355d39b6147980597ec9645e4729243f686ee4dc73945de72030/aiohttp-3.14.3-cp314-cp314t-macosx_10_15_universal2.whl", hash = "sha256:8800c996b01c2772a783e3e46f3e1abd5823029adca0df54231960de9bfefa5b", size = 791403, upload-time = "2026-07-23T01:56:37.972Z" },
-    { url = "https://files.pythonhosted.org/packages/80/ca/87c32a0a7704583cfc49660bd817889bae5b830bf53b5dcb4e92145ac2da/aiohttp-3.14.3-cp314-cp314t-macosx_10_15_x86_64.whl", hash = "sha256:ebe8e504f058fe91223351cecd2d9d6946c9d241bb0250d898ffbdf584cc72b0", size = 526413, upload-time = "2026-07-23T01:56:40.523Z" },
-    { url = "https://files.pythonhosted.org/packages/9e/d8/8ec0e471248c500acdce2be3f46db8fb62b5eb60efef072529cc85ee1d26/aiohttp-3.14.3-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:30402d03a7c0ff52bce290b57e564e9079fd9d0cb545c8aba73f86a103162d2e", size = 532135, upload-time = "2026-07-23T01:56:42.876Z" },
-    { url = "https://files.pythonhosted.org/packages/fe/45/f8919fd936e8b79fcd9bda7b6d8e62613462a713f4f17987fd7c34399142/aiohttp-3.14.3-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:9fc7b5bfec6573f3ae844f457fdde5adeb713f8b8e4a81ad64fc207b49383716", size = 1922742, upload-time = "2026-07-23T01:56:45.528Z" },
-    { url = "https://files.pythonhosted.org/packages/f6/ec/9ca76b28a27525b0cc53e20842e0228b022f301ce1f436b7d814b4aaf2df/aiohttp-3.14.3-cp314-cp314t-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:8a5fd34f7f7410d1730d5c2ba873cacb2eed3fede366feb268a70ba22581ed8f", size = 1787371, upload-time = "2026-07-23T01:56:48.045Z" },
-    { url = "https://files.pythonhosted.org/packages/b1/04/6acdbf17315f7b55f1937e3387acb89a3cddeb4995689553d064af8e92ab/aiohttp-3.14.3-cp314-cp314t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:270d3dace9ca2f10f0da5d8ebe519b7a310fc6112ed916e32df5866df0888553", size = 1912623, upload-time = "2026-07-23T01:56:50.605Z" },
-    { url = "https://files.pythonhosted.org/packages/86/e6/438b0c79ca6f45eb9fd9817dd4c01a91919a38c0de5ee9e05e2b4dc0ece7/aiohttp-3.14.3-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:3ae5b3a59436d089b5395d910121a390feed4d00578eb95a0fd1a329fe963100", size = 2005515, upload-time = "2026-07-23T01:56:53.153Z" },
-    { url = "https://files.pythonhosted.org/packages/bb/6b/62cbd6577758699525f5c712d1ddef57d9875fbab0ae8d5f5a202fd598f8/aiohttp-3.14.3-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:2498f0fe69ead802f9675beca44a7c21c62fdaa4ec5145ea1c3ad6edbee29f85", size = 1879906, upload-time = "2026-07-23T01:56:55.818Z" },
-    { url = "https://files.pythonhosted.org/packages/00/95/18bcbf830a21dc3aae24d8f6b6feaf3db1d2090242d00a7868db2ffb0b67/aiohttp-3.14.3-cp314-cp314t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:a0dc483c00da8b673abbb367eb6f8d8f4bcec30eb58529ea13cb42e7fd2dfa33", size = 1675849, upload-time = "2026-07-23T01:56:58.861Z" },
-    { url = "https://files.pythonhosted.org/packages/a9/19/47f4968659c5e23606c3790c80fc624e691c153d036148449ee84d31b287/aiohttp-3.14.3-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:c7d3a97c678d34fc5b59da671ee9cd630096ddc643e7b5a30d54a2a6f3574d3f", size = 1843496, upload-time = "2026-07-23T01:57:01.591Z" },
-    { url = "https://files.pythonhosted.org/packages/64/af/38c33c4dd82fddcb4e56c4653b6f1072a8edbc6b7fa15809f14932c41e2d/aiohttp-3.14.3-cp314-cp314t-musllinux_1_2_armv7l.whl", hash = "sha256:f8fb78a83c9e5f741ca3a68cfb455c1f5bb83b4e7249a3848b3cd78d0a8563b0", size = 1827746, upload-time = "2026-07-23T01:57:05.131Z" },
-    { url = "https://files.pythonhosted.org/packages/a1/9d/0537cda4885ac8f5b7053d164dd06312f4c483a4edcb8ee5b8aaf2a989bf/aiohttp-3.14.3-cp314-cp314t-musllinux_1_2_ppc64le.whl", hash = "sha256:74ab5b6a9fb13e873e5a90946588baecaf488745e1db1a4a5c433f971f035098", size = 1853810, upload-time = "2026-07-23T01:57:08.043Z" },
-    { url = "https://files.pythonhosted.org/packages/19/fe/26f9c5e6458385aa86497836b0dea6fb2f027827d63f37c7856cce9286ee/aiohttp-3.14.3-cp314-cp314t-musllinux_1_2_riscv64.whl", hash = "sha256:bd52f811e65f6fb634b1047159657c98f52b407f8efec907bcfc09da9a4c0a25", size = 1668895, upload-time = "2026-07-23T01:57:10.837Z" },
-    { url = "https://files.pythonhosted.org/packages/ec/4c/618b1db9b9ba079b8875d2cdf78e7c4a3bf72903bd5850fee7dd9544600a/aiohttp-3.14.3-cp314-cp314t-musllinux_1_2_s390x.whl", hash = "sha256:f0f177d1b195b9e06376cfd7d308d8a1b920909a609d03ac82a8c73bbb16d3b9", size = 1883833, upload-time = "2026-07-23T01:57:13.672Z" },
-    { url = "https://files.pythonhosted.org/packages/94/c6/bd959bd1e4771f9fd944e9e436224c48c77b018b73b519b5aad346335bcc/aiohttp-3.14.3-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:498c6c623134f8e09a3c4e60bcd607a0b4590dd7dbf08dd40851b27cbb520ccb", size = 1844251, upload-time = "2026-07-23T01:57:16.593Z" },
-    { url = "https://files.pythonhosted.org/packages/5e/19/08d41839658bdd44a0ed2480f3891705ecb487ce28c0dde62c9040c997e0/aiohttp-3.14.3-cp314-cp314t-win32.whl", hash = "sha256:b304db572b4368edd8dda8a2274f73156fe15558fca4a917cb8a09fc47af5963", size = 474180, upload-time = "2026-07-23T01:57:19.306Z" },
-    { url = "https://files.pythonhosted.org/packages/99/5d/3cd6ef0a2b2851f7ab913b5b079334781bd50ff56a323e4454063377a080/aiohttp-3.14.3-cp314-cp314t-win_amd64.whl", hash = "sha256:b20032766aedf6261c7a566585a40867d092ac03a0d81592d5370ef9b054f99b", size = 500528, upload-time = "2026-07-23T01:57:21.762Z" },
-    { url = "https://files.pythonhosted.org/packages/a4/37/cfd1ed540a4d318da025590d96b728e63713c09e9377950fc655dadeb856/aiohttp-3.14.3-cp314-cp314t-win_arm64.whl", hash = "sha256:2e1161602f45a54de2ce0905243a95f58cb42dcd378402f3697f5e0b21e9d2e7", size = 469280, upload-time = "2026-07-23T01:57:24.241Z" },
-]
-
-[[package]]
-name = "aiosignal"
-version = "1.4.0"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "frozenlist" },
-    { name = "typing-extensions", marker = "python_full_version < '3.13'" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/61/62/06741b579156360248d1ec624842ad0edf697050bbaf7c3e46394e106ad1/aiosignal-1.4.0.tar.gz", hash = "sha256:f47eecd9468083c2029cc99945502cb7708b082c232f9aca65da147157b251c7", size = 25007, upload-time = "2025-07-03T22:54:43.528Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/fb/76/641ae371508676492379f16e2fa48f4e2c11741bd63c48be4b12a6b09cba/aiosignal-1.4.0-py3-none-any.whl", hash = "sha256:053243f8b92b990551949e63930a839ff0cf0b0ebbe0597b0f3fb19e1a0fe82e", size = 7490, upload-time = "2025-07-03T22:54:42.156Z" },
-]
-
-[[package]]
-name = "annotated-types"
-version = "0.8.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/5f/56/a8120250d128bed162cd73c76d45f6ef9991f3e068f62a8ee060afa3104a/annotated_types-0.8.0.tar.gz", hash = "sha256:13b2beaad985e05e2d6407ee4c4f35590b11f8d693a258a561055cac8f64cab7", size = 15893, upload-time = "2026-07-23T20:16:13.995Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/99/91/8acff4f5e50511b911bbccb72b8628a49c68ce14148cd9f6431094859a90/annotated_types-0.8.0-py3-none-any.whl", hash = "sha256:f072f4d804ea359e4eaf198b1af7a8b0943881a87f31bb764f8bf219bb9419e0", size = 13427, upload-time = "2026-07-23T20:16:12.938Z" },
-]
-
-[[package]]
-name = "anyio"
-version = "4.14.2"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "idna" },
-    { name = "typing-extensions", marker = "python_full_version < '3.13'" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/61/cc/a381afa6efea9f496eff839d4a6a1aed3bfafc7b3ab4b0d1b243a12573dd/anyio-4.14.2.tar.gz", hash = "sha256:cfa139f3ed1a23ee8f88a145ddb5ac7605b8bbfd8592baacd7ce3d8bb4313c7f", size = 260176, upload-time = "2026-07-12T20:29:07.082Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/da/35/f2287558c17e29fafc8ef3daf819bb9834061cfa43bff8014f7df7f63bdc/anyio-4.14.2-py3-none-any.whl", hash = "sha256:9f505dda5ac9f0c8309b5e8bd445a8c2bf7246f3ce950121e45ea15bc41d1494", size = 125813, upload-time = "2026-07-12T20:29:05.763Z" },
-]
-
-[[package]]
-name = "attrs"
-version = "26.1.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/9a/8e/82a0fe20a541c03148528be8cac2408564a6c9a0cc7e9171802bc1d26985/attrs-26.1.0.tar.gz", hash = "sha256:d03ceb89cb322a8fd706d4fb91940737b6642aa36998fe130a9bc96c985eff32", size = 952055, upload-time = "2026-03-19T14:22:25.026Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/64/b4/17d4b0b2a2dc85a6df63d1157e028ed19f90d4cd97c36717afef2bc2f395/attrs-26.1.0-py3-none-any.whl", hash = "sha256:c647aa4a12dfbad9333ca4e71fe62ddc36f4e63b2d260a37a8b83d2f043ac309", size = 67548, upload-time = "2026-03-19T14:22:23.645Z" },
-]
-
-[[package]]
-name = "boto3"
-version = "1.43.79"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "botocore" },
-    { name = "jmespath" },
-    { name = "s3transfer" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/2d/1b/d5091a11b37633c987015516fb87e1330c5e97c42ab2d6527b778bdc537a/boto3-1.43.79.tar.gz", hash = "sha256:a36b4209a8170f7f8d2c19b36f350808f313b178939c9e5df0a8f683717a6d9c", size = 112682, upload-time = "2026-08-24T19:30:13.676Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/7a/90/eef59b9b64442b4c966b027e8db407f59d99200b82b71316fc4466562a53/boto3-1.43.79-py3-none-any.whl", hash = "sha256:4c2381cf99abf749c82762a636337f4aba4800fda6525412fcae2bebe4f72748", size = 140025, upload-time = "2026-08-24T19:30:12.331Z" },
-]
-
-[[package]]
-name = "botocore"
-version = "1.43.79"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "jmespath" },
-    { name = "python-dateutil" },
-    { name = "urllib3" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/4b/90/e67b32a388f5be5fa84adb92eb4be4d9bbe51a70fd4a208222bf6d428972/botocore-1.43.79.tar.gz", hash = "sha256:dcc0a97b65affcef80e0499745d2e6a5d120253c11b8727b8227df44ab3e958f", size = 15988663, upload-time = "2026-08-24T19:30:09.145Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/49/d5/f34b9313ca9db131ad7d74156e3459694ced17f81233a248bd00eb6d67b1/botocore-1.43.79-py3-none-any.whl", hash = "sha256:19b2c772ea2590d0baad6ae004a0e478cf2c982e0e6a39c8e2f882d9b2981445", size = 15680587, upload-time = "2026-08-24T19:30:04.397Z" },
-]
-
-[[package]]
-name = "certifi"
-version = "2026.7.22"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/a3/c2/24167ea9858356b47a87a50d39908bfdb72ceeefe0041586e704e5376b3a/certifi-2026.7.22.tar.gz", hash = "sha256:741e2c3b351ddf169a738da9f2c048608ff7f2c5cc02f1ebc6b118bb090d5d55", size = 138112, upload-time = "2026-07-22T03:35:12.644Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/0b/a7/71ac2cff56fec219ed242bb11b8efb69fcc4bec75db06fb7bfe35de520e6/certifi-2026.7.22-py3-none-any.whl", hash = "sha256:62f22742b58a1a33014a2b6b706588a8d7e2a88ae7bd1a6ebe8c992928483775", size = 136983, upload-time = "2026-07-22T03:35:11.276Z" },
-]
-
-[[package]]
-name = "charset-normalizer"
-version = "3.5.1"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/e5/3f/143b048436775b0f76ac3eec145c019e8173ccc2885c8f20319b996d5e83/charset_normalizer-3.5.1.tar.gz", hash = "sha256:6117b84ea48435e5356dc737f5121485c30920ba43375fa7b434fd753df0eac3", size = 171764, upload-time = "2026-08-15T08:20:44.807Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/30/27/78873dc8b6a56357517b74b6bb9568b80450e7bb4f6ef7e3fa9d22aa0bd7/charset_normalizer-3.5.1-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:5b6d1386bf0096d26d3a863dc0a487a5b4eb9aa93cf5ba69683d29dde6b9d60f", size = 344456, upload-time = "2026-08-15T08:17:10.072Z" },
-    { url = "https://files.pythonhosted.org/packages/9a/4c/be49ada26b1f0232d57aa89bbebf997a5cc2332a5616b6eca26ff680044d/charset_normalizer-3.5.1-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:4582c27e8c889d64811987b5967fbd3ae0c823fe1fd933b543d55ac20bb475fa", size = 238530, upload-time = "2026-08-15T08:17:11.563Z" },
-    { url = "https://files.pythonhosted.org/packages/76/84/6f1290fa07ae6978d3960caa3eb1b8019bf9284ab7c2297b00c099ef4250/charset_normalizer-3.5.1-cp312-cp312-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:1d1c7a53a6c2103925cdd6d7229f8c567379f211c869793df679f2e9f738c369", size = 230200, upload-time = "2026-08-15T08:17:12.919Z" },
-    { url = "https://files.pythonhosted.org/packages/e7/a0/47b18adeed31c8f16ba9700f32c1b18594cfa09f47eb672a488c273c22bf/charset_normalizer-3.5.1-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:e6621fb2a4988d6e53eedc455e5903e2679f3967b8acb3d639f1b63c14a2e893", size = 262222, upload-time = "2026-08-15T08:17:14.571Z" },
-    { url = "https://files.pythonhosted.org/packages/38/fe/341861ac118dae06f3ec0eb487488af52128f2ef2faf0b11003944d22259/charset_normalizer-3.5.1-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:7c0c10730342b0c9b35dd1d619beb8214e520bd96a1f870f452680b238aab3e0", size = 258951, upload-time = "2026-08-15T08:17:16.158Z" },
-    { url = "https://files.pythonhosted.org/packages/6f/89/bb5108dc6c3651dca963f2b0a3ba19bbcb370c94e1b6d3e0e844a58e6dca/charset_normalizer-3.5.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:b9af956078716df40d985fb0dfeb2c2120c5ca92ba4ff4b388acfd01cdc14d08", size = 248801, upload-time = "2026-08-15T08:17:17.683Z" },
-    { url = "https://files.pythonhosted.org/packages/b1/ba/ef83ae3aca816393decfa3530976f38a79812d707b80b580ac33b83f9877/charset_normalizer-3.5.1-cp312-cp312-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:f9f8405c2c758532c74fed975dbee57be1f31a6e865c031870c79a6ed3212ada", size = 244070, upload-time = "2026-08-15T08:17:19.191Z" },
-    { url = "https://files.pythonhosted.org/packages/f6/0b/c5292a2462d69b7378ea89793bbb5b2b6fcf6f7dd6d1667f9619094ad553/charset_normalizer-3.5.1-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:96fef3e886d6a9874b14f27fc193fbdc69d5d8035783d86aa4e1cea594e695f9", size = 240110, upload-time = "2026-08-15T08:17:20.547Z" },
-    { url = "https://files.pythonhosted.org/packages/46/22/111e5be3b740d5c2a5bfcedb3d237b6591e5c2e82ae9d6ffcb121fe0909c/charset_normalizer-3.5.1-cp312-cp312-musllinux_1_2_armv7l.whl", hash = "sha256:5d8531a6569d025f68e2321e7638fb7978f23db58e5f69f56913837aae03816e", size = 232836, upload-time = "2026-08-15T08:17:21.895Z" },
-    { url = "https://files.pythonhosted.org/packages/f9/d2/d2aad6fe0dbb44b194bf3becb60f5a0ac48446ade999a47fe7bb41eb09a7/charset_normalizer-3.5.1-cp312-cp312-musllinux_1_2_ppc64le.whl", hash = "sha256:aae2ee51122d3ae968a3837d97dc24a0aeebb0dea23694422cd172bd30017cd6", size = 262712, upload-time = "2026-08-15T08:17:23.727Z" },
-    { url = "https://files.pythonhosted.org/packages/35/5a/337e4663a5eae6de99db940ee8066d4145caafb61327db62deda15313cce/charset_normalizer-3.5.1-cp312-cp312-musllinux_1_2_riscv64.whl", hash = "sha256:7235dc28fc6dd9d832ac7c7bce95367dedb85929f17368a0c2bee1e080b9acbf", size = 242977, upload-time = "2026-08-15T08:17:25.157Z" },
-    { url = "https://files.pythonhosted.org/packages/ca/85/f82f8a92e31c7519410e2e1afdc630f28ec47490ce2c09a11c1a43cbb459/charset_normalizer-3.5.1-cp312-cp312-musllinux_1_2_s390x.whl", hash = "sha256:4abdc5f9ad448c1ecbfae2974b820535d6bc6e7eef63babbab3d81cf46968c71", size = 260207, upload-time = "2026-08-15T08:17:26.602Z" },
-    { url = "https://files.pythonhosted.org/packages/b7/52/643d11ffd60e9ac2fd1fb87e167a19285b9eefeff4a40e63c87cbfbeab36/charset_normalizer-3.5.1-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:ba501e667c17d8411f98e67a022d9604ef179aff0e459b7e292c796837c13573", size = 250562, upload-time = "2026-08-15T08:17:27.971Z" },
-    { url = "https://files.pythonhosted.org/packages/62/16/46556278c2168d12df9da7fede5dc6fc70e60301b26a82bbeec238c9cfe3/charset_normalizer-3.5.1-cp312-cp312-win32.whl", hash = "sha256:cfa1c0cc3a8f9f53f1243a5a99ac36fd003880199383b37672e86ddda9cb07e2", size = 178507, upload-time = "2026-08-15T08:17:29.277Z" },
-    { url = "https://files.pythonhosted.org/packages/9d/7a/4c6c298171e6b3e745633180ff59350fc0ca0db1ffd28df1e369e0579f71/charset_normalizer-3.5.1-cp312-cp312-win_amd64.whl", hash = "sha256:3617ac3cfd8b9888f145ad89dd6e692285834b0201c6074a5eeaad3fd4d668c2", size = 200551, upload-time = "2026-08-15T08:17:30.668Z" },
-    { url = "https://files.pythonhosted.org/packages/cd/d7/eb95a042f0dd22e304b0b6472b154f3546a1a039a9ee89ccb2a7f61591fc/charset_normalizer-3.5.1-cp312-cp312-win_arm64.whl", hash = "sha256:88e85ab89cb822c1e635f51d6d32e488f94e002e70e2f492bdb8b945543f345a", size = 180700, upload-time = "2026-08-15T08:17:32.028Z" },
-    { url = "https://files.pythonhosted.org/packages/bc/61/2cb6ad133dbbb449fa2d37ccae973232f4827e799af258d15e589a3d1e9e/charset_normalizer-3.5.1-cp313-cp313-android_24_arm64_v8a.whl", hash = "sha256:4f298bdadb8f0b9e5672877f647d1be9373ef5320c9e2f049795e26cad28b6a9", size = 211584, upload-time = "2026-08-15T08:17:33.597Z" },
-    { url = "https://files.pythonhosted.org/packages/18/57/a305c968be1ca13f3dd1b32f445877e97addf55d80b65c7cb35fac82b777/charset_normalizer-3.5.1-cp313-cp313-android_24_x86_64.whl", hash = "sha256:88ca277405c2d3b71c4e1c2ee0e7966e807bcba86a69d11e19ba199d18ae4491", size = 223359, upload-time = "2026-08-15T08:17:35.022Z" },
-    { url = "https://files.pythonhosted.org/packages/09/0a/d3646670292ce8d8f8cc11ac067d44885e697a5591f57a9221128da5e7b3/charset_normalizer-3.5.1-cp313-cp313-ios_13_0_arm64_iphoneos.whl", hash = "sha256:9362dd90aa7dab48c0054a21187791ccf05473f7dba5d92b8033ae62164675e7", size = 194464, upload-time = "2026-08-15T08:17:36.452Z" },
-    { url = "https://files.pythonhosted.org/packages/de/93/d51ec556e01042fed6f993ea859311bc7917b466684182fbbceb6ca24762/charset_normalizer-3.5.1-cp313-cp313-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:977cdbd483a9cff38179bea4fd754289a6f2195c7abd414aba85410b3e66cc5e", size = 197676, upload-time = "2026-08-15T08:17:37.819Z" },
-    { url = "https://files.pythonhosted.org/packages/a4/a0/562247944386f7d4ef94467e84876600cc1e0f1b93239aaa9213d2bc3cbd/charset_normalizer-3.5.1-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:e90251c0c7bdd54a100a0dce3c07b7e637278c93af29dbf78ebb89a58c4bac7d", size = 340473, upload-time = "2026-08-15T08:17:39.303Z" },
-    { url = "https://files.pythonhosted.org/packages/31/e7/1d994be1b93d41e9502b8b0460eaa88a1dd8df335df415db87d6c3e91ab2/charset_normalizer-3.5.1-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:94d78ecec2605a8d0398b0f365d5f12a63248438516f5dac536a5eff7337df4a", size = 240156, upload-time = "2026-08-15T08:17:40.66Z" },
-    { url = "https://files.pythonhosted.org/packages/09/53/27923ce5cc6cbccb832037b27dca98882d9c53e9b69e866bbbef4aae7fc8/charset_normalizer-3.5.1-cp313-cp313-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:d59b75732e9b6f27388e10c14b0259cc5f2e48c78627d185e6a177b58ad3cffe", size = 228246, upload-time = "2026-08-15T08:17:42.003Z" },
-    { url = "https://files.pythonhosted.org/packages/ce/48/5a97e84d63af1d55c07439cb80e56d99a8efb4295700eb4e18c0d1615d2c/charset_normalizer-3.5.1-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:0d929fc574b4d6fd9e7c0f5c2ede8716a41911923aa7fa5fce38e0818aa4a1ac", size = 263660, upload-time = "2026-08-15T08:17:43.627Z" },
-    { url = "https://files.pythonhosted.org/packages/7a/c2/071575791dcc88316c0a9a65ce38897a82e4cfe4a325f0f7fe1b1ac47bcf/charset_normalizer-3.5.1-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:394fea06235c8543390050ed5f529187074b029fb027213f6c46ac11ab5d950e", size = 260354, upload-time = "2026-08-15T08:17:45.094Z" },
-    { url = "https://files.pythonhosted.org/packages/fb/af/63240b0c0248c075c2535a1f1bd992821d8251b9f173abc13329661d09e4/charset_normalizer-3.5.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:62b55f6722735a6c472f88361cde6640608773d9443cebdbb51abf436a1fcdd3", size = 250638, upload-time = "2026-08-15T08:17:46.496Z" },
-    { url = "https://files.pythonhosted.org/packages/4d/66/70dfad64f15be09c15ccfee81330a7e515895dbe296dd23114e9a231268a/charset_normalizer-3.5.1-cp313-cp313-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:fa48b1b63d639f9483e0633e092f5851e2348c352f1f9bb6c8182f87884ef876", size = 244583, upload-time = "2026-08-15T08:17:47.963Z" },
-    { url = "https://files.pythonhosted.org/packages/c0/24/ef36367d38b9ddd4bccbf72888c342e8de1f5ae506fa0b2dcf970e2732a1/charset_normalizer-3.5.1-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:c71fb0d56c920c269cd3e2e3fe7c610e3f1fdb21a6ce60efa6430ff63676cea6", size = 242038, upload-time = "2026-08-15T08:17:49.481Z" },
-    { url = "https://files.pythonhosted.org/packages/db/ab/55e683ba0fff2e43adafc10daa3001eac90fdaa419a97227d5a7067eedde/charset_normalizer-3.5.1-cp313-cp313-musllinux_1_2_armv7l.whl", hash = "sha256:485a0d363cafefcd2538a73c7c838daa2035f09b2c9f9b5e3133f80c6aeb84c2", size = 233677, upload-time = "2026-08-15T08:17:50.845Z" },
-    { url = "https://files.pythonhosted.org/packages/bd/67/0f40eaf8d1b6e7cf15e82382a2965efaca787fc1c2794b7021d37aaf5036/charset_normalizer-3.5.1-cp313-cp313-musllinux_1_2_ppc64le.whl", hash = "sha256:5c0ea61a470e070686aa30892fed79e297d2c8d0ab46b8bcdf027d38c51da591", size = 264491, upload-time = "2026-08-15T08:17:52.61Z" },
-    { url = "https://files.pythonhosted.org/packages/5c/64/12b4c2a11ee8df4fcc518c78b0d93e3a92bd3d5253d1617ce74ff0e8c7ef/charset_normalizer-3.5.1-cp313-cp313-musllinux_1_2_riscv64.whl", hash = "sha256:90b7481fb62fbe172c558bc6fd1c4c98d82004a54a7551f20e11ac9bf0b8708c", size = 245196, upload-time = "2026-08-15T08:17:54.023Z" },
-    { url = "https://files.pythonhosted.org/packages/37/2e/651d910af6d0fba325eee1cda37ec5443462ed25360e666c144166eb6091/charset_normalizer-3.5.1-cp313-cp313-musllinux_1_2_s390x.whl", hash = "sha256:35fe081843b35aad20ffeccec3eeffbe637b15d14f3fb22cc1b59cd8ec17e93c", size = 261660, upload-time = "2026-08-15T08:17:55.491Z" },
-    { url = "https://files.pythonhosted.org/packages/90/c6/b09e05e6db7f64338e0dc067c79577b1138da86c1e38369096851d96be88/charset_normalizer-3.5.1-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:fd0350afdc3aabd5576f60ea109228bd5538139713c7b094c5cd27c73a98bc6f", size = 252618, upload-time = "2026-08-15T08:17:57.025Z" },
-    { url = "https://files.pythonhosted.org/packages/76/4e/362d4f9fdcdf5556fb2aa3ce7d4a58ebce03ed1ff03aa1d9aca8d02f13f3/charset_normalizer-3.5.1-cp313-cp313-pyemscripten_2025_0_wasm32.whl", hash = "sha256:9d9a0dc7cbe9bec24c3f767c9122c41fe5a1bc43f47cd099d00d393e09769de4", size = 140362, upload-time = "2026-08-15T08:17:58.425Z" },
-    { url = "https://files.pythonhosted.org/packages/b4/d4/703be739b26acce318bd29eb3b25b7209e1b1f527f9eae3d1f1f01fdde2b/charset_normalizer-3.5.1-cp313-cp313-win32.whl", hash = "sha256:d63600d620ad0064c3a748b950ac5ea38a80190e5498532efefa4b7b3f1da1f3", size = 177755, upload-time = "2026-08-15T08:18:00.037Z" },
-    { url = "https://files.pythonhosted.org/packages/8a/33/56d97ade41c8db611e727168c52ae46c9224c362ec28d4b65d7e9869e8da/charset_normalizer-3.5.1-cp313-cp313-win_amd64.whl", hash = "sha256:aea996a6aba25260827c9ea511d1addfde2da9eb686ac961838509086188b7e6", size = 199295, upload-time = "2026-08-15T08:18:01.506Z" },
-    { url = "https://files.pythonhosted.org/packages/5b/75/5b20dd1e6573a01a08158fe104104fa2c8abf941745596954185726cd46c/charset_normalizer-3.5.1-cp313-cp313-win_arm64.whl", hash = "sha256:fd0a274c0e5f9a21565cd9d3dd749b61f96b7aa1e20a93aa1ba4029518f2e5c0", size = 179856, upload-time = "2026-08-15T08:18:02.929Z" },
-    { url = "https://files.pythonhosted.org/packages/29/cd/2b812ce5e888f1ce69a5350281e58aab07ae64a958ecae8912f30865718e/charset_normalizer-3.5.1-cp314-cp314-android_24_arm64_v8a.whl", hash = "sha256:774d157f112367ff4abd29019f38f023c24e00e56edc7829c20e358a5a913ad8", size = 212318, upload-time = "2026-08-15T08:18:04.403Z" },
-    { url = "https://files.pythonhosted.org/packages/9e/4a/a6ee107430768a5334e6d63f31f148a04a1a491ef161a1ac9415a73f2fa8/charset_normalizer-3.5.1-cp314-cp314-android_24_x86_64.whl", hash = "sha256:26422d45fd13551cf564c58932f7d72b4f58b93b0fcf18c35ba6be12b46bb102", size = 224897, upload-time = "2026-08-15T08:18:05.997Z" },
-    { url = "https://files.pythonhosted.org/packages/c3/d9/35ae3f64f29d0179c35c3baefe575904df2913dde519129c7f75995a2b1d/charset_normalizer-3.5.1-cp314-cp314-ios_13_0_arm64_iphoneos.whl", hash = "sha256:09a7bba9f739468c8e78c36a75c33768e53cb1959fc638f510454c14683f00d5", size = 194848, upload-time = "2026-08-15T08:18:07.397Z" },
-    { url = "https://files.pythonhosted.org/packages/74/76/f2fc7380f056cc273a53af37f50d08ad54b2c59f61078f31432edcf1c2bd/charset_normalizer-3.5.1-cp314-cp314-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:4c9548dc78002099910abaebc0a72ac58b7d30931869e0351c09b507dff4ece3", size = 198163, upload-time = "2026-08-15T08:18:08.989Z" },
-    { url = "https://files.pythonhosted.org/packages/e9/40/095ce62fa078483cccc1fa2b36e6bc9580b85422a20ee9f925341c50e44f/charset_normalizer-3.5.1-cp314-cp314-macosx_10_15_universal2.whl", hash = "sha256:c428c6c31eb5f4277d7f8eccaf767fbd548ddd5ce3c8b4f4cbbfab3d96b5904c", size = 341823, upload-time = "2026-08-15T08:18:10.458Z" },
-    { url = "https://files.pythonhosted.org/packages/f1/5a/0e58b1c04a1596e0256f407274a92d5fb2ee21324409d1fab1da48a65b5b/charset_normalizer-3.5.1-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:2f06b7eae9dbe77fe1d644ca244dad508de8d302870a43f3c559b521270938a0", size = 242458, upload-time = "2026-08-15T08:18:11.989Z" },
-    { url = "https://files.pythonhosted.org/packages/22/95/b4618ce912e6db0b1aae89ba788e38e8a7eba0f3025cc66e8c0699f977b2/charset_normalizer-3.5.1-cp314-cp314-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:6b7430cf5728e68f6c462254009a6ef4086e1bea43cf2f57aa9c55fb4f50ff96", size = 226717, upload-time = "2026-08-15T08:18:13.401Z" },
-    { url = "https://files.pythonhosted.org/packages/8a/76/c681192bbda3d55356db5dadd64381d5202b37c6b598fcda5282e88b5d3d/charset_normalizer-3.5.1-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:ab743e9bc90c1f73552ec33e10e3331315acd2c397b36065b591b0181de533cc", size = 266111, upload-time = "2026-08-15T08:18:14.961Z" },
-    { url = "https://files.pythonhosted.org/packages/88/be/55127bfca72c0cff6c022488d140d7c5b04c771e3b72e9bdb4836d54979d/charset_normalizer-3.5.1-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:f6f7deae3feb4edfa2efaf7c574fe88cbf055038a6abdb40188e4fff66d5699f", size = 263128, upload-time = "2026-08-15T08:18:16.515Z" },
-    { url = "https://files.pythonhosted.org/packages/e0/91/39c3af510b0aa32bbda03374259200f28430febfd1bf5e511fe765282ce5/charset_normalizer-3.5.1-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:15f024313246a4ed976c60f440bb8d257815513a681d212ff74fd46f7d715a90", size = 251240, upload-time = "2026-08-15T08:18:18.127Z" },
-    { url = "https://files.pythonhosted.org/packages/1c/a5/cbe418bbc6ecdfc3e05a0116002897c4b403a5e838d697e64c78e9f0190d/charset_normalizer-3.5.1-cp314-cp314-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:823f82903d189af463d7df250ef1f7f696f3cee08cc8d91deb565e8d425f6506", size = 245282, upload-time = "2026-08-15T08:18:19.625Z" },
-    { url = "https://files.pythonhosted.org/packages/cc/a4/689bb42e8e7cd492f3cb64907c6bc00ad247ec9a3628cd3f8eed126e8ae1/charset_normalizer-3.5.1-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:01e93745f7f219b703b60ba7afead36cfc4242782be5af484673fc500df12da5", size = 244597, upload-time = "2026-08-15T08:18:21.121Z" },
-    { url = "https://files.pythonhosted.org/packages/c1/ce/9962938e179cf9f699d3f1e7b3114b5d7642dee6a893745229f9dd04f274/charset_normalizer-3.5.1-cp314-cp314-musllinux_1_2_armv7l.whl", hash = "sha256:329fc3ccb63ad22d867d84c2adea759a64079a37ba4a343433b02c7a2816871e", size = 231376, upload-time = "2026-08-15T08:18:22.57Z" },
-    { url = "https://files.pythonhosted.org/packages/85/54/46000450ada53bd9eac5429a2c8c54cd2d9b39c0c255f229aea9af0948a5/charset_normalizer-3.5.1-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:bb57753e36e4855b8ca375069482250a6246372331a3e4f3407eaebb007443f5", size = 266715, upload-time = "2026-08-15T08:18:24.235Z" },
-    { url = "https://files.pythonhosted.org/packages/3d/bb/618749d70f792b44252a777bf89bfb86823b9bbc1ea13fe8ce759b07f38a/charset_normalizer-3.5.1-cp314-cp314-musllinux_1_2_riscv64.whl", hash = "sha256:fce8cbd4997efeb450bd298b54f755dcdff18d496f7a5ddbb4867c6d7c88fdc3", size = 245848, upload-time = "2026-08-15T08:18:25.726Z" },
-    { url = "https://files.pythonhosted.org/packages/7e/3f/ffb64458527c7668031d5eb095d978de561958dc9f5b53f8e488a533e603/charset_normalizer-3.5.1-cp314-cp314-musllinux_1_2_s390x.whl", hash = "sha256:6c9cdde8becb25a7fde49924511aa2644d6f8081cc8df8e9452724303348d8e3", size = 264521, upload-time = "2026-08-15T08:18:27.193Z" },
-    { url = "https://files.pythonhosted.org/packages/4f/ab/74a55fd803916a35ac461daf002708191aac19b546b80dc8cabfedc63d98/charset_normalizer-3.5.1-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:9ac4444d8d4fd4c4bd08bf451ed3167aa9e7ec6cdb41b648794f1d1103652e36", size = 253054, upload-time = "2026-08-15T08:18:28.568Z" },
-    { url = "https://files.pythonhosted.org/packages/a0/2a/6a9034b7d3c60b17499afb482df5878bf9fa20b50cc3887d5ef017a833db/charset_normalizer-3.5.1-cp314-cp314-pyemscripten_2026_0_wasm32.whl", hash = "sha256:f03ac127268b43ef4fe9e6ab6794a6794b49485a0cc0c1db79876d2f33f75bc7", size = 140580, upload-time = "2026-08-15T08:18:30.214Z" },
-    { url = "https://files.pythonhosted.org/packages/f3/46/1d362e1a00d035d66b9869e1281eee115907f7e390a16a07824ab5737360/charset_normalizer-3.5.1-cp314-cp314-win32.whl", hash = "sha256:1f5883d77fd409a261abb5dc8ccbe335720d798b1de4abb3b1d47ccbbc76b53b", size = 180325, upload-time = "2026-08-15T08:18:31.877Z" },
-    { url = "https://files.pythonhosted.org/packages/7a/7c/4938c329b6a9d446f6a59aa2092ff7118f274209b5ed0e26893d1d30a63c/charset_normalizer-3.5.1-cp314-cp314-win_amd64.whl", hash = "sha256:c658c50ac0c98cd755a2dd50b7977d3bca7df401dcc47fbdfa87db53ef7d4e8b", size = 204175, upload-time = "2026-08-15T08:18:33.466Z" },
-    { url = "https://files.pythonhosted.org/packages/ac/33/eeb384dbd8dec570661354592f4f2e1b2fcc92585624d146a000caf53841/charset_normalizer-3.5.1-cp314-cp314-win_arm64.whl", hash = "sha256:4bea7f8ebe90bbd7f0e4a2de42ca6924ba23e3e76418c408ff82f1d46fabd687", size = 184123, upload-time = "2026-08-15T08:18:34.913Z" },
-    { url = "https://files.pythonhosted.org/packages/1c/6c/c73fa9d5a85f6ab05395de61c5f6984e0a9ff40bb5ff888d46dff02526c6/charset_normalizer-3.5.1-cp314-cp314t-macosx_10_15_universal2.whl", hash = "sha256:fbc597639158fd7c14d55e808718848319540f51b0e6746e3eefa59723a4a348", size = 381682, upload-time = "2026-08-15T08:18:36.349Z" },
-    { url = "https://files.pythonhosted.org/packages/30/c7/63565f860921457feba93bae6c86fb7746deb4cffeed2f375cb845318146/charset_normalizer-3.5.1-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:e71c909f353863b2b89c83de2ebed71ea6d0df8a6ef65a128193c5e650766bef", size = 240826, upload-time = "2026-08-15T08:18:37.887Z" },
-    { url = "https://files.pythonhosted.org/packages/06/ae/7ae8807410dfa33f8e6f1715740adeaafa8a816cc4cb33508f54b1f7c896/charset_normalizer-3.5.1-cp314-cp314t-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:7ac76cf9afd34929d76eb7fcb63be476a4853d8a96f0dcf2d0db68a0cbdf9885", size = 227861, upload-time = "2026-08-15T08:18:39.315Z" },
-    { url = "https://files.pythonhosted.org/packages/e9/a3/887c1642f0da26000b0e0652d91071113c0e72cea33952e225cf589f49a9/charset_normalizer-3.5.1-cp314-cp314t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:a3a370082ce34d0612f421e15fe011c53bb1feff21a26d06ad4fb244dab5a375", size = 260758, upload-time = "2026-08-15T08:18:40.88Z" },
-    { url = "https://files.pythonhosted.org/packages/3e/11/e6f5b9a3d0e55b0ef7505cd3765cdd48f22db89994c947b316f52f801fd8/charset_normalizer-3.5.1-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:256dd4d85d9e4dc595e2bc983c980e73f62ddeb3165c58b4c3dfe78c5c8548c1", size = 259950, upload-time = "2026-08-15T08:18:42.351Z" },
-    { url = "https://files.pythonhosted.org/packages/1b/ee/e4e10a94d51cd1ee638aa7e00b65399e6b2a4e8376ab6d2eac9f95586671/charset_normalizer-3.5.1-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:58d4aa13a59c969dbfdf9e6a9560e242cbfd9e8a8f50c2747714df1a423adf65", size = 249329, upload-time = "2026-08-15T08:18:43.914Z" },
-    { url = "https://files.pythonhosted.org/packages/c4/25/d5f4198819e6059735a84e8d0bfb72dc33976da67b97adcd3fb5a5e07ec6/charset_normalizer-3.5.1-cp314-cp314t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:0c6dfb5ca6723eeed15aa8e564a014d69fcb8812f94eef11fe3631e0508199f5", size = 243137, upload-time = "2026-08-15T08:18:45.368Z" },
-    { url = "https://files.pythonhosted.org/packages/a5/e9/e925ca7569cf9fb9701fd82503fee73eea5268fdb856bdd64947092d3daa/charset_normalizer-3.5.1-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:c010f5581d9c612804cc59fcf7b524b707fbcb72828551237ab545bb5c7034af", size = 242820, upload-time = "2026-08-15T08:18:46.842Z" },
-    { url = "https://files.pythonhosted.org/packages/34/17/672c251a888ed2aebcdd2fe830ad0104e25ff83c43f5c4f9c15e9fc6853c/charset_normalizer-3.5.1-cp314-cp314t-musllinux_1_2_armv7l.whl", hash = "sha256:52ec005752a56ae79547a05c0139ca2501a0c866390b6115008456b9f0e7cde1", size = 230504, upload-time = "2026-08-15T08:18:48.353Z" },
-    { url = "https://files.pythonhosted.org/packages/3f/fc/f6a85abebd42ce4da2f1db0aa56cc6a0df1995e318b3875d14401b8381d1/charset_normalizer-3.5.1-cp314-cp314t-musllinux_1_2_ppc64le.whl", hash = "sha256:2bced4061f000f7187254a02ad3433ae17eaf991747ceea2f478422590a5bba9", size = 263087, upload-time = "2026-08-15T08:18:49.859Z" },
-    { url = "https://files.pythonhosted.org/packages/98/66/7c42677e739ba66746b297e2046918d793078094dc239e1e72768cffccc6/charset_normalizer-3.5.1-cp314-cp314t-musllinux_1_2_riscv64.whl", hash = "sha256:9eea3ab2597a5e65fe65296e2d6a84570845a6b55532d90333d740d48bbc850a", size = 243269, upload-time = "2026-08-15T08:18:51.601Z" },
-    { url = "https://files.pythonhosted.org/packages/de/d8/a50b79237f417af10f8c2a501ce8d1ca87829a22e69117891ca4ba20a69e/charset_normalizer-3.5.1-cp314-cp314t-musllinux_1_2_s390x.whl", hash = "sha256:496846868fea80e479324862fa877f02411f2fd0f83b79ccee2607aa68b2a032", size = 258766, upload-time = "2026-08-15T08:18:53.23Z" },
-    { url = "https://files.pythonhosted.org/packages/2e/1d/0fc91aeaeb3c83b748f532399ce67cf84604b48297405d740000f7a9e786/charset_normalizer-3.5.1-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:85d5855daafc240cc045c026d7a15fd198a09b0fc8ff6f5ecbb5297b509cb11e", size = 250814, upload-time = "2026-08-15T08:18:54.768Z" },
-    { url = "https://files.pythonhosted.org/packages/ae/10/3d8c777cf9024615295aa1b808324ad5b4a77855869c00824bad74ffaf8a/charset_normalizer-3.5.1-cp314-cp314t-win32.whl", hash = "sha256:58d3e12c88e0950bca850ae1f7c256055c097639c2edb9eb123af9807d8b15e4", size = 191074, upload-time = "2026-08-15T08:18:56.305Z" },
-    { url = "https://files.pythonhosted.org/packages/4d/81/ae557d3c44d1a1d688696d60563413a0866a91b7ebc50f20df838be3d8c8/charset_normalizer-3.5.1-cp314-cp314t-win_amd64.whl", hash = "sha256:acaf604462bf330b0d07e7a07c1d6e4adac79e5fb13e9c5140590542cafacc00", size = 216476, upload-time = "2026-08-15T08:18:57.889Z" },
-    { url = "https://files.pythonhosted.org/packages/27/e9/61c01fb8b804692569c036b3fc50495814502dcf13a60649c6055390b02c/charset_normalizer-3.5.1-cp314-cp314t-win_arm64.whl", hash = "sha256:fdb8a068947befafba9952162645dc2fecaeb400e64584829ed5e9b2fbe21a7f", size = 194115, upload-time = "2026-08-15T08:18:59.418Z" },
-    { url = "https://files.pythonhosted.org/packages/4a/4e/8544831ef59d8f27ce92c80871380fdacc8076a8a56ed62f82e54f991333/charset_normalizer-3.5.1-cp315-cp315-macosx_10_15_universal2.whl", hash = "sha256:9085f87b0e38a2b92b8923059b4e8789fe40d9279712d15dcc670048d77079af", size = 342048, upload-time = "2026-08-15T08:19:01.054Z" },
-    { url = "https://files.pythonhosted.org/packages/7f/a6/e3b46852424246065355644f4fb6dbccc0239a42a2eee27ecfc8957f0bcd/charset_normalizer-3.5.1-cp315-cp315-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:2679de311c7946dde5d3b6f44941844133ff5c7cb86099c0061ab1e8901c20a8", size = 242997, upload-time = "2026-08-15T08:19:02.492Z" },
-    { url = "https://files.pythonhosted.org/packages/03/3b/0cc9a26777334ab2f2e3089b948bbf4e4fe72ea70b897715ef6415043ec8/charset_normalizer-3.5.1-cp315-cp315-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:baf3775a2635e5a11fbd5e4e64ee69c7e86875d224a5c72aca4c141064589a90", size = 237014, upload-time = "2026-08-15T08:19:03.943Z" },
-    { url = "https://files.pythonhosted.org/packages/8c/c2/027335f0aa337a2a2e121bac1ad88c4f02ba6053ea0926802784f3db11af/charset_normalizer-3.5.1-cp315-cp315-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:8ac8c94b6539074e0f40899301273ac8402b9b3e01c7b7ba269ff30340aaaf20", size = 266174, upload-time = "2026-08-15T08:19:05.598Z" },
-    { url = "https://files.pythonhosted.org/packages/86/d3/e367787febe4e74769dec0f406f2c3c8d1b955fce5aee1fd0f94e8367a45/charset_normalizer-3.5.1-cp315-cp315-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:8fe532b3c966d1fb794e0698e4589d0444017ae77fc0b31edea13c0e35bcc449", size = 263361, upload-time = "2026-08-15T08:19:07.251Z" },
-    { url = "https://files.pythonhosted.org/packages/af/3d/391b193eb9f3e84b02f9314088c386debdc0debee843535aaea2e2c6715d/charset_normalizer-3.5.1-cp315-cp315-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:5c84bec0ab5ae0c64bfe73a7d2adcb5ce73b467523fc27fd6a28ab2aa6cbe35a", size = 252143, upload-time = "2026-08-15T08:19:08.816Z" },
-    { url = "https://files.pythonhosted.org/packages/2e/57/de221f1745a90d418199761967e2776bfe2c275a1194220985e8c1d37833/charset_normalizer-3.5.1-cp315-cp315-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:854066be00447fa8de2ccbbe893e2ffc4b123ef16d897af794c1e18bd4a714b0", size = 252086, upload-time = "2026-08-15T08:19:10.255Z" },
-    { url = "https://files.pythonhosted.org/packages/c8/e3/d119f86a01f9331e8186175f24873b1d74a7ee9e2e4b4d68f9947dae5afd/charset_normalizer-3.5.1-cp315-cp315-musllinux_1_2_aarch64.whl", hash = "sha256:21b82d8082f6f5e7f456ef0bd16323d08de1266efbfeb476e64b2a91d1471a4e", size = 245231, upload-time = "2026-08-15T08:19:11.807Z" },
-    { url = "https://files.pythonhosted.org/packages/26/de/d8e48c135ae480879539cdb179c8d3b50c7879497d75dd899b5763b69cee/charset_normalizer-3.5.1-cp315-cp315-musllinux_1_2_armv7l.whl", hash = "sha256:838648accb3a7fd9803fd45c87bce8509648eb0c11bc34e216141300977244f2", size = 241546, upload-time = "2026-08-15T08:19:13.416Z" },
-    { url = "https://files.pythonhosted.org/packages/67/c4/217755fd1abc50d326c252922cd642002758095a81ff45010337b8b3ef65/charset_normalizer-3.5.1-cp315-cp315-musllinux_1_2_ppc64le.whl", hash = "sha256:195ce897c6153c0700078142cf8efe3e6454ca4cf4357499e4078dfd83396626", size = 267033, upload-time = "2026-08-15T08:19:14.981Z" },
-    { url = "https://files.pythonhosted.org/packages/b8/d7/34d8e404e358d2adcc5a228c2134643af00104c8fb0bf525f3688d756f05/charset_normalizer-3.5.1-cp315-cp315-musllinux_1_2_riscv64.whl", hash = "sha256:978eab16f55b4ab2c2a745be9a0a840bf8f09a7f227d9c76eb30214d078865a5", size = 252045, upload-time = "2026-08-15T08:19:16.618Z" },
-    { url = "https://files.pythonhosted.org/packages/5e/fa/40414471acf0aa0692ca77305aa00e434fcd8288f0941c93c30e9a5f8f2f/charset_normalizer-3.5.1-cp315-cp315-musllinux_1_2_s390x.whl", hash = "sha256:cc0329df4caaceb950d2f580b5ac716a377f7059624a0bafaeaf8a218c6ed774", size = 264866, upload-time = "2026-08-15T08:19:18.101Z" },
-    { url = "https://files.pythonhosted.org/packages/32/90/fcc850bae791abd2e0c041847f13e270aa08692a79f3e00de6d2dce1cb50/charset_normalizer-3.5.1-cp315-cp315-musllinux_1_2_x86_64.whl", hash = "sha256:687c9ca3035544b113bea2055e180af96fb63c0c476e22a9180f51925186e7b7", size = 253932, upload-time = "2026-08-15T08:19:19.734Z" },
-    { url = "https://files.pythonhosted.org/packages/af/af/53afe99068b3c10b4cbae592a52ef72a7c92c0188440e83ee3a078fd8f75/charset_normalizer-3.5.1-cp315-cp315-win32.whl", hash = "sha256:706bfd38730a5ac7a365793269a00f4e988178cec121391f4248d84ad8c972e9", size = 180320, upload-time = "2026-08-15T08:19:21.37Z" },
-    { url = "https://files.pythonhosted.org/packages/c9/bc/f46a132041b29e4a8779ed712d3df1bf112e94ca8de58b66d7ec2c0cf8b9/charset_normalizer-3.5.1-cp315-cp315-win_amd64.whl", hash = "sha256:92caef967d287a407085d61176fce4012b1dd62daed4eb6d5ceb26d3d2538712", size = 204174, upload-time = "2026-08-15T08:19:23.088Z" },
-    { url = "https://files.pythonhosted.org/packages/a1/5d/9ed554480eda8e447b673648628fdc29574d23dbad01fe11837adedd1cae/charset_normalizer-3.5.1-cp315-cp315-win_arm64.whl", hash = "sha256:5fc45d653ea8c9a20479167e11d4a0f8cb2fa3470737ab6f9c827532313187b7", size = 184126, upload-time = "2026-08-15T08:19:24.471Z" },
-    { url = "https://files.pythonhosted.org/packages/3b/32/9b8929bf384061ee1fe5d9c27c6f9776d3d824039ad4e14c88ec00c7808e/charset_normalizer-3.5.1-cp315-cp315t-macosx_10_15_universal2.whl", hash = "sha256:59171c6e45bf07d0d5cab3b0bf81d945035530f6873398b3b531c31184d46663", size = 381441, upload-time = "2026-08-15T08:19:26.038Z" },
-    { url = "https://files.pythonhosted.org/packages/96/10/e9aa7923d3ddac652c99a1c5f7be494e737e151566a44abe018daf757f2c/charset_normalizer-3.5.1-cp315-cp315t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:9dbdd9205662134957cf0c324f639bdc5031c0ca056e2369e238db75187c0f11", size = 241742, upload-time = "2026-08-15T08:19:27.532Z" },
-    { url = "https://files.pythonhosted.org/packages/28/53/a2d249ebddf47b889a100c0bdcb61a2f9dbb8bc24ef325cc062e4f476877/charset_normalizer-3.5.1-cp315-cp315t-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:e4b018dc5a0eee4676e38fe84a47a427816c590b93b55d9025274ec4d6ffc2dc", size = 235298, upload-time = "2026-08-15T08:19:29.274Z" },
-    { url = "https://files.pythonhosted.org/packages/7d/07/469f78af590f7d5cd48e20d8dbfa3d66deeff9ba37768c04d886b5afd45c/charset_normalizer-3.5.1-cp315-cp315t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:ced3fdd71aaa83ce593746c2edb42b7a59cb4c19c8b5c407781c72e493aae55a", size = 262500, upload-time = "2026-08-15T08:19:30.955Z" },
-    { url = "https://files.pythonhosted.org/packages/55/66/3bb56a47f7dcba014055b1a1d33c6f08bbe9c1e74dba154cfa25f90ae885/charset_normalizer-3.5.1-cp315-cp315t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:19a3dd5aa73cef1c99687c4fc57db016a9c17104ae1185da88ba566a5d3bebe4", size = 258888, upload-time = "2026-08-15T08:19:32.458Z" },
-    { url = "https://files.pythonhosted.org/packages/ff/c1/2adc2800903fb013210349313b710a5376856578d9e33e6b9a1d8b36714a/charset_normalizer-3.5.1-cp315-cp315t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:cc5d36d96478aa9c60654bd932525bf32964c62a7281eafdf16d85003a8d6004", size = 250243, upload-time = "2026-08-15T08:19:33.94Z" },
-    { url = "https://files.pythonhosted.org/packages/95/b5/a18d0dd1157ab655cc2cb14a545f4a4784bbad70ab3502412e36097502d9/charset_normalizer-3.5.1-cp315-cp315t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:04368edf83514385ffc3e1cfd4546e595f4f1272dd23ba437a93a9cc3741d47b", size = 249871, upload-time = "2026-08-15T08:19:35.413Z" },
-    { url = "https://files.pythonhosted.org/packages/ad/c3/525f508cd1e58d0450ac55ed40ac75bc3a97482c59def5278456a5fbf03c/charset_normalizer-3.5.1-cp315-cp315t-musllinux_1_2_aarch64.whl", hash = "sha256:9b5db6052055d34d41230fb78d7c439c23dc536a9896f6cb039e8dd92cfc1263", size = 243580, upload-time = "2026-08-15T08:19:36.886Z" },
-    { url = "https://files.pythonhosted.org/packages/7c/c1/49a91fe7e97c8140094ca5c64161ab623a70d9f636bf834eace14048acb5/charset_normalizer-3.5.1-cp315-cp315t-musllinux_1_2_armv7l.whl", hash = "sha256:252d099029bcbea642f2a06c4ed5046bdf8b5a8150b64afa5e027e88b106e5ee", size = 239807, upload-time = "2026-08-15T08:19:38.392Z" },
-    { url = "https://files.pythonhosted.org/packages/d3/58/56a48c296601274c4689b864a8e2dfb209b81dfcb39472753ce95eea662b/charset_normalizer-3.5.1-cp315-cp315t-musllinux_1_2_ppc64le.whl", hash = "sha256:6199d5606e2bbf2b096cf64d03f8b6790c91081d5ac866b8e7bb6422738cc60c", size = 264083, upload-time = "2026-08-15T08:19:39.856Z" },
-    { url = "https://files.pythonhosted.org/packages/10/4c/dc48409274a1817ff349711d26c62aa0c597df865d4d69ef79160c859193/charset_normalizer-3.5.1-cp315-cp315t-musllinux_1_2_riscv64.whl", hash = "sha256:77efcff2b23071c349402ac1066667a3d011f62398d81408c9b88ad991747c9e", size = 250317, upload-time = "2026-08-15T08:19:41.53Z" },
-    { url = "https://files.pythonhosted.org/packages/81/58/d325912115caec62d6bdd77bbab5e0b7da5d234a9f20affdffcbcb530d0b/charset_normalizer-3.5.1-cp315-cp315t-musllinux_1_2_s390x.whl", hash = "sha256:a5cbd90ecf0fc62e64726917ad083b73001f0563657a87ec3c0b504e277dc90d", size = 258173, upload-time = "2026-08-15T08:19:43.07Z" },
-    { url = "https://files.pythonhosted.org/packages/34/f7/b13b1ccae2c8ec63980d13be1890eb73f8aeabbfce02a24aabc0908788f5/charset_normalizer-3.5.1-cp315-cp315t-musllinux_1_2_x86_64.whl", hash = "sha256:4d26f14f041e83dd8edfd61f4cd4fa7285d31798b5bf1f28e70c367ba6c41d61", size = 251960, upload-time = "2026-08-15T08:19:44.587Z" },
-    { url = "https://files.pythonhosted.org/packages/1e/25/ed3f9919c5aef8cc818be1f972f565f7610d7b2076b8ebb98839516ffc3c/charset_normalizer-3.5.1-cp315-cp315t-win32.whl", hash = "sha256:ac13b004224fb341e1e25a1ed5e19d32f57cdb2a403e01f003b46f051a550f6f", size = 191186, upload-time = "2026-08-15T08:19:46.293Z" },
-    { url = "https://files.pythonhosted.org/packages/69/d5/43c2b3e9d8267092b913eb8b0603f0f71993c395632886bd37a7223f96cf/charset_normalizer-3.5.1-cp315-cp315t-win_amd64.whl", hash = "sha256:35aea775dc2bd5f54cd84a1cd2696cc3207c479cb9cf0bd346f0d343e4300ddb", size = 215947, upload-time = "2026-08-15T08:19:47.853Z" },
-    { url = "https://files.pythonhosted.org/packages/a8/76/9aad3e9c8865e5e0efa9a7f6f81c37a67635a985145ecd44528a81e088ee/charset_normalizer-3.5.1-cp315-cp315t-win_arm64.whl", hash = "sha256:fb78f6e7fcd8ad785d28cd577168bc1aaee827b25bb8755638f694794ea98f0a", size = 193909, upload-time = "2026-08-15T08:19:49.383Z" },
-    { url = "https://files.pythonhosted.org/packages/5b/97/fb4e82231aba271ffd775a1b4993b0defc4e3059f286ae41d9433409fe85/charset_normalizer-3.5.1-cp37-abi3-macosx_10_9_universal2.whl", hash = "sha256:41876ee62a3dddf48ff1121ad8f0798032aa03f2fd35f21f34a4cab14f18d8d2", size = 331467, upload-time = "2026-08-15T08:19:50.959Z" },
-    { url = "https://files.pythonhosted.org/packages/9f/2f/fe3f187327aac18e2d54e9d2b08e15d27bf9b642d9e51c219f130fc34d1a/charset_normalizer-3.5.1-cp37-abi3-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:a6dac12ff6b846103483683f60c5f8fee205121adc58ffd87e90a90a3af69e99", size = 253057, upload-time = "2026-08-15T08:19:52.654Z" },
-    { url = "https://files.pythonhosted.org/packages/d7/c7/9e48cee5c161fe24da823b61bf381921d77cb994a0a4de148e95018c1984/charset_normalizer-3.5.1-cp37-abi3-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:cee5dd7c6fb5dd52a0fe2a740f9bc6e3593f5f8b1788bde49de02086f30182b2", size = 240930, upload-time = "2026-08-15T08:19:54.163Z" },
-    { url = "https://files.pythonhosted.org/packages/49/e0/716601f3cc69be7b198951150c75ead1ece33c3c8036ff6ffa46029659a0/charset_normalizer-3.5.1-cp37-abi3-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:343fb4f2821043bd87095f7b08a1a181febc8e36ac64212143bbfd0a0e1bc235", size = 230822, upload-time = "2026-08-15T08:19:55.807Z" },
-    { url = "https://files.pythonhosted.org/packages/d3/05/71bfc5caa0abcc45aea1f6a4d50ac68e59605ddc7666fe8494f4cd229665/charset_normalizer-3.5.1-cp37-abi3-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:ae4a097991662cd4fff0ddc74e0fe7874f82e00042fa0ea00855645ed0c79598", size = 260037, upload-time = "2026-08-15T08:19:57.312Z" },
-    { url = "https://files.pythonhosted.org/packages/c3/92/de7e32ed05341e7a9c4c877c318418197b7f2d66a3b68d561bf2ac57ca3e/charset_normalizer-3.5.1-cp37-abi3-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:4b599739b93b2cbeded49645ae3c8d1405c29ddfbceac1545c87a3f9580a9e96", size = 255097, upload-time = "2026-08-15T08:19:59.056Z" },
-    { url = "https://files.pythonhosted.org/packages/f5/7b/ade0a122600319dfa0b1000ab0f9731c94a817904cf3c5de408c73a4ede7/charset_normalizer-3.5.1-cp37-abi3-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:b39b69b347e5e47a3b5b8cfc005c68c1ba347474e3960236c4944a8ecd174962", size = 250166, upload-time = "2026-08-15T08:20:00.612Z" },
-    { url = "https://files.pythonhosted.org/packages/75/9c/019fbb9f4834491a160951349b1a3714439376f66e5f7cf18b4f18f0c7aa/charset_normalizer-3.5.1-cp37-abi3-musllinux_1_2_aarch64.whl", hash = "sha256:a2028475ba855475b8b4d3cfeb4994269c967aea8b9892dfba907f4263a863a3", size = 241821, upload-time = "2026-08-15T08:20:02.321Z" },
-    { url = "https://files.pythonhosted.org/packages/2b/b8/11d4840bfc99330cc7fbcc2681ee5a044553a6e77655508d8f9b2bff7b34/charset_normalizer-3.5.1-cp37-abi3-musllinux_1_2_armv7l.whl", hash = "sha256:36047af20e17097c3bb9476c2b7655f2f7aa51322c0ba58c07695bedf755a950", size = 232529, upload-time = "2026-08-15T08:20:04.008Z" },
-    { url = "https://files.pythonhosted.org/packages/18/96/2b3a21492d9f65171ac75d872f5018260013d00bfa0ff70ec9f179148cbd/charset_normalizer-3.5.1-cp37-abi3-musllinux_1_2_ppc64le.whl", hash = "sha256:4c4fb141a727957c93edfe5c32a26ceb6b5f6461d67146e2d39f51e16170bea8", size = 260348, upload-time = "2026-08-15T08:20:05.877Z" },
-    { url = "https://files.pythonhosted.org/packages/d6/aa/a69a2028e8bd052476c245460ab19d7de595de084dd968f2d75cd50c3e25/charset_normalizer-3.5.1-cp37-abi3-musllinux_1_2_riscv64.whl", hash = "sha256:2f293479cce755c75f1697e87c409b7ae4c555c7dfecb6e988ad13abba943031", size = 247234, upload-time = "2026-08-15T08:20:07.487Z" },
-    { url = "https://files.pythonhosted.org/packages/35/8a/3d130aeabcaf3d2466af76b7b141c08d9e89c9016ab4b7cdd0f7dc2d1c62/charset_normalizer-3.5.1-cp37-abi3-musllinux_1_2_s390x.whl", hash = "sha256:3588e376b3ea2eea84976f67273d679f229e24c66dce7b82ae45aef04ff6e072", size = 256917, upload-time = "2026-08-15T08:20:09.142Z" },
-    { url = "https://files.pythonhosted.org/packages/80/c2/a7379b840292d0c1ab9fbd17d1f3967aa81794dc95bc74be8999d7fedcf7/charset_normalizer-3.5.1-cp37-abi3-musllinux_1_2_x86_64.whl", hash = "sha256:e199fb99720074809a7720f1c0b4d919eea8b87e88713e0f8f602f7bef543d9d", size = 254846, upload-time = "2026-08-15T08:20:10.727Z" },
-    { url = "https://files.pythonhosted.org/packages/01/65/d43b714731bb2f40d4053dfa00ecfc1c5a301f8e3316c5db3a09af59fe94/charset_normalizer-3.5.1-cp37-abi3-win32.whl", hash = "sha256:dd732602a7009217f658d5863d12d79d373a4de0eebc111094bcdd3bb8e0a6cc", size = 174216, upload-time = "2026-08-15T08:20:12.334Z" },
-    { url = "https://files.pythonhosted.org/packages/35/4f/b911ed898b26a09789eba9c9200c999aff6c61b4bafaf4838e56d1a1e1a3/charset_normalizer-3.5.1-cp37-abi3-win_amd64.whl", hash = "sha256:70055ff39b97c99e7ae40ea3e393fb62aa2e44dbd9b29f8d14f42fb0025c3959", size = 199764, upload-time = "2026-08-15T08:20:13.908Z" },
-    { url = "https://files.pythonhosted.org/packages/f0/a7/920baf467bfd9bf689f3b318340f37aee4572a71f162bd8db51da55ba4fa/charset_normalizer-3.5.1-cp37-abi3-win_arm64.whl", hash = "sha256:87e4f41d375c0b9be2fb5251aee4b8a689169e134535aed81bf085c3b647451e", size = 287318, upload-time = "2026-08-15T08:20:15.551Z" },
-    { url = "https://files.pythonhosted.org/packages/cc/61/d01fc49b8dea277640b55a9e15960dbca9fdc8c9fde18e572d39c59f4019/charset_normalizer-3.5.1-py3-none-any.whl", hash = "sha256:6df0ec430f9a831772c23ca5a224cba36517a58a84bb32c32bb59a9fa67c47f6", size = 68658, upload-time = "2026-08-15T08:20:43.306Z" },
-]
-
-[[package]]
-name = "click"
-version = "8.4.2"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "colorama", marker = "sys_platform == 'win32'" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/76/d4/81420972a676e8ffea40450d8c8c92943e7218a78fe9b64359836cc9876b/click-8.4.2.tar.gz", hash = "sha256:9a6cea6e60b17ebe0a44c5cc636d94f09bd66142c1cd7d8b4cd731c4917a15f6", size = 338000, upload-time = "2026-06-24T17:45:15.148Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/fb/e2/79c688af8b210d232694e31e59da9f6ec747bae31c3f5946e4e9b98860d5/click-8.4.2-py3-none-any.whl", hash = "sha256:e6f9f66136c816745b9d65817da91d61d957fb16e02e4dcd0552553c5a197b76", size = 119243, upload-time = "2026-06-24T17:45:13.73Z" },
-]
-
-[[package]]
-name = "cognitive-loop-engine"
-version = "0.1.0"
-source = { editable = "." }
-dependencies = [
-    { name = "litellm" },
-    { name = "pydantic" },
-    { name = "python-telegram-bot" },
-    { name = "pyyaml" },
-    { name = "watchdog" },
-]
-
-[package.optional-dependencies]
-dev = [
-    { name = "pytest" },
-]
-
-[package.metadata]
-requires-dist = [
-    { name = "litellm", specifier = ">=1.0" },
-    { name = "pydantic", specifier = ">=2.0" },
-    { name = "pytest", marker = "extra == 'dev'", specifier = ">=8.0" },
-    { name = "python-telegram-bot", specifier = ">=21.0" },
-    { name = "pyyaml", specifier = ">=6.0" },
-    { name = "watchdog", specifier = ">=4.0" },
-]
-provides-extras = ["dev"]
-
-[[package]]
-name = "colorama"
-version = "0.4.6"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/d8/53/6f443c9a4a8358a93a6792e2acffb9d9d5cb0a5cfd8802644b7b1c9a02e4/colorama-0.4.6.tar.gz", hash = "sha256:08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44", size = 27697, upload-time = "2022-10-25T02:36:22.414Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/d1/d6/3965ed04c63042e047cb6a3e6ed1a63a35087b6a609aa3a15ed8ac56c221/colorama-0.4.6-py2.py3-none-any.whl", hash = "sha256:4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6", size = 25335, upload-time = "2022-10-25T02:36:20.889Z" },
-]
-
-[[package]]
-name = "distro"
-version = "1.9.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/fc/f8/98eea607f65de6527f8a2e8885fc8015d3e6f5775df186e443e0964a11c3/distro-1.9.0.tar.gz", hash = "sha256:2fa77c6fd8940f116ee1d6b94a2f90b13b5ea8d019b98bc8bafdcabcdd9bdbed", size = 60722, upload-time = "2023-12-24T09:54:32.31Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/12/b3/231ffd4ab1fc9d679809f356cebee130ac7daa00d6d6f3206dd4fd137e9e/distro-1.9.0-py3-none-any.whl", hash = "sha256:7bffd925d65168f85027d8da9af6bddab658135b840670a223589bc0c8ef02b2", size = 20277, upload-time = "2023-12-24T09:54:30.421Z" },
-]
-
-[[package]]
-name = "fastuuid"
-version = "0.14.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/c3/7d/d9daedf0f2ebcacd20d599928f8913e9d2aea1d56d2d355a93bfa2b611d7/fastuuid-0.14.0.tar.gz", hash = "sha256:178947fc2f995b38497a74172adee64fdeb8b7ec18f2a5934d037641ba265d26", size = 18232, upload-time = "2025-10-19T22:19:22.402Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/02/a2/e78fcc5df65467f0d207661b7ef86c5b7ac62eea337c0c0fcedbeee6fb13/fastuuid-0.14.0-cp312-cp312-macosx_10_12_x86_64.macosx_11_0_arm64.macosx_10_12_universal2.whl", hash = "sha256:77e94728324b63660ebf8adb27055e92d2e4611645bf12ed9d88d30486471d0a", size = 510164, upload-time = "2025-10-19T22:31:45.635Z" },
-    { url = "https://files.pythonhosted.org/packages/2b/b3/c846f933f22f581f558ee63f81f29fa924acd971ce903dab1a9b6701816e/fastuuid-0.14.0-cp312-cp312-macosx_10_12_x86_64.whl", hash = "sha256:caa1f14d2102cb8d353096bc6ef6c13b2c81f347e6ab9d6fbd48b9dea41c153d", size = 261837, upload-time = "2025-10-19T22:38:38.53Z" },
-    { url = "https://files.pythonhosted.org/packages/54/ea/682551030f8c4fa9a769d9825570ad28c0c71e30cf34020b85c1f7ee7382/fastuuid-0.14.0-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:d23ef06f9e67163be38cece704170486715b177f6baae338110983f99a72c070", size = 251370, upload-time = "2025-10-19T22:40:26.07Z" },
-    { url = "https://files.pythonhosted.org/packages/14/dd/5927f0a523d8e6a76b70968e6004966ee7df30322f5fc9b6cdfb0276646a/fastuuid-0.14.0-cp312-cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:0c9ec605ace243b6dbe3bd27ebdd5d33b00d8d1d3f580b39fdd15cd96fd71796", size = 277766, upload-time = "2025-10-19T22:37:23.779Z" },
-    { url = "https://files.pythonhosted.org/packages/16/6e/c0fb547eef61293153348f12e0f75a06abb322664b34a1573a7760501336/fastuuid-0.14.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:808527f2407f58a76c916d6aa15d58692a4a019fdf8d4c32ac7ff303b7d7af09", size = 278105, upload-time = "2025-10-19T22:26:56.821Z" },
-    { url = "https://files.pythonhosted.org/packages/2d/b1/b9c75e03b768f61cf2e84ee193dc18601aeaf89a4684b20f2f0e9f52b62c/fastuuid-0.14.0-cp312-cp312-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:2fb3c0d7fef6674bbeacdd6dbd386924a7b60b26de849266d1ff6602937675c8", size = 301564, upload-time = "2025-10-19T22:30:31.604Z" },
-    { url = "https://files.pythonhosted.org/packages/fc/fa/f7395fdac07c7a54f18f801744573707321ca0cee082e638e36452355a9d/fastuuid-0.14.0-cp312-cp312-musllinux_1_1_aarch64.whl", hash = "sha256:ab3f5d36e4393e628a4df337c2c039069344db5f4b9d2a3c9cea48284f1dd741", size = 459659, upload-time = "2025-10-19T22:31:32.341Z" },
-    { url = "https://files.pythonhosted.org/packages/66/49/c9fd06a4a0b1f0f048aacb6599e7d96e5d6bc6fa680ed0d46bf111929d1b/fastuuid-0.14.0-cp312-cp312-musllinux_1_1_i686.whl", hash = "sha256:b9a0ca4f03b7e0b01425281ffd44e99d360e15c895f1907ca105854ed85e2057", size = 478430, upload-time = "2025-10-19T22:26:22.962Z" },
-    { url = "https://files.pythonhosted.org/packages/be/9c/909e8c95b494e8e140e8be6165d5fc3f61fdc46198c1554df7b3e1764471/fastuuid-0.14.0-cp312-cp312-musllinux_1_1_x86_64.whl", hash = "sha256:3acdf655684cc09e60fb7e4cf524e8f42ea760031945aa8086c7eae2eeeabeb8", size = 450894, upload-time = "2025-10-19T22:27:01.647Z" },
-    { url = "https://files.pythonhosted.org/packages/90/eb/d29d17521976e673c55ef7f210d4cdd72091a9ec6755d0fd4710d9b3c871/fastuuid-0.14.0-cp312-cp312-win32.whl", hash = "sha256:9579618be6280700ae36ac42c3efd157049fe4dd40ca49b021280481c78c3176", size = 154374, upload-time = "2025-10-19T22:29:19.879Z" },
-    { url = "https://files.pythonhosted.org/packages/cc/fc/f5c799a6ea6d877faec0472d0b27c079b47c86b1cdc577720a5386483b36/fastuuid-0.14.0-cp312-cp312-win_amd64.whl", hash = "sha256:d9e4332dc4ba054434a9594cbfaf7823b57993d7d8e7267831c3e059857cf397", size = 156550, upload-time = "2025-10-19T22:27:49.658Z" },
-    { url = "https://files.pythonhosted.org/packages/a5/83/ae12dd39b9a39b55d7f90abb8971f1a5f3c321fd72d5aa83f90dc67fe9ed/fastuuid-0.14.0-cp313-cp313-macosx_10_12_x86_64.macosx_11_0_arm64.macosx_10_12_universal2.whl", hash = "sha256:77a09cb7427e7af74c594e409f7731a0cf887221de2f698e1ca0ebf0f3139021", size = 510720, upload-time = "2025-10-19T22:42:34.633Z" },
-    { url = "https://files.pythonhosted.org/packages/53/b0/a4b03ff5d00f563cc7546b933c28cb3f2a07344b2aec5834e874f7d44143/fastuuid-0.14.0-cp313-cp313-macosx_10_12_x86_64.whl", hash = "sha256:9bd57289daf7b153bfa3e8013446aa144ce5e8c825e9e366d455155ede5ea2dc", size = 262024, upload-time = "2025-10-19T22:30:25.482Z" },
-    { url = "https://files.pythonhosted.org/packages/9c/6d/64aee0a0f6a58eeabadd582e55d0d7d70258ffdd01d093b30c53d668303b/fastuuid-0.14.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:ac60fc860cdf3c3f327374db87ab8e064c86566ca8c49d2e30df15eda1b0c2d5", size = 251679, upload-time = "2025-10-19T22:36:14.096Z" },
-    { url = "https://files.pythonhosted.org/packages/60/f5/a7e9cda8369e4f7919d36552db9b2ae21db7915083bc6336f1b0082c8b2e/fastuuid-0.14.0-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:ab32f74bd56565b186f036e33129da77db8be09178cd2f5206a5d4035fb2a23f", size = 277862, upload-time = "2025-10-19T22:36:23.302Z" },
-    { url = "https://files.pythonhosted.org/packages/f0/d3/8ce11827c783affffd5bd4d6378b28eb6cc6d2ddf41474006b8d62e7448e/fastuuid-0.14.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:33e678459cf4addaedd9936bbb038e35b3f6b2061330fd8f2f6a1d80414c0f87", size = 278278, upload-time = "2025-10-19T22:29:43.809Z" },
-    { url = "https://files.pythonhosted.org/packages/a2/51/680fb6352d0bbade04036da46264a8001f74b7484e2fd1f4da9e3db1c666/fastuuid-0.14.0-cp313-cp313-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:1e3cc56742f76cd25ecb98e4b82a25f978ccffba02e4bdce8aba857b6d85d87b", size = 301788, upload-time = "2025-10-19T22:36:06.825Z" },
-    { url = "https://files.pythonhosted.org/packages/fa/7c/2014b5785bd8ebdab04ec857635ebd84d5ee4950186a577db9eff0fb8ff6/fastuuid-0.14.0-cp313-cp313-musllinux_1_1_aarch64.whl", hash = "sha256:cb9a030f609194b679e1660f7e32733b7a0f332d519c5d5a6a0a580991290022", size = 459819, upload-time = "2025-10-19T22:35:31.623Z" },
-    { url = "https://files.pythonhosted.org/packages/01/d2/524d4ceeba9160e7a9bc2ea3e8f4ccf1ad78f3bde34090ca0c51f09a5e91/fastuuid-0.14.0-cp313-cp313-musllinux_1_1_i686.whl", hash = "sha256:09098762aad4f8da3a888eb9ae01c84430c907a297b97166b8abc07b640f2995", size = 478546, upload-time = "2025-10-19T22:26:03.023Z" },
-    { url = "https://files.pythonhosted.org/packages/bc/17/354d04951ce114bf4afc78e27a18cfbd6ee319ab1829c2d5fb5e94063ac6/fastuuid-0.14.0-cp313-cp313-musllinux_1_1_x86_64.whl", hash = "sha256:1383fff584fa249b16329a059c68ad45d030d5a4b70fb7c73a08d98fd53bcdab", size = 450921, upload-time = "2025-10-19T22:31:02.151Z" },
-    { url = "https://files.pythonhosted.org/packages/fb/be/d7be8670151d16d88f15bb121c5b66cdb5ea6a0c2a362d0dcf30276ade53/fastuuid-0.14.0-cp313-cp313-win32.whl", hash = "sha256:a0809f8cc5731c066c909047f9a314d5f536c871a7a22e815cc4967c110ac9ad", size = 154559, upload-time = "2025-10-19T22:36:36.011Z" },
-    { url = "https://files.pythonhosted.org/packages/22/1d/5573ef3624ceb7abf4a46073d3554e37191c868abc3aecd5289a72f9810a/fastuuid-0.14.0-cp313-cp313-win_amd64.whl", hash = "sha256:0df14e92e7ad3276327631c9e7cec09e32572ce82089c55cb1bb8df71cf394ed", size = 156539, upload-time = "2025-10-19T22:33:35.898Z" },
-    { url = "https://files.pythonhosted.org/packages/16/c9/8c7660d1fe3862e3f8acabd9be7fc9ad71eb270f1c65cce9a2b7a31329ab/fastuuid-0.14.0-cp314-cp314-macosx_10_12_x86_64.macosx_11_0_arm64.macosx_10_12_universal2.whl", hash = "sha256:b852a870a61cfc26c884af205d502881a2e59cc07076b60ab4a951cc0c94d1ad", size = 510600, upload-time = "2025-10-19T22:43:44.17Z" },
-    { url = "https://files.pythonhosted.org/packages/4c/f4/a989c82f9a90d0ad995aa957b3e572ebef163c5299823b4027986f133dfb/fastuuid-0.14.0-cp314-cp314-macosx_10_12_x86_64.whl", hash = "sha256:c7502d6f54cd08024c3ea9b3514e2d6f190feb2f46e6dbcd3747882264bb5f7b", size = 262069, upload-time = "2025-10-19T22:43:38.38Z" },
-    { url = "https://files.pythonhosted.org/packages/da/6c/a1a24f73574ac995482b1326cf7ab41301af0fabaa3e37eeb6b3df00e6e2/fastuuid-0.14.0-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:1ca61b592120cf314cfd66e662a5b54a578c5a15b26305e1b8b618a6f22df714", size = 251543, upload-time = "2025-10-19T22:32:22.537Z" },
-    { url = "https://files.pythonhosted.org/packages/1a/20/2a9b59185ba7a6c7b37808431477c2d739fcbdabbf63e00243e37bd6bf49/fastuuid-0.14.0-cp314-cp314-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:aa75b6657ec129d0abded3bec745e6f7ab642e6dba3a5272a68247e85f5f316f", size = 277798, upload-time = "2025-10-19T22:33:53.821Z" },
-    { url = "https://files.pythonhosted.org/packages/ef/33/4105ca574f6ded0af6a797d39add041bcfb468a1255fbbe82fcb6f592da2/fastuuid-0.14.0-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:a8a0dfea3972200f72d4c7df02c8ac70bad1bb4c58d7e0ec1e6f341679073a7f", size = 278283, upload-time = "2025-10-19T22:29:02.812Z" },
-    { url = "https://files.pythonhosted.org/packages/fe/8c/fca59f8e21c4deb013f574eae05723737ddb1d2937ce87cb2a5d20992dc3/fastuuid-0.14.0-cp314-cp314-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:1bf539a7a95f35b419f9ad105d5a8a35036df35fdafae48fb2fd2e5f318f0d75", size = 301627, upload-time = "2025-10-19T22:35:54.985Z" },
-    { url = "https://files.pythonhosted.org/packages/cb/e2/f78c271b909c034d429218f2798ca4e89eeda7983f4257d7865976ddbb6c/fastuuid-0.14.0-cp314-cp314-musllinux_1_1_aarch64.whl", hash = "sha256:9a133bf9cc78fdbd1179cb58a59ad0100aa32d8675508150f3658814aeefeaa4", size = 459778, upload-time = "2025-10-19T22:28:00.999Z" },
-    { url = "https://files.pythonhosted.org/packages/1e/f0/5ff209d865897667a2ff3e7a572267a9ced8f7313919f6d6043aed8b1caa/fastuuid-0.14.0-cp314-cp314-musllinux_1_1_i686.whl", hash = "sha256:f54d5b36c56a2d5e1a31e73b950b28a0d83eb0c37b91d10408875a5a29494bad", size = 478605, upload-time = "2025-10-19T22:36:21.764Z" },
-    { url = "https://files.pythonhosted.org/packages/e0/c8/2ce1c78f983a2c4987ea865d9516dbdfb141a120fd3abb977ae6f02ba7ca/fastuuid-0.14.0-cp314-cp314-musllinux_1_1_x86_64.whl", hash = "sha256:ec27778c6ca3393ef662e2762dba8af13f4ec1aaa32d08d77f71f2a70ae9feb8", size = 450837, upload-time = "2025-10-19T22:34:37.178Z" },
-    { url = "https://files.pythonhosted.org/packages/df/60/dad662ec9a33b4a5fe44f60699258da64172c39bd041da2994422cdc40fe/fastuuid-0.14.0-cp314-cp314-win32.whl", hash = "sha256:e23fc6a83f112de4be0cc1990e5b127c27663ae43f866353166f87df58e73d06", size = 154532, upload-time = "2025-10-19T22:35:18.217Z" },
-    { url = "https://files.pythonhosted.org/packages/1f/f6/da4db31001e854025ffd26bc9ba0740a9cbba2c3259695f7c5834908b336/fastuuid-0.14.0-cp314-cp314-win_amd64.whl", hash = "sha256:df61342889d0f5e7a32f7284e55ef95103f2110fee433c2ae7c2c0956d76ac8a", size = 156457, upload-time = "2025-10-19T22:33:44.579Z" },
-]
-
-[[package]]
-name = "filelock"
-version = "3.32.4"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/6d/30/03b03951873a1a0ffc7e8ca0e10c15597b59e8d0e39260704cd2ea087bc4/filelock-3.32.4.tar.gz", hash = "sha256:2bde2e4cf732e0153406d8a7bc80620ecf5e621fe0d25e41143c4e3b4733ff30", size = 222126, upload-time = "2026-08-23T17:37:55.363Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/01/a4/9b63d595d748e3aff8812b65eacc1a2c4bd90b7c2012e08e72373b4835eb/filelock-3.32.4-py3-none-any.whl", hash = "sha256:22e58ca3b1ae3b98993b762d7338367ae64fe50252bf78d59da3bfebcdf1cedd", size = 99864, upload-time = "2026-08-23T17:37:53.913Z" },
-]
-
-[[package]]
-name = "frozenlist"
-version = "1.8.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/2d/f5/c831fac6cc817d26fd54c7eaccd04ef7e0288806943f7cc5bbf69f3ac1f0/frozenlist-1.8.0.tar.gz", hash = "sha256:3ede829ed8d842f6cd48fc7081d7a41001a56f1f38603f9d49bf3020d59a31ad", size = 45875, upload-time = "2025-10-06T05:38:17.865Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/69/29/948b9aa87e75820a38650af445d2ef2b6b8a6fab1a23b6bb9e4ef0be2d59/frozenlist-1.8.0-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:78f7b9e5d6f2fdb88cdde9440dc147259b62b9d3b019924def9f6478be254ac1", size = 87782, upload-time = "2025-10-06T05:36:06.649Z" },
-    { url = "https://files.pythonhosted.org/packages/64/80/4f6e318ee2a7c0750ed724fa33a4bdf1eacdc5a39a7a24e818a773cd91af/frozenlist-1.8.0-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:229bf37d2e4acdaf808fd3f06e854a4a7a3661e871b10dc1f8f1896a3b05f18b", size = 50594, upload-time = "2025-10-06T05:36:07.69Z" },
-    { url = "https://files.pythonhosted.org/packages/2b/94/5c8a2b50a496b11dd519f4a24cb5496cf125681dd99e94c604ccdea9419a/frozenlist-1.8.0-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:f833670942247a14eafbb675458b4e61c82e002a148f49e68257b79296e865c4", size = 50448, upload-time = "2025-10-06T05:36:08.78Z" },
-    { url = "https://files.pythonhosted.org/packages/6a/bd/d91c5e39f490a49df14320f4e8c80161cfcce09f1e2cde1edd16a551abb3/frozenlist-1.8.0-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:494a5952b1c597ba44e0e78113a7266e656b9794eec897b19ead706bd7074383", size = 242411, upload-time = "2025-10-06T05:36:09.801Z" },
-    { url = "https://files.pythonhosted.org/packages/8f/83/f61505a05109ef3293dfb1ff594d13d64a2324ac3482be2cedc2be818256/frozenlist-1.8.0-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:96f423a119f4777a4a056b66ce11527366a8bb92f54e541ade21f2374433f6d4", size = 243014, upload-time = "2025-10-06T05:36:11.394Z" },
-    { url = "https://files.pythonhosted.org/packages/d8/cb/cb6c7b0f7d4023ddda30cf56b8b17494eb3a79e3fda666bf735f63118b35/frozenlist-1.8.0-cp312-cp312-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:3462dd9475af2025c31cc61be6652dfa25cbfb56cbbf52f4ccfe029f38decaf8", size = 234909, upload-time = "2025-10-06T05:36:12.598Z" },
-    { url = "https://files.pythonhosted.org/packages/31/c5/cd7a1f3b8b34af009fb17d4123c5a778b44ae2804e3ad6b86204255f9ec5/frozenlist-1.8.0-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:c4c800524c9cd9bac5166cd6f55285957fcfc907db323e193f2afcd4d9abd69b", size = 250049, upload-time = "2025-10-06T05:36:14.065Z" },
-    { url = "https://files.pythonhosted.org/packages/c0/01/2f95d3b416c584a1e7f0e1d6d31998c4a795f7544069ee2e0962a4b60740/frozenlist-1.8.0-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:d6a5df73acd3399d893dafc71663ad22534b5aa4f94e8a2fabfe856c3c1b6a52", size = 256485, upload-time = "2025-10-06T05:36:15.39Z" },
-    { url = "https://files.pythonhosted.org/packages/ce/03/024bf7720b3abaebcff6d0793d73c154237b85bdf67b7ed55e5e9596dc9a/frozenlist-1.8.0-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:405e8fe955c2280ce66428b3ca55e12b3c4e9c336fb2103a4937e891c69a4a29", size = 237619, upload-time = "2025-10-06T05:36:16.558Z" },
-    { url = "https://files.pythonhosted.org/packages/69/fa/f8abdfe7d76b731f5d8bd217827cf6764d4f1d9763407e42717b4bed50a0/frozenlist-1.8.0-cp312-cp312-musllinux_1_2_armv7l.whl", hash = "sha256:908bd3f6439f2fef9e85031b59fd4f1297af54415fb60e4254a95f75b3cab3f3", size = 250320, upload-time = "2025-10-06T05:36:17.821Z" },
-    { url = "https://files.pythonhosted.org/packages/f5/3c/b051329f718b463b22613e269ad72138cc256c540f78a6de89452803a47d/frozenlist-1.8.0-cp312-cp312-musllinux_1_2_ppc64le.whl", hash = "sha256:294e487f9ec720bd8ffcebc99d575f7eff3568a08a253d1ee1a0378754b74143", size = 246820, upload-time = "2025-10-06T05:36:19.046Z" },
-    { url = "https://files.pythonhosted.org/packages/0f/ae/58282e8f98e444b3f4dd42448ff36fa38bef29e40d40f330b22e7108f565/frozenlist-1.8.0-cp312-cp312-musllinux_1_2_s390x.whl", hash = "sha256:74c51543498289c0c43656701be6b077f4b265868fa7f8a8859c197006efb608", size = 250518, upload-time = "2025-10-06T05:36:20.763Z" },
-    { url = "https://files.pythonhosted.org/packages/8f/96/007e5944694d66123183845a106547a15944fbbb7154788cbf7272789536/frozenlist-1.8.0-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:776f352e8329135506a1d6bf16ac3f87bc25b28e765949282dcc627af36123aa", size = 239096, upload-time = "2025-10-06T05:36:22.129Z" },
-    { url = "https://files.pythonhosted.org/packages/66/bb/852b9d6db2fa40be96f29c0d1205c306288f0684df8fd26ca1951d461a56/frozenlist-1.8.0-cp312-cp312-win32.whl", hash = "sha256:433403ae80709741ce34038da08511d4a77062aa924baf411ef73d1146e74faf", size = 39985, upload-time = "2025-10-06T05:36:23.661Z" },
-    { url = "https://files.pythonhosted.org/packages/b8/af/38e51a553dd66eb064cdf193841f16f077585d4d28394c2fa6235cb41765/frozenlist-1.8.0-cp312-cp312-win_amd64.whl", hash = "sha256:34187385b08f866104f0c0617404c8eb08165ab1272e884abc89c112e9c00746", size = 44591, upload-time = "2025-10-06T05:36:24.958Z" },
-    { url = "https://files.pythonhosted.org/packages/a7/06/1dc65480ab147339fecc70797e9c2f69d9cea9cf38934ce08df070fdb9cb/frozenlist-1.8.0-cp312-cp312-win_arm64.whl", hash = "sha256:fe3c58d2f5db5fbd18c2987cba06d51b0529f52bc3a6cdc33d3f4eab725104bd", size = 40102, upload-time = "2025-10-06T05:36:26.333Z" },
-    { url = "https://files.pythonhosted.org/packages/2d/40/0832c31a37d60f60ed79e9dfb5a92e1e2af4f40a16a29abcc7992af9edff/frozenlist-1.8.0-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:8d92f1a84bb12d9e56f818b3a746f3efba93c1b63c8387a73dde655e1e42282a", size = 85717, upload-time = "2025-10-06T05:36:27.341Z" },
-    { url = "https://files.pythonhosted.org/packages/30/ba/b0b3de23f40bc55a7057bd38434e25c34fa48e17f20ee273bbde5e0650f3/frozenlist-1.8.0-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:96153e77a591c8adc2ee805756c61f59fef4cf4073a9275ee86fe8cba41241f7", size = 49651, upload-time = "2025-10-06T05:36:28.855Z" },
-    { url = "https://files.pythonhosted.org/packages/0c/ab/6e5080ee374f875296c4243c381bbdef97a9ac39c6e3ce1d5f7d42cb78d6/frozenlist-1.8.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:f21f00a91358803399890ab167098c131ec2ddd5f8f5fd5fe9c9f2c6fcd91e40", size = 49417, upload-time = "2025-10-06T05:36:29.877Z" },
-    { url = "https://files.pythonhosted.org/packages/d5/4e/e4691508f9477ce67da2015d8c00acd751e6287739123113a9fca6f1604e/frozenlist-1.8.0-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:fb30f9626572a76dfe4293c7194a09fb1fe93ba94c7d4f720dfae3b646b45027", size = 234391, upload-time = "2025-10-06T05:36:31.301Z" },
-    { url = "https://files.pythonhosted.org/packages/40/76/c202df58e3acdf12969a7895fd6f3bc016c642e6726aa63bd3025e0fc71c/frozenlist-1.8.0-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:eaa352d7047a31d87dafcacbabe89df0aa506abb5b1b85a2fb91bc3faa02d822", size = 233048, upload-time = "2025-10-06T05:36:32.531Z" },
-    { url = "https://files.pythonhosted.org/packages/f9/c0/8746afb90f17b73ca5979c7a3958116e105ff796e718575175319b5bb4ce/frozenlist-1.8.0-cp313-cp313-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:03ae967b4e297f58f8c774c7eabcce57fe3c2434817d4385c50661845a058121", size = 226549, upload-time = "2025-10-06T05:36:33.706Z" },
-    { url = "https://files.pythonhosted.org/packages/7e/eb/4c7eefc718ff72f9b6c4893291abaae5fbc0c82226a32dcd8ef4f7a5dbef/frozenlist-1.8.0-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:f6292f1de555ffcc675941d65fffffb0a5bcd992905015f85d0592201793e0e5", size = 239833, upload-time = "2025-10-06T05:36:34.947Z" },
-    { url = "https://files.pythonhosted.org/packages/c2/4e/e5c02187cf704224f8b21bee886f3d713ca379535f16893233b9d672ea71/frozenlist-1.8.0-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:29548f9b5b5e3460ce7378144c3010363d8035cea44bc0bf02d57f5a685e084e", size = 245363, upload-time = "2025-10-06T05:36:36.534Z" },
-    { url = "https://files.pythonhosted.org/packages/1f/96/cb85ec608464472e82ad37a17f844889c36100eed57bea094518bf270692/frozenlist-1.8.0-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:ec3cc8c5d4084591b4237c0a272cc4f50a5b03396a47d9caaf76f5d7b38a4f11", size = 229314, upload-time = "2025-10-06T05:36:38.582Z" },
-    { url = "https://files.pythonhosted.org/packages/5d/6f/4ae69c550e4cee66b57887daeebe006fe985917c01d0fff9caab9883f6d0/frozenlist-1.8.0-cp313-cp313-musllinux_1_2_armv7l.whl", hash = "sha256:517279f58009d0b1f2e7c1b130b377a349405da3f7621ed6bfae50b10adf20c1", size = 243365, upload-time = "2025-10-06T05:36:40.152Z" },
-    { url = "https://files.pythonhosted.org/packages/7a/58/afd56de246cf11780a40a2c28dc7cbabbf06337cc8ddb1c780a2d97e88d8/frozenlist-1.8.0-cp313-cp313-musllinux_1_2_ppc64le.whl", hash = "sha256:db1e72ede2d0d7ccb213f218df6a078a9c09a7de257c2fe8fcef16d5925230b1", size = 237763, upload-time = "2025-10-06T05:36:41.355Z" },
-    { url = "https://files.pythonhosted.org/packages/cb/36/cdfaf6ed42e2644740d4a10452d8e97fa1c062e2a8006e4b09f1b5fd7d63/frozenlist-1.8.0-cp313-cp313-musllinux_1_2_s390x.whl", hash = "sha256:b4dec9482a65c54a5044486847b8a66bf10c9cb4926d42927ec4e8fd5db7fed8", size = 240110, upload-time = "2025-10-06T05:36:42.716Z" },
-    { url = "https://files.pythonhosted.org/packages/03/a8/9ea226fbefad669f11b52e864c55f0bd57d3c8d7eb07e9f2e9a0b39502e1/frozenlist-1.8.0-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:21900c48ae04d13d416f0e1e0c4d81f7931f73a9dfa0b7a8746fb2fe7dd970ed", size = 233717, upload-time = "2025-10-06T05:36:44.251Z" },
-    { url = "https://files.pythonhosted.org/packages/1e/0b/1b5531611e83ba7d13ccc9988967ea1b51186af64c42b7a7af465dcc9568/frozenlist-1.8.0-cp313-cp313-win32.whl", hash = "sha256:8b7b94a067d1c504ee0b16def57ad5738701e4ba10cec90529f13fa03c833496", size = 39628, upload-time = "2025-10-06T05:36:45.423Z" },
-    { url = "https://files.pythonhosted.org/packages/d8/cf/174c91dbc9cc49bc7b7aab74d8b734e974d1faa8f191c74af9b7e80848e6/frozenlist-1.8.0-cp313-cp313-win_amd64.whl", hash = "sha256:878be833caa6a3821caf85eb39c5ba92d28e85df26d57afb06b35b2efd937231", size = 43882, upload-time = "2025-10-06T05:36:46.796Z" },
-    { url = "https://files.pythonhosted.org/packages/c1/17/502cd212cbfa96eb1388614fe39a3fc9ab87dbbe042b66f97acb57474834/frozenlist-1.8.0-cp313-cp313-win_arm64.whl", hash = "sha256:44389d135b3ff43ba8cc89ff7f51f5a0bb6b63d829c8300f79a2fe4fe61bcc62", size = 39676, upload-time = "2025-10-06T05:36:47.8Z" },
-    { url = "https://files.pythonhosted.org/packages/d2/5c/3bbfaa920dfab09e76946a5d2833a7cbdf7b9b4a91c714666ac4855b88b4/frozenlist-1.8.0-cp313-cp313t-macosx_10_13_universal2.whl", hash = "sha256:e25ac20a2ef37e91c1b39938b591457666a0fa835c7783c3a8f33ea42870db94", size = 89235, upload-time = "2025-10-06T05:36:48.78Z" },
-    { url = "https://files.pythonhosted.org/packages/d2/d6/f03961ef72166cec1687e84e8925838442b615bd0b8854b54923ce5b7b8a/frozenlist-1.8.0-cp313-cp313t-macosx_10_13_x86_64.whl", hash = "sha256:07cdca25a91a4386d2e76ad992916a85038a9b97561bf7a3fd12d5d9ce31870c", size = 50742, upload-time = "2025-10-06T05:36:49.837Z" },
-    { url = "https://files.pythonhosted.org/packages/1e/bb/a6d12b7ba4c3337667d0e421f7181c82dda448ce4e7ad7ecd249a16fa806/frozenlist-1.8.0-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:4e0c11f2cc6717e0a741f84a527c52616140741cd812a50422f83dc31749fb52", size = 51725, upload-time = "2025-10-06T05:36:50.851Z" },
-    { url = "https://files.pythonhosted.org/packages/bc/71/d1fed0ffe2c2ccd70b43714c6cab0f4188f09f8a67a7914a6b46ee30f274/frozenlist-1.8.0-cp313-cp313t-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:b3210649ee28062ea6099cfda39e147fa1bc039583c8ee4481cb7811e2448c51", size = 284533, upload-time = "2025-10-06T05:36:51.898Z" },
-    { url = "https://files.pythonhosted.org/packages/c9/1f/fb1685a7b009d89f9bf78a42d94461bc06581f6e718c39344754a5d9bada/frozenlist-1.8.0-cp313-cp313t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:581ef5194c48035a7de2aefc72ac6539823bb71508189e5de01d60c9dcd5fa65", size = 292506, upload-time = "2025-10-06T05:36:53.101Z" },
-    { url = "https://files.pythonhosted.org/packages/e6/3b/b991fe1612703f7e0d05c0cf734c1b77aaf7c7d321df4572e8d36e7048c8/frozenlist-1.8.0-cp313-cp313t-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:3ef2d026f16a2b1866e1d86fc4e1291e1ed8a387b2c333809419a2f8b3a77b82", size = 274161, upload-time = "2025-10-06T05:36:54.309Z" },
-    { url = "https://files.pythonhosted.org/packages/ca/ec/c5c618767bcdf66e88945ec0157d7f6c4a1322f1473392319b7a2501ded7/frozenlist-1.8.0-cp313-cp313t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:5500ef82073f599ac84d888e3a8c1f77ac831183244bfd7f11eaa0289fb30714", size = 294676, upload-time = "2025-10-06T05:36:55.566Z" },
-    { url = "https://files.pythonhosted.org/packages/7c/ce/3934758637d8f8a88d11f0585d6495ef54b2044ed6ec84492a91fa3b27aa/frozenlist-1.8.0-cp313-cp313t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:50066c3997d0091c411a66e710f4e11752251e6d2d73d70d8d5d4c76442a199d", size = 300638, upload-time = "2025-10-06T05:36:56.758Z" },
-    { url = "https://files.pythonhosted.org/packages/fc/4f/a7e4d0d467298f42de4b41cbc7ddaf19d3cfeabaf9ff97c20c6c7ee409f9/frozenlist-1.8.0-cp313-cp313t-musllinux_1_2_aarch64.whl", hash = "sha256:5c1c8e78426e59b3f8005e9b19f6ff46e5845895adbde20ece9218319eca6506", size = 283067, upload-time = "2025-10-06T05:36:57.965Z" },
-    { url = "https://files.pythonhosted.org/packages/dc/48/c7b163063d55a83772b268e6d1affb960771b0e203b632cfe09522d67ea5/frozenlist-1.8.0-cp313-cp313t-musllinux_1_2_armv7l.whl", hash = "sha256:eefdba20de0d938cec6a89bd4d70f346a03108a19b9df4248d3cf0d88f1b0f51", size = 292101, upload-time = "2025-10-06T05:36:59.237Z" },
-    { url = "https://files.pythonhosted.org/packages/9f/d0/2366d3c4ecdc2fd391e0afa6e11500bfba0ea772764d631bbf82f0136c9d/frozenlist-1.8.0-cp313-cp313t-musllinux_1_2_ppc64le.whl", hash = "sha256:cf253e0e1c3ceb4aaff6df637ce033ff6535fb8c70a764a8f46aafd3d6ab798e", size = 289901, upload-time = "2025-10-06T05:37:00.811Z" },
-    { url = "https://files.pythonhosted.org/packages/b8/94/daff920e82c1b70e3618a2ac39fbc01ae3e2ff6124e80739ce5d71c9b920/frozenlist-1.8.0-cp313-cp313t-musllinux_1_2_s390x.whl", hash = "sha256:032efa2674356903cd0261c4317a561a6850f3ac864a63fc1583147fb05a79b0", size = 289395, upload-time = "2025-10-06T05:37:02.115Z" },
-    { url = "https://files.pythonhosted.org/packages/e3/20/bba307ab4235a09fdcd3cc5508dbabd17c4634a1af4b96e0f69bfe551ebd/frozenlist-1.8.0-cp313-cp313t-musllinux_1_2_x86_64.whl", hash = "sha256:6da155091429aeba16851ecb10a9104a108bcd32f6c1642867eadaee401c1c41", size = 283659, upload-time = "2025-10-06T05:37:03.711Z" },
-    { url = "https://files.pythonhosted.org/packages/fd/00/04ca1c3a7a124b6de4f8a9a17cc2fcad138b4608e7a3fc5877804b8715d7/frozenlist-1.8.0-cp313-cp313t-win32.whl", hash = "sha256:0f96534f8bfebc1a394209427d0f8a63d343c9779cda6fc25e8e121b5fd8555b", size = 43492, upload-time = "2025-10-06T05:37:04.915Z" },
-    { url = "https://files.pythonhosted.org/packages/59/5e/c69f733a86a94ab10f68e496dc6b7e8bc078ebb415281d5698313e3af3a1/frozenlist-1.8.0-cp313-cp313t-win_amd64.whl", hash = "sha256:5d63a068f978fc69421fb0e6eb91a9603187527c86b7cd3f534a5b77a592b888", size = 48034, upload-time = "2025-10-06T05:37:06.343Z" },
-    { url = "https://files.pythonhosted.org/packages/16/6c/be9d79775d8abe79b05fa6d23da99ad6e7763a1d080fbae7290b286093fd/frozenlist-1.8.0-cp313-cp313t-win_arm64.whl", hash = "sha256:bf0a7e10b077bf5fb9380ad3ae8ce20ef919a6ad93b4552896419ac7e1d8e042", size = 41749, upload-time = "2025-10-06T05:37:07.431Z" },
-    { url = "https://files.pythonhosted.org/packages/f1/c8/85da824b7e7b9b6e7f7705b2ecaf9591ba6f79c1177f324c2735e41d36a2/frozenlist-1.8.0-cp314-cp314-macosx_10_13_universal2.whl", hash = "sha256:cee686f1f4cadeb2136007ddedd0aaf928ab95216e7691c63e50a8ec066336d0", size = 86127, upload-time = "2025-10-06T05:37:08.438Z" },
-    { url = "https://files.pythonhosted.org/packages/8e/e8/a1185e236ec66c20afd72399522f142c3724c785789255202d27ae992818/frozenlist-1.8.0-cp314-cp314-macosx_10_13_x86_64.whl", hash = "sha256:119fb2a1bd47307e899c2fac7f28e85b9a543864df47aa7ec9d3c1b4545f096f", size = 49698, upload-time = "2025-10-06T05:37:09.48Z" },
-    { url = "https://files.pythonhosted.org/packages/a1/93/72b1736d68f03fda5fdf0f2180fb6caaae3894f1b854d006ac61ecc727ee/frozenlist-1.8.0-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:4970ece02dbc8c3a92fcc5228e36a3e933a01a999f7094ff7c23fbd2beeaa67c", size = 49749, upload-time = "2025-10-06T05:37:10.569Z" },
-    { url = "https://files.pythonhosted.org/packages/a7/b2/fabede9fafd976b991e9f1b9c8c873ed86f202889b864756f240ce6dd855/frozenlist-1.8.0-cp314-cp314-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:cba69cb73723c3f329622e34bdbf5ce1f80c21c290ff04256cff1cd3c2036ed2", size = 231298, upload-time = "2025-10-06T05:37:11.993Z" },
-    { url = "https://files.pythonhosted.org/packages/3a/3b/d9b1e0b0eed36e70477ffb8360c49c85c8ca8ef9700a4e6711f39a6e8b45/frozenlist-1.8.0-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:778a11b15673f6f1df23d9586f83c4846c471a8af693a22e066508b77d201ec8", size = 232015, upload-time = "2025-10-06T05:37:13.194Z" },
-    { url = "https://files.pythonhosted.org/packages/dc/94/be719d2766c1138148564a3960fc2c06eb688da592bdc25adcf856101be7/frozenlist-1.8.0-cp314-cp314-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:0325024fe97f94c41c08872db482cf8ac4800d80e79222c6b0b7b162d5b13686", size = 225038, upload-time = "2025-10-06T05:37:14.577Z" },
-    { url = "https://files.pythonhosted.org/packages/e4/09/6712b6c5465f083f52f50cf74167b92d4ea2f50e46a9eea0523d658454ae/frozenlist-1.8.0-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:97260ff46b207a82a7567b581ab4190bd4dfa09f4db8a8b49d1a958f6aa4940e", size = 240130, upload-time = "2025-10-06T05:37:15.781Z" },
-    { url = "https://files.pythonhosted.org/packages/f8/d4/cd065cdcf21550b54f3ce6a22e143ac9e4836ca42a0de1022da8498eac89/frozenlist-1.8.0-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:54b2077180eb7f83dd52c40b2750d0a9f175e06a42e3213ce047219de902717a", size = 242845, upload-time = "2025-10-06T05:37:17.037Z" },
-    { url = "https://files.pythonhosted.org/packages/62/c3/f57a5c8c70cd1ead3d5d5f776f89d33110b1addae0ab010ad774d9a44fb9/frozenlist-1.8.0-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:2f05983daecab868a31e1da44462873306d3cbfd76d1f0b5b69c473d21dbb128", size = 229131, upload-time = "2025-10-06T05:37:18.221Z" },
-    { url = "https://files.pythonhosted.org/packages/6c/52/232476fe9cb64f0742f3fde2b7d26c1dac18b6d62071c74d4ded55e0ef94/frozenlist-1.8.0-cp314-cp314-musllinux_1_2_armv7l.whl", hash = "sha256:33f48f51a446114bc5d251fb2954ab0164d5be02ad3382abcbfe07e2531d650f", size = 240542, upload-time = "2025-10-06T05:37:19.771Z" },
-    { url = "https://files.pythonhosted.org/packages/5f/85/07bf3f5d0fb5414aee5f47d33c6f5c77bfe49aac680bfece33d4fdf6a246/frozenlist-1.8.0-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:154e55ec0655291b5dd1b8731c637ecdb50975a2ae70c606d100750a540082f7", size = 237308, upload-time = "2025-10-06T05:37:20.969Z" },
-    { url = "https://files.pythonhosted.org/packages/11/99/ae3a33d5befd41ac0ca2cc7fd3aa707c9c324de2e89db0e0f45db9a64c26/frozenlist-1.8.0-cp314-cp314-musllinux_1_2_s390x.whl", hash = "sha256:4314debad13beb564b708b4a496020e5306c7333fa9a3ab90374169a20ffab30", size = 238210, upload-time = "2025-10-06T05:37:22.252Z" },
-    { url = "https://files.pythonhosted.org/packages/b2/60/b1d2da22f4970e7a155f0adde9b1435712ece01b3cd45ba63702aea33938/frozenlist-1.8.0-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:073f8bf8becba60aa931eb3bc420b217bb7d5b8f4750e6f8b3be7f3da85d38b7", size = 231972, upload-time = "2025-10-06T05:37:23.5Z" },
-    { url = "https://files.pythonhosted.org/packages/3f/ab/945b2f32de889993b9c9133216c068b7fcf257d8595a0ac420ac8677cab0/frozenlist-1.8.0-cp314-cp314-win32.whl", hash = "sha256:bac9c42ba2ac65ddc115d930c78d24ab8d4f465fd3fc473cdedfccadb9429806", size = 40536, upload-time = "2025-10-06T05:37:25.581Z" },
-    { url = "https://files.pythonhosted.org/packages/59/ad/9caa9b9c836d9ad6f067157a531ac48b7d36499f5036d4141ce78c230b1b/frozenlist-1.8.0-cp314-cp314-win_amd64.whl", hash = "sha256:3e0761f4d1a44f1d1a47996511752cf3dcec5bbdd9cc2b4fe595caf97754b7a0", size = 44330, upload-time = "2025-10-06T05:37:26.928Z" },
-    { url = "https://files.pythonhosted.org/packages/82/13/e6950121764f2676f43534c555249f57030150260aee9dcf7d64efda11dd/frozenlist-1.8.0-cp314-cp314-win_arm64.whl", hash = "sha256:d1eaff1d00c7751b7c6662e9c5ba6eb2c17a2306ba5e2a37f24ddf3cc953402b", size = 40627, upload-time = "2025-10-06T05:37:28.075Z" },
-    { url = "https://files.pythonhosted.org/packages/c0/c7/43200656ecc4e02d3f8bc248df68256cd9572b3f0017f0a0c4e93440ae23/frozenlist-1.8.0-cp314-cp314t-macosx_10_13_universal2.whl", hash = "sha256:d3bb933317c52d7ea5004a1c442eef86f426886fba134ef8cf4226ea6ee1821d", size = 89238, upload-time = "2025-10-06T05:37:29.373Z" },
-    { url = "https://files.pythonhosted.org/packages/d1/29/55c5f0689b9c0fb765055629f472c0de484dcaf0acee2f7707266ae3583c/frozenlist-1.8.0-cp314-cp314t-macosx_10_13_x86_64.whl", hash = "sha256:8009897cdef112072f93a0efdce29cd819e717fd2f649ee3016efd3cd885a7ed", size = 50738, upload-time = "2025-10-06T05:37:30.792Z" },
-    { url = "https://files.pythonhosted.org/packages/ba/7d/b7282a445956506fa11da8c2db7d276adcbf2b17d8bb8407a47685263f90/frozenlist-1.8.0-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:2c5dcbbc55383e5883246d11fd179782a9d07a986c40f49abe89ddf865913930", size = 51739, upload-time = "2025-10-06T05:37:32.127Z" },
-    { url = "https://files.pythonhosted.org/packages/62/1c/3d8622e60d0b767a5510d1d3cf21065b9db874696a51ea6d7a43180a259c/frozenlist-1.8.0-cp314-cp314t-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:39ecbc32f1390387d2aa4f5a995e465e9e2f79ba3adcac92d68e3e0afae6657c", size = 284186, upload-time = "2025-10-06T05:37:33.21Z" },
-    { url = "https://files.pythonhosted.org/packages/2d/14/aa36d5f85a89679a85a1d44cd7a6657e0b1c75f61e7cad987b203d2daca8/frozenlist-1.8.0-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:92db2bf818d5cc8d9c1f1fc56b897662e24ea5adb36ad1f1d82875bd64e03c24", size = 292196, upload-time = "2025-10-06T05:37:36.107Z" },
-    { url = "https://files.pythonhosted.org/packages/05/23/6bde59eb55abd407d34f77d39a5126fb7b4f109a3f611d3929f14b700c66/frozenlist-1.8.0-cp314-cp314t-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:2dc43a022e555de94c3b68a4ef0b11c4f747d12c024a520c7101709a2144fb37", size = 273830, upload-time = "2025-10-06T05:37:37.663Z" },
-    { url = "https://files.pythonhosted.org/packages/d2/3f/22cff331bfad7a8afa616289000ba793347fcd7bc275f3b28ecea2a27909/frozenlist-1.8.0-cp314-cp314t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:cb89a7f2de3602cfed448095bab3f178399646ab7c61454315089787df07733a", size = 294289, upload-time = "2025-10-06T05:37:39.261Z" },
-    { url = "https://files.pythonhosted.org/packages/a4/89/5b057c799de4838b6c69aa82b79705f2027615e01be996d2486a69ca99c4/frozenlist-1.8.0-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:33139dc858c580ea50e7e60a1b0ea003efa1fd42e6ec7fdbad78fff65fad2fd2", size = 300318, upload-time = "2025-10-06T05:37:43.213Z" },
-    { url = "https://files.pythonhosted.org/packages/30/de/2c22ab3eb2a8af6d69dc799e48455813bab3690c760de58e1bf43b36da3e/frozenlist-1.8.0-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:168c0969a329b416119507ba30b9ea13688fafffac1b7822802537569a1cb0ef", size = 282814, upload-time = "2025-10-06T05:37:45.337Z" },
-    { url = "https://files.pythonhosted.org/packages/59/f7/970141a6a8dbd7f556d94977858cfb36fa9b66e0892c6dd780d2219d8cd8/frozenlist-1.8.0-cp314-cp314t-musllinux_1_2_armv7l.whl", hash = "sha256:28bd570e8e189d7f7b001966435f9dac6718324b5be2990ac496cf1ea9ddb7fe", size = 291762, upload-time = "2025-10-06T05:37:46.657Z" },
-    { url = "https://files.pythonhosted.org/packages/c1/15/ca1adae83a719f82df9116d66f5bb28bb95557b3951903d39135620ef157/frozenlist-1.8.0-cp314-cp314t-musllinux_1_2_ppc64le.whl", hash = "sha256:b2a095d45c5d46e5e79ba1e5b9cb787f541a8dee0433836cea4b96a2c439dcd8", size = 289470, upload-time = "2025-10-06T05:37:47.946Z" },
-    { url = "https://files.pythonhosted.org/packages/ac/83/dca6dc53bf657d371fbc88ddeb21b79891e747189c5de990b9dfff2ccba1/frozenlist-1.8.0-cp314-cp314t-musllinux_1_2_s390x.whl", hash = "sha256:eab8145831a0d56ec9c4139b6c3e594c7a83c2c8be25d5bcf2d86136a532287a", size = 289042, upload-time = "2025-10-06T05:37:49.499Z" },
-    { url = "https://files.pythonhosted.org/packages/96/52/abddd34ca99be142f354398700536c5bd315880ed0a213812bc491cff5e4/frozenlist-1.8.0-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:974b28cf63cc99dfb2188d8d222bc6843656188164848c4f679e63dae4b0708e", size = 283148, upload-time = "2025-10-06T05:37:50.745Z" },
-    { url = "https://files.pythonhosted.org/packages/af/d3/76bd4ed4317e7119c2b7f57c3f6934aba26d277acc6309f873341640e21f/frozenlist-1.8.0-cp314-cp314t-win32.whl", hash = "sha256:342c97bf697ac5480c0a7ec73cd700ecfa5a8a40ac923bd035484616efecc2df", size = 44676, upload-time = "2025-10-06T05:37:52.222Z" },
-    { url = "https://files.pythonhosted.org/packages/89/76/c615883b7b521ead2944bb3480398cbb07e12b7b4e4d073d3752eb721558/frozenlist-1.8.0-cp314-cp314t-win_amd64.whl", hash = "sha256:06be8f67f39c8b1dc671f5d83aaefd3358ae5cdcf8314552c57e7ed3e6475bdd", size = 49451, upload-time = "2025-10-06T05:37:53.425Z" },
-    { url = "https://files.pythonhosted.org/packages/e0/a3/5982da14e113d07b325230f95060e2169f5311b1017ea8af2a29b374c289/frozenlist-1.8.0-cp314-cp314t-win_arm64.whl", hash = "sha256:102e6314ca4da683dca92e3b1355490fed5f313b768500084fbe6371fddfdb79", size = 42507, upload-time = "2025-10-06T05:37:54.513Z" },
-    { url = "https://files.pythonhosted.org/packages/9a/9a/e35b4a917281c0b8419d4207f4334c8e8c5dbf4f3f5f9ada73958d937dcc/frozenlist-1.8.0-py3-none-any.whl", hash = "sha256:0c18a16eab41e82c295618a77502e17b195883241c563b00f0aa5106fc4eaa0d", size = 13409, upload-time = "2025-10-06T05:38:16.721Z" },
-]
-
-[[package]]
-name = "fsspec"
-version = "2026.7.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/00/78/f34251dadb8f3921264a1d9b8946f5e542014ee2614b285261b4e40e6775/fsspec-2026.7.0.tar.gz", hash = "sha256:c803c40f4cf860b49dea58ee3e1c33cb9c790520e233537e1340049f89b82a88", size = 317040, upload-time = "2026-07-28T16:34:51.052Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/fd/3c/6a2bf344106328fd04963664a60b9bb6496fc25df8e962fcdc1367285fb9/fsspec-2026.7.0-py3-none-any.whl", hash = "sha256:b57ddbafedfaef7018c1ecab32aa200a9d7ca26b77965f64e48b70061249d279", size = 206583, upload-time = "2026-07-28T16:34:49.538Z" },
-]
-
-[[package]]
-name = "h11"
-version = "0.16.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/01/ee/02a2c011bdab74c6fb3c75474d40b3052059d95df7e73351460c8588d963/h11-0.16.0.tar.gz", hash = "sha256:4e35b956cf45792e4caa5885e69fba00bdbc6ffafbfa020300e549b208ee5ff1", size = 101250, upload-time = "2025-04-24T03:35:25.427Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/04/4b/29cac41a4d98d144bf5f6d33995617b185d14b22401f75ca86f384e87ff1/h11-0.16.0-py3-none-any.whl", hash = "sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86", size = 37515, upload-time = "2025-04-24T03:35:24.344Z" },
-]
-
-[[package]]
-name = "hf-xet"
-version = "1.6.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/1b/ab/522a2ab67f27971a9d48ca666d4fca85ef7d5282d142e31fd087e27b1bbe/hf_xet-1.6.0.tar.gz", hash = "sha256:2e58454a340b3556dfa4972d5451aff4fba8dd42a236600ba1a1d2b1514f0fef", size = 920527, upload-time = "2026-08-03T22:33:13.243Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/41/62/3c062f593bd92ef4e77a0ef39541e3d82a0a1d3947c8a777a02a13a27828/hf_xet-1.6.0-cp314-cp314t-macosx_10_12_x86_64.whl", hash = "sha256:70cbb9c896901600128cb9b6f06e132954fbede1db30f31f7c6c63f84cb7c31d", size = 4074584, upload-time = "2026-08-03T22:32:47.364Z" },
-    { url = "https://files.pythonhosted.org/packages/bb/1e/c0ad437dd267a8e435bef594acf781bbc3874ff0b6435b4962d03ecf7cc4/hf_xet-1.6.0-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:23379c2f9ec8696d952b16414a2bae72cad86a52df869b050698ba60f538c675", size = 3867381, upload-time = "2026-08-03T22:32:49.049Z" },
-    { url = "https://files.pythonhosted.org/packages/d5/ee/7c0d7b6ab336167531b1c30af2af003f054af4c749becbd7209ae33a77c3/hf_xet-1.6.0-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:f2f7278c05c22fd60cb436cda1269649b3e81db65ecdc8496e5e164aa4143e7b", size = 4453982, upload-time = "2026-08-03T22:32:50.568Z" },
-    { url = "https://files.pythonhosted.org/packages/63/06/ad8eab1c9525246650cbaa821caa3cdbaca734ab1a5b8c91bea09cbd8d69/hf_xet-1.6.0-cp314-cp314t-manylinux_2_28_aarch64.whl", hash = "sha256:948f15d3a9545cfe5932f6bd8b440f6ae630aee108f14b7bd6c561f7c2dcc522", size = 4249445, upload-time = "2026-08-03T22:32:52.391Z" },
-    { url = "https://files.pythonhosted.org/packages/d8/26/1eee8aedb0dafc1ab9717dc9ac602cde33361b232dc06803f1f6ed18b58c/hf_xet-1.6.0-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:5153e6bb103ad49d6ea9f1b2e230db5a2ea32551ad09a706d2f61d7c7c80d80e", size = 4451099, upload-time = "2026-08-03T22:32:54.114Z" },
-    { url = "https://files.pythonhosted.org/packages/67/57/0b88af1f194ab6c9c650547d9cc06bfeaab836ae4dcdb331676bfb8be95a/hf_xet-1.6.0-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:35cec30d75c6f9eb9c16a77cef68e85a103b72e24d4b473714ec9ff06428bab9", size = 4664712, upload-time = "2026-08-03T22:32:55.547Z" },
-    { url = "https://files.pythonhosted.org/packages/53/a0/26b717a9d1840e8abf48dcec64b5ed8fbe472671d38ad28d30e147132b33/hf_xet-1.6.0-cp314-cp314t-win_amd64.whl", hash = "sha256:5789835d7c6bc9436962853192082374297fb72d7eff7e7762ec25ceb7e25338", size = 4025906, upload-time = "2026-08-03T22:32:57.391Z" },
-    { url = "https://files.pythonhosted.org/packages/49/f6/4a9966633c6fef83af997e2cff68ec1963676d412bdfd096df2a93b8e185/hf_xet-1.6.0-cp314-cp314t-win_arm64.whl", hash = "sha256:75765820ce4700db3750c94acc8fe27c5fae4c9ec000a0dbac3ca082acf97765", size = 3849221, upload-time = "2026-08-03T22:32:59.123Z" },
-    { url = "https://files.pythonhosted.org/packages/a2/50/7afa2c9c787405864fc47a0d1bbc02c62e9101947ed43c1f43899fc7d91d/hf_xet-1.6.0-cp38-abi3-macosx_10_12_x86_64.whl", hash = "sha256:633dc0cd71d32da58ab8c03ad38e2fac452c15c2b0a2866ebf6ededfe0a5061d", size = 4071729, upload-time = "2026-08-03T22:33:00.721Z" },
-    { url = "https://files.pythonhosted.org/packages/4b/69/55b8dcf636142ae660fec1869fcac14c4da2e8412e14d6eee1523be77e9f/hf_xet-1.6.0-cp38-abi3-macosx_11_0_arm64.whl", hash = "sha256:f0906082d9932ae0c0057fa194041c22b4e2cdb46b2592ef3b91f020d62a081a", size = 3876287, upload-time = "2026-08-03T22:33:02.251Z" },
-    { url = "https://files.pythonhosted.org/packages/67/4e/a28359bf1c1ecf11eba22123168c138698f7cb576ac678f5a2e16cd5da08/hf_xet-1.6.0-cp38-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:d62671bb130879cef0ee4c9ebe47a14af6c66ec53e6d84dc15936e5ffdfac82f", size = 4464663, upload-time = "2026-08-03T22:33:03.802Z" },
-    { url = "https://files.pythonhosted.org/packages/9a/69/1f0cbc2fb22ae6082d094f743d1b8945a3f36f6089cb95f42b7ee348cda7/hf_xet-1.6.0-cp38-abi3-manylinux_2_28_aarch64.whl", hash = "sha256:0e6e21fa3cdfcdcd76748564bf593870a5e013f47d97cf10aed63aa222cff5b7", size = 4262538, upload-time = "2026-08-03T22:33:05.287Z" },
-    { url = "https://files.pythonhosted.org/packages/d1/3a/4f4f2301ade26e404462d3336fa11f7958d914cabbabdd6e03c3c5d5658c/hf_xet-1.6.0-cp38-abi3-musllinux_1_2_aarch64.whl", hash = "sha256:4fc74352a17015bd0ee90038bc9efe38db894cde45f268b6712b04fce8cd0acb", size = 4460520, upload-time = "2026-08-03T22:33:06.81Z" },
-    { url = "https://files.pythonhosted.org/packages/ab/5f/311725e2a905534dfee2dcb5b08414f249147f1f12252bfc2bd24caa075c/hf_xet-1.6.0-cp38-abi3-musllinux_1_2_x86_64.whl", hash = "sha256:8fb4f71cba6129110c3374a33f919001ff130488fc23553698e34cc1c2a1198c", size = 4675937, upload-time = "2026-08-03T22:33:08.616Z" },
-    { url = "https://files.pythonhosted.org/packages/98/b7/8c59a66d15205024662f1d66968136f13893f96df1ddc5087e2e281fc95f/hf_xet-1.6.0-cp38-abi3-win_amd64.whl", hash = "sha256:fb4fadde1b2b70bf4c0c14a6dccbe7194b1c28947fefd5bbe3fed9d940676c3b", size = 4033128, upload-time = "2026-08-03T22:33:10.171Z" },
-    { url = "https://files.pythonhosted.org/packages/73/63/ca511b6f802f28cf3489b280fe77475bcca8de85e81a6299d7916b5b5555/hf_xet-1.6.0-cp38-abi3-win_arm64.whl", hash = "sha256:3dc3e35441ba395006af5aaacc40ef2e603c51ef46c3530b9156185f00935ea3", size = 3859359, upload-time = "2026-08-03T22:33:11.725Z" },
-]
-
-[[package]]
-name = "httpcore"
-version = "1.0.9"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "certifi" },
-    { name = "h11" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/06/94/82699a10bca87a5556c9c59b5963f2d039dbd239f25bc2a63907a05a14cb/httpcore-1.0.9.tar.gz", hash = "sha256:6e34463af53fd2ab5d807f399a9b45ea31c3dfa2276f15a2c3f00afff6e176e8", size = 85484, upload-time = "2025-04-24T22:06:22.219Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/7e/f5/f66802a942d491edb555dd61e3a9961140fd64c90bce1eafd741609d334d/httpcore-1.0.9-py3-none-any.whl", hash = "sha256:2d400746a40668fc9dec9810239072b40b4484b640a8c38fd654a024c7a1bf55", size = 78784, upload-time = "2025-04-24T22:06:20.566Z" },
-]
-
-[[package]]
-name = "httpx"
-version = "0.28.1"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "anyio" },
-    { name = "certifi" },
-    { name = "httpcore" },
-    { name = "idna" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/b1/df/48c586a5fe32a0f01324ee087459e112ebb7224f646c0b5023f5e79e9956/httpx-0.28.1.tar.gz", hash = "sha256:75e98c5f16b0f35b567856f597f06ff2270a374470a5c2392242528e3e3e42fc", size = 141406, upload-time = "2024-12-06T15:37:23.222Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/2a/39/e50c7c3a983047577ee07d2a9e53faf5a69493943ec3f6a384bdc792deb2/httpx-0.28.1-py3-none-any.whl", hash = "sha256:d909fcccc110f8c7faf814ca82a9a4d816bc5a6dbfea25d6591d6985b8ba59ad", size = 73517, upload-time = "2024-12-06T15:37:21.509Z" },
-]
-
-[[package]]
-name = "huggingface-hub"
-version = "1.28.0"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "click" },
-    { name = "filelock" },
-    { name = "fsspec" },
-    { name = "hf-xet", marker = "platform_machine == 'AMD64' or platform_machine == 'aarch64' or platform_machine == 'amd64' or platform_machine == 'arm64' or platform_machine == 'x86_64'" },
-    { name = "httpx" },
-    { name = "packaging" },
-    { name = "pyyaml" },
-    { name = "tqdm" },
-    { name = "typing-extensions" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/c6/ae/222a91937ebee7f62c0ca8f5ee0afd97577caf24c0abb927d1f5c7e9f6d2/huggingface_hub-1.28.0.tar.gz", hash = "sha256:46a2e950c09234de54093d587d1675382f0d08dbd600d9fb599b5932f5b2c6cb", size = 959609, upload-time = "2026-08-18T12:27:15.101Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/51/0e/eafef18f1a75e125e68395db21131db0cf868a128ecd2fce69b4df6c584b/huggingface_hub-1.28.0-py3-none-any.whl", hash = "sha256:58a8bacb03072edfc38067065e9dc24bbb34805410fcd36a1632de0b329660bb", size = 793202, upload-time = "2026-08-18T12:27:12.719Z" },
-]
-
-[[package]]
-name = "idna"
-version = "3.19"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/5f/f7/abb373e5757eaec4b922b92f97ec8d6d7e057cf06778247604fbc4e7c3f3/idna-3.19.tar.gz", hash = "sha256:5e0811a4383b21dc5838069f801c4fb62113b7447663d2530d2bd6e77b49bf15", size = 215237, upload-time = "2026-08-18T05:14:24.27Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/57/b0/0e52c878c53f245edd3a11020f20979b3f490f245af532c7cae3027754b5/idna-3.19-py3-none-any.whl", hash = "sha256:815e7be7a7806d54abb586dc943addc79e8b2ee16915059658cbeff4b1b43bf4", size = 68550, upload-time = "2026-08-18T05:14:22.343Z" },
-]
-
-[[package]]
-name = "importlib-metadata"
-version = "8.9.0"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "zipp" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/e7/72/c600ae4f68c28fc19f9c31b9403053e5dbb8cace2e6842c7b7c3e4d42fe9/importlib_metadata-8.9.0.tar.gz", hash = "sha256:58850626cef4bd2df100378b0f2aea9724a7b92f10770d547725b047078f99ee", size = 56140, upload-time = "2026-03-20T16:56:26.362Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/7d/f9/97f2ca8bb3ec6e4b1d64f983ebe98b9a192faddff67fac3d6303a537e670/importlib_metadata-8.9.0-py3-none-any.whl", hash = "sha256:e0f761b6ea91ced3b0844c14c9d955224d538105921f8e6754c00f6ca79fba7f", size = 27220, upload-time = "2026-03-20T16:56:25.07Z" },
-]
-
-[[package]]
-name = "iniconfig"
-version = "2.3.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/72/34/14ca021ce8e5dfedc35312d08ba8bf51fdd999c576889fc2c24cb97f4f10/iniconfig-2.3.0.tar.gz", hash = "sha256:c76315c77db068650d49c5b56314774a7804df16fee4402c1f19d6d15d8c4730", size = 20503, upload-time = "2025-10-18T21:55:43.219Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/cb/b1/3846dd7f199d53cb17f49cba7e651e9ce294d8497c8c150530ed11865bb8/iniconfig-2.3.0-py3-none-any.whl", hash = "sha256:f631c04d2c48c52b84d0d0549c99ff3859c98df65b3101406327ecc7d53fbf12", size = 7484, upload-time = "2025-10-18T21:55:41.639Z" },
-]
-
-[[package]]
-name = "jinja2"
-version = "3.1.6"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "markupsafe" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/df/bf/f7da0350254c0ed7c72f3e33cef02e048281fec7ecec5f032d4aac52226b/jinja2-3.1.6.tar.gz", hash = "sha256:0137fb05990d35f1275a587e9aee6d56da821fc83491a0fb838183be43f66d6d", size = 245115, upload-time = "2025-03-05T20:05:02.478Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/62/a1/3d680cbfd5f4b8f15abc1d571870c5fc3e594bb582bc3b64ea099db13e56/jinja2-3.1.6-py3-none-any.whl", hash = "sha256:85ece4451f492d0c13c5dd7c13a64681a86afae63a5f347908daf103ce6d2f67", size = 134899, upload-time = "2025-03-05T20:05:00.369Z" },
-]
-
-[[package]]
-name = "jiter"
-version = "0.16.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/1d/1f/10936e16d8860c70698a1aa939a46aa0224813b782bce4e000e637da0b2d/jiter-0.16.0.tar.gz", hash = "sha256:7b24c3492c5f4f84a37946ad9cf504910cf6a782d6a4e0689b6673c5894b4a1c", size = 176431, upload-time = "2026-06-29T13:05:13.657Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/83/2b/52ace16ed031354f0539749a49e4bf33797d82bea5137910835fa4b09793/jiter-0.16.0-cp312-cp312-macosx_10_12_x86_64.whl", hash = "sha256:67c3bc1760f8c99d805dcab4e644027142a53b1d5d861f18780ebdbd5d40b72a", size = 306943, upload-time = "2026-06-29T13:03:14.035Z" },
-    { url = "https://files.pythonhosted.org/packages/94/2e/34957c2c1b661c252ba9bcc60ae0bddc27e0f7202c6073326a13c5390eec/jiter-0.16.0-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:5af7780e4a26bd7d0d989592bf9ef12ebf806b74ab709223ecca37c749872ea9", size = 307779, upload-time = "2026-06-29T13:03:15.418Z" },
-    { url = "https://files.pythonhosted.org/packages/88/6c/59bd309cab4460c54cf1079f3eb7fe7af6a4c895c5c957a53378693bad2b/jiter-0.16.0-cp312-cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:d5bf78d0e05e45cfdd66558893938d59afe3d1b1a824a202039b20e607d25a72", size = 335826, upload-time = "2026-06-29T13:03:17.11Z" },
-    { url = "https://files.pythonhosted.org/packages/3b/8c/f5ef7b65f0df47afa16596969defb281ebb86e96df346d62be6fd853d620/jiter-0.16.0-cp312-cp312-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:f4444a83f946605990c98f625cdd3d2725bfb818158760c5748c653170a20e0e", size = 362573, upload-time = "2026-06-29T13:03:18.781Z" },
-    { url = "https://files.pythonhosted.org/packages/2b/0b/ace4354da061ee38844a0c27dc2c21eecd27aea119e8da324bea987522d0/jiter-0.16.0-cp312-cp312-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:3a23f0e4f957e1be65752d2dfac9a5a06b1917af8dc85deb639c3b9d02e31290", size = 457979, upload-time = "2026-06-29T13:03:20.293Z" },
-    { url = "https://files.pythonhosted.org/packages/55/40/c0253d3772eb9dcd8e6606ee9b2d53ec8e5b814589c47f140aa585f21eaa/jiter-0.16.0-cp312-cp312-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:c22a488f7b9218e245a0025a9ba6b100e2e54700831cf4cf16833a27fba3ad01", size = 372302, upload-time = "2026-06-29T13:03:21.739Z" },
-    { url = "https://files.pythonhosted.org/packages/a8/d2/4839422241aa12860ce597b20068727094ba0bc480723c74924ca5bad483/jiter-0.16.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:46add52f4ad47a08bfb1219f3e673da972191489a33016edefdb5ea55bfa8c48", size = 343805, upload-time = "2026-06-29T13:03:23.384Z" },
-    { url = "https://files.pythonhosted.org/packages/e2/59/e196888a05befdda7dbe299b722d56f2f6eec65402bc34c0a3306d595feb/jiter-0.16.0-cp312-cp312-manylinux_2_31_riscv64.whl", hash = "sha256:9c8a956fd72c2cf1e730d01ea080341f13aa0a97a4a33b51abebe725b7ae9ca9", size = 351107, upload-time = "2026-06-29T13:03:24.815Z" },
-    { url = "https://files.pythonhosted.org/packages/ec/74/4cd9e0fca65232136400354b630fbfcd2de634e22ccbb96567725981b548/jiter-0.16.0-cp312-cp312-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:561926e0573ffe4a32498420a76d64b16c513e1ab413b9d28158a8764ac701e5", size = 388441, upload-time = "2026-06-29T13:03:26.266Z" },
-    { url = "https://files.pythonhosted.org/packages/d9/8c/554691e48bc711299c0a293dd8a6179e24b2d66a54dc295421fcf64569c0/jiter-0.16.0-cp312-cp312-musllinux_1_1_aarch64.whl", hash = "sha256:44d019fa8cdaf89bf29c71b39e3712143fdd0ac76725c6ef954f9957a5ea8730", size = 516354, upload-time = "2026-06-29T13:03:28.02Z" },
-    { url = "https://files.pythonhosted.org/packages/a4/cb/01e9d69dc2cc6759d4f91e230b34489c4fdb2518992650633f9e20bece89/jiter-0.16.0-cp312-cp312-musllinux_1_1_x86_64.whl", hash = "sha256:0df91907609837f33341b8e6fe73b95991fdaa57caf1a0fbd343dffe826f386f", size = 547880, upload-time = "2026-06-29T13:03:29.534Z" },
-    { url = "https://files.pythonhosted.org/packages/79/70/2953195f1c6ad00f49fa67e13df7e60acb3dd4f387101bc15abccddd905e/jiter-0.16.0-cp312-cp312-win32.whl", hash = "sha256:51d7b836acb0108d7c77df1742332cac2a1fa04a74d6dacec46e7091f0e91274", size = 203473, upload-time = "2026-06-29T13:03:31.025Z" },
-    { url = "https://files.pythonhosted.org/packages/2d/05/2909a8b10699a4d560f8c502b6b2c5f3991b682b1922c1eedda242b225bd/jiter-0.16.0-cp312-cp312-win_amd64.whl", hash = "sha256:1878349266f8ee36ecb1375cc5ba2f115f35fd9f0a1a4119e725e379126647f7", size = 196905, upload-time = "2026-06-29T13:03:32.472Z" },
-    { url = "https://files.pythonhosted.org/packages/e9/a9/6b82bb1c8d7790d602489b967b982a909e5d092875a6c2ade96444c8dfc5/jiter-0.16.0-cp312-cp312-win_arm64.whl", hash = "sha256:2ed5738ae4af18271a51a528b8811b0cbfa4a1858de9d83359e4169855d6a331", size = 190618, upload-time = "2026-06-29T13:03:34.672Z" },
-    { url = "https://files.pythonhosted.org/packages/91/c0/555fc60473d30d66894ba825e63615e3be7524fac23858356afa7a38906c/jiter-0.16.0-cp313-cp313-macosx_10_12_x86_64.whl", hash = "sha256:41977aa5654023948c2dae2a81cbf9c43343954bef1cd59a154dd15a4d84c195", size = 306203, upload-time = "2026-06-29T13:03:36.243Z" },
-    { url = "https://files.pythonhosted.org/packages/d0/2b/c3eaf16f5d7c9bad66ea32f40a95bd169b29a91217fcc7f081375157e99c/jiter-0.16.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:d28bb3c26762358dadf3e5bf0bccd29ae987d65e6988d2e6f49829c76b003c09", size = 306489, upload-time = "2026-06-29T13:03:37.846Z" },
-    { url = "https://files.pythonhosted.org/packages/96/3f/02fdfc6705cad96127d883af5c34e4867f554f29ec7705ec1a46156400a9/jiter-0.16.0-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:0542a7189c26920778658fc8fcf2af8bae05bae9924577f71804acef37996536", size = 335453, upload-time = "2026-06-29T13:03:39.221Z" },
-    { url = "https://files.pythonhosted.org/packages/b2/a6/e4bda5920d4b0d7c5dfb7174ce4a6b2e4d3e11c9162c452ef0eab4cdbdbd/jiter-0.16.0-cp313-cp313-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:8fb8de1e23a0cb2a7f53c335049c7b72b6db41aa6227cdcc0972a1de5cb39450", size = 361625, upload-time = "2026-06-29T13:03:40.597Z" },
-    { url = "https://files.pythonhosted.org/packages/b7/97/4e6b59b2c6e55cbb3e183595f81ad65dcfb21c915fee5e19e335df21bc55/jiter-0.16.0-cp313-cp313-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:b72d0b2990ca754a9102779ac98d8597b7cb31678958562214a007f909eab78e", size = 456958, upload-time = "2026-06-29T13:03:42.074Z" },
-    { url = "https://files.pythonhosted.org/packages/15/e0/97e9557686d2f94f4b93786eccb7eed28e9228ad132ea8237f44727314a7/jiter-0.16.0-cp313-cp313-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:d5f91b1c27fc22a57993d5a5cb8a627cb8ed4b10502716fac1ffbfe1d19d84e8", size = 372017, upload-time = "2026-06-29T13:03:43.658Z" },
-    { url = "https://files.pythonhosted.org/packages/0f/94/db768b6938e0df35c86beeba3dfbbb025c9ee5c19e1aa271f2396e50864d/jiter-0.16.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:c682bea068a90b764577bdb78a60a4c1d1606daf9cd4c893832a37c7cc9d9026", size = 343320, upload-time = "2026-06-29T13:03:45.226Z" },
-    { url = "https://files.pythonhosted.org/packages/c1/d6/5a59d938244a30735fe62d9433fd325f9021ea29d89780ea4596ea93bc89/jiter-0.16.0-cp313-cp313-manylinux_2_31_riscv64.whl", hash = "sha256:8d031aabecc4f1b6276adfb42e3aabb77c89d468bf616600e8d3a11328929053", size = 350520, upload-time = "2026-06-29T13:03:46.671Z" },
-    { url = "https://files.pythonhosted.org/packages/67/f8/c4a857f49c9af125f6bbcac7e3eee7f7978ed89682833062e2dbf62576b1/jiter-0.16.0-cp313-cp313-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:eab2cd170150e70153de16896a1774e3a1dca80154c56b54d7a812c479a7165e", size = 387550, upload-time = "2026-06-29T13:03:48.361Z" },
-    { url = "https://files.pythonhosted.org/packages/8b/d6/5fbc2f7d6b67b754caa61a993a2e626e815dec47ffc2f9e35f01adfebec7/jiter-0.16.0-cp313-cp313-musllinux_1_1_aarch64.whl", hash = "sha256:6edb63a46e65a82c26800a868e49b2cac30dd5a4218b88d74bc2c848c8ad60bb", size = 515424, upload-time = "2026-06-29T13:03:49.881Z" },
-    { url = "https://files.pythonhosted.org/packages/ed/54/284f0164b64a5fed915fea6ba7e9ba9b3d8d37c67d59cf2e3bb99d45cdfe/jiter-0.16.0-cp313-cp313-musllinux_1_1_x86_64.whl", hash = "sha256:659039cc50b5addcc35fcc87ae2c1833b7c0a8e5326ef631a75e4478447bcf84", size = 546981, upload-time = "2026-06-29T13:03:51.363Z" },
-    { url = "https://files.pythonhosted.org/packages/13/c5/2a467585a576594384e1d2c43e1224deaafc085f24e243529cf98beef8e1/jiter-0.16.0-cp313-cp313-win32.whl", hash = "sha256:c9c53be232c2e206ef9cdbad81a48bfa74c3d3f08bcf8124630a8a748aad993e", size = 202853, upload-time = "2026-06-29T13:03:53.015Z" },
-    { url = "https://files.pythonhosted.org/packages/88/6a/de61d04b9eec69c71719968d2f716532a3bc121170c44a39e14979c6be81/jiter-0.16.0-cp313-cp313-win_amd64.whl", hash = "sha256:baad945ed47f163ad833314f8e3288c396118934f94e7bbb9e243ce4b341a4fd", size = 196160, upload-time = "2026-06-29T13:03:54.447Z" },
-    { url = "https://files.pythonhosted.org/packages/19/4b/b390ed59bafb3f31d008d1218578f10327714484b334439947f7e5b11e7f/jiter-0.16.0-cp313-cp313-win_arm64.whl", hash = "sha256:3c1fd2dbe1b0af19e987f03fe66c5f5bd105a2229c1aff4ab14890b24f41d21a", size = 189862, upload-time = "2026-06-29T13:03:55.754Z" },
-    { url = "https://files.pythonhosted.org/packages/a7/89/bc4f1b57d5da938fd344a466396541e586d161320d70bffd929aaafcd8f4/jiter-0.16.0-cp314-cp314-macosx_10_12_x86_64.whl", hash = "sha256:b2c61484666ad42726029af0c00ef4541f0f3b5cdc550221f56c2343208018ee", size = 308239, upload-time = "2026-06-29T13:03:57.205Z" },
-    { url = "https://files.pythonhosted.org/packages/65/7a/c415453e5213001bf3b411ff65dec3d303b0e76a4a2cfea9768cd4960994/jiter-0.16.0-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:63efadc657488f45db1c676d81e704cac2abf3fdb892def1faea61db053127e2", size = 308928, upload-time = "2026-06-29T13:03:58.643Z" },
-    { url = "https://files.pythonhosted.org/packages/11/fc/1f4fb7ebf9a724c7741994f4aae18fba1e2f3133df14521a79194952c34a/jiter-0.16.0-cp314-cp314-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:cf0d73f50e7b6935677854f6e8e31d499ca7064dd24734f703e060f5b237d883", size = 336998, upload-time = "2026-06-29T13:04:00.071Z" },
-    { url = "https://files.pythonhosted.org/packages/a0/8d/72cadaac05ccfa7cc3a0a2232862e6c72443ca40cf300ba8b57f9f18b69b/jiter-0.16.0-cp314-cp314-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:bf3ea07d9bc8e7d03a9fbc051295462e6dbc295b894fd72457c3136e3e43d898", size = 362112, upload-time = "2026-06-29T13:04:01.52Z" },
-    { url = "https://files.pythonhosted.org/packages/58/4a/c4b0d5f651fda90a24ffce9f8d56cde462a2e09d31ae3de3c68cef34c04e/jiter-0.16.0-cp314-cp314-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:26798522707abb47d767db536e4148ceac1b14446bf028ee85e579a2e043cfe5", size = 459807, upload-time = "2026-06-29T13:04:03.214Z" },
-    { url = "https://files.pythonhosted.org/packages/80/58/ef77879ea9aa56b50824edc5a445e226422c7a8d211f3fd2a56bcb9493cf/jiter-0.16.0-cp314-cp314-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:bc837c1b9631be10abfe0191537fe8009838204cec7e44827401ace390ddb567", size = 373181, upload-time = "2026-06-29T13:04:04.629Z" },
-    { url = "https://files.pythonhosted.org/packages/49/2e/ffbc3f254e4d8a66da3062c624a7df4b7c2b2cf9e1fe43cf394b3e104041/jiter-0.16.0-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:49060fd70737fad59d33ba9dcc0d83247dc9e77187de26053a19c16c9f32bd69", size = 344927, upload-time = "2026-06-29T13:04:06.067Z" },
-    { url = "https://files.pythonhosted.org/packages/9a/f6/0be5dc6d64a89f80aa8fec984f94dedb2973e251edcae55841d60786d578/jiter-0.16.0-cp314-cp314-manylinux_2_31_riscv64.whl", hash = "sha256:adbb8edeadd431bc4477879d5d371ece7cb1334486584e0f252656dd7ffada29", size = 352754, upload-time = "2026-06-29T13:04:07.477Z" },
-    { url = "https://files.pythonhosted.org/packages/da/6e/7d31243b3b91cd261dd19e9d3557fc3251a80883d3d8049c86174e7ab7af/jiter-0.16.0-cp314-cp314-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:31aaee5b80f672c1dc21272bcfb9cbdcfc1ea04ff50f00ed5af500b80c44fa93", size = 390553, upload-time = "2026-06-29T13:04:08.92Z" },
-    { url = "https://files.pythonhosted.org/packages/25/33/51ae371fde3c88897520f62b4d5f8b27ad7103e2bb10812ff52195609853/jiter-0.16.0-cp314-cp314-musllinux_1_1_aarch64.whl", hash = "sha256:6722bcef4ffc86c835574b1b2fac6b33b9fb4a889c781e67950e891591f3c55a", size = 516900, upload-time = "2026-06-29T13:04:10.407Z" },
-    { url = "https://files.pythonhosted.org/packages/a0/45/6449b3d123ea439ba79507c657288f461d55049e7bcbdc2cf8eb8210f491/jiter-0.16.0-cp314-cp314-musllinux_1_1_x86_64.whl", hash = "sha256:5ab4f50ff971b611d656554ea10b75f80097392c827bc32923c6eeb6386c8b00", size = 548754, upload-time = "2026-06-29T13:04:12.046Z" },
-    { url = "https://files.pythonhosted.org/packages/9b/e7/fd2fb11ae3e2649333da3aa170d04d7b3000bbdc3b270f6513382fdf4e04/jiter-0.16.0-cp314-cp314-pyemscripten_2026_0_wasm32.whl", hash = "sha256:710cc51d4ebdcd3c1f70b232c1db1ea1344a075770422bbd4bede5708335acbe", size = 122381, upload-time = "2026-06-29T13:04:13.413Z" },
-    { url = "https://files.pythonhosted.org/packages/26/80/f0b147a62c315a164ed2168908286ca302310824c218d3aae52b06c0c9a9/jiter-0.16.0-cp314-cp314-win32.whl", hash = "sha256:57b37fc887a32d44798e4d8ebfa7c9683ff3da1d5bf38f08d1bb3573ccb39106", size = 204578, upload-time = "2026-06-29T13:04:14.813Z" },
-    { url = "https://files.pythonhosted.org/packages/5e/e6/4758a14304b4523a6f5adb2419340086aa3593bd4327c2b25b5948a90548/jiter-0.16.0-cp314-cp314-win_amd64.whl", hash = "sha256:cbd18dd5e2df96b580487b5745adf57ef64ad89ba2d9662fc3c19386acce7db8", size = 198154, upload-time = "2026-06-29T13:04:16.272Z" },
-    { url = "https://files.pythonhosted.org/packages/26/be/41fa54a2e7ea41d6c99f1dc5b1f0fd4cb474680304b5d268dd518e81da3a/jiter-0.16.0-cp314-cp314-win_arm64.whl", hash = "sha256:a32d2027a9fa67f109ff245a3252ece3ccc32cc56703e1deab6cc846a59e0585", size = 191458, upload-time = "2026-06-29T13:04:17.707Z" },
-    { url = "https://files.pythonhosted.org/packages/81/6b/59127338b86d9fe4d99418f5a15118bea778103ee0fe9d9dd7e0af174e95/jiter-0.16.0-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:2577196f4474ef3fc4779a088a23b0897bbf86f9ea3679c372d45b8383b43207", size = 316739, upload-time = "2026-06-29T13:04:19.663Z" },
-    { url = "https://files.pythonhosted.org/packages/2d/95/49461034d5388196d3dabf98748935f017b7785d8f3f5349f834bcc4ed0d/jiter-0.16.0-cp314-cp314t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:616e89e008a93c01104161c75b4988e58716b01d62307ebfe161e52a56d2a818", size = 340911, upload-time = "2026-06-29T13:04:21.257Z" },
-    { url = "https://files.pythonhosted.org/packages/cd/97/a4369f2fb82cb3dda13b98622f31249b2e014b223fe64ee534413ad72294/jiter-0.16.0-cp314-cp314t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:0e2e9efbe042210df657bade597f66d6d75723e3d8f45a12ea6d8167ff8bbce3", size = 361747, upload-time = "2026-06-29T13:04:22.677Z" },
-    { url = "https://files.pythonhosted.org/packages/28/51/49b6ed456261646e1906016a6760367a28aacd3c24805e4e5fe64116c1db/jiter-0.16.0-cp314-cp314t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:3f4d9e473a5ce7d27fef8b848df4dc16e283893d3f53b4a585e72c9595f3c284", size = 460225, upload-time = "2026-06-29T13:04:24.441Z" },
-    { url = "https://files.pythonhosted.org/packages/33/b5/5689aff4f66c5b60be63106e591dbfcba2190df97d2c9c7cf052361ddb98/jiter-0.16.0-cp314-cp314t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:8d30a4a1c87713060c8d1cc59a7b6c8fb6b8ef0a6900368014c76c87922a2929", size = 373169, upload-time = "2026-06-29T13:04:25.884Z" },
-    { url = "https://files.pythonhosted.org/packages/a2/96/3ae1b85ee0d6d6cab254fb7f8da018272b932bbf2d69b07e98aa2a96c746/jiter-0.16.0-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:bae96332410f866e5900d809298b1ed82735932986c672495f9701daacd80620", size = 350332, upload-time = "2026-06-29T13:04:27.302Z" },
-    { url = "https://files.pythonhosted.org/packages/15/32/c99d7bafd78986556c95bf60ce84c6cc98786eac56066c12d7f828bb6747/jiter-0.16.0-cp314-cp314t-manylinux_2_31_riscv64.whl", hash = "sha256:da3d7ec75dc83bb18bca888b5edfae0656a26849056c59e05a7728badd17e7af", size = 353377, upload-time = "2026-06-29T13:04:28.731Z" },
-    { url = "https://files.pythonhosted.org/packages/0e/4b/f99a8e571287c3dec766bcc18528bbe8e8fb5365522ab5e6d64c93e87066/jiter-0.16.0-cp314-cp314t-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:ee6162b77d49a9939229df666dfa8af3e656b6701b54c4c84966d740e189264e", size = 387746, upload-time = "2026-06-29T13:04:30.319Z" },
-    { url = "https://files.pythonhosted.org/packages/75/69/c78a5b3f71040e34eb5917df26fb7ae9a2174cad1ccbf277512507c53a6e/jiter-0.16.0-cp314-cp314t-musllinux_1_1_aarch64.whl", hash = "sha256:63ffdbdae7d4499f4cda14eadc12ddcabef0fc0c081191bdc2247489cb698077", size = 517292, upload-time = "2026-06-29T13:04:31.709Z" },
-    { url = "https://files.pythonhosted.org/packages/c2/f7/095b38eda4c70d03651c403f29a5590f16d12ddc5d544aac9f9cddf72277/jiter-0.16.0-cp314-cp314t-musllinux_1_1_x86_64.whl", hash = "sha256:a111256a7193bea0759267b10385e5870949c239ed7b6ddbaaf57573edb38734", size = 549259, upload-time = "2026-06-29T13:04:33.721Z" },
-    { url = "https://files.pythonhosted.org/packages/2e/c5/6a0207d90e5f656d95af98ebd0934f382d37674416f215aeda2ff8063e51/jiter-0.16.0-cp314-cp314t-win32.whl", hash = "sha256:de5ba8763e56b793561f43bed197c9ea55776daa5e9a6b91eed68a909bc9cdbf", size = 206523, upload-time = "2026-06-29T13:04:35.068Z" },
-    { url = "https://files.pythonhosted.org/packages/a5/31/c757d5f30a8980fd945ce7b98be10be9e4ff59c7c42f5fd86804c2e87db8/jiter-0.16.0-cp314-cp314t-win_amd64.whl", hash = "sha256:b8a3f9a6008048fe9def7bf465180564a6e458047d2ce499149cfbe73c3ae9db", size = 200366, upload-time = "2026-06-29T13:04:36.61Z" },
-    { url = "https://files.pythonhosted.org/packages/7c/a2/d88de6d313d734a544a7901353ad5db67cb38dcfcd91713b7979dafc345d/jiter-0.16.0-cp314-cp314t-win_arm64.whl", hash = "sha256:0fa25b09b13075c46f5bc174f2690525a925a4fc2f7c82969a2bbabff22386ce", size = 190516, upload-time = "2026-06-29T13:04:38.004Z" },
-    { url = "https://files.pythonhosted.org/packages/98/ab/664fd8c4be028b2bedd3d2ff08769c4ede23d0dbc87a77c62384a0515b5d/jiter-0.16.0-graalpy312-graalpy250_312_native-macosx_10_12_x86_64.whl", hash = "sha256:f17d61a28b4b3e0e3e2ba98490c70501403b4d196f78732439160e7fd3678127", size = 303106, upload-time = "2026-06-29T13:05:07.118Z" },
-    { url = "https://files.pythonhosted.org/packages/1a/07/421f1d5b65493a76e16027b848aba6a7d28073ae75944fa4289cc914d39f/jiter-0.16.0-graalpy312-graalpy250_312_native-macosx_11_0_arm64.whl", hash = "sha256:96e38eea538c8ddf853a35727c7be0741c76c13f04148ac5c116222f50ece3b3", size = 304658, upload-time = "2026-06-29T13:05:08.708Z" },
-    { url = "https://files.pythonhosted.org/packages/0a/db/bba1155f01a01c3c37a89425d571da751bbedf5c54247b831a04cb971798/jiter-0.16.0-graalpy312-graalpy250_312_native-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:d284fb8d94d5855d60c44fefcab4bf966f1da6fada73992b01f6f0c9bc0c6702", size = 339719, upload-time = "2026-06-29T13:05:10.41Z" },
-    { url = "https://files.pythonhosted.org/packages/78/f7/18a1afcd64f35314b68c1f23afcd9994d0bc13e65cc77517afff4e83986d/jiter-0.16.0-graalpy312-graalpy250_312_native-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:64d613743df53199b1aa256a7d328340da6d7078aac7705a7db9d7a791e9cfd2", size = 343885, upload-time = "2026-06-29T13:05:12.087Z" },
-]
-
-[[package]]
-name = "jmespath"
-version = "1.1.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/d3/59/322338183ecda247fb5d1763a6cbe46eff7222eaeebafd9fa65d4bf5cb11/jmespath-1.1.0.tar.gz", hash = "sha256:472c87d80f36026ae83c6ddd0f1d05d4e510134ed462851fd5f754c8c3cbb88d", size = 27377, upload-time = "2026-01-22T16:35:26.279Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/14/2f/967ba146e6d58cf6a652da73885f52fc68001525b4197effc174321d70b4/jmespath-1.1.0-py3-none-any.whl", hash = "sha256:a5663118de4908c91729bea0acadca56526eb2698e83de10cd116ae0f4e97c64", size = 20419, upload-time = "2026-01-22T16:35:24.919Z" },
-]
-
-[[package]]
-name = "jsonschema"
-version = "4.26.0"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "attrs" },
-    { name = "jsonschema-specifications" },
-    { name = "referencing" },
-    { name = "rpds-py" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/b3/fc/e067678238fa451312d4c62bf6e6cf5ec56375422aee02f9cb5f909b3047/jsonschema-4.26.0.tar.gz", hash = "sha256:0c26707e2efad8aa1bfc5b7ce170f3fccc2e4918ff85989ba9ffa9facb2be326", size = 366583, upload-time = "2026-01-07T13:41:07.246Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/69/90/f63fb5873511e014207a475e2bb4e8b2e570d655b00ac19a9a0ca0a385ee/jsonschema-4.26.0-py3-none-any.whl", hash = "sha256:d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce", size = 90630, upload-time = "2026-01-07T13:41:05.306Z" },
-]
-
-[[package]]
-name = "jsonschema-specifications"
-version = "2025.9.1"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "referencing" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/19/74/a633ee74eb36c44aa6d1095e7cc5569bebf04342ee146178e2d36600708b/jsonschema_specifications-2025.9.1.tar.gz", hash = "sha256:b540987f239e745613c7a9176f3edb72b832a4ac465cf02712288397832b5e8d", size = 32855, upload-time = "2025-09-08T01:34:59.186Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/41/45/1a4ed80516f02155c51f51e8cedb3c1902296743db0bbc66608a0db2814f/jsonschema_specifications-2025.9.1-py3-none-any.whl", hash = "sha256:98802fee3a11ee76ecaca44429fda8a41bff98b00a0f2838151b113f210cc6fe", size = 18437, upload-time = "2025-09-08T01:34:57.871Z" },
-]
-
-[[package]]
-name = "litellm"
-version = "1.98.0"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "aiohttp" },
-    { name = "boto3" },
-    { name = "click" },
-    { name = "fastuuid" },
-    { name = "httpx" },
-    { name = "importlib-metadata" },
-    { name = "jinja2" },
-    { name = "jsonschema" },
-    { name = "openai" },
-    { name = "pydantic" },
-    { name = "pydantic-settings" },
-    { name = "python-dotenv" },
-    { name = "tiktoken" },
-    { name = "tokenizers" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/9c/97/c9da198af273d700bf44d7d82eb21c5b8078c82574b31856b71b1298234b/litellm-1.98.0.tar.gz", hash = "sha256:0e6ba5d645a73ca6d0ffb4e8ec539d94b6e8fad691f2a54c6819011e6d0de8bf", size = 17577139, upload-time = "2026-08-22T22:19:21.931Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/c8/90/2ef5e33b0a67b309be124a77e5098a261beffe28439221dbbc28e5f02e2e/litellm-1.98.0-cp310-abi3-macosx_10_12_x86_64.whl", hash = "sha256:9fda3497f1ec4686c943ce2aeab5767f8fb4a5989305d4b28d6d5d7e488b850c", size = 24026097, upload-time = "2026-08-22T22:19:03.567Z" },
-    { url = "https://files.pythonhosted.org/packages/b0/56/b4569b4ef3640732d5770e0d3f46a395fd20f35594db1f65629595daed00/litellm-1.98.0-cp310-abi3-macosx_11_0_arm64.whl", hash = "sha256:b89b6a0fc179d881191579f5309e622173dca802ee991b92e382acb918eea437", size = 23683944, upload-time = "2026-08-22T22:19:06.952Z" },
-    { url = "https://files.pythonhosted.org/packages/d9/a7/9f03de0e8d767ff27964ea99bbf07e4c37a12f9d3c168c09f40e068535d4/litellm-1.98.0-cp310-abi3-manylinux_2_28_aarch64.whl", hash = "sha256:3a95260f087a4cf763da85bbeeb2efa82caec243ad2394c9e6362ff747963738", size = 23824066, upload-time = "2026-08-22T22:19:09.714Z" },
-    { url = "https://files.pythonhosted.org/packages/69/de/ab46b521e2a6e6a94a5cb91ba3debd6c4e922feaeb47158a389400b0a0fe/litellm-1.98.0-cp310-abi3-manylinux_2_28_x86_64.whl", hash = "sha256:150993180bf049feafa3e20cf46ca0978c69cc66e2ef1639a47e852c682a4721", size = 24190393, upload-time = "2026-08-22T22:19:12.156Z" },
-    { url = "https://files.pythonhosted.org/packages/c5/0a/d2f549d906b9b267b38b406dde721eb93db21b46ec907ae0a7a2a89a50f6/litellm-1.98.0-cp310-abi3-musllinux_1_2_aarch64.whl", hash = "sha256:54d0bc2aba84644de5e84a265f24e5d436d91592ca5b7cc61cee478db297b0c3", size = 23901211, upload-time = "2026-08-22T22:19:14.708Z" },
-    { url = "https://files.pythonhosted.org/packages/85/08/1bd1653297d9c92eaf04425f8a21da817fcde12e1d9469394c543df19d72/litellm-1.98.0-cp310-abi3-musllinux_1_2_x86_64.whl", hash = "sha256:5e546d4af197c257d320299af11f4619f8e5a29f9bb7ce2d9974dd4b1e045499", size = 24290140, upload-time = "2026-08-22T22:19:17.145Z" },
-    { url = "https://files.pythonhosted.org/packages/de/91/14d11ad7e290137400e5b30bcf23de86f811085f4a46756f60684ed0f064/litellm-1.98.0-cp310-abi3-win_amd64.whl", hash = "sha256:1daac9a9a9d052fdbe58ee711c9924dc81d349d4621286cbd96d77baa12158c4", size = 24079638, upload-time = "2026-08-22T22:19:19.558Z" },
-]
-
-[[package]]
-name = "markupsafe"
-version = "3.0.3"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/7e/99/7690b6d4034fffd95959cbe0c02de8deb3098cc577c67bb6a24fe5d7caa7/markupsafe-3.0.3.tar.gz", hash = "sha256:722695808f4b6457b320fdc131280796bdceb04ab50fe1795cd540799ebe1698", size = 80313, upload-time = "2025-09-27T18:37:40.426Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/5a/72/147da192e38635ada20e0a2e1a51cf8823d2119ce8883f7053879c2199b5/markupsafe-3.0.3-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:d53197da72cc091b024dd97249dfc7794d6a56530370992a5e1a08983ad9230e", size = 11615, upload-time = "2025-09-27T18:36:30.854Z" },
-    { url = "https://files.pythonhosted.org/packages/9a/81/7e4e08678a1f98521201c3079f77db69fb552acd56067661f8c2f534a718/markupsafe-3.0.3-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:1872df69a4de6aead3491198eaf13810b565bdbeec3ae2dc8780f14458ec73ce", size = 12020, upload-time = "2025-09-27T18:36:31.971Z" },
-    { url = "https://files.pythonhosted.org/packages/1e/2c/799f4742efc39633a1b54a92eec4082e4f815314869865d876824c257c1e/markupsafe-3.0.3-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:3a7e8ae81ae39e62a41ec302f972ba6ae23a5c5396c8e60113e9066ef893da0d", size = 24332, upload-time = "2025-09-27T18:36:32.813Z" },
-    { url = "https://files.pythonhosted.org/packages/3c/2e/8d0c2ab90a8c1d9a24f0399058ab8519a3279d1bd4289511d74e909f060e/markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:d6dd0be5b5b189d31db7cda48b91d7e0a9795f31430b7f271219ab30f1d3ac9d", size = 22947, upload-time = "2025-09-27T18:36:33.86Z" },
-    { url = "https://files.pythonhosted.org/packages/2c/54/887f3092a85238093a0b2154bd629c89444f395618842e8b0c41783898ea/markupsafe-3.0.3-cp312-cp312-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:94c6f0bb423f739146aec64595853541634bde58b2135f27f61c1ffd1cd4d16a", size = 21962, upload-time = "2025-09-27T18:36:35.099Z" },
-    { url = "https://files.pythonhosted.org/packages/c9/2f/336b8c7b6f4a4d95e91119dc8521402461b74a485558d8f238a68312f11c/markupsafe-3.0.3-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:be8813b57049a7dc738189df53d69395eba14fb99345e0a5994914a3864c8a4b", size = 23760, upload-time = "2025-09-27T18:36:36.001Z" },
-    { url = "https://files.pythonhosted.org/packages/32/43/67935f2b7e4982ffb50a4d169b724d74b62a3964bc1a9a527f5ac4f1ee2b/markupsafe-3.0.3-cp312-cp312-musllinux_1_2_riscv64.whl", hash = "sha256:83891d0e9fb81a825d9a6d61e3f07550ca70a076484292a70fde82c4b807286f", size = 21529, upload-time = "2025-09-27T18:36:36.906Z" },
-    { url = "https://files.pythonhosted.org/packages/89/e0/4486f11e51bbba8b0c041098859e869e304d1c261e59244baa3d295d47b7/markupsafe-3.0.3-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:77f0643abe7495da77fb436f50f8dab76dbc6e5fd25d39589a0f1fe6548bfa2b", size = 23015, upload-time = "2025-09-27T18:36:37.868Z" },
-    { url = "https://files.pythonhosted.org/packages/2f/e1/78ee7a023dac597a5825441ebd17170785a9dab23de95d2c7508ade94e0e/markupsafe-3.0.3-cp312-cp312-win32.whl", hash = "sha256:d88b440e37a16e651bda4c7c2b930eb586fd15ca7406cb39e211fcff3bf3017d", size = 14540, upload-time = "2025-09-27T18:36:38.761Z" },
-    { url = "https://files.pythonhosted.org/packages/aa/5b/bec5aa9bbbb2c946ca2733ef9c4ca91c91b6a24580193e891b5f7dbe8e1e/markupsafe-3.0.3-cp312-cp312-win_amd64.whl", hash = "sha256:26a5784ded40c9e318cfc2bdb30fe164bdb8665ded9cd64d500a34fb42067b1c", size = 15105, upload-time = "2025-09-27T18:36:39.701Z" },
-    { url = "https://files.pythonhosted.org/packages/e5/f1/216fc1bbfd74011693a4fd837e7026152e89c4bcf3e77b6692fba9923123/markupsafe-3.0.3-cp312-cp312-win_arm64.whl", hash = "sha256:35add3b638a5d900e807944a078b51922212fb3dedb01633a8defc4b01a3c85f", size = 13906, upload-time = "2025-09-27T18:36:40.689Z" },
-    { url = "https://files.pythonhosted.org/packages/38/2f/907b9c7bbba283e68f20259574b13d005c121a0fa4c175f9bed27c4597ff/markupsafe-3.0.3-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:e1cf1972137e83c5d4c136c43ced9ac51d0e124706ee1c8aa8532c1287fa8795", size = 11622, upload-time = "2025-09-27T18:36:41.777Z" },
-    { url = "https://files.pythonhosted.org/packages/9c/d9/5f7756922cdd676869eca1c4e3c0cd0df60ed30199ffd775e319089cb3ed/markupsafe-3.0.3-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:116bb52f642a37c115f517494ea5feb03889e04df47eeff5b130b1808ce7c219", size = 12029, upload-time = "2025-09-27T18:36:43.257Z" },
-    { url = "https://files.pythonhosted.org/packages/00/07/575a68c754943058c78f30db02ee03a64b3c638586fba6a6dd56830b30a3/markupsafe-3.0.3-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:133a43e73a802c5562be9bbcd03d090aa5a1fe899db609c29e8c8d815c5f6de6", size = 24374, upload-time = "2025-09-27T18:36:44.508Z" },
-    { url = "https://files.pythonhosted.org/packages/a9/21/9b05698b46f218fc0e118e1f8168395c65c8a2c750ae2bab54fc4bd4e0e8/markupsafe-3.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:ccfcd093f13f0f0b7fdd0f198b90053bf7b2f02a3927a30e63f3ccc9df56b676", size = 22980, upload-time = "2025-09-27T18:36:45.385Z" },
-    { url = "https://files.pythonhosted.org/packages/7f/71/544260864f893f18b6827315b988c146b559391e6e7e8f7252839b1b846a/markupsafe-3.0.3-cp313-cp313-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:509fa21c6deb7a7a273d629cf5ec029bc209d1a51178615ddf718f5918992ab9", size = 21990, upload-time = "2025-09-27T18:36:46.916Z" },
-    { url = "https://files.pythonhosted.org/packages/c2/28/b50fc2f74d1ad761af2f5dcce7492648b983d00a65b8c0e0cb457c82ebbe/markupsafe-3.0.3-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:a4afe79fb3de0b7097d81da19090f4df4f8d3a2b3adaa8764138aac2e44f3af1", size = 23784, upload-time = "2025-09-27T18:36:47.884Z" },
-    { url = "https://files.pythonhosted.org/packages/ed/76/104b2aa106a208da8b17a2fb72e033a5a9d7073c68f7e508b94916ed47a9/markupsafe-3.0.3-cp313-cp313-musllinux_1_2_riscv64.whl", hash = "sha256:795e7751525cae078558e679d646ae45574b47ed6e7771863fcc079a6171a0fc", size = 21588, upload-time = "2025-09-27T18:36:48.82Z" },
-    { url = "https://files.pythonhosted.org/packages/b5/99/16a5eb2d140087ebd97180d95249b00a03aa87e29cc224056274f2e45fd6/markupsafe-3.0.3-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:8485f406a96febb5140bfeca44a73e3ce5116b2501ac54fe953e488fb1d03b12", size = 23041, upload-time = "2025-09-27T18:36:49.797Z" },
-    { url = "https://files.pythonhosted.org/packages/19/bc/e7140ed90c5d61d77cea142eed9f9c303f4c4806f60a1044c13e3f1471d0/markupsafe-3.0.3-cp313-cp313-win32.whl", hash = "sha256:bdd37121970bfd8be76c5fb069c7751683bdf373db1ed6c010162b2a130248ed", size = 14543, upload-time = "2025-09-27T18:36:51.584Z" },
-    { url = "https://files.pythonhosted.org/packages/05/73/c4abe620b841b6b791f2edc248f556900667a5a1cf023a6646967ae98335/markupsafe-3.0.3-cp313-cp313-win_amd64.whl", hash = "sha256:9a1abfdc021a164803f4d485104931fb8f8c1efd55bc6b748d2f5774e78b62c5", size = 15113, upload-time = "2025-09-27T18:36:52.537Z" },
-    { url = "https://files.pythonhosted.org/packages/f0/3a/fa34a0f7cfef23cf9500d68cb7c32dd64ffd58a12b09225fb03dd37d5b80/markupsafe-3.0.3-cp313-cp313-win_arm64.whl", hash = "sha256:7e68f88e5b8799aa49c85cd116c932a1ac15caaa3f5db09087854d218359e485", size = 13911, upload-time = "2025-09-27T18:36:53.513Z" },
-    { url = "https://files.pythonhosted.org/packages/e4/d7/e05cd7efe43a88a17a37b3ae96e79a19e846f3f456fe79c57ca61356ef01/markupsafe-3.0.3-cp313-cp313t-macosx_10_13_x86_64.whl", hash = "sha256:218551f6df4868a8d527e3062d0fb968682fe92054e89978594c28e642c43a73", size = 11658, upload-time = "2025-09-27T18:36:54.819Z" },
-    { url = "https://files.pythonhosted.org/packages/99/9e/e412117548182ce2148bdeacdda3bb494260c0b0184360fe0d56389b523b/markupsafe-3.0.3-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:3524b778fe5cfb3452a09d31e7b5adefeea8c5be1d43c4f810ba09f2ceb29d37", size = 12066, upload-time = "2025-09-27T18:36:55.714Z" },
-    { url = "https://files.pythonhosted.org/packages/bc/e6/fa0ffcda717ef64a5108eaa7b4f5ed28d56122c9a6d70ab8b72f9f715c80/markupsafe-3.0.3-cp313-cp313t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:4e885a3d1efa2eadc93c894a21770e4bc67899e3543680313b09f139e149ab19", size = 25639, upload-time = "2025-09-27T18:36:56.908Z" },
-    { url = "https://files.pythonhosted.org/packages/96/ec/2102e881fe9d25fc16cb4b25d5f5cde50970967ffa5dddafdb771237062d/markupsafe-3.0.3-cp313-cp313t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:8709b08f4a89aa7586de0aadc8da56180242ee0ada3999749b183aa23df95025", size = 23569, upload-time = "2025-09-27T18:36:57.913Z" },
-    { url = "https://files.pythonhosted.org/packages/4b/30/6f2fce1f1f205fc9323255b216ca8a235b15860c34b6798f810f05828e32/markupsafe-3.0.3-cp313-cp313t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:b8512a91625c9b3da6f127803b166b629725e68af71f8184ae7e7d54686a56d6", size = 23284, upload-time = "2025-09-27T18:36:58.833Z" },
-    { url = "https://files.pythonhosted.org/packages/58/47/4a0ccea4ab9f5dcb6f79c0236d954acb382202721e704223a8aafa38b5c8/markupsafe-3.0.3-cp313-cp313t-musllinux_1_2_aarch64.whl", hash = "sha256:9b79b7a16f7fedff2495d684f2b59b0457c3b493778c9eed31111be64d58279f", size = 24801, upload-time = "2025-09-27T18:36:59.739Z" },
-    { url = "https://files.pythonhosted.org/packages/6a/70/3780e9b72180b6fecb83a4814d84c3bf4b4ae4bf0b19c27196104149734c/markupsafe-3.0.3-cp313-cp313t-musllinux_1_2_riscv64.whl", hash = "sha256:12c63dfb4a98206f045aa9563db46507995f7ef6d83b2f68eda65c307c6829eb", size = 22769, upload-time = "2025-09-27T18:37:00.719Z" },
-    { url = "https://files.pythonhosted.org/packages/98/c5/c03c7f4125180fc215220c035beac6b9cb684bc7a067c84fc69414d315f5/markupsafe-3.0.3-cp313-cp313t-musllinux_1_2_x86_64.whl", hash = "sha256:8f71bc33915be5186016f675cd83a1e08523649b0e33efdb898db577ef5bb009", size = 23642, upload-time = "2025-09-27T18:37:01.673Z" },
-    { url = "https://files.pythonhosted.org/packages/80/d6/2d1b89f6ca4bff1036499b1e29a1d02d282259f3681540e16563f27ebc23/markupsafe-3.0.3-cp313-cp313t-win32.whl", hash = "sha256:69c0b73548bc525c8cb9a251cddf1931d1db4d2258e9599c28c07ef3580ef354", size = 14612, upload-time = "2025-09-27T18:37:02.639Z" },
-    { url = "https://files.pythonhosted.org/packages/2b/98/e48a4bfba0a0ffcf9925fe2d69240bfaa19c6f7507b8cd09c70684a53c1e/markupsafe-3.0.3-cp313-cp313t-win_amd64.whl", hash = "sha256:1b4b79e8ebf6b55351f0d91fe80f893b4743f104bff22e90697db1590e47a218", size = 15200, upload-time = "2025-09-27T18:37:03.582Z" },
-    { url = "https://files.pythonhosted.org/packages/0e/72/e3cc540f351f316e9ed0f092757459afbc595824ca724cbc5a5d4263713f/markupsafe-3.0.3-cp313-cp313t-win_arm64.whl", hash = "sha256:ad2cf8aa28b8c020ab2fc8287b0f823d0a7d8630784c31e9ee5edea20f406287", size = 13973, upload-time = "2025-09-27T18:37:04.929Z" },
-    { url = "https://files.pythonhosted.org/packages/33/8a/8e42d4838cd89b7dde187011e97fe6c3af66d8c044997d2183fbd6d31352/markupsafe-3.0.3-cp314-cp314-macosx_10_13_x86_64.whl", hash = "sha256:eaa9599de571d72e2daf60164784109f19978b327a3910d3e9de8c97b5b70cfe", size = 11619, upload-time = "2025-09-27T18:37:06.342Z" },
-    { url = "https://files.pythonhosted.org/packages/b5/64/7660f8a4a8e53c924d0fa05dc3a55c9cee10bbd82b11c5afb27d44b096ce/markupsafe-3.0.3-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:c47a551199eb8eb2121d4f0f15ae0f923d31350ab9280078d1e5f12b249e0026", size = 12029, upload-time = "2025-09-27T18:37:07.213Z" },
-    { url = "https://files.pythonhosted.org/packages/da/ef/e648bfd021127bef5fa12e1720ffed0c6cbb8310c8d9bea7266337ff06de/markupsafe-3.0.3-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:f34c41761022dd093b4b6896d4810782ffbabe30f2d443ff5f083e0cbbb8c737", size = 24408, upload-time = "2025-09-27T18:37:09.572Z" },
-    { url = "https://files.pythonhosted.org/packages/41/3c/a36c2450754618e62008bf7435ccb0f88053e07592e6028a34776213d877/markupsafe-3.0.3-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:457a69a9577064c05a97c41f4e65148652db078a3a509039e64d3467b9e7ef97", size = 23005, upload-time = "2025-09-27T18:37:10.58Z" },
-    { url = "https://files.pythonhosted.org/packages/bc/20/b7fdf89a8456b099837cd1dc21974632a02a999ec9bf7ca3e490aacd98e7/markupsafe-3.0.3-cp314-cp314-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:e8afc3f2ccfa24215f8cb28dcf43f0113ac3c37c2f0f0806d8c70e4228c5cf4d", size = 22048, upload-time = "2025-09-27T18:37:11.547Z" },
-    { url = "https://files.pythonhosted.org/packages/9a/a7/591f592afdc734f47db08a75793a55d7fbcc6902a723ae4cfbab61010cc5/markupsafe-3.0.3-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:ec15a59cf5af7be74194f7ab02d0f59a62bdcf1a537677ce67a2537c9b87fcda", size = 23821, upload-time = "2025-09-27T18:37:12.48Z" },
-    { url = "https://files.pythonhosted.org/packages/7d/33/45b24e4f44195b26521bc6f1a82197118f74df348556594bd2262bda1038/markupsafe-3.0.3-cp314-cp314-musllinux_1_2_riscv64.whl", hash = "sha256:0eb9ff8191e8498cca014656ae6b8d61f39da5f95b488805da4bb029cccbfbaf", size = 21606, upload-time = "2025-09-27T18:37:13.485Z" },
-    { url = "https://files.pythonhosted.org/packages/ff/0e/53dfaca23a69fbfbbf17a4b64072090e70717344c52eaaaa9c5ddff1e5f0/markupsafe-3.0.3-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:2713baf880df847f2bece4230d4d094280f4e67b1e813eec43b4c0e144a34ffe", size = 23043, upload-time = "2025-09-27T18:37:14.408Z" },
-    { url = "https://files.pythonhosted.org/packages/46/11/f333a06fc16236d5238bfe74daccbca41459dcd8d1fa952e8fbd5dccfb70/markupsafe-3.0.3-cp314-cp314-win32.whl", hash = "sha256:729586769a26dbceff69f7a7dbbf59ab6572b99d94576a5592625d5b411576b9", size = 14747, upload-time = "2025-09-27T18:37:15.36Z" },
-    { url = "https://files.pythonhosted.org/packages/28/52/182836104b33b444e400b14f797212f720cbc9ed6ba34c800639d154e821/markupsafe-3.0.3-cp314-cp314-win_amd64.whl", hash = "sha256:bdc919ead48f234740ad807933cdf545180bfbe9342c2bb451556db2ed958581", size = 15341, upload-time = "2025-09-27T18:37:16.496Z" },
-    { url = "https://files.pythonhosted.org/packages/6f/18/acf23e91bd94fd7b3031558b1f013adfa21a8e407a3fdb32745538730382/markupsafe-3.0.3-cp314-cp314-win_arm64.whl", hash = "sha256:5a7d5dc5140555cf21a6fefbdbf8723f06fcd2f63ef108f2854de715e4422cb4", size = 14073, upload-time = "2025-09-27T18:37:17.476Z" },
-    { url = "https://files.pythonhosted.org/packages/3c/f0/57689aa4076e1b43b15fdfa646b04653969d50cf30c32a102762be2485da/markupsafe-3.0.3-cp314-cp314t-macosx_10_13_x86_64.whl", hash = "sha256:1353ef0c1b138e1907ae78e2f6c63ff67501122006b0f9abad68fda5f4ffc6ab", size = 11661, upload-time = "2025-09-27T18:37:18.453Z" },
-    { url = "https://files.pythonhosted.org/packages/89/c3/2e67a7ca217c6912985ec766c6393b636fb0c2344443ff9d91404dc4c79f/markupsafe-3.0.3-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:1085e7fbddd3be5f89cc898938f42c0b3c711fdcb37d75221de2666af647c175", size = 12069, upload-time = "2025-09-27T18:37:19.332Z" },
-    { url = "https://files.pythonhosted.org/packages/f0/00/be561dce4e6ca66b15276e184ce4b8aec61fe83662cce2f7d72bd3249d28/markupsafe-3.0.3-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:1b52b4fb9df4eb9ae465f8d0c228a00624de2334f216f178a995ccdcf82c4634", size = 25670, upload-time = "2025-09-27T18:37:20.245Z" },
-    { url = "https://files.pythonhosted.org/packages/50/09/c419f6f5a92e5fadde27efd190eca90f05e1261b10dbd8cbcb39cd8ea1dc/markupsafe-3.0.3-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:fed51ac40f757d41b7c48425901843666a6677e3e8eb0abcff09e4ba6e664f50", size = 23598, upload-time = "2025-09-27T18:37:21.177Z" },
-    { url = "https://files.pythonhosted.org/packages/22/44/a0681611106e0b2921b3033fc19bc53323e0b50bc70cffdd19f7d679bb66/markupsafe-3.0.3-cp314-cp314t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:f190daf01f13c72eac4efd5c430a8de82489d9cff23c364c3ea822545032993e", size = 23261, upload-time = "2025-09-27T18:37:22.167Z" },
-    { url = "https://files.pythonhosted.org/packages/5f/57/1b0b3f100259dc9fffe780cfb60d4be71375510e435efec3d116b6436d43/markupsafe-3.0.3-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:e56b7d45a839a697b5eb268c82a71bd8c7f6c94d6fd50c3d577fa39a9f1409f5", size = 24835, upload-time = "2025-09-27T18:37:23.296Z" },
-    { url = "https://files.pythonhosted.org/packages/26/6a/4bf6d0c97c4920f1597cc14dd720705eca0bf7c787aebc6bb4d1bead5388/markupsafe-3.0.3-cp314-cp314t-musllinux_1_2_riscv64.whl", hash = "sha256:f3e98bb3798ead92273dc0e5fd0f31ade220f59a266ffd8a4f6065e0a3ce0523", size = 22733, upload-time = "2025-09-27T18:37:24.237Z" },
-    { url = "https://files.pythonhosted.org/packages/14/c7/ca723101509b518797fedc2fdf79ba57f886b4aca8a7d31857ba3ee8281f/markupsafe-3.0.3-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:5678211cb9333a6468fb8d8be0305520aa073f50d17f089b5b4b477ea6e67fdc", size = 23672, upload-time = "2025-09-27T18:37:25.271Z" },
-    { url = "https://files.pythonhosted.org/packages/fb/df/5bd7a48c256faecd1d36edc13133e51397e41b73bb77e1a69deab746ebac/markupsafe-3.0.3-cp314-cp314t-win32.whl", hash = "sha256:915c04ba3851909ce68ccc2b8e2cd691618c4dc4c4232fb7982bca3f41fd8c3d", size = 14819, upload-time = "2025-09-27T18:37:26.285Z" },
-    { url = "https://files.pythonhosted.org/packages/1a/8a/0402ba61a2f16038b48b39bccca271134be00c5c9f0f623208399333c448/markupsafe-3.0.3-cp314-cp314t-win_amd64.whl", hash = "sha256:4faffd047e07c38848ce017e8725090413cd80cbc23d86e55c587bf979e579c9", size = 15426, upload-time = "2025-09-27T18:37:27.316Z" },
-    { url = "https://files.pythonhosted.org/packages/70/bc/6f1c2f612465f5fa89b95bead1f44dcb607670fd42891d8fdcd5d039f4f4/markupsafe-3.0.3-cp314-cp314t-win_arm64.whl", hash = "sha256:32001d6a8fc98c8cb5c947787c5d08b0a50663d139f1305bac5885d98d9b40fa", size = 14146, upload-time = "2025-09-27T18:37:28.327Z" },
-]
-
-[[package]]
-name = "multidict"
-version = "6.7.1"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/1a/c2/c2d94cbe6ac1753f3fc980da97b3d930efe1da3af3c9f5125354436c073d/multidict-6.7.1.tar.gz", hash = "sha256:ec6652a1bee61c53a3e5776b6049172c53b6aaba34f18c9ad04f82712bac623d", size = 102010, upload-time = "2026-01-26T02:46:45.979Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/8d/9c/f20e0e2cf80e4b2e4b1c365bf5fe104ee633c751a724246262db8f1a0b13/multidict-6.7.1-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:a90f75c956e32891a4eda3639ce6dd86e87105271f43d43442a3aedf3cddf172", size = 76893, upload-time = "2026-01-26T02:43:52.754Z" },
-    { url = "https://files.pythonhosted.org/packages/fe/cf/18ef143a81610136d3da8193da9d80bfe1cb548a1e2d1c775f26b23d024a/multidict-6.7.1-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:3fccb473e87eaa1382689053e4a4618e7ba7b9b9b8d6adf2027ee474597128cd", size = 45456, upload-time = "2026-01-26T02:43:53.893Z" },
-    { url = "https://files.pythonhosted.org/packages/a9/65/1caac9d4cd32e8433908683446eebc953e82d22b03d10d41a5f0fefe991b/multidict-6.7.1-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:b0fa96985700739c4c7853a43c0b3e169360d6855780021bfc6d0f1ce7c123e7", size = 43872, upload-time = "2026-01-26T02:43:55.041Z" },
-    { url = "https://files.pythonhosted.org/packages/cf/3b/d6bd75dc4f3ff7c73766e04e705b00ed6dbbaccf670d9e05a12b006f5a21/multidict-6.7.1-cp312-cp312-manylinux1_i686.manylinux_2_28_i686.manylinux_2_5_i686.whl", hash = "sha256:cb2a55f408c3043e42b40cc8eecd575afa27b7e0b956dfb190de0f8499a57a53", size = 251018, upload-time = "2026-01-26T02:43:56.198Z" },
-    { url = "https://files.pythonhosted.org/packages/fd/80/c959c5933adedb9ac15152e4067c702a808ea183a8b64cf8f31af8ad3155/multidict-6.7.1-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:eb0ce7b2a32d09892b3dd6cc44877a0d02a33241fafca5f25c8b6b62374f8b75", size = 258883, upload-time = "2026-01-26T02:43:57.499Z" },
-    { url = "https://files.pythonhosted.org/packages/86/85/7ed40adafea3d4f1c8b916e3b5cc3a8e07dfcdcb9cd72800f4ed3ca1b387/multidict-6.7.1-cp312-cp312-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:c3a32d23520ee37bf327d1e1a656fec76a2edd5c038bf43eddfa0572ec49c60b", size = 242413, upload-time = "2026-01-26T02:43:58.755Z" },
-    { url = "https://files.pythonhosted.org/packages/d2/57/b8565ff533e48595503c785f8361ff9a4fde4d67de25c207cd0ba3befd03/multidict-6.7.1-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:9c90fed18bffc0189ba814749fdcc102b536e83a9f738a9003e569acd540a733", size = 268404, upload-time = "2026-01-26T02:44:00.216Z" },
-    { url = "https://files.pythonhosted.org/packages/e0/50/9810c5c29350f7258180dfdcb2e52783a0632862eb334c4896ac717cebcb/multidict-6.7.1-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:da62917e6076f512daccfbbde27f46fed1c98fee202f0559adec8ee0de67f71a", size = 269456, upload-time = "2026-01-26T02:44:02.202Z" },
-    { url = "https://files.pythonhosted.org/packages/f3/8d/5e5be3ced1d12966fefb5c4ea3b2a5b480afcea36406559442c6e31d4a48/multidict-6.7.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:bfde23ef6ed9db7eaee6c37dcec08524cb43903c60b285b172b6c094711b3961", size = 256322, upload-time = "2026-01-26T02:44:03.56Z" },
-    { url = "https://files.pythonhosted.org/packages/31/6e/d8a26d81ac166a5592782d208dd90dfdc0a7a218adaa52b45a672b46c122/multidict-6.7.1-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:3758692429e4e32f1ba0df23219cd0b4fc0a52f476726fff9337d1a57676a582", size = 253955, upload-time = "2026-01-26T02:44:04.845Z" },
-    { url = "https://files.pythonhosted.org/packages/59/4c/7c672c8aad41534ba619bcd4ade7a0dc87ed6b8b5c06149b85d3dd03f0cd/multidict-6.7.1-cp312-cp312-musllinux_1_2_armv7l.whl", hash = "sha256:398c1478926eca669f2fd6a5856b6de9c0acf23a2cb59a14c0ba5844fa38077e", size = 251254, upload-time = "2026-01-26T02:44:06.133Z" },
-    { url = "https://files.pythonhosted.org/packages/7b/bd/84c24de512cbafbdbc39439f74e967f19570ce7924e3007174a29c348916/multidict-6.7.1-cp312-cp312-musllinux_1_2_i686.whl", hash = "sha256:c102791b1c4f3ab36ce4101154549105a53dc828f016356b3e3bcae2e3a039d3", size = 252059, upload-time = "2026-01-26T02:44:07.518Z" },
-    { url = "https://files.pythonhosted.org/packages/fa/ba/f5449385510825b73d01c2d4087bf6d2fccc20a2d42ac34df93191d3dd03/multidict-6.7.1-cp312-cp312-musllinux_1_2_ppc64le.whl", hash = "sha256:a088b62bd733e2ad12c50dad01b7d0166c30287c166e137433d3b410add807a6", size = 263588, upload-time = "2026-01-26T02:44:09.382Z" },
-    { url = "https://files.pythonhosted.org/packages/d7/11/afc7c677f68f75c84a69fe37184f0f82fce13ce4b92f49f3db280b7e92b3/multidict-6.7.1-cp312-cp312-musllinux_1_2_s390x.whl", hash = "sha256:3d51ff4785d58d3f6c91bdbffcb5e1f7ddfda557727043aa20d20ec4f65e324a", size = 259642, upload-time = "2026-01-26T02:44:10.73Z" },
-    { url = "https://files.pythonhosted.org/packages/2b/17/ebb9644da78c4ab36403739e0e6e0e30ebb135b9caf3440825001a0bddcb/multidict-6.7.1-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:fc5907494fccf3e7d3f94f95c91d6336b092b5fc83811720fae5e2765890dfba", size = 251377, upload-time = "2026-01-26T02:44:12.042Z" },
-    { url = "https://files.pythonhosted.org/packages/ca/a4/840f5b97339e27846c46307f2530a2805d9d537d8b8bd416af031cad7fa0/multidict-6.7.1-cp312-cp312-win32.whl", hash = "sha256:28ca5ce2fd9716631133d0e9a9b9a745ad7f60bac2bccafb56aa380fc0b6c511", size = 41887, upload-time = "2026-01-26T02:44:14.245Z" },
-    { url = "https://files.pythonhosted.org/packages/80/31/0b2517913687895f5904325c2069d6a3b78f66cc641a86a2baf75a05dcbb/multidict-6.7.1-cp312-cp312-win_amd64.whl", hash = "sha256:fcee94dfbd638784645b066074b338bc9cc155d4b4bffa4adce1615c5a426c19", size = 46053, upload-time = "2026-01-26T02:44:15.371Z" },
-    { url = "https://files.pythonhosted.org/packages/0c/5b/aba28e4ee4006ae4c7df8d327d31025d760ffa992ea23812a601d226e682/multidict-6.7.1-cp312-cp312-win_arm64.whl", hash = "sha256:ba0a9fb644d0c1a2194cf7ffb043bd852cea63a57f66fbd33959f7dae18517bf", size = 43307, upload-time = "2026-01-26T02:44:16.852Z" },
-    { url = "https://files.pythonhosted.org/packages/f2/22/929c141d6c0dba87d3e1d38fbdf1ba8baba86b7776469f2bc2d3227a1e67/multidict-6.7.1-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:2b41f5fed0ed563624f1c17630cb9941cf2309d4df00e494b551b5f3e3d67a23", size = 76174, upload-time = "2026-01-26T02:44:18.509Z" },
-    { url = "https://files.pythonhosted.org/packages/c7/75/bc704ae15fee974f8fccd871305e254754167dce5f9e42d88a2def741a1d/multidict-6.7.1-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:84e61e3af5463c19b67ced91f6c634effb89ef8bfc5ca0267f954451ed4bb6a2", size = 45116, upload-time = "2026-01-26T02:44:19.745Z" },
-    { url = "https://files.pythonhosted.org/packages/79/76/55cd7186f498ed080a18440c9013011eb548f77ae1b297206d030eb1180a/multidict-6.7.1-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:935434b9853c7c112eee7ac891bc4cb86455aa631269ae35442cb316790c1445", size = 43524, upload-time = "2026-01-26T02:44:21.571Z" },
-    { url = "https://files.pythonhosted.org/packages/e9/3c/414842ef8d5a1628d68edee29ba0e5bcf235dbfb3ccd3ea303a7fe8c72ff/multidict-6.7.1-cp313-cp313-manylinux1_i686.manylinux_2_28_i686.manylinux_2_5_i686.whl", hash = "sha256:432feb25a1cb67fe82a9680b4d65fb542e4635cb3166cd9c01560651ad60f177", size = 249368, upload-time = "2026-01-26T02:44:22.803Z" },
-    { url = "https://files.pythonhosted.org/packages/f6/32/befed7f74c458b4a525e60519fe8d87eef72bb1e99924fa2b0f9d97a221e/multidict-6.7.1-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:e82d14e3c948952a1a85503817e038cba5905a3352de76b9a465075d072fba23", size = 256952, upload-time = "2026-01-26T02:44:24.306Z" },
-    { url = "https://files.pythonhosted.org/packages/03/d6/c878a44ba877f366630c860fdf74bfb203c33778f12b6ac274936853c451/multidict-6.7.1-cp313-cp313-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:4cfb48c6ea66c83bcaaf7e4dfa7ec1b6bbcf751b7db85a328902796dfde4c060", size = 240317, upload-time = "2026-01-26T02:44:25.772Z" },
-    { url = "https://files.pythonhosted.org/packages/68/49/57421b4d7ad2e9e60e25922b08ceb37e077b90444bde6ead629095327a6f/multidict-6.7.1-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:1d540e51b7e8e170174555edecddbd5538105443754539193e3e1061864d444d", size = 267132, upload-time = "2026-01-26T02:44:27.648Z" },
-    { url = "https://files.pythonhosted.org/packages/b7/fe/ec0edd52ddbcea2a2e89e174f0206444a61440b40f39704e64dc807a70bd/multidict-6.7.1-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:273d23f4b40f3dce4d6c8a821c741a86dec62cded82e1175ba3d99be128147ed", size = 268140, upload-time = "2026-01-26T02:44:29.588Z" },
-    { url = "https://files.pythonhosted.org/packages/b0/73/6e1b01cbeb458807aa0831742232dbdd1fa92bfa33f52a3f176b4ff3dc11/multidict-6.7.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:9d624335fd4fa1c08a53f8b4be7676ebde19cd092b3895c421045ca87895b429", size = 254277, upload-time = "2026-01-26T02:44:30.902Z" },
-    { url = "https://files.pythonhosted.org/packages/6a/b2/5fb8c124d7561a4974c342bc8c778b471ebbeb3cc17df696f034a7e9afe7/multidict-6.7.1-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:12fad252f8b267cc75b66e8fc51b3079604e8d43a75428ffe193cd9e2195dfd6", size = 252291, upload-time = "2026-01-26T02:44:32.31Z" },
-    { url = "https://files.pythonhosted.org/packages/5a/96/51d4e4e06bcce92577fcd488e22600bd38e4fd59c20cb49434d054903bd2/multidict-6.7.1-cp313-cp313-musllinux_1_2_armv7l.whl", hash = "sha256:03ede2a6ffbe8ef936b92cb4529f27f42be7f56afcdab5ab739cd5f27fb1cbf9", size = 250156, upload-time = "2026-01-26T02:44:33.734Z" },
-    { url = "https://files.pythonhosted.org/packages/db/6b/420e173eec5fba721a50e2a9f89eda89d9c98fded1124f8d5c675f7a0c0f/multidict-6.7.1-cp313-cp313-musllinux_1_2_i686.whl", hash = "sha256:90efbcf47dbe33dcf643a1e400d67d59abeac5db07dc3f27d6bdeae497a2198c", size = 249742, upload-time = "2026-01-26T02:44:35.222Z" },
-    { url = "https://files.pythonhosted.org/packages/44/a3/ec5b5bd98f306bc2aa297b8c6f11a46714a56b1e6ef5ebda50a4f5d7c5fb/multidict-6.7.1-cp313-cp313-musllinux_1_2_ppc64le.whl", hash = "sha256:5c4b9bfc148f5a91be9244d6264c53035c8a0dcd2f51f1c3c6e30e30ebaa1c84", size = 262221, upload-time = "2026-01-26T02:44:36.604Z" },
-    { url = "https://files.pythonhosted.org/packages/cd/f7/e8c0d0da0cd1e28d10e624604e1a36bcc3353aaebdfdc3a43c72bc683a12/multidict-6.7.1-cp313-cp313-musllinux_1_2_s390x.whl", hash = "sha256:401c5a650f3add2472d1d288c26deebc540f99e2fb83e9525007a74cd2116f1d", size = 258664, upload-time = "2026-01-26T02:44:38.008Z" },
-    { url = "https://files.pythonhosted.org/packages/52/da/151a44e8016dd33feed44f730bd856a66257c1ee7aed4f44b649fb7edeb3/multidict-6.7.1-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:97891f3b1b3ffbded884e2916cacf3c6fc87b66bb0dde46f7357404750559f33", size = 249490, upload-time = "2026-01-26T02:44:39.386Z" },
-    { url = "https://files.pythonhosted.org/packages/87/af/a3b86bf9630b732897f6fc3f4c4714b90aa4361983ccbdcd6c0339b21b0c/multidict-6.7.1-cp313-cp313-win32.whl", hash = "sha256:e1c5988359516095535c4301af38d8a8838534158f649c05dd1050222321bcb3", size = 41695, upload-time = "2026-01-26T02:44:41.318Z" },
-    { url = "https://files.pythonhosted.org/packages/b2/35/e994121b0e90e46134673422dd564623f93304614f5d11886b1b3e06f503/multidict-6.7.1-cp313-cp313-win_amd64.whl", hash = "sha256:960c83bf01a95b12b08fd54324a4eb1d5b52c88932b5cba5d6e712bb3ed12eb5", size = 45884, upload-time = "2026-01-26T02:44:42.488Z" },
-    { url = "https://files.pythonhosted.org/packages/ca/61/42d3e5dbf661242a69c97ea363f2d7b46c567da8eadef8890022be6e2ab0/multidict-6.7.1-cp313-cp313-win_arm64.whl", hash = "sha256:563fe25c678aaba333d5399408f5ec3c383ca5b663e7f774dd179a520b8144df", size = 43122, upload-time = "2026-01-26T02:44:43.664Z" },
-    { url = "https://files.pythonhosted.org/packages/6d/b3/e6b21c6c4f314bb956016b0b3ef2162590a529b84cb831c257519e7fde44/multidict-6.7.1-cp313-cp313t-macosx_10_13_universal2.whl", hash = "sha256:c76c4bec1538375dad9d452d246ca5368ad6e1c9039dadcf007ae59c70619ea1", size = 83175, upload-time = "2026-01-26T02:44:44.894Z" },
-    { url = "https://files.pythonhosted.org/packages/fb/76/23ecd2abfe0957b234f6c960f4ade497f55f2c16aeb684d4ecdbf1c95791/multidict-6.7.1-cp313-cp313t-macosx_10_13_x86_64.whl", hash = "sha256:57b46b24b5d5ebcc978da4ec23a819a9402b4228b8a90d9c656422b4bdd8a963", size = 48460, upload-time = "2026-01-26T02:44:46.106Z" },
-    { url = "https://files.pythonhosted.org/packages/c4/57/a0ed92b23f3a042c36bc4227b72b97eca803f5f1801c1ab77c8a212d455e/multidict-6.7.1-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:e954b24433c768ce78ab7929e84ccf3422e46deb45a4dc9f93438f8217fa2d34", size = 46930, upload-time = "2026-01-26T02:44:47.278Z" },
-    { url = "https://files.pythonhosted.org/packages/b5/66/02ec7ace29162e447f6382c495dc95826bf931d3818799bbef11e8f7df1a/multidict-6.7.1-cp313-cp313t-manylinux1_i686.manylinux_2_28_i686.manylinux_2_5_i686.whl", hash = "sha256:3bd231490fa7217cc832528e1cd8752a96f0125ddd2b5749390f7c3ec8721b65", size = 242582, upload-time = "2026-01-26T02:44:48.604Z" },
-    { url = "https://files.pythonhosted.org/packages/58/18/64f5a795e7677670e872673aca234162514696274597b3708b2c0d276cce/multidict-6.7.1-cp313-cp313t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:253282d70d67885a15c8a7716f3a73edf2d635793ceda8173b9ecc21f2fb8292", size = 250031, upload-time = "2026-01-26T02:44:50.544Z" },
-    { url = "https://files.pythonhosted.org/packages/c8/ed/e192291dbbe51a8290c5686f482084d31bcd9d09af24f63358c3d42fd284/multidict-6.7.1-cp313-cp313t-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:0b4c48648d7649c9335cf1927a8b87fa692de3dcb15faa676c6a6f1f1aabda43", size = 228596, upload-time = "2026-01-26T02:44:51.951Z" },
-    { url = "https://files.pythonhosted.org/packages/1e/7e/3562a15a60cf747397e7f2180b0a11dc0c38d9175a650e75fa1b4d325e15/multidict-6.7.1-cp313-cp313t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:98bc624954ec4d2c7cb074b8eefc2b5d0ce7d482e410df446414355d158fe4ca", size = 257492, upload-time = "2026-01-26T02:44:53.902Z" },
-    { url = "https://files.pythonhosted.org/packages/24/02/7d0f9eae92b5249bb50ac1595b295f10e263dd0078ebb55115c31e0eaccd/multidict-6.7.1-cp313-cp313t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:1b99af4d9eec0b49927b4402bcbb58dea89d3e0db8806a4086117019939ad3dd", size = 255899, upload-time = "2026-01-26T02:44:55.316Z" },
-    { url = "https://files.pythonhosted.org/packages/00/e3/9b60ed9e23e64c73a5cde95269ef1330678e9c6e34dd4eb6b431b85b5a10/multidict-6.7.1-cp313-cp313t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:6aac4f16b472d5b7dc6f66a0d49dd57b0e0902090be16594dc9ebfd3d17c47e7", size = 247970, upload-time = "2026-01-26T02:44:56.783Z" },
-    { url = "https://files.pythonhosted.org/packages/3e/06/538e58a63ed5cfb0bd4517e346b91da32fde409d839720f664e9a4ae4f9d/multidict-6.7.1-cp313-cp313t-musllinux_1_2_aarch64.whl", hash = "sha256:21f830fe223215dffd51f538e78c172ed7c7f60c9b96a2bf05c4848ad49921c3", size = 245060, upload-time = "2026-01-26T02:44:58.195Z" },
-    { url = "https://files.pythonhosted.org/packages/b2/2f/d743a3045a97c895d401e9bd29aaa09b94f5cbdf1bd561609e5a6c431c70/multidict-6.7.1-cp313-cp313t-musllinux_1_2_armv7l.whl", hash = "sha256:f5dd81c45b05518b9aa4da4aa74e1c93d715efa234fd3e8a179df611cc85e5f4", size = 235888, upload-time = "2026-01-26T02:44:59.57Z" },
-    { url = "https://files.pythonhosted.org/packages/38/83/5a325cac191ab28b63c52f14f1131f3b0a55ba3b9aa65a6d0bf2a9b921a0/multidict-6.7.1-cp313-cp313t-musllinux_1_2_i686.whl", hash = "sha256:eb304767bca2bb92fb9c5bd33cedc95baee5bb5f6c88e63706533a1c06ad08c8", size = 243554, upload-time = "2026-01-26T02:45:01.054Z" },
-    { url = "https://files.pythonhosted.org/packages/20/1f/9d2327086bd15da2725ef6aae624208e2ef828ed99892b17f60c344e57ed/multidict-6.7.1-cp313-cp313t-musllinux_1_2_ppc64le.whl", hash = "sha256:c9035dde0f916702850ef66460bc4239d89d08df4d02023a5926e7446724212c", size = 252341, upload-time = "2026-01-26T02:45:02.484Z" },
-    { url = "https://files.pythonhosted.org/packages/e8/2c/2a1aa0280cf579d0f6eed8ee5211c4f1730bd7e06c636ba2ee6aafda302e/multidict-6.7.1-cp313-cp313t-musllinux_1_2_s390x.whl", hash = "sha256:af959b9beeb66c822380f222f0e0a1889331597e81f1ded7f374f3ecb0fd6c52", size = 246391, upload-time = "2026-01-26T02:45:03.862Z" },
-    { url = "https://files.pythonhosted.org/packages/e5/03/7ca022ffc36c5a3f6e03b179a5ceb829be9da5783e6fe395f347c0794680/multidict-6.7.1-cp313-cp313t-musllinux_1_2_x86_64.whl", hash = "sha256:41f2952231456154ee479651491e94118229844dd7226541788be783be2b5108", size = 243422, upload-time = "2026-01-26T02:45:05.296Z" },
-    { url = "https://files.pythonhosted.org/packages/dc/1d/b31650eab6c5778aceed46ba735bd97f7c7d2f54b319fa916c0f96e7805b/multidict-6.7.1-cp313-cp313t-win32.whl", hash = "sha256:df9f19c28adcb40b6aae30bbaa1478c389efd50c28d541d76760199fc1037c32", size = 47770, upload-time = "2026-01-26T02:45:06.754Z" },
-    { url = "https://files.pythonhosted.org/packages/ac/5b/2d2d1d522e51285bd61b1e20df8f47ae1a9d80839db0b24ea783b3832832/multidict-6.7.1-cp313-cp313t-win_amd64.whl", hash = "sha256:d54ecf9f301853f2c5e802da559604b3e95bb7a3b01a9c295c6ee591b9882de8", size = 53109, upload-time = "2026-01-26T02:45:08.044Z" },
-    { url = "https://files.pythonhosted.org/packages/3d/a3/cc409ba012c83ca024a308516703cf339bdc4b696195644a7215a5164a24/multidict-6.7.1-cp313-cp313t-win_arm64.whl", hash = "sha256:5a37ca18e360377cfda1d62f5f382ff41f2b8c4ccb329ed974cc2e1643440118", size = 45573, upload-time = "2026-01-26T02:45:09.349Z" },
-    { url = "https://files.pythonhosted.org/packages/91/cc/db74228a8be41884a567e88a62fd589a913708fcf180d029898c17a9a371/multidict-6.7.1-cp314-cp314-macosx_10_15_universal2.whl", hash = "sha256:8f333ec9c5eb1b7105e3b84b53141e66ca05a19a605368c55450b6ba208cb9ee", size = 75190, upload-time = "2026-01-26T02:45:10.651Z" },
-    { url = "https://files.pythonhosted.org/packages/d5/22/492f2246bb5b534abd44804292e81eeaf835388901f0c574bac4eeec73c5/multidict-6.7.1-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:a407f13c188f804c759fc6a9f88286a565c242a76b27626594c133b82883b5c2", size = 44486, upload-time = "2026-01-26T02:45:11.938Z" },
-    { url = "https://files.pythonhosted.org/packages/f1/4f/733c48f270565d78b4544f2baddc2fb2a245e5a8640254b12c36ac7ac68e/multidict-6.7.1-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:0e161ddf326db5577c3a4cc2d8648f81456e8a20d40415541587a71620d7a7d1", size = 43219, upload-time = "2026-01-26T02:45:14.346Z" },
-    { url = "https://files.pythonhosted.org/packages/24/bb/2c0c2287963f4259c85e8bcbba9182ced8d7fca65c780c38e99e61629d11/multidict-6.7.1-cp314-cp314-manylinux1_i686.manylinux_2_28_i686.manylinux_2_5_i686.whl", hash = "sha256:1e3a8bb24342a8201d178c3b4984c26ba81a577c80d4d525727427460a50c22d", size = 245132, upload-time = "2026-01-26T02:45:15.712Z" },
-    { url = "https://files.pythonhosted.org/packages/a7/f9/44d4b3064c65079d2467888794dea218d1601898ac50222ab8a9a8094460/multidict-6.7.1-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:97231140a50f5d447d3164f994b86a0bed7cd016e2682f8650d6a9158e14fd31", size = 252420, upload-time = "2026-01-26T02:45:17.293Z" },
-    { url = "https://files.pythonhosted.org/packages/8b/13/78f7275e73fa17b24c9a51b0bd9d73ba64bb32d0ed51b02a746eb876abe7/multidict-6.7.1-cp314-cp314-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:6b10359683bd8806a200fd2909e7c8ca3a7b24ec1d8132e483d58e791d881048", size = 233510, upload-time = "2026-01-26T02:45:19.356Z" },
-    { url = "https://files.pythonhosted.org/packages/4b/25/8167187f62ae3cbd52da7893f58cb036b47ea3fb67138787c76800158982/multidict-6.7.1-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:283ddac99f7ac25a4acadbf004cb5ae34480bbeb063520f70ce397b281859362", size = 264094, upload-time = "2026-01-26T02:45:20.834Z" },
-    { url = "https://files.pythonhosted.org/packages/a1/e7/69a3a83b7b030cf283fb06ce074a05a02322359783424d7edf0f15fe5022/multidict-6.7.1-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:538cec1e18c067d0e6103aa9a74f9e832904c957adc260e61cd9d8cf0c3b3d37", size = 260786, upload-time = "2026-01-26T02:45:22.818Z" },
-    { url = "https://files.pythonhosted.org/packages/fe/3b/8ec5074bcfc450fe84273713b4b0a0dd47c0249358f5d82eb8104ffe2520/multidict-6.7.1-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:7eee46ccb30ff48a1e35bb818cc90846c6be2b68240e42a78599166722cea709", size = 248483, upload-time = "2026-01-26T02:45:24.368Z" },
-    { url = "https://files.pythonhosted.org/packages/48/5a/d5a99e3acbca0e29c5d9cba8f92ceb15dce78bab963b308ae692981e3a5d/multidict-6.7.1-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:fa263a02f4f2dd2d11a7b1bb4362aa7cb1049f84a9235d31adf63f30143469a0", size = 248403, upload-time = "2026-01-26T02:45:25.982Z" },
-    { url = "https://files.pythonhosted.org/packages/35/48/e58cd31f6c7d5102f2a4bf89f96b9cf7e00b6c6f3d04ecc44417c00a5a3c/multidict-6.7.1-cp314-cp314-musllinux_1_2_armv7l.whl", hash = "sha256:2e1425e2f99ec5bd36c15a01b690a1a2456209c5deed58f95469ffb46039ccbb", size = 240315, upload-time = "2026-01-26T02:45:27.487Z" },
-    { url = "https://files.pythonhosted.org/packages/94/33/1cd210229559cb90b6786c30676bb0c58249ff42f942765f88793b41fdce/multidict-6.7.1-cp314-cp314-musllinux_1_2_i686.whl", hash = "sha256:497394b3239fc6f0e13a78a3e1b61296e72bf1c5f94b4c4eb80b265c37a131cd", size = 245528, upload-time = "2026-01-26T02:45:28.991Z" },
-    { url = "https://files.pythonhosted.org/packages/64/f2/6e1107d226278c876c783056b7db43d800bb64c6131cec9c8dfb6903698e/multidict-6.7.1-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:233b398c29d3f1b9676b4b6f75c518a06fcb2ea0b925119fb2c1bc35c05e1601", size = 258784, upload-time = "2026-01-26T02:45:30.503Z" },
-    { url = "https://files.pythonhosted.org/packages/4d/c1/11f664f14d525e4a1b5327a82d4de61a1db604ab34c6603bb3c2cc63ad34/multidict-6.7.1-cp314-cp314-musllinux_1_2_s390x.whl", hash = "sha256:93b1818e4a6e0930454f0f2af7dfce69307ca03cdcfb3739bf4d91241967b6c1", size = 251980, upload-time = "2026-01-26T02:45:32.603Z" },
-    { url = "https://files.pythonhosted.org/packages/e1/9f/75a9ac888121d0c5bbd4ecf4eead45668b1766f6baabfb3b7f66a410e231/multidict-6.7.1-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:f33dc2a3abe9249ea5d8360f969ec7f4142e7ac45ee7014d8f8d5acddf178b7b", size = 243602, upload-time = "2026-01-26T02:45:34.043Z" },
-    { url = "https://files.pythonhosted.org/packages/9a/e7/50bf7b004cc8525d80dbbbedfdc7aed3e4c323810890be4413e589074032/multidict-6.7.1-cp314-cp314-win32.whl", hash = "sha256:3ab8b9d8b75aef9df299595d5388b14530839f6422333357af1339443cff777d", size = 40930, upload-time = "2026-01-26T02:45:36.278Z" },
-    { url = "https://files.pythonhosted.org/packages/e0/bf/52f25716bbe93745595800f36fb17b73711f14da59ed0bb2eba141bc9f0f/multidict-6.7.1-cp314-cp314-win_amd64.whl", hash = "sha256:5e01429a929600e7dab7b166062d9bb54a5eed752384c7384c968c2afab8f50f", size = 45074, upload-time = "2026-01-26T02:45:37.546Z" },
-    { url = "https://files.pythonhosted.org/packages/97/ab/22803b03285fa3a525f48217963da3a65ae40f6a1b6f6cf2768879e208f9/multidict-6.7.1-cp314-cp314-win_arm64.whl", hash = "sha256:4885cb0e817aef5d00a2e8451d4665c1808378dc27c2705f1bf4ef8505c0d2e5", size = 42471, upload-time = "2026-01-26T02:45:38.889Z" },
-    { url = "https://files.pythonhosted.org/packages/e0/6d/f9293baa6146ba9507e360ea0292b6422b016907c393e2f63fc40ab7b7b5/multidict-6.7.1-cp314-cp314t-macosx_10_15_universal2.whl", hash = "sha256:0458c978acd8e6ea53c81eefaddbbee9c6c5e591f41b3f5e8e194780fe026581", size = 82401, upload-time = "2026-01-26T02:45:40.254Z" },
-    { url = "https://files.pythonhosted.org/packages/7a/68/53b5494738d83558d87c3c71a486504d8373421c3e0dbb6d0db48ad42ee0/multidict-6.7.1-cp314-cp314t-macosx_10_15_x86_64.whl", hash = "sha256:c0abd12629b0af3cf590982c0b413b1e7395cd4ec026f30986818ab95bfaa94a", size = 48143, upload-time = "2026-01-26T02:45:41.635Z" },
-    { url = "https://files.pythonhosted.org/packages/37/e8/5284c53310dcdc99ce5d66563f6e5773531a9b9fe9ec7a615e9bc306b05f/multidict-6.7.1-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:14525a5f61d7d0c94b368a42cff4c9a4e7ba2d52e2672a7b23d84dc86fb02b0c", size = 46507, upload-time = "2026-01-26T02:45:42.99Z" },
-    { url = "https://files.pythonhosted.org/packages/e4/fc/6800d0e5b3875568b4083ecf5f310dcf91d86d52573160834fb4bfcf5e4f/multidict-6.7.1-cp314-cp314t-manylinux1_i686.manylinux_2_28_i686.manylinux_2_5_i686.whl", hash = "sha256:17307b22c217b4cf05033dabefe68255a534d637c6c9b0cc8382718f87be4262", size = 239358, upload-time = "2026-01-26T02:45:44.376Z" },
-    { url = "https://files.pythonhosted.org/packages/41/75/4ad0973179361cdf3a113905e6e088173198349131be2b390f9fa4da5fc6/multidict-6.7.1-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:7a7e590ff876a3eaf1c02a4dfe0724b6e69a9e9de6d8f556816f29c496046e59", size = 246884, upload-time = "2026-01-26T02:45:47.167Z" },
-    { url = "https://files.pythonhosted.org/packages/c3/9c/095bb28b5da139bd41fb9a5d5caff412584f377914bd8787c2aa98717130/multidict-6.7.1-cp314-cp314t-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:5fa6a95dfee63893d80a34758cd0e0c118a30b8dcb46372bf75106c591b77889", size = 225878, upload-time = "2026-01-26T02:45:48.698Z" },
-    { url = "https://files.pythonhosted.org/packages/07/d0/c0a72000243756e8f5a277b6b514fa005f2c73d481b7d9e47cd4568aa2e4/multidict-6.7.1-cp314-cp314t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:a0543217a6a017692aa6ae5cc39adb75e587af0f3a82288b1492eb73dd6cc2a4", size = 253542, upload-time = "2026-01-26T02:45:50.164Z" },
-    { url = "https://files.pythonhosted.org/packages/c0/6b/f69da15289e384ecf2a68837ec8b5ad8c33e973aa18b266f50fe55f24b8c/multidict-6.7.1-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:f99fe611c312b3c1c0ace793f92464d8cd263cc3b26b5721950d977b006b6c4d", size = 252403, upload-time = "2026-01-26T02:45:51.779Z" },
-    { url = "https://files.pythonhosted.org/packages/a2/76/b9669547afa5a1a25cd93eaca91c0da1c095b06b6d2d8ec25b713588d3a1/multidict-6.7.1-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:9004d8386d133b7e6135679424c91b0b854d2d164af6ea3f289f8f2761064609", size = 244889, upload-time = "2026-01-26T02:45:53.27Z" },
-    { url = "https://files.pythonhosted.org/packages/7e/a9/a50d2669e506dad33cfc45b5d574a205587b7b8a5f426f2fbb2e90882588/multidict-6.7.1-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:e628ef0e6859ffd8273c69412a2465c4be4a9517d07261b33334b5ec6f3c7489", size = 241982, upload-time = "2026-01-26T02:45:54.919Z" },
-    { url = "https://files.pythonhosted.org/packages/c5/bb/1609558ad8b456b4827d3c5a5b775c93b87878fd3117ed3db3423dfbce1b/multidict-6.7.1-cp314-cp314t-musllinux_1_2_armv7l.whl", hash = "sha256:841189848ba629c3552035a6a7f5bf3b02eb304e9fea7492ca220a8eda6b0e5c", size = 232415, upload-time = "2026-01-26T02:45:56.981Z" },
-    { url = "https://files.pythonhosted.org/packages/d8/59/6f61039d2aa9261871e03ab9dc058a550d240f25859b05b67fd70f80d4b3/multidict-6.7.1-cp314-cp314t-musllinux_1_2_i686.whl", hash = "sha256:ce1bbd7d780bb5a0da032e095c951f7014d6b0a205f8318308140f1a6aba159e", size = 240337, upload-time = "2026-01-26T02:45:58.698Z" },
-    { url = "https://files.pythonhosted.org/packages/a1/29/fdc6a43c203890dc2ae9249971ecd0c41deaedfe00d25cb6564b2edd99eb/multidict-6.7.1-cp314-cp314t-musllinux_1_2_ppc64le.whl", hash = "sha256:b26684587228afed0d50cf804cc71062cc9c1cdf55051c4c6345d372947b268c", size = 248788, upload-time = "2026-01-26T02:46:00.862Z" },
-    { url = "https://files.pythonhosted.org/packages/a9/14/a153a06101323e4cf086ecee3faadba52ff71633d471f9685c42e3736163/multidict-6.7.1-cp314-cp314t-musllinux_1_2_s390x.whl", hash = "sha256:9f9af11306994335398293f9958071019e3ab95e9a707dc1383a35613f6abcb9", size = 242842, upload-time = "2026-01-26T02:46:02.824Z" },
-    { url = "https://files.pythonhosted.org/packages/41/5f/604ae839e64a4a6efc80db94465348d3b328ee955e37acb24badbcd24d83/multidict-6.7.1-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:b4938326284c4f1224178a560987b6cf8b4d38458b113d9b8c1db1a836e640a2", size = 240237, upload-time = "2026-01-26T02:46:05.898Z" },
-    { url = "https://files.pythonhosted.org/packages/5f/60/c3a5187bf66f6fb546ff4ab8fb5a077cbdd832d7b1908d4365c7f74a1917/multidict-6.7.1-cp314-cp314t-win32.whl", hash = "sha256:98655c737850c064a65e006a3df7c997cd3b220be4ec8fe26215760b9697d4d7", size = 48008, upload-time = "2026-01-26T02:46:07.468Z" },
-    { url = "https://files.pythonhosted.org/packages/0c/f7/addf1087b860ac60e6f382240f64fb99f8bfb532bb06f7c542b83c29ca61/multidict-6.7.1-cp314-cp314t-win_amd64.whl", hash = "sha256:497bde6223c212ba11d462853cfa4f0ae6ef97465033e7dc9940cdb3ab5b48e5", size = 53542, upload-time = "2026-01-26T02:46:08.809Z" },
-    { url = "https://files.pythonhosted.org/packages/4c/81/4629d0aa32302ef7b2ec65c75a728cc5ff4fa410c50096174c1632e70b3e/multidict-6.7.1-cp314-cp314t-win_arm64.whl", hash = "sha256:2bbd113e0d4af5db41d5ebfe9ccaff89de2120578164f86a5d17d5a576d1e5b2", size = 44719, upload-time = "2026-01-26T02:46:11.146Z" },
-    { url = "https://files.pythonhosted.org/packages/81/08/7036c080d7117f28a4af526d794aab6a84463126db031b007717c1a6676e/multidict-6.7.1-py3-none-any.whl", hash = "sha256:55d97cc6dae627efa6a6e548885712d4864b81110ac76fa4e534c03819fa4a56", size = 12319, upload-time = "2026-01-26T02:46:44.004Z" },
-]
-
-[[package]]
-name = "openai"
-version = "2.54.0"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "anyio" },
-    { name = "distro" },
-    { name = "httpx" },
-    { name = "jiter" },
-    { name = "pydantic" },
-    { name = "sniffio" },
-    { name = "tqdm" },
-    { name = "typing-extensions" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/50/9a/8c75e8c8a5b407a0586faeb2afac91674ff955c191ecc1d6d3b6669f6788/openai-2.54.0.tar.gz", hash = "sha256:e3e6f8bc1ba30ddf381ace1a14340eed381cb984a1a59bd0f34b5be3b5d49cfa", size = 1100285, upload-time = "2026-08-11T18:46:59.035Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/64/a8/bb76c7356de8ad57f59d5ff993d434df0607f07f08bcc9c9a5c275e399c0/openai-2.54.0-py3-none-any.whl", hash = "sha256:89089789197ccdb87f173a03145ed1598d00795220c93e96cf712b1cbf5e5f2b", size = 1660351, upload-time = "2026-08-11T18:46:56.684Z" },
-]
-
-[[package]]
-name = "packaging"
-version = "26.3"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/7d/fa/3944b40b07da9ce895c0e6303a5ab7d53da063554f534556b134a54d6093/packaging-26.3.tar.gz", hash = "sha256:94edc256424af38762eb31306eed28beb9f0efc50a8837492c9d6fd6004aed79", size = 313412, upload-time = "2026-08-04T18:15:28.737Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/63/34/ba1c580383c9eada3711951fef0795c80b829a078d72188184bcab9dd527/packaging-26.3-py3-none-any.whl", hash = "sha256:d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c", size = 129956, upload-time = "2026-08-04T18:15:27.159Z" },
-]
-
-[[package]]
-name = "pluggy"
-version = "1.6.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/f9/e2/3e91f31a7d2b083fe6ef3fa267035b518369d9511ffab804f839851d2779/pluggy-1.6.0.tar.gz", hash = "sha256:7dcc130b76258d33b90f61b658791dede3486c3e6bfb003ee5c9bfb396dd22f3", size = 69412, upload-time = "2025-05-15T12:30:07.975Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/54/20/4d324d65cc6d9205fabedc306948156824eb9f0ee1633355a8f7ec5c66bf/pluggy-1.6.0-py3-none-any.whl", hash = "sha256:e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746", size = 20538, upload-time = "2025-05-15T12:30:06.134Z" },
-]
-
-[[package]]
-name = "propcache"
-version = "0.5.2"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/ec/44/c87281c333769159c50594f22610f77398a47ccbfbbf23074e744e86f87c/propcache-0.5.2.tar.gz", hash = "sha256:01c4fc7480cd0598bb4b57022df55b9ca296da7fc5a8760bd8451a7e63a7d427", size = 50208, upload-time = "2026-05-08T21:02:12.199Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/4a/cb/e27bc2b2737a0bb49962b275efa051e8f1c35a936df7d5139b6b658b7dc9/propcache-0.5.2-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:806719138ecd720339a12410fb9614ac9b2b2d3a5fdf8235d56981c36f4039ba", size = 95887, upload-time = "2026-05-08T21:00:11.277Z" },
-    { url = "https://files.pythonhosted.org/packages/e6/13/b8ae04c59392f8d11c6cd9fb4011d1dc7c86b81225c770280300e259ffe1/propcache-0.5.2-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:db2b80ea58eab4f86b2beec3cc8b39e8ff9276ac20e96b7cce43c8ae84cd6b5a", size = 54654, upload-time = "2026-05-08T21:00:12.604Z" },
-    { url = "https://files.pythonhosted.org/packages/2c/7d/49777a3e20b55863d4794384a38acd460c04157b0a00f8602b0d508b8431/propcache-0.5.2-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:e5cbfac9f61484f7e9f3597775500cd3ebe8274e9b050c38f9525c77c97520bf", size = 55190, upload-time = "2026-05-08T21:00:13.935Z" },
-    { url = "https://files.pythonhosted.org/packages/44/c7/085d0cd63062e84044e3f05797749c3f8e3938ff3aeb0eb2f69d43fafc91/propcache-0.5.2-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:5dbc581d2814337da56222fab8dc5f161cd798a434e49bac27930aaef798e144", size = 59995, upload-time = "2026-05-08T21:00:15.526Z" },
-    { url = "https://files.pythonhosted.org/packages/9c/42/32cf8e3009e92b2645cf1e944f701e8ea4e924dffde1ee26db860bcbf7e4/propcache-0.5.2-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:857187f381f88c8e2fa2fe56ab94879d011b883d5a2ee5a1b60a8cd2a06846d9", size = 63422, upload-time = "2026-05-08T21:00:16.824Z" },
-    { url = "https://files.pythonhosted.org/packages/9e/1b/f112433f99fc979431b87a39ef169e3f8df070d99a72792c56d6937ac48b/propcache-0.5.2-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:178b4a2cdaac1818e2bf1c5a99b94383fa73ea5382e032a48dec07dc5668dc42", size = 64342, upload-time = "2026-05-08T21:00:18.362Z" },
-    { url = "https://files.pythonhosted.org/packages/14/15/5574111ae50dd6e879456888c0eadd4c5a869959775854e18e18a6b345f3/propcache-0.5.2-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:6f328175a2cde1f0ff2c4ed8ce968b9dcfb55f3a7153f39e2957ed994da13476", size = 61639, upload-time = "2026-05-08T21:00:19.692Z" },
-    { url = "https://files.pythonhosted.org/packages/cc/da/4d775080b1490c0ae604acda868bd71aabe3a89ed16f2aa4339eb8a283e7/propcache-0.5.2-cp312-cp312-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:5671d09a36b06d0fd4a3da0fccbcae360e9b1570924171a15e9e0997f0249fba", size = 61588, upload-time = "2026-05-08T21:00:21.155Z" },
-    { url = "https://files.pythonhosted.org/packages/04/ac/f076982cbe2195ee9cf32de5a1e46951d9fb399fc207f390562dd0fd8fb2/propcache-0.5.2-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:80168e2ebe4d3ec6599d10ad8f520304ae1cad9b6c5a95372aef1b66b7bfb53a", size = 60029, upload-time = "2026-05-08T21:00:22.713Z" },
-    { url = "https://files.pythonhosted.org/packages/70/60/189be62e0dd898dce3b331e1b8c7a543cd3a405ac0c81fe8ee8a9d5d77e1/propcache-0.5.2-cp312-cp312-musllinux_1_2_armv7l.whl", hash = "sha256:45f11346f884bc47444f6e6647131055844134c3175b629f84952e2b5cd62b64", size = 56774, upload-time = "2026-05-08T21:00:24.001Z" },
-    { url = "https://files.pythonhosted.org/packages/ea/9e/93377b9c7939c1ffae98f878dee955efadfd638078bc86dbc21f9d52f651/propcache-0.5.2-cp312-cp312-musllinux_1_2_ppc64le.whl", hash = "sha256:8e778ebd44ef4f66ed60a0416b06b489687db264a9c0b3620362f26489492913", size = 63532, upload-time = "2026-05-08T21:00:25.545Z" },
-    { url = "https://files.pythonhosted.org/packages/14/f9/590ef6cfb9b8028d516d287812ece32bb0bc5f11fbb9c8bf6b2e6313fec8/propcache-0.5.2-cp312-cp312-musllinux_1_2_riscv64.whl", hash = "sha256:c0cb9ed24c8964e172768d455a38254c2dd8a552905729ce006cad3d3dda59b1", size = 61592, upload-time = "2026-05-08T21:00:27.186Z" },
-    { url = "https://files.pythonhosted.org/packages/b4/5e/70958b3034c297a630bba2f17ca7abc2d5f39a803ad7e370ab79d1ecd022/propcache-0.5.2-cp312-cp312-musllinux_1_2_s390x.whl", hash = "sha256:1d1ad32d9d4355e2be65574fd0bfd3677e7066b009cd5b9b2dee8aa6a6393b33", size = 64788, upload-time = "2026-05-08T21:00:28.8Z" },
-    { url = "https://files.pythonhosted.org/packages/12/fd/77fe5936d8c3086ca9048f7f415f122ed82e53884a9ec193646b42deef06/propcache-0.5.2-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:c80f4ba3e8f00189165999a742ee526ebeccedf6c3f7beb0c7df821e9772435a", size = 62514, upload-time = "2026-05-08T21:00:30.098Z" },
-    { url = "https://files.pythonhosted.org/packages/cf/74/66bd798b5b3be70aa1b391f5cc9d6a0a5532d7fd3b19ec0b213e72e6ad9d/propcache-0.5.2-cp312-cp312-win32.whl", hash = "sha256:8c7972d8f193740d9175f0998ab38717e6cd322d5935c5b0fef8c0d323fd9031", size = 39018, upload-time = "2026-05-08T21:00:31.622Z" },
-    { url = "https://files.pythonhosted.org/packages/61/7c/5c0d34aa3024694d6dcb9271cdbdd08c4e47c1c0ad95ec7e7bc74cdea145/propcache-0.5.2-cp312-cp312-win_amd64.whl", hash = "sha256:d9ee8826a7d47863a08ac44e1a5f611a462eefc3a194b492da242128bec75b42", size = 42322, upload-time = "2026-05-08T21:00:32.918Z" },
-    { url = "https://files.pythonhosted.org/packages/4d/91/875812f1a3feb20ceba818ef39fbe4d92f1081e04ac815c822496d0d038b/propcache-0.5.2-cp312-cp312-win_arm64.whl", hash = "sha256:2800a4a8ead6b28cccd1ec54b59346f0def7922ee1c7598e8499c733cfbb7c84", size = 38172, upload-time = "2026-05-08T21:00:35.124Z" },
-    { url = "https://files.pythonhosted.org/packages/c5/09/f049e45385503fe67db75a6b6186a7b9f0c3930366dc960522c312a825b1/propcache-0.5.2-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:099aaf4b4d1a02265b92a977edf00b5c4f63b3b17ac6de39b0d637c9cac0188a", size = 94457, upload-time = "2026-05-08T21:00:36.355Z" },
-    { url = "https://files.pythonhosted.org/packages/6b/65/83d1d05655baf63113731bd5a1008435e14f8d1e5a06cbe4ec5b23ad7a31/propcache-0.5.2-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:68ce1c44c7a813a7f71ea04315a8c7b330b63db99d059a797a4651bb6f69f117", size = 53835, upload-time = "2026-05-08T21:00:38.072Z" },
-    { url = "https://files.pythonhosted.org/packages/a9/12/a6ba6482bb5ea3260c000c9b20881c95fa11c6b30173715668259f844ed7/propcache-0.5.2-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:fc299c129490f55f254cd90be0deca4764e36e9a7c08b4aa588479a3bbed3098", size = 54545, upload-time = "2026-05-08T21:00:39.319Z" },
-    { url = "https://files.pythonhosted.org/packages/a9/19/7fa086f5764c59ec8a8e157cd93aa8497acc00aba9dcdec56bfffb32602d/propcache-0.5.2-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:a6ae2198be502c10f09b2516e7b5d019816924bc3183a43ce792a7bd6625e6f4", size = 59886, upload-time = "2026-05-08T21:00:40.621Z" },
-    { url = "https://files.pythonhosted.org/packages/a1/e4/5d7663dc8235956c8f5281698a3af1d351d8820341ddd890f59d9a9127f2/propcache-0.5.2-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:6041d31504dc1779d700e1edcfb08eea334b357620b06681a4eabb57a74e574e", size = 63261, upload-time = "2026-05-08T21:00:41.775Z" },
-    { url = "https://files.pythonhosted.org/packages/4a/4a/15a03adee24d6350da4292caeac44c34c033d2afe5e87eb370f38854560f/propcache-0.5.2-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:f7eabc04151c78a9f4d5bbb5f1faf571e4defeb4b585e0fe95b60ff2dbe4d3d7", size = 64184, upload-time = "2026-05-08T21:00:43.018Z" },
-    { url = "https://files.pythonhosted.org/packages/8b/c6/979176efdaa3d239e36d503d5af63a0a773b36662ed8f52e5b6a6d9fd40e/propcache-0.5.2-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:4db0ba63d693afd40d249bd93f842b5f144f8fcbb83de05660373bcf30517b1d", size = 61534, upload-time = "2026-05-08T21:00:44.507Z" },
-    { url = "https://files.pythonhosted.org/packages/c8/22/63e8cd1bae4c2d2be6493b6b7d10566ddafad88137cfbc99964a1119853c/propcache-0.5.2-cp313-cp313-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:1dbcf7675229b35d31abb6547d8ebc8c27a830ac3f9a794edff6254873ec7c0a", size = 61500, upload-time = "2026-05-08T21:00:45.796Z" },
-    { url = "https://files.pythonhosted.org/packages/60/5a/28e5d9acbac1cc9ccb67045e8c1b943aa8d79fdf39c93bd73cacd68008ea/propcache-0.5.2-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:d310c013aad2c72f1c3f2f8dd3279d460a858c551f97aeb8c63e4693cca7b4d2", size = 59994, upload-time = "2026-05-08T21:00:47.093Z" },
-    { url = "https://files.pythonhosted.org/packages/f3/40/db650677f554a95b9c01a7c9d93d629e93a15562f5deb4573c9ee136fed2/propcache-0.5.2-cp313-cp313-musllinux_1_2_armv7l.whl", hash = "sha256:06187263ddad280d05b4d8a8b3bb7d164cbebd469236544a42e6d9b28ac6a4fa", size = 56884, upload-time = "2026-05-08T21:00:48.376Z" },
-    { url = "https://files.pythonhosted.org/packages/80/45/70b39b89516ff8b96bf732fa6fded8cef20f293cb1508690101c3c07ec51/propcache-0.5.2-cp313-cp313-musllinux_1_2_ppc64le.whl", hash = "sha256:3115559b8effafd63b142ea5ed53d63a16ea6469cbc63dce4ee194b42db5d853", size = 63464, upload-time = "2026-05-08T21:00:49.954Z" },
-    { url = "https://files.pythonhosted.org/packages/f9/e2/fa59d3a89eac5534293124af4f1d0d0ada091ce4a0ab4610ce03fd2bdd8d/propcache-0.5.2-cp313-cp313-musllinux_1_2_riscv64.whl", hash = "sha256:c60462af8e6dc30c35407c7237ea908d777b22862bbee27bc4699c0d8bcdc45a", size = 61588, upload-time = "2026-05-08T21:00:51.281Z" },
-    { url = "https://files.pythonhosted.org/packages/0b/97/efb547a55c4bc7381cfb202d6a2239ac621045277bc1ea5dfd3a7f0516c0/propcache-0.5.2-cp313-cp313-musllinux_1_2_s390x.whl", hash = "sha256:40314bca9ac559716fe374094fc81c11dcc34b64fd6c585360f5775690505704", size = 64667, upload-time = "2026-05-08T21:00:52.602Z" },
-    { url = "https://files.pythonhosted.org/packages/92/56/f5c7d9b4b7595d5127da38974d791b2153f3d1eae6c674af3583ace92ad3/propcache-0.5.2-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:cfa21e036ce1e1db2be04ba3b85d2df1bb1702fa01932d984c5464c665228ff4", size = 62463, upload-time = "2026-05-08T21:00:54.303Z" },
-    { url = "https://files.pythonhosted.org/packages/bd/3b/484a3a65fc9f9f60c41dcd17b428bace5389544e2c680994534a20755066/propcache-0.5.2-cp313-cp313-win32.whl", hash = "sha256:f156a3529f38063b6dbaf356e15602a7f95f8055b1295a438433a6386f10463d", size = 38621, upload-time = "2026-05-08T21:00:55.808Z" },
-    { url = "https://files.pythonhosted.org/packages/1c/fd/3f0f10dba4dabad3bf53102be007abf55481067952bde0fdddff439e7c61/propcache-0.5.2-cp313-cp313-win_amd64.whl", hash = "sha256:dfed59d0a5aeb01e242e66ff0300bc4a265a7c05f612d30016f0b60b1017d757", size = 41649, upload-time = "2026-05-08T21:00:57.061Z" },
-    { url = "https://files.pythonhosted.org/packages/90/ec/6ce619cc32bb500a482f811f9cd509368b4e58e638d13f2c68f370d6b475/propcache-0.5.2-cp313-cp313-win_arm64.whl", hash = "sha256:ba338430e87ceb9c8f0cf754de38a9860560261e56c00376debd628698a7364f", size = 37636, upload-time = "2026-05-08T21:00:58.646Z" },
-    { url = "https://files.pythonhosted.org/packages/1b/82/c1d268bbbf2ef981c5bf0fbbe746db617c66e3bcefe431a1aa8943fbe23a/propcache-0.5.2-cp313-cp313t-macosx_10_13_universal2.whl", hash = "sha256:a592f5f3da71c8691c788c13cb6734b6d17663d2e1cb8caddf0673d01ef8847d", size = 98872, upload-time = "2026-05-08T21:00:59.889Z" },
-    { url = "https://files.pythonhosted.org/packages/f4/d4/52c871e73e864e6b34c0e2d58ac1ec5ccd149497ddc7ad2137ae98323a35/propcache-0.5.2-cp313-cp313t-macosx_10_13_x86_64.whl", hash = "sha256:6a997d0489e9668a384fcfd5061b857aa5361de73191cac204d04b889cfbbafa", size = 56257, upload-time = "2026-05-08T21:01:01.195Z" },
-    { url = "https://files.pythonhosted.org/packages/67/f0/9b90ca2a210b3d09bcfcd96ecd0f55545c091535abce2a45de2775cfd357/propcache-0.5.2-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:10734b5484ea113152ee25a91dccedf81631791805d2c9ccb054958e51842c94", size = 56696, upload-time = "2026-05-08T21:01:02.941Z" },
-    { url = "https://files.pythonhosted.org/packages/9d/0e/6e9d4ba07c8e56e21ddec1e75f12148142b21ca83a51871babce095334f4/propcache-0.5.2-cp313-cp313t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:cafca7e56c12bb02ae16d283742bef25a61122e9dab2b5b3f2ccbe589ce32164", size = 62378, upload-time = "2026-05-08T21:01:04.475Z" },
-    { url = "https://files.pythonhosted.org/packages/65/19/c10badaa463dde8a27ce884f8ee2ec37e6035b7c9f5ff0c8f74f06f08dac/propcache-0.5.2-cp313-cp313t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:f064f8d2b59177878b7615df1735cd8fe3462ed6be8c7b217d17a276489c2b7f", size = 65283, upload-time = "2026-05-08T21:01:05.959Z" },
-    { url = "https://files.pythonhosted.org/packages/b0/b6/93bea99ca80e19cef6512a8580e5b7857bbe09422d9daa7fd4ef5723306c/propcache-0.5.2-cp313-cp313t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:f78abfa8dfc32376fd1aacf597b2f2fbbe0ea751419aee718af5d4f82537ef8c", size = 66616, upload-time = "2026-05-08T21:01:07.228Z" },
-    { url = "https://files.pythonhosted.org/packages/83/e4/5c7462e50625f051f37fb38b8224f7639f667184bbd34424ec83819bb1b7/propcache-0.5.2-cp313-cp313t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:f7467da8a9822bf1a55336f877340c5bcbd3c482afc43a99771169f74a26dedc", size = 63773, upload-time = "2026-05-08T21:01:08.514Z" },
-    { url = "https://files.pythonhosted.org/packages/ca/b6/99238894047b13c823be25027e736626cd414a52a5e30d2c3347c2733529/propcache-0.5.2-cp313-cp313t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:a6ddc6ac9e25de626c1f129c1b467d7ecd33ce2237d3fd0c4e429feef0a7ee1f", size = 63664, upload-time = "2026-05-08T21:01:09.874Z" },
-    { url = "https://files.pythonhosted.org/packages/85/1e/a3a1a63116a2b8edb415a8bb9a6f0c34bd03830b1e18e8ce2904e1dc1cf4/propcache-0.5.2-cp313-cp313t-musllinux_1_2_aarch64.whl", hash = "sha256:2f22cbbac9e26a8e864c0985ff1268d5d939d53d9d9411a9824279097e03a2cb", size = 62643, upload-time = "2026-05-08T21:01:11.132Z" },
-    { url = "https://files.pythonhosted.org/packages/e4/03/893cf147de2fc6543c5eaa07ad833170e7e2a2385725bbebe8c0503723bb/propcache-0.5.2-cp313-cp313t-musllinux_1_2_armv7l.whl", hash = "sha256:fc76378c62a0f04d0cd82fbb1a2cd2d7e28fcb40d5873f28a6c44e388aaa2751", size = 59595, upload-time = "2026-05-08T21:01:12.387Z" },
-    { url = "https://files.pythonhosted.org/packages/86/3b/04c1a2e12c57766568ba75ba72b3bf2042818d4c1425fab6fc07155c7cff/propcache-0.5.2-cp313-cp313t-musllinux_1_2_ppc64le.whl", hash = "sha256:acd2c8edba48e31e58a363b8cf4e5c7db3b04b3f9e371f601df30d9b0d244836", size = 65711, upload-time = "2026-05-08T21:01:13.676Z" },
-    { url = "https://files.pythonhosted.org/packages/1c/34/80f8d0099f8d6bacc4de1624c85672681c8cd1149ca2da0e38fd120b817f/propcache-0.5.2-cp313-cp313t-musllinux_1_2_riscv64.whl", hash = "sha256:452b5065457eb9991ec5eb38ff41d6cd4c991c9ac7c531c4d5849ae473a9a13f", size = 64247, upload-time = "2026-05-08T21:01:14.936Z" },
-    { url = "https://files.pythonhosted.org/packages/f3/1a/8b08f3a5f1037e9e370c55883ceeeee0f6dd0416fb2d2d67b8bfc91f2a79/propcache-0.5.2-cp313-cp313t-musllinux_1_2_s390x.whl", hash = "sha256:3430bb2bfe1331885c427745a751e774ee679fd4344f80b97bf879815fe8fa55", size = 67102, upload-time = "2026-05-08T21:01:16.281Z" },
-    { url = "https://files.pythonhosted.org/packages/34/68/8bdb7bb7756d76e005490649d10e4a8369e610c74d619f71e1aedf889e9c/propcache-0.5.2-cp313-cp313t-musllinux_1_2_x86_64.whl", hash = "sha256:cef6cea3922890dd6c9654971001fa797b526c16ab5e1e46c05fd6f877be7568", size = 64964, upload-time = "2026-05-08T21:01:17.57Z" },
-    { url = "https://files.pythonhosted.org/packages/0a/aa/50fb0b5d3968b61a510926ff8b8465f1d6e976b3ab74496d7a4b9fc42515/propcache-0.5.2-cp313-cp313t-win32.whl", hash = "sha256:72d61e16dd78228b58c5d47be830ff3da7e5f139abdf0aef9d86cde1c5cf2191", size = 42546, upload-time = "2026-05-08T21:01:18.946Z" },
-    { url = "https://files.pythonhosted.org/packages/ae/4c/0ddbae64321bd4a95bcbfc19307238016b5b1fee645c84626c8d539e5b74/propcache-0.5.2-cp313-cp313t-win_amd64.whl", hash = "sha256:0958834041a0166d343b8d2cedcd8bcbaeb4fdbe0cf08320c5379f143c3be6e7", size = 46330, upload-time = "2026-05-08T21:01:20.162Z" },
-    { url = "https://files.pythonhosted.org/packages/00/d9/9cddc8efb78d8af264c5ec9f6d10b62f57c515feda8d321595f56010fb23/propcache-0.5.2-cp313-cp313t-win_arm64.whl", hash = "sha256:6de8bd93ddde9b992cf2b2e0d796d501a19026b5b9fd87356d7d0779531a8d96", size = 40521, upload-time = "2026-05-08T21:01:21.399Z" },
-    { url = "https://files.pythonhosted.org/packages/e2/ea/23ee535d90ce8bcc465a3028eb3cc0ce3bd1005f4bb27710b30587de798d/propcache-0.5.2-cp314-cp314-macosx_10_15_universal2.whl", hash = "sha256:46088abff4cba581dea21ae0467a480526cb25aa5f3c269e909f800328bc3999", size = 94662, upload-time = "2026-05-08T21:01:22.683Z" },
-    { url = "https://files.pythonhosted.org/packages/b5/06/c5a52f419b5d8972f8d46a7577476090d8e3263ff589ce40b5ca4968d5be/propcache-0.5.2-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:fc88b26f08d634f7bc819a7852e5214f5802641ab8d9fd5326892292eee1993e", size = 53928, upload-time = "2026-05-08T21:01:23.986Z" },
-    { url = "https://files.pythonhosted.org/packages/63/b1/4260d67d6bd85e58a66b72d54ce15d5de789b6f3870cc6bedf8ff9667401/propcache-0.5.2-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:97797ebb098e670a2f92dd66f32897e30d7615b14e7f59711de23e30a9072539", size = 54650, upload-time = "2026-05-08T21:01:25.305Z" },
-    { url = "https://files.pythonhosted.org/packages/70/06/2f46c318e3307cd7a6a7481def374ce838c0fe20084b39dd54b0879d0e99/propcache-0.5.2-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:ba57fffe4ac99c5d30076161b5866336d97600769bad35cc68f7774b15298a4e", size = 59912, upload-time = "2026-05-08T21:01:26.545Z" },
-    { url = "https://files.pythonhosted.org/packages/4c/29/fe1aebec2ce57ab985a9c382bded1124431f85078113aa222c5d278430d4/propcache-0.5.2-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:583c19759d9eec1e5b69e2fbef36a7d9c326041be9746cb822d335c8cedc2979", size = 63300, upload-time = "2026-05-08T21:01:27.937Z" },
-    { url = "https://files.pythonhosted.org/packages/b4/18/2334b26768b6c82be8c69e83671b767d5ef426aa09b0cba6c2ea47816774/propcache-0.5.2-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:d0326e2e5e1f3163fa306c834e48e8d490e5fae607a097a40c0648109b47ba80", size = 64208, upload-time = "2026-05-08T21:01:29.484Z" },
-    { url = "https://files.pythonhosted.org/packages/2b/76/7f1bfd6afff4c5e38e36a3c6d68eb5f4b7311ea80baf693db78d95b603c4/propcache-0.5.2-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:e00820e192c8dbebcafb383ebbf99030895f09905e7a0eb2e0340a0bcc2bc825", size = 61633, upload-time = "2026-05-08T21:01:31.068Z" },
-    { url = "https://files.pythonhosted.org/packages/c4/46/b3ff8aba2b4953a3e50de2cf72f1b5748b8eca93b15f3dc2c84339084c09/propcache-0.5.2-cp314-cp314-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:c66afea89b1e43725731d2004732a046fe6fe955d51f952c3e95a7314a284a39", size = 61724, upload-time = "2026-05-08T21:01:32.374Z" },
-    { url = "https://files.pythonhosted.org/packages/c5/01/814cfcafbcff954f94c01cf30e097ddc88a076b5440fbcf4570753437d40/propcache-0.5.2-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:d4dc37dec6c6cdad0b57881a5658fd14fbf53e333b1a86cf86559f190e1d9ec4", size = 60069, upload-time = "2026-05-08T21:01:33.67Z" },
-    { url = "https://files.pythonhosted.org/packages/da/68/5c6f7622d510cc666a300687e06fd060c1a43361c0c9b20d284f06d8096a/propcache-0.5.2-cp314-cp314-musllinux_1_2_armv7l.whl", hash = "sha256:5570dbcc97571c15f68068e529c92715a12f8d54030e272d264b377e22bd17a5", size = 57099, upload-time = "2026-05-08T21:01:34.915Z" },
-    { url = "https://files.pythonhosted.org/packages/55/27/9cb0b4c679124085327957d42521c99dba04c88c90c3e55a6f0b633ebccc/propcache-0.5.2-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:f814362777a9f841adddb200ecdf8f5cb1e5a3c4b7a86378edbd6ccb26edd702", size = 63391, upload-time = "2026-05-08T21:01:36.231Z" },
-    { url = "https://files.pythonhosted.org/packages/f0/9d/7258aaa5bdf60fc6f27591eef6fe52768cb0beda7140be477c8b12c9794a/propcache-0.5.2-cp314-cp314-musllinux_1_2_riscv64.whl", hash = "sha256:196913dea116aeb5a2ba95af4ddcb7ea85559ae07d8eee8751688310d09168c3", size = 61626, upload-time = "2026-05-08T21:01:37.545Z" },
-    { url = "https://files.pythonhosted.org/packages/8e/0d/41c602003e8a9b16fe1e7eadf62c7bfba9d5474370b24200bf48b315f45f/propcache-0.5.2-cp314-cp314-musllinux_1_2_s390x.whl", hash = "sha256:6e7b8719005dd1175be4ab1cd25e9b98659a5e0347331506ec6760d2773a7fb5", size = 64781, upload-time = "2026-05-08T21:01:38.83Z" },
-    { url = "https://files.pythonhosted.org/packages/8b/f3/38e66b1856e9bd079deea015bc4a55f7767c0e4db2f7dcf69e7e680ba4ce/propcache-0.5.2-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:51f96d685ab16e88cab128cd37a52c5da540809c8b879fa047731bfcb4ad35a4", size = 62570, upload-time = "2026-05-08T21:01:40.415Z" },
-    { url = "https://files.pythonhosted.org/packages/95/ca/bbfe9b910ce57dde8bb4876b4520fc02a4e89497c10de26be936758a3aaa/propcache-0.5.2-cp314-cp314-win32.whl", hash = "sha256:cc6fc3cc62e8501d3ed62894425040d2728ecddb1ed072737a5c70bd537aa9f0", size = 39436, upload-time = "2026-05-08T21:01:41.654Z" },
-    { url = "https://files.pythonhosted.org/packages/61/d2/45c9defbaa1ea297035d9d4cce9e8f80daafbf19319c6007f157c6256ea9/propcache-0.5.2-cp314-cp314-win_amd64.whl", hash = "sha256:81e3a30b0bb60caa22033dd0f8a3618d1d67356212514f62c57db75cb0ef410c", size = 42373, upload-time = "2026-05-08T21:01:43.041Z" },
-    { url = "https://files.pythonhosted.org/packages/44/68/9ea5103f41d5217d7d6ec24db90018e23aebec070c3f9a6e54d12b841fd8/propcache-0.5.2-cp314-cp314-win_arm64.whl", hash = "sha256:0d2c9bf8528f135dbb805ce027567e09164f7efa51a2be07458a2c0420f292d0", size = 38554, upload-time = "2026-05-08T21:01:44.336Z" },
-    { url = "https://files.pythonhosted.org/packages/8a/81/fadf555f42d3b762eea8a53950b0489fdc0aa9da5f8ed9e10ce0a4e01b48/propcache-0.5.2-cp314-cp314t-macosx_10_15_universal2.whl", hash = "sha256:4bc8ff1feffc6a61c7002ffe84634c41b822e104990ae009f44a0834430070bb", size = 99395, upload-time = "2026-05-08T21:01:45.883Z" },
-    { url = "https://files.pythonhosted.org/packages/f5/c9/c61e134a686949cf7971af3a390148b1156f7be81c73bc0cd12c873e2d48/propcache-0.5.2-cp314-cp314t-macosx_10_15_x86_64.whl", hash = "sha256:79aa3ff0a9b566633b642fa9caf7e21ed1c13d6feca718187873f199e1514078", size = 56653, upload-time = "2026-05-08T21:01:47.307Z" },
-    { url = "https://files.pythonhosted.org/packages/cb/73/daf935ea7048ddd7ec8eec5345b4a40b619d2d178b3c0a0900796bc3c794/propcache-0.5.2-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:1b31822f4474c4036bae62de9402710051d431a606d6a0f907fec79935a071aa", size = 56914, upload-time = "2026-05-08T21:01:48.573Z" },
-    { url = "https://files.pythonhosted.org/packages/79/9f/aba959b435ea18617edd7cf0a7ad0b9c574b8fc7e3d2cd55fb59cb255d33/propcache-0.5.2-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:13fef48778b5a2a756523fdb781326b028ca75e32858b04f2cdd19f394564917", size = 62567, upload-time = "2026-05-08T21:01:49.903Z" },
-    { url = "https://files.pythonhosted.org/packages/6c/a1/859942de9a791ff42f6141736f5b37749b8f53e65edfa49638c67dd67e6a/propcache-0.5.2-cp314-cp314t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:8b73ab70f1a3351fbc71f663b3e645af6dd0329100c353081cf69c37433fc6fe", size = 65542, upload-time = "2026-05-08T21:01:51.204Z" },
-    { url = "https://files.pythonhosted.org/packages/b5/61/315bc0fd6c0fc7f80a528b8afd209e5fc4a875ea79571b91b8f50f442907/propcache-0.5.2-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:5538d2c13d93e4698af7e092b57bc7298fd35d1d58e656ae18f23ee0d0378e03", size = 66845, upload-time = "2026-05-08T21:01:52.539Z" },
-    { url = "https://files.pythonhosted.org/packages/47/f7/9f8122e3132e8e354ac41975ef8f1099be7d5a16bc7ae562734e993665c0/propcache-0.5.2-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:cd645f03898405cabe694fb8bc35241e3a9c332ec85627584fe3de201452b335", size = 63985, upload-time = "2026-05-08T21:01:53.847Z" },
-    { url = "https://files.pythonhosted.org/packages/c8/54/c317819ec157cbf6f35df9df9657a6f82daf34d5faf15948b2f639c2192e/propcache-0.5.2-cp314-cp314t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:a473b3440261e0c60706e732b2ed2f517857344fc21bf48fdfe211e2d98eb285", size = 63999, upload-time = "2026-05-08T21:01:55.179Z" },
-    { url = "https://files.pythonhosted.org/packages/5a/56/387e3f7dfce0a9233df41fb888aa1c30222cb4bbbf09537c02dd9bd85fe2/propcache-0.5.2-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:7afa37062e6650640e932e4cc9297d81f9f42d9944029cc386b8247dea4da837", size = 62779, upload-time = "2026-05-08T21:01:57.489Z" },
-    { url = "https://files.pythonhosted.org/packages/a1/9c/596784cb5824ed61ee960d3f8655a3f0993e107c6e98ab6c818b7fb92ccb/propcache-0.5.2-cp314-cp314t-musllinux_1_2_armv7l.whl", hash = "sha256:8a90efd5777e996e42d568db9ac740b944d691e565cbfd31b2f7832f9184b2b8", size = 59796, upload-time = "2026-05-08T21:01:58.736Z" },
-    { url = "https://files.pythonhosted.org/packages/c2/3d/1a6cfa1726a48542c1e8784a0761421476a5b68e09b7f36bf95eb954aaba/propcache-0.5.2-cp314-cp314t-musllinux_1_2_ppc64le.whl", hash = "sha256:f19bb891234d72535764d703bfed1153cc34f4214d5bd7150aee1eec9e8f4366", size = 66023, upload-time = "2026-05-08T21:02:00.228Z" },
-    { url = "https://files.pythonhosted.org/packages/e4/0e/05fd6990369477076e4e280bcb970de760fddf0161a46e988bc95f7940ec/propcache-0.5.2-cp314-cp314t-musllinux_1_2_riscv64.whl", hash = "sha256:32775082acd2d807ee3db715c7770d38767b817870acfa08c29e057f3c4d5b56", size = 64448, upload-time = "2026-05-08T21:02:01.888Z" },
-    { url = "https://files.pythonhosted.org/packages/cd/86/5f8da315a4309c62c10c0b2516b17492d5d3bbe1bb862b96604db67e2a37/propcache-0.5.2-cp314-cp314t-musllinux_1_2_s390x.whl", hash = "sha256:9282fb1a3bccd038da9f768b927b24a0c753e466c086b7c4f3c6982851eefb2d", size = 67329, upload-time = "2026-05-08T21:02:03.484Z" },
-    { url = "https://files.pythonhosted.org/packages/da/d3/3368efe79ab21f0cdf86ef49895811c9cc933131d4cde1f28a624e22e712/propcache-0.5.2-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:cc49723e2f60d6b32a0f0b08a3fd6d13203c07f1cd9566cfce0f12a917c967a2", size = 65172, upload-time = "2026-05-08T21:02:04.745Z" },
-    { url = "https://files.pythonhosted.org/packages/d5/07/127e8b0bacfb325396196f9d976a22453049b89b9b2b08477cc3145faa44/propcache-0.5.2-cp314-cp314t-win32.whl", hash = "sha256:2d7aa89ebca5acc98cba9d1472d976e394782f587bad6661003602a619fd1821", size = 43813, upload-time = "2026-05-08T21:02:06.025Z" },
-    { url = "https://files.pythonhosted.org/packages/88/fb/46dad6c0ae49ed230ab1b16c890c2b6314e2403e6c412976f4a72d64a527/propcache-0.5.2-cp314-cp314t-win_amd64.whl", hash = "sha256:d447bb0b3054be5818458fbb171208b1d9ff11eba14e18ca18b90cbb45767370", size = 47764, upload-time = "2026-05-08T21:02:07.353Z" },
-    { url = "https://files.pythonhosted.org/packages/e7/c4/a47d0a63aa309d10d59ede6e9d4cff03a344a79d1f0f4cd0cd74997b53e0/propcache-0.5.2-cp314-cp314t-win_arm64.whl", hash = "sha256:fe67a3d11cd9b4efabfa45c3d00ffba2b26811442a73a581a94b67c2b5faccf6", size = 41140, upload-time = "2026-05-08T21:02:09.065Z" },
-    { url = "https://files.pythonhosted.org/packages/3a/ed/1cdcab6ba3d6ab7feca11fc14f0eeea80755bb53ef4e892079f31b10a25f/propcache-0.5.2-py3-none-any.whl", hash = "sha256:be1ddfcbb376e3de5d2e2db1d58d6d67463e6b4f9f040c000de8e300295465fe", size = 14036, upload-time = "2026-05-08T21:02:10.673Z" },
-]
-
-[[package]]
-name = "pydantic"
-version = "2.13.4"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "annotated-types" },
-    { name = "pydantic-core" },
-    { name = "typing-extensions" },
-    { name = "typing-inspection" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/18/a5/b60d21ac674192f8ab0ba4e9fd860690f9b4a6e51ca5df118733b487d8d6/pydantic-2.13.4.tar.gz", hash = "sha256:c40756b57adaa8b1efeeced5c196f3f3b7c435f90e84ea7f443901bec8099ef6", size = 844775, upload-time = "2026-05-06T13:43:05.343Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/fd/7b/122376b1fd3c62c1ed9dc80c931ace4844b3c55407b6fb2d199377c9736f/pydantic-2.13.4-py3-none-any.whl", hash = "sha256:45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba", size = 472262, upload-time = "2026-05-06T13:43:02.641Z" },
-]
-
-[[package]]
-name = "pydantic-core"
-version = "2.46.4"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "typing-extensions" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/9d/56/921726b776ace8d8f5db44c4ef961006580d91dc52b803c489fafd1aa249/pydantic_core-2.46.4.tar.gz", hash = "sha256:62f875393d7f270851f20523dd2e29f082bcc82292d66db2b64ea71f64b6e1c1", size = 471464, upload-time = "2026-05-06T13:37:06.98Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/ce/8c/af022f0af448d7747c5154288d46b5f2bc5f17366eaa0e23e9aa04d59f3b/pydantic_core-2.46.4-cp312-cp312-macosx_10_12_x86_64.whl", hash = "sha256:3245406455a5d98187ec35530fd772b1d799b26667980872c8d4614991e2c4a2", size = 2106158, upload-time = "2026-05-06T13:38:57.215Z" },
-    { url = "https://files.pythonhosted.org/packages/19/95/6195171e385007300f0f5574592e467c568becce2d937a0b6804f218bc49/pydantic_core-2.46.4-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:962ccbab7b642487b1d8b7df90ef677e03134cf1fd8880bf698649b22a69371f", size = 1951724, upload-time = "2026-05-06T13:37:02.697Z" },
-    { url = "https://files.pythonhosted.org/packages/8e/bc/f47d1ff9cbb1620e1b5b697eef06010035735f07820180e74178226b27b3/pydantic_core-2.46.4-cp312-cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:8233f2947cf85404441fd7e0085f53b10c93e0ee78611099b5c7237e36aacbf7", size = 1975742, upload-time = "2026-05-06T13:37:09.448Z" },
-    { url = "https://files.pythonhosted.org/packages/5b/11/9b9a5b0306345664a2da6410877af6e8082481b5884b3ddd78d47c6013ce/pydantic_core-2.46.4-cp312-cp312-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:3a233125ac121aa3ffba9a2b59edfc4a985a76092dc8279586ab4b71390875e7", size = 2052418, upload-time = "2026-05-06T13:37:38.234Z" },
-    { url = "https://files.pythonhosted.org/packages/f1/b7/a65fec226f5d78fc39f4a13c4cc0c768c22b113438f60c14adc9d2865038/pydantic_core-2.46.4-cp312-cp312-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:5b712b53160b79a5850310b912a5ef8e57e56947c8ad690c227f5c9d7e561712", size = 2232274, upload-time = "2026-05-06T13:38:27.753Z" },
-    { url = "https://files.pythonhosted.org/packages/68/f0/92039db98b907ef49269a8271f67db9cb78ae2fc68062ef7e4e77adb5f61/pydantic_core-2.46.4-cp312-cp312-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:9401557acd873c3a7f3eb9383edef8ac4968f9510e340f4808d427e75667e7b4", size = 2309940, upload-time = "2026-05-06T13:38:05.353Z" },
-    { url = "https://files.pythonhosted.org/packages/5f/97/2aab507d3d00ca626e8e57c1eac6a79e4e5fbcc63eb99733ff55d1717f65/pydantic_core-2.46.4-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:926c9541b14b12b1681dca8a0b75feb510b06c6341b70a8e500c2fdcff837cce", size = 2094516, upload-time = "2026-05-06T13:39:10.577Z" },
-    { url = "https://files.pythonhosted.org/packages/22/37/a8aca44d40d737dde2bc05b3c6c07dff0de07ce6f82e9f3167aeaf4d5dea/pydantic_core-2.46.4-cp312-cp312-manylinux_2_31_riscv64.whl", hash = "sha256:56cb4851bcaf3d117eddcef4fe66afd750a50274b0da8e22be256d10e5611987", size = 2136854, upload-time = "2026-05-06T13:40:22.59Z" },
-    { url = "https://files.pythonhosted.org/packages/24/99/fcef1b79238c06a8cbec70819ac722ba76e02bc8ada9b0fd66eba40da01b/pydantic_core-2.46.4-cp312-cp312-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:c68fcd102d71ea85c5b2dfac3f4f8476eff42a9e078fd5faefff6d145063536b", size = 2180306, upload-time = "2026-05-06T13:40:10.666Z" },
-    { url = "https://files.pythonhosted.org/packages/ae/6c/fc44000918855b42779d007ae63b0532794739027b2f417321cddbc44f6a/pydantic_core-2.46.4-cp312-cp312-musllinux_1_1_aarch64.whl", hash = "sha256:b2f69dec1725e79a012d920df1707de5caf7ed5e08f3be4435e25803efc47458", size = 2190044, upload-time = "2026-05-06T13:40:43.231Z" },
-    { url = "https://files.pythonhosted.org/packages/6b/65/d9cadc9f1920d7a127ad2edba16c1db7916e59719285cd6c94600b0080ba/pydantic_core-2.46.4-cp312-cp312-musllinux_1_1_armv7l.whl", hash = "sha256:8d0820e8192167f80d88d64038e609c31452eeca865b4e1d9950a27a4609b00b", size = 2329133, upload-time = "2026-05-06T13:39:57.365Z" },
-    { url = "https://files.pythonhosted.org/packages/d0/cf/c873d91679f3a30bcf5e7ac280ce5573483e72295307685120d0d5ad3416/pydantic_core-2.46.4-cp312-cp312-musllinux_1_1_x86_64.whl", hash = "sha256:fbdb89b3e1c94a30cc5edfce477c6e6a5dc4d8f84665b455c27582f211a1c72c", size = 2374464, upload-time = "2026-05-06T13:38:06.976Z" },
-    { url = "https://files.pythonhosted.org/packages/47/bd/6f2fc8188f31bf10590f1e98e7b306336161fac930a8c514cd7bd828c7dc/pydantic_core-2.46.4-cp312-cp312-win32.whl", hash = "sha256:9aa768456404a8bf48a4406685ac2bec8e72b62c69313734fa3b73cf33b3a894", size = 1974823, upload-time = "2026-05-06T13:40:47.985Z" },
-    { url = "https://files.pythonhosted.org/packages/40/8c/985c1d41ea1107c2534abd9870e4ed5c8e7669b5c308297835c001e7a1c4/pydantic_core-2.46.4-cp312-cp312-win_amd64.whl", hash = "sha256:e9c26f834c65f5752f3f06cb08cb86a913ceb7274d0db6e267808a708b46bc89", size = 2072919, upload-time = "2026-05-06T13:39:21.153Z" },
-    { url = "https://files.pythonhosted.org/packages/c4/ba/f463d006e0c47373ca7ec5e1a261c59dc01ef4d62b2657af925fb0deee3a/pydantic_core-2.46.4-cp312-cp312-win_arm64.whl", hash = "sha256:4fc73cb559bdb54b1134a706a2802a4cddd27a0633f5abb7e53056268751ac6a", size = 2027604, upload-time = "2026-05-06T13:39:03.753Z" },
-    { url = "https://files.pythonhosted.org/packages/51/a2/5d30b469c5267a17b39dec53208222f76a8d351dfac4af661888c5aee77d/pydantic_core-2.46.4-cp313-cp313-macosx_10_12_x86_64.whl", hash = "sha256:5d5902252db0d3cedf8d4a1bc68f70eeb430f7e4c7104c8c476753519b423008", size = 2106306, upload-time = "2026-05-06T13:37:48.029Z" },
-    { url = "https://files.pythonhosted.org/packages/c1/81/4fa520eaffa8bd7d1525e644cd6d39e7d60b1592bc5b516693c7340b50f1/pydantic_core-2.46.4-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:c94f0688e7b8d0a67abf40e57a7eaaecd17cc9586706a31b76c031f63df052b4", size = 1951906, upload-time = "2026-05-06T13:37:17.012Z" },
-    { url = "https://files.pythonhosted.org/packages/03/d5/fd02da45b659668b05923b17ba3a0100a0a3d5541e3bd8fcc4ecb711309e/pydantic_core-2.46.4-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:f027324c56cd5406ca49c124b0db10e56c69064fec039acc571c29020cc87c76", size = 1976802, upload-time = "2026-05-06T13:37:35.113Z" },
-    { url = "https://files.pythonhosted.org/packages/21/f2/95727e1368be3d3ed485eaab7adbd7dda408f33f7a36e8b48e0144002b91/pydantic_core-2.46.4-cp313-cp313-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:e739fee756ba1010f8bcccb534252e85a35fe45ae92c295a06059ce58b74ccd3", size = 2052446, upload-time = "2026-05-06T13:37:12.313Z" },
-    { url = "https://files.pythonhosted.org/packages/9c/86/5d99feea3f77c7234b8718075b23db11532773c1a0dbd9b9490215dc2eeb/pydantic_core-2.46.4-cp313-cp313-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:9d56801be94b86a9da183e5f3766e6310752b99ff647e38b09a9500d88e46e76", size = 2232757, upload-time = "2026-05-06T13:39:01.149Z" },
-    { url = "https://files.pythonhosted.org/packages/d2/3a/508ac615935ef7588cf6d9e9b91309fdc2da751af865e02a9098de88258c/pydantic_core-2.46.4-cp313-cp313-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:2412e734dcb48da14d4e4006b82b46b74f2518b8a26ee7e58c6844a6cd6d03c4", size = 2309275, upload-time = "2026-05-06T13:37:41.406Z" },
-    { url = "https://files.pythonhosted.org/packages/07/f8/41db9de19d7987d6b04715a02b3b40aea467000275d9d758ffaa31af7d50/pydantic_core-2.46.4-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:9551187363ffc0de2a00b2e47c25aeaeb1020b69b668762966df15fc5659dd5a", size = 2094467, upload-time = "2026-05-06T13:39:18.847Z" },
-    { url = "https://files.pythonhosted.org/packages/2c/e2/f35033184cb11d0052daf4416e8e10a502ea2ac006fc4f459aee872727d1/pydantic_core-2.46.4-cp313-cp313-manylinux_2_31_riscv64.whl", hash = "sha256:0186750b482eefa11d7f435892b09c5c606193ef3375bcf94aa00ae6bfb66262", size = 2134417, upload-time = "2026-05-06T13:40:17.944Z" },
-    { url = "https://files.pythonhosted.org/packages/7e/7b/6ceeb1cc90e193862f444ebe373d8fdf613f0a82572dde03fb10734c6c71/pydantic_core-2.46.4-cp313-cp313-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:5855698a4856556d86e8e6cd8434bc3ac0314ee8e12089ae0e143f64c6256e4e", size = 2179782, upload-time = "2026-05-06T13:40:32.618Z" },
-    { url = "https://files.pythonhosted.org/packages/5a/f2/c8d7773ede6af08036423a00ae0ceffce266c3c52a096c435d68c896083f/pydantic_core-2.46.4-cp313-cp313-musllinux_1_1_aarch64.whl", hash = "sha256:cbaf13819775b7f769bf4a1f066cb6df7a28d4480081a589828ef190226881cd", size = 2188782, upload-time = "2026-05-06T13:36:51.018Z" },
-    { url = "https://files.pythonhosted.org/packages/59/31/0c864784e31f09f05cdd87606f08923b9c9e7f6e51dd27f20f62f975ce9f/pydantic_core-2.46.4-cp313-cp313-musllinux_1_1_armv7l.whl", hash = "sha256:633147d34cf4550417f12e2b1a0383973bdf5cdfde212cb09e9a581cf10820be", size = 2328334, upload-time = "2026-05-06T13:40:37.764Z" },
-    { url = "https://files.pythonhosted.org/packages/c2/eb/4f6c8a41efa30baa755590f4141abf3a8c370fab610915733e74134a7270/pydantic_core-2.46.4-cp313-cp313-musllinux_1_1_x86_64.whl", hash = "sha256:82cf5301172168103724d49a1444d3378cb20cdee30b116a1bd6031236298a5d", size = 2372986, upload-time = "2026-05-06T13:39:34.152Z" },
-    { url = "https://files.pythonhosted.org/packages/5b/24/b375a480d53113860c299764bfe9f349a3dc9108b3adc0d7f0d786492ebf/pydantic_core-2.46.4-cp313-cp313-win32.whl", hash = "sha256:9fa8ae11da9e2b3126c6426f147e0fba88d96d65921799bb30c6abd1cb2c97fb", size = 1973693, upload-time = "2026-05-06T13:37:55.072Z" },
-    { url = "https://files.pythonhosted.org/packages/7e/e8/cff247591966f2d22ec8c003cd7587e27b7ba7b81ab2fb888e3ab75dc285/pydantic_core-2.46.4-cp313-cp313-win_amd64.whl", hash = "sha256:6b3ace8194b0e5204818c92802dcdca7fc6d88aabbb799d7c795540d9cd6d292", size = 2071819, upload-time = "2026-05-06T13:38:49.139Z" },
-    { url = "https://files.pythonhosted.org/packages/c6/1a/f4aee670d5670e9e148e0c82c7db98d780be566c6e6a97ee8035528ca0b3/pydantic_core-2.46.4-cp313-cp313-win_arm64.whl", hash = "sha256:184c081504d17f1c1066e430e117142b2c77d9448a97f7b65c6ac9fd9aee238d", size = 2027411, upload-time = "2026-05-06T13:40:45.796Z" },
-    { url = "https://files.pythonhosted.org/packages/8d/74/228a26ddad29c6672b805d9fd78e8d251cd04004fa7eed0e622096cd0250/pydantic_core-2.46.4-cp314-cp314-macosx_10_12_x86_64.whl", hash = "sha256:428e04521a40150c85216fc8b85e8d39fece235a9cf5e383761238c7fa9b96fb", size = 2102079, upload-time = "2026-05-06T13:38:41.019Z" },
-    { url = "https://files.pythonhosted.org/packages/ad/1f/8970b150a4b4365623ae00fc88603491f763c627311ae8031e3111356d6e/pydantic_core-2.46.4-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:23ace664830ee0bfe014a0c7bc248b1f7f25ed7ad103852c317624a1083af462", size = 1952179, upload-time = "2026-05-06T13:36:59.812Z" },
-    { url = "https://files.pythonhosted.org/packages/95/30/5211a831ae054928054b2f79731661087a2bc5c01e825c672b3a4a8f1b3e/pydantic_core-2.46.4-cp314-cp314-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:ce5c1d2a8b27468f433ca974829c44060b8097eedc39933e3c206a90ee49c4a9", size = 1978926, upload-time = "2026-05-06T13:37:39.933Z" },
-    { url = "https://files.pythonhosted.org/packages/57/e9/689668733b1eb67adeef047db3c2e8788fcf65a7fd9c9e2b46b7744fe245/pydantic_core-2.46.4-cp314-cp314-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:7283d57845ecf5a163403eb0702dfc220cc4fbdd18919cb5ccea4f95ee1cdab4", size = 2046785, upload-time = "2026-05-06T13:38:01.995Z" },
-    { url = "https://files.pythonhosted.org/packages/60/d9/6715260422ff50a2109878fd24d948a6c3446bb2664f34ee78cd972b3acd/pydantic_core-2.46.4-cp314-cp314-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:8daafc69c93ee8a0204506a3b6b30f586ef54028f52aeeeb5c4cfc5184fd5914", size = 2228733, upload-time = "2026-05-06T13:40:50.371Z" },
-    { url = "https://files.pythonhosted.org/packages/18/ae/fdb2f64316afca925640f8e70bb1a564b0ec2721c1389e25b8eb4bf9a299/pydantic_core-2.46.4-cp314-cp314-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:cd2213145bcc2ba85884d0ac63d222fece9209678f77b9b4d76f054c561adb28", size = 2307534, upload-time = "2026-05-06T13:37:21.531Z" },
-    { url = "https://files.pythonhosted.org/packages/89/1d/8eff589b45bb8190a9d12c49cfad0f176a5cbd1534908a6b5125e2886239/pydantic_core-2.46.4-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:7a5f930472650a82629163023e630d160863fce524c616f4e5186e5de9d9a49b", size = 2099732, upload-time = "2026-05-06T13:39:31.942Z" },
-    { url = "https://files.pythonhosted.org/packages/06/d5/ee5a3366637fee41dee51a1fc91562dcf12ddbc68fda34e6b253da2324bb/pydantic_core-2.46.4-cp314-cp314-manylinux_2_31_riscv64.whl", hash = "sha256:c1b3f518abeca3aa13c712fd202306e145abf59a18b094a6bafb2d2bbf59192c", size = 2129627, upload-time = "2026-05-06T13:37:25.033Z" },
-    { url = "https://files.pythonhosted.org/packages/94/33/2414be571d2c6a6c4d08be21f9292b6d3fdb08949a97b6dfe985017821db/pydantic_core-2.46.4-cp314-cp314-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:1a7dd0b3ee80d90150e3495a3a13ac34dbcbfd4f012996a6a1d8900e91b5c0fb", size = 2179141, upload-time = "2026-05-06T13:37:14.046Z" },
-    { url = "https://files.pythonhosted.org/packages/7b/79/7daa95be995be0eecc4cf75064cb33f9bbbfe3fe0158caf2f0d4a996a5c7/pydantic_core-2.46.4-cp314-cp314-musllinux_1_1_aarch64.whl", hash = "sha256:3fb702cd90b0446a3a1c5e470bfa0dd23c0233b676a9099ddcc964fa6ca13898", size = 2184325, upload-time = "2026-05-06T13:36:53.615Z" },
-    { url = "https://files.pythonhosted.org/packages/9f/cb/d0a382f5c0de8a222dc61c65348e0ce831b1f68e0a018450d31c2cace3a5/pydantic_core-2.46.4-cp314-cp314-musllinux_1_1_armv7l.whl", hash = "sha256:b8458003118a712e66286df6a707db01c52c0f52f7db8e4a38f0da1d3b94fc4e", size = 2323990, upload-time = "2026-05-06T13:40:29.971Z" },
-    { url = "https://files.pythonhosted.org/packages/05/db/d9ba624cc4a5aced1598e88c04fdbd8310c8a69b9d38b9a3d39ce3a61ed7/pydantic_core-2.46.4-cp314-cp314-musllinux_1_1_x86_64.whl", hash = "sha256:372429a130e469c9cd698925ce5fc50940b7a1336b0d82038e63d5bbc4edc519", size = 2369978, upload-time = "2026-05-06T13:37:23.027Z" },
-    { url = "https://files.pythonhosted.org/packages/f2/20/d15df15ba918c423461905802bfd2981c3af0bfa0e40d05e13edbfa48bc3/pydantic_core-2.46.4-cp314-cp314-win32.whl", hash = "sha256:85bb3611ff1802f3ee7fdd7dbff26b56f343fb432d57a4728fdd49b6ef35e2f4", size = 1966354, upload-time = "2026-05-06T13:38:03.499Z" },
-    { url = "https://files.pythonhosted.org/packages/fc/b6/6b8de4c0a7d7ab3004c439c80c5c1e0a3e8d78bbae19379b01960383d9e5/pydantic_core-2.46.4-cp314-cp314-win_amd64.whl", hash = "sha256:811ff8e9c313ab425368bcbb36e5c4ebd7108c2bbf4e4089cfbb0b01eff63fac", size = 2072238, upload-time = "2026-05-06T13:39:40.807Z" },
-    { url = "https://files.pythonhosted.org/packages/32/36/51eb763beec1f4cf59b1db243a7dcc39cbb41230f050a09b9d69faaf0a48/pydantic_core-2.46.4-cp314-cp314-win_arm64.whl", hash = "sha256:bfec22eab3c8cc2ceec0248aec886624116dc079afa027ecc8ad4a7e62010f8a", size = 2018251, upload-time = "2026-05-06T13:37:26.72Z" },
-    { url = "https://files.pythonhosted.org/packages/e8/91/855af51d625b23aa987116a19e231d2aaef9c4a415273ddc189b79a45fee/pydantic_core-2.46.4-cp314-cp314t-macosx_10_12_x86_64.whl", hash = "sha256:af8244b2bef6aaad6d92cda81372de7f8c8d36c9f0c3ea36e827c60e7d9467a0", size = 2099593, upload-time = "2026-05-06T13:39:47.682Z" },
-    { url = "https://files.pythonhosted.org/packages/fb/1b/8784a54c65edb5f49f0a14d6977cf1b209bba85a4c77445b255c2de58ab3/pydantic_core-2.46.4-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:5a4330cdbc57162e4b3aa303f588ba752257694c9c9be3e7ebb11b4aca659b5d", size = 1935226, upload-time = "2026-05-06T13:40:40.428Z" },
-    { url = "https://files.pythonhosted.org/packages/e8/e7/1955d28d1afc56dd4b3ad7cc0cf39df1b9852964cf16e5d13912756d6d6b/pydantic_core-2.46.4-cp314-cp314t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:29c61fc04a3d840155ff08e475a04809278972fe6aef51e2720554e96367e34b", size = 1974605, upload-time = "2026-05-06T13:37:32.029Z" },
-    { url = "https://files.pythonhosted.org/packages/93/e2/3fedbf0ba7a22850e6e9fd78117f1c0f10f950182344d8a6c535d468fdd8/pydantic_core-2.46.4-cp314-cp314t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:c50f2528cf200c5eed56faf3f4e22fcd5f38c157a8b78576e6ba3168ec35f000", size = 2030777, upload-time = "2026-05-06T13:38:55.239Z" },
-    { url = "https://files.pythonhosted.org/packages/f8/61/46be275fcaaba0b4f5b9669dd852267ce1ff616592dccf7a7845588df091/pydantic_core-2.46.4-cp314-cp314t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:0cbe8b01f948de4286c74cdd6c667aceb38f5c1e26f0693b3983d9d74887c65e", size = 2236641, upload-time = "2026-05-06T13:37:08.096Z" },
-    { url = "https://files.pythonhosted.org/packages/60/db/12e93e46a8bac9988be3c016860f83293daea8c716c029c9ace279036f2f/pydantic_core-2.46.4-cp314-cp314t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:617d7e2ca7dcb8c5cf6bcb8c59b8832c94b36196bbf1cbd1bfb56ed341905edd", size = 2286404, upload-time = "2026-05-06T13:40:20.221Z" },
-    { url = "https://files.pythonhosted.org/packages/e2/4a/4d8b19008f38d31c53b8219cfedc2e3d5de5fe99d90076b7e767de29274f/pydantic_core-2.46.4-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:7027560ee92211647d0d34e3f7cd6f50da56399d26a9c8ad0da286d3869a53f3", size = 2109219, upload-time = "2026-05-06T13:38:12.153Z" },
-    { url = "https://files.pythonhosted.org/packages/88/70/3cbc40978fefb7bb09c6708d40d4ad1a5d70fd7213c3d17f971de868ec1f/pydantic_core-2.46.4-cp314-cp314t-manylinux_2_31_riscv64.whl", hash = "sha256:f99626688942fb746e545232e7726926f3be91b5975f8b55327665fafda991c7", size = 2110594, upload-time = "2026-05-06T13:40:02.971Z" },
-    { url = "https://files.pythonhosted.org/packages/9d/20/b8d36736216e29491125531685b2f9e61aa5b4b2599893f8268551da3338/pydantic_core-2.46.4-cp314-cp314t-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:fc3e9034a63de20e15e8ade85358bc6efc614008cab72898b4b4952bea0509ff", size = 2159542, upload-time = "2026-05-06T13:39:27.506Z" },
-    { url = "https://files.pythonhosted.org/packages/1d/a2/367df868eb584dacf6bf82a389272406d7178e301c4ac82545ab98bc2dd9/pydantic_core-2.46.4-cp314-cp314t-musllinux_1_1_aarch64.whl", hash = "sha256:97e7cf2be5c77b7d1a9713a05605d49460d02c6078d38d8bef3cbe323c548424", size = 2168146, upload-time = "2026-05-06T13:38:31.93Z" },
-    { url = "https://files.pythonhosted.org/packages/c1/b8/4460f77f7e201893f649a29ab355dddd3beee8a97bcb1a320db414f9a06e/pydantic_core-2.46.4-cp314-cp314t-musllinux_1_1_armv7l.whl", hash = "sha256:3bf92c5d0e00fefaab325a4d27828fe6b6e2a21848686b5b60d2d9eeb09d76c6", size = 2306309, upload-time = "2026-05-06T13:37:44.717Z" },
-    { url = "https://files.pythonhosted.org/packages/64/c4/be2639293acd87dc8ddbcec41a73cee9b2ebf996fe6d892a1a74e88ad3f7/pydantic_core-2.46.4-cp314-cp314t-musllinux_1_1_x86_64.whl", hash = "sha256:3ecbc122d18468d06ca279dc26a8c2e2d5acb10943bb35e36ae92096dc3b5565", size = 2369736, upload-time = "2026-05-06T13:37:05.645Z" },
-    { url = "https://files.pythonhosted.org/packages/30/a6/9f9f380dbb301f67023bf8f707aaa75daadf84f7152d95c410fd7e81d994/pydantic_core-2.46.4-cp314-cp314t-win32.whl", hash = "sha256:e846ae7835bf0703ae43f534ab79a867146dadd59dc9ca5c8b53d5c8f7c9ef02", size = 1955575, upload-time = "2026-05-06T13:38:51.116Z" },
-    { url = "https://files.pythonhosted.org/packages/40/1f/f1eb9eb350e795d1af8586289746f5c5677d16043040d63710e22abc43c9/pydantic_core-2.46.4-cp314-cp314t-win_amd64.whl", hash = "sha256:2108ba5c1c1eca18030634489dc544844144ee36357f2f9f780b93e7ddbb44b5", size = 2051624, upload-time = "2026-05-06T13:38:21.672Z" },
-    { url = "https://files.pythonhosted.org/packages/f6/d2/42dd53d0a85c27606f316d3aa5d2869c4e8470a5ed6dec30e4a1abe19192/pydantic_core-2.46.4-cp314-cp314t-win_arm64.whl", hash = "sha256:4fcbe087dbc2068af7eda3aa87634eba216dbda64d1ae73c8684b621d33f6596", size = 2017325, upload-time = "2026-05-06T13:40:52.723Z" },
-    { url = "https://files.pythonhosted.org/packages/9d/1d/8987ad40f65ae1432753072f214fb5c74fe47ffbd0698bb9cbbb585664f8/pydantic_core-2.46.4-graalpy312-graalpy250_312_native-macosx_10_12_x86_64.whl", hash = "sha256:1d8ba486450b14f3b1d63bc521d410ec7565e52f887b9fb671791886436a42f7", size = 2095527, upload-time = "2026-05-06T13:39:52.283Z" },
-    { url = "https://files.pythonhosted.org/packages/64/d3/84c282a7eee1d3ac4c0377546ef5a1ea436ce26840d9ac3b7ed54a377507/pydantic_core-2.46.4-graalpy312-graalpy250_312_native-macosx_11_0_arm64.whl", hash = "sha256:3009f12e4e90b7f88b4f9adb1b0c4a3d58fe7820f3238c190047209d148026df", size = 1936024, upload-time = "2026-05-06T13:40:15.671Z" },
-    { url = "https://files.pythonhosted.org/packages/d7/ca/eac61596cdeb4d7e174d3dc0bd8a6238f14f75f97a24e7b7db4c7e7340a0/pydantic_core-2.46.4-graalpy312-graalpy250_312_native-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:ad785e92e6dc634c21555edc8bd6b64957ab844541bcb96a1366c202951ae526", size = 1990696, upload-time = "2026-05-06T13:38:34.717Z" },
-    { url = "https://files.pythonhosted.org/packages/fa/c3/7c8b240552251faf6b3a957db200fcfbbcec36763c050428b601e0c9b83b/pydantic_core-2.46.4-graalpy312-graalpy250_312_native-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:00c603d540afdd6b80eb39f078f33ebd46211f02f33e34a32d9f053bba711de0", size = 2147590, upload-time = "2026-05-06T13:39:29.883Z" },
-]
-
-[[package]]
-name = "pydantic-settings"
-version = "2.15.0"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "pydantic" },
-    { name = "python-dotenv" },
-    { name = "typing-inspection" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/68/ca/31c57507b13119d7d3cfa1576dad2911a4861e3be07b579395f4e9d393f9/pydantic_settings-2.15.0.tar.gz", hash = "sha256:694b793e84f766ba76a90ebdefc01d0a9a045dab0382bee70393da93712ad117", size = 261253, upload-time = "2026-08-07T09:24:57.419Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/30/a4/2bffa9f8e804325a09867f0e9d30795c80ea9f8d62560bd1b6ad6220eb2f/pydantic_settings-2.15.0-py3-none-any.whl", hash = "sha256:0ba092c291c94baceb5eff768aa0d56400a457585bc0175925a5a5510303da42", size = 69413, upload-time = "2026-08-07T09:24:55.839Z" },
-]
-
-[[package]]
-name = "pygments"
-version = "2.21.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/49/2e/ced460408999b33da6b31b0021b0f37d329e202d4169aeb164493778f25b/pygments-2.21.0.tar.gz", hash = "sha256:610ca751c9bc2492b38eb9a38a7fbc93edbbb2d7182edaf34e66ae493dee5c8c", size = 5005329, upload-time = "2026-08-17T08:02:48.824Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/71/46/17f022dd3e953bf20a04a028a21ec746d942f8d2af30fa0f124fa0e6a684/pygments-2.21.0-py3-none-any.whl", hash = "sha256:2363c69b61c4a97c838da3b130dcd6468f4848992b21a82f2a63ec34377137d9", size = 1250147, upload-time = "2026-08-17T08:02:44.912Z" },
-]
-
-[[package]]
-name = "pytest"
-version = "9.1.1"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "colorama", marker = "sys_platform == 'win32'" },
-    { name = "iniconfig" },
-    { name = "packaging" },
-    { name = "pluggy" },
-    { name = "pygments" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/e4/47/b9efed96c114afcfa3c9d3fe98a76a1d14c74a9e266d397cf6eb64be5e01/pytest-9.1.1.tar.gz", hash = "sha256:1088fbde8f2b49d95a549a195707afa7a76a3ce9bcadc26b6d71f0ffda5fe313", size = 1636369, upload-time = "2026-06-19T10:58:32.857Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/24/25/1de2678b631f5a49215c6c96fff41ba892b0a34df68d6d80292b1b48aa7f/pytest-9.1.1-py3-none-any.whl", hash = "sha256:37a86b45efb9a47a61a36449063e8e18d0cab3161329fc099eb21783169c4f0c", size = 386536, upload-time = "2026-06-19T10:58:31.347Z" },
-]
-
-[[package]]
-name = "python-dateutil"
-version = "2.9.0.post0"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "six" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/66/c0/0c8b6ad9f17a802ee498c46e004a0eb49bc148f2fd230864601a86dcf6db/python-dateutil-2.9.0.post0.tar.gz", hash = "sha256:37dd54208da7e1cd875388217d5e00ebd4179249f90fb72437e91a35459a0ad3", size = 342432, upload-time = "2024-03-01T18:36:20.211Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/ec/57/56b9bcc3c9c6a792fcbaf139543cee77261f3651ca9da0c93f5c1221264b/python_dateutil-2.9.0.post0-py2.py3-none-any.whl", hash = "sha256:a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427", size = 229892, upload-time = "2024-03-01T18:36:18.57Z" },
-]
-
-[[package]]
-name = "python-dotenv"
-version = "1.2.3"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/6a/53/ed9d74092561d4b01a2ef1349d52cdbc135e526c245f366b089cfca6de49/python_dotenv-1.2.3.tar.gz", hash = "sha256:a20a594dabeaa385725aa239d5244871c143ecb356add8a20fcf23773a6c3a35", size = 58945, upload-time = "2026-08-16T16:54:54.067Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/0d/17/c5c6b53ddc18f297992099b3d9ec16c855c0ccc83263a21fe4d1c625ec6c/python_dotenv-1.2.3-py3-none-any.whl", hash = "sha256:904552145e8bfed22162c09dab1c2b9b54fefa7b23ba780f4f26ca0316b0f0d9", size = 22780, upload-time = "2026-08-16T16:54:52.473Z" },
-]
-
-[[package]]
-name = "python-telegram-bot"
-version = "22.8"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "httpcore", marker = "python_full_version >= '3.14'" },
-    { name = "httpx" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/ba/77/153517bb1ac1bba670c6fb1dbf09e1fd0730494b1705934e715391413a0d/python_telegram_bot-22.8.tar.gz", hash = "sha256:f9d3847fcb23ee603477e442800b33bb4adf851a73e0619d2050be879decf1ef", size = 1551700, upload-time = "2026-06-12T08:10:29.1Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/60/7c/ed7d4dd94280bd434173cae9f7a7aedaaab9af128ae4f494423a5687c820/python_telegram_bot-22.8-py3-none-any.whl", hash = "sha256:42373918097f1b837cc4e717d588c19ea79651497ec712bb5b0c76e5e63c50e1", size = 769397, upload-time = "2026-06-12T08:10:27.066Z" },
-]
-
-[[package]]
-name = "pyyaml"
-version = "6.0.3"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/05/8e/961c0007c59b8dd7729d542c61a4d537767a59645b82a0b521206e1e25c2/pyyaml-6.0.3.tar.gz", hash = "sha256:d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f", size = 130960, upload-time = "2025-09-25T21:33:16.546Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/d1/33/422b98d2195232ca1826284a76852ad5a86fe23e31b009c9886b2d0fb8b2/pyyaml-6.0.3-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:7f047e29dcae44602496db43be01ad42fc6f1cc0d8cd6c83d342306c32270196", size = 182063, upload-time = "2025-09-25T21:32:11.445Z" },
-    { url = "https://files.pythonhosted.org/packages/89/a0/6cf41a19a1f2f3feab0e9c0b74134aa2ce6849093d5517a0c550fe37a648/pyyaml-6.0.3-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:fc09d0aa354569bc501d4e787133afc08552722d3ab34836a80547331bb5d4a0", size = 173973, upload-time = "2025-09-25T21:32:12.492Z" },
-    { url = "https://files.pythonhosted.org/packages/ed/23/7a778b6bd0b9a8039df8b1b1d80e2e2ad78aa04171592c8a5c43a56a6af4/pyyaml-6.0.3-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:9149cad251584d5fb4981be1ecde53a1ca46c891a79788c0df828d2f166bda28", size = 775116, upload-time = "2025-09-25T21:32:13.652Z" },
-    { url = "https://files.pythonhosted.org/packages/65/30/d7353c338e12baef4ecc1b09e877c1970bd3382789c159b4f89d6a70dc09/pyyaml-6.0.3-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:5fdec68f91a0c6739b380c83b951e2c72ac0197ace422360e6d5a959d8d97b2c", size = 844011, upload-time = "2025-09-25T21:32:15.21Z" },
-    { url = "https://files.pythonhosted.org/packages/8b/9d/b3589d3877982d4f2329302ef98a8026e7f4443c765c46cfecc8858c6b4b/pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc", size = 807870, upload-time = "2025-09-25T21:32:16.431Z" },
-    { url = "https://files.pythonhosted.org/packages/05/c0/b3be26a015601b822b97d9149ff8cb5ead58c66f981e04fedf4e762f4bd4/pyyaml-6.0.3-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:8dc52c23056b9ddd46818a57b78404882310fb473d63f17b07d5c40421e47f8e", size = 761089, upload-time = "2025-09-25T21:32:17.56Z" },
-    { url = "https://files.pythonhosted.org/packages/be/8e/98435a21d1d4b46590d5459a22d88128103f8da4c2d4cb8f14f2a96504e1/pyyaml-6.0.3-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:41715c910c881bc081f1e8872880d3c650acf13dfa8214bad49ed4cede7c34ea", size = 790181, upload-time = "2025-09-25T21:32:18.834Z" },
-    { url = "https://files.pythonhosted.org/packages/74/93/7baea19427dcfbe1e5a372d81473250b379f04b1bd3c4c5ff825e2327202/pyyaml-6.0.3-cp312-cp312-win32.whl", hash = "sha256:96b533f0e99f6579b3d4d4995707cf36df9100d67e0c8303a0c55b27b5f99bc5", size = 137658, upload-time = "2025-09-25T21:32:20.209Z" },
-    { url = "https://files.pythonhosted.org/packages/86/bf/899e81e4cce32febab4fb42bb97dcdf66bc135272882d1987881a4b519e9/pyyaml-6.0.3-cp312-cp312-win_amd64.whl", hash = "sha256:5fcd34e47f6e0b794d17de1b4ff496c00986e1c83f7ab2fb8fcfe9616ff7477b", size = 154003, upload-time = "2025-09-25T21:32:21.167Z" },
-    { url = "https://files.pythonhosted.org/packages/1a/08/67bd04656199bbb51dbed1439b7f27601dfb576fb864099c7ef0c3e55531/pyyaml-6.0.3-cp312-cp312-win_arm64.whl", hash = "sha256:64386e5e707d03a7e172c0701abfb7e10f0fb753ee1d773128192742712a98fd", size = 140344, upload-time = "2025-09-25T21:32:22.617Z" },
-    { url = "https://files.pythonhosted.org/packages/d1/11/0fd08f8192109f7169db964b5707a2f1e8b745d4e239b784a5a1dd80d1db/pyyaml-6.0.3-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:8da9669d359f02c0b91ccc01cac4a67f16afec0dac22c2ad09f46bee0697eba8", size = 181669, upload-time = "2025-09-25T21:32:23.673Z" },
-    { url = "https://files.pythonhosted.org/packages/b1/16/95309993f1d3748cd644e02e38b75d50cbc0d9561d21f390a76242ce073f/pyyaml-6.0.3-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:2283a07e2c21a2aa78d9c4442724ec1eb15f5e42a723b99cb3d822d48f5f7ad1", size = 173252, upload-time = "2025-09-25T21:32:25.149Z" },
-    { url = "https://files.pythonhosted.org/packages/50/31/b20f376d3f810b9b2371e72ef5adb33879b25edb7a6d072cb7ca0c486398/pyyaml-6.0.3-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:ee2922902c45ae8ccada2c5b501ab86c36525b883eff4255313a253a3160861c", size = 767081, upload-time = "2025-09-25T21:32:26.575Z" },
-    { url = "https://files.pythonhosted.org/packages/49/1e/a55ca81e949270d5d4432fbbd19dfea5321eda7c41a849d443dc92fd1ff7/pyyaml-6.0.3-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:a33284e20b78bd4a18c8c2282d549d10bc8408a2a7ff57653c0cf0b9be0afce5", size = 841159, upload-time = "2025-09-25T21:32:27.727Z" },
-    { url = "https://files.pythonhosted.org/packages/74/27/e5b8f34d02d9995b80abcef563ea1f8b56d20134d8f4e5e81733b1feceb2/pyyaml-6.0.3-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:0f29edc409a6392443abf94b9cf89ce99889a1dd5376d94316ae5145dfedd5d6", size = 801626, upload-time = "2025-09-25T21:32:28.878Z" },
-    { url = "https://files.pythonhosted.org/packages/f9/11/ba845c23988798f40e52ba45f34849aa8a1f2d4af4b798588010792ebad6/pyyaml-6.0.3-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:f7057c9a337546edc7973c0d3ba84ddcdf0daa14533c2065749c9075001090e6", size = 753613, upload-time = "2025-09-25T21:32:30.178Z" },
-    { url = "https://files.pythonhosted.org/packages/3d/e0/7966e1a7bfc0a45bf0a7fb6b98ea03fc9b8d84fa7f2229e9659680b69ee3/pyyaml-6.0.3-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:eda16858a3cab07b80edaf74336ece1f986ba330fdb8ee0d6c0d68fe82bc96be", size = 794115, upload-time = "2025-09-25T21:32:31.353Z" },
-    { url = "https://files.pythonhosted.org/packages/de/94/980b50a6531b3019e45ddeada0626d45fa85cbe22300844a7983285bed3b/pyyaml-6.0.3-cp313-cp313-win32.whl", hash = "sha256:d0eae10f8159e8fdad514efdc92d74fd8d682c933a6dd088030f3834bc8e6b26", size = 137427, upload-time = "2025-09-25T21:32:32.58Z" },
-    { url = "https://files.pythonhosted.org/packages/97/c9/39d5b874e8b28845e4ec2202b5da735d0199dbe5b8fb85f91398814a9a46/pyyaml-6.0.3-cp313-cp313-win_amd64.whl", hash = "sha256:79005a0d97d5ddabfeeea4cf676af11e647e41d81c9a7722a193022accdb6b7c", size = 154090, upload-time = "2025-09-25T21:32:33.659Z" },
-    { url = "https://files.pythonhosted.org/packages/73/e8/2bdf3ca2090f68bb3d75b44da7bbc71843b19c9f2b9cb9b0f4ab7a5a4329/pyyaml-6.0.3-cp313-cp313-win_arm64.whl", hash = "sha256:5498cd1645aa724a7c71c8f378eb29ebe23da2fc0d7a08071d89469bf1d2defb", size = 140246, upload-time = "2025-09-25T21:32:34.663Z" },
-    { url = "https://files.pythonhosted.org/packages/9d/8c/f4bd7f6465179953d3ac9bc44ac1a8a3e6122cf8ada906b4f96c60172d43/pyyaml-6.0.3-cp314-cp314-macosx_10_13_x86_64.whl", hash = "sha256:8d1fab6bb153a416f9aeb4b8763bc0f22a5586065f86f7664fc23339fc1c1fac", size = 181814, upload-time = "2025-09-25T21:32:35.712Z" },
-    { url = "https://files.pythonhosted.org/packages/bd/9c/4d95bb87eb2063d20db7b60faa3840c1b18025517ae857371c4dd55a6b3a/pyyaml-6.0.3-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:34d5fcd24b8445fadc33f9cf348c1047101756fd760b4dacb5c3e99755703310", size = 173809, upload-time = "2025-09-25T21:32:36.789Z" },
-    { url = "https://files.pythonhosted.org/packages/92/b5/47e807c2623074914e29dabd16cbbdd4bf5e9b2db9f8090fa64411fc5382/pyyaml-6.0.3-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:501a031947e3a9025ed4405a168e6ef5ae3126c59f90ce0cd6f2bfc477be31b7", size = 766454, upload-time = "2025-09-25T21:32:37.966Z" },
-    { url = "https://files.pythonhosted.org/packages/02/9e/e5e9b168be58564121efb3de6859c452fccde0ab093d8438905899a3a483/pyyaml-6.0.3-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:b3bc83488de33889877a0f2543ade9f70c67d66d9ebb4ac959502e12de895788", size = 836355, upload-time = "2025-09-25T21:32:39.178Z" },
-    { url = "https://files.pythonhosted.org/packages/88/f9/16491d7ed2a919954993e48aa941b200f38040928474c9e85ea9e64222c3/pyyaml-6.0.3-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:c458b6d084f9b935061bc36216e8a69a7e293a2f1e68bf956dcd9e6cbcd143f5", size = 794175, upload-time = "2025-09-25T21:32:40.865Z" },
-    { url = "https://files.pythonhosted.org/packages/dd/3f/5989debef34dc6397317802b527dbbafb2b4760878a53d4166579111411e/pyyaml-6.0.3-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:7c6610def4f163542a622a73fb39f534f8c101d690126992300bf3207eab9764", size = 755228, upload-time = "2025-09-25T21:32:42.084Z" },
-    { url = "https://files.pythonhosted.org/packages/d7/ce/af88a49043cd2e265be63d083fc75b27b6ed062f5f9fd6cdc223ad62f03e/pyyaml-6.0.3-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:5190d403f121660ce8d1d2c1bb2ef1bd05b5f68533fc5c2ea899bd15f4399b35", size = 789194, upload-time = "2025-09-25T21:32:43.362Z" },
-    { url = "https://files.pythonhosted.org/packages/23/20/bb6982b26a40bb43951265ba29d4c246ef0ff59c9fdcdf0ed04e0687de4d/pyyaml-6.0.3-cp314-cp314-win_amd64.whl", hash = "sha256:4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac", size = 156429, upload-time = "2025-09-25T21:32:57.844Z" },
-    { url = "https://files.pythonhosted.org/packages/f4/f4/a4541072bb9422c8a883ab55255f918fa378ecf083f5b85e87fc2b4eda1b/pyyaml-6.0.3-cp314-cp314-win_arm64.whl", hash = "sha256:93dda82c9c22deb0a405ea4dc5f2d0cda384168e466364dec6255b293923b2f3", size = 143912, upload-time = "2025-09-25T21:32:59.247Z" },
-    { url = "https://files.pythonhosted.org/packages/7c/f9/07dd09ae774e4616edf6cda684ee78f97777bdd15847253637a6f052a62f/pyyaml-6.0.3-cp314-cp314t-macosx_10_13_x86_64.whl", hash = "sha256:02893d100e99e03eda1c8fd5c441d8c60103fd175728e23e431db1b589cf5ab3", size = 189108, upload-time = "2025-09-25T21:32:44.377Z" },
-    { url = "https://files.pythonhosted.org/packages/4e/78/8d08c9fb7ce09ad8c38ad533c1191cf27f7ae1effe5bb9400a46d9437fcf/pyyaml-6.0.3-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:c1ff362665ae507275af2853520967820d9124984e0f7466736aea23d8611fba", size = 183641, upload-time = "2025-09-25T21:32:45.407Z" },
-    { url = "https://files.pythonhosted.org/packages/7b/5b/3babb19104a46945cf816d047db2788bcaf8c94527a805610b0289a01c6b/pyyaml-6.0.3-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:6adc77889b628398debc7b65c073bcb99c4a0237b248cacaf3fe8a557563ef6c", size = 831901, upload-time = "2025-09-25T21:32:48.83Z" },
-    { url = "https://files.pythonhosted.org/packages/8b/cc/dff0684d8dc44da4d22a13f35f073d558c268780ce3c6ba1b87055bb0b87/pyyaml-6.0.3-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:a80cb027f6b349846a3bf6d73b5e95e782175e52f22108cfa17876aaeff93702", size = 861132, upload-time = "2025-09-25T21:32:50.149Z" },
-    { url = "https://files.pythonhosted.org/packages/b1/5e/f77dc6b9036943e285ba76b49e118d9ea929885becb0a29ba8a7c75e29fe/pyyaml-6.0.3-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:00c4bdeba853cc34e7dd471f16b4114f4162dc03e6b7afcc2128711f0eca823c", size = 839261, upload-time = "2025-09-25T21:32:51.808Z" },
-    { url = "https://files.pythonhosted.org/packages/ce/88/a9db1376aa2a228197c58b37302f284b5617f56a5d959fd1763fb1675ce6/pyyaml-6.0.3-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:66e1674c3ef6f541c35191caae2d429b967b99e02040f5ba928632d9a7f0f065", size = 805272, upload-time = "2025-09-25T21:32:52.941Z" },
-    { url = "https://files.pythonhosted.org/packages/da/92/1446574745d74df0c92e6aa4a7b0b3130706a4142b2d1a5869f2eaa423c6/pyyaml-6.0.3-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:16249ee61e95f858e83976573de0f5b2893b3677ba71c9dd36b9cf8be9ac6d65", size = 829923, upload-time = "2025-09-25T21:32:54.537Z" },
-    { url = "https://files.pythonhosted.org/packages/f0/7a/1c7270340330e575b92f397352af856a8c06f230aa3e76f86b39d01b416a/pyyaml-6.0.3-cp314-cp314t-win_amd64.whl", hash = "sha256:4ad1906908f2f5ae4e5a8ddfce73c320c2a1429ec52eafd27138b7f1cbe341c9", size = 174062, upload-time = "2025-09-25T21:32:55.767Z" },
-    { url = "https://files.pythonhosted.org/packages/f1/12/de94a39c2ef588c7e6455cfbe7343d3b2dc9d6b6b2f40c4c6565744c873d/pyyaml-6.0.3-cp314-cp314t-win_arm64.whl", hash = "sha256:ebc55a14a21cb14062aa4162f906cd962b28e2e9ea38f9b4391244cd8de4ae0b", size = 149341, upload-time = "2025-09-25T21:32:56.828Z" },
-]
-
-[[package]]
-name = "referencing"
-version = "0.37.0"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "attrs" },
-    { name = "rpds-py" },
-    { name = "typing-extensions", marker = "python_full_version < '3.13'" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/22/f5/df4e9027acead3ecc63e50fe1e36aca1523e1719559c499951bb4b53188f/referencing-0.37.0.tar.gz", hash = "sha256:44aefc3142c5b842538163acb373e24cce6632bd54bdb01b21ad5863489f50d8", size = 78036, upload-time = "2025-10-13T15:30:48.871Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/2c/58/ca301544e1fa93ed4f80d724bf5b194f6e4b945841c5bfd555878eea9fcb/referencing-0.37.0-py3-none-any.whl", hash = "sha256:381329a9f99628c9069361716891d34ad94af76e461dcb0335825aecc7692231", size = 26766, upload-time = "2025-10-13T15:30:47.625Z" },
-]
-
-[[package]]
-name = "regex"
-version = "2026.7.19"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/20/98/04b13f1ddfb63158025291c02e03eb42fbb7acb51d091d541050eb4e35e8/regex-2026.7.19.tar.gz", hash = "sha256:7e77b324909c1617cbb4c668677e2c6ae13f44d7c1de0d4f15f2e3c10f3315b5", size = 416440, upload-time = "2026-07-19T00:19:48.923Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/3b/b9/d11d7e501ac8fd7d617684423ebb9561e0b998481c1e4cbc0cb212c5d74a/regex-2026.7.19-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:2cc3460cedf7579948486eab03bc9ad7089df4d7281c0f47f4afe03e8d13f02d", size = 496778, upload-time = "2026-07-19T00:17:05.677Z" },
-    { url = "https://files.pythonhosted.org/packages/3f/a9/a5ab6f312f24318019170dc485d5421fe4f89e43a98640da50d95a8a7041/regex-2026.7.19-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:0e9554c8785eac5cffe6300f69a91f58ba72bc88a5f8d661235ad7c6aa5b8ccd", size = 297122, upload-time = "2026-07-19T00:17:07.59Z" },
-    { url = "https://files.pythonhosted.org/packages/b3/63/4cab4d7f2d384a144d420b763d97674cb70619c878ea6fcd7640d0e62143/regex-2026.7.19-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:d7da47a0f248977f08e2cb659ff3c17ddc13a4d39b3a7baa0a81bf5b415430f6", size = 292009, upload-time = "2026-07-19T00:17:09.648Z" },
-    { url = "https://files.pythonhosted.org/packages/22/85/102a81b218298957d4ea7d2f084fae537a71add9d6ff93c8e67284c5f45e/regex-2026.7.19-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:93db40c8de0815baab96a06e08a984bac71f989d13bab789e382158c5d426797", size = 796708, upload-time = "2026-07-19T00:17:11.542Z" },
-    { url = "https://files.pythonhosted.org/packages/78/b5/dc136af5629938a037cd2b304c12240e132ec92f38be8ff9cc89af2a1f2d/regex-2026.7.19-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:66bd62c59a5427746e8c44becae1d9b99d22fb13f30f492083dfb9ad7c45cc18", size = 865651, upload-time = "2026-07-19T00:17:13.312Z" },
-    { url = "https://files.pythonhosted.org/packages/e0/75/67402ae3cd9c8c988a4c805d15ee3eef015e7ca4cb112cf3e640fc1f4153/regex-2026.7.19-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:1649eb39fcc9ea80c4d2f110fde2b8ab2aef3877b98f02ab9b14e961f418c511", size = 911756, upload-time = "2026-07-19T00:17:15.015Z" },
-    { url = "https://files.pythonhosted.org/packages/2a/8e/096d00c7c480ef2ff4265349b14e2261d4ab787ba1f74e2e80d1c58079c3/regex-2026.7.19-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:9dce8ec9695f531a1b8a6f314fd4b393adcccf2ea861db480cdf97a301d01a68", size = 801798, upload-time = "2026-07-19T00:17:17.208Z" },
-    { url = "https://files.pythonhosted.org/packages/f0/41/e7ecac6edb5722417f85cc67eaf386322fbe8acf6918ec2fdc37c20dd9d0/regex-2026.7.19-cp312-cp312-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:3080a7fd38ef049bd489e01c970c97dd84ff446a885b0f1f6b26d9b1ad13ce11", size = 776933, upload-time = "2026-07-19T00:17:19.347Z" },
-    { url = "https://files.pythonhosted.org/packages/6f/69/03c9b3f058d66403e0ca2c938696e81d51cd4c6d47ec5265f02f96948d9a/regex-2026.7.19-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:1d793a7988e04fcb1e2e135567443d82173225d657419ec09414a9b5a145b986", size = 784338, upload-time = "2026-07-19T00:17:21.057Z" },
-    { url = "https://files.pythonhosted.org/packages/f6/f7/b38ab3d43f284afbb618fcd15d0e77eb786ae461ce1f6bc7494619ddc0f2/regex-2026.7.19-cp312-cp312-musllinux_1_2_ppc64le.whl", hash = "sha256:e8b0abe7d870f53ca5143895fef7d1041a0c831a140d3dc2c760dd7ba25d4a8b", size = 860452, upload-time = "2026-07-19T00:17:23.119Z" },
-    { url = "https://files.pythonhosted.org/packages/15/5c/ff60ef0571121714f3cf9920bc183071e384a10b556d042e0fdb06cc07a5/regex-2026.7.19-cp312-cp312-musllinux_1_2_riscv64.whl", hash = "sha256:4e5413bd5f13d3a4e3539ca98f70f75e7fca92518dd7f117f030ebedd10b60cb", size = 765958, upload-time = "2026-07-19T00:17:24.81Z" },
-    { url = "https://files.pythonhosted.org/packages/aa/0f/bd34021162c0ab47f9a315bd56cd5642e920c8e5668a75ef6c6a6fca590d/regex-2026.7.19-cp312-cp312-musllinux_1_2_s390x.whl", hash = "sha256:73b133a9e6fb512858e7f065e96f1180aa46646bc74a83aea62f1d314f3dd035", size = 851765, upload-time = "2026-07-19T00:17:26.993Z" },
-    { url = "https://files.pythonhosted.org/packages/2a/20/a2ca43edade0595cccfdc98636739f536d9e26898e7dbddc2b9e98898953/regex-2026.7.19-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:dbe6493fbd27321b1d1f2dd4f5c7e5bd4d8b1d7cab7f32fd67db3d0b2ed8248a", size = 789714, upload-time = "2026-07-19T00:17:28.699Z" },
-    { url = "https://files.pythonhosted.org/packages/5d/47/e02db4015d424fc83c00ea0ac8c5e5ec14397943de9abf909d5ce3a25931/regex-2026.7.19-cp312-cp312-win32.whl", hash = "sha256:ddd67571c10869f65a5d7dde536d1e066e306cc90de57d7de4d5f34802428bb5", size = 267157, upload-time = "2026-07-19T00:17:31.051Z" },
-    { url = "https://files.pythonhosted.org/packages/08/8e/c780c131f79b42ed22d1bd7da4096c2c35f813e835acd02ef0f018bd892c/regex-2026.7.19-cp312-cp312-win_amd64.whl", hash = "sha256:e30d40268a28d54ce0437031750497004c22602b8e3ab891f759b795a003b312", size = 277777, upload-time = "2026-07-19T00:17:32.848Z" },
-    { url = "https://files.pythonhosted.org/packages/3e/4c/e4d7e086449bdf379d89774bf1f89dc4a41943f3c5a6125a03905b34b5fb/regex-2026.7.19-cp312-cp312-win_arm64.whl", hash = "sha256:de9208bb427130c82a5dbfd104f92c8876fc9559278c880b3002755bbbe9c83d", size = 277136, upload-time = "2026-07-19T00:17:34.803Z" },
-    { url = "https://files.pythonhosted.org/packages/5d/3d/84165e4299ff76f3a40fe1f2abf939e976f693383a08d2beea6af62bd2c1/regex-2026.7.19-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:f035d9dc1d25eff9d361456572231c7d27b5ccd473ca7dc0adfce732bd006d40", size = 496552, upload-time = "2026-07-19T00:17:36.808Z" },
-    { url = "https://files.pythonhosted.org/packages/02/a2/a65293e6e4cf28eb7ee1be5335a5386c40d6742e9f47fafc8fec785e16c7/regex-2026.7.19-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:c42572142ed0b9d5d261ba727157c426510da78e20828b66bbb855098b8a4e38", size = 296983, upload-time = "2026-07-19T00:17:38.816Z" },
-    { url = "https://files.pythonhosted.org/packages/95/47/2d0564e93d87bc48618360ddca232a2ca612bbdf53ce8465d45ca5ce14ee/regex-2026.7.19-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:40b34dd88658e4fedd2fddbf0275ac970d00614b731357f425722a3ed1983d11", size = 291832, upload-time = "2026-07-19T00:17:40.726Z" },
-    { url = "https://files.pythonhosted.org/packages/07/cd/42dfbabff3dfc9603c501c0e2e2c5adbb09d127b267bf5348de0af338c15/regex-2026.7.19-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:0c41c63992bf1874cebb6e7f56fd7d3c007924659a604ae3d90e427d40d4fd13", size = 796775, upload-time = "2026-07-19T00:17:42.382Z" },
-    { url = "https://files.pythonhosted.org/packages/df/5d/f6a4839f2b934e3eed5973fd07f5929ee97d4c98939fb275ea23c274ee16/regex-2026.7.19-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:1d3372064506b94dd2c67c845f2db8062e9e9ba84d04e33cb96d7d33c11fe1ae", size = 865687, upload-time = "2026-07-19T00:17:44.185Z" },
-    { url = "https://files.pythonhosted.org/packages/14/b0/b47d6c36049bc59806a50bd4c86ced70bbe058d787f80281b1d7a9b0e024/regex-2026.7.19-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:fce7760bf283405b2c7999cab3da4e72f7deca6396013115e3f7a955db9760da", size = 911962, upload-time = "2026-07-19T00:17:46.442Z" },
-    { url = "https://files.pythonhosted.org/packages/2a/be/ff61f28f9273658cfe23acbbac5217221f6519960ed401e61dfdab12bc35/regex-2026.7.19-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:c0d702548d89d572b2929879bc883bb7a4c4709efafe4512cadee56c55c9bd15", size = 801817, upload-time = "2026-07-19T00:17:48.25Z" },
-    { url = "https://files.pythonhosted.org/packages/c3/bb/8b4f7f26b333f9f79e1b453613c39bb4776f51d38ae66dd0ba31d6b354ca/regex-2026.7.19-cp313-cp313-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:d446c6ac40bb6e05025ccee55b84d80fe9bf8e93010ffc4bb9484f13d498835f", size = 776908, upload-time = "2026-07-19T00:17:50.183Z" },
-    { url = "https://files.pythonhosted.org/packages/09/13/610110fc5921d380516d03c26b652555f08aa0d23ea78a771231873c3638/regex-2026.7.19-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:4c3501bfa814ab07b5580741f9bf78dfdfe146a04057f82df9e2402d2a975939", size = 784426, upload-time = "2026-07-19T00:17:52.454Z" },
-    { url = "https://files.pythonhosted.org/packages/ca/f5/1ef9e2a83a5947c57ebff0b377cb5727c3d5ec1992317a320d035cd0dbb6/regex-2026.7.19-cp313-cp313-musllinux_1_2_ppc64le.whl", hash = "sha256:c4585c3e64b4f9e583b4d2683f18f5d5d872b3d71dcf24594b74ecc23602fa96", size = 860600, upload-time = "2026-07-19T00:17:54.229Z" },
-    { url = "https://files.pythonhosted.org/packages/a0/02/073af33a3ec149241d11c80acea91e722aa0adbf05addd50f251c4fe89c3/regex-2026.7.19-cp313-cp313-musllinux_1_2_riscv64.whl", hash = "sha256:571fde9741eb0ccde23dd4e0c1d50fbae910e901fa7e629faf39b2dda740d220", size = 765950, upload-time = "2026-07-19T00:17:56.041Z" },
-    { url = "https://files.pythonhosted.org/packages/81/a9/d1e9f819dc394a568ef370cd56cf25394e957a2235f8370f23b576e5a475/regex-2026.7.19-cp313-cp313-musllinux_1_2_s390x.whl", hash = "sha256:15b364b9b98d6d2fe1a85034c23a3180ff913f46caddc3895f6fd65186255ccc", size = 851794, upload-time = "2026-07-19T00:17:57.897Z" },
-    { url = "https://files.pythonhosted.org/packages/03/3a/8ae83eda7579feacdf984e71fb9e70635fb6f832eeddca58427ec4fca926/regex-2026.7.19-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:ffd8893ccc1c2fce6e0d6ca402d716fe1b29db70c7132609a05955e31b2aa8f2", size = 789845, upload-time = "2026-07-19T00:17:59.97Z" },
-    { url = "https://files.pythonhosted.org/packages/4b/23/c195cbfe5a75fdec64d8f6554fd15237b837919d2c61bdc141d7c807b08b/regex-2026.7.19-cp313-cp313-win32.whl", hash = "sha256:f0fa4fa9c3632d708742baf2282f2055c11d888a790362670a403cbf48a2c404", size = 267135, upload-time = "2026-07-19T00:18:01.958Z" },
-    { url = "https://files.pythonhosted.org/packages/b2/80/a11de8404b7272b70acb45c1c05987cce60b45d5693da2e176f0e390d564/regex-2026.7.19-cp313-cp313-win_amd64.whl", hash = "sha256:d51ffd3427640fa2da6ade574ceba932f210ad095f65fcc450a2b0a0d454868e", size = 277747, upload-time = "2026-07-19T00:18:04.121Z" },
-    { url = "https://files.pythonhosted.org/packages/d1/29/0f5c8eff1b4f1f3d83276d365fccecf666afcc7d947420943bf394d07adb/regex-2026.7.19-cp313-cp313-win_arm64.whl", hash = "sha256:c670fe7be5b6020b76bc6e8d2196074657e1327595bca93a389e1a76ab130ad8", size = 277129, upload-time = "2026-07-19T00:18:05.821Z" },
-    { url = "https://files.pythonhosted.org/packages/dc/4c/44b74742052cedda40f9ae469532a037112f7311a36669a891fba8984bb0/regex-2026.7.19-cp313-cp313t-macosx_10_13_universal2.whl", hash = "sha256:db47b561c9afd884baa1f96f797c9ca369872c4b65912bc691cfa99e68340af2", size = 501134, upload-time = "2026-07-19T00:18:07.567Z" },
-    { url = "https://files.pythonhosted.org/packages/f0/45/bbd038b5e39ee5613a5a689290145b40058cc152c41de9cc23639d2b9734/regex-2026.7.19-cp313-cp313t-macosx_10_13_x86_64.whl", hash = "sha256:65dcd28d3eba2ab7c2fd906485cc301392b47cc2234790d27d4e4814e02cdfda", size = 299418, upload-time = "2026-07-19T00:18:09.38Z" },
-    { url = "https://files.pythonhosted.org/packages/65/38/c5bde94b4cedfd5850d64c3f08222d8e1600e84f6ee71d9b44b4b8163f74/regex-2026.7.19-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:f2e7f8e2ab6c2922be02c7ec45185aa5bd771e2e57b95455ee343a44d8130dff", size = 294486, upload-time = "2026-07-19T00:18:11.188Z" },
-    { url = "https://files.pythonhosted.org/packages/d7/6a/2f5e107cb26c960b781967178899daf2787a7ab151844ed3c01d6fc95474/regex-2026.7.19-cp313-cp313t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:fe31f28c94402043161876a258a9c6f757cb485905c7614ce8d6cd40e6b7bdc1", size = 811643, upload-time = "2026-07-19T00:18:12.975Z" },
-    { url = "https://files.pythonhosted.org/packages/37/d4/a2f963406d7d73a62eed84ba05a258afb6cad1b21aa4517443ce40506b78/regex-2026.7.19-cp313-cp313t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:f8f6fa298bb4f7f58a33334406218ba74716e68feddf5e4e54cd5d8082705abf", size = 871081, upload-time = "2026-07-19T00:18:14.733Z" },
-    { url = "https://files.pythonhosted.org/packages/45/a3/44be546340bedb15f13063f5e7fe16793ea4d9ea2e805d09bd174ac27724/regex-2026.7.19-cp313-cp313t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:cc1b2440423a851fad781309dd87843868f4f66a6bcd1ddb9225cf4ec2c84732", size = 917372, upload-time = "2026-07-19T00:18:16.724Z" },
-    { url = "https://files.pythonhosted.org/packages/f8/f6/e0870b0fd2a40dba0074e4b76e514b21313d37946c9248453e34ec43923e/regex-2026.7.19-cp313-cp313t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:8ac59a0900474a52b7c04af8196affc22bd9842acb0950df12f7b813e983609a", size = 816089, upload-time = "2026-07-19T00:18:18.617Z" },
-    { url = "https://files.pythonhosted.org/packages/ae/27/957e8e22690ad6634572b39b71f130a6105f4d0718bb16849eac00fff147/regex-2026.7.19-cp313-cp313t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:4896db1f4ce0576765b8272aa922df324e0f5b9bb2c3d03044ff32a7234a9aba", size = 785206, upload-time = "2026-07-19T00:18:20.464Z" },
-    { url = "https://files.pythonhosted.org/packages/76/a4/186e410941e731037c01166069ab86da9f65e8f8110c18009ccf4bd623ee/regex-2026.7.19-cp313-cp313t-musllinux_1_2_aarch64.whl", hash = "sha256:4e6883a021db30511d9fb8cfb0f222ce1f2c369f7d4d8b0448f449a93ba0bdfc", size = 800431, upload-time = "2026-07-19T00:18:22.716Z" },
-    { url = "https://files.pythonhosted.org/packages/73/9f/e4e10e023d291d64a33e246610b724493bf1ce98e0e59c9b7c837e5acfb7/regex-2026.7.19-cp313-cp313t-musllinux_1_2_ppc64le.whl", hash = "sha256:09523a592938aa9f587fb74467c63ff0cf88fc3df14c82ab0f0517dcf76aaa62", size = 864906, upload-time = "2026-07-19T00:18:24.772Z" },
-    { url = "https://files.pythonhosted.org/packages/24/57/ccb20b6be5f1f52a053d1ba2a8f7a077edb9d918248b8490d7506c6832b3/regex-2026.7.19-cp313-cp313t-musllinux_1_2_riscv64.whl", hash = "sha256:1ebac3474b8589fce2f9b225b650afd61448f7c73a5d0255a10cc6366471aed1", size = 773559, upload-time = "2026-07-19T00:18:27.008Z" },
-    { url = "https://files.pythonhosted.org/packages/a3/82/f3b263cf8fad927dc102891da8502e718b7ff9d19af7a2a07c03865d7188/regex-2026.7.19-cp313-cp313t-musllinux_1_2_s390x.whl", hash = "sha256:4a0530bb1b8c1c985e7e2122e2b4d3aedd8a3c21c6bfddae6767c4405668b56e", size = 857739, upload-time = "2026-07-19T00:18:29.107Z" },
-    { url = "https://files.pythonhosted.org/packages/47/2e/1687bd1b6c2aed5e672ccf845fc11557821fe7366d921b50889ea5ce57bf/regex-2026.7.19-cp313-cp313t-musllinux_1_2_x86_64.whl", hash = "sha256:2ef7eeb108c47ce7bcc9513e51bcb1bf57e8f483d52fce68a8642e3527141ae0", size = 804522, upload-time = "2026-07-19T00:18:31.362Z" },
-    { url = "https://files.pythonhosted.org/packages/76/7c/cc4e7655181b2d9235b704f2c5e19d8eff002bbc437bae59baee0e381aca/regex-2026.7.19-cp313-cp313t-win32.whl", hash = "sha256:64b6ca7391a1395c2638dd5c7456d67bea44fc6c5e8e92c5dc8aa6a8f23292b4", size = 269141, upload-time = "2026-07-19T00:18:33.479Z" },
-    { url = "https://files.pythonhosted.org/packages/bb/14/961b4c7b05a2391c32dbc85e27773076671ef8f97f36cec70fe414734c02/regex-2026.7.19-cp313-cp313t-win_amd64.whl", hash = "sha256:f04b9f56b0e0614c0126be12c2c2d9f8850c1e57af302bd0a63bed379d4af974", size = 280036, upload-time = "2026-07-19T00:18:35.419Z" },
-    { url = "https://files.pythonhosted.org/packages/ce/67/795644550d788ddbb6dc458c95895f8009978ea6d6ea76b005eb3f45e8c9/regex-2026.7.19-cp313-cp313t-win_arm64.whl", hash = "sha256:fcee38cd8e5089d6d4f048ba1233b3ad76e5954f545382180889112ff5cb712d", size = 279394, upload-time = "2026-07-19T00:18:37.454Z" },
-    { url = "https://files.pythonhosted.org/packages/d2/25/0c4c452f8ef3efe456745b2f33195f5904b573fb4c2ff3f0cb9ec188461e/regex-2026.7.19-cp314-cp314-macosx_10_13_universal2.whl", hash = "sha256:a81758ed242b861b72e778ba34d41366441a2e10b16b472784c88da2dea7e2dd", size = 496750, upload-time = "2026-07-19T00:18:39.633Z" },
-    { url = "https://files.pythonhosted.org/packages/24/9e/b70ca6c1704f6c7cd32a9e143c86cc5968d10981eca284bad670c245ea7d/regex-2026.7.19-cp314-cp314-macosx_10_13_x86_64.whl", hash = "sha256:4aa5435cdb3eb6f55fe98a171b05e3fbcd95fadaa4aa32acf62afd9b0cfdbcac", size = 297093, upload-time = "2026-07-19T00:18:41.583Z" },
-    { url = "https://files.pythonhosted.org/packages/87/74/0b692da2520d51fbff19c88b83d97e4c702909dd02386c585998b7e2dbed/regex-2026.7.19-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:60be8693a1dadc210bbcbc0db3e26da5f7d01d1d5a3da594e99b4fa42df404f5", size = 292043, upload-time = "2026-07-19T00:18:43.347Z" },
-    { url = "https://files.pythonhosted.org/packages/e3/a7/1d478e614016045a33feae57446215f9fd65b665a5ceb2f891fb3183bc52/regex-2026.7.19-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:d19662dbedbe783d323196312d38f5ba53cf56296378252171985da6899887d3", size = 797214, upload-time = "2026-07-19T00:18:45.362Z" },
-    { url = "https://files.pythonhosted.org/packages/aa/ae/11b9c9411d92c30e3d2db32df5a31133e4a99a8fc397a604fd08f6c4bffb/regex-2026.7.19-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:d15df07081d91b76ff20d43f94592ee110330152d617b730fdbe5ef9fb680053", size = 866433, upload-time = "2026-07-19T00:18:47.315Z" },
-    { url = "https://files.pythonhosted.org/packages/b1/62/2b2efc4992f91d6d204b24c647c9f9412e85379d92b7c0ab9fdae622327e/regex-2026.7.19-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:56ad4d9f77df871a99e25c37091052a02528ec0eb059de928ee33956b854b45b", size = 911360, upload-time = "2026-07-19T00:18:49.588Z" },
-    { url = "https://files.pythonhosted.org/packages/14/71/986ceea9aa3da548bf1357cad89b63915ec6d21ec957c8113b29ece567df/regex-2026.7.19-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:7322ec6cc9fba9d49ab888bb82d67ac5625627aa168f0165139b17018df3fb8a", size = 801275, upload-time = "2026-07-19T00:18:51.767Z" },
-    { url = "https://files.pythonhosted.org/packages/15/be/ce9d9534b2cda96eab32c548261224b9b4e220a4126f098f60f42ae7b4cd/regex-2026.7.19-cp314-cp314-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:9c7472192ebfad53a6be7c4a8bfb2d64b81c0e93a1fc8c57e1dd0b638297b5d1", size = 777131, upload-time = "2026-07-19T00:18:54.053Z" },
-    { url = "https://files.pythonhosted.org/packages/61/2b/58b5c710f2c3929515a25f3a1ca0dad0dcd4518d4fff3cf23bc7adb8dcd2/regex-2026.7.19-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:c10b82c2634df08dfb13b1f04e38fe310d086ee092f4f69c0c8da234251e556e", size = 785020, upload-time = "2026-07-19T00:18:56.579Z" },
-    { url = "https://files.pythonhosted.org/packages/84/03/5fe091935b74f15fe0f97998c215cae418d1c0413f6258c7d4d2e83aa37f/regex-2026.7.19-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:17ed5692f6acc4183e98331101a5f9e4f64d72fe58b753da4d444a2c77d05b12", size = 861263, upload-time = "2026-07-19T00:18:58.64Z" },
-    { url = "https://files.pythonhosted.org/packages/d8/fa/d60bf82e10841eef62a9e32aac401468f05fddfbcb2942e342b1ba3d2433/regex-2026.7.19-cp314-cp314-musllinux_1_2_riscv64.whl", hash = "sha256:22a992de9a0d91bda927bf02b94351d737a0302905432c88a53de7c4b9ce62e2", size = 766199, upload-time = "2026-07-19T00:19:00.705Z" },
-    { url = "https://files.pythonhosted.org/packages/bf/5d/11e64d151b0662b81d6bf644c74dc118d461df85bdf2577fadbbf751788a/regex-2026.7.19-cp314-cp314-musllinux_1_2_s390x.whl", hash = "sha256:618a0aed532be87294c4477b0481f3aa0f1520f4014a4374dd4cf789b4cd2c97", size = 851317, upload-time = "2026-07-19T00:19:03.015Z" },
-    { url = "https://files.pythonhosted.org/packages/7c/34/532efb87488d90807bae6a443d357ee5e2728a478c597619c8aaa17cc0bd/regex-2026.7.19-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:2ce9e679f776649746729b6c86382da519ef649c8e34cc41df0d2e5e0f6c36d4", size = 789557, upload-time = "2026-07-19T00:19:05.338Z" },
-    { url = "https://files.pythonhosted.org/packages/d6/90/3a8d5ca977171ec3ae21a71207d2228b2663bde14d7f7ef0e6363ecf9290/regex-2026.7.19-cp314-cp314-win32.whl", hash = "sha256:73f272fba87b8ccfe70a137d02a54af386f6d27aa509fbffdd978f5947aae1aa", size = 272531, upload-time = "2026-07-19T00:19:07.487Z" },
-    { url = "https://files.pythonhosted.org/packages/96/e1/8862885e70409de70e8c005f57fb2e7be8d9ef0317250d60f4c9660a300d/regex-2026.7.19-cp314-cp314-win_amd64.whl", hash = "sha256:d721e53758b2cca74990185eb0671dd466d7a388a1a45d0c6f4c13cef41a68ac", size = 280831, upload-time = "2026-07-19T00:19:09.46Z" },
-    { url = "https://files.pythonhosted.org/packages/08/82/2693e53e29f9104d9de95d37ce4dd826bd32d5f9c0085d3aa6ac042675c4/regex-2026.7.19-cp314-cp314-win_arm64.whl", hash = "sha256:65fa6cb38ed5e9c3637e68e544f598b39c3b86b808ed0627a67b68320384b459", size = 281099, upload-time = "2026-07-19T00:19:11.398Z" },
-    { url = "https://files.pythonhosted.org/packages/92/b7/9a01aa16461a18cde9d7b9c3ab21e501db2ce33725f53014342b91df2b0a/regex-2026.7.19-cp314-cp314t-macosx_10_13_universal2.whl", hash = "sha256:5a2721c8720e2cb3c209925dfb9200199b4b07361c9e01d321719404b21458b3", size = 501121, upload-time = "2026-07-19T00:19:13.425Z" },
-    { url = "https://files.pythonhosted.org/packages/f3/5e/bbaeca815dc9191c424c94a4fdc5c87c75748a64a6271821212ebdd4e1a3/regex-2026.7.19-cp314-cp314t-macosx_10_13_x86_64.whl", hash = "sha256:199535629f25caf89698039af3d1ad5fcae7f933e2112c73f1cdf49165c99518", size = 299415, upload-time = "2026-07-19T00:19:15.43Z" },
-    { url = "https://files.pythonhosted.org/packages/cd/d6/0dd1a321afaab95eb7ff44aa0f637301786f1dc71c6b797b9ed236ed8890/regex-2026.7.19-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:9b60d7814174f059e5de4ab98271cc5ba9259cfea55273a81544dceea32dc8d9", size = 294483, upload-time = "2026-07-19T00:19:17.879Z" },
-    { url = "https://files.pythonhosted.org/packages/92/5f/40bacf91d0904f812e13bbbab3864604c463eced8afdc54aeaa50492ea95/regex-2026.7.19-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:dbece16025afda5e3031af0c4059207e61dcf73ef13af844964f57f387d1c435", size = 811833, upload-time = "2026-07-19T00:19:20.102Z" },
-    { url = "https://files.pythonhosted.org/packages/94/7c/4902744261f775aeede8b5627314b38482da29cf49a57b66a6fb753246c5/regex-2026.7.19-cp314-cp314t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:d24ecb4f5e009ea0bd275ee37ad9953b32005e2e5e60f8bbae16da0dbbf0d3a0", size = 871270, upload-time = "2026-07-19T00:19:22.365Z" },
-    { url = "https://files.pythonhosted.org/packages/16/70/6980c9be6bf21c0a60ed3e0aea39cf419ecf3b08d1d9947bc56e196ef186/regex-2026.7.19-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:8cae6fd77a5b72dae505084b1a2ee0360139faf72fedbab667cd7cc65aae7a6a", size = 917534, upload-time = "2026-07-19T00:19:24.529Z" },
-    { url = "https://files.pythonhosted.org/packages/52/92/8b2bd872782ce8c42691e39acb38eb8efe014e5ddb78ad7d943d6f197ce9/regex-2026.7.19-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:9724e6cb5e478cd7d8cabf027826178739cb18cf0e117d0e32814d479fa02276", size = 816135, upload-time = "2026-07-19T00:19:26.919Z" },
-    { url = "https://files.pythonhosted.org/packages/de/2d/33a602f657bdc4041f17d79f92ab18261d255d91a06117a6e29df023e5e2/regex-2026.7.19-cp314-cp314t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:572fc57b0009c735ee56c175ea021b637a15551a312f56734277f923d6fd0f6c", size = 785492, upload-time = "2026-07-19T00:19:29.192Z" },
-    { url = "https://files.pythonhosted.org/packages/9e/36/0987cf4cb271680064a70d24a475873775a151d0b7058698a006cb0cae4a/regex-2026.7.19-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:20568e182eb82d39a6bf7cff3fd58566f14c75c6f74b2c8c96537eecf9010e3a", size = 800658, upload-time = "2026-07-19T00:19:31.392Z" },
-    { url = "https://files.pythonhosted.org/packages/a8/24/c14f31c135e1ba55fa4f9a58ca98d0842512bf6188230763c31c8f449e3b/regex-2026.7.19-cp314-cp314t-musllinux_1_2_ppc64le.whl", hash = "sha256:1d58561843f0ff7dc78b4c28b5e2dc388f3eff94ebc8a232a3adba961fc00009", size = 865073, upload-time = "2026-07-19T00:19:33.485Z" },
-    { url = "https://files.pythonhosted.org/packages/14/85/181a12211f22469f24d2de1ebddfe397d2396e2c29013b9a58134a91069a/regex-2026.7.19-cp314-cp314t-musllinux_1_2_riscv64.whl", hash = "sha256:61bb1bd45520aacd56dd80943bd34991fb5350afdd1f36f2282230fd5154a218", size = 773684, upload-time = "2026-07-19T00:19:35.599Z" },
-    { url = "https://files.pythonhosted.org/packages/23/58/bd1a0c1a62251366f8d21f41b1ea3c76994962071b8b6ea42f72d505c0f0/regex-2026.7.19-cp314-cp314t-musllinux_1_2_s390x.whl", hash = "sha256:cd3584591ea4429026cdb931b054342c2bcf189b44ff367f8d5c15bc092a2966", size = 857769, upload-time = "2026-07-19T00:19:37.738Z" },
-    { url = "https://files.pythonhosted.org/packages/e4/4f/f7e2dad6756b2fe1fe75dd90a628c3b45f249d39f948dd90cd2476325417/regex-2026.7.19-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:5cc26a66e212fa5d6c6170c3a40d99d888db3020c6fdab1523250d4341382e44", size = 804546, upload-time = "2026-07-19T00:19:40.229Z" },
-    { url = "https://files.pythonhosted.org/packages/2b/d7/01d31d5bdb09bc026fab77f59a371fdf8f9b292e4810546c56182ca70498/regex-2026.7.19-cp314-cp314t-win32.whl", hash = "sha256:2c4e61e2e1be56f63ec3cc618aa9e0de81ef6f43d177205451840022e24f5b78", size = 274526, upload-time = "2026-07-19T00:19:42.398Z" },
-    { url = "https://files.pythonhosted.org/packages/52/0e/cea4ce73bc0a8247a0748228ae6669984c7e1f8134b6fa66e59c0572e0ea/regex-2026.7.19-cp314-cp314t-win_amd64.whl", hash = "sha256:c639ea314df70a7b2811e8020448c75af8c9445f5a60f8a4ced81c306a9380c2", size = 283763, upload-time = "2026-07-19T00:19:44.644Z" },
-    { url = "https://files.pythonhosted.org/packages/6f/b6/26e41975febae63b7a6e3e02f32cff6cff2e4f10d19c929082f56aebf7c6/regex-2026.7.19-cp314-cp314t-win_arm64.whl", hash = "sha256:9a15e785f244f3e07847b984ce8773fc3da10a9f3c131cc49a4c5b4d672b4547", size = 283451, upload-time = "2026-07-19T00:19:46.639Z" },
-]
-
-[[package]]
-name = "requests"
-version = "2.34.2"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "certifi" },
-    { name = "charset-normalizer" },
-    { name = "idna" },
-    { name = "urllib3" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/ac/c3/e2a2b89f2d3e2179abd6d00ebd70bff6273f37fb3e0cc209f48b39d00cbf/requests-2.34.2.tar.gz", hash = "sha256:f288924cae4e29463698d6d60bc6a4da69c89185ad1e0bcc4104f584e960b9ed", size = 142856, upload-time = "2026-05-14T19:25:27.735Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/a0/f4/c67b0b3f1b9245e8d266f0f112c500d50e5b4e83cb6f3b71b6528104182a/requests-2.34.2-py3-none-any.whl", hash = "sha256:2a0d60c172f83ac6ab31e4554906c0f3b3588d37b5cb939b1c061f4907e278e0", size = 73075, upload-time = "2026-05-14T19:25:26.443Z" },
-]
-
-[[package]]
-name = "rpds-py"
-version = "2026.6.3"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/aa/2a/9618a122aeb2a169a28b03889a2995fe297588964333d4a7d67bdf46e147/rpds_py-2026.6.3.tar.gz", hash = "sha256:1cebd1337c242e4ec2293e541f712b2da849b29f48f0c293684b71c0632625d4", size = 64051, upload-time = "2026-06-30T07:17:53.009Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/5c/be/2e8974163072e7bab7df1a5acd54c4498e75e35d6d18b864d3a9d5dadc92/rpds_py-2026.6.3-cp312-cp312-macosx_10_12_x86_64.whl", hash = "sha256:a0811d33247c3d6128a3001d763f2aa056bb3425204335400ac54f89eec3a0d0", size = 343691, upload-time = "2026-06-30T07:15:14.96Z" },
-    { url = "https://files.pythonhosted.org/packages/a4/73/319dfa745dd668efe89309141ded489126461fcecd2b8f3a3cda185129b6/rpds_py-2026.6.3-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:538949e262e46caa31ac01bdb3c1e8f642622922cacbabbae6a8445d9dc33eaf", size = 338542, upload-time = "2026-06-30T07:15:16.267Z" },
-    { url = "https://files.pythonhosted.org/packages/21/63/4239893be1c4d09b709b1a8f6be4188f0870084ff547f46606b8a75f1b03/rpds_py-2026.6.3-cp312-cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:55927d532399c2c646100ff7feb48eaa940ad70f42cd68e1328f3ded9f81ca24", size = 368180, upload-time = "2026-06-30T07:15:17.62Z" },
-    { url = "https://files.pythonhosted.org/packages/1c/ca/9c5de382225234ceb37b1844ebdb140db12b2a278bb9efe2fcd19f6c82ce/rpds_py-2026.6.3-cp312-cp312-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:f56f1695bc5c0871cbc33dc0130fcf503aab0c57dcc5a6700a4f49eba4f2652e", size = 375067, upload-time = "2026-06-30T07:15:18.952Z" },
-    { url = "https://files.pythonhosted.org/packages/87/dc/863f69d1bf04ade34b7fe0d59b9fdf6f0135fe2d7cbca74f1d665589559d/rpds_py-2026.6.3-cp312-cp312-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:270b293dae9058fc9fcedab50f13cebf46fb8ed1d1d54e0521a9da5d6b211975", size = 490509, upload-time = "2026-06-30T07:15:20.434Z" },
-    { url = "https://files.pythonhosted.org/packages/ce/ef/eac16a12048b45ec7c7fa94f2be3438a5f26bf9cc8580b18a1cfd609b7f6/rpds_py-2026.6.3-cp312-cp312-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:127565fead0a10943b282957bd5447804ff3160ad79f2ad2635e6d249e380680", size = 382754, upload-time = "2026-06-30T07:15:21.831Z" },
-    { url = "https://files.pythonhosted.org/packages/04/8f/d2f3f532616be4d06c316ef119683e832bd3d41e112bf3a88f4151c95b17/rpds_py-2026.6.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:ecabd69db66de867690f9797f2f8fa27ba501bbc24540cbdbdc649cd15888ba6", size = 366189, upload-time = "2026-06-30T07:15:23.371Z" },
-    { url = "https://files.pythonhosted.org/packages/e3/29/41a7b0e98a4b44cd676ab7598419623373eb43b20be68c084935c1a8cf88/rpds_py-2026.6.3-cp312-cp312-manylinux_2_31_riscv64.whl", hash = "sha256:58eadac9cd119677b60e1cf8ac4052f35949d71b8a9e5556efccbe82533cf22a", size = 377750, upload-time = "2026-06-30T07:15:24.659Z" },
-    { url = "https://files.pythonhosted.org/packages/2e/05/ecda0bec46f9a1565090bcdc941d023f6a25aff85fda28f89f8d19878152/rpds_py-2026.6.3-cp312-cp312-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:7491ee23305ac3eb59e492b6945881f5cd77a6f731061a3f25b77fd40f9e99a4", size = 395576, upload-time = "2026-06-30T07:15:25.987Z" },
-    { url = "https://files.pythonhosted.org/packages/68/a8/6ed52f03ee6cb854ce78785cc9a9a672eb880e83fd7224d471f667d151f1/rpds_py-2026.6.3-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:2c99f7e8ccb3dd6e3e4bfeac657a7b208c9bac8075f4b078c02d7404c34107fa", size = 543807, upload-time = "2026-06-30T07:15:27.356Z" },
-    { url = "https://files.pythonhosted.org/packages/8f/d6/156c0d3eea27ba09b92562ba2364ba124c0a061b199e17eac637cd25a5e2/rpds_py-2026.6.3-cp312-cp312-musllinux_1_2_i686.whl", hash = "sha256:62698275682bf121181861295c9181e789030a2d516071f5b8f3c23c170cd0fc", size = 611187, upload-time = "2026-06-30T07:15:28.931Z" },
-    { url = "https://files.pythonhosted.org/packages/f1/31/774212ed989c62f7f310220089f9b0a3fb8f40f5443d1727abd5d9f52bc9/rpds_py-2026.6.3-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:a214c993455f99a89aaeadc9b21241900037adc9d97203e374d75513c5911822", size = 573030, upload-time = "2026-06-30T07:15:30.553Z" },
-    { url = "https://files.pythonhosted.org/packages/c9/50/22f73127a41f1ce4f87fe39aadfb9a126345801c274aa93ae88456249327/rpds_py-2026.6.3-cp312-cp312-win32.whl", hash = "sha256:501f9f04a588d6a09179368c57071301445191767c64e4b52a6aa9871f1ef5ed", size = 202185, upload-time = "2026-06-30T07:15:32.027Z" },
-    { url = "https://files.pythonhosted.org/packages/04/3a/f0ee4d4dde9d3b69dedf1b5f74e7a40017046d55052d173e418c6a94f960/rpds_py-2026.6.3-cp312-cp312-win_amd64.whl", hash = "sha256:2c958bf94822e9290a40aaf2a822d4bc5c88099093e3948ad6c571eca9272e5f", size = 220394, upload-time = "2026-06-30T07:15:33.359Z" },
-    { url = "https://files.pythonhosted.org/packages/f3/83/3382fe37f809b59f02aac04dbc4e765b480b46ee0227ed516e3bdc4d3dfc/rpds_py-2026.6.3-cp312-cp312-win_arm64.whl", hash = "sha256:22bffe6042b9bcb0822bcd1955ec00e245daf17b4344e4ed8e9551b976b63e96", size = 215753, upload-time = "2026-06-30T07:15:34.778Z" },
-    { url = "https://files.pythonhosted.org/packages/a4/9e/b818ee580026ec578138e961027a68820c40afeb1ec8f6819b54fb99e196/rpds_py-2026.6.3-cp313-cp313-macosx_10_12_x86_64.whl", hash = "sha256:3cfe765c1da0072636ca06628261e0ea05688e160d5c8a03e0217c3854037223", size = 343012, upload-time = "2026-06-30T07:15:36.005Z" },
-    { url = "https://files.pythonhosted.org/packages/f3/6b/686d9dc4359a8f163cfbbf89ee0b4e586431de22fe8248edb63a8cf50d49/rpds_py-2026.6.3-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:f4d78253f6996be4901669ad25319f842f740eccf4d58e3c7f3dd39e6dde1d8f", size = 338203, upload-time = "2026-06-30T07:15:37.462Z" },
-    { url = "https://files.pythonhosted.org/packages/9e/9b/069aa329940f8207615e091f5eedbbd40e1e15eac68a0790fd05ccdf796c/rpds_py-2026.6.3-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:54f45a148e28767bf343d33a684693c70e451c6f4c0e9904709a723fafbdfc1f", size = 367984, upload-time = "2026-06-30T07:15:39.008Z" },
-    { url = "https://files.pythonhosted.org/packages/14/db/34c203e4becff3703e4d3bc121842c00b8689197f398161203a880052f4e/rpds_py-2026.6.3-cp313-cp313-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:842e7b070435622248c7a2c44ae53fa1440e073cc3023bc919fed570884097a7", size = 374815, upload-time = "2026-06-30T07:15:40.253Z" },
-    { url = "https://files.pythonhosted.org/packages/ee/7d/8071067d2cc453d916ad836e828c943f575e8a44612537759002a1e07381/rpds_py-2026.6.3-cp313-cp313-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:8020133a74bd81b4572dd8e4be028a6b1ebcd70e6726edc3918008c08bee6ee6", size = 490545, upload-time = "2026-06-30T07:15:41.729Z" },
-    { url = "https://files.pythonhosted.org/packages/a3/42/da06c5aa8f0484ff07f270787434204d9f4535e2f8c3b51ed402267e63c3/rpds_py-2026.6.3-cp313-cp313-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:cdc7e35386f3847df728fbcb5e887e2d79c19e2fa1eba9e51b6621d23e3243af", size = 382828, upload-time = "2026-06-30T07:15:43.327Z" },
-    { url = "https://files.pythonhosted.org/packages/57/d7/fe978efc2ae50abe48eb7464668ea99f53c010c60aeebb7b35ad27f23661/rpds_py-2026.6.3-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:acac386b453c2516111b50985d60ce46e7fadb5ea71ae7b25f4c946935bf27cf", size = 365678, upload-time = "2026-06-30T07:15:44.992Z" },
-    { url = "https://files.pythonhosted.org/packages/69/9d/1d8922e1990b2a6eb532b6ff53d3e73d2b3bbffc84116c75826bee73dfc6/rpds_py-2026.6.3-cp313-cp313-manylinux_2_31_riscv64.whl", hash = "sha256:425560c6fa0415f27261727bb20bd097568485e5eb0c121f1949417d1c516885", size = 377811, upload-time = "2026-06-30T07:15:46.523Z" },
-    { url = "https://files.pythonhosted.org/packages/b1/3d/198dceafb4fb034a6a47347e1b0735d34e0bd4a50be4e898d408ee66cb14/rpds_py-2026.6.3-cp313-cp313-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:a550fb4950a06dde3beb4721f5ad4b25bf4513784665b0a8522c792e2bd822a4", size = 395382, upload-time = "2026-06-30T07:15:47.955Z" },
-    { url = "https://files.pythonhosted.org/packages/1f/f1/13968e49655d40b6b19d8b9140296bbc6f1d86b3f0f6c346cf9f1adddf4b/rpds_py-2026.6.3-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:4f4bca01b63096f606e095734dd56e74e175f94cfbf24ff3d63281cec61f7bb7", size = 543832, upload-time = "2026-06-30T07:15:49.33Z" },
-    { url = "https://files.pythonhosted.org/packages/ac/ab/289bcb1b90bd3e40a2900c561fa0e2087345ecbb094f0b870f2345142b7c/rpds_py-2026.6.3-cp313-cp313-musllinux_1_2_i686.whl", hash = "sha256:ccffae9a092a00deb7efd545fe5e2c33c33b88e7c054337e9a74c179347d0b7d", size = 611011, upload-time = "2026-06-30T07:15:50.847Z" },
-    { url = "https://files.pythonhosted.org/packages/1e/16/5043105e679436ccfbc8e5e0dd2d663ed18a8b8113515fd06a5e5d77c83e/rpds_py-2026.6.3-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:1cf01971c4f2c5553b772a542e4aaf191789cd331bc2cd4ff0e6e65ba49e1e97", size = 572431, upload-time = "2026-06-30T07:15:52.394Z" },
-    { url = "https://files.pythonhosted.org/packages/85/ed/adab103321c0a6565d5ae1c2998349bc3ee175b82ccc5ae8fc04cc413075/rpds_py-2026.6.3-cp313-cp313-win32.whl", hash = "sha256:8c3d1e9c15b9d51ca0391e13da1a25a0a4df3c58a37c9dc368e0736cf7f69df0", size = 201710, upload-time = "2026-06-30T07:15:53.894Z" },
-    { url = "https://files.pythonhosted.org/packages/7b/ed/a03b09668e74e5dabbf2e211f6468e1820c0552f7b0500082da31841bf7b/rpds_py-2026.6.3-cp313-cp313-win_amd64.whl", hash = "sha256:9250a9a0a6fd4648b3f868da8d91a4c52b5811a62df58e753d50ae4454a36f80", size = 219454, upload-time = "2026-06-30T07:15:55.25Z" },
-    { url = "https://files.pythonhosted.org/packages/27/17/b8642c12930b71bc2b25831f6708ccf0f75abcd11883932ec9ce54ba3a78/rpds_py-2026.6.3-cp313-cp313-win_arm64.whl", hash = "sha256:900a67df3fd1660b035a4761c4ce73c382ea6b35f90f9863c36c6fd8bf8b09bb", size = 215063, upload-time = "2026-06-30T07:15:56.573Z" },
-    { url = "https://files.pythonhosted.org/packages/b6/36/7fbe9dcdaf857fb3f63c2a2284b62492d95f5e8334e947e5fb6e7f68c9be/rpds_py-2026.6.3-cp314-cp314-macosx_10_12_x86_64.whl", hash = "sha256:931908d9fc855d8f74783377822be318edb6dcb19e47169dc038f9a1bf60b06e", size = 344510, upload-time = "2026-06-30T07:15:57.921Z" },
-    { url = "https://files.pythonhosted.org/packages/ba/54/f785cc3d3f60839ca57a5af4927a9f347b07b2799c373fc20f7949f87c7e/rpds_py-2026.6.3-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:d7469697dce35be237db177d42e2a2ee26e6dcc5fc052078a6fefabd288c6edd", size = 339495, upload-time = "2026-06-30T07:15:59.238Z" },
-    { url = "https://files.pythonhosted.org/packages/63/ef/d4cdaf309e6b095b43597103cf8c0b951d6cca2acce68c474f75ec12e0c7/rpds_py-2026.6.3-cp314-cp314-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:bcfbcf66006befb9fd2aeaa9e01feaf881b4dc330a02ba07d2322b1c11be7b5d", size = 369454, upload-time = "2026-06-30T07:16:01.021Z" },
-    { url = "https://files.pythonhosted.org/packages/96/4a/9559a68b7ee15db09d7981212e8c2e219d2a1d6d4faa0391d813c3496a36/rpds_py-2026.6.3-cp314-cp314-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:847927daf4cffbd4e90e42bc890069897101edd015f956cb8721b3473372edda", size = 374583, upload-time = "2026-06-30T07:16:02.287Z" },
-    { url = "https://files.pythonhosted.org/packages/ef/75/8964aa7d2c6e8ac43eba8eb6e6b0fdda1f46d39f2fc3e6aa9f2cb17f485d/rpds_py-2026.6.3-cp314-cp314-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:aca6c1ef08a82bfe327cc156da694660f599923e2e6665b6d81c9c2d0ac9ffc8", size = 492919, upload-time = "2026-06-30T07:16:03.723Z" },
-    { url = "https://files.pythonhosted.org/packages/8f/97/6908094ac804115e65aedfd90f1b5fee4eebebd3f6c4cfc5419939267565/rpds_py-2026.6.3-cp314-cp314-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:ae50181a047c871561212bb97f7932a2d45fb53e947bd9b57ebad85b529cbc53", size = 383725, upload-time = "2026-06-30T07:16:05.305Z" },
-    { url = "https://files.pythonhosted.org/packages/d1/9c/0d1fdc2e7aba23e290d603bc494e97bd205bae262ce33c6b32a69768ed5e/rpds_py-2026.6.3-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:dc319e5a1de4b6913aac94bf6a2f9e847371e0a140a43dd4991db1a09bc2d504", size = 367255, upload-time = "2026-06-30T07:16:07.086Z" },
-    { url = "https://files.pythonhosted.org/packages/c4/fe/f0209ca4a9ed074bc8acb44dfd0e81c3122e94c9689f5645b7973a866719/rpds_py-2026.6.3-cp314-cp314-manylinux_2_31_riscv64.whl", hash = "sha256:e4316bf32babbed84e691e352faf967ce2f0f024174a8643c37c94a1080374fc", size = 379060, upload-time = "2026-06-30T07:16:08.525Z" },
-    { url = "https://files.pythonhosted.org/packages/c6/8d/f1cc54c616b9d8897de8738aac148d20afca93f68187475fe194d09a71b9/rpds_py-2026.6.3-cp314-cp314-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:8c6e5a2f750cc71c3e3b11d71661f21d6f9bc6cebc6564b1466417a1ec03ec77", size = 395960, upload-time = "2026-06-30T07:16:09.989Z" },
-    { url = "https://files.pythonhosted.org/packages/fb/04/aafff00f73aeca2945f734f1d483c64ab8f472d0864ab02377fd8e89c3b2/rpds_py-2026.6.3-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:4470ce197d4090875cf6affbf1f853338387428df97c4fb7b7106317b8214698", size = 545356, upload-time = "2026-06-30T07:16:11.816Z" },
-    { url = "https://files.pythonhosted.org/packages/fd/cc/e229663b9e4ddac5a4acbe9085dd80a71af2a5d356b8b39d6bff233f24b0/rpds_py-2026.6.3-cp314-cp314-musllinux_1_2_i686.whl", hash = "sha256:ea964164cc9afa72d4d9b23cc28dafae93693c0a53e0b42acbff15b22c3f9ddd", size = 612319, upload-time = "2026-06-30T07:16:13.586Z" },
-    { url = "https://files.pythonhosted.org/packages/e3/7a/8a0e6d3e6cd066af108b71b43122c3fe158dd9eb86acac626593a2582eb1/rpds_py-2026.6.3-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:639c8929aa0afe81be836b04de888460d6bed38b9c54cfc18da8f6bfabf5af5d", size = 573508, upload-time = "2026-06-30T07:16:15.23Z" },
-    { url = "https://files.pythonhosted.org/packages/87/03/2a69ab618a789cf6cf85c86bb844c62d090e700ab1a2aa676b3741b6c516/rpds_py-2026.6.3-cp314-cp314-win32.whl", hash = "sha256:882076c00c0a608b131187055ddc5ae29f2e7eaf870d6168980420d58528a5c8", size = 202504, upload-time = "2026-06-30T07:16:16.893Z" },
-    { url = "https://files.pythonhosted.org/packages/85/62/a3892ba945f4e24c78f352e5de3c7620d8479f73f211406a97263d13c7d2/rpds_py-2026.6.3-cp314-cp314-win_amd64.whl", hash = "sha256:0be972be84cfcaf46c8c6edf690ca0f154ac17babf1f6a955a51579b34ad2dc5", size = 220380, upload-time = "2026-06-30T07:16:18.108Z" },
-    { url = "https://files.pythonhosted.org/packages/3d/e7/c2bd44dc831931815ad11ebb5f430b5a0a4d3caa9de837107876c30c3432/rpds_py-2026.6.3-cp314-cp314-win_arm64.whl", hash = "sha256:2a9c6f195058cb45335e8cc3802745c603d716eb96bc9625950c1aac71c0c703", size = 215976, upload-time = "2026-06-30T07:16:19.654Z" },
-    { url = "https://files.pythonhosted.org/packages/79/9c/fff7b74bce9a091ec9a012a03f9ff5f69364eaf9451060dfc4486da2ffdd/rpds_py-2026.6.3-cp314-cp314t-macosx_10_12_x86_64.whl", hash = "sha256:f90938e92afda60266da758ee7d363447f7f0138c9559f9e1811629580582d90", size = 346840, upload-time = "2026-06-30T07:16:21.268Z" },
-    { url = "https://files.pythonhosted.org/packages/e9/44/77bcb1168b33704908295533d27f10eb811e9e3e193e8993dc99572211d3/rpds_py-2026.6.3-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:ec829541c45bca16e61c7ae50c20501f213605beb75d1aba91a6ee37fbbb56a4", size = 340282, upload-time = "2026-06-30T07:16:22.875Z" },
-    { url = "https://files.pythonhosted.org/packages/87/3c/7a9081c7c9e645b39efe19e4ffbeccd80add246327cd9b888aecffd72317/rpds_py-2026.6.3-cp314-cp314t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:afd70d95892096cdb26f15a00c45907b17817577aa8d1c76b2dcc2788391f9e9", size = 370403, upload-time = "2026-06-30T07:16:24.415Z" },
-    { url = "https://files.pythonhosted.org/packages/f7/69/af47021eb7dad6ff3396cb001c08f0f3c4d06c20253f75be6421a59fe6b7/rpds_py-2026.6.3-cp314-cp314t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:29dfa0533a5d4c94d4dfa1b694fcb56c9c63aad8330ffdd816fd225d0a7a162f", size = 376055, upload-time = "2026-06-30T07:16:26.111Z" },
-    { url = "https://files.pythonhosted.org/packages/81/fc/a3bcf517084396a6dd258c592567a3c011ba4557f2fde23dceaf26e74f2e/rpds_py-2026.6.3-cp314-cp314t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:af05d726809bff6b141be124d4c7ce998f9c9c7f30edb1f46c07aa103d540b41", size = 494419, upload-time = "2026-06-30T07:16:27.596Z" },
-    { url = "https://files.pythonhosted.org/packages/c9/eb/13d529d1788135425c7bf207f8463458ca5d92e43f3f701365b83e9dffc1/rpds_py-2026.6.3-cp314-cp314t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:9826217f048f620d9a712672818bf231442c1b35d96b227a07eabd11b4bb6945", size = 384848, upload-time = "2026-06-30T07:16:29.183Z" },
-    { url = "https://files.pythonhosted.org/packages/8e/f4/b7ac49f30013aba8f7b9566b1dd07e81de95e708c1374b7bacc5b9bc5c9c/rpds_py-2026.6.3-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:536bceea4fa4acf7e1c61da2b5786304367c816c8895be71b8f537c480b0ea1f", size = 371369, upload-time = "2026-06-30T07:16:30.912Z" },
-    { url = "https://files.pythonhosted.org/packages/31/86/6260bafa622f788b07ddec0e52d810305c8b9b0b8c27f58a2ab04bf62b4f/rpds_py-2026.6.3-cp314-cp314t-manylinux_2_31_riscv64.whl", hash = "sha256:bc0011654b91cc4fb2ae701bec0a0ba1e552c0714247fa7af6c59e0ccfa3a4e1", size = 379673, upload-time = "2026-06-30T07:16:32.486Z" },
-    { url = "https://files.pythonhosted.org/packages/19/c3/03f1ee79a047b48daeca157c89a18509cde22b6b951d642b9b0af1be660a/rpds_py-2026.6.3-cp314-cp314t-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:539d75de9e0d536c84ff18dfeb805398e58227001ce09231a26a08b9aed1ee0e", size = 397500, upload-time = "2026-06-30T07:16:34.471Z" },
-    { url = "https://files.pythonhosted.org/packages/f0/95/8ed0cd8c377dca12aea498f119fe639fc474d1461545c39d2b5872eb1c0f/rpds_py-2026.6.3-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:166cf54d9f44fc6ceb53c7860258dde44a81406646de79f8ed3234fca3b6e538", size = 545978, upload-time = "2026-06-30T07:16:36.45Z" },
-    { url = "https://files.pythonhosted.org/packages/d3/f2/0eb57f0eaa83f8fc152a7e03de968ab77e1f00732bebc892b190c6eebde7/rpds_py-2026.6.3-cp314-cp314t-musllinux_1_2_i686.whl", hash = "sha256:d34c20167764fbcf927194d532dd7e0c56772f0a5f943fa5ef9e9afbba8fb9db", size = 613350, upload-time = "2026-06-30T07:16:38.213Z" },
-    { url = "https://files.pythonhosted.org/packages/5b/de/e0674bdbc3ef7634989b3f854c3f34bc1f587d36e5bfdc5c378d57034619/rpds_py-2026.6.3-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:ea7bb13b7c9a29791f87a0387ba7d3ad3a6d783d827e4d3f27b40a0ff44495e2", size = 576486, upload-time = "2026-06-30T07:16:39.797Z" },
-    { url = "https://files.pythonhosted.org/packages/f2/f6/21101359743cd136ada781e8210a85769578422ba460672eea0e29739200/rpds_py-2026.6.3-cp314-cp314t-win32.whl", hash = "sha256:6de4744d05bd1aa1be4ed7ea1189e3979196808008113bbbf899a460966b925e", size = 201068, upload-time = "2026-06-30T07:16:41.316Z" },
-    { url = "https://files.pythonhosted.org/packages/a6/b2/9574d4d44f7760c2aa32d92a0a4f41698e33f5b204a0bf5c9758f52c79d5/rpds_py-2026.6.3-cp314-cp314t-win_amd64.whl", hash = "sha256:c7b9a2f8f4d8e90af72571d3d495deebdd7e3c75451f5b41719aee166e940fc2", size = 220600, upload-time = "2026-06-30T07:16:43.091Z" },
-    { url = "https://files.pythonhosted.org/packages/08/ae/f23a2697e6ee6340a578b0f136be6483657bef0c6f9497b752bb5c0964bb/rpds_py-2026.6.3-cp315-cp315-macosx_10_12_x86_64.whl", hash = "sha256:e059c5dde6452b44424bd1834557556c226b57781dee1227af23518459722b13", size = 344726, upload-time = "2026-06-30T07:16:44.5Z" },
-    { url = "https://files.pythonhosted.org/packages/c3/63/e7b3a1a5358dd32c930a1062d8e15b67fd6e8922e81df9e91706d66ee5c8/rpds_py-2026.6.3-cp315-cp315-macosx_11_0_arm64.whl", hash = "sha256:2f7c26fbc5acd2522b95d4177fe4710ffd8e9b20529e703ffbf8db4d93903f05", size = 339587, upload-time = "2026-06-30T07:16:46.255Z" },
-    { url = "https://files.pythonhosted.org/packages/ec/64/10a85681916ca55fffb91b0a211f84e34297c109243484dd6394660a8a7c/rpds_py-2026.6.3-cp315-cp315-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:a3086b538543802f84c843911242db20447de00d8752dd0efc936dbcf02218ba", size = 369585, upload-time = "2026-06-30T07:16:48.101Z" },
-    { url = "https://files.pythonhosted.org/packages/76/c2/baf95c7c38823e12ba34407c5f5767a89e5cf2233895e56f608167ae9493/rpds_py-2026.6.3-cp315-cp315-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:8f2e5c5ee828d42cb11760761c0af6507927bec42d0ad5458f97c9203b054617", size = 375479, upload-time = "2026-06-30T07:16:49.93Z" },
-    { url = "https://files.pythonhosted.org/packages/6a/94/0aad06c72d65101e11d33528d438cda99a39ce0da99466e156158f2541d3/rpds_py-2026.6.3-cp315-cp315-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:ed0c1e5d10cdc7135537988c74a0188da68e2f3c30813ba3744ab1e42e0480f9", size = 492418, upload-time = "2026-06-30T07:16:51.641Z" },
-    { url = "https://files.pythonhosted.org/packages/b5/17/de3f5a479a1f056535d7489819639d8cd591ea6281d700390b43b1abd745/rpds_py-2026.6.3-cp315-cp315-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:8c2642a7603ec0b16ed77da4555db3b4b472341904873788327c0b0d7b95f1bb", size = 384123, upload-time = "2026-06-30T07:16:53.622Z" },
-    { url = "https://files.pythonhosted.org/packages/46/7d/bf09bd1b145bb2671c03e1e6d1ab8651858d90d8c7dfeadd85a37a934fd8/rpds_py-2026.6.3-cp315-cp315-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:8e4320744c1ffdd95a603def63344bfab2d33edeab301c5007e7de9f9f5b3885", size = 367351, upload-time = "2026-06-30T07:16:55.241Z" },
-    { url = "https://files.pythonhosted.org/packages/a3/ea/1bb734f314b8be319149ddee80b18bd41372bdcfbdf88d28131c0cd37719/rpds_py-2026.6.3-cp315-cp315-manylinux_2_31_riscv64.whl", hash = "sha256:a9f4645593036b81bbdb36b9c8e0ea0d1c3fee968c4d59db0344c14087ef143a", size = 378827, upload-time = "2026-06-30T07:16:56.841Z" },
-    { url = "https://files.pythonhosted.org/packages/4b/93/d9611e5b25e26df9a3649813ed66193ace9347a7c7fc4ab7cf70e94851c0/rpds_py-2026.6.3-cp315-cp315-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:e55d236be29255554da47abe5c577637db7c24a02b8b46f0ca9524c855801868", size = 395966, upload-time = "2026-06-30T07:16:58.557Z" },
-    { url = "https://files.pythonhosted.org/packages/c3/cb/99d77e16e5534ae1d90629bbe419ba6ee170833a6a85e3aa1cc41726fbbc/rpds_py-2026.6.3-cp315-cp315-musllinux_1_2_aarch64.whl", hash = "sha256:24e9c5386e16669b674a69c156c8eeefcb578f3b3397b713b08e6d60f3c7b187", size = 545680, upload-time = "2026-06-30T07:17:00.164Z" },
-    { url = "https://files.pythonhosted.org/packages/59/15/11a29755f790cef7a2f755e8e14f4f0c33f39489e1893a632a2eee59672b/rpds_py-2026.6.3-cp315-cp315-musllinux_1_2_i686.whl", hash = "sha256:c60924535c75f1566b6eb75b5c31a48a43fef04fa2d0d201acbad8a9969c6107", size = 611853, upload-time = "2026-06-30T07:17:01.962Z" },
-    { url = "https://files.pythonhosted.org/packages/68/86/0c27547e21644da938fb530f7e1a8148dd24d02db07e7a5f2567a17ce710/rpds_py-2026.6.3-cp315-cp315-musllinux_1_2_x86_64.whl", hash = "sha256:38a2fea2787428f811719ceb9114cb78964a3138838320c29ac39526c79c16ba", size = 573715, upload-time = "2026-06-30T07:17:03.693Z" },
-    { url = "https://files.pythonhosted.org/packages/29/71/4d8fcf700931815594bce892255bbd973b94efaf0fc1932b0590df18d886/rpds_py-2026.6.3-cp315-cp315-win32.whl", hash = "sha256:d483fe17f01ad64b7bf7cc38fcefff1ca9fb83f8c2b2542b68f97ffe0611b369", size = 202864, upload-time = "2026-06-30T07:17:05.746Z" },
-    { url = "https://files.pythonhosted.org/packages/eb/62/b577562de0edbb55b2be85ce5fd09c33e386b9b13eee09833af4240fd5c4/rpds_py-2026.6.3-cp315-cp315-win_amd64.whl", hash = "sha256:67e3a721ffc5d8d2210d3671872298c4a84e4b8035cfe42ffd7cde35d772b146", size = 220430, upload-time = "2026-06-30T07:17:07.471Z" },
-    { url = "https://files.pythonhosted.org/packages/c8/95/d6d0b2509825141eef60669a5739eec88dbc6a48053d6c92993a5704defe/rpds_py-2026.6.3-cp315-cp315-win_arm64.whl", hash = "sha256:6e84adbcf4bf841aed8116a8264b9f50b4cb3e7bd89b516122e616ac56ca269e", size = 215877, upload-time = "2026-06-30T07:17:09.008Z" },
-    { url = "https://files.pythonhosted.org/packages/b7/bf/f3ea278f0afd615c1d0f19cb69043a41526e2bb600c2b536eb192218eb27/rpds_py-2026.6.3-cp315-cp315t-macosx_10_12_x86_64.whl", hash = "sha256:ae6dd8f10bd17aad820876d24caec9efdafd80a318d16c0a48edb5e136902c6b", size = 346933, upload-time = "2026-06-30T07:17:10.762Z" },
-    { url = "https://files.pythonhosted.org/packages/9d/29/9907bdf1c5346763cf10b7f6852aad86652168c259def904cbe0082c5864/rpds_py-2026.6.3-cp315-cp315t-macosx_11_0_arm64.whl", hash = "sha256:bdbd97738551fca3917c1bd7188bec1920bb520104f28e7e1007f9ceb17b7690", size = 340274, upload-time = "2026-06-30T07:17:12.266Z" },
-    { url = "https://files.pythonhosted.org/packages/6f/2c/8e03767b5778ef25cebf74a7a91a2c3806f8eced4c92cb7406bbe060756d/rpds_py-2026.6.3-cp315-cp315t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:8b95977e7211527ab0ba576e286d023389fbeeb32a6b7b771665d333c60e5342", size = 370763, upload-time = "2026-06-30T07:17:14.107Z" },
-    { url = "https://files.pythonhosted.org/packages/2e/e1/df2a7e1ba2efd796af26194250b8d42c821b46592311595162af9ef0528d/rpds_py-2026.6.3-cp315-cp315t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:d15fde0e6fb0d88a60d221204873743e5d9f0b7d29165e62cd86d0413ad74ba6", size = 376467, upload-time = "2026-06-30T07:17:15.76Z" },
-    { url = "https://files.pythonhosted.org/packages/6b/de/8a0814d1946af29cb068fb259aa8622f856df1d0bab58429448726b537f5/rpds_py-2026.6.3-cp315-cp315t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:a136d453475ac0fcbda502ef1e6504bd28d6d904700915d278deeab0d00fe140", size = 496689, upload-time = "2026-06-30T07:17:17.308Z" },
-    { url = "https://files.pythonhosted.org/packages/df/f3/f19e0c852ba13694f5a79f3b719331051573cb5693feacf8a88ffffc3a71/rpds_py-2026.6.3-cp315-cp315t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:f826877d462181e5eb1c26a0026b8d0cab05d99844ecb6d8bf3627a2ca0c0442", size = 385340, upload-time = "2026-06-30T07:17:18.928Z" },
-    { url = "https://files.pythonhosted.org/packages/e2/ae/7ec3a9d2d4351f99e37bcb06b6b6f954512646bfdbf9742e1de727865daf/rpds_py-2026.6.3-cp315-cp315t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:79486287de1730dbaff3dbd124d0ca4d2ef7f9d29bf2544f1f93c09b5bcbbd12", size = 372179, upload-time = "2026-06-30T07:17:20.539Z" },
-    { url = "https://files.pythonhosted.org/packages/d3/ac/9cee911dff2aaa9a5a8354f6610bf2e6a616de9197c5fff4f54f82585f1e/rpds_py-2026.6.3-cp315-cp315t-manylinux_2_31_riscv64.whl", hash = "sha256:808345f53cb952433ca2816f1604ff3515608a81784954f38d4452acfe8e61d5", size = 379993, upload-time = "2026-06-30T07:17:22.212Z" },
-    { url = "https://files.pythonhosted.org/packages/83/6b/7c2a07ba88d1e9a936612f7a5d067467ed03d971d5a06f7d309dff044a7e/rpds_py-2026.6.3-cp315-cp315t-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:1967debc37f64f2c4dc90a7f563aec558b471966e12adcac4e1c4240496b6ebf", size = 398909, upload-time = "2026-06-30T07:17:23.66Z" },
-    { url = "https://files.pythonhosted.org/packages/97/0b/776ffcb66783637b0031f6d58d6fb55913c8b5abf00aeecd46bf933fb477/rpds_py-2026.6.3-cp315-cp315t-musllinux_1_2_aarch64.whl", hash = "sha256:f0840b5b17057f7fd918b76183a4b5a0635f43e14eb2ce60dce1d4ee4707ea00", size = 546584, upload-time = "2026-06-30T07:17:25.264Z" },
-    { url = "https://files.pythonhosted.org/packages/55/33/ba3bc04d7092bd553c9b2b195624992d2cc4f3de1f380b7b93cbee67bd79/rpds_py-2026.6.3-cp315-cp315t-musllinux_1_2_i686.whl", hash = "sha256:faa679d19a6696fd54259ad321251ad77a13e70e03dd834daa762a44fb6196ef", size = 614357, upload-time = "2026-06-30T07:17:26.888Z" },
-    { url = "https://files.pythonhosted.org/packages/8b/71/14edf065f04630b1a8472f7653cad03f6c478bcf95ea0e6aed55451e33ea/rpds_py-2026.6.3-cp315-cp315t-musllinux_1_2_x86_64.whl", hash = "sha256:23a439f31ccbeff1574e24889128821d1f7917470e830cf6544dced1c662262a", size = 576533, upload-time = "2026-06-30T07:17:28.546Z" },
-    { url = "https://files.pythonhosted.org/packages/ba/76/65002b08596c389105720a8c0d22298b8dc25a4baf89b2ce431343c8b1de/rpds_py-2026.6.3-cp315-cp315t-win32.whl", hash = "sha256:913ca42ccad3f8cc6e292b587ae8ae49c8c823e5dce51a736252fc7c7cdfa577", size = 201204, upload-time = "2026-06-30T07:17:30.193Z" },
-    { url = "https://files.pythonhosted.org/packages/8c/97/d855d6b3c322d1f27e26f5241c42016b56cf01377ea8ed348285f54652f0/rpds_py-2026.6.3-cp315-cp315t-win_amd64.whl", hash = "sha256:ae3d4fe8c0b9213624fdce7279d70e3b148b682ca20719ebd193a23ebfa47324", size = 220719, upload-time = "2026-06-30T07:17:31.788Z" },
-]
-
-[[package]]
-name = "s3transfer"
-version = "0.19.2"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "botocore" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/76/43/35e4d8aa320bffe8287fe8f65f578fa2d2db0a64212f0e710dce58267854/s3transfer-0.19.2.tar.gz", hash = "sha256:ba0309fd86be3c27dbf78cdd813c13c5e1df16e5874b99d2535ebbdfb9892993", size = 165592, upload-time = "2026-07-22T19:30:44.432Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/bc/e7/5c595c75e9f41a44f30e526eda465ea0b4eec93470e074e4a111b253f13a/s3transfer-0.19.2-py3-none-any.whl", hash = "sha256:d8168eccca828cbb2cd573675333f3bddd254313a9c42494b84c76b539e8ba25", size = 90216, upload-time = "2026-07-22T19:30:43.251Z" },
-]
-
-[[package]]
-name = "six"
-version = "1.17.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/94/e7/b2c673351809dca68a0e064b6af791aa332cf192da575fd474ed7d6f16a2/six-1.17.0.tar.gz", hash = "sha256:ff70335d468e7eb6ec65b95b99d3a2836546063f63acc5171de367e834932a81", size = 34031, upload-time = "2024-12-04T17:35:28.174Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/b7/ce/149a00dd41f10bc29e5921b496af8b574d8413afcd5e30dfa0ed46c2cc5e/six-1.17.0-py2.py3-none-any.whl", hash = "sha256:4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274", size = 11050, upload-time = "2024-12-04T17:35:26.475Z" },
-]
-
-[[package]]
-name = "sniffio"
-version = "1.3.1"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/a2/87/a6771e1546d97e7e041b6ae58d80074f81b7d5121207425c964ddf5cfdbd/sniffio-1.3.1.tar.gz", hash = "sha256:f4324edc670a0f49750a81b895f35c3adb843cca46f0530f79fc1babb23789dc", size = 20372, upload-time = "2024-02-25T23:20:04.057Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/e9/44/75a9c9421471a6c4805dbf2356f7c181a29c1879239abab1ea2cc8f38b40/sniffio-1.3.1-py3-none-any.whl", hash = "sha256:2f6da418d1f1e0fddd844478f41680e794e6051915791a034ff65e5f100525a2", size = 10235, upload-time = "2024-02-25T23:20:01.196Z" },
-]
-
-[[package]]
-name = "tiktoken"
-version = "0.14.0"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "regex" },
-    { name = "requests" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/66/62/167a842aa0429d45f5e797354fd4343a96f6043d67d0513c675c7b8d36e6/tiktoken-0.14.0.tar.gz", hash = "sha256:231dec90efcdccf1b565a1416107736f1e09b1a08fe736ef9d6363e626d03874", size = 38898, upload-time = "2026-08-17T19:49:49.514Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/8c/da/e273746b9d24a63c776bc60fba914351573ad9c575b52601eb5e60632564/tiktoken-0.14.0-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:8e947aefe98ef74cce94923f90e48c98fe34eb1ec0a6bfdfadfc5a96359bfc36", size = 1094408, upload-time = "2026-08-17T19:48:49.269Z" },
-    { url = "https://files.pythonhosted.org/packages/69/9f/fe6b1aca23331aa5271df5a4bd07bf68a7059254d47faee1b8272592a777/tiktoken-0.14.0-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:d6cebe67765569df3dafac8474e4eccf5c19d24140492567a5e58a11445732a4", size = 1038499, upload-time = "2026-08-17T19:48:50.666Z" },
-    { url = "https://files.pythonhosted.org/packages/0b/35/e9f47647c9e163bd1de30fe1a491669b7248cfc67b7404c35c009a701e1a/tiktoken-0.14.0-cp312-cp312-manylinux_2_28_aarch64.whl", hash = "sha256:7db45b98e94adf4173a5cd7422b150999a7ee11ff847783a14f6e1b80cc38cb6", size = 1186355, upload-time = "2026-08-17T19:48:51.93Z" },
-    { url = "https://files.pythonhosted.org/packages/51/11/9976ad86980a00cdef05e730a0127a2578a1bc6d11644d8d47246de2eb26/tiktoken-0.14.0-cp312-cp312-manylinux_2_28_x86_64.whl", hash = "sha256:7896eea257fe497a2b7134474d909156c6744ce8da35bce88011a960e008aa0d", size = 1204197, upload-time = "2026-08-17T19:48:53.18Z" },
-    { url = "https://files.pythonhosted.org/packages/d4/9c/7035b0bcfaa68d1ee4803fc5be5214ad865669b05bd20e7105ae8a18afc6/tiktoken-0.14.0-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:b950248272f1b303dc32986396e2dccfa10cf6d1e83ec8f0bba1776660305482", size = 1250635, upload-time = "2026-08-17T19:48:54.392Z" },
-    { url = "https://files.pythonhosted.org/packages/bc/1d/69cabf18bed7f4366da076735816abce0d4db3fae491ae338a6612128777/tiktoken-0.14.0-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:3de75343041a1c57333b1e707ac8a9769738241d7d6a55d39e12cf84548337c6", size = 1316085, upload-time = "2026-08-17T19:48:55.525Z" },
-    { url = "https://files.pythonhosted.org/packages/bd/bd/a2e884fb1402cba5be08836590320012b2d8ada0e2eef9911a64df4bcd2d/tiktoken-0.14.0-cp312-cp312-win_amd64.whl", hash = "sha256:087538c080e5ff421abd3a0785ed63c5111d06af98e6cd0d374dbe5969147ca3", size = 941208, upload-time = "2026-08-17T19:48:56.938Z" },
-    { url = "https://files.pythonhosted.org/packages/50/53/ee1453623bf65f019328721ccb6587846d2c5b7b82f34e73ca09101f072e/tiktoken-0.14.0-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:e9c5fe393aab56469f04e432ff851216d3def3436cf5f07e442a240164bf500f", size = 1094198, upload-time = "2026-08-17T19:48:57.955Z" },
-    { url = "https://files.pythonhosted.org/packages/ad/5f/6448cfe278c3664ba9ec5b5ac08344341f7dc3d42888476e215a14eda2be/tiktoken-0.14.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:cbe2cc3bba939bcdaf103e03df9d5039d33887080b315624be28ec69059e5f94", size = 1038820, upload-time = "2026-08-17T19:48:59.015Z" },
-    { url = "https://files.pythonhosted.org/packages/69/3b/d67eac1bcce9dee3abe23aff5e3ded3116bbebaf67b80a0811c06d3806fc/tiktoken-0.14.0-cp313-cp313-manylinux_2_28_aarch64.whl", hash = "sha256:2157f52e4b4d7ac5ecc7457b3716834706e7ef9a46f5144029bfeb7cf71f4e06", size = 1186175, upload-time = "2026-08-17T19:49:00.068Z" },
-    { url = "https://files.pythonhosted.org/packages/37/62/cae690d9783146b0f81f564ada0f8f611de68178c0c9c7e1e969f0516b48/tiktoken-0.14.0-cp313-cp313-manylinux_2_28_x86_64.whl", hash = "sha256:26e60f6a956ee171ab728b37b8439905d7ea1db435c30f9822f291e9861c861d", size = 1203884, upload-time = "2026-08-17T19:49:01.163Z" },
-    { url = "https://files.pythonhosted.org/packages/b9/1e/633e30237b94e383cf814145499079f3bb9cdd4aeafc1bc42e01b0f810a6/tiktoken-0.14.0-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:380873f330b741c4435574f37edb20813d04603ace2d53e0a63560e1fec83010", size = 1250980, upload-time = "2026-08-17T19:49:02.274Z" },
-    { url = "https://files.pythonhosted.org/packages/cb/56/4c12f07b812f84206f38d723eb1ebfdd34bad9309b5dbc0bee6bbcff4cbf/tiktoken-0.14.0-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:3fd7c14b1cb45b486c39fc9b3443bb341f3e2fc7e6f31247f3435a5836651632", size = 1315434, upload-time = "2026-08-17T19:49:03.434Z" },
-    { url = "https://files.pythonhosted.org/packages/c9/e0/c65603f0c44811def666d3fbf611bf2af3b5e1ef613e06c19411419830b3/tiktoken-0.14.0-cp313-cp313-win_amd64.whl", hash = "sha256:90a762670c7f968184723769a06ed51f5cf5ce5dcd1e30164f25c72d85c2d1f1", size = 940883, upload-time = "2026-08-17T19:49:04.583Z" },
-    { url = "https://files.pythonhosted.org/packages/59/b0/1cf129f4af8fc513931f931023def596b7c4bfc77026513cd9d851da9e88/tiktoken-0.14.0-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:e067f4cbcc5d036e8aff7fe7a6b530a8f4de2e4616ad9005a24a1879e24e6450", size = 1096273, upload-time = "2026-08-17T19:49:05.807Z" },
-    { url = "https://files.pythonhosted.org/packages/62/85/2ae74575e321148484147e10b53c3b1717c59ebaa9edb4fe18b1f5c055f8/tiktoken-0.14.0-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:f2af4a336ea56d6c14f27741a0e1d8294a35dd0b038bcf990d232ebb54eb994b", size = 1040269, upload-time = "2026-08-17T19:49:06.943Z" },
-    { url = "https://files.pythonhosted.org/packages/89/29/92a1120a12e4bcf2d5464350d1a91b68a433d63ce656bb7f806c27aec09c/tiktoken-0.14.0-cp314-cp314-manylinux_2_28_aarch64.whl", hash = "sha256:f702e0aeeb6506e57687e881c59e844ebe8f0a6a097ddafe20e3ab25f387be4e", size = 1186101, upload-time = "2026-08-17T19:49:08.102Z" },
-    { url = "https://files.pythonhosted.org/packages/5b/7d/144af98dc5ad68108451a82e2f5a17f80e2663f5115058b8dfd215c1ad02/tiktoken-0.14.0-cp314-cp314-manylinux_2_28_x86_64.whl", hash = "sha256:e3442bbb2f0c588cec876061e37ae67b455b9df9978b003c8fe30e45f2ef5b42", size = 1204457, upload-time = "2026-08-17T19:49:09.28Z" },
-    { url = "https://files.pythonhosted.org/packages/e6/1f/be7cb06ab2108f612f3e92e7b76cf391e192db0db37a984616f0cc32aafc/tiktoken-0.14.0-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:979c1524f753b662b0f3cd261b135afe6659cce33caaa7a5ea00dd1756b3055c", size = 1251716, upload-time = "2026-08-17T19:49:10.509Z" },
-    { url = "https://files.pythonhosted.org/packages/ab/6b/81f158d0f90adb826cd704069c2129a046cb784a2a09861009519fc41cf4/tiktoken-0.14.0-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:2cc19ac87b41c9493c9778ff5847f0c8bbcf5bd0ec6b87ce06c1c802adc8a771", size = 1315432, upload-time = "2026-08-17T19:49:11.844Z" },
-    { url = "https://files.pythonhosted.org/packages/fc/ec/f5fa35ec13f07279fdcaf3cc9c04bbb154ea591d23978651f2b672593e8a/tiktoken-0.14.0-cp314-cp314-win_amd64.whl", hash = "sha256:eceeff0c62419bc78d4b6e70a4762a4d25df3ae8f2d5946e3853ce93e7a57098", size = 988046, upload-time = "2026-08-17T19:49:13.282Z" },
-    { url = "https://files.pythonhosted.org/packages/68/c9/7756717408d3d0dfea3f046c9466144b28afde39ff69d5808f2475dcd7f5/tiktoken-0.14.0-cp314-cp314t-macosx_10_15_x86_64.whl", hash = "sha256:6eb94895c45f26bb8f5546e5fd8a069efcf6e3f108ea9d5cbe3bf6f7f3983438", size = 1096261, upload-time = "2026-08-17T19:49:14.351Z" },
-    { url = "https://files.pythonhosted.org/packages/79/29/46ad8061f57bd9f8b2ea0aa82bf574e0f2aa040b0857a1582adba9957899/tiktoken-0.14.0-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:86951a971c53979ec857bd8c4a32dc227ab0fd33f6c12a3bd62d3fbf5f0bfcaa", size = 1040183, upload-time = "2026-08-17T19:49:15.707Z" },
-    { url = "https://files.pythonhosted.org/packages/5a/7c/3184d17b868456f17b60b1a75f5ec0405618a43aa753336df341d8f11781/tiktoken-0.14.0-cp314-cp314t-manylinux_2_28_aarch64.whl", hash = "sha256:e2eca764c53490f8930dbce329e0769f11108d87d908282a80c5c130e26e7037", size = 1186719, upload-time = "2026-08-17T19:49:16.84Z" },
-    { url = "https://files.pythonhosted.org/packages/0b/e8/46de4400d5bf859f640feee85bd7e32235f68ddf25db53c63be78e581e3a/tiktoken-0.14.0-cp314-cp314t-manylinux_2_28_x86_64.whl", hash = "sha256:26cc4b4840fa0e9f4b72ed489883e12f57e00d1021ca794720e3c29a12f0edef", size = 1204660, upload-time = "2026-08-17T19:49:17.987Z" },
-    { url = "https://files.pythonhosted.org/packages/29/ce/af8964c38bc8226dd8950305b7a255fa33345d5572f78af7275a313d28e0/tiktoken-0.14.0-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:2fc834fbe3f6a0736905c36ab709537e6840dbd63b982dc9e0216ae7d305ba1a", size = 1250932, upload-time = "2026-08-17T19:49:19.28Z" },
-    { url = "https://files.pythonhosted.org/packages/1d/4b/323631116fc986d9cc5bbeb2b8223c7c85e61a8bb94ea5ab4951023b149b/tiktoken-0.14.0-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:ca4db6ff5c5bf600f9b7761a0070ed44dfe5797a76bd432fb978bc480ef40c58", size = 1315190, upload-time = "2026-08-17T19:49:20.467Z" },
-    { url = "https://files.pythonhosted.org/packages/18/8b/ba48a73729c9270989b36f37ab2ed5525e52690d715097c9fa791aaa5d05/tiktoken-0.14.0-cp314-cp314t-win_amd64.whl", hash = "sha256:7aab286a020660a039097912a088236b985d18a3090d73f136c4413d29d37ca0", size = 987717, upload-time = "2026-08-17T19:49:21.704Z" },
-    { url = "https://files.pythonhosted.org/packages/1d/10/b73b7e319179e0f60b32475f783b044f9cece872c53b6662664e9084b0d0/tiktoken-0.14.0-cp315-cp315-macosx_10_15_x86_64.whl", hash = "sha256:14b47e3674f2624803a8acc8fb367b7e24fc53055f9df3296482fe9a3a34a232", size = 1096280, upload-time = "2026-08-17T19:49:22.779Z" },
-    { url = "https://files.pythonhosted.org/packages/c2/6b/09999a9bf1d559670d1680e8f8e419ac0e2c5f6aac82e9bfdf70f260b30a/tiktoken-0.14.0-cp315-cp315-macosx_11_0_arm64.whl", hash = "sha256:19d643d701fdaa70e5b9c7f8f96abcaffe77ca5e482a3a1a7dde46feb4284695", size = 1040433, upload-time = "2026-08-17T19:49:23.998Z" },
-    { url = "https://files.pythonhosted.org/packages/cd/7b/8537be0836f3df99b2a636b44399bfa43cd757f2b8b4097dacb794cf24a7/tiktoken-0.14.0-cp315-cp315-manylinux_2_28_aarch64.whl", hash = "sha256:e4ddf863b59347deaa92302dcd90e5eb003cdc9be06ec2b692c38d1bdd9efd49", size = 1186989, upload-time = "2026-08-17T19:49:25.021Z" },
-    { url = "https://files.pythonhosted.org/packages/7c/9d/f9c56d7a943a4468abf9ef37661bb9b8e0cd3aa8aa87368c7146cc3f3222/tiktoken-0.14.0-cp315-cp315-manylinux_2_28_x86_64.whl", hash = "sha256:60c47ca69ddda0dea8256fffd12e1b86f4b59734a20e4a70c61f63cc5f021df4", size = 1204615, upload-time = "2026-08-17T19:49:26.37Z" },
-    { url = "https://files.pythonhosted.org/packages/4b/d2/98a38579db25c4a8a84e31dd95d9072ec5f21f7e70de591da0412e29b25b/tiktoken-0.14.0-cp315-cp315-musllinux_1_2_aarch64.whl", hash = "sha256:728303a072163130c5b477b1f20d6211895569c1d5302c24ffc93a3009160871", size = 1251828, upload-time = "2026-08-17T19:49:27.423Z" },
-    { url = "https://files.pythonhosted.org/packages/0c/83/467be424746c039c5493c0f4102feab16b9b48eb6f5c089b2a2438e3cde2/tiktoken-0.14.0-cp315-cp315-musllinux_1_2_x86_64.whl", hash = "sha256:3c5349c9f916283bba32bec8af69b763e4faa304dc004d0eaaea66a3cf004c1f", size = 1316260, upload-time = "2026-08-17T19:49:29.101Z" },
-    { url = "https://files.pythonhosted.org/packages/02/ee/ddf46ca78e371f5890e96b6e7d089a85b3536432be219851eb0481786ca8/tiktoken-0.14.0-cp315-cp315-win_amd64.whl", hash = "sha256:1b6e4adcfd285c44502aed51df98aaaca4f0fea028165dbf8a9e857b9f98d8ea", size = 988230, upload-time = "2026-08-17T19:49:30.246Z" },
-    { url = "https://files.pythonhosted.org/packages/2a/00/5162e90c851a28da18ed382d34898b79a8022548e5619a64e14c03ce7c3d/tiktoken-0.14.0-cp315-cp315t-macosx_10_15_x86_64.whl", hash = "sha256:11d8211b290855d2721334ff17dd9b3a17bfb26872be01f25d73612ef7ece890", size = 1096186, upload-time = "2026-08-17T19:49:31.656Z" },
-    { url = "https://files.pythonhosted.org/packages/65/97/a5a7bfccf25b1bb65e82bae8edff11ac3c9c041c374b7b4a823d60c38133/tiktoken-0.14.0-cp315-cp315t-macosx_11_0_arm64.whl", hash = "sha256:d0781223705199b289faa59601bb9c2441712d4c600dd13c43d8fd6a33d22cd5", size = 1039947, upload-time = "2026-08-17T19:49:32.848Z" },
-    { url = "https://files.pythonhosted.org/packages/fb/ba/ef427fc638f1439181c5e12dd26b70e881861f89c007aa7e5b36300f8342/tiktoken-0.14.0-cp315-cp315t-manylinux_2_28_aarch64.whl", hash = "sha256:2ea70afba6b9eddbf22c165142e5f0a2ad7aa36a452873c48b57bb2aeb8492ae", size = 1186997, upload-time = "2026-08-17T19:49:34.121Z" },
-    { url = "https://files.pythonhosted.org/packages/3e/88/2f3f85a968cdc514152129af0a060ebcccb067005a2f29b0d5ef3c838514/tiktoken-0.14.0-cp315-cp315t-manylinux_2_28_x86_64.whl", hash = "sha256:78571efc311c30b73f31eb949a921d6dac39a5d9dc42d1cfa8f8db157b3447b1", size = 1205211, upload-time = "2026-08-17T19:49:35.284Z" },
-    { url = "https://files.pythonhosted.org/packages/4e/f6/80760e98a08e6649d2d68afb6035af713121dfb615acce8c4f73810ec438/tiktoken-0.14.0-cp315-cp315t-musllinux_1_2_aarch64.whl", hash = "sha256:86f66c85e796f5d05d5c4a60ec1d40cbfebc47a32464053528c797163fa9ab89", size = 1251479, upload-time = "2026-08-17T19:49:36.419Z" },
-    { url = "https://files.pythonhosted.org/packages/c5/84/50966fb6918a0fb9b32721277e5342bf729a2d74350074d662fbedf9772e/tiktoken-0.14.0-cp315-cp315t-musllinux_1_2_x86_64.whl", hash = "sha256:149d97453c4c98c04b081d64a85e635921269b532710d6faf81e9e82b790e7d3", size = 1316673, upload-time = "2026-08-17T19:49:37.756Z" },
-    { url = "https://files.pythonhosted.org/packages/35/5e/9b01afd037bfa22a0033963fa091e0f75b6fb15cd85bffb42ff86e697323/tiktoken-0.14.0-cp315-cp315t-win_amd64.whl", hash = "sha256:561e7580f84a79859af1ef6f676968e9030fcc3fe195700b15235bca64f009c9", size = 987929, upload-time = "2026-08-17T19:49:38.947Z" },
-]
-
-[[package]]
-name = "tokenizers"
-version = "0.23.1"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "huggingface-hub" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/c1/60/21f715d9faba5f5407ff759472ade058ec4a507ad62bcea47cb847239a73/tokenizers-0.23.1.tar.gz", hash = "sha256:1feeeadf865a7915adc25445dea30e9933e593c31bb96c277cee36de227c8bfa", size = 365748, upload-time = "2026-04-27T14:43:25.606Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/87/39/b87a87d5bb9470610b80a2d31df42fcffeaf35118b8b97952b2aff598cc7/tokenizers-0.23.1-cp310-abi3-macosx_10_12_x86_64.whl", hash = "sha256:e03d6ffcbe0d56ee9c1ccd070e70a13fa750727c0277e138152acbc0252c2224", size = 3146732, upload-time = "2026-04-27T14:43:15.427Z" },
-    { url = "https://files.pythonhosted.org/packages/e2/6a/068ed9f6e444c9d7e9d55ce134181325700f3d7f30410721bdc8f848d727/tokenizers-0.23.1-cp310-abi3-macosx_11_0_arm64.whl", hash = "sha256:e0948bbb1ac1d7cdfc9fb6d62c596e3b7550036ad60ecd654a66ad273326324e", size = 3054954, upload-time = "2026-04-27T14:43:13.745Z" },
-    { url = "https://files.pythonhosted.org/packages/6c/36/e006edf031154cba92b8416057d92c3abe3635e4c4b0aa0b5b9bb39dde70/tokenizers-0.23.1-cp310-abi3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:1bf13402aff9bc533c89cb849ec3b412dc3fbeacc9744840e423d7bf3f7dc0e3", size = 3374081, upload-time = "2026-04-27T14:43:01.241Z" },
-    { url = "https://files.pythonhosted.org/packages/a2/ef/7735d226f9c7f874a6bee5e3f27fb25ecabdf207d37b8cf45286d0795893/tokenizers-0.23.1-cp310-abi3-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:f836ca703b89ae07919a309f9651f7a88fd5a33d5f718ba5ad0870ec0256bad6", size = 3247641, upload-time = "2026-04-27T14:43:03.856Z" },
-    { url = "https://files.pythonhosted.org/packages/b9/d9/24827036f6e21297bfffda0768e58eb6096a4f411e932964a01707857931/tokenizers-0.23.1-cp310-abi3-manylinux_2_17_i686.manylinux2014_i686.whl", hash = "sha256:ae848657742035523fdf261773630cb819a26995fcd3d9ecae0c1daf6e5a4959", size = 3585624, upload-time = "2026-04-27T14:43:10.664Z" },
-    { url = "https://files.pythonhosted.org/packages/0c/9a/22f3582b3a4f49358293a5206e25317621ee4526bfe9cdaa0f07a12e770e/tokenizers-0.23.1-cp310-abi3-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:53b09e85775d5187941e7bab30e941b4134ab4a7dd8c68e783d231fb7ca27c51", size = 3844062, upload-time = "2026-04-27T14:43:05.643Z" },
-    { url = "https://files.pythonhosted.org/packages/7e/65/b8f8814eef95800f20721384136d9a1d22241d50b2874357cb70542c392f/tokenizers-0.23.1-cp310-abi3-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:ea5a0ce170074329faaa8ea3f6400ecde604b6678192688533af80980daae71a", size = 3460098, upload-time = "2026-04-27T14:43:08.854Z" },
-    { url = "https://files.pythonhosted.org/packages/0d/d5/1353e5f677ec27c2494fb6a6725e82d56c985f53e90ec511369e7e4f02c6/tokenizers-0.23.1-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:5075b405006415ea148a992d093699c66eb01952bf59f4d5727089a98bda45a4", size = 3346235, upload-time = "2026-04-27T14:43:12.377Z" },
-    { url = "https://files.pythonhosted.org/packages/71/89/39b6b8fc073fb6d413d0147aa333dc7eff7be65639ac9d19930a0b21bf33/tokenizers-0.23.1-cp310-abi3-manylinux_2_31_riscv64.whl", hash = "sha256:56f3a77de629917652f876294dc9fe6bad4a0c43bc229dc72e59bb23a0f4729a", size = 3426398, upload-time = "2026-04-27T14:43:07.264Z" },
-    { url = "https://files.pythonhosted.org/packages/0f/80/127c854da64827e5b79264ce524993a90dddcb320e5cd42412c5c02f9e8a/tokenizers-0.23.1-cp310-abi3-musllinux_1_2_aarch64.whl", hash = "sha256:9d10a6d957ef01896dc274e890eee27d41bd0e74ef31e60616f0fc311345184e", size = 9823279, upload-time = "2026-04-27T14:43:17.222Z" },
-    { url = "https://files.pythonhosted.org/packages/fe/ba/44c2502feb1a058f096ddfb4e0996ef3225a01a388e1a9b094e91689fe93/tokenizers-0.23.1-cp310-abi3-musllinux_1_2_armv7l.whl", hash = "sha256:1974288a609c343774f1b897c8b482c791ab17b75ab5c8c2b1737565c1d82288", size = 9644986, upload-time = "2026-04-27T14:43:19.45Z" },
-    { url = "https://files.pythonhosted.org/packages/9e/c1/464019a9fb059870bfe4eebb4ba12208f3042035e258bf5e782906bd3847/tokenizers-0.23.1-cp310-abi3-musllinux_1_2_i686.whl", hash = "sha256:120468fb4c24faf0543c835a4fabafa4deb3f20a035c9b6e83d0b553a97615d4", size = 9976181, upload-time = "2026-04-27T14:43:21.463Z" },
-    { url = "https://files.pythonhosted.org/packages/79/94/3ac1432bda31626071e9b6a12709b97ae05131c804b94c8f3ac622c5da32/tokenizers-0.23.1-cp310-abi3-musllinux_1_2_x86_64.whl", hash = "sha256:e3d8f40ea6268047de7046906326abed5134f27d4e8447b23763afe5808c8a96", size = 10113853, upload-time = "2026-04-27T14:43:23.617Z" },
-    { url = "https://files.pythonhosted.org/packages/6a/dd/631b21433c771b1382535326f0eca80b9c9cee2e64961dd993bc9ac4669e/tokenizers-0.23.1-cp310-abi3-win32.whl", hash = "sha256:93120a930b919416da7cd10a2f606ac9919cc69cacae7980fa2140e277660948", size = 2536263, upload-time = "2026-04-27T14:43:29.888Z" },
-    { url = "https://files.pythonhosted.org/packages/97/c9/2553f72aaf65a2797d4229e37fa7fbe38ffbf3e32912d31bdd78b3323e59/tokenizers-0.23.1-cp310-abi3-win_amd64.whl", hash = "sha256:e7bfaf995c1bdbbd21d13539decb6650967013759318627d85daeb7881af16b7", size = 2798223, upload-time = "2026-04-27T14:43:28.51Z" },
-    { url = "https://files.pythonhosted.org/packages/cd/2b/2be299bab55fc595e3d38567edb1a87f86e594842968fa9515a07bdcf422/tokenizers-0.23.1-cp310-abi3-win_arm64.whl", hash = "sha256:a26197957d8e4425dfba746315f3c425ea00cfa8367c5fbc4ec73447893dcea9", size = 2664127, upload-time = "2026-04-27T14:43:26.949Z" },
-]
-
-[[package]]
-name = "tqdm"
-version = "4.70.0"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "colorama", marker = "sys_platform == 'win32'" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/21/3b/6c24bec5be5e743ffd99576daa5cc077722fc7d5bbc00bd133fa0c698dc6/tqdm-4.70.0.tar.gz", hash = "sha256:55b0b0dbd97462d06ebee91e4dac24ed4d4702be82b24f07e6c1d27e08cea220", size = 795438, upload-time = "2026-07-27T11:33:15.271Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/f9/1c/01bfd571a64e7f270e6bab5e33777debe0edc56759233ce84f27dec92d14/tqdm-4.70.0-py3-none-any.whl", hash = "sha256:7f585706bfddbdebf89daac705b2dfcc16890130727d3197ca62c732b4310953", size = 80184, upload-time = "2026-07-27T11:33:13.167Z" },
-]
-
-[[package]]
-name = "typing-extensions"
-version = "4.16.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/f6/cc/6253133b5bb138fc3306cebfbda2c520f545d36b5be2c7255cc528bb45d6/typing_extensions-4.16.0.tar.gz", hash = "sha256:dc983d19a509c94dba722ee6abd33940f7c05a89e243c47e907eb4db6f1a43e5", size = 113555, upload-time = "2026-07-02T08:40:05.92Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/49/d3/b8441a820a491ddfc024b0b0cf0393375b75ea13866d9c66727e54c2fc80/typing_extensions-4.16.0-py3-none-any.whl", hash = "sha256:481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8", size = 45571, upload-time = "2026-07-02T08:40:04.659Z" },
-]
-
-[[package]]
-name = "typing-inspection"
-version = "0.4.4"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "typing-extensions" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/a3/26/b09b8010994eccc3c09092e6b34058f36a460eea2d4c3e8b910c695975a0/typing_inspection-0.4.4.tar.gz", hash = "sha256:547274fa6b0a561ccf549cc9524b999a578e737d015d8709d021f9d0d13bea47", size = 76928, upload-time = "2026-08-12T12:37:25.997Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/67/81/4add07e5172b7ac40d8ed5ff580409a7801a4fe26d529bdd915401dabfbe/typing_inspection-0.4.4-py3-none-any.whl", hash = "sha256:65b8397ba37ccbce054456aaccddfc91e6e3083c92824df348d96ca832f3f147", size = 14750, upload-time = "2026-08-12T12:37:24.648Z" },
-]
-
-[[package]]
-name = "urllib3"
-version = "2.7.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/53/0c/06f8b233b8fd13b9e5ee11424ef85419ba0d8ba0b3138bf360be2ff56953/urllib3-2.7.0.tar.gz", hash = "sha256:231e0ec3b63ceb14667c67be60f2f2c40a518cb38b03af60abc813da26505f4c", size = 433602, upload-time = "2026-05-07T16:13:18.596Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/7f/3e/5db95bcf282c52709639744ca2a8b149baccf648e39c8cc87553df9eae0c/urllib3-2.7.0-py3-none-any.whl", hash = "sha256:9fb4c81ebbb1ce9531cce37674bbc6f1360472bc18ca9a553ede278ef7276897", size = 131087, upload-time = "2026-05-07T16:13:17.151Z" },
-]
-
-[[package]]
-name = "watchdog"
-version = "6.0.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/db/7d/7f3d619e951c88ed75c6037b246ddcf2d322812ee8ea189be89511721d54/watchdog-6.0.0.tar.gz", hash = "sha256:9ddf7c82fda3ae8e24decda1338ede66e1c99883db93711d8fb941eaa2d8c282", size = 131220, upload-time = "2024-11-01T14:07:13.037Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/39/ea/3930d07dafc9e286ed356a679aa02d777c06e9bfd1164fa7c19c288a5483/watchdog-6.0.0-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:bdd4e6f14b8b18c334febb9c4425a878a2ac20efd1e0b231978e7b150f92a948", size = 96471, upload-time = "2024-11-01T14:06:37.745Z" },
-    { url = "https://files.pythonhosted.org/packages/12/87/48361531f70b1f87928b045df868a9fd4e253d9ae087fa4cf3f7113be363/watchdog-6.0.0-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:c7c15dda13c4eb00d6fb6fc508b3c0ed88b9d5d374056b239c4ad1611125c860", size = 88449, upload-time = "2024-11-01T14:06:39.748Z" },
-    { url = "https://files.pythonhosted.org/packages/5b/7e/8f322f5e600812e6f9a31b75d242631068ca8f4ef0582dd3ae6e72daecc8/watchdog-6.0.0-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:6f10cb2d5902447c7d0da897e2c6768bca89174d0c6e1e30abec5421af97a5b0", size = 89054, upload-time = "2024-11-01T14:06:41.009Z" },
-    { url = "https://files.pythonhosted.org/packages/68/98/b0345cabdce2041a01293ba483333582891a3bd5769b08eceb0d406056ef/watchdog-6.0.0-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:490ab2ef84f11129844c23fb14ecf30ef3d8a6abafd3754a6f75ca1e6654136c", size = 96480, upload-time = "2024-11-01T14:06:42.952Z" },
-    { url = "https://files.pythonhosted.org/packages/85/83/cdf13902c626b28eedef7ec4f10745c52aad8a8fe7eb04ed7b1f111ca20e/watchdog-6.0.0-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:76aae96b00ae814b181bb25b1b98076d5fc84e8a53cd8885a318b42b6d3a5134", size = 88451, upload-time = "2024-11-01T14:06:45.084Z" },
-    { url = "https://files.pythonhosted.org/packages/fe/c4/225c87bae08c8b9ec99030cd48ae9c4eca050a59bf5c2255853e18c87b50/watchdog-6.0.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:a175f755fc2279e0b7312c0035d52e27211a5bc39719dd529625b1930917345b", size = 89057, upload-time = "2024-11-01T14:06:47.324Z" },
-    { url = "https://files.pythonhosted.org/packages/a9/c7/ca4bf3e518cb57a686b2feb4f55a1892fd9a3dd13f470fca14e00f80ea36/watchdog-6.0.0-py3-none-manylinux2014_aarch64.whl", hash = "sha256:7607498efa04a3542ae3e05e64da8202e58159aa1fa4acddf7678d34a35d4f13", size = 79079, upload-time = "2024-11-01T14:06:59.472Z" },
-    { url = "https://files.pythonhosted.org/packages/5c/51/d46dc9332f9a647593c947b4b88e2381c8dfc0942d15b8edc0310fa4abb1/watchdog-6.0.0-py3-none-manylinux2014_armv7l.whl", hash = "sha256:9041567ee8953024c83343288ccc458fd0a2d811d6a0fd68c4c22609e3490379", size = 79078, upload-time = "2024-11-01T14:07:01.431Z" },
-    { url = "https://files.pythonhosted.org/packages/d4/57/04edbf5e169cd318d5f07b4766fee38e825d64b6913ca157ca32d1a42267/watchdog-6.0.0-py3-none-manylinux2014_i686.whl", hash = "sha256:82dc3e3143c7e38ec49d61af98d6558288c415eac98486a5c581726e0737c00e", size = 79076, upload-time = "2024-11-01T14:07:02.568Z" },
-    { url = "https://files.pythonhosted.org/packages/ab/cc/da8422b300e13cb187d2203f20b9253e91058aaf7db65b74142013478e66/watchdog-6.0.0-py3-none-manylinux2014_ppc64.whl", hash = "sha256:212ac9b8bf1161dc91bd09c048048a95ca3a4c4f5e5d4a7d1b1a7d5752a7f96f", size = 79077, upload-time = "2024-11-01T14:07:03.893Z" },
-    { url = "https://files.pythonhosted.org/packages/2c/3b/b8964e04ae1a025c44ba8e4291f86e97fac443bca31de8bd98d3263d2fcf/watchdog-6.0.0-py3-none-manylinux2014_ppc64le.whl", hash = "sha256:e3df4cbb9a450c6d49318f6d14f4bbc80d763fa587ba46ec86f99f9e6876bb26", size = 79078, upload-time = "2024-11-01T14:07:05.189Z" },
-    { url = "https://files.pythonhosted.org/packages/62/ae/a696eb424bedff7407801c257d4b1afda455fe40821a2be430e173660e81/watchdog-6.0.0-py3-none-manylinux2014_s390x.whl", hash = "sha256:2cce7cfc2008eb51feb6aab51251fd79b85d9894e98ba847408f662b3395ca3c", size = 79077, upload-time = "2024-11-01T14:07:06.376Z" },
-    { url = "https://files.pythonhosted.org/packages/b5/e8/dbf020b4d98251a9860752a094d09a65e1b436ad181faf929983f697048f/watchdog-6.0.0-py3-none-manylinux2014_x86_64.whl", hash = "sha256:20ffe5b202af80ab4266dcd3e91aae72bf2da48c0d33bdb15c66658e685e94e2", size = 79078, upload-time = "2024-11-01T14:07:07.547Z" },
-    { url = "https://files.pythonhosted.org/packages/07/f6/d0e5b343768e8bcb4cda79f0f2f55051bf26177ecd5651f84c07567461cf/watchdog-6.0.0-py3-none-win32.whl", hash = "sha256:07df1fdd701c5d4c8e55ef6cf55b8f0120fe1aef7ef39a1c6fc6bc2e606d517a", size = 79065, upload-time = "2024-11-01T14:07:09.525Z" },
-    { url = "https://files.pythonhosted.org/packages/db/d9/c495884c6e548fce18a8f40568ff120bc3a4b7b99813081c8ac0c936fa64/watchdog-6.0.0-py3-none-win_amd64.whl", hash = "sha256:cbafb470cf848d93b5d013e2ecb245d4aa1c8fd0504e863ccefa32445359d680", size = 79070, upload-time = "2024-11-01T14:07:10.686Z" },
-    { url = "https://files.pythonhosted.org/packages/33/e8/e40370e6d74ddba47f002a32919d91310d6074130fe4e17dabcafc15cbf1/watchdog-6.0.0-py3-none-win_ia64.whl", hash = "sha256:a1914259fa9e1454315171103c6a30961236f508b9b623eae470268bbcc6a22f", size = 79067, upload-time = "2024-11-01T14:07:11.845Z" },
-]
-
-[[package]]
-name = "yarl"
-version = "1.24.5"
-source = { registry = "https://pypi.org/simple" }
-dependencies = [
-    { name = "idna" },
-    { name = "multidict" },
-    { name = "propcache" },
-]
-sdist = { url = "https://files.pythonhosted.org/packages/31/33/ebe9e3d1f86c7a0b51094c0a146392045ca1631d2664889539dec8088a33/yarl-1.24.5.tar.gz", hash = "sha256:e81b83143bee16329c23db3c1b2d82b29892fcbcb849186d2f6e98a5abe9a57f", size = 228679, upload-time = "2026-07-20T02:07:45.435Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/1b/84/71d051c850b5af41d168c679d9eb67eb7c55283ac4ee131673edf134bc4e/yarl-1.24.5-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:d693396e5aea78db03decd60aec9ece16c9b40ba00a587f089615ff4e718a81d", size = 136035, upload-time = "2026-07-20T02:05:25.489Z" },
-    { url = "https://files.pythonhosted.org/packages/03/4d/8ad27f9a1b7e69313cca5d695b925b48efe51208d3490e0844bae97cabc0/yarl-1.24.5-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:3363fcc96e665878946ad7a106b9a13eac0541766a690ef287c0232ac768b6ec", size = 97642, upload-time = "2026-07-20T02:05:27.429Z" },
-    { url = "https://files.pythonhosted.org/packages/ea/b4/05b4131c407006cd1e410e9c6539f16a0945724677e5364447313c15ea3e/yarl-1.24.5-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:9d399bdcfb4a0f659b9b3788bbc89babe63d9a6a65aacdf4d4e7065ff2e6316c", size = 97323, upload-time = "2026-07-20T02:05:29.441Z" },
-    { url = "https://files.pythonhosted.org/packages/20/16/e618c875c73e0e39611f20a581b3d5e8d59b8857bf001bee3263044c6deb/yarl-1.24.5-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:90333fd89b43c0d08ac85f3f1447593fc2c66de18c3d6378d7125ea118dc7a54", size = 107741, upload-time = "2026-07-20T02:05:31.367Z" },
-    { url = "https://files.pythonhosted.org/packages/d9/9a/c4defeaf3ed33fcb346aacf9c6e971a8d4e2bde04a0310e79abb208e7965/yarl-1.24.5-cp312-cp312-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:665b0a2c463cc9423dd647e0bfd9f4ccc9b50f768c55304d5e9f80b177c1de12", size = 103570, upload-time = "2026-07-20T02:05:33.303Z" },
-    { url = "https://files.pythonhosted.org/packages/5f/e7/0e0e0de5865ebd5914537ef486f36c727a59865c3ac0cf5ff1b32aececbf/yarl-1.24.5-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:e006d3a974c4ee19512e5f058abedb6eef36a5e553c14812bdeba1758d812e6d", size = 115815, upload-time = "2026-07-20T02:05:35.292Z" },
-    { url = "https://files.pythonhosted.org/packages/2b/27/ca56b700cb170aba25a3893b75355b213935657dc5714d2383354a270e62/yarl-1.24.5-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:e7d42c531243450ef0d4d9c172e7ed6ef052640f195629065041b5add4e058d1", size = 116025, upload-time = "2026-07-20T02:05:37.503Z" },
-    { url = "https://files.pythonhosted.org/packages/d6/d0/d56c859b8222116f5d68459199f48359e0bf121b6f65a69bf329b3602ba0/yarl-1.24.5-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:f08c7513ecef5aad65687bfdf6bc601ae9fccd04a42904501f8f7141abad9eb9", size = 109835, upload-time = "2026-07-20T02:05:39.506Z" },
-    { url = "https://files.pythonhosted.org/packages/70/a2/3a35557e4d1a79425040eba202ccaf08bdc8717680fc77e2498a1ad2e0a5/yarl-1.24.5-cp312-cp312-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:6c95b17fe34ed802f17e205112e6e10db92275c34fee290aa9bdc55a9c724027", size = 108884, upload-time = "2026-07-20T02:05:41.584Z" },
-    { url = "https://files.pythonhosted.org/packages/e4/35/ef4c26356b7913c68983bac2d72a4212b3347af551cb8d250b99b5ed7b7f/yarl-1.24.5-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:56b149b22de33b23b0c6077ab9518c6dcb538ad462e1830e68d06591ccf6e38b", size = 107308, upload-time = "2026-07-20T02:05:43.697Z" },
-    { url = "https://files.pythonhosted.org/packages/d5/91/ff0dc66c2ccf3e0153ab97ff61eabab4400e6a5264af427ab30cd69f1857/yarl-1.24.5-cp312-cp312-musllinux_1_2_armv7l.whl", hash = "sha256:a8fe66b8f300da93798025a785a5b90b42f3810dc2b72283ff84a41aaaebc293", size = 103646, upload-time = "2026-07-20T02:05:45.895Z" },
-    { url = "https://files.pythonhosted.org/packages/74/f0/33b9271c7f881766359d58266fa0811d2e5210ed860e28da7dc6d7786344/yarl-1.24.5-cp312-cp312-musllinux_1_2_ppc64le.whl", hash = "sha256:377fe3732edbaf78ee74efdf2c9f49f6e99f20e7f9d2649fda3eb4badd77d76e", size = 115305, upload-time = "2026-07-20T02:05:47.832Z" },
-    { url = "https://files.pythonhosted.org/packages/ef/65/fd79fb1868c4a80db8661091de525bf430f63c3bea1b20e8b6a84fc7d359/yarl-1.24.5-cp312-cp312-musllinux_1_2_riscv64.whl", hash = "sha256:e8ffa78582120024f476a611d7befc123cee59e47e8309d470cf667d806e613b", size = 108404, upload-time = "2026-07-20T02:05:49.604Z" },
-    { url = "https://files.pythonhosted.org/packages/ff/ba/dbabe6b262f17a816c70cfc09558dbf03ece3ec76684d02f911a3d3a189c/yarl-1.24.5-cp312-cp312-musllinux_1_2_s390x.whl", hash = "sha256:daba5e594f06114e37db186efd2dd916609071e59daca901a0a2e71f02b142ce", size = 115940, upload-time = "2026-07-20T02:05:51.741Z" },
-    { url = "https://files.pythonhosted.org/packages/a5/43/fab2d1dad9d340a268cdde63756a123d069723efff6a372d123fa74a9517/yarl-1.24.5-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:65be18ec59496c13908f02a2472751d9ef840b4f3fb5726f129306bf6a2a7bba", size = 110006, upload-time = "2026-07-20T02:05:53.554Z" },
-    { url = "https://files.pythonhosted.org/packages/c4/27/41eb51bbd1b8d89546b83897cfb0164f1e109304fd408dbb151b639eec0f/yarl-1.24.5-cp312-cp312-win_amd64.whl", hash = "sha256:a929d878fec099030c292803b31e5d5540a7b6a31e6a3cc76cb4685fc2a2f51b", size = 97618, upload-time = "2026-07-20T02:05:55.57Z" },
-    { url = "https://files.pythonhosted.org/packages/3c/25/b2553764b3d65db711d8f45416351ec4f420847558eb669edcbcaadf5780/yarl-1.24.5-cp312-cp312-win_arm64.whl", hash = "sha256:7ce27823052e2013b597e0c738b13e7e36b8ccb9400df8959417b052ab0fd92c", size = 93018, upload-time = "2026-07-20T02:05:57.554Z" },
-    { url = "https://files.pythonhosted.org/packages/e1/63/64ef361967cc983573149dc1515d531db5da8a4c92d22bb833d59e01b313/yarl-1.24.5-cp313-cp313-macosx_10_13_universal2.whl", hash = "sha256:79af890482fc94648e8cde4c68620378f7fef60932710fa17a66abc039244da2", size = 135075, upload-time = "2026-07-20T02:05:59.671Z" },
-    { url = "https://files.pythonhosted.org/packages/bb/89/55920fd853ce43e608adbc3962456f0d649d6bb15250dc2988321da0fe1c/yarl-1.24.5-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:46c2f213e23a04b93a392942d782eb9e413e6ef6bf7c8c53884e599a5c174dcb", size = 97225, upload-time = "2026-07-20T02:06:01.769Z" },
-    { url = "https://files.pythonhosted.org/packages/15/f0/7688d3f2cfff7590df2af38ec46d969f4281a4dddb08a9ad2eafbcdddf98/yarl-1.24.5-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:92ab3e11448f2ff7bf53c5a26eff0edc086898ec8b21fb154b85839ce1d88075", size = 96751, upload-time = "2026-07-20T02:06:03.676Z" },
-    { url = "https://files.pythonhosted.org/packages/05/1a/a851a0f94aaaf379dd4f901bfc80f634280bec51eb260b47363e2a4cd62e/yarl-1.24.5-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:ebb0ec7f17803063d5aeb982f3b1bd2b2f4e4fae6751226cbd6ba1fcfe9e63ff", size = 107960, upload-time = "2026-07-20T02:06:05.699Z" },
-    { url = "https://files.pythonhosted.org/packages/6c/a8/faea066c12f9c77ca0de90641f1655f9dd7b412477bf28c76d692f3aecff/yarl-1.24.5-cp313-cp313-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:82632daed195dcc8ea664e8556dc9bdbd671960fb3776bd92806ce05792c2448", size = 103500, upload-time = "2026-07-20T02:06:07.556Z" },
-    { url = "https://files.pythonhosted.org/packages/fb/9c/1e67084c2a6e2f2db0e3be798328cb3be42c0119b621d25461479a224d21/yarl-1.24.5-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:53e549287ef628fecba270045c9701b0c564563a9b0577d24a4ec75b8ab8040f", size = 115780, upload-time = "2026-07-20T02:06:09.599Z" },
-    { url = "https://files.pythonhosted.org/packages/58/86/1f94664e147474337e3359f52012cf3d02f825f694317b178bfba1078c62/yarl-1.24.5-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:fcd3b77e2f17bbe4ca56ec7bcb07992647d19d0b9c05d84886dcd6f9eb810afd", size = 115308, upload-time = "2026-07-20T02:06:11.352Z" },
-    { url = "https://files.pythonhosted.org/packages/0a/43/8e55ae7538ba5f28ccb3c845c6dd4549cf7016d5992e5326512519107cdd/yarl-1.24.5-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:d46b86567dd4e248c6c159fcbcdcce01e0a5c8a7cd2334a0fff759d0fa075b16", size = 110574, upload-time = "2026-07-20T02:06:13.129Z" },
-    { url = "https://files.pythonhosted.org/packages/ce/ba/a889ec8765cedcf2ac44dcb02d6a21e4861399b243b263c5f2dde27ee740/yarl-1.24.5-cp313-cp313-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:7f72c74aa99359e27a2ee8d6613fefa28b5f76a983c083074dfc2aaa4ab46213", size = 109914, upload-time = "2026-07-20T02:06:15.243Z" },
-    { url = "https://files.pythonhosted.org/packages/9c/c3/e45f821af67b791c2dbbe4a9f4137a1d33f8d386654a05a0c3f47bdfa25d/yarl-1.24.5-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:3f45789ce415a7ec0820dc4f82925f9b5f7732070be1dec1f5f23ec381435a24", size = 107712, upload-time = "2026-07-20T02:06:17.443Z" },
-    { url = "https://files.pythonhosted.org/packages/02/00/2ab0f42c9857fcb490bfaa6647b14540b53d241ab209f23220b958cc5832/yarl-1.24.5-cp313-cp313-musllinux_1_2_armv7l.whl", hash = "sha256:6e73e7fe93f17a7b191f52ec9da9dd8c06a8fe735a1ecbd13b97d1c723bff385", size = 104251, upload-time = "2026-07-20T02:06:19.259Z" },
-    { url = "https://files.pythonhosted.org/packages/7a/70/709d9a286e98af2c7fd8e4e6cada658b5c0e30d87dd7e2a63c2fb5767217/yarl-1.24.5-cp313-cp313-musllinux_1_2_ppc64le.whl", hash = "sha256:4a36f9becdd4c5c52a20c3e9484128b070b1dcfc8944c006f3a528295a359a9c", size = 115319, upload-time = "2026-07-20T02:06:21.207Z" },
-    { url = "https://files.pythonhosted.org/packages/5c/6c/3eaa515142991fe84cfc483ff986492211f1978f90161ccefdbec919d09b/yarl-1.24.5-cp313-cp313-musllinux_1_2_riscv64.whl", hash = "sha256:7bcbe0fcf850eae67b6b01749815a4f7161c560a844c769ad7b48fcd99f791c4", size = 109163, upload-time = "2026-07-20T02:06:23.006Z" },
-    { url = "https://files.pythonhosted.org/packages/bb/64/711dafce66c323a3144d470547a71c5384c57623308ac8bb5e4b903ac148/yarl-1.24.5-cp313-cp313-musllinux_1_2_s390x.whl", hash = "sha256:24e861e9630e0daddcb9191fb187f60f034e17a4426f8101279f0c475cd74144", size = 115435, upload-time = "2026-07-20T02:06:24.923Z" },
-    { url = "https://files.pythonhosted.org/packages/cf/f3/9b9d0e6d84bea851eb1ba99e4bdc755b86fd813e49ec86dfe42f26befdef/yarl-1.24.5-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:9335a099ad87287c37fe5d1a982ff392fa5efe5d14b40a730b1ec1d6a41382b4", size = 110691, upload-time = "2026-07-20T02:06:26.973Z" },
-    { url = "https://files.pythonhosted.org/packages/86/e4/62a06b7e87c4246ac76b7c2da136f972eb4a3a1fc94abb07e7022d6fdb0a/yarl-1.24.5-cp313-cp313-win_amd64.whl", hash = "sha256:2dbe06fc16bc91502bca713704022182e5729861ae00277c3a23354b40929740", size = 97454, upload-time = "2026-07-20T02:06:29.163Z" },
-    { url = "https://files.pythonhosted.org/packages/9e/c9/5fc8025b318ab10db413b61056bd0d95c557a70e8df4210c7511f866329c/yarl-1.24.5-cp313-cp313-win_arm64.whl", hash = "sha256:6b8536851f9f65e7f00c7a1d49ba7f2be0ffe2c11555367fc9f50d9f842410a1", size = 92813, upload-time = "2026-07-20T02:06:31.113Z" },
-    { url = "https://files.pythonhosted.org/packages/a9/08/5f3085fef9564217074db9dd8573de1795bc82cde61a7ad10b6a7234a569/yarl-1.24.5-cp314-cp314-macosx_10_15_universal2.whl", hash = "sha256:2729fcfc4f6a596fb0c50f32090400aa9367774ac296a00387e65098c0befa76", size = 135680, upload-time = "2026-07-20T02:06:33.273Z" },
-    { url = "https://files.pythonhosted.org/packages/98/35/ba9436e579bd48a8801f2021d842d9ab4994c26e4c7dd3a4c1f1bcb57a9e/yarl-1.24.5-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:ff330d3c30db4eb6b01d79e29d2d0b407a7ecad39cfd9ec993ece57396a2ec0d", size = 97395, upload-time = "2026-07-20T02:06:35.259Z" },
-    { url = "https://files.pythonhosted.org/packages/18/a9/a07f76f3c44e02b25cc743af5ef93eef27f7013eadca770451b6a6ccb5db/yarl-1.24.5-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:e42d75862735da90e7fc5a7b23db0c976f737113a54b3c9777a9b665e9cbff75", size = 97223, upload-time = "2026-07-20T02:06:37.216Z" },
-    { url = "https://files.pythonhosted.org/packages/77/f7/a9a1d6fa7dd9e388f95b30f6ad3ec4e285f6c8f61f44ce16070c3fcfe414/yarl-1.24.5-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:a3732e66413163e72508da9eff9ce9d2846fde51fae45d3605393d3e6cd303e9", size = 108777, upload-time = "2026-07-20T02:06:39.292Z" },
-    { url = "https://files.pythonhosted.org/packages/2f/44/e0b86c302471fabd6f02808ecf2ac52b8412b624787849d4bf2cdb466f6f/yarl-1.24.5-cp314-cp314-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:5b8ee53be440a0cffc991a27be3057e0530122548dbe7c0892df08822fce5ede", size = 103119, upload-time = "2026-07-20T02:06:41.456Z" },
-    { url = "https://files.pythonhosted.org/packages/d1/16/9c16d180bf8faaf223225eb50e1245870ff1ae0e302a27153988e65c51fd/yarl-1.24.5-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:af3aefa655adb5869491fa907e652290386800ae99cc50095cba71e2c6aefdca", size = 116471, upload-time = "2026-07-20T02:06:43.696Z" },
-    { url = "https://files.pythonhosted.org/packages/d2/8d/b219b9df28a02ce95cfbdd41d2f7caa5669d0ff979c1c9975697145e33c5/yarl-1.24.5-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:2120b96872df4a117cde97d270bac96aea7cc52205d305cf4611df694a487027", size = 115974, upload-time = "2026-07-20T02:06:45.874Z" },
-    { url = "https://files.pythonhosted.org/packages/9b/e8/f20557aca240d88e69850ad1ee91756821d094bb1310565c04d25c6682a2/yarl-1.24.5-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:66410eb6345d467151934b49bfa70fb32f5b35a6140baa40ad97d6436abea2e9", size = 110830, upload-time = "2026-07-20T02:06:47.852Z" },
-    { url = "https://files.pythonhosted.org/packages/db/18/199b85109a53eeca64ee19c9cca228287e8e4ab0cc1a09b28f530e65cce0/yarl-1.24.5-cp314-cp314-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:4af7b7e1be0a69bee8210735fe6dcfc38879adfac6d62e789d53ba432d1ffa41", size = 110054, upload-time = "2026-07-20T02:06:49.84Z" },
-    { url = "https://files.pythonhosted.org/packages/aa/2f/ed28147f8cd7f48c49367c90713b30a555284b6105a6a56f3a05568da795/yarl-1.24.5-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:fa139875ff98ab97da323cfadfaff08900d1ad42f1b5087b0b812a55c5a06373", size = 108312, upload-time = "2026-07-20T02:06:51.835Z" },
-    { url = "https://files.pythonhosted.org/packages/c5/c5/55e16ae0a5c227cea8df1c6871ba57d614a34243146c05729caf2a1bd9c5/yarl-1.24.5-cp314-cp314-musllinux_1_2_armv7l.whl", hash = "sha256:0055afc45e864b92729ac7600e2d102c17bef060647e74bca75fa84d66b9ff36", size = 103662, upload-time = "2026-07-20T02:06:54.061Z" },
-    { url = "https://files.pythonhosted.org/packages/8d/ea/dbd7c2caec459c9a426f18b02688ecbfb58620d0f6a3422d24769fbaf8ab/yarl-1.24.5-cp314-cp314-musllinux_1_2_ppc64le.whl", hash = "sha256:f0e466ed7511fe9d459a819edbc6c2585c0b6eabde9fa8a8947552468a7a6ef0", size = 116090, upload-time = "2026-07-20T02:06:56.015Z" },
-    { url = "https://files.pythonhosted.org/packages/06/84/39ce4ce3059e07fece5fbdbee8c4053406af9aca911ce9fa5f8548aab6af/yarl-1.24.5-cp314-cp314-musllinux_1_2_riscv64.whl", hash = "sha256:f141474e85b7e54998ec5180530a7cda99ab29e282fa50e0756d89981a9b43c5", size = 109523, upload-time = "2026-07-20T02:06:57.926Z" },
-    { url = "https://files.pythonhosted.org/packages/a9/8b/71ff44137b405c64a7788075669c24010019f57a7464b78c3a6cbee539d9/yarl-1.24.5-cp314-cp314-musllinux_1_2_s390x.whl", hash = "sha256:e2935f8c39e3b03e83519292d78f075189978f3f4adc15a78144c7c8e2a1cba5", size = 116084, upload-time = "2026-07-20T02:06:59.868Z" },
-    { url = "https://files.pythonhosted.org/packages/62/c0/423078fdd4042e1862c11f0ffd977a0ffa393783c12bee94685923bc189e/yarl-1.24.5-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:9d1216a7f6f77836617dba35687c5b78a4170afc3c3f18fc788f785ba26565c4", size = 111006, upload-time = "2026-07-20T02:07:01.907Z" },
-    { url = "https://files.pythonhosted.org/packages/cf/52/6daa2ee9d95e5c98b8128f8df91eb692eb423ab274b8cf08db52152fad26/yarl-1.24.5-cp314-cp314-win_amd64.whl", hash = "sha256:5ba4f78df2bcc19f764a4b26a8a4f5049c110090ad5825993aacb052bf8003ad", size = 99215, upload-time = "2026-07-20T02:07:03.852Z" },
-    { url = "https://files.pythonhosted.org/packages/ec/0e/464a847d7359e0da75dd9fc5c1d1aa35d0159ea31e5f8e66a3c1c29ff3d0/yarl-1.24.5-cp314-cp314-win_arm64.whl", hash = "sha256:9e4e16c73d717c5cf27626c524d0a2e261ad20e46932b2670f64ad5dde23e26f", size = 94566, upload-time = "2026-07-20T02:07:06.074Z" },
-    { url = "https://files.pythonhosted.org/packages/e2/55/e03acc4446772660bc335e86e41ef31e4d0d838fd641531a11a5ee33b493/yarl-1.24.5-cp314-cp314t-macosx_10_15_universal2.whl", hash = "sha256:e1ae548a9d901adca07899a4147a7c826bbcc06239d3ce9a59f57886a28a4c88", size = 142533, upload-time = "2026-07-20T02:07:08.284Z" },
-    { url = "https://files.pythonhosted.org/packages/ae/71/4acd3a1fc7cf14345cdb302665ecd2097f62c365b4f14ca17d4f37775cf9/yarl-1.24.5-cp314-cp314t-macosx_10_15_x86_64.whl", hash = "sha256:ff405d91509d88e8d44129cd87b18d70acd1f0c1aeabd7bc3c46792b1fe2acba", size = 100776, upload-time = "2026-07-20T02:07:10.197Z" },
-    { url = "https://files.pythonhosted.org/packages/ff/0b/cfb76b7fe99686db264bff829779a539d923e7564ffd7ef18da6c54c3774/yarl-1.24.5-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:47e98aab9d8d82ff682e7b0b5dded33bf138a32b817fcf7fa3b27b2d7c412928", size = 100913, upload-time = "2026-07-20T02:07:12.357Z" },
-    { url = "https://files.pythonhosted.org/packages/8b/3f/7116e782992abbd4fb6948488aec72078895e929a23078290739e8396fce/yarl-1.24.5-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:f0a658a6d3fafee5c6f63c58f3e785c8c43c93fbc02bf9f2b6663f8185e0971f", size = 106507, upload-time = "2026-07-20T02:07:14.173Z" },
-    { url = "https://files.pythonhosted.org/packages/33/90/d4d2d73ee78229cc889872eb8e085d8f5c6f51abdb178409fd9b23cf74fd/yarl-1.24.5-cp314-cp314t-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:4377407001ca3c057773f44d8ddd6358fa5f691407c1ba92210bd3cf8d9e4c95", size = 99219, upload-time = "2026-07-20T02:07:16.019Z" },
-    { url = "https://files.pythonhosted.org/packages/3e/fa/a6df1a9bccd644eec00abee0dff4277416222cec435330fd1f2858523ec1/yarl-1.24.5-cp314-cp314t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:7c0494a31a1ac5461a226e7947a9c9b78c44e1dc7185164fa7e9651557a5d9bc", size = 111804, upload-time = "2026-07-20T02:07:18.141Z" },
-    { url = "https://files.pythonhosted.org/packages/8a/9e/7b2a1f4bcc20e9447156dd2b1c4d01f70d9df0759025ee7d09a84ffae134/yarl-1.24.5-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:a7cff474ab7cd149765bb784cf6d78b32e18e20473fb7bda860bce98ab58e9da", size = 110943, upload-time = "2026-07-20T02:07:20.06Z" },
-    { url = "https://files.pythonhosted.org/packages/08/ff/22c92affb0f9b623ca753d27d968b5625b868f12c6378d049d55ae247643/yarl-1.24.5-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:cbb833ccacdb5519eff9b8b71ee618cc2801c878e77e288775d77c3a2ced858a", size = 108251, upload-time = "2026-07-20T02:07:22.217Z" },
-    { url = "https://files.pythonhosted.org/packages/45/44/5769b96298c1e195fb412997b6090af2a84105cf59c17613558a2d011d1f/yarl-1.24.5-cp314-cp314t-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:82f75e05912e84b7a0fe57075d9c59de3cb352b928330f2eb69b2e1f54c3e1f0", size = 106025, upload-time = "2026-07-20T02:07:24.083Z" },
-    { url = "https://files.pythonhosted.org/packages/4c/40/009e8e791fd9762c0e1567e69248acb4f49064597e1680874c16dd8bb798/yarl-1.24.5-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:16a2f5010280020e90f5330257e6944bc33e73593b136cc5a241e6c1dc292498", size = 106573, upload-time = "2026-07-20T02:07:26.248Z" },
-    { url = "https://files.pythonhosted.org/packages/20/c6/b7480578f8a0a80946f36ad6df547ecec704f9ba69d2de60f8aa6f1c1cbf/yarl-1.24.5-cp314-cp314t-musllinux_1_2_armv7l.whl", hash = "sha256:ffcd54362564dc1a30fb74d8b8a6e5a6b11ebd5e27266adc3b7427a21a6c9104", size = 100751, upload-time = "2026-07-20T02:07:28.098Z" },
-    { url = "https://files.pythonhosted.org/packages/d4/27/4476f3360b91a48c5cf125e91f59a3bd35299d84a431a258d57f5977bb11/yarl-1.24.5-cp314-cp314t-musllinux_1_2_ppc64le.whl", hash = "sha256:0465ec8cedc2349b97a6b595ace64084a50c6e839eca40aa0626f38b8350e331", size = 111643, upload-time = "2026-07-20T02:07:30.88Z" },
-    { url = "https://files.pythonhosted.org/packages/4c/4b/5cdd3e5ee944e8af31e52f6cd3d3af5fd7b937e036ccbbba2c9ffebede95/yarl-1.24.5-cp314-cp314t-musllinux_1_2_riscv64.whl", hash = "sha256:4db9aecb141cb7a5447171b57aa1ed3a8fee06af40b992ffc31206c0b0121550", size = 106312, upload-time = "2026-07-20T02:07:33.06Z" },
-    { url = "https://files.pythonhosted.org/packages/18/86/f406b0c2a6f99575de2da671ef47aa06f89a5be83a27a46971c3b86cecdb/yarl-1.24.5-cp314-cp314t-musllinux_1_2_s390x.whl", hash = "sha256:f540c013589084679a6c7fac07096b10159737918174f5dfc5e11bf5bca4dfe6", size = 110379, upload-time = "2026-07-20T02:07:35.155Z" },
-    { url = "https://files.pythonhosted.org/packages/f0/6c/9f3adfbd3b30b4fa0f7ccb3a83eba2c1152d3fff554d535e640ba0f7ba2b/yarl-1.24.5-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:a61834fb15d81322d872eaafd333838ae7c9cea84067f232656f75965933d047", size = 108497, upload-time = "2026-07-20T02:07:37.35Z" },
-    { url = "https://files.pythonhosted.org/packages/dd/37/91eb2e5ca883a529c1b390348a74cd9fc0512171727f547ce70bfe02be5c/yarl-1.24.5-cp314-cp314t-win_amd64.whl", hash = "sha256:5c88e5815a49d289e599f3513aa7fde0bc2092ff188f99c940f007f90f53d104", size = 102450, upload-time = "2026-07-20T02:07:39.578Z" },
-    { url = "https://files.pythonhosted.org/packages/bf/f4/ed5c402ac8fde4403ed3366c2716bfddc8a6677ebd59f3d62772cc7fe468/yarl-1.24.5-cp314-cp314t-win_arm64.whl", hash = "sha256:cf139c02f5f23ef6532040a30ff662c00a318c952334f211046b8e60b7f17688", size = 97222, upload-time = "2026-07-20T02:07:41.55Z" },
-    { url = "https://files.pythonhosted.org/packages/61/02/962c1cbfc401a30c1d034dc67ff395f64b52302c6d62de556c1fca99acc0/yarl-1.24.5-py3-none-any.whl", hash = "sha256:a33700d13d9b7d84fd10947b09ff69fb9a792e519c8cb9764a3ca70baa6c23a7", size = 58612, upload-time = "2026-07-20T02:07:43.461Z" },
-]
-
-[[package]]
-name = "zipp"
-version = "4.1.0"
-source = { registry = "https://pypi.org/simple" }
-sdist = { url = "https://files.pythonhosted.org/packages/b9/d8/eab98a517c14134c0b2eb4e2387bc5f457334293ec5d2dd3857ec2966802/zipp-4.1.0.tar.gz", hash = "sha256:4cb57381f544315db7688e976e922a2b18cdb513d21cc194eb42232ba2a3e602", size = 26214, upload-time = "2026-05-18T20:08:57.967Z" }
-wheels = [
-    { url = "https://files.pythonhosted.org/packages/3a/13/547360d81e6d88d58492968ffda9f9542854f11310ee556fef14260cc886/zipp-4.1.0-py3-none-any.whl", hash = "sha256:25ad4e16390cd314347dd8f1de67a2ac538ae658ed4ab9db16029c07c188e97f", size = 10238, upload-time = "2026-05-18T20:08:57.045Z" },
-]
diff --git a/loop-engine/verifier.py b/loop-engine/verifier.py
deleted file mode 100644
index 712fec2..0000000
--- a/loop-engine/verifier.py
+++ /dev/null
@@ -1,460 +0,0 @@
-"""
-Polyglot Verification & Multi-Toolchain Test Runner.
-
-Deterministic lint/build/test execution per StackProfile.toolchain.
-Invoked from daemon._execute_and_qa immediately after diff verification,
-before LLM QA, to fail-fast on broken builds without wasting tokens.
-"""
-
-import asyncio
-import time
-from dataclasses import dataclass, field
-from pathlib import Path
-
-from sentinel import TypeDriftSentinel
-from blast_radius import (
-    calculate_affected_paths,
-    extract_modified_paths,
-    find_owning_package,
-)
-
-try:
-    from models import BlastRadiusConfig
-except Exception:
-    BlastRadiusConfig = None  # type: ignore
-
-
-@dataclass
-class CommandResult:
-    command: str
-    cmd_type: str
-    passed: bool
-    skipped: bool = False
-    returncode: int | None = None
-    stdout: str = ""
-    stderr: str = ""
-    duration_seconds: float = 0.0
-
-
-@dataclass
-class ToolchainResult:
-    passed: bool
-    commands: list[CommandResult] = field(default_factory=list)
-    summary: str = ""
-    report_md: str = ""
-
-
-class ToolchainRunner:
-    """Deterministic toolchain executor for StackProfile.toolchain.
-
-    Executes lint → build → test sequentially via shell, with per-command
-    timeout and evidence persistence. Mirrors PreflightRunner's subprocess
-    pattern but validates functional correctness, not just presence.
-    """
-
-    def __init__(
-        self,
-        timeout_per_command: float = 120.0,
-        evidence_base_dir: str | Path = "loop-engine/evidence",
-        workspace_root: str | Path | None = None,
-        skip_unaffected: bool = True,
-        blast_radius_config: "BlastRadiusConfig | None" = None,
-    ):
-        self.timeout_per_command = timeout_per_command
-        self.evidence_base_dir = Path(evidence_base_dir)
-        # Blast-radius scoping (LE-9 / Task 141): workspace_root defaults to
-        # the repo root (parent of loop-engine/). skip_unaffected is the
-        # legacy rollback flag — set False to always run full toolchain verification.
-        # blast_radius_config is the spec-compliant config (enabled, workspace_globs, conservative_root_fallback).
-        self.workspace_root = (
-            Path(workspace_root)
-            if workspace_root is not None
-            else Path(__file__).resolve().parent.parent
-        )
-        self.skip_unaffected = skip_unaffected
-        if blast_radius_config is not None:
-            self.blast_radius_config = blast_radius_config
-        elif BlastRadiusConfig is not None:
-            # Default config when not provided — enabled with standard globs
-            try:
-                self.blast_radius_config = BlastRadiusConfig()
-            except Exception:
-                self.blast_radius_config = None
-        else:
-            self.blast_radius_config = None
-        # Sync legacy flag with spec config for backward compat
-        if self.blast_radius_config is not None and not self.skip_unaffected:
-            # Legacy flag disables spec config as well (rollback)
-            try:
-                self.blast_radius_config.enabled = False
-            except Exception:
-                pass
-
-    async def run(
-        self,
-        profile,  # StackProfile
-        task_id: int | None = None,
-        cwd: str | Path | None = None,
-        diff_text: str = "",
-    ) -> ToolchainResult:
-        """Run toolchain commands sequentially.
-
-        Order: Type Drift Sentinel (LE-7) -> lint, build, test. Null/whitespace
-        commands are skipped as passed+skipped. Non-zero exit or timeout →
-        passed=False.
-        """
-        # --- Type Drift Sentinel (LE-7) — fail-fast before any toolchain command ---
-        # A hand-authored duplicate DTO/interface/model in a consumer path is a
-        # hard violation: the toolchain fails immediately and the actionable
-        # report is recorded as stderr so it reaches QA feedback, preventing
-        # broken duplicate types from reaching LLM QA.
-        if diff_text and str(diff_text).strip():
-            try:
-                sentinel_result = TypeDriftSentinel().check_diff(str(diff_text))
-                if not sentinel_result.passed:
-                    sentinel_cmd = CommandResult(
-                        command="type-drift-sentinel",
-                        cmd_type="lint",
-                        passed=False,
-                        skipped=False,
-                        returncode=None,
-                        stdout="",
-                        stderr=sentinel_result.report_md,
-                    )
-                    return self._finalize([sentinel_cmd], task_id)
-            except Exception as e:
-                # Sentinel infra error must not block the toolchain (mirrors the
-                # daemon's toolchain-infra-error tolerance). Log to the result.
-                print(f"[verifier] Type Drift Sentinel error (proceeding): {e}")
-
-        # --- Blast-Radius Global Scoping (LE-9 / Task 141 — Spec) ---
-        # Spec path: if monorepo and 0 packages affected, skip entire toolchain.
-        if diff_text and str(diff_text).strip():
-            try:
-                cfg = getattr(self, "blast_radius_config", None)
-                if cfg is not None and getattr(cfg, "enabled", False):
-                    modified_paths = extract_modified_paths(str(diff_text))
-                    # cwd or REPO_ROOT per spec; use workspace_root as repo root fallback
-                    effective_root = Path(cwd) if cwd is not None else self.workspace_root
-                    # If cwd is a file path inside workspace, use its parent? Use workspace_root for matrix
-                    # Spec says: calculate_affected_paths(modified_paths, cwd or REPO_ROOT, config)
-                    matrix = calculate_affected_paths(modified_paths, self.workspace_root, cfg)
-                    if getattr(matrix, "is_monorepo", False) and getattr(matrix, "is_empty", False):
-                        note = "Blast-Radius: 0 packages affected"
-                        skipped_commands: list[CommandResult] = [
-                            CommandResult(command="none", cmd_type=t, passed=True, skipped=True)
-                            for t in ("lint", "build", "test")
-                        ]
-                        # Append note to report_md via _finalize
-                        return ToolchainResult(
-                            passed=True,
-                            commands=skipped_commands,
-                            summary="Toolchain PASSED (Blast-Radius: 0 packages affected)",
-                            report_md=f"# Toolchain Verification Report\n\nToolchain PASSED (Blast-Radius: 0 packages affected)\n\n**Blast-radius scoping:** {note}\n",
-                        )
-            except Exception as e:
-                print(f"[verifier] Blast-radius global scoping error (proceeding): {e}")
-
-        # --- Blast-Radius Workspace Scoping (LE-9 / Task 141 — Legacy per-workspace) ---
-        # When the task diff touches only a subset of monorepo workspaces, a
-        # completely unaffected workspace skips its lint/build/test (all
-        # commands reported SKIPPED, result passes). The analyzer is
-        # deliberately conservative: it only skips when it can PROVE the
-        # verified workspace is unaffected, so affected modules are never
-        # silently missed (Task 141 Risk & Rollback).
-        if self.skip_unaffected and diff_text and str(diff_text).strip():
-            blast_note = self._blast_radius_note(diff_text, cwd)
-            if blast_note:
-                skipped_commands: list[CommandResult] = [
-                    CommandResult(command="none", cmd_type=t, passed=True, skipped=True)
-                    for t in ("lint", "build", "test")
-                ]
-                return self._finalize(
-                    skipped_commands, task_id, blast_radius_note=blast_note
-                )
-
-        # Defensive: profile may lack toolchain attr in mocks
-        toolchain = getattr(profile, "toolchain", None)
-        if toolchain is None:
-            # Treat as generic no-op
-            commands: list[CommandResult] = [
-                CommandResult(command="none", cmd_type=t, passed=True, skipped=True)
-                for t in ("lint", "build", "test")
-            ]
-            return self._finalize(commands, task_id)
-
-        # Sequential order: lint, build, test per spec
-        ordered = [
-            ("lint", getattr(toolchain, "lint_cmd", None)),
-            ("build", getattr(toolchain, "build_cmd", None)),
-            ("test", getattr(toolchain, "test_cmd", None)),
-        ]
-
-        results: list[CommandResult] = []
-        cwd_path = Path(cwd) if cwd is not None else None
-
-        for cmd_type, cmd in ordered:
-            # Null or whitespace-only → skipped
-            if cmd is None or (isinstance(cmd, str) and not cmd.strip()):
-                results.append(
-                    CommandResult(
-                        command="none",
-                        cmd_type=cmd_type,
-                        passed=True,
-                        skipped=True,
-                    )
-                )
-                continue
-
-            cmd_str = str(cmd)
-            start = time.monotonic()
-            try:
-                proc = await asyncio.create_subprocess_shell(
-                    cmd_str,
-                    stdout=asyncio.subprocess.PIPE,
-                    stderr=asyncio.subprocess.PIPE,
-                    cwd=str(cwd_path) if cwd_path else None,
-                )
-                try:
-                    stdout_bytes, stderr_bytes = await asyncio.wait_for(
-                        proc.communicate(), timeout=self.timeout_per_command
-                    )
-                except asyncio.TimeoutError:
-                    try:
-                        proc.kill()
-                    except ProcessLookupError:
-                        pass
-                    duration = time.monotonic() - start
-                    # Drain? proc already killed, attempt wait with timeout
-                    try:
-                        await asyncio.wait_for(proc.wait(), timeout=2.0)
-                    except Exception:
-                        pass
-                    results.append(
-                        CommandResult(
-                            command=cmd_str,
-                            cmd_type=cmd_type,
-                            passed=False,
-                            skipped=False,
-                            returncode=None,
-                            stdout="",
-                            stderr=f"Toolchain timeout ({self.timeout_per_command}s): {cmd_str}",
-                            duration_seconds=duration,
-                        )
-                    )
-                    continue
-
-                duration = time.monotonic() - start
-                stdout = stdout_bytes.decode(errors="replace").strip()
-                stderr = stderr_bytes.decode(errors="replace").strip()
-                passed = proc.returncode == 0
-                results.append(
-                    CommandResult(
-                        command=cmd_str,
-                        cmd_type=cmd_type,
-                        passed=passed,
-                        skipped=False,
-                        returncode=proc.returncode,
-                        stdout=stdout,
-                        stderr=stderr,
-                        duration_seconds=duration,
-                    )
-                )
-
-            except FileNotFoundError as e:
-                duration = time.monotonic() - start
-                results.append(
-                    CommandResult(
-                        command=cmd_str,
-                        cmd_type=cmd_type,
-                        passed=False,
-                        skipped=False,
-                        returncode=None,
-                        stdout="",
-                        stderr=f"Toolchain spawn failed: {cmd_str} → {e}",
-                        duration_seconds=duration,
-                    )
-                )
-            except Exception as e:
-                duration = time.monotonic() - start
-                results.append(
-                    CommandResult(
-                        command=cmd_str,
-                        cmd_type=cmd_type,
-                        passed=False,
-                        skipped=False,
-                        returncode=None,
-                        stdout="",
-                        stderr=f"Toolchain error: {cmd_str} → {e}",
-                        duration_seconds=duration,
-                    )
-                )
-
-        return self._finalize(results, task_id)
-
-    def _finalize(
-        self,
-        commands: list[CommandResult],
-        task_id: int | None,
-        blast_radius_note: str = "",
-    ) -> ToolchainResult:
-        passed = all(c.passed for c in commands)
-        # Summary: single line
-        summary_parts = []
-        for c in commands:
-            if c.skipped:
-                summary_parts.append(f"{c.cmd_type}: SKIPPED")
-            elif c.passed:
-                summary_parts.append(f"{c.cmd_type}: PASSED")
-            else:
-                summary_parts.append(f"{c.cmd_type}: FAILED")
-        summary = "Toolchain " + ("PASSED" if passed else "FAILED") + " | " + ", ".join(summary_parts)
-        if blast_radius_note:
-            summary += f" | {blast_radius_note}"
-
-        # Markdown report with summary table and error logs
-        report_md = self._build_report_md(commands, passed, summary, blast_radius_note)
-
-        result = ToolchainResult(
-            passed=passed, commands=commands, summary=summary, report_md=report_md
-        )
-
-        # Evidence persistence if task_id provided
-        if task_id is not None:
-            try:
-                # Only write if base dir's parent exists? spec says if evidence_base_dir exists: save
-                # We ensure mkdir for base + task subdir
-                evidence_path = self.evidence_base_dir / str(task_id)
-                evidence_path.mkdir(parents=True, exist_ok=True)
-                (evidence_path / "toolchain_report.md").write_text(report_md, encoding="utf-8")
-                (evidence_path / "toolchain_result.txt").write_text(
-                    "PASSED" if passed else "FAILED", encoding="utf-8"
-                )
-            except Exception:
-                # Evidence write failure should not fail the toolchain result itself
-                pass
-
-        return result
-
-    def _build_report_md(
-        self,
-        commands: list[CommandResult],
-        passed: bool,
-        summary: str,
-        blast_radius_note: str = "",
-    ) -> str:
-        lines: list[str] = []
-        lines.append("# Toolchain Verification Report")
-        lines.append("")
-        lines.append(summary)
-        lines.append("")
-        if blast_radius_note:
-            lines.append(f"**Blast-radius scoping:** {blast_radius_note}")
-            lines.append("")
-        lines.append(f"**Overall:** {'PASSED' if passed else 'FAILED'}")
-        lines.append("")
-        lines.append("| Type | Command | Result | Duration | Return Code |")
-        lines.append("|---|---|---|---|---|")
-        for c in commands:
-            if c.skipped:
-                result_str = "SKIPPED"
-                cmd_display = "none"
-                rc = "-"
-                dur = "-"
-            else:
-                result_str = "PASSED" if c.passed else "FAILED"
-                # Escape pipe in command for markdown table
-                cmd_display = c.command.replace("|", "\\|")
-                rc = str(c.returncode) if c.returncode is not None else "timeout"
-                dur = f"{c.duration_seconds:.2f}s"
-            lines.append(f"| {c.cmd_type} | `{cmd_display}` | {result_str} | {dur} | {rc} |")
-        lines.append("")
-        # Error logs for failing commands
-        failing = [c for c in commands if not c.passed and not c.skipped]
-        if failing:
-            lines.append("## Failures")
-            lines.append("")
-            for c in failing:
-                lines.append(f"### {c.cmd_type}: `{c.command}`")
-                lines.append("")
-                if c.stderr:
-                    lines.append("**stderr:**")
-                    lines.append("```")
-                    lines.append(c.stderr[:2000])
-                    lines.append("```")
-                if c.stdout:
-                    lines.append("**stdout:**")
-                    lines.append("```")
-                    lines.append(c.stdout[:2000])
-                    lines.append("```")
-                lines.append("")
-        else:
-            if passed and any(not c.skipped for c in commands):
-                lines.append("All toolchain commands passed.")
-                lines.append("")
-        return "\n".join(lines)
-
-    def is_workspace_affected(
-        self, diff_text: str, cwd: str | Path | None = None
-    ) -> bool:
-        """True when verification must run for the workspace at ``cwd``.
-
-        Returns False only when blast-radius analysis PROVES the workspace
-        (a discovered monorepo package, or the root package) is completely
-        unaffected by the diff. Conservative bias: any uncertainty — no cwd,
-        a non-monorepo layout, root-owned files, or a cwd outside the
-        package graph — returns True so the toolchain always runs.
-        """
-        return self._blast_radius_note(diff_text, cwd) == ""
-
-    def _blast_radius_note(self, diff_text: str, cwd: str | Path | None) -> str:
-        """Return a skip note when ``cwd`` is provably unaffected, else "".
-
-        The empty string means "run verification". A non-empty note is a
-        human-readable explanation appended to the summary/report so skipped
-        workspaces are observable in QA evidence.
-        """
-        if not cwd:
-            return ""
-        try:
-            cwd_path = Path(cwd).resolve()
-        except OSError:
-            return ""
-        try:
-            root = Path(self.workspace_root).resolve()
-        except OSError:
-            return ""
-        modified = extract_modified_paths(str(diff_text))
-        if not modified:
-            return ""
-        try:
-            matrix = calculate_affected_paths(modified, root)
-        except OSError:
-            return ""  # analyzer failure must never skip
-        if not matrix.packages:
-            return ""  # not a proven monorepo → conservative full verification
-        if matrix.root_owned_files:
-            return ""  # change outside the package graph → conservative
-        try:
-            cwd_rel = cwd_path.relative_to(root).as_posix()
-        except ValueError:
-            return ""  # cwd outside the workspace root → cannot scope
-        owner = find_owning_package(cwd_rel, matrix.packages)
-        if owner is None:
-            return ""  # cwd not inside any discovered package → conservative
-        if owner.name in matrix.affected_packages:
-            return ""
-        return (
-            f"Blast-radius scoping: workspace `{owner.name}` ({owner.path}) "
-            f"is unaffected by this diff — skipping unrelated toolchain verification"
-        )
-
-    def run_sync(
-        self,
-        profile,
-        task_id: int | None = None,
-        cwd: str | Path | None = None,
-        diff_text: str = "",
-    ) -> ToolchainResult:
-        """Synchronous wrapper for tests and sync callers."""
-        return asyncio.run(self.run(profile, task_id=task_id, cwd=cwd, diff_text=diff_text))
diff --git a/loop-engine/watcher.py b/loop-engine/watcher.py
deleted file mode 100644
index b4cee53..0000000
--- a/loop-engine/watcher.py
+++ /dev/null
@@ -1,146 +0,0 @@
-"""
-Kanban Watcher — detects new task files in tasks/backlog/.
-
-Uses Python watchdog filesystem observer.
-Read-only: never modifies task files.
-Triggers the pipeline by registering the task in StateMachine.
-
-Respects trigger_mode from LoopEngineConfig:
-- "auto": legacy behavior — immediately invokes on_task_detected (starts processing).
-- "telegram_button" / "command_only": registers as PENDING_TRIGGER, sends trigger card.
-"""
-
-import re
-import time
-from pathlib import Path
-from typing import Callable, Optional
-
-from watchdog.observers import Observer
-from watchdog.events import FileSystemEventHandler, FileCreatedEvent
-
-from models import TaskState, LoopEngineConfig
-from state import StateMachine
-
-
-def _parse_task_metadata(file_path: str) -> Optional[dict]:
-    """Extract task ID, title, source, type, status from a task file."""
-    path = Path(file_path)
-    if not path.suffix == ".md":
-        return None
-
-    content = path.read_text(encoding="utf-8")
-
-    # Extract task ID from filename: 01-feature-name.md → 01
-    match = re.match(r'^(\d+)-', path.stem)
-    if not match:
-        return None
-    task_id = int(match.group(1))
-
-    # Extract metadata headers
-    metadata = {"task_id": task_id, "file": str(path)}
-
-    for field in ["Source", "Type", "Status"]:
-        m = re.search(rf'\*\*{field}:\*\*\s*(.+)', content)
-        if m:
-            metadata[field.lower()] = m.group(1).strip()
-
-    return metadata
-
-
-class BacklogHandler(FileSystemEventHandler):
-    """Watches for new .md files in tasks/backlog/."""
-
-    def __init__(self, state: StateMachine, config: LoopEngineConfig,
-                 gateway=None, on_task_detected: Optional[Callable] = None):
-        self.state = state
-        self.config = config
-        self.gateway = gateway
-        self.on_task_detected = on_task_detected
-
-    def on_created(self, event):
-        if event.is_directory:
-            return
-
-        file_path = event.src_path
-
-        # Only watch .md files in tasks/backlog/
-        if not file_path.endswith(".md"):
-            return
-        if "tasks/backlog/" not in file_path:
-            return
-
-        # Ignore archive, loop-engine, .git
-        for ignore in ["archive", "loop-engine", ".git"]:
-            if ignore in file_path:
-                return
-
-        # Parse metadata
-        meta = _parse_task_metadata(file_path)
-        if not meta:
-            return
-
-        # Register in state machine
-        task_record = self.state.get_task_by_file(file_path)
-        if not task_record:
-            initial_state = (TaskState.BACKLOG if self.config.trigger_mode == "auto"
-                             else TaskState.PENDING_TRIGGER)
-            task_id = self.state.register_task(file_path, initial_state)
-            print(f"[watcher] New task detected ({initial_state.value}): "
-                  f"{file_path} (ID: {task_id})")
-
-            # Always dispatch via callback — the daemon handles async scheduling
-            # on the main event loop. Never call asyncio from this background thread.
-            if self.on_task_detected:
-                self.on_task_detected(task_id, file_path)
-
-
-class KanbanWatcher:
-    """Filesystem observer for tasks/backlog/."""
-
-    def __init__(self, state: StateMachine, config: LoopEngineConfig,
-                 gateway=None, tasks_dir: str = "tasks",
-                 on_task_detected: Optional[Callable] = None):
-        self.state = state
-        self.config = config
-        self.gateway = gateway
-        self.tasks_dir = Path(tasks_dir)
-        self.backlog_dir = self.tasks_dir / "backlog"
-        self.observer = Observer()
-        self.handler = BacklogHandler(state, config, gateway, on_task_detected)
-
-    def start(self):
-        """Start watching tasks/backlog/ for new files."""
-        self.backlog_dir.mkdir(parents=True, exist_ok=True)
-        self.observer.schedule(self.handler, str(self.backlog_dir), recursive=False)
-        self.observer.start()
-        print(f"[watcher] Watching {self.backlog_dir} for new tasks "
-              f"(trigger_mode={self.config.trigger_mode})...")
-
-    def stop(self):
-        self.observer.stop()
-        self.observer.join()
-
-    def scan_existing(self) -> list[dict]:
-        """Scan tasks/backlog/ for existing unregistered tasks.
-
-        Respects trigger_mode: auto → BACKLOG, else → PENDING_TRIGGER.
-        """
-        detected = []
-        if not self.backlog_dir.exists():
-            return detected
-
-        for md_file in sorted(self.backlog_dir.glob("*.md")):
-            meta = _parse_task_metadata(str(md_file))
-            if not meta:
-                continue
-
-            task_record = self.state.get_task_by_file(str(md_file))
-            if not task_record:
-                if self.config.trigger_mode == "auto":
-                    task_id = self.state.register_task(str(md_file), TaskState.BACKLOG)
-                else:
-                    task_id = self.state.register_task(str(md_file), TaskState.PENDING_TRIGGER)
-                detected.append({"task_id": task_id, "file": str(md_file)})
-                print(f"[watcher] Existing task registered: {md_file.name} (ID: {task_id})")
-
-        return detected
diff --git a/mcp-persona-server/dual_dispatch.py b/mcp-persona-server/dual_dispatch.py
new file mode 100644
index 0000000..078a5b1
--- /dev/null
+++ b/mcp-persona-server/dual_dispatch.py
@@ -0,0 +1,111 @@
+"""Dual-dispatch helpers for the persona MCP engine (Task 167).
+
+This module classifies raw persona-LLM output into two lanes:
+
+1. **XML lane** — the model emitted a structured ``<hands_*_task>`` (or
+   ``<failure_report>``) block. The block is isolated verbatim and handed
+   back to the caller as machine-readable instructions.
+2. **Question lane** — the model produced no XML but is asking for missing
+   context or clarification. The caller must relay the question instead of
+   treating the text as an actionable report.
+
+Anything that is neither XML nor a question is treated as a free-form
+evaluation report (``REPORT`` status at the server layer).
+
+Pure standard library — no third-party imports — so this module is trivially
+unit-testable without network access or LLM credentials.
+"""
+
+from __future__ import annotations
+
+import re
+from typing import Optional
+
+# Matches one structured control block, e.g. <hands_implementation_task> ...
+# </hands_implementation_task> or <failure_report> ... </failure_report>.
+# The back-reference (\\1) guarantees the closing tag matches the opening tag.
+# DOTALL lets a single block span multiple lines.
+XML_BLOCK_RE = re.compile(
+    r"<(hands_[a-z_]+_task|failure_report)\b[^>]*>([\s\S]*?)</\1>",
+    re.DOTALL,
+)
+
+# Heuristics for "the model is asking something / needs input".
+# Applied to text AFTER all XML blocks have been stripped out.
+QUESTION_RE = re.compile(
+    r"\b(what|which|who|whom|whose|when|where|why|how\b.*\?|clarif\w*|"
+    r"missing|need(?:ed|s)?|require[sd]?|awaiting|blocked on|unclear|"
+    r"please\s+(provide|specify|confirm|clarify|share|send|explain))\b",
+    re.IGNORECASE,
+)
+
+
+def extract_xml(text: str) -> tuple[bool, Optional[str], str]:
+    """Detect and isolate the outermost XML control block in ``text``.
+
+    Args:
+        text: Raw persona-LLM output, possibly with conversational preamble
+            and/or trailing commentary around the structured block.
+
+    Returns:
+        A ``(has_xml, xml_content, clean_text)`` triple where:
+        - ``has_xml`` is True when a well-formed block was found.
+        - ``xml_content`` is the full matched block (opening tag through
+          closing tag) verbatim, or None when absent/malformed.
+        - ``clean_text`` is the input with the extracted block removed and
+          surrounding whitespace stripped (the human-readable remainder).
+
+    Notes:
+        - Malformed XML (opening tag with no matching close) is NOT treated
+          as XML: ``has_xml`` is False and the text is returned unchanged so
+          the caller can fall through to question/report classification.
+        - Only the FIRST (outermost) block is extracted; any additional
+          blocks stay in ``clean_text`` for downstream handling.
+    """
+    if not text:
+        return False, None, ""
+    match = XML_BLOCK_RE.search(text)
+    if match is None:
+        # No well-formed block: opening tag without a matching close tag
+        # (or no tags at all) falls through here unchanged.
+        return False, None, text.strip()
+    xml_content = match.group(0)
+    # Remove just the extracted block; keep preamble + trailing commentary.
+    clean_text = (text[: match.start()] + text[match.end() :]).strip()
+    return True, xml_content, clean_text
+
+
+def strip_all_xml(text: str) -> str:
+    """Remove every well-formed XML control block from ``text``.
+
+    Helper for question detection: classification must run on the
+    human-readable remainder, never on structured tag contents.
+    """
+    if not text:
+        return ""
+    return XML_BLOCK_RE.sub("", text).strip()
+
+
+def is_clarification_question(text: str) -> bool:
+    """Return True when ``text`` (ignoring XML) asks for missing context.
+
+    The check is intentionally conservative and deterministic:
+
+    1. Strip all XML control blocks first.
+    2. An explicit ``?`` always counts as a question.
+    3. Otherwise match interrogative / request-for-input phrasing
+       (what/which/clarify/missing/need/please provide/...).
+
+    Args:
+        text: Raw persona-LLM output (may still contain XML blocks).
+
+    Returns:
+        True if the non-XML remainder poses a question or requests missing
+        context; False for pure statements, reports, and empty input.
+    """
+    remainder = strip_all_xml(text)
+    if not remainder:
+        return False
+    if "?" in remainder:
+        return True
+    return QUESTION_RE.search(remainder) is not None
diff --git a/mcp-persona-server/server.py b/mcp-persona-server/server.py
new file mode 100644
index 0000000..4419cf1
--- /dev/null
+++ b/mcp-persona-server/server.py
@@ -0,0 +1,231 @@
+#!/usr/bin/env -S uv run
+# /// script
+# requires-python = ">=3.10"
+# dependencies = [
+#     "mcp[cli]>=1.0,<2.0",
+#     "litellm",
+# ]
+# ///
+
+"""Persona dispatch MCP server (Task 167).
+
+Replaces the retired ``loop-engine/`` daemon with on-demand persona turns:
+the cognitive-executor calls ``dispatch_session_turn`` with a persona name
+(``QA Engineer``, ``Code Reviewer``, ...) plus the instruction, and a light
+LLM — holding the full system prompt, repo rules, and cumulative task
+history (progressive lineage projection) — responds. Raw model output is
+classified by the Dual Dispatch pattern:
+
+- XML control block present  -> ``status="XML_EXTRACTED"`` (+ verbatim block)
+- No XML but asks questions  -> ``status="QUESTION"`` (relay to the asker)
+- Otherwise                  -> ``status="REPORT"`` (free-form evaluation)
+
+Manager hard gates (Telegram inline Approve/Reject, open questions) are
+exposed as ``request_admin_approval`` / ``escalate_to_admin``.
+
+Transport: stdio FastMCP, mirroring mcp-context-server / mcp-memory-server.
+``litellm`` is imported lazily inside the dispatch path so module import
+(and unit tests) never need network access or provider credentials.
+"""
+
+from __future__ import annotations
+
+import os
+from pathlib import Path
+from typing import Any, Optional
+
+from mcp.server.fastmcp import FastMCP
+
+from dual_dispatch import extract_xml, is_clarification_question
+from session import append_turn, build_persona_messages, summarize_session
+from telegram import send_admin_question, send_approval_request
+
+# Repo root resolved from this file's location so path handling works no
+# matter which cwd the stdio server is launched from.
+REPO_ROOT = Path(__file__).resolve().parent.parent
+
+mcp = FastMCP("PersonaServer")
+
+
+def _get_persona_model() -> str:
+    """LLM model for persona turns; override via ``PERSONA_MODEL``."""
+    return os.environ.get("PERSONA_MODEL", "openrouter/google/gemini-3.8-flash").strip() or (
+        "openrouter/google/gemini-3.8-flash"
+    )
+
+
+def _get_reasoning_effort() -> str:
+    """Reasoning effort for persona turns; override via ``PERSONA_REASONING_EFFORT``."""
+    return (
+        os.environ.get("PERSONA_REASONING_EFFORT", "high").strip() or "high"
+    )
+
+
+def _get_temperature() -> float:
+    """Sampling temperature; override via ``PERSONA_TEMPERATURE`` (default 0.2)."""
+    try:
+        return float(os.environ.get("PERSONA_TEMPERATURE", "0.2") or 0.2)
+    except ValueError:
+        return 0.2
+
+
+def _get_max_tokens() -> int:
+    """Max completion tokens; override via ``PERSONA_MAX_TOKENS`` (default 16384)."""
+    try:
+        return int(os.environ.get("PERSONA_MAX_TOKENS", "16384") or 16384)
+    except ValueError:
+        return 16384
+
+
+def _call_llm(model: str, messages: list[dict[str, str]]) -> str:
+    """One LiteLLM completion; returns the assistant text (never None).
+
+    The import is lazy so importing this server module stays side-effect
+    free. ``drop_params=True`` keeps providers that reject ``reasoning_effort``
+    from failing the whole turn.
+    """
+    import litellm  # Lazy: no network/credentials needed at import time.
+
+    response = litellm.completion(
+        model=model,
+        messages=messages,
+        temperature=_get_temperature(),
+        max_tokens=_get_max_tokens(),
+        reasoning_effort=_get_reasoning_effort(),
+        drop_params=True,
+    )
+    return str(response.choices[0].message.content or "")
+
+
+def _read_task_file(task_file_path: Optional[str]) -> Optional[str]:
+    """Read the task file body for lineage injection; None when absent."""
+    if not task_file_path:
+        return None
+    candidate = Path(task_file_path)
+    if not candidate.is_absolute():
+        candidate = REPO_ROOT / task_file_path
+    try:
+        return candidate.read_text(encoding="utf-8")
+    except (OSError, UnicodeError):
+        return None
+
+
+@mcp.tool()
+def dispatch_session_turn(
+    task_id: int,
+    persona_name: str,
+    instruction: str,
+    task_file_path: Optional[str] = None,
+    force_xml: bool = False,
+) -> dict[str, Any]:
+    """Run one persona turn and classify the raw model output.
+
+    1. Reads ``system-prompt.md`` + the full task file body from disk
+       (progressive lineage projection via ``session.build_persona_messages``).
+    2. Appends the instruction turn to ``tasks/.sessions/{task_id}/``.
+    3. Calls LiteLLM (``PERSONA_MODEL``, ``PERSONA_REASONING_EFFORT``).
+    4. Dual Dispatch: XML present -> ``XML_EXTRACTED``; question -> ``QUESTION``;
+       otherwise -> ``REPORT``. With ``force_xml=True`` and no XML block, the
+       caller gets ``RETRY_NEEDED`` (re-dispatch with a stronger instruction)
+       instead of a silently unstructured answer.
+
+    Args:
+        task_id: Owning task id (session scope + audit trail).
+        persona_name: e.g. ``"QA Engineer"``, ``"Code Reviewer"``.
+        instruction: User-side instruction for this turn.
+        task_file_path: Optional repo-relative task file for context.
+        force_xml: Require a structured XML block in the reply.
+
+    Returns:
+        Dict with ``status``, ``persona_name``, ``task_id``, plus either
+        ``xml_content`` (XML_EXTRACTED), ``question`` (QUESTION),
+        ``report`` (REPORT), or ``hint`` (RETRY_NEEDED).
+    """
+    task_body = _read_task_file(task_file_path)
+    if task_body is not None:
+        append_turn(task_id, "user", f"Task file `{task_file_path}` injected.\n\n{task_body}")
+    append_turn(task_id, "user", instruction, name="executor")
+
+    # Transcript replay already carries the injected task body + instruction,
+    # so build messages without re-injecting the file (avoids triple context).
+    messages = build_persona_messages(
+        task_id, persona_name, instruction, None, repo_root=REPO_ROOT
+    )
+    output = _call_llm(_get_persona_model(), messages)
+    append_turn(task_id, "assistant", output, name=persona_name)
+
+    has_xml, xml_content, clean_text = extract_xml(output)
+    if has_xml:
+        return {
+            "status": "XML_EXTRACTED",
+            "task_id": int(task_id),
+            "persona_name": persona_name,
+            "xml_content": xml_content,
+            "remainder": clean_text,
+        }
+    if force_xml:
+        return {
+            "status": "RETRY_NEEDED",
+            "task_id": int(task_id),
+            "persona_name": persona_name,
+            "hint": (
+                "No XML control block found but force_xml=True. Re-dispatch with an "
+                "instruction that explicitly demands a <hands_*_task> block. Raw output: "
+                + output[:2000]
+            ),
+        }
+    if is_clarification_question(output):
+        return {
+            "status": "QUESTION",
+            "task_id": int(task_id),
+            "persona_name": persona_name,
+            "question": clean_text or output.strip(),
+        }
+    return {
+        "status": "REPORT",
+        "task_id": int(task_id),
+        "persona_name": persona_name,
+        "report": output.strip(),
+    }
+
+
+@mcp.tool()
+def get_session_summary(task_id: int) -> dict[str, Any]:
+    """Return the high-level milestone ledger for ``task_id``.
+
+    Read-only: turn counts by role, session time span, and the latest
+    assistant excerpt. Delegates to ``session.summarize_session``.
+    """
+    return summarize_session(task_id)
+
+
+@mcp.tool()
+def escalate_to_admin(
+    task_id: int, question: str, options: Optional[list[str]] = None
+) -> dict[str, str]:
+    """Ask the human manager an open question via Telegram and await reply.
+
+    Delegates to ``telegram.send_admin_question``. Always returns a dict —
+    transport failures arrive as ``"ERROR: ..."`` answer strings, never as
+    raised exceptions, so the executor loop stays alive.
+    """
+    answer = send_admin_question(task_id, question, options or [])
+    return {"task_id": str(task_id), "answer": answer}
+
+
+@mcp.tool()
+def request_admin_approval(
+    task_id: int, stage: str, summary: str, task_file_path: str = ""
+) -> dict[str, Any]:
+    """Open a Telegram Approve/Reject gate for ``stage`` and await the decision.
+
+    Delegates to ``telegram.send_approval_request``. The manager's decision
+    (``approve``/``reject``) is the hard gate: callers MUST NOT auto-continue
+    on any other outcome.
+    """
+    result = send_approval_request(task_id, stage, summary, task_file_path)
+    return {"task_id": int(task_id), "stage": stage, **result}
+
+
+if __name__ == "__main__":
+    mcp.run(transport="stdio")
diff --git a/mcp-persona-server/session.py b/mcp-persona-server/session.py
new file mode 100644
index 0000000..380ea34
--- /dev/null
+++ b/mcp-persona-server/session.py
@@ -0,0 +1,233 @@
+"""Append-only session transcripts for persona dispatch turns (Task 167).
+
+Each persona conversation lives under::
+
+    tasks/.sessions/{task_id}/transcript.jsonl
+
+One JSON object per line (``{"role", "content", "name", "timestamp"}``),
+which is both human-inspectable and directly reusable as LiteLLM message
+history (``role``/``content``). The file is append-only: turns are never
+rewritten, so the transcript doubles as the audit trail for manager
+approval gates.
+
+Progressive lineage projection (``build_persona_messages``) assembles the
+full LLM context for a turn: global system prompt, repo rules, persona
+brief, cumulative task conversation, and the new instruction — newest,
+most specific context last so the model weights it highest.
+"""
+
+from __future__ import annotations
+
+import json
+import os
+from datetime import datetime, timezone
+from pathlib import Path
+from typing import Any, Optional
+
+# Overridable for tests: point at a tmp dir to avoid touching the real repo.
+SESSIONS_ROOT = Path(os.environ.get("PERSONA_SESSIONS_DIR", "tasks/.sessions"))
+
+# Files projected into every persona turn (repo-root relative). Missing files
+# are skipped silently so sessions degrade gracefully on partial checkouts.
+LINEAGE_FILES = ("system-prompt.md", "AGENTS.md")
+
+
+def _utc_now() -> str:
+    """Current UTC time as an ISO-8601 string (used for turn timestamps)."""
+    return datetime.now(timezone.utc).isoformat()
+
+
+def session_dir(task_id: int) -> Path:
+    """Return (creating on demand) the session directory for ``task_id``.
+
+    Args:
+        task_id: Numeric task identifier; coerced to int so ``"167"`` and
+            ``167`` resolve to the same directory.
+
+    Raises:
+        ValueError: If ``task_id`` is not integer-coercible.
+    """
+    try:
+        tid = int(task_id)
+    except (TypeError, ValueError) as exc:
+        raise ValueError(f"task_id must be an integer, got {task_id!r}") from exc
+    path = SESSIONS_ROOT / str(tid)
+    path.mkdir(parents=True, exist_ok=True)
+    return path
+
+
+def transcript_path(task_id: int) -> Path:
+    """Full path of the JSONL transcript file for ``task_id``."""
+    return session_dir(task_id) / "transcript.jsonl"
+
+
+def append_turn(
+    task_id: int,
+    role: str,
+    content: str,
+    name: Optional[str] = None,
+) -> dict[str, Any]:
+    """Append one turn to the session transcript (append-only).
+
+    Args:
+        task_id: Owning task id.
+        role: LiteLLM message role (``system``/``user``/``assistant``).
+        content: Turn text.
+        name: Optional participant label (e.g. persona name).
+
+    Returns:
+        The stored record dict (including its timestamp).
+    """
+    record: dict[str, Any] = {
+        "role": role,
+        "content": content,
+        "name": name,
+        "timestamp": _utc_now(),
+    }
+    with open(transcript_path(task_id), "a", encoding="utf-8") as fh:
+        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
+    return record
+
+
+def read_transcript(task_id: int) -> list[dict[str, Any]]:
+    """Read all turns for ``task_id`` in order; empty list when none exist.
+
+    Corrupt lines are skipped (never crash a live session on a bad line);
+    a missing transcript simply means "no history yet".
+    """
+    path = session_dir(task_id) / "transcript.jsonl"
+    if not path.is_file():
+        return []
+    turns: list[dict[str, Any]] = []
+    with open(path, encoding="utf-8") as fh:
+        for line in fh:
+            line = line.strip()
+            if not line:
+                continue
+            try:
+                record = json.loads(line)
+            except json.JSONDecodeError:
+                continue  # Skip corrupt lines; keep the session usable.
+            if isinstance(record, dict) and "content" in record:
+                turns.append(record)
+    return turns
+
+
+def _read_repo_file(relative: str) -> Optional[str]:
+    """Read a repo-root-relative file; None when missing/unreadable."""
+    try:
+        return Path(relative).read_text(encoding="utf-8")
+    except (OSError, UnicodeError):
+        return None
+
+
+def build_persona_messages(
+    task_id: int,
+    persona_name: str,
+    instruction: str,
+    task_file_path: Optional[str] = None,
+    repo_root: Optional[Path] = None,
+) -> list[dict[str, str]]:
+    """Assemble the LiteLLM message list for one persona turn.
+
+    Progressive lineage projection, broadest context first:
+
+    1. ``system`` — global ``system-prompt.md`` + ``AGENTS.md`` (survives
+       every turn; the persona always reasons under repo rules).
+    2. ``system`` — persona brief (``prompts/fragments/06-personas.md`` when
+       present, else a minimal fallback naming the persona).
+    3. ``user`` — full task file body when ``task_file_path`` is given
+       (cumulative task conversation / acceptance criteria).
+    4. Prior transcript turns replayed verbatim (cumulative memory).
+    5. ``user`` — the new instruction (most specific, last).
+
+    Args:
+        task_id: Owning task id (for transcript replay).
+        persona_name: e.g. ``"QA Engineer"``, ``"Code Reviewer"``.
+        instruction: The new user-side instruction for this turn.
+        task_file_path: Optional task file to inject as task context.
+        repo_root: Directory lineage files resolve against (defaults to the
+            current working directory, i.e. the repo root under stdio).
+
+    Returns:
+        LiteLLM-compatible message list (``role``/``content`` dicts only —
+        ``name``/``timestamp`` are transcript metadata, not LLM fields).
+    """
+    root = Path(repo_root) if repo_root is not None else Path.cwd()
+
+    # 1. Global lineage: system prompt + repo rules.
+    system_parts = []
+    for relative in LINEAGE_FILES:
+        body = _read_repo_file(str(root / relative))
+        if body:
+            system_parts.append(f"# {relative}\n\n{body}")
+    system_text = (
+        "You are a persona of the Cognitive Lead AI multi-persona review pipeline.\n"
+        "Reason strictly under the repository rules below.\n\n" + "\n\n".join(system_parts)
+        if system_parts
+        else "You are a persona of the Cognitive Lead AI multi-persona review pipeline."
+    )
+    messages: list[dict[str, str]] = [{"role": "system", "content": system_text}]
+
+    # 2. Persona brief.
+    personas_body = _read_repo_file(str(root / "prompts" / "fragments" / "06-personas.md"))
+    if personas_body:
+        messages.append(
+            {
+                "role": "system",
+                "content": f"You are acting as persona: {persona_name}.\n\n{personas_body}",
+            }
+        )
+    else:
+        messages.append(
+            {"role": "system", "content": f"You are acting as persona: {persona_name}."}
+        )
+
+    # 3. Cumulative task context.
+    if task_file_path:
+        task_body = _read_repo_file(task_file_path)
+        if task_body:
+            messages.append(
+                {
+                    "role": "user",
+                    "content": f"Task file `{task_file_path}` (full context):\n\n{task_body}",
+                }
+            )
+
+    # 4. Replay prior turns (LiteLLM fields only).
+    for turn in read_transcript(task_id):
+        role = turn.get("role", "user")
+        if role not in ("system", "user", "assistant"):
+            role = "user"
+        messages.append({"role": role, "content": str(turn.get("content", ""))})
+
+    # 5. The new instruction goes last (highest recency weight).
+    messages.append({"role": "user", "content": instruction})
+    return messages
+
+
+def summarize_session(task_id: int) -> dict[str, Any]:
+    """Return a high-level milestone ledger for ``task_id``.
+
+    Counts turns by role, reports the time span, and surfaces the latest
+    assistant output as the current milestone. Pure read path — never mutates
+    the transcript.
+    """
+    turns = read_transcript(task_id)
+    by_role: dict[str, int] = {}
+    for turn in turns:
+        by_role[turn.get("role", "unknown")] = by_role.get(turn.get("role", "unknown"), 0) + 1
+    last_assistant: Optional[str] = None
+    for turn in reversed(turns):
+        if turn.get("role") == "assistant":
+            last_assistant = str(turn.get("content", ""))[:2000]
+            break
+    timestamps = [t.get("timestamp") for t in turns if t.get("timestamp")]
+    return {
+        "task_id": int(task_id),
+        "turn_count": len(turns),
+        "turns_by_role": by_role,
+        "first_turn_at": timestamps[0] if timestamps else None,
+        "last_turn_at": timestamps[-1] if timestamps else None,
+        "latest_assistant_excerpt": last_assistant,
+    }
diff --git a/mcp-persona-server/telegram.py b/mcp-persona-server/telegram.py
new file mode 100644
index 0000000..9ed7240
--- /dev/null
+++ b/mcp-persona-server/telegram.py
@@ -0,0 +1,245 @@
+"""Telegram manager-approval transport for the persona engine (Task 167).
+
+Thin wrapper over the Telegram Bot HTTP API using only the standard library
+(``urllib``) — no third-party client dependency. Two flows:
+
+- **Approval gate** (``send_approval_request``): posts a stage summary with an
+  inline ``[Approve]`` / ``[Reject]`` keyboard, then long-polls ``getUpdates``
+  for the manager's callback query. Oversized summaries fall back to a
+  document attachment so the gate never silently truncates context.
+- **Open question** (``send_admin_question``): posts a question (optionally
+  with an option keyboard) and awaits either a callback press or a plain
+  text reply.
+
+Credentials come from the environment (``TELEGRAM_BOT_TOKEN``,
+``TELEGRAM_CHAT_ID``); when absent the functions return
+``{"sent": False, ...}`` instead of raising, so the MCP server degrades
+gracefully on checkouts without a bot configured. Timeouts come from
+``TELEGRAM_APPROVAL_TIMEOUT_SECONDS`` (default 1800s).
+
+All network I/O funnels through ``_api()`` so tests can stub the transport
+without touching the network.
+"""
+
+from __future__ import annotations
+
+import json
+import os
+import time
+import urllib.parse
+import urllib.request
+from typing import Any, Callable, Optional
+
+# Telegram caps text messages at 4096 chars; stay safely under it.
+MAX_TEXT_LEN = 3500
+# Long-poll window per getUpdates call (seconds).
+POLL_WINDOW = 25
+
+
+def _env(name: str, default: str = "") -> str:
+    """Read ``name`` from the environment, stripped; ``default`` when unset."""
+    return os.environ.get(name, default).strip()
+
+
+def _api(
+    token: str,
+    method: str,
+    payload: dict[str, Any],
+    transport: Optional[Callable[..., dict[str, Any]]] = None,
+) -> dict[str, Any]:
+    """POST one Bot API call and return the decoded JSON response.
+
+    Args:
+        token: Bot token (already validated non-empty by callers).
+        method: Bot API method name (``sendMessage``, ``getUpdates``, ...).
+        payload: JSON-serializable parameters.
+        transport: Test hook — when given, called as
+            ``transport(method, payload)`` instead of hitting the network.
+
+    Raises:
+        RuntimeError: On transport errors or ``ok: false`` API responses.
+    """
+    if transport is not None:
+        return transport(method, payload)
+    url = f"https://api.telegram.org/bot{token}/{method}"
+    data = json.dumps(payload).encode("utf-8")
+    request = urllib.request.Request(
+        url, data=data, headers={"Content-Type": "application/json"}
+    )
+    try:
+        with urllib.request.urlopen(request, timeout=POLL_WINDOW + 10) as response:
+            body = json.loads(response.read().decode("utf-8"))
+    except Exception as exc:
+        raise RuntimeError(f"Telegram API call {method} failed: {exc}") from exc
+    if not body.get("ok"):
+        raise RuntimeError(f"Telegram API call {method} not ok: {body}")
+    return body
+
+
+def _approval_keyboard() -> dict[str, Any]:
+    """Inline keyboard markup with Approve / Reject callback buttons."""
+    return {
+        "inline_keyboard": [
+            [
+                {"text": "✅ Approve", "callback_data": "approve"},
+                {"text": "❌ Reject", "callback_data": "reject"},
+            ]
+        ]
+    }
+
+
+def _options_keyboard(options: list[str]) -> dict[str, Any]:
+    """Inline keyboard with one button per option (callback = option text)."""
+    return {"inline_keyboard": [[{"text": opt, "callback_data": opt}] for opt in options]}
+
+
+def _wait_for_update(
+    token: str,
+    chat_id: str,
+    timeout_s: int,
+    transport: Optional[Callable[..., dict[str, Any]]] = None,
+) -> dict[str, Any]:
+    """Long-poll ``getUpdates`` until an update for ``chat_id`` arrives.
+
+    Accepts either a ``callback_query`` (inline button press) or a plain
+    ``message`` (typed reply). Returns the raw update dict.
+
+    Raises:
+        TimeoutError: When ``timeout_s`` elapses with no matching update.
+    """
+    deadline = time.monotonic() + timeout_s
+    offset = 0
+    while time.monotonic() < deadline:
+        window = max(1, min(POLL_WINDOW, int(deadline - time.monotonic())))
+        body = _api(
+            token,
+            "getUpdates",
+            {"offset": offset, "timeout": window, "allowed_updates": ["message", "callback_query"]},
+            transport,
+        )
+        for update in body.get("result", []):
+            offset = max(offset, int(update.get("update_id", 0)) + 1)
+            # Callback press on our keyboard?
+            callback = update.get("callback_query") or {}
+            callback_msg = callback.get("message") or {}
+            callback_chat = callback_msg.get("chat") or {}
+            if str(callback_chat.get("id", "")) == str(chat_id) and callback.get("data"):
+                return update
+            # Plain typed reply in the target chat?
+            message = update.get("message") or {}
+            msg_chat = message.get("chat") or {}
+            if str(msg_chat.get("id", "")) == str(chat_id) and message.get("text"):
+                return update
+    raise TimeoutError(f"No Telegram response within {timeout_s}s")
+
+
+def _extract_answer(update: dict[str, Any]) -> str:
+    """Pull the manager's answer out of a raw update (callback or text)."""
+    callback = update.get("callback_query") or {}
+    if callback.get("data"):
+        return str(callback["data"])
+    message = update.get("message") or {}
+    return str(message.get("text", ""))
+
+
+def send_approval_request(
+    task_id: int,
+    stage: str,
+    summary: str,
+    task_file_path: str = "",
+    transport: Optional[Callable[..., dict[str, Any]]] = None,
+) -> dict[str, Any]:
+    """Post an approval gate to the manager and await Approve/Reject.
+
+    Args:
+        task_id: Owning task id (echoed in the message + callback scope).
+        stage: Gate name, e.g. ``"QA"`` or ``"closure"``.
+        summary: Human-readable stage summary. Oversized summaries are split
+            into sequential messages (keyboard on the last) so the gate
+            never silently truncates context.
+        task_file_path: Optional task file reference echoed in the message.
+        transport: Test hook forwarded to ``_api``/``_wait_for_update``.
+
+    Returns:
+        Dict with ``sent`` (bool), ``decision`` (``"approve"``/``"reject"``
+        or raw text), ``update_id``, and on failure ``reason`` instead of a
+        decision. Never raises for missing credentials — returns
+        ``{"sent": False, "reason": "missing Telegram credentials"}``.
+    """
+    token = _env("TELEGRAM_BOT_TOKEN")
+    chat_id = _env("TELEGRAM_CHAT_ID")
+    if not token or not chat_id:
+        return {"sent": False, "reason": "missing Telegram credentials"}
+    timeout_s = int(os.environ.get("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "1800") or 1800)
+
+    header = f"Task {task_id} — approval requested: {stage}\n"
+    ref = f"Task file: {task_file_path}\n" if task_file_path else ""
+    full_text = (header + ref + "\n" + summary).strip()
+    # Chunk oversized bodies into sequential messages (Telegram caps single
+    # messages); the inline keyboard rides on the FINAL chunk so the manager
+    # decides with the complete context above. Nothing is truncated.
+    chunks = [full_text[i : i + MAX_TEXT_LEN] for i in range(0, len(full_text), MAX_TEXT_LEN)]
+    try:
+        for chunk in chunks[:-1]:
+            _api(token, "sendMessage", {"chat_id": chat_id, "text": chunk}, transport)
+        _api(
+            token,
+            "sendMessage",
+            {
+                "chat_id": chat_id,
+                "text": chunks[-1],
+                "reply_markup": _approval_keyboard(),
+            },
+            transport,
+        )
+        update = _wait_for_update(token, chat_id, timeout_s, transport)
+        return {
+            "sent": True,
+            "decision": _extract_answer(update),
+            "update_id": update.get("update_id"),
+        }
+    except (RuntimeError, TimeoutError) as exc:
+        return {"sent": False, "reason": str(exc)}
+
+
+def send_admin_question(
+    task_id: int,
+    question: str,
+    options: Optional[list[str]] = None,
+    transport: Optional[Callable[..., dict[str, Any]]] = None,
+) -> str:
+    """Send an open question to the manager and await the reply text.
+
+    Args:
+        task_id: Owning task id (echoed in the message).
+        question: Question text.
+        options: Optional inline-button options; without them any typed
+            reply is accepted.
+        transport: Test hook forwarded to ``_api``/``_wait_for_update``.
+
+    Returns:
+        The manager's answer (callback data or message text), or an
+        explanatory ``"ERROR: ..."`` string when credentials are missing
+        or polling fails — never raises, so the MCP tool always returns.
+    """
+    token = _env("TELEGRAM_BOT_TOKEN")
+    chat_id = _env("TELEGRAM_CHAT_ID")
+    if not token or not chat_id:
+        return "ERROR: missing Telegram credentials"
+    timeout_s = int(os.environ.get("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "1800") or 1800)
+    payload: dict[str, Any] = {
+        "chat_id": chat_id,
+        "text": f"Task {task_id} — manager input needed:\n\n{question}".strip(),
+    }
+    if options:
+        payload["reply_markup"] = _options_keyboard(list(options))
+    try:
+        _api(token, "sendMessage", payload, transport)
+        update = _wait_for_update(token, chat_id, timeout_s, transport)
+        return _extract_answer(update)
+    except (RuntimeError, TimeoutError) as exc:
+        return f"ERROR: {exc}"
+
+
+# Re-export for callers that reference the query-string form explicitly.
+urlencode = urllib.parse.urlencode
diff --git a/opencode.json b/opencode.json
index 8e5bab9..d6a0575 100644
--- a/opencode.json
+++ b/opencode.json
@@ -24,6 +24,12 @@
       "command": ["uv", "run", "mcp-lint-server/server.py"],
       "enabled": true,
       "timeout": 15000
+    },
+    "persona": {
+      "type": "local",
+      "command": ["uv", "run", "mcp-persona-server/server.py"],
+      "enabled": true,
+      "timeout": 120000
     }
   },
   "permission": {
@@ -43,6 +49,10 @@
     "bundle_tasks": "allow",
     "blowsh_*": "allow",
     "telegram_*": "allow",
+    "dispatch_session_turn": "allow",
+    "get_session_summary": "allow",
+    "escalate_to_admin": "allow",
+    "request_admin_approval": "allow",
     "external_directory": {
       "*": "ask",
       "/tmp/**": "allow"
diff --git a/tests/test_persona_server.py b/tests/test_persona_server.py
new file mode 100644
index 0000000..ab28ea9
--- /dev/null
+++ b/tests/test_persona_server.py
@@ -0,0 +1,378 @@
+"""Unit tests for mcp-persona-server (Task 167).
+
+Covers:
+- ``dual_dispatch.extract_xml``: valid XML, malformed XML, conversational
+  preamble/trailing text, and pure question text.
+- ``dual_dispatch.is_clarification_question``: questions vs reports.
+- ``session`` transcript serialization + persistence (isolated via a tmp
+  sessions dir) and lineage message assembly.
+- ``server`` environment variable fallbacks and dispatch status
+  classification (``XML_EXTRACTED`` / ``QUESTION`` / ``REPORT`` /
+  ``RETRY_NEEDED``) with a stubbed ``litellm`` module — no network.
+- ``telegram`` approval flow via stub transport + missing-credential
+  degradation.
+
+Run: ``pytest tests/test_persona_server.py -v`` (repo root).
+"""
+
+import importlib
+import json
+import sys
+import types
+from pathlib import Path
+
+import pytest
+
+PERSONA_DIR = Path(__file__).parent.parent / "mcp-persona-server"
+sys.path.insert(0, str(PERSONA_DIR))
+
+
+def _load(name, filename):
+    spec = importlib.util.spec_from_file_location(name, PERSONA_DIR / filename)
+    mod = importlib.util.module_from_spec(spec)
+    sys.modules[name] = mod  # So cross-imports (server -> session) resolve.
+    spec.loader.exec_module(mod)
+    return mod
+
+
+@pytest.fixture(scope="module")
+def dual():
+    return _load("persona_dual_dispatch", "dual_dispatch.py")
+
+
+@pytest.fixture(scope="module")
+def sess(tmp_path_factory):
+    mod = _load("persona_session", "session.py")
+    mod.SESSIONS_ROOT = tmp_path_factory.mktemp("sessions")
+    return mod
+
+
+@pytest.fixture(scope="module")
+def server_mod(sess):
+    # server.py does `from session import ...` — alias our loaded module.
+    sys.modules["session"] = sess
+    sys.modules["dual_dispatch"] = _load("persona_dual_dispatch", "dual_dispatch.py")
+    sys.modules["telegram"] = _load("persona_telegram", "telegram.py")
+    return _load("persona_server", "server.py")
+
+
+# --- extract_xml -----------------------------------------------------------
+
+VALID_XML = """<hands_implementation_task>
+  <validation_phase>check rules</validation_phase>
+</hands_implementation_task>"""
+
+
+def test_extract_xml_valid_block(dual):
+    has_xml, xml, clean = dual.extract_xml(VALID_XML)
+    assert has_xml is True
+    assert xml == VALID_XML
+    assert clean == ""
+
+
+def test_extract_xml_with_preamble_and_trailing(dual):
+    text = "Here is your next instruction:\n\n" + VALID_XML + "\n\nGood luck!"
+    has_xml, xml, clean = dual.extract_xml(text)
+    assert has_xml is True
+    assert xml == VALID_XML
+    assert "Here is your next instruction" in clean
+    assert "Good luck!" in clean
+    assert "<hands_implementation_task>" not in clean
+
+
+def test_extract_xml_malformed_missing_close(dual):
+    text = "<hands_implementation_task>\n  <validation_phase>oops, no close tag"
+    has_xml, xml, clean = dual.extract_xml(text)
+    assert has_xml is False
+    assert xml is None
+    # Malformed input falls through unchanged (stripped) for downstream handling.
+    assert clean == text.strip()
+
+
+def test_extract_xml_pure_question_text(dual):
+    text = "Which model should I use for the QA persona?"
+    has_xml, xml, clean = dual.extract_xml(text)
+    assert has_xml is False
+    assert xml is None
+    assert clean == text
+
+
+def test_extract_xml_failure_report_tag(dual):
+    text = "<failure_report>\nBuild failed.\n</failure_report>"
+    has_xml, xml, clean = dual.extract_xml(text)
+    assert has_xml is True
+    assert xml == text
+
+
+def test_extract_xml_empty_input(dual):
+    assert dual.extract_xml("") == (False, None, "")
+
+
+def test_extract_xml_mismatched_tags_not_matched(dual):
+    text = "<hands_implementation_task>\nbody\n</hands_qa_task>"
+    has_xml, xml, clean = dual.extract_xml(text)
+    assert has_xml is False
+    assert xml is None
+
+
+# --- is_clarification_question ----------------------------------------------
+
+def test_question_mark_detected(dual):
+    assert dual.is_clarification_question("Should I run the full test suite?") is True
+
+
+def test_request_for_missing_context_detected(dual):
+    assert dual.is_clarification_question(
+        "The task file is missing acceptance criteria, please provide them."
+    ) is True
+
+
+def test_report_not_a_question(dual):
+    assert dual.is_clarification_question(
+        "All 55 tests pass. The implementation is complete and verified."
+    ) is False
+
+
+def test_empty_not_a_question(dual):
+    assert dual.is_clarification_question("") is False
+
+
+def test_xml_contents_ignored_for_question_check(dual):
+    # The XML block itself contains no question; trailing text is a statement.
+    text = VALID_XML + "\n\nDispatch acknowledged, proceeding."
+    assert dual.is_clarification_question(text) is False
+
+
+# --- session transcript ------------------------------------------------------
+
+def test_session_append_and_read_round_trip(sess):
+    sess.append_turn(167, "user", "Run QA", name="executor")
+    sess.append_turn(167, "assistant", "QA passed", name="QA Engineer")
+    turns = sess.read_transcript(167)
+    assert len(turns) == 2
+    assert turns[0]["role"] == "user" and turns[0]["content"] == "Run QA"
+    assert turns[0]["name"] == "executor"
+    assert turns[1]["role"] == "assistant" and turns[1]["name"] == "QA Engineer"
+    assert all(t["timestamp"] for t in turns)
+
+
+def test_session_transcript_is_jsonl(sess):
+    path = sess.transcript_path(167)
+    assert path.is_file()
+    for line in path.read_text(encoding="utf-8").splitlines():
+        record = json.loads(line)  # Must not raise: one JSON object per line.
+        assert {"role", "content", "name", "timestamp"} <= set(record)
+
+
+def test_session_read_missing_transcript_empty(sess):
+    assert sess.read_transcript(999999) == []
+
+
+def test_session_invalid_task_id_rejected(sess):
+    with pytest.raises(ValueError):
+        sess.session_dir("not-an-int")
+
+
+def test_session_build_messages_lineage_order(sess, tmp_path):
+    # Lineage files resolve against repo_root; transcript replays in the middle.
+    (tmp_path / "system-prompt.md").write_text("GLOBAL-SYSTEM", encoding="utf-8")
+    (tmp_path / "AGENTS.md").write_text("REPO-RULES", encoding="utf-8")
+    (tmp_path / "prompts").mkdir()
+    (tmp_path / "prompts" / "fragments").mkdir(parents=True)
+    (tmp_path / "prompts" / "fragments" / "06-personas.md").write_text(
+        "PERSONA-DEFS", encoding="utf-8"
+    )
+    task_file = tmp_path / "task.md"
+    task_file.write_text("TASK-BODY", encoding="utf-8")
+
+    sess.append_turn(168, "user", "prior instruction")
+    sess.append_turn(168, "assistant", "prior answer")
+    messages = sess.build_persona_messages(
+        168, "QA Engineer", "new instruction", str(task_file), repo_root=tmp_path
+    )
+    roles = [m["role"] for m in messages]
+    assert roles[0] == "system"  # Global lineage first.
+    assert "GLOBAL-SYSTEM" in messages[0]["content"]
+    assert "REPO-RULES" in messages[0]["content"]
+    assert any("PERSONA-DEFS" in m["content"] for m in messages)  # Persona brief.
+    assert any("TASK-BODY" in m["content"] for m in messages)  # Task file.
+    assert messages[-1] == {"role": "user", "content": "new instruction"}  # Newest last.
+    assert set(messages[-1]) == {"role", "content"}  # LiteLLM fields only.
+
+
+def test_session_summary_ledger(sess):
+    summary = sess.summarize_session(167)
+    assert summary["task_id"] == 167
+    assert summary["turn_count"] == 2
+    assert summary["turns_by_role"] == {"user": 1, "assistant": 1}
+    assert summary["first_turn_at"] and summary["last_turn_at"]
+    assert "QA passed" in (summary["latest_assistant_excerpt"] or "")
+
+
+# --- server env fallbacks -----------------------------------------------------
+
+def test_env_fallback_defaults(server_mod, monkeypatch):
+    for var in (
+        "PERSONA_MODEL",
+        "PERSONA_REASONING_EFFORT",
+        "PERSONA_TEMPERATURE",
+        "PERSONA_MAX_TOKENS",
+    ):
+        monkeypatch.delenv(var, raising=False)
+    assert server_mod._get_persona_model() == "openrouter/google/gemini-3.8-flash"
+    assert server_mod._get_reasoning_effort() == "high"
+    assert server_mod._get_temperature() == 0.2
+    assert server_mod._get_max_tokens() == 16384
+
+
+def test_env_overrides_respected(server_mod, monkeypatch):
+    monkeypatch.setenv("PERSONA_MODEL", "openrouter/custom/model")
+    monkeypatch.setenv("PERSONA_REASONING_EFFORT", "low")
+    monkeypatch.setenv("PERSONA_TEMPERATURE", "0.7")
+    monkeypatch.setenv("PERSONA_MAX_TOKENS", "4096")
+    assert server_mod._get_persona_model() == "openrouter/custom/model"
+    assert server_mod._get_reasoning_effort() == "low"
+    assert server_mod._get_temperature() == 0.7
+    assert server_mod._get_max_tokens() == 4096
+
+
+def test_env_invalid_numeric_falls_back(server_mod, monkeypatch):
+    monkeypatch.setenv("PERSONA_TEMPERATURE", "not-a-float")
+    monkeypatch.setenv("PERSONA_MAX_TOKENS", "not-an-int")
+    assert server_mod._get_temperature() == 0.2
+    assert server_mod._get_max_tokens() == 16384
+
+
+# --- dispatch classification (stubbed LLM) -------------------------------------
+
+def _stub_litellm(text):
+    """Fake litellm module whose completion returns ``text`` as the reply."""
+    message = types.SimpleNamespace(content=text)
+    choice = types.SimpleNamespace(message=message)
+    response = types.SimpleNamespace(choices=[choice])
+    stub = types.ModuleType("litellm")
+    stub.completion = lambda **kwargs: response
+    return stub
+
+
+def test_dispatch_xml_extracted(server_mod, sess, monkeypatch):
+    monkeypatch.setitem(sys.modules, "litellm", _stub_litellm("Preamble\n" + VALID_XML))
+    result = server_mod.dispatch_session_turn.fn(
+        171, "QA Engineer", "review this", task_file_path=None
+    ) if hasattr(server_mod.dispatch_session_turn, "fn") else server_mod.dispatch_session_turn(
+        171, "QA Engineer", "review this", task_file_path=None
+    )
+    assert result["status"] == "XML_EXTRACTED"
+    assert result["xml_content"] == VALID_XML
+    assert result["task_id"] == 171
+
+
+def test_dispatch_question(server_mod, monkeypatch):
+    monkeypatch.setitem(
+        sys.modules, "litellm", _stub_litellm("Which files should I review?")
+    )
+    call = server_mod.dispatch_session_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target(172, "Code Reviewer", "review this")
+    assert result["status"] == "QUESTION"
+    assert "Which files" in result["question"]
+
+
+def test_dispatch_report(server_mod, monkeypatch):
+    monkeypatch.setitem(
+        sys.modules, "litellm", _stub_litellm("All checks pass. No blocking findings.")
+    )
+    call = server_mod.dispatch_session_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target(173, "QA Engineer", "test this")
+    assert result["status"] == "REPORT"
+    assert "No blocking findings" in result["report"]
+
+
+def test_dispatch_force_xml_retry(server_mod, monkeypatch):
+    monkeypatch.setitem(sys.modules, "litellm", _stub_litellm("Just a plain report."))
+    call = server_mod.dispatch_session_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target(174, "QA Engineer", "test this", force_xml=True)
+    assert result["status"] == "RETRY_NEEDED"
+    assert "hint" in result
+
+
+# --- telegram transport ---------------------------------------------------------
+
+def test_telegram_approval_approve_flow(server_mod, monkeypatch):
+    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
+    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
+    calls = []
+
+    def fake_transport(method, payload):
+        calls.append(method)
+        if method == "sendMessage":
+            return {"ok": True, "result": {"message_id": 1}}
+        if method == "getUpdates":
+            return {
+                "ok": True,
+                "result": [
+                    {
+                        "update_id": 7,
+                        "callback_query": {
+                            "data": "approve",
+                            "message": {"chat": {"id": 12345}},
+                        },
+                    }
+                ],
+            }
+        raise AssertionError(method)
+
+    telegram = sys.modules["telegram"]
+    result = telegram.send_approval_request(
+        175, "QA", "All green.", transport=fake_transport
+    )
+    assert result["sent"] is True
+    assert result["decision"] == "approve"
+    assert result["update_id"] == 7
+    assert "sendMessage" in calls and "getUpdates" in calls
+
+
+def test_telegram_missing_credentials_degrade(server_mod, monkeypatch):
+    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
+    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
+    telegram = sys.modules["telegram"]
+    result = telegram.send_approval_request(175, "QA", "summary")
+    assert result["sent"] is False
+    assert "missing" in result["reason"].lower()
+    assert telegram.send_admin_question(175, "Proceed?").startswith("ERROR:")
+
+
+def test_telegram_long_summary_chunked_not_truncated(server_mod, monkeypatch):
+    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
+    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
+    sent_texts = []
+
+    def fake_transport(method, payload):
+        if method == "sendMessage":
+            sent_texts.append(payload["text"])
+            return {"ok": True, "result": {"message_id": 1}}
+        return {
+            "ok": True,
+            "result": [
+                {
+                    "update_id": 9,
+                    "callback_query": {
+                        "data": "reject",
+                        "message": {"chat": {"id": 12345}},
+                    },
+                }
+            ],
+        }
+
+    telegram = sys.modules["telegram"]
+    long_summary = "X" * (telegram.MAX_TEXT_LEN + 500)
+    result = telegram.send_approval_request(
+        176, "closure", long_summary, transport=fake_transport
+    )
+    assert result["sent"] is True
+    assert result["decision"] == "reject"
+    # Chunked delivery: every char sent, keyboard on the last message.
+    assert sum(len(t) for t in sent_texts) >= len(long_summary)
+    assert len(sent_texts) >= 2
```
<!-- END_GIT_DIFF -->
