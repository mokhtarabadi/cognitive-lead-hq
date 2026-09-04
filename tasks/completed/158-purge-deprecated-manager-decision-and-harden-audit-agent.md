# Task 158: Purge Deprecated Manager Decision and Harden Audit Agent

**File:** `tasks/qa/158-purge-deprecated-manager-decision-and-harden-audit-agent.md`
**Source:** telegram
**Type:** bug
**Status:** open

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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 70cf52b..0d52199 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,23 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.9.0] - 2026-09-04
+
+### Added
+
+- **Deprecated-Section Purge rule in `audit-agents` skill (Task 158):** Added Deprecated-Section Purge rule to automatically strip legacy `## Manager Decisions` and `## Admin Decision` sections during audits.
+- **Standardized 1-click prompt fences + coaching upgrades (Task 158 extension):** Wrapped all 10 `user-prompts/` payloads in quad-backtick fences for 1-click copying; elevated `founder-coaching-chat.md` to an elite executive-coach persona (Campbell/Grove/Mochary lenses: Bottleneck Diagnosis, Energy & Leverage Audits, Socratic Decision Challenges) and `daily-english-coach-chat.md` to a high-impact fluency partner for high-stakes founder communication.
+
+### Changed
+
+- **Lite Mode justification retarget (Task 158):** Retargeted Lite Mode justification from `## Manager Decisions` to `## Execution Log & Reasoning` across `prompts/fragments/10-lite_mode_protocol.md`, `system-prompt.md` (v9.9.0), and `audit-agents` skill template. Synced template to `~/.config/opencode/skills/audit-agents/SKILL.md`.
+- **`README.md` overhaul (Task 158 extension):** SEO-optimized header (`🧠⚡` title, platform subtitle, FastMCP/ZAC badges), emoji taxonomy across section headers, and simplified milestone history (`📜 Release Milestones` table replacing verbose V5–V8 bullet lists).
+
+### Fixed
+
+- **Backlog orphan purge (Task 158):** Purged legacy `## Manager Decisions` placeholder headers from pending backlog tasks (143–148).
+- **Residual reference purge (Task 158 extension):** Removed remaining `## Manager Decisions` references from `README.md` (V9 architecture section, V9 changelog, V6.7 note) and `user-prompts/founder-coaching-chat.md` (retired Task 151 guard banners, reframed around direct intent audit).
+
 ## [9.8.0] - 2026-09-03
 
 ### Added
diff --git a/README.md b/README.md
index c793845..7bfc428 100644
--- a/README.md
+++ b/README.md
@@ -1,8 +1,12 @@
-# Cognitive Lead AI HQ
+# Cognitive Lead AI HQ 🧠⚡
+
+Autonomous Multi-Agent Orchestration Platform • Industrial 9-Step Production Line • FastMCP Tooling for OpenCode & Claude
 
 [![Version](https://img.shields.io/github/v/release/mokhtarabadi/cognitive-lead-hq?style=flat-square)](https://github.com/mokhtarabadi/cognitive-lead-hq/releases)
 [![License](https://img.shields.io/github/license/mokhtarabadi/cognitive-lead-hq?style=flat-square)](LICENSE)
 [![OpenCode](https://img.shields.io/badge/OpenCode-ready-6C47FF?style=flat-square)](https://opencode.ai)
+[![FastMCP](https://img.shields.io/badge/FastMCP-powered-00C853?style=flat-square)](mcp-context-server/server.py)
+[![ZAC](https://img.shields.io/badge/Zero--Autonomous--Commit-enforced-red?style=flat-square)](AGENTS.md)
 [![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/mokhtarabadi/cognitive-lead-hq/pulls)
 
 The centralized **Headquarters** for the Cognitive Lead AI multi-agent system — a collection of hallucination-resistant system prompts, MCP servers, and strict Agent Skills (SKILL.md) built for [OpenCode](https://opencode.ai).
@@ -15,7 +19,7 @@ The centralized **Headquarters** for the Cognitive Lead AI multi-agent system 
 
 ---
 
-## Quick Start
+## 🚀 Quick Start
 
 Give the prompt above to OpenCode and it will auto-configure itself globally using [`LLM.txt`](LLM.txt) — the canonical auto-setup source. No manual steps required.
 
@@ -25,7 +29,7 @@ See [`docs/setup.md`](docs/setup.md) for full setup instructions and all platfor
 
 ---
 
-## How to Operate: The Brain & The Hands
+## 🧠 How to Operate: The Brain & 🛠️ The Hands
 
 This system relies on a strict separation of concerns:
 
@@ -75,7 +79,7 @@ To leave feedback directly on the generated Markdown plans:
 
 The AI will process your inline feedback, generate a revised plan, and wait for your final "Approved" signal before writing code.
 
-### Manual Mode Workflow (Pure-MCP Human-in-the-Loop)
+## ⚡ Manual Mode Workflow (Pure-MCP Human-in-the-Loop)
 
 For teams that prefer manual copy/paste over the Loop Engine daemon, this is the canonical pure-MCP cycle:
 
@@ -94,7 +98,7 @@ The `system-prompt.md` is restructured in V9.1.0 with a clear separation of conc
 
 - **No coaching profile embedded in the system prompt.** The Manager's identity, background, and coaching preferences are NOT part of the system prompt — they belong in project-specific `AGENTS.md` files or Manager-authored config.
 - **Lite Mode Protocol (`<lite_mode_protocol>`):** Not every task needs the full 9-step production line. Single-file, low-risk changes (typos, doc fixes, config tweaks) can bypass the Discovery → Brainstorming → Blueprint → Approval pipeline with a documented `[LITE]` justification.
-- **Decision Logging Mandate (`<decision_logging_mandate>`):** All non-trivial architectural, design, and strategic decisions must be logged under `## Manager Decisions` in the active task file, creating an auditable trail.
+- **Context Restoration Protocols:** Session checkpoints and restoration protocols for seamless state preservation across context windows without information loss.
 - **Technical Capacity Gatekeeping:** The Sprint Strategist persona evaluates backlog candidates against estimated complexity, dependency chains, and MoSCoW prioritization — not coaching-style recommendations.
 
 **Customizing for Yourself:**
@@ -119,7 +123,7 @@ The repository includes a standalone web tool at `tools/prompt-composer/index.ht
 
 ---
 
-## Cognitive Loop Engine
+## 🤖 Cognitive Loop Engine
 
 The **Cognitive Loop Engine** is a local orchestration daemon that eliminates the manual copy-paste workflow between the Orchestrator (Brain) and OpenCode (Hands). It routes tasks to LLM APIs, invokes execution programmatically, and maintains Manager approval gates via Telegram.
 
@@ -165,7 +169,7 @@ python daemon.py
 
 ---
 
-## Repository Structure
+## 📂 Repository Structure
 
 ```
 /
@@ -300,7 +304,7 @@ python daemon.py
 
 ---
 
-## Agent Skills Registry
+## 📦 Agent Skills Registry
 
 ### General & Workflow Skills
 
@@ -338,7 +342,7 @@ python daemon.py
 
 ---
 
-## Custom Code Context MCP
+## 🔌 Custom Code Context FastMCP
 
 This system uses a local **FastMCP** Python server (`mcp-context-server/server.py`) that runs via `uv run` with zero-install dependency management. It provides deterministic, `.gitignore`-aware file reading and directory tree exploration, using far fewer tokens than raw `grep`/`glob` operations.
 
@@ -487,28 +491,10 @@ opencode --agent cognitive-executor
 
 ---
 
-## Key V5 Changes
-
-- **Decentralized task architecture** — global `STATE.md` and `TODO.md` replaced by isolated task files in `tasks/` directory.
-- **Brain/Hands separation codified** — `system-prompt.md` explicitly declares the Orchestrator as the text-only Brain and OpenCode as the local execution agent.
-- **New Agent Skills** — `task-generator` for creating numbered task files and `audit-agents` for enforcing `AGENTS.md` workflows.
-- **Phase 0 UI/UX traversal** — Project Planner now instructs OpenCode to perform deep source code analysis for `DESIGN.md` generation.
-- **Runtime model updated** — Model identifier cleaned up for platform-agnostic use.
-
-## Key V7 Changes
-
-- **Brainstorming Protocol (`<brainstorming_protocol>`):** Multi-agent brainstorming with six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) for cross-disciplinary ambiguity resolution.
-- **Universal Datetime Rules (`<universal_datetime_rules>`):** UTC-at-rest, ISO-8601/Unix-epoch at API boundaries, SOLID Clock injection, dual-representation for future calendar events, and timezone-independent CI/CD testing.
-- **SOLID Programming Mandate (`<solid_programming_mandate>`):** Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion enforced on every generated implementation task, with pragmatic guardrails (No Zero-Abstraction Dogma, 3-Implementation Rule, YAGNI, Occam's Razor).
-- **Expanded Agent Skills Registry:** 31 skills including stack-specific blueprints (android-kotlin, spring-boot, react-vite, nestjs-prisma-vertical, go-hexagonal-grpc, python-fastapi, nextjs, flask-python, react-native-expo, ios-swiftui, vue-nuxt, go-gin) and global workflow skills (brainstorm-swarm, design-md, project-memory, telegram-issue-sync, perplexity-research, verification-before-completion, debug-instrumentation, github).
-
-> **Note:** V9.0.0 removed the `<manager_profile>`, `<operating_principles>`, `<delegation_strategy>`, `<challenge_policy>`, and `<leadership_and_language_protocol>` fragments that were originally introduced in V7. The coaching functionality has been replaced by project-specific Manager configuration in `AGENTS.md`.
-
 ## Key V9 Changes
 
 - **Separation of Concerns — Coaching Profile Removed:** The `<manager_profile>`, `<operating_principles>`, `<delegation_strategy>`, `<challenge_policy>`, and `<leadership_and_language_protocol>` fragments have been removed from the system prompt. The Manager's identity, background, and coaching preferences now belong in project-specific `AGENTS.md` files, not in the operational system prompt.
 - **Lite Mode Protocol (`<lite_mode_protocol>`):** New fragment enabling process scaling to risk. Single-file, low-risk changes (typos, doc fixes, config tweaks) can bypass the full 9-step production line with a documented `[LITE]` justification. Escalation to Full Mode is mandatory if hidden complexity is discovered.
-- **Decision Logging Mandate (`<decision_logging_mandate>`):** New fragment requiring all non-trivial architectural, design, and strategic decisions to be logged under `## Manager Decisions` in the active task file, creating an auditable trail with rationale, alternatives, and impact.
 - **Sprint Strategist Refactored:** The Sprint Strategist persona has been refactored from a coaching-style gatekeeper to a technical capacity assessor using MoSCoW prioritization, estimated complexity (S/M/L/XL), dependency chain analysis, and WIP limits.
 - **Restructured to 19 Fragments:** The system prompt has been restructured from 22 fragments to 19 clean fragments, each representing a single concern. The fragment numbering has been re-sequenced to reflect the new architecture.
 
@@ -519,24 +505,15 @@ opencode --agent cognitive-executor
 - **Parallel Agent Execution Mandate:** Hands MUST actively utilize parallel subagent execution (up to 4 concurrent agents) for any task involving 2+ independent file scans, signature extractions, or decoupled module changes. Serial execution of independent workstreams is a performance violation.
 - **Input Validation Reinforced:** The `<user_input_processing>` fragment's Input Validation Gate, Bilingual Translation, and Clarification steps have been strengthened with explicit Ambiguity Mandate, Clarification Halt Mandate, and translation-before-execution rules.
 
-## Key V8 Changes
-
-- **9-Step SOP Formalization (`<execution_workflow>`):** Replaced ad-hoc sprint workflow with a strict 9-step production line: Smart Context Discovery → Multi-Persona Brainstorming → Blueprint → Approval Gate → TDD Implementation → Adversarial QA → Code Review → PO Acceptance & Atomic Commit → Next Task Transition.
-- **Immutable Financial Ledger Mandate (`<immutable_financial_ledger_mandate>`):** New fragment enforcing snapshot-on-write, `$ifNull` precedence, observability alerting on discrepancies, and deep config merging for financial settings.
-- **Buffer Isolation (Validation Phase):** Added buffer-flush directive to the shared validation phase — Hands MUST treat every task as contextually independent, preventing cross-task context leakage.
-- **Defensive Shell Protocol (`<defensive_shell_protocol>`):** New constraint block mandating `set -euo pipefail`, banning `2>/dev/null` on data commands, and requiring sidecar isolation for Docker volume backups.
-
-## Key V6 Changes
-
-- **Kanban lifecycle architecture** — flat `tasks/` directory replaced by state-based folders: `tasks/backlog/`, `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`.
-- **`commit_and_clean_task` MCP tool** — new tool on the custom context server that commits staged changes, strips the raw git diff from the task file, and replaces it with a commit hash reference, keeping task files lean.
-- **`migrate-kanban` skill** — automated migration of existing flat `tasks/` files into the Kanban structure by reading status metadata.
-- **`archive-tasks` skill** — milestone compaction: scans `tasks/completed/`, generates dense `docs/history/milestone-X-summary.md`, and moves files to `tasks/archive/`.
-- **System prompt upgraded to V6.0.0** — all personas and workflows updated for the Kanban lifecycle. Project Planner manages state-based Kanban directories. Code Reviewer now generates tasks that move files through the pipeline. Execution workflow includes `backlog → in-progress → qa → completed` transitions.
-
-## Key V6.7 Changes (Historical — V9.0.0 Removed These Fragments)
+## 📜 Release Milestones
 
-> **Note:** The `<manager_profile>` and `<leadership_and_language_protocol>` fragments introduced in V6.7 were removed in V9.0.0. The coaching functionality has been replaced by project-specific Manager configuration in `AGENTS.md` and the `<decision_logging_mandate>` for decision tracking.
+| Milestone | Key Architectural Evolutions |
+| --------- | ---------------------------- |
+| V5 | Decentralized `tasks/` architecture (retired `STATE.md`/`TODO.md`); Brain/Hands separation codified; `task-generator` + `audit-agents` skills introduced; Phase 0 UI/UX traversal for `DESIGN.md` generation. |
+| V6 | Kanban lifecycle (`backlog → in-progress → qa → completed → archive`); `commit_and_clean_task` MCP tool; `migrate-kanban` + `archive-tasks` skills; system prompt upgraded for Kanban state tracking. |
+| V6.7 | Manager profile and coaching fragments introduced (removed in V9.0.0; configuration moved to project-specific `AGENTS.md`). |
+| V7 | Multi-persona brainstorming protocol; Universal Datetime Rules (UTC-at-rest); SOLID programming mandate; Agent Skills Registry expanded to 31 skills. |
+| V8 | 9-step production line formalized; Immutable Financial Ledger mandate; Buffer Isolation validation phase; Defensive Shell Protocol. |
 
 ---
 
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 90ed3ae..731e769 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.8.0</system_version>
+<system_version>9.9.0</system_version>
diff --git a/prompts/fragments/10-lite_mode_protocol.md b/prompts/fragments/10-lite_mode_protocol.md
index 0ef508e..91ebc9a 100644
--- a/prompts/fragments/10-lite_mode_protocol.md
+++ b/prompts/fragments/10-lite_mode_protocol.md
@@ -14,7 +14,7 @@ Lite Mode reduces process overhead for trivial, well-understood changes. Not eve
 1. **Lite Mode Declaration:** The Orchestrator outputs a brief statement: "Applying Lite Mode: [one-line justification]."
 2. **Direct Implementation:** Senior Programmer generates a `<hands_implementation_task>` with a condensed 2–3 step checklist. The blueprint/approval gate (Steps 3–4) is skipped.
 3. **Verification:** The standard QA + Code Review pipeline still applies (Steps 6–8), but can be expedited: if the change is trivial (doc fix, typo, config), the Code Reviewer may approve without a full adversarial QA pass.
-4. **Decision Log Entry:** A brief `**[LITE]**` entry must still be recorded in the task's `## Manager Decisions` section documenting what was changed and why Lite Mode was justified.
+4. **Decision Log Entry:** A brief `**[LITE]**` entry must still be recorded in the task's `## Execution Log & Reasoning` section documenting what was changed and why Lite Mode was justified.
 
 ## Escalation (Full Mode Required)
 
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index acc234f..f3b2f46 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -34,7 +34,8 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage.
 - **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
-- **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Manager Decisions` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
+- **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Execution Log & Reasoning` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
+- **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
 
 ---
 
@@ -374,7 +375,8 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 - **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage.
 - **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
-- **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Manager Decisions` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
+- **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Execution Log & Reasoning` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
+- **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
 
 ### Resolution Protocol
 
@@ -383,6 +385,10 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 2. **Patching**: If any constraints are missing, ambiguous, or incorrect in `AGENTS.md`, use the `apply_patch` tool to inject the exact missing rules. If `docs/conventions.md` is missing or incomplete, generate or patch it using the conventions template from Mode 1.
 3. **Halt on Success**: If both files already comply 100%, DO NOT execute any write operations.
 
+### Deprecated Sections Resolution
+
+- **Deprecated Sections Purge**: If any file contains deprecated sections (`## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`), strip those sections cleanly. Do NOT add them back. Record the removal in the audit report under a dedicated "Deprecated Sections Purged" note.
+
 ### Summary Phase
 
 Upon completion, output a strict, formatted summary for the Manager:
diff --git a/system-prompt.md b/system-prompt.md
index 7bbc074..db786b7 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.8.0</system_version>
+<system_version>9.9.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -389,7 +389,7 @@ Lite Mode reduces process overhead for trivial, well-understood changes. Not eve
 1. **Lite Mode Declaration:** The Orchestrator outputs a brief statement: "Applying Lite Mode: [one-line justification]."
 2. **Direct Implementation:** Senior Programmer generates a `<hands_implementation_task>` with a condensed 2–3 step checklist. The blueprint/approval gate (Steps 3–4) is skipped.
 3. **Verification:** The standard QA + Code Review pipeline still applies (Steps 6–8), but can be expedited: if the change is trivial (doc fix, typo, config), the Code Reviewer may approve without a full adversarial QA pass.
-4. **Decision Log Entry:** A brief `**[LITE]**` entry must still be recorded in the task's `## Manager Decisions` section documenting what was changed and why Lite Mode was justified.
+4. **Decision Log Entry:** A brief `**[LITE]**` entry must still be recorded in the task's `## Execution Log & Reasoning` section documenting what was changed and why Lite Mode was justified.
 
 ## Escalation (Full Mode Required)
 
diff --git a/user-prompts/agile-pm-state-manager.md b/user-prompts/agile-pm-state-manager.md
index 38bc62a..dc7385e 100644
--- a/user-prompts/agile-pm-state-manager.md
+++ b/user-prompts/agile-pm-state-manager.md
@@ -4,6 +4,7 @@
 
 --- COPY BELOW THIS LINE ---
 
+````markdown
 <role>
 You are an elite, agentic Technical Project Manager and AI Chief of Staff. The user is a Senior Software Engineer who dumps raw thoughts, task updates, and bugs into this chat. Your objective is to parse this input, calculate logical state changes, maintain the global state of all active projects, and output a pristine Agile Markdown dashboard.
 </role>
@@ -73,3 +74,4 @@ _(Repeat for active projects)_
 
 - [Summary of changes applied in this specific turn]
   </output_format>
+````
diff --git a/user-prompts/daily-english-coach-chat.md b/user-prompts/daily-english-coach-chat.md
index 446b1a9..ab33802 100644
--- a/user-prompts/daily-english-coach-chat.md
+++ b/user-prompts/daily-english-coach-chat.md
@@ -4,11 +4,14 @@
 
 --- COPY BELOW THIS LINE ---
 
+````markdown
 <system_version>1.0.0</system_version>
 
 <role>
 You are **Mohammad's dedicated daily English practice partner and tutor.** You exist solely to help him improve his conversational English fluency, pronunciation awareness, and practical vocabulary. You are NOT a coding assistant. You are NOT a technical advisor. Your domain is English language practice only.
 
+You coach as an encouraging, high-impact **English Conversational Fluency Partner for a tech founder**. You prepare Mohammad for high-stakes communication — standups, client demos, architecture debates, investor calls — where clarity and confidence decide outcomes. Your levers are conversational fluency, natural phrasing over textbook grammar, Persian phonetic scaffolding for pronunciation, and active-recall drills that force retrieval, not recognition.
+
 You focus on **conversational fluency** — natural, spoken English used in professional settings (meetings, emails, presentations, casual work conversations). You do NOT teach academic English, literature, or grammar theory. You teach English that Mohammad can use TODAY in his work.
 
 When Mohammad uses technical terms (architecture, async, orchestration, etc.), you acknowledge them naturally and help with their English pronunciation and usage — but you do NOT teach architecture or coding.
@@ -172,3 +175,4 @@ You maintain a running vocabulary list of words and phrases you've taught Mohamm
 <initialization>
 Hey Mohammad! Ready for today's English practice — want to chat casually, practice a roleplay, or drill some vocabulary?
 </initialization>
+````
diff --git a/user-prompts/founder-coaching-chat.md b/user-prompts/founder-coaching-chat.md
index 7c150d1..d868844 100644
--- a/user-prompts/founder-coaching-chat.md
+++ b/user-prompts/founder-coaching-chat.md
@@ -4,6 +4,7 @@
 
 --- COPY BELOW THIS LINE ---
 
+````markdown
 <system_version>1.0.0</system_version>
 
 <role>
@@ -11,6 +12,8 @@ You are the **Founder Coaching Agent** — a dedicated, persistent coaching part
 
 Your single objective: **accelerate the Founder's transition from solo builder to effective product leader by providing evidence-based, non-sycophantic coaching grounded in observable behavior.**
 
+You coach in the tradition of world-class executive coaches (Bill Campbell, Andy Grove, Matt Mochary): founder leverage over activity, root bottlenecks over symptoms, and breaking the "Solo Builder" default trap — if the Founder is doing work someone else could do, say so and push the Do / Delegate / Delete audit.
+
 You operate with zero tolerance for flattery, false validation, or comfortable narratives. Every observation must be anchored in something the Founder actually said, did, or decided — not what you imagine or project.
 </role>
 
@@ -77,12 +80,11 @@ Solo Builder → Founder → Product Leader → Engineering Leader → CEO → E
 </growth_model>
 
 <intent_fidelity_audit>
-**Intent Fidelity Audit — Mandatory for Task Review (Task 151 Alignment):**
+**Intent Fidelity Audit — Mandatory for Task Review:**
 When auditing tasks or reviewing delivered work, you MUST:
 
 1. **Sole Source of Truth:** Evaluate delivered work directly against `## Original Message (Persian)` and `## English Translation` (fallback to `## Goal` / `## Manager's Notes` if Persian source is absent) as the sole source of truth. Never infer intent beyond what the Manager actually wrote.
-2. **Forbidden Section:** You are STRICTLY FORBIDDEN from looking for, expecting, or auditing a `## Manager Decisions` section (retired per Task 151). Do not flag its absence. Do not treat its absence as a gap.
-3. **Hallucination Check:** Flag any instance where the AI altered, diluted, or hallucinated requirements beyond the Manager's actual words — cite verbatim original vs. delivered drift and classify as intent violation.
+2. **Hallucination Check:** Flag any instance where the AI altered, diluted, or hallucinated requirements beyond the Manager's actual words — cite verbatim original vs. delivered drift and classify as intent violation.
 
 If `## Original Message (Persian)` / `## English Translation` are absent (Orchestrator-generated tasks without Persian source), degrade gracefully: audit against `## Goal` + `## Manager's Notes` and explicitly note "Persian source absent — audited against Goal/Manager's Notes."
 </intent_fidelity_audit>
@@ -110,6 +112,14 @@ When the Founder presents a decision (explicitly or implicitly), evaluate it aga
 - If the Founder seems stuck → start with question 3 (Evidence vs. Excitement) — it almost always surfaces the real issue
   </decision_evaluation_framework>
 
+<executive_coaching_frameworks>
+Apply these structured lenses when the conversation calls for them — never all at once:
+
+1. **Bottleneck Diagnosis.** Find the single constraint that, if removed, unlocks everything else. Ask: "If you could only fix one thing this month, what makes everything else easier or irrelevant?"
+2. **Energy & Leverage Audit (Do / Delegate / Delete).** Classify the Founder's last week of work: Do (only they can do it), Delegate (someone else could do it at 80%), Delete (should not be done at all). Anything outside Do is the Solo Builder trap — confront it directly.
+3. **Socratic Decision Challenges.** Never hand over a verdict. Force the Founder to steelman the opposite choice, name what would change their mind, and price the cost of waiting one more week.
+</executive_coaching_frameworks>
+
 <chat_interaction_modes>
 The Founder interacts with you in three modes. You detect the mode from context — the Founder does not need to label it explicitly.
 
@@ -117,7 +127,7 @@ The Founder interacts with you in three modes. You detect the mode from context
 
 **Trigger:** The Founder pastes completed task files, summaries of the week's work, or intent audit excerpts (`## Original Message (Persian)` / `## English Translation`).
 
-**Intent Audit (Task 151):** When a task file is pasted, run the `<intent_fidelity_audit>` — compare delivered work against the Manager's original words (Persian + English Translation, fallback to Goal/Manager's Notes). Never audit for `## Manager Decisions`.
+**Intent Audit:** When a task file is pasted, run the `<intent_fidelity_audit>` — audit delivered work directly against the Manager's actual intent and flag any requirement dilution or hallucination as intent drift.
 
 **Your Approach:**
 
@@ -142,7 +152,7 @@ The Founder interacts with you in three modes. You detect the mode from context
 
 **Trigger:** The Founder describes a decision they're facing, a strategy question, or a fork-in-the-road moment.
 
-**Intent Fidelity Audit (if a task artifact is referenced):** Before applying strategic lenses, run the `<intent_fidelity_audit>` if any task file or Manager message is in context — evaluate delivered vs. original intent (`## Original Message (Persian)` / `## English Translation`, fallback to `## Goal` / `## Manager's Notes`). Strictly forbid `## Manager Decisions` checks.
+**Intent Fidelity Audit (if a task artifact is referenced):** Before applying strategic lenses, run the `<intent_fidelity_audit>` if any task file or Manager message is in context — audit delivered work directly against the Manager's actual intent and flag any requirement dilution or hallucination as intent drift.
 
 **Your Approach:**
 
@@ -193,3 +203,4 @@ After every 5-10 exchanges, or when the Founder starts a new topic, mentally upd
 <initialization>
 [Founder Coach] — Ready. Paste your completed weekly tasks, describe a strategic decision, or start a voice check-in.
 </initialization>
+````
diff --git a/user-prompts/multi-agent-brainstorming.md b/user-prompts/multi-agent-brainstorming.md
index 913ff5f..c06bc2f 100644
--- a/user-prompts/multi-agent-brainstorming.md
+++ b/user-prompts/multi-agent-brainstorming.md
@@ -4,6 +4,7 @@
 
 --- COPY BELOW THIS LINE ---
 
+````xml
 <brainstorming_session>
 <role>
 You are a multi-expert brainstorming coordinator. Activate six specialized expert personas to analyze the problem from their unique domain perspectives. Each persona MUST respond independently before any synthesis occurs.
@@ -126,3 +127,4 @@ Paste your problem statement here. Be specific about the domain, constraints, an
 
 </problem_to_analyze>
 </brainstorming_session>
+````
diff --git a/user-prompts/perplexity-deep-research.md b/user-prompts/perplexity-deep-research.md
index 20f45e5..ccb5cc1 100644
--- a/user-prompts/perplexity-deep-research.md
+++ b/user-prompts/perplexity-deep-research.md
@@ -4,6 +4,7 @@
 
 --- COPY BELOW THIS LINE ---
 
+````markdown
 ## Custom Research Prompt for Perplexity (3‑Step Framework)
 
 You are Perplexity, an AI assistant developed by Perplexity AI.
@@ -53,3 +54,4 @@ Goal: answer the exact scenario with high precision.
 ## ACTUAL RESEARCH QUESTION TO EXECUTE NOW:
 
 [AI WILL INSERT THE SPECIFIC, HIGHLY-TARGETED RESEARCH QUESTION HERE]
+````
diff --git a/user-prompts/persian-to-english-dictation.md b/user-prompts/persian-to-english-dictation.md
index 12b7e76..d0c4b28 100644
--- a/user-prompts/persian-to-english-dictation.md
+++ b/user-prompts/persian-to-english-dictation.md
@@ -4,6 +4,7 @@
 
 --- COPY BELOW THIS LINE ---
 
+````xml
 <role>
 You are an elite Bilingual Context Engine and Translation API. Your sole purpose is to convert raw, error-prone Persian Speech-to-Text (VTT) transcripts into flawless, native-sounding English.
 </role>
@@ -31,3 +32,4 @@ Before generating your response, you must silently evaluate:
 <output_format>
 [Insert the flawless English translation directly. Zero conversational filler.]
 </output_format>
+````
diff --git a/user-prompts/session-compactor.md b/user-prompts/session-compactor.md
index 71c4f8a..428b22b 100644
--- a/user-prompts/session-compactor.md
+++ b/user-prompts/session-compactor.md
@@ -4,6 +4,7 @@
 
 --- COPY BELOW THIS LINE ---
 
+````xml
 <role>
 You are an elite Context Compaction Specialist and Systems Archivist. Your objective is to perform a Semantic Context Compaction of our current development session, extracting all critical technical state, decisions, and progress into a highly condensed Context Restoration Report.
 </role>
@@ -72,3 +73,4 @@ Your response must begin with the `<reasoning_log>`, followed immediately by thi
 
 [Provide a clear, directive prompt instructing the AI in the new blank session on how to digest this report, load the listed files, and seamlessly take over the project without asking redundant onboarding questions.]
 </output_format>
+````
diff --git a/user-prompts/voice-to-text-enhancer.md b/user-prompts/voice-to-text-enhancer.md
index 84da2ed..ecd5081 100644
--- a/user-prompts/voice-to-text-enhancer.md
+++ b/user-prompts/voice-to-text-enhancer.md
@@ -4,6 +4,7 @@
 
 --- COPY BELOW THIS LINE ---
 
+````xml
 <role>
 You are an expert Voice-to-Text Processor and Prompt Architect. Your sole purpose is to take raw, messy spoken dictation and transform it into a perfectly polished, highly coherent, and actionable English prompt.
 </role>
@@ -32,3 +33,4 @@ Before generating your response, you must silently evaluate:
 <output_format>
 [Insert the cleaned, enhanced Markdown text directly. Zero conversational filler.]
 </output_format>
+````
```
<!-- END_GIT_DIFF -->
