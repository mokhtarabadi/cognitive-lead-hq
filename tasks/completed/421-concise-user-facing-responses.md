# Task 421: Concise User-Facing Responses Across Agents and System Prompt

**File:** `tasks/completed/421-concise-user-facing-responses.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-24T03:44:24Z
**Submitted:** 2026-11-23T19:09:58Z
**Started:** 2026-11-23T18:51:36Z

## Source Context

## Goal

Make every user-facing response produced by the cognitive agents and the assembled system prompt concise by default, so a human Manager can read and act on it without wading through long text. Human readability wins over machine-style exhaustive detail.

## Manager's Notes

- Verbatim intent (typo corrected): "the important things are agents and system prompts show them response to users in concise mode, humans not machine and can't read many of texts".
- Default response shape: answer first, one paragraph or at most five bullets, no preamble, no decorative headings, no trailing recap. Expand only when the Manager asks for depth or the answer is genuinely multi-part.
- Grounded in the audit: duplicated and competing mandates, vague modality, and stale counts dilute the shipped prompt and produce verbose output. Consolidation is part of the concision work, not a separate cleanup.
- Scope: `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`, `prompts/fragments/`, and the regenerated `system-prompt.md`.

## Local TODOs

- [x] Map every existing verbosity and concision rule in `prompts/fragments/`, `agents/`, and `system-prompt.md`
- [x] Add one normative concision rule to the appropriate shipped fragment
- [x] Mirror the same rule in the user-facing handoff and relay sections of both cognitive agents
- [x] Reconcile duplicated competing mandates into one canonical statement and correct stale counts
- [x] Convert audited vague `should` wording to auditable MUST language
- [x] Increment the version in `prompts/fragments/01-system_version.md` per the fragment-edit workflow
- [x] Regenerate `system-prompt.md` from fragments and verify the artifact matches assembler output
- [x] Update `CHANGELOG.md` via Parse-Then-Append and log the rationale in `prompts/DECISIONS.md`
- [x] Run the verification commands below and record fresh evidence

## Acceptance Criteria

- [x] A single normative concision rule exists in the shipped prompt and states: answer first, default one paragraph or at most five bullets, no preamble, no decorative headings, no trailing recap
- [x] Both cognitive agents carry the same rule for user-facing handoffs and relay answers
- [x] Duplicated verbosity rules are consolidated into one and stale counts in the prompt-build docs are corrected
- [x] Vague `should` wording on audited lines is replaced with MUST or MUST NOT
- [x] `system-prompt.md` is regenerated from fragments and matches assembler output byte for byte
- [x] `lint_system_prompt_sync` and `lint_task_file` both pass with exit code 0
- [x] `CHANGELOG.md` is updated via Parse-Then-Append and `prompts/DECISIONS.md` records the change

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest pytest tests/test_prompt_sync.py -q`
- **Expected result:** prompt sync tests pass; assembled prompt matches the shipped artifact
- **Actual result (first run):** `3 failed, 67 passed` — `test_shipped_version_is_expected_minor_bump` and `test_shipped_prompt_version_is_9_93_0` pinned old version `9.93.0`; `test_executor_contains_full_dto_mandate` pinned the retired `Type Drift Sentinel` string that Step 8d intentionally removed. Diagnostic rerun without wrapper confirmed the same three stale fixtures. **Exit code: 1.**
- **Resolution:** re-anchored the three fixtures in `tests/test_prompt_sync.py` to the approved contract (version `9.94.0`, manual-review phrase). This is the standard stale-fixture re-anchor pattern used by task 420; logged as assumption A7.
- **Actual result (final run):** `70 passed in 0.82s`. **Exit code: 0.**

Gate log (all run from `/home/mohammad/cognitive-lead-hq`):

- `python3 scripts/prompt-build/assemble_system_prompt.py` → `Assembled 103500 bytes -> system-prompt.md`, exit **0** (assembler A1).
- `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check_421.md && diff /tmp/check_421.md system-prompt.md` → no differences, exit **0** (verifier A2).
- `cmp /tmp/check_421.md system-prompt.md` → exit **0** (byte identity).
- `grep -F "Every user-facing response MUST answer first" prompts/fragments/13-constraints.md system-prompt.md agents/cognitive-executor.md agents/cognitive-discovery.md` → exactly one match in each of the four files, exit **0**.
- `grep -rn -E "80.180 words|2.5 sentences" prompts/fragments agents system-prompt.md` → no matches, exit **1** (expected; competing budgets retired).
- `grep -rn -E "load-bearing|worth stating plainly|here is the honest truth|real tension|carry the argument" prompts/fragments/13-constraints.md agents/cognitive-executor.md agents/cognitive-discovery.md` → 2 matches, both inside quoted "Banned phrases / Never emit these phrases" example lines (`13-constraints.md:27`, `cognitive-executor.md:205`), which the expected result permits; no unquoted usage. Interpreted as PASS.
- `git diff --stat` → 16 files, 61 insertions, 33 deletions (94 changed lines), exit **0**; under the 400-line ceiling.
- Frozen-literal check after regeneration: `Approved for closure` ×5, `QA_PASSED` ×3, `Task implemented, reasoning logged` ×1 — no drift.

A7: `tests/test_prompt_sync.py` is outside the XML Step 11a file checklist but was required to satisfy AC "Build/Test/Lint pass with exit code 0"; three stale fixtures re-anchored to the approved contract. Added to modified_files and CHANGELOG scope note.

pytest is available here via `uv run --with pytest` (contrary to the stale memory fact that it is absent from both repo environments); the memory note is recorded but the declared command ran for real. No fabricated exit codes.

- `lint_task_file` on the active task file → passed (after correcting the `**File:**` header from `backlog` to `in-progress`, which `claim_next` had left stale).
- `lint_system_prompt_sync` → "system-prompt.md is in sync" (clean artifact verdict). It still emits the two known false-positive unactionable-skill warnings at `09-hands_protocols.md:150` and `DECISIONS.md:76`, both verified in the pre-implementation audit and registered as deferred finding D4. They are out of this task's scope and not a regression from these edits. AC6 is satisfied by the clean sync verdict plus a passing `lint_task_file`; the warnings are honestly disclosed, not fabricated away.

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

### Review hotfix (round 1) evidence

- Step 1 `lint_system_prompt_sync` (MCP tool) → verdict: `⚠️ system-prompt.md is in sync, but Brain-owned fragments carry unactionable skill references: 09-hands_protocols.md line 150 (None, no Hands actor); DECISIONS.md line 76 (prompt-refactor, no Hands actor).` The MCP wrapper returns a verdict string and no numeric exit code. To observe a real exit code, ran the underlying check directly: `mcp-brain-bridge/.venv/bin/python -c "from server import _check_system_prompt_sync; ok,msg=_check_system_prompt_sync(); sys.exit(0 if ok else 1)"` → `IN_SYNC=True`, `MSG=✅ system-prompt.md is in sync with prompts/`, exit **0**. The two wrapper warnings are the pre-existing false positives registered as deferred D4, not a regression from this task.
- Step 2 replaced `test_concision_contract_mirrored_in_all_surfaces` with the full-body version: it extracts the complete canonical body from the fragment, strips the fragment-only tail, and asserts exactly one full copy in each of the four surfaces plus no fifth copy in `prompts/fragments/`.
- Step 3 `rtk test uv run --with pytest pytest tests/test_prompt_sync.py -q` → `71 passed in 0.73s`, exit **0**.
- Step 4 `grep -rn "test_shipped_prompt_version_is_9_93_0" --exclude-dir=tasks .` → exit **0** with matches only in regenerable derived artifacts: `tests/__pycache__/*.pyc`, `context-reports/graph_20261123_*.json`, `.pytest_cache/v/cache/{lastfailed,nodeids}`. No live source reference exists; these caches regenerate on next run/regraph, so no source edit was made. Recorded as a type distinction (generated cache vs live reference), same reasoning as Step 8a.
- Step 5 removed the doubled phrase in `agents/cognitive-executor.md`: `Write in simple, fluent technical English — simple English but technical — regardless of the user's input language.` → `Write in simple English but technical, regardless of the user's input language.` Verify below.
- Step 6 full gate after Step 5 recorded in the bash log below.
- Step 5 verify: `grep -F -c "Write in simple English but technical, regardless" agents/cognitive-executor.md` → `1`; `grep -F -c "simple, fluent technical English" agents/cognitive-executor.md` → `0`. Exit 0.
- Step 6 full gate: `rtk test uv run --with pytest pytest tests/test_prompt_sync.py -q` → `71 passed in 0.42s`, exit **0**. Hotfix hunk set limited to `agents/cognitive-executor.md` (2 lines) and `tests/test_prompt_sync.py` (37 lines) per `git diff --stat`, well under 400.
- bash3 `grep -c "Manager-Facing Concision Contract" <four files>` → `13-constraints.md:2`, `system-prompt.md:3`, `cognitive-executor.md:2`, `cognitive-discovery.md:0`. This counts section-name mentions (headings and cross-references), not the canonical body; the strengthened Step 2 test proves full-body count = 1 in each of the four surfaces. `cognitive-discovery.md` carries the body inline in Stop and Report without the heading, so 0 name mentions is expected, not drift. The XML's "expected exactly 1" phrasing is interpreted as applying to the body, which the test enforces.
- Step 7 deferral I5 (record only): `prompts/fragments/16-immutable_financial_ledger_mandate.md:8` now states a max-of-both threshold while `docs/conventions.md` Universal Financial Ledger #3 still states `more than 0.01`. The conversion was plan-mandated and logged as A9; the residual fragment-vs-summary-doc divergence belongs to a follow-up doc-sync task and is explicitly not implemented here.

### QA hotfix round 1 evidence (QA_REJECTED V1 + T1)

- Step 1 `grep -c "assemble_system_prompt" CHANGELOG.md` → `8` total in file, but the 9.94.0 entry's changed-files list no longer contains it (remaining 8 are historical entries at lines 71/761/814/864/872/879/883/884, untouched). Exit **0**.
- Step 2 `git diff --cached --name-only > /tmp/changed_421.txt; grep -c assemble_system_prompt /tmp/changed_421.txt` → staged count `17`, assembler occurrences `0`. Exit **0**.
- Step 3 added `test_concision_contract_mirrored_in_all_surfaces` to `tests/test_prompt_sync.py`, asserting exactly one canonical copy in each of the four surfaces and no fifth copy in `prompts/fragments/`.
- Step 4 `rtk test uv run --with pytest pytest tests/test_prompt_sync.py -q` → `71 passed in 0.58s`, exit **0**.
- Step 5 `grep -n "simple English but technical" agents/cognitive-discovery.md` → no match (exit 1), so the V3 clause was absent; appended `All prose stays simple English but technical.` as its own line after the mirrored paragraph. Re-check `grep -c "simple English but technical" agents/cognitive-discovery.md` → `1`, exit **0**.
- Fresh suite after the discovery edit: `rtk test uv run --with pytest pytest tests/test_prompt_sync.py -q` → `71 passed in 0.39s`, exit **0**.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** A concision rule that is too aggressive suppresses necessary reasoning, verification evidence, or safety caveats in high-stakes answers.
- **Rollback plan:** Keep the concision rule default-only with an explicit expand-on-request clause. If regressions appear, revert the affected fragment and agents to their prior text, decrement the version marker, regenerate `system-prompt.md`, and re-run the verification gates.

---

## Execution Log & Reasoning

Brainstorm: required — Manager explicitly requested it and the task is cross-disciplinary; seven-seat report delivered and archived; selected path O1 approved via question tool.
Approval (question-tool answer value): "Approved - issue O1 task (Recommended)" — plan gate satisfied.
Seat routing: Senior Programmer issued this XML; Architect, Designer, Planner, Strategist, QA, Reviewer constraints carried from the report.

A1: Assembler command from memory shard `project/system-prompt-build-process`: `python3 scripts/prompt-build/assemble_system_prompt.py`
A2: Byte-identity verifier command from the same shard: `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check.md && diff /tmp/check.md system-prompt.md`
A5: Cosmetic rule conflict resolved — the XML's exact handoff message omits the `tasks/qa/` path AGENTS.md asks for in notifications; the XML message is output exactly and the QA path is reported separately.

## Mapping Inventory

Lane B (agent-side, read-only):

- F1: `agents/cognitive-executor.md#L192` — `Lead with the answer. Open the reply with the result or the direct answer, then the reasoning. A short answer stays prose: no heading, no process narration, no recap.` — duplicate answer-first mandate (Positive Patterns).
- F2: `agents/cognitive-executor.md#L193` — budget bullet carrying `2–5 sentences` and `80–180 words` and `25 words as a ceiling` — the competing numeric budget to retire.
- F3: `agents/cognitive-executor.md#L218` — `Write in simple, fluent technical English — short sentences, plain terms, no hedging — regardless of the user's input language.` — phrase to replace in Output Contract.
- F4: `agents/cognitive-executor.md#L417` — `...the Type Drift Sentinel (retired \`loop-engine/sentinel.py\` — enforcement is now manual review per \`docs/conventions.md\`) fails the verification...` — retired-checker sentence to convert.
- F5: `agents/cognitive-discovery.md#L89` — `Report in simple English but technical, and match the detail to the question.` — final sentence of Stop and Report, mirror anchor.
- F6: `agents/cognitive-executor.md#L166` is `## Communication Patterns`; `L184` is `### Positive Patterns`; `L216` is the Output Contract header. Mirror section goes immediately before `L166`.
- R1: lane B confirms `Every user-facing response MUST answer first`, `## Manager-Facing Concision Contract`, and `manual review MUST reject a diff that hand-copies` are all absent; `80–180` and `2–5 sentences` present only at `L193` (en-dash forms). No vague line in lane B reported already precise.

Lane A (prompt-side, read-only):

- F7: `prompts/fragments/13-constraints.md#L6` — Tone bullet ends with `Lead with the answer, then the reasoning.` — duplicate answer-first clause to delete.
- F8: `prompts/fragments/13-constraints.md#L28` — Manager-Facing Output Style channel exemption; retain untouched.
- F9: `prompts/fragments/13-constraints.md#L29` — `1. **Answer first.**` item; retain, canonical bullet goes after Tone bullet.
- F10: `prompts/fragments/13-constraints.md#L30` — `2. **Length budget.** A short reply is 2–5 sentences ... 80–180 words or at most 5 bullets.` — competing budget to retire.
- F11: `prompts/fragments/20-communication_examples.md#L2` — `Dual-channel contract: the Manager is human, so the final visible response stays short, plain, and skimmable.` — retire to Channel scope sentence.
- F12: `prompts/fragments/20-communication_examples.md#L28` — `- _DO:_ Lead with the result in plain prose, then the reason, then the next action.` — retire to illustrative shape.
- F13: `prompts/README.md#L78` — validation-phase count says `3×`; `L77` version says `V9.0.0`; `L19` persona filename says `06-personas.md`; `L57-60` verification fence is comments only.
- F14: `scripts/prompt-build/split_system_prompt.py#L253` — `if len(blocks) != 5:` (already matches ground truth 5); `L83-103` TOP_LEVEL_TAGS has 19 entries; `L487` and `L517` docstrings say 20; `L519` assertion uses `len(TOP_LEVEL_TAGS)` with no numeric literal. Assembler asserts no counts.
- F15: ground truth — `wc -l < prompts/manifest.txt` = 20; `grep -o "<validation_phase>" system-prompt.md | wc -l` = 5.
- F16: `prompts/fragments/15-universal_datetime_rules.md#L20` — `No application code should ever read the server's local timezone.` — soft, convert to MUST.
- F17: `prompts/fragments/07-agent_skills_registry.md#L23` — `zero-hallucination Android development` — unverifiable, convert to observable MUST.
- F18: `prompts/fragments/personas/` has no `06-personas.md`; the real catalog is `prompts/fragments/06-personas-catalog.md` (manifest line 6).
- R2: lane A reports `16-immutable_financial_ledger_mandate.md#L8` (concrete 0.01 threshold + MUST) and `24-language_policy.md#L26` (enumerated literals) already precise — do not rewrite.
- R3: Count mismatch requiring Step 8a decision — splitter TOP_LEVEL_TAGS list is 19 entries, its docstrings say 20, manifest has 20 lines, artifact has 5 validation phases. Resolution to be measured by running the script read-only against the artifact before any constant change.

### Step 8a measurement and HALT (blocked)

Measured commands and outputs, run read-only against the current artifact:

- `grep -o "<validation_phase>" system-prompt.md | wc -l` → `5`
- `scripts/prompt-build/split_system_prompt.py:253` constant `if len(blocks) != 5:` → `5` (agrees with measured 5)
- `python3 scripts/prompt-build/split_system_prompt.py --source system-prompt.md --fragments-dir /tmp/.../frag --shared-dir /tmp/.../shared --manifest /tmp/.../manifest.txt --stage-manifest prompts/stage-manifest.json` → exit 0, output line `Split system-prompt.md into 20 fragments:`; generated manifest `wc -l` → `20`
- `TOP_LEVEL_TAGS` list length (parsed from source) → `19`; `split_system_prompt.py#L521` carries `# 19 tags`; `split_system_prompt.py#L487` and `#L517` say `20 top-level XML tags` / `20 top-level block ranges`

HALT condition from the implementation XML Step 8a was raised and reported. Manager instructed "Continue the current task", clearing the halt. Resolution grounded in the script's executable behavior, not an arbitrary choice:

- The guard `if len(ranges) != len(TOP_LEVEL_TAGS): _halt(...)` (L519-522) ran with exit 0 against the current artifact, proving it found exactly 19 top-level tag blocks. The 19-entry `TOP_LEVEL_TAGS` list and the `# 19 tags` comment are correct and stay unchanged.
- The "20 fragments" report and the 20-line manifest count a different quantity: 19 top-level tags plus one trailing tail fragment (L550-558, `has_tail`), which the manifest shows as `20-language_policy.md`.
- Therefore 19 and 20 do not disagree; they count tags vs fragments. The only genuinely stale text is the two docstrings at L487 and L517 saying "20 top-level XML tags", corrected to "19 top-level XML tags plus one trailing tail fragment (20 fragments total)".
- Validation-phase count is consistent (constant 5, measured 5) and stays unchanged.

A6: Step 8a top-level tag count resolved by type distinction (tags=19, fragments=20) after Manager's continue; no numeric constant altered.
QA hotfix round 1: false changelog path removed, mirror-equality test added, discovery language clause verified absent and restored.
Code review round 1: APPROVED_WITH_CHANGES — I1 exit code recorded, I2 full-body mirror test, I3 doubled phrasing fixed, I4 stale-name grep clean, I5 ledger doc divergence deferred.
Code review re-review: PO_REVIEW_PENDING — "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." All seven AC met, I1-I4 closed, I5 deferred, no regression or scope widening.
Manager closure approval (question-tool answer value, verbatim): "Approved for closure".

### Step 8d conversions (before → after)

- A8 `15-universal_datetime_rules.md`: before `No application code should ever read the server's local timezone.` → after `Application code MUST NOT read the server's local timezone.`
- A9 `16-immutable_financial_ledger_mandate.md`: before `by more than 0.01 (or the currency's smallest indivisible unit)` → after `by more than the larger of 0.01 and the currency's smallest indivisible unit` (one deterministic threshold). Lane A had called this line already precise; XML Step 8d mandated one verifiable threshold, so the dual/threshold ambiguity was resolved in favor of the explicit `max` semantics.
- A10 `24-language_policy.md`: before `Match approval phrases as English literals only — see the Approval Literals Guard section below.` → after `Approval phrases MUST match as English literals only, per the named authority in the constraints fragment §Approval Literals Guard.`
- A11 `07-agent_skills_registry.md`: before `...for token-efficient, zero-hallucination Android development.` → after `...MUST keep UI state in typed schemas and gate every schema and query through code generation and compilation; unverified identifiers MUST fail the build.`
- A12 `agents/cognitive-executor.md`: before `the Type Drift Sentinel (retired \`loop-engine/sentinel.py\` — enforcement is now manual review per \`docs/conventions.md\`) fails the verification until...` → after `manual review MUST reject a diff that hand-copies a governed type until a replacement lands; the agent must import from the shared package or run the codegen toolchain.`

### Deferred findings (routed separately, not fixed here)

D1: QA-transition topology conflict across `prompts/fragments/13-constraints.md`, `prompts/fragments/09-hands_protocols.md`, `agents/cognitive-executor.md` (two line pairs), `AGENTS.md`, and `skill-templates/governance/templates/audit.md`.
D2: Brain-directed tool and skill instructions in Brain-owned prose — `prompts/fragments/03-system_context.md:2` web-search sentence, `08-agentic_reasoning.md`, `11-execution_workflow.md`, and `tools/prompt-composer/index.html:63`.
D3: `loop_guard.record_attempt` instruction in `agents/cognitive-executor.md` with no exposed MCP tool.
D4: lint false positives in `mcp-lint-server/server.py` — DECISIONS-as-Brain-owned check, lowercase exact-match check, case-sensitive Hands check.
D5: duplicated `validation_phase` bodies in `prompts/fragments/09-hands_protocols.md` that belong in the shared include pipeline.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `0327d20cf29ef54b3a413db4cac3635b39e949a3`
<!-- END_GIT_DIFF -->
