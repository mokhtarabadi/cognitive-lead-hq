"""Capability-preflight tests for mcp-brain-bridge (GitHub issue 16).

RED-first: ``capability`` and ``session_ledger`` modules do not exist yet.
Covers the manifest producer (exactly three statuses, ``question`` tool
included), the gate (missing-required blocks approval-sensitive work),
the single approval rule, stage-implied requirements, and the
``brain_turn`` wiring (manifest diagnostic + ledger event + non-verdict
REPORT block on missing-required with zero transport calls).
"""

import json
import os
import sys
import types as _types
from pathlib import Path

import pytest

BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

import capability
import server as bridge


# --- manifest producer ---

def test_all_available_tools_report_available():
    manifest = capability.build_manifest(
        referenced=["lint_task_file", "brain_turn"], required=[])
    assert manifest == {"lint_task_file": "AVAILABLE",
                        "brain_turn": "AVAILABLE"}


def test_question_tool_is_available():
    manifest = capability.build_manifest(
        referenced=["question"], required=["question"])
    assert manifest == {"question": "AVAILABLE"}


def test_known_unavailable_registry_is_empty():
    assert capability.KNOWN_UNAVAILABLE == frozenset()


def test_unknown_required_tool_fails_closed():
    manifest = capability.build_manifest(
        referenced=["frobnicate"], required=["frobnicate"])
    assert manifest == {"frobnicate": "UNAVAILABLE_REQUIRED"}


def test_unknown_optional_tool_is_unavailable_optional():
    manifest = capability.build_manifest(
        referenced=["frobnicate"], required=[])
    assert manifest == {"frobnicate": "UNAVAILABLE_OPTIONAL"}


def test_caller_available_override_wins():
    manifest = capability.build_manifest(
        referenced=["frobnicate"], required=["frobnicate"],
        available={"frobnicate"})
    assert manifest == {"frobnicate": "AVAILABLE"}


def test_caller_unavailable_override_marks_required():
    manifest = capability.build_manifest(
        referenced=["lint_task_file"], required=["lint_task_file"],
        unavailable={"lint_task_file"})
    assert manifest == {"lint_task_file": "UNAVAILABLE_REQUIRED"}


def test_unavailable_override_demotes_granted_question_tool():
    """An explicit unavailable override still demotes a granted tool.

    `question` is in `AVAILABLE_EXACT` now, so this pins the override path
    for a registry-available name rather than an unknown one.
    """
    manifest = capability.build_manifest(
        referenced=["question"], required=["question"],
        unavailable={"question"})
    assert manifest == {"question": "UNAVAILABLE_REQUIRED"}


def test_only_three_statuses_exist():
    assert capability.STATUSES == (
        "AVAILABLE", "UNAVAILABLE_REQUIRED", "UNAVAILABLE_OPTIONAL")
    manifest = capability.build_manifest(
        referenced=["brain_turn", "question", "frobnicate"],
        required=["frobnicate"])
    assert set(manifest.values()) <= set(capability.STATUSES)


def test_internal_registry_name_never_emitted_as_status():
    manifest = capability.build_manifest(
        referenced=["brain_turn", "question", "frobnicate",
                    "lint_task_file"],
        required=["brain_turn", "frobnicate", "lint_task_file"])
    assert "KNOWN_UNAVAILABLE" not in manifest.values()
    assert manifest["frobnicate"] == "UNAVAILABLE_REQUIRED"
    assert manifest["question"] == "AVAILABLE"


def test_empty_referenced_gives_empty_manifest():
    assert capability.build_manifest(referenced=[], required=[]) == {}


# --- gate ---

def test_gate_passes_with_no_missing_required():
    manifest = capability.build_manifest(
        referenced=["lint_task_file", "frobnicate"],
        required=["lint_task_file"])
    assert capability.gate(manifest, stage="qa") is None


def test_gate_raises_naming_missing_tools():
    manifest = capability.build_manifest(
        referenced=["frobnicate"], required=["frobnicate"])
    with pytest.raises(capability.CapabilityBlockedError) as exc:
        capability.gate(manifest, stage="review")
    assert "frobnicate" in str(exc.value)
    assert "review" in str(exc.value)


def test_gate_error_carries_relay_block():
    manifest = capability.build_manifest(
        referenced=["frobnicate"], required=["frobnicate"])
    with pytest.raises(capability.CapabilityBlockedError) as exc:
        capability.gate(manifest, stage="review")
    block = capability.format_relay_block(exc.value)
    assert "frobnicate" in block
    assert "review" in block


# --- single approval rule ---

def test_closure_approval_only_exact_phrases():
    assert capability.is_approval("Approved for closure", "closure") is True
    assert capability.is_approval("Close task", "closure") is True
    assert capability.is_approval("APPROVED FOR CLOSURE", "closure") is True
    assert capability.is_approval("approved", "closure") is False
    assert capability.is_approval("looks good", "closure") is False


def test_plan_approval_accepts_bare_approved():
    assert capability.is_approval("approved", "plan") is True
    assert capability.is_approval("Approved", "plan") is True
    assert capability.is_approval("Approved for closure", "plan") is True
    assert capability.is_approval("ok", "plan") is False
    assert capability.is_approval("yes", "plan") is False


def test_unknown_gate_never_approves():
    assert capability.is_approval("approved", "bogus") is False


# --- stage-implied requirements ---

def test_stage_implied_requirements_cover_key_gates():
    assert "lint_task_file" in capability.STAGE_REQUIRED_TOOLS["qa"]
    assert ("custom_context_commit_and_clean_task"
            in capability.STAGE_REQUIRED_TOOLS["closure"])
    assert "brain_turn" in capability.STAGE_REQUIRED_TOOLS["plan"]


def test_stage_implied_missing_blocks_even_when_unlisted():
    manifest = capability.evaluate(
        referenced=[], required=[], stage="qa",
        unavailable={"lint_task_file"})
    with pytest.raises(capability.CapabilityBlockedError):
        capability.gate(manifest, stage="qa")


# --- brain_turn wiring ---

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


def _ok_payload(text="ok"):
    return {"output": [{"type": "message",
                        "content": [{"type": "output_text",
                                     "text": text}]}]}


def _stub_httpx(monkeypatch, script, holder):
    class _CapClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, json=None, headers=None, **kwargs):
            holder["calls"] = holder.get("calls", 0) + 1
            holder["body"] = json
            item = script.pop(0) if len(script) > 1 else script[0]
            if isinstance(item, Exception):
                raise item
            return item

    stub = _types.ModuleType("httpx")
    stub.Client = _CapClient
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})
    stub.Timeout = lambda *a, **k: None  # noqa: E731
    monkeypatch.setitem(sys.modules, "httpx", stub)


def _mk_env(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    prompt_file = tmp_path / ".config" / "opencode" / "sys.md"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text("sys", encoding="utf-8")
    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(prompt_file))
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    proj = tmp_path / "proj"
    (proj / "tasks").mkdir(parents=True)
    return proj


def test_brain_turn_missing_required_returns_non_verdict_report(
        tmp_path, monkeypatch, capsys):
    proj = _mk_env(tmp_path, monkeypatch)
    holder = {}
    _stub_httpx(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("review this", task_id="257", project_root=str(proj),
                    stage="review", required_tools=["frobnicate"])
    assert result["status"] == "REPORT"
    assert "frobnicate" in result["output"]
    for verdict in ("QA_PASSED", "QA_REJECTED", "VERDICT:",
                    "PO_REVIEW_PENDING", "APPROVED"):
        assert verdict not in result["output"]
    assert holder.get("calls", 0) == 0
    assert result["retry_count"] == 0


def test_brain_turn_all_available_reaches_transport(tmp_path, monkeypatch):
    proj = _mk_env(tmp_path, monkeypatch)
    holder = {}
    _stub_httpx(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("review this", task_id="257", project_root=str(proj),
                    stage="review", required_tools=["brain_turn"])
    assert result["status"] == "REPORT"
    assert result["output"] == "ok"
    assert holder.get("calls", 0) == 1


def test_brain_turn_emits_session_start_manifest_diagnostic(
        tmp_path, monkeypatch, capsys):
    proj = _mk_env(tmp_path, monkeypatch)
    holder = {}
    _stub_httpx(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    target("hello", task_id="257", project_root=str(proj))
    err = capsys.readouterr().err
    assert "capability-manifest" in err


def test_brain_turn_persists_manifest_ledger_event(tmp_path, monkeypatch):
    proj = _mk_env(tmp_path, monkeypatch)
    holder = {}
    _stub_httpx(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    target("hello", task_id="257", project_root=str(proj))
    ledger = proj / "tasks" / ".sessions" / "session_ledger.jsonl"
    assert ledger.is_file()
    events = [json.loads(line) for line in
              ledger.read_text(encoding="utf-8").splitlines()]
    manifests = [e for e in events if e.get("event") == "capability_manifest"]
    assert len(manifests) == 1
    assert manifests[0]["task_id"] == "257"
