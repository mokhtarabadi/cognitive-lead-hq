# Task 400: Harden the zen-proxy runtime and add observability

**File:** `tasks/completed/400-harden-zen-proxy-runtime-and-observability.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Started:** 2026-11-13T19:12:17Z
**Finished:** 2026-11-13T19:12:17Z
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

### Closure (2026-11-13)

The Manager issued the exact closure word `Close task` in answer to the
closure-approval question. Preconditions verified before the turn: the file was
in `tasks/qa/`, the Execution Log recorded `PO_REVIEW_PENDING`, the Brain QA seat
had returned `QA_PASSED` (2026-11-13T19:04:21Z, `gen-1794596655`), the Brain Code
Reviewer had returned `APPROVED` (2026-11-13T19:05:08Z, `gen-1794596693`), and
the QA queue held 2 tasks, under the cap of 3.

The file moved from `tasks/qa/` to `tasks/completed/` via `git mv`, the status
became `closed`, and the `**File:**` header was updated to the new path. The
atomic closure commit `custom_context_commit_and_clean_task` returned feature
commit `ca71093884cc98fba61185fde89be29a4173a1ec` and created the closure commit
`chore: close task 400 - harden zen proxy runtime and observability`
(`569dc32`) on top. The `## Factual Git Diff` block was replaced by the commit
reference, and the working tree is clean.

Planner lead-time stamps: `sync_task_times` is not exposed in this planner
build, so the stamp sync was skipped. The `**Started:**`, `**Submitted:**` and
`**Finished:**` fields are therefore absent from this task file; they are written
by the lane transitions themselves when the planner server provides the tool.

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
**Factual Git Diff:** Stored in Commit Hash: `50a5b64c4c4ad3239c3971c4ee1305edf59b5ad2`
<!-- END_GIT_DIFF -->
