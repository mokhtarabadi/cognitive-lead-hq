# Task 158: Purge Deprecated Manager Decision and Harden Audit Agent

**File:** `tasks/completed/158-purge-deprecated-manager-decision-and-harden-audit-agent.md`
**Source:** telegram
**Type:** bug
**Status:** closed

## Goal

Purge deprecated Manager/Admin Decision remnants from all task templates and add a deprecated-section purge rule to the audit-agents skill.

**Scope extension:** Overhaul `README.md` (SEO header, emoji taxonomy, purge stale decision-logging references, consolidate historical changelogs into a Release Milestones table) and standardize `user-prompts/` (purge retired guards, elevate coaching personas, wrap all copyable payloads in 1-click fences).

## Original Message (Persian)

### Message 564 (2026-09-03, reply_to 458, #bug)

ببین، یه بخشش قبلاً اضافه کردیم به اسم Manager Decision، خب؟ تصمیمات مدیر. بعد پاکش کردیم. این توی فایل Audit Agent قدیمی بود که میگفت باید اضافه کنی. اونو هم توی فایل Audit Agent پاک کردیم. ولی توی پروژههایی که قبلاً Audit Agent روشون انجام داده بودیم، اون بخش Manager Decision رو اضافه کرده بودند، هنوز هم دارن اون Manager Decision رو داخل تسکها مینویسن. باید Audit Agent رو ویرایش کنیم. این rule هم بهش اضافه کنیم که اگر این چیزهای deprecated رو داخل مثلاً فایل Agent.md دیدی، پاکشون کن. یکی از اون چیزهای deprecated شده همین Manager Decisionه. این skill رو ویرایش کن، بهاصطلاح به این چیزی که بهت گفتم که بعد نبرن روی پروژههای قدیمی اجراش کنن، که اون بخشها رو deprecated شده رو از توش پاک کنن.

#bug

### Message 565 (2026-09-03, reply_to 458, #remaining — continuation of 564)

این متن هم ادامهٔ متن بالا اضافه کن. ببین هر جایی که داریم تسک میسازیم، اون تمپلیت تسکها وجود دارن؛ هم توی تلگرام سینک، هم توی سیستم پرامپت، هم داخل خود تسک جنریتور اسکیل تسک جنریتور. اونجا هم حواست باشه ادمین دیسیژن یا منیجر دیسیژن پاک شده باشه، وجود نداشته باشه. اونم مطمئن شو.

#remaining

## English Translation

### Message 564

Look, we previously added a section called Manager Decision — manager's decisions. Then we removed it. It was in the old Audit Agent file that said you must add it. We also removed it from the Audit Agent file. But in projects where we previously ran Audit Agent, they had added that Manager Decision section, and they still keep writing that Manager Decision inside tasks. We must edit the Audit Agent. Add this rule to it that if you see these deprecated things inside e.g. AGENTS.md, delete them. One of those deprecated things is this Manager Decision. Edit this skill, so that when they run it on old projects, it removes those deprecated sections from them.

### Message 565 (continuation — add to the text above)

Add this text as a continuation of the text above. Look, everywhere we create tasks, those task templates exist; both in Telegram sync, and in the system prompt, and inside the task-generator skill itself. There too, make sure Admin Decision or Manager Decision has been removed, does not exist. Make sure of that too.

## Refactored Prompt

<role>
You are an elite Skill Governance & Template Consistency Engineer for the Cognitive Lead AI HQ ecosystem.
</role>

<system_context>
You operate inside the Cognitive Lead AI HQ repository (documentation-only: system prompts, MCP servers, Agent Skills). Task 151 already executed Option A (complete removal of ## Manager Decisions): stripped task-generator templates, prompts/fragments/09-hands_protocols.md, agents/cognitive-executor.md, docs/conventions.md, skill-templates/task-generator/SKILL.md, and audit-agents Decision Detection bullets. Residuals remain in: skill-templates/audit-agents/SKILL.md (2x Lite Mode Protocol bullets referencing ## Manager Decisions), prompts/fragments/10-lite_mode_protocol.md line 17, system-prompt.md line 392 (generated artifact), and the global installed copy ~/.config/opencode/skills/audit-agents/SKILL.md. Old third-party projects audited earlier still carry ## Manager Decisions sections in AGENTS.md / task files. Tools: grep, glob, read, lint_task_file, system-prompt assembler, prettier for Markdown.
</system_context>

<agentic_reasoning>
Before patching, output a <reasoning_log> covering:
1. Logical dependencies — which template is source of truth (skill-templates/task-generator/SKILL.md), which are derived (system-prompt.md via assembler, global skill copies via publish/sync), and the audit-agents purge rule insertion point (Scope Confinement / Target Audit Criteria vs Mode 2 Resolution Protocol).
2. Risk assessment — over-deletion (removing a live section the Manager still wants), archive immutability (tasks/archive/ and tasks/completed/ history must NOT be rewritten), stale generated artifact (system-prompt.md must be reassembled with version bump, not hand-edited).
3. Abductive reasoning — why residuals survived Task 151 (lite_mode fragment and audit-agents Lite Mode bullets were out of the listed micro-task scope; generated system-prompt.md was not reassembled for that orphan).
4. Precision and Grounding — cite file:line for every Manager/Admin Decision reference before editing; verify with grep before/after.
</agentic_reasoning>

<constraints>
- You MUST remove every positive ## Manager Decisions / Admin Decision reference from live templates: skill-templates/audit-agents/SKILL.md (both Lite Mode bullets), prompts/fragments/10-lite_mode_protocol.md, and reassemble system-prompt.md (bump <system_version>, CHANGELOG entry) — never hand-edit system-prompt.md alone.
- You MUST keep skill-templates/audit-agents/SKILL.md as single source of truth and sync it byte-identical to ~/.config/opencode/skills/audit-agents/SKILL.md after patching (report diff -q + wc -l evidence).
- You MUST add a Deprecated-Section Purge rule to the audit-agents skill: when auditing AGENTS.md / task files in any project, if a deprecated section (initial list: ## Manager Decisions, ## Admin Decision, Manager Decision, Admin Decision) is found, delete the section and note the removal — do NOT recreate it, do NOT flag its absence as a gap.
- You MUST NOT rewrite tasks/archive/ or tasks/completed/ history to remove old ## Manager Decisions headers — archive is immutable; future tasks simply omit the section.
- You MUST verify task-creation paths are clean: skill-templates/task-generator/SKILL.md, telegram-issue-sync skill (Variant B), and system-prompt task template excerpts contain zero Manager/Admin Decision references (grep evidence).
- Do NOT touch prompts/archive/17-decision_logging_mandate.md — archived mandate stays as historical record.
</constraints>

<output_format>
Provide: (1) Residual table — file:line before/after for every Manager/Admin Decision hit in live templates; (2) Patch diff — before→after for audit-agents purge rule + Lite Mode retarget (record [LITE] justification in Execution Log, not in a decisions section); (3) Sync evidence — diff -q template ↔ global copy + wc -l; (4) Verification — grep -rn "Manager Decisions" on live paths returns zero (excluding archive + completed history), lint_task_file passes, system-prompt assembler exit 0 with version bump.
</output_format>

## Relevant Code Context

- `skill-templates/audit-agents/SKILL.md:37,377` — Lite Mode Protocol bullets still reference `## Manager Decisions` for `[LITE]` justification; both need retarget + purge rule insertion point.
- `prompts/fragments/10-lite_mode_protocol.md:17` — `Decision Log Entry` step references `## Manager Decisions`; known orphan noted in Task 151 execution log, intentionally left unpatched there.
- `system-prompt.md:392` — generated artifact line mirroring the lite_mode fragment; must be fixed via reassembly, not hand-edit.
- `/home/mohammad/.config/opencode/skills/audit-agents/SKILL.md:37,377` — global installed copy with identical residuals; sync pattern requires template ↔ global byte-identical after fix (see `quirks/code_search_skill_sync_pattern` memory).
- `skill-templates/task-generator/SKILL.md` — already clean (grep returns zero); canonical source of truth to mirror, verify no regression.
- `tasks/completed/151-audit-manager-decision-logging.md` — prior Option A removal (stripped templates/protocols/executor/conventions, updated README/prompts); this task is the residual follow-up for lite_mode + audit-agents hardening.
- `tasks/completed/156-coach-prompt-alignment-and-manual-mode-optimizations.md` — retargeted coach intent audit from `## Manager Decisions` to `## Original Message (Persian)` / `## English Translation`; confirms new audit target convention.
- `prompts/archive/17-decision_logging_mandate.md` — archived mandate; must stay untouched as history.
- `.opencode/memory/telegram-sync/topic-scoped-sync-workflow.md` — topic-scoping + flood-wait + state semantics constraints governing this sync cycle.

## AI Analysis & Opinion

Root cause: Task 151 scoped its micro-tasks to the main decision-logging chain (fragment 17, fragment 09, cognitive-executor, conventions, task-generator, audit-agents decision bullets) but excluded the Lite Mode chain (fragment 10 + audit-agents Lite Mode bullets + generated system-prompt.md line). The audit-agents skill also lacks a forward-looking deprecated-section rule, so old projects audited earlier keep re-emitting ## Manager Decisions into new tasks.

Recommended fix: (1) Retarget Lite Mode justification from `## Manager Decisions` to Execution Log / task footer (check how Hands currently record `[LITE]` — align with fragment 09 documentation_phase); (2) Insert Deprecated-Section Purge rule into audit-agents skill (Scope Confinement or Mode 2 Resolution Protocol) with explicit deprecated list and delete-not-flag semantics; (3) Reassemble system-prompt.md with version bump + CHANGELOG; (4) Sync template → global copy, verify with diff/grep; (5) Verify telegram-issue-sync Variant B + task-generator templates stay clean.

Files to change: `skill-templates/audit-agents/SKILL.md`, `prompts/fragments/10-lite_mode_protocol.md`, `system-prompt.md` (via assembler), `~/.config/opencode/skills/audit-agents/SKILL.md` (sync target), `CHANGELOG.md`, this task file. Explicitly out of scope: `tasks/archive/*`, `tasks/completed/*` history rewrite, `prompts/archive/*`.

Risks: Over-gating Lite Mode logging so [LITE] justification is lost entirely — mitigate by defining an explicit new home (Execution Log). Version-bump omission on system-prompt.md — mitigate via lint_system_prompt_sync check.

## Local TODOs

- [x] Initial codebase exploration — grep all live Manager/Admin Decision residuals with file:line refs
- [x] Retarget Lite Mode justification + add Deprecated-Section Purge rule to audit-agents skill
- [x] Reassemble system-prompt.md with version bump, sync template → global copy
- [x] Verify functionality — grep zero residuals (live paths), diff identical, lint_task_file passes
- [x] README overhaul — SEO, emoji taxonomy, purge, milestones table
- [x] founder-coaching elevation — purge guards, executive-coach persona, fence
- [x] daily-english elevation — fluency partner persona, fence
- [x] Remaining 6 prompts fenced (verify cold-start/input-validation fences)
- [x] CHANGELOG extension entries + full verification + QA-transition

## Acceptance Criteria

- [x] Live templates contain zero positive Manager/Admin Decision references (skill-templates/audit-agents, prompts/fragments/10-lite_mode_protocol.md, system-prompt.md, task-generator, telegram-issue-sync Variant B)
- [x] audit-agents skill contains an explicit Deprecated-Section Purge rule that deletes ## Manager/Admin Decision sections when found in audited projects
- [x] system-prompt.md reassembled via assembler with version bump and CHANGELOG entry; template ↔ global skill copies byte-identical
- [x] README.md overhauled (SEO header + badges, emoji taxonomy, zero Manager Decision references, historical changelogs consolidated into Release Milestones table)
- [x] user-prompts standardized (founder-coaching purged + elevated to executive coach, daily-english elevated, all copyable payloads wrapped in 1-click fences)
- [x] Full cleanliness verified (README + user-prompts + live templates), skill sync parity holds, lint passes

## Verification Evidence

- **Test command:** `grep -rn "Manager Decisions\|Admin Decision" skill-templates/ prompts/fragments/ system-prompt.md tasks/backlog/ 2>/dev/null | grep -v "158-purge" || echo "CLEAN"`
- **Expected result:** No positive/prescriptive references (remaining hits, if any, must be only the new purge-rule target lists mandated by this task)
- **Actual result:** Only 3 hits, all in `skill-templates/audit-agents/SKILL.md` lines 38, 379 (`Deprecated-Section Purge Rule` target list) and 390 (`Deprecated Sections Purge` target list) — i.e. the rule text added by this task itself. Zero Lite Mode → Manager Decisions references, zero placeholders in `prompts/fragments/10-lite_mode_protocol.md`, `system-prompt.md`, `tasks/backlog/143-148`.
- **Exit code:** 0

- **Test command:** `diff -q skill-templates/audit-agents/SKILL.md ~/.config/opencode/skills/audit-agents/SKILL.md && echo "SYNC_OK"`
- **Expected result:** `SYNC_OK` + matching `wc -l`
- **Actual result:** `SYNC_OK`; `wc -l` → 402 template / 402 global (was 396/396 before; +6 lines: 2 purge-rule bullets, 1 resolution header, 1 purge bullet, 2 blanks)
- **Exit code:** 0

- **Test command:** `lint_task_file tasks/in-progress/158-purge-deprecated-manager-decision-and-harden-audit-agent.md`
- **Expected result:** passes
- **Actual result:** `✅ tasks/in-progress/158-purge-deprecated-manager-decision-and-harden-audit-agent.md passed Task File linting.`
- **Exit code:** 0

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py`
- **Expected result:** exit 0, `system-prompt.md` at `<system_version>9.9.0</system_version>`, line 392 retargeted to `## Execution Log & Reasoning`
- **Actual result:** `Assembled 75697 bytes -> system-prompt.md`; `grep "<system_version>"` → `<system_version>9.9.0</system_version>`; `system-prompt.md:392` confirms `## Execution Log & Reasoning`
- **Exit code:** 0

- **Test command:** `grep -rn "^## Manager Decisions" tasks/backlog/ tasks/in-progress/ tasks/qa/ 2>/dev/null || echo "BACKLOG_CLEAN"`
- **Expected result:** `BACKLOG_CLEAN`
- **Actual result:** `BACKLOG_CLEAN`
- **Exit code:** 0

## Extension Verification Evidence (scope extension, 2026-09-04)

- **Test command:** `grep -rn "Manager Decisions\|Manager Decision" README.md user-prompts/ 2>/dev/null || echo "CLEAN"`
- **Expected result:** `CLEAN`
- **Actual result:** `CLEAN` (founder-coaching guards purged; no other prompt references)
- **Exit code:** 0

- **Test command:** `grep -rn "Manager Decisions\|Admin Decision" skill-templates/ prompts/fragments/ system-prompt.md tasks/backlog/ README.md user-prompts/ 2>/dev/null | grep -v "158-purge" || echo "ALL_CLEAN"`
- **Expected result:** Only the intentional purge-rule target lists in `skill-templates/audit-agents/SKILL.md` (feature text mandated by this task)
- **Actual result:** Exactly 3 hits — skill lines 38, 379 (`Deprecated-Section Purge Rule` target list), 390 (`Deprecated Sections Purge` target list). Zero hits in `prompts/fragments/`, `system-prompt.md`, `tasks/backlog/`, `README.md`, `user-prompts/`.
- **Exit code:** 0

- **Test command:** `diff -q skill-templates/audit-agents/SKILL.md ~/.config/opencode/skills/audit-agents/SKILL.md && echo "SYNC_OK"`
- **Expected result:** `SYNC_OK` (402/402)
- **Actual result:** `SYNC_OK`; 402/402 (unchanged by extension — skill untouched in this pass)
- **Exit code:** 0

- **Test command:** quad-fence balance `for f in user-prompts/*.md; do grep -c '^````' "$f"; done`
- **Expected result:** exactly 2 per file across all 10 prompts
- **Actual result:** all 10 files report `quad=2` (balanced open/close)
- **Exit code:** 0

- **Test command:** `lint_task_file tasks/in-progress/158-purge-deprecated-manager-decision-and-harden-audit-agent.md`
- **Expected result:** passes
- **Actual result:** `✅ tasks/in-progress/158-purge-deprecated-manager-decision-and-harden-audit-agent.md passed Task File linting.`
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Lite Mode justification loses its home and [LITE] entries stop being recorded anywhere
- **Rollback plan:** Restore `skill-templates/audit-agents/SKILL.md` and `prompts/fragments/10-lite_mode_protocol.md` via `git checkout -- <path>`, re-sync global copy, reassemble system-prompt.md to prior version

---

## Execution Log & Reasoning

**Scope:** Residual follow-up to Task 151 (Option A removal). Task 151 stripped the main decision-logging chain but left the Lite Mode chain (fragment 10 → generated `system-prompt.md:392` → audit-agents Lite Mode bullets ×2) untouched. This task retargets that chain to `## Execution Log & Reasoning` and hardens the project-agnostic `audit-agents` skill with a forward-looking deprecated-section purge rule.

**Changes (11 files + 1 global sync target):**
- `prompts/fragments/10-lite_mode_protocol.md:17` — `## Manager Decisions` → `## Execution Log & Reasoning` (Step 1).
- `prompts/fragments/01-system_version.md` — `9.8.0` → `9.9.0` (Step 2).
- `system-prompt.md` — reassembled via `scripts/prompt-build/assemble_system_prompt.py` (75697 bytes, exit 0); line 392 retargeted (Step 3). Never hand-edited.
- `skill-templates/audit-agents/SKILL.md` (396→402 lines) — retargeted both Lite Mode bullets (lines 37, 377); added `Deprecated-Section Purge Rule` to both Target Audit Criteria mirrors (lines 38, 379, project-agnostic wording — no HQ-only paths, so the template stays project-agnostic per `AGENTS.md` HQ-ONLY rules); added `### Deprecated Sections Resolution` subsection with `Deprecated Sections Purge` bullet under Mode 2 Resolution Protocol (Step 4).
- `~/.config/opencode/skills/audit-agents/SKILL.md` — synced via `cp`, `diff -q` SYNC_OK, 402/402 (Step 5).
- `tasks/backlog/143,144,145,146,147,148` — stripped orphan `## Manager Decisions` header + placeholder italic + trailing blanks (Step 6); `grep ^## Manager Decisions` over backlog/in-progress/qa → BACKLOG_CLEAN.
- `CHANGELOG.md` — Parse-Then-Append `## [9.9.0] - 2026-09-04` with Added/Changed/Fixed (Step 7).
- This task file — moved backlog→in-progress (filesystem `mv` fallback: file was untracked, `git mv` refused with "not under version control"); `**File:**` header synced to in-progress path.

**Reasoning notes:** Kept the purge rule project-agnostic (only `AGENTS.md` + `tasks/` generic paths) to avoid violating the HQ-ONLY rule that forbids HQ scaffolding references in the global audit skill. Did not touch `prompts/archive/17-decision_logging_mandate.md`, `tasks/completed/*`, `tasks/archive/*` (immutable history). Residual grep hits that remain (skill lines 38/379/390) are the purge rule's own deprecated-name target lists — required by the spec, not prescriptive references. No `git commit`/`push` executed (ZAC); staging deferred to the atomic QA transition.

**Scope extension log (re-opened from qa → in-progress):**
- `README.md` — SEO header (`# Cognitive Lead AI HQ 🧠⚡` + platform subtitle + FastMCP/ZAC badges alongside existing Version/License/OpenCode/PRs badges); emoji taxonomy on all 8 specified `##` headers (`Manual Mode Workflow` promoted `###`→`##` per spec); purged 3 stale decision-logging references (V9 architecture bullet → Context Restoration Protocols; V9 changelog bullet removed; V6.7 note clause removed); consolidated verbose V5/V6/V7/V8 blocks into a `## 📜 Release Milestones` table (V9/V9.1 sections preserved in place). Verified `README_CLEAN`.
- `user-prompts/founder-coaching-chat.md` — removed 3 retired Task 151 guard banners (lines 84/120/145), reframed `<intent_fidelity_audit>` around direct intent-vs-delivery audit (sole source of truth unchanged); elevated role with Campbell/Grove/Mochary executive-coach framing + new `<executive_coaching_frameworks>` block (Bottleneck Diagnosis, Energy & Leverage Audit, Socratic Decision Challenges); wrapped payload in quad-backtick markdown fence (inner triple fences nest safely). Verified `FOUNDER_CLEAN`, fence balanced.
- `user-prompts/daily-english-coach-chat.md` — elevated role to high-impact Conversational Fluency Partner (high-stakes settings, natural phrasing, phonetic scaffolding, active recall); quad fence applied.
- Remaining 6 prompts (`agile-pm`, `multi-agent-brainstorming` [xml fence], `perplexity-deep-research`, `persian-to-english-dictation`, `session-compactor`, `voice-to-text-enhancer` [xml fences]) + `cold-start-context` / `input-validation-test` (verified presentation, upgraded to quad wrappers for uniform 1-click copy): all 10 files now carry exactly 2 quad-fence lines (balanced open/close). Verified `PROMPTS_CLEAN`.
- `CHANGELOG.md` — extended the `## [9.9.0]` Added/Changed/Fixed entries with the fence/persona, README, and purge notes (no new version header; same release).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `51b0da4d5b1b7c73250e9b14591e76f21e2f873a`
<!-- END_GIT_DIFF -->
