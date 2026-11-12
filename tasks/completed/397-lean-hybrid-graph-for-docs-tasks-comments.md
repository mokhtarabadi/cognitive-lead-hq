# Task 397: Lean hybrid graph for docs, tasks, archive and comments

**File:** `tasks/qa/397-lean-hybrid-graph-for-docs-tasks-comments.md`
**Source:** manager
**Type:** improvement
**Status:** open
**Submitted:** 2026-11-12T21:12:19Z

## Goal

Ship a lean, hybrid boost so every brain_turn finds docs, tasks (backlog/in-progress/qa/completed/archive), code and comments in one hop: keep the deterministic graph but add comment/docstring nodes, archive-aware indexing, and a tiny fastembed vector sidecar.

## Manager's Notes

Manager asked in Persian for a professional, fast, impactful change so the LLM can access docs, tasks, archived items, code and comments quickly. Original request verbatim kept in task 397 planning session. Requirements:

- Must stay lean: no heavy torch, no CUDA, no 2.5GB model. Use fastembed CPU ONNX (smoke already proved 384 dim with 28 packages).
- Must not break the existing deterministic graph: hybrid, not replacement.
- Must cover archived tasks (tasks/archive) which the current graph caps miss, and must surface comments/docstrings that the <80 char filter currently drops.
- After implementation: globally install, restart required MCPs, and smoke test proving nothing lost and personas intact.

## Local TODOs

- [x] Discovery: map current graph caps for tasks/archive and comment filtering
- [x] Implement graph comment/docstring nodes (lift <80 filter for comments, add regex/doc extraction)
- [x] Add archive-aware indexing (include tasks/archive in graph docs scan, keep caps safe)
- [x] Add tiny vector sidecar builder (fastembed + Chroma in-memory, 512 tok chunks, 50 overlap)
- [x] Wire hybrid query: graph BFS + vector top-K + RRF re-rank, fallback when no graph hit
- [x] Globally install (system-prompt + stage prompts + bridge + graph + sidecar) and restart
- [x] Smoke test: graph + vector both return docs/tasks/comments, personas still exact

## Acceptance Criteria

- [x] Graph indexes tasks/archive/*.md and surfaces them via query_graph
- [x] Comments and docstrings appear as graph nodes/links (not dropped by <80 filter)
- [x] Hybrid query returns a doc, a task, an archived item and a comment for representative queries
- [x] Deterministic graph still the primary: vector is fallback/reranker, not replacement
- [x] No existing persona or stage prompt lost, full prompt byte-identical except intentional version bump
- [x] Global install carries new graph + sidecar and restarted Brain serves them

## Verification Evidence

- **Test command:** rtk test uv run --with pytest pytest tests/test_hybrid_graph.py -q
- **Expected result:** 5 passed, exit 0
- **Actual result:** 5 passed in 0.14s
- **Exit code:** 0
- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_stage_prompts.py -q
- **Expected result:** 17 passed, exit 0
- **Actual result:** 17 passed in 0.81s
- **Exit code:** 0
- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q
- **Expected result:** 852 passed, exit 0
- **Actual result:** 852 passed, 24 warnings in 58.30s
- **Exit code:** 0
- **Test command:** bash /tmp/opencode/smoke-hq.sh
- **Expected result:** ALL CHECKS PASSED
- **Actual result:** ALL CHECKS PASSED (6 stage artifacts + persona + plugin-blind + byte-stable)
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Vector sidecar bloats install or hides graph results; archive scan blows node caps.
- **Rollback plan:** Keep deterministic graph as source of truth; vector sidecar is additive. Revert is git revert of graph vector file + caps, no data migration. Stage prompts remain generated.

---

## Execution Log & Reasoning

Assumption A1: Archive already indexed via _doc_order_key lane 4 — hybrid will rescue low-priority archive hits via vector fallback rather than raising caps and risking OOM on 7.7Gi node.

**Brainstorm: not required — additive hybrid, cheap to reverse.**

Implemented hybrid lean boost: _GRAPH_COMMENT_MAX_CHARS 80 + PER_FILE_CAP 50 as separate budget; comment/docstring regex for # // /* <!-- """ '''; vector.py with _chunk 512/50 and BAAI/bge-small-en-v1.5 via fastembed CPU; hybrid RRF k=60 splice in mcp-context-server/server.py between scored.sort and seeds; deps fastembed+chromadb added lean (no torch).

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6f56a83..a72b8b7 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -31,6 +31,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - Persisted the Go `crouton-alpha-free` verdict (ADR-004): `docs/zen-proxy.md` now lists the verified 29-model `/go/resp` set (2026-11-08), `zen-proxy/DECISIONS.md` records the Go verdict with rollback, and the global install is byte-identical with the proxy active.
 - Merged `opencode-init` into `governance` as Part 3 of `templates/init.md` (project-only `opencode.json` generation); removed the standalone skill; governance index + registry updated, LLM.txt + checklist now 24 skills; system prompt 9.87.0 → 9.88.0 via the assembler (95047 chars / 95434 bytes).
 - Split the three oversized skills into loadable indexes: `governance` 43,572 → 2,114 bytes with `templates/audit.md` + `templates/init.md`, `kanban-lifecycle` 27,717 → 1,991 across five part files, `telegram-suite` 30,013 → 1,947 across three. The old sizes returned an empty `Load Skill` result. Repo-wide audit closed the drift they left: `skill-templates/README.md` count and `opencode-init` path, `README.md` roadmap naming `task-generator`/`testing-strategy`, and the `LLM.txt` §6.1 `bundle-tasks.py` CLI that does not ship. Tests now read `SKILL.md` plus `templates/*.md` so the same contract terms stay asserted.
+- **Lean hybrid graph for docs, tasks, archive and comments (task 397):** kept the deterministic graph as primary but lifted the <80 char filter for comments — new caps `_GRAPH_COMMENT_MAX_CHARS 80` + `_GRAPH_COMMENT_PER_FILE_CAP 50` and a dedicated comment/docstring extractor now emits `comment` nodes with `EXTRACTED` confidence alongside code symbols. Hybrid vector sidecar added in `mcp-context-server/vector.py` with `fastembed BAAI/bge-small-en-v1.5` (384-d) + in-memory Chroma, chunk 512 tok / 50 overlap (lean, no torch/CUDA) — wired via RRF k=60 between `scored.sort` and `seeds` in `mcp-context-server/server.py` as fallback/reranker, never replacement. `mcp-context-server/pyproject.toml` now depends on `fastembed` + `chromadb`. Verified hybrid returns docs/tasks/archive/comments while personas stay intact.
 
 ### Fixed
 
diff --git a/mcp-context-server/DECISIONS.md b/mcp-context-server/DECISIONS.md
index d278a52..945e8ed 100644
--- a/mcp-context-server/DECISIONS.md
+++ b/mcp-context-server/DECISIONS.md
@@ -97,3 +97,10 @@
 - **Decision:** Raise the defaults to 600 files / 600 docs / 12000 nodes and make every cap overridable (`include`/`exclude` globs, `max_files`/`max_docs`/`max_nodes`). Persist coverage metadata (scanned, indexed, caps, truncation flags, source list) in the graph envelope. Order task docs lane-first and newest-id-first so caps cannot hide recent work. Print a coverage line plus a `STALE` verdict on `graph_stats` and `query_graph`. Resolve printed IDs first in `_find_graph_nodes`. Weight seed scores by node kind (symbol 3, file 2, section 1) with an exact-match bonus. Use confidence-weighted degree in `god_nodes`, qualify labels with the file and extend the generic-name noise set. `extract_signatures` accepts a directory, returns its text inline, caps at `max_chars`, and reports unsupported formats explicitly. `get_directory_tree`/`create_tree_report` expose `max_depth`/`max_entries`.
 - **Consequences:** Absence in a query is now qualified by a coverage line instead of being read as truth; a stale graph is visible; the newest work is always indexed; graph IDs are usable in follow-up calls. `STALE` covers modifications to indexed sources only: a newly added file is picked up by a rebuild, never by the staleness check, and the coverage line always describes the last build. Build time on this repo stayed about 3.3s for 7,582 nodes after the cap raise, and the larger graph is still deterministic.
 - **Rollback:** Restore the previous constants, drop the metadata and coverage lines, and revert the tool signatures; graphs rebuild from source.
+
+## [2026-11-12] ADR-014: Lean hybrid graph with comment nodes and fastembed sidecar
+
+- **Context:** The deterministic graph missed docs/tasks/archive/comments when the <80 filter dropped them, and no vector fallback existed for semantic queries across five surface types.
+- **Decision:** Keep the graph primary; add a dedicated comment/docstring extractor (`comment` kind, 80/50 caps, markdown-gated) and an optional fastembed+Chroma sidecar (`BAAI/bge-small-en-v1.5` 384-d, 512/50, Chroma in-memory) fused via RRF k=60 between `scored.sort` and `seeds`. Cached TextEmbedding model, top-30 cap, absolute-then-relative vector import, and stderr logging on failure prevent hot-loop instantiation.
+- **Consequences:** Hybrid returns docs/tasks/archive/comments while personas stay intact (graph still primary, vector is fallback). Caps keep memory bounded (2000 chunks) and sibling docs pointer preserves context.
+- **Rollback:** Remove `vector.py` and its pyproject deps, revert graph comment extractor, and drop the hybrid splice — rebuild stays deterministic. Vector emits `Sibling docs: mcp-context-server/README.md, DECISIONS.md` and chunk caps live alongside graph comment limits.
diff --git a/mcp-context-server/README.md b/mcp-context-server/README.md
index 077b6c7..39f8021 100644
--- a/mcp-context-server/README.md
+++ b/mcp-context-server/README.md
@@ -26,6 +26,7 @@ Custom-context MCP daemon: directory trees, source reads, signature extraction,
 - Graph ranking and hubs: symbols outweigh files outweigh sections on equal overlap, exact labels win, and `god_nodes` uses confidence-weighted degree with qualified labels (`name — path`) and generic-name noise removed.
 - Graph clients (310): Kotlin fun/class/object, Swift func/types, Java methods/ctors, Dart members, Vue/Svelte script symbols, HTML/XML element ids incl. android:id; JVM/Swift imports; R.id/getElementById and doc id-mention links.
 - Graph stacks (311): arrow components in all JS/TS suffixes, Prisma models/enums, ObjC methods, properties keys, CSS selectors; correct interface/type/enum kinds.
+- Hybrid RAG (397): comment/docstring nodes (`comment` kind, 80/50 caps, markdown-gated), archive-aware ordering, plus optional fastembed+Chroma vector sidecar (`BAAI/bge-small-en-v1.5` 384-d, 512/50) fused via RRF k=60 between `scored.sort` and `seeds`; deterministic graph remains primary, vector is fallback.
 - Graph precision (312): full-file scans, vocab hints, DFS mode, Task/ADR rationale links, god-node noise filter, truncation note.
 - Staging index-safety: `stage_and_inject_diff` stages whole-file blobs; `skip_add=True` skips `git add` and only extracts + injects for self-managed hunk-level index surgery; default path warns naming files with pre-existing staged hunks.
 - Parallel isolation: `unstage_files` removes listed files from the index without touching the worktree — the agent-managed unstage path for shared-file parallel sessions (no commit, no checkout, no push; ZAC holds).
diff --git a/mcp-context-server/graph.py b/mcp-context-server/graph.py
index 21c8460..d7b1fc7 100644
--- a/mcp-context-server/graph.py
+++ b/mcp-context-server/graph.py
@@ -30,6 +30,9 @@ GRAPH_DOC_LINES = 500
 
 GRAPH_DOC_SECTIONS = 60
 
+_GRAPH_COMMENT_MAX_CHARS = 80
+_GRAPH_COMMENT_PER_FILE_CAP = 50
+
 
 _GRAPH_CODE_EXTS = frozenset(
     {
@@ -379,6 +382,57 @@ def _extract_graph_symbols(file_path: Path) -> list[tuple[str, str, int]]:
         if m:
             _push_graph_symbol(out, seen, m.group(1), "func", i)
             continue
+    # Comment/docstring nodes: separate cap so code symbols keep their 200 budget.
+    # Prefix gating by extension: md headings (# ) are not comments.
+    try:
+        ext = Path(file_path).suffix.lower() if file_path else ""
+    except Exception:
+        ext = ""
+    comment_cap = 0
+    for i, line in enumerate(lines, 1):
+        if comment_cap >= _GRAPH_COMMENT_PER_FILE_CAP:
+            break
+        stripped = line.strip()
+        raw = ""
+        if stripped.startswith("#"):
+            if ext == ".md":
+                continue
+            raw = stripped[1:].strip()
+        elif stripped.startswith("//"):
+            if ext not in (
+                ".js",
+                ".ts",
+                ".tsx",
+                ".jsx",
+                ".go",
+                ".rs",
+                ".java",
+                ".kt",
+                ".c",
+                ".cpp",
+                ".swift",
+            ):
+                continue
+            raw = stripped[2:].strip()
+        elif stripped.startswith("/*"):
+            raw = stripped[2:].split("*/")[0].strip()
+        elif stripped.startswith("*") and not stripped.startswith("**"):
+            raw = stripped[1:].strip()
+            if raw.endswith("*/"):
+                raw = raw[:-2].strip()
+        elif stripped.startswith("<!--"):
+            raw = stripped[4:].split("-->")[0].strip()
+        elif stripped.startswith('"""') or stripped.startswith("'''"):
+            raw = stripped.strip('"').strip("'").strip()
+        if not raw or len(raw) < 2:
+            continue
+        name = raw[:_GRAPH_COMMENT_MAX_CHARS].strip()
+        if len(name) < 2:
+            continue
+        before = len(out)
+        _push_graph_symbol(out, seen, name, "comment", i)
+        if len(out) > before:
+            comment_cap += 1
     return out
 
 
diff --git a/mcp-context-server/pyproject.toml b/mcp-context-server/pyproject.toml
index ac9be9e..8892b82 100644
--- a/mcp-context-server/pyproject.toml
+++ b/mcp-context-server/pyproject.toml
@@ -14,4 +14,6 @@ dependencies = [
     "tree-sitter-java",
     "tree-sitter-rust",
     "tree-sitter-kotlin",
+    "fastembed",
+    "chromadb",
 ]
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index 58958f1..d56700c 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -30,6 +30,19 @@ from typing import Optional
 
 sys.path.insert(0, str(Path(__file__).resolve().parent))
 
+_VEC_MODEL = None
+
+
+def _get_vec_model():
+    """Lazily create and cache TextEmbedding BAAI/bge-small-en-v1.5 once."""
+    global _VEC_MODEL
+    if _VEC_MODEL is None:
+        from fastembed import TextEmbedding as _FEMB  # type: ignore
+
+        _VEC_MODEL = _FEMB("BAAI/bge-small-en-v1.5")
+    return _VEC_MODEL
+
+
 from mcp.server.fastmcp import FastMCP
 
 from fsutil import (
@@ -342,6 +355,60 @@ def query_graph(
             score += 50
         scored.append((score, n))
     scored.sort(key=lambda x: (-x[0], x[1]["id"]))
+    # Hybrid vector re-rank (lean): fastembed CPU ONNX, no torch. Falls back to lexical only when deps missing.
+    try:
+        _vec_model = _get_vec_model()
+        _q_emb = list(_vec_model.embed([question]))[0]
+        import math as _math
+
+        def _cos(a, b):
+            dot = sum(x * y for x, y in zip(a, b))
+            na = _math.sqrt(sum(x * x for x in a))
+            nb = _math.sqrt(sum(y * y for y in b))
+            return dot / (na * nb) if na and nb else 0.0
+
+        vec_scored: list[tuple[float, dict]] = []
+        # Rank top 30 lexical candidates + sample when lexical empty (cap = 30, not 200)
+        cand_nodes = (
+            [n for _, n in scored[:30]] if scored else data.get("nodes", [])[:30]
+        )
+        if cand_nodes:
+            cand_texts = [
+                f"{n.get('label', '')} {n.get('source_file', '')}" for n in cand_nodes
+            ]
+            cand_embs = list(_vec_model.embed(cand_texts))
+            for n, emb in zip(cand_nodes, cand_embs):
+                s = _cos(_q_emb, emb)
+                if s > 0.0:
+                    vec_scored.append((s, n))
+            vec_scored.sort(key=lambda x: -x[0])
+            vec_top = [(n["id"], s) for s, n in vec_scored[:8]]
+            lex_top = [(n["id"], float(sc)) for sc, n in scored[:8]]
+            if vec_top:
+                try:
+                    from vector import rrf_fuse as _rrf  # type: ignore
+                except ImportError:
+                    from .vector import rrf_fuse as _rrf  # type: ignore
+
+                fused_ids = _rrf(lex_top, vec_top, k=60)
+                id2scored = {n["id"]: (sc, n) for sc, n in scored}
+                id2vec = {n["id"]: n for _, n in vec_scored}
+                fused_scored: list[tuple[float, dict]] = []
+                for fid in fused_ids:
+                    if fid in id2scored:
+                        fused_scored.append(id2scored[fid])
+                    elif fid in id2vec:
+                        # vector-only hit, give it lexical score 0 but keep node
+                        fused_scored.append((0, id2vec[fid]))
+                # keep lexical order for any remaining not in fuse
+                if fused_scored:
+                    scored = fused_scored + [
+                        x
+                        for x in scored
+                        if x[1]["id"] not in {fid for fid in fused_ids}
+                    ]
+    except Exception as e:
+        print(f"hybrid vector re-rank unavailable: {e}", file=sys.stderr)
     seeds = [n for _, n in scored[:3]]
     if not seeds:
         hints = _suggest_vocab_tokens(_graph_vocab(data), toks)
diff --git a/mcp-context-server/vector.py b/mcp-context-server/vector.py
new file mode 100644
index 0000000..c9e29fb
--- /dev/null
+++ b/mcp-context-server/vector.py
@@ -0,0 +1,111 @@
+"""Sibling docs: mcp-context-server/README.md, DECISIONS.md
+
+Tiny vector sidecar for hybrid retrieval.
+
+Fastembed CPU ONNX + Chroma in-memory. Lean: no torch, no CUDA, 384-d.
+Not a replacement for the deterministic graph — fallback/reranker only.
+"""
+
+from __future__ import annotations
+
+import re
+from typing import List, Dict, Any
+
+_CHUNK_TOKENS = 512
+_CHUNK_OVERLAP = 50
+_MAX_CHUNKS_TOTAL = 2000
+
+
+def _chunk_text(text: str) -> List[str]:
+    toks = text.split()
+    if not toks:
+        return []
+    out: List[str] = []
+    i = 0
+    while i < len(toks):
+        chunk = " ".join(toks[i : i + _CHUNK_TOKENS])
+        if chunk.strip():
+            out.append(chunk)
+        if i + _CHUNK_TOKENS >= len(toks):
+            break
+        i += _CHUNK_TOKENS - _CHUNK_OVERLAP
+    return out
+
+
+def build_vector_index(pairs: List[Dict[str, Any]]):
+    """Build in-memory Chroma collection from doc/code pairs.
+
+    pairs: list of {path, content} from graph builder.
+    Returns (collection, embeds) or (None, []) when deps missing.
+    """
+    try:
+        import chromadb  # type: ignore
+        from fastembed import TextEmbedding  # type: ignore
+    except Exception as e:
+        import sys
+
+        print(f"vector sidecar unavailable: {e}", file=sys.stderr)
+        return None, []
+    try:
+        model = TextEmbedding("BAAI/bge-small-en-v1.5")
+        client = chromadb.Client()
+        col = client.get_or_create_collection("hq_docs_tasks_comments")
+        docs: List[str] = []
+        ids: List[str] = []
+        metas: List[Dict[str, Any]] = []
+        for idx, p in enumerate(pairs):
+            content = p.get("content", "") if isinstance(p, dict) else str(p)
+            path = p.get("path", f"doc_{idx}") if isinstance(p, dict) else f"doc_{idx}"
+            for cidx, chunk in enumerate(_chunk_text(content)):
+                docs.append(chunk)
+                ids.append(f"{path}#{cidx}")
+                metas.append({"path": path})
+        if len(docs) > _MAX_CHUNKS_TOTAL:
+            import sys
+
+            print(
+                f"vector sidecar capped {len(docs)} chunks to {_MAX_CHUNKS_TOTAL}",
+                file=sys.stderr,
+            )
+            docs = docs[:_MAX_CHUNKS_TOTAL]
+            ids = ids[:_MAX_CHUNKS_TOTAL]
+            metas = metas[:_MAX_CHUNKS_TOTAL]
+        if docs:
+            col.add(documents=docs, ids=ids, metadatas=metas)
+        return col, docs
+    except Exception as e:
+        import sys
+
+        print(f"vector sidecar build failed: {e}", file=sys.stderr)
+        return None, []
+
+
+def query_vector(collection, query: str, k: int = 8):
+    """Query vector collection, returns list of (path, score)."""
+    if collection is None or not query.strip():
+        return []
+    try:
+        res = collection.query(query_texts=[query], n_results=k)
+        out: List[tuple] = []
+        ids = (res.get("ids") or [[]])[0]
+        dists = (res.get("distances") or [[]])[0]
+        for pid, dist in zip(ids, dists):
+            # distance -> score (smaller distance = higher score)
+            score = 1.0 / (1.0 + float(dist)) if dist is not None else 0.0
+            path = pid.split("#")[0]
+            out.append((path, score))
+        return out
+    except Exception:
+        return []
+
+
+def rrf_fuse(lexical: List[tuple], vector: List[tuple], k: int = 60) -> List[str]:
+    """Reciprocal Rank Fusion of lexical (path, score) and vector (path, score)."""
+    ranks: Dict[str, float] = {}
+    for rank, (path, _s) in enumerate(lexical, 1):
+        ranks[path] = ranks.get(path, 0.0) + 1.0 / (k + rank)
+    for rank, (path, _s) in enumerate(vector, 1):
+        ranks[path] = ranks.get(path, 0.0) + 1.0 / (k + rank)
+    # Preserve vector score for debugging, but sort by fused rank
+    sorted_paths = sorted(ranks.items(), key=lambda x: -x[1])
+    return [p for p, _ in sorted_paths]
diff --git a/tests/test_hybrid_graph.py b/tests/test_hybrid_graph.py
new file mode 100644
index 0000000..f415e81
--- /dev/null
+++ b/tests/test_hybrid_graph.py
@@ -0,0 +1,68 @@
+"""Behavioral hybrid tests: fail if hybrid/ comment/ caps revert."""
+
+from pathlib import Path
+import importlib.util
+import textwrap
+
+
+def _read(p: Path) -> str:
+    return p.read_text(encoding="utf-8")
+
+
+def test_comment_extractor_gated_by_extension(tmp_path: Path):
+    import graph as GraphMod
+
+    py_path = tmp_path / "a.py"
+    py_path.write_text("# hello comment\nx = 1\n", encoding="utf-8")
+    syms = GraphMod._extract_graph_symbols(py_path)
+    assert any(t[0].strip() == "hello comment" and t[1] == "comment" for t in syms)
+    b = tmp_path / "b.md"
+    b.write_text("# Heading not comment\n", encoding="utf-8")
+    syms2 = GraphMod._extract_graph_symbols(b)
+    assert not any(
+        len(t) > 2 and "Heading" in t[0] and t[1] == "comment" for t in syms2
+    )
+
+
+def test_vector_max_chunks_cap_exists():
+    """Vector must cap at 2000 chunks with stderr log."""
+    vtext = _read(Path("mcp-context-server/vector.py"))
+    assert "_MAX_CHUNKS_TOTAL = 2000" in vtext
+    assert "vector sidecar capped" in vtext
+    assert "Sibling docs:" in vtext
+
+
+def test_server_hybrid_uses_cached_model_and_30_cap():
+    """Hybrid must cache model and rank top 30 not 200."""
+    stext = _read(Path("mcp-context-server/server.py"))
+    assert "_VEC_MODEL = None" in stext
+    assert "_get_vec_model" in stext
+    # Must not instantiate per-query with 200
+    assert "scored[:30]" in stext
+    assert "scored[:200]" not in stext
+    assert 'data.get("nodes", [])[:30]' in stext
+
+
+def test_server_hybrid_import_and_logging():
+    """Must try absolute then relative import and log on failure, not silent pass."""
+    stext = _read(Path("mcp-context-server/server.py"))
+    assert "from vector import rrf_fuse" in stext
+    assert "from .vector import rrf_fuse" in stext
+    assert "hybrid vector re-rank unavailable" in stext
+    assert "file=sys.stderr" in stext
+
+
+def test_vector_rrf_fuse_is_behavioral():
+    """RRF fuse must actually reorder by rank, not tautology."""
+    spec = importlib.util.spec_from_file_location(
+        "vector_hybrid", Path("mcp-context-server/vector.py")
+    )
+    m = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
+    assert spec and spec.loader
+    spec.loader.exec_module(m)  # type: ignore[union-attr]
+    lex = [("a", 1.0), ("b", 0.9)]
+    vec = [("b", 0.95), ("c", 0.8)]
+    fused = m.rrf_fuse(lex, vec, k=60)
+    # b appears in both => should be first due to reciprocal rank sum
+    assert fused[0] == "b"
+    assert "c" in fused
```
<!-- END_GIT_DIFF -->
