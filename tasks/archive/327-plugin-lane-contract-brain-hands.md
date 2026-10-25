# Task 327: Plugin lane contract for Brain and Hands

**File:** `tasks/completed/327-plugin-lane-contract-brain-hands.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Make the three OpenCode plugin lanes (goal, todolist, smart-compact) first-class in the Brain/Hands contract: audit the prompt system and the context executor for gaps and wrong statements, then fix them so the Hands knows which plugins it owns, how to call each, why, and exactly when — while the Brain stays a tool-less, context-only planner with the Hands as its sole tool-bearing channel.

## Manager's Notes

Manager description (translated from Persian, intent preserved):

- The Brain is where all the members (personas) live. It only receives context — the codebase. It thinks, it walks steps, members may talk to each other, and it generates an XML map (نقشه).
- Automatic mode emits bare XML; manual mode emits fenced XML for the admin.
- The Hands is the executor — me, right now. The Hands has access to everything, including the Brain. The Hands is the one that talks to the Brain, hands it the map, receives the map back, converses, and does the gap-filling work.
- The Hands must use the goal plugin (the OpenCode goal plugin) — the goal tool.
- The Hands must use the todolist plugin tool.
- The Hands must use the smart-compact / compaction plugin tool.
- The context executor is detailed: it is the agent that I am right now, in OpenCode, and I have access to it.
- The Brain has access to no agent, no skill, and no tool. Its only communication channel is the input and output that the Hands provides for it.
- Therefore: when the Brain builds a todo list or a micro-milestone, the Hands must call the todowrite tool. When a goal is defined — for example when the Hands receives an XML implementation — the Hands must create a goal for it. When the context window fills up, or old turns are no longer useful, or the previous task is fully finished and the Manager wants to define a new task in the same session, the Hands must compact the previous turns.
- Directive: run an audit and review on the codebase against the description above, fix any defects found in the prompt system or fragments, and fix problems inside the context executor as well, so that from now on the Hands knows which plugins it has access to, how, why, and where it must call them. Produce a task, request the plan (نقشه) from the Brain for it with sufficient context, and show the plan to the Manager.

### Round 2 direction: Brain/Hands plugin separation (Manager order)

The Manager reviewed the Round-1 shaping and ordered a cleaner split: the system prompt must not know what a plugin is — it only says to create a todo list and a micro-list — while the context executor explains when to compact, when to open a goal, and that the todo list must always be used (and that a Brain-provided micro-list is managed with the todo list). The goal and compaction lanes are dropped from the prompt entirely. The Hands agrees with the assessment: the lanes first landed split across the prompt and the executor, which still taught the Brain plugin machinery; moving the full lane surface into the executor and leaving the prompt plugin-blind is the better scenario. Applied in this same task: the plugin-directives schema, the three lane blocks, and the trailing goal note are removed from the Hands protocol fragment; both persona mandates speak only of a todo list (micro-list); the compaction fragment is archived out of the manifest and the splitter tag list; the executor owns every lane with exact signatures, triggers, error strings, caps, and the parameter contract; the lane tests assert absence in the prompt and presence in the executor.

### Round 3 direction: prompts are for the LLM, not the auditor (Manager order)

The Manager reviewed the executor and ordered it enhanced as a prompt: it must not contain code references like the loop citations. The Hands audited `agents/` and all prompt fragments for file and line pointers and found them only in the executor's Goal Boundary (plus history-only DECISIONS records, which stay). Applied in this same task: the executor's Goal Boundary now states behavior only — no `src/` file, no line ranges, no server paths — while keeping every tool name, signature, trigger, and error string the Hands must match against; the Brain Bridge parenthetical is simplified the same way. The lane tests now pin the absence of code references in the executor instead of pinning corrected citations. No fragment changed, so the assembled artifact is untouched.

## Architecture Facts (audited, source of truth for the plan)

### Brain capabilities

- `brain_turn` builds a plain chat array `[{role: system}, history..., {role: user}]` and sends a body of `{model, input, reasoning, max_output_tokens}` — there is no `tools` key, so the Brain model can never call a tool (`mcp-brain-bridge/server.py:3192-3205`).
- The only structured channel is the XML allowlist `hands_discovery_task`, `hands_implementation_task`, `hands_combined_task`, `failure_report`, `hotfix` (`mcp-brain-bridge/server.py:174-181`). There is no goal/todo/compact tag.
- The Brain therefore has no way to reach the plugins by itself; every plugin action must be triggered by the Hands, either from its own judgment or from an instruction carried inside the XML the Brain emits.

### Plugin 1 — goal (opencode-goal-plugin, five agent tools)

- Tools: `goal_set` (title), `goal_block` (reason), `goal_evidence` (id, claim, files[], tests[{command, exitCode}]), `goal_complete` (no args), `goal_resume` (no args). Schemas in `/home/mohammad/Develop/Projects/opencode-goal-plugin/src/goal.ts:138-219`; tool bodies in `src/tools.ts:478-583`.
- Statuses: `active | complete | blocked | cleared | interrupted` (`src/state.ts:10-11`). `setObjective` always allowed and resets to active; `blockGoal` and `completeGoal` only from `active`; `resumeGoal` only from `interrupted` or `blocked` (`src/goal.ts:340-434`).
- State is per project directory, one goal shared by all sessions (`src/state.ts:92-102`); the file lease TTL is 120s (`src/state.ts:93`).
- `goal_set` is the only creator of a goal — no code path creates one automatically (`src/goal.ts:340` call sites: `src/index.ts:151`, `src/index.ts:607`, `src/tools.ts:178`).
- `goal_complete` is evidence-gated: every criterion needs at least one existing file citation inside the project dir and one test with `exitCode: 0`, else the message is `Complete blocked: <reason>. Add file citations plus passing tests to evidence.` (`src/verifier.ts:84-128`, `src/tools.ts:413-419`).
- The idle auto-continue loop sends a continuation prompt when the goal is `active` and the session idles (`src/loop.ts:458-492` gate, `src/loop.ts:552-853` handler, send at `src/loop.ts:780`). HQ forbids that lane: `agents/cognitive-executor.md:114` and `prompts/fragments/09-hands_protocols.md:166`.
- The stop file is read only at `<projectDir>/.opencode/STOP_GOAL` (`src/index.ts:284-296`); the prompt text in `agents/cognitive-executor.md:114` also claims a project-root `STOP_GOAL`, which the code never checks.
- After compaction, only an `active` goal is re-injected into the context (`src/index.ts:910-923`); a cleared or completed goal is never resurrected.
- `isSafeGoalTitle` rejects path-escape shapes (`..`, leading `/`, drive letters) but no reserved words (`src/goal.ts:312-331`).

### Plugin 2 — todolist (opencode-todolist 0.6.1)

- Tools: `todowrite` (complete list every call — it replaces; `[]` clears) and `todoread` (read back). Item fields: `content` (required), `status` (required, one of `pending|in_progress|completed|cancelled`), `priority` (optional, `high|medium|low`); `additionalProperties: false` (`.../opencode-todolist/src/index.ts:18-66`).
- Runtime caps: at most 100 todos per list, content at most 500 characters (`src/todos.ts:24-25`, `src/todos.ts:42-77`).
- Session-scoped and durable — it lives in plugin storage, so the list survives compaction and session restart; the plugin re-injects it into each request automatically (`src/index.ts:137-175`).
- `todowrite` output is discarded by smart-compact after a compaction (`discardTools.todowrite` → `Successfully updated todos.`, smart-compact `src/config.ts:56-60`), so the list itself must come from `todoread` or the automatic re-injection, never from a remembered transcript.

### Plugin 3 — smart-compact (@mokhtarabadi/opencode-smart-compact 0.2.1)

- Tool: `compact_context` with optional `keepTurns` (integer ≥ 0, default 0) and `mode` (`compact` | `trim`, default `compact`); `additionalProperties: false`; no required fields (`src/index.ts:196-232`, `src/actions.ts:25-40`).
- Also `read_omitted_content` (required `contentId`, e.g. `omitted-0001`), session-scoped (`src/index.ts:167-191`).
- Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats` (`src/index.ts:125-162`).
- It never mutates the stored transcript: it applies summaries and omissions to the model-visible messages per request; user messages stay verbatim (`src/index.ts:4-10`, `src/apply.ts:59`).
- Effect is async — summaries are stored now, the prune applies on the next request (`src/index.ts:225-229`).
- Project config: `.opencode/smart-compact.jsonc` with `enabled: true`; the plugin reads defaults → global → project (`src/config.ts:313-336`).

## Audit Findings (facts, with citations)

### F1 — the goal lane has no create trigger, so it never fires

- `agents/cognitive-executor.md:118` states the Hands performs "exactly two goal writes per goal: at block via `goal_block`, and at closure first `goal_evidence` then `goal_complete`". `goal_set` is never named as a write.
- The goal note in `prompts/fragments/09-hands_protocols.md:165` describes what the five tools are but is prose placed after `</hands_combined_task_template>` (line 163), outside every task template, so it is never an executable step in any phase.
- The Brain-side mandate `prompts/fragments/06-personas.md:5` and `:18` uses "Goal" only as an abstract work-unit concept and names no plugin tool. The Brain cannot call tools at all (`mcp-brain-bridge/server.py:3192-3205`), so the Brain can never create the goal either.
- Result: nothing in the system ever calls `goal_set`. Confirmed by the live state file: `.opencode/goal-state.json` holds one long-lived `interrupted` objective with `iterationCount: 0` and empty evidence criteria — created once by a manual slash command, never by the agent.

### F2 — the todolist lane fires only for implementation checklists, and never from a Brain-produced plan

- The only `todowrite` instruction is `prompts/fragments/09-hands_protocols.md:57`, inside the implementation template's `<execution_phase>`, and only "when the checklist has 2 or more steps".
- The discovery template (`09-hands_protocols.md:2-35`) and the combined template's `<conditional_implementation_phase>` (`:134-140`) contain no todowrite/todoread instruction at all.
- The Manager's model is the opposite direction of the current rule: the Brain produces the todo list or micro-milestone plan, and the Hands mirrors it into `todowrite`. Nothing tells the Hands to mirror a Brain-produced plan.

### F3 — the compaction lane is missing the task-boundary trigger

- `prompts/fragments/22-compaction_protocol.md:8` and `:18` tell the agent to call `compact_context` "when the context window is under pressure".
- `agents/cognitive-executor.md` (Compaction & Context Pressure, item 5) lists the triggers: context pressure high, 50+ steps without progress, before a plan-approval handoff, before QA or review turns carry a large diff.
- Missing: the task-boundary case — the previous task is finished and the Manager defines a new task in the same session, so the old turns should be compacted. Nothing in the prompt system covers it.

### F4 — stale and wrong statements in the prompt text

- `agents/cognitive-executor.md:114` cites "Goal idle handler src/loop.ts 205-437". The real code is `shouldContinue` at `src/loop.ts:458-492` and `handleSessionIdle` at `src/loop.ts:552-853`; lines 205-437 hold neither.
- `agents/cognitive-executor.md:114` says the loop stops "If STOP_GOAL file exists at root or .opencode/STOP_GOAL". The code checks only `<projectDir>/.opencode/STOP_GOAL` (`src/index.ts:284-296`); the project root path is never read.
- `prompts/fragments/09-hands_protocols.md:165` lists the Manager slash inputs as `/goal <objective>`, `/goal status`, `/goal block <reason>`, `/goal complete`, `/goal clear`. The parser also accepts `/goal resume` and `/goal evidence <args>` (`src/goal.ts:89`, `src/goal.ts:113`).
- `agents/cognitive-executor.md:116` says "Goal slash inputs are exact-only: status plus clear plus complete accept no extras" — it omits `<objective>`, `block <reason>`, `resume`, and `evidence`.
- The same sentence says the loop must not auto-send "inside HQ sessions", but the plugin registers its idle handler for every project it loads in (`src/index.ts:782-857`); nothing in the plugin is HQ-aware. In HQ the only brake is the stop file, and HQ currently has no `.opencode/STOP_GOAL` — the file is git-ignored, so it cannot be relied on as a shipped control.

### F5 — no Brain-to-Hands channel for plugin intents

- The XML allowlist (`mcp-brain-bridge/server.py:174-181`) has no goal/todo/compact tag, and the three task templates carry no phase instruction that mentions the plugins as an executable step (only the two prose notes at `09-hands_protocols.md:57` and `:165-166`).
- Consequence: the Brain can state an intent in prose inside the XML, but the Hands has no rule that says "when the map carries a plan, mirror it into `todowrite`" or "when the map defines an objective, open a goal".

### F6 — the plugin surfaces in the prompt text are not the whole surface

- `todowrite` caps (100 items, 500-char content), the durable session-scoped storage, the automatic re-injection, and the fact that smart-compact replaces `todowrite` output with a fixed notice are all absent from the prompt system.
- The goal evidence gate details (file must exist, `exitCode: 0` required) are stated in prose at `09-hands_protocols.md:165` but not as a step anywhere.
- The `compact_context` async semantics are stated in `22-compaction_protocol.md:8` but the "do not re-call to verify" rule and the "recover with `todoread`, not memory" rule are not attached to the todolist lane.

### F7 — the installed smart-compact copy is behind its source repo

- The installed package is 0.2.1; the installed `src/` matches repo commits `b96661cc`/`c800af8e`. The repo HEAD adds `src/awareness.ts` and a `config.awareness` section (`src/config.ts:89`) with an advisory context-pressure reminder that is not in the installed copy. The project config `.opencode/smart-compact.jsonc` sets only `enabled: true`.
- Refreshing the install is a global-config action outside this repo, so it is out of scope here; it is recorded so the plan does not assume awareness-driven pressure warnings exist.

## Local TODOs (Round 3: LLM-clean prompts)

- [x] Audit `agents/` and all prompt fragments for code references; strip them from the executor Goal Boundary keeping behavior
- [x] Simplify the executor Brain Bridge server path parenthetical
- [x] Update the lane tests (drop file:line pins, assert no code refs in the executor)
- [x] Verify the assembled artifact is untouched, run the gates, record Round-3 evidence
- [x] Update the sibling docs and CHANGELOG, stage, and move back to tasks/qa

## Acceptance Criteria (Round 3: LLM-clean prompts)

- [x] No file or line citation remains in the executor or any prompt fragment (DECISIONS history records exempt)
- [x] Every lane behavior is preserved: tool names, signatures, triggers, error strings, caps, and the parameter contract
- [x] The lane tests assert the absence of code references in the executor, and the prompt-sync suite passes with exit code 0
- [x] The assembled artifact is byte-identical and untouched by Round 3

## Verification Evidence

- **Test command:** rtk test uv run --with pytest python -m pytest tests/test_prompt_sync.py -q
- **Expected result:** every prompt-sync check passes, including the new plugin-lane assertions, and the byte-identical rebuild check is green
- **Actual result:** exit 0, 16 passed (including the plugin-blind absence test and the executor-owned lane test)
- **Exit code:** 0
- **Test command:** rtk test uv run --with pytest python -m pytest ../tests/ -q (run from `mcp-context-server/`, the env that carries the `mcp` dependency)
- **Expected result:** the full suite is green except the 8 pre-existing environmental failures reproduced on pristine HEAD
- **Actual result:** exit 1, 8 failed, 521 passed. The same 8 tests fail identically on a pristine HEAD worktree (`/tmp/hq_head_check`, 8 failed / 519 passed) — 6 `mcp` module import errors plus `test_system_prompt_split_assemble_round_trip` and `test_lint_system_prompt_sync_clean`, both pre-existing per the release record. Delta is +2 passing, the two new lane gates.
- **Exit code:** 1
- **Test command:** python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check.md && diff /tmp/check.md system-prompt.md
- **Expected result:** the assembled artifact is byte-identical to the committed `system-prompt.md`
- **Actual result:** superseded by Round 2 (Round-1 size was 119186; Round-2 size is 108094, recorded below)
- **Exit code:** 0
- **Test command:** uv run python /tmp/rt_delta.py (split→assemble drift measured against pristine HEAD)
- **Expected result:** my change introduces no new round-trip drift
- **Actual result:** superseded by Round 2 (the 20-tag splitter changes the HEAD baseline; the Round-2 measurement is recorded below)
- **Exit code:** 0
- **Test command:** lint_markdown (06-personas.md, 09-hands_protocols.md, 22-compaction_protocol.md, 01-system_version.md, agents/cognitive-executor.md) + lint_system_prompt_sync
- **Expected result:** all lint calls pass
- **Actual result:** all five fragment and agent files pass Markdown linting; `system-prompt.md is in sync with prompts/`
- **Exit code:** 0
- **Test command:** git check-ignore --quiet .opencode/STOP_GOAL; git status --porcelain -uall
- **Expected result:** the marker is not ignored (exit 1) and shows as untracked, ready to be staged
- **Actual result:** exit 1 (not ignored); `?? .opencode/STOP_GOAL` present in status. The root `STOP_GOAL` pattern stays ignored (`.gitignore:65`), the negation at `.gitignore:68` re-includes only the `.opencode/` path.
- **Exit code:** 0
- **Test command (Round 1, SUPERSEDED):** grep -rn "plugin_directives" prompts/fragments/ agents/ system-prompt.md; grep -rn "goal_set" prompts/fragments/ agents/
- **Expected result:** hits in both fragment sources and the assembled prompt
- **Actual result:** superseded by Round 2 — `plugin_directives` no longer exists anywhere; the separation test asserts its absence
- **Exit code:** n/a (superseded)
- **Test command:** python3 scripts/prompt-build/assemble_system_prompt.py && python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check.md && diff /tmp/check.md system-prompt.md
- **Expected result:** the artifact regenerates from the reduced manifest and is byte-identical to a fresh assemble
- **Actual result:** exit 0, empty diff, 108094 bytes both sides (down from 119186 — the prompt is ~11KB lighter)
- **Exit code:** 0
- **Test command:** grep -c -E "goal_set|goal_block|goal_evidence|goal_complete|goal_resume|todowrite|todoread|compact_context|read_omitted_content|keepTurns|plugin_directives|smart-compact|magic-compact|tool_channel|goal-state\.json|goal-evidence\.json|STOP_GOAL|<compaction_protocol>|loop\.ts:458|loop\.ts:552" system-prompt.md; grep -c "micro-list" system-prompt.md; grep -c "MICRO-TASK CHECKLIST" system-prompt.md
- **Expected result:** zero plugin leaks; the plain-language micro-list and checklist vocabulary remains
- **Actual result:** 0 leaks; `micro-list` 3 hits; `MICRO-TASK CHECKLIST` 1 hit
- **Exit code:** 0
- **Test command:** rtk test uv run --with pytest python -m pytest tests/test_prompt_sync.py -q
- **Expected result:** all 16 checks pass, including the plugin-blind absence test and the executor-owned lane test
- **Actual result:** exit 0, 16 passed in 0.16s
- **Exit code:** 0
- **Test command:** rtk test uv run --with pytest python -m pytest ../tests/ -q (run from `mcp-context-server/`)
- **Expected result:** the full suite is green except the 8 pre-existing environmental failures reproduced on pristine HEAD
- **Actual result:** exit 1, 8 failed, 521 passed — the identical 8 failures as pristine HEAD (6 `mcp` module import errors plus the split round-trip and the lint-sync test, both pre-existing per the release record)
- **Exit code:** 1
- **Test command:** uv run python /tmp/rt_delta.py (split-to-assemble drift measured with the updated 20-tag splitter)
- **Expected result:** the tag removal introduces no new round-trip drift
- **Actual result:** exit 0; current drift 85 lines, all within the pre-existing night-mode and language-policy gap; new drift lines introduced by this change: 0
- **Exit code:** 0
- **Stack-skill binding:** root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, Package.swift, nest-cli.json, vite.config] matched=[] reason="prompt-text and Markdown contract change plus a Python test file; no app stack skill matches, so no stack Strict Tooling Gate applies"

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

**Corrected verification command:** the implementation XML mandated `rtk test uv run tests/test_prompt_sync.py -q`. That form is a false green: `uv run` executes the file as a script, the file has no `__main__` block, and it exits 0 without running a single assertion. The working form is `rtk test uv run --with pytest python -m pytest tests/test_prompt_sync.py -q`, which is what the evidence above records.

- **Test command:** grep -c -E "src/[a-z_]+\.(ts|py)|per lines [0-9]|loop\.ts|goal\.ts|tools\.ts|state\.ts|verifier\.ts|index\.ts|evidence\.ts|server\.py" agents/cognitive-executor.md; grep -c -E "goal_set|todowrite|compact_context|read_omitted_content|STOP_GOAL" agents/cognitive-executor.md
- **Expected result:** zero code references remain; the lane behavior (9 tool/path hits) is intact
- **Actual result:** exit 0; code refs 0, behavior hits 9
- **Exit code:** 0
- **Test command:** rtk test uv run --with pytest python -m pytest tests/test_prompt_sync.py -q
- **Expected result:** all 16 checks pass, including the no-code-references executor test and the plugin-blind prompt test
- **Actual result:** exit 0, 16 passed in 0.13s
- **Exit code:** 0
- **Test command:** python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check4.md && diff /tmp/check4.md system-prompt.md
- **Expected result:** no fragment changed in Round 3, so the artifact is untouched at 108094 bytes
- **Actual result:** exit 0, empty diff, 108094 bytes both sides
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** the prompt system drives every Brain and Hands turn, so a wrong lane rule corrupts behavior for the whole platform. A second risk is the goal idle loop: HQ's rule that the loop must not auto-send is enforced by prompt text only, and HQ has no committed `.opencode/STOP_GOAL`, so opening a goal inside HQ may let the plugin's idle handler inject continuation prompts that fight the Brain Bridge.
- **Rollback plan:** every change lands in tracked source files under `prompts/fragments/` and `agents/`, so `git checkout -- <paths>` plus a re-assemble restores the prior prompt; the system prompt version bump is reversible the same way. No plugin source in the external `opencode-goal-plugin` repo is modified by this task.

---

## Execution Log & Reasoning

Seat Check: prompt-contract design plus an implementable step list → Software Architect (lead) + Senior Programmer (step list). Trigger words fired: "contract" (Architect), "API design" absent, no UX keyword hit, no performance keyword hit. Skipped seats: UI/UX Designer (no user-visible surface), Sprint Strategist (no capacity question), QA Engineer and Code Reviewer (both run after implementation, not at plan). Brainstorm: not required — the task carries audited file:line findings F1-F7, no cross-disciplinary ambiguity, and prompt-text changes are reversible via git.

Plan verdict: Brain returned `REPORT` (blueprint, no XML block) on the first planning turn. No discovery round was needed — every fact was supplied in the fed-context block, so the plan cites file:line ground truth rather than assumptions. Blueprint accepted as the implementation basis, subject to the Manager's three decisions (Q1/Q2/Q3 below) and the plan-approval gate.

Fed context pinned for the plan turn: `mcp-brain-bridge/server.py:3192-3205` (Brain has no tools key) and `:174-181` (XML allowlist); `agents/cognitive-executor.md:114`, `:116`, `:118` (goal boundary claims); `prompts/fragments/09-hands_protocols.md:57` (only todowrite rule), `:165-166` (goal prose note outside the templates); `prompts/fragments/22-compaction_protocol.md:8`, `:18` (compaction triggers); `prompts/fragments/06-personas.md:5`, `:18` (Brain-side "Goal" metaphor); goal plugin `src/goal.ts:138-219`, `:340-434`, `src/tools.ts:94`, `:478-583`, `src/state.ts:10-11`, `:92-102`, `src/verifier.ts:84-128`, `src/loop.ts:458-492`, `:552-853`, `:780`, `src/index.ts:284-296`, `:782-857`, `:910-923`; todolist `src/index.ts:18-66`, `:137-175`, `src/todos.ts:24-25`, `:42-77`; smart-compact `src/index.ts:125-162`, `:167-191`, `:196-232`, `:225-229`, `src/actions.ts:25-40`, `src/apply.ts:59`, `src/config.ts:56-60`.

Blueprint summary (Software Architect + Senior Programmer):

- **Channel choice (one, justified):** a new XML sub-tag `<plugin_directives>` inside the EXISTING task templates — no `mcp-brain-bridge/server.py` change, because the sub-tag rides inside already-allowlisted top-level blocks. Schema: `<goal_objective>`, `<todo_mirror>`, `<compact_hint>`.
- **Brain side:** `prompts/fragments/06-personas.md` — state plainly that the Brain has no agents, no skills, and no tools, that the XML allowlist is its only structured channel, and that the Hands is its only tool-bearing counterpart; the Brain expresses plugin intent only through `<plugin_directives>`.
- **Hands side:** three executable lanes (not prose notes) in `prompts/fragments/09-hands_protocols.md` and `agents/cognitive-executor.md`. Lane G (goal) restores the missing `goal_set` create trigger and states the full lifecycle plus the evidence gate and the busy-lease retry. Lane T (todolist) states the mirror trigger and the surface facts (replace-whole-list, 100-item and 500-char caps, durable session storage, auto re-injection, smart-compact discarding the tool output). Lane C (smart-compact) adds the missing task-boundary trigger and states the async effect and the `omitted-NNNN` retrieval rule.
- **Corrections:** C1 loop.ts range, C2 STOP_GOAL path, C3 missing slash inputs, C4 the "exact-only" list, C5 the HQ idle-loop claim replaced with what the code actually does.
- **Version and tests:** bump `prompts/fragments/01-system_version.md` 9.62.0 → 9.63.0, regenerate `system-prompt.md` via `scripts/prompt-build/assemble_system_prompt.py`, verify byte-identical, and add lane assertions to `tests/test_prompt_sync.py` (no test pins any goal or todolist literal today).
- **Manager decisions requested by the Brain:** Q1 HQ goal policy (recommended default in the blueprint: forbid `goal_set` inside HQ until a code-level HQ guard lands), Q2 `todowrite` scope (recommended: mirror ANY Brain plan with 2+ steps), Q3 task-boundary compact depth (recommended: `keepTurns 0, mode compact`).

Assumption A1: the blueprint's Q1 recommendation is recorded but NOT taken as decided — the Manager owns that choice, and it changes behavior for the whole platform. The implementation waits for the plan-approval gate.

Round 2 (separation): the Manager's word is the plan — no second Brain planning turn needed. The Manager ordered the prompt plugin-blind and the executor lane-complete, and the Hands agreed on the record. Applied: removed the two `tool_channel` blocks from `06-personas.md` (2 replacements), rephrased both Goal-Oriented mandates to todo-list (micro-list) language, added one context-executor boundary sentence to the Senior Programmer behavior; removed the directives schema, Lane G, both Lane T blocks, and the trailing three-line goal note from `09-hands_protocols.md`, and plain-worded the checklist sentence; moved `22-compaction_protocol.md` to `prompts/archive/` with an archival header, removed it from `prompts/manifest.txt`, dropped it from the splitter `TOP_LEVEL_TAGS` (21 to 20 across 7 comment and code sites), and updated both prompt READMEs; expanded the executor's Goal Boundary (WHY line, exact signatures, WHEN triggers, evidence-gate and busy-lease strings, title safety, lease scope), Micro-Task Tracking (caps, durable storage, todoread recovery), and Compaction items (parameter contract, plugin-directives sentence replaced); rewrote the lane tests (removed the compaction-presence test, added the plugin-blind absence test, rewrote the lane test as executor-owned, extended the executor citation test). Regenerated: 119186 to 108094 bytes, byte-identical rebuild green, zero tool-name leaks in the artifact, prompt-sync 16 passed, full suite 521 passed with the same 8 pre-existing failures, zero new split-to-assemble drift lines. The earlier edit failures in this file were a `CHANGOG.md` typo in my own added TODO block — fixed, after which block edits matched.

Autopilot locked (Manager order "Auto pilot mode"): the Hands chains QA/review turns directly under this task_id without Manager ferrying; closure still needs the exact approval word; ZAC holds.

Review turn (autopilot, stage review, diff attached): Code Reviewer returned technical approval with PO_REVIEW_PENDING. Strengths F1-F4 confirm the separation, the executor lanes, the corrected citations with the tracked stop marker, and the byte-identical rebuild. One low-severity issue I1: the archived compaction copy carries a lane block that reads as normative in a history-only file; recommendation R1 (optional cleanup): add a superseded pointer or revert to header-only. Applied R1 as the pointer variant — the archived Lane C paragraph now opens with a superseded marker naming the executor as the live lane. Re-verified after the fix: prompt-sync 16 passed, assemble byte-identical at 108094 bytes (the archived file is not in the manifest, so the artifact is untouched). Worktree diff hash unchanged for all code paths; only the archived history file gained one marker line. Tooling note: stage_and_inject_diff errored twice on the qa-path file (once git-add 128 on the already-staged rename old-pathspec, once FileNotFoundError on a file that exists) — in both cases git status confirmed the intended staging state was actually achieved, so the re-stage goals were met by verification rather than by a clean tool return.

Round 3 (LLM-clean prompts): the Manager's word is the plan — no Brain planning turn needed. The earlier review verdict was set aside; the task reopened for this round with a fresh review after. Audit method: two ripgrep passes over `agents/` and `prompts/fragments/` for `src/`, server paths, and line ranges — hits only in the executor Goal Boundary plus the Brain Bridge parenthetical, and in history-only DECISIONS records which stay. Six surgical rewrites, behavior preserved verbatim (every tool name, signature, trigger, cap, and error string still present, grepped 9 behavior hits after the strip).

Round 3 re-review (autopilot): Code Reviewer technically approved again with PO_REVIEW_PENDING. Strengths F1-F4 confirm zero code references, intact lane behavior, enforcing tests, and the untouched byte-identical artifact. One low optional note I1: an internal self-reference (`lines 95-104`) remained in the Goal Boundary — applied R1 by naming the Compaction section instead; internal line-range count in the executor is now 0 and prompt-sync stays 16 passed.

Manager accept: Approved for closure

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `49c7bf74641aefcbb79e1a555e2c7a5420172c27`
<!-- END_GIT_DIFF -->
