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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 87de7dc..4a194aa 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -13,6 +13,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Brain Bridge tool-description fixes (direct Manager request, no task file):** `brain_turn` now documents `attachment_resume`, the continuation token a truncated response publishes, instead of silently accepting an undocumented parameter. `read_file` now states its five-key return dict and its caps, and `grep_files` now states that it searches only the six text suffixes — so an empty result for a `.py` file reads as "not searched" rather than "no match". The module docstring's four-tool count and its per-project sessions-root paragraph were corrected. No behavior changed; `mcp-brain-bridge/server.py` only. Full suite: **686 passed** (exit 0).
 - **Auditable brainstorm trigger and fragment 11 repair (Task 268):** `prompts/fragments/12-brainstorming_protocol.md` gains an `<auditability>` rule requiring every plan to state one line — `Brainstorm: required | not required — reason` — with cross-disciplinary plus hard-to-reverse work requiring the full seven-seat report; the matching instruction was added to the Planning Gate in `agents/cognitive-executor.md`. `prompts/fragments/11-execution_workflow.md` step 2 is no longer an automatic swarm invocation naming the removed out-of-band panel (`Architect, Security, PM, Strategist, Critical Thinker`) — it is now a conditional check that names exactly the seven `<personas>` seats, and its dead `user-prompts/` Perplexity pointer now points at the `blowsh` skill. Root cause of the earlier miss: Task 180's verification grep searched snake_case identifiers only, so the display name `Critical Thinker` survived. `system-prompt.md` regenerated and `<system_version>` bumped to 9.42.0. No brainstorm skill was created, and brainstorming is not always-on.
 - **Human-readable output style contract (Task 269):** the Manager reported that Manager-facing output reads machine-like rather than human. A four-track deep search — OpenAI Model Spec and the GPT-5.1 guide, Anthropic prompt-engineering and Claude Code output styles, Google Gemini guidance, the published ChatGPT/Claude/Cursor/Copilot/Perplexity/Manus prompts, and readability research from Nielsen Norman Group, GOV.UK, Google and Microsoft style — found that our style contract was prohibitions only, with no positive model of good prose. `prompts/fragments/13-constraints.md` now carries a positive **Manager-Facing Output Style** contract: answer first, an explicit length budget (short 2–5 sentences with no heading; normal 80–180 words or at most 5 bullets), flowing prose with 25 words as a ceiling rather than a target, a structure rule (prose for 1–2 items, flat bullets for 3–7, table only for repeated attributes, never nested), a clean open and close with no preamble and no recap, direct address with a plain word for each specialist term on first use, and pipeline mechanics kept out of the answer body. The **Tone and Demeanor** rule now targets a knowledgeable colleague instead of an impersonal analyst, and **Communication Patterns** grew from five banned phrases to a principle-based tell list covering hedging openers, significance inflation, negative parallelism, rote triples, collaborative preambles and trailing recaps. `prompts/fragments/02-role.md` requires the answer immediately after the persona bracket, `prompts/fragments/20-communication_examples.md` adds good-versus-bad prose pairs, and `agents/cognitive-executor.md` mirrors the contract. No behavior, tool, reasoning-log or XML change, and every evidence and verdict rule is untouched. `system-prompt.md` regenerated and `<system_version>` bumped to 9.43.0. Conflict C1 (the stored English-only rule versus answering in the user's language) was raised for a Manager decision, not auto-resolved.
+- **Stack skill strict tooling gates and the stacks/ folder decision (Task 270):** every stack skill was missing a machine-enforced lint, type-check, format, and static-analysis gate — the framework's only enforced gate checked task-file structure. Thirteen subagents researched the newest strict tooling per stack against live 2026 sources and each skill now carries a uniform **Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)** section with the same five-part shape: required toolchain table with pinned minimum versions, strict baseline config filenames and exact flags, mandatory gate order (format → lint → typecheck → static analysis → security → test → build), stack-specific hallucination traps and the evidence to record. The `stacks/` folder (five YAML profiles) had no live runtime consumer after the `loop-engine` daemon was deleted in Task 167 — its only references were one test assertion and one doc pointer — so it was removed per the Manager's rule, after carrying its toolchain commands into the skills. `prompts/fragments/09-hands_protocols.md` and `skill-templates/verification-before-completion/SKILL.md` now require the active stack skill's gate to run before any completion claim, and the registry in `prompts/fragments/07-agent_skills_registry.md` marks each stack blueprint as gate-included. `system-prompt.md` regenerated and `<system_version>` bumped to 9.45.0 (9.44.0 intermediate; QA hotfix unified the JS Node floor to 24.20.0, made the Spring actuator gate start the app before curling readiness, recorded the jsx-a11y override owner plus expiry, defined the four-field skip-record schema with the highest-Node-floor rule, and verified the Gradle 9.7.1 SHA `acd53f1e` via curl).
 
 ## [9.41.0] - 2026-09-20
 
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index def0ebe..36c8f9b 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.43.0</system_version>
+<system_version>9.45.0</system_version>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 80bcbe4..495bcc2 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -29,17 +29,17 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
-- **android-kotlin**: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development.
-- **flask-python**: Application Factory, Blueprints, SQLAlchemy, and config separation for Flask
-- **go-gin**: Idiomatic Go, Clean Architecture, and Gin routing best practices
-- **go-hexagonal-grpc**: Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx, and Redis caching for ultra-low latency Go backends.
-- **ios-swiftui**: SwiftUI, MVVM, and modern iOS app architecture
-- **nestjs-prisma-vertical**: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development.
-- **nextjs**: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js
-- **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters.
-- **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing.
-- **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps.
-- **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration
-- **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot
-- **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management
+- **android-kotlin**: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **flask-python**: Application Factory, Blueprints, SQLAlchemy, and config separation for Flask — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **go-gin**: Idiomatic Go, Clean Architecture, and Gin routing best practices — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **go-hexagonal-grpc**: Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx, and Redis caching for ultra-low latency Go backends. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **ios-swiftui**: SwiftUI, MVVM, and modern iOS app architecture — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **nestjs-prisma-vertical**: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **nextjs**: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
   </agent_skills_registry>
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index 7cea5e0..6d8df83 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -78,6 +78,7 @@
     CRITICAL RULE 5 (Pre-Commit Verification Gate): For DevOps, infrastructure, or deployment tasks, the verification gate MUST include environment-specific checks (registry authentication, token scope validation, network access) BEFORE staging any files. If ANY pre-commit check fails, HALT and output a `<failure_report>`. Do NOT stage or commit partial work.
     CRITICAL RULE 6 (Evidence Capture): Before proceeding to the `<summary_phase>`, you MUST capture the exact test command, expected result, actual result, and exit code. You MUST write these into the `## Verification Evidence` section of the active task file.
     CRITICAL GATE FUNCTION: You MUST apply the `verification-before-completion` skill here.
+    STRICT TOOLING GATE (Machine-Enforced — Forced Strict Mode): Before the verification gate, you MUST load the active stack skill from `<agent_skills_registry>` that matches the project and execute its **Strict Tooling Gate** section in fail-fast order (format → lint → typecheck → static analysis → security → test → build). Stop on the first failure. No completion claim, no `lint_task_file`, and no QA transition until the gate is green. Record the exact gate command, output, and exit code in `## Verification Evidence`. Selection: match by file markers per stack — `go.mod` (+ `import github.com/gin-gonic/gin` → `go-gin`, `buf.yaml`/`proto` + `go.mod` + `Fx` → `go-hexagonal-grpc`), `build.gradle.kts` (`+ compose` → `android-kotlin`, `+ Spring Boot` → `spring-boot`), `Package.swift`/`*.xcodeproj` → `ios-swiftui`, `pyproject.toml` + `Flask` → `flask-python`, `pyproject.toml` + `FastAPI` → `python-fastapi`, `package.json` + `next.config.*` → `nextjs`, `package.json` + `src/ports/` → `node-hexagonal-api`, `package.json` + `apps/expo` → `react-native-expo`, `vite.config.*` → `react-vite`, `nuxt.config.*` → `vue-nuxt`, `nest-cli.json`/`prisma/schema.prisma` → `nestjs-prisma-vertical`. Multi-match repos MUST run every matching gate in fail-fast order; do not silently skip any. When several JS skills match, use the highest Node floor among them and record it in `## Verification Evidence`. Docs-only or no-match repos MUST log a skip record with four fields — repo root, marker scan list, matched skills list, reason phrase — in `## Verification Evidence`. Passing example: `root=. markers=[package.json] matched=[] reason=no stack marker found`. Failing example (never do this): `skipped gates` with no fields. Deferred gates block `lint_task_file` and any QA transition until the nightly/merge queue is green, with queue URL plus commit SHA plus green verdict logged in `## Verification Evidence`.
     1. Run the test/build command.
     2. If tests fail, you have a maximum of 3 repair attempts. If the error persists after 3 attempts, you MUST HALT immediately and output a `<failure_report>` detailing the exact errors for the Manager.
     3. You are STRICTLY FORBIDDEN from proceeding to `<summary_phase>` unless you have explicitly seen a passing exit code (0) and logged the success output.
diff --git a/skill-templates/android-kotlin/SKILL.md b/skill-templates/android-kotlin/SKILL.md
index 218b19a..e2bd08b 100644
--- a/skill-templates/android-kotlin/SKILL.md
+++ b/skill-templates/android-kotlin/SKILL.md
@@ -57,6 +57,517 @@ Hilt is mandatory. Do not write manual dependency factories.
 | ViewModel (MVI) | Unit (Intent injection)    | JUnit 5 + Turbine (for Flows) |
 | UI / Composable | Snapshot / Compose UI Test | Compose Test                  |
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+### Strict Baseline
+
+Verified against live sources in September 2026. Suggested baseline stack: **Gradle 9.7.1**, **AGP 9.4.0**, **Kotlin 2.4.20**, **Compose BOM 2026.08.00**, **JDK 17** (toolchain), **Gradle Configuration Cache + Isolated Projects** enabled.
+
+### Required Toolchain
+
+| Tool | Purpose | Minimum version | Activate |
+| --- | --- | --- | --- |
+| Gradle | Build engine; dependency verification, locking, version catalogs, configuration cache | 9.7.1 (AGP 9.4 requires ≥9.6.0) | `gradle/wrapper/gradle-wrapper.properties`: `distributionUrl=https\://services.gradle.org/distributions/gradle-9.7.1-bin.zip` |
+| Android Gradle Plugin | Android + bundled Compose lint, R8 full mode, new Variant API | 9.4.0 | `plugins { id("com.android.application") version "9.4.0" }` |
+| Kotlin | Compiler strictness (`allWarningsAsErrors`, explicit API) | 2.4.20 | `plugins { kotlin("android") version "2.4.20" }` (AGP 9.4 also bundles KGP; pin explicitly) |
+| Compose Compiler plugin | Compose compiler + stability reports/metrics | 2.4.20 (= Kotlin version) | `plugins { id("org.jetbrains.kotlin.plugin.compose") version "2.4.20" }` |
+| Jetpack Compose BOM | Align all Compose artifacts | 2026.08.00 (Compose 1.12) | `implementation(platform("androidx.compose:compose-bom:2026.08.00"))` |
+| ktlint | Kotlin formatter/linter engine (stable; 2.0.0-ALPHA-4 is preview, needs JVM 17) | 1.8.0 | Pulled by Spotless: `ktlint("1.8.0")` |
+| Spotless | Format gate that **fails, never auto-fixes** in CI | 8.10.2 | `plugins { id("com.diffplug.spotless") version "8.10.2" }` |
+| detekt | Kotlin static analysis; warnings-as-errors, `buildUponDefaultConfig` | 2.0.0-alpha.6 (plugin id `dev.detekt`; aligned to Kotlin 2.4/AGP 9.3). Fallback: last stable `1.23.8` only supports Kotlin 2.0.21/AGP 8.8.1 — use it only on legacy stacks, and then downgrade the Kotlin/AGP toolchain to match; never mix the alpha config with the stable binary | `plugins { id("dev.detekt") version "2.0.0-alpha.6" }` |
+| detekt-compose-rules | Compose-specific static checks for detekt/ktlint | 0.6.6 (≥0.5.0 supports detekt 2.0) | `detektPlugins("io.nlopez.compose.rules:detekt:0.6.6")` |
+| Android Lint | Bundled AndroidX + Compose lint checks | ships with AGP 9.4.0 | `android { lint { warningsAsErrors = true; abortOnError = true; checkAllWarnings = true } }` |
+| Kover | Coverage verification gate | 0.9.9 | `plugins { id("org.jetbrains.kotlinx.kover") version "0.9.9" }` |
+| Robolectric | JVM Android/Compose unit tests (fast gate) | 4.17 | `testImplementation("org.robolectric:robolectric:4.17")` + `testOptions.unitTests.isIncludeAndroidResources = true` |
+| Compose UI Test | Instrumented UI gate (v2 test APIs are default from Compose 1.11) | BOM 2026.08.00 | `androidTestImplementation("androidx.compose.ui:ui-test-junit4")`, `debugImplementation("androidx.compose.ui:ui-test-manifest")` |
+| SQLDelight | Compile-time SQL typing + migration verification gate | 2.4.0 | `plugins { id("app.cash.sqldelight") version "2.4.0" }` |
+| Dependency Analysis (DAGP) | Unused / undeclared / mis-configured dependencies | 3.19.2 | `plugins { id("com.autonomousapps.build-health") version "3.19.2" }` |
+| Gradle dependency verification | Tamper/provenance detection for every artifact + plugin | built-in (Gradle 6.2+) | `./gradlew --write-verification-metadata sha256 help` → commit `gradle/verification-metadata.xml` |
+| Gradle dependency locking | Reproducible resolved versions | built-in (Gradle 4.8+) | `dependencyLocking { lockAllConfigurations() }` + `./gradlew dependencies --write-locks` |
+| Gradle version catalog | Single source of dependency coordinates | built-in | `gradle/libs.versions.toml` (default catalog) |
+| OSV-Scanner | Dependency CVE scan; reads `gradle.lockfile`, `buildscript-gradle.lockfile`, `gradle/verification-metadata.xml` | 2.6.0 | `osv-scanner scan source -r .` |
+| OWASP dependency-check | Graded CVE gate (`failBuildOnCVSS`) | 13.0.0 | `plugins { id("org.owasp.dependencycheck") version "13.0.0" }` + `./gradlew dependencyCheckAnalyze` |
+| gitleaks | Hardcoded-secret scan (must be ≥8.30.1 — CVE-2026-63728 affects <8.30.1) | 8.30.1 | `gitleaks git . --redact --exit-code 1` |
+| Hilt / Dagger | DI graph validated at compile time via KSP | 2.60.1 (`androidx.hilt` 1.4.0) | `implementation("com.google.dagger:hilt-android:2.60.1")` + `ksp("com.google.dagger:hilt-compiler:2.60.1")` |
+| KSP | Annotation processing (Hilt, Room, SQLDelight interop) | 2.3.11 | `plugins { id("com.google.devtools.ksp") version "2.3.11" }` |
+
+### Strict Baseline Config
+
+All snippets are Kotlin DSL, ready to paste. `./gradlew spotlessCheck`, `detekt`, `lint*`, `koverVerify`, `buildHealth`, and `verifySqlDelightMigration` all fail the build on any violation. **Never run `spotlessApply` / `detekt --auto-correct` in CI.**
+
+#### Bootstrap for fresh repos — Gradle verification
+
+Fresh clones have no `gradle/verification-metadata.xml`. Bootstrap once before enforcing strict mode:
+
+```bash
+./gradlew --write-verification-metadata sha256,pgp help
+git add gradle/verification-metadata.xml gradle/wrapper/gradle-wrapper.properties
+git commit -m "chore: bootstrap Gradle verification metadata"
+```
+
+Commit the file before running `--dependency-verification strict`; otherwise the first strict invocation fails. Verify with `./gradlew --dependency-verification strict help` (exit 0, blocks hallucinated artifacts via crypto-checked allowlist).
+
+#### `gradle/libs.versions.toml` (version catalog)
+
+```toml
+[versions]
+agp = "9.4.0"
+kotlin = "2.4.20"
+ksp = "2.3.11"
+composeBom = "2026.08.00"
+detekt = "2.0.0-alpha.6"
+composeRules = "0.6.6"
+spotless = "8.10.2"
+kover = "0.9.9"
+sqldelight = "2.4.0"
+hilt = "2.60.1"
+androidxHilt = "1.4.0"
+robolectric = "4.17"
+
+[libraries]
+compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "composeBom" }
+androidx-compose-ui = { group = "androidx.compose.ui", name = "ui" }
+androidx-compose-ui-test-junit4 = { group = "androidx.compose.ui", name = "ui-test-junit4" }
+androidx-compose-ui-test-manifest = { group = "androidx.compose.ui", name = "ui-test-manifest" }
+hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
+hilt-compiler = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }
+androidx-hilt-navigation-compose = { group = "androidx.hilt", name = "hilt-navigation-compose", version.ref = "androidxHilt" }
+robolectric = { group = "org.robolectric", name = "robolectric", version.ref = "robolectric" }
+
+[plugins]
+android-application = { id = "com.android.application", version.ref = "agp" }
+kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
+compose-compiler = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
+ksp = { id = "com.google.devtools.ksp", version.ref = "ksp" }
+hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
+detekt = { id = "dev.detekt", version.ref = "detekt" }
+spotless = { id = "com.diffplug.spotless", version.ref = "spotless" }
+kover = { id = "org.jetbrains.kotlinx.kover", version.ref = "kover" }
+sqldelight = { id = "app.cash.sqldelight", version.ref = "sqldelight" }
+build-health = { id = "com.autonomousapps.build-health", version = "3.19.2" }
+dependency-check = { id = "org.owasp.dependencycheck", version = "13.0.0" }
+```
+
+#### Root `build.gradle.kts` — formatter, detekt, dependency hygiene
+
+```kotlin
+plugins {
+    alias(libs.plugins.android.application) apply false
+    alias(libs.plugins.kotlin.android) apply false
+    alias(libs.plugins.compose.compiler) apply false
+    alias(libs.plugins.ksp) apply false
+    alias(libs.plugins.hilt) apply false
+    alias(libs.plugins.detekt)
+    alias(libs.plugins.spotless)
+    alias(libs.plugins.kover)
+    alias(libs.plugins.build.health)
+    alias(libs.plugins.dependency.check)
+}
+
+spotless {
+    kotlin {
+        target("**/*.kt")
+        targetExclude("**/build/**", "**/generated/**")
+        ktlint("1.8.0")
+        trimTrailingWhitespace()
+        endWithNewline()
+    }
+    kotlinGradle {
+        target("**/*.gradle.kts")
+        ktlint("1.8.0")
+    }
+}
+
+detekt {
+    toolVersion = libs.versions.detekt.get()
+    buildUponDefaultConfig = true          // start from ALL default rules
+    allWarningsAsErrors = true             // warnings are hard failures
+    parallel = true
+    config.setFrom(files("$rootDir/config/detekt/detekt.yml"))
+    baseline = file("$rootDir/config/detekt/baseline.xml")
+}
+
+dependencies {
+    detektPlugins("io.nlopez.compose.rules:detekt:${libs.versions.composeRules.get()}")
+}
+
+tasks.withType<dev.detekt.gradle.Detekt>().configureEach {
+    reports {
+        sarif.required.set(true)
+        html.required.set(true)
+        checkstyle.required.set(true)
+    }
+}
+
+dependencyAnalysis {
+    issues {
+        all {
+            onAny { severity("fail") }   // unused + used-transitive + wrong-config + unused processors
+        }
+    }
+}
+
+dependencyCheck {
+    failBuildOnCVSS = 7.0f               // default 11 never fails; set a real gate
+    formats = listOf("SARIF", "HTML")
+    failOnError = true
+}
+```
+
+#### `config/detekt/detekt.yml` — maximally strict ruleset
+
+`buildUponDefaultConfig = true` means this file only needs to raise thresholds/turn previously-off rules on; everything omitted keeps detekt's default (already active for standard rulesets).
+
+```yaml
+build:
+  maxIssues: 0                 # any issue fails the build
+  weights: { complexity: 0, LongParameterList: 2, comments: 0 }
+
+config:
+  validation: true
+  warningsAsErrors: true
+
+complexity:
+  active: true
+  CyclomaticComplexMethod:
+    active: true
+    threshold: 10
+  LongMethod:
+    active: true
+    threshold: 60
+  LongParameterList:
+    active: true
+    functionThreshold: 5
+    constructorThreshold: 7
+    ignoreDefaultParameters: false
+  TooManyFunctions:
+    active: true
+    thresholdInFiles: 15
+    thresholdInClasses: 15
+    thresholdInInterfaces: 15
+    thresholdInObjects: 11
+    thresholdInEnums: 11
+
+style:
+  active: true
+  MaxLineLength:
+    active: true
+    maxLineLength: 120
+    excludePackageStatements: false
+  MagicNumber:
+    active: true
+  WildcardImport:
+    active: true
+  ReturnCount:
+    active: true
+    max: 2
+  UnusedPrivateMember:
+    active: true
+  UnusedPrivateProperty:
+    active: true
+  ForbiddenComment:
+    active: true
+    comments: ['TODO:', 'FIXME:', 'STOPSHIP:']
+  ExplicitApi:                # for library modules
+    active: true
+
+potential-bugs:
+  active: true
+  UnsafeCallOnNullableType:
+    active: true
+    ignoreGetters: false
+  UnsafeCast:
+    active: true
+  CastNullableToNonNullableType:
+    active: true
+  NullableBooleanCheck:
+    active: true
+
+performance:
+  active: true
+
+coroutines:
+  active: true
+  GlobalCoroutineUsage:
+    active: true
+  InjectDispatcher:
+    active: true
+  RedundantSuspendModifier:
+    active: true
+  SleepInsteadOfDelay:
+    active: true
+
+naming:
+  active: true
+  MatchingDeclarationName:
+    active: true
+  FunctionNaming:
+    active: true
+    ignoreAnnotated: ['Composable']
+
+Compose:
+  ComposableAnnotationNaming:
+    active: true
+  ComposableNaming:
+    active: true
+  ComposableParamOrder:
+    active: true
+  CompositionLocalAllowlist:
+    active: true
+  CompositionLocalNaming:
+    active: true
+  ContentEmitterReturningValues:
+    active: true
+  ContentTrailingLambda:
+    active: true
+  DefaultsVisibility:
+    active: true
+  LambdaParameterEventTrailing:
+    active: true
+  LambdaParameterInRestartableEffect:
+    active: true
+  ModifierComposable:
+    active: true
+  ModifierMissing:
+    active: true
+  ModifierReused:
+    active: true
+  MultipleEmitters:
+    active: true
+  MutableParams:
+    active: true
+  PreviewAnnotationNaming:
+    active: true
+  PreviewNamingConvention:
+    active: true
+  PreviewPublic:
+    active: true
+  RememberMissing:
+    active: true
+  UnstableCollections:
+    active: true
+  ViewModelForwarding:
+    active: true
+  ViewModelInjection:
+    active: true
+```
+
+#### Module `app/build.gradle.kts` — lint, compiler strictness, coverage, R8
+
+```kotlin
+android {
+    lint {
+        warningsAsErrors = true        // every warning is an error
+        abortOnError = true            // non-zero exit on any error
+        checkAllWarnings = true        // include issues that are off-by-default
+        checkDependencies = true       // lint transitive library code too
+        checkReleaseBuilds = true
+        baseline = file("lint-baseline.xml")   // freeze-only; see policy below
+        sarifReport = true
+        htmlReport = true
+        absolutePaths = false
+        disable += setOf("GradleDependency", "NewerVersionAvailable") // keep the rest ON
+    }
+
+    testOptions {
+        unitTests.isIncludeAndroidResources = true   // Robolectric
+        unitTests.isReturnDefaultValues = true
+        unitTests.all { it.useJUnitPlatform() }
+    }
+
+    buildTypes {
+        release {
+            isMinifyEnabled = true
+            isShrinkResources = true
+            proguardFiles(
+                getDefaultProguardFile("proguard-android-optimize.txt"),
+                "proguard-rules.pro",
+            )
+            // R8 full mode is the AGP 8+/9+ default. Do NOT add android.enableR8.fullMode=false,
+            // and never add -ignorewarnings (removed in AGP 8; missing classes are hard errors).
+        }
+    }
+}
+
+kotlin {
+    compilerOptions {
+        allWarningsAsErrors.set(true)
+        progressiveMode.set(true)
+        freeCompilerArgs.addAll(
+            "-Xjsr305=strict",   // strict Java interop nullability
+            // "-Xexplicit-api=strict",  // LIBRARY MODULES ONLY (see explicitApi() below)
+        )
+    }
+    // For published/library modules only (not the app):
+    // explicitApi()   // == -Xexplicit-api=strict; requires explicit visibility + return types
+}
+
+// Compose compiler stability reports (run on release; feed the review, catch unstable params)
+composeCompiler {
+    reportsDestination = layout.buildDirectory.dir("compose_reports")
+    metricsDestination = layout.buildDirectory.dir("compose_metrics")
+}
+
+kover {
+    reports {
+        total {
+            verify {
+                rule {
+                    minBound(80)   // total line coverage must be >= 80%
+                    // Optional stricter bound:
+                    // bound { minValue = 70; coverageUnits = CoverageUnit.LINE }
+                }
+            }
+        }
+    }
+}
+```
+
+#### `gradle.properties` — global strict flags
+
+```properties
+# Dependency verification: strict is the default once verification-metadata.xml exists.
+org.gradle.dependency.verification=strict
+org.gradle.dependency.verification.console=verbose
+
+# Reproducibility + strict resource/namespace behavior
+android.nonTransitiveRClass=true
+android.nonFinalResIds=true
+android.enableJetifier=false
+android.defaults.buildfeatures.buildconfig=false
+
+# Kotlin
+kotlin.code.style=official
+
+# Do NOT add: android.enableR8.fullMode=false
+# Do NOT add: android.r8.failOnMissingClasses=false
+# Do NOT add: any -ignorewarnings / -dontwarn blanket in proguard-rules.pro
+```
+
+#### `settings.gradle.kts` — catalog + federated repositories
+
+```kotlin
+dependencyResolutionManagement {
+    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
+    repositories {
+        google {
+            content {
+                includeGroupByRegex("com\\.android.*")
+                includeGroupByRegex("androidx.*")
+                includeGroupByRegex("com\\.google.*")
+            }
+        }
+        mavenCentral()
+    }
+}
+```
+
+#### SQLDelight migration gate (`app/build.gradle.kts`)
+
+```kotlin
+sqldelight {
+    databases {
+        create("AppDatabase") {
+            packageName.set("com.example.db")
+            schemaOutputDirectory.set(file("src/main/sqldelight/databases"))
+            // generate<SourceSet><Db>Schema writes 1.db; verifySqlDelightMigration replays
+            // every .sqm onto 1.db and fails if the result != latest schema.
+        }
+    }
+}
+```
+
+#### Lint baseline policy
+
+`lint-baseline.xml` and `config/detekt/baseline.xml` are **freeze-only**: a baseline may be created once to stop the build failing on pre-existing debt, but it may only shrink. CI must fail on **any new** finding. Never regenerate a baseline to silence new violations; never use `--auto-correct` to rewrite baselines.
+
+### Mandatory Gate Order
+
+> **Precondition:** verify every tool in the Required Toolchain table is installed and matches its pinned minimum version (`java -version`, `./gradlew --version`, `kotlin -version`, `agp` version in `libs.versions.toml`). If any tool is missing or the wrong version, install or update it first and rerun the preflight. Do not proceed to the gates below until this check is green.
+
+1. `./gradlew --dependency-verification strict spotlessCheck` — formatting must be clean (no auto-fix)
+2. `./gradlew detekt` — static analysis, `allWarningsAsErrors`, `maxIssues: 0`
+3. `./gradlew :app:lintDebug :app:lintRelease` — Android/Compose lint, warnings-as-errors
+4. `./gradlew :app:compileDebugKotlin :app:compileReleaseKotlin` — Kotlin strictness (`allWarningsAsErrors`, `-Xjsr305=strict`)
+5. `if grep -rq "sqldelight" --include="*.kts" . || ls app/src/main/sqldelight app/src/commonMain/sqldelight 2>/dev/null | grep -q "\.sq"; then ./gradlew verifySqlDelightMigration; else echo "SKIP verifySqlDelightMigration | no sqldelight block and no .sq/.sqm files | SQLDelight gate not applicable | exit 0 for this step only"; fi` — SQL schema/query + migration compile-time verification
+6. `./gradlew testDebugUnitTest` — JUnit/JUnit5 + Robolectric unit tests
+7. `./gradlew :app:connectedDebugAndroidTest` — Compose UI instrumented tests (requires emulator/device; run as a separate stage)
+8. `./gradlew koverVerify` — coverage must satisfy the min-bound rule
+9. `./gradlew :app:assembleRelease` — R8 full mode; fails on missing classes / broken keep rules
+10. `./gradlew buildHealth` — no unused, undeclared, or mis-configured dependencies
+11. `osv-scanner scan source -r .` — CVE scan over `gradle.lockfile` + `gradle/verification-metadata.xml`
+12. `./gradlew dependencyCheckAnalyze` — OWASP SCA, fails at CVSS ≥ 7.0
+13. `gitleaks git . --redact --exit-code 1` — hardcoded-secret scan
+
+> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI. `--dependency-verification strict` must wrap every Gradle invocation (or keep `org.gradle.dependency.verification=strict` in `gradle.properties`). Gates 7 and 12 are still mandatory: if device emulators / NVD refresh are too slow for per-PR, defer them to a nightly/merge queue and log the deferral, but the release is blocked until that queue is green — deferral is scheduling only, never skipping. Deferred gates block `lint_task_file` and any QA transition until the nightly/merge queue is green, with the queue URL plus commit SHA plus green verdict logged in `## Verification Evidence`.
+
+### Hallucination Traps to Block
+
+- Invented Gradle coordinates or version numbers -> Gradle dependency verification (`gradle/verification-metadata.xml` + `--dependency-verification strict`) fails any artifact not in the crypto-checked allowlist; version-catalog accessors (`libs.*`) fail compilation for non-existent aliases.
+- Fabricated SQL tables/columns/queries or schema drift -> SQLDelight's compile-time code generation (`generateSqlDelightInterface`) rejects invalid SQL, and `verifySqlDelightMigration` replays `.sqm` files and fails if they don't reconstruct the latest schema.
+- Burying or silencing warnings (`@Suppress`, `-ignorewarnings`, `-dontwarn`) -> Kotlin `allWarningsAsErrors`, detekt `allWarningsAsErrors` + `build.maxIssues: 0`, Android Lint `warningsAsErrors = true`, and R8 full mode (missing classes are hard errors since AGP 8; `-ignorewarnings` is removed).
+- Missing ProGuard/R8 keep rules for reflection/DI -> `./gradlew :app:assembleRelease` fails with `Missing classes detected while running R8`, naming the exact classes and pointing at `build/outputs/mapping/release/missing_rules.txt`.
+- Fake or unstable Compose code -> detekt-compose-rules + bundled AndroidX Compose lint + `composeCompiler` class-stability reports (`unstable class ...`), all run before merge.
+- Unsafe null handling (`!!`, unchecked casts, Java-platform nulls) -> detekt `UnsafeCallOnNullableType` / `UnsafeCast` / `CastNullableToNonNullableType` + Kotlin `-Xjsr305=strict`; Kotlin's type system rejects nullable misuse at compile time.
+- Phantom coverage or untested code -> `koverVerify` min-bound rule fails the build unless measured coverage meets the threshold.
+- Dependency cruft and undeclared transitives -> `buildHealth` with `onAny { severity("fail") }` rejects unused deps, used-transitive deps, wrong configurations, and unused annotation processors.
+- Stale or vulnerable libraries, typosquats -> dependency locking + OSV-Scanner (reads the lockfile and verification metadata) + OWASP dependency-check at CVSS ≥ 7.0.
+- Hardcoded secrets (Google API keys, keystore passwords, tokens) -> gitleaks ≥ 8.30.1 with `--exit-code 1`.
+
+### Evidence to Record
+
+Paste the exact command and its verdict into Verification Evidence. Pass criteria:
+
+| Command | Pass criterion / artifact |
+| --- | --- |
+| `./gradlew --dependency-verification strict spotlessCheck` | `BUILD SUCCESSFUL`; zero Spotless violations |
+| `./gradlew detekt` | `BUILD SUCCESSFUL`; `build/reports/detekt/detekt.sarif` shows 0 findings, 0 warnings |
+| `./gradlew :app:lintDebug :app:lintRelease` | `BUILD SUCCESSFUL`; `build/reports/lint-results-*.sarif` with 0 errors, 0 warnings |
+| `./gradlew :app:compileDebugKotlin :app:compileReleaseKotlin` | `BUILD SUCCESSFUL`; no Kotlin warnings |
+| `./gradlew verifySqlDelightMigration` | `BUILD SUCCESSFUL`; migrations reconstruct the latest schema |
+| `./gradlew testDebugUnitTest` | `BUILD SUCCESSFUL`; test report shows 0 failures; Robolectric tests executed |
+| `./gradlew :app:connectedDebugAndroidTest` | `BUILD SUCCESSFUL`; 0 failed Compose UI tests |
+| `./gradlew koverVerify` | `BUILD SUCCESSFUL`; `build/reports/kover/report.xml` line coverage ≥ 80% |
+| `./gradlew :app:assembleRelease` | `BUILD SUCCESSFUL`; no `Missing classes detected while running R8` |
+| `./gradlew buildHealth` | `BUILD SUCCESSFUL`; `build/reports/dependency-analysis/` has no fail-severity advice |
+| `osv-scanner scan source -r .` | Exit 0; no un-ignored vulnerabilities in `gradle.lockfile` / `verification-metadata.xml` |
+| `./gradlew dependencyCheckAnalyze` | `BUILD SUCCESSFUL`; no dependency with CVSS ≥ 7.0 |
+| `gitleaks git . --redact --exit-code 1` | Exit 0; no secrets detected |
+
+<!-- sources -->
+- https://github.com/diffplug/spotless & https://plugins.gradle.org/plugin/com.diffplug.spotless (Spotless 8.10.2)
+- https://plugins.gradle.org/search?term=ktlint (ktlint Gradle plugins; `org.jlleitschuh.gradle.ktlint` 14.2.0, `io.github.usefulness.ktlint-gradle-plugin` 0.14.0)
+- https://github.com/ktlint/ktlint/releases (ktlint 1.8.0 stable, 2.0.0-ALPHA-4; JVM 17 requirement)
+- https://github.com/detekt/detekt/releases & https://detekt.dev/docs/introduction/compatibility (detekt 2.0.0-alpha.6; 1.23.8 last stable)
+- https://detekt.dev/docs/introduction/migration (detekt 2.0 plugin id `dev.detekt`, coordinates `dev.detekt:*`, min JDK 17/Kotlin 2.4/AGP 8.2.2)
+- https://mrmans0n.github.io/compose-rules/detekt/ (compose-rules 0.6.6; detekt 2.0 support matrix)
+- https://developer.android.com/reference/tools/gradle-api/8.9/com/android/build/api/dsl/Lint (lint DSL: warningsAsErrors/abortOnError/checkAllWarnings/checkDependencies)
+- https://developer.android.com/build/releases/agp-9-4-0-release-notes (AGP 9.4.0, Gradle 9.6.0, API 37)
+- https://developer.android.com/build/releases/gradle-plugin-roadmap (AGP 10 / new Variant API migration)
+- https://developer.android.com/agents/skills/performance/r8-analyzer/references/CONFIGURATION (R8 full mode default AGP 8+)
+- https://issuetracker.google.com/issues/243342123 (AGP 8 removed `-ignorewarnings`; missing classes are errors)
+- https://kotlinlang.org/docs/gradle-compiler-options.html & https://kotlinlang.org/api/kotlin-gradle-plugin/ (allWarningsAsErrors, explicitApi / `-Xexplicit-api=strict`)
+- https://github.com/JetBrains/kotlin/releases (Kotlin 2.4.20)
+- https://github.com/Kotlin/kotlinx-kover/releases & https://kotlin.github.io/kotlinx-kover/gradle-plugin/ (Kover 0.9.9 verification rules)
+- https://github.com/autonomousapps/dependency-analysis-gradle-plugin & https://plugins.gradle.org/plugin/com.autonomousapps.dependency-analysis (DAGP 3.19.2, `severity("fail")`)
+- https://docs.gradle.org/current/userguide/dependency_verification.html (verification metadata, strict mode)
+- https://docs.gradle.org/current/userguide/dependency_locking.html (lockAllConfigurations, `--write-locks`)
+- https://docs.gradle.org/current/userguide/version_catalogs.html (version catalog TOML)
+- https://gradle.org/releases/ (Gradle 9.7.1)
+- https://github.com/google/osv-scanner & https://google.github.io/osv-scanner/supported-languages-and-lockfiles/ (OSV-Scanner 2.x; Gradle lockfile + verification-metadata support)
+- https://github.com/dependency-check/dependency-check-gradle & https://dependency-check.github.io/DependencyCheck/dependency-check-gradle/configuration.html (dependency-check 13.0.0, failBuildOnCVSS)
+- https://github.com/gitleaks/gitleaks & https://www.vulncheck.com/advisories/gitleaks-secret-exfiltration-via-non-hermetic-sprig-template-functions-in-report-template-feature (gitleaks 8.30.1 fixes CVE-2026-63728)
+- https://github.com/cashapp/sqldelight/releases & https://sqldelight.github.io/sqldelight/2.4.0/android_sqlite/migrations/ (SQLDelight 2.4.0, verifySqlDelightMigration)
+- https://github.com/robolectric/robolectric/releases (Robolectric 4.17)
+- https://developer.android.com/develop/ui/compose/bom (Compose BOM 2026.08.00)
+- https://developer.android.com/reference/kotlin/androidx/compose/ui/test/junit4/package-summary (Compose v2 test APIs; createAndroidComposeRule)
+- https://developer.android.com/jetpack/androidx/releases/hilt & https://mvnrepository.com/artifact/com.google.dagger/hilt-android (Hilt 2.60.1; androidx.hilt 1.4.0)
+- https://kotlinlang.org/docs/whatsnew2420.html & https://whatsnew.fyi/product/ksp/latest (Kotlin 2.4.20; KSP 2.3.11)
+- https://mvnrepository.com/artifact/io.gitlab.arturbosch.detekt/detekt-gradle-plugin (detekt artifact history)
+
 ## Currency Baseline
 
 - **KSP codegen + Compose BOM:** Use KSP (never KAPT) for Room/Hilt processors, and pin Compose artifacts via the Compose BOM.
diff --git a/skill-templates/flask-python/SKILL.md b/skill-templates/flask-python/SKILL.md
index 8b251d4..59310ab 100644
--- a/skill-templates/flask-python/SKILL.md
+++ b/skill-templates/flask-python/SKILL.md
@@ -107,6 +107,404 @@ Create a `config.py` with at least three classes: `Config` (base), `DevelopmentC
 - Use an in-memory SQLite database for fast test runs.
 - For every Blueprint, write at least one test that validates the route returns the expected status code.
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+### Strict Baseline
+
+> **Substitute `<SERVICE_NAME>`** — replace every `<SERVICE_NAME>` in this file with your actual package name.
+> Example: `myapp` → run `sed -i 's/<SERVICE_NAME>/myapp/g'` after copying the template.
+> Keep the placeholder in the shared skill; never commit a concrete service name.
+> **Placeholder guard:** CI must fail if any `<SERVICE_NAME>` remains (`grep -r "<SERVICE_NAME>" --include="*.toml" --include="*.py" && echo "FAIL: unsubstituted <SERVICE_NAME>" && exit 1`) — this blocks the template from passing the gate without substitution.
+
+### Required Toolchain
+
+| Tool | Purpose | Minimum version | Activate |
+| --- | --- | --- | --- |
+| uv | Lockfile resolution + reproducible env (replaces pip/poetry) | 0.12.17 | `uv add --dev` (uv itself via installer) |
+| Ruff | Formatting + lint (replaces Black, isort, flake8, pyupgrade, flake8-bugbear/bandit subset) | 0.16.8 | `uv add --dev ruff==0.16.8` |
+| Pyright | Primary static type checker, `strict` mode (98% typing-spec conformance) | 1.1.414 | `uv add --dev pyright==1.1.414` |
+| mypy | Secondary/compat type checker, `--strict` | 2.3.1 | `uv add --dev mypy==2.3.1` |
+| ty | Fast beta checker — advisory only, NOT a gate (53% conformance) | 0.0.82 | `uv add --dev ty==0.0.82` (advisory only — do not install as required gate dependency unless project explicitly opts in; Pyright+mypy are the gates) |
+| Bandit | Python AST security scan (SAST) | 1.9.4 | `uv add --dev bandit==1.9.4` |
+| Semgrep | SAST + taint tracking; Flask-specific rules | 1.177.0 | `uv add --dev semgrep==1.177.0` |
+| pip-audit | CVE scan of the resolved dependency set | 2.10.1 | `uv add --dev pip-audit==2.10.1` |
+| vulture | Dead-code / unreachable-code detection | 2.16 | `uv add --dev vulture==2.16` |
+| deptry | Unused / undeclared / transitive dependency detection | 0.25.1 | `uv add --dev deptry==0.25.1` |
+| import-linter | Architecture contracts (layers / independence / forbidden) | 2.15 | `uv add --dev import-linter==2.15` |
+| pytest | Test runner with strict options | 9.1.1 | `uv add --dev pytest==9.1.1` |
+| pytest-cov + coverage.py | Branch coverage + hard threshold | 7.1.0 / 7.16.1 | `uv add --dev pytest-cov==7.1.0 coverage==7.16.1` |
+| pytest-randomly | Test-order randomization (order-dependence gate) | 5.0.0 | `uv add --dev pytest-randomly==5.0.0` |
+| testcontainers | Real Postgres/MySQL in tests (no SQLite substitutes) | 4.15.0 | `uv add --dev "testcontainers[postgres]==4.15.0"` |
+| Alembic | Migration drift gate (`alembic check`) | 1.20.0 | `uv add alembic==1.20.0` (app dep) |
+| Flask | Framework + `flask --app ... routes` runtime gate | 3.1.3 | `uv add flask==3.1.3` |
+| SQLAlchemy | ORM 2.0 `Mapped[]` / `DeclarativeBase` (typed, no stubs) | 2.0.54 | `uv add sqlalchemy==2.0.54` |
+| jinja-multilint | Jinja filter/test-name validation (syntax always fails in strict mode) | 0.1.2 | `uv add --dev jinja-multilint==0.1.2` |
+| j2lint | Jinja template style + `jinja-syntax-error` (S0) | 1.3.0 | `uv add --dev j2lint==1.3.0` |
+
+**Discarded / not needed (2025–2026 verification):**
+- **Black** (26.5.1) — still maintained, but redundant: `ruff format` is Black-compatible and one tool covers format + lint + import sort. Not a gate.
+- **flake8, isort, pyupgrade, pycodestyle, flake8-bandit** — superseded by Ruff rule families (`E/W/F/I/UP/S/B/...`). Archived/avoid.
+- **SQLAlchemy mypy plugin** (`sqlalchemy.ext.mypy.plugin`) — **deprecated** and removed in SQLAlchemy 2.1; it only works up to mypy 1.10.1. Do **not** install `sqlalchemy-stubs` / `sqlalchemy2-stubs` on 2.0; `Mapped[]` + `DeclarativeBase` is PEP 484-native and works in Pyright without plugins.
+- **safety** — older/less maintained than `pip-audit`; prefer pip-audit.
+
+### Strict Baseline Config
+
+**File: `pyproject.toml`** — locking, lint, types, tests, coverage, dead-code, deps.
+
+```toml
+[project]
+requires-python = ">=3.12"
+
+[tool.ruff]
+target-version = "py312"
+line-length = 100
+src = ["src", "tests"]
+required-version = ">=0.16"
+
+[tool.ruff.lint]
+# STRICTEST: every stable rule. Ruff auto-disables conflicting pydocstyle pairs.
+select = ["ALL"]
+# Documented ignore list — only formatter conflicts + genuinely subjective rules.
+ignore = [
+    # -- Rules that conflict with `ruff format` (Ruff docs "Formatter conflicts") --
+    "W191", "E111", "E114", "E117",   # indentation handled by formatter
+    "D206", "D300",                    # docstring formatting / triple quotes
+    "Q000", "Q001", "Q002", "Q003",    # quote style handled by formatter
+    "COM812", "COM819",                # trailing/missing comma
+    "ISC001",                          # implicit str concat (formatter conflict)
+    # -- Alternative docstring formats (ALL auto-disables the conflicting one) --
+    "D203", "D213",
+    # -- Subjective / low-signal noise, documented per project policy --
+    "D100", "D104", "D107",            # missing docstrings on module/package/__init__
+    "ERA001",                          # commented-out code
+    "TD002", "TD003",                  # TODO author / link formatting
+    "FBT001", "FBT002", "FBT003",      # boolean positional args (Flask/CLI callbacks)
+    "ANN401",                          # explicit Any at third-party boundaries
+    "PLR0913",                         # too many arguments (view/CLI signatures)
+    "E501",                            # line length is the formatter's job
+]
+fixable = ["ALL"]
+unfixable = ["F401", "F841"]           # unused import/local must be reviewed, not auto-deleted
+
+[tool.ruff.lint.per-file-ignores]
+"tests/**" = ["S101", "D", "ANN", "ARG", "PLR2004", "SLF001", "T20"]
+"migrations/**" = ["D", "ANN", "INP001", "E501", "T20"]
+"scripts/**" = ["T20", "INP001"]
+"**/__init__.py" = ["F401"]
+
+[tool.ruff.lint.isort]
+known-first-party = ["<SERVICE_NAME>"]
+required-imports = ["from __future__ import annotations"]
+
+[tool.ruff.format]
+quote-style = "double"
+indent-style = "space"
+docstring-code-format = true
+
+# ---------------------------------------------------------------------------
+# TYPE CHECKING — Pyright strict is the authority; mypy strict is the backstop.
+# SQLAlchemy 2.0 typing is NATIVE (Mapped[] + DeclarativeBase): no plugin,
+# no sqlalchemy-stubs / sqlalchemy2-stubs. The old mypy plugin is deprecated
+# and removed in SQLAlchemy 2.1, and only works up to mypy 1.10.1.
+# ---------------------------------------------------------------------------
+[tool.pyright]
+include = ["src", "tests"]
+exclude = ["**/migrations", "**/.venv", "**/build", "**/dist"]
+pythonVersion = "3.12"
+venvPath = "."
+venv = ".venv"
+typeCheckingMode = "strict"
+reportMissingTypeStubs = true
+reportUnnecessaryTypeIgnoreComment = true
+reportUnusedExpression = true
+# strict already implies: reportUnknownMemberType, reportUnknownVariableType,
+# reportUnknownParameterType, reportUnknownArgumentType, reportMissingParameterType,
+# reportMissingTypeArgument, reportUntypedFunctionDecorator, reportPrivateUsage, ...
+
+[tool.mypy]
+python_version = "3.12"
+strict = true
+warn_unreachable = true
+warn_no_return = true
+plugins = []                            # intentionally empty (SQLAlchemy 2.0 needs none)
+enable_error_code = ["ignore-without-code", "redundant-expr", "truthy-bool"]
+exclude = ["migrations/"]
+
+[[tool.mypy.overrides]]
+module = ["tests.*"]
+disallow_untyped_defs = false
+
+# ---------------------------------------------------------------------------
+# TESTS + COVERAGE
+# ---------------------------------------------------------------------------
+[tool.pytest.ini_options]
+minversion = "8.0"
+strict = true
+testpaths = ["tests"]
+addopts = [
+    "-ra",
+    "--tb=short",
+    "--cov=src",
+    "--cov-branch",
+    "--cov-report=term-missing",
+    "--cov-report=xml",
+]
+filterwarnings = ["error"]             # every warning is a failure
+markers = [
+    "integration: requires Docker/testcontainers",
+    "slow: long-running",
+]
+
+[tool.coverage.run]
+branch = true
+source = ["src"]
+parallel = true
+omit = ["*/migrations/*", "*/tests/*", "*/wsgi.py"]
+
+[tool.coverage.report]
+fail_under = 90                         # ratchet upward; never set 100
+show_missing = true
+skip_covered = false
+precision = 1
+exclude_also = [
+    "if TYPE_CHECKING:",
+    "raise NotImplementedError",
+    "if __name__ == .__main__.:",
+    "@(abc\\.)?abstractmethod",
+    "pragma: no cover",
+]
+
+# ---------------------------------------------------------------------------
+# DEAD CODE
+# ---------------------------------------------------------------------------
+[tool.vulture]
+min_confidence = 100                   # only guaranteed-dead code fails CI
+paths = ["src"]
+make_whitelist = false
+ignore_decorators = [
+    "@app.route", "@*.route", "@*.errorhandler",
+    "@*.before_request", "@*.after_request", "@*.teardown_appcontext",
+    "@*.cli.command", "@*.register_blueprint",
+]
+ignore_names = ["create_app", "app", "application", "init_app"]
+
+# ---------------------------------------------------------------------------
+# DEPENDENCY HYGIENE
+# ---------------------------------------------------------------------------
+[tool.deptry]
+known_first_party = ["<SERVICE_NAME>"]
+extend_exclude = ["migrations", "tests", "scripts", "\\.venv", "build", "dist"]
+
+[tool.deptry.per_rule_ignores]
+# runtime-only packages that are never imported directly
+DEP002 = ["gunicorn", "psycopg", "alembic"]
+
+# ---------------------------------------------------------------------------
+# SECURITY SAST
+# ---------------------------------------------------------------------------
+[tool.bandit]
+exclude_dirs = ["tests", "migrations", ".venv"]
+```
+
+**File: `pyproject.toml` (appended) — architecture contracts.**
+
+```toml
+# ---------------------------------------------------------------------------
+# ARCHITECTURE — Flask blueprint / layer boundaries
+# Layers are ordered HIGH -> LOW: a higher layer may import a lower layer,
+# never the reverse. `exhaustive = true` makes any unlisted new layer a failure.
+# ---------------------------------------------------------------------------
+[tool.importlinter]
+root_packages = ["<SERVICE_NAME>"]
+include_external_packages = true
+
+[[tool.importlinter.contracts]]
+name = "Flask layer hierarchy (web -> services -> repositories -> models)"
+type = "layers"
+layers = [
+    "<SERVICE_NAME>.web",           # Blueprints, routes, request/response glue (outer)
+    "<SERVICE_NAME>.services",      # application services / use cases
+    "<SERVICE_NAME>.repositories",  # data access (SQLAlchemy Session)
+    "<SERVICE_NAME>.models",        # SQLAlchemy declarative models (inner)
+]
+exhaustive = true
+
+[[tool.importlinter.contracts]]
+name = "Blueprints are mutually independent"
+type = "independence"
+modules = [
+    "<SERVICE_NAME>.web.billing",
+    "<SERVICE_NAME>.web.auth",
+    "<SERVICE_NAME>.web.admin",
+]
+
+[[tool.importlinter.contracts]]
+name = "Domain models never import Flask, services or web"
+type = "forbidden"
+source_modules = ["<SERVICE_NAME>.models"]
+forbidden_modules = ["flask", "<SERVICE_NAME>.web", "<SERVICE_NAME>.services", "<SERVICE_NAME>.repositories"]
+as_packages = false
+unmatched_ignore_imports_alerting = "warn"
+
+[[tool.importlinter.contracts]]
+name = "Repositories never import the web layer"
+type = "forbidden"
+source_modules = ["<SERVICE_NAME>.repositories"]
+forbidden_modules = ["<SERVICE_NAME>.web"]
+as_packages = false
+```
+
+**File: `tests/test_contract_runtime.py` — Flask runtime correctness gates.**
+
+```python
+from __future__ import annotations
+
+import json
+from pathlib import Path
+
+from <SERVICE_NAME> import create_app
+
+SNAPSHOT = Path(__file__).parent / "snapshots" / "url_map.json"
+
+
+def _url_map_snapshot(app) -> list[list[str]]:
+    return sorted(
+        [rule.rule, ",".join(sorted(rule.methods or [])), rule.endpoint]
+        for rule in app.url_map.iter_rules()
+    )
+
+
+def test_app_factory_imports_and_registers_routes() -> None:
+    app = create_app()
+    assert len(list(app.url_map.iter_rules())) > 1
+    assert "static" in {r.endpoint for r in app.url_map.iter_rules()}
+
+
+def test_url_map_matches_snapshot() -> None:
+    current = _url_map_snapshot(create_app())
+    assert SNAPSHOT.exists(), "missing url_map snapshot; generate with --snapshot"
+    assert current == json.loads(SNAPSHOT.read_text()), (
+        "URL map changed: review route additions/removals, then regenerate snapshot"
+    )
+
+
+def test_every_template_compiles() -> None:
+    app = create_app()
+    with app.app_context():
+        env = app.jinja_env
+        for name in env.list_templates():
+            env.get_template(name)          # raises TemplateSyntaxError on failure
+```
+
+Generate the snapshot once and commit it:
+
+```bash
+uv run python -c "import json,pathlib;from <SERVICE_NAME> import create_app;a=create_app();p=pathlib.Path('tests/snapshots/url_map.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(sorted([[r.rule,','.join(sorted(r.methods or [])),r.endpoint] for r in a.url_map.iter_rules()]),indent=2))"
+```
+
+### Mandatory Gate Order
+
+0. `! grep -r "<SERVICE_NAME>" --include="*.toml" --include="*.py" .` — placeholder guard: fail if any `<SERVICE_NAME>` remains unsubstituted (substitute first via `sed -i 's/<SERVICE_NAME>/myapp/g'`).
+1. `uv lock --check`
+2. `uv sync --locked`
+3. `uv run ruff format --check .`
+4. `uv run ruff check .`
+5. `uv run pyright`
+6. `uv run mypy src`
+7. `uv run lint-imports`
+8. `uv run bandit -c pyproject.toml -r src -lll -iii`
+9. `uv run semgrep --config p/python --config p/flask --config p/owasp-top-ten --error --strict --metrics=off`
+10. `uv run jinja-multilint --mode strict templates/`
+11. `uv run j2lint templates/`
+12. `uv run deptry .`
+13. `uv run pip-audit --locked --strict`
+14. `uv run vulture`
+15. `uv run python -c "from <SERVICE_NAME> import create_app; app = create_app(); assert len(list(app.url_map.iter_rules())) > 1"`
+16. `uv run flask --app <SERVICE_NAME>:create_app routes`
+17. `uv run pytest tests/test_contract_runtime.py -p no:randomly -q`
+18. `uv run pytest -p randomly --cov=src --cov-branch --cov-fail-under=90`
+19. `uv run alembic upgrade head && uv run alembic check`
+20. `uv run pip check`
+
+> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI. `pip-audit --strict` fails if dependency collection itself fails on any package; `semgrep --error` exits 1 on any finding and `--strict` exits 3 on invalid target syntax. Keep `pytest-randomly` enabled in CI (order-dependence is a real defect); the only place to use `-p no:randomly` is a local reproduction/bisect, and reproductions should prefer `--randomly-seed=last`.
+
+### Hallucination Traps to Block
+
+- Invented route/endpoint or broken blueprint registration -> `flask --app <SERVICE_NAME>:create_app routes` + URL-map snapshot test + import-linter `independence`/`forbidden`.
+- Model changed without an Alembic revision -> `alembic upgrade head && alembic check` (non-zero on pending ops) — catch before "Target database is not up to date" in prod.
+- SQLAlchemy 1.x-style `declarative_base()` / untyped `Column()` in code that claims to be 2.0 -> Pyright `strict` + mypy `--strict` against `Mapped[...]` / `DeclarativeBase` (the old mypy plugin is deprecated/removed, so it cannot rescue this).
+- Template referencing an undefined variable, filter, or endpoint -> `env.get_template()` compile test + jinja-multilint `--mode strict` + `j2lint` (S0 jinja-syntax-error).
+- Fabricated/undeclared dependency (import with no matching lock entry) -> `deptry` DEP001/DEP003 and `uv sync --locked` failing on lock drift.
+- Dead or orphaned view/service function presented as wired up -> Ruff `F401/F841` + `vulture --min-confidence 100`.
+- SQL injection / command injection via `request.args` reaching `execute()` or `subprocess` -> Semgrep `p/flask` taint rules + Bandit `-lll` (`B608`, `B602`).
+- Tests that only pass in file order (hidden shared DB/session state) -> `pytest-randomly` order shuffling + `filterwarnings = ["error"]` + transaction-rollback DB fixture.
+- `Any` erasing a type hole, or `# type: ignore` hiding a real error -> mypy `strict` (`disallow_any_generics`, `disallow_untyped_defs`) + Pyright `reportUnnecessaryTypeIgnoreComment`.
+- Hallucinated "hardcoded" URL instead of `url_for()` -> jinja-multilint / pytest-jinja-check hardcoded-route detection.
+
+### Evidence to Record
+
+Paste the command and its pass criterion (all must be green):
+
+| Command | Pass criterion |
+| --- | --- |
+| `uv lock --check && uv sync --locked` | exit 0; `uv.lock` unchanged by the run |
+| `uv run ruff format --check . && uv run ruff check .` | exit 0, `All checks passed!` / no reformatted files |
+| `uv run pyright` | `0 errors` |
+| `uv run mypy src` | `Success: no issues found` |
+| `uv run lint-imports` | `Contracts: N kept, 0 broken` |
+| `uv run bandit -c pyproject.toml -r src -lll -iii` | no HIGH severity, no HIGH confidence findings |
+| `uv run semgrep ... --error --strict` | exit 0 (no ERROR findings, no invalid syntax) |
+| `uv run jinja-multilint --mode strict templates/` | exit 0, no unknown filter/test errors |
+| `uv run j2lint templates/` | exit 0, no S0 jinja-syntax-error |
+| `uv run pip-audit --locked --strict` | `No known vulnerabilities found` |
+| `uv run deptry .` | `Success! No dependency issues found.` |
+| `uv run vulture` | no output, exit 0 |
+| `uv run flask --app <SERVICE_NAME>:create_app routes` | non-empty route table, exit 0 |
+| `uv run pytest -p randomly --cov=src --cov-branch --cov-fail-under=90` | all tests pass; `coverage: total >= 90%` |
+| `uv run alembic upgrade head && uv run alembic check` | `No new upgrade operations detected.` |
+| `uv run pip check` | `No broken requirements found.` |
+
+Record the URL-map snapshot diff (if any) and the pytest-randomly seed printed at run start; the seed is required to reproduce any order-dependent failure.
+
+<!-- sources -->
+- https://docs.astral.sh/ruff/linter/ (ALL selector, rule precedence, formatter-conflict rules)
+- https://docs.astral.sh/ruff/configuration/ (select/ignore/extend-select, per-file-ignores)
+- https://docs.astral.sh/ruff/settings/
+- https://docs.astral.sh/ruff/rules/missing-type-self/ (ANN101 removed — do not list in ignore)
+- https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md (removed rules ANN101/ANN102/E999/PD901/UP038)
+- https://pydevtools.com/handbook/how-to/how-to-configure-recommended-ruff-defaults/
+- https://pydevtools.com/handbook/how-to/how-to-configure-mypy-strict-mode/ (`strict = true` flag set)
+- https://www.danilchenko.dev/posts/ty-vs-mypy-vs-pyright/ (Pyright 98% vs mypy 58% vs ty 53% conformance)
+- https://docs.sqlalchemy.org/en/20/orm/extensions/mypy.html (mypy plugin deprecated, removed in 2.1; Mapped[] is native)
+- https://docs.sqlalchemy.org/en/latest/orm/declarative_styles.html (DeclarativeBase supersedes declarative_base)
+- https://bandit.readthedocs.io/en/latest/man/bandit.html (`-lll` HIGH severity, `-iii` HIGH confidence)
+- https://github.com/pypa/pip-audit (`--strict`, `--require-hashes`, `--locked`)
+- https://github.com/jendrikseipp/vulture (min-confidence, pyproject `[tool.vulture]`)
+- https://deptry.com/usage/ (DEP001–DEP005, per_rule_ignores, known_first_party)
+- https://github.com/osprey-oss/deptry (rules DEP001 missing / DEP002 unused / DEP003 transitive / DEP004 dev)
+- https://docs.semgrep.dev/cli-reference (`--error` exit 1, `--strict` exit 3)
+- https://semgrep.dev/p/flask and https://github.com/semgrep/semgrep-rules (Flask taint rules)
+- https://import-linter.readthedocs.io/en/stable/contract_types/layers/ (layers, containers, exhaustive)
+- https://import-linter.readthedocs.io/en/stable/contract_types/forbidden/ (forbidden, as_packages, include_external_packages)
+- https://kokonatt.com/blog/modular-boundaries-import-linter/ (hexagonal contracts, independence/protected/acyclic_siblings)
+- https://pytest-cov.readthedocs.io/en/latest/config.html (`--cov-fail-under`, `--cov-branch`)
+- https://qaskills.sh/blog/pytest-coverage-pytest-cov-guide-2026 (branch coverage, fail_under, combine)
+- https://github.com/pytest-dev/pytest-randomly (seed, `--randomly-seed=last`, `-p no:randomly`)
+- https://github.com/aristanetworks/j2lint (S0 jinja-syntax-error, CI)
+- https://pypi.org/project/jinja-multilint/ (--mode strict, unknown filter/test = error)
+- https://jinja.palletsprojects.com/en/stable/api/ (`compile_templates(..., ignore_errors=False)`)
+- https://flask.palletsprojects.com/en/stable/cli/ (`flask --app ... routes` factory discovery)
+- https://flask.palletsprojects.com/en/stable/testing/ (app factory fixtures, test_client)
+- https://flask.palletsprojects.com/en/stable/blueprints/ (blueprint boundaries)
+- https://alembic.sqlalchemy.org/en/latest/autogenerate.html (`alembic check` CI drift gate)
+- https://docs.docker.com/guides/testcontainers-python-getting-started/ (testcontainers + pytest)
+- https://qaskills.sh/blog/testcontainers-python-pytest-integration-guide (Postgres + Alembic + SQLAlchemy fixtures)
+- https://docs.astral.sh/uv/concepts/projects/sync/ (`--locked` vs `--frozen`, `uv lock --check`)
+- https://pydevtools.com/handbook/how-to/how-to-use-a-uv-lockfile-for-reproducible-python-environments/
+
 ## Currency Baseline
 
 - **Flask 3.x baseline:** Target Flask 3.x with Flask-SQLAlchemy 3 and SQLAlchemy 2.0-style typed models.
diff --git a/skill-templates/go-gin/SKILL.md b/skill-templates/go-gin/SKILL.md
index a5388e5..758727a 100644
--- a/skill-templates/go-gin/SKILL.md
+++ b/skill-templates/go-gin/SKILL.md
@@ -56,6 +56,407 @@ project/
 - **Mocking**: Generate mocks from interfaces using `mockery` or `go.uber.org/mock` for the Repository and Service layers (`github.com/golang/mock` is archived).
 - **Table-Driven Tests**: Use slice-of-structs to test multiple inputs/outputs in a single test function.
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+### Strict Baseline
+
+> **Substitute `<MODULE_PATH>`** — replace every `<MODULE_PATH>` in this file with your module path.
+> Example: `example.com/app` → run `sed -i 's|<MODULE_PATH>|example.com/app|g'` after copying.
+> Keep the placeholder in the shared skill; never commit a concrete module path.
+
+Static targets for Go 1.27 + Gin (Clean Architecture, REST). Versions verified against live
+releases on 2026-09-21. `golines` is **discarded**: `segmentio/golines` is a public archive
+(last release v0.13.0, 2025-08-21). Use `gofumpt` + `gci` + the `lll` linter instead of a
+line-wrapping formatter. `swaggo/swag` v2 is still `v2.0.0-rc6` (pre-release) — pin stable
+`v1.16.6`, or prefer `oapi-codegen` (contract-first) over annotation-first `swag`.
+
+### Required Toolchain
+
+| Tool | Purpose | Minimum version | Activate |
+| --- | --- | --- | --- |
+| Go toolchain | Compiler, `go vet`, `go test`, `go mod` | 1.27.0 (pin 1.27.1) | `go.mod`: `go 1.27.0` + `toolchain go1.27.1` |
+| gofumpt | Strictest superset of gofmt | v0.12.0 | `go install mvdan.cc/gofumpt@v0.12.0` |
+| gci | Deterministic import grouping/order | v0.14.0 | `go install github.com/daixiang0/gci@v0.14.0` |
+| golangci-lint | Linter runner, v2 schema | v2.13.2 | `go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.13.2` |
+| staticcheck | Advanced static analysis (standalone) | 2026.2.1 (module v0.8.1) | `go install honnef.co/go/tools/cmd/staticcheck@v0.8.1` |
+| govulncheck | Known-CVE reachability scan | v1.8.0 | `go install golang.org/x/vuln/cmd/govulncheck@v1.8.0` |
+| nilaway | Inter-procedural nil-safety | commit acb8859b (2026-09-18) | `go install go.uber.org/nilaway/cmd/nilaway@acb8859b` |
+| deadcode | Unreachable-function detection (RTA) | x/tools v0.50.0 | `go install golang.org/x/tools/cmd/deadcode@v0.50.0` |
+| go-arch-lint | Layer/dependency-direction enforcement | v1.19.0 | `go install github.com/fe3dback/go-arch-lint@v1.19.0` |
+| gotestsum | Machine-readable test gate output | v1.13.0 | `go install gotest.tools/gotestsum@v1.13.0` |
+| go-test-coverage | Coverage-threshold gate | v2.19.0 | `go install github.com/vladopajic/go-test-coverage/v2@v2.19.0` |
+| goleak | Goroutine-leak gate in tests | v1.3.0 | `go get go.uber.org/goleak@v1.3.0` |
+| testify | Assertions / suites | v1.12.1 | `go get github.com/stretchr/testify@v1.12.1` |
+| testifylint | testify misuse linter (via golangci-lint) | v1.6.4 | bundled by golangci-lint |
+| validator | Gin request validation engine | v10.30.5 | `go get github.com/go-playground/validator/v10@v10.30.5` |
+| gin | HTTP router/framework | v1.12.0 | `go get github.com/gin-gonic/gin@v1.12.0` |
+| oapi-codegen | Contract-first OpenAPI → Go (Gin + strict) | v2.8.0 | `go install github.com/oapi-codegen/oapi-codegen/v2/cmd/oapi-codegen@v2.8.0` |
+| oasdiff | Breaking-change gate between OpenAPI revisions | v1.32.1 | `go install github.com/oasdiff/oasdiff@v1.32.1` |
+
+### Strict Baseline Config
+
+Files: `.golangci.yml`, `.go-arch-lint.yml`, `.testcoverage.yml`, `oapi-codegen.yaml`, `go.mod` policy.
+
+`.golangci.yml` (v2 schema — note the required `version: "2"` and the separate `formatters` block):
+
+```yaml
+version: "2"
+
+run:
+  timeout: 5m
+  go: "1.27"
+  modules-download-mode: readonly
+  tests: true
+  issues-exit-code: 2
+
+linters:
+  default: none
+  enable:
+    - govet
+    - staticcheck
+    - errcheck
+    - gosec
+    - revive
+    - gocritic
+    - exhaustive
+    - bodyclose
+    - noctx
+    - sqlclosecheck
+    - rowserrcheck
+    - wrapcheck
+    - errorlint
+    - nilerr
+    - nilnesserr
+    - ineffassign
+    - unused
+    - misspell
+    - prealloc
+    - nestif
+    - cyclop
+    - dupl
+    - goconst
+    - godot
+    - depguard
+    - forbidigo
+    - testifylint
+    - nilnil
+    - contextcheck
+    - durationcheck
+    - errname
+    - thelper
+    - tparallel
+    - nolintlint
+    - containedctx
+    - unparam
+    - unconvert
+    - wastedassign
+    - whitespace
+    - copyloopvar
+    - makezero
+    - lll
+    - paralleltest
+    - usetesting
+    - perfsprint
+    - mirror
+    - gochecknoinits
+    - err113
+  settings:
+    govet:
+      enable:
+        - nilness
+        - shadow
+    cyclop:
+      max-complexity: 10
+    dupl:
+      threshold: 100
+    nestif:
+      min-complexity: 4
+    goconst:
+      min-len: 2
+      min-occurrences: 3
+    gocritic:
+      enabled-tags:
+        - diagnostic
+        - experimental
+        - opinionated
+        - performance
+        - style
+      disabled-checks:
+        - dupImport
+        - whyNoLint
+    godot:
+      scope: declarations
+      period: true
+    exhaustive:
+      check:
+        - switch
+        - map
+      default-signifies-exhaustive: false
+    errorlint:
+      errorf: true
+      asserts: true
+      comparison: true
+    nilnil:
+      detect-opposite: true
+    testifylint:
+      enable-all: true
+    nolintlint:
+      allow-unused: false
+      require-explanation: true
+      require-specific: true
+    forbidigo:
+      forbid:
+        - pattern: ^print(ln)?$
+        - pattern: ^fmt\.Print.*$
+          msg: Do not commit print statements; use structured logging.
+        - pattern: ^log\.(Fatal|Panic).*$
+          msg: Do not terminate inside library layers; return an error.
+        - pattern: ^panic$
+          msg: Return an error instead of panicking.
+    depguard:
+      rules:
+        domain-purity:
+          files:
+            - "**/internal/domain/**"
+          list-mode: strict
+          allow:
+            - $gostd
+            - <MODULE_PATH>/internal/domain
+          deny:
+            - pkg: github.com/gin-gonic/gin
+              desc: domain must not depend on the HTTP delivery layer
+            - pkg: net/http
+              desc: domain must not depend on net/http
+            - pkg: gorm.io/
+              desc: domain must not depend on the ORM
+            - pkg: database/sql
+              desc: domain must not depend on database/sql
+            - pkg: <MODULE_PATH>/internal/infrastructure
+              desc: domain must not depend on infrastructure
+            - pkg: <MODULE_PATH>/internal/delivery
+              desc: domain must not depend on delivery
+        usecase-purity:
+          files:
+            - "**/internal/usecase/**"
+          list-mode: strict
+          allow:
+            - $gostd
+            - <MODULE_PATH>/internal/domain
+            - <MODULE_PATH>/internal/usecase
+            - <MODULE_PATH>/pkg
+          deny:
+            - pkg: github.com/gin-gonic/gin
+              desc: use cases must not depend on the delivery layer
+            - pkg: net/http
+              desc: use cases must not depend on net/http
+            - pkg: gorm.io/
+              desc: use cases must depend on repository interfaces, not the ORM
+            - pkg: <MODULE_PATH>/internal/delivery
+              desc: use cases must not depend on delivery
+  exclusions:
+    generated: strict
+    warn-unused: true
+    rules:
+      - path: _test\.go
+        linters:
+          - err113
+          - dupl
+          - gosec
+          - wrapcheck
+
+formatters:
+  enable:
+    - gofumpt
+    - gci
+  settings:
+    gofumpt:
+      module-path: <MODULE_PATH>
+      extra:
+        group-params: true
+        clothe-returns: true
+        balance-calls: true
+    gci:
+      sections:
+        - standard
+        - default
+        - prefix(<MODULE_PATH>)
+      custom-order: true
+
+issues:
+  max-issues-per-linter: 0
+  max-same-issues: 0
+
+severity:
+  default: error
+```
+
+`.go-arch-lint.yml` (executable layer direction, independent of depguard):
+
+```yaml
+version: 3
+workdir: internal
+allow:
+  depOnAnyVendor: false
+components:
+  delivery:    { in: delivery/** }
+  usecase:     { in: usecase/** }
+  repository:  { in: infrastructure/persistence/** }
+  domain:      { in: domain/** }
+commonComponents:
+  - domain
+deps:
+  delivery:
+    mayDependOn:
+      - usecase
+  usecase:
+    mayDependOn:
+      - repository
+  repository:
+    mayDependOn:
+      - domain
+```
+
+`go.mod` toolchain policy + reproducibility:
+
+```go
+module <MODULE_PATH>
+
+go 1.27.0
+
+toolchain go1.27.1
+```
+
+`.testcoverage.yml`:
+
+```yaml
+profile: coverage.out
+threshold:
+  total: 80
+  package: 75
+  file: 70
+```
+
+`oapi-codegen.yaml` (Gin + strict server, contract-first):
+
+```yaml
+package: api
+generate:
+  gin-server: true
+  strict-server: true
+  models: true
+  embedded-spec: true
+output: internal/delivery/http/api/generated.gen.go
+```
+
+Strict Gin bootstrap (validator opt-in to v11 behaviour + reject unknown JSON fields):
+
+```go
+import (
+	"reflect"
+
+	"github.com/gin-gonic/gin/binding"
+	"github.com/go-playground/validator/v10"
+)
+
+func installStrictValidator() error {
+	v, ok := binding.Validator.Engine().(*validator.Validate)
+	if !ok {
+		return errors.New("gin binding validator engine is not *validator.Validate")
+	}
+	v.Validate = validator.New(validator.WithRequiredStructEnabled())
+	v.Validate.RegisterTagNameFunc(func(fld reflect.StructField) string {
+		return fld.Tag.Get("json")
+	})
+	return nil
+}
+
+// Request DTOs use strict binding tags:
+//   type CreateUserRequest struct {
+//       Name  string `json:"name"  binding:"required,min=1,max=64"`
+//       Email string `json:"email" binding:"required,email"`
+//   }
+```
+
+### Mandatory Gate Order
+
+0. `! grep -r "<MODULE_PATH>" --include="*.yml" --include="*.yaml" --include="*.go" --include="go.mod" .` — placeholder guard: fail if any `<MODULE_PATH>` remains unsubstituted (substitute first via `sed -i 's|<MODULE_PATH>|example.com/app|g'`).
+1. `gofumpt -l .` (must print nothing)
+2. `golangci-lint fmt --diff` (gofumpt + gci; must print nothing)
+3. `go vet ./...`
+4. `golangci-lint run --timeout=5m ./...`
+5. `staticcheck ./...`
+6. `nilaway ./...`
+7. `govulncheck ./...`
+8. `go-arch-lint check --project-path . --arch-file .go-arch-lint.yml`
+9. `go build ./...`
+10. `go mod verify`
+11. `go mod tidy -diff` (exits non-zero if go.mod/go.sum would change)
+12. `gotestsum --format=testname -- -race -shuffle=on -count=1 -covermode=atomic -coverprofile=coverage.out -coverpkg=./... ./...`
+13. `go-test-coverage --config .testcoverage.yml`
+14. `deadcode -test ./...`
+15. `if test -f api/openapi.yaml; then oapi-codegen -config oapi-codegen.yaml api/openapi.yaml && git diff --exit-code -- internal/delivery/http/api/generated.gen.go; else echo "SKIP oapi-codegen | no api/openapi.yaml present | contract-first gates not applicable | exit 0 for this step only"; fi`
+16. `if test -f api/openapi.yaml && test -f api/openapi.base.yaml; then oasdiff breaking --fail-on WARN api/openapi.base.yaml api/openapi.yaml; else echo "SKIP oasdiff | no api/openapi.yaml or api/openapi.base.yaml present | breaking-change gate not applicable | exit 0 for this step only"; fi`
+
+> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI.
+> Steps 1–2 are check-only (`gofumpt -l`, `fmt --diff`) — CI never rewrites source. Regeneration
+> (step 15) is the only write, and its staleness is proven by `git diff --exit-code`.
+
+### Hallucination Traps to Block
+
+- Unclosed HTTP response bodies from `gin`/`http.Get` -> `bodyclose`.
+- Dropped errors, unwrapped cross-package errors, `%v` instead of `%w` -> `errcheck`, `errorlint`, `wrapcheck`.
+- Context never propagated / stored on a struct / wrong parent context -> `noctx`, `contextcheck`, `containedctx`.
+- `switch` over a domain enum silently missing a new variant -> `exhaustive` (with `default-signifies-exhaustive: false`).
+- `sql.Rows`/`Stmt` leaks and unchecked `Rows.Err()` -> `sqlclosecheck`, `rowserrcheck`.
+- Architectural decay: domain/usecase importing Gin, GORM, or `net/http` -> `depguard` rules + `go-arch-lint`.
+- `return nil, nil`, swallowed errors, nil-map/nil-pointer derefs -> `nilnil`, `nilerr`, `nilnesserr`, `nilaway`.
+- Stale generated API code or a silent breaking API change -> regenerate + `git diff --exit-code`, `oasdiff breaking --fail-on WARN`.
+- Vulnerable transitive dependency introduced by an AI-suggested import -> `govulncheck` (reachability-based).
+- Goroutine leaks or wrong testify assertions in generated tests -> `goleak`, `testifylint`.
+
+### Evidence to Record
+
+Paste the exact commands and observed pass criteria into Verification Evidence:
+
+1. `gofumpt -l .` and `golangci-lint fmt --diff` -> **empty output**, exit 0.
+2. `golangci-lint run --timeout=5m ./...` -> exit 0, `0 issues` (severity default = error, exit code 2 on any issue).
+3. `staticcheck ./...` and `nilaway ./...` -> exit 0, no diagnostics.
+4. `govulncheck ./...` -> `No vulnerabilities found`, exit 0.
+5. `go-arch-lint check --project-path . --arch-file .go-arch-lint.yml` -> exit 0 (no layer violations).
+6. `go build ./... && go mod verify && go mod tidy -diff` -> all exit 0, no diff.
+7. `gotestsum ... -- -race -shuffle=on -count=1 -coverprofile=coverage.out ...` -> `-race` clean, all tests pass; then `go-test-coverage --config .testcoverage.yml` -> exit 0 (total ≥ 80%).
+8. `deadcode -test ./...` -> empty report (or documented allowlist).
+9. `oapi-codegen ... && git diff --exit-code` -> no diff; `oasdiff breaking --fail-on WARN` -> exit 0.
+10. Capture the toolchain prove-out: `go version` = `go1.27.1`, `GOTOOLCHAIN=local` set in CI (fail rather than silently download a different toolchain).
+
+<!-- sources -->
+- https://golangci-lint.run/docs/configuration/file/
+- https://golangci-lint.run/docs/linters/
+- https://golangci-lint.run/docs/configuration/cli/
+- https://github.com/golangci/golangci-lint/releases/tag/v2.13.2
+- https://github.com/golangci/golangci-lint/blob/main/.golangci.yml
+- https://github.com/golangci/golangci-lint/blob/main/.golangci.reference.yml
+- https://github.com/mvdan/gofumpt
+- https://github.com/daixiang0/gci
+- https://github.com/segmentio/golines
+- https://github.com/dominikh/go-tools
+- https://github.com/golang/vuln
+- https://github.com/uber-go/nilaway
+- https://pkg.go.dev/golang.org/x/tools/cmd/deadcode
+- https://github.com/fe3dback/go-arch-lint
+- https://github.com/gotestyourself/gotestsum
+- https://github.com/vladopajic/go-test-coverage
+- https://github.com/uber-go/goleak
+- https://github.com/Antonboom/testifylint
+- https://go.dev/doc/toolchain
+- https://github.com/oapi-codegen/oapi-codegen
+- https://github.com/oasdiff/oasdiff
+- https://github.com/go-playground/validator
+- https://github.com/gin-gonic/gin
+
 ## Currency Baseline
 
 - **Standard observability:** Prefer stdlib `log/slog` for structured logging; pin a recent Go toolchain in `go.mod`.
diff --git a/skill-templates/go-hexagonal-grpc/SKILL.md b/skill-templates/go-hexagonal-grpc/SKILL.md
index 35c35e9..79e4cee 100644
--- a/skill-templates/go-hexagonal-grpc/SKILL.md
+++ b/skill-templates/go-hexagonal-grpc/SKILL.md
@@ -94,6 +94,427 @@ Never panic. Return errors explicitly. Wrap errors with context using `%w` so th
 - Generate mocks for all interfaces in `internal/core/ports` using `mockery`.
 - AI must write table-driven tests (`[]struct`) for all core business logic.
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+### Strict Baseline
+
+> **Substitute `<MODULE_PATH>`** — replace every `<MODULE_PATH>` in this file with your module path.
+> Example: `github.com/acme/svc` → run `sed -i 's|<MODULE_PATH>|github.com/acme/svc|g'` after copying.
+> Keep the placeholder in the shared skill; never commit a concrete module path.
+
+Stack: Go + Hexagonal (Ports & Adapters) + gRPC/Protobuf + Uber Fx + Redis.
+Verified maintained as of **2026-09-21** (live web research; abandoned tools flagged inline).
+
+### Required Toolchain
+
+| Tool | Purpose | Minimum version | Activate |
+| --- | --- | --- | --- |
+| Go toolchain | language + `-race`, `go mod tidy -diff`, `toolchain` pinning | `go1.26.5` (must be ≥ 1.26.3 / 1.25.10 to fix CVE-2026-42501) | `go get go@1.26.5 toolchain@go1.26.5` |
+| buf | proto build/lint/breaking/format/codegen | `v1.72.0` (2026-07-17) | `go install github.com/bufbuild/buf/cmd/buf@v1.72.0` |
+| protoc-gen-go (remote) | Go message generation | `v1.36.11` | pin `remote: buf.build/protocolbuffers/go:v1.36.11` |
+| protoc-gen-go-grpc (remote) | gRPC stubs | `v1.5.1` | pin `remote: buf.build/grpc/go:v1.5.1` |
+| protovalidate-go | schema-native message validation | `v1.2.0` (module moved to `buf.build/go/protovalidate`) | `go get buf.build/go/protovalidate@v1.2.0` |
+| go-grpc-middleware protovalidate interceptor | server-side validation gate | `v2.3.2` | `go get github.com/grpc-ecosystem/go-grpc-middleware/v2@v2.3.2` |
+| golangci-lint | aggregated Go lint gate | `v2.13.2` (2026-08-27) | `go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.13.2` (upstream recommends binary install) |
+| gofumpt | stricter `gofmt` | `v0.11.0` (2026-07-27, Go 1.26 based) | `go install mvdan.cc/gofumpt@v0.11.0` |
+| gci | deterministic import grouping | `v0.14.0` (2026-02-28) | `go install github.com/daixiang0/gci@v0.14.0` |
+| NilAway | nil-panic static analysis (module plugin; not bundled) | `v0.0.0-20260728022246-eeeb1603aad0` | `.custom-gcl.yml` + `golangci-lint custom` |
+| go-arch-lint | architecture boundary enforcement | `v1.15.0` (2026-05-04) — or fork `vsfedorenko/go-arch-lint/v2 v2.6.0` (2026-08-22) | `go install github.com/fe3dback/go-arch-lint@v1.15.0` |
+| goleak | goroutine-leak gate | `v1.3.0` | `go get go.uber.org/goleak@v1.3.0` |
+| testcontainers-go | real Redis/DB in tests | `v0.44.0` | `go get github.com/testcontainers/testcontainers-go/modules/redis@v0.44.0` |
+| govulncheck | reachable-vulnerability gate | `v1.7.0` (`golang.org/x/vuln`) | `go install golang.org/x/vuln/cmd/govulncheck@v1.7.0` |
+| go-redis | Redis client | `v9.7.3` | `go get github.com/redis/go-redis/v9@v9.7.3` |
+
+**Discarded / not strict enough:** `protoc-gen-validate` (PGV) — superseded by Protovalidate; keep only if migrating. `gomodguard` (v1) — deprecated since v2.12.0, use `gomodguard_v2`. Standalone `nilaway` analyzer works but is best gated through the `custom-gcl` plugin so it shares the run.
+
+### Strict Baseline Config
+
+File names: `buf.yaml`, `buf.gen.yaml`, `.golangci.yml`, `.custom-gcl.yml`, `.go-arch-lint.yml`, plus `internal/platform/redis.go` and test files below.
+
+`buf.yaml` — STANDARD + both extra strict categories, and inline comment-ignores **banned**:
+```yaml
+version: v2
+modules:
+  - path: proto
+lint:
+  use:
+    - STANDARD
+    - COMMENTS        # leading comments required on every schema element
+    - UNARY_RPC        # forbidden client/server streaming (delete if you need streams)
+  disallow_comment_ignores: true   # no // buf:lint:ignore escape hatch in CI
+  enum_zero_value_suffix: _UNSPECIFIED
+  service_suffix: Service
+  rpc_allow_same_request_response: false
+  rpc_allow_google_protobuf_empty_requests: false
+  rpc_allow_google_protobuf_empty_responses: false
+breaking:
+  use:
+    - FILE             # strictest: source + JSON + wire compatibility
+  ignore_unstable_packages: false
+```
+> Note: there is **no `buf format --check`**. The strict CI check is `buf format --exit-code` (add `-d` to print the diff). `--exit-code` is what turns it into a gate.
+
+`buf.gen.yaml` — remote plugins pinned, reproducible, managed Go package:
+```yaml
+version: v2
+clean: true
+managed:
+  enabled: true
+  override:
+    - file_option: go_package_prefix
+      value: <MODULE_PATH>/gen/go
+plugins:
+  - remote: buf.build/protocolbuffers/go:v1.36.11
+    out: gen/go
+    opt: [paths=source_relative]
+  - remote: buf.build/grpc/go:v1.5.1
+    out: gen/go
+    opt: [paths=source_relative]
+inputs:
+  - directory: proto
+```
+
+`.custom-gcl.yml` — build the NilAway-enabled binary (cache it by file hash):
+```yaml
+version: v2.13.2
+plugins:
+  - module: go.uber.org/nilaway
+    import: go.uber.org/nilaway/cmd/gclplugin
+    version: v0.0.0-20260728022246-eeeb1603aad0
+```
+
+`.golangci.yml` — strict aggregator, hexagonal `depguard`, gRPC/Redis-context rules:
+```yaml
+version: "2"
+run:
+  timeout: 5m
+  tests: true
+linters:
+  default: none
+  enable:
+    - asasalint
+    - bodyclose
+    - containedctx
+    - contextcheck
+    - copyloopvar
+    - depguard
+    - durationcheck
+    - err113
+    - errcheck
+    - errchkjson
+    - errorlint
+    - exhaustive
+    - fatcontext
+    - forbidigo
+    - forcetypeassert
+    - funlen
+    - gocognit
+    - goconst
+    - gocritic
+    - gosec
+    - govet
+    - importas
+    - ineffassign
+    - makezero
+    - mirror
+    - musttag
+    - nilerr
+    - nilnesserr
+    - noctx
+    - nolintlint
+    - nonamedreturns
+    - paralleltest
+    - prealloc
+    - predeclared
+    - protogetter
+    - revive
+    - rowserrcheck
+    - spancheck
+    - sqlclosecheck
+    - staticcheck
+    - testifylint
+    - thelper
+    - tparallel
+    - unconvert
+    - unparam
+    - unused
+    - usestdlibvars
+    - usetesting
+    - wastedassign
+    - wrapcheck
+  settings:
+    govet:
+      enable-all: true
+      disable: [fieldalignment]   # alignment is an optimization, not a correctness gate
+    errcheck:
+      check-type-assertions: true
+      check-blank: true
+    gosec:
+      excludes: [G104]            # errcheck already covers unchecked errors
+    gocognit:
+      min-complexity: 20
+    funlen:
+      lines: 60
+      statements: 40
+    nolintlint:
+      require-explanation: true
+      require-specific: true
+      allow-unused: false
+    protogetter:
+      skip-generated-by: true
+    wrapcheck:
+      ignore-sigs:
+        - "errors.New("
+        - "fmt.Errorf("
+    depguard:
+      rules:
+        domain-purity:
+          files: ["**/internal/domain/**"]
+          list-mode: strict
+          allow:
+            - $gostd
+            - <MODULE_PATH>/internal/ports
+            - <MODULE_PATH>/internal/domain
+          deny:
+            - { pkg: google.golang.org/grpc,         desc: "domain must define a port, never import transport" }
+            - { pkg: google.golang.org/protobuf,     desc: "domain must not depend on generated protobuf types" }
+            - { pkg: github.com/redis/go-redis/v9,   desc: "domain must define a cache port" }
+            - { pkg: go.uber.org/fx,                 desc: "domain must not import the DI framework" }
+            - { pkg: <MODULE_PATH>/internal/adapters, desc: "domain must not import adapters" }
+        ports-purity:
+          files: ["**/internal/ports/**"]
+          list-mode: strict
+          allow:
+            - $gostd
+            - <MODULE_PATH>/internal/domain
+        app-no-transport:
+          files: ["**/internal/app/**"]
+          list-mode: strict
+          allow:
+            - $gostd
+            - <MODULE_PATH>/internal/domain
+            - <MODULE_PATH>/internal/ports
+          deny:
+            - { pkg: google.golang.org/grpc,       desc: "application layer is transport-agnostic" }
+            - { pkg: github.com/redis/go-redis/v9, desc: "application talks to the port, not the client" }
+        adapters-depend-on-ports:
+          files: ["**/internal/adapters/**"]
+          list-mode: strict
+          allow:
+            - $gostd
+            - <MODULE_PATH>/internal/domain
+            - <MODULE_PATH>/internal/ports
+            - <MODULE_PATH>/internal/app
+            - <MODULE_PATH>/internal/adapters
+            - google.golang.org/grpc
+            - google.golang.org/protobuf
+            - github.com/redis/go-redis/v9
+            - <MODULE_PATH>/gen/go
+  exclusions:
+    generated: strict
+    warn-unused: true
+    rules:
+      - path: _test\.go
+        linters: [funlen, gocognit, goconst, errcheck, dupl]
+formatters:
+  enable:
+    - gofumpt
+    - gci
+  settings:
+    gofumpt:
+      extra-rules: true          # all extra rules (group-params, clothe-returns, ...)
+    gci:
+      sections:
+        - standard
+        - default
+        - prefix(<MODULE_PATH>)
+```
+
+`.go-arch-lint.yml` — component graph; ports own the interfaces, adapters point inward:
+```yaml
+version: 3
+workdir: internal
+allow:
+  depOnAnyVendor: false    # every third-party import must be explicitly allow-listed
+  deepScan: true
+excludeFiles:
+  - "^.*_test\\.go$"
+components:
+  domain:        { in: domain/** }
+  ports:         { in: ports/** }
+  app:           { in: app/** }
+  adapter-grpc:  { in: adapters/grpc/** }
+  adapter-redis: { in: adapters/redis/** }
+  platform:      { in: platform/** }
+commonComponents:
+  - platform
+vendors:
+  grpc:     { in: google.golang.org/grpc }
+  protobuf: { in: google.golang.org/protobuf }
+  redis:    { in: github.com/redis/go-redis/v9 }
+  fx:       { in: go.uber.org/fx }
+deps:
+  domain:
+    mayDependOn: [ports]
+    mayNotDependOn: [app, adapter-grpc, adapter-redis, platform]
+  ports:
+    mayDependOn: [domain]
+  app:
+    mayDependOn: [domain, ports]
+    canUse: [fx]
+  adapter-grpc:
+    mayDependOn: [domain, ports, app]
+    canUse: [grpc, protobuf]
+  adapter-redis:
+    mayDependOn: [domain, ports]
+    canUse: [redis]
+```
+> Stricter fork option (`github.com/vsfedorenko/go-arch-lint/v2`, Go DSL in `.go-arch-lint/arch.go`): `Interfaces(func(){ MustLiveWithConsumer() })` fails any port interface declared next to its implementation instead of its consumer. *(The v3 line of that fork dropped the `Interfaces` rule — pin v2.6.0 if you use it.)*
+
+**Uber Fx gate** — `fx.ValidateApp` is the current recommended graph gate (no constructors or Invokes run, no side effects), and it detects cycles (`"cycle detected in dependency graph"`):
+```go
+func TestAppGraph(t *testing.T) {
+	t.Parallel()
+	require.NoError(t, fx.ValidateApp(
+		module.Domain, module.Ports, module.App,
+		module.AdapterGRPC, module.AdapterRedis, module.Platform,
+	), "fx graph must build with no missing deps and no cycles")
+}
+```
+Use `fxtest.New(t, ...)` + `app.RequireStart().RequireStop()` for lifecycle hooks, `fx.Annotate(..., fx.As(new(Port)))` so adapters bind to interfaces, and inside each `fx.Module` keep provide/annotate declarations together. `fx.ValidateApp` at app-assembly test time is the gate; startup smoke tests are not a substitute.
+
+**Redis strictness** — explicit timeouts, bounded pool, and context-enabled deadlines:
+```go
+rdb := redis.NewClient(&redis.Options{
+	Addr:                  cfg.Addr,
+	DialTimeout:           2 * time.Second,
+	ReadTimeout:           1 * time.Second,
+	WriteTimeout:          1 * time.Second,
+	PoolTimeout:           2 * time.Second,
+	PoolSize:              50,  // max total connections in pool (strict cap — blocks hallucinated pool-field spellings)
+	MinIdleConns:          10,
+	ConnMaxIdleTime:       5 * time.Minute,
+	ConnMaxLifetime:       30 * time.Minute,
+	ContextTimeoutEnabled: true,   // honor ctx deadlines/deadlines
+	MaxRetries:            2,
+})
+```
+Do **not** rely on `ContextTimeoutEnabled` alone for blocking commands (`BLPOP`, `PubSub`) — go-redis cannot cancel socket reads mid-flight; bound those with the Redis command timeout as well. Every adapter method must take `ctx context.Context`; a custom `cache` port wrapper with mandatory ctx is the enforcement point, while `noctx`, `contextcheck`, `containedctx`, `fatcontext`, `spancheck` and `gosec` G118 catch regressions.
+
+**Test gates:**
+```go
+func TestMain(m *testing.M) { goleak.VerifyTestMain(m) }
+
+func TestGRPCService(t *testing.T) { // in-process full transport via bufconn
+	t.Parallel()
+	lis := bufconn.Listen(1 << 20)
+	t.Cleanup(func() { lis.Close() })
+	srv := grpc.NewServer(
+		grpc.ChainUnaryInterceptor(
+			protovalidate_middleware.UnaryServerInterceptor(mustValidator(t)),
+			recoveryInterceptor,
+		),
+	)
+	reflection.Register(srv) // asserted by a reflection test
+	pb.RegisterSvcServer(srv, testServer(t))
+	go func() { _ = srv.Serve(lis) }()
+	t.Cleanup(srv.GracefulStop)
+
+	conn, err := grpc.NewClient("passthrough:///bufconn",
+		grpc.WithContextDialer(func(ctx context.Context, _ string) (net.Conn, error) { return lis.DialContext(ctx) }),
+		grpc.WithTransportCredentials(insecure.NewCredentials()),
+	)
+	require.NoError(t, err)
+	t.Cleanup(func() { _ = conn.Close() })
+	// ... assert InvalidArgument carries *errdetails.BadRequest for a malformed request
+}
+
+// Redis adapter test with a real server:
+func newRedis(t *testing.T) *redis.Client {
+	t.Helper()
+	c, err := tcredis.Run(t.Context(), "redis:7")
+	require.NoError(t, err)
+	url, err := c.ConnectionString(t.Context())
+	require.NoError(t, err)
+	opt, err := redis.ParseURL(url)
+	require.NoError(t, err)
+	return redis.NewClient(opt)
+}
+```
+
+### Mandatory Gate Order
+
+0. `! grep -r "<MODULE_PATH>" --include="*.yml" --include="*.yaml" --include="*.go" --include="go.mod" --include="buf.gen.yaml" .` — placeholder guard: fail if any `<MODULE_PATH>` remains unsubstituted (substitute first via `sed -i 's|<MODULE_PATH>|github.com/acme/svc|g'`).
+1. `go mod verify`
+2. `go mod tidy -diff`            # fails if go.mod/go.sum are not tidy; never mutate in CI
+3. `test -z "$(gofumpt -l .)"`    # unformatted files -> non-empty -> fail
+4. `test -z "$(gci diff --section standard --section default --section 'Prefix(<MODULE_PATH>)' ./...)"`
+5. `buf format --exit-code`
+6. `buf lint`
+7. `git fetch --unshallow origin main 2>/dev/null || git fetch --depth 0 origin main 2>/dev/null || true; buf breaking --against '.git#branch=main'`  # requires full history; CI must clone with --fetch-depth 0 or full history — the .git#branch shorthand fails on shallow clones without this fetch
+8. `buf generate --clean && git --no-pager diff --exit-code -- gen/`   # generated-code drift gate
+9. `test -x ./custom-gcl && [ \"$(sha256sum .custom-gcl.yml | cut -d' ' -f1)\" = \"$(cat .custom-gcl.sha 2>/dev/null || echo)\" ] || (golangci-lint custom && sha256sum .custom-gcl.yml | cut -d' ' -f1 > .custom-gcl.sha)`  # bootstrap: build NilAway binary per .custom-gcl.yml (expected ./custom-gcl), cache by file hash before lint
+   `./custom-gcl run ./...`       # golangci-lint + NilAway, warnings are errors
+10. `go-arch-lint check --project-path . --arch-file .go-arch-lint.yml`
+11. `go build ./...`
+12. `go vet ./...`
+13. `go test -race -shuffle=on -count=1 ./...`
+14. `go test -race -shuffle=on -count=1 -tags=integration -covermode=atomic -coverpkg=./... -coverprofile=cover.out ./...`
+15. `test "$(go tool cover -func=cover.out | tail -1 | awk '{gsub("%","",$NF); print int($NF)}')" -ge 90`
+16. `govulncheck ./...`
+
+> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI. (Step 15 is a portable 90% gate; `github.com/vladopajic/go-test-coverage` is an optional richer alternative.)
+
+### Hallucination Traps to Block
+
+- **Invented/renamed proto fields or changed field types** → `buf breaking --against '.git#branch=main'` with `breaking.use: [FILE]`.
+- **Domain/application importing a framework (gRPC, Redis, Fx, protobuf)** → `depguard` `domain-purity` / `app-no-transport` (strict list-mode) + `go-arch-lint deps` + `mayNotDependOn`.
+- **Context dropped from Redis/gRPC/DB calls** → `noctx`, `contextcheck`, `containedctx`, `gosec` G118 (`fatcontext`/`spancheck` as backup).
+- **Swallowed or unwrapped errors across boundaries** → `errcheck` (`check-blank`), `errorlint`, `wrapcheck`, `err113`.
+- **Fx graph with missing provides or dependency cycles** → `fx.ValidateApp(...)` test asserts `"cycle detected in dependency graph"` / missing-type errors before `fxtest` lifecycle.
+- **Hand-edited stubs or stale generated code** → step 8 `buf generate --clean && git diff --exit-code -- gen/`; `protogetter` forbids direct proto field access.
+- **Nil-pointer regressions in adapters/handlers** → NilAway plugin (`./custom-gcl run`).
+- **Leaked goroutines / unclosed Redis or gRPC servers in tests** → `goleak.VerifyTestMain` + `t.Cleanup` on `bufconn` listener, server, container, and client.
+- **Unpinned toolchain/plugins or vulnerable deps** → `go.mod toolchain` pin + pinned remote plugin tags + `govulncheck ./...` (reachable findings fail).
+
+### Evidence to Record
+
+Paste the exact command and the observed result for each gate:
+- `go mod verify` → pass criterion: `all modules verified` (exit 0).
+- `go mod tidy -diff` → pass criterion: empty output (exit 0).
+- `buf lint` / `buf breaking --against '.git#branch=main'` → pass criterion: no violations printed (exit 0); include the `buf.yaml` `lint.use`/`breaking.use` values in the log.
+- `buf generate --clean && git --no-pager diff --exit-code -- gen/` → pass criterion: zero diff.
+- `./custom-gcl run ./...` → pass criterion: `0 issues` and exit 0 (record the custom-gcl hash + NilAway version).
+- `go-arch-lint check --project-path . --arch-file .go-arch-lint.yml` → pass criterion: exit 0; paste the `go-arch-lint mapping` output showing component→package assignment.
+- `go test ... -race -shuffle=on -count=1 ./...` → pass criterion: `ok` for every package and no `DATA RACE`.
+- coverage → pass criterion: `go tool cover -func=cover.out | tail -1` total ≥ 90%.
+- `govulncheck ./...` → pass criterion: `No vulnerabilities found` (or only non-reachable findings explicitly listed as informational).
+- Fx → `fx.ValidateApp` returns `nil`; goleak → no leaked-goroutine failure.
+
+<!-- sources -->
+- https://buf.build/docs/lint/rules/ — STANDARD/BASIC/MINIMAL + COMMENTS + UNARY_RPC categories
+- https://buf.build/docs/lint/usage/ — `buf.yaml` v2 lint keys, `disallow_comment_ignores`
+- https://buf.build/docs/format/usage/ and https://buf.build/docs/reference/cli/buf/format/ — `--exit-code` (no `--check`)
+- https://buf.build/docs/bsr/remote-plugins/ and https://buf.build/docs/bsr/remote-plugins/usage/ — pinned remote plugins, `protocolbuffers/go`, `grpc/go`
+- https://github.com/bufbuild/buf/blob/main/README.md — buf v1.72.0, `breaking` FILE/PACKAGE/WIRE_JSON/WIRE
+- https://protovalidate.com/quickstart/grpc-go/ — Protovalidate gRPC interceptor quickstart
+- https://pkg.go.dev/buf.build/go/protovalidate@v0.14.0 (module history to v1.2.0) and https://pkg.go.dev/github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/protovalidate
+- https://github.com/golangci/golangci-lint/releases/tag/v2.13.2 and https://golangci-lint.run/docs/configuration/file/ — v2 config schema
+- https://golangci-lint.run/docs/linters/configuration/ — depguard `list-mode: strict`, gosec G118/G120 codes
+- https://pkg.go.dev/github.com/daixiang0/gci@v0.14.0 and https://github.com/mvdan/gofumpt/releases/tag/v0.11.0
+- https://github.com/uber-go/nilaway — module plugin into golangci-lint (`.custom-gcl.yml`)
+- https://github.com/fe3dback/go-arch-lint — v1.15.0 (2026-05-04); https://github.com/vsfedorenko/go-arch-lint — Go DSL fork, `MustLiveWithConsumer`, v2.6.0
+- https://github.com/uber-go/fx/blob/master/app_test.go — `ValidateApp` cycle/missing-dep behavior; https://pkg.go.dev/go.uber.org/fx
+- https://github.com/redis/go-redis/blob/v9.7.0/options.go and https://redis.uptrace.dev/guide/go-redis-debugging.html — timeout/pool/context semantics
+- https://pkg.go.dev/github.com/testcontainers/testcontainers-go/modules/redis@v0.43.0 (v0.44.0 release train) and https://golang.testcontainers.org/modules/redis/
+- https://github.com/uber-go/goleak and https://pkg.go.dev/google.golang.org/grpc/test/bufconn
+- https://pkg.go.dev/golang.org/x/vuln@v1.7.0 (govulncheck) and https://tip.golang.org/doc/tutorial/govulncheck
+- https://go.dev/doc/toolchain and https://nvd.nist.gov/vuln/detail/CVE-2026-42501 — toolchain pinning + required patch level
+- https://go.dev/doc/devel/release — Go 1.26.x minor releases
+
 ## Currency Baseline
 
 - **Proto toolchain:** Generate code with `buf` (`buf generate`) and validate contracts with `protovalidate` (`protoc-gen-validate` is archived); keep `.proto` files as the single source of truth.
diff --git a/skill-templates/ios-swiftui/SKILL.md b/skill-templates/ios-swiftui/SKILL.md
index 8632715..013aeeb 100644
--- a/skill-templates/ios-swiftui/SKILL.md
+++ b/skill-templates/ios-swiftui/SKILL.md
@@ -53,6 +53,329 @@ App/
 - **Unit Tests**: Test ViewModels independently of Views. Inject mock network clients via protocols to verify state changes.
 - **UI Tests**: Use Accessibility Identifiers (`.accessibilityIdentifier("login_btn")`) to write stable UI tests.
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+### Strict Baseline
+
+> Target: Swift + SwiftUI (MVVM), Swift Package Manager + Xcode. Verified live 2026-09-21.
+> Rule: every gate below must FAIL (non-zero exit) on a violation. Nothing auto-fixes in CI.
+
+### Required Toolchain
+
+| Tool | Purpose | Minimum version | Activate |
+| --- | --- | --- | --- |
+| Swift / swiftc (toolchain) | Language mode, strict concurrency, upcoming features, warnings-as-errors | Swift 6.2 (Xcode 26+); latest open-source `swift-6.4.0-RELEASE` (Sep 2026) | `xcode-select -p` pin via `.xcode-version`; `SWIFT_VERSION = 6.0` |
+| SwiftLint | Lint rules + type-checked analyzer rules (AST) | 0.65.1 (2026-08-21) | `brew install swiftlint` **or** SPM plugin dep `https://github.com/realm/SwiftLint` (`.exact("0.65.1")`) |
+| swift-format (Apple) | Canonical formatter; bundled in the Swift toolchain, `--strict` fails on lint warnings | 600.0.0 (Swift 6 toolchain); standalone latest 604.0.0 (2026-09-16) | bundled — `xcrun --find swift-format` / `swift format` |
+| SwiftFormat (nicklockwood) | Optional richer formatter, only if swift-format is not used | 0.63.0 (2026-08-30) | `brew install swiftformat` **or** `ghcr.io/nicklockwood/swiftformat:latest` |
+| xcodebuild + clang static analyzer | `analyze` (Clang analyzer) + build gates | Xcode 26+ | built in |
+| `xcrun xccov` | Coverage extraction + threshold gate | Xcode 26+ | built in (`.xcresult`) |
+| OSV-Scanner | Dependency vulnerability + license scanning | v2.6.0 (2026-09-14) | `brew install osv-scanner` / release binary |
+| gitleaks | Secret scanning (git history + working tree) | v8.30.1 (2026-03-21) | `brew install gitleaks` |
+| jq | JSON processor for `xccov` coverage extraction | 1.8.1 (2026) | `brew install jq` |
+| swift-snapshot-testing | Snapshot tests for SwiftUI views/view-models | 1.19.5 (2026-09-15) | SPM `.package(url: "https://github.com/pointfreeco/swift-snapshot-testing", from: "1.19.5")` |
+| Swift Testing | Modern test framework (bundled) | Swift 6.2+ / swift-testing 6.4.0 | bundled with the toolchain |
+| XcodeGen | Deterministic `.xcodeproj` generation from YAML | 2.46.0 (2026-07-16) | `brew install xcodegen` |
+| Tuist | Alternative project generator (Swift manifests, caching) | 4.211.x (2026) | `brew install tuist` / `mise` |
+| `swift-dependency-audit` | Declared-vs-imported SPM dependency audit (unused/missing) | 2.0.8 (2025-12-30) — young, use as advisory | `brew install tonyarnold/tap/swift-dependency-audit` |
+
+> **Advisory only — Periphery:** OSS Periphery 3.8.0 was archived 2026-08-12 (read-only). Do NOT gate on it. Use commercial `periphery.pro` open beta or a source fork as an advisory scan only.
+
+**Discarded / not maintained (do not add):**
+- **Periphery (OSS)** — archived 2026-08-12 by the author; moved to a commercial product (`periphery.pro`). The last OSS tag (3.8.0) still runs, but gets no Swift-version sync.
+- **`swift package diagnose-api-breaking-changes`** — `experimental-api-diff` was promoted but is still marked experimental for production use; keep it as an advisory gate on library targets, not a hard blocker for apps.
+- **xcov / slather** — depend on the legacy `.xcresult` layout; prefer native `xcrun xccov`.
+
+### Strict Baseline Config
+
+**`.xcode-version`** (repo root — pins the toolchain for mise/Tuist/CI):
+```
+26.4
+```
+
+**`Config/Strict.xcconfig`** (imported by all targets; deterministic strict settings):
+```
+SWIFT_VERSION = 6.0
+SWIFT_STRICT_CONCURRENCY = complete
+SWIFT_TREAT_WARNINGS_AS_ERRORS = YES
+GCC_TREAT_WARNINGS_AS_ERRORS = YES
+CLANG_WARN_DOCUMENTATION_COMMENTS = YES
+CLANG_ANALYZER_LOCALIZABILITY_NONLOCALIZED = YES
+ENABLE_USER_SCRIPT_SANDBOXING = YES
+ENABLE_MODULE_VERIFIER = YES
+DEAD_CODE_STRIPPING = YES
+SWIFT_EMIT_LOC_STRINGS = YES
+OTHER_SWIFT_FLAGS = $(inherited) -enable-upcoming-feature ExistentialAny -enable-upcoming-feature InternalImportsByDefault -enable-upcoming-feature MemberImportVisibility -enable-upcoming-feature InferIsolatedConformances -enable-upcoming-feature NonisolatedNonsendingByDefault -enable-upcoming-feature ImmutableWeakCaptures -warnings-as-errors
+```
+
+**`.swiftlint.yml`** (strict lint + all analyzer rules; run under `swiftlint lint` and `swiftlint analyze`):
+```yaml
+strict: true
+
+analyzer_rules: # pinned for SwiftLint 0.65.1 — do not use `all` (floats)
+  - capture_variable
+  - explicit_self
+  - typesafe_array_init
+  - unused_declaration
+  - unused_import
+
+opt_in_rules: # pinned subset for 0.65.1 — expand only with reviewed additions, never `all`
+  - empty_count
+  - empty_string
+  - force_unwrapping
+  - implicitly_unwrapped_optional
+  - closure_end_indentation
+  - collection_alignment
+  - explicit_acl
+  - file_header
+  - force_cast
+  - force_try
+  - missing_docs
+  - redundant_nil_coalescing
+  - vertical_whitespace
+  - yoda_condition
+
+disabled_rules:
+  # owned by swift-format -> avoid double-reporting
+  - trailing_whitespace
+  - indentation_width
+  - opening_brace
+  - closure_spacing
+  - comma
+  - colon
+  - comment_spacing
+  - empty_enum_arguments
+  - sorted_imports
+  # policy exceptions (documented, not silent)
+  - todo
+  - explicit_top_level_acl
+  - no_extension_access_modifier
+  - no_grouping_extension
+  - number_separator
+  - prefixed_toplevel_constant
+  - prohibited_interface_builder
+  - required_deinit
+  - explicit_init
+
+line_length:
+  warning: 120
+  error: 160
+  ignores_comments: false
+  ignores_urls: false
+
+function_body_length:
+  warning: 60
+  error: 100
+
+type_body_length:
+  warning: 300
+  error: 400
+
+file_length:
+  warning: 500
+  error: 800
+
+identifier_name:
+  min_length:
+    error: 3
+  excluded: [id, x, y, z, i, j, k, vm, db, ui]
+```
+
+**`.swift-format`** (Apple swift-format; run under `swift format lint --strict`. Regenerate defaults for your toolchain with `swift-format dump-configuration`):
+```json
+{
+  "version": 1,
+  "lineLength": 120,
+  "indentation": { "spaces": 4 },
+  "tabWidth": 4,
+  "maximumBlankLines": 1,
+  "respectsExistingLineBreaks": true,
+  "lineBreakBeforeEachArgument": false,
+  "multiElementCollectionTrailingCommas": true,
+  "prioritizeKeepingFunctionOutputTogether": true,
+  "indentConditionalCompilationBlocks": true,
+  "indentSwitchCaseLabels": false,
+  "rules": {
+    "AlwaysUseLowerCamelCase": true,
+    "AmbiguousTrailingClosureOverload": true,
+    "DoNotUseSemicolons": true,
+    "NoBlockComments": true,
+    "NoParensAroundConditions": true,
+    "NoVoidReturnOnFunctionSignature": true,
+    "OneCasePerLine": true,
+    "OneVariableDeclarationPerLine": true,
+    "OrderedImports": true,
+    "ReturnVoidInsteadOfEmptyTuple": true,
+    "UseEarlyExits": true,
+    "UseShorthandTypeNames": true,
+    "UseSingleLinePropertyGetter": true,
+    "UseTripleSlashForDocumentationComments": true,
+    "UseWhereClausesInForLoops": true,
+    "ValidateDocumentationComments": false
+  }
+}
+```
+
+**`Package.swift`** (SPM strictness; requires tools-version 6.2 for `treatAllWarnings`/`strictMemorySafety`):
+```swift
+// swift-tools-version: 6.2
+import PackageDescription
+
+let strict: [SwiftSetting] = [
+    .enableUpcomingFeature("ExistentialAny"),                 // SE-0335 (Swift 5.6)
+    .enableUpcomingFeature("InternalImportsByDefault"),       // SE-0409 (Swift 6.0)
+    .enableUpcomingFeature("MemberImportVisibility"),         // SE-0444 (Swift 6.1)
+    .enableUpcomingFeature("InferIsolatedConformances"),      // SE-0470 (Swift 6.2)
+    .enableUpcomingFeature("NonisolatedNonsendingByDefault"), // SE-0461 (Swift 6.2)
+    .enableUpcomingFeature("ImmutableWeakCaptures"),          // SE-0481 (Swift 6.2)
+    .strictMemorySafety(),                                    // PackageDescription 6.2
+    .treatAllWarnings(as: .error),                            // PackageDescription 6.2
+]
+
+let package = Package(
+    name: "Feature",
+    platforms: [.iOS(.v18)],
+    products: [.library(name: "Feature", targets: ["Feature"])],
+    targets: [
+        .target(name: "Feature", swiftSettings: strict),
+        .testTarget(name: "FeatureTests", dependencies: ["Feature"], swiftSettings: strict),
+    ]
+)
+```
+
+> Swift 5 language mode only (migration window): add `.enableUpcomingFeature("StrictConcurrency")` and `.unsafeFlags(["-strict-concurrency=complete"])` (root packages only — `unsafeFlags` is rejected in dependencies).
+
+**`.xcodegen/project.yml`** (deterministic project; commit the generated `.xcodeproj`):
+```yaml
+name: App
+options:
+  minimumXcodeGenVersion: 2.46.0
+  deploymentTarget:
+    iOS: "18.0"
+  createIntermediateGroups: true
+targets:
+  App:
+    type: application
+    platform: iOS
+    sources: [Sources/App]
+    configFiles:
+      Debug: Config/Strict.xcconfig
+      Release: Config/Strict.xcconfig
+    scheme:
+      gatherCoverageData: true
+      testTargets: [AppTests, AppUITests]
+```
+
+### Mandatory Gate Order
+
+> **Precondition:** verify every tool in the Required Toolchain table is installed and matches its pinned minimum version (`xcodebuild -version`, `swift --version`, `swiftlint version`, `swift-format --version`, `xcodegen --version`). If any tool is missing or the wrong version, install or update it first and rerun the check. Do not proceed to the gates below until this check is green.
+
+```bash
+# 0. Generate the project deterministically (commit the result; CI regenerates + asserts no diff)
+xcodegen generate --spec .xcodegen/project.yml --project . && git diff --exit-code -- App.xcodeproj
+
+# 1. Format gate — Apple swift-format (toolchain-bundled) — warnings are failures (required)
+swift-format lint --strict --recursive Sources Tests
+# Optional appendix — SwiftFormat (nicklockwood) — never run as required gate alongside Apple swift-format; both must never run together as required gates. Use only if Apple gate is disabled:
+# swiftformat --lint Sources Tests
+
+# 2. Style gate — every warning is an error
+swiftlint lint --strict --config .swiftlint.yml
+
+# 3. Build gate — Swift 6 strict concurrency + warnings-as-errors, capture compiler log
+xcodebuild -project App.xcodeproj -scheme App -configuration Debug \
+  -destination 'generic/platform=iOS Simulator' \
+  SWIFT_TREAT_WARNINGS_AS_ERRORS=YES SWIFT_STRICT_CONCURRENCY=complete \
+  clean build > xcodebuild.log 2>&1
+
+# 4. Analyzer gate — type-checked AST rules (explicit_self, unused_declaration, unused_import, capture_variable, typesafe_array_init)
+swiftlint analyze --strict --compiler-log-path xcodebuild.log
+
+# 5. Static analyzer gate (Clang analyzer)
+xcodebuild -project App.xcodeproj -scheme App -configuration Debug analyze
+
+# 6. API-breakage gate (library/package targets only)
+BASELINE=$(git describe --tags --abbrev=0 2>/dev/null || true)
+if [ -z "$BASELINE" ]; then echo "SKIP: no git tags — cannot diff public API (tag a baseline release to enable this gate)"; else swift package diagnose-api-breaking-changes "$BASELINE"; fi
+
+# 7. Dependency hygiene — declared vs imported (advisory until it stabilizes)
+swift-dependency-audit --path . --fail-on-unused
+
+# 8. Secret gate — fails on any finding
+gitleaks detect --source . --redact --no-banner --exit-code 1
+
+# 9. Vulnerability + license gate
+osv-scanner scan source -r . --licenses
+
+# 10. Test + coverage gate
+xcodebuild test -project App.xcodeproj -scheme App \
+  -destination 'platform=iOS Simulator,name=iPhone 16' \
+  -enableCodeCoverage YES -resultBundlePath Test.xcresult
+COVERAGE=$(xcrun xccov view --report --json Test.xcresult | jq -r '[.targets[] | select(.name=="App.app")][0].lineCoverage // empty')
+if [ -z "$COVERAGE" ] || [ "$COVERAGE" = "null" ]; then echo "FAIL coverage: App target not found in xccov report (check .xcodeproj scheme gatherCoverageData)"; exit 1; fi
+awk -v c="$COVERAGE" 'BEGIN { if (c+0 < 0.80) { print "FAIL coverage "c" < 0.80"; exit 1 } }'
+
+# 11. Thread Sanitizer gate (separate CI job)
+xcodebuild test -project App.xcodeproj -scheme App \
+  -destination 'platform=iOS Simulator,name=iPhone 16' \
+  -enableThreadSanitizer YES
+
+# 12. Address Sanitizer gate (separate CI job)
+xcodebuild test -project App.xcodeproj -scheme App \
+  -destination 'platform=iOS Simulator,name=iPhone 16' \
+  -enableAddressSanitizer YES
+```
+
+> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI.
+
+### Hallucination Traps to Block
+
+- AI passes a non-`Sendable` model across an actor/`@MainActor` boundary -> `SWIFT_STRICT_CONCURRENCY=complete` / `-strict-concurrency=complete` (Swift 6 mode makes it a hard error).
+- AI omits `any` on protocol existentials (`let delegate: Foo`) -> `-enable-upcoming-feature ExistentialAny` forces `any Foo`.
+- AI imports a module or declares a target dependency it never uses -> SwiftLint analyzer `unused_import` / `unused_declaration`, plus `swift-dependency-audit`.
+- AI leaves generated scaffolding, dead VMs, or unused `@ViewBuilder` helpers -> SwiftLint analyzer `unused_declaration` (advisory only: `periphery.pro` or a fork for a full scan).
+- AI force-unwraps, uses `try!`, `as!`, or implicitly unwrapped optionals -> swift-format rules `NeverForceUnwrap`/`NeverUseForceTry`/`NeverUseImplicitlyUnwrappedOptionals`; SwiftLint `force_unwrapping`/`force_cast`/`force_try`.
+- AI hard-codes API keys/tokens in Swift config or `Info.plist` -> gitleaks (`--exit-code 1`, scans history + archives).
+- AI pins a vulnerable package version -> osv-scanner (`Package.resolved`/`Package.swift`).
+- AI ships a data race that only manifests under concurrency -> Thread Sanitizer gate (`-enableThreadSanitizer YES`).
+- AI silently breaks a public package API -> `swift package diagnose-api-breaking-changes <baseline>`.
+
+### Evidence to Record
+
+Paste into Verification Evidence (commands + pass criterion):
+
+1. `swift-format lint --strict --recursive Sources Tests` -> **exit 0**, zero diagnostics (Apple swift-format 604.0.0) — required gate; SwiftFormat (nicklockwood) is optional appendix only, never run alongside Apple gate as required.
+2. `swiftlint lint --strict --config .swiftlint.yml` -> **exit 0**, zero warnings.
+3. `xcodebuild ... build SWIFT_TREAT_WARNINGS_AS_ERRORS=YES SWIFT_STRICT_CONCURRENCY=complete > xcodebuild.log 2>&1` -> **exit 0**, no `warning:`/`error:`; record `xcodebuild -version` and `swift --version`.
+4. `swiftlint analyze --strict --compiler-log-path xcodebuild.log` -> **exit 0**, zero analyzer violations.
+5. `xcodebuild ... analyze` -> **exit 0**, no analyzer findings.
+6. `swift package diagnose-api-breaking-changes <baseline>` (library only) -> **exit 0**, "no breaking changes".
+7. `gitleaks detect --source . --redact --exit-code 1` -> **exit 0**, "no leaks found".
+8. `osv-scanner scan source -r . --licenses` -> **exit 0**, no known vulnerabilities.
+9. `xcodebuild test ... -enableCodeCoverage YES` + `xccov` threshold -> tests pass and line coverage >= 0.80 (paste the exact computed percentage).
+10. TSan job and ASan job -> **exit 0**, zero sanitizer reports.
+
+<!-- sources -->
+- https://github.com/realm/SwiftLint/releases (SwiftLint 0.65.1) and https://github.com/realm/SwiftLint (strict/analyze/analyzer_rules)
+- https://realm.github.io/SwiftLint/rule-directory.html (analyzer rules: capture_variable, explicit_self, typesafe_array_init, unused_declaration, unused_import)
+- https://github.com/nicklockwood/SwiftFormat/releases (0.63.0) and https://github.com/nicklockwood/SwiftFormat (--lint exit codes)
+- https://github.com/swiftlang/swift-format/releases (604.0.0) and https://github.com/swiftlang/swift-format (lint `-s/--strict`)
+- https://developer.apple.com/documentation/Swift/AdoptingSwift6 (strict concurrency)
+- https://www.swift.org/migration/documentation/migrationguide/ (Swift 6 language mode opt-in)
+- https://github.com/treastrain/swift-upcomingfeatureflags-cheatsheet (ExistentialAny, InternalImportsByDefault, MemberImportVisibility, InferIsolatedConformances, NonisolatedNonsendingByDefault, ImmutableWeakCaptures)
+- https://github.com/swiftlang/swift-package-manager/blob/main/Sources/Runtimes/PackageDescription/BuildSettings.swift (`.treatAllWarnings(as:)`, `.strictMemorySafety()`, `.enableUpcomingFeature`)
+- https://github.com/swiftlang/swift-package-manager/blob/main/Sources/PackageManagerDocs/Documentation.docc/Package/PackageDiagnoseAPIBreakingChange.md
+- https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early (`-enableThreadSanitizer YES`, `-enableAddressSanitizer YES`)
+- https://github.com/google/osv-scanner/releases (v2.6.0)
+- https://github.com/gitleaks/gitleaks/releases (v8.30.1)
+- https://github.com/pointfreeco/swift-snapshot-testing/releases (1.19.5)
+- https://github.com/yonaskolb/XcodeGen/releases (2.46.0) and https://github.com/tuist/tuist/releases (4.211.x)
+- https://github.com/peripheryapp/periphery (archived 2026-08-12) and https://periphery.pro/a-new-chapter (commercial transition)
+- https://github.com/tonyarnold/swift-dependency-audit (v2.0.8, unused/missing SPM deps)
+
 ## Currency Baseline
 
 - **Swift 6 mode:** Enable the Swift 6 language mode (complete concurrency checking); all types crossing actor boundaries must conform to `Sendable`, with ViewModels kept `@MainActor`-isolated.
diff --git a/skill-templates/nestjs-prisma-vertical/SKILL.md b/skill-templates/nestjs-prisma-vertical/SKILL.md
index 9482da3..9d0b70a 100644
--- a/skill-templates/nestjs-prisma-vertical/SKILL.md
+++ b/skill-templates/nestjs-prisma-vertical/SKILL.md
@@ -75,3 +75,434 @@ Do not use inline `try/catch` for standard HTTP errors. Throw NestJS exceptions
 | Feature Service  | Unit      | Jest + Mock Prisma        | `auth.service.spec.ts`    |
 | Controller       | Unit      | Jest                      | `auth.controller.spec.ts` |
 | Feature Endpoint | E2E       | Jest + Supertest + TestDB | `auth.e2e-spec.ts`        |
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+### Strict Baseline
+
+> Target: **NestJS 12 + Prisma 7 + TypeScript, organized as Vertical Slice Architecture**
+> (`src/slices/<slice>/…`, one public `index.ts` barrel per slice).
+> All versions verified live against the npm registry / official docs in Sep 2026. Pinned to the
+> **strictest actively-maintained** tool for each role. Deprecated or dormant tools are named and
+> excluded. Two stack-specific deviations from a plain Node service are called out inline: NestJS DI
+> relies on **parameter properties + `emitDecoratorMetadata`**, and Prisma 7 requires **ESM**.
+
+### Required Toolchain
+
+| Tool | Purpose | Minimum version | Activate |
+| --- | --- | --- | --- |
+| Node.js | Runtime; LTS only | 24.x Active LTS | `printf '24\n' > .nvmrc` + `"engines": { "node": ">=24.0.0" }` |
+| Corepack | Pin the package manager (`packageManager` field) | bundled in Node ≤24 (install manually on Node ≥25) | `corepack enable` + `"packageManager": "npm@11.6.0"` + `"devEngines": { "packageManager": { "name": "npm", "onFail": "error" } }` |
+| TypeScript | `tsc --noEmit` type gate + parser backend for typed lint | 6.0.3 (npm `latest` is 7.0.2 — **not** a typed-lint backend, see Discarded) | `npm i -D typescript@6.0.3` |
+| @typescript/native-preview (optional) | TS7 `tsgo` fast `--noEmit` gate alongside TS6 | 7.0.2 | `npm i -D @typescript/native-preview@^7` (run `tsgo --noEmit` only) |
+| ESLint | Core linter, flat config only (eslintrc removed in v10) | 10.0.0 (10.11.0) | `npm i -D eslint@^10 @eslint/js@^10` |
+| typescript-eslint | Type-aware rules (`strictTypeChecked` + `stylisticTypeChecked`) | 8.70.1 | `npm i -D typescript-eslint@^8` |
+| eslint-plugin-n | Node correctness (`no-process-exit`, `no-missing-import`) | 18.2.2 | `npm i -D eslint-plugin-n@^18` |
+| eslint-plugin-import-x | Fast `no-restricted-paths` per-file guard (maintained fork of frozen `eslint-plugin-import`) | 4.16.2 | `npm i -D eslint-plugin-import-x@^4` |
+| dependency-cruiser | **Primary** slice-boundary + cycle gate on the real resolved graph | 18.4.0 | `npm i -D dependency-cruiser@^18` |
+| eslint-plugin-boundaries | Secondary, in-editor boundary feedback (entity model v7) | 7.2.0 | `npm i -D eslint-plugin-boundaries@^7` |
+| Prettier | Formatting, run **separately** (never merged into ESLint) | 3.9.8 | `npm i -D prettier@^3 eslint-config-prettier@^10` |
+| knip | Unused files, exports, and dependencies | 6.37.0 | `npm i -D knip@^6` |
+| lockfile-lint | Lockfile host/integrity policy (anti-typosquat / injection) | 5.0.1 | `npm i -D lockfile-lint@^5` |
+| osv-scanner | Vulnerability scan against OSV (replaces/augments `npm audit`) | 2.5.1 | `go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest` (or the official GH Action) |
+| Prisma CLI + Client | Schema, migration, and generated type gate | prisma 7.10.0 / @prisma/client 7.10.0 (v8 is in RC — see note) | `npm i -D prisma@^7.10.0` + `npm i @prisma/client@^7.10.0 @prisma/adapter-pg@^7.10.0` |
+| @nestjs/testing | Nest DI test module builder | 12.0.4 | `npm i -D @nestjs/testing@^12.0.4` |
+| supertest | HTTP e2e assertions against the real Nest app | 7.2.2 | `npm i -D supertest@^7 @types/supertest@^7` |
+| class-validator + class-transformer | DTO contract enforcement (`whitelist`, `forbidNonWhitelisted`) | 0.15.1 / 0.5.x | `npm i class-validator@^0.15.1 class-transformer@^0.5` |
+| Vitest + @vitest/coverage-v8 | Unit/integration runner with fail-on-threshold coverage | 5.0.1 | `npm i -D vitest@^5 @vitest/coverage-v8@^5` |
+| type-coverage | Compile-time `any` budget gate | 2.30.1 | `npm i -D type-coverage@^2` |
+| oasdiff | OpenAPI breaking-change gate (Nest `@nestjs/swagger` output) | 1.11.x | `brew install oasdiff` / `curl -fsSL …/install.sh \| sh` / GH Action |
+| @nestjs/swagger | Emits `openapi.json` for the oasdiff contract gate | 12.x | `npm i @nestjs/swagger@^12` |
+
+**Prisma major-version note (2026).** The **stable** line is **Prisma 7.10.0** (`@prisma/client@7.10.0`);
+Prisma **8** is rolling out — the `prisma` CLI's `latest` dist-tag already points at **`8.0.0-rc.15`**
+and the docs call v8 "the current release", but the runtime (`@prisma/orm-postgres`, `@prisma/client`)
+is still `7.10.0` on `latest` with v8 only under `dev`/RC tags. Pin `^7.10.0` for a strict gate today.
+v7 breaking changes that the gates below depend on: **ESM-only** (`"type": "module"`), the
+`prisma-client` generator with a **required `output`**, **driver adapters required**, `prisma.config.ts`
+is the new config home, **env is not auto-loaded** (`import "dotenv/config"` in the config), `migrate dev`
+**no longer auto-runs `generate`**, and `migrate diff` flags changed from `--from-url`/`--to-url` to
+`--from-config-datasource`/`--to-config-datasource`. Prisma 8 replaces the migrate flow with
+`contract infer/emit` + `migration plan` + `db sign`/`db migrate`/`db verify`; treat that as a future
+migration, not this baseline.
+
+**Discarded / demoted (say so, do not silently use):**
+- **`ts-prune`** — last npm release **0.10.3 (2021)**, dormant. Superseded by **knip** (files + exports + deps in one pass).
+- **`depcheck`** — 1.4.7; its own README now says *"We strongly recommend switching to knip, a more actively maintained and feature-rich alternative."* Excluded.
+- **`eslint-plugin-import`** — 2.32.0, effectively frozen and refuses modern `exports`/specifier support; use **`eslint-plugin-import-x`** (declares ESLint 8/9/10 support).
+- **`eslint-plugin-prettier`** — merging Prettier into ESLint is explicitly discouraged (slow, duplicate diagnostics). Run `prettier --check` as its own gate and let **`eslint-config-prettier`** (10.1.8) only switch off conflicting stylistic rules.
+- **TypeScript 7.0.2 as the typed-lint backend** — 7.x is npm `latest`, but `typescript-eslint@8` supports only up to **`<6.1.0`**; pointing `typescript` at 7 makes typed lint crash. Pin `typescript@6.0.3` for lint and run TS7 (`tsgo`) side-by-side for the fast type-check only.
+- **`erasableSyntaxOnly`** — valid and strict on Node backends, but **rejected for NestJS**: it bans parameter properties (`constructor(private readonly db: PrismaService)`) which NestJS DI depends on. Leave it **off** here (it is on in the plain-Node sibling gate).
+- **`madge`** — cycle/graph visualiser, dormant; cycle detection is already a `dependency-cruiser` rule.
+
+### Strict Baseline Config
+
+`tsconfig.json` — every strict flag; `tsc --noEmit` is the gate. NestJS deviations are marked:
+
+```jsonc
+{
+  "compilerOptions": {
+    "target": "es2024",
+    "lib": ["es2024"],
+    "module": "nodenext",
+    "moduleResolution": "nodenext",
+    "moduleDetection": "force",
+    "types": ["node"],
+    "rootDir": "./src",
+    "outDir": "./dist",
+
+    /* NestJS: decorator metadata + DI parameter properties */
+    "experimentalDecorators": true,
+    "emitDecoratorMetadata": true,
+    /* "erasableSyntaxOnly" is intentionally NOT set: NestJS DI uses parameter properties */
+
+    /* maximum static strictness */
+    "strict": true,
+    "noUncheckedIndexedAccess": true,
+    "exactOptionalPropertyTypes": true,
+    "noImplicitOverride": true,
+    "noImplicitReturns": true,
+    "noFallthroughCasesInSwitch": true,
+    "noImplicitThis": true,
+    "useUnknownInCatchVariables": true,
+    "noPropertyAccessFromIndexSignature": true,
+    "noUnusedLocals": true,
+    "noUnusedParameters": true,
+    "allowUnreachableCode": false,
+    "allowUnusedLabels": false,
+    "forceConsistentCasingInFileNames": true,
+
+    /* module purity */
+    "verbatimModuleSyntax": true,
+    "isolatedModules": true,
+    "noUncheckedSideEffectImports": true,
+
+    "declaration": true,
+    "declarationMap": true,
+    "sourceMap": true,
+    "skipLibCheck": false
+  },
+  "include": ["src"],
+  "exclude": ["dist", "node_modules", "generated/prisma"]
+}
+```
+
+> ⚠️ `verbatimModuleSyntax` + `emitDecoratorMetadata` conflict: never write `import type { Foo }` for a
+> class that is **injected** (`constructor(private foo: Foo)`), or Nest emits `Object` metadata and DI
+> silently fails at boot. Because of this, the `consistent-type-imports` autofix is **disabled** below;
+> the e2e boot test is the real guard.
+
+`eslint.config.mjs` — ESLint 10 flat config, strictest type-checked presets:
+
+```js
+// @ts-check
+import js from '@eslint/js';
+import { defineConfig } from 'eslint/config';
+import tseslint from 'typescript-eslint';
+import node from 'eslint-plugin-n';
+import importX from 'eslint-plugin-import-x';
+import prettier from 'eslint-config-prettier';
+
+export default defineConfig(
+  { ignores: ['dist/**', 'coverage/**', 'node_modules/**', 'generated/prisma/**', '**/*.d.ts'] },
+
+  js.configs.recommended,
+
+  ...tseslint.configs.strictTypeChecked,
+  ...tseslint.configs.stylisticTypeChecked,
+
+  {
+    files: ['**/*.{ts,mts,cts}'],
+    languageOptions: {
+      parserOptions: {
+        projectService: true,                    // typed linting; no tsconfig.eslint.json
+        tsconfigRootDir: import.meta.dirname,
+      },
+    },
+    rules: {
+      '@typescript-eslint/no-floating-promises': ['error', { ignoreVoid: false }],
+      '@typescript-eslint/no-misused-promises': ['error', {
+        checksConditionals: true,
+        checksSpreads: true,
+        checksVoidReturn: { arguments: true, attributes: false, returns: true },
+      }],
+      '@typescript-eslint/switch-exhaustiveness-check': ['error', {
+        considerDefaultExhaustiveForUnions: true,
+        requireDefaultForNonUnion: true,
+      }],
+      '@typescript-eslint/consistent-type-imports': 'off',   // Nest DI: do NOT type-only injected classes
+      '@typescript-eslint/no-explicit-any': 'error',
+      '@typescript-eslint/explicit-function-return-type': ['error', { allowExpressions: true }],
+      'no-console': 'error',
+
+      /* Prisma raw-query discipline: unsafe variants are banned */
+      'no-restricted-properties': ['error',
+        { object: 'prisma', property: '$queryRawUnsafe',   message: 'Use Prisma.sql tagged $queryRaw.' },
+        { object: 'prisma', property: '$executeRawUnsafe', message: 'Use Prisma.sql tagged $executeRaw.' },
+        { object: 'this',   property: '$queryRawUnsafe',   message: 'Use Prisma.sql tagged $queryRaw.' },
+        { object: 'this',   property: '$executeRawUnsafe', message: 'Use Prisma.sql tagged $executeRaw.' },
+      ],
+    },
+  },
+
+  node.configs["flat/recommended-module"],
+  importX.flatConfigs.recommended,
+
+  prettier,   // LAST: turns off formatting rules that would fight Prettier
+);
+```
+
+`.dependency-cruiser.cjs` — **the slice-boundary gate** (copy-paste; layout `src/slices/<slice>/…`):
+
+```js
+/** @type {import('dependency-cruiser').IConfiguration} */
+module.exports = {
+  forbidden: [
+    {
+      name: 'no-circular',
+      severity: 'error',
+      comment: 'No dependency cycles anywhere.',
+      from: {},
+      to: { circular: true },
+    },
+    {
+      name: 'no-cross-slice-imports',
+      severity: 'error',
+      comment: 'A slice may not import another slice except through its public index.ts barrel.',
+      from: { path: '^src/slices/([^/]+)/' },
+      to: {
+        path: '^src/slices/(?!$1)([^/]+)/',            // $1 validated on dependency-cruiser 18.4 — proven backreference, do not expand manually unless version <18.4
+        pathNot: ['^src/slices/[^/]+/index\\.ts$'],    // only the public barrel is allowed
+      },
+    },
+    {
+      name: 'no-slice-internals-from-shared',
+      severity: 'error',
+      comment: 'Shared/platform code must never depend on a slice.',
+      from: { path: '^src/(shared|platform)/' },
+      to: { path: '^src/slices/' },
+    },
+    {
+      name: 'no-slice-to-app-root',
+      severity: 'error',
+      comment: 'Slices must not import the composition root (main.ts / app.module.ts).',
+      from: { path: '^src/slices/' },
+      to: { path: '^src/(main|app\\.module)\\.ts$' },
+    },
+    {
+      name: 'no-orphans',
+      severity: 'error',
+      comment: 'Unreferenced modules are dead code.',
+      from: { orphan: true, pathNot: ['\\.d\\.ts$', '\\.(spec|e2e-spec)\\.ts$', '^src/main\\.ts$'] },
+      to: {},
+    },
+  ],
+  options: {
+    tsConfig: { fileName: 'tsconfig.json' },
+    tsPreCompilationDeps: true,
+    doNotFollow: { path: 'node_modules' },
+    enhancedResolveOptions: { exportsFields: ['exports'], conditionNames: ['import', 'require', 'node', 'default'] },
+    exclude: { path: ['\\.(spec|e2e-spec)\\.ts$', '\\.config\\.(ts|js|mjs|cjs)$', '^dist/', '^generated/prisma/'] },
+    includeOnly: { path: '^src/' },
+  },
+};
+```
+
+ESLint-native alternative (in-editor, same intent) via **eslint-plugin-boundaries v7**:
+
+```js
+{
+  files: ['src/slices/**/*.ts'],
+  plugins: { boundaries },
+  settings: {
+    'boundaries/elements': [
+      { type: 'slice', pattern: 'src/slices/*', capture: ['slice'] },
+      { type: 'shared', pattern: 'src/shared/*' },
+    ],
+  },
+  rules: {
+    'boundaries/dependencies': [2, {
+      default: 'disallow',
+      policies: [
+        { from: { element: { type: 'slice' } }, allow: { to: { element: { type: 'slice', filters: { slice: '{{ from.slice }}' } } } } },
+        { from: { element: { type: 'slice' } }, allow: { to: { element: { type: 'shared' } } } },
+      ],
+    }],
+  },
+}
+```
+
+`knip.json` — dead code / dependency hygiene:
+
+```jsonc
+{
+  "$schema": "https://unpkg.com/knip@6/schema.json",
+  "entry": ["src/main.ts", "src/**/*.module.ts", "test/**/*.e2e-spec.ts"],
+  "project": ["src/**/*.ts", "!generated/prisma/**"],
+  "ignoreExportsUsedInFile": true,
+  "ignoreDependencies": ["@prisma/client", "@nestjs/testing"]
+}
+```
+
+`vitest.config.ts` — coverage thresholds are the gate (Vitest 5: `coverage.include` required):
+
+```ts
+import { defineConfig } from 'vitest/config';
+
+export default defineConfig({
+  test: {
+    environment: 'node',
+    include: ['src/**/*.spec.ts', 'test/**/*.e2e-spec.ts'],
+    coverage: {
+      provider: 'v8',
+      reporter: ['text', 'json-summary', 'lcov'],
+      include: ['src/slices/**/*.ts'],
+      exclude: ['src/**/*.module.ts', 'src/**/index.ts', 'generated/prisma/**'],
+      thresholds: {
+        lines: 90,
+        functions: 90,
+        branches: 85,
+        statements: 90,
+        perFile: true,                          // every slice file, not just the aggregate
+      },
+    },
+  },
+});
+```
+
+`prisma.config.ts` (root, Prisma 7 shape) — env is NOT auto-loaded:
+
+```ts
+import 'dotenv/config';
+import { defineConfig, env } from 'prisma/config';
+
+export default defineConfig({
+  schema: 'prisma/schema.prisma',
+  migrations: { path: 'prisma/migrations', seed: 'tsx prisma/seed.ts' },
+  datasource: { url: env('DATABASE_URL') },
+});
+```
+
+DTO strictness — the global pipe (mass-assignment / unknown-field guard):
+
+```ts
+app.useGlobalPipes(new ValidationPipe({
+  whitelist: true,
+  forbidNonWhitelisted: true,
+  forbidUnknownValues: true,
+  transform: true,
+  transformOptions: { enableImplicitConversion: false },
+  validationError: { target: false, value: false },
+}));
+```
+
+`package.json` — single gate chain + pins:
+
+```jsonc
+{
+  "type": "module",
+  "engines": { "node": ">=24.0.0" },
+  "packageManager": "npm@11.6.0",
+  "devEngines": { "packageManager": { "name": "npm", "onFail": "error" } },
+  "scripts": {
+    "verify": "npm run typecheck && npm run lint && npm run arch && npm run deadcode && npm run prisma:check && npm run test && npm run types && npm run api:diff",
+    "typecheck": "tsc --noEmit",
+    "lint": "eslint . --max-warnings=0",
+    "format:check": "prettier --check .",
+    "arch": "depcruise src --config .dependency-cruiser.cjs",
+    "deadcode": "knip --production --no-progress",
+    "prisma:check": "prisma validate && prisma format --check && prisma migrate diff --exit-code --from-migrations prisma/migrations --to-schema prisma/schema.prisma && prisma generate && git diff --exit-code -- generated/prisma",
+    "test": "vitest run --coverage",
+    "types": "type-coverage --at-least 99 --strict --ignore-catch"
+  }
+}
+```
+
+### Mandatory Gate Order
+
+1. `corepack enable && npm ci --ignore-scripts`  *(supply-chain: no install-time scripts)*
+2. `npx lockfile-lint --path package-lock.json --type npm --validate-https --allowed-hosts npm --validate-integrity`
+3. `npx osv-scanner scan -L package-lock.json --format=table`  *(or `npm audit --audit-level=high`)*
+4. `npx tsc --noEmit`
+5. `npx eslint . --max-warnings=0`
+6. `npx depcruise src --config .dependency-cruiser.cjs`
+7. `npx knip --production --no-progress`
+8. `npx prisma validate`
+9. `npx prisma format --check`
+10. `npx prisma migrate diff --exit-code --from-migrations prisma/migrations --to-schema prisma/schema.prisma`  *(exit `2` = schema and migrations drifted)*
+11. `npx prisma generate && git diff --exit-code -- generated/prisma`  *(proves the committed client matches the schema; commit `generated/prisma` for this check)*
+12. `npx prisma migrate status`  *(needs a live DB service; exits `1` on pending/diverged/failed migrations)*
+13. `npx vitest run --coverage`
+14. `npx type-coverage --at-least 99 --strict --ignore-catch`
+15. `npx oasdiff breaking openapi.baseline.json openapi.generated.json --fail-on ERR`
+
+> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI.
+> (`eslint` is invoked WITHOUT `--fix`; `--max-warnings=0` makes any warning fatal.)
+
+### Hallucination Traps to Block
+
+- Invented Prisma model/field/relation names in queries → `prisma validate` + `prisma generate` (typed client) + `npx tsc --noEmit`; the generated client has no such member.
+- A slice reaching into another slice's internals ("just import the repository") → `dependency-cruiser` `no-cross-slice-imports` (group-capture `$1`, only `index.ts` barrels allowed).
+- Untyped raw SQL or SQL string concatenation → `no-restricted-properties` bans `$queryRawUnsafe`/`$executeRawUnsafe`; `strictTypeChecked`'s `no-unsafe-*` flags `any` rows; require `Prisma.sql` tagged templates.
+- An unawaited `await` on a write (`prisma.user.create(...)` without `await`) silently succeeding → `@typescript-eslint/no-floating-promises` + `no-misused-promises`.
+- A new status-enum member added but a `switch` handler not updated → `@typescript-eslint/switch-exhaustiveness-check` (`requireDefaultForNonUnion`, `considerDefaultExhaustiveForUnions`).
+- Editing the generated Prisma client instead of `schema.prisma` → gate 11 `prisma generate && git diff --exit-code -- generated/prisma` fails on the hand-edit.
+- Migration files and `schema.prisma` drifting apart (missing migration) → gate 10 `prisma migrate diff --exit-code` returns `2`.
+- DTO accepts unknown/extra JSON fields (mass assignment) → global `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })`; e2e supertest asserts `400` for an unknown field.
+- AI marks an **injected** provider as `import type` and breaks `emitDecoratorMetadata` → `consistent-type-imports` kept off; e2e `Test.createTestingModule(...).compile()` boot test fails loudly.
+- Dead slice/export/dependency left after a refactor → `knip --production`.
+- Shipping a breaking API change → `oasdiff breaking … --fail-on ERR`.
+
+### Evidence to Record
+
+Paste the exact command and its pass signal into Verification Evidence; all must exit `0`.
+
+- `npx tsc --noEmit` → exit `0`, no output.
+- `npx eslint . --max-warnings=0` → exit `0`, `0 problems`.
+- `npx depcruise src --config .dependency-cruiser.cjs` → exit `0`, `no dependency violations found`.
+- `npx knip --production --no-progress` → exit `0`, no unused files/exports/dependencies listed.
+- `npx prisma validate` → exit `0`, `The schema at … is valid`.
+- `npx prisma format --check` → exit `0` (no diff; unformatted schema fails).
+- `npx prisma migrate diff --exit-code --from-migrations prisma/migrations --to-schema prisma/schema.prisma` → exit `0` (empty diff; `2` = drift).
+- `npx prisma generate && git diff --exit-code -- generated/prisma` → exit `0` (generated client is fresh and committed).
+- `npx prisma migrate status` → exit `0`, `Database schema is up to date!`.
+- `npx vitest run --coverage` → exit `0`, every coverage threshold line `>= 90` and all `Test Files` passed.
+- `npx type-coverage --at-least 99 --strict --ignore-catch` → exit `0`, reported `type coverage >= 99%`.
+- `npx oasdiff breaking openapi.baseline.json openapi.generated.json --fail-on ERR` → exit `0`, no breaking changes.
+- `npx lockfile-lint …` and `npx osv-scanner scan -L package-lock.json` → exit `0`, no host violations and **no HIGH/CRITICAL** advisories.
+- E2E boot proof: `npx vitest run test/app.e2e-spec.ts` exits `0` (Nest DI module compiles; all injections resolve).
+
+<!-- sources -->
+- https://typescript-eslint.io/getting-started/typed-linting/
+- https://typescript-eslint.io/users/configs/
+- https://typescript-eslint.io/rules/switch-exhaustiveness-check/
+- https://typescript-eslint.io/rules/no-floating-promises/
+- https://typescript-eslint.io/rules/no-misused-promises/
+- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html
+- https://www.typescriptlang.org/tsconfig/noUncheckedSideEffectImports.html
+- https://www.typescriptlang.org/tsconfig/
+- https://docs.bswen.com/blog/2026-02-21-typescript-60-tsconfig-defaults/
+- https://eslint.org/blog/2026/02/eslint-v10.0.0-released/
+- https://docs.synapsestudios.com/implementation/frameworks/nest/dependency-cruiser-config.html
+- https://github.com/sverweij/dependency-cruiser
+- https://github.com/javierbrea/eslint-plugin-boundaries
+- https://github.com/un-ts/eslint-plugin-import-x
+- https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7
+- https://www.prisma.io/docs/orm/reference/prisma-cli-reference
+- https://www.prisma.io/docs/guides/upgrade-prisma-orm/postgresql
+- https://github.com/webpro-nl/knip
+- https://github.com/depcheck/depcheck
+- https://github.com/lirantal/lockfile-lint
+- https://google.github.io/osv-scanner/usage/
+- https://github.com/oasdiff/oasdiff
+- https://vitest.dev/config/coverage
+- https://github.com/plantain-00/type-coverage
+- https://github.com/nodejs/corepack/blob/main/README.md
+- https://prettier.io/docs/integrating-with-linters
+- https://registry.npmjs.org/-/package/typescript/dist-tags
+- https://registry.npmjs.org/-/package/prisma/dist-tags
+- https://registry.npmjs.org/-/package/@prisma/client/dist-tags
+- https://registry.npmjs.org/-/package/typescript-eslint/dist-tags
+- https://registry.npmjs.org/-/package/dependency-cruiser/dist-tags
diff --git a/skill-templates/nextjs/SKILL.md b/skill-templates/nextjs/SKILL.md
index b2d6b0e..c0f056b 100644
--- a/skill-templates/nextjs/SKILL.md
+++ b/skill-templates/nextjs/SKILL.md
@@ -127,6 +127,363 @@ Server Component (fetches data) → passes data as props → Client Component (r
 - Use Playwright for E2E testing; run against a real or preview deployment.
 - Write a minimum of one accessibility test per page using `jest-axe` or Playwright's built-in a11y snapshot.
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+### Strict Baseline
+
+### Required Toolchain
+| Tool | Purpose | Minimum version | Activate |
+| --- | --- | --- | --- |
+| Next.js | framework / `next build` gate | 16.3.5 | `pnpm add next@^16.3.5 react@latest react-dom@latest` |
+| React | runtime (App Router uses React 19.2 canary) | 19.2 | pulled by `next@16` |
+| TypeScript | type-check (`tsc --noEmit`) | 6.0.2 (JS API) / 7.0.2 (native) | `pnpm add -D typescript@^6.0.2` (TS 7 alias in config below) |
+| ESLint | lint engine (flat config only in v10; pin 9 for jsx-a11y) | 9.39.5 | `pnpm add -D eslint@^9.39.5` |
+| typescript-eslint | `strictTypeChecked` + `stylisticTypeChecked` | 8.70.1 | `pnpm add -D typescript-eslint@^8.70.1` |
+| @next/eslint-plugin-next | Next.js rules + core-web-vitals (use plugin directly, not `eslint-config-next`) | 16.3.5 | `pnpm add -D @next/eslint-plugin-next@^16.3.5` |
+| eslint-plugin-react-hooks | Rules of Hooks + React Compiler diagnostics | 7.1.1 | `pnpm add -D eslint-plugin-react-hooks@^7.1.1` |
+| eslint-plugin-jsx-a11y | strict a11y rules | 6.10.2 | `pnpm add -D eslint-plugin-jsx-a11y@^6.10.2` |
+| eslint-plugin-tailwindcss | unknown/contradicting Tailwind classes | 4.4.0 | `pnpm add -D eslint-plugin-tailwindcss@^4.4.0` |
+| eslint-config-prettier | disable formatting rules that fight Prettier | 10.x | `pnpm add -D eslint-config-prettier@latest` |
+| Prettier | formatter (`--check` gate) | 3.x | `pnpm add -D prettier@latest` |
+| prettier-plugin-tailwindcss | class sorting + duplicate removal | 0.8.1 | `pnpm add -D prettier-plugin-tailwindcss@^0.8.1` |
+| babel-plugin-react-compiler | React Compiler build-time memoization | 1.0.0 | `pnpm add -D babel-plugin-react-compiler@1.0.0` |
+| server-only | hard block on server-only imports in client bundles | 0.0.1 | `pnpm add server-only` |
+| size-limit + @size-limit/file | hard bundle-size budget | 14.0.0 | `pnpm add -D size-limit@^14.0.0 @size-limit/file@^14.0.0` |
+| @next/bundle-analyzer | Webpack bundle analysis (Turbopack uses `next experimental-analyze`) | 16.3.5 | `pnpm add -D @next/bundle-analyzer@^16.3.5` |
+| Vitest + @vitest/coverage-v8 | unit tests + coverage thresholds | 5.0.1 | `pnpm add -D vitest@^5.0.1 @vitest/coverage-v8@^5.0.1` |
+| @testing-library/react | component tests | 16.3.3 | `pnpm add -D @testing-library/react@^16.3.3 @testing-library/jest-dom@latest jsdom@latest` |
+| @playwright/test | end-to-end | 1.63.0 | `pnpm add -D @playwright/test@^1.63.0` |
+| @axe-core/playwright | automated WCAG checks in E2E | 4.13.0 | `pnpm add -D @axe-core/playwright@^4.13.0` |
+| knip | unused files / exports / dependencies | 6.37.0 | `pnpm add -D knip@^6.37.0` |
+| depcheck | unused-dependency cross-check (redundant with Knip) | 1.4.7 | optional: `pnpm add -D depcheck@^1.4.7` |
+| madge | circular-dependency detection | 8.0.0 | `pnpm add -D madge@^8.0.0` |
+| lockfile-lint | lockfile poisoning / non-HTTPS / rogue hosts | 5.0.1 | `pnpm add -D lockfile-lint@^5.0.1` |
+| osv-scanner | known-vulnerability scan (OSV database) | 2.x | binary / `go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest` |
+| Node.js | runtime floor (Next 16 needs ≥20.9; Knip & Tailwind plugin need ≥20.19) | 22.18.0 LTS | `.nvmrc` + `engines` + `.npmrc engine-strict=true` |
+
+> **Compatibility notes (2025–2026).** `next lint` was **removed in Next.js 16** and `next build` **no longer runs linting**; run ESLint (or Biome) directly. Migrate with `npx @next/codemod@canary next-lint-to-eslint-cli .`. `eslint-config-next@16` peer-accepts ESLint ≥9, but it depends on `eslint-plugin-jsx-a11y@^6`, whose peer range stops at `^9` — so installing the **strict a11y set on ESLint 10 fails (`ERESOLVE`)**. Pin ESLint 9.39.x until jsx-a11y ships an ESLint 10 release, and consume `@next/eslint-plugin-next` directly. `eslint-plugin-react-compiler` is **obsolete** (compiler rules now ship in `eslint-plugin-react-hooks@≥6`). `depcheck` is retained only as an optional cross-check; **Knip supersedes it** (files + exports + deps). TS 7.0 has no JS compiler API, so type-aware linting needs the `typescript@6` alias (documented below).
+
+### Strict Baseline Config
+
+**`tsconfig.json` — every strict flag + Next 16 requirements** (TS 6/7 already default `strict: true`; the extras below are what Next's generated config omits):
+
+```jsonc
+{
+  "compilerOptions": {
+    /* strict family — full set */
+    "strict": true,
+    "noUncheckedIndexedAccess": true,
+    "exactOptionalPropertyTypes": true,
+    "noImplicitOverride": true,
+    "noImplicitReturns": true,
+    "noFallthroughCasesInSwitch": true,
+    "noUnusedLocals": true,
+    "noUnusedParameters": true,
+    "noPropertyAccessFromIndexSignature": true,
+    "allowUnreachableCode": false,
+    "allowUnusedLabels": false,
+    "useUnknownInCatchVariables": true,
+    "strictBuiltinIteratorReturn": true,
+
+    /* module / interop — bundler-grade strictness */
+    "verbatimModuleSyntax": true,
+    "isolatedModules": true,
+    "erasableSyntaxOnly": true,
+    "noUncheckedSideEffectImports": true,
+    "forceConsistentCasingInFileNames": true,
+    "moduleDetection": "force",
+    "module": "esnext",
+    "moduleResolution": "bundler",
+    "target": "ES2022",
+    "lib": ["dom", "dom.iterable", "esnext"],
+
+    /* Next.js requirements */
+    "jsx": "preserve",
+    "noEmit": true,
+    "incremental": true,
+    "skipLibCheck": true,
+    "plugins": [{ "name": "next" }],
+    "paths": { "@/*": ["./*"] }
+  },
+  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
+  "exclude": ["node_modules"]
+}
+```
+
+**`package.json` — TypeScript 7 (fast native `tsc`) alongside the TS 6 API that typescript-eslint requires** (from the official TS 7 announcement; use the simpler `"typescript": "^6.0.2"` if you don't need 7's speed):
+
+```json
+{
+  "devDependencies": {
+    "@typescript/native": "npm:typescript@^7.0.2",
+    "typescript": "npm:@typescript/typescript6@^6.0.2"
+  }
+}
+```
+
+**`eslint.config.mjs` — flat config, strictTypeChecked + strict a11y + compiler diagnostics:**
+
+```js
+// eslint.config.mjs
+import { defineConfig, globalIgnores } from 'eslint/config'
+import tseslint from 'typescript-eslint'
+import reactHooks from 'eslint-plugin-react-hooks'
+import jsxA11y from 'eslint-plugin-jsx-a11y'
+import next from '@next/eslint-plugin-next'
+import tailwind from 'eslint-plugin-tailwindcss'
+import prettier from 'eslint-config-prettier/flat'
+
+export default defineConfig(
+  globalIgnores(['.next/**', 'out/**', 'build/**', 'coverage/**', 'next-env.d.ts']),
+
+  // 1. Type-aware TypeScript — strictest preset, uses real type info
+  {
+    files: ['**/*.{ts,tsx,mjs}'],
+    extends: [
+      ...tseslint.configs.strictTypeChecked,
+      ...tseslint.configs.stylisticTypeChecked,
+    ],
+    languageOptions: {
+      parserOptions: {
+        projectService: true,                 // auto-discovers tsconfig.json
+        tsconfigRootDir: import.meta.dirname,
+      },
+    },
+    rules: {
+      '@typescript-eslint/no-explicit-any': 'error',
+      '@typescript-eslint/ban-ts-comment': [
+        'error',
+        { 'ts-expect-error': 'allow-with-description', minimumDescriptionLength: 10 },
+      ],
+    },
+  },
+
+  // 2. React / Next / a11y / Tailwind — all as ERRORS
+  {
+    files: ['**/*.{jsx,tsx}'],
+    extends: [
+      jsxA11y.flatConfigs.strict,
+      tailwind.configs['flat/recommended'],
+    ],
+    plugins: { 'react-hooks': reactHooks, '@next/next': next },
+    rules: {
+      // React compiler-powered diagnostics (recommended-latest enables the full set)
+      ...reactHooks.configs.flat['recommended-latest'].rules,
+      'react-hooks/exhaustive-deps': 'error',     // NEVER leave this at warn
+      'react-hooks/rules-of-hooks': 'error',
+      // Next.js rules + Core Web Vitals promoted to errors
+      ...next.configs.recommended.rules,
+      ...next.configs['core-web-vitals'].rules,
+      '@next/next/no-async-client-component': 'error',
+      // Tailwind: unknown / contradicting classes are errors; dedup is Prettier's job
+      'tailwindcss/no-custom-classname': 'error',
+      'tailwindcss/no-contradicting-classname': 'error',
+      'tailwindcss/enforces-shorthand': 'error',
+      'tailwindcss/no-unnecessary-arbitrary-value': 'error',
+    },
+    settings: {
+      tailwindcss: { cssConfigPath: './app/globals.css' }, // REQUIRED by the plugin
+    },
+  },
+
+  // 3. Formatting is Prettier's job
+  prettier,
+)
+```
+
+> `eslint-plugin-tailwindcss@4` requires the shared setting **`tailwindcss.cssConfigPath`** (your Tailwind v4 CSS entry, e.g. `app/globals.css`). Rule names dropped by v4 (e.g. old `classnames-order`) are replaced; run `npx eslint --print-config src/app/page.tsx` if a rule name is rejected.
+
+**`.prettierrc` — class sorting; plugin MUST be last; duplicates removed by default:**
+
+```json
+{
+  "plugins": ["prettier-plugin-tailwindcss"],
+  "tailwindStylesheet": "./app/globals.css",
+  "tailwindFunctions": ["cn", "cva", "clsx", "twMerge"],
+  "tailwindPreserveDuplicates": false
+}
+```
+
+**Tailwind v4 content config (CSS-first; no `tailwind.config.js` needed):**
+
+```css
+/* app/globals.css */
+@import "tailwindcss";
+@source "../app/**/*.{ts,tsx}";
+@source "../components/**/*.{ts,tsx}";
+@theme { /* design tokens */ }
+```
+
+**`next.config.ts` — React Compiler + no type/lint escape hatches:**
+
+```ts
+import type { NextConfig } from 'next'
+
+const nextConfig: NextConfig = {
+  reactCompiler: true,          // stable in Next 16; requires babel-plugin-react-compiler
+  cacheComponents: true,        // opt-in PPR/use cache model (replaces experimental.ppr)
+  eslint: { ignoreDuringBuilds: false },          // must never be true
+  typescript: { ignoreBuildErrors: false },       // must never be true
+}
+
+export default nextConfig
+```
+
+**`size-limit` budget (Next 16 removed `First Load JS` from build output, so budget it explicitly) — `.size-limit.json`:**
+
+```json
+[
+  {
+    "name": "next-client-chunks",
+    "path": ".next/static/chunks/**/*.js",
+    "limit": "200 kB"
+  }
+]
+```
+
+**`vitest.config.ts` — coverage thresholds (positive = minimum %, negative = max uncovered):**
+
+```ts
+import { defineConfig } from 'vitest/config'
+
+export default defineConfig({
+  test: {
+    environment: 'jsdom',
+    coverage: {
+      provider: 'v8',
+      reporter: ['text', 'lcov'],
+      include: ['app/**', 'components/**', 'lib/**'],
+      exclude: ['**/*.test.*', '**/*.spec.*', '**/*.d.ts'],
+      thresholds: {
+        statements: 90,
+        branches: 85,
+        functions: 90,
+        lines: 90,
+        perFile: true,
+      },
+    },
+  },
+})
+```
+
+**`knip.json` — dead files / exports / dependencies:**
+
+```json
+{
+  "$schema": "https://unpkg.com/knip@6/schema.json",
+  "entry": ["app/**/{page,layout,route,error,loading,not-found}.{ts,tsx}", "proxy.ts", "next.config.ts", "playwright.config.ts"],
+  "project": ["**/*.{ts,tsx}"],
+  "ignore": ["**/*.d.ts"],
+  "ignoreDependencies": ["@types/*"]
+}
+```
+
+**`playwright` a11y fixture — WCAG 2.1 A/AA as a hard failure:**
+
+```ts
+// tests/axe-test.ts
+import { test as base } from '@playwright/test'
+import AxeBuilder from '@axe-core/playwright'
+
+export const test = base.extend<{ makeAxeBuilder: () => AxeBuilder }>({
+  makeAxeBuilder: async ({ page }, use) => {
+    await use(() =>
+      new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']),
+    )
+  },
+})
+export { expect } from '@playwright/test'
+```
+
+**Node pinning — `.nvmrc` + `package.json` + `.npmrc`:**
+
+```
+22.18.0
+```
+
+```json
+{ "engines": { "node": ">=22.18.0 <23" }, "packageManager": "pnpm@10.0.0" }
+```
+
+```
+# .npmrc
+engine-strict=true
+```
+
+### Mandatory Gate Order
+1. `npx tsc --noEmit`
+2. `npx eslint . --max-warnings=0`
+3. `npx prettier --check .`
+4. `npx knip`
+5. `npx madge --circular --extensions ts,tsx app`
+6. `npx vitest run --coverage`
+7. `npx next build`
+8. `npx size-limit`
+9. `npx playwright test`
+10. `pnpm exec lockfile-lint --path pnpm-lock.yaml --type pnpm --allowed-hosts npm --validate-https`
+11. `osv-scanner scan source -r . --licenses`
+
+> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI.
+
+### Hallucination Traps to Block
+- Invented/deprecated Next.js APIs and sync `params`/`searchParams`/`cookies()` -> `tsc --noEmit` against Next 16 async request APIs (`await props.params`) + generated `PageProps<'/route'>` / `LayoutProps<'/route'>` / `RouteContext` types from `next typegen`.
+- `useState`/`useEffect`/event handlers used without a `'use client'` boundary, or an `async` Client Component -> `next build` (hard error) + `@next/next/no-async-client-component`.
+- Server-only module (DB client, secrets) imported into a Client Component -> `import 'server-only'` (build-time throw) + Next `taint` API (`experimental.taint`) for sensitive values.
+- Suppressing type errors with `any`, `as`, or `@ts-ignore` -> `@typescript-eslint/no-explicit-any` + the `no-unsafe-*` rules from `strictTypeChecked` + `ban-ts-comment` (description required).
+- Stale closures / missing effect deps / setState-in-effect / ref reads during render -> `react-hooks/exhaustive-deps` (error), `react-hooks/set-state-in-effect`, `react-hooks/refs`, `react-hooks/purity`.
+- Illegal render-time mutation or broken manual memoization -> `react-hooks/immutability`, `react-hooks/preserve-manual-memoization`, `react-hooks/set-state-in-render`.
+- Non-existent, duplicate, or contradicting Tailwind utilities -> `tailwindcss/no-custom-classname`, `tailwindcss/no-contradicting-classname`; duplicates stripped by `prettier-plugin-tailwindcss` (`preserveDuplicates: false`).
+- Bloat from a newly added dependency -> `size-limit` (hard kB budget over `.next/static/chunks/**/*.js`).
+- Circular imports that crash only at runtime -> `madge --circular`.
+- Dead files / unused exports / unused dependencies -> `knip`.
+- Lockfile-poisoned or vulnerable dependencies -> `lockfile-lint` + `osv-scanner`.
+- Inaccessible UI (unlabeled controls, `div` with `onClick`, missing `alt`) -> `jsx-a11y` strict + `@axe-core/playwright` (`violations` must equal `[]`).
+
+### Evidence to Record
+Paste the raw output of each gate and the exact command that produced it:
+- `npx tsc --noEmit` — exit code `0`, no diagnostics.
+- `npx eslint . --max-warnings=0` — exit code `0`; "0 problems" (warnings are failures).
+- `npx prettier --check .` — "All matched files use Prettier code style!".
+- `npx knip` — exit code `0`; no unused files/exports/dependencies reported.
+- `npx madge --circular --extensions ts,tsx app` — exit code `0`, no cycles (madge exits non-zero when a cycle exists).
+- `npx vitest run --coverage` — all tests pass and coverage meets/exceeds `statements 90 / branches 85 / functions 90 / lines 90` (per-file).
+- `npx next build` — "Compiled successfully"; zero errors/warnings; `typescript.ignoreBuildErrors` and `eslint.ignoreDuringBuilds` are `false`.
+- `npx size-limit` — every entry under its `limit` (e.g. ≤ `200 kB` Brotli).
+- `npx playwright test` — all pass; axe scan asserts `accessibilityScanResults.violations` `toEqual([])`; visual snapshots match within `maxDiffPixelRatio: 0.01`.
+- `npx lockfile-lint ...` — no output ("file passes").
+- `osv-scanner scan source -r . --licenses` — no vulnerabilities at/above the agreed severity threshold.
+
+<!-- sources -->
+- https://nextjs.org/docs/app/api-reference/config/eslint
+- https://nextjs.org/docs/app/guides/upgrading/version-16
+- https://nextjs.org/blog/next-16
+- https://nextjs.org/docs/app/api-reference/config/typescript
+- https://nextjs.org/docs/app/guides/package-bundling
+- https://nextjs.org/docs/app/guides/production-checklist
+- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
+- https://www.typescriptlang.org/tsconfig/
+- https://typescript-eslint.io/users/configs/
+- https://react.dev/blog/2025/10/07/react-compiler-1
+- https://react.dev/reference/eslint-plugin-react-hooks
+- https://raw.githubusercontent.com/facebook/react/main/packages/eslint-plugin-react-hooks/README.md
+- https://github.com/jsx-eslint/eslint-plugin-jsx-a11y
+- https://registry.npmjs.org/eslint-plugin-jsx-a11y/latest
+- https://registry.npmjs.org/eslint-config-next/16.3.3
+- https://chris.lu/web_development/tutorials/next-js-16-linting-setup-eslint-10-flat-config
+- https://github.com/francoismassart/eslint-plugin-tailwindcss
+- https://github.com/tailwindlabs/prettier-plugin-tailwindcss
+- https://knip.dev/overview/getting-started
+- https://knip.dev/overview/configuration
+- https://github.com/ai/size-limit
+- https://playwright.dev/docs/accessibility-testing
+- https://vitest.dev/config/coverage
+- https://github.com/google/osv-scanner
+- https://github.com/lirantal/lockfile-lint
+- https://github.com/pahen/madge
+
 ## Currency Baseline
 
 - **No default cache (Next 15+):** `fetch`, `GET` route handlers, and client navigations are not cached unless opted in (`cache: 'force-cache'`, `revalidate`, or a `fetchCache` segment config). Never assume caching by default.
diff --git a/skill-templates/node-hexagonal-api/SKILL.md b/skill-templates/node-hexagonal-api/SKILL.md
index 492b47c..6f052e1 100644
--- a/skill-templates/node-hexagonal-api/SKILL.md
+++ b/skill-templates/node-hexagonal-api/SKILL.md
@@ -69,6 +69,377 @@ project-root/
 - Write table-driven (`it.each`) tests for all use cases against faked outbound ports.
 - Inbound HTTP routes tested via supertest-style injection with the real container and faked repositories.
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+### Strict Baseline
+
+> Target: Node.js + TypeScript backend organized as Hexagonal Architecture (Ports and Adapters).
+> All versions verified live against the npm registry / project release pages in 2025-2026. Pinned
+> to the **strictest maintained** tool for each role. Deprecated or dormant tools are called out
+> explicitly and excluded from the mandatory chain.
+
+### Required Toolchain
+
+| Tool | Purpose | Minimum version | Activate |
+| --- | --- | --- | --- |
+| Node.js | Runtime; LTS only | 24.0.0 (24.x Active LTS "Krypton") | `.nvmrc` → `24` ; `package.json` → `"engines": { "node": ">=24.0.0" }` |
+| TypeScript | `tsc --noEmit` type gate + parser backend for typed lint | 6.0.3 | `npm i -D typescript@6.0.3` |
+| @typescript/native-preview (optional) | TS7 `tsgo` fast type-check *alongside* TS6; TS7 has no programmatic API yet so typed-lint tools cannot use it | 7.0.2 | `npm i -D @typescript/native-preview@^7` (run via `tsgo --noEmit` only) |
+| ESLint | Core linter, flat config only (eslintrc deleted in v10) | 10.0.0 (10.4.x) | `npm i -D eslint@^10 @eslint/js@^10` |
+| typescript-eslint | Type-aware rule engine (`strictTypeChecked`, `stylisticTypeChecked`) | 8.70.1 | `npm i -D typescript-eslint@^8` |
+| eslint-plugin-n | Node correctness (`no-process-exit`, `no-missing-import`, deprecation) | 18.2.2 | `npm i -D eslint-plugin-n@^18` |
+| dependency-cruiser | **Primary** architectural boundary + cycle enforcement on the real resolved graph | 18.4.0 | `npm i -D dependency-cruiser@^18.4` |
+| eslint-plugin-boundaries | Secondary, in-editor boundary feedback (import-time, entity model v7) | 7.2.0 | `npm i -D eslint-plugin-boundaries@^7` |
+| eslint-plugin-import-x (optional) | Fast per-file `no-restricted-paths` guard; maintained fork (ESLint 10 ready) | 4.16.2 | `npm i -D eslint-plugin-import-x@^4` |
+| Vitest + @vitest/coverage-v8 | Unit / contract / property runner with fail-on-threshold coverage | 4.1.9 | `npm i -D vitest@^4 @vitest/coverage-v8@^4` |
+| testcontainers | Real infra in contract tests (Postgres, Redis, broker) | 12.1.0 | `npm i -D testcontainers@^12` |
+| fast-check | Property-based tests for core invariants | 4.9.0 | `npm i -D fast-check@^4` |
+| tsd | Type-level tests (`expectType` / `expectError`) | 0.33.0 | `npm i -D tsd@^0.33` |
+| @microsoft/api-extractor | Public API surface + declaration-diff gate | 7.59.1 | `npm i -D @microsoft/api-extractor@^7` |
+| publint | Package `exports` / publish-metadata gate | 0.3.24 | `npm i -D publint@^0.3` |
+| @arethetypeswrong/cli | Consumer-side `.d.ts` / module-resolution gate | 0.18.5 | `npm i -D @arethetypeswrong/cli@^0.18` |
+| knip | Unused files, exports, and dependencies | 6.4.1 | `npm i -D knip@^6` |
+| lockfile-lint | Lockfile host/integrity policy (anti-typosquat/injection) | 5.0.1 | `npm i -D lockfile-lint@^5` |
+| osv-scanner | Vulnerability scan against OSV (replaces/augments `npm audit`) | 2.5.1 | `go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest` or the official GH Action / binary |
+| zod (or valibot) | Strict boot-time environment schema | 4.5.4 (valibot 1.4.2) | `npm i zod@^4` |
+
+**Discarded / demoted (say so, do not silently use):**
+- **madge** — cycle/graph tool, but last npm release is **8.0.0, Aug 2024** (dormant ~2 years, download trend falling). Its only irreplaceable role, cycle detection, is already covered by dependency-cruiser's `no-circular` rule (actively maintained, minimum 18.4.0 — the `$1` backreference used below was validated on 18.4). Keep madge only for one-off visual graphs, never as a gate.
+- **depcheck** — superseded by **knip** (knip covers files + exports + dependencies and is actively maintained; depcheck 1.4.7 last shipped Aug 2025 and is narrower).
+- **eslint-plugin-import** — effectively frozen/refuses `exports`/specifier support; the maintained successor is **eslint-plugin-import-x**, which declares ESLint `^8.57 || ^9 || ^10`.
+- **TypeScript 7.x as the typed-linting backend** — 7.0.2 is npm `latest`, but `typescript-eslint` supports only `>=4.8.4 <6.1.0`; pointing `typescript` at 7 makes typed lint crash (`ts.Extension.Cjs` undefined). Pin `typescript@6.0.3` for lint; run TS7 side-by-side via `tsgo` for speed only.
+
+### Strict Baseline Config
+
+`tsconfig.json` — every strict flag, `tsc --noEmit` is the gate:
+
+```jsonc
+{
+  "compilerOptions": {
+    "target": "es2024",
+    "lib": ["es2024"],
+    "module": "nodenext",
+    "moduleResolution": "nodenext",
+    "moduleDetection": "force",
+    "types": ["node"],
+    "rootDir": "./src",
+    "outDir": "./dist",
+
+    /* maximum static strictness */
+    "strict": true,
+    "noUncheckedIndexedAccess": true,
+    "exactOptionalPropertyTypes": true,
+    "noImplicitOverride": true,
+    "noImplicitReturns": true,
+    "noFallthroughCasesInSwitch": true,
+    "noImplicitThis": true,
+    "useUnknownInCatchVariables": true,
+    "noPropertyAccessFromIndexSignature": true,
+    "noUnusedLocals": true,
+    "noUnusedParameters": true,
+    "allowUnreachableCode": false,
+    "allowUnusedLabels": false,
+    "forceConsistentCasingInFileNames": true,
+
+    /* module purity */
+    "verbatimModuleSyntax": true,
+    "isolatedModules": true,
+    "noUncheckedSideEffectImports": true,
+    "erasableSyntaxOnly": true,
+
+    /* emit for libs; keep type-check honest */
+    "declaration": true,
+    "declarationMap": true,
+    "sourceMap": true,
+    "skipLibCheck": false
+  },
+  "include": ["src"],
+  "exclude": ["dist", "node_modules"]
+}
+```
+
+`eslint.config.mjs` — ESLint 10 flat config, strictest type-checked presets:
+
+```js
+// @ts-check
+import js from '@eslint/js';
+import { defineConfig } from 'eslint/config';
+import tseslint from 'typescript-eslint';
+import node from 'eslint-plugin-n';
+
+export default defineConfig(
+  { ignores: ['dist/**', 'coverage/**', 'node_modules/**', '**/*.d.ts'] },
+
+  js.configs.recommended,
+
+  ...tseslint.configs.strictTypeChecked,
+  ...tseslint.configs.stylisticTypeChecked,
+
+  {
+    files: ['**/*.{ts,mts,cts}'],
+    languageOptions: {
+      parserOptions: {
+        projectService: true,               // typed linting; no tsconfig.eslint.json
+        tsconfigRootDir: import.meta.dirname,
+      },
+    },
+    rules: {
+      '@typescript-eslint/no-floating-promises': ['error', { ignoreVoid: false }],
+      '@typescript-eslint/no-misused-promises': ['error', {
+        checksConditionals: true,
+        checksSpreads: true,
+        checksVoidReturn: { arguments: true, attributes: false, returns: true },
+      }],
+      '@typescript-eslint/switch-exhaustiveness-check': ['error', {
+        considerDefaultExhaustiveForUnions: true,
+        requireDefaultForNonUnion: true,
+      }],
+      '@typescript-eslint/consistent-type-imports': ['error', { prefer: 'type-imports', fixStyle: 'inline-type-imports' }],
+      '@typescript-eslint/no-import-type-side-effects': 'error',
+      '@typescript-eslint/explicit-function-return-type': ['error', { allowExpressions: false }],
+      '@typescript-eslint/no-explicit-any': 'error',
+    },
+  },
+
+  node.configs["flat/recommended-module"],
+);
+```
+
+`.dependency-cruiser.cjs` — **the boundary gate** (copy-paste; layout `src/core`, `src/adapters`, `src/shared`, `src/composition`):
+
+```js
+/** @type {import('dependency-cruiser').IConfiguration} */
+module.exports = {
+  forbidden: [
+    {
+      name: 'no-circular',
+      severity: 'error',
+      comment: 'No dependency cycles anywhere.',
+      from: {},
+      to: { circular: true },
+    },
+    {
+      name: 'core-no-runtime-deps',
+      severity: 'error',
+      comment: 'domain+ports (the hexagon) must have ZERO npm runtime dependencies.',
+      from: { path: '^src/core/' },
+      to: { dependencyTypes: ['npm'], pathNot: '^src/core/' },
+    },
+    {
+      name: 'core-no-node-builtins',
+      severity: 'error',
+      comment: 'domain+ports must not touch Node builtins (fs/net/http/crypto).',
+      from: { path: '^src/core/' },
+      to: { dependencyTypes: ['core'] },
+    },
+    {
+      name: 'core-no-outward',
+      severity: 'error',
+      comment: 'core must never import adapters, shared infra, or the composition root.',
+      from: { path: '^src/core/' },
+      to: { path: '^src/(adapters|shared|composition)/' },
+    },
+    {
+      name: 'no-cross-adapter',
+      severity: 'error',
+      comment: 'adapters must not import each other; collaborate through core ports.',
+      from: { path: '^src/adapters/([^/]+)/' },
+      to: { path: '^src/adapters/([^/]+)/', pathNot: '^src/adapters/$1/' }, // $1 validated on 18.4
+    },
+    {
+      name: 'adapters-inward-only',
+      severity: 'error',
+      comment: 'adapters may import core/shared/their own folder only — never the composition root.',
+      from: { path: '^src/adapters/' },
+      to: { path: '^src/(?!core/|adapters/|shared/)' },
+    },
+    {
+      name: 'shared-no-outward',
+      severity: 'error',
+      comment: 'shared infra must not depend on core, adapters, or composition.',
+      from: { path: '^src/shared/' },
+      to: { path: '^src/(core|adapters|composition)/' },
+    },
+    {
+      name: 'no-orphans',
+      severity: 'error',
+      comment: 'unreferenced modules are dead code.',
+      from: { orphan: true, pathNot: ['\\.d\\.ts$', '\\.test\\.ts$', '\\.spec\\.ts$', '^src/composition/'] },
+      to: {},
+    },
+  ],
+  options: {
+    tsConfig: { fileName: 'tsconfig.json' },   // resolves tsconfig paths + aliases
+    tsPreCompilationDeps: true,
+    doNotFollow: { path: 'node_modules' },
+    enhancedResolveOptions: { exportsFields: ['exports'], conditionNames: ['import', 'require', 'node', 'default'] },
+    exclude: { path: ['\\.test\\.ts$', '\\.spec\\.ts$', '\\.config\\.(ts|js|mjs|cjs)$', '^dist/'] },
+    includeOnly: { path: '^src/' },
+  },
+};
+```
+
+`knip.json` — dead code / dependency hygiene:
+
+```jsonc
+{
+  "$schema": "https://unpkg.com/knip@6/schema.json",
+  "entry": ["src/composition/main.ts"],
+  "project": ["src/**/*.ts", "!src/**/*.test.ts", "!src/**/*.spec.ts"],
+  "ignoreExportsUsedInFile": true
+}
+```
+
+`vitest.config.ts` — coverage thresholds are the gate (Vitest 4 requires `coverage.include`; `coverage.all` was removed):
+
+```ts
+import { defineConfig } from 'vitest/config';
+
+export default defineConfig({
+  test: {
+    environment: 'node',
+    include: ['src/**/*.test.ts', 'test/**/*.test.ts'],
+    coverage: {
+      provider: 'v8',
+      reporter: ['text', 'json-summary'],
+      include: ['src/core/**/*.ts', 'src/adapters/**/*.ts'],
+      thresholds: {
+        lines: 100,
+        functions: 100,
+        branches: 100,
+        statements: 100,
+        perFile: true,                         // every file, not just aggregate
+        'src/core/**': { branches: 100, functions: 100, lines: 100, statements: 100 }, // the hexagon is fully covered
+      },
+    },
+  },
+});
+```
+
+Boot-time env schema (fails the process before the server listens; unit-tested):
+
+```ts
+// src/composition/config.ts
+import { z } from 'zod';
+
+const Env = z.object({
+  NODE_ENV: z.enum(['development', 'test', 'production']),
+  PORT: z.coerce.number().int().positive(),
+  DATABASE_URL: z.string().url(),
+});
+
+export type Config = z.infer<typeof Env>;
+export const loadConfig = (env: NodeJS.ProcessEnv = process.env): Config => Env.parse(env);
+```
+
+`package.json` scripts — the single gate chain:
+
+```jsonc
+{
+  "type": "module",
+  "engines": { "node": ">=24.0.0" },
+  "scripts": {
+    "verify": "npm run typecheck && npm run lint && npm run arch && npm run deadcode && npm run test && npm run types && npm run package"
+  }
+}
+```
+
+### Mandatory Gate Order
+
+1. `npm ci --ignore-scripts`  *(npm 12 already blocks dependency install scripts; `--ignore-scripts` makes it explicit and works on npm 11)*
+2. `npx lockfile-lint --path package-lock.json --type npm --allowed-hosts npm --validate-https`
+3. `osv-scanner scan source -r . --licenses`
+4. `npx tsc --noEmit`
+5. `npx eslint . --max-warnings=0`
+6. `npx depcruise src --config .dependency-cruiser.cjs`
+7. `npx knip --production`
+8. `npx vitest run --coverage`
+9. `npx tsd`
+10. `npx publint && npx attw --pack .`  *(only when the package is published)*
+11. `npx api-extractor run --local`  *(only when a `.api.md` surface is maintained)*
+
+> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI.
+> (`eslint` is invoked WITHOUT `--fix`; `--max-warnings=0` makes any warning fatal.)
+
+### Hallucination Traps to Block
+
+- Domain/core importing an ORM or web framework (Prisma, TypeORM, Express, NestJS) → `dependency-cruiser` `core-no-runtime-deps` (blocks every `dependencyTypes: ["npm"]` edge into `src/core/`).
+- Adapter A importing adapter B directly instead of via a port → `dependency-cruiser` `no-cross-adapter` group-capture rule (`$1` matching).
+- Floating / unawaited promise in an async handler silently swallowing failures → `@typescript-eslint/no-floating-promises`.
+- Async function passed where a `void`-returning callback is expected (event emitters, `setTimeout`, `forEach`) → `@typescript-eslint/no-misused-promises` (`checksVoidReturn`).
+- New union member added but a `switch` not updated → `@typescript-eslint/switch-exhaustiveness-check` (`requireDefaultForNonUnion`).
+- `process.exit()` bypassing graceful shutdown (in-flight requests dropped) → `eslint-plugin-n` `n/no-process-exit`.
+- Reading `process.env.X` directly (unvalidated/possibly `undefined`) → `zod`/`valibot` boot schema + `noPropertyAccessFromIndexSignature` + `noUncheckedIndexedAccess` + `useUnknownInCatchVariables`.
+- Dead adapter / unused export left behind after a refactor → `knip` (files, exports, dependencies).
+- `any` leaking through `catch` or library boundaries → `strictTypeChecked` (`no-unsafe-*`) + `@typescript-eslint/no-explicit-any`.
+- Broken `exports`/`.d.ts` for consumers despite green local tests → `publint` + `@arethetypeswrong/cli`.
+- Supply-chain code execution at install time (Shai-Hulud-class) → `npm ci --ignore-scripts` + `lockfile-lint` + `osv-scanner`.
+
+### Evidence to Record
+
+Paste the exact command and its pass signal into Verification Evidence; all must exit `0`.
+
+- `npx tsc --noEmit` → exit `0`, no output.
+- `npx eslint . --max-warnings=0` → exit `0`, summary `0 problems`.
+- `npx depcruise src --config .dependency-cruiser.cjs` → exit `0`, output `no dependency violations found`.
+- `npx knip --production` → exit `0`, no unused files/exports/dependencies listed.
+- `npx vitest run --coverage` → exit `0`, every threshold line reports `>= 100` and `Test Files` all passed.
+- `npx tsd` → exit `0`, no type assertion failures.
+- `npx publint && npx attw --pack .` → exit `0` (publint: no errors; attw: all resolution modes `🟢`).
+- `npx lockfile-lint ... && osv-scanner scan source -r . --licenses` → exit `0`, no `allowed-hosts` violations and **no HIGH/CRITICAL** advisories.
+- Unit-only core test proof: `npx vitest run src/core` exits `0` with no `testcontainers`/network started (core has no I/O).
+- Env failure proof: `node -e "import('./dist/composition/config.js').then(m=>m.loadConfig({}))" ; test $? -ne 0` (missing vars must throw, not boot).
+
+<!-- sources -->
+- https://typescript-eslint.io/users/configs/
+- https://typescript-eslint.io/getting-started/typed-linting
+- https://typescript-eslint.io/users/dependency-versions/
+- https://github.com/typescript-eslint/typescript-eslint/issues/12518
+- https://eslint.org/blog/2026/02/eslint-v10.0.0-released/
+- https://eslint.org/docs/latest/use/migrate-to-10.0.0
+- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html
+- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html
+- https://registry.npmjs.org/-/package/typescript/dist-tags
+- https://github.com/eslint-community/eslint-plugin-n
+- https://github.com/sverweij/dependency-cruiser
+- https://github.com/sverweij/dependency-cruiser/blob/HEAD/doc/rules-reference.md
+- https://github.com/sverweij/dependency-cruiser/blob/HEAD/doc/options-reference.md
+- https://github.com/javierbrea/eslint-plugin-boundaries
+- https://github.com/javierbrea/eslint-plugin-boundaries/releases/tag/v7.0.0
+- https://github.com/un-ts/eslint-plugin-import-x
+- https://github.com/un-ts/eslint-plugin-import-x/blob/master/docs/rules/no-restricted-paths.md
+- https://vitest.dev/config/coverage
+- https://vitest.dev/guide/migration/
+- https://github.com/testcontainers/testcontainers-node/releases
+- https://fast-check.dev/
+- https://knip.dev/reference/configuration
+- https://knip.dev/guides/configuring-project-files
+- https://github.com/lirantal/lockfile-lint
+- https://google.github.io/osv-scanner/supported-languages-and-lockfiles/
+- https://github.com/google/osv-scanner/releases
+- https://github.com/tsdjs/tsd
+- https://www.npmjs.com/package/@microsoft/api-extractor
+- https://www.pkgpulse.com/guides/publint-vs-arethetypeswrong-vs-knip-2026
+- https://www.pkgpulse.com/guides/publint-vs-arethetypeswrong-vs-pkg-pr-new-package-quality-2026
+- https://www.npmjs.com/package/dependency-cruiser
+- https://www.npmjs.com/package/eslint-plugin-boundaries
+- https://www.npmjs.com/package/eslint-plugin-n
+- https://www.npmjs.com/package/madge
+- https://www.npmjs.com/package/depcheck
+- https://www.npmjs.com/package/lockfile-lint
+- https://www.npmjs.com/package/zod
+- https://www.npmjs.com/package/valibot
+- https://www.npmjs.com/package/knip
+- https://cve.optibot.re/blog/nodejs-24-lts-security-guide-2026
+- https://github.com/nodejs/Release/issues/1161
+- https://www.michal-drozd.com/en/blog/architectural-linting/
+- https://github.com/fusic-toybox/architecture-as-steering
+- https://docs.synapsestudios.com/implementation/frameworks/nest/dependency-cruiser-config
+- https://github.com/zpratt/lousy-agents/blob/main/.dependency-cruiser.cjs
+
 ## Currency Baseline
 
 - **Runtime:** Node 22 LTS. **Package manager:** `pnpm` (fallback `npm`). **Validation:** `zod`. **ORM:** `prisma` (migrations via `prisma migrate`, never `db push` on shared DBs).
diff --git a/skill-templates/python-fastapi/SKILL.md b/skill-templates/python-fastapi/SKILL.md
index 410a6ad..a170669 100644
--- a/skill-templates/python-fastapi/SKILL.md
+++ b/skill-templates/python-fastapi/SKILL.md
@@ -63,6 +63,297 @@ Ported from the Go blueprint (`go-hexagonal-grpc`). Same rules, Python idioms:
 | Service      | Unit        | Pytest                     | `test_user_service.py` |
 | Route / View | Integration | Pytest + httpx AsyncClient | `test_users.py`        |
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+> Scope: FastAPI + Pydantic V2, async-first, hexagonal ports/adapters, `Clock` abstraction,
+> timezone-aware datetimes (the stack already mandated by `skill-templates/python-fastapi/SKILL.md`).
+> All versions verified **2026-09** against PyPI JSON and GitHub Releases API; Python target is **3.14**
+> (3.14.7 current stable; 3.15.0 final lands Oct 2026 — do NOT pin 3.15 yet).
+
+## Required Toolchain
+
+| Tool                                       | Purpose                                          | Minimum version to pin | Install / availability note                                    |
+| ------------------------------------------ | ------------------------------------------------ | ---------------------- | -------------------------------------------------------------- |
+| `python`                                   | Runtime + toolchain pin                          | **3.14.7**             | `.python-version` = `3.14`; `requires-python = ">=3.14"`       |
+| `uv`                                       | Env, lockfile, build, native audit               | **0.12.17**            | standalone installer (`astral.sh/uv`); `uv self update`        |
+| `ruff`                                     | Format + lint + import sort + bandit subset      | **0.16.8**             | `uv add --dev ruff==0.16.8` (single binary, 900+ rules)        |
+| `basedpyright`                             | Primary strict type checker                      | **1.40.1**             | `uv add --dev basedpyright==1.40.1` (PyPI wrapper, no Node)    |
+| `mypy`                                     | Secondary checker (Pydantic plugin support)      | **2.3.1**              | `uv add --dev mypy==2.3.1`                                     |
+| `semgrep`                                  | SAST / security scanning (cross-file)            | **1.177.0**            | `uv add --dev semgrep==1.177.0` (or `uvx semgrep`)             |
+| `pip-audit`                                | Vulnerability audit fallback                     | **2.10.1**             | `uvx pip-audit` (only when `uv audit` unavailable)             |
+| `deptry`                                   | Unused / missing / transitive dependency hygiene | **0.25.1**             | `uv add --dev deptry==0.25.1` (org moved to `osprey-oss`)      |
+| `vulture`                                  | Dead-code detection                              | **2.16**               | `uv add --dev vulture==2.16`                                   |
+| `import-linter`                            | Architecture / import-boundary enforcement       | **2.15**               | `uv add --dev import-linter==2.15`                             |
+| `pytest`                                   | Test runner                                      | **9.1.1**              | `uv add --dev pytest==9.1.1`                                   |
+| `pytest-cov` / `coverage`                  | Coverage + threshold gate                        | **7.1.0 / 7.16.1**     | `uv add --dev pytest-cov==7.1.0`                               |
+| `pytest-randomly` / `pytest-xdist`         | Order shuffling + parallel flake surfacing       | **5.0.0 / 3.8.0**      | `uv add --dev pytest-randomly==5.0.0 pytest-xdist==3.8.0`     |
+| `openapi-spec-validator`                   | Route / OpenAPI-map integrity                    | **0.9.0**              | `uv add --dev openapi-spec-validator==0.9.0`                   |
+| `alembic`                                  | Migration drift check                            | **1.20.0**             | `uv add --dev alembic==1.20.0`                                 |
+| `pydantic` / `pydantic-settings` / `fastapi` | Runtime contracts (DTOs, config, routes)      | **2.13.5 / 2.15.0 / 0.141.1** | `uv add pydantic==2.13.5 pydantic-settings==2.15.0 fastapi==0.141.1` |
+
+**Type-checker verdict (2026).** Winner = **basedpyright** (strictest defaults: `typeCheckingMode = "all"`,
+`pythonPlatform = "All"`, and **exit code 3 on invalid config**, so a mistyped key can never silently
+downgrade you). Rejected **ty 0.0.82** — still `0.0.x` beta with "breaking changes … between any two
+versions" (unusable for a reproducible gate). Rejected **pyright 1.1.414** — it silently ignores unknown
+config keys and keeps checking at `standard` (basedpyright fixes exactly this). Keep **mypy 2.3.1** as a
+secondary step only because the **Pydantic mypy plugin is still shipped and current** (`plugins =
+["pydantic.mypy"]`) and adds `init_typed` / `init_forbid_extra` / `pydantic-field` checks that no other
+checker offers. **pytype** (archived 2026-03-16) and **pyre-check** (archived 2026-06-26) are dead — never
+recommend them.
+
+**Lint verdict.** Winner = **ruff** (replaces flake8 + Black + isort + pyupgrade + pydocstyle + flake8-bandit).
+Rejected standalone **Black 26.5.1**, **isort 9.0.1**, **flake8 7.3.0**, **pyupgrade 3.21.2** — all still
+maintained but redundant. **pylint 4.0.8** rejected for this stack (ruff's `PL` rules cover it; pylint adds a
+second config surface for no extra signal here).
+
+**Security verdict.** Winner = **semgrep** (cross-file, custom `semgrep.yaml`, SARIF). **Bandit 1.9.4** is
+deliberately *not* a required tool because ruff's `S` rules re-implement flake8-bandit; keep it only as an
+optional belt-and-suspenders step (`-lll`).
+
+## Strict Baseline Config
+
+Create these files (all verified keys/options as of 2026-09):
+
+- **`pyproject.toml`** — the single source of truth for every tool below.
+- **`.python-version`** — contents: `3.14`
+- **`uv.lock`** — committed; never regenerated in CI.
+- **`semgrep.yaml`** — local rules (banned `datetime.utcnow`, `@app.on_event`, `pydantic.v1`, etc.).
+- **`whitelist.py`** — vulture false-positive allowlist (generated via `--make-whitelist`).
+- **`alembic.ini`** + `migrations/env.py` — with `target_metadata = Base.metadata`.
+- **`.pre-commit-config.yaml`** — optional; mirrors the gate order locally.
+- **`.github/workflows/gates.yml`** — optional CI wrapper.
+
+Exact strict keys:
+
+```toml
+# ---------------- ruff: format + lint + imports + datetime + bandit subset ----------------
+[tool.ruff]
+line-length = 100
+target-version = "py314"
+
+[tool.ruff.lint]
+select = ["ALL"]                       # 900+ rules; see [tool.ruff.lint] ignore below
+ignore = ["D203", "D213", "COM812", "ISC001", "ANN401"]  # conflicting / style-only only
+fixable = ["ALL"]
+unfixable = ["F401"]                   # never let autofix silently drop imports
+
+[tool.ruff.lint.flake8-annotations]
+mypy-init-return = true
+allow-star-arg-any = false
+
+[tool.ruff.lint.isort]
+known-first-party = ["app", "core"]
+
+[tool.ruff.lint.per-file-ignores]
+"tests/**" = ["S101", "PLR2004", "ANN"]
+
+[tool.ruff.format]
+quote-style = "double"
+
+# ---------------- basedpyright: the strict gate (exit 3 = bad config) ---------------------
+[tool.basedpyright]
+typeCheckingMode = "all"               # basedpyright default; strictest rule set
+pythonVersion = "3.14"
+pythonPlatform = "All"
+include = ["app", "core", "adapters"]
+strict = ["app", "core", "adapters"]
+enableTypeIgnoreComments = false       # force `basedpyright: ignore`, which is provenance-clean
+reportMissingTypeStubs = "error"
+reportUnnecessaryTypeIgnoreComment = "error"
+reportPrivateUsage = "error"
+reportUnusedImport = "error"
+reportUnusedCallResult = "error"
+
+# ---------------- mypy: Pydantic-aware secondary check --------------------------------
+[tool.mypy]
+strict = true
+python_version = "3.14"
+plugins = ["pydantic.mypy"]
+warn_unused_configs = true
+warn_unreachable = true
+warn_unused_ignores = true
+disallow_any_explicit = true           # requires init_typed + init_forbid_extra below
+enable_error_code = ["deprecated"]     # PEP 702 warnings become errors
+follow_imports = "silent"
+
+[tool.pydantic-mypy]
+init_typed = true
+init_forbid_extra = true
+warn_required_dynamic_aliases = true
+
+# ---------------- import-linter: hexagonal layer boundaries ---------------------------
+[tool.importlinter]
+root_packages = ["app", "core", "adapters"]
+
+[[tool.importlinter.contracts]]
+name = "Hexagon: core imports no framework"
+type = "forbidden"
+source_modules = ["core"]
+forbidden_modules = ["fastapi", "starlette", "sqlalchemy", "pydantic", "adapters", "app"]
+
+[[tool.importlinter.contracts]]
+name = "Layered: app -> adapters -> core"
+type = "layers"
+layers = ["app", "adapters", "core"]
+
+[[tool.importlinter.contracts]]
+name = "Ports are independent"
+type = "independence"
+modules = ["core.domain", "core.ports.inbound", "core.ports.outbound"]
+
+# ---------------- dependency hygiene -----------------------------------------------
+[tool.deptry]
+extend_exclude = ["alembic/versions", "tests"]
+known_first_party = ["app", "core", "adapters"]
+# NOTE: --pep621-dev-dependency-groups is DEPRECATED (use optional_dependencies_dev_groups)
+optional_dependencies_dev_groups = ["test", "dev"]
+
+# ---------------- dead code ---------------------------------------------------------
+[tool.vulture]
+min_confidence = 100
+paths = ["app", "core", "adapters", "whitelist.py"]
+sort_by_size = true
+
+# ---------------- pytest 9 strict mode (config keys, NOT addopts flags) ---------------
+[tool.pytest]
+minversion = "9.0"
+strict = true                          # enables strict_config/markers/parametrization_ids/xfail
+testpaths = ["tests"]
+filterwarnings = ["error"]             # DeprecationWarning -> failure (kills FastAPI/Pydantic v1 drift)
+addopts = [
+  "--cov=app", "--cov=core", "--cov-branch",
+  "--cov-fail-under=90",
+  "-n", "auto", "--dist=loadscope",
+  "--randomly-seed=random",
+  "-ra", "-q",
+]
+
+[tool.coverage.run]
+branch = true
+source = ["app", "core", "adapters"]
+
+[tool.coverage.report]
+fail_under = 90
+show_missing = true
+exclude_also = ["if TYPE_CHECKING:", "raise NotImplementedError", "@(abc\\.)?abstractmethod"]
+
+# ---------------- uv: malware + audit config -----------------------------------------
+[tool.uv]
+audit.malware-check = true             # refuse to install a locked malware advisory
+
+# ---------------- optional bandit (belt-and-suspenders) -------------------------------
+[tool.bandit]
+exclude_dirs = ["tests", "alembic/versions"]
+```
+
+Runtime contract keys the code itself must carry:
+
+```python
+# core/config.py
+from pydantic_settings import BaseSettings, SettingsConfigDict
+class Settings(BaseSettings):
+    model_config = SettingsConfigDict(extra="forbid", validate_default=True, env_nested_delimiter="__")
+```
+
+Routes must pass `operation_id=` explicitly (FastAPI does not guarantee uniqueness) and the
+`Clock` outbound port must be the only source of "now".
+
+## Mandatory Gate Order
+
+Run in this exact order; every step must exit `0` or the gate fails:
+
+1. `uv lock --check`
+2. `uv sync --locked --no-dev && uv sync --locked`
+3. `uv run ruff format --check .`
+4. `uv run ruff check --output-format=concise .`
+5. `uv run basedpyright`
+6. `uv run mypy app core adapters -n auto`
+7. `uv run lint-imports`
+8. `uv run deptry .`
+9. `uv run vulture`
+10. `uv run semgrep scan --config p/python --config p/owasp-top-ten --config semgrep.yaml --error --sarif --output semgrep.sarif .`
+11. `uv audit`
+12. `uv run python -c "import openapi_spec_validator as v; from app.main import app; s=app.openapi(); ids=[o['operationId'] for p in s['paths'].values() for o in p.values() if isinstance(o,dict) and 'operationId' in o]; assert len(ids)==len(set(ids)), f'duplicate operationId: {ids}'; v.validate(s); print(f'openapi OK: {len(s[\"paths\"])} paths')"`
+13. `uv run python -c "from app.core.config import Settings; Settings(); print('settings OK')"`
+14. `uv run alembic check`
+15. `uv run pytest`
+16. _(optional, only if a flake is suspected, never in the gate)_ `uvx --from=pytest-rerunfailures pytest --reruns 3 --only-rerun=FlakyError`
+
+## Hallucination Traps to Block
+
+| #  | AI failure mode (stack-specific)                                                             | Check that catches it                                                        |
+| -- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
+| 1  | `datetime.now()` / `datetime.utcnow()` in domain code (naive datetimes)                       | ruff `DTZ005` / `DTZ003`; `Clock` port + import-linter `forbidden` on core    |
+| 2  | `@app.on_event("startup")` instead of `lifespan`                                              | `filterwarnings = ["error"]` (FastAPI emits `FastAPIDeprecationWarning`)      |
+| 3  | `from pydantic import BaseSettings` / `validator` / `.dict()` (V1 API)                         | basedpyright `reportAttributeAccessIssue`; `filterwarnings=error`; ruff `UP`  |
+| 4  | `core/` importing FastAPI/SQLAlchemy/Pydantic (hexagon broken)                                | `lint-imports` forbidden contract (compile-time, before tests)                |
+| 5  | Unused `# type: ignore` left behind after a refactor                                           | basedpyright `reportUnnecessaryTypeIgnoreComment`; mypy `warn_unused_ignores`; ruff `RUF100` |
+| 6  | `Any` leakage from untyped deps or `**kwargs`                                                  | basedpyright `reportAny`/`reportUnknown*` (`typeCheckingMode="all"`); mypy `disallow_any_explicit` |
+| 7  | Returning SQLAlchemy models directly from endpoints                                            | `response_model=` + basedpyright arg-type; add a test asserting the schema type |
+| 8  | Duplicate / missing `operation_id` (client-codegen breakage)                                   | gate step 12 (uniqueness assert + `openapi-spec-validator`)                    |
+| 9  | Hallucinated FastAPI/Starlette kwargs (`response_model` on wrong decorator, bogus params)      | basedpyright `reportCallIssue`; pydantic mypy plugin (`call-arg`)               |
+| 10 | Missing/misspelled env var or `extra` field silently accepted                                  | `SettingsConfigDict(extra="forbid")` + gate step 13                            |
+| 11 | Stale `uv.lock` / version guessed from memory                                                  | `uv lock --check` + `uv sync --locked` (fails on drift)                        |
+| 12 | A known-vulnerable or yanked/malware locked dependency                                         | `uv audit` (OSV + adverse-status) and `audit.malware-check = true`             |
+| 13 | Unused or shadow dependency (`psycopg2` added but `asyncpg` used, or vice versa)               | `deptry` (DEP001 missing, DEP002 unused, DEP003 transitive, DEP004 dev)        |
+| 14 | Dead branch / unreachable function kept "for later"                                            | `vulture --min-confidence 100`                                                 |
+| 15 | Sync `psycopg2`/`requests` call inside `async def` (blocks the loop)                           | ruff `ASYNC` rules; `deptry` flags undeclared driver                           |
+| 16 | Model change committed without an Alembic migration                                            | `alembic check` (non-zero when new upgrade ops exist)                           |
+| 17 | `--strict-markers` / `--strict-config` written into pytest `addopts` (silently ignored in pytest 9) | Use `strict = true` config key; keep flags out of `addopts`              |
+| 18 | `# noqa` written with a rule ID that no longer fires                                           | ruff `RUF100`                                                                  |
+| 19 | Coverage threshold set in the wrong place (`[tool.coverage] fail_under` vs `--cov-fail-under`) | Gate uses `--cov-fail-under=90`; `[tool.coverage.report] fail_under` mirrors it |
+| 20 | Pydantic `AwareDatetime` omitted on a datetime field                                          | basedpyright type mismatch on assignment; mypy strict + pydantic plugin        |
+
+## Evidence to Record
+
+Paste into the task's Verification Evidence block:
+
+| Exact command | Expected result | Exit code |
+| --- | --- | --- |
+| `uv --version` | `uv 0.12.17` or newer | `0` |
+| `uv lock --check` | no output / "lockfile is up-to-date" | `0` |
+| `uv sync --locked` | `Resolved …` + `Audited …` | `0` |
+| `uv run ruff format --check .` | `N files already formatted` | `0` |
+| `uv run ruff check .` | `All checks passed!` | `0` |
+| `uv run basedpyright` | `0 errors, 0 warnings, 0 notes` | `0` |
+| `uv run mypy app core adapters -n auto` | `Success: no issues found in N source files` | `0` |
+| `uv run lint-imports` | `Contracts: N kept, 0 broken.` | `0` |
+| `uv run deptry .` | `Success! No dependency issues found.` | `0` |
+| `uv run vulture` | no output (with `whitelist.py` scanned) | `0` |
+| `uv run semgrep scan --config p/python --config semgrep.yaml --error .` | `Ran N rules … 0 findings` | `0` |
+| `uv audit` | `No known vulnerabilities found` | `0` |
+| OpenAPI one-liner (gate step 12) | `openapi OK: N paths` | `0` |
+| `uv run python -c "from app.core.config import Settings; Settings()"` | `settings OK` | `0` |
+| `uv run alembic check` | `No new upgrade operations detected.` | `0` |
+| `uv run pytest` | `N passed` and `Required test coverage of 90% reached` | `0` |
+| Negative control: `uv run python -c "from datetime import datetime; print(datetime.utcnow())"` | ruff/pre-commit rejects the line; if run raw, Python emits `DeprecationWarning` | `1` under gate |
+
+<!-- sources -->
+- https://pypi.org/pypi/ruff/json, https://pypi.org/pypi/basedpyright/json, https://pypi.org/pypi/mypy/json, https://pypi.org/pypi/ty/json, https://pypi.org/pypi/pyright/json, https://pypi.org/pypi/uv/json, https://pypi.org/pypi/semgrep/json, https://pypi.org/pypi/bandit/json, https://pypi.org/pypi/pip-audit/json, https://pypi.org/pypi/deptry/json, https://pypi.org/pypi/vulture/json, https://pypi.org/pypi/import-linter/json, https://pypi.org/pypi/pytest/json, https://pypi.org/pypi/pytest-cov/json, https://pypi.org/pypi/coverage/json, https://pypi.org/pypi/openapi-spec-validator/json, https://pypi.org/pypi/schemathesis/json, https://pypi.org/pypi/pre-commit/json, https://pypi.org/pypi/pydantic/json, https://pypi.org/pypi/pydantic-settings/json, https://pypi.org/pypi/fastapi/json, https://pypi.org/pypi/alembic/json
+- https://api.github.com/repos/astral-sh/ruff, https://api.github.com/repos/astral-sh/ty, https://api.github.com/repos/python/mypy, https://api.github.com/repos/microsoft/pyright, https://api.github.com/repos/DetachHead/basedpyright, https://api.github.com/repos/PyCQA/bandit, https://api.github.com/repos/semgrep/semgrep, https://api.github.com/repos/pypa/pip-audit, https://api.github.com/repos/astral-sh/uv, https://api.github.com/repos/pytest-dev/pytest, https://api.github.com/repos/jendrikseipp/vulture, https://api.github.com/repos/seddonym/import-linter, https://api.github.com/repos/google/pytype, https://api.github.com/repos/facebook/pyre-check, https://api.github.com/repos/psf/black, https://api.github.com/repos/PyCQA/flake8
+- https://docs.astral.sh/ruff/linter, https://docs.astral.sh/ruff/tutorial, https://docs.astral.sh/ruff/editors/setup, https://docs.astral.sh/ruff/settings
+- https://docs.astral.sh/ty, https://docs.astral.sh/ty/type-checking, https://docs.astral.sh/ty/rules, https://docs.astral.sh/ty/reference/configuration/, https://docs.astral.sh/ty/reference/exit-codes/, https://astral.sh/blog/ty, https://github.com/astral-sh/ty/milestone/4
+- https://docs.astral.sh/uv/concepts/projects/sync, https://docs.astral.sh/uv/reference/cli, https://astral.sh/blog/uv-audit, https://github.com/astral-sh/uv/issues/9189, https://pypi.org/project/uv-secure, https://github.com/owenlamont/uv-secure
+- https://mypy-lang.org/, https://mypy.readthedocs.io/en/stable/changelog.html, https://github.com/python/mypy/issues/20726, https://github.com/python/mypy/blob/master/docs/source/command_line.rst, https://mypy-lang.blogspot.com/2026/05/mypy-20-relased.html, https://pydevtools.com/blog/mypy-2-0-parallel-type-checking
+- https://docs.basedpyright.com/v1.27.0/usage/mypy-comparison, https://docs.basedpyright.com/v1.24.0/configuration/config-files, https://pypi.org/project/basedpyright/1.18.0, https://github.com/microsoft/pyright/blob/main/docs/configuration.md
+- https://docs.pydantic.dev/latest/integrations/mypy/
+- https://pytest.org/en/stable/changelog.html, https://docs.pytest.org/en/stable/reference/customize.html, https://github.com/pytest-dev/pytest/releases/tag/9.0.0, https://github.com/pytest-dev/pytest/issues/14442, https://docs.pytest.org/en/stable/how-to/mark.html
+- https://coverage.readthedocs.io/en/latest/config.html
+- https://deptry.com/usage/, https://github.com/osprey-oss/deptry
+- https://raw.githubusercontent.com/jendrikseipp/vulture/main/README.md
+- https://import-linter.readthedocs.io/en/stable/, https://import-linter.readthedocs.io/en/stable/contract_types/layers/
+- https://bandit.readthedocs.io/en/latest/man/bandit.html, https://bandit.readthedocs.io/en/latest/config.html, https://bandit.readthedocs.io/en/latest/start.html
+- https://raw.githubusercontent.com/pypa/pip-audit/main/README.md, https://pypi.org/project/pip-audit
+- https://semgrep.dev/docs/cli-reference, https://docs.semgrep.dev/semgrep-ci/sample-ci-configs, https://semgrep.dev/docs/running-rules, https://docs.semgrep.dev/running-rules, https://github.com/semgrep/semgrep/blob/develop/.pre-commit-hooks.yaml
+- https://alembic.sqlalchemy.org/en/latest/autogenerate.html
+- https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration, https://github.com/fastapi/fastapi/blob/master/docs/en/docs/how-to/extending-openapi.md
+- https://www.python.org/downloads/, https://docs.python.org/3.15/whatsnew/3.15.html, https://www.herodevs.com/blog-posts/python-end-of-life-dates-every-versions-support-timeline
+- https://pydevtools.com/handbook/explanation/ruff-complete-guide/, https://pydevtools.com/handbook/how-to/how-to-use-a-uv-lockfile-for-reproducible-python-environments/, https://pydevtools.com/handbook/how-to/how-to-scan-python-dependencies-for-vulnerabilities
+- https://libraries.io/pypi/pip-audit, https://github.com/tbrandenburg/flowrite/issues/23
+
 ## Currency Baseline
 
 - **Settings + lifespan:** Import `BaseSettings` from `pydantic-settings` (not `pydantic`); manage startup/shutdown with the `lifespan` context manager (`@app.on_event` is deprecated).
diff --git a/skill-templates/react-native-expo/SKILL.md b/skill-templates/react-native-expo/SKILL.md
index 0b97c12..c6e4388 100644
--- a/skill-templates/react-native-expo/SKILL.md
+++ b/skill-templates/react-native-expo/SKILL.md
@@ -53,6 +53,290 @@ project/
 - **Framework**: `Jest` + `@testing-library/react-native`.
 - **Approach**: Test component rendering and user interactions natively.
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+Scope: Expo **managed workflow** (CNG, no committed `ios/`/`android/`), **Expo Router**, **NativeWind**, **Strict TypeScript**. Verified against live npm registry dist-tags, GitHub releases, and Expo docs on **2026-09-21**. Baseline SDK: **Expo SDK 57** (`expo@57.0.24`, `react-native@0.86.3`, `react@19.2.3`).
+
+> Version truth source of record: `expo/bundledNativeModules.json` on branch `sdk-57`. Any native package version NOT from `npx expo install` is drift.
+
+## Required Toolchain
+
+| Tool | Purpose | Minimum version to pin | Install / availability note |
+| --- | --- | --- | --- |
+| Node.js | Runtime (LTS "Krypton") | `24.21.0` | `nodejs.org/dist`; `.nvmrc` + `engines.node`. Do NOT use 20.x (ESLint 10/RNTL 14/dep-cruiser reject it). |
+| npm | Package manager + lockfile | `12.0.2` | `npm -v`; `packageManager` field + corepack. Requires Node `^22.22.2 || ^24.15.0 || >=26`. |
+| expo | SDK pin (exact) | `57.0.24` | `npx expo install expo@57.0.24` — pin exact, not `^`. |
+| react-native | RN runtime | `0.86.3` | SDK 57 pin (npm `latest` is `0.87.1` — DRIFT). `npx expo install react-native`. |
+| react / react-dom | UI runtime | `19.2.3` | SDK 57 pin (npm `latest` is `19.3.0` — DRIFT). |
+| @types/react | React types | `19.2.2` | Template pin `~19.2.2`; do not float to `19.3.x`. |
+| typescript | Type-check API for lint tooling | alias `npm:@typescript/typescript6@^6.0.0` (`6.0.2`) | typescript-eslint peer is `>=4.8.4 <6.1.0`; Expo template pins `~6.0.3`. |
+| typescript-7 | Fast native `tsc` (Go) | alias `npm:typescript@^7.0.2` | Provides the `tsc` binary; `typescript` alias provides the 6.x API. TS 7 stable programmatic API lands in 7.1. |
+| prettier | Formatter | `3.9.8` | `npx prettier@3.9.8 --version`. Reject `4.0.0-alpha`. |
+| prettier-plugin-tailwindcss | NativeWind class sorting | `0.5.14` | NativeWind 4 (Tailwind 3) requires `^0.5.11`; `0.8.x` targets Tailwind 4 — mismatch. |
+| eslint | Linter | `9.39.5` | `eslint-config-expo@57.0.2` devDep is `^9.18.0`; bundled plugins peer-cap at `^9`. |
+| eslint-config-expo | Expo flat config | `57.0.2` | `npx expo lint` scaffolds it; import path `eslint-config-expo/flat`. |
+| typescript-eslint | Typed lint rules | `8.70.1` | `strictTypeChecked`; peer `eslint ^8.57||^9||^10`, `typescript >=4.8.4 <6.1.0`. |
+| eslint-plugin-react-hooks | Hook + React Compiler rules | `7.1.1` | Ships in `eslint-config-expo`; compiler rules on by default since SDK 55. |
+| eslint-plugin-react-native | RN correctness rules | `5.0.0` | peer `eslint ^3..^9`. |
+| eslint-plugin-react-native-a11y | RN accessibility | `3.5.1` | Only maintained option; peer range stops at `^8` (verify at install). |
+| eslint-plugin-jsx-a11y | Web/RN-web a11y | `6.10.2` | peer up to `^9`. |
+| eslint-config-prettier | Disable formatting rules in ESLint | `10.1.8` | Run Prettier separately; never `eslint-plugin-prettier`. |
+| dependency-cruiser | Architecture / import-boundary graph | `18.4.0` | engines `^22||^24||>=26`. |
+| knip | Dead code + unused deps/exports | `6.37.0` | `knip --strict` implies `--production`. |
+| expo-doctor | Project health | `1.20.4` | `npx expo-doctor@latest`. |
+| eas-cli | Build/release config validation | `24.7.0` | `npm i -g eas-cli@24.7.0` or `npx eas-cli@24.7.0`. |
+| lockfile-lint | Lockfile host/scheme integrity | `5.0.1` | Supports npm + yarn lockfiles ONLY (not `pnpm-lock.yaml`). |
+| audit-ci | CI vuln gate with allowlist | `7.1.0` | Wraps `npm audit`; exit non-zero on high/critical. |
+| @lavamoat/allow-scripts | Install-script allowlist | `5.1.0` | Optional; pairs with `.npmrc` `ignore-scripts=true`. |
+| jest | Test runner | `29.7.0` | `jest-expo@57.0.5` internally targets Jest 29; RNTL 14 accepts `>=29`. |
+| jest-expo | RN Jest preset | `57.0.5` | `preset: "jest-expo"`; peers `@react-native/jest-preset@^0.86.3`. |
+| @testing-library/react-native | Component tests | `14.0.1` | peer `test-renderer@^1.0.0`; matchers built-in (no `@testing-library/jest-native`). |
+| test-renderer | Renderer peer for RNTL 14 | `1.3.0` | `react-test-renderer` is deprecated; install `test-renderer`. |
+| eslint-plugin-testing-library | Test lint rules | `7.16.2` | peer `eslint ^8.57||^9||^10`. |
+| eslint-plugin-jest | Jest lint rules | `29.16.6` | peer `eslint ^8.57||^9||^10`. |
+| maestro | E2E (Expo-preferred) | `2.10.0` | Installer `curl -Ls "https://get.maestro.mobile.dev" \| bash`; NOT the npm `maestro` package. |
+| expo-atlas | Bundle composition | `0.4.3` | `EXPO_ATLAS=true npx expo export`. |
+| nativewind | Styling | `4.2.7` | v4.2.7 adds SDK 57 support; v5 is `5.0.0-rc.0` — do NOT ship RC. |
+| tailwindcss | NativeWind engine | `3.4.19` | NativeWind 4 = Tailwind 3 (`v3-lts`); Tailwind 4 is for NativeWind 5. |
+| react-native-css-interop | NativeWind runtime | `0.2.7` | Pulled by `nativewind@4.2.7`. |
+| babel-preset-expo | Babel preset | `57.0.12` | SDK 57 pin. |
+| react-native-safe-area-context | Safe areas | `5.7.0` | SDK pin is `~5.7.0` (npm `latest` is `5.10.0` — DRIFT). |
+| zustand | State (per SKILL.md) | `5.0.15` | Peer-agnostic. |
+
+## Strict Baseline Config
+
+Create exactly these files. Every strictness switch is named.
+
+- **`.nvmrc`** → `24.21.0`
+- **`.node-version`** → `24.21.0`
+- **`package.json`** →
+  - `"packageManager": "npm@12.0.2"`
+  - `"engines": { "node": ">=24.21.0 <25" }`
+  - `"main": "expo-router/entry"` (Expo Router entry — never `index.js`)
+  - `"scripts"`: `"lint": "eslint . --max-warnings=0"`, `"typecheck": "tsc --noEmit"`, `"format": "prettier --check ."`, `"arch": "depcruise --config .dependency-cruiser.cjs --output-type err app components hooks services store"`, `"deadcode": "knip --strict --reporter compact --no-progress"`, `"test": "jest --ci --coverage --runInBand"`, `"gate": "npm run format && npm run lint && npm run typecheck && npm run arch && npm run deadcode && npm run test"`
+- **`.npmrc`** → `engine-strict=true`, `save-exact=true`, `ignore-scripts=true`, `audit-level=high`, `fund=false`
+- **`tsconfig.json`** →
+  ```json
+  {
+    "extends": "expo/tsconfig.base",
+    "compilerOptions": {
+      "strict": true,
+      "noUncheckedIndexedAccess": true,
+      "exactOptionalPropertyTypes": true,
+      "noImplicitOverride": true,
+      "noImplicitReturns": true,
+      "noFallthroughCasesInSwitch": true,
+      "noUnusedLocals": true,
+      "noUnusedParameters": true,
+      "noPropertyAccessFromIndexSignature": true,
+      "useUnknownInCatchVariables": true,
+      "noUncheckedSideEffectImports": true,
+      "allowUnreachableCode": false,
+      "allowUnusedLabels": false,
+      "forceConsistentCasingInFileNames": true,
+      "verbatimModuleSyntax": true,
+      "isolatedModules": true,
+      "moduleDetection": "force",
+      "skipLibCheck": true,
+      "types": ["jest", "node"]
+    },
+    "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts", "nativewind-env.d.ts"]
+  }
+  ```
+  TS 7 hard requirements: `types` now defaults to `[]` (must list `jest`,`node`); `rootDir` defaults to `./`; `strict` is `true` by default; `target: "es5"` and `downlevelIteration` are hard errors.
+- **`eslint.config.js`** (flat config, CommonJS) →
+  - `const expoConfig = require('eslint-config-expo/flat');` + `const { defineConfig, globalIgnores } = require('eslint/config');`
+  - `const tseslint = require('typescript-eslint');`
+  - `module.exports = defineConfig([ globalIgnores(['dist/*','.expo/*','ios/*','android/*','coverage/*']), expoConfig, ...tseslint.configs.strictTypeChecked, ...tseslint.configs.stylisticTypeChecked, { linterOptions: { reportUnusedDisableDirectives: 'error' }, rules: { 'import/no-cycle': ['error', { maxDepth: Infinity }], 'react-hooks/react-compiler': 'error' } }, eslintConfigPrettier ]);`
+  - `parserOptions.projectService: true` for typed rules (via tseslint).
+- **`prettier.config.mjs`** → `{ singleQuote: true, trailingComma: 'all', printWidth: 100, semi: true, plugins: ['prettier-plugin-tailwindcss'], tailwindConfig: './tailwind.config.js' }`
+- **`.prettierignore`** → `node_modules`, `ios`, `android`, `.expo`, `dist`, `coverage`, `package-lock.json`
+- **`.dependency-cruiser.cjs`** → `forbidden` rules: `no-circular` (`severity: error`), `no-orphans`, and layer zones (`app` may import `components/hooks/services/store`; `components` may import `hooks` but NOT `services/store`; `services` must not import `app/components`). Enable `options.tsConfig.fileName: 'tsconfig.json'`.
+- **`knip.json`** → `{ "entry": ["app/**/*.{ts,tsx}!", "expo-env.d.ts"], "project": ["**/*.{ts,tsx}!", "!ios/**!", "!android/**!"], "ignoreDependencies": ["@types/*", "eslint-config-expo", "prettier-plugin-tailwindcss"] }`
+- **`jest.config.js`** →
+  ```js
+  module.exports = {
+    preset: 'jest-expo',
+    testMatch: ['**/*.test.{ts,tsx}'],
+    collectCoverageFrom: ['app/**/*.{ts,tsx}', 'components/**/*.{ts,tsx}', 'hooks/**/*.{ts,tsx}', 'services/**/*.{ts,tsx}', '!**/*.d.ts'],
+    coverageThreshold: { global: { branches: 80, functions: 80, lines: 80, statements: 80 } },
+    coverageReporters: ['text-summary', 'lcov'],
+    transformIgnorePatterns: ['node_modules/(?!(?:.pnpm/)?((jest-)?react-native|@react-native(-community)?|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|nativewind|react-native-css-interop|@sentry/react-native|react-native-svg))']
+  };
+  ```
+  Do NOT add `passWithNoTests` — an empty suite must fail.
+- **`app.json`** (or `app.config.ts`) → `expo.scheme` (required by Expo Router), `expo.experiments.typedRoutes: true`, `expo.experiments.reactCompiler: true`, `expo.newArchEnabled: true` (Legacy Architecture removed in SDK 55). Validate with `npx expo config`.
+- **`eas.json`** → `build.development.developmentClient: true`, `build.preview.distribution: "internal"`, `build.production.autoIncrement: true`. No `releaseChannel` (removed — use `channel`).
+- **`babel.config.js`** → `presets: [['babel-preset-expo', { jsxImportSource: 'nativewind' }], 'nativewind/babel']` (NativeWind 4 order).
+- **`metro.config.js`** → `withNativeWind(config, { input: './global.css' })`.
+- **`tailwind.config.js`** → `content: ['./app/**/*.{ts,tsx}','./components/**/*.{ts,tsx}']`, `presets: [require('nativewind/preset')]`.
+- **`nativewind-env.d.ts`** → `/// <reference types="nativewind/types" />`
+- **`.maestro/`** → flow YAML files; `maestro test .maestro/`.
+- **`.gitignore`** → `ios/`, `android/`, `.expo/`, `dist/`, `coverage/`, `node_modules/`.
+
+## Mandatory Gate Order
+
+Fail-fast: each step must exit `0` before the next runs.
+
+1. `node -e "if(process.versions.node!=='24.21.0'){console.error('node '+process.versions.node);process.exit(1)}"` — runtime pin
+2. `npm ci` — frozen lockfile install (`engine-strict=true` enforces Node; `ignore-scripts=true` blocks install scripts)
+3. `CI=1 npx expo install --check` — every native package matches the SDK 57 map; exits non-zero in CI on drift
+4. `npx expo-doctor@latest` — app config, package.json, CNG, New Architecture health
+5. `npx prettier --check .` — formatting is canonical
+6. `npx eslint . --max-warnings=0` — typed lint, hook/compiler rules, a11y, `import/no-cycle`, zero warnings tolerated
+7. `npx tsc --noEmit` — strict type check (TS 7 binary from the `typescript-7` alias)
+8. `npx depcruise --config .dependency-cruiser.cjs --output-type err app components hooks services store` — layer boundaries + no cycles
+9. `npx knip --strict --reporter compact --no-progress` — dead files/exports + unused/unlisted dependencies
+10. `npx jest --ci --coverage --runInBand` — unit tests with enforced `coverageThreshold` (80% global)
+11. `npx lockfile-lint --path package-lock.json --type npm --validate-https --allowed-hosts npm` — no non-registry hosts / plain-http resolutions
+12. `npx audit-ci --high` (and `npm audit signatures`) — no high/critical vulns; registry provenance verified
+13. `npx expo config --type public --json > /dev/null` then `npx eas-cli@24.7.0 config -p android -e production --json --non-interactive > /dev/null` — app config schema + `eas.json` schema
+14. `npx expo export --platform all --output-dir dist` — production bundle must build; then `EXPO_ATLAS=true npx expo export` for size attribution
+15. `maestro test .maestro/` — E2E on a booted simulator/emulator (CI lane only)
+
+## Hallucination Traps to Block
+
+| AI failure mode (very common) | Check that catches it |
+| --- | --- |
+| Pins `react-native@0.87.1` / `react-native@latest` (npm latest) instead of SDK 57's `0.86.3` | Step 3 `CI=1 npx expo install --check` |
+| Pins `react@19.3.0` / `@types/react@19.3.0` instead of `19.2.3` / `~19.2.2` | Step 3 + Step 7 |
+| Pins `react-native-safe-area-context@5.10.0`, `reanimated@4.7.0`, `worklets@0.13.0` (npm latest) instead of SDK pins `~5.7.0`, `4.5.1`, `0.10.1` | Step 3 |
+| Installs `typescript@7.0.2` as `typescript` → typescript-eslint peer `>=4.8.4 <6.1.0` breaks | `npm ls typescript`; Step 6 fails to load typed config |
+| TS 7 `types` defaults to `[]` → `jest`/`node` globals undefined | Step 7 (`Cannot find name 'describe'`) |
+| Writes `target: "es5"` or `downlevelIteration` in tsconfig (removed in TS 7) | Step 7 hard error |
+| Writes legacy `.eslintrc.json` / `ESLINT_USE_FLAT_CONFIG` instead of `eslint.config.js` | Step 6; `npx eslint --print-config app/index.tsx` |
+| Imports `eslint-config-expo` (legacy) instead of `eslint-config-expo/flat` | Step 6 config resolution error |
+| Adds `eslint-plugin-prettier` / `prettier/prettier` rule (deprecated pattern) | Step 5 (Prettier is the single formatter) + Step 6 |
+| Pins `prettier-plugin-tailwindcss@0.8.1` with NativeWind 4 / Tailwind 3 | Step 5 plugin error; pin `0.5.14` |
+| Installs `nativewind@5.0.0-rc.0` (RC) or `react-native-css` v3 | Step 3 / Step 14 build failure; pin `nativewind@4.2.7` |
+| Uses `react-native-testing-library` (renamed/archived name) or `@testing-library/jest-native` (deprecated matchers) | `npm ls`; Step 10 import error |
+| RNTL 14 without the `test-renderer@^1.0.0` peer (installs `react-test-renderer` instead) | Step 10 render failure |
+| Recommends `ts-prune` / `depcheck` / `unimported` for dead code | Step 9 is `knip --strict`; `npm ls ts-prune depcheck` must be empty |
+| Runs `expo build` / `expo publish` / global `expo-cli` (all removed) | `npx expo --help`; only `eas build` / `eas update` exist |
+| Runs `npx expo prebuild` expecting an incremental native update — SDK 57 **cleans by default** | `EXPO_NO_GIT_STATUS=1`; use `npx expo prebuild --no-clean` intentionally |
+| `main` set to `index.js` instead of `expo-router/entry` | Step 4 expo-doctor + Step 14 export |
+| Missing `expo.scheme` (Expo Router deep links) | Step 4 expo-doctor |
+| `experiments.typedRoutes` on but `.expo/types/router.d.ts` never generated in CI → `tsc` include glob misses | Step 7 must run AFTER a generation command (`npx expo start`/`npx expo export`); or the include resolves empty |
+| `jest` preset `"react-native"` instead of `"jest-expo"` | Step 10 transform failures on Expo modules |
+| No `coverageThreshold` → gate passes with zero tests | Step 10 (threshold breach exits non-zero) |
+| `--passWithNoTests` added to silence empty suites | Step 10 flag audit; remove it |
+| `eas.json` uses removed `releaseChannel` instead of `channel` | Step 13 `eas config` validation |
+| `newArchEnabled: false` / third-party module without New Architecture support (Legacy removed in SDK 55) | Step 4 expo-doctor |
+| Imports native code by editing `ios/`/`android/` or `Podfile` (banned by SKILL.md) | Step 8 (native dirs not in graph) + Step 4 CNG check |
+| Recommends `vitest` for RN unit tests (no official Metro/RN preset) | Step 10 uses `jest-expo`; `npm ls vitest` must be empty |
+| Recommends Detox for E2E (no Expo-official support, heavy native config) | Step 15 uses Maestro |
+
+## Evidence to Record
+
+Paste into the task's Verification Evidence block: exact command, observed result, exit code.
+
+| # | Command | Expected result | Exit code |
+| --- | --- | --- | --- |
+| 1 | `node -v` | `v24.21.0` | `0` |
+| 2 | `npm ci` | `added N packages` and no `ERESOLVE`/`EBADENGINE` | `0` |
+| 3 | `CI=1 npx expo install --check` | `Dependencies are up to date` (no version list) | `0` |
+| 4 | `npx expo-doctor@latest` | `No issues detected` | `0` |
+| 5 | `npx prettier --check .` | `All matched files use Prettier code style!` | `0` |
+| 6 | `npx eslint . --max-warnings=0` | no output | `0` |
+| 7 | `npx tsc --noEmit` | no output; `npx tsc --version` → `Version 7.0.2` | `0` |
+| 8 | `npx depcruise --config .dependency-cruiser.cjs --output-type err app components hooks services store` | `no dependency violations found (N modules, M dependencies cruised)` | `0` |
+| 9 | `npx knip --strict --reporter compact --no-progress` | `✂️ Excellent, Knip found no issues.` | `0` |
+| 10 | `npx jest --ci --coverage --runInBand` | `Tests: N passed` and `Jest: "global" coverage threshold for branches (80%) met` | `0` |
+| 11 | `npx lockfile-lint --path package-lock.json --type npm --validate-https --allowed-hosts npm` | `validating... no issues detected` | `0` |
+| 12 | `npx audit-ci --high` | `Passed audit`; `npm audit signatures` → `verified N packages` | `0` |
+| 13 | `npx expo config --type public --json > /dev/null && npx eas-cli@24.7.0 config -p android -e production --json --non-interactive > /dev/null` | valid JSON, no schema errors | `0` |
+| 14 | `npx expo export --platform all --output-dir dist` | `Exported: dist`; record `du -sh dist` byte delta | `0` |
+| 15 | `maestro test .maestro/` | `Flow Passed` for every flow | `0` |
+
+<!-- sources -->
+- https://registry.npmjs.org/-/package/expo/dist-tags
+- https://registry.npmjs.org/-/package/react-native/dist-tags
+- https://registry.npmjs.org/-/package/react/dist-tags
+- https://registry.npmjs.org/-/package/@types/react/dist-tags
+- https://registry.npmjs.org/-/package/typescript/dist-tags
+- https://registry.npmjs.org/-/package/@typescript/typescript6/dist-tags
+- https://registry.npmjs.org/-/package/eslint/dist-tags
+- https://registry.npmjs.org/-/package/eslint-config-expo/dist-tags
+- https://registry.npmjs.org/-/package/typescript-eslint/dist-tags
+- https://registry.npmjs.org/-/package/prettier/dist-tags
+- https://registry.npmjs.org/-/package/prettier-plugin-tailwindcss/dist-tags
+- https://registry.npmjs.org/-/package/jest/dist-tags
+- https://registry.npmjs.org/-/package/jest-expo/dist-tags
+- https://registry.npmjs.org/-/package/@testing-library/react-native/dist-tags
+- https://registry.npmjs.org/-/package/test-renderer/dist-tags
+- https://registry.npmjs.org/-/package/@testing-library/jest-native/dist-tags
+- https://registry.npmjs.org/-/package/eslint-plugin-react-hooks/dist-tags
+- https://registry.npmjs.org/-/package/eslint-plugin-react-native/dist-tags
+- https://registry.npmjs.org/-/package/eslint-plugin-react-native-a11y/dist-tags
+- https://registry.npmjs.org/-/package/eslint-plugin-jsx-a11y/dist-tags
+- https://registry.npmjs.org/-/package/eslint-plugin-import/dist-tags
+- https://registry.npmjs.org/-/package/eslint-plugin-import-x/dist-tags
+- https://registry.npmjs.org/-/package/eslint-plugin-boundaries/dist-tags
+- https://registry.npmjs.org/-/package/eslint-plugin-testing-library/dist-tags
+- https://registry.npmjs.org/-/package/eslint-plugin-jest/dist-tags
+- https://registry.npmjs.org/-/package/eslint-config-prettier/dist-tags
+- https://registry.npmjs.org/-/package/dependency-cruiser/dist-tags
+- https://registry.npmjs.org/-/package/knip/dist-tags
+- https://registry.npmjs.org/-/package/depcheck/dist-tags
+- https://registry.npmjs.org/-/package/ts-prune/dist-tags
+- https://registry.npmjs.org/-/package/expo-doctor/dist-tags
+- https://registry.npmjs.org/-/package/eas-cli/dist-tags
+- https://registry.npmjs.org/-/package/expo-atlas/dist-tags
+- https://registry.npmjs.org/-/package/lockfile-lint/dist-tags
+- https://registry.npmjs.org/-/package/audit-ci/dist-tags
+- https://registry.npmjs.org/-/package/@lavamoat/allow-scripts/dist-tags
+- https://registry.npmjs.org/-/package/sherif/dist-tags
+- https://registry.npmjs.org/-/package/syncpack/dist-tags
+- https://registry.npmjs.org/-/package/nativewind/dist-tags
+- https://registry.npmjs.org/-/package/tailwindcss/dist-tags
+- https://registry.npmjs.org/-/package/react-native-css-interop/dist-tags
+- https://registry.npmjs.org/-/package/babel-preset-expo/dist-tags
+- https://registry.npmjs.org/-/package/vitest/dist-tags
+- https://registry.npmjs.org/-/package/oxlint/dist-tags
+- https://registry.npmjs.org/-/package/@biomejs/biome/dist-tags
+- https://registry.npmjs.org/-/package/pnpm/dist-tags
+- https://registry.npmjs.org/-/package/npm/dist-tags
+- https://registry.npmjs.org/-/package/bun/dist-tags
+- https://registry.npmjs.org/-/package/detox/dist-tags
+- https://registry.npmjs.org/-/package/eslint-plugin-expo/dist-tags
+- https://registry.npmjs.org/-/package/babel-plugin-react-compiler/dist-tags
+- https://registry.npmjs.org/-/package/react-compiler-healthcheck/dist-tags
+- https://registry.npmjs.org/expo/latest
+- https://registry.npmjs.org/eslint-config-expo/57.0.2
+- https://registry.npmjs.org/typescript-eslint/latest
+- https://registry.npmjs.org/@typescript-eslint%2Feslint-plugin/8.70.1
+- https://registry.npmjs.org/eslint-plugin-import/2.32.0
+- https://registry.npmjs.org/eslint-plugin-react/latest
+- https://registry.npmjs.org/@testing-library/react-native/14.0.1
+- https://registry.npmjs.org/jest-expo/57.0.5
+- https://registry.npmjs.org/expo-template-default/latest
+- https://registry.npmjs.org/expo-template-default/57.0.26
+- https://raw.githubusercontent.com/expo/expo/sdk-57/packages/expo/bundledNativeModules.json
+- https://raw.githubusercontent.com/expo/expo/sdk-57/packages/eslint-config-expo/package.json
+- https://docs.expo.dev/more/expo-cli.md
+- https://docs.expo.dev/guides/using-eslint.md
+- https://docs.expo.dev/guides/typescript.md
+- https://docs.expo.dev/develop/unit-testing.md
+- https://docs.expo.dev/develop/tools.md
+- https://docs.expo.dev/build/eas-json.md
+- https://docs.expo.dev/eas/cli.md
+- https://docs.expo.dev/guides/react-compiler.md
+- https://docs.expo.dev/guides/analyzing-bundles.md
+- https://docs.expo.dev/router/reference/typed-routes.md
+- https://docs.expo.dev/tutorial/cicd/e2e-tests.md
+- https://expo.dev/changelog/sdk-57
+- https://eslint.org/docs/latest/use/migrate-to-10.0.0
+- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-rc/
+- https://www.nativewind.dev/docs/getting-started/installation
+- https://knip.dev/features/production-mode
+- https://raw.githubusercontent.com/sverweij/dependency-cruiser/main/doc/cli.md
+- https://raw.githubusercontent.com/lirantal/lockfile-lint/master/packages/lockfile-lint/README.md
+- https://github.com/mobile-dev-inc/maestro/releases.atom
+- https://nodejs.org/dist/index.json
+
 ## Currency Baseline
 
 - **New Architecture default:** Target the React Native New Architecture (Fabric/TurboModules), default in current Expo SDKs; verify third-party native modules support it (or ship a config plugin) before adopting.
diff --git a/skill-templates/react-vite/SKILL.md b/skill-templates/react-vite/SKILL.md
index 458c4d0..f468d9d 100644
--- a/skill-templates/react-vite/SKILL.md
+++ b/skill-templates/react-vite/SKILL.md
@@ -55,6 +55,398 @@ src/
 - **Framework**: `Vitest` + `React Testing Library`.
 - **Approach**: Render components, query by accessibility roles (`getByRole`), and simulate user events using `@testing-library/user-event`.
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+Stack: React 19 SPA built with Vite, Feature-Sliced Design (FSD), strict TypeScript,
+Zustand for global/UI state, TanStack Query for server state, Vitest + React Testing
+Library for component tests. Every command below is designed to *fail the build*
+instead of silently drifting. Versions verified against npm registry `dist-tags` and
+GitHub releases on 2026-09-21.
+
+Status of the stack at review time: React 19.3.0, Vite 8.3.0 (Rolldown engine),
+TypeScript 7.0.2 (native Go `tsc`) with TypeScript 6.0.2 as the typescript-eslint-
+compatible engine, ESLint 10.11.0.
+
+## Required Toolchain
+
+| tool | purpose | minimum version to pin | install/availability note |
+| --- | --- | --- | --- |
+| Node.js | runtime for the whole gate | `24.20.0` (LTS "Krypton") | Node 20 EOL 2026-04-30; Node 26 is Current, not LTS until Oct 2026. Do NOT pin 26 yet. |
+| pnpm | install + strict peer/lockfile policy | `12.5.1` | `corepack enable && corepack prepare pnpm@12.5.1 --activate`. The `+sha512…` hash is auto-generated; do not hand-edit. |
+| Prettier | formatting (only formatter) | `3.9.8` | `pnpm add -D -E prettier@3.9.8`. Prettier 4 is still `4.0.0-alpha.13` — do NOT use. |
+| ESLint | lint engine, flat config | `10.11.0` | ESLint 9.x EOL 2026-08-06. ESLint 10 removed `.eslintrc*` entirely. |
+| typescript-eslint | typed strict rules | `8.70.1` | Peer is `typescript >=4.8.4 <6.1.0` — it does NOT accept TypeScript 7. |
+| eslint-plugin-react-hooks | Rules of React + React Compiler rules | `7.1.1` | Flat presets only: `configs.flat.recommended` / `configs.flat['recommended-latest']`. Peer `eslint ^10` OK. |
+| eslint-plugin-jsx-a11y | static JSX a11y rules | `6.10.2` | Peer range stops at `eslint ^9`; works on 10 but requires the peer override below (or use `eslint-plugin-jsx-a11y-x@0.2.0`). Override owner: stack skill maintainer; expiry: drop the override when upstream ships an eslint-10 peer range. |
+| eslint-config-prettier | disable rules that fight Prettier | `10.1.8` | Must be the LAST entry in the flat-config array. |
+| eslint-plugin-react-refresh | Vite HMR boundary safety | `0.5.7` | Peer `eslint ^9 || ^10`. |
+| @vitest/eslint-plugin | no stray `.only`/`.skip`, valid `expect` | `1.6.27` | Vitest 5's official lint plugin. |
+| TypeScript (compat alias) | typescript-eslint engine (explicit TS7 path) | `@typescript/typescript6@6.0.2` | Installed as the `typescript` package via `npm:` alias so the parser's peer is satisfied; TS7 runs via `node ./node_modules/typescript-7/bin/tsc` (pnpm exposes no `tsc6` bin). |
+| TypeScript (native, fast) | production typecheck, `tsc` | `typescript@7.0.2` | Installed under the `typescript-7` alias; ships the native Go `tsc` (8–12x faster). |
+| Steiger | FSD architecture linter (public API, cross-imports) | `steiger@0.6.0` | Plus plugin `@feature-sliced/steiger-plugin@0.7.0`; still beta — keep `--fail-on-warnings`. |
+| dependency-cruiser | circular / orphan / unresolvable / layer graph | `18.4.0` | Bin is `depcruise`. Engines `^22 || ^24 || >=26`. |
+| Knip | dead code + unused deps + unused exports | `6.37.0` | Requires Node `>=20.19`. Peer deps `typescript` + `@types/node`. |
+| audit-ci | vulnerability gate for pnpm | `7.1.0` | Reads `pnpm audit`; config `audit-ci.jsonc`. |
+| npm-check-updates | dependency currency check | `23.1.0` | `ncu` for deliberate upgrades; not a silent auto-bump. |
+| Vitest | unit/component test runner | `5.0.1` | `pnpm add -D -E vitest@5.0.1`. |
+| @vitest/coverage-v8 | coverage + thresholds | `5.0.1` | Must match Vitest exactly (`peer vitest@5.0.1`). |
+| @testing-library/react | component tests | `16.3.3` | RTL for React 19. |
+| @testing-library/user-event | realistic event simulation | `14.6.7` | Use instead of `fireEvent`. |
+| @testing-library/jest-dom | DOM matchers | `7.0.1` | Import in `vitest.setup.ts`. |
+| jsdom | DOM environment | `30.1.0` | Required for axe; do NOT use happy-dom (see traps). |
+| axe-core | a11y engine | `4.13.0` | Direct, or via jest-axe. |
+| jest-axe | axe matchers for Vitest `expect` | `11.0.0` | Framework-agnostic matchers; `vitest-axe` on npm is stale (see traps). |
+| @playwright/test | end-to-end tests | `1.63.0` | `pnpm exec playwright install --with-deps chromium`. |
+| @axe-core/playwright | a11y assertions in E2E (incl. color contrast) | `4.13.0` | Peer `playwright-core >= 1.0.0`. |
+| Vite | build + dev server | `8.3.0` | Rolldown is the only bundler; Rollup/esbuild options are renamed/deprecated. |
+| @vitejs/plugin-react | React fast-refresh (Oxc) | `6.1.1` | Peer `vite ^8`. Babel removed; React Compiler is opt-in via `reactCompilerPreset`. |
+| size-limit + @size-limit/file | hard bundle budgets | `size-limit@14.0.0`, `@size-limit/file@14.0.0` | Engines include `^24.5.0`. |
+| rollup-plugin-visualizer | chunk/module analysis | `7.1.1` | Peer includes `rolldown ^1` (Vite 8 compatible). |
+| globals | browser globals for ESLint flat config | `17.12.0` | `languageOptions.globals: globals.browser`. |
+| @eslint/js | core recommended preset | `10.0.1` | Pairs with ESLint 10. |
+
+**Archived / deprecated / superseded in 2026 — never recommend:** `eslint-plugin-import@2.32.0`
+(stale, peer stops at ESLint 9 → use `eslint-plugin-import-x`), `ts-prune@0.10.3` and
+`depcheck@1.4.7` (superseded by Knip), `vitest-axe@0.1.0` (npm build 4 years old, no Vitest 5),
+`better-npm-audit@3.11.0` (npm-only; use `audit-ci`), `.eslintrc*` (removed in ESLint 10),
+Prettier 4 (alpha only). Biome is rejected: it cannot run type-aware `typescript-eslint` rules
+or the React Compiler rules this stack depends on.
+
+## Strict Baseline Config
+
+Create these files at the repo root. Exact strict settings:
+
+**`.nvmrc` / `.node-version`** — both contain the single line `24.20.0`.
+
+**`package.json`** — pinning + script surface (all scripts fail fast). Run `corepack prepare pnpm@12.5.1 --activate` to generate the `+sha512…` hash; do not hand-edit it:
+```jsonc
+{
+  "packageManager": "pnpm@12.5.1",
+  "engines": { "node": ">=24.20.0 <25", "pnpm": ">=12.5.1" },
+  "devDependencies": {
+    "typescript": "npm:@typescript/typescript6@6.0.2",
+    "typescript-7": "npm:typescript@7.0.2"
+  },
+  "pnpm": {
+    "onlyBuiltDependencies": [],
+    "peerDependencyRules": { "allowedVersions": { "eslint-plugin-jsx-a11y>eslint": "10" } }
+  },
+  "scripts": {
+    "format:check": "prettier --check .",
+    "lint": "eslint . --max-warnings=0 --cache",
+    "typecheck": "tsc --noEmit",
+    "typecheck:native": "node ./node_modules/typescript-7/bin/tsc --noEmit",
+    "arch": "steiger ./src --fail-on-warnings",
+    "graph": "depcruise --config .dependency-cruiser.cjs src",
+    "deadcode": "knip --treat-config-hints-as-errors",
+    "audit": "audit-ci --config ./audit-ci.jsonc",
+    "test": "vitest run --coverage",
+    "build": "vite build",
+    "size": "size-limit",
+    "e2e": "playwright test"
+  }
+}
+```
+
+**`.npmrc`** — the actual strict install policy:
+```ini
+strict-peer-dependencies=true
+auto-install-peers=false
+save-exact=true
+verify-deps-before-run=true
+```
+
+**`tsconfig.json`** — TS 6/7 defaults are already strict (`strict`, `module: esnext`,
+`target: es2025`), but pin them explicitly and add the non-default strict flags; also
+compensate for the new `types: []` and `rootDir: .` defaults:
+```jsonc
+{
+  "compilerOptions": {
+    "strict": true,
+    "noUncheckedIndexedAccess": true,
+    "exactOptionalPropertyTypes": true,
+    "noImplicitOverride": true,
+    "noPropertyAccessFromIndexSignature": true,
+    "noImplicitReturns": true,
+    "noFallthroughCasesInSwitch": true,
+    "noUnusedLocals": true,
+    "noUnusedParameters": true,
+    "allowUnreachableCode": false,
+    "allowUnusedLabels": false,
+    "useUnknownInCatchVariables": true,
+    "verbatimModuleSyntax": true,
+    "isolatedModules": true,
+    "moduleDetection": "force",
+    "noUncheckedSideEffectImports": true,
+    "forceConsistentCasingInFileNames": true,
+    "module": "esnext",
+    "moduleResolution": "bundler",
+    "target": "es2025",
+    "lib": ["ES2025", "DOM", "DOM.Iterable"],
+    "types": ["vite/client"],
+    "rootDir": "./src",
+    "noEmit": true,
+    "skipLibCheck": true,
+    "jsx": "react-jsx"
+  },
+  "include": ["src"]
+}
+```
+`tsconfig.node.json` covers `vite.config.ts`, `eslint.config.mjs`, `playwright.config.ts`
+with `"types": ["node"]` and `"lib": ["ES2025"]`.
+
+**`eslint.config.mjs`** — flat config, typed linting via `projectService` (NOT the removed
+`parserOptions.project`), strict variants, compiler rules last-but-one, Prettier last:
+```js
+// @ts-check
+import js from '@eslint/js';
+import { defineConfig } from 'eslint/config';
+import tseslint from 'typescript-eslint';
+import reactHooks from 'eslint-plugin-react-hooks';
+import jsxA11y from 'eslint-plugin-jsx-a11y';
+import reactRefresh from 'eslint-plugin-react-refresh';
+import vitest from '@vitest/eslint-plugin';
+import prettier from 'eslint-config-prettier';
+
+export default defineConfig([
+  { ignores: ['dist', 'coverage', 'playwright-report', 'test-results'] },
+  {
+    files: ['**/*.{ts,tsx}'],
+    extends: [
+      js.configs.recommended,
+      tseslint.configs.strictTypeChecked,
+      tseslint.configs.stylisticTypeChecked,
+      reactHooks.configs.flat['recommended-latest'],   // all React Compiler rules on
+      jsxA11y.flatConfigs.strict,
+    ],
+    languageOptions: {
+      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
+    },
+    plugins: { 'react-refresh': reactRefresh },
+    rules: {
+      'react-refresh/only-export-components': ['error', { allowConstantExport: true }],
+      '@typescript-eslint/no-explicit-any': 'error',
+      '@typescript-eslint/no-unsafe-assignment': 'error',
+      '@typescript-eslint/explicit-module-boundary-types': 'error',
+    },
+  },
+  {
+    files: ['src/**/*.{test,spec}.{ts,tsx}'],
+    extends: [vitest.configs.recommended],
+    rules: { 'vitest/no-focused-tests': 'error', 'vitest/no-disabled-tests': 'error' },
+  },
+  prettier, // MUST stay last
+]);
+```
+`reactHooks.configs.flat['recommended-latest']` enables the compiler rules
+`react-hooks/purity`, `/immutability`, `/refs`, `/set-state-in-effect`,
+`/set-state-in-render`, `/preserve-manual-memoization`, `/static-components`,
+`/incompatible-library` — use `configs.flat.recommended` instead if the compiler is off.
+
+**`.prettierrc`** — `{ "singleQuote": true, "trailingComma": "all", "printWidth": 100 }`
+plus `.prettierignore` (`dist`, `coverage`, lockfile, `playwright-report`).
+Run it as `prettier --check .` — never `prettier --write` inside a gate.
+
+**`steiger.config.ts`** — FSD-native rules; keep warnings fatal:
+```ts
+import { defineConfig } from 'steiger';
+import fsd from '@feature-sliced/steiger-plugin';
+export default defineConfig([...fsd.configs.recommended]);
+```
+Run `steiger ./src --fail-on-warnings`. This enforces `fsd/public-api` (every slice must
+export through `index.ts`), `fsd/forbidden-imports` (no imports from higher layers, no
+cross-imports between same-layer slices), `fsd/no-public-api-sidestep` (no deep imports
+into a slice's internals), `fsd/no-reserved-folder-names`, `fsd/insignificant-slice`.
+
+**`.dependency-cruiser.cjs`** — graph hygiene that Steiger does not cover:
+```js
+module.exports = {
+  forbidden: [
+    { name: 'no-circular', severity: 'error', from: {}, to: { circular: true } },
+    { name: 'no-orphans', severity: 'error', from: { orphan: true }, to: {} },
+    { name: 'not-to-unresolvable', severity: 'error', from: {}, to: { couldNotResolve: true } },
+  ],
+  options: {
+    tsConfig: { fileName: 'tsconfig.json' },
+    doNotFollow: { path: 'node_modules' },
+    tsPreCompilationDeps: true,
+  },
+};
+```
+Run `depcruise --config .dependency-cruiser.cjs src`.
+
+**`knip.json`** — dead code + unused deps; make the FSD public API the entry points:
+```jsonc
+{
+  "entry": ["src/main.tsx", "src/app/**/index.ts"],
+  "project": ["src/**/*.{ts,tsx}"],
+  "ignoreDependencies": [],
+  "rules": { "files": "error", "dependencies": "error", "unlisted": "error", "exports": "error", "types": "error" }
+}
+```
+Run `knip --treat-config-hints-as-errors`. Do NOT use `--strict` on a single-package SPA —
+it flips production mode and stops reporting unused `devDependencies`.
+
+**`vitest.config.ts`** — Vitest 5, jsdom (axe-safe), thresholds are the gate:
+```ts
+import { defineConfig } from 'vitest/config';
+export default defineConfig({
+  test: {
+    environment: 'jsdom',
+    setupFiles: ['./vitest.setup.ts'],
+    globals: true,
+    restoreMocks: true,
+    clearMocks: true,
+    unstubGlobals: true,
+    coverage: {
+      provider: 'v8',
+      include: ['src/**/*.{ts,tsx}'],
+      exclude: ['src/**/*.d.ts', 'src/main.tsx', 'src/**/index.ts'],
+      reporter: ['text', 'lcov'],
+      thresholds: {
+        lines: 85, functions: 85, branches: 80, statements: 85,
+        perFile: { lines: 70, functions: 70, branches: 60, statements: 70 },
+      },
+    },
+  },
+});
+```
+**`vitest.setup.ts`** — `import '@testing-library/jest-dom/vitest';` then
+`import { toHaveNoViolations } from 'jest-axe'; expect.extend(toHaveNoViolations);`
+Component tests use `@testing-library/react` + `@testing-library/user-event` and query by
+role (`getByRole`, `findByRole`); a11y assertions call `axe(container)` from `jest-axe`.
+
+**`playwright.config.ts`** — `forbidOnly: !!process.env.CI`, `retries: process.env.CI ? 2 : 0`,
+`workers: process.env.CI ? 1 : undefined`, `use: { trace: 'on-first-retry' }`,
+`webServer: { command: 'vite preview --port 4173', url: 'http://localhost:4173' }`.
+E2E a11y uses `AxeBuilder` from `@axe-core/playwright`.
+
+**`size-limit.config.mjs`** — hard budgets, checked after `vite build`:
+```js
+export default [
+  { path: 'dist/assets/index-*.js', limit: '180 kB', gzip: true },
+  { path: 'dist/assets/*.css', limit: '40 kB', gzip: true },
+];
+```
+
+**`audit-ci.jsonc`**:
+```jsonc
+{ "package-manager": "pnpm", "audit-level": "high", "allowlist": [], "report-type": "important" }
+```
+
+**`vite.config.ts`** — Vite 8 names (see traps), analyzer, no sourcemaps in prod:
+```ts
+import { defineConfig } from 'vite';
+import react from '@vitejs/plugin-react';
+import { visualizer } from 'rollup-plugin-visualizer';
+export default defineConfig({
+  plugins: [react(), visualizer({ filename: 'dist/stats.html', gzipSize: true, brotliSize: true })],
+  build: {
+    sourcemap: false,
+    chunkSizeWarningLimit: 500,
+    rolldownOptions: { output: { manualChunks: (id) => (id.includes('node_modules') ? 'vendor' : undefined) } },
+  },
+});
+```
+
+## Mandatory Gate Order
+
+Fail-fast, cheapest first. Run each as its own CI step so the first failure stops the chain.
+
+1. `corepack enable && node --version && pnpm --version` — preflight; expect `v24.20.0` / `12.5.1`.
+2. `pnpm install --frozen-lockfile --strict-peer-dependencies` — immutable install; fails on drift or phantom peers.
+3. `pnpm exec lockfile-lint --path pnpm-lock.yaml --type pnpm --allowed-hosts npm --validate-https` — lockfile provenance and HTTPS check; fails on non-HTTPS or unexpected registry.
+4. `pnpm exec prettier --check .`
+5. `pnpm exec eslint . --max-warnings=0 --cache`
+6. `pnpm exec tsc --noEmit` — TypeScript 6.0.2 parity check (same engine typescript-eslint uses; the `typescript` package is the v6 alias so the parser peer `>=4.8.4 <6.1.0` resolves).
+7. `node ./node_modules/typescript-7/bin/tsc --noEmit` — TypeScript 7 native typecheck (fast; explicit path into the aliased `typescript-7` package because pnpm exposes no `tsc6` bin).
+8. `pnpm exec steiger ./src --fail-on-warnings`
+9. `pnpm exec depcruise --config .dependency-cruiser.cjs src`
+10. `pnpm exec knip --treat-config-hints-as-errors`
+11. `pnpm exec audit-ci --config ./audit-ci.jsonc`
+12. `pnpm exec vitest run --coverage`
+13. `pnpm exec vite build`
+14. `pnpm exec size-limit`
+15. `pnpm exec playwright test`
+16. `pnpm dlx npm-check-updates@23.1.0 --errorLevel 1` — optional currency report (non-blocking owner).
+
+## Hallucination Traps to Block
+
+Concrete failure modes an AI generates on this exact stack, and the gate step that catches each:
+
+| Trap (what an AI writes from stale memory) | Why it is wrong in 2026 | Caught by |
+| --- | --- | --- |
+| `"typescript": "^5.x"` or `"^7.0.2"` in devDependencies | typescript-eslint 8.70.1 peer is `>=4.8.4 <6.1.0`; TS 7 support issue #12518 was closed *not planned*. TS 7 breaks the typed-lint program (`getWatchProgramsForProjects`). | Step 2 (peer resolution) and Step 4 (parser crash) |
+| Running only `tsc --noEmit` and assuming lint covers types | Vite 8 does not typecheck on `vite build`; type errors ship silently. | Steps 5 + 6 before build |
+| `.eslintrc.json` / `"eslintConfig"` in package.json / `--ext .ts` | Legacy config was removed in ESLint 10; `--ext` was removed with flat config. | Step 4 fails immediately |
+| `parserOptions: { project: true }` | Deprecated for typed linting; current form is `parserOptions.projectService: true`. | Step 4 (type-aware rules silently stop firing if mis-set) |
+| `setupFilesAfterEach`, `eslint-env mocks`, `--rulesdir` | Removed/erroring in ESLint 10. | Step 4 |
+| `build.rollupOptions` / `transformWithEsbuild` / `esbuild: {}` in Vite config | Renamed in Vite 8: `build.rolldownOptions`, `transformWithOxc`, `oxc: {}`. Old names warn (and will be removed); `worker.rollupOptions` → `worker.rolldownOptions`. | Step 12 (deprecation warning + build) |
+| Object-form `manualChunks: { vendor: [...] }` | Rolldown does not support the object form — only the function form. | Step 12 (build error) |
+| `import { x } from '@/features/auth/ui/LoginForm'` (deep slice import) | Violates FSD public API and `no-public-api-sidestep`. | Step 7 |
+| `features/cart` importing `features/product` | Same-layer cross-import violates the FSD import rule. | Step 7 (`fsd/forbidden-imports`) |
+| Component test env set to `happy-dom` | axe-core's `Node.prototype.isConnected` check breaks under happy-dom, so a11y assertions pass vacuously. | Step 11 with `environment: 'jsdom'` |
+| Importing `vitest-axe` and calling `.toHaveNoViolations()` | npm `vitest-axe` is `0.1.0` (4 years old); matchers may be undefined → tests pass without asserting. | Step 11 (`jest-axe` + explicit `expect.extend`) |
+| Fake timers left on around `axe()` | axe times out when `setTimeout` is mocked; results become empty and pass. | Step 11 (axe assertions) |
+| `@testing-library/react` queried by `container.querySelector` | Bypasses a11y roles and hides broken markup. | Step 4 (`jsx-a11y`) + Step 11 (role queries). |
+| `expect(true).toBe(true)` / snapshot-only tests to raise coverage | Coverage thresholds measure lines executed, not assertions; per-file thresholds limit the damage. | Step 11 (`coverage.thresholds.perFile`) |
+| `tsconfig` relying on `types` auto-loading all `@types/*` | TypeScript 6.0 changed `types` default to `[]`; globals vanish (`process`, `describe`) without an explicit list. | Steps 5 + 6 |
+| `"outDir": "dist"` without `"rootDir": "./src"` | TS 6.0 defaults `rootDir` to the tsconfig dir → emit lands in `dist/src/`. | Step 5/6 emit paths, build smoke |
+| `moduleResolution: "node"`, `target: "es5"`, `assert { type: 'json' }` | ES5 deprecated; `assert` replaced by `with` in TS 6/7; `node` resolution deprecated. | Steps 5 + 6 |
+| Adding a dep to `package.json` without installing, or leaving `let x` unused | Drift between manifest and code. | Step 9 (`knip` `unlisted`, `dependencies`, `exports`) |
+| Committing `pnpm-lock.yaml` changes while `strict-peer-dependencies=false` | Phantom/duplicated packages, non-reproducible CI. | Step 2 |
+| `size-limit` config pointing at `dist/index.js` after a Vite rename | Budgets silently check a non-existent file. | Step 13 (size-limit errors on missing path) |
+| `playwright test` without `forbidOnly` | A committed `.only` skips the rest of the suite and CI stays green. | Step 14 (`forbidOnly: !!process.env.CI`) |
+
+## Evidence to Record
+
+Paste the raw command output into the task's Verification Evidence block. Every row is a
+separate gate; `$?` must be `0` for PASS.
+
+| Gate | Exact command | Expected result | Exit code |
+| --- | --- | --- | --- |
+| Install | `pnpm install --frozen-lockfile --strict-peer-dependencies` | `Lockfile is up to date` / `Done`; no peer errors | 0 |
+| Format | `pnpm exec prettier --check .` | `All matched files use Prettier code style!` | 0 |
+| Lint | `pnpm exec eslint . --max-warnings=0 --cache` | no output; zero warnings | 0 |
+| Typecheck (TS6) | `pnpm exec tsc --noEmit` | no diagnostics | 0 |
+| Typecheck (TS7) | `node ./node_modules/typescript-7/bin/tsc --noEmit` | no diagnostics | 0 |
+| FSD | `pnpm exec steiger ./src --fail-on-warnings` | `✔ No problems found` (0 errors, 0 warnings) | 0 |
+| Graph | `pnpm exec depcruise --config .dependency-cruiser.cjs src` | `no dependency violations found` | 0 |
+| Dead code | `pnpm exec knip --treat-config-hints-as-errors` | `No issues found` | 0 |
+| Vulns | `pnpm exec audit-ci --config ./audit-ci.jsonc` | no advisories at/above `high` | 0 |
+| Unit + coverage | `pnpm exec vitest run --coverage` | all suites pass; coverage table ≥ thresholds | 0 |
+| Build | `pnpm exec vite build` | `built in <n>ms`; `dist/index.html` + hashed assets exist | 0 |
+| Budgets | `pnpm exec size-limit` | each entry `Size limit: Passed` | 0 |
+| E2E | `pnpm exec playwright test` | `N passed` (no skipped-only run) | 0 |
+
+Record also: `node --version` (`v24.20.0`), `pnpm --version` (`12.5.1`), and
+`pnpm exec tsc --version` (`Version 6.0.2`). If any gate is intentionally waived, record
+the waiver, the owner, and an expiry date in the task file.
+
+<!-- sources -->
+- npm registry dist-tags (`https://registry.npmjs.org/-/package/<pkg>/dist-tags`) and `https://registry.npmjs.org/<pkg>/latest` for every pinned package
+- GitHub Releases API (`https://api.github.com/repos/<owner>/<repo>/releases/latest`) for TypeScript, ESLint, typescript-eslint, Vite, Vitest, Playwright, Knip, eslint-plugin-boundaries, Prettier, Node
+- TypeScript 7: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0 , https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-rc , https://www.infoq.com/news/2026/08/typescript-7-released
+- TypeScript 6.0 breaking changes: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0 , https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html
+- typescript-eslint TS7 gap: https://github.com/typescript-eslint/typescript-eslint/issues/12518 , https://github.com/typescript-eslint/typescript-eslint/releases , https://typescript-eslint.io/users/configs , https://typescript-eslint.io/linting/typed-linting/
+- ESLint 10: https://eslint.org/blog/2026/02/eslint-v10.0.0-released , https://eslint.org/docs/latest/use/migrate-to-10.0.0 , https://eslint.org/blog/2026/06/eslint-v10.6.0-released , https://eslint.org/docs/latest/versions/
+- react-hooks v7 flat/compiler configs: https://github.com/react/react/tree/main/packages/eslint-plugin-react-hooks , https://github.com/facebook/react/blob/main/packages/eslint-plugin-react-hooks/CHANGELOG.md
+- jsx-a11y ESLint 10: https://github.com/jsx-eslint/eslint-plugin-jsx-a11y , https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/issues/1075 , https://dev.to/booyaka101/eslint-plugin-jsx-a11y-says-it-doesnt-support-eslint-10-it-does-380f
+- eslint-plugin-import replacement: https://github.com/un-ts/eslint-plugin-import-x , https://github.com/e18e/module-replacements/blob/main/docs/modules/eslint-plugin-import.md
+- FSD import rules: https://feature-sliced.design/docs/guides/issues/cross-imports , https://github.com/feature-sliced/steiger , https://github.com/feature-sliced/steiger/blob/master/packages/steiger-plugin-fsd/src/forbidden-imports/README.md
+- dependency-cruiser rules: https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md
+- Knip: https://knip.dev/overview/getting-started , https://knip.dev/reference/cli
+- Supply chain: https://github.com/IBM/audit-ci , https://github.com/lirantal/lockfile-lint (pnpm FAQ) , https://github.com/jeemok/better-npm-audit , https://pnpm.io/npmrc
+- Vitest 5 + coverage: https://vitest.dev/config/coverage , https://vitest.dev/guide/migration , https://traceary.com/vitest
+- Accessibility in tests: https://github.com/chaance/vitest-axe , https://github.com/nickcolley/jest-axe , https://www.javascript-testing.com/component-integration-testing-frameworks/accessibility-testing-for-components/automating-axe-accessibility-checks-in-vitest
+- Playwright 1.63.0: https://github.com/microsoft/playwright/releases
+- Vite 8: https://vite.dev/blog/announcing-vite8 , https://vite.dev/blog/announcing-vite8-1 , https://vite.dev/config/build-options , https://github.com/vitejs/vite/blob/main/packages/vite/CHANGELOG.md
+- Node LTS: https://nodejs.org/en/blog/release , https://endoflife.date/nodejs
+- Bundle budgets: https://github.com/ai/size-limit , https://github.com/btd/rollup-plugin-visualizer
+
 ## Currency Baseline
 
 - **React 19:** Baseline React 19 (`useActionState`, `useOptimistic`, ref-as-prop); with React Compiler v1.0 available, keep manual `memo`/`useMemo`/`useCallback` to profiled bottlenecks only.
diff --git a/skill-templates/spring-boot/SKILL.md b/skill-templates/spring-boot/SKILL.md
index 4d8a3bb..09a37ee 100644
--- a/skill-templates/spring-boot/SKILL.md
+++ b/skill-templates/spring-boot/SKILL.md
@@ -108,6 +108,300 @@ Create a single `@RestControllerAdvice` class that catches all exceptions.
 - Prefer `Mockito` for mocking; never use `PowerMock`.
 - Use `Testcontainers` for database-dependent integration tests.
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+> Stack baseline (verified September 2026): **Java 25 LTS** (latest feature release is 27; 25 is
+> the LTS and the newest version inside Spring Boot 4.1's supported range), **Spring Boot 4.1.1**
+> (Spring Framework 7.0.9, Jakarta EE 11, Servlet 6.1). Released 2026-08-20.
+> This section assumes the DDD + hexagonal layout and the bans already declared in
+> `skill-templates/spring-boot/SKILL.md` (pure `domain/`, `@RequiredArgsConstructor`,
+> MapStruct `@Mapper(componentModel="spring")`, injected `Clock`, no `LocalDateTime` in DTOs,
+> Flyway/Liquibase only, no `hibernate.ddl-auto=update`). The SKILL's "Currency Baseline"
+> (Boot 3.x / Java 17) is stale for 2026 and should be bumped when this gate is adopted.
+
+## Required Toolchain
+
+| Tool | Purpose | Minimum version to pin | Install / availability note |
+| --- | --- | --- | --- |
+| JDK (Temurin/Adoptium) | Runtime + compiler | **25** (LTS) | Toolchain-managed; Adoptium latest LTS = 25, latest feature = 27 (non-LTS, outside Boot 4.1 support). Reject 27. |
+| Gradle | Build, locking, verification | **9.7.1** | Runs on JVM 17–26; toolchain support for 25 from 9.1.0, for 26 from 9.4.0. |
+| Spring Boot | Framework | **4.1.1** | `org.springframework.boot` plugin; Maven 3.6.3+ / Gradle 8.14+/9.x. Reject 4.2.0-M1 (milestone) and 3.5.x (final 3.x line). |
+| Spotless | Formatting gate | **3.10.2** | Plugin id `com.diffplug.spotless`; lib is 4.10.2 (plugin numbering differs). |
+| google-java-format | Java formatter engine | **1.36.1** | Resolved by Spotless; never invoke the raw CLI (see traps). |
+| Error Prone | Compile-time bug/semantic lint | **2.50.0** | Must run on JDK 21+; last JDK-17 line is 2.42.0. Pin `error_prone_core`. |
+| NullAway | Nullness checker (Error Prone plugin) | **0.14.1** | Runs under Error Prone; JSpecify mode enabled. |
+| JSpecify | Nullness annotations | **1.0.1** | `org.jspecify:jspecify`. Boot 4 ships JSpecify annotations; `org.springframework.lang.Nullable` is gone. |
+| SpotBugs | Bytecode analysis | **4.10.4** | `com.github.spotbugs:spotbugs`. |
+| find-sec-bugs | SpotBugs security detectors | **1.14.0** | `com.h3xstream.findsecbugs:findsecbugs-plugin`. Maintained, low cadence. |
+| ArchUnit | Layer / hexagon / cycle rules | **1.5.0** | `com.tngtech.archunit:archunit-junit5`. Winner for hexagonal enforcement. |
+| Spring Modulith | Module-cycle verification (optional) | **2.1.1** | Aligns with Boot 4.1; secondary — does not enforce layer direction. |
+| osv-scanner | SCA / dependency vulnerabilities | **2.6.0** | V2 beta, OSV.dev + osv-scalibr; no NVD API key needed. |
+| gitleaks | Secret scanning | **8.30.1** | Feature-complete / security-patch-only; successor is Betterleaks (see Deprecated). |
+| JUnit | Test framework | **6.0.3** (Boot-managed) / 6.1.3 latest | Java 17 + Kotlin 2.1 baseline; single version for Platform/Jupiter/Vintage. |
+| Testcontainers | Real-dependency integration tests | **2.0.5** | Boot 4.1 manages 2.0.5; JUnit 4 support removed; classes relocated. |
+| AssertJ | Fluent assertions | **3.27.7** | Boot-managed. 4.0.0-M1 is a milestone — do not pin. |
+| jqwik | Property-based tests | **1.10.1** | `net.jqwik:jqwik`. |
+| PIT (pitest) | Mutation testing | **1.15.0** (Gradle plugin) / 1.30.0 core | `info.solidsoft.pitest` + `org.pitest:pitest-junit5-plugin:1.2.3`. |
+| JaCoCo | Coverage thresholds | **0.8.15** | Gradle built-in `jacoco` plugin; pin tool version. |
+| Flyway | Schema migration + validate | **12.4.0** | Use the Boot-managed runtime version (12.4.0), NOT latest 13.7.0. |
+| Liquibase | Schema migration + validate | **5.0.3** | Use Boot-managed 5.0.3, NOT latest 5.0.4. |
+| MapStruct | Compile-time DTO mapping | **1.6.3** | 1.7.0 is Beta only. Add `lombok-mapstruct-binding:0.2.0`. |
+| Lombok | Boilerplate (`@RequiredArgsConstructor`) | **1.18.46** | Boot-managed; latest 1.18.48. Use Boot's managed value. |
+| Mockito | Mocking | **5.23.0** | Boot-managed. PowerMock is banned (dead project). |
+
+## Strict Baseline Config
+
+Create these files. Each line is a setting that makes the tool strict, not advisory.
+
+**`gradle/wrapper/gradle-wrapper.properties`** — pin the wrapper and its checksum:
+
+```properties
+distributionUrl=https\://services.gradle.org/distributions/gradle-9.7.1-bin.zip
+# Fetch the expected hash: curl -s https://services.gradle.org/distributions/gradle-9.7.1-bin.zip.sha256 | cut -d' ' -f1
+distributionSha256Sum=acd53f1edaf02f1a8ff99879f8a34b302661a057d9b063ae9e35b552f804d20a
+```
+
+**`gradle/libs.versions.toml`** — single source of truth for every version above. No version
+literals anywhere else; this is what makes the gate AI-auditable.
+
+**`settings.gradle.kts`** — dependency-confusion defense (repository content filtering) plus
+fail-fast on repositories that are not allowlisted:
+
+```kotlin
+dependencyResolutionManagement {
+    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
+    repositories {
+        mavenCentral {
+            content {
+                includeGroupByRegex("org\\.springframework.*"); includeGroupByRegex("com\\.google.*")
+                includeGroupByRegex("org\\.jspecify"); includeGroupByRegex("net\\.jqwik")
+                includeGroupByRegex("com\\.tngtech.*"); includeGroupByRegex("org\\.owasp.*")
+                includeGroupByRegex("org\\.flywaydb.*"); includeGroupByRegex("org\\.liquibase.*")
+                includeGroupByRegex("org\\.testcontainers.*"); includeGroupByRegex("org\\.assertj.*")
+                includeGroupByRegex("org\\.mockito.*"); includeGroupByRegex("org\\.mapstruct.*")
+                includeGroupByRegex("tools\\.jackson.*"); includeGroupByRegex("com\\.fasterxml.*")
+                includeGroupByRegex("io\\.micrometer.*"); includeGroupByRegex("org\\.hibernate.*")
+                includeGroupByRegex("org\\.junit.*")
+            }
+        }
+        gradlePluginPortal()
+    }
+}
+```
+
+**`gradle/verification-metadata.xml`** — generated, then committed; build fails on any
+checksum/PGP mismatch (dependency verification, the strongest supply-chain gate):
+
+```bash
+./gradlew --write-verification-metadata sha256,pgp --write-locks help
+```
+
+**`gradle.lockfile`** — dependency locking for every configuration:
+
+```kotlin
+// in build.gradle.kts
+dependencyLocking { lockAllConfigurations() }
+```
+
+**`build.gradle.kts`** — compiler + static analysis + toolchain. Key strict settings:
+
+```kotlin
+java {
+    toolchain { languageVersion.set(JavaLanguageVersion.of(25)) }
+}
+dependencies {
+    errorprone("com.google.errorprone:error_prone_core:2.50.0")
+    testImplementation("com.tngtech.archunit:archunit-junit5:1.5.0")
+    testImplementation("org.jspecify:jspecify:1.0.1")
+}
+tasks.withType<JavaCompile>().configureEach {
+    options.encoding = "UTF-8"
+    options.compilerArgs.addAll(listOf(
+        "--release", "25", "-Xlint:all", "-Werror", "-parameters", "-proc:full",
+        "-XDcompilePolicy=simple", "--should-stop=ifError=FLOW"
+    ))
+    options.errorprone {
+        disableWarningsInGeneratedCode.set(true)
+        check("NullAway", CheckSeverity.ERROR)
+        option("NullAway:AnnotatedPackages", "com.company.project")
+        option("NullAway:JSpecifyMode", "true")
+        option("NullAway:CheckOptionalEmptiness", "true")
+    }
+}
+tasks.withType<Test>().configureEach { useJUnitPlatform(); failFast = true }
+```
+
+**Per-tool strict settings:**
+
+- Spotless: `spotless { java { googleJavaFormat("1.36.1").reflowLongStrings(); removeUnusedImports(); importOrder(); formatAnnotations(); forbidWildcardImports() } }` and `check` depends on `spotlessCheck`.
+- Checkstyle (if kept): `checkstyle { toolVersion = "14.1.0"; maxErrors = 0; maxWarnings = 0; configFile = file("config/checkstyle/checkstyle.xml") }`.
+- PMD (if kept): `pmd { toolVersion = "7.27.0"; isIgnoreFailures = false }`.
+- SpotBugs: `spotbugs { toolVersion = "4.10.4"; effort = Effort.MAX; reportLevel = Confidence.LOW; excludeFilter = file("config/spotbugs/spotbugs-exclude.xml") }`; plugin `spotbugsPlugins("com.h3xstream.findsecbugs:findsecbugs-plugin:1.14.0")`.
+- JaCoCo: `tasks.jacocoTestCoverageVerification { violationRules { rule { limit { counter = "LINE"; value = "COVEREDRATIO"; minimum = "0.80".toBigDecimal() } } rule { limit { counter = "BRANCH"; value = "COVEREDRATIO"; minimum = "0.70".toBigDecimal() } } } }`.
+- PIT: `pitest { mutationThreshold.set(70); failWhenNoMutations.set(true); outputFormats.set(setOf("XML","HTML")); timestampedReports.set(false) }`.
+- Flyway/Liquibase: `spring.flyway.validate-on-migrate=true`; `spring.liquibase.enabled=true`; run `flywayValidate` / `liquibaseValidate` as gates.
+- Config validation: every `@ConfigurationProperties` class gets `@Validated` + Jakarta `@NotNull`/`@Min`; add `org.springframework.boot:spring-boot-properties-migrator` only during upgrades.
+- `.gitleaks.toml`: `[extend] useDefault = true` plus an allowlist only for test fixtures.
+- `osv-scanner.toml`: `[[IgnoredVulns]]` with an `id`, `ignoreUntil`, and `reason` — no bare suppressions.
+- `config/archunit/archunit.properties`: `archunit.freeze.store.default.path=archunit_store` (only if using frozen rules).
+
+**Maven fallback (only if the org mandates it):** pin **Maven 3.9.16** via
+`.mvn/wrapper/maven-wrapper.properties` (`distributionUrl=...apache-maven-3.9.16-bin.zip`,
+`distributionSha256Sum=PUT_MAVEN_HASH_FETCHED_VIA_CURL_FROM_SHA512_URL_ABOVE`), set `project.build.outputTimestamp` for reproducible builds, and
+use `maven-enforcer-plugin:3.6.3` with `requireUpperBoundDeps`, `dependencyConvergence`,
+`banDuplicatePomDependencyVersions`, `requireReleaseDeps`, and `requireMavenVersion [3.6.3,)`.
+Maven cannot natively lock/verify transitive artifacts the way Gradle does, and **Maven 4.0.0 is
+still 4.0.0-rc-6 (not GA)** — that is why Gradle wins.
+
+## Mandatory Gate Order
+
+Run in this exact order; each step fails the build (non-zero exit) before the next is allowed.
+
+1. `./gradlew --no-daemon --version | grep -qE '^Gradle 9\.7\.1$'`
+2. `./gradlew --no-daemon spotlessCheck`
+3. `./gradlew --no-daemon compileJava compileTestJava`
+4. `./gradlew --no-daemon test --tests 'com.company.project.ArchitectureTest'`
+5. `./gradlew --no-daemon test checkstyleMain pmdMain spotbugsMain`
+6. `gitleaks git --redact --exit-code 1 --report-format sarif --report-path build/gitleaks.sarif`
+7. `osv-scanner scan source --licenses -r .`
+8. `./gradlew --no-daemon integrationTest`
+9. `./gradlew --no-daemon jacocoTestCoverageVerification`
+10. `./gradlew --no-daemon pitest`
+11. `./gradlew --no-daemon flywayValidate`
+12. Start the app, then check readiness: `(./gradlew --no-daemon bootRun &>/tmp/bootrun.log & echo $! > /tmp/bootrun.pid; sleep 20; curl --fail --silent http://localhost:8080/actuator/health/readiness | jq -e '.status=="UP"'; rc=$?; kill $(cat /tmp/bootrun.pid); exit $rc)` — if the app cannot start locally, treat readiness as a post-deploy check and verify it against the deployed environment instead; never pass this step without a live readiness response.
+
+Notes: step 1 also implicitly verifies the wrapper checksum. Step 3 is the Error Prone + NullAway
+gate. Step 11 exits non-zero when vulnerabilities are present by default. After the first
+resolution, add `--offline` to steps 2–9 in CI to forbid surprise remote changes.
+
+## Hallucination Traps to Block
+
+| AI failure mode | The check that catches it |
+| --- | --- |
+| Writes `javax.validation.*` / `javax.persistence.*` (pre-Boot-3 memory). | Compile fails; add ArchUnit `noClasses().should().dependOnClassesThat().resideInAPackage("javax..")`. |
+| Restores removed Boot mock annotations `@MockBean` / `@SpyBean`. | Compile fails in Boot 4; add `forbiddenapis`/ArchUnit ban on `org.springframework.boot.test.mock.mockito.*`. Replace with `@MockitoBean` / `@MockitoSpyBean`. |
+| Uses `spring-boot-starter-web` (deprecated → `spring-boot-starter-webmvc`). | `./gradlew dependencyInsight --dependency spring-boot-starter-web`; CI fails when the deprecated starter is a direct dependency. |
+| Imports Jackson 2 types (`com.fasterxml.jackson.databind.*`) under Boot 4's Jackson 3. | Compile fails; ban `com.fasterxml.jackson` via `forbiddenapis`. Boot 4 uses `tools.jackson.*`. |
+| Pins Flyway 13.7.0 / Liquibase 5.0.4 while Boot 4.1.1 manages 12.4.0 / 5.0.3. | `./gradlew dependencyInsight --dependency flyway-core`; `resolutionStrategy.failOnVersionConflict()` + lockfile. |
+| Adds `junit-platform-runner` / JUnit 4 rules (Testcontainers 1.x style). | Dependency resolution fails (module removed in JUnit 6, JUnit 4 dropped in Testcontainers 2.0); ban `org.junit.rules.*`. |
+| Field `@Autowired` injection, violating the SKILL's constructor-injection rule. | ArchUnit `noFields().should().beAnnotatedWith(Autowired.class)`. |
+| `domain/` importing Spring/JPA/adapters (hexagon inversion). | ArchUnit `onionArchitecture()` / `layeredArchitecture()` + `slices().matching("..domain.(*)..").should().beFreeOfCycles()`. |
+| Calls `Instant.now()` / `LocalDateTime.now()` in business logic instead of injected `Clock`. | ArchUnit `noClasses().that().resideInAPackage("..domain..").should().callMethod(Instant.class, "now")` and the same for `LocalDateTime`. |
+| Puts `LocalDateTime`/`java.util.Date` in API DTOs. | ArchUnit dependency rule scoped to `..adapter.inbound.dto..`; plus `@JsonFormat` only on `OffsetDateTime`. |
+| Leaves a `@Mapper` field unmapped (manual mapping creep). | MapStruct `unmappedTargetPolicy = ReportingPolicy.ERROR` fails compilation. |
+| Omits `-proc:full`; JDK 21+ emits an annotation-processing warning that `-Werror` turns into a failure. | Step 3 exits non-zero until `-proc:full` is present (do not "fix" by removing `-Werror`). |
+| Invokes `google-java-format` directly; JDK 16+ throws `IllegalAccessError` without `--add-exports jdk.compiler/...`. | Always run through Spotless (`spotlessCheck`); ban raw GJF in scripts. |
+| Uses gitleaks `detect` / `protect` (deprecated in 8.19). | CI script asserts `gitleaks git` / `gitleaks dir`; old subcommands are hidden and unsupported. |
+| Uses PMD's pre-7 CLI (`pmd -d src -R ...`). | Run `./gradlew pmdMain`; PMD 7 uses the unified `pmd check` subcommand. |
+| Enables `--enable-preview` in the release build (bytecode/runtime mismatch). | Compile the preview code in a separate source set only; `javap -verbose` minor version must be 69 (Java 25), not 65535. |
+
+## Evidence to Record
+
+Paste each row into the task's Verification Evidence block verbatim.
+
+| Command | Expected result | Exit code |
+| --- | --- | --- |
+| `./gradlew --version` | `Gradle 9.7.1`, `Launcher JVM: 25` | 0 |
+| `./gradlew spotlessCheck` | `BUILD SUCCESSFUL`, 0 reformatted files | 0 |
+| `./gradlew compileJava compileTestJava` | `BUILD SUCCESSFUL`, no `error:`/`warning:` lines | 0 |
+| `./gradlew test --tests '*ArchitectureTest'` | all ArchUnit rules pass; count of rules > 0 | 0 |
+| `./gradlew checkstyleMain pmdMain spotbugsMain` | `BUILD SUCCESSFUL`, 0 violations | 0 |
+| `./gradlew jacocoTestCoverageVerification` | `BUILD SUCCESSFUL` (line ≥ 0.80, branch ≥ 0.70) | 0 |
+| `./gradlew pitest` | mutation score ≥ 70%, no "no mutations found" | 0 |
+| `./gradlew flywayValidate` | `Successfully validated N migrations` | 0 |
+| `gitleaks git --redact --exit-code 1` | `no leaks found` | 0 |
+| `osv-scanner scan source --licenses -r .` | `No issues found` | 0 |
+| `curl --fail .../actuator/health/readiness` | `{"status":"UP"}` | 0 |
+| `git diff --exit-code gradle/verification-metadata.xml gradle.lockfile` | no diff after `--write-locks` | 0 |
+
+## Archived / Deprecated / Superseded in 2026 — never recommend
+
+- **gitleaks** — author declares the project *feature complete*; future releases are
+  **security patches only**, and focus has shifted to **Betterleaks**. Keep 8.30.1 pinned for now,
+  but track Betterleaks as the successor.
+- **OWASP Dependency-Check** — not archived, but rejected as the primary SCA gate: since 9.0.0 it
+  uses the NVD API and is **extremely slow without an NVD API key**; Sonatype OSS Index now
+  requires **Sonatype Guide tokens** (enforced from Sept 2025, migration through 2026) or the
+  analyzer silently disables itself. Use osv-scanner instead.
+- **Maven 4.0.0** — still `4.0.0-rc-6` (not GA) in Sept 2026; do not pin. Stable Maven is 3.9.16.
+- **Maven 3.8.x and older** — below Boot 4's 3.6.3 floor and unsupported; pin 3.9.16 if Maven is forced.
+- **Spring Boot 3.5.x** — final 3.x line; OSS support ends and only commercial support remains. Migrate to 4.1.x.
+- **JUnit 4 / Vintage-based harnesses** — JUnit 6 is the baseline; `junit-platform-runner` and
+  `junit-platform-jfr` are removed, `org.junit.jupiter.migrationsupport` is deprecated for removal,
+  and Testcontainers 2.0 dropped JUnit 4 entirely.
+- **Undertow support** — removed from Spring Boot 4 (Servlet 6.1 baseline not met).
+- **Spock integration** — removed from Spring Boot 4 (no Groovy 5 support).
+- **Spring Session Hazelcast / MongoDB** — no longer managed by Boot 4 (moved to vendor projects).
+- **Spring Retry dependency management** — removed from Boot 4; use Spring Framework's core retry.
+- **maven-compiler-plugin 4.0.0-beta-5** — prerelease; pin the Boot-managed 3.15.0 (or 3.16.0 stable).
+- **AssertJ 4.0.0-M1** — milestone; pin 3.27.7.
+- **MapStruct 1.7.0-Beta2** — prerelease; pin 1.6.3.
+
+## Breaking changes that silently fail if written from memory
+
+- **Boot 4 starter renames:** `spring-boot-starter-web` → `spring-boot-starter-webmvc`;
+  `spring-boot-starter-aop` → `spring-boot-starter-aspectj`; `spring-boot-starter-oauth2-*` →
+  `spring-boot-starter-security-oauth2-*`; `spring-boot-starter-web-services` →
+  `spring-boot-starter-webservices`. Flyway/Liquibase now need `spring-boot-starter-flyway` /
+  `spring-boot-starter-liquibase`; health needs `spring-boot-health`.
+- **Jackson 3:** package `com.fasterxml.jackson` → `tools.jackson` (annotations stay under
+  `com.fasterxml.jackson.annotation`); `@JsonComponent` → `@JacksonComponent`;
+  `Jackson2ObjectMapperBuilderCustomizer` → `JsonMapperBuilderCustomizer`;
+  `spring.jackson.read/write.*` → `spring.jackson.json.read/write.*`.
+- **JSpecify:** `org.springframework.lang.Nullable` is removed; use `org.jspecify.annotations.Nullable`.
+- **`@EntityScan`** moved to `org.springframework.boot.persistence.autoconfigure.EntityScan`;
+  `spring.dao.exceptiontranslation.enabled` → `spring.persistence.exceptiontranslation.enabled`.
+- **Hibernate:** `hibernate-jpamodelgen` → `hibernate-processor`.
+- **Optional deps** are excluded from Boot 4 uber jars; set `<includeOptional>true</includeOptional>`.
+- **Classic uber-jar loader** removed; delete `<loaderImplementation>CLASSIC</loaderImplementation>`.
+- **Liveness/readiness probes** are enabled by default in Boot 4; disable via
+  `management.endpoint.health.probes.enabled=false`.
+- **Error Prone flags:** must run on **JDK 21+** (2.42.0 is the last JDK-17 line); needs
+  `-XDcompilePolicy=simple`, `--should-stop=ifError=FLOW`, and on JDK 21+
+  `-XDaddTypeAnnotationsToSymbol=true`; forked/toolchain compiles additionally need the
+  `--add-exports jdk.compiler/...` set.
+- **osv-scanner V2:** command is `osv-scanner scan source -r <dir>` (V1 was `osv-scanner -r <dir>`);
+  `fix` is experimental.
+- **gitleaks:** `detect` → `git`, and `--no-git`/`--source` mapping → `dir`; both changed in v8.19.
+- **PMD 7:** unified CLI `pmd check` (also `pmd cpd`, `pmd ast-dump`); ruleset paths changed.
+- **Spotless 4.x lib / 3.10.2 plugin:** requires Java 17; `RemoveWildcardImportsStep` renamed to
+  `ForbidWildcardImportsStep`; `googleJavaFormat` default is 1.28.0 on JVM 17, 1.30.0 on 21+, and
+  at least 1.30.0 on 25+.
+- **Testcontainers 2.0:** classes relocated and JUnit 4 removed; when using the Boot parent, remove
+  any explicit Testcontainers 1.x BOM/version override.
+- **Gradle 9:** runs on JVM 17–26 only (JVM 27 unsupported); toolchain 25 requires Gradle ≥ 9.1.0.
+- **maven-pmd-plugin 3.28.0** defaults to PMD 7.17.0 — override `<pmdVersion>7.27.0</pmdVersion>`.
+
+<!-- sources -->
+- https://repo1.maven.org/maven2/org/springframework/boot/spring-boot-starter-parent/maven-metadata.xml
+- https://central.sonatype.com/api/internal/browse/component/versions?filter=namespace%3Aorg.springframework.boot%2Cname%3Aspring-boot-starter-parent
+- https://search.maven.org/solrsearch/select?q=g:org.springframework.boot+AND+a:spring-boot-starter-parent
+- https://docs.spring.io/spring-boot/system-requirements.html
+- https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
+- https://repo1.maven.org/maven2/org/springframework/boot/spring-boot-dependencies/4.1.1/spring-boot-dependencies-4.1.1.pom
+- https://repo1.maven.org/maven2/org/springframework/boot/spring-boot-starter-parent/4.1.1/spring-boot-starter-parent-4.1.1.pom
+- https://docs.gradle.org/current/userguide/compatibility.html
+- https://api.github.com/repos/gradle/gradle/releases/latest
+- https://services.gradle.org/distributions/gradle-9.7.1-bin.zip.sha256
+- https://errorprone.info/docs/installation
+- https://raw.githubusercontent.com/diffplug/spotless/main/CHANGES.md
+- https://raw.githubusercontent.com/diffplug/spotless/main/plugin-maven/CHANGES.md
+- https://raw.githubusercontent.com/diffplug/spotless/main/plugin-gradle/CHANGES.md
+- https://raw.githubusercontent.com/gitleaks/gitleaks/master/README.md
+- https://raw.githubusercontent.com/google/osv-scanner/main/README.md
+- https://raw.githubusercontent.com/dependency-check/DependencyCheck/main/README.md
+- https://docs.junit.org/current/release-notes/index.html
+- https://docs.pmd-code.org/pmd-doc-7.7.0/pmd_release_notes_pmd7.html
+- https://checkstyle.org/
+- https://checkstyle.org/release-notes.html
+- https://github.com/find-sec-bugs/find-sec-bugs
+- https://api.adoptium.net/v3/info/available_releases
+- https://docs.github.com/en/rest/rate-limit/rate-limit (GitHub rate limit documentation; replaces raw rate_limit endpoint)
+- Maven Central metadata (`https://repo1.maven.org/maven2/<group-path>/<artifact>/maven-metadata.xml`) for: spotless-maven-plugin, google-java-format, palantir-java-format, checkstyle, pmd-core, spotbugs, spotbugs-maven-plugin, findsecbugs-plugin, error_prone_core, archunit-junit5, spring-modulith-api, spring-modulith-bom, jspecify, nullaway, dependency-check-maven, dependency-check-gradle, junit-jupiter, testcontainers, assertj-core, jqwik, pitest-maven, pitest-junit5-plugin, flyway-core, flyway-maven-plugin, liquibase-core, liquibase-maven-plugin, jacoco-maven-plugin, mockito-core, mapstruct, lombok, lombok-mapstruct-binding, sonar-maven-plugin, maven-pmd-plugin, maven-checkstyle-plugin, apache-maven, maven-core, maven-wrapper, maven-enforcer-plugin, maven-toolchains-plugin, maven-dependency-plugin, maven-surefire-plugin, maven-failsafe-plugin, maven-compiler-plugin, flatten-maven-plugin, gradle-pitest-plugin
+
 ## Currency Baseline
 
 - **Spring Boot 3.x:** Baseline Java 17+ with the `jakarta.*` namespace (never `javax.*`); enable virtual threads via `spring.threads.virtual.enabled=true` for IO-bound services.
diff --git a/skill-templates/testing-strategy/SKILL.md b/skill-templates/testing-strategy/SKILL.md
index c40d191..5354e64 100644
--- a/skill-templates/testing-strategy/SKILL.md
+++ b/skill-templates/testing-strategy/SKILL.md
@@ -34,5 +34,5 @@ Trivial single-file changes with zero behavior delta (typo fixes, comment-only,
 
 ## Verification Contract
 
-- Run the project's test command BEFORE claiming done (see each stack's `toolchain.test_cmd`).
+- Run the project's test command BEFORE claiming done — see the active stack skill's **Strict Tooling Gate** section for the exact `test` step and its prerequisites (format, lint, typecheck, and security must pass first).
 - Failing tests are fixed in code, never deleted or weakened to pass. A deleted failing test is a QA rejection.
diff --git a/skill-templates/verification-before-completion/SKILL.md b/skill-templates/verification-before-completion/SKILL.md
index da3e0e9..58cb859 100644
--- a/skill-templates/verification-before-completion/SKILL.md
+++ b/skill-templates/verification-before-completion/SKILL.md
@@ -20,3 +20,11 @@ BEFORE claiming success or moving to the <summary_phase>:
 4. VERIFY: Does the output explicitly confirm success?
    - If NO: Fix the code and re-run.
    - If YES: You may now proceed.
+
+## Strict Tooling Gate (MANDATORY — Forced Strict Mode)
+
+Every completion claim must pass the active stack skill's **Strict Tooling Gate** before `lint_task_file` and before any QA transition. The gate is machine-enforced, not advisory.
+
+1. LOAD the single stack skill from `<agent_skills_registry>` that matches the project's language and framework. If none matches, the gate is the repo's base `rtk test` suite plus `lint_task_file`.
+2. EXECUTE that skill's **Strict Tooling Gate** section in fail-fast order: format → lint → typecheck → static analysis → security → test → build. Stop on the first non-zero exit.
+3. RECORD the exact gate command, its output excerpt, and exit code `0` in `## Verification Evidence`. A completion claim without this evidence is a hallucination and is REJECTED at QA.
diff --git a/skill-templates/vue-nuxt/SKILL.md b/skill-templates/vue-nuxt/SKILL.md
index f56d083..b15f485 100644
--- a/skill-templates/vue-nuxt/SKILL.md
+++ b/skill-templates/vue-nuxt/SKILL.md
@@ -65,6 +65,343 @@ project/
 - **Component Testing**: Mount components and test DOM output/emitted events.
 - **E2E Testing**: Use `Playwright` or `Cypress`.
 
+
+## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)
+
+Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.
+
+Stack: **Vue 3.5 (Composition API, `<script setup>`) + Nuxt 4.5 + Strict TypeScript**.
+All versions below were read live from `registry.npmjs.org` dist-tags and official docs on **2026-09-21**; none are guessed. `latest` means the npm `latest` dist-tag on that date.
+
+## Required Toolchain
+
+| Tool | Purpose | Minimum version to pin | Install / availability note |
+| --- | --- | --- | --- |
+| Node.js | Runtime floor for every gate | `24.20.0` (LTS "Krypton") | `.nvmrc`/`.node-version`; Vitest 5 needs `^22.12 \|\| ^24 \|\| >=26`, size-limit 14 needs `^22.19 \|\| ^24.5 \|\| >=26` → Node 24 only |
+| pnpm | Deterministic install | `12.5.1` | `packageManager: "pnpm@12.5.1"` + Corepack; `--frozen-lockfile` in CI |
+| nuxt (CLI `@nuxt/cli`) | Framework + `nuxt prepare/typecheck/build/analyze` | `4.5.2` (CLI `3.37.0`) | binary is `nuxt`; the old `nuxi` name is legacy |
+| vue | Runtime | `3.5.43` | transitive via Nuxt, pin explicitly anyway |
+| typescript | Type engine used by vue-tsc + typescript-eslint | `6.0.3` — **NOT 7.0.2** | TS 7 has no stable programmatic compiler API; typescript-eslint peer is `>=4.8.4 <6.1.0`; vue-tsc 3.3.11 breaks on TS 7 |
+| vue-tsc | SFC type checker for `nuxt typecheck` | `3.3.11` | `@vue/language-core@3.3.11`; peer `typescript >=5.0.0` |
+| @vue/tsconfig | Base strict tsconfig | `0.9.1` | requires TS `>=5.8` |
+| eslint | Linter (flat config only) | `10.11.0` | `.eslintrc` removed in v10; Node ≥20.19/22.13/24 |
+| @eslint/js | Core rules preset | `10.0.1` | must match ESLint 10 major |
+| @nuxt/eslint | Project-aware Nuxt flat config generator | `1.17.0` | peer `eslint ^9 \|\| ^10`; emits `.nuxt/eslint.config.mjs` |
+| eslint-plugin-vue | Vue correctness rules | `10.11.0` | flat presets incl. `flat/recommended-error`; peer `vue-eslint-parser ^10.3.0` |
+| vue-eslint-parser | Parser for `.vue` | `10.4.1` | peer dependency of eslint-plugin-vue v10 |
+| typescript-eslint | Typed TS rules | `8.70.1` | `strictTypeChecked` + `stylisticTypeChecked`; peer eslint `^8.57 \|\| ^9 \|\| ^10` |
+| prettier | Formatter | `3.9.8` | native `.vue` support, no plugin needed |
+| eslint-config-prettier | Disables conflicting stylistic rules | `10.1.8` | append LAST in flat config |
+| knip | Dead code + unused dependency detection | `6.37.0` | `--strict`; replaces ts-prune/depcheck |
+| dependency-cruiser | Import-boundary / architecture enforcement | `18.4.0` | `.dependency-cruiser.mjs`; `tsConfig` option resolves Nuxt aliases |
+| vitest | Unit + Nuxt + e2e runner | `5.0.1` | peer `vite ^6.4 \|\| ^7 \|\| ^8` |
+| @vitest/coverage-v8 | Coverage provider | `5.0.1` | must equal vitest version exactly |
+| @nuxt/test-utils | Nuxt runtime env + e2e helpers | `4.3.2` | peer `vitest ^4.0.2 \|\| ^5.0.0` |
+| @vue/test-utils | Component mounting | `2.5.1` | peer of @nuxt/test-utils (`^2.4.2`) |
+| @playwright/test | Browser / e2e driver | `1.63.0` | peer `^1.43.1` for @nuxt/test-utils |
+| @axe-core/playwright | WCAG assertions in e2e | `4.13.0` | pairs with `axe-core@4.13.0` |
+| eslint-plugin-vuejs-accessibility | Static a11y rules | `2.6.0` | flat preset `configs['flat/recommended']`; peer eslint `^5…^10` |
+| size-limit | Bundle-size budget | `14.0.0` | pair with `@size-limit/file@14.0.0` |
+| lockfile-lint | Lockfile provenance / HTTPS check | `5.0.1` | supports `--type pnpm` |
+| happy-dom | DOM for unit tests | `20.14.5` | `@nuxt/test-utils` peer `>=20.0.11`; jsdom `30.1.0` is the alternative |
+
+**Rejected / superseded — never recommend:**
+- `tsc` alone as Vue type checker — cannot parse `.vue`; use `vue-tsc` via `nuxt typecheck`.
+- **TypeScript 7.0.2 with any Vue tooling** — `vue-tsc` fails `Cannot find module 'typescript/lib/tsc'` (vuejs/language-tools #6156); typescript-eslint caps at `<6.1.0`.
+- `typescript-native-bridge` (`6.0.3-bridge.17.tsgo.7.0.2`) — unofficial pre-release bridge for TS7; not a stable gate dependency.
+- **Golar** `0.1.10` — pre-1.0 (0.x), `golar.config.ts` marked `golar/unstable`; `nuxt typecheck --checker golar` is only an opt-in. Do not use as the gate checker.
+- `ts-prune` `0.10.3` (last publish 2021) — unmaintained; superseded by knip.
+- `depcheck` `1.4.7` (last publish 2023-10) — blind to Nuxt auto-imports/SFCs; superseded by knip.
+- `vitest-axe` `0.1.0` (last publish 2022) — abandoned; use `@axe-core/playwright` or `axe-core` directly.
+- `@nuxt/a11y` `1.0.0-alpha.1` — alpha DevTools module, API will change; never a CI gate.
+- Biome `2.5.14` / oxlint `1.85.0` / oxfmt `0.70.0` — no full `eslint-plugin-vue` parity (oxc issue #15761); cannot run typescript-eslint typed rules.
+- `@nuxtjs/axios` `5.13.6` — Nuxt-2-era; use `$fetch`/`useFetch`.
+- Cypress — rejected in favor of Playwright (first-class with `@nuxt/test-utils`).
+- `.eslintrc.*` any format — removed in ESLint 10.
+
+## Strict Baseline Config
+
+Create exactly these files at project root. Every setting below is load-bearing.
+
+**`package.json`** (pinning + scripts)
+```json
+{
+  "type": "module",
+  "packageManager": "pnpm@12.5.1",
+  "engines": { "node": ">=24.20.0", "pnpm": ">=12.5.1" },
+  "scripts": {
+    "prepare": "nuxt prepare",
+    "format:check": "prettier --check .",
+    "lint": "eslint . --max-warnings 0 --report-unused-disable-directives",
+    "lint:fix": "eslint . --fix",
+    "deadcode": "knip --strict",
+    "boundaries": "depcruise --config .dependency-cruiser.mjs app server shared",
+    "typecheck": "nuxt typecheck --checker vue-tsc",
+    "test": "vitest run",
+    "test:cov": "vitest run --coverage",
+    "e2e": "playwright test",
+    "build": "nuxt build",
+    "size": "size-limit",
+    "audit": "pnpm audit --audit-level=high"
+  }
+}
+```
+
+**`.nvmrc`** = `24.20.0` · **`.node-version`** = `24.20.0`
+
+**`.npmrc`** (exact pins, no silent engine skips)
+```ini
+save-exact=true
+engine-strict=true
+strict-peer-dependencies=true
+```
+
+**`nuxt.config.ts`** (turn every checker on; strict is opt-out here)
+```ts
+export default defineNuxtConfig({
+  modules: ['@nuxt/eslint', '@nuxt/test-utils/module'], // add '@pinia/nuxt' here only together with pinned `pinia` + `@pinia/nuxt` dependencies (same major); never list a module that package.json does not pin
+  eslint: { checker: true, config: { stylistic: false } },
+  typescript: {
+    typeCheck: true,
+    strict: true,
+    tsConfig: {
+      compilerOptions: {
+        noUncheckedIndexedAccess: true,
+        exactOptionalPropertyTypes: true,
+        noImplicitOverride: true,
+        noFallthroughCasesInSwitch: true,
+        noUnusedLocals: true,
+        noUnusedParameters: true,
+        verbatimModuleSyntax: true,
+        isolatedModules: true
+      }
+    }
+  }
+})
+```
+> Do **not** hand-edit root `tsconfig.json`; Nuxt generates `.nuxt/tsconfig.app.json`, `.nuxt/tsconfig.server.json`, `.nuxt/tsconfig.shared.json`, `.nuxt/tsconfig.node.json` via project references. Extend only through `typescript.tsConfig`.
+
+**`eslint.config.mjs`** (single flat config; Nuxt-aware, then hard-locked)
+```js
+import withNuxt from './.nuxt/eslint.config.mjs'
+import vue from 'eslint-plugin-vue'
+import tseslint from 'typescript-eslint'
+import vueA11y from 'eslint-plugin-vuejs-accessibility'
+import prettier from 'eslint-config-prettier'
+
+export default withNuxt(
+  ...vue.configs['flat/recommended-error'],
+  ...vueA11y.configs['flat/recommended'],
+  ...tseslint.configs.strictTypeChecked,
+  ...tseslint.configs.stylisticTypeChecked,
+  {
+    files: ['**/*.{ts,vue}'],
+    languageOptions: { parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname } },
+    rules: {
+      'vue/component-api-style': ['error', ['script-setup']],
+      'vue/block-lang': ['error', { script: { lang: 'ts' } }],
+      'vue/block-order': ['error', { order: ['script', 'template', 'style'] }],
+      'vue/define-macros-order': ['error', { order: ['defineOptions', 'defineProps', 'defineEmits', 'defineSlots'] }],
+      'vue/define-props-declaration': ['error', 'type-based'],
+      'vue/define-emits-declaration': ['error', 'type-based'],
+      'vue/no-import-compiler-macros': 'error',
+      'vue/no-ref-as-operand': 'error',
+      'vue/no-mutating-props': 'error',
+      'vue/no-setup-props-reactivity-loss': 'error',
+      'vue/no-watch-after-await': 'error',
+      'vue/no-lifecycle-after-await': 'error',
+      'vue/require-explicit-emits': 'error',
+      'vue/multi-word-component-names': 'error',
+      'nuxt/prefer-import-meta': 'error',
+      'no-console': 'error',
+      'no-restricted-globals': ['error', { name: 'fetch', message: 'Use useFetch/$fetch in Nuxt.' }],
+      'no-restricted-imports': ['error', { paths: [{ name: 'axios', message: 'Banned: use useFetch/$fetch.' }] }],
+      '@typescript-eslint/no-explicit-any': 'error',
+      '@typescript-eslint/no-floating-promises': 'error',
+      '@typescript-eslint/no-unsafe-assignment': 'error'
+    }
+  },
+  prettier
+)
+```
+
+**`.prettierrc.json`** = `{ "semi": false, "singleQuote": true, "printWidth": 100, "vueIndentScriptAndStyle": false }` · **`.prettierignore`** = `node_modules`, `.nuxt`, `.output`, `dist`, `pnpm-lock.yaml`
+
+**`knip.jsonc`** (Nuxt entry roots)
+```jsonc
+{
+  "entry": ["nuxt.config.ts", "app/app.vue", "server/**/*.ts", "app/plugins/*.ts"],
+  "project": ["**/*.{ts,vue}"],
+  "ignoreExportsUsedInFile": true,
+  "ignoreDependencies": ["@nuxt/test-utils", "@nuxt/eslint", "happy-dom"]
+}
+```
+
+**`.dependency-cruiser.mjs`** (Nuxt layers / composables / components boundaries)
+```js
+export default {
+  forbidden: [
+    { name: 'no-circular', severity: 'error', from: {}, to: { circular: true } },
+    { name: 'no-server-to-app', severity: 'error', from: { path: '^server/' }, to: { path: '^app/' } },
+    { name: 'no-app-to-server', severity: 'error', from: { path: '^app/' }, to: { path: '^server/' } },
+    { name: 'shared-is-leaf', severity: 'error', from: { path: '^shared/' }, to: { path: '^(app|server)/' } },
+    { name: 'components-not-pages', severity: 'error', from: { path: '^app/components/' }, to: { path: '^app/pages/' } },
+    { name: 'no-orphans', severity: 'warn', from: { orphan: true, pathNot: ['\\.(d|config|test|spec)\\.(ts|js)$'] }, to: {} }
+  ],
+  options: {
+    tsConfig: { fileName: '.nuxt/tsconfig.app.json' },
+    tsPreCompilationDeps: true,
+    doNotFollow: { path: 'node_modules' },
+    exclude: { path: '(node_modules|\\.output|\\.nuxt|coverage)' }
+  }
+}
+```
+
+**`vitest.config.ts`** (projects + coverage gate; Vitest 5 shape)
+```ts
+import { defineConfig } from 'vitest/config'
+import { defineVitestProject } from '@nuxt/test-utils/config'
+
+export default defineConfig({
+  test: {
+    projects: [
+      { test: { name: 'unit', include: ['test/unit/**/*.{test,spec}.ts'], environment: 'node' } },
+      await defineVitestProject({ test: { name: 'nuxt', include: ['test/nuxt/**/*.{test,spec}.ts'], environment: 'nuxt' } }),
+      { test: { name: 'e2e', include: ['test/e2e/**/*.{test,spec}.ts'], environment: 'node' } }
+    ],
+    coverage: {
+      provider: 'v8',
+      reporter: ['text', 'json-summary'],
+      include: ['app/**/*.{ts,vue}', 'shared/**/*.ts', 'server/**/*.ts'],
+      exclude: ['**/*.d.ts', 'app/pages/**'],
+      thresholds: { lines: 90, functions: 90, branches: 85, statements: 90, perFile: true }
+    }
+  }
+})
+```
+
+**`playwright.config.ts`** — `testDir: './test/e2e-browser'`, `use: { baseURL: 'http://localhost:3000' }`, `webServer: { command: 'nuxt build && nuxt preview', url: 'http://localhost:3000', reuseExistingServer: !process.env.CI }`.
+
+**`test/e2e-browser/hydration.spec.ts`** — attach `page.on('console', …)`, collect messages matching `/hydration|mismatch/i`, assert the array is empty.
+**`test/e2e-browser/a11y.spec.ts`** — `new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()`; assert `violations.length === 0`.
+
+**`.size-limit.json`**
+```json
+[
+  { "name": "client entry", "path": ".output/public/_nuxt/entry-*.js", "limit": "180 kB", "gzip": true },
+  { "name": "all client JS", "path": ".output/public/_nuxt/*.js", "limit": "450 kB" }
+]
+```
+
+## Mandatory Gate Order
+
+Fail-fast: cheapest/deterministic gates first, network/browser/build gates last. Run each line as one command; a non-zero exit stops the pipeline.
+
+1. `corepack enable && pnpm install --frozen-lockfile`
+2. `pnpm exec nuxt prepare`
+3. `pnpm exec prettier --check .`
+4. `pnpm exec eslint . --max-warnings 0 --report-unused-disable-directives`
+5. `pnpm exec knip --strict`
+6. `pnpm exec depcruise --config .dependency-cruiser.mjs app server shared`
+7. `pnpm exec nuxt typecheck --checker vue-tsc`
+8. `pnpm exec lockfile-lint --path pnpm-lock.yaml --type pnpm --allowed-hosts npm --validate-https`
+9. `pnpm audit --audit-level=high`
+10. `pnpm exec vitest run --coverage`
+11. `pnpm exec playwright test`
+12. `pnpm exec nuxt build`
+13. `pnpm exec size-limit`
+14. `pnpm exec nuxt analyze --no-serve`
+
+Optional maintenance (not part of the blocking chain): `pnpm exec vitest doctor`, `pnpm exec ncu --format group` (`npm-check-updates@23.1.0`), `pnpm exec nuxt upgrade --channel stable`.
+
+## Hallucination Traps to Block
+
+| AI failure mode (stack-specific) | Check that catches it |
+| --- | --- |
+| Writes Options API (`export default { data() {} }`) | `vue/component-api-style: ['error',['script-setup']]` + `vue/no-deprecated-data-object-declaration` |
+| Omits `lang="ts"` on `<script setup>` | `vue/block-lang` with `{ script: { lang: 'ts' } }` |
+| Imports compiler macros (`import { defineProps } from 'vue'`) | `vue/no-import-compiler-macros` (new in eslint-plugin-vue v10) |
+| Uses `count + 1` instead of `count.value` | `vue/no-ref-as-operand` |
+| Mutates props (`props.x = …`) | `vue/no-mutating-props` |
+| Destructures props and loses reactivity | `vue/no-setup-props-reactivity-loss` |
+| `await` before registering `watch`/lifecycle hooks | `vue/no-watch-after-await` / `vue/no-lifecycle-after-await` |
+| Uses `process.client` / `process.server` | `nuxt/prefer-import-meta` (`import.meta.client`) |
+| Calls bare `fetch` or `axios` inside a component | `no-restricted-globals` (fetch) + `no-restricted-imports` (axios) |
+| Any + unchecked promise drift | `@typescript-eslint/no-explicit-any`, `no-floating-promises`, `no-unsafe-assignment` via `strictTypeChecked` |
+| Wall-clock / locale content rendered during SSR | Playwright hydration spec fails on `/mismatch/i` console output; use `NuxtTime`/`useState`/`useCookie` |
+| Browser API (`localStorage`, `window`) read in `setup()` | Playwright hydration spec + `nuxt typecheck` (DOM lib absent on server context) |
+| Missing/wrong auto-import (typo'd composable) | `nuxt prepare` + `nuxt typecheck` against `.nuxt/imports.d.ts` |
+| Imports `server/` code into `app/`, or deep-imports a page from a component | `depcruise` rules `no-app-to-server`, `components-not-pages`, `shared-is-leaf` |
+| Dead exports / unused deps / unused files accumulate | `knip --strict` |
+| Lockfile resolves to a non-HTTPS or unexpected registry | `lockfile-lint --validate-https --allowed-hosts npm` |
+| TypeScript 7 accidentally installed (e.g. `npm i -D typescript@latest`) | `nuxt typecheck` fails (`Cannot find module 'typescript/lib/tsc'`); `.npmrc save-exact` + pinned `6.0.3` prevents it |
+| Writes old flag `eslint . --ext .ts,.vue` | Flat config ignores `--ext`; the script uses `eslint .` — `--ext` must never appear |
+| Adds `.eslintrc.json` "for compatibility" | ESLint 10 errors; only `eslint.config.mjs` is honoured |
+| Writes `nuxi upgrade --check` / `nuxt doctor` | Both flags/commands do not exist: `nuxt upgrade` has only `--channel`, and there is no `nuxt doctor` (use `vitest doctor`) |
+| Uses Vitest 3-style `workspace` / `experimental.fsModuleCache` | Vitest 5 requires `test.projects` and top-level `fsModuleCache`; old keys are ignored → silent no-op |
+| Scatters `new Date()` / `Intl` without explicit timeZone | Playwright hydration spec + review against the SKILL's `useDateTimeFormatter` rule |
+| Over-budget client bundle sneaks in | `size-limit` exits non-zero when a budget is exceeded |
+
+## Evidence to Record
+
+Paste into the task's Verification Evidence block; include raw output and exit code (`echo $?`) for each.
+
+| # | Command | Expected result | Exit |
+| --- | --- | --- | --- |
+| 1 | `node -v && pnpm -v` | `v24.20.0`, `12.5.1` | `0` |
+| 2 | `pnpm install --frozen-lockfile` | "Lockfile is up to date"; no `ERR_PNPM_OUTDATED_LOCKFILE` | `0` |
+| 3 | `pnpm exec lockfile-lint --path pnpm-lock.yaml --type pnpm --allowed-hosts npm --validate-https` | no violations printed | `0` |
+| 4 | `pnpm audit --audit-level=high` | `No known vulnerabilities found` | `0` |
+| 5 | `pnpm exec prettier --check .` | `All matched files use Prettier code style!` | `0` |
+| 6 | `pnpm exec eslint . --max-warnings 0 --report-unused-disable-directives` | no output (zero errors, zero warnings) | `0` |
+| 7 | `pnpm exec knip --strict` | no unused files/exports/deps | `0` |
+| 8 | `pnpm exec depcruise --config .dependency-cruiser.mjs app server shared` | `no dependency violations found (N modules, M dependencies cruised)` | `0` |
+| 9 | `pnpm exec nuxt typecheck --checker vue-tsc` | `Process exited with code 0`; no TS errors | `0` |
+| 10 | `pnpm exec vitest run --coverage` | tests pass; `Coverage for lines/functions/branches/statements` all ≥ thresholds | `0` |
+| 11 | `pnpm exec playwright test` | all specs pass, including 0 axe violations and 0 hydration messages | `0` |
+| 12 | `pnpm exec nuxt build` | `✔ Client built` + `✔ Server built`; no type-check errors | `0` |
+| 13 | `pnpm exec size-limit` | every budget `Size limit` line under its limit | `0` |
+| 14 | `pnpm exec nuxt analyze --no-serve` | analysis JSON written; no build failure | `0` |
+| 15 | `pnpm exec vue-tsc --version` | `3.3.11` (proves TS 6 engine, not TS 7) | `0` |
+
+<!-- sources -->
+- https://nuxt.com/docs/4.x/guide/concepts/code-style
+- https://nuxt.com/docs/4.x/api/commands/typecheck
+- https://nuxt.com/docs/4.x/api/commands/upgrade
+- https://nuxt.com/docs/4.x/api/commands/analyze
+- https://nuxt.com/docs/4.x/getting-started/testing
+- https://nuxt.com/docs/4.x/guide/best-practices/hydration
+- https://nuxt.com/docs/4.x/guide/best-practices/accessibility
+- https://nuxt.com/docs/guide/concepts/typescript (Nuxt TypeScript concepts; project references, `typescript.typeCheck`, strict default)
+- https://eslint.nuxt.com/packages/module
+- https://eslint.nuxt.com/packages/config
+- https://eslint.nuxtjs.org.cn/packages/plugin (`nuxt/prefer-import-meta`)
+- https://eslint.vuejs.org/user-guide/
+- https://eslint.vuejs.org/rules/
+- https://newreleases.io/project/npm/eslint-plugin-vue/release/10.0.0
+- https://eslint.org/docs/latest/use/migrate-to-10.0.0
+- https://eslint.org/blog/2026/02/eslint-v10.0.0-released/
+- https://typescript-eslint.io/getting-started/typed-linting
+- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
+- https://github.com/vuejs/language-tools/issues/6156
+- https://github.com/vuejs/language-tools/discussions/6121
+- https://golar.dev/modes/typecheck/
+- https://github.com/NikhilVerma/vue-tsgo
+- https://vitest.dev/blog/vitest-5.html
+- https://vitest.dev/guide/cli
+- https://vitest.dev/config/coverage
+- https://github.com/sverweij/dependency-cruiser
+- https://github.com/sverweij/dependency-cruiser/blob/main/doc/options-reference.md
+- https://knip.dev/
+- https://github.com/vuejs/tsconfig
+- https://github.com/nuxt/a11y
+- https://github.com/chaance/vitest-axe
+- https://github.com/snyk-labs/lockfile-lint
+- https://vue-a11y.github.io/eslint-plugin-vuejs-accessibility/
+- https://unpkg.com/eslint-plugin-vuejs-accessibility@2.6.0/dist/index.js (verified `configs['flat/recommended']`)
+- https://nodejs.org/dist/index.json (Node LTS "Krypton" v24.20.0)
+- registry.npmjs.org package metadata for: nuxt, vue, eslint, eslint-plugin-vue, typescript-eslint, vue-tsc, typescript, @nuxt/eslint, vitest, @nuxt/test-utils, @vue/test-utils, prettier, knip, dependency-cruiser, @vitest/coverage-v8, @playwright/test, @axe-core/playwright, vitest-axe, size-limit, nuxi, eslint-plugin-vuejs-accessibility, typescript-native-bridge, golar, ts-prune, depcheck, pnpm
+
 ## Currency Baseline
 
 - **Nuxt 4 (current major):** Scaffold with the `app/` directory layout (`app/components`, `app/pages`) and shared types in `shared/`; Nuxt 3 is end-of-life, so do not pin new work to v3 conventions.
diff --git a/stacks/generic.yaml b/stacks/generic.yaml
deleted file mode 100644
index 95049ba..0000000
--- a/stacks/generic.yaml
+++ /dev/null
@@ -1,13 +0,0 @@
-name: generic
-display_name: Generic (Fallback)
-detection:
-  marker_files: []
-  extensions: []
-  task_keywords: []
-skills: []
-preflight: []
-toolchain:
-  test_cmd: null
-  build_cmd: null
-  lint_cmd: null
-model_preferences: {}
diff --git a/stacks/go-gin.yaml b/stacks/go-gin.yaml
deleted file mode 100644
index aee4d8d..0000000
--- a/stacks/go-gin.yaml
+++ /dev/null
@@ -1,16 +0,0 @@
-name: go-gin
-display_name: Go / Gin
-detection:
-  marker_files: ["go.mod", "go.sum"]
-  extensions: [".go"]
-  task_keywords: ["go", "gin", "golang", "grpc"]
-skills: ["go-gin", "go-hexagonal-grpc"]
-preflight:
-  - "go version"
-toolchain:
-  test_cmd: "go test ./..."
-  build_cmd: "go build ./..."
-  lint_cmd: "golangci-lint run || go vet ./..."
-model_preferences:
-  deep: ["openai/gpt-5.6-sol", "anthropic/claude-3-7-sonnet"]
-  quick: ["gemini/gemini-2.5-flash"]
diff --git a/stacks/kotlin-android.yaml b/stacks/kotlin-android.yaml
deleted file mode 100644
index 695927e..0000000
--- a/stacks/kotlin-android.yaml
+++ /dev/null
@@ -1,17 +0,0 @@
-name: kotlin-android
-display_name: Kotlin / Android
-detection:
-  marker_files: ["build.gradle.kts", "build.gradle", "settings.gradle.kts"]
-  extensions: [".kt", ".kts"]
-  task_keywords: ["kotlin", "android", "compose", "gradle"]
-skills: ["android-kotlin"]
-preflight:
-  - "java -version"
-  - "./gradlew -version || gradle -version"
-toolchain:
-  test_cmd: "./gradlew test"
-  build_cmd: "./gradlew assembleDebug"
-  lint_cmd: "./gradlew ktlintCheck"
-model_preferences:
-  deep: ["anthropic/claude-3-7-sonnet", "openai/gpt-5.6-sol"]
-  quick: ["gemini/gemini-2.5-flash"]
diff --git a/stacks/node-ts.yaml b/stacks/node-ts.yaml
deleted file mode 100644
index d6b048c..0000000
--- a/stacks/node-ts.yaml
+++ /dev/null
@@ -1,17 +0,0 @@
-name: node-ts
-display_name: Node.js / TypeScript
-detection:
-  marker_files: ["package.json", "tsconfig.json"]
-  extensions: [".ts", ".tsx", ".js"]
-  task_keywords: ["node", "typescript", "nextjs", "react"]
-skills: ["nextjs", "react-vite", "node-hexagonal-api"]
-preflight:
-  - "node --version"
-  - "pnpm --version || npm --version"
-toolchain:
-  test_cmd: "pnpm test || npm test"
-  build_cmd: "pnpm build || npm run build"
-  lint_cmd: "pnpm lint || npm run lint"
-model_preferences:
-  deep: ["openai/gpt-5.6-sol", "anthropic/claude-3-7-sonnet"]
-  quick: ["kimi/kimi-k3"]
diff --git a/stacks/python-fastapi.yaml b/stacks/python-fastapi.yaml
deleted file mode 100644
index f6a3a31..0000000
--- a/stacks/python-fastapi.yaml
+++ /dev/null
@@ -1,17 +0,0 @@
-name: python-fastapi
-display_name: Python / FastAPI
-detection:
-  marker_files: ["pyproject.toml", "requirements.txt", "Pipfile"]
-  extensions: [".py"]
-  task_keywords: ["python", "fastapi", "pydantic", "pytest"]
-skills: ["python-fastapi"]
-preflight:
-  - "python3 --version"
-  - "uv --version || pytest --version"
-toolchain:
-  test_cmd: "pytest -q"
-  build_cmd: null
-  lint_cmd: "ruff check . || flake8 ."
-model_preferences:
-  deep: ["openai/gpt-5.6-sol", "gemini/gemini-2.5-pro"]
-  quick: ["gemini/gemini-2.5-flash"]
diff --git a/system-prompt.md b/system-prompt.md
index d912538..e63f0db 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.43.0</system_version>
+<system_version>9.45.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -146,19 +146,19 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
-- **android-kotlin**: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development.
-- **flask-python**: Application Factory, Blueprints, SQLAlchemy, and config separation for Flask
-- **go-gin**: Idiomatic Go, Clean Architecture, and Gin routing best practices
-- **go-hexagonal-grpc**: Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx, and Redis caching for ultra-low latency Go backends.
-- **ios-swiftui**: SwiftUI, MVVM, and modern iOS app architecture
-- **nestjs-prisma-vertical**: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development.
-- **nextjs**: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js
-- **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters.
-- **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing.
-- **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps.
-- **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration
-- **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot
-- **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management
+- **android-kotlin**: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **flask-python**: Application Factory, Blueprints, SQLAlchemy, and config separation for Flask — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **go-gin**: Idiomatic Go, Clean Architecture, and Gin routing best practices — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **go-hexagonal-grpc**: Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx, and Redis caching for ultra-low latency Go backends. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **ios-swiftui**: SwiftUI, MVVM, and modern iOS app architecture — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **nestjs-prisma-vertical**: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **nextjs**: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 </agent_skills_registry>
 
 <agentic_reasoning>
@@ -305,6 +305,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     CRITICAL RULE 5 (Pre-Commit Verification Gate): For DevOps, infrastructure, or deployment tasks, the verification gate MUST include environment-specific checks (registry authentication, token scope validation, network access) BEFORE staging any files. If ANY pre-commit check fails, HALT and output a `<failure_report>`. Do NOT stage or commit partial work.
     CRITICAL RULE 6 (Evidence Capture): Before proceeding to the `<summary_phase>`, you MUST capture the exact test command, expected result, actual result, and exit code. You MUST write these into the `## Verification Evidence` section of the active task file.
     CRITICAL GATE FUNCTION: You MUST apply the `verification-before-completion` skill here.
+    STRICT TOOLING GATE (Machine-Enforced — Forced Strict Mode): Before the verification gate, you MUST load the active stack skill from `<agent_skills_registry>` that matches the project and execute its **Strict Tooling Gate** section in fail-fast order (format → lint → typecheck → static analysis → security → test → build). Stop on the first failure. No completion claim, no `lint_task_file`, and no QA transition until the gate is green. Record the exact gate command, output, and exit code in `## Verification Evidence`. Selection: match by file markers per stack — `go.mod` (+ `import github.com/gin-gonic/gin` → `go-gin`, `buf.yaml`/`proto` + `go.mod` + `Fx` → `go-hexagonal-grpc`), `build.gradle.kts` (`+ compose` → `android-kotlin`, `+ Spring Boot` → `spring-boot`), `Package.swift`/`*.xcodeproj` → `ios-swiftui`, `pyproject.toml` + `Flask` → `flask-python`, `pyproject.toml` + `FastAPI` → `python-fastapi`, `package.json` + `next.config.*` → `nextjs`, `package.json` + `src/ports/` → `node-hexagonal-api`, `package.json` + `apps/expo` → `react-native-expo`, `vite.config.*` → `react-vite`, `nuxt.config.*` → `vue-nuxt`, `nest-cli.json`/`prisma/schema.prisma` → `nestjs-prisma-vertical`. Multi-match repos MUST run every matching gate in fail-fast order; do not silently skip any. When several JS skills match, use the highest Node floor among them and record it in `## Verification Evidence`. Docs-only or no-match repos MUST log a skip record with four fields — repo root, marker scan list, matched skills list, reason phrase — in `## Verification Evidence`. Passing example: `root=. markers=[package.json] matched=[] reason=no stack marker found`. Failing example (never do this): `skipped gates` with no fields. Deferred gates block `lint_task_file` and any QA transition until the nightly/merge queue is green, with queue URL plus commit SHA plus green verdict logged in `## Verification Evidence`.
     1. Run the test/build command.
     2. If tests fail, you have a maximum of 3 repair attempts. If the error persists after 3 attempts, you MUST HALT immediately and output a `<failure_report>` detailing the exact errors for the Manager.
     3. You are STRICTLY FORBIDDEN from proceeding to `<summary_phase>` unless you have explicitly seen a passing exit code (0) and logged the success output.
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 0250a87..d1517fd 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -39,7 +39,7 @@ def test_shipped_version_matches_fragment():
 def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(r"<system_version>(.*?)</system_version>",
                         _read(SHIPPED)).group(1)
-    assert shipped == "9.43.0"
+    assert shipped == "9.45.0"
 
 
 def test_no_manager_language_rule_in_shipped_prompt():
diff --git a/tests/test_skill_registry.py b/tests/test_skill_registry.py
index 43e74c6..451726d 100644
--- a/tests/test_skill_registry.py
+++ b/tests/test_skill_registry.py
@@ -126,8 +126,6 @@ def test_hexagonal_expansion_contract():
         assert required in node, f"contract term missing: {required}"
     reg = REGISTRY.read_text(encoding="utf-8")
     assert "node-hexagonal-api" in reg
-    stacks = (ROOT / "stacks" / "node-ts.yaml").read_text(encoding="utf-8")
-    assert "node-hexagonal-api" in stacks
 
 
 def test_opencode_init_skill_contract():
```
<!-- END_GIT_DIFF -->
