# Task 0378: Brain keeps saying "context ندارم" — discovery-fed grounding gap

**File:** `tasks/qa/0378-brain-discovery-fed-grounding-gap.md`
**Source:** manager
**Type:** bug
**Status:** open
**Submitted:** 2026-11-06T08:09:34Z

## Goal

End the planning-loop stall where the Brain answers a fed discovery round with a second `<missing_context>` list: make the Hands feed verbatim file bodies (via `context_paths` and/or capped verbatim ranges inside `[fed-context]`), because prose summaries alone never satisfy the Brain's No-Hallucination + Strict Grounding rules.

## Manager's Notes

Persian verbatim: "مشکل برین رو هم حل من ... چرا هی میگه کانتکس ندارم ... باگ و gap رو پیدا کن ... به خود برین بگو self improvement ... یادت میده چطوری با هم مشکل برین رو پیدا منید و تسکش کنید ... و حلش کنید"

Translation: fix the Brain problem too — why does it keep saying it has no context; find the bug and the gap; tell the Brain itself (self-improvement); learn how to find the Brain problem together, task it, and solve it.

## Root cause (verified in repo truth, case: dumble 1046)

F1 — Hands fed prose, not bodies. `agents/cognitive-executor.md` "Discovery-fed planning" says to feed results back "with the fed context marked by a `[fed-context]` block", and the file-context line says to "pull the needed code ranges and feed them into the next turn as `[fed-context]`". Neither sentence requires verbatim bodies or `context_paths`. In the 1046 loop the Hands fed citation-style prose (`- file:line claim...`, no bodies). The Brain's No-Hallucination rule (`system-prompt.md` constraint: missing critical files → STOP + `<missing_context>`) and Strict Grounding rule (claims must rest on directly-observed content; missing info → request discovery, never guess) cannot verify prose-about-code, so the second `missing_context` was the contractually correct output — the loop mechanics did not fail, the fed material did not qualify as grounding.

F2 — `context_paths` sat unused. The bridge reads real files server-side (`mcp-brain-bridge/server.py`, `context_paths` attach with per-file/total caps, `#Lstart-end` slices, truncation notes the narrowing rule understands per ADR-010). The 1046 retry turn passed no `context_paths`. The exact tool built for this starvation was never called.

F3 — bridge pin + narrowing are healthy. The `[fed-context]` pin is saved and prepended on later turns (server.py `save_fed_context` / `load_fed_context`), and the second request correctly narrowed to ranges instead of repeating whole files. No bridge code change is indicated; the gap is purely the Hands-side feeding contract.

## Local TODOs

- [x] Amend "Discovery-fed planning" in `agents/cognitive-executor.md`: a fed retry MUST carry verbatim code (capped ranges) and/or `context_paths=[paths]`; a prose-only `[fed-context]` is a protocol violation that predicts a second `missing_context`.
- [x] Mirror the one-line rule at the file-context retrieval line (same file) so both instructions agree.
- [x] Add a regression test in `tests/test_prompt_sync.py` pinning the new contract sentences (red-first, then green).
- [x] Sync the live global agent copy (same pattern as task 0352) and verify byte-identical.
- [x] Living docs: `agents/DECISIONS.md` ADR + `agents/README.md` invariant if it names the contract.
- [x] CHANGELOG entry; full HQ suite green; `lint_task_file` green.

## Acceptance Criteria

- [ ] The executor names prose-only fed-context as a violation and mandates verbatim ranges and/or `context_paths` on the retry turn.
- [ ] The regression test fails on the old text and passes on the new text.
- [ ] Live agent copy matches the repo file byte for byte.
- [ ] Full suite green and `lint_task_file` green.

## Verification Evidence (Phase 1)

- **Test command:** `uv run --project mcp-brain-bridge --with pytest python -m pytest tests/test_prompt_sync.py -q` (new test red-first, then green) + full HQ suite
- **Expected result:** new contract test fails before the doc edit, full suite green after
- **Actual result:** new test FAILED pre-edit (`AssertionError`), `test_prompt_sync.py` 24/24 post-edit; full HQ suite `784 passed` (with `--with pyyaml`; 6 memory-server tests fail without it — pre-existing env-only `ModuleNotFoundError: No module named 'yaml'`, unrelated files); live copy `diff` exits 0
- **Exit code:** 0

## Verification Evidence (Phase 2 hotfix)

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q`
- **Expected result:** 24/24 green; no added task-number refs in the four files; hand-edited hunks whitespace-clean
- **Actual result:** 24/24 green (exit 0); `grep -E '^\+[^+].*(0378|0361)'` on the four-file diff → no hits; `git diff --check --cached` exit 0; plain `git diff --check` flags only lines inside the MCP-injected `BEGIN_GIT_DIFF` block (verbatim staged-diff reproduction, MCP-owned, not hand-editable — recorded, not fixed)
- **Exit code:** 0 (tests), 0 (cached check)
- **Stack-gate skip:** `root=.`, scanned `requirements*.txt`/`pyproject.toml`/`package.json`/`go.mod`/`*.sln`, `matched=[]`, `reason=no matching stack marker for this documentation-only hotfix`

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** verbatim bodies inflate the retry prompt; mitigated by existing `context_paths` caps and `#L` slices, which the contract points at instead of whole files.
- **Rollback:** revert the executor paragraphs and the regression test; the old stall behavior returns.

## Phase 2 — full codemode reversal (Manager override, appended 2026-11-06)

Manager decision: full reversal of the 0361 policy — every MCP server goes to Code Mode (`codemode: true` default), appended to THIS task (not a new one) by explicit Manager choice. Phase 1 above is untouched and stays verified as-is.

### Phase 2 TODOs

- [x] Timestamped backup of global `~/.config/opencode/opencode.json`, then remove `"codemode": false` from the six in-house servers (explicit default `true` restored)
- [x] Validate JSON + prove resolved values (six `True`, telegram unchanged)
- [x] Update `docs/services.md` policy table, `docs/setup.md`, `README.md` block, `LLM.txt` install block, memory `workflows/codemode-policy`
- [x] CHANGELOG entry; `lint_task_file` green; back to qa

### Phase 2 Acceptance Criteria

- [ ] Global config parses as JSON; all six in-house servers resolve `codemode=True`, telegram entry untouched
- [ ] All five doc/memory surfaces name the Code-Mode-for-all policy
- [ ] `lint_task_file` passes

---

## Execution Log & Reasoning

- Seat Check: single-slice prompt-contract fix (executor prose + prompt-sync test) → Senior Programmer; the word "contract" in the body names a process contract, not an API/schema contract, so no Architect seat. Brainstorm: not required — single-discipline, fully reversible doc change.
- F1 (verified `agents/cognitive-executor.md:387-400`, `system-prompt.md:502,511`, `mcp-brain-bridge/server.py:3887-3911`): Hands fed prose summaries; Brain's grounding rules cannot verify them; second `missing_context` contractually correct. F2: `context_paths` unused on the retry (server.py `build_paths_attach` + caps + `#L` slices). F3: pin + ADR-010 narrowing healthy — no bridge code change.
- Red-first: new test failed pre-edit as designed; green post-edit (24/24). Live copy synced via `cp`, `diff -q` exits 0.

## Execution Log & Reasoning (Phase 2 hotfix — QA_REJECTED → fix)

- QA rejected Phase 2 for F1: task-number provenance in four prompt-facing policy files (repo task-number discipline). Removed the IDs from `README.md`, `docs/services.md`, `docs/setup.md`, `.opencode/memory/workflows/codemode-policy.md`; policy meaning and dates unchanged; provenance stays in CHANGELOG + task record.
- Stack-gate skip: `root=.`, scanned `requirements*.txt`/`pyproject.toml`/`package.json`/`go.mod`/`*.sln`, `matched=[]`, `reason=no matching stack marker for this documentation-only hotfix` (`python-fastapi` loaded for discipline only, no FastAPI coverage claimed).

- 0378 moved qa → in-progress for the appended scope per Manager order; Phase 1 hunks untouched.
- Config: `cp` backup `opencode.json.bak-20261106-0378` beside the live file, then 6× `"codemode": false` → `"codemode": true` (explicit, auditable). `python3 json.load` proves six `True`, telegram key absent (= default true, untouched).
- Live proof: this session's Code Mode catalog refreshed in place — `brain`, `custom_context`, `lint`, `planner`, `project_memory`, `blowsh`, `telegram` all now route via `execute` (the lint call above ran through `tools.lint.lint_task_file`).
- Quirk: `test_prompt_sync.py::test_executor_has_no_code_references` still green — the new paragraphs carry only tool names and `#L` slice syntax, no file:line citations.
- Code review fix F2: strengthened the prompt-sync regression test to assert the normative MUST clause and mirrored file-context rule, preventing non-binding wording or mirror removal from passing.
- Rollback: restore the backup over `opencode.json` + revert the doc hunks; restart the session to reload the catalog.

## Code Review Fix Checklist (F2 — APPROVED_WITH_CHANGES)

- [x] **Step 1:** Strengthened `test_executor_fed_context_requires_verbatim_or_paths` to normalize whitespace and assert the full MUST clause + mirror rule (fixed one mismatch: mirror heading is bold `**...:**` in the executor). Targeted test green.
- [x] **Step 2:** Execution-log note + CHANGELOG entry appended; `git diff --check -- tests/test_prompt_sync.py CHANGELOG.md` exit 0.
- [x] **Step 3:** Full `test_prompt_sync.py` 24/24 green; `py_compile` clean (no LSP tool in session — compile check substituted, recorded); evidence updated; lint green; diff re-injected via `stage_and_inject_diff`.

## Code Review Fix Checklist (F1 stale rationale — second review round)

- [x] **Step 1–2:** Task back to in-progress with header sync; replaced the obsolete split rationale in `docs/services.md` with the uniform-policy sentence; no other file touched.
- [x] **Step 3–4:** CHANGELOG line appended under the current `### Fixed`; fix note + evidence recorded here; stack-gate skip `root=. markers=[requirements*.txt, pyproject.toml, package.json, go.mod, *.sln] matched=[] reason=docs-only review fix`.
- [x] **Step 5–8:** Verification below; task back to qa via `qa_transition`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/workflows/codemode-policy.md b/.opencode/memory/workflows/codemode-policy.md
index aab2223..3419577 100644
--- a/.opencode/memory/workflows/codemode-policy.md
+++ b/.opencode/memory/workflows/codemode-policy.md
@@ -9,7 +9,7 @@ updated_at: '2026-10-29T06:47:37.577501+00:00'
 
 Per-server flag: `mcp.servers.<name>.codemode` (default true = tools behind `execute`).
 
-Policy in force: EVERY server runs with `codemode: false` (native tools) except `telegram`. `custom_context` (16), `project_memory` (6), `lint` (4), `brain` (1), `planner` (11), `blowsh` (5) are direct calls — ~43 small tools total, all invoked per task, so the wrapper hop costs more than the schema saves. `telegram` (147 tools) stays in Code Mode: its schemas must not enter the system prompt.
+Policy in force (2026-11-06): EVERY server runs in Code Mode (`codemode: true`, the default). `custom_context`, `project_memory`, `lint`, `brain`, `planner`, `blowsh` and `telegram` are all `execute` wrappers — no MCP tool schemas enter the system prompt. Cost accepted by explicit Manager order: one `execute` hop per call.
 
 Apply by editing `~/.config/opencode/opencode.json` after a timestamped backup, then validating with `python3 -c "import json;json.load(open(...))"`. The flag is host-level: the singleton services do not change, and an OpenCode/session restart applies it. Do NOT use this flag to hide individual tools — that is `permission` on the normalized `<server>_<tool>` name.
 
diff --git a/CHANGELOG.md b/CHANGELOG.md
index eccd6d5..cb3671c 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Service policy text now describes the uniform all-server Code Mode routing.**
+- **Prompt-sync regression test pins the binding fed-context contract:** assertions now require the mandatory verbatim-code-or-`context_paths` clause and its mirrored retrieval rule.
+- **Prompt-facing Code Mode docs omit task-number provenance:** the current policy is stated without task IDs; provenance remains in this changelog and the task record.
+- **All MCP servers to Code Mode (Task 0378 Phase 2, Manager-ordered full reversal of 0361):** the six in-house servers (`custom_context`, `project_memory`, `lint`, `brain`, `planner`, `blowsh`) are back to `codemode: true` in the global `opencode.json` (timestamped backup kept beside it; JSON re-validated; resolved values proven six `True`, telegram untouched). Every MCP call now routes through `execute` and no tool schemas enter the system prompt — the per-call hop cost is accepted by explicit Manager order. Docs updated (`docs/services.md` table, `docs/setup.md`, `README.md` block + sample, `LLM.txt` install block) and the `workflows/codemode-policy` memory shard rewritten.
+
+- **Discovery-fed retries must ground with bodies, not prose (Task 0378):** a planning loop stalled on two consecutive `missing_context` answers. The Hands had fed citation-style prose (paths with lines, no bodies) per the Discovery-fed wording; prose-about-code cannot satisfy No-Hallucination + Strict Grounding, so the second request was contractually correct. The executor now binds the retry to verbatim code (capped ranges) and/or `context_paths=[paths]` — prose-only fed-context is a protocol violation — mirrored at the file-context retrieval line. Prompt-sync regression test (red-first verified), live agent copy synced byte-identical, agents ADR + README invariant recorded.
 - **Brain `missing_context` narrowing rule + raised context-paths caps (Task 0375):** a planning loop stalled 3 turns re-requesting files the bridge had already delivered (truncated at the 60 KB/file cap with an explicit note). The contract only said STOP-and-list, giving the model no narrowing strategy. The rule now states: a truncation note means *partially present* — verify visible scope first, never re-request a fully-present file, narrow instead of repeating (smaller path, section, symbols). Caps raised `_CTX_PATHS_PER_FILE` 60k → 150k and `_CTX_PATHS_TOTAL` 200k → 400k (env overrides unchanged); `context_paths` also accepts `#Lstart-end` / `#Lstart-` slices, wired into both the tested helper and the live-turn path through shared parsers. System prompt rebuilt to `9.70.3` via the assembler (byte-identical except the two intended hunks); `test_prompt_sync` 22/22, `test_brain_bridge` 304/304 (incl. the exact-default pin test and 7 range tests). QA round made the contract explicit: the narrowing rule now names the `#Lstart-end` / `#Lstart-` slice forms so the Brain uses them, with a prompt-sync regression test pinning both forms and matching `docs/brain-bridge.md` documentation. QA round 2 classified malformed `#L` fragments on supported paths as explicit `bad range` labels (instead of resolution fall-through) with live-path (`_path_candidates`) regression coverage on both entry points. Bridge documentation distinguishes clamped bounds from empty and malformed ranges.
 - **Brain `context_paths` rejected source files (Task 0372):** `_ALLOWED_READ_SUFFIXES` predated the task-210 injection feature and allowed only docs/reports, so every `.java`/`.js`/`.tsx` came back `[unavailable: unsupported extension]` — byte-proven (29.5k of 87k attached). Suffix set extended to source-text languages; binaries still rejected; traversal/size/budget guards untouched. 294/294 brain-bridge tests green.
 - **Brain follow-ups (Task 0374):** truncation notes verified pre-existing in the allocator (no code change); ledger rows carry per-path attach outcomes (`path`/`status`/`chars`, leak-tested — no file text ever); monthly quota counter with stderr warning past the threshold (best-effort, never blocks a turn); end-to-end `.java` injection proven live (91,991 chars attached, 297/297 green).
diff --git a/LLM.txt b/LLM.txt
index b5b9821..da9bf34 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -238,35 +238,35 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
       "custom_context": {
         "type": "remote",
         "url": "http://127.0.0.1:8102/mcp",
-        "codemode": false,
+        "codemode": true,
         "disabled": false,
         "timeout": { "catalog": 15000, "execution": 15000 }
       },
       "project_memory": {
         "type": "remote",
         "url": "http://127.0.0.1:8103/mcp",
-        "codemode": false,
+        "codemode": true,
         "disabled": false,
         "timeout": { "catalog": 15000, "execution": 15000 }
       },
       "lint": {
         "type": "remote",
         "url": "http://127.0.0.1:8101/mcp",
-        "codemode": false,
+        "codemode": true,
         "disabled": false,
         "timeout": { "catalog": 15000, "execution": 15000 }
       },
       "brain": {
         "type": "remote",
         "url": "http://127.0.0.1:8105/mcp",
-        "codemode": false,
+        "codemode": true,
         "disabled": false,
         "timeout": { "catalog": 600000, "execution": 600000 }
       },
       "blowsh": {
         "type": "remote",
         "url": "http://127.0.0.1:8107/mcp",
-        "codemode": false,
+        "codemode": true,
         "disabled": false,
         "timeout": { "catalog": 120000, "execution": 120000 }
       },
@@ -279,7 +279,7 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
       "planner": {
         "type": "remote",
         "url": "http://127.0.0.1:8108/mcp",
-        "codemode": false,
+        "codemode": true,
         "disabled": false,
         "timeout": { "catalog": 15000, "execution": 30000 }
       }
diff --git a/README.md b/README.md
index 348debe..7b11625 100644
--- a/README.md
+++ b/README.md
@@ -393,7 +393,7 @@ Best if you want this codebase exploration tool available in _every_ terminal di
         "/Users/<YOUR_USER>/.config/opencode/mcp-context-server/.venv/bin/python",
         "/Users/<YOUR_USER>/.config/opencode/mcp-context-server/server.py"
       ],
-      "codemode": false,
+      "codemode": true,
       "enabled": true,
       "timeout": 15000
     }
@@ -409,7 +409,7 @@ Best if you want this codebase exploration tool available in _every_ terminal di
 
 _(Note: Replace `/Users/<YOUR_USER>` with your actual home directory path)._
 
-`codemode: false` exposes the server's tools as native calls instead of routing them through `execute`. The HQ ships this policy for every server except `telegram` (147 tools, stays in Code Mode) — including `blowsh`; see `docs/services.md`.
+`codemode: true` (the default — key absent or explicit) keeps the server's tools behind `execute` instead of exposing them as native calls. The HQ ships Code Mode for every server, including `telegram` (147 tools); see `docs/services.md`.
 
 Full HQ install covering all core MCP servers plus skills plus both agents is documented in LLM.txt sections 4 through 7 and the global-install-upgrade memory workflow not here. The steps above cover only the standalone context server for third party projects.
 
diff --git a/agents/DECISIONS.md b/agents/DECISIONS.md
index 91b15b8..93bc1be 100644
--- a/agents/DECISIONS.md
+++ b/agents/DECISIONS.md
@@ -1,5 +1,14 @@
 # Architectural Decisions: agents
 
+## Discovery-fed retries must ground with bodies, not prose
+
+Date: 2026-11-06
+Status: accepted
+Context: A planning loop stalled with two consecutive `missing_context` answers. The Hands had fed citation-style prose (file paths with lines, no bodies) per the Discovery-fed wording, but prose-about-code cannot satisfy the Brain's No-Hallucination + Strict Grounding rules, so the second request was contractually correct and the loop hit its stop signal. The bridge's `context_paths` reader (server-side bodies, caps, `#L` slices) sat unused on the retry turn.
+Decision: The executor's Discovery-fed planning section now binds the retry to verbatim code (capped ranges pasted inline) and/or `context_paths=[paths]`; a prose-only `[fed-context]` is a protocol violation that predicts its own second `missing_context`. The File context retrieval line mirrors the rule. A prompt-sync regression test fails if the sentences disappear.
+Consequences: Fed retries arrive verifiable, so planning turns ground instead of re-requesting. Retry prompts grow by the quoted ranges; the existing caps and slices bound that cost.
+Rollback: Revert the two paragraphs and the regression test; the stall behavior returns.
+
 ## Implementation Delegation Lane Beside Discovery
 
 Date: 2026-10-28
diff --git a/agents/README.md b/agents/README.md
index 11b464d..4fbae40 100644
--- a/agents/README.md
+++ b/agents/README.md
@@ -15,6 +15,7 @@ Defines the two OpenCode agent personas for the Cognitive Lead HQ: primary execu
 - Persona changes must stay in sync with `system-prompt.md` fragments and `prompts/` sources.
 - Plan approval surface: an approval question is only valid after the full plan body is visible in the same turn, and the question payload repeats it. A bare "Approve the plan?" ask is a protocol bug.
 - Brain results cross into the transcript whole: `status`, `output`, `xml_blocks` and diagnostic/`truncated` fields are never sliced, field-shaped or summarized on return. Size is managed before the call (`compact_context`, leaner prompt, `include_bundle=false`), never after.
+- Discovery-fed grounding: a retry without verbatim code or `context_paths` predicts its own second `missing_context` — prose-only fed-context is a protocol violation.
 - No runtime code here; changes are prompt-contract changes with system-wide effect.
 
 ### Free-tier bash gate
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 0c1433e..e191468 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -398,6 +398,13 @@ the session and prepends it to later turns until session end. The
 final plan must cite fed context (file paths with lines); if it cites
 none, re-prompt once with a grounding reminder, then escalate rather
 than invent.
+**Grounding rule (binding):** a prose-only `[fed-context]` is a protocol violation —
+prose-about-code never satisfies the Brain's No-Hallucination + Strict Grounding
+rules, so the retry correctly returns a second `missing_context` and the loop stalls
+by design. The fed retry MUST carry verbatim code (capped ranges, pasted inline) and/or
+pass `context_paths=[paths]` on the `brain_turn` call so the bridge reads the bodies
+server-side; use `#Lstart-end` slices for large files. A retry that carries only
+summaries predicts its own second `missing_context` — never send one.
 
 ## Manual Workflow (Active Default)
 
@@ -559,6 +566,7 @@ blocker instead of skipping it.
 ### File context retrieval
 
 The Brain has no direct file-system access — it sees only what a `brain_turn` carries. For file inspection, use your own native OpenCode tools (`read`, `grep`, `glob`) to pull the needed code ranges and feed them into the next turn as `[fed-context]`. The five-file context bundle attaches automatically.
+**Mirror of the Discovery-fed grounding rule:** paste the ranges verbatim (capped) and/or pass the same paths via `context_paths` — a prose-only `[fed-context]` is a protocol violation that predicts a second `missing_context`.
 
 ## Personas Roster (local seat resolution)
 
diff --git a/docs/services.md b/docs/services.md
index b8bcef5..c5b9df1 100644
--- a/docs/services.md
+++ b/docs/services.md
@@ -25,14 +25,13 @@ to the nearest ancestor of its working directory that holds `tasks/`.
 ### Code Mode policy (v2 `mcp.servers.<name>.codemode`)
 
 Code Mode keeps a server's tool schemas out of the system prompt, but it
-adds one `execute` hop per call. The split follows cost, not seniority:
+adds one `execute` hop per call. Code Mode applies uniformly to all seven servers:
 
 | Servers | `codemode` | Why |
 | --- | --- | --- |
-| `custom_context`, `project_memory`, `lint`, `brain`, `planner`, `blowsh` | `false` (direct tools) | ~43 small tools in total; all are called directly and their schema cost is small |
-| `telegram` (147 tools) | `true` (default) | 147 schemas would flood the system prompt |
+| all seven (`custom_context`, `project_memory`, `lint`, `brain`, `planner`, `blowsh`, `telegram`) | `true` (default) | Manager decision 2026-11-06: every server's tools route through `execute`, keeping all schemas out of the system prompt |
 
-Setting `codemode: false` puts each tool in the native tool list
+Setting `codemode: false` would put each tool in the native tool list
 (`lint_task_file`, `claim_next`, `brain_turn`, …) instead of behind
 `execute`. It is a host-level flag: the singletons do not change, and a
 session restart applies it. Per-tool hiding still belongs to
diff --git a/docs/setup.md b/docs/setup.md
index db208f6..a68897e 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -51,7 +51,7 @@ gh auth login
 
 The project uses five FastMCP Python servers, all running as supervised singletons (one process each, shared across sessions) on loopback HTTP (`MCP_TRANSPORT=streamable-http`, ports 8101–8105; telegram 8106, blowsh 8107 — see `docs/services.md`). `opencode.json` points at them via `type: "remote"` — no stdio entries remain.
 
-**Code Mode:** only `telegram` stays in Code Mode — its 147 tool schemas must not enter the system prompt. Every other server (`custom_context`, `project_memory`, `lint`, `brain`, `planner`, `blowsh`) sets `codemode: false` and is called as native tools. See `docs/services.md` for the rationale table.
+**Code Mode:** every server runs in Code Mode (default `codemode: true`) — all tool schemas stay out of the system prompt and every call routes through `execute`. Manager decision 2026-11-06. See `docs/services.md` for the rationale table.
 
 | Server                                        | Purpose                                                                       | Singleton (port)              |
 | --------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------- |
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 6574b3d..bd1c694 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -134,6 +134,30 @@ def test_executor_shows_plan_before_asking_for_approval():
     assert "sees only Relay questions" not in text
 
 
+def test_executor_fed_context_requires_verbatim_or_paths():
+    """A discovery-fed retry without bodies starves the Brain by contract.
+
+    Regression: the executor told the Hands to feed discovery back as a
+    prose `[fed-context]` block. Prose-about-code cannot satisfy the
+    Brain's No-Hallucination + Strict Grounding rules, so the retry
+    correctly returns a second `missing_context` and the loop stalls.
+    """
+    text = _read(EXECUTOR)
+    normalized_text = " ".join(text.split())
+    assert "prose-only `[fed-context]` is a protocol violation" in normalized_text
+    assert (
+        "The fed retry MUST carry verbatim code (capped ranges, pasted inline) "
+        "and/or pass `context_paths=[paths]` on the `brain_turn` call"
+    ) in normalized_text
+    assert (
+        "**Mirror of the Discovery-fed grounding rule:** paste the ranges verbatim "
+        "(capped) and/or pass the same paths via `context_paths`"
+    ) in normalized_text
+    assert (
+        "A retry that carries only summaries predicts its own second `missing_context`"
+    ) in normalized_text
+
+
 def test_shipped_prompt_is_plugin_blind():
     """The system prompt carries no plugin knowledge (separation).
```
<!-- END_GIT_DIFF -->
