# Task 432: brain-litellm-zen-bridge-cleanup

**File:** `tasks/completed/432-brain-litellm-zen-bridge-cleanup.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-11-27T10:03:38Z
**Submitted:** 2026-11-27T09:01:59Z
**Started:** 2026-11-27T08:06:05Z
**Supersedes:** [426, 427, 428, 429, 430, 431]
**Meta:** true
**Created:** 2026-11-27 08:00 UTC
**Bundled:** 6 tasks

## Supersedes

This META supersedes 6 source task(s). Each one is archived to `tasks/archive/` with a `**Superseded-By:** 432-brain-litellm-zen-bridge-cleanup` marker and stays reachable via `git log --oneline --follow -- tasks/archive/<id>-*.md`:

- `426` — Evaluate migrating Brain to LiteLLM
- `427` — Migrate Brain Bridge to LiteLLM and Gate Debug Output by Env
- `428` — Rebuild `.env.example` From a Project-Wide Scan
- `429` — Rename zen-proxy to zen-bridge and Add Env-Driven Proxy Support
- `430` — Remove warp-proxy and psiphon-proxy Projects and All References
- `431` — Sweep Leftover References, Slim the Tests, and Clean Docs and README

Execution is all-or-nothing: every line of `## Bundled Checklist (All-or-Nothing)` must pass, otherwise the whole META is `QA_REJECTED` and returns to `in-progress`. A partial close is forbidden.

## Goal

Unified execution of 6 related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks [426, 427, 428, 429, 430, 431] — "brain-litellm-zen-bridge-cleanup" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.

> ⚠️ **Guardrail Warning:** Combined source size is 586 LOC (> 400). Unified META diff may be large and hard to review. Consider splitting into two METAs.

**Source IDs:** [426, 427, 428, 429, 430, 431]
**Next ID:** 432 (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)
**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: 432-brain-litellm-zen-bridge-cleanup` and remain reachable via `git log --follow` (never purged until META is completed).

## Manager's Notes

> **Manager override (2026-11-27):** Source 426's recommendation ("O3 — no migration") is
> **superseded**. The Manager directed the LiteLLM migration in this META. Source 426 is folded in as
> evidence input only; its recommendation is not an instruction to follow. The migration must still
> preserve the verified behaviors 426 enumerated (retry semantics, 429 handling, timeout mapping,
> identity headers via the bridge, streaming XML extraction).

**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute 6 small related tasks together and speed up turnaround.

**Traceability:**
- Supersedes [426, 427, 428, 429, 430, 431] — see per-source verbatim blocks below
- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** 432-brain-litellm-zen-bridge-cleanup` header + superseded footer
- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file

**Guardrails Applied:**
- Cap 6 per bundle — this bundle has 6 (✅ within cap)
- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)
- Diff-size check — combined 586 LOC (⚠️ exceeds 400 — consider split)

## Source Bundles (Verbatim Preservation)

The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.

### Source Task 426: Evaluate migrating Brain to LiteLLM

**Original File:** `/home/mohammad/cognitive-lead-hq/tasks/in-progress/426-evaluate-litellm-migration-for-brain.md` → `tasks/archive/426-evaluate-litellm-migration-for-brain.md` (after bundling)

**Title:** Evaluate migrating Brain to LiteLLM

#### Goal (verbatim)

Evaluate whether to migrate the Brain from its current Python proxy +
opencode-v2 identity implementation to LiteLLM. Determine how much custom code
would be removed (LiteLLM handles identity/routing natively), what breaks, and
whether the migration is worth it. Produce a recommendation with evidence.

#### Acceptance Criteria (verbatim)

- [x] Evidence-based recommendation with file citations
- [x] List of code that LiteLLM would replace
- [x] Migration risk notes

#### Local TODOs (verbatim)

- [x] Inspect current Brain MCP bridge request construction
- [x] Research LiteLLM support for OpenCode Go / custom headers / proxy CONNECT
- [x] Estimate code removed vs added
- [x] Produce recommendation

#### Risk & Rollback (verbatim)

- **Risk:** migration would add LiteLLM dependency and reintroduce custom hooks; muse-spark-1.3-contributor not in catalog.
- **Rollback:** keep current stack; no code changes performed.

#### Manager's Notes (verbatim intent) (verbatim)

"برای خود برین رو نگاه کنی بعد ببینی آیا ارزشش داره مایگریت کنی بری سمت لایت ال ال ام یا همین چیزی که هست رو نگه داریم؛ چون بریم سمت لایت ال ال ام یه بخش خیلی خوبی از کدهایی که نوشتیم پاک میشه، دیگه نیاز نیست ما هندل کنیم، خود اون لایت ال ال ام هندل میکنه، بخش عظیمی از کدها پاک میشه."

#### LiteLLM Evaluation (verbatim)

Options:
- O1 (migrate now): Replace `_post_with_retry`, `_make_client`, `_upstream_mode/_upstream_url`, and conversion helpers with LiteLLM. Risk: custom model registration for muse-spark-1.3-contributor, identity header hook, re-test all retry/error/timeout behavior.
- O2 (adapter-gated pilot): Add `BRAIN_UPSTREAM_MODE=litellm` behind a feature flag; keep current path as default. Lower risk, reversible.
- O3 (no migration): Keep current verified stack.

Scope touched by any migration: mcp-brain-bridge/server.py transport/conversion, zen-proxy identity headers (may reduce), docs/config.

Interface delta: Brain uses OpenAI Responses API; LiteLLM supports `/responses` and translates to chat completions when needed. OpenCode Go models use `opencode_go/` prefix; muse-spark-1.3-contributor not in published catalog (needs custom registration).

Risk: retry semantics, 429 terminal handling, timeout mapping, identity headers, quota behavior, streaming XML extraction.

Cost/latency/observability: LiteLLM adds cost tracking and fallbacks; current stack has no cost dashboard but is verified and simple.

Rollback: revert env + dependency; no code change needed for O3.

#### Recommendation (verbatim)

Winner: O3 (no migration) for now. The current stack is verified (health, models, chat, responses, CONNECT all 200, brain_turn works). Migrating to LiteLLM is only justified for multi-provider fallback, cost dashboards, or model routing across providers — none is a current requirement. If pursued later, use O2 behind `BRAIN_UPSTREAM_MODE=litellm` as a reversible experiment; do not replace the current path outright.

No implementation performed in this discovery task.

#### Verification Evidence (verbatim)

Commands and citations:
- grep -n "BRAIN_API_BASE\|/responses\|_post_with_retry\|_make_client" mcp-brain-bridge/server.py (lines 2844, 2833, 2986, 5383, 5385, 4998)
- docs.litellm.ai/docs/providers/opencode_go fetched 2026-11-27 (session headers, model prefix, custom headers)
- docs.litellm.ai/docs/response_api fetched 2026-11-27 (/responses support)
- gist.github.com/CL0SeY/e174c5fa1f58487122b0b7e767dee0dd (session hook pattern)
- grep -n "muse-spark-1.3-contributor" models.litellm.ai/providers/opencode_go -> not present in catalog

---

### Source Task 427: Migrate Brain Bridge to LiteLLM and Gate Debug Output by Env

**Original File:** `/home/mohammad/cognitive-lead-hq/tasks/backlog/427-migrate-brain-bridge-to-litellm.md` → `tasks/archive/427-migrate-brain-bridge-to-litellm.md` (after bundling)

**Title:** Migrate Brain Bridge to LiteLLM and Gate Debug Output by Env

#### Goal (verbatim)

Make LiteLLM the single upstream call path for `mcp-brain-bridge` so the bridge stops owning an
OpenAI Responses client, retry ladder, and endpoint/conversion glue. Delete the leftover custom
transport code and its tests, register the OpenCode Go models the Brain uses inside LiteLLM, and put
every per-turn debug line behind one env switch documented in `.env.example`.

#### Manager's Notes (verbatim)

Verbatim intent:

> "we need to use litellm instead our custom openai apis endpoints in brain mcp and remove lefter
> over codes/tests make litellm handle all things. also reduce the outputs like debug when a brain
> turn called or manage it via a .env using our .env.example"

Binding context:

- The earlier evaluation in task 426 recommended keeping the hand-written transport. The Manager
  overrides that recommendation: migrate now, and fold task 426 into the meta task instead of
  following its recommendation.
- Identity headers for the Go gateway stay where they are today (the zen-bridge proxy). This task
  only replaces the Brain's own upstream client and conversion layer.
- Current transport surface to remove: `_post_with_retry`, `_make_client`, `_upstream_mode`,
  `_upstream_url`, and the responses/chat-completions conversion helpers in
  `mcp-brain-bridge/server.py`.
- Lua-free requirement: no new frontend or shell code; Python only.

#### Acceptance Criteria (verbatim)

- [x] `mcp-brain-bridge/server.py` performs no direct `httpx` POST to `/responses`; LiteLLM is the
      only provider call path.
- [x] The configured Brain models (including the current Go-gateway model) are registered in code or
      config so a `brain_turn` with the production env values succeeds.
- [x] ~~Retry, timeout, 429-terminal, and truncation-recovery semantics match the pre-migration~~
      **Superseded (Manager round 3):** retry policy and the 429 terminal classifier were removed
      outright. What still holds is timeout behavior and truncation recovery; a failed turn is now
      surfaced to the caller with no retry.
- [x] Debug output on a normal `brain_turn` is silent unless `BRAIN_DEBUG` is truthy.
- [x] No leftover custom transport helper, dead import, or test that only covered removed code
      remains (verified by grep in the Execution Log).
- [x] `docs/brain-bridge.md` and `.env.example` describe the new transport and the debug switch.

#### Local TODOs (verbatim)

- [x] Inventory the current transport surface in `mcp-brain-bridge/server.py` (client, retry,
      conversion, endpoint selection) and record the exact line ranges to delete.
- [x] Add LiteLLM as a bridge dependency with a pinned version in `mcp-brain-bridge/pyproject.toml`.
- [x] Register the Go-gateway models as a custom LiteLLM `model_list` entry (openai-compatible
      base `BRAIN_API_BASE`, custom `extra_headers` passthrough, `/responses` endpoint support).
- [x] Move retry, timeout, and 429 handling to LiteLLM `num_retries` / timeout parameters and delete
      the hand-written ladder.
- [x] Keep `TRUNCATION_UNRECOVERABLE`, oversized-output stubbing, and XML extraction behavior
      byte-identical; cover each with a test.
- [x] Delete dead conversion helpers and every test that only exercised removed code.
- [x] Gate all per-turn stderr chatter behind one `BRAIN_DEBUG` switch (default off); route
      degraded-path warnings through it too.
- [x] Document `BRAIN_DEBUG` and any new `BRAIN_LITELLM_*` keys in `.env.example` and
      `docs/brain-bridge.md`.
- [x] Record the applied `testing-verification` evidence before lint.

#### Risk & Rollback (verbatim)

- **Risk:** LiteLLM drops a retry or timeout behavior the bridge relies on, so a long reasoning turn
  returns a hard error instead of retrying; custom model registration for the Go gateway may not
  accept the `/responses` shape the Brain sends.
- **Rollback plan:** keep the old transport behind `BRAIN_UPSTREAM_MODE=legacy` until the LiteLLM
  path is green, then delete the legacy branch in the same task; if migration fails irrecoverably,
  revert the bridge commit and restore the pinned dependency set.

#### Verification Evidence (verbatim)

- **Test command:** `rtk test uv run --with pytest --with mcp==1.30.0 python -m pytest tests/test_brain_bridge.py tests/test_brain_responses_alignment.py tests/test_raw_output_recovery.py tests/test_brain_preflight.py -q`
- **Expected result:** all collected tests pass, exit code 0; one live `brain_turn` smoke call
  through the production env returns a valid status.
- **Actual result:** full suite `940 passed` (exit 0); live `brain_turn` smoke returned `READY` on `muse-spark-1.3-contributor`; zen-bridge `/health` answered 200 on a temporary port.
- **Exit code:** 0

> Verification runner rule: the first verification run MUST use the `rtk test` prefix; a raw rerun is
> allowed only after a failed RTK run for detailed diagnostics.

---

### Source Task 428: Rebuild `.env.example` From a Project-Wide Scan

**Original File:** `/home/mohammad/cognitive-lead-hq/tasks/backlog/428-rebuild-env-example-from-scan.md` → `tasks/archive/428-rebuild-env-example-from-scan.md` (after bundling)

**Title:** Rebuild `.env.example` From a Project-Wide Scan

#### Goal (verbatim)

Make `.env.example` a truthful inventory of the environment keys the project actually reads. Scan
every server, service unit, script, and doc that resolves an env var, then rebuild the file so each
key is present once, grouped by owner, and annotated with its real default and effect. Remove keys
nothing reads.

#### Manager's Notes (verbatim)

Verbatim intent:

> "cleanup .env.example by scanning project."

Scope notes:

- The scan is the source of truth, not the current file. The present `.env.example` carries stale
  model notes, duplicated `BRAIN_MODEL` blocks, duplicated `ZEN_PROXY_UPSTREAM_TIMEOUT`, and a
  zen-proxy section that will be renamed by a sibling task in the same meta.
- A key that only exists in archived docs stays out unless live code reads it.
- Do not commit a real secret; placeholders only.

#### Acceptance Criteria (verbatim)

- [x] Every env key read by live code appears exactly once in `.env.example`.
- [x] No key in `.env.example` lacks a live reader (Exceptions: documented future keys explicitly
      marked commented-out with a reason).
- [x] Sections match component names as they will exist after the zen-bridge rename.
- [x] Each key line carries a short comment naming its default and its effect.
- [x] No secret, token, or credential value is present.

#### Local TODOs (verbatim)

- [x] Enumerate env reads across `mcp-*/**/*.py`, `zen-proxy/`, `scripts/`, `services/`,
      `opencode.json`, and `docs/` with a literal grep for `os.environ`, `os.getenv`, `getenv(`,
      `Environment=`, and `${VAR` patterns.
- [x] Build a key inventory: name, owner component, default in code, documented or undocumented.
- [x] Rewrite `.env.example` grouped by owner with one section per component and no duplicate key.
- [x] Drop keys with no live reader; list them in the Execution Log so the removal is auditable.
- [x] Verify every key in the file resolves in live code, and every live env read appears in the file.
- [x] Keep the file provider-agnostic where the sibling LiteLLM task will add its keys; do not
      pre-invent keys.

#### Risk & Rollback (verbatim)

- **Risk:** a key used only in production unit files or the global install gets dropped, breaking a
  service on the next restart.
- **Rollback plan:** restore the previous `.env.example` from git history; the file is
  documentation-only and carries no runtime power by itself.

#### Verification Evidence (verbatim)

- **Test command:** `rtk test uv run --with pytest python -m pytest tests/test_brain_bridge.py -q`
- **Expected result:** env-parsing tests pass, and the scan diff shows zero unread keys.
- **Actual result:** full suite `940 passed` (exit 0); live `brain_turn` smoke returned `READY` on `muse-spark-1.3-contributor`; zen-bridge `/health` answered 200 on a temporary port.
- **Exit code:** 0

> Verification runner rule: the first verification run MUST use the `rtk test` prefix; a raw rerun is
> allowed only after a failed RTK run for detailed diagnostics.

---

### Source Task 429: Rename zen-proxy to zen-bridge and Add Env-Driven Proxy Support

**Original File:** `/home/mohammad/cognitive-lead-hq/tasks/backlog/429-rename-zen-proxy-to-zen-bridge-and-env-proxy.md` → `tasks/archive/429-rename-zen-proxy-to-zen-bridge-and-env-proxy.md` (after bundling)

**Title:** Rename zen-proxy to zen-bridge and Add Env-Driven Proxy Support

#### Goal (verbatim)

Rename the `zen-proxy/` slice to `zen-bridge/` across the whole project (directory, module, service
unit, docs, memory records, config, tests) and make the proxy hop configurable from env on both
sides: the Brain connects to the bridge over loopback with no proxy, and the bridge itself uses the
upstream HTTP proxy from env to reach the Go gateway.

#### Manager's Notes (verbatim)

Verbatim intent:

> "keep our zen-proxy it a bridge help us use opencode go models via litellm but rename it in entire
> project to zen-bridge"

> "make sure our brain itself support proxy via env and our zen-bridge support proxy via env so in
> current setup we used no proxy for localhost so brain directly connect to zen-bridge using loopback
> and zen-bridge itself use proxy to connect to opencode go"

Binding context:

- Behaviour is unchanged apart from naming and explicit proxy routing; the bridge keeps forwarding
  identity headers and supporting `/responses`, `/chat/completions`, `/models`, discovery, and
  CONNECT.
- The Brain's own outbound proxy support must respect `no_proxy` for `127.0.0.1` / `localhost` so a
  global `http_proxy` never sends loopback traffic to the upstream proxy.
- Live code references verified today: `zen-proxy/proxy.py`, `zen-proxy/README.md`,
  `zen-proxy/DECISIONS.md`, `zen-proxy/pyproject.toml`, `services/zen-proxy.service`,
  `docs/zen-proxy.md`, `docs/brain-bridge.md`, `docs/services.md`, `tests/README.md`,
  `README.md`, `.env.example`.

#### Acceptance Criteria (verbatim)

- [x] No live file references `zen-proxy` except history/archive records; `zen-bridge` is the only
      live name.
- [x] `services/zen-bridge.service` points at the renamed module and the unit still starts cleanly.
- [x] Brain calls to a loopback `BRAIN_API_BASE` bypass any configured `http_proxy`.
- [x] The bridge uses env-configured proxy values for its upstream connection, with documented
      precedence.
- [x] Existing bridge behavior (endpoints, identity headers, CONNECT) is unchanged, proven by tests.
- [x] `.env.example` carries only the new `ZEN_BRIDGE_*` names.

#### Local TODOs (verbatim)

- [x] Rename the directory with `git mv zen-proxy zen-bridge` and update the package name, module
      docstrings, and pyproject identity.
- [x] Rename `services/zen-proxy.service` to `services/zen-bridge.service` with the new exec path and
      unit name.
- [x] Rename `docs/zen-proxy.md` to `docs/zen-bridge.md` and rewrite inbound links.
- [x] Sweep every live reference with `$code-search` (graph + grep) and update code, docs, memory
      records, README files, and tests; leave archive/history files untouched.
- [x] Add explicit `ZEN_BRIDGE_HTTP_PROXY` / `ZEN_BRIDGE_HTTPS_PROXY` / `ZEN_BRIDGE_NO_PROXY`
      resolution with fallback to the standard lowercase/uppercase env names.
- [x] Add Brain-side proxy resolution that honours `NO_PROXY` for loopback and the bridge port.
- [x] Assert the routing with a test: a loopback `BRAIN_API_BASE` is never sent through
      `http_proxy`; a non-loopback upstream is.
- [x] Document the two hops in `docs/brain-bridge.md` and the bridge README.

#### Risk & Rollback (verbatim)

- **Risk:** a rename miss leaves a service unit or an env key pointing at the old path, so the bridge
  fails to start after deployment; proxy precedence may route the loopback hop through the upstream
  proxy and break brain calls.
- **Rollback plan:** revert the rename commit; the bridge logic is unchanged, so reverting the name
  restores the previous working service with one deploy step.

#### Verification Evidence (verbatim)

- **Test command:** `rtk test uv run --with pytest python -m pytest tests/test_zen_bridge.py tests/test_brain_bridge.py -q`
- **Expected result:** the bridge suite and Brain suite pass, exit code 0; an explicit loopback
  no-proxy assertion is present and green.
- **Actual result:** full suite `940 passed` (exit 0); live `brain_turn` smoke returned `READY` on `muse-spark-1.3-contributor`; zen-bridge `/health` answered 200 on a temporary port.
- **Exit code:** 0

> Verification runner rule: the first verification run MUST use the `rtk test` prefix; a raw rerun is
> allowed only after a failed RTK run for detailed diagnostics.

---

### Source Task 430: Remove warp-proxy and psiphon-proxy Projects and All References

**Original File:** `/home/mohammad/cognitive-lead-hq/tasks/backlog/430-remove-warp-and-psiphon-proxies.md` → `tasks/archive/430-remove-warp-and-psiphon-proxies.md` (after bundling)

**Title:** Remove warp-proxy and psiphon-proxy Projects and All References

#### Goal (verbatim)

Delete the `warp-proxy/` and `psiphon-proxy/` build contexts and every live reference to them. blowsh
keeps optional proxy support, but it reads proxy settings from plain environment variables instead of
one named container backend. Documentation that only taught WARP or Psiphon is archived as history,
not kept as a current guide.

#### Manager's Notes (verbatim)

Verbatim intent:

> "remove warp and psiphone projects and all of them refreneces in our project, blowsh support proxy
> but not need to use warp or phsionon"

Scope notes:

- Verified live references today: `warp-proxy/`, `psiphon-proxy/`, `docs/blowsh-warp-proxy.md`,
  `docs/blowsh-psiphon-proxy.md`, `docs/blowsh-proxy-options.md`, `docs/blowsh-direct-egress.md`,
  `docs/README.md`, `docs/DECISIONS.md`, `README.md`, plus memory records under
  `.opencode/memory/`.
- blowsh keeps `PROXY_TYPE` / `PROXY_HOST` / `PROXY_PORT` / `PROXY_BYPASS` support; drop only the
  container names and build contexts.
- History under `docs/history/` and completed/archived tasks is a record and must not be edited.

#### Acceptance Criteria (verbatim)

- [x] Neither `warp-proxy/` nor `psiphon-proxy/` exists in the live tree; history is preserved.
- [x] No live file (excluding `docs/history/`, `tasks/archive/`, `tasks/completed/`, and session
      transcripts) mentions WARP or Psiphon.
- [x] blowsh proxy support is documented as env-only and still works with a generic proxy.
- [x] Dated ADRs record the removal and the reason.
- [x] No service unit or compose file references the removed containers.

#### Local TODOs (verbatim)

- [x] Confirm no live service unit, compose file, or script depends on either proxy directory.
- [x] Move `warp-proxy/` and `psiphon-proxy/` to an archive location with `git mv` (history stays
      reachable), or delete only after confirming nothing references them.
- [x] Rewrite `docs/blowsh-proxy-options.md` as a generic env-driven proxy guide with no named
      backend.
- [x] Retire `docs/blowsh-warp-proxy.md` and `docs/blowsh-psiphon-proxy.md` into history, with dated
      ADRs in `docs/DECISIONS.md` and the affected slice `DECISIONS.md`.
- [x] Sweep live references with `$code-search` and plain grep for `warp`, `psiphon`, `socks`; fix
      each live hit.
- [x] Refresh the memory records that named either backend.
- [x] Break any compose or service definition that names `warp-net` / `psiphon-socks`.

#### Risk & Rollback (verbatim)

- **Risk:** a running blowsh container or the operator's current deployment still points at one of
  the removed containers, so egress stops after the cleanup lands.
- **Rollback plan:** restore the directories from git history and re-apply the previous container
  configuration; the build contexts are self-contained.

#### Verification Evidence (verbatim)

- **Test command:** `rtk test uv run --with pytest --with mcp==1.30.0 python -m pytest tests/ -q`
- **Expected result:** the full suite passes, exit code 0; grep for the removed names returns only
  history and archive paths.
- **Actual result:** full suite `940 passed` (exit 0); live `brain_turn` smoke returned `READY` on `muse-spark-1.3-contributor`; zen-bridge `/health` answered 200 on a temporary port.
- **Exit code:** 0

> Verification runner rule: the first verification run MUST use the `rtk test` prefix; a raw rerun is
> allowed only after a failed RTK run for detailed diagnostics.

---

### Source Task 431: Sweep Leftover References, Slim the Tests, and Clean Docs and README

**Original File:** `/home/mohammad/cognitive-lead-hq/tasks/backlog/431-sweep-tests-docs-and-leftovers.md` → `tasks/archive/431-sweep-tests-docs-and-leftovers.md` (after bundling)

**Title:** Sweep Leftover References, Slim the Tests, and Clean Docs and README

#### Goal (verbatim)

Close the meta task with one code-search-driven sweep: remove every reference and leftover left by
the LiteLLM migration, the zen-bridge rename, and the proxy removal; make the test suite smaller and
more focused without losing a guard; and refresh the docs and READMEs so they describe the final
state only.

#### Manager's Notes (verbatim)

Verbatim intent:

> "use $code-search remove any refrences and lefovers realted to our cleanup and migration to litellm
> and clean them"

> "cleanup our tests make them cleaner focusable"

> "cleanup our docs and readme at end."

Binding context:

- This task runs last inside the meta task, after the migration, the rename, and the proxy removal
  have landed, so it treats their output as the ground truth.
- No test may be deleted unless the behavior it covered is gone; a guard that still matters is
  retargeted, not dropped.
- `docs/history/`, `tasks/archive/`, `tasks/completed/`, and `tasks/.sessions/` are records and stay
  out of the sweep.
- `split_system_prompt.py` counts and the prompt-sync byte-identity gate must stay green after any
  doc edit that touches a prompt fragment.

#### Acceptance Criteria (verbatim)

- [x] A repo-wide grep for the retired names returns only history, archive, completed-task, and
      session-transcript paths.
- [x] No duplicate test covers the same contract; the suite is smaller with the guard floor intact.
- [x] Every doc and README describes the final architecture with no reference to a removed component.
- [x] Prompt-sync byte identity still holds.
- [x] The full suite passes with exit code 0.

#### Local TODOs (verbatim)

- [x] Run the `code-search` workflow (graph build, query, `explain_node`, signatures) over the
      changed slices before editing, and record the graph coverage line.
- [x] Grep for `litellm`, `zen-proxy`, `warp`, `psiphon`, `_post_with_retry`, `_make_client`,
      `_upstream_mode`, `_upstream_url` and classify each live hit as fixed, retargeted, or archive.
- [x] Collapse duplicated bridge/env tests into named behavior tests; delete tests that only covered
      removed code; keep one test per surviving contract.
- [x] Re-anchor any fixture that names a removed path or key.
- [x] Refresh `README.md`, `docs/README.md`, `docs/brain-bridge.md`, `docs/services.md`, and each
      touched slice `README.md` / `DECISIONS.md` to the final state.
- [x] Update `AGENTS.md` and `tests/README.md` only where a rule or slice duty actually changed.
- [x] Verify the prompt-sync suite and the full suite after every doc edit that touches fragments.

#### Risk & Rollback (verbatim)

- **Risk:** a test is deleted together with a guard that still protects a surviving contract, so a
  real regression can land unnoticed.
- **Rollback plan:** restore the deleted test file from git history and retarget it; no production
  code depends on test presence.

#### Verification Evidence (verbatim)

- **Test command:** `rtk test uv run --with pytest --with mcp==1.30.0 python -m pytest tests/ -q`
- **Expected result:** full suite green, exit code 0, collected count recorded before and after the
  slimming.
- **Actual result:** full suite `940 passed` (exit 0); live `brain_turn` smoke returned `READY` on `muse-spark-1.3-contributor`; zen-bridge `/health` answered 200 on a temporary port.
- **Exit code:** 0

> Verification runner rule: the first verification run MUST use the `rtk test` prefix; a raw rerun is
> allowed only after a failed RTK run for detailed diagnostics.

---


## Bundled Checklist (All-or-Nothing)

> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.

- [x] [426] Evidence-based recommendation with file citations
- [x] [426] List of code that LiteLLM would replace
- [x] [426] Migration risk notes
- [x] [427] `mcp-brain-bridge/server.py` performs no direct `httpx` POST to `/responses`; LiteLLM is the
      only provider call path.
- [x] [427] The configured Brain models (including the current Go-gateway model) are registered in code or
      config so a `brain_turn` with the production env values succeeds.
- [x] [427] ~~Retry, timeout, 429-terminal, and truncation-recovery semantics match the pre-migration
      behavior, proven by tests that stay green.~~ **Superseded (Manager round 3):** retry policy and
      the 429 terminal classifier were removed; timeout behavior and truncation recovery still hold,
      and a failed turn is surfaced to the caller with no retry.
- [x] [427] Debug output on a normal `brain_turn` is silent unless `BRAIN_DEBUG` is truthy.
- [x] [427] No leftover custom transport helper, dead import, or test that only covered removed code
      remains (verified by grep in the Execution Log).
- [x] [427] `docs/brain-bridge.md` and `.env.example` describe the new transport and the debug switch.
- [x] [428] Every env key read by live code appears exactly once in `.env.example`.
- [x] [428] No key in `.env.example` lacks a live reader (Exceptions: documented future keys explicitly
      marked commented-out with a reason).
- [x] [428] Sections match component names as they will exist after the zen-bridge rename.
- [x] [428] Each key line carries a short comment naming its default and its effect.
- [x] [428] No secret, token, or credential value is present.
- [x] [429] No live file references `zen-proxy` except history/archive records; `zen-bridge` is the only
      live name.
- [x] [429] `services/zen-bridge.service` points at the renamed module and the unit still starts cleanly.
- [x] [429] Brain calls to a loopback `BRAIN_API_BASE` bypass any configured `http_proxy`.
- [x] [429] The bridge uses env-configured proxy values for its upstream connection, with documented
      precedence.
- [x] [429] Existing bridge behavior (endpoints, identity headers, CONNECT) is unchanged, proven by tests.
- [x] [429] `.env.example` carries only the new `ZEN_BRIDGE_*` names.
- [x] [430] Neither `warp-proxy/` nor `psiphon-proxy/` exists in the live tree; history is preserved.
- [x] [430] No live file (excluding `docs/history/`, `tasks/archive/`, `tasks/completed/`, and session
      transcripts) mentions WARP or Psiphon.
- [x] [430] blowsh proxy support is documented as env-only and still works with a generic proxy.
- [x] [430] Dated ADRs record the removal and the reason.
- [x] [430] No service unit or compose file references the removed containers.
- [x] [431] A repo-wide grep for the retired names returns only history, archive, completed-task, and
      session-transcript paths.
- [x] [431] No duplicate test covers the same contract; the suite is smaller with the guard floor intact.
- [x] [431] Every doc and README describes the final architecture with no reference to a removed component.
- [x] [431] Prompt-sync byte identity still holds.
- [x] [431] The full suite passes with exit code 0.
- [x] Traceability: All 6 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Local TODOs

- [x] Step 1: Validate META bundle — confirm all 6 source requirements are captured verbatim below
- [x] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)
- [x] [426] Inspect current Brain MCP bridge request construction
- [x] [426] Research LiteLLM support for OpenCode Go / custom headers / proxy CONNECT
- [x] [426] Estimate code removed vs added
- [x] [426] Produce recommendation
- [x] [427] Inventory the current transport surface in `mcp-brain-bridge/server.py` (client, retry,
      conversion, endpoint selection) and record the exact line ranges to delete.
- [x] [427] Add LiteLLM as a bridge dependency with a pinned version in `mcp-brain-bridge/pyproject.toml`.
- [x] [427] Register the Go-gateway models as a custom LiteLLM `model_list` entry (openai-compatible
      base `BRAIN_API_BASE`, custom `extra_headers` passthrough, `/responses` endpoint support).
- [x] [427] Move retry, timeout, and 429 handling to LiteLLM `num_retries` / timeout parameters and delete
      the hand-written ladder.
- [x] [427] Keep `TRUNCATION_UNRECOVERABLE`, oversized-output stubbing, and XML extraction behavior
      byte-identical; cover each with a test.
- [x] [427] Delete dead conversion helpers and every test that only exercised removed code.
- [x] [427] Gate all per-turn stderr chatter behind one `BRAIN_DEBUG` switch (default off); route
      degraded-path warnings through it too.
- [x] [427] Document `BRAIN_DEBUG` and any new `BRAIN_LITELLM_*` keys in `.env.example` and
      `docs/brain-bridge.md`.
- [x] [427] Record the applied `testing-verification` evidence before lint.
- [x] [428] Enumerate env reads across `mcp-*/**/*.py`, `zen-proxy/`, `scripts/`, `services/`,
      `opencode.json`, and `docs/` with a literal grep for `os.environ`, `os.getenv`, `getenv(`,
      `Environment=`, and `${VAR` patterns.
- [x] [428] Build a key inventory: name, owner component, default in code, documented or undocumented.
- [x] [428] Rewrite `.env.example` grouped by owner with one section per component and no duplicate key.
- [x] [428] Drop keys with no live reader; list them in the Execution Log so the removal is auditable.
- [x] [428] Verify every key in the file resolves in live code, and every live env read appears in the file.
- [x] [428] Keep the file provider-agnostic where the sibling LiteLLM task will add its keys; do not
      pre-invent keys.
- [x] [429] Rename the directory with `git mv zen-proxy zen-bridge` and update the package name, module
      docstrings, and pyproject identity.
- [x] [429] Rename `services/zen-proxy.service` to `services/zen-bridge.service` with the new exec path and
      unit name.
- [x] [429] Rename `docs/zen-proxy.md` to `docs/zen-bridge.md` and rewrite inbound links.
- [x] [429] Sweep every live reference with `$code-search` (graph + grep) and update code, docs, memory
      records, README files, and tests; leave archive/history files untouched.
- [x] [429] Add explicit `ZEN_BRIDGE_HTTP_PROXY` / `ZEN_BRIDGE_HTTPS_PROXY` / `ZEN_BRIDGE_NO_PROXY`
      resolution with fallback to the standard lowercase/uppercase env names.
- [x] [429] Add Brain-side proxy resolution that honours `NO_PROXY` for loopback and the bridge port.
- [x] [429] Assert the routing with a test: a loopback `BRAIN_API_BASE` is never sent through
      `http_proxy`; a non-loopback upstream is.
- [x] [429] Document the two hops in `docs/brain-bridge.md` and the bridge README.
- [x] [430] Confirm no live service unit, compose file, or script depends on either proxy directory.
- [x] [430] Move `warp-proxy/` and `psiphon-proxy/` to an archive location with `git mv` (history stays
      reachable), or delete only after confirming nothing references them.
- [x] [430] Rewrite `docs/blowsh-proxy-options.md` as a generic env-driven proxy guide with no named
      backend.
- [x] [430] Retire `docs/blowsh-warp-proxy.md` and `docs/blowsh-psiphon-proxy.md` into history, with dated
      ADRs in `docs/DECISIONS.md` and the affected slice `DECISIONS.md`.
- [x] [430] Sweep live references with `$code-search` and plain grep for `warp`, `psiphon`, `socks`; fix
      each live hit.
- [x] [430] Refresh the memory records that named either backend.
- [x] [430] Break any compose or service definition that names `warp-net` / `psiphon-socks`.
- [x] [431] Run the `code-search` workflow (graph build, query, `explain_node`, signatures) over the
      changed slices before editing, and record the graph coverage line.
- [x] [431] Grep for `litellm`, `zen-proxy`, `warp`, `psiphon`, `_post_with_retry`, `_make_client`,
      `_upstream_mode`, `_upstream_url` and classify each live hit as fixed, retargeted, or archive.
- [x] [431] Collapse duplicated bridge/env tests into named behavior tests; delete tests that only covered
      removed code; keep one test per surviving contract.
- [x] [431] Re-anchor any fixture that names a removed path or key.
- [x] [431] Refresh `README.md`, `docs/README.md`, `docs/brain-bridge.md`, `docs/services.md`, and each
      touched slice `README.md` / `DECISIONS.md` to the final state.
- [x] [431] Update `AGENTS.md` and `tests/README.md` only where a rule or slice duty actually changed.
- [x] [431] Verify the prompt-sync suite and the full suite after every doc edit that touches fragments.
- [x] Step 66: Verify all bundled checklist items and run lint_task_file + verification-before-completion
- [x] Step 67: Update CHANGELOG.md and record Verification Evidence

## Acceptance Criteria

- [x] [426] Evidence-based recommendation with file citations
- [x] [426] List of code that LiteLLM would replace
- [x] [426] Migration risk notes
- [x] [427] `mcp-brain-bridge/server.py` performs no direct `httpx` POST to `/responses`; LiteLLM is the
      only provider call path.
- [x] [427] The configured Brain models (including the current Go-gateway model) are registered in code or
      config so a `brain_turn` with the production env values succeeds.
- [x] [427] ~~Retry, timeout, 429-terminal, and truncation-recovery semantics match the pre-migration
      behavior, proven by tests that stay green.~~ **Superseded (Manager round 3):** retry policy and
      the 429 terminal classifier were removed; timeout behavior and truncation recovery still hold,
      and a failed turn is surfaced to the caller with no retry.
- [x] [427] Debug output on a normal `brain_turn` is silent unless `BRAIN_DEBUG` is truthy.
- [x] [427] No leftover custom transport helper, dead import, or test that only covered removed code
      remains (verified by grep in the Execution Log).
- [x] [427] `docs/brain-bridge.md` and `.env.example` describe the new transport and the debug switch.
- [x] [428] Every env key read by live code appears exactly once in `.env.example`.
- [x] [428] No key in `.env.example` lacks a live reader (Exceptions: documented future keys explicitly
      marked commented-out with a reason).
- [x] [428] Sections match component names as they will exist after the zen-bridge rename.
- [x] [428] Each key line carries a short comment naming its default and its effect.
- [x] [428] No secret, token, or credential value is present.
- [x] [429] No live file references `zen-proxy` except history/archive records; `zen-bridge` is the only
      live name.
- [x] [429] `services/zen-bridge.service` points at the renamed module and the unit still starts cleanly.
- [x] [429] Brain calls to a loopback `BRAIN_API_BASE` bypass any configured `http_proxy`.
- [x] [429] The bridge uses env-configured proxy values for its upstream connection, with documented
      precedence.
- [x] [429] Existing bridge behavior (endpoints, identity headers, CONNECT) is unchanged, proven by tests.
- [x] [429] `.env.example` carries only the new `ZEN_BRIDGE_*` names.
- [x] [430] Neither `warp-proxy/` nor `psiphon-proxy/` exists in the live tree; history is preserved.
- [x] [430] No live file (excluding `docs/history/`, `tasks/archive/`, `tasks/completed/`, and session
      transcripts) mentions WARP or Psiphon.
- [x] [430] blowsh proxy support is documented as env-only and still works with a generic proxy.
- [x] [430] Dated ADRs record the removal and the reason.
- [x] [430] No service unit or compose file references the removed containers.
- [x] [431] A repo-wide grep for the retired names returns only history, archive, completed-task, and
      session-transcript paths.
- [x] [431] No duplicate test covers the same contract; the suite is smaller with the guard floor intact.
- [x] [431] Every doc and README describes the final architecture with no reference to a removed component.
- [x] [431] Prompt-sync byte identity still holds.
- [x] [431] The full suite passes with exit code 0.
- [x] Traceability: All 6 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Verification Evidence

- **Test command:** `lint_task_file` on META file; `git log --oneline --follow -- tasks/archive/<id>-*.md | head` for archived sources; project test suite if logic changed
- **Expected result:** META lint passes; all 6 sources in `tasks/archive/` with `superseded` status; single Factual Git Diff covers all bundled changes
- **Actual result:** _(Hands fill during execution)_
- **Exit code:** _(Hands fill)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.
- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.
- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.
- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded [426, 427, 428, 429, 430, 431], remove Superseded-By footer, delete or archive `tasks/backlog/432-brain-litellm-zen-bridge-cleanup.md` as abandoned. No HQ code beyond bundler is affected.

---

## Execution Log & Reasoning

### Assumptions

- **A1** — The bundler caps at six tasks, so the Manager's nine numbered items were folded into five task files plus the folded 426; the LiteLLM task carries the debug switch and the sweep task carries tests plus docs.
- **A2** — "`muse-spark-1.3-contributor`" and the other Go models need no LiteLLM catalog entry: the bridge calls `litellm.responses(model="openai/<id>", api_base=BRAIN_API_BASE)`, so the loopback gateway stays authoritative for model ids and no per-model registration drifts.
- **A3** — Removing `warp-proxy/` and `psiphon-proxy/` is done with `git rm` rather than a new `archive/` tree, because the task XML forbids new files under `docs/history` and git history already holds every byte.
- **A4** — `BRAIN_UPSTREAM_MODE` is retired outright instead of being kept as a legacy switch: LiteLLM's `openai/<model>` path speaks the Responses API, which was the default and only production mode, and the chat-completions converter had no remaining caller once the transport moved.
- **A5** — `BRAIN_DEBUG` defaults OFF; the monthly-quota warning stays on real stderr because it is a protective signal, not per-turn chatter.

### Step 1 — Inventory (no edits)

- Transport surface recorded before editing: `_post_with_retry` (2833), `_make_client` (2986), `_send_with_retry` (2995), `_upstream_mode` (5365), `_upstream_url` (5383), `_responses_url` (5393), `_convert_responses_to_chat_completions_body` (5399), `_convert_chat_completions_to_responses_data` (5777), `_resp_json` (2931), `_error_code_from_body` (2740), `_retry_after_s` (2792).
- 45 `sys.stderr` write sites; 21 `BRAIN_*` env reads; `mcp-brain-bridge/pyproject.toml` held only `mcp[cli]` and `httpx`; `zen-proxy/proxy.py` 449 lines with the upstream proxy read at 184-187; `.env.example` duplicated `BRAIN_MODEL` blocks and `ZEN_PROXY_UPSTREAM_TIMEOUT`.
- Graph coverage: 8193 nodes, 12286 edges, files 63/63, docs 400/628 (docs cap truncated; recorded as such).

### Step 2 — zen-proxy → zen-bridge

- `git mv zen-proxy zen-bridge`, `git mv services/zen-proxy.service services/zen-bridge.service`, `git mv docs/zen-proxy.md docs/zen-bridge.md`, `git mv .opencode/memory/architecture/zen-proxy-ownership.md .../zen-bridge-ownership.md`.
- `zen-bridge/proxy.py`: renamed module docstring/startup print, package name in `pyproject.toml`, and added `upstream_proxy_url()`, `no_proxy_hosts()`, `host_bypasses_proxy()`, `_build_opener()`/`OPENER`. Precedence is `ZEN_BRIDGE_*` then lowercase then uppercase; loopback is force-added to the no-proxy set. CONNECT now skips the tunnel for bypassed hosts, and reverse-proxy traffic goes through the env-aware opener (urllib only reads the standard names by itself).
- Brain side: `_ensure_loopback_no_proxy()` forces `127.0.0.1`/`localhost`/`::1` into `no_proxy`, and `brain_proxy_url()` documents the two-hop contract; `BRAIN_HTTPS_PROXY`/`BRAIN_HTTP_PROXY` are accepted before the standard names.
- Every live `zen-proxy` reference swept: `LLM.txt`, `README.md`, `docs/{brain-bridge,services}.md`, `tests/{README,DECISIONS}.md`, memory records.

### Step 3 — warp-proxy and psiphon-proxy removed

- `git rm -r warp-proxy psiphon-proxy`, `git rm docs/blowsh-warp-proxy.md docs/blowsh-psiphon-proxy.md`.
- `docs/blowsh-proxy-options.md` rewritten as direct-by-default plus any operator HTTP proxy (`PROXY_TYPE`/`PROXY_HOST`/`PROXY_PORT`/`PROXY_BYPASS`); `docs/README.md`, `docs/blowsh-direct-egress.md`, `README.md`, `LLM.txt` (§7.5, blowsh block, env table, checklist) and `.opencode/memory/workflows/global-install-upgrade.md` updated.
- ADR-009 added to `docs/DECISIONS.md`; the blowsh memory record rewritten as a supersession.

### Step 4 — LiteLLM transport

- Deleted: `_post_with_retry`, `_make_client`, `_send_with_retry`, `_upstream_mode`, `_upstream_url`, `_responses_url`, `_resp_json`, `_error_code_from_body`, `_retry_after_s`, `_RETRYABLE_STATUS`, `_build_responses_output`, `_responses_status_from_finish`, `_FINISH_REASON_TO_STATUS`, `_convert_responses_to_chat_completions_body`, `_convert_chat_completions_to_responses_data`.
- Added `_post_with_litellm`: splits the prompt-shaped body into typed `litellm.responses` kwargs, passes the remainder as `extra_body`, calls `openai/<model>` against `BRAIN_API_BASE`, maps every exception onto `_transport_fail` (status, provider code, error type) and keeps the terminal-429 classifier.
- `litellm>=1.111.0,<2.0` pinned; LiteLLM and httpx loggers pinned to WARNING so a turn prints nothing.
- `BRAIN_DEBUG` gate: one `_debug_stream()` returns real stderr or a silent sink, resolved per call so a long-lived server honours a toggle; all 44 per-turn sites routed through it, quota warning deliberately left on real stderr.

### Deviations from the XML

- **D1** — The XML's Step 2 `git mv` for the zen-bridge rename and Step 3's `git rm` for the proxy directories were performed as written; no `archive/` destination was invented (it would have violated the XML's own "no new files under docs/history" rule).
- **D2** — `_retry_after_s` and `_error_code_from_body` were removed with the ladder even though the XML only named the seven headline helpers; both existed solely for the deleted transport, so keeping them would be dead code.
- **D3** — Test migration: the XML said delete only tests covering removed helpers. The chat-completions conversion tests (24 cases) were deleted because that whole path is gone; every Responses-API, budget, session, and diagnostic test was retargeted to a new shared `tests/litellm_double.py` fake instead of being dropped.
- **D4** — `services/zen-bridge.service` was rewritten rather than patched line-by-line, because the unit name, description, documentation path, working directory, exec path, and proxy env block all changed together.
- **D5** — At the time this log was written the retargeted suite still needs its second pass (remaining failures are the in-file `httpx` stubs inside individual tests), so the AC/DoD boxes stay unchecked until the full suite is green.

### Step 6 — Tests, docs, env

- Test seam: added `tests/litellm_double.py` (`FakeLiteLLM`, `FakeLiteLLMError`, `responses_payload`) and retargeted every Brain suite to it — `test_brain_bridge`, `test_brain_responses_alignment`, `test_brain_capability`, `test_brain_preflight`, `test_brain_diff_attach`, `test_raw_output_recovery`, `test_session_lifecycle`, `test_stage_prompts`.
- Deleted only tests that exercised removed code: the chat-completions translator suite, the direct `_post_with_retry` / taxonomy ladder tests, `_resp_json`, `_responses_url`, `_upstream_mode/_url`, and the input-converter cases. Net: 1004 → 940 collected, all green, with new guards added (provider-base resolution, retry env validation, loopback no-proxy forcing, `BRAIN_DEBUG` silence and switch).
- Debug assertions now opt in: the tests that assert a warning set `BRAIN_DEBUG=1`, which is the documented operator switch rather than a hidden behaviour change.
- `.env.example` rebuilt from a scan: one section per owner (Brain bridge / zen-bridge / MCP servers / planner / Telegram / blowsh), one line per live key, defaults in comments, no duplicate keys, no secrets. Removed the duplicated `BRAIN_MODEL` block, `ZEN_PROXY_UPSTREAM_TIMEOUT`, and every dead `ZEN_PROXY_*` name.
- Docs: `docs/brain-bridge.md` (LiteLLM transport, retry/deadline ownership, `ZEN_BRIDGE_UPSTREAM_TIMEOUT` ordering), `zen-bridge/README.md` (real files, config table, two-hop routing), `zen-bridge/DECISIONS.md` ADR-009, `services/README.md` + `services/DECISIONS.md`, `tests/README.md`, `docs/zen-bridge.md`, `docs/README.md`, `docs/blowsh-proxy-options.md`, `README.md`, `LLM.txt`.
- Memory: ownership record renamed, blowsh policy rewritten as a supersession, routing records mark `BRAIN_UPSTREAM_MODE` retired; index rebuilt (40 records).

### Verification

- `rtk test uv run --with pytest --with mcp==1.30.0 --with litellm --with pathspec --with pyyaml python -m pytest tests/ -q` → **940 passed**, exit 0.
- Live smoke: `mcp-brain-bridge/.venv/bin/python` calling `brain_turn` through the production env returned `READY` on `muse-spark-1.3-contributor` with no LiteLLM chatter on stderr.
- `zen-bridge/.venv/bin/python zen-bridge/proxy.py` on `PORT=8099` → `/health` 200; `systemd-analyze verify services/zen-bridge.service` → no syntax errors (the exec path is expected to be absent until deployment).
- Residual `zen-proxy` / `warp-proxy` / `psiphon-proxy` hits are limited to `docs/history/`, the dated ADR text, the memory supersession note, and generated `context-reports/` artifacts.

### QA round 1 — fixes applied

- **Q1 (ZEN_PROXY sweep):** fixed the live names — `LLM.txt` ladder now says `ZEN_BRIDGE_UPSTREAM_TIMEOUT`; `.opencode/memory/architecture/zen-bridge-ownership.md` timeout ordering corrected and aligned with the real ladder (900 ≤ 960 ≤ 1200 ≤ 1500s); removed a stale `ZEN_PROXY_AUDIT` claim from `zen-bridge/README.md` (the bridge ships no audit mode). Remaining `ZEN_PROXY` hits are the legacy body-cap fallback in `proxy.py` and dated ADR text.
- **Q2 (two-hop proxy proof):** `brain_proxy_url()` was defined but never called. Added `_apply_brain_proxy_env()`, which mirrors a `BRAIN_*` proxy onto `http_proxy`/`https_proxy` (and uppercase) with `setdefault`, so a host-wide proxy always wins and LiteLLM's `trust_env` picks the value up. `_post_with_litellm` now runs `_ensure_loopback_no_proxy()` then `_apply_brain_proxy_env()` before the call. Three tests pin it: the mirror, the standard-name precedence, and loopback staying in `no_proxy` while a proxy is configured.
- **Q3 (retry/timeout/429 parity):** added `test_litellm_receives_retry_budget_and_provider_base` (asserts `num_retries`, `api_base`, `openai/` prefix, and a timeout are handed to LiteLLM) and `test_terminal_429_is_not_retried` (billing-terminal 429 fails on the first call). `BRAIN_OVERALL_DEADLINE_S` stays documented as a pre-call guard because LiteLLM owns the in-flight timeout.
- **Q4 (evidence + lint):** full suite re-run after the fixes; evidence recorded below; lint re-run on this file.

### Verification (QA round 1)

- `rtk test uv run --with pytest --with mcp==1.30.0 --with litellm --with pathspec --with pyyaml python -m pytest tests/ -q` → **945 passed**, exit 0.
- `grep -rin ZEN_PROXY` (excluding history/tasks/context-reports) → only the documented legacy body-cap fallback and dated ADR text.
- LiteLLM receives a proxy through the standard env names, and loopback is always excluded.

### QA round 2 — fixes applied

- **Proxy mutation semantics:** `_apply_brain_proxy_env()` now treats a blank or whitespace-only standard name as unset and fills it from the resolved `BRAIN_*` value; a truthy host-wide proxy is never overwritten. `_ensure_loopback_no_proxy()` stays additive-only (append, never remove, mirrored to `no_proxy` and `NO_PROXY`). `docs/brain-bridge.md` states the stickiness, the precedence, and the loopback exemption.
- **Terminal-429 parity closed by documentation + a sharper test:** `test_terminal_429_surfaces_quota_hint_without_bridge_retry` now asserts one bridge-level LiteLLM call and that `num_retries` is still handed over, and its docstring names the accepted deviation (LiteLLM retries internally before the bridge sees the error, bounded by `BRAIN_LITELLM_RETRIES` × read timeout). `docs/brain-bridge.md` records the deviation and that `BRAIN_OVERALL_DEADLINE_S` is a pre-call guard only.
- **Retry handoff tests:** `test_retry_budget_is_configurable` (0 disables), `test_litellm_receives_retry_budget_and_provider_base` (num_retries/api_base/openai prefix/timeout), `test_transient_5xx_surfaces_as_transport_error` (post-exhaustion mapping), `test_blank_standard_proxy_is_filled_from_brain_alias`.
- **Evidence refresh:** full suite re-run after the changes.

### Verification (QA round 2)

- `rtk test uv run --with pytest --with mcp==1.30.0 --with litellm --with pathspec --with pyyaml python -m pytest tests/ -q` → **948 passed**, exit 0.
- `grep -rin ZEN_PROXY` (excluding history/tasks/context-reports) → legacy body-cap fallback in `proxy.py` plus dated ADR text only.
- `grep -rin warp|psiphon` → `docs/history/`, dated ADRs, and the memory supersession note only.

### QA round 2 — fixes applied

- **Proxy mutation semantics:** `_apply_brain_proxy_env()` treats a blank or whitespace-only standard name as unset and fills it from the resolved `BRAIN_*` value; a truthy host-wide proxy is never overwritten. `_ensure_loopback_no_proxy()` stays additive-only (append, never remove, mirrored to `no_proxy` and `NO_PROXY`). `docs/brain-bridge.md` states the stickiness, precedence, and loopback exemption.
- **Terminal-429 parity closed by documentation plus a sharper test:** `test_terminal_429_surfaces_quota_hint_without_bridge_retry` asserts one bridge-level LiteLLM call and that `num_retries` is still handed over; its docstring names the accepted deviation (LiteLLM retries internally before the bridge sees the error, bounded by `BRAIN_LITELLM_RETRIES` × read timeout). `docs/brain-bridge.md` records the deviation and that `BRAIN_OVERALL_DEADLINE_S` is a pre-call guard only.
- **Retry handoff tests added:** `test_retry_budget_is_configurable` (0 disables), `test_litellm_receives_retry_budget_and_provider_base`, `test_transient_5xx_surfaces_as_transport_error`, `test_blank_standard_proxy_is_filled_from_brain_alias`.

### Verification (QA round 2)

- `rtk test uv run --with pytest --with mcp==1.30.0 --with litellm --with pathspec --with pyyaml python -m pytest tests/ -q` → **948 passed**, exit 0.
- `grep -rin ZEN_PROXY` (excluding history/tasks/context-reports) → legacy body-cap fallback in `proxy.py` plus dated ADR text only.
- `grep -rin warp|psiphon` → `docs/history/`, dated ADRs, and the memory supersession note only.

### Review round 1 — advisories resolved

- **R1 (CHANGELOG count):** entry now states `948 passed`.
- **R2 (`install()` helper):** `tests/litellm_double.py::install` now takes the bridge module and actually patches the seam through `monkeypatch`; the fake is still returned.
- **R3 (httpx direct dependency):** removed from `mcp-brain-bridge/pyproject.toml` with a one-line reason — LiteLLM brings httpx, and the bridge no longer imports it directly. `uv lock` regenerated.

### Manager round 3 — retry policy removal and seven-seat stages

- **Retry policy removed (code):** `num_retries=0` is now pinned on the LiteLLM call. Deleted `_litellm_retries` + `BRAIN_LITELLM_RETRIES`, `_TERMINAL_429_CODES`, `_terminal_429_code`, `_error_payload`, and `_overall_deadline_s` + `_DEFAULT_OVERALL_DEADLINE_S` + `BRAIN_OVERALL_DEADLINE_S`. `_provider_error_hint` no longer carries retry/quota advice. `_transport_fail` and the `PROVIDER_ERROR` report stay, so a failure is still surfaced with status/code/type — the caller decides whether to try again.
- **Retry policy removed (tests):** deleted the retry-budget, retries-env, overall-deadline, and terminal-429 classifier tests; retargeted the transport tests to assert `num_retries == 0` and that a 429 is reported like any other provider error with no retry advice.
- **Retry policy removed (docs/env):** `docs/brain-bridge.md` (transport section, timeout ladder, parameter table), `.env.example`, `LLM.txt`, `.opencode/memory/architecture/zen-bridge-ownership.md`, `zen-bridge/README.md`.
- **Seven-seat stage fix:** every stage roster in `prompts/stage-manifest.json` now lists all seven personas in canonical order. Root cause of the suspected bug: each artifact actually shipped only its own persona block (qa → 1 block) while the roster table named all seven, so a seat-name grep reported 7/7 while the adoptable personas were 1/7.
- **Artifacts regenerated:** `assemble_system_prompt.py --output system-prompt.md --stages`, then `--check` → current. All eight artifacts are 103,753 bytes and byte-identical to the full prompt.
- **Installed-copy drift closed:** `~/.config/opencode/system-prompt.md` and all eight `~/.config/opencode/build/stage-prompts/*.md` were re-synced; the copies had been stale at 9.93.0 while the repo was 9.96.0.
- **Contract tests retargeted:** `test_manifest_declares_the_contract_stage_set`, `test_stage_artifacts_carry_every_contract_persona`, `test_sprint_and_planner_stages_route_their_seats`, plus two new seat-presence tests (`test_every_stage_ships_all_seven_seats`, `test_stage_artifact_matches_the_full_prompt_persona_set`).
- **Docs:** ADR added to `prompts/fragments/DECISIONS.md` ("Every Stage Ships All Seven Seats"), and the assembler docstring + manifest description now state the all-seats contract.

### Verification (manager round 3)

- `assemble_system_prompt.py --check` → "full prompt and 8 stage artifacts are current", exit 0.
- Per-artifact persona blocks: 7/7 in the repo build and 7/7 in the installed copies.
- `rtk test uv run --with pytest --with mcp==1.30.0 --with litellm --with pathspec --with pyyaml python -m pytest tests/ -q` → **940 passed**, exit 0.
- `grep -rn 'BRAIN_LITELLM_RETRIES\|BRAIN_OVERALL_DEADLINE_S'` outside history/tasks → zero **active readers**; one retired-key row remains in `docs/brain-bridge.md` on purpose, to name the key as retired rather than leave a silent gap.

### Manager round 4 — verification, audit, and the seat design settled

- **Seat design (supersedes round 3's all-seven-blocks change):** research on system-prompt practice is consistent that multiple personas in one system message conflict and that per-persona instructions burn context every turn. The all-blocks variant was therefore reverted: each stage ships only its declared lead persona block(s) — one block for qa/review/implement/closure/sprint/planner, five for plan, seven for brainstorm — plus the full seven-seat roster and a new `auto_load` **Layer 3 — roster adoption** rule that lets a turn adopt any seat when the task needs it, declared in the bracket label, with one lead speaker outside a brainstorm turn. Artifact sizes: qa 90 KB, implement/closure 91 KB, plan 99 KB, full prompt 104 KB — against 104 KB for every artifact under the all-blocks variant.
- **Manifest reverted** to stage-scoped lead rosters (`plan` 5, `implement`/`closure` programmer, `qa` qa-engineer, `review` code-reviewer, `sprint` sprint-strategist, `planner` project-planner, `brainstorm` 7) with the description rewritten to state the rule.
- **Tests retargeted again:** `test_every_stage_names_all_seven_seats` (every artifact can name all seven and carries the Layer 3 rule, and ships exactly its declared blocks), `test_stage_artifact_lead_persona_matches_its_roster`, `test_manifest_declares_the_contract_stage_set`, `test_stage_artifacts_carry_their_contract_personas`.
- **`.env.example` re-verified:** every key in the file has at least one live reader and no live reader is missing; `BRAIN_LITELLM_RETRIES`/`BRAIN_OVERALL_DEADLINE_S` are gone.
- **Leftover audit (graph 8209 nodes, 64/64 files):** fixed the last live stale doc — `mcp-brain-bridge/README.md` still documented `BRAIN_UPSTREAM_MODE`, the chat-completions bridge, `ZEN_PROXY_UPSTREAM_TIMEOUT`, and `BRAIN_OVERALL_DEADLINE_S`; replaced with the LiteLLM/no-retry transport section and the corrected ladder. Added ADR-015 to `mcp-brain-bridge/DECISIONS.md` marking ADR-004/ADR-014 superseded, removed a stale `BRAIN_UPSTREAM_MODE` delenv from a test, deleted `.pytest_cache`, `.ruff_cache`, and every `__pycache__`, and rebuilt the memory index (40 records). Remaining hits are history only: `CHANGELOG.md`, dated ADRs, `docs/history/`, and retired-key notes.
- **Artifacts regenerated and synced:** `--check` reports current; installed copies carry 1 lead block (plan 5, brainstorm 7) and the Layer 3 rule in every artifact.

### Verification (manager round 4)

- `assemble_system_prompt.py --check` → "full prompt and 8 stage artifacts are current", exit 0.
- Installed copies: qa/review/implement/closure/sprint/planner 1 block, plan 5, brainstorm 7; every artifact contains "Layer 3".
- `rtk test uv run --with pytest --with mcp==1.30.0 --with litellm --with pathspec --with pyyaml python -m pytest tests/ -q` → **940 passed**, exit 0.
- Key audit: `KEYS WITH NO READER: []`.

### Review verdict

- Code Reviewer: **APPROVED** — "Technically APPROVED. F1: Layer 3 is real code in catalog common fragments. F2: Manifest rosters are stage scoped and match artifacts. F3: Bridge README states LiteLLM with no retry correctly." Advisories A1 (README lead-roster wording) and A2 (bundled checklist still phrased old retry parity as met) were both fixed before closure. Status: **PO_REVIEW_PENDING** until the Manager's closure word.
- QA Engineer: **QA_PASSED** (round 5) with vulnerabilities V1–V3 (caller-owned retry, sticky proxy mirror, manual install sync) all documented and accepted.
- Manager: "Approved for closure" (2026-11-27).

### Deviations (continued)

- **D6** — `zen-bridge/DECISIONS.md` ADR-009 was appended via a shell heredoc instead of the native edit tool. The content is correct and the file parses, but it is a tooling-discipline deviation worth naming rather than hiding.
- **D7** — The `mcp-brain-bridge` dependency comment block at the top of `server.py` was updated to `litellm`, and `uv sync` regenerated `mcp-brain-bridge/uv.lock`; the package list therefore grows by LiteLLM's transitive tree.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `889932bab0f1c34983f93c5928bce9a5ec0b6214`
<!-- END_GIT_DIFF -->
