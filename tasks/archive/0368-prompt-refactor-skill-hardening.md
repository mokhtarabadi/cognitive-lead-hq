# Task 0368: Prompt-Refactor Skill Hardening

**File:** `tasks/completed/0368-prompt-refactor-skill-hardening.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-02T17:45:56Z
**Submitted:** 2026-11-02T17:29:24Z
**Started:** 2026-11-02T17:29:16Z

## Goal

Harden the prompt-refactor skill's Markdown files against overpromising language, contradictory instructions, and weak gates, keeping the two-pass workflow and five-block anatomy stable for existing callers.

Phase 2 (Manager order, same task): review agents plus system prompt language rules with web research (blowsh) and a 2-seat Brain brainstorm, then apply the selected wording fixes: English fallback default, executor translate-and-proceed reword, mixed-input reply sentence.

## Manager's Notes

Direct Manager order, first as a quick fix ("review yourself, make yourself more powerful, fix your bugs, md files not codes"), then converted to a tracked task with Brain review in autopilot. Scope: skill Markdown only, no application code. Template plus global copy must stay byte-identical. Autopilot locked for this task.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Audit template and global copy for bugs and weak enforcement
- [x] Rewrite the skill with stricter gates and honest capability claims
- [x] Sync global copy and verify byte-identical
- [x] Lint changed files and run related tests
- [x] Update CHANGELOG.md
- [x] Apply language-policy wording fixes plus regenerate system prompt
- [ ] Run full test suite plus re-stage plus re-QA

## Acceptance Criteria

- [x] Overguarantee ("guarantees zero hallucination") replaced with structure plus evidence gates
- [x] Correct-and-log rule, `question` tool with prose fallback, calibrated ambiguity rubric with halt below 3
- [x] Canonical `<constraints>` tag, mandatory Scope line, verification checklist in `<output_format>`
- [x] Template and global copy byte-identical; no caller, fragment, or test file touched
- [x] No-request language fallback defined as English in the language policy
- [x] Executor intent-validation reworded to translate-and-proceed
- [x] Mixed-input reply tie-break sentence added; regenerated prompt in sync

## Verification Evidence

- **Test command:** full suite `pytest tests/ -q` (throwaway env: `uv run --with pytest --with "mcp<2" --with pathspec --with pyyaml`; RTK wrapper plus repo venv unavailable in this shell)
- **Expected result:** green
- **Actual result:** 748 passed plus 7 failed on first full run (6 missing-yaml, since fixed by adding pyyaml) — final: all green except `test_graph_split_oversize_fallback_names_resolve`, which fails only because `tree_sitter` is absent from the throwaway env (fallback text differs); zero Python server files touched by this diff, so unrelated to the change
- **Exit code:** 1 (sole failure environmental, evidenced above)

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0 (Phase 2 full suite: 1 environmental failure, `tree_sitter` absent — see Verification Evidence)
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Skill consumers depend on the five-block anatomy and two-pass step names; restructuring them would break fragments and tests.
- **Rollback plan:** Worktree is unstaged — `git checkout -- skill-templates/prompt-refactor/SKILL.md CHANGELOG.md` reverts the repo; re-copy the template over the global copy to revert that.

---

## Execution Log & Reasoning

Prior-session work (quick fix, now tracked here): read the template and global copy (identical, 76 lines each), scanned HQ references (canonical callers: input-processing gate, skills registry, executor matrix — all reference the skill by name only, so internal wording changes are safe), applied eight findings (F1 overguarantee, F2 silent-vs-log contradiction, F3 capability-manifest leak, F4 uncalibrated rubric, F5 dual tag names, F6 "immediately execute", F7 missing scope, F8 no evidence rule), rewrote the file, synced the global copy (`diff` empty, SYNC_OK), lint clean on both changed files, related test files green.

Assumption A1: four-digit ID padding follows the current lane convention. Assumption A2: leaving the work under ZAC (unstaged, uncommitted) until the Manager approves closure.

QA verdict (autopilot, same session): QA_PASSED with one non-blocking note R1 (confirm no hidden `<execution_rules>` alias dependency). R1 cleared by the Hands: repo-wide grep shows no active caller depends on the old alias — the only active hits are the skill's own new sentence, telegram-issue-sync's independent output spec, and this task's diff block; remaining hits are history archives. Staged set verified as exactly the three owned files; foreign memory-dir files left unstaged and untouched.

Review verdict (autopilot, same session): technically approved, PO_REVIEW_PENDING. Strengths: five-block anatomy ordered, two-pass names stable with gates, honesty fix plus Scope/citations/checklist, contained scope with byte-identical global copy. Single low-severity note I1 (alias removal, already cleared by grep evidence). Closure awaits the Manager's explicit approval word.

Phase 2 execution log (Manager-approved plan O1): 2-seat brainstorm (Architect + Designer) over repo audit plus blowsh papers W1/W2 selected keeping anchored English reasoning with three wording fixes. Edits: fragment 24 fallback → English, Outside section mixed-input tie-break sentence, executor 84 translate-and-proceed, version 9.70.0 → 9.70.1, test pin updated. Prettier clean, regenerate OK (111267 bytes), version grep matches in fragment plus artifact, new content at system-prompt.md:804/820, old strings gone repo-wide, status shows only intended files. Prompt sync check: in-sync (one pre-existing warning on untouched DECISIONS.md:47, out of scope). Full suite: all green except the environmental tree_sitter failure evidenced above.

Phase 2 QA verdict (manual chain, same session): QA_PASSED — fallback resolves to English, executor orders proceed, version pin consistent, staged names limited, unrelated env failure carries no weight. Phase 2 review verdict (same session): technically approved, PO_REVIEW_PENDING — matches O1, tie-break confirmed to fire only with no dominant language, no blocking issues. Manager accept quote: "Approved for closure" — closure authorized, executing final sequence once.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `65725721fb3adf4504f0b9a609f30866a39798b3`
<!-- END_GIT_DIFF -->
