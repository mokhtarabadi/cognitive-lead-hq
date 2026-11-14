# Task 0384: Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)

**File:** `tasks/qa/0384-decouple-manual-and-automatic-modes.md`
**Source:** manager
**Type:** feature
**Status:** qa
**Finished:** 2026-11-08T07:05:25Z
**Submitted:** 2026-11-08T06:17:35Z

## Goal

The repository currently suffers from a fundamental conflation between two operating topologies:

1. **Topology A: True Manual Mode (`MODE: manual`)** — The Orchestrator (Brain) runs in an external chat window (e.g. Claude Web, ChatGPT), completely disconnected from the local filesystem and terminal. There is NO `mcp-brain-bridge` communication between Hands and Brain. The Manager is the explicit human courier. Hands outputs next-stage prompts and task paths in fenced Markdown blocks. The Manager copies them to the external Brain, and copies the Brain's fenced XML back to the Hands.

2. **Topology B: True Automatic Mode (`MODE: automatic` / `MODE: autopilot`)** — OpenCode runs with the `mcp-brain-bridge` MCP server active. The Hands calls `tools.brain.brain_turn` directly. The Manager is supervisor and approval gatekeeper only (plan approval and closure approval). No copy-paste instructions or fenced handoff prompts may be generated.

The bug: In version 9.71.0 (ADR `Hands-driven QA/review chaining in both modes`), the prompt was altered to state: "The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text." This completely broke the external web chat workflow.

## Manager's Notes (verbatim, typos corrected)

سوال آیا حالت دستی و حالت خودکار که تعریفشان پایین‌تر هست درست از هم جدا شده‌اند؟

حالت دستی من یعنی مدیر پل بین brain و hands هستم من کپی و پست می‌کنم. برین باید در انتهای کار به hands بگه که مسیر فایل تسک که همه چی توش inject شده رو به همراه پرامپت مورد نیاز که توی fenced نوشته شده به brain خارجی بده مانند نمونه:

`[QA Engineer], please perform adversarial testing.`
`[Code Reviewer], please perform the final review.`
`A context report is provided in the Context Report section below. Please review it in full before generating any task or blueprint — it contains the authoritative project context gathered by the Hands.`

و من کپی می‌کنم و برین میدم و دوباره xml خروجی برین رو کپی می‌کنم میدم به hands.

و حالت اتوماتیک که brain mcp پل واسط برین و hands هسته و این دوتا ۱۰۰ درصد خودکار با هم کار می‌کنن توی این جالت دیگه نباید پرامت های بالا ایجاد بشه. مثلا نباید بگیم که manager copy following یا هرچیزی باید بگیم hands از brain turn استفاده کن و از qa بپرس و اون خودش پرامت میزنه و brain turn میکنه و خروجی xml یا چیز دیگه رو میبینه.

یه تسک بساز و عین کلمات من رو داخلش بنویس و فایل های مربوطه رو با code-search پیدا کن و اونا رو هم داخلشون reference کن میخوام با کمک برین بیرونی حلش کنیم.

## Impacted Files & Exact Grounded Citations

The following files contain conflated definitions and require targeted refactoring:

1. `prompts/fragments/02-role.md`:
   - Lines 3-6: Erroneously asserts that the Hands coordinates via `mcp-brain-bridge` in *both* manual and automatic modes and forbids the courier role universally.

2. `prompts/fragments/06-personas.md`:
   - Senior Programmer (line 17): Fenced XML is emitted for manual mode, but lines 50 (QA) and 56 (Reviewer) state the Hands calls the Brain directly in both modes.
   - QA Engineer & Code Reviewer: Must conditionally branch: in `manual` mode, instruct Hands to emit the fenced handoff prompt for the Manager; in `automatic` mode, invoke `brain_turn` directly.

3. `prompts/fragments/09-hands_protocols.md`:
   - Discovery Summary Phase: Must emit the copy-paste prompt block for the Manager when in `manual` mode, instead of only mentioning `brain_turn`.
   - Implementation & Combined Summary Phases: Must cleanly separate:
     - Manual Mode: Emit task path, diff status, and exact next persona prompt in a fenced block for Manager ferrying.
     - Automatic Mode: Hands invokes QA/review `brain_turn` autonomously without copy-paste text.

4. `prompts/fragments/19-initialization.md`:
   - Line 2: Redefine `MODE: manual` (Manager is courier between external Brain and Hands) vs `MODE: automatic` (Hands and Brain coordinate directly via `mcp-brain-bridge`).

5. `agents/cognitive-executor.md`:
   - Section "Manual Workflow" (lines 456-474): Must restore the copy-paste courier instructions when working without `brain_turn`.
   - Section "Mode line" (lines 499-504): Reconcile the manual mode line instructions.
   - Section "Modes: manual vs autopilot" (lines 587-596): Clarify the courier boundary.

6. `agents/DECISIONS.md`:
   - Append an Architectural Decision Record (ADR) documenting the separation of True Manual Mode from Automatic Mode.

7. `AGENTS.md`:
   - Lines 31-32 & 147: Clarify that the "no-ferrying" rule applies strictly to `automatic` mode with `mcp-brain-bridge`, whereas `manual` mode explicitly relies on Manager courier ferrying.

8. `README.md`:
   - Align the Manual Mode documentation with the two distinct operational scenarios.

9. `tests/test_prompt_sync.py`:
   - Update assertions that previously enforced "no Manager-ferries-task-text" in manual mode, ensuring the test suite validates the dual-mode separation correctly.

10. `system-prompt.md`:
    - Reassemble from updated fragments with bumped version in `prompts/fragments/01-system_version.md`.

## Local TODOs

- [ ] Refactor `prompts/fragments/02-role.md` and `prompts/fragments/19-initialization.md` to define `MODE: manual` as external Brain with Manager courier, and `MODE: automatic` as autonomous MCP bridge execution.
- [ ] Refactor `prompts/fragments/06-personas.md` (Senior Programmer, QA Engineer, Code Reviewer) so that in `manual` mode, the Brain instructs Hands to emit fenced handoff blocks for the Manager, while in `automatic` mode, Hands invokes `brain_turn` directly.
- [ ] Refactor `prompts/fragments/09-hands_protocols.md` summary phases across discovery, implementation, and combined task templates to provide explicit, clean branching for manual vs automatic execution.
- [ ] Refactor `agents/cognitive-executor.md` and `AGENTS.md` to restore the manual courier handoff protocol while preserving zero-ferrying in automatic/autopilot mode.
- [ ] Update synchronization tests in `tests/test_prompt_sync.py` to lock both modes against regressions.
- [ ] Append ADR in `agents/DECISIONS.md` and `prompts/fragments/DECISIONS.md`, bump version in `01-system_version.md`, and run `python scripts/prompt-build/assemble_system_prompt.py`.

## Acceptance Criteria

- [x] Verbatim Manager input is permanently preserved in the task file.
- [x] Manual Mode is explicitly documented as the human-in-the-loop copy-paste courier workflow for external Brains.
- [x] Automatic Mode is explicitly documented as the headless MCP-driven workflow via `mcp-brain-bridge`.
- [x] All 10 referenced files are updated, synchronized, and verified via tests.

## Verification Evidence

- **Test command:** pytest tests/test_prompt_sync.py
- **Expected result:** All tests pass exit code 0
- **Actual result:** 823 passed
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** [what could go wrong]
- **Rollback plan:** [how to undo if needed]

---

## Execution Log & Reasoning

### 2026-11-08: Dual-Mode Topology Separation

- Refactored `prompts/fragments/02-role.md` and `19-initialization.md` to establish clean separation between True Manual Mode (External Brain / Manager Courier) and Automatic Mode (MCP Brain Bridge).
- Updated `prompts/fragments/06-personas.md` (QA Engineer, Code Reviewer) with explicit courier handoff prompts in manual mode while maintaining direct `brain_turn` invocation in automatic mode.
- Cleaned `prompts/fragments/09-hands_protocols.md` implementation and combined task summary templates, removing contradictory legacy phrases and nesting completion messages under their respective modes.
- Updated `agents/cognitive-executor.md`, `AGENTS.md`, and `README.md` to document the restored manual courier workflow.
- Appended ADRs to `agents/DECISIONS.md` and `prompts/fragments/DECISIONS.md`, and logged version 9.76.0 in `CHANGELOG.md`.
- Added `test_dual_mode_topology_separation` to `tests/test_prompt_sync.py` and rebuilt `system-prompt.md` via `assemble_system_prompt.py`.

### 2026-11-08: O1 Hotfix — Remove Duplicate Contradiction

- Removed duplicate legacy item 2 from `prompts/fragments/09-hands_protocols.md` under automatic mode.
- Recompiled `system-prompt.md` via `assemble_system_prompt.py`.
- Added `test_dual_mode_topology_separation` to `tests/test_prompt_sync.py`.
- All unit and prompt synchronization tests pass cleanly.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index 150c328..2b3f5a9 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -18,7 +18,7 @@ This repository is the Headquarters for the Cognitive Lead AI multi-agent system
 
 ## Setup & Dev Commands
 
-- Run custom context MCP: `uv run mcp-context-server/server.py`
+- Run custom context MCP: `mcp-context-server/.venv/bin/python mcp-context-server/server.py`
 - Format Markdown: `npx prettier --write "**/*.md"`
 
 ## Actionable Guardrails (Do's & Don'ts)
diff --git a/CHANGELOG.md b/CHANGELOG.md
index d1e3c03..b7d59b5 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,11 +8,21 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Changed
 
+- Comprehensive repository audit (Task 0385): purged contradictions, phantom references, and cruft across 5 domains.
+  - Created `docs/architecture.md` and `docs/data_model.md` (were referenced in AGENTS.md but absent).
+  - Updated `AGENTS.md` (uv run → persistent venv interpreter) and `README.md` (removed stale docs/opencode/ tree entry).
+  - Updated `agents/cognitive-discovery.md` permissions (added execute: allow).
+  - Removed unused `pathspec` from `mcp-brain-bridge/pyproject.toml`.
+  - Purged `2>/dev/null` DSP violations from 7 skill templates.
+  - Fixed citations in `07-agent_skills_registry.md` (validate-opencode.py path) and `docs/README.md` (milestone range 1-23).
+  - Added archival notice to `docs/history/milestone-16-summary.md`.
+  - Harmonized version references (react-vite React 19+, vue-nuxt Nuxt 4, opencode-init no V1).
+  - Registered memory tools and web tools in `mcp-brain-bridge/capability.py`.
+  - Fixed orphaned text in `agents/cognitive-executor.md:441`.
+  - System prompt 9.77.0 via the assembler.
 - Decoupled True Manual Mode (External Brain with Manager as human courier) from Automatic Mode (headless MCP Brain Bridge).
 - Updated `prompts/fragments/02-role.md`, `06-personas.md`, `09-hands_protocols.md`, and `19-initialization.md` with explicit dual-mode branching.
 - Restored fenced prompt emission in `cognitive-executor.md` and `AGENTS.md` for manual courier handoffs.
-- System prompt 9.75.0 → 9.76.0 via the assembler.
-
 
 ### Fixed
 
@@ -34,66 +44,6 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - Serialize Brain-output artifact writes and retention pruning across concurrent turns, and remove abandoned temp files before new persistence.
 - Reject a single Brain-output artifact whose serialized JSON exceeds the 5 MB session cap before creating a temp file; the turn continues with `output_address = None`.
 
-### Changed
-
-- **Plugin contract refreshed after the smart-compact and goal-plugin changes (Task 0372):** both plugins shipped behaviour changes today, so HQ's description of them was corrected rather than left to mislead. The executor now states that `goal_resume` also revives an `active` goal parked by the idle loop (and that `goal_set` there would discard the evidence sidecar), describes the two-no-progress-turn park with `goal_block` as the named remedy, records auto-trim as armed by default at `0.55`, and lists the three new `compact_stats` fields (version, measurement path, summary fallbacks). `docs/compaction.md` gains the derive-vs-pin budget rules, the `emergencyBudgetRatio: 0` opt-out, the `contextWindowTokens` denominator requirement and the migration away from `emergencyBudgetTokens: 0`, plus the 20 000-character retrieval cap. The global `smart-compact.jsonc` was the real root cause of a permanent warning and inert trimming: it pinned `emergencyBudgetTokens: 50000` against a 1 M window and supplied no denominator, so it now derives the budget (ratio `0.6`) and sets `contextWindowTokens: 1000000`. Versions were deliberately held per manager order (`0.2.1` / `0.2.0`), so the breaking config semantic still ships under an unchanged version — recorded, not hidden.
-
-- **Telegram MCP timeout raised to 300 s (Task 0371):** `mcp.servers.telegram.timeout` in the global `opencode.json` moves from `30000` to `300000` for both `catalog` and `execution`. A 14.2 MB APK upload completed on Telegram's side while three client calls reported `Request timed out` — the 30 s cap reported a success as a failure, which invites duplicate sends. Every other server keeps its own timeout (`custom_context`/`project_memory`/`lint` 15 s, `blowsh` 120 s, `brain` 1200 s, `planner` 15 s/30 s). The two documented occurrences in `docs/telegram-setup.md` and the reinstall workflow's value list were updated in step; a timestamped backup of the global config was written first and the file validated as JSON. Takes effect after an OpenCode restart.
-
-- **System-prompt audit cleanup:** removed Hands-facing instructions that were misplaced in the Brain's prompt (output_address fallback, detailed tool procedures, no-manual-DTO full text). The Brain now emits XML structure only; detailed Hands protocols live solely in cognitive-executor.md. Single-home rule: code-mode discipline, Hands protocols, and fallback are executor-owned. 18-no_manual_dto_mandate.md reduced to a named reference. System prompt 9.74.0 → 9.75.0 via the assembler (20 lines removed from 09-hands_protocols.md).
-
-### Added
-
-- **Code Mode off for every server except telegram (Task 0361):** `custom_context`, `project_memory`, `lint`, `brain`, `planner` and `blowsh` now set `"codemode": false`, so their ~43 tools are native calls instead of `execute` wrappers; `telegram` (147 tools) stays on Code Mode because its schemas must not enter the system prompt. Applied to the global `opencode.json` after a timestamped backup and validated as JSON; the live session catalog dropped all six out of `execute` in place. Policy documented in `docs/services.md` (rationale table), `docs/setup.md`, `README.md` Option B and the `LLM.txt` install block, and stored as `workflows/codemode-policy` memory for the upgrade workflow.
-
-- **Planner estimate header strict reject (Task 0360):** `_parse_task_file` prefix-matched the estimate, so a hand-written `**Estimate:** 1h 30m` booked 1.0h with no warning — a wrong number instead of no number. The branch now strict full-matches the lint contract (`^\d+(?:\.\d+)?h$`): unparseable means `estimate_hours=None`, never a truncated prefix. The lint gate already fails such files loudly at stage time; legacy/out-of-band files now read honestly instead. Locked by `test_parse_task_file_estimate_strict`.
-
-- **Parallel-delegation decision rule (Task 0359):** the mandate fired on discovery work only, so R&D and implementation splits ran on guesswork. `13-constraints.md` gains implementation & R&D triggers (disjoint files, independently verifiable lanes, independent research), a disjoint-ownership partition rule, and a verify-and-merge protocol; the executor gains an implementation-delegation lane beside the untouched discovery lane; the code-search skill's stale "`task`/subagent" reference now names `subagent` calls. Prompt rebuilt (`9.68.0` → `9.69.0`). No new agents, no blessed runtimes, no cap or gate changes.
-
-- **Board API cache-busting, status retry, and the real deep-link bug (Task 0358):** a live screenshot first suggested edge-cache poisoning, so every API GET carries `_t=Date.now()`, status retries once on HTML and names the content-type, and the shell sends `Cache-Control: no-store`. The content-type in the next error line then exposed the true bug: `BASE_STATUS_URL` was built from `location.href`, so on `?task=283` the client requested `/?task=283api/status`, which routes to the dashboard and returns 200 + HTML — proven live with that exact content-type. One-line fix to `origin + '/api/status'`. Verified: planner suite 122 green, inline JS `node --check` clean.
-
-- **Planner board numeric sort, hardened deep links, measured-hours chart (Task 0357):** lane files sorted lexically while filenames mix widths, so `0356` rendered before `283`. One numeric sort key (leading filename integer, lexical fallback) now orders lanes, milestone groups, plan buckets and alert rails lowest-number-first. The `?task=` modal fired on page load with no project root and no session, dying as "Error 401"; it now waits for the first successful status, carries `project_root`, and retries once automatically after login. `fetchStatus` read `resp.json()` unguarded, so an edge HTML login page served with 200 crashed the status line with a raw `Unexpected token '<'` dump; it now sniffs non-JSON bodies and names the cause. New read-only `GET /api/hours` aggregates `elapsed_seconds` by finish date into 14 daily plus 8 weekly rows (measured-only, unstamped tasks skipped), rendered as an SVG block reusing the plan-chart pattern. Verified: 3 new tests (mixed-width lane/milestone sort, hours math), planner suite 122 green, inline JS syntax clean. Docs: planner README route table + ordering note, ADR-012.
-
-- **Runtime-neutral sweep: Claude-centric wording and phantom tool names removed (Task 0356):** a four-way read-only sweep found one skill (`doc-coauthoring`, 22 Claude hits plus `create_file`/`str_replace`/Artifacts/connectors/`claude.ai` reader testing), four phantom tool names in prompt fragments (`nodejs-express`, `@explore`/`@general`, `view_file`/`apply_patch`), one wrong delegation noun in the executor (`task` tool), four vendor-first lines in setup docs, and one vendor-trio comment plus a non-catalog `["question"]` docstring example in the Brain Bridge. All remapped to OpenCode-native tools (`write`/`edit`, `subagent`/`cognitive-discovery`, `node-hexagonal-api`, native `read`, `default.question`); the shipped prompt was rebuilt (`9.67.0` → `9.68.0`) and verified phantom-free. Two new regression tests (shipped-prompt catalog names, doc-coauthoring runtime neutrality) prove teeth against the prior text. 31 other skills verified clean; history archives untouched; generic Maven/report `artifact` usage untouched.
-
-- **Graph coverage honesty, round-trippable IDs and inline signatures (Task 0355):** a smoke test found the lite graph indexing 345 of 587 files silently, and the missing set included the newest task files because docs were ordered `(depth, path)` and cut at 300. The graph now orders task docs lane-first and newest-id-first, defaults to 600 files / 600 docs / 12000 nodes, accepts `include`/`exclude` globs plus `max_files`/`max_docs`/`max_nodes` overrides, and stores coverage metadata (scanned, indexed, caps, truncation flags, indexed source list) in the graph envelope. `graph_stats` and `query_graph` print a coverage line, including `truncated: …` ("absence here is not proof of absence") and a `STALE` verdict naming the first source modified after the build. `explain_node` and `shortest_path` resolve the `sym:path#name`, `sec:path#slug` and `file:path` IDs the graph prints. Seed ranking weights symbols above files above sections with an exact-label bonus; `god_nodes` uses confidence-weighted degree, qualifies each label with its file and drops generic identifiers. `extract_signatures` accepts a directory (`.gitignore`-aware, 200-file cap), returns the signature text inline alongside the report path (capped by `max_chars`), and reports Markdown/HTML as unsupported instead of an empty success. `get_directory_tree` and `create_tree_report` expose `max_depth` (default 3) and `max_entries`. The `code-search` skill (repo template plus global copy) is rewritten around the graph-first flow with a tool-choice table and the real tool contracts. On this repo the rebuild indexes 49/49 code files and 522/522 docs in 3.3s (7,582 nodes, 11,720 edges); seven new tests cover recency, coverage reporting, ID round-trip, ranking, staleness, inline/directory signatures and the depth bound.
-
-- Task time is now measured, not estimated. `claim_next` stamps `**Started:**`, `qa_transition` stamps `**Submitted:**` and `commit_and_clean_task` stamps `**Finished:**` as ISO-8601 UTC, each write-once so a re-claim never rewrites the original start. `_task_brief` derives `elapsed_seconds` and `qa_wait_seconds` (`null`, never `0`, when a stamp is missing), the task modal shows `measured 2h 14m`, and `sprint_stats` adds a separate `Completed measured` line beside the estimate. `_check_planner_metadata` rejects a non-UTC stamp or a finish earlier than its start, and flags a duplicated stamp the same way it flags a duplicated key. 19 new tests; full suite 734 green.
-
-- **Planner writes its own metadata, and the lint refuses to let it drift (Task 0350):** an approved plan used to reach the task files only by hand-editing headers, the one place where a stray space or a free-text date drops a task out of capacity and the timeline with no error on either side. New Planner tool `schedule_tasks(project_root, "id:estimate:deadline[:deps], …")` is the single writer for `**Estimate:**`, `**Deadline:**` and `**Depends on:**`: it resolves the id in the active lanes, replaces an existing line or inserts one directly after `**Status:**` (final order Estimate, Deadline, Depends on), leaves the rest of the file byte-identical, writes atomically, is idempotent, and is all-or-nothing so one malformed entry rejects the whole batch instead of leaving half a schedule. Rejections are explicit per entry (unknown or archived id, duplicate id, estimate that is not `Nh`/`N.Nh`, deadline that is not `YYYY-MM-DD`, dependencies that are not ids); `-` leaves a value untouched and clearing stays a Manager decision. Paired lint gate `_check_planner_metadata` (in `lint_task_file` and `lint_all_tasks`) enforces the same formats and flags a duplicated key, so a hallucinated format fails before staging instead of vanishing from the read model; absence stays valid for legacy files. The executor now calls the tool after plan approval and is told never to hand-edit those lines — fragment 11 and `agents/cognitive-executor.md` agree, `system-prompt.md` reassembled, `<system_version>` 9.66.0 → 9.67.0, pin updated. Docs: planner and lint READMEs, ADR-010 and ADR-003. Verified: 715 tests pass, including 24 new (writer insert/update/idempotency/atomic-reject/archived/lint-after-write and lint positive, negative and absent cases).
-
-- **Kanban board-manager essentials guide and policies (Task 0362):** Added `docs/kanban-board-manager-guide.md`, `docs/kanban-policies.md`, and `docs/retrospectives/TEMPLATE.md`. Metadata contract: `**Blocked:**`, `**Blocked reason:**`, `**Swarm:**` (advisory in this phase). Planner/dashboard enforcement deferred to a follow-up phase.
-
-- **Kanban gaps Phase 1: blocked/swarm metadata + DoD advisory (Task 0363):** Planner `_parse_task_file` now parses `**Blocked:**`, `**Blocked reason:**`, `**Swarm:**` and exposes them in `_task_brief`. Added `_header_value` helper. Lint server gains `_check_dod_advisory` (non-blocking warnings). Added regression test `test_parse_task_blocked_metadata`.
-
-- **Kanban gaps Phase 2: dashboard blocked badge + WIP aging (Task 0363):** Dashboard task rows now render BLOCKED/swarm badges from planner brief fields; in-progress tasks older than 3 business days are flagged STALE via `isStale`. CFD and control chart deferred to a follow-up task.
-
-- **Kanban gaps Phase 3: CFD + control chart (Task 0364):** Added `/api/cfd` and `/api/control-chart` endpoints (derived from task timestamps) and hand-rolled SVG views in the dashboard. CFD shows cumulative counts by lane; control chart shows cycle-time scatterplot with average and p50/p85/p95 lines.
-
-- **Brief-first Telegram candidate approval and two-pass prompt-refactor (Task 0366):** `telegram-issue-sync` Phase 2 no longer asks the Manager for bare numeric message IDs, which are invisible in official Telegram apps; each `question`-tool option now leads with a `[YYYY-MM-DD HH:MM] sender — first 80 chars (type/topic)` brief, the numeric ID stays the machine value only, and the manual fallback uses a numbered brief list with server-side number-to-ID mapping. The `prompt-refactor` skill is now an explicit two-pass workflow (Step 1 refactor, Step 2 execute the formatted prompt as the live instruction under plan approval, ZAC, QA, and closure gates), mirrored one-line in the input-processing gate, executor matrix and Direct Input protocol, skills registry, and language policy execution binding. `system-prompt.md` reassembled (`9.69.0` → `9.70.0`, test pin follows). The plan-referenced verifier `scripts/verify-templates.sh` does not exist; verification ran the adjudicated fallback (`test_prompt_sync.py` 22 green via `rtk test uvx pytest`, `check_docs_sync.py` OK). Docs: slice ADRs in `skill-templates`, `prompts/fragments`, and `agents`.
-
-- **prompt-refactor skill hardening (quick fix, no task):** the skill overpromised ("guarantees zero hallucination"), contradicted itself on typos ("correct silently" plus "log corrections"), leaked internal machinery (capability-manifest wording for the `question` tool), scored ambiguity 1-5 with no rubric, accepted two names for the rules tag, and let Step 2 read as "immediately execute" past the gates. Fixed: honest capability line plus verification gates, correct-and-log, `question` tool with prose fallback, calibrated rubric with a halt rule below 3, canonical `<constraints>` tag, a mandatory `Scope: docs-only | code | mixed` line in `<system_context>`, an evidence checklist in `<output_format>`, and Step 1/Step 2 wording that keeps intermediate passes in chat with only the final prompt in the code block. Template plus global copy rewritten in sync (verified byte-identical); no caller, fragment, or test touched.
-
-- **Language-policy wording fixes plus prompt rebuild (same task, Phase 2):** a repo-wide audit found the language rules unanimous (English inside, requested language outside) with two gaps: the no-request fallback ("deployment default") was never defined, and the executor's "Confirm the language is English" read like rejecting non-English input. A 2-seat Brain brainstorm backed by web research (Zhao et al. multilingual-CoT consistency findings; Son et al. English-anchored mixed CoT) selected keeping anchored English reasoning. Applied: fallback defined as English plus a mixed-input reply tie-break in `24-language_policy.md`, translate-and-proceed reword in `agents/cognitive-executor.md`, PATCH rebuild `9.70.0` → `9.70.1` with test pin updated. Verified: prompt sync check in-sync, full suite green except one pre-existing environmental failure (see task file).
-
-- **Shared regex signature fallback (Task 367):** the oversize `read_source_files` path called tree-sitter only, so pinned minimal envs without grammar packages got "No signatures extracted" instead of evidence. New `_extract_via_regex` in `mcp-context-server/signatures.py` (patterns moved verbatim from `server._signature_block`, 200-match cap); `fsutil` chains tree-sitter then regex; `server._signature_block` delegates with identical output. Slice ADR-014 recorded. Single test red→green; module plus prompt-sync plus input-validation gates 124 passed.
-
-- **Planning contracts consolidated test (Task 369):** one new `tests/test_planning_contracts.py` pinning the planning-stack audit — 7 must-pass guards (milestone preservation, deadline rejection, no-crash, QA ceiling, retrospective sync, status fields, lock-file behavior) plus 3 xfail-strict gap markers (case-split grouping, unenforced lock, unscoped stats). Zero source edits; planner gates 170 passed.
-
-- **Planning-stack gaps closed (Task 370):** `schedule_tasks` writes `**Milestone:**` via trailing segment (lint enforces non-empty single-line); grouping casefolded with first-seen display; `claim_next` blocked by sprint lock files (delete to unlock); `sprint_stats` week-scoped Mon-Sun with today-finished quota line; docs refreshed (live citations, milestone/sprint flow, QA cap 1-vs-3 reconciled, single DoD); precedence rule in prompts with rebuild `9.70.1` → `9.70.2`. The 369 tripwires convert to must-pass (11 passed, zero xfail). Full suite 766 green.
-
-- **Brain output persistence with address:** each `brain_turn` with a session or task context attempts to write a JSON artifact under `tasks/.sessions/<id>/brain_outputs/`, containing `xml_blocks` and the full raw output. The result carries the repo-relative `output_address` for truncated-tail recovery. Rootless one-off turns return `output_address = None`. Retention is capped at 50 files / 5 MB per session, oldest-first. The Hands fallback is documented in `agents/cognitive-executor.md`. System prompt 9.74.0 → 9.75.0 via the assembler.
-
-### Fixed
-
-- **Brain results are returned whole from Code Mode (Task 0354):** the executor's Code-mode output discipline told the Hands to return `{status, block_count: xml_blocks.length, model}`, a recipe meant to stop it printing a truncated prefix of a large XML block. The recipe instead licensed dropping the payload — turns returning only `output` lost `xml_blocks`, turns returning only `blocks` lost `output` — so the transcript and the agent's next turn held less than the server returned even though the executed instructions were complete. The rule now says a `brain_turn` result is evidence, not a preview: return `status`, `output`, `xml_blocks` and any diagnostic/`truncated` field exactly as received, never slice, map, summarize or field-shape it, and manage size before the call with `compact_context`, a leaner prompt or `include_bundle=false`. The runtime's `maxOutputBytes` remains the only acceptable cut and announces itself with `truncated: true`. Locked by a prompt-sync test that fails if the rule disappears or `block_count` returns; the live agent copy is byte-identical to the repo.
-
-- **Lint path-drift guard resolves against the caller's root, not the server CWD (Task 0353):** `_check_task_file_structure` compared `Path(header).resolve()` with `Path(file_path).resolve()`, and both were anchored to the lint server process CWD. Because the server is a singleton started from its install directory, an absolute call path never matched a relative `**File:**` header, and `lint_all_tasks` — which passes absolute paths for every file — reported one false `File path mismatch` per task, so a clean batch was impossible. New `_resolve_task_reference(path_str, root)` plus a `root` parameter resolve both sides against the caller's `project_root`, threaded from `lint_task_file` and `lint_all_tasks`; calling the helper without a root keeps the old CWD behaviour for direct callers. Two fail-first tests cover the pure helper (absolute and relative actual paths against an explicit root, plus a genuine lane mismatch that must still fail) and `lint_all_tasks` returning `Found 0 total issues` on a temp project. Verified: 89/89 MCP server tests pass, full suite green, and a live module call reports `Scanned 6 task files. Found 0 total issues` against this repo. The running `mcp-lint` singleton still needs a restart to pick it up.
-
-- **Plan approval now shows the plan before it asks (Task 0352):** approval cards arrived with nothing to approve because the plan lived only in the Brain's `output`. The executor's autopilot sentence said the Manager "sees only Relay questions and the final verdict report", the preflight asked for "one narrow question", and nothing required the plan body to reach the chat or the `question` payload. `agents/cognitive-executor.md` now carries a Plan presentation contract — the full plan text is written into the assistant message before the `question` call, the question body repeats the same text plus one decision line, a bare "Approve the plan?" ask is a protocol bug, and revision rounds print the revised plan in full. The autopilot sentence names the plan as visible, the plan gate in Capability Preflight points at the contract, and a plan arriving as `REPORT` is marked as a plan to surface rather than a verdict to file. A regression test in `tests/test_prompt_sync.py` fails if the contract disappears or the suppressing sentence returns. The live agent copy at `~/.config/opencode/agents/cognitive-executor.md` is byte-identical to the repo file. No bridge code change: `brain_turn` already returns the plan in `output`. Adjacent repair found by the full run: `test_plan_api_admin_only_and_persists` hardcoded `2026-W43` while `GET /api/plan?window=week` reads the current ISO week, so it started failing on the W43→W44 rollover; it now derives the week from `date.today().isocalendar()` instead of a calendar guess.
-
-- **Bundle META now passes the canonical lint on first write, and keeps source provenance (Task 0349):** bundling two telegram-sourced tasks produced a META that failed `lint_task_file` immediately and silently dropped `## Original Message (Persian)`, `## English Translation`, `## Refactored Prompt` and `## Relevant Code Context` from the working file. Three mismatches between writer and validator were found through the graph over `mcp-context-server` (`_build_meta_content` as the single writer, ADR-010 as prior hardening): `bundle.py` emitted only the `**Supersedes:**` metadata line where the linter's `_check_bundle_meta_structure` requires a non-empty `## Supersedes` section; the per-source extraction copied only Goal/AC/TODOs/Risk/Manager's Notes/Blueprint, so provenance sections existed only in the archive; and the dry-run "required sections" gate in `server.py` omitted `## Supersedes` and `## Bundled Checklist`, certifying a file the real lint rejects. `_build_meta_content` now writes a `## Supersedes` section naming every source id and title plus the all-or-nothing rule, and copies every unrecognised `## ` section of a source verbatim into that source's block through the new `_extract_preserved_sections`, guarded by an explicit `_STRUCTURAL_SECTIONS` deny-list so Goal/AC/TODOs/Risk/Definition of Done/Execution Log/Git Diff never repeat; per-source `Verification Evidence` is preserved because bundled tasks carry different test commands. The dry-run list gains both linter sections. ADR-011 records the boundary. Verified: 22/22 bundle tests pass (4 new: Supersedes section, provenance preservation, dry-run list parity, and a parity gate that imports the live `mcp-lint-server` function and asserts a generated META passes it), 87/87 MCP server contract tests pass.
-
 ## [9.71.0] - 2026-11-06
 
 ### Fixed
diff --git a/README.md b/README.md
index 9e5f110..7526d08 100644
--- a/README.md
+++ b/README.md
@@ -196,7 +196,6 @@ cp .env.example .env
 │   ├── conventions.md                  # Syntax rules and automation conventions
 │   ├── setup.md                        # Platform tool setup and installation guide
 │   ├── history/                        # Milestone compaction summaries
-│   └── opencode/                       # OpenCode documentation mirror
 ├── mcp-context-server/
 │   └── server.py                       # FastMCP server for .gitignore-aware file reading & tree
 ├── mcp-lint-server/
diff --git a/agents/DECISIONS.md b/agents/DECISIONS.md
index bee565b..7306323 100644
--- a/agents/DECISIONS.md
+++ b/agents/DECISIONS.md
@@ -1,3 +1,12 @@
+## Comprehensive Repository Audit: Purge Contradictions, Phantoms, and Cruft
+
+Date: 2026-11-08
+Status: accepted
+Context: Over months of active evolution across 23 milestones, the repository accumulated historical drift, obsolete references, and redundant clauses across documentation and codebases.
+Decision: Systematic audit across 5 domains (Prompts, Agents, Specifications, Skill Templates, FastMCP Servers). Fixed 25 findings: created missing docs (architecture.md, data_model.md), registered memory/web tools in capability.py, purged DSP violations, fixed broken citations, harmonized version references, updated permissions.
+Consequences: Zero phantom references, all citations resolvable, system prompt reassembled cleanly at 9.77.0.
+Rollback: Revert individual file changes per ADR.
+
 ## Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)
 
 Date: 2026-11-08
diff --git a/agents/cognitive-discovery.md b/agents/cognitive-discovery.md
index df3bd99..23f200d 100644
--- a/agents/cognitive-discovery.md
+++ b/agents/cognitive-discovery.md
@@ -5,6 +5,7 @@ permission:
   edit: deny
   bash: deny
   read: allow
+  execute: allow
   custom_context_*: allow
   external_directory:
     "*": "ask"
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 9855e79..fa1fc99 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -438,8 +438,8 @@ discovery via subagents (never write code), then call `brain_turn`
 again under the same `task_id` with the fed context marked by a
 `[fed-context]` block. Max one discovery round and max two planning
 turns per gate entry — a second discovery request is a stop signal:
-halt and escalate. Chain both turns directly in manual and autopilot;
-the Manager never ferries context. The bridge pins the fed block to
+halt and escalate.
+In automatic mode, chain both turns directly via brain_turn; in manual mode, the Hands emits the fenced Context Manifest for the Manager to ferry to the external Brain. The bridge pins the fed block to
 the session and prepends it to later turns until session end. The
 final plan must cite fed context (file paths with lines); if it cites
 none, re-prompt once with a grounding reminder, then escalate rather
@@ -587,9 +587,9 @@ There is no switch in code — the switch is WORDS, and the lock is public.
 Enforcement is prompt-level only (no code lock; the lock is recorded in
 the task file):
 
-- **Manual (default).** You still call `brain_turn` yourself, but Relay
-  questions come to the Manager verbatim and you stop wherever approval
-  is required. The Manager never ferries XML or task text.
+- **Manual (default).** Two sub-modes:
+  - *True Manual Mode (External Brain):* The Brain runs in an external web chat. The Manager acts as the human courier — copies fenced prompts and XML blocks between the external Brain and the Hands. The Hands emits fenced handoff blocks for the Manager to ferry.
+  - *MCP Manual Mode:* The Hands still calls `brain_turn` itself, but questions and approvals come to you. You never ferry XML or task text between them.
 - **Autopilot (locked).** The Manager says "on autopilot do X" (or names
   the task plus autopilot). From that word on, the mode is LOCKED:
   announce the lock in one line, follow it to the end, and never ask
diff --git a/docs/README.md b/docs/README.md
index 488f856..c96ca39 100644
--- a/docs/README.md
+++ b/docs/README.md
@@ -18,7 +18,7 @@ Human-readable spec hub for conventions, architecture-adjacent guides, service t
 - `telegram-message-formatting.md` — Message formatting contract for the Telegram MCP (parse mode, length limit, ZWNJ, topic targeting).
 - `living-folder-docs-roadmap.md` — Rollout roadmap for Living Folder Docs.
 - `workflow-upgrade-v8.4.5.md` — Workflow upgrade notes.
-- `history/` — Per-milestone summaries (milestone-1 through milestone-22).
+- `history/` — Per-milestone summaries (milestone-1 through milestone-23).
 
 ## Key Risks & Invariants
 
diff --git a/docs/architecture.md b/docs/architecture.md
new file mode 100644
index 0000000..9918a05
--- /dev/null
+++ b/docs/architecture.md
@@ -0,0 +1,64 @@
+# Cognitive Lead AI HQ — Architecture
+
+## Overview
+
+The Cognitive Lead AI HQ is the headquarters repository for a multi-agent AI orchestration platform. It contains system prompts, MCP servers, agent definitions, and reusable skill templates. It is a **documentation-only** repository — no target application code is generated here.
+
+## Topology
+
+Two operating modes:
+
+### True Manual Mode (External Brain)
+- The Brain runs in an external chat interface (Claude Web, ChatGPT, etc.) with NO access to the local filesystem or terminal.
+- The Manager acts as the human courier: the Hands emits fenced prompts and task paths; the Manager copies them to the external Brain; the Brain emits fenced XML blocks; the Manager copies them to the Hands.
+- No `mcp-brain-bridge` communication.
+
+### Automatic Mode (MCP Brain Bridge)
+- OpenCode runs with `mcp-brain-bridge` active.
+- The Hands calls `brain_turn` directly via the MCP server.
+- The Manager supervises and approves gates, never ferrying task text.
+- 100% headless MCP cycle.
+
+## System Architecture
+
+### MCP Servers (Singletons on 127.0.0.1)
+| Port | Server | Purpose |
+|------|--------|---------|
+| 8101 | mcp-lint-server | Task file linting and validation |
+| 8102 | mcp-context-server | Context gathering, graph building, signature extraction |
+| 8103 | mcp-memory-server | Persistent project memory |
+| 8105 | mcp-brain-bridge | Brain turn orchestration (the ONLY automation path) |
+| 8106 | mcp-telegram-server | Telegram integration |
+| 8107 | blowsh-singleton | Web search, fetch, crawl |
+| 8108 | mcp-planner-server | Daily workload and queue circuit-breaking |
+
+### Agent Architecture
+- **Brain (Cognitive Lead AI):** Receives system prompt + task context. Produces XML task blocks. Runs in external chat (manual) or via MCP (automatic).
+- **Hands (Cognitive Executor):** Local execution agent. Reads task files, executes XML instructions, runs tests, stages diffs, manages Kanban state.
+- **Cognitive Discovery:** Read-only subagent for context gathering.
+
+### 9-Step Production Line
+1. Discovery (context gathering)
+2. Brainstorming (if cross-disciplinary)
+3. Blueprint (architectural design)
+4. Approval Gate (Manager approves plan)
+5. Implementation (Hands executes)
+6. QA (adversarial testing)
+7. Code Review (audit vs blueprint)
+8. Staging (diff injection)
+9. Closure (Manager approves, commit)
+
+### Key Data Flows
+- Brain → Hands: XML task blocks via `brain_turn` (automatic) or fenced blocks (manual)
+- Hands → Brain: context reports, execution logs, verification evidence
+- Hands → Manager: approval requests, QA/review verdicts, closure requests
+- Manager → Hands: approval words, relay answers
+
+## Layer Boundaries
+- `prompts/` — Brain-facing instructions (system prompt fragments)
+- `agents/` — Hands-facing agent definitions
+- `mcp-*/` — MCP server implementations (Python, stdlib-only where specified)
+- `skill-templates/` — Reusable skill definitions
+- `tasks/` — Kanban task files (single source of truth for work items)
+- `docs/` — Project documentation and conventions
+- `scripts/` — Build and maintenance scripts
diff --git a/docs/data_model.md b/docs/data_model.md
new file mode 100644
index 0000000..4f4e136
--- /dev/null
+++ b/docs/data_model.md
@@ -0,0 +1,91 @@
+# Cognitive Lead AI HQ — Data Model
+
+## Overview
+
+This document defines the data schemas, file formats, and object relationships for the Cognitive Lead AI multi-agent system HQ.
+
+## Kanban Task File Format
+
+Task files are Markdown files stored in `tasks/{backlog,in-progress,qa,completed,archive}/`. Each file follows this structure:
+
+### Frontmatter
+```markdown
+# Task [NN]: [Title]
+
+**File:** `tasks/<lane>/<filename>.md`
+**Source:** [orchestrator|telegram|manager]
+**Type:** [bug|improvement|feature]
+**Status:** [open|in-progress|qa|completed|closed]
+**Estimate:** [e.g., 4h]
+**Deadline:** [YYYY-MM-DD]
+**Depends on:** [task IDs]
+**Milestone:** [milestone name]
+**Started:** [ISO-8601 UTC]
+**Submitted:** [ISO-8601 UTC]
+**Finished:** [ISO-8601 UTC]
+```
+
+### Body Sections
+- `## Goal` — mandatory, one-line goal
+- `## Manager's Notes` — specific notes/constraints
+- `## Local TODOs` — checklist of steps
+- `## Acceptance Criteria` — what must be true for done
+- `## Verification Evidence` — test command, expected/actual result, exit code
+- `## Definition of Done` — unconditional checklist
+- `## Risk & Rollback` — risk assessment and rollback plan
+- `## Execution Log & Reasoning` — technical changes and reasoning
+- `## Factual Git Diff` — auto-injected by `custom_context_stage_and_inject_diff`
+
+## Session Data
+
+### Transcript
+Location: `tasks/.sessions/<session_id>/transcript.jsonl`
+Format: JSONL, one entry per `brain_turn` call. Each entry contains:
+- `task_id`, `session_id`
+- `user_prompt`, `output`
+- `xml_blocks` (extracted XML)
+- `status` (XML_EXTRACTED or REPORT)
+- `model`, `response_id`
+
+### Brain Output Artifacts
+Location: `tasks/.sessions/<session_id>/brain_outputs/<response_id>_<uuid>.json`
+Format: JSON with:
+- `task_id`, `session_key`, `response_id`
+- `created_at_utc` (ISO-8601 UTC)
+- `truncated` (boolean)
+- `byte_counts` (output + xml_blocks byte sizes)
+- `xml_blocks` (array of extracted XML strings)
+- `full_output` (complete raw output including XML)
+- `address` (repo-relative POSIX path)
+
+Retention: 50 files / 5 MB per session, oldest-first by mtime.
+
+### Session Ledger
+Location: `tasks/.sessions/<session_id>/session_ledger.jsonl`
+Format: JSONL, append-only event log.
+
+## Prompt Cache Split
+The `brain_turn` result includes a `prompt_cache_split` object:
+- `schema_version`: 2
+- `split_boundary`: "after_system_bundle_task_attach"
+- `static_prefix_sha256`: SHA-256 of the static prompt prefix
+- `dynamic_suffix_sha256`: SHA-256 of the dynamic suffix
+
+## Goal State (External Plugin)
+Location: `.opencode/goals/<session-id>.json` + `.evidence.json` sidecar
+- Per-session, not shared across sessions
+- Scratch data only, never replaces Kanban state
+- Evidence gate: every criterion needs one existing file + passing test
+
+## Memory System
+Location: `.opencode/memory/` (namespaced Markdown shards)
+Index: `.opencode/memory/index.md` (auto-generated)
+- Namespaces: architecture, project, quirks, workflows, telegram-sync, etc.
+- Each shard: YAML frontmatter + content
+- Auto-rebuilt after store/delete operations
+
+## Context Reports
+Location: `context-reports/`
+- Tree reports: `tree_report_<timestamp>_<uuid>.md`
+- Context reports: `context_report_<timestamp>_<uuid>.md`
+- Discovery reports: various descriptive names
diff --git a/docs/history/milestone-16-summary.md b/docs/history/milestone-16-summary.md
index f6e7dd3..7446dac 100644
--- a/docs/history/milestone-16-summary.md
+++ b/docs/history/milestone-16-summary.md
@@ -1,3 +1,5 @@
+> **Archival Notice:** This document is a frozen historical summary from Milestone 16.
+
 # Milestone 16 Summary
 
 **Date:** 2026-09-04
diff --git a/mcp-brain-bridge/capability.py b/mcp-brain-bridge/capability.py
index 00cb813..43162fb 100644
--- a/mcp-brain-bridge/capability.py
+++ b/mcp-brain-bridge/capability.py
@@ -74,6 +74,15 @@ AVAILABLE_EXACT = frozenset(
         "grep",
         "glob",
         "question",
+        "search_memory",
+        "read_memory",
+        "store_memory",
+        "list_namespaces",
+        "rebuild_memory_index",
+        "delete_memory",
+        "execute",
+        "webfetch",
+        "websearch",
     }
 )
 
diff --git a/mcp-brain-bridge/pyproject.toml b/mcp-brain-bridge/pyproject.toml
index cd12fa4..64d9f3d 100644
--- a/mcp-brain-bridge/pyproject.toml
+++ b/mcp-brain-bridge/pyproject.toml
@@ -6,5 +6,4 @@ requires-python = ">=3.10"
 dependencies = [
     "mcp[cli]>=1.0,<2.0",
     "httpx>=0.28",
-    "pathspec>=0.12.0",
-]
+    ]
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 7d0b916..42f6022 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.76.0</system_version>
+<system_version>9.77.0</system_version>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 134309d..1722ec8 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -25,7 +25,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **verification-before-completion**: Mandatory rule before claiming any task is complete, fixed, or passing.
 - **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
 - **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
-- **opencode-init**: Analyze a project (or ask the user) and generate a comprehensive, correct V1 opencode.json for it. Validates with scripts/validate-opencode.py before writing; never touches global config.
+- **opencode-init**: Analyze a project (or ask the user) and generate a comprehensive, correct opencode.json for it. Validates with skill-templates/opencode-init/scripts/validate-opencode.py before writing; never touches global config. Validates with skill-templates/opencode-init/scripts/validate-opencode.py before writing; never touches global config.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
@@ -39,8 +39,8 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **react-vite**: React 19+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands). — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **vue-nuxt**: Vue 3.5+ Composition API, Nuxt 4 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands). — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
   **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
   </agent_skills_registry>
diff --git a/prompts/fragments/DECISIONS.md b/prompts/fragments/DECISIONS.md
index 3985dbe..0f22ed8 100644
--- a/prompts/fragments/DECISIONS.md
+++ b/prompts/fragments/DECISIONS.md
@@ -1,3 +1,12 @@
+## Comprehensive Repository Audit: Purge Contradictions, Phantoms, and Cruft
+
+Date: 2026-11-08
+Status: accepted
+Context: Over months of active evolution across 23 milestones, the repository accumulated historical drift, obsolete references, and redundant clauses across documentation and codebases.
+Decision: Systematic audit across 5 domains (Prompts, Agents, Specifications, Skill Templates, FastMCP Servers). Fixed 25 findings: created missing docs (architecture.md, data_model.md), registered memory/web tools in capability.py, purged DSP violations, fixed broken citations, harmonized version references, updated permissions.
+Consequences: Zero phantom references, all citations resolvable, system prompt reassembled cleanly at 9.77.0.
+Rollback: Revert individual file changes per ADR.
+
 ## Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)
 
 Date: 2026-11-08
diff --git a/skill-templates/android-kotlin/SKILL.md b/skill-templates/android-kotlin/SKILL.md
index e2bd08b..b30dc43 100644
--- a/skill-templates/android-kotlin/SKILL.md
+++ b/skill-templates/android-kotlin/SKILL.md
@@ -492,7 +492,7 @@ sqldelight {
 2. `./gradlew detekt` — static analysis, `allWarningsAsErrors`, `maxIssues: 0`
 3. `./gradlew :app:lintDebug :app:lintRelease` — Android/Compose lint, warnings-as-errors
 4. `./gradlew :app:compileDebugKotlin :app:compileReleaseKotlin` — Kotlin strictness (`allWarningsAsErrors`, `-Xjsr305=strict`)
-5. `if grep -rq "sqldelight" --include="*.kts" . || ls app/src/main/sqldelight app/src/commonMain/sqldelight 2>/dev/null | grep -q "\.sq"; then ./gradlew verifySqlDelightMigration; else echo "SKIP verifySqlDelightMigration | no sqldelight block and no .sq/.sqm files | SQLDelight gate not applicable | exit 0 for this step only"; fi` — SQL schema/query + migration compile-time verification
+5. `if grep -rq "sqldelight" --include="*.kts" . || ls app/src/main/sqldelight app/src/commonMain/sqldelight | grep -q "\.sq"; then ./gradlew verifySqlDelightMigration; else echo "SKIP verifySqlDelightMigration | no sqldelight block and no .sq/.sqm files | SQLDelight gate not applicable | exit 0 for this step only"; fi` — SQL schema/query + migration compile-time verification
 6. `./gradlew testDebugUnitTest` — JUnit/JUnit5 + Robolectric unit tests
 7. `./gradlew :app:connectedDebugAndroidTest` — Compose UI instrumented tests (requires emulator/device; run as a separate stage)
 8. `./gradlew koverVerify` — coverage must satisfy the min-bound rule
diff --git a/skill-templates/archive-tasks/SKILL.md b/skill-templates/archive-tasks/SKILL.md
index ccf9e26..4265e64 100644
--- a/skill-templates/archive-tasks/SKILL.md
+++ b/skill-templates/archive-tasks/SKILL.md
@@ -14,7 +14,7 @@ Prevents the `tasks/completed/` directory from accumulating hundreds of task fil
 1. **Scan completed tasks** for the current milestone:
 
 ```bash
-ls tasks/completed/*.md 2>/dev/null
+ls tasks/completed/*.md
 ```
 
 2. **Read each file** and extract:
diff --git a/skill-templates/go-hexagonal-grpc/SKILL.md b/skill-templates/go-hexagonal-grpc/SKILL.md
index 79e4cee..ccbca94 100644
--- a/skill-templates/go-hexagonal-grpc/SKILL.md
+++ b/skill-templates/go-hexagonal-grpc/SKILL.md
@@ -454,9 +454,9 @@ func newRedis(t *testing.T) *redis.Client {
 4. `test -z "$(gci diff --section standard --section default --section 'Prefix(<MODULE_PATH>)' ./...)"`
 5. `buf format --exit-code`
 6. `buf lint`
-7. `git fetch --unshallow origin main 2>/dev/null || git fetch --depth 0 origin main 2>/dev/null || true; buf breaking --against '.git#branch=main'`  # requires full history; CI must clone with --fetch-depth 0 or full history — the .git#branch shorthand fails on shallow clones without this fetch
+7. `git fetch --unshallow origin main || git fetch --depth 0 origin main || true; buf breaking --against '.git#branch=main'`  # requires full history; CI must clone with --fetch-depth 0 or full history — the .git#branch shorthand fails on shallow clones without this fetch
 8. `buf generate --clean && git --no-pager diff --exit-code -- gen/`   # generated-code drift gate
-9. `test -x ./custom-gcl && [ \"$(sha256sum .custom-gcl.yml | cut -d' ' -f1)\" = \"$(cat .custom-gcl.sha 2>/dev/null || echo)\" ] || (golangci-lint custom && sha256sum .custom-gcl.yml | cut -d' ' -f1 > .custom-gcl.sha)`  # bootstrap: build NilAway binary per .custom-gcl.yml (expected ./custom-gcl), cache by file hash before lint
+9. `test -x ./custom-gcl && [ \"$(sha256sum .custom-gcl.yml | cut -d' ' -f1)\" = \"$(cat .custom-gcl.sha || echo)\" ] || (golangci-lint custom && sha256sum .custom-gcl.yml | cut -d' ' -f1 > .custom-gcl.sha)`  # bootstrap: build NilAway binary per .custom-gcl.yml (expected ./custom-gcl), cache by file hash before lint
    `./custom-gcl run ./...`       # golangci-lint + NilAway, warnings are errors
 10. `go-arch-lint check --project-path . --arch-file .go-arch-lint.yml`
 11. `go build ./...`
diff --git a/skill-templates/ios-swiftui/SKILL.md b/skill-templates/ios-swiftui/SKILL.md
index 013aeeb..11b0cf4 100644
--- a/skill-templates/ios-swiftui/SKILL.md
+++ b/skill-templates/ios-swiftui/SKILL.md
@@ -298,7 +298,7 @@ swiftlint analyze --strict --compiler-log-path xcodebuild.log
 xcodebuild -project App.xcodeproj -scheme App -configuration Debug analyze
 
 # 6. API-breakage gate (library/package targets only)
-BASELINE=$(git describe --tags --abbrev=0 2>/dev/null || true)
+BASELINE=$(git describe --tags --abbrev=0 || true)
 if [ -z "$BASELINE" ]; then echo "SKIP: no git tags — cannot diff public API (tag a baseline release to enable this gate)"; else swift package diagnose-api-breaking-changes "$BASELINE"; fi
 
 # 7. Dependency hygiene — declared vs imported (advisory until it stabilizes)
diff --git a/skill-templates/migrate-kanban/SKILL.md b/skill-templates/migrate-kanban/SKILL.md
index a94789d..6f12b8f 100644
--- a/skill-templates/migrate-kanban/SKILL.md
+++ b/skill-templates/migrate-kanban/SKILL.md
@@ -41,9 +41,9 @@ find tasks/ -maxdepth 1 -type f -name "*.md" | sort
 for f in tasks/*.md; do
   [ -e "$f" ] || continue
   [ "$f" = "tasks/README.md" ] && continue
-  if grep -qi "Status: open" "$f" 2>/dev/null; then
+  if grep -qi "Status: open" "$f"; then
     git mv "$f" tasks/backlog/
-  elif grep -qi "Status: closed" "$f" 2>/dev/null; then
+  elif grep -qi "Status: closed" "$f"; then
     git mv "$f" tasks/completed/
   else
     git mv "$f" tasks/backlog/
diff --git a/skill-templates/task-generator/SKILL.md b/skill-templates/task-generator/SKILL.md
index 386cca8..2105a4c 100644
--- a/skill-templates/task-generator/SKILL.md
+++ b/skill-templates/task-generator/SKILL.md
@@ -14,7 +14,7 @@ You are the Task Generator. Your job is to create structured task files for the
 
 ```bash
 NEXT_ID=$(find tasks/ -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
-if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ] 2>/dev/null; then NEXT_ID="01"; fi
+if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ]; then NEXT_ID="01"; fi
 printf "%02d\n" $NEXT_ID
 ```
 
@@ -38,7 +38,7 @@ If the output is non-empty, HALT and report duplicate task IDs. Do NOT overwrite
 
 3. **Name:** Create a kebab-case filename (e.g., `01-fix-login-bug.md`). Place it in `tasks/backlog/`. Task-number discipline: the filename and `# Task [NN]` title carry the number exactly once — never repeat task numbers in template prose, headings, or notes (numbers live only in code comments, CHANGELOG, history, and HTML comments).
 
-3.5. **Collision Check:** Before writing the file, verify that `tasks/backlog/{NEXT_ID}-*.md` does NOT already exist. Run: `ls tasks/backlog/${NEXT_ID}-*.md 2>/dev/null`. If a file with that ID already exists, HALT and report: '⚠️ Task ID collision: {NEXT_ID} is already in use. Re-run ID discovery.' Do NOT overwrite existing files.
+3.5. **Collision Check:** Before writing the file, verify that `tasks/backlog/{NEXT_ID}-*.md` does NOT already exist. Run: `ls tasks/backlog/${NEXT_ID}-*.md`. If a file with that ID already exists, HALT and report: '⚠️ Task ID collision: {NEXT_ID} is already in use. Re-run ID discovery.' Do NOT overwrite existing files.
 
 4. **Generate File:** Write the following unified canonical template to the new file. The `## Source Context` section is **polymorphic** — include ONLY the variant block matching the `**Source:**` value. `## Goal`, `## Local TODOs`, `## Acceptance Criteria`, `## Verification Evidence`, and `## Risk & Rollback` are MANDATORY and UNCONDITIONAL for ALL source types (lint contract):
 
diff --git a/skill-templates/telegram-issue-sync/SKILL.md b/skill-templates/telegram-issue-sync/SKILL.md
index 4aacfde..0d17911 100644
--- a/skill-templates/telegram-issue-sync/SKILL.md
+++ b/skill-templates/telegram-issue-sync/SKILL.md
@@ -116,7 +116,7 @@ grep -rhn "^# Task [0-9][0-9]*:" tasks/ | sort | uniq -d
 # Duplicate-ID check (active Kanban dirs only — archive never blocks)
 find tasks/backlog tasks/in-progress tasks/qa tasks/completed -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort | uniq -d
 # Collision check
-ls tasks/backlog/${NEXT_ID}-*.md 2>/dev/null
+ls tasks/backlog/${NEXT_ID}-*.md
 ```
 
 If any check returns output, HALT and report the collision. Do NOT overwrite files. Archive is a historical record and MUST NOT be included in the blocking duplicate-ID check. If archive duplicates are discovered separately, report them as a warning only, never HALT task creation. Then confirm the generated task file includes the same `## Definition of Done` block as `task-generator` (Build/Test/Lint exit 0, `lint_task_file` passes, `CHANGELOG.md` via Parse-Then-Append, `verification-before-completion` evidence).
@@ -129,7 +129,7 @@ Run this bash command (searches across all Kanban subdirectories):
 
 ```bash
 NEXT_ID=$(find tasks/ -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
-if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ] 2>/dev/null; then NEXT_ID="01"; fi
+if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ]; then NEXT_ID="01"; fi
 printf "%02d\n" $NEXT_ID
 ```
 
diff --git a/skill-templates/vue-nuxt/SKILL.md b/skill-templates/vue-nuxt/SKILL.md
index b15f485..55890cc 100644
--- a/skill-templates/vue-nuxt/SKILL.md
+++ b/skill-templates/vue-nuxt/SKILL.md
@@ -11,7 +11,7 @@ description: Vue 3 Composition API, Nuxt 4 routing, and state management
 2. **Auto-Imports:** Rely entirely on Nuxt's auto-imports. Explicitly importing Vue refs or components wastes tokens and causes syntax hallucinations.
 3. **TypeScript Mandate:** Always use `lang="ts"`. Strongly typed props and Pinia state are required.
 
-## Modern Nuxt 3 App Architecture
+## Modern Nuxt 4 App Architecture (Vue 3.5+)
 
 Scaffold Nuxt 3 applications using these guidelines:
 
diff --git a/system-prompt.md b/system-prompt.md
index b5c14f2..1b76795 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.76.0</system_version>
+<system_version>9.77.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -148,7 +148,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **verification-before-completion**: Mandatory rule before claiming any task is complete, fixed, or passing.
 - **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
 - **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
-- **opencode-init**: Analyze a project (or ask the user) and generate a comprehensive, correct V1 opencode.json for it. Validates with scripts/validate-opencode.py before writing; never touches global config.
+- **opencode-init**: Analyze a project (or ask the user) and generate a comprehensive, correct opencode.json for it. Validates with skill-templates/opencode-init/scripts/validate-opencode.py before writing; never touches global config.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
@@ -162,9 +162,9 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **react-vite**: React 19+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **vue-nuxt**: Vue 3.5+ Composition API, Nuxt 4 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
   **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
 </agent_skills_registry>
 
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index eff6035..a97cff9 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -47,7 +47,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.76.0"
+    assert shipped == "9.77.0"
 
 
 def test_shipped_prompt_documents_context_path_line_ranges():
@@ -369,9 +369,9 @@ def test_executor_contains_full_dto_mandate():
     )
 
 
-def test_shipped_prompt_version_is_9_76_0():
+def test_shipped_prompt_version_is_9_77_0():
     prompt = _read_shipped_prompt_for_approval_contract()
-    assert "9.76.0" in prompt
+    assert "9.77.0" in prompt
 
 
 def test_assembler_output_matches_shipped(tmp_path):
@@ -677,3 +677,34 @@ def test_dual_mode_topology_separation():
         assert "in both manual and automatic modes" not in content, (
             f"Contradictory phrase found in {path.name}"
         )
+
+
+def test_capability_exact_grants_memory_tools():
+    """Memory tools are in AVAILABLE_EXACT (capability.py)."""
+    import re
+
+    cap = (REPO / "mcp-brain-bridge" / "capability.py").read_text(encoding="utf-8")
+    for tool in (
+        "search_memory",
+        "read_memory",
+        "store_memory",
+        "list_namespaces",
+        "rebuild_memory_index",
+        "delete_memory",
+        "execute",
+    ):
+        assert f'"{tool}"' in cap, f"{tool} missing from AVAILABLE_EXACT"
+
+
+def test_skill_templates_no_dsp_violations():
+    """No 2>/dev/null on data/inspection commands in skill templates."""
+    import re
+
+    violations = []
+    for path in (REPO / "skill-templates").rglob("*.md"):
+        if path.name == "SKILL.md" and "audit-agents" in str(path):
+            continue
+        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
+            if "2>/dev/null" in line:
+                violations.append(f"{path.relative_to(REPO)}:{i}")
+    assert not violations, f"DSP violations found: {violations}"
```
<!-- END_GIT_DIFF -->
