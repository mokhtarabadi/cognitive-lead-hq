# Task 429: Rename zen-proxy to zen-bridge and Add Env-Driven Proxy Support

**File:** `tasks/backlog/429-rename-zen-proxy-to-zen-bridge-and-env-proxy.md`
**Source:** manager
**Type:** improvement
**Status:** backlog

## Goal

Rename the `zen-proxy/` slice to `zen-bridge/` across the whole project (directory, module, service
unit, docs, memory records, config, tests) and make the proxy hop configurable from env on both
sides: the Brain connects to the bridge over loopback with no proxy, and the bridge itself uses the
upstream HTTP proxy from env to reach the Go gateway.

## Manager's Notes

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

## Local TODOs

- [ ] Rename the directory with `git mv zen-proxy zen-bridge` and update the package name, module
      docstrings, and pyproject identity.
- [ ] Rename `services/zen-proxy.service` to `services/zen-bridge.service` with the new exec path and
      unit name.
- [ ] Rename `docs/zen-proxy.md` to `docs/zen-bridge.md` and rewrite inbound links.
- [ ] Sweep every live reference with `$code-search` (graph + grep) and update code, docs, memory
      records, README files, and tests; leave archive/history files untouched.
- [ ] Add explicit `ZEN_BRIDGE_HTTP_PROXY` / `ZEN_BRIDGE_HTTPS_PROXY` / `ZEN_BRIDGE_NO_PROXY`
      resolution with fallback to the standard lowercase/uppercase env names.
- [ ] Add Brain-side proxy resolution that honours `NO_PROXY` for loopback and the bridge port.
- [ ] Assert the routing with a test: a loopback `BRAIN_API_BASE` is never sent through
      `http_proxy`; a non-loopback upstream is.
- [ ] Document the two hops in `docs/brain-bridge.md` and the bridge README.

## Acceptance Criteria

- [ ] No live file references `zen-proxy` except history/archive records; `zen-bridge` is the only
      live name.
- [ ] `services/zen-bridge.service` points at the renamed module and the unit still starts cleanly.
- [ ] Brain calls to a loopback `BRAIN_API_BASE` bypass any configured `http_proxy`.
- [ ] The bridge uses env-configured proxy values for its upstream connection, with documented
      precedence.
- [ ] Existing bridge behavior (endpoints, identity headers, CONNECT) is unchanged, proven by tests.
- [ ] `.env.example` carries only the new `ZEN_BRIDGE_*` names.

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest python -m pytest tests/test_zen_bridge.py tests/test_brain_bridge.py -q`
- **Expected result:** the bridge suite and Brain suite pass, exit code 0; an explicit loopback
  no-proxy assertion is present and green.
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: the first verification run MUST use the `rtk test` prefix; a raw rerun is
> allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `testing-verification` applied and evidence recorded

## Risk & Rollback

- **Risk:** a rename miss leaves a service unit or an env key pointing at the old path, so the bridge
  fails to start after deployment; proxy precedence may route the loopback hop through the upstream
  proxy and break brain calls.
- **Rollback plan:** revert the rename commit; the bridge logic is unchanged, so reverting the name
  restores the previous working service with one deploy step.

---

## Execution Log & Reasoning

_(The Hands: log technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
