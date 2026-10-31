#!/usr/bin/env python3
"""zen-proxy: sidecar between Open WebUI and the OpenCode Zen/Go gateways.

Why this exists:
  1. The gateways reject requests without an `x-opencode-session` header
     (Go: always; Zen free tier: always). Open WebUI cannot send it.
  2. Cloudflare in front of opencode.ai blocks bare SDK user-agents (HTTP 1010).
   3. Open WebUI merges model lists across connections by ID, so each mount
      path filters `/models` to only the IDs that actually work on its API
      style (chat/completions vs responses). Without this, picking e.g. a
      responses-only model on a chat connection fails.
   4. Open WebUI sends reasoning effort chat-completions style (top-level
      `reasoning_effort`); the gateways' /responses endpoints only accept
      the Responses-API shape (`reasoning: {effort}`) — the proxy rewrites
      one into the other so high/xhigh actually reach the model.

Routes (all mounted under port 8081, compose network only):
  /zen/chat/* -> https://opencode.ai/zen/v1/*      (chat models, free)
  /zen/resp/* -> https://opencode.ai/zen/v1/*      (responses models, free Muse)
  /go/chat/*  -> https://opencode.ai/zen/go/v1/*   (Go subscription, chat)
  /go/resp/*  -> https://opencode.ai/zen/go/v1/*   (Go subscription, Responses;
                  verified 2026-10-21: muse 1.2/1.3-contrib, gpt-5.6/6-luna,
                  grok-4.6/4.7, glm-5.3, kimi-k3, qwen3.8-max,
                  mimo-v2.6-pro, deepseek-v4-pro/v4.1-flash, glm-5.3-flash)

Stdlib only. SSE streaming is relayed chunk-by-chunk, never buffered.
Auth (Authorization: Bearer <key>) passes straight through untouched.
"""
import json
import os
import uuid
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "https://opencode.ai"
SESSION_ID = os.environ.get("ZEN_SESSION_ID", "00000000-0000-4000-8000-000000000000")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# Audit mode: when "1", every proxied request appends one JSON line to
# audit.jsonl plus full request/response capture files, so you can prove
# exactly what effort value was sent upstream and what came back.
# Flip via ZEN_PROXY_AUDIT in .env (needs container recreate), default off.
# NOTE: captures contain your prompts — local disk only, disable after testing.
AUDIT = os.environ.get("ZEN_PROXY_AUDIT", "0") == "1"
AUDIT_DIR = os.path.expanduser("~/.local/share/zen-proxy/audit-logs")
AUDIT_MAX_BYTES = 2 * 1024 * 1024  # per-response capture cap

# Upstream socket timeout (seconds). 2026-10-22: was hard-coded 300, which
# silently truncated long reasoning turns — a big xhigh/max turn on
# gpt-6-luna thinks for 5-10 minutes, so the proxy dropped the socket at
# 300s and the bridge saw "RemoteProtocolError: Server disconnected
# without sending a response", retried, and burned its own 500s deadline.
# Env-tunable so a slow model can be given more room without a code edit.
UPSTREAM_TIMEOUT = float(os.environ.get("ZEN_PROXY_UPSTREAM_TIMEOUT", "900"))

# Refreshed live 2026-10-14 against upstream /zen/go/v1/models (40) and
# /zen/v1/models (47). Removed IDs gone upstream; added new ones.
# Re-verified 2026-10-21: upstream /responses accepts far more Go models
# than the docs imply — glm-5.3, kimi-k3, qwen3.8-max, mimo-v2.6-pro,
# deepseek-v4-pro, deepseek-v4.1-flash, glm-5.3-flash all returned 200
# completed on POST /zen/go/v1/responses (direct, paid key). They stay on
# GO_CHAT too (dual-endpoint models, chat verified 2026-10-14).
# Anthropic-/messages-only (claude-*) and single-endpoint models
# (gemini-*) stay out — no OpenAI-compatible client can use them.
# qwen3.6-plus / qwen3.7-max: endpoint unverified (absent from docs +
# models.dev); placed on chat as Qwen is OpenAI-compatible by default —
# move if a real call 400s.
GO_CHAT = {
    "beam-free",
    "glm-5.1", "glm-5.2", "glm-5.3", "glm-5.3-flash",
    "kimi-k2.6", "kimi-k2.7-code", "kimi-k3",
    "longcat-2.0", "longcat-2.5-preview-free",
    "deepseek-v4-pro", "deepseek-v4.1-flash",
    "mimo-v2.5", "mimo-v2.5-pro", "mimo-v2.6-flash", "mimo-v2.6-pro",
    "minimax-m2.5", "minimax-m2.7", "minimax-m3",
    "qwen3.6-plus", "qwen3.7-max", "qwen3.8-max",
    "space-bunny", "step-5-preview-free", "cat-jam-free",
    "hy3", "hy4-preview",
    "omen-alpha",
}
GO_RESP = {
    "beam-free",
    "muse-spark-1.3-contributor", "muse-spark-1.2-contributor",
    "gpt-5.6-luna", "gpt-6-luna", "grok-4.6", "grok-4.7",
    # Verified 2026-10-21 on POST /zen/go/v1/responses (200 completed,
    # paid key): chat+responses dual-endpoint models.
    "glm-5.3", "kimi-k3", "qwen3.8-max",
    "mimo-v2.6-pro", "deepseek-v4-pro", "deepseek-v4.1-flash",
    "glm-5.3-flash",
}

# Per-model context windows (tokens), for callers that pre-size prompts
# (e.g. brain BRAIN_CONTEXT_WINDOW_TOKENS). Values from models.dev feed
# 2026-10-21; default when absent below is 1048576. WARNING: grok-4.7 is
# only 500000 — never send it a 1M-sized prompt, the server rejects it.
MODEL_WINDOWS = {
    "grok-4.6": 500000,
    "grok-4.7": 500000,
    "hy3": 256000,
    "deepseek-v4-flash": 1000000,
    "deepseek-v4-flash-free": 200000,
    "deepseek-v4.1-flash-free": 200000,
    "glm-5.3-flash-free": 200000,
    "mimo-v2.6-flash-free": 200000,
    "longcat-2.5-preview-free": 1000000,
}
ZEN_CHAT = {
    "big-pickle", "nemotron-3.5-lightning-free",
    "cat-jam-free", "longcat-2.5-preview-free",
    "mimo-v2.6-flash-free", "space-bunny-free", "step-5-preview-free",
}
ZEN_RESP = {
    "muse-spark-1.3-contributor-free", "muse-spark-1.2-contributor-free",
}

def _translate_reasoning_effort(payload):
    """Rewrite chat-style top-level `reasoning_effort` (what Open WebUI
    sends) into Responses-API style `reasoning: {effort}` (what the
    gateways' /responses endpoints accept, incl. low/high/xhigh).
    Returns True if the payload was changed."""
    if not isinstance(payload, dict) or "reasoning_effort" not in payload:
        return False
    effort = payload.pop("reasoning_effort")
    reasoning = payload.get("reasoning")
    if not isinstance(reasoning, dict):
        reasoning = {}
        payload["reasoning"] = reasoning
    reasoning.setdefault("effort", effort)
    return True

ROUTES = {
    "/zen/chat": ("/zen/v1", ZEN_CHAT),
    "/zen/resp": ("/zen/v1", ZEN_RESP),
    "/go/chat": ("/zen/go/v1", GO_CHAT),
    "/go/resp": ("/zen/go/v1", GO_RESP),
}


def _find_route(model):
    """Return the mount prefix that serves `model`, or None."""
    for prefix, (_, allow) in ROUTES.items():
        if model in allow:
            return prefix
    return None


def _audit_write(record, req_body=None):
    """Append one JSONL line + optional capture files. Never breaks proxying."""
    try:
        os.makedirs(AUDIT_DIR, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        if req_body is not None:
            rpath = os.path.join(AUDIT_DIR, f"audit-{ts}-req.json")
            with open(rpath, "wb") as f:
                f.write(req_body)
            record["req_capture"] = rpath
        with open(os.path.join(AUDIT_DIR, "audit.jsonl"), "a") as f:
            f.write(json.dumps(record) + "\n")
        return ts
    except OSError:
        return None


class Handler(BaseHTTPRequestHandler):
    server_version = "zen-proxy/1.0"

    def log_message(self, *args):
        pass  # keep logs quiet; errors still surface via status codes

    def _send_upstream(self):
        if self.path == "/health":
            body = b'{"status":"ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        for prefix, (base, allow) in ROUTES.items():
            if self.path == prefix or self.path.startswith(prefix + "/"):
                rest = self.path[len(prefix):] or "/"
                self._proxy(base + rest, allow)
                return
        self.send_error(404, "unknown zen-proxy route")

    do_GET = _send_upstream
    do_POST = _send_upstream

    def _proxy(self, upstream_path, allow):
        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else None
        t0 = time.monotonic()
        # Gate POST by the route allowlist: a model served on another
        # mount gets a 404 naming its correct route instead of a confusing
        # upstream 400 (endpoint/style mismatch).
        if self.command == "POST" and body:
            try:
                _probe = json.loads(body)
            except ValueError:
                _probe = None
            if isinstance(_probe, dict) and isinstance(_probe.get("model"), str):
                _mid = _probe["model"]
                if _mid not in allow:
                    _hint = _find_route(_mid)
                    _err = {
                        "type": "error",
                        "error": {
                            "type": "ModelNotServedHere",
                            "message": (
                                f"zen-proxy: model '{_mid}' is not served on "
                                f"{self.path};"
                                + (f" use {_hint} instead."
                                   if _hint else
                                   " it is on no known route (check upstream list).")
                            ),
                        },
                    }
                    _errb = json.dumps(_err).encode()
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(_errb)))
                    self.end_headers()
                    self.wfile.write(_errb)
                    return
        record = None
        if AUDIT and self.command == "POST":
            record = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "method": self.command,
                "route": self.path,
                "upstream": upstream_path,
                "auth_present": bool(self.headers.get("Authorization")),
                "model": None,
                "stream": None,
                "effort_in": None,   # top-level reasoning_effort as received
                "effort_out": None,  # reasoning.effort as sent upstream
                "translated": False,
            }
        if (self.command == "POST" and body
                and upstream_path.endswith("/responses")):
            try:
                payload = json.loads(body)
            except ValueError:
                payload = None
            if isinstance(payload, dict):
                if record is not None:
                    record["model"] = payload.get("model")
                    record["stream"] = payload.get("stream")
                    record["effort_in"] = payload.get("reasoning_effort")
                if _translate_reasoning_effort(payload):
                    body = json.dumps(payload).encode()
                    if record is not None:
                        record["translated"] = True
                        reasoning = payload.get("reasoning") or {}
                        record["effort_out"] = reasoning.get("effort")
        elif record is not None and body:
            try:
                payload = json.loads(body)
            except ValueError:
                payload = None
            if isinstance(payload, dict):
                record["model"] = payload.get("model")
                record["stream"] = payload.get("stream")
                record["effort_in"] = payload.get("reasoning_effort")
        minted_session = (
            self.headers.get("x-opencode-session")
            or self.headers.get("X-Session-ID")
            or str(uuid.uuid4())  # Hermes recipe: mint fresh ID per request
        )
        client_ua = self.headers.get("User-Agent", "")
        out_headers = {
                "Authorization": self.headers.get("Authorization", ""),
                "Content-Type": self.headers.get("Content-Type", "application/json"),
                "Accept": self.headers.get("Accept", "*/*"),
                # Pass through genuine client-minted identity headers when the
                # caller is a real OpenCode client (A3 path); otherwise fall
                # back to the configured defaults below.
                "User-Agent": client_ua if client_ua.startswith("opencode/") else UA,
                "x-opencode-session": minted_session,
                "X-Session-ID": minted_session,
        }
        for h in ("x-opencode-client", "x-opencode-request",
                  "x-opencode-request-id", "x-opencode-project"):
            v = self.headers.get(h)
            if v:
                out_headers[h] = v
        req = urllib.request.Request(
            UPSTREAM + upstream_path, data=body, method=self.command,
            headers=out_headers,
        )
        try:
            upstream = urllib.request.urlopen(req, timeout=UPSTREAM_TIMEOUT)
            status, headers, stream = upstream.status, upstream.headers, upstream
        except urllib.error.HTTPError as e:
            status, headers, stream = e.code, e.headers, e
        except urllib.error.URLError as e:
            # Pool egress failure (e.g. MITM node cert refused, fail-closed).
            # Answer 502 instead of dropping the socket so SDK clients get a
            # parseable error they can retry against another node.
            err = json.dumps({"type": "error", "error": {
                "type": "BadGatewayError",
                "message": f"zen-proxy: upstream unreachable: {e.reason}"}}).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)
            return

        ctype = headers.get("Content-Type", "")
        if upstream_path.endswith("/models") and self.command == "GET":
            raw = stream.read()
            stream.close()
            try:
                data = json.loads(raw)
            except ValueError:
                # Upstream error page (e.g. 404 on a mistyped path, 401 on a
                # bad key) — relay it as-is instead of dropping the
                # connection with an empty reply that clients can't explain.
                self.send_response(status)
                self.send_header("Content-Type", ctype or "application/octet-stream")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
                return
            data["data"] = [m for m in data.get("data", [])
                            if m.get("id") in allow]
            out = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)
            return

        self.send_response(status)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        if "text/event-stream" not in ctype:
            self.send_header("Connection", "close")
        self.end_headers()
        cap = None
        if record is not None:
            record["upstream_status"] = status
            record["content_type"] = ctype
            try:
                os.makedirs(AUDIT_DIR, exist_ok=True)
                ts_fname = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
                record["resp_capture"] = os.path.join(
                    AUDIT_DIR, f"audit-{ts_fname}-resp.sse")
                cap = open(record["resp_capture"], "wb")
            except OSError:
                cap = None
        sent = 0
        try:
            while True:
                chunk = stream.read(8192)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
                sent += len(chunk)
                if cap is not None:
                    if sent <= AUDIT_MAX_BYTES:
                        cap.write(chunk)
                    elif cap is not None:
                        cap.write(b"\n...[truncated]\n")
                        cap.close()
                        cap = None
        finally:
            stream.close()
            if cap is not None:
                cap.close()
        if record is not None:
            record["resp_bytes"] = sent
            record["duration_ms"] = round((time.monotonic() - t0) * 1000)
            _audit_write(record, req_body=body)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8081), Handler).serve_forever()
