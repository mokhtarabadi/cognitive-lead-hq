# Architectural Decisions: zen-proxy

## [2026-10-22] ADR-001: This slice owns the proxy, not the homelab repo

- **Context:** The proxy was born in the `code-server` homelab repo as an
  Open-WebUI sidecar (Docker, then a native revival). Open-WebUI was retired
  2026-09-19, and the only remaining consumer became this project's Brain
  Bridge (`BRAIN_API_BASE=http://127.0.0.1:8081/go/resp`). Every behavioural
  change since then — route allowlists, `reasoning.effort` translation,
  per-model windows, the 900s upstream timeout, the 64-char input-id rule —
  was driven by Brain and Hands needs, yet lived in the other repo. Two repos
  owning one runtime contract is what let fixes go missing (the owner repo's
  docs still described 8081 as closed while it served live traffic).
- **Decision:** Move source, docs, and the systemd unit here. Install
  globally next to the MCP server slices (`~/.config/opencode/zen-proxy/`),
  build the venv with `uv`, and launch through that venv interpreter from
  `services/zen-proxy.service`. Read configuration from the single global
  `~/.config/opencode/.env`. `code-server` keeps only a historical pointer.
- **Consequences:** One repo owns the proxy's behaviour and its consumer.
  The port (8081), the four mount paths, and `BRAIN_API_BASE` are unchanged,
  so Brain needs no reconfiguration. The proxy adds no secret of its own: it
  passes the caller's `Authorization` header through and only reads
  `ZEN_SESSION_ID` as a fallback.
- **Rollback:** Restore `archive/zen-proxy-native-2026-09-27/` from
  `code-server` git history, re-point the unit to that path, restart.

## [2026-10-22] ADR-002: Upstream timeout is tunable and defaults to 900s

- **Context:** Long `xhigh`/`max` reasoning turns failed with
  `RemoteProtocolError: Server disconnected without sending a response` and
  the bridge reported `provider overall deadline hit (500.0s)`. The proxy's
  hard-coded `urlopen(timeout=300)` was the real limiter: any upstream call
  whose first byte arrived after five minutes was dropped with no response,
  the caller retried, and the retry-burn hit its own deadline. A deep
  `gpt-6-luna` turn spends 14-19K reasoning tokens — five to ten minutes.
- **Decision:** `ZEN_PROXY_UPSTREAM_TIMEOUT` (default 900s) replaces the
  constant. Ordering contract recorded: proxy timeout ≤ caller overall
  deadline ≤ MCP client execution timeout.
- **Consequences:** Reasoning turns up to ~15 minutes complete. A genuinely
  hung upstream surfaces later; the client timeout caps the worst case and
  the `502 BadGatewayError` path still answers pool failures.
- **Rollback:** Set `ZEN_PROXY_UPSTREAM_TIMEOUT=300` in the unit env — no
  code change needed.

## [2026-10-22] ADR-003: Mounts are enforced on POST as well as on /models

- **Context:** The route allowlists originally filtered only `GET /models`,
  which made them display-only: a model posted to the wrong mount reached
  the upstream and came back as an opaque 400 about API style.
- **Decision:** `POST` bodies are checked against the mount's allowlist
  before dispatch. A mismatch returns `404 ModelNotServedHere` with the
  correct mount named, or `no known route` when the id is unserved anywhere.
- **Consequences:** Callers get an actionable error instead of a provider
  400. The allowlist must be refreshed against upstream when it drifts;
  `GO_RESP` was widened on 2026-10-21 after probing showed every Go chat
  model tested also answers on `/responses`.
- **Rollback:** Remove the POST gate; `GET /models` filtering alone remains
  as before.
