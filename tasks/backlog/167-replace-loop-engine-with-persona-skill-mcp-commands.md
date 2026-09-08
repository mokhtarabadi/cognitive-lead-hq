# Task 167: Replace Loop-Engine With Persona Skill-MCP Slash Commands

**File:** `tasks/backlog/167-replace-loop-engine-with-persona-skill-mcp-commands.md`
**Source:** telegram
**Type:** improvement
**Status:** open

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

- [ ] Initial codebase exploration
- [ ] Inventory loop-engine responsibilities vs OpenCode-native equivalents
- [ ] Verify functionality

## Acceptance Criteria

- [ ] Removal inventory maps every loop-engine module to replace-or-justify-delete
- [ ] Skill/MCP spec defines /QA, /reviewer, /manager commands with I/O contracts and wait semantics
- [ ] Manager Telegram approval remains a hard gate with audit trail

## Verification Evidence

- **Test command:** TBD by implementer (e.g., `pytest loop-engine/ -q` pre-removal baseline; post-migration skill/MCP smoke test)
- **Expected result:** All persona commands callable from cognitive-executor with approval gate enforced
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Deleting loop-engine loses scheduling, QA rigor, and approval audit trail with no replacement.
- **Rollback plan:** Keep branch with loop-engine/ intact until persona-command replacement passes QA; restore via `git revert`.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
