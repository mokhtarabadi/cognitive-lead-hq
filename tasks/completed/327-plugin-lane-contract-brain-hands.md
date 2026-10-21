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
```diff
diff --git a/.gitignore b/.gitignore
index e31b4c0..8f2e594 100644
--- a/.gitignore
+++ b/.gitignore
@@ -64,4 +64,6 @@ htmlcov/
 .opencode/goal-evidence.json
 STOP_GOAL
 .opencode/STOP_GOAL
+# Task-boundary idle-loop brake stays tracked
+!.opencode/STOP_GOAL
 
diff --git a/.opencode/STOP_GOAL b/.opencode/STOP_GOAL
new file mode 100644
index 0000000..e69de29
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 69e8818..dd4dee6 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,22 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Added
+
+- **Plugin lane contract for Brain and Hands (Task 327):** the goal, todolist, and smart-compact lanes become executable steps instead of trailing prose. Lane G (goal) restores the missing `goal_set` create trigger and states the full lifecycle with the evidence gate and the busy-lease retry; Lane T (todolist) mirrors ANY Brain-produced plan with 2 or more steps, including the combined conditional phase, and states the replace-whole-list semantics, the 100-item and 500-char caps, the durable session storage, and the automatic re-injection; Lane C (smart-compact) adds the task-boundary trigger (previous task finished, new task in the same session) and states the async effect plus the `omitted-NNNN` retrieval rule. (Round 2 superseded the in-prompt lanes: the prompt is now plugin-blind and the executor owns every lane — see the separation entries below.)
+- **Brain-side vocabulary reduced to plan and checklist (same task, Round 2):** both persona mandates speak only of a todo list (micro-list) with verification gates, plus a single sentence stating that how the Hands tracks and executes them is defined solely in the context executor. No tool, plugin, or channel names remain in the prompt.
+- **Tracked idle-loop brake (same task):** `.opencode/STOP_GOAL` is now a tracked marker (the `.gitignore` negation lifts the ignore for that path while the root `STOP_GOAL` stays ignored), so the goal plugin's idle auto-continue is braked by a committed control instead of a prompt promise. The marker stops only the idle loop and never blocks the five agent tools.
+- **Brain/Hands plugin separation (same task, Round 2):** the system prompt is now plugin-blind — the `plugin_directives` schema, the three lane blocks, and the trailing goal note are removed from the Hands protocol fragment, both persona mandates speak only of a todo list (micro-list) with a single context-executor boundary sentence, and the compaction fragment is archived out of the manifest and the splitter tag list; the executor instead owns the full lane surface (exact tool signatures, WHEN triggers, evidence-gate and busy-lease strings, todolist caps, compact parameter contract). The assembled prompt shrinks and carries zero tool names.
+- **Lane tests assert the separation (same task):** `test_shipped_prompt_is_plugin_blind` fails on any tool name, plugin name, state path, or channel tag leaking into the assembled artifact, and `test_executor_owns_all_three_plugin_lanes` pins the full lane surface in the context executor; the obsolete compaction-protocol presence test is removed.
+- **Executor reads as behavior only (same task, Round 3):** every file and line citation is stripped from the context executor's Goal Boundary (history records keep theirs); the lane tests now assert the absence of code references in the executor instead of pinning corrected citations. No fragment changed, so the assembled artifact is untouched.
+
+### Fixed
+
+- **Stale plugin citations corrected (same task):** the executor's `src/loop.ts 205-437` reference now names the real gate (`shouldContinue` at `src/loop.ts:458-492`) and handler (`handleSessionIdle` at `src/loop.ts:552-853`); the stop-file claim now states that the code reads only the projectDir `.opencode/STOP_GOAL` path (`src/index.ts:284-296`) and that the project-root path is never read; the "exact-only" slash list now covers the full parser surface (objective, block reason, resume, and evidence accept arguments; status, clear, and complete are exact-only); the missing `/goal resume` and `/goal evidence` slash inputs are documented; the goal lane's "exactly two goal writes" rule becomes three writes plus resume, matching the restored `goal_set` trigger.
+- **Compaction task-boundary gap closed (same task):** the previous task being finished and the Manager defining a new task in the same session now triggers `compact_context` with `keepTurns` 0 and `mode` `compact`, and the todo list is recovered with `todoread` rather than from a remembered transcript.
+- **False-green verification command (same task):** the `uv run tests/test_prompt_sync.py` form ran the file as a script with no main block and exited 0 without executing a single assertion; the working form is `uv run --with pytest python -m pytest tests/test_prompt_sync.py -q` (16 passed).
+- **Compaction fragment retired (same task):** `prompts/fragments/22-compaction_protocol.md` moved to `prompts/archive/` with an archival header, removed from `prompts/manifest.txt`, and dropped from the splitter `TOP_LEVEL_TAGS` (21 to 20); split-to-assemble drift introduces zero new lines versus the pre-existing night-mode and language-policy gap.
+
 ## [9.62.0] - 2026-10-19
 
 ### Added
diff --git a/README.md b/README.md
index bedddb7..ebcef32 100644
--- a/README.md
+++ b/README.md
@@ -478,7 +478,7 @@ opencode --agent cognitive-executor
 
 ### OpenCode Plugins
 
-Three plugins: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) — lossless, V2-native context compaction, maintained in its own repo. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Smart Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. It never mutates the stored transcript — it stores a per-session compaction state and applies it to the model-visible messages per request. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`. Install with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` (the Git spec, until it is published to npm); full guide in [`docs/compaction.md`](docs/compaction.md). Plus **`goal`** (`opencode-goal-plugin`, maintained in its own repo) — tracks one long-running objective in `.opencode/goal-state.json` with evidence in `.opencode/goal-evidence.json`: `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal complete` (needs file citations plus passing tests), `/goal clear` (Manager lane; agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`, never write the state files directly). Install with `opencode plugin add github:mokhtarabadi/opencode-goal-plugin` (the Git spec, `opencode-goal-plugin` once published to npm). Plus **`todolist`** (`opencode-todolist`) — restores the V1 session todo tools (`todowrite`/`todoread`) removed in V2, with a live TUI sidebar strip. Install with `opencode plugin add opencode-todolist` and enable the strip via `plugins` in `~/.config/opencode/cli.json`.
+Three plugins: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) — lossless, V2-native context compaction, maintained in its own repo. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Smart Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. It never mutates the stored transcript — it stores a per-session compaction state and applies it to the model-visible messages per request. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`. Install with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` (the Git spec, until it is published to npm); full guide in [`docs/compaction.md`](docs/compaction.md). Plus **`goal`** (`opencode-goal-plugin`, maintained in its own repo) — tracks one long-running objective in `.opencode/goal-state.json` with evidence in `.opencode/goal-evidence.json`: `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal resume`, `/goal evidence <args>`, `/goal complete` (needs file citations plus passing tests), `/goal clear` (Manager lane; agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`, never write the state files directly). The agent creates the goal with `goal_set` when an objective is defined, blocks with `goal_block`, records proof with `goal_evidence` before closing, and resumes with `goal_resume` after a block or interruption. Install with `opencode plugin add github:mokhtarabadi/opencode-goal-plugin` (the Git spec, `opencode-goal-plugin` once published to npm). Plus **`todolist`** (`opencode-todolist`) — restores the V1 session todo tools (`todowrite`/`todoread`) removed in V2, with a live TUI sidebar strip. Install with `opencode plugin add opencode-todolist` and enable the strip via `plugins` in `~/.config/opencode/cli.json`.
 
 ---
 
diff --git a/agents/DECISIONS.md b/agents/DECISIONS.md
index 2deed67..9a88724 100644
--- a/agents/DECISIONS.md
+++ b/agents/DECISIONS.md
@@ -7,7 +7,35 @@
 - **Consequences:** All future structural or contract changes must be recorded here.
 - **Rollback:** N/A (baseline adoption).
 
+## Plugin lane contract and the tracked idle-loop brake
+
+Date: 2026-10-21
+Status: accepted
+Context: The context executor is the agent's own instruction file, so it is where the Hands learns which plugins it owns. Its goal boundary named only two goal writes and never `goal_set`, cited a `src/loop.ts` range that holds neither the gate nor the handler, claimed the stop file is read at the project root when the code reads only the projectDir `.opencode/STOP_GOAL` path, and asserted a rule the plugin does not enforce anywhere. Because the goal plugin registers its idle handler for every project it loads, opening a goal inside HQ could let the plugin inject continuation prompts that fight the Brain Bridge.
+Decision: Correct the citations to the real ones, replace the prompt-enforced idle ban with the honest description of what the plugin does, add the missing `goal_set` create trigger and the task-boundary compaction trigger, and ship a tracked `.opencode/STOP_GOAL` marker so the brake is a committed control rather than a local accident. The marker brakes only the idle loop and never blocks the five agent tools.
+Consequences: The executor's goal lifecycle is three writes plus resume, the compaction lane covers the task boundary, and the idle loop stays silent in HQ by an actual mechanism instead of a promise. The root `STOP_GOAL` stays git-ignored; the `.opencode/STOP_GOAL` path is negated in `.gitignore` so the marker is tracked.
+Rollback: Revert the executor wording and the `.gitignore` negation, delete the tracked marker, and re-run the assembler.
+
+## Lanes consolidated in the executor, prompt goes blind
+
+Date: 2026-10-21
+Status: accepted
+Context: The lane surface first landed split across the prompt fragments and the executor, which still taught the Brain plugin machinery. The Manager ordered full separation: the prompt emits only a plan and checklist, the executor owns every lane.
+Decision: Move the remaining lane knowledge (exact tool signatures, WHEN triggers, evidence-gate and busy-lease strings, todolist caps, compact parameter contract, the Brain-has-no-tools WHY) into the executor's Goal Boundary, Micro-Task Tracking, and Compaction sections, and strip the same knowledge from the prompt fragments.
+Consequences: The executor is the single file the Hands needs for which plugins it owns, how to call each, why, and when. The prompt carries zero tool names.
+Rollback: Revert the executor sections and restore the fragment wording, then re-run the assembler.
+
+## Prompts are for the LLM, not the auditor
+
+Date: 2026-10-21
+Status: accepted
+Context: The executor carried file and line citations into the Goal Boundary. Those pointers serve human audits, but the executor is read by the agent every turn — for the LLM they are unverifiable noise.
+Decision: Strip every code reference (source files, line ranges, server paths) from the executor, keeping all tool names, signatures, triggers, caps, and error strings. History records (DECISIONS, CHANGELOG, task files) keep their citations; the lane tests now assert the absence of code references in the executor.
+Consequences: The executor reads as behavior only. A regression that re-adds a pointer fails the prompt-sync gate.
+Rollback: Restore the citations from git history.
+
 ## Free-tier bash gate documented
+
 Date: 2026-10-17
 Status: accepted
 Context: Upstream free-tier models discriminate by request-body tool list. Agents omitting bash receive 403 FreeTierError on free-tier models.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index ca3f2b3..b28a74e 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -105,17 +105,18 @@ Context is finite. Two layers keep long sessions productive, and the agent's dur
 Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
 
 3. **Survival contract.** Keep the task file holding: the active task id and Kanban lane, the pinned `[fed-context]` block with citations, the current persona/seat, the locked mode (manual or autopilot), the latest staged diff hash, open blockers, and the next action. Resume from that file after any compaction — never from a summary.
-4. **Trigger it yourself, or hand off the command.** The agent cannot run the `/magic-*` slash commands, but it CAN call the `compact_context` tool directly — prefer that when context pressure is high (pass `keepTurns` to protect recent turns, `mode: "trim"` to prune tool output only), state one line about it, then continue from the task file. Effect is async (stored now, prunes next request) — do not re-call to verify. In autopilot never ask the Manager to run slash commands; call it yourself and chain the next turn. Fall back to recommending a `/magic-compact` run to the Manager only when a tool call is not available in manual mode. Do not edit compaction config files.
-5. **Call it before heavy payloads, not after stalling.** Invoke `compact_context` yourself at these triggers: context pressure is high, 50+ steps ran without measurable progress, before a plan-approval handoff, and before QA or review turns carry a large diff. Use `mode: "trim"` when only tool output is bulky and full `compact` when turns are stale. Never re-run a source tool for pruned output — retrieve it with `read_omitted_content` by Content ID. The Brain bridge needs no change: the executor already holds direct `compact_context` access, so no Brain mention is added.
+4. **Trigger it yourself, or hand off the command.** The agent cannot run the `/magic-*` slash commands, but it CAN call the `compact_context` tool directly — prefer that when context pressure is high (pass `keepTurns` to protect recent turns, `mode: "trim"` to prune tool output only), state one line about it, then continue from the task file. Contract: `keepTurns` is a non-negative integer defaulting to 0, `mode` is `compact` or `trim` defaulting to `compact`, neither is required; `read_omitted_content` takes a session-scoped Content ID such as `omitted-0001`. Effect is async (stored now, prunes next request) — do not re-call to verify. In autopilot never ask the Manager to run slash commands; call it yourself and chain the next turn. Fall back to recommending a `/magic-compact` run to the Manager only when a tool call is not available in manual mode. Do not edit compaction config files.
+5. **Call it before heavy payloads, not after stalling.** Invoke `compact_context` yourself at these triggers: context pressure is high, 50+ steps ran without measurable progress, before a plan-approval handoff, before QA or review turns carry a large diff, plus the task-boundary trigger from the compaction protocol. Use `mode: "trim"` when only tool output is bulky and full `compact` when turns are stale. Never re-run a source tool for pruned output — retrieve it with `read_omitted_content` by Content ID. The Brain never names tools or plugins; it emits only a plan and checklist, and this executor maps them onto `compact_context`.
 
 ### Goal Plugin Boundary - global helper, not truth
 
 - HQ task file in tasks backlog plus in-progress plus qa plus completed remains single source of truth.
-- File at .opencode/goal-state.json is external scratch only and never replaces Kanban state per src/index.ts 39-45 and src/state.ts 54 and 61-64.
-- Goal idle handler src/loop.ts 205-437 MUST NOT auto-send inside HQ sessions. Brain Bridge remains sole automation path with ZAC plus WIP3 plus approval gates per lines 24-52. If STOP_GOAL file exists at root or .opencode/STOP_GOAL, loop MUST stop immediately per src/limits.ts 25-26.
-- Goal slash inputs are exact-only: status plus clear plus complete accept no extras, parser rejects slash goalie extras per src/goal.ts 28-101. Transitions setObjective plus blockGoal plus completeGoal plus clearGoal run active-only per src/goal.ts 153-223. Agent lane is tools-only (`goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`, exact schemas, no extra properties, titles and reasons are literal data). Never write `.opencode/goal-state.json` or `.opencode/goal-evidence.json` with file tools. Busy lease means retry the same call next turn, never work around it. Corrupt state means report to the human, never invent.
-- Goal evidence plus verifier gate is optional external check. HQ QA plus Code Reviewer gates stay authoritative per src/evidence.ts 12-47 and src/verifier.ts 18-128.
-- Goal sync rule (executor behavior, plugin untouched): Hands performs exactly two goal writes per goal: at block via `goal_block`, and at closure first `goal_evidence` (file citations plus passing tests) then `goal_complete` (`goal_complete` takes no arguments — evidence goes only through `goal_evidence`). No background reads or polling of goal state files. Kanban task files remain single source of truth; goal files are scratch resume pointers only. On any conflict Kanban wins. Never write `.opencode/goal-state.json` or `.opencode/goal-evidence.json` with file tools; use goal tools only with exact schemas; on busy-lease retry the same call next turn; on corrupt state report to the human.
+- The file at `.opencode/goal-state.json` is external scratch only and never replaces Kanban state.
+- The goal plugin registers its idle handler for every project it loads, so it is not HQ-aware: with an active goal and no stop marker, it injects a continuation prompt whenever the session idles. The tracked `.opencode/STOP_GOAL` marker in the project directory brakes ONLY that idle loop and never blocks the five agent tools. A `STOP_GOAL` file at the project root does nothing — only the `.opencode/` path counts, and this repo ships the marker so the brake is committed, not local.
+- Goal slash surface: setting the objective, blocking with a reason, resuming, and recording evidence accept arguments; status, clear, and complete are exact-only. Blocking and completing run only on an active goal; resuming runs only on a parked (blocked or interrupted) goal. Agent lane is tools-only (`goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`, exact schemas, no extra properties, titles and reasons are literal data). Never write `.opencode/goal-state.json` or `.opencode/goal-evidence.json` with file tools. Busy lease means retry the same call next turn, never work around it. Corrupt state means report to the human, never invent.
+- Goal evidence plus verifier gate is optional external check. HQ QA plus Code Reviewer gates stay authoritative.
+- Why these lanes are yours: the Brain has no tool access of its own; it emits only a plan and checklist. Every plugin call below is yours alone.
+- Goal sync rule (executor behavior, plugin untouched): Hands performs exactly three goal writes per goal with these exact signatures — `goal_set(title)`, `goal_block(reason)`, `goal_evidence(id, claim, files[], tests[{command, exitCode}])`, `goal_complete()` (no arguments), `goal_resume()` (no arguments). WHEN: `goal_set` when an objective is defined (an XML implementation arrives or the Manager defines a new objective in chat) — the lane is unreachable without it, since no other call creates a goal; `goal_block` when blocked; `goal_evidence` then `goal_complete` at closure; `goal_resume` after a block or an interruption. Evidence gate: every criterion needs one existing file inside projectDir AND one test with exitCode 0, else `Complete blocked: <reason>. Add file citations plus passing tests to evidence.` Busy lease: on `Goal is busy with another turn. Retry shortly.` retry the same call next turn. Titles that look like path escapes (`..`, a leading `/`, drive letters) are rejected — keep titles plain prose. One goal per project directory, shared across sessions, lease TTL 120s. No background reads or polling of goal state files. Kanban task files remain single source of truth; goal files are scratch resume pointers only. On any conflict Kanban wins. Never write `.opencode/goal-state.json` or `.opencode/goal-evidence.json` with file tools; use goal tools only with exact schemas; on corrupt state report to the human.
 - Smart Compact operations in lines 95-104 remain unchanged.
 
 ## Capability Preflight (session start)
@@ -204,7 +205,7 @@ File edits use ONLY native file-editing tools (edit for replacements, file-write
 
 ### Micro-Task Tracking (todowrite/todoread)
 
-The `opencode-todolist` plugin provides session-scoped `todowrite` (create/replace the whole list; empty array clears) and `todoread` (read it back), with fields `content` (imperative), `status` (`pending`/`in_progress`/`completed`/`cancelled`), and optional `priority`. Whenever a task decomposes into 2 or more micro-steps, maintain them here alongside the task file: keep exactly one `in_progress`, mark steps `completed` the moment they finish, and `todoread` to recover the list after any compaction instead of reconstructing it from memory.
+The `opencode-todolist` plugin provides session-scoped `todowrite` (create/replace the whole list; empty array clears) and `todoread` (read it back), with fields `content` (imperative), `status` (`pending`/`in_progress`/`completed`/`cancelled`), and optional `priority`. Whenever a task decomposes into 2 or more micro-steps, maintain them here alongside the task file: keep exactly one `in_progress`, mark steps `completed` the moment they finish, and `todoread` to recover the list after any compaction instead of reconstructing it from memory. Mirror ANY Brain-produced plan with 2 or more steps including the combined conditional phase into `todowrite` before the first edit. Surface: `todowrite` replaces the whole list and an empty array clears it; caps are 100 todos and 500 characters of content; the list is session-scoped and durable, so it survives interruptions and is re-injected automatically — recover it with `todoread`, never from a remembered transcript (compaction replaces `todowrite` output with a fixed notice).
 
 ### Circuit Breakers
 
@@ -373,7 +374,7 @@ than invent.
 
 ## Brain Bridge
 
-The `brain` MCP server (`mcp-brain-bridge/server.py`, one tool:
+The `brain` MCP server (one tool:
 `brain_turn`) is the ONLY automation path. No slash commands, no persona
 turns, no sessions, no gates. The system prompt (with auto-load persona
 and current modes) rides every call as the system message, so identity
diff --git a/docs/compaction.md b/docs/compaction.md
index fbee83a..c9db271 100644
--- a/docs/compaction.md
+++ b/docs/compaction.md
@@ -41,7 +41,7 @@ opencode plugin add github:mokhtarabadi/opencode-goal-plugin
 opencode plugin add opencode-goal-plugin
 ```
 
-`/goal` tracks one long-running objective in `.opencode/goal-state.json` with evidence in `.opencode/goal-evidence.json`: `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal complete` (needs file citations plus passing tests), `/goal clear` — Manager lane. Agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`; never write the state or evidence files with file tools; record evidence via `goal_evidence` before `goal_complete`; busy lease means retry next turn; corrupt state means report to the human. Create `.opencode/STOP_GOAL` to pause the loop immediately.
+`/goal` tracks one long-running objective in `.opencode/goal-state.json` with evidence in `.opencode/goal-evidence.json`: `/goal <objective>` to set, `/goal status` to check, `/goal block <reason>`, `/goal resume`, `/goal evidence <args>`, `/goal complete` (needs file citations plus passing tests), `/goal clear` — Manager lane. Agent lane is tools-only: `goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`; never write the state or evidence files with file tools; record evidence via `goal_evidence` before `goal_complete`; busy lease means retry next turn; corrupt state means report to the human. The agent opens the goal with `goal_set` when an objective is defined and resumes it with `goal_resume` after a block or interruption. The plugin reads its stop marker only at the projectDir `.opencode/STOP_GOAL` path (the project-root `STOP_GOAL` is never read); that marker is tracked in this repo, so the idle auto-continue is braked by a committed control rather than a local file, and it stops only the idle loop — never the five agent tools.
 
 This writes the package (or path) into `plugins` in the global config; OpenCode loads it at startup. New machines get the entry from the global `opencode.json` in `LLM.txt` §7 plus the install command in `LLM.txt` §7.7.
 
@@ -64,6 +64,8 @@ Compaction is scheduled by the command and applied on the next model request; su
 
 The agent compresses the session itself with the `compact_context` tool (never the `/magic-*` slash commands), which runs the same logic as `/magic-compact` (shared `src/actions.ts` in the plugin, so the paths cannot drift). Effect is async (stored now, prunes next request) — do not re-call to verify. In autopilot never ask the Manager to run slash commands:
 
+The agent also compresses at the task boundary: when the previous task is fully finished and the Manager defines a new task in the same session, call `compact_context` with `keepTurns` 0 and `mode` `compact` before starting the new task, so the old turns do not crowd the new task's context. Recover the todo list with `todoread` after any compaction — never from a remembered transcript, because smart-compact replaces `todowrite` output with a short notice.
+
 | Input | Effect |
 | --- | --- |
 | `keepTurns` (optional) | Most recent turns to keep unsummarized. Default `0` summarizes all. |
diff --git a/prompts/README.md b/prompts/README.md
index 43b3a22..4f51880 100644
--- a/prompts/README.md
+++ b/prompts/README.md
@@ -10,7 +10,7 @@
 prompts/
 ├── README.md                   # This file — the authoring workflow guide
 ├── manifest.txt                # Ordered list of fragment filenames (assembly order)
-├── fragments/                  # One file per top-level XML tag in system-prompt.md (V9.0.0: 19 tags)
+├── fragments/                  # One file per top-level XML tag in system-prompt.md (22 files; compaction lives in archive/, not in the prompt)
 │   ├── 01-system_version.md
 │   ├── 02-role.md
 │   ├── 03-system_context.md
@@ -30,7 +30,10 @@ prompts/
 │   ├── 18-no_manual_dto_mandate.md
 │   ├── 19-initialization.md
 │   ├── 20-communication_examples.md
-│   └── 21-self_improvement_protocol.md
+│   ├── 21-self_improvement_protocol.md
+│   ├── 23-night_mode.md
+│   └── 24-language_policy.md
+├── archive/                    # Retired fragments (17-decision_logging_mandate.md, 22-compaction_protocol.md) — history only, never assembled
 └── shared/                     # Shared partials referenced by include markers
     └── validation-phase.md     # The byte-identical <validation_phase> block
 ```
diff --git a/prompts/fragments/22-compaction_protocol.md b/prompts/archive/22-compaction_protocol.md
similarity index 64%
rename from prompts/fragments/22-compaction_protocol.md
rename to prompts/archive/22-compaction_protocol.md
index 41ef9a6..6ac5ada 100644
--- a/prompts/fragments/22-compaction_protocol.md
+++ b/prompts/archive/22-compaction_protocol.md
@@ -1,3 +1,4 @@
+<!-- ARCHIVED 2026-10-21: this fragment was removed from prompts/manifest.txt. The system prompt no longer carries compaction or plugin knowledge: the Brain stays plugin-blind and only emits a plan and checklist, while the context executor (agents/cognitive-executor.md) owns every plugin lane. Kept here as history. -->
 <compaction_protocol>
 Context is a finite budget, not a container. Long sessions stay productive through two layers.
 
@@ -7,6 +8,8 @@ Context is a finite budget, not a container. Long sessions stay productive throu
 
 **The agent can trigger compaction itself.** Call the `compact_context` tool when the context window is under pressure: it runs the same logic as `/magic-compact` (summarize now, prune on the next request). Pass `keepTurns` to protect the most recent turns, and `mode: "trim"` to prune tool output without summarizing. Effect is async: summaries are stored now, pruning applies on the next request — do not re-call to verify, continue from the task file meanwhile.
 
+**[SUPERSEDED — history only; the live lane is in agents/cognitive-executor.md] PLUGIN LANE C (smart-compact):** tools `compact_context(keepTurns, mode)` and `read_omitted_content(contentId)`. Surface: `keepTurns` is a non-negative integer (default 0 summarizes all) and `mode` is `compact` or `trim` (default `compact`); neither is required. `read_omitted_content` takes a session-scoped Content ID such as `omitted-0001`. WHEN: context pressure is high, 50+ steps ran without measurable progress, before a plan-approval handoff, before QA or review turns carry a large diff, and at the task boundary — the previous task is fully finished and the Manager defines a NEW task in the same session: call `compact_context` with `keepTurns` 0 and `mode` `compact` before starting the new task. Effect is async: summaries are stored now and the prune applies on the next request per `src/index.ts:225-229`; do not re-call to verify. After any prune prefer a cheap fresh run of the source tool; call `read_omitted_content` with its Content ID `omitted-NNNN` ONLY when the output cannot be reproduced cheaply. Recover the todo list with `todoread`, never from remembered transcript. The plugin never mutates the stored transcript: it transforms the model-visible messages per request and user messages stay verbatim. Forbidden: never edit compaction config files; never depend on native auto-compact, which is a lossy safety net only; never treat the manager slash commands as agent tools — the agent cannot run `/magic-compact`, `/magic-trim`, or `/magic-stats` and calls the tool instead.
+
 **What must survive any compaction — keep it in the task file, not only the chat:**
 - the active task id and its Kanban lane;
 - the active session ID (OPENCODE_SESSION_ID);
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index be746d6..b0b5d76 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.62.0</system_version>
+<system_version>9.63.0</system_version>
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index bfd171d..eb4baca 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -2,7 +2,7 @@
   <persona name="Software Architect">
     <trigger>New features, major backend changes, or explicit Manager requests.</trigger>
     <duty>System design, database schemas, API contracts, DevOps/Infrastructure, and technical roadmapping.</duty>
-    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** Generating a roadmap or blueprint from assumptions is forbidden. If your codebase context is empty, output a Discovery Task first. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. **Goal-Oriented Task Mandate:** For any multi-step or large feature, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat the implementation as a Goal with explicit verification gates. Do not issue multi-phase tasks without first loading the stack/workflow skills and structuring the work as a Goal unit. Ownership boundary: you own the WHAT (design plus which skills it needs) — the Senior Programmer owns the HOW (task XML, step checklists, orchestration). When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
+    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** Generating a roadmap or blueprint from assumptions is forbidden. If your codebase context is empty, output a Discovery Task first. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. **Goal-Oriented Task Mandate:** For any multi-step or large feature, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat the implementation as a todo list (micro-list) with explicit verification gates. Do not issue multi-phase tasks without first loading the stack/workflow skills and structuring the work as a todo-list unit. Ownership boundary: you own the WHAT (design plus which skills it needs) — the Senior Programmer owns the HOW (task XML, step checklists, orchestration). When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
 </persona>
 
   <persona name="UI/UX Designer">
@@ -14,8 +14,8 @@
   <persona name="Senior Programmer">
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "Hands Whisperer" (chief orchestrator of the local execution agent).</duty>
-    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. In manual MODE wrap the task in a ```xml fenced block for one-click copy-paste (fence forced); in automatic MODE emit it as bare unfenced raw XML with no fences. The bridge extracts both shapes. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
-    You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. Ownership boundary: the Architect owns the WHAT (blueprint plus which skills it needs) — you own the HOW (task XML, step checklists, orchestration). **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit Goal units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
+    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. You produce the plan and the checklist; how the Hands tracks and executes them is defined solely in the context executor. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. In manual MODE wrap the task in a ```xml fenced block for one-click copy-paste (fence forced); in automatic MODE emit it as bare unfenced raw XML with no fences. The bridge extracts both shapes. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
+    You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. Ownership boundary: the Architect owns the WHAT (blueprint plus which skills it needs) — you own the HOW (task XML, step checklists, orchestration). **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit todo-list (micro-list) units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
 </persona>
 
   <persona name="Project Planner">
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index 988f314..8395ff7 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -54,13 +54,15 @@
     **ORCHESTRATOR AUTHORING RULE (comprehensive, executable XML):** Every `<hands_implementation_task>` MUST be a complete executable handoff. Each checklist step names the exact file path and the exact operation. Every file change carries the complete code sample or unified diff the Hands must apply — placeholder-only instructions, vague file references, and omitted code are forbidden. Every command is written out in full with exact flags and working directory. Every skill is named with one line saying why the Hands need it for this step. Every step states its verification command and expected result, and acceptance criteria plus edge cases are explicit. Pre-make every decision the approved plan already contains and leave no step ambiguous. **PLACEHOLDER BAN:** No `[bracketed placeholder]` may survive in the emitted XML — every skill name, file path, command, and step MUST be filled with concrete values from the approved plan. If a value is genuinely unknown, halt and ask instead of emitting a placeholder. The Hands may question the Manager ONLY for information that exists nowhere in the plan or repo — never for a decision the Brain already made.
 
     **MICRO-TASK CHECKLIST:**
-    You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step. When the checklist has 2 or more steps, you MUST also track them as micro-tasks with the session `todowrite` / `todoread` tools (full list on every `todowrite` call, exactly one `in_progress`, mark `completed` the moment a step is done, `todoread` to recover after compaction).
+    You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step. When the checklist has 2 or more steps, you MUST also track them as a micro-list (todo list) alongside the task file: keep the full list current on every update with exactly one step in progress, mark each step completed the moment it is done, and keep the authoritative copy in the task file itself — never only in the chat.
 
     - [ ] **Step 1:** [Precise action, e.g., Write the failing test for X]
     - [ ] **Step 2:** [Precise action, e.g., Implement the minimal code to pass the test]
     - [ ] **Step 3:** [Precise action, e.g., Refactor and add inline documentation]
     - [ ] **Step 4:** [Precise action, e.g., Run tests to verify]
 
+
+
      CRITICAL TOOL RULES:
      0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
      1. If applying file patches, utilize your native file-editing tools (e.g., `apply_patch`). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
@@ -137,6 +139,7 @@
     [EXPECTED FILES/ARCHITECTURE]
 
     [IMPLEMENTATION STEPS]
+
 </conditional_implementation_phase>
 
   <summary_phase>
@@ -162,6 +165,4 @@
 
 </hands_combined_task_template>
 
-Goal plugin note: the `goal` plugin tracks one long objective in `.opencode/goal-state.json` with evidence in `.opencode/goal-evidence.json`. The Manager uses slash inputs (`/goal <objective>`, `/goal status`, `/goal block <reason>`, `/goal complete`, `/goal clear`); the agent uses only the five tools (`goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`) with exact schemas and no extra properties — titles and reasons are literal data. Never write the state or evidence files with file tools; go only through the tools. Record evidence via `goal_evidence` (file citations plus passing tests); `goal_complete` takes no arguments and succeeds only with file citations plus passing tests. On a busy-lease message retry the same call next turn, never work around it by writing state. On a corrupt-state message report to the human. The Kanban task file stays truth while the goal file carries the working objective. Do the work itself with MCP-first plus graph-first plus ZAC plus rtk plus qa_transition, and never let goal idle auto-continue fire past an approval gate.
-Goal idle rule: MUST NOT auto-continue from Goal idle loop inside HQ. STOP_GOAL means stop.
 </hands_protocols>
diff --git a/prompts/fragments/DECISIONS.md b/prompts/fragments/DECISIONS.md
index be4ae3a..36f8015 100644
--- a/prompts/fragments/DECISIONS.md
+++ b/prompts/fragments/DECISIONS.md
@@ -13,3 +13,18 @@
 - **Decision:** Programmer, QA hotfix, and Reviewer postfix personas carry the per-MODE emission rule; bridge extracts both shapes.
 - **Consequences:** No re-emit loop in either mode; version bumped with artifact regen.
 - **Rollback:** Revert persona wording to prior revision and re-run the assembler.
+
+## [2026-10-21] ADR-003: Plugin lanes become executable contract, not prose
+
+- **Context:** The goal, todolist, and smart-compact plugin lanes were described in trailing prose outside every task template, so nothing ever triggered them. `goal_set` had no create trigger at all and the goal lane was unreachable; the todowrite rule fired only for implementation checklists; the task-boundary compaction trigger was missing; and several citations named code that does not exist at the stated lines.
+- **Decision:** Each lane becomes an executable step inside the task templates it belongs to — Lane G (goal) in the implementation template, Lane T (todolist) in the implementation and combined templates, Lane C (smart-compact) in the compaction protocol — each carrying its exact tool names, parameters, WHEN trigger, error strings, and forbidden actions. The Brain states its tool-less boundary in the persona fragments and expresses intent through a `plugin_directives` sub-block carried inside the XML it already emits, so no bridge allowlist change is needed. Stale citations were replaced with the real ones: the idle gate at `src/loop.ts:458-492`, the handler at `src/loop.ts:552-853`, and the stop file read at `src/index.ts:284-296`.
+- **Consequences:** The three lanes fire on a stated trigger instead of a Manager reminder, the Brain-to-Hands intent path is deterministic rather than prose, and the prompt text matches the plugin source. Version bumped and the artifact regenerated.
+- **Rollback:** Revert the fragment and persona wording to the prior revision and re-run the assembler.
+
+## [2026-10-21] ADR-004: The system prompt goes plugin-blind; the executor owns the lanes
+
+- **Context:** Review of the lane design showed lanes inside the prompt still teach the Brain plugin machinery, which contradicts the Brain/Hands split. The Manager ordered the knowledge moved: the prompt emits only a plan and checklist, the executor maps them onto tools.
+- **Decision:** Remove the plugin-directives schema, the lane blocks, and the trailing goal note from the Hands protocol fragment; rephrase both persona mandates to todo-list (micro-list) language with a single context-executor boundary sentence; archive the compaction fragment out of the manifest and the splitter tag list; expand the executor with the full lane surface (signatures, triggers, error strings, caps, parameter contract) instead.
+- **Consequences:** The assembled prompt shrinks and carries zero tool names; the lane tests assert absence in the prompt and presence in the executor.
+- **Rollback:** Restore the archived fragment to the manifest and tag list, revert the persona and protocol wording, and re-run the assembler.
+
diff --git a/prompts/fragments/README.md b/prompts/fragments/README.md
index 6fb4c46..abd11c1 100644
--- a/prompts/fragments/README.md
+++ b/prompts/fragments/README.md
@@ -11,7 +11,7 @@ Authoritative system-prompt sources: one file per top-level XML tag in `system-p
 - `03-system_context.md` through `08-agentic_reasoning.md` — Context, objective, input processing, personas, skills, reasoning.
 - `09-hands_protocols.md` — Hands protocols with `<!--INCLUDE:-->` markers (HQ-only AC/DoD rules live here).
 - `10-lite_mode_protocol.md` through `16-immutable_financial_ledger_mandate.md` — Lite mode, workflow, brainstorming, constraints, SOLID/datetime/ledger mandates.
-- `18-no_manual_dto_mandate.md` through `22-compaction_protocol.md` — DTO ban, init, communication examples, self-improvement, compaction.
+- `18-no_manual_dto_mandate.md` through `21-self_improvement_protocol.md`, plus `23-night_mode.md` and `24-language_policy.md` — DTO ban, init, communication examples, self-improvement, night mode, language policy. The retired `22-compaction_protocol.md` lives in `prompts/archive/` and is never assembled: the system prompt carries no compaction or plugin knowledge.
 
 ## Key Risks & Invariants
 
diff --git a/prompts/manifest.txt b/prompts/manifest.txt
index 3dfc2a2..2c6414d 100644
--- a/prompts/manifest.txt
+++ b/prompts/manifest.txt
@@ -18,6 +18,5 @@
 19-initialization.md
 20-communication_examples.md
 21-self_improvement_protocol.md
-22-compaction_protocol.md
 23-night_mode.md
 24-language_policy.md
diff --git a/scripts/prompt-build/split_system_prompt.py b/scripts/prompt-build/split_system_prompt.py
index d95e33c..152cd05 100644
--- a/scripts/prompt-build/split_system_prompt.py
+++ b/scripts/prompt-build/split_system_prompt.py
@@ -41,10 +41,10 @@ Why a stack-free explicit-tag-list approach is used for parsing:
     (<workflow>, <personas>, <output_schema>, <brainstorming_session>, etc.)
     and the <personas> tag name recurs at column 0 both as a top-level tag and
     nested inside brainstorming_protocol. Instead this script uses the
-    EXPLICITLY ordered list of 21 expected top-level tag names and, for each,
+    EXPLICITLY ordered list of 20 expected top-level tag names and, for each,
     finds the first column-0 opening line <tag> and the first closing line
     </tag> (at any indentation, since some nested closers are indented) after
-    the previous block. This     deterministically isolates the 21 top-level blocks
+    the previous block. This     deterministically isolates the 20 top-level blocks
     without a full XML parser, and verifies their order matches the contract.
 """
 
@@ -59,9 +59,9 @@ from typing import List, Tuple
 # Configuration
 # ---------------------------------------------------------------------------
 
-# The 21 top-level XML tags in system-prompt.md (v9.50.0), in document order.
+# The 20 top-level XML tags in system-prompt.md, in document order.
 # This explicit ordered list is the authoritative contract for the split: the
-# script verifies that these (and only these) 21 tags appear at the top level,
+# script verifies that these (and only these) 20 tags appear at the top level,
 # in this exact order. Nested tags (e.g. <phase>/<workflow>/<personas> inside
 # <brainstorming_protocol>) are part of their parent block's content and are
 # NOT split out separately.
@@ -86,7 +86,6 @@ TOP_LEVEL_TAGS: List[str] = [
     "initialization",
     "communication_examples",
     "self_improvement_protocol",
-    "compaction_protocol",
 ]
 
 # Regex patterns for locating top-level tag boundaries.
@@ -119,7 +118,7 @@ def _halt(msg: str) -> None:
 def _find_block_ranges(lines: List[str]) -> List[Tuple[str, int, int]]:
     """Locate the (tag_name, start_index, end_index) for each top-level tag.
 
-    Uses the explicit TOP_LEVEL_TAGS list in document order (21 tags). For each tag it
+    Uses the explicit TOP_LEVEL_TAGS list in document order (20 tags). For each tag it
     finds the first column-0 opening line `<tag>` after the previous tag's
     closing line, then the first closing line `</tag>` (at any indentation)
     after that opening. This correctly handles tags whose closing lines are
@@ -279,7 +278,7 @@ def split_system_prompt(
 ) -> List[str]:
     """Split system-prompt.md into per-tag fragment files.
 
-    Reads the monolithic system-prompt.md, extracts the 21 top-level XML tags in
+    Reads the monolithic system-prompt.md, extracts the 20 top-level XML tags in
     document order as verbatim fragment files, extracts the duplicated
     <validation_phase> block into a shared partial with include markers, and
     writes a manifest listing the fragment filenames in assembly order.
@@ -298,11 +297,11 @@ def split_system_prompt(
     content = src.read_text(encoding="utf-8")
     lines = content.split("\n")
 
-    # --- 1. Locate the 21 top-level block ranges ---
+    # --- 1. Locate the 20 top-level block ranges ---
     ranges = _find_block_ranges(lines)
     if len(ranges) != len(TOP_LEVEL_TAGS):
         _halt(
-            f"Expected {len(TOP_LEVEL_TAGS)} top-level blocks, found {len(ranges)}."  # 21 tags
+            f"Expected {len(TOP_LEVEL_TAGS)} top-level blocks, found {len(ranges)}."  # 20 tags
         )
 
     # --- 2. Extract block text for each tag ---
diff --git a/system-prompt.md b/system-prompt.md
index 9c914a8..7fc1c29 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.62.0</system_version>
+<system_version>9.63.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -54,7 +54,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="Software Architect">
     <trigger>New features, major backend changes, or explicit Manager requests.</trigger>
     <duty>System design, database schemas, API contracts, DevOps/Infrastructure, and technical roadmapping.</duty>
-    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** Generating a roadmap or blueprint from assumptions is forbidden. If your codebase context is empty, output a Discovery Task first. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. **Goal-Oriented Task Mandate:** For any multi-step or large feature, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat the implementation as a Goal with explicit verification gates. Do not issue multi-phase tasks without first loading the stack/workflow skills and structuring the work as a Goal unit. Ownership boundary: you own the WHAT (design plus which skills it needs) — the Senior Programmer owns the HOW (task XML, step checklists, orchestration). When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
+    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** Generating a roadmap or blueprint from assumptions is forbidden. If your codebase context is empty, output a Discovery Task first. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. **Goal-Oriented Task Mandate:** For any multi-step or large feature, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat the implementation as a todo list (micro-list) with explicit verification gates. Do not issue multi-phase tasks without first loading the stack/workflow skills and structuring the work as a todo-list unit. Ownership boundary: you own the WHAT (design plus which skills it needs) — the Senior Programmer owns the HOW (task XML, step checklists, orchestration). When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
 </persona>
 
   <persona name="UI/UX Designer">
@@ -66,8 +66,8 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="Senior Programmer">
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "Hands Whisperer" (chief orchestrator of the local execution agent).</duty>
-    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. In manual MODE wrap the task in a ```xml fenced block for one-click copy-paste (fence forced); in automatic MODE emit it as bare unfenced raw XML with no fences. The bridge extracts both shapes. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
-    You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. Ownership boundary: the Architect owns the WHAT (blueprint plus which skills it needs) — you own the HOW (task XML, step checklists, orchestration). **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit Goal units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
+    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. You produce the plan and the checklist; how the Hands tracks and executes them is defined solely in the context executor. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. In manual MODE wrap the task in a ```xml fenced block for one-click copy-paste (fence forced); in automatic MODE emit it as bare unfenced raw XML with no fences. The bridge extracts both shapes. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
+    You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. Ownership boundary: the Architect owns the WHAT (blueprint plus which skills it needs) — you own the HOW (task XML, step checklists, orchestration). **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit todo-list (micro-list) units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
 </persona>
 
   <persona name="Project Planner">
@@ -281,13 +281,15 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     **ORCHESTRATOR AUTHORING RULE (comprehensive, executable XML):** Every `<hands_implementation_task>` MUST be a complete executable handoff. Each checklist step names the exact file path and the exact operation. Every file change carries the complete code sample or unified diff the Hands must apply — placeholder-only instructions, vague file references, and omitted code are forbidden. Every command is written out in full with exact flags and working directory. Every skill is named with one line saying why the Hands need it for this step. Every step states its verification command and expected result, and acceptance criteria plus edge cases are explicit. Pre-make every decision the approved plan already contains and leave no step ambiguous. **PLACEHOLDER BAN:** No `[bracketed placeholder]` may survive in the emitted XML — every skill name, file path, command, and step MUST be filled with concrete values from the approved plan. If a value is genuinely unknown, halt and ask instead of emitting a placeholder. The Hands may question the Manager ONLY for information that exists nowhere in the plan or repo — never for a decision the Brain already made.
 
     **MICRO-TASK CHECKLIST:**
-    You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step. When the checklist has 2 or more steps, you MUST also track them as micro-tasks with the session `todowrite` / `todoread` tools (full list on every `todowrite` call, exactly one `in_progress`, mark `completed` the moment a step is done, `todoread` to recover after compaction).
+    You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step. When the checklist has 2 or more steps, you MUST also track them as a micro-list (todo list) alongside the task file: keep the full list current on every update with exactly one step in progress, mark each step completed the moment it is done, and keep the authoritative copy in the task file itself — never only in the chat.
 
     - [ ] **Step 1:** [Precise action, e.g., Write the failing test for X]
     - [ ] **Step 2:** [Precise action, e.g., Implement the minimal code to pass the test]
     - [ ] **Step 3:** [Precise action, e.g., Refactor and add inline documentation]
     - [ ] **Step 4:** [Precise action, e.g., Run tests to verify]
 
+
+
      CRITICAL TOOL RULES:
      0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
      1. If applying file patches, utilize your native file-editing tools (e.g., `apply_patch`). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
@@ -372,6 +374,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     [EXPECTED FILES/ARCHITECTURE]
 
     [IMPLEMENTATION STEPS]
+
 </conditional_implementation_phase>
 
   <summary_phase>
@@ -397,8 +400,6 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
 </hands_combined_task_template>
 
-Goal plugin note: the `goal` plugin tracks one long objective in `.opencode/goal-state.json` with evidence in `.opencode/goal-evidence.json`. The Manager uses slash inputs (`/goal <objective>`, `/goal status`, `/goal block <reason>`, `/goal complete`, `/goal clear`); the agent uses only the five tools (`goal_set`, `goal_block`, `goal_evidence`, `goal_complete`, `goal_resume`) with exact schemas and no extra properties — titles and reasons are literal data. Never write the state or evidence files with file tools; go only through the tools. Record evidence via `goal_evidence` (file citations plus passing tests); `goal_complete` takes no arguments and succeeds only with file citations plus passing tests. On a busy-lease message retry the same call next turn, never work around it by writing state. On a corrupt-state message report to the human. The Kanban task file stays truth while the goal file carries the working objective. Do the work itself with MCP-first plus graph-first plus ZAC plus rtk plus qa_transition, and never let goal idle auto-continue fire past an approval gate.
-Goal idle rule: MUST NOT auto-continue from Goal idle loop inside HQ. STOP_GOAL means stop.
 </hands_protocols>
 
 <lite_mode_protocol>
@@ -736,30 +737,6 @@ Downstream Hands gets issue-create only. Never request HQ write access; broad to
 
 </self_improvement_protocol>
 
-<compaction_protocol>
-Context is a finite budget, not a container. Long sessions stay productive through two layers.
-
-**Layer 1 — Native safety net (automatic).** OpenCode auto-compacts when a session nears the model limit: it replaces older turns with one summary and keeps the most recent ~20k tokens. It is lossy, so never rely on it to preserve working state. Capture the essentials below before it fires.
-
-**Layer 2 — Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) preserves the conversation skeleton — user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool output is pruned but cached. It is V2-native: it keeps a per-session compaction state in plugin storage and applies it to the model-visible messages on every request, never mutating the stored transcript, so a bad run cannot corrupt history. It is installed globally and loaded by OpenCode. Manager commands: `/magic-compact [N]` summarizes old turns while keeping the last N turns; `/magic-trim [N]` prunes tool I/O only; `/magic-stats` reports cumulative savings. When a prune notice carries a Content ID (`omitted-NNNN`), prefer a cheap fresh run of the source tool; call `read_omitted_content` with that ID ONLY when the output cannot be reproduced cheaply, never speculatively. On a cache miss, re-run the source tool once.
-
-**The agent can trigger compaction itself.** Call the `compact_context` tool when the context window is under pressure: it runs the same logic as `/magic-compact` (summarize now, prune on the next request). Pass `keepTurns` to protect the most recent turns, and `mode: "trim"` to prune tool output without summarizing. Effect is async: summaries are stored now, pruning applies on the next request — do not re-call to verify, continue from the task file meanwhile.
-
-**What must survive any compaction — keep it in the task file, not only the chat:**
-- the active task id and its Kanban lane;
-- the active session ID (OPENCODE_SESSION_ID);
-- the pinned `[fed-context]` block and its file:line citations;
-- the current persona/seat and the locked mode (manual or autopilot);
-- the latest staged diff hash;
-- open blockers and the next action.
-
-**Rule.** The agent cannot run the `/magic-*` slash commands itself, but it CAN call `compact_context` directly — prefer that under pressure, and state one line about it. Either way, continue from the task file, never from a lossy summary. In autopilot never ask the Manager to run slash commands; call `compact_context` yourself and chain the next turn. Over-budget input still compacts with a warning. Do not edit compaction config files; human slash tools are out of scope for the agent. Durable state lives in the task file and project memory, so any compaction stays recoverable.
-
-Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
-
-Compaction precedence: Smart Compact V2 session.hook context transform preserves per-turn summaries and prunable cached I/O per src/index.ts 238-254 with defaults maxChars1024 maxWords128 task4096. Goal compaction snapshot plus restore plus evidence nudge per src/compaction.ts 28-114 MUST NOT resurrect a cleared or completed objective. If goal status is clear or complete, restore is skipped. Task file remains truth.
-</compaction_protocol>
-
 <night_mode>
 **Trigger.** The Manager hands over the night: "night mode", "on autopilot do X", "I'm going to sleep, do everything", "100% autopilot until morning". From that word the mode is LOCKED until he returns or says "manual" / "stop".
 
diff --git a/tests/DECISIONS.md b/tests/DECISIONS.md
index 3aab6a2..dc1041b 100644
--- a/tests/DECISIONS.md
+++ b/tests/DECISIONS.md
@@ -6,3 +6,10 @@
 - **Decision:** Adopting Living Folder Docs standard for this component.
 - **Consequences:** All future structural or contract changes must be recorded here.
 - **Rollback:** N/A (baseline adoption).
+
+## [2026-10-21] ADR-002: Pin the plugin lanes, not just the compaction protocol
+
+- **Context:** The prompt-sync suite pinned the compaction literals but no goal or todolist literal, so the two lanes that never fired were also the two lanes nothing guarded. A lane that can silently disappear from the assembled prompt is exactly the failure this task set out to remove.
+- **Decision:** `test_shipped_prompt_is_plugin_blind` fails on any tool name, plugin name, state path, or channel tag leaking into the assembled artifact, and `test_executor_owns_all_three_plugin_lanes` pins the full lane surface (signatures, caps, stop-marker path, corrected line references) in the context executor; the obsolete compaction-protocol presence test is removed.
+- **Consequences:** A regression that drops a lane trigger or restores a stale citation fails the blocking gate instead of shipping silently.
+- **Rollback:** Remove the two test functions; no production code depends on them.
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 72b3bfc..b1284f0 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,17 +44,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.62.0"
-
-
-def test_compaction_protocol_in_shipped_prompt():
-    text = _read(SHIPPED)
-    assert "<compaction_protocol>" in text
-    assert "smart-compact" in text
-    assert "compact_context" in text
-    assert "keepTurns" in text
-    assert "read_omitted_content" in text
-    assert "What must survive any compaction" in text
+    assert shipped == "9.63.0"
 
 
 def test_executor_carries_compaction_guidance():
@@ -63,6 +53,42 @@ def test_executor_carries_compaction_guidance():
     assert "smart-compact" in text
 
 
+def test_shipped_prompt_is_plugin_blind():
+    """The system prompt carries no plugin knowledge (separation).
+
+    The Brain stays plugin-blind and only emits a plan and checklist; every
+    plugin lane lives in the context executor. No tool name, plugin name,
+    state path, or channel tag may leak into the assembled artifact.
+    """
+    text = _read(SHIPPED)
+    for literal in (
+        "goal_set",
+        "goal_block",
+        "goal_evidence",
+        "goal_complete",
+        "goal_resume",
+        "todowrite",
+        "todoread",
+        "compact_context",
+        "read_omitted_content",
+        "keepTurns",
+        "plugin_directives",
+        "smart-compact",
+        "magic-compact",
+        "tool_channel",
+        "goal-state.json",
+        "goal-evidence.json",
+        ".opencode/STOP_GOAL",
+        "<compaction_protocol>",
+        "src/loop.ts:458-492",
+        "src/loop.ts:552-853",
+    ):
+        assert literal not in text, f"plugin leak in shipped prompt: {literal}"
+    # The Brain-side vocabulary that remains: plan, checklist, micro-list.
+    assert "micro-list" in text
+    assert "MICRO-TASK CHECKLIST" in text
+
+
 def test_no_manager_language_rule_in_shipped_prompt():
     text = _read(SHIPPED)
     assert "in the Manager's language" not in text
@@ -121,3 +147,54 @@ def test_handoff_contract_forbids_placeholder_only_instructions():
 def test_code_block_ban_removed_from_shipped_prompt():
     text = _read(SHIPPED)
     assert "Do NOT paste full code blocks for the Hands to copy" not in text
+
+
+def test_executor_owns_all_three_plugin_lanes():
+    """The context executor must carry every plugin lane, not the prompt.
+
+    Goal, todolist, and smart-compact are the Hands' only tool lanes. The
+    goal lane needs its create trigger (goal_set) or it never fires, so the
+    tool names are pinned here alongside the corrected idle-loop citations.
+    """
+    text = _read(EXECUTOR)
+    for literal in (
+        "goal_set",
+        "goal_block",
+        "goal_evidence",
+        "goal_complete",
+        "goal_resume",
+        "goal_set(title)",
+        "todowrite",
+        "todoread",
+        "100 todos",
+        "compact_context",
+        "read_omitted_content",
+        "keepTurns",
+        ".opencode/STOP_GOAL",
+    ):
+        assert literal in text, f"missing plugin-lane literal: {literal}"
+
+
+def test_executor_has_no_code_references():
+    """The context executor is a prompt for the LLM, not an audit trail.
+
+    File and line citations belong in task files, DECISIONS records, and the
+    CHANGELOG — never in the instructions the agent reads every turn. The
+    lane behavior (tools, triggers, error strings) stays; the pointers go.
+    """
+    text = _read(EXECUTOR)
+    for literal in (
+        "src/loop.ts",
+        "src/index.ts",
+        "src/goal.ts",
+        "src/tools.ts",
+        "src/state.ts",
+        "src/verifier.ts",
+        "src/evidence.ts",
+        "server.py",
+        "205-437",
+        "no Brain mention is added",
+    ):
+        assert literal not in text, f"code reference in executor: {literal}"
+    assert "goal_set" in text
+    assert ".opencode/STOP_GOAL" in text
```
<!-- END_GIT_DIFF -->
