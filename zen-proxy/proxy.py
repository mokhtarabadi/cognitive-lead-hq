#!/usr/bin/env python3
"""zen-proxy: loopback gateway in front of the OpenCode Zen/Go gateways.

Why this exists:
  1. The gateways reject requests without an `x-opencode-session` header
     (Go: always; Zen free tier: always). A plain SDK client cannot send it.
  2. Cloudflare in front of opencode.ai blocks bare SDK user-agents (HTTP 1010).
   3. Clients merge model lists across connections by ID, so each mount
      path filters `/models` to only the IDs that actually work on its API
      style (chat/completions vs responses). Without this, picking e.g. a
      responses-only model on a chat connection fails.
   4. Some clients send reasoning effort chat-completions style (top-level
      `reasoning_effort`); the gateways' /responses endpoints only accept
      the Responses-API shape (`reasoning: {effort}`) — the proxy rewrites
      one into the other so high/xhigh actually reach the model.

Routes (all mounted on 127.0.0.1:8081, loopback only):
  /zen/chat/* -> https://opencode.ai/zen/v1/*      (chat models, free)
  /zen/resp/* -> https://opencode.ai/zen/v1/*      (responses models, free Muse)
  /go/chat/*  -> https://opencode.ai/zen/go/v1/*   (Go subscription, chat)
  /go/resp/*  -> https://opencode.ai/zen/go/v1/*   (Go subscription, Responses;
                  verified 2026-11-08 against live upstream (30 models);
                  crouton-alpha-free works on BOTH /responses and
                  /chat/completions, but only on /go — Zen's copy hits the
                  free-tier quota with the same key)

The consumer today is the brain bridge (mcp-brain-bridge), which talks
Responses API on /go/resp. The Open WebUI consumer is retired (2026-09-19);
the compose sidecar it used to run in is gone, and the slice now runs as a
systemd user unit.

Failure contract (2026-11-13): every failure answers with a parseable JSON
error instead of dropping the socket — 504 GatewayTimeout when the upstream
stalls, 502 BadGatewayError when the upstream is unreachable, 413
PayloadTooLarge when the request body is over the cap, 400 BadRequest for a
malformed body, 404 ModelNotServedHere for a model that another mount owns.

Stdlib only. SSE streaming is relayed chunk-by-chunk, never buffered.
Auth (Authorization: Bearer <key>) passes straight through untouched.
"""

import json
import os
import re
import signal
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "https://opencode.ai"
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

# Exit code used when a configuration value is malformed. The process
# refuses to start rather than silently falling back: the upstream timeout
# is part of a contract (proxy timeout <= caller deadline <= client
# timeout), and a substituted default would break the ordering it protects.
EXIT_CONFIG_ERROR = 2


def _env_int(name, default, minimum=1):
    """Read an integer environment variable.

    A malformed or out-of-range value stops the process with a readable
    message instead of a traceback, because a silently substituted default
    would hide the very mistake the value exists to prevent.
    """
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw.strip())
    except ValueError:
        sys.stderr.write(
            f"zen-proxy: {name}={raw!r} is not an integer; use a whole "
            f"number (default {default}) or unset it.\n"
        )
        raise SystemExit(EXIT_CONFIG_ERROR)
    if value < minimum:
        sys.stderr.write(
            f"zen-proxy: {name}={value} is below the minimum of {minimum}.\n"
        )
        raise SystemExit(EXIT_CONFIG_ERROR)
    return value


def _env_float(name, default, minimum=1.0):
    """Read a float environment variable with the same fail-loud policy."""
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = float(raw.strip())
    except ValueError:
        sys.stderr.write(
            f"zen-proxy: {name}={raw!r} is not a number; use a number "
            f"(default {default}) or unset it.\n"
        )
        raise SystemExit(EXIT_CONFIG_ERROR)
    if value < minimum:
        sys.stderr.write(
            f"zen-proxy: {name}={value} is below the minimum of {minimum}.\n"
        )
        raise SystemExit(EXIT_CONFIG_ERROR)
    return value


# Audit mode: when "1", every proxied request appends one JSON line to
# audit.jsonl plus full request/response capture files, so you can prove
# exactly what effort value was sent upstream and what came back.
# Flip via ZEN_PROXY_AUDIT in .env (restart the unit), default off.
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
# It is a socket timeout, so it is re-armed on every read: it is the
# silence wall of a stream and the wall for the first byte of a response.
UPSTREAM_TIMEOUT = _env_float("ZEN_PROXY_UPSTREAM_TIMEOUT", 900.0)

# Hard cap on an inbound request body. The cap is enforced while reading,
# before the body is buffered, so an oversized body costs one rejected
# request instead of the process memory it would have consumed.
MAX_BODY_BYTES = _env_int("ZEN_PROXY_MAX_BODY_BYTES", 32 * 1024 * 1024)

# How long a SIGTERM waits for in-flight requests to finish before the
# process exits anyway. Zero means "do not wait".
DRAIN_TIMEOUT_S = _env_int("ZEN_PROXY_DRAIN_TIMEOUT_S", 30, minimum=0)

# Bounded reception: a client that connects and dribbles a body must not
# hold a handler thread forever. The window is reopened before a response
# is streamed, so a slow upstream never trips it.
CLIENT_RECEIVE_TIMEOUT_S = 60


class _BodyTooLarge(Exception):
    """Raised when an inbound body exceeds MAX_BODY_BYTES."""


def _read_exact(rfile, count):
    """Read exactly `count` bytes, or fewer when the stream ends."""
    data = bytearray()
    while len(data) < count:
        chunk = rfile.read(count - len(data))
        if not chunk:
            break
        data += chunk
    return bytes(data)


def _read_chunked(rfile, cap):
    """Decode an HTTP/1.1 chunked request body under a byte cap.

    Raises _BodyTooLarge when the decoded body would exceed `cap` and
    ValueError when the framing is malformed. Trailers are consumed and
    discarded.
    """
    out = bytearray()
    while True:
        line = rfile.readline(65536)
        if not line:
            raise ValueError("missing chunk header")
        size_field = line.split(b";", 1)[0].strip()
        try:
            size = int(size_field, 16)
        except ValueError:
            raise ValueError(f"malformed chunk header {size_field!r}")
        if size == 0:
            while True:  # consume optional trailers
                trailer = rfile.readline(65536)
                if not trailer or trailer in (b"\r\n", b"\n"):
                    break
            return bytes(out)
        if len(out) + size > cap:
            raise _BodyTooLarge()
        chunk = _read_exact(rfile, size)
        if len(chunk) != size:
            raise ValueError("truncated chunk body")
        out += chunk
        rfile.readline(8)  # the CRLF that terminates the chunk


def _read_body(headers, rfile, cap):
    """Read the request body under a hard cap.

    Returns a (body, error) pair. `body` is None when the request carries
    no body. `error` is a (status, error_type, message) triple when the
    body must be rejected.
    """
    encoding = (headers.get("Transfer-Encoding") or "").lower()
    if "chunked" in encoding:
        try:
            return _read_chunked(rfile, cap), None
        except _BodyTooLarge:
            return None, (
                413,
                "PayloadTooLarge",
                f"zen-proxy: request body exceeds the {cap} byte limit",
            )
        except ValueError as exc:
            return None, (
                400,
                "BadRequest",
                f"zen-proxy: malformed chunked request body: {exc}",
            )
        except TimeoutError:
            return None, (
                408,
                "RequestTimeout",
                "zen-proxy: timed out reading the request body",
            )
    raw_length = headers.get("Content-Length")
    if raw_length is None:
        return None, None
    try:
        length = int(raw_length.strip())
    except (AttributeError, ValueError):
        return None, (400, "BadRequest", "zen-proxy: invalid Content-Length header")
    if length < 0:
        return None, (400, "BadRequest", "zen-proxy: invalid Content-Length header")
    if length > cap:
        return None, (
            413,
            "PayloadTooLarge",
            f"zen-proxy: request body of {length} bytes exceeds the {cap} byte limit",
        )
    try:
        body = _read_exact(rfile, length)
    except TimeoutError:
        return None, (
            408,
            "RequestTimeout",
            "zen-proxy: timed out reading the request body",
        )
    if len(body) != length:
        return None, (
            400,
            "BadRequest",
            "zen-proxy: request body shorter than Content-Length",
        )
    return (body or None), None


# A streamed response is only complete when it carries its terminal event.
# Without this check a stream that dies mid-reply is indistinguishable from
# a short but complete answer, and the caller believes it got a full turn.
_TERMINAL_PATTERNS = (
    re.compile(rb"response\.(completed|failed|incomplete)"),
    re.compile(rb"\[DONE\]"),
    re.compile(rb'"finish_reason"\s*:\s*"(?!null)'),
)


def _has_terminal_event(buffer):
    """True when the buffered SSE bytes carry a terminal event marker."""
    return any(pattern.search(buffer) for pattern in _TERMINAL_PATTERNS)


# Refreshed live 2026-11-08 (Go: 30 models, Zen: 45 models; authenticated
# with opencode UA + session). Go now includes crouton-alpha-free,
# iceman-contributor-free and longcat-2.0 — they work on BOTH
# /zen/go/v1/responses and /chat/completions (verified 2026-11-08 via
# proxy 7890 + oc_sk key). Zen's crouton-alpha-free is the same id but hits
# the free-tier account quota (429) — use the Go mount for it.
# Anthropic-/messages-only (claude-*) and single-endpoint models
# (gemini-*) stay out — no OpenAI-compatible client can use them.
GO_CHAT = {
    "beam-free",
    "crouton-alpha-free",
    "gemini-4-argon",
    "glm-5.2",
    "glm-5.3",
    "glm-5.3-flash",
    "iceman-contributor-free",
    "longcat-2.0",
    "mimo-v2.6-flash",
    "mimo-v2.6-pro",
    "minimax-m3",
    "minimax-m3.1-flash",
    "deepseek-v4-pro",
    "deepseek-v4.1-flash",
    "hy3",
    "hy4",
    "hy4-preview",
    "kimi-k2.7-code",
    "kimi-k3",
    "kimi-k3.1-pro",
    "qwen3.7-plus",
    "qwen3.8-flash",
    "qwen3.8-max",
    "step-5-preview",
}
GO_RESP = {
    "beam-free",
    "crouton-alpha-free",
    "gemini-4-argon",
    "glm-5.2",
    "glm-5.3",
    "glm-5.3-flash",
    "gpt-5.6-luna",
    "gpt-6-luna",
    "grok-4.7",
    "iceman-contributor-free",
    "longcat-2.0",
    "mimo-v2.6-flash",
    "mimo-v2.6-pro",
    "minimax-m3",
    "minimax-m3.1-flash",
    "muse-spark-1.3-contributor",
    "muse-spark-1.2-contributor",
    "deepseek-v4-pro",
    "deepseek-v4.1-flash",
    "hy3",
    "hy4",
    "hy4-preview",
    "kimi-k2.7-code",
    "kimi-k3",
    "kimi-k3.1-pro",
    "qwen3.7-plus",
    "qwen3.8-flash",
    "qwen3.8-max",
    "step-5-preview",
}

# Per-model context windows (tokens) are the caller's business: brain sizes
# its prompts from BRAIN_CONTEXT_WINDOW_TOKENS. WARNING: grok-4.7 accepts
# only 500000 — never send it a 1M-sized prompt, the server rejects it.
ZEN_CHAT = {
    "big-pickle",
    "nemotron-3.5-lightning-free",
    "nemotron-3.5-super-vl-free",
    "crouton-alpha-free",
    "iceman-free",
    "flint-40b-free",
    "inkling-2-small-free",
    "mimo-v2.6-flash-free",
}
ZEN_RESP = {
    "muse-spark-1.3-contributor-free",
    "muse-spark-1.2-contributor-free",
    "crouton-alpha-free",
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

    # Bounded reception: a client that connects and dribbles a body must
    # not hold a handler thread for the life of the process. The window is
    # reopened before a response is streamed (see _proxy_inner).
    timeout = CLIENT_RECEIVE_TIMEOUT_S

    def log_message(self, *args):
        pass  # one structured line per request is written by _log_request

    def _send_json(self, status, payload, req_id=None):
        """Answer with a JSON body and the headers a client needs."""
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if req_id:
            self.send_header("X-Request-Id", req_id)
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status, error_type, message, req_id=None):
        """Answer with the error envelope the clients parse."""
        self._send_json(
            status,
            {"type": "error", "error": {"type": error_type, "message": message}},
            req_id,
        )

    def _write_stream_error(self, error_type, message):
        """Report a mid-stream failure in band.

        The status line is already on the wire at this point, so the only
        honest signal left is an error event inside the stream itself.
        """
        payload = {"type": "error", "error": {"type": error_type, "message": message}}
        try:
            self.wfile.write(
                ("event: error\ndata: " + json.dumps(payload) + "\n\n").encode()
            )
            self.wfile.flush()
        except OSError:
            pass

    def _log_request(
        self, req_id, started, status, outcome, model, session_id, session_origin, sent
    ):
        """Write one structured line per request to stdout (the journal).

        The Authorization value, the request body and the response body are
        never written: this line is safe to keep in the journal.
        """
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = (
            f"ts={ts} req_id={req_id} method={self.command} path={self.path} "
            f"status={status} outcome={outcome} model={model or '-'} "
            f"duration_ms={round((time.monotonic() - started) * 1000)} "
            f"session={(session_id or '-')[:8]}({session_origin}) bytes={sent}"
        )
        try:
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
        except OSError:
            pass

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
                rest = self.path[len(prefix) :] or "/"
                self._proxy(base + rest, allow)
                return
        self.send_error(404, "unknown zen-proxy route")

    do_GET = _send_upstream
    do_POST = _send_upstream

    def _proxy(self, upstream_path, allow):
        """Relay one request upstream and answer the client.

        Every failure path answers with a parseable JSON error instead of
        dropping the socket, so the caller can tell a timeout from a
        rejected body from a refused connection.
        """
        req_id = uuid.uuid4().hex[:8]
        started = time.monotonic()
        state = {
            "status": 500,
            "outcome": "error",
            "model": None,
            "session_id": "",
            "session_origin": "client",
            "sent": 0,
        }
        try:
            return self._proxy_inner(req_id, started, upstream_path, allow, state)
        finally:
            self._log_request(
                req_id,
                started,
                state["status"],
                state["outcome"],
                state["model"],
                state["session_id"],
                state["session_origin"],
                state["sent"],
            )

    def _proxy_inner(self, req_id, started, upstream_path, allow, state):
        body, body_error = _read_body(self.headers, self.rfile, MAX_BODY_BYTES)
        if body_error:
            status, error_type, message = body_error
            state["status"] = status
            state["outcome"] = "rejected"
            self._send_error(status, error_type, message, req_id)
            return
        # A streamed response can outlive the bounded reception window, so
        # the window is widened to the upstream timeout for the response
        # phase. It is not cleared: a client that stops reading must not
        # hold this handler thread forever, or the drain would have to kill
        # the process with a turn still in flight.
        self.connection.settimeout(UPSTREAM_TIMEOUT)
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
                    state["status"] = 404
                    state["outcome"] = "model_not_served"
                    state["model"] = _mid
                    self._send_error(
                        404,
                        "ModelNotServedHere",
                        (
                            f"zen-proxy: model '{_mid}' is not served on "
                            f"{self.path};"
                            + (
                                f" use {_hint} instead."
                                if _hint
                                else " it is on no known route (check upstream list)."
                            )
                        ),
                        req_id,
                    )
                    return
        record = None
        if AUDIT and self.command == "POST":
            record = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "req_id": req_id,
                "method": self.command,
                "route": self.path,
                "upstream": upstream_path,
                "auth_present": bool(self.headers.get("Authorization")),
                "model": None,
                "stream": None,
                "effort_in": None,  # top-level reasoning_effort as received
                "effort_out": None,  # reasoning.effort as sent upstream
                "translated": False,
            }
        if self.command == "POST" and body and upstream_path.endswith("/responses"):
            try:
                payload = json.loads(body)
            except ValueError:
                payload = None
            if isinstance(payload, dict):
                state["model"] = payload.get("model")
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
        elif body:
            try:
                payload = json.loads(body)
            except ValueError:
                payload = None
            if isinstance(payload, dict):
                state["model"] = payload.get("model")
                if record is not None:
                    record["model"] = payload.get("model")
                    record["stream"] = payload.get("stream")
                    record["effort_in"] = payload.get("reasoning_effort")
        # Identity: a client that already carries a session keeps it, every
        # other caller gets a fresh one per request (Hermes recipe), so the
        # gateway never sees one shared session standing in for all traffic.
        client_session = self.headers.get("x-opencode-session") or self.headers.get(
            "X-Session-ID"
        )
        if client_session:
            minted_session = client_session
            state["session_origin"] = "client"
        else:
            minted_session = str(uuid.uuid4())
            state["session_origin"] = "injected"
        state["session_id"] = minted_session
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
        for h in (
            "x-opencode-client",
            "x-opencode-request",
            "x-opencode-request-id",
            "x-opencode-project",
        ):
            v = self.headers.get(h)
            if v:
                out_headers[h] = v
        req = urllib.request.Request(
            UPSTREAM + upstream_path,
            data=body,
            method=self.command,
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
            state["status"] = 502
            state["outcome"] = "egress_failed"
            self._send_error(
                502,
                "BadGatewayError",
                f"zen-proxy: upstream unreachable: {e.reason}",
                req_id,
            )
            return
        except TimeoutError as e:
            # The upstream did not answer inside the socket timeout. This
            # used to escape both handlers and drop the socket with no
            # status, which the caller saw as "Server disconnected without
            # sending a response".
            state["status"] = 504
            state["outcome"] = "timeout"
            self._send_error(
                504,
                "GatewayTimeout",
                (
                    f"zen-proxy: upstream did not respond within "
                    f"{UPSTREAM_TIMEOUT:g}s ({e})"
                ),
                req_id,
            )
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
                state["status"] = status
                state["outcome"] = "ok"
                state["sent"] = len(raw)
                self.send_response(status)
                self.send_header("Content-Type", ctype or "application/octet-stream")
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("X-Request-Id", req_id)
                self.end_headers()
                self.wfile.write(raw)
                return
            data["data"] = [m for m in data.get("data", []) if m.get("id") in allow]
            out = json.dumps(data).encode()
            state["status"] = status
            state["outcome"] = "ok"
            state["sent"] = len(out)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.send_header("X-Request-Id", req_id)
            self.end_headers()
            self.wfile.write(out)
            return

        state["status"] = status
        self.send_response(status)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("X-Request-Id", req_id)
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
                    AUDIT_DIR, f"audit-{ts_fname}-resp.sse"
                )
                # The capture file stays open across the relay, so it is
                # closed by hand in the finally block below.
                cap = open(record["resp_capture"], "wb")  # noqa: SIM115
            except OSError:
                cap = None
        sent = 0
        tail = bytearray()
        is_sse = "text/event-stream" in ctype
        failure = None
        try:
            while True:
                try:
                    chunk = stream.read(8192)
                except TimeoutError as e:
                    # The upstream went silent mid-reply. The status line is
                    # already on the wire, so the failure is reported in band.
                    failure = (
                        "UpstreamStreamTimeout",
                        (
                            "zen-proxy: upstream stalled for more than "
                            f"{UPSTREAM_TIMEOUT:g}s while streaming ({e})"
                        ),
                    )
                    break
                except OSError as e:
                    failure = (
                        "UpstreamStreamError",
                        f"zen-proxy: upstream stream failed ({e})",
                    )
                    break
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError) as e:
                    # The client hung up. Stop the upstream read so an
                    # unread turn stops consuming quota.
                    state["outcome"] = "client_gone"
                    failure = (
                        "ClientDisconnected",
                        f"zen-proxy: client disconnected ({e})",
                    )
                    break
                except TimeoutError as e:
                    # The client stopped reading and the write window
                    # expired. Same outcome as a disconnect.
                    state["outcome"] = "client_gone"
                    failure = (
                        "ClientDisconnected",
                        f"zen-proxy: client stopped reading ({e})",
                    )
                    break
                sent += len(chunk)
                if is_sse:
                    tail += chunk
                    if len(tail) > 65536:
                        del tail[:-32768]
                if cap is not None:
                    if sent <= AUDIT_MAX_BYTES:
                        cap.write(chunk)
                    else:
                        cap.write(b"\n...[truncated]\n")
                        cap.close()
                        cap = None
        finally:
            stream.close()
            if cap is not None:
                cap.close()
        if failure is not None and state["outcome"] == "client_gone":
            # The client is gone. There is nothing left to signal on the
            # wire; the only record is the journal line, and a disconnect
            # must never be rewritten into a clean end.
            pass
        elif failure is not None:
            error_type, message = failure
            self._write_stream_error(error_type, message)
            state["outcome"] = "stream_truncated"
            state["status"] = 502
        elif is_sse and sent and not _has_terminal_event(bytes(tail)):
            # The stream ended without its terminal event, so the turn was
            # cut short. Reporting it as a clean end would let the caller
            # believe it received a complete answer.
            self._write_stream_error(
                "UpstreamStreamTruncated",
                "zen-proxy: upstream stream ended without its terminal event",
            )
            state["outcome"] = "stream_truncated"
            state["status"] = 502
        else:
            state["outcome"] = "ok"
        state["sent"] = sent
        if record is not None:
            record["resp_bytes"] = sent
            record["outcome"] = state["outcome"]
            record["duration_ms"] = round((time.monotonic() - started) * 1000)
            _audit_write(record, req_body=body)


class ZenProxyServer(ThreadingHTTPServer):
    """Threading server that can be drained instead of killed.

    `daemon_threads` is off and `block_on_close` is on, so `server_close`
    waits for the in-flight handlers to finish. That is what makes a
    SIGTERM graceful: the listener stops first, the running turns are
    allowed to complete.
    """

    daemon_threads = False
    block_on_close = True
    allow_reuse_address = True


def _drain_watchdog():
    """Force the process to exit when the drain deadline expires.

    A wedged upstream must not keep the unit from restarting, so the
    drain is bounded: after the deadline the process leaves on its own.
    """
    time.sleep(DRAIN_TIMEOUT_S)
    sys.stdout.write(
        f"ts={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} "
        f"event=drain_timeout seconds={DRAIN_TIMEOUT_S} action=exit\n"
    )
    sys.stdout.flush()
    os._exit(0)


def _install_signal_handlers(server):
    """Stop the listener on SIGTERM/SIGINT and let the turns finish."""

    def _shutdown(signum, _frame):
        sys.stdout.write(
            f"ts={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} "
            f"event=signal signal={signal.Signals(signum).name} action=drain\n"
        )
        sys.stdout.flush()
        # shutdown() blocks until serve_forever() returns, so it must not
        # run on the thread that is inside serve_forever().
        threading.Thread(target=server.shutdown, daemon=True).start()
        if DRAIN_TIMEOUT_S > 0:
            threading.Thread(target=_drain_watchdog, daemon=True).start()

    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, _shutdown)


if __name__ == "__main__":
    _server = ZenProxyServer(("127.0.0.1", 8081), Handler)
    _install_signal_handlers(_server)
    try:
        _server.serve_forever()
    finally:
        # server_close() joins the in-flight handlers: the drain.
        _server.server_close()
