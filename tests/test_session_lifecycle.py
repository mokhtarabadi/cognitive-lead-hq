"""Session ledger, taskless decisions, lint carve-out, analysis lifecycle.

Workstream 4 (GitHub issue 19). RED-first: the session_ledger extensions
(checkpoints, tolerant reader, pending candidates), the decision-server
taskless path (session_id), the ```source-evidence lint carve-out, and
the analysis task type do not exist yet.
"""

import importlib
import json
import shutil
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
BRIDGE_DIR = REPO / "mcp-brain-bridge"
DECISION_DIR = REPO / "mcp-decision-server"
sys.path.insert(0, str(BRIDGE_DIR))

import server as bridge
import session_ledger as ledger


# --- ledger fixtures -------------------------------------------------------

def _sessions(tmp_path, name="proj"):
    proj = tmp_path / name
    (proj / "tasks" / ".sessions").mkdir(parents=True)
    return proj


# --- Part 1: session ledger and checkpoints --------------------------------

def test_start_session_carries_all_required_fields(tmp_path):
    proj = _sessions(tmp_path)
    rec = ledger.start_session("s1", project_root=str(proj))
    for field in ("session_id", "phase", "checkpoints", "request_hash",
                  "response_hash", "retry_counts", "capability_manifest",
                  "approval_events", "transcript_path",
                  "transport_corrections", "final_status"):
        assert field in rec, f"missing ledger field: {field}"
    assert rec["session_id"] == "s1"
    assert rec["checkpoints"] == []
    assert rec["final_status"] == "open"
    assert rec["transcript_path"].endswith(
        "tasks/.sessions/s1/transcript.jsonl")


def test_checkpoint_rejects_unknown_name(tmp_path):
    proj = _sessions(tmp_path)
    ledger.start_session("s1", project_root=str(proj))
    with pytest.raises(ValueError):
        ledger.checkpoint("s1", "nonsense_boundary",
                          project_root=str(proj))


def test_all_nine_checkpoints_accepted_in_order(tmp_path):
    proj = _sessions(tmp_path)
    ledger.start_session("s1", project_root=str(proj))
    assert len(ledger.CHECKPOINTS) == 9
    for name in ledger.CHECKPOINTS:
        ledger.checkpoint("s1", name, project_root=str(proj))
    names = [e["checkpoint"] for e in ledger.read_ledger(
        project_root=str(proj)) if e["event"] == "checkpoint"]
    assert names == list(ledger.CHECKPOINTS)


def test_checkpoints_append_only_and_ordered(tmp_path):
    proj = _sessions(tmp_path)
    ledger.start_session("s1", project_root=str(proj))
    ledger.checkpoint("s1", ledger.CHECKPOINTS[0], project_root=str(proj))
    ledger.checkpoint("s1", ledger.CHECKPOINTS[1], project_root=str(proj))
    path = proj / "tasks" / ".sessions" / "session_ledger.jsonl"
    assert len(path.read_text(encoding="utf-8").splitlines()) == 3
    events = [e["event"] for e in ledger.read_ledger(
        project_root=str(proj))]
    assert events == ["session_started", "checkpoint", "checkpoint"]


def test_reader_tolerates_unknown_fields_and_corrupt_lines(tmp_path):
    proj = _sessions(tmp_path)
    ledger.start_session("s1", project_root=str(proj),
                         future_field="kept")
    path = proj / "tasks" / ".sessions" / "session_ledger.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        fh.write("this is not json\n")
    records = ledger.read_ledger(project_root=str(proj))
    assert len(records) == 1
    assert records[0]["future_field"] == "kept"


def test_pending_candidate_stays_out_of_committed_store(tmp_path):
    proj = _sessions(tmp_path)
    ledger.start_session("s1", project_root=str(proj))
    cand = {"summary": "use X", "verbatim": "use X now"}
    ledger.record_pending_candidate("s1", cand, project_root=str(proj))
    events = [e for e in ledger.read_ledger(project_root=str(proj))
              if e["event"] == "decision_pending"]
    assert len(events) == 1
    assert events[0]["status"] == "pending"
    assert list((proj / "tasks").rglob("DEC-*.json")) == []


def test_approval_promotes_only_via_explicit_record(tmp_path):
    proj = _sessions(tmp_path)
    ledger.start_session("s1", project_root=str(proj))
    cand = {"summary": "use X", "verbatim": "use X now"}
    ledger.record_pending_candidate("s1", cand, project_root=str(proj))
    returned = ledger.promote_pending_candidate(
        "s1", 0, project_root=str(proj))
    assert returned["summary"] == "use X"
    # Promotion alone writes no committed decision: the caller must pass
    # the returned payload to record_manager_decision explicitly.
    assert list((proj / "tasks").rglob("DEC-*.json")) == []
    kinds = [e["event"] for e in ledger.read_ledger(
        project_root=str(proj))]
    assert "decision_approved" in kinds


def test_rejected_candidate_auditable_never_active(tmp_path):
    proj = _sessions(tmp_path)
    ledger.start_session("s1", project_root=str(proj))
    ledger.record_pending_candidate("s1", {"summary": "bad idea"},
                                    project_root=str(proj))
    ledger.resolve_pending_candidate("s1", 0, "rejected",
                                     project_root=str(proj))
    records = ledger.read_ledger(project_root=str(proj))
    assert {e["event"] for e in records} >= {"decision_pending",
                                             "decision_rejected"}
    assert list((proj / "tasks").rglob("DEC-*.json")) == []


# --- Part 2: decision persistence without numeric task ids ------------------

def _load_decision_server():
    sys.modules["redactor"] = _decision_load(
        "decision_redactor", "redactor.py")
    return _decision_load("decision_server", "server.py")


def _decision_load(name, filename):
    spec = importlib.util.spec_from_file_location(
        name, DECISION_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def srv():
    return _load_decision_server()


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    monkeypatch.setenv("DECISION_REPO_PATH", str(tmp_path))
    (tmp_path / "decisions").mkdir()
    real_scripts = (REPO / ".opencode" / "decisions" / "scripts")
    shutil.copytree(real_scripts, tmp_path / "scripts")
    return tmp_path


def _plant_taskless_transcript(root, session_id):
    path = (root / "tasks" / ".sessions" / session_id
            / "transcript.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"role": "user", "content": "ship taskless",
                    "name": "m",
                    "timestamp": "2026-09-08T00:00:00+00:00"}) + "\n",
        encoding="utf-8")
    return path


def _stub_decision_llm(monkeypatch, candidates):
    stub_resp = types.SimpleNamespace(
        status_code=200, text="stub", headers={},
        raise_for_status=lambda: None,
        json=lambda: {
            "output": [
                {"type": "message",
                 "content": [{"type": "output_text",
                              "text": json.dumps(candidates)}]}
            ]
        },
    )

    class _FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, *a, **k):
            return stub_resp

    stub = types.ModuleType("httpx")
    stub.Client = _FakeClient
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            pass

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)


_CANDS = [{
    "verbatim_quote": {"original": "ship taskless",
                       "english_translation": "ship taskless"},
    "extracted_decision": {"summary": "s", "category": "architecture",
                           "rationale": "r", "alternatives": [],
                           "tradeoffs": "t"},
}]


def test_extract_session_id_missing_transcript_returns_empty(
        srv, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    call = srv.extract_session_decisions
    target = call.fn if hasattr(call, "fn") else call
    assert target(session_id="saga-missing") == []


def test_extract_session_id_parses_stubbed_llm(
        srv, tmp_path, monkeypatch):
    _plant_taskless_transcript(tmp_path, "saga2")
    monkeypatch.chdir(tmp_path)
    _stub_decision_llm(monkeypatch, _CANDS)
    call = srv.extract_session_decisions
    target = call.fn if hasattr(call, "fn") else call
    assert target(session_id="saga2") == _CANDS


def test_extract_numeric_task_id_path_unchanged(
        srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        json.dumps({"role": "user", "content": "ship taskless", "name": "m",
                    "timestamp": "2026-09-08T00:00:00+00:00"}) + "\n",
        encoding="utf-8")
    _stub_decision_llm(monkeypatch, _CANDS)
    call = srv.extract_session_decisions
    target = call.fn if hasattr(call, "fn") else call
    assert target(7, transcript_path=str(transcript)) == _CANDS


def test_extract_string_task_id_treated_as_session(
        srv, tmp_path, monkeypatch):
    _plant_taskless_transcript(tmp_path, "abc")
    monkeypatch.chdir(tmp_path)
    _stub_decision_llm(monkeypatch, _CANDS)
    call = srv.extract_session_decisions
    target = call.fn if hasattr(call, "fn") else call
    assert target("abc") == _CANDS


def test_extract_neither_task_nor_session_raises(srv):
    call = srv.extract_session_decisions
    target = call.fn if hasattr(call, "fn") else call
    with pytest.raises(ValueError):
        target()


def test_extract_rejects_bad_session_id(srv):
    call = srv.extract_session_decisions
    target = call.fn if hasattr(call, "fn") else call
    with pytest.raises(ValueError):
        target(session_id="../evil")


def test_sync_status_is_not_approval_status(srv, repo):
    call = srv.get_sync_status
    target = call.fn if hasattr(call, "fn") else call
    assert "approv" not in target().lower()


# --- Part 3: lint carve-out and analysis lifecycle --------------------------

def _lint_mod():
    path = REPO / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_ws4", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_TASK_HEAD = """# Task 99: Lifecycle fixture

**File:** `tasks/backlog/99-test.md`
**Source:** manager
**Type:** {kind}
**Status:** open

## Goal

Prove the fence.

## Local TODOs

- [ ] x

## Acceptance Criteria

- [ ] y

{evidence}

## Risk & Rollback

- **Risk:** none
- **Rollback plan:** revert

## Execution Log & Reasoning

notes

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

<!-- END_GIT_DIFF -->
"""

_VERIFY = """## Verification Evidence

- **Test command:** rtk test pytest tests/ -q
- **Expected result:** pass
- **Actual result:** pass
- **Exit code:** 0
"""

_REPORT = """## Report Evidence

Report: context-reports/analysis-99.md

Result: The saga failed at the transport boundary because project_root
was omitted; the ledger now records the correction.
"""


def test_source_evidence_fence_exempt_from_prose_checks():
    mod = _lint_mod()
    body = _TASK_HEAD.format(
        kind="bug",
        evidence=_VERIFY + "\n```source-evidence\n"
        "verbatim Persian: گزارش خرابی\n"
        "a line with trailing space \n"
        "#looks-like-heading-no-blank-line\n"
        "```\n")
    assert mod._check_markdown_basics(
        body, "tasks/backlog/99-test.md") == []


def test_unclosed_source_evidence_fence_fails():
    mod = _lint_mod()
    body = _TASK_HEAD.format(
        kind="bug",
        evidence=_VERIFY + "\n```source-evidence\nnever closed\n")
    issues = mod._check_markdown_basics(body, "tasks/backlog/99-test.md")
    assert any("source-evidence" in i for i in issues)


def test_unclosed_fence_does_not_exempt_rest():
    mod = _lint_mod()
    body = ("# Task 99: Lifecycle fixture\n"
            "## Goal\n"  # missing blank line before heading
            + _TASK_HEAD.split("## Goal\n", 1)[1].format(
                kind="bug",
                evidence=_VERIFY + "\n```source-evidence\nnever closed\n"))
    issues = mod._check_markdown_basics(body, "tasks/backlog/99-test.md")
    assert any("source-evidence" in i for i in issues)
    assert any("blank line" in i for i in issues)


def test_fence_contents_do_not_satisfy_structure():
    mod = _lint_mod()
    body = _TASK_HEAD.format(
        kind="bug",
        evidence=_VERIFY + "\n```source-evidence\n## Goal\n```\n")
    body = body.replace("## Goal\n\nProve the fence.\n\n", "")
    issues = mod._check_task_file_structure(body, "tasks/backlog/99-test.md")
    assert any("## Goal" in i for i in issues)


def test_structure_checks_continue_outside_fence():
    mod = _lint_mod()
    body = _TASK_HEAD.format(
        kind="bug",
        evidence=_VERIFY + "\n```source-evidence\nverbatim\n```\n")
    body = body.replace("## Risk & Rollback\n", "")
    issues = mod._check_task_file_structure(body, "tasks/backlog/99-test.md")
    assert any("Risk & Rollback" in i for i in issues)


def test_analysis_task_report_evidence_passes():
    mod = _lint_mod()
    body = _TASK_HEAD.format(kind="analysis", evidence=_REPORT)
    assert mod._check_task_file_structure(
        body, "tasks/backlog/99-test.md") == []


def test_analysis_task_blank_result_fails():
    mod = _lint_mod()
    body = _TASK_HEAD.format(
        kind="analysis",
        evidence="## Report Evidence\n\nReport: context-reports/r.md\n\nResult: \n")
    issues = mod._check_task_file_structure(body, "tasks/backlog/99-test.md")
    assert any("Result" in i for i in issues)


def test_analysis_task_missing_report_path_fails():
    mod = _lint_mod()
    body = _TASK_HEAD.format(
        kind="analysis",
        evidence="## Report Evidence\n\nResult: some finding\n")
    issues = mod._check_task_file_structure(body, "tasks/backlog/99-test.md")
    assert any("Report" in i for i in issues)


def test_analysis_task_exit_code_is_not_report():
    mod = _lint_mod()
    body = _TASK_HEAD.format(
        kind="analysis",
        evidence="## Report Evidence\n\nReport: context-reports/r.md\n\n"
        "Result: \n\nExit code: 0\n")
    issues = mod._check_task_file_structure(body, "tasks/backlog/99-test.md")
    assert any("Result" in i for i in issues)


def test_implementation_tasks_unaffected_by_analysis_branch():
    mod = _lint_mod()
    body = _TASK_HEAD.format(kind="bug", evidence=_VERIFY)
    assert mod._check_task_file_structure(
        body, "tasks/backlog/99-test.md") == []


# --- Part 4: brain_turn checkpoint integration -------------------------------

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
    def __init__(self, script, bodies):
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
    stub = types.ModuleType("httpx")
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
                        "content": [{"type": "output_text",
                                     "text": text}]}]}


def _turn_env(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    prompt_file = tmp_path / ".config" / "opencode" / "sys.md"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text("sys", encoding="utf-8")
    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(prompt_file))
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    proj = tmp_path / "proj"
    (proj / "tasks").mkdir(parents=True)
    return proj


def _unsupported_400_text(param):
    return json.dumps({"error": {
        "message": f"Unsupported parameter: '{param}'. Try again.",
        "type": "invalid_request_error",
        "param": param,
        "code": "unsupported_parameter",
    }})


def _ledger_events(proj):
    ledger_path = proj / "tasks" / ".sessions" / "session_ledger.jsonl"
    return [json.loads(line) for line in
            ledger_path.read_text(encoding="utf-8").splitlines()]


def test_brain_turn_emits_ordered_checkpoints(tmp_path, monkeypatch):
    proj = _turn_env(tmp_path, monkeypatch)
    bodies: list = []
    _stub_client(monkeypatch,
                 [_FakeResp(200, "fine", _ok_payload())], bodies)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="999", project_root=str(proj))
    assert result["status"] == "REPORT"
    names = [e.get("checkpoint") for e in _ledger_events(proj)
             if e["event"] == "checkpoint"]
    assert names == ["request_accepted", "preflight_completed",
                     "capability_completed", "transport_started",
                     "response_parsed"]


def test_brain_turn_correction_checkpoint(tmp_path, monkeypatch):
    proj = _turn_env(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
    bodies: list = []
    script = [_FakeResp(400, _unsupported_400_text("temperature")),
              _FakeResp(200, "fine", _ok_payload("recovered"))]
    _stub_client(monkeypatch, script, bodies)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="999", project_root=str(proj))
    assert result["output"] == "recovered"
    names = [e.get("checkpoint") for e in _ledger_events(proj)
             if e["event"] == "checkpoint"]
    assert "transport_correction_or_escalation" in names
