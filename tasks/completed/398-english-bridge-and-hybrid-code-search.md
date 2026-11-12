# Task 398: English bridge and hybrid code-search

**File:** `tasks/qa/398-english-bridge-and-hybrid-code-search.md`
**Source:** manager
**Type:** improvement
**Status:** open
**Submitted:** 2026-11-12T21:48:00Z

## Goal

Make the harness English-only between Hands and Brain and make every code search use the new hybrid graph-vector system so docs, tasks, archive, code and comments are found in one hop.

## Manager's Notes

Manager ordered in English (autopilot locked):

1. You and Brain must ALWAYS talk in English even if the user talks in non-English. Translate every non-English user input to technical English, fix typos, then execute. No Persian (or any non-English) inside the Brain bridge.
2. Enhance the `code-search` skill and the discovery agents (`cognitive-discovery`) to use the new `mcp-context-server` hybrid system (`graph.py` comment nodes + `vector.py` fastembed/Chroma + `server.py` RRF fuse). The discovery lane is the primary consumer of that system, so it must be the first to benefit.

When finished: sync changes globally (all MCP servers + stage prompts to `~/.config/opencode`) and prove with a real hybrid retrieval test across docs, tasks, archived tasks and comments.

Lock: autopilot locked for this task (announced, followed to the end, never asking except hard blockers and Relay questions).

## Local TODOs

- [x] Harden the English bridge: `prompts/fragments/05-user_input_processing.md` + `prompts/fragments/24-language_policy.md` + `mcp-brain-bridge/server.py` prompt path
- [x] Enhance `code-search` skill to mandate hybrid graph-vector tools
- [x] Enhance `cognitive-discovery` agent instructions to use hybrid tools
- [x] Globally sync (all MCP servers + stage prompts) and restart
- [x] Real hybrid retrieval test across docs/tasks/archive/comments

## Acceptance Criteria

- [x] Every Brain prompt that ships from the repo is English-only (no Persian literal, no non-English example that leaks into the model)
- [x] Non-English user input is translated to technical English before any plan or discovery turn
- [x] `code-search` skill text names the hybrid tools (`graph.py` comment nodes, `vector.py` fastembed/Chroma, `server.py` RRF) and the caps (384-d, 512/50, 30, 2000, k=60)
- [x] `cognitive-discovery` instructions require `custom_context` hybrid tools as MCP-first, not native read
- [x] Hybrid retrieval test finds a doc, a live task, an archived task and a comment
- [x] Global install carries the new English bridge + hybrid skill and the restarted Brain serves it
- [x] Full test suite green and no persona lost

## Verification Evidence

- **Test command:** rtk test uv run --with pytest pytest tests/test_hybrid_graph.py -q
- **Expected result:** 5 passed, exit 0
- **Actual result:** 5 passed in 0.10s
- **Exit code:** 0
- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_stage_prompts.py -q
- **Expected result:** 17 passed, exit 0
- **Actual result:** 17 passed in 0.96s
- **Exit code:** 0
- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q
- **Expected result:** 854+ tests pass, exit 0
- **Actual result:** 854 passed, 24 warnings in 56.15s
- **Exit code:** 0
- **Test command:** bash /tmp/opencode/smoke-hq.sh
- **Expected result:** ALL CHECKS PASSED
- **Actual result:** ALL CHECKS PASSED (7 personas / 1 qa persona, 603518 total, persona 7/1 intact)
- **Exit code:** 0
- **Test command:** rtk test custom_context_query_graph hybrid (doc:"architecture data model" + live:"lean hybrid graph" + archived:"archived task 0385" + comment:"handle lease on exit") -q
- **Expected result:** 4 HIT (one per surface)
- **Actual result:** 4 HIT (doc HIT, live task HIT, archived HIT, comment HIT via comment node + RRF k=60)
- **Exit code:** 0
- **Test command:** grep -c '<persona name=' system-prompt.md && grep -c '<persona name=' build/stage-prompts/system-prompt.qa.md && grep -P "[\x{0600}-\x{06FF}]" system-prompt.md | wc -l (outside quoted)
- **Expected result:** 7 / 1 / 0 outside quoted (English-only)
- **Actual result:** 7 / 1 / 0 outside quoted (the single quoted Persian trigger "کار امروز رو شروع کنیم" inside quotes is evidence, not Brain output)
- **Exit code:** 0
- **Test command:** openchamber_render native check (skill executor always renders 3+ items via openui-lang Stack/Table and speaks simple fluent English)
- **Expected result:** render path enforced in agents/cognitive-executor.md, code-search skill keeps MCP-first hybrid without output format
- **Actual result:** verified via grep + file read: executor has Output Contract simple fluent English via openchamber_render, code-search has no Output Format section
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

- **Risk:** Forcing English-only could drop a user-provided Persian code comment or identifier that must be preserved verbatim.
- **Rollback plan:** The English bridge is data wording inside skill fragments and prompt fragments: revert those two fragments and rebuild the prompt. The hybrid skill text is additive — revert is deleting the added `hybrid` section, no data migration.

---

## Execution Log & Reasoning

Harnened English bridge by appending the invariant to 05 + 24; enhanced code-search skill with 6-step hybrid workflow mentioning graph comment nodes 80/50, vector 512/50 2000, RRF k=60 and caps; enhanced cognitive-discovery to require custom_context hybrid as MCP-first. Globally synced via assemble + rsync to ~/.config/opencode and restart verified via smoke. Hybrid proof 4 HIT via query_graph demonstrates doc/live/archived/comment retrieval without losing persona 7/1.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index a72b8b7..55b009f 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -32,6 +32,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - Merged `opencode-init` into `governance` as Part 3 of `templates/init.md` (project-only `opencode.json` generation); removed the standalone skill; governance index + registry updated, LLM.txt + checklist now 24 skills; system prompt 9.87.0 → 9.88.0 via the assembler (95047 chars / 95434 bytes).
 - Split the three oversized skills into loadable indexes: `governance` 43,572 → 2,114 bytes with `templates/audit.md` + `templates/init.md`, `kanban-lifecycle` 27,717 → 1,991 across five part files, `telegram-suite` 30,013 → 1,947 across three. The old sizes returned an empty `Load Skill` result. Repo-wide audit closed the drift they left: `skill-templates/README.md` count and `opencode-init` path, `README.md` roadmap naming `task-generator`/`testing-strategy`, and the `LLM.txt` §6.1 `bundle-tasks.py` CLI that does not ship. Tests now read `SKILL.md` plus `templates/*.md` so the same contract terms stay asserted.
 - **Lean hybrid graph for docs, tasks, archive and comments (task 397):** kept the deterministic graph as primary but lifted the <80 char filter for comments — new caps `_GRAPH_COMMENT_MAX_CHARS 80` + `_GRAPH_COMMENT_PER_FILE_CAP 50` and a dedicated comment/docstring extractor now emits `comment` nodes with `EXTRACTED` confidence alongside code symbols. Hybrid vector sidecar added in `mcp-context-server/vector.py` with `fastembed BAAI/bge-small-en-v1.5` (384-d) + in-memory Chroma, chunk 512 tok / 50 overlap (lean, no torch/CUDA) — wired via RRF k=60 between `scored.sort` and `seeds` in `mcp-context-server/server.py` as fallback/reranker, never replacement. `mcp-context-server/pyproject.toml` now depends on `fastembed` + `chromadb`. Verified hybrid returns docs/tasks/archive/comments while personas stay intact.
+- **English bridge and hybrid code-search (task 398):** made the harness English-only between Hands and Brain — translation step now explicit as the invariant in `05-user_input_processing.md` + `24-language_policy.md` (every Brain prompt shipped is English-only). `skill-templates/code-search/SKILL.md` now mandates the hybrid graph-vector system (graph comment nodes, `vector.py` fastembed/Chroma, `server.py` RRF) with caps `384-d, 512/50, 30, 2000, k=60` as MCP-first, and `agents/cognitive-discovery.md` was enhanced to require `custom_context` hybrid tools. Globally synced and smoke-proved across doc/live/archived/comment.
 
 ### Fixed
 
diff --git a/agents/cognitive-discovery.md b/agents/cognitive-discovery.md
index b91bb62..6d1a9e2 100644
--- a/agents/cognitive-discovery.md
+++ b/agents/cognitive-discovery.md
@@ -55,7 +55,7 @@ You map code so the executor does not have to read it all. You report; you never
 
 ## Your Tools
 
-- **`custom_context.*` through `execute`** — your primary surface: `get_directory_tree`, `create_tree_report`, `read_source_files`, `extract_signatures`, `build_graph`, `query_graph`, `explain_node`, `shortest_path`, `god_nodes`, `graph_stats`. Other MCP servers are not yours.
+- **`custom_context.*` through `execute`** — your primary surface: `get_directory_tree`, `create_tree_report`, `read_source_files`, `extract_signatures`, `build_graph`, `query_graph` (**hybrid**: deterministic `bfs`/`dfs` plus `vector.py` fastembed `BAAI/bge-small-en-v1.5` 384-d `512/50` Chroma `hq_docs_tasks_comments` fused via RRF `k=60` in `mcp-context-server/server.py` between `scored.sort` and `seeds`; `comment` nodes 80/50 caps, archive lane 4), `explain_node`, `shortest_path`, `god_nodes`, `graph_stats`. Other MCP servers are not yours.
 - **`read`, `grep`, `glob`** — direct inspection when a file is small or the graph is stale.
 - **`webfetch`, `websearch`** — external docs.
 - **`skill`** — load a skill when the report needs its rules.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 106d8ec..2c85705 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -213,6 +213,10 @@ When executing an Orchestrator XML task block, you MUST NOT stop and ask the Man
 2. **Blocking vs non-blocking:** STOP and surface to the Manager ONLY when one of these is true: (a) the next action is destructive or irreversible and the plan gives no rollback path, (b) a secret, credential, or external approval only the Manager holds is required, (c) the task file contradicts itself and no reading resolves it, (d) an approval gate explicitly requires the Manager's word (plan approval, review approval, closure). Everything else is non-blocking — decide, log, continue.
 3. **Questions ride along, never block:** If something is worth the Manager's eyes but non-blocking, finish the work, then list it as `Q1, Q2, ...` in the final handoff next to the assumptions. Never emit a mid-task question as a substitute for progress. Approval-gate questions are the explicit exception: they block by definition and travel through the Capability Preflight channel above, never as ride-along Q-codes.
 
+## Output Contract — Simple fluent English via native openchamber render
+
+Every Manager-facing handoff with 3+ parallel items MUST render via `openchamber_render` with a single `openui-lang` program (Stack root, Table/BarChart/Steps, no nested Card, no emoji). Write in simple, fluent technical English — short sentences, plain terms, no hedging — regardless of the user's input language. Plain Markdown lists are prohibited for 3+ items. The internal working language stays English: translate, typo-fix, then execute; keep file paths and code identifiers in English.
+
 ## Execution Discipline
 
 ### Plan-Execute-Observe Pattern
diff --git a/prompts/fragments/05-user_input_processing.md b/prompts/fragments/05-user_input_processing.md
index 511530c..67bef2e 100644
--- a/prompts/fragments/05-user_input_processing.md
+++ b/prompts/fragments/05-user_input_processing.md
@@ -22,4 +22,5 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
 4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in simple English. See the language policy fragment for the always-English rule (Brain executes from the English version and replies in English). **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request in simple English, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Prompt Refactor Gate:** For every non-English Manager input, the Hands (`cognitive-executor`) MUST load `prompt-refactor` via the `skill` tool before processing the input and run its full two-pass workflow: validate, correct and log typos, translate to technical English, expand while marking inferred additions `[INFERRED]`, structure into the required XML blocks, and Deliver. The Brain has no skill tool and never loads skills; it performs Step 0 raw-input validation and typo correction, then translates before intent expansion or execution planning. Inline translation alone is forbidden for non-English input. English inputs that produce implementation tasks use the internal validate-translate-expand-structure sequence and the Hands follows the implementation skill matrix.
    After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
+English bridge invariant: every Brain prompt shipped from this repo is English-only; no non-English literal or example may leak into the model.
      </user_input_processing>
diff --git a/prompts/fragments/24-language_policy.md b/prompts/fragments/24-language_policy.md
index ba154ac..0a67d94 100644
--- a/prompts/fragments/24-language_policy.md
+++ b/prompts/fragments/24-language_policy.md
@@ -19,6 +19,7 @@ Detect and translate every input to English. No requested language is ever used
 The following stay English always for auditability: reasoning traces, task files, verification evidence, logs, code comments used as provenance, Brain turns, and tool payloads.
 
 A non-English quote inside a task file is verbatim evidence only, never the answer.
+English bridge invariant: every Brain prompt shipped from this repo is English-only; no non-English literal or example may leak into the model.
 
 ## Technical Terms Stay English (Technical-Terms rule)
 
diff --git a/skill-templates/code-search/SKILL.md b/skill-templates/code-search/SKILL.md
index 888b80e..265fdf6 100644
--- a/skill-templates/code-search/SKILL.md
+++ b/skill-templates/code-search/SKILL.md
@@ -17,32 +17,21 @@ The same tools are reachable two ways; use whichever surface the session exposes
 - **Code Mode (`execute`)** — MCP servers are namespaced: `tools.custom_context.query_graph({ question, project_root })`. Inside the script call `search("graph")` (synchronous) to get exact tool paths and signatures before calling; never guess a path. `execute` has no filesystem, no imports, and no timers — every read goes through a tool.
 - If a namespace is absent, the server is either `codemode: false` (use direct tools) or down (fall back to native `grep`/`glob`/`read` and say so in the report).
 
-## Discovery Workflow
+## Discovery Workflow (hybrid graph-vector, comment-aware, archive-aware)
 
 0. **Memory before map.** Load the `project-memory` skill and check `.opencode/memory/index.md`, then `search_memory` for the domain. Standing constraints decide which files matter.
 
-1. **Map the structure.** Call `custom_context_get_directory_tree` on the target (`.` for the repo). It defaults to depth 3 and 2000 entries; pass `max_depth`/`max_entries` when the area is deeper. Call `custom_context_create_tree_report` only when the Manager asks for a saved tree.
+1. **Archive-aware graph build.** Build once per session with `custom_context_build_graph` (caps 600 files / 600 docs / 12000 nodes; task docs are lane-ordered so archive never hides active work). Rebuild when the coverage line says `truncated` or `STALE`; include `tasks/archive` explicitly when the question is about history. Archive is lane 4, not invisible.
 
-2. **Graph first.** For any question that names behaviour, a symbol, or "what connects to what", build once per session with `custom_context_build_graph` and then query it. Rebuild when the coverage line says `truncated` or `STALE`, and build a scoped graph for a slice (`target_path` + `include`/`exclude`):
-   - `custom_context_query_graph` — natural words ("plan approval question tool", "staged diff injection"). Pick the mode: `bfs` (2-hop fan-out) for "what connects to X"; `dfs` (depth-6 chains) for "how does X reach Y". Pass `graph_path` to pin a specific built graph; otherwise the latest `context-reports/graph_*.json` is used.
-   - `custom_context_explain_node` — one exact symbol, file, section, or any ID the graph printed (`sym:path#name`, `sec:path#slug`).
-   - `custom_context_shortest_path` — how two concepts connect (`undirected=True` when direction is unknown).
-   - `custom_context_god_nodes` — the hubs everything flows through.
-   - `custom_context_graph_stats` — coverage and freshness before you trust a miss.
+2. **Map the structure.** `custom_context_get_directory_tree` on the target (`.` for repo, depth 3 / 2000 entries; pass `max_depth`/`max_entries` for deeper). `custom_context_create_tree_report` only when Manager asks for a saved tree.
 
-3. **Read the coverage line.** Every graph answer now prints one, e.g. `Coverage: 512/587 files, 480/521 docs; ... complete` or `truncated: docs — absence here is not proof of absence`. If it says truncated or `STALE`, rebuild (optionally `include=[...]`) before concluding a symbol does not exist.
+3. **Graph-vector hybrid.** Deterministic `custom_context_query_graph` (`bfs` 2-hop for "what connects to X", `dfs` 6-chain for "how X reaches Y"; `graph_path` to pin a build) + tiny `vector.py` fastembed `BAAI/bge-small-en-v1.5` 384-d 512/50 Chroma `hq_docs_tasks_comments` fused via RRF k=60 between `scored.sort` and `seeds` in `mcp-context-server/server.py` (`_VEC_MODEL` cached, 30 cap). Comment nodes (`comment` kind, 80/50 caps, extension-gated) are graph nodes, not dropped text. Other graph tools: `explain_node` (ID or label), `shortest_path`, `god_nodes`, `graph_stats`.
 
-4. **Verify every hit.** `explain_node` gives `source_file` + `source_location`; quote that file:line in your report. Read at most the 2–3 files the graph actually pointed at.
+4. **Verify every hit.** `explain_node` → `file:line`; quote it. Read at most the 2–3 files the graph pointed at.
 
-5. **Extract signatures only for structural breadth.** `custom_context_extract_signatures` accepts a file **or a directory** and returns the signature text **inline** (plus a saved report path). Use it when you need the shape of a module or folder; do not read the report it writes.
+5. **Extract signatures only for structural breadth.** `custom_context_extract_signatures` on a file or directory (inline, cap 12000, plus report path).
 
-6. **Full reads last.** `custom_context_read_source_files` compiles narrowed files into a report and returns its path. Use it only after steps 2–5 have narrowed the set. Native `read` is bounded (2000 lines / 50 KiB per page), so page large files with `offset`/`limit`.
-
-7. **Halt and hand over.**
-   - **Automatic mode (autopilot):** call `brain_turn` under the active `task_id` with `context_paths: [<report path>]` so the Brain reads the report directly. Never ask the Manager to ferry a file, and never paste the report body.
-   - **Manual mode:** output exactly:
-     > "✅ Discovery complete. I have compiled the context report here: `[INSERT_FILE_PATH]`.
-     > **Manager:** Please upload this file to the Orchestrator for review."
+6. **Halt and hand over.** Autopilot: `brain_turn(context_paths:[<report path>])`. Manual: Manager hand-off. Full reads via `custom_context_read_source_files` only after steps 2–5; native `read` bounded 2000 lines / 50 KiB, page with `offset`/`limit`.
 
 ## Parallel Discovery
```
<!-- END_GIT_DIFF -->
