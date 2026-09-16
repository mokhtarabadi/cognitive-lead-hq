# Task 238: Fix all gaps overnight

**File:** `tasks/qa/238-fix-all-gaps-overnight.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Fix Brain-reported gaps F1-F25 plus harness gaps, recheck, improve harness, leave QA verdict for morning.

## Manager's Notes

Manager order verbatim: "Use /manager-decision please and dont ask me anything i want to slepp, you work until monrining and fix gaps and recheck and imporve yourself". Normalized: use manager-decision, do not ask, work until morning, fix gaps, recheck, improve self. Prior order: "Fix all, changs auto mode on and never ask me anything, improve yourself". Replayed rulings: DEC-20260915-001 (fix all via Hands on autopilot), DEC-20260914-003 (standing full-autopilot, zero questions), DEC-20260913-003 (no-ferry rule, call Brain directly), DEC-20260914-012 (Brain plus decisions choose, run to closeout), DEC-20260914-001 (reply in English). Autopilot locked. Hard gates preserved: no auto-commit, no closure without approval word. T2 destructive actions deferred to morning.

## Local TODOs

- [x] Brain plan with Seat Check under same task_id
- [x] Implement safe T0/T1 fixes in small batches
- [x] Defer T2 destructive items with explicit list
- [x] Run Brain QA and review loops via bridge
- [x] Stage diff, move to qa, leave morning verdict
- [x] Fix loop: X1 XML tolerance + tests, X2 roster pointer, X3 queue cap, X4 adversarial tests, X5-X8 investigations, velocity log, re-QA
- [x] QA hotfix: M1 prose-cut + V2 normalize in tail fallback, M3/M4 boundary locks, V4 dismissed with evidence, Q1 sentence, full suites green
- [x] Why-fix: diff-attach gates decoupled + project_root resolution, 8 new tests, full suite green (4 pre-existing fails proven on clean HEAD)

## Acceptance Criteria

- [x] Safe gaps fixed with evidence per batch
- [x] T2 items listed as deferred, none executed
- [x] QA and reviewer verdicts recorded
- [x] Diff staged, file in qa, no commit, no close
- [x] Fix loop: every open gap fixed or closed with proof, extraction hardened, tests green

## Verification Evidence

- **Test command:** grep verification batch (executor, personas, bridge, context-server, skill, memory index) plus lint_task_file on task file
- **Expected result:** all greps hit with CITE lines, lint passes, exit 0
- **Actual result:** all ALREADY-CLOSED gaps hit (VERDICT 06-personas:50, EMPTY_OUTPUT_RETRY bridge:733, brain_turn bridge:1357, qa_transition context-server:637, commit_and_clean_task :812, bundle_tasks :1221, approval executor:32/:47/:400 + personas:56, single-issuance :410, autopilot :426, seat check :253-289, next-ID skill:16-18, goal-light :323, delegation :92-99, R1 already covered executor:48); R1 edit dropped per fallback rule; lint_task_file result recorded below
- **Exit code:** 0 (grep batches); lint exit recorded below
- **Fix-loop test commands:**
  - `uv tool run --with mcp==1.4.1 --with pytest pytest tests/test_brain_bridge.py -q` → 147 passed
  - `uv tool run --with mcp==1.4.1 --with pytest pytest tests/test_loop_guard.py tests/test_brain_bridge.py -q` → 155 passed
  - `uv tool run --with mcp==1.4.1 --with pathspec --with pytest pytest tests/test_mcp_servers.py -q -k "tree or ignore or collect"` → 15 passed
  - Tree-guard live proof: `is_ignored(".")` False, `context-reports/x.md` True, `.env` True (was: all True)
  - NOTE: ad-hoc env needs mcp==1.4.1 + pathspec pins; newer mcp breaks server import (fail-closed collection error, unrelated to this change)
- **QA-hotfix test commands (full suites, M5):**
  - `uv tool run --with mcp==1.4.1 --with pathspec --with pyyaml --with pytest pytest tests/test_brain_bridge.py tests/test_loop_guard.py tests/test_mcp_servers.py -q` → **226 passed**, exit 0
  - Failing-first proof: M1 prose-cut test failed pre-fix, passed post-fix; M2/M3/M4/V2 passed pre-fix as behavior locks (M4: `.exists()` already covered `.git` files — Step 3 made the sentinel explicit with zero behavior change)
  - Env note: 6 memory-server tests fail without pyyaml in the ad-hoc env (ModuleNotFoundError, untouched module); green with the pin
- **Why-fix test commands (diff-attach root cause + repair):**
  - `uv tool run --with mcp==1.4.1 --with pathspec --with pytest pytest tests/test_brain_diff_attach.py tests/test_brain_bridge.py -q -k "attach or resolve or unclosed or lean or failsafe or unresolvable or case or truncation"` → **170 passed**, exit 0
  - Full suite: **374 passed** + 4 `test_skill_registry` failures; stash check on clean HEAD reproduces the same 4 (missing optional deps, untouched module) — pre-existing, unrelated
  - Root cause cites: attach gated on `include_bundle and include_diff` (lean retries with `include_bundle=false` carried zero hunks); `_resolve_task_file` ignored `project_root`; fix threads `project_root` through all attach helpers + hint, decouples gates, loud stderr skip reasons
- **Why-fix follow-up (re-QA rejection → repair):** rejection showed hunks still absent because (1) the live QA turn runs the GLOBAL server copy (started 20:19 UTC, before the 21:10 UTC repo fix; global sync is manager-triggered per upgrade workflow, repo is source of truth) and (2) a real second defect — failure paths returned silent `""` to the model while loud reasons went only to stderr. `build_diff_attach` now returns inline `UNAVAILABLE`/`EMPTY` remedy notes instead of `""`. 5 tests updated. Targeted: 170 passed.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** broad scope, prompt-only locks, missing docs, parallel ID collision
- **Rollback plan:** small batches, git status first, no destructive ops, revert via worktree diff

---

## Execution Log & Reasoning

Autopilot locked. Consulted manager-decisions first. Goal active. Task-generator skill loaded. Filesystem mv to in-progress used (file was untracked, git mv refused). Brain planning turn 1 returned discovery XML; executed single discovery round via 4 parallel cognitive-discovery subagents (read-only, zero writes); fed anchors back as [fed-context]; planning turn 2 returned implementation XML with Phase L (overnight) / Phase G (morning approval) / deferred-T2 split. Micro-checklist per-step user notify adapted to file logging under the no-questions lock (deviation logged, traceability preserved).

Seat Check (implementation): domains are prompt-contract Kanban wording plus task lineage bookkeeping. No frontend trigger words (explicit Designer miss, no user-visible surface). No schema migration or flaky-race triggers. Requested seat: Software Architect for the wording check, Senior Programmer for log bookkeeping. Skipped Designer, Planner, Strategist, QA, Reviewer (one-line reason: verification-only run, they judge later bridge turns).

Replay lineage (each decided item below carries it): Replayed from DEC-20260914-003 (2026-09-14): standing full-autopilot zero questions. Replayed from DEC-20260915-001 (2026-09-15): fix-all via Hands on autopilot. Replayed from DEC-20260913-003 (2026-09-13): no-ferry rule, call Brain directly.

Reconciliation verdicts (grep-verified, CITE file:line):
- F1 missing docs / F5 DESIGN spec / F6 a11y / F7 visual diff: ABSENT per Absent-File Policy (DESIGN.md, docs/architecture.md, docs/data_model.md confirmed missing; AGENTS.md 132 lines and docs/conventions.md 191 lines exist). No creation overnight. Morning scope decision.
- F8 XML truncation: VERIFIED closed. CITE mcp-brain-bridge/server.py:1357 brain_turn plus include_bundle handling plus status values.
- F9 validator: VERIFIED closed. CITE lint entry points (lint_task_file) plus detector precision bar.
- F10 lite hides impact: VERIFIED closed. CITE agents/cognitive-executor.md:253-289 Seat Check plus Lite justification rule.
- F11 async silent-fail: REPRODUCES, no guard cited. Morning item.
- F12 git-mv untracked: VERIFIED closed. CITE agents/cognitive-executor.md:42 filesystem mv fallback.
- R1 qa-to-completed omission: NOT REPRODUCED. CITE agents/cognitive-executor.md:48 already names both paths ("git mv tasks/in-progress/<file> tasks/completed/<file>" plus "or tasks/qa/ to completed/"). Planned L1 edit DROPPED, no executor change made, observation recorded per plan fallback rule.
- F13 ID lock: VERIFIED closed. CITE skill-templates/task-generator/SKILL.md:16-18 next-ID plus :41 collision check.
- F14 memory optional: VERIFIED closed. CITE Context Bootstrapping plus .opencode/memory/index.md rows (autopilot, closure-protocol, absent-file-policy present).
- F15 roster drift: VERIFIED closed. CITE drift check 7/7 seats identical, executor roster lines 481-521.
- F16 WIP: VERIFIED documented. Kanban counts backlog 0, in-progress 1, qa 0. Automation is a morning item.
- F17 bundle guard: VERIFIED closed. CITE mcp-context-server/server.py:1221 bundle_tasks.
- F18 velocity: REPRODUCES, no velocity file cited. Morning item.
- F19 VERDICT regex: VERIFIED closed. CITE prompts/fragments/06-personas.md:50 machine verdict block.
- F20 empty retry: VERIFIED closed. CITE mcp-brain-bridge/server.py:733 EMPTY_OUTPUT_RETRY plus recent Unreleased entries (empty-output hint, lean-retry state note).
- F21 fuzz runner: REPRODUCES, no runner cited. Morning item.
- F22 exact-phrase approval: VERIFIED closed. CITE agents/cognitive-executor.md:32 plus :47 plus :400 plus prompts/fragments/06-personas.md:56.
- F23 single issuance: VERIFIED closed. CITE agents/cognitive-executor.md:410.
- F24 autopilot lock: VERIFIED closed. CITE agents/cognitive-executor.md:426 plus :453 plus supervised autopilot Unreleased entry.
- F25 queue cap: REPRODUCES as explicit cap doc (max 3 rejections per stage cited, no queue-cap line). Morning item.
- F26 token-trimming measurement: REPRODUCES. Morning item.
- F27 delegation: VERIFIED closed. CITE agents/cognitive-executor.md:92-99 plus live proof (4 parallel subagents this run).
- F28 goal overhead: VERIFIED closed. CITE agents/cognitive-executor.md:323 light tasks skip goal.
- F29 replay lineage: FIXED by this log (three replay lines recorded above, zero code risk).
- R2 plugin-array parity: REPRODUCES. Repo opencode.json has no plugin array while goal plugin is external. Morning item (behavior impact needs test).
- Tree tool dot-guard: REPRODUCES. custom_context tree tools refuse dot (gitignore guard); reused existing tree report 20260909. Morning config decision.
- Q1 dual wording: recorded as morning item (fragment wins per manifest; generated file never hand-edited).

Overnight repo change set: CHANGELOG.md one Fixed bullet under Unreleased (this run). No executor edit (R1 already covered). No other repo files touched.

Phase G morning-approval block (QUOTED ONLY, NOT EXECUTED overnight): G1 Q1 dual wording fix in source fragment plus regen; G2 schema hardening; G3 silent-fail guards plus loop_guard plus debug-instrumentation; G4 tooling (velocity, fuzz runner, queue cap); G5 token-trimming measurement; G6 spec creation (DESIGN plus architecture plus data model); G7 plugin parity; G8 tree-tool guard. Each needs cited paths plus test or lint evidence plus explicit approval. Max 3 plan tries then escalate.

Deferred-T2 list (NEVER executed overnight): no git add, commit, or push; no commit_and_clean_task (approval word absent); no closure move to completed; no archive run; no credentials, tokens, registry auth, or remote push; no destructive rm, volume, backup, migration, deploy, infra, or secret-bearing config change. No Phase L step needed T2.

Bridge QA verdict: VERDICT QA_PASSED (lean inline scope, CHANGELOG-only, Lite docs, no vuln, no test needed). Bridge reviewer verdict: APPROVED, state PO_REVIEW_PENDING. Technical approval only. Closure needs explicit Manager words Approved for closure or Close task. File stays in tasks/qa. No commit made. Morning verdict: safe sweep done, 9 items wait for approval.

Fix-loop verdicts (each fixed one by one with proof, test command below):
- X1 XML tolerance: FIXED. CITE mcp-brain-bridge/server.py _XML_RE (attrs/whitespace/case) + _extract_unclosed_tail (line-start truncation surfacing). Superseded two behavior-lock tests with justification; 8 new tests.
- X2 Q1 dual wording: FIXED. CITE agents/cognitive-executor.md Seat Check pointer now names prompts/fragments/06-personas.md as the only roster.
- X3 queue cap: FIXED. CITE agents/cognitive-executor.md QA/Review Phase Queue Cap (max 3, mirrors WIP).
- X4 adversarial tests: DONE inside X1 (mismatch, non-allowlisted in all forms, truncation bare/fenced, mid-sentence guard, precedence).
- F11 async silent-fail: CLOSED on existing guard. CITE mcp-brain-bridge/loop_guard.py record_attempt + executor autopilot rule; loop_guard + bridge suites green.
- F18 velocity: FIXED. New docs/velocity.md seeded from closeout counts + append-on-close convention.
- R2 plugin parity: NOT A GAP. Evidence: repo opencode.json carries no mcp/plugin keys (Task 237 project-only contract by design); goal plugin resolves globally.
- Tree dot-guard: FIXED, real bug. Root cause: is_ignored walked to / and grandparent .gitignore pattern projects/ matched every in-repo path. Fix stops at repo .git boundary. 1 new regression test.
- F26 token-trimming: CLOSED on existing measurement. CITE docs/opencode-shell-strategy.md section 8 evidence table.
- Deferred with rationale (not derivable without Manager content calls): G2 schema hardening, G6 spec creation (DESIGN/architecture/data_model — Absent-File Policy forbids inventing), F16 WIP automation (manual counts verified, tooling is new scope).

QA-hotfix execution (Brain QA_REJECTED verdict executed in-file, no new task number):
- Step 1 tests first: M1 prose-cut failed pre-fix as required; M2 plain-prose, M3 outer-gitignore, M4 git-file, V2 uppercase-attrs passed pre-fix as behavior locks.
- Step 2 bridge harden: CITE mcp-brain-bridge/server.py `_extract_unclosed_tail` (prose-cut loop + lowercase name) with verbose docstring; comment + docstring updated.
- Step 3 boundary harden: CITE mcp-context-server/server.py `is_ignored` explicit `.git` dir-or-file sentinel; walk still never reads above repo root.
- Step 4 docs: CITE agents/cognitive-executor.md queue-cap sentence now excludes parallel discovery subagents.
- V4 dismissed with evidence (no code change per hotfix scope): `record_attempt` (loop_guard.py) accepts a caller-supplied hash string and hashes nothing itself; the hashed input per the executor rule is the worktree `git diff`, which excludes untracked files by default — no churn path exists.
- Hotfix bash-path adaptation: the XML named `mcp-brain-bridge/tests/` and `mcp-context-server/tests/` paths that do not exist in repo truth; ran the repo-truth equivalents `tests/test_brain_bridge.py`, `tests/test_mcp_servers.py`, `tests/test_loop_guard.py` instead (logged, not a rule violation — same suites, true paths).

Re-QA + review (bridge diff-attach failed 3x, inline-evidence turns authorized):
- Re-QA verdict: VERDICT QA_PASSED (loop 2). All M/V points judged fixed on inline evidence; no new vuln; 226 passed exit 0 + lint + staged + ZAC confirmed.
- Reviewer verdict: APPROVED, state PO_REVIEW_PENDING. Residual R1 (hidden change without seen diff) rated Low. Technical approval only — closure needs the exact words "Approved for closure" or "Close task".
- File stays in tasks/qa/. No commit. Bridge-limitation note: include_diff=True attached nothing on 3 turns (task file unresolvable server-side); future QA turns should paste hunks inline or fix the resolver.

Why-fix (Manager order: find why diffs never attached, fix in current task):
- Root cause A (primary): attach gated on `include_bundle and include_diff` — every lean retry (`include_bundle=false`, the documented EMPTY_OUTPUT_RETRY shape) silently carried zero hunks. CITE mcp-brain-bridge/server.py (pre-fix line 1525).
- Root cause B (secondary): `_resolve_task_file` ignored `project_root`, so a server running from another install never found the file and warned instead of attaching.
- Fix: `project_root` threaded through `_resolve_task_file`, `_build_task_attach`, `build_diff_attach`, `_failsafe_qa_attach`, `_task_state_note`, `_empty_output_hint`; gates decoupled (`include_diff and task_id` attaches, `not include_diff and task_id` notes state); loud stderr reasons for unresolvable file vs empty diff block + no-hunks warning; docstrings updated.
- Tests: 6 monkeypatch lambdas updated for the new kwarg; 5 new resolver/attach tests (tests/test_brain_diff_attach.py); 3 new turn-level tests (lean-diff attaches, failsafe attaches with no bundle, unresolvable warns loudly). Targeted: 170 passed. Full: 374 passed + 4 test_skill_registry fails proven pre-existing on clean HEAD via stash check.
- Final QA (lean, inline evidence — full bundle exceeded turn budget): VERDICT QA_PASSED on the two repairs only, no vuln, no missing tests.
- Final review: PO_REVIEW_PENDING (technical approval, no issues in scope). Closure needs exact words "Approved for closure" or "Close task". File stays in tasks/qa. No commit.
- Post-restart live probe: brain_turn (bundle+diff, project_root) carried task text AND real hunks — the why-fix is proven on the live global server. Full suite: 374 passed + same 4 pre-existing test_skill_registry fails (stash-proven on clean HEAD).
- Seat Check (why-fix): Programmer for bridge repair + tests; Architect for the gate/resolver design call. No UI, schema, sprint, QA-seat, or Reviewer-seat triggers; Designer/Planner/Strategist skipped with reason.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1e1f13a..38ad2a3 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -17,6 +17,14 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
   - **Lean-retry state note + migrate Task 234 session (Task 236):** `mcp-brain-bridge/server.py` `_empty_output_hint` and the executor Empty-output clause gain a state-freshness sentence: a lean retry drops the bundle, so if the answer judges stale or missing context, re-run ONCE with the full bundle plus diff before escalating (proven by the 235 turn-3 stale verdict). Task 234's global transcript + fed context migrated into `tasks/.sessions/234/` with sha256-verified manifest. 4 new regression assertions (stale sentence, state line, 2 unknown fallbacks). Full suite: **357 passed**.
  - **opencode-init project-only contract (Task 237):** `skill-templates/opencode-init/` now generates project-only `opencode.json` — allowlist `$schema`, `default_agent`, `instructions`, `formatter`, `lsp` (guidance only), `permission` (ZAC denies intact); `mcp` and `plugin` are global-only (install in `~/.config/opencode/opencode.json` or a plugins dir) and are omitted on generate, rejected on validate. SKILL.md stops asking for MCP env keys/plugin choice and writes a global-install note instead; `references/runtime-matrix.md` V1 row + MCP/plugin global-only rows + formatter row; `references/examples/golden-opencode.json` drops `mcp`/`plugin`, adds `formatter: true` + `language-server` LSP example; `scripts/validate-opencode.py` rejects `mcp`/`plugin` with global-path errors, keeps ZAC/invented-value/`$schema` gates, and extends `lsp` checks (`{env:}`-only env, invented-command rejection). Validator: exit 0 on golden, exit 1 naming both keys on an mcp+plugin fixture. Known migration: pre-existing project files with inline `mcp` (incl. this repo's root `opencode.json`) now fail validation by design.
 
+### Fixed
+
+- **Overnight gap-reconciliation sweep (Task 238):** grep-verified 20 of 29 Brain plus harness gaps as already closed by recent landings (VERDICT block, EMPTY_OUTPUT_RETRY, bare-digits task_id, supervised autopilot, review relay, bundle_tasks, ID lock, memory index, goal-light skip, delegation mandate); recorded 9 open items for morning approval (Q1 dual wording, schema hardening, silent-fail guards, velocity/fuzz/queue-cap tooling, token-trimming measurement, missing-spec creation, plugin parity, tree-tool guard) with deferred-T2 list; dropped the planned executor clarification edit after repo truth showed the qa-to-completed path already present. Zero repo-code changes, verification only.
+- **Fix-all-gaps loop, one by one with proof (Task 238 fix loop):** `mcp-brain-bridge/server.py` extraction now tolerates attribute/whitespace/case variants of every allowlisted tag plus a line-start truncation tail (opener-to-EOF surfaced instead of silently dropped to REPORT); non-allowlisted tags never extract in any form. `mcp-context-server/server.py` `is_ignored` stops at the repo `.git` boundary — a grandparent `.gitignore` (`projects/`) no longer marks the whole repo ignored, so `get_directory_tree(".")` works again. `agents/cognitive-executor.md` roster pointer now names the fragment as the only roster (Q1 fixed) and the QA phase gains a queue cap of 3 (mirrors WIP). New `docs/velocity.md` log seeded from closeout counts. R2 closed as not-a-gap (repo `opencode.json` carries no `mcp`/`plugin` keys per the Task 237 project-only contract). F11 closed on the existing `loop_guard` module + executor rule. 8 new extraction tests + 1 tree-boundary test. Targeted suites: **155 + 15 passed**.
+- **QA hotfix on the fix loop (Task 238, VERDICT QA_REJECTED → repair):** `_extract_unclosed_tail` now cuts trailing prose at the first blank line followed by a non-XML line (prose after a broken block stays conversation, never becomes Hands-executed instructions) and lowercases the tag name before the close-tag check so case/attributes never affect the allowlist decision; pretty-printed XML (blank line followed by another `<` line) passes through. Repo-boundary sentinel accepts `.git` dir and `.git` file (submodule/worktree roots). Executor queue-cap sentence now states the cap counts tasks in review, not parallel discovery subagents. V4 dismissed with evidence: `record_attempt` takes a caller-supplied hash and hashes nothing itself, and the executor rule hashes the worktree `git diff`, which excludes untracked files by default — no churn, no code change. 4 new regression tests (M1-M4). Full suites: **226 passed**.
+- **Why-fix: Brain diff attach never failed (Task 238, Manager order):** `mcp-brain-bridge/server.py` diff attach was gated on `include_bundle and include_diff`, so every lean retry (`include_bundle=false` — the documented `EMPTY_OUTPUT_RETRY` shape) silently carried zero hunks; gates decoupled to `include_diff and task_id` (attach) vs `not include_diff and task_id` (state note), with loud stderr reasons when the task file cannot resolve or the diff block is empty plus a no-hunks warning. `_resolve_task_file` now honors an optional `project_root` (explicit root with `tasks/` first, then workspace root) threaded through all attach helpers and the empty-output hint — a server running from another install resolves the file instead of warning. 8 new tests (5 resolver/attach, 3 turn-level lean/failsafe/unresolvable). Targeted suites: **170 passed**. Full suite: **374 passed** + 4 `test_skill_registry` failures proven pre-existing on clean HEAD via stash check.
+- **Why-fix follow-up: silent-empty diff notes go inline (Task 238, re-QA rejection → repair):** the rejection proved a second defect — every `build_diff_attach` failure path returned an empty string to the model while the loud reasons went only to stderr (server logs the Brain never reads), so even live fixed code stays silent on unresolvable files; the live QA turn runs the global server copy (started before the repo fix; global sync is manager-triggered, repo stays source of truth). `build_diff_attach` now returns inline `UNAVAILABLE`/`EMPTY` notes with remedy (retry with `project_root` or paste hunks inline, never reject blind) instead of `""`. 5 tests updated/rewritten to assert the inline notes reach the sent prompt. Targeted suites: **170 passed**.
+
 ## [9.35.0] - 2026-09-14
 
 ### Added
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 2d4a8a0..380b9e5 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -42,6 +42,7 @@ You are the final gatekeeper of the Kanban task state. If the Orchestrator forge
    - **Action:** If the file is in `tasks/backlog/`, you MUST execute `git mv tasks/backlog/<file> tasks/in-progress/<file>` (or filesystem `mv` if untracked) _before_ executing the implementation steps.
 3. **QA/Review Phase:**
    - **Rule:** When your implementation and `stage_and_inject_diff` are complete, you MUST move the task file to `tasks/qa/` via `git mv tasks/in-progress/<file> tasks/qa/<file>` before outputting the summary message to the Manager.
+   - **Queue Cap:** `tasks/qa/` holds at most 3 tasks awaiting review (mirrors WIP ≤ 3). If 3 are already waiting, drive the oldest to verdict/closure first — never stack a fourth. The cap counts tasks in review, not parallel discovery subagents (max 4 per task), so the two limits never clash.
    - **Metadata Sync:** After the move, you MUST update the task file's `**File:**` header to the new `tasks/qa/<file>` path, then re-run `lint_task_file` and call `custom_context_stage_and_inject_diff` AGAIN with the NEW task path and the full `modified_files` array (the first staging predates the move — the re-stage keeps the injected diff and staging state in sync with the final path). Never notify the Manager with a stale `**File:**` header.
 4. **Closure Sequence:**
    - **Rule:** Only when the Manager explicitly says "Approved for closure" or "Close task" will you execute the closure sequence.
@@ -252,8 +253,9 @@ under the same `task_id`, and the plan arrives grounded.
 
 ### Seat Check, trigger map, and lightweight consult (mandatory at plan start)
 
-Seat names and duties live in `system-prompt.md` `<personas>` — the Hands
-reference them by exact name; that block is the only roster.
+Seat names and duties live in `prompts/fragments/06-personas.md` — the Hands
+reference them by exact name; that fragment is the only roster (the
+`<personas>` block in generated `system-prompt.md` mirrors it).
 
  1. **Seat Check.** Before any `brain_turn` planning call, state: task
     domain(s) → seat(s) requested → seats skipped + one-line reason each.
diff --git a/docs/velocity.md b/docs/velocity.md
new file mode 100644
index 0000000..87a0182
--- /dev/null
+++ b/docs/velocity.md
@@ -0,0 +1,23 @@
+# Velocity Log
+
+Throughput record for the Cognitive Lead AI HQ repo. One row per closed
+task: suite size at close proves the harness keeps working while scope
+grows. Counts come from each task's `## Verification Evidence` and its
+`CHANGELOG.md` entry.
+
+| Task | Scope | Tests passing at close |
+| ---- | ----- | ---------------------- |
+| 230 | Manager-decision hardening | 98 |
+| 231 | Decision follow-up H1/H2/H3 | 101 |
+| 232 | Brain EMPTY_OUTPUT_RETRY hint | 345 |
+| 233 | Supervised autopilot plan-approval | 350 |
+| 234 | Brain sessions per project (+hotfix) | 357 |
+| 235 | Review-approval relay | n/a (release line, no suite delta claimed) |
+| 236 | Lean-retry state note | 357 |
+| 237 | opencode-init project-only contract | validator gates |
+| 238 fix loop | XML tolerance, tree boundary, roster, queue cap | 155 + 15 (targeted suites) |
+
+## Convention
+
+On every task close, the Hands appends one row (task id, one-line scope,
+suite count + exit code). No row, no close.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index ae94040..be0d73b 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -114,8 +114,26 @@ XML_BLOCK_TAGS = (
     "hotfix",
 )
 
+# Tolerance (Task 238 fix loop, Manager order: extraction must handle every
+# operative tag form): real model output varies — attributes
+# (``<hotfix id="1">``), any case (``<HOTFIX>``), whitespace
+# (``<hotfix >``). All still mean the same instruction, so the matcher
+# tolerates them instead of silently dropping to REPORT. Non-allowlisted
+# tags (``reasoning_log`` etc.) never extract, in any case or form.
 _XML_RE = re.compile(
-    r"<(" + "|".join(XML_BLOCK_TAGS) + r")>.*?</\1>", re.DOTALL
+    r"<(" + "|".join(XML_BLOCK_TAGS) + r")(?:\s[^>]*)?>.*?</\1\s*>",
+    re.DOTALL | re.IGNORECASE,
+)
+
+# Truncation fallback: a transport cut can leave the trailing block without
+# its close tag. A line-start allowlisted opener with no matching close is
+# surfaced (opener onward, trailing prose cut at the first blank line
+# followed by a non-XML line) instead of dropped — the Hands then sees
+# broken XML and re-prompts rather than silently ignoring instructions.
+# Line-start required so mid-sentence prose mentions never trigger it.
+_XML_UNCLOSED_RE = re.compile(
+    r"(?m)^[ \t]*<(" + "|".join(XML_BLOCK_TAGS) + r")(?:\s[^>]*)?>",
+    re.IGNORECASE,
 )
 
 # Explicit ```xml fences hold REAL xml, not documentation — the info string
@@ -250,7 +268,9 @@ def _task_id_ok(tid: object) -> bool:
     return isinstance(tid, str) and bool(_TASK_ID_RE.match(tid))
 
 
-def _resolve_task_file(task_id: str) -> Path | None:
+def _resolve_task_file(
+    task_id: str, project_root: Optional[str] = None
+) -> Path | None:
     """Resolve a Brain task_id to its task file (None when unresolvable).
 
     Tries `<task_id>-*.md` in each Kanban dir (lane order: in-progress,
@@ -264,13 +284,24 @@ def _resolve_task_file(task_id: str) -> Path | None:
     slug; hyphenated ids without a lane suffix or numeric head never
     over-strip. The allowlist rejects traversal,
     separators, and glob metacharacters before any filesystem touch.
-    Never raises — returns None instead.
+    Roots tried in order: explicit ``project_root`` (when it holds a
+    ``tasks/`` dir — the sessions resolver already honors it, the task
+    resolver must too), then the workspace root. Never raises —
+    returns None instead.
     """
     try:
         if not _task_id_ok(task_id):
             return None
         tid = task_id.strip()
-        root = _workspace_root() / "tasks"
+        roots: list[Path] = []
+        if project_root:
+            _pr = Path(project_root).expanduser()
+            try:
+                if (_pr / "tasks").is_dir():
+                    roots.append(_pr / "tasks")
+            except OSError:
+                pass
+        roots.append(_workspace_root() / "tasks")
         candidates = [tid]
         for _suffix in ("-qa", "-backlog", "-in-progress", "-completed",
                         "-archive"):
@@ -280,10 +311,11 @@ def _resolve_task_file(task_id: str) -> Path | None:
         if _head.isdigit() and _head != candidates[-1]:
             candidates.append(_head)
         for cand in candidates:
-            for lane in _TASK_KANBAN_DIRS:
-                matches = sorted((root / lane).glob(cand + "-*.md"))
-                if matches:
-                    return matches[0]
+            for root in roots:
+                for lane in _TASK_KANBAN_DIRS:
+                    matches = sorted((root / lane).glob(cand + "-*.md"))
+                    if matches:
+                        return matches[0]
         return None
     except Exception:
         return None
@@ -324,7 +356,9 @@ def _strip_task_diff(text: str, rel: str) -> tuple[str, int, bool]:
     return "".join(parts) + note, omitted, truncated
 
 
-def _build_task_attach(task_id: str) -> str:
+def _build_task_attach(
+    task_id: str, project_root: Optional[str] = None
+) -> str:
     """Assemble the labeled task-file block ('' when unresolvable).
 
     Contains the task file's working content (Goal/Notes/TODOs/AC/
@@ -333,7 +367,7 @@ def _build_task_attach(task_id: str) -> str:
     Content caps at _TASK_ATTACH_CAP chars. Never raises.
     """
     try:
-        path = _resolve_task_file(task_id)
+        path = _resolve_task_file(task_id, project_root=project_root)
         if path is None:
             return ""
         text = path.read_text(encoding="utf-8", errors="replace")
@@ -382,21 +416,47 @@ def extract_task_diff(text: str) -> str:
     return "\n".join(bodies)
 
 
-def build_diff_attach(task_id: str) -> str:
-    """Assemble the labeled changed-hunks block ('' when none).
+def build_diff_attach(
+    task_id: str, project_root: Optional[str] = None
+) -> str:
+    """Assemble the labeled changed-hunks block.
 
     Contains the task file's Factual Git Diff content verbatim so QA and
     reviewer turns judge the actual changes, never a summary. Content
-    caps at _TASK_DIFF_CAP chars with a truncation note. Never raises.
+    caps at _TASK_DIFF_CAP chars with a truncation note. When the hunks
+    cannot attach, an inline UNAVAILABLE/EMPTY note is returned INSTEAD
+    of "" — stderr is invisible to the model, so a silent "" made the
+    Brain reject blind ("no diff present, cannot judge"); the inline
+    note tells it WHY (unresolvable file vs empty diff block) and the
+    remedy (pass project_root, or paste hunks inline). Never raises.
     """
     try:
-        path = _resolve_task_file(task_id)
+        tid = task_id.strip() if isinstance(task_id, str) else "task"
+        path = _resolve_task_file(task_id, project_root=project_root)
         if path is None:
-            return ""
+            print(f"brain-bridge: diff attach skipped "
+                  f"(task file unresolvable for {task_id!r})",
+                  file=sys.stderr)
+            return (
+                f"[changed-hunks:{tid}: UNAVAILABLE — task file "
+                f"unresolvable for {task_id!r}. The server could not "
+                f"find the task file (wrong project_root, or the task "
+                f"lives in another install). Remedy: retry with the "
+                f"correct project_root, or paste the Factual Git Diff "
+                f"hunks inline. Do NOT reject blind on missing hunks."
+            )
         text = path.read_text(encoding="utf-8", errors="replace")
         diff = extract_task_diff(text)
         if not diff.strip():
-            return ""
+            print(f"brain-bridge: diff attach skipped "
+                  f"(no Factual Git Diff block in {path.name})",
+                  file=sys.stderr)
+            return (
+                f"[changed-hunks:{tid}: EMPTY — no Factual Git Diff "
+                f"block in {path.name} yet. Stage the diff first "
+                f"(stage_and_inject_diff), then re-run this turn. "
+                f"Do NOT reject blind on missing hunks."
+            )
         try:
             rel = path.resolve().relative_to(
                 _workspace_root().resolve()).as_posix()
@@ -408,7 +468,6 @@ def build_diff_attach(task_id: str) -> str:
                 + f"\n[...diff truncated at {_TASK_DIFF_CAP} chars — "
                 + f"pull remainder via read_file({rel!r}, offset, limit)]"
             )
-        tid = task_id.strip() if isinstance(task_id, str) else "task"
         # Same V1 guard as the task attach: break fence parsing invisibly
         # so embedded fences in diff content cannot close our block early.
         diff = diff.replace(chr(96) * 3, chr(96) * 2 + chr(8203) + chr(96))
@@ -418,10 +477,20 @@ def build_diff_attach(task_id: str) -> str:
         )
     except Exception as exc:  # never fail a turn on attach problems
         print(f"brain-bridge: diff attach skipped ({exc})", file=sys.stderr)
-        return ""
+        tid = (task_id.strip() if isinstance(task_id, str)
+               else "task")
+        return (
+            f"[changed-hunks:{tid}: UNAVAILABLE — attach raised "
+            f"({exc}). Retry the turn; if it persists, paste the "
+            f"Factual Git Diff hunks inline. Do NOT reject blind "
+            f"on missing hunks."
+        )
 
 
-def _failsafe_qa_attach(user_prompt: object, task_id: object) -> str:
+def _failsafe_qa_attach(
+    user_prompt: object, task_id: object,
+    project_root: Optional[str] = None,
+) -> str:
     """Return the diff-attach block for QA-like prompts ('' otherwise).
 
     Keyword gate only: fires when the prompt reads like a QA/reviewer
@@ -433,7 +502,8 @@ def _failsafe_qa_attach(user_prompt: object, task_id: object) -> str:
     if ("qa engineer" in lowered or "code reviewer" in lowered
             or "adversarial" in lowered):
         return build_diff_attach(
-            task_id.strip() if isinstance(task_id, str) else "")
+            task_id.strip() if isinstance(task_id, str) else "",
+            project_root=project_root)
     return ""
 
 
@@ -635,21 +705,75 @@ def load_system_prompt(explicit_path: Optional[str] = None) -> str:
     )
 
 
+def _extract_unclosed_tail(text: str) -> str | None:
+    """Return the truncated trailing block for the first line-start
+    allowlisted opener with no matching close tag after it, else None.
+    Pure helper for the truncation fallback in ``extract_xml_blocks``.
+
+    Two QA-hotfix guards keep broken output from becoming live
+    instructions. First, the tag NAME alone decides allowlist membership:
+    it is lowercased before the close-tag check, and attributes never
+    participate (the opener regex already captures only the name). Second,
+    trailing PROSE is cut: a blank line followed by a line that does not
+    open XML ends the block, because prose after a broken block is
+    conversation, not instructions — the Hands executes whatever lands in
+    ``xml_blocks``. Pretty-printed XML (blank line followed by another
+    ``<`` line) passes through untouched. Empty remainder means None.
+    """
+    for m in _XML_UNCLOSED_RE.finditer(text):
+        # Lowercase: the close-tag search below is case-insensitive, and
+        # the allowlist match above already ignored case — the name, not
+        # its surface form or attributes, carries the decision.
+        name = m.group(1).lower()
+        close_re = re.compile(r"</" + name + r"\s*>", re.IGNORECASE)
+        if close_re.search(text, m.end()):
+            continue
+        lines = text[m.start():].split("\n")
+        cut = len(lines)
+        for i, line in enumerate(lines):
+            if line.strip():
+                continue
+            # Blank line: peek at the next non-blank line. XML continues
+            # only when it opens another tag; prose ends the block here.
+            for nxt in lines[i + 1:]:
+                if not nxt.strip():
+                    continue
+                if not nxt.lstrip().startswith("<"):
+                    cut = i
+                break
+            if cut != len(lines):
+                break
+        tail = "\n".join(lines[:cut]).rstrip()
+        if tail:
+            return tail
+    return None
+
+
 def extract_xml_blocks(output: str) -> list[str]:
     """Return verbatim XML control blocks in document order. Fenced code
     blocks are stripped first (XML inside backticks is documentation, not
     instructions — fence-only output means REPORT), EXCEPT explicit
     ```xml fences: the info string marks real XML, so when the unfenced
     scan finds nothing, allowlist tags inside ```xml bodies are returned
-    as a fallback (Task 215: reviewer hotfix XML arrived fenced). Empty
-    list means plain conversation — the Hands takes the whole output."""
+    as a fallback (Task 215: reviewer hotfix XML arrived fenced). Tag
+    matching tolerates attributes, whitespace, and case (Task 238 fix
+    loop). A trailing line-start opener with no close tag is surfaced
+    with trailing prose cut (truncation) instead of dropped. Empty list
+    means plain conversation — the Hands takes the whole output."""
     clean, _ = _strip_fences(output)
     blocks = [m.group(0) for m in _XML_RE.finditer(clean)]
     if blocks:
         return blocks
+    tail = _extract_unclosed_tail(clean)
+    if tail:
+        return [tail]
     out: list[str] = []
     for body in _XML_FENCE_RE.finditer(output):
-        out.extend(m.group(0) for m in _XML_RE.finditer(body.group(1)))
+        content = body.group(1)
+        out.extend(m.group(0) for m in _XML_RE.finditer(content))
+        tail = _extract_unclosed_tail(content)
+        if tail:
+            out.append(tail)
     return out
 
 
@@ -1389,6 +1513,11 @@ def brain_turn(
         include_diff: When True, append the task file's changed hunks
             (Factual Git Diff content, verbatim, capped) whenever
             task_id resolves to a file that carries a diff block.
+            Stands alone: honored even on lean turns with
+            include_bundle=False (the EMPTY_OUTPUT_RETRY shape) — the
+            old bundle gate silently dropped QA diffs on every lean
+            retry. When True but nothing attaches, a stderr reason
+            says why (unresolvable file vs empty diff block).
             QA and reviewer turns MUST pass True — the Brain judges
             the actual changes, never a summary. Fail-safe: when the
             flag is False but the prompt reads like a QA/reviewer turn
@@ -1401,9 +1530,13 @@ def brain_turn(
             unavailable labels. Default off. Small pulls stay inline.
         project_root: Optional project dir holding ``tasks/``. Its
             ``tasks/.sessions/`` stores this turn's history (per-project
-            sessions). When omitted the resolver tries
-            ``BRAIN_PROJECT_ROOT`` / ``BRAIN_WORKSPACE_ROOT`` / cwd
-            walk-up, then falls back to legacy reads.
+            sessions), and its ``tasks/`` lanes resolve the task file
+            for the task attach and the diff attach — without it both
+            resolvers fall back to the workspace root, which misses
+            when the server runs from another install. When omitted the
+            resolver tries ``BRAIN_PROJECT_ROOT`` /
+            ``BRAIN_WORKSPACE_ROOT`` / cwd walk-up, then falls back to
+            legacy reads.
 
     Returns:
         {"status": "XML_EXTRACTED"|"REPORT", "xml_blocks": [...],
@@ -1428,7 +1561,7 @@ def brain_turn(
         effective_prompt = _build_context_bundle() + "\n\n---\n\n" + user_prompt
     if include_bundle and task_id:
         try:
-            attach = _build_task_attach(task_id)
+            attach = _build_task_attach(task_id, project_root=project_root)
             _ns = (
                 f"{_TASK_FILE_MARKER}{task_id.strip()}: "
                 if isinstance(task_id, str)
@@ -1450,21 +1583,30 @@ def brain_turn(
         except Exception as exc:  # never fail a turn on attach problems
             print(f"brain-bridge: paths attach skipped ({exc})",
                   file=sys.stderr)
-    if include_bundle and include_diff and task_id:
+    # Explicit flag stands alone: a lean turn (include_bundle=False,
+    # the documented EMPTY_OUTPUT_RETRY shape) with include_diff=True
+    # MUST still carry the hunks — gating the diff on the bundle
+    # silently dropped QA diffs on every lean retry.
+    if include_diff and task_id:
         try:
             dattach = build_diff_attach(
-                task_id.strip() if isinstance(task_id, str) else "")
+                task_id.strip() if isinstance(task_id, str) else "",
+                project_root=project_root)
             if dattach:
                 effective_prompt = effective_prompt + "\n\n---\n\n" + dattach
+            else:
+                print("brain-bridge: include_diff=True but no hunks "
+                      "attached (see reason above)", file=sys.stderr)
         except Exception as exc:  # never fail a turn on attach problems
             print(f"brain-bridge: diff attach skipped ({exc})", file=sys.stderr)
-    if include_bundle and not include_diff and task_id:
+    if not include_diff and task_id:
         # Fail-safe: QA/reviewer-like prompts carry the changed hunks even
         # when the caller forgot the flag — a silent drop would let the
         # Brain judge a summary instead of the changes. Keyword gate only;
         # normal turns are untouched when the flag is False.
         try:
-            dattach = _failsafe_qa_attach(user_prompt, task_id)
+            dattach = _failsafe_qa_attach(
+                user_prompt, task_id, project_root=project_root)
             if dattach:
                 print("brain-bridge: QA turn without include_diff, "
                       "auto-attaching diff", file=sys.stderr)
@@ -1563,7 +1705,8 @@ def brain_turn(
         # REPORT. Substitute the retry hint; status stays REPORT so old
         # callers keep working. The transcript below records the hint,
         # not a verdict.
-        output = _empty_output_hint(task_id, _task_state_note(task_id))
+        output = _empty_output_hint(
+            task_id, _task_state_note(task_id, project_root))
     fence_drops = list(_last_fence_drops)
     if task_id:
         prompt_hash = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
@@ -1605,7 +1748,9 @@ def _get_reasoning_effort() -> str:
     return val
 
 
-def _task_state_note(task_id: Optional[str]) -> str:
+def _task_state_note(
+    task_id: Optional[str], project_root: Optional[str] = None
+) -> str:
     """One-line state note for the empty-output retry hint (never raises).
 
     Format: ``path | status | diff-hash``. Lets the retry-er judge whether
@@ -1615,7 +1760,7 @@ def _task_state_note(task_id: Optional[str]) -> str:
     try:
         if not task_id or not isinstance(task_id, str):
             return "unknown"
-        path = _resolve_task_file(task_id)
+        path = _resolve_task_file(task_id, project_root=project_root)
         if path is None:
             return "unknown"
         try:
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index 40f3623..bf657c0 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -53,7 +53,35 @@ class GitIgnoreFilter:
         abs_path = path.resolve()
         if ".git" in abs_path.parts or abs_path.name == ".git":
             return True
-        current = abs_path.parent
+        # Repo boundary (Task 238 fix loop): git only applies .gitignore
+        # files INSIDE the repo. The old walk-to-/ let a grandparent
+        # .gitignore (e.g. `projects/` two levels up) mark every in-repo
+        # path ignored, which broke get_directory_tree("."). Stop at the
+        # nearest self-or-ancestor dir containing .git (its spec still
+        # applies); with no repo found, floor at cwd when the path lives
+        # under it, else keep the legacy walk-to-/ behavior.
+        boundary: Path | None = None
+        probe = abs_path if abs_path.is_dir() else abs_path.parent
+        cwd = Path.cwd().resolve()
+        # Both .git forms stop the walk: a directory in normal repos, a
+        # FILE in submodule/worktree roots (gitdir pointer). Either way
+        # this dir is a repo root and .gitignore files above it never
+        # apply inside.
+        while True:
+            dot_git = probe / ".git"
+            if dot_git.is_dir() or dot_git.is_file():
+                boundary = probe
+                break
+            if probe == probe.parent:
+                break
+            probe = probe.parent
+        if boundary is None:
+            try:
+                abs_path.relative_to(cwd)
+                boundary = cwd
+            except ValueError:
+                boundary = None
+        current = abs_path if abs_path.is_dir() else abs_path.parent
         while True:
             spec = self._get_spec(current)
             if spec:
@@ -66,6 +94,8 @@ class GitIgnoreFilter:
                         return True
                 except ValueError:
                     pass
+            if boundary is not None and current == boundary:
+                break
             if current == current.parent:
                 break
             current = current.parent
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 5c5846a..c750b05 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1012,6 +1012,70 @@ def test_brain_turn_include_bundle_false_skips_attach(tmp_path, monkeypatch):
     assert not any("[task-file:" in c for c in user_contents)
 
 
+def test_brain_turn_lean_diff_attaches_without_bundle(tmp_path, monkeypatch):
+    # Task 238 "why" fix: the old bundle gate silently dropped QA diffs
+    # on every lean retry (include_bundle=False). The explicit flag
+    # stands alone now — hunks must ride the lean turn.
+    _mk_tasks_root(tmp_path)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    holder = {}
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))], holder)
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("q", task_id="200",
+                     include_bundle=False, include_diff=True)
+    assert result["status"] == "REPORT"
+    user_contents = [t["content"] for t in holder["body"]["input"]]
+    assert any("[changed-hunks:" in c for c in user_contents)
+    assert any("DIFFSTUFF" in c for c in user_contents)
+
+
+def test_brain_turn_failsafe_fires_without_bundle(tmp_path, monkeypatch):
+    # QA-like prompt, flag forgotten, bundle off — the failsafe must
+    # still auto-attach the hunks (it no longer requires the bundle).
+    _mk_tasks_root(tmp_path)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    holder = {}
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))], holder)
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("qa engineer, adversarial review please",
+                     task_id="200", include_bundle=False)
+    assert result["status"] == "REPORT"
+    user_contents = [t["content"] for t in holder["body"]["input"]]
+    assert any("[changed-hunks:" in c for c in user_contents)
+
+
+def test_brain_turn_include_diff_unresolvable_warns(tmp_path, monkeypatch,
+                                                     capsys):
+    # Loud skip: flag set but no file — stderr must say why instead
+    # of silently sending a diff-less QA turn.
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    holder = {}
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))], holder)
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("q", task_id="200", include_diff=True)
+    assert result["status"] == "REPORT"
+    assert "unresolvable" in capsys.readouterr().err
+    # Re-QA repair: the model itself must see WHY — the inline note
+    # rides in the sent prompt, never a silent empty attach.
+    user_contents = [t["content"] for t in holder["body"]["input"]]
+    assert any("UNAVAILABLE" in c for c in user_contents)
+
+
 def test_task_resolve_tmp_root_integration(tmp_path, monkeypatch):
     for lane in ("backlog", "qa"):
         d = tmp_path / "tasks" / lane
@@ -1351,10 +1415,12 @@ def test_extract_uppercase_fence_lowercase_tag():
     assert blocks[0].startswith("<hotfix>")
 
 
-def test_extract_uppercase_tag_stays_ignored():
-    # Locks current behavior: tag names are lowercase per protocol.
-    assert bridge.extract_xml_blocks("<HOTFIX>x</HOTFIX>") == []
-    assert bridge.extract_xml_blocks("```xml\n<HOTFIX>x</HOTFIX>\n```") == []
+def test_extract_uppercase_tag_tolerated():
+    # Task 238 fix loop (supersedes the lowercase-only lock): model output
+    # varies in case; an operative tag in any case still extracts.
+    blocks = bridge.extract_xml_blocks("<HOTFIX>x</HOTFIX>")
+    assert len(blocks) == 1
+    assert bridge.extract_xml_blocks("```xml\n<HOTFIX>x</HOTFIX>\n```") != []
 
 
 def test_extract_fence_without_newline_ignored():
@@ -1367,10 +1433,16 @@ def test_extract_empty_hotfix_block():
     assert len(blocks) == 1
 
 
-def test_extract_tag_with_attributes_stays_ignored():
-    # Locks current behavior: bare tag names only; attribute-form tags
-    # are not operative instructions.
-    assert bridge.extract_xml_blocks('<hotfix id="1">x</hotfix>') == []
+def test_extract_tag_with_attributes_tolerated():
+    # Task 238 fix loop (supersedes the bare-names-only lock): attribute
+    # and whitespace forms of operative tags still extract.
+    for variant in (
+        '<hotfix id="1">x</hotfix>',
+        "<hotfix >x</hotfix>",
+        '<HANDS_IMPLEMENTATION_TASK retry="2">y</HANDS_IMPLEMENTATION_TASK>',
+    ):
+        blocks = bridge.extract_xml_blocks(variant)
+        assert len(blocks) == 1, variant
 
 
 def test_extract_quad_xml_fence_stays_ignored():
@@ -1379,6 +1451,80 @@ def test_extract_quad_xml_fence_stays_ignored():
     out = "````xml\n<hotfix>x</hotfix>\n````"
     assert bridge.extract_xml_blocks(out) == []
 
+
+# --- Task 238 fix loop: tolerance + truncation fallback ---
+
+def test_extract_mismatched_close_stays_ignored():
+    # Mid-line so the truncation fallback (line-start only) stays out.
+    assert bridge.extract_xml_blocks("note <hotfix>x</failure_report> tail") == []
+
+
+def test_extract_non_allowlisted_tag_never_extracts():
+    # reasoning_log is conversation, never instructions — any case, attrs,
+    # fenced or bare, closed or line-start unclosed.
+    assert bridge.extract_xml_blocks("<reasoning_log>x</reasoning_log>") == []
+    assert bridge.extract_xml_blocks("<REASONING_LOG>x</REASONING_LOG>") == []
+    assert bridge.extract_xml_blocks('<reasoning_log tone="t">x</reasoning_log>') == []
+    assert bridge.extract_xml_blocks("```xml\n<reasoning_log>x</reasoning_log>\n```") == []
+    assert bridge.extract_xml_blocks("notes\n<reasoning_log>truncated") == []
+
+
+def test_extract_truncated_trailing_block_surfaced():
+    out = "thinking\n<hotfix>apply A1-A8"
+    blocks = bridge.extract_xml_blocks(out)
+    assert len(blocks) == 1
+    assert blocks[0].startswith("<hotfix>")
+
+
+def test_extract_truncated_tail_cuts_trailing_prose():
+    # QA hotfix M1: prose after the broken block must stay conversation,
+    # never become instructions the Hands executes.
+    out = "notes\n<hotfix>apply A1\n\nC1 explains why this is safe"
+    blocks = bridge.extract_xml_blocks(out)
+    assert len(blocks) == 1
+    assert "explains" not in blocks[0]
+    assert blocks[0].startswith("<hotfix>")
+
+
+def test_extract_plain_prose_angle_brackets_never_extracts():
+    # QA hotfix M2: angle brackets with no allowlisted tag yield nothing.
+    assert bridge.extract_xml_blocks("compare a < b and c > d, done") == []
+    assert bridge.extract_xml_blocks("price <10> and <20> ok") == []
+
+
+def test_extract_unclosed_uppercase_with_attrs_surfaced():
+    # QA hotfix V2: case and attributes never affect the allowlist
+    # decision — the tag NAME alone decides.
+    out = "notes\n<HOTFIX ID=\"7\">do step 1"
+    blocks = bridge.extract_xml_blocks(out)
+    assert len(blocks) == 1
+    assert blocks[0].startswith("<HOTFIX")
+
+
+def test_extract_truncated_block_with_attributes_surfaced():
+    out = "thinking\n<HANDS_IMPLEMENTATION_TASK retry=\"2\">do step 1"
+    blocks = bridge.extract_xml_blocks(out)
+    assert len(blocks) == 1
+
+
+def test_extract_mid_sentence_unclosed_mention_ignored():
+    # Line-start required: prose mentions never trigger the fallback.
+    assert bridge.extract_xml_blocks("use <hotfix> for urgent fixes") == []
+
+
+def test_extract_truncated_inside_xml_fence_surfaced():
+    out = "notes\n```xml\n<hotfix>apply A1"
+    blocks = bridge.extract_xml_blocks(out)
+    assert len(blocks) == 1
+    assert blocks[0].startswith("<hotfix>")
+
+
+def test_extract_closed_block_wins_over_truncated_tail():
+    out = "<failure_report>live</failure_report>\n<hotfix>truncated"
+    blocks = bridge.extract_xml_blocks(out)
+    assert len(blocks) == 1
+    assert blocks[0].startswith("<failure_report>")
+
 # --- Task-number gate: task_id is a bare number, never suffixed ---
 # (Session finding: "215qa"/"215rev"/"215plan" forked one task's history
 # into separate transcript dirs. The tool entry now rejects them.)
diff --git a/tests/test_brain_diff_attach.py b/tests/test_brain_diff_attach.py
index 5e010e1..b295f26 100644
--- a/tests/test_brain_diff_attach.py
+++ b/tests/test_brain_diff_attach.py
@@ -54,28 +54,44 @@ def test_extract_diff_unclosed_cuts_to_eof():
 def test_build_diff_attach_resolved_with_diff(monkeypatch, tmp_path):
     target = tmp_path / "99-sample.md"
     target.write_text(_task_text("+added"), encoding="utf-8")
-    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
+    monkeypatch.setattr(
+        bridge, "_resolve_task_file",
+        lambda tid, project_root=None: target)
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
     out = bridge.build_diff_attach("99")
     assert "+added" in out
 
 
-def test_build_diff_attach_no_diff_returns_empty(monkeypatch, tmp_path):
+def test_build_diff_attach_no_diff_returns_inline_empty_note(
+        monkeypatch, tmp_path):
+    # Re-QA repair: stderr is invisible to the model, so an empty diff
+    # returns an inline EMPTY note (never silent "") with the remedy.
     target = tmp_path / "99-sample.md"
     target.write_text("# Task 99: no diff\n", encoding="utf-8")
-    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
-    assert bridge.build_diff_attach("99") == ""
+    monkeypatch.setattr(
+        bridge, "_resolve_task_file",
+        lambda tid, project_root=None: target)
+    out = bridge.build_diff_attach("99")
+    assert "EMPTY" in out
+    assert "stage_and_inject_diff" in out
 
 
-def test_build_diff_attach_unresolvable_returns_empty(monkeypatch):
-    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: None)
-    assert bridge.build_diff_attach("nope") == ""
+def test_build_diff_attach_unresolvable_returns_inline_note(monkeypatch):
+    # Re-QA repair: unresolvable file returns an inline UNAVAILABLE
+    # note (never silent "") naming project_root as the remedy.
+    monkeypatch.setattr(
+        bridge, "_resolve_task_file", lambda tid, project_root=None: None)
+    out = bridge.build_diff_attach("nope")
+    assert "UNAVAILABLE" in out
+    assert "project_root" in out
 
 
 def test_build_diff_attach_over_cap_truncates(monkeypatch, tmp_path):
     target = tmp_path / "99-sample.md"
     target.write_text(_task_text("x" * 50000), encoding="utf-8")
-    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
+    monkeypatch.setattr(
+        bridge, "_resolve_task_file",
+        lambda tid, project_root=None: target)
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
     monkeypatch.setattr(bridge, "_TASK_DIFF_CAP", 100)
     out = bridge.build_diff_attach("99")
@@ -91,7 +107,9 @@ def test_extract_diff_empty_pair_yields_empty():
 def test_build_diff_attach_breaks_embedded_fences(monkeypatch, tmp_path):
     target = tmp_path / "99-sample.md"
     target.write_text(_task_text("line\n```evil\nline"), encoding="utf-8")
-    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
+    monkeypatch.setattr(
+        bridge, "_resolve_task_file",
+        lambda tid, project_root=None: target)
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
     out = bridge.build_diff_attach("99")
     assert "```evil" not in out
@@ -101,7 +119,9 @@ def test_build_diff_attach_breaks_embedded_fences(monkeypatch, tmp_path):
 def test_failsafe_qa_prompt_attaches_without_flag(monkeypatch, tmp_path):
     target = tmp_path / "99-sample.md"
     target.write_text(_task_text("+added"), encoding="utf-8")
-    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
+    monkeypatch.setattr(
+        bridge, "_resolve_task_file",
+        lambda tid, project_root=None: target)
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
     out = bridge._failsafe_qa_attach(
         "QA engineer, adversarial review please", "99")
@@ -111,5 +131,68 @@ def test_failsafe_qa_prompt_attaches_without_flag(monkeypatch, tmp_path):
 def test_failsafe_normal_prompt_stays_empty(monkeypatch, tmp_path):
     target = tmp_path / "99-sample.md"
     target.write_text(_task_text("+added"), encoding="utf-8")
-    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
+    monkeypatch.setattr(
+        bridge, "_resolve_task_file",
+        lambda tid, project_root=None: target)
     assert bridge._failsafe_qa_attach("fix the login bug", "99") == ""
+
+
+def _mk_project(tmp_path, name="proj"):
+    proj = tmp_path / name
+    lane = proj / "tasks" / "qa"
+    lane.mkdir(parents=True)
+    (lane / "999-sample.md").write_text(
+        _task_text("+via-project-root"), encoding="utf-8")
+    return proj
+
+
+def test_resolve_task_file_honors_project_root(monkeypatch, tmp_path):
+    proj = _mk_project(tmp_path)
+    empty = tmp_path / "empty"
+    empty.mkdir()
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: empty)
+    found = bridge._resolve_task_file("999", project_root=str(proj))
+    assert found is not None and found.name == "999-sample.md"
+    assert bridge._resolve_task_file("999") is None
+
+
+def test_resolve_task_file_project_root_without_tasks_falls_back(
+        monkeypatch, tmp_path):
+    lane = tmp_path / "tasks" / "qa"
+    lane.mkdir(parents=True)
+    (lane / "999-sample.md").write_text(
+        _task_text("+via-workspace"), encoding="utf-8")
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    bare = tmp_path / "bare"
+    bare.mkdir()
+    found = bridge._resolve_task_file("999", project_root=str(bare))
+    assert found is not None and found.name == "999-sample.md"
+
+
+def test_build_diff_attach_via_project_root(monkeypatch, tmp_path):
+    proj = _mk_project(tmp_path)
+    empty = tmp_path / "empty"
+    empty.mkdir()
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: empty)
+    out = bridge.build_diff_attach("999", project_root=str(proj))
+    assert "+via-project-root" in out
+
+
+def test_build_diff_attach_unresolvable_says_so(monkeypatch, capsys):
+    monkeypatch.setattr(
+        bridge, "_resolve_task_file",
+        lambda tid, project_root=None: None)
+    out = bridge.build_diff_attach("nope")
+    assert "UNAVAILABLE" in out  # inline note for the model, not ""
+    assert "unresolvable" in capsys.readouterr().err  # stderr kept too
+
+
+def test_build_diff_attach_empty_diff_says_so(monkeypatch, tmp_path, capsys):
+    target = tmp_path / "99-sample.md"
+    target.write_text("# Task 99: no diff\n", encoding="utf-8")
+    monkeypatch.setattr(
+        bridge, "_resolve_task_file",
+        lambda tid, project_root=None: target)
+    out = bridge.build_diff_attach("99")
+    assert "EMPTY" in out  # inline note for the model, not ""
+    assert "no Factual Git Diff block" in capsys.readouterr().err
diff --git a/tests/test_mcp_servers.py b/tests/test_mcp_servers.py
index b923929..9244396 100644
--- a/tests/test_mcp_servers.py
+++ b/tests/test_mcp_servers.py
@@ -2171,6 +2171,82 @@ def test_tree_rejects_parent_escape():
             os.chdir(old_cwd)
 
 
+def test_tree_dot_not_ignored_by_parent_gitignore():
+    """Task 238 fix loop: a grandparent .gitignore must not mark the whole
+    repo ignored — get_directory_tree('.') returns the tree."""
+    import os
+    import tempfile
+    from pathlib import Path
+
+    mod = _load_context_server_hardening()
+    with tempfile.TemporaryDirectory() as tmpdir:
+        parent = Path(tmpdir)
+        (parent / ".gitignore").write_text("repo/\n", encoding="utf-8")
+        repo = parent / "repo"
+        (repo / ".git").mkdir(parents=True)
+        (repo / ".gitignore").write_text("ignored-dir/\n", encoding="utf-8")
+        (repo / "ignored-dir").mkdir()
+        (repo / "kept.txt").write_text("x", encoding="utf-8")
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            result = mod.get_directory_tree(".")
+            assert result.startswith("## Directory Tree:"), result[:120]
+            assert "kept.txt" in result
+            assert "ignored-dir" not in result
+        finally:
+            os.chdir(old_cwd)
+
+
+def test_tree_outer_gitignore_naming_inner_file_does_not_apply():
+    """QA hotfix M3: an outer .gitignore OUTSIDE the repo root naming an
+    inner file must not hide it — outer rules never apply inside."""
+    import os
+    import tempfile
+    from pathlib import Path
+
+    mod = _load_context_server_hardening()
+    with tempfile.TemporaryDirectory() as tmpdir:
+        parent = Path(tmpdir)
+        (parent / ".gitignore").write_text("kept.txt\n", encoding="utf-8")
+        repo = parent / "repo"
+        (repo / ".git").mkdir(parents=True)
+        (repo / "kept.txt").write_text("x", encoding="utf-8")
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            result = mod.get_directory_tree(".")
+            assert result.startswith("## Directory Tree:"), result[:120]
+            assert "kept.txt" in result
+        finally:
+            os.chdir(old_cwd)
+
+
+def test_tree_git_file_stops_upward_walk():
+    """QA hotfix M4: submodule/worktree roots carry a .git FILE, not a
+    dir — it must stop the upward .gitignore walk like a .git dir."""
+    import os
+    import tempfile
+    from pathlib import Path
+
+    mod = _load_context_server_hardening()
+    with tempfile.TemporaryDirectory() as tmpdir:
+        parent = Path(tmpdir)
+        (parent / ".gitignore").write_text("kept.txt\n", encoding="utf-8")
+        repo = parent / "sub"
+        repo.mkdir()
+        (repo / ".git").write_text("gitdir: /elsewhere\n", encoding="utf-8")
+        (repo / "kept.txt").write_text("x", encoding="utf-8")
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            result = mod.get_directory_tree(".")
+            assert result.startswith("## Directory Tree:"), result[:120]
+            assert "kept.txt" in result
+        finally:
+            os.chdir(old_cwd)
+
+
 def test_tree_none_defaults_to_workspace_root():
     """Non-string target degrades gracefully to the whole-project default."""
     import os
```
<!-- END_GIT_DIFF -->
