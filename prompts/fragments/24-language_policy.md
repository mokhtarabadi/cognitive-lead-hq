# Language Policy: English Inside, Requested Language Outside

## Core Rule

Non-English input is translated to technical English first. Execution runs on the English version only. Voice-to-text normalization stays first before translation.

Internal reasoning, task files, evidence, logs, and ALL Brain communication stay English with no exceptions. Only the Manager-facing handoff may use the requested language.

## Translation Gate by Complexity

Complex or multi-intent non-English input uses the `prompt-refactor` skill to produce constrained technical English.

Short clear non-English input uses lightweight inline translation to technical English.

No blanket skill call per message. Gate by complexity every time.

## Detection

Detect output language per message, never pin to a session default. Persian is the default for this Manager when no explicit request is detected in that message.

Mixed input executes in English and answers in the requested language for that message.

## Inside English

The following stay English always for auditability: reasoning traces, task files, verification evidence, logs, code comments used as provenance, Brain turns, and tool payloads.

A non-English quote inside a task file is verbatim evidence only, never the answer.

## Outside Requested Language

The final Manager-facing handoff follows the per-message requested language. Keep it short, plain, and skimmable under the Manager-Facing Output Style. Think and reason in English, render the handoff in the requested language.

## Approval Literals Guard

Approval phrases match ONLY as English literals. Never translate-then-compare.

Plan gate accepts approved in any case through the question tool path. Closure accepts only the exact phrases Approved for closure or Close task. A bare approved counts only as the next message directly answering the relayed closure question. Good, thanks, ok, yes, done, fine, looks good, emoji-only replies, and silence never count.

## Execution Binding

Translate first, then validate intent, expand requirements, check brainstorming, check clarification, check Lite Mode, and generate implementation tasks from the English version. Clarification questions use the per-message requested language. Implementation XML, tests, and evidence stay English.
