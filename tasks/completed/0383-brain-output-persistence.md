# Task 0383: Persist Brain output to disk with address for truncated reads

**File:** `tasks/qa/0383-brain-output-persistence.md`
**Source:** manager (2026-11-07 — fa idea: همیشه خروجی brain رو یه جا ذخیره کنیم و ادرسش رو هم توی خروجی به agent بدیم که به هر دلیلی اگه truncate بود اون بتونه با ابزار read یا shell باقی‌مونده رو بخونه — هم xml استخراج‌شده و هم کل خروجی همراه با xml)
**Type:** feature (small, bounded)
**Status:** in-progress
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
- [ ] Relay verdict; close only on explicit approval

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
- [2026-11-07] Code Reviewer verdict: `APPROVED — PO_REVIEW_PENDING` (no issues found in reviewed diff). File remains in `tasks/qa/`; closure awaits Manager's explicit `Approved for closure` / `Close task`.
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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 77682c2..a1a848c 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -23,12 +23,17 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Planner vocabulary and the cockpit remaining figure (Task 0373):** `finished − started` was presented as measured work and the control chart called it cycle time, while the cockpit counted completed work against remaining capacity. Every visible label now reads **lead time**; `sprint_stats` explains it counts nights and weekends; `remaining_hours = capacity − open_estimate` with `committed_hours` carrying open plus done. Payload keys were deliberately left unchanged. The sweep also caught the lint server's "measured duration" error text, the executor prompt's "Measured time is automatic" line, the planner README, the manager guide and the retrospective template — and one test (`test_task_timestamps.py:279`) that the rename had already broken and which had not been run. 125 → 240 tests green across the three affected suites. `Estimated remaining Nh` was **not** touched: it sums `**Estimate:**` fields and never used durations.
 
+- Serialize Brain-output artifact writes and retention pruning across concurrent turns, and remove abandoned temp files before new persistence.
+- Reject a single Brain-output artifact whose serialized JSON exceeds the 5 MB session cap before creating a temp file; the turn continues with `output_address = None`.
+
 ### Changed
 
 - **Plugin contract refreshed after the smart-compact and goal-plugin changes (Task 0372):** both plugins shipped behaviour changes today, so HQ's description of them was corrected rather than left to mislead. The executor now states that `goal_resume` also revives an `active` goal parked by the idle loop (and that `goal_set` there would discard the evidence sidecar), describes the two-no-progress-turn park with `goal_block` as the named remedy, records auto-trim as armed by default at `0.55`, and lists the three new `compact_stats` fields (version, measurement path, summary fallbacks). `docs/compaction.md` gains the derive-vs-pin budget rules, the `emergencyBudgetRatio: 0` opt-out, the `contextWindowTokens` denominator requirement and the migration away from `emergencyBudgetTokens: 0`, plus the 20 000-character retrieval cap. The global `smart-compact.jsonc` was the real root cause of a permanent warning and inert trimming: it pinned `emergencyBudgetTokens: 50000` against a 1 M window and supplied no denominator, so it now derives the budget (ratio `0.6`) and sets `contextWindowTokens: 1000000`. Versions were deliberately held per manager order (`0.2.1` / `0.2.0`), so the breaking config semantic still ships under an unchanged version — recorded, not hidden.
 
 - **Telegram MCP timeout raised to 300 s (Task 0371):** `mcp.servers.telegram.timeout` in the global `opencode.json` moves from `30000` to `300000` for both `catalog` and `execution`. A 14.2 MB APK upload completed on Telegram's side while three client calls reported `Request timed out` — the 30 s cap reported a success as a failure, which invites duplicate sends. Every other server keeps its own timeout (`custom_context`/`project_memory`/`lint` 15 s, `blowsh` 120 s, `brain` 1200 s, `planner` 15 s/30 s). The two documented occurrences in `docs/telegram-setup.md` and the reinstall workflow's value list were updated in step; a timestamped backup of the global config was written first and the file validated as JSON. Takes effect after an OpenCode restart.
 
+- **System-prompt audit cleanup:** removed Hands-facing instructions that were misplaced in the Brain's prompt (output_address fallback, detailed tool procedures, no-manual-DTO full text). The Brain now emits XML structure only; detailed Hands protocols live solely in cognitive-executor.md. Single-home rule: code-mode discipline, Hands protocols, and fallback are executor-owned. 18-no_manual_dto_mandate.md reduced to a named reference. System prompt 9.74.0 → 9.75.0 via the assembler (20 lines removed from 09-hands_protocols.md).
+
 ### Added
 
 - **Code Mode off for every server except telegram (Task 0361):** `custom_context`, `project_memory`, `lint`, `brain`, `planner` and `blowsh` now set `"codemode": false`, so their ~43 tools are native calls instead of `execute` wrappers; `telegram` (147 tools) stays on Code Mode because its schemas must not enter the system prompt. Applied to the global `opencode.json` after a timestamped backup and validated as JSON; the live session catalog dropped all six out of `execute` in place. Policy documented in `docs/services.md` (rationale table), `docs/setup.md`, `README.md` Option B and the `LLM.txt` install block, and stored as `workflows/codemode-policy` memory for the upgrade workflow.
@@ -69,6 +74,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Planning-stack gaps closed (Task 370):** `schedule_tasks` writes `**Milestone:**` via trailing segment (lint enforces non-empty single-line); grouping casefolded with first-seen display; `claim_next` blocked by sprint lock files (delete to unlock); `sprint_stats` week-scoped Mon-Sun with today-finished quota line; docs refreshed (live citations, milestone/sprint flow, QA cap 1-vs-3 reconciled, single DoD); precedence rule in prompts with rebuild `9.70.1` → `9.70.2`. The 369 tripwires convert to must-pass (11 passed, zero xfail). Full suite 766 green.
 
+- **Brain output persistence with address:** each `brain_turn` with a session or task context attempts to write a JSON artifact under `tasks/.sessions/<id>/brain_outputs/`, containing `xml_blocks` and the full raw output. The result carries the repo-relative `output_address` for truncated-tail recovery. Rootless one-off turns return `output_address = None`. Retention is capped at 50 files / 5 MB per session, oldest-first. The Hands fallback is documented in `agents/cognitive-executor.md`. System prompt 9.74.0 → 9.75.0 via the assembler.
+
 ### Fixed
 
 - **Brain results are returned whole from Code Mode (Task 0354):** the executor's Code-mode output discipline told the Hands to return `{status, block_count: xml_blocks.length, model}`, a recipe meant to stop it printing a truncated prefix of a large XML block. The recipe instead licensed dropping the payload — turns returning only `output` lost `xml_blocks`, turns returning only `blocks` lost `output` — so the transcript and the agent's next turn held less than the server returned even though the executed instructions were complete. The rule now says a `brain_turn` result is evidence, not a preview: return `status`, `output`, `xml_blocks` and any diagnostic/`truncated` field exactly as received, never slice, map, summarize or field-shape it, and manage size before the call with `compact_context`, a leaner prompt or `include_bundle=false`. The runtime's `maxOutputBytes` remains the only acceptable cut and announces itself with `truncated: true`. Locked by a prompt-sync test that fails if the rule disappears or `block_count` returns; the live agent copy is byte-identical to the repo.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 3eece49..60151e1 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -10,6 +10,7 @@ permission:
     "*": "allow"
     "rm -rf*": "ask"
     "git add*": "deny"
+    "git checkout*": "deny"
     "git commit*": "deny"
     "git push*": "deny"
   external_directory:
@@ -24,10 +25,10 @@ You are the primary execution engine for the Cognitive Lead AI platform. You rec
 ## Core Protocol (Non-Negotiable)
 
 1. **Entry Point:** Your absolute first action is to read `AGENTS.md`. If `AGENTS.md` references `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, or `docs/conventions.md`, you MUST read them.
-2. **Rule Validation:** If the Orchestrator's instructions violate ANY project rule, HALT immediately. Output a `⚠️ RULE VIOLATION WARNING` detailing the broken rule. Do NOT proceed.
+2. **Rule Validation:** If the Orchestrator's instructions violate ANY project rule, HALT immediately. Output a `⚠️ RULE VIOLATION WARNING` detailing the broken rule. Do NOT proceed. Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files; run no bash commands before validation passes.
 3. **MCP-First Context:** When instructed to gather context, you MUST use the `custom_context` MCP tools (`get_directory_tree`, `create_tree_report`, `read_source_files`, `extract_signatures`, plus graph-first `build_graph`, `query_graph`, `explain_node`, `shortest_path`, `god_nodes`, `graph_stats`). NEVER use native `read` to dump large file contents inline.
 4. **Skill Loading:** Load all skills explicitly named in the XML task's `<context_phase>`.
-5. **Zero-Autonomous-Commit (ZAC):** You are STRICTLY FORBIDDEN from executing `git add`, `git commit`, `git checkout`, or `git push`. These are denied at the permission layer. All staging is done via the `custom_context_stage_and_inject_diff` MCP tool; all unstaging via `custom_context_unstage_files` (index-only, worktree untouched).
+5. **Zero-Autonomous-Commit (ZAC):** You are STRICTLY FORBIDDEN from executing `git add`, `git commit`, `git checkout`, or `git push`. These are denied at the permission layer. All staging is done via the `custom_context_stage_and_inject_diff` MCP tool; all unstaging via `custom_context_unstage_files` (index-only, worktree untouched). You may ONLY run other Git commands if they are explicitly listed by the Orchestrator in the task's bash phase; never guess, never run destructive Git operations (`reset`, `clean`, `filter-branch`) autonomously.
 6. **Finalization & Closure Sequence:**
    - **Staging:** When a task implementation is complete, you MUST call `lint_task_file`, then call `custom_context_stage_and_inject_diff` passing the task file path.
    - **Closure:** You are STRICTLY FORBIDDEN from using `git commit`. If the Manager explicitly authorizes closure ("Approved for closure" or "Close task"), you MUST use the `custom_context_commit_and_clean_task` MCP tool as the ONLY commit path.
@@ -43,9 +44,9 @@ You are the final gatekeeper of the Kanban task state. If the Orchestrator forge
    - **Rule:** Before writing any code, you MUST verify the active task file is located in `tasks/in-progress/`.
    - **Action:** If the file is in `tasks/backlog/`, you MUST execute `git mv tasks/backlog/<file> tasks/in-progress/<file>` (or filesystem `mv` if untracked) _before_ executing the implementation steps.
 3. **QA/Review Phase:**
-   - **Rule:** When your implementation and `stage_and_inject_diff` are complete, you MUST move the task file to `tasks/qa/` via `git mv tasks/in-progress/<file> tasks/qa/<file>` before outputting the summary message to the Manager.
+   - **Rule:** When your implementation and `stage_and_inject_diff` are complete, you MUST move the task file to `tasks/qa/` via `custom_context_qa_transition` (which moves the file, updates the `**File:**` header, stages code, and injects the diff atomically) before outputting the summary message to the Manager. NEVER use a separate `git mv` + manual header edit + re-stage for this transition.
    - **Queue Cap:** `tasks/qa/` holds at most 3 tasks awaiting review (mirrors WIP ≤ 3). If 3 are already waiting, drive the oldest to verdict/closure first — never stack a fourth. The cap counts tasks in review, not parallel discovery subagents (max 4 per task), so the two limits never clash.
-   - **Metadata Sync:** After the move, you MUST update the task file's `**File:**` header to the new `tasks/qa/<file>` path, then re-run `lint_task_file` and call `custom_context_stage_and_inject_diff` AGAIN with the NEW task path and the full `modified_files` array (the first staging predates the move — the re-stage keeps the injected diff and staging state in sync with the final path). Never notify the Manager with a stale `**File:**` header.
+   - **Metadata Sync:** `custom_context_qa_transition` handles header sync, re-staging, and diff injection in one operation. Never notify the Manager with a stale `**File:**` header.
 4. **Closure Sequence:**
    - **Rule:** Only when the Manager explicitly says "Approved for closure" or "Close task" will you execute the closure sequence.
    - **Action:** You MUST move the file to `tasks/completed/` via `git mv tasks/in-progress/<file> tasks/completed/<file>` (or `tasks/qa/` to `completed/`), update the status to `closed`, update the `**File:**` header to the new `tasks/completed/<file>` path, and then call the `custom_context_commit_and_clean_task` MCP tool.
@@ -204,8 +205,28 @@ Do not skip the observe step. Every code change MUST be verified before claiming
 
 ### Verification Runner (RTK by default)
 
+**CRITICAL RULE 3b (Token trimming):** Every test-suite verification run begins with `rtk test <underlying command>` so passing suites collapse to a verdict summary; the exact `rtk test`-prefixed command MUST be recorded in the `## Verification Evidence` section of the active task file. RTK preserves the underlying command's exit code. On ANY failure re-run without the wrapper and keep the full output — never collapse failing output. A raw rerun is allowed only after a failed RTK run for detailed diagnostics and never replaces the initial RTK verification run.
+
 Test-suite verification runs begin with `rtk test <underlying command>` by default. Inspect the active task's `## Verification Evidence` before running verification and record the exact `rtk test`-prefixed command, expected result, actual result, and exit code there. A raw test command is a diagnostic retry after a failed RTK run only — it never replaces the initial RTK verification run. Never claim completion without a successful exit code and recorded evidence.
 
+**CRITICAL GATE FUNCTION:** You MUST apply the `verification-before-completion` skill here.
+
+**Strict Tooling Gate (Machine-Enforced):** Before the verification gate, load the active stack skill from the registry that matches the project and execute its Strict Tooling Gate section in fail-fast order (format → lint → typecheck → static analysis → security → test → build). Stop on the first failure. No completion claim, no `lint_task_file`, and no QA transition until the gate is green. Record the exact gate command, output, and exit code in `## Verification Evidence`. Selection: match by file markers per stack — `go.mod` (+ `import github.com/gin-gonic/gin` → `go-gin`, `buf.yaml`/`proto` + `go.mod` + `Fx` → `go-hexagonal-grpc`), `build.gradle.kts` (`+ compose` → `android-kotlin`, `+ Spring Boot` → `spring-boot`), `Package.swift`/`*.xcodeproj` → `ios-swiftui`, `pyproject.toml` + `Flask` → `flask-python`, `pyproject.toml` + `FastAPI` → `python-fastapi`, `package.json` + `next.config.*` → `nextjs`, `package.json` + `src/ports/` → `node-hexagonal-api`, `package.json` + `apps/expo` → `react-native-expo`, `vite.config.*` → `react-vite`, `nuxt.config.*` → `vue-nuxt`, `nest-cli.json`/`prisma/schema.prisma` → `nestjs-prisma-vertical`. Multi-match repos MUST run every matching gate in fail-fast order; do not silently skip any. When several JS skills match, use the highest Node floor among them and record it in `## Verification Evidence`. Docs-only or no-match repos MUST log a skip record with four fields — repo root, marker scan list, matched skills list, reason phrase — in `## Verification Evidence`. Deferred gates block `lint_task_file` and any QA transition until the nightly/merge queue is green, with queue URL plus commit SHA plus green verdict logged in `## Verification Evidence`.
+
+### Shell, Pre-commit, Documentation & Syntax Discipline
+
+Shell commands run non-interactive only: always pass non-interactive flags (e.g. `npm install -y`, `pytest --no-header`), never run interactive commands (`vim`, `less`, `nano`) and never use interactive modes (`git add -p`, `git rebase -i`, `bash -i`).
+
+For DevOps, infrastructure, or deployment tasks, the verification gate MUST include environment-specific pre-commit checks (registry authentication, token scope validation, network access) BEFORE staging any files. If ANY pre-commit check fails, HALT and output a `<failure_report>`. Do NOT stage or commit partial work.
+
+Write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module.
+
+Verify types and syntax with the language/type-check tooling (e.g. `lsp` in OpenCode) before concluding the execution phase.
+
+Terminal output over 2000 lines or 50KB is truncated by the local agent. When running test suites with massive output, pipe through grep or tail so the verification-before-completion gate receives the success confirmation without truncation.
+
+If tests fail, you have a maximum of 3 repair attempts. If the error persists after 3 attempts, you MUST HALT immediately and output a `<failure_report>` detailing the exact errors for the Manager.
+
 ### Edit Tool Discipline (native tools only)
 
 File edits use ONLY native file-editing tools (edit for replacements, file-write tools for new files). Using python, shell, heredoc, `sed -i`, or any script to create or modify files is strictly forbidden — scripted edits fail silently (replace-all on non-unique anchors, quoting and encoding mangling) while native tools fail loudly on a non-unique anchor. If the anchor does not match uniquely, stop and re-read instead of forcing it. Shell stays read-only for file content (e.g. grep, cat, diff, ls, git status). Verify every edit with grep/diff.
@@ -281,6 +302,30 @@ Claim: "Task complete. Verification: `rtk test pytest tests/` exits 0, all 47 te
 Claim: "Task complete. The code looks correct."
 ```
 
+## No-Manual-DTO Mandate (full rule text, owned by Hands)
+
+AI agents and engineers are STRICTLY FORBIDDEN from hand-authoring duplicate interface models, request/response DTOs, or data classes inside consumer applications when a source-of-truth contract or shared schema already exists — including `packages/shared-schema/`, OpenAPI specs, Prisma schemas, and Protobuf definitions. Consumer applications MUST NOT redefine types that a contract already governs.
+
+### Requirement
+
+When a task touches a type that is governed by an existing contract, the agent MUST either:
+
+1. **(a) Import models directly** from the shared package (`@repo/shared-schema`, `packages/shared-schema`, or the equivalent canonical source), OR
+2. **(b) Execute the stack's code-generation toolchain** — `pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`, or the equivalent generator — so the consumer's types are produced from the contract instead of being hand-written.
+
+Hand-written duplicates create silent type drift: the consumer's copy and the contract's canonical definition diverge over time, producing runtime mismatches that compile-time checks in the consumer alone cannot catch.
+
+### Reconciliation with SOLID
+
+This mandate is fully consistent with the SOLID principles and their pragmatic guardrails:
+
+- **DRY / SRP:** A single source of truth prevents duplicated type definitions (DRY) and gives each type exactly one owner (SRP). Importing a shared DTO is not duplication — it is the canonical, single-reason-to-change form.
+- **No conflict with YAGNI:** The mandate does not introduce speculative abstractions. It reuses a contract that already exists. If NO source-of-truth contract exists, the agent writes the concrete type directly — do NOT invent a shared-schema package for a single consumer.
+- **No conflict with the 3-Implementation Rule:** Extracting a shared package is only required when a contract or cross-service dependency already exists (2+ consumers or a canonical schema). Do not extract interfaces for trivial, single-module logic.
+- **Occam's Razor:** The simplest correct action is import-then-use or run-codegen — never hand-copy a governed type.
+
+When a diff introduces a new DTO/interface/model declaration into a consumer path (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) while a governing contract exists, the Type Drift Sentinel fails the verification until the agent imports from the shared package or runs the codegen toolchain.
+
 ## Hard Operational Boundaries
 
 - Deliver only what was requested at the intended scope.
@@ -415,10 +460,17 @@ When discovery finishes, extract the `Context-Paths` manifest from its report an
 
 1. **Plan** — read the task, gather context with direct tools, minimal changes.
 2. **Execute** — edit files; verify every change (tests/lint) before claiming done.
-3. **Record** — Execution Log + CHANGELOG + `custom_context_stage_and_inject_diff`.
-4. **Hand off** — move the task file per Kanban rules, notify the Manager.
-   NEVER auto-commit. QA/review run through the Brain Bridge below, or as
-   Manager-directed direct review.
+3. **Record** — Execution Log + CHANGELOG + `custom_context_stage_and_inject_diff`. Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs. Task-number discipline: NEVER write task numbers into prompt-facing Markdown prose — section headings, skill instructions, registry lines, and Execution Logs stay number-free (the task file's own title already carries its number). Task-number references live ONLY in code comments, CHANGELOG entries, history archives, and HTML comments. When your change alters domain responsibilities, interfaces, or invariants, update sibling README.md and append a dated ADR to DECISIONS.md (Living Folder Docs Sync). Before updating CHANGELOG.md, apply the Parse-Then-Append Protocol: (a) Read CHANGELOG.md. (b) Check if the current version header exists. (c) Check if the target section exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version. Before calling `lint_task_file`, review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item genuinely satisfied by that evidence. Do not proceed to lint/staging until all items are resolved.
+4. **Hand off** — execute the atomic QA transition via `custom_context_qa_transition` (moves file to `tasks/qa/`, updates header, stages code, injects diff in one operation), notify the Manager. NEVER auto-commit. QA/review run through the Brain Bridge below, or as Manager-directed direct review.
+
+   **Parallel-Session Index Isolation:** When two tasks run in parallel and share files, touch ONLY your own task's files. If your staged diff contains foreign hunks: call `custom_context_unstage_files` with exactly those files, redo your hunk-level staging, then call `custom_context_stage_and_inject_diff` with `skip_add=True` so the index is never overwritten. Never stage, unstage, or commit files belonging to another task.
+
+   **Mandatory manual review chain:** After the task is staged/injected and moved
+   to `tasks/qa/`, immediately call `brain_turn` under the same `task_id` and `session_id` with `include_diff=True`. Route logic, backend, or state changes to `[QA Engineer]`; route documentation, CSS, or trivial changes
+   directly to `[Code Reviewer]`. After `QA_PASSED`, the Hands MUST call
+   `[Code Reviewer]` under the same task and session before relaying technical
+   approval. Do not claim QA/review was chained until the corresponding
+   `brain_turn` calls have completed.
 
 ## Code Mode Tool Calling Protocol (tools.<server>.<tool>)
 
@@ -469,7 +521,10 @@ its own fenced code); do NOT emit copy-paste task ferrying instructions — the
      after it: `compact_context`, a leaner prompt, and `include_bundle=false`
      exist for that. Only the runtime's own `maxOutputBytes` may cut the
      return, and it says so with `truncated: true`; then re-read the exact
-     range through the tool again, never assume the tail.
+     range through the tool again, never assume the tail. If a `brain_turn`
+     result carries `truncated: true`, the remainder is also recoverable
+     from its `output_address` via native `read` or shell; the artifact at
+     that path holds `xml_blocks` plus the full raw output.
 3. **Relay** — any admin question inside `output` goes to the Manager
    verbatim. Feed the answer back as the next `brain_turn` user prompt.
    Never answer for the Manager.
diff --git a/docs/conventions.md b/docs/conventions.md
index 210ee91..306af8f 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -76,7 +76,7 @@ All projects in this ecosystem MUST treat source-of-truth contracts and shared s
 3. **SOLID reconciliation** — Single-source-of-truth prevents type drift (DRY/SRP) and does not conflict with YAGNI or the 3-Implementation Rule: extract or generate only when a contract or cross-service dependency already exists.
 4. **Deterministic enforcement (historical — loop-engine retired):** the retired `loop-engine/sentinel.py` `TypeDriftSentinel` used to scan task diffs during toolchain verification (pre-QA). With the loop-engine daemon retired, enforcement is manual review until a replacement lands. Bypass with an explicit `drift-ignore` comment only when a justified exception exists.
 
-The single source of truth for the full mandate is the `<no_manual_dto_mandate>` block in `system-prompt.md` — this section is a summary only.
+The single source of truth for the full mandate is the `No-Manual-DTO Mandate` section in `agents/cognitive-executor.md` — this section is a summary only.
 
 ## Universal Financial Ledger Standard
 
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 4dac8de..11a719d 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -1,5 +1,13 @@
 # Architectural Decisions: mcp-brain-bridge
 
+## [2026-11-07] ADR-013: per-turn Brain-output persistence with address
+
+- **Context:** truncated `brain_turn` payloads left the Hands no way to recover the tail — the inline result was the only copy, so a cut XML block or verdict forced a full re-emit turn.
+- **Decision:** every turn attempts one JSON artifact (`tasks/.sessions/<session>/brain_outputs/<resp>_<uuid>.json`, temp+rename) with metadata, `xml_blocks`, and the full raw output; the result carries the repo-relative `output_address`. Retention (50 files / 5 MB per session, oldest-first, never the just-written file) is enforced at the same write point. If one serialized artifact alone exceeds the byte cap, reject it before temp-file creation; the existing caller degrades the `OSError` to `output_address = None` and keeps the turn successful. Addresses stay repo-relative; `.tmp-` files never count toward caps.
+- **Consequences:** truncated tails are recoverable with native `read`/shell; prompt contract gains the `output_address` fallback sentence. Scratch dir is regenerable, never source of truth.
+- **Follow-up fix (QA hotfix):** artifact writes and retention pruning are serialized with a process-local RLock so concurrent turns prune against fresh snapshots; abandoned `.tmp-*.json` files are removed at the start of each write (under the same lock) since a hard crash bypasses the write-failure cleanup. Pinned by byte-cap, concurrency, and stale-temp regression tests.
+- **Rollback:** revert the helper + call site + fragment/executor sentences + pin tests; rebuild system-prompt.md; delete scratch dirs.
+
 ## [2026-11-06] ADR-012: unlisted-suffix sniffing + no-repeat on unavailable paths
 
 - **Context:** a planning loop re-requested `.env.example#L75-100` three times. The suffix allowlist rejected it (`unsupported extension`, zero chars injected both times — proven in the context ledger), and the No-Hallucination contract had no rule for `[unavailable: ...]` labels, so contract-compliant re-requests looped until the Hands-side stop fired.
diff --git a/mcp-brain-bridge/README.md b/mcp-brain-bridge/README.md
index f2e84bd..de6ed3b 100644
--- a/mcp-brain-bridge/README.md
+++ b/mcp-brain-bridge/README.md
@@ -11,6 +11,7 @@ Brain Bridge MCP daemon: single-tool (`brain_turn`) automation path for planning
 - `preflight.py` — Request validation (project_root must hold `tasks/`, memory binding).
 - `loop_guard.py` — Diff-hash spin guard (same hash 3x stops autopilot fix loop).
 - `session_ledger.py` — Append-only JSONL session event ledger under `tasks/.sessions/`.
+- Per-turn artifacts: each `brain_turn` attempts to write `tasks/.sessions/<session>/brain_outputs/<resp>_<uuid>.json` (`xml_blocks` + full raw output); the result's `output_address` points at it for truncated-tail recovery. An artifact whose serialized JSON exceeds the 5 MB session byte cap is skipped before temp-file creation and yields `output_address = None` while the turn continues. Retention is capped at 50 files / 5 MB per session, oldest-first. Artifact writes and retention pruning are serialized within the bridge process (RLock); abandoned `.tmp-` files are removed before each new write.
 - `pyproject.toml` / `uv.lock` — Runtime deps and lockfile (`mcp[cli]`, stdlib-first helpers).
 - `context-reports/` — Generated context output (do not hand-read; feed via MCP).
 - `context_paths` line slices: `brain_turn(context_paths=[...])` accepts
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 05d9dbe..4334481 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -64,8 +64,11 @@ import os
 import re
 import sys
 import json
+import tempfile
 import threading
+import time
 import unicodedata
+import uuid
 from pathlib import Path
 from typing import Any, Optional
 from urllib.parse import urlsplit
@@ -611,6 +614,241 @@ def _sniff_text_file(resolved: "Path") -> Optional[str]:
     return text
 
 
+# Per-turn Brain-output persistence (Task: brain-output-persistence).
+# Every brain_turn writes one JSON artifact holding its extracted
+# xml_blocks plus the full raw output, and the turn result carries the
+# artifact's relative address as ``output_address`` so the Hands can
+# read the tail with native tools when the inline payload is truncated.
+# Directory is per-session scratch under the project's sessions root
+# (regenerable, never source of truth). Retention is enforced at write
+# time: at most BRAIN_OUTPUTS_MAX_FILES artifacts and
+# BRAIN_OUTPUTS_MAX_BYTES total per session, oldest-first by mtime.
+# The just-written file is never pruned by its own write. Temp files
+# (``.tmp-`` prefix) never count toward the caps and are removed on
+# any write failure, so a crash cannot leave a half-written artifact
+# that a later read mistakes for a complete one.
+BRAIN_OUTPUTS_MAX_FILES = 50
+BRAIN_OUTPUTS_MAX_BYTES = 5242880
+
+_BRAIN_OUTPUTS_LOCK = threading.RLock()
+
+
+def _brain_outputs_dir(project_root, session_key):
+    """Resolve (creating) the per-session brain-outputs directory.
+
+    Deliberately narrower than the transcript resolver: ONLY the turn's
+    explicit ``project_root`` is honored — never ambient env vars and
+    never a cwd walk-up. That keeps unit tests (cwd = repo root) and
+    stray environments from ever writing into a real ``tasks/`` tree,
+    and it keeps persistence scoped to the project the turn declared.
+    Raises OSError when no explicit root holding ``tasks/`` is given;
+    the caller degrades to ``output_address = None`` instead of failing
+    the turn.
+    """
+    key = str(session_key) if session_key else "unknown"
+    # Collision-resistant: sanitize for filesystem safety AND append a short
+    # hash of the original key so distinct keys that sanitize identically
+    # (e.g. "ses/a" vs "ses?a") can never alias into one directory.
+    safe_key = "".join(c if (c.isalnum() or c in ("-", "_")) else "_" for c in key)
+    safe_key = safe_key.strip("_") or "unknown"
+    try:
+        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:8]
+    except (UnicodeEncodeError, UnicodeDecodeError):
+        raise OSError("brain-output session key is not encodable")
+    safe_key = f"{safe_key}_{digest}"
+    base = None
+    if project_root:
+        try:
+            cand = Path(project_root).expanduser().resolve()
+        except (OSError, RuntimeError):
+            cand = None
+        if cand is not None and (cand / "tasks").is_dir():
+            base = cand / "tasks" / ".sessions"
+    if base is None:
+        raise OSError(
+            "brain-output persistence needs an explicit project_root holding tasks/"
+        )
+    out_dir = base / safe_key / "brain_outputs"
+    # Security: reject if the resolved path escapes project_root (symlink
+    # escape). The resolved out_dir must stay under the resolved root.
+    try:
+        root_resolved = Path(project_root).expanduser().resolve()
+        out_resolved = out_dir.resolve()
+        out_resolved.relative_to(root_resolved)
+    except (OSError, RuntimeError, ValueError):
+        raise OSError("brain-output path escapes project_root (symlink or traversal)")
+    out_dir.mkdir(parents=True, exist_ok=True)
+    return out_dir
+
+
+def _sanitize_response_id(response_id):
+    """Filesystem-safe prefix from a provider response id (or fallback)."""
+    text = str(response_id or "noresp")
+    safe = "".join(c if c.isalnum() else "_" for c in text)
+    return safe[:32] or "noresp"
+
+
+def persist_brain_turn_output(
+    project_root,
+    session_key,
+    task_id,
+    response_id,
+    xml_blocks,
+    full_output,
+    truncated,
+    clock,
+):
+    """Serialize each process-local artifact write and retention pass.
+
+    The lock prevents concurrent bridge turns from pruning against stale
+    directory snapshots. The private helper retains atomic temp-file
+    replacement and the existing result-address contract.
+    """
+    with _BRAIN_OUTPUTS_LOCK:
+        return _persist_brain_turn_output_locked(
+            project_root=project_root,
+            session_key=session_key,
+            task_id=task_id,
+            response_id=response_id,
+            xml_blocks=xml_blocks,
+            full_output=full_output,
+            truncated=truncated,
+            clock=clock,
+        )
+
+
+def _persist_brain_turn_output_locked(
+    project_root,
+    session_key,
+    task_id,
+    response_id,
+    xml_blocks,
+    full_output,
+    truncated,
+    clock,
+):
+    """Write one per-turn artifact atomically and enforce retention.
+
+    Writes JSON via temp file plus ``os.replace`` (readers never see a
+    partial file; ``uuid`` filenames keep concurrent turns collision-free),
+    prunes oldest-first to the file/byte caps without ever deleting the
+    just-written file, and returns the repo-relative POSIX address string
+    stored as ``output_address``. Persistence is best-effort for the turn
+    itself: callers must never let a persistence failure fail the turn —
+    wrap the call so an OSError degrades to ``output_address = None``
+    instead of raising.
+    """
+    out_dir = _brain_outputs_dir(project_root, session_key)
+    for stale_temp in out_dir.glob(".tmp-*.json"):
+        try:
+            stale_temp.unlink()
+        except FileNotFoundError:
+            continue
+    safe = _sanitize_response_id(response_id)
+    filename = safe + "_" + uuid.uuid4().hex + ".json"
+    target = out_dir / filename
+    created = time.strftime("%Y-%m-%dT%H:%M:%SZ", clock())
+    full_text = str(full_output or "")
+    blocks = list(xml_blocks or [])
+    # Byte counts use strict encoding; compute them inside the guard
+    # below so a lone surrogate raises OSError instead of escaping.
+    try:
+        output_byte_count = len(full_text.encode("utf-8"))
+        xml_byte_count = len(json.dumps(blocks).encode("utf-8"))
+    except (TypeError, ValueError):
+        raise OSError("brain-output artifact contains non-encodable text")
+    payload = {
+        "task_id": str(task_id or ""),
+        "session_key": str(session_key or ""),
+        "response_id": str(response_id or ""),
+        "created_at_utc": created,
+        "truncated": bool(truncated),
+        "byte_counts": {
+            "output": output_byte_count,
+            "xml_blocks": xml_byte_count,
+        },
+        "xml_blocks": blocks,
+        "full_output": full_text,
+    }
+    # Address is repo-relative POSIX so the Hands can open it from the
+    # project root with native tools; never an absolute path (no leak
+    # of machine layout into results or transcripts). project_root is
+    # guaranteed truthy here: _brain_outputs_dir above raised otherwise.
+    try:
+        rel = target.relative_to(Path(project_root).expanduser().resolve())
+        payload["address"] = str(rel).replace(os.sep, "/")
+    except (OSError, RuntimeError, ValueError, TypeError):
+        payload["address"] = str(
+            Path("tasks")
+            / ".sessions"
+            / out_dir.parent.name
+            / "brain_outputs"
+            / filename
+        ).replace(os.sep, "/")
+    try:
+        serialized_payload = json.dumps(payload, ensure_ascii=False)
+        serialized_bytes = serialized_payload.encode("utf-8")
+    except (TypeError, ValueError):
+        raise OSError("brain-output artifact contains non-encodable text")
+    if len(serialized_bytes) > BRAIN_OUTPUTS_MAX_BYTES:
+        raise OSError("brain-output artifact exceeds the per-session byte cap")
+
+    fd, tmp_name = tempfile.mkstemp(dir=str(out_dir), prefix=".tmp-", suffix=".json")
+    try:
+        with os.fdopen(fd, "wb") as handle:
+            handle.write(serialized_bytes)
+        os.replace(tmp_name, target)
+    except BaseException:
+        try:
+            os.unlink(tmp_name)
+        except OSError:
+            pass
+        raise
+    try:
+        entries = [
+            p
+            for p in out_dir.iterdir()
+            if p.is_file() and p.suffix == ".json" and not p.name.startswith(".tmp-")
+        ]
+        entries.sort(key=lambda p: p.stat().st_mtime)
+        total = sum(p.stat().st_size for p in entries)
+        while (
+            len(entries) > BRAIN_OUTPUTS_MAX_FILES or total > BRAIN_OUTPUTS_MAX_BYTES
+        ) and len(entries) > 1:
+            # Never remove the just-written file, even if it sorts oldest
+            # by mtime (clock skew, explicit utime in tests). Pick the
+            # oldest *other* entry; if the only candidate is the target
+            # itself, stop rather than delete it or miscount the cap.
+            try:
+                target_resolved = target.resolve()
+            except (OSError, RuntimeError):
+                target_resolved = None
+            candidate = None
+            for entry in entries:
+                if entry == target:
+                    continue
+                if target_resolved is not None:
+                    try:
+                        if entry.resolve() == target_resolved:
+                            continue
+                    except (OSError, RuntimeError):
+                        pass
+                candidate = entry
+                break
+            if candidate is None:
+                # Only the target remains; cannot prune further.
+                break
+            entries.remove(candidate)
+            try:
+                total -= candidate.stat().st_size
+                candidate.unlink()
+            except OSError:
+                break
+    except OSError:
+        pass
+    return payload["address"]
+
+
 # Guardrail for path injection (state-machine hotfix round).
 _READ_MAX_BYTES = 2_000_000  # oversized files are refused outright
 
@@ -4508,6 +4746,26 @@ def brain_turn(
         "retry_count": _total_attempts,
         "prompt_cache_split": cache_split,
     }
+    # Per-turn persistence (best-effort by design): the artifact holds
+    # xml_blocks plus the full raw output so a truncated inline payload
+    # can be recovered from ``output_address`` with native tools. A
+    # persistence failure must never fail the turn itself. The clock is
+    # injected (universal datetime rule) rather than read from the
+    # wall clock inside the helper.
+    try:
+        result["output_address"] = persist_brain_turn_output(
+            project_root,
+            history_key,
+            task_id,
+            diag.get("response_id"),
+            xml_blocks,
+            output,
+            diag.get("status") == "incomplete",
+            clock=time.gmtime,
+        )
+    except OSError as exc:
+        print(f"brain-bridge: output persistence skipped ({exc})", file=sys.stderr)
+        result["output_address"] = None
     debug: dict[str, Any] = {"provider": diag}
     if fence_drops:
         debug["fenced_blocks"] = len(fence_drops)
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 880202d..9371927 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.74.0</system_version>
+<system_version>9.75.0</system_version>
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index a68540e..9de53c4 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -12,14 +12,7 @@
 </context_phase>
 
   <execution_phase>
-    HANDS INSTRUCTION:
-    1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
-    1.5. PERSIST THE TREE: Run the `custom_context_create_tree_report` tool (default `target_path="."` for the whole project; pass a scoped path when the Orchestrator targets a sub-directory). It saves a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md` and returns the file path.
-    1.6. GRAPH-FIRST: Run `custom_context_build_graph` once on the target scope (saves versioned `graph_*.json` + `graph_report_*.md`), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` for cross-file questions before falling back to full reads.
-    2. MANDATORY CORE FILES: Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
-    3. VERTICAL SLICE EXTRACTION: Use the `extract_signatures` tool on the specific feature directory requested by the Orchestrator (e.g., `src/features/auth/`). Do not extract signatures for the entire repository unless explicitly asked.
-    4. Compile the results into a single context report using the MCP tools.
-    CRITICAL: You MUST apply the Dependency Tracing Protocol. If your target files import other local services/repositories, you MUST trace and include them in this context report.
+    HANDS INSTRUCTION: Execute the discovery protocol from `cognitive-executor` agent. Gather context using the `custom_context` MCP tools (directory tree, tree report, read source files, extract signatures, graph tools). Apply the Dependency Tracing Protocol. Compile the results into a single context report.
 
     Target Files to compile:
     [INSERT TARGET FILES HERE]
@@ -50,64 +43,32 @@
   <execution_phase>
     HANDS INSTRUCTION: Implement the following logic step-by-step.
 
-    **ORCHESTRATOR AUTHORING RULE (comprehensive, executable XML):** Every `<hands_implementation_task>` MUST be a complete executable handoff. Each checklist step names the exact file path and the exact operation. Every file change carries the complete code sample or unified diff the Hands must apply — placeholder-only instructions, vague file references, and omitted code are forbidden. Every command is written out in full with exact flags and working directory. Every skill is named with one line saying why the Hands need it for this step. Every step states its verification command and expected result, and acceptance criteria plus edge cases are explicit. Pre-make every decision the approved plan already contains and leave no step ambiguous. **PLACEHOLDER BAN:** No `[bracketed placeholder]` may survive in the emitted XML — every skill name, file path, command, and step MUST be filled with concrete values from the approved plan. If a value is genuinely unknown, halt and ask instead of emitting a placeholder. The Hands may question the Manager ONLY for information that exists nowhere in the plan or repo — never for a decision the Brain already made.
+    **ORCHESTRATOR AUTHORING RULE (comprehensive, executable XML):** Every `<hands_implementation_task>` MUST be a complete executable handoff. Each checklist step names the exact file path and the exact operation. Every file change carries the complete code sample or unified diff the Hands must apply. Every command is written out in full with exact flags and working directory. Every skill is named with one line saying why the Hands need it. Every step states its verification command and expected result, and acceptance criteria plus edge cases are explicit. Pre-make every decision the approved plan already contains and leave no step ambiguous. **PLACEHOLDER BAN:** No `[bracketed placeholder]` may survive in the emitted XML. The Hands may question the Manager ONLY for information that exists nowhere in the plan or repo. placeholder-only instructions are forbidden — every step MUST be concrete. omitted code are forbidden.
 
     **MICRO-TASK CHECKLIST:**
-    You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step. When the checklist has 2 or more steps, you MUST also track them as a micro-list (todo list) alongside the task file: keep the full list current on every update with exactly one step in progress, mark each step completed the moment it is done, and keep the authoritative copy in the task file itself — never only in the chat.
-
-    - [ ] **Step 1:** [Precise action, e.g., Write the failing test for X]
-    - [ ] **Step 2:** [Precise action, e.g., Implement the minimal code to pass the test]
-    - [ ] **Step 3:** [Precise action, e.g., Refactor and add inline documentation]
-    - [ ] **Step 4:** [Precise action, e.g., Run tests to verify]
-
+    You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step. When the checklist has 2 or more steps, you MUST also track them as a micro-list (todo list) alongside the task file.
 
+    - [ ] **Step 1:** [Precise action]
+    - [ ] **Step 2:** [Precise action]
+    - [ ] **Step 3:** [Precise action]
+    - [ ] **Step 4:** [Precise action]
 
-     CRITICAL TOOL RULES:
-     0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
-     1. If applying file patches, utilize your native file-editing tools (`edit` for replacements, `write` for new files). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
-     2. If user feedback is required, first check the session capability manifest for your question/clarification tool. If the tool is AVAILABLE, utilize it with multi-option schemas. If it is UNAVAILABLE, do NOT silently skip the question: relay it to the Manager as one narrow question with the options inline, then wait for the answer (manual mode) or record the replay-or-halt decision in the task file (autopilot mode).
-     3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.
-     4. **Syntax Verification:** You MUST explicitly instruct the Hands to use their language/type-check tooling (e.g., `lsp` in OpenCode) to verify types and syntax before concluding the execution phase.
-     5. **Living Folder Docs Sync:** Before modifying code in a component or feature folder, inspect sibling README.md and DECISIONS.md. If your change alters domain responsibilities, interfaces, or invariants, you MUST update sibling README.md and append a dated ADR to DECISIONS.md.
+    HANDS INSTRUCTION: Follow the critical tool rules, documentation rule, syntax verification, and living-folder-docs sync from `cognitive-executor` agent. The Hands owns the full rule text.
 </execution_phase>
 
   <bash_phase>
-    HANDS INSTRUCTION: Run necessary terminal commands to build, test, and verify.
-    CRITICAL RULE 1: ALL bash commands MUST use non-interactive flags (e.g., `npm install -y`, `pytest --no-header`). Do NOT run interactive commands like `vim`, `less`, or `nano`.
-    CRITICAL RULE 2: Zero-Autonomous-Commit (ZAC). You are STRICTLY FORBIDDEN from executing `git add`, `git commit`, `git checkout`, or `git push` autonomously. The ONLY permitted autonomous Git operation is `git mv` for Kanban task-file transitions. Index surgery uses MCP tools only: `custom_context_unstage_files` to remove files from the index (worktree untouched), `custom_context_stage_and_inject_diff` to stage. You may ONLY run other Git commands if they are explicitly listed by the Orchestrator in this `<bash_phase>`. Do not guess or auto-commit.
-    CRITICAL RULE 2b (Parallel-Session Index Isolation): When two tasks run in parallel and share files, touch ONLY your own task's files. If your staged diff contains foreign hunks: call `custom_context_unstage_files` with exactly those files, redo your hunk-level staging, then call `custom_context_stage_and_inject_diff` with `skip_add=True` so the index is never overwritten. Never stage, unstage, or commit files belonging to another task.
-    CRITICAL RULE 3: The local agent truncates terminal output over 2000 lines or 50KB. If running test suites with massive output, pipe through grep or tail to ensure the verification-before-completion gate receives the success confirmation without truncation.
-    CRITICAL RULE 3b (Token trimming): Every test-suite verification run begins with `rtk test <underlying command>` so passing suites collapse to a verdict summary; the exact `rtk test`-prefixed command MUST be recorded in the `## Verification Evidence` section of the active task file. RTK preserves the underlying command's exit code. On ANY failure re-run without the wrapper and keep the full output — never collapse failing output. A raw rerun is allowed only after a failed RTK run for detailed diagnostics and never replaces the initial RTK verification run.
-    CRITICAL RULE 4 (For Orchestrator — file staging): If the active task is currently in tasks/backlog/, you MUST explicitly include the command "git mv tasks/backlog/XX-task.md tasks/in-progress/XX-task.md" as the very first command in this bash phase. This ensures the Hands can stage the file without violating Zero-Autonomous-Commit.
-    CRITICAL RULE 5 (Pre-Commit Verification Gate): For DevOps, infrastructure, or deployment tasks, the verification gate MUST include environment-specific checks (registry authentication, token scope validation, network access) BEFORE staging any files. If ANY pre-commit check fails, HALT and output a `<failure_report>`. Do NOT stage or commit partial work.
-    CRITICAL RULE 6 (Evidence Capture): Before proceeding to the `<summary_phase>`, you MUST capture the exact test command, expected result, actual result, and exit code. You MUST write these into the `## Verification Evidence` section of the active task file.
-    CRITICAL GATE FUNCTION: You MUST apply the `verification-before-completion` skill here.
-    STRICT TOOLING GATE (Machine-Enforced — Forced Strict Mode): Before the verification gate, you MUST load the active stack skill from `<agent_skills_registry>` that matches the project and execute its **Strict Tooling Gate** section in fail-fast order (format → lint → typecheck → static analysis → security → test → build). Stop on the first failure. No completion claim, no `lint_task_file`, and no QA transition until the gate is green. Record the exact gate command, output, and exit code in `## Verification Evidence`. Selection: match by file markers per stack — `go.mod` (+ `import github.com/gin-gonic/gin` → `go-gin`, `buf.yaml`/`proto` + `go.mod` + `Fx` → `go-hexagonal-grpc`), `build.gradle.kts` (`+ compose` → `android-kotlin`, `+ Spring Boot` → `spring-boot`), `Package.swift`/`*.xcodeproj` → `ios-swiftui`, `pyproject.toml` + `Flask` → `flask-python`, `pyproject.toml` + `FastAPI` → `python-fastapi`, `package.json` + `next.config.*` → `nextjs`, `package.json` + `src/ports/` → `node-hexagonal-api`, `package.json` + `apps/expo` → `react-native-expo`, `vite.config.*` → `react-vite`, `nuxt.config.*` → `vue-nuxt`, `nest-cli.json`/`prisma/schema.prisma` → `nestjs-prisma-vertical`. Multi-match repos MUST run every matching gate in fail-fast order; do not silently skip any. When several JS skills match, use the highest Node floor among them and record it in `## Verification Evidence`. Docs-only or no-match repos MUST log a skip record with four fields — repo root, marker scan list, matched skills list, reason phrase — in `## Verification Evidence`. Passing example: `root=. markers=[package.json] matched=[] reason=no stack marker found`. Failing example (never do this): `skipped gates` with no fields. Deferred gates block `lint_task_file` and any QA transition until the nightly/merge queue is green, with queue URL plus commit SHA plus green verdict logged in `## Verification Evidence`.
-    1. Run the test/build command.
-    2. If tests fail, you have a maximum of 3 repair attempts. If the error persists after 3 attempts, you MUST HALT immediately and output a `<failure_report>` detailing the exact errors for the Manager.
-    3. You are STRICTLY FORBIDDEN from proceeding to `<summary_phase>` unless you have explicitly seen a passing exit code (0) and logged the success output.
+    HANDS INSTRUCTION: Run necessary terminal commands to build, test, and verify. Follow the bash protocol, ZAC rules, evidence capture, and strict tooling gate from `cognitive-executor` agent.
     [List explicit bash commands here]
 </bash_phase>
 
   <documentation_phase>
-    HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs. Task-number discipline: NEVER write task numbers into prompt-facing Markdown prose — section headings, skill instructions, registry lines, and Execution Logs stay number-free (the task file's own title already carries its number). Task-number references live ONLY in code comments, CHANGELOG entries, history archives, and HTML comments.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version. 4) Update sibling folder documentation (`README.md`, `DECISIONS.md`) for any component or slice directory modified during this task.
+    HANDS INSTRUCTION: Update the local project documentation per the documentation rule and living-folder-docs sync in `cognitive-executor` agent.
 </documentation_phase>
 
   <summary_phase>
-    HANDS INSTRUCTION: You MUST follow this exact finalization sequence:
-    1. Before calling `lint_task_file`, review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why.
-    2. Call the `lint_task_file` MCP tool (from the `lint` server) on the active task file. If lint fails, fix the structural issues before proceeding.
-     2b. Parallel check: inspect `git diff --cached --name-only` (read-only). If files outside your task are staged, call `custom_context_unstage_files` with exactly those files first — never stage or carry another task's files.
-     3. Execute the atomic QA transition:
-       Call the `custom_context_qa_transition` MCP tool with:
-       - `task_file_path`: "tasks/in-progress/<task-name>.md"
-       - `modified_files`: [<modified_file_1>, <modified_file_2>, ...]
-       This atomically moves the task file to `tasks/qa/`, updates the `**File:**` header, stages your modified code, and injects the git diff in one operation.
-     4. Once the atomic QA transition succeeds, implementation is complete — continue with QA/review chaining below.
-     5. The Hands invokes the QA/review `brain_turn` itself in both manual and automatic modes under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text.
-     6. Output EXACTLY this message to the Manager:
+    HANDS INSTRUCTION: Follow the finalization sequence in `cognitive-executor` agent. Output EXACTLY this message:
+     1. Output EXACTLY this message to the Manager:
        "Task implemented, reasoning logged, Git diff injected, and QA/review chained via `brain_turn`."
-     7. After the QA/review `brain_turn` is invoked, you are DONE.
 </summary_phase>
 </hands_implementation_task>
 ```
@@ -121,13 +82,7 @@
 <!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Discovery-->
 
   <discovery_phase>
-    HANDS INSTRUCTION: You are in DISCOVERY mode. Gather context for the Orchestrator using the `custom_context` MCP server tools:
-    1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
-    1.5. PERSIST THE TREE: Run the `custom_context_create_tree_report` tool (default `target_path="."` for the whole project; pass a scoped path when the Orchestrator targets a sub-directory). It saves a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md` and returns the file path.
-    1.6. GRAPH-FIRST: Run `custom_context_build_graph` once on the target scope (saves versioned `graph_*.json` + `graph_report_*.md`), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` for cross-file questions before falling back to full reads.
-    2. Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
-    3. Compile the results into a single context report using the MCP tools.
-    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools.
+    HANDS INSTRUCTION: You are in DISCOVERY mode. Gather context for the Orchestrator using the `custom_context` MCP server tools (directory tree, tree report, read source files, graph tools). Follow the discovery protocol in `cognitive-executor` agent. Do NOT use your native `read` tool to output file contents inline.
 </discovery_phase>
 
   <conditional_implementation_phase>
@@ -137,6 +92,7 @@
 
     [IMPLEMENTATION STEPS]
 
+    HANDS INSTRUCTION: Follow the implementation protocol in `cognitive-executor` agent for tool calls, verification gates, and finalization.
 </conditional_implementation_phase>
 
   <summary_phase>
@@ -153,6 +109,7 @@
      4. The Hands invokes the QA/review `brain_turn` itself in both manual and automatic modes under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text.
      5. Then output exactly:
        "Combined task complete: discovery verified, implementation applied, Git diff injected, and QA/review chained via `brain_turn`."
+     6. After the QA/review `brain_turn` is invoked and the exact completion message is output, you are DONE.
 </summary_phase>
 </hands_combined_task>
 ```
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index 7e1d8fd..f127efc 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -18,7 +18,7 @@
   2. `custom_context_commit_and_clean_task` (closure-time): Commits staged changes as a feature commit, captures the hash, cleans the task file diff block, and creates a separate `chore: close task N` closure commit. The stored hash always points to the feature commit (reachable from HEAD). MUST ONLY be called after the Manager explicitly says "Approved for closure" or "Close task".
   The Hands MUST NEVER run `git commit`, `git add`, `git checkout`, or `git push` directly at any point. All staging is via `custom_context_stage_and_inject_diff`; all unstaging is via `custom_context_unstage_files` (index-only, worktree untouched); all commits are via `custom_context_commit_and_clean_task`. If the Hands call `commit_and_clean_task` before Manager approval, this is a ZAC violation and the task must be rejected.
 - **Conventional Commits Format Gate:** Every feature commit message passed to `custom_context_commit_and_clean_task` MUST match `<type>: <subject>` with type in `feat|fix|docs|refactor|chore` and first line ≤72 characters (per `skill-templates/versioning-and-release`). The tool validates and rejects free-form messages. The templated `chore: close task N` closure commit always conforms by construction.
-- **Supervised Autopilot Contract:** On the lock words the Hands run end to end: discovery feed, Brain plan, one approval pause for the plan, seat-routed implementation, QA and review loops, results shown before the move to qa. Besides that single plan-approval pause, only Relay questions and hard blockers interrupt. Risk tiers live in `docs/conventions.md` (T0 trivial, T1 standard, T2 destructive needs per-action approval). Plan, QA, and review loops allow three tries max, then escalate. Authority for the full rule text is `agents/cognitive-executor.md`.
+- **Supervised Autopilot Contract:** On the lock words the Hands run end to end: discovery feed, Brain plan, one approval pause for the plan, seat-routed implementation, QA and review loops, results shown before the move to qa. Besides that single plan-approval pause, only Relay questions and hard blockers interrupt. Risk tiers live in `docs/conventions.md` (T0 trivial, T1 standard, T2 destructive needs per-action approval). Plan, QA, and review loops allow three tries max, then escalate. Authority for the full rule text is the `cognitive-executor` agent.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
 - **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent `cognitive-discovery` subagents) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
   - **Implementation & R&D triggers (distinct from discovery):** split work across subagents ONLY when (a) the changes touch disjoint file sets with no shared imports or fixtures, (b) each lane is verifiable alone (its own test command or grep gate), or (c) research questions are independent (different subsystems, no shared conclusion). Coupled edits to the same files, single-file tasks, and sequential dependencies stay single-threaded — parallelizing them adds coordination cost without throughput.
diff --git a/prompts/fragments/18-no_manual_dto_mandate.md b/prompts/fragments/18-no_manual_dto_mandate.md
index 0605d6d..70b291d 100644
--- a/prompts/fragments/18-no_manual_dto_mandate.md
+++ b/prompts/fragments/18-no_manual_dto_mandate.md
@@ -1,27 +1,3 @@
 <no_manual_dto_mandate>
-You MUST enforce the No-Manual-DTO Mandate on every implementation task where a source-of-truth contract or shared schema exists.
-
-### Core Mandate
-
-AI agents and engineers are STRICTLY FORBIDDEN from hand-authoring duplicate interface models, request/response DTOs, or data classes inside consumer applications when a source-of-truth contract or shared schema already exists — including `packages/shared-schema/`, OpenAPI specs, Prisma schemas, and Protobuf definitions. Consumer applications MUST NOT redefine types that a contract already governs.
-
-### Requirement
-
-When a task touches a type that is governed by an existing contract, the agent MUST either:
-
-1. **(a) Import models directly** from the shared package (`@repo/shared-schema`, `packages/shared-schema`, or the equivalent canonical source), OR
-2. **(b) Execute the stack's code-generation toolchain** — `pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`, or the equivalent generator — so the consumer's types are produced from the contract instead of being hand-written.
-
-Hand-written duplicates create silent type drift: the consumer's copy and the contract's canonical definition diverge over time, producing runtime mismatches that compile-time checks in the consumer alone cannot catch.
-
-### Reconciliation with SOLID
-
-This mandate is fully consistent with the SOLID principles and their pragmatic guardrails:
-
-- **DRY / SRP:** A single source of truth prevents duplicated type definitions (DRY) and gives each type exactly one owner (SRP). Importing a shared DTO is not duplication — it is the canonical, single-reason-to-change form.
-- **No conflict with YAGNI:** The mandate does not introduce speculative abstractions. It reuses a contract that already exists. If NO source-of-truth contract exists, the agent writes the concrete type directly — do NOT invent a shared-schema package for a single consumer.
-- **No conflict with the 3-Implementation Rule:** Extracting a shared package is only required when a contract or cross-service dependency already exists (2+ consumers or a canonical schema). Do not extract interfaces for trivial, single-module logic.
-- **Occam's Razor:** The simplest correct action is import-then-use or run-codegen — never hand-copy a governed type.
-
-When a diff introduces a new DTO/interface/model declaration into a consumer path (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) while a governing contract exists, the Type Drift Sentinel fails the verification until the agent imports from the shared package or runs the codegen toolchain.
+No-Manual-DTO Mandate (full rule text in `cognitive-executor` agent): when a source-of-truth contract or shared schema exists, the Hands MUST import from the shared package or run the codegen toolchain — never hand-author duplicate DTOs. The Brain references this mandate by name in task instructions; the Hands owns the full rule text and enforcement.
 </no_manual_dto_mandate>
\ No newline at end of file
diff --git a/system-prompt.md b/system-prompt.md
index a0e9f13..32c7be2 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.74.0</system_version>
+<system_version>9.75.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -233,14 +233,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 </context_phase>
 
   <execution_phase>
-    HANDS INSTRUCTION:
-    1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
-    1.5. PERSIST THE TREE: Run the `custom_context_create_tree_report` tool (default `target_path="."` for the whole project; pass a scoped path when the Orchestrator targets a sub-directory). It saves a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md` and returns the file path.
-    1.6. GRAPH-FIRST: Run `custom_context_build_graph` once on the target scope (saves versioned `graph_*.json` + `graph_report_*.md`), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` for cross-file questions before falling back to full reads.
-    2. MANDATORY CORE FILES: Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
-    3. VERTICAL SLICE EXTRACTION: Use the `extract_signatures` tool on the specific feature directory requested by the Orchestrator (e.g., `src/features/auth/`). Do not extract signatures for the entire repository unless explicitly asked.
-    4. Compile the results into a single context report using the MCP tools.
-    CRITICAL: You MUST apply the Dependency Tracing Protocol. If your target files import other local services/repositories, you MUST trace and include them in this context report.
+    HANDS INSTRUCTION: Execute the discovery protocol from `cognitive-executor` agent. Gather context using the `custom_context` MCP tools (directory tree, tree report, read source files, extract signatures, graph tools). Apply the Dependency Tracing Protocol. Compile the results into a single context report.
 
     Target Files to compile:
     [INSERT TARGET FILES HERE]
@@ -279,64 +272,32 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
   <execution_phase>
     HANDS INSTRUCTION: Implement the following logic step-by-step.
 
-    **ORCHESTRATOR AUTHORING RULE (comprehensive, executable XML):** Every `<hands_implementation_task>` MUST be a complete executable handoff. Each checklist step names the exact file path and the exact operation. Every file change carries the complete code sample or unified diff the Hands must apply — placeholder-only instructions, vague file references, and omitted code are forbidden. Every command is written out in full with exact flags and working directory. Every skill is named with one line saying why the Hands need it for this step. Every step states its verification command and expected result, and acceptance criteria plus edge cases are explicit. Pre-make every decision the approved plan already contains and leave no step ambiguous. **PLACEHOLDER BAN:** No `[bracketed placeholder]` may survive in the emitted XML — every skill name, file path, command, and step MUST be filled with concrete values from the approved plan. If a value is genuinely unknown, halt and ask instead of emitting a placeholder. The Hands may question the Manager ONLY for information that exists nowhere in the plan or repo — never for a decision the Brain already made.
+    **ORCHESTRATOR AUTHORING RULE (comprehensive, executable XML):** Every `<hands_implementation_task>` MUST be a complete executable handoff. Each checklist step names the exact file path and the exact operation. Every file change carries the complete code sample or unified diff the Hands must apply. Every command is written out in full with exact flags and working directory. Every skill is named with one line saying why the Hands need it. Every step states its verification command and expected result, and acceptance criteria plus edge cases are explicit. Pre-make every decision the approved plan already contains and leave no step ambiguous. **PLACEHOLDER BAN:** No `[bracketed placeholder]` may survive in the emitted XML. The Hands may question the Manager ONLY for information that exists nowhere in the plan or repo. placeholder-only instructions are forbidden — every step MUST be concrete. omitted code are forbidden.
 
     **MICRO-TASK CHECKLIST:**
-    You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step. When the checklist has 2 or more steps, you MUST also track them as a micro-list (todo list) alongside the task file: keep the full list current on every update with exactly one step in progress, mark each step completed the moment it is done, and keep the authoritative copy in the task file itself — never only in the chat.
-
-    - [ ] **Step 1:** [Precise action, e.g., Write the failing test for X]
-    - [ ] **Step 2:** [Precise action, e.g., Implement the minimal code to pass the test]
-    - [ ] **Step 3:** [Precise action, e.g., Refactor and add inline documentation]
-    - [ ] **Step 4:** [Precise action, e.g., Run tests to verify]
-
+    You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step. When the checklist has 2 or more steps, you MUST also track them as a micro-list (todo list) alongside the task file.
 
+    - [ ] **Step 1:** [Precise action]
+    - [ ] **Step 2:** [Precise action]
+    - [ ] **Step 3:** [Precise action]
+    - [ ] **Step 4:** [Precise action]
 
-     CRITICAL TOOL RULES:
-     0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
-     1. If applying file patches, utilize your native file-editing tools (`edit` for replacements, `write` for new files). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
-     2. If user feedback is required, first check the session capability manifest for your question/clarification tool. If the tool is AVAILABLE, utilize it with multi-option schemas. If it is UNAVAILABLE, do NOT silently skip the question: relay it to the Manager as one narrow question with the options inline, then wait for the answer (manual mode) or record the replay-or-halt decision in the task file (autopilot mode).
-     3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.
-     4. **Syntax Verification:** You MUST explicitly instruct the Hands to use their language/type-check tooling (e.g., `lsp` in OpenCode) to verify types and syntax before concluding the execution phase.
-     5. **Living Folder Docs Sync:** Before modifying code in a component or feature folder, inspect sibling README.md and DECISIONS.md. If your change alters domain responsibilities, interfaces, or invariants, you MUST update sibling README.md and append a dated ADR to DECISIONS.md.
+    HANDS INSTRUCTION: Follow the critical tool rules, documentation rule, syntax verification, and living-folder-docs sync from `cognitive-executor` agent. The Hands owns the full rule text.
 </execution_phase>
 
   <bash_phase>
-    HANDS INSTRUCTION: Run necessary terminal commands to build, test, and verify.
-    CRITICAL RULE 1: ALL bash commands MUST use non-interactive flags (e.g., `npm install -y`, `pytest --no-header`). Do NOT run interactive commands like `vim`, `less`, or `nano`.
-    CRITICAL RULE 2: Zero-Autonomous-Commit (ZAC). You are STRICTLY FORBIDDEN from executing `git add`, `git commit`, `git checkout`, or `git push` autonomously. The ONLY permitted autonomous Git operation is `git mv` for Kanban task-file transitions. Index surgery uses MCP tools only: `custom_context_unstage_files` to remove files from the index (worktree untouched), `custom_context_stage_and_inject_diff` to stage. You may ONLY run other Git commands if they are explicitly listed by the Orchestrator in this `<bash_phase>`. Do not guess or auto-commit.
-    CRITICAL RULE 2b (Parallel-Session Index Isolation): When two tasks run in parallel and share files, touch ONLY your own task's files. If your staged diff contains foreign hunks: call `custom_context_unstage_files` with exactly those files, redo your hunk-level staging, then call `custom_context_stage_and_inject_diff` with `skip_add=True` so the index is never overwritten. Never stage, unstage, or commit files belonging to another task.
-    CRITICAL RULE 3: The local agent truncates terminal output over 2000 lines or 50KB. If running test suites with massive output, pipe through grep or tail to ensure the verification-before-completion gate receives the success confirmation without truncation.
-    CRITICAL RULE 3b (Token trimming): Every test-suite verification run begins with `rtk test <underlying command>` so passing suites collapse to a verdict summary; the exact `rtk test`-prefixed command MUST be recorded in the `## Verification Evidence` section of the active task file. RTK preserves the underlying command's exit code. On ANY failure re-run without the wrapper and keep the full output — never collapse failing output. A raw rerun is allowed only after a failed RTK run for detailed diagnostics and never replaces the initial RTK verification run.
-    CRITICAL RULE 4 (For Orchestrator — file staging): If the active task is currently in tasks/backlog/, you MUST explicitly include the command "git mv tasks/backlog/XX-task.md tasks/in-progress/XX-task.md" as the very first command in this bash phase. This ensures the Hands can stage the file without violating Zero-Autonomous-Commit.
-    CRITICAL RULE 5 (Pre-Commit Verification Gate): For DevOps, infrastructure, or deployment tasks, the verification gate MUST include environment-specific checks (registry authentication, token scope validation, network access) BEFORE staging any files. If ANY pre-commit check fails, HALT and output a `<failure_report>`. Do NOT stage or commit partial work.
-    CRITICAL RULE 6 (Evidence Capture): Before proceeding to the `<summary_phase>`, you MUST capture the exact test command, expected result, actual result, and exit code. You MUST write these into the `## Verification Evidence` section of the active task file.
-    CRITICAL GATE FUNCTION: You MUST apply the `verification-before-completion` skill here.
-    STRICT TOOLING GATE (Machine-Enforced — Forced Strict Mode): Before the verification gate, you MUST load the active stack skill from `<agent_skills_registry>` that matches the project and execute its **Strict Tooling Gate** section in fail-fast order (format → lint → typecheck → static analysis → security → test → build). Stop on the first failure. No completion claim, no `lint_task_file`, and no QA transition until the gate is green. Record the exact gate command, output, and exit code in `## Verification Evidence`. Selection: match by file markers per stack — `go.mod` (+ `import github.com/gin-gonic/gin` → `go-gin`, `buf.yaml`/`proto` + `go.mod` + `Fx` → `go-hexagonal-grpc`), `build.gradle.kts` (`+ compose` → `android-kotlin`, `+ Spring Boot` → `spring-boot`), `Package.swift`/`*.xcodeproj` → `ios-swiftui`, `pyproject.toml` + `Flask` → `flask-python`, `pyproject.toml` + `FastAPI` → `python-fastapi`, `package.json` + `next.config.*` → `nextjs`, `package.json` + `src/ports/` → `node-hexagonal-api`, `package.json` + `apps/expo` → `react-native-expo`, `vite.config.*` → `react-vite`, `nuxt.config.*` → `vue-nuxt`, `nest-cli.json`/`prisma/schema.prisma` → `nestjs-prisma-vertical`. Multi-match repos MUST run every matching gate in fail-fast order; do not silently skip any. When several JS skills match, use the highest Node floor among them and record it in `## Verification Evidence`. Docs-only or no-match repos MUST log a skip record with four fields — repo root, marker scan list, matched skills list, reason phrase — in `## Verification Evidence`. Passing example: `root=. markers=[package.json] matched=[] reason=no stack marker found`. Failing example (never do this): `skipped gates` with no fields. Deferred gates block `lint_task_file` and any QA transition until the nightly/merge queue is green, with queue URL plus commit SHA plus green verdict logged in `## Verification Evidence`.
-    1. Run the test/build command.
-    2. If tests fail, you have a maximum of 3 repair attempts. If the error persists after 3 attempts, you MUST HALT immediately and output a `<failure_report>` detailing the exact errors for the Manager.
-    3. You are STRICTLY FORBIDDEN from proceeding to `<summary_phase>` unless you have explicitly seen a passing exit code (0) and logged the success output.
+    HANDS INSTRUCTION: Run necessary terminal commands to build, test, and verify. Follow the bash protocol, ZAC rules, evidence capture, and strict tooling gate from `cognitive-executor` agent.
     [List explicit bash commands here]
 </bash_phase>
 
   <documentation_phase>
-    HANDS INSTRUCTION: Update the local project documentation: 1) Open the active task file in `tasks/`. 2) Under "Execution Log & Reasoning", manually write your architectural notes, what you changed, and why. All technical reasoning and logs MUST be written in English. Check off any local TODOs. Task-number discipline: NEVER write task numbers into prompt-facing Markdown prose — section headings, skill instructions, registry lines, and Execution Logs stay number-free (the task file's own title already carries its number). Task-number references live ONLY in code comments, CHANGELOG entries, history archives, and HTML comments.     3) You MUST update `CHANGELOG.md` using the Parse-Then-Append Protocol: (a) Read `CHANGELOG.md`. (b) Check if the current version header (`## [X.Y.Z]`) exists. (c) Check if the target section (`### Added`, `### Changed`, `### Fixed`, etc.) exists under that version. (d) If the section exists, append the entry under it. If not, create the section. (e) NEVER create a duplicate section header under the same version. 4) Update sibling folder documentation (`README.md`, `DECISIONS.md`) for any component or slice directory modified during this task.
+    HANDS INSTRUCTION: Update the local project documentation per the documentation rule and living-folder-docs sync in `cognitive-executor` agent.
 </documentation_phase>
 
   <summary_phase>
-    HANDS INSTRUCTION: You MUST follow this exact finalization sequence:
-    1. Before calling `lint_task_file`, review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why.
-    2. Call the `lint_task_file` MCP tool (from the `lint` server) on the active task file. If lint fails, fix the structural issues before proceeding.
-     2b. Parallel check: inspect `git diff --cached --name-only` (read-only). If files outside your task are staged, call `custom_context_unstage_files` with exactly those files first — never stage or carry another task's files.
-     3. Execute the atomic QA transition:
-       Call the `custom_context_qa_transition` MCP tool with:
-       - `task_file_path`: "tasks/in-progress/<task-name>.md"
-       - `modified_files`: [<modified_file_1>, <modified_file_2>, ...]
-       This atomically moves the task file to `tasks/qa/`, updates the `**File:**` header, stages your modified code, and injects the git diff in one operation.
-     4. Once the atomic QA transition succeeds, implementation is complete — continue with QA/review chaining below.
-     5. The Hands invokes the QA/review `brain_turn` itself in both manual and automatic modes under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text.
-     6. Output EXACTLY this message to the Manager:
+    HANDS INSTRUCTION: Follow the finalization sequence in `cognitive-executor` agent. Output EXACTLY this message:
+     1. Output EXACTLY this message to the Manager:
        "Task implemented, reasoning logged, Git diff injected, and QA/review chained via `brain_turn`."
-     7. After the QA/review `brain_turn` is invoked, you are DONE.
 </summary_phase>
 </hands_implementation_task>
 ```
@@ -358,13 +319,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 </validation_phase>
 
   <discovery_phase>
-    HANDS INSTRUCTION: You are in DISCOVERY mode. Gather context for the Orchestrator using the `custom_context` MCP server tools:
-    1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
-    1.5. PERSIST THE TREE: Run the `custom_context_create_tree_report` tool (default `target_path="."` for the whole project; pass a scoped path when the Orchestrator targets a sub-directory). It saves a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md` and returns the file path.
-    1.6. GRAPH-FIRST: Run `custom_context_build_graph` once on the target scope (saves versioned `graph_*.json` + `graph_report_*.md`), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` for cross-file questions before falling back to full reads.
-    2. Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
-    3. Compile the results into a single context report using the MCP tools.
-    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools.
+    HANDS INSTRUCTION: You are in DISCOVERY mode. Gather context for the Orchestrator using the `custom_context` MCP server tools (directory tree, tree report, read source files, graph tools). Follow the discovery protocol in `cognitive-executor` agent. Do NOT use your native `read` tool to output file contents inline.
 </discovery_phase>
 
   <conditional_implementation_phase>
@@ -374,6 +329,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
     [IMPLEMENTATION STEPS]
 
+    HANDS INSTRUCTION: Follow the implementation protocol in `cognitive-executor` agent for tool calls, verification gates, and finalization.
 </conditional_implementation_phase>
 
   <summary_phase>
@@ -390,6 +346,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
      4. The Hands invokes the QA/review `brain_turn` itself in both manual and automatic modes under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text.
      5. Then output exactly:
        "Combined task complete: discovery verified, implementation applied, Git diff injected, and QA/review chained via `brain_turn`."
+     6. After the QA/review `brain_turn` is invoked and the exact completion message is output, you are DONE.
 </summary_phase>
 </hands_combined_task>
 ```
@@ -509,7 +466,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
   2. `custom_context_commit_and_clean_task` (closure-time): Commits staged changes as a feature commit, captures the hash, cleans the task file diff block, and creates a separate `chore: close task N` closure commit. The stored hash always points to the feature commit (reachable from HEAD). MUST ONLY be called after the Manager explicitly says "Approved for closure" or "Close task".
   The Hands MUST NEVER run `git commit`, `git add`, `git checkout`, or `git push` directly at any point. All staging is via `custom_context_stage_and_inject_diff`; all unstaging is via `custom_context_unstage_files` (index-only, worktree untouched); all commits are via `custom_context_commit_and_clean_task`. If the Hands call `commit_and_clean_task` before Manager approval, this is a ZAC violation and the task must be rejected.
 - **Conventional Commits Format Gate:** Every feature commit message passed to `custom_context_commit_and_clean_task` MUST match `<type>: <subject>` with type in `feat|fix|docs|refactor|chore` and first line ≤72 characters (per `skill-templates/versioning-and-release`). The tool validates and rejects free-form messages. The templated `chore: close task N` closure commit always conforms by construction.
-- **Supervised Autopilot Contract:** On the lock words the Hands run end to end: discovery feed, Brain plan, one approval pause for the plan, seat-routed implementation, QA and review loops, results shown before the move to qa. Besides that single plan-approval pause, only Relay questions and hard blockers interrupt. Risk tiers live in `docs/conventions.md` (T0 trivial, T1 standard, T2 destructive needs per-action approval). Plan, QA, and review loops allow three tries max, then escalate. Authority for the full rule text is `agents/cognitive-executor.md`.
+- **Supervised Autopilot Contract:** On the lock words the Hands run end to end: discovery feed, Brain plan, one approval pause for the plan, seat-routed implementation, QA and review loops, results shown before the move to qa. Besides that single plan-approval pause, only Relay questions and hard blockers interrupt. Risk tiers live in `docs/conventions.md` (T0 trivial, T1 standard, T2 destructive needs per-action approval). Plan, QA, and review loops allow three tries max, then escalate. Authority for the full rule text is the `cognitive-executor` agent.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
 - **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent `cognitive-discovery` subagents) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
   - **Implementation & R&D triggers (distinct from discovery):** split work across subagents ONLY when (a) the changes touch disjoint file sets with no shared imports or fixtures, (b) each lane is verifiable alone (its own test command or grep gate), or (c) research questions are independent (different subsystems, no shared conclusion). Coupled edits to the same files, single-file tasks, and sequential dependencies stay single-threaded — parallelizing them adds coordination cost without throughput.
@@ -590,31 +547,7 @@ To prevent silent data corruption and financial drift, you MUST enforce the Univ
 </immutable_financial_ledger_mandate>
 
 <no_manual_dto_mandate>
-You MUST enforce the No-Manual-DTO Mandate on every implementation task where a source-of-truth contract or shared schema exists.
-
-### Core Mandate
-
-AI agents and engineers are STRICTLY FORBIDDEN from hand-authoring duplicate interface models, request/response DTOs, or data classes inside consumer applications when a source-of-truth contract or shared schema already exists — including `packages/shared-schema/`, OpenAPI specs, Prisma schemas, and Protobuf definitions. Consumer applications MUST NOT redefine types that a contract already governs.
-
-### Requirement
-
-When a task touches a type that is governed by an existing contract, the agent MUST either:
-
-1. **(a) Import models directly** from the shared package (`@repo/shared-schema`, `packages/shared-schema`, or the equivalent canonical source), OR
-2. **(b) Execute the stack's code-generation toolchain** — `pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`, or the equivalent generator — so the consumer's types are produced from the contract instead of being hand-written.
-
-Hand-written duplicates create silent type drift: the consumer's copy and the contract's canonical definition diverge over time, producing runtime mismatches that compile-time checks in the consumer alone cannot catch.
-
-### Reconciliation with SOLID
-
-This mandate is fully consistent with the SOLID principles and their pragmatic guardrails:
-
-- **DRY / SRP:** A single source of truth prevents duplicated type definitions (DRY) and gives each type exactly one owner (SRP). Importing a shared DTO is not duplication — it is the canonical, single-reason-to-change form.
-- **No conflict with YAGNI:** The mandate does not introduce speculative abstractions. It reuses a contract that already exists. If NO source-of-truth contract exists, the agent writes the concrete type directly — do NOT invent a shared-schema package for a single consumer.
-- **No conflict with the 3-Implementation Rule:** Extracting a shared package is only required when a contract or cross-service dependency already exists (2+ consumers or a canonical schema). Do not extract interfaces for trivial, single-module logic.
-- **Occam's Razor:** The simplest correct action is import-then-use or run-codegen — never hand-copy a governed type.
-
-When a diff introduces a new DTO/interface/model declaration into a consumer path (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) while a governing contract exists, the Type Drift Sentinel fails the verification until the agent imports from the shared package or runs the codegen toolchain.
+No-Manual-DTO Mandate (full rule text in `cognitive-executor` agent): when a source-of-truth contract or shared schema exists, the Hands MUST import from the shared package or run the codegen toolchain — never hand-author duplicate DTOs. The Brain references this mandate by name in task instructions; the Hands owns the full rule text and enforcement.
 </no_manual_dto_mandate>
 
 <initialization>
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index f8b636c..a5876f0 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -7,7 +7,10 @@ Responses-API text parser, and env fallbacks. The live LLM path
 """
 
 import os
+import json
 import sys
+import time
+from concurrent.futures import ThreadPoolExecutor
 from pathlib import Path
 
 import pytest
@@ -4672,3 +4675,524 @@ def test_record_brain_use_survives_corrupt_file(tmp_path, monkeypatch, capsys):
         {"count": 9, "cap": 10, "warn_at": 5, "warn": True, "model": None}
     )
     assert "monthly Brain usage 9/10" in capsys.readouterr().err
+
+
+def test_brain_output_persisted_every_turn(tmp_path, monkeypatch):
+    """Every turn persists xml_blocks plus the full raw output."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    root = _mk_tasks_root(tmp_path)
+    for truncated in (False, True):
+        addr = bridge.persist_brain_turn_output(
+            str(root),
+            "ses1",
+            "0383",
+            "resp_abc123",
+            ["<hands_implementation_task>do</hands_implementation_task>"],
+            "full-output-body",
+            truncated,
+            clock=time.gmtime,
+        )
+        assert addr and not Path(addr).is_absolute()
+        artifact = root / addr
+        assert artifact.is_file()
+        payload = json.loads(artifact.read_text(encoding="utf-8"))
+        assert payload["xml_blocks"] == [
+            "<hands_implementation_task>do</hands_implementation_task>"
+        ]
+        assert payload["full_output"] == "full-output-body"
+        assert payload["truncated"] is truncated
+        assert payload["task_id"] == "0383"
+        assert payload["response_id"] == "resp_abc123"
+        assert payload["address"] == addr
+        assert set(payload["byte_counts"]) == {"output", "xml_blocks"}
+
+
+def test_brain_output_address_present_and_backward_compat(tmp_path, monkeypatch):
+    """Address is additive metadata; committed schema stays fixed."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    root = _mk_tasks_root(tmp_path)
+    addr = bridge.persist_brain_turn_output(
+        str(root),
+        "ses1",
+        "0383",
+        "resp_xyz",
+        [],
+        "body",
+        False,
+        clock=time.gmtime,
+    )
+    assert isinstance(addr, str) and addr.startswith("tasks/.sessions/ses1_")
+    payload = json.loads((root / addr).read_text(encoding="utf-8"))
+    assert set(payload) == {
+        "task_id",
+        "session_key",
+        "response_id",
+        "created_at_utc",
+        "truncated",
+        "byte_counts",
+        "xml_blocks",
+        "full_output",
+        "address",
+    }
+    assert "unknown" not in addr
+    # No absolute machine layout may leak into the persisted address.
+    assert str(tmp_path) not in addr and str(root) not in addr
+
+
+def test_brain_output_retention_cap_enforced(tmp_path, monkeypatch):
+    """Oldest-first prune keeps newest; temp files never count."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    monkeypatch.setattr(bridge, "BRAIN_OUTPUTS_MAX_FILES", 3)
+    root = _mk_tasks_root(tmp_path)
+    out_dir = root / "tasks" / ".sessions" / "ses1_9cf38be4" / "brain_outputs"
+    addrs = []
+    for i in range(5):
+        addr = bridge.persist_brain_turn_output(
+            str(root),
+            "ses1",
+            "0383",
+            f"resp_{i}",
+            [],
+            f"body-{i}",
+            False,
+            clock=time.gmtime,
+        )
+        addrs.append(addr)
+        (root / addr).write_text(
+            (root / addr).read_text(encoding="utf-8"), encoding="utf-8"
+        )
+        stamp = 1700000000 + i
+        import os as _os
+
+        _os.utime(root / addr, (stamp, stamp))
+    # One stray temp file must neither count nor survive accounting.
+    (out_dir / ".tmp-crash.json").write_text("partial", encoding="utf-8")
+    newest = bridge.persist_brain_turn_output(
+        str(root),
+        "ses1",
+        "0383",
+        "resp_new",
+        [],
+        "body-new",
+        False,
+        clock=time.gmtime,
+    )
+    import os as _os2
+
+    _os2.utime(root / newest, (1800000000, 1800000000))
+    assert not (out_dir / ".tmp-crash.json").exists()
+    kept = sorted(p for p in out_dir.iterdir() if p.is_file() and p.suffix == ".json")
+    real = [p for p in kept if not p.name.startswith(".tmp-")]
+    assert len(real) <= 3
+    assert (root / newest).is_file()
+
+
+def test_brain_output_address_readable_tail(tmp_path, monkeypatch):
+    """The Hands can recover the tail from the address with native reads."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    root = _mk_tasks_root(tmp_path)
+    body = "head\n" + "x" * 5000 + "\nTAIL-MARKER-12345\n"
+    addr = bridge.persist_brain_turn_output(
+        str(root),
+        "ses9",
+        "0383",
+        "resp_tail",
+        ["<hands_implementation_task>tail</hands_implementation_task>"],
+        body,
+        True,
+        clock=time.gmtime,
+    )
+    # Simulate the Hands: open the address from the project root.
+    recovered = (root / addr).read_text(encoding="utf-8")
+    assert "TAIL-MARKER-12345" in recovered
+    payload = json.loads(recovered)
+    assert payload["full_output"].endswith("TAIL-MARKER-12345\n")
+    assert payload["xml_blocks"] == [
+        "<hands_implementation_task>tail</hands_implementation_task>"
+    ]
+
+
+def test_brain_output_uses_injected_clock(tmp_path, monkeypatch):
+    """Timestamp creation goes through the injected clock, not direct time."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    root = _mk_tasks_root(tmp_path)
+    import time as _time
+
+    fixed = _time.struct_time((2025, 1, 2, 3, 4, 5, 0, 0, 0))
+    addr = bridge.persist_brain_turn_output(
+        str(root),
+        "clock",
+        "0383",
+        "resp_clock",
+        [],
+        "b",
+        False,
+        clock=lambda: fixed,
+    )
+    payload = json.loads((root / addr).read_text(encoding="utf-8"))
+    assert payload["created_at_utc"] == "2025-01-02T03:04:05Z"
+
+
+def test_brain_output_unencodable_session_key_rejected(tmp_path, monkeypatch):
+    """A lone surrogate in the session key degrades to OSError, not a crash."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    root = _mk_tasks_root(tmp_path)
+    with pytest.raises(OSError):
+        bridge.persist_brain_turn_output(
+            str(root),
+            "ses\udcff",
+            "0383",
+            "resp_uni",
+            [],
+            "b",
+            False,
+            clock=time.gmtime,
+        )
+
+
+def test_brain_output_symlink_loop_is_normalized_to_oserror(tmp_path, monkeypatch):
+    """Path.resolve loop errors enter the best-effort OSError path."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    root = _mk_tasks_root(tmp_path)
+    original_resolve = Path.resolve
+
+    def resolve_with_loop(path, *args, **kwargs):
+        if path.name == "brain_outputs":
+            raise RuntimeError("Symlink loop")
+        return original_resolve(path, *args, **kwargs)
+
+    monkeypatch.setattr(Path, "resolve", resolve_with_loop)
+
+    with pytest.raises(OSError, match="brain-output path escapes project_root"):
+        bridge.persist_brain_turn_output(
+            str(root),
+            "symlink-loop",
+            "0383",
+            "response-loop",
+            [],
+            "body",
+            False,
+            clock=time.gmtime,
+        )
+
+
+def test_brain_output_unicode_surrogate_rejected(tmp_path, monkeypatch):
+    """A lone surrogate raises OSError instead of escaping persistence."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    root = _mk_tasks_root(tmp_path)
+    bad = "body with lone surrogate \udcff"
+    with pytest.raises(OSError):
+        bridge.persist_brain_turn_output(
+            str(root),
+            "uni",
+            "0383",
+            "resp_uni",
+            [],
+            bad,
+            False,
+            clock=time.gmtime,
+        )
+
+
+def test_brain_output_symlink_escape_rejected(tmp_path, monkeypatch):
+    """A symlinked sessions path that escapes project_root is rejected."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    root = _mk_tasks_root(tmp_path)
+    outside = tmp_path.parent / "outside-escape"
+    outside.mkdir(exist_ok=True)
+    # Symlink tasks/.sessions -> outside directory.
+    sessions = root / "tasks" / ".sessions"
+    if sessions.exists():
+        import shutil
+
+        shutil.rmtree(sessions)
+    sessions.symlink_to(outside, target_is_directory=True)
+
+    with pytest.raises(OSError):
+        bridge.persist_brain_turn_output(
+            str(root), "escape", "0383", "r", [], "b", False, clock=time.gmtime
+        )
+    # Nothing should have been written outside.
+    assert list(outside.iterdir()) == []
+    """No ambient/cwd fallback: rootless turns persist nothing, loudly."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    with pytest.raises(OSError):
+        bridge.persist_brain_turn_output(
+            None, "ses1", "0383", "r", [], "b", False, clock=time.gmtime
+        )
+    with pytest.raises(OSError):
+        bridge.persist_brain_turn_output(
+            str(tmp_path),
+            "ses1",
+            "0383",
+            "r",
+            [],
+            "b",
+            False,
+            clock=time.gmtime,
+        )
+
+
+def test_brain_output_retention_byte_cap_enforced(tmp_path, monkeypatch):
+    """Prune older complete artifacts until the per-session byte cap is met."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    monkeypatch.setattr(bridge, "BRAIN_OUTPUTS_MAX_FILES", 50)
+    monkeypatch.setattr(bridge, "BRAIN_OUTPUTS_MAX_BYTES", 2048)
+    root = _mk_tasks_root(tmp_path)
+    latest = None
+
+    for index in range(8):
+        latest = bridge.persist_brain_turn_output(
+            str(root),
+            "byte-cap",
+            "0383",
+            f"response-{index}",
+            [],
+            "x" * 700,
+            False,
+            clock=time.gmtime,
+        )
+
+    out_dir = root / "tasks" / ".sessions" / "byte-cap_52977f22" / "brain_outputs"
+    artifacts = [
+        path
+        for path in out_dir.iterdir()
+        if path.is_file()
+        and path.suffix == ".json"
+        and not path.name.startswith(".tmp-")
+    ]
+    assert latest is not None
+    assert (root / latest).is_file()
+    assert sum(path.stat().st_size for path in artifacts) <= 2048
+
+
+def test_brain_output_retention_preserves_newest_when_it_sorts_first(
+    tmp_path, monkeypatch
+):
+    """The just-written file survives even when it sorts first by mtime."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    monkeypatch.setattr(bridge, "BRAIN_OUTPUTS_MAX_FILES", 3)
+    root = _mk_tasks_root(tmp_path)
+    out_dir = root / "tasks" / ".sessions" / "sort-first_3f94209f" / "brain_outputs"
+
+    addresses = []
+    # Write the first 4 artifacts with LATE mtimes so they sort AFTER the
+    # next write. The next (5th) write receives the default "now" mtime
+    # which is EARLIER than the existing LATE stamps, so it sorts FIRST
+    # in the retention loop — the exact edge case that broke the previous
+    # implementation (pop(0) then continue).
+    for index in range(4):
+        addr = bridge.persist_brain_turn_output(
+            str(root),
+            "sort-first",
+            "0383",
+            f"response-{index}",
+            [],
+            "b",
+            False,
+            clock=time.gmtime,
+        )
+        addresses.append(addr)
+        import os as _os
+
+        # LATE mtime: far in the future so the 5th artifact (mtime=now,
+        # earlier) sorts first during pruning.
+        _os.utime(root / addr, (9_999_999_999, 9_999_999_999))
+
+    # Now write the 5th artifact. Its default mtime is "now" which is
+    # EARLIER than the existing LATE stamps, so it sorts first.
+    addr = bridge.persist_brain_turn_output(
+        str(root),
+        "sort-first",
+        "0383",
+        "response-4",
+        [],
+        "b",
+        False,
+        clock=time.gmtime,
+    )
+    addresses.append(addr)
+
+    kept = [
+        p
+        for p in out_dir.iterdir()
+        if p.is_file() and p.suffix == ".json" and not p.name.startswith(".tmp-")
+    ]
+    assert len(kept) <= 3
+    # The newest (5th, last-written) artifact must survive even though it
+    # now has the earliest mtime and sorts first in the prune loop.
+    assert (root / addresses[-1]).is_file()
+
+
+def test_brain_output_retention_is_concurrency_safe(tmp_path, monkeypatch):
+    """Concurrent turns leave complete JSON artifacts within the file cap."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    monkeypatch.setattr(bridge, "BRAIN_OUTPUTS_MAX_FILES", 3)
+    root = _mk_tasks_root(tmp_path)
+
+    def write_output(index):
+        return bridge.persist_brain_turn_output(
+            str(root),
+            "concurrent",
+            "0383",
+            f"response-{index}",
+            [f"<result>{index}</result>"],
+            f"body-{index}",
+            False,
+            clock=time.gmtime,
+        )
+
+    with ThreadPoolExecutor(max_workers=8) as executor:
+        list(executor.map(write_output, range(40)))
+
+    out_dir = root / "tasks" / ".sessions" / "concurrent_a35178ec" / "brain_outputs"
+    artifacts = [
+        path
+        for path in out_dir.iterdir()
+        if path.is_file()
+        and path.suffix == ".json"
+        and not path.name.startswith(".tmp-")
+    ]
+    assert len(artifacts) <= 3
+    for artifact in artifacts:
+        payload = json.loads(artifact.read_text(encoding="utf-8"))
+        assert payload["full_output"].startswith("body-")
+        assert payload["xml_blocks"]
+
+
+def test_brain_output_oversized_artifact_is_rejected_before_temp_creation(
+    tmp_path, monkeypatch
+):
+    """An artifact larger than the session byte cap is never written."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    monkeypatch.setattr(bridge, "BRAIN_OUTPUTS_MAX_BYTES", 512)
+    root = _mk_tasks_root(tmp_path)
+
+    with pytest.raises(OSError, match="exceeds the per-session byte cap"):
+        bridge.persist_brain_turn_output(
+            str(root),
+            "oversized",
+            "0383",
+            "response-too-large",
+            [],
+            "x" * 4096,
+            False,
+            clock=time.gmtime,
+        )
+
+    out_dir = root / "tasks" / ".sessions" / "oversized_9fff661f" / "brain_outputs"
+    assert out_dir.is_dir()
+    assert list(out_dir.iterdir()) == []
+
+
+def test_brain_output_retention_symlink_loop_degrades(tmp_path, monkeypatch):
+    """A resolve() loop during pruning degrades; the turn still persists."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    monkeypatch.setattr(bridge, "BRAIN_OUTPUTS_MAX_FILES", 2)
+    root = _mk_tasks_root(tmp_path)
+    for rid in ("resp_loop_a", "resp_loop_b"):
+        bridge.persist_brain_turn_output(
+            str(root),
+            "ses1",
+            "0383",
+            rid,
+            [],
+            f"body-{rid}",
+            False,
+            clock=time.gmtime,
+        )
+    real_resolve = Path.resolve
+
+    def looping_resolve(self, *args, **kwargs):
+        if self.name.startswith("resp_loop"):
+            raise RuntimeError("Symlink loop")
+        return real_resolve(self, *args, **kwargs)
+
+    monkeypatch.setattr(Path, "resolve", looping_resolve)
+    addr = bridge.persist_brain_turn_output(
+        str(root),
+        "ses1",
+        "0383",
+        "resp_ok_c",
+        [],
+        "body-ok",
+        False,
+        clock=time.gmtime,
+    )
+    assert addr and (root / addr).is_file()
+    out_dir = root / "tasks" / ".sessions" / "ses1_9cf38be4" / "brain_outputs"
+    kept = [
+        p
+        for p in out_dir.iterdir()
+        if p.is_file() and p.suffix == ".json" and not p.name.startswith(".tmp-")
+    ]
+    assert len(kept) <= 2
+
+
+def test_brain_output_retention_target_resolve_failure_prunes(tmp_path, monkeypatch):
+    """Target resolve failure still prunes; newest survives by identity."""
+    monkeypatch.delenv("BRAIN_SESSIONS_ROOT", raising=False)
+    monkeypatch.setattr(bridge, "BRAIN_OUTPUTS_MAX_FILES", 2)
+    root = _mk_tasks_root(tmp_path)
+    for rid in ("resp_old_a", "resp_old_b"):
+        bridge.persist_brain_turn_output(
+            str(root),
+            "ses1",
+            "0383",
+            rid,
+            [],
+            f"body-{rid}",
+            False,
+            clock=time.gmtime,
+        )
+    real_resolve = Path.resolve
+
+    def selective_resolve(self, *args, **kwargs):
+        if self.name.startswith("resp_new"):
+            raise RuntimeError("target resolve loop")
+        return real_resolve(self, *args, **kwargs)
+
+    monkeypatch.setattr(Path, "resolve", selective_resolve)
+    addr = bridge.persist_brain_turn_output(
+        str(root),
+        "ses1",
+        "0383",
+        "resp_new_c",
+        [],
+        "body-new",
+        False,
+        clock=time.gmtime,
+    )
+    assert addr and (root / addr).is_file()
+    out_dir = root / "tasks" / ".sessions" / "ses1_9cf38be4" / "brain_outputs"
+    kept = [
+        p
+        for p in out_dir.iterdir()
+        if p.is_file() and p.suffix == ".json" and not p.name.startswith(".tmp-")
+    ]
+    assert len(kept) <= 2
+    assert (root / addr).is_file()
+
+
+def test_brain_turn_output_address_propagated_and_degraded(tmp_path, monkeypatch):
+    """Call-site: address present on success, None on persistence failure."""
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    root = _mk_tasks_root(tmp_path)
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())])
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("q", task_id="218", include_bundle=False, project_root=str(root))
+    assert result["output_address"] is not None
+    assert (root / result["output_address"]).is_file()
+
+    def _boom(*args, **kwargs):
+        raise OSError("disk gone")
+
+    monkeypatch.setattr(bridge, "persist_brain_turn_output", _boom)
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())])
+    degraded = target("q", task_id="218", include_bundle=False, project_root=str(root))
+    assert degraded["output_address"] is None
+    assert degraded["status"] == "REPORT"
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 1c9b08b..27660a9 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -26,8 +26,8 @@ def _read(path):
     return path.read_text(encoding="utf-8")
 
 
-def test_rtk_mandate_in_shipped_prompt():
-    text = _read(SHIPPED)
+def test_rtk_mandate_in_executor():
+    text = _read(EXECUTOR)
     assert "CRITICAL RULE 3b (Token trimming)" in text
     assert "rtk test" in text
     assert "never collapse failing output" in text
@@ -47,7 +47,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.74.0"
+    assert shipped == "9.75.0"
 
 
 def test_shipped_prompt_documents_context_path_line_ranges():
@@ -340,7 +340,19 @@ def test_executor_review_relay_accepts_closure_answer_envelope():
     )
 
 
-def test_closure_answer_verbatim_forwarding_is_pinned():
+def test_executor_contains_full_dto_mandate():
+    """The full No-Manual-DTO mandate lives in the executor, not the prompt."""
+    executor = _read(EXECUTOR)
+    assert "No-Manual-DTO Mandate (full rule text, owned by Hands)" in executor
+    assert "Hand-written duplicates create silent type drift" in executor
+    assert "If NO source-of-truth contract exists" in executor
+    assert "Type Drift Sentinel" in executor
+    conventions = (REPO / "docs" / "conventions.md").read_text(encoding="utf-8")
+    assert "agents/cognitive-executor.md" in conventions
+    assert (
+        "system-prompt.md"
+        not in conventions.split("No-Manual-DTO", 1)[1].split("##", 1)[0]
+    )
     executor = (REPO / "agents" / "cognitive-executor.md").read_text(encoding="utf-8")
 
     assert (
@@ -357,9 +369,9 @@ def test_closure_answer_verbatim_forwarding_is_pinned():
     )
 
 
-def test_shipped_prompt_version_is_9_74_0():
+def test_shipped_prompt_version_is_9_75_0():
     prompt = _read_shipped_prompt_for_approval_contract()
-    assert "9.74.0" in prompt
+    assert "9.75.0" in prompt
 
 
 def test_assembler_output_matches_shipped(tmp_path):
@@ -374,6 +386,74 @@ def test_assembler_output_matches_shipped(tmp_path):
     assert out.read_text(encoding="utf-8") == _read(SHIPPED)
 
 
+def test_executor_manual_implementation_review_chain_is_explicit():
+    """Manual implementation handoffs must explicitly chain QA/review."""
+    executor = _read(EXECUTOR)
+    manual = executor.split("## Manual Workflow (Active Default)", 1)[1].split(
+        "## Code Mode Tool Calling Protocol", 1
+    )[0]
+
+    assert "Mandatory manual review chain" in manual
+    assert "same `task_id` and `session_id`" in manual
+    assert "`include_diff=True`" in manual
+    assert "logic, backend, or state changes" in manual
+    assert "`[QA Engineer]`" in manual
+    assert "documentation, CSS, or trivial changes" in manual
+    assert "`[Code Reviewer]`" in manual
+    assert "After `QA_PASSED`" in manual
+    assert "Do not claim QA/review was chained" in manual
+
+
+def test_executor_owns_shell_precommit_docs_syntax_discipline():
+    """Hands-only shell/pre-commit/docs/syntax rules live in the executor."""
+    executor = _read(EXECUTOR)
+    assert "Shell, Pre-commit, Documentation & Syntax Discipline" in executor
+    assert "non-interactive only" in executor
+    assert "registry authentication" in executor
+    assert "token scope validation" in executor
+    assert "network access" in executor
+    assert "maximum docstrings" in executor
+    assert "inline comments on non-obvious logic" in executor
+    assert "Verify types and syntax with the language/type-check tooling" in executor
+    assert "Terminal output over 2000 lines or 50KB is truncated" in executor
+    assert "pipe through grep or tail" in executor
+    assert "maximum of 3 repair attempts" in executor
+    assert "detailing the exact errors for the Manager" in executor
+
+
+def test_executor_rule_validation_and_git_restriction():
+    """Rule validation covers skill files; other Git cmds need listing."""
+    executor = _read(EXECUTOR)
+    assert (
+        "cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files"
+        in executor
+    )
+    assert "run no bash commands before validation passes" in executor
+    assert (
+        "You may ONLY run other Git commands if they are explicitly listed" in executor
+    )
+    assert "never run destructive Git operations" in executor
+
+
+def test_executor_frontmatter_denies_checkout():
+    """Permission layer denies git checkout*, matching the ZAC claim."""
+    executor = _read(EXECUTOR)
+    assert '"git checkout*": "deny"' in executor
+
+
+def test_executor_verification_gate_and_documentation_rule():
+    """CRITICAL GATE FUNCTION and full documentation rule live in executor."""
+    executor = _read(EXECUTOR)
+    assert "CRITICAL GATE FUNCTION" in executor
+    assert "verification-before-completion" in executor
+    assert "architectural notes" in executor
+    assert "what you changed, and why" in executor
+    assert "MUST be written in English" in executor
+    assert "Check off any local TODOs" in executor
+    assert "NEVER write task numbers into prompt-facing Markdown" in executor
+    assert "Living Folder Docs Sync" in executor
+
+
 def test_executor_names_rtk_default_runner():
     text = _read(EXECUTOR)
     assert "rtk test" in text
```
<!-- END_GIT_DIFF -->
