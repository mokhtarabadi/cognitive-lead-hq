# Task 265: Harden Responses API transport (HTTPS guard + configurable read timeout)

**File:** `tasks/completed/265-harden-responses-transport-https-and-read-timeout.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Close gaps R1 and R2 from the Responses API audit in BOTH MCP servers
(`mcp-brain-bridge/server.py`, `mcp-decision-server/server.py`):

- R1: the provider base URL (`BRAIN_API_BASE` / `DECISION_API_BASE`) is read
  from the environment with no scheme check. An `http://` value sends the
  Bearer API key in cleartext. Fail closed on any non-HTTPS base, allowing
  plain HTTP only for loopback hosts (local proxy).
- R2: the httpx read timeout is a fixed 120s for a non-streaming call. A
  high-effort reasoning turn can exceed that and be aborted. Make the read
  timeout configurable (`BRAIN_HTTP_READ_TIMEOUT` /
  `DECISION_HTTP_READ_TIMEOUT`) with a higher default of 600s; leave
  connect/write/pool unchanged.

## Manager's Notes

- Findings come from the read-only Responses API audit; only R1 and R2 were
  approved. R3-R7 stay deferred until separately tasked.
- Both server files ship self-contained to the global install, so the helper
  is duplicated in each by design (same pattern as the retry constants).
- ZAC applies: no `git add`/`commit`/`push`; staging goes through the MCP tool.

## Local TODOs

- [x] Add an HTTPS-scheme guard helper to both servers
- [x] Apply it in brain `_responses_url()`
- [x] Apply it in decision `_get_api_base()`
- [x] Add a configurable read-timeout helper to both servers and wire it into the HTTP client
- [x] Document both knobs in `.env.example`
- [x] Add focused tests for the guard and the timeout parser
- [x] Run the full test suite

## Acceptance Criteria

- [x] Both servers reject an `http://` non-loopback base with a fail-closed error naming the env key.
- [x] `http://localhost` and `http://127.0.0.1` bases remain allowed (loopback only).
- [x] An `https://` base passes through unchanged.
- [x] Read timeout is configurable by env with a 600s default; a malformed or non-positive value fails loud.
- [x] connect/write/pool timeouts are unchanged.
- [x] `.env.example` documents both new knobs.
- [x] Full test suite passes with exit code 0.

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** all tests pass
- **Actual result:** 686 passed, 10 warnings in 4.75s
- **Exit code:** 0

> Verification runner rule: the command above is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; a raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** A too-strict guard could break a legitimate local-proxy setup, or the longer timeout could make a hung request take longer to fail.
- **Rollback plan:** Revert the two server files (and `.env.example`) to the pre-change state; the edits are additive and self-contained.

---

## Execution Log & Reasoning

### Scope

Fixes gaps R1 and R2 from the read-only Responses-API audit, in both
Responses-API MCP servers. R3-R7 stay deferred (not approved).

### Changes

1. `mcp-brain-bridge/server.py`
   - Added `from urllib.parse import urlsplit`.
   - Added `_https_guard(base, env_key)` — returns `https://` bases
     unchanged; allows `http://` only for loopback hosts
     (`localhost`, `127.0.0.1`, `::1`); otherwise raises `RuntimeError`
     naming the env key.
   - Added `_get_read_timeout()` — reads `BRAIN_HTTP_READ_TIMEOUT`
     (default `600`), float-parses, raises on a non-number or `<= 0`.
   - `_make_client()` now uses `read=_get_read_timeout()`
     (connect/write/pool unchanged at 10/30/10).
   - `_responses_url()` calls `_https_guard(base, "BRAIN_API_BASE")`.
2. `mcp-decision-server/server.py`
   - Added `from urllib.parse import urlsplit`.
   - Added `_https_guard(base, env_key)` and `_get_decision_read_timeout()`
     (reads `DECISION_HTTP_READ_TIMEOUT`, default `600`).
   - `_get_api_base()` resolves the base then returns
     `_https_guard(base, "DECISION_API_BASE/BRAIN_API_BASE")`.
   - The extraction `httpx.Client(...)` uses
     `read=_get_decision_read_timeout()`.
3. `.env.example` — documents the https requirement on `BRAIN_API_BASE`
   and adds `#BRAIN_HTTP_READ_TIMEOUT=600` and
   `#DECISION_HTTP_READ_TIMEOUT=600`.

### Assumptions

- A1: The helper is duplicated in both servers by design; they ship
  self-contained to the global install (same pattern as the retry
  constants), so no shared import was introduced.
- A2: Loopback exemption covers `localhost`, `127.0.0.1`, and `::1` —
  the common local-proxy forms — and nothing else.
- A3: `600` is the new default read timeout; it is env-overridable, so a
  slower endpoint can raise it without a code change.

### Test-suite hermeticity fix

Both servers call `load_env_files()` at import, so the developer's real
gitignored `.env` leaked into assertions. Added
`monkeypatch.delenv` for `BRAIN_REASONING_EFFORT` + `BRAIN_MAX_TOKENS`
(in `_clean_routing_env`) and for `DECISION_MAX_TOKENS` (three decision
tests), and re-pointed two pre-existing tests that asserted the old
`http://` passthrough to loopback/https.

### Verification

- `rtk test uv run --with pytest ... pytest tests/ -q` -> first run
  `7 failed, 679 passed` (all 7 pre-existing env-leak / old-passthrough
  expectations, none from the new logic), second run `2 failed, 684
  passed`, final run **686 passed, exit 0**.

### ZAC

No `git add`/`commit`/`push`. Staging goes through
`custom_context_stage_and_inject_diff` only.

### QA + Review turns (Brain Bridge, autopilot)

- **QA (stage=qa, include_diff) -> `QA_PASSED`.** Confirmed the guard and
  timeout wiring in both servers. Non-blocking gaps noted: the `::1`
  allow path has no direct test; `nan`/`inf` timeout values are not
  explicitly rejected (the `<= 0` check does not catch `nan`); no mock
  assertion on the httpx Client wiring.
- **Review (stage=review, include_diff) -> technical `APPROVED`, status
  `PO_REVIEW_PENDING`.** Findings I1-I4 all Low/Info: `nan`/`inf` parser
  edge, error text names only `localhost` while code also allows
  `127.0.0.1`/`::1`, missing direct `::1` test, helper names differ
  across servers. Reviewer recommended accepting the change now and
  hardening the `nan`/`inf` and text gaps in a future task.
- Awaiting the Manager's explicit closure words; R3-R7 remain deferred.
- **Closure:** Manager accept words "Approved for closure" (exact phrase).
  Moved `tasks/qa/265-harden-responses-transport-https-and-read-timeout.md`
  to `tasks/completed/265-harden-responses-transport-https-and-read-timeout.md`,
  set `**Status:** closed`, and committed via
  `custom_context_commit_and_clean_task`. R3-R7 remain deferred to future
  tasks.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `20a08aec1e28ab3826bd836ba98ea2d952463715`
<!-- END_GIT_DIFF -->
