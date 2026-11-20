# Task 0396: Stage-aware Brain prompt routing with scoped persona slices

**File:** `tasks/completed/396-stage-aware-brain-prompt-routing.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-11-12T15:44:13Z
**Submitted:** 2026-11-12T14:56:43Z

## Goal

Split the Brain's single 717-line monolithic system prompt into a shared COMMON core plus per-stage persona slices, so every `brain_turn` only carries the persona it actually needs (QA sees QA alone, planning sees planning seats, brainstorming sees all seven), cutting input tokens and removing cross-persona instruction interference.

## Manager's Notes

Manager ordered: make the Brain prompt system "intelligent" — state-aware instead of always shipping every persona. The measured baseline (2026-11-12 smoke test): a `brain_turn` ping consumed 20278 input tokens before the question was even seen, and the full graph build showed the whole prompt and all seven personas load on every turn.

Manager's explicit rules for this work:

1. COMMON fragments always ship — the persona catalog is the only stage-dependent part.
2. Stage routing is deterministic code, never a per-turn hand-off: the bridge resolves the stage to a prompt file.
3. A missing or unknown stage degrades to the full prompt (current behavior), never to an empty prompt.
4. The Brain stays plugin-blind (no `goal_set`, `compact_context`, `read_omitted_content`, `smart-compact`, `magic-compact` literals) in every generated slice.
5. Everything must be globally installed, restarted, and smoke-tested with measured before/after numbers.

Scope guard: this task owns the HQ prompt pipeline only. The two plugin repositories carry their own task files.

## Local TODOs

- [ ] Split `prompts/fragments/06-personas.md` into a shared catalog plus per-persona slice fragments
- [ ] Add a stage-to-slice manifest under `prompts/`
- [ ] Extend `scripts/prompt-build/assemble_system_prompt.py` to emit one artifact per stage
- [ ] Extend `scripts/prompt-build/split_system_prompt.py` to round-trip the new fragment layout
- [ ] Route `brain_turn(stage=...)` in `mcp-brain-bridge/server.py` to the matching prompt file
- [ ] Keep the full prompt as the fallback for a missing or unknown stage
- [ ] Add tests for stage routing, slice content, and plugin-blindness
- [ ] Bump the system version fragment and reassemble
- [ ] Update `CHANGELOG.md` via Parse-Then-Append
- [ ] Update sibling `README.md` and `DECISIONS.md` where the contract changed
- [ ] Deploy the generated prompts and bridge to the global install and restart the Brain MCP
- [ ] Smoke test: measure input tokens per stage against the recorded baseline

## Acceptance Criteria

- [x] Every stage prompt file contains the shared COMMON fragments verbatim plus exactly its own persona slice
- [x] The QA stage prompt contains the QA persona and none of the other six personas
- [x] The planning stage prompt contains the planning seats and not the QA or Reviewer personas
- [x] The brainstorming stage prompt contains all seven personas
- [x] A known stage whose artifact is missing on disk falls back to the full prompt with one stderr note, never empty (loader fallback)
- [x] An unknown stage string is rejected loudly by preflight `PreflightError`, never silently downgraded (deviation D2; a direct loader call with an unknown stage still returns the full prompt for API safety)
- [x] `brain_turn(stage=...)` resolves the matching prompt file with no hand-written path from the Hands
- [x] No generated prompt file contains a plugin-lane literal
- [x] The assembler output for every stage is byte-stable across two consecutive runs
- [x] The split script round-trips the new fragment layout without a byte-identity break
- [x] Full test suite green with exit code 0 and evidence recorded
- [x] The global install carries the stage prompt files and the restarted Brain MCP serves the QA stage prompt

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q
- **Expected result:** all tests pass with exit code 0
- **Actual result:** 845 passed, 24 warnings in 59.32s (0 failed). The count grew from 832 to 845 because this task added 13 stage-routing tests in `tests/test_stage_prompts.py`.
- **Exit code:** 0
- **Test command:** rtk test python3 scripts/prompt-build/assemble_system_prompt.py
- **Expected result:** byte-identical rebuild of the committed prompt, exit code 0
- **Actual result:** exit 0; `git --no-pager diff --stat system-prompt.md` shows exactly 2 changed lines (the 9.88.0 → 9.89.0 version bump and the one `<panel>` sentence in `12-brainstorming_protocol.md`). The persona re-splice reproduces every other byte, which proves the seven slices are verbatim.
- **Exit code:** 0
- **Test command:** rtk test python3 scripts/prompt-build/split_system_prompt.py --source /tmp/opencode/rt3/pristine.md --fragments-dir /tmp/opencode/rt3/fragments --shared-dir /tmp/opencode/rt3/shared --manifest /tmp/opencode/rt3/manifest.txt
- **Expected result:** the splitter decomposes the monolith into 20 fragments plus the catalog, 7 persona slices and the slice index; exit code 0
- **Actual result:** exit 0; the follow-up reassembly was `cmp`-identical to the pristine monolith (sha256 `bdb84d6e398b3eae2a7f26b791ec5d33158c159a8e57ccab8793554528802dce` on both sides).
- **Exit code:** 0
- **Test command:** rtk test bash /tmp/opencode/smoke-hq.sh
- **Expected result:** every check passes, exit code 0
- **Actual result:** all checks passed. Service active; 6 stage artifacts present; qa smaller than brainstorm (80140 < 95428 bytes); each stage carries exactly its declared roster; all 7 artifacts plugin-blind; artifacts byte-stable across regeneration; 6 artifacts present in the global install.
- **Exit code:** 0
- **Test command:** ~/.config/opencode/mcp-brain-bridge/.venv/bin/python -c "load_system_prompt(None, stage=<stage>) against the DEPLOYED global install"
- **Expected result:** each stage resolves to its own artifact; an unknown stage falls back to the full prompt without raising
- **Actual result:** stage=None → 95428 bytes / 7 personas; qa → 80140 bytes / 1 persona (QA Engineer only); implement → 80991 / 1 (Senior Programmer); review → 80850 / 1 (Code Reviewer); plan → 89690 / 5 (planning seats); brainstorm → 95428 / 7; bogus-stage → 95428 / 7 with no exception. This is the deployed code path, not the repository copy.
- **Exit code:** 0
- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q (QA hotfix round)
- **Expected result:** all tests pass with exit code 0
- **Actual result:** 849 passed, 24 warnings in 62.70s, 0 failed. The count grew from 845 to 849 because the QA hotfix round added 4 tests: the two-layer unknown-stage contract, the corrupt-manifest stderr report, the empty-roster guard, and the artifact catalog/core completeness check.
- **Exit code:** 0
- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_stage_prompts.py -q
- **Expected result:** all stage tests pass with exit code 0
- **Actual result:** 17 passed in 1.07s. The first run of the hotfix suite was 1 failed / 16 passed: the new unknown-stage test failed because the loader degraded an unknown stage without a stderr note. That failure is the evidence the fix was load-bearing; after the loader change the suite is fully green.
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** A stage prompt missing a fragment silently changes Brain behavior for that stage, and a missing stage value could ship an empty prompt.
- **Rollback plan:** The full prompt stays the committed artifact and the fallback path. Restoring `system-prompt.md` from git plus reverting the bridge routing restores the previous behavior with no data migration.

---

## Execution Log & Reasoning

### Brain plan verdict (recorded at plan approval, Task 396)

**Plan source:** `brain_turn(stage="plan")` under session `harness-intel-2026-11-12`, Brain status `XML_EXTRACTED`, task `396`. Seat Check: Software Architect (trigger `contract`, `API design`) + Senior Programmer (trigger `race`); skipped UI/UX Designer (no UI surface), Project Planner and Sprint Strategist as planning seats (file state only).

**Brainstorm: not required** — the prompt artifact is regenerable from source fragments, so the change is cheap to reverse; a 2-seat consult covers the cross-disciplinary gate.

**Normative stage-to-prompt-file mapping (from the Brain plan):**

| stage | repo artifact | global install artifact | persona slice carried |
| ----- | ------------- | ------------------------- | --------------------- |
| plan | `system-prompt.plan.md` | `~/.config/opencode/system-prompt.plan.md` | Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist |
| implement | `system-prompt.implement.md` | `~/.config/opencode/system-prompt.implement.md` | Senior Programmer only |
| qa | `system-prompt.qa.md` | `~/.config/opencode/system-prompt.qa.md` | QA Engineer only |
| review | `system-prompt.review.md` | `~/.config/opencode/system-prompt.review.md` | Code Reviewer only |
| closure | `system-prompt.closure.md` | `~/.config/opencode/system-prompt.closure.md` | Senior Programmer (see deviation D1) |
| brainstorm | `system-prompt.brainstorm.md` | `~/.config/opencode/system-prompt.brainstorm.md` | all seven |
| missing / unknown / None | `system-prompt.md` | `~/.config/opencode/system-prompt.md` | all seven, current behavior unchanged |

**Deviation D2 (HAND-OWNED, with citation):** the Brain plan proposed that `preflight.py` degrade an unknown stage string to `None` with a stderr warning. That conflicts with the existing tested contract in `tests/test_brain_bridge.py` (unknown stage MUST raise `PreflightError`), and a silently-typo'd stage is worse than a loud rejection. The implementation keeps the loud rejection for an unknown stage string, and adds `brainstorm` to `ALLOWED_STAGES`. "Degrades to the full prompt, never an empty prompt" is implemented where it matters: a KNOWN stage whose stage artifact is missing on disk falls back to the full prompt.

**Deviation D3 (HAND-OWNED, with citation):** the Brain plan listed every common fragment as always shipping, including `12-brainstorming_protocol.md`, whose `<panel>` sentence reads "the seven personas declared in `<personas>`". Once `<personas>` carries only a stage-scoped roster, that sentence is false in a scoped artifact. The implementation keeps the fragment common and corrects the sentence to "the personas declared in `<personas>`", which is true in every stage. That content edit changes the committed `system-prompt.md` bytes, so the system version is bumped `9.88.0` → `9.89.0` per the AGENTS.md rule on editing the prompt.

**Stage-to-persona contract (binding for implementation and review):**

| stage | persona slices carried | artifact file |
| ----- | ---------------------- | ------------- |
| plan | software-architect, ui-ux-designer, senior-programmer, project-planner, sprint-strategist | `system-prompt.plan.md` |
| implement | senior-programmer | `system-prompt.implement.md` |
| qa | qa-engineer | `system-prompt.qa.md` |
| review | code-reviewer | `system-prompt.review.md` |
| closure | senior-programmer | `system-prompt.closure.md` |
| brainstorm | all seven | `system-prompt.brainstorm.md` |
| none / unknown | all seven (full prompt) | `system-prompt.md` |

Stage artifacts are generated into `build/stage-prompts/` and installed to `~/.config/opencode/system-prompt.<stage>.md`. The full prompt stays the committed `system-prompt.md` at the repo root.

**Implementation contract (binding — both implementation lanes work from this):**

- Persona slice files live at `prompts/fragments/personas/<slug>.md`, one file per persona, each containing exactly the `<persona name="...">...</persona>` block for that seat. Slugs: `software-architect`, `ui-ux-designer`, `senior-programmer`, `project-planner`, `sprint-strategist`, `qa-engineer`, `code-reviewer`.
- The persona catalog fragment `prompts/fragments/06-personas-catalog.md` holds the `<personas>` wrapper, the `<auto_load>` block, and the closing tag — the part that ALWAYS ships. The per-persona `<persona>` blocks move out of it into the slice files.
- `prompts/stage-manifest.json` declares, per stage: the stage key, the ordered persona slugs it carries, the output artifact filename, and the artifact directory. The manifest is the single routing table for both the assembler and the bridge.
- `scripts/prompt-build/assemble_system_prompt.py` gains a stage mode: it emits one artifact per stage into `build/stage-prompts/`, plus the unchanged full `system-prompt.md`. The full artifact must stay byte-identical to the committed `system-prompt.md`.
- `scripts/prompt-build/split_system_prompt.py` learns the personas layout: it must reconstruct `prompts/fragments/personas/*.md` plus the catalog from the monolith, and the round-trip must reproduce the monolith byte-for-byte.
- `mcp-brain-bridge/server.py` gains `resolve_stage_prompt_path(stage)` (pure, side-effect free) next to `load_system_prompt`, and `load_system_prompt` gains a `stage` parameter. Resolution order: explicit path → stage artifact → `BRAIN_SYSTEM_PROMPT` env → the full prompt. A missing stage artifact falls back to the full prompt; it never yields an empty prompt.
- `mcp-brain-bridge/preflight.py` gains `brainstorm` in `ALLOWED_STAGES`.

**Unknown-stage semantics (two layers, one rule).** The preflight gate is the public API and it rejects an unknown stage string with `PreflightError` — a typo fails visible instead of silently running unscoped. The loader is the internal API and it is total: `load_system_prompt` with an unknown stage returns the full prompt and never raises. The two are consistent, not contradictory: the gate blocks the bad input before the loader ever sees it, and the loader stays safe for any internal caller that bypasses the gate. A test asserts BOTH layers.

**Deviation D1 (HAND-OWNED, with citation):** the Brain plan mapped the `closure` stage to Project Planner. The executor spec states that the final closure XML is produced by the Senior Programmer (`agents/cognitive-executor.md`, Review-approval relay: "call `brain_turn` once as Senior Programmer for the final closure XML"). A closure turn carrying only the Project Planner persona cannot emit the closure XML it is required to emit. The mapping therefore carries Senior Programmer for `closure`. The Brain plan is followed in every other respect.

**Artifact layout (from the Brain plan):**

- `prompts/fragments/06-personas-catalog.md` — the personas wrapper plus the `auto_load` block; always ships.
- `prompts/fragments/personas/<slug>.md` — seven verbatim persona slices: `software-architect`, `ui-ux-designer`, `senior-programmer`, `project-planner`, `sprint-strategist`, `qa-engineer`, `code-reviewer`.
- `prompts/stage-manifest.json` — `schema_version`, `common_fragments`, `personas_dir`, `catalog`, `personas` map, `stages` map, `artifacts`.
- `build/stage-prompts/system-prompt.<stage>.md` — generated per-stage artifacts; the full `system-prompt.md` stays the committed fallback.

**Resolution site (from the Brain plan):** a pure `resolve_stage_prompt_path(stage)` in `mcp-brain-bridge/server.py` beside `load_system_prompt`, plus `load_system_prompt(explicit_path, stage)` where the explicit path wins, then the stage file, then `BRAIN_SYSTEM_PROMPT`, then the full prompt. `mcp-brain-bridge/preflight.py` gains `brainstorm` in `ALLOWED_STAGES` and degrades an unknown stage string to `None` with a stderr warning instead of raising.

**Round-trip contract:** the full artifact assembled from the catalog plus the seven slices must equal the committed `system-prompt.md` byte-for-byte; each stage artifact must be byte-stable across two consecutive runs; the splitter must learn the personas directory layout and still round-trip.

**Test list (from the Brain plan),** in `tests/test_stage_prompts.py`: manifest validity, QA-only slice, plan excludes QA and Reviewer, brainstorm carries all seven, every stage file plugin-blind, per-stage byte stability, splitter round-trip, bridge stage resolution plus fallback.

### Implementation record (Hands)

**What changed and why.** The persona block was the only stage-dependent part of the Brain prompt, so the split targets exactly that and leaves every common fragment untouched. `prompts/fragments/06-personas.md` became `prompts/fragments/06-personas-catalog.md` (the `<personas>` wrapper plus the `<auto_load>` rules, always shipping) plus seven verbatim slices under `prompts/fragments/personas/`. A single new file `prompts/stage-manifest.json` declares the stage-to-persona routing, and BOTH the assembler and the bridge read it, so the routing table has one owner and cannot drift between the two sides.

**Why the routing table is data and not code.** A stage mapping hard-coded in the assembler and a second copy in the bridge would be two sources of truth for the same contract. One JSON file means a stage is added once and both sides pick it up. The bridge resolves it through the pure function `resolve_stage_prompt_path`, which is side-effect free and therefore testable without touching the filesystem.

**Fallback ordering is the safety property.** `load_system_prompt` resolves explicit path → stage artifact → `BRAIN_SYSTEM_PROMPT` → full prompt. A known stage whose artifact is missing on disk falls through to the full prompt and logs to stderr; it never returns an empty prompt and never raises. That is the property that makes the change safe to deploy: a partially-installed global install degrades to today's behavior instead of failing.

**Measured effect (bytes of the assembled artifact, 2026-11-12).** Full 95428; plan 89690 (7% smaller); implement 80991 (16%); qa 80140 (17%); review 80850 (16%); closure 80991 (16%); brainstorm 95428 (unchanged, because it already carried every seat). The scope check is exact: the QA artifact contains the QA Engineer block once and zero occurrences of the other six seat names.

**Honest correction to the earlier estimate.** The first analysis projected a 35-45% reduction for the QA stage. The measured reduction is 17%. The projection over-counted because it treated the persona blocks as a large share of the prompt; in fact the seven persona blocks together are roughly 15KB of a 95KB prompt. The 17% figure is the real one and the earlier estimate was wrong. The remaining bulk is common fragments (the largest single fragment is 11KB), which are genuinely shared and were deliberately left alone.

**Byte-identity proof.** The committed `system-prompt.md` diff after reassembly contains exactly two changed lines: the version bump `9.88.0` → `9.89.0` and the one `<panel>` sentence in `12-brainstorming_protocol.md`. The persona re-splice reproduces the artifact byte-for-byte, which is the strongest available evidence that the slices are verbatim.

**Scope discipline.** The two plugin repositories carry their own task files and were implemented as separate lanes. No plugin-lane literal appears in any generated artifact.

### QA hotfix round (Brain verdict QA_REJECTED, all four findings reproduced)

**V1 — the acceptance criterion was too broad.** It claimed an unknown stage loads the full prompt with no behavior change. That is true of the loader and false of the public API: the preflight gate rejects an unknown stage with `PreflightError`, deliberately, so a typo fails visible instead of silently running unscoped. The criterion now states both layers separately, and the Execution Log records the two-layer rule: the gate is the public API and rejects loudly, the loader is the internal API and is total. The two are consistent because the gate blocks the bad input before the loader sees it.

**V2 — an empty roster could ship a stub artifact.** `_stage_persona_filenames` accepted a stage whose persona list was empty and would assemble an artifact whose `<personas>` block held no seat at all — a prompt with no role definition. The assembler now raises `ValueError` naming the stage. This was a latent manifest-authoring hazard, not a live bug: no declared stage has an empty roster today.

**V3 — a corrupt routing table degraded silently.** `_load_stage_manifest` returned `None` for an unreadable, malformed, or non-object manifest with no diagnostic, so a broken manifest looked exactly like "this stage has no artifact". Every degraded path now reports on stderr, and the loader additionally announces an unknown stage, which previously degraded without a word.

**V4 — the missing tests exposed a real defect.** The new test asserting that an unknown stage announces itself on stderr FAILED on the first run. The loader warned only for a KNOWN stage with a missing artifact; an unknown stage degraded in silence. That was the same class of defect as V3 and it survived the original 13-test suite because no test covered the unknown-stage path. The loader now prints `unknown stage <stage>; served the full system prompt`. The failing test is the proof that the fix is load-bearing rather than tautological.

**Net effect of the hotfix round:** the suite grew from 845 to 849 passing tests, and two of the four findings were documentation defects in the task file itself rather than code defects. The code defects that were real (V2, V3, V4) were all in the "fail silently" family, which is the same failure mode this whole task exists to prevent.

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `e681d0154313d5bbb8bf4c547951c11a3d616b6e`
<!-- END_GIT_DIFF -->
