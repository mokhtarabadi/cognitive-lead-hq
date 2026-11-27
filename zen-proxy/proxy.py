#!/usr/bin/env python3
"""Enhanced zen-proxy — pure Python stdlib, no external dependencies.

Purpose: let paid OpenCode Go models be used anywhere (especially the Brain)
through a single local endpoint that behaves like the real OpenCode client.

Features:
  * HTTP CONNECT proxy support (works as a normal HTTP proxy).
  * Reverse-proxy endpoints: responses API, chat completions, model list,
    discovery, transparent passthrough.
  * Caller supplies model + prompt + API key (Authorization header).
  * OpenCode-v2 reverse-engineered identity headers generated ONCE at process
    start and cached; new values on each restart.
  * No API key stored in the project; caller Authorization wins, optional
    process env BRAIN_API_KEY / OPENCODE_API_KEY as fallback.
  * No free models. No allowlists. No Python dependencies beyond stdlib.

Endpoints:
  GET  /health                                    local status
  POST /v1/responses, /responses                  /zen/go/v1/responses
  POST /v1/chat/completions, /chat/completions    /zen/go/v1/chat/completions
  GET  /v1/models, /models                        /zen/go/v1/models
  GET  /api.json, /experimental/v2.0/api.json     models.opencode.ai discovery
  ANY  /zen/*, /inference/*, /*                   transparent passthrough
  CONNECT host:port                              raw TCP tunnel (HTTP proxy)
"""

from __future__ import annotations

import os
import re
import secrets
import socket
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# --------------------------------------------------------------------------
# Config (environment injected externally, no project .env is read here)
# --------------------------------------------------------------------------
BASE = os.environ.get("OPENCODE_BASE", "https://opencode.ai").rstrip("/")
MODELS_HOST = os.environ.get(
    "OPENCODE_MODELS_HOST", "https://models.opencode.ai"
).rstrip("/")
PORT = int(os.environ.get("PORT", "8081"))
CLIENT = os.environ.get("OPENCODE_CLIENT", "cli")
CHANNEL = os.environ.get("OPENCODE_CHANNEL", "latest")
VERSION = os.environ.get("OPENCODE_VERSION", "2.3.2")
NAME = os.environ.get("OPENCODE_NAME", "cli")
PROJECT_ID = os.environ.get("OPENCODE_PROJECT_ID", "global")
TIMEOUT = float(os.environ.get("UPSTREAM_TIMEOUT_SEC", "900"))
MAX_BODY_BYTES = int(os.environ.get("ZEN_PROXY_MAX_BODY_BYTES", "33554432"))


# --------------------------------------------------------------------------
# OpenCode-v2 identity, generated once per process and cached (never rebuilt
# per request). Restart produces fresh values.
# --------------------------------------------------------------------------
def _hex(n: int) -> str:
    return secrets.token_hex(n)


SESSION = "ses_" + _hex(32) + _hex(32)
REQ_PREFIX = _hex(16)
TRACE_ID = _hex(16)
SPAN_ID = _hex(8)
PARENT_SPAN_ID = _hex(8)
B3 = f"{TRACE_ID}-{SPAN_ID}-1-{PARENT_SPAN_ID}"
TRACEPARENT = f"00-{TRACE_ID}-{SPAN_ID}-01"
USER_AGENT = f"opencode/{CHANNEL}/{VERSION}/{NAME}"
HOST_RE = re.compile(r"^[A-Za-z0-9.\-]+$")
ALLOWED_CONNECT_HOSTS = {"opencode.ai", "models.opencode.ai"}
ALLOWED_CONNECT_PORTS = {80, 443}


def identity_headers(
    content_len: int | None, caller_auth: str | None
) -> dict[str, str]:
    """Build the cached OpenCode identity header set for one upstream request."""
    auth = caller_auth
    if not auth:
        env_key = os.environ.get("BRAIN_API_KEY") or os.environ.get("OPENCODE_API_KEY")
        auth = f"Bearer {env_key}" if env_key else None
    headers = {
        "Accept": "*/*",
        "x-opencode-client": CLIENT,
        "x-opencode-project": PROJECT_ID,
        "x-opencode-session": SESSION,
        "x-opencode-session-id": SESSION,
        "x-session-affinity": SESSION,
        "X-Session-Id": SESSION,
        "x-session-id": SESSION,
        "x-opencode-channel": CHANNEL,
        "x-opencode-version": VERSION,
        "x-opencode-request": REQ_PREFIX + "-" + _hex(16),
        "x-opencode-request-id": _hex(16),
        "User-Agent": USER_AGENT,
        "b3": B3,
        "traceparent": TRACEPARENT,
    }
    if auth:
        headers["Authorization"] = auth
    if content_len:
        headers["Content-Type"] = "application/json"
        headers["Content-Length"] = str(content_len)
    return headers


def map_path(path: str) -> str | None:
    """Map a caller path to the real OpenCode upstream path."""
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    if path == "/health":
        return None
    if path in ("/v1/chat/completions", "/chat/completions"):
        return f"{BASE}/zen/go/v1/chat/completions"
    if path in ("/v1/models", "/models"):
        return f"{BASE}/zen/go/v1/models"
    if path in ("/api.json", "/experimental/v2.0/api.json"):
        return f"{MODELS_HOST}/experimental/v2.0/api.json"
    if path in ("/responses", "/v1/responses"):
        return f"{BASE}/zen/go/v1/responses"
    if path.startswith(("/zen/", "/inference/")):
        return f"{BASE}{path}"
    return f"{BASE}{path}"


def _strip_bad_response_headers(headers: dict[str, str]) -> dict[str, str]:
    """Case-insensitive single-pass strip; preserves content-encoding unchanged.

    Drops only framing/hop headers we recompute ourselves; `content-encoding`
    is forwarded unchanged so the client decodes correctly.
    """
    drop = {
        "transfer-encoding",
        "content-length",
        "connection",
        "server",
        "date",
        "cf-ray",
        "cf-placement",
    }
    return {k: v for k, v in headers.items() if k.lower() not in drop}


class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, fmt: str, *args) -> None:
        pass  # keep the service log quiet

    # ---- HTTP CONNECT: raw bidirectional TCP tunnel -----------------------
    def do_CONNECT(self) -> None:
        target = self.path
        if target.startswith("http://") or target.startswith("https://"):
            parsed_target = urllib.parse.urlsplit(target)
            host = parsed_target.hostname or ""
            port = parsed_target.port or (443 if target.startswith("https://") else 80)
        else:
            try:
                host, port_s = target.rsplit(":", 1)
                port = int(port_s)
            except (ValueError, TypeError):
                header_host = (self.headers.get("Host") or "").split(":", 1)[0].lower()
                if header_host and header_host not in ALLOWED_CONNECT_HOSTS:
                    self.send_error(403, "CONNECT target not allowed")
                else:
                    self.send_error(400, "Bad CONNECT target")
                return
        host = host.lower()
        if not HOST_RE.match(host):
            self.send_error(400, "Bad CONNECT host")
            return
        if host not in ALLOWED_CONNECT_HOSTS or port not in ALLOWED_CONNECT_PORTS:
            self.send_error(403, "CONNECT target not allowed")
            return
        # If an upstream HTTP proxy is configured (e.g. ~/.config/openchamber/startup.env),
        # tunnel through it; otherwise connect directly. Direct-only hosts are
        # honoured via no_proxy so loopback never loops through the proxy.
        pending = None
        proxy_url = (
            os.environ.get("https_proxy")
            or os.environ.get("HTTPS_PROXY")
            or os.environ.get("http_proxy")
            or os.environ.get("HTTP_PROXY")
            or ""
        )
        try:
            if proxy_url:
                p = urllib.parse.urlsplit(proxy_url)
                proxy_host = p.hostname or ""
                proxy_port = p.port or (443 if p.scheme == "https" else 80)
                upstream = socket.create_connection(
                    (proxy_host, proxy_port), timeout=10
                )
                connect_req = (
                    f"CONNECT {host}:{port} HTTP/1.1\r\n"
                    f"Host: {host}:{port}\r\n"
                    f"Proxy-Connection: Keep-Alive\r\n\r\n"
                ).encode("ascii")
                upstream.sendall(connect_req)
                response = b""
                while b"\r\n\r\n" not in response and len(response) < 8192:
                    chunk = upstream.recv(4096)
                    if not chunk:
                        raise OSError("upstream proxy closed during CONNECT")
                    response += chunk
                status_line = response.split(b"\r\n", 1)[0].decode("latin1")
                if " 200 " not in status_line:
                    upstream.close()
                    raise OSError(f"upstream proxy CONNECT failed: {status_line}")
                head, _, tail = response.partition(b"\r\n\r\n")
                # Keep any bytes read past the CONNECT header so the TLS handshake
                # that may already be in flight is not lost.
                pending = tail if tail else None
            else:
                upstream = socket.create_connection((host, port), timeout=10)
        except OSError as exc:
            self.send_error(502, f"upstream connect failed: {exc}")
            return
        self.wfile.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        self.wfile.flush()

        def relay(src: socket.socket, dst: socket.socket) -> None:
            try:
                while True:
                    data = src.recv(65536)
                    if not data:
                        break
                    dst.sendall(data)
            except OSError:
                pass
            finally:
                try:
                    dst.shutdown(socket.SHUT_WR)
                except OSError:
                    pass

        client_sock = self.connection
        if pending:
            try:
                client_sock.sendall(pending)
            except OSError:
                pass
        t = threading.Thread(target=relay, args=(upstream, client_sock), daemon=True)
        t.start()
        try:
            relay(client_sock, upstream)
        finally:
            t.join(timeout=2)
            upstream.close()

    # ---- reverse proxy endpoints -----------------------------------------
    def _proxy(self) -> None:
        parsed = urllib.parse.urlsplit(self.path)
        upstream = map_path(parsed.path)
        if upstream is None:
            if parsed.path == "/health":
                key_present = bool(
                    self.headers.get("Authorization")
                    or os.environ.get("BRAIN_API_KEY")
                    or os.environ.get("OPENCODE_API_KEY")
                )
                body = (
                    '{"status":"ok","base":"'
                    + BASE
                    + '","models_host":"'
                    + MODELS_HOST
                    + '","project":"'
                    + PROJECT_ID
                    + '","session":"'
                    + SESSION
                    + '","key_present":'
                    + ("true" if key_present else "false")
                    + ',"connect":true}'
                ).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.send_header("Connection", "close")
                self.end_headers()
            return
        if parsed.query:
            upstream += "?" + parsed.query
        transfer_encoding = (self.headers.get("Transfer-Encoding") or "").lower()
        if "chunked" in transfer_encoding:
            payload = b'{"error":"BadRequest","message":"chunked transfer-encoding is not supported"}'
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(payload)
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except (TypeError, ValueError):
            payload = b'{"error":"BadRequest","message":"invalid Content-Length"}'
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(payload)
            return
        if length < 0:
            payload = b'{"error":"BadRequest","message":"negative Content-Length"}'
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(payload)
            return
        if length > MAX_BODY_BYTES:
            payload = (
                b'{"error":"PayloadTooLarge","message":"request body exceeds cap"}'
            )
            self.send_response(413)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(payload)
            return
        body = self.rfile.read(length) if length else b""
        headers = identity_headers(
            len(body) if body else None, self.headers.get("Authorization")
        )
        caller_ct = self.headers.get("Content-Type")
        if caller_ct:
            headers["Content-Type"] = caller_ct
        req = urllib.request.Request(
            upstream, data=body if body else None, headers=headers, method=self.command
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                raw = resp.read()
                status = resp.status
                resp_headers = dict(resp.headers.items())
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            status = exc.code
            resp_headers = dict(exc.headers.items()) if exc.headers else {}
        except urllib.error.URLError as exc:
            reason = exc.reason
            if isinstance(reason, (TimeoutError, socket.timeout)) or (
                "timed out" in str(reason).lower() or "timeout" in str(reason).lower()
            ):
                payload = (
                    '{"error":"GatewayTimeout","message":"'
                    + str(reason).replace('"', "'")
                    + '"}'
                ).encode()
                self.send_response(504)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(payload)
                return
            payload = (
                '{"error":"BadGatewayError","message":"'
                + str(reason).replace('"', "'")
                + '"}'
            ).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(payload)
            return
        except (TimeoutError, socket.timeout) as exc:
            payload = (
                '{"error":"GatewayTimeout","message":"'
                + str(exc).replace('"', "'")
                + '"}'
            ).encode()
            self.send_response(504)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(payload)
            return
        self.send_response(status)
        for key, value in _strip_bad_response_headers(resp_headers).items():
            if key.lower() in (
                "connection",
                "server",
                "date",
                "cf-ray",
                "cf-placement",
            ):
                continue
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Connection", "close")
        self.end_headers()
        # Always write the upstream response body, including GET requests.
        try:
            self.wfile.write(raw)
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self) -> None:
        self._proxy()

    def do_POST(self) -> None:
        self._proxy()

    def do_PUT(self) -> None:
        self._proxy()

    def do_DELETE(self) -> None:
        self._proxy()

    def do_PATCH(self) -> None:
        self._proxy()


class ThreadingProxy(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main() -> None:
    server = ThreadingProxy(("127.0.0.1", PORT), ProxyHandler)
    print(f"zen-proxy (python, enhanced) on :{PORT} -> {BASE}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
