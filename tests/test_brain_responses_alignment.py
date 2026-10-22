# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Responses-API alignment tests (Task 329).

Offline only: covers the request-body builder behind env switches, the
extended diagnostics parser (response model, cached tokens, error
codes), the billing-terminal 429 classifier, the corrected effort
ladder, fail-loud token cap, versioned transcript replay with phase,
estimator calibration, and the fatal-4xx-as-REPORT path. The live LLM
path (httpx POST) is never touched: provider calls are faked.
"""

import os
import sys
import types as _types
from pathlib import Path

import pytest

BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

import server as bridge


@pytest.fixture(autouse=True)
def _clean_responses_env(monkeypatch):
    """Hermetic defaults for every alignment test: drop ambient session
    binding and every request-shape switch so the default wire bytes
    stay identical to the pre-329 shape unless a test opts in."""
    monkeypatch.delenv("OPENCODE_SESSION_ID", raising=False)
    for var in (
        "BRAIN_SEND_STORE",
        "BRAIN_SEND_INCLUDE_ENCRYPTED",
        "BRAIN_SEND_CACHE_KEY",
        "BRAIN_SEND_TRUNCATION",
        "BRAIN_SEND_CONTEXT_MANAGEMENT",
        "BRAIN_USE_INSTRUCTIONS",
        "BRAIN_CHARS_PER_TOKEN",
        "BRAIN_COMPACTION_THRESHOLD",
        "BRAIN_TEMPERATURE",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "medium")
    monkeypatch.setenv("BRAIN_MAX_TOKENS", "32768")
    # Reset the calibrated estimator so tests never inherit each other.
    bridge._calibrated_chars_per_token = None  # type: ignore[attr-defined]
    yield
    bridge._calibrated_chars_per_token = None  # type: ignore[attr-defined]


def _history():
    return [
        {"role": "user", "content": "first question"},
        {"role": "assistant", "content": "first answer"},
    ]


# --- Request-body builder (F1/F3/F4/F10) ---------------------------------


def test_body_builder_default_shape_unchanged():
    """With every switch off, wire bytes are identical to pre-329 shape."""
    body = bridge._build_request_body("sys", _history(), "do it")
    assert set(body) == {"model", "input", "reasoning", "max_output_tokens"}
    assert body["input"][0] == {"role": "system", "content": "sys"}
    assert body["input"][-1] == {"role": "user", "content": "do it"}
    assert body["reasoning"] == {"effort": "medium"}


def test_body_builder_flags_matrix(monkeypatch):
    """Each opt-in switch adds exactly its documented key, nothing else."""
    monkeypatch.setenv("BRAIN_SEND_STORE", "1")
    body = bridge._build_request_body("sys", _history(), "do it")
    assert body["store"] is False

    monkeypatch.setenv("BRAIN_SEND_CACHE_KEY", "yes")
    body = bridge._build_request_body("sys", _history(), "do it")
    assert isinstance(body["prompt_cache_key"], str)
    assert body["prompt_cache_key"].startswith("brain-")
    key2 = bridge._build_request_body("sys", _history(), "different prompt")[
        "prompt_cache_key"
    ]
    assert body["prompt_cache_key"] == key2, "key must be stable per system prompt"
    key3 = bridge._build_request_body("other-sys", _history(), "do it")[
        "prompt_cache_key"
    ]
    assert key3 != body["prompt_cache_key"], "key must vary with system prompt"

    monkeypatch.setenv("BRAIN_SEND_TRUNCATION", "true")
    body = bridge._build_request_body("sys", _history(), "do it")
    assert body["truncation"] == "auto"

    monkeypatch.setenv("BRAIN_SEND_INCLUDE_ENCRYPTED", "on")
    body = bridge._build_request_body("sys", _history(), "do it")
    assert body["include"] == ["reasoning.encrypted_content"]

    monkeypatch.setenv("BRAIN_SEND_CONTEXT_MANAGEMENT", "1")
    body = bridge._build_request_body("sys", _history(), "do it")
    assert body["context_management"] == [
        {"type": "compaction", "compact_threshold": 100000}
    ]

    monkeypatch.setenv("BRAIN_USE_INSTRUCTIONS", "1")
    body = bridge._build_request_body("sys", _history(), "do it")
    assert body["instructions"] == "sys"
    assert all(t.get("role") != "system" for t in body["input"])
    assert body["input"][-1] == {"role": "user", "content": "do it"}


# --- Diagnostics parser (F4/F5/F6) ----------------------------------------


def test_diagnostics_reads_model_and_cached_tokens_and_error_codes():
    data = {
        "id": "resp_123",
        "model": "muse-spark-1.3-contributor",
        "service_tier": "default",
        "status": "completed",
        "usage": {
            "input_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 15,
            "input_tokens_details": {"cached_tokens": 4},
            "output_tokens_details": {"reasoning_tokens": 2},
        },
        "error": {
            "message": "quota hit",
            "code": "insufficient_quota",
            "type": "insufficient_quota",
        },
        "output": [],
    }
    diag = bridge.parse_responses_diagnostics(data)
    assert diag["response_model"] == "muse-spark-1.3-contributor"
    assert diag["response_id"] == "resp_123"
    assert diag["service_tier"] == "default"
    assert diag["usage"]["cached_tokens"] == 4
    assert diag["usage"]["reasoning_tokens"] == 2
    assert diag["error"] == "quota hit"
    assert diag["error_code"] == "insufficient_quota"
    assert diag["error_type"] == "insufficient_quota"


def test_diagnostics_new_keys_default_to_none():
    diag = bridge.parse_responses_diagnostics({"status": "completed"})
    assert diag["response_model"] is None
    assert diag["response_id"] is None
    assert diag["service_tier"] is None
    assert diag["provider_status_code"] is None
    assert diag["usage"]["cached_tokens"] is None
    assert diag["error_code"] is None
    assert diag["error_type"] is None


def test_effort_validation_normalizes_case(monkeypatch):
    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "XHigh")
    assert bridge._get_reasoning_effort() == "xhigh"


# --- Terminal 429 classifier (F6) ------------------------------------------


@pytest.mark.parametrize(
    "code",
    [
        "credit_balance_exhausted",
        "organization_spend_limit_exceeded",
        "project_spend_limit_exceeded",
        "organization_usage_limit_exceeded",
        "insufficient_quota",
        "billing_hard_limit_exceeded",
    ],
)
def test_terminal_429_codes_are_terminal(code):
    assert bridge._terminal_429_code(429, {"error": {"code": code}}) == code


def test_non_terminal_429_returns_none():
    assert (
        bridge._terminal_429_code(429, {"error": {"code": "rate_limit_exceeded"}})
        is None
    )
    assert bridge._terminal_429_code(429, {"error": {"message": "slow down"}}) is None
    assert bridge._terminal_429_code(429, "slow down") is None
    assert (
        bridge._terminal_429_code(500, {"error": {"code": "insufficient_quota"}})
        is None
    )


# --- Effort vocabulary and ladder (F8) --------------------------------------


def test_effort_ladder_includes_minimal_and_never_raises():
    assert bridge._step_down_effort("max") == "xhigh"
    assert bridge._step_down_effort("xhigh") == "high"
    assert bridge._step_down_effort("high") == "medium"
    assert bridge._step_down_effort("medium") == "low"
    assert bridge._step_down_effort("low") == "minimal"
    assert bridge._step_down_effort("minimal") == "minimal"
    # Unknown values keep the current effort (floor guard => no recovery),
    # never jump up to medium.
    assert bridge._step_down_effort("turbo") == "turbo"
    assert bridge._step_down_effort("none") == "none"


def test_effort_ladder_bad_types_fall_to_low():
    assert bridge._step_down_effort("") == "low"
    assert bridge._step_down_effort(None) == "low"


def test_effort_validation_accepts_official_vocabulary(monkeypatch):
    for effort in ("none", "minimal", "low", "medium", "high", "xhigh", "max"):
        monkeypatch.setenv("BRAIN_REASONING_EFFORT", effort)
        assert bridge._get_reasoning_effort() == effort


def test_effort_validation_rejects_garbage(monkeypatch):
    import pytest as _pt

    for bad in ("bad effort!!", "x" * 65, "MEDIUM!!"):
        monkeypatch.setenv("BRAIN_REASONING_EFFORT", bad)
        with _pt.raises(ValueError):
            bridge._get_reasoning_effort()


# --- Token cap fails loud (F9) -----------------------------------------------


def test_get_max_tokens_fail_loud(monkeypatch):
    import pytest as _pt

    monkeypatch.setenv("BRAIN_MAX_TOKENS", "not-a-number")
    with _pt.raises(ValueError, match="BRAIN_MAX_TOKENS"):
        bridge._get_max_tokens()
    monkeypatch.setenv("BRAIN_MAX_TOKENS", "-5")
    with _pt.raises(ValueError, match="BRAIN_MAX_TOKENS"):
        bridge._get_max_tokens()
    monkeypatch.setenv("BRAIN_MAX_TOKENS", "16384")
    assert bridge._get_max_tokens() == 16384


# --- Transcript replay with phase and reasoning items (F2) --------------------


def test_parse_turns_keeps_provider_items_and_phase():
    raw = (
        '{"role": "user", "content": "q"}\n'
        '{"role": "assistant", "content": "a", "phase": "final_answer", '
        '"response_id": "resp_1", "provider_items": '
        '[{"id": "rs_1", "type": "reasoning", "encrypted_content": "e30="}]}\n'
    )
    turns, skipped = bridge._parse_turns(raw)
    assert skipped == 0
    assert turns[1]["phase"] == "final_answer"
    assert turns[1]["response_id"] == "resp_1"
    assert turns[1]["provider_items"] == [
        {"id": "rs_1", "type": "reasoning", "encrypted_content": "e30="}
    ]


def test_old_transcript_replays_exactly_as_today():
    raw = '{"role": "user", "content": "q"}\n{"role": "assistant", "content": "a"}\n'
    turns, _ = bridge._parse_turns(raw)
    assert "provider_items" not in turns[1]
    assert "phase" not in turns[1]
    body = bridge._build_request_body("sys", turns, "next")
    assert body["input"][1] == {"role": "user", "content": "q"}
    assert body["input"][2] == {"role": "assistant", "content": "a"}


def test_new_transcript_replays_reasoning_items_and_phase():
    raw = (
        '{"role": "user", "content": "q"}\n'
        '{"role": "assistant", "content": "a", "phase": "final_answer", '
        '"provider_items": [{"id": "rs_1", "type": "reasoning"}]}\n'
    )
    turns, _ = bridge._parse_turns(raw)
    body = bridge._build_request_body("sys", turns, "next")
    assistant = body["input"][2]
    assert assistant["content"] == "a"
    assert assistant["phase"] == "final_answer"
    assert {"id": "rs_1", "type": "reasoning"} in body["input"][3:]


def test_replay_strips_status_from_reasoning_items():
    # 2026-10-22: upstream attaches "status" (e.g. "completed") to reasoning
    # output items; the Go gateway's gpt-6-luna endpoint 400s with
    # "Unknown parameter: 'input[N].status'" when it is replayed, while
    # muse-spark-1.3-contributor silently accepts it. The replay must drop
    # the volatile key but keep id/type/encrypted_content intact.
    raw = (
        '{"role": "user", "content": "q"}\n'
        '{"role": "assistant", "content": "a", "phase": "final_answer", '
        '"provider_items": [{"id": "rs_1", "type": "reasoning", '
        '"status": "completed", "content": [], "summary": [], '
        '"encrypted_content": "e30="}]}\n'
    )
    turns, _ = bridge._parse_turns(raw)
    body = bridge._build_request_body("sys", turns, "next")
    replayed = [
        it for it in body["input"][3:]
        if isinstance(it, dict) and it.get("type") == "reasoning"
    ]
    assert len(replayed) == 1
    assert "status" not in replayed[0]
    assert replayed[0]["id"] == "rs_1"
    assert replayed[0]["type"] == "reasoning"
    assert replayed[0]["encrypted_content"] == "e30="


def test_replay_without_status_stays_byte_identical():
    # No dropped keys present -> the exact same object rides the wire
    # (F2 verbatim contract).
    raw = (
        '{"role": "user", "content": "q"}\n'
        '{"role": "assistant", "content": "a", '
        '"provider_items": [{"id": "rs_1", "type": "reasoning", '
        '"encrypted_content": "e30="}]}\n'
    )
    turns, _ = bridge._parse_turns(raw)
    original = turns[1]["provider_items"][0]
    body = bridge._build_request_body("sys", turns, "next")
    assert body["input"][3] is original


# --- Estimator calibration (F3) -----------------------------------------------


def test_estimator_calibration_from_observed_usage():
    assert bridge._estimate_input_tokens_from_chars(4000) == 1000
    bridge._note_observed_ratio(4600, 1000)
    assert bridge._estimate_input_tokens_from_chars(4600) == 1000
    # Garbage observations never corrupt the estimator.
    bridge._note_observed_ratio(0, 0)
    bridge._note_observed_ratio(-10, 5)
    assert bridge._estimate_input_tokens_from_chars(4600) == 1000


def test_chars_per_token_env_override_fail_loud(monkeypatch):
    import pytest as _pt

    monkeypatch.setenv("BRAIN_CHARS_PER_TOKEN", "junk")
    with _pt.raises(ValueError, match="BRAIN_CHARS_PER_TOKEN"):
        bridge._estimate_input_tokens_from_chars(100)
    monkeypatch.setenv("BRAIN_CHARS_PER_TOKEN", "2")
    assert bridge._estimate_input_tokens_from_chars(100) == 50


# --- Fatal 4xx as structured REPORT (F7) ---------------------------------------


class _FakeResp:
    def __init__(self, status_code=200, text="", payload=None):
        self.status_code = status_code
        self.text = text
        self._payload = payload
        self.headers = {"content-type": "application/json"}

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class _FakeClient:
    def __init__(self, script):
        self._script = list(script)
        self.last_body = None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def post(self, url, json=None, headers=None, **kwargs):
        self.last_body = json
        item = self._script.pop(0) if len(self._script) > 1 else self._script[0]
        if isinstance(item, Exception):
            raise item
        return item


def _mk_sys_prompt(tmp_path, monkeypatch, text="sys"):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    prompt_file = tmp_path / ".config" / "opencode" / "sys.md"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(text, encoding="utf-8")
    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(prompt_file))


def _stub_client(monkeypatch, script):
    stub = _types.ModuleType("httpx")
    stub.Client = lambda *a, **k: _FakeClient(script)
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            self.args, self.kwargs = a, k

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)


def test_fatal_4xx_returns_report_with_provider_diagnostics(tmp_path, monkeypatch):
    """A 400 with an error code must surface as a REPORT carrying
    debug.provider — never as a raw tool exception (F7)."""
    import time as _time

    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setattr(_time, "sleep", lambda s: None)
    body_text = '{"error": {"message": "quota hit", "code": "insufficient_quota"}}'
    _stub_client(monkeypatch, [_FakeResp(400, body_text, None)])
    target = (
        bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn") else bridge.brain_turn
    )
    result = target("q", task_id="329")
    assert result["status"] == "REPORT"
    assert bridge.PROVIDER_ERROR in result["output"]
    assert "insufficient_quota" in result["output"]
    assert result["debug"]["provider"]["error_code"] == "insufficient_quota"
    assert result["debug"]["provider"]["provider_status_code"] == 400
