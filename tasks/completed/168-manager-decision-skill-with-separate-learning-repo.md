# Task 168: Manager-Decision Skill With Separate Learning Repo

**File:** `tasks/completed/168-manager-decision-skill-with-separate-learning-repo.md`
**Source:** telegram
**Type:** feature
**Status:** closed

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

- [x] Initial codebase exploration
- [x] Define decision-repo schema and redaction policy
- [x] Verify functionality

## Acceptance Criteria

- [x] Decision-repo schema defined with verbatim-quote + linkage fields
- [x] Skill/MCP/plugin invocation contract specified with per-session example
- [x] Sample-evolution loop includes human review gate before identity update

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with "mcp[cli]>=1.0,<2.0" --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin -- pytest tests/ -q` (repo root)
- **Expected result:** Full suite green: 55 pre-existing + 32 persona + 14 new decision-server tests = 101 passed; `py_compile` clean; `opencode.json` + schema JSON valid; both decision scripts exit 0 on empty repo
- **Actual result:** `101 passed, 8 warnings in 1.10s` (pre-existing pathspec notices); `COMPILE-OK`; `JSON-OK`; `validate-exit:0`; `compile-exit:0`
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Verbatim manager statements leak sensitive reasoning; auto-evolution drifts identity.
- **Rollback plan:** Keep decision repo append-only with revertible PRs; disable auto-promotion, keep manual review.

---

## Execution Log & Reasoning

Micro-task checklist (Steps 1–8, in order):

- [x] **Step 1:** `git mv tasks/backlog/168-*.md tasks/in-progress/168-*.md` (clean tree); header → `tasks/in-progress/...`, status → `in-progress`.
- [x] **Step 2:** Scaffolded `packages/cognitive-lead-decisions/` — `schema/decision.schema.json` (`decision_id` DEC-YYYYMMDD-NNN, `timestamp`, `project_name`, `verbatim_quote` original+English, `extracted_decision` summary/category/rationale/alternatives/tradeoffs, `redaction_verified`), `samples/manager_profile.md` (curated baseline: composition-over-inheritance, FastMCP-over-daemons, append-only, hard gates; generated section marked DO-NOT-EDIT), `scripts/compile_profile.py` (prints review draft to stdout, never writes the sample), `scripts/validate_decisions.py` (dependency-free structural validator, exit codes for CI).
- [x] **Step 3:** Implemented `mcp-decision-server/` — `redactor.py` (`sanitize_text` for sk-/ghp-/AIzaSy-/Bearer-/private-IP/credential patterns, `verify_clean` with a lookahead so `[REDACTED]` markers never false-positive; idempotent fixed point), `server.py` (FastMCP `ManagerDecisions`, `DECISION_REPO_PATH` with in-repo fallback; 5 tools: extract/record/query/profile/propose; lazy litellm; record path scrubs → verifies → validates → writes JSON+MD under `decisions/YYYY/MM/` → regenerates INDEX.md; propose runs the compile script in a subprocess and returns DRAFT_READY/EMPTY/ERROR without touching the sample).
- [x] **Step 4:** Created `skill-templates/manager-decision/SKILL.md` (frontmatter convention per project-memory template; triggers, extraction/consultation/evolution workflows, redaction rules, per-session invocation example; no legacy `OpenCode Execution Log` wording).
- [x] **Step 5:** Registered `manager_decisions` in `opencode.json` in repo list-form (`uv run mcp-decision-server/server.py`, 120s timeout — grounded deviation from the XML's stale `python`/`args` shape, same as Task 167) + 5 tool permission allows.
- [x] **Step 6:** `agents/cognitive-executor.md` — `manager-decision` row in the Skill Auto-Loading Matrix; Context Bootstrapping now consults `query_manager_decisions` + profile injection for architectural ambiguities.
- [x] **Step 7–8:** `tests/test_decision_server.py` — 14 tests (redactor ×5, record/validate ×4, query/profile/propose ×3, extract ×2 with stubbed litellm, all repo I/O in tmp dirs). Full suite **101 passed** (55 + 32 + 14), exit 0.

Fix during testing: `extract_session_decisions` imported litellm before the missing-transcript check, breaking its own graceful-empty contract under a bare interpreter — moved the existence check first (also cheaper at runtime).

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ea9a862dee286b9e33f8981afd4991504179cc29`
<!-- END_GIT_DIFF -->
