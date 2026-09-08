# Task 167: Replace Loop-Engine With Persona Skill-MCP Slash Commands

**File:** `tasks/completed/167-replace-loop-engine-with-persona-skill-mcp-commands.md`
**Source:** telegram
**Type:** improvement
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `693318bf945fb0a1886905a71c0f3d05d597c8ae`
<!-- END_GIT_DIFF -->
