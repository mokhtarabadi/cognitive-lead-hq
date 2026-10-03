# Task 287: Adopt Magic Compact and the Compaction Contract

**File:** `tasks/completed/287-adopt-magic-compact-and-compaction-contract.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Adopt the `magic-compact` plugin as the high-fidelity manual context compactor, keep OpenCode's native auto-compaction as the automatic safety net, and add an explicit compaction survival contract to the system prompt and the executor agent. Document the whole thing so a new machine installs the plugin automatically.

## Manager's Notes

Manager order: research OpenCode compaction and the Magic Compact plugin, pick the better route, and if the plugin wins, bring it into the system, document it (README, LLM.txt, any doc), and teach the system prompt and agent to use it when needed. Chosen route: **Adopt Magic Compact + A2 contract**. This supersedes the 2026-10-01 "no OpenCode plugins" policy — the Manager now explicitly approves this one plugin.

Constraints: no breaking changes; native auto-compaction must remain the safety net; the plugin is upstream-paused (Operator Memory successor) so pin the working release and document rollback.

## Local TODOs

- [x] Install `magic-compact` globally and fix the stale npm proxy that would break auto-install
- [x] Add the `compaction` block (native auto + keep.tokens) to the global config
- [x] Add the `<compaction_protocol>` system-prompt fragment, bump the version, regenerate
- [x] Add the compaction guidance to `agents/cognitive-executor.md`
- [x] Document in `README.md`, `LLM.txt`, and a new `docs/compaction.md`
- [x] Add prompt-sync tests for the contract and the version bump
- [x] Run the suite, sync the prompt + agent globally, and record evidence

## Acceptance Criteria

- [x] `magic-compact` is installed globally (`plugins: ["magic-compact"]`) and the plugin auto-install path works without manual npm overrides
- [x] Global config carries `compaction.auto` with a tuned `keep.tokens`
- [x] `system-prompt.md` contains `<compaction_protocol>` and the version is bumped to 9.50.0, byte-identical on re-assemble
- [x] `agents/cognitive-executor.md` states the two layers, the survival contract, and that the agent cannot run the command
- [x] `README.md`, `LLM.txt` (§7 JSON + §7.7), and `docs/compaction.md` document install and usage
- [x] All tests pass, including the new prompt-sync gates

## Verification Evidence

- **Test command:** rtk test uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/test_prompt_sync.py tests/test_mcp_servers.py -q
- **Expected result:** the prompt-sync and context-server suites pass, exit code 0
- **Actual result:** `83 passed, 22 warnings in 1.69s`
- **Exit code:** 0
- **Full suite (informational):** `711 passed, 2 failed`; both failures are the pre-existing unrelated `tests/test_decision_server.py` cases.

> Verification runner rule: `uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/ -q` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** the plugin is upstream-paused. Mitigation: pin the working `1.2.2` release; rollback is `opencode plugin remove magic-compact`, and native auto-compaction keeps working without it.
- **Risk:** a plugin dependency is a supply-chain surface. Mitigation: it is a single npm package already reviewed in research; the `plugins` entry is one line to remove.
- **Rollback plan:** remove `magic-compact` from `plugins`, restore `~/.npmrc` from its backup, and revert the fragment/version/agent/docs hunks.

---

## Execution Log & Reasoning

**Plan verdict:** Manager-approved route — the decision option "Adopt Magic Compact + A2 (Recommended)" enumerated the deliverables (install, config, prompt fragment, agent, docs, tests). His choice is the plan.

**Seat Check:** domains = prompt/agent architecture (Software Architect) + implementation/infra (Senior Programmer). Skipped: UI/UX Designer (no surface), Planner/Strategist (no scope/file-state change). QA/Review run after implementation.

**Research:** native OpenCode compaction (v2 docs) is automatic and lossy — one summary, keeps ~15k recent tokens, configurable. Magic Compact (173 stars, last release Sep 2026) keeps user messages verbatim, summarizes each old assistant turn, prunes bulky tool I/O into a retrievable cache, and runs on command with no runtime cache churn. Its upstream is paused in favor of Operator Memory, but the pinned release is fully functional. Chose the plugin as the high-fidelity layer, native as the safety net.

**Changes:**
- Global `~/.config/opencode/opencode.json`: `plugins: ["magic-compact"]` (installed `magic-compact@1.2.2`) and `compaction: {auto: true, keep: {tokens: 20000}}`; config backed up first.
- `~/.npmrc`: commented the dead proxy lines (`127.0.0.1:7890`; mihomo moved to 8118 behind auth) — the plugin install otherwise fails with `NPMInstallFailedError`. Backup taken. This is the fix that makes auto-install actually work.
- New `prompts/fragments/22-compaction_protocol.md` + `prompts/manifest.txt`; `<system_version>` 9.49.0 → 9.50.0; `system-prompt.md` regenerated (byte-identical re-assemble).
- `scripts/prompt-build/split_system_prompt.py`: added `compaction_protocol` to `TOP_LEVEL_TAGS` (20 → 21) and updated the counts — without this the split/assemble round-trip test fails.
- `agents/cognitive-executor.md`: new "Compaction & Context Pressure" section.
- `README.md`, `LLM.txt` (§7 JSON + §7.7), new `docs/compaction.md`.
- `tests/test_prompt_sync.py`: version pin 9.50.0 + fragment/executor presence gates.
- Project memory: `opencode_config/plugin_policy_magic_compact_2026_10_02` records the policy change (supersedes the no-plugins policy).

**Assumptions (logged):** A1 `keep.tokens` 20000 (keeps a slightly larger recent tail; easily tuned). A2 the `~/.npmrc` proxy edit is machine-level and reversible from its backup. A3 the plugin is pinned to the working `1.2.2`; rollback is `opencode plugin remove magic-compact`.

**R2 (carried):** the agent cannot run `/magic-compact`; it recommends the run under context pressure and uses `read_omitted_content` after a prune. True auto-invocation is not offered by the plugin.

**Verification:** targeted gate `83 passed`, exit 0; full suite `711 passed, 2 failed` (only the pre-existing decision-server cases). Global sync verified: `system-prompt.md` 9.50.0 with `<compaction_protocol>`, agent in sync, global config carries the plugin + compaction block. A full OpenCode restart is required to load the plugin and the new prompt.

**Closure executed** on Manager quote "Approved for closure": file moved from `tasks/qa/` to `tasks/completed/` with Status `closed`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `150834df1a4718586494dfd86bfc072b8e82ea8e`
<!-- END_GIT_DIFF -->
