"""Unit tests for mcp-brain-bridge (Task 190).

Offline only: covers the XML extractor, the system-prompt loader, the
Responses-API text parser, and env fallbacks. The live LLM path
(httpx POST) is never touched.
"""

import os
import sys
from pathlib import Path

import pytest

BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

import server as bridge


def test_extract_single_implementation_block():
    out = 'Think <hands_implementation_task>{"a": 1}</hands_implementation_task> tail'
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert blocks[0].startswith("<hands_implementation_task>")


def test_extract_multiple_blocks_in_order():
    out = (
        "<hands_discovery_task>one</hands_discovery_task> noise "
        "<failure_report>two</failure_report>"
    )
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 2
    assert blocks[0].startswith("<hands_discovery_task>")
    assert blocks[1].startswith("<failure_report>")


def test_extract_no_xml_returns_empty():
    assert bridge.extract_xml_blocks("Just a plain answer, no blocks.") == []


def test_extract_ignores_unknown_tags():
    out = "<reasoning_log>thinking</reasoning_log>"
    assert bridge.extract_xml_blocks(out) == []


def test_load_system_prompt_explicit_path(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    target = tmp_path / ".config" / "opencode" / "prompt.md"
    target.parent.mkdir(parents=True)
    target.write_text("hello prompt", encoding="utf-8")
    assert bridge.load_system_prompt(str(target)) == "hello prompt"


def test_load_system_prompt_missing_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("BRAIN_SYSTEM_PROMPT", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    with pytest.raises(FileNotFoundError):
        bridge.load_system_prompt(
            str(tmp_path / ".config" / "opencode" / "nope.md"))


def test_load_system_prompt_prefers_env(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    target = tmp_path / ".config" / "opencode" / "env-prompt.md"
    target.parent.mkdir(parents=True)
    target.write_text("from env", encoding="utf-8")
    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(target))
    assert bridge.load_system_prompt() == "from env"


def test_brain_model_default_and_override(monkeypatch):
    monkeypatch.delenv("BRAIN_MODEL", raising=False)
    assert bridge._get_brain_model() == "muse-spark-1.3-contributor-free"
    monkeypatch.setenv("BRAIN_MODEL", "  ")
    assert bridge._get_brain_model() == "muse-spark-1.3-contributor-free"
    monkeypatch.setenv("BRAIN_MODEL", "custom/model")
    assert bridge._get_brain_model() == "custom/model"


def test_history_missing_task_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    assert bridge.load_history("fresh-task-1") == []


def test_history_append_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    bridge.append_turn("task-9", "user", "hello brain")
    bridge.append_turn("task-9", "assistant", "hello hands")
    history = bridge.load_history("task-9")
    assert history == [
        {"role": "user", "content": "hello brain",
         "model": None, "prompt_hash": None, "truncated": 0},
        {"role": "assistant", "content": "hello hands",
         "model": None, "prompt_hash": None, "truncated": 0},
    ]


def test_history_skips_corrupt_lines(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    bridge.append_turn("task-7", "user", "good line")
    path = tmp_path / "sessions" / "task-7" / "transcript.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        fh.write("not json at all\n")
        fh.write('{"role": "alien", "content": "x"}\n')
    assert bridge.load_history("task-7") == [
        {"role": "user", "content": "good line",
         "model": None, "prompt_hash": None, "truncated": 0}
    ]


def test_history_limit_caps_oldest_first(tmp_path, monkeypatch):
    # 45 appends exceed the 30-message compaction trigger, so load
    # compacts to a summary + the last 10 (the 40-cap stays as backstop).
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    for i in range(45):
        bridge.append_turn("task-5", "user", f"msg {i}")
    history = bridge.load_history("task-5")
    assert len(history) == 11
    assert "compacted" in history[0]
    assert [t["content"] for t in history[1:]] == [f"msg {i}" for i in range(35, 45)]


def test_task_id_sanitized_against_traversal(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    with pytest.raises(ValueError):
        bridge.append_turn("../../evil", "user", "x")
    with pytest.raises(ValueError):
        bridge.load_history("...")


def test_parse_responses_text_message_items():
    data = {
        "output": [
            {"type": "reasoning", "status": "completed"},
            {
                "type": "message",
                "content": [
                    {"type": "output_text", "text": "Hello"},
                    {"type": "output_text", "text": "World"},
                ],
            },
        ]
    }
    assert bridge.parse_responses_text(data) == "Hello\nWorld"


def test_parse_responses_text_empty_and_malformed():
    assert bridge.parse_responses_text({}) == ""
    assert bridge.parse_responses_text({"output": "nope"}) == ""
    assert bridge.parse_responses_text({"output": [{"type": "other"}]}) == ""


def test_responses_url_default_and_override(monkeypatch):
    monkeypatch.delenv("BRAIN_API_BASE", raising=False)
    assert bridge._responses_url() == "http://127.0.0.1:8081/zen/resp/responses"
    monkeypatch.setenv("BRAIN_API_BASE", "http://x:1/base/")
    assert bridge._responses_url() == "http://x:1/base/responses"


# --- hotfix hardening (QA_REJECTED follow-up, mocked HTTP only) ---

import time as _time
import types as _types


class _FakeResp:
    def __init__(self, status_code=200, text="", payload=None, ctype="application/json"):
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
        self.last_body = None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def post(self, url, json=None, headers=None, **kwargs):
        self.calls += 1
        self.last_body = json
        item = self._script.pop(0) if len(self._script) > 1 else self._script[0]
        if isinstance(item, Exception):
            raise item
        return item


def _ok_payload(text="ok"):
    return {"output": [{"type": "message",
                        "content": [{"type": "output_text", "text": text}]}]}


def _stub_httpx(monkeypatch):
    stub = _types.ModuleType("httpx")
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            self.args, self.kwargs = a, k

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)
    return stub


def test_api_key_empty_raises(monkeypatch):
    monkeypatch.delenv("BRAIN_API_KEY", raising=False)
    import pytest as _pt
    with _pt.raises(RuntimeError, match="empty"):
        bridge._get_api_key()


def test_post_retry_succeeds_after_429(monkeypatch):
    _stub_httpx(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setattr(_time, "sleep", lambda s: None)
    script = [_FakeResp(429, "slow down"),
              _FakeResp(200, "fine", _ok_payload())]
    resp, attempts = bridge._post_with_retry(
        _FakeClient(script), "http://x/responses", {})
    assert resp.status_code == 200
    assert attempts == 2


def test_post_final_500_raises_without_key_leak(monkeypatch):
    _stub_httpx(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-SECRET-XYZ")
    monkeypatch.setattr(_time, "sleep", lambda s: None)
    script = [_FakeResp(500, "boom")]
    import pytest as _pt
    with _pt.raises(RuntimeError) as exc:
        bridge._post_with_retry(_FakeClient(script), "http://x/responses", {})
    msg = str(exc.value)
    assert "500" in msg
    assert "SECRET" not in msg


def test_resp_json_non_json_raises():
    import pytest as _pt
    resp = _FakeResp(200, "<html>not json</html>", ValueError("bad"), "text/html")
    with _pt.raises(RuntimeError, match="non-JSON"):
        bridge._resp_json(resp)


def test_task_id_allowlist_rejects_separators(tmp_path, monkeypatch):
    import pytest as _pt
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    with _pt.raises(ValueError):
        bridge.load_history("a/b")
    with _pt.raises(ValueError):
        bridge.load_history("")


def test_extract_ignores_fenced_blocks():
    fenced = "```json\n<hands_implementation_task>{\"a\": 1}</hands_implementation_task>\n```"
    assert bridge.extract_xml_blocks(fenced) == []
    mixed = fenced + "\n<hands_implementation_task>{\"b\": 2}</hands_implementation_task>"
    blocks = bridge.extract_xml_blocks(mixed)
    assert len(blocks) == 1
    assert '"b": 2' in blocks[0]


def test_brain_turn_truncates_oldest_history(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    prompt_file = tmp_path / ".config" / "opencode" / "sys.md"
    prompt_file.parent.mkdir(parents=True)
    prompt_file.write_text("sys", encoding="utf-8")
    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(prompt_file))
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    for _ in range(10):
        bridge.append_turn("bigtask", "user", "x" * 30000)
    holder = {}
    script = [_FakeResp(200, "fine", _ok_payload())]

    class _CapClient(_FakeClient):
        def post(self, url, json=None, headers=None, **kwargs):
            holder["body"] = json
            return super().post(url, json=json, headers=headers, **kwargs)

    stub = _types.ModuleType("httpx")
    stub.Client = lambda *a, **k: _CapClient(script)
    stub.TimeoutException = Exception
    stub.TransportError = Exception

    class _Timeout:
        def __init__(self, *a, **k):
            pass

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="bigtask")
    assert result["status"] == "REPORT"
    assert result["output"] == "ok"
    big_turns = [t for t in holder["body"]["input"]
                 if t.get("content", "").startswith("x")]
    assert 1 <= len(big_turns) < 10


# --- Hotfix-2 new tests (mocked httpx only) ---

def _mk_bridge_client(monkeypatch, script, holder=None):
    class _CapClient(_FakeClient):
        def post(self, url, json=None, headers=None, **kwargs):
            if holder is not None:
                holder["body"] = json
            return super().post(url, json=json, headers=headers, **kwargs)

    stub = _types.ModuleType("httpx")
    stub.Client = lambda *a, **k: _CapClient(script)
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            self.args, self.kwargs = a, k

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)
    return stub


def _mk_sys_prompt(tmp_path, monkeypatch, text="sys"):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    prompt_file = tmp_path / ".config" / "opencode" / "sys.md"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(text, encoding="utf-8")
    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(prompt_file))


def test_post_overall_deadline_fast_fail(monkeypatch):
    _stub_httpx(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setattr(_time, "sleep", lambda s: None)
    monkeypatch.setattr(bridge, "_OVERALL_DEADLINE_S", 0)
    import pytest as _pt
    with _pt.raises(RuntimeError, match="deadline"):
        bridge._post_with_retry(
            _FakeClient([_FakeResp(500, "boom")]), "http://x/responses", {})


def test_post_retry_after_honored(monkeypatch):
    _stub_httpx(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    sleeps = []
    monkeypatch.setattr(_time, "sleep", lambda s: sleeps.append(s))
    r429 = _FakeResp(429, "slow down")
    r429.headers["Retry-After"] = "2"
    script = [r429, _FakeResp(200, "fine", _ok_payload())]
    resp, _ = bridge._post_with_retry(
        _FakeClient(script), "http://x/responses", {})
    assert resp.status_code == 200
    assert sleeps and sleeps[0] >= 2


def test_strip_quadruple_tilde_unclosed_fences():
    quad = "````\n<hands_implementation_task>{\"a\": 1}</hands_implementation_task>\n````"
    assert bridge.extract_xml_blocks(quad) == []
    tilde = "~~~\n<hands_implementation_task>{\"a\": 1}</hands_implementation_task>\n~~~"
    assert bridge.extract_xml_blocks(tilde) == []
    unclosed = "```json\n<hands_implementation_task>{\"a\": 1}</hands_implementation_task>\n"
    assert bridge.extract_xml_blocks(unclosed) == []
    assert bridge._last_fence_drops, "drops must be recorded"


def test_brain_turn_fence_only_reports_debug(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    fenced = "```json\n{\"note\": \"just docs\"}\n```"
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload(fenced))])
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q")
    assert result["status"] == "REPORT"
    assert result["debug"]["fenced_blocks"] >= 1
    assert any("just docs" in s for s in result["debug"]["snippets"])


def test_brain_turn_budget_return_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    for _ in range(10):
        bridge.append_turn("fieldstask", "user", "x" * 30000)
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())])
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="fieldstask")
    assert set(("truncated_count", "budget_chars", "retry_count")) <= set(result)


def _mk_tasks_root(tmp_path):
    tasks = tmp_path / "tasks" / "backlog"
    tasks.mkdir(parents=True)
    (tasks / "200-foo.md").write_text(
        "# T\n\nGoal line.\n\n<!-- BEGIN_GIT_DIFF -->\nDIFFSTUFF\n<!-- END_GIT_DIFF -->\n",
        encoding="utf-8")
    return tmp_path


def test_task_attach_strip_pure():
    cleaned, omitted, truncated = bridge._strip_task_diff(
        "head\n<!-- BEGIN_GIT_DIFF -->\na\nb\n<!-- END_GIT_DIFF -->\ntail",
        "tasks/x.md")
    assert "DIFFSTUFF" not in cleaned and "a\nb" not in cleaned
    assert "head" in cleaned and "tail" in cleaned
    assert omitted == 4  # block lines incl. markers (impl counts span newlines + 1)
    assert truncated is False
    assert "read_file" in cleaned


def test_task_attach_resolve_exact_and_fallback(tmp_path, monkeypatch):
    _mk_tasks_root(tmp_path)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    found = bridge._resolve_task_file("200-foo")
    assert found is not None and found.name == "200-foo.md"
    fallback = bridge._resolve_task_file("200-foo-qa")
    assert fallback is not None and fallback.name == "200-foo.md"
    assert bridge._resolve_task_file("nope-no-file") is None


def test_task_attach_unresolvable_empty(tmp_path, monkeypatch):
    _mk_tasks_root(tmp_path)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    assert bridge._build_task_attach("nope-no-file") == ""


def test_brain_turn_task_attach_in_body(tmp_path, monkeypatch):
    _mk_tasks_root(tmp_path)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))])
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="200-foo")
    assert result["status"] == "REPORT"
    user_line = (tmp_path / "sessions" / "200-foo" / "transcript.jsonl").read_text(
        encoding="utf-8").splitlines()[0]
    assert "[task-file:200-foo:" in user_line
    assert "Goal line." in user_line
    assert "DIFFSTUFF" not in user_line


def test_brain_turn_task_attach_no_duplicate(tmp_path, monkeypatch):
    _mk_tasks_root(tmp_path)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))])
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("[task-file:200-foo: 200-foo.md]\nq", task_id="200-foo")
    assert result["status"] == "REPORT"
    user_line = (tmp_path / "sessions" / "200-foo" / "transcript.jsonl").read_text(
        encoding="utf-8").splitlines()[0]
    assert user_line.count("[task-file:200-foo:") == 1


def test_brain_turn_unresolvable_task_id_succeeds(tmp_path, monkeypatch):
    _mk_tasks_root(tmp_path)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))])
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="nope-no-file")
    assert result["status"] == "REPORT"
    assert result["output"] == "ok"


def test_brain_turn_temperature_omitted_unless_set(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    holder = {}
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    target("q")
    assert "temperature" not in holder["body"]
    assert "reasoning_effort" in holder["body"]
    monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
    holder2 = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder2)
    target("q2")
    assert holder2["body"]["temperature"] == 0.7
    assert "reasoning_effort" not in holder2["body"]


def test_long_task_id_error_carries_migration_hint(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    import pytest as _pt
    with _pt.raises(ValueError, match="migrat"):
        bridge.load_history("a" * 65)


def test_invalid_effort_value_raises(monkeypatch):
    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "bad effort!!")
    import pytest as _pt
    with _pt.raises(ValueError):
        bridge._get_reasoning_effort()


# --- context bundle / file tools (mocked/offline only) ---

def _unwrap(tool):
    return tool.fn if hasattr(tool, "fn") else tool


def _mk_workspace(tmp_path, files):
    ws = tmp_path / "ws"
    for rel, text in files.items():
        target = ws / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return ws


def test_bundle_skips_missing_file_with_marker(tmp_path, monkeypatch):
    ws = _mk_workspace(tmp_path, {
        "agents/cognitive-executor.md": "exec content",
        "docs/conventions.md": "conv",
    })
    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
    out = _unwrap(bridge.get_context_bundle)()
    assert "=== agents/cognitive-executor.md ===" in out
    assert "exec content" in out
    assert "[missing: docs/architecture.md]" in out
    assert "[missing: DESIGN.md]" in out


def test_bundle_truncates_large_file(tmp_path, monkeypatch):
    big = "x" * 65000
    ws = _mk_workspace(tmp_path, {"DESIGN.md": big})
    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
    out = _unwrap(bridge.get_context_bundle)()
    assert "[truncated]" in out
    section = out.split("=== DESIGN.md ===")[1]
    assert len(section) < len(big) + 5000


def test_read_file_offset_limit(tmp_path, monkeypatch):
    ws = _mk_workspace(tmp_path, {"notes.md": "a\nb\nc\nd\ne\n"})
    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
    result = _unwrap(bridge.read_file)("notes.md", offset=2, limit=2)
    assert result["total_lines"] == 5
    assert result["lines"] == ["2: b", "3: c"]


def test_read_file_rejects_traversal(tmp_path, monkeypatch):
    ws = _mk_workspace(tmp_path, {"notes.md": "hi\n"})
    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
    import pytest as _pt
    with _pt.raises(ValueError):
        _unwrap(bridge.read_file)("../evil.md")
    outside = tmp_path / "outside.md"
    outside.write_text("evil\n", encoding="utf-8")
    with _pt.raises(ValueError):
        _unwrap(bridge.read_file)(str(outside))


def test_read_file_rejects_bad_extension(tmp_path, monkeypatch):
    ws = _mk_workspace(tmp_path, {"run.py": "print(1)\n"})
    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
    import pytest as _pt
    with _pt.raises(ValueError):
        _unwrap(bridge.read_file)("run.py")


def test_grep_finds_planted_string(tmp_path, monkeypatch):
    ws = _mk_workspace(tmp_path, {
        "docs/a.md": "hello PLANTED_NEEDLE world\nsecond line\n",
        "notes.txt": "nothing here\n",
    })
    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
    hits = _unwrap(bridge.grep_files)("PLANTED_NEEDLE")
    assert any("docs/a.md:1:" in h and "PLANTED_NEEDLE" in h for h in hits)


def test_grep_skips_git(tmp_path, monkeypatch):
    ws = _mk_workspace(tmp_path, {
        "notes.md": "visible SKIPME_GIT_TEST\n",
    })
    git_file = ws / ".git" / "hidden.md"
    git_file.parent.mkdir(parents=True, exist_ok=True)
    git_file.write_text("hidden SKIPME_GIT_TEST\n", encoding="utf-8")
    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
    hits = _unwrap(bridge.grep_files)("SKIPME_GIT_TEST")
    assert any("notes.md" in h for h in hits)
    assert not any("/.git/" in h or h.startswith(".git/") for h in hits)


def _mk_bundle_ws(tmp_path, monkeypatch):
    ws = _mk_workspace(tmp_path, {
        "agents/cognitive-executor.md": "bundle-content",
    })
    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    return ws


def test_brain_turn_include_bundle_prepends(tmp_path, monkeypatch):
    _mk_bundle_ws(tmp_path, monkeypatch)
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
    target = _unwrap(bridge.brain_turn)
    target("tiny question")
    user_msgs = [t for t in holder["body"]["input"] if t.get("role") == "user"]
    assert user_msgs
    assert "=== agents/cognitive-executor.md ===" in user_msgs[-1]["content"]
    assert user_msgs[-1]["content"].rstrip().endswith("tiny question")
    # system prompt untouched by the bundle
    assert holder["body"]["input"][0]["role"] == "system"
    assert "=== agents/cognitive-executor.md ===" not in holder["body"]["input"][0]["content"]


def test_brain_turn_include_bundle_false_skips(tmp_path, monkeypatch):
    _mk_bundle_ws(tmp_path, monkeypatch)
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
    target = _unwrap(bridge.brain_turn)
    target("tiny question", include_bundle=False)
    user_msgs = [t for t in holder["body"]["input"] if t.get("role") == "user"]
    assert "=== agents/cognitive-executor.md ===" not in user_msgs[-1]["content"]
    assert user_msgs[-1]["content"] == "tiny question"


def test_brain_turn_no_duplicate_bundle(tmp_path, monkeypatch):
    _mk_bundle_ws(tmp_path, monkeypatch)
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
    target = _unwrap(bridge.brain_turn)
    pre = "=== agents/cognitive-executor.md ===\nalready there\ntiny question"
    target(pre)
    user_msgs = [t for t in holder["body"]["input"] if t.get("role") == "user"]
    assert user_msgs[-1]["content"].count("=== agents/cognitive-executor.md ===") == 1


def test_load_history_skips_monster_lines(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    path = bridge._transcript_path("big")
    path.parent.mkdir(parents=True, exist_ok=True)
    import json as _json
    good = _json.dumps({"role": "user", "content": "hello"})
    path.write_text(good + "\n" + "z" * 200_001 + "\n" + good + "\n",
                    encoding="utf-8")
    turns = bridge.load_history("big")
    # File exceeds _COMPACT_FILE_BYTES (monster line) → byte trigger
    # compacts: junk purged, summary + the 2 valid turns kept.
    assert [t["content"] for t in turns][1:] == ["hello", "hello"]
    assert turns[0].get("compacted") is True
    assert bridge._last_load_stats["skipped"] >= 1
    again = bridge.load_history("big")  # idempotent: no re-compaction
    assert [t["content"] for t in again] == [t["content"] for t in turns]


# --- hotfix follow-up: merge + atomicity + bounds (QA_REJECTED round 1) ---

def test_compact_merges_prior_summary(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _fill_turns("merge", 35)
    first = bridge.load_history("merge")
    assert len(first) == 11
    assert first[0].get("compacted_count") == 35
    _fill_turns("merge", 25, prefix="more")
    second = bridge.load_history("merge")
    assert len(second) == 11
    assert second[0].get("compacted_count") == 35 + 35
    assert "compacted" in second[0]


def test_compact_skips_corrupt_lines(tmp_path, monkeypatch):
    import json as _json
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    path = bridge._transcript_path("corrupt")
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for i in range(35):
        lines.append(_json.dumps({"role": "user", "content": f"ok {i}"}))
    lines.insert(3, "{not json")
    lines.insert(10, _json.dumps({"role": "nope", "content": "x"}))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    turns = bridge.load_history("corrupt")
    assert len(turns) == 11
    assert bridge._last_load_stats["skipped"] >= 2


def test_payload_contains_only_role_content(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    bridge.append_turn("pure", "user", "hi", model="m",
                       prompt_hash="h", truncated=3)
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
    target = _unwrap(bridge.brain_turn)
    target("q", task_id="pure")
    for item in holder["body"]["input"]:
        assert set(item.keys()) == {"role", "content"}


def test_old_records_without_metadata_load(tmp_path, monkeypatch):
    import json as _json
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    path = bridge._transcript_path("legacy")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _json.dumps({"role": "user", "content": "old"}) + "\n"
        + _json.dumps({"role": "assistant", "content": "older"}) + "\n",
        encoding="utf-8")
    turns = bridge.load_history("legacy")
    assert turns == [{"role": "user", "content": "old"},
                     {"role": "assistant", "content": "older"}]


def test_large_turns_trigger_byte_compaction(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    for i in range(10):
        bridge.append_turn("huge", "user", "y" * 30000 + f" {i}")
    turns = bridge.load_history("huge")
    assert len(turns) == 11
    assert turns[0].get("compacted") is True


# --- Task 194: transcript compaction + per-record traceability ---

def _fill_turns(task, n, prefix="msg"):
    for i in range(n):
        role = "user" if i % 2 == 0 else "assistant"
        bridge.append_turn(task, role, f"{prefix} {i}")


def test_compact_fifty_to_summary_plus_ten(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _fill_turns("c50", 50)
    turns = bridge.load_history("c50")
    assert len(turns) == 11
    assert turns[0]["role"] == "assistant" and "compacted" in turns[0]
    assert [t["content"] for t in turns[1:]] == [f"msg {i}" for i in range(40, 50)]


def test_compact_summary_bounded_and_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _fill_turns("cbound", 50)
    first = bridge.load_history("cbound")
    assert len(first[0]["content"]) <= 4000
    second = bridge.load_history("cbound")
    assert second == first  # 11 records: no re-compaction on reload


def test_records_carry_metadata_keys(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    bridge.append_turn("m1", "user", "hi", model="m-x",
                       prompt_hash="ab" * 32, truncated=3)
    (turn,) = bridge.load_history("m1")
    assert turn["model"] == "m-x"
    assert turn["prompt_hash"] == "ab" * 32
    assert turn["truncated"] == 3


def test_append_defaults_stay_compatible(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    bridge.append_turn("m0", "user", "hi")
    (turn,) = bridge.load_history("m0")
    assert turn["model"] is None
    assert turn["prompt_hash"] is None
    assert turn["truncated"] == 0


def test_brain_turn_writes_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    prompt_file = tmp_path / ".config" / "opencode" / "sys.md"
    prompt_file.parent.mkdir(parents=True)
    prompt_file.write_text("sys", encoding="utf-8")
    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(prompt_file))
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setenv("BRAIN_MODEL", "test-model-1")
    script = [_FakeResp(200, "fine", _ok_payload())]

    class _CapClient(_FakeClient):
        def post(self, url, json=None, headers=None, **kwargs):
            return super().post(url, json=json, headers=headers, **kwargs)

    stub = _types.ModuleType("httpx")
    stub.Client = lambda *a, **k: _CapClient(script)
    stub.TimeoutException = Exception
    stub.TransportError = Exception

    class _Timeout:
        def __init__(self, *a, **k):
            pass

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("hello", task_id="meta")
    assert result["output"] == "ok"
    turns = bridge.load_history("meta")
    assert len(turns) == 2
    assert turns[0]["model"] == "test-model-1"
    assert len(turns[0]["prompt_hash"]) == 64
    assert turns[1]["truncated"] >= 0


def test_taxonomy_fatal_400_no_retry(monkeypatch):
    _stub_httpx(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    client = _FakeClient([_FakeResp(400, "bad request")])
    with pytest.raises(RuntimeError, match="no retry"):
        bridge._post_with_retry(client, "http://x/responses", {})
    assert client.calls == 1


def test_taxonomy_fatal_401_no_retry(monkeypatch):
    _stub_httpx(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    client = _FakeClient([_FakeResp(401, "unauthorized")])
    with pytest.raises(RuntimeError, match="401"):
        bridge._post_with_retry(client, "http://x/responses", {})
    assert client.calls == 1


def test_taxonomy_retryable_503_then_200(monkeypatch):
    import time as _tmod
    _stub_httpx(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setattr(_tmod, "sleep", lambda s: None)
    script = [_FakeResp(503, "busy"), _FakeResp(200, "fine", {"ok": True})]
    resp, attempts = bridge._post_with_retry(_FakeClient(script), "http://x/responses", {})
    assert resp.status_code == 200
    assert attempts == 2


# --- hotfix taxonomy per-class tests (Step 4-9, direct _post unit) ---

def _ensure_httpx_exc(monkeypatch):
    import sys as _sysmod
    _stub_httpx(monkeypatch)
    _sysmod.modules["httpx"].TimeoutException = type(
        "TimeoutException", (Exception,), {})
    _sysmod.modules["httpx"].TransportError = type(
        "TransportError", (Exception,), {})
    return _sysmod.modules["httpx"]


def test_taxonomy_fatal_403_no_retry(monkeypatch):
    _ensure_httpx_exc(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    client = _FakeClient([_FakeResp(403, "forbidden")])
    with pytest.raises(RuntimeError, match="no retry"):
        bridge._post_with_retry(client, "http://x/responses", {})
    assert client.calls == 1


def test_taxonomy_fatal_404_no_retry(monkeypatch):
    _ensure_httpx_exc(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    client = _FakeClient([_FakeResp(404, "not here")])
    with pytest.raises(RuntimeError, match="no retry"):
        bridge._post_with_retry(client, "http://x/responses", {})
    assert client.calls == 1


def test_taxonomy_fatal_422_no_retry(monkeypatch):
    _ensure_httpx_exc(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    client = _FakeClient([_FakeResp(422, "unprocessable")])
    with pytest.raises(RuntimeError, match="no retry"):
        bridge._post_with_retry(client, "http://x/responses", {})
    assert client.calls == 1


def test_taxonomy_retryable_429_then_200(monkeypatch):
    import time as _tmod
    _ensure_httpx_exc(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setattr(_tmod, "sleep", lambda s: None)
    script = [_FakeResp(429, "slow"), _FakeResp(200, "fine", {"ok": True})]
    resp, attempts = bridge._post_with_retry(
        _FakeClient(script), "http://x/responses", {})
    assert resp.status_code == 200
    assert attempts == 2


def test_taxonomy_timeout_then_200(monkeypatch):
    import time as _tmod
    httpx_stub = _ensure_httpx_exc(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setattr(_tmod, "sleep", lambda s: None)
    script = [httpx_stub.TimeoutException("timed out"),
              _FakeResp(200, "fine", {"ok": True})]
    resp, attempts = bridge._post_with_retry(
        _FakeClient(script), "http://x/responses", {})
    assert resp.status_code == 200
    assert attempts == 2


def test_taxonomy_message_contract(monkeypatch):
    _ensure_httpx_exc(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-SECRET-XYZ")
    client = _FakeClient([_FakeResp(403, "denied detail")])
    with pytest.raises(RuntimeError) as exc:
        bridge._post_with_retry(client, "http://x/responses", {})
    msg = str(exc.value)
    assert "403" in msg and "responses" in msg and "denied detail" in msg
    assert "SECRET" not in msg


def test_taxonomy_sleep_skipped_on_fatal(monkeypatch):
    import time as _tmod
    _ensure_httpx_exc(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    sleeps = []
    monkeypatch.setattr(_tmod, "sleep", lambda s: sleeps.append(s))
    client = _FakeClient([_FakeResp(404, "gone")])
    with pytest.raises(RuntimeError, match="no retry"):
        bridge._post_with_retry(client, "http://x/responses", {})
    assert sleeps == []
    assert client.calls == 1


def test_taxonomy_non_httpx_error_propagates(monkeypatch):
    _ensure_httpx_exc(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    client = _FakeClient([ValueError("boom")])
    with pytest.raises(ValueError, match="boom"):
        bridge._post_with_retry(client, "http://x/responses", {})


def test_task_id_allowlist_rejects_traversal(tmp_path, monkeypatch):
    _mk_tasks_root(tmp_path)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    assert bridge._resolve_task_file("../x") is None
    assert bridge._resolve_task_file("a/b") is None
    assert bridge._resolve_task_file("*") is None
    assert bridge._resolve_task_file("200-foo;rm") is None
    assert bridge._build_task_attach("../x") == ""


def test_task_attach_escapes_embedded_fences(tmp_path, monkeypatch):
    d = tmp_path / "tasks" / "backlog"
    d.mkdir(parents=True, exist_ok=True)
    (d / "200-foo.md").write_text(
        "# T\nGoal line.\n```\nevil()\n```\n", encoding="utf-8")
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    attach = bridge._build_task_attach("200-foo")
    lines = attach.splitlines()
    assert lines[1] == "```markdown"
    assert lines[-1] == "```"
    assert not any(l == "```" for l in lines[2:-1])


def test_task_attach_omitted_note_has_offset_relpath(tmp_path, monkeypatch):
    d = tmp_path / "tasks" / "backlog"
    d.mkdir(parents=True, exist_ok=True)
    (d / "200-foo.md").write_text(
        "# T\n<!-- BEGIN_GIT_DIFF -->\nx\n<!-- END_GIT_DIFF -->\n", encoding="utf-8")
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    attach = bridge._build_task_attach("200-foo")
    assert "read_file(" in attach
    assert "offset" in attach and "limit" in attach
    assert "200-foo.md" in attach
    assert str(d) not in attach


def test_brain_turn_include_bundle_false_skips_attach(tmp_path, monkeypatch):
    _mk_tasks_root(tmp_path)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))], holder)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="200-foo", include_bundle=False)
    assert result["status"] == "REPORT"
    user_contents = [t["content"] for t in holder["body"]["input"]]
    assert not any("[task-file:" in c for c in user_contents)


def test_task_resolve_tmp_root_integration(tmp_path, monkeypatch):
    for lane in ("backlog", "qa"):
        d = tmp_path / "tasks" / lane
        d.mkdir(parents=True, exist_ok=True)
    (tmp_path / "tasks" / "qa" / "200-foo.md").write_text(
        "# T\nGoal line.\n", encoding="utf-8")
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    found = bridge._resolve_task_file("200-foo")
    assert found is not None and found.name == "200-foo.md"
    attach = bridge._build_task_attach("200-foo")
    assert "Goal line." in attach


def test_task_id_non_strings_rejected(tmp_path, monkeypatch):
    _mk_tasks_root(tmp_path)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    assert bridge._resolve_task_file(200) is None
    assert bridge._resolve_task_file(None) is None
    assert bridge._resolve_task_file("") is None
    assert bridge._resolve_task_file("   ") is None
    assert bridge._build_task_attach(None) == ""


def test_task_resolve_lane_order_backlog_first(tmp_path, monkeypatch):
    for lane in ("backlog", "completed"):
        d = tmp_path / "tasks" / lane
        d.mkdir(parents=True, exist_ok=True)
        (d / "200-foo.md").write_text(f"# from {lane}\n", encoding="utf-8")
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    found = bridge._resolve_task_file("200-foo")
    assert found is not None and "backlog" in str(found)


def test_task_attach_truncates_big_file(tmp_path, monkeypatch):
    d = tmp_path / "tasks" / "backlog"
    d.mkdir(parents=True, exist_ok=True)
    (d / "200-foo.md").write_text("# T\n" + ("y" * 30000), encoding="utf-8")
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    attach = bridge._build_task_attach("200-foo")
    assert "[...truncated" in attach
    assert "read_file(" in attach and "200-foo.md" in attach
    assert len(attach) < 30000


def test_strip_multi_unclosed_lone_markers():
    two = ("a\n<!-- BEGIN_GIT_DIFF -->\nx\n<!-- END_GIT_DIFF -->\nmid\n"
           "<!-- BEGIN_GIT_DIFF -->\ny\n<!-- END_GIT_DIFF -->\nz")
    cleaned, omitted, truncated = bridge._strip_task_diff(two, "t.md")
    assert "x\n" not in cleaned and "\ny\n" not in cleaned
    assert "a\n" in cleaned and "mid\n" in cleaned and "z[Factual" in cleaned
    assert truncated is False
    unclosed = "keep\n<!-- BEGIN_GIT_DIFF -->\nleak this"
    cleaned_u, _o, trunc_u = bridge._strip_task_diff(unclosed, "t.md")
    assert "keep" in cleaned_u and "leak this" not in cleaned_u
    assert trunc_u is True
    lone = "keep\n<!-- END_GIT_DIFF -->\nall"
    cleaned_l, omitted_l, trunc_l = bridge._strip_task_diff(lone, "t.md")
    assert cleaned_l == lone and omitted_l == 0 and trunc_l is False


def test_task_resolve_known_suffix_only(tmp_path, monkeypatch):
    _mk_tasks_root(tmp_path)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    assert bridge._resolve_task_file("200-qa").name == "200-foo.md"
    assert bridge._resolve_task_file("200-foo").name == "200-foo.md"
    assert bridge._resolve_task_file("my-cool-task") is None


def test_task_attach_truncation_has_pull_path(tmp_path, monkeypatch):
    d = tmp_path / "tasks" / "backlog"
    d.mkdir(parents=True, exist_ok=True)
    (d / "200-foo.md").write_text("# T\n" + ("y" * 30000), encoding="utf-8")
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    attach = bridge._build_task_attach("200-foo")
    assert "read_file(" in attach and "200-foo.md" in attach
    assert len(attach) < 30000
