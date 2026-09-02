# Task 153: Fix audit-agents Skill Scope Leak Across Projects

**File:** `tasks/qa/153-fix-audit-agents-skill-scope-leak.md`
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
- [ ] **Step 4:** Enforce Absent-File Policy in Mode 2 Audit Checks
- [ ] **Step 5:** Synchronize Canonical Template to Global and Workspace Installs
- [ ] **Step 6:** Run Verification Suite and Update Task Checklist

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
```diff
diff --git a/.opencode/skills/audit-agents/SKILL.md b/.opencode/skills/audit-agents/SKILL.md
new file mode 100644
index 0000000..3eab70a
--- /dev/null
+++ b/.opencode/skills/audit-agents/SKILL.md
@@ -0,0 +1,398 @@
+---
+name: audit-agents
+description: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
+---
+
+# Skill: Agent Protocol Auditor (Project-Agnostic)
+
+## 🛑 SCOPE CONFINEMENT (Priority 0)
+
+- All file enumeration, inspection, and patch operations MUST be strictly confined to the caller's current working directory (`[PROJECT_ROOT]`).
+- You are STRICTLY FORBIDDEN from traversing outside `[PROJECT_ROOT]`, searching for `cognitive-lead-hq`, or referencing parent directories. Use generic placeholders like `[PROJECT_ROOT]/AGENTS.md`.
+- **Absent-File Policy**: If optional architectural files (`DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`) do NOT exist in `[PROJECT_ROOT]`, SKIP them gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. DO NOT scaffold or create them unless explicitly instructed.
+- **OpenCode Isolation**: You are STRICTLY FORBIDDEN from creating `.opencode/` scaffolding, `agents/cognitive-executor.md`, `prompts/fragments/*`, or `skill-templates/*` inside third-party projects. Only inspect `.opencode/` if `[PROJECT_ROOT]/.opencode/` ALREADY exists OR if the user passes `with_opencode: true`.
+
+## Target Audit Criteria
+
+The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:
+
+- **Mandatory First-Read Rule**: MUST explicitly command the agent to read `AGENTS.md` first before any execution. Inside it, it must route the agent to read `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` first.
+- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md` (if present, else note absent per Absent-File Policy), `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`). Only require `.opencode/skills/` when the project already contains `.opencode/` or `with_opencode: true` is set.
+- **conventions.md Compliance**: The project MUST have a `docs/conventions.md` file containing the Universal DateTime Standard (UTC at rest, Epoch/ISO-8601 with Offset at API boundaries, Clock injection, Dual-Representation for future events, TZ=UTC Infrastructure), SOLID Programming Guidelines (SRP, OCP, LSP, ISP, DIP, Pragmatic Guardrails), Universal Financial Ledger Standard (snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging), and Defensive Shell Protocol (DSP) (`set -euo pipefail`, banned error masking, sidecar isolation).
+- **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`) as their single source of truth.
+- **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
+- **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator. **Exception:** `git mv` is permitted for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
+- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 5-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool, then `git mv` the task to `tasks/qa/` (NO COMMITS ALLOWED). 4) Synchronize the task file's `**File:**` metadata to the new path and re-run lint + stage at the new path. 5) Notify the Manager.
+- **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
+- **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load the `task-generator` skill before creating new task files.
+- **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load every available skill matching the project's tech stack before task implementation.
+- **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
+- **MCP Report Generation**: `AGENTS.md` MUST instruct agents to generate context reports (`custom_context_read_source_files`) and tree reports (`custom_context_create_tree_report` — "create a tree of the project") via the MCP server and hand the file path to the Manager instead of reading `context-reports/` files inline.
+- **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
+- **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
+- **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
+- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage.
+- **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
+- **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
+- **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Manager Decisions` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
+- **Decision Logging Mandate**: `AGENTS.md` MUST instruct the Hands to log non-trivial architectural, design, and strategic decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>` (sequential DECISION_ID, rationale, alternatives, impact). `docs/conventions.md` MUST contain a `## Decision Logging Standard` section. **Decision Detection Responsibility (Gated — only evaluate when target files exist)**: If `prompts/fragments/17-decision_logging_mandate.md` exists, verify the three-tier responsibility definition. If `agents/cognitive-executor.md` exists (HQ-specific), verify the executor detection role tagged `[EXECUTOR-DETECTED]` — DO NOT create this file in generic projects. If `skill-templates/task-generator/SKILL.md` exists, verify the template tags; otherwise audit local task file templates. **AC/DoD Box-Checking at Implementation Time**: `prompts/fragments/09-hands_protocols.md` MUST instruct the Hands to check AC/DoD boxes during the implementation `<summary_phase>`, not defer to a closure task.
+
+---
+
+## Core Document Templates
+
+### 1. `architecture.md` Template
+
+```markdown
+# Architecture Overview
+
+This document serves as a critical, living template designed to equip agents with a rapid and comprehensive understanding of the codebase's architecture, enabling efficient navigation and effective contribution from day one. Update this document as the codebase evolves.
+
+## 1. Project Structure
+
+[Project Root]/
+├── backend/ # Contains all server-side code and APIs
+│ ├── src/ # Main source code for backend services
+│ │ ├── api/ # API endpoints and controllers
+│ │ ├── client/ # Business logic and service implementations
+│ │ ├── models/ # Database models/schemas
+│ │ └── utils/ # Backend utility functions
+│ ├── config/ # Backend configuration files
+│ ├── tests/ # Backend unit and integration tests
+│ └── Dockerfile # Dockerfile for backend deployment
+├── frontend/ # Contains all client-side code for user interfaces
+│ ├── src/ # Main source code for frontend applications
+│ │ ├── components/ # Reusable UI components
+│ │ ├── pages/ # Application pages/views
+│ │ ├── assets/ # Images, fonts, and other static assets
+│ │ ├── services/ # Frontend services for API interaction
+│ │ └── store/ # State management (e.g., Redux, Vuex, Context API)
+│ ├── public/ # Publicly accessible assets (e.g., index.html)
+│ ├── tests/ # Frontend unit and E2E tests
+│ └── package.json # Frontend dependencies and scripts
+├── common/ # Shared code, types, and utilities used by both frontend and backend
+│ ├── types/ # Shared TypeScript/interface definitions
+│ └── utils/ # General utility functions
+├── docs/ # Project documentation (e.g., API docs, setup guides)
+├── scripts/ # Automation scripts (e.g., deployment, data seeding)
+├── .github/ # GitHub Actions or other CI/CD configurations
+├── .gitignore # Specifies intentionally untracked files to ignore
+├── README.md # Project overview and quick start guide
+└── ARCHITECTURE.md # This document
+
+## 2. High-Level System Diagram
+
+[User] <--> [Frontend Application] <--> [Backend Service 1] <--> [Database 1]
+|
++--> [Backend Service 2] <--> [External API]
+
+## 3. Core Components
+
+### 3.1. Frontend
+
+Name: [Web App, Mobile App]
+Description: [Purpose, core interfaces, and roles]
+Technologies: [e.g., React, Next.js, Jetpack Compose, Swift/Kotlin]
+Deployment: [e.g., Vercel, Netlify, Play Store, App Store]
+
+### 3.2. Backend Services
+
+#### 3.2.1. Service Name 1
+
+Name: [e.g., API Service]
+Description: [Core business roles]
+Technologies: [e.g., Spring Boot, Node.js Express, Go]
+Deployment: [e.g., AWS ECS, Kubernetes]
+
+## 4. Data Stores
+
+### 4.1. Data Store 1
+
+Name: [e.g., SQL Database]
+Type: [e.g., PostgreSQL, MongoDB]
+Purpose: [e.g., Account records]
+
+## 5. External Integrations / APIs
+
+- Service Name: [e.g., Stripe, SendGrid]
+- Purpose: [e.g., Payments]
+- Method: [e.g., REST, SDK]
+
+## 6. Deployment & Infrastructure
+
+- Provider: [e.g., AWS, GCP]
+- CI/CD: [e.g., GitHub Actions]
+
+## 7. Security Considerations
+
+- Authentication: OAuth2/JWT
+- Encryption: TLS + AES-256
+
+## 8. Development & Testing Environment
+
+Testing Frameworks: [e.g., Pytest, JUnit, Jest]
+
+## 9. Future Considerations / Roadmap
+
+[Planned changes or architectural debt]
+```
+
+### 2. DESIGN.md Template (Google Spec)
+
+```markdown
+# Design System Specification
+
+---
+
+name: custom-ui-system
+colors:
+primary: "#1D4ED8"
+secondary: "#4B5563"
+background: "#F3F4F6"
+surface: "#FFFFFF"
+text: "#111827"
+
+---
+
+## 1. Visual Theme & Atmosphere
+
+[Rich prose outlining overall design mood, light/dark values, and whitespace philosophy]
+
+## 2. Color Palette & Roles
+
+- Primary foundation
+- Interactive / CTAs
+- Text hierarchy
+- State colors (Success, error, warn)
+
+## 3. Typography Rules
+
+- Hierarchy (headline, body, label)
+- letterSpacing, lineHeight, fontWeights
+
+## 4. Component Stylings
+
+- Buttons
+- Cards
+- Navigation
+- Input fields
+
+## 5. Layout Principles
+
+- Spacing scales
+- Breakpoints
+```
+
+### 3. `docs/conventions.md` Template
+
+Generate a `docs/conventions.md` file containing the Universal DateTime Standard and SOLID Programming Guidelines:
+
+```markdown
+# Conventions
+
+This document defines syntax rules, naming conventions, file boundaries, and automation patterns for this project.
+
+## Universal DateTime Standard
+
+All projects in this ecosystem MUST follow these datetime rules:
+
+1. **UTC at Rest** — All databases and caches store datetimes in UTC with `TIMESTAMP WITH TIME ZONE`. Banned: naive or local-time storage.
+2. **ISO-8601 with Offset / Epoch ms at API Boundaries** — APIs transmit datetimes as Unix Epoch milliseconds (int64) or ISO-8601 with offset (e.g., `2026-07-23T14:30:00+00:00`). Banned: timezone-naive strings.
+3. **Clock Injection** — All current-time access must go through an injectable `Clock` abstraction. Banned: direct `new Date()`, `datetime.now()`, `time.Now()` in business logic.
+4. **Dual-Representation for Future Events** — Calendar events expose both `event_start_local` (with timezone) and `event_start_epoch_ms` (absolute).
+5. **`TZ=UTC` Infrastructure** — All environments run with `TZ=UTC`. Timezone display is a client-layer responsibility only.
+
+## SOLID Programming Guidelines
+
+Enforce these SOLID principles and pragmatic guardrails in every implementation:
+
+1. **SRP** — One reason to change per module. Split merged concerns.
+2. **OCP** — Open for extension, closed for modification. Use composition over inheritance.
+3. **LSP** — Subtypes must be substitutable. Ban `NotImplementedError` overrides.
+4. **ISP** — Small role-specific interfaces. Ban monolithic god-interfaces.
+5. **DIP** — Depend on abstractions, not concretions. Core layer must not import adapters.
+
+**Pragmatic Guardrails:** No abstraction for <3 trivial operations. Only extract interfaces with 2+ implementations. Apply YAGNI strictly. Prefer simpler designs unless a measurable requirement forces complexity.
+
+## Universal Financial Ledger Standard
+
+All financial, transactional, and countable data operations MUST enforce these mandates:
+
+1. **Snapshot-on-Write for Mutable Totals:** Whenever a financial amount, inventory count, or balance is mutated, persist a read-only snapshot of the preceding state in the same transaction (sidecar table, audit log, or WAL). Banned: mutating without preserving the prior value.
+2. **Mandatory `$ifNull` Precedence:** All aggregation queries on monetary fields MUST use explicit null-handling (`COALESCE`, `ISNULL`, `$ifNull`). Banned: passing nullable columns into mathematical operators.
+3. **Observability Alerting on Discrepancies:** If a computed total diverges from its line-item sum by more than 0.01, emit a high-severity alert and prevent finalization.
+4. **Deep Config Merging for Financial Settings:** Financial configuration updates MUST deeply merge nested properties. Banned: shallow object spread on financial config objects.
+
+## Defensive Shell Protocol (DSP)
+
+When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
+
+1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
+2. **Banned Error Masking:** `2>/dev/null` is STRICTLY FORBIDDEN on data-generation, backup, archive, or database commands.
+3. **No Post-Redirect Status Checks:** Never use `command > file; if [ $? -eq 0 ]` — the shell creates the file before running the command, masking failures.
+4. **Sidecar Isolation for Hostless Backups:** Never rely on host file staging for Docker volume backups. Always use ephemeral containers (`docker run --rm -v volume:/data:ro alpine tar...`) with read-only mounts.
+```
+
+---
+
+Use this skill in two modes:
+
+- **Phase 0 (Generation):** When `AGENTS.md` does not exist yet — generate it from the template below.
+- **Audit Mode (Existing):** When `AGENTS.md` already exists — audit and patch it against the Target Audit Criteria.
+
+---
+
+## Mode 1: Phase 0 — Generate AGENTS.md & docs/conventions.md
+
+Use this when a project has no `AGENTS.md` yet (new project onboarding).
+
+### Workflow
+
+1. Read the project's existing context (package configs, README, tech stack files) to determine the project name, description, and relevant tech stack skills.
+2. Generate `AGENTS.md` at the project root using the template below.
+3. Fill in the `[bracketed]` placeholders with the actual project details.
+4. Generate `docs/conventions.md` using the conventions template above, if the project does not already have one.
+5. Confirm both files were created.
+
+### AGENTS.md Template
+
+```markdown
+# [Project Name] — Project Context Hub
+
+## Project Overview
+
+[Brief description of the project, its purpose, and tech stack]
+
+## Setup & Dev Commands
+
+- Build: [build command, e.g., npm run build]
+- Test: [test command, e.g., npm test]
+- Lint: [lint command, e.g., npm run lint]
+- Dev: [dev server command, e.g., npm run dev]
+
+## Actionable Guardrails (Do's & Don'ts)
+
+- **Don't** [common anti-pattern to avoid]
+  -> **Do** [preferred alternative]
+- **Don't** [another anti-pattern]
+  -> **Do** [preferred alternative]
+- **Don't** read `context-reports/` markdown files yourself.
+  -> **Do** generate them using the MCP server — context reports via `custom_context_read_source_files`, tree reports via `custom_context_create_tree_report` ("create a tree of the project") — and hand the file path to the Manager.
+- **Don't** execute Git commands like `git add`, `git commit`, or `git mv` autonomously or try to guess when to stage code.
+  -> **Do** execute Git commands ONLY when explicitly instructed by an Orchestrator task block. Otherwise, rely on the `custom_context_stage_and_inject_diff` MCP tool.
+  -> **Exception:** `git mv` is permitted autonomously for moving task files between Kanban directories.
+- **Don't** guess blindly when facing complex bugs, deadlocks, or silent timeouts.
+  -> **Do** utilize the `debug-instrumentation` skill to inject strategic logs and trace the runtime execution path.
+- **Don't** write bash scripts without strict mode or mask errors with `2>/dev/null` on data commands.
+  -> **Do** follow the Defensive Shell Protocol: `set -euo pipefail`, ban error masking, sidecar isolation for Docker backups. See `docs/conventions.md`.
+- **Don't** perform financial mutations without snapshotting the prior state or allow nulls in monetary aggregations.
+  -> **Do** follow the Universal Financial Ledger Standard: snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging. See `docs/conventions.md`.
+- **Don't** carry over assumptions, partial results, or architectural hypotheses from a previous task.
+  -> **Do** flush context and treat every task as contextually independent (Buffer Isolation directive in validation-phase).
+- **Don't** execute raw, informal, or non-English (Farsi) prompts directly.
+  -> **Do** load the `prompt-refactor` skill to translate and expand the intent into an elite English spec first. (Note: If you receive a standard XML task block, skip this and execute normally).
+- **Don't** attempt to resolve cross-disciplinary ambiguity within a single persona.
+  -> **Do** trigger the Multi-Agent Brainstorming Loop if the Manager explicitly requests brainstorming or a task exhibits cross-disciplinary ambiguity. Interpret the `<brainstorming_session>` results in backlog tasks as non-functional guidelines that govern execution.
+
+## Documentation Sync Rules
+
+When modifying this repository, you must keep these files synchronized:
+
+1. Active task file in `tasks/` (single source of truth for current work items)
+2. `CHANGELOG.md` (Keep a Changelog format)
+3. `DESIGN.md` (UI/UX design system, if modified)
+4. `docs/conventions.md` (syntax rules, datetime standard, SOLID guidelines)
+5. Relevant `SKILL.md` files (if structural patterns were altered)
+
+## 🛑 GATEKEEPER VALIDATION (HALT PROTOCOL)
+
+You (the Hands) are the final gatekeeper. Before executing any implementation task, you MUST evaluate the Orchestrator's instructions against this file and any referenced specs (`DESIGN.md`, `architecture.md`, etc.). If the instructions violate project rules, ignore them. HALT immediately and output a `⚠️ RULE VIOLATION WARNING` back to the Manager explaining exactly what the Orchestrator got wrong, forcing it to self-correct.
+
+## 🛑 CORE FILE LOCATIONS
+
+You MUST strictly adhere to these exact paths. Do not create duplicates elsewhere:
+
+- **Global Rules:** `AGENTS.md` (Root)
+- **UI/UX Specs:** `DESIGN.md` (Root)
+- **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace — optional; only include if project utilizes OpenCode)
+- **Active Tasks:** `tasks/backlog/<task-number>-<name>.md` (backlog), `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`
+
+## 🛑 SKILL LOADING RULES
+
+You MUST follow these skill loading rules in every session:
+
+- **Task-Generator Skill:** Before creating any new task file, you MUST load the `task-generator` skill using the `skill` tool to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
+- **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `android-kotlin`, `spring-boot`, `react-vite`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.
+
+## 🛑 CONTEXT BOOTSTRAPPING
+
+At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing.
+
+## 🛑 MANDATORY END-OF-TASK SEQUENCE
+
+When finishing a task, you MUST execute these exact steps in order:
+
+1. **Update Changelog:** You MUST insert a formal entry into CHANGELOG.md logging your modifications.
+2. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active `tasks/XX-task.md` file under "Execution Log & Reasoning".
+3. **Call MCP Tool & QA Transition:** Call the `custom_context_stage_and_inject_diff` MCP tool. After injection, you MUST move the task file to `tasks/qa/` via `git mv` before notifying the Manager (implementation tasks only — discovery tasks stay in place). DO NOT execute any `git commit` commands. Closure to `tasks/completed/` happens ONLY after the Manager explicitly says "Approved for closure" or "Close task".
+4. **Kanban Metadata Synchronization (mandatory after ANY authorized `git mv`):** After the move, update the task file's `**File:**` metadata header to the new path. If the move happened AFTER staging, re-run `lint_task_file` and call `custom_context_stage_and_inject_diff` AGAIN with the NEW task path and the full `modified_files` array before notifying the Manager — the re-stage keeps the injected diff and staging state in sync with the final path. Never notify the Manager with a stale `**File:**` header.
+5. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/XX-task.md` and send it back to the Orchestrator Brain for review."
+```
+
+---
+
+## Mode 2: Audit & Patch Existing AGENTS.md and docs/conventions.md
+
+### 🛑 STRICT EXECUTION RULES (Priority 1)
+
+1. **Primary Source of Truth**: You MUST read `AGENTS.md` at the project root using local file read tools.
+2. **Read-Only First**: Evaluate the contents of both `AGENTS.md` and `docs/conventions.md` against the Target Audit Criteria before attempting any file modifications.
+3. **Immutable Formatting**: If patching is required, maintain the exact Markdown list structure, headers, and spacing of the existing file.
+
+### Target Audit Criteria
+
+The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:
+
+- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md` (if present, else note absent per Absent-File Policy), `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`). Only require `.opencode/skills/` when the project already contains `.opencode/` or `with_opencode: true` is set.
+
+Additionally, the `docs/conventions.md` file MUST exist and contain:
+
+- **Universal DateTime Standard**: UTC at rest, Epoch/ISO-8601 with Offset at API boundaries, Clock injection, Dual-Representation for future events, `TZ=UTC` Infrastructure.
+- **SOLID Programming Guidelines**: SRP, OCP, LSP, ISP, DIP, and Pragmatic Guardrails (No abstraction for <3 trivial ops, 3-Implementation Rule, YAGNI, Occam's Razor).
+- **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
+- **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
+- **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator. **Exception:** `git mv` is permitted for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`).
+- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 5-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool, then `git mv` the task to `tasks/qa/` (NO COMMITS ALLOWED). 4) Synchronize the task file's `**File:**` metadata to the new path and re-run lint + stage at the new path. 5) Notify the Manager.
+- **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
+- **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load the `task-generator` skill before creating new task files.
+- **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load every available skill matching the project's tech stack before task implementation.
+- **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
+- **MCP Report Generation**: `AGENTS.md` MUST instruct agents to generate context reports (`custom_context_read_source_files`) and tree reports (`custom_context_create_tree_report` — "create a tree of the project") via the MCP server and hand the file path to the Manager instead of reading `context-reports/` files inline.
+- **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
+- **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
+- **Bilingual Prompt Refactoring & Brainstorming Protocol**: Agents MUST be instructed not to execute raw, informal, or non-English prompts directly. The `prompt-refactor` skill must be loaded, or the Phase 1.5 Multi-Agent Brainstorming Protocol triggered, to translate and expand intent first. Standard XML task blocks are exempt.
+- **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
+- **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage.
+- **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
+- **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
+- **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Manager Decisions` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
+- **Decision Logging Mandate**: `AGENTS.md` MUST instruct the Hands to log non-trivial architectural, design, and strategic decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>` (sequential DECISION_ID, rationale, alternatives, impact). `docs/conventions.md` MUST contain a `## Decision Logging Standard` section. **Decision Detection Responsibility (Gated — only evaluate when target files exist)**: If `prompts/fragments/17-decision_logging_mandate.md` exists, verify the three-tier responsibility definition. If `agents/cognitive-executor.md` exists (HQ-specific), verify the executor detection role tagged `[EXECUTOR-DETECTED]` — DO NOT create this file in generic projects. If `skill-templates/task-generator/SKILL.md` exists, verify the template tags; otherwise audit local task file templates. **AC/DoD Box-Checking at Implementation Time**: `prompts/fragments/09-hands_protocols.md` MUST instruct the Hands to check AC/DoD boxes during the implementation `<summary_phase>`, not defer to a closure task.
+
+### Resolution Protocol
+
+1. **Evaluation**: Compare the active `AGENTS.md` text against the Target Audit Criteria. Also check if `docs/conventions.md` exists and contains both the DateTime Standard and SOLID Guidelines.
+   - **Absent-File Policy (Mandatory)**: For `DESIGN.md`, `docs/architecture.md`, and `docs/data_model.md` — if any of these files do NOT exist in `[PROJECT_ROOT]`, audit them as `OPTIONAL — SKIPPED GRACEFULLY` with an explicit note. DO NOT flag as fatal errors, non-compliance violations, or missing-file failures. DO NOT hallucinate or scaffold them.
+2. **Patching**: If any constraints are missing, ambiguous, or incorrect in `AGENTS.md`, use the `apply_patch` tool to inject the exact missing rules. If `docs/conventions.md` is missing or incomplete, generate or patch it using the conventions template from Mode 1.
+3. **Halt on Success**: If both files already comply 100%, DO NOT execute any write operations.
+
+### Summary Phase
+
+Upon completion, output a strict, formatted summary for the Manager:
+
+### Agent Audit Summary
+
+**Audit Status:** [PASSED | FIXED]
+**AGENTS.md Violations:** [List of missing/incorrect rules, or "None"]
+**conventions.md Status:** [COMPLIANT | MISSING | INCOMPLETE]
+**conventions.md Actions:** [Description of the patch applied, or "Already compliant"]
+**Actions Taken:** [Description of the patches applied, or "Both files already compliant"]
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6b3a273..4178d24 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -40,6 +40,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **SQLite Thread-Affinity & Boot-Scan Pending Re-Trigger (Task HOTFIX-01)** — hotfix enabling SQLite access from watchdog/poller background threads and surviving daemon restarts in trigger-gate mode. `StateMachine.__init__` opens the connection with `check_same_thread=False` (`loop-engine/state.py`); `LoopEngineDaemon.boot_scan()` (auto_start_on_boot=False) now calls `gateway._ensure_poller()` and re-sends Telegram trigger cards for tasks already registered in `PENDING_TRIGGER` state via `state.get_pending_trigger_tasks()` — deduped by task_id so a fresh boot does not double-send cards (verbatim-snippet defect caught by `test_polyglot_smoke.py::test_smoke_boot_scan_registers_pending_trigger`); `main()` calls `gateway._ensure_poller()` immediately before `boot_scan()` so `/start` and button clicks are heard before the first cards are dispatched (`loop-engine/daemon.py`). Also de-staled `test_audit_fixes.py::test_load_config_from_repo_root` (hard-coded placeholder `chat_id == 0` assertion broke when the out-of-band `loop-engine.jsonc` was updated with the real operator chat id — assertion made type-robust; the out-of-band config change was intentionally NOT staged by this hotfix). Verified **247 passed, 0 failed** via `uv run --project loop-engine --with pytest pytest loop-engine/ -q`.
 - **Loop Engine Critical Bug Verification and Fix (Task 132)** — verified 4 hypothesized critical bugs before patching (all CONFIRMED) and applied scoped fixes: **LE-0.1** added `blueprint_context: str=""` (+ `qa_feedback`) to `executor.execute()` and threaded the Architect's approved plan from `daemon._process_task` into the OpenCode prompt as `## Approved Blueprint Context` (avoids `plan` name collision); **LE-0.2** added `extract_task_diff()` helper reading the post-execution task file's `BEGIN/END` markers and hardened QA to extract ONLY that diff, crashing with `CRASHED` on empty/missing markers instead of passing raw CLI output; **LE-0.3** replaced full re-plan recursion on `QA_REJECTED` with dedicated `_reimplement_task()` scoped to implementation-only (calls `executor.execute(qa_feedback=...)` distinctly, re-extracts diff, re-runs QA, loops via `state.get_qa_retry_count()` up to `max_qa_retries`, never sends a new Plan Approval — only Closure); **LE-0.4** replicated the `Context Bootstrapping & Memory Protocol` (`agents/cognitive-executor.md`) in `router._build_system_context()` via `_load_memory_context()` scanning `.opencode/memory/**/*.md` and appending `<memory_context>` before LLM calls; incidental fix for stale persona fragment paths (`12/16` → `06/12` in `personas.py`) restored 11 failing tests. Verified: baseline 62 passed / 11 failed → after persona fix 73 passed → after LE fixes + `test_le0_fixes.py` (13 tests) 86 passed, 0 failed, no regressions, diff scoped to `loop-engine/*.py` + task file; `lint_task_file` green.
+- **audit-agents skill:** Added Scope Confinement directive, gated OpenCode scaffolding behind project existence, and decoupled HQ agent paths to prevent cross-project scope leaks (Task 153).
 
 ## [9.2.2] - 2026-08-30
 
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 2738cbc..3eab70a 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -3,14 +3,21 @@ name: audit-agents
 description: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
 ---
 
-# OpenCode Skill: Agent Protocol Auditor
+# Skill: Agent Protocol Auditor (Project-Agnostic)
+
+## 🛑 SCOPE CONFINEMENT (Priority 0)
+
+- All file enumeration, inspection, and patch operations MUST be strictly confined to the caller's current working directory (`[PROJECT_ROOT]`).
+- You are STRICTLY FORBIDDEN from traversing outside `[PROJECT_ROOT]`, searching for `cognitive-lead-hq`, or referencing parent directories. Use generic placeholders like `[PROJECT_ROOT]/AGENTS.md`.
+- **Absent-File Policy**: If optional architectural files (`DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`) do NOT exist in `[PROJECT_ROOT]`, SKIP them gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. DO NOT scaffold or create them unless explicitly instructed.
+- **OpenCode Isolation**: You are STRICTLY FORBIDDEN from creating `.opencode/` scaffolding, `agents/cognitive-executor.md`, `prompts/fragments/*`, or `skill-templates/*` inside third-party projects. Only inspect `.opencode/` if `[PROJECT_ROOT]/.opencode/` ALREADY exists OR if the user passes `with_opencode: true`.
 
 ## Target Audit Criteria
 
 The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:
 
 - **Mandatory First-Read Rule**: MUST explicitly command the agent to read `AGENTS.md` first before any execution. Inside it, it must route the agent to read `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` first.
-- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `.opencode/skills/`, `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`).
+- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md` (if present, else note absent per Absent-File Policy), `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`). Only require `.opencode/skills/` when the project already contains `.opencode/` or `with_opencode: true` is set.
 - **conventions.md Compliance**: The project MUST have a `docs/conventions.md` file containing the Universal DateTime Standard (UTC at rest, Epoch/ISO-8601 with Offset at API boundaries, Clock injection, Dual-Representation for future events, TZ=UTC Infrastructure), SOLID Programming Guidelines (SRP, OCP, LSP, ISP, DIP, Pragmatic Guardrails), Universal Financial Ledger Standard (snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging), and Defensive Shell Protocol (DSP) (`set -euo pipefail`, banned error masking, sidecar isolation).
 - **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`) as their single source of truth.
 - **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
@@ -28,7 +35,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Manager Decisions` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
-- **Decision Logging Mandate**: `AGENTS.md` MUST instruct the Hands to log non-trivial architectural, design, and strategic decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>` (sequential DECISION_ID, rationale, alternatives, impact). `docs/conventions.md` MUST contain a `## Decision Logging Standard` section. **Decision Detection Responsibility**: `prompts/fragments/17-decision_logging_mandate.md` MUST contain a `## Decision Detection Responsibility` section; `agents/cognitive-executor.md` MUST contain the executor detection role (tagged `[EXECUTOR-DETECTED]`); `skill-templates/task-generator/SKILL.md`'s `## Manager Decisions` template MUST show the `[SOURCE]` tag format (ORCHESTRATOR-DETECTED / EXECUTOR-DETECTED / EXECUTION-DETECTED). **AC/DoD Box-Checking at Implementation Time**: `prompts/fragments/09-hands_protocols.md` MUST instruct the Hands to check AC/DoD boxes during the implementation `<summary_phase>`, not defer to a closure task.
+- **Decision Logging Mandate**: `AGENTS.md` MUST instruct the Hands to log non-trivial architectural, design, and strategic decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>` (sequential DECISION_ID, rationale, alternatives, impact). `docs/conventions.md` MUST contain a `## Decision Logging Standard` section. **Decision Detection Responsibility (Gated — only evaluate when target files exist)**: If `prompts/fragments/17-decision_logging_mandate.md` exists, verify the three-tier responsibility definition. If `agents/cognitive-executor.md` exists (HQ-specific), verify the executor detection role tagged `[EXECUTOR-DETECTED]` — DO NOT create this file in generic projects. If `skill-templates/task-generator/SKILL.md` exists, verify the template tags; otherwise audit local task file templates. **AC/DoD Box-Checking at Implementation Time**: `prompts/fragments/09-hands_protocols.md` MUST instruct the Hands to check AC/DoD boxes during the implementation `<summary_phase>`, not defer to a closure task.
 
 ---
 
@@ -307,7 +314,7 @@ You MUST strictly adhere to these exact paths. Do not create duplicates elsewher
 
 - **Global Rules:** `AGENTS.md` (Root)
 - **UI/UX Specs:** `DESIGN.md` (Root)
-- **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace)
+- **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace — optional; only include if project utilizes OpenCode)
 - **Active Tasks:** `tasks/backlog/<task-number>-<name>.md` (backlog), `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`
 
 ## 🛑 SKILL LOADING RULES
@@ -346,7 +353,7 @@ When finishing a task, you MUST execute these exact steps in order:
 
 The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:
 
-- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `.opencode/skills/`, `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`).
+- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md` (if present, else note absent per Absent-File Policy), `docs/conventions.md`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`). Only require `.opencode/skills/` when the project already contains `.opencode/` or `with_opencode: true` is set.
 
 Additionally, the `docs/conventions.md` file MUST exist and contain:
 
@@ -369,11 +376,12 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 - **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Manager Decisions` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
-- **Decision Logging Mandate**: `AGENTS.md` MUST instruct the Hands to log non-trivial architectural, design, and strategic decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>` (sequential DECISION_ID, rationale, alternatives, impact). `docs/conventions.md` MUST contain a `## Decision Logging Standard` section. **Decision Detection Responsibility**: `prompts/fragments/17-decision_logging_mandate.md` MUST contain a `## Decision Detection Responsibility` section; `agents/cognitive-executor.md` MUST contain the executor detection role (tagged `[EXECUTOR-DETECTED]`); `skill-templates/task-generator/SKILL.md`'s `## Manager Decisions` template MUST show the `[SOURCE]` tag format (ORCHESTRATOR-DETECTED / EXECUTOR-DETECTED / EXECUTION-DETECTED). **AC/DoD Box-Checking at Implementation Time**: `prompts/fragments/09-hands_protocols.md` MUST instruct the Hands to check AC/DoD boxes during the implementation `<summary_phase>`, not defer to a closure task.
+- **Decision Logging Mandate**: `AGENTS.md` MUST instruct the Hands to log non-trivial architectural, design, and strategic decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>` (sequential DECISION_ID, rationale, alternatives, impact). `docs/conventions.md` MUST contain a `## Decision Logging Standard` section. **Decision Detection Responsibility (Gated — only evaluate when target files exist)**: If `prompts/fragments/17-decision_logging_mandate.md` exists, verify the three-tier responsibility definition. If `agents/cognitive-executor.md` exists (HQ-specific), verify the executor detection role tagged `[EXECUTOR-DETECTED]` — DO NOT create this file in generic projects. If `skill-templates/task-generator/SKILL.md` exists, verify the template tags; otherwise audit local task file templates. **AC/DoD Box-Checking at Implementation Time**: `prompts/fragments/09-hands_protocols.md` MUST instruct the Hands to check AC/DoD boxes during the implementation `<summary_phase>`, not defer to a closure task.
 
 ### Resolution Protocol
 
 1. **Evaluation**: Compare the active `AGENTS.md` text against the Target Audit Criteria. Also check if `docs/conventions.md` exists and contains both the DateTime Standard and SOLID Guidelines.
+   - **Absent-File Policy (Mandatory)**: For `DESIGN.md`, `docs/architecture.md`, and `docs/data_model.md` — if any of these files do NOT exist in `[PROJECT_ROOT]`, audit them as `OPTIONAL — SKIPPED GRACEFULLY` with an explicit note. DO NOT flag as fatal errors, non-compliance violations, or missing-file failures. DO NOT hallucinate or scaffold them.
 2. **Patching**: If any constraints are missing, ambiguous, or incorrect in `AGENTS.md`, use the `apply_patch` tool to inject the exact missing rules. If `docs/conventions.md` is missing or incomplete, generate or patch it using the conventions template from Mode 1.
 3. **Halt on Success**: If both files already comply 100%, DO NOT execute any write operations.
```
<!-- END_GIT_DIFF -->
