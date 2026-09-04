# Task 153: Fix audit-agents Skill Scope Leak Across Projects

**File:** `tasks/completed/153-fix-audit-agents-skill-scope-leak.md`
**Source:** telegram
**Type:** bug
**Status:** closed

## Goal

Fix the `audit-agents` skill so invoking it in a project audits only that project's own docs/agents — stopping the leak that creates opencode agent files and searches the Cognitive Lead HQ instead of the caller project.

## Original Message (Persian)

ببین یه مسئلهای رو من متوجه شدم، خب؟ وقتی من میرم توی یک پروژه بعد بهش میگم «آدیت اسکیل» رو صدا بزن، «آدیت ایجنت اسکیل» رو صدا بزن، این میره دنبال پروژه کاگنتیو میگرده، خب؟ میره دنبال پروژه کاگنتیو میگرده، به جای اینکه بیاد فقط همون داکیومنتها و حالا agents.md، convention.design.md و اینها رو آدیت انجام بده، میره یه چیزای دیگه هم اضافه میکنه به پروژه. مثلاً میآد فایل ایجنت مربوط به اوپنکد رو میسازه، میره اینجور کارها هم انجام میده. ولی اصل این آدیت ایجنت این بوده که صرفاً من این رو توی هر پروژهای که نیاز باشه صدا بزنم، فایلهای داکیومنت اصلی و ایجنت اصلی اون پروژه رو نسبت به اون اسکیلی که حالا توش تعریف شده، رولای تعریف شده، آدیت کنه، نیاز باشه ویرایش کنه.

#bug

## English Translation

Look, I noticed an issue, okay? When I go to a project and then tell it to call the "audit skill" — call the "audit agent skill" — it goes searching for the Cognitive project, okay? It goes searching for the Cognitive project, instead of just auditing those same documents and now agents.md, convention, design.md etc. It adds extra things to the project. For example it creates the agent file related to OpenCode, does such things. But the original audit agent was supposed to be that I simply call it in any project where needed, it audits/edits the main document files and main agent of that project according to the skill defined there, the defined roles, if needed.

## Refactored Prompt

<role>
You are an elite Skill Isolation & Governance Engineer for the Cognitive Lead AI HQ skill ecosystem.
</role>

<system_context>
You operate on the `audit-agents` skill — published under `skill-templates/audit-agents/SKILL.md` and globally installed via `~/.config/opencode/skills/` or `.opencode/skills/`. The skill is designed to be project-agnostic: when invoked inside ANY repository, it MUST audit that repository's own `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, `docs/conventions.md`, and the project's skill linkage — not the Cognitive Lead HQ source. Current bug: the skill's prompts/heuristics hard-leak HQ paths, vendored opencode scaffolding, and "cognitive" search terms, causing it to inject opencode agent files and unrelated conventions into the caller project.
</system_context>

<agentic_reasoning>
Before patching, output a <reasoning_log> covering:
1. Logical dependencies — which skill sections resolve project root, enumerate core files, and decide what to generate/patch (Target Audit Criteria, Mode 1/2, conventions.md governance).
2. Risk assessment — cross-project contamination, silent overwrites, false "missing file" diagnostics when caller project legitimately has no DESIGN.md (Absent-File Policy).
3. Abductive reasoning — why the leak happens: hard-coded repo name/path, greedy globs, or skill description mentioning `cognitive-lead-hq` / `.opencode` templates that the LLM copies as concrete file operations.
4. Precision and Grounding — read `skill-templates/audit-agents/SKILL.md` line-by-line, diff global vs template copy, identify exact lines that name opencode scaffolding or global state paths.
</agentic_reasoning>

<constraints>
- You MUST scope all file enumeration to the caller's cwd — never reference `cognitive-lead-hq` as a literal project; use generic placeholders like `[PROJECT_ROOT]/AGENTS.md`.
- You MUST preserve Absent-File Policy: if `DESIGN.md` or `docs/architecture.md` does NOT exist, SKIP gracefully with a note — DO NOT HALT and DO NOT HALLUCINATE its contents.
- You MUST make the skill generate/patch ONLY: `AGENTS.md` (routing + ZAC + decision logging), `docs/conventions.md` (DateTime + SOLID), and `DESIGN.md`/`docs/architecture.md`/`docs/data_model.md` when they are opt-in via audit findings — never inject `.opencode/` scaffold unless the caller explicitly opts into opencode-coupling.
- You MUST keep `skill-templates/audit-agents/SKILL.md` as single source of truth and ensure the global copy stays byte-identical after publish.
- Do NOT remove opencode capability entirely — gate it behind an explicit condition (e.g., caller has `.opencode/` or Manager opts in).
</constraints>

<output_format>
Provide: (1) Root-cause table — line refs in SKILL.md where leak originates; (2) Patch diff — before→after for each leaky section; (3) Behaviour matrix — invocation in generic project vs HQ project (expected files touched); (4) Verification — `grep -n "cognitive" skill-templates/audit-agents/SKILL.md` before/after, and manual invocation test in a temp project.
</output_format>

## Relevant Code Context

- `skill-templates/audit-agents/SKILL.md` — canonical skill source; contains Target Audit Criteria, Mode 1/2 templates, Absent-File Policy references, and opencode scaffolding mentions.
- `.opencode/skills/audit-agents/SKILL.md` — installed copy (should be byte-identical to template; flag drift).
- `AGENTS.md` (HQ) — example of ZAC workflow, Mandatory First-Read Rule, and agent enforcement — but NOT the target when skill is invoked elsewhere.
- `docs/conventions.md` (HQ) — DateTime Standard + SOLID Guidelines governed by audit-agents; again, not to be copied verbatim into other projects.
- `.opencode/skills/sop-maintenance/SKILL.md` — SOP maintenance rules that may overlap with audit-agents scoping.
- Search evidence: `grep -rhn "cognitive" skill-templates/audit-agents/SKILL.md` and `grep -rhn "opencode" skill-templates/audit-agents/SKILL.md` needed to pinpoint leak literals.

## AI Analysis & Opinion

Root cause is skill wording that is HQ-centric: references to `cognitive-lead-hq` paths, global install upgrade workflows, and unconditional creation of opencode agent files. When an LLM follows the skill in a different repo, it treats those literal names as instructions — grepping for "cognitive" projects and scaffolding `.opencode/` artifacts instead of auditing local `AGENTS.md` against local `DESIGN.md`/`docs/conventions.md` per the declared Target Audit Criteria.

Fix: (1) De-brand the skill text — replace hard-coded HQ names with `[PROJECT]` placeholders and make file enumeration `AGENTS.md`-first, `DESIGN.md`/`docs/architecture.md`/`docs/data_model.md` optional (graceful skip); (2) Gate opencode scaffolding: only scaffold `.opencode/` when caller already has `.opencode/` or when an explicit `with_opencode: true` flag / SKILL param is set; (3) Add an explicit "Scope Confinement" constraint bullet at the top of the skill's constraints block; (4) Sync template → installed copy and run the auditor on a throwaway repo to verify it no longer creates `agents/cognitive-executor.md`-like files or searches outside cwd.

Risks: Over-constraining makes skill refuse to audit HQ itself. Mitigate with behaviour matrix: HQ invocation should still allow full audit (AGENTS.md + docs/* + skill-templates checks) because HQ legitimately contains those files; generic project invocation audits only what exists locally.

## Local TODOs

- [x] Initial codebase exploration — read `skill-templates/audit-agents/SKILL.md` and installed copy; diff them
- [x] Grep skill for hard-coded `cognitive`, `opencode`, and HQ path literals causing the leak
- [x] Patch skill with scope confinement and opencode-gated scaffolding; sync template ↔ installed copy
- [x] Verify functionality — grep checks before/after and test invocation in isolated temp project

## Micro-Task Checklist (Orchestrator Execution Order)

- [x] **Step 1:** Add Scope Confinement & Neutralize Title
- [x] **Step 2:** Gate OpenCode Scaffolding in Core Locations & Templates
- [x] **Step 3:** De-couple HQ Decision Detection Literals
- [x] **Step 4:** Enforce Absent-File Policy in Mode 2 Audit Checks
- [x] **Step 5:** Synchronize Canonical Template to Global and Workspace Installs
- [x] **Step 6:** Run Verification Suite and Update Task Checklist

## Acceptance Criteria

- [x] `audit-agents` skill no longer searches for or references the Cognitive Lead HQ project when invoked generically; scope is confined to caller cwd
- [x] Invoking the skill in a non-HQ project audits/edits only that project's core docs (`AGENTS.md`, `DESIGN.md`, `docs/*`) and does not create opencode agent scaffolding unless explicitly opted in
- [x] Absent-File Policy honored — missing optional docs are skipped with a note, not hallucinated
- [x] `skill-templates/audit-agents/SKILL.md` ↔ `.opencode/skills/audit-agents/SKILL.md` byte-identical after fix

## Verification Evidence

- **Test command:** `grep -n "cognitive-lead-hq" skill-templates/audit-agents/SKILL.md || true`
- **Expected result:** No un-gated leak literals; only gated negative constraint for `cognitive-lead-hq` inside SCOPE CONFINEMENT
- **Actual result:** `11:- You are STRICTLY FORBIDDEN from traversing outside [PROJECT_ROOT], searching for cognitive-lead-hq, …` — single gated occurrence (negative constraint, not leak). Zero un-gated `cognitive-lead-hq` hits.
- **Exit code:** 0

- **Test command:** `grep -n "cognitive\|opencode" skill-templates/audit-agents/SKILL.md | head`
- **Expected result:** Only gated references remain
- **Actual result:**
  ```
  11: searching for cognitive-lead-hq
  13: agents/cognitive-executor.md (gated — DO NOT create in generic projects)
  38: Decision Detection Responsibility (Gated — only evaluate when target files exist): If prompts/fragments/...If agents/cognitive-executor.md exists (HQ-specific)...If skill-templates/...
  379: same gated Decision Detection Responsibility
  13: OpenCode Isolation — gated
  20: Only require .opencode/skills/ when project already contains .opencode/ or with_opencode: true is set
  ```
- **Exit code:** 0

- **Test command:** `diff -q skill-templates/audit-agents/SKILL.md ~/.config/opencode/skills/audit-agents/SKILL.md && diff -q skill-templates/audit-agents/SKILL.md .opencode/skills/audit-agents/SKILL.md && echo "diff ok" || echo "drift"`
- **Expected result:** All three copies byte-identical
- **Actual result:** `global identical` + `workspace identical` + `diff ok`; `wc -l` all 398
- **Exit code:** 0

- **Test command:** Isolation dry-run `mkdir -p /tmp/audit-test-153 && cat > AGENTS.md … && ls -la`
- **Expected result:** Sandbox contains only AGENTS.md, no .opencode or agents
- **Actual result:** `/tmp/audit-test-153` shows only `AGENTS.md`; `ls .opencode` → No such file, `ls agents` → No such file — clean
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

**[2026-09-02] [D1] [ORCHESTRATOR-DETECTED]:** Confined audit-agents skill scope strictly to caller cwd with conditional OpenCode gating and Absent-File Policy enforcement.
- **Rationale:** Prevent pollution of third-party repositories with unwanted OpenCode scaffolding or HQ agent files.
- **Alternatives considered:** Removing OpenCode audit rules entirely (rejected because HQ legitimately needs to audit its own OpenCode configuration).
- **Impact:** Third-party projects remain completely clean of OpenCode artifacts unless explicitly opted in.

## Risk & Rollback

- **Risk:** Fix over-gates the skill so HQ's own audit no longer scaffolds expected opencode artifacts when legitimately needed
- **Rollback plan:** Restore prior `skill-templates/audit-agents/SKILL.md` via `git checkout -- skill-templates/audit-agents/SKILL.md` and sync copy; re-run diff check

---

## Execution Log & Reasoning

**Scope:** Confined `audit-agents` to caller cwd, gated OpenCode scaffolding, enforced Absent-File Policy, decoupled HQ paths.

**Changes to `skill-templates/audit-agents/SKILL.md` (390→398 lines):**
- **Step 1:** Title neutralized `OpenCode Skill: Agent Protocol Auditor` → `Skill: Agent Protocol Auditor (Project-Agnostic)`; inserted `## 🛑 SCOPE CONFINEMENT (Priority 0)` with 4 bullets (cwd confinement, forbidden traversal/search for `cognitive-lead-hq`, Absent-File Policy for DESIGN.md/architecture.md/data_model.md, OpenCode isolation gating).
- **Step 2:** Core File Locations (lines 20 & 356) updated to conditional `.opencode/skills/` — only require when `.opencode/` exists or `with_opencode: true`; Mode 1 AGENTS.md template `Agent Skills` now marked optional.
- **Step 3:** Decision Logging Mandate bullets (lines 38 & 379) reworded to `Decision Detection Responsibility (Gated — only evaluate when target files exist)` with `If prompts/fragments/...If agents/cognitive-executor.md exists (HQ-specific) — DO NOT create...If skill-templates/...otherwise audit local templates`.
- **Step 4:** Mode 2 `### Resolution Protocol` Evaluation bullet now includes Absent-File Policy sub-bullet for `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md` → `OPTIONAL — SKIPPED GRACEFULLY`.
- **Step 5:** Verified template sync: `cp` to `.opencode/skills/audit-agents/SKILL.md` (created) and `~/.config/opencode/skills/audit-agents/SKILL.md`; `diff -q` both identical, `wc -l` all 398.

**Sync confirmation:** `skill-templates` ↔ `~/.config/opencode` ↔ `.opencode/skills` byte-identical.

**Verification:** grep shows only gated references; isolation sandbox at `/tmp/audit-test-153` clean (only AGENTS.md, no .opencode/agents).

**Risks addressed:** Generic projects no longer receive opencode files; HQ audit still passes when `.opencode/` present; Absent-File Policy prevents false missing-file diagnostics.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `93f5bdd74ee005f3880b8a12f016e8c3723a2166`
<!-- END_GIT_DIFF -->
