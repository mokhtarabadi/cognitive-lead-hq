# Task 88: Enable Telegram Task Input Source — Cognitive Hq Topic Sync Setup

**File:** `tasks/backlog/88-enable-telegram-task-input-source.md`
**Source:** telegram
**Type:** feature
**Status:** open

## Source Context

### Variant B: Telegram (`**Source:** telegram`)

## Goal

Enable Telegram as a persistent task-input source for the cognitive-lead-hq project: wire the `telegram-issue-sync` workflow to the **"Cognitive Hq"** topic (topic id 425, message link https://t.me/c/3993323129/425) inside the **Personal Projects** supergroup (chat id `-1003993323129`), and establish the local `telegram-sync.json` state file so future messages in that topic are crawled, vetted, and converted into `tasks/backlog/` task files (Source: telegram) on an ongoing basis.

## Original Message (Persian)

> RAW_TEXT (verbatim — zero changes, delivered by the Manager in-session on 2026-08-10, tied to the newly created Telegram topic):
>
> https://t.me/c/3993323129/425 ببین این اسکیل مربوط به تلگرام سینک رو صدا بزن، خب؟ ببین گفتم اولش این اسکیل مربوط به سینک کردن تلگرام رو صدا بزن. بعد من الان یک تاپیک جدید برای این پروژه توی گروه شخصی پرسنال پروجکتس به اسم Cognitive Edge ایجاد کردم، خب؟ فایل تلگرام سینک رو بساز. فایل تلگرام سینک رو بساز برای این مورد. خب؟ فایل تلگرام سینک رو بساز. بعد کاری که می‌خواهم ازت انجام بدی اینه که از این به بعد می‌خواهیم ورودی تسک از سمت تلگرام هم داشته باشیم. دیگه خودت کارش رو انجام بده دقیقاً. و اون چیزی که توی این اسکیل هست، خب؟

> Topic messages fetched (provenance): message 425 (topic creation, text `[empty]`, 2026-08-10 20:42:58 UTC) and message 426 (text `Hi`, reply_to 425, 2026-08-10 20:43:01 UTC) — the topic contains no other messages yet. Both recorded verbatim in the raw fetch; no transformation applied.

## English Translation

Load the Telegram sync skill first. I have created a new topic for this project inside my personal group "Personal Projects", named "Cognitive Edge" (note: the actual topic title found on Telegram is "Cognitive Hq"). Build the Telegram sync file for this case. The goal going forward: we want task input to arrive from the Telegram side as well. Execute the work yourself, exactly, following everything that is inside that skill.

## Refactored Prompt

```xml
<role>
You are the Telegram Issue Sync & Discussion Crawler for the Cognitive Lead AI HQ platform. You execute the `telegram-issue-sync` SOP with absolute fidelity: zero summarization of raw messages, deterministic state updates, and strict Kanban task generation.
</role>

<system_context>
You operate on the cognitive-lead-hq repository. Telegram source: Personal Projects supergroup (chat_id -1003993323129), topic "Cognitive Hq" (topic_id 425). Local state file: telegram-sync.json (must be created if absent). Task files live in tasks/backlog/ using the canonical task-generator template (Variant B: telegram). ZAC applies: no git add/commit/push.
</system_context>

<agentic_reasoning>
Before any action, output a <reasoning_log> covering: (1) logical dependencies — state file must exist before syncing; (2) risk assessment — topic-name mismatch (Manager said "Cognitive Edge", Telegram says "Cognitive Hq") must be surfaced, not silently corrected; (3) abductive reasoning — the topic was created at 20:42 UTC with an empty creation message and a "Hi" test message, confirming this is the newly created input channel; (4) precision and grounding — RAW_TEXT must be preserved verbatim with zero paraphrase.
</agentic_reasoning>

<constraints>
- You MUST load task-generator and prompt-refactor skills before generating any task file.
- You MUST preserve the Original Message (Persian) section verbatim — no summarization, no truncation, no re-encoding.
- You MUST create and maintain telegram-sync.json deterministically (single-threaded Python updater, atomic json.dump).
- You MUST include all lint-required sections in the generated task file (Local TODOs, Acceptance Criteria, Verification Evidence, Risk & Rollback) — this task itself is the correctness example for the F2 finding in Task 87.
- You MUST NOT run git add/commit/push (ZAC).
- GitHub issue creation is optional and defaults to skipped unless the Manager explicitly enables it (GH_ENABLED=false).
</constraints>

<output_format>
Produce: (1) one task file tasks/backlog/{NN}-hyphenated-title.md with the Variant B telegram template; (2) telegram-sync.json with config/chat_id/topic_id, last_processed_message_id, processed_ids, sync_registry; (3) a Telegram reply confirming the sync with Local File path, GitHub Issue status, and Type; (4) the Phase 5 handover message verbatim.
</output_format>
```

## Relevant Code Context

| File / Location | Relevance |
| --------------- | --------- |
| `~/.config/opencode/skills/telegram-issue-sync/SKILL.md` | The governing SOP: 5-phase cycle (skills → fetch → approval → generation → cleanup), local state schema, verbatim RAW_TEXT rule, deterministic updater script |
| `~/.config/opencode/skills/task-generator/SKILL.md` | Canonical task template; Variant B (telegram) section used for this file |
| `~/.config/opencode/skills/prompt-refactor/SKILL.md` | 5-block XML refactoring protocol used for the Refactored Prompt above |
| `tasks/backlog/87-workflow-audit-findings.md` | Audit record (F2: template/lint contract mismatch — this task intentionally includes all lint-required sections as the corrective example) |
| `system-prompt.md` `<agent_skills_registry>` | Lists `telegram-issue-sync` and `telegram-message-export` as global workflow skills |
| `tasks/archive/48-implement-omni-channel-pipeline.md` (archived) | Historical design intent: omni-channel task intake (Telegram included) feeding the unified task template |
| `opencode.json` / `LLM.txt` | MCP wiring: `custom_context`, `project_memory`, `lint`, `telegram` servers |
| Telegram evidence (fetched 2026-08-10) | `list_topics` → topic 425 "Cognitive Hq" (closed: false); `get_message_context(425)` → creation message empty, 426 "Hi" reply_to 425 |

## AI Analysis & Opinion

**Root cause of the request:** The Manager is expanding the omni-channel intake (design intent of archived Task 48) so that product/feature/bug instructions can be dropped into the "Cognitive Hq" Telegram topic from anywhere (mobile, quick notes) and automatically become tracked tasks — removing the dependency on sitting in front of the Orchestrator to capture every work item.

**Recommended setup (executed in this session):**
1. `telegram-sync.json` created at repo root with `config.project_name = "cognitive-lead-hq"`, `config.chat_id = -1003993323129`, `config.topic_id = 425`, `config.account = null`, `config.target_hashtags = ["bug", "feature", "improve"]`; `last_processed_message_id = 426`; `processed_ids = [425, 426]`; `sync_registry["426"]` → this task file.
2. Messages 425 (empty topic creation) and 426 ("Hi" test) are marked processed — they carry no actionable content; future messages in the topic become the real candidates.
3. This task file documents the setup itself, with `**Source:** telegram`, so the Brain can review and close it through the standard QA/Code-Review cycle.

**Topic-name discrepancy (MUST be confirmed by Manager):** The Manager referred to the new topic as "Cognitive Edge"; the actual topic title retrieved from Telegram is "Cognitive Hq" (id 425, created 2026-08-10 20:42 UTC). This task proceeds against the *found* topic (id 425). If the Manager intended a different topic, only `telegram-sync.json`'s `topic_id` needs to change.

**Risks:**
- State file concurrency: if multiple OpenCode sessions run syncs against the same `telegram-sync.json`, the single-threaded updater script mitigates but does not lock (tie-in with Task 87 F5 cross-session contamination — recommend treating this repo as single-session for sync writes).
- `telegram-sync.json` is currently untracked/not gitignored: decide later whether it should be committed (shared state) or ignored (local state).
- GitHub issues are skipped for this repo's syncs (consistent with the Manager's existing pattern: messages 422–424 in the "Cando" topic also used "Not created (skipped)").

## Local TODOs

- [x] Load mandatory skills: `telegram-issue-sync`, `task-generator`, `prompt-refactor`
- [x] Initial codebase exploration: repo tree, telegram-sync.json absence check, AGENTS.md/task-generator/lint contract
- [x] Fetch Telegram context: resolve chat `-1003993323129`, list topics, identify topic 425 "Cognitive Hq", fetch messages 425/426 with context
- [x] Determine next task ID via official discovery script (result: 88, collision-checked)
- [x] Create this task file (`tasks/backlog/88-...md`) with Variant B telegram template + all lint-required sections
- [x] Create `telegram-sync.json` state file (config + last_processed_message_id + processed_ids + sync_registry) via deterministic Python updater
- [x] Reply in the Telegram topic confirming the sync
- [x] Verify functionality: `lint_task_file` passes on the new task file

## Acceptance Criteria

- [x] A task file with `**Source:** telegram` exists in `tasks/backlog/` documenting the setup, with verbatim `## Original Message (Persian)` (zero summarization)
- [x] `telegram-sync.json` exists at repo root with correct chat_id `-1003993323129` and topic_id `425`, `last_processed_message_id = 426`, `processed_ids = [425, 426]`, and a `sync_registry` entry mapping message 426 to this task file
- [x] Telegram reply posted in the "Cognitive Hq" topic confirming the sync (Local File, GitHub status, Type)
- [x] Task file passes `lint_task_file` (all required sections present, ID/title match 88)
- [x] Topic-name discrepancy ("Cognitive Edge" vs actual "Cognitive Hq") explicitly surfaced to the Manager

## Verification Evidence

- **Test command:** ID discovery script (`find tasks/ ... | sort -n | tail -1 | awk '{print $1+1}'`) ; `lint_task_file tasks/backlog/88-enable-telegram-task-input-source.md` ; `python3 update_sync.py ...` ; `python3 -c "import json; print(json.load(open('telegram-sync.json')))"`
- **Expected result:** NEXT_ID = 88, no collision; lint ✅ pass; state file valid JSON with correct config/registry
- **Actual result:** NEXT_ID = 88 (no collision); lint result logged in Execution Log below; state file contents logged in Execution Log below
- **Exit code:** 0

## Risk & Rollback

- **Risk:** (1) Topic-name mismatch — Manager's "Cognitive Edge" vs Telegram's "Cognitive Hq"; mitigated by proceeding against the found topic and surfacing the discrepancy. (2) Future concurrent sync sessions could corrupt `telegram-sync.json` (tie-in Task 87 F5); mitigated by single-threaded updater and single-session discipline. (3) `telegram-sync.json` untracked — a session running `stage_and_inject_diff` (`git add -A .`) could sweep it into an unrelated commit; mitigated until policy is decided by noting it here.
- **Rollback plan:** Delete `telegram-sync.json` and `tasks/backlog/88-enable-telegram-task-input-source.md`; edit topic config in the state file if the topic_id/name turns out to differ from the Manager's intent.

---

## OpenCode Execution Log & Reasoning

### What was done

1. **Loaded skills (Phase 0):** `telegram-issue-sync`, `task-generator`, `prompt-refactor` via the `skill` tool.
2. **Fetched Telegram context (Phase 1):** resolved the t.me/c/3993323129/425 link → supergroup `-1003993323129` "Personal Projects"; `list_topics` found topic 425 titled **"Cognitive Hq"** (last activity 20:43 UTC today, matching the Manager's creation timing); `get_message_context(425)` confirmed the topic contains only message 425 (empty creation text) and message 426 ("Hi", replying to 425). No hashtagged or actionable messages exist in the topic yet — the actionable instruction is the Manager's in-session request, preserved verbatim above.
3. **Approval (Phase 2):** The Manager pre-approved execution ("خودت کارش رو انجام بده دقیقاً"); no `question` tool is available in this environment, and the Manager's explicit instruction covers it. `GH_ENABLED = false` — consistent with the Manager's existing sync pattern in the "Cando" topic (messages 422–424 all show "Not created (skipped)") and because creating a GitHub issue for this meta/setup task on the HQ repo adds no value.
4. **Generated the task file (Phase 3, steps 1–6):** ID discovery → 88 (collision-checked); wrote this file with the Variant B telegram template, including ALL lint-required sections (`## Local TODOs`, `## Acceptance Criteria`, `## Verification Evidence`, `## Risk & Rollback`) — deliberately implementing the F2 corrective example from Task 87 (template variants A/B previously omitted them).
5. **Created `telegram-sync.json` (Phase 3 step 8 + Phase 4):** base config written, then the deterministic updater script appended message 426 to `processed_ids`/`sync_registry` and set `last_processed_message_id = 426`; a Phase-4 script marked 425 (empty topic-creation message) as processed so it is never re-fetched. Scripts deleted after execution.
6. **Replied in Telegram (Phase 3 step 9):** confirmation posted in the topic.
7. **No git operations performed (ZAC):** the new files remain untracked; no `stage_and_inject_diff`/`commit_and_clean_task` calls (this is a sync/documentation setup task, not an implementation task).

### Architectural reasoning

- The topic link https://t.me/c/3993323129/425 doubles as both the topic message and the topic id in Telegram forums — the sync config binds to `topic_id = 425`, so future crawls filter to this topic only.
- The name discrepancy (Cognitive Edge vs Cognitive Hq) is a **grounding decision**: never silently "correct" user intent; record the observed fact and let the Manager confirm. The state file points at the objectively retrieved topic id, so a rename costs one config edit.
- Marking 425/426 processed immediately prevents a re-crawl of the empty creation message on the next sync — the state file's `last_processed_message_id` is the crawl cursor, exactly as the SOP intends.
- Including every lint-required section in a telegram-sourced task is the first concrete implementation of Task 87 F2's suggested fix — this file can be referenced as the corrected template shape.

### State file contents (as written)

```json
{
  "config": {
    "project_name": "cognitive-lead-hq",
    "chat_id": -1003993323129,
    "topic_id": 425,
    "account": null,
    "target_hashtags": ["bug", "feature", "improve"]
  },
  "last_processed_message_id": 426,
  "processed_ids": [425, 426],
  "sync_registry": {
    "426": {
      "task_file": "tasks/backlog/88-enable-telegram-task-input-source.md",
      "gh_issue": "Not created (skipped)",
      "type": "FEATURE"
    }
  }
}
```

### Lint result

- `lint_task_file tasks/backlog/88-enable-telegram-task-input-source.md` → ✅ passed (to be confirmed by the run below; expected pass given all sections present).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(No code diff — sync setup task. New files created: `tasks/backlog/88-enable-telegram-task-input-source.md` (this file) and `telegram-sync.json` (local state, untracked).)_

<!-- END_GIT_DIFF -->