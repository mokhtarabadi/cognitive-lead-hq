# Task 71: P0 Consistency & Safety Fixes

**File:** `tasks/backlog/71-p0-consistency-and-safety-fixes.md`
**Source:** orchestrator
**Type:** improvement
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Fix P0 consistency and safety issues: resolve documentation-only contradictions, harden Git staging/amend commands in MCP servers, fix version sync rules, resolve DESIGN.md path conflicts, and secure memory deletion permissions.

## Blueprint Reference

V8.0.0 Improvement Roadmap Phase 2

## Manager's Notes

7 micro-tasks covering documentation contradictions, MCP server hardening, and memory safety. All changes must be verified before completion.

---

## Local TODOs

- [x] Phase 1: Create Task File
- [x] Phase 2: Documentation & Path Contradictions
  - [x] AGENTS.md exception for MCP servers
  - [x] Version sync rules in versioning-and-release skill
  - [x] Design-md path conflict fix
  - [x] Archive-tasks mv -> git mv
- [x] Phase 3: MCP Server Hardening
  - [x] Harden stage_and_inject_diff git add
  - [x] Harden commit_and_clean_task (empty staged check + upstream push warning)
- [x] Phase 4: Memory Safety & Permissions
  - [x] opencode.json delete_memory to ask
  - [x] LLM.txt delete_memory to ask
  - [x] project-memory skill safety gate
- [x] Phase 5: Verification
  - [x] Python syntax check for MCP server

---

## OpenCode Execution Log & Reasoning

_(OpenCode: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

### Files Modified

| File | Change | Reasoning |
| --- | --- | --- |
| `AGENTS.md` | Added exception for MCP servers, scripts, and platform tooling | Resolves contradiction: repo is "documentation-only" but hosts MCP servers and scripts that are core to the platform. Adding explicit exceptions prevents gatekeeper halts on legitimate tooling. |
| `skill-templates/versioning-and-release/SKILL.md` | Added rules 4, 5, 6 to Phase 2 | Rules 4-5 enforce that system-prompt.md version bumps are tied to behavioral changes, not just metadata. Rule 6 ensures `[Unreleased]` is emptied after releases to prevent stale entries. |
| `skill-templates/design-md/SKILL.md` | Changed Phase 3 output path from `.stitch/DESIGN.md` to project root | Aligns with AGENTS.md Core File Locations which declares `DESIGN.md` (root) as canonical. Stitch copy is now optional and secondary. |
| `skill-templates/archive-tasks/SKILL.md` | Replaced `mv` with `git mv` + untracked fallback note | `git mv` preserves file history in Git. The fallback note handles edge cases where files aren't tracked yet. |
| `mcp-context-server/server.py` — `stage_and_inject_diff` | Hardened `git add .` with exclusion patterns | Prevents accidental staging of `.env`, `.key`, `.pem`, credentials, secrets, context-reports, and cache files. Defense-in-depth for sensitive file exposure. |
| `mcp-context-server/server.py` — `commit_and_clean_task` | Added empty-staged check + upstream push warning | Empty check prevents empty commits. Upstream warning alerts when amending a commit that has already been pushed, reducing force-push risks. |
| `opencode.json` | Changed `delete_memory` from `"allow"` to `"ask"` | Memory deletion is destructive and irreversible. Requiring user confirmation prevents accidental data loss. |
| `LLM.txt` | Changed `delete_memory` from `"allow"` to `"ask"` | Syncs with opencode.json to ensure global installations also require confirmation for memory deletion. |
| `skill-templates/project-memory/SKILL.md` | Added Safety Gate to DELETE Memory section | Agent now must output confirmation prompt and wait for Manager approval before deleting memory (except store-time supersession). Prevents autonomous memory pruning. |

### Verification

- Python syntax: `python3 -m py_compile mcp-context-server/server.py` — ✅ passed
- JSON syntax: `python3 -c "import json; json.load(open('opencode.json'))"` — ✅ passed

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `19694762beb06fbfc6acab96350df0453a8c660b`
<!-- END_GIT_DIFF -->
