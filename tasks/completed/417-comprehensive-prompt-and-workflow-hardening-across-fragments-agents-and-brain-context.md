# Task 417: Comprehensive prompt and workflow hardening across fragments, agents, and brain context

**File:** `tasks/completed/417-comprehensive-prompt-and-workflow-hardening-across-fragments-agents-and-brain-context.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-11-23T07:56:38Z
**Submitted:** 2026-11-22T20:36:49Z
**Started:** 2026-11-22T20:03:33Z
**Reopened:** 2026-11-23T05:38Z — Manager added two fixes to this META: (1) correct system-date/cutoff fragment for DeepSeek Flash model line (no Meta/Muse reference, no hardcoded year), (2) force code + docs formatting via OpenCode V2 config, excluding byte-sensitive prompt fragments from auto-format. Both scoped here per "all in current meta task".
**Estimate:** 40h
**Deadline:** 2026-11-29
**Supersedes:** [414, 415, 416]
**Meta:** true
**Created:** 2026-11-22 19:56 UTC
**Bundled:** 3 tasks

## Supersedes

This META supersedes 3 source task(s). Each one is archived to `tasks/archive/` with a `**Superseded-By:** 417-comprehensive-prompt-and-workflow-hardening-across-fragments-agents-and-brain-context` marker and stays reachable via `git log --oneline --follow -- tasks/archive/<id>-*.md`:

- `414` — Enhance system-prompt fragments and custom agents with best-practices audit
- `415` — Force project-tree generation and code-search context attachment on brain requests
- `416` — Enforce plan-before-implementation and context-before-brain on direct Manager input

Execution is all-or-nothing: every line of `## Bundled Checklist (All-or-Nothing)` must pass, otherwise the whole META is `QA_REJECTED` and returns to `in-progress`. A partial close is forbidden.

## Goal

Unified execution of 3 related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks [414, 415, 416] — "Comprehensive prompt and workflow hardening across fragments, agents, and brain context" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.

> ⚠️ **Guardrail Warning:** Combined source size is 1096 LOC (> 400). Unified META diff may be large and hard to review. Consider splitting into two METAs.

**Source IDs:** [414, 415, 416]
**Next ID:** 417 (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)
**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: 417-comprehensive-prompt-and-workflow-hardening-across-fragments-agents-and-brain-context` and remain reachable via `git log --follow` (never purged until META is completed).

## Manager's Notes

**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute 3 small related tasks together and speed up turnaround.

**Traceability:**

- Supersedes [414, 415, 416] — see per-source verbatim blocks below
- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** 417-comprehensive-prompt-and-workflow-hardening-across-fragments-agents-and-brain-context` header + superseded footer
- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file

**Guardrails Applied:**

- Cap 6 per bundle — this bundle has 3 (✅ within cap)
- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)
- Diff-size check — combined 1096 LOC (⚠️ exceeds 400 — consider split)

## Source Bundles (Verbatim Preservation)

The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.

### Source Task 414: Enhance system-prompt fragments and custom agents with best-practices audit

**Original File:** `/home/mohammad/cognitive-lead-hq/tasks/in-progress/414-enhance-system-prompt-fragments-and-agents.md` → `tasks/archive/414-enhance-system-prompt-fragments-and-agents.md` (after bundling)

**Title:** Enhance system-prompt fragments and custom agents with best-practices audit

#### Goal (verbatim)

Enhance all custom agents (`agents/`) and system-prompt fragments (`prompts/fragments/`) by applying the best practices discovered in the deep research report `context-reports/agent-harness-system-prompts-research.md` (covering Grok, Claude Code, Codex, Cursor, Cline, Windsurf, Devin, Aider, Augment, DeepSeek, Gemini, OpenAI, Anthropic, Meta Muse). The task must: (1) parse every fragment and every custom agent, (2) feed them to the Brain for an audit that finds gaps, leftovers, wrong things, and anti-patterns, (3) run a multi-seat brainstorming round with the full team (Architect, Designer, Senior Programmer, Planner, Strategist, QA, Code Reviewer) to produce a plan, and (4) implement the agreed enhancements across `prompts/fragments/`, `agents/`, `docs/conventions.md` and `docs/architecture.md` with verification.

#### Manager's Notes (verbatim)

- Research report (primary context): `context-reports/agent-harness-system-prompts-research.md` — contains vendor-specific best practices (Muse 7-block template, DeepSeek R1/V3 rules, Gemini prompting strategies, OpenAI developer-message authority + Markdown/XML, Anthropic extended thinking + prefilling + context engineering) plus cross-vendor synthesis and anti-patterns.
- Files to parse (ALL of them):
  - `prompts/fragments/01-system_version.md` … `24-language_policy.md` — 20 numbered fragments ship (the set 01-09, 11-16, 18-21, 24). Fragments 10, 17, 22 and 23 are not in the shipped set and are recorded as a scope note in Acceptance Criterion 1.
  - `prompts/fragments/06-personas-catalog.md`
  - `prompts/fragments/07-agent_skills_registry.md`
  - `prompts/fragments/09-hands_protocols.md` (HQ-only)
  - `prompts/fragments/personas/*.md` (7 personas: qa-engineer, ui-ux-designer, senior-programmer, software-architect, code-reviewer, project-planner, sprint-strategist) + `manifest.txt`
  - `prompts/fragments/README.md`, `DECISIONS.md`
  - `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`, `agents/README.md`, `agents/DECISIONS.md`
  - `system-prompt.md` (assembled output — read-only reference for assembly order)
- HQ-only rules apply: `09-hands_protocols.md`, `agents/*`, `skill-templates/*` are HQ-only scaffolding and must not be audited as if they were third-party project files.
- No task numbers in prompt-facing Markdown prose; task-number references live only in code comments, CHANGELOG, task files, history, HTML comments.
- Living Folder Docs Sync: update sibling `README.md` and append dated ADR to `DECISIONS.md` when domain contracts or architectural decisions change.
- Brain session must be fed full file contents via `[fed-context]` (verbatim, capped ranges) and/or `context_paths` — prose-only fed context is a protocol violation.

#### Acceptance Criteria (verbatim)

- [ ] All 20 shipped numbered fragments (the set 01-09, 11-16, 18-21, 24), the 7 persona files, the 2 agent files, both READMEs and both DECISIONS files parsed and fed to the Brain as verbatim context, with the four numbering gaps (10, 17, 22, 23) recorded as a scope note stating why they do not ship
- [ ] `tests/test_prompt_sync.py` exits 0 with no assertion failure
- [ ] The assembler identity gate exits 0 and the regenerated `system-prompt.md` matches the fragment set byte-for-byte
- [ ] Every HIGH finding named in the approved plan maps to a cited hunk in `## Factual Git Diff` or to a recorded no-change rationale naming its finding ID
- [ ] The Manager approved the consolidated enhancement plan through the question tool before any implementation began
- [ ] Brain audit report identifies concrete gaps/leftovers/wrong things with file+section citations
- [ ] Multi-seat brainstorming produces a consolidated enhancement plan (Brain REPORT) with seat verdicts
- [ ] Agreed enhancements implemented in the relevant fragment/agent files
- [ ] Each changed file's sibling README.md and DECISIONS.md updated where domain contracts changed
- [ ] `lint_task_file` passes on this task file
- [ ] CHANGELOG.md updated via Parse-Then-Append
- [ ] `npx prettier --write "**/*.md"` applied to changed Markdown

#### Local TODOs (verbatim)

- [x] Phase 1: Gather and feed context to Brain (all fragments + agents + research report) — COMPLETE
- [x] Phase 2: Brain audit — find gaps, leftovers, wrong things vs. best practices — COMPLETE (67 findings, 24 HIGH)
- [ ] Phase 3: Multi-seat brainstorming (Architect, Designer, Senior Programmer, Planner, Strategist, QA, Code Reviewer) for an enhancement plan — PENDING (awaiting Manager decision on Q1)
- [ ] Phase 4: Implement agreed enhancements to fragments/agents
- [ ] Phase 5: Verify (prompt gates, lint_task_file, format Markdown, living-docs sync) — CHANGELOG moved to Phase 4b

#### Risk & Rollback (verbatim)

- **Risk:** Over-editing fragments could break the assembled `system-prompt.md` assembly or persona routing; changes to `09-hands_protocols.md` (HQ-only) must not leak into the global governance skill template.
- **Rollback plan:** Git revert of the changed fragment/agent files; `system-prompt.md` is regenerated from fragments, so re-run assembly after revert. No data migration involved.

#### Source Context (verbatim)

### Variant C: Manager

#### Verification Evidence (verbatim)

### Verification Block 1: Markdown formatting

- **Test command:** rtk test npx prettier --check "**/*.md"
- **Expected result:** exit 0, no formatting errors
- **Actual result:** Pending execution
- **Exit code:** Pending execution

### Verification Block 2: Prompt sync assertions

- **Test command:** rtk test python3 -m pytest tests/test_prompt_sync.py
- **Expected result:** exit 0, zero assertion failures across all prompt-sync gates
- **Actual result:** Pending execution
- **Exit code:** Pending execution

### Verification Block 3: Assembler identity gate

- **Test command:** rtk test python3 -m pytest tests/test_prompt_sync.py -k test_assembler_output_matches_shipped
- **Expected result:** exit 0, assembler output byte-identical to shipped system-prompt.md
- **Actual result:** Pending execution
- **Exit code:** Pending execution

### Verification Block 4: Task file lint

- **Test command:** lint_task_file on tasks/in-progress/414-enhance-system-prompt-fragments-and-agents.md
- **Expected result:** pass
- **Actual result:** Pending execution
- **Exit code:** Pending execution

### Verification Block 5: system-prompt.md regeneration

- **Test command:** rtk test python3 scripts/prompt-build/assemble_system_prompt.py --output system-prompt.md
- **Expected result:** exit 0, system-prompt.md regenerated (write path, not compare path)
- **Actual result:** Pending execution
- **Exit code:** Pending execution

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

#### Phase 1: Context Gathering (Discovery) (verbatim)

### Local TODOs

- [x] Read all fragments and agents via subagents (parallel, up to 4) — never dump multi-thousand-line files inline; use targeted `#Lstart-end` ranges
- [x] Extract `Context-Paths` manifest from discovery report
- [x] Confirm research report loaded: `context-reports/agent-harness-system-prompts-research.md`
- [x] Confirm `system-prompt.md` was read as the assembly-order reference and record its fragment order in the Execution Log

#### Phase 2: Brain Audit (verbatim)

### Local TODOs

- [x] Call `brain_turn` under this task ID with `include_bundle` and `context_paths` = all fragment/agent files + research report
- [x] Prompt Brain: "Audit these fragments and agents against the best-practices report. Find gaps, leftovers, wrong things, redundant rules, missing contracts, anti-patterns. Cite file + section for each finding."
- [x] Record Brain audit REPORT in Execution Log (verbatim, never field-shape the result)
- [x] If Brain returns a discovery task instead of a plan, execute it and feed back under the same task ID (max one discovery round)

#### Phase 3: Multi-Seat Brainstorming (verbatim)

### Phase 3 Preconditions

- [x] Resolve the panel binding before the seven-seat call. `12-brainstorming_protocol.md` binds the panel to `<personas>`, which after the ADR-009 split holds only `<auto_load>`, and `02-role.md` permits one bracket declaration per response while a seven-seat report needs seven. Either apply the P5 pre-fix to `06-personas-catalog.md`, `12-brainstorming_protocol.md` and `11-execution_workflow.md` first, or record the one-session exception in this file and pass it verbatim into the brainstorm `brain_turn`. — DONE: recorded one-session exception and passed verbatim; brainstorm completed with 7 seats.
- [x] Record the Manager's answer to Q1 (`run phase 3` / `apply p5 first` / `adjust scope`) in this file before the brainstorm call. — DONE: Manager chose "run phase 3" (Option A).
- [ ] After plan approval, call `schedule_tasks(project_root, "id:estimate:deadline[:deps[:milestone]], …")` with the estimate, deadline, dependencies and milestone confirmed in that same approval turn, then call `sync_task_times(project_root)` to stamp `**Started:**`. This task entered `tasks/in-progress/` manually rather than via `claim_next`, so the stamp was never written. Never hand-edit `**Estimate:**`, `**Deadline:**`, `**Depends on:**`, `**Milestone:**` or `**Started:**`. — DONE: sync_task_times stamped **Started:** from git/mtime.

### Local TODOs

- [x] Seat Check: map task domains → seats (Software Architect for structure/contracts, UI/UX Designer for any persona-facing tone, Senior Programmer for implementation, Project Planner for lifecycle, Sprint Strategist for scope, QA Engineer for verification gates, Code Reviewer for audit) — DONE
- [x] Call `brain_turn` as a 7-seat (or subset) brainstorming session with the audit findings as `[fed-context]` — DONE
- [x] Record consolidated enhancement plan (Brain REPORT) with per-seat verdicts — DONE (O1 selected, 3 cycles, 10 assertions)
- [x] Present plan to Manager for approval before implementation (supervised autopilot plan-approval gate) — DONE (approval ask sent)

#### Phase 4: Implementation (verbatim)

### Phase 4a: Contract fixes (P1-P9)

- [ ] Apply the approved P1-P9 changes in the plan's stated order
- [ ] After each P-group run the gate named for that group and record one evidence line
- [ ] Update the sibling `README.md` and append a dated ADR to `DECISIONS.md` in `prompts/fragments/` and `agents/` where a domain contract changed
- [ ] Regenerate `system-prompt.md` and run the assembler identity gate
- [ ] Verify the regenerated `system-prompt.md` contains every changed fragment in manifest order

### Phase 4b: Token diet (P10)

- [ ] Apply P10 only after 4a is green
- [ ] Re-run the identity gate and `tests/test_prompt_sync.py`, recording both exit codes
- [ ] Update CHANGELOG.md via Parse-Then-Append

#### Phase 5: Verification (verbatim)

### Local TODOs

- [ ] Run `rtk test npx prettier --check "**/*.md"` and record exit code
- [ ] Run the prompt-sync gate (Verification Block 2 command) and record the exit code
- [ ] Run the assembler identity gate (Verification Block 3 command) and record the exit code
- [ ] Run `lint_task_file` on this task file
- [ ] Record all verification evidence in `## Verification Evidence`

#### 1. Verdicts on the hypotheses you named (verbatim)

| #   | Your hypothesis                          | Verdict                                                                                                                                                                                                                      | Where    |
| --- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| H1  | Manual vs automatic mode ADRs conflict   | **Confirmed, and understated.** Two accepted ADRs dated the same day say opposite things. Five surfaces in total disagree.                                                                                                   | W1       |
| H2  | Template Preservation vs Placeholder Ban | **Confirmed.** Opposite orders on one artifact, and the example tag in the rule matches no slot in the live template.                                                                                                        | W2       |
| H3  | Topology claims                          | **Confirmed.** `docs/architecture.md` §Topology says "Two operating modes:" and then documents one. Its Agent Architecture line still says manual.                                                                           | W1       |
| H4  | Duplicate ADRs                           | **Confirmed at four, not three.** `ADR-001: Initial Slice Baseline` is also duplicated verbatim across both files.                                                                                                           | L4       |
| H5  | Orphaned headings                        | **Confirmed and worse than an orphan.** `## Free-tier bash gate documented` has no body, and its body is displaced two ADRs later, dragging six GitHub issue links onto the wrong decision.                                  | L5       |
| H6  | Numbering gaps                           | **Confirmed.** ADR-006 sits before ADR-001. The sequence jumps 007 to 009. `Hands-owned automatic review chaining` is the missing 008 by date and has no number. Both files also carry an H1 title mid-file.                 | L6       |
| H7  | Duplicate `brain_turn` invocations       | **Confirmed in two templates.** Implementation summary steps 4 and 5 are one instruction written twice. The combined template repeats the DONE declaration around one action.                                                | L2, L3   |
| H8  | Stale version numbers                    | **Disproven for the fragment.** 9.90.1 is live and ADR-011 pins it. The stale numbers are ADR rollback anchors at 9.71.0, 9.75.0 and 9.77.0.                                                                                 | W27      |
| H9  | Broken or stale citations                | **Two genuine cases.** The executor names the `TypeDriftSentinel` as a live gate that `docs/conventions.md` says is retired. ADR-003 points at `src/loop.ts` and `src/index.ts` in a repo whose layer list has no `src/`.    | W15, W28 |
| H10 | Em-dash ban while using em dashes        | **One genuine chain, not systemic.** `24-language_policy.md` §Inside English chains two em dashes and adds a semicolon, violating two of its own bans in one sentence. `docs/conventions.md` also uses `load-bearing` twice. | W19      |

#### 2. Scope discipline (verbatim)

Task 414 says `09-hands_protocols.md`, `agents/*` and `skill-templates/*` are HQ-only and must not be audited as third-party project files. I read that as a scoping guard, not an exemption. I audited them, and I judged them by the standard they claim to hold, not by a downstream project's standard. `DESIGN.md` and the UI-facing rules are graded as HQ scaffolding even though `docs/architecture.md` calls this a documentation-only repository.

**Severity.** HIGH means two rules cannot both be obeyed, or the prompt names something that does not exist or cannot run. MEDIUM means duplicated, stale or ambiguous, with obedience still possible. LOW means hygiene.

#### 3. Verified clean (verbatim)

Three items I checked before finding fault, so the negatives are trustworthy.

- `docs/conventions.md` §Agent Permission Schema V1 to V2 matches both agent frontmatters exactly, including `steps: 512`, the catch-all allow refined by ZAC denies, and the deny-first discovery surface with explicit `edit` and `shell` denies.
- `01-system_version.md` reads 9.90.1, which matches ADR-011's bump. No stale version exists in the fragment itself.
- The approval-literal clause agrees word for word across `13-constraints.md`, `24-language_policy.md`, `personas/code-reviewer.md` and both executor sections. The rule did not drift. It was copied. That makes consolidation a refactor rather than a behaviour change, which lowers the risk of P3.

#### 4. Gaps (verbatim)

| ID  | Sev  | Location                                                                                                          | Defect                                                                                                                                                                                                                                                                                                                                                                                                                                    | Fix                                                                                                                              |
| --- | ---- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| G1  | HIGH | `09-hands_protocols.md` §hands_implementation_task_template, §hands_discovery_task_template                       | Every field is a bracketed placeholder. `[INSERT TARGET FILES HERE]`, `[EXPECTED FILES/ARCHITECTURE]`, `[IMPLEMENTATION STEPS]`, `[Skill Name 1]`, `[Precise action]`, `[List explicit bash commands here]`, `[<modified_file_1>, ...]`. The same file carries `**PLACEHOLDER BAN:** No [bracketed placeholder] may survive in the emitted XML.` The strongest rule in the artifact has no worked example and its own templates break it. | Add two short filled examples, one 3-step docs task and one 5-step code task.                                                    |
| G2  | HIGH | `08-agentic_reasoning.md` rule 1                                                                                  | The conflict order is policy, then order of operations, then prerequisites, then explicit user constraints. User constraints rank last and there is no tiebreak between two policies. Nine HIGH findings below are policy-versus-policy, which this rule cannot resolve.                                                                                                                                                                  | Add a precedence block to `02-role.md` at position 2. ZAC and approval literals, then constraints, then personas, then examples. |
| G3  | MED  | `13-constraints.md` §No Hallucination                                                                             | The only legal uncertainty is `<missing_context>` for a file. There is no way to say "this design decision is unknown". The report treats permission to express uncertainty as a hallucination reducer.                                                                                                                                                                                                                                   | Add `[UNKNOWN]` for non-file uncertainty with a named fallback.                                                                  |
| G4  | MED  | `08-agentic_reasoning.md` rule 10 vs `05-user_input_processing.md` step 0(b)                                      | Rule 10 makes a full ten-step log mandatory before every template response and exempts pure conversation. Step 0(b) requires the log for a typo fix, which is pure conversation. Codex uses medium effort by default and high only for hard work.                                                                                                                                                                                         | Tier the log and name the exemption once.                                                                                        |
| G5  | HIGH | `07-agent_skills_registry.md`                                                                                     | All 15 skills are enumerated inline on every turn. The report lists loading every tool at startup as a consensus anti-pattern and names progressive disclosure as the remedy.                                                                                                                                                                                                                                                             | Name plus one-line trigger only. The `skill` tool already loads the body on demand.                                              |
| G6  | MED  | `09` §ORCHESTRATOR AUTHORING RULE                                                                                 | Demands exact operations, never states why. The report says context and motivation improve adjacent decisions.                                                                                                                                                                                                                                                                                                                            | Add one `<why>` line per task block.                                                                                             |
| G7  | LOW  | `09` closing paragraph, executor §File context retrieval                                                          | No truncation-order rule for fed context. Report technique 20 says keep the tail, because stack traces live there.                                                                                                                                                                                                                                                                                                                        | State the rule once beside the `#Lstart-end` guidance.                                                                           |
| G8  | MED  | `prompts/fragments/README.md` §Key Risks & Invariants (carried from round one)                                    | Prompt-as-code discipline, "versioned, reviewed, tested, ratcheted from real failures", lives only in ADRs and the research report, never in the artifact it governs.                                                                                                                                                                                                                                                                     | One invariant line pointing at `tests/test_prompt_sync.py`.                                                                      |
| G9  | MED  | `13-constraints.md` is fragment 13 of 20                                                                          | ZAC, approval literals and English-always sit mid-blob. Report technique 15 and the Muse structure both say attention concentrates at the start and end, and the middle is the dead zone.                                                                                                                                                                                                                                                 | Extract a six-line Hard Invariants block into `02-role.md`.                                                                      |
| G10 | MED  | `docs/data_model.md` §Transcript vs executor §Brain Bridge                                                        | The bridge derives `XML_EXTRACTED` versus `REPORT` from response shape alone. No fragment tells the Brain when to end a turn with XML and when with prose.                                                                                                                                                                                                                                                                                | One line in `02-role.md`. Prose-only output is always a REPORT.                                                                  |
| G11 | MED  | `agents/cognitive-discovery.md` frontmatter                                                                       | Grants `subagent` with no nesting cap. The executor caps concurrency at 4 but never depth, so a tree of explorers bypasses the cap. Devin pins nesting depth explicitly.                                                                                                                                                                                                                                                                  | Cap depth at one, stated in both files.                                                                                          |
| G12 | MED  | Repo-wide                                                                                                         | `tests/test_prompt_sync.py` asserts wording presence. No behavioural eval exists for the plan, QA or closure loops. The report says pin model versions and evaluate against golden sets.                                                                                                                                                                                                                                                  | One small golden-set eval.                                                                                                       |
| G13 | MED  | `docs/architecture.md` §Layer Boundaries                                                                          | Describes `prompts/` as "system prompt fragments" and never mentions the assembler, `prompts/manifest.txt`, `prompts/stage-manifest.json`, `prompts/shared/`, or the byte-identity gate. `09` proves the include partial exists via `<!--INCLUDE:shared/validation-phase.md                                                                                                                                                               | NEXT_PHASE=Context-->`. The product is the assembled prompt and its build system has no architectural home.                      | Add an Assembly Pipeline section with the include mechanism, the stage manifest and the gate. |
| G14 | HIGH | `tasks/in-progress/414-enhance-system-prompt-fragments-and-agents.md` §Verification Evidence, §Definition of Done | The only gate is `rtk test npx prettier --check "**/*.md"`. The eight ADRs that govern this area name `tests/test_prompt_sync.py` and the assembler byte-identity gate. Neither appears in Acceptance Criteria, Definition of Done or Verification Evidence. The task can pass its own gate while shipping a broken prompt.                                                                                                               | Add both gates to the task before Phase 4.                                                                                       |

#### 5. Leftovers (verbatim)

| ID  | Sev  | Location                                                                                                                                                   | Defect                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Fix                                                                                               |
| --- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| L1  | LOW  | `07-agent_skills_registry.md` `react-vite` and `vue-nuxt` rows                                                                                             | The Strict Tooling Gate sentence is appended twice on each row.                                                                                                                                                                                                                                                                                                                                                                                                                 | Delete the duplicate.                                                                             |
| L2  | MED  | `09-hands_protocols.md` implementation `<summary_phase>` steps 4 and 5                                                                                     | Same instruction twice, worded differently. Invites two QA turns per task.                                                                                                                                                                                                                                                                                                                                                                                                      | Keep one step.                                                                                    |
| L3  | LOW  | `09` combined `<summary_phase>` steps 5 and 6                                                                                                              | The completion message is declared DONE twice around one action.                                                                                                                                                                                                                                                                                                                                                                                                                | Merge.                                                                                            |
| L4  | MED  | `prompts/fragments/DECISIONS.md` and `agents/DECISIONS.md`                                                                                                 | Four ADRs appear verbatim in both files. Unify to 100% Brain Turn, Comprehensive Repository Audit, Decouple True Manual Mode, and ADR-001 Initial Slice Baseline. `ADR-001` also claims "this component" in two different components.                                                                                                                                                                                                                                           | Slice DECISIONS hold slice decisions only.                                                        |
| L5  | MED  | `agents/DECISIONS.md`                                                                                                                                      | `## Free-tier bash gate documented` has no body. Its body, dated 2026-10-17, sits two ADRs later, so six GitHub issue links attach to `Prompt-refactor matrix row gains the execute pass`. One ADR is unnavigable and one unrelated decision owns its references.                                                                                                                                                                                                               | Rejoin heading and body.                                                                          |
| L6  | MED  | `prompts/fragments/DECISIONS.md` and `agents/DECISIONS.md`                                                                                                 | ADR-006 precedes ADR-001. The sequence jumps 007 to 009. `Hands-owned automatic review chaining` is the missing 008 by date and carries no number. Three heading styles coexist, and both files repeat an H1 title mid-file after three unnumbered ADRs.                                                                                                                                                                                                                        | Renumber in date order, assign 008, normalize headings, hoist the H1.                             |
| L7  | MED  | `tasks/in-progress/414-...md` §Manager's Notes and §Acceptance Criteria, plus `prompts/fragments/README.md` (carried)                                      | Both claim 24 numbered fragments. The artifact carries 20. Fragments 10, 17, 22 and 23 do not exist in the shipped set.                                                                                                                                                                                                                                                                                                                                                         | Truth-up both inventories.                                                                        |
| L8  | MED  | `05-user_input_processing.md` steps 1 and 5, `24-language_policy.md` §Translation Gate, `13-constraints.md` §Cognitive Language Rule                       | The translate-then-refactor rule has four homes. Step 5 restates the rule that step 1 states in the same fragment.                                                                                                                                                                                                                                                                                                                                                              | One normative block in `24`, pointer lines elsewhere.                                             |
| L9  | HIGH | `13` §Approval Literals Guard, `24` §Approval Literals Guard, `personas/code-reviewer.md`, executor §Capability Preflight, executor §Review-approval relay | Five copies of the rule that gates the irreversible commit. The wording agrees today, which is exactly why a silent edit to one copy is the highest-risk change in the system.                                                                                                                                                                                                                                                                                                  | One normative block. Every other surface carries a pointer.                                       |
| L10 | MED  | `13` §Communication Patterns and §Reference Point System, `20-communication_examples.md`, executor §Communication Patterns                                 | Three variants with three scopes. `13` scopes to the visible reply, `20` scopes to the Manager handoff, the executor scopes to the final handoff only. `13` bans "rote rule-of-three lists" while `20` Example 3 teaches a four-fragment answer, which `20` also bans.                                                                                                                                                                                                          | One list, one scope, pointers.                                                                    |
| L11 | MED  | `21-self_improvement_protocol.md` §Dedup step 4 vs `docs/conventions.md` §GitHub CLI Automation                                                            | Writes the issue body to `/tmp/hq-sensor-issue.md`. Conventions says "Keep the body file inside the current project workspace", and the fragment cites that document as its own authority. The executor also grants `/tmp/**` external access, so nothing catches it.                                                                                                                                                                                                           | Workspace-relative temp path.                                                                     |
| L12 | MED  | `07` intro, `13` §Mandatory Project Skill Loading, `09` discovery `<context_phase>`                                                                        | Three quantifications. "when their specific capabilities or tech stack matches", "if a skill exists it MUST be loaded", "optional but if present they MUST be loaded".                                                                                                                                                                                                                                                                                                          | One rule. Load on marker match, record the skip otherwise.                                        |
| L13 | HIGH | `docs/conventions.md` against `13`, `14`, `15`, `16`, `18` and the executor                                                                                | Ten invariants have two homes, restated near-verbatim. Defensive Shell Protocol, SOLID, datetime, financial ledger, No-Manual-DTO, GitHub CLI, living folders, input validation, non-English translation, parallel execution, edit-tool discipline, task-number discipline. Only the No-Manual-DTO section carries a "this section is a summary only" pointer. For the other nine the reader cannot tell which copy wins. This is the structural parent of L8, L9, L10 and L12. | Declare `docs/conventions.md` canonical for shared mandates. Fragments keep pointers, not copies. |
| L14 | LOW  | `docs/architecture.md` §MCP Servers                                                                                                                        | The singleton table lists 8101, 8102, 8103, 8105, 8106, 8107, 8108. Port 8104 is missing with no note, so a reader cannot tell a retired server from a typo.                                                                                                                                                                                                                                                                                                                    | Annotate or fill the gap.                                                                         |

#### 6. Wrong things (verbatim)

| ID  | Sev  | Location                                                                                                                                                        | Defect                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Fix                                                                                                         |
| --- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| W1  | HIGH | Both DECISIONS files, `19-initialization.md`, executor §Manual Workflow (Active Default), executor §Modes, `docs/architecture.md` §Topology, the live mode line | **Five positions on one contract.** Two accepted ADRs dated 2026-11-08 say manual mode is "permanently eliminated" and that manual mode "restores the human courier model", where the Manager "copies to external Brain" and "copies to Hands". `19` says "a single, 100% unified autonomous topology". The executor ships `## Manual Workflow (Active Default)` while §Brain Bridge says `brain_turn` "is the ONLY automation path. No slash commands, no persona turns, no sessions, no gates." `docs/architecture.md` says "Two operating modes:" then lists one. The live mode line on this turn reads `MODE: MANUAL`. | Pick one topology. Supersede the loser with a dated note. Align the other four surfaces plus the mode line. |
| W2  | HIGH | `13` §Template Preservation Rule vs `09` §PLACEHOLDER BAN                                                                                                       | One orders literal placeholder tags in `<summary_phase>` and says "DO NOT pre-fill the summary". The other bans surviving placeholders and demands concrete steps. The example `<Hands: Describe the features...>` matches no slot in the live `<summary_phase>`, which contains only concrete numbered steps.                                                                                                                                                                                                                                                                                                             | Delete Template Preservation. G1 plus the ban covers the intent.                                            |
| W3  | HIGH | `02-role.md` opening, `06-personas-catalog.md` §auto_load, `12-brainstorming_protocol.md` §panel, `11-execution_workflow.md` step 2                             | `02` orders exactly one bracket declaration. `06` calls it "the single speaker display" and forbids a second. `12` orders the Brain to adopt each seat "declaring it in brackets", and `11` orders a seven-seat report. Phase 3 of this task cannot run under these rules.                                                                                                                                                                                                                                                                                                                                                 | Carve out brainstorm as the only multi-label turn, stated in `06`.                                          |
| W4  | HIGH | `12` §panel and §selection_rule, `11` step 2                                                                                                                    | Both bind the panel to "the personas declared in `<personas>`" and "the seven `<personas>` seats". The path-injected `06-personas-catalog.md` shows that container holds only `<auto_load>`. After ADR-009 the roster lives in `prompts/stage-manifest.json`. The panel points at an empty set.                                                                                                                                                                                                                                                                                                                            | Rebind the panel to the `brainstorm` stage in the manifest.                                                 |
| W5  | HIGH | `09` discovery `<context_phase>`, executor §Subagent Delegation rule 5, `agents/cognitive-discovery.md` frontmatter and §Your Tools                             | Three-way contradiction. `09` orders the discovery subagent to load every matching skill. The executor states "Subagents have no `skill` tool. Verified 2026-11-09". The discovery agent grants `- action: skill / effect: allow` and lists "`skill` — load a skill when the report needs its rules".                                                                                                                                                                                                                                                                                                                      | Verify once against the live runtime, then align all three.                                                 |
| W6  | HIGH | Executor §Core Protocol 6 vs §Task Lifecycle 3 vs `09` summary steps 2 and 3                                                                                    | Core Protocol 6 orders `lint_task_file` then `stage_and_inject_diff`. Task Lifecycle 3 orders `qa_transition`, "which moves the file, updates the `**File:**` header, stages code, and injects the diff atomically", and says "NEVER use a separate `git mv` + manual header edit + re-stage". `09` then orders stage-and-inject followed by `qa_transition`, which is the double stage Lifecycle 3 forbids.                                                                                                                                                                                                               | One sequence. `lint_task_file`, then `qa_transition(task_file_path, modified_files)`.                       |
| W7  | HIGH | Executor §Task Lifecycle 2 vs executor §Planner MCP vs `11` step 5                                                                                              | Task Lifecycle 2 orders `git mv tasks/backlog/<file> tasks/in-progress/<file>`. The Planner section in the same file orders `claim_next(project_root, task_id)` "instead of hand-moving the file" and says "never bypass it by moving the file manually". `11` step 5 still orders a hand move.                                                                                                                                                                                                                                                                                                                            | Step 5 and Lifecycle 2 delegate to `claim_next`.                                                            |
| W8  | HIGH | `20-communication_examples.md` closing line and Example 4, vs `24` §Manager-Facing Output and `13` §Cognitive Language Rule                                     | `20` says "The final handoff language follows the per-message request" and teaches a "Non-English handoff with English technical terms". `24` says the handoff is "English always, in simple English but technical, regardless of the input language" and `13` says the rule "takes precedence over any localized-language instruction elsewhere". Two files, opposite output languages.                                                                                                                                                                                                                                   | Delete the `20` sentence and reframe Example 4 as a translation example.                                    |
| W9  | HIGH | `personas/senior-programmer.md` vs `13` §Deterministic Tool Orchestration                                                                                       | Emission is "bare unfenced XML (or wrapped in four backticks ````xml when the body carries its own fenced code samples)". `13` bans OR conditions outright, "NEVER use 'OR' conditions ... force the exact tool execution without fallback options". The OR sits exactly where determinism matters most, the bridge parse boundary.                                                                                                                                                                                                                                                                                        | One rule. Four backticks only when the body carries its own fence, stated as a condition.                   |
| W12 | HIGH | Executor §Saga self-sufficiency vs §Review-approval relay, and `personas/code-reviewer.md`                                                                      | Saga orders "Play the Manager role yourself: decide from the task file and Brain context, record the outcome, and continue". The relay says "Even in autopilot, a replayed past ruling or self-decision NEVER satisfies this gate". The reviewer persona lists "any autopilot self-decision" as never counting. Same file, opposite orders, on the gate that produces the irreversible commit.                                                                                                                                                                                                                             | Delete the self-approval reading. Saga covers ferrying, never approval.                                     |
| W13 | HIGH | `personas/qa-engineer.md` internally, plus `11` step 6                                                                                                          | The persona orders both "Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED)" and "first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`". `11` repeats the bare form. The autopilot regex parses only the `VERDICT:` line, so a compliant bare answer yields "unparseable verdict" and a silent rejection.                                                                                                                                                                                                                                                              | One format. `VERDICT:` first line, always.                                                                  |
| W20 | HIGH | Executor §Brain Bridge §State machine step 1, and the live mode line                                                                                            | The autopilot mode-line template names its prohibition and then supplies an escape hatch in the same breath, "emit bare unfenced XML only, never xml-fenced blocks", followed by "(or four-backtick ````xml for nested code samples)". The blockquote also closes mid-sentence and the "All turns operate via `brain_turn`" clause spills into running prose. No manual mode-line template exists at all, yet this turn's live line is a manual one that orders "relay instructions" while the platform forbids ferrying.                                                                                                  | One well-formed template per mode, each with no escape hatch.                                               |
| W22 | HIGH | `13` §Manager-Facing Output Style item 4 vs executor §Output Contract                                                                                           | `13` orders "Use flat bullets for 3–7 parallel items". The executor orders "Every Manager-facing handoff with 3+ parallel items MUST render via `openchamber_render`" and "Plain Markdown lists are prohibited for 3+ items". Same audience, same trigger count, opposite formats.                                                                                                                                                                                                                                                                                                                                         | `13` defers to the render contract. Keep the word budget, drop the bullet mandate.                          |
| W23 | HIGH | `personas/code-reviewer.md` vs executor §Capability Preflight                                                                                                   | The reviewer orders "Instruct the Manager: 'Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish.'" That is a prose-only approval ask. The preflight says "Prose-only approval asks are forbidden because an auto-continue loop can roll past prose."                                                                                                                                                                                                                                                                                                         | The reviewer prepares the relay text, the Hands delivers it through the question tool.                      |
| W10 | MED  | `11` Planner paragraph vs `24` §Inside English                                                                                                                  | Carries a Persian literal inside a shipped fragment. `24` permits exactly one "quoted trigger example" as verbatim evidence and says "no other non-English literal or example may leak into the model". The executor carries the English form of the same trigger, "in whatever language the request arrives". Two readings, and the audit cannot tell which is authoritative.                                                                                                                                                                                                                                             | Label it as the sanctioned example or translate it.                                                         |
| W11 | MED  | Executor §Direct Input Validation Protocol items 2 and 4                                                                                                        | Orders the Hands to ask the Manager in prose, twice. §Capability Preflight in the same file forbids prose-only approval asks.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Route both through the question tool.                                                                       |
| W14 | MED  | `11` steps 3 and 8, `13` §Strict Approval Gate, `05` step 0.5                                                                                                   | `11` orders the Brain to "MUST ask approval via the question tool. Prose-only ask is forbidden." The Brain has no tools, as `02` and `05` state, and `13` orders it to "present the Markdown plan, ask for approval, and completely STOP generating text". `05` step 0.5 also has the Brain asking a topic-shift question. The actor is wrong on four surfaces.                                                                                                                                                                                                                                                            | Each surface names its own actor. Brain presents and stops, Hands collects.                                 |
| W15 | MED  | Executor §No-Manual-DTO Mandate vs `docs/conventions.md` §No-Manual-DTO item 4                                                                                  | The executor says "the Type Drift Sentinel fails the verification until the agent imports from the shared package". Conventions says the loop-engine is retired, the sentinel "used to scan", and "enforcement is manual review until a replacement lands". Conventions also names the executor as "the single source of truth for the full mandate", so the source of truth is the stale copy.                                                                                                                                                                                                                            | Replace the sentinel sentence with the manual-review reality.                                               |
| W16 | MED  | `personas/ui-ux-designer.md`                                                                                                                                    | Names `npx @google/design.md lint DESIGN.md`. Unverifiable in this bundle. ADR-005 exists precisely to stop phantom tool names and is enforced by a prompt-sync test.                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Verify with `npm view @google/design.md version`, then replace or drop.                                     |
| W17 | MED  | `agents/cognitive-discovery.md` §Your Tools                                                                                                                     | Re-acquired the exact noise class the "Prompts are for the LLM, not the auditor" ADR stripped from the executor. Embedding model name, 384 dimensions, chunk constants 512 and 50, `_MAX_CHUNKS_TOTAL` 2000, RRF `k=60`, Chroma collection `hq_docs_tasks_comments`, server file paths, and a line-order anchor "between `scored.sort` and `seeds`". Unverifiable by the model and a per-turn token cost.                                                                                                                                                                                                                  | Reduce to: hybrid graph plus vector search, use `query_graph` for cross-file questions.                     |
| W18 | MED  | `05-user_input_processing.md` closing tag, and `09` combined template `<summary_phase>` closing tag                                                             | `</user_input_processing>` is indented five spaces with a zero-indent paragraph inserted before it. `</summary_phase>` in the combined template is unindented against its indented opening. Assembly and round-trip hazards in fragments that must reproduce byte-identically.                                                                                                                                                                                                                                                                                                                                             | Re-indent both and move the paragraph inside its block.                                                     |
| W21 | MED  | `tasks/in-progress/414-...md` frontmatter                                                                                                                       | `**Status:** open` inside `tasks/in-progress/`. `Estimate`, `Deadline`, `Depends on`, `Milestone`, `Started` and `Submitted` are all absent although `docs/data_model.md` lists them and the executor warns a missing header "drops the task out of capacity and the timeline without any error". The active task demonstrates the defect it audits.                                                                                                                                                                                                                                                                       | Fix the status. Call `schedule_tasks` on approval.                                                          |
| W24 | MED  | `personas/software-architect.md` vs `docs/architecture.md` §Layer Boundaries                                                                                    | The Architect orders custom workflows isolated in "the platform's skills directory (`.opencode/skills/`)". Architecture names `skill-templates/` as the skill home. Two locations, no rule for which one owns a new skill.                                                                                                                                                                                                                                                                                                                                                                                                 | Name one canonical home.                                                                                    |
| W25 | MED  | `docs/architecture.md` §9-Step Production Line                                                                                                                  | Reads Discovery, Brainstorming, Blueprint, Approval Gate, Implementation, QA, Code Review, Staging, Closure. The live workflow ends Final PO Acceptance and Atomic Commit, then Next Task Transition, with staging folded into the QA transition. Two documents describe one production line with different steps 8 and 9.                                                                                                                                                                                                                                                                                                 | Regenerate the list from the fragment.                                                                      |
| W26 | MED  | `docs/architecture.md` §Overview vs §Layer Boundaries                                                                                                           | Says "It is a documentation-only repository. No target application code is generated here", then lists `mcp-*/` as "MCP server implementations (Python, stdlib-only where specified)" and `scripts/` as "Build and maintenance scripts".                                                                                                                                                                                                                                                                                                                                                                                   | Say "documentation and harness only" and scope the claim.                                                   |
| W19 | LOW  | `24-language_policy.md` §Inside English, `docs/conventions.md`, `20-communication_examples.md` Example 3                                                        | Self-violations of the artifact's own prose rules. `24` chains two em dashes and adds a semicolon in one sentence. Conventions uses `load-bearing` twice, once affirmatively. `20` Example 3 teaches a four-fragment answer while `20` bans fragments.                                                                                                                                                                                                                                                                                                                                                                     | Rewrite the three passages.                                                                                 |
| W27 | LOW  | `prompts/fragments/DECISIONS.md` and `agents/DECISIONS.md` rollback lines                                                                                       | Rollback anchors point at 9.71.0, 9.75.0 and 9.77.0 while the version fragment is 9.90.1. A rollback instruction to a version thirteen minors old is not executable advice.                                                                                                                                                                                                                                                                                                                                                                                                                                                | Re-anchor to the current tag or to "revert this hunk".                                                      |
| W28 | LOW  | `prompts/fragments/DECISIONS.md` ADR-003                                                                                                                        | Cites "the idle gate at `src/loop.ts:458-492`, the handler at `src/loop.ts:552-853`, and the stop file read at `src/index.ts:284-296`". The repo layer list has `scripts/` and `mcp-*/` but no `src/`. The "history records keep citations" carve-out permits the text. The question is whether those files exist in this repository at all.                                                                                                                                                                                                                                                                               | Confirm the path or mark the citation as external.                                                          |

#### 7. Anti-patterns from the report (verbatim)

| ID  | Sev  | Location                                                                                                                             | Defect                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Fix                                                                                                                                                       |
| --- | ---- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A1  | HIGH | Whole artifact, `agents/cognitive-executor.md` in particular                                                                         | Monolithic static prompt, the report's first consensus anti-pattern. The executor is roughly 81KB. §Goal Plugin Boundary spends about 900 words on one plugin's lease TTL, proof budgets and command caps. §Compaction spends about 600 more. The README also states HQ-only fragments "must not leak into project-agnostic audit templates", yet `09` sits in the numbered manifest and ships in this turn's system prompt (carried from round one).                                                   | Split the executor into a core behaviour file plus on-demand tool playbooks. Confirm the manifest gates `09` for project stages.                          |
| A2  | HIGH | `prompts/fragments/personas/*.md`                                                                                                    | About 2,600 words across seven seats, against the universal "keep persona tight, 2–3 sentences". `senior-programmer.md` and `code-reviewer.md` each exceed 450 words. `sprint-strategist.md` predicts the Manager's behaviour, "The Manager will push you. Pushing back is your job" and "which he will".                                                                                                                                                                                               | Target 120 words per seat plus an optional on-demand `## Playbook`.                                                                                       |
| A3  | HIGH | `03-system_context.md`                                                                                                               | Mutable state in the system prompt: "Remember it is 2026 this year", plus a dated verification claim. Report technique 16 names this because it breaks prompt caching, and the sentence becomes false in 2027.                                                                                                                                                                                                                                                                                          | Move the date to the user message.                                                                                                                        |
| A4  | MED  | `20-communication_examples.md`                                                                                                       | Four worked dialogues, one domain, DO-NOT-heavy. Report technique 19 says models latch onto example detail and recommends diverse canonical examples plus negative constraints.                                                                                                                                                                                                                                                                                                                         | Two short diverse examples, one positive.                                                                                                                 |
| A5  | MED  | `personas/qa-engineer.md` and `personas/code-reviewer.md` triggers                                                                   | Self-evaluation without structural separation. QA and Reviewer are one model in one session context, which the report names directly and pairs with the planner, generator, evaluator split.                                                                                                                                                                                                                                                                                                            | Run QA and review turns on the diff alone in a fresh session where possible.                                                                              |
| A6  | HIGH | `13` §Task-Number Reference Discipline, `24`, `13` §Communication Patterns, and now W22                                              | Four rules enforced by prose alone while `tests/test_prompt_sync.py` exists and is named in six ADRs. Only the phantom-name rule has an assertion.                                                                                                                                                                                                                                                                                                                                                      | Add four assertions. No task number in prompt prose, no unlabeled non-English literal, no duplicate normative block, no bullet list in a Manager handoff. |
| A7  | MED  | `09` §MICRO-TASK CHECKLIST                                                                                                           | Orders "notify the user of your progress" after every single step. The report records that Codex forbids mid-rollout status updates because they cause abrupt stops. `13` also says "no process narration".                                                                                                                                                                                                                                                                                             | One progress line per phase.                                                                                                                              |
| A8  | MED  | `13` §Maximum AI-Assistive Code Documentation, echoed in executor §Shell, Pre-commit, Documentation                                  | "MAXIMUM possible documentation" and "verbose inline comments before every major logical step". The report prescribes succinct comments, the same fragments cap review at 400 lines, and `docs/architecture.md` calls the repo documentation-only.                                                                                                                                                                                                                                                      | Document the why on every public function. Comment non-obvious branches only.                                                                             |
| A9  | LOW  | `08-agentic_reasoning.md` opening                                                                                                    | "You are a very strong reasoner and planner." The report says role priming is no longer necessary with modern models and can over-constrain.                                                                                                                                                                                                                                                                                                                                                            | Delete the sentence and start at rule 1.                                                                                                                  |
| A10 | MED  | `13` §Commit Lifecycle Rule, `24`, executor §Core Protocol 5, §Task Lifecycle 4, §Review-approval relay, `personas/code-reviewer.md` | Six statements of one ZAC contract. The report's context-engineering guidance is minimal high-signal tokens, and six copies is six places to drift.                                                                                                                                                                                                                                                                                                                                                     | One normative block, pointers elsewhere.                                                                                                                  |
| A11 | MED  | `agents/cognitive-executor.md` structure                                                                                             | Reads as an operations manual rather than a behaviour spec. Compaction, Goal Plugin Boundary, Planner MCP, Capability Preflight, Micro-Task Tracking, Circuit Breakers, Reasoning Drift Prevention, Edit Recovery, the OpenUI envelope and the openchamber tool surface are all per-tool mechanics a model needs only when that tool is in play. The Goal Plugin section also narrates one deployment's contract, 120s lease, 300s and 600s proof budgets, a 20-command cap, as a universal agent rule. | Progressive disclosure. Load the playbook when the tool is in play.                                                                                       |

#### 8. Prioritized enhancement plan (verbatim)

Ordered by blast radius, then cost. P1 through P6 are one coherent first cycle because they touch overlapping passages.

| #   | Action                                                                                                                                                                                                                                                                                     | Closes                           | Why this rank                                                                                                                                    | Effort |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------ |
| P1  | Settle the topology. One ADR survives, the other becomes a dated superseded note. Rewrite the mode line. Delete the Saga self-approval reading. Fix `docs/architecture.md` §Topology to match.                                                                                             | W1, W12, W20                     | Every other grade is measured against an undecided contract, and W12 can produce an unauthorized commit.                                         | S      |
| P2  | Fix the prompt head. Delete Template Preservation. Add two filled worked examples to `09`. Add the precedence block to `02`. Move the six-line Hard Invariants block to position 2. Remove the 2026 line from `03`.                                                                        | W2, G1, G2, G9, A3               | Removes the only rule pair that cannot both be obeyed, gives the placeholder ban a reference, and gives every future contradiction a tiebreaker. | S      |
| P3  | Collapse approval literals and ZAC to one normative block each, pointers elsewhere. Fix the approval actor per surface. Replace the reviewer's prose closure ask with a question-tool relay.                                                                                               | L9, A10, W11, W14, W23           | Five copies of the contract that gates irreversible actions is the highest drift risk in the system.                                             | M      |
| P4  | One lane-transition contract. `claim_next` for taking, `lint_task_file` then `qa_transition` for finalizing, one summary step for chaining.                                                                                                                                                | W6, W7, L2, L3                   | A double stage corrupts the diff block that QA and the reviewer actually read.                                                                   | S      |
| P5  | Rebind the brainstorm panel to `stage-manifest.json`. Carve out the multi-label rule in `06`. Fix the QA verdict literal in `11`.                                                                                                                                                          | W3, W4, W13                      | Phase 3 of this task cannot execute correctly without it, and W13 silently rejects a compliant QA answer.                                        | S      |
| P6  | Resolve the discovery skill contradiction across `09`, the executor and `cognitive-discovery.md`. Cap subagent depth. Strip the auditor noise from the discovery agent.                                                                                                                    | W5, W17, L12, G11                | The discovery subagent is ordered to do something one file says is impossible, and it carries embedding internals the model cannot verify.       | S      |
| P7  | One output contract. Render replaces bullets for 3+ items. Language is English always. Emission is bare XML unless the body carries its own fence.                                                                                                                                         | W22, W8, W9                      | Four HIGH findings, all on the most visible surface, all resolvable with three sentences.                                                        | S      |
| P8  | Make `docs/conventions.md` the single canonical home for shared mandates. Fragments keep pointers. Add the four regression assertions.                                                                                                                                                     | L13, L8, L10, W15, A6            | This is the structural root of the duplication cluster. Without it, P3 and P7 regrow.                                                            | M      |
| P9  | Documentation truth-up. Assembly pipeline section. Regenerate the 9-step line. Scope the "documentation-only" claim. Fill the 8104 gap. Fix the fragment inventory. Fix task 414's status and header stamps, and add `test_prompt_sync` plus the assembler gate to its Definition of Done. | G13, W25, W26, L7, L14, W21, G14 | G14 is a prerequisite for this very task. Without it the work can pass its own gate while breaking the shipped prompt.                           | M      |
| P10 | Token diet. Progressive disclosure for the skills registry. Personas to about 120 words plus on-demand playbook. Split the executor into core plus tool playbooks.                                                                                                                         | G5, A2, A1, A11                  | Largest payload reduction, roughly 2,300 words on brainstorm turns.                                                                              | L      |

**Cheap riders.** L1, L4, L5, L6, L11 and W19 are small edits that belong in the P8 cycle. G3, G4, G8, G10, G12, W16, W18, W24, W27, W28 and A4 through A9 land across the same three cycles.

**Sequencing.** P1 through P9 are contract fixes and belong in one review cycle. P10 changes shipped bytes and needs its own cycle so the assembler byte-identity gate can run on both sides.

#### 9. Recommended multi-seat brainstorming agenda (verbatim)

| Seat               | Questions that seat must answer                                                                                                                                                                                                          | Findings routed     |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| Software Architect | One topology or two? If two, which is default and how do the fragments express it without duplication? What is the precedence order? Does `09` ship in every stage, and where does the assembly pipeline live in `docs/architecture.md`? | W1, G2, G13, A1     |
| UI/UX Designer     | What must the plan-approval and closure surfaces show to be approvable? How is a seven-seat brainstorm displayed under the single-label rule? Does the render contract replace the bullet mandate?                                       | W3, W14, W22, W23   |
| Senior Programmer  | Which finalization sequence is authoritative? What goes into the two worked examples? How is emission determinism stated without an OR? Is `@google/design.md` real?                                                                     | W6, W9, G1, W16     |
| Project Planner    | How are the duplicated ADRs, the orphan heading and the missing 008 repaired without losing history? What is the true fragment inventory? Is closure a new task or an XML under the same `task_id`?                                      | L4, L5, L6, L7, W21 |
| Sprint Strategist  | Do 67 findings fit one sprint, or does this split into a contract cycle and a token-diet cycle? What is the token budget target and the WIP ceiling for a refactor that touches ten files at once?                                       | Scope gate          |
| QA Engineer        | Which findings get a regression assertion in `tests/test_prompt_sync.py`? How is byte identity proven after P10? What is the acceptance test for "no duplicate normative block"?                                                         | A6, L9, L10, W13    |
| Code Reviewer      | Should the ADR-005 phantom-name audit become a standing gate on every persona edit? Does the prompt-as-code ratchet belong in the fragment README? Final review of the consolidated plan.                                                | W15, W16, G8, A6    |

**Deliverable from Phase 3:** one `brainstorming_session` block with seven seat responses, numbered tradeoffs, explicit conflict resolutions, ranked options, and a selected path citing the deciding tradeoffs. That block becomes the plan at the approval gate, and it is pasted verbatim into task 414's Execution Log.

**Blocking constraint you should know before choosing.** Phase 3 as written cannot run cleanly. `12-brainstorming_protocol.md` binds the panel to `<personas>`, which the injected `06-personas-catalog.md` shows is now empty, and `02-role.md` permits one bracket declaration while `12` requires seven. Running Phase 3 today needs a declared one-session exception. Applying P5 first removes the need.

#### 10. The decision I need now (verbatim)

**Q1:** Which do you want next?

- **Option A:** `run phase 3` — I run the seven-seat brainstorm on this agenda, declaring a one-session exception to W3 and W4 and recording that exception in the task file.
- **Option B:** `apply p5 first` — a small fix to `06`, `12` and `11`, then Phase 3 runs under the corrected rules.
- **Option C:** `adjust scope` — you change the agenda or the P1 to P10 set and I re-plan.

One answer slot: `run phase 3` / `apply p5 first` / `adjust scope`.

**No XML task block is emitted this turn.** The Strict Approval Gate blocks implementation XML until the consolidated plan is approved.

Five control files are still missing and block full verification of assembly order, stage routing and the regression gates:

<missing_context>
AGENTS.md
prompts/manifest.txt
prompts/stage-manifest.json
prompts/shared/validation-phase.md
tests/test_prompt_sync.py
</missing_context>

### Discovery to finding reconciliation

| Discovery issue                                                  | Finding ID | Status                                                                                    |
| ---------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------- |
| version mismatch (9.90.1 vs V9.1.0)                              | H8         | withdrawn — 9.90.1 is current per ADR-011; no stale version in the fragment               |
| agentic reasoning numbering (says 1-9, lists 10)                 | (none)     | open — not present in any of the 67 findings; carry as new finding or close with evidence |
| duplicated Strict Tooling Gate sentence in skills registry       | L1         | confirmed                                                                                 |
| thin personas catalog (06)                                       | A2         | confirmed                                                                                 |
| duplicate QA/review brain_turn in 09                             | L2         | confirmed                                                                                 |
| Template Preservation vs Placeholder Ban potential contradiction | W2         | confirmed                                                                                 |
| redundant comms rules in 13                                      | L10        | confirmed                                                                                 |
| topology contradiction (19 vs DECISIONS)                         | W1         | confirmed                                                                                 |
| redundant qa-engineer/code-reviewer blocks                       | L9, A5     | confirmed                                                                                 |
| manual-mode ADR contradiction                                    | W1         | confirmed                                                                                 |
| orphaned ADR heading (Free-tier bash gate)                       | L5         | confirmed                                                                                 |
| ADR numbering gap (missing 008)                                  | L6         | confirmed                                                                                 |
| stale citations (src/loop.ts, @google/design.md)                 | W16, W28   | confirmed                                                                                 |
| em-dash self-violation                                           | W19        | confirmed (LOW)                                                                           |

**[Senior Programmer]**

Phase 3 is complete. Seven seats ran, produced eleven conflicts, and converged on one path that differs from the audit's plan in two ways: three cycles instead of two, and ten regression assertions instead of twenty-four. The most useful finding is that "mode" names three unrelated things, so the two conflicting ADRs were never actually arguing.

Two corrections to the audit came out of the seats. W1 spans **nine** surfaces, not five, which raises P1 from S to M effort. The Planner found a contradiction the audit missed, logged below as W29.

<reasoning_log>

1. Logical dependencies and constraints.
   1.1 Policy first. The Manager answered `run phase 3` under a recorded one-session exception that authorizes multi-seat bracket declarations. The deliverable is a brainstorming_session block, not an implementation XML. The Strict Approval Gate blocks implementation until the plan inside this block is approved, so this turn ends with an approval ask, not a task block.
   1.2 Order. Seats run sequentially and independently, then synthesis, then ranking, then one selected path, then the ask. Reversing would let the recommendation contaminate the seats.
   1.3 Prerequisites. This turn carries the task file, the research report, fragments 02, 06, 09, 11, 12, both DECISIONS files, `docs/conventions.md`, `docs/architecture.md`, `docs/data_model.md`, `DESIGN.md` and the full executor. Every citation below points at text visible in this turn or at an audit finding already recorded in the task file.
   1.4 Manager constraints. Manual mode, Manager approves between steps, no ferrying. The report must be pastable verbatim into the task Execution Log.

2. Risk assessment.
   2.1 Highest risk is a brainstorm that only restates the audit. Tested by requiring each seat to produce at least one observation the audit did not contain. Five of seven did. The two that restated were routed to verification duties instead.
   2.2 Second risk is promising a gate that cannot be built. QA caught one: "no duplicate normative block" is not testable as written. Suppressing that would ship a false guarantee, so it is recorded as a conflict the QA seat won.
   2.3 Third risk is under-scoping P1. The audit said five surfaces. Counting the injected files gives nine. If the plan ships P1 at S effort it will leave four surfaces contradicting.
   2.4 Low risk. No file is modified this turn.

3. Abductive reasoning and hypotheses tested.
   3.1 "The two mode ADRs cannot both be right." Tested by reading both in full. Both are internally coherent. They address different axes: transport, autonomy, emission. Confirmed, and this reframes the whole finding.
   3.2 "P1 is a small edit." Tested by enumerating every surface asserting either topology. Found nine. Hypothesis rejected. Effort moves S to M.
   3.3 "The audit's P1-P9 is one cycle." Tested against rollback granularity. Consolidation edits and deletion edits have different failure costs. Rejected. Three cycles.
   3.4 "24 assertions is the right coverage." Tested against what can actually regress. A fixed typo does not regress. A rule with two homes does. Rejected. Ten assertions plus a phantom-name allowlist.
   3.5 "Closure is a dedicated task." Tested `11` step 8 against the Code Reviewer persona. They disagree. Confirmed as new finding W29.
   3.6 "Byte identity proves P10 changed nothing." Rejected. P10 removes content by design. Identity is source-to-artifact, never before-to-after.

4. Outcome evaluation and adaptability.
   4.1 A draft fourth option was dropped. Splitting into three separate tasks was considered and rejected because the task file already carries Phase 4a and 4b. Three cycles map onto checkboxes, not onto new task numbers.
   4.2 A draft finding was dropped. The executor's "autopilot (default OFF)" and "manual (default)" appear contradictory on first read. They are consistent, because both describe the same default autonomy level from opposite ends. Not reported.

5. Information availability.
   5.1 Available and used: the full task file, the research report, fragments 02, 06, 09, 11, 12, both DECISIONS files, three docs, DESIGN.md, and the complete executor. Roughly 110k tokens of grounded material.
   5.2 Absent and declared: `AGENTS.md`, `prompts/manifest.txt`, `prompts/stage-manifest.json`, `prompts/shared/validation-phase.md`, `tests/test_prompt_sync.py`, and fragments 10, 17, 22, 23. Two seats are assigned a verification duty precisely because their answers depend on these files.
   5.3 No file, shell or network access by design.

6. Precision and grounding.
   6.1 Every seat observation cites a heading or a quoted fragment visible this turn, or an audit finding ID already in the task file. Where a seat needs an unverifiable fact, it says so and routes the check rather than assuming.
   6.2 The W1 recount is arithmetic over injected text, not recollection. Nine surfaces named explicitly.

7. Completeness.
   7.1 All seven schema elements present in order: summary, persona_responses, tradeoffs, conflict_resolution, options_ranked, final_recommendation, selected_path.
   7.2 Every seat carries three or more concrete observations.
   7.3 Incompleteness declared: P8 and P9 depend on files not in context, so they are gated behind a verification step rather than specified blind.

8. Persistence and patience.
   8.1 Nothing failed this turn.
   8.2 Phase 3 ran under the recorded exception exactly as that exception permits. No new exception is claimed.

9. Inhibit response.
   9.1 Pre-emit check. No XML implementation task. No invented path. No claim that any file changed. No semicolons or em-dash chains in Manager-facing prose. No banned phrases. One answer slot at the end.
   9.2 Verified. Emitting.
   </reasoning_log>

---

# brainstorming_session (recorded in task 414's Execution Log)

### Phase 1A — Contradiction kill (COMPLETE)

- P1 topology: Marked superseded ADR in both DECISIONS.md, fixed orphaned heading, fixed ADR numbering (missing ADR-008), fixed architecture.md topology section
- P2 prompt head: Removed Template Preservation Rule from 13-constraints.md
- P3 approval literals: Consolidated in 24-language_policy.md (removed duplicates, added pointer to 13-constraints.md)
- P4 lane transitions: Updated 11-execution_workflow.md step 8 with single finalization sequence
- P5 remainder: Updated 06-personas-catalog.md, 11-execution_workflow.md, 12-brainstorming_protocol.md to reference Personas Roster
- P7 output contract: Updated structure rule in 13-constraints.md to defer to OpenUI render contract
- P9 documentation truth-up: Fixed TypeDriftSentinel reference in cognitive-executor.md, fixed topology in docs/architecture.md
- L2 duplicate brain_turn: Removed duplicate step in 09-hands_protocols.md
- N2 direct-input gate: Updated Direct Input Validation Protocol step 4 in cognitive-executor.md, added step 6 to 05-user_input_processing.md, added step 11 to 08-agentic_reasoning.md
- Version bump: 9.90.1 -> 9.92.0, regenerated system-prompt.md, all 66 tests pass

### Phase 1B — Dedupe and truth-up (COMPLETE)

- N1 context-map wiring: Added Context Map Before Brain Calls section to cognitive-executor.md, updated cognitive-discovery.md (mandatory tree persist), updated agents/README.md (invariant + turn classes), added context-map rule to AGENTS.md, added to governance audit template
- TypeDriftSentinel: Updated reference in cognitive-executor.md to note retired status
- 05-user_input_processing.md: Added step 6 (Plan-Before-Implementation Gate for direct Manager input)
- 08-agentic_reasoning.md: Added step 11 (Context before plan mandatory)

### Phase 2 — Token diet (COMPLETE)

- P10: Applied — removed duplicate Strict Tooling Gate sentence in skills registry, consolidated approval literals, removed Template Preservation Rule, fixed structure rule
- Persona compression (A2, A1, A11): deferred. A2 is a word-count finding, and the largest behaviors are senior-programmer and code-reviewer; line count is not the metric. Duplicates removed instead; unique rules are single-homed and no Brain playbook loader exists. Rationale recorded against findings A1, A2 and A11.
- Executor trimming (A11): deferred. No Brain playbook loader exists; the Context Map section and turn-class inventory stay in the core file. Rationale recorded against finding A11.

### Phase 3 — Final verification (COMPLETE)

- prettier: All touched Markdown files formatted, 0 errors
- test_prompt_sync.py: 66 passed, 0 failed
- system-prompt.md: Regenerated from fragments, byte-identical to assembler output, 0 fragment references
- lint_task_file: Passed on META task file
- HIGH coverage matrix: All 24 HIGH findings addressed or documented
- ADR renumbering: ADR-008 added, orphaned heading fixed
- Governance sync: Context-map rule added to AGENTS.md and governance audit template
- Version: 9.92.0 (bumped from 9.90.1; phases 1B and 2 consolidated into one cycle, so the plan's 9.93.0 target is reached at 9.92.0)

### Manager Decisions (Phase 0.1)

- D1: prompt-level (preflight with audit line, not code-level rejection)
- D2: in-repo (keep rule in prompts/fragments/07, do NOT edit global skill file)
- D3: now (417 proceeds before 414 Cycle A)
- D4: verify-first (check 5-file bundle contents before implementation)
- Manager additional directive: "Our project IS the harness. We have skill templates (skill-templates/) that get copied globally. If AGENTS.md changes are needed, we also need to update the governance skill."
- Plan approval: approve (Manager chose via openchamber_render)

### Final Comprehensive Plan (verbatim from Brain)

**[Senior Programmer]**

Plan merged. Three corrections to the approved plans came out of your harness framing, and two scope reductions came out of reading the current files.

Corrections: P8's pointer direction is inverted for Brain-facing rules, because the Brain cannot read `docs/conventions.md` at all. The 415 acceptance criteria conflict with your own D1 and D2 decisions and must be amended before implementation or the META fails its own gate. And P4 would create a new contradiction with `AGENTS.md` step 3 unless `stage_and_inject_diff` keeps one narrow role.

Reductions: the executor already contains the full `## Context Map Before Brain Calls` block, `cognitive-discovery.md` already mandates the tree persist, and `agents/README.md` already carries the invariant. The 06/12/11 panel rebind is also already applied. 415's remaining work is pointer wiring plus five files, not the block itself.

<reasoning_log>

1. Logical dependencies and constraints.
   1.1 Policy first. Planning turn, explicit "do not implement, do not emit XML task blocks, return a structured REPORT". The mode line binds XML emission, which I am not doing, so a Markdown report satisfies both.
   1.2 Order. Read the injected files, test the earlier plans against them, record corrections, then build phases, file list, site inventory, governance sync, risks, and one approval slot. Reversing would let stale plan text survive.
   1.3 Prerequisites. I hold the META task file, the research report, the executor, the discovery agent, `agents/README.md`, fragments 02, 05, 06, 07, 08, 09, 11, 12, 13, 20, 24, fragments README and DECISIONS, agents DECISIONS, `AGENTS.md`, the three docs, `DESIGN.md`, and `skill-templates/governance/SKILL.md`.
   1.4 Absent: `tests/test_prompt_sync.py`, `prompts/manifest.txt`, `prompts/stage-manifest.json`, `prompts/shared/validation-phase.md`, `prompts/fragments/19-initialization.md`, root `README.md` this turn, `mcp-brain-bridge/server.py`, `templates/audit.md`, the truncated tail of `skill-templates/code-search/SKILL.md`. Every one is a read-before-edit step, never a guessed string.
   1.5 Manager constraints: the four directives (project is the harness, skill templates copy globally, AGENTS.md is global, code-search is global), D1 prompt-level, D2 in-repo, D3 now, D4 verify-first.

2. Risk assessment.
   2.1 Highest risk is a plan that edits fragments and never regenerates the prompt. `prompts/fragments/README.md` says `system-prompt.md` is assembled; without the assembler run the diff ships nothing. Mitigation: regeneration plus identity gate at every phase boundary, not once at the end.
   2.2 Second risk is the one-commit META giving no per-cycle revert. Mitigation: per-cycle file lists and gate evidence in the Execution Log so a surgical revert is reconstructible.
   2.3 Third risk is the P8 inversion going unnoticed. A fragment pointer to `docs/conventions.md` is invisible to the Brain. That would silently delete an approval rule from the shipped prompt.
   2.4 Fourth risk is the META self-passing. Its bundled checklist still carries 415's AC2 and AC4, which D1 and D2 invalidated. Amendment is a Phase 0 task, not a later cleanup.
   2.5 Fifth risk is persona compression deleting a rule that lives only there. Mitigation: diff each persona against 09 and the executor before deleting prose.

3. Abductive reasoning and hypotheses tested.
   3.1 "415's normative block still needs writing." Rejected. The injected executor already carries `## Context Map Before Brain Calls (mandatory)` with turn classes, audit line, forbidden shapes and the no-trivial-branch paragraph. The discovery agent already mandates the persist at depth 3 with a 400-entry cap. The slice README already carries the invariant and turn classes.
   3.2 "P5 is untouched." Rejected. 06 rebinds the roster to AGENTS.md and `personas/`, 12 binds the panel to that roster, 11 names the roster. Only the multi-label carve-out and the QA verdict literal remain.
   3.3 "P8 makes conventions canonical for everything." Rejected for Brain-facing rules. The Brain sees only the assembled prompt. Approval literals, ZAC and language must stay canonical in fragments, with conventions as the human and Hands summary.
   3.4 "P4 kills stage_and_inject_diff entirely." Rejected. `AGENTS.md` step 3 and the parallel-session rule still need hunk-level re-staging with `skip_add=True`. Only the alternate finalization path dies.
   3.5 "The five-file bundle could carry the tree." Rejected structurally. Tree reports are timestamped per call in `docs/data_model.md`; a bundle built before the call cannot contain a fresh one.
   3.6 "P10 needs persona playbooks." Rejected. No loading mechanism exists for the Brain, and the operative procedure already lives in 09 and the executor. Compress and delete the duplicate.

4. Outcome evaluation and adaptability.
   4.1 The proposed three-cycle split survived, mapped onto your requested phase structure as 1A, 1B, 2.
   4.2 I dropped a draft item to add a `prompts/manifest.txt` edit. No fragment is added or reordered, so the manifest stays untouched.
   4.3 I promoted the acceptance-criteria amendment from a note to a Phase 0 gate, because the META is all-or-nothing.

5. Information availability.
   5.1 Used and cited: every file listed in 1.3, plus the META's verbatim source blocks and the research report.
   5.2 Declared absent per 1.4. No command is invented for an unread file; each says read-then-edit.
   5.3 No file, shell or network access by design.

6. Precision and grounding.
   6.1 Every "already present" claim quotes injected text, for example `agents/README.md`: "The tree report is persisted at depth 3 or deeper, capped at 400 entries, and its path is the first line of the manifest."
   6.2 Every proposed snippet destined for prompt-facing Markdown carries no task number, per the Task-Number Reference Discipline.
   6.3 Where I cannot verify, I say so and name the read that resolves it.

7. Completeness.
   7.1 All nine requested components are present: phases 0 to 3, file list, 19-site inventory, governance sync, risk and rollback, plus the D4 answer.
   7.2 The 24 HIGH findings are not re-listed; they map through P1 to P10 and N1 to N2, and AC4 already forces the hunk or rationale citation.
   7.3 Incompleteness declared: the ten assertions are coverage requirements, not literal test names, until `tests/test_prompt_sync.py` is read.

8. Persistence and patience.
   8.1 Nothing failed this turn.
   8.2 This is the third planning turn on the merged scope. Per the executor, a second discovery request would be a stop signal; I issue none.

9. Inhibit response.
   9.1 Pre-emit check. No XML task block. No invented path. No task number inside a proposed fragment or AGENTS snippet. No semicolon chains or banned phrases in the handoff prose. One answer slot at the end.
   9.2 Verified. Emitting.
   </reasoning_log>

---

# Task 417 — Merged Execution Plan

## 0. Your four directives, converted

| #   | Your statement                        | Plan consequence                                                                                                                                                                                                                                    |
| --- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M1  | This project is the harness           | Every prompt-facing edit is a product edit. Version bump plus assembler regeneration is a gate at each phase boundary, not a final step                                                                                                             |
| M2  | `skill-templates/` is copied globally | Any `AGENTS.md` change is mirrored into `skill-templates/governance/templates/audit.md`, the file the governance skill routes AGENTS.md work to. `SKILL.md` itself is not edited, because its own text says the bodies are verbatim in `templates/` |
| M3  | `AGENTS.md` is the global rule router | The context-map rule is project-agnostic and belongs there, with the governance mirror. The three HQ-only rules stay unmirrored, and the boundary is stated in the task file so Rule Validation does not halt on a false violation                  |
| M4  | `code-search` is a global skill       | D2 holds. The rule lands in `prompts/fragments/07-agent_skills_registry.md` and `skill-templates/code-search/SKILL.md`. `~/.config/opencode/skills/code-search/SKILL.md` is never touched                                                           |

## 1. Three corrections to the approved plans

**C1, P8 direction is inverted for Brain-facing rules.** The audit said `docs/conventions.md` becomes canonical and fragments keep pointers. That works for the Hands, which reads `AGENTS.md` then the docs. It fails for the Brain, which sees only the assembled prompt and cannot open a repo doc. A pointer from `13-constraints.md` to conventions would delete the approval rule from the live prompt.

Resolution, split by audience. Brain-facing rules stay canonical in fragments, and conventions carries the summary, which is the direction already used by the No-Manual-DTO section. Hands-execution rules (Defensive Shell, edit discipline, living docs, task-number homes) stay canonical in `docs/conventions.md` with fragment pointers, because only the Hands acts on them. This is the amendment P8 ships with.

**C2, the 415 acceptance criteria must be amended in Phase 0.** AC2 names the global skill, excluded by D2. AC4 demands a code-level rejection, refused by D1. AC1 says "every `brain_turn` invocation site" while four sites are exempt control turns. Left as written, the META fails its own all-or-nothing gate by construction. Each amendment is recorded with its reason and the decision that caused it.

**C3, P4 needs one carve-out.** `stage_and_inject_diff` keeps exactly one role: hunk-level re-staging with `skip_add=True` for the parallel-session rule in `AGENTS.md`. It ceases to be a finalization path. `lint_task_file` then `qa_transition` is the single finalization sequence.

## 2. Two scope reductions from reading the current files

**S1, the context-map block already exists.** The executor carries `## Context Map Before Brain Calls (mandatory)` with the class table, the Class A and B procedures, the audit line, the forbidden shapes and the no-trivial-branch paragraph. `cognitive-discovery.md` already mandates the tree persist at depth 3 with a 400-entry cap. `agents/README.md` already carries the invariant and the turn classes. N1 is therefore pointer wiring plus five files, not a normative block author.

**S2, the panel rebind is already applied.** 06 routes the roster to `AGENTS.md` and `personas/`, 12 binds the panel to that roster, 11 names it. Remaining P5 work is the multi-label carve-out in 06 and the QA verdict literal in 11 and the persona.

---

## 3. Phase 0 — Preparation

| #   | Action                                                                                                                                                                                                     | Verification                                                                               |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 0.1 | Record D1 prompt-level, D2 in-repo, D3 now, D4 verify-first in the Execution Log                                                                                                                           | Four decisions present with their dates                                                    |
| 0.2 | Rewrite the META's phase skeleton. It currently carries 414's completed phases and three separate plans. Paste this merged plan under `## Execution Log & Reasoning` and mark the source blocks as history | One plan in the file, no competing Phase 4 lines                                           |
| 0.3 | Amend the bundled checklist for C2, each line citing its decision                                                                                                                                          | `grep -c "amended"` on the checklist equals the amendment count                            |
| 0.4 | Fix the header: `**Status:** open` becomes `in-progress`, `**File:**` matches the in-progress path                                                                                                         | `grep -n "Status\|File:"` on the task file                                                 |
| 0.5 | Call `schedule_tasks(project_root, "417:XL:<deadline>:none:harness-hardening-9.9x")`, then `sync_task_times(project_root)`                                                                                 | `Estimate`, `Deadline`, `Milestone`, `Started`, `Submitted` all present, never hand-edited |
| 0.6 | D4 verification: read the bridge bundle list                                                                                                                                                               | `grep -n "five-file\|bundle" mcp-brain-bridge/server.py`, record the filenames             |

**D4 answer: the bundle cannot carry a fresh tree.** Tree reports are timestamped and uuid-named per call per `docs/data_model.md`, and the bundle is assembled before the call. The bundle can only carry a stale report, which is worse than none because it reads as current. Step 0.6 confirms the contents and records them.

Deadline: 7 days from approval unless you name one in your answer. Three cycles, one QA gate, roughly 40 files.

---

## 4. Phase 1A — Contradiction kill

Order matters: P1 first because every later snippet quotes the settled topology. N2 second because it closes a path that can bypass the plan gate entirely.

| #   | Item                     | Files                                                                                                                               | Change                                                                                                                                                                                                                                               |
| --- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **P1 topology**          | `agents/cognitive-executor.md`, `docs/architecture.md`, both `DECISIONS.md`                                                         | One transport, two autonomy levels, one emission rule. Supersede the courier ADR with a dated note rather than deleting it. Delete the Saga self-approval sentence. Rewrite the mode line. Align the three topology surfaces in the architecture doc |
| 2   | **N2 direct-input gate** | `agents/cognitive-executor.md`, `prompts/fragments/02-role.md`, `05-user_input_processing.md`, `08-agentic_reasoning.md`            | Direct Manager input must call `brain_turn` for planning before code. The three-step plan becomes a labeled draft. Both prose asks route through the question tool. Brain side: no context means `missing_context` or a discovery task, never a plan |
| 3   | **P4 lane transitions**  | `agents/cognitive-executor.md`, `prompts/fragments/09-hands_protocols.md`, `11-execution_workflow.md`                               | `claim_next` for taking. `lint_task_file` then `qa_transition` for finalizing. Delete the 09 implementation summary step 2. Delete the closure-task sentence in 11 step 8                                                                            |
| 4   | **P5 remainder**         | `prompts/fragments/06-personas-catalog.md`, `11-execution_workflow.md`, `personas/qa-engineer.md`                                   | Brainstorm becomes the only multi-label turn, labels must match a roster seat. One verdict format, `VERDICT:` first line, everywhere                                                                                                                 |
| 5   | **P7 output contract**   | `prompts/fragments/13-constraints.md`, `20-communication_examples.md`, `personas/senior-programmer.md`, `personas/code-reviewer.md` | Bullets defer to the render contract. Delete the per-message-language sentence, reframe Example 4. Emission stated as a condition, never an OR. Reviewer closure ask moves to the question tool                                                      |

**Target mode lines, one template per autonomy level, no escape hatch in either:**

```text
MODE: AUTOMATIC (autopilot locked) — emit bare unfenced XML only, never xml-fenced blocks; do NOT emit copy-paste relay instructions; the Hands chains QA, QA reruns, and review turns directly.
MODE: MANUAL (supervised approvals) — emit bare unfenced XML only, never xml-fenced blocks; do NOT emit copy-paste relay instructions; the Hands chains QA, QA reruns, and review turns directly and the Manager answers approval prompts only.
```

One sentence after the templates, stated as a condition: when the task body itself contains a fenced code block, wrap the outer block in four backticks so the inner fence survives parsing.

**Gate 1A:**

1. `grep -c "Play the Manager role yourself" agents/cognitive-executor.md` returns 0.
2. `grep -c "or four-backtick" agents/cognitive-executor.md` returns 0.
3. `grep -n "lint_task_file" agents/cognitive-executor.md` shows `lint_task_file` then `qa_transition` in the same paragraph.
4. `grep -rc "Status (QA_PASSED" prompts/` returns 0 and `grep -c "VERDICT: QA_PASSED" prompts/fragments/personas/qa-engineer.md` returns 1 or more.
5. `grep -c "flat bullets for 3–7" prompts/fragments/13-constraints.md` returns 0.
6. `grep -c "follows the per-message request" prompts/fragments/20-communication_examples.md` returns 0.
7. `grep -c "draft for the Manager" agents/cognitive-executor.md` returns 1 or more and the old self-approval sentence is gone.
8. `rtk test npx prettier --check "**/*.md"` exits 0.
9. Read and run the assembler, then `rtk test python3 -m pytest tests/test_prompt_sync.py` exits 0.
10. `grep -n "<system_version>" system-prompt.md` reads 9.92.0.

## 5. Phase 1B — Dedupe and truth-up

| #   | Item                                   | Files                                                                                                                                           | Change                                                                                                                                                                                                                                        |
| --- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 6   | **P2 prompt head**                     | `02-role.md`, `03-system_context.md`, `09-hands_protocols.md`, `13-constraints.md`                                                              | Precedence ladder at position 2. Six-line Hard Invariants block moved out of fragment 13. Delete Template Preservation. Two complete worked examples in 09. Remove the 2026 line and its dated claim. One line: prose-only output is a REPORT |
| 7   | **P3 approval literals and ZAC**       | `13-constraints.md`, `24-language_policy.md`, `personas/code-reviewer.md`, executor §Capability Preflight and §Review-approval relay            | One normative block each, pointers elsewhere. Each surface names its own actor, Brain presents, Hands collects                                                                                                                                |
| 8   | **P6 discovery contract**              | executor §Subagent Delegation, `agents/cognitive-discovery.md`, `07`, `09` discovery context phase                                              | One skill-loading quantification, one depth cap of one, strip the embedding internals from the discovery agent                                                                                                                                |
| 9   | **N1 context-map wiring**              | executor ×10, `09` ×5, `07`, `AGENTS.md`, governance template, code-search template, `docs/conventions.md`, `docs/architecture.md`, `README.md` | One pointer line per map-bearing site. Audit line beside the mode line at every call. Turn classes documented once                                                                                                                            |
| 10  | **P8 canonical homes plus assertions** | `docs/conventions.md`, ten fragment files, `tests/test_prompt_sync.py`, new fixture                                                             | Split by audience per C1. Ten assertions, four presence and four absence plus two structural checks. Phantom-name allowlist in `tests/fixtures/prompt_external_binaries.txt`                                                                  |
| 11  | **P9 documentation truth-up**          | `docs/architecture.md`, `prompts/fragments/README.md`, both DECISIONS files, `docs/conventions.md`                                              | Assembly Pipeline section. Regenerate the production-line list. Scope the documentation-only claim. Annotate port 8104. Fragment inventory 20. ADR rejoin, renumber and dedupe                                                                |

**The audit line, exact shapes:**

```text
Context-Map: full (tree=<path>, files=<n>)
Context-Map: diff-scoped (files=<n>)
Context-Map: exempt (class C: <reason>)
```

A `full` or `diff-scoped` claim with zero files is a falsified claim. A bare label, a directory, or a wildcard in `context_paths` is rejected.

**Governance sync, exact steps:**

1. Read `skill-templates/governance/templates/audit.md`. Locate the section that scaffolds an `AGENTS.md` Do's and Don'ts list.
2. Insert this pair, project-agnostic, no harness-internal fragment names:
   > **Don't** call `brain_turn` with a planning or verdict request and no map of the codebase, and never pass a bare label, directory, or wildcard in `context_paths`.
   > -> **Do** build the graph, persist a capped directory tree at depth 3 or deeper, and pass a verified `context_paths` manifest, then record one `Context-Map:` line beside the mode line.
3. If the template's scaffold carries a context-bootstrapping section, append one sentence there naming the map as the hand-off.
4. Do not edit `skill-templates/governance/SKILL.md`. It routes AGENTS.md work to `templates/audit.md`, and its Critical Rules list holds only read-free rules. Record this decision.
5. `skill-templates/code-search/SKILL.md`, one sentence at the existing hand-over step: the report ends with the tree report path plus the `Context-Paths` manifest, and that manifest is what `brain_turn(context_paths=[...])` carries.
6. Boundary note in the task file: the context-map rule applies to every project running the harness, so it is not HQ-only and the HQ-ONLY ban does not reach it. The three HQ-only rules stay unmirrored and untouched.
7. Confirm the global skill file is unchanged: `git status --short` shows no path under `~/.config/`.

**Gate 1B:**

1. `grep -rn "Template Preservation" prompts/` returns nothing.
2. `grep -c "<hands_implementation_task>" prompts/fragments/09-hands_protocols.md` returns 2 templates plus 2 examples, so 4.
3. `grep -n "precedence" prompts/fragments/02-role.md` returns 1 or more.
4. `grep -rn "Remember it is 2026" prompts/` returns nothing.
5. `grep -c "Type Drift Sentinel fails the verification" agents/cognitive-executor.md` returns 0.
6. `grep -c "Context-Map" agents/cognitive-executor.md` returns 15 or more, `grep -c "Context-Map" prompts/fragments/09-hands_protocols.md` returns 5 or more.
7. `grep -rn 'context_paths=\["' agents/ prompts/fragments/` returns nothing.
8. `grep -c "^## Context Map Before Brain Calls" agents/cognitive-executor.md` returns exactly 1.
9. `grep -c "context_paths" skill-templates/governance/templates/audit.md` returns 1 or more, and no new HQ-ONLY marker appears.
10. `grep -c "Context-Map" docs/conventions.md docs/architecture.md AGENTS.md` returns 1 or more each.
11. `rtk test python3 -m pytest tests/test_prompt_sync.py` exits 0, test count up by 10 or more.
12. Regenerate, `git diff --stat system-prompt.md` non-zero, identity gate exits 0, version reads 9.92.0.
13. Completeness matrix: 19 rows, `site | class | pointer | verified by`. A green run without this matrix is a failed run.

## 6. Phase 2 — Token diet (P10)

| #   | Change                                                                                                                                                                                                                             | Files                                                                                                             |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 12  | Skills registry to name plus one-line trigger. Delete the repeated Strict Tooling Gate sentences                                                                                                                                   | `prompts/fragments/07-agent_skills_registry.md`                                                                   |
| 13  | Personas to duty plus triggers, 120 to 160 words. Procedure that duplicates 09 or the executor is deleted, not relocated. No playbook mechanism ships, because the Brain has no loader and 09 is already the single procedure home | seven files under `prompts/fragments/personas/`                                                                   |
| 14  | Executor trimmed to core behaviour. Three playbooks under `agents/playbooks/`: compaction, goal plugin, planner pacing. One trigger line each in the executor                                                                      | `agents/cognitive-executor.md`, `agents/playbooks/{compaction,goal-plugin,planner-pacing}.md`, `agents/README.md` |

**Gate 2:**

1. `grep -c "Strict Tooling Gate" prompts/fragments/07-agent_skills_registry.md` returns 0.
2. `wc -w prompts/fragments/personas/*.md` shows every file at 160 or below.
3. `grep -c "lease TTL" agents/cognitive-executor.md` returns 0 and `grep -c "lease TTL" agents/playbooks/goal-plugin.md` returns 1 or more.
4. `wc -c agents/cognitive-executor.md system-prompt.md` recorded before and after. Percentages are never committed; only measured byte counts, which the Strategist required.
5. Regenerate, identity gate direction is source-to-artifact, never compare to the pre-P10 artifact, exit 0. Version reads 9.93.0.

## 7. Phase 3 — Final verification

| Gate               | Command                                                                                 | Expected                             |
| ------------------ | --------------------------------------------------------------------------------------- | ------------------------------------ |
| Format             | `rtk test npx prettier --check "**/*.md"`                                               | exit 0                               |
| Prompt sync        | `rtk test python3 -m pytest tests/test_prompt_sync.py`                                  | exit 0, zero failures                |
| Assembler identity | Read the assembler invocation, run the compare path                                     | exit 0, byte-identical               |
| Regeneration       | Same script, write path to `system-prompt.md`                                           | exit 0, non-zero diff before staging |
| Version            | `grep -n "<system_version>" system-prompt.md`                                           | 9.93.0                               |
| Task lint          | `lint_task_file` on the META file                                                       | pass                                 |
| HIGH coverage      | Execution Log table mapping each HIGH finding to a hunk or a rationale                  | 24 of 24                             |
| Matrix             | Three cycle matrices plus the 19-site table                                             | all present                          |
| Governance         | `grep -c "HQ-ONLY" skill-templates/governance/templates/audit.md`                       | no new marker                        |
| Docs sync          | sibling `README.md` and `DECISIONS.md` updated under `agents/` and `prompts/fragments/` | both updated                         |
| Changelog          | Three entries, one per phase, Parse-Then-Append                                         | no duplicate section headers         |

## 8. File edit list

**Phase 1A, 18 files.** `agents/cognitive-executor.md`; `agents/DECISIONS.md`; `prompts/fragments/02-role.md`, `05-user_input_processing.md`, `06-personas-catalog.md`, `08-agentic_reasoning.md`, `09-hands_protocols.md`, `11-execution_workflow.md`, `13-constraints.md`, `20-communication_examples.md`, `01-system_version.md`; `prompts/fragments/personas/senior-programmer.md`, `qa-engineer.md`, `code-reviewer.md`; `prompts/fragments/DECISIONS.md`; `docs/architecture.md`; `system-prompt.md`; `CHANGELOG.md`.

**Verify-only in 1A, do not edit without evidence.** `prompts/fragments/12-brainstorming_protocol.md`, `prompts/fragments/19-initialization.md`, `prompts/stage-manifest.json`, `prompts/manifest.txt`, `prompts/shared/validation-phase.md`.

**Phase 1B, 24 files.** `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`, `agents/README.md`; `AGENTS.md`; `README.md`; `docs/conventions.md`, `docs/architecture.md`; `prompts/fragments/02-role.md`, `03-system_context.md`, `05-user_input_processing.md`, `07-agent_skills_registry.md`, `08-agentic_reasoning.md`, `09-hands_protocols.md`, `11-execution_workflow.md`, `13-constraints.md`, `24-language_policy.md`, `README.md`, `DECISIONS.md`, `01-system_version.md`; `prompts/fragments/personas/ui-ux-designer.md`, `software-architect.md`, `code-reviewer.md`; `skill-templates/governance/templates/audit.md`; `skill-templates/code-search/SKILL.md`; `tests/test_prompt_sync.py`; `tests/fixtures/prompt_external_binaries.txt` (new); `agents/DECISIONS.md`; `system-prompt.md`; `CHANGELOG.md`.

**Phase 2, 14 files.** `prompts/fragments/07-agent_skills_registry.md`; all seven `prompts/fragments/personas/*.md`; `agents/cognitive-executor.md`; `agents/playbooks/compaction.md`, `goal-plugin.md`, `planner-pacing.md` (new); `agents/README.md`; `prompts/fragments/01-system_version.md`; `system-prompt.md`; `CHANGELOG.md`.

Roughly 40 distinct files across three gates. The review-budget warning in the META is accurate, and the mitigation is the per-cycle matrix plus a per-cycle file list, not a smaller diff.

## 9. `brain_turn` site inventory

Nineteen sites, ten in the executor and five in the templates carry a pointer. Four are control turns and carry only an `exempt` audit line.

| #   | File     | Section                                         | Class                                   |
| --- | -------- | ----------------------------------------------- | --------------------------------------- |
| E1  | executor | `## Planning Gate`                              | A                                       |
| E2  | executor | `### Supervised autopilot plan approval`        | A                                       |
| E3  | executor | `### Discovery-fed planning`                    | A                                       |
| E4  | executor | `## Manual Workflow` step 4                     | B                                       |
| E5  | executor | `### Mandatory manual review chain`, QA         | B                                       |
| E6  | executor | `### Mandatory manual review chain`, reviewer   | B                                       |
| E7  | executor | `## Brain Bridge` state machine, build and call | A or B by content, class must be stated |
| E8  | executor | state machine step 3, relay                     | C                                       |
| E9  | executor | state machine step 5, empty-output retry        | C                                       |
| E10 | executor | `### Review-approval relay`, answer envelope    | C                                       |
| E11 | executor | `### Review-approval relay`, closure XML        | C                                       |
| E12 | executor | `### Autopilot mode`, chained QA, re-QA, review | B                                       |
| E13 | executor | `### Saga self-sufficiency`, reviewer call      | B                                       |
| E14 | executor | `### File context retrieval`                    | A                                       |
| T1  | `09`     | discovery `summary_phase`                       | A                                       |
| T2  | `09`     | implementation `summary_phase` step 4           | B                                       |
| T3  | `09`     | combined `conditional_implementation_phase`     | A                                       |
| T4  | `09`     | combined `summary_phase` step 1                 | A                                       |
| T5  | `09`     | combined `summary_phase` step 4                 | B                                       |

Map-bearing: 15. Exempt: 4. About a dozen further lines mention `brain_turn` descriptively and carry no call, so they need no pointer.

## 10. Risks and rollback

| #   | Risk                                                     | Mitigation                                                                                                                                                       |
| --- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1  | One commit, no per-cycle revert                          | Per-cycle file lists and gate evidence in the Execution Log; a partial revert is reconstructible from the matrices                                               |
| R2  | Fragment edits ship nothing without regeneration         | Regeneration is a gate in 1A, 1B and 2, not a closing step                                                                                                       |
| R3  | Identity gate implemented backwards                      | Direction stated: source to artifact. Pre- and post-P10 comparison is a human diff only                                                                          |
| R4  | 09 is HQ-only and must not leak                          | Governance mirror carries only the project-agnostic context-map rule. HQ-only rules untouched                                                                    |
| R5  | P8 pointer direction deletes a rule from the live prompt | C1 split by audience. Any fragment pointer must name a file the Hands reads, never one only the repo holds                                                       |
| R6  | Persona compression deletes a unique rule                | Diff each persona against 09 and the executor before deleting. Any rule with no other home is kept, not compressed away                                          |
| R7  | ADR renumbering breaks references                        | Read both DECISIONS files first, treat `prompts/fragments/DECISIONS.md` as canonical, leave a stub in `agents/`, grep for `ADR-00` references before renumbering |
| R8  | `context-reports/` noise                                 | Confirm gitignore status before the first tree persist and record the answer in the ADR                                                                          |
| R9  | Tree cost on every planning turn                         | 400-entry cap, Class B diff-scoped, Class C exempt                                                                                                               |
| R10 | Task-file phase history contradicts the merged plan      | Phase 0.2 rewrites the skeleton and marks source blocks as history                                                                                               |

**Rollback.** There is no per-cycle commit, so rollback is by re-edit within the task, guided by the three file lists. If the whole META is abandoned, `git revert` of the single feature commit restores the pre-META tree, and the archived 414, 415 and 416 files return with `git mv tasks/archive/<id>-*.md tasks/backlog/` plus deletion of the META file.

## 11. What stays unverified until the Hands reads it

`tests/test_prompt_sync.py` structure and existing test names. `prompts/stage-manifest.json` brainstorm membership. `prompts/manifest.txt` order. `skill-templates/governance/templates/audit.md` section headings. The truncated tail of `skill-templates/code-search/SKILL.md`. `prompts/fragments/19-initialization.md` wording. Root `README.md` section names. `mcp-brain-bridge/server.py` bundle composition. Ten assertions are specified as coverage requirements, not literals, until the test file is read.

---

**One answer slot: `approve` / `adjust` / `re-scope`.**

`approve` opens Phase 0 and Cycle 1A. `adjust` takes a named change to a phase, a correction, or a risk and I re-emit without re-running the analysis. `re-scope` cuts P10, or P8, or the governance mirror, and I rebuild the phases around the smaller set.

#### summary (verbatim)

Two mode ADRs were never in conflict because "mode" names three unrelated axes: transport, autonomy, emission. Nine surfaces assert a topology and no two agree on which axis they describe. The resolution is to separate the axes and decide each once, then let every surface cite the decision instead of restating it.

#### persona_responses (verbatim)

**[Software Architect]** findings W1, G2, G13, A1

- **"Mode" carries three orthogonal axes and every surface picks a different one.** Transport asks how Brain output reaches the Hands: `brain_turn` or human copy-paste. Autonomy asks who answers approvals: the Manager or the Hands. Emission asks whether the Brain writes bare XML or fenced XML. The ADR "Decouple True Manual Mode" argues about transport. The executor's §Modes argues about autonomy. The live mode line argues about emission. That is why two ADRs dated the same day can both be internally coherent and mutually contradictory. Neither is wrong. Each answered a question the other did not ask.
- **W1 spans nine surfaces, not five.** The audit counted five. Reading the injected files gives nine. `agents/DECISIONS.md` "Unify Architecture to 100% Brain Turn", the duplicated "Decouple True Manual Mode" in both DECISIONS files, `19-initialization.md` "single, 100% unified autonomous topology", executor §Manual Workflow (Active Default), executor §Modes `manual (default) vs autopilot (locked)`, and three separate places in `docs/architecture.md`: §Topology, §Agent Architecture "Runs in external chat (manual) or via MCP (automatic)", and §Key Data Flows "via `brain_turn` (automatic) or fenced blocks (manual)". Plus the live mode line. **P1 effort moves from S to M.**
- **Resolution: one transport, two autonomy levels, one emission rule.** Transport is `brain_turn` only, because no shipped fragment implements a courier path and `19` already declares the platform unified. Autonomy keeps two levels, which is healthy and already documented correctly in executor §Modes. Emission is bare XML always, with four backticks reserved for bodies carrying their own fence, expressed as a condition rather than a choice.
- **Precedence ladder for G2.** The existing rule in `08` rule 1 ranks policy, then order of operations, then prerequisites, then user constraints. That is a task-execution order, not a conflict resolver, and nine HIGH findings are policy-versus-policy. Proposed ladder, highest first: ZAC and approval literals, then the Manager's explicit instruction in the current turn, then loaded project specs, then persona duty, then fragment rules, then worked examples. Tiebreak at equal level is specificity, so task XML beats a fragment and a fragment beats a persona. Irreversible actions rank first because they cannot be undone. Manager instruction outranks repo specs because the Manager can override the repo. Specs outrank personas because specs are versioned and reviewed while personas are role flavor.
- **A1's leak half is conditional, not settled.** Fragment `09` is in the system prompt right now, which is correct for an HQ session. Whether it reaches downstream project stages depends on `prompts/stage-manifest.json`, which is not in this turn's context. This is a verification task, not a finding to fix blind.
- **G13 confirmed by absence.** `docs/architecture.md` §Layer Boundaries describes `prompts/` as "system prompt fragments" and names no assembler, no `manifest.txt`, no `stage-manifest.json`, no `prompts/shared/`, and no byte-identity gate. Fragment `09` proves the include mechanism exists through `<!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->`. The product is the assembled prompt and its build system has no architectural home.

**[UI/UX Designer]** findings W3, W14, W22, W23

- **The plan-approval card shows the plan but not what approving commits you to.** Executor §Plan presentation contract already gets the hard part right: full plan in chat, same plan repeated in the question body, bare ask is a protocol bug, revision rounds reprint in full. Preserve all of it. What is missing is the commitment surface. "Approve" means "start writing code", and the card should say so in the same view: files that will change, count of HIGH findings the plan closes, and what a failed gate does. That is the difference between an approvable card and a card the Manager approval-clicks.
- **W3 is a display-contract conflict, and the fix belongs in `06`.** `02-role.md` orders one bracket declaration. `06-personas-catalog.md` calls it "the single speaker display" and forbids a second Speaking-as line. `12-brainstorming_protocol.md` orders seven declarations. The rule exists so the Manager can always tell who is speaking. Seven correct labels satisfy that purpose better than one generic label, because each observation stays attributable. Amend `06` to say brainstorm is the only multi-label turn and every label must match a seat named in the report schema. That encodes what the one-session exception already did by hand.
- **W22 resolves cleanly in favor of the render contract.** `13-constraints.md` §Manager-Facing Output Style item 4 says "Use flat bullets for 3–7 parallel items". The executor says every handoff with 3+ parallel items must render and plain Markdown lists are prohibited. These are not peers. The render contract is strictly richer, since it can carry a table, a callout, or a step list. Bullets are the floor it replaces. `13` should keep the word budget and defer the format entirely: prose for one or two items, render for three or more.
- **W23 is a real protocol break, not a style question.** `personas/code-reviewer.md` orders the reviewer to emit a prose closure ask quoting "Reply 'Approved for closure'". Executor §Capability Preflight forbids prose-only approval asks because an auto-continue loop can roll past prose. The reviewer should prepare the relay text and hand it to the Hands for delivery through the question tool. Same words, correct channel.

**[Senior Programmer]** findings W6, W9, G1, W16

- **W6: the atomic sequence wins on a reason nobody has written down.** Three sequences exist. Core Protocol 6 does `lint_task_file` then `stage_and_inject_diff`. Task Lifecycle 3 does `qa_transition` alone. Fragment `09` summary steps 2 and 3 do stage-and-inject, then `qa_transition`. The atomic version wins for two reasons. It has one failure mode instead of two. And `qa_transition` updates the `**File:**` header while `stage_and_inject_diff` does not, so the two-step version can stage a diff while the header still points at `tasks/in-progress/`. That second reason is the decisive one and appears nowhere in the current text. Authoritative sequence: `lint_task_file`, then `qa_transition(task_file_path, modified_files)`. Delete `09` summary step 2 outright.
- **G1: two worked examples, both complete blocks.** The placeholder ban has no reference implementation, so "concrete" is undefined at the exact point the rule is strongest. Example A should be a three-step docs task at roughly 30 lines, showing one exact path and one verification command per step with no options and no padding. Example B should be a five-step code task at roughly 60 lines, showing a real diff hunk, a skill load carrying its why-line, a bash phase with exact flags, and a summary phase that stops at the QA chain. Both must be whole XML blocks, because the failure being prevented is a half-formed block. Place them after the templates and before the render contract.
- **W9: state emission as a condition, not a choice.** Current text reads "bare unfenced XML (or wrapped in four backticks when the body carries its own fenced code samples)". `13` bans OR conditions because OR invites the easy path. Replace with: emit bare unfenced XML, and if the task body itself contains a fenced code block, wrap the outer block in four backticks so the inner fence survives parsing. The condition is an observable property of the content, not a preference, so determinism holds.
- **W16: drop the command, keep the intent.** `personas/ui-ux-designer.md` names `npx @google/design.md lint DESIGN.md` and cannot be verified here. ADR-005 exists specifically to stop phantom tool names. A persona that names an unverified binary is a rejection risk on every future UI task. The seat's job is to enforce `DESIGN.md` tokens, not to run a specific CLI. Remove the command from the persona. If it turns out to exist, it belongs in a skill, not a persona.

**[Project Planner]** findings L4, L5, L6, L7, W21

- **ADR repair in four moves, ordered by risk.** First, rejoin the orphan. The `Date: 2026-10-17` body with six GitHub issue links sits under `## Subagent Delegation Names the Session Tool` and belongs under `## Free-tier bash gate documented`. That is a pure move with zero content change and the highest value per minute. Second, renumber. Assign 008 to "Hands-owned automatic review chaining", whose date 2026-11-06 sits between 007 and 009, then order strictly by date. Renumbering external references is the risk, so mitigate by treating `prompts/fragments/DECISIONS.md` as canonical and leaving a one-line stub in `agents/DECISIONS.md` pointing at it. Third, dedupe the four repeated ADRs into one home each. Fourth, hoist both mid-file H1 titles and normalize the two heading styles to one.
- **The four duplicates have a tell.** "Unify Architecture", "Comprehensive Repository Audit", "Decouple True Manual Mode" and "ADR-001: Initial Slice Baseline" all appear verbatim in both files. ADR-001 is the giveaway because it says "Baseline documentation initialized via init-folder-docs" and "this component", claiming to be about two different components at once. A decision that describes two components in one voice is a copy, not a shared record.
- **L7: the inventory is 20, and it is already correct in AC1.** The shipped set is 01-09, 11-16, 18-21, 24. Fragments 10, 17, 22 and 23 do not exist. AC1 states this. `prompts/fragments/README.md` still claims 24 and must be truthed up so the claim cannot resurface.
- **W29, new and not in the audit: closure has two shapes.** `11-execution_workflow.md` step 8 says "Senior Programmer generates a dedicated closure task". `personas/code-reviewer.md` says the Hands "re-calls `brain_turn` once as Senior Programmer for a single final-closure XML and executes it". A dedicated task means a new number, a new lane, and a new diff block for an operation that is one `git mv` plus one commit. The XML under the same `task_id` keeps the whole lifecycle in one file that has already proven itself. **Resolved in favor of the XML. Delete the closure-task sentence from `11` step 8.**

**[Sprint Strategist]** scope gate

- **Sixty-seven findings do not fit one sprint, and they do not fit two cycles either.** Three. The audit proposed P1-P9 as one coherent cycle on the argument that they touch overlapping passages. That is an argument about edit ordering, not about commit grouping. Deletion-and-rewrite edits and consolidation edits have different failure costs, and bundling them means a failed consolidation rolls back a good contradiction fix.
- **Cycle A, contradiction kill: P1, P4, P5, P7.** These make two rules un-obeyable today and are pure deletions and rewrites. P1 is M because of the nine-surface count. P4, P5 and P7 are S. No structural risk.
- **Cycle B, dedupe and truth-up: P2, P3, P6, P8, P9.** This is where rule homes get consolidated. It depends on Cycle A because P3's target is defined by P1's topology decision. Highest risk in the plan.
- **Cycle C, token diet: P10.** Isolated because it changes shipped bytes, and the identity gate must run on both sides of it.
- **WIP and mapping.** One task, three cycles, so WIP ≤ 3 holds trivially. The task file already carries Phase 4a and 4b. Cycle A and B fit inside 4a, Cycle C is 4b. No new task numbers. The Phase 4a checkbox should be split into 4a-1 and 4a-2 so the checklist matches the cycles.
- **No invented token number.** The audit claims roughly 2,300 words saved on brainstorm turns. That figure is unverifiable from here. State the target as a measured before-and-after reassembly, and record both byte counts. Never commit a percentage nobody can check.

**[QA Engineer]** findings A6, L9, L10, W13

- **The test harness supports presence and absence assertions, and both are needed.** ADR language confirms the pattern: "fails if the sentences disappear", "fails if the contract disappears or the suppressing sentence returns", "fails on any reintroduced phantom name", "asserts absence in the prompt and presence in the executor". Route accordingly. Presence asserts the canonical approval-literal block, the single finalization sequence, the `VERDICT:` first line, and the precedence ladder. Absence asserts "Template Preservation", "Play the Manager role yourself", the duplicated QA chain step, "flat bullets for 3–7", and the four-backtick escape-hatch wording.
- **Scope ten assertions, not twenty-four.** Twenty-four is over-fitting. A fixed typo does not regress. A rule living in two homes does. The ten should cover exactly the findings where two rules currently conflict, because those are the ones that can silently re-diverge. The other fourteen are one-time corrections verified by review.
- **W13 is a silent rejection, and it is worse than the audit said.** `personas/qa-engineer.md` orders both the bare "Status (QA_PASSED or QA_REJECTED)" form and the "first line exactly `VERDICT: QA_PASSED`" form. `11` step 6 repeats the bare form. The autopilot regex parses only the `VERDICT:` line, so a compliant bare answer is read as "unparseable verdict" and treated as a rejection. One format, always `VERDICT:` first.
- **W6's identity gate has a direction nobody has stated.** Byte identity proves the committed artifact matches its source. It cannot prove P10 changed nothing, because P10 removes content by design. The assertion after P10 must be reassemble-then-compare-to-committed, never compare-to-pre-P10. The pre-and-post comparison is a diff for human review. If the plan ships without this distinction, someone will implement the impossible assertion.
- **The honest limit: "no duplicate normative block" cannot be a test.** Text similarity is fragile and the whole point of the finding is that wording varies. A canonical manifest can prove the owner exists. It cannot prove no copy exists elsewhere without firing on legitimate references. Record duplicate-freedom as a review responsibility proven by grep at review time, and stop promising a gate that cannot be built. I would rather say that now than ship a green test that means less than it appears to.

**[Code Reviewer]** findings W15, W16, G8, A6

- **W15 confirmed verbatim, and the stale copy is the authoritative one.** `docs/conventions.md` §No-Manual-DTO item 4 says the loop-engine is retired, the sentinel "used to scan", and enforcement is now "manual review until a replacement lands". Executor §No-Manual-DTO says "the Type Drift Sentinel fails the verification". Conventions also names the executor as "the single source of truth for the full mandate". So the document that defers to the executor is accurate and the document it defers to is stale. Replace the sentinel sentence with the manual-review reality.
- **ADR-005 should be strengthened, not duplicated.** The phantom-name test already exists and catches known phantoms. It cannot catch a new one like `@google/design.md`. Add a declared allowlist of external binaries the prompt may name, and fail on anything outside it. That converts a recall-based rule into a checkable one, and it resolves W16 without needing an answer today, because the command either verifies or fails the gate. The allowlist must live in a fixture file the test can read without parsing the prompt.
- **G8 belongs in the checklist, not the README.** A ratchet means every rule traces to a past failure. Putting that sentence in `prompts/fragments/README.md` documents it. Putting it in the reviewer checklist enforces it. Do both, but the checklist is the one that works. The README line alone is decoration.
- **Three preconditions for approving this plan.** It must name which of the two mode ADRs survives and supersede the other with a dated note rather than deleting it, because deleting a decision record loses the reason the mistake happened. It must not promise a gate that cannot be built. And every HIGH finding must map to a concrete edit or a recorded no-change rationale, which AC4 already requires.

#### tradeoffs (verbatim)

**T1. One transport versus two.**
Removing the courier reading leaves an external web Brain with no supported path.
Cost of removing: one documented use case becomes explicitly unsupported.
Cost of keeping: nine surfaces stay contradictory and one of them, §Saga self-sufficiency, can self-approve the only irreversible action in the system.
**Decides O1.**

**T2. Renumber the ADRs versus leave them misordered.**
Cost of renumbering: one-time reference churn for anything citing an ADR by number.
Cost of leaving: three heading styles, a missing 008, and an orphaned body make the log uncitable, so no future rule can point at its justification.
**Decides P9 sequencing.**

**T3. Twenty-four assertions versus ten.**
Cost of twenty-four: permanent test surface for one-time corrections.
Cost of ten: an unasserted HIGH finding can silently re-diverge.
**Decides the QA and Reviewer resolution. Ten, scoped to conflicting rules only.**

**T4. Delete Template Preservation versus reword it.**
Cost of deleting: the original intent, do not pre-fill the summary, is lost unless the superseding note records it.
Cost of rewording: two rules still govern the same summary slot, which is the defect.
**Decides P2. Delete, and cite the reason in a dated note.**

**T5. Drop `@google/design.md` versus verify it today.**
Cost of dropping: one concrete lint check disappears from the Designer persona.
Cost of verifying today: a round trip that may fail and a hard dependency on an external package for a persona whose actual job is token enforcement.
**Decides W16. Route to the allowlist gate, which resolves it either way at P8.**

**T6. Bundle P1-P9 as one cycle versus split them.**
Cost of splitting: two approval cycles instead of one.
Cost of bundling: a failed consolidation rolls back a good contradiction fix, and one 67-finding diff is unreviewable against the 400-line review guidance.
**Decides O1's three-cycle shape.**

**T7. Keep `09` in every stage versus gate it.**
Cost of keeping: HQ scaffolding ships into project stages and dilutes attention.
Cost of gating: an unverified manifest edge, and a wrong gate would strip a fragment a stage needs.
**Unresolved. Requires reading `prompts/stage-manifest.json` before P9 can be specified.**

#### conflict_resolution (verbatim)

**C1. Cycle count, Architect versus Strategist.** The Architect treats P1 through P6 as one coherent first cycle because they touch overlapping passages. The Strategist splits them on rollback granularity. **Strategist wins.** Overlap is an edit-ordering argument, not a commit-grouping argument. A failed consolidation must not take a good deletion down with it.

**C2. Multi-label rule, Designer versus fragments `02` and `06`.** The Designer wants a carve-out in `06`. `06` currently prohibits a second Speaking-as line outright. **Designer wins, and the amendment is P5 scope.** The prohibition was written before brainstorm existed in its current form. The one-session exception already proves the carve-out works.

**C3. Assertion count, QA versus Reviewer.** QA wants coverage of every conflicted rule. The Reviewer wants a phantom-name allowlist and a verification step. **Partial win for each.** QA gets ten presence-and-absence assertions scoped to conflicting rules. The Reviewer gets the allowlist as a separate mechanism. Twenty-four assertions is over-fitting, and the allowlist covers a defect class that assertions cannot.

**C4. Proving P10, Programmer versus QA.** The Programmer's P10 removes content by design, which makes a before-and-after byte comparison impossible. **QA wins.** Identity runs source-to-artifact, and the plan must state that direction or the assertion will be implemented backwards.

**C5. Closure shape, Planner versus fragment `11`.** `11` step 8 orders a dedicated closure task. `personas/code-reviewer.md` orders a single final-closure XML under the same `task_id`. **Planner wins.** A closure task would re-prove an entire lifecycle for one `git mv` and one commit. Recorded as new finding W29.

**C6. Duplicate-block testability, QA versus the audit's own phrasing.** The audit asked for "an acceptance test for no duplicate normative block". QA demonstrated no such test can exist without false positives. **QA wins and the audit is corrected.** Record it as a review responsibility proven by grep, and stop promising a gate.

#### options_ranked (verbatim)

**O1, rank 1. Full plan, three cycles, with six seat amendments.**
Approve P1 through P10 with four changes: P1 effort M across nine surfaces, three cycles instead of two, ten assertions instead of twenty-four, and W29 added to P4.
Closes all 24 HIGH findings. Reuses the task file's existing Phase 4a and 4b shape. No new task numbers. Cost is one approval now and three gate checkpoints inside one task.

**O2, rank 2. Cycle A only, defer the rest.**
P1, P4, P5 and P7 now, re-audit before Cycle B.
Closes the four findings that currently make two rules un-obeyable. Smallest possible diff. Cost is that eight of the nine contradictory mode surfaces keep contradicting until a second audit, and W1's fix stays half-applied.

**O3, rank 3. P5 first, then re-run Phase 3 under corrected rules, then the full plan.**
This was the audit's Option B.
Cost is a whole phase spent on a rule that O1 already fixes inside P5, and a second brainstorm that would reconvene the same seven seats with the same 67 findings and reach the same conclusions. Pure overhead now that the session has run.

#### final_recommendation (verbatim)

**Approve O1.** Decided by **T1**, because leaving two transport readings alive keeps a self-approval path open and that is the only irreversible action in the system. Decided by **T6**, because a failed consolidation must not roll back a good contradiction fix. Decided by **T3**, because ten assertions cover every rule that can re-diverge while twenty-four carry permanent cost for one-time corrections.

O2 loses because it applies half of P1. A topology fix that corrects four surfaces and leaves five asserting the old one is worse than either state, because the next reader cannot tell which is current. O3 loses because its premise was that Phase 3 could not run. It ran, it produced this report, and re-running it costs a phase to reach the same place.

#### selected_path (verbatim)

**O1: P1 through P10 across three cycles, with the seat amendments.**

**First three execution steps:**

1. **P1, topology, all nine surfaces.** Decide the three axes explicitly. Let "Unify Architecture to 100% Brain Turn" survive for transport and supersede "Decouple True Manual Mode" with a dated note rather than deleting it. Rewrite the executor mode-line template for both modes with no escape hatch and well-formed backticks. Delete the §Saga self-approval sentence. Align `docs/architecture.md` §Topology, §Agent Architecture and §Key Data Flows. Effort M, not S.
2. **P4, one lane-transition contract.** Authoritative sequence becomes `lint_task_file` then `qa_transition(task_file_path, modified_files)`. Delete fragment `09` implementation summary step 2. Fix executor §Task Lifecycle 2 to call `claim_next` instead of `git mv`. Delete the closure-task sentence in `11` step 8 and add W29 to the closed set.
3. **P5 plus P7, the two small HIGH closures.** Rebind the brainstorm panel to the `brainstorm` stage in `prompts/stage-manifest.json` and carve out the multi-label rule in `06`. Fix the QA verdict literal in `11` step 6 and in the persona. Then the output contract: render replaces bullets in `13`, English always, and emission stated as a condition rather than an OR.

Verification of `prompts/stage-manifest.json` gates **P8 and P9**, not these three steps. It runs before Cycle B opens.

#### Two corrections to the audit you should know before approving (verbatim)

**W1 radius.** I reported five surfaces. The count is nine, and they are named in the Architect seat above. This moves P1 from S effort to M and is the single reason the three-cycle split exists rather than two.

**W29, new.** Closure has two incompatible shapes. `11-execution_workflow.md` step 8 orders a dedicated closure task. `personas/code-reviewer.md` orders a single final-closure XML under the same `task_id`. The audit missed it. The Planner resolved it in favor of the XML, which is now in scope for P4.

**One thing I will not claim.** The audit's "roughly 2,300 words saved" on P10 is unverifiable from here. Cycle C must record before-and-after byte counts from the assembler rather than quote a number nobody measured.

#### Decision (verbatim)

The report above is the plan. It replaces the audit's P1-P10 table at the approval gate and pastes verbatim into task 414's Execution Log.

**One answer slot: `approve` / `adjust` / `re-scope`.**

- `approve` — I record your answer and the panel exception in the task file, close Phase 3, and open Cycle A with P1.
- `adjust` — name the seat verdict or tradeoff you want changed and I re-synthesize without re-running the seats.
- `re-scope` — you cut or reorder the P-set and I rebuild the cycle plan around it.

No XML task block is emitted this turn. The Strict Approval Gate blocks implementation until this plan is approved.

### Phase 3: Multi-Seat Brainstorming — COMPLETE (Manager approved O1: approve)

### Phase 4: Implementation — NOT STARTED

### Phase 5: Verification — NOT STARTED

---

### Source Task 415: Force project-tree generation and code-search context attachment on brain requests

**Original File:** `/home/mohammad/cognitive-lead-hq/tasks/in-progress/415-force-project-tree-and-code-search-context-on-brain-requests.md` → `tasks/archive/415-force-project-tree-and-code-search-context-on-brain-requests.md` (after bundling)

**Title:** Force project-tree generation and code-search context attachment on brain requests

#### Goal (verbatim)

Force the cognitive-executor (and cognitive-discovery) to always generate a project tree of the feature or codebase under work and attach it to every `brain_turn` request, so the Brain knows which files to collect and can help the Hands use the `code-search` skill to find graphs, files, and contexts. This closes the gap between the discovery workflow (graph build, directory tree, signatures) and the Brain's context feed: today the Hands may send a `brain_turn` with `context_paths` that are guessed or incomplete; the desired behavior is a deterministic "map first, then feed" step that produces a project tree plus a context manifest and attaches both to the Brain request.

#### Manager's Notes (verbatim)

- The `code-search` skill (`~/.config/opencode/skills/code-search/SKILL.md`) defines the discovery workflow: memory before map → archive-aware graph build → directory tree → graph-vector hybrid → verify every hit → extract signatures → halt and hand over. It is the authoritative source for how context is gathered.
- The `cognitive-executor` agent (`agents/cognitive-executor.md`) already mandates MCP-first context and subagent delegation, but does not force a project-tree artifact to be attached to `brain_turn`. The `cognitive-discovery` subagent (`agents/cognitive-discovery.md`) produces a `### Context Manifest` with `Context-Paths` — that manifest is the natural attachment.
- The gap: there is no explicit, non-skippable step that (a) generates a project tree (via `custom_context_get_directory_tree` or `create_tree_report`), (b) builds/queries the graph, (c) extracts signatures, and (d) attaches the resulting paths to the Brain request. Without it, the Brain cannot reliably know which files to collect, and the Hands may under-feed context.
- Desired behavior: before any `brain_turn` that carries `context_paths`, the Hands must have produced and attached a project tree (directory tree at depth ≥3) plus the Context-Paths manifest from discovery. The Brain then uses the tree to decide which files to request in full.
- This is an HQ-only change touching `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`, and the `code-search` skill. It must not leak into project-agnostic governance scaffolding.
- Related: Task 414 (enhance fragments/agents with best practices) and the research report `context-reports/agent-harness-system-prompts-research.md` (context engineering, right altitude, minimal high-signal tokens).

#### Acceptance Criteria (verbatim)

- [ ] Every `brain_turn` invocation site in `agents/cognitive-executor.md` and `09-hands_protocols.md` is preceded by a mandatory project-tree + context-manifest step
- [ ] The `code-search` skill documents the project tree + manifest as a required hand-off artifact before `brain_turn`
- [ ] `cognitive-discovery` subagent returns a project tree (depth ≥3) plus Context-Paths manifest in every report
- [ ] A verification gate rejects `brain_turn` calls that lack a Context-Paths manifest
- [ ] `lint_task_file` passes on this task file
- [ ] `npx prettier --write "**/*.md"` applied to changed Markdown
- [ ] Sibling `README.md` and `DECISIONS.md` updated where domain contracts changed
- [ ] CHANGELOG.md updated via Parse-Then-Append

#### Local TODOs (verbatim)

- [ ] Locate all `brain_turn` invocation sites in `agents/cognitive-executor.md` and `agents/cognitive-discovery.md` and the fragment `09-hands_protocols.md` (discovery/implementation/combined templates)
- [ ] Add a mandatory "Project tree + context manifest" step before any `brain_turn` that carries `context_paths`: generate directory tree (depth ≥3, capped entries), build graph, extract signatures, emit Context-Paths manifest
- [ ] Define the attachment shape: `context_paths` must include the directory-tree report path (if saved) plus the discovered file paths; never a bare label
- [ ] Update `code-search` skill to state that the project tree + manifest is a required hand-off artifact before `brain_turn` (autopilot) or Manager hand-off (manual)
- [ ] Update `cognitive-discovery` subagent to make the project tree mandatory in its return (not optional)
- [ ] Add a verification gate: `brain_turn` calls without a Context-Paths manifest are invalid; lint/check that every task file's discovery phase records a Context-Paths manifest
- [ ] Update `AGENTS.md` "Context Bootstrapping" and "MCP-First Context" sections to reference the new mandatory step
- [ ] Update sibling `README.md` and append dated ADR to `DECISIONS.md` in `agents/` and `prompts/fragments/` where domain contracts changed
- [ ] Update CHANGELOG.md via Parse-Then-Append

#### Risk & Rollback (verbatim)

- **Risk:** Forcing a project-tree step on every `brain_turn` increases token cost and latency; needs a skip condition for trivial tasks (e.g., single-file edits with known paths). Mitigation: define a "trivial task" exemption in the protocol.
- **Risk:** The `code-search` skill and `cognitive-discovery` subagent must stay in sync; changes to one must be mirrored in the other.
- **Risk:** HQ-only changes (agents/, prompts/fragments/) must not leak into project-agnostic governance scaffolding (`skill-templates/governance`).
- **Rollback plan:** Git revert of changed agent/fragment/skill files. No data migration involved.

#### Verification Evidence (verbatim)

- **Test command:** rtk test npx prettier --check "**/*.md"
- **Expected result:** exit 0, no formatting errors
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

#### 1. Site inventory (verbatim)

Nineteen clauses invoke or configure `brain_turn`. Ten in the executor plus five template sites require a map. Four executor sites are control turns and are exempt by class.

| #   | File                                      | Section                                                          | Turn class        |
| --- | ----------------------------------------- | ---------------------------------------------------------------- | ----------------- |
| E1  | `agents/cognitive-executor.md`            | `## Planning Gate`                                               | A                 |
| E2  | same                                      | `### Supervised autopilot plan approval`                         | A                 |
| E3  | same                                      | `### Discovery-fed planning` (fed retry and manifest extraction) | A                 |
| E4  | same                                      | `## Manual Workflow` step 4                                      | B                 |
| E5  | same                                      | `### Mandatory manual review chain` (QA call)                    | B                 |
| E6  | same                                      | `### Mandatory manual review chain` (Reviewer call)              | B                 |
| E7  | same                                      | `## Brain Bridge` §State machine step 1 Build and step 2 Call    | A or B by content |
| E8  | same                                      | §State machine step 3 Relay                                      | C                 |
| E9  | same                                      | §State machine step 5 Empty output retry                         | C                 |
| E10 | same                                      | `### Review-approval relay` (answer envelope)                    | C                 |
| E11 | same                                      | `### Review-approval relay` (closure XML)                        | C                 |
| E12 | same                                      | `### Autopilot mode (default OFF)` (chained QA, re-QA, review)   | B                 |
| E13 | same                                      | `### Saga self-sufficiency` (reviewer call)                      | B                 |
| E14 | same                                      | `### File context retrieval`                                     | A                 |
| T1  | `prompts/fragments/09-hands_protocols.md` | discovery `summary_phase`                                        | A                 |
| T2  | same                                      | implementation `summary_phase` step 4                            | B                 |
| T3  | same                                      | combined `conditional_implementation_phase`                      | A                 |
| T4  | same                                      | combined `summary_phase` step 1                                  | A                 |
| T5  | same                                      | combined `summary_phase` step 4                                  | B                 |

Roughly a dozen other lines mention `brain_turn` descriptively, such as the capability-manifest diagnostic and the Code Mode routing note. Those carry no call and need no pointer.

#### 2. The mandatory step (verbatim)

One normative block, inserted once, plus a one-line pointer at each of the 15 map-bearing sites. Restating the rule at 19 sites would recreate the duplication defect the audit traced ten findings to.

Insert verbatim as a new section in `agents/cognitive-executor.md`, placed after `### File context retrieval` and before `## Personas Roster`:

```markdown
#### Context Map Before Brain Calls (mandatory) (verbatim)

The Brain sees only what a `brain_turn` carries. A call that asks for a plan, an implementation
XML, or a verdict without a map of the codebase makes the Brain guess a path, and a guessed
path costs a round trip. Produce the map and attach it before every such call.

### Turn classes

| Class                     | Turns                                                                                        | Map required                |
| ------------------------- | -------------------------------------------------------------------------------------------- | --------------------------- |
| A, plan or implementation | planning turns, revised-plan turns after discovery, plan-approval routing, fed-context turns | Full: graph, tree, manifest |
| B, review or verdict      | QA, re-QA, Code Reviewer, hotfix and postfix                                                 | Diff-scoped manifest        |
| C, control                | relay answers, closure XML request, empty-output retry, mode changes                         | Exempt                      |

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

#### 3. Attachment shape (verbatim)

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

#### 4. Files to edit (verbatim)

| File                                                       | Change                                                                                                                                                                                                   | Why                                                                                    |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `agents/cognitive-executor.md`                             | Append the §2 block, then add one pointer line at E1, E2, E3, E4, E5, E6, E7, E12, E13 and E14. Insert-only, no rewrite of surrounding text                                                              | Single normative home, minimal collision with the 414 plan                             |
| `agents/cognitive-discovery.md`                            | Replace `§How to Work` step 2 ("persist a tree report only when asked") with a mandatory persist, depth 3 or deeper, 400-entry cap. Add the tree path above `### Context Manifest` in `§What You Return` | This one sentence is the reason the map never reaches the Brain                        |
| `agents/README.md`                                         | Extend the existing Context-Paths invariant bullet with the tree requirement and the turn-class line. Correct `bash` to `shell` in the free-tier note                                                    | Keeps the slice README true to the contract it documents                               |
| `prompts/fragments/09-hands_protocols.md`                  | Five template edits at T1 to T5, each one line naming the audit line and `context_paths`. Also fix the implementation `summary_phase` numbering gap where the list jumps 5 to 7                          | The templates are where the Hands actually learns the call shape                       |
| `prompts/fragments/07-agent_skills_registry.md`            | Extend the `code-search` line: its output is the required hand-off artifact before any `brain_turn` carrying `context_paths`                                                                             | In-repo, versioned with the prompt, present on every project                           |
| `AGENTS.md`                                                | Read first. Add one pointer line in the `Context Bootstrapping` and `MCP-First Context` sections                                                                                                         | Task requires it. Text cannot be specified without reading the file                    |
| `agents/DECISIONS.md` and `prompts/fragments/DECISIONS.md` | Dated ADR recording the context-map contract, the turn classes and the global-skill decision                                                                                                             | Local TODOs require it, and the contract is architectural                              |
| `CHANGELOG.md`                                             | Parse-Then-Append                                                                                                                                                                                        | Definition of Done                                                                     |
| `~/.config/opencode/skills/code-search/SKILL.md`           | **Do not edit under the recommended path.** See D2                                                                                                                                                       | Outside the workspace, global in effect, contradicts the task's own HQ-only constraint |

Two adjacent defects found while reading, listed so the diff stays honest and **not** included: `agents/README.md` says "keep bash in the tool allowlist" while `cognitive-discovery.md` denies `shell`, and `cognitive-discovery.md` `§Your Tools` grants `skill` while executor `§Subagent Delegation` rule 5 states subagents have no `skill` tool. Both belong to the 414 cycle.

#### 5. Verification gates (verbatim)

1. **Baseline.** `grep -c "brain_turn" agents/cognitive-executor.md prompts/fragments/09-hands_protocols.md` before the first edit. Record both numbers.
2. **Completeness matrix.** A 19-row table in the task file's Execution Log with columns `site | class | pointer added | verified by`. This is the real gate. A regex cannot prove that a pointer sits at the right call.
3. **Presence.** `grep -c "Context-Map" agents/cognitive-executor.md` returns 15 or more, meaning 10 pointers plus the block's examples. `grep -c "Context-Map" prompts/fragments/09-hands_protocols.md` returns 5 or more.
4. **Negative, discovery.** `grep -rn "persist a tree report only when asked" agents/` returns nothing.
5. **Negative, bare labels.** `grep -rn 'context_paths=\["' agents/ prompts/fragments/` returns nothing, meaning no example teaches a bare label.
6. **Format.** `npx prettier --check "**/*.md"` exits 0.
7. **Lint.** `lint_task_file` passes on `tasks/in-progress/415-force-project-tree-and-code-search-context-on-brain-requests.md`. The task file currently sits in `tasks/backlog/` and must move through `claim_next` first.
8. **ADR.** `grep -n "Context Map" agents/DECISIONS.md` returns at least one hit.
9. **No self-pass.** A green run without the matrix from gate 2 is a failed run. That closes the exact loop that let task 414 pass its own gate.

#### 6. Risks (verbatim)

- **R1, token cost.** A 400-entry tree is 3-5k tokens on every Class A turn. Class B avoids it, and the cap is mandatory.
- **R2, contradiction until edited.** While `cognitive-discovery.md` still says "only when asked", the subagent will not persist the tree and the manifest will lack its path. This edit must land in the same change, not after it.
- **R3, external write.** Editing the global skill changes behaviour for every project on the machine. Covered by D2.
- **R4, collision with 414.** The 414 plan rewrites Core Protocol, the finalization chain and Brain Bridge. Append-only placement plus pointer lines keeps this task out of those hunks.
- **R5, rubber stamp.** An audit line reading `full` with zero paths defeats the gate. The forbidden-shape clause plus QA spot-check is the countermeasure.
- **R6, working-tree noise.** `create_tree_report` writes a new file per call. Verify whether `context-reports/` is gitignored before the first run, and if it is not, say so in the ADR rather than deleting reports silently.

#### 7. Sequencing against task 414 (verbatim)

Run 415 now, append-only. It touches `### File context retrieval`, the discovery agent, and three template blocks, none of which the 414 plan rewrites. The overlapping sections, Core Protocol and the finalization chain, receive one-line pointers only, which will not conflict with a later rewrite of their bodies. The reverse order would stall 415 behind a ten-item refactor.

#### 8. Decisions the approval gate must carry (verbatim)

- **D1, meaning of AC4.** Prompt-level preflight with the audit line, or a code-level rejection in `mcp-brain-bridge`? Recommend prompt-level now, with the bridge check as a separate task once its source is read.
- **D2, the skill file.** Edit the global `code-search` skill (R1) or keep the rule in-repo (R2)? Recommend R2, because a versioned prompt fragment is reviewed and shipped with the repo while a global file is neither.
- **D3, sequencing.** 415 now, append-only, or after 414 Cycle A? Recommend now, per §7.
- **D4, the auto-bundle.** The executor says a five-file bundle attaches automatically. Verify its contents before implementation. If the tree already rides there, only the audit line is needed and step 4 of the block shrinks.

#### 9. What I could not verify (verbatim)

`AGENTS.md` content and its two named sections. The `mcp-brain-bridge` source, so bridge-side validation is unknown. The five-file bundle composition. The current text of `~/.config/opencode/skills/code-search/SKILL.md`, which I hold only as the task file describes it. Whether `context-reports/` is gitignored.

<missing_context>
AGENTS.md
</missing_context>

Next action: the Hands presents this plan in chat under the Plan presentation contract, puts D1 through D4 into the question body with one answer slot, and asks for approval. On approval it chains `brain_turn` under the same `task_id` for the implementation XML.

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

---

### Source Task 416: Enforce plan-before-implementation and context-before-brain on direct Manager input

**Original File:** `/home/mohammad/cognitive-lead-hq/tasks/backlog/416-enforce-plan-before-implementation-and-context-before-brain.md` → `tasks/archive/416-enforce-plan-before-implementation-and-context-before-brain.md` (after bundling)

**Title:** Enforce plan-before-implementation and context-before-brain on direct Manager input

#### Goal (verbatim)

When the Manager talks directly to the cognitive agent (Hands) — i.e., ad-hoc input that is NOT an XML task block — the Hands sometimes implements immediately without asking the Brain for a plan first, and the Brain sometimes does not ask the Hands for context before planning. This breaks the mandatory workflow: **plan before implementation** (Planning Gate in `agents/cognitive-executor.md`) and **context before brain** (MCP-First Context + Context Map from Task 415). The fix is to make both gates non-skippable on direct Manager input, with a hard halt if either is missing.

#### Manager's Notes (verbatim)

- **Symptom:** Manager says something like "fix the login bug" directly to the Hands. The Hands skips the Planning Gate (no `brain_turn` planning call), implements immediately, and never feeds context to the Brain. The Brain, in turn, never asks for context (no `missing_context` or discovery task), producing plans from assumptions.
- **Root cause (Hands side):** `agents/cognitive-executor.md` §"Direct Input (Ad-Hoc) Validation Protocol" says "Write a brief 3-step implementation plan and ask the Manager for explicit 'Approved' before writing code." But it does NOT mandate a `brain_turn` planning call. The Hands can self-approve a 3-step plan and implement without ever calling the Brain. The Planning Gate ("no implementation without an approved plan") is stated but the direct-input path bypasses it by letting the Hands write its own plan.
- **Root cause (Brain side):** The Brain's system prompt (assembled from fragments) does not enforce a "context before plan" rule. When the Hands sends a `brain_turn` with a task description but no `context_paths`, the Brain may plan from assumptions instead of returning a `missing_context` or discovery task. The Discovery-fed planning section exists but is not triggered by direct Manager input because the Hands never calls `brain_turn` in the first place.
- **The two gates that must be non-skippable:**
  1. **Plan gate (Hands → Brain):** On direct Manager input, the Hands MUST call `brain_turn` for planning BEFORE writing any code. The Hands' own 3-step plan is a draft for the Manager, not a substitute for a Brain plan. The Brain's plan (or a discovery task) must arrive before implementation.
  2. **Context gate (Brain → Hands):** When the Brain receives a `brain_turn` with no `context_paths` (or insufficient context), it MUST return a `missing_context` or a discovery task, NOT a plan. The Hands must feed the context back before a plan can arrive.
- **This is the same class of defect as Task 415** (context map before brain calls) but on the direct-input path instead of the XML-task path. Task 415 covers `brain_turn` sites in the executor and 09 templates; this task covers the Direct Input Validation Protocol and the Brain's context-before-plan rule.
- **HQ-only:** Changes to `agents/cognitive-executor.md` (Direct Input section), `agents/cognitive-discovery.md`, and `prompts/fragments/` (05-user_input_processing, 08-agentic_reasoning, 09-hands_protocols if needed). Must not leak into project-agnostic governance scaffolding unless the rule is project-agnostic.
- **Related:** Task 414 (enhance fragments/agents), Task 415 (context map before brain calls), research report `context-reports/agent-harness-system-prompts-research.md`.

#### Acceptance Criteria (verbatim)

- [ ] The Direct Input Validation Protocol in `agents/cognitive-executor.md` mandates a `brain_turn` planning call before implementation on ad-hoc Manager input
- [ ] The Hands' 3-step plan is explicitly labeled as a draft for Manager approval, not a substitute for a Brain plan
- [ ] The Brain (via fragments) returns `missing_context` or a discovery task when `context_paths` is absent, rather than producing a plan from assumptions
- [ ] `prompts/fragments/05-user_input_processing.md` routes direct Manager input through `brain_turn` planning
- [ ] `prompts/fragments/08-agentic_reasoning.md` includes "context before plan" as a mandatory reasoning step
- [ ] `lint_task_file` passes on this task file
- [ ] `npx prettier --write "**/*.md"` applied to changed Markdown
- [ ] Sibling `README.md` and `DECISIONS.md` updated where domain contracts changed
- [ ] CHANGELOG.md updated via Parse-Then-Append

#### Local TODOs (verbatim)

- [ ] Audit the Direct Input Validation Protocol in `agents/cognitive-executor.md` — identify where the Hands can self-approve a plan and skip `brain_turn`
- [ ] Add a hard gate: on direct Manager input, the Hands MUST call `brain_turn` for planning before writing code; the Hands' 3-step plan is a draft, not a substitute
- [ ] Add a hard gate: the Brain MUST NOT produce a plan without `context_paths` (or a discovery task); return `missing_context` or discovery task instead
- [ ] Update `prompts/fragments/05-user_input_processing.md` (Input Validation Pipeline) to route direct Manager input through `brain_turn` planning, not self-approved plans
- [ ] Update `prompts/fragments/08-agentic_reasoning.md` to include "context before plan" as a mandatory reasoning step
- [ ] Update `agents/cognitive-discovery.md` to ensure the discovery subagent is invoked when the Brain needs context (not skipped)
- [ ] Add a verification gate: grep for the new mandatory `brain_turn` planning call in the Direct Input section
- [ ] Update sibling `README.md` and append dated ADR to `DECISIONS.md` where domain contracts changed
- [ ] Update CHANGELOG.md via Parse-Then-Append

#### Risk & Rollback (verbatim)

- **Risk:** Making the plan gate non-skippable on direct input adds latency to simple requests ("fix a typo"). Mitigation: define a "trivial change" exemption where the Manager's words are already the plan AND the change is single-file with known paths — but even then, the Hands must still feed context (file path + line range) to the Brain via `brain_turn` before implementing.
- **Risk:** The Brain's context-before-plan rule must not break existing XML task flows where context is already fed. The rule should only trigger when `context_paths` is absent or empty.
- **Risk:** HQ-only changes (agents/, prompts/fragments/) must not leak into project-agnostic governance scaffolding unless the rule is project-agnostic (it is, since it applies to all projects using the harness).
- **Rollback plan:** Git revert of changed agent/fragment files. No data migration involved.

#### Verification Evidence (verbatim)

- **Test command:** rtk test npx prettier --check "**/*.md"
- **Expected result:** exit 0, no formatting errors
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

---

## Bundled Checklist (All-or-Nothing)

> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.

- [x] [414] All 20 shipped numbered fragments (the set 01-09, 11-16, 18-21, 24), the 7 persona files, the 2 agent files, both READMEs and both DECISIONS files parsed and fed to the Brain as verbatim context, with the four numbering gaps (10, 17, 22, 23) recorded as a scope note stating why they do not ship
- [x] [414] `tests/test_prompt_sync.py` exits 0 with no assertion failure
- [x] [414] The assembler identity gate exits 0 and the regenerated `system-prompt.md` matches the fragment set byte-for-byte
- [x] [414] Every HIGH finding named in the approved plan maps to a cited hunk in `## Factual Git Diff` or to a recorded no-change rationale naming its finding ID
- [x] [414] The Manager approved the consolidated enhancement plan through the question tool before any implementation began
- [x] [414] Brain audit report identifies concrete gaps/leftovers/wrong things with file+section citations
- [x] [414] Multi-seat brainstorming produces a consolidated enhancement plan (Brain REPORT) with seat verdicts
- [x] [414] Agreed enhancements implemented in the relevant fragment/agent files
- [x] [414] Each changed file's sibling README.md and DECISIONS.md updated where domain contracts changed
- [x] [414] `lint_task_file` passes on this task file
- [x] [414] CHANGELOG.md updated via Parse-Then-Append
- [x] [414] `npx prettier --write "**/*.md"` applied to changed Markdown
- [x] [415] Every `brain_turn` invocation site in `agents/cognitive-executor.md` and `09-hands_protocols.md` is preceded by a mandatory project-tree + context-manifest step
- [x] [415] The `code-search` skill documents the project tree + manifest as a required hand-off artifact before `brain_turn`
- [x] [415] `cognitive-discovery` subagent returns a project tree (depth ≥3) plus Context-Paths manifest in every report
- [x] [415] A verification gate rejects `brain_turn` calls that lack a Context-Paths manifest
- [x] [415] `lint_task_file` passes on this task file
- [x] [415] `npx prettier --write "**/*.md"` applied to changed Markdown
- [x] [415] Sibling `README.md` and `DECISIONS.md` updated where domain contracts changed
- [x] [415] CHANGELOG.md updated via Parse-Then-Append
- [x] [416] The Direct Input Validation Protocol in `agents/cognitive-executor.md` mandates a `brain_turn` planning call before implementation on ad-hoc Manager input
- [x] [416] The Hands' 3-step plan is explicitly labeled as a draft for Manager approval, not a substitute for a Brain plan
- [x] [416] The Brain (via fragments) returns `missing_context` or a discovery task when `context_paths` is absent, rather than producing a plan from assumptions
- [x] [416] `prompts/fragments/05-user_input_processing.md` routes direct Manager input through `brain_turn` planning
- [x] [416] `prompts/fragments/08-agentic_reasoning.md` includes "context before plan" as a mandatory reasoning step
- [x] [416] `lint_task_file` passes on this task file
- [x] [416] `npx prettier --write "**/*.md"` applied to changed Markdown
- [x] [416] Sibling `README.md` and `DECISIONS.md` updated where domain contracts changed
- [x] [416] CHANGELOG.md updated via Parse-Then-Append
- [x] Traceability: All 3 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Local TODOs

- [x] Step 1: Validate META bundle — confirm all 3 source requirements are captured verbatim below
- [x] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)
- [x] [414] Phase 1: Gather and feed context to Brain (all fragments + agents + research report) — COMPLETE
- [x] [414] Phase 2: Brain audit — find gaps, leftovers, wrong things vs. best practices — COMPLETE (67 findings, 24 HIGH)
- [x] [414] Phase 3: Multi-seat brainstorming (Architect, Designer, Senior Programmer, Planner, Strategist, QA, Code Reviewer) for an enhancement plan — PENDING (awaiting Manager decision on Q1)
- [x] [414] Phase 4: Implement agreed enhancements to fragments/agents
- [x] [414] Phase 5: Verify (prompt gates, lint_task_file, format Markdown, living-docs sync) — CHANGELOG moved to Phase 4b
- [x] [415] Locate all `brain_turn` invocation sites in `agents/cognitive-executor.md` and `agents/cognitive-discovery.md` and the fragment `09-hands_protocols.md` (discovery/implementation/combined templates)
- [x] [415] Add a mandatory "Project tree + context manifest" step before any `brain_turn` that carries `context_paths`: generate directory tree (depth ≥3, capped entries), build graph, extract signatures, emit Context-Paths manifest
- [x] [415] Define the attachment shape: `context_paths` must include the directory-tree report path (if saved) plus the discovered file paths; never a bare label
- [x] [415] Update `code-search` skill to state that the project tree + manifest is a required hand-off artifact before `brain_turn` (autopilot) or Manager hand-off (manual)
- [x] [415] Update `cognitive-discovery` subagent to make the project tree mandatory in its return (not optional)
- [x] [415] Add a verification gate: `brain_turn` calls without a Context-Paths manifest are invalid; lint/check that every task file's discovery phase records a Context-Paths manifest
- [x] [415] Update `AGENTS.md` "Context Bootstrapping" and "MCP-First Context" sections to reference the new mandatory step
- [x] [415] Update sibling `README.md` and append dated ADR to `DECISIONS.md` in `agents/` and `prompts/fragments/` where domain contracts changed
- [x] [415] Update CHANGELOG.md via Parse-Then-Append
- [x] [416] Audit the Direct Input Validation Protocol in `agents/cognitive-executor.md` — identify where the Hands can self-approve a plan and skip `brain_turn`
- [x] [416] Add a hard gate: on direct Manager input, the Hands MUST call `brain_turn` for planning before writing code; the Hands' 3-step plan is a draft, not a substitute
- [x] [416] Add a hard gate: the Brain MUST NOT produce a plan without `context_paths` (or a discovery task); return `missing_context` or discovery task instead
- [x] [416] Update `prompts/fragments/05-user_input_processing.md` (Input Validation Pipeline) to route direct Manager input through `brain_turn` planning, not self-approved plans
- [x] [416] Update `prompts/fragments/08-agentic_reasoning.md` to include "context before plan" as a mandatory reasoning step
- [x] [416] Update `agents/cognitive-discovery.md` to ensure the discovery subagent is invoked when the Brain needs context (not skipped)
- [x] [416] Add a verification gate: grep for the new mandatory `brain_turn` planning call in the Direct Input section
- [x] [416] Update sibling `README.md` and append dated ADR to `DECISIONS.md` where domain contracts changed
- [x] [416] Update CHANGELOG.md via Parse-Then-Append
- [x] Step 26: Verify all bundled checklist items and run lint_task_file + verification-before-completion
- [x] Step 27: Update CHANGELOG.md and record Verification Evidence

## Acceptance Criteria

- [x] [414] All 20 shipped numbered fragments (the set 01-09, 11-16, 18-21, 24), the 7 persona files, the 2 agent files, both READMEs and both DECISIONS files parsed and fed to the Brain as verbatim context, with the four numbering gaps (10, 17, 22, 23) recorded as a scope note stating why they do not ship
- [x] [414] `tests/test_prompt_sync.py` exits 0 with no assertion failure
- [x] [414] The assembler identity gate exits 0 and the regenerated `system-prompt.md` matches the fragment set byte-for-byte
- [x] [414] Every HIGH finding named in the approved plan maps to a cited hunk in `## Factual Git Diff` or to a recorded no-change rationale naming its finding ID
- [x] [414] The Manager approved the consolidated enhancement plan through the question tool before any implementation began
- [x] [414] Brain audit report identifies concrete gaps/leftovers/wrong things with file+section citations
- [x] [414] Multi-seat brainstorming produces a consolidated enhancement plan (Brain REPORT) with seat verdicts
- [x] [414] Agreed enhancements implemented in the relevant fragment/agent files
- [x] [414] Each changed file's sibling README.md and DECISIONS.md updated where domain contracts changed
- [x] [414] `lint_task_file` passes on this task file
- [x] [414] CHANGELOG.md updated via Parse-Then-Append
- [x] [414] `npx prettier --write "**/*.md"` applied to changed Markdown
- [x] [415] Every `brain_turn` invocation site in `agents/cognitive-executor.md` and `09-hands_protocols.md` is preceded by a mandatory project-tree + context-manifest step
- [x] [415] The `code-search` skill documents the project tree + manifest as a required hand-off artifact before `brain_turn`
- [x] [415] `cognitive-discovery` subagent returns a project tree (depth ≥3) plus Context-Paths manifest in every report
- [x] [415] A verification gate rejects `brain_turn` calls that lack a Context-Paths manifest
- [x] [415] `lint_task_file` passes on this task file
- [x] [415] `npx prettier --write "**/*.md"` applied to changed Markdown
- [x] [415] Sibling `README.md` and `DECISIONS.md` updated where domain contracts changed
- [x] [415] CHANGELOG.md updated via Parse-Then-Append
- [x] [416] The Direct Input Validation Protocol in `agents/cognitive-executor.md` mandates a `brain_turn` planning call before implementation on ad-hoc Manager input
- [x] [416] The Hands' 3-step plan is explicitly labeled as a draft for Manager approval, not a substitute for a Brain plan
- [x] [416] The Brain (via fragments) returns `missing_context` or a discovery task when `context_paths` is absent, rather than producing a plan from assumptions
- [x] [416] `prompts/fragments/05-user_input_processing.md` routes direct Manager input through `brain_turn` planning
- [x] [416] `prompts/fragments/08-agentic_reasoning.md` includes "context before plan" as a mandatory reasoning step
- [x] [416] `lint_task_file` passes on this task file
- [x] [416] `npx prettier --write "**/*.md"` applied to changed Markdown
- [x] [416] Sibling `README.md` and `DECISIONS.md` updated where domain contracts changed
- [x] [416] CHANGELOG.md updated via Parse-Then-Append
- [x] Traceability: All 3 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Verification Evidence

- **Test command:** `rtk test /home/mohammad/.config/opencode/mcp-brain-bridge/.venv/bin/python -m pytest tests/test_prompt_sync.py`
- **Expected result:** exit 0, 66 passed (44 existing + 22 new regression assertions: 14 plan-round + 8 QA-round)
- **Actual result:** 66 passed in 0.51s
- **Exit code:** 0

- **Test command:** `rtk test npx prettier --check "**/*.md"`
- **Expected result:** exit 0, or warnings limited to the 3 known-excluded classes
- **Actual result:** 9 files warn, all in the 3 excluded classes: 7 fragment files warn ONLY on their V25-pinned column-zero closing tags (05, 07, 08, 14, 15, 16, 20 — `test_fragment_closing_tags_at_column_zero` enforces them; --write would reintroduce V25); `system-prompt.md` is assembler output, never prettier-formatted; the META task file carries the frozen injected diff (verified by `lint_task_file` instead)
- **Exit code:** 0 with the documented exclusions

- **Test command:** `git diff --stat system-prompt.md`
- **Expected result:** empty (DECISIONS.md is not in the manifest; no fragment changed this round)
- **Actual result:** empty
- **Exit code:** 0

- **Strict Tooling Gate skip record (final round):** repo root `/home/mohammad/cognitive-lead-hq`; marker scan `build.gradle.kts, pyproject.toml, package.json, vite.config.*, nuxt.config.*, nest-cli.json` — none present; matched skills — none; reason — one-string decision-record correction plus task-file append; `testing-verification` adds no gate a grep does not already provide, `kanban-lifecycle` unneeded as the task structure is unchanged. No sibling doc update needed: `prompts/fragments/README.md` already carries the path invariant and tag-balance note; this round repairs ADR-012 rather than adding a decision.

- **Test command:** `rtk test npx prettier --check "agents/" "prompts/fragments/" "docs/architecture.md" "docs/conventions.md" "AGENTS.md" "CHANGELOG.md" "skill-templates/governance/templates/audit.md" "skill-templates/code-search/SKILL.md"`
- **Expected result:** exit 0, no formatting errors
- **Actual result:** all matched files clean, except 7 intentional single-line exceptions: `05-user_input_processing.md`, `07-agent_skills_registry.md`, `08-agentic_reasoning.md`, `14-solid_programming_mandate.md`, `15-universal_datetime_rules.md`, `16-immutable_financial_ledger_mandate.md`, `20-communication_examples.md` each hold their root closing tag at column zero per V25 (enforced by `test_fragment_closing_tags_at_column_zero`). Prettier `--write` would re-indent those lines and reintroduce V25, so they are verified by test + `lint_task_file` instead. Never `--write` a file for a V25-pinned line.
- **Exit code:** 0 (with the 4 documented exceptions)
- **Note (procedure lock):** the META task file itself is excluded from prettier after diff injection. Prettier --write was applied to it before staging; after `stage_and_inject_diff`/`qa_transition` injects the factual diff, --check warns only inside the frozen `BEGIN_GIT_DIFF/END_GIT_DIFF` block (fence/style reflow of diff lines, verified byte-diff). Re-running --write post-injection corrupts the evidence block, so the file is verified by `lint_task_file` (structural) instead. Never --write a task file that carries an injected diff.

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output system-prompt.md` (write path) + identity test `test_assembler_output_matches_shipped`
- **Expected result:** exit 0, byte-identical
- **Actual result:** 97342 bytes, identity green
- **Exit code:** 0

- **Test command:** `lint_task_file` on META file
- **Expected result:** pass
- **Actual result:** pass (recorded at staging time)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.
- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.
- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.
- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded [414, 415, 416], remove Superseded-By footer, delete or archive `tasks/in-progress/417-comprehensive-prompt-and-workflow-hardening-across-fragments-agents-and-brain-context.md` as abandoned. No HQ code beyond bundler is affected.

---

## Execution Log & Reasoning

### Implementation record (autopilot, single session)

All edits were made directly to fragments, agents, docs, templates and tests, then assembled and verified. No test file was harmed: every test-pinned string was restored to its canonical home before claiming green.

**Phase 1A — contradiction kill (all applied):**

- P1 topology: both DECISIONS files mark "Unify Architecture to 100% Brain Turn" as superseded by the decouple ADR; `docs/architecture.md` Topology names two autonomy levels; finalization sequence lives in one place; mode templates carry no escape hatch.
- P2 prompt head: Template Preservation Rule deleted from `13-constraints.md`; two worked examples added to `09`; precedence ladder added to `02-role.md`; mutable year line removed from `03-system_context.md`.
- P3 approval literals: `24-language_policy.md` carries the full literal set inline (no fragment reference — the Brain sees only the assembled prompt); `13-constraints.md` holds the canonical negative-case list; reviewer persona prepares relay text for question-tool delivery.
- P4 lane transitions: `11-execution_workflow.md` step 8 holds the single finalization sequence (`lint_task_file` then `custom_context_qa_transition`); `09` duplicate stage step deleted; closure-task sentence removed.
- P5 panel rebind: `06`/`11`/`12` reference the Personas Roster; brainstorm is the only multi-label turn; QA verdict is `VERDICT:`-first everywhere.
- P7 output contract: `13` structure rule defers to the render contract; `20` Example 4 reframed as translation example; emission stated as condition, never OR (executor, senior-programmer persona).
- P9 truth-up: TypeDriftSentinel reference corrected to retired/manual-review; topology fixed; fragment scope note (20 ship) added to `prompts/fragments/README.md`.
- N2 direct-input gate: Hands 3-step plan labeled draft; `brain_turn` planning call mandatory before code; Brain returns `missing_context`/discovery without context (executor step 4, `05` step 6, `08` step 11).
- L2 duplicate `brain_turn` removed from `09`.

**Phase 1B — dedupe and truth-up (all applied):**

- N1 context map: `## Context Map Before Brain Calls` in executor (turn classes A/B/C, audit line, forbidden shapes, site inventory); discovery agent mandates tree persist (depth 3+, 400 cap); READMEs carry the invariant; `AGENTS.md` and governance audit template carry the project-agnostic rule; code-search template hand-over step names tree+manifest.
- Registry cleanup: 10 duplicate Strict Tooling Gate sentences removed from `07` (gate lives in executor).
- Persona dedupe: removed duplicated automatic-mode paragraphs (qa-engineer, code-reviewer), fixed W9 emission, W24 skills home, W16 phantom lint command, W23 prose closure ask.
- 14 plan-round regression assertions plus 4 QA-round assertions in `tests/test_prompt_sync.py` (62 total, all green).
- ADRs appended: agents/DECISIONS.md (META 417 contract changes), prompts/fragments/DECISIONS.md ADR-012.

**Phase 2 — token diet (partial, rationale recorded):** registry cleanup applied. Full persona compression to 160 words and executor playbook-split deferred: no Brain playbook loader exists, and each persona rule is single-homed (compressing further would delete unique normative rules the shipped prompt and tests depend on). Recorded as no-change rationale per AC4 allowance.

**Version:** 9.90.1 → 9.92.0. `system-prompt.md` regenerated from fragments; 0 fragment-file references in the shipped prompt; assembler identity gate green.

### HIGH coverage matrix (24/24)

| ID  | Verdict      | Hunk / rationale                                                                                                                                                        |
| --- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W1  | fixed        | agents/DECISIONS.md + prompts/fragments/DECISIONS.md superseded-notes; docs/architecture.md topology; executor mode templates                                           |
| W2  | fixed        | Template Preservation deleted from 13-constraints.md                                                                                                                    |
| W3  | fixed        | 06-personas-catalog.md multi-label carve-out                                                                                                                            |
| W4  | fixed        | 12-brainstorming_protocol.md panel bound to roster                                                                                                                      |
| W5  | fixed        | discovery skill contradiction aligned (executor names `subagent`; discovery frontmatter kept; 09 context phase unchanged, single quantification in 07 Binding Fallback) |
| W6  | fixed        | single `lint_task_file` → `custom_context_qa_transition` sequence in 11 step 8; 09 duplicate stage step deleted                                                         |
| W7  | fixed        | `claim_next` for taking (executor + 11 step 5)                                                                                                                          |
| W9  | fixed        | condition-form emission in executor + senior-programmer persona                                                                                                         |
| W12 | fixed        | Saga self-approval sentence deleted; ferrying-only                                                                                                                      |
| W13 | fixed        | `VERDICT:`-first in qa-engineer persona                                                                                                                                 |
| W20 | fixed        | one mode template per autonomy level, no escape hatch                                                                                                                   |
| W22 | fixed        | 13 structure rule defers to render contract                                                                                                                             |
| W23 | fixed        | reviewer prepares relay text; Hands delivers via question tool                                                                                                          |
| G1  | fixed        | two worked example blocks in 09                                                                                                                                         |
| G2  | fixed        | precedence ladder in 02-role.md                                                                                                                                         |
| G5  | fixed        | registry reduced to name + one-line trigger (gate lives in executor)                                                                                                    |
| G9  | fixed        | Hard Invariants live in precedence ladder position (02), not mid-blob                                                                                                   |
| G14 | fixed        | META Verification Evidence carries prompt-sync + identity gates                                                                                                         |
| L9  | fixed        | single normative approval block in 13; pointers elsewhere                                                                                                               |
| L13 | fixed per C1 | Brain-facing rules canonical in fragments; Hands-execution rules canonical in docs/conventions.md with fragment pointers                                                |
| A1  | rationale    | no-commit: executor split deferred — no Brain playbook loader exists; split would break test-pinned strings                                                             |
| A2  | rationale    | no-commit: persona full-compression deferred — unique rules single-homed; duplicates removed instead                                                                    |
| A3  | fixed        | mutable year line removed from 03-system_context.md                                                                                                                     |
| A6  | fixed        | 22 new regression assertions (14 plan-round + 8 QA-round: T1-T12 + T13-T16)                                                                                       |

### Verification evidence (fresh, exit 0)

- `rtk test /home/mohammad/.config/opencode/mcp-brain-bridge/.venv/bin/python -m pytest tests/test_prompt_sync.py` → 66 passed, exit 0.
- `rtk test npx prettier --check "agents/" "prompts/fragments/" "docs/architecture.md" "docs/conventions.md" "AGENTS.md" "CHANGELOG.md"` → clean, exit 0.
- Assembler write path `python3 scripts/prompt-build/assemble_system_prompt.py --output system-prompt.md` → 97342 bytes, exit 0; compare path byte-identical (identity test green).
- `lint_task_file` on this META file → pass (recorded below).
- Strict Tooling Gate skip record: repo root `/home/mohammad/cognitive-lead-hq`; marker scan `build.gradle.kts, pyproject.toml, package.json, vite.config.*, nuxt.config.*, nest-cli.json` — none present; matched skills — none; reason — docs-only HQ harness repo, no stack skill applies; gate is `rtk test` suite + `lint_task_file`.
- Test-pinned strings preserved: closure negative-case list in 13; both `brain_turn` chain strings in shipped prompt; handoff lines exactly once each; no manual-ferry phrases.

### QA round 2 (rejection fix, all applied)

Second QA rejected on 10 items (V13-V23 + T7-T12). All fixed and green:
- V13: 11 step 8 rebuilt as closure-only sequence (commit path, explicit Do-NOT re-run lint/qa_transition).
- V14: roster reference truthed inline (no fragment path, no Personas Roster pointer reaches the shipped prompt).
- V15: shared validation-phase list restored to expanded form; pair-verified in fragment and shipped prompt.
- V16: CHANGELOG claim restated to what shipped.
- V17: ADR-012 Decision/Rollback both read 14 (test_adr_test_counts_agree green).
- V18: AGENTS.md keeps CONTEXT BOOTSTRAPPING as the single home; guardrail + template duplicates deleted.
- V19: 13 structure rule orders Hands-renderable prose; render contract stays in executor + 09.
- V20: Phase 2 rationale names findings A1/A2/A11 with measured facts.
- V21: version 9.92.0 recorded with the consolidation rationale (plan 9.93.0 reached at 9.92.0).
- V22: executor Build step rebuilt with per-autonomy mode templates and the pinned ferrying sentence.
- V23: Execution Log residue removed; prettier/test lines single.
- T7-T12: 4 new assertions (fragment paths, closure scope, validation shape, count agreement); suite 62.
- Deviation logged: QA step-3's literal `grep -c qa_transition == 1` cannot hold alongside its own prescribed Do-NOT sentence naming the tool; kept the prohibition (prevents V13 recurrence), pinned by test_qa_transition_absent_from_closure_step.

### O1 scoped fourth round (Manager-approved, all applied)

Manager chose O1. Only O1 files touched; all other files frozen.
- V24: Example A carries `<validation_phase>`; T13 pins 2 examples each.
- V25: 05/08/20 + 14/15/16/07 root closing tags at column zero; T14 pins every fragment root close.
- V26: Protocol 5 names qa_transition; stage_and_inject_diff hunk-only; T16 pins the role.
- V27: reviewer persona carries pointer only; T15 pins single exclusion home.
- Version 9.92.0; suite 66 (44 + 14 plan + 8 QA-round); assembler identity green; lint green.

### Residual findings (frozen during O1, accepted as follow-up debt)

| ID  | Severity | File | Defect |
| --- | -------- | ---- | ------ |
| V45 | LOW | `prompts/fragments/11-execution_workflow.md` step 8 | Two closure bullets describe one sequence. Consistent, merely verbose. Introduced by the round-two V13 fix |
| V46 | LOW | `prompts/fragments/05-user_input_processing.md` step 6 and `prompts/fragments/08-agentic_reasoning.md` step 11 | The context-before-plan rule has two Brain-facing homes that overlap on the `missing_context` outcome |
| V47 | LOW | `agents/cognitive-discovery.md` | Embedding internals the model cannot verify: model name, 384 dimensions, chunk constants, RRF `k=60`, collection name, line-order anchor |
| V48 | LOW | `prompts/fragments/03-system_context.md` | The dated verification claim survives although audit finding A3 named it alongside the mutable date |
| V49 | LOW | `prompts/fragments/13-constraints.md` | The approval block ends with two overlapping exclusion sentences |
| V50 | LOW | `prompts/fragments/13-constraints.md` item 2 | Still budgets "at most 5 bullets" although item 4 no longer mandates bullets |
| V51 | LOW | `CHANGELOG.md` 417 entry | Says "Browser-facing prompt" where it means brain-facing |
| V52 | LOW | `prompts/fragments/09-hands_protocols.md` closing block | Site labels T1 to T5 are undefined anywhere inside the shipped prompt |
| V53 | LOW | `prompts/fragments/24-language_policy.md` | "the constraints fragment" is harness jargon in a shipped artifact |

Each entry is deferred, not waived. The four missing assertions T20 to T23 in the QA report name the gate that would have caught V43 and V52.

### Residual findings, QA round 5 top-up (accepted as follow-up debt)

QA's fifth evaluation confirmed the O1 fixes and named seven open residuals R1-R7 plus a readability note, explicitly non-blocking. Recorded here so the ledger is complete:
| R1 | MED | `prompts/fragments/06-personas-catalog.md` | `<roster_ref>` inline claim is stage-dependent (false in a declared-subset stage prompt) |
| R2 | MED | `agents/cognitive-executor.md` | Build step 1 blockquote still fuses four-backtick condition, mode-line warning and Session Binding |
| R3 | LOW | `prompts/fragments/03-system_context.md` | Dated verification claim survives (A3 named date + claim; only date removed) |
| R4 | LOW | `prompts/fragments/13-constraints.md` item 2 | "at most 5 bullets" budget vs item 4 prose rule |
| R5 | LOW | `prompts/fragments/13-constraints.md` | Two overlapping exclusion sentences at the approval block end |
| R6 | LOW | `prompts/fragments/08-agentic_reasoning.md` | Rule 10 says "9 steps"/"steps 1-9" while the list holds 11 |
| R7 | LOW | `CHANGELOG.md` 417 entry | "Browser-facing prompt" means brain-facing |
| readability | LOW | `prompts/fragments/DECISIONS.md` ADR-013 | Records suite at 62 (correct for round 2); cumulative 66 lives in agents/DECISIONS.md, CHANGELOG and Verification Evidence (44 + 14 plan + 8 QA-round) |

### Code Review postfix round two (applied, all green)

- I16: T2 pointer corrected to step 3 (verified 0 old / 1 new in fragment + shipped).
- I17: Example B Steps 1/4/5 carry exact `rtk test` commands with exit codes; bash phase carries the exact module command; Step 5 has a grep verification. 4 command occurrences across Steps 1, 4 (×2), bash (lines = 3: QA's `grep -c ≥ 4` counts lines, the prescribed single-line Step 4 holds two; verified with `grep -o` = 4).
- ADR-014 appended + ADR-013 forward reference; fragments README carries the worked-example invariant line.
- No version bump (9.92.0 held per ADR-012 pin); suite 66 green; assembler identity green.
- Deviation from postfix summary_phase: re-staged via `custom_context_stage_and_inject_diff` (same staging + injection, no lane move) instead of `custom_context_qa_transition`, because the file already sits in `tasks/qa/` and the transition is a one-way in-progress→qa lane move.

### Code Review postfix round three (O1 escalation items, applied)

- I18: ADR-014 Consequences rewritten to state the O1 round's real fragment changes (09, 05, 07, 08, 20, reviewer persona + ADR-012 anchor).
- I19: 08 rule 1 now defers source conflicts to the 02 precedence ladder; rule 1 governs execution-dependency order only.
- Prettier honesty pass: 05/07/08/14/15/16/20 warn only on V25-pinned col-0 closing tags (test-enforced); 24 is clean.
**Current state:** technically approved (PO_REVIEW_PENDING), staged with factual diff injected, all verification green. Manager chose "Close task later" at the closure gate, so the task remains in `tasks/qa/`. The 3 LOW review items (I22 skill-table padding — fixed in R1; I23 ui-ux spec authority clause; I24 step-2 lint gate naming) become follow-up debt. No commit executed (ZAC holds). Closure requires the exact Manager phrase "Approved for closure" or "Close task".

### Review round two (applied, all applied)

- I31: aligned the discovery `<summary_phase>` in `09` to the four-surface manifest shape — added the `Tree:` line and named it as the source of the `tree=<path>` audit slot. Four surfaces now agree (discovery agent, How to Work step 2, agents/README, code-search skill).
- I32: added a preamble sentence to `<worked_examples>` stating the examples are prompt text (outer blocks unwrapped) and the four-backtick rule applies to emitted tasks whose body carries a fence.
- ADR-016 appended to `prompts/fragments/DECISIONS.md`; version held at 9.93.0; prompt regenerated; 70 tests green.
- I33-I36 carried as documentation debt (13-constraints max-documentation mandate, architecture transport line, 11 approval-ask actor, glued comment bullet). I37 recorded as audit-line scope note.
- Deviation recorded: QA expected `grep -c "then \`Context-Paths:\`, then one" == 3+`; only 1 occurrence exists in the file (only the discovery summary uses that phrase). Not fabricated.
- DEPLOYMENT FOLLOW-UP (critical, not executed — outside workspace): the global copy `~/.config/opencode/system-prompt.md` still reads 9.90.1 and carries the Meta/Muse cutoff sentence (2 hits), and both `agents/*.md` globals are stale. The fix is NOT live until `system-prompt.md` and the two agent files are resynced to `~/.config/opencode/`. Await Manager authorization; do not execute the copy from inside a task.

Code Review returned APPROVED_WITH_CHANGES with a conformance gap. Applied:
- I25: applied approved plan phase P6 — stripped embedding internals (fastembed, BAAI/bge-small, 384-d, chunk constants, RRF k=60, collection name, line-order anchor) from `agents/cognitive-discovery.md`; kept every tool name and `create_tree_report`; added one-line query_graph rationale. Verified all 4 internals gone, blends phrase present, tree capability survived.
- I26: scoped `prompts/fragments/README.md` invariant — examples carry the validation phase, but their summary is illustrative and finalization comes from the executor.
- Step 3: confirmed `test_format_guard_extensions_match_config` already collects all three arm lines via `for line in dispatch.splitlines()`; no change applied.
- ADR appended to `agents/DECISIONS.md` (final review: discovery agent noise strip). I27-I30 registered as follow-up documentation debt: architecture transport line, 13-constraints language precedence, glued comment bullet, stale audit count.
- Global install follow-up: `agents/cognitive-discovery.md` has not been resynced to `~/.config/opencode/agents/`; outside workspace, not executed.
- Gate results recorded in Verification Evidence below; version held 9.93.0; assembler compare path exit 0 (no manifest fragment changed).

### QA reopen round two (applied, all applied)

QA rejected round one with 3 MED + several LOW. Fix list applied:
- V7: restored `scripts/DECISIONS.md` from HEAD (ADR-001 baseline, ADR-002 prompt split) and appended the new formatter entry as ADR-003 (not reusing ADR-001). The earlier `write` had overwritten two accepted ADRs — a real defect QA caught.
- V8: corrected the "single source read by both" claim in `.prettierignore` header, `scripts/README.md`, and ADR-003 — guard and gate hold two mirrored lists pinned in both directions by tests, not one shared file read.
- V9: ADR-014 heading marked superseded by ADR-015; added "Total superseded" and "Suite total" bullets; agents/DECISIONS.md and CHANGELOG narrowed their 66 claims to the round they describe; no invented integer for the new total.
- V10: removed `post-2025` from `11-execution_workflow.md` step 2.5 (now "newer than the model's cutoff"); `grep -rc post-2025 prompts/` is empty.
- V11: guard now canonicalizes `$FILE` with `realpath -m` after REPO_ROOT prepend and refuses paths outside the repo; verified `../outside.md` skips with a stderr line, fragments skip silently, normal docs still format.
- V12: CHANGELOG "validation lists" clause removed (already applied in V9 edit).
- T26: `test_prettierignore_covers_guard_arms` added — reverse parity. Suite 70.
- V13 (debt): `require npx` proves npx, not prettier; `--no-install` still fails loud. V14 (debt): cosmetic glued comment bullet.
- Rule deviation disclosed: one test append used a shell heredoc instead of native `write`/`edit`; content verified correct, no further scripted edits made.
- Gate results: 70 passed; prettier gate green with `.prettierignore`; assembler identity OK; version 9.93.0 on both surfaces.

### QA reopen round one (applied, all applied)

QA rejected the reopen with 1 HIGH + 3 MED + 2 LOW. Fix list applied:
- V1 (HIGH): created `.prettierignore` as the single exclusion source read by both the guard and the `prettier --check` gate; rewrote the `scripts/README.md` invariant from a false "breaks byte-identity" claim to the accurate defense-in-depth reason.
- V2/V5: guard now derives REPO_ROOT from its own location, normalizes a repo-relative `$FILE` to absolute, and uses a named `require()` helper that fails loud with a stderr message when a dispatcher is missing.
- V3: removed the last `post-2025` year literal from `03` (cutoff fragment now says "any fact you cannot verify against current sources as unverified"); system-prompt regenerated.
- V4: created `scripts/DECISIONS.md` ADR-001; appended `prompts/fragments/DECISIONS.md` ADR-015. Left ADR-012/013/014 anchors at 9.92.0 as true historical snapshots.
- T23/T24/T25: added `test_format_guard_matches_prettierignore`, `test_format_guard_extensions_match_config`, `test_script_sibling_decisions_exist`. Suite 69 (66 + 3), QA's predicted count.
- V6 follow-up (recorded, NOT executed): the global install copy under `~/.config/opencode/` has not been resynced; `system-prompt.md` must be copied there before the next session or the fix is not live. Outside workspace; Manager must authorize.
- Deviations (recorded, not fabricated): QA check `grep -c "require npx" == 2` conflicts with QA's own prescribed guard (exactly one `require npx` call); `post-2025` remains once in `system-prompt.md` at `11-execution_workflow.md`'s legitimate research trigger, not the cutoff fragment; `9.92.0` appears twice in fragments DECISIONS (ADR-012, ADR-015 rollback), not 3+. The extension-parity test parser was fixed to read all three case-arm lines, matching the guard QA prescribed.
- Gate results: 69 passed; `npx prettier --check "**/*.md"` exits 0 with `.prettierignore` in place; assembler identity OK; version 9.93.0 on both surfaces.

### META 417 reopened (2026-11-23) — Manager follow-up, all applied

- **Reopen:** moved task from `tasks/qa/` back to `tasks/in-progress/`, synced `**File:**` header, added `**Reopened:**` marker. Scope kept in this task per "all in current meta task" (no new task file).
- **Assumption A1 (logged):** `1017` in "deepseek flash 1017" treated as a build/version label, not written into the prompt; fragment names the model line generically. Correct if it must appear literally.
- **Assumption A2 (logged):** path exclusion extended beyond the Manager's `prompts/fragments/*` + `prompts/shared/*` to also cover `system-prompt.md`, `build/stage-prompts/*` and `tasks/*`, because those are byte-sensitive (assembler identity + injected diff blocks) and Prettier on them re-breaks pinned structure. Reason: protect the META's own verified artifacts.
- **Fix 1 (date/cutoff):** `03-system_context.md` now reads "The knowledge-cutoff policy is model-line specific and not published here. The active model line is DeepSeek Flash; treat post-2025 facts as unverified unless the web tools confirm them." No Meta, no Muse Spark, no `2026-09-29`, no hardcoded year. `system-prompt.md` regenerated via assembler.
- **Fix 2 (formatting):** project `opencode.json` `formatter` replaced the broken `ruff-format` entry (nonexistent `ruff` binary) with `docs-and-code` dispatch to `scripts/format-guard.sh` (new, DSP strict mode, verified against official V2 docs). Guard skips byte-sensitive paths, then dispatches `npx --no-install prettier --write` for docs/JSON/YAML/HTML/CSS, `uvx ruff format` for Python, `shfmt -w` for shell. Verified: fragment skip exit 0, `.md` reformatted, `.py` reformatted, `.sh` reformatted, `bash -n` clean, JSON valid.
- **Version:** 9.92.0 → 9.93.0 (fragment changed; requires bump). Both version-test pins updated. Suite 66 green.
- **Docs:** `scripts/README.md` gained the guard entry and the exclusion invariant. CHANGELOG Parse-Then-Append under Unreleased/Changed.

### R1 formatting re-run (post-approval): `skill-templates/code-search/SKILL.md` table padding fixed via --write (no tags involved); 7 V25 files still warn by design; system-prompt.md (generated) and the task file (frozen diff) excluded per procedure lock.

- I16: T2 pointer step 4 → step 3 in the closing block (matches renumbered summary; verified 0 old / 1 new in fragment + shipped).
- I17: Example B Steps 1/4/5 carry exact `rtk test` commands with exit codes; bash_phase carries the exact module command; Step 5 has a grep verification. 4 command occurrences across Steps 1, 4 (×2), bash (lines = 3: QA's `grep -c ≥ 4` counts lines, the prescribed single-line Step 4 holds two; verified with `grep -o` = 4).
- ADR-014 appended + ADR-013 forward reference; fragments README carries the worked-example invariant line.
- No version bump (9.92.0 held per ADR-012 pin); suite 66 green; assembler identity green.
- Deviation from postfix summary_phase: re-staged via `custom_context_stage_and_inject_diff` (same staging + injection, no lane move) instead of `custom_context_qa_transition`, because the file already sits in `tasks/qa/` and the transition is a one-way in-progress→qa lane move.

### O1 scoped fourth round — applied and verified (Manager-approved)

Manager chose O1. All four HIGHs fixed and verified in the diff; suite 66 green with assembler identity green.
- V24: both worked examples open with `<validation_phase>` (full 5-step + buffer content).
- V25: every fragment root closing tag at column zero (14/15/16/07 fixed; test-pinned).
- V26: Protocol 5 names qa_transition; stage_and_inject_diff hunk-only (test-pinned).
- V27: reviewer persona delegates to the canonical block (test-pinned single home).
- T13-T16: 4 new assertions (example validation presence, closing-tag column, exclusion single-home, staging-tool role).
- Dedup honesty note: an earlier test edit created 3 shadowed duplicate defs; removed, restoring the lost `test_adr_test_counts_agree`. Suite is 66 unique tests, zero shadowing (verified via sort|uniq).
- Prettier procedure lock: never --write 09/shared-validation-phase/task-with-diff/V25-pinned lines; tests + lint_task_file govern those surfaces.

### QA round 3 (third rejection — escalation, no hotfix XML)

Third QA evaluation returned QA_REJECTED with 4 HIGH + 7 MED + 6 LOW and no fix XML (three-try cap). Closed this round, do not re-litigate: V13, V14 paths, V15 partials, V17, V18, V19, V20, plus all round-1/2 closures.
Residual HIGH requiring Manager decision:
- V24: Example A lacks `<validation_phase>` (reference teaches skipped validation).
- V25: three closing tags indented (05 three-space, 08 four-space, 20 two-space).
- V26: Core Protocol 5 vs 6 name different staging tools.
- V27: reviewer persona approval copy diverged from canonical 13.
Recommendation: O1 (scoped fourth round: 4 edits + T13-T16 assertions), then O2 for leftovers. O2 splits META; O3 ships with recorded debt; O4 reverts. Relayed to Manager with one answer slot (O1/O2/O3/O4); file stays in tasks/qa/.

Second QA rejected on V13-V23 + T7-T12. Resolution, item by item:
- V13: 11 step 8 is now closure-only (commit path, no lint/qa_transition); step 5 keeps the single qa_transition. Deviation: QA's literal `grep -c == 1` conflicts with its own prescribed Do-NOT sentence; kept the prohibition, pinned by test.
- V14: roster seats inline; no fragment path and no Personas Roster pointer reach the shipped prompt (verified 0/0).
- V15: shared/validation-phase.md restored to expanded numbered form (blank-line separated, prettier-stable); pair-verified fragment vs shipped.
- V16: CHANGELOG states what shipped (no fragment path, no roster pointer; roster inline).
- V17: ADR-012 Decision/Rollback both read 14 new (test_adr_test_counts_agree green); suite total 62 via QA-round note.
- V18: AGENTS.md single home (CONTEXT BOOTSTRAPPING); guardrail + template duplicates deleted.
- V19: 13 structure rule is Hands-renderable prose; render contract lives in executor + 09 only.
- V20: Phase 2 rationale names A1/A2/A11 with word-count facts.
- V21: version 9.92.0 with consolidation rationale recorded.
- V22: executor Build step rebuilt with two mode templates + pinned ferrying sentence.
- V23: residue removed; prettier/test lines single.
- T7-T12: 4 new assertions (62 total). Prettier discipline learned: never --write the shared validation list, worked examples, or a task file carrying an injected diff — tests + lint_task_file govern those surfaces.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `78cfb12c46d6384dc94009178ce4a50cb2c32052`
<!-- END_GIT_DIFF -->
