# Task 397: Lean hybrid graph for docs, tasks, archive and comments

**File:** `tasks/completed/397-lean-hybrid-graph-for-docs-tasks-comments.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-12T21:32:54Z
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
**Factual Git Diff:** Stored in Commit Hash: `246cd4080883973dcb2ad6fadd4f516ec178fc7c`
<!-- END_GIT_DIFF -->
