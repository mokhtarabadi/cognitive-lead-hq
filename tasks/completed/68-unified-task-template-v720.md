# Task 68: Unified Task Template V7.2.0

**File:** `tasks/backlog/68-unified-task-template-v720.md`
**Source:** orchestrator
**Type:** improvement
**Status:** closed

## Source Context

### Variant A: Orchestrator

## Goal

Implement the Unified Task Template (V7.2.0) across task-generator, telegram-issue-sync, archive-tasks skills and bump the system prompt to 7.2.0 with a matching CHANGELOG entry.

## Blueprint Reference

Code Reviewer closure of Tasks 66/67 (commit `88296ed`). Orchestrator implementation task "Unified Task Template (V7.2.0)" — 5 steps.

## Manager's Notes

- Orchestrator Step 4a references `<system_version>7.0.1` — STALE. Actual current version is `7.1.1`; bump to `7.2.0` (MINOR per SemVer).
- This task file itself uses the new unified template (dogfooding), `Source: orchestrator`.

---

## Local TODOs

- [x] Initial codebase exploration
- [x] Step 1: task-generator unified canonical template
- [x] Step 2: telegram-issue-sync references unified template
- [x] Step 3: archive-tasks Source metadata + Source Distribution table
- [x] Step 4: system-prompt version bump to 7.2.0
- [x] Step 5: CHANGELOG 7.2.0 entry
- [x] Verify: prettier check + version gate + inject diff

---

## OpenCode Execution Log & Reasoning

### Gatekeeper note (stale version reference)

The Orchestrator's Step 4a instructed changing `<system_version>7.0.1</system_version>` → `7.2.0`. The literal target was stale: the actual current version was `7.1.1` (bumped during Tasks 66/67). This is a factual stale-target, not a rule violation — the intent (MINOR bump to 7.2.0 per SemVer: non-breaking feature addition) is fully compliant. Self-corrected to `7.1.1` → `7.2.0`. This task file itself was created using the NEW unified template with `Source: orchestrator` (dogfooding).

### Step 1 — task-generator/SKILL.md (unified canonical template)

- Step 4 "Generate File" template replaced: metadata header now `**Source:** [orchestrator|telegram|manager]` alongside File/Type/Status; title format is `# Task [NN]: [Title]`.
- New polymorphic `## Source Context` section with three variant blocks (Orchestrator: Goal + Blueprint Reference + Manager's Notes; Telegram: Goal + Original Message ([Language]) + English Translation + Refactored Prompt + Relevant Code Context + AI Analysis & Opinion; Manager: Goal + Manager's Notes).
- `## Goal` and `## Local TODOs` declared MANDATORY for all source types; `## Goal` emphasized MANDATORY inside each variant.
- `---` horizontal rule retained before `## OpenCode Execution Log & Reasoning`; `<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `fe21fd1e23153110247f528023e0435fb0551ead`
<!-- END_GIT_DIFF -->
