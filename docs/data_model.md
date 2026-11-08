# Cognitive Lead AI HQ — Data Model

## Overview

This document defines the data schemas, file formats, and object relationships for the Cognitive Lead AI multi-agent system HQ.

## Kanban Task File Format

Task files are Markdown files stored in `tasks/{backlog,in-progress,qa,completed,archive}/`. Each file follows this structure:

### Frontmatter
```markdown
# Task [NN]: [Title]

**File:** `tasks/<lane>/<filename>.md`
**Source:** [orchestrator|telegram|manager]
**Type:** [bug|improvement|feature]
**Status:** [open|in-progress|qa|completed|closed]
**Estimate:** [e.g., 4h]
**Deadline:** [YYYY-MM-DD]
**Depends on:** [task IDs]
**Milestone:** [milestone name]
**Started:** [ISO-8601 UTC]
**Submitted:** [ISO-8601 UTC]
**Finished:** [ISO-8601 UTC]
```

### Body Sections
- `## Goal` — mandatory, one-line goal
- `## Manager's Notes` — specific notes/constraints
- `## Local TODOs` — checklist of steps
- `## Acceptance Criteria` — what must be true for done
- `## Verification Evidence` — test command, expected/actual result, exit code
- `## Definition of Done` — unconditional checklist
- `## Risk & Rollback` — risk assessment and rollback plan
- `## Execution Log & Reasoning` — technical changes and reasoning
- `## Factual Git Diff` — auto-injected by `custom_context_stage_and_inject_diff`

## Session Data

### Transcript
Location: `tasks/.sessions/<session_id>/transcript.jsonl`
Format: JSONL, one entry per `brain_turn` call. Each entry contains:
- `task_id`, `session_id`
- `user_prompt`, `output`
- `xml_blocks` (extracted XML)
- `status` (XML_EXTRACTED or REPORT)
- `model`, `response_id`

### Brain Output Artifacts
Location: `tasks/.sessions/<session_id>/brain_outputs/<response_id>_<uuid>.json`
Format: JSON with:
- `task_id`, `session_key`, `response_id`
- `created_at_utc` (ISO-8601 UTC)
- `truncated` (boolean)
- `byte_counts` (output + xml_blocks byte sizes)
- `xml_blocks` (array of extracted XML strings)
- `full_output` (complete raw output including XML)
- `address` (repo-relative POSIX path)

Retention: 50 files / 5 MB per session, oldest-first by mtime.

### Session Ledger
Location: `tasks/.sessions/<session_id>/session_ledger.jsonl`
Format: JSONL, append-only event log.

## Prompt Cache Split
The `brain_turn` result includes a `prompt_cache_split` object:
- `schema_version`: 2
- `split_boundary`: "after_system_bundle_task_attach"
- `static_prefix_sha256`: SHA-256 of the static prompt prefix
- `dynamic_suffix_sha256`: SHA-256 of the dynamic suffix

## Goal State (External Plugin)
Location: `.opencode/goals/<session-id>.json` + `.evidence.json` sidecar
- Per-session, not shared across sessions
- Scratch data only, never replaces Kanban state
- Evidence gate: every criterion needs one existing file + passing test

## Memory System
Location: `.opencode/memory/` (namespaced Markdown shards)
Index: `.opencode/memory/index.md` (auto-generated)
- Namespaces: architecture, project, quirks, workflows, telegram-sync, etc.
- Each shard: YAML frontmatter + content
- Auto-rebuilt after store/delete operations

## Context Reports
Location: `context-reports/`
- Tree reports: `tree_report_<timestamp>_<uuid>.md`
- Context reports: `context_report_<timestamp>_<uuid>.md`
- Discovery reports: various descriptive names
