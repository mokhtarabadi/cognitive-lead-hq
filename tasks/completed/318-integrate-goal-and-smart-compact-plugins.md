# Task 318: Integrate goal and smart-compact plugins into HQ system

**File:** `tasks/completed/318-integrate-goal-and-smart-compact-plugins.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Fully understand both user-developed globally installed OpenCode plugins in the parent folder, then integrate them into cognitive-lead-hq as callable operational tools: the executor knows both plugins exist and calls them when needed, and implementation plans suggest the Goal plugin for long objectives so the system works correctly in every project running this workflow.

## Manager's Notes

Original (FA, verbatim evidence): "Opencode goal plugin and opengoal smart plugin Both located at parent folder and both installed globally هدف اینه این دو تا پلاگین من رو کامل بخونه، توی پوشه parent وجود دارن، کامل درکشون کنه. این پلاگین‌ها رو خودم توسعه دادم. بعد کامل که فهمیدی، درکشون کردی، می‌خوام توی سیستم‌مون integrateش کنی. سیستم ما مثلاً می‌تونه cognitive executor باشه، مثلاً اونجا باشه، توی agentش می‌تونه تو audit skill باشه، اگر نیازه Gitignore نسبت به این پلاگین‌ها ویرایش بشه یا agent چیزی نسبت به این پلاگین‌ها ویرایش بشه. می‌تونه توی system prompt باشه، توی اون fragmentها باشه. یه task بساز، بعد context full بگیر، بعد با graph چیزهایی که از پلاگین‌ها هم فهمیدی یاد بگیر، هدفشون چیه، کارشون چیه، چرا ساخته شدن. همه چیز رو با هم بده به brain و از brain بخواه که برات برنامه‌ریزی کنه."

Translated technical English (prompt-refactor output): Explore `../opencode-goal-plugin` (slash `/goal` with file state, idle auto-continue, compaction-safe) and `../opencode-smart-compact` (`/magic-compact|trim|stats` plus `compact_context` and `read_omitted_content` tools, V2-native per-turn summaries with verbatim user messages). Both are globally installed via `~/.config/opencode/opencode.json` plugins list and user-developed. Identify each plugin's purpose, behavior, and rationale with file citations. Then integrate into HQ at the correct touchpoints (candidate: `agents/cognitive-executor.md`, `skill-templates/audit-agents/SKILL.md`, `.gitignore`, `prompts/fragments/*` plus regenerated `system-prompt.md`). Create this task, gather full HQ plus plugin context including knowledge graph, and request Brain planning via `brain_turn`. No implementation until the Brain plan is approved.

## Local TODOs

- [x] Step 1: Move and baseline (tree/graph/reads)
- [x] Step 2: Update .gitignore with Goal runtime state
- [x] Step 3: Update agents/cognitive-executor.md with Goal boundary
- [x] Step 4: Update audit-agents SKILL runtime versus config rule
- [x] Step 5: Sync fragments 22 and 09 plus version bump
- [x] Step 6: Update docs/compaction.md global plugins clarification
- [x] Step 7: Regenerate system-prompt.md plus sync check
- [x] Step 8: Documentation and evidence plus lint plus qa_transition

## Acceptance Criteria

- [x] AC1 .gitignore contains goal runtime lines and zero smart-compact ignore lines
- [x] AC2 executor contains Goal boundary and preserves Smart Compact ops
- [x] AC3 audit SKILL distinguishes runtime versus deliberate config
- [x] AC4 both fragments synced and system-prompt regenerated with sync check green
- [x] AC5 docs/compaction confirms global plugins and no repo plugins key
- [x] AC6 CHANGELOG plus task evidence complete with no placeholders

## Verification Evidence

- **Test command:** _(docs-only change, no test suite; marker scan plus grep gates plus assembler plus lint)_
- **Expected result:** all grep gates exit 0 (negative check exit 1 handled), assembler exit 0 with version 9.59.1, sync check green, `lint_task_file` passes
- **Actual result:**
  - `grep -n goal-state .gitignore` → 63:.opencode/goal-state.json, exit 0
  - `grep -n STOP_GOAL .gitignore` → 65:STOP_GOAL, 66:.opencode/STOP_GOAL, exit 0
  - `grep -n goal-evidence .gitignore` → 64:.opencode/goal-evidence.json, exit 0
  - `grep -n smart-compact .gitignore` → empty (correctly absent deliberate config), exit 1 handled with echo
  - `grep -n Goal Plugin Boundary agents/cognitive-executor.md` → 105, exit 0; `grep -n magic-compact agents/cognitive-executor.md` → matches, exit 0
  - `grep -n goal-state skill-templates/audit-agents/SKILL.md` → 42, exit 0; `grep -n smart-compact.jsonc skill-templates/audit-agents/SKILL.md` → 14, 41, exit 0
  - `grep -n Smart Compact prompts/fragments/22-compaction_protocol.md` → 6, exit 0; `grep -n Goal state note prompts/fragments/09-hands_protocols.md` → 165, exit 0
  - `grep -n no plugins key docs/compaction.md` → 90, exit 0
  - `python3 scripts/prompt-build/assemble_system_prompt.py` → Assembled 105766 bytes, exit 0; `head -1 system-prompt.md` → 9.59.1; `lint_system_prompt_sync` → in sync, exit 0
  - Strict tooling gate (docs-only): root dot, marker scan [package.json, requirements.txt, go.mod, Cargo.toml, pom.xml, build.gradle] matched empty, reason no stack marker found, test/build/lint/typecheck skipped as N/A for markdown plus gitignore change
  - Sibling docs: agents, prompts/fragments, skill-templates, docs README plus DECISIONS inspected before edits; additive docs only, no structural contract change, explicitly no ADR added
- **Exit code:** 0
- **Rework evidence:** assembler re-run after operational rewrite → 106124 bytes, version 9.59.2, `lint_system_prompt_sync` green, `lint_task_file` green; executor Goal section verified operational via read; no new files, same eight paths
- **Hotfix evidence:** `sed limits.ts 25-26` → STOP_FILE_NAME STOP_GOAL inside .opencode, exit 0; `sed state.ts 54,61-64` → goal-state.json plus .opencode join, exit 0; `grep goal-state/STOP_GOAL .gitignore` → 4 lines exact block, exit 0; `grep smart-compact .gitignore` → empty, exit 1 handled; `grep MUST NOT auto-send executor` → match, exit 0; `grep Goal idle rule fragment 09` → match, exit 0; `grep Compaction precedence docs plus fragment 22` → both match, exit 0; assembler → 106637 bytes version 9.59.3, sync green; `lint_task_file` → pass (re-run after evidence edit); tooling gate docs-only skip recorded above

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Plugin host APIs drift from HQ assumptions, or fragment edits drift generated `system-prompt.md` without regeneration (mitigated: assembler run plus sync check green).
- **Rollback plan:** Revert docs/config hunks via `git checkout --` on the eight touched paths only; task file stays in `tasks/in-progress/` until QA transition.

---

## Execution Log & Reasoning

Assumption A1: `opengoal smart plugin` means `../opencode-smart-compact` (only smart plugin in parent folder, globally installed). Reason: exact name match on parent listing plus global plugins list.
Assumption A2: Integration stays inside HQ repo (executor, audit skill, gitignore, fragments). Reason: Manager examples all point inside HQ, no plugin-repo edits requested.
Intent validation: FA plus EN input translated to technical English above. Clarity check passed (explore, task, full context, graph, Brain plan). No Clarification Halt.
Seat Check: domains = plugin runtime plus HQ SOP integration → seats requested: Software Architect plus Senior Programmer (2-seat lightweight consult); skipped UI/UX Designer (no user surface), Planner/Strategist (no scope decisions), QA/Reviewer (later stages). Trigger map TITLE+BODY whole-word: no UI, Architect, or Programmer triggers hit (workflow/package are substrings); UX-intent fallback miss. Single-seat would be valid, 2-seat consult chosen for cross-domain safety.
Brainstorm: not required — docs/config integration fully reversible via git, 2-seat consult suffices.
Context evidence: parent listing confirms opencode-goal-plugin plus opencode-smart-compact globally installed via ~/.config/opencode/opencode.json plugins list. Goal graph src 68 nodes/79 edges; smart-compact graph src 101 nodes/110 edges; HQ graph 4484 nodes/6265 edges (previous build). Subagents ses_ebac17155ffe (goal), ses_ebac17153ffe (smart), ses_ebac17143ffe (HQ touchpoints) all completed read-only.
Brain plan verdict (task 318, session ses_ebac9dae6ffe, stage plan): REPORT with F1-F5, D1-D4, 6 touchpoints (.gitignore, executor, audit skill, 2 fragments, docs/compaction, regenerate system-prompt), 6 implementation steps, R1-R3. Selected path: HQ task file stays truth, goal stays external scratch, Brain Bridge stays only automation path, Smart Compact fragment sync only, no plugin-repo edits, no repo plugins key. Manager approval received via question tool ("Approve plan", try 1). Implementation XML issued bare unfenced after one timeout retry plus one strict-reject re-emit.
Implementation notes: docs and config only across eight paths. `.gitignore` appends four goal runtime lines while smart-compact config stays tracked. Executor gains Goal boundary subsection under compaction with Smart Compact ops untouched. Audit skill gains project-agnostic Goal runtime bullet beside existing deliberate-config rules. Fragment 22 already synced so no edit, fragment 09 appends goal-state note, version bumped 9.59.0 to 9.59.1. `docs/compaction.md` gains global-plugins bullet. `system-prompt.md` regenerated (105766 bytes) with sync check green. CHANGELOG entry appended under Unreleased Added without header duplication. Sibling README plus DECISIONS inspected in agents, prompts/fragments, skill-templates, docs; additive docs only, explicitly no ADR added. No task numbers in prompt-facing prose; CHANGELOG carries the reference as allowed.
Rework per Manager rejection of the boundary framing: the first pass kept the goal plugin at arm's length, but the essence of this project is a reusable OpenCode workflow, so the executor must know both plugins and call them when needed. Rewrote the executor section, fragment 09 note, docs bullet, Goal, and CHANGELOG entry to operational tool-use; version bumped again to 9.59.2. No new task created; all rework stays inside this task file.
QA hotfix (QA_REJECTED, 3 gaps): verified kill-switch truth in plugin sources (STOP_FILE_NAME STOP_GOAL inside .opencode per limits.ts, STATE_FILENAME goal-state.json with .opencode join per state.ts 54 and 61-64) and fixed .gitignore header to the exact required block; replaced the executor Goal section with the exact hardened text (MUST NOT auto-send, STOP behavior, exact-only inputs, active-only transitions) keeping slash, state, and evidence knowledge; appended the exact idle-rule line to fragment 09 beside the operational note; appended the exact compaction-precedence paragraph to fragment 22 and docs/compaction (restore never resurrects cleared or completed); bumped version to 9.59.3 and regenerated (106637 bytes, sync green). Stays in qa lane; staged via stage_and_inject_diff, no lane move.
Autopilot pipeline: re-QA returned QA_PASSED (kill switch covered, idle blocked, precedence present, exact inputs match parser; docs-only so grep plus assembler plus sync plus lint suffice). Code Reviewer returned technically APPROVED with PO_REVIEW_PENDING (5 strengths, 3 lows: executor line numbers may shift, docs spells paths as words, Step 8 unchecked until close; follow-ups R1-R3). Manager accept quote for closure: Approved for closure.
Closure note 2026-10-16: QA_PASSED plus technical APPROVED with PO_REVIEW_PENDING on record; file moved qa to completed via git mv; staged hunks committed via commit_and_clean_task with docs message; sibling slices inspected, no slice change.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `57560168b3563b8c3c511fa1b5646707d16953a2`
<!-- END_GIT_DIFF -->
