# Task 266: Release v9.41.0 with milestone-20 archive

**File:** `tasks/qa/266-release-v9-41-0-with-milestone-20-archive.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Cut release v9.41.0. Archive the 33 completed tasks (229-265) into `docs/history/milestone-20-summary.md` and move them to `tasks/archive/` FIRST, then move the CHANGELOG `[Unreleased]` entries under a `## [9.41.0]` header leaving `[Unreleased]` empty, run every release verification gate (task lint, markdown lint, prompt-fragment sync, py_compile, docs-sync, full pytest suite), generate the executable push script at `/tmp/cognitive-lead-push-release.sh`, stage via the MCP tool, and hand the Manager the review hand-off.

## Manager's Notes

- Release version **9.41.0** matches the current `<system_version>` (system-prompt.md and prompts/fragments/01_system_version.md both read 9.41.0), so no fragment edit or prompt rebuild is needed — the prompt was already rebuilt during the 9.36.0-9.41.0 work. This follows the Task 229 precedent.
- Memory `release/release-workflow` governs this task: archive-on-release is a standing rule (archive BEFORE the release), `[Unreleased]` MUST be empty after the release, and an executable push script at `/tmp/cognitive-lead-push-release.sh` MUST be created with strict mode, tag creation, push, and GitHub Release steps.
- ZAC: the Hands never run `git add`, `git commit`, `git push`, `git tag`, or `gh release create`. Only `git mv` for Kanban moves. Staging is MCP-only; the commit goes through `custom_context_commit_and_clean_task` after the Manager's exact closure words.
- The public tag and GitHub Release publication are a manual Manager step.

## Local TODOs

- [x] Create the release task file and move it to `tasks/in-progress/`
- [x] Archive step FIRST: write `docs/history/milestone-20-summary.md` covering tasks 229-265, then `git mv tasks/completed/*.md tasks/archive/`
- [x] CHANGELOG Parse-Then-Append: move every `[Unreleased]` entry under `## [9.41.0] - 2026-09-20`, leaving `[Unreleased]` empty
- [x] Run all release verification gates (task lint, markdown lint, prompt sync, py_compile, docs-sync, full pytest)
- [x] Write the executable push script at `/tmp/cognitive-lead-push-release.sh`
- [x] Stage via `custom_context_stage_and_inject_diff` and move the task to `tasks/qa/`
- [x] Stale-memory audit report (read-only; no deletes without Manager approval)

## Acceptance Criteria

- [x] Archive step done FIRST: `docs/history/milestone-20-summary.md` exists with the milestone structure, `tasks/completed/` is empty, and all 33 files are in `tasks/archive/`
- [x] CHANGELOG `[Unreleased]` section is empty; every former entry sits under `## [9.41.0] - 2026-09-20` with no duplicate version or category headers
- [x] Full test suite passes exit 0; `scripts/check_docs_sync.py` passes; prompt-fragment sync verified byte-identical; `python3 -m py_compile` passes for the prompt-build scripts and the lint server
- [x] `lint_task_file` passes on the active release task file
- [x] `/tmp/cognitive-lead-push-release.sh` exists, is `chmod +x`, starts with `set -euo pipefail`, detects the repo root, defines `VERSION="v9.41.0"`, verifies a clean tree and `gh auth status`, creates the annotated tag only if missing, pushes commits and tags, then creates or verifies the GitHub Release
- [x] Diff staged via the MCP tool and injected into this task file; no commit by the Hands
- [x] Manager receives the exact tag/push/release commands for manual execution

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** full suite green exit 0; `scripts/check_docs_sync.py` OK; `lint_system_prompt_sync` in sync at 9.41.0; py_compile clean; `lint_task_file` clean
- **Actual result:** `rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q` → `686 passed, 10 warnings in 5.56s`. Other gates: `lint_markdown CHANGELOG.md` PASS; `lint_markdown docs/history/milestone-20-summary.md` PASS; prompt sync verified byte-identical via `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/opencode/system-prompt-check-266.md` + `diff -q system-prompt.md` → PROMPT_SYNC_OK; `python3 -m py_compile scripts/prompt-build/assemble_system_prompt.py scripts/prompt-build/split_system_prompt.py scripts/check_docs_sync.py mcp-lint-server/server.py` → PY_COMPILE_OK; `python3 scripts/check_docs_sync.py` → `docs-sync: OK`; `bash -n /tmp/cognitive-lead-push-release.sh` → BASH_SYNTAX_OK. Archive: `git mv tasks/completed/*.md tasks/archive/` → 33 renames, `tasks/completed/` empty, `tasks/archive/` grew 225 → 258.
- **Exit code:** 0 (pytest), 0 (check_docs_sync.py)

> Verification runner rule: the command above is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** archiving loses task history, or the release is cut with a non-empty `[Unreleased]` section and a wrong version header; a stray commit by the Hands would break ZAC.
- **Rollback plan:** archival uses `git mv` so history stays reachable via `git log --follow -- tasks/archive/<file>`; the CHANGELOG edit is a pure section move, revertible from git; no `git add`/`commit`/`push`/`tag` is ever run by the Hands; the tag is created only if missing and never force-moved.

---

## Execution Log & Reasoning

### Skills and memory loaded (release-workflow SOP)

Loaded `archive-tasks`, `versioning-and-release`, `project-memory`, `verification-before-completion`, `task-lint`. Read memory `release/release-workflow` (the governing SOP) plus `workflows/no_task_for_global_upgrade` and `workflows/global-install-upgrade`.

### Assumptions

- **A1 — "milestone skill" = `archive-tasks`.** No skill named `milestone` exists in the 36-skill global set; `archive-tasks` is described as the milestone-compaction skill, so it is the one the Manager named.
- **A2 — Release version = 9.41.0.** `system-prompt.md` line 1 and `prompts/fragments/01_system_version.md` line 1 both read `9.41.0`, and no prompt change ships in this release. Following the Task 229 precedent, the release version matches the already-built `<system_version>`, so no fragment edit and no prompt rebuild are needed; the CHANGELOG simply catches up from its last header (9.35.0) to 9.41.0. This is a MINOR-class release body (new skills/workflow capabilities accumulated across 9.36.0-9.41.0) recorded under the 9.41.0 header.
- **A3 — prompt sync verified by the repo assembler, not the MCP tool.** `lint_system_prompt_sync` resolved the assembler against the GLOBAL lint-server install dir (`/home/mohammad/.config/opencode/scripts/prompt-build/assemble_system_prompt.py`) and errored with `Errno 2` because the global install ships only the server code, not `scripts/`. Equivalent verification was therefore run in-repo: assemble to a temp path and `diff -q` against `system-prompt.md` → byte-identical. The gate intent (no prompt/fragment drift) is satisfied.

### Changes

1. **Task file** `tasks/in-progress/266-release-v9-41-0-with-milestone-20-archive.md` created from the canonical template (Source: manager, Type: feature) and moved out of `tasks/backlog/`.
2. **Archive step done FIRST** (standing Manager rule 2026-09-12): `docs/history/milestone-20-summary.md` written covering all 33 completed tasks (229-252, 257-265); `git mv tasks/completed/*.md tasks/archive/` moved all 33 files (staged as renames `R`), leaving `tasks/completed/` empty and `tasks/archive/` at 258 files. History stays reachable via `git log --follow -- tasks/archive/<file>`.
3. **CHANGELOG Parse-Then-Append**: inserted `## [9.41.0] - 2026-09-20` between `## [Unreleased]` and the existing `### Added` block. No version or category header was duplicated; the existing `### Added` and `### Fixed` blocks now sit under 9.41.0 and `[Unreleased]` is empty. `## [9.35.0] - 2026-09-14` and older headers are untouched.
4. **Push script** `/tmp/cognitive-lead-push-release.sh` written and `chmod +x` (mode 755), syntax-checked with `bash -n`. It starts with `set -euo pipefail`, resolves the repo root, sets `VERSION="v9.41.0"`, refuses a dirty tree, requires `gh auth status`, pushes the branch, creates the annotated tag only if missing, pushes tags, then creates or verifies the GitHub Release and prints the remote tag and release URL.
5. **Stale Memory Report (read-only — nothing deleted, Manager approval required):**

   | Namespace / Key | Reason flagged | Evidence |
   | --------------- | -------------- | -------- |
   | `opencode_config/plugin_policy_dcp_only_2026_09_08` | Claims the goal plugin was removed from all four configs (dcp-only). Live config contradicts it. | `tui.json` (repo and global) carries `plugin: ["@prevalentware/opencode-goal-plugin", "@tarquinen/opencode-dcp@latest"]`, and the goal plugin is active in this session. |
   | `workflows/global-install-upgrade` (embedded 2026-09-09 claim) | One embedded claim says the persona and manager_decisions MCP servers were DISABLED in repo and global `opencode.json`. | The global config currently enables 7 servers including `manager_decisions` and `brain`; `opencode mcp list` reports 7/7 connected. The rest of this workflow memory is current and was used as-is. |
   | `opencode_config/global_goal_plugin_upgrade_2026_08_27` | Overlaps `plugin_policy_dcp_only_2026_09_08` on the same topic (goal plugin presence) with conflicting conclusions. | Both cover the goal plugin; the 2026-08-27 entry matches live config, the 2026-09-08 entry does not. Flagged as a duplicate-topic pair, not individually stale. |

   No memory was deleted or edited. All three require explicit Manager approval before any `delete_memory` call.

### Verification

- Full suite (RTK-prefixed, first run): **686 passed, 10 warnings in 5.56s**, exit 0.
- `lint_markdown` CHANGELOG.md → PASS; `lint_markdown` docs/history/milestone-20-summary.md → PASS.
- Prompt sync → byte-identical (see A3). `python3 -m py_compile` on the two prompt-build scripts, `check_docs_sync.py` and `mcp-lint-server/server.py` → clean. `scripts/check_docs_sync.py` → `docs-sync: OK`, exit 0 (two warn-only orphans: `scripts/fetch-opencode-docs.py`, `scripts/repomd`).
- `lint_task_file` on the active task file → PASS (the initial run flagged only the stale `tasks/backlog/...` `**File:**` header, corrected to the in-progress path).
- Milestone summary completeness: 33 `### Task` sections, all IDs 229-252 and 257-265 present in both the `## Criteria Met` table and `## Individual Task Summaries`; sources all `manager`; types 12 bug / 13 improvement / 8 feature.

### ZAC

No `git add`, `git commit`, `git push`, `git tag`, or `gh release create` was run. `git mv` was used only for the Kanban archive move. Staging goes through `custom_context_stage_and_inject_diff` only, and the tag/release publication is left to the Manager via the generated script. Closure still requires the Manager's exact words "Approved for closure" or "Close task".

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b6c7420..b1c79d8 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,8 +6,11 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.41.0] - 2026-09-20
+
 ### Added
 
+- **Release ceremony: milestone-20 archive + v9.41.0 push tooling (Task 266):** the 33 completed tasks (229-265) were compacted into `docs/history/milestone-20-summary.md` and moved to `tasks/archive/` **before** the release, the accumulated CHANGELOG `[Unreleased]` backlog was moved under `## [9.41.0] - 2026-09-20` leaving `[Unreleased]` empty, and an executable push script `/tmp/cognitive-lead-push-release.sh` was generated for Manager-run tagging, pushing and GitHub Release creation (strict mode, clean-tree and `gh auth` preflight, annotated tag created only if missing, release created or verified). `system-prompt.md` version unchanged — the shipped prompt was already built at 9.41.0.
 - **Risk-aware Brain model routing enabled by default (Task 261):** `brain_turn` no longer sends every turn to one model. It now derives the model from the turn `stage`: the hard stages `plan` and `review` route to the high model `openai/gpt-5.6-luna`, while the lighter `implement`, `qa` and `closure` stages route to the low model `deepseek/deepseek-v4.1-flash`; a missing stage falls back to `BRAIN_MODEL`, while an unknown stage is rejected by the request preflight. An explicit `risk_tier` on the call still wins over the stage-derived tier. `mcp-brain-bridge/server.py` gains a pure `resolve_stage_tier()` resolver and a `_get_stage_tiers()` map, and the context-ledger row now records the effective tier. Every routing value is `.env`-overridable (`BRAIN_MODEL_LOW`, `BRAIN_MODEL_HIGH`, `BRAIN_STAGE_TIERS`) while carrying that same value as its built-in code default, so the baseline works with no `.env` entries at all; routing itself defaults ON and a falsy `BRAIN_RISK_ROUTING_ENABLED` disables it so every turn falls back to `BRAIN_MODEL`. `docs/brain-bridge.md` and `.env.example` were updated, including two previously stale defaults (`BRAIN_REASONING_EFFORT` now `medium`, `BRAIN_MAX_TOKENS` now `32768`). Full suite: **632 passed**.
 
 - **Brain-bridge reliability bundle META 257 (syncs GitHub issues 16, 17, 18, 19):** four stdlib-only modules plus prompt reconciliation. `mcp-brain-bridge/preflight.py` (Issue 18, P1): local request validation before transport — explicit `project_root` must hold `tasks/` (raise, never silent workspace-root fallback — the fallback WAS the Cando-828 double failure), omitted root resolves via explicit → `BRAIN_PROJECT_ROOT` → `BRAIN_WORKSPACE_ROOT` → cwd walk-up and raises naming the remedy on exhaustion; new `session_id`/`stage` (plan/implement/qa/review/closure)/`kanban_path`/`required_tools` params; exactly-one task_id/session_id binding for memory turns, neither means one-off. `mcp-brain-bridge/capability.py` (Issue 16, P3): three-status manifest (`AVAILABLE`/`UNAVAILABLE_REQUIRED`/`UNAVAILABLE_OPTIONAL`) grounded in `opencode.json` permissions — `question` resolves to `UNAVAILABLE_REQUIRED` (internal registry `KNOWN_UNAVAILABLE`: absent from permissions, zero repo definitions — the registry name is never emitted as a public manifest status); stage-implied requirements (qa→lint_task_file, closure→commit_and_clean, plan/review→brain_turn); blocked approval-sensitive work returns a non-verdict REPORT relay block with zero transport calls, and the `question`-tool handoff contradictions are reconciled in `agents/cognitive-executor.md`, `prompts/fragments/09-hands_protocols.md`, and `skill-templates/telegram-issue-sync/SKILL.md` (manifest check first, never silent skip; single approval rule; manual→relay+pause, autopilot→replay-or-halt). `mcp-brain-bridge/transport_learning.py` (Issue 17, P2): `unsupported_parameter` 400 classifier with protected keys (model/input never dropped), one corrected retry, saga-scoped correction memory keyed by task_id persisted as ledger events, repeat same-class failures escalate via marked `TransportEscalationError` — transport raises preserved, never verdicts. `mcp-brain-bridge/session_ledger.py` + decision/lint extensions (Issue 19, P4-P7): append-only `session_ledger.jsonl` with `start_session` (10 required fields) + 9 ordered checkpoints wired into `brain_turn`; `extract_session_decisions` accepts taskless `session_id`/non-numeric ids; pending→approved/rejected ledger candidates never touch the DEC store before approval; lint exempts ```source-evidence fenced blocks from markdown-basics (unclosed block is its own error, fence contents never satisfy structure) and a new `analysis` task Type accepts Report Evidence instead of test-command evidence. Shipped prompt rebuilt to **9.41.0**. 86 new tests (`test_brain_preflight`, `test_brain_capability`, `test_brain_transport_learning`, `test_session_lifecycle`) + 4 existing tests re-seamed to explicit `project_root`. Full suite: **596 passed**, zero regressions.
diff --git a/docs/history/milestone-20-summary.md b/docs/history/milestone-20-summary.md
new file mode 100644
index 0000000..367030e
--- /dev/null
+++ b/docs/history/milestone-20-summary.md
@@ -0,0 +1,298 @@
+# Milestone 20 Summary
+
+**Date:** 2026-09-20
+**Tasks Compacted:** 33 (229-265)
+
+## Source Distribution
+
+| Source       | Count |
+| ------------ | ----- |
+| orchestrator | 0     |
+| telegram     | 0     |
+| manager      | 33    |
+
+## Architectural Changes
+
+- Release ceremony: v9.35.0 cut with the milestone-19 archive, CHANGELOG `[Unreleased]` moved under the release header, and an executable Manager push script (229).
+- Brain session isolation matured from a global folder into per-project `tasks/.sessions/` keyed by project root + task id, with a shared resolver, loud legacy read-through, no-global-write enforcement, an append-only transcript (compaction bounds the send view only), a migration manifest, and a cross-project bleed guard for legacy fallbacks (234, 236, 241, 262).
+- Supervised autopilot replaced fire-and-forget: discovery feed, mandatory plan-approval pause, seat routing, bounded QA/review loops, risk tiers T0/T1/T2 with max-3-tries escalation, and a trivial fast path; the review-approval relay now requires exact accept words, single issuance, and an idempotent audit-skill session-history gitignore (233, 235).
+- Brain Bridge gained a local transport preflight (project_root/task_id/session_id/stage/kanban validation, no silent cwd default), a three-status capability manifest with required-tool blocking, transport-failure learning (one corrected retry, saga memory, escalation), and a session ledger with ordered phase checkpoints plus taskless decision-persistence candidates (257).
+- Prompt/output contract hardened: `EMPTY_OUTPUT_RETRY` with a pre-call size warning, provider diagnostics (`status`/`incomplete_details`/`usage`/`error`/`refusal`) attached every turn, terminal ordered triage error→refusal→max_output_tokens→flake, nested `reasoning.effort`, and an HTTPS scheme guard plus configurable 600s read timeout on both Responses-API servers (232, 244, 259, 265).
+- Attachment pipeline rewritten: six env-configurable caps with raised defaults, one shared per-turn budget derived from the real model window, stage priority so QA/review diff and explicit `context_paths` outrank the bundle and history, explicit per-attachment truncation reporting separate from `history_turns_dropped`, numbered parts with resume, and a marker-safe diff extractor that survives an embedded `END_GIT_DIFF` literal (262).
+- Risk-aware model routing added behind flags (246) then enabled as a baseline with a deterministic stage→tier mapping (plan/review→high, implement/qa/closure→low, missing→`BRAIN_MODEL`, unknown rejected by preflight) and explicit `risk_tier` precedence; prompt assembly separated into a byte-stable static prefix and a dynamic suffix exposed hash-only, provider-neutral (247, 261).
+- Manager-decision platform repaired and hardened end to end: install-once repo path, auto-extract on successful close, first reviewed profile promotion, fidelity/mode/scope/fingerprint fields, standing-vs-episode tags, sync-debt surfacing (230, 231); credential redactor word-edge fix (242); `DECISION_*` envs with `BRAIN_*` fallback (243); extract/record/recall crash repair (248); transcript character cap with loud cap validation (263).
+- Retrieval and evaluation: authority-ranked retrieval (decisions > memory > repo > web) with gather-then-narrow chunk assembly, and a scored eval harness reporting parse/grounding/rule/ZAC/QA-repair/cost/latency with caller-owned golden JSON; semantic XML validation added over the tolerant parser and the context-path resolver fixed to honour `project_root` (245, 249, 251).
+- Process enforcement: English-only reasoning plus the mandatory validate→translate→enrich→refactor→execute input pipeline (252); RTK-first verification wired structurally into the executor, task templates, and memory (250); an overnight F1-F29 gap reconciliation with tree-guard and diff-attach root repairs (238).
+- Tooling fixes: opencode-init retrofitted to a project-only config contract whose validator rejects global-only MCP/plugin keys (237, 239); 28 MCP tool descriptions audited for when-to-use lines, look-alike comparisons, and Hands-pull/Brain-quotes-paths wording (258).
+
+## Files Modified
+
+| File | Change |
+| ---- | ------ |
+| mcp-brain-bridge/server.py | per-project session resolver, no-global-write guards, lean-retry state note, empty-output/provider diagnostics, routing + prompt-cache split, shared attachment budget/parts/resume, marker-safe diff extraction, HTTPS guard + read timeout, preflight/capability/ledger wiring |
+| mcp-brain-bridge/preflight.py | new: mandatory request preflight (project_root, task/session id, Kanban path, stage) |
+| mcp-brain-bridge/capability.py | new: three-status capability manifest, required-tool blocking, `question` availability |
+| mcp-brain-bridge/transport_learning.py | new: unsupported-parameter classifier, one corrected retry, saga-scoped memory, escalation |
+| mcp-brain-bridge/session_ledger.py | new: session start fields, ordered phase checkpoints, pending→approved candidate index |
+| mcp-brain-bridge/authority_retrieval.py | new: authority-ranked retrieval, gather-then-narrow chunk assembly |
+| mcp-brain-bridge/eval_harness.py | new: parse/grounding/rule/ZAC/repair/cost/latency metrics; absolute-path ZAC + finite-value hardening |
+| mcp-brain-bridge/loop_guard.py | project_root threading and per-project hash scoping |
+| mcp-context-server/server.py | tree-guard `.git` boundary fix, over-cap signatures fallback, tool docstrings |
+| mcp-memory-server/server.py | when-to-use tool docstrings |
+| mcp-lint-server/server.py | fenced source-evidence carve-out + `analysis` Type lifecycle |
+| mcp-decision-server/server.py | B1/B2 hardening, `DECISION_*` envs, provider diagnostics, transcript cap + loud cap validation, HTTPS guard + read timeout |
+| mcp-decision-server/redactor.py | word-edge credential-leak fix + short-Bearer rule |
+| agents/cognitive-executor.md | supervised autopilot, review-approval relay, seat routing, `question` grant, input-validation matrix |
+| prompts/fragments/ | version 9.35.0 → 9.41.0; validation gate reorder, reviewer contract, RTK rule 3b, autopilot contract, English-only rule |
+| system-prompt.md | rebuilt deterministically through 9.41.0 |
+| docs/conventions.md | risk tiers T0/T1/T2, Lite fast-path rules |
+| docs/brain-bridge.md | routing baseline, prompt-cache split, attachment caps/parts/resume, new env rows |
+| docs/velocity.md | new: closeout velocity ledger |
+| docs/history/milestone-19-summary.md | new: milestone-19 compaction |
+| skill-templates/opencode-init/ | project-only contract + validator/golden/matrix; LSP/formatter shape correction |
+| skill-templates/audit-agents/SKILL.md | session-history gitignore rule for other projects |
+| skill-templates/telegram-issue-sync/SKILL.md | autopilot data-ask contract note |
+| skill-templates/*/SKILL.md | six skills gained manifest-aware `question`-channel wording |
+| .gitignore | `tasks/.sessions/` ignore; `.env.*` (with `!.env.example`) and `*.bak*` |
+| .env.example | DECISION block, routing knobs, HTTPS + read-timeout knobs |
+| tests/ | suite 331 → 686 green |
+| CHANGELOG.md | per-task Parse-Then-Append entries |
+| tasks/.sessions/ | migrated per-project Brain session transcripts (230-234) |
+
+## Criteria Met
+
+| Task | Acceptance Criteria | Status |
+| ---- | ------------------- | ------ |
+| 229 | Archive step first; CHANGELOG `[Unreleased]` empty under `[9.35.0]`; suite + docs-sync + prompt-sync pass; diff staged via MCP; push script written | ✅ Met |
+| 230 | Issue 8 body + all comments verbatim; B1/B2/P1 captured; sync comment on issue; no per-call path prompt; auto-capture evidence; first promotion lands | ✅ Met |
+| 231 | Real close-run shows `extract_session_decisions` firing; H1/H2/H3 fixed with regressions; decision suite exit 0 | ✅ Met |
+| 232 | Empty-output root cause documented; tool returns retry instruction; actionable MCP lints; suites exit 0 | ✅ Met |
+| 233 | Plan shown and awaited before non-trivial work; Lite runs without pauses; seat routing; bounded QA/review; tests + suite exit 0 | ✅ Met |
+| 234 | Same number in different roots → different paths; same root → same path; no cross-project writes; HQ folders migrated losslessly; suite exit 0 | ✅ Met |
+| 235 | Relay loop documented/working; `tasks/.sessions/` gitignored with zero tracked files; audit skill updates other projects; Brain consulted | ✅ Met |
+| 236 | Lean retry carries path/status/diff hash; regression proves state note; 234 folder byte-identical; manifest hashes match | ✅ Met |
+| 237 | Project-only config; no project-level MCP/plugin; skill/matrix/golden/validator consistent; validator rejects global-only; lint + CHANGELOG | ✅ Met |
+| 238 | Safe gaps fixed with evidence; T2 items deferred, none executed; QA + reviewer verdicts; staged, in qa, no commit/close | ✅ Met |
+| 239 | Validator accepts corrected golden, rejects wrapper shape; registry fully green; CHANGELOG present; staged, in qa | ✅ Met |
+| 240 | Note no longer orders Brain `read_file`; UNVERIFIABLE-not-REJECTED for unseen scope; pull path to Hands; tests + QA | ✅ Met |
+| 241 | History keyed by root+task_id with test; extraction fires at close with lint gate; rtk mandate in prompt; context ledger + over-cap fallback | ✅ Met |
+| 242 | No secret string passes `verify_clean`; suite exit 0; QA + reviewer verdicts recorded | ✅ Met |
+| 243 | All 4 `DECISION_*` envs with `BRAIN_*` fallback; both keys absent fails closed naming both; docs + example; suite exit 0 | ✅ Met |
+| 244 | Orphaned hunks verified as nested-effort scope only; focused + full suites green; staged, in qa; QA + reviewer verdicts | ✅ Met |
+| 245 | Context-path bug reproduced/root-caused/fixed/proven; semantic XML validation added; suite exit 0 | ✅ Met |
+| 246 | Tier resolves via one pure function; default reproduces current behavior; env overrides per tier; no secrets in cache keys; suite exit 0 | ✅ Met |
+| 247 | Static prefix byte-stable; dynamic suffix carries variation; split observable without leaking; inert = no wire change; suite + lint + CHANGELOG | ✅ Met |
+| 248 | Extract returns candidates or clean empty; record persists + returns id; profile consult predictable with/without sample; regressions; suite exit 0 | ✅ Met |
+| 249 | Authority order proven by tests; gather-then-narrow chunks; eval reports all metrics; goldens as JSON; suite exit 0 | ✅ Met |
+| 250 | Executor names RTK default runner; task files prescribe `rtk test`; memory holds RTK-first rule; suite exit 0 via `rtk test` | ✅ Met |
+| 251 | Absolute-path git flagged by ZAC scanner; boolean/non-finite cost latency excluded; suite exit 0 | ✅ Met |
+| 252 | No non-English prose in prompt rules; input-validation pipeline mandatory; deterministic prompt rebuild; suite exit 0 | ✅ Met |
+| 257 | All bundled issue criteria (capability preflight, transport learning, request preflight, session ledger/decision persistence/lint carve-out); archive traceability; suite green | ✅ Met |
+| 258 | Each tool states when to call it; look-alike pairs differ; no behavior change; runbook Hands-pull/Brain-quotes-paths; private helper hidden; suite evidence | ✅ Met |
+| 259 | Provider diagnostics every turn; budget exhaustion hints effort/cap not lean retry; refusal/error verbatim; xhigh+16k guarded; mirrored to decision server; issue 20 closed | ✅ Met |
+| 260 | Both servers explicit cap + effort defaults; `visible_tokens` logged; effort warning; `question` granted; gitignore hardened; skills point at question; suite exit 0 | ✅ Met |
+| 261 | Hard stage→high, light→low, missing→`BRAIN_MODEL`, unknown rejected; explicit `risk_tier` wins; off = single model; ledger records model+tier; docs + tests; global sync | ✅ Met |
+| 262 | Env-configurable caps ≥ old defaults; 60k context file untruncated; shared budget; QA/review priority; separate truncation report; back-compat history name; numbered parts; <250KB no UNVERIFIABLE; compact transcript; append-only; marker-safe extraction | ✅ Met |
+| 263 | Prompt bounded by env cap; explicit truncation note with dropped size; malformed/non-positive cap fails loud; temperature reader fails loud; request shape conformant; regressions; decisions extracted/saved | ✅ Met |
+| 264 | Bundle reads passed project root not install dir; missing markers correct; file-pull tools resolve active root; regression; suite green | ✅ Met |
+| 265 | `http://` non-loopback rejected naming env key; loopback allowed; https passes; read timeout configurable 600s default, malformed fails loud; connect/write/pool unchanged; `.env.example`; suite exit 0 | ✅ Met |
+
+## Individual Task Summaries
+
+### Task 229: Release v9.35.0 with milestone-19 archive
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Cut release v9.35.0 by archiving the 5 completed tasks into milestone-19 and moving them to archive first, then closing CHANGELOG `[Unreleased]` under `[9.35.0]` and verifying suite, docs-sync, and prompt-sync gates. Staged 9 release paths through the sanctioned MCP tool, wrote an executable push script for the Manager, and logged a benign stale-memory audit. Closed on Manager approval with features committed via hash `933488e`.
+
+### Task 230: Manager-decision improvements synced with issue 8
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Synced the local task with GitHub issue 8 and implemented B1 (install-once decision repo path), B2 (auto-extract on successful close), and P1 (first reviewed profile promotion). B1 resolved via shell/`.env` + SKILL + server docstring because per-user path resolution breaks shared config; auto-record stayed behind the confirm gate. Manager approved the promotion ("Approve merge clean migrate"), landing `manager_profile.md` in the personal repo pending his push; 98 decision + 90 adjacent tests passed.
+
+### Task 231: Manager-decision follow-up — B2 live proof plus fingerprint hardening
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Proved B2 auto-capture on a real close and closed the H1/H2/H3 fingerprint edge notes from the parent review. H1 coerces non-dict `verbatim_quote`/`extracted_decision`, H2 skips non-dict stored records in fingerprint lookup and index rewrite, and H3 treats explicit `None` optionals as unset so safe defaults apply. `extract_session_decisions(231)` fired and returned `[]` loudly with nothing written; suite 101 passed after 3 new regression tests.
+
+### Task 232: Brain empty-output root cause plus MCP-side retry hint and stronger lints
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Root-caused intermittent empty Brain output to `parse_responses_text` returning `""` on a missing/non-list `output` with no guard, then shipped `EMPTY_OUTPUT_RETRY`, a `_PROMPT_WARN_CHARS=60000` pre-call warning, a choke-point guard that keeps status REPORT, and actionable MCP lints. A regression test covers the empty case; full suite 345 passed. The only review change was removing a standing task id from executor prose per the task-number discipline.
+
+### Task 233: Supervised autopilot with plan approval and seat routing
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Replaced fire-and-forget autopilot with supervised autopilot: discovery feed, mandatory plan-approval pause, seat routing, bounded QA/review loops, and risk tiers with max-3-tries escalation. Implemented across `agents/cognitive-executor.md`, `mcp-brain-bridge/server.py` (bundle total cap + plan-verdict validator), `docs/conventions.md`, and the telegram skill, mirrored into the shipped prompt 9.35.0→9.36.0. Postfix hardening added word-bound verdict fields and suffix-safe truncation; suite 350 passed.
+
+### Task 234: Brain sessions per project under tasks sessions dir
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Stopped Brain task history bleeding across projects by storing sessions at `<project>/tasks/.sessions/` behind a shared `_project_root()` resolver with a legacy read-through fallback. Root cause was the bridge building one global path from a bare task number, so same-numbered tasks shared a folder. Migrated HQ folders 230-233 with sha256-verified copies plus 7 tests, then closed after a no-global-write hotfix; suite 357 passed.
+
+### Task 235: Review approval relay to Brain plus gitignore for session history
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Closed the review-approval loop (Hands relays technical approval → Manager accepts → Brain Programmer emits one final XML) using exact-word gates, a bare-"approved" exception scoped to the relayed question, a qa + `PO_REVIEW_PENDING` double gate, and single issuance with failure-only re-call. Also gitignored `tasks/.sessions/` and extended the audit-agents skill (repo template + global copy) with an idempotent session-history rule. Three QA rounds; prompt regenerated 9.37.0→9.37.2; suite 357 passed.
+
+### Task 236: Fix lean-retry context loss and migrate global 234 session folder
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Closed the two session-context gaps proven by the 235 transcript audit: lean retries now carry a tiny `_task_state_note()` (task path + status + diff hash) so the Brain cannot judge a stale file version, and the global task-234 folder moved into `tasks/.sessions/234` with matching sha256 hashes. The hint stayed pure while the caller does I/O; bridge file 140 + full suite 357 passed.
+
+### Task 237: Fix opencode-init skill to be project-only
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Retrofitted the opencode-init skill to generate project-only `opencode.json` (formatter, LSP guidance, instructions, permissions) and ban project-level MCP/plugin keys, which install globally. Updated SKILL.md, runtime-matrix, golden example, and the validator to reject global-only keys with global-path errors while keeping ZAC/invented-value/$schema gates. Manager approved; validator golden exit 0, negative fixture exit 1 as designed.
+
+### Task 238: Fix all gaps overnight
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Overnight full-autopilot sweep: reconciled F1-F29 against disk with grep-verified cites and per-item verdicts, fixed X1 XML tolerance, X2 roster pointer, X3 queue cap, X4 adversarial tests, and the tree-tool dot-guard, and deferred T2 destructive items explicitly. A QA hotfix hardened `_extract_unclosed_tail` and `is_ignored`, and a why-fix decoupled diff-attach gates from `include_bundle` and threaded `project_root` through the attach helpers, then surfaced inline UNAVAILABLE/EMPTY remedies. Suite 374 passed plus 4 pre-existing registry failures.
+
+### Task 239: opencode-init LSP formatter shape correction
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Landed the uncommitted opencode-init shape correction: flat LSP map, named formatter map, `env` not `environment`, and rejection of the stale `language-server` wrapper. Hands verified (not authored) the Manager's worktree changes, confirmed the registry suite went red→green (20 passed), and left QA/review to the bridge. Closed on the exact "Close task" word.
+
+### Task 240: Bridge truncation note orders Brain to read_file it cannot call
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Fixed the `[changed-hunks]` truncation note that ordered the Brain to `read_file` despite QA turns having zero tool calls, causing round-1 `QA_REJECTED` on unseen scope. The note now marks unseen scope UNVERIFIABLE (never REJECTED) and routes the pull to the Hands, who quote needed paths. Prompt-wording-only change with a new assertion test; full suite 381 passed.
+
+### Task 241: Bridge follow-up cross-project bleed decision-extract rtk mandate
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Closed issue 15's two bridge bugs and two process gaps: legacy history/fed-context fallback now applies only when the resolved root IS the global (fixing cross-project bleed), decision auto-extraction runs at close behind a `validate_closure_checklist` gate, and the rtk mandate was added to fragment 09 with version 9.38.0. Extended with a per-turn context-utilisation ledger and an over-cap signatures fallback in the context server. Suite 389 passed; QA and reviewer approved.
+
+### Task 242: Fix decision-redactor word-edge credential leak (B1)
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Closed the credential-leak path in `redactor.py`: the `\b` word edge let `BRAIN_API_KEY=...` env-style names and short `Bearer` tokens pass `verify_clean`, so a `(?<![A-Za-z0-9])` edge plus a digit-gated short-Bearer rule now catch them while leaving `topsecret=x` untouched. Reproduce-first via an inline old-vs-new regex proof; 4 new tests, decision suite 105 passed. The disputed QA F1 was refuted (the `-` sits inside the token class) and closure scoping kept only 242 files in its commit.
+
+### Task 243: DECISION_* env support for decision server
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Gave the decision server its own `DECISION_API_BASE`, `DECISION_API_KEY`, `DECISION_MODEL`, and `DECISION_REASONING_EFFORT` envs with `BRAIN_*` fallback and fail-closed behavior naming both key names when neither is set. Documented the contracts in `.env.example` and set the live `.env` (mode 600, values never printed). Three new contract tests plus two hermeticity fixes; suite 396 passed.
+
+### Task 244: Bridge nested reasoning effort fix
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Tasked the orphaned Bridge `reasoning.effort` fix so it was verified and closable instead of riding the worktree unowned. Confirmed the worktree hunks were nested-effort scope only (a live 400 forced flat `reasoning_effort` → nested `reasoning:{effort}`) and kept sibling task-243 files out. Focused 157 + full 400 passed; QA and reviewer approved; closed on "Approved for closure".
+
+### Task 245: Harness upgrade to professional software-factory plus context-path delivery fix
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Fixed the Brain context-path delivery bug where `build_paths_attach` always used `_workspace_root` and ignored `project_root`, then added a semantic XML gate (`validate_hands_xml_blocks`) on top of the tolerant parser. Discovery ran four read-only subagents; TDD red-green added 9 tests then 11 more after QA and review rejections (incomplete phase sets, non-path-like root, bare-word phase matching). Suite 415 passed; routing, cache, retrieval, and eval deferred to follow-up tasks.
+
+### Task 246: Risk-aware model routing for the Brain bridge
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Added risk-aware model routing behind `BRAIN_RISK_ROUTING_ENABLED` (default off) with a pure `resolve_routed_model` and `BRAIN_MODEL_LOW/HIGH` overrides, reproducing today's single-model behavior exactly when inert. Consulted stored decisions and a two-seat Brain plan first; discovery confirmed no router existed and tiers were process-policy only. 8 new tests; suite 423 passed with zero default behavior change.
+
+### Task 247: Stable prompt-cache separation for Brain turns
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Split every Brain turn prompt into a byte-stable static prefix and a dynamic suffix so repeated turns share prefix bytes, exposing the split hash-only via the result and ledger with no provider-specific cache params. A QA rejection drove a hotfix: a separate `failsafe_text` slot, label length-prefixing (schema v2), post-truncation derivation, and tuple-keyed cache. Suite 434 passed; the reviewer's only residual was an unsynchronized cache lookup, deferred as non-blocking.
+
+### Task 248: Manager-Decision Tools Repair (extract + record failures)
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Repaired the broken manager-decision tool chain: `extract_session_decisions` drops malformed non-string-tradeoffs candidates with a stderr note instead of crashing, `record_manager_decision` raises field-named `ValueError` on non-string leaves before any write, and `query_manager_decisions` skips tampered records. TDD red-green (6 tests) plus two QA-hotfix rounds (falsey alternatives laundering, nested leaf validation). Suite 452 passed.
+
+### Task 249: Memory Authority Retrieval plus Eval Harness
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** Added authority-ranked retrieval (`authority_retrieval.py`) and a scored eval harness (`eval_harness.py`) with caller-owned golden JSON cases. Manager decisions outrank project memory, then repo files, then web; retrieval gathers the top 20 candidates then narrows to 5 with chunk overlap; metrics cover parse, grounding, rule, ZAC, QA-repair, cost, and latency. A QA hotfix kept missing `qa_repairs` as `None` rather than coerced 0; suite 491 passed.
+
+### Task 250: RTK Output-Trimming Structural Wiring
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Made RTK output-trimming structural instead of advisory after the Manager found ~0% usage: extended RULE 3b operationally, added an executor Verification Runner policy and RTK-prefixed evidence example, changed both task templates, normalized four normative prescribers, and stored the RTK-first rule in memory. Version 9.39.0→9.40.0 with byte-identical double rebuild; suite 502 passed via `rtk test`.
+
+### Task 251: Eval Harness Residual Hardening
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Hardened the eval harness against the two low residuals deferred at review: `_op_is_zac` now basenames absolute paths and handles `sudo` wrappers, and `_is_finite_number` rejects booleans and non-finite cost/latency values. TDD 6 tests (5 RED, 1 already-clean guard); focused eval+golden 30/30 and full suite 508 passed via `rtk test`.
+
+### Task 252: English-Only Reasoning Plus Input-Validation Enforcement
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Enforced English-only thinking/reasoning/responses and the priority-one validate→translate→enrich→refactor→execute input pipeline. Discovery found contradictory "clarify in Manager language" prose with zero test gates; reordered the validation gate to step 0.5, replaced the language lines with simple English, added the quoted-source-only exception, and added `prompt-refactor` to the executor matrix. Version 9.39.0; suite 499 passed.
+
+### Task 257: github-open-issues-bundle
+
+- **Type:** feature
+- **Source:** manager
+- **Reasoning:** META bundling open GitHub issues 16-19 into one all-or-nothing diff: WS1 transport request preflight, WS2 capability manifest with required-tool blocking, WS3 transport-failure learning with one corrected retry, and WS4 session ledger + taskless decision persistence + lint carve-out and `analysis` Type. Four reviewer rounds triaged findings against disk (three refuted with evidence) and regenerated the prompt 9.40.0→9.41.0. Suite 596 passed; closed on "Approved for closure".
+
+### Task 258: MCP tool description usability fixes
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Made 28 MCP tool descriptions usable: added when-to-use lines and look-alike comparisons, clarified path-return surprises, corrected the runbook to Hands-pull/Brain-quotes-paths, and hid the private `_note_checkpoint` from the tool list. Docs-only with no user-facing behavior change; bridge 191 plus adjacent suites green. Closed on "Approved for closure".
+
+### Task 259: brain_turn EMPTY_OUTPUT_RETRY loop max_output_tokens exhaustion misreported
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Fixed `EMPTY_OUTPUT_RETRY` misdiagnosis when the Responses API returns `status=incomplete` / `reason=max_output_tokens`: added provider diagnostics (`debug.provider`) on every turn and ordered terminal classification error→refusal→budget→flake, so budget exhaustion hints lower effort or raise tokens instead of a lean retry. Mirrored the treatment to the decision server per Manager order; a QA round added 4 hotfix fixes plus 5 regressions. Suite 621 passed; issue 20 commented and closed.
+
+### Task 260: Responses-API reasoning budget fix, question-tool grant, and repo hygiene
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Shipped a working-tree change set as one reviewed unit: reasoning-budget starvation fixed on both servers (bridge `medium`/32768, decision `high`/16384), `visible_tokens` logging, a warn-only effort-support guard, the native `question` tool granted to the executor, `.gitignore` hardened with a secrets-bearing env backup relocated, and manifest-aware question wording in six skills. QA rejection repairs hardened effort coercion and ignore patterns; suite 626 passed.
+
+### Task 261: Enable the risk-aware Brain model routing baseline
+
+- **Type:** improvement
+- **Source:** manager
+- **Reasoning:** Enabled the risk-aware routing baseline: `BRAIN_RISK_ROUTING_ENABLED` defaults on, per-tier model code defaults replace empty strings, and a deterministic stage→tier mapping runs (plan/review→T2 high; implement/qa/closure→T0 low; missing→`BRAIN_MODEL`; unknown rejected by preflight). Explicit `risk_tier` still wins and the ledger records the effective tier/model, with a three-state unset/blank/value override contract. docs and `.env.example` updated; suite 632 passed after two QA contract repairs and global sync.
+
+### Task 262: Brain Bridge attachment caps prevent any seat from seeing a full change set in one turn
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Fixed the bridge's inability to deliver a full change set: env-configurable caps with raised defaults, one shared per-turn budget derived from the real window, stage priority so QA/review diff and `context_paths` outrank bundle and history, explicit `attachments_truncated` separate from `history_turns_dropped`, numbered parts with resume, and a marker-safe `_diff_block_end`. Folded in R3: compact stored-attachment markers and an append-only transcript. Four review rounds fixed loud cap failure, wrapper overhead pricing, and group-total enforcement; suite 660 passed.
+
+### Task 263: Decision server sends the whole session transcript unbounded and swallows a malformed output-token cap
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Bounded the decision server's extraction prompt with `DECISION_TRANSCRIPT_MAX_CHARS` (default 131072, blank-means-unset) plus an explicit dropped-size truncation marker, and made `_get_decision_max_tokens()` and `_get_decision_temperature()` fail loudly instead of falling back. The audit first established that most of task 262 did not apply (no history or attachments). A docs rejection added the `.env.example` DECISION block; suite 665 passed and the Manager's decisions were re-extracted and saved.
+
+### Task 264: Brain Bridge resolves the active project root for the context bundle and file-pull tools
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Fixed issue 24: the auto-context-bundle and file-pull tools resolved against the install dir instead of the active project root. `_workspace_root()` now tries `BRAIN_WORKSPACE_ROOT` → `BRAIN_PROJECT_ROOT`/cwd walk-up → install dir as a loud last resort; `_build_context_bundle`, `read_file`, and `grep_files` accept `project_root`, and a one-off turn re-pins an explicit existing root. 5 regressions; bridge 243 + adjacent 411 passed.
+
+### Task 265: Harden Responses API transport (HTTPS guard + configurable read timeout)
+
+- **Type:** bug
+- **Source:** manager
+- **Reasoning:** Hardened Responses-API transport in both servers: `_https_guard` fails closed on any non-HTTPS base naming the env key (loopback HTTP allowed) and a configurable read timeout defaults to 600s with a loud parse failure, while connect/write/pool stay unchanged. Also fixed test hermeticity so the developer's real `.env` no longer leaked into assertions. Suite 686 passed; R3-R7 remain deferred.
```
<!-- END_GIT_DIFF -->
