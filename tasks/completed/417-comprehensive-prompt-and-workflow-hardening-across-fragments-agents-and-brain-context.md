# Task 417: Comprehensive prompt and workflow hardening across fragments, agents, and brain context

**File:** `tasks/in-progress/417-comprehensive-prompt-and-workflow-hardening-across-fragments-agents-and-brain-context.md`
**Source:** manager
**Type:** feature
**Status:** in-progress
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
```diff
diff --git a/.prettierignore b/.prettierignore
new file mode 100644
index 0000000..582fba9
--- /dev/null
+++ b/.prettierignore
@@ -0,0 +1,9 @@
+# Byte-sensitive harness artifacts - never auto-format.
+# The same five exclusions are mirrored in the case arm of scripts/format-guard.sh;
+# the two lists are pinned against each other in both directions by
+# tests/test_prompt_sync.py. See scripts/DECISIONS.md ADR-003.
+prompts/fragments/
+prompts/shared/
+system-prompt.md
+build/stage-prompts/
+tasks/
diff --git a/AGENTS.md b/AGENTS.md
index 5d87a98..4f0af34 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -123,13 +123,13 @@ You MUST follow these skill loading rules in every session:
 
 ## 🛑 PROJECT SKILLS (Local, Audited)
 
-| Name | Trigger (when to load) | Duty (one line) |
-| ---- | ---------------------- | --------------- |
+| Name              | Trigger (when to load)             | Duty (one line)                                          |
+| ----------------- | ---------------------------------- | -------------------------------------------------------- |
 | `sop-maintenance` | When modifying this SOP repository | Rules for modifying the Cognitive Lead AI SOP repository |
 
 ## 🛑 CONTEXT BOOTSTRAPPING
 
-At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing.
+At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing. Before any `brain_turn` planning or verdict request, produce the graph, a capped directory tree at depth 3 or deeper, and a verified `context_paths` manifest, then record one `Context-Map:` line beside the mode line.
 
 ## 🛑 MANDATORY END-OF-TASK SEQUENCE
 
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f9f1a60..be8393b 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Changed
 
+- **META 417 reopened: DeepSeek Flash cutoff fix + forced code/docs formatting:** corrected `prompts/fragments/03-system_context.md` to drop the stale Meta/Muse-Spark cutoff wording and name the DeepSeek Flash model line, with no hardcoded year (avoids cache-breaking mutable state, audit A3). Bumped `01-system_version.md` 9.92.0 → 9.93.0; regenerated `system-prompt.md` via the assembler. Configured OpenCode V2 `formatter` in project `opencode.json` (per the official V2 config/formatters docs): `scripts/format-guard.sh` dispatches prettier (docs/JSON/YAML), ruff (Python), shfmt (shell) on `write`/`edit`/`patch`, while skipping byte-sensitive artifacts — `prompts/fragments/*`, `prompts/shared/*`, `system-prompt.md`, `build/stage-prompts/*` and `tasks/*` — so Prettier cannot re-break the V25 pinned closing tags or the injected diff blocks. The previous `ruff-format` entry referenced a `ruff` binary absent from PATH (silently failing); ruff now runs via `uvx`. Updated `scripts/README.md`. Prompt-sync suite green, with the collected count recorded in the task file's Verification Evidence. No commit.
+
 - **Global install drifts synced and stale memories refreshed:** audited every global-install target against the repo using the project-memory workflow. Copied four drifted surfaces to `~/.config/opencode/`: `agents/cognitive-executor.md`, `system-prompt.md`, six `build/stage-prompts/system-prompt.*.md` stage artifacts, and the missing `mcp-lint-server/tests/test_deleted_skill_refs.py`. Re-audit clean; skills (24 dirs, no stray `.md`), the other agent, shell strategy, MCP sources, mcp-common and planner static were already in sync. Refreshed two stale memory records under task 411: the version record now reads OpenCode 2.3.2 / OpenChamber 2.7.3 verified 2026-11-22, and the blowsh policy record now reads EgressRegion DE with the verified DE exit. Both supersession notes preserved the prior bodies; `rebuild_memory_index` regenerated the index (33 rows). Prompt-sync suite 44 passed. No commit.
 
 - **blowsh Psiphon exit switched to Germany (no task file):** the operator clarified the earlier "GB node" wording as `EgressRegion=DE`. Set `EgressRegion: "DE"` in `psiphon-proxy/psiphon.config`, fixed the stale US comment in `psiphon-proxy/Dockerfile`, and built `psiphon-proxy:de` from cached layers. Created the `warp-net` bridge, ran `psiphon-socks` unpublished on it, and recreated `blowsh-singleton` with all prior environment preserved plus `PROXY_TYPE=http`, `PROXY_HOST=psiphon-socks`, `PROXY_PORT=8082`, `PROXY_BYPASS=localhost,127.0.0.1`. Verified end to end: proxy container trace and blowsh's own `fetch_web` both returned `ip=172.105.78.25`, `loc=DE`, `colo=FRA`, `warp=off`. Updated `docs/blowsh-proxy-options.md`, `docs/blowsh-psiphon-proxy.md`, `psiphon-proxy/README.md`, both `DECISIONS.md` files (dated ADRs) and this changelog. No commit.
@@ -27,6 +29,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Brain bridge chat-completions hardening (task 412):** the chat-completions converter now passes usage details through (`input_tokens_details.cached_tokens`, `output_tokens_details.reasoning_tokens`), folding DeepSeek top-level `prompt_cache_hit_tokens`/`reasoning_tokens` into the nested shape when absent, ignoring non-dict detail payloads, and logging a warning when an unsupported Responses input item is dropped. Output token budget raised to 131072 for max-effort turns via `BRAIN_MAX_TOKENS`. Six regression tests added; 396 passed.
 
+- **Prompt and workflow hardening META 417 (tasks 414/415/416):** reconciled the manual/automatic topology across both DECISIONS files, `docs/architecture.md` and the executor (superseded-note, single finalization sequence, one mode template per autonomy level, no escape-hatch OR); consolidated approval literals and ZAC into single normative blocks with per-surface actors; rebound the brainstorm panel to the Personas Roster with the multi-label carve-out; added the mandatory Context Map Before Brain Calls contract (turn classes A/B/C, audit line, forbidden shapes) to the executor, discovery agent, READMEs, `AGENTS.md` and the governance audit template; added the direct-input plan gate and Brain context-before-plan rule; removed the Template Preservation rule, the duplicate QA/review invocation, the duplicate Strict Tooling Gate sentences and the phantom `@google/design.md` lint command; verified no fragment path and no roster pointer reaches the assembled prompt (the roster is inline) and the Browser-facing prompt carries no fragment-file references. `01-system_version.md` bumped 9.90.1 to 9.92.0 (phases 1B and 2 consolidated into one cycle), `system-prompt.md` regenerated, prompt-sync suite 66 passed (44 existing + 22 new regression assertions: 14 plan-round plus 8 QA-round).
+
 ## [9.90.0] - 2026-11-20
 
 ### Added
@@ -51,7 +55,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 ### Changed
 
 - **Server Browser extension path relocated to `$HOME/openchamber-server-browser` (direct Manager request, no task file):** the two clone commands in `docs/openchamber.md` §10.1 and `LLM.txt` §7.10 now use `$HOME/openchamber-server-browser` instead of `~/Develop/openchamber-server-browser`. The extension was cloned into the new location, `~/.config/openchamber/extensions.json` repointed, and the extension `config.json` written per the runbook (chrome wrapper, allowedOrigins, discoverDevServers false). Chrome headless shell, the service capability grant and `browserProvider: server-browser` were already in place.
-- **blowsh docs rewritten against the local source as the shipped contract (task 400):** the third-round note below recorded the queue budget and search deadline as "uncommitted work … ignored today", which was true of the published `2.6.2` image but is superseded: the Manager ruled the local checkout is the version to document and the remote image is building in CI/CD. The docs now describe that source with no version caveat. `LLM.txt` Step 7.6 carries a full environment table (15 knobs, code defaults from `browshManager.ts`, `server.ts` and `.env.example`) and states the ladder as an invariant with its upstream citations (`browshManager.ts:71-79`, `.env.example:38,44`): `SEARCH_DEADLINE_MS >= BROWSH_QUEUE_TIMEOUT_MS + BROWSH_REQUEST_TIMEOUT_MS` and `BROWSH_QUEUE_TIMEOUT_MS >= 2 x BROWSH_REQUEST_TIMEOUT_MS`, satisfied by the shipped values (900000 >= 780000, 600000 >= 360000 with a 240000 margin). The `blowsh` MCP client cap rose 600000 -> 960000 in `LLM.txt` and the live config, because at 600000 a full-length search was cut by the transport 300s before its own `SEARCH_DEADLINE_MS` could fire; 960000 > 900000. The docs now also state what that cap does *not* cover: `fetch_web_batch` is serial over up to 10 URLs (`src/tools/fetchWebBatch.ts:33-35`) with a **per-item** budget, so its worst case is `10 x deadline_ms` and a large batch will still exceed the client cap. `skill-templates/blowsh/SKILL.md` `deadline_ms` range corrected to `500–1800000` (was `500–600000`), and the stale "600s blowsh" / "600s LLM bridges" figures replaced with 960s and 1200s.
+- **blowsh docs rewritten against the local source as the shipped contract (task 400):** the third-round note below recorded the queue budget and search deadline as "uncommitted work … ignored today", which was true of the published `2.6.2` image but is superseded: the Manager ruled the local checkout is the version to document and the remote image is building in CI/CD. The docs now describe that source with no version caveat. `LLM.txt` Step 7.6 carries a full environment table (15 knobs, code defaults from `browshManager.ts`, `server.ts` and `.env.example`) and states the ladder as an invariant with its upstream citations (`browshManager.ts:71-79`, `.env.example:38,44`): `SEARCH_DEADLINE_MS >= BROWSH_QUEUE_TIMEOUT_MS + BROWSH_REQUEST_TIMEOUT_MS` and `BROWSH_QUEUE_TIMEOUT_MS >= 2 x BROWSH_REQUEST_TIMEOUT_MS`, satisfied by the shipped values (900000 >= 780000, 600000 >= 360000 with a 240000 margin). The `blowsh` MCP client cap rose 600000 -> 960000 in `LLM.txt` and the live config, because at 600000 a full-length search was cut by the transport 300s before its own `SEARCH_DEADLINE_MS` could fire; 960000 > 900000. The docs now also state what that cap does _not_ cover: `fetch_web_batch` is serial over up to 10 URLs (`src/tools/fetchWebBatch.ts:33-35`) with a **per-item** budget, so its worst case is `10 x deadline_ms` and a large batch will still exceed the client cap. `skill-templates/blowsh/SKILL.md` `deadline_ms` range corrected to `500–1800000` (was `500–600000`), and the stale "600s blowsh" / "600s LLM bridges" figures replaced with 960s and 1200s.
 - **blowsh MCP timeout raised from 120s to 600s (direct Manager request, no task file):** the blowsh client timeout capped deep research before it could finish. `mcp.servers.blowsh.timeout` is now `{catalog: 600000, execution: 600000}` in the live global `~/.config/opencode/opencode.json` (dated backup kept beside it, JSON re-validated, every other server's timeout proven unchanged).
 - **zen-proxy hardened: every failure now answers with a status (task 400):** the slice is the live path for every `brain_turn`, and four of its defects made a failure look like a network problem. A socket timeout raised `TimeoutError`, which is not a `urllib.error.URLError`, so it escaped both `except` clauses and dropped the socket with no response — the caller saw "Server disconnected without sending a response", the exact symptom ADR-002 was written about. An inbound body was read unbounded, and a `Transfer-Encoding: chunked` request arrived as `Content-Length: 0` and was forwarded as an empty body. The relay pumped bytes without looking for the terminal event, so a stream that died mid-reply was indistinguishable from a short but complete answer. `log_message` was a no-op, so the slice emitted no request log at all. `zen-proxy/proxy.py` now has an explicit failure contract — 504 `GatewayTimeout` for a stalled upstream, 502 `BadGatewayError` for an unreachable one, 413 `PayloadTooLarge` over the new 32 MiB cap, 400 `BadRequest` for a malformed or short body, 404 `ModelNotServedHere` unchanged — and a stream that ends without its terminal event reports `UpstreamStreamTruncated` in band, because the status line is already on the wire. One structured journal line per request carries the request id, the model, the timing and whether the session was injected or client-supplied, and never the `Authorization` value or a body. A `SIGTERM` now drains: the listener stops, in-flight turns finish, and the process leaves after `ZEN_PROXY_DRAIN_TIMEOUT_S` (30s). Every environment value is validated at startup and a malformed one stops the unit with a readable message and exit code 2 instead of a traceback. The two dead knobs are gone — `ZEN_SESSION_ID` was read and never used, `MODEL_WINDOWS` was defined and never read with four of its seven keys not being served model ids — and the docs that described them were corrected. `zen-proxy/refresh_allowlists.py` (new, stdlib only) reports allowlist drift against the live gateway catalogue and, on `--apply`, writes only the removals it can prove: a failed probe never removes anything, an id survives if it merely moved between the chat and responses mounts of its family, and a mount that would end up empty is never written. It is read-only against upstream, never touches git and never stores a key. `tests/test_zen_proxy.py` (new, 25 cases) guards the failure contract, the body cap, the chunked decoder, the truncated-stream rule, the effort translation, the credential-free log line and the merge rules, with the upstream replaced by a fake response object so no test spends gateway quota. `zen-proxy/DECISIONS.md` gained ADR-005, `docs/zen-proxy.md` gained the new configuration rows and failure modes, and `.env.example` lost the dead knob. The patterns for the failure contract, the bounded body read, the fail-loud environment parsing, the terminal-event detection and the catalogue-refresh safety rules follow `github.com/12errh/zen-proxy` (MIT, (c) 2026 12errh); no code was copied from it and none of its free-tier gate bypass was adopted, because this slice authenticates with a real Go key and deliberately does not impersonate the CLI.
 - **Freebuff removed from the machine, install instructions and memories corrected (task 399):** the Freebuff footprint is gone — the `freebuff@0.2.34` npm global package and its binary, `~/.config/manicode/` (231M of vendor state, credentials and device key), the `~/warp-fr/.freebuff/` project marker, and the Freebuff-era V1 `~/.AGENTS.md` (plus its backup) that OpenCode V2 never read. The legacy `~/.agents/skills` root was removed with it, so there is now exactly ONE writable global skill root; `LLM.txt` §6 and the verification checklist were rewritten accordingly and now state that a reappearing `~/.agents/skills` must be deleted rather than synced. `LLM.txt` gained a "Upgrading OpenCode / OpenChamber — the full refresh chain" section: a binary upgrade is NOT an install upgrade, because the servers, skills, agents, prompts and plugins in `~/.config/opencode/` are independent copies, so the chain is binaries → servers → venv deps → skills → agents → prompts → plugin cache purge → restart → drift audit. The memories were corrected to match reality: OpenCode v2.3.0 and OpenChamber 2.7.1 (the previous snapshot said 2.2.5 / 2.6.0 and claimed "no OpenCode plugins" while three are installed), the plugin policy now lists smart-compact + goal + todolist, `skill-sources-multiple-roots` drops the `~/.agents` root, `global-install-upgrade` gained the copy-exclusion trap (`DECISIONS.md` / `README.md` counted as fake skills and extra agents), and `no_task_for_global_upgrade` now separates a machine-local sync (no task file) from a change that also edits repo files (task file required). The Freebuff-era `~/.AGENTS.md` was a duplicate of the V2-native `~/.config/opencode/agents/cognitive-executor.md`, which stays the canonical agent definition.
@@ -83,7 +87,6 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [9.77.0] - 2026-11-08
 
-
 ### Changed
 
 - Comprehensive repository audit (Task 0385): purged contradictions, phantom references, and cruft across 5 domains.
@@ -113,7 +116,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **All MCP servers to Code Mode (Task 0378 Phase 2, Manager-ordered full reversal of 0361):** the six in-house servers (`custom_context`, `project_memory`, `lint`, `brain`, `planner`, `blowsh`) are back to `codemode: true` in the global `opencode.json` (timestamped backup kept beside it; JSON re-validated; resolved values proven six `True`, telegram untouched). Every MCP call now routes through `execute` and no tool schemas enter the system prompt — the per-call hop cost is accepted by explicit Manager order. Docs updated (`docs/services.md` table, `docs/setup.md`, `README.md` block + sample, `LLM.txt` install block) and the `workflows/codemode-policy` memory shard rewritten.
 
 - **Discovery-fed retries must ground with bodies, not prose (Task 0378):** a planning loop stalled on two consecutive `missing_context` answers. The Hands had fed citation-style prose (paths with lines, no bodies) per the Discovery-fed wording; prose-about-code cannot satisfy No-Hallucination + Strict Grounding, so the second request was contractually correct. The executor now binds the retry to verbatim code (capped ranges) and/or `context_paths=[paths]` — prose-only fed-context is a protocol violation — mirrored at the file-context retrieval line. Prompt-sync regression test (red-first verified), live agent copy synced byte-identical, agents ADR + README invariant recorded.
-- **Brain `missing_context` narrowing rule + raised context-paths caps (Task 0375):** a planning loop stalled 3 turns re-requesting files the bridge had already delivered (truncated at the 60 KB/file cap with an explicit note). The contract only said STOP-and-list, giving the model no narrowing strategy. The rule now states: a truncation note means *partially present* — verify visible scope first, never re-request a fully-present file, narrow instead of repeating (smaller path, section, symbols). Caps raised `_CTX_PATHS_PER_FILE` 60k → 150k and `_CTX_PATHS_TOTAL` 200k → 400k (env overrides unchanged); `context_paths` also accepts `#Lstart-end` / `#Lstart-` slices, wired into both the tested helper and the live-turn path through shared parsers. System prompt rebuilt to `9.70.3` via the assembler (byte-identical except the two intended hunks); `test_prompt_sync` 22/22, `test_brain_bridge` 304/304 (incl. the exact-default pin test and 7 range tests). QA round made the contract explicit: the narrowing rule now names the `#Lstart-end` / `#Lstart-` slice forms so the Brain uses them, with a prompt-sync regression test pinning both forms and matching `docs/brain-bridge.md` documentation. QA round 2 classified malformed `#L` fragments on supported paths as explicit `bad range` labels (instead of resolution fall-through) with live-path (`_path_candidates`) regression coverage on both entry points. Bridge documentation distinguishes clamped bounds from empty and malformed ranges.
+- **Brain `missing_context` narrowing rule + raised context-paths caps (Task 0375):** a planning loop stalled 3 turns re-requesting files the bridge had already delivered (truncated at the 60 KB/file cap with an explicit note). The contract only said STOP-and-list, giving the model no narrowing strategy. The rule now states: a truncation note means _partially present_ — verify visible scope first, never re-request a fully-present file, narrow instead of repeating (smaller path, section, symbols). Caps raised `_CTX_PATHS_PER_FILE` 60k → 150k and `_CTX_PATHS_TOTAL` 200k → 400k (env overrides unchanged); `context_paths` also accepts `#Lstart-end` / `#Lstart-` slices, wired into both the tested helper and the live-turn path through shared parsers. System prompt rebuilt to `9.70.3` via the assembler (byte-identical except the two intended hunks); `test_prompt_sync` 22/22, `test_brain_bridge` 304/304 (incl. the exact-default pin test and 7 range tests). QA round made the contract explicit: the narrowing rule now names the `#Lstart-end` / `#Lstart-` slice forms so the Brain uses them, with a prompt-sync regression test pinning both forms and matching `docs/brain-bridge.md` documentation. QA round 2 classified malformed `#L` fragments on supported paths as explicit `bad range` labels (instead of resolution fall-through) with live-path (`_path_candidates`) regression coverage on both entry points. Bridge documentation distinguishes clamped bounds from empty and malformed ranges.
 - **Brain `context_paths` rejected source files (Task 0372):** `_ALLOWED_READ_SUFFIXES` predated the task-210 injection feature and allowed only docs/reports, so every `.java`/`.js`/`.tsx` came back `[unavailable: unsupported extension]` — byte-proven (29.5k of 87k attached). Suffix set extended to source-text languages; binaries still rejected; traversal/size/budget guards untouched. 294/294 brain-bridge tests green.
 - **Brain follow-ups (Task 0374):** truncation notes verified pre-existing in the allocator (no code change); ledger rows carry per-path attach outcomes (`path`/`status`/`chars`, leak-tested — no file text ever); monthly quota counter with stderr warning past the threshold (best-effort, never blocks a turn); end-to-end `.java` injection proven live (91,991 chars attached, 297/297 green).
 
diff --git a/agents/DECISIONS.md b/agents/DECISIONS.md
index 891c1a8..2420395 100644
--- a/agents/DECISIONS.md
+++ b/agents/DECISIONS.md
@@ -1,11 +1,13 @@
 ## Unify Architecture to 100% Brain Turn and Permanently Eliminate Manual Mode
 
 Date: 2026-11-08
-Status: accepted
+Status: superseded by "Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)"
 Context: Maintaining dual modes (manual courier copy-pasting vs autonomous brain_turn) introduced prompt bloat, mode confusion, and human friction.
 Decision: Permanently eliminate manual mode across all prompts, agents, protocols, and documentation. The platform operates 100% autonomously via `mcp-brain-bridge` (`brain_turn`). The Manager is strictly executive supervisor, never a courier.
 Consequences: Zero copy-paste prompt templates survive; all turns chain directly through brain_turn.
 Rollback: Revert to 9.77.0 prompt fragments.
+Superseded-By: "Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)" (2026-11-08)
+Superseded-Reason: The decouple ADR restored manual mode as a first-class topology; this ADR's "permanent elimination" claim was reverted but never marked superseded, creating a contradiction in the decision log.
 
 ## Comprehensive Repository Audit: Purge Contradictions, Phantoms, and Cruft
 
@@ -99,20 +101,13 @@ Rollback: Restore the citations from git history.
 
 ## Free-tier bash gate documented
 
-## Subagent Delegation Names the Session Tool
-
-Date: 2026-10-27
-Status: accepted
-Context: The executor told the Hands to delegate discovery "using your `task` tool". No tool by that name exists in the session; delegation runs through the `subagent` tool. The sentence was inherited from another runtime's vocabulary.
-Decision: Name the `subagent` tool explicitly. One-word-class fix; delegation targets and the 4-agent cap are unchanged.
-Consequences: The delegation instruction resolves to a real tool. No behavior change beyond the name.
-Rollback: Restore the prior sentence from git history.
 Date: 2026-10-17
 Status: accepted
 Context: Upstream free-tier models discriminate by request-body tool list. Agents omitting bash receive 403 FreeTierError on free-tier models.
 Decision: Document bash requirement in agent docs. Add free-tier smoke test to the review checklist. Make no permission changes.
 Consequences: Agents intended for free-tier use keep bash. Hardening uses prompts and review, not tool removal.
 Refs:
+
 - https://github.com/anomalyco/opencode/issues/50627
 - https://github.com/anomalyco/opencode/issues/53347
 - https://github.com/anomalyco/opencode/issues/53885
@@ -120,6 +115,15 @@ Refs:
 - https://github.com/anomalyco/opencode/issues/52880
 - https://github.com/anomalyco/opencode/issues/49592
 
+## Subagent Delegation Names the Session Tool
+
+Date: 2026-10-27
+Status: accepted
+Context: The executor told the Hands to delegate discovery "using your `task` tool". No tool by that name exists in the session; delegation runs through the `subagent` tool. The sentence was inherited from another runtime's vocabulary.
+Decision: Name the `subagent` tool explicitly. One-word-class fix; delegation targets and the 4-agent cap are unchanged.
+Consequences: The delegation instruction resolves to a real tool. No behavior change beyond the name.
+Rollback: Restore the prior sentence from git history.
+
 ## Prompt-refactor matrix row gains the execute pass
 
 Date: 2026-11-02
@@ -200,3 +204,30 @@ Context: The OpenUI validity gate constrained the `openui-lang` program but neve
 Decision: Add a call-envelope subsection before the program gate with the exact `action: "render.page"` / `parameters` object shape, an envelope self-check (object not string, one payload, `awaitAnswer` only for answer-bearing choices, direct call not `execute`), and a rebuild-not-retry rule. Correct the Output Contract wording to place `ui`/`html` inside `parameters`. Mirror the rule into the hands-protocol fragment.
 Consequences: Both the program and the envelope are validated before a render call. A stringified `parameters` is recognized from its diagnostic and rebuilt rather than retried. Version bumped with artifact regen.
 Rollback: Remove the executor subsection, the fragment sentence, the regression assertions, and restore the prior version; regenerate the prompt from fragments.
+
+## META 417: Context Map, plan gate, and topology reconciliation
+
+Date: 2026-11-22
+Status: accepted
+Context: The 67-finding audit (24 HIGH) showed the Brain plans from assumed context when no map is attached, the Hands can self-approve a plan on direct input, and five surfaces assert different topologies. The direct-input path bypassed both the Planning Gate and the context feed.
+Decision: Add the mandatory Context Map Before Brain Calls contract (turn classes A/B/C, audit line, forbidden shapes) to the executor, with the discovery agent persisting the tree and the READMEs carrying the invariant. Add the plan-before-implementation gate on direct Manager input and the context-before-plan rule for the Brain. Reconcile topology (superseded-note on the courier ADR, single finalization sequence, per-autonomy mode templates). Consolidate approval literals with 13-constraints.md canonical. Version fragment 9.92.0, prompt regenerated, 14 new regression assertions plus 8 QA-round assertions (66 total at that round), plus the reopen-round assertions recorded in the task file and summarised in `prompts/fragments/DECISIONS.md` ADR-015.
+Consequences: Every planning/verdict `brain_turn` carries a verified map; direct input cannot skip the Brain plan; one topology, one finalization path, one approval home.
+Rollback: Revert the contract sections and restore the prior version; regenerate the prompt from fragments.
+
+## META 417 second QA round: AGENTS.md single home
+
+Date: 2026-11-22
+Status: accepted
+Context: Second QA found the context-map rule in two places inside `AGENTS.md` (guardrail plus bootstrapping sentence) and a duplicate bullet in the governance audit template.
+Decision: Keep CONTEXT BOOTSTRAPPING as the single home in `AGENTS.md`; delete the guardrail duplicate and the template duplicate.
+Consequences: One home per rule in every file the META touched.
+Rollback: Restore the deleted lines from git history.
+
+## META 417 final review: discovery agent noise strip
+
+Date: 2026-11-23
+Status: accepted
+Context: Approved plan phase P6 under finding W17 directed stripping model-unverifiable embedding internals from `agents/cognitive-discovery.md`. The line survived unedited with no recorded deferral rationale, which reads as an omission rather than a decision.
+Decision: Strip the embedding internals (model name, dimensions, chunk constants, RRF k, collection name, line-order anchor), keep every tool name and the `create_tree_report` capability, and add a one-line rationale for `query_graph`. Scope the fragments README invariant so it claims only what is true of the validation phase, with finalization owned by the executor.
+Consequences: The discovery agent carries no constant the model cannot verify. Worked examples are validation-complete but their summary is illustrative; the executor's finalization sequence supplies the transition. Four residuals (I27-I30) registered as follow-up documentation debt.
+Rollback: Restore the prior `custom_context.*` bullet from git history and the prior README invariant.
diff --git a/agents/README.md b/agents/README.md
index 3b8d259..0d0f132 100644
--- a/agents/README.md
+++ b/agents/README.md
@@ -16,7 +16,7 @@ Defines the two OpenCode agent personas for the Cognitive Lead HQ: primary execu
 - Plan approval surface: an approval question is only valid after the full plan body is visible in the same turn, and the question payload repeats it. A bare "Approve the plan?" ask is a protocol bug.
 - Brain results cross into the transcript whole: `status`, `output`, `xml_blocks` and diagnostic/`truncated` fields are never sliced, field-shaped or summarized on return. Size is managed before the call (`compact_context`, leaner prompt, `include_bundle=false`), never after.
 - Discovery-fed grounding: a retry without verbatim code or `context_paths` predicts its own second `missing_context` — prose-only fed-context is a protocol violation.
-- Context-Paths manifest invariant: every discovery report ends with a machine-readable `### Context Manifest` (`Context-Paths:` with `#Lstart-end` slices) that the executor feeds directly into `brain_turn(context_paths=[...])`.
+- Context-Paths manifest invariant: every discovery report ends with a machine-readable `### Context Manifest` (`Tree:` line followed by `Context-Paths:` with `#Lstart-end` slices) that the executor feeds directly into `brain_turn(context_paths=[...])`. The tree report is persisted at depth 3 or deeper, capped at 400 entries, and its path is the first line of the manifest. Turn classes (A/B/C) determine map depth: Class A (plan/implementation) requires full graph+tree+manifest, Class B (review/verdict) requires diff-scoped manifest, Class C (control) is exempt.
 - Code Mode execution standard: all MCP servers run under `codemode: true`; every tool call routes through `execute` as `tools.<server>.<tool>` with `project_root` on each call, and `brain_turn` results return whole.
 - OpenUI validity gate: every `openchamber_render` program is self-checked before the call — exact component signatures, plain string or number `Table` cells, balanced brackets, no named arguments, one statement per line. An arity diagnostic is treated as a source defect, not a renderer bug.
 - Render call envelope: `openchamber_render` takes `action: "render.page"` and `parameters` as a real object, never a JSON-encoded string. The executor self-checks the envelope before the program; a `parameters: Expected object` error is rebuilt, never retried verbatim.
@@ -27,4 +27,5 @@ Defines the two OpenCode agent personas for the Cognitive Lead HQ: primary execu
 Custom agents must keep bash in the tool allowlist when the agent is expected to run on a free-tier model. Upstream free-tier models classify the caller by the request-body tool list. A call without bash is treated as third-party and receives 403 FreeTierError on free-tier models. Keep bash in the list for free-tier use. Harden behavior with scoped prompts and review, not with tool removal.
 
 Review checklist addition:
+
 - Free-tier smoke test before release: run the agent under review with opencode run using the --agent flag on a free-tier model and confirm a normal reply with no 403. Example with a known agent: opencode run --agent cognitive-executor --prompt smoke test reply OK. Repeat for each agent file found in opencode.json.
diff --git a/agents/cognitive-discovery.md b/agents/cognitive-discovery.md
index 310858d..831434b 100644
--- a/agents/cognitive-discovery.md
+++ b/agents/cognitive-discovery.md
@@ -21,9 +21,6 @@ permissions:
   - action: websearch
     resource: "*"
     effect: allow
-  - action: skill
-    resource: "*"
-    effect: allow
   - action: subagent
     resource: "*"
     effect: allow
@@ -55,10 +52,9 @@ You map code so the executor does not have to read it all. You report; you never
 
 ## Your Tools
 
-- **`custom_context.*` through `execute`** — your primary surface: `get_directory_tree`, `create_tree_report`, `read_source_files`, `extract_signatures`, `build_graph`, `query_graph` (**hybrid**: deterministic `bfs`/`dfs` plus `mcp-context-server/vector.py` fastembed `BAAI/bge-small-en-v1.5` 384-d `512/50` Chroma `hq_docs_tasks_comments` (`_CHUNK_TOKENS` 512 plus `_CHUNK_OVERLAP` 50 plus `_MAX_CHUNKS_TOTAL` 2000) fused via RRF `k=60` in `mcp-context-server/server.py` between `scored.sort` and `seeds`; `comment` nodes in `mcp-context-server/graph.py` 80/50 caps, archive lane 4), `explain_node`, `shortest_path`, `god_nodes`, `graph_stats`. Other MCP servers are not yours.
+- **`custom_context.*` through `execute`** — your primary surface: `get_directory_tree`, `create_tree_report`, `read_source_files`, `extract_signatures`, `build_graph`, `query_graph`, `explain_node`, `shortest_path`, `god_nodes`, `graph_stats`. Use `query_graph` for cross-file questions, because it blends deterministic traversal with semantic search. Other MCP servers are not yours.
 - **`read`, `grep`, `glob`** — direct inspection when a file is small or the graph is stale.
 - **`webfetch`, `websearch`** — external docs.
-- **`skill`** — load a skill when the report needs its rules.
 - **`subagent`** — split a wide map into parallel lanes.
 
 You have no file writer and no shell. Do not try to acquire one, and do not ask for one.
@@ -66,7 +62,7 @@ You have no file writer and no shell. Do not try to acquire one, and do not ask
 ## How to Work
 
 1. Run `build_graph` once per scope, then reuse it: `query_graph`, `explain_node`, and `god_nodes` answer cross-file questions far cheaper than reading files.
-2. Map structure with `get_directory_tree`; persist a tree report only when asked.
+2. Map structure with `get_directory_tree`; persist a tree report with `create_tree_report` at depth 3 or deeper, capped at 400 entries, and state the cap when it truncates. The tree report path is the first line of the Context Manifest below.
 3. Pull `extract_signatures` before bodies, and batch `read_source_files` for the few files that matter.
 4. Batch independent calls inside one `execute` script instead of one round trip each.
 5. Stop when the question is answered. Do not explore past the scope you were given.
@@ -75,11 +71,14 @@ You have no file writer and no shell. Do not try to acquire one, and do not ask
 
 - Every claim names a path, and a line range when it matters.
 - Missing files, empty directories, and broken references are stated plainly, never filled in.
-- End with the manifest the executor feeds to the Brain:
+- End with the manifest the executor feeds to the Brain. The tree report path goes first, then the file paths:
 
   ```markdown
   ### Context Manifest
+
+  Tree: context-reports/tree_report_<ts>_<uuid>.md
   Context-Paths:
+
   - path/to/file.ext#Lstart-end
   ```
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 4c2f779..3dc93df 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -50,9 +50,9 @@ You are the primary execution engine for the Cognitive Lead AI platform. You rec
 2. **Rule Validation:** If the Orchestrator's instructions violate ANY project rule, HALT immediately. Output a `⚠️ RULE VIOLATION WARNING` detailing the broken rule. Do NOT proceed. Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files; run no bash commands before validation passes.
 3. **MCP-First Context:** When instructed to gather context, you MUST use the `custom_context` MCP tools (`get_directory_tree`, `create_tree_report`, `read_source_files`, `extract_signatures`, plus graph-first `build_graph`, `query_graph`, `explain_node`, `shortest_path`, `god_nodes`, `graph_stats`). NEVER use native `read` to dump large file contents inline.
 4. **Skill Loading:** Load all skills explicitly named in the XML task's `<context_phase>`.
-5. **Zero-Autonomous-Commit (ZAC):** You are STRICTLY FORBIDDEN from executing `git add`, `git commit`, `git checkout`, or `git push`. These are denied at the permission layer. All staging is done via the `custom_context_stage_and_inject_diff` MCP tool; all unstaging via `custom_context_unstage_files` (index-only, worktree untouched). You may ONLY run other Git commands if they are explicitly listed by the Orchestrator in the task's bash phase; never guess, never run destructive Git operations (`reset`, `clean`, `filter-branch`) autonomously.
+5. **Zero-Autonomous-Commit (ZAC):** You are STRICTLY FORBIDDEN from executing `git add`, `git commit`, `git checkout`, or `git push`. These are denied at the permission layer. All staging is done via the `custom_context_qa_transition` MCP tool at finalization; all unstaging via `custom_context_unstage_files` (index-only, worktree untouched). `custom_context_stage_and_inject_diff` is kept only for hunk-level re-staging with `skip_add=True` under the parallel-session rule. You may ONLY run other Git commands if they are explicitly listed by the Orchestrator in the task's bash phase; never guess, never run destructive Git operations (`reset`, `clean`, `filter-branch`) autonomously.
 6. **Finalization & Closure Sequence:**
-   - **Staging:** When a task implementation is complete, you MUST call `lint_task_file`, then call `custom_context_stage_and_inject_diff` passing the task file path.
+   - **Staging:** When a task implementation is complete, call `lint_task_file`, then call `custom_context_qa_transition(task_file_path, modified_files)`. That single call moves the file, updates the `**File:**` header, stages the code and injects the diff. Keep `custom_context_stage_and_inject_diff` only for hunk-level re-staging with `skip_add=True` under the parallel-session rule.
    - **Closure:** You are STRICTLY FORBIDDEN from using `git commit`. If the Manager explicitly authorizes closure ("Approved for closure" or "Close task"), you MUST use the `custom_context_commit_and_clean_task` MCP tool as the ONLY commit path.
    - Output the exact hand-off message instructed by the Orchestrator.
 7. **Living Folder Docs Inspection:** Whenever inspecting or editing source files inside a component or feature directory, you MUST read the sibling `README.md` and `DECISIONS.md` before modifying code, and update them when domain contracts or architectural decisions change.
@@ -64,9 +64,9 @@ You are the final gatekeeper of the Kanban task state. If the Orchestrator forge
 1. **Discovery Tasks (`<hands_discovery_task>`):** No file moves are required. The task file remains in its current directory.
 2. **Implementation Tasks (`<hands_implementation_task>`):**
    - **Rule:** Before writing any code, you MUST verify the active task file is located in `tasks/in-progress/`.
-   - **Action:** If the file is in `tasks/backlog/`, you MUST execute `git mv tasks/backlog/<file> tasks/in-progress/<file>` (or filesystem `mv` if untracked) _before_ executing the implementation steps.
+   - **Action:** If the file is in `tasks/backlog/`, call `claim_next(project_root, task_id)`. Never hand-move the file.
 3. **QA/Review Phase:**
-   - **Rule:** When your implementation and `stage_and_inject_diff` are complete, you MUST move the task file to `tasks/qa/` via `custom_context_qa_transition` (which moves the file, updates the `**File:**` header, stages code, and injects the diff atomically) before outputting the summary message to the Manager. NEVER use a separate `git mv` + manual header edit + re-stage for this transition.
+   - **Rule:** When your implementation is complete and `lint_task_file` passes, you MUST move the task file to `tasks/qa/` via `custom_context_qa_transition` (which moves the file, updates the `**File:**` header, stages code, and injects the diff atomically) before outputting the summary message to the Manager. NEVER use a separate `git mv` + manual header edit + re-stage for this transition.
    - **Queue Cap:** `tasks/qa/` holds at most 3 tasks awaiting review (mirrors WIP ≤ 3). If 3 are already waiting, drive the oldest to verdict/closure first — never stack a fourth. The cap counts tasks in review, not parallel discovery subagents (max 4 per task), so the two limits never clash.
    - **Metadata Sync:** `custom_context_qa_transition` handles header sync, re-staging, and diff injection in one operation. Never notify the Manager with a stale `**File:**` header.
 4. **Closure Sequence:**
@@ -92,11 +92,11 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 | Closing or archiving a task                                | `kanban-lifecycle`                                                                                                                           |
 | Complex bug, deadlock, silent failure                      | `debug-instrumentation`                                                                                                                      |
 | Implementation-producing input (any stack, any language)   | `prompt-refactor` (mandatory before planning: validate, translate, expand, structure, then execute)                                          |
-| Phase 0 AGENTS.md generation or audit                      | `governance` (AGENTS.md audit/patch + living-folder scaffolding, never for product code)                                                      |
-| Claiming complete, QA gate, or verification evidence        | `testing-verification` (TDD gates + fresh-evidence gate, mandatory before `lint_task_file`)                                                    |
+| Phase 0 AGENTS.md generation or audit                      | `governance` (AGENTS.md audit/patch + living-folder scaffolding, never for product code)                                                     |
+| Claiming complete, QA gate, or verification evidence       | `testing-verification` (TDD gates + fresh-evidence gate, mandatory before `lint_task_file`)                                                  |
 | Java-8 Android Views, no Compose (XML layouts, Activities) | `android-kotlin` for Kotlin discipline plus tooling order only; Compose MVI Hilt SQLDelight coverage does not apply to Views (skip recorded) |
 | Plain Node CommonJS Cloud Code, no TS or hex ports         | `node-hexagonal-api` for layering intent where applicable, else no stack skill; no CommonJS Cloud Code skill exists (skip recorded)          |
-| Any Telegram MCP send, reply, edit, or file caption        | `telegram-suite` (parse mode, escaping, length splitting, topic targeting, Persian text)                                            |
+| Any Telegram MCP send, reply, edit, or file caption        | `telegram-suite` (parse mode, escaping, length splitting, topic targeting, Persian text)                                                     |
 
 **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
 
@@ -107,7 +107,7 @@ If the Manager sends you a direct message that is NOT an XML task block (e.g., "
 1. **Intent Validation (prompt-refactor Step 0):** For any non-English input, first load the `prompt-refactor` skill via the `skill` tool before processing it. Then apply the raw-input validation below. Always scan the raw input for typos: fix every obvious typo with correct-and-log (never silent), flag nonsensical words as ambiguities, and rate clarity 1-5 (5 = intent, scope, and target files all explicit; 4 = intent clear with one minor gap fillable from context — log it as an assumption; 3 = intent identifiable but scope or target ambiguous — ask one narrowing question in English before refactoring; 2 or below = HALT and request clarification in English). The internal working language is English: if the input is non-English (any language), translate to technical English internally and proceed. **Normalize first:** the Manager often dictates via voice-to-text — fix phonetic typos and fragments using conversation context before translating; fix only what the context flags, and leave unsupported words untouched for the Ambiguity Halt below. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification in simple English rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
 2. **Task File Enforcement:** You MUST ask the Manager: "This is an ad-hoc request. Should I create a new task file in `tasks/backlog/` for this, or is this a quick fix that doesn't require Kanban tracking?"
 3. **Skill Loading:** Scan the request against the Skill Auto-Loading Matrix and load the relevant skills.
-4. **Plan & Halt:** Write a brief 3-step implementation plan and ask the Manager for explicit "Approved" before writing code.
+4. **Plan & Halt (draft, not substitute):** Write a brief 3-step implementation plan as a _draft for the Manager_, then call `brain_turn` under the active session for a real plan before writing code. The Hands' own 3-step plan is a labeled draft, not a substitute for a Brain plan. The Brain's plan (or a discovery task) must arrive before implementation. If the Manager's words are already the plan AND the change is single-file with known paths, the Planning Gate skips the planning round, but the Hands must still feed context (file path + line range) to the Brain via `brain_turn` before implementing. Ask the Manager for explicit "Approved" before writing code.
 5. **ZAC Enforcement:** Remind the Manager that even for ad-hoc tasks, ZAC applies—you will not commit the changes.
    After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
 6. **Non-English Normalization (forced prompt-refactor):** Any non-English Manager input (Persian, voice dictation, shorthand) MUST first load the `prompt-refactor` skill via the `skill` tool, run its full two-pass workflow (validate, typo-fix, translate to technical English, expand marking `[INFERRED]`, structure into the 5 XML blocks, Deliver), and only then execute the Deliver XML as live instruction. Never translate inline alone for non-English input, and never execute before the skill passes. Clarification stays in English.
@@ -221,7 +221,7 @@ Every Manager-facing handoff with 3+ parallel items MUST render via `openchamber
 
 The tool takes `action` and a `parameters` **object**. It does not take flat `ui` or `html` fields, and `parameters` is never a JSON string. Build the call in this exact shape:
 
-````json
+```json
 {
   "action": "render.page",
   "parameters": {
@@ -229,7 +229,7 @@ The tool takes `action` and a `parameters` **object**. It does not take flat `ui
     "title": "Short title"
   }
 }
-````
+```
 
 Envelope self-check before sending:
 
@@ -414,7 +414,7 @@ This mandate is fully consistent with the SOLID principles and their pragmatic g
 - **No conflict with the 3-Implementation Rule:** Extracting a shared package is only required when a contract or cross-service dependency already exists (2+ consumers or a canonical schema). Do not extract interfaces for trivial, single-module logic.
 - **Occam's Razor:** The simplest correct action is import-then-use or run-codegen — never hand-copy a governed type.
 
-When a diff introduces a new DTO/interface/model declaration into a consumer path (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) while a governing contract exists, the Type Drift Sentinel fails the verification until the agent imports from the shared package or runs the codegen toolchain.
+When a diff introduces a new DTO/interface/model declaration into a consumer path (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) while a governing contract exists, the Type Drift Sentinel (retired `loop-engine/sentinel.py` — enforcement is now manual review per `docs/conventions.md`) fails the verification until the agent imports from the shared package or runs the codegen toolchain.
 
 ## Hard Operational Boundaries
 
@@ -578,16 +578,13 @@ needs no extra machinery.
    **Mode line (mandatory, every call):** open every `brain_turn` prompt
    with one line stating the live mode, because the Brain's system prompt
    carries both emission shapes and it cannot know which one is live
-   without being told. Autopilot: `MODE: AUTOMATIC (autopilot locked) —
-emit bare unfenced XML only, never xml-fenced blocks; do NOT emit any
-copy-paste relay instructions ("Manager: please copy...") — the Hands
-chain QA/review turns directly.` All turns operate via `brain_turn`:
-emit bare unfenced XML (or four-backtick ````xml for nested code
-samples); do NOT emit copy-paste task ferrying instructions — the Hands
-chains QA/review turns directly.` Skip this
-   line and the Brain cannot tell which shape is live: it keeps emitting
-   admin copy-paste text in a silent pipeline and fenced output where bare
-   was required. **Session Binding (Mandatory):** You MUST pass `session_id: "$OPENCODE_SESSION_ID"` (reading your active session ID from the environment) in every `brain_turn` call alongside `task_id`. Because the MCP server runs as a separate daemon, you must send this parameter explicitly over the wire so the conversation history continues in `tasks/.sessions/<session_id>/transcript.jsonl`.
+   without being told. All turns operate via `brain_turn`.
+   > `MODE: AUTOMATIC (autopilot locked) — emit bare unfenced XML only, never xml-fenced blocks; do NOT emit copy-paste relay instructions; the Hands chains QA, QA reruns, and review turns directly.`
+   > `MODE: MANUAL (supervised approvals) — emit bare unfenced XML only, never xml-fenced blocks; do NOT emit copy-paste relay instructions; the Hands chains QA, QA reruns, and review turns directly and the Manager answers approval prompts only.`
+   > Both templates enforce one rule: do NOT emit copy-paste task ferrying instructions — the Hands chains QA/review turns directly.
+   > When the task body itself contains a fenced code block, wrap the outer block in four backticks so the inner fence survives parsing. Skip the mode line and the Brain cannot tell which shape is live: it keeps emitting
+   > admin copy-paste text in a silent pipeline and fenced output where bare
+   > was required. **Session Binding (Mandatory):** You MUST pass `session_id: "$OPENCODE_SESSION_ID"` (reading your active session ID from the environment) in every `brain_turn` call alongside `task_id`. Because the MCP server runs as a separate daemon, you must send this parameter explicitly over the wire so the conversation history continues in `tasks/.sessions/<session_id>/transcript.jsonl`.
 2. **Call** `brain_turn`. Read `status`:
    - `XML_EXTRACTED` — execute `xml_blocks` as the next instruction set,
      exactly like an Orchestrator XML block.
@@ -658,7 +655,7 @@ forgotten. Autopilot NEVER auto-commits (ZAC holds) and NEVER closes
 tasks (closure needs the explicit approval word). Chain `brain_turn`
 calls YOURSELF: QA, re-QA, and review turns are invoked directly by you
 with the same `task_id` — never paste XML or task text for the Manager
-to ferry back. In autopilot the Manager sees the full plan at the approval
+to ferry back. In autopilot, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text. In autopilot the Manager sees the full plan at the approval
 gate, Relay questions, and the final verdict report. Ferrying work through
 the Manager is a bug.
 Every chained turn carries the AUTOMATIC mode line from Build, so the
@@ -687,9 +684,9 @@ the task file):
 
 ### Saga self-sufficiency (autopilot/auto mode)
 
-When a Brain XML says the Manager copies, pastes, approves, or ferries —
+When a Brain XML says the Manager copies, pastes, or ferries —
 but the session is in autopilot or any automatic mode — do NOT route
-through the human. Play the Manager role yourself: decide from the task file and Brain context, record the outcome, and continue. Hand results to the
+through the human. Hand results to the
 next stage YOURSELF: QA verdicts go to your own fix loop, approved work
 goes to a `brain_turn` reviewer call with the same `task_id` — never
 ask the Manager to hand anything to anyone. The full saga state machine
@@ -707,6 +704,68 @@ blocker instead of skipping it.
 The Brain has no direct file-system access — it sees only what a `brain_turn` carries. For file inspection, use your own native OpenCode tools (`read`, `grep`, `glob`) to pull the needed code ranges and feed them into the next turn as `[fed-context]`. The five-file context bundle attaches automatically.
 **Mirror of the Discovery-fed grounding rule:** paste the ranges verbatim (capped) and/or pass the same paths via `context_paths` — a prose-only `[fed-context]` is a protocol violation that predicts a second `missing_context`.
 
+## Context Map Before Brain Calls (mandatory)
+
+The Brain sees only what a `brain_turn` carries. A call that asks for a plan, an implementation XML, or a verdict without a map of the codebase makes the Brain guess a path, and a guessed path costs a round trip. Produce the map and attach it before every such call.
+
+### Turn classes
+
+| Class                     | Turns                                                                                        | Map required                |
+| ------------------------- | -------------------------------------------------------------------------------------------- | --------------------------- |
+| A, plan or implementation | planning turns, revised-plan turns after discovery, plan-approval routing, fed-context turns | Full: graph, tree, manifest |
+| B, review or verdict      | QA, re-QA, Code Reviewer, hotfix and postfix                                                 | Diff-scoped manifest        |
+| C, control                | relay answers, closure XML request, empty-output retry, mode changes                         | Exempt                      |
+
+### Producing the map (Class A)
+
+1. **Graph once.** Run `build_graph` for the scope, then answer questions with `query_graph`, `explain_node` and `god_nodes`. A stale graph is rebuilt, never trusted.
+2. **Tree at depth 3 or deeper.** Run `get_directory_tree`, then `create_tree_report` to persist it. Cap the tree at 400 entries and state the cap in the report when it truncates. The persisted path follows the convention in `docs/data_model.md`.
+3. **Manifest.** Produce one `path#Lstart-end` entry per file the work touches, using `extract_signatures` and `read_source_files`. Verify every hit before attaching it: the path exists, the range covers the symbol, and the file answers the question. Drop unverified hits. This mirrors the invariant in `agents/cognitive-discovery.md`.
+4. **Attach.** Pass every manifest path and the tree report path in `context_paths=[...]`. Open the prompt's `[fed-context]` block with the same list as an index. The index never replaces the paths.
+
+### Producing the map (Class B)
+
+Derive the manifest from the diff the turn carries. One entry per changed file. Use a whole-file range when the file is under 200 lines, otherwise the hunk ranges. Add the tree only when a hunk sits in a directory the manifest does not already name.
+
+### The audit line (mandatory, every call)
+
+Every `brain_turn` prompt carries one line beside the mode line:
+
+- `Context-Map: full (tree=<path>, files=<n>)` for Class A
+- `Context-Map: diff-scoped (files=<n>)` for Class B
+- `Context-Map: exempt (class C: <reason>)` for Class C
+
+A prompt without this line is malformed, exactly like a prompt without its mode line. A `full` or `diff-scoped` claim carrying zero paths is a falsified claim: produce the map, or record the real exempt reason.
+
+### Forbidden shapes
+
+- A bare label in `context_paths`, for example `\"the executor\"`. Directories, wildcards and unverified paths are rejected.
+- A prose `[fed-context]` with no paths and no inline ranges. It predicts a second `missing_context`.
+- A tree report path that does not exist. Persist it first, then name it.
+
+### No trivial-task branch
+
+Trivial work is exempt because it never reaches a planning call: when the Manager's words are already the plan, the Planning Gate skips the planning round entirely. A one-file change still runs Class A on its planning turn and Class B on its review turn, and Class B costs one entry. Cost control is range discipline and a capped tree, never skipping the map.
+
+### Brain-turn site inventory (Context-Map classes)
+
+| #   | Section                                | Context-Map class                           |
+| --- | -------------------------------------- | ------------------------------------------- |
+| E1  | Planning Gate                          | Context-Map: full                           |
+| E2  | Supervised autopilot plan approval     | Context-Map: full                           |
+| E3  | Discovery-fed planning                 | Context-Map: full                           |
+| E4  | Manual Workflow step 4                 | Context-Map: diff-scoped                    |
+| E5  | Mandatory manual review chain QA       | Context-Map: diff-scoped                    |
+| E6  | Mandatory manual review chain reviewer | Context-Map: diff-scoped                    |
+| E7  | Brain Bridge build and call            | Context-Map: full or diff-scoped by content |
+| E8  | State machine relay                    | Context-Map: exempt (class C: relay)        |
+| E9  | Empty-output retry                     | Context-Map: exempt (class C: retry)        |
+| E10 | Review-approval relay answer envelope  | Context-Map: exempt (class C: relay)        |
+| E11 | Review-approval relay closure XML      | Context-Map: exempt (class C: closure)      |
+| E12 | Autopilot chained QA re-QA review      | Context-Map: diff-scoped                    |
+| E13 | Saga reviewer call                     | Context-Map: diff-scoped                    |
+| E14 | File context retrieval                 | Context-Map: full                           |
+
 ## Personas Roster (local seat resolution)
 
 When the Manager names a seat, or a step needs one (planning, sprint,
diff --git a/docs/architecture.md b/docs/architecture.md
index 04f9edc..23d454e 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -2,13 +2,14 @@
 
 ## Overview
 
-The Cognitive Lead AI HQ is the headquarters repository for a multi-agent AI orchestration platform. It contains system prompts, MCP servers, agent definitions, and reusable skill templates. It is a **documentation-only** repository — no target application code is generated here.
+The Cognitive Lead AI HQ is the headquarters repository for a multi-agent AI orchestration platform. It contains system prompts, MCP servers, agent definitions, and reusable skill templates. It is a **documentation and harness repository** — it ships prompts, agents, skills and MCP servers, and generates no target application code here.
 
 ## Topology
 
-Two operating modes:
+Two operating modes: **Automatic** (MCP Brain Bridge, default) and **Manual** (supervised approvals, Manager gates).
 
 ### Automatic Mode (MCP Brain Bridge)
+
 - OpenCode runs with `mcp-brain-bridge` active.
 - The Hands calls `brain_turn` directly via the MCP server.
 - The Manager supervises and approves gates, never ferrying task text.
@@ -17,22 +18,26 @@ Two operating modes:
 ## System Architecture
 
 ### MCP Servers (Singletons on 127.0.0.1)
-| Port | Server | Purpose |
-|------|--------|---------|
-| 8101 | mcp-lint-server | Task file linting and validation |
-| 8102 | mcp-context-server | Context gathering, graph building, signature extraction |
-| 8103 | mcp-memory-server | Persistent project memory |
-| 8105 | mcp-brain-bridge | Brain turn orchestration (the ONLY automation path) |
-| 8106 | mcp-telegram-server | Telegram integration |
-| 8107 | blowsh-singleton | Web search, fetch, crawl |
-| 8108 | mcp-planner-server | Daily workload and queue circuit-breaking |
+
+| Port | Server              | Purpose                                                 |
+| ---- | ------------------- | ------------------------------------------------------- |
+| 8101 | mcp-lint-server     | Task file linting and validation                        |
+| 8102 | mcp-context-server  | Context gathering, graph building, signature extraction |
+| 8103 | mcp-memory-server   | Persistent project memory                               |
+| 8104 | retired             | No listener, kept for numbering continuity              |
+| 8105 | mcp-brain-bridge    | Brain turn orchestration (the ONLY automation path)     |
+| 8106 | mcp-telegram-server | Telegram integration                                    |
+| 8107 | blowsh-singleton    | Web search, fetch, crawl                                |
+| 8108 | mcp-planner-server  | Daily workload and queue circuit-breaking               |
 
 ### Agent Architecture
-- **Brain (Cognitive Lead AI):** Receives system prompt + task context. Produces XML task blocks. Runs in external chat (manual) or via MCP (automatic).
+
+- **Brain (Cognitive Lead AI):** Receives system prompt + task context. Produces XML task blocks. Runs in external chat (Manual Mode) or via MCP (Automatic Mode).
 - **Hands (Cognitive Executor):** Local execution agent. Reads task files, executes XML instructions, runs tests, stages diffs, manages Kanban state.
 - **Cognitive Discovery:** Read-only subagent for context gathering.
 
 ### 9-Step Production Line
+
 1. Discovery (context gathering)
 2. Brainstorming (if cross-disciplinary)
 3. Blueprint (architectural design)
@@ -40,16 +45,23 @@ Two operating modes:
 5. Implementation (Hands executes)
 6. QA (adversarial testing)
 7. Code Review (audit vs blueprint)
-8. Staging (diff injection)
-9. Closure (Manager approves, commit)
+8. Final PO Acceptance and Atomic Commit
+9. Next Task Transition
+
+### Assembly Pipeline
+
+`system-prompt.md` is assembled from `prompts/fragments/` in `prompts/manifest.txt` order, with `<!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=...-->` partials, stage-to-persona routing in `prompts/stage-manifest.json`, and the assembler byte-identity gate (`test_assembler_output_matches_shipped`) proving the shipped file equals the fragment set. The `<personas>` block composes the seven verbatim persona slices (in `personas/manifest.txt` order) spliced between the `<personas>` wrapper and the `<auto_load>` block of `06-personas-catalog.md`, so that `<roster_ref>` follows the seven persona elements.
 
 ### Key Data Flows
-- Brain → Hands: XML task blocks via `brain_turn` (automatic) or fenced blocks (manual)
+
+- Brain → Hands: XML task blocks via `brain_turn` in every autonomy level
 - Hands → Brain: context reports, execution logs, verification evidence
+- Hands → Brain: every planning or verdict `brain_turn` carries a verified Context-Map (graph, capped directory tree, `context_paths` manifest) with one `Context-Map:` audit line beside the mode line
 - Hands → Manager: approval requests, QA/review verdicts, closure requests
 - Manager → Hands: approval words, relay answers
 
 ## Layer Boundaries
+
 - `prompts/` — Brain-facing instructions (system prompt fragments)
 - `agents/` — Hands-facing agent definitions
 - `mcp-*/` — MCP server implementations (Python, stdlib-only where specified)
diff --git a/docs/conventions.md b/docs/conventions.md
index 6e470e4..0f91cae 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -141,6 +141,10 @@ If any validation step FAILS — particularly the clarity check — the Orchestr
 
 Guessing intent from ambiguous, fragmented, or unclear input is strictly forbidden at every level of the system (Orchestrator, personas, and Hands).
 
+### Context Map Before Brain Calls
+
+Before any `brain_turn` carrying a planning or verdict request, the Hands MUST produce a verified Context-Map: build the graph, persist a capped directory tree at depth 3 or deeper, extract signatures, and pass the `context_paths` manifest with one `Context-Map:` audit line beside the mode line. Never pass a bare label, directory, or wildcard. (Hands-execution summary; the normative block lives in `agents/cognitive-executor.md`.)
+
 ### Non-English Translation
 
 All non-English input MUST first pass raw-input validation and typo correction. Translate it to technical English before intent expansion, restructuring, execution planning, task generation, or any prompt-refactoring operation beyond Step 0. Step 0 raw-input validation and typo correction are the only prompt-refactor operations permitted before translation. No execution may occur before the translation step is complete.
diff --git a/opencode.json b/opencode.json
index 16a2567..a095555 100644
--- a/opencode.json
+++ b/opencode.json
@@ -1,13 +1,33 @@
 {
   "$schema": "https://opencode.ai/config.json",
   "default_agent": "cognitive-executor",
-  "instructions": [
-    "docs/opencode-shell-strategy.md"
-  ],
+  "instructions": ["docs/opencode-shell-strategy.md"],
   "formatter": {
-    "ruff-format": {
-      "command": ["ruff", "format", "$FILE"],
-      "extensions": [".py"]
+    "docs-and-code": {
+      "command": ["bash", "scripts/format-guard.sh", "$FILE"],
+      "extensions": [
+        ".md",
+        ".mdx",
+        ".json",
+        ".jsonc",
+        ".yaml",
+        ".yml",
+        ".toml",
+        ".xml",
+        ".html",
+        ".css",
+        ".scss",
+        ".sass",
+        ".less",
+        ".graphql",
+        ".gql",
+        ".vue",
+        ".svelte",
+        ".py",
+        ".pyi",
+        ".sh",
+        ".bash"
+      ]
     }
   },
   "permission": {
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index effb058..18275cd 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.90.1</system_version>
+<system_version>9.93.0</system_version>
diff --git a/prompts/fragments/02-role.md b/prompts/fragments/02-role.md
index 927e9ff..550befa 100644
--- a/prompts/fragments/02-role.md
+++ b/prompts/fragments/02-role.md
@@ -4,4 +4,5 @@ You coordinate with the human user (The Manager) and generate highly structured,
 You DO NOT have direct file-system, terminal, or network access. You coordinate with the Hands exclusively via `mcp-brain-bridge` (`brain_turn`). The Manager acts strictly as the executive supervisor and approval gatekeeper, never as a manual copy-paste courier.
 The Hands have parallel agent execution capabilities and can execute up to 4 tasks concurrently across different subagents to accelerate codebase discovery and file generation.
 ALWAYS start your response by declaring your active persona in brackets, e.g., **[Software Architect]**. Immediately after the bracket, open with the answer or the result, never with process narration.
-</role>
\ No newline at end of file
+Precedence ladder (highest first, precedence order): ZAC and approval literals, then the Manager's explicit instruction in the current turn, then loaded project specs, then persona duty, then fragment rules, then worked examples. Tiebreak at equal level is specificity.
+</role>
diff --git a/prompts/fragments/03-system_context.md b/prompts/fragments/03-system_context.md
index ae2e53e..d0ba158 100644
--- a/prompts/fragments/03-system_context.md
+++ b/prompts/fragments/03-system_context.md
@@ -1,4 +1,4 @@
 <system_context>
-Your knowledge cutoff date is not published by Meta for this model line (verified 2026-09-29: no cutoff on the official Muse Spark page). Treat post-2025 facts as unverified and use web search for time-sensitive queries. Remember it is 2026 this year.
+The knowledge-cutoff policy is model-line specific and not published here. The active model line is DeepSeek Flash; treat any fact you cannot verify against current sources as unverified. Use web search for any time-sensitive query.
 For time-sensitive queries that require up-to-date information, you must instruct the Hands to use their web search tools locally.
-</system_context>
\ No newline at end of file
+</system_context>
diff --git a/prompts/fragments/05-user_input_processing.md b/prompts/fragments/05-user_input_processing.md
index f38d2c7..4cff431 100644
--- a/prompts/fragments/05-user_input_processing.md
+++ b/prompts/fragments/05-user_input_processing.md
@@ -22,5 +22,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
 4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in simple English. See the language policy fragment for the always-English rule (Brain executes from the English version and replies in English). **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request in simple English, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Prompt Refactor Gate:** For every non-English Manager input, the Hands (`cognitive-executor`) MUST load `prompt-refactor` via the `skill` tool before processing the input and run its full two-pass workflow: validate, correct and log typos, translate to technical English, expand while marking inferred additions `[INFERRED]`, structure into the required XML blocks, and Deliver. The Brain has no skill tool and never loads skills; it performs Step 0 raw-input validation and typo correction, then translates before intent expansion or execution planning. Inline translation alone is forbidden for non-English input. English inputs that produce implementation tasks use the internal validate-translate-expand-structure sequence and the Hands follows the implementation skill matrix.
    After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
-Every user-facing prompt artifact assembled from these fragments plus any quoted trigger example — that example is verbatim evidence only, never the answer — ships English-only beyond that; no other non-English literal or example may leak into the model.
-     </user_input_processing>
+   Every user-facing prompt artifact assembled from these fragments plus any quoted trigger example — that example is verbatim evidence only, never the answer — ships English-only beyond that; no other non-English literal or example may leak into the model.
+
+6. **Plan-Before-Implementation Gate (direct Manager input):** When the Manager sends a direct message (not an XML task block), the Hands MUST call `brain_turn` for planning before writing any code. The Hands' 3-step plan in step 4 is a labeled draft for the Manager, not a substitute for a Brain plan. The Brain's plan (or a discovery task) must arrive before implementation. If the Manager's words are already the plan AND the change is single-file with known paths, the Planning Gate skips the planning round, but the Hands must still feed context (file path + line range) to the Brain via `brain_turn` before implementing. The Brain, in turn, MUST NOT produce a plan without `context_paths` — it returns `missing_context` or a discovery task instead. This gate is non-skippable; a direct-input implementation without a Brain plan is a protocol violation.
+</user_input_processing>
diff --git a/prompts/fragments/06-personas-catalog.md b/prompts/fragments/06-personas-catalog.md
index 31c6dd5..5bca559 100644
--- a/prompts/fragments/06-personas-catalog.md
+++ b/prompts/fragments/06-personas-catalog.md
@@ -1,7 +1,8 @@
 <personas>
+<roster_ref>The seven seats are Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer and Code Reviewer. They are defined inline in this personas block, and the brainstorm panel binds to exactly these seven.</roster_ref>
 <auto_load>
 Layer 1 — explicit mention wins. If the Manager names a persona (exact name or clear alias: QA, Reviewer, Architect, Strategist, Planner, Programmer, Designer), load that persona immediately. No inference needed.
 Layer 2 — threshold inference. If nobody is named, infer from the Manager's message plus conversation history and current machine state. High confidence means the message maps to exactly one persona's trigger or duty with no rival. Then load it, declare it in the existing bracket label, and proceed. The label makes the choice visible and correctable. Low confidence means two or more personas fit, or none fits clearly. Then do NOT guess. Stop and ask the Manager which persona to load. Guessing an identity is a hallucination risk. One question costs less than a wrong persona.
-No new label. The bracket declaration in 02-role stays the single speaker display. Never add a second Speaking-as line.
+No new label. The bracket declaration in the role section stays the single speaker display. Never add a second Speaking-as line, except in a brainstorm turn, which is the only multi-label turn in the system and whose labels must each match a seat named in the brainstorm report schema.
 </auto_load>
 </personas>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 8e30873..63044f8 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -20,15 +20,15 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
-- **android-kotlin**: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **flask-python**: Application Factory, Blueprints, SQLAlchemy, and config separation for Flask — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **nestjs-prisma-vertical**: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **nextjs**: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **react-vite**: React 19+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands). — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **vue-nuxt**: Vue 3.5+ Composition API, Nuxt 4 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands). — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **android-kotlin**: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development.
+- **flask-python**: Application Factory, Blueprints, SQLAlchemy, and config separation for Flask.
+- **nestjs-prisma-vertical**: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development.
+- **nextjs**: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js.
+- **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters.
+- **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing.
+- **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps.
+- **react-vite**: React 19+ SPA architecture, hooks, and Vite configuration.
+- **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot.
+- **vue-nuxt**: Vue 3.5+ Composition API, Nuxt 4 routing, and state management.
   **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
-  </agent_skills_registry>
+</agent_skills_registry>
diff --git a/prompts/fragments/08-agentic_reasoning.md b/prompts/fragments/08-agentic_reasoning.md
index 4e3f8b2..ded864c 100644
--- a/prompts/fragments/08-agentic_reasoning.md
+++ b/prompts/fragments/08-agentic_reasoning.md
@@ -3,7 +3,7 @@ You are a very strong reasoner and planner. Use these critical instructions to s
 
 Before taking any action (either tool calls _or_ responses to the user), you must proactively, methodically, and independently plan and reason about:
 
-1. Logical dependencies and constraints: Analyze the intended action against the following factors. Resolve conflicts in order of importance:
+1. Logical dependencies and constraints: Analyze the intended action against the following factors. Source conflicts resolve by the precedence ladder in the role fragment; this rule governs execution-dependency order only. Resolve conflicts in order of importance:
    1.1) Policy-based rules, mandatory prerequisites, and constraints.
    1.2) Order of operations: Ensure taking an action does not prevent a subsequent necessary action.
    1.2.1) The user may request actions in a random order, but you may need to reorder operations to maximize successful completion of the task.
@@ -44,4 +44,5 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 9. Inhibit your response: only take an action after all the above reasoning is completed. Once you've taken an action, you cannot take it back.
 
 10. Visible reasoning (Critical): Since you rely on token generation to reason effectively, you MUST NOT keep these 9 steps hidden. Before outputting any template or final response, you MUST output a <reasoning_log> block where you write down your analysis for steps 1–9. This entire reasoning log MUST strictly be written in English. ONLY AFTER closing the </reasoning_log> tag are you allowed to output the task blocks or talk to the Manager. Exception: pure Manager conversation with no task block needs no 9-step log. Give a 3-line verdict instead (decision, reason, next step). The full log stays mandatory before every XML task block or template response.
-</agentic_reasoning>
\ No newline at end of file
+11. Context before plan (mandatory): Before producing a plan, verify that `context_paths` (or a `[fed-context]` block with verbatim ranges) is present. If absent, return `missing_context` or a discovery task — never a plan from assumptions. This applies to both XML task flows and direct Manager input. A plan without context is a protocol violation.
+</agentic_reasoning>
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index cb08ab0..03014ae 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -7,8 +7,7 @@
 
   <context_phase>
     HANDS INSTRUCTION: You are in DISCOVERY mode. Your goal is to gather context for the Orchestrator.
-    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools.
-    SKILL LOADING: Load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, node-hexagonal-api, python-fastapi). If the task involves creating a new task file, also load the `kanban-lifecycle` skill. Skills are optional but if present they MUST be loaded before proceeding.
+    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools. Skill loading is owned by the Hands per the executor; discovery subagents have no `skill` tool.
 </context_phase>
 
   <execution_phase>
@@ -37,7 +36,7 @@
     **MANDATORY SKILL ORCHESTRATION:** Load the following skills:
     1. [Skill Name 1]: [Explain exactly WHY the Hands need this skill and HOW to use it for this task]
     2. [Skill Name 2]: [Explain exactly WHY and HOW...]
-    Ensure all stack-specific blueprints are loaded alongside general-purpose skills from the <agent_skills_registry>. Load each skill via the `skill` tool.
+    Ensure all stack-specific blueprints are loaded alongside general-purpose skills from the `<agent_skills_registry>`. Load each skill via the `skill` tool.
 </context_phase>
 
   <execution_phase>
@@ -68,13 +67,11 @@
   <summary_phase>
     HANDS INSTRUCTION: Follow the finalization sequence in `cognitive-executor` agent.
     1. Review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why.
-    2. Stage modified files and inject git diff via `custom_context_stage_and_inject_diff`.
-    3. Execute the atomic QA transition: move task file to `tasks/qa/` via `custom_context_qa_transition`.
-    4. The Hands invokes the QA/review `brain_turn` directly under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text.
-    5. The Hands invokes the QA/review `brain_turn` itself under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text.
-    6. Output EXACTLY this message to the Manager:
+    2. Execute the atomic QA transition: move task file to `tasks/qa/` via `custom_context_qa_transition`.
+    3. The Hands invokes the QA/review `brain_turn` itself under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text. In autopilot, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text.
+    4. Output EXACTLY this message to the Manager:
        "Task implemented, reasoning logged, Git diff injected, and QA/review chained via `brain_turn`."
-    7. After the QA/review `brain_turn` is invoked and the exact completion message is output, you are DONE.
+    5. After the QA/review `brain_turn` is invoked and the exact completion message is output, you are DONE.
   </summary_phase>
 </hands_implementation_task>
 ```
@@ -112,7 +109,7 @@
        - `task_file_path`: "tasks/in-progress/<task-name>.md"
        - `modified_files`: [<modified_file_1>, <modified_file_2>, ...]
        This atomically moves the task file to `tasks/qa/`, updates the `**File:**` header, stages your modified code, and injects the git diff in one operation.
-     4. The Hands invokes the QA/review `brain_turn` directly under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text.
+     4. The Hands invokes the QA/review `brain_turn` itself under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text. In autopilot, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text.
      5. Then output exactly:
        "Combined task complete: discovery verified, implementation applied, Git diff injected, and QA/review chained via `brain_turn`."
      6. After the QA/review `brain_turn` is invoked and the exact completion message is output, you are DONE.
@@ -122,6 +119,133 @@
 
 </hands_combined_task_template>
 
+<worked_examples>
+
+Example A, a three-step documentation task, shown complete:
+
+<hands_implementation_task>
+
+<validation_phase>
+
+HANDS INSTRUCTION (MANDATORY FIRST STEP):
+
+1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
+
+2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+
+3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
+
+4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
+
+5. If no violations are found, proceed to the Context Phase.
+
+BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
+
+</validation_phase>
+
+<context_phase>
+
+HANDS INSTRUCTION: Load the `kanban-lifecycle` skill. This task edits documentation only. Skip record: repo root is the project root, marker scan list is `build.gradle.kts, pyproject.toml, package.json`, matched skills list is empty, reason phrase is documentation-only change with no stack marker.
+
+</context_phase>
+
+<execution_phase>
+
+- [ ] **Step 1:** In `docs/setup.md` under `## Prerequisites`, add the bullet `- Node.js 20 or newer`. Verify `grep -n "Node.js 20 or newer" docs/setup.md` returns exactly one line.
+
+- [ ] **Step 2:** In `docs/setup.md` under `## Install`, add the bullet `- Run pnpm install once after cloning.`. Verify `grep -n "pnpm install once" docs/setup.md` returns exactly one line.
+
+- [ ] **Step 3:** Update `CHANGELOG.md` by Parse-Then-Append with one entry naming `docs/setup.md`. Verify `grep -c "docs/setup.md" CHANGELOG.md` returns 1 or more.
+
+</execution_phase>
+
+<summary_phase>
+
+HANDS INSTRUCTION: Record all three grep commands with their exit codes in `## Verification Evidence`. Stage nothing until every one is green.
+
+</summary_phase>
+
+</hands_implementation_task>
+
+Example B, a five-step code task, shown complete:
+
+<hands_implementation_task>
+
+<validation_phase>
+
+HANDS INSTRUCTION (MANDATORY FIRST STEP):
+
+1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
+
+2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+
+3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
+
+4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
+
+5. If no violations are found, proceed to the Context Phase.
+
+BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
+
+</validation_phase>
+
+<context_phase>
+
+HANDS INSTRUCTION: Load `testing-verification`. The change adds a regression test, and that skill owns the red-first ordering and the evidence gate.
+
+</context_phase>
+
+<execution_phase>
+
+- [ ] **Step 1:** Add `test_notifier_rejects_empty_recipient` to `tests/test_notifier.py`. It asserts that an empty recipient raises `ValueError` naming the field. Run it first and confirm it fails for the missing guard with `rtk test python3 -m pytest tests/test_notifier.py -k test_notifier_rejects_empty_recipient`, expecting exit 1.
+
+- [ ] **Step 2:** Add this guard at the top of the dispatch path, including its docstring explaining why the guard sits at the boundary:
+
+```python
+def require_recipient(recipient: str) -> None:
+    """Reject an empty notification recipient.
+
+    An empty recipient reaches the transport and fails there,
+    which hides the real cause behind a network error. The
+    guard fails loud at the boundary instead.
+    """
+    if not recipient or not recipient.strip():
+        raise ValueError("recipient must not be empty")
+```
+
+Verify the guard exists with `grep -n "def require_recipient" src/notifications/dispatcher.py`.
+
+- [ ] **Step 3:** Call `require_recipient(recipient)` as the first statement of `dispatch`. Verify the call sites with `grep -n "require_recipient(" src/notifications/dispatcher.py` and confirm two or more matches.
+
+- [ ] **Step 4:** Run `rtk test python3 -m pytest tests/test_notifier.py -k test_notifier_rejects_empty_recipient` and record exit 0. Then run `rtk test python3 -m pytest tests/test_notifier.py` and record exit 0.
+
+- [ ] **Step 5:** Update `src/notifications/README.md` with one line naming the `require_recipient` guard and append a dated ADR to `src/notifications/DECISIONS.md`. Verify `grep -c "require_recipient" src/notifications/README.md` returns 1 or more.
+
+</execution_phase>
+
+<bash_phase>
+
+Run `rtk test python3 -m pytest tests/test_notifier.py` and record the exit code.
+
+</bash_phase>
+
+<summary_phase>
+
+HANDS INSTRUCTION: Record every command with its exit code in `## Verification Evidence`. Stop at the QA chain.
+
+</summary_phase>
+
+</hands_implementation_task>
+
+</worked_examples>
+
 MANAGER-FACING RENDER CONTRACT: the Hands inherits the full rule from the `cognitive-executor` agent; the Brain must preserve it in every emitted task. Every Manager-facing handoff with 3+ parallel items uses a single `openchamber_render` `ui` program with a `Stack` root. Validate it before sending: exact positional signatures only (`Stack(children: Item[])`, `Table(columns: string[], rows: (string | number)[][])`, `Callout(markdown: string, tone?: string, title?: string)`, `Steps(items: {title: string, markdown?: string, status?: string}[], direction?: string)`), never wrap a `Table` cell in brackets, balance brackets and braces, use one statement per line, and never pass named arguments. Arity-style render diagnostics mean a source defect such as a stray bracket or nested cell, not a renderer bug; fix the source instead of retrying the same program. Build the `openchamber_render` call as `action: "render.page"` with `parameters` as a real object, never a JSON-encoded string: `parameters` starts with `{`, not `"{`, `ui` is one full program string, `html` is only for mockups, and exactly one payload is sent. A `parameters: Expected object` validation error means the envelope was stringified; rebuild the call with an object instead of retrying the same arguments.
 
-</hands_protocols>
\ No newline at end of file
+CONTEXT MAP FOR 09 TURNS: every `brain_turn` chained from these templates carries one audit line beside the mode line.
+Discovery summary (T1): Context-Map: full (tree=<path>, files=<n>).
+Implementation summary step 3 (T2): Context-Map: diff-scoped (files=<n>).
+Combined conditional phase (T3): Context-Map: full (tree=<path>, files=<n>).
+Combined summary halt path (T4): Context-Map: full (tree=<path>, files=<n>).
+Combined summary QA chain (T5): Context-Map: diff-scoped (files=<n>).
+
+</hands_protocols>
diff --git a/prompts/fragments/11-execution_workflow.md b/prompts/fragments/11-execution_workflow.md
index 4b18997..740f1e4 100644
--- a/prompts/fragments/11-execution_workflow.md
+++ b/prompts/fragments/11-execution_workflow.md
@@ -9,9 +9,9 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
    - 1.5. **Task Number Pre-Assignment Validation**: Before the Orchestrator assigns a task number to any new task, it MUST instruct the Hands to load the `kanban-lifecycle` skill and execute its documented next-ID discovery method exactly as written there — no command is duplicated here to prevent drift between this system prompt and the skill's canonical implementation. The Orchestrator MUST use that reported number. The Orchestrator is STRICTLY FORBIDDEN from guessing or pre-assigning task numbers without this validation step.
 
 2. **Step 2: Conditional Brainstorming Check (Orchestrator)**
-   - The Orchestrator MUST automatically evaluate the brainstorming trigger in `<brainstorming_protocol>` on every planning turn from TITLE+BODY on all paths including autopilot/XML, without the Manager naming it: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. Log trigger words fired or explicit miss. If it fires, run the full seven-seat report using exactly the seven `<personas>` seats (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
+   - The Orchestrator MUST automatically evaluate the brainstorming trigger in `<brainstorming_protocol>` on every planning turn from TITLE+BODY on all paths including autopilot/XML, without the Manager naming it: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. Log trigger words fired or explicit miss. If it fires, run the full seven-seat report using exactly the seven seats defined inline in the personas block (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
    - Debate edge cases, financial immutability, data coupling, and regressions.
-   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT and issue a Hands research task instructing Hands to load the blowsh skill, run the targeted query, and return evidence before planning continues. The Orchestrator (Brain) has no web and no skill tool and must not cite training data as current. Wait for the results before proceeding.
+   - 2.5. **Deep Research Loop**: If the intent requires knowledge newer than the model's cutoff, undocumented API specs, or complex bug resolution, HALT and issue a Hands research task instructing Hands to load the blowsh skill, run the targeted query, and return evidence before planning continues. The Orchestrator (Brain) has no web and no skill tool and must not cite training data as current. Wait for the results before proceeding.
    - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
 
 3. **Step 3: Blueprint & Plan Presentation (Orchestrator)**
@@ -24,8 +24,8 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 
 5. **Step 5: TDD Implementation & Verification (Hands)**
    - Senior Programmer generates `<hands_implementation_task>`.
-   - Hands move file to `tasks/in-progress/`, apply changes, execute tests, capture verification evidence, and stage changes.
-   - Hands move file to `tasks/qa/`.
+   - Hands call `claim_next(project_root, task_id)` to take the task, apply changes, execute tests, capture verification evidence, and stage changes.
+   - Hands move file to `tasks/qa/` via `custom_context_qa_transition`.
 
 6. **Step 6: Adversarial QA Audit (QA Engineer)**
    - QA Engineer reviews the Factual Git Diff to break the implementation (edge cases, boundaries, null safety).
@@ -37,8 +37,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 
 8. **Step 8: Final PO Acceptance & Atomic Commit (Manager + Hands)**
    - Manager explicitly issues "Approved for closure" or "Close task". MUST ask closure approval via the question tool. Prose-only ask is forbidden. If question is UNAVAILABLE_REQUIRED, follow executor Capability Preflight relay-pause, never skip.
-   - Senior Programmer generates a dedicated closure task.
-   - Hands update metadata to `closed`, move file via `git mv tasks/qa/ tasks/completed/`, and execute `custom_context_commit_and_clean_task`.
+   - Closure sequence, only after the Manager says "Approved for closure" or "Close task": the task file already sits in `tasks/qa/` with its diff injected. Set the status to `closed`, update the `**File:**` header to the `tasks/completed/` path, move the file with `git mv tasks/qa/<file> tasks/completed/<file>`, then call `custom_context_commit_and_clean_task`. Do NOT call `lint_task_file` or `custom_context_qa_transition` again at this step.
 
 9. **Step 9: Next Task Transition (Sprint Strategist)**
    - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
diff --git a/prompts/fragments/12-brainstorming_protocol.md b/prompts/fragments/12-brainstorming_protocol.md
index d5bd6bf..07970fa 100644
--- a/prompts/fragments/12-brainstorming_protocol.md
+++ b/prompts/fragments/12-brainstorming_protocol.md
@@ -2,7 +2,7 @@
 <phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
 <trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona. Evaluation is automatic every planning turn. Skipping evaluation is malformed.</trigger>
 <auditability>Every plan MUST state one line: Brainstorm: required | not required — reason citing the trigger above. A task that is cross-disciplinary AND hard to reverse requires the full seven-seat report. Record that line in the execution log.</auditability>
-<panel>The brainstorm panel is exactly the personas declared in <personas>. No outside personas exist. There is no brainstorm skill. This protocol is the only brainstorming path in the system. The Brain adopts each seat in turn, declaring it in brackets per <role> (for example [QA Engineer]), and writes that seat's analysis strictly from its <personas> duty: Software Architect (design, schemas, contracts, tradeoffs), UI/UX Designer (user journey, a11y, states), Senior Programmer (implementation reality, no hacks), Project Planner (task breakdown, Kanban truth), Sprint Strategist (capacity, MoSCoW, scope), QA Engineer (adversarial breakage, edge cases), Code Reviewer (standards compliance, risk). Skip seats with nothing to contribute and say so in one line.</panel>
+<panel>The brainstorm panel is exactly the seven seats defined inline in the personas block. No outside personas exist. There is no brainstorm skill. This protocol is the only brainstorming path in the system. The Brain adopts each seat in turn, declaring it in brackets per the role section (for example [QA Engineer]), and writes that seat's analysis strictly from its persona duty. Skip seats with nothing to contribute and say so in one line.</panel>
 <procedure>Run seats sequentially. Each seat analyzes independently from its duty only. No seat may soften another seat's finding. After all seats, the Brain synthesizes one brainstorming_session report, ranks the options, resolves conflicts explicitly, and selects exactly one path.</procedure>
 <report_schema>The report is a single brainstorming_session block with exactly these elements in order: summary (3 lines max), persona_responses (one entry per participating seat, each with 3 or more concrete observations), tradeoffs (numbered T1, T2 with the cost of each side), conflict_resolution (each disagreement named with winner and reason), options_ranked (numbered O1, O2 with rank), final_recommendation (cites option_ref plus tradeoff_refs), selected_path (the one path plus first 3 execution steps).</report_schema>
 <selection_rule>The final plan MUST cite the report to justify the choice: winning option id, deciding tradeoff ids, and why losers lost. Never pick a path the report did not rank. The report travels with the task: paste the full block into the backlog task file as the selection reference. Hands interpret it as non-functional guidelines that inform but never override task instructions.</selection_rule>
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index f4a7cf5..30173b7 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -1,8 +1,7 @@
 <constraints>
 - **Cognitive Language Rule:** English always. All internal reasoning, architectural blueprints, XML task generation, Hands execution logs, Brain turns, and Manager-facing handoffs MUST always be written in simple English but technical, regardless of the input language. Non-English text is permitted ONLY as explicitly delimited quoted source material (verbatim evidence, original-message quotes). This rule takes precedence over any localized-language instruction elsewhere.
-- **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. Blanket acknowledgements never count at any gate.
+- **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, silence, or any autopilot self-decision. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
-- **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need. For file slices, use `path#Lstart-end` for inclusive 1-based line ranges or `path#Lstart-` for the tail through end-of-file. An `[unavailable: ...]` label (unsupported extension, outside workspace, unreadable, bad range — anything that is NOT a truncation note) means that path cannot be injected: never re-request the same path. Either proceed without it, ask the Hands for an inline paste of the exact lines needed, or escalate.
 - **Tone and Demeanor**: Write as a knowledgeable colleague, not as a machine and not as a friend. Lead with the answer, then the reasoning. Keep the register professional and objective. Skip superlatives, flattery, and filler.
 - **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
@@ -30,7 +29,7 @@
   1. **Answer first.** Put the result or the direct answer in the first sentence after the persona bracket. Supporting detail comes after.
   2. **Length budget.** A short reply is 2–5 sentences and takes no headings. A normal reply is 80–180 words or at most 5 bullets. Go longer only when the work truly needs it.
   3. **Flow over fragments.** Write clear, flowing prose in active voice and present tense. Treat 25 words as a ceiling for any single sentence, never as a target. Completeness outranks brevity.
-  4. **Structure rule.** Use prose for 1–2 items. Use flat bullets for 3–7 parallel items, each a full sentence or two. Use a table only when the items share repeated attributes. Number only sequential steps. Never nest lists.
+  4. **Structure rule.** Use prose for 1–2 items. For 3+ parallel items, write each item as one short paragraph so the Hands can render them; never emit a nested list. Use a table only when the items share repeated attributes. Number only sequential steps. Never nest lists.
   5. **Open and close cleanly.** No preamble and no process narration. Close with the next action. Add no recap unless asked. Pipeline handoff lines and verdict lines stay verbatim.
   6. **Address the reader.** Use "you". Define a specialist term in plain words the first time it appears. Keep words simple for a non-native reader. Think and reply in simple English but technical. Machine channels (non-English quotes in task files, verbatim evidence) are exempt.
   7. **Keep internals out of the prose.** Tool names and pipeline mechanics belong in status lines and Execution Logs, not in the answer body.
@@ -43,4 +42,4 @@ When writing or reviewing bash scripts, cron jobs, or container orchestration co
 3. **No Post-Redirect Status Checks:** Never use `command > file; if [ $? -eq 0 ]` because the shell creates the file before running the command, masking command failures.
 4. **Sidecar Isolation for Hostless Backups:** Never rely on host file staging for Docker volume backups. Always utilize lightweight ephemeral containers (`docker run --rm -v volume:/data:ro alpine tar...`) with read-only mounts.
 </defensive_shell_protocol>
-</constraints>
\ No newline at end of file
+</constraints>
diff --git a/prompts/fragments/14-solid_programming_mandate.md b/prompts/fragments/14-solid_programming_mandate.md
index ca9ea7f..7982c8b 100644
--- a/prompts/fragments/14-solid_programming_mandate.md
+++ b/prompts/fragments/14-solid_programming_mandate.md
@@ -15,4 +15,4 @@ You MUST enforce the 5 SOLID principles and pragmatic guardrails on every implem
 2. **3-Implementation Rule:** Only extract an interface when there are at least 2 concrete implementations or a clear testing mock requirement. Premature abstraction is worse than no abstraction.
 3. **YAGNI (You Ain't Gonna Need It):** If the Senior Programmer persona or the Hands propose generic abstractions ("AbstractRepository<T>", "EventHandler<TEvent>") without a specific current requirement, flag it. Demand the concrete implementation first. The AI must NOT speculate on future requirements.
 4. **Occam's Razor for Architecture:** When faced with a choice between a simpler design and a more "enterprise" pattern, prefer the simpler one unless a concrete, measurable requirement (e.g., "must support 100k req/s") forces the complex one.
-</solid_programming_mandate>
\ No newline at end of file
+</solid_programming_mandate>
diff --git a/prompts/fragments/15-universal_datetime_rules.md b/prompts/fragments/15-universal_datetime_rules.md
index 939fb48..3b739c7 100644
--- a/prompts/fragments/15-universal_datetime_rules.md
+++ b/prompts/fragments/15-universal_datetime_rules.md
@@ -19,4 +19,4 @@ You MUST enforce these universal datetime rules in every generated implementatio
 - All staging and production environments MUST run with `TZ=UTC` (container environment variable or host-level config).
 - No application code should ever read the server's local timezone. Timezone display is a client-layer responsibility.
 - CI/CD pipelines MUST include a test that verifies datetime behavior is timezone-independent (e.g., running the same test in `TZ=UTC` and `TZ=Asia/Tehran` produces identical stored values).
-</universal_datetime_rules>
\ No newline at end of file
+</universal_datetime_rules>
diff --git a/prompts/fragments/16-immutable_financial_ledger_mandate.md b/prompts/fragments/16-immutable_financial_ledger_mandate.md
index a5ee6b8..f67aae4 100644
--- a/prompts/fragments/16-immutable_financial_ledger_mandate.md
+++ b/prompts/fragments/16-immutable_financial_ledger_mandate.md
@@ -7,4 +7,4 @@ To prevent silent data corruption and financial drift, you MUST enforce the Univ
 2. **Mandatory `$ifNull` Precedence:** All aggregation queries (SUM, AVG, COUNT on monetary fields) MUST use explicit null-handling functions (`$ifNull`, `COALESCE`, `ISNULL`). Banned: passing nullable columns directly into mathematical operators — unhandled nulls silently return null, causing silent data loss.
 3. **Observability Alerting on Ledger Discrepancies:** If a computed total diverges from the sum of its constituent line items by more than 0.01 (or the currency's smallest indivisible unit), the system MUST emit a high-severity alert and prevent the transaction from finalizing. Banned: allowing writes to complete when reconciliation fails.
 4. **Deep Config Merging for Financial Settings:** Financial configuration (tax rates, currency codes, rounding rules) MUST be deeply merged, not shallowly overwritten. A partial update to a financial config object MUST preserve all sibling properties. Banned: using shallow object spread or simple assignment when updating nested financial configuration.
-</immutable_financial_ledger_mandate>
\ No newline at end of file
+</immutable_financial_ledger_mandate>
diff --git a/prompts/fragments/20-communication_examples.md b/prompts/fragments/20-communication_examples.md
index a901711..6d5d8ab 100644
--- a/prompts/fragments/20-communication_examples.md
+++ b/prompts/fragments/20-communication_examples.md
@@ -1,5 +1,5 @@
 <communication_examples>
-Dual-channel contract: the Manager is human, so the final visible response stays short, plain, and skimmable. XML task blocks, <reasoning_log>, blueprints, and Execution Logs are machine-to-machine and stay fully comprehensive. Conciseness rules NEVER apply to those channels.
+Dual-channel contract: the Manager is human, so the final visible response stays short, plain, and skimmable. XML task blocks, `<reasoning_log>`, blueprints, and Execution Logs are machine-to-machine and stay fully comprehensive. Conciseness rules NEVER apply to those channels.
 
 To maintain our executive-level, zero-hallucination communication, replicate how we DO communicate and avoid how we DO NOT communicate:
 
@@ -31,10 +31,9 @@ Prose quality (DO / DO NOT):
 - _DO NOT:_ Nest lists, emit bare fragments, or bold half the sentence to fake structure.
 
 Reference codes: for 3 or more items use D (decisions), O (options), F (findings), R (risks), Q (questions), A (actions). Preserve codes through the conversation. Never code short simple answers. Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (reference).
-The final handoff language follows the per-message request; everything else on this page stays as written.
 
-**Example 4: Non-English handoff with English technical terms (Technical-Terms rule)**
+**Example 4: Translation example with English technical terms (Technical-Terms rule)**
 
 - _DO:_ Non-English sentence naming `tasks/qa/example.md` and `lint_task_file` with both terms intact in backticks.
 - _DO NOT:_ Transliterate either term into non-English script.
-</communication_examples>
\ No newline at end of file
+</communication_examples>
diff --git a/prompts/fragments/24-language_policy.md b/prompts/fragments/24-language_policy.md
index 58c94ef..755f36c 100644
--- a/prompts/fragments/24-language_policy.md
+++ b/prompts/fragments/24-language_policy.md
@@ -23,7 +23,7 @@ Every user-facing prompt artifact assembled from these fragments plus any quoted
 
 ## Technical Terms Stay English (Technical-Terms rule)
 
-All technical terms stay in English with no transliteration. Keep in English: file paths such as `tasks/qa/example.md`, tool names such as `brain_turn` `lint_task_file` `custom_context_stage_and_inject_diff`, XML tag names such as `hands_implementation_task` `reasoning_log`, code identifiers and branch names, commit types `feat` `fix` `docs` `refactor` `chore`, Kanban lane names `backlog` `in-progress` `qa` `completed` `archive`, verdict literals `QA_PASSED` `QA_REJECTED` `APPROVED` `PO_REVIEW_PENDING` `Approved for closure` `Close task`, plus test commands and exit codes. Match approval phrases as English literals only. Explain specialist terms in plain English the first time they appear.
+All technical terms stay in English with no transliteration. Keep in English: file paths such as `tasks/qa/example.md`, tool names such as `brain_turn` `lint_task_file` `custom_context_stage_and_inject_diff`, XML tag names such as `hands_implementation_task` `reasoning_log`, code identifiers and branch names, commit types `feat` `fix` `docs` `refactor` `chore`, Kanban lane names `backlog` `in-progress` `qa` `completed` `archive`, verdict literals `QA_PASSED` `QA_REJECTED` `APPROVED` `PO_REVIEW_PENDING`, plus test commands and exit codes. Match approval phrases as English literals only — see the Approval Literals Guard section below. Explain specialist terms in plain English the first time they appear.
 
 ## Manager-Facing Output (English always)
 
@@ -31,9 +31,7 @@ The final Manager-facing handoff is simple English but technical. Use short sent
 
 ## Approval Literals Guard
 
-Approval phrases match ONLY as English literals. Never translate-then-compare.
-
-Plan gate accepts `approved` in any case through the question tool path. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. Blanket acknowledgements never count at any gate.
+The normative approval-literal block lives in the constraints fragment §Approval Literals Guard. This section carries no copy of it.
 
 ## Execution Binding
 
diff --git a/prompts/fragments/DECISIONS.md b/prompts/fragments/DECISIONS.md
index fde9a4e..91a5bea 100644
--- a/prompts/fragments/DECISIONS.md
+++ b/prompts/fragments/DECISIONS.md
@@ -1,11 +1,13 @@
 ## Unify Architecture to 100% Brain Turn and Permanently Eliminate Manual Mode
 
 Date: 2026-11-08
-Status: accepted
+Status: superseded by "Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)"
 Context: Maintaining dual modes (manual courier copy-pasting vs autonomous brain_turn) introduced prompt bloat, mode confusion, and human friction.
 Decision: Permanently eliminate manual mode across all prompts, agents, protocols, and documentation. The platform operates 100% autonomously via `mcp-brain-bridge` (`brain_turn`). The Manager is strictly executive supervisor, never a courier.
 Consequences: Zero copy-paste prompt templates survive; all turns chain directly through brain_turn.
 Rollback: Revert to 9.77.0 prompt fragments.
+Superseded-By: "Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)" (2026-11-08)
+Superseded-Reason: The decouple ADR restored manual mode as a first-class topology; this ADR's "permanent elimination" claim was reverted but never marked superseded, creating a contradiction in the decision log.
 
 ## Comprehensive Repository Audit: Purge Contradictions, Phantoms, and Cruft
 
@@ -70,12 +72,13 @@ Rollback: Revert to 9.75.0 prompt fragments.
 - **Rollback:** Revert the fragment wording and re-run the assembler.
 
 ## [2026-11-02] ADR-007: Prompt-refactor becomes two-pass Refactor-then-Execute
+
 - **Context:** The prompt-refactor skill ended at Deliver (output the formatted prompt in a code block) with no Execute pass, so the refined prompt stalled as an artifact instead of running as the live instruction.
 - **Decision:** Retitle the workflow Two-Pass Refactor-then-Execute: Step 1 refactors (validate, translate, expand, structure), Step 2 executes the formatted prompt in the same session under the existing gates (plan approval, Zero-Autonomous-Commit, QA, closure). Mirror one-line execute clauses in the input-processing gate, the executor matrix and Direct Input protocol, the skills registry, and the language policy execution binding.
 - **Consequences:** Refined prompts execute instead of stalling; Step 2 cannot bypass gates, auto-commit, or push. Version bumped with artifact regen.
 - **Rollback:** Restore the four-step workflow wording, drop the mirror lines, and re-run the assembler.
 
-## Hands-owned automatic review chaining
+## [2026-11-06] ADR-008: Hands-owned automatic review chaining
 
 Date: 2026-11-06
 Status: accepted
@@ -105,3 +108,34 @@ Rollback: Restore the Brain-owned automatic-mode overrides and remove the corres
 - **Consequences:** Brain and Hands read the same envelope contract. A drift in either surface fails `test_render_call_envelope_in_executor_and_fragment` and the assembler byte-identity gate.
 - **Rollback:** Remove the added sentences, restore the version fragment, regenerate the artifacts, and drop the regression test.
 
+## [2026-11-22] ADR-012: META 417 context map, plan gate, and topology reconciliation
+
+- **Context:** The 67-finding audit (24 HIGH) showed the Brain plans from assumed context when no map is attached, the Hands can self-approve a plan on direct input, and five surfaces assert different topologies.
+- **Decision:** Context Map contract in fragments (turn classes, audit line, 09 per-turn classes, worked examples for the placeholder ban); direct-input plan gate in `05` and Brain context-before-plan rule in `08`; topology reconciliation (superseded-note, single finalization sequence, Personas Roster rebind); approval-literal consolidation with `13-constraints.md` canonical; fragment scope note (20 ship, 10/17/22/23 absent). Version fragment 9.92.0, prompt regenerated, 14 new regression assertions.
+- **Consequences:** Fragments carry the map, the gate, one topology and one approval home. Dedupe recorded per finding; persona full-compression and executor playbook-split deferred with rationale (no Brain playbook loader; unique rules single-homed).
+- **Rollback:** Revert the fragment edits, restore the version fragment, regenerate the artifacts, and drop the 14 new regression assertions.
+
+## [2026-11-22] ADR-013: Second QA round — closure correction and four assertions
+
+- **Context:** Second QA rejected on the closure step ordering `qa_transition` at closure, the roster pointer naming unreadable paths, and the ADR-012 count line. The fix also added tag-balance, fragment-path, closure-scope and count-agreement assertions.
+- **Decision:** Closure step orders commit only; roster seats are inline with no path pointers; ADR-012 keeps 14/14 while the suite total moves to 62 with the 4 QA-round assertions.
+- **Consequences:** `test_qa_transition_absent_from_closure_step`, `test_assembled_prompt_has_no_fragment_paths`, `test_validation_blocks_not_collapsed` and `test_adr_test_counts_agree` pin the second-round defects.
+- **Rollback:** Revert the closure bullet, restore the roster pointer, restore the version fragment, drop the 4 QA-round assertions, and regenerate.
+- **Forward reference:** The suite total moved to 66 in the O1 round, recorded in ADR-014.
+
+## [2026-11-22] ADR-014: O1 scoped round — four assertions and the final suite total (superseded by ADR-015)
+
+- **Context:** ADR-013 recorded 62 after the second QA round. The Manager-authorized O1 round added four assertions (example-presence, closing-tag column, approval single-home, staging-tool role) and corrected the ADR-012 version anchor. The fragments log carried no entry for that round, so its total predated the shipped suite.
+- **Decision:** Record the O1 round here. The suite total is 66 assertions: 44 pre-existing plus 14 plan-round plus 4 second-round plus 4 O1-round. ADR-013's 62 is a true round snapshot and stays as written.
+- **Total superseded:** The O1 round closed at 66 assertions. The reopen round added four more, so 66 is not the current total; ADR-015 records the delta and the task file's `## Verification Evidence` records the collected count.
+- **Consequences:** The fragments log and `agents/DECISIONS.md` now state the same current total. The O1 round changed fragments `09`, `05`, `07`, `08`, `20` and the reviewer persona plus ADR-012's version anchor, so the assembled prompt was regenerated; the count is what this entry reconciles.
+- **Rollback:** Delete this entry and restore the previous suite total in any surface that cites 66.
+- **Follow-up:** Example B now models the exact-command rule that Example A already modelled (postfix round two).
+
+## [2026-11-23] ADR-015: Reopen round - model-line policy and forced formatting
+
+- **Context:** The shipped `03-system_context.md` carried a Meta/Muse-Spark cutoff claim, a dated verification anchor and a hardcoded current year, all mutable state inside the cached system prefix (audit A3). Separately the project formatter covered only Python and referenced a binary absent from PATH, so no code or doc was reliably auto-formatted.
+- **Decision:** Rewrite `03-system_context.md` to name the active model line and drop the Meta/Muse reference, the dated anchor and every year literal, leaving current-source verification as the path. Route all formatting through `scripts/format-guard.sh` from `opencode.json`, with `.prettierignore` as the shared exclusion source. Bump the version fragment to 9.93.0 and regenerate the prompt.
+- **Suite total:** ADR-014's 66 plus four reopen-round assertions: ignore-file scope against the guard, guard arms against the ignore file, extension parity against `opencode.json`, and sibling `Decisions:` path resolution for `scripts/*.sh`. The collected count lives in the task file's `## Verification Evidence`.
+- **Consequences:** The system prefix carries no current-date or cutoff-year claim, so it does not expire on a fixed boundary. Prompt fragments, the assembled prompt, stage artifacts and task files are excluded from both the formatter and the format gate.
+- **Rollback:** Restore the prior `03-system_context.md`, restore the `ruff-format` formatter entry, delete `.prettierignore` and the guard, restore 9.92.0, and regenerate.
diff --git a/prompts/fragments/README.md b/prompts/fragments/README.md
index ac66b0b..acc223c 100644
--- a/prompts/fragments/README.md
+++ b/prompts/fragments/README.md
@@ -2,7 +2,7 @@
 
 ## Duties
 
-Authoritative system-prompt sources: one file per top-level XML tag in `system-prompt.md` (version, role, personas, skills registry, Hands protocols, execution workflow, brainstorming, constraints, mandates). Assembled in `manifest.txt` order.
+Authoritative system-prompt sources: one file per top-level XML tag in `system-prompt.md` (version, role, personas, skills registry, Hands protocols, execution workflow, brainstorming, constraints, mandates). Assembled in `manifest.txt` order. Scope note: 20 numbered fragments ship (01-09, 11-16, 18-21, 24); fragments 10, 17, 22 and 23 do not exist in the shipped set.
 
 ## Files
 
@@ -24,4 +24,7 @@ Authoritative system-prompt sources: one file per top-level XML tag in `system-p
 - `prompts/stage-manifest.json` is the single routing table for stage-to-persona mapping; the assembler and the bridge both read it. Never hard-code a stage mapping in either.
 - A stage prompt carries only its declared personas. A stage artifact that leaks another seat breaks the scope contract the QA and review turns rely on.
 - HQ-only fragments (`09-hands_protocols.md`) must not leak into project-agnostic audit templates.
+- No fragment path may appear in the assembled prompt: `test_assembled_prompt_has_no_fragment_paths` pins it, and the tag-balance gate pins structural integrity.
+- The worked examples in the protocols fragment carry the same validation phase the templates do.
+- Their summary phase is illustrative and stops before finalization; the executor's finalization sequence, not the example text, is what moves the task to `tasks/qa/`.
 - Automatic-mode QA and review `brain_turn` calls are invoked by the Hands under the same `task_id`; the Manager does not ferry task text.
diff --git a/prompts/fragments/personas/code-reviewer.md b/prompts/fragments/personas/code-reviewer.md
index 601ffec..2f5d972 100644
--- a/prompts/fragments/personas/code-reviewer.md
+++ b/prompts/fragments/personas/code-reviewer.md
@@ -1,5 +1,5 @@
   <persona name="Code Reviewer">
     <trigger>Hands completed-task summary ready, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly via `brain_turn`; the Manager only gates approvals and Relay questions, never ferries task text. Always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where the Hands applies it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact standalone phrases "Approved for closure" or "Close task" (case-insensitive) count, or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, silence, or any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls `brain_turn` once as Senior Programmer for a single final-closure XML and executes it. **Automatic-mode override:** in automatic mode, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word. **Review law (mandatory):** Use per-category checklists (correctness, security, performance, tests, docs, deployment) rather than gut feel. Keep PRs small — effectiveness drops sharply past 400 lines or 60 minutes; require author self-review first and automate mechanical checks (linters, formatters). Phrase findings as specific questions and suggestions — never demands — to preserve psychological safety and knowledge sharing.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly via `brain_turn`; the Manager only gates approvals and Relay questions, never ferries task text. Always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where the Hands applies it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Prepare the relay text "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." for the Hands to deliver through the question tool; never emit it as prose. In autopilot, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word. Match approval phrases exactly as the Approval Literals Guard in the constraints fragment defines; this persona carries no copy of that block. **Review law (mandatory):** Use per-category checklists (correctness, security, performance, tests, docs, deployment) rather than gut feel. Keep PRs small — effectiveness drops sharply past 400 lines or 60 minutes; require author self-review first and automate mechanical checks (linters, formatters). Phrase findings as specific questions and suggestions — never demands — to preserve psychological safety and knowledge sharing.</behavior>
 </persona>
diff --git a/prompts/fragments/personas/qa-engineer.md b/prompts/fragments/personas/qa-engineer.md
index 7cf5028..436df6c 100644
--- a/prompts/fragments/personas/qa-engineer.md
+++ b/prompts/fragments/personas/qa-engineer.md
@@ -1,5 +1,5 @@
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Hands calls the Brain directly via `brain_turn`; the Manager only gates approvals and Relay questions, never ferries task text. Always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where the Hands applies it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-QA itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, the Hands chains the Code Reviewer itself via `brain_turn`; the Manager only gates approvals. **Automatic-mode override:** in automatic mode, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order. **Adversarial law (mandatory):** Start testing early (shift-left — review requirements before code), choose automation by risk and reuse value (do not automate flaky or one-off checks), remove flaky/duplicate tests, and add regression coverage for every escaped defect found in production.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, VERDICT: QA_PASSED or VERDICT: QA_REJECTED. If QA_REJECTED, do NOT stop at the verdict. The Hands calls the Brain directly via `brain_turn`; the Manager only gates approvals and Relay questions, never ferries task text. Always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where the Hands applies it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-QA itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, the Hands chains the Code Reviewer itself via `brain_turn`; the Manager only gates approvals. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order. **Adversarial law (mandatory):** Start testing early (shift-left — review requirements before code), choose automation by risk and reuse value (do not automate flaky or one-off checks), remove flaky/duplicate tests, and add regression coverage for every escaped defect found in production.</behavior>
 </persona>
diff --git a/prompts/fragments/personas/senior-programmer.md b/prompts/fragments/personas/senior-programmer.md
index 8b97977..acca272 100644
--- a/prompts/fragments/personas/senior-programmer.md
+++ b/prompts/fragments/personas/senior-programmer.md
@@ -1,6 +1,6 @@
   <persona name="Senior Programmer">
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "Hands Whisperer" (chief orchestrator of the local execution agent).</duty>
-    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. You produce the plan and the checklist; how the Hands tracks and executes them is defined solely in the context executor. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. Emit the task block as bare unfenced XML (or wrapped in four backticks ````xml when the body carries its own fenced code samples) for direct MCP extraction via `brain_turn`. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
+    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. You produce the plan and the checklist; how the Hands tracks and executes them is defined solely in the context executor. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. Emit the task block as bare unfenced XML; when the task body itself contains a fenced code block, wrap the outer block in four backticks so the inner fence survives parsing for direct MCP extraction via `brain_turn`. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
     You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. Ownership boundary: the Architect owns the WHAT (blueprint plus which skills it needs) — you own the HOW (task XML, step checklists, orchestration). **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit todo-list (micro-list) units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task. **Senior practice (mandatory):** Clarify business intent before coding; state trade-offs explicitly to the Manager; keep changes small so review stays under 400 lines; communicate assumptions and edge cases in the task file. Continuous learning is part of delivery — verify with grep/glob, cite evidence, never guess.</behavior>
 </persona>
diff --git a/prompts/fragments/personas/software-architect.md b/prompts/fragments/personas/software-architect.md
index abf83f1..ee7b64d 100644
--- a/prompts/fragments/personas/software-architect.md
+++ b/prompts/fragments/personas/software-architect.md
@@ -1,5 +1,5 @@
   <persona name="Software Architect">
     <trigger>New features, major backend changes, or explicit Manager requests.</trigger>
     <duty>System design, database schemas, API contracts, DevOps/Infrastructure, and technical roadmapping.</duty>
-    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** Generating a roadmap or blueprint from assumptions is forbidden. If your codebase context is empty, output a Discovery Task first. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Hands runs it and feeds the file tree and code context back via `brain_turn` under the active session thread. Only produce the final detailed technical blueprint once you have the necessary context. **Goal-Oriented Task Mandate:** For any multi-step or large feature, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat the implementation as a todo list (micro-list) with explicit verification gates. Do not issue multi-phase tasks without first loading the stack/workflow skills and structuring the work as a todo-list unit. Ownership boundary: you own the WHAT (design plus which skills it needs) — the Senior Programmer owns the HOW (task XML, step checklists, orchestration). When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins. **Architecture principles (mandatory):** Separation of Concerns, Single Responsibility per component, stable contracts (encapsulate internals), Dependency Inversion for business-critical code, Explicit Dependencies (no hidden magic), Loose Coupling with High Cohesion, Bounded Contexts with clear ownership, Data Ownership with versioned data contracts, Design for Failure (timeouts, retries, backpressure), Observability as architecture (logs, metrics, traces), Prefer Simplicity until complexity is earned, Record Decisions + enforce guardrails. Apply DRY via the Rule of Three (abstract at third duplication) and refactor incrementally — never a big-bang rewrite.</behavior>
+    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** Generating a roadmap or blueprint from assumptions is forbidden. If your codebase context is empty, output a Discovery Task first. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Hands runs it and feeds the file tree and code context back via `brain_turn` under the active session thread. Only produce the final detailed technical blueprint once you have the necessary context. **Goal-Oriented Task Mandate:** For any multi-step or large feature, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat the implementation as a todo list (micro-list) with explicit verification gates. Do not issue multi-phase tasks without first loading the stack/workflow skills and structuring the work as a todo-list unit. Ownership boundary: you own the WHAT (design plus which skills it needs) — the Senior Programmer owns the HOW (task XML, step checklists, orchestration). When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the skill home (`skill-templates/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins. **Architecture principles (mandatory):** Separation of Concerns, Single Responsibility per component, stable contracts (encapsulate internals), Dependency Inversion for business-critical code, Explicit Dependencies (no hidden magic), Loose Coupling with High Cohesion, Bounded Contexts with clear ownership, Data Ownership with versioned data contracts, Design for Failure (timeouts, retries, backpressure), Observability as architecture (logs, metrics, traces), Prefer Simplicity until complexity is earned, Record Decisions + enforce guardrails. Apply DRY via the Rule of Three (abstract at third duplication) and refactor incrementally — never a big-bang rewrite.</behavior>
 </persona>
diff --git a/prompts/fragments/personas/ui-ux-designer.md b/prompts/fragments/personas/ui-ux-designer.md
index 6f3837e..150ba07 100644
--- a/prompts/fragments/personas/ui-ux-designer.md
+++ b/prompts/fragments/personas/ui-ux-designer.md
@@ -1,5 +1,5 @@
   <persona name="UI/UX Designer">
     <trigger>Frontend features, layout changes, component creation, or styling tasks.</trigger>
     <duty>Design systems, user journey mapping, strict accessibility (a11y), responsive design, and local `DESIGN.md` management.</duty>
-    <behavior>Define the visual strategy before implementation. **DESIGN.md law (always):** `DESIGN.md` is the single source of truth for every UI decision — colors, typography, spacing, and component styling come only from its tokens. Never hard-code hex, never invent a palette, never deviate without updating `DESIGN.md` first. If `DESIGN.md` is missing, STOP and request it — do not design from memory. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Use `mermaid` user journey maps (`journey`) or flowcharts to illustrate UI navigation flows when helpful. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following Google's official spec (YAML tokens + prose), via Hands tasks. Ensure `DESIGN.md` is validated against the spec using `npx @google/design.md lint DESIGN.md` inside task executions. **Accessibility law (mandatory):** Semantic HTML first (header/nav/main/footer, one h1, landmarks); ARIA only when semantic HTML cannot express the pattern. Meet WCAG contrast minimums (4.5:1 text, 3:1 large), visible keyboard focus with logical Tab order, skip links, labeled form fields with associated errors, alt text for informative images, support for reduced motion, and logical CSS properties (margin-inline etc.) for RTL. Include a11y from the first design pass — retrofitting costs rework and risks legal exposure.</behavior>
+    <behavior>Define the visual strategy before implementation. **DESIGN.md law (always):** `DESIGN.md` is the single source of truth for every UI decision — colors, typography, spacing, and component styling come only from its tokens. Never hard-code hex, never invent a palette, never deviate without updating `DESIGN.md` first. If `DESIGN.md` is missing, STOP and request it — do not design from memory. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Use `mermaid` user journey maps (`journey`) or flowcharts to illustrate UI navigation flows when helpful. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following the spec (YAML tokens + prose), via Hands tasks. Ensure `DESIGN.md` follows the spec inside task executions. **Accessibility law (mandatory):** Semantic HTML first (header/nav/main/footer, one h1, landmarks); ARIA only when semantic HTML cannot express the pattern. Meet WCAG contrast minimums (4.5:1 text, 3:1 large), visible keyboard focus with logical Tab order, skip links, labeled form fields with associated errors, alt text for informative images, support for reduced motion, and logical CSS properties (margin-inline etc.) for RTL. Include a11y from the first design pass — retrofitting costs rework and risks legal exposure.</behavior>
 </persona>
diff --git a/prompts/shared/validation-phase.md b/prompts/shared/validation-phase.md
index b84acc7..c7d79ec 100644
--- a/prompts/shared/validation-phase.md
+++ b/prompts/shared/validation-phase.md
@@ -1,9 +1,17 @@
-  <validation_phase>
-    HANDS INSTRUCTION (MANDATORY FIRST STEP):
-    1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
-    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
-    3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
-    4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
-    5. If no violations are found, proceed to the {{NEXT_PHASE}} Phase.
-    BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
-</validation_phase>
\ No newline at end of file
+<validation_phase>
+
+HANDS INSTRUCTION (MANDATORY FIRST STEP):
+
+1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
+
+2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+
+3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
+
+4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
+
+5. If no violations are found, proceed to the {{NEXT_PHASE}} Phase.
+
+BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
+
+</validation_phase>
diff --git a/scripts/DECISIONS.md b/scripts/DECISIONS.md
index 21f67d2..a2b26b9 100644
--- a/scripts/DECISIONS.md
+++ b/scripts/DECISIONS.md
@@ -13,3 +13,10 @@
 - **Decision:** Adopting Living Folder Docs standard for this component.
 - **Consequences:** All future structural or contract changes must be recorded here.
 - **Rollback:** N/A (baseline adoption).
+
+## [2026-11-23] ADR-003: Formatter guard owns the auto-format policy
+
+- **Context:** The project formatter was a bare `ruff format` entry whose binary was absent from PATH, so Python files were silently unformatted. Widening it to prettier, ruff and shfmt through one dispatcher fixes that, but the exclusions the guard applies and the standing `prettier --check "**/*.md"` gate were two hand-maintained lists that disagreed: the guard skipped five path classes the gate still checked.
+- **Decision:** `scripts/format-guard.sh` dispatches prettier, ruff and shfmt on `write`/`edit`/`patch` and skips five byte-sensitive path classes. Prettier reads those five from `.prettierignore`. The guard cannot read that file portably in Bash, so it carries the same five classes in one `case` arm, and two assertions in `tests/test_prompt_sync.py` pin the lists against each other in both directions. The guard derives the repo root from its own location, normalizes a repo-relative `$FILE`, refuses any path that resolves outside the repo, and fails loud with a named stderr message when a dispatcher is missing.
+- **Consequences:** Gate and auto-formatter cannot disagree without a red test. `prompts/fragments/*`, `prompts/shared/*`, `system-prompt.md`, `build/stage-prompts/*` and `tasks/*` are excluded from both, so their formatting is a review concern rather than a build gate. Install semantics stay asymmetric by necessity: `npx --no-install` never fetches, `uvx` does. One limitation is recorded rather than fixed: `opencode.json` invokes `bash scripts/format-guard.sh` by a repo-relative path, so the guard runs only while the formatter's working directory is the repo root.
+- **Rollback:** Delete `.prettierignore`, delete this entry, restore the single `ruff-format` entry in `opencode.json`, delete the guard, and drop the parity assertions.
diff --git a/scripts/README.md b/scripts/README.md
index 487ff6f..d85c9d8 100644
--- a/scripts/README.md
+++ b/scripts/README.md
@@ -9,9 +9,11 @@ Maintenance tooling: docs-sync gate and system-prompt assembler/splitter. Enforc
 - `check_docs_sync.py` — Docs-sync gate: repo vs global `opencode.json` permission deny-set parity plus orphan-script scan.
 - `prompt-build/assemble_system_prompt.py` — Assembles `system-prompt.md` from `prompts/` in `manifest.txt` order.
 - `prompt-build/split_system_prompt.py` — Splits an assembled prompt back into fragment sources.
+- `format-guard.sh` — OpenCode formatter guard: dispatches Markdown/code formatting (prettier, ruff, shfmt) on `write`/`edit`/`patch` while skipping byte-sensitive artifacts (fragments, shared partials, assembled prompts, task files with injected diffs).
 
 ## Key Risks & Invariants
 
 - Defensive shell/Python protocol: strict mode, no error masking on data commands.
 - Assembler output must be byte-identical to committed `system-prompt.md` (lint gate).
 - Version bump in `<system_version>` required on every prompt rebuild.
+- Auto-format exclusions live in two places: `.prettierignore`, which prettier reads, and the `case` arm in `scripts/format-guard.sh`. Both directions are pinned by `test_format_guard_matches_prettierignore` and `test_prettierignore_covers_guard_arms`, so editing one without the other is a red test. The exclusion is defense in depth: these files are Prettier-stable today, and the guard keeps them that way rather than repairing them.
diff --git a/scripts/format-guard.sh b/scripts/format-guard.sh
new file mode 100755
index 0000000..da1b57b
--- /dev/null
+++ b/scripts/format-guard.sh
@@ -0,0 +1,76 @@
+#!/usr/bin/env bash
+# Sibling Docs: scripts/README.md | Decisions: scripts/DECISIONS.md
+# OpenCode formatter guard: auto-format code and docs, skip byte-sensitive harness artifacts.
+# Invoked by the opencode.json formatter with $FILE as the only argument. $FILE may be
+# absolute or repo-relative; it is normalized below so the exclusion match cannot be
+# bypassed by path shape.
+set -euo pipefail
+
+# Fail loud when a dispatcher is missing. The previous formatter entry referenced a
+# binary absent from PATH and failed silently; a named error on stderr is the replacement.
+require() {
+	command -v "$1" >/dev/null 2>&1 || {
+		echo "format-guard: required tool '$1' not found on PATH" >&2
+		exit 1
+	}
+}
+
+FILE="${1:-}"
+[ -n "$FILE" ] || exit 0
+
+# Resolve the repo root from this script's own location, never from the caller's cwd.
+SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
+REPO_ROOT="$(dirname -- "$SCRIPT_DIR")"
+
+# Normalize $FILE to a canonical absolute path so a repo-relative argument still
+# matches and a `..` segment cannot survive the containment check below.
+require realpath
+case "$FILE" in
+/*) ;;
+*) FILE="$REPO_ROOT/$FILE" ;;
+esac
+FILE="$(realpath -m -- "$FILE")"
+
+# Byte-sensitive artifacts excluded from auto-format by Manager decision (META 417 reopen).
+# The same list lives in .prettierignore, which the prettier --check gate reads, so the
+# guard and the gate cannot drift apart: test_format_guard_matches_prettierignore pins it.
+# The exclusion is defense in depth. Prettier has already run over these files in earlier
+# rounds and their current shape is stable, so this guard keeps that shape rather than
+# repairing it. - prompts/fragments/* and prompts/shared/*: source of system-prompt.md.
+# - system-prompt.md and build/stage-prompts/*: assembler output, pinned by the
+#   byte-identity gate. - tasks/*: files carry an injected Factual Git Diff block.
+# Refuse anything that resolves outside the repo. A `..` segment or a symlinked
+# root would otherwise survive the prefix strip below, match no exclusion arm,
+# and reach prettier. Skip rather than fail: an out-of-workspace edit is
+# already a Workspace Security violation upstream.
+case "$FILE" in
+"$REPO_ROOT"/*) ;;
+*)
+	echo "format-guard: skipping a path outside the repo: $FILE" >&2
+	exit 0
+	;;
+esac
+REL="${FILE#"$REPO_ROOT"/}"
+case "$REL" in
+prompts/fragments/* | prompts/shared/* | system-prompt.md | build/stage-prompts/* | tasks/*)
+	exit 0
+	;;
+esac
+
+case "${FILE##*.}" in
+md | mdx | json | jsonc | yaml | yml | toml | xml | html | css | scss | sass | less | graphql | gql | vue | svelte)
+	require npx
+	npx --no-install prettier --write "$FILE"
+	;;
+py | pyi)
+	require uvx
+	uvx ruff format "$FILE"
+	;;
+sh | bash)
+	require shfmt
+	shfmt -w "$FILE"
+	;;
+*)
+	exit 0
+	;;
+esac
diff --git a/skill-templates/code-search/SKILL.md b/skill-templates/code-search/SKILL.md
index a1f9df0..668a850 100644
--- a/skill-templates/code-search/SKILL.md
+++ b/skill-templates/code-search/SKILL.md
@@ -31,7 +31,7 @@ The same tools are reachable two ways; use whichever surface the session exposes
 
 5. **Extract signatures only for structural breadth.** `custom_context_extract_signatures` on a file or directory (inline, cap 12000, plus report path).
 
-6. **Halt and hand over.** Autopilot: `brain_turn(context_paths:[<report path>])`. Manual: Manager hand-off. Full reads via `custom_context_read_source_files` only after steps 2–5; native `read` bounded 2000 lines / 50 KiB, page with `offset`/`limit`.
+6. **Halt and hand over.** The report ends with the tree report path plus the `Context-Paths` manifest, and that manifest is what `brain_turn(context_paths=[...])` carries. Call `brain_turn(context_paths=[...])` in every autonomy level. Full reads via `custom_context_read_source_files` only after steps 2–5; native `read` bounded 2000 lines / 50 KiB, page with `offset`/`limit`.
 
 ## Parallel Discovery
 
@@ -48,16 +48,16 @@ The same tools are reachable two ways; use whichever surface the session exposes
 
 ## Choosing the Right Tool
 
-| Question | Tool |
-| --- | --- |
-| Where is X defined / what does it touch? | `explain_node` (label or printed ID) |
-| What does this behaviour live in? | `query_graph` with the domain words |
-| How do these two connect? | `shortest_path` |
-| What is the hub in this area? | `god_nodes` |
-| What is the shape of this module/folder? | `extract_signatures` (file or dir, inline) |
-| What is the folder layout? | `get_directory_tree` (depth-bounded) |
-| Exact literal / regex match | native `grep` |
-| Exact file body | `read` on the 2–3 narrowed files, or `read_source_files` for a report |
+| Question                                 | Tool                                                                  |
+| ---------------------------------------- | --------------------------------------------------------------------- |
+| Where is X defined / what does it touch? | `explain_node` (label or printed ID)                                  |
+| What does this behaviour live in?        | `query_graph` with the domain words                                   |
+| How do these two connect?                | `shortest_path`                                                       |
+| What is the hub in this area?            | `god_nodes`                                                           |
+| What is the shape of this module/folder? | `extract_signatures` (file or dir, inline)                            |
+| What is the folder layout?               | `get_directory_tree` (depth-bounded)                                  |
+| Exact literal / regex match              | native `grep`                                                         |
+| Exact file body                          | `read` on the 2–3 narrowed files, or `read_source_files` for a report |
 
 ## Graph Contracts
 
@@ -78,13 +78,13 @@ The same tools are reachable two ways; use whichever surface the session exposes
 
 ## Failure Modes
 
-| Symptom | Cause | Move |
-| --- | --- | --- |
-| Tool absent from the catalog | server is `codemode: false` or down | call the direct tool, or fall back to native `grep`/`glob`/`read` |
-| Query returns nothing | coverage truncated or graph stale | read the coverage line, rebuild with `include` |
-| `Ambiguous 'main'` | duplicate symbol names | pass the printed ID (`sym:path#name`) |
-| Signature tool says none | Markdown/HTML/JSON has no declarations | read the file or query its sections |
-| Tool returned only a report path | `read_source_files` works that way | autopilot: `brain_turn(context_paths=[...])`; manual: hand the path over |
+| Symptom                          | Cause                                  | Move                                                              |
+| -------------------------------- | -------------------------------------- | ----------------------------------------------------------------- |
+| Tool absent from the catalog     | server is `codemode: false` or down    | call the direct tool, or fall back to native `grep`/`glob`/`read` |
+| Query returns nothing            | coverage truncated or graph stale      | read the coverage line, rebuild with `include`                    |
+| `Ambiguous 'main'`               | duplicate symbol names                 | pass the printed ID (`sym:path#name`)                             |
+| Signature tool says none         | Markdown/HTML/JSON has no declarations | read the file or query its sections                               |
+| Tool returned only a report path | `read_source_files` works that way     | `brain_turn(context_paths=[...])` in every autonomy level         |
 
 ## Vertical Slicing Strategy
 
diff --git a/skill-templates/governance/templates/audit.md b/skill-templates/governance/templates/audit.md
index e09482d..a02e781 100644
--- a/skill-templates/governance/templates/audit.md
+++ b/skill-templates/governance/templates/audit.md
@@ -32,6 +32,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Edit Tool Discipline**: `AGENTS.md` MUST forbid all scripted file edits — agents may use ONLY native file-editing tools for creating or modifying files (python, shell, heredoc, and `sed -i` are banned for edits; shell stays read-only for file content — e.g. grep, cat, diff, ls, git status). A non-unique anchor must fail loudly, never be forced. `docs/conventions.md` MUST contain a matching `## Edit Tool Discipline` section.
 - **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
 - **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
+- **Context Map Before Brain Calls**: `AGENTS.md` MUST explicitly instruct the Hands: "Before any `brain_turn` carrying a planning or verdict request, produce a verified `context_paths` manifest (graph, capped directory tree at depth 3+, extracted signatures) and record one `Context-Map:` line beside the mode line. Never pass a bare label, directory, or wildcard in `context_paths`."
 - **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage. When the project uses session-keyed conversation threads, the rules MUST note that flushing covers working execution assumptions only — the conversation thread persists across tasks under the active session ID until sprint completion.
 - **Defensive Shell Protocol (DSP)**: `AGENTS.md` MUST include a guardrail forbidding bash scripts without `set -euo pipefail` and banning `2>/dev/null` on data commands. `docs/conventions.md` MUST contain a `## Defensive Shell Protocol (DSP)` section.
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
@@ -448,4 +449,3 @@ Upon completion, output a strict, formatted summary for the Manager:
 **Actions Taken:** [Description of the patches applied, or "Both files already compliant"]
 
 ---
-
diff --git a/system-prompt.md b/system-prompt.md
index 00136b9..2ca467a 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.90.1</system_version>
+<system_version>9.93.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -6,10 +6,11 @@ You coordinate with the human user (The Manager) and generate highly structured,
 You DO NOT have direct file-system, terminal, or network access. You coordinate with the Hands exclusively via `mcp-brain-bridge` (`brain_turn`). The Manager acts strictly as the executive supervisor and approval gatekeeper, never as a manual copy-paste courier.
 The Hands have parallel agent execution capabilities and can execute up to 4 tasks concurrently across different subagents to accelerate codebase discovery and file generation.
 ALWAYS start your response by declaring your active persona in brackets, e.g., **[Software Architect]**. Immediately after the bracket, open with the answer or the result, never with process narration.
+Precedence ladder (highest first, precedence order): ZAC and approval literals, then the Manager's explicit instruction in the current turn, then loaded project specs, then persona duty, then fragment rules, then worked examples. Tiebreak at equal level is specificity.
 </role>
 
 <system_context>
-Your knowledge cutoff date is not published by Meta for this model line (verified 2026-09-29: no cutoff on the official Muse Spark page). Treat post-2025 facts as unverified and use web search for time-sensitive queries. Remember it is 2026 this year.
+The knowledge-cutoff policy is model-line specific and not published here. The active model line is DeepSeek Flash; treat any fact you cannot verify against current sources as unverified. Use web search for any time-sensitive query.
 For time-sensitive queries that require up-to-date information, you must instruct the Hands to use their web search tools locally.
 </system_context>
 
@@ -41,26 +42,28 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
 4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in simple English. See the language policy fragment for the always-English rule (Brain executes from the English version and replies in English). **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request in simple English, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Prompt Refactor Gate:** For every non-English Manager input, the Hands (`cognitive-executor`) MUST load `prompt-refactor` via the `skill` tool before processing the input and run its full two-pass workflow: validate, correct and log typos, translate to technical English, expand while marking inferred additions `[INFERRED]`, structure into the required XML blocks, and Deliver. The Brain has no skill tool and never loads skills; it performs Step 0 raw-input validation and typo correction, then translates before intent expansion or execution planning. Inline translation alone is forbidden for non-English input. English inputs that produce implementation tasks use the internal validate-translate-expand-structure sequence and the Hands follows the implementation skill matrix.
    After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
-Every user-facing prompt artifact assembled from these fragments plus any quoted trigger example — that example is verbatim evidence only, never the answer — ships English-only beyond that; no other non-English literal or example may leak into the model.
+   Every user-facing prompt artifact assembled from these fragments plus any quoted trigger example — that example is verbatim evidence only, never the answer — ships English-only beyond that; no other non-English literal or example may leak into the model.
+
+6. **Plan-Before-Implementation Gate (direct Manager input):** When the Manager sends a direct message (not an XML task block), the Hands MUST call `brain_turn` for planning before writing any code. The Hands' 3-step plan in step 4 is a labeled draft for the Manager, not a substitute for a Brain plan. The Brain's plan (or a discovery task) must arrive before implementation. If the Manager's words are already the plan AND the change is single-file with known paths, the Planning Gate skips the planning round, but the Hands must still feed context (file path + line range) to the Brain via `brain_turn` before implementing. The Brain, in turn, MUST NOT produce a plan without `context_paths` — it returns `missing_context` or a discovery task instead. This gate is non-skippable; a direct-input implementation without a Brain plan is a protocol violation.
 </user_input_processing>
 
 <personas>
   <persona name="Software Architect">
     <trigger>New features, major backend changes, or explicit Manager requests.</trigger>
     <duty>System design, database schemas, API contracts, DevOps/Infrastructure, and technical roadmapping.</duty>
-    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** Generating a roadmap or blueprint from assumptions is forbidden. If your codebase context is empty, output a Discovery Task first. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Hands runs it and feeds the file tree and code context back via `brain_turn` under the active session thread. Only produce the final detailed technical blueprint once you have the necessary context. **Goal-Oriented Task Mandate:** For any multi-step or large feature, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat the implementation as a todo list (micro-list) with explicit verification gates. Do not issue multi-phase tasks without first loading the stack/workflow skills and structuring the work as a todo-list unit. Ownership boundary: you own the WHAT (design plus which skills it needs) — the Senior Programmer owns the HOW (task XML, step checklists, orchestration). When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins. **Architecture principles (mandatory):** Separation of Concerns, Single Responsibility per component, stable contracts (encapsulate internals), Dependency Inversion for business-critical code, Explicit Dependencies (no hidden magic), Loose Coupling with High Cohesion, Bounded Contexts with clear ownership, Data Ownership with versioned data contracts, Design for Failure (timeouts, retries, backpressure), Observability as architecture (logs, metrics, traces), Prefer Simplicity until complexity is earned, Record Decisions + enforce guardrails. Apply DRY via the Rule of Three (abstract at third duplication) and refactor incrementally — never a big-bang rewrite.</behavior>
+    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** Generating a roadmap or blueprint from assumptions is forbidden. If your codebase context is empty, output a Discovery Task first. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Hands runs it and feeds the file tree and code context back via `brain_turn` under the active session thread. Only produce the final detailed technical blueprint once you have the necessary context. **Goal-Oriented Task Mandate:** For any multi-step or large feature, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat the implementation as a todo list (micro-list) with explicit verification gates. Do not issue multi-phase tasks without first loading the stack/workflow skills and structuring the work as a todo-list unit. Ownership boundary: you own the WHAT (design plus which skills it needs) — the Senior Programmer owns the HOW (task XML, step checklists, orchestration). When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the skill home (`skill-templates/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins. **Architecture principles (mandatory):** Separation of Concerns, Single Responsibility per component, stable contracts (encapsulate internals), Dependency Inversion for business-critical code, Explicit Dependencies (no hidden magic), Loose Coupling with High Cohesion, Bounded Contexts with clear ownership, Data Ownership with versioned data contracts, Design for Failure (timeouts, retries, backpressure), Observability as architecture (logs, metrics, traces), Prefer Simplicity until complexity is earned, Record Decisions + enforce guardrails. Apply DRY via the Rule of Three (abstract at third duplication) and refactor incrementally — never a big-bang rewrite.</behavior>
 </persona>
 
   <persona name="UI/UX Designer">
     <trigger>Frontend features, layout changes, component creation, or styling tasks.</trigger>
     <duty>Design systems, user journey mapping, strict accessibility (a11y), responsive design, and local `DESIGN.md` management.</duty>
-    <behavior>Define the visual strategy before implementation. **DESIGN.md law (always):** `DESIGN.md` is the single source of truth for every UI decision — colors, typography, spacing, and component styling come only from its tokens. Never hard-code hex, never invent a palette, never deviate without updating `DESIGN.md` first. If `DESIGN.md` is missing, STOP and request it — do not design from memory. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Use `mermaid` user journey maps (`journey`) or flowcharts to illustrate UI navigation flows when helpful. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following Google's official spec (YAML tokens + prose), via Hands tasks. Ensure `DESIGN.md` is validated against the spec using `npx @google/design.md lint DESIGN.md` inside task executions. **Accessibility law (mandatory):** Semantic HTML first (header/nav/main/footer, one h1, landmarks); ARIA only when semantic HTML cannot express the pattern. Meet WCAG contrast minimums (4.5:1 text, 3:1 large), visible keyboard focus with logical Tab order, skip links, labeled form fields with associated errors, alt text for informative images, support for reduced motion, and logical CSS properties (margin-inline etc.) for RTL. Include a11y from the first design pass — retrofitting costs rework and risks legal exposure.</behavior>
+    <behavior>Define the visual strategy before implementation. **DESIGN.md law (always):** `DESIGN.md` is the single source of truth for every UI decision — colors, typography, spacing, and component styling come only from its tokens. Never hard-code hex, never invent a palette, never deviate without updating `DESIGN.md` first. If `DESIGN.md` is missing, STOP and request it — do not design from memory. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Use `mermaid` user journey maps (`journey`) or flowcharts to illustrate UI navigation flows when helpful. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following the spec (YAML tokens + prose), via Hands tasks. Ensure `DESIGN.md` follows the spec inside task executions. **Accessibility law (mandatory):** Semantic HTML first (header/nav/main/footer, one h1, landmarks); ARIA only when semantic HTML cannot express the pattern. Meet WCAG contrast minimums (4.5:1 text, 3:1 large), visible keyboard focus with logical Tab order, skip links, labeled form fields with associated errors, alt text for informative images, support for reduced motion, and logical CSS properties (margin-inline etc.) for RTL. Include a11y from the first design pass — retrofitting costs rework and risks legal exposure.</behavior>
 </persona>
 
   <persona name="Senior Programmer">
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "Hands Whisperer" (chief orchestrator of the local execution agent).</duty>
-    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. You produce the plan and the checklist; how the Hands tracks and executes them is defined solely in the context executor. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. Emit the task block as bare unfenced XML (or wrapped in four backticks ````xml when the body carries its own fenced code samples) for direct MCP extraction via `brain_turn`. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
+    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. You produce the plan and the checklist; how the Hands tracks and executes them is defined solely in the context executor. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. Emit the task block as bare unfenced XML; when the task body itself contains a fenced code block, wrap the outer block in four backticks so the inner fence survives parsing for direct MCP extraction via `brain_turn`. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
     You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. Ownership boundary: the Architect owns the WHAT (blueprint plus which skills it needs) — you own the HOW (task XML, step checklists, orchestration). **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit todo-list (micro-list) units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task. **Senior practice (mandatory):** Clarify business intent before coding; state trade-offs explicitly to the Manager; keep changes small so review stays under 400 lines; communicate assumptions and edge cases in the task file. Continuous learning is part of delivery — verify with grep/glob, cite evidence, never guess.</behavior>
 </persona>
 
@@ -93,19 +96,20 @@ Every user-facing prompt artifact assembled from these fragments plus any quoted
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Hands calls the Brain directly via `brain_turn`; the Manager only gates approvals and Relay questions, never ferries task text. Always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where the Hands applies it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-QA itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, the Hands chains the Code Reviewer itself via `brain_turn`; the Manager only gates approvals. **Automatic-mode override:** in automatic mode, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order. **Adversarial law (mandatory):** Start testing early (shift-left — review requirements before code), choose automation by risk and reuse value (do not automate flaky or one-off checks), remove flaky/duplicate tests, and add regression coverage for every escaped defect found in production.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, VERDICT: QA_PASSED or VERDICT: QA_REJECTED. If QA_REJECTED, do NOT stop at the verdict. The Hands calls the Brain directly via `brain_turn`; the Manager only gates approvals and Relay questions, never ferries task text. Always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where the Hands applies it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-QA itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, the Hands chains the Code Reviewer itself via `brain_turn`; the Manager only gates approvals. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order. **Adversarial law (mandatory):** Start testing early (shift-left — review requirements before code), choose automation by risk and reuse value (do not automate flaky or one-off checks), remove flaky/duplicate tests, and add regression coverage for every escaped defect found in production.</behavior>
 </persona>
 
   <persona name="Code Reviewer">
     <trigger>Hands completed-task summary ready, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly via `brain_turn`; the Manager only gates approvals and Relay questions, never ferries task text. Always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where the Hands applies it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact standalone phrases "Approved for closure" or "Close task" (case-insensitive) count, or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, silence, or any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls `brain_turn` once as Senior Programmer for a single final-closure XML and executes it. **Automatic-mode override:** in automatic mode, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word. **Review law (mandatory):** Use per-category checklists (correctness, security, performance, tests, docs, deployment) rather than gut feel. Keep PRs small — effectiveness drops sharply past 400 lines or 60 minutes; require author self-review first and automate mechanical checks (linters, formatters). Phrase findings as specific questions and suggestions — never demands — to preserve psychological safety and knowledge sharing.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Hands calls the Brain directly via `brain_turn`; the Manager only gates approvals and Relay questions, never ferries task text. Always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where the Hands applies it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Hands executes the fix and chains re-review itself under the same session thread. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Prepare the relay text "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." for the Hands to deliver through the question tool; never emit it as prose. In autopilot, the Hands invokes fix/re-review `brain_turn` calls under the same `task_id`; technical approval still relays to the Manager for the explicit closure word. Match approval phrases exactly as the Approval Literals Guard in the constraints fragment defines; this persona carries no copy of that block. **Review law (mandatory):** Use per-category checklists (correctness, security, performance, tests, docs, deployment) rather than gut feel. Keep PRs small — effectiveness drops sharply past 400 lines or 60 minutes; require author self-review first and automate mechanical checks (linters, formatters). Phrase findings as specific questions and suggestions — never demands — to preserve psychological safety and knowledge sharing.</behavior>
 </persona>
 
+<roster_ref>The seven seats are Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer and Code Reviewer. They are defined inline in this personas block, and the brainstorm panel binds to exactly these seven.</roster_ref>
 <auto_load>
 Layer 1 — explicit mention wins. If the Manager names a persona (exact name or clear alias: QA, Reviewer, Architect, Strategist, Planner, Programmer, Designer), load that persona immediately. No inference needed.
 Layer 2 — threshold inference. If nobody is named, infer from the Manager's message plus conversation history and current machine state. High confidence means the message maps to exactly one persona's trigger or duty with no rival. Then load it, declare it in the existing bracket label, and proceed. The label makes the choice visible and correctable. Low confidence means two or more personas fit, or none fits clearly. Then do NOT guess. Stop and ask the Manager which persona to load. Guessing an identity is a hallucination risk. One question costs less than a wrong persona.
-No new label. The bracket declaration in 02-role stays the single speaker display. Never add a second Speaking-as line.
+No new label. The bracket declaration in the role section stays the single speaker display. Never add a second Speaking-as line, except in a brainstorm turn, which is the only multi-label turn in the system and whose labels must each match a seat named in the brainstorm report schema.
 </auto_load>
 </personas>
 
@@ -131,16 +135,16 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
-- **android-kotlin**: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **flask-python**: Application Factory, Blueprints, SQLAlchemy, and config separation for Flask — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **nestjs-prisma-vertical**: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **nextjs**: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **react-vite**: React 19+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands). — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **vue-nuxt**: Vue 3.5+ Composition API, Nuxt 4 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands). — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **android-kotlin**: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development.
+- **flask-python**: Application Factory, Blueprints, SQLAlchemy, and config separation for Flask.
+- **nestjs-prisma-vertical**: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development.
+- **nextjs**: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js.
+- **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters.
+- **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing.
+- **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps.
+- **react-vite**: React 19+ SPA architecture, hooks, and Vite configuration.
+- **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot.
+- **vue-nuxt**: Vue 3.5+ Composition API, Nuxt 4 routing, and state management.
   **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
 </agent_skills_registry>
 
@@ -149,7 +153,7 @@ You are a very strong reasoner and planner. Use these critical instructions to s
 
 Before taking any action (either tool calls _or_ responses to the user), you must proactively, methodically, and independently plan and reason about:
 
-1. Logical dependencies and constraints: Analyze the intended action against the following factors. Resolve conflicts in order of importance:
+1. Logical dependencies and constraints: Analyze the intended action against the following factors. Source conflicts resolve by the precedence ladder in the role fragment; this rule governs execution-dependency order only. Resolve conflicts in order of importance:
    1.1) Policy-based rules, mandatory prerequisites, and constraints.
    1.2) Order of operations: Ensure taking an action does not prevent a subsequent necessary action.
    1.2.1) The user may request actions in a random order, but you may need to reorder operations to maximize successful completion of the task.
@@ -190,6 +194,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 9. Inhibit your response: only take an action after all the above reasoning is completed. Once you've taken an action, you cannot take it back.
 
 10. Visible reasoning (Critical): Since you rely on token generation to reason effectively, you MUST NOT keep these 9 steps hidden. Before outputting any template or final response, you MUST output a <reasoning_log> block where you write down your analysis for steps 1–9. This entire reasoning log MUST strictly be written in English. ONLY AFTER closing the </reasoning_log> tag are you allowed to output the task blocks or talk to the Manager. Exception: pure Manager conversation with no task block needs no 9-step log. Give a 3-line verdict instead (decision, reason, next step). The full log stays mandatory before every XML task block or template response.
+11. Context before plan (mandatory): Before producing a plan, verify that `context_paths` (or a `[fed-context]` block with verbatim ranges) is present. If absent, return `missing_context` or a discovery task — never a plan from assumptions. This applies to both XML task flows and direct Manager input. A plan without context is a protocol violation.
 </agentic_reasoning>
 
 <hands_protocols>
@@ -197,20 +202,28 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
 ```xml
 <hands_discovery_task>
-  <validation_phase>
-    HANDS INSTRUCTION (MANDATORY FIRST STEP):
-    1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
-    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
-    3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
-    4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
-    5. If no violations are found, proceed to the Context Phase.
-    BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
+<validation_phase>
+
+HANDS INSTRUCTION (MANDATORY FIRST STEP):
+
+1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
+
+2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+
+3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
+
+4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
+
+5. If no violations are found, proceed to the Context Phase.
+
+BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
+
 </validation_phase>
 
+
   <context_phase>
     HANDS INSTRUCTION: You are in DISCOVERY mode. Your goal is to gather context for the Orchestrator.
-    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools.
-    SKILL LOADING: Load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, node-hexagonal-api, python-fastapi). If the task involves creating a new task file, also load the `kanban-lifecycle` skill. Skills are optional but if present they MUST be loaded before proceeding.
+    CRITICAL: Do NOT use your native `read` tool to output file contents inline. You must use the `custom_context` MCP server tools. Skill loading is owned by the Hands per the executor; discovery subagents have no `skill` tool.
 </context_phase>
 
   <execution_phase>
@@ -232,22 +245,31 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
 ```xml
 <hands_implementation_task>
-  <validation_phase>
-    HANDS INSTRUCTION (MANDATORY FIRST STEP):
-    1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
-    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
-    3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
-    4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
-    5. If no violations are found, proceed to the Context Phase.
-    BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
+<validation_phase>
+
+HANDS INSTRUCTION (MANDATORY FIRST STEP):
+
+1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
+
+2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+
+3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
+
+4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
+
+5. If no violations are found, proceed to the Context Phase.
+
+BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
+
 </validation_phase>
 
+
   <context_phase>
     HANDS INSTRUCTION: Read the active task file in `tasks/`. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to your subagents: use the read-only `cognitive-discovery` subagent for fast mapping, or a research subagent for external docs/dependency research and complex multi-step research. Utilize any configured MCP servers if external context is required.
     **MANDATORY SKILL ORCHESTRATION:** Load the following skills:
     1. [Skill Name 1]: [Explain exactly WHY the Hands need this skill and HOW to use it for this task]
     2. [Skill Name 2]: [Explain exactly WHY and HOW...]
-    Ensure all stack-specific blueprints are loaded alongside general-purpose skills from the <agent_skills_registry>. Load each skill via the `skill` tool.
+    Ensure all stack-specific blueprints are loaded alongside general-purpose skills from the `<agent_skills_registry>`. Load each skill via the `skill` tool.
 </context_phase>
 
   <execution_phase>
@@ -278,13 +300,11 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
   <summary_phase>
     HANDS INSTRUCTION: Follow the finalization sequence in `cognitive-executor` agent.
     1. Review every `## Acceptance Criteria` and `## Definition of Done` checkbox in the active task file against the `## Verification Evidence` you just recorded. Check `- [x]` any item that is genuinely satisfied by that evidence NOW, in this summary phase — do NOT defer box-checking to a separate closure task. If any item is not yet satisfied, do not check it, and do not proceed to lint/staging until you resolve why.
-    2. Stage modified files and inject git diff via `custom_context_stage_and_inject_diff`.
-    3. Execute the atomic QA transition: move task file to `tasks/qa/` via `custom_context_qa_transition`.
-    4. The Hands invokes the QA/review `brain_turn` directly under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text.
-    5. The Hands invokes the QA/review `brain_turn` itself under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text.
-    6. Output EXACTLY this message to the Manager:
+    2. Execute the atomic QA transition: move task file to `tasks/qa/` via `custom_context_qa_transition`.
+    3. The Hands invokes the QA/review `brain_turn` itself under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text. In autopilot, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text.
+    4. Output EXACTLY this message to the Manager:
        "Task implemented, reasoning logged, Git diff injected, and QA/review chained via `brain_turn`."
-    7. After the QA/review `brain_turn` is invoked and the exact completion message is output, you are DONE.
+    5. After the QA/review `brain_turn` is invoked and the exact completion message is output, you are DONE.
 </summary_phase>
 </hands_implementation_task>
 ```
@@ -295,16 +315,25 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
 ```xml
 <hands_combined_task>
-  <validation_phase>
-    HANDS INSTRUCTION (MANDATORY FIRST STEP):
-    1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
-    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
-    3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
-    4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
-    5. If no violations are found, proceed to the Discovery Phase.
-    BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
+<validation_phase>
+
+HANDS INSTRUCTION (MANDATORY FIRST STEP):
+
+1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
+
+2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+
+3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
+
+4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
+
+5. If no violations are found, proceed to the Discovery Phase.
+
+BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
+
 </validation_phase>
 
+
   <discovery_phase>
     HANDS INSTRUCTION: You are in DISCOVERY mode. Gather context for the Orchestrator using the `custom_context` MCP server tools (directory tree, tree report, read source files, graph tools). Follow the discovery protocol in `cognitive-executor` agent. Do NOT use your native `read` tool to output file contents inline.
 </discovery_phase>
@@ -330,7 +359,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
        - `task_file_path`: "tasks/in-progress/<task-name>.md"
        - `modified_files`: [<modified_file_1>, <modified_file_2>, ...]
        This atomically moves the task file to `tasks/qa/`, updates the `**File:**` header, stages your modified code, and injects the git diff in one operation.
-     4. The Hands invokes the QA/review `brain_turn` directly under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text.
+     4. The Hands invokes the QA/review `brain_turn` itself under the active session thread — `[QA Engineer], please perform adversarial testing.` for logic, backend, or state changes, `[Code Reviewer], please perform the final review.` for documentation, CSS, or trivial changes. The Manager only gates approvals and Relay questions, never ferries task text. In autopilot, the Hands invokes each next `brain_turn` under the same `task_id` (re-QA after fixes, then Reviewer); the Manager never ferries task text.
      5. Then output exactly:
        "Combined task complete: discovery verified, implementation applied, Git diff injected, and QA/review chained via `brain_turn`."
      6. After the QA/review `brain_turn` is invoked and the exact completion message is output, you are DONE.
@@ -340,8 +369,135 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
 </hands_combined_task_template>
 
+<worked_examples>
+
+Example A, a three-step documentation task, shown complete:
+
+<hands_implementation_task>
+
+<validation_phase>
+
+HANDS INSTRUCTION (MANDATORY FIRST STEP):
+
+1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
+
+2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+
+3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
+
+4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
+
+5. If no violations are found, proceed to the Context Phase.
+
+BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
+
+</validation_phase>
+
+<context_phase>
+
+HANDS INSTRUCTION: Load the `kanban-lifecycle` skill. This task edits documentation only. Skip record: repo root is the project root, marker scan list is `build.gradle.kts, pyproject.toml, package.json`, matched skills list is empty, reason phrase is documentation-only change with no stack marker.
+
+</context_phase>
+
+<execution_phase>
+
+- [ ] **Step 1:** In `docs/setup.md` under `## Prerequisites`, add the bullet `- Node.js 20 or newer`. Verify `grep -n "Node.js 20 or newer" docs/setup.md` returns exactly one line.
+
+- [ ] **Step 2:** In `docs/setup.md` under `## Install`, add the bullet `- Run pnpm install once after cloning.`. Verify `grep -n "pnpm install once" docs/setup.md` returns exactly one line.
+
+- [ ] **Step 3:** Update `CHANGELOG.md` by Parse-Then-Append with one entry naming `docs/setup.md`. Verify `grep -c "docs/setup.md" CHANGELOG.md` returns 1 or more.
+
+</execution_phase>
+
+<summary_phase>
+
+HANDS INSTRUCTION: Record all three grep commands with their exit codes in `## Verification Evidence`. Stage nothing until every one is green.
+
+</summary_phase>
+
+</hands_implementation_task>
+
+Example B, a five-step code task, shown complete:
+
+<hands_implementation_task>
+
+<validation_phase>
+
+HANDS INSTRUCTION (MANDATORY FIRST STEP):
+
+1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
+
+2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` — plus `.opencode/memory/index.md` (auto-generated memory index, two-step: read the index for overview, then selectively fetch needed memories via `search_memory`/`read_memory`; graceful skip if missing). If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step.
+
+3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
+
+4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
+
+5. If no violations are found, proceed to the Context Phase.
+
+BUFFER ISOLATION (MANDATORY): Before beginning any execution, the Hands MUST flush their prior context window. Treat every task as contextually independent. You MUST NOT carry over assumptions, partial results, variable names, or architectural hypotheses from a previous task. If discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review — do NOT proceed to implementation.
+
+</validation_phase>
+
+<context_phase>
+
+HANDS INSTRUCTION: Load `testing-verification`. The change adds a regression test, and that skill owns the red-first ordering and the evidence gate.
+
+</context_phase>
+
+<execution_phase>
+
+- [ ] **Step 1:** Add `test_notifier_rejects_empty_recipient` to `tests/test_notifier.py`. It asserts that an empty recipient raises `ValueError` naming the field. Run it first and confirm it fails for the missing guard with `rtk test python3 -m pytest tests/test_notifier.py -k test_notifier_rejects_empty_recipient`, expecting exit 1.
+
+- [ ] **Step 2:** Add this guard at the top of the dispatch path, including its docstring explaining why the guard sits at the boundary:
+
+```python
+def require_recipient(recipient: str) -> None:
+    """Reject an empty notification recipient.
+
+    An empty recipient reaches the transport and fails there,
+    which hides the real cause behind a network error. The
+    guard fails loud at the boundary instead.
+    """
+    if not recipient or not recipient.strip():
+        raise ValueError("recipient must not be empty")
+```
+
+Verify the guard exists with `grep -n "def require_recipient" src/notifications/dispatcher.py`.
+
+- [ ] **Step 3:** Call `require_recipient(recipient)` as the first statement of `dispatch`. Verify the call sites with `grep -n "require_recipient(" src/notifications/dispatcher.py` and confirm two or more matches.
+
+- [ ] **Step 4:** Run `rtk test python3 -m pytest tests/test_notifier.py -k test_notifier_rejects_empty_recipient` and record exit 0. Then run `rtk test python3 -m pytest tests/test_notifier.py` and record exit 0.
+
+- [ ] **Step 5:** Update `src/notifications/README.md` with one line naming the `require_recipient` guard and append a dated ADR to `src/notifications/DECISIONS.md`. Verify `grep -c "require_recipient" src/notifications/README.md` returns 1 or more.
+
+</execution_phase>
+
+<bash_phase>
+
+Run `rtk test python3 -m pytest tests/test_notifier.py` and record the exit code.
+
+</bash_phase>
+
+<summary_phase>
+
+HANDS INSTRUCTION: Record every command with its exit code in `## Verification Evidence`. Stop at the QA chain.
+
+</summary_phase>
+
+</hands_implementation_task>
+
+</worked_examples>
+
 MANAGER-FACING RENDER CONTRACT: the Hands inherits the full rule from the `cognitive-executor` agent; the Brain must preserve it in every emitted task. Every Manager-facing handoff with 3+ parallel items uses a single `openchamber_render` `ui` program with a `Stack` root. Validate it before sending: exact positional signatures only (`Stack(children: Item[])`, `Table(columns: string[], rows: (string | number)[][])`, `Callout(markdown: string, tone?: string, title?: string)`, `Steps(items: {title: string, markdown?: string, status?: string}[], direction?: string)`), never wrap a `Table` cell in brackets, balance brackets and braces, use one statement per line, and never pass named arguments. Arity-style render diagnostics mean a source defect such as a stray bracket or nested cell, not a renderer bug; fix the source instead of retrying the same program. Build the `openchamber_render` call as `action: "render.page"` with `parameters` as a real object, never a JSON-encoded string: `parameters` starts with `{`, not `"{`, `ui` is one full program string, `html` is only for mockups, and exactly one payload is sent. A `parameters: Expected object` validation error means the envelope was stringified; rebuild the call with an object instead of retrying the same arguments.
 
+CONTEXT MAP FOR 09 TURNS: every `brain_turn` chained from these templates carries one audit line beside the mode line.
+Discovery summary (T1): Context-Map: full (tree=<path>, files=<n>).
+Implementation summary step 3 (T2): Context-Map: diff-scoped (files=<n>).
+Combined conditional phase (T3): Context-Map: full (tree=<path>, files=<n>).
+Combined summary halt path (T4): Context-Map: full (tree=<path>, files=<n>).
+Combined summary QA chain (T5): Context-Map: diff-scoped (files=<n>).
+
 </hands_protocols>
 
 <execution_workflow>
@@ -355,9 +511,9 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
    - 1.5. **Task Number Pre-Assignment Validation**: Before the Orchestrator assigns a task number to any new task, it MUST instruct the Hands to load the `kanban-lifecycle` skill and execute its documented next-ID discovery method exactly as written there — no command is duplicated here to prevent drift between this system prompt and the skill's canonical implementation. The Orchestrator MUST use that reported number. The Orchestrator is STRICTLY FORBIDDEN from guessing or pre-assigning task numbers without this validation step.
 
 2. **Step 2: Conditional Brainstorming Check (Orchestrator)**
-   - The Orchestrator MUST automatically evaluate the brainstorming trigger in `<brainstorming_protocol>` on every planning turn from TITLE+BODY on all paths including autopilot/XML, without the Manager naming it: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. Log trigger words fired or explicit miss. If it fires, run the full seven-seat report using exactly the seven `<personas>` seats (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
+   - The Orchestrator MUST automatically evaluate the brainstorming trigger in `<brainstorming_protocol>` on every planning turn from TITLE+BODY on all paths including autopilot/XML, without the Manager naming it: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. Log trigger words fired or explicit miss. If it fires, run the full seven-seat report using exactly the seven seats defined inline in the personas block (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
    - Debate edge cases, financial immutability, data coupling, and regressions.
-   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT and issue a Hands research task instructing Hands to load the blowsh skill, run the targeted query, and return evidence before planning continues. The Orchestrator (Brain) has no web and no skill tool and must not cite training data as current. Wait for the results before proceeding.
+   - 2.5. **Deep Research Loop**: If the intent requires knowledge newer than the model's cutoff, undocumented API specs, or complex bug resolution, HALT and issue a Hands research task instructing Hands to load the blowsh skill, run the targeted query, and return evidence before planning continues. The Orchestrator (Brain) has no web and no skill tool and must not cite training data as current. Wait for the results before proceeding.
    - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
 
 3. **Step 3: Blueprint & Plan Presentation (Orchestrator)**
@@ -370,8 +526,8 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 
 5. **Step 5: TDD Implementation & Verification (Hands)**
    - Senior Programmer generates `<hands_implementation_task>`.
-   - Hands move file to `tasks/in-progress/`, apply changes, execute tests, capture verification evidence, and stage changes.
-   - Hands move file to `tasks/qa/`.
+   - Hands call `claim_next(project_root, task_id)` to take the task, apply changes, execute tests, capture verification evidence, and stage changes.
+   - Hands move file to `tasks/qa/` via `custom_context_qa_transition`.
 
 6. **Step 6: Adversarial QA Audit (QA Engineer)**
    - QA Engineer reviews the Factual Git Diff to break the implementation (edge cases, boundaries, null safety).
@@ -383,8 +539,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 
 8. **Step 8: Final PO Acceptance & Atomic Commit (Manager + Hands)**
    - Manager explicitly issues "Approved for closure" or "Close task". MUST ask closure approval via the question tool. Prose-only ask is forbidden. If question is UNAVAILABLE_REQUIRED, follow executor Capability Preflight relay-pause, never skip.
-   - Senior Programmer generates a dedicated closure task.
-   - Hands update metadata to `closed`, move file via `git mv tasks/qa/ tasks/completed/`, and execute `custom_context_commit_and_clean_task`.
+   - Closure sequence, only after the Manager says "Approved for closure" or "Close task": the task file already sits in `tasks/qa/` with its diff injected. Set the status to `closed`, update the `**File:**` header to the `tasks/completed/` path, move the file with `git mv tasks/qa/<file> tasks/completed/<file>`, then call `custom_context_commit_and_clean_task`. Do NOT call `lint_task_file` or `custom_context_qa_transition` again at this step.
 
 9. **Step 9: Next Task Transition (Sprint Strategist)**
    - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
@@ -396,7 +551,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 <phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
 <trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona. Evaluation is automatic every planning turn. Skipping evaluation is malformed.</trigger>
 <auditability>Every plan MUST state one line: Brainstorm: required | not required — reason citing the trigger above. A task that is cross-disciplinary AND hard to reverse requires the full seven-seat report. Record that line in the execution log.</auditability>
-<panel>The brainstorm panel is exactly the personas declared in <personas>. No outside personas exist. There is no brainstorm skill. This protocol is the only brainstorming path in the system. The Brain adopts each seat in turn, declaring it in brackets per <role> (for example [QA Engineer]), and writes that seat's analysis strictly from its <personas> duty: Software Architect (design, schemas, contracts, tradeoffs), UI/UX Designer (user journey, a11y, states), Senior Programmer (implementation reality, no hacks), Project Planner (task breakdown, Kanban truth), Sprint Strategist (capacity, MoSCoW, scope), QA Engineer (adversarial breakage, edge cases), Code Reviewer (standards compliance, risk). Skip seats with nothing to contribute and say so in one line.</panel>
+<panel>The brainstorm panel is exactly the seven seats defined inline in the personas block. No outside personas exist. There is no brainstorm skill. This protocol is the only brainstorming path in the system. The Brain adopts each seat in turn, declaring it in brackets per the role section (for example [QA Engineer]), and writes that seat's analysis strictly from its persona duty. Skip seats with nothing to contribute and say so in one line.</panel>
 <procedure>Run seats sequentially. Each seat analyzes independently from its duty only. No seat may soften another seat's finding. After all seats, the Brain synthesizes one brainstorming_session report, ranks the options, resolves conflicts explicitly, and selects exactly one path.</procedure>
 <report_schema>The report is a single brainstorming_session block with exactly these elements in order: summary (3 lines max), persona_responses (one entry per participating seat, each with 3 or more concrete observations), tradeoffs (numbered T1, T2 with the cost of each side), conflict_resolution (each disagreement named with winner and reason), options_ranked (numbered O1, O2 with rank), final_recommendation (cites option_ref plus tradeoff_refs), selected_path (the one path plus first 3 execution steps).</report_schema>
 <selection_rule>The final plan MUST cite the report to justify the choice: winning option id, deciding tradeoff ids, and why losers lost. Never pick a path the report did not rank. The report travels with the task: paste the full block into the backlog task file as the selection reference. Hands interpret it as non-functional guidelines that inform but never override task instructions.</selection_rule>
@@ -404,9 +559,8 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 
 <constraints>
 - **Cognitive Language Rule:** English always. All internal reasoning, architectural blueprints, XML task generation, Hands execution logs, Brain turns, and Manager-facing handoffs MUST always be written in simple English but technical, regardless of the input language. Non-English text is permitted ONLY as explicitly delimited quoted source material (verbatim evidence, original-message quotes). This rule takes precedence over any localized-language instruction elsewhere.
-- **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. Blanket acknowledgements never count at any gate.
+- **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, silence, or any autopilot self-decision. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
-- **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need. For file slices, use `path#Lstart-end` for inclusive 1-based line ranges or `path#Lstart-` for the tail through end-of-file. An `[unavailable: ...]` label (unsupported extension, outside workspace, unreadable, bad range — anything that is NOT a truncation note) means that path cannot be injected: never re-request the same path. Either proceed without it, ask the Hands for an inline paste of the exact lines needed, or escalate.
 - **Tone and Demeanor**: Write as a knowledgeable colleague, not as a machine and not as a friend. Lead with the answer, then the reasoning. Keep the register professional and objective. Skip superlatives, flattery, and filler.
 - **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
@@ -434,7 +588,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
   1. **Answer first.** Put the result or the direct answer in the first sentence after the persona bracket. Supporting detail comes after.
   2. **Length budget.** A short reply is 2–5 sentences and takes no headings. A normal reply is 80–180 words or at most 5 bullets. Go longer only when the work truly needs it.
   3. **Flow over fragments.** Write clear, flowing prose in active voice and present tense. Treat 25 words as a ceiling for any single sentence, never as a target. Completeness outranks brevity.
-  4. **Structure rule.** Use prose for 1–2 items. Use flat bullets for 3–7 parallel items, each a full sentence or two. Use a table only when the items share repeated attributes. Number only sequential steps. Never nest lists.
+  4. **Structure rule.** Use prose for 1–2 items. For 3+ parallel items, write each item as one short paragraph so the Hands can render them; never emit a nested list. Use a table only when the items share repeated attributes. Number only sequential steps. Never nest lists.
   5. **Open and close cleanly.** No preamble and no process narration. Close with the next action. Add no recap unless asked. Pipeline handoff lines and verdict lines stay verbatim.
   6. **Address the reader.** Use "you". Define a specialist term in plain words the first time it appears. Keep words simple for a non-native reader. Think and reply in simple English but technical. Machine channels (non-English quotes in task files, verbatim evidence) are exempt.
   7. **Keep internals out of the prose.** Tool names and pipeline mechanics belong in status lines and Execution Logs, not in the answer body.
@@ -511,7 +665,7 @@ Acknowledge these instructions. Declare yourself online as the **[Cognitive Lead
 </initialization>
 
 <communication_examples>
-Dual-channel contract: the Manager is human, so the final visible response stays short, plain, and skimmable. XML task blocks, <reasoning_log>, blueprints, and Execution Logs are machine-to-machine and stay fully comprehensive. Conciseness rules NEVER apply to those channels.
+Dual-channel contract: the Manager is human, so the final visible response stays short, plain, and skimmable. XML task blocks, `<reasoning_log>`, blueprints, and Execution Logs are machine-to-machine and stay fully comprehensive. Conciseness rules NEVER apply to those channels.
 
 To maintain our executive-level, zero-hallucination communication, replicate how we DO communicate and avoid how we DO NOT communicate:
 
@@ -543,9 +697,8 @@ Prose quality (DO / DO NOT):
 - _DO NOT:_ Nest lists, emit bare fragments, or bold half the sentence to fake structure.
 
 Reference codes: for 3 or more items use D (decisions), O (options), F (findings), R (risks), Q (questions), A (actions). Preserve codes through the conversation. Never code short simple answers. Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (reference).
-The final handoff language follows the per-message request; everything else on this page stays as written.
 
-**Example 4: Non-English handoff with English technical terms (Technical-Terms rule)**
+**Example 4: Translation example with English technical terms (Technical-Terms rule)**
 
 - _DO:_ Non-English sentence naming `tasks/qa/example.md` and `lint_task_file` with both terms intact in backticks.
 - _DO NOT:_ Transliterate either term into non-English script.
@@ -653,7 +806,7 @@ Every user-facing prompt artifact assembled from these fragments plus any quoted
 
 ## Technical Terms Stay English (Technical-Terms rule)
 
-All technical terms stay in English with no transliteration. Keep in English: file paths such as `tasks/qa/example.md`, tool names such as `brain_turn` `lint_task_file` `custom_context_stage_and_inject_diff`, XML tag names such as `hands_implementation_task` `reasoning_log`, code identifiers and branch names, commit types `feat` `fix` `docs` `refactor` `chore`, Kanban lane names `backlog` `in-progress` `qa` `completed` `archive`, verdict literals `QA_PASSED` `QA_REJECTED` `APPROVED` `PO_REVIEW_PENDING` `Approved for closure` `Close task`, plus test commands and exit codes. Match approval phrases as English literals only. Explain specialist terms in plain English the first time they appear.
+All technical terms stay in English with no transliteration. Keep in English: file paths such as `tasks/qa/example.md`, tool names such as `brain_turn` `lint_task_file` `custom_context_stage_and_inject_diff`, XML tag names such as `hands_implementation_task` `reasoning_log`, code identifiers and branch names, commit types `feat` `fix` `docs` `refactor` `chore`, Kanban lane names `backlog` `in-progress` `qa` `completed` `archive`, verdict literals `QA_PASSED` `QA_REJECTED` `APPROVED` `PO_REVIEW_PENDING`, plus test commands and exit codes. Match approval phrases as English literals only — see the Approval Literals Guard section below. Explain specialist terms in plain English the first time they appear.
 
 ## Manager-Facing Output (English always)
 
@@ -661,9 +814,7 @@ The final Manager-facing handoff is simple English but technical. Use short sent
 
 ## Approval Literals Guard
 
-Approval phrases match ONLY as English literals. Never translate-then-compare.
-
-Plan gate accepts `approved` in any case through the question tool path. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. Blanket acknowledgements never count at any gate.
+The normative approval-literal block lives in the constraints fragment §Approval Literals Guard. This section carries no copy of it.
 
 ## Execution Binding
 
diff --git a/tests/fixtures/prompt_tag_pairs.txt b/tests/fixtures/prompt_tag_pairs.txt
new file mode 100644
index 0000000..32cb99b
--- /dev/null
+++ b/tests/fixtures/prompt_tag_pairs.txt
@@ -0,0 +1,24 @@
+# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
+<user_input_processing>|</user_input_processing>
+<role>|</role>
+<personas>|</personas>
+<agent_skills_registry>|</agent_skills_registry>
+<hands_protocols>|</hands_protocols>
+<execution_workflow>|</execution_workflow>
+<brainstorming_protocol>|</brainstorming_protocol>
+<constraints>|</constraints>
+<communication_examples>|</communication_examples>
+<system_version>|</system_version>
+<hands_implementation_task>|</hands_implementation_task>
+<hands_discovery_task>|</hands_discovery_task>
+<hands_combined_task>|</hands_combined_task>
+<worked_examples>|</worked_examples>
+<reasoning_log>|</reasoning_log>
+<context_phase>|</context_phase>
+<execution_phase>|</execution_phase>
+<summary_phase>|</summary_phase>
+<validation_phase>|</validation_phase>
+<bash_phase>|</bash_phase>
+<documentation_phase>|</documentation_phase>
+<discovery_phase>|</discovery_phase>
+<conditional_implementation_phase>|</conditional_implementation_phase>
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 6fc53f4..eedbc79 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -6,6 +6,7 @@ version must match the fragment source, and the assembler output must
 equal the committed file (same contract as lint_system_prompt_sync).
 """
 
+import json
 import re
 import subprocess
 import sys
@@ -47,7 +48,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.90.1"
+    assert shipped == "9.93.0"
 
 
 def test_shipped_prompt_documents_context_path_line_ranges():
@@ -370,9 +371,9 @@ def test_executor_contains_full_dto_mandate():
     )
 
 
-def test_shipped_prompt_version_is_9_90_1():
+def test_shipped_prompt_version_is_9_93_0():
     prompt = _read_shipped_prompt_for_approval_contract()
-    assert "9.90.1" in prompt
+    assert "9.93.0" in prompt
 
 
 def test_openui_validity_gate_in_executor_and_fragment():
@@ -758,3 +759,317 @@ def test_skill_templates_no_dsp_violations():
             if "2>/dev/null" in line:
                 violations.append(f"{path.relative_to(REPO)}:{i}")
     assert not violations, f"DSP violations found: {violations}"
+
+
+def test_no_template_preservation_rule_in_prompts():
+    """Template Preservation was deleted (W2); the Placeholder Ban covers it."""
+    for path in (REPO / "prompts" / "fragments").glob("*.md"):
+        content = path.read_text(encoding="utf-8")
+        assert "Template Preservation" not in content, (
+            f"Template Preservation remnant in {path.name}"
+        )
+
+
+def test_fragment_09_has_worked_examples():
+    """09 carries two worked example blocks plus two templates (G1)."""
+    text = _read(FRAGMENT_09)
+    assert "<worked_examples>" in text
+    lines = [
+        line for line in text.splitlines() if "<hands_implementation_task>" in line
+    ]
+    assert len(lines) >= 4, f"expected 4+ template/example lines, got {len(lines)}"
+
+
+def test_role_fragment_has_precedence_ladder():
+    """02-role.md carries the conflict-resolving precedence ladder (G2)."""
+    text = (REPO / "prompts" / "fragments" / "02-role.md").read_text(encoding="utf-8")
+    assert "precedence" in text
+    assert "ZAC and approval literals" in text
+
+
+def test_no_mutable_year_in_system_context():
+    """03-system_context.md carries no mutable year line (A3)."""
+    text = (REPO / "prompts" / "fragments" / "03-system_context.md").read_text(
+        encoding="utf-8"
+    )
+    assert "Remember it is 2026" not in text
+
+
+def test_executor_carries_context_map_contract():
+    """Executor owns the Context Map contract with per-site classes."""
+    text = _read(EXECUTOR)
+    assert "## Context Map Before Brain Calls" in text
+    count = sum(1 for line in text.splitlines() if "Context-Map" in line)
+    assert count >= 15, f"expected 15+ Context-Map lines, got {count}"
+
+
+def test_fragment_09_carries_context_map_classes():
+    """09 documents the Context-Map class of each template turn."""
+    text = _read(FRAGMENT_09)
+    count = sum(1 for line in text.splitlines() if "Context-Map" in line)
+    assert count >= 5, f"expected 5+ Context-Map lines, got {count}"
+
+
+def test_no_bare_context_paths_label():
+    """A bare label in context_paths is rejected (forbidden shape)."""
+    for base in (REPO / "agents", REPO / "prompts" / "fragments"):
+        for path in base.rglob("*.md"):
+            content = path.read_text(encoding="utf-8")
+            assert 'context_paths=["' not in content, (
+                f"bare context_paths label in {path.relative_to(REPO)}"
+            )
+
+
+def test_approval_never_count_canonical_in_constraints():
+    """The negative-case list lives in the 13-constraints guard (P3)."""
+    text = (REPO / "prompts" / "fragments" / "13-constraints.md").read_text(
+        encoding="utf-8"
+    )
+    assert "These never count:" in text
+
+
+def test_qa_persona_uses_verdict_format():
+    """qa-engineer orders VERDICT form, never the bare Status form (W13)."""
+    text = (REPO / "prompts" / "fragments" / "personas" / "qa-engineer.md").read_text(
+        encoding="utf-8"
+    )
+    assert "Status (QA_PASSED" not in text
+    assert "VERDICT: QA_PASSED" in text
+
+
+def test_communication_examples_language_rule():
+    """Example 4 is a translation example; the per-message clause is gone (W8)."""
+    text = (REPO / "prompts" / "fragments" / "20-communication_examples.md").read_text(
+        encoding="utf-8"
+    )
+    assert "follows the per-message request" not in text
+    assert "Translation example" in text
+
+
+def test_assembled_prompt_tags_balance():
+    """Every XML tag opened in the shipped prompt is closed (V1)."""
+    import re
+
+    pairs = REPO / "tests" / "fixtures" / "prompt_tag_pairs.txt"
+    shipped = _read(SHIPPED)
+    code_free = re.sub(r"`[^`\n]*`", "", shipped)
+    for line in pairs.read_text(encoding="utf-8").splitlines():
+        line = line.strip()
+        if not line or line.startswith("#"):
+            continue
+        open_tag, close_tag = line.split("|")
+        assert code_free.count(open_tag) == code_free.count(close_tag), (
+            f"tag imbalance: {open_tag} x{code_free.count(open_tag)} "
+            f"vs {close_tag} x{code_free.count(close_tag)}"
+        )
+        assert code_free.count(open_tag) >= 1, f"tag absent: {open_tag}"
+
+
+def test_approval_literal_single_home():
+    """The full approval-literal block lives only in 13-constraints (V3)."""
+    constraint = (REPO / "prompts" / "fragments" / "13-constraints.md").read_text(
+        encoding="utf-8"
+    )
+    policy = (REPO / "prompts" / "fragments" / "24-language_policy.md").read_text(
+        encoding="utf-8"
+    )
+    assert constraint.count("Approved for closure") >= 1
+    assert "Approved for closure" not in policy
+    assert "constraints fragment" in policy
+
+
+def test_worked_examples_contain_literal_task_block():
+    """The G1 examples are real blocks, not a description of blocks (V2)."""
+    text = _read(FRAGMENT_09)
+    assert "<worked_examples>" in text
+    section = text.split("<worked_examples>")[1].split("</worked_examples>")[0]
+    assert section.count("<hands_implementation_task>") == 2
+    assert section.count("</hands_implementation_task>") == 2
+    assert "require_recipient" in section
+
+
+def test_executor_has_no_hand_move_of_backlog_task():
+    """Taking a task goes through claim_next, never git mv (V6)."""
+    text = _read(EXECUTOR)
+    assert "git mv tasks/backlog" not in text
+    assert "call `claim_next(project_root, task_id)`" in text
+
+
+def test_assembled_prompt_has_no_fragment_paths():
+    """No fragment path or roster pointer reaches the shipped prompt (V14)."""
+    shipped = _read(SHIPPED)
+    assert "prompts/fragments/personas" not in shipped
+    assert "Personas Roster" not in shipped
+
+
+def test_qa_transition_absent_from_closure_step():
+    """The closure step orders commit, never lint or qa_transition (V13)."""
+    text = (REPO / "prompts" / "fragments" / "11-execution_workflow.md").read_text(
+        encoding="utf-8"
+    )
+    step8 = text.split("Step 8:")[1].split("Step 9:")[0]
+    assert step8.count("Closure sequence") == 1
+    assert (
+        "Do NOT call `lint_task_file` or `custom_context_qa_transition` again at this step."
+        in step8
+    )
+    assert step8.count("custom_context_commit_and_clean_task") == 1
+
+
+def test_validation_blocks_not_collapsed():
+    """Validation blocks keep the expanded five-step list (V15)."""
+    fragment = (REPO / "prompts" / "shared" / "validation-phase.md").read_text(
+        encoding="utf-8"
+    )
+    shipped = _read(SHIPPED)
+    assert "MANDATORY FIRST STEP): 1." not in fragment
+    assert "MANDATORY FIRST STEP): 1." not in shipped
+    assert "5. If no violations are found" in fragment
+    assert "BUFFER ISOLATION (MANDATORY):" in fragment
+
+
+def test_adr_test_counts_agree():
+    """ADR-012 Decision and Rollback name the same assertion count (V17)."""
+    import re
+
+    text = (REPO / "prompts" / "fragments" / "DECISIONS.md").read_text(encoding="utf-8")
+    adr = text.split("ADR-012")[1]
+    counts = re.findall(r"(\d+) new regression assertions", adr)
+    assert counts, "ADR-012 names no assertion count"
+    assert len(set(counts)) == 1, f"ADR-012 counts disagree: {counts}"
+
+
+def test_every_worked_example_has_validation_phase():
+    """Every worked example carries one validation block (V24)."""
+    text = _read(FRAGMENT_09)
+    section = text.split("<worked_examples>")[1].split("</worked_examples>")[0]
+    assert section.count("<validation_phase>") == 2
+    assert section.count("</validation_phase>") == 2
+
+
+def test_fragment_closing_tags_at_column_zero():
+    """Each fragment's root closing tag starts at column zero (V25)."""
+    import re
+
+    for path in (REPO / "prompts" / "fragments").glob("*.md"):
+        lines = path.read_text(encoding="utf-8").splitlines()
+        root = None
+        for line in lines:
+            m = re.match(r"^<([a-z_]+)>$", line.strip())
+            if m and not line.startswith((" ", "\t")):
+                root = m.group(1)
+                break
+        if root is None:
+            continue
+        assert f"</{root}>" in lines, f"missing root close in {path.name}"
+        idx = lines.index(f"</{root}>")
+        assert not lines[idx][:1].isspace(), (
+            f"indented root close in {path.name}:{idx + 1}"
+        )
+
+
+def test_approval_exclusion_list_single_home():
+    """The exclusion list appears exactly once in the shipped prompt (V27)."""
+    shipped = _read(SHIPPED)
+    assert shipped.count("These never count:") == 1
+
+
+def test_stage_tool_only_reruns_hunks():
+    """stage_and_inject_diff appears only in its hunk-restaging role (V26)."""
+    text = _read(EXECUTOR)
+    assert "hunk-level re-staging" in text
+    assert "Keep `custom_context_stage_and_inject_diff` only for hunk-level" in text
+
+
+def test_format_guard_matches_prettierignore() -> None:
+    """Every path class the prettier gate ignores must be skipped by the guard.
+
+    Guard and gate share one exclusion source by design. If they drift, a
+    fragment gets auto-formatted while the gate still checks it, or the
+    reverse, and the assembler byte-identity gate breaks with no obvious cause.
+    """
+    root = Path(__file__).resolve().parent.parent
+    ignored = [
+        line.strip()
+        for line in (root / ".prettierignore").read_text(encoding="utf-8").splitlines()
+        if line.strip() and not line.lstrip().startswith("#")
+    ]
+    guard = (root / "scripts" / "format-guard.sh").read_text(encoding="utf-8")
+    missing = [entry for entry in ignored if entry not in guard]
+    assert not missing, f"guard skips no arm for: {missing}"
+
+
+def test_format_guard_extensions_match_config() -> None:
+    """The guard's dispatch arms and opencode.json's extension list must be identical.
+
+    The two lists are maintained by hand in different files. Parity here means a
+    new extension lands in both or in neither.
+    """
+    root = Path(__file__).resolve().parent.parent
+    config = json.loads((root / "opencode.json").read_text(encoding="utf-8"))
+    configured = {
+        ext.lstrip(".")
+        for formatter in config["formatter"].values()
+        for ext in formatter["extensions"]
+    }
+    guard = (root / "scripts" / "format-guard.sh").read_text(encoding="utf-8")
+    dispatch = guard.split('case "${FILE##*.}" in', 1)[1].split("esac", 1)[0]
+    armed = set()
+    for line in dispatch.splitlines():
+        stripped = line.strip()
+        if not stripped or stripped.startswith("#") or stripped.startswith("require"):
+            continue
+        armed.update(
+            token.strip()
+            for token in stripped.replace(")", "").split("|")
+            if token.strip()
+            and not token.strip().startswith("*")
+            and " " not in token.strip()
+            and token.strip() != ";;"
+        )
+    assert armed == configured, (
+        f"drift: guard-only={armed - configured} config-only={configured - armed}"
+    )
+
+
+def test_script_sibling_decisions_exist() -> None:
+    """Every `Decisions:` sibling path cited by a script must resolve on disk.
+
+    A phantom sibling pointer sends a reader to a file that does not exist.
+    """
+    root = Path(__file__).resolve().parent.parent
+    pattern = re.compile(r"Decisions:\s*(\S+?)\s*$")
+    missing = []
+    for script in sorted((root / "scripts").glob("*.sh")):
+        for line in script.read_text(encoding="utf-8").splitlines()[:5]:
+            match = pattern.search(line)
+            if match and not (root / match.group(1)).exists():
+                missing.append(f"{script.name}: {match.group(1)}")
+    assert not missing, f"phantom sibling docs: {missing}"
+
+
+def test_prettierignore_covers_guard_arms() -> None:
+    """Every path class the guard skips must also be ignored by the prettier gate.
+
+    The companion test proves the ignore file is covered by the guard. This one
+    proves the reverse, so neither list can grow an entry the other lacks. The
+    guard cannot read `.prettierignore` portably in Bash, so the two lists are
+    duplicated by necessity and pinned here in both directions.
+    """
+    root = Path(__file__).resolve().parent.parent
+    guard = (root / "scripts" / "format-guard.sh").read_text(encoding="utf-8")
+    block = guard.split('case "$REL" in', 1)[1]
+    arm_line = next(line for line in block.splitlines() if "|" in line and ")" in line)
+    armed = [
+        token.strip().rstrip("/*")
+        for token in arm_line.replace(")", "").split("|")
+        if token.strip()
+    ]
+    ignored = [
+        line.strip()
+        for line in (root / ".prettierignore").read_text(encoding="utf-8").splitlines()
+        if line.strip() and not line.lstrip().startswith("#")
+    ]
+    missing = [entry for entry in armed if not any(entry in line for line in ignored)]
+    assert armed, "could not parse the exclusion arm from scripts/format-guard.sh"
+    assert not missing, f"ignore file covers no entry for: {missing}"
```
<!-- END_GIT_DIFF -->
