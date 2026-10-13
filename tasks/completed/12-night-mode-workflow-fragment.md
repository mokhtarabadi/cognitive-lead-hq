# Task 12: Night mode workflow fragment + audit ignore for the compact config

**File:** `tasks/qa/12-night-mode-workflow-fragment.md`
**Source:** manager (2026-10-13, after the overnight autopilot run)
**Type:** feature
**Status:** open

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
closure approval.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 23953b5..184925c 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,9 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Night mode workflow** (`prompts/fragments/23-night_mode.md`, cross-referenced from the execution workflow, human-readable copy in `docs/night-mode.md`). Documents the overnight autopilot mode proven in practice: a locked no-questions rule with self-decisions logged in the task file, delegated authority bounded to plan/QA/review/closure (never deploys, release bumps, credentials or pushes), a one-task-at-a-time pipeline, evidence rules including the dispute path for rejections that contradict the working tree, compaction survival through project memory, and a fixed morning-report shape. `system-prompt.md` rebuilt; version bumped to 9.59.0.
+- **`audit-agents` ignores the session-compact config.** `.opencode/smart-compact.jsonc` is deliberate, agent-managed plugin configuration, so the auditor never flags it as OpenCode scaffolding, never patches or deletes it, and never demands it be gitignored.
+
 - **Brain pre-send token budget guard (Task 317):** the bridge now estimates input as chars divided by four, adds the live reserved output cap, and checks the total against the provider window minus margin before sending. Window and margin are env-tunable (`BRAIN_CONTEXT_WINDOW_TOKENS`, `BRAIN_BUDGET_MARGIN_TOKENS`, defaults 1048576 and 8192, documented in `.env.example` and set in `.env`) — nothing hardcoded in the send path. Trim order is oldest history, then diffs and context, then bundle; persistent over-budget returns a `BRAIN_BUDGET_OVER` REPORT hint with numbers and skips the provider instead of a hard 400. Pure helpers plus eight regression tests; 128K and 256K caps with xhigh keep working inside the window.
 
 - **Index-safe staging mode for `stage_and_inject_diff` (Task 315, fixes #29):** new opt-in `skip_add` flag skips the `git add` step and only extracts + injects the staged diff, so parallel sessions sharing files can keep hunk-level index surgery (`git apply --cached`) intact; the default path now snapshots pre-existing staged state and warns naming affected files; whole-file staging contract documented in the tool docstring. Trailing-optional param, fully backwards compatible. Test-backed (preserve / warn / default-unchanged).
@@ -40,7 +43,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
-- **Brain dual-mode XML contract (Task 316, system prompt 9.58.2):** manual copy-paste mode forces fenced ```xml output while automatic mode emits bare unfenced XML, and the bridge extracts both shapes (bare first, ```xml-fence fallback second; other fences stay documentation-only, bare unclosed tails still strict-reject). This supersedes the bare-only 9.58.1 attempt the Manager rejected: the Senior Programmer, QA hotfix, and Reviewer postfix personas now carry the per-MODE rule, the runbook describes dual-mode extraction, and the fence-fallback tests pin extraction instead of rejection.
+- **Brain dual-mode XML contract (Task 316, system prompt 9.58.2):** manual copy-paste mode forces fenced `xml output while automatic mode emits bare unfenced XML, and the bridge extracts both shapes (bare first, `xml-fence fallback second; other fences stay documentation-only, bare unclosed tails still strict-reject). This supersedes the bare-only 9.58.1 attempt the Manager rejected: the Senior Programmer, QA hotfix, and Reviewer postfix personas now carry the per-MODE rule, the runbook describes dual-mode extraction, and the fence-fallback tests pin extraction instead of rejection.
 
 - **Context MCP singleton report write path (Task 286):** after the singleton migration the context server runs from `~/.config/opencode/mcp-context-server`, but `create_tree_report`, `read_source_files`, and `extract_signatures` wrote their reports to `Path("context-reports")` — the process cwd — so generated maps landed in the global install dir and the project's `context-reports/` went stale (the newest repo tree report stayed at 2026-09-18, still listing the removed `stacks/` directory; found by the task 285 smoke test). All three writers now resolve `report_dir = workspace_root / "context-reports"` from the per-call `project_root` argument the caller supplies, and the `.gitignore` safeguard writes to `<project_root>/.gitignore` via a new `_ensure_context_reports_ignored(workspace_root)` parameter. `extract_signatures`'s regex fallback also reads the resolved `path` instead of the cwd-relative `file_path`. The project_root-omitted path is unchanged (cwd fallback, still surfaced client-visibly), and a new regression test proves a foreign cwd writes nothing outside `<project_root>/context-reports/`. Context-server suite: **70 passed** (69 pre-existing + 1 new).
 
@@ -168,7 +171,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Bridge follow-up: attach-note wording, cross-project bleed, closure gate, rtk mandate (Task 241, syncs GitHub issue 15):** remaining `read_file` pull orders removed from both task-attach notes (`_strip_task_diff`, `_TASK_ATTACH_CAP`) — no file tools, quote paths, Hands feeds `fed-context` under the same `task_id`. `load_history`/`load_fed_context` legacy fallbacks now apply ONLY when the resolved root IS the legacy global (a project with its own `tasks/` dir gets fresh `[]`/`''`, never foreign turns); writes were already per-project. New `validate_closure_checklist` (QA_PASSED + PO_REVIEW_PENDING + exact approval words + non-empty diff + `extract_session_decisions` evidence) closes the never-called decision-capture gap. New CRITICAL RULE 3b in `prompts/fragments/09-hands_protocols.md` mandates `rtk test` for passing suites; shipped prompt rebuilt to **9.38.0**. 9 new tests (wording, no-bleed, closure gate, prompt-sync). Full suite: **387 passed**, zero failures.
 - **Context-handling gaps: utilization ledger + over-cap signatures fallback (Task 241 extension, web-research findings):** `mcp-brain-bridge/server.py` gains a per-turn context ledger (`_MODEL_WINDOW_CHARS=200000`, one JSON line per turn — task_id, budget_chars, est_tokens, util_pct, truncated — to `context_ledger.jsonl`, best-effort never-raise) and the prompt-size warn now shows `util~%`, so truncation pressure is measured instead of guessed. `mcp-context-server/server.py` `process_source_file` over-cap branch now appends tree-sitter signatures (or a narrow-paths pointer) instead of silently skipping the file, so discovery keeps structural signal past the cap. 2 new tests (ledger+util, too-large-signatures). Full suite: **389 passed**, zero failures.
 - **Decision-redactor word-edge leak (Task 242, Phase 1 B1):** `mcp-decision-server/redactor.py` assignment rule leading edge `\b` → `(?<![A-Za-z0-9])` in both sanitize and verify patterns, so ENV-style `KEY=value` names (`BRAIN_API_KEY=`, `FOO_SECRET=`) redact while prose `topsecret=` stays untouched; new short-Bearer rule (`{4,7}` chars with digit gate) catches `Bearer abc123`-shaped tokens while prose `Bearer tokens` and the `{8,}` rule stay unchanged. 4 new tests (3 failed pre-fix as required). Full decision suite: **105 passed**, zero failures. QA-hotfix regression tests added (punctuation Bearer, quoted forms — all green pre-fix; the claimed `-1` suffix leak did not reproduce: `-` is inside the token class, direct evidence recorded in Task 242). Full suite: **400 passed**, zero failures.
-- _*Decision-server DECISION_* env support (Task 243):_* `mcp-decision-server/server.py` now reads `DECISION_API_BASE`, `DECISION_API_KEY`, `DECISION_MODEL`, `DECISION_REASONING_EFFORT`, each with `BRAIN_*` fallback (fail-closed error names both key vars); new module-level `_get_api_base()` helper; `.env.example` DECISION section extended with the four lines + fallback docs. 3 new contract tests (precedence, blank-fallback, fail-closed); 2 old tests fixed for env hermeticity. Full suite: **396 passed**, zero failures.
+- _\*Decision-server DECISION_* env support (Task 243):_* `mcp-decision-server/server.py` now reads `DECISION_API_BASE`, `DECISION_API_KEY`, `DECISION_MODEL`, `DECISION_REASONING_EFFORT`, each with `BRAIN_*` fallback (fail-closed error names both key vars); new module-level `_get_api_base()` helper; `.env.example` DECISION section extended with the four lines + fallback docs. 3 new contract tests (precedence, blank-fallback, fail-closed); 2 old tests fixed for env hermeticity. Full suite: **396 passed**, zero failures.
 - **Bridge nested reasoning-effort fix (Task 244):** `mcp-brain-bridge/server.py` now sends `reasoning.effort` as a nested `reasoning: {effort}` object in the Responses body (the flat `reasoning_effort` key was rejected with a provider 400 on the first live OpenRouter turn); the explicit-temperature branch drops the reasoning key, mirroring the bridge contract. 2 existing tests updated to the nested shape. Full suite: **400 passed**, zero failures.
 - **Context-paths project-root fix plus semantic XML gate (Task 245, Phase 1):** `mcp-brain-bridge/server.py` `build_paths_attach` now accepts `project_root` via a new `_paths_base` helper (explicit project dir wins, workspace root stays fallback) and the `brain_turn` call site threads it through — relative `context-reports/*.md` paths resolve under the project instead of the server install dir, ending the cross-install `missing_context` loop; caps and labels unchanged. New pure `validate_hands_xml_blocks` (required phase markers per block type, word-bound; unknown roots, missing close tags, empty bodies rejected) runs after tolerant extraction — syntactically valid but contract-incomplete XML now triages as REPORT with an inline `[xml-semantic-reject]` list instead of executing. 11 new tests (5 resolver: project-root win, missing label, invalid fallback, cwd independence, size-pattern truncation; 6 validator: valid accept, missing phase, missing bash_phase, empty/unclosed, unknown root, non-string root fallback). Full suite: **411 passed**, zero failures (6 memory-server tests need the memory project env for `yaml`; proven env-only, green there). Review hotfix: phase checks now match opening elements inside the comment-stripped root body (bare words, comments, post-close text rejected) plus a `brain_turn` REPORT-integration test; docstring number removed. 4 more tests. Full suite: **415 passed**, zero failures.
 - **Eval harness residual hardening (Task 251):** `mcp-brain-bridge/eval_harness.py` closes the two low residuals deferred at review time. `_op_is_zac` now normalizes the executable position (basename of token 0, or token 1 when token 0 is exactly `sudo`) and requires a protected verb (`add`/`commit`/`push`) next, so path-prefixed (`/usr/bin/git add`) and `sudo`-prefixed git invocations are flagged while prose (`legit git status`, `git status`) stays clean. New pure `_is_finite_number` predicate (finite int/float, booleans and nan/inf rejected) backs `_mean` and the cost/latency aggregate filters, so invalid numerics never enter aggregates; per-row columns still preserve raw values. 6 new tests (absolute-path, sudo, prose guard, boolean aggregates, non-finite aggregates, mean filter). Full suite: **508 passed**.
diff --git a/docs/README.md b/docs/README.md
index 609cf63..282dbd3 100644
--- a/docs/README.md
+++ b/docs/README.md
@@ -9,6 +9,7 @@ Human-readable spec hub for conventions, architecture-adjacent guides, service t
 - `conventions.md` — Syntax, naming, file boundaries, and automation patterns (bound spec).
 - `brain-bridge.md` — Brain Bridge protocol reference for QA/review turns.
 - `compaction.md` — Context compaction and smart-compact usage.
+- `night-mode.md` — Overnight autopilot workflow (delegated authority, per-task pipeline, morning report).
 - `openchamber.md` — OpenChamber session linking guide.
 - `opencode-shell-strategy.md` — Shell execution strategy.
 - `services.md` — Service topology for MCP daemons.
diff --git a/docs/night-mode.md b/docs/night-mode.md
new file mode 100644
index 0000000..eb679fc
--- /dev/null
+++ b/docs/night-mode.md
@@ -0,0 +1,71 @@
+# Night Mode (Overnight Autopilot)
+
+Night mode is the standing workflow for handing the Manager's night over to the
+Hands: a queue of tasks is planned, implemented, verified, reviewed, and closed
+while he sleeps, and he wakes up to finished work plus evidence instead of a
+queue of questions.
+
+Source of truth: `prompts/fragments/23-night_mode.md` (assembled into
+`system-prompt.md`). The execution workflow cross-references it, and it overrides
+the Step 6 QA gate, the Step 7 review gate, and the Step 8 closure approval for
+the duration of the night.
+
+## Trigger
+
+Any of: "night mode", "on autopilot do X", "I'm going to sleep, do everything",
+"100% autopilot until morning". The mode locks from that word until the Manager
+returns or says "manual" / "stop".
+
+## The one rule
+
+**Do not ask.** No `question` tool, no approval waits. Decide on the Manager's
+behalf and log every self-decision in the task file as `D1, D2, …` with a
+one-line reason.
+
+## Delegated authority (and its ceiling)
+
+Granted: plan approval, QA verdicts, review acceptance, and task closure
+including the staging and closure commits.
+
+Not granted: production deploys, release version bumps, destructive or
+irreversible operations, credential use, pushing to remotes. Those wait for
+morning.
+
+## Per-task pipeline
+
+One task at a time (WIP = 1): plan with a Seat Check → review the plan and accept
+or send edits → implement → run the named tests and record command/expected/
+actual/exit code → QA with the diff → Code Review with the diff → accept on the
+Manager's behalf and close per protocol → next task. Never batch two tasks into
+one commit.
+
+## Evidence rules
+
+- Every verdict carries file:line, or a command plus its exit code.
+- A rejection that contradicts the working tree is a **dispute**, not a fix:
+  re-read the file, cite the lines, record the dispute. Three rejections on the
+  same evidence switch to the dispute path — never loop a fourth time.
+- Prove a regression test has teeth by reintroducing the bug once, watching it
+  fail, then restoring the fix.
+- Log every adaptation (substituted command, skipped tool, replaced approach)
+  with its reason.
+
+## Compaction survival
+
+Before context gets tight, write the mode, the queue, the active task id, and the
+next action into project memory; re-read that memory after any compaction. See
+`compaction.md` for the compaction layers themselves.
+
+## Morning report shape
+
+1. One-line verdict per task, with commit hashes.
+2. What shipped, grouped, with the tests that prove it.
+3. What needs the Manager (checks only he can perform, credentials, production
+   parameters).
+4. Flags: anything left in a non-production state.
+5. Honest notes: disputes, extra commits, workarounds, unverified items.
+
+## Rollback
+
+Night mode grants no irreversible authority, so ending it is just the word
+"manual": the pipeline reverts to the normal Manager-gated approvals.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index b869417..d995bff 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.58.2</system_version>
+<system_version>9.59.0</system_version>
diff --git a/prompts/fragments/11-execution_workflow.md b/prompts/fragments/11-execution_workflow.md
index a70588a..a1cb011 100644
--- a/prompts/fragments/11-execution_workflow.md
+++ b/prompts/fragments/11-execution_workflow.md
@@ -41,4 +41,6 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 
 9. **Step 9: Next Task Transition (Sprint Strategist)**
    - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
+
+**Night mode override.** When the Manager hands over the night ("night mode", "100% autopilot until morning"), `<night_mode>` governs: the Step 6 QA gate, the Step 7 review gate, and the Step 8 closure approval are pre-authorized and played by the Hands, and the question tool is not used until he returns. Every other step in this pipeline is unchanged.
 </execution_workflow>
diff --git a/prompts/fragments/23-night_mode.md b/prompts/fragments/23-night_mode.md
new file mode 100644
index 0000000..e7710f6
--- /dev/null
+++ b/prompts/fragments/23-night_mode.md
@@ -0,0 +1,38 @@
+<night_mode>
+**Trigger.** The Manager hands over the night: "night mode", "on autopilot do X", "I'm going to sleep, do everything", "100% autopilot until morning". From that word the mode is LOCKED until he returns or says "manual" / "stop".
+
+**The one rule that defines night mode: do not ask.** No `question` tool, no approval waits, no "should I?" messages. Decide on the Manager's behalf and log every self-decision in the task file as `D1, D2, …` with a one-line reason. He wakes up to decisions plus evidence, never to a queue of questions.
+
+**Authority granted for the night — and nothing more.**
+
+- Plan approval, QA verdicts, and review acceptance are played by the Hands.
+- Task closure is pre-authorized: accept on his behalf and close per protocol, including staging and the closure commit.
+- NOT granted: production deploys, release version bumps, destructive or irreversible operations, credential use, pushing to remotes. Those wait for morning.
+
+**Per-task pipeline (one task at a time, WIP = 1).**
+
+1. Take the next task from the sprint queue (sprint doc or Kanban order) and move it to `in-progress`.
+2. Brain plan under the same `task_id` with a Seat Check; the UI/UX Designer seat is mandatory for anything user-facing.
+3. Review the plan yourself: accept it, or send edits back. Never forward a plan you have not read.
+4. Implement from the plan; run the tests it names; record command, expected, actual, and exit code.
+5. Brain QA with the diff. Fix what reproduces; dispute the rest with file:line evidence.
+6. Brain Code Reviewer with the diff. Apply change requests; otherwise accept on his behalf.
+7. Close per protocol, then start the next task. Never batch two tasks into one commit.
+
+**Evidence rules for an unattended run.**
+
+- A verdict you cannot cite is not a verdict: every rejection, approval, and self-decision carries file:line, or a command plus its exit code.
+- A rejection that contradicts the working tree is a dispute, not a fix: re-read the file, cite the lines, and record the dispute. Three rejections on the same evidence switch to the dispute path — never loop a fourth time.
+- Prove a regression test has teeth by reintroducing the bug once and watching the test fail, then restoring the fix.
+- Record every adaptation (a substituted command, a skipped tool, a replaced approach) in the task file, with the reason.
+
+**Survival across compaction.** Write the mode, the queue, the active task id, and the next action into project memory before context gets tight, and re-read that memory after any compaction. Durable state lives in the task file and project memory, never only in the chat.
+
+**Morning report — always the same shape.**
+
+1. One-line verdict per task, with commit hashes.
+2. What shipped, grouped, with the tests that prove it.
+3. What needs the Manager: a short numbered list of checks only he can perform, credentials, or production parameters.
+4. Flags: anything left in a non-production state (staging values, temporary overrides, untracked files).
+5. Honest notes: disputes, extra commits, workarounds, and anything you could not verify.
+</night_mode>
diff --git a/prompts/manifest.txt b/prompts/manifest.txt
index e63ad5c..c9fd495 100644
--- a/prompts/manifest.txt
+++ b/prompts/manifest.txt
@@ -19,3 +19,4 @@
 20-communication_examples.md
 21-self_improvement_protocol.md
 22-compaction_protocol.md
+23-night_mode.md
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 3c5f728..9bdf219 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -11,6 +11,7 @@ description: Enforces decentralized task management, UI/UX design strictness, an
 - You are STRICTLY FORBIDDEN from traversing outside `[PROJECT_ROOT]` or referencing parent directories. Use generic placeholders like `[PROJECT_ROOT]/AGENTS.md`.
 - **Absent-File Policy**: If optional architectural files (`DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`) do NOT exist in `[PROJECT_ROOT]`, SKIP them gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. DO NOT scaffold or create them unless explicitly instructed.
 - **OpenCode Isolation**: You are STRICTLY FORBIDDEN from creating `.opencode/` scaffolding inside third-party projects. Only inspect `.opencode/` if `[PROJECT_ROOT]/.opencode/` ALREADY exists OR if the user passes `with_opencode: true`.
+- **Session-Compact Config Is Agent Tooling**: `[PROJECT_ROOT]/.opencode/smart-compact.jsonc` is deliberate, agent-managed configuration for the context-compaction plugin. IGNORE it entirely: never flag it as OpenCode scaffolding, never patch or delete it, and never demand it be added to `.gitignore`. Report it only if the Manager explicitly asks about compaction settings.
 
 ## Target Audit Criteria
 
@@ -37,7 +38,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Execution Log & Reasoning` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
 - **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
-- **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
+- **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. Deliberate agent config (`[PROJECT_ROOT]/.opencode/smart-compact.jsonc`) is NOT runtime state and MUST NOT be gitignored. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
 
 - **Living Folder Docs Sibling Inspection**: AGENTS.md MUST instruct agents to inspect sibling README.md and DECISIONS.md before editing code in any component or vertical slice directory, and update them when domain contracts or architectural decisions change.
 
diff --git a/system-prompt.md b/system-prompt.md
index 2b8e96a..0d52a7f 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.58.2</system_version>
+<system_version>9.59.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -471,6 +471,8 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 
 9. **Step 9: Next Task Transition (Sprint Strategist)**
    - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
+
+**Night mode override.** When the Manager hands over the night ("night mode", "100% autopilot until morning"), `<night_mode>` governs: the Step 6 QA gate, the Step 7 review gate, and the Step 8 closure approval are pre-authorized and played by the Hands, and the question tool is not used until he returns. Every other step in this pipeline is unchanged.
 </execution_workflow>
 
 <brainstorming_protocol>
@@ -742,3 +744,42 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 
 **Rule.** The agent cannot run the `/magic-*` slash commands itself, but it CAN call `compact_context` directly — prefer that under pressure, and state one line about it. Either way, continue from the task file, never from a lossy summary. Durable state lives in the task file and project memory, so any compaction stays recoverable.
 </compaction_protocol>
+
+<night_mode>
+**Trigger.** The Manager hands over the night: "night mode", "on autopilot do X", "I'm going to sleep, do everything", "100% autopilot until morning". From that word the mode is LOCKED until he returns or says "manual" / "stop".
+
+**The one rule that defines night mode: do not ask.** No `question` tool, no approval waits, no "should I?" messages. Decide on the Manager's behalf and log every self-decision in the task file as `D1, D2, …` with a one-line reason. He wakes up to decisions plus evidence, never to a queue of questions.
+
+**Authority granted for the night — and nothing more.**
+
+- Plan approval, QA verdicts, and review acceptance are played by the Hands.
+- Task closure is pre-authorized: accept on his behalf and close per protocol, including staging and the closure commit.
+- NOT granted: production deploys, release version bumps, destructive or irreversible operations, credential use, pushing to remotes. Those wait for morning.
+
+**Per-task pipeline (one task at a time, WIP = 1).**
+
+1. Take the next task from the sprint queue (sprint doc or Kanban order) and move it to `in-progress`.
+2. Brain plan under the same `task_id` with a Seat Check; the UI/UX Designer seat is mandatory for anything user-facing.
+3. Review the plan yourself: accept it, or send edits back. Never forward a plan you have not read.
+4. Implement from the plan; run the tests it names; record command, expected, actual, and exit code.
+5. Brain QA with the diff. Fix what reproduces; dispute the rest with file:line evidence.
+6. Brain Code Reviewer with the diff. Apply change requests; otherwise accept on his behalf.
+7. Close per protocol, then start the next task. Never batch two tasks into one commit.
+
+**Evidence rules for an unattended run.**
+
+- A verdict you cannot cite is not a verdict: every rejection, approval, and self-decision carries file:line, or a command plus its exit code.
+- A rejection that contradicts the working tree is a dispute, not a fix: re-read the file, cite the lines, and record the dispute. Three rejections on the same evidence switch to the dispute path — never loop a fourth time.
+- Prove a regression test has teeth by reintroducing the bug once and watching the test fail, then restoring the fix.
+- Record every adaptation (a substituted command, a skipped tool, a replaced approach) in the task file, with the reason.
+
+**Survival across compaction.** Write the mode, the queue, the active task id, and the next action into project memory before context gets tight, and re-read that memory after any compaction. Durable state lives in the task file and project memory, never only in the chat.
+
+**Morning report — always the same shape.**
+
+1. One-line verdict per task, with commit hashes.
+2. What shipped, grouped, with the tests that prove it.
+3. What needs the Manager: a short numbered list of checks only he can perform, credentials, or production parameters.
+4. Flags: anything left in a non-production state (staging values, temporary overrides, untracked files).
+5. Honest notes: disputes, extra commits, workarounds, and anything you could not verify.
+</night_mode>
```
<!-- END_GIT_DIFF -->
