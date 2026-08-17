# Task 98: System Prompt Runtime-Agnostic + Freebuff Full Support

**File:** `tasks/completed/98-system-prompt-runtime-agnostic-freebuff-full-support.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Make the Cognitive Lead AI workflow fully portable: (1) deep-research how Freebuff (Codebuff-based) defines
custom agents and global rules; (2) complete the partial Freebuff support by unblocking custom agents on the
free tier and installing a global rules file; (3) strip the "OpenCode" keyword from `system-prompt.md` and
address the local execution agent as "the Hands" with runtime-agnostic `<hands_*_task>` blocks so the same
system prompt works in OpenCode, Freebuff, or any compatible agent.

## Manager's Notes

- Freebuff custom agents = `.agents/*.ts` exporting an `AgentDefinition`; the `model` field is optional and
  omitting it falls back to the free-mode default (fixes HTTP 403 `free_mode_invalid_agent_model`).
- Freebuff global rules = home-directory files (`~/.knowledge.md`, `~/.AGENTS.md`, `~/.CLAUDE.md`);
  `~/.AGENTS.md` is the vendor-agnostic standard to install.
- The `## OpenCode Execution Log & Reasoning` section header is validated by the lint server and generated
  by the task-generator skill — rename to `## Execution Log & Reasoning` end-to-end.
- Keep OpenCode-specific docs (`docs/opencode-*.md`, `docs/opencode-schema.json`) unchanged; they are
  legitimate OpenCode references.
- Bump `<system_version>` to 8.4.5, update CHANGELOG, create this task file (AGENTS.md mandate).
- Home-dir installs (`~/.agents/*.ts`, `~/.AGENTS.md`) follow the Task 96 machine-global port pattern.

## Local TODOs

- [x] Web research: Freebuff custom agents + global rules (codebuff.com docs + binary-analysis doc)
- [x] Generalize `system-prompt.md` v8.4.5 (Hands naming, `<hands_*_task>` tags, generic tool names, header)
- [x] Update cross-references: `agents/cognitive-executor.md`, `skill-templates/task-generator/SKILL.md`,
      `mcp-lint-server/server.py`, `tests/test_mcp_servers.py`, `README.md`
- [x] Author in-repo Freebuff artifacts: `freebuff/agents/*.ts` (v1.1.0, model omitted) +
      `freebuff/AGENTS.global.md`
- [x] Install home-dir artifacts: `~/.agents/*.ts`, `~/.AGENTS.md`, re-sync global task-generator skill
- [x] Update docs: `docs/freebuff-support.md` (FULL status), README Freebuff section, LLM.txt Step 7.5
- [x] Update CHANGELOG.md (Parse-Then-Append, v8.4.5)
- [x] Verify: grep gates, pytest suite, Node parse of `.ts` ports, `lint_task_file`, prettier

### QA Round 8 Final Stabilization

- [x] Repair Task 98 execution-log completeness
- [x] Canonicalize QA-transition Kanban rules
- [x] Harden lint duplicate-heading checks
- [x] Add missing regression tests
- [x] Author the v8.4.5 upgrade guide
- [x] Verify docs accuracy and non-breaking upgrade path
- [x] Run full verification gates
- [x] Update evidence, changelog, lint, staging, and QA move

### QA Round 9 Kanban Metadata Stabilization

- [x] Locate active Task 98
- [x] Add path-drift regression tests
- [x] Add Kanban metadata synchronization rule
- [x] Repair Task 98 final Kanban state
- [x] Update verification evidence and changelog
- [x] Re-lint and re-stage at the final task path

### QA Round 10 Defect Repair

- [x] Restore QA/Review Phase Rule in `agents/cognitive-executor.md` (verified present — preserved + regression-locked)
- [x] Restore Closure Sequence Rule in `agents/cognitive-executor.md` (verified present — preserved + regression-locked)
- [x] Fix duplicate summary_phase step numbering in `system-prompt.md`
- [x] Add regression tests for executor rules and summary numbering
- [x] Update evidence, changelog, and execution log

## Acceptance Criteria

- [x] `system-prompt.md` contains zero `<opencode_*>` tags and no "OpenCode" as the execution-agent name
      (only intentional "OpenCode vs Freebuff" parentheticals); `<system_version>` = 8.4.5
- [x] `<hands_discovery_task>` / `<hands_implementation_task>` / `<hands_combined_task>` are the canonical
      task block names across system prompt, OpenCode agents, and Freebuff ports
- [x] `## Execution Log & Reasoning` header is consistent in system prompt, task-generator skill, lint
      server, and tests; lint + test suite pass
- [x] Freebuff agent ports (`freebuff/agents/*.ts`) and installed `~/.agents/*.ts` contain NO `model:`
      field; both parse with Node type-stripping
- [x] `~/.AGENTS.md` installed from `freebuff/AGENTS.global.md`
- [x] `docs/freebuff-support.md` reports ✅ FULL (REPO-LEVEL) status with the free-tier fix documented and
      the live free-tier spawn flagged as a manual verification item pending Manager confirmation
- [x] `lint_task_file` passes on this task file
- [x] **QA Round 8:** duplicate-heading lint protection exists (`## Factual Git Diff` + Execution Log, pre-diff scoped)
- [x] **QA Round 8:** regression tests exist (Freebuff skill alternative, duplicate-heading rejection, both-headers rejection, `tasks/qa/` in summary phase, upgrade guide) — 27 tests passing
- [x] **QA Round 8:** `docs/workflow-upgrade-v8.4.5.md` exists and is linked from README
- [x] **QA Round 8:** the QA-transition Kanban rule is consistent across `system-prompt.md`, `AGENTS.md`, `agents/cognitive-executor.md`, `freebuff/agents/cognitive-executor.ts`, and `skill-templates/audit-agents/SKILL.md`
- [x] **QA Round 8:** no new task file was created — all work recorded inside Task 98
- [x] **QA Round 10:** `agents/cognitive-executor.md` QA/Review Phase Rule restored (verified present — preserved + regression-locked, no duplication)
- [x] **QA Round 10:** `agents/cognitive-executor.md` Closure Sequence Rule restored (verified present — preserved + regression-locked, no duplication)
- [x] **QA Round 10:** `system-prompt.md` implementation summary_phase numbering fixed
- [x] **QA Round 10:** regression tests added — 31 tests passing

## Verification Evidence

- **Test command:** `uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q`
- **Expected result:** 31 passed (29 previous + 2 new QA round-10 tests: `test_cognitive_executor_preserves_qa_and_closure_rules`, `test_hands_implementation_summary_phase_has_unique_step_numbers`)
- **Actual result:** 31 passed, 9 warnings
- **Exit code:** 0
- **QA round-10 follow-up re-verification:** targeted `test_cognitive_executor_preserves_qa_and_closure_rules` → 1 passed (Rule bullets confirmed present at lines 44/47 of `agents/cognitive-executor.md`); full suite → 31 passed, 9 warnings, exit 0
- **QA round-10 gates:** `py_compile` ✅; grep gates ✅ (no `<opencode_` tags; `/skill:<name>` present; `tasks/qa/` in summary phases; BOTH executor Rule bullets present verbatim — QA Review `git mv` + Closure authorization)
- **QA round-9 path-drift gates:** `py_compile` ✅; grep gates ✅ (no `<opencode_` tags; `/skill:<name>` present; `tasks/qa/` in summary phases; exactly one `## Factual Git Diff` heading)
- **Final `lint_task_file` result (QA round 9):** run on the FINAL task path `tasks/qa/98-system-prompt-runtime-agnostic-freebuff-full-support.md` — `**File:**` header now matches the actual path (structural checks ✅; markdown-basics noise confined to the pre-existing injected diff block, see QA round-7/8 logs)
- **Freebuff schema validation (QA pass, v1.2.0):** `toolNames` cross-checked against the Codebuff Agent Reference 17-tool platform whitelist (live docs, 2026-08-13) — executor pruned from 20 → 11 valid tools, discovery from 8 → 4 valid tools; `spawnableAgents` fixed to local `cognitive-discovery` + built-ins in `publisher/name@version` format. Live free-tier spawn NOT performed from this environment — flagged as a manual Manager verification item (§7/Step 7).

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0 (pytest 31/31 ✅, exit 0; `py_compile` ✅; grep gates ✅)
- [x] `lint_task_file` passes on the active task file (structural checks ✅; markdown-basics noise confined to the pre-existing injected diff block, see QA round-7 log)
- [x] `CHANGELOG.md` updated via Parse-Then-Append (QA round-8, round-9, and round-10 entries under v8.4.5 `### Added` + `### Fixed`; no duplicate headers)
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** the free-tier agent fix is hypothesis-backed (model omission) — a live spawn may still be
  restricted if Freebuff bans custom agents themselves in free mode.
- **Rollback plan:** re-add `model: 'deepseek/deepseek-v4-flash'` to the ports and reinstall; revert
  `system-prompt.md` from git.

---

## Execution Log & Reasoning

**Runtime-agnostic system prompt (v8.4.5):** renamed the local execution agent from "OpenCode" to "the Hands"
(defined as OpenCode, Freebuff, or any compatible terminal agent); renamed all task block tags
`<opencode_*_task>` → `<hands_*_task>` and `<opencode_protocols>` → `<hands_protocols>`; generalized
OpenCode-specific tool references (`apply_patch`, `lsp`, `@explore`/`@general`, `websearch`, `question` tool,
`.opencode/skills/` paths, `opencode.json`) into native-tool descriptions with per-runtime examples; renamed
the task-file section header `## OpenCode Execution Log & Reasoning` → `## Execution Log & Reasoning`.

**Cross-reference cascade:** `agents/cognitive-executor.md` (tags), `skill-templates/task-generator/SKILL.md`
(header + "OpenCode fills..." placeholders), `mcp-lint-server/server.py` (required-section list),
`tests/test_mcp_servers.py` (5 fixtures), `README.md` (tag reference), `docs/system-prompt-modularization.md`
(stale tag names).

**Freebuff full support:** authored `freebuff/agents/cognitive-executor.ts` + `freebuff/agents/cognitive-discovery.ts`
(v1.1.0 — `model` field omitted so the runtime falls back to the free-mode default model, fixing the HTTP 403
`free_mode_invalid_agent_model`; task tags updated to `<hands_*>`); authored `freebuff/AGENTS.global.md` (global
rules, installed as `~/.AGENTS.md` — read by Freebuff in every session per `knowledge.md`/`AGENTS.md`/`CLAUDE.md`
home-dir hierarchy). Installed `~/.agents/*.ts` + `~/.AGENTS.md`, re-synced the global task-generator skill to
`~/.config/opencode/skills/` and `~/.agents/skills/`. Rewrote `docs/freebuff-support.md` to ✅ FULL status,
updated README Freebuff section and LLM.txt Step 7.5 (installs agents + global rules).

**Verification:** grep gates (0 `<opencode_` tags in system-prompt.md; only intentional parentheticals remain),
Node type-stripping parse of both `.ts` ports (executor 1.1.0, discovery 1.1.0), pytest 17/17 ✅,
`lint_task_file` ✅, `lint_markdown` ✅ (system-prompt, docs/freebuff-support, AGENTS.global, task-generator),
prettier ✅. Free-tier spawn smoke test left to the Manager (live Freebuff session)._

**QA adversarial pass (2026-08-13, v1.2.0):** the QA Engineer's adversarial review surfaced four
real defects, all fixed:

1. **AGENTS.md still OpenCode-named:** line 58 gatekeeper phrasing said "You (OpenCode) are the final
gatekeeper" and line 86 still referenced the task-file section as "OpenCode Execution Log". Renamed to
"the Hands" / "Execution Log & Reasoning" to match the runtime-agnostic v8.4.5 system prompt, and added a
Freebuff-equivalents note (`.agents/skills/`, `~/.AGENTS.md`) under the `.opencode/skills/` CORE FILE
LOCATIONS bullet (the OpenCode path stays as a legitimate install location).

2. **Invalid Freebuff `toolNames` (schema-unsafe):** both ports whitelisted tools that are NOT in the
Codebuff 17-tool platform whitelist (`apply_patch`, `list_directory`, `glob`, `read_subtree`, `read_url`,
`skill`, `ask_user`, `suggest_followups`, `lookup_agent_info`). Verified live against the Codebuff Agent
Reference (codebuff.com/docs/agents/agent-reference, 2026-08-13): executor pruned 20 → **11** valid tools
(`read_files`, `write_file`, `str_replace`, `code_search`, `find_files`, `run_terminal_command`,
`web_search`, `read_docs`, `spawn_agents`, `set_output`, `end_turn`); discovery pruned 8 → **4**
(`read_files`, `code_search`, `find_files`, `set_output`). Directory/context mapping remains fully covered
by the `custom_context` MCP tools, which are auto-available to all base agents and need no whitelisting.
Skills are loaded via `/skill:<name>` slash commands (the `skill` tool is not whitelistable).

3. **Invalid `spawnableAgents`:** 8 of 10 entries (`code-searcher`, `basher`, `researcher-web`,
`researcher-docs`, `code-reviewer-deepseek-flash`, `browser-use`, `tmux-cli`, `context-pruner`) were
neither local `.agents/*.ts` agents nor documented built-ins in `publisher/name@version` format. Fixed to
local `cognitive-discovery` + the three verified built-ins `codebuff/file-picker@0.0.1`,
`codebuff/researcher@0.0.1`, `codebuff/reviewer@0.0.1` (exact documented catalog + format).

4. **Missing regression tests + overclaimed status:** added T1 (`test_lint_task_file_rejects_old_header`),
T2 (`test_freebuff_agents_have_no_model_key`), T4 (`test_system_prompt_has_no_opencode_task_tags`) to
`tests/test_mcp_servers.py` (17 → **20** tests). Downgraded `docs/freebuff-support.md`/README status from
`✅ FULL` to **`✅ FULL (REPO-LEVEL)`** with an explicit note that the live free-tier spawn remains a manual
verification item until the Manager confirms it (verification-before-completion). Both ports bumped to
**v1.2.0**. Installed `~/.agents/*.ts` copies now trail the fixed in-repo ports — re-sync via LLM.txt Step
7.5 when the Manager next touches the machine install._

**QA round 3 (2026-08-13): repo-wide consistency sweep + residual fixes.**

1. **Repo-wide search (Step 1).** Ran the deterministic grep
   (`OpenCode Execution Log` | `<opencode_` | `using the \`skill\` tool` | `v1.1.0`, excluding `.git`/
   `context-reports`/`.pytest_cache`). Every match was classified:
   - **Intentional OpenCode documentation / history:** `docs/opencode-*.md`, `docs/opencode-schema.json`,
     all `tasks/archive/*`, `CHANGELOG.md` (historical entries), `docs/history/*`, `.opencode/node_modules/*`.
   - **Intentional version history in active files:** the `v1.1.0` mentions in `freebuff/agents/*.ts` header
     comments (lines 7/44 executor, 7/34 discovery) and `docs/freebuff-support.md` §5 document the v1.1.0
     model-omission fix as history — the files are at v1.2.0; these are accurate records, not drift.
   - **Intentional test fixtures:** `tests/test_mcp_servers.py` T1 embeds the OLD header string to prove the
     linter rejects it; T2's docstring references the v1.1.0 fix; the T4 docstring names the historical
     `<opencode_*_task>` tags it guards against.
   - **Real defects (fixed in this round):** (a) `LLM.txt` Step 7.5 still claimed "works on the free tier
     (v1.1.0)" — updated to v1.2.0, schema-validated + model-free, live spawn as a MANUAL verification item,
     linked to `docs/freebuff-support.md` §5; (b) `freebuff/agents/cognitive-executor.ts` — the Skill
     Auto-Loading Matrix and Direct-Input Protocol still told the Hands to load skills "using the \`skill\`
     tool" (not in the 17-tool whitelist) — both reworded to the `/skill:<name>` slash command; (c) `AGENTS.md`
     Task-Generator bullet now documents the Freebuff `/skill:task-generator` alternative alongside the
     `skill` tool (the base agent retains the `skill` tool in both runtimes — proven in-session — but the
     slash-command form is the portable one).
   - **Observed, out of this task's scope (flagged for a follow-up if the QA wants them):** stale
     "OpenCode Execution Log" / "using the \`skill\` tool" strings remain in `skill-templates/audit-agents/`,
     `skill-templates/versioning-and-release/`, `skill-templates/archive-tasks/`, and
     `agents/cognitive-executor.md` — none are in the QA's defect-file list for this round.
2. **Test strengthened (Step 4):** `test_system_prompt_has_no_opencode_task_tags` → renamed
   `test_system_prompt_has_no_opencode_tags` and broadened to assert that NO line of `system-prompt.md`
   contains the case-sensitive `<opencode_` prefix (catches any future OpenCode-only tag variant, not just
   the three historical spellings).
3. **Task file (Step 5):** all Acceptance Criteria checked off; the docs-status criterion updated to
   `✅ FULL (REPO-LEVEL)` to match the documented status.
4. **CHANGELOG (Step 6):** Parse-Then-Append — appended this round's fixes under the existing v8.4.5
   `### Fixed` section (no duplicate headers created)._

**QA round 4 (2026-08-13): residual skill-template + agent normalization (the follow-up flagged in round 3).**

1. **Targeted grep (Step 1):** `grep -RIn "OpenCode Execution Log\|using the \`skill\` tool" skill-templates agents`
   matched exactly the four expected files: `skill-templates/audit-agents/SKILL.md` (8 lines),
   `skill-templates/versioning-and-release/SKILL.md` (1), `skill-templates/archive-tasks/SKILL.md` (1), and
   `agents/cognitive-executor.md` (1). No other active workflow skill templates matched.
2. **Files changed (Steps 2–3):**
   - `skill-templates/audit-agents/SKILL.md` — `OpenCode Execution Log` → `Execution Log & Reasoning`
     (Explicit Staging Contract ×2, Write-your-Summary), `instruct OpenCode to` → `instruct the Hands to`
     (Task-Generator/Project Skill Loading ×2, Context Bootstrapping ×2), `You (OpenCode) are the final
     gatekeeper` → `You (the Hands) are the final gatekeeper`, and the task-generator bullet now notes the
     `/skill:<name>` Freebuff form. Kept as intentional product/category references: the `# OpenCode Skill:`
     title and the quoted `Task Management & OpenCode Rules` AGENTS.md section label.
   - `skill-templates/versioning-and-release/SKILL.md` — logged-under section name → `Execution Log & Reasoning`.
   - `skill-templates/archive-tasks/SKILL.md` — historical summary field → `Execution Log & Reasoning`.
   - `agents/cognitive-executor.md` — Skill Auto-Loading Matrix now documents the `/skill:<name>` Freebuff
     form; the file keeps its OpenCode frontmatter/paths/tool names (it IS the OpenCode agent definition).
3. **Regression test (Step 4):** added `test_workflow_skills_have_no_opencode_execution_log` — globs all
   29 `skill-templates/*/SKILL.md` + `agents/cognitive-executor.md` and fails-first on either the old
   `## OpenCode Execution Log & Reasoning` header or the prose wording (20 → **21 tests**).
4. **CHANGELOG (Step 6):** Parse-Then-Append under v8.4.5 `### Fixed`, no duplicate headers.
5. **Acceptance Criteria:** all genuinely-met boxes were already checked off in round 3; `## Definition of
   Done` boxes deliberately left unchecked pending final closure authorization._

**QA round 6 (2026-08-13): double verification (live-doc deep check) + minimal adjustments.**

Phase A — Freebuff deep verification (sources retrieved 2026-08-13):
- Freebuff CLI **0.0.149** (installed binary `~/.config/manicode/freebuff --version`) — docs said 0.0.147.
- Codebuff Agent Reference (codebuff.com/docs/agents/agent-reference): **17-tool platform whitelist CONFIRMED**
  (exact match with `freebuff/agents/*.ts`), `spawnableAgents` **`publisher/name@version` format CONFIRMED**,
  `model` field upstream-marked **required** (see adjustment below).
- Codebuff FAQ (codebuff.com/docs/help/faq): **home-directory rules files CONFIRMED** (`~/.knowledge.md`,
  `~/.AGENTS.md`, `~/.CLAUDE.md`, case-insensitive; per-directory order knowledge → AGENTS → CLAUDE),
  matching `docs/freebuff-support.md` §2.4/§2.5.
- Free-tier custom-agent behavior: no official doc covers it (manicode Freebuff fork); evidence remains
  Task 96/98 empirical (pinned `model` → HTTP 403; omission → free-mode fallback). Live spawn still a
  manual Manager verification item.
Phase B — OpenCode deep verification (vendored `docs/opencode/`): agent frontmatter (`mode`/`temperature`/
`permission`), `steps` field (valid — vendored agents.md §Max steps), skills via `.opencode/skills/`, MCP via
`opencode.json` — all intact; Task 98 touched none of the OpenCode artifacts (git status clean).
Phase C — adjustments (LOW/MEDIUM docs-only; no workflow behavior changed):
1. Freebuff CLI version `0.0.147` → **`0.0.149`** in `docs/freebuff-support.md` (4 refs) + `README.md` (1 ref).
2. `model` field doc clarified in `docs/freebuff-support.md` §2.3 — upstream Agent Reference marks it
   required; Freebuff free-tier effectively requires omission (HTTP 403 when pinned).
Deferred (no change): `model` omission in the `.ts` ports themselves (core free-tier fix — re-adding a
pinned model would break it); live spawn confirmation. Full report:
`context-reports/task-98-double-verification.md` + patch `context-reports/task-98-double-verification.patch`._

**QA round 7 (2026-08-13): non-breaking upgrade guarantee & residual consistency.**

1. **Task file structural cleanup (Step 1):** removed the duplicate `## Factual Git Diff` heading directly
   above the Git-Diff BEGIN marker — exactly ONE heading now precedes the diff block.
2. **Lint server backward compatibility (Step 2, non-breaking guarantee):** `mcp-lint-server/server.py`
   `_check_task_file_structure` now accepts EITHER the canonical `## Execution Log & Reasoning` header OR
   the deprecated legacy OpenCode-named header, so pre-v8.4.5 projects that still carry the old header do
   not hard-fail lint. The `task-generator` skill still emits the new canonical header (verified:
   `skill-templates/task-generator/SKILL.md` emits `## Execution Log & Reasoning` in both the single-phase
   and multi-phase templates), and a file with NEITHER header still fails with the canonical
   missing-section message.
3. **Lint regression tests updated (Step 3):** `test_lint_task_file_rejects_old_header` renamed to
   `test_lint_task_file_accepts_old_and_new_headers` (asserts BOTH the canonical and the legacy header pass
   the structure check), and a new `test_lint_task_file_rejects_missing_execution_log` proves a file with
   NEITHER header still fails (21 → **22 tests**).
4. **System prompt skill-loading wording (Step 4):** the `<agent_skills_registry>` intro and the
   `<hands_implementation_task_template>` context phase now document the Freebuff `/skill:<name>` slash
   command as the alternative to the `skill` tool.
5. **Git/ZAC wording consistency (Step 5):** `system-prompt.md` CRITICAL RULE 2 and the `AGENTS.md`
   guardrail now explicitly state the forbidden set (`git add` / `git commit` / `git push` — STRICTLY
   FORBIDDEN) and the ONLY permitted autonomous Git operation (`git mv` for Kanban task-file
   transitions), removing the contradictory phrasing that listed `git mv` as generally forbidden.
6. **Documentation accuracy audit (Step 6):** `README.md` and `docs/freebuff-support.md` no longer claim
   the custom agents are "verified live"; status stays `✅ FULL (REPO-LEVEL)` with the live free-tier spawn
   explicitly a manual Manager verification item pending §5 confirmation. `LLM.txt` Step 7.5 already
   documented the manual-spawn caveat (no change needed).

**QA round 8 (final stabilization): canonical QA-transition rule + lint duplicate-heading hardening + upgrade guide.**

1. **QA Round 8 preparation (Step 1):** added the `### QA Round 8 Final Stabilization` subsection under
   `## Local TODOs` (8 checklist items mirroring this round's micro-tasks). No new task file was created —
   all work is recorded inside Task 98.
2. **Execution-log repair (Step 2):** completed the truncated QA round 7 log above with the six fixes
   already recorded in `CHANGELOG.md` (lint backward compatibility, test updates, system-prompt skill
   wording, ZAC wording clarification, docs accuracy, duplicate task-file heading cleanup); preserved all
   prior QA rounds verbatim. The live Freebuff free-tier spawn is NOT claimed as confirmed — it remains a
   manual Manager verification item (see `docs/freebuff-support.md` §5).
3. **Canonical QA-transition Kanban rule (Step 3):** the workflow now has ONE deterministic transition —
   after a successful implementation, `lint_task_file`, and `custom_context_stage_and_inject_diff`, the
   Hands move the implementation task from `tasks/in-progress/` to `tasks/qa/` via the explicitly
   authorized `git mv`. Updated to agree:
   - `system-prompt.md` — the `<summary_phase>` of both the `<hands_implementation_task_template>` and
     the `<hands_combined_task_template>` now include the QA move (implementation tasks only, AFTER
     successful staging, via the `git mv` listed in the `<bash_phase>`) and explicitly forbid movement to
     `tasks/completed/` without explicit Manager closure authorization ("Approved for closure" / "Close
     task"); the hand-off message path now points at `tasks/qa/<task-name>.md`.
   - `AGENTS.md` — the MANDATORY END-OF-TASK SEQUENCE now separates QA transition (step 4: `git mv` to
     `tasks/qa/` after successful staging) from closure (step 5: `tasks/completed/` + status `closed`
     ONLY after explicit Manager authorization, via `custom_context_commit_and_clean_task`).
   - `skill-templates/audit-agents/SKILL.md` — the generated-`AGENTS.md` template's End-Of-Task Sequence
     gained the same closure-authorization note ("Closure to `tasks/completed/` happens ONLY after the
     Manager explicitly says 'Approved for closure' or 'Close task'").
   - `agents/cognitive-executor.md` and `freebuff/agents/cognitive-executor.ts` were verified ALREADY
     compliant: their QA/Review Phase moves the task to `tasks/qa/` only after staging, and their Closure
     Sequence requires explicit Manager authorization before `tasks/completed/` — no change required.
4. **Lint duplicate-heading hardening (Step 4):** `mcp-lint-server/server.py` `_check_task_file_structure`
   now scopes ALL structural heading inspection to the pre-diff portion of the file (the content before
   the Git-Diff BEGIN marker) and:
   - requires EXACTLY ONE `## Factual Git Diff` heading before the diff block (duplicate → reported);
   - requires EXACTLY ONE Execution Log heading before the diff block, counting EITHER the canonical
     `## Execution Log & Reasoning` OR the legacy OpenCode-named header — but NOT both (both → reported
     as duplicate);
   - preserves the round-7 backward compatibility (either header alone passes) and the neither-header
     rejection. Heading counts use exact-line matching so prose that merely MENTIONS a heading inside
     backticks cannot false-positive. Extensive docstrings/comments explain why only the pre-diff section
     is inspected (the injected block is machine-generated raw diff text and must never count as
     structure) and why duplicate headings are rejected (they desync the Git-Diff markers).
5. **Missing regression tests (Step 5):** five deterministic tests added (22 → **27 tests**):
   - `test_system_prompt_contains_freebuff_skill_alternative` — `/skill:<name>` appears in the
     `<agent_skills_registry>` block AND in the `<hands_implementation_task_template>` context phase
     (≥ 2 occurrences overall);
   - `test_lint_task_file_rejects_duplicate_factual_git_diff_heading` — two `## Factual Git Diff`
     headings before the diff block are rejected;
   - `test_lint_task_file_rejects_both_execution_log_headers` — canonical + legacy Execution Log headers
     both present are rejected;
   - `test_system_prompt_summary_mentions_qa_transition` — at least one `<summary_phase>` block in
     `system-prompt.md` mentions `tasks/qa/`;
   - `test_workflow_upgrade_guide_exists` — `docs/workflow-upgrade-v8.4.5.md` exists.
   All round-7 guarantees remain covered: either header alone passes, neither header fails, Freebuff
   agents have no `model:` key, system prompt has no `<opencode_` tags, and workflow skills have no old
   OpenCode Execution Log wording.
6. **v8.4.5 upgrade guide (Step 6):** authored `docs/workflow-upgrade-v8.4.5.md` covering the
   runtime-agnostic rename (`<opencode_*_task>` → `<hands_*_task>`, execution agent → "the Hands",
   legacy header → canonical header), the non-breaking guarantee, a safe step-by-step upgrade path for
   existing projects, and what NOT to change (OpenCode-specific docs, historical changelog/task records).
   Linked from `README.md` (Step 7) in the Freebuff Support section.
7. **Docs accuracy verification (Step 8):** confirmed all active docs agree — Freebuff custom agents are
   `✅ FULL (REPO-LEVEL)`, the live free-tier spawn remains a manual Manager verification item, OpenCode
   support remains intact, the lint server is backward-compatible with legacy task-file headers, and the
   `task-generator` skill emits the new canonical header.
8. **Acceptance criteria + evidence (Step 9):** QA Round 8 acceptance criteria added (duplicate-heading
   lint protection, regression tests, upgrade guide, consistent QA-transition rule, no new task file
   created) and checked off only after the verification gates passed; `## Verification Evidence` updated
   to the exact final test count (27) and exit code 0.

**QA round 9 (2026-08-13): Kanban metadata stabilization — the stale `**File:**` header after the QA `git mv`.**

The round-8 finalization moved Task 98 to `tasks/qa/` via the authorized `git mv`, but the task file's
`**File:**` metadata header still pointed at the old `tasks/in-progress/` path — the exact path-drift the
lint server's guard (Task 97) was built to catch. This round closes the loop so a Kanban move can never
again leave a stale header behind:

1. **Deterministic location (Steps 1–2):** `find tasks/in-progress tasks/qa` located Task 98 at
   `tasks/qa/98-system-prompt-runtime-agnostic-freebuff-full-support.md` — recorded as `ACTIVE_TASK_PATH`.
   No guessing; the round-9 checklist was appended under `## Local TODOs`.
2. **Path-drift regression tests (Step 3):** two deterministic tests added to `tests/test_mcp_servers.py`
   (27 → **29 tests**): `test_lint_task_file_rejects_file_path_mismatch` (header says `tasks/backlog/`, file
   actually at `tasks/qa/` → mismatch reported — the post-`git mv` Kanban drift scenario) and
   `test_lint_task_file_accepts_matching_file_path` (header and actual path both `tasks/qa/` → no mismatch).
   The existing path-drift guard itself was NOT weakened — these tests lock in the Kanban-specific cases.
3. **Kanban metadata synchronization rule (Step 4)** — now codified in all five workflow documents so
   they agree: after ANY authorized Kanban `git mv`, the Hands MUST update the task file's `**File:**`
   header to the new path; if the move happened after staging, they MUST re-run `lint_task_file` and call
   `custom_context_stage_and_inject_diff` AGAIN with the NEW task path + full `modified_files` array
   (re-stage keeps injected diff and staging state in sync with the final path) before notifying the
   Manager. Never notify with a stale header.
   - `AGENTS.md` — the MANDATORY END-OF-TASK SEQUENCE gained a dedicated step 5 (Kanban Metadata
     Synchronization) and the closure step 6 now also requires the `**File:**` update to `tasks/completed/`.
   - `system-prompt.md` — the `<summary_phase>` of BOTH the `<hands_implementation_task_template>` and
     the `<hands_combined_task_template>` now insert the metadata-sync step after the QA move, and the
     "you are DONE" / "then output exactly" steps come only after re-lint + re-stage at the new path.
   - `agents/cognitive-executor.md` + `freebuff/agents/cognitive-executor.ts` — QA/Review Phase gains a
     Metadata Sync bullet; Closure Sequence gains the `**File:**` update to `tasks/completed/`.
   - `skill-templates/audit-agents/SKILL.md` — the generated-`AGENTS.md` End-Of-Task Sequence is now a
     5-step process (metadata sync inserted between the QA move and Notify Manager), and both audit
     criteria descriptors were updated to match.
4. **Task 98 final Kanban state repaired (Step 5):** the `**File:**` header was updated to
   `tasks/qa/98-system-prompt-runtime-agnostic-freebuff-full-support.md` (the ACTIVE_TASK_PATH) — the file
   was already in `tasks/qa/`, so no `git mv` was needed this round; the metadata is what had drifted.
5. **Verification (bash phase):** pytest **29/29 ✅** (exit 0), `py_compile` ✅, grep gates ✅ (no
   `<opencode_` tags; `/skill:<name>` present; `tasks/qa/` in summary phases). `lint_task_file` on the QA
   path confirms the header/path now match. The live Freebuff free-tier spawn is NOT claimed — it remains
   a manual Manager verification item (see `docs/freebuff-support.md` §5).

**QA round 10 (2026-08-13): defect repair — verify-and-preserve, not blind restore.**

The QA Engineer's round-10 findings were triaged against the ACTUAL repository state. Two of the three
claimed defects did NOT exist as described; one real defect was confirmed and fixed:

1. **QA/Review Phase Rule bullet — ALREADY PRESENT (no defect).** The Orchestrator claimed the
   `- **Rule:**` bullet (git mv from `tasks/in-progress/` to `tasks/qa/`) was removed from
   `agents/cognitive-executor.md`. Verified: the bullet exists verbatim at line 44 in BOTH the working
   tree and the staged diff — round 9's metadata-sync edit preserved it (the round-9 replacement added
   the `- **Metadata Sync:**` bullet WITHOUT removing the Rule bullet). Per the Orchestrator's own
   constraint "Do NOT duplicate it", no replacement was applied — restoring by re-adding would have
   created a duplicate bullet. Instead, a fail-first regression test now asserts the exact bullet string.
2. **Closure Sequence Rule bullet — ALREADY PRESENT (no defect).** Same analysis: the `- **Rule:**`
   bullet (explicit Manager closure authorization) exists verbatim at line 47 in both the working tree
   and the staged diff. No change applied (no duplication); regression test added.
3. **Duplicate step `5.` numbering in `<hands_implementation_task_template>` `<summary_phase>` — REAL
   defect, FIXED.** Round 9 inserted the KANBAN METADATA SYNCHRONIZATION step as `4.` and renumbered the
   old `4.` ("Once the move succeeds, you are DONE") to `5.`, but the following "Output EXACTLY this
   message to the Manager:" step was left at `5.` — producing two `5.` steps (lines 472–473). Fixed:
   the second `5.` is now `6.`. The `<hands_combined_task_template>` summary phase was verified clean
   (numbered 1–5 sequentially) and left unchanged per the Orchestrator's instruction.
4. **Regression tests (Step 5):** two deterministic tests appended to `tests/test_mcp_servers.py`
   (29 → **31 tests**): `test_cognitive_executor_preserves_qa_and_closure_rules` (asserts BOTH Rule
   bullets survive in `agents/cognitive-executor.md` — this is the durable lock that makes the
   verify-and-preserve decision safe) and `test_hands_implementation_summary_phase_has_unique_step_numbers`
   (extracts the numbered steps in the implementation summary phase and asserts they are exactly 1..N
   with no duplicates or gaps — guards against any future renumbering regression).
5. **Live Freebuff free-tier spawn: NOT claimed.** It remains a manual Manager verification item
   (see `docs/freebuff-support.md` §5). No `git mv`, `git add`, `git commit`, or `git push` was run;
   Task 98 stays in `tasks/qa/`.

**CLOSURE (2026-08-13): Manager-authorized.** The Manager explicitly said "Approved for closure",
authorizing the final closure sequence. The task file was moved from `tasks/qa/` to `tasks/completed/`
via the authorized `git mv` Kanban transition; the `**Status:**` metadata was updated to `closed` and the
`**File:**` header to `tasks/completed/98-system-prompt-runtime-agnostic-freebuff-full-support.md` per the
Kanban metadata synchronization rule. Closure commit created via the ONLY authorized commit path
(`custom_context_commit_and_clean_task`). The live Freebuff free-tier spawn remains a manual Manager
verification item (see `docs/freebuff-support.md` §5) — noted for the record at closure.

**QA round 10 follow-up re-verification (2026-08-13):** re-ran the exact verification the QA Engineer
asked for, fresh against the on-disk file: (1) `grep` confirms BOTH Rule bullets present in
`agents/cognitive-executor.md` — QA/Review Phase Rule at line 44 (before the Metadata Sync bullet) and
Closure Sequence Rule at line 47 (before the Action bullet); (2) the targeted regression test
`test_cognitive_executor_preserves_qa_and_closure_rules` **PASSED** (1 passed); (3) the full suite
**31 passed, exit 0**. The round-10 log above was therefore NOT inaccurate — it correctly reported the
Rule bullets as present (verified in both the working tree and the round-9 staged diff, where they appear
as unchanged context lines). The claim stands: no restoration was needed, and the regression test is the
durable lock. No code files were modified in this follow-up; only this task file was updated.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `aafb79216a47753060f196a17efbacd7052d2c0f`
<!-- END_GIT_DIFF -->
