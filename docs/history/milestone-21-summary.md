# Milestone 21 Summary

**Date:** 2026-09-26
**Tasks Compacted:** 7 (266–272)

## Source Distribution

| Source       | Count |
| ------------ | ----- |
| manager      | 7     |
| orchestrator | 0     |
| telegram     | 0     |

## Architectural Changes

Prompt-contract milestone plus a full V2 platform migration. Tasks 268–271 each changed shipped-prompt behavior and bumped `<system_version>` 9.41.0 → 9.46.0: auditable brainstorm trigger with fragment-11 repair, a positive Manager-facing output-style contract, machine-enforced Strict Tooling Gates on all 13 stack skills with the dead `stacks/` folder removed, and a comprehensive executable-handoff contract for Programmer XML. Task 267 added the source-verified manager-decisions MCP contract doc. Task 272 migrated the live platform to Opencode 2.0.18 + OpenChamber 2.0.2 with dual-key V1/V2 configs and a stable server-password sync that fixed the V2 401. Task 266 was the previous release ceremony (v9.41.0 + milestone-20 archive).

## Files Modified

| File | Change |
| ---- | ------ |
| `docs/history/milestone-20-summary.md` | new: 33-task compaction (266) |
| `docs/manager-decisions.md` | new: six-tool contract + drift table (267) |
| `docs/setup.md` | cross-link to manager-decisions (267) |
| `README.md` | doc links (267); V2 wording + plugins/cli.json (272) |
| `docs/openchamber-tailscale.md` | V2 version + password-sync section + 401 rows (272) |
| `LLM.txt` | V2 install subsection + password runbook (272) |
| `prompts/fragments/01-system_version.md` | 9.41.0 → 9.42.0 (268) → 9.43.0 (269) → 9.44.0 → 9.45.0 (270) → 9.46.0 (271) |
| `prompts/fragments/02-role.md` | answer-first after persona bracket (269) |
| `prompts/fragments/07-agent_skills_registry.md` | strict-gate suffix on 13 stack lines (270) |
| `prompts/fragments/09-hands_protocols.md` | strict tooling gate + fallback/skip schema (270); executable-handoff contract (271) |
| `prompts/fragments/11-execution_workflow.md` | conditional brainstorm step, seven seats, blowsh pointer (268) |
| `prompts/fragments/12-brainstorming_protocol.md` | `<auditability>` one-line rule (268) |
| `prompts/fragments/13-constraints.md` | positive output-style contract + tell rules (269) |
| `prompts/fragments/20-communication_examples.md` | prose good-versus-bad pairs (269) |
| `system-prompt.md` | regenerated each bump 9.42.0 → 9.46.0 |
| `agents/cognitive-executor.md` | brainstorm audit line (268); style mirror (269) |
| `skill-templates/<13 stacks>/SKILL.md` | new Strict Tooling Gate sections (270) |
| `skill-templates/testing-strategy/SKILL.md` | stacks pointer repointed to skill gate (270) |
| `skill-templates/verification-before-completion/SKILL.md` | mandatory gate section (270) |
| `stacks/` (5 YAMLs) | deleted, toolchain carried into skills (270) |
| `opencode.json` (repo + global) | dual-key V1/V2 compat (272) |
| `~/.config/opencode/cli.json` | new: V2 native global client config (272) |
| `tests/test_prompt_sync.py` | version pins 9.42.0 → 9.46.0 + regression gates (268–271) |
| `tests/test_skill_registry.py` | stacks read/assertion dropped (270) |
| `CHANGELOG.md` | per-task Parse-Then-Append entries (all) |

## Criteria Met

| Task | Acceptance Criteria | Status |
| ---- | ------------------- | ------ |
| 266 | Archive first + completed/ empty; Unreleased empty under 9.41.0; suite + sync + prompt gates; task lint; push script strict + executable; MCP-staged, no commit; Manager handoff | ✅ Met (7/7) |
| 267 | Six tools with signatures/effects/failures; file:line cites + BRAIN_MODEL correction; drift reported-not-fixed, zero source edits; enum/store/field contracts; README + setup links; Unreleased entry; suite + sync + lint green | ✅ Met (7/7) |
| 268 | Fragment-11 seven seats + conditional; zero old-panel hits; user-prompts → blowsh; protocol audit line; executor mirror; 9.42.0 + byte-identical regen; Unreleased; suite + lint green | ✅ Met (8/8) |
| 269 | Plan approved pre-edit; G1–G10 addressed/deferred; positive model; length budgets; structure rule; principle-based tells; open/close rules; C1 raised; 9.43.0 regen + pin; Unreleased | ✅ Met (10/10) |
| 270 | 13 skills with exact strict sections; strict configs; completion gate; toolchain preserved; stacks/ deleted + test/pointer fixed; registry-consistent; framework enforcement; Unreleased; suite + lint; grep proofs | ✅ Met (10/10) |
| 271 | Complete XML contract; placeholder/omission/vagueness bans; regression proof; prompt sync; targeted + lint green; CHANGELOG | ✅ Met (6/6 AC; Local TODO section left unchecked — sealed as-is) |
| 272 | Opencode ≥ 2.0.15 (2.0.18); OpenChamber ≥ 2.0.0 (2.0.2) + sessions; no V1-only refs; 7/7 MCP + plugins load; lint + tests green; global install migrated | ✅ Met (6/6) |

## Individual Task Summaries

### Task 266: Release v9.41.0 with milestone-20 archive

- **Type:** feature
- **Source:** manager
- **Reasoning:** Cut release v9.41.0 by writing `docs/history/milestone-20-summary.md` covering 33 tasks (229–265) and moving them to `tasks/archive/` first, leaving `tasks/completed/` empty. Moved all `[Unreleased]` CHANGELOG entries under `## [9.41.0] - 2026-09-20`, leaving `[Unreleased]` empty with no duplicated headers. Verified with full 686-test suite, docs-sync, byte-identical prompt assembly, py_compile, and markdown/task lint; wrote executable `/tmp/cognitive-lead-push-release.sh` and closed on verbatim "Approved for closure" with tag `v9.41.0` public.

### Task 267: docs: manager-decisions MCP tool schemas and usage contract for agents

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Wrote `docs/manager-decisions.md` (10 sections) as the source-verified contract for all six `manager_decisions` tools, every claim pinned by `file:line` citations at commit `0183433`. Corrected the issue body's false `DECISION_MODEL else BRAIN_MODEL` claim: only `DECISION_MODEL` overrides the default; `BRAIN_MODEL` is never read. Drift shipped as reported-not-fixed with zero server/skill edits; cross-linked README + setup; Brain QA + technical APPROVED; closes GitHub issue 25.

### Task 268: Make the brainstorm trigger auditable and repair fragment 11

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Resolved the fragment 11 vs 12 contradiction (automatic step 2 vs conditional trigger) by making step 2 a conditional check naming the seven `<personas>` seats. Added the `<auditability>` rule: every plan states `Brainstorm: required | not required — reason`; cross-disciplinary plus hard-to-reverse work requires the full report, mirrored in the executor Planning Gate. Repaired the dead `user-prompts/` pointer to the `blowsh` skill; root cause was Task 180's snake_case-only grep missing display-form "Critical Thinker". Bumped 9.41.0 → 9.42.0, regenerated prompt, QA_PASSED + technical APPROVED.

### Task 269: Make the Hands' output human-readable — output-style gap repair

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Ran four parallel research subagents plus a Manager-requested seven-seat brainstorm (O1 minimal style-contract patch selected), plan explicitly approved before edits. Closed gaps G1–G10 with a positive 8-rule output-style contract: answer-first after the persona bracket, length budgets (short 2–5 sentences; normal 80–180 words or ≤ 5 bullets), structure rule (prose 1–2, flat bullets 3–7, table only for repeated attributes), no preamble/recap, principle-based AI-tell rules replacing the 5-phrase ban. Kept English-only per stored ruling; bumped 9.42.0 → 9.43.0, QA_PASSED + APPROVED.

### Task 270: Stack skill strict tooling gates and the stacks/ folder decision

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Proved `stacks/` had no live runtime consumer and deleted all 5 YAMLs after carrying every toolchain command into the owning skills. Researched all 13 stack skills and injected a uniform Strict Tooling Gate section into each (toolchain table, strict config + flags, fail-fast gate order, hallucination traps, evidence rows). Added framework enforcement in `09-hands_protocols.md` + verification skill; bumped to 9.44.0 then 9.45.0 across QA hotfixes; ended QA_PASSED + APPROVED with suite green.

### Task 271: Generate Comprehensive Programmer XML Handoffs

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Root-caused generic handoffs to the template's code-block omission rule and replaced it with an executable-handoff contract (exact paths, complete code/diffs, full commands, named skills with reasons, per-step verification, AC + edge cases, placeholder ban). Brain plan approved by Manager; seat routing Architect + Programmer. Added 3 regression gates; targeted 268 passed, full 689 passed, QA_PASSED, review PO_REVIEW_PENDING, closed on approval.

### Task 272: Full System Upgrade to Opencode V2 and OpenChamber V2

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Upgraded via the official V2 installer to Opencode 2.0.18 and OpenChamber 1.24.2 → 2.0.2 with dual-key compat configs (`permission.shell` alongside `bash`, `plugins` alongside `plugin`, global `cli.json` mirroring `tui.json`; no project `cli.json` by design). All 7 MCP servers load unchanged; fixed the round-3 V2 401 by syncing a stable `OPENCODE_SERVER_PASSWORD` across the service drop-in and OpenChamber `startup.env`. Taught the V2 path in `LLM.txt`, README, and tailscale docs; closed on "Approved for closure" after reviewer APPROVED relay.
