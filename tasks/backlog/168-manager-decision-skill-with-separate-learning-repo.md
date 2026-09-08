# Task 168: Manager-Decision Skill With Separate Learning Repo

**File:** `tasks/backlog/168-manager-decision-skill-with-separate-learning-repo.md`
**Source:** telegram
**Type:** feature
**Status:** open

## Source Context

## Goal

Build a manager-decision skill that extracts per-session manager decisions into a separate repo to evolve a manager-AI sample.

## Original Message (Persian)

بعد یک بخش جدید هم میشه اضافه کرد بهش منیجر دیسیژن، یک اسکیل باشه، خب؟ هر وقت فراخوانی بشه توی اون جلسه، تصمیمهایی که مدیر گرفته صحبتهایی کرده سیستم دیزاینی که کرده، همه رو یاد بگیریم توی یک ریپوی جداگانه همیشه داشته باشیم تصمیمات مدیر رو که بعداً اون نمونهی هوش مصنوعی که از مدیر ساختیم روز به روز بتونه بهبود پیدا کنه و بهتر بشه. بعد یک جای دیگه کامل یه نمونه کامل باشه بعد تصمیمات جزء دیگه نیاز به منیجر واقعی نباشه و از همون نمونه ساخته شده ایآی که از تصمیمات منیجر شکل گرفته توی سشنها استفاده بشه، مثلاً این شکل باشه، این نحو باشه که توی سشنهای مختلف خود منیجر مثلاً اون اسکیل یا ام سی پی میتونه باشه یا اسکیل میتونه باشه یا یک پلاگین برای اوپن کد باشه. صدا بزنه بعد اون سشن تصمیماتی که مدیر گرفته، مدیر گرفته شده استخراج بشه و هویت بصری ایآی منیجر یا مدیر آپدیت بشه.

#remaining

## English Translation

Then a new section can be added to it — manager decision — as a skill, okay? Whenever it is invoked in that session, the decisions the manager made, the things said, the system design done — we learn all of it and always keep the manager's decisions in a separate repo, so that later the AI sample we built from the manager can improve day by day and get better. Then somewhere else there is a complete full sample; after that, micro-decisions no longer need the real manager, and we use that built AI sample shaped from the manager's decisions in the sessions. For example it would be like this — in different sessions the manager itself, e.g., that skill or MCP, or it can be a skill or a plugin for OpenCode — it calls, then the decisions made by the manager in that session are extracted, and the visual identity of the AI manager is updated.

## Refactored Prompt

```markdown
<role>
You are an elite Knowledge Systems Architect specializing in decision-capture pipelines, skill/MCP design for OpenCode, and continual manager-AI refinement.
</role>

<system_context>
Environment: Cognitive Lead HQ + OpenCode. Requirement: a manager-decision skill (or MCP, or OpenCode plugin) invoked per session that extracts manager decisions/statements/system-designs and persists them in a separate repo, continually improving a manager-AI sample until micro-decisions no longer need the real manager. Related to Task 167 (persona commands) but scoped here to decision learning + identity update.
</system_context>

<agentic_reasoning>
Before designing, output a <reasoning_log> analyzing: (1) logical dependencies — session transcript source, extraction trigger, repo schema, sample update cadence; (2) risk assessment — privacy/leakage of manager statements, hallucinated decisions, identity drift; (3) abductive reasoning — which session signals count as decisions vs chatter; (4) precision and grounding — cite prompts/archive/17-decision_logging_mandate.md, project-memory skill, .opencode/memory structure.
</agentic_reasoning>

<constraints>
- You MUST store raw manager statements verbatim alongside extracted decisions; do NOT summarize away the source.
- You MUST define the separate repo schema (decision record fields, session linkage, versioning) before any automation.
- You MUST define the invocation contract (skill vs MCP vs plugin — pick one primary, list trade-offs).
- Do NOT auto-evolve the manager-AI sample without a review gate; identity updates require approval.
- Do NOT overlap Task 167's persona-command scope except via explicit interface.
</constraints>

<output_format>
Return: (1) repo schema + storage layout, (2) skill/MCP/plugin spec with invocation examples, (3) extraction pipeline (transcript → decisions → repo PR), (4) sample-evolution loop with review gate and identity-update rule, (5) privacy/redaction policy.
</output_format>
```

## Relevant Code Context

- `prompts/archive/17-decision_logging_mandate.md` — prior decision-logging mandate to extend.
- `.opencode/memory/*` + `project-memory` skill — existing memory shards vs new separate decision repo.
- `skill-templates/*` — template for the new manager-decision skill.
- `agents/cognitive-executor.md` — invocation point inside sessions.
- `mcp-memory-server/server.py` — existing memory MCP if MCP option chosen.

## AI Analysis & Opinion

This is the learning half of message 587's execution half: 587 moves execution into persona commands, 588 preserves the manager's judgment as training data. Recommend a decision-record schema (session id, timestamp, verbatim quote, decision, rationale, system-design refs, outcome) stored as append-only Markdown/JSON in the separate repo, with a gated promotion job that updates the manager-AI sample + visual identity. Biggest risks are privacy (manager statements persisted verbatim) and feedback loops (AI trained on its own outputs); mitigate with redaction rules and human review before sample promotion. Build after or alongside Task 167 with a shared invocation contract.

## Local TODOs

- [ ] Initial codebase exploration
- [ ] Define decision-repo schema and redaction policy
- [ ] Verify functionality

## Acceptance Criteria

- [ ] Decision-repo schema defined with verbatim-quote + linkage fields
- [ ] Skill/MCP/plugin invocation contract specified with per-session example
- [ ] Sample-evolution loop includes human review gate before identity update

## Verification Evidence

- **Test command:** TBD by implementer (e.g., decision-extraction dry run on a sample session transcript)
- **Expected result:** Decisions extracted verbatim into repo schema; sample update requires approval
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

- **Risk:** Verbatim manager statements leak sensitive reasoning; auto-evolution drifts identity.
- **Rollback plan:** Keep decision repo append-only with revertible PRs; disable auto-promotion, keep manual review.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
