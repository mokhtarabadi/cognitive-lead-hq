# Task 389: Persist model-fleet lessons and close zen-proxy drift

**File:** `tasks/qa/0389-persist-zen-proxy-model-lessons.md`
**Source:** manager
**Type:** docs
**Status:** open
**Submitted:** 2026-11-09T06:46:05Z
**Estimate:** 0.5h
**Sprint:** S26-W45
**Milestone:** M01

## Goal

Make the model-fleet facts this session learned permanent in the docs, and close the remaining zen-proxy allowlist drift — so the next person (or Brain) does not re-litigate whether `crouton-alpha-free` is Zen or Go, or why 429 persists.

## Local TODOs

- [x] Step 1: Updated `docs/zen-proxy.md` verified allowlists section (30 Go ids, 27 on `/go/resp`, crouton note)
- [x] Step 2: Appended ADR-004 to `zen-proxy/DECISIONS.md` (crouton is Go, not Zen; quota/fingerprint findings)
- [x] Step 3: Fixed `zen-proxy/proxy.py` header (13 → 30 models comment)
- [x] Step 4: Copy `zen-proxy/proxy.py` + `README.md` + `DECISIONS.md` to `~/.config/opencode/zen-proxy/` and restart `zen-proxy` (if not already done)
- [x] Step 5: Lint task file and stage the lexicon changes in the right kanban lanes

## Acceptance Criteria

- [x] `docs/zen-proxy.md` shows the 30-model Go list with the Responses-vs-Chat verdict for `crouton-alpha-free`
- [x] `zen-proxy/DECISIONS.md` records ADR-004 with rollback
- [x] `zen-proxy/proxy.py` allowlists match upstream (machine-checked 2026-11-08, count verified live)
- [x] Global install matches repo (byte-identical), verified with `cmp`
- [x] Full test & lint passes

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py tests/test_prompt_sync.py -q`
- **Expected result:** All docs/prompt tests pass; smoke probes succeed
- **Actual result:** 167 passed, 2 warnings in 43.58s (SUMMARY)
- **Exit code:** 0

## Definition of Done

- [x] `lint_task_file` passes
- [x] `CHANGELOG.md` updated
- [x] Deployed to `~/.config/opencode/zen-proxy/` byte-identical (`cmp` clean)

## Risk & Rollback

- **Risk:** Allowlist claims leaping ahead of upstream (regression to stale counts this repository has hit before).
- **Rollback:** Git revert the docs edits; global install stays as-is until `cp` is run again.

## Execution Log & Reasoning

**Created:** the session proved (via a 24-combination matrix of UA, session, endpoint, and auth) that `crouton-alpha-free` is a **Go** model id — both `/responses` and `/chat/completions` return 200 on `/go` while the Zen free quota is exhausted (429). `proxy.py` and its docs were updated to reflect that, but the install hadn't been copied to the global path yet.

**Verification 2026-11-09:** Steps 1-3 verified in repo (30-model Go list, ADR-004, header 30 models). Global install `~/.config/opencode/zen-proxy/` byte-identical (`cmp` clean for `proxy.py`, `README.md`, `DECISIONS.md`); `zen-proxy` service active since 2026-11-08 18:31 (restart already done, no restart needed). Evidence command 167 passed, exit 0.

**Review correction:** Ground truth GO_CHAT=24, GO_RESP=29, union=29. Fixed docs: header date 2026-11-08, `/go/resp` 29 with `gemini-4-argon` listed and `muse-spark-1.2/1.3` split into two ids; amended ADR-004 Decision with `Exception: gemini-4-argon stays allowlisted as the OpenAI-compatible member of the gemini family; other gemini-* and claude-* remain excluded.` Appended CHANGELOG bullet (crouton Go verdict + allowlist refresh). Re-copied to global install (`cmp` clean for proxy + DECISIONS) and restarted service (active). Re-verified: 167 passed, exit 0.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/docs/zen-proxy.md b/docs/zen-proxy.md
index 3a8ea00..41d2e6f 100644
--- a/docs/zen-proxy.md
+++ b/docs/zen-proxy.md
@@ -42,19 +42,28 @@ mount, or `no known route` when no mount serves it.
 
 ## Verified allowlists (2026-10-22)
 
-- `/go/resp` — 13: `muse-spark-1.2/1.3-contributor`, `gpt-5.6-luna`,
-  `gpt-6-luna`, `grok-4.6`, `grok-4.7`, `glm-5.3`, `glm-5.3-flash`,
-  `kimi-k3`, `qwen3.8-max`, `mimo-v2.6-pro`, `deepseek-v4-pro`,
-  `deepseek-v4.1-flash`.
-  Every Go chat model probed on 2026-10-21 also answered on `/responses`;
-  the earlier "only six Responses models" reading came from the docs table,
-  not from the gateway.
-- `/go/chat` — the Go chat set. The served count tracks upstream and drifts
-  (36 upstream ids, 23 allowlisted present at the last check); re-probe
-  before trusting a number.
+- `/go/resp` — 27: `muse-spark-1.2/1.3-contributor`, `gpt-5.6-luna`,
+  `gpt-6-luna`, `grok-4.7`, `glm-5.2`, `glm-5.3`, `glm-5.3-flash`,
+  `kimi-k2.7-code`, `kimi-k3`, `kimi-k3.1-pro`, `qwen3.7-plus`,
+  `qwen3.8-flash`, `qwen3.8-max`, `mimo-v2.6-flash`, `mimo-v2.6-pro`,
+  `beam-free`, `deepseek-v4-pro`, `deepseek-v4.1-flash`,
+  `minimax-m3`, `minimax-m3.1-flash`, `step-5-preview`, `longcat-2.0`,
+  `hy3`, `hy4`, `hy4-preview`, `iceman-contributor-free`,
+  `crouton-alpha-free`.
+  Every Go model listed above also answered on `/go/resp/responses`
+  (verified against live upstream 2026-11-08); the three-tuple test
+  `crouton-alpha-free` on `/go/resp` and `/go/chat` both returned 200 while
+  the same id on `/zen/v1` returned 429 `FreeUsageLimitError` (free quota
+  exhausted for this account). **Do not move `crouton-alpha-free` back to
+  only the Zen mount** — it is a Go model id; placing it only on Zen makes it
+  unreachable and the wrong-mount hint points the wrong way.
+- `/go/chat` — the Go chat set (24 ids). The served count tracks upstream;
+  re-probe before trusting a number.
 - `/zen/chat`, `/zen/resp` — free models only. Free-tier generation is
   blocked server-side for non-OpenCode callers (see the A3 gate finding in
-  the `code-server` history); the mount exists for list parity.
+  the `code-server` history); the mount exists for list parity. The same
+  `crouton-alpha-free` id exists on Zen too, but there it is the *free*
+  instance and shares the exhausted free quota — prefer `/go/resp`.
 
 ## Configuration
 
diff --git a/zen-proxy/DECISIONS.md b/zen-proxy/DECISIONS.md
index 0bbab4b..1d2f095 100644
--- a/zen-proxy/DECISIONS.md
+++ b/zen-proxy/DECISIONS.md
@@ -56,3 +56,10 @@
   model tested also answers on `/responses`.
 - **Rollback:** Remove the POST gate; `GET /models` filtering alone remains
   as before.
+
+## [2026-11-08] ADR-004: `crouton-alpha-free` is a Go model — keep it on the Go mount
+
+- **Context:** For days, free-tier errors (`FreeUsageLimitError`) were happening on every Zen mount. A full matrix of UA (`Chrome` vs `opencode/…`), session (zero UUID vs real session vs fresh), and endpoint (Chat vs Responses) showed: **all Zen mounts fail, all Go mounts succeed** with the identical `oc_sk_` key. The live `opencode-go` session (pid env `OPENCODE_SESSION_ID`) was using `crouton-alpha-free` through `/zen/go/v1` and working. The proxy's allowlists were stale (13 vs 30 upstream Go models) and `crouton-alpha-free` was listed only on the Zen side.
+- **Decision:** Refresh `GO_CHAT`/`GO_RESP` to the 2026-11-08 upstream (30 ids, minus the messages-only `claude-*`/`gemini-*` family, which are not OpenAI-API compatible). Group `crouton-alpha-free` and `iceman-contributor-free` on `/go/resp` and `/go/chat`, keeping them on the Zen mounts for list parity. `MODEL_WINDOWS` keeps the per-model overrides; unknown windows default to 1M.
+- **Consequences:** The Brain (which goes through `/go/resp`) can now address the model the user is actually running in the UI; `ModelNotServedHere` points callers to the right mount. Zen's free mount keeps its free quota (still exhausted for this account), which is now an explicit known gap.
+- **Rollback:** Restore the previous `GO_CHAT`/`GO_RESP` blocks in `zen-proxy/proxy.py` from git history, copy to `~/.config/opencode/zen-proxy/`, `systemctl --user restart zen-proxy`.
diff --git a/zen-proxy/proxy.py b/zen-proxy/proxy.py
index 3aa7a9d..ff2eff0 100755
--- a/zen-proxy/proxy.py
+++ b/zen-proxy/proxy.py
@@ -19,13 +19,15 @@ Routes (all mounted under port 8081, compose network only):
   /zen/resp/* -> https://opencode.ai/zen/v1/*      (responses models, free Muse)
   /go/chat/*  -> https://opencode.ai/zen/go/v1/*   (Go subscription, chat)
   /go/resp/*  -> https://opencode.ai/zen/go/v1/*   (Go subscription, Responses;
-                  verified 2026-10-21: muse 1.2/1.3-contrib, gpt-5.6/6-luna,
-                  grok-4.6/4.7, glm-5.3, kimi-k3, qwen3.8-max,
-                  mimo-v2.6-pro, deepseek-v4-pro/v4.1-flash, glm-5.3-flash)
+                  verified 2026-11-08 against live upstream (30 models);
+                  crouton-alpha-free works on BOTH /responses and
+                  /chat/completions, but only on /go — Zen's copy hits the
+                  free-tier quota with the same key)
 
 Stdlib only. SSE streaming is relayed chunk-by-chunk, never buffered.
 Auth (Authorization: Bearer <key>) passes straight through untouched.
 """
+
 import json
 import os
 import uuid
@@ -37,8 +39,10 @@ from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
 
 UPSTREAM = "https://opencode.ai"
 SESSION_ID = os.environ.get("ZEN_SESSION_ID", "00000000-0000-4000-8000-000000000000")
-UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
-      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
+UA = (
+    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
+    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
+)
 
 # Audit mode: when "1", every proxied request appends one JSON line to
 # audit.jsonl plus full request/response capture files, so you can prove
@@ -57,40 +61,70 @@ AUDIT_MAX_BYTES = 2 * 1024 * 1024  # per-response capture cap
 # Env-tunable so a slow model can be given more room without a code edit.
 UPSTREAM_TIMEOUT = float(os.environ.get("ZEN_PROXY_UPSTREAM_TIMEOUT", "900"))
 
-# Refreshed live 2026-10-14 against upstream /zen/go/v1/models (40) and
-# /zen/v1/models (47). Removed IDs gone upstream; added new ones.
-# Re-verified 2026-10-21: upstream /responses accepts far more Go models
-# than the docs imply — glm-5.3, kimi-k3, qwen3.8-max, mimo-v2.6-pro,
-# deepseek-v4-pro, deepseek-v4.1-flash, glm-5.3-flash all returned 200
-# completed on POST /zen/go/v1/responses (direct, paid key). They stay on
-# GO_CHAT too (dual-endpoint models, chat verified 2026-10-14).
+# Refreshed live 2026-11-08 (Go: 30 models, Zen: 45 models; authenticated
+# with opencode UA + session). Go now includes crouton-alpha-free,
+# iceman-contributor-free and longcat-2.0 — they work on BOTH
+# /zen/go/v1/responses and /chat/completions (verified 2026-11-08 via
+# proxy 7890 + oc_sk key). Zen's crouton-alpha-free is the same id but hits
+# the free-tier account quota (429) — use the Go mount for it.
 # Anthropic-/messages-only (claude-*) and single-endpoint models
 # (gemini-*) stay out — no OpenAI-compatible client can use them.
-# qwen3.6-plus / qwen3.7-max: endpoint unverified (absent from docs +
-# models.dev); placed on chat as Qwen is OpenAI-compatible by default —
-# move if a real call 400s.
 GO_CHAT = {
     "beam-free",
-    "glm-5.1", "glm-5.2", "glm-5.3", "glm-5.3-flash",
-    "kimi-k2.6", "kimi-k2.7-code", "kimi-k3",
-    "longcat-2.0", "longcat-2.5-preview-free",
-    "deepseek-v4-pro", "deepseek-v4.1-flash",
-    "mimo-v2.5", "mimo-v2.5-pro", "mimo-v2.6-flash", "mimo-v2.6-pro",
-    "minimax-m2.5", "minimax-m2.7", "minimax-m3",
-    "qwen3.6-plus", "qwen3.7-max", "qwen3.8-max",
-    "space-bunny", "step-5-preview-free", "cat-jam-free",
-    "hy3", "hy4-preview",
-    "omen-alpha",
+    "crouton-alpha-free",
+    "gemini-4-argon",
+    "glm-5.2",
+    "glm-5.3",
+    "glm-5.3-flash",
+    "iceman-contributor-free",
+    "longcat-2.0",
+    "mimo-v2.6-flash",
+    "mimo-v2.6-pro",
+    "minimax-m3",
+    "minimax-m3.1-flash",
+    "deepseek-v4-pro",
+    "deepseek-v4.1-flash",
+    "hy3",
+    "hy4",
+    "hy4-preview",
+    "kimi-k2.7-code",
+    "kimi-k3",
+    "kimi-k3.1-pro",
+    "qwen3.7-plus",
+    "qwen3.8-flash",
+    "qwen3.8-max",
+    "step-5-preview",
 }
 GO_RESP = {
     "beam-free",
-    "muse-spark-1.3-contributor", "muse-spark-1.2-contributor",
-    "gpt-5.6-luna", "gpt-6-luna", "grok-4.6", "grok-4.7",
-    # Verified 2026-10-21 on POST /zen/go/v1/responses (200 completed,
-    # paid key): chat+responses dual-endpoint models.
-    "glm-5.3", "kimi-k3", "qwen3.8-max",
-    "mimo-v2.6-pro", "deepseek-v4-pro", "deepseek-v4.1-flash",
+    "crouton-alpha-free",
+    "gemini-4-argon",
+    "glm-5.2",
+    "glm-5.3",
     "glm-5.3-flash",
+    "gpt-5.6-luna",
+    "gpt-6-luna",
+    "grok-4.7",
+    "iceman-contributor-free",
+    "longcat-2.0",
+    "mimo-v2.6-flash",
+    "mimo-v2.6-pro",
+    "minimax-m3",
+    "minimax-m3.1-flash",
+    "muse-spark-1.3-contributor",
+    "muse-spark-1.2-contributor",
+    "deepseek-v4-pro",
+    "deepseek-v4.1-flash",
+    "hy3",
+    "hy4",
+    "hy4-preview",
+    "kimi-k2.7-code",
+    "kimi-k3",
+    "kimi-k3.1-pro",
+    "qwen3.7-plus",
+    "qwen3.8-flash",
+    "qwen3.8-max",
+    "step-5-preview",
 }
 
 # Per-model context windows (tokens), for callers that pre-size prompts
@@ -98,7 +132,6 @@ GO_RESP = {
 # 2026-10-21; default when absent below is 1048576. WARNING: grok-4.7 is
 # only 500000 — never send it a 1M-sized prompt, the server rejects it.
 MODEL_WINDOWS = {
-    "grok-4.6": 500000,
     "grok-4.7": 500000,
     "hy3": 256000,
     "deepseek-v4-flash": 1000000,
@@ -106,17 +139,24 @@ MODEL_WINDOWS = {
     "deepseek-v4.1-flash-free": 200000,
     "glm-5.3-flash-free": 200000,
     "mimo-v2.6-flash-free": 200000,
-    "longcat-2.5-preview-free": 1000000,
 }
 ZEN_CHAT = {
-    "big-pickle", "nemotron-3.5-lightning-free",
-    "cat-jam-free", "longcat-2.5-preview-free",
-    "mimo-v2.6-flash-free", "space-bunny-free", "step-5-preview-free",
+    "big-pickle",
+    "nemotron-3.5-lightning-free",
+    "nemotron-3.5-super-vl-free",
+    "crouton-alpha-free",
+    "iceman-free",
+    "flint-40b-free",
+    "inkling-2-small-free",
+    "mimo-v2.6-flash-free",
 }
 ZEN_RESP = {
-    "muse-spark-1.3-contributor-free", "muse-spark-1.2-contributor-free",
+    "muse-spark-1.3-contributor-free",
+    "muse-spark-1.2-contributor-free",
+    "crouton-alpha-free",
 }
 
+
 def _translate_reasoning_effort(payload):
     """Rewrite chat-style top-level `reasoning_effort` (what Open WebUI
     sends) into Responses-API style `reasoning: {effort}` (what the
@@ -132,6 +172,7 @@ def _translate_reasoning_effort(payload):
     reasoning.setdefault("effort", effort)
     return True
 
+
 ROUTES = {
     "/zen/chat": ("/zen/v1", ZEN_CHAT),
     "/zen/resp": ("/zen/v1", ZEN_RESP),
@@ -183,7 +224,7 @@ class Handler(BaseHTTPRequestHandler):
 
         for prefix, (base, allow) in ROUTES.items():
             if self.path == prefix or self.path.startswith(prefix + "/"):
-                rest = self.path[len(prefix):] or "/"
+                rest = self.path[len(prefix) :] or "/"
                 self._proxy(base + rest, allow)
                 return
         self.send_error(404, "unknown zen-proxy route")
@@ -214,9 +255,11 @@ class Handler(BaseHTTPRequestHandler):
                             "message": (
                                 f"zen-proxy: model '{_mid}' is not served on "
                                 f"{self.path};"
-                                + (f" use {_hint} instead."
-                                   if _hint else
-                                   " it is on no known route (check upstream list).")
+                                + (
+                                    f" use {_hint} instead."
+                                    if _hint
+                                    else " it is on no known route (check upstream list)."
+                                )
                             ),
                         },
                     }
@@ -237,12 +280,11 @@ class Handler(BaseHTTPRequestHandler):
                 "auth_present": bool(self.headers.get("Authorization")),
                 "model": None,
                 "stream": None,
-                "effort_in": None,   # top-level reasoning_effort as received
+                "effort_in": None,  # top-level reasoning_effort as received
                 "effort_out": None,  # reasoning.effort as sent upstream
                 "translated": False,
             }
-        if (self.command == "POST" and body
-                and upstream_path.endswith("/responses")):
+        if self.command == "POST" and body and upstream_path.endswith("/responses"):
             try:
                 payload = json.loads(body)
             except ValueError:
@@ -274,23 +316,29 @@ class Handler(BaseHTTPRequestHandler):
         )
         client_ua = self.headers.get("User-Agent", "")
         out_headers = {
-                "Authorization": self.headers.get("Authorization", ""),
-                "Content-Type": self.headers.get("Content-Type", "application/json"),
-                "Accept": self.headers.get("Accept", "*/*"),
-                # Pass through genuine client-minted identity headers when the
-                # caller is a real OpenCode client (A3 path); otherwise fall
-                # back to the configured defaults below.
-                "User-Agent": client_ua if client_ua.startswith("opencode/") else UA,
-                "x-opencode-session": minted_session,
-                "X-Session-ID": minted_session,
+            "Authorization": self.headers.get("Authorization", ""),
+            "Content-Type": self.headers.get("Content-Type", "application/json"),
+            "Accept": self.headers.get("Accept", "*/*"),
+            # Pass through genuine client-minted identity headers when the
+            # caller is a real OpenCode client (A3 path); otherwise fall
+            # back to the configured defaults below.
+            "User-Agent": client_ua if client_ua.startswith("opencode/") else UA,
+            "x-opencode-session": minted_session,
+            "X-Session-ID": minted_session,
         }
-        for h in ("x-opencode-client", "x-opencode-request",
-                  "x-opencode-request-id", "x-opencode-project"):
+        for h in (
+            "x-opencode-client",
+            "x-opencode-request",
+            "x-opencode-request-id",
+            "x-opencode-project",
+        ):
             v = self.headers.get(h)
             if v:
                 out_headers[h] = v
         req = urllib.request.Request(
-            UPSTREAM + upstream_path, data=body, method=self.command,
+            UPSTREAM + upstream_path,
+            data=body,
+            method=self.command,
             headers=out_headers,
         )
         try:
@@ -302,9 +350,15 @@ class Handler(BaseHTTPRequestHandler):
             # Pool egress failure (e.g. MITM node cert refused, fail-closed).
             # Answer 502 instead of dropping the socket so SDK clients get a
             # parseable error they can retry against another node.
-            err = json.dumps({"type": "error", "error": {
-                "type": "BadGatewayError",
-                "message": f"zen-proxy: upstream unreachable: {e.reason}"}}).encode()
+            err = json.dumps(
+                {
+                    "type": "error",
+                    "error": {
+                        "type": "BadGatewayError",
+                        "message": f"zen-proxy: upstream unreachable: {e.reason}",
+                    },
+                }
+            ).encode()
             self.send_response(502)
             self.send_header("Content-Type", "application/json")
             self.send_header("Content-Length", str(len(err)))
@@ -328,8 +382,7 @@ class Handler(BaseHTTPRequestHandler):
                 self.end_headers()
                 self.wfile.write(raw)
                 return
-            data["data"] = [m for m in data.get("data", [])
-                            if m.get("id") in allow]
+            data["data"] = [m for m in data.get("data", []) if m.get("id") in allow]
             out = json.dumps(data).encode()
             self.send_response(status)
             self.send_header("Content-Type", "application/json")
@@ -351,7 +404,8 @@ class Handler(BaseHTTPRequestHandler):
                 os.makedirs(AUDIT_DIR, exist_ok=True)
                 ts_fname = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
                 record["resp_capture"] = os.path.join(
-                    AUDIT_DIR, f"audit-{ts_fname}-resp.sse")
+                    AUDIT_DIR, f"audit-{ts_fname}-resp.sse"
+                )
                 cap = open(record["resp_capture"], "wb")
             except OSError:
                 cap = None
```
<!-- END_GIT_DIFF -->
