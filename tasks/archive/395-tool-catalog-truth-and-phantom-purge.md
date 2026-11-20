# Task 395: Tool Catalog Truth and Phantom Name Purge

**File:** `tasks/completed/395-tool-catalog-truth-and-phantom-purge.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Finished:** 2026-11-11T05:59:40Z
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

**Manager accept (verbatim):** "Approved for closure" — closure authorized after
the edit-instruction audit closed F1 and F2.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `f512ad24eabfa62de0bc3ffec73663cad16b51a9`
<!-- END_GIT_DIFF -->
