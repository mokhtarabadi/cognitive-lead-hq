# Task 422: Regenerate Stage Prompts Every Release and Repair Handoff Test

**File:** `tasks/qa/422-regenerate-stage-prompts-every-release.md`
**Source:** manager
**Type:** bug
**Status:** in-progress
**Submitted:** 2026-11-24T05:38:43Z
**Estimate:** 5h
**Deadline:** 2026-11-25
**Started:** 2026-11-24T05:12:06Z

## Source Context

## Goal

Prevent releases from leaving stale stage prompts that bypass the full system prompt, and repair the handoff-language test regression found after task 421. Every prompt release must regenerate and verify both the full prompt and all stage prompts before global install.

## Manager's Notes

- Verbatim request: "this is important, always must be regenerate add this to our docs or our scripts in each release them generated too" and "fix both, a task required, that important for us".
- F1: `tests/test_input_validation_pipeline.py::test_executor_handoff_uses_requested_language` expects the retired exact phrase `regardless of the input language`. Task 421 kept the always-English behavior but changed the wording to `regardless of the user's input language`. The test must verify the behavior without pinning a brittle duplicate sentence.
- F2: `build/stage-prompts/system-prompt.*.md` remained at version 9.93.0 after task 421 regenerated only `system-prompt.md`. Brain Bridge prefers stage artifacts when present, so stage-scoped turns silently used the old 80–180-word and 2–5-sentence budgets.
- Standing rule saved to project memory: every release that changes prompt fragments must regenerate the full prompt and all stage prompts, and the release is incomplete while any stage artifact is stale.
- Stage artifacts are gitignored build/deploy outputs. The durable fix belongs in scripts, tests, and release documentation, not in committing generated stage files.

## Local TODOs

- [x] Inspect assembler `--stages`, stage manifest, Brain Bridge stage-artifact preference, and release docs
- [x] Write a failing regression test for stale stage-prompt detection before changing implementation
- [x] Implement an automated stage-prompt freshness check tied to the assembler/release workflow
- [x] Document mandatory full-prompt plus stage-prompt regeneration in release docs and skill copies
- [x] Repair F1 with a behavior-focused assertion, not a weaker test
- [x] Bump the system-prompt patch version and regenerate both full and stage prompts
- [x] Run stage generation twice and verify deterministic, fresh artifacts
- [x] Run the full test suite, prompt-sync checks, and task lint
- [x] Update CHANGELOG, decisions, and task evidence
- [x] Deploy regenerated full/stage prompts to the global install and verify versions

## Acceptance Criteria

- [x] F1 passes while still proving the executor requires user-facing output to remain technical English regardless of input language
- [x] A machine-enforced check fails when stage prompts are stale relative to the full prompt or current fragments
- [x] The release workflow invokes or requires that check before a release is accepted
- [x] `prompts/README.md` and both copies of the versioning skill document full-prompt plus stage-prompt regeneration
- [x] `system-prompt.md` and all eight stage prompts report the same new version
- [x] Every stage prompt contains the current fragment delta, including the Manager-Facing Concision Contract
- [x] The full test suite passes with exit code 0 and fresh evidence is recorded
- [x] Global install receives the regenerated full prompt and all stage prompts

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml pytest tests/ -q
- **Expected result:** all tests pass, including stale-stage detection and handoff-language behavior
- **Actual result:** 998 passed, 23 warnings. Includes F1 repair, stale-stage fallback, assembler freshness gate, orphan-stage rejection, explicit override priority, and release ordering.
- **Exit code:** 0
- **Additional gates:** docs sync exit 0; targeted suites 108 passed exit 0; full/stage regeneration exit 0; `--check` exit 0 with 8 current artifacts; version equality 9.94.1 across all 9 prompts; concision delta in all 8 stages; determinism diff exit 0; release script `bash -n` exit 0; global deploy comparisons exit 0; `build/` remains ignored.

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** A release guard that compares generated files incorrectly can block valid releases or miss stale stage subsets. A semantic handoff assertion could become too loose and stop catching regressions.
- **Rollback plan:** Revert the guard implementation and test changes, restore the prior release wording, decrement the version marker, regenerate the full prompt, and re-run the suite. Stage artifacts can be regenerated from current fragments at any time.

---

## Execution Log & Reasoning

Baseline F1: `rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml pytest tests/test_input_validation_pipeline.py::test_executor_handoff_uses_requested_language -q` → 1 failed, exit 1, before implementation.
Baseline stage tests: `rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml pytest tests/test_stage_prompts.py -q` → 22 passed, exit 0, before implementation.
Versioning skill byte equality: `cmp skill-templates/versioning-and-release/SKILL.md ~/.config/opencode/skills/versioning-and-release/SKILL.md` → exit 0.
Discovery loader finding: `mcp-brain-bridge/server.py#L1659-1682` accepts an existing stage artifact using only `path.is_file()` and `read_text`; no version, hash, timestamp, or content check. Repo artifacts precede global basenames. Missing artifacts fall back to the full prompt. Full-prompt sync tests do not cover stage freshness.
Discovery F1 finding: `tests/test_input_validation_pipeline.py#L74` pins the retired phrase `regardless of the input language`; `agents/cognitive-executor.md#L222` now says `regardless of the user's input language`. The behavior remains always-English technical output, so the test needs a section-scoped semantic assertion.

Approved plan: O1 runtime fallback plus assembler byte-freshness gate plus release ordering, version 9.94.1. Manager approved via question tool. No Hands restart; ADR provenance uses HTML comments only.
A1: Release deploy loop uses standalone `cmp` followed by `echo`, not `cmp && echo`, because `set -e` does not reliably exit on a failed left-hand command in an AND list. This preserves the intended hard gate.
Rule correction 1: the first implementation XML ordered a Hands restart; halted and reissued with Manager-owned restart only, per `.opencode/memory/workflows/global-install-upgrade.md:66`.
Rule correction 2: the first implementation XML put HQ-specific assembler flags into the redistributed versioning skill; halted and reissued with a conditional command-free rule, per `skill-templates/README.md:14`.
AC4 mapping: the generic rule in both byte-identical versioning-skill copies plus the HQ-specific commands in `prompts/README.md` and `scripts/README.md` satisfy the release-documentation criterion without leaking HQ scaffolding.
Phase 1 evidence: F1 module baseline 1 failed/5 passed exit 1; after semantic repair 6 passed exit 0. Runtime tests RED 24 passed/1 failed exit 1. Assembler/release tests RED 24 passed/5 failed exit 1.
Phase 2 evidence: bridge guard targeted tests 4 passed exit 0; assembler --check tests 3 passed exit 0; full stage module 29 passed exit 0; `bash -n scripts/release-9.66.0.sh` exit 0.
Phase 3 evidence: full assembler exit 0; stage assembler exit 0 for all 8 artifacts; `--check` exit 0 with `check: full prompt and 8 stage artifacts are current`. Distinct version output exactly `<system_version>9.94.1</system_version>`. Concision-contract file count 8. Retired-budget grep exit 1 (no matches). Two independent stage builds diff exit 0. `git status --short build/` empty. Stale `9.94.0` test literals grep exit 1 (none).
Phase 4 docs evidence: `prompts/README.md` has Stage Prompt Freshness; `scripts/README.md` has the release invariant; `mcp-brain-bridge/README.md` records stale fallback and override priority. Versioning skill copies `cmp` exit 0, conditional rule present, HQ-leak grep exit 1. ADR task-number hits are HTML-comment provenance only; visible-prose grep exit 1.
Edge hardening: explicit stage-path override RED 1 failed, then GREEN after tracking ungated override candidates; orphan stage-file check RED 1 failed, then GREEN after exact filename-set comparison. Targeted final 108 passed exit 0; full final 998 passed exit 0; post-doc freshness exit 0; `bash -n` exit 0.
Deploy evidence: copied full plus all 8 stage prompts to `~/.config/opencode/`; every `cmp -s` exit 0; deployed mtimes recorded at 2026-11-24 06:28:25 +0100. No `systemctl`, no singleton/OpenCode/OpenChamber restart.
restart owed to Manager: the running bridge still serves pre-deploy prompts and pre-change loader code until the Manager restarts OpenCode.
A2: The approved summary omitted `system-prompt.md` from `modified_files` even though Phase 3 regenerated it. The factual staged set must include it, so the repo-file count is 17 before the task file, not 16.
A3: `tests/README.md` and `tests/DECISIONS.md` were added to the changed set because test contracts changed and the Living Folder Docs Standard requires sibling synchronization.
A4: `.opencode/memory/release/stage-prompts-regenerate-every-release.md` and its auto-generated `.opencode/memory/index.md` were created at the Manager's explicit request immediately before this task. They are included in the factual changed set so the standing rule is committed with its enforcement; no duplicate memory write occurred during implementation.
Final lint: `lint_task_file` passed; QA budget 0/1. `lint_system_prompt_sync` reports `system-prompt.md is in sync` plus the two known false positives at `09-hands_protocols.md:150` and `DECISIONS.md:76`, previously verified and deferred; no new warning was introduced.
QA round 1 dispute: the requested CHANGELOG relocation does not reproduce. `grep -n '^## \[' CHANGELOG.md` returns `Unreleased` at line 7, `9.94.1` at line 43, then `9.90.0` at line 56. `grep -c '^## \[9\.94\.0\]' CHANGELOG.md` returns 0 with exit 1, so the cited destination header does not exist. The `9.94.1` section is already directly below Unreleased and above the next actual version header, which is the newest-first position. No CHANGELOG content or position was changed for this dispute. Pre-existing Unreleased debt is outside this task's scope.
QA round 2: QA_PASSED, recovered from the bridge artifact `tasks/.sessions/ses_df6723727ffeyqIEuj01fTgRgS_8777faaf/brain_outputs/chatcmpl_3c3f5c2c_d7bd_475b_8403_4452dc88ab184a5ebaa8c372e08cfd85.json` after two client-side timeouts. QA confirmed the original relocation finding was its error. Non-blocking observations for review: offender-count exit can exceed 1; stale stderr note can precede a fresh second-home fallback; pre-existing Unreleased debt remains out of scope.
Review blocker: the Code Mode catalog removed the `brain` namespace. `brain_turn` is unavailable and no replacement tool exists in the catalog search. The mandatory Code Reviewer turn cannot run, so technical approval and closure are blocked. Task remains in `tasks/qa/` with all changes staged; no commit or restart performed.
Review blocker re-check after Manager reported Brain restored: `tools.brain.brain_turn` still returns `Unknown tool 'brain.brain_turn'`; a fresh registry search for Brain review tools returns zero Brain entries. The service may be running, but this session has not reloaded the MCP tool registry. Task remains in `tasks/qa/`; parallel-session unstaged changes remain untouched.
Code review round 1: PO_REVIEW_PENDING — technically approved against the staged diff. Non-blocking recommendations R1-R4: reword --check help to non-zero on drift; make stderr note reflect the finally selected candidate; schedule release-cutoff cleanup for pre-existing Unreleased debt; consider stacked review slices for future releases over 400 lines.
Manager closure approval (question-tool answer value, verbatim): "Approved for closure".

## Implementation Progress

- [x] Step 1: claim task through planner
- [x] Step 2: schedule 5h estimate and 2026-11-25 deadline
- [x] Step 3: repair F1 semantic assertion; module green 6 passed, exit 0
- [x] Step 4: add runtime freshness tests; RED 24 passed, 1 failed, exit 1
- [x] Step 5: add assembler/release tests; RED 24 passed, 5 failed, exit 1
- [x] Step 6: add bridge version helpers
- [x] Step 7: wire stale-stage fallback
- [x] Step 8: add assembler --check
- [x] Step 9: gate release script generation/check/deploy
- [x] Step 10: bump version to 9.94.1
- [x] Step 11: re-anchor pinned test versions
- [x] Step 12: regenerate full and stage artifacts; run --check
- [x] Step 13: prove versions, delta, determinism, gitignore
- [x] Step 14: update normative READMEs
- [x] Step 15: update and mirror versioning skill
- [x] Step 16: CHANGELOG entry
- [x] Step 17: four ADRs with HTML-comment provenance
- [x] Step 18: deploy full and stage artifacts; no restart
- [x] Step 19: full green gate

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/index.md b/.opencode/memory/index.md
index b1eabb3..43b980f 100644
--- a/.opencode/memory/index.md
+++ b/.opencode/memory/index.md
@@ -29,6 +29,7 @@
 | quirks | full_output_verification_rule | Never trust truncated command output. Head tail cuts hide status lines and cause false alarms. Always re-run with ful... |  |
 | quirks | skill-tool-output-discarded-by-smart-compact | # Skill output must never be discarded or pruned | skills, smart-compact, opencode |
 | release | release-workflow | Release workflow for cognitive-lead-hq. |  |
+| release | stage-prompts-regenerate-every-release | Every release that changes prompt fragments must regenerate both the full prompt and all stage prompts before global ... | release, prompts, stage-artifacts |
 | telegram-sync | message-formatting-contract | # Telegram Message Formatting Contract (Manager rule, 2026-10-21) |  |
 | telegram-sync | topic-scoped-sync-workflow | # Telegram Sync Workflow Constraints (Cognitive Lead HQ) |  |
 | workflows | approval_gates_use_question_tool | # Approval gates must use the question tool (Manager standing rule 2026-09-27) |  |
diff --git a/.opencode/memory/release/stage-prompts-regenerate-every-release.md b/.opencode/memory/release/stage-prompts-regenerate-every-release.md
new file mode 100644
index 0000000..917e8ec
--- /dev/null
+++ b/.opencode/memory/release/stage-prompts-regenerate-every-release.md
@@ -0,0 +1,7 @@
+---
+tags: [release, prompts, stage-artifacts]
+---
+
+Every release that changes prompt fragments must regenerate both the full prompt and all stage prompts before global install.
+
+Rule: In each release cycle, run `python3 scripts/prompt-build/assemble_system_prompt.py` and then `python3 scripts/prompt-build/assemble_system_prompt.py --stages`. Copy `system-prompt.md` and all `build/stage-prompts/system-prompt.*.md` to the global install. A release is not complete if any stage artifact is stale or lacks the current fragment delta. Reason: Brain Bridge prefers stage artifacts when present, so stale stage prompts silently bypass the new full-prompt contract. Scope: Cognitive Lead AI HQ release workflow and global install sync.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 8c938a6..665c984 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -40,6 +40,19 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Prompt and workflow hardening META 417 (tasks 414/415/416):** reconciled the manual/automatic topology across both DECISIONS files, `docs/architecture.md` and the executor (superseded-note, single finalization sequence, one mode template per autonomy level, no escape-hatch OR); consolidated approval literals and ZAC into single normative blocks with per-surface actors; rebound the brainstorm panel to the Personas Roster with the multi-label carve-out; added the mandatory Context Map Before Brain Calls contract (turn classes A/B/C, audit line, forbidden shapes) to the executor, discovery agent, READMEs, `AGENTS.md` and the governance audit template; added the direct-input plan gate and Brain context-before-plan rule; removed the Template Preservation rule, the duplicate QA/review invocation, the duplicate Strict Tooling Gate sentences and the phantom `@google/design.md` lint command; verified no fragment path and no roster pointer reaches the assembled prompt (the roster is inline) and the Browser-facing prompt carries no fragment-file references. `01-system_version.md` bumped 9.90.1 to 9.92.0 (phases 1B and 2 consolidated into one cycle), `system-prompt.md` regenerated, prompt-sync suite 66 passed (44 existing + 22 new regression assertions: 14 plan-round plus 8 QA-round).
 
+## [9.94.1] - 2026-11-24
+
+### Added
+
+- **Stage-prompt freshness gate:** `assemble_system_prompt.py --check` regenerates the full prompt and all eight stage artifacts into a temporary tree, compares exact bytes, and exits 1 on any missing or stale artifact. Regression tests cover fresh, stale-stage, and stale-full cases. The release script now regenerates full and stage prompts, runs the gate before deployment, deploys all eight stage artifacts, and verifies each byte-identical. The versioning skill carries a conditional, project-agnostic rule for repositories that generate stage-scoped prompts.
+
+### Fixed
+
+- **Stale stage prompts no longer override current rules:** the Brain loader compares each stage artifact's `<system_version>` with the current source and falls back to the full prompt with a stderr note on mismatch. Explicit prompt overrides remain ungated. The running singleton requires a Manager restart to load the changed loader.
+- **Handoff-language regression test:** the test now verifies the always-English technical-output behavior inside the Output Contract section instead of pinning one retired sentence.
+
+Changed files: `mcp-brain-bridge/server.py`, `scripts/prompt-build/assemble_system_prompt.py`, `scripts/release-9.66.0.sh`, `tests/test_input_validation_pipeline.py`, `tests/test_stage_prompts.py`, `tests/test_prompt_sync.py`, `prompts/fragments/01-system_version.md`, `system-prompt.md`, `CHANGELOG.md`, `prompts/README.md`, `scripts/README.md`, `mcp-brain-bridge/README.md`, `skill-templates/versioning-and-release/SKILL.md`, `prompts/DECISIONS.md`, `scripts/DECISIONS.md`, `mcp-brain-bridge/DECISIONS.md`, `skill-templates/DECISIONS.md`, `tests/README.md`, `tests/DECISIONS.md`, `.opencode/memory/release/stage-prompts-regenerate-every-release.md`, `.opencode/memory/index.md`. Task 422. No commit from Hands.
+
 ## [9.90.0] - 2026-11-20
 
 ### Added
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 50382c7..ea5a0d7 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -160,3 +160,12 @@
 - **Decision:** Add sprint and planner to ALLOWED_STAGES, the routing manifest, and the stage tiers; document aliases (code review maps to review, planning maps to plan); regression-test every stage literal in prompt-facing Markdown against the admitted set.
 - **Consequences:** Two persona-scoped artifacts join the six existing ones; stage drift becomes test-enforced instead of prose-enforced.
 - **Rollback strategy:** Revert the enum line, the two manifest objects, the two tier lines, the added tests, and the docs sentences; no runtime state is touched.
+
+<!-- provenance: tasks/in-progress/422-regenerate-stage-prompts-every-release.md -->
+
+## [2026-11-24] ADR-016: Stale stage artifacts fall back instead of failing the turn
+
+- **Context:** The loader accepted any existing stage artifact without checking its release version. A stale artifact silently replaced current rules for every stage-scoped turn.
+- **Decision:** Compare the artifact version with the current source version. Skip a stale artifact with one stderr note and continue to the next candidate, ending at the full prompt. Explicit path and environment overrides remain ungated.
+- **Consequences:** Stage scoping is preserved while artifacts are fresh, and a release omission degrades safely instead of breaking the only automation path. The running singleton needs a Manager restart to load the new loader.
+- **Rollback:** Remove the version helpers and candidate-loop guard, then restart the singleton through the Manager-owned process.
diff --git a/mcp-brain-bridge/README.md b/mcp-brain-bridge/README.md
index a4218ce..5935c2e 100644
--- a/mcp-brain-bridge/README.md
+++ b/mcp-brain-bridge/README.md
@@ -56,7 +56,7 @@ In `chat_completions` mode:
 
 `brain_turn(stage=...)` selects the system prompt the Brain receives. The routing table is `prompts/stage-manifest.json` in the repository — the same file the assembler uses to generate the artifacts — so a stage is declared once and both sides agree on it. `resolve_stage_prompt_path(stage)` is pure and side-effect free: it returns the artifact path for a known stage and `None` for an unknown or empty stage.
 
-Resolution order in `load_system_prompt`: explicit `system_prompt_path` → the stage artifact (repo copy first, then the `~/.config/opencode/` install) → `BRAIN_SYSTEM_PROMPT` → the full committed prompt. A known stage whose artifact is missing on disk falls through to the full prompt with one stderr note; it never returns an empty prompt and never raises because of a stage. An unknown stage string is rejected loudly by the preflight gate (`PreflightError`) rather than silently downgraded, so a typo fails visible instead of quietly running unscoped. `preflight.ALLOWED_STAGES` accepts `plan`, `implement`, `qa`, `review`, `closure`, and `brainstorm`.
+Resolution order in `load_system_prompt`: explicit `system_prompt_path` → the stage artifact (repo copy first, then the `~/.config/opencode/` install) → `BRAIN_SYSTEM_PROMPT` → the full committed prompt. A stage artifact whose `<system_version>` differs from the current source is skipped with a stderr note and the full prompt serves; an explicit `system_prompt_path` override is never gated. A known stage whose artifact is missing on disk falls through to the full prompt with one stderr note; it never returns an empty prompt and never raises because of a stage. An unknown stage string is rejected loudly by the preflight gate (`PreflightError`) rather than silently downgraded, so a typo fails visible instead of quietly running unscoped. `preflight.ALLOWED_STAGES` accepts `plan`, `implement`, `qa`, `review`, `closure`, and `brainstorm`. A changed loader needs a Manager restart to take effect in the running singleton.
 
 Measured artifact sizes: full 95428 bytes; plan 89690; implement 80991; qa 80140; review 80850; closure 80991; brainstorm 95428.
 
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 14ed51f..468d5cd 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1630,6 +1630,45 @@ def _stage_prompt_candidates(stage: Optional[str]) -> list[Path]:
     return out
 
 
+_SYSTEM_VERSION_RE = re.compile(r"<system_version>(.*?)</system_version>")
+
+
+def _artifact_system_version(path: Path) -> Optional[str]:
+    """Return the ``<system_version>`` an artifact declares, or None.
+
+    Unreadable files and files with no version tag both read as None, which
+    the guard treats as "not current". A prompt with no version marker must
+    never win an argument with a staged artifact, because the marker is the
+    contract the release gate enforces.
+    """
+    try:
+        text = path.read_text(encoding="utf-8")
+    except OSError:
+        return None
+    match = _SYSTEM_VERSION_RE.search(text)
+    return match.group(1) if match else None
+
+
+def _expected_system_version() -> Optional[str]:
+    """The version every served stage artifact must carry, or None to disable.
+
+    Sources in trust order: the fragment the assembler itself reads, the
+    bridge-root full prompt, then the global install copy. None means no
+    source is readable at all — a stripped install — so the guard stays
+    silent rather than failing the only automation path.
+    """
+    root = _bridge_root()
+    for source in (
+        root / "prompts" / "fragments" / "01-system_version.md",
+        root / "system-prompt.md",
+        Path.home() / ".config" / "opencode" / "system-prompt.md",
+    ):
+        version = _artifact_system_version(source)
+        if version:
+            return version
+    return None
+
+
 def load_system_prompt(
     explicit_path: Optional[str] = None, stage: Optional[str] = None
 ) -> str:
@@ -1648,16 +1687,42 @@ def load_system_prompt(
     ~/.config/opencode) with a .md suffix.
     """
     candidates: list[Path] = []
+    ungated_candidates: list[Path] = []
     if explicit_path:
-        candidates.append(_check_prompt_path(Path(explicit_path)))
+        override = _check_prompt_path(Path(explicit_path))
+        candidates.append(override)
+        ungated_candidates.append(override)
     stage_candidates = _stage_prompt_candidates(stage)
     candidates.extend(stage_candidates)
     env_path = os.environ.get("BRAIN_SYSTEM_PROMPT", "").strip()
     if env_path:
-        candidates.append(_check_prompt_path(Path(env_path)))
+        override = _check_prompt_path(Path(env_path))
+        candidates.append(override)
+        ungated_candidates.append(override)
     candidates.append(Path.home() / ".config" / "opencode" / "system-prompt.md")
+    expected = _expected_system_version() if stage_candidates else None
     for path in candidates:
         if path.is_file():
+            # A stale stage artifact carries the previous release's rules.
+            # Skip it, never serve it, never raise: the next candidate (a
+            # second artifact home, then the full prompt) still gives the
+            # Brain current instructions. Explicit and environment overrides
+            # stay ungated even when they name the same path as a stage
+            # candidate, because operator intent outranks automatic freshness.
+            if (
+                expected is not None
+                and path in stage_candidates
+                and path not in ungated_candidates
+            ):
+                found = _artifact_system_version(path)
+                if found != expected:
+                    print(
+                        f"brain-bridge: stage artifact {path.name} is stale "
+                        f"(v{found or 'unknown'} != current v{expected}); "
+                        "served the full system prompt",
+                        file=sys.stderr,
+                    )
+                    continue
             # A known stage whose artifact never made it to disk fell back
             # to a lower-priority candidate. The note says so, because a
             # silent scope loss looks exactly like a routing bug to
diff --git a/prompts/DECISIONS.md b/prompts/DECISIONS.md
index e207adb..4274d3d 100644
--- a/prompts/DECISIONS.md
+++ b/prompts/DECISIONS.md
@@ -13,3 +13,12 @@
 - **Decision:** One canonical Manager-Facing Concision Contract in the constraints fragment, mirrored verbatim into both cognitive agents; duplicate restatements retired; audited counts and vague modality corrected in the same pass; version bumped 9.93.0 → 9.94.0 and the artifact regenerated.
 - **Consequences:** User-facing replies shorten to answer, reason, next action with a five-bullet ceiling; internal channels and verbatim pipeline strings are explicitly exempt.
 - **Rollback:** Revert the fragment and the two agent files, decrement the version marker to 9.93.0, regenerate, and re-run both lints and the byte comparison.
+
+<!-- provenance: tasks/in-progress/422-regenerate-stage-prompts-every-release.md -->
+
+## [2026-11-24] ADR-003: Stage prompts are release artifacts, not optional copies
+
+- **Context:** A version bump left every stage artifact on the previous release while the loader accepted any existing artifact. The full prompt looked current, but stage-scoped Brain turns silently used retired rules.
+- **Decision:** Treat the full prompt and every declared stage artifact as one release set. Regenerate both, compare exact bytes with the freshness gate, and deploy both. Generated stage files remain ignored; the executable gate is the enforcement.
+- **Consequences:** A release that skips stage regeneration now fails loudly. Stage scoping survives while artifacts are fresh, and a stale artifact can no longer override the current full prompt.
+- **Rollback:** Revert the gate and release-script changes, decrement the version marker, and regenerate from the current fragments.
diff --git a/prompts/README.md b/prompts/README.md
index 1e969a9..3784ad9 100644
--- a/prompts/README.md
+++ b/prompts/README.md
@@ -121,6 +121,18 @@ security boundary applies to its entries as to include paths:
 - **Parent-directory traversal in manifest entries** (e.g. `../outside.md`)
   is rejected by the assembler with a `ValueError` naming the unsafe entry.
 
+## Stage Prompt Freshness
+
+A fragment or version edit makes all eight stage artifacts stale because `01-system_version.md` and every other common fragment ships inside each of them. Regenerate the full prompt and every stage artifact before release:
+
+```bash
+python3 scripts/prompt-build/assemble_system_prompt.py
+python3 scripts/prompt-build/assemble_system_prompt.py --stages
+python3 scripts/prompt-build/assemble_system_prompt.py --check
+```
+
+`--check` is the machine gate: it regenerates into a temporary directory, compares exact bytes, and exits 1 on any missing or stale artifact. `build/` stays gitignored, so the gate and the release script, not a commit of generated files, are the enforcement.
+
 ## Sync Verification
 
 The lint MCP server exposes `lint_system_prompt_sync()`, which re-runs the
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 81353f1..b6ecfab 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.94.0</system_version>
+<system_version>9.94.1</system_version>
diff --git a/scripts/DECISIONS.md b/scripts/DECISIONS.md
index a2b26b9..d988a14 100644
--- a/scripts/DECISIONS.md
+++ b/scripts/DECISIONS.md
@@ -20,3 +20,12 @@
 - **Decision:** `scripts/format-guard.sh` dispatches prettier, ruff and shfmt on `write`/`edit`/`patch` and skips five byte-sensitive path classes. Prettier reads those five from `.prettierignore`. The guard cannot read that file portably in Bash, so it carries the same five classes in one `case` arm, and two assertions in `tests/test_prompt_sync.py` pin the lists against each other in both directions. The guard derives the repo root from its own location, normalizes a repo-relative `$FILE`, refuses any path that resolves outside the repo, and fails loud with a named stderr message when a dispatcher is missing.
 - **Consequences:** Gate and auto-formatter cannot disagree without a red test. `prompts/fragments/*`, `prompts/shared/*`, `system-prompt.md`, `build/stage-prompts/*` and `tasks/*` are excluded from both, so their formatting is a review concern rather than a build gate. Install semantics stay asymmetric by necessity: `npx --no-install` never fetches, `uvx` does. One limitation is recorded rather than fixed: `opencode.json` invokes `bash scripts/format-guard.sh` by a repo-relative path, so the guard runs only while the formatter's working directory is the repo root.
 - **Rollback:** Delete `.prettierignore`, delete this entry, restore the single `ruff-format` entry in `opencode.json`, delete the guard, and drop the parity assertions.
+
+<!-- provenance: tasks/in-progress/422-regenerate-stage-prompts-every-release.md -->
+
+## [2026-11-24] ADR-004: Prompt releases gate and deploy the full stage set
+
+- **Context:** The release script regenerated and deployed only the full prompt. Stage artifacts stayed stale, and the assembler had no mode that could prove freshness without rewriting files.
+- **Decision:** Add an exact-byte freshness check that rebuilds into a temporary tree. The release script regenerates the full prompt and all stage artifacts, runs the check before deployment, then copies and compares the complete set.
+- **Consequences:** Missing or drifted stage artifacts block a release. Generated files stay out of Git, and a failed comparison halts under strict shell mode.
+- **Rollback:** Remove the check mode and release-script gate, restore the prior deploy block, and regenerate the full prompt from fragments.
diff --git a/scripts/README.md b/scripts/README.md
index d85c9d8..bf54e3d 100644
--- a/scripts/README.md
+++ b/scripts/README.md
@@ -16,4 +16,5 @@ Maintenance tooling: docs-sync gate and system-prompt assembler/splitter. Enforc
 - Defensive shell/Python protocol: strict mode, no error masking on data commands.
 - Assembler output must be byte-identical to committed `system-prompt.md` (lint gate).
 - Version bump in `<system_version>` required on every prompt rebuild.
+- Every prompt release regenerates AND verifies the full prompt plus all eight stage artifacts before global install; `assemble_system_prompt.py --check` exits 1 on drift.
 - Auto-format exclusions live in two places: `.prettierignore`, which prettier reads, and the `case` arm in `scripts/format-guard.sh`. Both directions are pinned by `test_format_guard_matches_prettierignore` and `test_prettierignore_covers_guard_arms`, so editing one without the other is a red test. The exclusion is defense in depth: these files are Prettier-stable today, and the guard keeps them that way rather than repairing them.
diff --git a/scripts/prompt-build/assemble_system_prompt.py b/scripts/prompt-build/assemble_system_prompt.py
index f6d44a0..e06b7e3 100644
--- a/scripts/prompt-build/assemble_system_prompt.py
+++ b/scripts/prompt-build/assemble_system_prompt.py
@@ -63,6 +63,7 @@ import argparse
 import json
 import re
 import sys
+import tempfile
 from pathlib import Path
 from typing import Callable, Dict, List, Optional, Sequence, Tuple
 
@@ -994,6 +995,85 @@ def assemble_stages(
     ]
 
 
+def check_freshness(
+    output_path: str = "system-prompt.md",
+    fragments_dir: str = "prompts/fragments",
+    shared_dir: str = "prompts/shared",
+    manifest_path: str = "prompts/manifest.txt",
+    stage_manifest_path: Optional[str] = None,
+    artifact_dir: Optional[str] = None,
+) -> int:
+    """Fail when the shipped full prompt or any stage artifact is not current.
+
+    Regeneration is the only honest definition of fresh: a version string can
+    agree while a fragment edit went unpropagated. Everything is rebuilt into
+    a throwaway directory and compared byte-for-byte against the shipped set,
+    so a check never rewrites the tree it audits.
+
+    Returns the number of stale or missing artifacts, 0 when everything is
+    current. The release workflow treats non-zero as a hard gate.
+    """
+    offenders: List[str] = []
+    prompts_dir = Path(fragments_dir).parent
+    manifest_file = resolve_stage_manifest_path(prompts_dir, stage_manifest_path)
+    if manifest_file is None:
+        raise FileNotFoundError(
+            "No stage manifest found; the freshness gate needs the routing manifest."
+        )
+    stage_manifest = load_stage_manifest(manifest_file)
+    declared = list((stage_manifest.get("stages") or {}).keys())
+
+    with tempfile.TemporaryDirectory() as tmp:
+        tmp_dir = Path(tmp)
+        rebuilt_full = tmp_dir / "system-prompt.md"
+        assemble(
+            output_path=str(rebuilt_full),
+            fragments_dir=fragments_dir,
+            shared_dir=shared_dir,
+            manifest_path=manifest_path,
+            stage_manifest_path=str(manifest_file),
+        )
+        shipped_full = Path(output_path)
+        if not shipped_full.is_file():
+            offenders.append(f"missing full prompt: {output_path}")
+        elif shipped_full.read_bytes() != rebuilt_full.read_bytes():
+            offenders.append(
+                f"stale full prompt: {output_path} (regenerate: "
+                "assemble_system_prompt.py)"
+            )
+
+        built = assemble_stages(
+            stages=declared,
+            fragments_dir=fragments_dir,
+            shared_dir=shared_dir,
+            manifest_path=manifest_path,
+            stage_manifest_path=str(manifest_file),
+            artifact_dir=str(tmp_dir / "stages"),
+        )
+        expected_by_dir: Dict[Path, set[str]] = {}
+        for stage, (rebuilt_path, _rebuilt_text) in zip(declared, built):
+            shipped_path = stage_artifact_path(stage, stage_manifest, artifact_dir)
+            if shipped_path is None or not Path(shipped_path).is_file():
+                offenders.append(f"missing stage artifact: {stage} -> {shipped_path}")
+                continue
+            expected_by_dir.setdefault(Path(shipped_path).parent, set()).add(
+                Path(shipped_path).name
+            )
+            if Path(shipped_path).read_bytes() != rebuilt_path.read_bytes():
+                offenders.append(f"stale stage artifact: {stage} -> {shipped_path}")
+
+        for directory, expected_names in expected_by_dir.items():
+            actual_names = {path.name for path in directory.glob("system-prompt.*.md")}
+            for name in sorted(actual_names - expected_names):
+                offenders.append(f"unexpected stage artifact: {directory / name}")
+
+    for line in offenders:
+        print(f"CHECK FAILED: {line}", file=sys.stderr)
+    if not offenders:
+        print(f"check: full prompt and {len(declared)} stage artifacts are current")
+    return len(offenders)
+
+
 # ---------------------------------------------------------------------------
 # CLI entry point
 # ---------------------------------------------------------------------------
@@ -1038,6 +1118,12 @@ def main() -> None:
         help="Emit one artifact per declared stage into the stage artifact "
         "directory (default: build/stage-prompts).",
     )
+    parser.add_argument(
+        "--check",
+        action="store_true",
+        help="Verify the shipped full prompt and every declared stage artifact "
+        "are current; write nothing and exit 1 on drift.",
+    )
     parser.add_argument(
         "--stage",
         metavar="KEY",
@@ -1059,6 +1145,20 @@ def main() -> None:
 
     if args.stage and args.stages:
         parser.error("--stage and --stages are mutually exclusive.")
+    if args.check and (args.stage or args.stages):
+        parser.error("--check cannot combine with --stages/--stage.")
+
+    if args.check:
+        raise SystemExit(
+            check_freshness(
+                output_path=args.output,
+                fragments_dir=args.fragments_dir,
+                shared_dir=args.shared_dir,
+                manifest_path=args.manifest,
+                stage_manifest_path=args.stage_manifest,
+                artifact_dir=args.stage_dir,
+            )
+        )
 
     # Stage mode: build the per-stage artifacts. The full prompt keeps its
     # own invocation (no flags) so the committed artifact stays untouched.
diff --git a/scripts/release-9.66.0.sh b/scripts/release-9.66.0.sh
index cdbe7fb..6c5f786 100755
--- a/scripts/release-9.66.0.sh
+++ b/scripts/release-9.66.0.sh
@@ -15,21 +15,23 @@ echo "==> repo: $REPO (branch: $(git rev-parse --abbrev-ref HEAD))"
 
 echo "==> 1/7 bump system prompt version to ${VERSION}"
 sed -i "s#<system_version>9\.65\.0</system_version>#<system_version>${VERSION}</system_version>#" \
-  prompts/fragments/01-system_version.md
+	prompts/fragments/01-system_version.md
 sed -i "s#assert shipped == \"9\.65\.0\"#assert shipped == \"${VERSION}\"#" \
-  tests/test_prompt_sync.py
+	tests/test_prompt_sync.py
 
 echo "==> 2/7 reassemble system-prompt.md"
 uv run scripts/prompt-build/assemble_system_prompt.py
 grep -q "<system_version>${VERSION}</system_version>" system-prompt.md
+uv run scripts/prompt-build/assemble_system_prompt.py --stages
+uv run scripts/prompt-build/assemble_system_prompt.py --check
 
 echo "==> 3/7 prompt + splitter tests"
 uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette \
-  python -m pytest tests/test_prompt_sync.py tests/test_mcp_servers.py -q
+	python -m pytest tests/test_prompt_sync.py tests/test_mcp_servers.py -q
 
 echo "==> 4/7 planner tests"
 uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette \
-  python -m pytest tests/test_planner_server.py -q
+	python -m pytest tests/test_planner_server.py -q
 
 echo "==> 5/7 docs sync"
 python3 scripts/check_docs_sync.py
@@ -37,12 +39,17 @@ python3 scripts/check_docs_sync.py
 echo "==> 6/7 deploy prompt and restart the Brain bridge"
 cp system-prompt.md "$HOME/.config/opencode/system-prompt.md"
 cmp -s system-prompt.md "$HOME/.config/opencode/system-prompt.md" && echo "    deployed byte-identical"
+cp build/stage-prompts/system-prompt.*.md "$HOME/.config/opencode/"
+for stage_artifact in build/stage-prompts/system-prompt.*.md; do
+	cmp -s "$stage_artifact" "$HOME/.config/opencode/$(basename "$stage_artifact")"
+	echo "    deployed $(basename "$stage_artifact") byte-identical"
+done
 systemctl --user restart mcp-brain || true
 
 echo "==> 7/7 commit, tag, push"
 git add -A
 git commit -m "release: v${VERSION} — planner cockpit, design system, board hardening" \
-  -m "Closes milestone M02: Brain extraction and prompt pipeline exactness (342), planner protocol in the system prompt (340), Bootstrap/Graphite Desk surfaces with live-board hardening and jalaali-js (344), day/week/month cockpit (345), saved weekly plan state (347), ownership and nudges (346). Tasks archived under tasks/archive/, milestone recorded in tasks/milestones/M02-planner-cockpit-and-design-system.md."
+	-m "Closes milestone M02: Brain extraction and prompt pipeline exactness (342), planner protocol in the system prompt (340), Bootstrap/Graphite Desk surfaces with live-board hardening and jalaali-js (344), day/week/month cockpit (345), saved weekly plan state (347), ownership and nudges (346). Tasks archived under tasks/archive/, milestone recorded in tasks/milestones/M02-planner-cockpit-and-design-system.md."
 git tag -a "$TAG" -m "v${VERSION} — planner cockpit and design system"
 git push origin HEAD
 git push origin "$TAG"
diff --git a/skill-templates/DECISIONS.md b/skill-templates/DECISIONS.md
index f07daca..8afc8f1 100644
--- a/skill-templates/DECISIONS.md
+++ b/skill-templates/DECISIONS.md
@@ -27,3 +27,12 @@
 - **Decision:** Each `question`-tool option now leads with a brief ([YYYY-MM-DD HH:MM] sender — first 80 chars, type/topic); the numeric ID stays the machine value only, and the closing prompt asks for option numbers, names, or All, with a numbered-list manual fallback and server-side number-to-ID mapping.
 - **Consequences:** The Manager picks by visible brief instead of transcribing IDs; the sync registry still keys on numeric IDs.
 - **Rollback:** Restore the prior Phase 2 steps from git history.
+
+<!-- provenance: tasks/in-progress/422-regenerate-stage-prompts-every-release.md -->
+
+## [2026-11-24] ADR-005: Stage-artifact regeneration is conditional and project-agnostic
+
+- **Context:** A release omitted stage-prompt regeneration and shipped stale scoped prompts. The reusable versioning skill needed to prevent the same class of omission without embedding HQ-specific paths or commands.
+- **Decision:** Add a conditional rule: repositories that generate stage-scoped prompt artifacts must regenerate the full set and pass their freshness gate before deployment. Concrete commands remain in the owning repository's docs and scripts.
+- **Consequences:** Downstream projects receive the safeguard only when their architecture has stage artifacts. The template stays portable and contains no HQ scaffolding.
+- **Rollback:** Remove the conditional item from the versioning skill and restore the prior Phase 2 numbering.
diff --git a/skill-templates/versioning-and-release/SKILL.md b/skill-templates/versioning-and-release/SKILL.md
index 0da68a1..99e89a6 100644
--- a/skill-templates/versioning-and-release/SKILL.md
+++ b/skill-templates/versioning-and-release/SKILL.md
@@ -66,8 +66,9 @@ All git commit messages MUST use lowercase prefixes followed by a colon and a sp
 2. Open `CHANGELOG.md` and insert a formal release entry under the new version header, categorizing your modifications correctly.
 3. Open the active task file in `tasks/` and ensure your final reasoning and files modified are accurately logged under the "Execution Log & Reasoning" section.
 4. If a release includes changes to system behavior, skills, MCP servers, task templates, or workflow rules, `system-prompt.md` version MUST be bumped.
-5. If a release is metadata-only (e.g., LICENSE addition), the CHANGELOG MUST explicitly state: "system-prompt.md version unchanged."
-6. The `[Unreleased]` section MUST be empty after a release. All entries MUST be moved under the new version header.
+5. If the repository generates stage-scoped prompt artifacts, every release that changes prompt sources must regenerate the full prompt and every declared stage artifact, then pass the repository freshness gate before deployment. A release with a stale stage artifact is incomplete.
+6. If a release is metadata-only (e.g., LICENSE addition), the CHANGELOG MUST explicitly state: "system-prompt.md version unchanged."
+7. The `[Unreleased]` section MUST be empty after a release. All entries MUST be moved under the new version header.
 
 ### Phase 3: Staging & Factual Diff Injection
 
diff --git a/system-prompt.md b/system-prompt.md
index 0fb5eca..5818090 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.94.0</system_version>
+<system_version>9.94.1</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
diff --git a/tests/DECISIONS.md b/tests/DECISIONS.md
index 7175c39..7c4035d 100644
--- a/tests/DECISIONS.md
+++ b/tests/DECISIONS.md
@@ -41,3 +41,12 @@
 - **Decision:** (1) Re-anchor the executor guard to the ZAC deny-resource surface and the drift-guard mutation to a phrase verified present in HEAD; change the splitter's stale VP regex/count (`2-space indent`, `== 3`) to the real column-0, five-block structure so the byte-identity round trip is lossless — no shipped prompt edits. (2) Fix planner auth isolation at the test fixture: point `PLANNER_USERS_CONFIG` at a non-existent temp path so `_load_user_config` falls back to open local mode (fail-open on missing config — the documented no-auth behavior, not a security guard). The server's 401 is correct RFC 9110 behavior; no production change. (3) Fix the skill-registry race by per-test `tmp_path` isolation, not retry/sleep masking. (4) No test deleted to reach green; guard floor held at 960 test functions and 4 pre-existing skip/xfails.
 - **Consequences:** A future prompt regeneration that changes the VP block count or indentation requires a matching splitter update; the byte-identity gate catches any mismatch. Auth-enabled planner deployments still require real credentials; only the offline tests run open mode.
 - **Rollback:** Revert the three test files (`test_mcp_servers.py`, `test_planner_409_regression.py`, `test_skill_registry.py`) plus `scripts/prompt-build/split_system_prompt.py`; no runtime auth or server code was changed.
+
+<!-- provenance: tasks/in-progress/422-regenerate-stage-prompts-every-release.md -->
+
+## [2026-11-24] ADR-007: Pin stage freshness and release ordering offline
+
+- **Context:** Existing stage tests skipped missing artifacts and checked content shape, not freshness. A stale stage set could therefore pass while overriding the current full prompt.
+- **Decision:** Add hermetic tests that generate into temporary directories, mutate one artifact, and require the freshness gate to fail. Pin runtime fallback, fresh-artifact serving, explicit override priority, and release-script ordering.
+- **Consequences:** A clean clone needs no prebuilt `build/` tree to prove the gate. Stale full prompts, stale stage prompts, and deploy-before-check regressions all fail offline.
+- **Rollback:** Remove the added tests and helpers; no production behavior depends on the tests.
diff --git a/tests/README.md b/tests/README.md
index d58342f..5cbce55 100644
--- a/tests/README.md
+++ b/tests/README.md
@@ -11,6 +11,7 @@ Offline-only verification suite for the HQ platform: Brain Bridge turns, capabil
 - `test_brain_diff_attach.py` — Diff attachment on QA/reviewer turns.
 - `test_bundle_tasks.py` — META bundling, verbatim preservation, auto-archive moves.
 - `test_prompt_sync.py` — Assembled prompt equals committed `system-prompt.md` (rtk mandate included).
+- `test_stage_prompts.py` — Stage routing, runtime freshness fallback, assembler freshness gate, and release ordering.
 - `test_session_lifecycle.py` / `test_loop_guard.py` — Session ledger lifecycle and spin-guard hashing.
 - `test_mcp_servers.py` / `test_skill_registry.py` / `test_input_validation_pipeline.py` — Server contracts, registry, input pipeline.
 - `test_zen_proxy.py` — the zen-proxy slice: failure contract, body limits, stream termination, request log, allowlist refresher.
diff --git a/tests/test_input_validation_pipeline.py b/tests/test_input_validation_pipeline.py
index 82d601a..17ac919 100644
--- a/tests/test_input_validation_pipeline.py
+++ b/tests/test_input_validation_pipeline.py
@@ -7,6 +7,7 @@ translate, enrich, and prompt-refactor steps, and every clarification
 or response must stay in simple English.
 """
 
+import re
 from pathlib import Path
 
 REPO = Path(__file__).resolve().parent.parent
@@ -67,10 +68,23 @@ def test_prompt_refactor_in_executor_matrix():
 
 
 def test_executor_handoff_uses_requested_language():
-    # Historical name retained; the executor documents the always-English
-    # handoff (option 1: update-tests), see the executor handoff rule and
-    # prompts/fragments/24-language_policy.md.
+    # Historical name retained: the documented policy is always-English
+    # output, and this test enforces that policy semantically rather than
+    # pinning one exact sentence, so wording drift in the executor no
+    # longer fakes a regression (see prompts/fragments/24-language_policy.md).
     text = _read(EXECUTOR)
-    assert "regardless of the input language" in text
-    assert "simple English but technical" in text
-    assert "English inside, requested language outside" not in text
+    start = text.index("## Output Contract")
+    rest = text[start + len("## Output Contract") :]
+    end = rest.find("\n## ")
+    section = rest if end == -1 else rest[:end]
+    assert "simple English but technical" in section
+    assert re.search(r"regardless of the (?:user's )?input language", section), (
+        "the Output Contract lost its input-language independence clause"
+    )
+    assert "English inside, requested language outside" not in section
+    assert not re.search(
+        r"(?:respond|reply|write|answer)[^\n]{0,40}in (?:the )?"
+        r"(?:Manager's|requested|input|user's) language",
+        section,
+        re.I,
+    ), "the executor now instructs non-English Manager-facing output"
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index faa55bc..9372587 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -48,7 +48,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.94.0"
+    assert shipped == "9.94.1"
 
 
 def test_shipped_prompt_documents_context_path_line_ranges():
@@ -373,9 +373,9 @@ def test_executor_contains_full_dto_mandate():
     )
 
 
-def test_shipped_prompt_version_is_9_94_0():
+def test_shipped_prompt_version_is_9_94_1():
     prompt = _read_shipped_prompt_for_approval_contract()
-    assert "9.94.0" in prompt
+    assert "9.94.1" in prompt
 
 
 def test_openui_validity_gate_in_executor_and_fragment():
diff --git a/tests/test_stage_prompts.py b/tests/test_stage_prompts.py
index f103959..3171e1d 100644
--- a/tests/test_stage_prompts.py
+++ b/tests/test_stage_prompts.py
@@ -22,6 +22,7 @@ the bridge lane stays verifiable on its own.
 
 import json
 import re
+import subprocess
 import sys
 import types
 from pathlib import Path
@@ -38,6 +39,9 @@ import server as bridge
 #: The stage manifest the prompt lane writes (the shared routing table).
 MANIFEST = REPO / "prompts" / "stage-manifest.json"
 
+#: The real assembler exercised by the hermetic freshness-gate tests.
+ASSEMBLER = REPO / "scripts" / "prompt-build" / "assemble_system_prompt.py"
+
 #: Contract stage set (the task's stage-to-persona table).
 CONTRACT_STAGES = (
     "plan",
@@ -762,3 +766,188 @@ def test_no_invalid_stage_literals_in_prompt_surfaces():
                 if literal not in preflight.ALLOWED_STAGES:
                     offenders.append(path.as_posix() + ' -> stage="' + literal + '"')
     assert not offenders, "invalid stage literals: " + ", ".join(offenders)
+
+
+def _seed_current_version(root, version="9.94.1"):
+    """Give a throwaway bridge root the version the guard must expect.
+
+    The guard reads the source fragment first, so seeding it keeps the test
+    about artifact staleness instead of about missing sources.
+    """
+    frag_dir = root / "prompts" / "fragments"
+    frag_dir.mkdir(parents=True, exist_ok=True)
+    (frag_dir / "01-system_version.md").write_text(
+        f"<system_version>{version}</system_version>\n", encoding="utf-8"
+    )
+    (root / "system-prompt.md").write_text(
+        f"<system_version>{version}</system_version> full prompt body\n",
+        encoding="utf-8",
+    )
+
+
+def test_stale_stage_artifact_falls_back_to_the_full_prompt(fake_bridge_root):
+    """A stage artifact from an older release must never be served.
+
+    This is the release bug in miniature: the loader accepted any existing
+    artifact on `is_file()` alone, so a stale one silently overrode the
+    current rules with retired ones for every stage-scoped turn.
+    """
+    root = fake_bridge_root
+    _write_manifest(root)
+    _seed_current_version(root, "9.94.1")
+    stale = (
+        "<system_version>9.93.0</system_version>\n"
+        "STALE RULES FROM THE PREVIOUS RELEASE\n"
+    )
+    _write_artifact(root, "qa", stale)
+    full = (root / "system-prompt.md").read_text(encoding="utf-8")
+
+    served = bridge.load_system_prompt(stage="qa")
+
+    assert served == full, "a stale stage artifact was served"
+    assert "STALE RULES" not in served
+
+
+def test_current_stage_artifact_is_still_served(fake_bridge_root):
+    """The guard must not cost stage scoping when artifacts are fresh."""
+    root = fake_bridge_root
+    _write_manifest(root)
+    _seed_current_version(root, "9.94.1")
+    fresh = "<system_version>9.94.1</system_version>\nCURRENT STAGE RULES\n"
+    _write_artifact(root, "qa", fresh)
+
+    served = bridge.load_system_prompt(stage="qa")
+
+    assert "CURRENT STAGE RULES" in served, "the freshness guard broke scoping"
+
+
+def test_explicit_prompt_path_override_bypasses_the_freshness_guard(fake_bridge_root):
+    """An operator override is intentional and outranks the guard.
+
+    Resolution order stays explicit path first; gating it would make the
+    documented escape hatch unusable during an emergency deploy.
+    """
+    root = fake_bridge_root
+    _write_manifest(root)
+    _seed_current_version(root, "9.94.1")
+    override = root / "custom.md"
+    override.write_text(
+        "<system_version>0.0.0</system_version>\nOVERRIDDEN BODY\n", encoding="utf-8"
+    )
+
+    served = bridge.load_system_prompt(explicit_path=str(override), stage="qa")
+
+    assert "OVERRIDDEN BODY" in served
+
+
+def test_explicit_stage_artifact_override_is_never_gated(fake_bridge_root):
+    """An explicit path wins even when it names a stale stage artifact.
+
+    Operator intent outranks automatic freshness: an emergency override may
+    deliberately pin an older prompt while a release is being repaired.
+    """
+    root = fake_bridge_root
+    _write_manifest(root)
+    _seed_current_version(root, "9.94.1")
+    stale = "<system_version>9.93.0</system_version>\nPINNED OVERRIDE\n"
+    override = _write_artifact(root, "qa", stale)
+
+    served = bridge.load_system_prompt(explicit_path=str(override), stage="qa")
+
+    assert "PINNED OVERRIDE" in served
+
+
+def _run_assembler(args, cwd=REPO):
+    """Invoke the real assembler as a subprocess from the repo root."""
+    return subprocess.run(
+        [sys.executable, str(ASSEMBLER), *args],
+        capture_output=True,
+        text=True,
+        cwd=str(cwd),
+    )
+
+
+def _build_into(tmp_path):
+    """Generate the full prompt and every stage artifact into one temp tree.
+
+    Hermetic by design: the shipped `build/` tree is never required for the
+    gate tests, so a missing build directory can never read as a green check.
+    """
+    full = tmp_path / "system-prompt.md"
+    stages = tmp_path / "stages"
+    proc = _run_assembler(["--output", str(full)])
+    assert proc.returncode == 0, proc.stderr[-2000:]
+    proc = _run_assembler(["--stages", "--stage-dir", str(stages)])
+    assert proc.returncode == 0, proc.stderr[-2000:]
+    return full, stages
+
+
+def test_assembler_check_passes_on_freshly_generated_artifacts(tmp_path):
+    """--check is the release gate: fresh bytes must exit 0 and write nothing."""
+    full, stages = _build_into(tmp_path)
+    before = sorted(p.name for p in stages.glob("system-prompt.*.md"))
+
+    proc = _run_assembler(
+        ["--check", "--output", str(full), "--stage-dir", str(stages)]
+    )
+
+    assert proc.returncode == 0, proc.stderr[-2000:]
+    after = sorted(p.name for p in stages.glob("system-prompt.*.md"))
+    assert before == after, "--check must not rewrite artifacts"
+
+
+def test_assembler_check_reports_a_stale_stage_artifact(tmp_path):
+    """One mutated stage artifact must fail the gate and name the stage."""
+    full, stages = _build_into(tmp_path)
+    victim = stages / "system-prompt.qa.md"
+    victim.write_text(
+        victim.read_text(encoding="utf-8") + "\nDRIFT\n", encoding="utf-8"
+    )
+
+    proc = _run_assembler(
+        ["--check", "--output", str(full), "--stage-dir", str(stages)]
+    )
+
+    assert proc.returncode == 1, (proc.returncode, proc.stdout[-2000:])
+    assert "qa" in (proc.stderr + proc.stdout)
+
+
+def test_assembler_check_reports_a_stale_full_prompt(tmp_path):
+    """The full prompt is gated too, so an unpropagated fragment edit fails."""
+    full, stages = _build_into(tmp_path)
+    full.write_text(full.read_text(encoding="utf-8") + "\nDRIFT\n", encoding="utf-8")
+
+    proc = _run_assembler(
+        ["--check", "--output", str(full), "--stage-dir", str(stages)]
+    )
+
+    assert proc.returncode == 1, (proc.returncode, proc.stderr[-2000:])
+    assert "system-prompt" in (proc.stderr + proc.stdout)
+
+
+def test_assembler_check_rejects_unexpected_stage_artifact(tmp_path):
+    """An orphan stage file must fail the exact filename-set gate."""
+    full, stages = _build_into(tmp_path)
+    (stages / "system-prompt.orphan.md").write_text(
+        "<system_version>9.94.1</system_version>\nORPHAN\n", encoding="utf-8"
+    )
+
+    proc = _run_assembler(
+        ["--check", "--output", str(full), "--stage-dir", str(stages)]
+    )
+
+    assert proc.returncode == 1, (proc.returncode, proc.stderr[-2000:])
+    assert "orphan" in (proc.stderr + proc.stdout)
+
+
+def test_release_script_generates_and_checks_stage_prompts_before_deploy():
+    """The release workflow must regenerate and verify every stage artifact.
+
+    Order is the whole point: a deploy before the check can ship stale stage
+    prompts, which is the defect this task closes.
+    """
+    script = (REPO / "scripts" / "release-9.66.0.sh").read_text(encoding="utf-8")
+    stages = script.index("--stages")
+    check = script.index("--check")
+    deploy = script.index("cp system-prompt.md")
+    assert stages < check < deploy, (stages, check, deploy)
```
<!-- END_GIT_DIFF -->
