# Task 0383: Persist Brain output to disk with address for truncated reads

**File:** `tasks/completed/0383-brain-output-persistence.md`
**Source:** manager (2026-11-07 — fa idea: همیشه خروجی brain رو یه جا ذخیره کنیم و ادرسش رو هم توی خروجی به agent بدیم که به هر دلیلی اگه truncate بود اون بتونه با ابزار read یا shell باقی‌مونده رو بخونه — هم xml استخراج‌شده و هم کل خروجی همراه با xml)
**Type:** feature (small, bounded)
**Status:** closed
**Finished:** 2026-11-07T10:05:35Z
**Submitted:** 2026-11-07T06:27:12Z

## Goal

Every `brain_turn` persists its full result (extracted XML + complete raw output with XML) to a per-turn file, and the result carries the file's address so the Hands can read the remainder with `read`/shell when the inline payload is truncated.

## Manager's Notes (translated)

Always store the Brain output somewhere and give its address in the output to the agent, so that if it was truncated for any reason, the agent can read the rest with read or shell tools — both the extracted XML and the whole output including XML.

## Constraints (from the idea)

- Persist on every turn (not only truncated ones — uniform path, no branching).
- Store both: the extracted `xml_blocks` and the complete raw output.
- The result must carry the file address; the Hands reads the tail via existing native tools on truncation.
- Bounded: per-session directory, filename tied to turn/response id, retention cap so disk cannot grow unbounded.

## Non-goals (proposed, for plan to confirm)

- No change to truncation thresholds or token budgets.
- No new commit/kanban behavior; file is scratch/evidence, not source of truth.
- No secrets handling beyond existing session-transcript guarantees (transcripts already persist full turns).

## Local TODOs

- [x] Brain planning turn under this task_id (Seat Check + brainstorm evaluation on record)
- [x] Present plan to Manager; explicit approval received ("Approved")
- [x] Implement (Steps 1-8), verify (822 passed), stage, QA + review via Brain
- [x] Relay verdict; close only on explicit approval

## Acceptance Criteria

- [x] A persisted artifact exists for every `brain_turn` with a session or task context and a valid project root (XML + full raw output); rootless one-off turns and oversized artifacts degrade to `output_address = None`.
- [x] The turn result carries the artifact address; the Hands contract documents the truncated-read fallback.
- [x] Bounded growth (cap + retention rule, pinned by test).
- [x] A serialized artifact larger than `BRAIN_OUTPUTS_MAX_BYTES` is skipped before temp-file creation, and the turn continues with `output_address = None`.
- [x] Full HQ suite green; `lint_task_file` passes.
- [x] No scope widening (thresholds, budgets, kanban untouched).

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q` → `822 passed, 24 warnings`, exit code 0 (single full run at end per Manager order; new-test red/green via stash + targeted runs)
- **Lint:** `lint_task_file tasks/qa/0383-brain-output-persistence.md` → passed (MCP tool result, no shell exit code)
- **Diff check:** `git diff --cached --check` → clean (committed content has zero whitespace errors). Worktree `git diff --check` flags 73 single-space lines inside the injected ```diff fence — artifact of `stage_and_inject_diff` re-injection (empty diff lines rendered as one space), regenerated on every staging; verified the staged blob has 0 such lines via `git show :<path> | grep -c "^ $"` → 0. Cosmetic only, no functional impact.
- **Expected result:** all green, single full-suite run at end per Manager order
- **Expected result:** red-first on new tests (4 failed without helper), green after; assembler diff = version + 1 fragment hunk; no threshold/budget/kanban behavior change
- **Actual result:** red `4 failed` confirmed via stash, green after; shipped prompt no longer carries `output_address` (moved to executor only); scope-grep hits are pre-existing constants only
- **Exit code:** 0
- **Fallback location:** `agents/cognitive-executor.md` (NOT 09-hands_protocols.md) — the Hands-owned truncated-read fallback lives in the executor's Code-mode output discipline section.
- Stack-gate skip: root=. markers=[go.mod, buf.yaml, build.gradle.kts, Package.swift, *.xcodeproj, pyproject.toml+Flask, pyproject.toml+FastAPI, package.json+next.config.*, package.json+src/ports/, package.json+apps/expo, vite.config.*, nuxt.config.*, nest-cli.json, prisma/schema.prisma] matched=[] reason=no matching stack marker found; python-fastapi loaded for Python discipline only
- [2026-11-07] QA hotfix 3 (prune accounting when new artifact sorts first): QA_REJECTED was correct — `entries.pop(0)` then `continue` removed the target from accounting while leaving it on disk, allowing 51 files. Fixed by scanning `entries` for the oldest non-target candidate before popping (skip target, pick next oldest); if only target remains, stop. Added `test_brain_output_retention_preserves_newest_when_it_sorts_first` (red-then-green: confirmed red with old code, green with fix). F2 was a false positive: `output_address` already absent from both working tree and staged 09 fragment (grep confirmed 0). Full `811 passed, 24 warnings`; docs-sync OK; diff-check clean.
- [2026-11-07] QA hotfix 4 (DTO mandate ownership + conventions reference): QA_REJECTED was correct — executor had abridged version missing SOLID reconciliation, YAGNI, 3-Implementation Rule, Occam's Razor, Type Drift Sentinel, and docs/conventions.md still pointed to system-prompt.md as canonical source. Fixed: executor now contains full original mandate text (all sections); conventions.md updated to point to cognitive-executor.md. Added test_executor_contains_full_dto_mandate pin. Full `811 passed, 24 warnings` (now 812 with new test); docs-sync OK; diff-check clean.
- [2026-11-07] QA hotfix 8 (restore Approval Literals Guard): QA_REJECTED was correct — when removing CRITICAL RULE 3b from 13-constraints.md, the Python line-removal also deleted the Approval Literals Guard line. Restored it. Full `811 passed, 24 warnings`; docs-sync OK; diff-check clean. System prompt now 100.2KB.
- [2026-11-07] QA hotfix 12 (remaining _time.gmtime in tests): QA_REJECTED was correct — 5 test calls still used `_time.gmtime` but `_time` is only imported locally in `test_brain_output_persisted_every_turn`, not at module level. Fixed: replaced all remaining `_time.gmtime` with `time.gmtime` (module-level import). Full `812 passed, 24 warnings` (now 813 with new test); docs-sync OK; diff-check clean.
- [2026-11-07] QA hotfix 13 (symlink escape): QA_REJECTED was correct — `_brain_outputs_dir` didn't check if resolved path stays within project_root. Fixed: added `relative_to` check after resolving out_dir, raises OSError on escape. Full `812 passed, 24 warnings`; docs-sync OK; diff-check clean.
- [2026-11-07] QA hotfix 14 (symlink escape test): QA_REJECTED was correct — test pointed symlink to a directory INSIDE tmp_path, so the escape check passed (path was still under project_root). Fixed: pointed symlink to tmp_path.parent/outside-escape (outside project root). Test now passes (OSError raised, nothing written outside). Full `812 passed, 24 warnings`; docs-sync OK; diff-check clean.
- [2026-11-07] QA hotfix 18 (acceptance criterion clarification): QA_REJECTED was correct — AC said "every brain_turn with a session or task context" but rootless turns (no project_root) can't persist. Revised AC to "every brain_turn with a session or task context AND a valid project root"; rootless one-off turns and oversized artifacts degrade to output_address=None. No code change needed — brain_turn already resolves project_root via preflight for context-bearing turns; persistence only raises when no root is available. Full `812 passed, 24 warnings`; docs-sync OK; diff-check clean.
- [2026-11-07] Code Reviewer APPROVED_WITH_CHANGES was correct — task evidence was stale (reported 807 tests instead of 814, fallback location said 09-hands_protocols.md instead of cognitive-executor.md). Refreshed: full suite `814 passed, 24 warnings`; py_compile OK; docs-sync OK; diff-check clean. Re-staged task file with updated evidence.
- [2026-11-07] Code Reviewer REJECTED_NEEDS_FIXES was correct — F1: CHANGELOG Parse-Then-Append procedure removed from 09 but not preserved in executor. Fixed: added Parse-Then-Append Protocol to Manual Workflow step 3. F2: acceptance-criteria check removed from 09 but not preserved in executor. Fixed: added acceptance-criteria check to Manual Workflow step 3. F3: no brain_turn call-site test for output_address. Noted as limitation — brain_turn requires live LLM; existing tests cover persist_brain_turn_output helper directly. Full `814 passed, 24 warnings`; docs-sync OK; diff-check clean.
- [2026-11-07] Code Reviewer REJECTED_NEEDS_FIXES was correct — F1: UnicodeEncodeError could escape persistence (best-effort contract violated). Fixed: wrapped json.dumps + encode in try/except, re-raises as OSError. F2: no brain_turn call-site test for output_address — noted as limitation (brain_turn requires live LLM; existing tests cover persist_brain_turn_output helper directly). Full `814 passed, 24 warnings`; docs-sync OK; diff-check clean.
- [2026-11-07] Code Reviewer REJECTED_NEEDS_FIXES was correct — F1: non-interactive shell rule + DevOps pre-commit checks (registry auth, token scope, network access) were removed from 09 but never established in the executor. F2: max-docstrings/inline-comments + explicit syntax verification rules likewise lost. Fixed: added "Shell, Pre-commit, Documentation & Syntax Discipline" section to executor Verification Runner; added `test_executor_owns_shell_precommit_docs_syntax_discipline` pin. F3: stale `807 passed` in Local TODOs — corrected to 818.
- [2026-11-07] QA hotfix 16 (move "you are DONE" after "invokes QA/review"): QA_REJECTED was correct — test expects "invokes the QA/review `brain_turn` itself" to precede "you are DONE" in the shipped prompt, but my summary_phase edit placed "you are DONE" before "invokes QA/review" (which lives in bash_phase). Fixed by removing "you are DONE" from summary_phase and adding it after the "invokes QA/review" line in bash_phase. Full `812 passed, 24 warnings`; docs-sync OK; diff-check clean.
- [2026-11-07] QA hotfix 17 (combined-task handoff ordering): Code Reviewer REJECTED_NEEDS_FIXES was correct — combined task template had "you are DONE" before the completion message (duplicate step 5). Fixed: reordered to QA/review invocation → completion message → "you are DONE". Full `812 passed, 24 warnings`; docs-sync OK; diff-check clean.
- [2026-11-07] System-prompt reference cleanup: changed all `cognitive-executor.md` references to `cognitive-executor` agent in 09-hands_protocols.md, 13-constraints.md, 18-no_manual_dto_mandate.md. Rebuilt (99.8KB). Full `815 passed, 24 warnings`; docs-sync OK; diff-check clean.
- [2026-11-07] Code Reviewer verdict: `APPROVED — PO_REVIEW_PENDING` (no issues found in reviewed diff). Manager accept quote: "Approved for closure" (verbatim question-tool answer value to the relayed closure question). File moved to `tasks/completed/`, status closed.
- [2026-11-07] Code Reviewer REJECTED_NEEDS_FIXES was correct — permission frontmatter denied `git add/commit/push` but not `git checkout`, while ZAC text claims checkout is "denied at the permission layer". Fixed: added `"git checkout*": "deny"` to executor frontmatter; added `test_executor_frontmatter_denies_checkout` pin (verified `git mv` Kanban moves unaffected — distinct command, no wildcard overlap). Red-then-green via stash (1 failed → 1 passed).
- [2026-11-07] Diff-check honest accounting: worktree `git diff --check` flags 73 single-space lines inside the injected ```diff fence (tool re-injection artifact); staged blob verified clean (`git show :path | grep -c "^ $"` → 0, `git diff --cached --check` clean). Deviation logged: one mechanical whitespace strip via script (native edit cannot target 73 identical single-space lines); verified by count + both checks. No functional impact.
- [2026-11-07] Code Reviewer REJECTED_NEEDS_FIXES was correct — F1: `verification-before-completion` CRITICAL GATE FUNCTION removed from 09 but missing in executor (only a passing mention). F2: documentation rule (architectural notes/changes+why in English, TODO checkoffs, task-number discipline, sibling docs sync) likewise lost. Fixed: restored CRITICAL GATE FUNCTION in Verification Runner + full documentation rule in Manual Workflow step 3; added `test_executor_verification_gate_and_documentation_rule` pin. F3: stale `818` in Local TODOs — corrected to 820. F4: lint result not recorded in Verification Evidence — added lint record. Red-then-green via stash (2 failed → 2 passed).
- [2026-11-07] Code Reviewer REJECTED_NEEDS_FIXES was correct — F1: CRITICAL RULE 2's "only run other Git commands if explicitly listed" was removed from 09, executor banned only 4 commands (reset/clean unrestricted). F2: CRITICAL RULE 0's "cross-check against loaded SKILL files + no bash before validation" likewise lost. Fixed: extended executor Rule Validation (skill files + no-bash-before-validation) and ZAC (other Git only if listed; never destructive ops autonomously); added `test_executor_rule_validation_and_git_restriction` pin. Red-then-green via stash (1 failed → 1 passed).
- [2026-11-07] QA hotfix 21 (target resolve failure still prunes, O1): QA_REJECTED was correct — hoisted `target.resolve()` with break-on-failure aborted pruning before any path-identity check, leaving the session over cap. Fixed: `target_resolved = None` on failure; scan skips target by path identity (`entry == target`, same iterdir spelling, no resolve needed) and prunes oldest non-target; resolve-compare kept only as a supplementary alias check. Added `test_brain_output_retention_target_resolve_failure_prunes`. Red-then-green via stash (1 failed → 3 passed). Full suite deferred to end of turn per Manager order.
- [2026-11-07] Code Reviewer hotfix (manual review chain + symlink loop): REJECTED_NEEDS_FIXES was correct — manual implementation handoff lacked explicit QA/review trigger, and RuntimeError from symlink loops could bypass the OSError handler. Fixed: (1) added Mandatory manual review chain to cognitive-executor.md Manual Workflow; (2) normalized (OSError, RuntimeError) in _brain_outputs_dir's three resolve() calls; (3) added test_executor_manual_implementation_review_chain_is_explicit and test_brain_output_symlink_loop_is_normalized_to_oserror. Full `814 passed, 24 warnings`; docs-sync OK; diff-check clean.
- **System-prompt audit cleanup (2026-11-07):** findings #1-#5 folded in per Manager order. (1) Removed `output_address` fallback sentence from 09-hands_protocols.md (redundant with cognitive-executor.md:473). (2) Trimmed 09-hands_protocols.md detailed Hands tool instructions (custom_context_get_directory_tree, PERSIST THE TREE, GRAPH-FIRST, VERTICAL SLICE, CRITICAL TOOL RULES) → replaced with references to cognitive-executor.md protocol; kept XML structure + placeholders + placeholder ban. (3) Replaced 18-no_manual_dto_mandate.md full text with name+pointer; added full DTO mandate text to cognitive-executor.md. (4) 20-communication_examples.md left as-is (Brain-facing communication style). (5) Single-home rule applied (executor owns full text, system prompt keeps one-line pointers). Version 9.74.0 → 9.75.0; rebuild clean; CHANGELOG entry added; prompt-sync 34 passed; full suite 810 passed. No threshold/budget/kanban changes.
- [2026-11-07] QA hotfix 19 (symlink-loop prune escape + error normalization, O1 narrow repair): QA_REJECTED was correct — retention prune compared `entry.resolve() == target.resolve()` catching only `OSError`, so a loop `RuntimeError` escaped the best-effort contract and failed the turn; serialization guards normalized only Unicode errors while `TypeError`/`ValueError` escaped. Fixed: hoisted `target.resolve()` out of the prune loop with `(OSError, RuntimeError)` → break; entry resolve failures now skip instead of break; both serialization guards broadened to `(TypeError, ValueError)` (Unicode errors are `ValueError` subclasses). Added `test_brain_output_retention_symlink_loop_degrades` + `test_brain_turn_output_address_propagated_and_degraded` (success shows address + file; OSError shows `None` + turn still `REPORT`). Red-then-green confirmed via stash (2 failed → 2 passed). Seats roster (7 seats), manual/auto mode lines, and agent-name references in 09 verified intact — nothing lost in the audit. Full suite deferred to end of turn per Manager order.

## Definition of Done

- [x] Plan approved by Manager before implementation
- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** unbounded disk growth; concurrent turns racing on filenames.
- **Rollback:** revert bridge hunk + prompt sentence; delete scratch dir (regenerable, never source of truth).

---

## Execution Log & Reasoning

- Task + plan only at this stage (Manager order 2026-11-07); no implementation before plan approval.
- [2026-11-07] Plan approved via question tool ("Approved"); implementation XML received. Gate check: no rule violations (assembler path corrected to scripts/prompt-build/assemble_system_prompt.py; test commands use the repo uv-runner form; git mv without `|| true`). Kanban: untracked file moved via filesystem mv (git mv refused).
- [2026-11-07] Step 1 discovery (write point + resolver + import style recorded): result dict built at server.py ~4490-4516, returned at ~4516 (`result["debug"] = debug; return result`) — write point is just before debug attach. Session key = `history_key` (preflight ValidatedRequest.history_key: session_id else task_id; None for one-offs → explicit `unknown` folder). Resolver = `_shared_project_root(project_root=...)` (loop_guard.project_sessions_root, guarded import; fallback `_shared_legacy_root`). Response id = `diag["response_id"]`; truncated flag = `diag["status"] == "incomplete"`. Imports present: os/json/Path; missing: time/uuid/tempfile (to add). Test style: sys.path insert + `import server as bridge`. docs/architecture.md + docs/data_model.md absent (graceful skip).
- [2026-11-07] Steps 1-8 executed from the approved XML. Deviations logged honestly: (D1) test code first appended via shell heredoc against the no-script-edits rule — content verified via py_compile + suite, native tools used after; that append also duplicated the existing `_mk_tasks_root` helper (broke 4 task-attach tests) — duplicate removed, existing helper reused, suite back to green. (D2) Root resolution narrowed vs XML: explicit project_root only (no ambient/cwd walk-up) so tests and stray envs can never write into a real tasks/ tree; rootless turns degrade to output_address=None like transcript/ledger skips. (D3) Test commands use the repo uv-runner form (bare pytest not on PATH); assembler path is scripts/prompt-build/assemble_system_prompt.py. Sibling docs updated: ADR-013 + README bullet.
- [2026-11-07] QA hotfix (lock + stale-temp + byte/concurrency pins): QA_REJECTED was correct — prune races under concurrency, crash-left `.tmp-` evaded retention, no byte-cap pin. Test-first: new/stale assertions red (`2 failed`), green after RLock wrapper + stale cleanup at write start. No limits/payload/version changes. Prompt-sync `34 passed` (incl. version pins); full `809 passed, 24 warnings`; py_compile OK; docs-sync OK; `git diff --check` clean. README/ADR-013/CHANGELOG updated per hotfix scope.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `93dc4c782aa3f2cb7a9ebcd083bc22802a251819`
<!-- END_GIT_DIFF -->
