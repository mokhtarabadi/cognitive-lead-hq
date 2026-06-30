---
name: telegram-issue-sync
description: Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.
---

# Telegram Issue Sync & Discussion Crawler SOP

## Purpose
Syncs actionable Telegram messages into GitHub Issues and local `tasks/` files. It features deep "Intent Parsing" (crawling parent/child replies) and uses a deterministic Python script to mutate the `telegram-sync.json` state, ensuring zero data loss or LLM hallucination during JSON updates.

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

### Phase 1: Context Fetch & Deep Crawling
1. Read `telegram-sync.json` at the project root to get `config.chat_id`, `config.topic_id`, `config.account`, and `last_processed_message_id`.
2. Call `telegram_get_history` (with `account` if set, limit=100) and filter for messages where `id > last_processed_message_id`.
3. **Candidate Selection:** Identify messages containing `target_hashtags`. *Crucially, also identify any messages without hashtags that strongly resemble bug reports or feature requests.*
4. **Deep Context:** For every selected candidate, check `reply_to_message_id`. If it exists, call `telegram_get_message_context` to fetch the parent message. Merge the parent message (the "what") with the child message (the "intent").

### Phase 2: Manager Approval
1. Use the `question` tool to present the identified candidates to the Manager.
2. Ask: *"Which of these candidates should be synced? (Provide the Message IDs, or state 'All')"*
3. Only proceed with the approved candidates.

### Phase 3: Task Generation & Automation (Per Approved Candidate)
For *each* approved candidate, execute the following steps strictly in order:

**1. Determine Next Task ID:**
Run this bash command to calculate the next task prefix:
```bash
NEXT_ID=$(ls tasks/ | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
if [ -z "$NEXT_ID" ]; then NEXT_ID="01"; fi
printf "%02d\n" $NEXT_ID
```

**2. Generate Local Task File:**
Create `tasks/{NEXT_ID}-hyphenated-title.md` utilizing the standard project template (`<!-- BEGIN_GIT_DIFF -->`, etc.). Inject the translated Telegram discussion context and codebase correlation.

**3. Create GitHub Issue:**
Run the GitHub CLI to create the issue and capture the URL.
```bash
GH_URL=$(gh issue create --title "{Task Title}" --body "Migrated from Telegram. See local task file for details." --label "telegram-sync")
echo "GH_URL=$GH_URL"
```

**4. Update State Deterministically (The Updater Script):**
Create a temporary file named `update_sync.py` with the exact code below.
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
python3 update_sync.py "{MSG_ID}" "tasks/{NEXT_ID}-title.md" "$GH_URL" "{TYPE}"
rm update_sync.py
```

**5. Reply in Telegram:**
Call `telegram_reply_to_message(chat_id=chat_id, message_id=MSG_ID, text="✅ Task synced successfully.\n📁 Local File: tasks/{NEXT_ID}-title.md\n🌐 GitHub Issue: $GH_URL", account=account)`.

### Phase 4: Mark Non-Actionable Messages
Once all approved tasks are generated, you must update `last_processed_message_id` to the highest message ID you observed in the batch so they are not fetched again. Create a short python script similar to Phase 3 to just update `last_processed_message_id` and append the skipped IDs to `processed_ids`.
