# Task 0385: Comprehensive Repository Audit: Purge Contradictions, Phantoms, and Cruft across Markdowns and MCP Servers

**File:** `tasks/completed/0385-comprehensive-repo-audit.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-08T11:50:07Z
**Submitted:** 2026-11-08T11:40:43Z

## Goal

Over months of active evolution across 23 milestones, the repository has accumulated historical drift, obsolete references, and redundant clauses across its documentation and codebases:
1. **Mode Contradictions:** Lingering mentions of manual ferrying vs autonomous execution that create ambiguity for agents.
2. **Phantom Names:** References to tools, skills, or subagents that do not exist in the active runtime or were renamed.
3. **Dead References:** Citations pointing to retired components (e.g. `loop-engine/sentinel.py`, legacy CLI scripts) or obsolete line numbers.
4. **Token Bloat & Redundancy:** Duplicate instruction blocks repeated across fragments and agent specs.
5. **MCP Server Drift:** Ensuring tool schemas, error handling, blank-means-unset rules, and capability manifests strictly match prompt claims.

### Target Domains:

- **Domain 1 (Prompts):** `prompts/fragments/*.md`, `prompts/shared/*.md`, `system-prompt.md`.
- **Domain 2 (Agents):** `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`, `agents/README.md`.
- **Domain 3 (Specifications):** `AGENTS.md`, `DESIGN.md`, `docs/conventions.md`, `docs/*.md`.
- **Domain 4 (Skill Templates):** `skill-templates/*/SKILL.md`.
- **Domain 5 (FastMCP Servers):** `mcp-brain-bridge/`, `mcp-context-server/`, `mcp-lint-server/`, `mcp-memory-server/`, `mcp-planner-server/`, `zen-proxy/`.

## Manager's Notes

تمام شد — میتونی یه تسک audit بنویسی که همه چیزها جمع‌آوری بشه و هزیون‌ها و اینطور نواقص دیگه و اضافه‌ها از همه markdownها و mcp سرورها پیدا بشه و با هم رفعشون کنیم.

## Local TODOs

- [x] **Phase 1:** Execute comprehensive discovery scans across all 5 target domains and compile raw findings.
- [x] **Phase 2:** Produce the prioritized Audit Findings Catalog in `context-reports/repo-audit-findings.md`.
- [x] **Phase 3.1:** Resolve Class 1 (P1) contradictions in prompts, agents, and initialization.
- [x] **Phase 3.2:** Resolve Class 2 (P2) phantom references and broken citations in skills and docs.
- [x] **Phase 3.3:** Purge Class 3 (P3) dead text and redundancies across Markdown files and MCP servers.
- [x] **Phase 4:** Reassemble `system-prompt.md`, update `CHANGELOG.md`, append ADRs, and run test suite.

## Acceptance Criteria

- [x] Complete scan report produced covering all 5 domains with concrete file:line citations.
- [x] Zero phantom tool, skill, or subagent names survive in prompts or documentation.
- [x] All broken file and line citations are either corrected or gracefully documented.
- [x] System prompt reassembled cleanly, all unit tests (`pytest`) pass with exit code 0.
- [x] Task file verified and closed following ZAC and conventional commit protocols.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q`
- **Expected result:** All tests pass with exit code 0
- **Actual result:** 826 passed, 24 warnings
- **Exit code:** 0

## Definition of Done

- [x] `pytest tests/` passes with exit code 0
- [x] `lint_task_file` passes on all modified and active task files
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] ADRs appended to `DECISIONS.md` files where architectural rules change

## Risk & Rollback

- **Risk:** [what could go wrong]
- **Rollback plan:** [how to undo if needed]

---

## Execution Log & Reasoning

### 2026-11-08: Comprehensive Repository Audit

- Fixed orphaned text in `agents/cognitive-executor.md:441` (removed duplicate "Chain both turns directly in autopilot;" fragment).
- Synced `prompts/fragments/07-agent_skills_registry.md` with corrected version references (opencode-init validate-opencode.py path, react-vite React 19+, vue-nuxt Nuxt 4).
- Confirmed `mcp-brain-bridge/capability.py` has memory tools and web tools in AVAILABLE_EXACT.
- Created `docs/architecture.md` and `docs/data_model.md` (were referenced in AGENTS.md but absent).
- Updated `AGENTS.md` (uv run → persistent venv interpreter) and `README.md` (removed stale docs/opencode/ tree entry).
- Updated `agents/cognitive-discovery.md` permissions (added execute: allow).
- Removed unused `pathspec` from `mcp-brain-bridge/pyproject.toml`.
- Purged `2>/dev/null` DSP violations from 7 skill templates.
- Fixed citations in `07-agent_skills_registry.md` (validate-opencode.py path) and `docs/README.md` (milestone range 1-23).
- Added archival notice to `docs/history/milestone-16-summary.md`.
- Harmonized version references (react-vite React 19+, vue-nuxt Nuxt 4, opencode-init no V1).
- Bumped version to 9.77.0 and rebuilt system-prompt.md.
- Full test suite: 826 passed, 24 warnings. Docs-sync OK. Diff-check clean.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `d2802189b0da023916489218b959d022348f52cc`
<!-- END_GIT_DIFF -->
