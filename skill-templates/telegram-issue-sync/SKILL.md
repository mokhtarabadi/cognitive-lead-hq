---
name: telegram-issue-sync
description: Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management. Preserves raw bilingual messages verbatim, injects refactored prompts, and correlates codebase context.
---

# Telegram Issue Sync & Discussion Crawler SOP

## Purpose

Syncs actionable Telegram messages into GitHub Issues and local `tasks/` files. Unlike the previous version which **summarized** raw messages (BUG: Phase 3 Step 2 had vague "inject translated context" language that allowed LLMs to paraphrase and discard the original text), this SOP enforces:

- **Zero-summarization**: raw Persian (or any original language) text is preserved verbatim
- **Bilingual task files**: original message + complete English translation
- **Prompt refactoring**: loads `prompt-refactor` skill to generate an enhanced prompt from the raw text
- **Codebase correlation**: autonomously searches the codebase for files relevant to the described bug/feature
- **Interactive cycle**: asks Manager for approval → generates tasks → optionally creates GitHub issues → replies to Telegram

## Root Cause of the Summarization Bug

The old Phase 3 Step 2 read:

> _"Inject the translated Telegram discussion context and codebase correlation."_

This was **ambiguously phrased** — it did not mandate verbatim preservation. LLMs interpret "inject context" as "extract the gist and summarize." The fix is:

1. Explicit `## Original Message (Persian)` section with the **exact raw text** — no transformation allowed
2. A separate `## English Translation` section so the original is never overwritten or merged
3. Strict `execution_rules` in the system prompt forbidding any truncation or paraphrasing

## Local State Schema (`telegram-sync.json`)

```json
{
  "config": {
    "project_name": "[Name]",
    "chat_id": "[Chat ID]",
    "topic_id": null,
    "account": null,
    "target_hashtags": ["bug", "feature", "improve"]
  },
  "last_processed_message_id": 0,
  "processed_ids": [],
  "sync_registry": {}
}
```

## Detailed Workflow

### Phase 0: Load Mandatory Skills

Before any Telegram fetching, you MUST load these skills:

```markdown
1. Load `task-generator` skill — ensures task files use the correct template with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
2. Load `prompt-refactor` skill — will be used in Phase 3 to generate the `## Refactored Prompt` section.
```

Use the `skill` tool for each. If loading fails, HALT and report the error.

### Phase 1: Context Fetch & Deep Crawling

1. Read `telegram-sync.json` at the project root to get `config.chat_id`, `config.topic_id`, `config.account`, and `last_processed_message_id`.
2. Call `telegram_get_history` (with `account` if set, limit=100). This returns messages from ALL forum topics — Telegram has no server-side topic filter. **You MUST client-filter** to `reply_to == config.topic_id` OR walk the `reply_to` chain via `telegram_get_message_context` until you reach the topic root `config.topic_id`. Only messages whose `reply_to` chain terminates at `config.topic_id` belong to this project. Then additionally filter for `id > last_processed_message_id`.
3. **Candidate Selection:** Identify messages containing `target_hashtags` from the *topic-filtered* set. Also identify messages without hashtags that strongly resemble bug reports or feature requests.
4. **Deep Context:** For every selected candidate, check `reply_to_message_id`. If it exists, call `telegram_get_message_context` to fetch the parent message. Merge the parent message (the "what") with the child message (the "intent").

**CRITICAL — Message Integrity Rule:** Store the raw message text in a variable `RAW_TEXT` immediately after fetching. You MUST NOT modify, trim, or summarize this value at any point. Use it verbatim in Phase 3.

### Forum Topic Targeting (Critical)

This MCP implementation does **NOT** expose a `topic_id` parameter. Forum topics are identified by the `reply_to` field:

- **Reading messages from a specific topic:** Call `telegram_get_history(chat_id=config.chat_id, limit=100, account=config.account)`. It returns messages from all topics. **Filter results by `reply_to`** — direct replies have `reply_to == config.topic_id` (e.g., `458` = Cognitive Lead, `455` = other project, `1` = General). For nested replies, walk the chain via `telegram_get_message_context` recursively until you hit the topic root `MessageActionTopicCreate`; discard messages whose chain terminates at `455`/`1`/`null`.
- **Sending a message to a specific topic:** You MUST use `telegram_reply_to_message` with `message_id` set to `config.topic_id`. Never post topic confirmations to General.
- **MANDATORY per `.opencode/memory/telegram-sync/topic-scoped-sync-workflow.md`:** `config.topic_id` defines the ONLY channel to sync. NEVER fetch/scan group-wide history.

### Phase 2: Manager Approval

1. Use the `question` tool to present the identified candidates to the Manager.
2. For each candidate, show:
   - Message ID
   - Snippet of the raw text (first 200 chars to identify it)
   - Detected type (bug/feature/improve)
   - Reply parent context (if any)
3. Ask: _"Which of these candidates should be synced? (Provide the Message IDs, or state 'All')"_
4. Also ask: _"Should GitHub issues be created for these? (yes/no)"_
5. Only proceed with the approved candidates.

Store the Manager's GitHub preference in a variable `GH_ENABLED` (true/false).

### Phase 3: Task Generation & Automation (Per Approved Candidate)

For **each** approved candidate, execute the following steps **strictly in order**:

> **TASK-GENERATOR MIRROR MANDATE:** Task creation MUST mirror `task-generator` exactly: same ID discovery command, same duplicate-title check, same duplicate-ID check, same collision check, same canonical template, and same `## Definition of Done` block. Do NOT maintain divergent logic — if the `task-generator` skill's workflow changes, mirror those changes here.

---

**0. Mirror Checks (from task-generator):**

Before writing the task file, run the same guards the `task-generator` skill runs:

```bash
# Duplicate-title check
grep -rhn "^# Task [0-9][0-9]*:" tasks/ | sort | uniq -d
# Duplicate-ID check (active Kanban dirs only — archive never blocks)
find tasks/backlog tasks/in-progress tasks/qa tasks/completed -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort | uniq -d
# Collision check
ls tasks/backlog/${NEXT_ID}-*.md 2>/dev/null
```

If any check returns output, HALT and report the collision. Do NOT overwrite files. Archive is a historical record and MUST NOT be included in the blocking duplicate-ID check. If archive duplicates are discovered separately, report them as a warning only, never HALT task creation. Then confirm the generated task file includes the same `## Definition of Done` block as `task-generator` (Build/Test/Lint exit 0, `lint_task_file` passes, `CHANGELOG.md` via Parse-Then-Append, `verification-before-completion` evidence).

---

**1. Determine Next Task ID:**

Run this bash command (searches across all Kanban subdirectories):

```bash
NEXT_ID=$(find tasks/ -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ] 2>/dev/null; then NEXT_ID="01"; fi
printf "%02d\n" $NEXT_ID
```

---

**2. Generate English Translation:**

Using the `RAW_TEXT` (the verbatim original message, which may be Persian or any language), produce a complete English translation. Store it in a variable `EN_TRANSLATION`.

---

**3. Load & Run Prompt Refactor (The Omni-Channel Filter):**

The `prompt-refactor` skill should already be loaded (from Phase 0). Use it as the omni-channel filter: pass the `RAW_TEXT` (which may be Farsi) to it so it translates the text to English, expands the architectural intent, and generates an enhanced "Max Power" prompt. Store the output in a variable `REFACTORED_PROMPT`.

The refactored prompt MUST include the 5 XML blocks:

- `<role>`
- `<system_context>`
- `<agentic_reasoning>`
- `<constraints>` or `<execution_rules>`
- `<output_format>`

---

**4. Search Codebase for Relevant Context:**

Use codebase exploration tools to find files related to the bug/feature described in the `RAW_TEXT`. Execute searches in this order:

```markdown
1. grep for key technical terms from the message across the codebase
2. glob for likely file patterns (e.g., if the bug mentions "sync" → `**/*sync*`)
3. Read the top 2-3 most relevant files to extract key excerpts
```

Store the results as `CODEBASE_CONTEXT` — a list of file paths with brief relevant excerpts.

---

**5. Generate Your AI Analysis & Opinion:**

Form an architectural diagnosis:

- What is the root cause of the issue described?
- What is the recommended fix?
- What files need to change?
- What are the risks?

Store as `AI_OPINION`.

---

**6. Generate Local Task File:**

Create `tasks/backlog/{NEXT_ID}-hyphenated-title.md` using the **unified canonical template** from the `task-generator` skill, with `**Source:** telegram`. Do NOT define a separate inline template — the `task-generator` skill is the single source of truth for the file structure.

Populate the telegram variant (`## Source Context` → Variant B) by filling these fields:

- `## Goal` — **MANDATORY.** Derive a one-line goal from the `RAW_TEXT` before writing the file.
- `## Acceptance Criteria` — **MANDATORY.** Derive 2-3 concrete, verifiable conditions from the Telegram message's intent before writing the file.
- `## Original Message ({LANGUAGE})` — `{RAW_TEXT}` — **verbatim, zero changes.**

  **RULE:** The `## Original Message` section MUST contain the exact text from Telegram. If the text is Persian, the section header is `## Original Message (Persian)`. If Arabic, `## Original Message (Arabic)`, etc. If the language is unknown, use `## Original Message (Raw)`.

- `## English Translation` — `{EN_TRANSLATION}`
- `## Refactored Prompt` — `{REFACTORED_PROMPT}`
- `## Relevant Code Context` — `{CODEBASE_CONTEXT}`
- `## AI Analysis & Opinion` — `{AI_OPINION}`

`## Local TODOs` MUST be populated with at minimum:

```markdown
- [ ] Initial codebase exploration
- [ ] Verify functionality
```

---

**7. Create GitHub Issue (Optional):**

Only if `GH_ENABLED` is true:

```bash
cat > /tmp/gh-issue-body.md << 'EOF'
## Original Message
{RAW_TEXT}

## English Translation
{EN_TRANSLATION}

## AI Analysis
{AI_OPINION}

---
Migrated from Telegram. See local task file for details.
EOF

GH_URL=$(gh issue create \
  --title "{Task Title}" \
  --body-file /tmp/gh-issue-body.md \
  --label "telegram-sync")
rm -f /tmp/gh-issue-body.md
echo "GH_URL=$GH_URL"
```

If `GH_ENABLED` is false, set `GH_URL="Not created (skipped)"`.

---

**8. Update State Deterministically (The Updater Script):**

Create a temporary file named `update_sync.py` with the exact code below:

```python
import json, sys, os

msg_id = int(sys.argv[1])
task_file = sys.argv[2]
gh_issue_url = sys.argv[3]
issue_type = sys.argv[4].upper()

file_path = 'telegram-sync.json'
with open(file_path, 'r') as f:
    data = json.load(f)

data['last_processed_message_id'] = max(data.get('last_processed_message_id', 0), msg_id)

if msg_id not in data.get('processed_ids', []):
    data.setdefault('processed_ids', []).append(msg_id)
    data['processed_ids'].sort()

data.setdefault('sync_registry', {})[str(msg_id)] = {
    "task_file": task_file,
    "gh_issue": gh_issue_url,
    "type": issue_type
}

with open(file_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Successfully updated registry for msg {msg_id}")
```

Run it via Bash, passing the arguments, then delete it:

```bash
python3 update_sync.py "{MSG_ID}" "tasks/backlog/{NEXT_ID}-title.md" "$GH_URL" "{TYPE}"
rm update_sync.py
```

---

**9. Reply in Telegram:**

Call `telegram_reply_to_message` with:

```
✅ Task synced successfully.
📁 Local File: tasks/backlog/{NEXT_ID}-title.md
🌐 GitHub Issue: {GH_URL}
📝 Type: {BUG|FEATURE|IMPROVE}
```

---

### Phase 4: Mark Non-Actionable Messages

Once all approved tasks are generated, update `last_processed_message_id` to the highest message ID observed in the batch so skipped messages are not fetched again. Create a short Python script similar to Phase 3 Step 8 that updates `last_processed_message_id` and appends the skipped IDs to `processed_ids`.

### Phase 5: Return Control

After the entire cycle completes, output exactly:

```
Task ready. Manager, please copy the contents of tasks/backlog/{NEXT_ID}-task.md and send it back to the Orchestrator Brain for review.
```

## Data Integrity Guarantees

| Risk                            | Mitigation                                                                                                                                                                         |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LLM summarizes raw text         | `## Original Message` is declared as verbatim; the system prompt for the task-generation LLM MUST include "Do NOT summarize, paraphrase, or truncate the Original Message section" |
| Persian text gets corrupted     | The raw text is stored immediately on fetch and never re-encoded; the task file is written in UTF-8                                                                                |
| Codebase search misses context  | Three-pass search strategy (grep → glob → read) with fallback: if grep yields 0 results, broaden the search terms                                                                  |
| State file has concurrent edits | Single-threaded Python updater script with atomic `json.dump` write                                                                                                                |
| GitHub issue creation fails     | `GH_URL` gracefully defaults to `"Failed to create"`; the task file and Telegram reply still complete                                                                              |
