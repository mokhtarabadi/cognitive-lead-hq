# Task 238: Fix all gaps overnight

**File:** `tasks/completed/238-fix-all-gaps-overnight.md`
**Source:** manager
**Type:** improvement
**Status:** closed

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
- Manager accept quote: "Close task" — closure gate satisfied (file in tasks/qa + PO_REVIEW_PENDING logged). Executing single-issuance closure: move to tasks/completed, status closed, commit via commit_and_clean_task only.
- Post-restart live probe: brain_turn (bundle+diff, project_root) carried task text AND real hunks — the why-fix is proven on the live global server. Full suite: 374 passed + same 4 pre-existing test_skill_registry fails (stash-proven on clean HEAD).
- Seat Check (why-fix): Programmer for bridge repair + tests; Architect for the gate/resolver design call. No UI, schema, sprint, QA-seat, or Reviewer-seat triggers; Designer/Planner/Strategist skipped with reason.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `bcfee926a79544019f29a40e1d7e3589bb47d43f`
<!-- END_GIT_DIFF -->
