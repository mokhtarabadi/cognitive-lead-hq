# Language Policy: English Inside, Requested Language Outside

## Core Rule

Non-English input is translated to technical English first. Execution runs on the English version only. Voice-to-text normalization stays first before translation.

Internal reasoning, task files, evidence, logs, and ALL Brain communication stay English with no exceptions. Only the Manager-facing handoff may use the requested language.

## Translation Gate by Complexity

Complex or multi-intent non-English input uses Brain-internal structured expansion to produce constrained technical English, and only Hands loads the prompt-refactor skill via the skill tool.

Short clear non-English input uses lightweight inline translation to technical English.

No blanket skill call per message. Gate by complexity every time.

## Detection

Detect output language per message, never pin to a session default. When no explicit request is detected in that message, fall back to the deployment default.

Mixed input executes in English and answers in the requested language for that message.

## Inside English

The following stay English always for auditability: reasoning traces, task files, verification evidence, logs, code comments used as provenance, Brain turns, and tool payloads.

A non-English quote inside a task file is verbatim evidence only, never the answer.

## Technical Terms Stay English (Technical-Terms rule)

Inside non-English handoffs, technical terms stay in English with no transliteration into the requested language. Keep in English: file paths such as `tasks/qa/example.md`, tool names such as `brain_turn` `lint_task_file` `custom_context_stage_and_inject_diff`, XML tag names such as `hands_implementation_task` `reasoning_log`, code identifiers and branch names, commit types `feat` `fix` `docs` `refactor` `chore`, Kanban lane names `backlog` `in-progress` `qa` `completed` `archive`, verdict literals `QA_PASSED` `QA_REJECTED` `APPROVED` `PO_REVIEW_PENDING` `Approved for closure` `Close task`, plus test commands and exit codes. Match approval phrases as English literals only. Write non-English sentence structure around the terms and leave each term intact in backticks.

## Outside Requested Language

The final Manager-facing handoff follows the per-message requested language. Keep it short, plain, and skimmable under the Manager-Facing Output Style. Think and reason in English, render the handoff in the requested language.

## Approval Literals Guard

Approval phrases match ONLY as English literals. Never translate-then-compare.

Plan gate accepts approved in any case through the question tool path. Closure accepts only the exact phrases Approved for closure or Close task. A bare approved counts only as the next message directly answering the relayed closure question. Good, thanks, ok, yes, done, fine, looks good, emoji-only replies, and silence never count.

## Execution Binding

Translate first, then validate intent, expand requirements, check brainstorming, check clarification, check Lite Mode, and generate implementation tasks from the English version. Clarification questions use the per-message requested language. Implementation XML, tests, and evidence stay English.
