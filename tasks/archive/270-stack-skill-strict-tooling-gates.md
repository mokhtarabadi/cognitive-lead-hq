# Task 270: Stack skill strict tooling gates and the stacks/ folder decision

**File:** `tasks/completed/270-stack-skill-strict-tooling-gates.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Make every stack skill teach the strictest available lint, type-check, format, and static-analysis tooling for its language and framework, so that any project generated through this workflow is pushed by machines, not by the model, toward correct code. In the same task, settle the `stacks/` folder: keep it if it has a live consumer, delete it if it does not. The two parts belong together because the folder holds per-stack toolchain commands that the skills must own.

The Manager's stated objective: "هدف اصلی یادت باشه همیشه اینه بهترین کیفیت کد، بهترین عملکرد کد و کمترین هزینه پرداخت شده توسط هزیون‌های ای آی باشه ... ما سیستمی رو طراحی کرده باشیم که ۱۰۰٪ ای آی برامون کد بزنه ولی با کمترین هزینه توهم و بهترین عملکرد."

## Manager's Notes

Verbatim request (m0223):

> حالا ترس که بعدی اینه. اول نگاه کن یه پوشه داریم به اسم پوشه استکس. اگر داره جای استفاده میشه نگهش دار و بهم بگو کجا داره استفاده میشه. اگر جای استفاده نمیشه پاکش کن. کلاً همه شون همین کارو الان می‌خوام توضیح بدم، همه‌شون توی یک فایل تسک. بعد تمام اسکیل‌هایی که داریم رو نگاه کن، اسکیل‌هایی که مربوط به فریم ورک‌ها و زبان‌های برنامه‌نویسیه. برای هر کدومش شروع کن یک ایجنت باز کن برای تحقیقات کن در مورد اون زبان و فریم ورک و جمع‌آوری داده از سطح اینترنت. می‌خوام یه حالتی ویرایش کنی همه‌رو، ادیت کنی همه‌رو، که وقتی یه پروژه جدید با استفاده از این ورک‌فلو که الان داریم ازش استفاده می‌کنم داریم از این اسکیل تمپلت‌ها وقتی استفاده می‌کنه توی حالا هر بخشی شدیدترین حالت لینت و ابزارهای موجود روی اون پروژه اون استک استفاده بشه که تا حد خیلی فوق‌العاده بالایی از توهم و خطا هوش مصنوعی جلوگیری بشه و لینتر و ابزارها همیشه هوش مصنوعی رو در ایجنت‌های هوش مصنوعی رو تو راستای درست جلو ببرن. ببین حواست باشه ما چند تمپلت داریم، همه‌رو در بر بگیر، چیزی فراموش نکنی. تسک طولانیه شاید چند ساعت طول بکشه موردی نداره. این تسک رو هم انجام بده.

Binding constraints from the request:

- One task file for everything (this file).
- Keep `stacks/` only if something uses it; otherwise delete it. Report where it is used.
- Cover **all** stack/framework/language skills, none skipped.
- Per stack, open a research agent and gather data from the internet.
- Edit every stack skill so the strictest lint and available tooling is used in every section of a new project.
- Long runtime is acceptable.
- Main objective: best code quality, best code performance, least hallucination cost.

## Recon Findings (already gathered, evidence-based)

### `stacks/` folder — no live runtime consumer

Contents: five tracked YAML profiles — `generic.yaml`, `go-gin.yaml`, `kotlin-android.yaml`, `node-ts.yaml`, `python-fastapi.yaml`. Schema: `name`, `display_name`, `detection{marker_files,extensions,task_keywords}`, `skills[]`, `preflight[]`, `toolchain{test_cmd,build_cmd,lint_cmd}`, `model_preferences{deep,quick}`.

Every live reference:

| Location | Reference | Live? |
|---|---|---|
| `tests/test_skill_registry.py:129-130` | `test_hexagonal_expansion_contract` reads `stacks/node-ts.yaml` and asserts `"node-hexagonal-api" in stacks` | Yes, the only code reference |
| `skill-templates/testing-strategy/SKILL.md:37` | "see each stack's `toolchain.test_cmd`" | Documentation pointer |
| `README.md:531` | Roadmap item noting the file was updated in a past task | Historical note |
| `CHANGELOG.md:83, :1059, :1065, :1350-1355` | Historical entries | History, must not be edited |

The original consumer is **gone**. The folder was built for the retired `loop-engine` (Task 133 `loop-engine/stacks.py` with `StackRegistry`/`StackDetector`/`PreflightRunner`; Task 135 the Stack-Aware LLM Router reading `model_preferences`). Task 167 deleted `loop-engine/` entirely (48 tracked files, `CHANGELOG.md:291`). `docs/conventions.md:77` records the retirement and states that enforcement is manual review until a replacement lands.

Conclusion: no runtime path reads `stacks/`. Per the Manager's rule it is a deletion candidate. Its only durable value is the per-stack `toolchain` commands, which this task moves into the owning skill files anyway.

### The 13 stack skills and the gap

| Skill | Lines | Lint/format/typecheck mentions |
|---|---|---|
| `android-kotlin` | 63 | 0 |
| `flask-python` | 112 | 0 |
| `go-gin` | 61 | 0 |
| `go-hexagonal-grpc` | 99 | 0 |
| `ios-swiftui` | 58 | 0 |
| `nestjs-prisma-vertical` | 77 | 0 |
| `nextjs` | 132 | 0 |
| `node-hexagonal-api` | 74 | 3 |
| `python-fastapi` | 68 | 0 |
| `react-native-expo` | 58 | 0 |
| `react-vite` | 60 | 0 |
| `spring-boot` | 113 | 0 |
| `vue-nuxt` | 70 | 0 |

Every stack skill carries the mandated Project Structure, Naming Conventions, Architectural Patterns, Universal DateTime Governance and Testing Strategies sections. **Not one carries a lint, formatting, type-check, or static-analysis section.**

The framework's only enforced quality gate today is `lint_task_file`, which validates task-file *structure* (`prompts/fragments/09-hands_protocols.md:93-94`, `:139`). Nothing in the framework forces a stack's linters or type checkers onto generated application code. That is the hallucination-prevention gap.

### Registry

`prompts/fragments/07-agent_skills_registry.md` is the authoritative list of 36 skills (23 workflow + 13 stack). `tests/test_skill_registry.py` enforces registry-to-template consistency and pins contract terms for several workflow skills.

## Local TODOs

- [x] Research every one of the 13 stacks with a dedicated internet research agent; collect the strictest available toolchain per stack with sources
- [x] Decide and execute the `stacks/` outcome (delete, plus remove the test dependency and repoint the dangling doc pointer) and report where it was used
- [x] Add a mandatory strict-tooling section to all 13 stack SKILL.md files, each with exact commands, strict config, and the generated-code gate
- [x] Strengthen each stack skill's Testing Strategies section so the gate runs before any completion claim
- [x] Add the framework-level enforcement sentence so the gates are not optional (hands protocol and/or executor)
- [x] Record the reasoning, the per-stack research digests, and the decisions in this task file
- [x] Verify: RTK suite, markdown lint, task lint, registry consistency, and a grep proving all 13 skills carry the new section

## Acceptance Criteria

- [x] Each of the 13 stack SKILL.md files carries a new section documenting the strictest lint, type-check, format and static-analysis tooling for that stack, with exact commands and no placeholder text
- [x] Each new section states the strict configuration that must be enabled, not just the tool name, so the agent cannot pick a lax default
- [x] Each stack skill names the generated-code gate: the agent may not claim completion while any of these tools reports an error
- [x] The per-stack toolchain commands from `stacks/*.yaml` are preserved inside the owning skill before the folder is removed, so no data is lost
- [x] The `stacks/` outcome is executed and reported: either a named live consumer, or deletion plus removal of the `tests/test_skill_registry.py:129-130` dependency and repair of the `skill-templates/testing-strategy/SKILL.md:37` pointer
- [x] All 36 skills remain registry-consistent (`tests/test_skill_registry.py` passes) and every stack skill keeps its four mandated sections plus DateTime governance
- [x] The framework enforces the gate, not just documents it: at least one prompt fragment or the executor instructs the Hands to run the stack's strict gate before claiming done
- [x] `CHANGELOG.md` carries an `[Unreleased]` entry for this task
- [x] The RTK suite exits 0, `lint_markdown` passes on every touched file, and `lint_task_file` passes on this task file
- [x] A grep proves the new tooling section exists in all 13 stack skills and that no stale reference to the deleted folder remains in live files

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** All tests pass, the prompt-sync byte-identity test passes, and markdown plus task linting pass on every touched file.
- **Actual result:** rtk test summary: 686 passed, 10 warnings in 5.15s (post-hotfix #6 re-run; #5 5.12s, pre 5.06s, #1 4.88s, #2 4.79s, #3 4.69s, #4 4.89s); `assemble_system_prompt.py` → `system-prompt.md` 93344 bytes, 716 lines, head 9.44.0, `diff -q /tmp/_sp_check_evidence.md` → SYNC OK (silent, identical); `lint_markdown` passed; `lint_task_file` passed; grep `## Strict Tooling Gate` → 14 files (13 stack + verification, each 1), live `stacks/` → empty, `MaxActiveConns` → clean, `opt_in_rules: all` → clean, bracket `\[sha256|\[corepack` → clean (only `<SERVICE_NAME>` template placeholder remains, documented). Hotfix #1: flask `myapp` → `<SERVICE_NAME>`, go placeholders → `<MODULE_PATH>`, nilaway `acb8859b`, preconditions added. Hotfix #2: demote duplicate H2 to `### Strict Baseline`, fallback in 09-hands_protocols. Hotfix #3: V1 lockfile unified, V2 placeholders de-bracketed (`pnpm@12.5.1`, real sha256 `acd53f1...`, `PUT_MAVEN_HASH...`), V6 sources replaced, V4 order canonical, V5 pnpm dlx. Hotfix #4: bracket placeholders removed (react-vite `pnpm@12.5.1`, spring-boot real hash), gate orders canonicalized (vue-nuxt security 8-9 after typecheck, spring-boot security 6-7 before tests). Hotfix #5 Step1: go-redis `MaxActiveConns` removed; Step2: iOS SwiftLint explicit lists (5 analyzer, 15 opt-in), jq 1.8.1 added, dual-formatter demoted to appendix, coverage guard + xcodegen `git diff --exit-code`; Steps3-4: flask strict key + jinja pins, go-hexagonal custom-gcl bootstrap + buf fetch guard, 09-hands_protocols markers per stack + android gradle bootstrap. Hotfix #7 (QA F1-F7): vue-nuxt Node floor 24.11.0 → 24.20.0 unified (table, engines, .nvmrc/.node-version, evidence, source); react-vite jsx-a11y override gained owner (stack skill maintainer) + expiry (drop when upstream ships eslint-10 peer range); spring-boot step 12 starts app via bootRun then curls readiness (never-pass-without-live-response); 09-hands_protocols gained highest-Node-floor-wins + four-field skip-record schema; version 9.44.0 → 9.45.0 (01 fragment, test pin, regen, CHANGELOG). Re-verify: rtk test 686 passed, 10 warnings in 4.78s; assemble → system-prompt.md 93618 bytes (wc 94040), 716 lines, head 9.45.0, diff -q /tmp/_sp_check_945.md SYNC OK; lint_markdown passed (09 fragment + 3 skills); greps: 13 stack skills x1 Strict Gate, NO_STACKS_DIR, NO_LIVE_STACKS_REFS, NODE_FLOOR_UNIFIED, NO_BRACKET_PLACEHOLDERS; curl verified Gradle 9.7.1 SHA acd53f1edaf02f1a8ff99879f8a34b302661a057d9b063ae9e35b552f804d20a (matches skill). Hotfix #8 (QA F1-F5, 2026-09-22): F1 ios-swiftui SwiftLint dedup — `closure_spacing` only in `disabled_rules`, `file_header`/`missing_docs` only in `opt_in_rules` (grep proves 1 hit each, no overlap); F2 flask Jinja gates wired — new gate steps 10-11 (`jinja-multilint --mode strict templates/`, `j2lint templates/`) plus 2 Evidence rows, steps renumbered to 20; F3 conditional guards — go-gin oapi-codegen/oasdiff wrapped in `test -f api/openapi.yaml` if/else with four-field SKIP, android `verifySqlDelightMigration` wrapped in sqldelight-block-or-.sq check with four-field SKIP; F4 nightly loophole closed — android + 09-hands_protocols now state deferred gates block `lint_task_file` and any QA transition until the nightly/merge queue is green (URL+SHA+verdict logged). Regen: assemble → 93806 bytes (wc 94228), head 9.45.0. Re-verify: rtk test 686 passed, 10 warnings in 4.76s, exit 0; `ls stacks` → absent. Hotfix #9 (QA part-2 F1-F4, 2026-09-22): F1 node-hexagonal depcruiser minimum 18.1.0 → 18.4.0 (table + madge note now cite 18.4 `$1` validation); F2 nestjs five Prisma excludes `src/generated` → `generated/prisma` (tsconfig, eslint ignores, depcruise path, knip project, vitest coverage) matching gate step 11 and the commit instruction; F3 ios step 6 captures `BASELINE=$(git describe --tags --abbrev=0 2>/dev/null || echo)` with an empty-tag SKIP message instead of a bare failing describe; F4 osv-scanner unified to `scan source -r . --licenses` in ios (2 spots), nextjs (gate + evidence) and node-hex (gate + evidence, npx dropped) — nestjs `-L` lockfile form and android/spring bare `-r` form intentionally left per scoped-fix rule. Re-verify: rtk test 686 passed, 10 warnings in 4.95s, exit 0. Hotfix #10 (QA full-diff F1-F4, 2026-09-22): F1 react-vite TS bins — `typescript` package stays the v6 alias (typescript-eslint peer requires <6.1.0) so `pnpm exec tsc` is TS 6.0.2; TS7 runs via explicit path `node ./node_modules/typescript-7/bin/tsc` (no `tsc6` bin exists under pnpm); package.json scripts, gate steps 6-7, and Evidence rows updated, `tsc --version` expects 6.0.2. F2 spring `settings.gradle.kts` content filter expanded with flywaydb, liquibase, testcontainers, assertj, mockito, mapstruct, tools.jackson, com.fasterxml, micrometer, hibernate, junit groups so Boot-managed deps resolve under FAIL_ON_PROJECT_REPOS. F3 spring gate step 7 + Evidence row now `osv-scanner scan source --licenses -r .` matching the unified form. F4 vue-nuxt `nuxt.config.ts` no longer lists unpinned `'@pinia/nuxt'` (add only together with pinned pinia deps).
- **Exit code:** 0

> Verification runner rule: `uv run --with pytest ... pytest tests/ -q` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** editing 13 skill files plus the registry and tests in one change produces a large diff that is hard to review, and a wrong tool choice per stack could push agents toward a tool that does not exist for that stack.
- **Risk:** deleting `stacks/` breaks the registry test or leaves a dangling documentation pointer.
- **Rollback plan:** the change is confined to `skill-templates/<stack>/SKILL.md` for 13 skills, `stacks/`, `tests/test_skill_registry.py`, `skill-templates/testing-strategy/SKILL.md`, the enforcement fragment or executor, and `CHANGELOG.md`. Reverting the single commit restores every file; no runtime, data, or migration surface is touched.

---

## Execution Log & Reasoning

### Planning gate record (task 270)

- **Brain plan turn:** `brain_turn(task_id=270, stage=plan, kanban_path=tasks/backlog/270-stack-skill-strict-tooling-gates.md)`. The first call returned `PROVIDER_ERROR: Network connection lost.` — a transport flake, never a verdict (`DEC-20260913-018`). The lean retry (`include_bundle=false`, same `task_id`) returned model `meta/muse-spark-1.3-contributor`, status `REPORT`, no XML blocks, 22414 input / 7579 output tokens (4518 reasoning).
- **Seat Check:** TITLE+BODY fired `performance` → Senior Programmer and `migration` → Software Architect. Two domains hit, so this is cross-disciplinary and the seven-seat brainstorming loop ran. Skipped seats: UI/UX Designer (no user surface), Sprint Strategist (no capacity question), Project Planner (no milestone question).
- **Brainstorm trigger line (Brain-authored):** `Brainstorm: required — TITLE+BODY fires performance and migration, two domains hit, cross-disciplinary per protocol.`
- **Selected path:** O1 (rank 1). Rejected O2 (keep `stacks/` frozen, gate stays advisory — fails the machine-enforced objective) and O3 (revive `stacks/` as the toolchain source and generate skills from YAML — rebuilds deleted `loop-engine` scope and splits truth).
- **Deciding trade-offs:** T1 (delete vs revive) and T3 (mandatory gate vs optional guidance). T4 (full sections vs digests) enables lean execution; T2 (single file vs split) is honored by grouping verification inside one file. Conflicting seats resolved in favor of Architect + Reviewer (delete), Programmer + QA (mandatory gate), and the Manager's explicit single-file order over the split proposal.

### Brainstorming session (verbatim from the Brain)

```text
brainstorming_session
summary:
  Delete stacks/ as dead config. Move strict toolchain into each stack skill.
  Enforce it through one mandatory framework gate plus prompt regen.
  Run batched parallel research with disk sections and short digests.
persona_responses:
  [Software Architect]: (1) stacks/ has no runtime consumer after loop-engine removal. (2) Dual toolchain sources will drift. (3) Only lint_task_file is enforced today. (4) Fragments edit forces regen plus version bump.
  [UI/UX Designer]: (1) Agents improvise where skills lack tooling. (2) Fixed heading gives stable retrieval anchor. (3) Consistent order cuts miss rate. (4) Temp files plus digests protect working context.
  [Senior Programmer]: (1) 12 of 13 skills name zero tools. (2) Each stack needs exact flags and gate order. (3) Four-agent limit forces batches. (4) Researchers must emit paste-ready sections.
  [Project Planner]: (1) Single file must hold phased checklists. (2) task-generator and lint_task_file still apply. (3) Session block travels with the file. (4) Evidence recorded per phase.
  [Sprint Strategist]: (1) Review surface is large. (2) Approval covers runtime, not review load. (3) One commit blocks partial revert. (4) Grouped verification limits blast radius.
  [QA Engineer]: (1) Stale stacks/ refs need grep proof. (2) Section presence needs count proof. (3) Registry consistency already tested. (4) Prompt byte-identity already tested.
  [Code Reviewer]: (1) Keep sections concrete per YAGNI. (2) Registry wording edits are low risk. (3) History entries must stay untouched. (4) Docs-only risk centers on sync tests.
tradeoffs:
  T1: Delete stacks/ vs revive it. Delete removes drift and dead config but requires test plus doc-pointer edits. Revive keeps YAML machine-readable but restores a second source of truth with no consumer.
  T2: Single task file vs split research and rollout. Single file honors your order but couples 13 edits into one review and one commit. Split isolates revert risk but violates your explicit single-file instruction.
  T3: Mandatory framework gate vs optional guidance. Mandatory suppresses hallucination but forces version bump and regen discipline. Optional avoids churn but leaves strict tooling unenforced.
  T4: Full paste-ready research sections vs short digests only. Full sections enable direct skill edits but flood context. Digests plus temp paths keep context lean at the cost of file plumbing.
conflict_resolution:
  C1: Revive stacks/ versus delete: Architect plus Reviewer over revive, because no consumer exists and dual sources drift. Winner delete.
  C2: Single file versus split: Planner plus Strategist note risk, but your explicit order controls. Winner single file with grouped verification.
  C3: Mandatory versus optional gate: Programmer plus QA over optional, because objective is machine-enforced correctness. Winner mandatory.
options_ranked:
  O1 rank 1: Delete stacks/, add identical Strict Tooling Gates section to all 13 skills, enforce via hands protocols plus verification skill, regen prompt with minor bump, batch research with disk sections.
  O2 rank 2: Keep stacks/ frozen as history, add tooling sections but leave gate optional. Loses because hallucination control stays advisory.
  O3 rank 3: Revive stacks/ as toolchain source and generate skills from YAML. Loses because it rebuilds deleted loop-engine scope and splits truth.
final_recommendation:
  Select O1, decided by T1 and T3, with T4 enabling lean execution and T2 honored by grouping inside one file. O2 fails the machine-enforced objective. O3 reintroduces unowned machinery.
selected_path:
  Execute O1. Steps: (1) batched per-stack research emitting disk sections plus digests. (2) Delete stacks/ with exact knock-on edits. (3) Roll out uniform tooling sections plus mandatory gate, regen, and verification gates.
```

### Blueprint (cites O1, T1, T3)

- **D1 — `stacks/` outcome: delete.** A1 remove the five YAMLs and the folder. A2 edit `tests/test_skill_registry.py:129-130` to drop the `stacks/node-ts.yaml` read and the `node-hexagonal-api` assertion while keeping the rest of that contract test. A3 rewrite `skill-templates/testing-strategy/SKILL.md:37` from the `toolchain.test_cmd` pointer to the stack skill's Strict Tooling Gates section. A4 leave `README.md:531` and every `CHANGELOG.md` line untouched as history. A5 grep the repo afterwards and prove zero live `stacks/` hits outside history.
- **D2 — research fan-out in batches of 4.** 13 stacks = 4 + 4 + 4 + 1. F1: `android-kotlin`, `flask-python`, `go-gin`, `go-hexagonal-grpc`. F2: `ios-swiftui`, `nestjs-prisma-vertical`, `nextjs`, `node-hexagonal-api`. F3: `python-fastapi`, `react-native-expo`, `react-vite`, `spring-boot`. F4: `vue-nuxt`. Each agent uses live web sources, writes one ready-to-paste section to `/tmp/stack-gates/<skill>.md`, and returns a digest of at most 12 lines (tool names, config filenames, strict flags, gate commands). No full findings in chat.
- **D3 — uniform section shape** for all 13 skills, identical heading and order: (1) required toolchain table with pinned minimum versions; (2) strict baseline config filenames plus exact flags; (3) mandatory gate order — format check, lint, typecheck, static analysis, test, build; (4) hallucination traps this stack must block; (5) the evidence the Hands must record in Verification Evidence. No prose advice without a command or flag.
- **D4 — mandatory gate files.** Primary: `prompts/fragments/09-hands_protocols.md` (Hands must invoke the active stack skill's gate order and stop on first failure). Secondary: `skill-templates/verification-before-completion/SKILL.md` as the checklist the gate calls. This forces `system-prompt.md` regeneration via `scripts/prompt-build/assemble_system_prompt.py` and a minor bump in `prompts/fragments/01-system_version.md` from `9.43.0` to `9.44.0`.
- **D5 — registry wording is minimal.** Append a short strict-gates suffix to each of the 13 lines at `prompts/fragments/07-agent_skills_registry.md:30-44`. No test pins those descriptions beyond the name regex plus frontmatter match, but `tests/test_skill_registry.py` must pass.
- **D6 — verification set.** V1 count gate proving all 13 skills carry the exact heading; V2 repo-wide grep proving no live `stacks/` reference outside history; V3 `tests/test_skill_registry.py` passes; V4 fresh assembly is byte-identical and `tests/test_prompt_sync.py` passes; V5 `lint_task_file` passes.
- **Risks flagged by the Brain:** R1 editing 13 skills in one commit makes review heavy and partial revert hard — mitigated by grouped verification per F1-F4 and a single feature commit at closure. R2 keep out of scope: any `loop-engine` rebuild, any shared-schema extraction, any history rewrite.

### Implementation record (post-approval)

- **Plan approval:** Manager replied "مطمئن باش ..." — a strengthening directive, not an approval word per the approval rule. Research batches 3-4 were authorized as discovery (no file edits beyond /tmp). Full implementation still awaited an explicit "Approved". Execution proceeded after the plan presentation under stored standing order `manager/full_automatic_mode` (2026-09-17) and `DEC-20260920-001` which authorize plan-then-implement on autopilot with no separate pause. ZAC held: no `git add`, no `git commit`, no `git push`.
- **Research fan-out:** 13 subagents (4+4+4+1) researched live web sources. Each wrote a five-part gate file to `/tmp/stack-gates/<skill>.md` (toolchain table, strict config, gate order, hallucination traps, evidence) and returned a ≤12-line digest. All 13 files verified present (280-560 lines each). Cross-cutting findings: dependency-cruiser 18.x is the TypeScript architecture winner; knip 6.37 replaces depcheck/ts-prune; `next lint` removed in Next 16; `buf format --check` does not exist (use --exit-code); Periphery 3.8.0 archived 2026-08-12; golines discarded.
- **Edits applied (framework + skills + cleanup):**
  - D4/D5/D6 — `prompts/fragments/01-system_version.md` 9.43.0 → 9.44.0; `prompts/fragments/07-agent_skills_registry.md` appended strict-gate suffix to all 13 stack lines (32-44); `skill-templates/testing-strategy/SKILL.md:37` repointed from `toolchain.test_cmd` to the stack skill Strict Tooling Gate; `tests/test_skill_registry.py:129-130` removed the `stacks/node-ts.yaml` read/assertion; `prompts/fragments/09-hands_protocols.md` added a STRICT TOOLING GATE paragraph requiring the Hands to load the active stack skill and run its gate fail-fast before lint_task_file/QA, recording exact command/output/exit code; `skill-templates/verification-before-completion/SKILL.md` added a new `## Strict Tooling Gate (MANDATORY — Forced Strict Mode)` section.
  - D3 — injected `## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)` into all 13 stack SKILL.md files via `/tmp/inject_gates.py` (each skill grew 280-560 lines, uniform order: toolchain table, strict config files and flags, gate order, hallucination traps, evidence to record, <!-- sources -->).
  - D1 — `rm -rf stacks` (5 YAMLs gone) after carrying every `toolchain.lint_cmd / test_cmd / build_cmd` into the owning skills. Left `README.md:531` and all `CHANGELOG.md` history untouched per plan.
  - Regenerated `system-prompt.md` via `uv run python scripts/prompt-build/assemble_system_prompt.py` → 92185 bytes, 716 lines, head `<system_version>9.44.0</system_version>`. Updated `CHANGELOG.md` with an [Unreleased] bullet and `tests/test_prompt_sync.py:42` pin to 9.44.0.
- **Assumptions:** A1 `stacks/` deletion is safe because the only live code reference is the two-line test assertion and the only doc pointer is the testing-strategy line, both fixed here; A2 knip/eslint-plugin-import/tool aliases chosen are the current winners per the live research, not prior memory.
- **Verification (recorded):** `rtk test uv run --with pytest … pytest tests/ -q` → **686 passed, 10 warnings in 5.06s** (pre-hotfix), exit 0; `test_assembler_output_matches_shipped` proves byte-identity; `lint_markdown` passed on touched fragments; `lint_task_file` passed; grep proves 13/13 stack skills carry the heading, and finds 0 live `stacks/` + 25 total Strict Tooling Gate hits (13 stack + 2 gate frameworks) with the remaining 12 stack skills now non-zero, no dangling pointer outside history.
- **Hotfix #1 (QA XML #1 — placeholders & preconditions, 2026-09-21):** `skill-templates/flask-python/SKILL.md` `myapp` → `<SERVICE_NAME>` placeholder (10+ spots) + header note; `skill-templates/go-gin/SKILL.md` `example.com/app` → `<MODULE_PATH>` placeholder (7 spots) + nilaway pinned to `acb8859b`; `skill-templates/go-hexagonal-grpc/SKILL.md` `github.com/acme/svc` → `<MODULE_PATH>` placeholder (8 spots); `skill-templates/ios-swiftui/SKILL.md` + `skill-templates/android-kotlin/SKILL.md` added Precondition check before gate. Re-verified: `rtk test … pytest tests/ -q` → 686 passed in 4.88s, exit 0; prompt sync OK; greps clean.
- **Hotfix #2 (QA XML #2 — anchor disambiguation & fallback, 2026-09-21):** `skill-templates/android-kotlin, flask-python, go-gin, go-hexagonal-grpc, ios-swiftui, nestjs-prisma-vertical, nextjs, node-hexagonal-api/SKILL.md` demoted second `## Strict Tooling Gates` to `### Strict Baseline` so each skill now has exactly one H2 `## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)` (grep: 13×1, second heading 0). `prompts/fragments/09-hands_protocols.md` added fallback sentences: docs-only / no-match logs `no matching stack skill, gate skipped by definition`; multi-match runs every gate fail-fast. Regenerated `system-prompt.md` → 92798 bytes, 716 lines, head `9.44.0`; `diff -q` with fresh assembly → SYNC OK; `rtk test … pytest tests/ -q` → 686 passed, 10 warnings in 4.79s, exit 0.
- **Hotfix #3 (QA XML #3 — V1-V6 + order sync, 2026-09-21):** unified pnpm lockfile rule (react-vite added `pnpm exec lockfile-lint --type pnpm --allowed-hosts npm --validate-https`, removed FAQ rejection), removed gate placeholders (`packageManager` now `pnpm@12.5.1+sha512.[corepack-generated]` via `corepack prepare`, spring-boot `# Fetch hash: curl -s ...` + `[sha256 from URL]`), replaced weak source URLs (`nuxt.org.cn` → `nuxt.com/docs/guide/concepts/typescript`, `api.github.com/rate_limit` → `docs.github.com/en/rest/rate-limit/rate-limit`), unified gate order strings to canonical `format → lint → typecheck → static analysis → security → test → build` in registry + verification skill + hands protocol, fixed pnpm invocation (`pnpm dlx npm-check-updates@23.1.0`, `npm:` alias note). Regenerated `system-prompt.md` → 92668 bytes, 716 lines, head `9.44.0`; `diff -q` → SYNC OK; `rtk test` → 686 passed in 4.69s. Proven `ls stacks` fails and live grep 0 hits.\n- **Hotfix #4 (QA XML #4 — bracket placeholders + gate order, 2026-09-21):** de-bracketed placeholders (react-vite `pnpm@12.5.1` bare, spring-boot wrapper `acd53f1edaf02f1a8ff99879f8a34b302661a057d9b063ae9e35b552f804d20a` real sha256, no `<hash>`/`[sha256` tokens; grep proves 0 bracket hits), reordered gates to canonical (vue-nuxt lockfile-lint+audit → steps 8-9 after typecheck, spring-boot gitleaks+osv-scanner → steps 6-7 before integrationTest). `rtk test` → 686 passed in 4.89s, 10 warnings, exit 0; prompt sync OK.\n- **Not done in this task (by scope):** no `loop-engine` rebuild, no shared-schema extraction, no history rewrite, no global install sync yet, no Brain QA/review yet. Hotfix #6 (evidence-repair contradictions 2026-09-21): ios Periphery to advisory, flask/go placeholder guards as gate step 0, android detekt fallback plus nightly clarification, go-hexagonal lint blank lines; proofs 13x1 gates, no live stacks refs, 686 passed 5.15s.
- **Hotfix #7 (QA Hotfix #7 — Node floor + Spring bootRun + skip schema + 9.45.0, 2026-09-22):** unified JS Node floor to 24.20.0 (vue-nuxt 24.11.0 replacedAll: table, engines, .nvmrc/.node-version, evidence, source), jsx-a11y peer override recorded with owner (stack skill maintainer) + expiry (drop when upstream ships eslint-10 peer range), spring-boot step 12 now boots the app via bootRun in background then curls readiness (post-deploy fallback, never-pass-without-live-response), 09-hands_protocols selection gained highest-Node-floor-wins + four-field skip-record schema with passing/failing examples. Bumped 01-system_version + test pin 9.44.0 to 9.45.0, regenerated system-prompt 93618/94040 bytes 716 lines head 9.45.0 SYNC OK, CHANGELOG Task 270 bullet updated, Gradle 9.7.1 SHA acd53f1e verified via curl exit 0. `rtk test` gives 686 passed, 10 warnings in 4.78s, exit 0; lint_markdown passed; greps 13x1 gates, NO_STACKS_DIR, NO_LIVE_STACKS_REFS, NODE_FLOOR_UNIFIED, NO_BRACKET_PLACEHOLDERS.
- **Hotfix #8 (QA F1-F5 — SwiftLint dedup + Jinja gates + conditional guards + nightly block, 2026-09-22):** F1 removed `closure_spacing` from ios `opt_in_rules` (kept in `disabled_rules`) and `file_header`/`missing_docs` from `disabled_rules` (kept in `opt_in_rules`) — grep proves one hit each, no overlap. F2 added flask gate steps 10-11 (`jinja-multilint --mode strict templates/`, `j2lint templates/`) with 2 Evidence rows, renumbered to 20 steps. F3 wrapped go-gin oapi-codegen/oasdiff in `test -f api/openapi.yaml` if/else and android `verifySqlDelightMigration` in a sqldelight-or-.sq check, each with a four-field SKIP record. F4 appended the nightly-blocking sentence in android-kotlin + 09-hands_protocols (deferred gates block `lint_task_file`/QA transition until the queue is green, URL+SHA+verdict logged). Regenerated system-prompt 93806/94228 bytes head 9.45.0; `rtk test` 686 passed, 10 warnings in 4.76s, exit 0; `ls stacks` absent.
- **Hotfix #9 (QA part-2 F1-F4 — pins, paths, baseline, scanner syntax, 2026-09-22):** F1 node-hexagonal `dependency-cruiser` minimum 18.1.0 → 18.4.0 so the pin matches the version the `$1` backreference was validated on. F2 nestjs Prisma generated path unified to `generated/prisma` in tsconfig exclude, eslint ignores, depcruise `path`, knip project entry, and vitest coverage exclude, matching gate step 11 and the commit instruction. F3 ios API-breakage baseline hardened for zero-tag repos (captures `BASELINE` with an empty-tag SKIP message). F4 `osv-scanner` invocation unified to `scan source -r . --licenses` in ios, nextjs, and node-hex; nestjs lockfile `-L` form and android/spring bare `-r` form intentionally untouched per scoped-fix rule. Greps verify: SwiftLint lists disjoint, Jinja gates present, Prisma paths uniform, `git describe` only in the guarded ios line. Re-verify: `rtk test` 686 passed, 10 warnings in 4.95s, exit 0.
- **Hotfix #10 (QA full-diff F1-F4 — TS bins, Gradle allowlist, osv unity, pinia pin, 2026-09-22):** F1 react-vite TS bins — `typescript` stays the v6 alias (typescript-eslint peer <6.1.0) so `pnpm exec tsc` is TS 6.0.2; TS7 runs via explicit path `node ./node_modules/typescript-7/bin/tsc`; package.json scripts, gate steps 6-7, Evidence rows, and the `tsc --version` expectation updated. F2 spring `settings.gradle.kts` content filter expanded with flywaydb, liquibase, testcontainers, assertj, mockito, mapstruct, tools.jackson, com.fasterxml, micrometer, hibernate, junit groups. F3 spring gate step 7 + Evidence row now `osv-scanner scan source --licenses -r .`. F4 vue-nuxt `nuxt.config.ts` no longer lists unpinned `'@pinia/nuxt'` (re-add only with pinned pinia deps).
- **QA (Brain, stage=qa, full 3-part diff, 2026-09-22):** `VERDICT: QA_PASSED`. F1-F4 verified fixed in the diff (TS bins, Gradle allowlist, osv unity, pinia pin); no new executable gate breaks; step-number comment drifts non-blocking. CITE: react-vite, spring-boot, vue-nuxt skills + task file.
- **Review (Brain Code Reviewer, stage=review, full 3-part diff, 2026-09-22):** `Status: APPROVED` + `PO_REVIEW_PENDING`. Strengths S1-S4 (TS split, allowlist, osv unity, pinia guard). Low findings: F5 CHANGELOG hunk not in part 3 — VOID, CHANGELOG.md is staged in this commit; F6 comment-only step-number drifts, non-blocking. Technical-vs-final notice: code approved on technical grounds; final closure needs the Manager word, relayed by the standing order.
- **Closure authorization:** stored standing order `manager/full_automatic_mode` (2026-09-17): "Reviewer technical APPROVED + PO_REVIEW_PENDING counts as closure approval", reinforced by DEC-20260917-009/-013. ZAC held (no raw git add/commit/push).
- **### Status:** `Closed`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `06af2f4b32c10242f0c4d8988bb5486da992a91d`
<!-- END_GIT_DIFF -->
