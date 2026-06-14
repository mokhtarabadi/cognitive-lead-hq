# Task 06: Implement Global Telegram Issue Sync Skill

**Type:** feature
**Status:** completed

## Goal

Implement the global, optional Telegram-to-GitHub sync skill template (`telegram-issue-sync`) inside `skill-templates/` with advanced non-tagged conversation crawling and automatic Telegram replies on task completion.

## Manager's Notes

- The skill must be strictly optional for projects.
- Implement non-tagged discussion crawling to capture context from replies.
- Synchronize with the CHANGELOG.

## Local TODOs

- [x] Create skill-templates/telegram-issue-sync/SKILL.md
- [x] Integrate optional onboarding logic
- [x] Integrate non-tagged reply/context crawling logic
- [x] Integrate end-of-task completion Telegram notification sequence
- [x] Update CHANGELOG.md

## OpenCode Execution Log & Reasoning

- Added the complete `telegram-issue-sync` skill under templates.
- Fully modeled the dual-flow sync: "Pull" (Telegram -> Local/GitHub) and "Push" (Local Completion -> Telegram Reply).
- Modeled the "Optional" nature using existence of local `telegram-sync.json` state file.
- Designed the advanced Regex/Metadata-driven thread discussion crawling that parses non-tagged messages in Supergroup topics.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

````diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b20048c..0d65eee 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -124,6 +124,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ### Added

+- **`skill-templates/telegram-issue-sync/SKILL.md`** — new global, optional Agent Skill template for syncing Telegram group topics with local tasks and GitHub issues, featuring advanced non-tagged discussion thread crawling.
+- **Task 06** — local task file tracking the synchronization skill implementation.
 - **Mandatory Code Documentation constraint** in `system-prompt.md` — OpenCode is now required to write docstrings on all public functions/classes, inline comments on non-obvious logic, and README/header comments for new modules. Enforced via both `<constraints>` and the `<opencode_implementation_task_template>` execution phase.
 - **`system_version` tag** added to `system-prompt.md` at version 5.2.0 for tracking system prompt iterations.
 - **`skill-templates/doc-coauthoring/SKILL.md`** — Anthropic's doc-coauthoring skill: a structured 3-stage workflow (Context Gathering, Refinement & Structure, Reader Testing) for co-authoring documents with AI.
diff --git a/skill-templates/telegram-issue-sync/SKILL.md b/skill-templates/telegram-issue-sync/SKILL.md
new file mode 100644
index 0000000..f255e4d
--- /dev/null
+++ b/skill-templates/telegram-issue-sync/SKILL.md
@@ -0,0 +1,80 @@
+---
+name: telegram-issue-sync
+description: Optional, pure agentic sync of Telegram supergroup topics into local task files and GitHub issues, featuring non-tagged conversation crawling.
+---
+
+# Telegram Issue Sync & Discussion Crawler SOP
+
+## Purpose
+
+Provides an optional, highly advanced workflow for syncing actionable Telegram supergroup messages into GitHub Issues and local task files without custom Python scripts, utilizing existing Telegram MCP and `gh` CLI tools. It features "Thread Crawling" to pull in non-tagged messages for discussion context.
+
+## Activation (Strictly Optional)
+
+- This skill is **OPTIONAL**. Do NOT execute or force setup unless:
+  - A `telegram-sync.json` file already exists at the project root.
+  - **OR** the Manager explicitly commands a sync (e.g., "sync telegram", "@explore search telegram issues").
+  - If neither condition is met, silently skip this skill entirely during initialization or normal tasks.
+
+## Local State Schema (`telegram-sync.json`)
+
+Stored at project root to track local configuration and message states:
+
+```json
+{
+  "config": {
+    "project_name": "[Name]",
+    "chat_id": "[Chat ID]",
+    "topic_id": [Topic ID],
+    "target_hashtags": ["bug", "feature", "improve"]
+  },
+  "last_processed_message_id": 0,
+  "processed_ids": [],
+  "sync_registry": {}
+}
+```
+
+## Detailed Workflow
+
+### Phase 1: Verification & Optional Onboarding
+
+1. Check for `telegram-sync.json` at project root.
+2. If missing AND the command was explicitly requested:
+   - Run the `question` tool to interactively ask the Manager for: `project_name`, `chat_id`, `topic_id`, and `target_hashtags`.
+   - Create the `telegram-sync.json` file with the collected config, setting `last_processed_message_id` to `0` and initializing `processed_ids` and `sync_registry`.
+3. If missing and NOT explicitly requested:
+   - Abort this skill immediately. Do not prompt the user.
+
+### Phase 2: Candidate Fetch & Discussion Crawling
+
+1. **Fetch Message History:** Call the Telegram MCP `telegram_get_history` (or equivalent tool) using the `chat_id` and `topic_id` from the config.
+2. **Primary Filter (Actionable Items):** Filter for messages where:
+   - Message ID > `last_processed_message_id`
+   - Message text contains any of the target hashtags (e.g., `#bug`, `#feature`, `#improve`).
+3. **Secondary Filter (Discussion & Non-tagged Replies):** For each matched candidate:
+   - Retrieve all replies and subsequent discussions. Use the Telegram tools to search for messages replying to this candidate (`reply_to_message_id` matching candidate's `id`).
+   - Fetch neighboring messages around the candidate's timestamp (+/- 10 minutes) in the same topic. Extract the non-tagged dialogue, questions, and decisions made by teammates to capture the full context.
+4. **Translation & Title Generation:**
+   - Translate any Persian messages (and their crawl-extracted replies) into clear English.
+   - **Rule 8 Compliance:** Generate a professional, concise title (<60 chars) prefixed with 'Bug: ', 'Feature: ', or 'Improve: '.
+5. **Codebase Correlation:** Scan the workspace using `custom_context_extract_signatures` with keywords from the translated discussion to identify target files.
+
+### Phase 3: Manager Approval & Multi-Sync
+
+1. Present the candidates and their crawled discussions to the Manager using the `question` tool.
+2. For each approved candidate:
+   - **Local Task:** Generate `tasks/XX-slug.md` (using your task template) with a dedicated `## Telegram Discussion Context` section containing the crawled non-tagged discussion.
+   - **GitHub Issue:** Run the non-interactive `gh` CLI:
+     `gh issue create --title "[Sync] Generated Title" --body "Detailed Body with Crawled Discussion"`
+     Extract the generated GitHub issue number from the output URL.
+   - **State Save:** Update `telegram-sync.json` local state (append to `processed_ids`, update `last_processed_message_id`, and add msg ID to `sync_registry` mapping).
+
+### Phase 4: Closing the Loop (Completion Telegram Reply)
+
+1. When a task file inside `tasks/` is marked as completed or successfully approved by the Code Reviewer:
+2. Read `telegram-sync.json` to check if the completed task file path exists in `sync_registry`.
+3. If a match is found:
+   - Extract the corresponding Telegram `msg_id` from the registry map.
+   - Call your Telegram MCP tools (`telegram_send_message` or equivalent) to reply directly to the original `msg_id` inside the supergroup topic.
+   - **Notification Template:**
+     _"The bug/feature reported in this thread has been successfully resolved and committed under Local Task XX (GitHub Issue #YY). Thank you!"_
diff --git a/tasks/05-v53-ultimate-factual-diff-architecture.md b/tasks/05-v53-ultimate-factual-diff-architecture.md
index 83a4af2..7829e5f 100644
--- a/tasks/05-v53-ultimate-factual-diff-architecture.md
+++ b/tasks/05-v53-ultimate-factual-diff-architecture.md
@@ -57,10 +57,10 @@ The V5.3.0 upgrade introduces two new MCP tools on the custom context server:
 2. **`stage_and_inject_diff`** — Automates the end-of-task finalization sequence: stages all changes via `git add .`, extracts the factual `git diff --staged`, and injects it into the task file's `<!-- BEGIN_GIT_DIFF -->
 ```diff
 diff --git a/.opencode/skills/code-search/SKILL.md b/.opencode/skills/code-search/SKILL.md
-index 5fce73b..d4c8d6e 100644
+index 5fce73b..00dcdb9 100644
 --- a/.opencode/skills/code-search/SKILL.md
 +++ b/.opencode/skills/code-search/SKILL.md
-@@ -11,10 +11,10 @@ You are the Executor. Your job is to extract codebase context so the Manager can
+@@ -11,11 +11,11 @@ You are the Executor. Your job is to extract codebase context so the Manager can

  ## Discovery Workflow

@@ -70,10 +70,12 @@ index 5fce73b..d4c8d6e 100644
 +2. **Extract Signatures (Prevent Context Bloat):** Before reading full files, call the `custom_context_extract_signatures` MCP tool on the target files to understand their structural map (classes/functions) without loading massive file bodies.
  3. **Target Files:** Analyze the ASCII tree to identify the exact files relevant to the Manager's request.
 -4. **Compile Report:** Call the `read_source_files` MCP tool, passing the list of targeted file paths. This tool will safely read the files (respecting `.gitignore`) and compile them into a single Markdown file inside the `context-reports/` directory.
+-5. **Halt and Handover:** Once the `read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
 +4. **Compile Report:** Call the `custom_context_read_source_files` MCP tool, passing the list of targeted file paths. This tool will safely read the files (respecting `.gitignore`) and compile them into a single Markdown file inside the `context-reports/` directory.
- 5. **Halt and Handover:** Once the `read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
++5. **Halt and Handover:** Once the `custom_context_read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
  6. **Output Message:** Output the following exact message to the Manager:
     > "✅ Discovery complete. I have compiled the context report here: `[INSERT_FILE_PATH]`.
+    > **Manager:** Please upload this file to AI Studio for the Orchestrator's review."
 diff --git a/AGENTS.md b/AGENTS.md
 index d037887..d5181cc 100644
 --- a/AGENTS.md
@@ -99,10 +101,10 @@ index 0ca71aa..999ca30 100644

  ## Resolution Protocol
 diff --git a/skill-templates/code-search/SKILL.md b/skill-templates/code-search/SKILL.md
-index 5fce73b..d4c8d6e 100644
+index 5fce73b..00dcdb9 100644
 --- a/skill-templates/code-search/SKILL.md
 +++ b/skill-templates/code-search/SKILL.md
-@@ -11,10 +11,10 @@ You are the Executor. Your job is to extract codebase context so the Manager can
+@@ -11,11 +11,11 @@ You are the Executor. Your job is to extract codebase context so the Manager can

  ## Discovery Workflow

@@ -112,10 +114,12 @@ index 5fce73b..d4c8d6e 100644
 +2. **Extract Signatures (Prevent Context Bloat):** Before reading full files, call the `custom_context_extract_signatures` MCP tool on the target files to understand their structural map (classes/functions) without loading massive file bodies.
  3. **Target Files:** Analyze the ASCII tree to identify the exact files relevant to the Manager's request.
 -4. **Compile Report:** Call the `read_source_files` MCP tool, passing the list of targeted file paths. This tool will safely read the files (respecting `.gitignore`) and compile them into a single Markdown file inside the `context-reports/` directory.
+-5. **Halt and Handover:** Once the `read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
 +4. **Compile Report:** Call the `custom_context_read_source_files` MCP tool, passing the list of targeted file paths. This tool will safely read the files (respecting `.gitignore`) and compile them into a single Markdown file inside the `context-reports/` directory.
- 5. **Halt and Handover:** Once the `read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
++5. **Halt and Handover:** Once the `custom_context_read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
  6. **Output Message:** Output the following exact message to the Manager:
     > "✅ Discovery complete. I have compiled the context report here: `[INSERT_FILE_PATH]`.
+    > **Manager:** Please upload this file to AI Studio for the Orchestrator's review."
 diff --git a/system-prompt.md b/system-prompt.md
 index b3395ba..5133680 100644
 --- a/system-prompt.md
````

<!-- END_GIT_DIFF -->
