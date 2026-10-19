# Task 325: English Technical Terms in Handoffs

**File:** `tasks/completed/325-english-technical-terms-in-handoffs.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Enforce that non-English Manager-facing handoffs keep technical and programming keywords in English to avoid translation mistakes, in both the cognitive executor guidance and the assembled system prompt. No operating instruction may pin a specific language; all wording uses non-English and requested language only. META extension: fix unactionable skill references in the system prompt (Brain has no skill tool; only Hands does), strengthen the lint tool to catch these bug classes, and fix bundle_tasks bugs — all in this same task.

## META Scope (all in task 325, single QA gate, all-or-nothing)

### M1: Language generalization (done, QA_PASSED, review APPROVED twice)

### M2: Unactionable skill references (blueprint approved in principle, O3 reword-only direction pending final sign-off)

Brain has no skill tool, no file access, no web; only Hands (OpenCode) has the skill tool. Five instances: 05:31 Prompt Refactor Gate, 24:11 complexity gating, 11:13 Deep Research Loop with blowsh, 05:22 parenthetical, 21:45 passive task-generator. Direction: reword with explicit Hands actor, no skill-content injection (O3 beats O1 paraphrase and O2 port on cost vs unproven benefit; measurement gate before any prompt growth).

### M3: Lint strengthening (new)

Extend `mcp-lint-server` with checks that catch these bug classes mechanically: unactionable skill-verb check for prompt-facing prose (Brain-actor skill invocation without a Hands actor), plus bundle-task structural checks. Exact check list per final blueprint.

### M4: bundle_tasks bug fixes (new, audit of record)

Subagent audit plus baseline (7 passed via `uv run --project mcp-context-server --with pytest`): B1 stale META content on ID retry (`server.py` rebuild missing), B2 dead collision check (unpadded glob plus no-op pass), B3 non-atomic create (x-open then write), B4 silent dedup plus single-task accept vs 2-6 message, B5 duplicate-vs-missing conflated in `_find_task_file`, B6 lossy rollback (no cwd, no untracked fallback, swallowed errors, hardcoded backlog origin), B7 checklist extractor dead branch plus blank-line splits, B8 checksum gaps, B9 status regex single-word plus date-format drift, B10 test drift (T1 re-implements logic, T3 never invokes bundle_tasks). Fix per final blueprint priority; extend tests to cover fixed paths.

## Manager's Notes

Original request (Persian, verbatim evidence only): "یه تسک بساز برای زبان به cogntive و هم system prompot بکو کلمات تخصصی و فنی رو همیشه سعی کنه انگلیسی بشگه که مشکل در ترجمه باعث اشتباه نشه یعنی الان داری فارسی حرف میزنی با من کلمات تخصصی و کلید واژه های برنامه نویسی رو مثلا سعی کن انگلیسی بگی."

English translation: Create a task for language: tell cognitive and also system prompt to always keep specialized and technical words in English so translation issues do not cause mistakes; i.e. when speaking Persian with me, say specialized words and programming keywords in English.

Follow-up (verbatim evidence only): "دنبال کلمه فارسی یا farsi یا persian بگرد توی پروژه نباید روی زبان خاصی باشه باید بنویسه non english همه رو تغییر بده توی همین تسک و دوباره بفرست برای pipeline brain"

Follow-up translation: search the project for the words Persian, Farsi, and persian; nothing may target a specific language, everything must say non-English; change all of it under this same task and resend through the Brain pipeline.

Scope: update `prompts/fragments/24-language_policy.md` (and `20-communication_examples.md` if it shows handoff style) plus `agents/cognitive-executor.md` communication section, then rebuild `system-prompt.md` via `scripts/prompt-build/assemble_system_prompt.py` and verify sync. Keep reasoning and task file in English; only the final handoff may use the requested language with English technical terms preserved. Follow-up scope: generalize every Persian and Farsi mention in operating instructions (fragments 05, 13, 20, 24, `agents/cognitive-executor.md`, `docs/conventions.md`, `AGENTS.md`) to non-English and requested language; history archives and verbatim evidence quotes stay untouched. Second sweep: repo-wide grep found remaining operating-prose mentions in `skill-templates/telegram-issue-sync/SKILL.md`, `skill-templates/bundle-tasks/SKILL.md`, `README.md`, and a `Unicode/Persian` docstring in `mcp-context-server/gitops.py` — all generalized; `tests/test_bundle_tasks.py` and `test_session_lifecycle.py` keep Persian strings as Unicode test data (not language pinning); `docs/history`, `tasks/completed`, `tasks/.sessions`, `prompts/archive`, and `.opencode/memory` are records and stay untouched.

## Local TODOs

- [x] Inspect `prompts/fragments/24-language_policy.md` and communication examples
- [x] Inspect `agents/cognitive-executor.md` handoff wording rules
- [x] Add English-technical-terms rule with examples (task file, Brain turn, code, Git Diff stay English)
- [x] Generalize all Persian and Farsi mentions in operating instructions to non-English and requested language
- [x] Second sweep: generalize remaining mentions in skill templates, README, and gitops docstring
- [x] Rebuild system prompt and verify sync
- [x] Verify functionality
- [x] META audit: unactionable skill mentions plus lint gaps plus bundle_tasks bugs (done, findings in scope)
- [x] META blueprint: Brain plan plus critique loop until final
- [x] M2: reword 5 unactionable skill references with explicit actors
- [x] M3: strengthen mcp-lint-server with new mechanical checks
- [x] M4: fix bundle_tasks bugs plus extend tests
- [ ] Full verify (prompt sync plus bundle suite plus lint self-check), stage, qa_transition, Brain QA plus review

## Acceptance Criteria

- [x] Non-English handoffs keep technical terms (file paths, tool names, XML tags, code identifiers, Kanban terms) in English with no transliteration into the requested language
- [x] Zero Persian or Farsi mentions remain in operating instructions (`prompts/fragments`, `agents/cognitive-executor.md`, `docs/conventions.md`, `AGENTS.md`, `skill-templates/telegram-issue-sync`, `skill-templates/bundle-tasks`, `README.md`, `mcp-context-server/gitops.py`, assembled `system-prompt.md`); history archives, session transcripts, test data, and verbatim evidence quotes untouched
- [x] Zero unactionable skill references in Brain-owned fragments (every skill verb names Hands or states the no-tool boundary)
- [x] Lint catches the new bug classes mechanically (residual grep plus new lint checks green)
- [x] bundle_tasks fixes verified by extended tests (no pre-existing failures introduced)
- [x] Rule present in both fragment source and executor guidance, and assembled `system-prompt.md` contains it
- [x] `lint_system_prompt_sync` passes (no drift between fragments and assembled prompt)

## Verification Evidence

- **Test command:** rtk test uv run tests/test_prompt_sync.py -q
- **Expected result:** all prompt sync checks pass, assembled prompt matches fragments
- **Actual result:** exit 0, assembled 112600 bytes, Technical-Terms rule intact, all 14 checks pass; byte-identity rebuild confirmed (assemble twice, empty diff)
- **Exit code:** 0
- **Test command:** cd mcp-context-server && uv run --with pytest python -m pytest ../tests/test_bundle_tasks.py -q
- **Expected result:** 7 baseline green plus 11 new red-proof tests green after fixes
- **Actual result:** exit 0, 18 passed; red proof recorded first (9 failed on old code: count, duplicate, retry-stale, rollback-header, collision-helper, extractor, checksum, status, plus e2e-dry-run assertion fixed to section-gate line)
- **Exit code:** 0
- **Test command:** mcp-lint-server self-check (new gates on reworded fragments plus /tmp negative fixture, fixture removed)
- **Expected result:** reworded files pass, old wording fails with file-plus-line citation
- **Actual result:** 4 reworded fragments pass with zero issues via lint_markdown; a negative fixture carrying the old blowsh wording fires Unactionable skill reference (line 1) via both lint_markdown and lint_system_prompt_sync; META gate passes non-META files and flags broken META; fixture deleted after run. Note: the live MCP singleton still serves pre-change lint code until redeployed — direct function runs above use the edited file.
- **Exit code:** 0
- **Stack-skill binding:** root=. markers=[package.json, go.mod, pyproject.toml server, build.gradle.kts] matched=[] reason=prompt prose plus Python MCP change, no app stack skill matches

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Overly broad wording could force English into places where the requested language is required by the Manager.
- **Risk (META):** Lint false positives on quoted Hands examples — mitigated by Hands-window, fence, marker, and registry exemptions; bundle behavior changes are covered by 18 tests.
- **Rollback plan:** Revert fragment and executor edits via git, rebuild system prompt, re-run sync check. META: revert `mcp-lint-server/server.py` + `mcp-context-server/{server,bundle,gitops}.py` + tests; prior behavior returns; never commit.

---

## Execution Log & Reasoning

Seat Check: docs-only prompt language policy change, single domain, requested Software Architect, skipped Designer and Senior Programmer (no trigger words in title plus body). Brainstorm: not required, single domain and reversible via git.
Fed-context: `prompts/fragments/24-language_policy.md:1` (policy file exists), `prompts/manifest.txt:23` (manifest already lists 24), `agents/cognitive-executor.md:161` (handoff bullet updated), `prompts/fragments/20-communication_examples.md:34` (handoff line governs examples), `scripts/prompt-build/assemble_system_prompt.py:372` (assemble entrypoint).
Changes: added Technical-Terms rule section to 24-language_policy.md, added Technical-Terms bullet to executor Communication Patterns, appended Example 4 to 20-communication_examples.md, rebuilt system-prompt.md (112374 bytes, rule at line 830). Manifest needed no change. Assumption A1: existing 20 file governs handoffs so one example is appropriate. Sibling docs inspected: prompts/fragments README/DECISIONS and agents README/DECISIONS carry no contract change for this wording rule, logged no-change.
QA: QA_PASSED with two non-blocking notes (sync test pins no drift only, Example 4 descriptive). Review: APPROVED with PO_REVIEW_PENDING, no blocking issues.
Follow-up: generalized every Persian and Farsi mention in operating instructions to non-English and requested language across fragments 05, 13, 20, 24, `agents/cognitive-executor.md`, `docs/conventions.md`, and `AGENTS.md`; rebuilt `system-prompt.md` (112269 bytes); grep confirms zero remaining matches in all six surfaces; history archives and verbatim evidence quotes intentionally untouched. Assumption A2: deployment default fallback needs no named language; per-message detection governs. Resending through Brain QA and review pipeline.
Re-QA: QA_PASSED, zero specific-language pinning in operating instructions, Technical-Terms rule intact, sync green. Re-review: APPROVED with PO_REVIEW_PENDING, no blocking issues; follow-up suggestions are deployment-default definition and pinning asserts.
Second sweep: repo-wide grep surfaced remaining operating-prose mentions in `skill-templates/telegram-issue-sync/SKILL.md` (verbatim section headers, translation steps, integrity table), `skill-templates/bundle-tasks/SKILL.md` (Unicode slug line), `README.md` (clarification-halt mandate), and `mcp-context-server/gitops.py` (`_kebab_case` docstring) — all generalized to non-English and requested language. Deliberately untouched: `tests/test_bundle_tasks.py` and `tests/test_session_lifecycle.py` Persian strings (Unicode test data, not language pinning), `docs/history`, `tasks/completed`, `tasks/.sessions`, `prompts/archive`, `.opencode/memory`, `.pytest_cache` (records, transcripts, caches). Sibling docs inspected: `mcp-context-server/README.md` and `DECISIONS.md` carry no contract change for a docstring edit, logged no-change. Assumption A3: example slug `تست-باندل` stays as functional sample data. Resending through Brain QA and review pipeline.
Second-sweep QA: QA_PASSED, no residual pinning in operating prose, test data and archives correctly untouched. Second-sweep review: APPROVED with PO_REVIEW_PENDING, no blocking issues; follow-ups are deployment-default definition and pinning asserts.
META: Brain plan (Architect plus Senior Programmer) plus critique loop reached FINAL with 7 resolved debatables. M2 applied 5 O3 rewords with Orchestrator-scoped no-tool boundary (fragments 05, 11, 21, 24). M3 added `_check_unactionable_skill_verbs` (fragment-scoped, registry-exempt, Hands-window plus fence plus marker exemptions) wired into `lint_markdown` and `lint_system_prompt_sync`, plus `_check_bundle_meta_structure` (META-only) wired into `lint_task_file`; backtick-blindness in the verb regex caught and fixed during self-test; ADRs recorded in both slice DECISIONS. M4 fixed B1 (rebuild after final ID, atomic create-plus-write), B5 (distinct locate states), B6 (byte-identical restore to recorded origin, surfaced errors), B2 (padded plus bare collision helper), B3 (atomic write), B4 (2-6 floor plus duplicate-input error), B7 (blank-line paragraphs, stripped nested boxes, dead branch removed), B8 (no length gate), B9 (full-line status, aligned datetime); red proof recorded with 9 failing tests on old code, then 18 passed. Locked runner used throughout (`cd mcp-context-server && uv run --with pytest`); `test_mcp_servers.py` failures are environmental (missing pathspec/yaml) plus one pre-existing split round-trip failure also failing on pristine HEAD. Assumption A4: hand-created same-ID files are ambiguous by definition, so collision is an error, not a warning.
META QA: QA_PASSED — zero unactionable verbs and zero language pinning in operating prose, lint gates fire on old wording and pass on rewords with non-META unaffected, 18 bundle tests green with red proof, sync green with byte-identity rebuild. META review: APPROVED with PO_REVIEW_PENDING, no blocking issues; QA notes ride as follow-ups (file-level boundary masking, fragments README/DECISIONS future false-positive, META gate non-empty vs verbatim).
Manager accept 2026-10-19: 'Approved for closure' — PO_REVIEW_PENDING cleared, closing per protocol.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `76d8414c6ce06d9597e2b2acf89094ecb6bfd07c`
<!-- END_GIT_DIFF -->
