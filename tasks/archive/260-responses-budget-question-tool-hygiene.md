# Task 260: Responses-API reasoning budget fix, question-tool grant, and repo hygiene

**File:** `tasks/completed/260-responses-budget-question-tool-hygiene.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Ship the current working-tree change set as one reviewed unit: fix reasoning-budget starvation on both Responses-API MCP servers, grant the native OpenCode `question` tool to the cognitive executor, harden repository hygiene so env backups can never be committed, and point skills that ask the Manager at the structured question channel.

## Manager's Notes

Created on autopilot as a review vehicle for changes already implemented on disk in this session. The Manager asked for a task file built from the working tree, then routed through the autopilot cycle for a QA verdict and a Code Reviewer verdict. No new implementation is expected unless QA rejects. Standing orders apply: zero-question autopilot, consult Brain personas via `brain_turn`, RTK-first verification.

## Change Set Under Review

1. Reasoning-budget starvation fix — `mcp-brain-bridge/server.py` and `mcp-decision-server/server.py`. Reasoning tokens are billed as output and count against the output cap; `reasoning.effort` allocates a share of that cap (`xhigh`/`max` about 95%, `high` about 80%, `medium` about 50%). The old bridge defaults (`BRAIN_REASONING_EFFORT=xhigh`, `BRAIN_MAX_TOKENS=16384`) left roughly 820 tokens for visible text, so Brain replies truncated mid-sentence while the reasoning tokens were still charged.
2. Question-tool grant — `agents/cognitive-executor.md` plus `mcp-brain-bridge/capability.py`. The tool is a native OpenCode built-in that the agent had switched off; it is now allowed and registered as available.
3. Repository hygiene — `.gitignore` plus removal of a secrets-bearing env backup from the worktree.
4. Skill question-channel parity — six `skill-templates/*/SKILL.md` files.

## Local TODOs

- [x] Fix bridge defaults and add visible-token logging
- [x] Add the decision-path output cap and effort default
- [x] Add the warn-only effort-support guard
- [x] Grant the `question` tool and correct the capability registry
- [x] Harden `.gitignore` and relocate the env backup
- [x] Add manifest-aware question wording to the asking skills
- [x] Run the RTK-first targeted and full suites
- [ ] Stage, run the QA-review cycle, and close

## Acceptance Criteria

- [x] Both servers send an explicit output cap and a model-appropriate reasoning effort default: bridge `medium` with a `32768` cap, decision server `high` with a `16384` cap.
- [x] Both servers log a `visible_tokens` count (output minus reasoning) on every provider call.
- [x] The decision server warns without failing when the configured effort is outside the model's advertised set.
- [x] The `question` tool is granted to the cognitive executor and registered as available in the capability registry.
- [x] `.gitignore` ignores `.env.*` and `*.bak*` while `.env.example` stays tracked, and no secrets-bearing backup file exists inside the worktree.
- [x] Every skill template that asks the Manager points at the `question` tool when the capability manifest shows it available, with a prose fallback.
- [x] The full test suite passes with exit code 0.

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** the whole suite passes with no failures.
- **Actual result:** 626 passed, 10 warnings in 4.64s (targeted bridge + decision + capability suites: 373 passed).
- **Exit code:** 0

> Verification runner rule: the `pytest tests/ -q` command above is the complete underlying test command. The first verification run used the `rtk test` prefix; the exact prefixed command is recorded above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task.

## Risk & Rollback

- **Risk:** a wrong default changes every Brain turn; an over-broad `.gitignore` could hide a legitimate file; the capability-registry change could mark a genuinely missing tool available.
- **Rollback plan:** revert the affected files with `git checkout -- <path>` and re-run the full suite. Env rollback copies exist at `~/.config/opencode/.env.bak-20260919b` and `~/.config/opencode/.env.project.bak-20260919b`.

---

## Execution Log & Reasoning

### Context

Autopilot locked. Memory `manager/full_automatic_mode` is the authorization basis: zero clarification halts, consult Brain personas via `brain_turn`, reviewer technical approval plus `PO_REVIEW_PENDING` counts as closure approval. RTK-first verification per `workflows/rtk_first_verification`. No task file was created earlier for this work under `workflows/no_task_for_global_upgrade`; the Manager has now asked for a review vehicle, so this file records it.

### 1. Reasoning-budget root cause

OpenRouter bills reasoning tokens as output and counts them against the request output cap. The documented allocation is `max`/`xhigh` about 95 percent, `high` about 80 percent, `medium` about 50 percent, `low` about 20 percent. The bridge sent `reasoning.effort=xhigh` with `max_output_tokens=16384`, so only about 820 tokens remained for visible text. That single fact explains the truncated replies, the wasted spend, and the useless answers. A live provider probe confirmed the parameters themselves were never rejected: three real calls with the decision model and the Brain model all returned HTTP 200.

### 2. Bridge changes

- `_get_max_tokens()` default raised from `16384` to `32768`, with a docstring explaining the reasoning-token accounting.
- `_get_reasoning_effort()` default changed from `xhigh` to `medium`, the model's own advertised default.
- `_log_provider_diagnostics()` now computes and prints `visible_tokens` (output minus reasoning) on every provider call.
- `_maybe_warn_reasoning_budget()` docstring rewritten; the warning still fires when an explicit cap under `32768` meets `high` or `xhigh`.

### 3. Decision-server changes

- `_get_decision_effort()` fallback changed from `xhigh` to `high`, the DeepSeek V4.1 Flash default.
- New `_get_decision_max_tokens()` reading `DECISION_MAX_TOKENS`, default `16384`; the request body now sends `max_output_tokens` instead of leaving the ceiling to the provider.
- `_log_responses_diagnostics()` gained the same `visible_tokens` count.
- `_resolve_decision_effort()` warns without failing when the configured effort is outside the model's advertised set and coerces the value to the model's own default.

### 4. Question-tool grant

The `question` tool is a native OpenCode built-in. `opencode debug agent` showed the custom primary agent resolving `"question": false` while the built-in primaries resolved `true`: OpenCode applies a base `question: deny` rule and grants its own primary agents a later `allow` that wins. The agent definition now carries `question: allow`, and the capability registry moved `question` into the available set with the unavailable registry emptied. Verified live: the resolved config now reports `"question": true`.

### 5. Repository hygiene

The project `.env` backup sat in the repository root and was not ignored, so a broad `git add` could have committed secrets. It was moved out of the worktree to `~/.config/opencode/.env.project.bak-20260919b` with mode `600`, and `.gitignore` gained `.env.*` with an explicit `!.env.example` negation, plus `*.bak*`.

### 6. Skill question-channel parity

Six skill templates gained manifest-aware wording: `telegram-message-export` (its unconditional mandate replaced), `decision-migration` (both gate spots), `opencode-init`, `doc-coauthoring`, `prompt-refactor`, and `manager-decision`. `telegram-issue-sync` already carried the wording. Every changed skill is synced to the global install.

### 7. Verification

- Targeted suites: 373 passed, exit 0.
- Full suite: 626 passed, 10 warnings, exit 0.
- `py_compile` clean on both servers; global copies verified IN-SYNC.
- Live provider probe: three real calls, all HTTP 200.
- `opencode debug agent cognitive-executor` reports `"question": true`.

### Incidents

Two bridge tests failed on the first targeted run. The cause was a stale inherited `BRAIN_REASONING_EFFORT=xhigh` exported by the running daemon before this session's edits. Re-running with the stale variables cleared passed all 346 tests, and after the restart the same tests pass with no workaround.

### QA round 1 rejection and repair

The first QA turn returned `QA_REJECTED` with two risks and two test gaps, all repaired:

- R1 (high): the decision server still inherited `BRAIN_REASONING_EFFORT` before applying its own default, so a configured `xhigh` kept extraction at an effort the model does not advertise. `_maybe_warn_effort_support()` was replaced by `_resolve_decision_effort(model, effort)`, which keeps the inheritance chain but coerces an unadvertised effort to the model's own default and warns without failing; unknown models pass through untouched.
- R2 (medium): the ignore rules used `*.bak` plus `*.bak-*`, which leaves names such as `config.bak1` trackable. Both were replaced by the single `*.bak*` pattern.
- F1: the capability tests no longer proved that an explicit unavailable override can demote the newly granted tool. Added `test_unavailable_override_demotes_granted_question_tool`.
- F2: nothing covered the `visible_tokens` logging or the effort warning. Added bridge and decision-server `visible_tokens` tests plus a coercion test for `_resolve_decision_effort`.

The repair suite is green: targeted 373 passed, full 626 passed, exit 0.

### Closure authorization

The Manager answered the closure question through the native `question` tool — the first live use of the granted channel — with the exact phrase **"Approved for closure"**. The task was moved to `tasks/completed/`, its status set to `closed`, and the staged 16-file change set committed through `custom_context_commit_and_clean_task`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ca622ecb4fb7dce32a84a0453e91bce6dec3708c`
<!-- END_GIT_DIFF -->
