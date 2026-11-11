# Task 395: Tool Catalog Truth and Phantom Name Purge

**File:** `tasks/qa/395-tool-catalog-truth-and-phantom-purge.md`
**Source:** manager
**Type:** bug
**Status:** in-progress
**Submitted:** 2026-11-11T05:38:23Z

## Goal

Make every instruction artifact name only tools that exist in the OpenCode 2 /
OpenChamber 2 session, and record the real catalog with its model gate so the
phantom-name defect cannot return.

## Manager's Notes

Research first, then fix. The Manager's question that opened this task: the
Hands drifts to python/shell edits on large repos instead of the native edit
tool. Research answered why: the session has no `apply_patch`, several live
skills still order the agent to call it, and the edit ban is prose-only. Scope
is the tool references and the catalog truth, not a redesign of the edit
policy.

## Research Findings (verified this turn)

- **F1 — `apply_patch` is a phantom in live skills.**
  `skill-templates/debug-instrumentation/SKILL.md:25` and `:49` say "Use the
  `apply_patch` tool". `skill-templates/governance/templates/audit.md:430`
  repeats it. The installed copies under `~/.config/opencode/skills/` carry the
  same lines, so loading either skill injects a tool that cannot be called.
- **F2 — the shell tool is misnamed.**
  `skill-templates/debug-instrumentation/SKILL.md:34` says "your `bash` tool".
  OpenCode 2 exposes `shell`; permission action is `shell`.
- **F3 — stale subagent syntax in the root rules.**
  `AGENTS.md:63` names `@explore` / `@general`. OpenCode 2 calls subagents
  through the `subagent` tool with `agent: "explore" | "general" |
  "cognitive-discovery"`; the `@name` form is not a callable syntax and the
  line omits `cognitive-discovery`.
- **F4 — the model gate that explains the whole drift.**
  OpenCode docs (https://opencode.ai/docs/tools, fetched 2026-11-11): "OpenCode
  exposes `patch` for supported GPT models; other models receive `edit` and
  `write` instead." The shipped binary carries `apply_patch` and the
  `*** Update File:` patch parser, so the code exists but is not exposed to a
  non-GPT model. Our default model is DeepSeek, so `apply_patch` can never
  appear in this session — no config change fixes it.
- **F5 — no sanctioned recovery after a failed edit.**
  `agents/cognitive-executor.md:233` bans forcing a non-unique anchor but names
  no retry, so the agent improvises with the only always-available writer.
  Recorded breaches of that same rule: `tasks/archive/0350`, `0372`, `0373`,
  `0383`.
- **F6 — OpenChamber 2 tools are undocumented here.**
  The session exposes `openchamber_render`, `openchamber_secret`,
  `openchamber_notify`, `openchamber_web`, and the `opencode` namespace
  (`models`, `worktree_create/list/remove`, `session_move`, `session_rename`,
  `read_mcp_resource`, `list_mcp_resources`). `docs/openchamber.md` mentions
  only `openchamber_web`. OpenChamber 2 also documents `openchamber` (control)
  and `openchamber_schedule`, which this session does not expose.
- **F7 — verified non-issues.** `view_file`, `multiedit`, `str_replace_editor`,
  `create_file`, `websearch`, `nodejs-express` return zero hits in live
  artifacts; the hits in `prompts/fragments/DECISIONS.md:67` and
  `skill-templates/DECISIONS.md:18` are historical ADR evidence and stay.

## Local TODOs

- [x] Research the OpenCode 2 and OpenChamber 2 catalogs and record citations
- [x] Create the task file in `tasks/backlog/`
- [x] Seat Check and Brain planning round
- [x] Present the plan and collect Manager approval
- [x] Purge `apply_patch` and `bash` from `skill-templates/**`
- [x] Fix the `AGENTS.md` subagent syntax and name `cognitive-discovery`
- [x] Add the catalog-truth section with the model gate to the executor agent
- [x] Add the edit recovery protocol next to the edit discipline rule
- [x] Add a regression test over `skill-templates/**` and `AGENTS.md`
- [x] Update `CHANGELOG.md` and run the full gate

## Acceptance Criteria

- [x] `grep -rn "apply_patch" skill-templates/ AGENTS.md README.md agents/ docs/` returns zero hits
- [x] `grep -rn "\`bash\` tool" skill-templates/ agents/` returns zero hits
- [x] `AGENTS.md` describes subagents via the `subagent` tool and names `cognitive-discovery`
- [x] The executor names its real writers (`edit`, `write`) in a "Your Tool Surface" section and carries no model-identity or patch archaeology
- [x] The executor names the sanctioned recovery after a failed edit
- [x] `docs/openchamber.md` lists the OpenChamber tools this session exposes
- [x] A regression test fails on any phantom tool name in `skill-templates/**`, `AGENTS.md`, `README.md`, `prompts/**`, `agents/**`, or `docs/**`
- [x] A regression test fails on any `sed -i` edit instruction in a live artifact
- [x] No installed skill under `~/.config/opencode/skills/` diverges from its `skill-templates/` source
- [x] Both agents are rewritten as lean operator guides with no plugin provenance, version history, or dated verification stamps
- [x] Full pytest suite passes with exit code 0

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml pytest tests/ -q`
- **Expected result:** all tests pass, including the new phantom-name regression tests
- **Actual result:** `832 passed, 23 warnings in 63.29s` (final run, after the edit-instruction audit added `test_no_scripted_edit_instructions`)
- **Exit code:** 0

**Gate detail**

- Exact-pin note: the recorded command uses `mcp==1.30.0` rather than `mcp[cli]>=1.0,<2.0`. `rtk test` joins its arguments without quoting, so a `<` inside a version spec is misparsed as input redirection (documented in `docs/opencode-shell-strategy.md` §8). The exact pin keeps the wrapper safe and the exit code honest.
- New regression file alone: `uv run --with pytest pytest tests/test_tool_catalog_truth.py -q` → `5 passed`, exit 0.
- Legacy gate files after the V2 rewrite: `tests/test_agent_tool_gate.py` + `tests/test_prompt_sync.py` + the new file → `49 passed`, exit 0.
- Purge greps: `grep -rn "apply_patch" skill-templates/ AGENTS.md README.md` → 0 hits; `` grep -rn '`bash` tool' skill-templates/ `` → 0 hits; `grep -rn "@explore" AGENTS.md README.md skill-templates/ prompts/fragments/` (DECISIONS excluded) → 0 hits.
- Permission probe (P5): `git add -n .` → `permission.rejected: Permission denied: shell`. The ZAC deny is enforced by the permission layer, not only by prose. The probe is a non-mutating dry run and it never executed.

> Verification runner rule: the first verification run MUST use the `rtk test`
> prefix; a raw rerun is allowed only after a failed RTK run for diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

## Risk & Rollback

- **Risk:** a purge that also deletes the historical ADR evidence in
  `prompts/fragments/DECISIONS.md` and `skill-templates/DECISIONS.md`, or a
  regression test so broad that it flags legitimate prose.
- **Rollback plan:** every change is prose plus one test file; revert the
  touched files from `HEAD` and the suite returns to its previous state.

---

## Execution Log & Reasoning

**Plan provenance:** Architect planning turn, Manager approved twice — the first
plan, then the revised plan after research exposed the V1/V2 permission schema
split. The Senior Programmer emitted the implementation XML from that approval.

**Assumption A1:** "fix our bugs, gaps, missing, extra things across entire
project system" was read as *tool-related* drift across the project, not a
general refactor. Every fix below is a tool reference, an agent permission
rule, or a doc describing them.

**Deviation D1 (XML vs approved plan):** the implementation XML encoded the new
frontmatter as single-key maps (`- read: allow`). That is not the V2 schema and
would have produced rules OpenCode cannot match, so permissions would have
failed open. The approved plan named `{action, resource, effect}`, so that is
what shipped. The XML's Step 9 also duplicated a sentence; the shipped text
keeps one.

**Deviation D2 (test command):** the task file recorded `--with
'mcp[cli]>=1.0,<2.0'`. Under `rtk test` the unquoted `<` is read as input
redirection, so the recorded command became the exact pin `mcp==1.30.0` — the
same dependency set, wrapper-safe, exit code preserved.

**Changes**

1. `skill-templates/debug-instrumentation/SKILL.md` — `apply_patch` → `edit`
   (log injection and the real fix), `` `bash` tool `` → `` `shell` tool ``.
2. `skill-templates/governance/templates/audit.md` — `apply_patch` → `edit`.
3. `AGENTS.md` — `@explore`/`@general` mention syntax replaced with the
   `subagent` tool and the three real agent IDs.
4. `README.md` — same fix in the worked example.
5. `agents/cognitive-executor.md` — frontmatter rewritten to a V2 `permissions`
   array: catch-all allow first, then `external_directory` ask with `/tmp/**`
   allowed, `rm -rf*` ask, and the four ZAC shell denies. `temperature` dropped,
   `steps: 512` kept. Added **Tool Catalog Truth** (the GPT-only `patch` gate
   with its source, the real writers, the real shell/subagent/MCP surfaces) and
   the **Edit Recovery Protocol**.
6. `agents/cognitive-discovery.md` — frontmatter rewritten to deny everything,
   then allow only the read-only surface, closing with explicit `edit` and
   `shell` denies.
7. `docs/openchamber.md` — new §11 session tool catalog: four exposed
   OpenChamber tools, the `opencode` namespace, and the not-exposed set.
8. `docs/conventions.md` — V1-to-V2 permission schema note, including the
   last-match ordering rule.
9. `tests/test_tool_catalog_truth.py` — new five-test gate.
10. `tests/test_agent_tool_gate.py` — helpers now parse the V2 rule array and
    resolve effects by last match instead of scanning for a `bash: allow` map
    entry; both assertions renamed to the shell action.
11. `tests/test_prompt_sync.py` — the checkout deny assertion now reads the V2
    rule instead of the retired map syntax.
12. `CHANGELOG.md` — Parse-Then-Append under Unreleased → Fixed.

**Why the drift happened (the question that opened this task):** the session has
no `apply_patch` because OpenCode exposes `patch` only to supported GPT models;
the drift was not a hallucination but an instruction gap — two live skills
ordered a call that could never succeed, and the edit rule banned forcing an
anchor without naming a sanctioned retry. Both are now closed at the source and
gated by a test.

**Local TODOs:** every item completed; see the checked list above.

## Round 2 — Lean Rewrite (Manager follow-up)

**Manager's words:** the agents should only guide the agent — what to do when XML
arrives, what to do with a raw Manager message, which tools exist. No proof of
origin, no plugin provenance, no model identity. "When GPT is not the model, do
not write that apply_patch exists; say nothing about it."

**Assumption A2:** the two halves of that sentence ("say nothing" and "say it
does not exist") were read as one intent — the topic disappears. Explaining that
a tool is absent still spends tokens on tool archaeology.

**What changed**

1. `agents/cognitive-executor.md` — the "Tool Catalog Truth" section (dated
   stamp, upstream URL, GPT-only explanation, patch parser aside) became **Your
   Tool Surface**: a plain list of what exists. The Smart Compact paragraph lost
   the plugin package name, the V2-internals explanation, the ratio history, and
   the log-line behaviour, keeping only what the agent must do. `todowrite` lost
   its plugin attribution. New **What You Receive, and What You Do** section
   gives the four entry paths (Brain XML, raw Manager message, review verdict,
   nothing actionable) in one place.
2. `agents/cognitive-discovery.md` — 119 lines to 90. Objective list, plugin
   asides, and duplicated discipline sections became **Your Tools**, **How to
   Work**, **What You Return**, **Stop and Report**.
3. `docs/openchamber.md` — the not-exposed note now covers only the two
   OpenChamber tools; the patch/GPT paragraph is gone.
4. `tests/test_tool_catalog_truth.py` — `test_executor_states_model_gate` became
   `test_executor_states_tool_surface`, which now also fails on the words
   `GPT`, `non-GPT`, `apply_patch`, and `patch parser` returning to the executor.
   The sweep roots grew from four to six: `agents/` and `docs/` are now scanned,
   which is the blind spot QA flagged as M1.
5. `tests/test_prompt_sync.py` — two literals were load-bearing assertions that
   the rewrite touched ("100 todos", and the manifest sentence boundary); both
   were restored in the leaner wording rather than weakening the tests.

**Why this is cheaper, not just shorter:** every removed sentence was either
provenance the agent cannot act on, or an explanation of why a tool is missing —
which teaches a model to reason about a tool that is not in its catalog. The
operator guide now states only what exists and what to do, so the model spends
its context on the task instead of on tool archaeology.

## Round 3 — Review Postfix

Code Reviewer returned `APPROVED_WITH_CHANGES` with two doc-level issues:

- **I1 (major):** the Tool Surface list was closed-world but omitted `skill`,
  `question`, `webfetch`, and `websearch`, all of which the executor is required
  to use elsewhere. Fixed by one bullet in the same section.
- **I2 (minor):** the CHANGELOG still described the retired Tool Catalog Truth
  section and its GPT-only language. Fixed by rewriting that sentence.
- **I3 (low, follow-up):** the checkout assertion checks `resource` and `effect`
  on separate lines rather than as one bound rule. A mismatch inside one file
  would pass that single test. The V2 last-match helper and the recorded runtime
  deny probe cover it here, so it stays a follow-up rather than scope creep.

## Round 4 — Review Verdict

Code Reviewer re-reviewed the postfix and returned **PO_REVIEW_PENDING**
(technical approval; PO closure decision outstanding).

- F1–F3: P1 purge, P2 permission rewrite, and P3 operator guide all hold against
  the approved plan.
- F4: I1 closed — `skill`, `question`, `webfetch`, `websearch` are in the Tool
  Surface list.
- F5: I2 closed — the CHANGELOG names **Your Tool Surface** with no model
  identity and no retired section name.
- R1 (read conflict, no runtime effect): one live CHANGELOG slice in the reviewer
  feed read as stale. Confirmed on disk: `grep -n "Your Tool Surface"
  CHANGELOG.md` → 1 hit; `grep -c "Tool Catalog Truth" CHANGELOG.md` → 0.
- R2: I3 remains a follow-up by agreement; no scope widening.

**Status:** `PO_REVIEW_PENDING` — awaiting the Manager's explicit
"Approved for closure".

**PO decision:** "Hold for changes" — closure not authorized. Nothing was
committed; the task stays in `tasks/qa/` with the diff injected, so the change
set is intact and reviewable while the requested changes are defined.

## Round 5 — Repo-Wide Edit-Instruction Audit

**Question asked:** does any live artifact tell the agent to edit files with
python or a script, and is the prohibition consistent everywhere?

**Answer: two contradictions existed, both now closed.**

- **F1 — installed skills were stale.** `~/.config/opencode/skills/debug-instrumentation/SKILL.md`
  and `…/governance/templates/audit.md` still carried `apply_patch`. These are
  the copies the agent actually loads; the repo templates were fixed in round 1
  but the installed copies were not. Synced byte-for-byte from the templates and
  verified with `diff -q` (all three identical, zero `apply_patch` hits under
  `~/.config/opencode/skills/`).
- **F2 — `flask-python` instructed a `sed -i` edit.**
  `skill-templates/flask-python/SKILL.md:118` and `:410` told the agent to run
  `sed -i 's/<SERVICE_NAME>/myapp/g'`. That is a scripted file edit, banned by
  `AGENTS.md:46` and `docs/conventions.md:168`. Both lines now direct the agent
  to the native `edit` tool with `replaceAll`. Installed copy synced.

**Clean surfaces (no wrong instruction found):** `AGENTS.md:46`,
`docs/conventions.md:168`, `agents/cognitive-executor.md:255,280`,
`skill-templates/governance/SKILL.md:21`, and `skill-templates/governance/templates/audit.md`
all state the same ban in the same words. Every remaining `python` mention in a
live surface is a legitimate one — MCP server launch commands, the `flask-python`
/ `python-fastapi` skill names, and the prompt assembler invocation. `LLM.txt`
and `README.md` mention python only for installation and server startup.

**New gate:** `test_no_scripted_edit_instructions` fails on any `sed -i '`
substitution shape in a live artifact, while still allowing the ban prose that
names `` `sed -i` ``. Suite: 832 passed, exit 0.

**Full drift check:** every directory under `skill-templates/` now compares
identical to its installed counterpart — no stale skill remains.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index 5641122..5d87a98 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -60,7 +60,7 @@ This repository is the Headquarters for the Cognitive Lead AI multi-agent system
 - **Don't** issue multi-step or large tasks without loading relevant skills and structuring work as a Goal.
   -> **Do** instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat multi-phase implementations as Goal units with explicit verification gates. (Goal-Oriented Tasks — V9.1.0)
 - **Don't** execute independent file scans, signature extractions, or decoupled module changes serially.
-  -> **Do** spawn parallel subagents (up to 4 concurrent agents, e.g., `@explore` or `@general`) whenever a task involves 2+ independent workstreams. (Parallel Agent Execution — V9.1.0)
+  -> **Do** spawn parallel subagents (up to 4 concurrent agents) via the `subagent` tool with `agent` set to `explore`, `general`, or `cognitive-discovery` whenever a task involves 2+ independent workstreams. (Parallel Agent Execution — V9.1.0)
 - **Don't** reference task numbers in Markdown prose (prompts, skills, docs, headings).
   -> **Do** reference task numbers ONLY in code comments, `CHANGELOG.md`, task files, history archives, and HTML comments. See Task-Number Reference Discipline in `docs/conventions.md`.
 - **Don't** silently alter slice architecture or domain invariants.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 293b236..e734b16 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -33,6 +33,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Tool catalog truth and phantom-name purge (task 395):** live artifacts no longer name tools the session cannot call. `apply_patch` became `edit` in `skill-templates/debug-instrumentation/SKILL.md` and `skill-templates/governance/templates/audit.md`; the `bash` tool reference became `shell`; the `@explore`/`@general` mention syntax in `AGENTS.md` and `README.md` became the `subagent` tool with `agent` set to `explore`, `general`, or `cognitive-discovery`. Both custom agents moved to the canonical V2 `permissions` array (the deprecated `permission` map, `tools`, `temperature`, and `bash` action are gone): the executor keeps a catch-all allow refined by the ZAC shell denies, and the discovery agent denies everything first then allows only its read-only surface. `agents/cognitive-executor.md` gained a **Your Tool Surface** operator list plus an **Edit Recovery Protocol** with no model-identity prose. `docs/openchamber.md` gained the session tool catalog and `docs/conventions.md` the V1-to-V2 permission note. New `tests/test_tool_catalog_truth.py` gates all of it.
 - **Harness suite green again (task 394):** repaired three stale assertions left behind by earlier consolidations. F1 (`tests/test_mcp_servers.py`) now derives its target inventory from `skill-templates/*/SKILL.md` on disk plus `agents/cognitive-executor.md` instead of a hardcoded `>= 31` floor, keeping both `OpenCode Execution Log` bans. F2/F3 (`tests/test_input_validation_pipeline.py`) assert the documented always-English policy — "clarification request in simple English" in fragment 05, "in simple English, no matter which language the input used" in `docs/conventions.md`, and "regardless of the input language" plus "simple English but technical" in `agents/cognitive-executor.md` — with negative asserts against the retired per-message requested-language phrases. Test-only; no production prompt or doc changed.
 
 ## [9.77.0] - 2026-11-08
diff --git a/README.md b/README.md
index fa137ea..ce6fb64 100644
--- a/README.md
+++ b/README.md
@@ -454,7 +454,7 @@ To make the `code-search` skill (or any other reusable skill) available in _ever
    ```
    Under the available skills list, you will see `code-search` listed. You can now use it in any project by asking:
    ```plaintext
-   @explore find the main router using the code-search skill
+   Use the subagent tool with agent explore to find the main router using the code-search skill
    ```
 
 ---
diff --git a/agents/cognitive-discovery.md b/agents/cognitive-discovery.md
index 9825b5a..b91bb62 100644
--- a/agents/cognitive-discovery.md
+++ b/agents/cognitive-discovery.md
@@ -1,83 +1,90 @@
 ---
 description: Read-only subagent for gathering context via custom_context MCP tools.
 mode: subagent
-permission:
-  edit: deny
-  bash: deny
-  read: allow
-  execute: allow
-  skill: allow
-  custom_context_*: allow
-  external_directory:
-    "*": "ask"
-    "/tmp/**": "allow"
+permissions:
+  # Deny everything first, then allow the read-only discovery surface.
+  - action: "*"
+    resource: "*"
+    effect: deny
+  - action: read
+    resource: "*"
+    effect: allow
+  - action: glob
+    resource: "*"
+    effect: allow
+  - action: grep
+    resource: "*"
+    effect: allow
+  - action: webfetch
+    resource: "*"
+    effect: allow
+  - action: websearch
+    resource: "*"
+    effect: allow
+  - action: skill
+    resource: "*"
+    effect: allow
+  - action: subagent
+    resource: "*"
+    effect: allow
+  # Code Mode is the only path to the custom_context MCP tools.
+  - action: execute
+    resource: "*"
+    effect: allow
+  - action: "custom_context_*"
+    resource: "*"
+    effect: allow
+  - action: external_directory
+    resource: "*"
+    effect: ask
+  - action: external_directory
+    resource: "/tmp/**"
+    effect: allow
+  # Read-only guarantees, stated last so they win.
+  - action: edit
+    resource: "*"
+    effect: deny
+  - action: shell
+    resource: "*"
+    effect: deny
 ---
 
-# Cognitive Discovery Subagent
+# Cognitive Discovery
 
-You are a read-only assistant specialized in codebase mapping and context extraction. Report always in simple English but technical. Never call `goal_*` or `compact_*` tools — this agent is `custom_context_*` only.
+You map code so the executor does not have to read it all. You report; you never change anything.
 
-## Objective
+## Your Tools
 
-When invoked, you must use the `custom_context` MCP tools to compile comprehensive context reports.
+- **`custom_context.*` through `execute`** — your primary surface: `get_directory_tree`, `create_tree_report`, `read_source_files`, `extract_signatures`, `build_graph`, `query_graph`, `explain_node`, `shortest_path`, `god_nodes`, `graph_stats`. Other MCP servers are not yours.
+- **`read`, `grep`, `glob`** — direct inspection when a file is small or the graph is stale.
+- **`webfetch`, `websearch`** — external docs.
+- **`skill`** — load a skill when the report needs its rules.
+- **`subagent`** — split a wide map into parallel lanes.
 
-1. Use `get_directory_tree` to map the requested directory structure.
-2. Use `create_tree_report` to persist a `.gitignore-aware` tree of a path or the whole project as `context-reports/tree_report_<timestamp>_<uuid>.md` when the Manager asks to "create a tree of the project".
-3. Use `read_source_files` to fetch the exact source code of requested files.
-4. Use `extract_signatures` to pull function/class signatures for vertical slices.
-5. Graph-first: run `build_graph` once per scope (saves versioned `graph_*.json` + `graph_report_*.md` with EXTRACTED/INFERRED edges), then prefer `query_graph` / `explain_node` / `shortest_path` / `god_nodes` for cross-file questions before full reads. Use `graph_stats` to confirm coverage.
-6. You still must not write, record, or evolve anything.
-7. End every report with a machine-readable `### Context Manifest` section listing the concrete sliced paths the executor feeds directly into `brain_turn(context_paths=[...])`:
+You have no file writer and no shell. Do not try to acquire one, and do not ask for one.
 
-   ```markdown
-   ### Context Manifest
-   Context-Paths:
-   - path/to/file1.ext#Lstart-end
-   - path/to/file2.ext#Lstart-end
-   ```
+## How to Work
 
-   Every `Context-Paths` entry MUST use a concrete `#Lstart-end` range. For a small file, use the full-file line range. The manifest is the primary deliverable for Brain planning turns; the prose findings above it are secondary.
+1. Run `build_graph` once per scope, then reuse it: `query_graph`, `explain_node`, and `god_nodes` answer cross-file questions far cheaper than reading files.
+2. Map structure with `get_directory_tree`; persist a tree report only when asked.
+3. Pull `extract_signatures` before bodies, and batch `read_source_files` for the few files that matter.
+4. Batch independent calls inside one `execute` script instead of one round trip each.
+5. Stop when the question is answered. Do not explore past the scope you were given.
 
-Do not modify any files. Do not attempt to execute code. Compile the report with its Context Manifest and halt.
+## What You Return
 
-## Execution Discipline
+- Every claim names a path, and a line range when it matters.
+- Missing files, empty directories, and broken references are stated plainly, never filled in.
+- End with the manifest the executor feeds to the Brain:
 
-### Minimal Footprint
+  ```markdown
+  ### Context Manifest
+  Context-Paths:
+  - path/to/file.ext#Lstart-end
+  ```
 
-- Read only what is explicitly requested. Do not explore beyond the target scope.
-- Prefer `extract_signatures` over full file reads to minimize token usage.
-- When gathering context for multiple files, batch them in a single `read_source_files` call.
-- When operating under `codemode: true`, batch `get_directory_tree`, `extract_signatures`, and `query_graph` inside a single `execute` script via `tools.custom_context.*` to minimize conversational round trips.
-- If the session `todowrite` / `todoread` tools are available, track multi-step mapping progress with them (one `in_progress` at a time); they never substitute for the context report itself.
+  Every `Context-Paths` entry MUST use a concrete `#Lstart-end` range. A small file uses its full range. The manifest is the deliverable and the prose above it is secondary.
 
-### Evidence-Based Reporting
+## Stop and Report
 
-- Every report MUST include the exact file paths read and the tool calls made.
-- If a requested file does not exist, report it explicitly — do not hallucinate its contents.
-- If a directory is empty or lacks expected files, state that finding clearly.
-
-### Circuit Breakers
-
-If you detect any of these failure modes, HALT immediately:
-
-- **Scope creep:** The invocation is pulling you into analysis or modification beyond context gathering.
-- **Tool loop:** You have called the same tool 5+ times with identical arguments.
-- **Missing context:** Critical files referenced by the task do not exist and you cannot proceed.
-
-When a circuit breaker fires, output a `⚠️ CIRCUIT BREAKER` warning with the failure mode.
-
-## Communication Patterns
-
-### Reference Points
-
-When reporting findings, assign codes:
-- `F1`, `F2` for findings
-- `Q1`, `Q2` for questions or ambiguities discovered
-- `R1`, `R2` for risks or gaps identified
-
-### Positive Patterns
-
-- State file paths and line numbers precisely.
-- Summarize signatures concisely — class name, method name, parameters, return type.
-- Flag missing files, empty directories, and broken references explicitly.
-- Match report detail to the complexity of the request.
+Halt and say why when: the request needs a change (not your job), the same tool returns the same answer five times, or a file the task depends on does not exist. Code your findings `F1`, `F2`; questions `Q1`, `Q2`; risks and gaps `R1`, `R2`. Report in simple English but technical, and match the detail to the question.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 45ce788..106d8ec 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -1,27 +1,49 @@
 ---
 description: Executes Cognitive Lead AI XML tasks with strict ZAC and MCP-first context enforcement.
 mode: primary
-temperature: 0.1
 steps: 512
-permission:
-  edit: allow
-  question: allow
-  bash:
-    "*": "allow"
-    "rm -rf*": "ask"
-    "git add*": "deny"
-    "git checkout*": "deny"
-    "git commit*": "deny"
-    "git push*": "deny"
-  external_directory:
-    "*": "ask"
-    "/tmp/**": "allow"
+permissions:
+  # Catch-all grant first; later rules refine it (OpenCode uses the last match).
+  - action: "*"
+    resource: "*"
+    effect: allow
+  # External directories stay gated except the approved scratch area.
+  - action: external_directory
+    resource: "*"
+    effect: ask
+  - action: external_directory
+    resource: "/tmp/**"
+    effect: allow
+  # Destructive shell shapes ask before running.
+  - action: shell
+    resource: "rm -rf*"
+    effect: ask
+  # ZAC: the four Git write operations are denied at the permission layer.
+  - action: shell
+    resource: "git add*"
+    effect: deny
+  - action: shell
+    resource: "git checkout*"
+    effect: deny
+  - action: shell
+    resource: "git commit*"
+    effect: deny
+  - action: shell
+    resource: "git push*"
+    effect: deny
 ---
 
 # Cognitive Executor Agent
 
 You are the primary execution engine for the Cognitive Lead AI platform. You receive highly structured XML task blocks and execute them with absolute precision.
 
+## What You Receive, and What You Do
+
+- **An XML task block from the Brain** (`<hands_implementation_task>`, `<hands_discovery_task>`, `<hands_combined_task>`): execute its phases in order — validation, context, execution, bash, documentation, summary. The block is the approved plan; do not re-plan it.
+- **A direct message from the Manager**: validate the intent first (typos, clarity 1-5). At 3 ask one narrowing question, at 2 or below halt. Then load the matching skills, state a short plan, and get explicit approval before writing code.
+- **A review verdict** (`QA_REJECTED`, `REJECTED_NEEDS_FIXES`, or `APPROVED_WITH_CHANGES`): fix only what reproduces, dispute the rest with evidence in the task file.
+- **Nothing actionable**: say so in one line instead of inventing work.
+
 ## Core Protocol (Non-Negotiable)
 
 1. **Entry Point:** Your absolute first action is to read `AGENTS.md`. If `AGENTS.md` references `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, or `docs/conventions.md`, you MUST read them.
@@ -105,7 +127,7 @@ To prevent hallucinations and respect hidden project constraints, you MUST integ
 Context is finite. Two layers of tooling keep long sessions productive — the plugin's own awareness rides on the second — and the agent's durable state lives in the task file and project memory, never only in the chat.
 
 1. **Native safety net.** OpenCode auto-compacts near the model limit: it replaces older turns with one lossy summary and keeps the most recent ~20k tokens (config: `compaction.keep.tokens`). Never depend on it to preserve working state — write the essentials to the task file as you go.
-2. **Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) is installed globally and loaded by OpenCode. It is V2-native: it stores a per-session compaction state and applies it to the model-visible messages per request, so it never mutates the stored transcript. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. Pressure is measured against a budget, not against the model ceiling: `awareness.contextWindowTokens` is a hard cap on the denominator, so the fill is computed against `min(registry limit, configured)` instead of whichever figure happens to be larger. A 1M-token window makes the shipped ratios useless in practice — `warnRatio` 0.5 would only speak at 500k, long after your work has degraded — so the plugin also fires on absolute thresholds, `awareness.warnAtTokens` and `awareness.emergencyAtTokens` (`0` disables either), and this repo pins a 200k working budget with warn at 120k and emergency at 160k in `.opencode/smart-compact.jsonc`. Below the warn line, `awareness.autoTrimRatio` still trims tool output by itself between requests, so expect a tool result to read as a notice even when you did not call `compact_context`; that is the plugin working as intended, and the original is one `read_omitted_content` call away. The plugin logs one line each time it fires a reminder and each time it queues a trim, so a quiet log means nothing fired — not that the mechanism is broken. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. `compact_stats` is the agent's read-only copy of that report (no inputs, never writes), which you call when you need to know whether a compaction actually reclaimed anything: `prunedParts` high with `summarizedTurns` 0 means the bulk is tool output, so a trim is the cheaper move. The line also reports the plugin version, the effective window and whether your configured cap is what set it, the measurement path behind the numbers (`tokenizer` or `heuristic`) and a count of summary `fallbacks`, so a compaction that degraded to truncated prose is visible instead of looking normal. After a prune, prefer a cheap fresh run of the source tool; call `read_omitted_content` with its Content ID (`omitted-NNNN`) ONLY when the output cannot be reproduced cheaply, never speculatively. On a cache miss, re-run the source tool once.
+2. **Smart Compact.** Installed globally and loaded by OpenCode. It keeps your user messages verbatim, condenses each old assistant turn, and prunes bulky tool output into a retrievable cache. It never mutates the stored transcript. Pressure is measured against a working budget, not the model ceiling: this repo pins a 200k budget with a reminder at 120k and an emergency at 160k in `.opencode/smart-compact.jsonc`. Below the reminder line it trims tool output on its own, so a tool result reading as a notice is the plugin working, and the original is one `read_omitted_content` call away. The Manager runs `/magic-compact`, `/magic-trim`, and `/magic-stats`; you cannot. What you can do: call `compact_context` yourself when context is heavy (`keepTurns` protects recent turns, `mode: "trim"` prunes tool output only), call `compact_stats` when you need to know whether a compaction reclaimed anything, and use `read_omitted_content` with its Content ID (`omitted-NNNN`) only when the pruned output cannot be reproduced cheaply. Prefer a cheap fresh run of the source tool; on a cache miss, re-run it once. Never re-run a source tool for output you can retrieve by Content ID.
    Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
 
 3. **Survival contract.** Keep the task file holding: the active task id and Kanban lane, the pinned `[fed-context]` block with citations, the current persona/seat, the locked mode (manual or autopilot), the latest staged diff hash, open blockers, and the next action. Resume from that file after any compaction — never from a summary.
@@ -230,11 +252,36 @@ If tests fail, you have a maximum of 3 repair attempts. If the error persists af
 
 ### Edit Tool Discipline (native tools only)
 
-File edits use ONLY native file-editing tools (edit for replacements, file-write tools for new files). Using python, shell, heredoc, `sed -i`, or any script to create or modify files is strictly forbidden — scripted edits fail silently (replace-all on non-unique anchors, quoting and encoding mangling) while native tools fail loudly on a non-unique anchor. If the anchor does not match uniquely, stop and re-read instead of forcing it. Shell stays read-only for file content (e.g. grep, cat, diff, ls, git status). Verify every edit with grep/diff.
+File edits use ONLY native file-editing tools (edit for replacements, file-write tools for new files). Using python, shell, heredoc, `sed -i`, or any script to create or modify files is strictly forbidden — scripted edits fail silently (replace-all on non-unique anchors, quoting and encoding mangling) while native tools fail loudly on a non-unique anchor. If the anchor does not match uniquely, follow the Edit Recovery Protocol below instead of forcing it. Shell stays read-only for file content (e.g. grep, cat, diff, ls, git status). Verify every edit with grep/diff.
+
+### Your Tool Surface
+
+You write files with `edit` (replace one exact, unique `oldString`) and `write` (create a file or overwrite one whole). Nothing else writes file content. A name outside this list is not a tool you have:
+
+- `read`, `grep`, `glob` — inspect the workspace.
+- `edit`, `write` — change files.
+- `shell` — run commands; read-only for file content.
+- `subagent` — delegate with `agent` set to `explore`, `general`, or `cognitive-discovery`.
+- `execute` — Code Mode; every MCP tool is `tools.<server>.<tool>`.
+- `skill`, `question`, `webfetch`, `websearch` — load a skill, ask the Manager, and read external docs.
+- `todowrite`, `todoread` — track micro-steps.
+- `openchamber_render`, `openchamber_secret`, `openchamber_notify`, `openchamber_web` — chat UI, secrets, notifications, browser panel.
+- `opencode.models`, `opencode.worktree_create`, `opencode.worktree_list`, `opencode.worktree_remove`, `opencode.session_move`, `opencode.session_rename`, `opencode.read_mcp_resource`, `opencode.list_mcp_resources` — models, worktrees, sessions, MCP resources.
+
+### Edit Recovery Protocol
+
+When `edit` reports a missing or non-unique anchor:
+
+1. Re-read the exact slice.
+2. Widen the anchor with unique surrounding context.
+3. Retry once, narrower.
+4. Use `write` only for a file that does not exist yet.
+
+Never reach for python, a shell heredoc, or `sed` to write files. After two failed retries, halt and surface the slice.
 
 ### Micro-Task Tracking (todowrite/todoread)
 
-The `opencode-todolist` plugin provides session-scoped `todowrite` (create/replace the whole list; empty array clears) and `todoread` (read it back), with fields `content` (imperative), `status` (`pending`/`in_progress`/`completed`/`cancelled`), and optional `priority`. Whenever a task decomposes into 2 or more micro-steps, maintain them here alongside the task file: keep exactly one `in_progress`, mark steps `completed` the moment they finish, and `todoread` to recover the list after any compaction instead of reconstructing it from memory. Mirror ANY Brain-produced plan with 2 or more steps including the combined conditional phase into `todowrite` before the first edit. Surface: `todowrite` replaces the whole list and an empty array clears it; caps are 100 todos and 500 characters of content; the list is session-scoped and durable, so it survives interruptions and is re-injected automatically — recover it with `todoread`, never from a remembered transcript (compaction replaces `todowrite` output with a fixed notice).
+When a task decomposes into 2 or more micro-steps, keep them in `todowrite` alongside the task file: exactly one `in_progress`, mark each step `completed` the moment it finishes, and `todoread` to recover the list after any compaction instead of rebuilding it from memory. Mirror any Brain plan with 2+ steps before the first edit. `todowrite` replaces the whole list and an empty array clears it; the list is session-scoped and durable, so it survives interruptions, and it caps at 100 todos.
 
 ### Circuit Breakers
 
diff --git a/docs/conventions.md b/docs/conventions.md
index d25f795..6e470e4 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -167,6 +167,25 @@ Task numbers are provenance for humans, not reasoning material for the model. A
 
 File edits use ONLY native file-editing tools (edit for replacements, file-write tools for new files). Using python, shell, heredoc, `sed -i`, or any script to create or modify files is strictly forbidden — scripted edits fail silently (replace-all on non-unique anchors, quoting and encoding mangling) while native tools fail loudly on a non-unique anchor. Shell stays read-only for file content (e.g. grep, cat, diff, ls, git status). Verify every edit with grep/diff.
 
+### Agent Permission Schema V1 to V2
+
+Agent frontmatter uses the canonical V2 `permissions` array of
+`{action, resource, effect}` rules. OpenCode rules are evaluated in order
+and the **last match wins**, so a catch-all grant or deny goes first and
+the refinements follow it.
+
+The V1 shapes are deprecated and must not be used in new or edited agent
+files: `permission` (singular map), `tools`, `temperature`, `top_p`,
+`prompt`, `disable`, `maxSteps`, and action-scoped `bash` entries. The V2
+shell action is named `shell`. `doom_loop` and `lsp` are not V2 actions.
+See <https://opencode.ai/docs/agents> and
+<https://opencode.ai/docs/permissions>.
+
+`agents/cognitive-executor.md` keeps `steps: 512` and grants a catch-all
+allow refined by the ZAC shell denies. `agents/cognitive-discovery.md`
+denies everything first, then allows the read-only surface, and closes
+with explicit `edit` and `shell` denies.
+
 ## Living Folder Docs Standard
 
 All vertical slices and component directories across projects in this ecosystem MUST maintain colocated documentation and decision records:
diff --git a/docs/openchamber.md b/docs/openchamber.md
index e86b47d..7faaefb 100644
--- a/docs/openchamber.md
+++ b/docs/openchamber.md
@@ -269,3 +269,30 @@ so configure-then-purge loops forever; remove the stub first.
 - [ ] `browser.snapshot` lists the tab; `browser.capture` writes
       `.openchamber/screenshots/*.png`.
 - [ ] Server Browser panel shows the same page the agent opened.
+
+## 11. Session Tool Catalog (verified 2026-11-11)
+
+The agent tool surface in an OpenChamber 2 session is not the same as the
+upstream documentation set. This section records what a session actually
+exposes, so instructions never name a tool the agent cannot call.
+
+**Exposed in this session:**
+
+| Tool | Purpose |
+| ---- | ------- |
+| `openchamber_render` | Draw an HTML page or a `ui` form inline in the chat; `awaitAnswer` collects a choice |
+| `openchamber_secret` | Request a secret on a private card and return only its file path |
+| `openchamber_notify` | Send a notification outside the chat |
+| `openchamber_web` | OpenChamber's browser panel: open a page, snapshot it, click and type |
+
+**Exposed `opencode` namespace:** `models`, `worktree_create`,
+`worktree_list`, `worktree_remove`, `session_move`, `session_rename`,
+`read_mcp_resource`, `list_mcp_resources`.
+
+**Not exposed in this session:** the `openchamber` control tool and
+`openchamber_schedule`, both documented upstream at
+<https://docs.openchamber.dev/agent-control-tool/> and enabled only when
+OpenChamber runs its own local OpenCode server.
+
+Rule: instruction artifacts name only exposed tools. The file writers are
+`edit` and `write`; the shell tool is `shell`.
diff --git a/skill-templates/debug-instrumentation/SKILL.md b/skill-templates/debug-instrumentation/SKILL.md
index 23a967c..ce77a6d 100644
--- a/skill-templates/debug-instrumentation/SKILL.md
+++ b/skill-templates/debug-instrumentation/SKILL.md
@@ -22,7 +22,7 @@ Locate the areas of the codebase relevant to the bug. Look for:
 
 ### 2. Inject Strategic Logs (Instrumentation)
 
-Use the `apply_patch` tool to inject temporary, highly visible logging statements into the code.
+Use the `edit` tool to inject temporary, highly visible logging statements into the code.
 
 - Log _before_ and _after_ acquiring a lock or starting a transaction.
 - Log the current thread ID, process ID, or unique request ID.
@@ -31,7 +31,7 @@ Use the `apply_patch` tool to inject temporary, highly visible logging statement
 
 ### 3. Execution & Capture
 
-Run the application, test suite, or specific reproduction script using your `bash` tool.
+Run the application, test suite, or specific reproduction script using your `shell` tool.
 
 - Ensure you capture `stdout` and `stderr`.
 - If testing for a deadlock, set a strict timeout on your bash command (e.g., `timeout 10s npm test`) so the agent loop does not hang indefinitely.
@@ -46,5 +46,5 @@ Read the captured log output. Look for:
 
 ### 5. Implement Fix & Clean Up
 
-- Once the root cause is identified from the logs, use `apply_patch` to fix the actual bug.
+- Once the root cause is identified from the logs, use `edit` to fix the actual bug.
 - **CRITICAL:** You MUST remove all temporary `[DEBUG-TRACE]` logs you injected before finishing the task. Never commit temporary instrumentation to the codebase.
diff --git a/skill-templates/governance/templates/audit.md b/skill-templates/governance/templates/audit.md
index f32b6e4..e09482d 100644
--- a/skill-templates/governance/templates/audit.md
+++ b/skill-templates/governance/templates/audit.md
@@ -427,7 +427,7 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 
 1. **Evaluation**: Compare the active `AGENTS.md` text against the Target Audit Criteria. Also check if `docs/conventions.md` exists and contains both the DateTime Standard and SOLID Guidelines.
    - **Absent-File Policy (Mandatory)**: For `DESIGN.md`, `docs/architecture.md`, and `docs/data_model.md` — if any of these files do NOT exist in `[PROJECT_ROOT]`, audit them as `OPTIONAL — SKIPPED GRACEFULLY` with an explicit note. DO NOT flag as fatal errors, non-compliance violations, or missing-file failures. DO NOT hallucinate or scaffold them.
-2. **Patching**: If any constraints are missing, ambiguous, or incorrect in `AGENTS.md`, use the `apply_patch` tool to inject the exact missing rules. If `docs/conventions.md` is missing or incomplete, generate or patch it using the conventions template from Mode 1.
+2. **Patching**: If any constraints are missing, ambiguous, or incorrect in `AGENTS.md`, use the `edit` tool to inject the exact missing rules. If `docs/conventions.md` is missing or incomplete, generate or patch it using the conventions template from Mode 1.
 3. **Halt on Success**: If both files already comply 100%, DO NOT execute any write operations.
 
 ### Deprecated Sections Resolution
diff --git a/tests/test_agent_tool_gate.py b/tests/test_agent_tool_gate.py
index a41a5d2..3349549 100644
--- a/tests/test_agent_tool_gate.py
+++ b/tests/test_agent_tool_gate.py
@@ -11,7 +11,7 @@ Upstream evidence:
   Bash presence is necessary but not sufficient for restricted shapes. Docs note only, not a code fix.
 
 Exemption:
-- cognitive-discovery is a read-only subagent that denies edit plus bash by design; it is asserted as deny with reason.
+- cognitive-discovery is a read-only subagent that denies edit plus the shell action by design; it is asserted as deny with reason.
 """
 
 from pathlib import Path
@@ -40,31 +40,65 @@ def _extract_frontmatter(markdown_text: str) -> str:
     return ""
 
 
-def _permission_allows_bash(frontmatter: str) -> bool:
-    """Return True when permission block allows bash. Args: frontmatter extracted frontmatter text. Returns: True for allow, False for missing or deny."""
-    low = frontmatter.lower()
-    # Bash must be mentioned at all.
-    if "bash" not in low:
-        return False
-    # Explicit deny patterns fail closed.
-    if re.search(r"bash\s*:\s*deny", low):
-        return False
-    if re.search(r"bash.*deny\s*-\s*all", low):
-        return False
-    # Direct allow patterns pass.
-    if re.search(r"bash\s*:\s*allow", low):
-        return True
-    if re.search(r'"bash"\s*:\s*"allow', low):
-        return True
-    # Nested shape with bash key plus allow token in permission scope passes.
-    perm = low.split("permission", 1)[-1] if "permission" in low else low
-    return "allow" in perm
+def _parse_rules(frontmatter: str) -> list:
+    """Parse a V2 `permissions` array into ordered rule dicts.
+
+    Args: frontmatter extracted frontmatter text.
+    Returns: list of {action, resource, effect} dicts in declaration order.
+    """
+    rules = []
+    current = {}
+    in_permissions = False
+    for raw in frontmatter.splitlines():
+        line = raw.strip()
+        if line.startswith("permissions:"):
+            in_permissions = True
+            continue
+        if not in_permissions:
+            continue
+        if line.startswith("- "):
+            if current:
+                rules.append(current)
+            current = {}
+            line = line[2:].strip()
+        match = re.match(r"(action|resource|effect):\s*(.+)$", line)
+        if match:
+            current[match.group(1)] = match.group(2).strip().strip('"').strip("'")
+    if current:
+        rules.append(current)
+    return rules
+
+
+def _effective_effect(frontmatter: str, action: str, resource: str = "*"):
+    """Return the effective effect for an action after last-match resolution.
+
+    OpenCode evaluates permission rules in order and the last match wins, so
+    this mirrors that instead of scanning for the first allow or deny.
+
+    Args: frontmatter extracted text; action permission action; resource
+    concrete resource, defaulting to the wildcard.
+    Returns: "allow", "deny", "ask", or None when no rule matches.
+    """
+    effect = None
+    for rule in _parse_rules(frontmatter):
+        rule_action = rule.get("action", "")
+        rule_resource = rule.get("resource", "")
+        if rule_action not in ("*", action):
+            continue
+        if rule_resource not in ("*", resource):
+            continue
+        effect = rule.get("effect")
+    return effect
+
+
+def _permission_allows_shell(frontmatter: str) -> bool:
+    """True when the shell action resolves to allow under V2 last-match rules."""
+    return _effective_effect(frontmatter, "shell") == "allow"
 
 
 def _permission_denies(frontmatter: str, tool: str) -> bool:
-    """Return True when permission block denies the named tool. Args: frontmatter extracted text; tool tool name. Returns: True for deny."""
-    low = frontmatter.lower()
-    return bool(re.search(rf"{re.escape(tool)}\s*:\s*deny", low))
+    """True when the named action resolves to deny under V2 last-match rules."""
+    return _effective_effect(frontmatter, tool) == "deny"
 
 
 def _agent_files():
@@ -76,7 +110,7 @@ def _agent_files():
 
 
 def test_free_tier_agents_keep_bash():
-    """Free-tier-intended agents must allow bash; discovery exempt is skipped here."""
+    """Free-tier-intended agents must expose the shell tool; discovery exempt is skipped here."""
     # Collect failures for one clear assertion message.
     missing = []
     # Iterate every agent file to prevent silent additions without the gate.
@@ -85,18 +119,20 @@ def test_free_tier_agents_keep_bash():
             continue
         text = _read_text(agent_path)
         front = _extract_frontmatter(text)
-        if not _permission_allows_bash(front):
+        if not _permission_allows_shell(front):
             missing.append(agent_path.name)
-    assert not missing, f"free-tier-intended agents must allow bash, missing: {missing}"
+    assert not missing, (
+        f"free-tier-intended agents must allow shell, missing: {missing}"
+    )
 
 
 def test_read_only_agent_stays_deny():
-    """Read-only subagent must stay deny for edit plus bash by design."""
+    """Read-only subagent must stay deny for edit plus shell by design."""
     target = AGENTS_DIR / "cognitive-discovery.md"
     assert target.exists(), "read-only discovery agent file must exist"
     text = _read_text(target)
     front = _extract_frontmatter(text)
     # Discovery denies edit by design as read-only.
     assert _permission_denies(front, "edit"), "discovery must deny edit"
-    # Discovery denies bash by design as read-only.
-    assert _permission_denies(front, "bash"), "discovery must deny bash"
+    # Discovery denies the shell action by design as read-only.
+    assert _permission_denies(front, "shell"), "discovery must deny shell"
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 0111dd1..ec5a17f 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -439,7 +439,8 @@ def test_executor_rule_validation_and_git_restriction():
 def test_executor_frontmatter_denies_checkout():
     """Permission layer denies git checkout*, matching the ZAC claim."""
     executor = _read(EXECUTOR)
-    assert '"git checkout*": "deny"' in executor
+    assert 'resource: "git checkout*"' in executor
+    assert "effect: deny" in executor
 
 
 def test_executor_verification_gate_and_documentation_rule():
diff --git a/tests/test_tool_catalog_truth.py b/tests/test_tool_catalog_truth.py
new file mode 100644
index 0000000..e8a3e59
--- /dev/null
+++ b/tests/test_tool_catalog_truth.py
@@ -0,0 +1,147 @@
+# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
+"""Tool-catalog truth gates for the live instruction artifacts.
+
+Every instruction artifact the Hands reads must name only tools that exist
+in an OpenCode 2 session. A phantom name is a hard failure, not a style
+nit: the agent cannot call what does not exist, so it improvises with the
+only always-available writer (the shell), which is exactly the python-patch
+drift this gate exists to stop.
+
+The scan deliberately skips `DECISIONS.md` files and archive/history
+directories: those are historical evidence and must keep their verbatim
+records of retired tool names.
+"""
+
+from pathlib import Path
+
+REPO = Path(__file__).resolve().parent.parent
+EXECUTOR = REPO / "agents" / "cognitive-executor.md"
+DISCOVERY = REPO / "agents" / "cognitive-discovery.md"
+OPENCHAMBER = REPO / "docs" / "openchamber.md"
+
+# Every live instruction surface that a model may read as operating rules.
+SCAN_ROOTS = [
+    REPO / "skill-templates",
+    REPO / "AGENTS.md",
+    REPO / "README.md",
+    REPO / "prompts",
+    REPO / "agents",
+    REPO / "docs",
+]
+
+# Historical evidence keeps its own text; never rewrite an ADR to satisfy a gate.
+SKIP_DIR_NAMES = {"archive", "history", ".sessions"}
+SKIP_FILE_NAMES = {"DECISIONS.md"}
+
+# Tokens that resolve to no callable tool in this session.
+PHANTOM_TOKENS = (
+    "apply_patch",
+    "`bash` tool",
+    "@explore",
+    "@general",
+    "view_file",
+    "multiedit",
+    "str_replace_editor",
+    "create_file",
+)
+
+
+def _read(path: Path) -> str:
+    """Return a file's text as UTF-8."""
+    return path.read_text(encoding="utf-8")
+
+
+def _is_skipped(path: Path) -> bool:
+    """True when the path is historical evidence rather than live instruction."""
+    if path.name in SKIP_FILE_NAMES:
+        return True
+    return any(part in SKIP_DIR_NAMES for part in path.parts)
+
+
+def _iter_scan_files():
+    """Yield every live Markdown artifact under SCAN_ROOTS, sorted for stability."""
+    for root in SCAN_ROOTS:
+        if root.is_file():
+            if not _is_skipped(root):
+                yield root
+            continue
+        for path in sorted(root.rglob("*.md")):
+            if not _is_skipped(path):
+                yield path
+
+
+def test_no_phantom_tool_names_in_live_artifacts():
+    """No live artifact may name a tool the session cannot call."""
+    offenders = []
+    for path in _iter_scan_files():
+        text = _read(path)
+        for token in PHANTOM_TOKENS:
+            if token in text:
+                offenders.append(f"{path.relative_to(REPO)} -> {token}")
+    assert offenders == [], "phantom tool names in live artifacts:\n" + "\n".join(
+        offenders
+    )
+
+
+def test_executor_states_tool_surface():
+    """The executor must name its real writers and carry no tool archaeology.
+
+    A lean operator guide says what exists. It does not explain which model
+    gets which tool, and it never names a tool that cannot be called.
+    """
+    text = _read(EXECUTOR)
+    assert "`edit`" in text and "`write`" in text
+    assert "Your Tool Surface" in text
+    assert "Edit Recovery Protocol" in text
+    assert "`shell`" in text
+    assert "`subagent`" in text
+    # The topic is retired: no patch archaeology, no model-identity prose.
+    for retired in ("apply_patch", "GPT", "non-GPT", "patch parser"):
+        assert retired not in text, f"retired tool prose still in executor: {retired}"
+
+
+def test_openchamber_lists_session_tools():
+    """The OpenChamber doc must list what the session exposes and what it does not."""
+    text = _read(OPENCHAMBER)
+    for exposed in (
+        "openchamber_render",
+        "openchamber_secret",
+        "openchamber_notify",
+        "openchamber_web",
+    ):
+        assert exposed in text, f"exposed tool missing from docs: {exposed}"
+    assert "opencode" in text and "namespace" in text
+    assert "openchamber_schedule" in text
+    assert "Not exposed in this session" in text
+
+
+def test_agent_frontmatter_uses_v2_permissions():
+    """Agent frontmatter must use the V2 `permissions` array, not V1 fields.
+
+    V1 `permission` (singular map), `tools`, `temperature`, and action-scoped
+    `bash` entries are deprecated. A frontmatter that keeps them is read
+    through a compatibility path, so the rules silently stop matching the
+    live tool names.
+    """
+    for agent in (EXECUTOR, DISCOVERY):
+        text = _read(agent)
+        parts = text.split("---")
+        assert len(parts) >= 3, f"no frontmatter block in {agent.name}"
+        frontmatter = parts[1]
+        assert "permissions:" in frontmatter, f"missing V2 permissions in {agent.name}"
+        assert "action:" in frontmatter, f"no action rules in {agent.name}"
+        assert "effect:" in frontmatter, f"no effect values in {agent.name}"
+        for legacy in ("permission:", "tools:", "temperature", "bash:"):
+            assert legacy not in frontmatter, (
+                f"legacy V1 field {legacy!r} in {agent.name} frontmatter"
+            )
+
+
+def test_executor_keeps_zac_denies():
+    """The ZAC deny rules must survive the V2 rewrite, or staging is unguarded."""
+    frontmatter = _read(EXECUTOR).split("---")[1]
+    for command in ("git add", "git checkout", "git commit", "git push"):
+        assert f'resource: "{command}*"' in frontmatter, (
+            f"missing ZAC deny for {command}"
+        )
+    assert frontmatter.count("effect: deny") >= 4
```
<!-- END_GIT_DIFF -->
