# Task 414: Enhance system-prompt fragments and custom agents with best-practices audit

**File:** `tasks/in-progress/414-enhance-system-prompt-fragments-and-agents.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress
**Started:** 2026-11-22T19:41:48Z

## Source Context

### Variant C: Manager

## Goal

Enhance all custom agents (`agents/`) and system-prompt fragments (`prompts/fragments/`) by applying the best practices discovered in the deep research report `context-reports/agent-harness-system-prompts-research.md` (covering Grok, Claude Code, Codex, Cursor, Cline, Windsurf, Devin, Aider, Augment, DeepSeek, Gemini, OpenAI, Anthropic, Meta Muse). The task must: (1) parse every fragment and every custom agent, (2) feed them to the Brain for an audit that finds gaps, leftovers, wrong things, and anti-patterns, (3) run a multi-seat brainstorming round with the full team (Architect, Designer, Senior Programmer, Planner, Strategist, QA, Code Reviewer) to produce a plan, and (4) implement the agreed enhancements across `prompts/fragments/`, `agents/`, `docs/conventions.md` and `docs/architecture.md` with verification.

## Manager's Notes

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

## Local TODOs

- [x] Phase 1: Gather and feed context to Brain (all fragments + agents + research report) — COMPLETE
- [x] Phase 2: Brain audit — find gaps, leftovers, wrong things vs. best practices — COMPLETE (67 findings, 24 HIGH)
- [ ] Phase 3: Multi-seat brainstorming (Architect, Designer, Senior Programmer, Planner, Strategist, QA, Code Reviewer) for an enhancement plan — PENDING (awaiting Manager decision on Q1)
- [ ] Phase 4: Implement agreed enhancements to fragments/agents
- [ ] Phase 5: Verify (prompt gates, lint_task_file, format Markdown, living-docs sync) — CHANGELOG moved to Phase 4b

## Acceptance Criteria

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

## Verification Evidence

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

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `testing-verification` applied and evidence recorded
- [ ] Prompt gates green: `tests/test_prompt_sync.py` and the assembler identity gate both exit 0, with command and exit code recorded in `## Verification Evidence`

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Over-editing fragments could break the assembled `system-prompt.md` assembly or persona routing; changes to `09-hands_protocols.md` (HQ-only) must not leak into the global governance skill template.
- **Rollback plan:** Git revert of the changed fragment/agent files; `system-prompt.md` is regenerated from fragments, so re-run assembly after revert. No data migration involved.

---

## Phase 1: Context Gathering (Discovery)

### Local TODOs

- [x] Read all fragments and agents via subagents (parallel, up to 4) — never dump multi-thousand-line files inline; use targeted `#Lstart-end` ranges
- [x] Extract `Context-Paths` manifest from discovery report
- [x] Confirm research report loaded: `context-reports/agent-harness-system-prompts-research.md`
- [x] Confirm `system-prompt.md` was read as the assembly-order reference and record its fragment order in the Execution Log

## Phase 2: Brain Audit

### Local TODOs

- [x] Call `brain_turn` under this task ID with `include_bundle` and `context_paths` = all fragment/agent files + research report
- [x] Prompt Brain: "Audit these fragments and agents against the best-practices report. Find gaps, leftovers, wrong things, redundant rules, missing contracts, anti-patterns. Cite file + section for each finding."
- [x] Record Brain audit REPORT in Execution Log (verbatim, never field-shape the result)
- [x] If Brain returns a discovery task instead of a plan, execute it and feed back under the same task ID (max one discovery round)

## Phase 3: Multi-Seat Brainstorming

### Phase 3 Preconditions

- [x] Resolve the panel binding before the seven-seat call. `12-brainstorming_protocol.md` binds the panel to `<personas>`, which after the ADR-009 split holds only `<auto_load>`, and `02-role.md` permits one bracket declaration per response while a seven-seat report needs seven. Either apply the P5 pre-fix to `06-personas-catalog.md`, `12-brainstorming_protocol.md` and `11-execution_workflow.md` first, or record the one-session exception in this file and pass it verbatim into the brainstorm `brain_turn`. — DONE: recorded one-session exception and passed verbatim; brainstorm completed with 7 seats.
- [x] Record the Manager's answer to Q1 (`run phase 3` / `apply p5 first` / `adjust scope`) in this file before the brainstorm call. — DONE: Manager chose "run phase 3" (Option A).
- [ ] After plan approval, call `schedule_tasks(project_root, "id:estimate:deadline[:deps[:milestone]], …")` with the estimate, deadline, dependencies and milestone confirmed in that same approval turn, then call `sync_task_times(project_root)` to stamp `**Started:**`. This task entered `tasks/in-progress/` manually rather than via `claim_next`, so the stamp was never written. Never hand-edit `**Estimate:**`, `**Deadline:**`, `**Depends on:**`, `**Milestone:**` or `**Started:**`. — DONE: sync_task_times stamped **Started:** from git/mtime.

### Local TODOs

- [x] Seat Check: map task domains → seats (Software Architect for structure/contracts, UI/UX Designer for any persona-facing tone, Senior Programmer for implementation, Project Planner for lifecycle, Sprint Strategist for scope, QA Engineer for verification gates, Code Reviewer for audit) — DONE
- [x] Call `brain_turn` as a 7-seat (or subset) brainstorming session with the audit findings as `[fed-context]` — DONE
- [x] Record consolidated enhancement plan (Brain REPORT) with per-seat verdicts — DONE (O1 selected, 3 cycles, 10 assertions)
- [x] Present plan to Manager for approval before implementation (supervised autopilot plan-approval gate) — DONE (approval ask sent)

## Phase 4: Implementation

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

## Phase 5: Verification

### Local TODOs

- [ ] Run `rtk test npx prettier --check "**/*.md"` and record exit code
- [ ] Run the prompt-sync gate (Verification Block 2 command) and record the exit code
- [ ] Run the assembler identity gate (Verification Block 3 command) and record the exit code
- [ ] Run `lint_task_file` on this task file
- [ ] Record all verification evidence in `## Verification Evidence`

## Execution Log & Reasoning

### Phase 1: Context Gathering (Discovery) — COMPLETE

- 4 parallel cognitive-discovery subagents read all 24 numbered fragments (actual: 20 present, 10/17/22/23 missing), 7 persona files, 2 agent files, READMEs, DECISIONS files, and the research report.
- Context-Paths manifests extracted from all 4 subagent reports.
- Discovery issues identified: version mismatch (9.90.1 vs V9.1.0), agentic reasoning numbering (says 1-9, lists 10), duplicated Strict Tooling Gate sentence in skills registry, thin personas catalog, duplicate QA/review brain_turn in 09, Template Preservation vs Placeholder Ban potential contradiction, redundant comms rules in 13, topology contradiction (19 vs DECISIONS), redundant qa-engineer/code-reviewer blocks, manual-mode ADR contradiction, orphaned ADR heading, ADR numbering gap (missing 008), stale citations, em-dash self-violation.

### Phase 2: Brain Audit — COMPLETE

- Called brain_turn (task 414, session ses_dfb6b5151ffeFUfi8ShHXVNimC) with 18 context_paths + research report. Brain returned REPORT (deepseek-v4.1-flash, 110770 input tokens, 34962 output tokens, 23458 reasoning tokens).
- Full output saved at: tasks/.sessions/ses_dfb6b5151ffeFUfi8ShHXVNimC_625cb562/brain_outputs/gw_ede5efeab21a_18aaa9f_916b32c3abe447d4b499600d60b32c77.json
- **67 findings total, 24 HIGH severity**, grouped: Gaps (14), Leftovers (14), Wrong things (28), Anti-patterns (11).
- **Hypothesis verdicts:** H1 confirmed (5 surfaces disagree), H2 confirmed, H3 confirmed, H4 confirmed at 4 (not 3), H5 confirmed worse, H6 confirmed, H7 confirmed in 2 templates, H8 disproven (9.90.1 is current), H9 two genuine cases, H10 one genuine chain (not systemic).
- **Root cause:** 10 invariants live in 2 homes (docs/conventions.md + fragments), 4 in 5 homes. Duplication is the structural parent of most findings.
- **Top 3 highest-consequence:** (1) mode topology contradiction (W1), (2) closure gate self-approval contradiction (W12), (3) double staging sequence (W6).
- **Missing control files (block full verification):** AGENTS.md, prompts/manifest.txt, prompts/stage-manifest.json, prompts/shared/validation-phase.md, tests/test_prompt_sync.py.
- **Brain's decision question (Q1):** Option A (run phase 3 brainstorm now, with one-session exception to W3/W4), Option B (apply P5 first then brainstorm), Option C (adjust scope).
- **Brain's P1-P10 enhancement plan:** P1 topology, P2 prompt head (delete Template Preservation + worked examples + precedence block + move Hard Invariants + remove 2026 line), P3 collapse approval literals + ZAC, P4 one lane-transition contract, P5 rebind brainstorm panel, P6 resolve discovery skill contradiction, P7 one output contract, P8 canonical home for shared mandates + 4 assertions, P9 documentation truth-up, P10 token diet.
- **Manifest path verified:** `prompts/manifest.txt` exists (confirmed). `prompts/fragments/personas/manifest.txt` also exists (personas manifest). `prompts/fragments/manifest.txt` does not exist (Brain R11 concern does not apply — the task file correctly references the personas-level manifest). Manager's Notes line 24 (`manifest.txt` relative to personas directory) is correct.

### Brain Audit Report (verbatim)

**[Senior Programmer]**

The audit is complete over the full bundle. Two of your hypotheses hold harder than stated, one is disproven, and the bundle surfaced nine defects that were invisible at round two. The dominant root cause is not a bad rule. It is that ten invariants now live in two homes, `docs/conventions.md` and the prompt fragments, and four of them live in five homes.

**Scale:** 67 findings, 24 high severity. IDs are renumbered contiguously for this round. Citations use file plus heading, because path-injected bodies carry no line range.

<reasoning_log>

1. Logical dependencies and constraints.
   1.1 Policy first. The Manager ordered a structured REPORT, "do not invent files", and "use only the provided context". My Strict Approval Gate forbids emitting `<hands_implementation_task>` before an approved plan, and task 414's own Phase 3 has not run. So this turn is report only, closing with one decision ask.
   1.2 Order of operations. Audit, then plan, then agenda, then ask. Any reordering hands the Manager a plan built on an unaudited base.
   1.3 Prerequisites. The bundle now carries task 414, `docs/conventions.md`, `docs/architecture.md`, `docs/data_model.md`, `DESIGN.md`, both `DECISIONS.md` files, `agents/cognitive-discovery.md`, path-injected bodies for nine fragments and four personas, and the research report. `AGENTS.md`, `prompts/manifest.txt`, `prompts/stage-manifest.json`, `prompts/shared/validation-phase.md` and `tests/test_prompt_sync.py` did not arrive. That is a declared limit, not a reason to stall.
   1.4 Manager constraints. Manual mode, fenced blocks, no task-text ferrying, four finding groups, file plus section citation, severity per finding, top-10 plan, brainstorm agenda.

2. Risk assessment.
   2.1 Highest-consequence item is the mode topology. Five surfaces disagree, and one of them orders the exact behaviour the platform forbids. Every other severity grade is measured against an undecided contract, so it must be first.
   2.2 Second highest is the closure gate. `agents/cognitive-executor.md` §Saga self-sufficiency orders the Hands to "play the Manager role yourself" while §Review-approval relay says a self-decision never satisfies the gate, and `personas/code-reviewer.md` says the same. That pair can produce an unauthorized commit, which is the only irreversible action in the system.
   2.3 Third is the double staging sequence. Two files order `stage_and_inject_diff` and then `qa_transition`, which stages again, while the executor's own Task Lifecycle 3 forbids exactly that. The corrupted artifact is the diff block that QA and the reviewer actually read.
   2.4 Low risk. This turn is analysis over supplied text. No file claims beyond what was injected.

3. Abductive reasoning and hypotheses.
   3.1 Hypothesis: most defects share one cause, no single owner per invariant. Tested by counting homes. Approval literals 5, banned phrases 3, reference codes 3, translation gate 4, skill-loading quantifications 3, finalization sequences 3, ZAC statements 6, shared mandates 2 (conventions plus fragments). Confirmed.
   3.2 Hypothesis: several defects are ADR-009 split artifacts. Tested: `12-brainstorming_protocol.md` and `11-execution_workflow.md` both bind the panel to `<personas>`, and the path-injected `06-personas-catalog.md` holds only `<auto_load>`. Confirmed, and it blocks the phase this task needs.
   3.3 Hypothesis: defects entered after an ADR banned them. Tested: `agents/cognitive-discovery.md` re-acquired embedding dimensions, chunk constants, server paths and a line-order anchor, which is the class the "Prompts are for the LLM, not the auditor" ADR stripped from the executor. Confirmed.
   3.4 Considered and tested against the Manager: "stale version numbers". The version fragment reads 9.90.1 and ADR-011 bumped to 9.90.1, so the fragment is current. The stale numbers are elsewhere, in ADR rollback anchors pointing at 9.71.0, 9.75.0 and 9.77.0. Reported as W27, not as a fragment defect.
   3.5 Considered and rejected: the Manager's em-dash hypothesis as a systemic defect. The ban is on chaining, not the character. One genuine chain plus one semicolon exists, in `24-language_policy.md` §Inside English. Reported as W19, LOW, together with two other self-violations of the same prose rules.

4. Outcome evaluation and adaptability.
   4.1 Nine round-two findings hardened once the full text arrived. W13 moved from MED to HIGH because `personas/qa-engineer.md` contradicts itself, not just the workflow fragment. L4 moved from three duplicate ADRs to four. W8 gained a second conflicting clause, `20-communication_examples.md` Example 4.
   4.2 Two new conflicts appeared only from the pairing of injected bodies. W22, bullets versus render, and W23, prose closure ask versus prose-ask ban. Both are HIGH and neither was visible at round two.
   4.3 One draft finding was dropped. A claim that `docs/architecture.md` omits manual mode entirely does not survive inspection, because its Agent Architecture line still says "Runs in external chat (manual) or via MCP (automatic)". The defect is narrower and I stated it that way.

5. Information availability.
   5.1 Available and used: the assembled system prompt, path-injected bodies for fragments 05, 06, 07, 08, 09, 13, 19, 20, 24, personas for QA, Code Reviewer, Senior Programmer and Software Architect, both agent files, both DECISIONS files, `docs/conventions.md`, `docs/architecture.md`, `docs/data_model.md`, `DESIGN.md`, task 414, and the research report.
   5.2 Unavailable and declared: `AGENTS.md`, `prompts/manifest.txt`, `prompts/stage-manifest.json`, `prompts/shared/validation-phase.md`, `tests/test_prompt_sync.py`, `prompts/fragments/README.md` (carried from round one), fragments 10, 17, 22, 23, and all `skill-templates/*`.
   5.3 No file system, shell or network access by design. Every citation names a heading that exists in the supplied text.

6. Precision and grounding.
   6.1 I verified three things as correct before writing, so the report is not one-sided. `docs/conventions.md` §Agent Permission Schema V1 to V2 matches both agent frontmatters exactly. `01-system_version.md` matches ADR-011. The approval-literal wording agrees word for word across its five homes, so the defect is placement, not drift, and consolidation is a refactor rather than a behaviour change.
   6.2 Where the artifact is right I say so. Where a claim needs the live runtime, such as `@google/design.md`, I mark it unverified instead of asserting a violation.

7. Completeness.
   7.1 Four requested categories are separate tables, severity is defined once, each table is sorted high to low.
   7.2 The top-10 plan closes every HIGH finding. I checked the mapping explicitly.
   7.3 Incompleteness is declared. Three control files and one include partial are absent, so assembly order and stage routing stay unverified.

8. Persistence and patience.
   8.1 Task 414's first Acceptance Criterion asks for 24 numbered fragments. The artifact carries 20, and 10, 17, 22, 23 were never supplied. I report the arithmetic and rewrite the criterion as part of the plan rather than marking the box or refusing the audit.
   8.2 Nothing failed, so nothing is retried.

9. Inhibit response.
   9.1 Pre-emit check. No XML implementation task. No claim of file modification. No invented path. No semicolons or em-dash chains in my own prose. Exactly one decision question with one answer slot.
   9.2 Verified. Emitting.
   </reasoning_log>

## 1. Verdicts on the hypotheses you named

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

## 2. Scope discipline

Task 414 says `09-hands_protocols.md`, `agents/*` and `skill-templates/*` are HQ-only and must not be audited as third-party project files. I read that as a scoping guard, not an exemption. I audited them, and I judged them by the standard they claim to hold, not by a downstream project's standard. `DESIGN.md` and the UI-facing rules are graded as HQ scaffolding even though `docs/architecture.md` calls this a documentation-only repository.

**Severity.** HIGH means two rules cannot both be obeyed, or the prompt names something that does not exist or cannot run. MEDIUM means duplicated, stale or ambiguous, with obedience still possible. LOW means hygiene.

## 3. Verified clean

Three items I checked before finding fault, so the negatives are trustworthy.

- `docs/conventions.md` §Agent Permission Schema V1 to V2 matches both agent frontmatters exactly, including `steps: 512`, the catch-all allow refined by ZAC denies, and the deny-first discovery surface with explicit `edit` and `shell` denies.
- `01-system_version.md` reads 9.90.1, which matches ADR-011's bump. No stale version exists in the fragment itself.
- The approval-literal clause agrees word for word across `13-constraints.md`, `24-language_policy.md`, `personas/code-reviewer.md` and both executor sections. The rule did not drift. It was copied. That makes consolidation a refactor rather than a behaviour change, which lowers the risk of P3.

## 4. Gaps

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

## 5. Leftovers

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

## 6. Wrong things

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

## 7. Anti-patterns from the report

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

## 8. Prioritized enhancement plan

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

## 9. Recommended multi-seat brainstorming agenda

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

## 10. The decision I need now

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

# brainstorming_session

**Paste this block verbatim into task 414 under `## Execution Log & Reasoning`, replacing the `Phase 3 — IN PROGRESS` line with it.**

## summary

Two mode ADRs were never in conflict because "mode" names three unrelated axes: transport, autonomy, emission. Nine surfaces assert a topology and no two agree on which axis they describe. The resolution is to separate the axes and decide each once, then let every surface cite the decision instead of restating it.

## persona_responses

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

## tradeoffs

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

## conflict_resolution

**C1. Cycle count, Architect versus Strategist.** The Architect treats P1 through P6 as one coherent first cycle because they touch overlapping passages. The Strategist splits them on rollback granularity. **Strategist wins.** Overlap is an edit-ordering argument, not a commit-grouping argument. A failed consolidation must not take a good deletion down with it.

**C2. Multi-label rule, Designer versus fragments `02` and `06`.** The Designer wants a carve-out in `06`. `06` currently prohibits a second Speaking-as line outright. **Designer wins, and the amendment is P5 scope.** The prohibition was written before brainstorm existed in its current form. The one-session exception already proves the carve-out works.

**C3. Assertion count, QA versus Reviewer.** QA wants coverage of every conflicted rule. The Reviewer wants a phantom-name allowlist and a verification step. **Partial win for each.** QA gets ten presence-and-absence assertions scoped to conflicting rules. The Reviewer gets the allowlist as a separate mechanism. Twenty-four assertions is over-fitting, and the allowlist covers a defect class that assertions cannot.

**C4. Proving P10, Programmer versus QA.** The Programmer's P10 removes content by design, which makes a before-and-after byte comparison impossible. **QA wins.** Identity runs source-to-artifact, and the plan must state that direction or the assertion will be implemented backwards.

**C5. Closure shape, Planner versus fragment `11`.** `11` step 8 orders a dedicated closure task. `personas/code-reviewer.md` orders a single final-closure XML under the same `task_id`. **Planner wins.** A closure task would re-prove an entire lifecycle for one `git mv` and one commit. Recorded as new finding W29.

**C6. Duplicate-block testability, QA versus the audit's own phrasing.** The audit asked for "an acceptance test for no duplicate normative block". QA demonstrated no such test can exist without false positives. **QA wins and the audit is corrected.** Record it as a review responsibility proven by grep, and stop promising a gate.

## options_ranked

**O1, rank 1. Full plan, three cycles, with six seat amendments.**
Approve P1 through P10 with four changes: P1 effort M across nine surfaces, three cycles instead of two, ten assertions instead of twenty-four, and W29 added to P4.
Closes all 24 HIGH findings. Reuses the task file's existing Phase 4a and 4b shape. No new task numbers. Cost is one approval now and three gate checkpoints inside one task.

**O2, rank 2. Cycle A only, defer the rest.**
P1, P4, P5 and P7 now, re-audit before Cycle B.
Closes the four findings that currently make two rules un-obeyable. Smallest possible diff. Cost is that eight of the nine contradictory mode surfaces keep contradicting until a second audit, and W1's fix stays half-applied.

**O3, rank 3. P5 first, then re-run Phase 3 under corrected rules, then the full plan.**
This was the audit's Option B.
Cost is a whole phase spent on a rule that O1 already fixes inside P5, and a second brainstorm that would reconvene the same seven seats with the same 67 findings and reach the same conclusions. Pure overhead now that the session has run.

## final_recommendation

**Approve O1.** Decided by **T1**, because leaving two transport readings alive keeps a self-approval path open and that is the only irreversible action in the system. Decided by **T6**, because a failed consolidation must not roll back a good contradiction fix. Decided by **T3**, because ten assertions cover every rule that can re-diverge while twenty-four carry permanent cost for one-time corrections.

O2 loses because it applies half of P1. A topology fix that corrects four surfaces and leaves five asserting the old one is worse than either state, because the next reader cannot tell which is current. O3 loses because its premise was that Phase 3 could not run. It ran, it produced this report, and re-running it costs a phase to reach the same place.

## selected_path

**O1: P1 through P10 across three cycles, with the seat amendments.**

**First three execution steps:**

1. **P1, topology, all nine surfaces.** Decide the three axes explicitly. Let "Unify Architecture to 100% Brain Turn" survive for transport and supersede "Decouple True Manual Mode" with a dated note rather than deleting it. Rewrite the executor mode-line template for both modes with no escape hatch and well-formed backticks. Delete the §Saga self-approval sentence. Align `docs/architecture.md` §Topology, §Agent Architecture and §Key Data Flows. Effort M, not S.
2. **P4, one lane-transition contract.** Authoritative sequence becomes `lint_task_file` then `qa_transition(task_file_path, modified_files)`. Delete fragment `09` implementation summary step 2. Fix executor §Task Lifecycle 2 to call `claim_next` instead of `git mv`. Delete the closure-task sentence in `11` step 8 and add W29 to the closed set.
3. **P5 plus P7, the two small HIGH closures.** Rebind the brainstorm panel to the `brainstorm` stage in `prompts/stage-manifest.json` and carve out the multi-label rule in `06`. Fix the QA verdict literal in `11` step 6 and in the persona. Then the output contract: render replaces bullets in `13`, English always, and emission stated as a condition rather than an OR.

Verification of `prompts/stage-manifest.json` gates **P8 and P9**, not these three steps. It runs before Cycle B opens.

---

## Two corrections to the audit you should know before approving

**W1 radius.** I reported five surfaces. The count is nine, and they are named in the Architect seat above. This moves P1 from S effort to M and is the single reason the three-cycle split exists rather than two.

**W29, new.** Closure has two incompatible shapes. `11-execution_workflow.md` step 8 orders a dedicated closure task. `personas/code-reviewer.md` orders a single final-closure XML under the same `task_id`. The audit missed it. The Planner resolved it in favor of the XML, which is now in scope for P4.

**One thing I will not claim.** The audit's "roughly 2,300 words saved" on P10 is unverifiable from here. Cycle C must record before-and-after byte counts from the assembler rather than quote a number nobody measured.

---

## Decision

The report above is the plan. It replaces the audit's P1-P10 table at the approval gate and pastes verbatim into task 414's Execution Log.

**One answer slot: `approve` / `adjust` / `re-scope`.**

- `approve` — I record your answer and the panel exception in the task file, close Phase 3, and open Cycle A with P1.
- `adjust` — name the seat verdict or tradeoff you want changed and I re-synthesize without re-running the seats.
- `re-scope` — you cut or reorder the P-set and I rebuild the cycle plan around it.

No XML task block is emitted this turn. The Strict Approval Gate blocks implementation until this plan is approved.

### Phase 3: Multi-Seat Brainstorming — COMPLETE (Manager approved O1: approve)

### Phase 4: Implementation — NOT STARTED

### Phase 5: Verification — NOT STARTED

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
