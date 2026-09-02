# Task 153: Fix audit-agents Skill Scope Leak Across Projects

**File:** `tasks/backlog/153-fix-audit-agents-skill-scope-leak.md`
**Source:** telegram
**Type:** bug
**Status:** open

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

- [ ] Initial codebase exploration — read `skill-templates/audit-agents/SKILL.md` and installed copy; diff them
- [ ] Grep skill for hard-coded `cognitive`, `opencode`, and HQ path literals causing the leak
- [ ] Patch skill with scope confinement and opencode-gated scaffolding; sync template ↔ installed copy
- [ ] Verify functionality — grep checks before/after and test invocation in isolated temp project

## Acceptance Criteria

- [ ] `audit-agents` skill no longer searches for or references the Cognitive Lead HQ project when invoked generically; scope is confined to caller cwd
- [ ] Invoking the skill in a non-HQ project audits/edits only that project's core docs (`AGENTS.md`, `DESIGN.md`, `docs/*`) and does not create opencode agent scaffolding unless explicitly opted in
- [ ] Absent-File Policy honored — missing optional docs are skipped with a note, not hallucinated
- [ ] `skill-templates/audit-agents/SKILL.md` ↔ `.opencode/skills/audit-agents/SKILL.md` byte-identical after fix

## Verification Evidence

- **Test command:** `grep -n "cognitive\|opencode" skill-templates/audit-agents/SKILL.md | head && diff -q skill-templates/audit-agents/SKILL.md .opencode/skills/audit-agents/SKILL.md && echo "diff ok" || echo "drift"`
- **Expected result:** Hard-coded HQ literals removed or gated; template and installed copy identical; grep shows only generic or gated references
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>` where SOURCE is ORCHESTRATOR-DETECTED, EXECUTOR-DETECTED, or EXECUTION-DETECTED. The Orchestrator is expected to pre-seed this section with `[ORCHESTRATOR-DETECTED]` entries during task generation when applicable. For Lite Mode tasks, log a `[LITE]` justification entry.)_

## Risk & Rollback

- **Risk:** Fix over-gates the skill so HQ's own audit no longer scaffolds expected opencode artifacts when legitimately needed
- **Rollback plan:** Restore prior `skill-templates/audit-agents/SKILL.md` via `git checkout -- skill-templates/audit-agents/SKILL.md` and sync copy; re-run diff check

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
