# Task 0356: Night sweep — identity grounding plus Claude-centric defect sweep, single fix, deploy, smoke test

**File:** `tasks/qa/0356-night-sweep-claude-defects.md`
**Source:** manager
**Type:** bug
**Status:** in-progress
**Started:** 2026-10-27T19:05:16Z
**Estimate:** 3h
**Deadline:** 2026-10-28

## Goal

Understand the executor identity fully, find every Claude-centric instruction and system defect of the same class across skills, prompts, docs and MCP servers, fix them all in this one task, deploy globally, restart MCP singletons where needed (never OpenCode itself), and smoke test.

## Manager's Notes

Original (Persian): آره، می‌خوام اول ماهیت خودت رو درک کنی، کامل بفهمی خودت کی هستی، بعد می‌خوام نواقص این‌چنینی، نواقص این‌جوری که توی سیستم هست رو همه رو پیدا کنی، بعد خودت رو شروع کنی به حل نقص کردن. یعنی هر نقصی که دیدی، باگی دیدی، باگ‌های سیستم رو پیدا کنی، اول ماهیت رو درک کردی، باگ‌های سیستم رو پیدا کنی، مثل این، همه رو توی یک task برام fix کنی. بعد deployشون کنی همه رو، بعد smoke test بزنی. restart هم هر جا که نیاز بود، غیر از open code، open code رو restart نکن، بقیه MCP و سرورها رو هر جا نیاز بود restart کن. برو حالت شب، حالت خودکار، autopilot mode. کامل هر کاری که باید انجام بدی انجام بده.

English translation: First fully understand your own nature/identity, then find all deficiencies of this kind in the system, then start fixing them yourself. Fix every defect and system bug you see, all in one task. Then deploy them all, then smoke test. Restart wherever needed except OpenCode itself; restart other MCPs and servers where needed. Go night mode, automatic mode, autopilot mode. Do everything that must be done, completely.

## Local TODOs

- [x] Ground identity (executor, night mode, memory, Code Mode surfaces)
- [x] Parallel defect sweep (skills, prompts/fragments, docs, MCP servers)
- [x] Brain plan under same task_id with Seat Check
- [x] Implement all fixes from the plan
- [ ] Deploy globally (servers, skills, agents, prompt) and restart singletons except OpenCode
- [ ] Smoke test and record evidence
- [x] Verify functionality

## Acceptance Criteria

- [x] Executor identity is grounded in file:line citations (agent file, night mode, memory, Code Mode docs)
- [x] Every Claude-centric reference (Claude, claude.ai, Anthropic, create_file, str_replace, artifacts) in operating instructions is remapped to OpenCode-native tools or removed
- [x] No new task numbers are created for this sweep; all fixes land in this task file
- [x] Global install matches repo for every touched file (cmp-verified)
- [x] MCP singletons that serve changed code are restarted; OpenCode itself is never restarted
- [x] Smoke test proves the fixed surfaces live

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/ -q
- **Expected result:** full HQ suite green including new regression tests
- **Actual result:** `747 passed, 24 warnings` (42/42 prompt-sync plus skill-registry; two new regression tests green, teeth proven against prior text via git-show)
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a separate closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** broad sweep could touch many files; mitigated by one defect class only (Claude-centric instructions) plus generated-artifact rebuilds, all reversible via git.
- **Rollback plan:** revert this task's commits; restart singletons to restore prior builds.

---

## Execution Log & Reasoning

**Mode.** Autopilot LOCKED plus night mode (Manager order 2026-10-27, Persian): "fix everything in one task, deploy, smoke test, restart where needed except OpenCode, night mode, autopilot". No `question` tool this run; the Hands plays plan approval, QA, review and closure per `prompts/fragments/23-night_mode.md`. WIP = 1.

**D1 (plan self-approval):** accepted the Brain's 0356 plan verbatim — single defect class, docs-plus-comments scope, prompt rebuild with version bump, global sync, regression guards. Reason: the plan matches the four discovery reports line for line and adds no scope. No separate approval pause exists in night mode.

**Identity grounding.** Hands = `agents/cognitive-executor.md` (primary engine, ZAC, MCP-first, Kanban gatekeeper, permission `edit`/`question`/`bash` with git-write denies). Subagent = `agents/cognitive-discovery.md` (read-only). Night contract = `prompts/fragments/23-night_mode.md` (do-not-ask rule, pre-authorized plan/QA/review/closure, no OpenCode restart, no production deploys). Memory index read (36 shards; approval-gates, mode-line, global-install-upgrade workflows applied). Absent files skipped per policy: `docs/architecture.md`, `docs/data_model.md` do not exist. `DESIGN.md` and `docs/conventions.md` read. Code Mode surfaces verified live against upstream `dev`: confined JS interpreter, `execute` + synchronous `search()`, MCP servers namespaced by default (`codemode: true`), `default.question`/`default.skill` session tools with no `tools.*` Code Mode path.

**Seat Check.** Domains: SOP wording remediation + prompt contracts + docs + one server comment. Requested: Software Architect (contract wording) + Senior Programmer (edits). Skipped: Designer (no user-visible surface), Planner/Strategist (single task), QA/Reviewer (later stages). Trigger map on TITLE+BODY: explicit miss on all three sets. Brainstorm: not required — single defect class, reversible. One 2-seat planning turn; plan arrived as REPORT with five fields.

**Discovery (4 parallel read-only subagents).** F1: `skill-templates/doc-coauthoring/SKILL.md` is the sole Claude-centric skill (22 Claude hits, `create_file`/`str_replace`/Artifacts/connectors/`claude.ai`); 31 other skills clean; generic Maven/report `artifact` usage elsewhere left alone. F2: zero Claude hits in `prompts/`+`agents/`; four phantom names (`nodejs-express`, `@explore`/`@general`, `view_file`/`apply_patch`) plus wrong `task`-tool noun in the executor. F3: `docs/telegram-setup.md` (4 lines) + `docs/brain-bridge.md:79` vendor-first; history frozen, untouched. F4: one code comment (`mcp-brain-bridge/server.py:2489`) + one non-catalog docstring example (`["question"]`); all other cross-refs verified in-catalog via live `search()`.

**Implementation.** Rewrote `doc-coauthoring/SKILL.md` end to end (three stages intact; `write` creates, `edit` changes, `subagent` tests, integrations via MCP/paste). Fixed `09-hands_protocols.md` (`node-hexagonal-api`, `cognitive-discovery`, native `read`/`edit`/`write`) and `13-constraints.md` (parallel `cognitive-discovery` subagents). Fixed executor delegation noun (`subagent` tool). Reworded the four doc lines (OpenCode-first, interop kept). Reworded the server comment and the docstring example (`default.question`). Bumped `01-system_version.md` 9.67.0 → 9.68.0 and rebuilt `system-prompt.md` via the assembler (109,826 bytes, phantom-free). Appended ADRs to all five sibling DECISIONS files. CHANGELOG entry under [Unreleased].

**Verification shape.** Two regression tests written (shipped-prompt catalog names; doc-coauthoring runtime neutrality); teeth proven by asserting the prior text (via `git show HEAD:`) contains every banned term. Prompt-sync + registry: 42 passed. Full suite: `747 passed`, exit 0.

**Deployment.** Global copies synced with `cp` and verified with `cmp` (all IDENTICAL): `skills/doc-coauthoring/SKILL.md`, `agents/cognitive-executor.md`, `system-prompt.md` (9.68.0), `mcp-brain-bridge/server.py`. Docs, fragments, DECISIONS, tests and CHANGELOG are repo-only with no global counterpart. `systemctl --user restart mcp-brain` executed (only singleton serving changed code); all six singletons `active` afterwards; OpenCode never restarted per the night-mode ban.

**Smoke test (live, post-restart).** Lean `brain_turn` (no bundle) returned `BRAIN_SMOKE_OK` with the full result envelope intact. Global `system-prompt.md` + executor grep: zero phantom names. Global `doc-coauthoring` grep: zero Claude-centric terms. Global brain server line 3352 carries `default.question`. Port 8105 answers; all singletons active.

**Assumption A1.** `Estimate: 3h`, deadline 2026-10-28, chosen by the Hands; the Manager gave no size.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e52b84c..8a81ac7 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Runtime-neutral sweep: Claude-centric wording and phantom tool names removed (Task 0356):** a four-way read-only sweep found one skill (`doc-coauthoring`, 22 Claude hits plus `create_file`/`str_replace`/Artifacts/connectors/`claude.ai` reader testing), four phantom tool names in prompt fragments (`nodejs-express`, `@explore`/`@general`, `view_file`/`apply_patch`), one wrong delegation noun in the executor (`task` tool), four vendor-first lines in setup docs, and one vendor-trio comment plus a non-catalog `["question"]` docstring example in the Brain Bridge. All remapped to OpenCode-native tools (`write`/`edit`, `subagent`/`cognitive-discovery`, `node-hexagonal-api`, native `read`, `default.question`); the shipped prompt was rebuilt (`9.67.0` → `9.68.0`) and verified phantom-free. Two new regression tests (shipped-prompt catalog names, doc-coauthoring runtime neutrality) prove teeth against the prior text. 31 other skills verified clean; history archives untouched; generic Maven/report `artifact` usage untouched.
+
 - **Graph coverage honesty, round-trippable IDs and inline signatures (Task 0355):** a smoke test found the lite graph indexing 345 of 587 files silently, and the missing set included the newest task files because docs were ordered `(depth, path)` and cut at 300. The graph now orders task docs lane-first and newest-id-first, defaults to 600 files / 600 docs / 12000 nodes, accepts `include`/`exclude` globs plus `max_files`/`max_docs`/`max_nodes` overrides, and stores coverage metadata (scanned, indexed, caps, truncation flags, indexed source list) in the graph envelope. `graph_stats` and `query_graph` print a coverage line, including `truncated: …` ("absence here is not proof of absence") and a `STALE` verdict naming the first source modified after the build. `explain_node` and `shortest_path` resolve the `sym:path#name`, `sec:path#slug` and `file:path` IDs the graph prints. Seed ranking weights symbols above files above sections with an exact-label bonus; `god_nodes` uses confidence-weighted degree, qualifies each label with its file and drops generic identifiers. `extract_signatures` accepts a directory (`.gitignore`-aware, 200-file cap), returns the signature text inline alongside the report path (capped by `max_chars`), and reports Markdown/HTML as unsupported instead of an empty success. `get_directory_tree` and `create_tree_report` expose `max_depth` (default 3) and `max_entries`. The `code-search` skill (repo template plus global copy) is rewritten around the graph-first flow with a tool-choice table and the real tool contracts. On this repo the rebuild indexes 49/49 code files and 522/522 docs in 3.3s (7,582 nodes, 11,720 edges); seven new tests cover recency, coverage reporting, ID round-trip, ranking, staleness, inline/directory signatures and the depth bound.
 
 - Task time is now measured, not estimated. `claim_next` stamps `**Started:**`, `qa_transition` stamps `**Submitted:**` and `commit_and_clean_task` stamps `**Finished:**` as ISO-8601 UTC, each write-once so a re-claim never rewrites the original start. `_task_brief` derives `elapsed_seconds` and `qa_wait_seconds` (`null`, never `0`, when a stamp is missing), the task modal shows `measured 2h 14m`, and `sprint_stats` adds a separate `Completed measured` line beside the estimate. `_check_planner_metadata` rejects a non-UTC stamp or a finish earlier than its start, and flags a duplicated stamp the same way it flags a duplicated key. 19 new tests; full suite 734 green.
diff --git a/agents/DECISIONS.md b/agents/DECISIONS.md
index 66ebac4..6c7b9c2 100644
--- a/agents/DECISIONS.md
+++ b/agents/DECISIONS.md
@@ -54,6 +54,14 @@ Rollback: Restore the citations from git history.
 
 ## Free-tier bash gate documented
 
+## Subagent Delegation Names the Session Tool
+
+Date: 2026-10-27
+Status: accepted
+Context: The executor told the Hands to delegate discovery "using your `task` tool". No tool by that name exists in the session; delegation runs through the `subagent` tool. The sentence was inherited from another runtime's vocabulary.
+Decision: Name the `subagent` tool explicitly. One-word-class fix; delegation targets and the 4-agent cap are unchanged.
+Consequences: The delegation instruction resolves to a real tool. No behavior change beyond the name.
+Rollback: Restore the prior sentence from git history.
 Date: 2026-10-17
 Status: accepted
 Context: Upstream free-tier models discriminate by request-body tool list. Agents omitting bash receive 403 FreeTierError on free-tier models.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 6a17cda..410688b 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -126,7 +126,7 @@ Before approval-sensitive work (plan approval, review approval, closure), check
 
 ## Subagent Delegation for Context Discovery
 
-To preserve your primary context window for implementation logic, you MUST delegate heavy context-gathering tasks to the `cognitive-discovery` subagent using your `task` tool:
+To preserve your primary context window for implementation logic, you MUST delegate heavy context-gathering tasks to the `cognitive-discovery` subagent using your `subagent` tool:
 
 1. **Discovery Tasks (`<hands_discovery_task>`):** You MUST invoke the `cognitive-discovery` subagent. Pass the target directories and file lists to the subagent. Do not read the files yourself.
 2. **Combined Tasks (`<hands_combined_task>`):** For the `<discovery_phase>`, delegate to `cognitive-discovery`. Wait for its context report before proceeding to the `<conditional_implementation_phase>`.
diff --git a/docs/DECISIONS.md b/docs/DECISIONS.md
index dfe1b84..4e0c78e 100644
--- a/docs/DECISIONS.md
+++ b/docs/DECISIONS.md
@@ -13,3 +13,10 @@
 - **Decision:** The contract is stored verbatim as `docs/telegram-message-formatting.md` (server-side facts plus a binding authoring-rules table). The agent-facing rulebook is a skill, `skill-templates/telegram-message-format/SKILL.md`, so the Hands can load it on demand; the doc stays the reference the skill points at.
 - **Consequences:** Every Telegram send from a skill or a direct MCP call must load the skill and obey the 9 authoring rules. The two Telegram skills and the Hands skill matrix now name it explicitly.
 - **Rollback:** Delete the skill and the doc, and remove the registry line, the skill-matrix row, and the skill references from the two Telegram skills.
+
+## [2026-10-27] ADR-003: Setup Docs Stay Runtime-Neutral
+
+- **Context:** `docs/telegram-setup.md` labeled callback mode "for Claude Code", listed only external MCP clients, and gave a `claude mcp add` command; `docs/brain-bridge.md` presented one vendor trio as the industry pattern. Operating docs must describe this platform first.
+- **Decision:** Callback mode is labeled for agentic clients; client lists name OpenCode first with others as compatible examples; the vendor trio became "OpenCode and other agentic clients".
+- **Consequences:** Setup docs no longer route the reader to another runtime. External-client interop facts are kept, not deleted.
+- **Rollback:** Restore the prior wording from git history.
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index bc891fa..ce5d05a 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -76,7 +76,7 @@ disk. Only the load VIEW is compacted in memory — one deterministic
 digest record plus the newest records — so a task keeps its full
 history while the send path stays bounded. The earlier lossy rewrite
 (which replaced the file with the digest) was removed. This matches
-the industry pattern: OpenCode, Claude Code, and Codex all persist the
+the industry pattern: OpenCode and other agentic clients all persist the
 full transcript and compact only what they send; OpenCode keeps full
 session history in SQLite.
 
diff --git a/docs/telegram-setup.md b/docs/telegram-setup.md
index 8220fd1..4e9edfc 100644
--- a/docs/telegram-setup.md
+++ b/docs/telegram-setup.md
@@ -13,7 +13,7 @@
 | **Media** | `send_file`, `download_media`, `send_voice`, `send_sticker` | File-path security via allowed roots |
 | **Profile/Privacy** | `get_me`, `update_profile`, `set_profile_photo`, `get_user_info` | |
 | **Folders/Drafts** | `list_folders`, `create_folder`, `save_draft` | |
-| **Events** | `wait_for_new_message`, `wait_for_settled_message`, `enable_incoming_feed`, `incoming_feed_status` | Callback mode for Claude Code |
+| **Events** | `wait_for_new_message`, `wait_for_settled_message`, `enable_incoming_feed`, `incoming_feed_status` | Callback mode for agentic clients |
 
 All Telegram-controlled strings are sanitized (`sanitize_user_content`) and returned as structured JSON.
 
@@ -23,7 +23,7 @@ All Telegram-controlled strings are sanitized (`sanitize_user_content`) and retu
 
 1. Python 3.10+ and `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
 2. Telegram API credentials from https://my.telegram.org/apps → `API_ID` + `API_HASH`
-3. MCP client (OpenCode, Claude Desktop, Cursor)
+3. MCP client (OpenCode, or any MCP-compatible client such as Claude Desktop or Cursor)
 4. Optional: `python-socks` for proxy (`uv sync --extra proxy`)
 
 ## 3. Generate a Session String (per account)
@@ -167,7 +167,7 @@ $HOME/.config/opencode/mcp-telegram-server/.venv/bin/python $HOME/.config/openco
 
 Replace `$HOME` with your actual absolute home path (e.g., `/home/<user>` or `/Users/<user>`, see `LLM.txt` Step 3). Restart OpenCode after saving (`opencode.json` loaded once at startup).
 
-### 5.2 Claude Desktop / Cursor
+### 5.2 Other MCP clients (Claude Desktop / Cursor)
 
 ```json
 {
@@ -190,7 +190,8 @@ Replace `$HOME` with your actual absolute home path (e.g., `/home/<user>` or `/U
 ```bash
 MCP_TRANSPORT=http MCP_HOST=0.0.0.0 uv run main.py  # inside container/Docker
 # publish only locally: docker run -p 127.0.0.1:8765:8765
-claude mcp add --transport http telegram http://127.0.0.1:8765/mcp
+# any MCP-compatible CLI can register the shared endpoint, e.g.:
+# <client> mcp add --transport http telegram http://127.0.0.1:8765/mcp
 codex mcp add telegram --url http://127.0.0.1:8765/mcp
 ```
 
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 7f4dde6..2cce99f 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -57,3 +57,10 @@
 - **Decision:** `_OVERALL_DEADLINE_S` becomes `BRAIN_OVERALL_DEADLINE_S` (default 900s, fail-loud on malformed), and the proxy hop becomes `ZEN_PROXY_UPSTREAM_TIMEOUT` (default 900s). Ordering contract: httpx read ≤ bridge overall ≤ MCP client execution, with the proxy at or below the bridge overall so its disconnects surface as retryable rather than as a deadline.
 - **Consequences:** Long reasoning turns complete; a truly hung provider now surfaces later (bounded by the client timeout). The existing test that forced the deadline was updated to patch the new default constant.
 - **Rollback:** Unset both env vars to restore code defaults, or set them to 500/300 explicitly for the old behavior.
+
+## [2026-10-27] ADR-009: Server Prose Stays Runtime-Neutral
+
+- **Context:** A code comment named a vendor trio as the transcript-persistence pattern, and the `brain_turn` docstring used `["question"]` as its `required_tools` example although no `tools.question` Code Mode path exists.
+- **Decision:** The comment names OpenCode and other agentic clients; the example names `default.question`, the session tool that actually gates the turn.
+- **Consequences:** Server prose no longer teaches tool names the catalog cannot resolve. Comment-only change; no wire behavior touched.
+- **Rollback:** Restore the two lines from git history.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 796899d..f54f9b8 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -2486,7 +2486,7 @@ _LINE_CAP_CHARS = 200_000
 #:
 #: This bounds ONLY what is sent to the model. The transcript file is
 #: append-only and keeps every turn forever: the industry pattern
-#: (OpenCode, Claude Code, Codex) is to persist the full transcript and
+#: (OpenCode and other agentic clients) is to persist the full transcript and
 #: compact the sent context, never to discard stored history.
 _COMPACT_AFTER_MESSAGES = 30
 _COMPACT_KEEP_LAST = 10
@@ -3349,7 +3349,7 @@ def brain_turn(
             ``<project_root>/tasks/`` (e.g. "tasks/qa/257-x.md").
             Paths escaping the tasks/ lanes are rejected.
         required_tools: Optional list of tool names the turn's stage
-            requires (e.g. ["question"]). Missing-required tools gate
+            requires (e.g. ["default.question"]). Missing-required tools gate
             the turn before transport (see capability).
 
     Returns:
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 7ee41e8..255e22f 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.67.0</system_version>
\ No newline at end of file
+<system_version>9.68.0</system_version>
\ No newline at end of file
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index 209dd78..9594c96 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -7,8 +7,8 @@
 
   <context_phase>
     HANDS INSTRUCTION: You are in DISCOVERY mode. Your goal is to gather context for the Orchestrator.
-    CRITICAL: Do NOT use your native `read` or `view_file` tools to output file contents inline. You must use the `custom_context` MCP server tools.
-    SKILL LOADING: Load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi). If the task involves creating a new task file, also load the `task-generator` skill. Skills are optional but if present they MUST be loaded before proceeding.
+    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools.
+    SKILL LOADING: Load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, node-hexagonal-api, python-fastapi). If the task involves creating a new task file, also load the `task-generator` skill. Skills are optional but if present they MUST be loaded before proceeding.
 </context_phase>
 
   <execution_phase>
@@ -41,7 +41,7 @@
 <!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->
 
   <context_phase>
-    HANDS INSTRUCTION: Read the active task file in `tasks/`. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to your subagents: use a read-only codebase-mapping subagent (e.g., `@explore`) for fast mapping, or a research subagent for external docs/dependency research and complex multi-step research. Utilize any configured MCP servers if external context is required.
+    HANDS INSTRUCTION: Read the active task file in `tasks/`. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to your subagents: use the read-only `cognitive-discovery` subagent for fast mapping, or a research subagent for external docs/dependency research and complex multi-step research. Utilize any configured MCP servers if external context is required.
     **MANDATORY SKILL ORCHESTRATION:** Load the following skills:
     1. [Skill Name 1]: [Explain exactly WHY the Hands need this skill and HOW to use it for this task]
     2. [Skill Name 2]: [Explain exactly WHY and HOW...]
@@ -65,7 +65,7 @@
 
      CRITICAL TOOL RULES:
      0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
-     1. If applying file patches, utilize your native file-editing tools (e.g., `apply_patch`). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
+     1. If applying file patches, utilize your native file-editing tools (`edit` for replacements, `write` for new files). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
      2. If user feedback is required, first check the session capability manifest for your question/clarification tool. If the tool is AVAILABLE, utilize it with multi-option schemas. If it is UNAVAILABLE, do NOT silently skip the question: relay it to the Manager as one narrow question with the options inline, then wait for the answer (manual mode) or record the replay-or-halt decision in the task file (autopilot mode).
      3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.
      4. **Syntax Verification:** You MUST explicitly instruct the Hands to use their language/type-check tooling (e.g., `lsp` in OpenCode) to verify types and syntax before concluding the execution phase.
@@ -130,7 +130,7 @@
     1.6. GRAPH-FIRST: Run `custom_context_build_graph` once on the target scope (saves versioned `graph_*.json` + `graph_report_*.md`), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` for cross-file questions before falling back to full reads.
     2. Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
     3. Compile the results into a single context report using the MCP tools.
-    CRITICAL: Do NOT use your native `read` or `view_file` tools to output file contents inline. You must use the `custom_context` MCP server tools.
+    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools.
 </discovery_phase>
 
   <conditional_implementation_phase>
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index 8b26d7a..9269c53 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -20,7 +20,7 @@
 - **Conventional Commits Format Gate:** Every feature commit message passed to `custom_context_commit_and_clean_task` MUST match `<type>: <subject>` with type in `feat|fix|docs|refactor|chore` and first line ≤72 characters (per `skill-templates/versioning-and-release`). The tool validates and rejects free-form messages. The templated `chore: close task N` closure commit always conforms by construction.
 - **Supervised Autopilot Contract:** On the lock words the Hands run end to end: discovery feed, Brain plan, one approval pause for the plan, seat-routed implementation, QA and review loops, results shown before the move to qa. Besides that single plan-approval pause, only Relay questions and hard blockers interrupt. Risk tiers live in `docs/conventions.md` (T0 trivial, T1 standard, T2 destructive needs per-action approval). Plan, QA, and review loops allow three tries max, then escalate. Authority for the full rule text is `agents/cognitive-executor.md`.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
-- **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent subagents, e.g., `@explore` or `@general`) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
+- **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent `cognitive-discovery` subagents) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. Keep AI tells out of the prose: no hedging openers ("it is worth noting", "it is important to note"), no inflated significance ("stands as a testament", "underscores the importance"), no negative parallelism ("not just X, but Y"), no rote rule-of-three lists, no collaborative preambles ("Great question", "Let me unpack this"), and no trailing recap that repeats what you already said. Banned phrases (never emit them): "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
 - **Reference Point System:** When presenting three or more findings, options, decisions, or questions to the Manager, you MUST assign a short code to each item (e.g., F1, F2 for Findings; O1, O2 for Options; D1 for Decisions; Q1 for Questions). This anchors complex discussions and makes them highly traceable.
 - **Manager-Facing Output Style (positive contract):** This governs the final externally visible reply to the Manager. `<reasoning_log>`, chain-of-thought, XML task generation, blueprints, and Hands Execution Logs stay unrestricted and rich — conciseness rules NEVER apply to those channels.
diff --git a/prompts/fragments/DECISIONS.md b/prompts/fragments/DECISIONS.md
index 36f8015..143f89c 100644
--- a/prompts/fragments/DECISIONS.md
+++ b/prompts/fragments/DECISIONS.md
@@ -28,3 +28,10 @@
 - **Consequences:** The assembled prompt shrinks and carries zero tool names; the lane tests assert absence in the prompt and presence in the executor.
 - **Rollback:** Restore the archived fragment to the manifest and tag list, revert the persona and protocol wording, and re-run the assembler.
 
+## [2026-10-27] ADR-005: Prompt Names Only Tools That Exist
+
+- **Context:** Fragments named a `nodejs-express` skill that was never created, `@explore`/`@general` subagents that exist in no roster, and `view_file`/`apply_patch` native tools outside the session toolset. The Hands cannot call what does not exist.
+- **Decision:** Name `node-hexagonal-api`, the `cognitive-discovery` subagent, and the native `read`/`edit`/`write` tools. A prompt-sync test fails on any reintroduced phantom name.
+- **Consequences:** Every tool the shipped prompt names resolves in the session. Version bumped with artifact regen.
+- **Rollback:** Revert the fragment wording and re-run the assembler.
+
diff --git a/skill-templates/DECISIONS.md b/skill-templates/DECISIONS.md
index 70d5ca3..f43cd27 100644
--- a/skill-templates/DECISIONS.md
+++ b/skill-templates/DECISIONS.md
@@ -8,8 +8,14 @@
 - **Rollback:** N/A (baseline adoption).
 
 ## [2026-10-21] ADR-002: Telegram Message Formatting Is a Skill, Not an Inline Rule
-
 - **Context:** The Telegram MCP server does not behave like the Bot API — `parse_mode: "Markdown"` strips code fences without creating entities, `*bold*` stays literal, payloads over 4096 characters fail with an opaque `GEN-ERR-184`, U+200C ZWNJ is dropped on the read path, and `send_message` has no `topic_id` so it lands in General. Without a shared rule, each Telegram skill re-derives (or ignores) the behavior and messages render broken.
 - **Decision:** Add a dedicated `telegram-message-format` skill holding the nine binding authoring rules, the message templates, and the pre-send checklist. The two Telegram skills load it in their mandatory-skill phase; the HQ evidence document `docs/telegram-message-formatting.md` stays the reference the skill points at.
 - **Consequences:** One place owns Telegram render correctness; the skill is discoverable through the agent skills registry and loadable on demand by any agent that sends a Telegram message. The template stays project-agnostic — no HQ paths, task numbers, or chat ids inside it.
 - **Rollback:** Delete `skill-templates/telegram-message-format/`, remove the registry line, the skill-matrix row, and the skill references from the two Telegram skills.
+
+## [2026-10-27] ADR-003: doc-coauthoring Goes Runtime-Neutral
+
+- **Context:** The skill was written for another agent runtime: it named `Claude` in 22 places, `create_file`/`str_replace` for edits, Claude Artifacts for drafting, Claude-settings connectors for integrations, and `claude.ai` for reader testing. None of those exist in OpenCode sessions, so every instruction misfired.
+- **Decision:** Remap to native tools: `write` creates the draft, `edit` makes every change, the `subagent` tool runs reader testing with a same-session fallback, and integrations resolve to MCP servers or pasted content. The three-stage workflow is unchanged.
+- **Consequences:** The skill now executes in OpenCode without translation. A registry test fails on any reintroduced Claude-centric term.
+- **Rollback:** Restore the prior SKILL.md from git history.
diff --git a/skill-templates/doc-coauthoring/SKILL.md b/skill-templates/doc-coauthoring/SKILL.md
index e73315e..86c5461 100644
--- a/skill-templates/doc-coauthoring/SKILL.md
+++ b/skill-templates/doc-coauthoring/SKILL.md
@@ -18,17 +18,17 @@ This skill provides a structured workflow for guiding users through collaborativ
 **Initial offer:**
 Offer the user a structured workflow for co-authoring the document. Explain the three stages:
 
-1. **Context Gathering**: User provides all relevant context while Claude asks clarifying questions
+1. **Context Gathering**: User provides all relevant context while the agent asks clarifying questions
 2. **Refinement & Structure**: Iteratively build each section through brainstorming and editing
-3. **Reader Testing**: Test the doc with a fresh Claude (no context) to catch blind spots before others read it
+3. **Reader Testing**: Test the doc with a fresh subagent (no context) to catch blind spots before others read it
 
-Explain that this approach helps ensure the doc works well when others read it (including when they paste it into Claude). Ask if they want to try this workflow or prefer to work freeform.
+Explain that this approach helps ensure the doc works well when others read it (including when they paste it into an AI assistant). Ask if they want to try this workflow or prefer to work freeform.
 
 If user declines, work freeform. If user accepts, proceed to Stage 1.
 
 ## Stage 1: Context Gathering
 
-**Goal:** Close the gap between what the user knows and what Claude knows, enabling smart guidance later.
+**Goal:** Close the gap between what the user knows and what the agent knows, enabling smart guidance later.
 
 ### Initial Questions
 
@@ -52,7 +52,7 @@ Inform them they can answer in shorthand or dump information however works best
 
 - Use the appropriate integration to read the current state
 - Check for images without alt-text
-- If images exist without alt-text, explain that when others use Claude to understand the doc, Claude won't be able to see them. Ask if they want alt-text generated. If so, request they paste each image into chat for descriptive alt-text generation.
+- If images exist without alt-text, explain that when others use a text-only AI assistant to understand the doc, it won't be able to see them. Ask if they want alt-text generated. If so, request they paste each image into chat for descriptive alt-text generation.
 
 ### Info Dumping
 
@@ -74,7 +74,7 @@ Advise them not to worry about organizing it - just get it all out. Offer multip
 
 **If integrations are available** (e.g., Slack, Teams, Google Drive, SharePoint, or other MCP servers), mention that these can be used to pull in context directly.
 
-**If no integrations are detected and in Claude.ai or Claude app:** Suggest they can enable connectors in their Claude settings to allow pulling context from messaging apps and document storage directly.
+**If no integrations are available:** Suggest connecting the relevant integration, or pasting the relevant content directly.
 
 Inform them clarifying questions will be asked once they've done their initial dump.
 
@@ -82,7 +82,7 @@ Inform them clarifying questions will be asked once they've done their initial d
 
 - If user mentions team channels or shared documents:
   - If integrations available: Inform them the content will be read now, then use the appropriate integration
-  - If integrations not available: Explain lack of access. Suggest they enable connectors in Claude settings, or paste the relevant content directly.
+  - If integrations not available: Explain lack of access. Suggest connecting the relevant integration, or pasting the relevant content directly.
 
 - If user mentions entities/projects that are unknown:
   - Ask if connected tools should be searched to learn more
@@ -137,21 +137,7 @@ Ask if this structure works, or if they want to adjust it.
 
 Create the initial document structure with placeholder text for all sections.
 
-**If access to artifacts is available:**
-Use `create_file` to create an artifact. This gives both Claude and the user a scaffold to work from.
-
-Inform them that the initial structure with placeholders for all sections will be created.
-
-Create artifact with all section headers and brief placeholder text like "[To be written]" or "[Content here]".
-
-Provide the scaffold link and indicate it's time to fill in each section.
-
-**If no access to artifacts:**
-Create a markdown file in the working directory. Name it appropriately (e.g., `decision-doc.md`, `technical-spec.md`).
-
-Inform them that the initial structure with placeholders for all sections will be created.
-
-Create file with all section headers and placeholder text.
+Use the `write` tool to create a markdown file in the working directory with all section headers and brief placeholder text like "[To be written]" or "[Content here]". Name it appropriately (e.g., `decision-doc.md`, `technical-spec.md`).
 
 Confirm the filename has been created and indicate it's time to fill in each section.
 
@@ -193,16 +179,10 @@ Based on what they've selected, ask if there's anything important missing for th
 
 ### Step 5: Drafting
 
-Use `str_replace` to replace the placeholder text for this section with the actual drafted content.
+Use the `edit` tool to replace the placeholder text for this section with the actual drafted content.
 
 Announce the [SECTION NAME] section will be drafted now based on what they've selected.
 
-**If using artifacts:**
-After drafting, provide a link to the artifact.
-
-Ask them to read through it and indicate what to change. Note that being specific helps learning for the next sections.
-
-**If using a file (no artifacts):**
 After drafting, confirm completion.
 
 Inform them the [SECTION NAME] section has been drafted in [filename]. Ask them to read through it and indicate what to change. Note that being specific helps learning for the next sections.
@@ -214,9 +194,8 @@ Provide a note: Instead of editing the doc directly, ask them to indicate what t
 
 As user provides feedback:
 
-- Use `str_replace` to make edits (never reprint the whole doc)
-- **If using artifacts:** Provide link to artifact after each edit
-- **If using files:** Just confirm edits are complete
+- Use the `edit` tool to make edits (never reprint the whole doc)
+- Just confirm edits are complete
 - If user edits doc directly and asks to read it: mentally note the changes they made and keep them in mind for future sections (this shows their preferences)
 
 **Continue iterating** until user is satisfied with the section.
@@ -251,14 +230,14 @@ Ask if ready to move to Reader Testing, or if they want to refine anything else.
 
 ## Stage 3: Reader Testing
 
-**Goal:** Test the document with a fresh Claude (no context bleed) to verify it works for readers.
+**Goal:** Test the document with a fresh subagent (no context bleed) to verify it works for readers.
 
 **Instructions to user:**
 Explain that testing will now occur to see if the document actually works for readers. This catches blind spots - things that make sense to the authors but might confuse others.
 
 ### Testing Approach
 
-**If access to sub-agents is available (e.g., in Claude Code):**
+**If the subagent tool is available:**
 
 Perform the testing directly without user involvement.
 
@@ -270,24 +249,24 @@ Generate 5-10 questions that readers would realistically ask.
 
 ### Step 2: Test with Sub-Agent
 
-Announce that these questions will be tested with a fresh Claude instance (no context from this conversation).
+Announce that these questions will be tested with a fresh subagent instance (no context from this conversation).
 
-For each question, invoke a sub-agent with just the document content and the question.
+For each question, invoke a subagent with just the document content and the question.
 
-Summarize what Reader Claude got right/wrong for each question.
+Summarize what the reader agent got right/wrong for each question.
 
 ### Step 3: Run Additional Checks
 
 Announce additional checks will be performed.
 
-Invoke sub-agent to check for ambiguity, false assumptions, contradictions.
+Invoke a subagent to check for ambiguity, false assumptions, contradictions.
 
 Summarize any issues found.
 
 ### Step 4: Report and Fix
 
 If issues found:
-Report that Reader Claude struggled with specific issues.
+Report that the reader agent struggled with specific issues.
 
 List the specific issues.
 
@@ -297,13 +276,13 @@ Loop back to refinement for problematic sections.
 
 ---
 
-**If no access to sub-agents (e.g., claude.ai web interface):**
+**If the subagent tool is not available:**
 
 The user will need to do the testing manually.
 
 ### Step 1: Predict Reader Questions
 
-Ask what questions people might ask when trying to discover this document. What would they type into Claude.ai?
+Ask what questions people might ask when trying to discover this document. What would they ask an AI assistant?
 
 Generate 5-10 questions that readers would realistically ask.
 
@@ -311,21 +290,20 @@ Generate 5-10 questions that readers would realistically ask.
 
 Provide testing instructions:
 
-1. Open a fresh Claude conversation: https://claude.ai
-2. Paste or share the document content (if using a shared doc platform with connectors enabled, provide the link)
-3. Ask Reader Claude the generated questions
+1. Open a fresh session and paste the document content
+2. Ask the reader agent the generated questions
 
-For each question, instruct Reader Claude to provide:
+For each question, instruct the reader to provide:
 
 - The answer
 - Whether anything was ambiguous or unclear
 - What knowledge/context the doc assumes is already known
 
-Check if Reader Claude gives correct answers or misinterprets anything.
+Check if the reader gives correct answers or misinterprets anything.
 
 ### Step 3: Additional Checks
 
-Also ask Reader Claude:
+Also ask the reader:
 
 - "What in this doc might be ambiguous or unclear to readers?"
 - "What knowledge or context does this doc assume readers already have?"
@@ -333,7 +311,7 @@ Also ask Reader Claude:
 
 ### Step 4: Iterate Based on Results
 
-Ask what Reader Claude got wrong or struggled with. Indicate intention to fix those gaps.
+Ask what the reader got wrong or struggled with. Indicate intention to fix those gaps.
 
 Loop back to refinement for any problematic sections.
 
@@ -341,12 +319,12 @@ Loop back to refinement for any problematic sections.
 
 ### Exit Condition (Both Approaches)
 
-When Reader Claude consistently answers questions correctly and doesn't surface new gaps or ambiguities, the doc is ready.
+When the reader consistently answers questions correctly and doesn't surface new gaps or ambiguities, the doc is ready.
 
 ## Final Review
 
 When Reader Testing passes:
-Announce the doc has passed Reader Claude testing. Before completion:
+Announce the doc has passed reader testing. Before completion:
 
 1. Recommend they do a final read-through themselves - they own this document and are responsible for its quality
 2. Suggest double-checking any facts, links, or technical details
@@ -380,12 +358,12 @@ Announce document completion. Provide a few final tips:
 - Throughout, if context is missing on something mentioned, proactively ask
 - Don't let gaps accumulate - address them as they come up
 
-**Artifact Management:**
+**File Management:**
 
-- Use `create_file` for drafting full sections
-- Use `str_replace` for all edits
-- Provide artifact link after every change
-- Never use artifacts for brainstorming lists - that's just conversation
+- Use `write` to create the draft file with full sections
+- Use `edit` for all subsequent edits
+- Confirm the file path after every change
+- Never use file drafts for brainstorming lists - that's just conversation
 
 **Quality over Speed:**
 
diff --git a/system-prompt.md b/system-prompt.md
index 1fc4749..d7a0634 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.67.0</system_version>
+<system_version>9.68.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -227,8 +227,8 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
   <context_phase>
     HANDS INSTRUCTION: You are in DISCOVERY mode. Your goal is to gather context for the Orchestrator.
-    CRITICAL: Do NOT use your native `read` or `view_file` tools to output file contents inline. You must use the `custom_context` MCP server tools.
-    SKILL LOADING: Load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi). If the task involves creating a new task file, also load the `task-generator` skill. Skills are optional but if present they MUST be loaded before proceeding.
+    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools.
+    SKILL LOADING: Load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, node-hexagonal-api, python-fastapi). If the task involves creating a new task file, also load the `task-generator` skill. Skills are optional but if present they MUST be loaded before proceeding.
 </context_phase>
 
   <execution_phase>
@@ -269,7 +269,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 </validation_phase>
 
   <context_phase>
-    HANDS INSTRUCTION: Read the active task file in `tasks/`. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to your subagents: use a read-only codebase-mapping subagent (e.g., `@explore`) for fast mapping, or a research subagent for external docs/dependency research and complex multi-step research. Utilize any configured MCP servers if external context is required.
+    HANDS INSTRUCTION: Read the active task file in `tasks/`. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to your subagents: use the read-only `cognitive-discovery` subagent for fast mapping, or a research subagent for external docs/dependency research and complex multi-step research. Utilize any configured MCP servers if external context is required.
     **MANDATORY SKILL ORCHESTRATION:** Load the following skills:
     1. [Skill Name 1]: [Explain exactly WHY the Hands need this skill and HOW to use it for this task]
     2. [Skill Name 2]: [Explain exactly WHY and HOW...]
@@ -293,7 +293,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
      CRITICAL TOOL RULES:
      0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
-     1. If applying file patches, utilize your native file-editing tools (e.g., `apply_patch`). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
+     1. If applying file patches, utilize your native file-editing tools (`edit` for replacements, `write` for new files). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
      2. If user feedback is required, first check the session capability manifest for your question/clarification tool. If the tool is AVAILABLE, utilize it with multi-option schemas. If it is UNAVAILABLE, do NOT silently skip the question: relay it to the Manager as one narrow question with the options inline, then wait for the answer (manual mode) or record the replay-or-halt decision in the task file (autopilot mode).
      3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.
      4. **Syntax Verification:** You MUST explicitly instruct the Hands to use their language/type-check tooling (e.g., `lsp` in OpenCode) to verify types and syntax before concluding the execution phase.
@@ -366,7 +366,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     1.6. GRAPH-FIRST: Run `custom_context_build_graph` once on the target scope (saves versioned `graph_*.json` + `graph_report_*.md`), then prefer `custom_context_query_graph` / `custom_context_explain_node` / `custom_context_shortest_path` / `custom_context_god_nodes` for cross-file questions before falling back to full reads.
     2. Run the `custom_context_read_source_files` tool to fetch the absolute source of truth: `AGENTS.md`, `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. If they exist, they MUST be included in the report.
     3. Compile the results into a single context report using the MCP tools.
-    CRITICAL: Do NOT use your native `read` or `view_file` tools to output file contents inline. You must use the `custom_context` MCP server tools.
+    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools.
 </discovery_phase>
 
   <conditional_implementation_phase>
@@ -515,7 +515,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 - **Conventional Commits Format Gate:** Every feature commit message passed to `custom_context_commit_and_clean_task` MUST match `<type>: <subject>` with type in `feat|fix|docs|refactor|chore` and first line ≤72 characters (per `skill-templates/versioning-and-release`). The tool validates and rejects free-form messages. The templated `chore: close task N` closure commit always conforms by construction.
 - **Supervised Autopilot Contract:** On the lock words the Hands run end to end: discovery feed, Brain plan, one approval pause for the plan, seat-routed implementation, QA and review loops, results shown before the move to qa. Besides that single plan-approval pause, only Relay questions and hard blockers interrupt. Risk tiers live in `docs/conventions.md` (T0 trivial, T1 standard, T2 destructive needs per-action approval). Plan, QA, and review loops allow three tries max, then escalate. Authority for the full rule text is `agents/cognitive-executor.md`.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
-- **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent subagents, e.g., `@explore` or `@general`) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
+- **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent `cognitive-discovery` subagents) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. Keep AI tells out of the prose: no hedging openers ("it is worth noting", "it is important to note"), no inflated significance ("stands as a testament", "underscores the importance"), no negative parallelism ("not just X, but Y"), no rote rule-of-three lists, no collaborative preambles ("Great question", "Let me unpack this"), and no trailing recap that repeats what you already said. Banned phrases (never emit them): "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
 - **Reference Point System:** When presenting three or more findings, options, decisions, or questions to the Manager, you MUST assign a short code to each item (e.g., F1, F2 for Findings; O1, O2 for Options; D1 for Decisions; Q1 for Questions). This anchors complex discussions and makes them highly traceable.
 - **Manager-Facing Output Style (positive contract):** This governs the final externally visible reply to the Manager. `<reasoning_log>`, chain-of-thought, XML task generation, blueprints, and Hands Execution Logs stay unrestricted and rich — conciseness rules NEVER apply to those channels.
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 0340220..ab35097 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,28 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.67.0"
+    assert shipped == "9.68.0"
+
+
+def test_shipped_prompt_names_only_catalog_tools():
+    """The shipped prompt must not name tools outside the session toolset.
+
+    Regression (night sweep): fragments named `nodejs-express` (no such
+    skill), `@explore`/`@general` (no such subagents), and `view_file` /
+    `apply_patch` (no such native tools). The Hands cannot call what does
+    not exist, so phantom names are a hard failure, not style.
+    """
+    text = _read(SHIPPED)
+    for phantom in (
+        "nodejs-express",
+        "@explore",
+        "@general",
+        "view_file",
+        "apply_patch",
+    ):
+        assert phantom not in text, f"phantom tool name in shipped prompt: {phantom}"
+    assert "node-hexagonal-api" in text
+    assert "cognitive-discovery" in text
 
 
 def test_executor_carries_compaction_guidance():
diff --git a/tests/test_skill_registry.py b/tests/test_skill_registry.py
index ee61cd4..3bcddc6 100644
--- a/tests/test_skill_registry.py
+++ b/tests/test_skill_registry.py
@@ -407,6 +407,23 @@ def _local_skill_names():
     )
 
 
+def test_doc_coauthoring_skill_is_runtime_neutral():
+    text = _template_text("doc-coauthoring")
+    for banned in (
+        "Claude",
+        "claude.ai",
+        "Anthropic",
+        "create_file",
+        "str_replace",
+        "connectors",
+        "artifact",
+    ):
+        assert banned not in text, f"Claude-centric term in doc-coauthoring: {banned}"
+    assert "`write` tool" in text
+    assert "`edit` tool" in text
+    assert "subagent" in text
+
+
 def test_audit_template_requires_project_skills_table():
     text = (ROOT / "skill-templates" / "audit-agents" / "SKILL.md").read_text(
         encoding="utf-8"
```
<!-- END_GIT_DIFF -->
