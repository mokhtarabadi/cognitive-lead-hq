# Task 418: Agent-facing context MCP tool outputs

**File:** `tasks/completed/418-agent-facing-context-mcp-tool-outputs.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-23T09:03:37Z
**Submitted:** 2026-11-23T08:54:51Z
**Started:** 2026-11-23T08:40:03Z

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Remove human/Manager-facing wording from Python MCP tool output strings so that tool output consumed by the agents and the cognitive executor is addressed to the agent, not to a person who copies and pastes files.

## Manager's Notes

- Manager request (voice-dictated, normalized): "Search and find all places we used keywords like `Manager: You can now open` in the tool output and input now used by agents and cognitive executor, so drop `Manager` from all of them — the tools, Python MCP. Make the system more comfortable for yourself. A task is required. Brain seats required. Skill loading and code search required. Auto mode lock."
- Correction note (prompt-refactor): `serach`→`search`, `cogntive exectotor`→`cognitive executor`, `comortable`→`comfortable`, `brain setas`→`brain seats`, `auto mode lock`→`autopilot locked`. Clarity 3/5; scope resolved by code search before planning.
- Autopilot locked for this task from the Manager's "auto mode lock" order. ZAC holds — no `git add`, `git commit`, `git checkout`, `git push`. Plan-approval and closure-approval gates still apply.
- Skills loaded: `prompt-refactor`, `code-search`, `project-memory`, `sop-maintenance`, `kanban-lifecycle`. `testing-verification` to be applied before the verification gate.
- Code-search finding: only two tool-output strings match the pattern, both in `mcp-context-server/server.py` (`build_context` and `create_tree_report` return blocks). A deployed copy exists at `~/.config/opencode/mcp-context-server/server.py` and is a separate deployment concern, not repo source.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Input validation, typo correction, and skill loading
- [x] Code search: locate every `Manager:` tool output/input string in the Python MCP servers
- [x] Create this task file
- [x] Seat-routed Brain plan, then Manager plan approval
- [x] Update the two tool-output strings in `mcp-context-server/server.py` to agent-facing wording
- [x] Add or update a regression test asserting no `Manager:` token in those tool outputs
- [x] Update sibling `README.md`/`DECISIONS.md` if the tool-output contract changes, and `CHANGELOG.md`
- [x] Run the verification gate and record evidence here
- [x] QA transition via `custom_context_qa_transition` and chain QA/review via `brain_turn` (both chained and answered: QA_PASSED, then APPROVED / PO_REVIEW_PENDING)

## Acceptance Criteria

- [x] A repo-wide grep of `mcp-*/**/*.py` for the literal `Manager:` returns no tool output/input strings (documentation and historical task files are out of scope)
- [x] `read_source_files` and `create_tree_report` return messages addressed to the calling agent, with no `Manager:` prefix and no "copy/paste it for the AI" instruction
- [x] A regression test fails on the old wording and passes on the new wording
- [x] `CHANGELOG.md` updated via Parse-Then-Append; sibling living-folder docs inspected
- [x] Verification evidence recorded with an exact `rtk test`-prefixed command and exit code 0 (recorded command exits 1 due to 8 pre-existing/environmental failures; the two new tests exit 0 — see `## Verification Evidence`). Waived by the Manager's "Approved for closure" on 2026-11-23, which resolves review finding F7. The exit-code-0 condition is waived, not met.

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec==0.12.1 --with pyyaml==6.0.2 python -m pytest tests/ -q`
- **Expected result:** all tests pass, exit code 0
- **Actual result:** Scoped red/green: `tests/test_agent_facing_tool_outputs.py` → 2 failed (exit 1) then 2 passed (exit 0). Full suite: `8 failed, 969 passed, 1 warning in 81.20s`. The 8 failures are pre-existing and unrelated to this change: 3 in `tests/test_mcp_servers.py` (system-prompt sync drift fixture stale — mutation target missing from `03-system_context.md`; `cognitive-executor.md` missing the QA/closure Rule bullet from a prior task) and 5 in `tests/test_planner_409_regression.py` (401 Unauthorized — auth token not present in this environment). None touches the files changed by this task. ruff format --check: exit 0 on both changed files. ruff check: exit 0 on the new test file; on `server.py` reports 115 pre-existing findings, none on the edited lines 766-767, 842-843, or 778. Typecheck and security stages: no config in `mcp-context-server/pyproject.toml` — skip records below.
- **Exit code:** 1 (full suite, pre-existing failures). The two new regression tests exit 0.

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0 (full suite exits 1 on 8 pre-existing/environmental failures; the two new tests and ruff format/check on the new test exit 0 — see `## Verification Evidence`). Waived by the Manager's "Approved for closure" on 2026-11-23, which resolves review finding F7. The exit-code-0 condition is waived, not met.
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** The deployed singleton at `~/.config/opencode/mcp-context-server/server.py` keeps the old wording until a separate redeploy; agents would still see `Manager:` at runtime even after this repo change.
- **Rollback plan:** Revert the two string literals (and the regression test) in `mcp-context-server/server.py`; no data or schema change. Deployment copy is untouched by this task.

---

## Execution Log & Reasoning

_Planning phase. Autopilot locked per Manager order. Code search located exactly two matching tool-output strings in `mcp-context-server/server.py` (lines 766 and 841). Context-Map produced: graph `context-reports/graph_20261123_092849_e9b7c41d.json`, tree report `context-reports/tree_report_20261123_092850_08a392f2.md`, verified manifest `mcp-context-server/server.py#L760-767` and `#L838-842`. Sibling living-folder docs read before editing. No code changed yet._

- Plan: approved by Manager via question tool ("Approved"), option O1. `Brainstorm: not required — single-domain, fully reversible string contract change`. Seats [Software Architect] + [Senior Programmer]; Brain issued the implementation XML.
- Lane claim: `claim_next(task_id=418)` succeeded; moved to `tasks/in-progress/`, `**Started:** 2026-11-23T08:40:03Z` stamped by the transition. `**File:**` header synced to the in-progress path by hand because the transition did not rewrite it.
- Tooling fallback record: repo root `/home/mohammad/cognitive-lead-hq`; marker scan list — `mcp-context-server/pyproject.toml`, `mcp-context-server/server.py` (FastMCP app, no Flask/FastAPI/Pydantic); matched skills list — `python-fastapi` (closest, discipline only for gate order); reason phrase — "no MCP or FastMCP stack skill exists in the agent skills registry".
- Skill load record: `prompt-refactor`, `code-search`, `project-memory`, `sop-maintenance`, `kanban-lifecycle`, `testing-verification`, `python-fastapi` all loaded. Skips — `code-search` already executed in planning; no new task file to lint; no version bump or release in scope.
- Red proof: `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec==0.12.1 --with pyyaml==6.0.2 python -m pytest tests/test_agent_facing_tool_outputs.py -q` → `2 failed`, exit 1. Intended TDD red proof — old wording still present at `server.py:766` and `:841`. Syntax gate on the test file passed (exit 0).
- **Correction C1 (grounded):** the Brain plan named the codebase-context tool `build_context`, but the actual top-level function returning that text is `read_source_files` (`mcp-context-server/server.py#L690`). The first green attempt failed `test_context_tool_outputs_are_agent_addressed` with `build_context: definition not found`; the test mapping and the task AC were corrected to the real symbol. No tool behavior changed.
- Green proof: identical scoped command after the correction → `2 passed`, exit 0. Red-to-green pair closes Acceptance Criterion 3.
- Two return blocks rewritten with O1 wording: `read_source_files` at `server.py#L766-767` now `Context report written to … / Read it with your file tools to review the compiled codebase context.`; `create_tree_report` at `server.py#L842-843` now `Tree report written to … / Read it with your file tools to review the project tree.` Emoji prefixes, metrics line, `Generated Report` line, and `\\n\\n` separator untouched. Repo-wide grep for both retired sentinels in `mcp-*/**/*.py` prints nothing (exit 1 = PASS).
- Audit of other tools and parts (Manager request): grep of `mcp-*` source (excluding `.venv`) for `Manager:`, `copy/paste`, `local editor`, `for the AI`, `please copy`, `please upload`, `send it back to the AI Studio` returned no tool output strings beyond the two already fixed. Only other hit was a `create_tree_report` docstring ("Use when the Manager asks to..."), updated to "Use when the caller asks to...". No other human-facing tool strings found; scope stayed minimal.
- Tooling gate (fail-fast): (1) `uvx ruff format` write mode — exit 0, no changes. (2) `uvx ruff format --check` — exit 0 on both changed files. (3) `uvx ruff check` on `tests/test_agent_facing_tool_outputs.py` — exit 0. On `mcp-context-server/server.py` — 115 pre-existing findings (unused re-exported imports, blind exceptions, mutable defaults, etc.), none on the edited lines 766-767, 842-843, or 778; skip record: config path checked `mcp-context-server/pyproject.toml` (no `[tool.ruff]` section), reason "pre-existing findings not introduced by this change; ruff config absent; cleanup is a separate task". (4) Typecheck: `pyproject.toml` configures no typechecker (basedpyright/mypy/ty absent) — skip record: configuration path read, "no typechecker configured for this slice". (5) Security: no bandit/semgrep/pip-audit configured — skip record: configuration path checked, "no security scanner configured for this slice".
- Assumption log: A1 — ADR-015 placed newest-first before the existing ADR-014 entries (matching the file's 2026-11-02 top entry), not renumbering history. A2 — new test placed at repo-root `tests/` because that directory exists and `mcp-context-server/tests/` does not. A3 — the Brain plan's `build_context` name corrected to the real symbol `read_source_files` (`server.py#L690`); task AC and test mapping updated accordingly. A4 — 8 full-suite failures are pre-existing/environmental and unrelated to this change; the `exit code 0` AC/DoD boxes are left unchecked with this recorded reason.
- QA verdict (chained via `brain_turn`, [QA Engineer]): QA_PASSED. Findings F1 (vendor skip hardening), F2 (sentinel vs. semantic detection), F3 (redundant report path), F4 (exit-code-0 boxes left unchecked — correct), F5 (wider phrase sweep prose-only). None blocking.
- Code Review verdict (chained via `brain_turn`, [Code Reviewer]): APPROVED, STATUS PO_REVIEW_PENDING, BLOCKER F7 (waiver-with-baseline vs. deferral decision before closure). Findings F6 (docstring widening deliberate), F7 (exit-code gate decision), F8 (planning ritual — read the enclosing symbol), F9 (`claim_next` header stamping follow-up), F10 (conventional commit message suggestion). No code change required.
- Closure: Manager issued the exact phrase "Approved for closure" through the review relay on 2026-11-23. That phrase is the closure approval and resolves finding F7 by explicit waiver of the exit-code-0 condition; the waiver is recorded inline on the two affected checkboxes as "waived, not met". QA verdict QA_PASSED and review verdict APPROVED / PO_REVIEW_PENDING are both recorded above. Commit message: `refactor: address context MCP tool outputs to calling agent` (55 characters, Conventional Commits `refactor` type). Feature commit plus `chore: close task 418` closure commit created via `custom_context_commit_and_clean_task`, the only commit path. No push. The deployed singleton at `~/.config/opencode/mcp-context-server/server.py` stays untouched and still needs a separate Manager-approved redeploy before agents see the new wording at runtime.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `084a94deb1234822394efce94b226742073fa32c`
<!-- END_GIT_DIFF -->
