# Task 0355: Graph coverage honesty and search ergonomics

**File:** `tasks/qa/0355-graph-coverage-and-search-ergonomics.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress
**Submitted:** 2026-10-27T06:35:02Z
**Estimate:** 3h
**Deadline:** 2026-10-28
**Started:** 2026-10-27T06:23:40Z

## Goal

Make the lite graph find things reliably: index recent work instead of truncating it silently, report coverage on every surface, accept the IDs it prints, rank exact symbols above prose, return signatures inline, and stop the code-search skill from describing tool contracts that do not exist.

## Manager's Notes

> now start smoke test our graph and $code-search skill, it comperhensive ? to easy find a things? or can make it even better? why?

> fix all in one task.

## Smoke-test evidence (2026-10-27)

- Build: 4.24s, 5000 nodes exactly (node cap), 7387 edges, 345 of 587 indexable files (59%).
- Missing 243 files: `tasks/` 190, `.opencode/memory` 31, `services/` 7. Recent task files 0352-0354 absent while archive 233 present, because docs are ordered by `(depth, path)` and truncated at 300.
- `explain_node` and `shortest_path` reject the `sym:...#...` IDs that `query_graph` prints; only bare labels work.
- `extract_signatures` returns only a report path (no inline text), has no directory mode, and returns nothing for Markdown/HTML, which is 521 of 609 tracked files. The skill simultaneously says to prefer signatures and never to read generated reports.
- `god_nodes` returns `output` and `system-prompt` from inline JS in `tools/prompt-composer/index.html`, plus three bare `main`s from different files.
- `query_graph` ranks prose sections over the actual symbol for natural queries; `get_directory_tree` dumps 28.6 KB at the repo root with no depth control.

## Local TODOs

- [x] Graph: caps, filters, recency ordering, coverage metadata, ID lookup, seed weighting
- [x] Tools: stats/query coverage lines, staleness, god-node hygiene, tree depth, inline signatures
- [x] Tests for each behaviour
- [x] Docs: context-server README + ADR, CHANGELOG, code-search skill (repo + global)
- [x] Suite and task lint

## Acceptance Criteria

- [x] `build_graph` orders task docs by lane and newest id first, takes `include`/`exclude` globs and cap overrides, and saves coverage metadata (scanned/indexed files and docs, caps, truncation reasons, build time).
- [x] Default caps index this repository fully (no silent 41% loss).
- [x] `graph_stats` prints coverage, caps, truncation reasons and a staleness verdict.
- [x] `query_graph` prints a one-line coverage caveat when the graph is truncated and scores symbols above files above sections on equal overlap.
- [x] `explain_node` and `shortest_path` resolve `sym:`/`file:`/`sec:` IDs exactly as printed.
- [x] `god_nodes` qualifies each label with its file, drops generic names, and never shows two identical bare labels.
- [x] `extract_signatures` accepts a file or a directory, returns the signatures inline (capped) alongside the report path, and says so for Markdown/HTML.
- [x] `get_directory_tree` and `create_tree_report` expose `max_depth` and `max_entries`.
- [x] `skill-templates/code-search/SKILL.md` and the global copy describe the real contracts and add a graph-first decision table and a coverage check.
- [x] Context-server README, DECISIONS ADR, CHANGELOG updated; suite and `lint_task_file` green.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/ -q`
- **Expected result:** full suite green including the new graph and signature tests
- **Actual result:** seven new tests pass (`test_graph_indexes_recent_tasks_and_reports_coverage`, `test_graph_resolves_printed_ids_and_qualifies_god_nodes`, `test_query_graph_prefers_symbols_over_sections`, `test_graph_stats_reports_stale_sources`, `test_graph_cap_overrides_and_include_filter`, `test_extract_signatures_inline_and_directory`, `test_directory_tree_depth_is_bounded`); full suite `745 passed in 53.07s`, exit 0. Live rebuild on this repo: `7581 nodes, 11741 links in 2.61s`, `Coverage: 49/49 files, 522/522 docs (complete)`; `explain_node("sym:mcp-lint-server/server.py#_resolve_task_reference")` resolves; the "never trim brain results" query seeds on the new test and `tasks/completed/0354-...`; `extract_signatures("mcp-brain-bridge")` returns 5 files inline with no `.venv` contamination.
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** raising caps increases build time and graph size; measured, and caps stay overridable.
- **Risk:** changing the tree default depth alters output for existing callers; documented, and depth stays a parameter.
- **Risk:** inline signatures enlarge tool results; capped by `max_chars`.
- **Rollback:** restore the previous constants, signatures and tool signatures; graphs rebuild from source.

---

## Execution Log & Reasoning

**What the smoke test proved.** Three failures, not one. Coverage was partial and silent (345/587 files, node cap exactly 5000), and the missing set held the three most recent task files because docs sorted `(depth, path)`; the printed `sym:`/`sec:` IDs were rejected by the two tools that take endpoints; and the signature tool returned only a report path while the code-search skill forbade opening generated reports, so its "prefer signatures" step was a dead end. The rest was ergonomics: prose outranked symbols, god nodes carried generic JS identifiers, and the root tree dumped 28 KB.

**Seat Check.** Domains: graph engine and tool contracts, plus a skill rewrite. Whole-word trigger `index` fired in the task body → Software Architect. UI/UX Designer skipped (no user-visible surface), QA/Reviewer later stages. Brainstorm: not required — one component plus one skill, reversible, and the smoke test already fixed the scope.

**Planning gate.** The Manager's own order is the plan: the smoke-test findings define the seven fixes and "fix all in one task" authorises them. No separate Brain planning round.

**Implementation.** Caps 300/300/5000 → 600/600/12000, every one overridable by `include`/`exclude`/`max_*`. Task docs now sort lane-first and newest-id-first, which is what keeps 0354 in the graph after a cap hit. The build stores `scanned`, `indexed`, `caps`, `truncated`, `built_at` and the indexed source list in the graph envelope, so `graph_stats` and `query_graph` can print one honest coverage line and name a source modified after the build as `STALE`. `_find_graph_nodes` tries the exact ID first, then the exact label, which makes the printed IDs round-trip. Seeds score `overlap × kind weight` (symbol 3, file 2, section 1) with +50 for an exact match. `god_nodes` uses confidence-weighted degree and qualified labels, and the noise set gained `output`, `system-prompt`, `role`, `wrapper`. `extract_signatures` now takes a directory through `collect_files` (so `.gitignore` keeps `.venv` out — the first rglob attempt returned 200 venv files), returns text inline up to `max_chars`, and reports Markdown/HTML as unsupported. Trees take `max_depth` (default 3) and `max_entries`. The skill was rewritten around the graph-first flow with a tool-choice table.

**Live numbers after the change.** Build 2.61-3.31s, 7,581 nodes, 11,741 edges, 49/49 code files and 522/522 docs. The symbol/noise/ID/ranking fixes are visible in the query output quoted in the evidence above.

**Deployment.** Global `mcp-context-server` copies (`server.py`, `graph.py`) and the global `code-search` skill were synced with native writes; `cmp` verifies both. The running `mcp-context` singleton keeps the old build until the Manager restarts it.

**Assumptions.** A1: caps 600/600/12000 (covers this repo with headroom, still bounded). A2: tree depth default 3 (files under `mcp-*/` remain visible while deep doc trees stop dominating). A3: 200-file cap and 12,000-char inline cap for signatures.

**QA cycle 1 (Brain).** `QA_REJECTED` with two blocking defects and three test gaps. F1: the doc-file loop and the rationale link cap still compared against `GRAPH_MAX_NODES`, so a `max_nodes` override leaked on the doc path. F2: `STALE` only stats indexed sources, so a newly added file is invisible. Fixed: both guards now use `cap_nodes`, and overrides are clamped (files/docs 1–5000, nodes 1–200000) so a trusted caller cannot wedge the single-threaded server; the `STALE` scope is documented in the README invariant and the ADR. New test `test_graph_cap_overrides_and_include_filter` builds with `max_nodes=6` (asserted bound) and with `include=["a.py"]` (asserted single source).

**QA cycle 2 (Brain).** `QA_PASSED`. F1 verified closed at `graph.py:691/717/734` with both link caps on `cap_nodes * 2`; F2 accepted as documented limitation (README invariant, ADR). Non-blocking residue: the one-second `built_at` truncation window and the absence of a test for the documented `STALE` miss.

**Review cycle 1 (Brain).** `APPROVED_WITH_CHANGES`: one factual defect — the CHANGELOG said six new tests where seven exist — plus a low note that the tree default has no README line (reviewer asked to defer it to the next edit of that file, not a new task). Count corrected to seven; `tests/test_mcp_servers.py` re-ran 96 passed, exit 0.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index ffc2d3f..b8d1a13 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Graph coverage honesty, round-trippable IDs and inline signatures (Task 0355):** a smoke test found the lite graph indexing 345 of 587 files silently, and the missing set included the newest task files because docs were ordered `(depth, path)` and cut at 300. The graph now orders task docs lane-first and newest-id-first, defaults to 600 files / 600 docs / 12000 nodes, accepts `include`/`exclude` globs plus `max_files`/`max_docs`/`max_nodes` overrides, and stores coverage metadata (scanned, indexed, caps, truncation flags, indexed source list) in the graph envelope. `graph_stats` and `query_graph` print a coverage line, including `truncated: …` ("absence here is not proof of absence") and a `STALE` verdict naming the first source modified after the build. `explain_node` and `shortest_path` resolve the `sym:path#name`, `sec:path#slug` and `file:path` IDs the graph prints. Seed ranking weights symbols above files above sections with an exact-label bonus; `god_nodes` uses confidence-weighted degree, qualifies each label with its file and drops generic identifiers. `extract_signatures` accepts a directory (`.gitignore`-aware, 200-file cap), returns the signature text inline alongside the report path (capped by `max_chars`), and reports Markdown/HTML as unsupported instead of an empty success. `get_directory_tree` and `create_tree_report` expose `max_depth` (default 3) and `max_entries`. The `code-search` skill (repo template plus global copy) is rewritten around the graph-first flow with a tool-choice table and the real tool contracts. On this repo the rebuild indexes 49/49 code files and 522/522 docs in 3.3s (7,582 nodes, 11,720 edges); six new tests cover recency, coverage reporting, ID round-trip, ranking, staleness, inline/directory signatures and the depth bound.
+
 - Task time is now measured, not estimated. `claim_next` stamps `**Started:**`, `qa_transition` stamps `**Submitted:**` and `commit_and_clean_task` stamps `**Finished:**` as ISO-8601 UTC, each write-once so a re-claim never rewrites the original start. `_task_brief` derives `elapsed_seconds` and `qa_wait_seconds` (`null`, never `0`, when a stamp is missing), the task modal shows `measured 2h 14m`, and `sprint_stats` adds a separate `Completed measured` line beside the estimate. `_check_planner_metadata` rejects a non-UTC stamp or a finish earlier than its start, and flags a duplicated stamp the same way it flags a duplicated key. 19 new tests; full suite 734 green.
 
 - **Planner writes its own metadata, and the lint refuses to let it drift (Task 0350):** an approved plan used to reach the task files only by hand-editing headers, the one place where a stray space or a free-text date drops a task out of capacity and the timeline with no error on either side. New Planner tool `schedule_tasks(project_root, "id:estimate:deadline[:deps], …")` is the single writer for `**Estimate:**`, `**Deadline:**` and `**Depends on:**`: it resolves the id in the active lanes, replaces an existing line or inserts one directly after `**Status:**` (final order Estimate, Deadline, Depends on), leaves the rest of the file byte-identical, writes atomically, is idempotent, and is all-or-nothing so one malformed entry rejects the whole batch instead of leaving half a schedule. Rejections are explicit per entry (unknown or archived id, duplicate id, estimate that is not `Nh`/`N.Nh`, deadline that is not `YYYY-MM-DD`, dependencies that are not ids); `-` leaves a value untouched and clearing stays a Manager decision. Paired lint gate `_check_planner_metadata` (in `lint_task_file` and `lint_all_tasks`) enforces the same formats and flags a duplicated key, so a hallucinated format fails before staging instead of vanishing from the read model; absence stays valid for legacy files. The executor now calls the tool after plan approval and is told never to hand-edit those lines — fragment 11 and `agents/cognitive-executor.md` agree, `system-prompt.md` reassembled, `<system_version>` 9.66.0 → 9.67.0, pin updated. Docs: planner and lint READMEs, ADR-010 and ADR-003. Verified: 715 tests pass, including 24 new (writer insert/update/idempotency/atomic-reject/archived/lint-after-write and lint positive, negative and absent cases).
diff --git a/mcp-context-server/DECISIONS.md b/mcp-context-server/DECISIONS.md
index b77b627..23e9c47 100644
--- a/mcp-context-server/DECISIONS.md
+++ b/mcp-context-server/DECISIONS.md
@@ -83,3 +83,10 @@
 - **Decision:** `gitops.stamp_task_header(path, field)` writes `**Submitted:**` / `**Finished:**` as ISO-8601 UTC, inserted after `**Status:**`, and only when the field is absent. Both tools call it at the moment of the move, so the stamp cannot drift from the transition.
 - **Consequences:** durations are measured at the source, re-transitions cannot overwrite a real start, and a failed stamp is harmless (the header update is already best-effort; the move is what matters). The planner reads the same lines and never writes them, keeping one writer per stamp.
 - **Rollback:** remove the two calls and the helper; the header lines become inert and the planner reports `null` durations.
+
+## [2026-10-27] ADR-013: Graph coverage honesty and search ergonomics
+
+- **Context:** A smoke test over this repo found the graph indexing 345 of 587 files without saying so, and the missing set included the three most recent task files because docs were ordered `(depth, path)` and cut at 300. The graph printed IDs (`sym:path#name`) that `explain_node` and `shortest_path` rejected, ranked prose sections above the symbol on natural queries, listed generic hubs from inline JS (`output`, `system-prompt`), and `extract_signatures` returned only a report path while the code-search skill forbade reading generated reports.
+- **Decision:** Raise the defaults to 600 files / 600 docs / 12000 nodes and make every cap overridable (`include`/`exclude` globs, `max_files`/`max_docs`/`max_nodes`). Persist coverage metadata (scanned, indexed, caps, truncation flags, source list) in the graph envelope. Order task docs lane-first and newest-id-first so caps cannot hide recent work. Print a coverage line plus a `STALE` verdict on `graph_stats` and `query_graph`. Resolve printed IDs first in `_find_graph_nodes`. Weight seed scores by node kind (symbol 3, file 2, section 1) with an exact-match bonus. Use confidence-weighted degree in `god_nodes`, qualify labels with the file and extend the generic-name noise set. `extract_signatures` accepts a directory, returns its text inline, caps at `max_chars`, and reports unsupported formats explicitly. `get_directory_tree`/`create_tree_report` expose `max_depth`/`max_entries`.
+- **Consequences:** Absence in a query is now qualified by a coverage line instead of being read as truth; a stale graph is visible; the newest work is always indexed; graph IDs are usable in follow-up calls. `STALE` covers modifications to indexed sources only: a newly added file is picked up by a rebuild, never by the staleness check, and the coverage line always describes the last build. Build time on this repo stayed about 3.3s for 7,582 nodes after the cap raise, and the larger graph is still deterministic.
+- **Rollback:** Restore the previous constants, drop the metadata and coverage lines, and revert the tool signatures; graphs rebuild from source.
diff --git a/mcp-context-server/README.md b/mcp-context-server/README.md
index 4827fe0..077b6c7 100644
--- a/mcp-context-server/README.md
+++ b/mcp-context-server/README.md
@@ -19,8 +19,11 @@ Custom-context MCP daemon: directory trees, source reads, signature extraction,
 - ZAC enforcement point: staging goes through `stage_and_inject_diff`; never `git commit` directly.
 - Path confinement: all scans stay inside project root; vendor dirs excluded.
 - Bundle lifecycle (META + supersede/archive) is the only writer of `tasks/archive/` moves.
-- Graph lite: stdlib-only deterministic build (files + symbols, contains/imports EXTRACTED, references INFERRED); caps files 300 / nodes 5000; reports under `context-reports/` (gitignored).
-- Graph unified (schema 2): same engine plus Markdown docs (file + heading-section nodes, md-link/[[wiki]] references edges, doc-to-symbol INFERRED links), SQL tables/views with REFERENCES edges, natural-word tokenizer (snake_case/camelCase split); caps docs 300.
+- Graph lite: stdlib-only deterministic build (files + symbols, contains/imports EXTRACTED, references INFERRED); caps files 600 / docs 600 / nodes 12000, all overridable per build; reports under `context-reports/` (gitignored).
+- Graph unified (schema 2): same engine plus Markdown docs (file + heading-section nodes, md-link/[[wiki]] references edges, doc-to-symbol INFERRED links), SQL tables/views with REFERENCES edges, natural-word tokenizer (snake_case/camelCase split).
+- Graph coverage honesty: every build stores scanned/indexed counts, caps, truncation reasons and source paths in the graph envelope; `graph_stats` and `query_graph` print one coverage line, and a source modified after the build is reported as `STALE`. `STALE` covers modifications to indexed sources only — a newly added file is picked up by a rebuild, not by this check, and the coverage line always reports the counts of the last build. Task docs are ordered lane-first and newest-id-first, so a cap cannot hide recent work.
+- Graph IDs round-trip: `explain_node` and `shortest_path` accept `sym:path#name`, `sec:path#slug` and `file:path` exactly as the graph prints them; bare labels remain supported but ambiguous names (`main`) need the ID.
+- Graph ranking and hubs: symbols outweigh files outweigh sections on equal overlap, exact labels win, and `god_nodes` uses confidence-weighted degree with qualified labels (`name — path`) and generic-name noise removed.
 - Graph clients (310): Kotlin fun/class/object, Swift func/types, Java methods/ctors, Dart members, Vue/Svelte script symbols, HTML/XML element ids incl. android:id; JVM/Swift imports; R.id/getElementById and doc id-mention links.
 - Graph stacks (311): arrow components in all JS/TS suffixes, Prisma models/enums, ObjC methods, properties keys, CSS selectors; correct interface/type/enum kinds.
 - Graph precision (312): full-file scans, vocab hints, DFS mode, Task/ADR rationale links, god-node noise filter, truncation note.
diff --git a/mcp-context-server/graph.py b/mcp-context-server/graph.py
index be0c07a..21c8460 100644
--- a/mcp-context-server/graph.py
+++ b/mcp-context-server/graph.py
@@ -3,6 +3,7 @@
 
 """Lite knowledge-graph: constants, parsers, build, query primitives. Stdlib-pure: no MCP imports, no registration, no import back to server."""
 
+import fnmatch
 import json
 import re
 import time
@@ -15,13 +16,13 @@ from fsutil import GitIgnoreFilter, collect_files
 GRAPH_SCHEMA_VERSION = 2
 
 
-GRAPH_MAX_FILES = 300
+GRAPH_MAX_FILES = 600
 
 
-GRAPH_MAX_NODES = 5000
+GRAPH_MAX_NODES = 12000
 
 
-GRAPH_MAX_DOCS = 300
+GRAPH_MAX_DOCS = 600
 
 
 GRAPH_DOC_LINES = 500
@@ -195,7 +196,9 @@ _GRAPH_TASK_REF_RE = re.compile(r"\bTask\s+(\d{1,4})\b")
 _GRAPH_ADR_REF_RE = re.compile(r"\bADR-(\d{1,3})\b", re.IGNORECASE)
 
 
-_GRAPH_GOD_NOISE = frozenset({"run", "json", "post", "data"})
+_GRAPH_GOD_NOISE = frozenset(
+    {"run", "json", "post", "data", "output", "system-prompt", "role", "wrapper"}
+)
 
 
 _GRAPH_MAX_SCAN_BYTES = 1048576
@@ -563,47 +566,99 @@ def _resolve_import_to_rel(mod: str, from_rel: str, rel_set: set[str]) -> str |
     return None
 
 
-def _build_graph_data(workspace_root: Path, target: Path) -> dict:
+_TASK_LANE_ORDER = {
+    "in-progress": 0,
+    "qa": 1,
+    "backlog": 2,
+    "completed": 3,
+    "archive": 4,
+}
+
+
+def _doc_order_key(rel: str) -> tuple:
+    """Order docs so recent task files survive the cap.
+
+    The old ``(depth, path)`` order put ``tasks/archive/0001-...`` first and
+    cut ``tasks/completed/0355-...`` once the doc cap was reached, so the
+    newest work was invisible in the graph. Task docs now come first, in lane
+    order (active lanes before archive) and newest id first; every other doc
+    keeps the shallow-path ordering.
+    """
+    parts = rel.split("/")
+    if len(parts) >= 3 and parts[0] == "tasks" and parts[1] in _TASK_LANE_ORDER:
+        match = re.match(r"(\d+)", parts[2])
+        number = int(match.group(1)) if match else -1
+        return (0, _TASK_LANE_ORDER[parts[1]], -number, rel)
+    return (1, len(parts), rel)
+
+
+def _graph_paths_filtered(
+    candidates: list[Path],
+    workspace_root: Path,
+    include: list[str] | None,
+    exclude: list[str] | None,
+) -> list[tuple[str, Path]]:
+    """Relative-path pairs that pass the optional include/exclude globs."""
+    pairs: list[tuple[str, Path]] = []
+    for path in candidates:
+        try:
+            rel = path.resolve().relative_to(workspace_root).as_posix()
+        except ValueError:
+            continue
+        if include and not any(fnmatch.fnmatch(rel, pat) for pat in include):
+            continue
+        if exclude and any(fnmatch.fnmatch(rel, pat) for pat in exclude):
+            continue
+        pairs.append((rel, path.resolve()))
+    return pairs
+
+
+def _build_graph_data(
+    workspace_root: Path,
+    target: Path,
+    include: list[str] | None = None,
+    exclude: list[str] | None = None,
+    max_files: int | None = None,
+    max_docs: int | None = None,
+    max_nodes: int | None = None,
+) -> dict:
+    cap_files = max(1, min(max_files or GRAPH_MAX_FILES, 5000))
+    cap_docs = max(1, min(max_docs or GRAPH_MAX_DOCS, 5000))
+    cap_nodes = max(1, min(max_nodes or GRAPH_MAX_NODES, 200000))
     filt = GitIgnoreFilter()
     all_found = collect_files(str(target), filt)
-    files = [
+    code_candidates = [
         p
         for p in all_found
         if p.suffix.lower() in _GRAPH_CODE_EXTS and "context-reports" not in p.parts
     ]
-    files.sort(key=lambda p: (len(p.parts), p.as_posix()))
-    files = files[:GRAPH_MAX_FILES]
-    docs = [
+    code_pairs = _graph_paths_filtered(
+        code_candidates, workspace_root, include, exclude
+    )
+    code_pairs.sort(key=lambda item: (len(Path(item[0]).parts), item[0]))
+    doc_candidates = [
         p
         for p in all_found
         if p.suffix.lower() == ".md" and "context-reports" not in p.parts
     ]
-    docs.sort(key=lambda p: (len(p.parts), p.as_posix()))
-    docs = docs[:GRAPH_MAX_DOCS]
-    rels: list[str] = []
-    rel_set: set[str] = set()
-    resolved: list[Path] = []
+    doc_pairs = _graph_paths_filtered(doc_candidates, workspace_root, include, exclude)
+    doc_pairs.sort(key=lambda item: _doc_order_key(item[0]))
+    scanned_files = len(code_pairs)
+    scanned_docs = len(doc_pairs)
+    code_pairs = code_pairs[:cap_files]
+    doc_pairs = doc_pairs[:cap_docs]
+    rels: list[str] = [rel for rel, _path in code_pairs]
+    rel_set: set[str] = set(rels)
+    resolved: list[Path] = [path for _rel, path in code_pairs]
     doc_rels: list[str] = []
     doc_set: set[str] = set()
     doc_resolved: list[Path] = []
-    for p in files:
-        try:
-            rel = p.resolve().relative_to(workspace_root).as_posix()
-        except ValueError:
-            continue
-        if rel not in rel_set:
-            rel_set.add(rel)
-            rels.append(rel)
-            resolved.append(p.resolve())
-    for p in docs:
-        try:
-            rel = p.resolve().relative_to(workspace_root).as_posix()
-        except ValueError:
+    for rel, path in doc_pairs:
+        if rel in rel_set or rel in doc_set:
             continue
-        if rel not in doc_set and rel not in rel_set:
-            doc_set.add(rel)
-            doc_rels.append(rel)
-            doc_resolved.append(p.resolve())
+        doc_set.add(rel)
+        doc_rels.append(rel)
+        doc_resolved.append(path)
     nodes: list[dict] = []
     links: list[dict] = []
     sym_index: dict[str, list[str]] = {}
@@ -633,7 +688,7 @@ def _build_graph_data(workspace_root: Path, target: Path) -> dict:
         else:
             symbols = _extract_graph_symbols(abs_p)
         for name, kind, lineno in symbols:
-            if len(nodes) >= GRAPH_MAX_NODES:
+            if len(nodes) >= cap_nodes:
                 break
             sid = f"sym:{rel}#{name}"
             nodes.append(
@@ -657,8 +712,9 @@ def _build_graph_data(workspace_root: Path, target: Path) -> dict:
             )
             sym_index.setdefault(name, []).append(sid)
     doc_contents: dict[str, str] = {}
+    seen_section_ids: set[str] = set()
     for rel, abs_p in zip(doc_rels, doc_resolved):
-        if len(nodes) >= GRAPH_MAX_NODES:
+        if len(nodes) >= cap_nodes:
             break
         nodes.append(
             {
@@ -675,10 +731,11 @@ def _build_graph_data(workspace_root: Path, target: Path) -> dict:
             content = ""
         doc_contents[rel] = content
         for heading, _level, lineno in _extract_md_sections(abs_p):
-            if len(nodes) >= GRAPH_MAX_NODES:
+            if len(nodes) >= cap_nodes:
                 break
             sec_id = f"sec:{rel}#{_slugify_section(heading)}"
-            if sec_id not in {n["id"] for n in nodes}:
+            if sec_id not in seen_section_ids:
+                seen_section_ids.add(sec_id)
                 nodes.append(
                     {
                         "id": sec_id,
@@ -699,7 +756,7 @@ def _build_graph_data(workspace_root: Path, target: Path) -> dict:
                     }
                 )
     for rel, content in doc_contents.items():
-        if not content or len(links) >= GRAPH_MAX_NODES * 2:
+        if not content or len(links) >= cap_nodes * 2:
             break
         for tgt in _extract_md_link_targets(content):
             resolved_tgt = _resolve_doc_link(tgt, rel, doc_set)
@@ -733,7 +790,7 @@ def _build_graph_data(workspace_root: Path, target: Path) -> dict:
                             "source_file": rel,
                         }
                     )
-                if len(seen_doc_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
+                if len(seen_doc_refs) >= 40 or len(links) >= cap_nodes * 2:
                     break
     for rel in rels:
         content = file_contents.get(rel, "")
@@ -752,7 +809,7 @@ def _build_graph_data(workspace_root: Path, target: Path) -> dict:
                         "source_file": rel,
                     }
                 )
-        if len(links) >= GRAPH_MAX_NODES * 2:
+        if len(links) >= cap_nodes * 2:
             break
         seen_refs: set[str] = set()
         for id_re in (_GRAPH_R_ID_RE, _GRAPH_GET_ID_RE):
@@ -801,9 +858,9 @@ def _build_graph_data(workspace_root: Path, target: Path) -> dict:
                         "source_file": rel,
                     }
                 )
-                if len(seen_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
+                if len(seen_refs) >= 40 or len(links) >= cap_nodes * 2:
                     break
-            if len(seen_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
+            if len(seen_refs) >= 40 or len(links) >= cap_nodes * 2:
                 break
     rationale_refs: list[tuple[str, str, str]] = []
     for rel in rels:
@@ -847,7 +904,7 @@ def _build_graph_data(workspace_root: Path, target: Path) -> dict:
                 if n["id"].startswith("sec:") and needle in n["label"].lower():
                     target = n["id"]
                     break
-        if target and target in node_ids and len(links) < GRAPH_MAX_NODES * 2:
+        if target and target in node_ids and len(links) < cap_nodes * 2:
             if (rel, target) in seen_rat:
                 continue
             seen_rat.add((rel, target))
@@ -873,7 +930,27 @@ def _build_graph_data(workspace_root: Path, target: Path) -> dict:
                 continue
             e = {**e, "target": tid}
         pruned.append(e)
-    return {"nodes": nodes, "links": pruned}
+    newest = 0.0
+    for path in resolved + doc_resolved:
+        try:
+            newest = max(newest, path.stat().st_mtime)
+        except OSError:
+            continue
+    meta = {
+        "built_at": int(time.time()),
+        "target": str(target),
+        "caps": {"files": cap_files, "docs": cap_docs, "nodes": cap_nodes},
+        "scanned": {"files": scanned_files, "docs": scanned_docs},
+        "indexed": {"files": len(rels), "docs": len(doc_rels)},
+        "truncated": {
+            "files": scanned_files > len(rels),
+            "docs": scanned_docs > len(doc_rels),
+            "nodes": len(nodes) >= cap_nodes,
+        },
+        "newest_source_mtime": int(newest),
+        "sources": rels + doc_rels,
+    }
+    return {"nodes": nodes, "links": pruned, "meta": meta}
 
 
 def _graph_degrees(data: dict) -> dict[str, int]:
@@ -905,6 +982,7 @@ def _save_graph(
             "schema_version": GRAPH_SCHEMA_VERSION,
             "graphify_version": None,
             "root": target_label,
+            **(data.get("meta") or {}),
         },
     }
     with open(json_path, "w", encoding="utf-8") as f:
@@ -999,7 +1077,11 @@ def _graph_tokens(text: str) -> set[str]:
 
 
 def _find_graph_nodes(nodes: list[dict], label: str) -> list[dict]:
-    ll = label.lower()
+    needle = label.strip()
+    exact_id = [n for n in nodes if n.get("id", "") == needle]
+    if exact_id:
+        return exact_id
+    ll = needle.lower()
     exact = [n for n in nodes if n.get("label", "").lower() == ll]
     if exact:
         return exact
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index f2bdb31..945a4ee 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -182,8 +182,29 @@ def _project_tool(fn):
     return mcp.tool()(wrapper)
 
 
+def _safe_depth(value: object) -> int:
+    """Clamp a caller-supplied tree depth to the supported range."""
+    try:
+        return max(1, min(int(value), TREE_MAX_DEPTH))
+    except (TypeError, ValueError):
+        return 3
+
+
+def _safe_entries(value: object) -> int:
+    """Clamp a caller-supplied tree entry cap to the supported range."""
+    try:
+        return max(1, min(int(value), TREE_MAX_ENTRIES))
+    except (TypeError, ValueError):
+        return TREE_MAX_ENTRIES
+
+
 @_project_tool
-def get_directory_tree(target_path: str = ".", project_root: str | None = None) -> str:
+def get_directory_tree(
+    target_path: str = ".",
+    project_root: str | None = None,
+    max_depth: int = 3,
+    max_entries: int = TREE_MAX_ENTRIES,
+) -> str:
     """Generates an ASCII tree representation of the directory, respecting .gitignore. Use this to discover codebase structure with immediate inline output. Use create_tree_report instead when a persistent saved report file is required. project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
     # Security: mirror create_tree_report — coerce bad types, resolve against
     # the workspace root, reject escapes. Previously a bare "/" walked the
@@ -207,8 +228,12 @@ def get_directory_tree(target_path: str = ".", project_root: str | None = None)
         return f"Error: {target_path} is not a valid directory."
     if ignore_filter.is_ignored(tree_path):
         return f"Warning: Target tree path is ignored by .gitignore: {target_path}"
-    return f"## Directory Tree: `{tree_path}`\n\n" + generate_tree(
-        tree_path, ignore_filter
+    depth = _safe_depth(max_depth)
+    entries = _safe_entries(max_entries)
+    return (
+        f"## Directory Tree: `{tree_path}`\n\n"
+        f"(depth {depth}, entry cap {entries}; pass max_depth/max_entries for more)\n\n"
+        + generate_tree(tree_path, ignore_filter, max_depth=depth, max_entries=entries)
     )
 
 
@@ -220,7 +245,15 @@ def get_directory_tree(target_path: str = ".", project_root: str | None = None)
 
 
 @_project_tool
-def build_graph(target_path: str = ".", project_root: str | None = None) -> str:
+def build_graph(
+    target_path: str = ".",
+    project_root: str | None = None,
+    include: list[str] | None = None,
+    exclude: list[str] | None = None,
+    max_files: int | None = None,
+    max_docs: int | None = None,
+    max_nodes: int | None = None,
+) -> str:
     """Builds a unified deterministic knowledge-graph (code incl. SQL plus Markdown docs: files + symbols + sections, contains/imports/references with EXTRACTED/INFERRED tags) and saves versioned graph.json plus a markdown report under context-reports/. Use before query_graph/explain_node/shortest_path/god_nodes. project_root scopes the scan; target_path scopes the subgraph."""
     if not isinstance(target_path, str):
         target_path = "."
@@ -242,10 +275,35 @@ def build_graph(target_path: str = ".", project_root: str | None = None) -> str:
     if not tgt.exists():
         return f"Error: {target_path} not found."
     started = time.monotonic()
-    data = _build_graph_data(workspace_root, tgt if tgt.is_dir() else tgt.parent)
+    data = _build_graph_data(
+        workspace_root,
+        tgt if tgt.is_dir() else tgt.parent,
+        include=include if isinstance(include, list) else None,
+        exclude=exclude if isinstance(exclude, list) else None,
+        max_files=max_files if isinstance(max_files, int) else None,
+        max_docs=max_docs if isinstance(max_docs, int) else None,
+        max_nodes=max_nodes if isinstance(max_nodes, int) else None,
+    )
     json_path, md_path = _save_graph(workspace_root, data, str(tgt))
     dur = time.monotonic() - started
-    return f"✅ Success: Graph built for `{tgt}`.\n📊 {len(data['nodes'])} nodes, {len(data['links'])} links in {dur:.2f}s (schema {GRAPH_SCHEMA_VERSION}, caps files {GRAPH_MAX_FILES}).\n📁 Graph: `{json_path}`\n📁 Report: `{md_path}`"
+    meta = data.get("meta", {})
+    caps = meta.get("caps", {})
+    scanned = meta.get("scanned", {})
+    indexed = meta.get("indexed", {})
+    reasons = [name for name, hit in (meta.get("truncated") or {}).items() if hit]
+    coverage = (
+        f"📈 Coverage: {indexed.get('files', 0)}/{scanned.get('files', 0)} files, "
+        f"{indexed.get('docs', 0)}/{scanned.get('docs', 0)} docs"
+        + (f" (truncated: {', '.join(reasons)})" if reasons else " (complete)")
+    )
+    return (
+        f"✅ Success: Graph built for `{tgt}`.\n"
+        f"📊 {len(data['nodes'])} nodes, {len(data['links'])} links in {dur:.2f}s "
+        f"(schema {GRAPH_SCHEMA_VERSION}, caps files {caps.get('files')}/docs "
+        f"{caps.get('docs')}/nodes {caps.get('nodes')}).\n"
+        f"{coverage}\n"
+        f"📁 Graph: `{json_path}`\n📁 Report: `{md_path}`"
+    )
 
 
 @_project_tool
@@ -269,12 +327,19 @@ def query_graph(
     if err or data is None:
         return f"Error: {err}"
     toks = _graph_tokens(question)
+    exact_needle = question.strip().lower()
     scored: list[tuple[int, dict]] = []
     for n in data.get("nodes", []):
         nt = _graph_tokens(f"{n.get('label', '')} {n.get('source_file', '')}")
-        s = len(toks & nt)
-        if s > 0:
-            scored.append((s, n))
+        overlap = len(toks & nt)
+        if overlap == 0 and n.get("label", "").lower() != exact_needle:
+            continue
+        nid = n.get("id", "")
+        weight = 3 if nid.startswith("sym:") else 2 if nid.startswith("file:") else 1
+        score = overlap * weight
+        if n.get("label", "").lower() == exact_needle or nid.lower() == exact_needle:
+            score += 50
+        scored.append((score, n))
     scored.sort(key=lambda x: (-x[0], x[1]["id"]))
     seeds = [n for _, n in scored[:3]]
     if not seeds:
@@ -326,6 +391,7 @@ def query_graph(
     lines = [
         f"Query ({mode}): {question}",
         f"Graph: `{gp}`",
+        _graph_coverage_line(data, workspace_root),
         f"Seeds: {', '.join(s.get('label', '?') for s in seeds)}",
         "",
         f"Nodes ({len(keep)}):",
@@ -448,7 +514,12 @@ def god_nodes(
     data, gp, err = _load_graph_data(workspace_root, graph_path)
     if err or data is None:
         return f"Error: {err}"
-    deg = _graph_degrees(data)
+    weights = {"EXTRACTED": 2, "INFERRED": 1}
+    deg: dict[str, int] = {n["id"]: 0 for n in data.get("nodes", [])}
+    for e in data.get("links", []):
+        w = weights.get(e.get("confidence"), 1)
+        deg[e["source"]] = deg.get(e["source"], 0) + w
+        deg[e["target"]] = deg.get(e["target"], 0) + w
     id2n = {n["id"]: n for n in data.get("nodes", [])}
 
     def _noisy(label: str) -> bool:
@@ -469,11 +540,61 @@ def god_nodes(
     for d, nid in ranked:
         n = id2n.get(nid, {})
         lines.append(
-            f"- {n.get('label', '?')} (degree {d}, {n.get('source_file', '?')} {n.get('source_location', '')})"
+            f"- {n.get('label', '?')} — {n.get('source_file', '?')}"
+            f"{(' ' + n.get('source_location')) if n.get('source_location') else ''}"
+            f" (weighted degree {d})"
         )
     return "\n".join(lines)
 
 
+def _graph_stale_source(data: dict, workspace_root: Path) -> str | None:
+    """Name the first indexed source modified after the build, if any."""
+    meta = data.get("graph", {}) or {}
+    built_at = meta.get("built_at")
+    sources = meta.get("sources") or []
+    if not built_at or not sources:
+        return None
+    newest_mtime = 0.0
+    newest_path: str | None = None
+    for rel in sources:
+        try:
+            mtime = (workspace_root / rel).stat().st_mtime
+        except OSError:
+            continue
+        if mtime > newest_mtime:
+            newest_mtime, newest_path = mtime, rel
+    return newest_path if newest_mtime > built_at else None
+
+
+def _graph_coverage_line(data: dict, workspace_root: Path) -> str:
+    """One line that makes partial coverage and staleness impossible to miss."""
+    meta = data.get("graph", {}) or {}
+    scanned = meta.get("scanned") or {}
+    indexed = meta.get("indexed") or {}
+    caps = meta.get("caps") or {}
+    truncated = meta.get("truncated") or {}
+    if not scanned:
+        return "Coverage: unknown (graph built before coverage metadata; rebuild)."
+    flags = [name for name, hit in truncated.items() if hit]
+    line = (
+        f"Coverage: {indexed.get('files', 0)}/{scanned.get('files', 0)} files, "
+        f"{indexed.get('docs', 0)}/{scanned.get('docs', 0)} docs; caps "
+        f"files {caps.get('files', '?')}/docs {caps.get('docs', '?')}/"
+        f"nodes {caps.get('nodes', '?')}"
+    )
+    if flags:
+        line += (
+            f"; truncated: {', '.join(flags)} — absence here is not proof of "
+            "absence, rebuild or narrow with include"
+        )
+    else:
+        line += "; complete"
+    stale = _graph_stale_source(data, workspace_root)
+    if stale:
+        line += f"; STALE: `{stale}` changed after the build (rebuild)"
+    return line
+
+
 @_project_tool
 def graph_stats(graph_path: str | None = None, project_root: str | None = None) -> str:
     """Reports node/edge counts plus EXTRACTED/INFERRED/AMBIGUOUS split and schema version for a built graph."""
@@ -488,7 +609,13 @@ def graph_stats(graph_path: str | None = None, project_root: str | None = None)
     inf = sum(1 for e in data.get("links", []) if e.get("confidence") == "INFERRED")
     tot = len(data.get("links", []))
     schema = (data.get("graph", {}) or {}).get("schema_version", "?")
-    return f"Graph: `{gp}`\nNodes: {len(data.get('nodes', []))} Edges: {tot} (EXTRACTED {ext} / INFERRED {inf} / AMBIGUOUS {tot - ext - inf})\nSchema: {schema}"
+    return (
+        f"Graph: `{gp}`\n"
+        f"Nodes: {len(data.get('nodes', []))} Edges: {tot} "
+        f"(EXTRACTED {ext} / INFERRED {inf} / AMBIGUOUS {tot - ext - inf})\n"
+        f"{_graph_coverage_line(data, workspace_root)}\n"
+        f"Schema: {schema}"
+    )
 
 
 @_project_tool
@@ -573,7 +700,12 @@ def read_source_files(
 
 
 @_project_tool
-def create_tree_report(target_path: str = ".", project_root: str | None = None) -> str:
+def create_tree_report(
+    target_path: str = ".",
+    project_root: str | None = None,
+    max_depth: int = 3,
+    max_entries: int = TREE_MAX_ENTRIES,
+) -> str:
     """Creates a .gitignore-aware directory tree of a path or the entire project and saves it as a Markdown file under context-reports/ (named tree_report_<timestamp>_<uuid>.md). Use when the Manager asks to 'create a tree of the project' or 'create a tree of <path>'. Security: target_path is resolved against the workspace root and rejected if it escapes the project (path traversal prevention). project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
     # Security: Coerce None or invalid types back to the whole-project default
     # so a malformed tool invocation degrades gracefully instead of crashing.
@@ -605,7 +737,12 @@ def create_tree_report(target_path: str = ".", project_root: str | None = None)
     if ignore_filter.is_ignored(tree_path):
         return f"Warning: Target tree path is ignored by .gitignore: {target_path}"
 
-    tree_text = generate_tree(tree_path, ignore_filter)
+    tree_text = generate_tree(
+        tree_path,
+        ignore_filter,
+        max_depth=_safe_depth(max_depth),
+        max_entries=_safe_entries(max_entries),
+    )
 
     # Ensure the PROJECT's output directory exists (never the server cwd).
     report_dir = workspace_root / "context-reports"
@@ -637,9 +774,62 @@ def create_tree_report(target_path: str = ".", project_root: str | None = None)
     )
 
 
+_SIGNATURE_EXTS = {
+    ".py",
+    ".js",
+    ".jsx",
+    ".mjs",
+    ".cjs",
+    ".ts",
+    ".tsx",
+    ".mts",
+    ".cts",
+    ".go",
+    ".java",
+    ".jsp",
+    ".rs",
+    ".kt",
+    ".kts",
+    ".swift",
+    ".rb",
+    ".php",
+    ".cs",
+}
+
+
+def _signature_block(path: Path, label: str) -> str | None:
+    """Tree-sitter first, regex fallback. None when the file has no signature."""
+    try:
+        ts_result = _extract_via_tree_sitter(path)
+    except Exception:
+        ts_result = None
+    if ts_result:
+        return ts_result
+    try:
+        with open(path, "r", encoding="utf-8") as f:
+            content = f.read()
+    except Exception:
+        return None
+    pattern = re.compile(
+        r"^(?:\s*(?:export|default|public|private|protected|internal|pub|static|abstract|final|override|inline|open|suspend)\s+)*"
+        r"(?:class|struct|enum|trait|impl|interface|type|def|fun|func(?:tion)?)\s+\w+.*$",
+        re.MULTILINE,
+    )
+    arrow_pattern = re.compile(
+        r"^(?:export\s+)?(?:const|let)\s+\w+\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=]*)\s*=>.*$",
+        re.MULTILINE,
+    )
+    all_matches = pattern.findall(content) + arrow_pattern.findall(content)
+    if not all_matches:
+        return None
+    return f"### Signatures in {label}\n" + "\n".join(all_matches)
+
+
 @_project_tool
-def extract_signatures(file_path: str, project_root: str | None = None) -> str:
-    """Extracts structural signatures (classes, functions, methods) from source files using tree-sitter AST. Falls back to regex when no tree-sitter grammar is available for the language. Saves the result to a Markdown file under context-reports/ and returns the report file path. Use for a structural API outline without file bodies. Use read_source_files instead when full source content is required. project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
+def extract_signatures(
+    file_path: str, project_root: str | None = None, max_chars: int = 12000
+) -> str:
+    """Extracts structural signatures (classes, functions, methods, interfaces) with tree-sitter AST and a regex fallback. Accepts one file OR a directory (up to 200 matching files), writes a Markdown report under context-reports/, and returns the signatures inline (capped by max_chars) so the caller never has to open the report. Markdown/HTML/JSON report that no signatures exist instead of failing silently. project_root scopes resolution; max_chars caps the inline text."""
     # Master try/except: ensure extract_signatures never crashes the MCP server
     try:
         try:
@@ -653,51 +843,47 @@ def extract_signatures(file_path: str, project_root: str | None = None) -> str:
         path = Path(file_path)
         if not path.is_absolute():
             path = workspace_root / file_path
-        if not path.is_file():
-            return f"Error: File not found: {file_path}"
         try:
             path.resolve().relative_to(workspace_root)
         except ValueError:
             return f"Error: path escapes project: {file_path}"
-
-        result_content = None
-
-        # Try tree-sitter AST extraction first (wrapped — fall back to regex on any failure)
-        try:
-            ts_result = _extract_via_tree_sitter(path)
-            if ts_result:
-                result_content = ts_result
-        except Exception as ts_err:
-            # Tree-sitter failed (missing grammar, parse error, etc.) — proceed to regex
-            pass
-
-        # Fallback to regex if tree-sitter did not produce results
-        if result_content is None:
-            # Read the RESOLVED path: under the singleton the raw relative
-            # file_path resolves against the server cwd, not the project root.
-            with open(path, "r", encoding="utf-8") as f:
-                content = f.read()
-
-            # Match class, function, def, interface, type — with access modifiers
-            pattern = re.compile(
-                r"^(?:\s*(?:export|default|public|private|protected|internal|pub|static|abstract|final|override|inline|open|suspend)\s+)*"
-                r"(?:class|struct|enum|trait|impl|interface|type|def|fun|func(?:tion)?)\s+\w+.*$",
-                re.MULTILINE,
+        if not path.exists():
+            return f"Error: File not found: {file_path}"
+        if path.is_dir():
+            ignore = GitIgnoreFilter()
+            targets = sorted(
+                p
+                for p in collect_files(str(path), ignore)
+                if p.is_file() and p.suffix.lower() in _SIGNATURE_EXTS
+            )[:200]
+        else:
+            targets = [path]
+        if not targets:
+            return (
+                f"No structural signatures found in {file_path}. "
+                f"Supported extensions: {', '.join(sorted(_SIGNATURE_EXTS))}."
             )
-            matches = pattern.findall(content)
 
-            # Match const/let arrow functions
-            arrow_pattern = re.compile(
-                r"^(?:export\s+)?(?:const|let)\s+\w+\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=]*)\s*=>.*$",
-                re.MULTILINE,
+        blocks: list[str] = []
+        without_signatures = 0
+        for target in targets:
+            try:
+                label = target.resolve().relative_to(workspace_root).as_posix()
+            except ValueError:
+                continue
+            block = _signature_block(target, label)
+            if block:
+                blocks.append(block)
+            else:
+                without_signatures += 1
+        if not blocks:
+            return (
+                f"No structural signatures found in {file_path} "
+                f"({len(targets)} file(s) scanned). Supported extensions: "
+                f"{', '.join(sorted(_SIGNATURE_EXTS))}."
             )
-            arrow_matches = arrow_pattern.findall(content)
-
-            all_matches = matches + arrow_matches
-            if not all_matches:
-                return f"No structural signatures found in {file_path}."
 
-            result_content = f"### Signatures in {file_path}\n" + "\n".join(all_matches)
+        result_content = "\n\n".join(blocks)
 
         # Ensure the PROJECT's output directory exists (never the server cwd).
         report_dir = workspace_root / "context-reports"
@@ -712,10 +898,25 @@ def extract_signatures(file_path: str, project_root: str | None = None) -> str:
         with open(report_file, "w", encoding="utf-8") as f:
             f.write(result_content)
 
+        try:
+            cap = max(2000, min(int(max_chars), 60000))
+        except (TypeError, ValueError):
+            cap = 12000
+        inline = result_content
+        if len(inline) > cap:
+            inline = (
+                inline[:cap]
+                + f"\n... (inline cap {cap} chars; full text in the report)"
+            )
+        scope = (
+            f"{len(targets)} file(s), {without_signatures} without signatures"
+            if path.is_dir()
+            else "1 file"
+        )
         return (
-            f"✅ Success: Signatures extracted from `{file_path}`.\n"
+            f"✅ Success: Signatures extracted from `{file_path}` ({scope}).\n"
             f"📁 Generated Report: `{report_file}`\n\n"
-            f"Manager: You can now open `{report_file}` in your local editor to view the extracted signatures or copy/paste it directly for the AI."
+            f"{inline}"
         )
     except Exception as e:
         return f"Error extracting signatures from {file_path}: {str(e)}"
diff --git a/skill-templates/code-search/SKILL.md b/skill-templates/code-search/SKILL.md
index bc31511..1acdf52 100644
--- a/skill-templates/code-search/SKILL.md
+++ b/skill-templates/code-search/SKILL.md
@@ -7,99 +7,71 @@ description: Mandatory workflow for exploring the codebase and gathering context
 
 You are the Executor. Your job is to extract codebase context so the Manager can upload it to the Orchestrator.
 
-**CRITICAL GUARDRAIL:** You MUST NOT read, analyze, or process the generated reports yourself. You are strictly a data gatherer in this phase.
+**CRITICAL GUARDRAIL:** You MUST NOT read, analyze, or process generated report files (`context-reports/*.md`) yourself. Inline tool output — graph query results, signature text, tree output — is yours to use; the files those tools write are hand-off artifacts only.
 
 ## Discovery Workflow
 
-1. **Map the Structure:** Call the `custom_context_get_directory_tree` MCP tool on the target directory (e.g., `.`, `src/`, `packages/`).
+1. **Map the structure.** Call `custom_context_get_directory_tree` on the target (`.` for the repo). It defaults to depth 3 and 2000 entries; pass `max_depth`/`max_entries` when the area is deeper. Call `custom_context_create_tree_report` only when the Manager asks for a saved tree.
 
-1.5. **Persist the Tree (Recommended):** Call `custom_context_create_tree_report` (default `target_path="."` = whole project; pass any sub-path to scope it) to save a `.gitignore`-aware tree as `context-reports/tree_report_<timestamp>_<uuid>.md`. Use this whenever the Manager asks to "create a tree of the project".
+2. **Graph first.** For any question that names behaviour, a symbol, or "what connects to what", build once per session with `custom_context_build_graph` and then query it:
+   - `custom_context_query_graph` — natural words ("plan approval question tool", "staged diff injection").
+   - `custom_context_explain_node` — one exact symbol, file, section, or any ID the graph printed (`sym:path#name`, `sec:path#slug`).
+   - `custom_context_shortest_path` — how two concepts connect (`undirected=True` when direction is unknown).
+   - `custom_context_god_nodes` — the hubs everything flows through.
+   - `custom_context_graph_stats` — coverage and freshness before you trust a miss.
 
-1.6. **Graph-First (Recommended):** For multi-file questions call `custom_context_build_graph` once (saves versioned `graph_*.json` + `graph_report_*.md` over code, SQL, Markdown, and docs with EXTRACTED/INFERRED edges), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` over full reads. Natural words match symbols (snake_case/camelCase split). Use `custom_context_graph_stats` to confirm coverage. Fall back to signatures/reads only for exact bodies the subgraph does not answer.
+3. **Read the coverage line.** Every graph answer now prints one, e.g. `Coverage: 512/587 files, 480/521 docs; ... complete` or `truncated: docs — absence here is not proof of absence`. If it says truncated or `STALE`, rebuild (optionally `include=[...]`) before concluding a symbol does not exist.
 
-2. **Prefer Signature Extraction Over Full Reads:** Before reading a single file body, you MUST call `custom_context_extract_signatures` on every file or directory you plan to explore. This tool uses **tree-sitter AST** (not regex) to extract structural signatures — classes, functions, methods, interfaces, enums, type aliases — across all major languages. Signature extraction costs a fraction of the tokens compared to reading the full file, and is strictly preferred for initial exploration.
+4. **Verify every hit.** `explain_node` gives `source_file` + `source_location`; quote that file:line in your report. Read at most the 2–3 files the graph actually pointed at.
 
-3. **Target Files:** Use the directory tree AND the extracted signatures together to identify exactly which files contain the logic relevant to the Manager's request. The signatures give you a structural map of each file's exports without loading its body.
+5. **Extract signatures only for structural breadth.** `custom_context_extract_signatures` accepts a file **or a directory** and returns the signature text **inline** (plus a saved report path). Use it when you need the shape of a module or folder; do not read the report it writes.
 
-4. **Compile Report (Only When Necessary):** Call `custom_context_read_source_files` ONLY when you have already narrowed the exploration to specific files and need their full bodies for detailed analysis. For broad exploration, signatures alone are sufficient.
+6. **Full reads last.** `custom_context_read_source_files` compiles narrowed files into a report and returns its path. Use it only after steps 2–5 have narrowed the set.
 
-5. **Halt and Handover:** Once the `custom_context_read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
-
-6. **Output Message:** Output the following exact message to the Manager:
+7. **Halt and hand over.** Output exactly:
    > "✅ Discovery complete. I have compiled the context report here: `[INSERT_FILE_PATH]`.
    > **Manager:** Please upload this file to the Orchestrator for review."
 
----
-
-### Vertical Slicing Strategy
-
-When the Orchestrator requests context for a **specific feature module** (e.g., `packages/billing/`, `src/features/auth/`, `apps/web/app/dashboard/`), follow this strategy instead of scanning the entire repository:
-
-1. **Target the Slice:** Run `custom_context_get_directory_tree` on the specific feature directory only — not the whole repo.
-2. **Extract Signatures:** Run `custom_context_extract_signatures` on all files within that slice to map its structural surface without full body reads.
-3. **Core SOP Files (Mandatory):** Regardless of the slice, **always** append the full text of `AGENTS.md`, `DESIGN.md`, and `docs/*.md` to the final context report. This ensures the Orchestrator Brain is always grounded in the project's global rules and design system.
-4. **Dependency Trace:** If the slice imports from other local modules (e.g., shared `lib/` or `core/` packages), trace and include signatures for those dependencies too.
-5. **Compile:** Call `custom_context_read_source_files` only for the slice's key files and the mandatory Core SOP files.
-
-**Why this matters:** Full-repo scans waste tokens and dilute signal. Vertical Slicing focuses the Brain on the exact feature boundaries that matter, while the mandatory Core SOP injection guarantees structural alignment with the project's architecture.
-
----
-
-## Signature Extraction (`custom_context_extract_signatures`) — Details
-
-### Why Prefer Signatures Over Full File Reads?
-
-| Approach                           | Token Cost                          | Structural Accuracy                         | Speed                  |
-| ---------------------------------- | ----------------------------------- | ------------------------------------------- | ---------------------- |
-| `extract_signatures` (tree-sitter) | **Very low** — only signature lines | **High** — AST-parsed, no regex blind spots | Instant                |
-| `read_source_files` (full body)    | **High** — entire file bodies       | N/A (full content)                          | Slower for large files |
-
-For repositories with many files, extracting signatures first lets you decide which 2–3 files genuinely need full reading. This directly prevents context bloat in the Orchestrator session.
-
-### Languages Supported (Tree-Sitter AST)
+## Choosing the Right Tool
 
-| Language       | Signatures Detected                                                                |
-| -------------- | ---------------------------------------------------------------------------------- |
-| **Python**     | `def`, `class`                                                                     |
-| **JavaScript** | `function`, `class`, `method`, `arrow function`, `generator`                       |
-| **TypeScript** | `function`, `class`, `interface`, `type alias`, `enum`, `method`, `arrow function` |
-| **Java**       | `method`, `class`, `interface`, `enum`, `record`                                   |
-| **Kotlin**     | `fun`, `class`                                                                     |
-| **Go**         | `func`, `method`, `type struct`                                                    |
-| **Rust**       | `fn`, `struct`, `enum`, `trait`, `type alias`, `impl`                              |
+| Question | Tool |
+| --- | --- |
+| Where is X defined / what does it touch? | `explain_node` (label or printed ID) |
+| What does this behaviour live in? | `query_graph` with the domain words |
+| How do these two connect? | `shortest_path` |
+| What is the hub in this area? | `god_nodes` |
+| What is the shape of this module/folder? | `extract_signatures` (file or dir, inline) |
+| What is the folder layout? | `get_directory_tree` (depth-bounded) |
+| Exact literal / regex match | native `grep` |
+| Exact file body | `read` on the 2–3 narrowed files, or `read_source_files` for a report |
 
-For languages not listed above, the tool gracefully falls back to regex-based extraction (class/function/def/interface patterns).
+## Graph Contracts
 
-**Regex Fallback Languages:** Swift, Ruby, PHP, and C# are mapped in the extension table but do NOT have tree-sitter queries configured in the MCP server. They use regex-based extraction which is less accurate. Tree-sitter support for these languages is planned for a future release.
+- **IDs are round-trippable.** `sym:path#name`, `sec:path#slug`, `file:path` all work in `explain_node` and `shortest_path`. Bare labels still work but can be ambiguous (`main` exists in several scripts); prefer the printed ID.
+- **Build options:** `include`/`exclude` take glob lists on repo-relative paths; `max_files`, `max_docs`, `max_nodes` override the caps (600/600/12000 by default).
+- **Recency bias:** task documents are indexed lane-first (in-progress, qa, backlog, completed, archive) and newest id first, so a cap never hides the work you just did.
+- **Ranking:** symbol nodes outweigh files, files outweigh prose sections on equal overlap; an exact label match always wins.
+- **Freshness:** `graph_stats` names the first source modified after the build (`STALE: ...`). Rebuild rather than reusing a stale graph.
+- **God nodes** are qualified as `name — path (weighted degree N)` and skip generic identifiers; two same-named functions in different files are distinguishable.
 
-### What Signatures Include
+## Signature Contract
 
-- **Function/method signatures:** name, parameters (including type annotations), return type, decorators if on the same line
-- **Class definitions:** name, parent class/interface if on the same line
-- **Interface/trait definitions:** name
-- **Type aliases:** name, type expression
-- **Enum definitions:** name
-- **Record/struct definitions:** name
-- **Multi-line parameter lists:** correctly captured until the closing `)` or opening `{`
+- One file or a directory (recursive, `.gitignore`-aware, up to 200 matching files).
+- Returns the extracted text inline, capped by `max_chars` (default 12000), plus the report path.
+- Tree-sitter AST for Python, JavaScript, TypeScript, Go, Java, Rust, Kotlin; regex fallback for others.
+- Markdown, HTML and JSON have no structural signatures: the tool says so explicitly instead of returning an empty success.
+- Captures declarations and parameter lists; never bodies, comments, imports, or multi-line decorators.
 
-### What Signatures Exclude (Intentionally)
+## Vertical Slicing Strategy
 
-- **Function/class bodies** — the body is cut off at the opening `{` or `:` to minimize token usage
-- **Decorators on separate lines** — only the decorated definition line is captured
-- **Comments and docstrings** — structural intent only
-- **Imports and module-level variables** — these are not structural signatures
+When the Orchestrator asks for one feature module (e.g. `packages/billing/`, `src/features/auth/`):
 
-### Example Usage
+1. `get_directory_tree` on that directory only.
+2. `build_graph` on that directory (or `query_graph` against the repo graph with the slice words), then `explain_node` for its entry points.
+3. `extract_signatures` on the slice for the structural surface.
+4. Trace local imports into shared packages and include their signatures.
+5. Append `AGENTS.md`, `DESIGN.md`, and `docs/*.md` to the final report — mandatory core context.
 
-```json
-// Extract signatures from a single file — result is saved to context-reports/signatures_report_<timestamp>_<uuid>.md
-custom_context_extract_signatures({ "file_path": "src/services/user_service.py" })
-// Returns: "✅ Success: Signatures extracted from `src/services/user_service.py`.
-//          📁 Generated Report: `context-reports/signatures_report_20260821_104224_cc209479.md`"
+## Why This Order Matters
 
-// The generated report contains the extracted signatures, e.g.:
-// ### Signatures in src/services/user_service.py
-// class UserService:
-// def get_user_by_id(id: int) -> User:
-// def create_user(data: CreateUserDTO) -> User:
-```
+Full-repo scans waste tokens and dilute signal. The graph answers "where" from an index that already carries file:line; signatures answer "what shape" without bodies; full reads answer "what exactly" for the few files that remain. Skipping straight to reads costs the most and grounds the Orchestrator least.
diff --git a/tests/test_mcp_servers.py b/tests/test_mcp_servers.py
index 9dc20a6..1ce7530 100644
--- a/tests/test_mcp_servers.py
+++ b/tests/test_mcp_servers.py
@@ -2861,6 +2861,144 @@ def test_graph_query_explain_path_god_stats():
         assert "Nodes:" in stats and "EXTRACTED" in stats, stats
 
 
+def test_graph_indexes_recent_tasks_and_reports_coverage():
+    """Recent task docs survive the cap, and the build reports real coverage."""
+    import json
+
+    mod = _load_context_server_hardening()
+    import tempfile
+
+    with tempfile.TemporaryDirectory() as td:
+        repo = Path(td)
+        (repo / "a.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
+        for lane, task in (
+            ("archive", "0001-old-history.md"),
+            ("completed", "0355-recent-work.md"),
+        ):
+            (repo / "tasks" / lane).mkdir(parents=True, exist_ok=True)
+            (repo / "tasks" / lane / task).write_text(
+                f"# Task: {task}\n\n## Goal\n\nNotes.\n", encoding="utf-8"
+            )
+        out = mod.build_graph(".", max_docs=1, project_root=str(repo))
+        assert "Coverage:" in out, out
+        assert "truncated: docs" in out, out
+        graphs = sorted((repo / "context-reports").glob("graph_*.json"))
+        data = json.loads(graphs[-1].read_text(encoding="utf-8"))
+        meta = data["graph"]
+        assert meta["indexed"]["docs"] == 1, meta
+        assert meta["truncated"]["docs"] is True, meta
+        ids = {n["id"] for n in data["nodes"]}
+        assert "file:tasks/completed/0355-recent-work.md" in ids, ids
+        assert "file:tasks/archive/0001-old-history.md" not in ids, ids
+
+
+def test_graph_resolves_printed_ids_and_qualifies_god_nodes():
+    """The IDs the graph prints are usable, and god labels carry their file."""
+    mod = _load_context_server_hardening()
+    import tempfile
+
+    with tempfile.TemporaryDirectory() as td:
+        repo = _graph_fixture_repo(Path(td))
+        assert "✅ Success" in mod.build_graph(".", project_root=str(repo))
+        ex = mod.explain_node("sym:a.py#alpha", project_root=str(repo))
+        assert "Node: alpha" in ex, ex[:400]
+        sp = mod.shortest_path(
+            "sym:c.py#gamma", "sym:b.py#beta", undirected=True, project_root=str(repo)
+        )
+        assert "hops" in sp.lower(), sp[:400]
+        gods = mod.god_nodes(3, project_root=str(repo))
+        assert "alpha — a.py" in gods, gods
+
+
+def test_query_graph_prefers_symbols_over_sections():
+    """Equal token overlap must rank the symbol above a prose section."""
+    mod = _load_context_server_hardening()
+    import tempfile
+
+    with tempfile.TemporaryDirectory() as td:
+        repo = _graph_fixture_repo(Path(td))
+        (repo / "NOTES.md").write_text(
+            "# Alpha notes\n\nAlpha is discussed at length here.\n", encoding="utf-8"
+        )
+        assert "✅ Success" in mod.build_graph(".", project_root=str(repo))
+        q = mod.query_graph("alpha", project_root=str(repo))
+        seeds = q.split("Seeds: ", 1)[1].split("\n", 1)[0]
+        assert seeds.split(",")[0].strip() == "alpha", q[:600]
+
+
+def test_graph_cap_overrides_and_include_filter():
+    """Cap overrides are honored on every node path and include globs filter."""
+    import json
+
+    mod = _load_context_server_hardening()
+    import tempfile
+
+    with tempfile.TemporaryDirectory() as td:
+        repo = _graph_fixture_repo(Path(td))
+        out = mod.build_graph(".", max_nodes=6, project_root=str(repo))
+        assert "✅ Success" in out, out
+        graphs = sorted((repo / "context-reports").glob("graph_*.json"))
+        data = json.loads(graphs[-1].read_text(encoding="utf-8"))
+        assert len(data["nodes"]) <= 6, len(data["nodes"])
+        # include filtering keeps only the matching file plus its symbols
+        out2 = mod.build_graph(".", include=["a.py"], project_root=str(repo))
+        assert "✅ Success" in out2, out2
+        filtered_path = Path(out2.split("Graph: `", 1)[1].split("`", 1)[0])
+        filtered = json.loads(filtered_path.read_text(encoding="utf-8"))
+        sources = {
+            n.get("source_file") for n in filtered["nodes"] if n.get("source_file")
+        }
+        assert sources == {"a.py"}, sources
+
+
+def test_graph_stats_reports_stale_sources():
+    """A source touched after the build must make stats say STALE."""
+    mod = _load_context_server_hardening()
+    import os as _os
+    import tempfile
+    import time as _time
+
+    with tempfile.TemporaryDirectory() as td:
+        repo = _graph_fixture_repo(Path(td))
+        assert "✅ Success" in mod.build_graph(".", project_root=str(repo))
+        future = _time.time() + 120
+        _os.utime(repo / "a.py", (future, future))
+        stats = mod.graph_stats(project_root=str(repo))
+        assert "STALE" in stats and "a.py" in stats, stats
+
+
+def test_extract_signatures_inline_and_directory():
+    """Signatures come back inline, a directory works, and docs say why empty."""
+    mod = _load_context_server_hardening()
+    import tempfile
+
+    with tempfile.TemporaryDirectory() as td:
+        repo = Path(td)
+        (repo / "src").mkdir()
+        (repo / "src" / "one.py").write_text("def one():\n    return 1\n")
+        (repo / "src" / "two.py").write_text("class Two:\n    pass\n")
+        (repo / "NOTES.md").write_text("# Notes\n\nprose only\n")
+        out = mod.extract_signatures("src", project_root=str(repo))
+        assert "✅ Success" in out and "Generated Report:" in out, out
+        assert "def one(" in out and "class Two" in out, out
+        empty = mod.extract_signatures("NOTES.md", project_root=str(repo))
+        assert "No structural signatures" in empty, empty
+
+
+def test_directory_tree_depth_is_bounded():
+    """max_depth keeps the root tree small and announces the cut."""
+    mod = _load_context_server_hardening()
+    import tempfile
+
+    with tempfile.TemporaryDirectory() as td:
+        repo = Path(td)
+        (repo / "a" / "b").mkdir(parents=True)
+        (repo / "a" / "b" / "deep.py").write_text("x=1\n")
+        out = mod.get_directory_tree(".", project_root=str(repo), max_depth=1)
+        assert "(depth 1" in out, out
+        assert "deep.py" not in out, out
+
+
 def test_graph_tree_respects_project_root():
     """Regression: get_directory_tree with project_root lists project files (not server cwd)."""
     mod = _load_context_server_hardening()
```
<!-- END_GIT_DIFF -->
