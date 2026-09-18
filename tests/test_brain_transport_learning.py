"""Unit tests for transport-failure learning (GitHub issue 17).

Offline only: the classifier, the saga-scoped correction memory, and
the ``brain_turn`` send path (mocked httpx) that retries once with a
corrected body and escalates on repeat — never surfacing a verdict.
"""

import json
import sys
import time as _time
import types as _types
from pathlib import Path

import pytest

BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

import server as bridge
import transport_learning as tl


# --- local harness (mirrors test_brain_bridge.py) ---

class _FakeResp:
    def __init__(self, status_code=200, text="", payload=None,
                 ctype="application/json"):
        self.status_code = status_code
        self.text = text
        self._payload = payload
        self.headers = {"content-type": ctype}

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class _RecClient:
    """Fake client capturing every POST body in order; script drives replies."""

    def __init__(self, script, bodies):
        # SHARED script reference (no copy): the learning send path
        # builds one client per round, and rounds must consume one
        # shared script in order.
        self._script = script
        self._bodies = bodies
        self.calls = 0

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def post(self, url, json=None, headers=None, **kwargs):
        self.calls += 1
        self._bodies.append(json)
        item = self._script.pop(0) if len(self._script) > 1 else self._script[0]
        if isinstance(item, Exception):
            raise item
        return item


def _stub_client(monkeypatch, script, bodies):
    stub = _types.ModuleType("httpx")
    stub.Client = lambda *a, **k: _RecClient(script, bodies)
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            self.args, self.kwargs = a, k

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)


def _ok_payload(text="ok"):
    return {"output": [{"type": "message",
                        "content": [{"type": "output_text", "text": text}]}]}


def _mk_sys_prompt(tmp_path, monkeypatch, text="sys"):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    prompt_file = tmp_path / ".config" / "opencode" / "sys.md"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(text, encoding="utf-8")
    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(prompt_file))


def _mk_project(tmp_path, name="proj"):
    proj = tmp_path / name
    (proj / "tasks").mkdir(parents=True)
    return proj


def _unsupported_400_text(param):
    return json.dumps({"error": {
        "message": f"Unsupported parameter: '{param}'. Try again.",
        "type": "invalid_request_error",
        "param": param,
        "code": "unsupported_parameter",
    }})


def _turn_env(tmp_path, monkeypatch):
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    return _mk_project(tmp_path)


# --- classifier: correctable class ---

def test_classify_400_unsupported_parameter_drops_key():
    body = {"model": "m", "input": [], "temperature": 0.7}
    exc = RuntimeError(
        "fatal provider error 400 (no retry) at responses: "
        + _unsupported_400_text("temperature"))
    corr = tl.classify_transport_error(exc, body)
    assert corr is not None
    assert corr.param == "temperature"
    assert corr.action == "drop"
    assert corr.failure_class == "unsupported_parameter"


def test_classify_ignores_non_400_status():
    body = {"model": "m", "input": []}
    exc = RuntimeError("provider failed after 3 attempts (500) at x: boom")
    assert tl.classify_transport_error(exc, body) is None


def test_classify_ignores_400_without_unsupported_pattern():
    body = {"model": "m", "input": []}
    exc = RuntimeError(
        "fatal provider error 400 (no retry) at responses: bad request")
    assert tl.classify_transport_error(exc, body) is None


def test_classify_refuses_when_param_absent_from_body():
    body = {"model": "m", "input": []}
    exc = RuntimeError(
        "fatal provider error 400 (no retry) at responses: "
        + _unsupported_400_text("top_p"))
    assert tl.classify_transport_error(exc, body) is None


def test_classify_never_drops_protected_keys():
    for key in ("model", "input"):
        body = {"model": "m", "input": []}
        exc = RuntimeError(
            "fatal provider error 400 (no retry) at responses: "
            + _unsupported_400_text(key))
        assert tl.classify_transport_error(exc, body) is None


def test_correction_apply_returns_new_body_without_key():
    body = {"model": "m", "input": [], "temperature": 0.7}
    exc = RuntimeError(
        "fatal provider error 400 (no retry) at responses: "
        + _unsupported_400_text("temperature"))
    corr = tl.classify_transport_error(exc, body)
    fixed = corr.apply(body)
    assert "temperature" not in fixed
    assert fixed["model"] == "m"
    assert "temperature" in body  # original untouched


# --- correction memory: saga-scoped, ledger-backed ---

def test_memory_seen_record_roundtrip_with_ledger(tmp_path):
    sessions = tmp_path / "sessions"
    mem = tl.CorrectionMemory("257")
    assert mem.seen("unsupported_parameter:drop:temperature") is False
    body = {"model": "m", "input": [], "temperature": 0.7}
    exc = RuntimeError("fatal provider error 400 (no retry) at r: "
                       + _unsupported_400_text("temperature"))
    corr = tl.classify_transport_error(exc, body)
    record = mem.record(corr, task_id="257", sessions_dir=str(sessions))
    assert record["event"] == "transport_correction"
    assert record["persisted"] is True
    assert mem.seen(corr.fingerprint) is True
    lines = (sessions / "session_ledger.jsonl").read_text(
        encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["event"] == "transport_correction"
    assert event["task_id"] == "257"
    assert event["param"] == "temperature"


def test_memory_history_preload_marks_seen():
    mem = tl.CorrectionMemory(
        "257", seen_fingerprints=["unsupported_parameter:drop:temperature"])
    assert mem.seen("unsupported_parameter:drop:temperature") is True
    assert mem.seen("unsupported_parameter:drop:top_p") is False


def test_memory_record_without_roots_skips_ledger():
    mem = tl.CorrectionMemory("257")
    body = {"model": "m", "input": [], "temperature": 0.7}
    exc = RuntimeError("fatal provider error 400 (no retry) at r: "
                       + _unsupported_400_text("temperature"))
    corr = tl.classify_transport_error(exc, body)
    record = mem.record(corr)
    assert record["persisted"] is False
    assert mem.seen(corr.fingerprint) is True


def test_failure_signature_identifies_repeat_without_body_key():
    exc = RuntimeError(
        "fatal provider error 400 (no retry) at responses: "
        + _unsupported_400_text("temperature"))
    assert tl.failure_signature(exc) == "unsupported_parameter:temperature"
    assert tl.failure_signature(RuntimeError("provider failed (500)")) is None


def test_memory_tracks_corrected_signatures():
    mem = tl.CorrectionMemory("257")
    assert mem.already_corrected("unsupported_parameter:temperature") is False
    body = {"model": "m", "input": [], "temperature": 0.7}
    exc = RuntimeError("fatal provider error 400 (no retry) at r: "
                       + _unsupported_400_text("temperature"))
    mem.record(tl.classify_transport_error(exc, body))
    assert mem.already_corrected("unsupported_parameter:temperature") is True
    assert mem.already_corrected("unsupported_parameter:top_p") is False


def test_escalation_message_marks_never_verdict():
    msg = tl.escalation_message(
        "257", "unsupported_parameter:drop:temperature", repeats=2)
    assert "transport-learning-escalation" in msg
    assert "257" in msg
    for verdict in ("QA_PASSED", "QA_REJECTED", "VERDICT",
                    "PO_REVIEW_PENDING", "XML_EXTRACTED"):
        assert verdict not in msg


# --- transport seam: attempt accounting ---

def test_post_with_retry_fatal_carries_attempt_count(monkeypatch):
    _stub_client(monkeypatch, [_FakeResp(400, "bad")], [])
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")

    class _OneShot:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, json=None, headers=None, **kwargs):
            return _FakeResp(400, "bad")

    import httpx  # noqa: F401  (stubbed above)
    with pytest.raises(RuntimeError) as exc:
        bridge._post_with_retry(_OneShot(), "http://x/responses", {})
    assert getattr(exc.value, "transport_attempts", None) == 1


# --- brain_turn integration ---

def test_brain_turn_corrects_once_and_succeeds(tmp_path, monkeypatch):
    proj = _turn_env(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
    bodies: list = []
    script = [_FakeResp(400, _unsupported_400_text("temperature")),
              _FakeResp(200, "fine", _ok_payload("recovered"))]
    _stub_client(monkeypatch, script, bodies)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="999", project_root=str(proj))
    assert result["status"] == "REPORT"
    assert result["output"] == "recovered"
    assert len(bodies) == 2
    assert bodies[0]["temperature"] == 0.7
    assert "temperature" not in bodies[1]
    assert result["retry_count"] == 2
    ledger = proj / "tasks" / ".sessions" / "session_ledger.jsonl"
    events = [json.loads(line) for line in
              ledger.read_text(encoding="utf-8").splitlines()]
    transport = [e["event"] for e in events
                 if e["event"].startswith("transport_")]
    assert transport == ["transport_correction"]


def test_brain_turn_repeat_failure_escalates_never_verdict(
        tmp_path, monkeypatch):
    proj = _turn_env(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
    bodies: list = []
    script = [_FakeResp(400, _unsupported_400_text("temperature")),
              _FakeResp(400, _unsupported_400_text("temperature"))]
    _stub_client(monkeypatch, script, bodies)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    with pytest.raises(tl.TransportEscalationError) as exc:
        target("q", task_id="999", project_root=str(proj))
    msg = str(exc.value)
    assert "transport-learning-escalation" in msg
    assert "999" in msg
    for verdict in ("QA_PASSED", "QA_REJECTED", "VERDICT",
                    "PO_REVIEW_PENDING", "XML_EXTRACTED"):
        assert verdict not in msg
    ledger = proj / "tasks" / ".sessions" / "session_ledger.jsonl"
    kinds = [json.loads(line)["event"] for line in
             ledger.read_text(encoding="utf-8").splitlines()
             if json.loads(line)["event"].startswith("transport_")]
    assert kinds == ["transport_correction", "transport_escalation"]


def test_brain_turn_noncorrectable_error_passes_through(
        tmp_path, monkeypatch):
    proj = _turn_env(tmp_path, monkeypatch)
    monkeypatch.setattr(_time, "sleep", lambda s: None)
    bodies: list = []
    _stub_client(monkeypatch, [_FakeResp(500, "boom")], bodies)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    with pytest.raises(RuntimeError) as exc:
        target("q", task_id="999", project_root=str(proj))
    assert not isinstance(exc.value, tl.TransportEscalationError)
    assert "500" in str(exc.value)
    # The capability-manifest event (WS2) still lands, but learning
    # itself must not engage on a non-correctable failure.
    ledger = proj / "tasks" / ".sessions" / "session_ledger.jsonl"
    kinds = [json.loads(line)["event"] for line in
             ledger.read_text(encoding="utf-8").splitlines()]
    assert "transport_correction" not in kinds
    assert "transport_escalation" not in kinds
