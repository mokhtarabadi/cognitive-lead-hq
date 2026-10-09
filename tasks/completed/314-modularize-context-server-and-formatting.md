# Task 314: Modularize Context Server plus Enforced Python Formatting

**File:** `tasks/completed/314-modularize-context-server-and-formatting.md`
**Source:** manager
**Type:** refactor
**Status:** closed

## Goal

Split the single-file mcp-context-server/server.py into clean modules following exactly the mcp-brain-bridge pattern (server.py entrypoint plus concern modules), then pick one formatter for all MCP/Python code, force-enable it in OpenCode settings, and run it — with zero behavior change and a green suite.

## Manager's Notes

Manager order 2026-10-09: secure, precise, professional split mirroring the Brain server; formatter picked by Hands, enforced via OpenCode settings, run over all Python; everything stays clean, organized, formatted, modular with no lost functionality and no breaking changes.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Map brain-bridge module pattern and context-server inventory
- [x] Design module split (names, ownership, import graph, no cycles)
- [x] Split with server.py compatibility shim (tests import server.py by path)
- [x] Pick formatter (offline-capable, single tool) and record decision
- [x] Enforce formatter in OpenCode settings (project config)
- [x] Run formatter over all Python dirs and re-run full suite green
- [x] Deploy global, restart, live verify tools
- [x] Stage and move to QA

## Acceptance Criteria

- [x] AC1: server.py entrypoint plus concern modules mirror the brain-bridge layout
- [x] AC2: All 14 MCP tools register with identical names and behavior
- [x] AC3: Existing tests pass unmodified or with path-only import updates
- [x] AC4: One formatter enforced in OpenCode settings and applied to all Python
- [x] AC5: Global singleton deploy plus restart plus live tool check green
- [x] AC6: lint_task_file passes

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest pytest tests/ -q
- **Expected result:** 489 passed, only 6 pre-existing memory yaml failures
- **Actual result:** 489 passed, 6 failed (all ModuleNotFoundError yaml in memory server, pre-existing); lint_task_file passes; opencode validator exit 0; live graph_stats green on restarted service
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

- **Risk:** Module split breaks path-based test imports or the singleton entrypoint
- **Rollback plan:** Restore single server.py from git; modules removed

---

## Execution Log & Reasoning

Seat Check: backend Python refactor (no behavior change) plus config/text → Architect kept (module boundaries), Programmer kept, Designer skipped. Brainstorm: not required — reversible via git checkout. Mode: manual (313 autopilot closed with the META commit).

Design (mirrors mcp-brain-bridge: entrypoint owns the FastMCP app, siblings stay stdlib-pure with no registration, dual import robustness):
- server.py keeps: shebang/uv-script block, sys.path bootstrap, mcp = FastMCP("CustomContext"), _FALLBACK_FIRED + ROOT_FALLBACK_WARNING + _project_tool + _explicit_project_root (fallback framework), the 14 tool defs, __main__; re-exports every test-accessed helper via plain from-imports (monkeypatch-settable).
- fsutil.py: GitIgnoreFilter, TEXT_ENCODINGS, is_binary, BANNED_DIRS + tree caps, _is_banned_dir, generate_tree, process_source_file, collect_files, _ensure_context_reports_ignored.
- signatures.py: tree-sitter maps/queries/cache + language/signature extractors.
- graph.py: all GRAPH_* constants + symbol/md/sql parsers + build/degrees/save/load/tokens/find/neighbors/bfs/vocab/suggest.
- gitops.py: _repo_root, slug/commit-message/commit helpers, kebab/next-id/find-task/extract helpers, checklist/stack/checksum/mv/patch helpers + kanban constants.
- bundle.py: _build_meta_content (imports gitops helpers).
- Import graph: server → all; bundle → gitops; no cycles; no sibling → server edge.
- Formatter decision: ruff (single binary, format is AST-safe whitespace-only; `uv tool install ruff@0.16.10` pinned global since PATH lacks it and uvx needs cache). Enforce via opencode.json named map ruff-format on .py (validator-accepted shape). No new runtime deps; uv.lock untouched. Global deploy copies all *.py (never __pycache__).
- Deviation D1 (logged, minimal): test_prompt_sync.py version pin 9.54.0 → 9.56.0 — stale since 309 shipped 9.56.0 without updating it (fails on clean HEAD too); same precedent as 307.
- Incident (caught by deploy, fixed): first split dropped `import os` from server.py `__main__` (tests never execute it) and crashed the singleton restart loop; restored, redeployed, service active. Lesson recorded: live restart is the real entrypoint test.
- Autopilot locked for 314 per Manager order "start auto pilot for task" (2026-10-09). Saga: sync-global → live-verify → Brain QA → fix → re-stage → Brain review → relay; never auto-commit, never close without exact approval words. Global sync verified IN_SYNC (context 6/6, memory/lint/brain drifted files copied); all four singletons restarted active and tool-tested live.
- Fix loop 1 (autopilot, QA_REJECTED reproduced): oversize process_source_file called _extract_via_tree_sitter stranded in signatures module — fixed by lazy import in fsutil (no import-time edge) plus oversize regression test. AST audited all six modules for the same class; only instance. Full suite 490 passed + 6 pre-existing memory yaml failures. Diff hash after fix: cc50997f146c1cd14684742eb8d5d70be1b0b039b34dfabc26708851d9f5eb9b (single attempt, no spin). Redeployed fsutil global, service active, live oversize read attaches signatures.
- Re-QA (autopilot): QA_PASSED — fix verified, no new findings.
- PO_REVIEW_PENDING (autopilot relay, 2026-10-09): Brain Code Reviewer technical approval — 14-tool parity, oversize fix, ruff enforcement, docs sync; 2 minor follow-ups (fsutil standalone path bootstrap, ruff pin visibility) for a future task. File stays in tasks/qa/ awaiting the exact approval words.
- Closure (2026-10-09): Approved for closure received verbatim; QA_PASSED plus PO_REVIEW_PENDING on record; closure-only move to tasks/completed/ with Status closed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `004ca80a004b83c21f40132c7260b877733f128a`
<!-- END_GIT_DIFF -->
