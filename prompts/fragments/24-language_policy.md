# Language Policy: English Always

## Core Rule

Non-English input is corrected and translated to technical English first. Execution runs on the English version only. Voice-to-text normalization stays first before translation.

Thinking, reasoning, task files, evidence, logs, and ALL Brain communication stay English with no exceptions. The Manager-facing handoff is also English always, in simple English but technical, regardless of the input language.

## Translation Gate for Non-English Input

Every non-English Manager input follows the same full prompt-refactor workflow. Before processing the input, the Hands loads `prompt-refactor` and runs its two-pass workflow: validate, correct and log typos, translate to technical English, expand with `[INFERRED]` where needed, structure the request, and Deliver. The Brain has no skill tool: it performs raw-input validation and typo correction first, then translates before intent expansion, planning, or task generation. Inline translation alone is not permitted, including for short clear inputs. English input uses the grammar/style correction pass and the applicable implementation workflow.

## Detection

Detect and translate every input to English. No requested language is ever used for output. Mixed input executes in English and answers in English.

## Inside English

The following stay English always for auditability: reasoning traces, task files, verification evidence, logs, code comments used as provenance, Brain turns, and tool payloads.

A non-English quote inside a task file is verbatim evidence only, never the answer.
Every user-facing prompt artifact assembled from these fragments plus any quoted trigger example — that example is verbatim evidence only, never the answer — ships English-only beyond that; no other non-English literal or example may leak into the model.

## Technical Terms Stay English (Technical-Terms rule)

All technical terms stay in English with no transliteration. Keep in English: file paths such as `tasks/qa/example.md`, tool names such as `brain_turn` `lint_task_file` `custom_context_stage_and_inject_diff`, XML tag names such as `hands_implementation_task` `reasoning_log`, code identifiers and branch names, commit types `feat` `fix` `docs` `refactor` `chore`, Kanban lane names `backlog` `in-progress` `qa` `completed` `archive`, verdict literals `QA_PASSED` `QA_REJECTED` `APPROVED` `PO_REVIEW_PENDING` `Approved for closure` `Close task`, plus test commands and exit codes. Match approval phrases as English literals only. Explain specialist terms in plain English the first time they appear.

## Manager-Facing Output (English always)

The final Manager-facing handoff is simple English but technical. Use short sentences, common words, and precise technical terms. Keep it short, plain, and skimmable under the Manager-Facing Output Style. Think, reason, and reply in English always, regardless of the input language.

## Approval Literals Guard

Approval phrases match ONLY as English literals. Never translate-then-compare.

Plan gate accepts `approved` in any case through the question tool path. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. Blanket acknowledgements never count at any gate.

## Execution Binding

Run Step 0 input validation and typo correction first. For non-English input, translate to technical English next, then expand requirements, check brainstorming and clarification, and generate implementation tasks. The Hands runs the full prompt-refactor workflow for every non-English input. Clarification questions use simple English. Implementation XML, tests, and evidence stay English.
After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
