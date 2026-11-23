# Task 415: Force project-tree generation and code-search context attachment on brain requests

**File:** `tasks/in-progress/415-force-project-tree-and-code-search-context-on-brain-requests.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress
**Started:** 2026-11-22T19:46:09Z

## Goal

Force the cognitive-executor (and cognitive-discovery) to always generate a project tree of the feature or codebase under work and attach it to every `brain_turn` request, so the Brain knows which files to collect and can help the Hands use the `code-search` skill to find graphs, files, and contexts. This closes the gap between the discovery workflow (graph build, directory tree, signatures) and the Brain's context feed: today the Hands may send a `brain_turn` with `context_paths` that are guessed or incomplete; the desired behavior is a deterministic "map first, then feed" step that produces a project tree plus a context manifest and attaches both to the Brain request.

## Manager's Notes

- The `code-search` skill (`~/.config/opencode/skills/code-search/SKILL.md`) defines the discovery workflow: memory before map → archive-aware graph build → directory tree → graph-vector hybrid → verify every hit → extract signatures → halt and hand over. It is the authoritative source for how context is gathered.
- The `cognitive-executor` agent (`agents/cognitive-executor.md`) already mandates MCP-first context and subagent delegation, but does not force a project-tree artifact to be attached to `brain_turn`. The `cognitive-discovery` subagent (`agents/cognitive-discovery.md`) produces a `### Context Manifest` with `Context-Paths` — that manifest is the natural attachment.
- The gap: there is no explicit, non-skippable step that (a) generates a project tree (via `custom_context_get_directory_tree` or `create_tree_report`), (b) builds/queries the graph, (c) extracts signatures, and (d) attaches the resulting paths to the Brain request. Without it, the Brain cannot reliably know which files to collect, and the Hands may under-feed context.
- Desired behavior: before any `brain_turn` that carries `context_paths`, the Hands must have produced and attached a project tree (directory tree at depth ≥3) plus the Context-Paths manifest from discovery. The Brain then uses the tree to decide which files to request in full.
- This is an HQ-only change touching `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`, and the `code-search` skill. It must not leak into project-agnostic governance scaffolding.
- Related: Task 414 (enhance fragments/agents with best practices) and the research report `context-reports/agent-harness-system-prompts-research.md` (context engineering, right altitude, minimal high-signal tokens).

## Local TODOs

- [ ] Locate all `brain_turn` invocation sites in `agents/cognitive-executor.md` and `agents/cognitive-discovery.md` and the fragment `09-hands_protocols.md` (discovery/implementation/combined templates)
- [ ] Add a mandatory "Project tree + context manifest" step before any `brain_turn` that carries `context_paths`: generate directory tree (depth ≥3, capped entries), build graph, extract signatures, emit Context-Paths manifest
- [ ] Define the attachment shape: `context_paths` must include the directory-tree report path (if saved) plus the discovered file paths; never a bare label
- [ ] Update `code-search` skill to state that the project tree + manifest is a required hand-off artifact before `brain_turn` (autopilot) or Manager hand-off (manual)
- [ ] Update `cognitive-discovery` subagent to make the project tree mandatory in its return (not optional)
- [ ] Add a verification gate: `brain_turn` calls without a Context-Paths manifest are invalid; lint/check that every task file's discovery phase records a Context-Paths manifest
- [ ] Update `AGENTS.md` "Context Bootstrapping" and "MCP-First Context" sections to reference the new mandatory step
- [ ] Update sibling `README.md` and append dated ADR to `DECISIONS.md` in `agents/` and `prompts/fragments/` where domain contracts changed
- [ ] Update CHANGELOG.md via Parse-Then-Append

## Acceptance Criteria

- [ ] Every `brain_turn` invocation site in `agents/cognitive-executor.md` and `09-hands_protocols.md` is preceded by a mandatory project-tree + context-manifest step
- [ ] The `code-search` skill documents the project tree + manifest as a required hand-off artifact before `brain_turn`
- [ ] `cognitive-discovery` subagent returns a project tree (depth ≥3) plus Context-Paths manifest in every report
- [ ] A verification gate rejects `brain_turn` calls that lack a Context-Paths manifest
- [ ] `lint_task_file` passes on this task file
- [ ] `npx prettier --write "**/*.md"` applied to changed Markdown
- [ ] Sibling `README.md` and `DECISIONS.md` updated where domain contracts changed
- [ ] CHANGELOG.md updated via Parse-Then-Append

## Verification Evidence

- **Test command:** rtk test npx prettier --check "**/*.md"
- **Expected result:** exit 0, no formatting errors
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Forcing a project-tree step on every `brain_turn` increases token cost and latency; needs a skip condition for trivial tasks (e.g., single-file edits with known paths). Mitigation: define a "trivial task" exemption in the protocol.
- **Risk:** The `code-search` skill and `cognitive-discovery` subagent must stay in sync; changes to one must be mirrored in the other.
- **Risk:** HQ-only changes (agents/, prompts/fragments/) must not leak into project-agnostic governance scaffolding (`skill-templates/governance`).
- **Rollback plan:** Git revert of changed agent/fragment/skill files. No data migration involved.

## Execution Log & Reasoning

### Brain Plan (verbatim)

**[Senior Programmer]**

Plan ready. Nineteen `brain_turn` sites exist across the two files, not the handful the task assumes, and three of the task file's own premises need a decision before implementation. No XML is emitted because this is a planning turn, and the Hands drives the approval gate from this report.

The three things you should see before the plan:

- **The `code-search` skill lives outside the workspace.** Editing `~/.config/opencode/skills/code-search/SKILL.md` triggers the executor's `external_directory: ask` permission, and it changes behaviour for every project on the machine. That collides with the task's own "HQ-only, must not leak" constraint. Recommendation: keep the rule in-repo.
- **Acceptance Criterion 4 as written implies a code change.** "A verification gate rejects `brain_turn` calls" can only mean a change inside `mcp-brain-bridge`. A prompt-level preflight is implementable today. Pick one.
- **`cognitive-discovery.md` currently forbids the change.** Its `§How to Work` step 2 says "persist a tree report only when asked". That single sentence is why the map never reaches the Brain.

<reasoning_log>
1. Logical dependencies and constraints.
   1.1 Policy first. The turn is a planning turn under the Planning Gate, so the deliverable is a plan, not an XML task block. The explicit instruction repeats that. The automatic-mode emission rule binds XML blocks only, so a REPORT satisfies both the mode line and the instruction. No relay sentences, because the Hands chains.
   1.2 Order. Enumerate sites from injected text, then design the rule, then the attachment shape, then the file table, then gates, then the decisions that must precede implementation. Reversing would let a design centre on sites I had not counted.
   1.3 Prerequisites. I hold the full executor, the full discovery agent, `agents/README.md`, fragment `09`, fragment `07`, `docs/conventions.md`, `docs/architecture.md`, `docs/data_model.md`, `DESIGN.md` and the task file. I do not hold `AGENTS.md`, the bridge source, the skill file, or the bundle composition.
   1.4 Manager constraints. Plan only, structured report, exact files, verification gates, no invented files, no scope widening beyond the three named targets.

2. Risk assessment.
   2.1 Highest risk is a rule that binds 19 sites by restatement. That is the duplication defect the earlier audit named as the root cause of ten findings. Mitigation baked into the design: one normative block, one-line pointers at each site.
   2.2 Second risk is an external write. `~/.config/opencode/skills/code-search/SKILL.md` is outside the workspace and global in effect. The task declares it in scope and simultaneously demands no leakage. That is a task-file contradiction, so it becomes a decision rather than a silent default.
   2.3 Third risk is token cost. A 400-entry tree per Class A turn is 3-5k tokens. Mitigated by turn classes, so review turns carry a diff-scoped manifest instead of a tree.
   2.4 Fourth risk is edit collision with the 414 plan, which rewrites Core Protocol, Brain Bridge and the finalization chain. Mitigated by append-only placement plus pointer lines.

3. Abductive reasoning and hypotheses tested.
   3.1 "The sites are few." Counted 19 clauses across 14 executor sections and 5 template sections. Hypothesis rejected. The task's phrase "every `brain_turn` request" is therefore also wrong as stated, because four of the sites are control turns where a tree is pure waste.
   3.2 "A trivial-task exemption is needed." Rejected. Trivial work never reaches a planning call, because the Manager's words are already the plan under the Planning Gate. The exemption is a turn class, not a task size, and it needs no new branch.
   3.3 "The tree belongs in the auto-bundle." Filed as unverified. The executor says a five-file bundle attaches automatically, and I do not know its composition. If the tree is already there, only the audit line is needed.
   3.4 "`create_tree_report` output has a stable path." Rejected. `docs/data_model.md` names `context-reports/tree_report_<timestamp>_<uuid>.md`, so the path changes per call and must be carried by the audit line rather than pinned.
   3.5 "AC4 is prompt-level." Rejected on reading. A rejection of a call is server behaviour. The plan therefore offers both readings and recommends the cheap one first.
   3.6 "The discovery agent already returns the tree." Rejected against its own text: "persist a tree report only when asked". That sentence is the defect.

4. Outcome evaluation and adaptability.
   4.1 A first draft required the tree on all 19 sites. Routing control turns as exempt cut the cost roughly in half without weakening the goal, because a closure turn carries no repo question.
   4.2 A first draft put the audit line in the Execution Log only. Moving it into the prompt beside the mode line makes it visible to the Brain and greppable by QA, which is the only way the gate can be checked.
   4.3 A draft step to also rewrite `docs/architecture.md` §Key Data Flows was dropped. It is outside the task's declared scope and would blur an already-wide diff.

5. Information availability.
   5.1 Used and cited: executor, discovery agent, `agents/README.md`, fragments `09` and `07`, three docs, `DESIGN.md`, task 415.
   5.2 Absent and declared in §9: `AGENTS.md`, `mcp-brain-bridge` source, the skill file text, the bundle composition, and whether `context-reports/` is gitignored.
   5.3 No file, shell or network access by design.

6. Precision and grounding.
   6.1 Every site in the inventory names a heading that exists in the injected text, and every tool named exists in Core Protocol 3 or the discovery agent.
   6.2 Where the task file contradicts itself, I quote it rather than paraphrase. The HQ-only versus global-skill tension is quoted from `## Manager's Notes`.
   6.3 I do not name a bridge parameter I have not seen. `context_paths`, `include_diff` and `include_bundle` are grounded in the executor text, so only those are used.

7. Completeness.
   7.1 All five requested elements are answered as numbered sections: sites, mandatory step, attachment shape, file list, gates.
   7.2 Two adjacent defects found while reading are listed but explicitly deferred, so the diff stays honest.
   7.3 Incompleteness is declared rather than papered over in §9, and D4 turns the largest unknown into a pre-implementation check.

8. Persistence and patience.
   8.1 Nothing failed this turn.
   8.2 This is the first planning turn for task 415, so the two-planning-turn ceiling is not approached.

9. Inhibit response.
   9.1 Pre-emit check. No XML task block. No relay instruction. No invented path. No semicolon or em-dash chain in the report prose. Every command is one I can construct from the injected text or from the task file's own verification section.
   9.2 Verified. Emitting.
</reasoning_log>

## 1. Site inventory

Nineteen clauses invoke or configure `brain_turn`. Ten in the executor plus five template sites require a map. Four executor sites are control turns and are exempt by class.

| # | File | Section | Turn class |
|---|---|---|---|
| E1 | `agents/cognitive-executor.md` | `## Planning Gate` | A |
| E2 | same | `### Supervised autopilot plan approval` | A |
| E3 | same | `### Discovery-fed planning` (fed retry and manifest extraction) | A |
| E4 | same | `## Manual Workflow` step 4 | B |
| E5 | same | `### Mandatory manual review chain` (QA call) | B |
| E6 | same | `### Mandatory manual review chain` (Reviewer call) | B |
| E7 | same | `## Brain Bridge` §State machine step 1 Build and step 2 Call | A or B by content |
| E8 | same | §State machine step 3 Relay | C |
| E9 | same | §State machine step 5 Empty output retry | C |
| E10 | same | `### Review-approval relay` (answer envelope) | C |
| E11 | same | `### Review-approval relay` (closure XML) | C |
| E12 | same | `### Autopilot mode (default OFF)` (chained QA, re-QA, review) | B |
| E13 | same | `### Saga self-sufficiency` (reviewer call) | B |
| E14 | same | `### File context retrieval` | A |
| T1 | `prompts/fragments/09-hands_protocols.md` | discovery `summary_phase` | A |
| T2 | same | implementation `summary_phase` step 4 | B |
| T3 | same | combined `conditional_implementation_phase` | A |
| T4 | same | combined `summary_phase` step 1 | A |
| T5 | same | combined `summary_phase` step 4 | B |

Roughly a dozen other lines mention `brain_turn` descriptively, such as the capability-manifest diagnostic and the Code Mode routing note. Those carry no call and need no pointer.

## 2. The mandatory step

One normative block, inserted once, plus a one-line pointer at each of the 15 map-bearing sites. Restating the rule at 19 sites would recreate the duplication defect the audit traced ten findings to.

Insert verbatim as a new section in `agents/cognitive-executor.md`, placed after `### File context retrieval` and before `## Personas Roster`:

```markdown
## Context Map Before Brain Calls (mandatory)

The Brain sees only what a `brain_turn` carries. A call that asks for a plan, an implementation
XML, or a verdict without a map of the codebase makes the Brain guess a path, and a guessed
path costs a round trip. Produce the map and attach it before every such call.

### Turn classes

| Class | Turns | Map required |
| ----- | ----- | ------------ |
| A, plan or implementation | planning turns, revised-plan turns after discovery, plan-approval routing, fed-context turns | Full: graph, tree, manifest |
| B, review or verdict | QA, re-QA, Code Reviewer, hotfix and postfix | Diff-scoped manifest |
| C, control | relay answers, closure XML request, empty-output retry, mode changes | Exempt |

### Producing the map (Class A)

1. **Graph once.** Run `build_graph` for the scope, then answer questions with `query_graph`,
   `explain_node` and `god_nodes`. A stale graph is rebuilt, never trusted.
2. **Tree at depth 3 or deeper.** Run `get_directory_tree`, then `create_tree_report` to persist
   it. Cap the tree at 400 entries and state the cap in the report when it truncates. The
   persisted path follows the convention in `docs/data_model.md`.
3. **Manifest.** Produce one `path#Lstart-end` entry per file the work touches, using
   `extract_signatures` and `read_source_files`. Verify every hit before attaching it: the path
   exists, the range covers the symbol, and the file answers the question. Drop unverified hits.
   This mirrors the invariant in `agents/cognitive-discovery.md`.
4. **Attach.** Pass every manifest path and the tree report path in `context_paths=[...]`. Open
   the prompt's `[fed-context]` block with the same list as an index. The index never replaces
   the paths.

### Producing the map (Class B)

Derive the manifest from the diff the turn carries. One entry per changed file. Use a whole-file
range when the file is under 200 lines, otherwise the hunk ranges. Add the tree only when a hunk
sits in a directory the manifest does not already name.

### The audit line (mandatory, every call)

Every `brain_turn` prompt carries one line beside the mode line:

- `Context-Map: full (tree=<path>, files=<n>)` for Class A
- `Context-Map: diff-scoped (files=<n>)` for Class B
- `Context-Map: exempt (class C: <reason>)` for Class C

A prompt without this line is malformed, exactly like a prompt without its mode line. A `full`
or `diff-scoped` claim carrying zero paths is a falsified claim: produce the map, or record the
real exempt reason.

### Forbidden shapes

- A bare label in `context_paths`, for example `"the executor"`. Directories, wildcards and
  unverified paths are rejected.
- A prose `[fed-context]` with no paths and no inline ranges. It predicts a second
  `missing_context`.
- A tree report path that does not exist. Persist it first, then name it.

### No trivial-task branch

Trivial work is exempt because it never reaches a planning call: when the Manager's words are
already the plan, the Planning Gate skips the planning round entirely. A one-file change still
runs Class A on its planning turn and Class B on its review turn, and Class B costs one entry.
Cost control is range discipline and a capped tree, never skipping the map.
```

## 3. Attachment shape

Concrete target for a Class A call:

```text
MODE: AUTOMATIC (autopilot locked) …
Context-Map: full (tree=context-reports/tree_report_20261122T194610Z_a1b2c3d4.md, files=7)

[fed-context]
Index (same paths are passed in context_paths):
- context-reports/tree_report_20261122T194610Z_a1b2c3d4.md#L1-L180
- agents/cognitive-executor.md#L1-L120
- agents/cognitive-discovery.md#L1-L60
- prompts/fragments/09-hands_protocols.md#L1-L95
<verbatim ranges follow>
```

Rules the shape enforces:

- The tree path is concrete and freshly written, never a stable alias, because `docs/data_model.md` gives the report a timestamp and uuid and a stable alias would need a freshness check.
- Every manifest entry carries a line range. The discovery invariant already forbids range-free entries.
- The audit line mirrors what `context_paths` carries, so a mismatch between claim and payload is visible in the transcript without a tool call.

## 4. Files to edit

| File | Change | Why |
|---|---|---|
| `agents/cognitive-executor.md` | Append the §2 block, then add one pointer line at E1, E2, E3, E4, E5, E6, E7, E12, E13 and E14. Insert-only, no rewrite of surrounding text | Single normative home, minimal collision with the 414 plan |
| `agents/cognitive-discovery.md` | Replace `§How to Work` step 2 ("persist a tree report only when asked") with a mandatory persist, depth 3 or deeper, 400-entry cap. Add the tree path above `### Context Manifest` in `§What You Return` | This one sentence is the reason the map never reaches the Brain |
| `agents/README.md` | Extend the existing Context-Paths invariant bullet with the tree requirement and the turn-class line. Correct `bash` to `shell` in the free-tier note | Keeps the slice README true to the contract it documents |
| `prompts/fragments/09-hands_protocols.md` | Five template edits at T1 to T5, each one line naming the audit line and `context_paths`. Also fix the implementation `summary_phase` numbering gap where the list jumps 5 to 7 | The templates are where the Hands actually learns the call shape |
| `prompts/fragments/07-agent_skills_registry.md` | Extend the `code-search` line: its output is the required hand-off artifact before any `brain_turn` carrying `context_paths` | In-repo, versioned with the prompt, present on every project |
| `AGENTS.md` | Read first. Add one pointer line in the `Context Bootstrapping` and `MCP-First Context` sections | Task requires it. Text cannot be specified without reading the file |
| `agents/DECISIONS.md` and `prompts/fragments/DECISIONS.md` | Dated ADR recording the context-map contract, the turn classes and the global-skill decision | Local TODOs require it, and the contract is architectural |
| `CHANGELOG.md` | Parse-Then-Append | Definition of Done |
| `~/.config/opencode/skills/code-search/SKILL.md` | **Do not edit under the recommended path.** See D2 | Outside the workspace, global in effect, contradicts the task's own HQ-only constraint |

Two adjacent defects found while reading, listed so the diff stays honest and **not** included: `agents/README.md` says "keep bash in the tool allowlist" while `cognitive-discovery.md` denies `shell`, and `cognitive-discovery.md` `§Your Tools` grants `skill` while executor `§Subagent Delegation` rule 5 states subagents have no `skill` tool. Both belong to the 414 cycle.

## 5. Verification gates

1. **Baseline.** `grep -c "brain_turn" agents/cognitive-executor.md prompts/fragments/09-hands_protocols.md` before the first edit. Record both numbers.
2. **Completeness matrix.** A 19-row table in the task file's Execution Log with columns `site | class | pointer added | verified by`. This is the real gate. A regex cannot prove that a pointer sits at the right call.
3. **Presence.** `grep -c "Context-Map" agents/cognitive-executor.md` returns 15 or more, meaning 10 pointers plus the block's examples. `grep -c "Context-Map" prompts/fragments/09-hands_protocols.md` returns 5 or more.
4. **Negative, discovery.** `grep -rn "persist a tree report only when asked" agents/` returns nothing.
5. **Negative, bare labels.** `grep -rn 'context_paths=\["' agents/ prompts/fragments/` returns nothing, meaning no example teaches a bare label.
6. **Format.** `npx prettier --check "**/*.md"` exits 0.
7. **Lint.** `lint_task_file` passes on `tasks/in-progress/415-force-project-tree-and-code-search-context-on-brain-requests.md`. The task file currently sits in `tasks/backlog/` and must move through `claim_next` first.
8. **ADR.** `grep -n "Context Map" agents/DECISIONS.md` returns at least one hit.
9. **No self-pass.** A green run without the matrix from gate 2 is a failed run. That closes the exact loop that let task 414 pass its own gate.

## 6. Risks

- **R1, token cost.** A 400-entry tree is 3-5k tokens on every Class A turn. Class B avoids it, and the cap is mandatory.
- **R2, contradiction until edited.** While `cognitive-discovery.md` still says "only when asked", the subagent will not persist the tree and the manifest will lack its path. This edit must land in the same change, not after it.
- **R3, external write.** Editing the global skill changes behaviour for every project on the machine. Covered by D2.
- **R4, collision with 414.** The 414 plan rewrites Core Protocol, the finalization chain and Brain Bridge. Append-only placement plus pointer lines keeps this task out of those hunks.
- **R5, rubber stamp.** An audit line reading `full` with zero paths defeats the gate. The forbidden-shape clause plus QA spot-check is the countermeasure.
- **R6, working-tree noise.** `create_tree_report` writes a new file per call. Verify whether `context-reports/` is gitignored before the first run, and if it is not, say so in the ADR rather than deleting reports silently.

## 7. Sequencing against task 414

Run 415 now, append-only. It touches `### File context retrieval`, the discovery agent, and three template blocks, none of which the 414 plan rewrites. The overlapping sections, Core Protocol and the finalization chain, receive one-line pointers only, which will not conflict with a later rewrite of their bodies. The reverse order would stall 415 behind a ten-item refactor.

## 8. Decisions the approval gate must carry

- **D1, meaning of AC4.** Prompt-level preflight with the audit line, or a code-level rejection in `mcp-brain-bridge`? Recommend prompt-level now, with the bridge check as a separate task once its source is read.
- **D2, the skill file.** Edit the global `code-search` skill (R1) or keep the rule in-repo (R2)? Recommend R2, because a versioned prompt fragment is reviewed and shipped with the repo while a global file is neither.
- **D3, sequencing.** 415 now, append-only, or after 414 Cycle A? Recommend now, per §7.
- **D4, the auto-bundle.** The executor says a five-file bundle attaches automatically. Verify its contents before implementation. If the tree already rides there, only the audit line is needed and step 4 of the block shrinks.

## 9. What I could not verify

`AGENTS.md` content and its two named sections. The `mcp-brain-bridge` source, so bridge-side validation is unknown. The five-file bundle composition. The current text of `~/.config/opencode/skills/code-search/SKILL.md`, which I hold only as the task file describes it. Whether `context-reports/` is gitignored.

<missing_context>
AGENTS.md
</missing_context>

Next action: the Hands presents this plan in chat under the Plan presentation contract, puts D1 through D4 into the question body with one answer slot, and asks for approval. On approval it chains `brain_turn` under the same `task_id` for the implementation XML.


_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
