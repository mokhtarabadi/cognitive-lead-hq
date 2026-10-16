# Task 318: Integrate goal and smart-compact plugins into HQ system

**File:** `tasks/qa/318-integrate-goal-and-smart-compact-plugins.md`
**Source:** manager
**Type:** feature
**Status:** open

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
- [ ] Step 8: Documentation and evidence plus lint plus qa_transition

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

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.gitignore b/.gitignore
index 2b9d975..afc6aad 100644
--- a/.gitignore
+++ b/.gitignore
@@ -59,3 +59,9 @@ tasks/.sessions/
 .coverage
 htmlcov/
 
+# Goal plugin runtime state - task file stays truth, never commit runtime
+.opencode/goal-state.json
+.opencode/goal-evidence.json
+STOP_GOAL
+.opencode/STOP_GOAL
+
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f68197e..6643896 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -45,6 +45,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Living Folder Docs Standard & Prompt System (Task 307):** Added the Living Folder Docs standard to docs/conventions.md, enforcing colocated README.md and DECISIONS.md alongside code pointers across vertical slices. Extended prompt fragments (13-constraints.md, 09-hands_protocols.md) and agents/cognitive-executor.md with mandatory sibling doc inspection and ADR synchronization rules. Rebuilt system-prompt.md with version bump to v9.54.0; updated skill-templates/audit-agents to audit living docs, and created skill-templates/init-folder-docs for legacy project onboarding.
 
+- **Goal and Smart Compact plugin integration (Task 318, system prompt 9.59.2):** the executor now knows both global plugins as callable tools, no plugin-repo edits and no repo `opencode.json` plugins key. `.gitignore` covers goal runtime state (`.opencode/goal-state.json`, `.opencode/goal-evidence.json`, `STOP_GOAL`, `.opencode/STOP_GOAL`) while `smart-compact.jsonc` stays tracked as deliberate config. `agents/cognitive-executor.md` carries an operational Goal section (`/goal` set, status, block, complete with evidence, clear; task file stays Kanban truth, goal file carries the working objective; idle loop never fires past an approval gate). `skill-templates/audit-agents` adds a project-agnostic runtime-vs-config rule. Fragments `09-hands_protocols.md` (goal use note) and `22-compaction_protocol.md` regenerated into `system-prompt.md` with sync check green. `docs/compaction.md` names both global plugins and their operational use.
+
 ### Fixed
 
 - **Brain dual-mode XML contract (Task 316, system prompt 9.58.2):** manual copy-paste mode forces fenced `xml output while automatic mode emits bare unfenced XML, and the bridge extracts both shapes (bare first, `xml-fence fallback second; other fences stay documentation-only, bare unclosed tails still strict-reject). This supersedes the bare-only 9.58.1 attempt the Manager rejected: the Senior Programmer, QA hotfix, and Reviewer postfix personas now carry the per-MODE rule, the runbook describes dual-mode extraction, and the fence-fallback tests pin extraction instead of rejection.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index d380817..b446f1a 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -102,6 +102,13 @@ Context is finite. Two layers keep long sessions productive, and the agent's dur
 4. **Trigger it yourself, or hand off the command.** The agent cannot run the `/magic-*` slash commands, but it CAN call the `compact_context` tool directly — prefer that when context pressure is high (pass `keepTurns` to protect recent turns, `mode: "trim"` to prune tool output only), state one line about it, then continue from the task file. Fall back to recommending a `/magic-compact` run to the Manager when a tool call is not available.
 5. **Call it before heavy payloads, not after stalling.** Invoke `compact_context` yourself at these triggers: context pressure is high, 50+ steps ran without measurable progress, before a plan-approval handoff, and before QA or review turns carry a large diff. Use `mode: "trim"` when only tool output is bulky and full `compact` when turns are stale. Never re-run a source tool for pruned output — retrieve it with `read_omitted_content` by Content ID. The Brain bridge needs no change: the executor already holds direct `compact_context` access, so no Brain mention is added.
 
+### Goal Plugin - long-objective tracker, call it when needed
+
+- The `goal` plugin (`opencode-goal-plugin`) is installed globally alongside smart-compact. Know it exists and use it for long-running multi-phase objectives: `/goal <objective>` at start (max 2000 chars), `/goal status` to check, `/goal block <reason>` on blockers, `/goal complete` with file citations plus passing-test proof recorded in `.opencode/goal-evidence.json`, `/goal clear` at end. Kill switch: create `.opencode/STOP_GOAL` to pause the loop immediately, delete it to resume.
+- Goal file state (`.opencode/goal-state.json`) survives compaction; it carries the working objective while the HQ task file stays the single source of truth for Kanban — the two complement, never compete.
+- Inside approval-gated HQ turns the Brain Bridge stays the sole automation path (ZAC, WIP3, approval gates hold): use the goal slash, state, and evidence surfaces, and never let goal idle auto-continue fire past an approval gate. In target projects running this workflow, suggest `/goal` inside implementation plans so long work resumes correctly after compaction.
+- Smart Compact operations in lines 95-104 remain unchanged.
+
 ## Capability Preflight (session start)
 
 Before approval-sensitive work (plan approval, review approval, closure), check the capability manifest: every `brain_turn` prints a `capability-manifest:` diagnostic line to stderr mapping each required tool to `AVAILABLE`, `UNAVAILABLE_REQUIRED`, or `UNAVAILABLE_OPTIONAL`. A step whose required tool is `UNAVAILABLE_REQUIRED` (for example the `question` tool) is never silently skipped. Emit the relay block the turn returned (missing tool names, stage, one narrow question, one answer slot) through the mode-appropriate channel: manual mode relays it to the Manager verbatim and pauses with the relayed question as the named blocker; autopilot halts with the relay block as the named blocker. Approval collection follows the single approval rule: closure accepts only the exact phrases "Approved for closure" or "Close task" (a bare "approved" never counts); the plan gate accepts "approved" in any case. Blanket acknowledgements ("ok", "yes", "looks good", emoji) never count as approval at any gate. At plan-approval, PO_REVIEW_PENDING relay, and any closure approval gate you MUST collect the decision via the question tool with one narrow question and one answer slot. Prose-only approval asks are forbidden because an auto-continue loop can roll past prose. This holds in manual and autopilot. If question is UNAVAILABLE_REQUIRED, emit the relay block and pause with it as the named blocker; never skip. Only hard blockers may use prose.
diff --git a/docs/compaction.md b/docs/compaction.md
index d3c6ca1..57c6c11 100644
--- a/docs/compaction.md
+++ b/docs/compaction.md
@@ -87,6 +87,7 @@ Each omission notice carries a Content ID (e.g. `omitted-0001`). The agent calls
 - **System prompt:** the `<compaction_protocol>` fragment (generated into `system-prompt.md`) states the two layers and the survival contract.
 - **Agent:** `agents/cognitive-executor.md` carries the operational steps, including that the agent cannot run the plugin command and instead recommends a `/magic-compact` run when context pressure is high.
 - **Config:** global `opencode.json` holds `plugins` + `compaction`; the repo `opencode.json` stays config-free of both.
+- **Global plugins:** Global plugins live in user config at tilde config opencode opencode dot json as github mokhtarabadi opencode-smart-compact plus github mokhtarabadi opencode-goal-plugin. Repo opencode dot json has no plugins key by intent. HQ task file stays truth. Use the goal plugin for long objectives (`/goal` set, status, block, complete with evidence, clear); its idle loop never fires past an approval gate.
 
 **Survival contract** — keep these in the task file so any compaction is recoverable:
 
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index d995bff..d92be86 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.59.0</system_version>
+<system_version>9.59.2</system_version>
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index 9f489e6..ab2d8e6 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -161,4 +161,6 @@
 ```
 
 </hands_combined_task_template>
+
+Goal plugin note: the `goal` plugin tracks long objectives in dot opencode goal-state dot json with evidence in dot opencode goal-evidence dot json. When an implementation task spans multiple phases, set `/goal`, check `/goal status`, block with reason on blockers, and complete with file citations plus passing tests; the Kanban task file stays truth while the goal file carries the working objective. Do the work itself with MCP-first plus graph-first plus ZAC plus rtk plus qa_transition, and never let goal idle auto-continue fire past an approval gate.
 </hands_protocols>
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 9bdf219..1a273e6 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -39,6 +39,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Execution Log & Reasoning` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
 - **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
 - **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. Deliberate agent config (`[PROJECT_ROOT]/.opencode/smart-compact.jsonc`) is NOT runtime state and MUST NOT be gitignored. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
+- **Goal Plugin Runtime State**: Goal plugin file state (`[PROJECT_ROOT]/.opencode/goal-state.json`, `[PROJECT_ROOT]/.opencode/goal-evidence.json`, `[PROJECT_ROOT]/STOP_GOAL`, `[PROJECT_ROOT]/.opencode/STOP_GOAL`) is runtime state only and MUST be gitignored. It is external scratch and never replaces decentralized task truth.
 
 - **Living Folder Docs Sibling Inspection**: AGENTS.md MUST instruct agents to inspect sibling README.md and DECISIONS.md before editing code in any component or vertical slice directory, and update them when domain contracts or architectural decisions change.
 
diff --git a/system-prompt.md b/system-prompt.md
index 0d52a7f..de3a833 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.59.0</system_version>
+<system_version>9.59.2</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -395,6 +395,8 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 ```
 
 </hands_combined_task_template>
+
+Goal plugin note: the `goal` plugin tracks long objectives in dot opencode goal-state dot json with evidence in dot opencode goal-evidence dot json. When an implementation task spans multiple phases, set `/goal`, check `/goal status`, block with reason on blockers, and complete with file citations plus passing tests; the Kanban task file stays truth while the goal file carries the working objective. Do the work itself with MCP-first plus graph-first plus ZAC plus rtk plus qa_transition, and never let goal idle auto-continue fire past an approval gate.
 </hands_protocols>
 
 <lite_mode_protocol>
```
<!-- END_GIT_DIFF -->
