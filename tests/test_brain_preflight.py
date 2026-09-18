"""Unit tests for the brain_turn request preflight (GitHub issue 18).

Offline only: the preflight validator is pure (stdlib, no network), and
the brain_turn wiring tests use the mocked-httpx harness. Every test
here FAILS until ``mcp-brain-bridge/preflight.py`` exists.
"""

import sys
import types as _types
from pathlib import Path

import pytest

BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

import preflight
import server as bridge


def _mk_project(tmp_path, name="proj"):
    proj = tmp_path / name
    (proj / "tasks" / "backlog").mkdir(parents=True)
    return proj


def _clean_env(monkeypatch):
    for key in ("BRAIN_PROJECT_ROOT", "BRAIN_WORKSPACE_ROOT"):
        monkeypatch.delenv(key, raising=False)


# --- resolve_project_root: explicit root is strict ---

def test_explicit_root_with_tasks_resolves(tmp_path):
    proj = _mk_project(tmp_path)
    assert preflight.resolve_project_root(str(proj)) == proj.resolve()


def test_explicit_root_without_tasks_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # cwd HAS no tasks; must not matter
    bare = tmp_path / "bare"
    bare.mkdir()
    with pytest.raises(preflight.PreflightError, match="project_root"):
        preflight.resolve_project_root(str(bare))


def test_explicit_root_missing_raises(tmp_path):
    with pytest.raises(preflight.PreflightError, match="project_root"):
        preflight.resolve_project_root(str(tmp_path / "nope"))


def test_explicit_root_file_not_dir_raises(tmp_path):
    f = tmp_path / "f.txt"
    f.write_text("x", encoding="utf-8")
    with pytest.raises(preflight.PreflightError, match="project_root"):
        preflight.resolve_project_root(str(f))


# --- resolve_project_root: omitted root resolves via chain ---

def test_env_project_root_used_when_omitted(tmp_path, monkeypatch):
    proj = _mk_project(tmp_path)
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.chdir(bare)
    monkeypatch.setenv("BRAIN_PROJECT_ROOT", str(proj))
    assert preflight.resolve_project_root(None) == proj.resolve()


def test_env_root_without_tasks_falls_through_to_walkup(tmp_path, monkeypatch):
    proj = _mk_project(tmp_path)
    sub = proj / "sub"
    sub.mkdir()
    monkeypatch.chdir(sub)
    monkeypatch.setenv("BRAIN_PROJECT_ROOT", str(tmp_path / "bare"))
    (tmp_path / "bare").mkdir()
    assert preflight.resolve_project_root(None) == proj.resolve()


def test_walkup_finds_parent_tasks(tmp_path, monkeypatch):
    proj = _mk_project(tmp_path)
    deep = proj / "a" / "b"
    deep.mkdir(parents=True)
    monkeypatch.chdir(deep)
    _clean_env(monkeypatch)
    assert preflight.resolve_project_root(None) == proj.resolve()


def test_nothing_resolves_raises_with_remedy(tmp_path, monkeypatch):
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.chdir(bare)
    _clean_env(monkeypatch)
    with pytest.raises(preflight.PreflightError, match="project_root"):
        preflight.resolve_project_root(None)


# --- task / session binding ---

def test_task_id_bare_digits_ok(tmp_path):
    proj = _mk_project(tmp_path)
    req = preflight.validate_request(task_id="257", project_root=str(proj))
    assert req.binding == "task"
    assert req.task_id == "257"
    assert req.session_id is None


def test_task_id_suffix_rejected(tmp_path):
    proj = _mk_project(tmp_path)
    with pytest.raises(preflight.PreflightError, match="task_id"):
        preflight.validate_request(task_id="215qa", project_root=str(proj))


def test_session_id_ok(tmp_path):
    proj = _mk_project(tmp_path)
    req = preflight.validate_request(session_id="cando-828",
                                     project_root=str(proj))
    assert req.binding == "session"
    assert req.session_id == "cando-828"


def test_session_id_bad_chars_rejected(tmp_path):
    proj = _mk_project(tmp_path)
    with pytest.raises(preflight.PreflightError, match="session_id"):
        preflight.validate_request(session_id="a/b", project_root=str(proj))


def test_both_ids_rejected(tmp_path):
    proj = _mk_project(tmp_path)
    with pytest.raises(preflight.PreflightError, match="exactly one"):
        preflight.validate_request(task_id="257", session_id="s",
                                   project_root=str(proj))


def test_neither_id_is_oneoff_without_root(tmp_path, monkeypatch):
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.chdir(bare)
    _clean_env(monkeypatch)
    req = preflight.validate_request()
    assert req.binding == "one-off"
    assert req.project_root is None


# --- stage / flags / kanban / required_tools ---

def test_stage_allowlist_ok(tmp_path):
    proj = _mk_project(tmp_path)
    req = preflight.validate_request(task_id="1", project_root=str(proj),
                                     stage="qa")
    assert req.stage == "qa"


def test_stage_unknown_rejected(tmp_path):
    proj = _mk_project(tmp_path)
    with pytest.raises(preflight.PreflightError, match="stage"):
        preflight.validate_request(task_id="1", project_root=str(proj),
                                   stage="bogus")


def test_flags_must_be_bool(tmp_path):
    proj = _mk_project(tmp_path)
    with pytest.raises(preflight.PreflightError, match="include_bundle"):
        preflight.validate_request(task_id="1", project_root=str(proj),
                                   include_bundle="yes")
    with pytest.raises(preflight.PreflightError, match="include_diff"):
        preflight.validate_request(task_id="1", project_root=str(proj),
                                   include_diff=1)


def test_kanban_path_under_tasks_ok(tmp_path):
    proj = _mk_project(tmp_path)
    req = preflight.validate_request(task_id="1", project_root=str(proj),
                                     kanban_path="tasks/qa/257-x.md")
    assert req.kanban_path == (proj.resolve() / "tasks" / "qa" / "257-x.md")


def test_kanban_path_escape_rejected(tmp_path):
    proj = _mk_project(tmp_path)
    with pytest.raises(preflight.PreflightError, match="kanban_path"):
        preflight.validate_request(task_id="1", project_root=str(proj),
                                   kanban_path="../outside.md")
    with pytest.raises(preflight.PreflightError, match="kanban_path"):
        preflight.validate_request(task_id="1", project_root=str(proj),
                                   kanban_path="/etc/passwd")


def test_required_tools_typechecked(tmp_path):
    proj = _mk_project(tmp_path)
    req = preflight.validate_request(task_id="1", project_root=str(proj),
                                     required_tools=["question"])
    assert req.required_tools == ("question",)
    with pytest.raises(preflight.PreflightError, match="required_tools"):
        preflight.validate_request(task_id="1", project_root=str(proj),
                                   required_tools="question")
    with pytest.raises(preflight.PreflightError, match="required_tools"):
        preflight.validate_request(task_id="1", project_root=str(proj),
                                   required_tools=[123])


# --- brain_turn wiring: preflight runs before transport ---

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


class _FakeClient:
    def __init__(self, script, **kwargs):
        self._script = list(script)
        self.calls = 0

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def post(self, url, json=None, headers=None, **kwargs):
        self.calls += 1
        item = self._script.pop(0) if len(self._script) > 1 else self._script[0]
        if isinstance(item, Exception):
            raise item
        return item


def _ok_payload(text="ok"):
    return {"output": [{"type": "message",
                        "content": [{"type": "output_text", "text": text}]}]}


def _mk_bridge_client(monkeypatch, script):
    clients = []

    class _CapClient(_FakeClient):
        def post(self, url, json=None, headers=None, **kwargs):
            return super().post(url, json=json, headers=headers, **kwargs)

    def _factory(*a, **k):
        client = _CapClient(script)
        clients.append(client)
        return client

    stub = _types.ModuleType("httpx")
    stub.Client = _factory
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            self.args, self.kwargs = a, k

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)
    return clients


def _mk_sys_prompt(tmp_path, monkeypatch, text="sys"):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    prompt_file = tmp_path / ".config" / "opencode" / "sys.md"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(text, encoding="utf-8")
    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(prompt_file))


def _brain_turn():
    call = bridge.brain_turn
    return call.fn if hasattr(call, "fn") else call


def test_brain_turn_bad_explicit_root_raises_before_transport(
        tmp_path, monkeypatch):
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    clients = _mk_bridge_client(
        monkeypatch, [_FakeResp(200, "fine", _ok_payload())])
    with pytest.raises(preflight.PreflightError):
        _brain_turn()("q", task_id="257",
                      project_root=str(tmp_path / "bare-no-tasks"))
    assert clients == []


def test_brain_turn_task_and_session_rejected_before_transport(
        tmp_path, monkeypatch):
    proj = _mk_project(tmp_path)
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    clients = _mk_bridge_client(
        monkeypatch, [_FakeResp(200, "fine", _ok_payload())])
    with pytest.raises(preflight.PreflightError, match="exactly one"):
        _brain_turn()("q", task_id="257", session_id="s",
                      project_root=str(proj))
    assert clients == []


def test_brain_turn_legacy_shape_still_works(tmp_path, monkeypatch):
    proj = _mk_project(tmp_path)
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())])
    result = _brain_turn()("q", task_id="257", project_root=str(proj))
    assert result["status"] == "REPORT"
    assert result["output"] == "ok"
