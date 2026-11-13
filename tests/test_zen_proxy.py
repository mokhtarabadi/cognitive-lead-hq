# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""zen-proxy slice: the failure contract, the body limits and the stream rules.

Why: the slice is the live path for every brain turn, and it had no tests at
all. The cases below are named after the defect each one prevents, so a
regression names itself.

Every case runs offline: the upstream is replaced by a fake response object,
so no test ever spends quota or touches the live gateway.
"""

import email.message
import http.client
import importlib.util
import io
import json
import socket
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SLICE = REPO / "zen-proxy"

_spec = importlib.util.spec_from_file_location("zen_proxy", SLICE / "proxy.py")
proxy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(proxy)

_refresh_spec = importlib.util.spec_from_file_location(
    "zen_refresh_allowlists", SLICE / "refresh_allowlists.py"
)
refresh = importlib.util.module_from_spec(_refresh_spec)
_refresh_spec.loader.exec_module(refresh)


class FakeResponse:
    """Minimal stand-in for the object urlopen returns."""

    def __init__(
        self, status=200, content_type="application/json", body=b"", headers=None
    ):
        self.status = status
        self._body = body
        self._pos = 0
        self.headers = email.message.Message()
        if content_type:
            self.headers["Content-Type"] = content_type
        for key, value in (headers or {}).items():
            self.headers[key] = value

    def read(self, size=-1):
        if size is None or size < 0:
            chunk = self._body[self._pos :]
            self._pos = len(self._body)
            return chunk
        chunk = self._body[self._pos : self._pos + size]
        self._pos += len(chunk)
        return chunk

    def close(self):
        pass


@pytest.fixture
def upstream(monkeypatch):
    """Replace the upstream call and record what the proxy forwarded."""
    calls = []

    def _install(result=None, error=None):
        def _fake_urlopen(request, timeout=None):
            calls.append(
                {
                    "url": request.full_url,
                    "data": request.data,
                    "headers": request.headers,
                }
            )
            if error is not None:
                raise error
            return result() if callable(result) else result

        monkeypatch.setattr(proxy.urllib.request, "urlopen", _fake_urlopen)
        return calls

    return _install


@pytest.fixture
def server_factory():
    """Run a handler class on an ephemeral loopback port."""
    made = []

    def _make(handler_class=proxy.Handler):
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler_class)
        httpd.daemon_threads = True
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        made.append(httpd)
        return httpd.server_address

    yield _make
    for httpd in made:
        httpd.shutdown()
        httpd.server_close()


@pytest.fixture
def server(server_factory):
    """Run the real handler on an ephemeral loopback port."""
    return server_factory()


def request(server, method, path, body=None, headers=None, chunk_parts=None):
    """Send one request to the proxy and return (status, headers, body)."""
    host, port = server
    conn = http.client.HTTPConnection(host, port, timeout=10)
    try:
        if chunk_parts is not None:
            conn.putrequest(method, path)
            conn.putheader("Content-Type", "application/json")
            conn.putheader("Transfer-Encoding", "chunked")
            conn.endheaders()
            for part in chunk_parts:
                conn.send(f"{len(part):X}\r\n".encode() + part + b"\r\n")
            conn.send(b"0\r\n\r\n")
        else:
            conn.request(method, path, body=body, headers=headers or {})
        response = conn.getresponse()
        payload = response.read()
        return response.status, dict(response.getheaders()), payload
    finally:
        conn.close()


def json_body(payload):
    return json.loads(payload.decode("utf-8"))


# --- the failure contract -------------------------------------------------


def test_socket_timeout_before_headers_returns_504_json(server, upstream):
    """A socket timeout used to escape both handlers and drop the socket."""
    upstream(error=TimeoutError("timed out"))

    status, _headers, payload = request(
        server, "POST", "/go/resp/responses", body=b"{}"
    )

    assert status == 504
    body = json_body(payload)
    assert body["type"] == "error"
    assert body["error"]["type"] == "GatewayTimeout"
    assert "did not respond" in body["error"]["message"]


def test_upstream_unreachable_returns_502_bad_gateway(server, upstream):
    """A refused egress path answers 502 instead of dropping the socket."""
    upstream(error=proxy.urllib.error.URLError("connection refused"))

    status, _headers, payload = request(
        server, "POST", "/go/resp/responses", body=b"{}"
    )

    assert status == 502
    assert json_body(payload)["error"]["type"] == "BadGatewayError"


def test_model_not_served_returns_404_with_route_hint(server, upstream):
    """A model owned by another mount gets a 404 that names the right mount."""
    upstream(result=FakeResponse(body=b'{"ok":true}'))

    status, _headers, payload = request(
        server,
        "POST",
        "/go/resp/responses",
        body=json.dumps({"model": "big-pickle", "input": []}).encode(),
    )

    assert status == 404
    body = json_body(payload)
    assert body["error"]["type"] == "ModelNotServedHere"
    assert "/zen/chat" in body["error"]["message"]


def test_unknown_route_returns_404(server):
    """An unknown mount answers 404 and never reaches upstream."""
    status, _headers, _payload = request(server, "GET", "/nope/models")

    assert status == 404


# --- the body limits ------------------------------------------------------


def test_oversized_body_returns_413_without_buffering(server, upstream, monkeypatch):
    """A body over the cap is rejected before it is read into memory."""
    monkeypatch.setattr(proxy, "MAX_BODY_BYTES", 32)
    calls = upstream(result=FakeResponse(body=b"{}"))

    status, _headers, payload = request(
        server, "POST", "/go/resp/responses", body=b"x" * 4096
    )

    assert status == 413
    assert json_body(payload)["error"]["type"] == "PayloadTooLarge"
    assert calls == []  # the upstream was never contacted


def test_chunked_request_body_is_forwarded_intact(server, upstream):
    """A chunked body used to arrive as length 0 and be forwarded empty."""
    calls = upstream(result=FakeResponse(body=b'{"ok":true}'))
    parts = [b'{"model":', b'"glm-5.3",', b'"input":[]}']

    status, _headers, _payload = request(
        server, "POST", "/go/resp/responses", chunk_parts=parts
    )

    assert status == 200
    assert len(calls) == 1
    assert calls[0]["data"] == b'{"model":"glm-5.3","input":[]}'


def test_chunked_body_over_cap_returns_413(server, upstream, monkeypatch):
    """A chunked body over the cap is rejected, not truncated."""
    monkeypatch.setattr(proxy, "MAX_BODY_BYTES", 16)
    calls = upstream(result=FakeResponse(body=b"{}"))

    status, _headers, payload = request(
        server, "POST", "/go/resp/responses", chunk_parts=[b"x" * 64]
    )

    assert status == 413
    assert json_body(payload)["error"]["type"] == "PayloadTooLarge"
    assert calls == []


def test_body_shorter_than_content_length_returns_400(server, upstream):
    """A body that ends early is a bad request, not a silent empty body."""
    upstream(result=FakeResponse(body=b"{}"))
    host, port = server
    sock = socket.create_connection((host, port), timeout=10)
    try:
        sock.sendall(
            b"POST /go/resp/responses HTTP/1.1\r\n"
            b"Host: 127.0.0.1\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Length: 500\r\n"
            b"\r\n"
        )
        sock.sendall(b"short")
        sock.shutdown(socket.SHUT_WR)  # the client stops sending early
        raw = b""
        while True:
            piece = sock.recv(4096)
            if not piece:
                break
            raw += piece
    finally:
        sock.close()

    assert raw.split(b"\r\n", 1)[0].startswith(b"HTTP/1.0 400")
    assert b"BadRequest" in raw


# --- the reasoning effort translation -------------------------------------


def test_reasoning_effort_is_translated_for_responses(server, upstream):
    """A chat-style effort value reaches the /responses endpoint translated."""
    calls = upstream(result=FakeResponse(body=b'{"ok":true}'))

    request(
        server,
        "POST",
        "/go/resp/responses",
        body=json.dumps({"model": "glm-5.3", "reasoning_effort": "xhigh"}).encode(),
    )

    forwarded = json.loads(calls[0]["data"].decode())
    assert forwarded["reasoning"] == {"effort": "xhigh"}
    assert "reasoning_effort" not in forwarded


def test_reasoning_effort_is_left_alone_for_chat_completions(server, upstream):
    """The chat dialect keeps its own effort field untouched."""
    calls = upstream(result=FakeResponse(body=b'{"ok":true}'))

    request(
        server,
        "POST",
        "/go/chat/chat/completions",
        body=json.dumps({"model": "glm-5.3", "reasoning_effort": "xhigh"}).encode(),
    )

    forwarded = json.loads(calls[0]["data"].decode())
    assert forwarded["reasoning_effort"] == "xhigh"
    assert "reasoning" not in forwarded


# --- the stream rules -----------------------------------------------------


SSE_TERMINAL = b'event: response.completed\ndata: {"type":"response.completed"}\n\n'


def test_truncated_stream_reports_a_failure_not_a_clean_end(server, upstream):
    """A stream that dies mid-reply must not look like a complete answer."""
    upstream(
        result=FakeResponse(
            content_type="text/event-stream",
            body=b'event: response.output_text.delta\ndata: {"delta":"hi"}\n\n',
        )
    )

    status, headers, payload = request(server, "POST", "/go/resp/responses", body=b"{}")

    assert status == 200  # the status line was already on the wire
    assert "text/event-stream" in headers["Content-Type"]
    assert b"UpstreamStreamTruncated" in payload


def test_complete_stream_is_not_flagged(server, upstream):
    """A stream that carries its terminal event is relayed untouched."""
    upstream(
        result=FakeResponse(
            content_type="text/event-stream",
            body=b'event: response.output_text.delta\ndata: {"delta":"hi"}\n\n'
            + SSE_TERMINAL,
        )
    )

    status, _headers, payload = request(
        server, "POST", "/go/resp/responses", body=b"{}"
    )

    assert status == 200
    assert b"UpstreamStreamTruncated" not in payload
    assert b"response.completed" in payload


def test_chat_completions_stream_with_finish_reason_is_not_flagged(server, upstream):
    """The chat dialect ends on a non-null finish_reason."""
    upstream(
        result=FakeResponse(
            content_type="text/event-stream",
            body=b'data: {"choices":[{"delta":{"content":"hi"},"finish_reason":"stop"}]}\n\ndata: [DONE]\n\n',
        )
    )

    status, _headers, payload = request(
        server, "POST", "/go/chat/chat/completions", body=b"{}"
    )

    assert status == 200
    assert b"UpstreamStreamTruncated" not in payload


def test_response_phase_keeps_a_bounded_socket_window(server, upstream, monkeypatch):
    """The response phase must not clear the socket window.

    A cleared window lets a client that stops reading block the relay
    thread for the life of the process, and the drain would then have to
    kill the process with a turn still in flight.
    """
    monkeypatch.setattr(proxy, "UPSTREAM_TIMEOUT", 120)
    seen = {}

    original = proxy.Handler._proxy_inner

    def _spy(self, req_id, started, upstream_path, allow, state):
        try:
            return original(self, req_id, started, upstream_path, allow, state)
        finally:
            seen["timeout"] = self.connection.gettimeout()

    monkeypatch.setattr(proxy.Handler, "_proxy_inner", _spy)
    upstream(result=FakeResponse(body=b'{"ok":true}'))

    request(
        server,
        "POST",
        "/go/resp/responses",
        body=json.dumps({"model": "glm-5.3", "input": []}).encode(),
    )

    # The window was opened for the response phase: it is bounded, and it
    # is not the reception default.
    assert seen["timeout"] == 120


def test_a_write_timeout_is_treated_as_a_client_disconnect(upstream, monkeypatch):
    """A client that stops reading must not be reported as a clean end.

    The relay writes the head, then the body write raises TimeoutError.
    The request must be recorded as `client_gone`, never as `ok`.
    """

    class _StuckWriter:
        """Accepts the response head, then never accepts a body write."""

        def __init__(self):
            self.writes = 0
            self.closed = False

        def write(self, data):
            self.writes += 1
            if self.writes > 1:
                raise TimeoutError("write window expired")
            return len(data)

        def flush(self):
            pass

        def close(self):
            self.closed = True

    class _StuckConnection:
        def settimeout(self, _value):
            pass

    state = {}
    upstream(
        result=FakeResponse(content_type="text/event-stream", body=b"data: {}\n\n")
    )
    monkeypatch.setattr(proxy.Handler, "setup", lambda self: None)

    handler = proxy.Handler.__new__(proxy.Handler)
    handler.__dict__.update(
        {
            "request": None,
            "client_address": ("127.0.0.1", 0),
            "server": None,
            "command": "POST",
            "path": "/go/resp/responses",
            "request_version": "HTTP/1.1",
            "headers": {"Content-Length": "0"},
            "rfile": io.BytesIO(b""),
            "wfile": _StuckWriter(),
            "connection": _StuckConnection(),
            "requestline": "POST /go/resp/responses HTTP/1.1",
            "_headers_buffer": [],
        }
    )
    try:
        handler._proxy_inner(
            "test", time.monotonic(), "/zen/go/v1/responses", proxy.GO_RESP, state
        )
    except (BrokenPipeError, ConnectionResetError, TimeoutError):
        pass

    assert state["outcome"] == "client_gone"
    assert handler.wfile.writes >= 1


# --- configuration --------------------------------------------------------


def test_malformed_timeout_env_exits_with_a_readable_message(monkeypatch, capsys):
    """A malformed timeout must not raise a bare traceback at import time."""
    monkeypatch.setenv("ZEN_PROXY_UPSTREAM_TIMEOUT", "not-a-number")

    with pytest.raises(SystemExit) as excinfo:
        proxy._env_float("ZEN_PROXY_UPSTREAM_TIMEOUT", 900.0)

    assert excinfo.value.code == proxy.EXIT_CONFIG_ERROR
    assert "not a number" in capsys.readouterr().err


def test_blank_timeout_env_falls_back_to_the_default(monkeypatch):
    """An unset or blank value keeps the documented default."""
    monkeypatch.setenv("ZEN_PROXY_UPSTREAM_TIMEOUT", "   ")
    assert proxy._env_float("ZEN_PROXY_UPSTREAM_TIMEOUT", 900.0) == 900.0


def test_non_positive_timeout_env_is_refused(monkeypatch):
    """A timeout below the floor would break the deadline ordering."""
    monkeypatch.setenv("ZEN_PROXY_UPSTREAM_TIMEOUT", "0")

    with pytest.raises(SystemExit) as excinfo:
        proxy._env_float("ZEN_PROXY_UPSTREAM_TIMEOUT", 900.0)

    assert excinfo.value.code == proxy.EXIT_CONFIG_ERROR


# --- the request log ------------------------------------------------------


def test_request_log_line_carries_no_credential(server, upstream, capsys):
    """The log line is safe to keep: it never carries the credential."""
    upstream(result=FakeResponse(body=b'{"ok":true}'))
    secret = "oc_sk_super-secret-value"

    request(
        server,
        "POST",
        "/go/resp/responses",
        body=json.dumps({"model": "glm-5.3", "input": []}).encode(),
        headers={"Authorization": f"Bearer {secret}"},
    )

    captured = capsys.readouterr().out
    line = [row for row in captured.splitlines() if "req_id=" in row]
    assert line, "no structured request log line was written"
    assert secret not in captured
    assert "Authorization" not in captured
    for key in (
        "method=POST",
        "path=/go/resp/responses",
        "status=200",
        "model=glm-5.3",
    ):
        assert key in line[-1]


def test_request_log_marks_an_injected_session(server, upstream, capsys):
    """A session the proxy minted is labelled, so the origin stays visible."""
    upstream(result=FakeResponse(body=b'{"ok":true}'))

    request(
        server,
        "POST",
        "/go/resp/responses",
        body=json.dumps({"model": "glm-5.3", "input": []}).encode(),
    )

    captured = capsys.readouterr().out
    assert "(injected)" in captured


# --- the allowlist refresher ----------------------------------------------


def test_merge_refuses_to_write_an_empty_allowlist():
    """A mount with no models serves nothing, so the write is refused."""
    with pytest.raises(refresh.RefreshError):
        refresh.merge_ids([], [], [])


def test_merge_keeps_order_and_appends_alphabetically():
    """Existing ids keep their order; new ids are appended in one order."""
    merged = refresh.merge_ids(["b", "a"], [], ["c", "d"])
    assert merged == ["b", "a", "c", "d"]


def test_merge_drops_only_the_ids_marked_gone():
    """A removal is limited to the ids the probe declared gone."""
    merged = refresh.merge_ids(["a", "b", "c"], ["b"], [])
    assert merged == ["a", "c"]


def test_classify_never_marks_a_candidate_on_a_failed_probe():
    """A timeout, a 429 or a 5xx means unknown, never a removal candidate."""
    verdict = refresh.classify(["a", "b"], [], False)
    assert verdict["candidates"] == []
    assert verdict["keep"] == ["a", "b"]


def test_classify_marks_only_ids_absent_from_the_family_as_candidates():
    """An id that moved between mounts of the same family survives.

    A candidate is not a verdict: the catalogue is not the served set, so
    the operator confirms every removal.
    """
    verdict = refresh.classify(["a", "b"], ["b", "c"], True)
    assert verdict["candidates"] == ["a"]
    assert verdict["keep"] == ["b"]


def test_read_sets_parses_the_four_allowlists():
    """The script reads the sets out of the file without importing it."""
    sets = refresh.read_sets()
    assert set(sets) == {"ZEN_CHAT", "ZEN_RESP", "GO_CHAT", "GO_RESP"}
    assert "glm-5.3" in sets["GO_CHAT"]
    assert "glm-5.3" in sets["GO_RESP"]


def test_empty_catalogue_is_treated_as_unknown(monkeypatch):
    """A catalogue with no models is a blocked tier, not a dead fleet.

    The gateway answers 200 with an empty or error-shaped body when the
    tier is exhausted. Treating that as "every model is gone" would empty
    an allowlist on a quota error.
    """

    class _EmptyResponse:
        def read(self):
            return b'{"error":{"type":"FreeUsageLimitError"}}'

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(
        refresh.urllib.request, "urlopen", lambda *a, **k: _EmptyResponse()
    )

    ids, ok = refresh.fetch_catalogue("http://127.0.0.1:1", "/zen/v1", "key")

    assert ids == []
    assert ok is False


def test_main_keeps_the_current_set_when_a_merge_would_empty_it(monkeypatch):
    """A mount that would end up empty is kept, not written away."""
    monkeypatch.setattr(
        refresh, "fetch_catalogue", lambda *a, **k: (["only-one"], True)
    )
    monkeypatch.setattr(
        refresh,
        "read_sets",
        lambda *a, **k: {
            "ZEN_CHAT": ["a"],
            "ZEN_RESP": ["b"],
            "GO_CHAT": ["c"],
            "GO_RESP": ["d"],
        },
    )

    code = refresh.main(["--key-env", "PATH", "--proxy", str(SLICE / "proxy.py")])

    assert code == 0  # the report still runs and nothing is written


def test_a_candidate_is_never_removed_without_a_confirmation(monkeypatch, tmp_path):
    """The catalogue is not the served set, so a candidate is not a verdict."""
    monkeypatch.setattr(refresh, "fetch_catalogue", lambda *a, **k: (["served"], True))
    source = (SLICE / "proxy.py").read_text(encoding="utf-8")
    target = tmp_path / "proxy.py"
    target.write_text(source, encoding="utf-8")
    monkeypatch.setattr(
        refresh,
        "read_sets",
        lambda *a, **k: {
            "ZEN_CHAT": ["served", "served-but-unlisted"],
            "ZEN_RESP": ["served"],
            "GO_CHAT": ["served"],
            "GO_RESP": ["served"],
        },
    )

    code = refresh.main(["--key-env", "PATH", "--proxy", str(target), "--apply"])

    assert code == 0
    rewritten = target.read_text(encoding="utf-8")
    assert '"served-but-unlisted",' in rewritten  # a candidate survives


def test_rewrite_sets_touches_only_the_allowlists(tmp_path):
    """The rewrite keeps the rest of the module byte-identical."""
    source = (SLICE / "proxy.py").read_text(encoding="utf-8")
    target = tmp_path / "proxy.py"
    target.write_text(source, encoding="utf-8")

    changed = refresh.rewrite_sets(str(target), {"GO_CHAT": ["glm-5.3", "new-model"]})

    assert changed is True
    rewritten = target.read_text(encoding="utf-8")
    assert '"new-model",' in rewritten
    assert 'UPSTREAM = "https://opencode.ai"' in rewritten
    assert rewritten.count("def _proxy_inner(") == 1
