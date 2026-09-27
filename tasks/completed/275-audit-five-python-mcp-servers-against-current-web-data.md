# Task 275: Audit five Python MCP servers against current web data

**File:** `tasks/qa/275-audit-five-python-mcp-servers-against-current-web-data.md`
**Source:** manager
**Type:** improvement
**Status:** closed (closure ordered by Manager; file move to `tasks/completed/` needs a shell this runtime lacks — see log)

## Goal

Audit the five hand-written Python MCP servers against current MCP specification and SDK data from the web, and report findings with no code changes.

## Manager's Notes

Manager order (verbatim): "audit our mcp servers. from data you find from web." Scope answers from the Manager: our 5 Python servers (custom_context, project_memory, lint, brain, manager_decisions); third-party blowsh and telegram excluded. Tracked task file requested. Plan approved with "Approved" before any work.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Inventory the five servers (code layout, dependencies, pinned versions)
- [x] Pull current web data (MCP spec version, Python SDK version, security guidance)
- [x] Audit each server against that data and write findings into this file
- [x] Verify functionality (lint + test suite green, no code changes made)

## Acceptance Criteria

- [x] All five servers inventoried with versions recorded in this file
- [x] Current web data (spec, SDK, security notes) recorded with sources
- [x] Per-server findings written, each marked pass or flagged with evidence
- [x] No source code modified during the audit (report only)

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** existing suite passes unchanged (audit makes no code edits)
- **Actual result:** 689 passed, 10 warnings in 5.89s. (Note: the task file as created named `--project mcp-persona-server`, which no longer exists — that directory was deleted in Task 191. Corrected here to `--project mcp-brain-bridge`, whose pyproject carries the `mcp[cli]>=1.0,<2.0` pin. A bare `--with pytest --with pathspec` run fails collection with `ModuleNotFoundError: No module named 'mcp'`; the canonical setup.md command with all `--with` deps is required. One rtk quoting footnote: an inline `'mcp[cli]>=1.0,<2.0'` breaks rtk's sh parsing (`cannot open 2.0`); using `--project` avoids it.)
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Web data misread as a required change; audit stays report-only so no code risk
- **Rollback plan:** No code changes planned; delete the task file if the audit is cancelled

---

## Execution Log & Reasoning

**Autopilot locked** for task 275 per Manager order "start auto pilot for task 275". Mode recorded here; lock breaks only on "manual", "stop", or a new direct order.

**Seat Check (planning gate):** domains = MCP server code, spec compliance, dependency versions → seat requested: Software Architect (API contracts). Skipped: UI/UX Designer (no UI surface, no trigger words), Senior Programmer (audit is read-only, no implementation), others (wrong phase). Trigger scan on TITLE+BODY: explicit miss on all three trigger groups (no designer keywords, no architect keywords, no programmer keywords) — "contract" appears only in Manager's Notes as "usage contract" prose, not a trigger hit.
**Brainstorm line:** not required — single-domain read-only audit, fully reversible (report only).
**Planning-gate deviation:** `brain_turn` is not exposed in this runtime's Code Mode catalog (verified via three `search` queries: planning-terms, namespace `brain`, exact `brain_turn` — no `tools.brain.*` path returned). Per Capability Preflight, the missing planning turn is not silently skipped: the Hands-drafted plan below goes to the Manager for explicit approval instead, and this deviation is logged here.

## Audit findings (read-only, no source modified)

**F1 — Inventory (repo state, verified by glob/grep/wc 2026-09-27).** Five Python servers, 8,427 LOC total. All use `from mcp.server.fastmcp import FastMCP` + stdio transport (`mcp.run(transport="stdio")`; brain-bridge uses bare `mcp.run()`, same stdio default). All five pyprojects pin `mcp[cli]>=1.0,<2.0`; uv.lock resolves **1.30.0**.

| Server | LOC | Tools |
| --- | --- | --- |
| mcp-context-server | 1,498 | 8: get_directory_tree, read_source_files, create_tree_report, extract_signatures, stage_and_inject_diff, qa_transition, commit_and_clean_task, bundle_tasks |
| mcp-memory-server | 388 | 6: store/read/delete/search_memory, list_namespaces, rebuild_memory_index |
| mcp-lint-server | 704 | 4: lint_markdown, lint_task_file, lint_all_tasks, lint_system_prompt_sync |
| mcp-decision-server (+redactor 85, +detector 149) | 1,838 | 6: extract_session_decisions, record_manager_decision, query_manager_decisions, get_sync_status, get_manager_profile, propose_profile_evolution |
| mcp-brain-bridge (+9 modules) | 3,687 | 4: get_context_bundle, read_file, grep_files, brain_turn |

Shared lib `mcp-common` (env.py, 73 lines) imported by decision + brain servers. Global install mirrors repo 1:1 (7 MCP entries incl. third-party blowsh docker + telegram upstream; `enabled: true`, per-server timeouts). Live `opencode mcp list` earlier showed 7/7 connected under opencode 2.0.18.

**F2 — Web data (sources: modelcontextprotocol.io spec 2026-07-28 + changelog, py.sdk.modelcontextprotocol.io v2 whats-new + migration guide, PyPI mcp JSON, CSA agentic-MCP guide, mcp-sec-audit paper, 3 practitioner audit guides).** Spec current revision **2026-07-28** (stateless core, `server/discover`, no handshake, no server-initiated requests, `Mcp-Method`/`Mcp-Name` routing headers). Python SDK **v2.2.0** current stable; **v1.x in maintenance** (critical/security fixes only). Upstream migration rule quoted verbatim: not ready → keep upper bound `mcp>=1.28,<2`. PyPI check 2026-09-27: latest overall **2.2.0**, latest v1.x **1.30.0** — our lock is exactly latest-v1 (an earlier string-sort claiming 1.9.4 was my sort bug, corrected with tuple comparison). Security consensus: stdio-local servers need no OAuth; controls that matter for us are input validation, no secret leakage, least-privilege tools, audit logging; untrusted-content fencing is the industry's most-missed control.

**F3 — Per-server verdicts: all PASS, keep as-is.**
- Transport: stdio + loopback `uv run` is the correct shape for local servers per every guide ("stdio behind host auth"; our host is the local opencode process, no network listener, no auth surface). V2 spec changes target HTTP/session semantics — stdio FastMCP v1 servers are operationally unaffected, proven by 7/7 connected on opencode 2.0.18.
- Dependencies: `mcp[cli]>=1.0,<2.0` + locked latest-v1 1.30.0 is exactly the upstream-advised posture. SDK v2 migration (`FastMCP`→`MCPServer`, constructor/run split, `mcp_types`, httpx2) is optional; no trigger today.
- Dangerous patterns: zero hits for `shell=True`, `os.system`, `eval(`, `pickle.loads`, `exec(` across all five servers + common. `subprocess` uses are list-form only: context-server `git add/mv/diff/rev-parse/commit` (the ZAC-approved commit path), decision-server `git -C <repo>` helper and `sys.executable scripts/compile_profile.py` (both capture_output, timeouts). No tokens in code; `BRAIN_API_KEY` via env.
- `mcp-persona-server/` is **gone** (deleted in Task 191, 2026-09-12) — global install already clean (no dir, no config entry). One stale sentence in memory `workflows/global-install-upgrade` still claims "Server code dirs KEPT (not deleted)": flagged for Manager, not edited (memory writes need explicit order). **Q1 for Manager:** approve a one-line memory correction, or leave the historical note?
- Observation (not a finding): `read_source_files` returns raw file content with no untrusted-content fencing markers — matches the industry-wide gap, acceptable for a single-user loopback tool; no action proposed.

**Verdict: KEEP all five on SDK v1 pinned line; no migration, no deprecation, no code changes.** Revisit only if (a) a v1 security advisory touches our surface, or (b) a future opencode drops v1-protocol stdio support.

**Execution deviations logged:** (1) All 3 parallel `cognitive-discovery` subagents failed — this runtime's provider rejects subagent calls ("free tier can only be used from within OpenCode"); inventory done directly with read-only grep/glob/read. (2) Planning-gate `brain_turn` unavailable here (logged above); plan went to Manager and was approved with "Approved". (3) Suite command from the created task file named `--project mcp-persona-server` (deleted dir) — corrected to `--project mcp-brain-bridge` in Verification Evidence above; canonical full-dep command lives in docs/setup.md:95.

**Closure round (2026-09-27):** Manager order (verbatim): "close task 275 if finished using tools so all things auto staged and commited". Task is finished — all TODO/AC/DoD boxes checked, findings sealed, no code touched. No Brain QA ferry was completed for this task; closure proceeds on the Manager's explicit order, review skipped (not backfilled). Q1 (one-line memory correction for the stale persona-KEPT sentence) stays deferred — memory untouched without explicit approval. Post-QA brain-context probes ran under this task per "keep current task" and confirmed live `brain_turn` reachability with history attach (see session record). This runtime exposes no shell/`git mv`, so the Kanban move to `tasks/completed/` cannot be executed here: if `commit_and_clean_task` does not relocate the file, one manual `git mv tasks/qa/275-*.md tasks/completed/` plus push remains Manager-side.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `81dc8c47e90a19ef5744eea0776eda673af34bab`
<!-- END_GIT_DIFF -->
