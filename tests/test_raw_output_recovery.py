# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Raw-output preservation and deterministic Hands recovery tests."""

import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
BRIDGE_DIR = ROOT / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))
import server as bridge

HELPER = BRIDGE_DIR / "parse_brain_output.py"


class _FakeResp:
    def __init__(self, payload):
        self.status_code = 200
        self.text = "ok"
        self._payload = payload
        self.headers = {"content-type": "application/json"}

    def json(self):
        return self._payload


def _payload(text):
    return {
        "output": [
            {"type": "message", "content": [{"type": "output_text", "text": text}]}
        ]
    }


def _setup(tmp_path, monkeypatch, raw):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    prompt = tmp_path / ".config" / "opencode" / "sys.md"
    prompt.parent.mkdir(parents=True, exist_ok=True)
    prompt.write_text("sys", encoding="utf-8")
    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(prompt))
    (tmp_path / "tasks" / "backlog").mkdir(parents=True)
    stub = types.ModuleType("httpx")

    class _Client:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, *args, **kwargs):
            return _FakeResp(_payload(raw))

    stub.Client = _Client
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})
    stub.Timeout = type("Timeout", (), {"__init__": lambda self, *a, **k: None})
    monkeypatch.setitem(sys.modules, "httpx", stub)
    target = (
        bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn") else bridge.brain_turn
    )
    return target(
        "q",
        task_id="424",
        session_id="raw-session",
        include_bundle=False,
        project_root=str(tmp_path),
    )


def _artifact(tmp_path, result):
    return json.loads((tmp_path / result["output_address"]).read_text(encoding="utf-8"))


def _helper(path):
    proc = subprocess.run(
        [sys.executable, str(HELPER), str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return proc, json.loads(proc.stdout)


def _truncated_raw():
    return "````xml\n<hands_implementation_task>\n" + ("x" * 3000)


def test_strict_reject_preserves_raw_bytes(tmp_path, monkeypatch):
    """A strict reject must never destroy the provider's complete raw text."""
    raw = _truncated_raw()
    result = _setup(tmp_path, monkeypatch, raw)
    artifact = _artifact(tmp_path, result)
    assert result["status"] == "REPORT"
    assert result["output"].startswith("[xml-strict-reject]")
    assert "chars withheld" in result["output"]
    assert artifact["full_output"] == raw


def test_semantic_reject_preserves_raw(tmp_path, monkeypatch):
    """A contract-incomplete block remains visible in the raw artifact."""
    raw = (
        "<hands_implementation_task><validation_phase>x</validation_phase>"
        "</hands_implementation_task>"
    )
    result = _setup(tmp_path, monkeypatch, raw)
    artifact = _artifact(tmp_path, result)
    assert result["status"] == "REPORT"
    assert result["output"].startswith("[xml-semantic-reject]")
    assert artifact["full_output"] == raw


def test_block_count_is_truthful(tmp_path, monkeypatch):
    """Block count is a number of blocks, never the JSON byte length."""
    raw = "<hotfix>a</hotfix>\n<hotfix>b</hotfix>"
    result = _setup(tmp_path, monkeypatch, raw)
    artifact = _artifact(tmp_path, result)
    assert result["status"] == "XML_EXTRACTED"
    assert result["block_count"] == 2
    assert artifact["block_count"] == 2
    assert artifact["byte_counts"]["xml_blocks"] != 2


def test_diagnostics_fields_present(tmp_path, monkeypatch):
    """Reject artifacts expose code, raw size, and persistence truth."""
    raw = _truncated_raw()
    result = _setup(tmp_path, monkeypatch, raw)
    artifact = _artifact(tmp_path, result)
    assert artifact["diagnostics"]["code"] == bridge.STRICT_XML_FENCE_FALLBACK_CODE
    assert artifact["raw_bytes"] == len(raw.encode("utf-8"))
    assert isinstance(result["diagnostics"], dict)
    assert result["diagnostics"]["raw_persisted"] is True


def test_transcript_stays_compact_on_reject(tmp_path, monkeypatch):
    """Replay history keeps a preview plus pointer, not the bulky raw body."""
    raw = _truncated_raw()
    result = _setup(tmp_path, monkeypatch, raw)
    transcripts = list((tmp_path / "sessions").rglob("transcript.jsonl"))
    assert transcripts
    rows = [json.loads(line) for line in transcripts[0].read_text().splitlines()]
    assistant = [row for row in rows if row.get("role") == "assistant"][-1]
    assert len(assistant["content"]) < len(raw)
    assert result["output_address"] in assistant["content"]


def test_old_artifact_without_new_keys_reads(tmp_path):
    """Legacy artifacts remain readable by the deterministic helper."""
    path = tmp_path / "legacy.json"
    path.write_text(
        json.dumps(
            {
                "xml_blocks": ["<hotfix>legacy</hotfix>"],
                "full_output": "<hotfix>legacy</hotfix>",
            }
        ),
        encoding="utf-8",
    )
    proc, report = _helper(path)
    assert proc.returncode == 0
    assert report["block_count"] == 1
    assert report["executable"] is True


@pytest.mark.parametrize(
    "raw",
    [
        "````xml\n<hands_implementation_task><validation_phase>a</validation_phase>"
        "<context_phase>b</context_phase><execution_phase>```python\nprint(1)\n```"
        "</execution_phase><bash_phase>c</bash_phase><documentation_phase>d</documentation_phase>"
        "<summary_phase>e</summary_phase></hands_implementation_task>\n````",
        "```xml\n<hands_implementation_task><validation_phase>a</validation_phase>"
        "<context_phase>b</context_phase><execution_phase>```python\nprint(1)\n```"
        "</execution_phase><bash_phase>c</bash_phase><documentation_phase>d</documentation_phase>"
        "<summary_phase>e</summary_phase></hands_implementation_task>\n```",
    ],
)
def test_nested_fence_corpus_no_divergence(tmp_path, raw):
    """The helper and bridge must agree on every supported fence shape."""
    path = tmp_path / "fenced.json"
    path.write_text(
        json.dumps({"full_output": raw, "xml_blocks": []}), encoding="utf-8"
    )
    proc, report = _helper(path)
    assert proc.returncode == 0
    assert report["blocks"] == bridge.extract_xml_blocks(raw)


def test_truncated_block_not_executable_by_helper(tmp_path):
    """A genuinely partial block is visible but never executable."""
    path = tmp_path / "partial.json"
    path.write_text(json.dumps({"full_output": _truncated_raw()}), encoding="utf-8")
    proc, report = _helper(path)
    assert proc.returncode == 0
    assert report["executable"] is False
    assert report["validation_problems"]
