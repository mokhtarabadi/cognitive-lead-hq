# Task 12: Night mode workflow fragment + audit ignore for the compact config

**File:** `tasks/completed/12-night-mode-workflow-fragment.md`
**Source:** manager (2026-10-13, after the overnight autopilot run)
**Type:** feature
**Status:** closed

## Goal

Two deliverables:

1. Add the proven overnight autopilot ("night mode") workflow to the prompt
   fragments so it becomes a standing mode of the system, and rebuild
   `system-prompt.md` from it.
2. Make the `audit-agents` skill ignore the session-compact project config file
   (`.opencode/smart-compact.jsonc`) so audits never flag or patch agent-managed
   tooling.

## Manager's Notes (verbatim)

> می‌تونی حالت شب رو به این پروژه هم اضافه کنی؟ و همینطور skill template audit
> agents رو ویرایش کنی که این فایل مربوط به session compact رو هم ایگنور کنه؟
> حالت شبی که دیشب انجام دادی عالی بود می‌خوام داشته‌مش توی workflow هام.

## Scope

- New fragment `prompts/fragments/23-night_mode.md` (the mode: trigger, locked
  no-questions rule, delegated authority, per-task pipeline, evidence rules,
  compaction survival, morning report shape).
- `prompts/manifest.txt` entry so the assembler includes it.
- `prompts/fragments/01-system_version.md` bump (a new mode is a minor change).
- Regenerated `system-prompt.md` (generated artifact, must stay byte-identical to
  the assembler output).
- `skill-templates/audit-agents/SKILL.md`: ignore the session-compact config.
- `CHANGELOG.md` entry.

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output system-prompt.md` then re-assemble to `/tmp/system-prompt-check-12.md` and diff, plus `python3 scripts/check_docs_sync.py`; greps `grep -n "### Added" CHANGELOG.md | head -20` and `grep -n "smart-compact.jsonc" skill-templates/audit-agents/SKILL.md`
- **Expected result:** assembler output identical to the committed `system-prompt.md`; docs-sync gate passes; single `### Added` under top Unreleased block; placeholder skill paths
- **Actual result:** `Assembled 105565 bytes`, `REPRODUCIBLE_OK`, `docs-sync: OK`; top block `### Added` only at line 9 (next at line 69 in a later version block); skill refs use `[PROJECT_ROOT]/.opencode/smart-compact.jsonc` (lines 14, 41); fragment tail ends `</night_mode>` flush-left; `system-prompt.md` reports `<system_version>9.59.0</system_version>`
- **Exit code:** 0
- **Stack gate:** docs plus prompt fragments only; root=. markers=[package.json] matched=[] reason=no stack marker found, no language stack gate applies

## Definition of Done

- [x] Night-mode fragment written and manifest-registered
- [x] Version bumped and `system-prompt.md` rebuilt from fragments
- [x] audit-agents ignores `.opencode/smart-compact.jsonc`
- [x] CHANGELOG updated; docs-sync gate green

## Acceptance Criteria

- [x] Assembled prompt is reproducible (assembler output == committed file)
- [x] The night-mode rules match the mode actually exercised overnight
- [x] The auditor neither flags nor patches the compact config file

## Local TODOs

- [x] Fragment written and manifest-registered
- [x] Version bumped and prompt rebuilt
- [x] audit-agents ignore added
- [x] CHANGELOG and docs-sync green

## Self-decisions

- D1: delivered as a prompt fragment plus a docs page rather than a skill template, because night mode is a system mode, not a task-shaped skill; the execution workflow cross-references it so the Step 6/7/8 gates are explicitly overridden for the night.
- D2: version bumped 9.58.2 -> 9.59.0 (minor: new mode), per the repo rule that every prompt rebuild carries a version bump.
- D3: prettier ran on the fragment sources before the final assembly so the generated prompt stays byte-identical to the assembler output.

## Risk & Rollback

- **Risk:** a prompt fragment edit that the assembler cannot reproduce breaks the
  byte-identity lint gate.
- **Rollback plan:** revert the fragment, the manifest line and the rebuilt prompt.

## Execution Log & Reasoning

Requested by the Manager the morning after the overnight autopilot run, which he
rated as the target behaviour. The mode is therefore documented from the run that
worked, not invented: no-question rule, delegated acceptance and closure, one task
at a time, evidence-cited verdicts, dispute path for false rejections, compaction
survival via project memory, and a fixed morning-report shape.

QA hotfix (QA_REJECTED round): merged the duplicate `### Added` header in
CHANGELOG.md so the night-mode entries sit under the single top Unreleased
header with no history reformatting; normalized the fragment closing tag to
flush-left `</night_mode>`; switched both skill path refs to the
`[PROJECT_ROOT]` placeholder form with ignore semantics unchanged; rebuilt
`system-prompt.md` from fragments and confirmed `REPRODUCIBLE_OK` plus
`docs-sync: OK`. `docs/README.md` night-mode line confirmed intact.

QA re-test: QA_PASSED with cites on CHANGELOG.md:9, fragment closing
tag, manifest, version, workflow override, both skill bullets,
system-prompt version, and the docs page.

Code Review: PO_REVIEW_PENDING (technically APPROVED). Strengths: fragment
chain intact (fragment, manifest, 9.59.0, assembled prompt), placeholder
skill ignore in both bullets, docs mirror plus index, REPRODUCIBLE_OK and
docs-sync OK. Follow-ups noted: cosmetic history lines, executor closure
gate alignment, trigger breadth. File stays in tasks/qa/ pending explicit
closure approval. File verified in `tasks/qa/`.

Closure: Manager quote `Approved for closure` (2026-10-13); prior
`QA_PASSED` and `PO_REVIEW_PENDING` confirmed; moved from `tasks/qa/` to
`tasks/completed/` per protocol.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `723e3ffbd69c98e9d89cf8e3870a64f8c3630719`
<!-- END_GIT_DIFF -->
