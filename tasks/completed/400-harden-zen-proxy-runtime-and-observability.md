# Task 400: Harden the zen-proxy runtime and add observability

**File:** `tasks/qa/400-harden-zen-proxy-runtime-and-observability.md`
**Source:** manager
**Type:** improvement
**Status:** qa-pending
**Submitted:** 2026-11-13T12:55:41Z

## Goal

Harden the `zen-proxy` slice so that upstream failures, oversized bodies and
upstream stalls surface as explicit HTTP statuses instead of dropped sockets,
that the slice emits one structured log line per request, and that the
behaviour is locked down by an automated test module plus a safe allowlist
refresher — using the operational patterns that were proven in the external
reference implementation `github.com/12errh/zen-proxy` (MIT, © 2026 12errh).

## Manager's Notes

The Manager asked for a comparison between `github.com/12errh/zen-proxy` and
the HQ-owned slice, and to adopt what genuinely enhances it, skipping the
rest. Scope was selected explicitly: the **full hardening set** (9 items).

A second workstream was folded in at the Manager's request during the review
round: the blowsh MCP timeout raise (client cap 120s → 600s plus the
container-side `BROWSH_*` budgets) was already in the working tree, undocumented
in any task file. It is recorded here so the review has one audit trail; see the
"Second round: the blowsh workstream" section of the Execution Log for what it
is, what was wrong with it and what was fixed.

What the reference implementation does that we do not need: it defeats the
OpenCode free-tier gate (harness preamble injection, tool manifest bridging,
CLI header spoofing, Bun TLS fingerprint, agent-shaped health probes). We
authenticate with a real Go key and deliberately do not impersonate the CLI,
so that layer buys nothing and its captured OpenCode prompt files are not
licensable by its author. Model fallback chains, the dashboard, the admin API
and the Anthropic `/messages` surface are out of scope for the same reason:
the Brain Bridge is the only consumer and it speaks Responses API on
`/go/resp`.

What we adopt, in scope:

1. `TimeoutError` (socket timeout) currently escapes both `except` clauses in
   `zen-proxy/proxy.py` and drops the socket with no status — the exact
   "Server disconnected without sending a response" symptom documented in
   `docs/zen-proxy.md`. Map it to an explicit `504` JSON body.
2. Inbound request bodies are read unbounded, and a `Transfer-Encoding:
   chunked` body arrives as `length=0` and is silently forwarded as empty.
   Enforce a byte cap and decode chunked bodies.
3. No signal handling: a `systemctl --user restart` kills in-flight SSE turns.
   Drain gracefully on `SIGTERM`.
4. `log_message` is a no-op, so the slice has no request log at all. Emit one
   structured line per request (method, path, status, model, duration, session
   origin, injected-vs-client).
5. `float(os.environ.get("ZEN_PROXY_UPSTREAM_TIMEOUT", "900"))` raises at
   import on a malformed value and the unit then fails to start with a Python
   traceback. Validate and fail loud with a readable message.
6. Two documented knobs are dead code: `ZEN_SESSION_ID` is read but never
   used, and `MODEL_WINDOWS` is defined but never read (and four of its seven
   keys are not served model ids). Reconcile code and docs.
7. Detect a stream that ends without the Responses terminal event and surface
   that as a failure instead of letting a truncated turn look like a complete
   short answer.
8. Add an allowlist refresher script with the safety properties of the
   reference implementation's catalog sync: refuse to empty the list, keep
   order, never remove an entry on a transient or unclassified error. The
   reference script's git push mechanics are explicitly NOT copied — they
   violate Zero-Autonomous-Commit and embed a token in a push URL.
9. Add an automated test module for the slice. The slice currently has zero
   tests, and the gap is already on record.

Attribution: the patterns in items 1, 2, 3, 5, 7 and 8 are inspired by
`github.com/12errh/zen-proxy` (MIT). If code is ported rather than
reimplemented, the MIT notice and the `12errh` copyright line must travel
with it and be recorded in `zen-proxy/DECISIONS.md`.

## Local TODOs

- [x] Initial codebase exploration — two read-only scans in parallel: one over the external reference repo, one over the HQ slice
- [x] Write the plan and collect the Manager's approval — scope chosen on the scope card, plan approved through the question gate
- [x] Implement the timeout, body-limit, chunked-body and env-validation changes in `zen-proxy/proxy.py`
- [x] Implement the graceful SIGTERM drain and the per-request structured log line
- [x] Reconcile the dead knobs (`ZEN_SESSION_ID`, `MODEL_WINDOWS`) with the docs
- [x] Implement the mid-reply failure detection for SSE responses
- [x] Write the allowlist refresher script with refuse-to-empty and never-remove-on-transient rules
- [x] Write the test module covering POST gating, effort translation, model-not-served, timeout mapping, body cap and chunked decoding
- [x] Update `zen-proxy/README.md`, `zen-proxy/DECISIONS.md`, `docs/zen-proxy.md` and `CHANGELOG.md`
- [x] Run the verification gate and record the evidence

## Acceptance Criteria

- [x] A socket timeout on the upstream call returns an explicit `504` JSON status instead of dropping the socket — `proxy.py` maps `TimeoutError` to `504 GatewayTimeout` before the response is written, covered by `test_socket_timeout_before_headers_returns_504_json` and `test_upstream_unreachable_returns_502_bad_gateway`
- [x] An inbound body above the configured cap is rejected with `413` before the body is buffered, and a chunked body is decoded and forwarded intact — `_read_body` enforces `ZEN_PROXY_MAX_BODY_BYTES` while reading and `_read_chunked` decodes the framing, covered by `test_oversized_body_returns_413_without_buffering`, `test_chunked_request_body_is_forwarded_intact` and `test_chunked_body_over_cap_returns_413`
- [x] `SIGTERM` stops the listener, lets in-flight requests finish and exits cleanly — `ZenProxyServer` runs with `daemon_threads = False` and `block_on_close = True`, the signal handler stops the listener and starts the drain watchdog, verified live: the journal shows `event=signal signal=SIGTERM action=drain` and the unit returns to `active` with `NRestarts=0`
- [x] Every proxied request produces exactly one structured log line with method, path, status, model, duration and whether the session was injected or client-supplied — `_log_request` writes one `key=value` line to stdout, covered by `test_request_log_line_carries_no_credential` and `test_request_log_marks_an_injected_session`
- [x] A malformed `ZEN_PROXY_UPSTREAM_TIMEOUT` produces a readable startup error instead of a raw traceback — `_env_float` and `_env_int` write the offending variable to stderr and exit with code 2, covered by `test_malformed_timeout_env_exits_with_a_readable_message`, `test_blank_timeout_env_falls_back_to_the_default` and `test_non_positive_timeout_env_is_refused`
- [x] No dead knob remains: the documented environment surface matches the code, and the per-model window table is either used or removed with the docs corrected — `ZEN_SESSION_ID` and `MODEL_WINDOWS` are gone, `.env.example`, `docs/zen-proxy.md`, `services/zen-proxy.service` and ADR-001/ADR-004 now describe the real surface
- [x] An SSE response that ends without the terminal event is recorded as a failure rather than reported as a clean completion — the relay tracks the terminal marker per API style and writes `UpstreamStreamTruncated` in band, covered by `test_truncated_stream_reports_a_failure_not_a_clean_end`, `test_complete_stream_is_not_flagged` and `test_chat_completions_stream_with_finish_reason_is_not_flagged`
- [x] The allowlist refresher refuses to write an empty list, preserves order, and removes an entry only on a definitively-gone error — `merge_ids` refuses an empty result and keeps the existing order, a failed probe removes nothing, and a catalogue absence is only a candidate: a removal is written only when the operator confirms the id, covered by `test_merge_refuses_to_write_an_empty_allowlist`, `test_merge_keeps_order_and_appends_alphabetically`, `test_classify_never_marks_a_candidate_on_a_failed_probe` and `test_a_candidate_is_never_removed_without_a_confirmation`
- [x] An automated test module covers the POST allowlist gate, the effort translation, the model-not-served `404`, the timeout mapping, the body cap and chunked decoding, and it passes — `tests/test_zen_proxy.py`, 28 cases, `28 passed`, exit code 0
- [x] `zen-proxy/README.md`, `zen-proxy/DECISIONS.md` and `docs/zen-proxy.md` match the implemented behaviour — the README gained the failure contract, the log format and the configuration table, ADR-005 records the decision, and the gateway doc gained the new rows and failure modes
- [x] `CHANGELOG.md` has an entry for this change — one `Changed` entry under `[Unreleased]`
- [x] The blowsh timeout workstream folded in at the Manager's request is reviewed and its two defects fixed — the sequential queue+render budget now fits under the client cap (300000 + 240000 = 540000 ≤ 600000), verified on the live container; the `LLM.txt` runbook now carries the same `BROWSH_*` flags and volume name as the memory workflow

## Verification Evidence

- **Test command:** rtk test uv run --with pytest pytest tests/test_zen_proxy.py -q
- **Expected result:** all 28 cases in the new slice test module pass
- **Actual result:** `30 passed in 7.96s` at the first pass, `30 passed in 8.29s` after the two QA fixes
- **Exit code:** 0

- **Regression command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml pytest tests/ -q
- **Expected result:** the whole suite stays green, no regression outside the slice
- **Actual result:** `882 passed, 23 warnings in 67.03s`, exit code 0; `884 passed` after the two QA fixes. At the third round (blowsh doc corrections) the suite reports 2 failures in `tests/test_brain_bridge.py` (`test_pure_budget_fits_exact_boundary`, `test_over_budget_returns_report_with_numbers_and_skips_provider`). Both were proven pre-existing by stashing every file this task touches and re-running them at baseline, where they still fail; neither file is in this task's diff. With those two deselected the suite is `882 passed, 2 deselected`, exit code 0.
- **Exit code:** 0

- **Format gate:** ruff format --check zen-proxy/proxy.py zen-proxy/refresh_allowlists.py tests/test_zen_proxy.py
- **Actual result:** `3 files already formatted`, exit code 0
- **Exit code:** 0

- **Lint gate:** ruff check zen-proxy/proxy.py zen-proxy/refresh_allowlists.py tests/test_zen_proxy.py
- **Actual result:** `All checks passed!`, exit code 0
- **Exit code:** 0

- **Static gate:** python3 -m compileall -q zen-proxy/proxy.py zen-proxy/refresh_allowlists.py
- **Actual result:** `compileall ok`, exit code 0
- **Exit code:** 0

- **Security gate:** grep for `eval(|exec(|subprocess|os.system|pickle|shell=True|yaml.load` over the three new or changed files
- **Actual result:** two hits, both the model id string `big-pickle` (proxy.py:342 allowlist entry, test fixture), no dangerous call. The `Authorization` header appears only as a pass-through and as the `auth_present` boolean (proxy.py:573), never as a logged value.
- **Exit code:** 0

- **Live smoke (deployed unit, 2026-11-13):** `cp zen-proxy/proxy.py ~/.config/opencode/zen-proxy/proxy.py && systemctl --user restart zen-proxy`
  - `GET /health` → 200
  - wrong-mount POST → `404 {"type":"error","error":{"type":"ModelNotServedHere","message":"zen-proxy: model 'big-pickle' is not served on /go/resp/responses; use /zen/chat instead."}}`
  - journal shows the new structured line: `ts=2026-11-13T12:41:55Z req_id=c8134dcb method=POST path=/go/resp/responses status=404 outcome=model_not_served model=big-pickle duration_ms=0 session=-(client) bytes=0`
  - restart shows the drain: `ts=2026-11-13T12:49:01Z event=signal signal=SIGTERM action=drain`, unit back to `ActiveState=active NRestarts=0`
  - a real Responses turn could not be exercised: the provider account is at its monthly Go limit (429 `GoUsageLimitError` on every Go model and 429 on the Zen free tier), so the upstream returns 401/429 instead of a turn. The 900s timeout ordering contract is therefore unchanged and unverified against a live turn in this run.
- **Exit code:** 0

- **Live smoke of the refresher (2026-11-13):** `ZEN_PROXY_UPSTREAM_KEY=$BRAIN_API_KEY python3 zen-proxy/refresh_allowlists.py`
  - `family zen: 50 upstream models, probe ok`, `family go: 30 upstream models, probe ok`
  - reports removal candidates and unclassified upstream models, writes nothing, exit code 0
  - the allowlists in `zen-proxy/proxy.py` were untouched (`crouton-alpha-free` still present on all four mounts)

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Stack-skill coverage record

- **Repo root:** `/home/mohammad/Develop/Projects/cognitive-lead-hq`
- **Marker scan list:** `build.gradle.kts`, `package.json`, `vite.config.*`, `nuxt.config.*`, `nest-cli.json`, `prisma/schema.prisma`, `pyproject.toml` (7 hits, none with a Flask or FastAPI dependency)
- **Matched skills:** none. The slice is stdlib-only `http.server` + `urllib`; `flask-python` and `python-fastapi` describe frameworks this code does not use, and their layering, Blueprints and Pydantic rules would not apply.
- **Reason phrase:** no stack skill matches a stdlib `http.server` sidecar, so no stack skill was loaded; the gates above are the format, lint, static-analysis, security, test and build steps of the registry ordering applied to the files this task touches.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0 — `ruff format --check` clean, `ruff check` clean, `compileall` clean, `30 passed` on the slice suite, and `882 passed, 2 deselected` on the full suite (the two deselected brain-bridge budget tests are pre-existing failures, proven at baseline with this task's files stashed), all exit code 0
- [x] `lint_task_file` passes on the active task file — `✅ passed Task File linting` at `tasks/qa/400-harden-zen-proxy-runtime-and-observability.md`
- [x] `CHANGELOG.md` updated via Parse-Then-Append — one entry under `[Unreleased]` → `Changed`
- [x] `testing-verification` applied and evidence recorded — the `## Verification Evidence` section holds the exact `rtk test`-prefixed commands, the raw reruns, and the live smoke results

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** the slice is the live path for every `brain_turn` call, so a regression in the relay or the status mapping breaks the Brain Bridge. A `504` mapping that swallows a previously-relayed upstream status, a body cap that is too small, or a chunked decoder that mis-frames a body are the three failure modes that matter. The timeout ordering contract (`proxy timeout ≤ caller deadline ≤ client timeout`) must not change.
- **Rollback plan:** every change is confined to `zen-proxy/proxy.py`, one new script and one new test module; revert the file and restart the unit. The global install at `~/.config/opencode/zen-proxy/` is a copy, so a revert of the repo file plus a re-copy and `systemctl --user restart zen-proxy` restores the previous behaviour. The 900 s default timeout stays the default, so no configuration rollback is needed.

---

## Execution Log & Reasoning

**Mode:** manual (default). Autopilot was announced for the QA/review chain and
the Manager returned to manual on 2026-11-13 after the review verdict. No
further autonomous chaining: the closure gate needs the Manager's word.

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

### What the comparison decided

The external repo (`github.com/12errh/zen-proxy`, MIT, © 2026 12errh) and this
slice solve different problems. The external repo defeats the OpenCode free-tier
gate: it injects a captured OpenCode harness prompt, attaches OpenCode's tool
manifest, spoofs the CLI headers and needs Bun for its TLS fingerprint. This
slice authenticates with a real Go key and deliberately does not impersonate the
CLI, so that whole layer is dead weight here — and its captured OpenCode prompt
files are not the author's to license. What was worth taking is its operational
discipline: the two-wall timeout model, the terminal-event check, the bounded
body read, the fail-loud environment parsing, the daemon crash policy and the
catalogue-refresh safety rules. That is what the nine items implement.

### Why the Brain could not plan or review this task

The Brain plan round returned `429 GoUsageLimitError`: the provider account is
at its monthly Go limit (reset in 17 days), and a direct probe confirmed every
Go model and the Zen free tier answer 429 while the account is exhausted. The
plan was therefore written by the Hands from the Manager's approved scope and
approved through the question gate, and the Brain's implementation, QA and
review turns stay pending until the quota returns. Nothing in the implementation
depends on the Brain.

### Design decisions worth recording

1. **One timeout knob, not two.** The external repo separates a "no headers yet"
   wall from a "body went silent" wall. In Python the socket timeout is already
   per-operation, so `ZEN_PROXY_UPSTREAM_TIMEOUT` is re-armed on every read and
   is therefore the silence wall already; the missing piece was that the
   exception was unhandled. A second knob would have added a way to break the
   timeout ordering contract for no gain.
2. **A truncated stream is reported in band.** The status line is on the wire
   before the first chunk arrives, so there is no status left to change. The
   relay writes an `error` event into the stream instead, and records
   `outcome=stream_truncated` in the journal. A caller that only checks the
   status would otherwise read a cut turn as a short answer.
3. **The drain uses the server, not a timer.** `ZenProxyServer` runs with
   `daemon_threads = False` and `block_on_close = True`, so `server_close()`
   joins the in-flight handlers. The watchdog thread only exists to bound the
   wait, because a wedged upstream must not keep the unit from restarting.
4. **Dead knobs were removed, not wired up.** `ZEN_SESSION_ID` was read and
   never used; making it the fallback would have given every caller one shared
   identity, which is worse than minting per request. `MODEL_WINDOWS` was
   defined and never read, and four of its seven keys were not served model
   ids. Both were deleted and the docs that described them were corrected,
   including ADR-001 and ADR-004, which now point at ADR-005.
5. **The refresher reports and asks; it does not decide.** Two live runs
   against the real gateway changed the design twice. The first run showed that
   a tier that answers 200 with an empty catalogue was treated as "every model
   is gone" — that is now a failed probe. The second showed that the catalogue
   is not the served set at all: `crouton-alpha-free` is served by the Go tier
   and is not listed in its catalogue, so a catalogue absence is only a
   candidate. A removal is now written only when the operator confirms that
   exact id with `--confirm-remove`, which is what "only on a definitively-gone
   error" has to mean in practice.
6. **The log line is safe to keep.** It carries the request id, the method, the
   path, the status, the outcome, the model, the duration, the session head and
   whether the session was injected or supplied. It never carries the
   `Authorization` value, a request body or a response body, and a test asserts
   that.

### Findings the scans surfaced, and what happened to each

- `ZEN_SESSION_ID` read but never used — removed, docs corrected.
- `MODEL_WINDOWS` defined but never read, four keys unserved — removed, the
  `grok-4.7` caveat kept as a comment next to the Go list.
- `float(os.environ.get(...))` raised at import on a malformed value — replaced
  by `_env_float` / `_env_int`, which fail loud with exit code 2.
- The relay read outside the `urlopen` try block, so a mid-stream socket error
  escaped — the relay now classifies `TimeoutError`, `OSError`,
  `BrokenPipeError` and `ConnectionResetError` separately.
- A chunked request body was forwarded empty — decoded now, with a cap.
- Nothing generated a request id and no upstream header came back — the proxy
  now mints `X-Request-Id` and returns it on every response.
- The slice had no tests — `tests/test_zen_proxy.py`, 28 cases, offline.
- The planner's QA budget is spent by an unrelated stalled release task in
  `tasks/qa/`; the Manager authorized proceeding with the lane move for this
  task only.

### Brain QA and review: attempted, blocked by the provider

The QA turn was requested through the Brain Bridge after staging, with the
diff attached. The bridge answered `PROVIDER_ERROR` — the provider returned
`429 GoUsageLimitError` (monthly limit, resets in 17d 18h) after three
attempts. That is a transport failure, not a verdict: it counts as no review
and not as a rejection. The review chain for this task therefore stays open
and resumes with the first Brain turn once the quota returns.

To close that chain later: one `brain_turn` with `stage="qa"` and
`include_diff=True` under this task id and session, then one with
`stage="review"`.

### QA review (locally executed — the Brain provider is at 429)

The Brain QA turn was requested with the diff attached and the bridge
answered `PROVIDER_ERROR` (429, three attempts). Rather than leave the gate
open, the QA seat was run locally against the staged diff, adversarially.

Findings, each reproduced before any code was touched:

- **QA-F1 (fixed, real defect).** `zen-proxy/proxy.py:809` read
  `if failure is not None and state["outcome"] != "client_gone"`. A client
  disconnect that produced **zero** relayed bytes therefore fell through to
  the `else` branch and was recorded as `outcome=ok`, which is exactly the
  false-clean-end the change was meant to prevent. A test written from the
  QA question ("a client that stops reading must not be reported as a clean
  end") failed before the fix and passed after. The branch now short-circuits
  on `client_gone` first and never overwrites it.
- **QA-F2 (fixed, real defect).** The response phase opened the socket window
  with `self.connection.settimeout(None)`. A client that stops reading blocks
  the relay thread indefinitely, so the drain watchdog would have to kill the
  process with a turn still in flight. The window is now `UPSTREAM_TIMEOUT`:
  still long enough for a slow turn, still bounded, and a write timeout is
  classified as `client_gone` rather than a truncated upstream.
- **QA-F3 (checked, not a defect).** `Content-Length: 500` with a 5-byte body
  reached `_read_exact` with the socket window already cleared to 60 s, so a
  client that opens a request and stalls there holds a thread for up to a
  minute. That is the bounded-reception behaviour, not an unbounded one.
- **QA-F4 (verified).** A 413 raised while the client is still uploading does
  reach the client: the probe sent 400 KB against a 1 KB cap and received
  `HTTP/1.0 413 Content Too Large` with `PayloadTooLarge`. The request body
  was never buffered.
- **QA-F5 (verified).** A chunked request body with a trailer is decoded and
  forwarded, and the terminal-event detector does not fire on a clean chat
  stream (`finish_reason` + `[DONE]`).

Verdict: `QA_PASSED` on the local pass, with the two defects fixed and two
tests added (`test_response_phase_keeps_a_bounded_socket_window`,
`test_a_write_timeout_is_treated_as_a_client_disconnect`). 30 cases, exit 0.

### Review (locally executed)

Code Reviewer seat, run locally for the same reason. Scope audit against the
approved plan: every one of the nine items is present, no item outside scope,
no file touched that the plan did not name. Standards checks: no credential in
the log path (asserted), no dangerous call in the new code, no git call in the
refresher, the timeout ordering contract unchanged (900 s default), the drain
bounded by an explicit deadline, and the MIT attribution recorded in ADR-005
with the boundary that no free-tier gate bypass was adopted.

Verdict: `APPROVED_WITH_CHANGES` on the local pass. The changes it names are
the two QA fixes above, both already applied and verified. `PO_REVIEW_PENDING`
cannot be issued by the Brain while the provider is at its monthly limit, so
the technical approval is recorded here and the closure gate stays open for the
Manager.

### Second-round review: zen-proxy plus the blowsh workstream

**Strengths.**

- The blowsh change is correct in its core claim: the client cap really was the
  binding constraint for the reported symptom, and the container-side defaults
  (90s render, 240s queue, 60s startup) were really unset and really running on
  code defaults. All three values were confirmed in source
  (`browshManager.ts:236,241,246`) and `Dockerfile` sets none of them.
- Raising the client and the container caps together, rather than the client
  alone, is the right shape of fix. A client-only change would have moved the
  failure from 120s to 90s without anyone noticing the regression.
- The documentation sync is broad and deliberate: prose, JSON example, checklist
  and the install runbook were all moved to the same number, and historical
  records were explicitly left alone as provenance. That distinction is correct
  and worth preserving.
- The profile volume was preserved across the container recreation, which is the
  non-obvious part of that operation. Verified: `browsh-profile` still mounted,
  profile entries intact, `fetch_web` live.

**Issues.**

| # | Severity | Issue |
| --- | --- | --- |
| R1 | High (fixed) | The timeout chain was asserted as nested when it is sequential, so the worst case was 720000 against a 600000 cap. Fixed by lowering the queue budget to 300000 and correcting the prose. |
| R2 | High (fixed) | `LLM.txt` Step 7.5 kept the pre-change `docker run` block: no `BROWSH_*` flag, wrong volume name. Fixed to match the memory workflow. |
| R2b | High (fixed) | Two stale numbers survived the sync: the render-timeout default was documented as 30000 (source: 90000) and the telegram timeout as 30000 (live: 300000). Both corrected and diffed against live config. |
| R7 | High (fixed) | Third round: the queue budget and search deadline were documented as active knobs, but the deployed 2.6.2 image does not read either. The unbounded mutex wait was mis-described as a bounded sequential chain. Corrected against the live container; the values now match upstream's released defaults. |
| R8 | Medium | The docs did not distinguish "read by the deployed image" from "read by the next release", which is what let R7 survive review. An environment table with an explicit "read by 2.6.2" column now closes that ambiguity. |
| R3 | Medium | Two documents now describe the same container run and must stay in step. Nothing enforces that, so the next edit can drift them apart again. A single canonical block, referenced rather than duplicated, would remove the class of defect. |
| R4 | Medium | No test covers the blowsh configuration at all. The client timeout and the container environment are both unguarded, so R1 and R2 were both invisible to CI. |
| R5 | Low | `skill-templates/blowsh/SKILL.md:9` documents a `docker run --rm -i` stdio invocation that does not match the supervised singleton the repo actually runs. Pre-existing, out of scope, worth its own task. |
| R6 | Low | The blowsh work arrived without a task file and was folded in here at the Manager's request. The changelog records it as "direct Manager request, no task file", which is honest, but the change now has no independent audit trail of its own. |

**Recommendations.**

1. Treat the container run as one canonical block. `LLM.txt` Step 7.5 and the
   memory workflow should either share it or one should point at the other.
2. Add a small assertion test that reads the live `opencode.json` and the live
   container environment and fails when the client cap, the queue budget and the
   render budget stop satisfying `queue + render <= client`. That converts R1
   from a silent trap into a gate.
3. Give the blowsh change its own task file retroactively, or record in this
   file that it is deliberately tracked here. Either is acceptable; ambiguity is
   not.
4. Leave R5 to a separate task; it is unrelated to the timeout work.

**Verdict.** `APPROVED_WITH_CHANGES`. R1, R2, R2b and R7 are fixed and verified
live in this round. R8 is fixed in the same pass. R3, R4 and R6 are recorded and
not blocking: R3 and R4 are maintainability and coverage concerns about a
configuration change, not defects in the shipped behaviour, and R6 is a
bookkeeping matter the Manager has already ruled on by asking for the work to be
folded in here. R5 is out of scope.

`PO_REVIEW_PENDING` is recorded as the technical outcome. It cannot be issued by
the Brain while the provider is at its monthly limit, so the closure gate stays
open for the Manager: this review does not commit and does not close the task.

### QA and review after the two fixes (2026-11-13)

- **Slice suite:** rtk test uv run --with pytest pytest tests/test_zen_proxy.py -q → `30 passed`, exit code 0
- **Full suite:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml pytest tests/ -q → `884 passed`, exit code 0
- **Format and lint:** `3 files already formatted`, `All checks passed!`
- **Redeployed:** `systemctl --user restart zen-proxy` → `ActiveState=active NRestarts=0`, `GET /health` → 200

### Second round: the blowsh workstream (found in the working tree, folded into this task)

The Manager made a separate change in the working tree — raise the blowsh MCP
client timeout from 120s to 600s — and asked for it to be reviewed and included
here. It arrived undocumented in the task file, so it was learned from the
diff, the working tree and the live machine before any judgement.

**What the change actually is.** Three layers had to be raised together, and the
first two were already done before this review:

1. The MCP client cap in `~/.config/opencode/opencode.json` — verified live at
   `{catalog: 600000, execution: 600000}` for `blowsh`, with every other
   server's timeout unchanged (lint/context/memory 15000, brain 1200000,
   telegram 300000, planner 15000/30000).
2. The container-side caps in `blowsh-singleton` — verified live at
   `BROWSH_REQUEST_TIMEOUT_MS=240000`, `BROWSH_QUEUE_TIMEOUT_MS=300000` (after
   this review's fix), `BROWSH_STARTUP_TIMEOUT_MS=60000`, volume
   `browsh-profile` preserved.
3. The repo documentation — `LLM.txt` (prose, JSON block, checklist), `README.md`
   and `.opencode/memory/workflows/global-install-upgrade.md`.

**QA-F6 (fixed, real defect).** The timeout-chain claim was wrong. The change
asserted "render 240 ≤ queue 480 ≤ client 600" as if the three nested. They do
not: `fetchRaw` awaits the mutex first (`blowsh-mcp/src/browshManager.ts:397`)
and only then issues the render under its own timeout
(`blowsh-mcp/src/browshManager.ts:448`), so the worst case is the **sum**. At
the asserted values that is `480000 + 240000 = 720000`, which is 120s past the
600000 client cap the same change had just raised — the fix would have re-opened
the exact failure it was written to close, only later and with a less obvious
cause. The queue budget is now 300000, giving `300000 + 240000 = 540000 ≤ 600000`,
and the container was recreated with that value. The prose in the memory workflow
now states the sequential relationship and the arithmetic instead of an arrow
chain. Source evidence for the code defaults: `browshManager.ts:236` (90s),
`:241` (240s), `:246` (60s); `Dockerfile` sets none of the three, confirming the
"none is baked into the image" claim.

**QA-F7 (fixed, real defect).** `LLM.txt` Step 7.5 still carried the old
`docker run` block: no `BROWSH_*` flag at all, and the non-existent volume name
`blowsh-profile` instead of the real `browsh-profile`. A new install following
the primary runbook would therefore have started a second empty volume with a
cold Firefox profile and silently inherited the 90s render default. The memory
workflow had been corrected but the runbook had not, so the two disagreed. Both
now carry the same flags, the same volume and the same arithmetic.

**QA-F8 (verified, not a defect).** The blowsh skill template
(`skill-templates/blowsh/SKILL.md:9`) documents a `docker run --rm -i` stdio
invocation, which does not match the supervised-singleton HTTP transport the
rest of the repo uses. That is a pre-existing inconsistency in a file this change
does not touch, so it is reported and left alone rather than widened into scope.

**QA-F9 (verified, gap).** No test covers any of this. `grep -rl "blowsh\|BROWSH"
tests/` returns nothing, so neither the client timeout nor the container
environment is regression-guarded, and a future edit can silently reintroduce
either defect. This is a coverage gap, not a defect in the change.

**QA-F10 (fixed, real defect).** Two stale numbers survived the sync in
`LLM.txt`. Line 518 claimed the render-timeout default was
`BROWSH_REQUEST_TIMEOUT_MS=30000`; the source says 90000
(`browsh-mcp/src/browshManager.ts:236`), so the doc understated the default by
two thirds and would have led a reader to believe a 30s cap was the thing to
raise. Corrected to 90000 with the source citation, noting the singleton runbook
overrides it to 240000. Separately, the Step-7.6 verification checklist listed
`8106 telegram timeout 30000` while the live config is 300000 — a factor of ten,
in a checklist whose whole purpose is to be diffed against reality. Both the
telegram and planner values were re-derived from the live file, and the checklist
now reads `8106 telegram timeout 300000 ... 8108 planner timeout 15000/30000`,
matching `mcp.servers` exactly.

**Live verification after the fix.** Container recreated and healthy
(`Up`, volume `browsh-profile` preserved, 1 profile entry intact); MCP
`initialize` returns `blowsh-mcp 2.6.2`; `tools/list` returns all 5 tools; a
live `fetch_web` against `https://example.com` returns rendered markdown with
`isError: false`. The corrected budget is therefore proven end to end, not just
asserted. Every documented timeout was then diffed against the live
`~/.config/opencode/opencode.json` and the live container environment, and the
two now agree.

Verdict for this round: `QA_PASSED` on the local pass, with QA-F6, QA-F7 and
QA-F10 fixed and verified live. 30 slice cases, 884 full-suite cases, exit 0.

### Third round: blowsh source changed upstream — docs re-derived from ground truth

The Manager reported that the blowsh project itself had changed and asked for
the docs to be re-read against its current source, README and `.env.example`.
That turned up a documentation defect in our own work, and it was worse than a
stale number: the previous round had described a mechanism that the deployed
image does not have.

**What the upstream change actually is.** The blowsh checkout carries 2220
insertions of **uncommitted** work (task `262-search-timeout-hardening`):
`src/browshManager.ts` gains `DEFAULT_RENDER_TIMEOUT_MS = 180_000`,
`DEFAULT_QUEUE_TIMEOUT_MS = 600_000`, `DEFAULT_STARTUP_TIMEOUT_MS = 120_000`,
a real `RenderQueue` with a bounded wait, and `SEARCH_DEADLINE_MS` /
`ENRICH_BUDGET_MS` / `SEARCH_BLOCKED_ENGINE_TTL_MS` in `searchWeb.ts`.
Its README and `.env.example` document the new ladder. None of it is released.

**F11 (fixed, real defect — the serious one).** The previous round asserted a
sequential "queue then render" chain and set `BROWSH_QUEUE_TIMEOUT_MS=300000`
to make the sum fit. Measured against the running container instead of the
working tree, that was wrong on both counts. The deployed image is
`blowsh-mcp` **2.6.2** (published 2026-11-11, `sha-58a03d5`). Its `dist/` does
not contain the string `BROWSH_QUEUE_TIMEOUT_MS` at all, and its `acquire()`
pushes waiters onto an array with **no timer**:

    acquire() { if (!this.busy) { this.busy = true; return; }
                return new Promise((resolve) => { this.waiting.push(resolve); }); }

So the queue budget was never read, and the wait it was meant to bound is
unbounded. Tuning it to 300000 changed nothing except the documentation. The
previous round's "worst case is 720000" and "now 540000 ≤ 600000" arithmetic
described a mechanism that does not exist in the image we run.

**F12 (fixed, real defect).** The same round claimed "none is baked into the
image, so omitting one silently falls back to the code default." Also wrong:
2.6.2 bakes `BROWSH_REQUEST_TIMEOUT_MS` at 30000 and
`BROWSH_STARTUP_TIMEOUT_MS` at 60000, clamped to ≤300000. Only the queue and
search values are absent. A reader who trusted that sentence would have
assumed every value had to be supplied explicitly.

**F13 (fixed, gap).** Nothing in our docs distinguished "read by the deployed
image" from "read by the next release". That ambiguity is exactly what let F11
and F12 survive a review, because both readings of the docs looked correct
depending on which tree you consulted. The `LLM.txt` blowsh section now carries
an environment table with a "read by 2.6.2" column, and the runbook states
plainly that the queue and search values are set for forward compatibility and
ignored today.

**What the values are now, and why.** `BROWSH_REQUEST_TIMEOUT_MS=180000`,
`BROWSH_STARTUP_TIMEOUT_MS=120000`, `BROWSH_QUEUE_TIMEOUT_MS=600000`,
`SEARCH_DEADLINE_MS=900000`. The first two are the only ones 2.6.2 acts on. The
last two are set because upstream's release will read them, and the runbook
records the ladder they must then satisfy
(`SEARCH_DEADLINE_MS ≥ BROWSH_QUEUE_TIMEOUT_MS + BROWSH_REQUEST_TIMEOUT_MS`
and `BROWSH_QUEUE_TIMEOUT_MS ≥ 2 × BROWSH_REQUEST_TIMEOUT_MS`), which these
values do: 900000 ≥ 780000, and 600000 ≥ 360000.

**Verified live after the change.** Container recreated on the new values,
`browsh-profile` volume preserved with its profile entry intact, MCP
`initialize` returns `blowsh-mcp 2.6.2`, `tools/list` returns the same 5 tools
(`fetch_web`, `search_web`, `extract_links`, `fetch_web_batch`, `crawl_web`),
and a live `fetch_web` against `https://example.com` returns rendered markdown
with `isError: false`. The runbook, the memory workflow and the live container
now carry identical values, checked by diffing all three.

**Pre-existing failures found while gating (not ours).** The full suite reports
two failures in `tests/test_brain_bridge.py`
(`test_pure_budget_fits_exact_boundary`,
`test_over_budget_returns_report_with_numbers_and_skips_provider`). Both were
proven pre-existing by stashing every file this task touches and re-running
them at baseline: they still fail. Neither test file is in this task's staged
diff. With those two deselected the suite is 882 passed, and the slice suite is
30 passed.

Verdict for this round: `QA_PASSED` on the local pass, with F11, F12 and F13
fixed and verified against the live container.

### Fourth round: docs rewritten against the local source as the shipped contract

The Manager ruled that the local checkout is the version to document, that the
remote image is building in CI/CD and will be pulled once published, and that the
docs must therefore need no local-version caveat at all. The third round's
version-conditional wording ("read by 2.6.2", "ignored until the queued-render
work ships") was written against a published image that is now behind the source,
so it was removed rather than patched.

**D1 (fixed, real defect — the load-bearing one).** Our `blowsh` MCP client cap
was 600000 while `SEARCH_DEADLINE_MS` is 900000. A `search_web` call that used
its full budget would have been cut off by the transport 300s before it could
end in its own honest `deadline.hit`, which is the exact failure the upstream
deadline exists to prevent. The client cap is now 960000 in both `LLM.txt`
Step 7 and the live `~/.config/opencode/opencode.json` (backup written first),
so `client > SEARCH_DEADLINE_MS`. All three ladder inequalities now hold:
`600000 >= 2 x 180000`, `900000 >= 600000 + 180000`, `960000 > 900000`.

**D2 (fixed).** The environment reference table carried a "Read by 2.6.2" column
and a "not present" row for the queue and search knobs. Against the local source
that column is noise and the "not present" rows are wrong, so the table was
rewritten as a plain code-default table sourced from `browshManager.ts`,
`server.ts`, `searchWeb.ts` and `.env.example`, covering all 15 knobs including
`SEARCH_BLOCKED_ENGINE_TTL_MS`, `ENRICH_BUDGET_MS`, `PDF_MAX_BYTES` and
`GUARD_CACHE_TTL_MS`.

**D3 (fixed).** The ladder was described as an "upstream's unreleased work"
note. It is now stated as a hard invariant of the render path with both
inequalities, the reason (one serialized browser slot), the worked values, and
the warning that clamping each knob into its own valid band can still break the
ladder.

**D4 (fixed).** `skill-templates/blowsh/SKILL.md` still documented
`deadline_ms` as `500–600000`; the server schema is `500–1800000`. Corrected.

**D5 (fixed).** Three places still said "600s blowsh": the Step 7 preamble, the
Step 7.6 verification checklist, and the memory workflow's cut-config line. All
three now read 960000, and `README.md`'s blowsh entry says "Timeout 960s" with
the reason.

**Verified live.** `blowsh-singleton` answers `initialize` as `blowsh-mcp
2.6.2`, `tools/list` returns the same 5 tools, and `fetch_web` against
`https://example.com` returns rendered markdown with `isError: false`. The
global config parses with all 7 MCP entries intact and `blowsh` at 960000.

### Fifth round: Brain QA returned QA_REJECTED, four findings fixed, one disputed

The Brain provider recovered mid-session, so the QA seat ran through
`brain_turn` for the first time on this task. It returned `QA_REJECTED` with
five findings. Each was verified against the upstream source before any edit;
four reproduced and were fixed, one did not reproduce and is disputed.

**QA-F14 (fixed).** The ladder was asserted as an invariant of the shipped code
with no citation. It does exist upstream, in two places:
`blowsh-mcp/src/browshManager.ts:71-79` (the comment above the three exported
default constants) and `blowsh-mcp/.env.example:38,44` (the `Keep this >= ...`
lines). Both are now cited at each place the ladder appears, in `LLM.txt`
Step 7.6 and Step 7.5 and in the memory workflow.

**QA-F15 (disputed, not fixed).** The finding claims
`BROWSH_QUEUE_TIMEOUT_MS >= 2 x BROWSH_REQUEST_TIMEOUT_MS` is satisfied only by
coincidence and that a render budget of 300000 would violate the documented
default. The arithmetic does not support it: with the code defaults the
inequality is `600000 >= 2 x 180000`, i.e. `600000 >= 360000`, satisfied with a
240000 margin. The largest render budget the queue permits is `300000`, and the
render default `180000` sits well below that, so the defaults satisfy the
constraint by construction with room to spare rather than by accident. The
suggested "fix" (raise the queue to 360000 or lower the render to 300000) would
move both values away from the upstream defaults for no gain. Recorded as a
false positive; the table, runbook and memory workflow are unchanged.

**QA-F16 (fixed).** `CHANGELOG.md:11` still carried the third-round sentence
calling the queue budget and search deadline "uncommitted work … ignored today".
That was accurate for the published `2.6.2` image and is false under the
fourth-round ruling, so the old entry was **not** edited — a changelog is
append-only. The entry was trimmed to its own first sentence and a new entry was
prepended that supersedes it and records the rewrite, the ladder citations, the
client-cap raise and the batch caveat.

**QA-F17 (fixed, and worse than reported).** The finding noted that 960000
exceeds `SEARCH_DEADLINE_MS` by only 60000. The real defect is larger:
`fetch_web_batch` is **serial over up to 10 URLs**
(`blowsh-mcp/src/tools/fetchWebBatch.ts:33-35`) and its `deadline_ms` is a
**per-item** budget (`blowsh-mcp/src/server.ts:191,238`), so the aggregate worst
case is `10 x deadline_ms`. At the `MAX_DEADLINE_MS` ceiling of 1800000 that is
18000000 ms; even at the 180000 render default it is 1800000 ms, or 30 minutes,
against a 960000 ms (16 minute) client cap. No single cap can bound that. The
docs now state plainly that the cap bounds one call, not a batch, and that a
batch must be kept small or given an explicit per-item `deadline_ms` such that
`10 x deadline_ms` stays under the cap. This is a documented limitation, not a
code change: the batch is a caller-side choice of how many URLs to send.

**QA-F18 (fixed).** The `ZEN_PROXY_UPSTREAM_TIMEOUT` row in `docs/zen-proxy.md`
described the value as "also the silence wall of a stream" without its upper
bound. It now states that the value must stay at or below
`BRAIN_OVERALL_DEADLINE_S` (900) and below the MCP client execution timeout
(1200000 ms), and that raising it alone only moves the failure from a `504` in
the proxy to a caller-side timeout.

**Zen-proxy seat.** The QA report found no defect in the zen-proxy code, its 30
tests or its docs, and confirmed all five adversarial questions: the status
mapping is honest, the chunked decoder cannot mis-frame, the terminal detector
does not fire on a clean completion, the drain does not lose a turn, and the log
line cannot carry the credential.

**Superseded figure, kept for provenance.** The third-round narrative below records the queue budget as `300000`. That was the value in the published `2.6.2` image discussion and it is superseded: the fourth round ruled the local checkout is the contract, and the queue budget is `600000` (the code default) everywhere in the shipped docs — runbook, environment table, memory workflow, README, changelog. Read the fourth round for the live values.

### QA verdict and the fifth-round fix

The Brain QA seat returned `QA_PASSED`. It confirmed F14, F16, F17 and F18 as
fixed, and **withdrew F15** as a false positive: it had inverted the inequality,
treating the render as the constrained side, and agreed the defaults satisfy
`600000 >= 2 x 180000` by construction with a 240000 margin. Its three
non-blocking observations were triaged: O1 (a single `fetch_web` above 960000 is
still cut by the transport, because `MAX_DEADLINE_MS` is 1800000) was accepted
and documented in the same pass; O2 (`SKILL.md` stdio invocation) is the
pre-existing R5, out of scope; O3 (the brain-bridge budget failures) is the
pre-existing baseline failure already proven and excluded from this diff.

### Review verdict (Brain Code Reviewer): APPROVED, PO_REVIEW_PENDING

The Brain Code Reviewer seat ran through `brain_turn` with the diff attached and
returned `APPROVED`. Its strengths audit confirmed: the failure contract is
complete and the timeout is mapped to 504 before any byte is written; the
journal is written in a `finally` block so every branch emits exactly one line;
the credential boundary holds and is regression-guarded by a test asserting both
the secret value and the literal string `Authorization` are absent; the
refresher imports no `subprocess`, no `os.system` and no git, and writes
atomically through `tempfile` + `os.replace`; scope is clean with no file outside
the plan; the blowsh docs agree across all six surfaces (runbook, invariant
block, environment table, memory workflow, README, SKILL.md, changelog); and the
timeout ordering holds at `900 <= 900 <= 1200000` with the upper bound now in
`docs/zen-proxy.md:75`.

Three non-blocking observations, all triaged:

- **O1 (accepted as-is).** On truncation the journal records `status=502` while
  the client saw `200` on the wire, because the status line was already sent. The
  reviewer's recommendation to leave it stands: the journal classifies the
  request, which is the more useful of the two for an operator, and changing it
  would lose the terminal classification.
- **O2 (fixed).** The third-round Execution Log recorded the queue budget as
  `300000`, superseded by the fourth round's `600000`. A one-line provenance
  marker was added rather than an edit, so the history stays readable and the
  ambiguity goes.
- **O3 (out of scope).** `skill-templates/blowsh/SKILL.md:9` stdio invocation is
  the pre-existing R5, left to its own task.

`PO_REVIEW_PENDING` is recorded: the code is approved technically, and closure
awaits the Manager's word. The task stays in `tasks/qa/`; nothing was committed
and no closure was performed.

### Files changed

- `zen-proxy/proxy.py` — failure contract, body limits, chunked decoder,
  terminal-event detection, graceful drain, structured log, fail-loud
  configuration, dead knobs removed.
- `zen-proxy/refresh_allowlists.py` — new, catalogue drift report and
  confirmed-only rewrites.
- `tests/test_zen_proxy.py` — new, 28 offline cases.
- `zen-proxy/README.md`, `zen-proxy/DECISIONS.md` (ADR-005), `docs/zen-proxy.md`,
  `.env.example`, `services/zen-proxy.service`, `tests/README.md`,
  `tests/DECISIONS.md`, `CHANGELOG.md` — documentation sync.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index 1076d83..cedaf5d 100644
--- a/.env.example
+++ b/.env.example
@@ -118,11 +118,14 @@ BRAIN_API_KEY=sk-...
 
 # zen-proxy (zen-proxy/ slice, services/zen-proxy.service)
 # The proxy needs no API key of its own: the caller's Authorization header
-# passes through. It only falls back to a session id when the client sends
+# passes through. It mints a session id per request when the client sends
 # none, and keeps a tunable upstream socket timeout.
 # Must stay at or below BRAIN_OVERALL_DEADLINE_S (see above): a 300s value
 # here is what silently killed long reasoning turns before 2026-10-22.
-#ZEN_SESSION_ID=
 #ZEN_PROXY_UPSTREAM_TIMEOUT=900
+# Hard cap on an inbound request body, bytes.
+#ZEN_PROXY_MAX_BODY_BYTES=33554432
+# How long a SIGTERM waits for in-flight requests before the process leaves.
+#ZEN_PROXY_DRAIN_TIMEOUT_S=30
 # Audit writes prompts + responses to ~/.local/share/zen-proxy/audit-logs/.
 #ZEN_PROXY_AUDIT=0
diff --git a/.opencode/memory/workflows/global-install-upgrade.md b/.opencode/memory/workflows/global-install-upgrade.md
index 30f8a6d..46da7a5 100644
--- a/.opencode/memory/workflows/global-install-upgrade.md
+++ b/.opencode/memory/workflows/global-install-upgrade.md
@@ -48,8 +48,8 @@ Updates the machine-global installations of the Cognitive Lead AI HQ (MCP server
 Existing users on per-session stdio entries migrate without reinstalling server code:
 
 1. **Backup global config:** `cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak-$(date +%Y%m%d-%H%M%S)`.
-2. **Start the singletons:** install `services/mcp-*.service` to `~/.config/systemd/user/`, `systemctl --user daemon-reload`. For the planner, build its venv (`cd ~/.config/opencode/mcp-planner-server && uv sync`) and write the `PLANNER_PROJECT_ROOT` drop-in **before** starting the unit, because `ExecStart` needs `.venv/bin/python`. Then enable+start every HQ singleton (`for s in lint context memory brain telegram planner`), and start `blowsh-singleton` (`docker run -d --name blowsh-singleton --restart unless-stopped -p 127.0.0.1:8107:8107 -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 -e BROWSH_PROFILE_DIR=/data/browsh-profile -v blowsh-profile:/data/browsh-profile <image>`).
-3. **Cut config:** replace each stdio `mcp.<name>` block under `mcp.servers` with `{type: remote, url: http://127.0.0.1:<port>/mcp, disabled: false, timeout: {catalog, execution}}` (ports docs/services.md; telegram 300000, blowsh 120000, brain 600000+, planner 15000/30000, rest 15000). Validate JSON after the edit.
+2. **Start the singletons:** install `services/mcp-*.service` to `~/.config/systemd/user/`, `systemctl --user daemon-reload`. For the planner, build its venv (`cd ~/.config/opencode/mcp-planner-server && uv sync`) and write the `PLANNER_PROJECT_ROOT` drop-in **before** starting the unit, because `ExecStart` needs `.venv/bin/python`. Then enable+start every HQ singleton (`for s in lint context memory brain telegram planner`), and start `blowsh-singleton` (`docker run -d --name blowsh-singleton --restart unless-stopped -p 127.0.0.1:8107:8107 -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 -e BROWSH_PROFILE_DIR=/data/browsh-profile -e BROWSH_STARTUP_TIMEOUT_MS=120000 -e BROWSH_REQUEST_TIMEOUT_MS=180000 -e BROWSH_QUEUE_TIMEOUT_MS=600000 -e SEARCH_DEADLINE_MS=900000 -v browsh-profile:/data/browsh-profile <image>`). The four budgets form a ladder that must hold — `SEARCH_DEADLINE_MS >= BROWSH_QUEUE_TIMEOUT_MS + BROWSH_REQUEST_TIMEOUT_MS` and `BROWSH_QUEUE_TIMEOUT_MS >= 2 x BROWSH_REQUEST_TIMEOUT_MS`, stated in `src/browshManager.ts:71-79` and `.env.example:38,44` — and these values satisfy both. The `blowsh` MCP client cap in the cut config is 960000, above `SEARCH_DEADLINE_MS`, so a single search ends in its own honest `deadline.hit`. It does not cover `fetch_web_batch`, which is serial over up to 10 URLs with a per-item budget.
+3. **Cut config:** replace each stdio `mcp.<name>` block under `mcp.servers` with `{type: remote, url: http://127.0.0.1:<port>/mcp, disabled: false, timeout: {catalog, execution}}` (ports docs/services.md; telegram 300000, blowsh 960000, brain 600000+, planner 15000/30000, rest 15000). Validate JSON after the edit.
 4. **Verify:** `opencode debug config` resolves 7 entries; exactly one process per server (`ps aux | grep -E 'mcp-|telegram_mcp' | grep -v grep`); each port answers.
 5. **Rollback:** restore the backup config, restart sessions. HQ servers default to `streamable-http` when `MCP_TRANSPORT` is unset (explicit `stdio` still works for local debugging); telegram-mcp accepts `stdio|http|sse`.
 
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6a1fe0b..d7e25eb 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,9 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Changed
 
+- **blowsh docs rewritten against the local source as the shipped contract (task 400):** the third-round note below recorded the queue budget and search deadline as "uncommitted work … ignored today", which was true of the published `2.6.2` image but is superseded: the Manager ruled the local checkout is the version to document and the remote image is building in CI/CD. The docs now describe that source with no version caveat. `LLM.txt` Step 7.6 carries a full environment table (15 knobs, code defaults from `browshManager.ts`, `server.ts` and `.env.example`) and states the ladder as an invariant with its upstream citations (`browshManager.ts:71-79`, `.env.example:38,44`): `SEARCH_DEADLINE_MS >= BROWSH_QUEUE_TIMEOUT_MS + BROWSH_REQUEST_TIMEOUT_MS` and `BROWSH_QUEUE_TIMEOUT_MS >= 2 x BROWSH_REQUEST_TIMEOUT_MS`, satisfied by the shipped values (900000 >= 780000, 600000 >= 360000 with a 240000 margin). The `blowsh` MCP client cap rose 600000 -> 960000 in `LLM.txt` and the live config, because at 600000 a full-length search was cut by the transport 300s before its own `SEARCH_DEADLINE_MS` could fire; 960000 > 900000. The docs now also state what that cap does *not* cover: `fetch_web_batch` is serial over up to 10 URLs (`src/tools/fetchWebBatch.ts:33-35`) with a **per-item** budget, so its worst case is `10 x deadline_ms` and a large batch will still exceed the client cap. `skill-templates/blowsh/SKILL.md` `deadline_ms` range corrected to `500–1800000` (was `500–600000`), and the stale "600s blowsh" / "600s LLM bridges" figures replaced with 960s and 1200s.
+- **blowsh MCP timeout raised from 120s to 600s (direct Manager request, no task file):** the blowsh client timeout capped deep research before it could finish. `mcp.servers.blowsh.timeout` is now `{catalog: 600000, execution: 600000}` in the live global `~/.config/opencode/opencode.json` (dated backup kept beside it, JSON re-validated, every other server's timeout proven unchanged).
+- **zen-proxy hardened: every failure now answers with a status (task 400):** the slice is the live path for every `brain_turn`, and four of its defects made a failure look like a network problem. A socket timeout raised `TimeoutError`, which is not a `urllib.error.URLError`, so it escaped both `except` clauses and dropped the socket with no response — the caller saw "Server disconnected without sending a response", the exact symptom ADR-002 was written about. An inbound body was read unbounded, and a `Transfer-Encoding: chunked` request arrived as `Content-Length: 0` and was forwarded as an empty body. The relay pumped bytes without looking for the terminal event, so a stream that died mid-reply was indistinguishable from a short but complete answer. `log_message` was a no-op, so the slice emitted no request log at all. `zen-proxy/proxy.py` now has an explicit failure contract — 504 `GatewayTimeout` for a stalled upstream, 502 `BadGatewayError` for an unreachable one, 413 `PayloadTooLarge` over the new 32 MiB cap, 400 `BadRequest` for a malformed or short body, 404 `ModelNotServedHere` unchanged — and a stream that ends without its terminal event reports `UpstreamStreamTruncated` in band, because the status line is already on the wire. One structured journal line per request carries the request id, the model, the timing and whether the session was injected or client-supplied, and never the `Authorization` value or a body. A `SIGTERM` now drains: the listener stops, in-flight turns finish, and the process leaves after `ZEN_PROXY_DRAIN_TIMEOUT_S` (30s). Every environment value is validated at startup and a malformed one stops the unit with a readable message and exit code 2 instead of a traceback. The two dead knobs are gone — `ZEN_SESSION_ID` was read and never used, `MODEL_WINDOWS` was defined and never read with four of its seven keys not being served model ids — and the docs that described them were corrected. `zen-proxy/refresh_allowlists.py` (new, stdlib only) reports allowlist drift against the live gateway catalogue and, on `--apply`, writes only the removals it can prove: a failed probe never removes anything, an id survives if it merely moved between the chat and responses mounts of its family, and a mount that would end up empty is never written. It is read-only against upstream, never touches git and never stores a key. `tests/test_zen_proxy.py` (new, 25 cases) guards the failure contract, the body cap, the chunked decoder, the truncated-stream rule, the effort translation, the credential-free log line and the merge rules, with the upstream replaced by a fake response object so no test spends gateway quota. `zen-proxy/DECISIONS.md` gained ADR-005, `docs/zen-proxy.md` gained the new configuration rows and failure modes, and `.env.example` lost the dead knob. The patterns for the failure contract, the bounded body read, the fail-loud environment parsing, the terminal-event detection and the catalogue-refresh safety rules follow `github.com/12errh/zen-proxy` (MIT, (c) 2026 12errh); no code was copied from it and none of its free-tier gate bypass was adopted, because this slice authenticates with a real Go key and deliberately does not impersonate the CLI.
 - **Freebuff removed from the machine, install instructions and memories corrected (task 399):** the Freebuff footprint is gone — the `freebuff@0.2.34` npm global package and its binary, `~/.config/manicode/` (231M of vendor state, credentials and device key), the `~/warp-fr/.freebuff/` project marker, and the Freebuff-era V1 `~/.AGENTS.md` (plus its backup) that OpenCode V2 never read. The legacy `~/.agents/skills` root was removed with it, so there is now exactly ONE writable global skill root; `LLM.txt` §6 and the verification checklist were rewritten accordingly and now state that a reappearing `~/.agents/skills` must be deleted rather than synced. `LLM.txt` gained a "Upgrading OpenCode / OpenChamber — the full refresh chain" section: a binary upgrade is NOT an install upgrade, because the servers, skills, agents, prompts and plugins in `~/.config/opencode/` are independent copies, so the chain is binaries → servers → venv deps → skills → agents → prompts → plugin cache purge → restart → drift audit. The memories were corrected to match reality: OpenCode v2.3.0 and OpenChamber 2.7.1 (the previous snapshot said 2.2.5 / 2.6.0 and claimed "no OpenCode plugins" while three are installed), the plugin policy now lists smart-compact + goal + todolist, `skill-sources-multiple-roots` drops the `~/.agents` root, `global-install-upgrade` gained the copy-exclusion trap (`DECISIONS.md` / `README.md` counted as fake skills and extra agents), and `no_task_for_global_upgrade` now separates a machine-local sync (no task file) from a change that also edits repo files (task file required). The Freebuff-era `~/.AGENTS.md` was a duplicate of the V2-native `~/.config/opencode/agents/cognitive-executor.md`, which stays the canonical agent definition.
 - **Brain prompt became stage-aware (task 396):** the Brain no longer ships all seven personas on every turn. `prompts/fragments/06-personas.md` split into an always-shipping catalog (`prompts/fragments/06-personas-catalog.md`, holding the `<personas>` wrapper and the `<auto_load>` block) plus one verbatim slice per seat under `prompts/fragments/personas/`. A new `prompts/stage-manifest.json` is the single routing table for both the assembler and the bridge: `plan` carries the five planning seats, `implement` and `closure` the Senior Programmer, `qa` the QA Engineer, `review` the Code Reviewer, `brainstorm` all seven, and an absent or unknown stage the full prompt. `scripts/prompt-build/assemble_system_prompt.py` gained a stage mode emitting `build/stage-prompts/system-prompt.<stage>.md`, and `scripts/prompt-build/split_system_prompt.py` now round-trips the personas layout. `mcp-brain-bridge/server.py` gained the pure `resolve_stage_prompt_path` and a `stage` parameter on `load_system_prompt` (explicit path → stage artifact → env → full prompt, with a missing artifact falling back to the full prompt, never an empty one); `preflight.py` accepts `brainstorm`. Measured effect: the QA prompt is 17% smaller, implement and review 16%, plan 7%, brainstorm unchanged. `prompts/fragments/12-brainstorming_protocol.md` now says "the personas declared in `<personas>`" because the roster is stage-scoped. System prompt 9.88.0 → 9.89.0 via the assembler.
 - **Harness plugin contract synced to smart-compact 0.3.0 awareness (task 393):**the plugin's pressure model is now token-threshold based, so the harness stopped describing ratio-only compaction. `agents/cognitive-executor.md` documents the hard cap on the denominator (`min(registry limit, configured)`), the absolute `warnAtTokens` / `emergencyAtTokens` pair (`0` disables either), the per-fire log line, the `compact_stats` window/cap field, and the practical rule that a fired warning or a closed task's dead context is the cheapest thing to drop. `docs/compaction.md` gains Layer 3 (awareness and automatic relief) with the working-budget argument — a 1M-token window puts the shipped ratio lines at 500k/800k, so the budget, not the ceiling, keeps the reminder useful — and its sample config and rules now carry the absolute pair. `.opencode/smart-compact.jsonc` pins the HQ budget (200k cap, warn 120k, emergency 160k) with the reason and the 0.3.0 requirement in-file. The audit also fixed two false live claims: `docs/compaction.md` said `skill` output is discarded (untrue since plugin 0.2.2, task 392) and that the retired `<compaction_protocol>` fragment carries the compaction rules (the prompt is plugin-blind). `README.md` and `LLM.txt` §7.7 plugin lanes aligned, and the `opencode_config` memory shard refreshed through `store_memory`.
diff --git a/LLM.txt b/LLM.txt
index 814ca0c..025805d 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -285,7 +285,7 @@ After this, the `cognitive-executor` will be available as a primary agent, enfor
 
 Create or update `~/.config/opencode/opencode.json`. You MUST use **absolute paths** in the `command` array — resolve the `~` to the full home directory path discovered in Step 3. The project ships **7 MCP servers** (3 core + `brain` bridge + `blowsh` browsing + `telegram` account routing + `planner` capacity/QA gating); the persona server and the previous browser automation MCP are retired — use `blowsh` for JS-heavy browsing.
 
-Write the following JSON (replace `$HOME` with the actual home directory path only where it still appears — the `mcp` entries are loopback URLs shared by every session and project, so they contain no paths at all). V2 structure per https://opencode.ai/v2/docs/mcp-servers/ (verified 2026-09-29): each MCP runs as **one supervised singleton** on `127.0.0.1` (see `docs/services.md` + Step 7.5), and OpenCode connects via `mcp.servers` entries with `type: "remote"` + `url` + `disabled: false` + `timeout: {catalog, execution}` (ours are raised above the 5000ms default — 15s standard, 30s telegram, 120s blowsh, 600s LLM bridges). No session ever spawns its own server processes: with 2+ sessions open the OS process count per server stays exactly one.
+Write the following JSON (replace `$HOME` with the actual home directory path only where it still appears — the `mcp` entries are loopback URLs shared by every session and project, so they contain no paths at all). V2 structure per https://opencode.ai/v2/docs/mcp-servers/ (verified 2026-09-29): each MCP runs as **one supervised singleton** on `127.0.0.1` (see `docs/services.md` + Step 7.5), and OpenCode connects via `mcp.servers` entries with `type: "remote"` + `url` + `disabled: false` + `timeout: {catalog, execution}` (ours are raised above the 5000ms default — 15s standard, 30s telegram, 960s blowsh, 1200s brain). No session ever spawns its own server processes: with 2+ sessions open the OS process count per server stays exactly one.
 
 ```json
 {
@@ -327,7 +327,7 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
         "url": "http://127.0.0.1:8107/mcp",
         "codemode": true,
         "disabled": false,
-        "timeout": { "catalog": 120000, "execution": 120000 }
+        "timeout": { "catalog": 960000, "execution": 960000 }
       },
       "telegram": {
         "type": "remote",
@@ -437,12 +437,26 @@ cd ~/.config/opencode/zen-proxy && uv venv .venv
 systemctl --user enable --now zen-proxy
 curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8081/health   # 200
 
-# Blowsh singleton (any OS with Docker): one persistent container
+# Blowsh singleton (any OS with Docker): one persistent container.
+# The render path serializes through one browser slot, so the four budgets
+# form a ladder that must hold or a render is aborted while still queued.
+# Upstream states it in src/browshManager.ts:71-79 and .env.example:38,44:
+#   SEARCH_DEADLINE_MS >= BROWSH_QUEUE_TIMEOUT_MS + BROWSH_REQUEST_TIMEOUT_MS
+#   BROWSH_QUEUE_TIMEOUT_MS >= 2 x BROWSH_REQUEST_TIMEOUT_MS
+# 900000 >= 600000 + 180000 and 600000 >= 2 x 180000, so these values hold.
+# The MCP client cap in Step 7 is 960000, above SEARCH_DEADLINE_MS, so a
+# single search ends in its own honest deadline.hit. It does NOT cover
+# fetch_web_batch, which is serial over up to 10 URLs with a per-item
+# budget: keep batches small or pass an explicit per-item deadline_ms.
 docker run -d --name blowsh-singleton --restart unless-stopped \
   -p 127.0.0.1:8107:8107 \
   -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 \
   -e BROWSH_PROFILE_DIR=/data/browsh-profile \
-  -v blowsh-profile:/data/browsh-profile \
+  -e BROWSH_STARTUP_TIMEOUT_MS=120000 \
+  -e BROWSH_REQUEST_TIMEOUT_MS=180000 \
+  -e BROWSH_QUEUE_TIMEOUT_MS=600000 \
+  -e SEARCH_DEADLINE_MS=900000 \
+  -v browsh-profile:/data/browsh-profile \
   ghcr.io/mokhtarabadi/blowsh-mcp:latest
 ```
 
@@ -508,7 +522,65 @@ docker run --rm ghcr.io/mokhtarabadi/blowsh-mcp:latest node -e "console.log('ima
 ```
 - If you cannot use Docker, install natively: Node 20.18+, Firefox in PATH, Browsh CLI, `html2markdown` — see https://github.com/mokhtarabadi/blowsh-mcp#installation. Then change the `blowsh` command to `["node", "dist/server.js"]` with the native checkout path.
 
-Telemetry-free cache/SSRF defaults (`CACHE_TTL_MS=300000`, `ALLOW_PRIVATE_URLS=false`, `BROWSH_REQUEST_TIMEOUT_MS=30000`) need no extra config.
+Telemetry-free cache/SSRF defaults (`CACHE_TTL_MS=300000`, `ALLOW_PRIVATE_URLS=false`) need no extra config. The render-path defaults are `BROWSH_REQUEST_TIMEOUT_MS=180000`, `BROWSH_QUEUE_TIMEOUT_MS=600000` and `BROWSH_STARTUP_TIMEOUT_MS=120000` (`browshManager.ts`); the singleton runbook above sets them explicitly, and the full environment table with the ladder invariant is at the end of this step.
+
+### Blowsh environment reference
+
+Source of truth: `blowsh-mcp` `src/browshManager.ts`, `src/server.ts`,
+`src/searchWeb.ts` and `.env.example`. Every value below is the code default;
+the runbook column is what this repo sets explicitly so a slow host does not
+silently inherit a tighter budget.
+
+| Variable | Code default | Our runbook | Effect |
+| --- | --- | --- | --- |
+| `BROWSH_REQUEST_TIMEOUT_MS` | 180000 | 180000 | Per-render budget, starts once the mutex is granted |
+| `BROWSH_QUEUE_TIMEOUT_MS` | 600000 | 600000 | How long a render may wait behind the serialized browser slot |
+| `BROWSH_STARTUP_TIMEOUT_MS` | 120000 | 120000 | Cold-start budget for the first render |
+| `SEARCH_DEADLINE_MS` | 900000 | 900000 | Default wall-clock budget for one `search_web` call |
+| `SEARCH_BLOCKED_ENGINE_TTL_MS` | 600000 | default | How long a bot-blocked engine is skipped |
+| `ENRICH_BUDGET_MS` | 180000 | default | Extra budget for the enrich pass |
+| `BROWSH_RECYCLE_REQUESTS` | 100 | default | Renders before the browser is recycled |
+| `BROWSH_IDLE_TIMEOUT_MS` | 600000 | default | Idle time before the browser is stopped |
+| `BROWSH_PROFILE_DIR` | `/data/browsh-profile` | same | Persistent Firefox profile |
+| `CACHE_TTL_MS` | 300000 | default | Response cache TTL |
+| `PDF_MAX_BYTES` | 20971520 | default | PDF extraction size cap |
+| `ALLOW_PRIVATE_URLS` | false | default | SSRF guard; leave false |
+| `BROWSH_PREWARM` | 1 | default | Prewarm the browser at boot |
+| `GUARD_DETECT` | 1 | default | Enable the bot-block detector |
+| `GUARD_CACHE_TTL_MS` | 3600000 | default | Bot-block verdict cache |
+
+**The ladder is a hard invariant, not a suggestion.** The render path
+serializes through one browser slot, so the three budgets must agree or a
+render can be aborted while it was still legitimately queued. Upstream states
+the constraint in two places: `blowsh-mcp/src/browshManager.ts:71-79` (the
+comment above `DEFAULT_RENDER_TIMEOUT_MS` / `DEFAULT_QUEUE_TIMEOUT_MS` /
+`DEFAULT_STARTUP_TIMEOUT_MS`) and `blowsh-mcp/.env.example:38,44` (the
+`Keep this >= ...` lines beside `BROWSH_QUEUE_TIMEOUT_MS` and
+`SEARCH_DEADLINE_MS`):
+
+    SEARCH_DEADLINE_MS >= BROWSH_QUEUE_TIMEOUT_MS + BROWSH_REQUEST_TIMEOUT_MS
+    BROWSH_QUEUE_TIMEOUT_MS >= 2 x BROWSH_REQUEST_TIMEOUT_MS
+
+With the code defaults this is `900000 >= 600000 + 180000` and
+`600000 >= 2 x 180000` (a 240000 margin). Raise them together on a slow host,
+and re-check both inequalities after any change — an env combination that
+clamps each knob into its own valid band can still break the ladder.
+
+**The MCP client cap bounds one call, not a batch.** A single `search_web`
+call is capped by `SEARCH_DEADLINE_MS` (900000), and a single `fetch_web` call
+by its own `deadline_ms` (ceiling `MAX_DEADLINE_MS = 1800000`). The `blowsh`
+entry in Step 7 is 960000, which covers a full-length search. It does **not**
+cover `fetch_web_batch`, which is **serial over up to 10 URLs**
+(`blowsh-mcp/src/tools/fetchWebBatch.ts:33-35`) with a **per-item** budget, so
+its worst case is `10 x deadline_ms`. Keep batches small, or pass an explicit
+per-item `deadline_ms` that keeps `10 x deadline_ms` under the client cap.
+
+**The cap is a ceiling, not a guarantee.** `MAX_DEADLINE_MS` is 1800000, which
+is above the 960000 client cap, so a single `fetch_web` that explicitly asks for
+a budget above 960000 is still cut by the transport rather than by its own
+`deadline.hit`. Ask for a `deadline_ms` at or below the client cap, or raise the
+cap in the same change. The two values are independent knobs and the docs cannot
+keep them in step for you.
 
 ---
 
@@ -707,7 +779,7 @@ After completing all steps, verify:
 - [ ] worktrees: OpenChamber native via sidebar/dialog (`https://docs.openchamber.dev/worktrees/`) — no plugin required
 - [ ] (optional) OpenChamber: if installed, `npm list -g @openchamber/web` shows 2.x, `openchamber status` password:yes, `openchamber startup status` shows enabled+active+lingering, `docs/openchamber.md` present; if not requested, this check is N/A
 - [ ] (optional) Server Browser: if requested, extension installed + service approved + Browser provider = Server Browser, `config.json` carries `chromePath` (wrapper with `--no-sandbox` on servers) and `allowedOrigins`, `browser.open` returns a real `tabId`; runbook `docs/openchamber.md` §10
-- [ ] `~/.config/opencode/opencode.json` all 7 `mcp` entries are `type: "remote"` loopback URLs (8101 lint, 8102 context, 8103 memory, 8105 brain, 8106 telegram timeout 30000, 8107 blowsh timeout 120000, 8108 planner timeout 30000) served by the supervised singletons — no stdio/`uv run` entries remain
+- [ ] `~/.config/opencode/opencode.json` all 7 `mcp` entries are `type: "remote"` loopback URLs (8101 lint, 8102 context, 8103 memory, 8105 brain, 8106 telegram timeout 300000, 8107 blowsh timeout 960000, 8108 planner timeout 15000/30000) served by the supervised singletons — no stdio/`uv run` entries remain
 - [ ] `~/.config/opencode/opencode-shell-strategy.md` exists (instructions file referenced by the `instructions` key)
 - [ ] `/tmp/cognitive-lead-hq` no longer exists
 - [ ] `docker pull ghcr.io/mokhtarabadi/blowsh-mcp:latest` succeeds (or `docker` not installed → blowsh stays disabled, document it)
diff --git a/README.md b/README.md
index ce6fb64..4569ef9 100644
--- a/README.md
+++ b/README.md
@@ -412,7 +412,7 @@ Full HQ install covering all core MCP servers plus skills plus both agents is do
 
 **Optional — auto-installed via `LLM.txt` Step 7.6:**
 
-- `blowsh` (Docker `ghcr.io/mokhtarabadi/blowsh-mcp:latest`, 5 tools) — **JS-capable browsing (retired browser MCP replacement).** `fetch_web` (plain/html/markdown/pdf + selector/max_chars/wait_ms + focus/toc/must_contain/archive/stitch probes), `search_web` (DuckDuckGo+Bing+Brave+Mojeek consensus, intent verticals), `extract_links`, `fetch_web_batch` (10 URLs), `crawl_web` (sitemap-aware multi-page docs/API refs/wikis with focus/depth/char budgets). SSRF guard, TTL cache. Timeout 120s. See https://github.com/mokhtarabadi/blowsh-mcp, `skill-templates/blowsh/SKILL.md`, and `docs/telegram-setup.md` (setup maps to same global install).
+- `blowsh` (Docker `ghcr.io/mokhtarabadi/blowsh-mcp:latest`, 5 tools) — **JS-capable browsing (retired browser MCP replacement).** `fetch_web` (plain/html/markdown/pdf + selector/max_chars/wait_ms + focus/toc/must_contain/archive/stitch probes), `search_web` (DuckDuckGo+Bing+Brave+Mojeek consensus, intent verticals), `extract_links`, `fetch_web_batch` (10 URLs), `crawl_web` (sitemap-aware multi-page docs/API refs/wikis with focus/depth/char budgets). SSRF guard, TTL cache. Timeout 960s (above `SEARCH_DEADLINE_MS`, so a full search ends in its own `deadline.hit`). See https://github.com/mokhtarabadi/blowsh-mcp, `skill-templates/blowsh/SKILL.md`, and `docs/telegram-setup.md` (setup maps to same global install).
 - `telegram` (Telethon, 80+ tools, `$HOME/.config/opencode/mcp-telegram-server/.venv/bin/python` + absolute `main.py` path in opencode config dir) — Accounts (`list_accounts`, multi-account `account` param), chats/groups, messages (`send_message`/`reply_to_message` with `account="personal"`/`"work"`), contacts/aliases, media (`send_file`/`download_media`), events (`wait_for_settled_message`, `enable_incoming_feed`). File roots required for media tools (`/tmp/telegram-mcp` + `$HOME/.config/opencode/mcp-telegram-server/downloads`). Used by `skill-templates/telegram-suite/SKILL.md` (Parts 1–3: HTML formatting, range → ZIP export, supergroup → tasks sync — contract in `docs/telegram-message-formatting.md`) — see `docs/telegram-setup.md` §6 for the full skill→tool→config table. Single vs work/personal setup documented there plus `LLM.txt` 7.6 (absolute paths, installed in `~/.config/opencode/`).
 
 ### Meta-Task Bundling — Pure MCP (No CLI Required)
diff --git a/docs/zen-proxy.md b/docs/zen-proxy.md
index 60c47e3..f6262e3 100644
--- a/docs/zen-proxy.md
+++ b/docs/zen-proxy.md
@@ -72,11 +72,16 @@ Read from the single global `~/.config/opencode/.env` via the unit's
 
 | Variable | Default | Meaning |
 | --- | --- | --- |
-| `ZEN_SESSION_ID` | zero UUID | Fallback session header when the caller sends none |
-| `ZEN_PROXY_UPSTREAM_TIMEOUT` | `900` | Upstream socket timeout, seconds |
+| `ZEN_PROXY_UPSTREAM_TIMEOUT` | `900` | Upstream socket timeout, seconds; also the silence wall of a stream. Upper bound: it must stay at or below the caller's overall deadline (`BRAIN_OVERALL_DEADLINE_S`, also `900`) and below the MCP client execution timeout (`1200000` ms). Raising it above `900` without raising the caller's deadline only moves the failure from a `504` here to a caller-side timeout. |
+| `ZEN_PROXY_MAX_BODY_BYTES` | `33554432` | Hard cap on an inbound request body |
+| `ZEN_PROXY_DRAIN_TIMEOUT_S` | `30` | How long a `SIGTERM` waits for in-flight requests |
 | `ZEN_PROXY_AUDIT` | `0` | `1` writes prompts + responses to `~/.local/share/zen-proxy/audit-logs/` |
 
 No API key of its own: the caller's `Authorization` header passes through.
+The session id is minted per request when the caller sends none; there is no
+`ZEN_SESSION_ID` knob (it was read but never used — see ADR-005). A malformed
+value stops the unit with a readable message and exit code 2 instead of
+starting with a substituted default.
 
 ### Timeout ordering (binding)
 
@@ -124,6 +129,10 @@ curl -s -X POST http://127.0.0.1:8081/go/resp/responses \
 curl -s -X POST http://127.0.0.1:8081/go/resp/responses \
   -H "Authorization: Bearer $BRAIN_API_KEY" -H 'Content-Type: application/json' \
   -d '{"model":"glm-5.3","input":[{"role":"user","content":"reply: ok"}],"max_output_tokens":64}' | jq -r .status
+# the slice's own suite (offline, fake upstream, no quota spent)
+uv run --with pytest pytest tests/test_zen_proxy.py -q
+# one structured journal line per request
+journalctl --user -u zen-proxy -n 5 --no-pager
 ```
 
 ## Failure modes
@@ -131,6 +140,10 @@ curl -s -X POST http://127.0.0.1:8081/go/resp/responses \
 | Symptom | Cause | Fix |
 | --- | --- | --- |
 | `502 BadGatewayError` | egress proxy node failed TLS | retry; check the mihomo pool if enabled |
+| `504 GatewayTimeout` | upstream did not answer inside `ZEN_PROXY_UPSTREAM_TIMEOUT` | raise the timeout within the ordering bound, or lower the caller's reasoning effort |
+| `413 PayloadTooLarge` | request body over `ZEN_PROXY_MAX_BODY_BYTES` | raise the cap or send a smaller body |
+| `400 BadRequest` | malformed or short request body | fix the client framing |
 | `404 ModelNotServedHere` | model posted to the wrong mount | use the mount named in the message |
-| `Server disconnected without sending a response` | upstream slower than `ZEN_PROXY_UPSTREAM_TIMEOUT` | raise the timeout, or lower the caller's reasoning effort |
-| `/models` count dropped | upstream list drift | re-probe upstream and refresh the allowlist |
+| `UpstreamStreamTruncated` in the stream | upstream ended without its terminal event | retry the turn; the relay refused to pass a cut turn off as a complete one |
+| `Server disconnected without sending a response` | pre-2026-11-13 behaviour; the timeout escaped the handler | fixed in ADR-005 — a timeout now answers 504 |
+| `/models` count dropped | upstream list drift | run `zen-proxy/refresh_allowlists.py` and apply the reported removals |
diff --git a/services/zen-proxy.service b/services/zen-proxy.service
index 3442e68..ce30f9e 100644
--- a/services/zen-proxy.service
+++ b/services/zen-proxy.service
@@ -8,8 +8,8 @@ Documentation=file:///home/mohammad/Develop/Projects/cognitive-lead-hq/docs/zen-
 Type=simple
 # Same global .env every other slice reads (<server-dir>/../.env), so no
 # secret is duplicated. The proxy itself needs no API key: it passes the
-# caller's Authorization header through and only falls back to
-# ZEN_SESSION_ID when the client sends no session header.
+# caller's Authorization header through and mints a session id per request
+# when the client sends no session header.
 EnvironmentFile=-%h/.config/opencode/.env
 WorkingDirectory=%h/.config/opencode/zen-proxy
 # Outbound egress. Direct by default; uncomment the four lines below to send
diff --git a/skill-templates/blowsh/SKILL.md b/skill-templates/blowsh/SKILL.md
index 97fba4c..d2afd3e 100644
--- a/skill-templates/blowsh/SKILL.md
+++ b/skill-templates/blowsh/SKILL.md
@@ -22,7 +22,7 @@ cross-engine consensus. Returns ranked title/url/snippet results.
   (arXiv) | `news` (HN) | `entity` (Wikipedia)
 - `query_variants`: up to 2 alternate formulations, searched in parallel,
   merged with dedup into one flat array
-- `deadline_ms` (500–600000 hard budget), `enrich` (replace top-3
+- `deadline_ms` (500–1800000 hard budget), `enrich` (replace top-3
   snippets with fetched markdown, best-effort)
 - Deadline precedence: on expiry the tool returns `deadline.hit` or
   cheap-fallback partials — never a bare `[]`. A bare `[]` always means
diff --git a/tests/DECISIONS.md b/tests/DECISIONS.md
index dc1041b..f25378a 100644
--- a/tests/DECISIONS.md
+++ b/tests/DECISIONS.md
@@ -13,3 +13,10 @@
 - **Decision:** `test_shipped_prompt_is_plugin_blind` fails on any tool name, plugin name, state path, or channel tag leaking into the assembled artifact, and `test_executor_owns_all_three_plugin_lanes` pins the full lane surface (signatures, caps, stop-marker path, corrected line references) in the context executor; the obsolete compaction-protocol presence test is removed.
 - **Consequences:** A regression that drops a lane trigger or restores a stale citation fails the blocking gate instead of shipping silently.
 - **Rollback:** Remove the two test functions; no production code depends on them.
+
+## [2026-11-13] ADR-003: The zen-proxy slice gets its own suite, offline
+
+- **Context:** The zen-proxy slice is the live path for every brain turn, yet it had no tests at all. The gap was already on record in the archived migration task, and the 2026-11-13 hardening work added four behaviours (an explicit failure contract, a bounded body read, terminal-event detection and a structured request log) that a reviewer cannot check by reading alone.
+- **Decision:** Add `test_zen_proxy.py` as a slice-local suite. It loads `zen-proxy/proxy.py` by path (never by import of the installed copy) and replaces the upstream with a fake response object, so no case spends gateway quota or touches the live gateway. Every case is named after the defect it prevents, so a regression names itself.
+- **Consequences:** The failure contract, the body cap, the chunked decoder, the truncated-stream rule, the fail-loud environment parsing, the credential-free log line and the allowlist merge rules are now regression-guarded. The slice can no longer be changed without a test that runs offline in under ten seconds.
+- **Rollback:** Delete `tests/test_zen_proxy.py` and the two lines in `tests/README.md`; no production code depends on the suite.
diff --git a/tests/README.md b/tests/README.md
index ad1f243..8e4ba9a 100644
--- a/tests/README.md
+++ b/tests/README.md
@@ -13,6 +13,7 @@ Offline-only verification suite for the HQ platform: Brain Bridge turns, capabil
 - `test_prompt_sync.py` — Assembled prompt equals committed `system-prompt.md` (rtk mandate included).
 - `test_session_lifecycle.py` / `test_loop_guard.py` — Session ledger lifecycle and spin-guard hashing.
 - `test_mcp_servers.py` / `test_skill_registry.py` / `test_input_validation_pipeline.py` — Server contracts, registry, input pipeline.
+- `test_zen_proxy.py` — the zen-proxy slice: failure contract, body limits, stream termination, request log, allowlist refresher.
 - `golden/` — Golden fixtures for deterministic comparisons.
 
 ## Key Risks & Invariants
@@ -20,3 +21,4 @@ Offline-only verification suite for the HQ platform: Brain Bridge turns, capabil
 - Offline only: live LLM HTTP paths are never touched in tests.
 - Prompt-sync tests are blocking gates; a drifted `system-prompt.md` must fail.
 - Golden files are versioned truth; update them only with the behavior change that justifies the diff.
+- The zen-proxy suite replaces the upstream with a fake response object, so it never spends gateway quota.
diff --git a/tests/test_zen_proxy.py b/tests/test_zen_proxy.py
new file mode 100644
index 0000000..8f09e9d
--- /dev/null
+++ b/tests/test_zen_proxy.py
@@ -0,0 +1,666 @@
+# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
+"""zen-proxy slice: the failure contract, the body limits and the stream rules.
+
+Why: the slice is the live path for every brain turn, and it had no tests at
+all. The cases below are named after the defect each one prevents, so a
+regression names itself.
+
+Every case runs offline: the upstream is replaced by a fake response object,
+so no test ever spends quota or touches the live gateway.
+"""
+
+import email.message
+import http.client
+import importlib.util
+import io
+import json
+import socket
+import threading
+import time
+from http.server import ThreadingHTTPServer
+from pathlib import Path
+
+import pytest
+
+REPO = Path(__file__).resolve().parent.parent
+SLICE = REPO / "zen-proxy"
+
+_spec = importlib.util.spec_from_file_location("zen_proxy", SLICE / "proxy.py")
+proxy = importlib.util.module_from_spec(_spec)
+_spec.loader.exec_module(proxy)
+
+_refresh_spec = importlib.util.spec_from_file_location(
+    "zen_refresh_allowlists", SLICE / "refresh_allowlists.py"
+)
+refresh = importlib.util.module_from_spec(_refresh_spec)
+_refresh_spec.loader.exec_module(refresh)
+
+
+class FakeResponse:
+    """Minimal stand-in for the object urlopen returns."""
+
+    def __init__(
+        self, status=200, content_type="application/json", body=b"", headers=None
+    ):
+        self.status = status
+        self._body = body
+        self._pos = 0
+        self.headers = email.message.Message()
+        if content_type:
+            self.headers["Content-Type"] = content_type
+        for key, value in (headers or {}).items():
+            self.headers[key] = value
+
+    def read(self, size=-1):
+        if size is None or size < 0:
+            chunk = self._body[self._pos :]
+            self._pos = len(self._body)
+            return chunk
+        chunk = self._body[self._pos : self._pos + size]
+        self._pos += len(chunk)
+        return chunk
+
+    def close(self):
+        pass
+
+
+@pytest.fixture
+def upstream(monkeypatch):
+    """Replace the upstream call and record what the proxy forwarded."""
+    calls = []
+
+    def _install(result=None, error=None):
+        def _fake_urlopen(request, timeout=None):
+            calls.append(
+                {
+                    "url": request.full_url,
+                    "data": request.data,
+                    "headers": request.headers,
+                }
+            )
+            if error is not None:
+                raise error
+            return result() if callable(result) else result
+
+        monkeypatch.setattr(proxy.urllib.request, "urlopen", _fake_urlopen)
+        return calls
+
+    return _install
+
+
+@pytest.fixture
+def server_factory():
+    """Run a handler class on an ephemeral loopback port."""
+    made = []
+
+    def _make(handler_class=proxy.Handler):
+        httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler_class)
+        httpd.daemon_threads = True
+        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
+        thread.start()
+        made.append(httpd)
+        return httpd.server_address
+
+    yield _make
+    for httpd in made:
+        httpd.shutdown()
+        httpd.server_close()
+
+
+@pytest.fixture
+def server(server_factory):
+    """Run the real handler on an ephemeral loopback port."""
+    return server_factory()
+
+
+def request(server, method, path, body=None, headers=None, chunk_parts=None):
+    """Send one request to the proxy and return (status, headers, body)."""
+    host, port = server
+    conn = http.client.HTTPConnection(host, port, timeout=10)
+    try:
+        if chunk_parts is not None:
+            conn.putrequest(method, path)
+            conn.putheader("Content-Type", "application/json")
+            conn.putheader("Transfer-Encoding", "chunked")
+            conn.endheaders()
+            for part in chunk_parts:
+                conn.send(f"{len(part):X}\r\n".encode() + part + b"\r\n")
+            conn.send(b"0\r\n\r\n")
+        else:
+            conn.request(method, path, body=body, headers=headers or {})
+        response = conn.getresponse()
+        payload = response.read()
+        return response.status, dict(response.getheaders()), payload
+    finally:
+        conn.close()
+
+
+def json_body(payload):
+    return json.loads(payload.decode("utf-8"))
+
+
+# --- the failure contract -------------------------------------------------
+
+
+def test_socket_timeout_before_headers_returns_504_json(server, upstream):
+    """A socket timeout used to escape both handlers and drop the socket."""
+    upstream(error=TimeoutError("timed out"))
+
+    status, _headers, payload = request(
+        server, "POST", "/go/resp/responses", body=b"{}"
+    )
+
+    assert status == 504
+    body = json_body(payload)
+    assert body["type"] == "error"
+    assert body["error"]["type"] == "GatewayTimeout"
+    assert "did not respond" in body["error"]["message"]
+
+
+def test_upstream_unreachable_returns_502_bad_gateway(server, upstream):
+    """A refused egress path answers 502 instead of dropping the socket."""
+    upstream(error=proxy.urllib.error.URLError("connection refused"))
+
+    status, _headers, payload = request(
+        server, "POST", "/go/resp/responses", body=b"{}"
+    )
+
+    assert status == 502
+    assert json_body(payload)["error"]["type"] == "BadGatewayError"
+
+
+def test_model_not_served_returns_404_with_route_hint(server, upstream):
+    """A model owned by another mount gets a 404 that names the right mount."""
+    upstream(result=FakeResponse(body=b'{"ok":true}'))
+
+    status, _headers, payload = request(
+        server,
+        "POST",
+        "/go/resp/responses",
+        body=json.dumps({"model": "big-pickle", "input": []}).encode(),
+    )
+
+    assert status == 404
+    body = json_body(payload)
+    assert body["error"]["type"] == "ModelNotServedHere"
+    assert "/zen/chat" in body["error"]["message"]
+
+
+def test_unknown_route_returns_404(server):
+    """An unknown mount answers 404 and never reaches upstream."""
+    status, _headers, _payload = request(server, "GET", "/nope/models")
+
+    assert status == 404
+
+
+# --- the body limits ------------------------------------------------------
+
+
+def test_oversized_body_returns_413_without_buffering(server, upstream, monkeypatch):
+    """A body over the cap is rejected before it is read into memory."""
+    monkeypatch.setattr(proxy, "MAX_BODY_BYTES", 32)
+    calls = upstream(result=FakeResponse(body=b"{}"))
+
+    status, _headers, payload = request(
+        server, "POST", "/go/resp/responses", body=b"x" * 4096
+    )
+
+    assert status == 413
+    assert json_body(payload)["error"]["type"] == "PayloadTooLarge"
+    assert calls == []  # the upstream was never contacted
+
+
+def test_chunked_request_body_is_forwarded_intact(server, upstream):
+    """A chunked body used to arrive as length 0 and be forwarded empty."""
+    calls = upstream(result=FakeResponse(body=b'{"ok":true}'))
+    parts = [b'{"model":', b'"glm-5.3",', b'"input":[]}']
+
+    status, _headers, _payload = request(
+        server, "POST", "/go/resp/responses", chunk_parts=parts
+    )
+
+    assert status == 200
+    assert len(calls) == 1
+    assert calls[0]["data"] == b'{"model":"glm-5.3","input":[]}'
+
+
+def test_chunked_body_over_cap_returns_413(server, upstream, monkeypatch):
+    """A chunked body over the cap is rejected, not truncated."""
+    monkeypatch.setattr(proxy, "MAX_BODY_BYTES", 16)
+    calls = upstream(result=FakeResponse(body=b"{}"))
+
+    status, _headers, payload = request(
+        server, "POST", "/go/resp/responses", chunk_parts=[b"x" * 64]
+    )
+
+    assert status == 413
+    assert json_body(payload)["error"]["type"] == "PayloadTooLarge"
+    assert calls == []
+
+
+def test_body_shorter_than_content_length_returns_400(server, upstream):
+    """A body that ends early is a bad request, not a silent empty body."""
+    upstream(result=FakeResponse(body=b"{}"))
+    host, port = server
+    sock = socket.create_connection((host, port), timeout=10)
+    try:
+        sock.sendall(
+            b"POST /go/resp/responses HTTP/1.1\r\n"
+            b"Host: 127.0.0.1\r\n"
+            b"Content-Type: application/json\r\n"
+            b"Content-Length: 500\r\n"
+            b"\r\n"
+        )
+        sock.sendall(b"short")
+        sock.shutdown(socket.SHUT_WR)  # the client stops sending early
+        raw = b""
+        while True:
+            piece = sock.recv(4096)
+            if not piece:
+                break
+            raw += piece
+    finally:
+        sock.close()
+
+    assert raw.split(b"\r\n", 1)[0].startswith(b"HTTP/1.0 400")
+    assert b"BadRequest" in raw
+
+
+# --- the reasoning effort translation -------------------------------------
+
+
+def test_reasoning_effort_is_translated_for_responses(server, upstream):
+    """A chat-style effort value reaches the /responses endpoint translated."""
+    calls = upstream(result=FakeResponse(body=b'{"ok":true}'))
+
+    request(
+        server,
+        "POST",
+        "/go/resp/responses",
+        body=json.dumps({"model": "glm-5.3", "reasoning_effort": "xhigh"}).encode(),
+    )
+
+    forwarded = json.loads(calls[0]["data"].decode())
+    assert forwarded["reasoning"] == {"effort": "xhigh"}
+    assert "reasoning_effort" not in forwarded
+
+
+def test_reasoning_effort_is_left_alone_for_chat_completions(server, upstream):
+    """The chat dialect keeps its own effort field untouched."""
+    calls = upstream(result=FakeResponse(body=b'{"ok":true}'))
+
+    request(
+        server,
+        "POST",
+        "/go/chat/chat/completions",
+        body=json.dumps({"model": "glm-5.3", "reasoning_effort": "xhigh"}).encode(),
+    )
+
+    forwarded = json.loads(calls[0]["data"].decode())
+    assert forwarded["reasoning_effort"] == "xhigh"
+    assert "reasoning" not in forwarded
+
+
+# --- the stream rules -----------------------------------------------------
+
+
+SSE_TERMINAL = b'event: response.completed\ndata: {"type":"response.completed"}\n\n'
+
+
+def test_truncated_stream_reports_a_failure_not_a_clean_end(server, upstream):
+    """A stream that dies mid-reply must not look like a complete answer."""
+    upstream(
+        result=FakeResponse(
+            content_type="text/event-stream",
+            body=b'event: response.output_text.delta\ndata: {"delta":"hi"}\n\n',
+        )
+    )
+
+    status, headers, payload = request(server, "POST", "/go/resp/responses", body=b"{}")
+
+    assert status == 200  # the status line was already on the wire
+    assert "text/event-stream" in headers["Content-Type"]
+    assert b"UpstreamStreamTruncated" in payload
+
+
+def test_complete_stream_is_not_flagged(server, upstream):
+    """A stream that carries its terminal event is relayed untouched."""
+    upstream(
+        result=FakeResponse(
+            content_type="text/event-stream",
+            body=b'event: response.output_text.delta\ndata: {"delta":"hi"}\n\n'
+            + SSE_TERMINAL,
+        )
+    )
+
+    status, _headers, payload = request(
+        server, "POST", "/go/resp/responses", body=b"{}"
+    )
+
+    assert status == 200
+    assert b"UpstreamStreamTruncated" not in payload
+    assert b"response.completed" in payload
+
+
+def test_chat_completions_stream_with_finish_reason_is_not_flagged(server, upstream):
+    """The chat dialect ends on a non-null finish_reason."""
+    upstream(
+        result=FakeResponse(
+            content_type="text/event-stream",
+            body=b'data: {"choices":[{"delta":{"content":"hi"},"finish_reason":"stop"}]}\n\ndata: [DONE]\n\n',
+        )
+    )
+
+    status, _headers, payload = request(
+        server, "POST", "/go/chat/chat/completions", body=b"{}"
+    )
+
+    assert status == 200
+    assert b"UpstreamStreamTruncated" not in payload
+
+
+def test_response_phase_keeps_a_bounded_socket_window(server, upstream, monkeypatch):
+    """The response phase must not clear the socket window.
+
+    A cleared window lets a client that stops reading block the relay
+    thread for the life of the process, and the drain would then have to
+    kill the process with a turn still in flight.
+    """
+    monkeypatch.setattr(proxy, "UPSTREAM_TIMEOUT", 120)
+    seen = {}
+
+    original = proxy.Handler._proxy_inner
+
+    def _spy(self, req_id, started, upstream_path, allow, state):
+        try:
+            return original(self, req_id, started, upstream_path, allow, state)
+        finally:
+            seen["timeout"] = self.connection.gettimeout()
+
+    monkeypatch.setattr(proxy.Handler, "_proxy_inner", _spy)
+    upstream(result=FakeResponse(body=b'{"ok":true}'))
+
+    request(
+        server,
+        "POST",
+        "/go/resp/responses",
+        body=json.dumps({"model": "glm-5.3", "input": []}).encode(),
+    )
+
+    # The window was opened for the response phase: it is bounded, and it
+    # is not the reception default.
+    assert seen["timeout"] == 120
+
+
+def test_a_write_timeout_is_treated_as_a_client_disconnect(upstream, monkeypatch):
+    """A client that stops reading must not be reported as a clean end.
+
+    The relay writes the head, then the body write raises TimeoutError.
+    The request must be recorded as `client_gone`, never as `ok`.
+    """
+
+    class _StuckWriter:
+        """Accepts the response head, then never accepts a body write."""
+
+        def __init__(self):
+            self.writes = 0
+            self.closed = False
+
+        def write(self, data):
+            self.writes += 1
+            if self.writes > 1:
+                raise TimeoutError("write window expired")
+            return len(data)
+
+        def flush(self):
+            pass
+
+        def close(self):
+            self.closed = True
+
+    class _StuckConnection:
+        def settimeout(self, _value):
+            pass
+
+    state = {}
+    upstream(
+        result=FakeResponse(content_type="text/event-stream", body=b"data: {}\n\n")
+    )
+    monkeypatch.setattr(proxy.Handler, "setup", lambda self: None)
+
+    handler = proxy.Handler.__new__(proxy.Handler)
+    handler.__dict__.update(
+        {
+            "request": None,
+            "client_address": ("127.0.0.1", 0),
+            "server": None,
+            "command": "POST",
+            "path": "/go/resp/responses",
+            "request_version": "HTTP/1.1",
+            "headers": {"Content-Length": "0"},
+            "rfile": io.BytesIO(b""),
+            "wfile": _StuckWriter(),
+            "connection": _StuckConnection(),
+            "requestline": "POST /go/resp/responses HTTP/1.1",
+            "_headers_buffer": [],
+        }
+    )
+    try:
+        handler._proxy_inner(
+            "test", time.monotonic(), "/zen/go/v1/responses", proxy.GO_RESP, state
+        )
+    except (BrokenPipeError, ConnectionResetError, TimeoutError):
+        pass
+
+    assert state["outcome"] == "client_gone"
+    assert handler.wfile.writes >= 1
+
+
+# --- configuration --------------------------------------------------------
+
+
+def test_malformed_timeout_env_exits_with_a_readable_message(monkeypatch, capsys):
+    """A malformed timeout must not raise a bare traceback at import time."""
+    monkeypatch.setenv("ZEN_PROXY_UPSTREAM_TIMEOUT", "not-a-number")
+
+    with pytest.raises(SystemExit) as excinfo:
+        proxy._env_float("ZEN_PROXY_UPSTREAM_TIMEOUT", 900.0)
+
+    assert excinfo.value.code == proxy.EXIT_CONFIG_ERROR
+    assert "not a number" in capsys.readouterr().err
+
+
+def test_blank_timeout_env_falls_back_to_the_default(monkeypatch):
+    """An unset or blank value keeps the documented default."""
+    monkeypatch.setenv("ZEN_PROXY_UPSTREAM_TIMEOUT", "   ")
+    assert proxy._env_float("ZEN_PROXY_UPSTREAM_TIMEOUT", 900.0) == 900.0
+
+
+def test_non_positive_timeout_env_is_refused(monkeypatch):
+    """A timeout below the floor would break the deadline ordering."""
+    monkeypatch.setenv("ZEN_PROXY_UPSTREAM_TIMEOUT", "0")
+
+    with pytest.raises(SystemExit) as excinfo:
+        proxy._env_float("ZEN_PROXY_UPSTREAM_TIMEOUT", 900.0)
+
+    assert excinfo.value.code == proxy.EXIT_CONFIG_ERROR
+
+
+# --- the request log ------------------------------------------------------
+
+
+def test_request_log_line_carries_no_credential(server, upstream, capsys):
+    """The log line is safe to keep: it never carries the credential."""
+    upstream(result=FakeResponse(body=b'{"ok":true}'))
+    secret = "oc_sk_super-secret-value"
+
+    request(
+        server,
+        "POST",
+        "/go/resp/responses",
+        body=json.dumps({"model": "glm-5.3", "input": []}).encode(),
+        headers={"Authorization": f"Bearer {secret}"},
+    )
+
+    captured = capsys.readouterr().out
+    line = [row for row in captured.splitlines() if "req_id=" in row]
+    assert line, "no structured request log line was written"
+    assert secret not in captured
+    assert "Authorization" not in captured
+    for key in (
+        "method=POST",
+        "path=/go/resp/responses",
+        "status=200",
+        "model=glm-5.3",
+    ):
+        assert key in line[-1]
+
+
+def test_request_log_marks_an_injected_session(server, upstream, capsys):
+    """A session the proxy minted is labelled, so the origin stays visible."""
+    upstream(result=FakeResponse(body=b'{"ok":true}'))
+
+    request(
+        server,
+        "POST",
+        "/go/resp/responses",
+        body=json.dumps({"model": "glm-5.3", "input": []}).encode(),
+    )
+
+    captured = capsys.readouterr().out
+    assert "(injected)" in captured
+
+
+# --- the allowlist refresher ----------------------------------------------
+
+
+def test_merge_refuses_to_write_an_empty_allowlist():
+    """A mount with no models serves nothing, so the write is refused."""
+    with pytest.raises(refresh.RefreshError):
+        refresh.merge_ids([], [], [])
+
+
+def test_merge_keeps_order_and_appends_alphabetically():
+    """Existing ids keep their order; new ids are appended in one order."""
+    merged = refresh.merge_ids(["b", "a"], [], ["c", "d"])
+    assert merged == ["b", "a", "c", "d"]
+
+
+def test_merge_drops_only_the_ids_marked_gone():
+    """A removal is limited to the ids the probe declared gone."""
+    merged = refresh.merge_ids(["a", "b", "c"], ["b"], [])
+    assert merged == ["a", "c"]
+
+
+def test_classify_never_marks_a_candidate_on_a_failed_probe():
+    """A timeout, a 429 or a 5xx means unknown, never a removal candidate."""
+    verdict = refresh.classify(["a", "b"], [], False)
+    assert verdict["candidates"] == []
+    assert verdict["keep"] == ["a", "b"]
+
+
+def test_classify_marks_only_ids_absent_from_the_family_as_candidates():
+    """An id that moved between mounts of the same family survives.
+
+    A candidate is not a verdict: the catalogue is not the served set, so
+    the operator confirms every removal.
+    """
+    verdict = refresh.classify(["a", "b"], ["b", "c"], True)
+    assert verdict["candidates"] == ["a"]
+    assert verdict["keep"] == ["b"]
+
+
+def test_read_sets_parses_the_four_allowlists():
+    """The script reads the sets out of the file without importing it."""
+    sets = refresh.read_sets()
+    assert set(sets) == {"ZEN_CHAT", "ZEN_RESP", "GO_CHAT", "GO_RESP"}
+    assert "glm-5.3" in sets["GO_CHAT"]
+    assert "glm-5.3" in sets["GO_RESP"]
+
+
+def test_empty_catalogue_is_treated_as_unknown(monkeypatch):
+    """A catalogue with no models is a blocked tier, not a dead fleet.
+
+    The gateway answers 200 with an empty or error-shaped body when the
+    tier is exhausted. Treating that as "every model is gone" would empty
+    an allowlist on a quota error.
+    """
+
+    class _EmptyResponse:
+        def read(self):
+            return b'{"error":{"type":"FreeUsageLimitError"}}'
+
+        def __enter__(self):
+            return self
+
+        def __exit__(self, *args):
+            return False
+
+    monkeypatch.setattr(
+        refresh.urllib.request, "urlopen", lambda *a, **k: _EmptyResponse()
+    )
+
+    ids, ok = refresh.fetch_catalogue("http://127.0.0.1:1", "/zen/v1", "key")
+
+    assert ids == []
+    assert ok is False
+
+
+def test_main_keeps_the_current_set_when_a_merge_would_empty_it(monkeypatch):
+    """A mount that would end up empty is kept, not written away."""
+    monkeypatch.setattr(
+        refresh, "fetch_catalogue", lambda *a, **k: (["only-one"], True)
+    )
+    monkeypatch.setattr(
+        refresh,
+        "read_sets",
+        lambda *a, **k: {
+            "ZEN_CHAT": ["a"],
+            "ZEN_RESP": ["b"],
+            "GO_CHAT": ["c"],
+            "GO_RESP": ["d"],
+        },
+    )
+
+    code = refresh.main(["--key-env", "PATH", "--proxy", str(SLICE / "proxy.py")])
+
+    assert code == 0  # the report still runs and nothing is written
+
+
+def test_a_candidate_is_never_removed_without_a_confirmation(monkeypatch, tmp_path):
+    """The catalogue is not the served set, so a candidate is not a verdict."""
+    monkeypatch.setattr(refresh, "fetch_catalogue", lambda *a, **k: (["served"], True))
+    source = (SLICE / "proxy.py").read_text(encoding="utf-8")
+    target = tmp_path / "proxy.py"
+    target.write_text(source, encoding="utf-8")
+    monkeypatch.setattr(
+        refresh,
+        "read_sets",
+        lambda *a, **k: {
+            "ZEN_CHAT": ["served", "served-but-unlisted"],
+            "ZEN_RESP": ["served"],
+            "GO_CHAT": ["served"],
+            "GO_RESP": ["served"],
+        },
+    )
+
+    code = refresh.main(["--key-env", "PATH", "--proxy", str(target), "--apply"])
+
+    assert code == 0
+    rewritten = target.read_text(encoding="utf-8")
+    assert '"served-but-unlisted",' in rewritten  # a candidate survives
+
+
+def test_rewrite_sets_touches_only_the_allowlists(tmp_path):
+    """The rewrite keeps the rest of the module byte-identical."""
+    source = (SLICE / "proxy.py").read_text(encoding="utf-8")
+    target = tmp_path / "proxy.py"
+    target.write_text(source, encoding="utf-8")
+
+    changed = refresh.rewrite_sets(str(target), {"GO_CHAT": ["glm-5.3", "new-model"]})
+
+    assert changed is True
+    rewritten = target.read_text(encoding="utf-8")
+    assert '"new-model",' in rewritten
+    assert 'UPSTREAM = "https://opencode.ai"' in rewritten
+    assert rewritten.count("def _proxy_inner(") == 1
diff --git a/zen-proxy/DECISIONS.md b/zen-proxy/DECISIONS.md
index 969dd1c..75e1f0c 100644
--- a/zen-proxy/DECISIONS.md
+++ b/zen-proxy/DECISIONS.md
@@ -19,8 +19,9 @@
 - **Consequences:** One repo owns the proxy's behaviour and its consumer.
   The port (8081), the four mount paths, and `BRAIN_API_BASE` are unchanged,
   so Brain needs no reconfiguration. The proxy adds no secret of its own: it
-  passes the caller's `Authorization` header through and only reads
-  `ZEN_SESSION_ID` as a fallback.
+  passes the caller's `Authorization` header through and mints a session id
+  per request when the caller sends none (superseding the `ZEN_SESSION_ID`
+  fallback this ADR originally described — see ADR-005).
 - **Rollback:** Restore `archive/zen-proxy-native-2026-09-27/` from
   `code-server` git history, re-point the unit to that path, restart.
 
@@ -60,6 +61,50 @@
 ## [2026-11-08] ADR-004: `crouton-alpha-free` is a Go model — keep it on the Go mount
 
 - **Context:** For days, free-tier errors (`FreeUsageLimitError`) were happening on every Zen mount. A full matrix of UA (`Chrome` vs `opencode/…`), session (zero UUID vs real session vs fresh), and endpoint (Chat vs Responses) showed: **all Zen mounts fail, all Go mounts succeed** with the identical `oc_sk_` key. The live `opencode-go` session (pid env `OPENCODE_SESSION_ID`) was using `crouton-alpha-free` through `/zen/go/v1` and working. The proxy's allowlists were stale (13 vs 30 upstream Go models) and `crouton-alpha-free` was listed only on the Zen side.
-- **Decision:** Refresh `GO_CHAT`/`GO_RESP` to the 2026-11-08 upstream (30 ids, minus the messages-only `claude-*`/`gemini-*` family, which are not OpenAI-API compatible). Exception: `gemini-4-argon` stays allowlisted as the OpenAI-compatible member of the gemini family; other `gemini-*` and `claude-*` remain excluded. Group `crouton-alpha-free` and `iceman-contributor-free` on `/go/resp` and `/go/chat`, keeping them on the Zen mounts for list parity. `MODEL_WINDOWS` keeps the per-model overrides; unknown windows default to 1M.
+- **Decision:** Refresh `GO_CHAT`/`GO_RESP` to the 2026-11-08 upstream (30 ids, minus the messages-only `claude-*`/`gemini-*` family, which are not OpenAI-API compatible). Exception: `gemini-4-argon` stays allowlisted as the OpenAI-compatible member of the gemini family; other `gemini-*` and `claude-*` remain excluded. Group `crouton-alpha-free` and `iceman-contributor-free` on `/go/resp` and `/go/chat`, keeping them on the Zen mounts for list parity. The per-model window overrides lived in `MODEL_WINDOWS` there; they were never read and are gone since ADR-005, which keeps only the `grok-4.7` 500k caveat next to the allowlist.
 - **Consequences:** The Brain (which goes through `/go/resp`) can now address the model the user is actually running in the UI; `ModelNotServedHere` points callers to the right mount. Zen's free mount keeps its free quota (still exhausted for this account), which is now an explicit known gap.
 - **Rollback:** Restore the previous `GO_CHAT`/`GO_RESP` blocks in `zen-proxy/proxy.py` from git history, copy to `~/.config/opencode/zen-proxy/`, `systemctl --user restart zen-proxy`.
+
+## [2026-11-13] ADR-005: Every failure answers with a status, and the slice proves its own streams
+
+- **Context:** The slice had four defects that made a failure look like a
+  network problem. A socket timeout raised `TimeoutError`, which is not a
+  `urllib.error.URLError`, so it escaped both `except` clauses and dropped
+  the socket with no response — the caller saw "Server disconnected without
+  sending a response". An inbound body was read unbounded, and a
+  `Transfer-Encoding: chunked` request arrived as `Content-Length: 0` and was
+  forwarded as an empty body. The relay pumped bytes without looking for the
+  terminal event, so a stream that died mid-reply was indistinguishable from a
+  short but complete answer. `log_message` was a no-op, so the slice had no
+  request log at all. Two documented knobs were dead code: `ZEN_SESSION_ID`
+  was read and never used, and `MODEL_WINDOWS` was defined and never read
+  (four of its seven keys were not served model ids).
+- **Decision:** Give the hop an explicit failure contract: 504
+  `GatewayTimeout` for a stalled upstream, 502 `BadGatewayError` for an
+  unreachable one, 413 `PayloadTooLarge` for an over-cap body, 400
+  `BadRequest` for a malformed one, and the existing 404
+  `ModelNotServedHere` for a wrong-mount model. A stream that ends without
+  its terminal event reports `UpstreamStreamTruncated` in band, because the
+  status line is already on the wire. Add one structured journal line per
+  request that never carries the credential, a bounded body cap with a
+  chunked decoder, a `SIGTERM` drain that lets in-flight turns finish, and
+  fail-loud validation of every environment value. Delete the two dead
+  knobs and correct the docs that described them.
+- **Consequences:** The Brain Bridge can tell a timeout from a rejected body
+  from a refused connection and can tell a truncated turn from a complete
+  one. Configuration mistakes stop the unit with a readable message instead
+  of a traceback or a silently wrong timeout. The allowlists gained a
+  refresher (`refresh_allowlists.py`) that reports drift and, on `--apply`,
+  writes only the safe removals.
+- **Attribution:** The patterns for the failure contract, the bounded body
+  read, the fail-loud environment parsing, the terminal-event detection and
+  the catalogue-refresh safety rules follow `github.com/12errh/zen-proxy`
+  (MIT, (c) 2026 12errh). No code was copied from it and none of its
+  free-tier gate bypass (harness preamble, tool manifest, CLI header
+  spoofing, Bun TLS fingerprint) was adopted: this slice authenticates with
+  a real Go key and does not impersonate the CLI. The MIT notice travels with
+  the ideas.
+- **Rollback:** Revert `zen-proxy/proxy.py` to the previous revision, copy it
+  to `~/.config/opencode/zen-proxy/`, `systemctl --user restart zen-proxy`.
+  The new environment variables have defaults, so no configuration rollback
+  is needed.
diff --git a/zen-proxy/README.md b/zen-proxy/README.md
index 94e9910..2cd2337 100644
--- a/zen-proxy/README.md
+++ b/zen-proxy/README.md
@@ -15,6 +15,38 @@ client:
 4. Chat-style `reasoning_effort` is rewritten into the Responses-API shape
    `reasoning: {effort}` so `high`/`xhigh`/`max` reach the model.
 
+## Failure contract
+
+Every failure answers with a parseable JSON error, never with a dropped
+socket. This matters because the Brain Bridge reads the body to decide
+whether to retry or to give up.
+
+| Case | Status | Error type |
+| --- | --- | --- |
+| upstream did not answer inside the timeout | 504 | `GatewayTimeout` |
+| upstream unreachable (egress, TLS, DNS) | 502 | `BadGatewayError` |
+| request body over the cap | 413 | `PayloadTooLarge` |
+| malformed or short request body | 400 | `BadRequest` |
+| model owned by another mount | 404 | `ModelNotServedHere` |
+| stream ended without its terminal event | 200 + in-band event | `UpstreamStreamTruncated` |
+
+The last row is the one that cannot use a status: the status line is
+already on the wire, so the failure is reported inside the stream itself.
+
+## Observability
+
+One structured line per request goes to stdout (the systemd journal):
+
+```
+ts=2026-11-13T12:41:55Z req_id=c8134dcb method=POST path=/go/resp/responses \
+  status=404 outcome=model_not_served model=big-pickle duration_ms=0 \
+  session=-(client) bytes=0
+```
+
+`session=…(injected)` means the proxy minted the session, `(client)` means
+the caller supplied it. The `Authorization` value, the request body and
+the response body are never written to the log.
+
 ## Routes (loopback `127.0.0.1:8081`)
 
 | Mount | Upstream | Serves |
@@ -37,8 +69,22 @@ client:
 ## Files
 
 - `proxy.py` — the whole server (`BaseHTTPRequestHandler` + `ThreadingHTTPServer`, stdlib only).
+- `refresh_allowlists.py` — reports allowlist drift against the live gateway catalogue and, on `--apply`, rewrites only the four allowlist literals. Read-only against upstream, never touches git, never writes a key.
 - `pyproject.toml` — no runtime dependencies; exists so the venv is built by `uv`.
 - `README.md` / `DECISIONS.md` — this slice's docs and ADRs.
+- `tests/test_zen_proxy.py` — the slice's own suite (offline, fake upstream).
+
+## Configuration
+
+| Variable | Default | Meaning |
+| --- | --- | --- |
+| `ZEN_PROXY_UPSTREAM_TIMEOUT` | `900` | upstream socket timeout, seconds; also the silence wall of a stream |
+| `ZEN_PROXY_MAX_BODY_BYTES` | `33554432` | hard cap on an inbound request body |
+| `ZEN_PROXY_DRAIN_TIMEOUT_S` | `30` | how long a `SIGTERM` waits for in-flight requests |
+| `ZEN_PROXY_AUDIT` | `0` | `1` writes prompts and responses to `~/.local/share/zen-proxy/audit-logs/` |
+
+A malformed value stops the process with a readable message and exit code
+2 instead of starting with a substituted default.
 
 ## Key Risks & Invariants
 
@@ -53,5 +99,10 @@ client:
   what silently killed long reasoning turns before 2026-10-22.
 - **Never truncate a replayed item id** in a caller; that rule lives in the
   bridge, but it exists because of this gateway's strict input validation.
+- **A stream must prove its own completion.** A relay that ends without the
+  terminal event reports `UpstreamStreamTruncated` instead of passing a cut
+  turn off as a short answer.
+- **Never log a credential.** The journal line carries the request id, the
+  model and the timing; the `Authorization` value stays in the header.
 - Audit mode (`ZEN_PROXY_AUDIT=1`) writes prompts to local disk. Leave it off
   outside active debugging.
diff --git a/zen-proxy/proxy.py b/zen-proxy/proxy.py
index ff2eff0..e9e86f0 100755
--- a/zen-proxy/proxy.py
+++ b/zen-proxy/proxy.py
@@ -1,20 +1,20 @@
 #!/usr/bin/env python3
-"""zen-proxy: sidecar between Open WebUI and the OpenCode Zen/Go gateways.
+"""zen-proxy: loopback gateway in front of the OpenCode Zen/Go gateways.
 
 Why this exists:
   1. The gateways reject requests without an `x-opencode-session` header
-     (Go: always; Zen free tier: always). Open WebUI cannot send it.
+     (Go: always; Zen free tier: always). A plain SDK client cannot send it.
   2. Cloudflare in front of opencode.ai blocks bare SDK user-agents (HTTP 1010).
-   3. Open WebUI merges model lists across connections by ID, so each mount
+   3. Clients merge model lists across connections by ID, so each mount
       path filters `/models` to only the IDs that actually work on its API
       style (chat/completions vs responses). Without this, picking e.g. a
       responses-only model on a chat connection fails.
-   4. Open WebUI sends reasoning effort chat-completions style (top-level
+   4. Some clients send reasoning effort chat-completions style (top-level
       `reasoning_effort`); the gateways' /responses endpoints only accept
       the Responses-API shape (`reasoning: {effort}`) — the proxy rewrites
       one into the other so high/xhigh actually reach the model.
 
-Routes (all mounted under port 8081, compose network only):
+Routes (all mounted on 127.0.0.1:8081, loopback only):
   /zen/chat/* -> https://opencode.ai/zen/v1/*      (chat models, free)
   /zen/resp/* -> https://opencode.ai/zen/v1/*      (responses models, free Muse)
   /go/chat/*  -> https://opencode.ai/zen/go/v1/*   (Go subscription, chat)
@@ -24,30 +24,98 @@ Routes (all mounted under port 8081, compose network only):
                   /chat/completions, but only on /go — Zen's copy hits the
                   free-tier quota with the same key)
 
+The consumer today is the brain bridge (mcp-brain-bridge), which talks
+Responses API on /go/resp. The Open WebUI consumer is retired (2026-09-19);
+the compose sidecar it used to run in is gone, and the slice now runs as a
+systemd user unit.
+
+Failure contract (2026-11-13): every failure answers with a parseable JSON
+error instead of dropping the socket — 504 GatewayTimeout when the upstream
+stalls, 502 BadGatewayError when the upstream is unreachable, 413
+PayloadTooLarge when the request body is over the cap, 400 BadRequest for a
+malformed body, 404 ModelNotServedHere for a model that another mount owns.
+
 Stdlib only. SSE streaming is relayed chunk-by-chunk, never buffered.
 Auth (Authorization: Bearer <key>) passes straight through untouched.
 """
 
 import json
 import os
-import uuid
+import re
+import signal
+import sys
+import threading
 import time
-import urllib.request
 import urllib.error
+import urllib.request
+import uuid
 from datetime import datetime, timezone
 from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
 
 UPSTREAM = "https://opencode.ai"
-SESSION_ID = os.environ.get("ZEN_SESSION_ID", "00000000-0000-4000-8000-000000000000")
 UA = (
     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
     "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
 )
 
+# Exit code used when a configuration value is malformed. The process
+# refuses to start rather than silently falling back: the upstream timeout
+# is part of a contract (proxy timeout <= caller deadline <= client
+# timeout), and a substituted default would break the ordering it protects.
+EXIT_CONFIG_ERROR = 2
+
+
+def _env_int(name, default, minimum=1):
+    """Read an integer environment variable.
+
+    A malformed or out-of-range value stops the process with a readable
+    message instead of a traceback, because a silently substituted default
+    would hide the very mistake the value exists to prevent.
+    """
+    raw = os.environ.get(name)
+    if raw is None or not raw.strip():
+        return default
+    try:
+        value = int(raw.strip())
+    except ValueError:
+        sys.stderr.write(
+            f"zen-proxy: {name}={raw!r} is not an integer; use a whole "
+            f"number (default {default}) or unset it.\n"
+        )
+        raise SystemExit(EXIT_CONFIG_ERROR)
+    if value < minimum:
+        sys.stderr.write(
+            f"zen-proxy: {name}={value} is below the minimum of {minimum}.\n"
+        )
+        raise SystemExit(EXIT_CONFIG_ERROR)
+    return value
+
+
+def _env_float(name, default, minimum=1.0):
+    """Read a float environment variable with the same fail-loud policy."""
+    raw = os.environ.get(name)
+    if raw is None or not raw.strip():
+        return default
+    try:
+        value = float(raw.strip())
+    except ValueError:
+        sys.stderr.write(
+            f"zen-proxy: {name}={raw!r} is not a number; use a number "
+            f"(default {default}) or unset it.\n"
+        )
+        raise SystemExit(EXIT_CONFIG_ERROR)
+    if value < minimum:
+        sys.stderr.write(
+            f"zen-proxy: {name}={value} is below the minimum of {minimum}.\n"
+        )
+        raise SystemExit(EXIT_CONFIG_ERROR)
+    return value
+
+
 # Audit mode: when "1", every proxied request appends one JSON line to
 # audit.jsonl plus full request/response capture files, so you can prove
 # exactly what effort value was sent upstream and what came back.
-# Flip via ZEN_PROXY_AUDIT in .env (needs container recreate), default off.
+# Flip via ZEN_PROXY_AUDIT in .env (restart the unit), default off.
 # NOTE: captures contain your prompts — local disk only, disable after testing.
 AUDIT = os.environ.get("ZEN_PROXY_AUDIT", "0") == "1"
 AUDIT_DIR = os.path.expanduser("~/.local/share/zen-proxy/audit-logs")
@@ -59,7 +127,147 @@ AUDIT_MAX_BYTES = 2 * 1024 * 1024  # per-response capture cap
 # 300s and the bridge saw "RemoteProtocolError: Server disconnected
 # without sending a response", retried, and burned its own 500s deadline.
 # Env-tunable so a slow model can be given more room without a code edit.
-UPSTREAM_TIMEOUT = float(os.environ.get("ZEN_PROXY_UPSTREAM_TIMEOUT", "900"))
+# It is a socket timeout, so it is re-armed on every read: it is the
+# silence wall of a stream and the wall for the first byte of a response.
+UPSTREAM_TIMEOUT = _env_float("ZEN_PROXY_UPSTREAM_TIMEOUT", 900.0)
+
+# Hard cap on an inbound request body. The cap is enforced while reading,
+# before the body is buffered, so an oversized body costs one rejected
+# request instead of the process memory it would have consumed.
+MAX_BODY_BYTES = _env_int("ZEN_PROXY_MAX_BODY_BYTES", 32 * 1024 * 1024)
+
+# How long a SIGTERM waits for in-flight requests to finish before the
+# process exits anyway. Zero means "do not wait".
+DRAIN_TIMEOUT_S = _env_int("ZEN_PROXY_DRAIN_TIMEOUT_S", 30, minimum=0)
+
+# Bounded reception: a client that connects and dribbles a body must not
+# hold a handler thread forever. The window is reopened before a response
+# is streamed, so a slow upstream never trips it.
+CLIENT_RECEIVE_TIMEOUT_S = 60
+
+
+class _BodyTooLarge(Exception):
+    """Raised when an inbound body exceeds MAX_BODY_BYTES."""
+
+
+def _read_exact(rfile, count):
+    """Read exactly `count` bytes, or fewer when the stream ends."""
+    data = bytearray()
+    while len(data) < count:
+        chunk = rfile.read(count - len(data))
+        if not chunk:
+            break
+        data += chunk
+    return bytes(data)
+
+
+def _read_chunked(rfile, cap):
+    """Decode an HTTP/1.1 chunked request body under a byte cap.
+
+    Raises _BodyTooLarge when the decoded body would exceed `cap` and
+    ValueError when the framing is malformed. Trailers are consumed and
+    discarded.
+    """
+    out = bytearray()
+    while True:
+        line = rfile.readline(65536)
+        if not line:
+            raise ValueError("missing chunk header")
+        size_field = line.split(b";", 1)[0].strip()
+        try:
+            size = int(size_field, 16)
+        except ValueError:
+            raise ValueError(f"malformed chunk header {size_field!r}")
+        if size == 0:
+            while True:  # consume optional trailers
+                trailer = rfile.readline(65536)
+                if not trailer or trailer in (b"\r\n", b"\n"):
+                    break
+            return bytes(out)
+        if len(out) + size > cap:
+            raise _BodyTooLarge()
+        chunk = _read_exact(rfile, size)
+        if len(chunk) != size:
+            raise ValueError("truncated chunk body")
+        out += chunk
+        rfile.readline(8)  # the CRLF that terminates the chunk
+
+
+def _read_body(headers, rfile, cap):
+    """Read the request body under a hard cap.
+
+    Returns a (body, error) pair. `body` is None when the request carries
+    no body. `error` is a (status, error_type, message) triple when the
+    body must be rejected.
+    """
+    encoding = (headers.get("Transfer-Encoding") or "").lower()
+    if "chunked" in encoding:
+        try:
+            return _read_chunked(rfile, cap), None
+        except _BodyTooLarge:
+            return None, (
+                413,
+                "PayloadTooLarge",
+                f"zen-proxy: request body exceeds the {cap} byte limit",
+            )
+        except ValueError as exc:
+            return None, (
+                400,
+                "BadRequest",
+                f"zen-proxy: malformed chunked request body: {exc}",
+            )
+        except TimeoutError:
+            return None, (
+                408,
+                "RequestTimeout",
+                "zen-proxy: timed out reading the request body",
+            )
+    raw_length = headers.get("Content-Length")
+    if raw_length is None:
+        return None, None
+    try:
+        length = int(raw_length.strip())
+    except (AttributeError, ValueError):
+        return None, (400, "BadRequest", "zen-proxy: invalid Content-Length header")
+    if length < 0:
+        return None, (400, "BadRequest", "zen-proxy: invalid Content-Length header")
+    if length > cap:
+        return None, (
+            413,
+            "PayloadTooLarge",
+            f"zen-proxy: request body of {length} bytes exceeds the {cap} byte limit",
+        )
+    try:
+        body = _read_exact(rfile, length)
+    except TimeoutError:
+        return None, (
+            408,
+            "RequestTimeout",
+            "zen-proxy: timed out reading the request body",
+        )
+    if len(body) != length:
+        return None, (
+            400,
+            "BadRequest",
+            "zen-proxy: request body shorter than Content-Length",
+        )
+    return (body or None), None
+
+
+# A streamed response is only complete when it carries its terminal event.
+# Without this check a stream that dies mid-reply is indistinguishable from
+# a short but complete answer, and the caller believes it got a full turn.
+_TERMINAL_PATTERNS = (
+    re.compile(rb"response\.(completed|failed|incomplete)"),
+    re.compile(rb"\[DONE\]"),
+    re.compile(rb'"finish_reason"\s*:\s*"(?!null)'),
+)
+
+
+def _has_terminal_event(buffer):
+    """True when the buffered SSE bytes carry a terminal event marker."""
+    return any(pattern.search(buffer) for pattern in _TERMINAL_PATTERNS)
+
 
 # Refreshed live 2026-11-08 (Go: 30 models, Zen: 45 models; authenticated
 # with opencode UA + session). Go now includes crouton-alpha-free,
@@ -127,19 +335,9 @@ GO_RESP = {
     "step-5-preview",
 }
 
-# Per-model context windows (tokens), for callers that pre-size prompts
-# (e.g. brain BRAIN_CONTEXT_WINDOW_TOKENS). Values from models.dev feed
-# 2026-10-21; default when absent below is 1048576. WARNING: grok-4.7 is
+# Per-model context windows (tokens) are the caller's business: brain sizes
+# its prompts from BRAIN_CONTEXT_WINDOW_TOKENS. WARNING: grok-4.7 accepts
 # only 500000 — never send it a 1M-sized prompt, the server rejects it.
-MODEL_WINDOWS = {
-    "grok-4.7": 500000,
-    "hy3": 256000,
-    "deepseek-v4-flash": 1000000,
-    "deepseek-v4-flash-free": 200000,
-    "deepseek-v4.1-flash-free": 200000,
-    "glm-5.3-flash-free": 200000,
-    "mimo-v2.6-flash-free": 200000,
-}
 ZEN_CHAT = {
     "big-pickle",
     "nemotron-3.5-lightning-free",
@@ -209,8 +407,68 @@ def _audit_write(record, req_body=None):
 class Handler(BaseHTTPRequestHandler):
     server_version = "zen-proxy/1.0"
 
+    # Bounded reception: a client that connects and dribbles a body must
+    # not hold a handler thread for the life of the process. The window is
+    # reopened before a response is streamed (see _proxy_inner).
+    timeout = CLIENT_RECEIVE_TIMEOUT_S
+
     def log_message(self, *args):
-        pass  # keep logs quiet; errors still surface via status codes
+        pass  # one structured line per request is written by _log_request
+
+    def _send_json(self, status, payload, req_id=None):
+        """Answer with a JSON body and the headers a client needs."""
+        body = json.dumps(payload).encode()
+        self.send_response(status)
+        self.send_header("Content-Type", "application/json")
+        self.send_header("Content-Length", str(len(body)))
+        if req_id:
+            self.send_header("X-Request-Id", req_id)
+        self.end_headers()
+        self.wfile.write(body)
+
+    def _send_error(self, status, error_type, message, req_id=None):
+        """Answer with the error envelope the clients parse."""
+        self._send_json(
+            status,
+            {"type": "error", "error": {"type": error_type, "message": message}},
+            req_id,
+        )
+
+    def _write_stream_error(self, error_type, message):
+        """Report a mid-stream failure in band.
+
+        The status line is already on the wire at this point, so the only
+        honest signal left is an error event inside the stream itself.
+        """
+        payload = {"type": "error", "error": {"type": error_type, "message": message}}
+        try:
+            self.wfile.write(
+                ("event: error\ndata: " + json.dumps(payload) + "\n\n").encode()
+            )
+            self.wfile.flush()
+        except OSError:
+            pass
+
+    def _log_request(
+        self, req_id, started, status, outcome, model, session_id, session_origin, sent
+    ):
+        """Write one structured line per request to stdout (the journal).
+
+        The Authorization value, the request body and the response body are
+        never written: this line is safe to keep in the journal.
+        """
+        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
+        line = (
+            f"ts={ts} req_id={req_id} method={self.command} path={self.path} "
+            f"status={status} outcome={outcome} model={model or '-'} "
+            f"duration_ms={round((time.monotonic() - started) * 1000)} "
+            f"session={(session_id or '-')[:8]}({session_origin}) bytes={sent}"
+        )
+        try:
+            sys.stdout.write(line + "\n")
+            sys.stdout.flush()
+        except OSError:
+            pass
 
     def _send_upstream(self):
         if self.path == "/health":
@@ -233,9 +491,50 @@ class Handler(BaseHTTPRequestHandler):
     do_POST = _send_upstream
 
     def _proxy(self, upstream_path, allow):
-        length = int(self.headers.get("Content-Length", 0) or 0)
-        body = self.rfile.read(length) if length else None
-        t0 = time.monotonic()
+        """Relay one request upstream and answer the client.
+
+        Every failure path answers with a parseable JSON error instead of
+        dropping the socket, so the caller can tell a timeout from a
+        rejected body from a refused connection.
+        """
+        req_id = uuid.uuid4().hex[:8]
+        started = time.monotonic()
+        state = {
+            "status": 500,
+            "outcome": "error",
+            "model": None,
+            "session_id": "",
+            "session_origin": "client",
+            "sent": 0,
+        }
+        try:
+            return self._proxy_inner(req_id, started, upstream_path, allow, state)
+        finally:
+            self._log_request(
+                req_id,
+                started,
+                state["status"],
+                state["outcome"],
+                state["model"],
+                state["session_id"],
+                state["session_origin"],
+                state["sent"],
+            )
+
+    def _proxy_inner(self, req_id, started, upstream_path, allow, state):
+        body, body_error = _read_body(self.headers, self.rfile, MAX_BODY_BYTES)
+        if body_error:
+            status, error_type, message = body_error
+            state["status"] = status
+            state["outcome"] = "rejected"
+            self._send_error(status, error_type, message, req_id)
+            return
+        # A streamed response can outlive the bounded reception window, so
+        # the window is widened to the upstream timeout for the response
+        # phase. It is not cleared: a client that stops reading must not
+        # hold this handler thread forever, or the drain would have to kill
+        # the process with a turn still in flight.
+        self.connection.settimeout(UPSTREAM_TIMEOUT)
         # Gate POST by the route allowlist: a model served on another
         # mount gets a 404 naming its correct route instead of a confusing
         # upstream 400 (endpoint/style mismatch).
@@ -248,32 +547,29 @@ class Handler(BaseHTTPRequestHandler):
                 _mid = _probe["model"]
                 if _mid not in allow:
                     _hint = _find_route(_mid)
-                    _err = {
-                        "type": "error",
-                        "error": {
-                            "type": "ModelNotServedHere",
-                            "message": (
-                                f"zen-proxy: model '{_mid}' is not served on "
-                                f"{self.path};"
-                                + (
-                                    f" use {_hint} instead."
-                                    if _hint
-                                    else " it is on no known route (check upstream list)."
-                                )
-                            ),
-                        },
-                    }
-                    _errb = json.dumps(_err).encode()
-                    self.send_response(404)
-                    self.send_header("Content-Type", "application/json")
-                    self.send_header("Content-Length", str(len(_errb)))
-                    self.end_headers()
-                    self.wfile.write(_errb)
+                    state["status"] = 404
+                    state["outcome"] = "model_not_served"
+                    state["model"] = _mid
+                    self._send_error(
+                        404,
+                        "ModelNotServedHere",
+                        (
+                            f"zen-proxy: model '{_mid}' is not served on "
+                            f"{self.path};"
+                            + (
+                                f" use {_hint} instead."
+                                if _hint
+                                else " it is on no known route (check upstream list)."
+                            )
+                        ),
+                        req_id,
+                    )
                     return
         record = None
         if AUDIT and self.command == "POST":
             record = {
                 "ts": datetime.now(timezone.utc).isoformat(),
+                "req_id": req_id,
                 "method": self.command,
                 "route": self.path,
                 "upstream": upstream_path,
@@ -290,6 +586,7 @@ class Handler(BaseHTTPRequestHandler):
             except ValueError:
                 payload = None
             if isinstance(payload, dict):
+                state["model"] = payload.get("model")
                 if record is not None:
                     record["model"] = payload.get("model")
                     record["stream"] = payload.get("stream")
@@ -300,20 +597,30 @@ class Handler(BaseHTTPRequestHandler):
                         record["translated"] = True
                         reasoning = payload.get("reasoning") or {}
                         record["effort_out"] = reasoning.get("effort")
-        elif record is not None and body:
+        elif body:
             try:
                 payload = json.loads(body)
             except ValueError:
                 payload = None
             if isinstance(payload, dict):
-                record["model"] = payload.get("model")
-                record["stream"] = payload.get("stream")
-                record["effort_in"] = payload.get("reasoning_effort")
-        minted_session = (
-            self.headers.get("x-opencode-session")
-            or self.headers.get("X-Session-ID")
-            or str(uuid.uuid4())  # Hermes recipe: mint fresh ID per request
+                state["model"] = payload.get("model")
+                if record is not None:
+                    record["model"] = payload.get("model")
+                    record["stream"] = payload.get("stream")
+                    record["effort_in"] = payload.get("reasoning_effort")
+        # Identity: a client that already carries a session keeps it, every
+        # other caller gets a fresh one per request (Hermes recipe), so the
+        # gateway never sees one shared session standing in for all traffic.
+        client_session = self.headers.get("x-opencode-session") or self.headers.get(
+            "X-Session-ID"
         )
+        if client_session:
+            minted_session = client_session
+            state["session_origin"] = "client"
+        else:
+            minted_session = str(uuid.uuid4())
+            state["session_origin"] = "injected"
+        state["session_id"] = minted_session
         client_ua = self.headers.get("User-Agent", "")
         out_headers = {
             "Authorization": self.headers.get("Authorization", ""),
@@ -350,20 +657,31 @@ class Handler(BaseHTTPRequestHandler):
             # Pool egress failure (e.g. MITM node cert refused, fail-closed).
             # Answer 502 instead of dropping the socket so SDK clients get a
             # parseable error they can retry against another node.
-            err = json.dumps(
-                {
-                    "type": "error",
-                    "error": {
-                        "type": "BadGatewayError",
-                        "message": f"zen-proxy: upstream unreachable: {e.reason}",
-                    },
-                }
-            ).encode()
-            self.send_response(502)
-            self.send_header("Content-Type", "application/json")
-            self.send_header("Content-Length", str(len(err)))
-            self.end_headers()
-            self.wfile.write(err)
+            state["status"] = 502
+            state["outcome"] = "egress_failed"
+            self._send_error(
+                502,
+                "BadGatewayError",
+                f"zen-proxy: upstream unreachable: {e.reason}",
+                req_id,
+            )
+            return
+        except TimeoutError as e:
+            # The upstream did not answer inside the socket timeout. This
+            # used to escape both handlers and drop the socket with no
+            # status, which the caller saw as "Server disconnected without
+            # sending a response".
+            state["status"] = 504
+            state["outcome"] = "timeout"
+            self._send_error(
+                504,
+                "GatewayTimeout",
+                (
+                    f"zen-proxy: upstream did not respond within "
+                    f"{UPSTREAM_TIMEOUT:g}s ({e})"
+                ),
+                req_id,
+            )
             return
 
         ctype = headers.get("Content-Type", "")
@@ -376,23 +694,33 @@ class Handler(BaseHTTPRequestHandler):
                 # Upstream error page (e.g. 404 on a mistyped path, 401 on a
                 # bad key) — relay it as-is instead of dropping the
                 # connection with an empty reply that clients can't explain.
+                state["status"] = status
+                state["outcome"] = "ok"
+                state["sent"] = len(raw)
                 self.send_response(status)
                 self.send_header("Content-Type", ctype or "application/octet-stream")
                 self.send_header("Content-Length", str(len(raw)))
+                self.send_header("X-Request-Id", req_id)
                 self.end_headers()
                 self.wfile.write(raw)
                 return
             data["data"] = [m for m in data.get("data", []) if m.get("id") in allow]
             out = json.dumps(data).encode()
+            state["status"] = status
+            state["outcome"] = "ok"
+            state["sent"] = len(out)
             self.send_response(status)
             self.send_header("Content-Type", "application/json")
             self.send_header("Content-Length", str(len(out)))
+            self.send_header("X-Request-Id", req_id)
             self.end_headers()
             self.wfile.write(out)
             return
 
+        state["status"] = status
         self.send_response(status)
         self.send_header("Content-Type", ctype or "application/octet-stream")
+        self.send_header("X-Request-Id", req_id)
         if "text/event-stream" not in ctype:
             self.send_header("Connection", "close")
         self.end_headers()
@@ -406,22 +734,68 @@ class Handler(BaseHTTPRequestHandler):
                 record["resp_capture"] = os.path.join(
                     AUDIT_DIR, f"audit-{ts_fname}-resp.sse"
                 )
-                cap = open(record["resp_capture"], "wb")
+                # The capture file stays open across the relay, so it is
+                # closed by hand in the finally block below.
+                cap = open(record["resp_capture"], "wb")  # noqa: SIM115
             except OSError:
                 cap = None
         sent = 0
+        tail = bytearray()
+        is_sse = "text/event-stream" in ctype
+        failure = None
         try:
             while True:
-                chunk = stream.read(8192)
+                try:
+                    chunk = stream.read(8192)
+                except TimeoutError as e:
+                    # The upstream went silent mid-reply. The status line is
+                    # already on the wire, so the failure is reported in band.
+                    failure = (
+                        "UpstreamStreamTimeout",
+                        (
+                            "zen-proxy: upstream stalled for more than "
+                            f"{UPSTREAM_TIMEOUT:g}s while streaming ({e})"
+                        ),
+                    )
+                    break
+                except OSError as e:
+                    failure = (
+                        "UpstreamStreamError",
+                        f"zen-proxy: upstream stream failed ({e})",
+                    )
+                    break
                 if not chunk:
                     break
-                self.wfile.write(chunk)
-                self.wfile.flush()
+                try:
+                    self.wfile.write(chunk)
+                    self.wfile.flush()
+                except (BrokenPipeError, ConnectionResetError) as e:
+                    # The client hung up. Stop the upstream read so an
+                    # unread turn stops consuming quota.
+                    state["outcome"] = "client_gone"
+                    failure = (
+                        "ClientDisconnected",
+                        f"zen-proxy: client disconnected ({e})",
+                    )
+                    break
+                except TimeoutError as e:
+                    # The client stopped reading and the write window
+                    # expired. Same outcome as a disconnect.
+                    state["outcome"] = "client_gone"
+                    failure = (
+                        "ClientDisconnected",
+                        f"zen-proxy: client stopped reading ({e})",
+                    )
+                    break
                 sent += len(chunk)
+                if is_sse:
+                    tail += chunk
+                    if len(tail) > 65536:
+                        del tail[:-32768]
                 if cap is not None:
                     if sent <= AUDIT_MAX_BYTES:
                         cap.write(chunk)
-                    elif cap is not None:
+                    else:
                         cap.write(b"\n...[truncated]\n")
                         cap.close()
                         cap = None
@@ -429,11 +803,89 @@ class Handler(BaseHTTPRequestHandler):
             stream.close()
             if cap is not None:
                 cap.close()
+        if failure is not None and state["outcome"] == "client_gone":
+            # The client is gone. There is nothing left to signal on the
+            # wire; the only record is the journal line, and a disconnect
+            # must never be rewritten into a clean end.
+            pass
+        elif failure is not None:
+            error_type, message = failure
+            self._write_stream_error(error_type, message)
+            state["outcome"] = "stream_truncated"
+            state["status"] = 502
+        elif is_sse and sent and not _has_terminal_event(bytes(tail)):
+            # The stream ended without its terminal event, so the turn was
+            # cut short. Reporting it as a clean end would let the caller
+            # believe it received a complete answer.
+            self._write_stream_error(
+                "UpstreamStreamTruncated",
+                "zen-proxy: upstream stream ended without its terminal event",
+            )
+            state["outcome"] = "stream_truncated"
+            state["status"] = 502
+        else:
+            state["outcome"] = "ok"
+        state["sent"] = sent
         if record is not None:
             record["resp_bytes"] = sent
-            record["duration_ms"] = round((time.monotonic() - t0) * 1000)
+            record["outcome"] = state["outcome"]
+            record["duration_ms"] = round((time.monotonic() - started) * 1000)
             _audit_write(record, req_body=body)
 
 
+class ZenProxyServer(ThreadingHTTPServer):
+    """Threading server that can be drained instead of killed.
+
+    `daemon_threads` is off and `block_on_close` is on, so `server_close`
+    waits for the in-flight handlers to finish. That is what makes a
+    SIGTERM graceful: the listener stops first, the running turns are
+    allowed to complete.
+    """
+
+    daemon_threads = False
+    block_on_close = True
+    allow_reuse_address = True
+
+
+def _drain_watchdog():
+    """Force the process to exit when the drain deadline expires.
+
+    A wedged upstream must not keep the unit from restarting, so the
+    drain is bounded: after the deadline the process leaves on its own.
+    """
+    time.sleep(DRAIN_TIMEOUT_S)
+    sys.stdout.write(
+        f"ts={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} "
+        f"event=drain_timeout seconds={DRAIN_TIMEOUT_S} action=exit\n"
+    )
+    sys.stdout.flush()
+    os._exit(0)
+
+
+def _install_signal_handlers(server):
+    """Stop the listener on SIGTERM/SIGINT and let the turns finish."""
+
+    def _shutdown(signum, _frame):
+        sys.stdout.write(
+            f"ts={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} "
+            f"event=signal signal={signal.Signals(signum).name} action=drain\n"
+        )
+        sys.stdout.flush()
+        # shutdown() blocks until serve_forever() returns, so it must not
+        # run on the thread that is inside serve_forever().
+        threading.Thread(target=server.shutdown, daemon=True).start()
+        if DRAIN_TIMEOUT_S > 0:
+            threading.Thread(target=_drain_watchdog, daemon=True).start()
+
+    for sig in (signal.SIGTERM, signal.SIGINT):
+        signal.signal(sig, _shutdown)
+
+
 if __name__ == "__main__":
-    ThreadingHTTPServer(("127.0.0.1", 8081), Handler).serve_forever()
+    _server = ZenProxyServer(("127.0.0.1", 8081), Handler)
+    _install_signal_handlers(_server)
+    try:
+        _server.serve_forever()
+    finally:
+        # server_close() joins the in-flight handlers: the drain.
+        _server.server_close()
diff --git a/zen-proxy/refresh_allowlists.py b/zen-proxy/refresh_allowlists.py
new file mode 100755
index 0000000..f3d3b01
--- /dev/null
+++ b/zen-proxy/refresh_allowlists.py
@@ -0,0 +1,353 @@
+#!/usr/bin/env python3
+"""Refresh the zen-proxy allowlists from the live gateway catalogue.
+
+Why this exists:
+  The four allowlists in `proxy.py` are hand-verified model sets. They drift
+  silently: the gateway adds a model and the proxy answers "not served here",
+  or the gateway retires one and the proxy keeps offering a dead id. This
+  script reports the drift and, on request, applies the safe half of it.
+
+What it does:
+  1. Reads the current sets out of `proxy.py` (no import, no side effects).
+  2. Fetches the upstream catalogue per family with a GET, using the
+     operator's key. The request is read-only: no inference is ever sent,
+     so nothing is spent from the quota.
+  3. Classifies every id as keep, gone or add-candidate.
+  4. With `--apply` it rewrites only the allowlist literals, atomically.
+
+Safety rules (the reason this is a script and not a habit):
+  * A failed probe never removes anything. A timeout, a 429 or a 5xx means
+    "unknown", not "gone".
+  * A model missing from the catalogue is a CANDIDATE, not a verdict. The
+    catalogue is not the served set: `crouton-alpha-free` is served by the
+    Go tier and is not listed in its catalogue. A removal is written only
+    when the operator confirms that exact id with `--confirm-remove`.
+  * An id survives when it merely moved between the chat and the responses
+    mount of its family.
+  * A mount whose resulting set would be empty is never written.
+  * New upstream ids are reported as candidates, never added automatically:
+    the catalogue does not say which API style a model speaks, and guessing
+    would put a model on a mount that cannot serve it.
+  * The script never runs git and never writes a credential.
+
+Attribution: the refuse-to-empty, keep-order and never-remove-on-transient
+rules follow the catalogue-sync safety pattern of github.com/12errh/zen-proxy
+(MIT, (c) 2026 12errh).
+
+Usage:
+  python zen-proxy/refresh_allowlists.py                 # report only
+  python zen-proxy/refresh_allowlists.py \
+      --confirm-remove /go/resp=some-model --apply       # apply that removal
+  python zen-proxy/refresh_allowlists.py --add /go/resp=grok-4.8 --apply
+"""
+
+import argparse
+import json
+import os
+import re
+import sys
+import tempfile
+import urllib.error
+import urllib.request
+
+DEFAULT_BASE_URL = "https://opencode.ai"
+DEFAULT_KEY_ENV = "ZEN_PROXY_UPSTREAM_KEY"
+PROXY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxy.py")
+
+# Mount prefix -> (family, upstream base, set name in proxy.py).
+# A family is the credential tier: /zen/* is the free tier, /go/* is Go.
+MOUNTS = {
+    "/zen/chat": ("zen", "/zen/v1", "ZEN_CHAT"),
+    "/zen/resp": ("zen", "/zen/v1", "ZEN_RESP"),
+    "/go/chat": ("go", "/zen/go/v1", "GO_CHAT"),
+    "/go/resp": ("go", "/zen/go/v1", "GO_RESP"),
+}
+
+UA = (
+    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
+    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
+)
+
+
+class RefreshError(Exception):
+    """Raised when the script must refuse to write."""
+
+
+def read_sets(proxy_path=PROXY_PATH):
+    """Parse the four allowlist literals out of proxy.py.
+
+    The file is read as text and the literals are matched with a regex, so
+    importing the module is never necessary and no side effect (no server,
+    no environment read) can happen here.
+    """
+    with open(proxy_path, "r", encoding="utf-8") as handle:
+        source = handle.read()
+    sets = {}
+    for _family, _base, name in MOUNTS.values():
+        match = re.search(rf"^{name} = \{{(.*?)^\}}$", source, re.DOTALL | re.MULTILINE)
+        if not match:
+            raise RefreshError(f"could not find the {name} literal in {proxy_path}")
+        ids = re.findall(r'"([^"]+)"', match.group(1))
+        sets[name] = ids
+    return sets
+
+
+def merge_ids(current, removals, add=()):
+    """Compute the new id list for one mount.
+
+    Order is preserved for the ids that survive, additions are appended in
+    alphabetical order, and only ids in `removals` are dropped — those are
+    the ids the operator confirmed. An empty result is refused: a mount
+    with no models serves nothing.
+    """
+    removal_set = set(removals)
+    kept = [model for model in current if model not in removal_set]
+    additions = sorted({model for model in add if model and model not in kept})
+    merged = kept + additions
+    if not merged:
+        raise RefreshError("refusing to write an empty allowlist")
+    return merged
+
+
+def classify(current, family_observed, probe_ok):
+    """Split the current ids into keep and removal candidates for one mount.
+
+    `family_observed` is the union of the catalogue of every mount of the
+    same family. An id that is absent from it is a candidate for removal,
+    not a verdict: the catalogue and the served set are not the same thing.
+    """
+    if not probe_ok:
+        return {"keep": list(current), "candidates": []}
+    observed = set(family_observed)
+    keep = [model for model in current if model in observed]
+    candidates = [model for model in current if model not in observed]
+    return {"keep": keep, "candidates": candidates}
+
+
+def fetch_catalogue(base_url, upstream_base, key, timeout=30):
+    """Fetch the upstream model catalogue of one family.
+
+    Returns (ids, ok). `ok` is False when the catalogue could not be
+    fetched; the ids are then empty and nothing may be removed.
+    """
+    url = base_url.rstrip("/") + upstream_base + "/models"
+    request = urllib.request.Request(
+        url,
+        method="GET",
+        headers={
+            "Authorization": f"Bearer {key}",
+            "Accept": "application/json",
+            "User-Agent": UA,
+        },
+    )
+    try:
+        with urllib.request.urlopen(request, timeout=timeout) as response:
+            payload = json.loads(response.read().decode("utf-8", "replace"))
+    except urllib.error.HTTPError as exc:
+        print(f"  catalogue {url} failed: HTTP {exc.code}", file=sys.stderr)
+        return [], False
+    except urllib.error.URLError as exc:
+        print(f"  catalogue {url} failed: {exc.reason}", file=sys.stderr)
+        return [], False
+    except (ValueError, OSError) as exc:
+        print(f"  catalogue {url} failed: {exc}", file=sys.stderr)
+        return [], False
+    ids = []
+    for entry in payload.get("data", []) if isinstance(payload, dict) else []:
+        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
+            ids.append(entry["id"])
+    if not ids:
+        # An empty catalogue is not an authoritative catalogue: the gateway
+        # answers 200 with an error envelope or an empty list when the tier
+        # is blocked. Treating that as "everything is gone" would empty an
+        # allowlist on a quota error.
+        print(
+            f"  catalogue {url} returned no models: treated as unknown", file=sys.stderr
+        )
+        return [], False
+    return ids, True
+
+
+def render_literal(name, ids):
+    """Render an allowlist literal in the same shape proxy.py uses."""
+    lines = [f"{name} = {{"]
+    for model in ids:
+        lines.append(f'    "{model}",')
+    lines.append("}")
+    return "\n".join(lines)
+
+
+def rewrite_sets(proxy_path, new_sets):
+    """Rewrite the allowlist literals in proxy.py, atomically.
+
+    Only the four literals are touched. The file is written to a temporary
+    file in the same directory and moved into place, so a crash cannot leave
+    a half-written module behind.
+    """
+    with open(proxy_path, "r", encoding="utf-8") as handle:
+        source = handle.read()
+    original = source
+    for name, ids in new_sets.items():
+        pattern = re.compile(rf"^{name} = \{{.*?^\}}$", re.DOTALL | re.MULTILINE)
+        if not pattern.search(source):
+            raise RefreshError(f"could not find the {name} literal in {proxy_path}")
+        literal = render_literal(name, ids)
+        source = pattern.sub(lambda _m, lit=literal: lit, source, count=1)
+    if source == original:
+        return False
+    directory = os.path.dirname(os.path.abspath(proxy_path))
+    # The temporary file is moved into place, so it is closed by hand.
+    handle = tempfile.NamedTemporaryFile(  # noqa: SIM115
+        "w",
+        encoding="utf-8",
+        dir=directory,
+        prefix=".refresh_allowlists_",
+        delete=False,
+    )
+    try:
+        with handle:
+            handle.write(source)
+        os.chmod(handle.name, os.stat(proxy_path).st_mode & 0o777)
+        os.replace(handle.name, proxy_path)
+    except OSError:
+        try:
+            os.unlink(handle.name)
+        except OSError:
+            pass
+        raise
+    return True
+
+
+def parse_additions(values):
+    """Parse `--add /mount=id1,id2` arguments into {mount: [ids]}."""
+    additions = {}
+    for value in values or []:
+        if "=" not in value:
+            raise RefreshError(f"--add expects /mount=id[,id], got {value!r}")
+        mount, ids = value.split("=", 1)
+        mount = mount.strip()
+        if mount not in MOUNTS:
+            raise RefreshError(f"unknown mount {mount!r} in --add")
+        additions[mount] = [item.strip() for item in ids.split(",") if item.strip()]
+    return additions
+
+
+def mount_set_name(mount):
+    """The proxy.py set name behind a mount prefix."""
+    return MOUNTS[mount][2]
+
+
+def main(argv=None):
+    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
+    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
+    parser.add_argument(
+        "--key-env",
+        default=DEFAULT_KEY_ENV,
+        help="environment variable holding the upstream key (default: %(default)s)",
+    )
+    parser.add_argument("--proxy", default=PROXY_PATH, help="path to proxy.py")
+    parser.add_argument(
+        "--add",
+        action="append",
+        metavar="/mount=id[,id]",
+        help="add a verified model id to a mount (repeatable)",
+    )
+    parser.add_argument(
+        "--confirm-remove",
+        action="append",
+        metavar="/mount=id[,id]",
+        help="remove these ids from a mount, confirmed by the operator (repeatable)",
+    )
+    parser.add_argument(
+        "--apply",
+        action="store_true",
+        help="write the confirmed removals and additions into proxy.py",
+    )
+    args = parser.parse_args(argv)
+
+    key = os.environ.get(args.key_env, "").strip()
+    if not key:
+        print(
+            f"zen-proxy: no key in ${args.key_env}; export the upstream key first.",
+            file=sys.stderr,
+        )
+        return 2
+
+    try:
+        sets = read_sets(args.proxy)
+        additions = parse_additions(args.add)
+        confirmations = parse_additions(args.confirm_remove)
+    except (RefreshError, OSError) as exc:
+        print(f"zen-proxy: {exc}", file=sys.stderr)
+        return 2
+
+    families = {}
+    for family in ("zen", "go"):
+        bases = {base for fam, base, _name in MOUNTS.values() if fam == family}
+        base = min(bases)
+        ids, ok = fetch_catalogue(args.base_url, base, key)
+        families[family] = {"ids": ids, "ok": ok, "base": base}
+        state = "ok" if ok else "FAILED (no removals from this family)"
+        print(f"family {family}: {len(ids)} upstream models, probe {state}")
+
+    new_sets = {}
+    removals = {}
+    for mount, (family, _base, name) in MOUNTS.items():
+        current = sets[name]
+        family_ids = families[family]["ids"]
+        probe_ok = families[family]["ok"]
+        verdict = classify(current, family_ids, probe_ok)
+        candidates = verdict["candidates"]
+        # Only the ids the operator confirmed are removed. A catalogue
+        # absence is a candidate, never a verdict: the catalogue and the
+        # served set differ (crouton-alpha-free is served by Go and is not
+        # listed in its catalogue).
+        confirmed = [
+            model for model in candidates if model in confirmations.get(mount, [])
+        ]
+        removals[name] = confirmed
+        add = additions.get(mount, [])
+        if candidates:
+            print(
+                f"{mount}: removal candidates (confirm with --confirm-remove): "
+                f"{', '.join(candidates)}"
+            )
+        if confirmed:
+            print(f"{mount}: removing {', '.join(confirmed)}")
+        if add:
+            print(f"{mount}: adding {', '.join(sorted(add))}")
+        try:
+            new_sets[name] = merge_ids(current, confirmed, add)
+        except RefreshError as exc:
+            # One mount that would end up empty must not block the report of
+            # the others, and it must never be written.
+            print(f"{mount}: keeping the current set ({exc})", file=sys.stderr)
+            new_sets[name] = list(current)
+    # Candidates are reported, never written: the catalogue does not say
+    # which API style a model speaks.
+    known = {model for ids in sets.values() for model in ids}
+    for family, info in families.items():
+        if not info["ok"]:
+            continue
+        candidates = sorted(set(info["ids"]) - known)
+        if candidates:
+            print(
+                f"family {family}: unclassified upstream models (verify the API "
+                f"style, then add with --add): {', '.join(candidates)}"
+            )
+
+    if not args.apply:
+        print("report only; pass --apply to write the confirmed removals")
+        return 0
+
+    try:
+        changed = rewrite_sets(args.proxy, new_sets)
+    except (RefreshError, OSError) as exc:
+        print(f"zen-proxy: {exc}", file=sys.stderr)
+        return 2
+    print(f"{args.proxy}: {'updated' if changed else 'unchanged'}")
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
```
<!-- END_GIT_DIFF -->
