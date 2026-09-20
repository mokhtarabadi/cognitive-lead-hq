# Task 259: brain_turn EMPTY_OUTPUT_RETRY loop max_output_tokens exhaustion misreported

**File:** `tasks/completed/259-brain-turn-empty-output-max-tokens-misreported.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Fix brain_turn EMPTY_OUTPUT_RETRY misdiagnosis when Responses API returns incomplete max_output_tokens so lean retry is not suggested for output-budget failures.

## Manager's Notes

Created from GitHub issue 20 (https://github.com/mokhtarabadi/cognitive-lead-hq/issues/20) on autopilot. Fix and close issue and task. Standing orders apply: FULL AUTOMATIC MODE (zero questions), consult ALL Brain personas via brain_turn, RTK-first verification, one-by-one closure with issue comment and close.

## Local TODOs

- [x] Explore mcp-brain-bridge/server.py parse_responses_text and empty-output guard
- [x] Implement provider diagnostics logging and correct remediation hint
- [x] Apply the same provider-diagnosis fix to mcp-decision-server/server.py (Manager order, autopilot turn)
- [x] Verify with tests via rtk test prefix and record evidence
- [x] Stage diff, QA-review cycle, close task and issue 20

## Acceptance Criteria

- [x] Provider diagnostics (status, incomplete_details.reason, usage, error/refusal) are logged and returned on every turn
- [x] max_output_tokens exhaustion hints lower reasoning effort or raise max tokens instead of lean retry and is not counted as flake retry
- [x] Refusal text and top-level error surface verbatim instead of EMPTY_OUTPUT_RETRY
- [x] xhigh plus 16k default combo is guarded (auto-bump cap or startup warning)
- [x] Same provider-diagnosis treatment applied to the manager-decisions MCP server (mcp-decision-server/server.py) within this task
- [x] GitHub issue 20 closed with fix comment

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q`
- **Expected result:** all tests pass
- **Actual result:** `621 passed, 10 warnings in 4.47s` full suite; targeted runs `346 passed` (bridge + decision server) after the hotfix; the pre-hotfix runs were `616 passed` full / `202 passed` bridge / `139 passed` decision server
- **Exit code:** 0

> Verification runner rule: the command above IS the `rtk test`-prefixed first run. Exact pin `mcp==1.30.0` is used because `rtk test` joins arguments without quoting, so `mcp<2` would be misparsed as redirection (docs/opencode-shell-strategy.md §8). Raw `pytest` is not on PATH, so the documented `uv run` wrapper is the underlying command.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** mis-handling provider response shape breaks existing retry path
- **Rollback plan:** revert mcp-brain-bridge/server.py change via git checkout of that file and re-run tests

---

## Execution Log & Reasoning

Autopilot locked for issue 20. Memory: FULL_AUTOMATIC_MODE zero-questions, consult ALL personas, RTK-first, one-by-one closure. Absent-file note: DESIGN.md, docs/architecture.md, docs/data_model.md absent per ls — skipped gracefully.

### Deep web research (blowsh) — Responses API + LiteLLM, 2026-09-19

Authoritative facts confirmed against OpenAI docs, the official `openai-python` type stubs, and OpenAI community repro reports:

- `Response.status` `"incomplete"` carries `incomplete_details.reason` with exactly one of `max_output_tokens | max_messages | content_filter | steered` (source: `openai/types/responses/response.py`, class `IncompleteDetails`).
- Reasoning tokens count toward `max_output_tokens` (the cap covers reasoning + visible output + non-visible formatting). Per-turn reasoning usage is at `usage.output_tokens_details.reasoning_tokens` (source: OpenAI reasoning guide, "Controlling costs").
- Failure mode is documented and reproducible: `status=incomplete`, `reason=max_output_tokens`, `output` contains only `type:"reasoning"` items, no `type:"message"` item, so `output_text` is empty while `usage.output_tokens` is non-zero. Blank-output rate rises with `reasoning.effort` (community report 1373609: `high` blanked 5/5 at 800 tokens; `low` blanked 0/5 at 400). This is exactly Task 799's symptom.
- Refusal is a separate content item: `{"type":"refusal","refusal":"<text>"}` (`openai/types/responses/response_output_refusal.py`), distinct from `{"type":"output_text","text":"...","annotations":[...]}`. Top-level provider failures arrive as `Response.error`.
- `reasoning.effort` values are now `none|minimal|low|medium|high|xhigh|max`; defaults are model-dependent (GPT-5.6 defaults `medium`). `xhigh` is documented as "deep research, asynchronous workflows... only use when evals show a clear benefit". Our bridge hardcodes default `xhigh` + 16384, precisely the risky combo.
- Community-recommended client mitigations match our planned fix: allocate budget for reasoning + message, detect the condition client-side, and retry with a higher budget or lower effort — NOT a lean retry.

### Decision: do NOT migrate to LiteLLM (D1)

- LiteLLM's `/v1/responses` (SDK `litellm.responses(model=..., input=..., max_output_tokens=...)`, v1.63.8+) is a proxy/normalization layer. It does not change provider token accounting, so reasoning still consumes `max_output_tokens` and the blank-output condition persists. It cannot fix this bug.
- The defect is a client-side diagnosis gap in `parse_responses_text` + the empty-output guard. The fix is small, pure, and fully testable with the existing `_FakeResp` harness — no new runtime dependency.
- Migration would add a proxy hop, a new uptime/version failure surface, and scope well beyond "minimal change" (plan constraint + AGENTS.md no-scope-creep). LiteLLM stays a future option if multi-provider routing is ever needed.
- Rationale logged under the stored full-automatic order (manager/full_automatic_mode) and DEC-20260914-001 (consult all personas); no manager page required.

### Brain consult constraint set (autopilot, all-personas)

Brain consult returned `VERDICT: APPROVED_WITH_CONSTRAINTS` and confirmed D1 (no LiteLLM migration). The binding constraints implemented: C1 `debug.provider` attached on EVERY turn with stable keys/nulls; C2 diagnostics parser pure + tolerant, existing text parser untouched; C3 ordered branches error → refusal → max_output_tokens → generic flake; C4 budget exhaustion terminal (no EMPTY_OUTPUT_RETRY, no lean retry, no flake-counter bump); C5 refusal scanned in both direct items and nested content; C6 non-breaking warning for high/xhigh under 32768 output tokens, no default bump; C7 end-to-end regression tests; C8 scope preserved (no default cap change, no provider migration).

### Implementation — mcp-brain-bridge/server.py

- Added machine tokens `OUTPUT_BUDGET_EXHAUSTED`, `PROVIDER_ERROR`, `PROVIDER_REFUSAL` plus `_HIGH_EFFORT`/`_REASONING_BUDGET_FLOOR = 32768` beside the existing empty-output contract.
- Added pure helpers: `_as_int`, `parse_responses_diagnostics` (status / incomplete_reason / usage{input,output,reasoning,total} / error / refusal; scans refusal in direct and nested items), `_log_provider_diagnostics` (one stderr line every turn), `_provider_error_hint`, `_provider_refusal_hint`, `_output_budget_hint`, `_maybe_warn_reasoning_budget`.
- Rewired the empty-output guard: parse diagnostics once, log them, then branch in the order error → refusal → incomplete/max_output_tokens → generic `_empty_output_hint`.
- `result["debug"]` now always carries `{"provider": diag}` (existing fenced-block fields preserved when present).
- Emitted the reasoning-budget warning before the provider request when effort is high/xhigh and the cap is below 32768.

### Implementation — mcp-decision-server/server.py (Manager follow-up)

Manager order (autopilot): "apply samething for manager desctions mcp too. in current active task." Applied the same treatment to the manager-decisions extraction server, which shares the empty-envelope failure mode (a blank envelope previously became a misleading `decision model returned non-JSON`):

- Added the same three machine tokens and pure helpers `_as_int`, `_responses_diagnostics`, `_log_responses_diagnostics`, `_provider_failure_message`.
- In `extract_session_decisions`, diagnostics are parsed and logged once per provider call; an empty envelope with a provider cause now raises a precise terminal RuntimeError carrying `OUTPUT_BUDGET_EXHAUSTED` / `PROVIDER_ERROR` / `PROVIDER_REFUSAL` with verbatim error/refusal text and remediation, instead of the generic non-JSON error. A genuine model blank (no provider cause) keeps the existing generic error, so no previously-working path changed.
- Decision-server note: the current request body sends no `max_output_tokens` (provider default applies), so no budget warning was added there; the diagnosis surfaces the provider's reported cause verbatim.

### Tests

- `tests/test_brain_bridge.py`: added 11 end-to-end + pure tests covering the diagnostics parser (full payload, malformed tolerance, refusal direct/nested, error shapes), the budget-hint contract, and brain_turn turns for budget exhaustion (terminal, no EMPTY_OUTPUT_RETRY), refusal verbatim, provider error verbatim, `debug.provider` on success, and the high/low-effort warning behavior. Result: `202 passed`.
- `tests/test_decision_server.py`: added 9 tests covering the mirrored diagnostics parser, `_provider_failure_message` precedence, terminal budget/error/refusal extraction via the stubbed transport, the unchanged generic-blank path, and the every-call diagnostics log. Result: `139 passed`.
- Full suite (task verification command): `616 passed, 10 warnings in 5.18s`, exit 0.

### Hotfix — QA round 2 rejection (F1-F4) and corrections

The first Brain QA round passed the visible scope but could not see the truncated tail; a second round with the pulled tail attached returned `QA_REJECTED` with four findings. All four were valid and are fixed in both mirrored servers, with regression tests added first-class.

- **F1 — malformed nested content could crash parsing.** Both parsers iterated `item.get("content") or []`; a truthy scalar (e.g. `{"content": 1}`) survived `or []` and then raised `TypeError`, so the empty-envelope path returned neither a terminal diagnosis nor the generic blank. Fixed by checking `isinstance(content, list)` before iterating (bridge `parse_responses_diagnostics`, decision `_responses_diagnostics`).
- **F2 — non-finite usage values could raise.** `int(float("nan"))` raises `ValueError` and `int(float("inf"))` raises `OverflowError`, breaking the "never raises on malformed fields" contract. `_as_int` now wraps the float conversion in `try/except (ValueError, OverflowError)` and returns `None`.
- **F3 — `_provider_failure_message` could raise on a scalar `usage`.** The budget branch called `.get()` on `diag["usage"]`; a scalar usage raised `AttributeError` and the terminal classification was lost. Both `_provider_failure_message` and the stderr logger now normalize a non-dict `usage` to `{}`, so classification is preserved with null usage values.
- **F4 — warning tests did not cover the required effort values.** The high-effort test now covers both `high` and `xhigh` and asserts both warning lines appear; the no-warning test now uses `low` (the implementation's `_HIGH_EFFORT` set is `{"high", "xhigh"}`).
- Also hardened: the error-dict JSON serialization in both parsers now falls back to `str(error)` if `json.dumps` raises.

Regression tests added (not weakening existing assertions): bridge `test_parse_responses_diagnostics_scalar_content_does_not_raise`, `test_parse_responses_diagnostics_non_finite_usage_is_none`; decision server `test_responses_diagnostics_scalar_content_does_not_raise`, `test_responses_diagnostics_non_finite_usage_is_none`, `test_provider_failure_message_scalar_usage_still_terminal`. Precedence, stable diagnostic keys, the 16384 default cap, and genuine-blank `EMPTY_OUTPUT_RETRY` behavior are unchanged.

Post-hotfix evidence: targeted `346 passed in 2.34s`, full suite `621 passed, 10 warnings in 4.47s`, exit 0 for both.

### Incidents

- Full-suite first attempt failed collection: bare `pytest tests/` lacks `pathspec`; unpinned `mcp[cli]` resolved to mcp 2.x (FastMCP renamed). Fixed by using the documented `docs/setup.md` wrapper with the exact pin `mcp==1.30.0`. The `<2.0` specifier was replaced by the exact pin per the `rtk test` no-quoting rule.
- One authored decision-server test initially failed because candidate verbatim quotes must be exact transcript substrings; the helper transcript now embeds the tagged content after the quote.

### QA and review verdicts (autopilot, Brain Bridge)

- **QA round 1** (`brain_turn`, stage `qa`, task_id 259): `QA_PASSED` for the visible scope, with the truncated decision-server and test hunks explicitly marked UNVERIFIABLE because the injected diff hit the 20000-char `_TASK_DIFF_CAP`. The Hands closed that gap by attaching three complete per-file diffs as context paths instead of accepting a partial verdict.
- **QA round 2**: `QA_REJECTED` with four findings (F1 malformed nested `content` could raise; F2 non-finite usage floats could raise; F3 non-dict `usage` could break terminal classification; F4 warning tests missed `xhigh` and used `medium` instead of `low`). All four were fixed, plus extra error-serialization hardening, and 5 further regression tests were added.
- **QA round 3**: `QA_PASSED`. Findings F1-F4 confirmed addressed, precedence and genuine-blank behavior confirmed intact, no missing tests for the corrections.
- **Code Review** (`brain_turn`, stage `review`): **APPROVED**, status **`PO_REVIEW_PENDING`**. Findings: I1 informational (combined diff truncation, not grounds for rejection), I2 the GitHub-issue checkbox is a closure-stage action. Recommendations R1 (comment + close issue 20 during closure) and R2 (keep the unrelated `docs/openchamber-tailscale.md` worktree modification out of this task) were both honored.

### Closure authorization

The Brain Bridge rule normally requires the Manager's exact phrase ("Approved for closure" / "Close task") before closure. Two independent authorizations apply here, so no human relay was required:

1. The Manager's direct instruction in this session, verbatim: **"create a task from https://github.com/mokhtarabadi/cognitive-lead-hq/issues/20 and fix and close issue and task (use auto pilot mode)"** — the Manager's own word is the plan and the approval.
2. The stored standing order `manager/full_automatic_mode` (2026-09-17): the Manager has no session access and cannot be paged; a reviewer technical APPROVED with `PO_REVIEW_PENDING` counts as Manager closure approval; zero clarification halts. Supporting closure protocol: `manager-decisions/task_closure_protocol_one_by_one` (DEC-20260914-003/004) — verify, move to `tasks/completed/`, commit per task, post the closing comment with the feature hash on the linked issue, then close it.

Replayed ruling basis: `Replayed from manager/full_automatic_mode (2026-09-17): reviewer technical APPROVED + PO_REVIEW_PENDING counts as Manager closure approval.`

### Closure actions executed

- GitHub issue 20 commented and closed as completed: https://github.com/mokhtarabadi/cognitive-lead-hq/issues/20#issuecomment-5741599215 (state verified `CLOSED`). AC "GitHub issue 20 closed with fix comment" is therefore satisfied.
- The unrelated `docs/openchamber-tailscale.md` worktree change was never staged and is excluded from this task's commit (review recommendation R2 honored).
- Task file moved `tasks/qa/` → `tasks/completed/`, `**Status:** closed`, `**File:**` header synced, then staged and committed via `custom_context_commit_and_clean_task` (ZAC — no manual `git add`/`git commit`).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c7d6cb5c683989ed15015a0bd1b86fb542d9a225`
<!-- END_GIT_DIFF -->
