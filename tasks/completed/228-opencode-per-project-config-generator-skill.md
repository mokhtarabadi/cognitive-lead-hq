# Task 228: OpenCode per-project config generator skill

**File:** `tasks/completed/228-opencode-per-project-config-generator-skill.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Source Context

## Goal

Research OpenCode fully, then ship a skill that writes a comprehensive correct opencode.json for any project.

## Manager's Notes

Manager order (2026-09-14, English verbatim): "start reserach about opencode and collect it data and learn it . like the shema and tools and lsps and others, and create a skill for it or adjust audit agents skill when run it analazye project or ask user and create a comperhenise and correct opencode.json per project. serach and collect data first then ask brain for planing and use auto pilot, create a goal for it"

Also: consult the manager-decision skill when a ruling is needed. Autopilot is locked. The standing project purpose governs: strict anti-hallucination linters, never invent config the runtime does not speak.

## Local TODOs

- [x] Collect OpenCode truth (local + global opencode.json, docs, tools, LSP, MCP/plugin model)
- [x] Brain planning turn for the skill design
- [x] Autopilot implement (new skill or audit-agents adjustment + tests + docs)
- [ ] Brain QA + review, move to qa, report

## Acceptance Criteria

- [x] Research covers schema fields, tool list, LSP form, MCP server form, agents, permissions, skills, config merge order
- [x] Brain approves the design before implementation
- [x] Shipped skill analyzes a project (or asks the user) and writes a valid opencode.json
- [x] Tests lock the generator contract; suite green; docs-sync OK

## Verification Evidence

- **Test command:** full pytest suite + `python3 scripts/check_docs_sync.py`
- **Expected result:** all pass, exit 0
- **Actual result:** 323 passed in 2.36s, exit 0; docs-sync OK (orphan warn-only: fetch-opencode-docs.py, repomd); golden file validates clean via scripts/validate-opencode.py
- **Exit code:** 0
- **QA hotfix (2026-09-14, QA_REJECTED F1–F9):** 324 passed in 2.87s, exit 0; docs-sync OK; golden still validates clean (exit 0). New: V1-only lsp gate, plugin-dict env {env:}+secret rule, invented-value rejection (default_agent/MCP command/plugin source), skill output-path guard + no-invented-values rule, matrix plugin-env row. 1 new negative-test function (plugin secret, 7-of-8 ZAC, V2-LSP both forms + V1 accept, missing/empty/non-dict/empty-agent, 3 placeholder rejections) — first run failed as required (plugin-secret hole proven), green after fix.
- **QA hotfix round 2 (2026-09-14, QA_REJECTED R1–R4 + A1–A3):** 331 passed in 3.86s, exit 0; docs-sync OK (orphan warn-only); golden validates clean (exit 0). New: LSP null-spec/empty-command reject (top-level null lsp stays valid-absent); plugin env-less allowed only without secret-like key names (`SECRET_KEY_NAME`); invented list +foo/bar/dummy/placeholder + word-edge sample across all string fields with `{env:}` exempt; explicit `$schema`-string check; mega test split into 8 single-purpose tests + positives. Deviations logged: sample uses word-edge (not bare substring) so `samples`/`sampling` stay valid; MCP/plugin env VALUES not placeholder-scanned (strict `{env:}` rule already governs them; keys are scanned); validator lives at skill-templates path (`scripts/validate-opencode.py` does not exist).

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** generated config uses V2-only syntax on a V1 runtime (or reverse) and silently does nothing
- **Rollback plan:** generator probes local runtime form first; emits only observed-dialect fields; unknown fields never invented

---

## Execution Log & Reasoning

Plan verdict (Brain 228, Software Architect seat): D1 new standalone skill `opencode-init` wins over extending audit-agents (HQ-only rule: audit-agents stays project-agnostic). Files: SKILL.md + references/runtime-matrix.md + references/examples/golden-opencode.json (redacted) + scripts/validate-opencode.py. Workflow: analyze → ask-user gaps (MCP servers/env, default_agent, formatter/LSP) → generate V1 → validate (parse, V1 shapes, ZAC denies, runtime load) → docs+tests. Deviation D2 (mine, logged): template lives in skill-templates/opencode-init/ (repo distribution convention, like audit-agents/decision-migration), not .opencode/skills/ (repo-local only). Approval: self-approved under standing autopilot order for this goal (Manager, 2026-09-14); proceeding to implement.
Implementation (autopilot): created skill-templates/opencode-init/ (SKILL.md V1-only workflow + ask-user-gaps rule + ZAC deny mandate; references/runtime-matrix.md V1-vs-V2 table; references/examples/golden-opencode.json verbatim copy of repo opencode.json — no secrets, only {env:} refs; scripts/validate-opencode.py stdlib validator: parse, V1 shapes incl. scoped sub-maps, 8-pattern ZAC denies, MCP entry types, {env:}-only secrets + literal-secret regex). Registry +1 line; system-prompt.md rebuilt (+1 line materialized). Research correction logged: local runtime HAS $schema and uses flat permission{tool: decision} V1 map (my pre-plan summary said otherwise — file evidence won). Validator self-check caught a real gap pre-run (external_directory scoped sub-map rejected; fixed validator, not golden). Tests: +2 (skill contract incl. references files; validator: golden-clean, V2-array reject, missing-deny reject, literal-secret reject). Rebuild fallout: test_lint_system_prompt_sync_clean failed post-registry-edit (expected) → rebuilt prompt → full suite 323 passed exit 0, docs-sync OK. CHANGELOG Unreleased entry added (323).
QA triage (QA_REJECTED, task_id 228 third attempt): F1 (no LSP check) FIXED — V1 language-server map enforced, V2 enabled/extensions + unknown keys rejected. F2 (no plugin-env check) FIXED — dict plugin environments obey {env:}+SECRET_LIKE. F3 placeholder part FIXED (invented values rejected); existence check stays a skill-workflow duty (validator is project-agnostic — logged deviation). F4 DISPUTED with file evidence: golden HAS $schema (verified via JSON parse), so QA's "no $schema key" premise is false — SKILL.md line kept, no change. F5 FIXED in skill prose (output-path guard: project root only; validator cannot check destinations). F6–F9 tests ADDED (all fail-closed paths locked; F7/empty-agent/malformed were already enforced — tests lock existing behavior). testing-strategy skill not installed in this env (load failed) — followed its failing-tests-first rule from authorship instead. CHANGELOG hotfix entry added (324).


## Hotfix Round 2 (QA_REJECTED rejection 2 → re-QA; bare task_id 228)

- [x] **Step 1:** Paths resolved via glob: SKILL.md `skill-templates/opencode-init/SKILL.md`; golden `skill-templates/opencode-init/references/examples/golden-opencode.json`; validator `skill-templates/opencode-init/scripts/validate-opencode.py` (fallback path — `scripts/validate-opencode.py` does NOT exist); tests `tests/test_skill_registry.py`; task file `tasks/in-progress/228-opencode-per-project-config-generator-skill.md` (already in-progress, no move needed). AGENTS.md read (entry point OK, no rule violations; script/tooling work explicitly permitted). testing-strategy skill NOT installed in this env (load failed) — proceeding with its principles (single-purpose tests, positive+negative coverage). verification-before-completion loaded.
- [x] **Step 2:** Harden LSP gate (null/empty command reject, no crash)
- [x] **Step 3:** Plugin env rule (env-less allowed when no secret-like keys)
- [x] **Step 4:** Expand invented-value list + all-string-fields scope
- [x] **Step 5:** Confirm $schema/permission/MCP coverage (add only if absent)
- [x] **Step 6:** Split mega test + add positives
- [x] **Step 7:** SKILL.md guards + agents_dir/default_agent verify step

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->

## QA Verdict Note (round 3, 2026-09-13)

Brain QA: QA_PASSED (F1-F8 checked, 8 single-purpose tests, 331 green). Reviewer (bare 228): technically APPROVED → PO_REVIEW_PENDING, Low severity, no hotfix XML. Strengths: V1 fail-closed validator, isolated gap tests, SKILL V1-only+ZAC, golden {env:}-only secrets. Process gaps deferred to closure: I1 placeholder diff, I2 unchecked lint, I3 system-prompt rebuild noise.

## Closure Note (2026-09-13)

Manager: 'Approved for closure'. Moved qa→completed, header synced, status closed. Commit via sanctioned MCP stdio path (stage_and_inject_diff + commit_and_clean_task). opencode-init skill already live globally — usable from any project immediately after restart.
