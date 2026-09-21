# Task 267: docs: manager-decisions MCP tool schemas and usage contract for agents

**File:** `tasks/qa/267-manager-decisions-mcp-tool-schemas.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Write `docs/manager-decisions.md`: the source-verified schema and usage
contract for the six `manager_decisions` MCP tools, so any agent can call
them correctly on the first try. Every claim is grounded in the server
source (`mcp-decision-server/server.py`, `redactor.py`, `detector.py`) with
`file:line` citations. Cross-link the new doc from `README.md` and
`docs/setup.md`, record the source-versus-skill divergences in a Doc drift
section marked "reported, not fixed", and log a CHANGELOG entry. This
closes GitHub issue #25.

## Manager's Notes

- Source issue: <https://github.com/mokhtarabadi/cognitive-lead-hq/issues/25>
  — the issue body already carries a draft; it is a starting point, NOT
  ground truth.
- The issue body claims the extraction model resolves as
  "`DECISION_MODEL`, else `BRAIN_MODEL`". Source-verified discovery proved
  this FALSE: `DEFAULT_DECISION_MODEL = "gpt-6-astra"` (`server.py:195`) and
  only `DECISION_MODEL` overrides it (`server.py:265-275`). `BRAIN_MODEL` is
  never read by this server. The new doc must correct this explicitly.
- Drift items are "reported, not fixed": do NOT edit `server.py`,
  `redactor.py`, `detector.py`, or any skill file in this task.
- Documentation-only change. No application code (AGENTS.md guardrail).
- Follow `sop-maintenance` (Markdown only, CHANGELOG sync, no global state
  files).
- Canonical precedent for tone and structure: `docs/brain-bridge.md`.

## Local TODOs

- [x] Re-read the six tool definitions and validation paths in `mcp-decision-server/server.py`; confirm every citation line number before writing
- [x] Write `docs/manager-decisions.md` (overview, store resolution, the six tool schemas, shared field contract, pitfalls, workflow, doc drift)
- [x] Add cross-links in `README.md` (Documentation list + repository tree) and `docs/setup.md` (MCP Servers table)
- [x] Add the `[Unreleased]` CHANGELOG entry
- [x] Run `lint_markdown` on the new doc and `lint_task_file` on this task
- [x] Run the RTK-prefixed full test suite plus `scripts/check_docs_sync.py`; record evidence

## Acceptance Criteria

- [x] `docs/manager-decisions.md` exists and documents all six tools (`extract_session_decisions`, `record_manager_decision`, `query_manager_decisions`, `get_sync_status`, `get_manager_profile`, `propose_profile_evolution`) with exact signatures, argument names and types, return shapes, side effects, and failure modes
- [x] Every factual claim carries a `file:line` citation into `mcp-decision-server/`; the issue's `BRAIN_MODEL` claim is explicitly corrected (only `DECISION_MODEL` is read, default `gpt-6-astra`)
- [x] A Doc drift section lists the source-versus-`SKILL.md` divergences as "reported, not fixed", and no server source or skill file is modified by this task
- [x] The store-resolution order, the eight-value category enum, the three optional enums (`fidelity`/`mode`/`scope`), and the six required fields are documented exactly as the source enforces them
- [x] `README.md` and `docs/setup.md` link to the new doc
- [x] `CHANGELOG.md` carries an `[Unreleased]` entry describing the new doc
- [x] The RTK-prefixed full suite exits 0; `scripts/check_docs_sync.py` reports OK; `lint_markdown` on the new doc and `lint_task_file` on this task both pass

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** all tests pass
- **Actual result:** Full suite green — `rtk test` summarized **686 passed, 10 warnings in 5.17s**. Supporting gates: `lint_markdown` on `docs/manager-decisions.md` → passed; `lint_task_file` on this task file → passed; `uv run scripts/check_docs_sync.py` → `docs-sync: OK` (two pre-existing warn-only orphan scripts: `scripts/fetch-opencode-docs.py`, `scripts/repomd`).
- **Exit code:** 0

> Verification runner rule: `uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** The issue body contains an unverified claim (`BRAIN_MODEL` override) and stale references; copying it instead of re-reading source would ship a wrong contract. Separate risk: `file:line` citations rot when `server.py` changes, so every citation is re-confirmed at write time and the doc states it is pinned to the current revision.
- **Rollback plan:** Revert the single docs commit (`git revert <hash>`) — the change touches only `docs/manager-decisions.md`, `README.md`, `docs/setup.md`, and `CHANGELOG.md`, so no code or data path is affected.

---

## Execution Log & Reasoning

**Pipeline mode:** full-automatic autopilot, authorized by the stored standing
order `manager/full_automatic_mode` (set 2026-09-17) and ruling
`DEC-20260917-009`/`DEC-20260917-013` (a reviewer technical `APPROVED` with
`PO_REVIEW_PENDING` satisfies the closure gate), plus `DEC-20260920-001`
(autopilot plans through the Brain, then implements without a separate plan
approval pause). ZAC holds: nothing is committed except through the MCP tools.

**Planning gate.** Brain plan turn under `task_id=267`, `stage=plan`, seat
Software Architect (the TITLE+BODY words "schema" and "contract" fire the
`schema|contract|migration|quota|index|API design` trigger). Blueprint:
"Manager-Decisions MCP Contract Doc" — in scope F1 the new doc, F2 the README
cross-link, F3 the `docs/setup.md` cross-link, F4 the `[Unreleased]` CHANGELOG
entry; out of scope any server source, any `SKILL.md`, and any behavior change.

**Discovery.** All six tool anchors, the store-resolution helper, the
validator, the redactor and the detector were read from source with line
numbers re-confirmed immediately before writing
(`server.py` 1258/1259, 1550/1551, 1642/1643, 1745/1746, 1759/1760,
1784/1785; `mcp.run(transport="stdio")` 1821). No claim in the new page rests
on the issue body alone.

**Changes.**

1. `docs/manager-decisions.md` (new, 10 sections): purpose and scope with a
   pinned revision note; server identity and transport; store resolution
   including the fail-closed explicit-path behavior; six-tool quick reference
   plus the enum sheet; per-tool detail for all six; the shared record field
   contract; an agent pitfalls table; a recommended workflow; the doc-drift
   table; and the could-not-verify list.
2. `docs/setup.md` — the `mcp-decision-server` row in the MCP Servers table now
   links to the new page.
3. `README.md` — the Documentation list gained the new page, and the repository
   tree gained both `docs/manager-decisions.md` and the previously missing
   `mcp-decision-server/` stanza.
4. `CHANGELOG.md` — one `[Unreleased]` / `### Added` bullet describing the page,
   the correction, and the six reported-not-fixed drift items.

All four files were then reformatted with the repo's Prettier.

**Correction shipped.** The issue body's "`DECISION_MODEL`, else `BRAIN_MODEL`"
claim is false. Only `DECISION_MODEL` overrides
`DEFAULT_DECISION_MODEL = "gpt-6-astra"` (`server.py:196`, `:265-275`);
`BRAIN_MODEL` is read nowhere in `mcp-decision-server/`; the deliberate
non-fallback target is `PERSONA_MODEL` (`server.py:268`).

**Assumptions.**

- **A1** — The doc-drift items ship as "reported, not fixed" and no source or
  skill file is touched. Reason: the task's Manager's Notes and the Brain
  Blueprint both scope the change to documentation only, and AGENTS.md forbids
  widening work beyond the request.
- **A2** — The Related section points at `skill-templates/manager-decision/SKILL.md`
  rather than `.opencode/skills/manager-decision/SKILL.md`. Reason: this repo
  holds only `sop-maintenance` under `.opencode/skills/`; the manager-decision
  skill exists in-repo only as a template.
- **A3** — Citations are pinned to commit `0183433` and dated 2026-09-21 in the
  page header. Reason: line numbers shift when `server.py` changes, so the page
  states its revision rather than implying permanence.

**Verification.** `rtk test … pytest tests/ -q` → `686 passed, 10 warnings in
5.17s`, exit 0. `lint_markdown docs/manager-decisions.md` → passed.
`lint_task_file` → passed. `uv run scripts/check_docs_sync.py` → `docs-sync: OK`,
exit 0. The two orphan warnings it prints (`fetch-opencode-docs.py`,
`repomd`) are pre-existing and warn-only by design.

**Not done in this task (by scope).** No fix for any of the six drift items, no
edit to `server.py`/`redactor.py`/`detector.py`, no edit to any `SKILL.md`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b1c79d8..a0b6461 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Added
+
+- **Manager-decisions MCP contract doc (Task 267, fixes GitHub issue 25):** new `docs/manager-decisions.md` is the source-verified agent usage contract for the six `manager_decisions` tools. It documents server identity and stdio transport, the `_repo_root()` store resolution order including the fail-closed explicit-path behavior, a six-tool quick-reference table, per-tool sections (signature, arguments, return shape, side effects, failure modes) for `extract_session_decisions`, `record_manager_decision`, `query_manager_decisions`, `get_sync_status`, `get_manager_profile` and `propose_profile_evolution`, the shared decision-record field contract (six required fields, the closed eight-value `category` enum, the `fidelity`/`mode`/`scope` enums, fingerprint and id shapes, server-stamped `active_root`/`store_mode`), an agent pitfalls table, a recommended workflow, a doc-drift table and a could-not-verify list. Every factual claim carries a `mcp-decision-server/*.py:line` citation pinned to commit `0183433`. The issue's claim that the extraction model resolves as `DECISION_MODEL` else `BRAIN_MODEL` is corrected: `BRAIN_MODEL` is never read by this server, `_get_decision_model()` returns `DEFAULT_DECISION_MODEL` (`gpt-6-astra`) unless `DECISION_MODEL` is set, and the deliberate non-fallback target is `PERSONA_MODEL`. Six drift items are reported, not fixed: the seven-of-eight category list in the extraction prompt, the undocumented required `project_name`, the uncapped `query_manager_decisions` result set, the dead `_SCRUB_FIELDS` constant, the push-command mismatch with the skill text, and the stale `detector.py` docstring line numbers. No server source and no skill file was modified. `README.md` and `docs/setup.md` link to the new page, and the README repository tree gains the previously missing `mcp-decision-server/` entry. Full suite: **686 passed** (exit 0); `scripts/check_docs_sync.py` reports `docs-sync: OK`.
+
 ## [9.41.0] - 2026-09-20
 
 ### Added
@@ -24,11 +28,11 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Decision follow-up hardening H1/H2/H3 + B2 live proof (Task 231):** fingerprint path now tolerates a stray string `verbatim_quote`/`extracted_decision` (H1), skips tampered non-dict store files in both the duplicate scan and the index rewrite instead of crashing (H2), and treats explicit `None` optionals as unset so safe defaults still apply (H3). B2 live evidence: `extract_session_decisions(231)` fired at close handling and returned `[]` loudly (no session transcript in headless run — nothing queued, nothing written). 3 new regression tests. Full decision suite: **101 passed**.
 - **Brain empty-output retry hint + prompt-size warn (Task 232):** `mcp-brain-bridge/server.py` no longer returns a silent blank REPORT — root cause confirmed in code: `parse_responses_text` yields `""` on missing/non-list output and `brain_turn` forwarded it with no guard. A single choke-point guard now substitutes the machine-readable `EMPTY_OUTPUT_RETRY` hint (fixed token, lean-retry shape: same task_id, `include_bundle=false`, escalate if still empty; verdict content never invented, status stays REPORT so old callers keep working), plus a stderr advisory when the prompt exceeds 60k chars (oversized prompts correlated with both observed flakes). `agents/cognitive-executor.md` Empty-output clause now names the token. 6 new offline tests (hint contract, missing/None/whitespace payloads, normal passthrough, stderr warn). Full suite: **345 passed**.
 - **Supervised autopilot with plan approval and seat routing (Task 233):** `agents/cognitive-executor.md` gains a supervised plan-approval section (discovery feed → Brain plan → one approval pause → seat-routed implementation; Relay questions and hard blockers are the only other interrupts), a Seat Check trigger-citation line, a goal-pause carve-out for plan approval, and generous lock-word recognition. `mcp-brain-bridge/server.py` gains a 150 KB total bundle cap (truncate/skip with notes) and a text `validate_plan_verdict` checker (5 fields; cites need path:line shape). `docs/conventions.md` gains risk tiers T0/T1/T2 plus a 3-tries-then-escalate contract. `skill-templates/telegram-issue-sync/SKILL.md` folds the GitHub-preference data question into the planning turn (repo + global copies). Shipped prompt rebuilt to 9.36.0 with a Supervised Autopilot Contract bullet (authority stays in the executor file). 5 new offline bridge tests. Full suite: **350 passed**. Postfix: verdict checker uses word-bound field matching (stub text inside longer words no longer validates), bundle truncation reserves suffix length so the total never exceeds the cap, contract bullet reworded to a single plan-approval pause.
- - **Brain sessions per project, legacy global read-through (Task 234):** `mcp-brain-bridge/loop_guard.py` gains `project_sessions_root()` (explicit override → param/`BRAIN_PROJECT_ROOT`/`BRAIN_WORKSPACE_ROOT` → cwd walk-up to a `tasks/` dir → legacy global fallback) plus `legacy_sessions_root()`; `server.py` threads an optional `project_root` through `_sessions_root`, `_transcript_path`, `_fed_context_path`, `load_history`, `append_turn`, `save/load_fed_context`, and `brain_turn` — writes always land per project under `tasks/.sessions/<id>/`, while reads fall back to the legacy global dir with a loud stderr note when the per-project file is missing. HQ folders 230-233 migrated from the global store into `tasks/.sessions/` with a sha256 manifest (`/tmp/migrate-234-manifest.json`), globals kept as fallback. 4 new offline regression tests. Full suite: **354 passed**. Hotfix: no-global-write (fallback writes reroute to `cwd/tasks/.sessions` with stderr warn), package-then-plain sibling import, per-project loop-guard hashes with legacy read fallback, per-turn sessions-root stderr line, 3 more tests (T5-T7). Full suite: **357 passed**.
-  - **Review-approval relay + session-history gitignore (Task 235):** `agents/cognitive-executor.md` gains a Review-approval relay rule (technical approval → verbatim relay, file stays in qa; only the exact words "Approved for closure"/"Close task" count; Hands re-calls Brain Programmer once for a single final-closure XML and executes it exactly once) plus a relay line in the Code Reviewer roster row. `prompts/fragments/06-personas.md` Code Reviewer contract now routes closure through the relayed Programmer XML instead of emitting it directly. Shipped prompt rebuilt to 9.37.0. Global `audit-agents` skill Plugin Runtime-State rule now covers Brain session history (`tasks/.sessions/` added only after confirming the dir exists). Hotfix: relay tightened (bare-approved counts only as the next message answering the relayed question; explicit never-list incl. yes/done/okay/looks-good/emoji/silence; qa + PO_REVIEW_PENDING double-gate; single issuance with failure-only re-call; autopilot self-decision never satisfies); repo `skill-templates/audit-agents/SKILL.md` template extended too (both occurrences) so the rule ships in-repo. Second hotfix: reviewer contract mirrors the executor relay exactly (bare-approved exception + full never-list incl. okay/done/fine/looks-good/emoji-only + autopilot bar), audit clause gains a duplicate-line guard (check first, add only if missing), shipped prompt rebuilt to 9.37.2.
-  - **Lean-retry state note + migrate Task 234 session (Task 236):** `mcp-brain-bridge/server.py` `_empty_output_hint` and the executor Empty-output clause gain a state-freshness sentence: a lean retry drops the bundle, so if the answer judges stale or missing context, re-run ONCE with the full bundle plus diff before escalating (proven by the 235 turn-3 stale verdict). Task 234's global transcript + fed context migrated into `tasks/.sessions/234/` with sha256-verified manifest. 4 new regression assertions (stale sentence, state line, 2 unknown fallbacks). Full suite: **357 passed**.
-  - **opencode-init project-only contract (Task 237):** `skill-templates/opencode-init/` now generates project-only `opencode.json` — allowlist `$schema`, `default_agent`, `instructions`, `formatter`, `lsp` (guidance only), `permission` (ZAC denies intact); `mcp` and `plugin` are global-only (install in `~/.config/opencode/opencode.json` or a plugins dir) and are omitted on generate, rejected on validate. SKILL.md stops asking for MCP env keys/plugin choice and writes a global-install note instead; `references/runtime-matrix.md` V1 row + MCP/plugin global-only rows + formatter row; `references/examples/golden-opencode.json` drops `mcp`/`plugin`, adds `formatter: true` + `language-server` LSP example; `scripts/validate-opencode.py` rejects `mcp`/`plugin` with global-path errors, keeps ZAC/invented-value/`$schema` gates, and extends `lsp` checks (`{env:}`-only env, invented-command rejection). Validator: exit 0 on golden, exit 1 naming both keys on an mcp+plugin fixture. Known migration: pre-existing project files with inline `mcp` (incl. this repo's root `opencode.json`) now fail validation by design.
- - **opencode-init LSP/formatter shape correction:** `skill-templates/opencode-init/` enforced a stale `language-server` LSP wrapper and an ambiguous flat formatter that the real runtime (`opencode debug config` against https://opencode.ai/config.json) rejects — apex failed with `Missing key formatter.command`, blowsh-mcp with `Missing key lsp.language-server.command`. Golden file, `references/runtime-matrix.md`, SKILL.md Ground Truth/workflow/rules, and `scripts/validate-opencode.py` now emit and enforce the true shapes: LSP flat map `{<name>: {command, extensions?, env?, initialization?, disabled?}}` (`env`, never `environment`), formatter `true|false|{<name>: {command?, extensions?, environment?, disabled?}}`; the wrapper and flat-formatter fixtures fail with actionable errors. Installed copy at `~/.config/opencode/skills/opencode-init/` re-synced identical. `tests/test_skill_registry.py`: 6 stale tests rewritten (contract markers, secret-via-LSP-env, wrapper rejection, formatter named-map, mcp/plugin global-only rejection, flat-LSP positives) + 2 new tests; runnable suites **34 passed** (decision/brain suites error on pre-existing missing `mcp` module, untouched).
+- **Brain sessions per project, legacy global read-through (Task 234):** `mcp-brain-bridge/loop_guard.py` gains `project_sessions_root()` (explicit override → param/`BRAIN_PROJECT_ROOT`/`BRAIN_WORKSPACE_ROOT` → cwd walk-up to a `tasks/` dir → legacy global fallback) plus `legacy_sessions_root()`; `server.py` threads an optional `project_root` through `_sessions_root`, `_transcript_path`, `_fed_context_path`, `load_history`, `append_turn`, `save/load_fed_context`, and `brain_turn` — writes always land per project under `tasks/.sessions/<id>/`, while reads fall back to the legacy global dir with a loud stderr note when the per-project file is missing. HQ folders 230-233 migrated from the global store into `tasks/.sessions/` with a sha256 manifest (`/tmp/migrate-234-manifest.json`), globals kept as fallback. 4 new offline regression tests. Full suite: **354 passed**. Hotfix: no-global-write (fallback writes reroute to `cwd/tasks/.sessions` with stderr warn), package-then-plain sibling import, per-project loop-guard hashes with legacy read fallback, per-turn sessions-root stderr line, 3 more tests (T5-T7). Full suite: **357 passed**.
+- **Review-approval relay + session-history gitignore (Task 235):** `agents/cognitive-executor.md` gains a Review-approval relay rule (technical approval → verbatim relay, file stays in qa; only the exact words "Approved for closure"/"Close task" count; Hands re-calls Brain Programmer once for a single final-closure XML and executes it exactly once) plus a relay line in the Code Reviewer roster row. `prompts/fragments/06-personas.md` Code Reviewer contract now routes closure through the relayed Programmer XML instead of emitting it directly. Shipped prompt rebuilt to 9.37.0. Global `audit-agents` skill Plugin Runtime-State rule now covers Brain session history (`tasks/.sessions/` added only after confirming the dir exists). Hotfix: relay tightened (bare-approved counts only as the next message answering the relayed question; explicit never-list incl. yes/done/okay/looks-good/emoji/silence; qa + PO_REVIEW_PENDING double-gate; single issuance with failure-only re-call; autopilot self-decision never satisfies); repo `skill-templates/audit-agents/SKILL.md` template extended too (both occurrences) so the rule ships in-repo. Second hotfix: reviewer contract mirrors the executor relay exactly (bare-approved exception + full never-list incl. okay/done/fine/looks-good/emoji-only + autopilot bar), audit clause gains a duplicate-line guard (check first, add only if missing), shipped prompt rebuilt to 9.37.2.
+- **Lean-retry state note + migrate Task 234 session (Task 236):** `mcp-brain-bridge/server.py` `_empty_output_hint` and the executor Empty-output clause gain a state-freshness sentence: a lean retry drops the bundle, so if the answer judges stale or missing context, re-run ONCE with the full bundle plus diff before escalating (proven by the 235 turn-3 stale verdict). Task 234's global transcript + fed context migrated into `tasks/.sessions/234/` with sha256-verified manifest. 4 new regression assertions (stale sentence, state line, 2 unknown fallbacks). Full suite: **357 passed**.
+- **opencode-init project-only contract (Task 237):** `skill-templates/opencode-init/` now generates project-only `opencode.json` — allowlist `$schema`, `default_agent`, `instructions`, `formatter`, `lsp` (guidance only), `permission` (ZAC denies intact); `mcp` and `plugin` are global-only (install in `~/.config/opencode/opencode.json` or a plugins dir) and are omitted on generate, rejected on validate. SKILL.md stops asking for MCP env keys/plugin choice and writes a global-install note instead; `references/runtime-matrix.md` V1 row + MCP/plugin global-only rows + formatter row; `references/examples/golden-opencode.json` drops `mcp`/`plugin`, adds `formatter: true` + `language-server` LSP example; `scripts/validate-opencode.py` rejects `mcp`/`plugin` with global-path errors, keeps ZAC/invented-value/`$schema` gates, and extends `lsp` checks (`{env:}`-only env, invented-command rejection). Validator: exit 0 on golden, exit 1 naming both keys on an mcp+plugin fixture. Known migration: pre-existing project files with inline `mcp` (incl. this repo's root `opencode.json`) now fail validation by design.
+- **opencode-init LSP/formatter shape correction:** `skill-templates/opencode-init/` enforced a stale `language-server` LSP wrapper and an ambiguous flat formatter that the real runtime (`opencode debug config` against https://opencode.ai/config.json) rejects — apex failed with `Missing key formatter.command`, blowsh-mcp with `Missing key lsp.language-server.command`. Golden file, `references/runtime-matrix.md`, SKILL.md Ground Truth/workflow/rules, and `scripts/validate-opencode.py` now emit and enforce the true shapes: LSP flat map `{<name>: {command, extensions?, env?, initialization?, disabled?}}` (`env`, never `environment`), formatter `true|false|{<name>: {command?, extensions?, environment?, disabled?}}`; the wrapper and flat-formatter fixtures fail with actionable errors. Installed copy at `~/.config/opencode/skills/opencode-init/` re-synced identical. `tests/test_skill_registry.py`: 6 stale tests rewritten (contract markers, secret-via-LSP-env, wrapper rejection, formatter named-map, mcp/plugin global-only rejection, flat-LSP positives) + 2 new tests; runnable suites **34 passed** (decision/brain suites error on pre-existing missing `mcp` module, untouched).
 - **MCP tool description usability fixes (Task 258):** description-only pass over the 28 Python MCP tools so an LLM picks the right tool. Short docstrings on tree, source reader, signatures, memory CRUD, and brain file-pull helpers gain one-line use-when plus look-alike distinctions (inline tree versus saved report, outline versus full content, store versus search, locate versus slice pull). Helpers that return a report path say so. `_note_checkpoint` loses its public tool decorator (private ledger wiring, body and calls unchanged). `docs/brain-bridge.md` file-pull section is Hands-first (Hands pull via read and grep or path injection, Brain quotes paths) with the `brain_turn` export mapping documented. No signatures, return shapes, allowlists, or limits changed.
 
 ### Fixed
@@ -56,7 +60,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Bridge follow-up: attach-note wording, cross-project bleed, closure gate, rtk mandate (Task 241, syncs GitHub issue 15):** remaining `read_file` pull orders removed from both task-attach notes (`_strip_task_diff`, `_TASK_ATTACH_CAP`) — no file tools, quote paths, Hands feeds `fed-context` under the same `task_id`. `load_history`/`load_fed_context` legacy fallbacks now apply ONLY when the resolved root IS the legacy global (a project with its own `tasks/` dir gets fresh `[]`/`''`, never foreign turns); writes were already per-project. New `validate_closure_checklist` (QA_PASSED + PO_REVIEW_PENDING + exact approval words + non-empty diff + `extract_session_decisions` evidence) closes the never-called decision-capture gap. New CRITICAL RULE 3b in `prompts/fragments/09-hands_protocols.md` mandates `rtk test` for passing suites; shipped prompt rebuilt to **9.38.0**. 9 new tests (wording, no-bleed, closure gate, prompt-sync). Full suite: **387 passed**, zero failures.
 - **Context-handling gaps: utilization ledger + over-cap signatures fallback (Task 241 extension, web-research findings):** `mcp-brain-bridge/server.py` gains a per-turn context ledger (`_MODEL_WINDOW_CHARS=200000`, one JSON line per turn — task_id, budget_chars, est_tokens, util_pct, truncated — to `context_ledger.jsonl`, best-effort never-raise) and the prompt-size warn now shows `util~%`, so truncation pressure is measured instead of guessed. `mcp-context-server/server.py` `process_source_file` over-cap branch now appends tree-sitter signatures (or a narrow-paths pointer) instead of silently skipping the file, so discovery keeps structural signal past the cap. 2 new tests (ledger+util, too-large-signatures). Full suite: **389 passed**, zero failures.
 - **Decision-redactor word-edge leak (Task 242, Phase 1 B1):** `mcp-decision-server/redactor.py` assignment rule leading edge `\b` → `(?<![A-Za-z0-9])` in both sanitize and verify patterns, so ENV-style `KEY=value` names (`BRAIN_API_KEY=`, `FOO_SECRET=`) redact while prose `topsecret=` stays untouched; new short-Bearer rule (`{4,7}` chars with digit gate) catches `Bearer abc123`-shaped tokens while prose `Bearer tokens` and the `{8,}` rule stay unchanged. 4 new tests (3 failed pre-fix as required). Full decision suite: **105 passed**, zero failures. QA-hotfix regression tests added (punctuation Bearer, quoted forms — all green pre-fix; the claimed `-1` suffix leak did not reproduce: `-` is inside the token class, direct evidence recorded in Task 242). Full suite: **400 passed**, zero failures.
-- **Decision-server DECISION_* env support (Task 243):** `mcp-decision-server/server.py` now reads `DECISION_API_BASE`, `DECISION_API_KEY`, `DECISION_MODEL`, `DECISION_REASONING_EFFORT`, each with `BRAIN_*` fallback (fail-closed error names both key vars); new module-level `_get_api_base()` helper; `.env.example` DECISION section extended with the four lines + fallback docs. 3 new contract tests (precedence, blank-fallback, fail-closed); 2 old tests fixed for env hermeticity. Full suite: **396 passed**, zero failures.
+- _*Decision-server DECISION_* env support (Task 243):_* `mcp-decision-server/server.py` now reads `DECISION_API_BASE`, `DECISION_API_KEY`, `DECISION_MODEL`, `DECISION_REASONING_EFFORT`, each with `BRAIN_*` fallback (fail-closed error names both key vars); new module-level `_get_api_base()` helper; `.env.example` DECISION section extended with the four lines + fallback docs. 3 new contract tests (precedence, blank-fallback, fail-closed); 2 old tests fixed for env hermeticity. Full suite: **396 passed**, zero failures.
 - **Bridge nested reasoning-effort fix (Task 244):** `mcp-brain-bridge/server.py` now sends `reasoning.effort` as a nested `reasoning: {effort}` object in the Responses body (the flat `reasoning_effort` key was rejected with a provider 400 on the first live OpenRouter turn); the explicit-temperature branch drops the reasoning key, mirroring the bridge contract. 2 existing tests updated to the nested shape. Full suite: **400 passed**, zero failures.
 - **Context-paths project-root fix plus semantic XML gate (Task 245, Phase 1):** `mcp-brain-bridge/server.py` `build_paths_attach` now accepts `project_root` via a new `_paths_base` helper (explicit project dir wins, workspace root stays fallback) and the `brain_turn` call site threads it through — relative `context-reports/*.md` paths resolve under the project instead of the server install dir, ending the cross-install `missing_context` loop; caps and labels unchanged. New pure `validate_hands_xml_blocks` (required phase markers per block type, word-bound; unknown roots, missing close tags, empty bodies rejected) runs after tolerant extraction — syntactically valid but contract-incomplete XML now triages as REPORT with an inline `[xml-semantic-reject]` list instead of executing. 11 new tests (5 resolver: project-root win, missing label, invalid fallback, cwd independence, size-pattern truncation; 6 validator: valid accept, missing phase, missing bash_phase, empty/unclosed, unknown root, non-string root fallback). Full suite: **411 passed**, zero failures (6 memory-server tests need the memory project env for `yaml`; proven env-only, green there). Review hotfix: phase checks now match opening elements inside the comment-stripped root body (bare words, comments, post-close text rejected) plus a `brain_turn` REPORT-integration test; docstring number removed. 4 more tests. Full suite: **415 passed**, zero failures.
 - **Eval harness residual hardening (Task 251):** `mcp-brain-bridge/eval_harness.py` closes the two low residuals deferred at review time. `_op_is_zac` now normalizes the executable position (basename of token 0, or token 1 when token 0 is exactly `sudo`) and requires a protected verb (`add`/`commit`/`push`) next, so path-prefixed (`/usr/bin/git add`) and `sudo`-prefixed git invocations are flagged while prose (`legit git status`, `git status`) stays clean. New pure `_is_finite_number` predicate (finite int/float, booleans and nan/inf rejected) backs `_mean` and the cost/latency aggregate filters, so invalid numerics never enter aggregates; per-row columns still preserve raw values. 6 new tests (absolute-path, sudo, prose guard, boolean aggregates, non-finite aggregates, mean filter). Full suite: **508 passed**.
@@ -77,7 +81,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Executor-local personas roster (no task, manager-direct):** `agents/cognitive-executor.md` gained a `Personas Roster` section — all 7 seats (Architect, Designer, Programmer, Planner, Strategist, QA, Reviewer) with trigger + one-line duty plus the Layer 1/2 load rules — so the Hands resolves seats locally without a Brain round-trip. Anti-drift rule: `prompts/fragments/06-personas.md` is source of truth and every edit there updates the table in the same commit.
 - **Decision-migration skill (Task 217):** new Hands-invoked `skill-templates/decision-migration/SKILL.md` (no standalone script per manager correction) migrates a project's per-project `.opencode/decisions/` store into the separate personal repo: resolve endpoints (HALT when source INDEX or `DECISION_REPO_PATH` target missing), mandatory dry-run classification (`would-migrate`/`would-skip`/`would-reject`) with Manager batch approval before any write, writes only via `record_manager_decision` with `migrated_from` provenance, idempotent reruns, counts report, append-only tombstone corrections, ZAC. Registered in `07-agent_skills_registry.md`; system prompt rebuilt to 9.34.0. 2 new offline registry-consistency tests. QA-hotfix hardening: explicit batch-approval phrase (ambiguous replies count as NOT approved), never-invent-target-path rule, `migrated_from` skip-if-exists pre-check, `git status --porcelain` source-immutability proof, rejected-IDs-with-reasons report rule, plus 3 contract tests. Full suite: **304 passed**.
 - **Separate personal manager-decisions repo (Task 216):** manager rulings now persist to ONE personal repo (`DECISION_REPO_PATH`) as the authoritative cross-project personality source — per-project `.opencode/decisions/` drops to write-through cache + offline fallback (Task 213 mirror-never-authority superseded by manager order). `mcp-decision-server/server.py` gained `_active_root_info()` (resolution logging on every record + fail-closed scope docstring) and auto-creates the personal `decisions/` tree on first write. `skill-templates/manager-decision/SKILL.md` gained the consult-on-stuck protocol (mandatory replay line `Replayed from <DEC-ID> (<date>): <quote>`, no-match escalation, autopilot loop-pole). `LLM.txt` §7.11 onboards the repo (declare `DECISION_REPO_PATH` or `gh repo create`, public default). QA-hotfix hardening: every stored record carries queryable `active_root` + `store_mode` provenance (no stderr dependence), unusable `DECISION_REPO_PATH` fails closed with a clear error (never silent fallback), 7 more offline tests (fail-closed ordering, stderr secrecy, provenance, empty-env fallback, nested path, file-as-path, sequential ids). 4 new offline tests. Reviewer follow-ups: stored `active_root` holds the repo display name only (no absolute paths leak into public-default repos); stale mirror-wording audit found only historical closed-task records plus intentional supersession notes, no live rule. Full suite: **299 passed**.
-- **Brain-bridge hotfix XML extraction (Task 215):** `extract_xml_blocks` in `mcp-brain-bridge/server.py` stopped dropping reviewer hotfix XML two ways — `hotfix` joined the `XML_BLOCK_TAGS` allowlist, and an explicit ```xml-fence fallback returns allowlist tags from ```xml bodies (closed or unclosed) when the unfenced scan finds nothing. Other fences (json/bare/tilde/quad — quad via a `(?<!`)` guard, reviewer follow-up A1) stay documentation-only and unknown tags stay ignored, so no over-extraction. `docs/brain-bridge.md` runbook updated. 14 new offline extractor tests (7 incident + 6 QA follow-ups: multi-fence order, uppercase fence, uppercase-tag/attribute/no-newline locks, empty block; + quad-fence lock). Full suite: **288 passed**.
+- **Brain-bridge hotfix XML extraction (Task 215):** `extract_xml_blocks` in `mcp-brain-bridge/server.py` stopped dropping reviewer hotfix XML two ways — `hotfix` joined the `XML_BLOCK_TAGS` allowlist, and an explicit `xml-fence fallback returns allowlist tags from `xml bodies (closed or unclosed) when the unfenced scan finds nothing. Other fences (json/bare/tilde/quad — quad via a `(?<!`)`guard, reviewer follow-up A1) stay documentation-only and unknown tags stay ignored, so no over-extraction.`docs/brain-bridge.md` runbook updated. 14 new offline extractor tests (7 incident + 6 QA follow-ups: multi-fence order, uppercase fence, uppercase-tag/attribute/no-newline locks, empty block; + quad-fence lock). Full suite: **288 passed**.
 
 - **Manager-decision auto-extraction (Task 213):** new pure-function `mcp-decision-server/detector.py` — `detect_decision_moments` flags turns with 2+ signals (owner:manager + ruling-phrase + tradeoff-marker + scope-noun); only `passes_precision_bar` candidates (named owner + 2 content signals) feed `extract_session_decisions`, and every persist still needs the mandatory human confirm gate (auto-record forbidden). `skill-templates/manager-decision` gained Auto-Trigger Spec (live detector + end-of-sprint sweep reusing the extraction LRU/repair path) and Shared Personal Repo design (per-project store authoritative, one-way append-only redacted mirror, sanitize+verify boundary, versioned challenge-question protocol under the existing review gate). Task 168 scope extended, not forked; Task 151 deletion stands. Detector hardened per QA: speaker filter (only manager/confirmed turns queue), weak-signal pairing (bare modals/scope nouns need a strong ruling or tradeoff), word-edge excerpts, tombstone retraction rule. 9 new offline detector tests. Full suite: **274 passed**.
 
diff --git a/README.md b/README.md
index 0785f60..69778dc 100644
--- a/README.md
+++ b/README.md
@@ -166,6 +166,7 @@ cp .env.example .env
 - [Blowsh Web Skill](skill-templates/blowsh/SKILL.md) — live-web search/fetch/crawl via the blowsh MCP server
 - [Cognitive Executor Agent](agents/cognitive-executor.md) (Bridge + Autopilot sections)
 - [Setup Guide](docs/setup.md)
+- [Manager-Decisions MCP Server](docs/manager-decisions.md) — tool schemas and usage contract for the six decision tools
 
 ---
 
@@ -188,6 +189,7 @@ cp .env.example .env
 ├── docs/
 │   ├── conventions.md                  # Syntax rules and automation conventions
 │   ├── setup.md                        # Platform tool setup and installation guide
+│   ├── manager-decisions.md            # manager_decisions MCP tool schemas and usage contract
 │   ├── history/                        # Milestone compaction summaries
 │   └── opencode/                       # OpenCode documentation mirror
 ├── mcp-context-server/
@@ -196,6 +198,8 @@ cp .env.example .env
 │   └── server.py                       # FastMCP server for task file linting
 ├── mcp-memory-server/
 │   └── server.py                       # FastMCP server for persistent project memory
+├── mcp-decision-server/
+│   └── server.py                       # FastMCP server for Manager-decision capture & consultation
 ├── mcp-brain-bridge/                  # Unified Brain bridge
 │   └── server.py                       # FastMCP `BrainBridge`: brain_turn (prompt loader + LLM + XML extract)
 ├── prompts/                            # System prompt source tree (fragments + shared partials)
@@ -285,21 +289,21 @@ cp .env.example .env
 
 ### General & Workflow Skills
 
-| Skill Name                | Purpose                                                                                                                                                                                                                                    |
-| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
-| `audit-agents`            | Enforces Zero-Autonomous-Commit (ZAC) workflows and generates/audits `AGENTS.md` for new and existing projects.                                                                                                                            |
-| `code-search`             | Mandatory for discovery. Uses MCP tools (`get_directory_tree`, `read_source_files`, `extract_signatures`) to explore the codebase without token bloat.                                                                                     |
-| `debug-instrumentation`   | Diagnoses complex runtime bugs, deadlocks, race conditions, and silent failures via strategic temporary logging and tracing.                                                                                                               |
-| `design-md`               | Extracts a comprehensive design system (`DESIGN.md`) directly from frontend source code — React, Vue, Svelte, Angular, plain HTML/CSS, or any web framework.                                                                               |
-| `doc-coauthoring`         | Guides users through a structured 3-stage workflow (Context Gathering, Refinement & Structure, Reader Testing) for co-authoring documentation with AI.                                                                                     |
-| `github`                  | GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.                                                                                                                                   |
-| `prompt-refactor`         | Meta-cognitive skill that refactors basic human prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.                                                                                          |
+| Skill Name                | Purpose                                                                                                                                                                                                                         |
+| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
+| `audit-agents`            | Enforces Zero-Autonomous-Commit (ZAC) workflows and generates/audits `AGENTS.md` for new and existing projects.                                                                                                                 |
+| `code-search`             | Mandatory for discovery. Uses MCP tools (`get_directory_tree`, `read_source_files`, `extract_signatures`) to explore the codebase without token bloat.                                                                          |
+| `debug-instrumentation`   | Diagnoses complex runtime bugs, deadlocks, race conditions, and silent failures via strategic temporary logging and tracing.                                                                                                    |
+| `design-md`               | Extracts a comprehensive design system (`DESIGN.md`) directly from frontend source code — React, Vue, Svelte, Angular, plain HTML/CSS, or any web framework.                                                                    |
+| `doc-coauthoring`         | Guides users through a structured 3-stage workflow (Context Gathering, Refinement & Structure, Reader Testing) for co-authoring documentation with AI.                                                                          |
+| `github`                  | GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.                                                                                                                        |
+| `prompt-refactor`         | Meta-cognitive skill that refactors basic human prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.                                                                               |
 | `bundle-tasks`            | Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Pure-MCP tool `bundle_tasks` — see `skill-templates/bundle-tasks/SKILL.md`. |
-| `blowsh`                  | Live-web research via the blowsh MCP server (Docker): `search_web`, `fetch_web`, `fetch_web_batch`, `crawl_web`, `extract_links` — rendered engines, JS rendering, sitemap-aware crawls. See `skill-templates/blowsh/SKILL.md`.            |
-| `task-generator`          | Automatically generates decentralized task files based on Manager instructions, with correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.                                                                                  |
-| `telegram-issue-sync`     | Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.                                                                                           |
-| `telegram-message-export` | Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.                                                                    |
-| `versioning-and-release`  | Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.                                                                                                |
+| `blowsh`                  | Live-web research via the blowsh MCP server (Docker): `search_web`, `fetch_web`, `fetch_web_batch`, `crawl_web`, `extract_links` — rendered engines, JS rendering, sitemap-aware crawls. See `skill-templates/blowsh/SKILL.md`. |
+| `task-generator`          | Automatically generates decentralized task files based on Manager instructions, with correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.                                                                       |
+| `telegram-issue-sync`     | Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.                                                                                |
+| `telegram-message-export` | Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.                                                         |
+| `versioning-and-release`  | Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.                                                                                     |
 
 ### Stack-Specific Blueprints
 
diff --git a/docs/manager-decisions.md b/docs/manager-decisions.md
new file mode 100644
index 0000000..eda9712
--- /dev/null
+++ b/docs/manager-decisions.md
@@ -0,0 +1,274 @@
+# manager-decisions MCP Server
+
+The `manager_decisions` server is the Cognitive Lead AI memory for Manager rulings. Agents call it to consult a stored decision before paging the human, and to persist a new ruling the Manager just made.
+
+This document is the agent-facing usage contract: server identity, store resolution, every tool signature, the shared record schema, and the failure modes. It is written so an agent can call each tool correctly on the first try.
+
+> **Revision note (pinned).** Every factual claim below was verified against source at commit `0183433ccec9cc9252f874060df5140c4618ecb4` (2026-09-20), read on 2026-09-21. File and line citations are pinned to that revision: `mcp-decision-server/server.py` is 1821 lines, `redactor.py` is 85 lines, `detector.py` is 149 lines. If any of these files change, re-verify before trusting a citation.
+
+## Purpose and Scope
+
+In scope here:
+
+- The six MCP tools exposed by `mcp-decision-server/server.py`, with argument names, types, return shapes, side effects, and failure modes.
+- The decision store layout and how the server picks a store.
+- The decision-record field contract that `record_manager_decision` enforces.
+- Known divergence between this server's source and the `manager-decision` skill text, reported as-is.
+
+Out of scope: changing server behavior. Documented drift is **reported, not fixed** — no source file and no skill file was modified to write this page.
+
+## Server Identity and Transport
+
+| Property                  | Value                                     | Source                                                        |
+| ------------------------- | ----------------------------------------- | ------------------------------------------------------------- |
+| Server object             | `mcp = FastMCP("ManagerDecisions")`       | `mcp-decision-server/server.py:190`                           |
+| Transport                 | stdio, entered under the `__main__` guard | `mcp-decision-server/server.py:1820-1821`                     |
+| Package                   | `mcp-decision-server`, version `1.0.0`    | `mcp-decision-server/pyproject.toml:2-3`                      |
+| Script entry point        | none declared                             | `mcp-decision-server/pyproject.toml` (no `[project.scripts]`) |
+| Launch                    | `uv run mcp-decision-server/server.py`    | `docs/setup.md:59`                                            |
+| Extraction model constant | `DEFAULT_DECISION_MODEL = "gpt-6-astra"`  | `mcp-decision-server/server.py:196`                           |
+| Model override env        | `DECISION_MODEL`                          | `mcp-decision-server/server.py:265-275`                       |
+
+**Model resolution correction.** The only model override for this server is the `DECISION_MODEL` environment variable. `_get_decision_model()` reads `DECISION_MODEL` first and otherwise returns `DEFAULT_DECISION_MODEL` (`mcp-decision-server/server.py:265-275`). `BRAIN_MODEL` is **never read** by this server — grep finds no reference to it anywhere in `mcp-decision-server/`. The code deliberately does not fall back to `PERSONA_MODEL` either; the reason is recorded inline at `mcp-decision-server/server.py:268`: a stale persona model value once hijacked extraction calls and caused 401s. Sibling variables that do carry a `BRAIN_` prefix are unrelated to model choice: `BRAIN_REASONING_EFFORT` (`mcp-decision-server/server.py:288`), `BRAIN_API_KEY` (`mcp-decision-server/server.py:363`), and `BRAIN_API_BASE` (`mcp-decision-server/server.py:399`).
+
+## Store Resolution
+
+`_repo_root()` (`mcp-decision-server/server.py:78`) picks the decision store in a fixed order and fails closed at the end:
+
+1. **Explicit path.** `DECISION_REPO_PATH` wins if set to a non-blank value (`mcp-decision-server/server.py:92`). The directory is created with `mkdir(parents=True, exist_ok=True)` (line 95). If creation fails, the server raises `RuntimeError` and does **not** fall back — the message names the variable and advises fixing the path or unsetting it (`mcp-decision-server/server.py:95-104`, message at line 102).
+2. **Per-project fallback.** Otherwise the server walks `(Path.cwd(), INSTALL_ROOT)` and tries `base / ".opencode" / "decisions"` for each (`mcp-decision-server/server.py:106-112`). A candidate that cannot be created is skipped with `OSError` (`continue`). `INSTALL_ROOT = Path(__file__).resolve().parent.parent` (`mcp-decision-server/server.py:75`).
+3. **No writable location.** Exhausting both candidates raises `RuntimeError("cannot create a decision store: no writable location found")` (`mcp-decision-server/server.py:113`).
+
+The server tells the operator which store is live. `_active_root_info(repo)` (`mcp-decision-server/server.py:116`) returns `personal repo (DECISION_REPO_PATH set)` (line 130) or `project fallback (DECISION_REPO_PATH unset)` (line 131). `record_manager_decision` prints this to stderr as `decision-server: active store: …` (`mcp-decision-server/server.py:1587`).
+
+Two provenance fields are stamped on every record rather than left to the caller:
+
+- `active_root = repo.name` — the repo **display name only**, never the absolute path (`mcp-decision-server/server.py:1604`).
+- `store_mode` — `"personal"` when `DECISION_REPO_PATH` is set, else `"project-fallback"` (`mcp-decision-server/server.py:1605-1607`).
+
+Full paths stay in local stderr logs and are never written into a record.
+
+## Six-Tool Quick Reference
+
+All six are decorated with `@mcp.tool()` in `mcp-decision-server/server.py`.
+
+| Tool                        | Decorator / `def` | Signature                                                                                                                                      | Returns                                                      |
+| --------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
+| `extract_session_decisions` | `:1258` / `:1259` | `(task_id: Optional[Union[int, str]] = None, transcript_path: Optional[str] = None, session_id: Optional[str] = None) -> list[dict[str, Any]]` | list of candidate decision dicts, unscrubbed and unvalidated |
+| `record_manager_decision`   | `:1550` / `:1551` | `(decision: dict[str, Any]) -> str`                                                                                                            | human-readable confirmation naming the record id             |
+| `query_manager_decisions`   | `:1642` / `:1643` | `(query: str, category: Optional[str] = None) -> str`                                                                                          | formatted ranked summaries, or a no-match message            |
+| `get_sync_status`           | `:1745` / `:1746` | `() -> str`                                                                                                                                    | active store plus sync-debt report                           |
+| `get_manager_profile`       | `:1759` / `:1760` | `() -> str`                                                                                                                                    | the profile sample text, or an explanatory message           |
+| `propose_profile_evolution` | `:1784` / `:1785` | `() -> dict[str, Any]`                                                                                                                         | `{"status": "DRAFT_READY"｜"EMPTY"｜"ERROR", "draft": str}`  |
+
+Enum sheet used across tools and records:
+
+| Field      | Allowed values                                                                                       | Where enforced                                              |
+| ---------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
+| `category` | `architecture`, `process`, `scope`, `quality-gate`, `tooling`, `release`, `other`, `autopilot-cycle` | `mcp-decision-server/server.py:959-962`                     |
+| `fidelity` | `verbatim`, `reconstructed` (default `verbatim`)                                                     | `mcp-decision-server/server.py:896-900`, default at `:1595` |
+| `mode`     | `manual`, `autopilot` (default `manual`)                                                             | `mcp-decision-server/server.py:896-900`, default at `:1595` |
+| `scope`    | `standing`, `episode` (default `episode`)                                                            | `mcp-decision-server/server.py:896-900`, default at `:1596` |
+
+## Tool Details
+
+### `extract_session_decisions`
+
+```python
+extract_session_decisions(
+    task_id: Optional[Union[int, str]] = None,
+    transcript_path: Optional[str] = None,
+    session_id: Optional[str] = None,
+) -> list[dict[str, Any]]
+```
+
+**When to call.** At the end of every session in which the Manager ruled, chose, or constrained something, before closing the task (`mcp-decision-server/server.py:1264-1294`). Feed the output into `record_manager_decision`. The output is **unscrubbed and unvalidated** — it is only a candidate list.
+
+**Arguments.**
+
+- `task_id` — session scope as `tasks/.sessions/{task_id}/transcript.jsonl`. A numeric value resolves the numeric path.
+- `session_id` — taskless session scope, sanitized before use (`mcp-decision-server/server.py:1249`).
+- `transcript_path` — explicit override, mainly for tests and replays.
+
+**Resolution order.** `transcript_path` wins if given (`mcp-decision-server/server.py:1296-1297`). Otherwise the scope is `session_id` or `task_id`; if both are `None` the tool raises `ValueError("decision extract: pass task_id or session_id (or transcript_path for replays)")` (`mcp-decision-server/server.py:1300-1304`). Numeric scope reads `tasks/.sessions/{int}/transcript.jsonl` (`mcp-decision-server/server.py:1312-1316`); a non-numeric session id is sanitized into `tasks/.sessions/{sanitized_sid}/transcript.jsonl` (`mcp-decision-server/server.py:1305-1311`).
+
+**Return shape.** A JSON array of candidates, each item shaped as `{"verbatim_quote": {"original": …, "english_translation": …}, "extracted_decision": {"summary": …, "category": …, "rationale": …, "alternatives": [], "tradeoffs": …}}` (extraction prompt at `mcp-decision-server/server.py:1348-1355`).
+
+**Side effects.** One LLM call to the `DECISION_MODEL` model. Reads a transcript; writes nothing.
+
+**Failure modes.**
+
+- Missing transcript file → returns `[]` gracefully, before the lazy LLM import runs (`mcp-decision-server/server.py:1317-1318`).
+- Present but zero-turn transcript → raises `RuntimeError` (`mcp-decision-server/server.py:1330-1334`). A broken pipeline must not be mistaken for a quiet session.
+- Malformed model output → raises `RuntimeError` (`mcp-decision-server/server.py:1264-1294`).
+- No scope given, or an unsafe session id → raises `ValueError` (`mcp-decision-server/server.py:1300-1304`, `:1249`).
+- Oversized transcript → capped by `_get_decision_transcript_max_chars()` with an explicit `[...truncated at N chars]` marker, never silently (`mcp-decision-server/server.py:1339-1347`).
+
+### `record_manager_decision`
+
+```python
+record_manager_decision(decision: dict[str, Any]) -> str
+```
+
+**When to call.** Immediately after extraction returns candidates, or as soon as the Manager states a ruling mid-session — do not wait for session end (`mcp-decision-server/server.py:1552-1585`).
+
+**Pipeline.** `sanitize_text` every free-text field → `verify_clean` gate → schema validation → write `.json` + `.md` → regenerate `INDEX.md`. The scrub gate fail-closes on every root, including an explicitly configured personal repo; there is no bypass flag (`mcp-decision-server/server.py:1552-1585`).
+
+**Argument.** A single `decision` dict. The tool fills these when absent: `decision_id` (`mcp-decision-server/server.py:1591`), `timestamp` (`:1592`), `fingerprint` (`:1600-1602`), plus hardened defaults `fidelity="verbatim"`, `mode="manual"`, `scope="episode"`, `goal_ref=""` (`:1593-1599`). An explicit `None` counts as unset for those four, so a `None` never survives as a value.
+
+> **Warning.** `project_name` is **required** and is **not** defaulted (`mcp-decision-server/server.py:873-874`, `:1591-1602`). The docstring's `Args` block documents only `decision` (`mcp-decision-server/server.py:1575-1577`), so an omission surfaces as an undocumented `ValueError`. Always pass it.
+
+**Return shape.** A string such as `Recorded DEC-YYYYMMDD-NNN (`decisions/YYYY/MM/….json`+`.md`; index now holds N).` (`mcp-decision-server/server.py:1637-1639`). When the fingerprint matches an earlier record, the same string carries `Possible duplicate of <id> (same fingerprint) — kept as a separate record; confirm intent.` (`mcp-decision-server/server.py:1603`, `:1635-1636`).
+
+**Side effects.** Writes `decisions/YYYY/MM/DEC-YYYYMMDD-NNN.json` with `json.dumps(indent=2, ensure_ascii=False)` (`mcp-decision-server/server.py:1614-1616`) and a companion `.md` (`:1619-1633`), regenerates `INDEX.md` (`:1634`), prints the active store to stderr (`:1587`), and reports unpushed commits (`:1637-1639`). It never commits or pushes.
+
+**Failure modes.** Sensitive residue after sanitizing, or any schema violation, raises `ValueError` and writes **nothing** (`mcp-decision-server/server.py:1608-1610`, `:1552-1585`). An unwritable store raises `RuntimeError` from `_repo_root()` (`:113`).
+
+### `query_manager_decisions`
+
+```python
+query_manager_decisions(query: str, category: Optional[str] = None) -> str
+```
+
+**When to call.** Automatically, **before** paging the human Manager with a question. If a past ruling covers the question, decide from the record instead of asking (`mcp-decision-server/server.py:1644-1661`). Also call it during discovery when the task touches architecture, process, scope, or quality gates.
+
+**Arguments.**
+
+- `query` — keyword(s). Case-insensitive ranked match over `summary` (weight 3), verbatim `original` (2), verbatim `english_translation` (2), `rationale` (2), `tradeoffs` (1), joined `alternatives` (1) (`mcp-decision-server/server.py:1713-1720`). A blank query scores every record 1, so it returns everything in the category (`:1644-1661`).
+- `category` — optional filter against the eight-value enum (`mcp-decision-server/server.py:1692-1693`, `:1644-1661`).
+
+**Return shape.** `"{n} decision(s) match:\n\n"` followed by the joined hit blocks (`mcp-decision-server/server.py:1741-1742`). Each hit block is `### <decision_id> [<category>] <summary>`, then `> <english_translation>`, then `Rationale: <rationale>` (`mcp-decision-server/server.py:1733-1736`).
+
+**Side effects.** Pulls the store first; reads only. Never writes, commits, or pushes.
+
+**Failure modes.** No hits → the string `No manager decisions match query='…' category=…` (`mcp-decision-server/server.py:1738-1739`). A failed pull does **not** error out: the server prints `decision-server: pull failed (…); reading local state` and serves local state so reads stay available (`mcp-decision-server/server.py:1663-1669`). Malformed record files are skipped, not fatal: non-dict records, non-dict `extracted_decision`, non-dict `verbatim_quote`, and non-list `alternatives` are all filtered before scoring (`mcp-decision-server/server.py:1676-1711`).
+
+**No result cap.** The tool returns **every** matching record. There is no top-N limit; the literal `3` at `mcp-decision-server/server.py:1714` is the `summary` scoring weight. On a large store, expect long output.
+
+### `get_sync_status`
+
+```python
+get_sync_status() -> str
+```
+
+**When to call.** At session start, so silent sync debt is visible before new records land (`mcp-decision-server/server.py:1747-1750`).
+
+**Return shape.** `"{active store info}; {freshness}; {unpushed report}"` (`mcp-decision-server/server.py:1746-1756`).
+
+**Side effects.** Read-only; never commits or pushes (ZAC holds). A failed pull degrades to local state with a stderr note rather than raising (`mcp-decision-server/server.py:1746-1756`).
+
+### `get_manager_profile`
+
+```python
+get_manager_profile() -> str
+```
+
+**When to call.** Automatically whenever resolving an architectural ambiguity or applying a house rule — the profile is the Manager's standing judgment (`mcp-decision-server/server.py:1761-1770`).
+
+**Return shape.** The text of `<store>/samples/manager_profile.md`, or the explanatory string `No manager profile sample exists yet.` when the sample is absent.
+
+**Notes.** The baseline section is curated; a generated aggregate appears only from reviewed compilations. The tool never synthesizes guidance (`mcp-decision-server/server.py:1761-1770`). Cheap, read-only, no side effects. A failed pull degrades to local state (`mcp-decision-server/server.py:1760-1781`).
+
+### `propose_profile_evolution`
+
+```python
+propose_profile_evolution() -> dict[str, Any]
+```
+
+**When to call.** Only when new recorded decisions exist that the current sample does not reflect — roughly once per sprint, never per session. Present the draft to the Manager; merge nothing without explicit approval (`mcp-decision-server/server.py:1786-1799`).
+
+**Behavior.** Runs `scripts/compile_profile.py` in a subprocess via `subprocess.run([sys.executable, str(script), "--repo", str(repo)], capture_output=True, text=True, timeout=120)` (`mcp-decision-server/server.py:1785-1817`). Nothing is written to the sample; the draft is returned as a staged diff-like payload.
+
+**Return shape.** A dict with `status` in `DRAFT_READY` / `EMPTY` / `ERROR` plus `draft`.
+
+- Missing compile script → `{"status": "ERROR", "draft": "compile script missing: <path>"}`.
+- Subprocess error or non-zero return code → `{"status": "ERROR", …}` with the reason.
+- Empty output, or output starting `No decisions found` → `{"status": "EMPTY", …}`.
+- Otherwise → `{"status": "DRAFT_READY", "draft": <text>}`.
+
+**Failure modes.** Never raises; every failure arrives as `status: ERROR`.
+
+## Shared Decision-Record Field Contract
+
+`_validate_against_schema` (`mcp-decision-server/server.py:865-912`) enforces the shape below before anything is written.
+
+**Required fields** — the tuple at `mcp-decision-server/server.py:873-874`:
+
+| Field                | Type / shape                                                                                                                         | Source                                    |
+| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------- |
+| `decision_id`        | `DEC-\d{8}-\d{3}`, generated when absent                                                                                             | `:879`, generated at `:753-764` / `:1591` |
+| `timestamp`          | ISO string parsed via `datetime.fromisoformat(str(…).replace("Z", "+00:00"))`; generated as `datetime.now(timezone.utc).isoformat()` | `:881-884`, `:1592`                       |
+| `project_name`       | present in the required tuple; **never defaulted**                                                                                   | `:873-874`, `:1591-1602`                  |
+| `verbatim_quote`     | mapping with `original` and `english_translation`                                                                                    | `:873-874`, `:1348-1355`                  |
+| `extracted_decision` | mapping with `summary`, `category`, `rationale`, `alternatives[]`, `tradeoffs`                                                       | `:873-874`, `:1348-1355`                  |
+| `redaction_verified` | server-set `True` after the scrub gate passes                                                                                        | `:861`, `:910`                            |
+
+**Validated enums and optional fields:**
+
+| Field         | Rule                                         | Source                               |
+| ------------- | -------------------------------------------- | ------------------------------------ |
+| `category`    | must be one of the eight values              | `:959-962`, `:892-894`, `:1045`      |
+| `fidelity`    | `verbatim` or `reconstructed` when present   | `:896-900`                           |
+| `mode`        | `manual` or `autopilot` when present         | `:896-900`                           |
+| `scope`       | `standing` or `episode` when present         | `:896-900`                           |
+| `fingerprint` | `[0-9a-f]{64}` sha256, generated when absent | `:904-906`, `:767-784`, `:1600-1602` |
+| `goal_ref`    | optional string                              | `:907-909`                           |
+
+**Server-stamped provenance:** `active_root` (repo display name) and `store_mode` (`personal` / `project-fallback`) — see Store Resolution above (`mcp-decision-server/server.py:1604-1607`).
+
+The redactor (`mcp-decision-server/redactor.py`) backs the `redaction_verified` gate. `sanitize_text` is idempotent, coerces non-strings to `str`, and maps empty input to `""` (`redactor.py:58-72`). `verify_clean` returns `False` when a sensitive pattern survives and must block the write (`redactor.py:75-85`). `REDACTION_RULES` (`redactor.py:19-43`) covers provider keys (`sk-`, `ghp_`, `AIzaSy`), Bearer tokens (with a digit gate so prose like "Bearer tokens" is untouched), private IPv4 ranges (`10/8`, `172.16/12`, `192.168/16`), and generic `password|passwd|secret|api_key|auth_token = …` assignments. `_VERIFY_RESIDUE` (`redactor.py:52-55`) reuses those rules but swaps the assignment rule for `_VERIFY_ASSIGNMENT` (`redactor.py:49-51`), which carries a `(?!\[REDACTED\])` lookahead so an already-redacted marker is not mistaken for a live secret.
+
+## Pitfalls for Agents
+
+| Pitfall                                                 | Correct behavior                                                                                                                                                  |
+| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
+| Omitting `project_name`                                 | Always pass it. It is required and not defaulted (`mcp-decision-server/server.py:873-874`, `:1591-1602`), yet the tool docstring does not list it (`:1575-1577`). |
+| `verbatim_quote` as a plain string                      | Must be a mapping with `original` and `english_translation`.                                                                                                      |
+| `extracted_decision` as a plain string                  | Must be a mapping with `summary`, `category`, `rationale`, `alternatives[]`, `tradeoffs`.                                                                         |
+| `alternatives` as a string or `None`                    | Must be a list. The query tool filters non-list `alternatives` before scoring (`mcp-decision-server/server.py:1702-1711`).                                        |
+| `tradeoffs` as a list                                   | Must be a string.                                                                                                                                                 |
+| Inventing a category                                    | The enum is closed: eight values only. `product-behavior` is invalid (`mcp-decision-server/server.py:959-962`).                                                   |
+| Paging the Manager first                                | Query stored decisions first; a past ruling may already answer it (`mcp-decision-server/server.py:1644-1661`).                                                    |
+| Expecting a short query result                          | There is no result cap (`mcp-decision-server/server.py:1741-1742`).                                                                                               |
+| Passing `None` for `fidelity`/`mode`/`scope`/`goal_ref` | Treated as unset; the server applies `verbatim` / `manual` / `episode` / `""` (`mcp-decision-server/server.py:1593-1599`).                                        |
+| Treating auto-record as allowed                         | It is forbidden. Every persist passes the Manager confirm gate and `record_manager_decision` (`mcp-decision-server/detector.py:1-20`).                            |
+| Expecting `propose_profile_evolution` to write          | It writes nothing; it returns a draft for approval (`mcp-decision-server/server.py:1786-1799`).                                                                   |
+| Expecting a blocked pull to break reads                 | A failed pull degrades to local state with a stderr note; reads still work (`mcp-decision-server/server.py:1663-1669`).                                           |
+
+## Recommended Workflow
+
+1. **Session open:** call `get_sync_status` so pending push debt is visible (`mcp-decision-server/server.py:1747-1750`).
+2. **Before asking the Manager:** call `query_manager_decisions` with keywords from the question. Decide from the record when a ruling covers it (`mcp-decision-server/server.py:1644-1661`).
+3. **Resolving ambiguity:** call `get_manager_profile` for the standing judgment (`mcp-decision-server/server.py:1761-1770`).
+4. **Mid-session ruling:** call `record_manager_decision` immediately, while the verbatim quote is still exact (`mcp-decision-server/server.py:1552-1585`).
+5. **Before closing a task:** call `extract_session_decisions`, then queue each candidate through `record_manager_decision` — never persist raw extractor output (`mcp-decision-server/server.py:1264-1294`, `:1552-1585`).
+6. **Roughly once per sprint:** call `propose_profile_evolution` and present the draft for approval (`mcp-decision-server/server.py:1786-1799`).
+
+Sync is pull-before-read and pull-before-write (`_ensure_fresh`, `mcp-decision-server/server.py:168`), and the server never commits or pushes; a human or the sanctioned commit path does that.
+
+## Doc Drift (Reported, Not Fixed)
+
+These divergences exist in the source as of commit `0183433`. They are recorded here for agents and maintainers. **No source file and no skill file was changed to write this page.**
+
+| ID  | Drift                                                                                                                                                | Evidence                                                                                                                                    |
+| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
+| D1  | The extraction prompt advertises only seven categories, while the validator accepts eight. The model is never told `autopilot-cycle` exists.         | prompt `mcp-decision-server/server.py:1353` vs `_VALID_CATEGORIES` `mcp-decision-server/server.py:959-962` and the inline set at `:892-894` |
+| D2  | `project_name` is hard-required but is not documented in the tool's `Args` block.                                                                    | required at `mcp-decision-server/server.py:873-874`; `Args` documents only `decision` at `:1575-1577`                                       |
+| D3  | `query_manager_decisions` has no result cap, so a large store returns full output. The literal `3` in the function is a scoring weight, not a limit. | scoring `mcp-decision-server/server.py:1713-1720`; uncapped return at `:1741-1742`                                                          |
+| D4  | `_SCRUB_FIELDS` is a dead constant — defined, never referenced. The real scrub list is hardcoded in `_scrub_free_text`.                              | definition `mcp-decision-server/server.py:193`; hardcoded leaves/targets at `:831-851`                                                      |
+| D5  | The skill text and the tool's own guidance describe different push commands.                                                                         | skill text vs the guidance carried in `get_sync_status` / `_unpushed_report` (`mcp-decision-server/server.py:177`, `:1746-1756`)            |
+| D6  | The `detector.py` module docstring cites stale `server.py` line numbers for `extract_session_decisions` and `record_manager_decision`.               | `mcp-decision-server/detector.py:1-20`; actual lines are `mcp-decision-server/server.py:1258` and `:1550`                                   |
+
+`autopilot-cycle` is accepted by the validator but is absent from the extraction prompt (D1). Note also that `_validate_against_schema` embeds a second copy of the eight-value category set inline (`mcp-decision-server/server.py:892-893`) instead of importing `_VALID_CATEGORIES` (`:959-962`) — a duplication that can drift independently.
+
+## Could Not Verify
+
+- **Generated MCP `inputSchema`.** The server was read, never executed. The JSON Schema a client derives from these signatures was not observed.
+- **`migrated_from` field.** Not defined anywhere in `mcp-decision-server/`; no behavior can be documented.
+- **Behavior against a diverged remote.** The stale-on-pull-failure path is documented from source (`mcp-decision-server/server.py:1663-1669`, `:1746-1756`, `:1760-1781`) but was not reproduced against a real diverged remote.
+
+## Related
+
+- [`docs/brain-bridge.md`](brain-bridge.md) — the Brain Bridge server that consumes these rulings in autopilot.
+- [`docs/setup.md`](setup.md) — MCP server table and start commands.
+- [`skill-templates/manager-decision/SKILL.md`](../skill-templates/manager-decision/SKILL.md) — the agent workflow around these tools.
diff --git a/docs/setup.md b/docs/setup.md
index 0ff2d9b..9dcd0fd 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -51,13 +51,13 @@ gh auth login
 
 The project uses five FastMCP Python servers, all run via `uv`:
 
-| Server               | Purpose                                           | Start Command                         |
-| -------------------- | ------------------------------------------------- | ------------------------------------- |
-| `mcp-context-server` | `.gitignore`-aware file reading, tree exploration | `uv run mcp-context-server/server.py` |
-| `mcp-memory-server`  | Persistent project memory (namespaces + index)    | `uv run mcp-memory-server/server.py`  |
-| `mcp-lint-server`    | Task file linting and Markdown validation         | `uv run mcp-lint-server/server.py`    |
-| `mcp-decision-server` | Manager-decision capture and consultation        | `uv run mcp-decision-server/server.py` |
-| `mcp-brain-bridge` | Unified Brain bridge: `brain_turn` (system-prompt loader + LLM + XML extract) | `uv run mcp-brain-bridge/server.py` |
+| Server                                        | Purpose                                                                       | Start Command                          |
+| --------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------- |
+| `mcp-context-server`                          | `.gitignore`-aware file reading, tree exploration                             | `uv run mcp-context-server/server.py`  |
+| `mcp-memory-server`                           | Persistent project memory (namespaces + index)                                | `uv run mcp-memory-server/server.py`   |
+| `mcp-lint-server`                             | Task file linting and Markdown validation                                     | `uv run mcp-lint-server/server.py`     |
+| [`mcp-decision-server`](manager-decisions.md) | Manager-decision capture and consultation                                     | `uv run mcp-decision-server/server.py` |
+| `mcp-brain-bridge`                            | Unified Brain bridge: `brain_turn` (system-prompt loader + LLM + XML extract) | `uv run mcp-brain-bridge/server.py`    |
 
 These are configured in `opencode.json` and auto-start with OpenCode.
```
<!-- END_GIT_DIFF -->
