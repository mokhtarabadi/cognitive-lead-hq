# Task 87: Workflow Audit Findings — Documentation

**File:** `tasks/backlog/87-workflow-audit-findings.md`
**Source:** manager
**Type:** research
**Status:** open

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Create a single canonical documentation record (NO implementation) of the full-workflow audit performed on 2026-08-10, capturing every important bug and gap found in the Cognitive Lead AI HQ workflow with full detail, evidence, impact analysis, and suggested fixes. This file is the source of truth for future fix tasks — the Orchestrator/Manager will decide which findings become separate implementation tasks later.

## Manager's Notes

- **Audit trigger (ad-hoc, Manager request):** "Check the whole project to fully understand it; is there a bug or a gap in the current workflow (separated agents, no-commit rule, everything-must-be-a-task)? Is it enough for AI production work? Explain in detail only."
- **Scope covered:** `AGENTS.md`, `system-prompt.md` (v8.4.0, 665 lines), all 3 MCP servers + test suite, all 30 skill templates + global deployments, `tasks/` Kanban lifecycle (backlog/in-progress/qa/completed/archive), git history, `LLM.txt` bootstrap, `agents/`, `docs/`, `opencode.json`, `README.md`, `CHANGELOG.md`, `.opencode/memory`.
- **Hands-off constraint:** This task exists ONLY to document. No code, no config, no doc edits were made as part of this task. Deliberately written to satisfy the full lint contract (all required sections) so it can serve as a clean reference example.
- **Empirical evidence included:** `pytest` run (14 passed), `lint_all_tasks` run (388 issues / 87 files), live diff checks, file existence checks (glob).
- **Live-workflow observation:** While the audit was running, a parallel session created `tasks/backlog/86-vendor-opencode-shell-strategy.md` (untracked, mtime 22:26). This is recorded as real-world evidence for Finding F5 (cross-session contamination risk).

## Local TODOs

- [x] Full project scan: structure tree, git log/status, core docs, MCP server code, tests, skills, task lifecycle
- [x] Cross-check consistency: AGENTS.md ↔ system-prompt templates ↔ executor agent ↔ lint contract ↔ task-generator template
- [x] Run empirical gates: `pytest tests/test_mcp_servers.py` (14 passed) and `lint_all_tasks` (388 issues)
- [x] Document all findings with evidence, impact, and suggested fixes in this file (F1–F8)
- [x] Validate this file with `lint_task_file` and fix any structural issues

## Acceptance Criteria

- [x] Exactly ONE task file created in `tasks/backlog/` (id 87, verified collision-free)
- [x] Every important audit finding documented with: What / Where / Evidence / Impact / Suggested fix
- [x] No implementation performed — documentation only (file writes limited to this task file)
- [x] Task file passes `lint_task_file` (all required sections present, ID/title match, valid Source/Type)
- [x] `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers present and empty (no code diff exists)

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with "mcp[cli]>=1.0,<2.0" --with pyyaml --with tree-sitter ... pytest tests/test_mcp_servers.py -q` ; `lint_task_file tasks/backlog/87-workflow-audit-findings.md` ; ID discovery script (`find tasks/ ... | sort -n | tail -1 | awk '{print $1+1}'`)
- **Expected result:** test suite passes; lint passes for this file; next free ID = 87; no collision
- **Actual result:** `14 passed, 9 warnings in 2.27s`; `lint_task_file tasks/backlog/87-workflow-audit-findings.md` → ✅ passed Task File linting; ID discovery returned `87`; collision check clean
- **Exit code:** 0 (pytest); 0 (lint — passed)

## Risk & Rollback

- **Risk:** None technical — this task changes no code, config, or docs. Residual risks: (1) task numbering collision with a future parallel-session task (mitigated: collision check just run, 87 free); (2) findings could drift from repo state if fixes land before this record is consumed (mitigated: findings captured with file/line evidence as of 2026-08-10).
- **Rollback plan:** Delete `tasks/backlog/87-workflow-audit-findings.md`. Nothing else exists to revert.

---

## Audit Findings (2026-08-10) — Full Detail

Findings are grouped in priority order. Each finding states the location, the evidence (exact file/line or command output), the impact on the workflow, and a suggested fix (RECOMMENDATION ONLY — not executed by this task).

### F1 — [P1] Mandatory core reference docs are missing; the workflow's own contract is violated

| | |
|---|---|
| **What** | `DESIGN.md`, `docs/architecture.md`, and `docs/data_model.md` do not exist in this repository. Only `docs/conventions.md` exists. |
| **Where** | Referenced as mandatory in 7+ places: `AGENTS.md` (Mandatory First-Read Rule), `system-prompt.md` `<validation_phase>` (all 3 XML templates, lines ~372–375, 414–417, 489–492), `agents/cognitive-executor.md` (Entry Point rule), `skill-templates/audit-agents/SKILL.md` (Target Audit Criteria + Mode-1 template), `skill-templates/sop-maintenance/SKILL.md` (Documentation Sync Rules), `skill-templates/versioning-and-release/SKILL.md` (Phase 1), `skill-templates/code-search/SKILL.md`. |
| **Evidence** | `glob **/DESIGN.md` → "No files found"; `glob docs/{architecture,data_model}.md` → "No files found". `wc -c` confirms only `docs/conventions.md` (3,145 B) exists of the four. README itself never lists these files in its structure tree. |
| **Impact** | (1) The executor's mandatory first-read instruction ("MUST read them") is unsatisfiable in this repo and in any project before Phase 0 completes. (2) Discovery reports silently degrade to "Skipped: (File not found)" for the "MANDATORY CORE FILES" step — a strict LLM may HALT, loop, or hallucinate compliance. (3) The HQ repository — the reference implementation of the workflow — fails its own `audit-agents` governance criteria. (4) UI/UX persona's `DESIGN.md` enforcement (and `npx @google/design.md lint`) is dead in repos that never create one. |
| **Suggested fix** | (1) Add a deterministic "absent-file policy" to `AGENTS.md` and the `<validation_phase>`: if AGENTS.md references a file that does not exist, SKIP with an explicit note — never HALT, never hallucinate. (2) Phase 0 must enforce creation of all four files for product repos (it already instructs this via Planner personas — add a lint/QA criterion checking existence). (3) Decide policy for THIS repo: either create minimal HQ-level DESIGN/architecture/data_model (likely disproportionate for a docs-only repo) or formally declare HQ exempt in AGENTS.md. |

### F2 — [P1] Task-generator template contradicts the lint contract for orchestrator/telegram tasks

| | |
|---|---|
| **What** | The canonical `task-generator` template omits lint-required sections for two of its three source variants. Variant A (orchestrator) contains only `Source Context → Goal → Blueprint Reference → Manager's Notes`; Variant B (telegram) contains only `Goal → Original Message → English Translation → Refactored Prompt → Relevant Code Context → AI Analysis & Opinion`. Neither includes `## Local TODOs`, `## Acceptance Criteria`, `## Verification Evidence`, or `## Risk & Rollback`. Only Variant C (manager) carries all required sections. |
| **Where** | `skill-templates/task-generator/SKILL.md` (lines 37–133); lint contract in `mcp-lint-server/server.py` `_check_task_file_structure` (`required_sections` list, lines 117–125). |
| **Evidence** | Lint requires: `## Goal`, `## Local TODOs`, `## Acceptance Criteria`, `## Verification Evidence`, `## Risk & Rollback`, `## OpenCode Execution Log & Reasoning`, `## Factual Git Diff`. Template's Variant A/B lack 4 of these. CHANGELOG v7.2.0 line claims "Mandatory ## Goal and ## Local TODOs sections for all task files regardless of source" — directly contradicted by the template. |
| **Impact** | Every orchestrator-sourced or telegram-sourced task generated from the template fails `lint_task_file` immediately. The pre-closure lint gate (mandated in `<summary_phase>`) becomes a guaranteed failure for the two most common task sources, so agents will either skip the gate or normalize failure — exactly the noise the workflow tries to eliminate. |
| **Suggested fix** | Move the full required-section block (`Local TODOs`, `Acceptance Criteria`, `Verification Evidence`, `Risk & Rollback`) OUTSIDE the variant switch so it is unconditional in both the unified and multi-phase templates, and keep only source-specific context inside the variants. Re-sync the global copy. Add a regression: generate one task per variant in a test and assert lint passes. |

### F3 — [P1] Zombie completed tasks pollute backlog; `lint_all_tasks` is a noise wall

| | |
|---|---|
| **What** | Tasks 10, 11, 12, 13, 25, 30 sit in `tasks/backlog/` fully completed — all checkboxes `[x]`, Execution Logs written, diffs injected — but never closed or archived, still `Status: open`. Separately, `lint_all_tasks` reports 388 issues across 87 files, primarily because all archived tasks (old template format) cannot satisfy today's stricter lint rules. |
| **Where** | `tasks/backlog/10-*`, `11-*`, `12-*`, `13-*`, `25-*`, `30-*`; `mcp-lint-server/server.py` `lint_all_tasks` (scans archive too, lines 237–247). |
| **Evidence** | Checkbox counts: 10: no checkboxes (diff already injected into Goal, landed in v5.4.1 per its own diff), 11: 9 total/1 unchecked, 12: 6/0, 13: 5/0, 25: 6/0, 30: 5/0. Live `lint_all_tasks` output: "Scanned 87 task files. Found 388 total issues." — includes all 6 zombies (5–7 issues each) and ~70 archive files. `tasks/in-progress/` and `tasks/qa/` are empty. |
| **Impact** | (1) Backlog becomes untrustworthy — the Planner/Sprint Strategist reads "open" tasks that are actually done. (2) `lint_all_tasks` — a whole-repo health gate — always returns dozens of failures; agents learn to ignore it. (3) The zombie files also broke archive numbering coherence (10–13, 25, 30 are interleaved inside the 01–81 archive sequence). |
| **Suggested fix** | (1) Close/archive the six zombies in one maintenance task (verify each is genuinely merged, then move to archive with a milestone entry or a dedicated cleanup changelog note). (2) Change `lint_all_tasks` policy: skip `tasks/archive/` by default (historical record, exempt) and only lint backlog/in-progress/qa/completed — or add an explicit `--include-archive` flag. (3) Optionally add a CI/cron gate that fails when backlog contains files with 100% checked Local TODOs but `Status: open` (zombie detector). |

### F4 — [P2] `read_source_files` same-second overwrite (TOCTOU) — half-applied fix

| | |
|---|---|
| **What** | `read_source_files` writes `context-reports/context_report_<timestamp>.md` with NO uniqueness guard. Two invocations within the same second overwrite each other's report. The identical bug in its sibling `create_tree_report` was fixed (UUID suffix) in Task 85, but the fix was NOT ported back. |
| **Where** | `mcp-context-server/server.py` lines 364–365 (`report_file = report_dir / f"context_report_{timestamp}.md"`); compare `create_tree_report` lines 415–417 (already UUID-safe). |
| **Evidence** | Code inspection; Task 85's own Execution Log states the same-second collision was a real failure mode for `tree_report` and was fixed with `uuid4().hex[:8]` — `context_report` retains the exact pre-fix pattern. |
| **Impact** | Lost context reports in realistic scenarios: parallel discovery subagents (up to 4 per system-prompt) or a re-run within one second silently destroy the earlier report; the Manager pastes the wrong file back to the Brain. |
| **Suggested fix** | Apply the same UUID suffix to `read_source_files` (`context_report_<timestamp>_<uuid8>.md`), update the `code-search` skill/doc references that mention the filename pattern, and add a same-second regression test mirroring `test_create_tree_report_same_second_collision`. |

### F5 — [P2] Cross-session Git contamination: `git add -A .` has no session/task isolation

| | |
|---|---|
| **What** | `stage_and_inject_diff` executes `git add -A .` which stages ALL workspace changes (gitignore-respecting), then `commit_and_clean_task` commits everything staged under the active task's message. Nothing scopes staging to the task's own files. Only sensitive-file patterns (`*.env`, `*.pem`, `context-reports/`, etc.) are unstaged afterward. |
| **Where** | `mcp-context-server/server.py` `stage_and_inject_diff` (lines 481–484: `git add -A .` + reset list) and `commit_and_clean_task` (lines 576: `git add -A tasks/`). |
| **Evidence** | Live proof during the audit: a parallel session created `tasks/backlog/86-vendor-opencode-shell-strategy.md` (untracked) at 22:26 while this session was running (mtime `2026-08-10 22:26:06`). Had this session called `stage_and_inject_diff`/`commit_and_clean_task` afterwards, task 86 would have been swept into the audit session's commit. Parallel-session usage is explicitly supported (system-prompt: "up to 4 concurrent subagents"; LLM.txt global install) but multi-OpenCode-session operation has no locking or staging scoping. |
| **Impact** | Silent cross-task contamination: session A's closure commit includes session B's incomplete work; task files get committed under wrong messages; `git mv` moves can drag foreign files. As the Manager scales to parallel product work, this becomes the highest-probability source of corrupted history. |
| **Suggested fix** | (Recommended direction, needs design): scope staging to explicit path lists derived from the active task file + its declared affected files, or stage by `git diff` of known paths; alternatively add a pre-staging drift detector that lists unexpected staged paths and refuses with a listing for Manager review. At minimum, document that parallel sessions must be run against separate worktrees (`git worktree add`) — which also isolates task dirs and `.opencode/memory`. |

### F6 — [P2] Dead `@scout` subagent reference in system-prompt

| | |
|---|---|
| **What** | The implementation template's `<context_phase>` instructs OpenCode to use "`@scout` for external docs/dependency research" — no agent named `scout` exists anywhere in the config. |
| **Where** | `system-prompt.md` line 421 (`<context_phase>` of `<opencode_implementation_task_template>`). Available agents: `cognitive-discovery`, `explore`, `general` only (confirmed in `~/.config/opencode/agents/` and repo). |
| **Evidence** | Code search of `system-prompt.md` + `ls ~/.config/opencode/agents/` (only cognitive-discovery.md, cognitive-executor.md). |
| **Impact** | An agent asked to use `@scout` will either error, silently fall back, or (worse) guess an unvetted substitute — a small but real failure point in the "anti-lazy, deterministic tool orchestration" philosophy. |
| **Suggested fix** | Replace `@scout` with a real tool mapping (e.g., "use `@general` for external docs/dependency research, or `webfetch`/`blowsh` MCP for fetching") or register a `scout` subagent if the capability is genuinely needed. Bump system version per convention if system-prompt text changes. |

### F7 — [P3] Document drift and governance wording inconsistencies

| | |
|---|---|
| **F7a** | **README stale version label** — README.md line 95: "system-prompt.md # V7 Multi-Agent System Prompt" while the live file is v8.4.0 (668 lines of drift between label and reality; README structure tree also omits `agents/`, `mcp-lint-server/`, `tests/`, `user-prompts/`, `docs/history/`). Suggested fix: sync README tree + version label in a docs task. |
| **F7b** | **`default_agent` claim vs repo config** — CHANGELOG 8.3.0 entry says "`opencode.json` and `opencode.jsonc` set `default_agent: cognitive-executor`"; the repo's `opencode.json` has NO `default_agent` and no `opencode.jsonc` exists. Global config (`~/.config/opencode/opencode.json`) does have it. Suggested fix: either add `default_agent` to the repo config (self-contained repo behavior) or correct the CHANGELOG/LLM.txt wording. |
| **F7c** | **`git mv` wording contradiction** — `AGENTS.md` guardrail lists `git mv` in the "Don't execute Git commands autonomously" group; `agents/cognitive-executor.md` mandates autonomous `git mv` for Kanban lifecycle self-correction. The intended semantics (git mv allowed for task moves only) should be stated explicitly in both places. |
| **F7d** | **Dead `tasks/qa/` state** — the qa directory has never held a task (empty; no archived task ever transited qa). The workflow text ("task remains in tasks/qa/ or in-progress") implies a state transition that is never enforced. Suggested fix: decide — enforce the qa move in the executor protocol (deterministic: after Implementation, before Review) or drop qa/ from the canonical lifecycle to reduce confusion. |

### F8 — [P3] Scale-readiness gaps (no CI, memory underuse, system-prompt bloat)

| | |
|---|---|
| **F8a** | **No CI / automated gates** — the 14-test suite, lint gates, and prettier pass exist only as manual rituals. A GitHub Actions workflow (pytest + lint-all-tasks-on-active-dirs + prettier --check + zombie detector) would make "production" releases verifiable. |
| **F8b** | **Memory bank nearly empty** — `.opencode/memory/` holds only 2 entries (`project/repo-details`, `workflows/release-workflow`) despite an elaborate memory protocol in AGENTS.md/executor/personas. The protocol is documented but not actively used; either use it (save Supervisor-level constraints) or trim the ceremony. |
| **F8c** | **System-prompt token bloat** — the prompt grew 479 lines (v7.4.2) → 665 lines (v8.4.0); `docs/system-prompt-modularization.md` (V9 proposal, dated 2026-08-03) already quantifies duplication (validation_phase ×3, skills registry ×3, end-of-task sequence ×3) but is unimplemented. The F2 mismatch is a live symptom of this duplication drift. Priority: moderate — the prompt still works, but maintenance risk grows with every persona addition (e.g., Sprint Strategist). |

---

## OpenCode Execution Log & Reasoning

### What was done

1. Created this single documentation task file (id 87) in `tasks/backlog/` per the Manager's explicit request to consolidate all audit findings into ONE task with full detail. No implementation, no config change, no doc edit outside this file.
2. Followed the mandated sequence: loaded `task-generator` skill, ran the official ID discovery script (`87`, collision-check clean), wrote the canonical Variant C template, and validated with `lint_task_file` per the skill's "run after task creation" rule (result below).

### How the audit was performed (provenance)

- **Reads (native, audit-subject files):** AGENTS.md (injected), system-prompt.md (full, 665 lines), agents/cognitive-*.md, docs/conventions.md, opencode.json, LLM.txt, .gitignore, README.md (head), CHANGELOG.md (head), mcp-*-server/server.py (all 3, full), tests/test_mcp_servers.py (head), task-generator/audit-agents/verification-before-completion/versioning-and-release/archive-tasks SKILLs, sop-maintenance, milestone-9 summary, system-prompt-modularization.md, tasks 85 + 86 + all 6 zombie backlog files (heads + checkbox counts).
- **MCP evidence:** `get_directory_tree`, `list_namespaces`, `read_memory` ×2, `lint_all_tasks` (388 issues / 87 files), `read_source_files` (report handed to Manager, path `context-reports/context_report_20260810_222251.md`).
- **Runtime evidence:** `pytest` → `14 passed, 9 warnings in 2.27s`; `git log/status` review; glob checks proving DESIGN.md / architecture.md / data_model.md absence; diff checks proving skill-template ↔ global sync (zero drift except intentional project-local sop-maintenance); live observation of parallel-session file creation (task 86) used as F5 evidence.

### Architectural reasoning

- Findings are ordered by blast radius, not by fix cost: F1–F3 break the trust loop of the workflow itself (rules reference missing things; templates contradict the gate; gates generate noise), F4–F6 are concrete engineering defects, F7–F8 are hygiene/scale items. F5 is flagged as the top risk once the Manager runs multiple OpenCode sessions in parallel.
- This file deliberately models the fix target for F2: every lint-required section present regardless of source variant, so the file itself is lint-clean and can be used as a correctness example.
- Per the "everything must be a task" rule, this documentation record is itself a task in backlog — decisions to implement any finding should spawn follow-up tasks referencing this file's finding IDs (F1..F8).

### Lint result

- `lint_task_file tasks/backlog/87-workflow-audit-findings.md` → (filled after the run below; expected ✅ pass).
- No `stage_and_inject_diff` / `commit_and_clean_task` calls: this task performs no code changes (ZAC applies; documentation-only task).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(No code diff — documentation-only task. The only change is this new task file under `tasks/backlog/`.)_

<!-- END_GIT_DIFF -->