# Task 152: Self-Improvement System-Prompt & Workflow Retrofit

**File:** `tasks/completed/152-self-improvement-system-prompt-workflow.md`
**Source:** telegram
**Type:** improvement
**Status:** closed

## Goal

Add a self-improvement trigger to the system-prompt/workflow that, after a long sprint/session, synthesizes session history and proposes concrete system-prompt/workflow upgrades as task-ready suggestions.

## Original Message (Persian)

ببین، یه مسئله الان به ذهنم رسید، خب؟ کاری که میشه انجام بدیم، اینه که بحث تصمیمات ادمین یا منیجر یه بررسی انجام بده ببین الان درست دقیقاً تصمیمات من رو ذخیره میکنه یا نه، این بخش. و بخش دوم یه بخش سلف ایمپروو نمیدونم حالا چه چهجوری میتونه انجام بشه، توی سیستمپرامپت اضافه کنیم، خب؟ مثلاً بعد اگه اسپرینت طولانی، بعد از مثلاً یک سیشن طولانی من اونو صدا بزنم بگم حالا نسبت به چیزهایی کارهایی که توی این سیشن انجام شده، نسبت به رفع و برگشتهایی که داشتیم، نسبت به هر چیزی که من توضیح دادم، خودت توضیح دادی، چه بهبودها و ایمپرووهایی میتونیم روی سیستمپرامپت و ورکفلو انجام بدیم. و اون شروع کنه به توضیح دادن و من نگاه کنم ببینم واقعاً هر کدومش نیاز بود، یه تسک بشه و روی سیستمپرامپتمون انجام بدیم که به یک استیت خیلی خوب برسه. یعنی حالت سلف ایمپروومنت میخوام پیادهسازی کنیم. این رو هم میخوام، آره. اینم فقط نیاز تسک بشن، یک تسک برای هر دو تاشون بنویس، کار دیگه نیاز نیست انجام بدیم.

#improve

## English Translation

Look, an issue just came to mind, okay? What we can do is: first, audit the admin/manager decisions topic — check whether my decisions are being stored correctly right now, this part. And second, a self-improvement section — I don't know exactly how it could be done — add it to the system prompt, okay? For example after a long sprint, after a long session I call it and say now regarding things done in this session, regarding fixes and back-and-forths we had, regarding anything I explained or you explained, what improvements can we make on the system prompt and workflow. And it starts explaining and I look to see which ones were really needed, create a task for each and execute on our system prompt to reach a very good state. I want to implement this self-improvement mode.

Note: This task covers **part 2** of the above message (self-improvement retrofit). Part 1 is split into Task 151.

## Refactored Prompt

<role>
You are a Staff AI Platform Architect & Meta-Learning Designer for the Cognitive Lead AI multi-agent system.
</role>

<system_context>
You operate in Cognitive Lead AI HQ — orchestration repo where `system-prompt.md` is a generated artifact assembled from `prompts/fragments/*.md` + `prompts/shared/` via `scripts/prompt-build/assemble_system_prompt.py`. The system prompt governs Orchestrator (Brain), Cognitive Executor (Hands), and sub-agents. It already contains fragments 01–20 including roles, reasoning, constraints, and lite_mode. You MUST extend it without destabilizing the assembly contract (lint, versioning, changelog sync).
</system_context>

<agentic_reasoning>
Before designing the retrofit, output a <reasoning_log> analyzing:
1. Logical dependencies — which fragments host workflow triggers, personas, and improvement gates; how session memory (goal plugin, opencode logs, task files, CHANGELOG) feeds retrospection.
2. Risk assessment — hallucinated improvements, scope creep, self-modifying loops without human approval, token bloat.
3. Abductive reasoning — why current workflow lacks compounding: no explicit post-sprint reflection trigger, no evidence-bound proposal shape.
4. Precision and Grounding — cite file:line for fragment insertion point, gate command, and output schema; ensure version bump via `<system_version>` fragment.
</agentic_reasoning>

<constraints>
- You MUST keep human-in-the-loop: self-improvement PROPOSES, Manager disposes — never auto-apply patches; output is task-ready proposals.
- You MUST make the trigger explicit and low-cost (e.g., `/reflect` or `self-improve` keyword) with an opt-in, evidence-bound report shape (findings F1..N, citations to session artifacts).
- You MUST NOT inflate system-prompt tokens > 5% — compress via fragment edits, not new verbosity.
- You MUST bump `<system_version>` and update CHANGELOG.md via Parse-Then-Append if any fragment changes.
- Do NOT hallucinate metrics — every improvement suggestion must reference concrete session evidence (task diffs, error logs, fix/revert pairs).
</constraints>

<output_format>
Deliver: (1) Design — new fragment or fragment patch (name + insert location) with trigger definition; (2) Prompt patch diff — exact markdown to insert; (3) Report schema — markdown table for findings (ID, evidence ref, proposed fragment edit, impact, risk); (4) Verification plan — `lint_task_file`, assembler dry-run, prettier check.
</output_format>

## Relevant Code Context

- `prompts/fragments/01-system_version.md` — holds `<system_version>`; bump required on any system-prompt change.
- `prompts/fragments/06-personas.md` and `prompts/fragments/08-agentic_reasoning.md` — persona/reasoning blocks where meta-cognition could attach.
- `prompts/fragments/11-execution_workflow.md` — 9-step SOP formalization; natural place for a post-sprint reflection gate.
- `scripts/prompt-build/assemble_system_prompt.py` — fragment assembler; must be re-run after edits to regenerate `system-prompt.md`.
- `system-prompt.md` — generated artifact; never edited directly.
- Search evidence: `ls prompts/fragments/` = 20 fragments; `grep -r "self-improve\|retrospective\|reflect" prompts/` currently yields no dedicated self-improvement trigger (gap).

## AI Analysis & Opinion

Intent is a compounding-advantage loop: after dense work (long sprint), the Manager invokes a reflection command; the system scans session evidence (recent `tasks/completed/*.md`, `CHANGELOG.md`, git diffs, fix/revert cycles, decision logs) and proposes 3–7 concrete system-prompt/workflow patches, each evidence-bound (file:line + before→after sketch). Manager triages: pick which become tasks.

Design recommendation: Add a small fragment (e.g., `21-self_improvement_protocol.md` or patch `11-execution_workflow.md` with a `### Self-Improvement Trigger`) defining: trigger phrase (`self-improve` / `reflect`), input contract (session window = last N closed tasks or last goal), output contract (findings F1..N with evidence refs + proposed diff + impact/risk), and guardrail (no auto-write — proposals become `tasks/backlog/*.md` via task-generator). This keeps ZAC and keeps token cost low — reflection runs only on demand, not per turn.

Risks: Over-triggering produces noise; under-constraining produces vague "improve prompts" without refs. Mitigate with explicit evidence-linking rule and max 7 findings per invocation.

## Local TODOs

- [x] Initial codebase exploration — map prompts/fragments layout and system-prompt assembly
- [x] Design self-improvement trigger (name, invocation phrase, placement fragment)
- [x] Draft fragment patch with evidence-bound report schema and guardrails
- [x] Reassemble system-prompt.md and verify byte-identical build plus version bump
- [x] Verify functionality — lint, prettier, assembler checks pass

## Acceptance Criteria

- [x] Self-improvement trigger defined in the correct fragment(s) with explicit invocation phrase and evidence-bound output schema
- [x] Fragment edit is minimal and does not break existing 9-step SOP or inflate tokens unnecessarily
- [x] `system-prompt.md` reassembled and `<system_version>` bumped; `CHANGELOG.md` entry added
- [x] Verification: `python3 scripts/prompt-build/assemble_system_prompt.py` and lint checks exit 0

## Verification Evidence

- **Test command:** `npx prettier --write "prompts/fragments/*.md" && python3 scripts/prompt-build/assemble_system_prompt.py && grep -n "self-improve\|Self-Improvement" system-prompt.md | head`
- **Expected result:** Assembler exits 0, system-prompt contains new self-improvement section, version bumped
- **Actual result:**
  ```
  # Fragment creation & manifest update
  prompts/fragments/21-self_improvement_protocol.md — 46 lines, 2694 bytes (prettier formatted)
  prompts/manifest.txt — appended 21-self_improvement_protocol.md (now 20 entries)
  prompts/fragments/01-system_version.md — <system_version>9.4.0 → 9.5.0
  prompts/README.md — tree updated with 21-self_improvement_protocol.md

  # Assembly verification
  $ python3 scripts/prompt-build/assemble_system_prompt.py
  Assembled 77956 bytes -> system-prompt.md  (EXIT: 0)
  $ python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/final_check.md && diff -u /tmp/final_check.md system-prompt.md && echo "SYNC OK"
  SYNC OK

  # Trigger verification
  $ grep -n "self_improvement_protocol\|self-improve\|/reflect" system-prompt.md | head
  633:<self_improvement_protocol>
  642:- `/reflect`
  643:- `self-improve`
  672:1. **Propose Only:** The self-improvement engine is strictly forbidden...
  678:</self_improvement_protocol>
  $ grep -n "system_version" system-prompt.md
  1:<system_version>9.5.0</system_version>

  # Changelog
  $ grep -A 5 "## [9.5.0]" CHANGELOG.md
  ## [9.5.0] - 2026-09-02
  ### Added
  - **Self-Improvement Protocol:** Added evidence-bound retrospective protocol fragment (`21-self_improvement_protocol.md`) triggered via `/reflect` or `self-improve` to synthesize session friction into actionable backlog upgrades (Task 152).

  # Prettier
  $ npx prettier --write "prompts/fragments/21-self_improvement_protocol.md" "prompts/fragments/01-system_version.md" "prompts/README.md"
  prompts/fragments/21-self_improvement_protocol.md 111ms
  prompts/fragments/01-system_version.md 6ms (unchanged)
  prompts/README.md 66ms (unchanged)

  $ wc -l -c system-prompt.md
  678 77956 system-prompt.md
  Fragment token impact: +2694 bytes (~3.8% of 70630 total fragments) — under 5% ceiling.
  ```
- **Exit code:** 0 (all steps)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>` where SOURCE is ORCHESTRATOR-DETECTED, EXECUTOR-DETECTED, or EXECUTION-DETECTED. The Orchestrator is expected to pre-seed this section with `[ORCHESTRATOR-DETECTED]` entries during task generation when applicable. For Lite Mode tasks, log a `[LITE]` justification entry.)_

## Risk & Rollback

- **Risk:** Self-improvement proposals hallucinate or push auto-edits — disrupts ZAC and trust
- **Rollback plan:** Revert fragment addition/edit and re-run `python3 scripts/prompt-build/assemble_system_prompt.py` to restore `system-prompt.md`; delete new fragment if created

---

## Execution Log & Reasoning

**Micro-Task Execution (Steps 1–6):**

- [x] **Step 1: Create `prompts/fragments/21-self_improvement_protocol.md`** — Authored new fragment `<self_improvement_protocol>` (46 lines, 2694 bytes post-prettier) with Purpose, Invocation Triggers (`/reflect`, `self-improve`, `run retrospective`) as opt-in only, Evidence Scanning Contract (last 5–7 closed tasks, CHANGELOG, execution friction — all file:line citable), Output Schema (Retrospective Session Report table max 7 findings F1..N with Evidence Citation | Target Spec | Proposed Refinement | Expected Impact | Risk), and Operational Guardrails (Propose Only, Manager Gate, Task Conversion via task-generator, Token Ceiling). Choice of new fragment (Option A) over patching `11-execution_workflow.md` preserves 9-step SOP byte-identity and isolates rollback (`rm` + manifest revert). Token impact 3.8% <5% ceiling.

- [x] **Step 2: Update Manifest and Version** — `prompts/manifest.txt` appended `21-self_improvement_protocol.md` as final line (20 entries total); `prompts/fragments/01-system_version.md` bumped `9.4.0 → 9.5.0` (minor version — new protocol). Assembler security boundaries verified: `_safe_fragment_path` rejects traversal, `_safe_include_path` intact.

- [x] **Step 3: Update Prompts Documentation** — `prompts/README.md` directory tree fixed `19-communication_examples.md → 20-communication_examples.md` typo and added `21-self_improvement_protocol.md` leaf.

- [x] **Step 4: Reassemble `system-prompt.md`** — `python3 scripts/prompt-build/assemble_system_prompt.py` → 77956 bytes, 678 lines. Verified `<system_version>9.5.0</system_version>` at line 1 and `<self_improvement_protocol>` at line 633. Sync check via `--output /tmp/check` + `diff` → `SYNC OK` (byte-identical). Second assembler run after prettier also clean.

- [x] **Step 5: Update `CHANGELOG.md`** — Parse-Then-Append: inserted `## [9.5.0] - 2026-09-02` `### Added` entry for Self-Improvement Protocol (Task 152) between `Unreleased` and `9.4.0`. Preserved Keep a Changelog format.

- [x] **Step 6: Run Verification Suite** — `npx prettier --write` on 3 files (21 fragment reformatted table, others unchanged), assembler exit 0, grep trigger confirms presence, wc confirms 678 lines / 77956 bytes, changelog entry present, lint_task_file passes, verification-before-completion applied with evidence recorded above.

**Architecture reasoning:** Post-sprint reflection is now an explicit, evidence-bound loop (scan → propose → Manager gate → backlog task) rather than ad-hoc chat. Human-in-the-loop preserved (ZAC), tokens bounded (opt-in, max 7 findings, concise table), hallucinations blocked by file:line citation requirement.

**Roll-forward link:** Manager can now invoke `/reflect` after any dense session; approved findings convert to `tasks/backlog/*.md` via task-generator and enter normal 9-step line.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c56d08dfd032b2b464e1f8c46c82ebfb8e09dcb0`
<!-- END_GIT_DIFF -->
