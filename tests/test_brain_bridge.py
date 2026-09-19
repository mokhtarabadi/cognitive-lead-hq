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
    assert bridge._get_brain_model() == "gpt-6-astra"
    monkeypatch.setenv("BRAIN_MODEL", "  ")
    assert bridge._get_brain_model() == "gpt-6-astra"
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
    assert bridge._responses_url() == "https://api.openai.com/v1/responses"
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
        bridge.append_turn("215", "user", "x" * 30000)
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
    result = target("q", task_id="215")
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
        bridge.append_turn("216", "user", "x" * 30000)
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())])
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="216")
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
    # Task 241 Bug 1: no Brain pull order — Hands route instead.
    assert "read_file" not in cleaned
    assert "no file tools" in cleaned and "Hands" in cleaned


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
    # Preflight seam (issue 18): the turn resolves via explicit
    # project_root, not the mocked workspace root.
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))])
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="200", project_root=str(tmp_path))
    assert result["status"] == "REPORT"
    user_line = (tmp_path / "sessions" / "200" / "transcript.jsonl").read_text(
        encoding="utf-8").splitlines()[0]
    assert "[task-file:200:" in user_line
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
    result = target("[task-file:200: 200-foo.md]\nq", task_id="200")
    assert result["status"] == "REPORT"
    user_line = (tmp_path / "sessions" / "200" / "transcript.jsonl").read_text(
        encoding="utf-8").splitlines()[0]
    assert user_line.count("[task-file:200:") == 1


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
    result = target("q", task_id="999")
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
    assert holder["body"].get("reasoning", {}).get("effort")
    monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
    holder2 = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder2)
    target("q2")
    assert holder2["body"]["temperature"] == 0.7
    assert "reasoning" not in holder2["body"]


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
    bridge.append_turn("217", "user", "hi", model="m",
                       prompt_hash="h", truncated=3)
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
    target = _unwrap(bridge.brain_turn)
    target("q", task_id="217")
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
    result = target("hello", task_id="218")
    assert result["output"] == "ok"
    turns = bridge.load_history("218")
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
    # Task 241 Bug 1: the Brain has no file tools — the note must route
    # the pull to the Hands, never order a read_file pull.
    assert "read_file(" not in attach
    assert "no file tools" in attach and "Hands" in attach
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
    result = target("q", task_id="200", include_bundle=False)
    assert result["status"] == "REPORT"
    user_contents = [t["content"] for t in holder["body"]["input"]]
    assert not any("[task-file:" in c for c in user_contents)


def test_brain_turn_lean_diff_attaches_without_bundle(tmp_path, monkeypatch):
    # Task 238 "why" fix: the old bundle gate silently dropped QA diffs
    # on every lean retry (include_bundle=False). The explicit flag
    # stands alone now — hunks must ride the lean turn.
    _mk_tasks_root(tmp_path)
    # Preflight seam (issue 18): the turn resolves via explicit
    # project_root, not the mocked workspace root.
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))], holder)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="200",
                     include_bundle=False, include_diff=True,
                     project_root=str(tmp_path))
    assert result["status"] == "REPORT"
    user_contents = [t["content"] for t in holder["body"]["input"]]
    assert any("[changed-hunks:" in c for c in user_contents)
    assert any("DIFFSTUFF" in c for c in user_contents)


def test_brain_turn_failsafe_fires_without_bundle(tmp_path, monkeypatch):
    # QA-like prompt, flag forgotten, bundle off — the failsafe must
    # still auto-attach the hunks (it no longer requires the bundle).
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
    result = target("qa engineer, adversarial review please",
                     task_id="200", include_bundle=False)
    assert result["status"] == "REPORT"
    user_contents = [t["content"] for t in holder["body"]["input"]]
    assert any("[changed-hunks:" in c for c in user_contents)


def test_brain_turn_include_diff_unresolvable_warns(tmp_path, monkeypatch,
                                                     capsys):
    # Loud skip: flag set but no file — stderr must say why instead
    # of silently sending a diff-less QA turn. The fixture root holds
    # tasks/ lanes (preflight resolves) but no task-200 file, so the
    # diff attach stays loud-skipped.
    (tmp_path / "tasks" / "backlog").mkdir(parents=True)
    # The workspace fallback lane stays mocked to the fixture root so the
    # missing file is unresolvable everywhere (hermetic — never leaks to
    # the real repo lanes).
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))], holder)
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", task_id="200", include_diff=True,
                    project_root=str(tmp_path))
    assert result["status"] == "REPORT"
    assert "unresolvable" in capsys.readouterr().err
    # Re-QA repair: the model itself must see WHY — the inline note
    # rides in the sent prompt, never a silent empty attach.
    user_contents = [t["content"] for t in holder["body"]["input"]]
    assert any("UNAVAILABLE" in c for c in user_contents)


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
    assert "read_file(" not in attach
    assert "no file tools" in attach and "fed-context" in attach
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
    assert "UNVERIFIABLE" in cleaned_u and "QA_REJECTED" not in cleaned_u
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
    assert "read_file(" not in attach
    assert "no file tools" in attach and "Hands" in attach
    assert len(attach) < 30000


def test_task_attach_pull_path_is_lane_relative_and_live(tmp_path, monkeypatch):
    d = tmp_path / "tasks" / "backlog"
    d.mkdir(parents=True, exist_ok=True)
    (d / "200-foo.md").write_text(
        "# T\n<!-- BEGIN_GIT_DIFF -->\nx\n<!-- END_GIT_DIFF -->\n",
        encoding="utf-8")
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    attach = bridge._build_task_attach("200-foo")
    assert "tasks/backlog/200-foo.md" in attach
    pulled = bridge._read_file_impl("tasks/backlog/200-foo.md")
    assert pulled["total_lines"] == 4


def test_grep_skips_symlink_escape(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    sub = ws / "docs"
    sub.mkdir(parents=True)
    (sub / "real.md").write_text("hello\n", encoding="utf-8")
    outside = tmp_path / "outside-secret.md"
    outside.write_text("SECRET-XYZ\n", encoding="utf-8")
    (sub / "evil.md").symlink_to(outside)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: ws)
    hits = bridge._grep_files_impl("SECRET-XYZ", "docs")
    assert hits == []


def test_read_file_limit_clamped(tmp_path, monkeypatch):
    (tmp_path / "big.md").write_text(
        "".join(f"line {n}\n" for n in range(2500)), encoding="utf-8")
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    result = bridge._read_file_impl("big.md", limit=10 ** 9)
    assert result["limit"] == bridge._READ_MAX_LINES
    assert len(result["lines"]) == bridge._READ_MAX_LINES


def test_read_file_oversize_refused(tmp_path, monkeypatch):
    (tmp_path / "huge.md").write_bytes(b"x" * (bridge._READ_MAX_BYTES + 1))
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    with pytest.raises(ValueError, match="too large"):
        bridge._read_file_impl("huge.md")


def test_grep_pattern_too_long_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    with pytest.raises(ValueError, match="too long"):
        bridge._grep_files_impl("a" * (bridge._GREP_PATTERN_MAX + 1))


def test_grep_skips_overlong_lines(tmp_path, monkeypatch):
    sub = tmp_path / "docs"
    sub.mkdir()
    (sub / "mix.md").write_text(
        "MATCH " + ("z" * 5000) + "\nplain MATCH line\n", encoding="utf-8")
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    hits = bridge._grep_files_impl("MATCH", "docs")
    assert len(hits) == 1 and ":2:" in hits[0]


def test_extract_fed_context_present():
    prompt = "plan please\n[fed-context]\nCTX-1 tree\nCTX-2 gate\n[/fed-context]\nend"
    assert bridge.extract_fed_context(prompt) == "CTX-1 tree\nCTX-2 gate"


def test_extract_fed_context_unclosed_runs_to_end():
    prompt = "hi\n[fed-context]\nCTX-1 tree"
    assert bridge.extract_fed_context(prompt) == "CTX-1 tree"


def test_extract_fed_context_absent():
    assert bridge.extract_fed_context("plain plan, no marker") == ""
    assert bridge.extract_fed_context(None) == ""


def test_fed_context_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path))
    assert bridge.load_fed_context("t1") == ""
    bridge.save_fed_context("t1", "CTX-1 tree")
    assert bridge.load_fed_context("t1") == "CTX-1 tree"


def test_fed_context_truncates_at_cap(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path))
    bridge.save_fed_context("t2", "x" * (bridge._FED_CONTEXT_CAP + 100))
    saved = bridge.load_fed_context("t2")
    assert len(saved) <= bridge._FED_CONTEXT_CAP + 100
    assert "truncated" in saved


def test_fed_context_empty_clears_pin(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path))
    bridge.save_fed_context("t3", "something")
    bridge.save_fed_context("t3", "   ")
    assert bridge.load_fed_context("t3") == ""


def test_fed_context_bad_id_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path))
    with pytest.raises(ValueError):
        bridge.save_fed_context("../evil", "x")


def test_fed_context_load_bad_id_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path))
    assert bridge.load_fed_context("../evil") == ""


def _ws(tmp_path, monkeypatch):
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    return tmp_path


def test_paths_attach_off_by_default():
    assert bridge.build_paths_attach(None) == ""
    assert bridge.build_paths_attach([]) == ""
    assert bridge.build_paths_attach("not-a-list") == ""


def test_paths_attach_happy_path(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    (tmp_path / "ctx.md").write_text("# ctx\nbody\n", encoding="utf-8")
    out = bridge.build_paths_attach(["ctx.md"])
    assert "[path-injected: ctx.md]" in out
    assert "body" in out


def test_paths_attach_traversal_labelled(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    out = bridge.build_paths_attach(["../evil.md"])
    assert "outside workspace" in out


def test_paths_attach_bad_suffix_labelled(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    (tmp_path / "run.py").write_text("x = 1\n", encoding="utf-8")
    out = bridge.build_paths_attach(["run.py"])
    assert "unsupported extension" in out


def test_paths_attach_missing_labelled(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    out = bridge.build_paths_attach(["gone.md"])
    assert "unreadable" in out


def test_paths_attach_empty_labelled(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    (tmp_path / "empty.md").write_text("   \n", encoding="utf-8")
    out = bridge.build_paths_attach(["empty.md"])
    assert "empty file" in out


def test_paths_attach_per_file_cap(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    (tmp_path / "big.md").write_text(
        "y" * (bridge._CTX_PATHS_PER_FILE + 10), encoding="utf-8")
    out = bridge.build_paths_attach(["big.md"])
    assert "truncated" in out


def test_paths_attach_total_budget(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    chunk = "z" * bridge._CTX_PATHS_TOTAL
    (tmp_path / "a.md").write_text(chunk, encoding="utf-8")
    (tmp_path / "b.md").write_text(chunk, encoding="utf-8")
    (tmp_path / "c.md").write_text("tiny\n", encoding="utf-8")
    out = bridge.build_paths_attach(["a.md", "b.md", "c.md"])
    assert "total budget" in out
    assert "tiny" in out  # skip does not abort later files


def test_paths_attach_too_large_labelled(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    (tmp_path / "huge.md").write_bytes(b"q" * (bridge._READ_MAX_BYTES + 1))
    out = bridge.build_paths_attach(["huge.md"])
    assert "too large" in out


def test_paths_attach_absolute_escape_labelled(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    out = bridge.build_paths_attach(["/etc/hostname"])
    assert "outside workspace" in out


def test_paths_attach_project_root_wins_over_workspace(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)  # server install dir lacks the report
    proj = tmp_path / "proj"
    (proj / "context-reports").mkdir(parents=True)
    (proj / "context-reports" / "r.md").write_text(
        "# real\nbody\n", encoding="utf-8")
    out = bridge.build_paths_attach(
        ["context-reports/r.md"], project_root=str(proj))
    assert "[path-injected: context-reports/r.md]" in out
    assert "body" in out


def test_paths_attach_project_root_missing_stays_labelled(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    proj = tmp_path / "proj"
    (proj / "tasks").mkdir(parents=True)
    out = bridge.build_paths_attach(["gone.md"], project_root=str(proj))
    assert "unreadable" in out


def test_paths_attach_project_root_invalid_falls_back(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    (tmp_path / "ctx.md").write_text("# ctx\nbody\n", encoding="utf-8")
    out = bridge.build_paths_attach(
        ["ctx.md"], project_root=str(tmp_path / "nope"))
    assert "[path-injected: ctx.md]" in out


def test_paths_attach_ignores_cwd(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    (tmp_path / "ctx.md").write_text("# ctx\nbody\n", encoding="utf-8")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    out = bridge.build_paths_attach(["ctx.md"])
    assert "[path-injected: ctx.md]" in out


def test_paths_attach_size_pattern_truncates_never_blanks(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    (tmp_path / "small.md").write_text("s\n", encoding="utf-8")
    (tmp_path / "mid.md").write_text("m" * 6000 + "\n", encoding="utf-8")
    (tmp_path / "big.md").write_text("b" * 47000 + "\n", encoding="utf-8")
    out = bridge.build_paths_attach(["small.md", "mid.md", "big.md"])
    assert "[path-injected: small.md]" in out
    assert "truncated" in out  # big report truncates per-file, never blanks all


_IMPL_OK = (
    "<hands_implementation_task><!--INCLUDE:shared/validation-phase.md-->"
    "<validation_phase>v</validation_phase>"
    "<context_phase>x</context_phase>"
    "<execution_phase>y</execution_phase>"
    "<bash_phase>pytest</bash_phase>"
    "<documentation_phase>d</documentation_phase>"
    "<summary_phase>z</summary_phase></hands_implementation_task>"
)
_DISC_OK = (
    "<hands_discovery_task><!--INCLUDE:shared/validation-phase.md-->"
    "<validation_phase>v</validation_phase>"
    "<context_phase>x</context_phase>"
    "<execution_phase>y</execution_phase>"
    "<summary_phase>z</summary_phase></hands_discovery_task>"
)


def test_validate_hands_xml_accepts_valid_blocks():
    assert bridge.validate_hands_xml_blocks([_IMPL_OK, _DISC_OK]) == []
    assert bridge.validate_hands_xml_blocks(["<hotfix>do X</hotfix>"]) == []
    assert bridge.validate_hands_xml_blocks(
        ["<failure_report>boom</failure_report>"]) == []
    assert bridge.validate_hands_xml_blocks(
        ["<hands_combined_task><!--INCLUDE:shared/validation-phase.md-->"
         "<validation_phase>v</validation_phase>"
         "<discovery_phase>x</discovery_phase>"
         "</hands_combined_task>"]) == []


def test_validate_hands_xml_rejects_missing_phase():
    bad = ("<hands_implementation_task><context_phase>x</context_phase>"
           "</hands_implementation_task>")
    problems = bridge.validate_hands_xml_blocks([bad])
    assert problems
    assert any("summary_phase" in p for p in problems)


def test_validate_hands_xml_rejects_missing_bash_phase():
    bad = ("<hands_implementation_task>"
           "<validation_phase>v</validation_phase>"
           "<context_phase>x</context_phase>"
           "<execution_phase>y</execution_phase>"
           "<summary_phase>z</summary_phase></hands_implementation_task>")
    problems = bridge.validate_hands_xml_blocks([bad])
    assert problems
    assert any("bash_phase" in p for p in problems)


def test_paths_attach_project_root_non_string_falls_back(tmp_path, monkeypatch):
    _ws(tmp_path, monkeypatch)
    (tmp_path / "ctx.md").write_text("# ctx\nbody\n", encoding="utf-8")
    out = bridge.build_paths_attach(["ctx.md"], project_root=123)
    assert "[path-injected: ctx.md]" in out


def test_validate_hands_xml_rejects_empty_and_unclosed():
    assert bridge.validate_hands_xml_blocks(["<hotfix>   </hotfix>"])
    assert bridge.validate_hands_xml_blocks(
        ["<hands_discovery_task><context_phase>x"])


def test_validate_hands_xml_rejects_unknown_root_and_empty_input():
    assert bridge.validate_hands_xml_blocks(
        ["<reasoning_log>hi</reasoning_log>"])
    assert bridge.validate_hands_xml_blocks([])


def test_validate_hands_xml_rejects_bare_phase_words():
    bare = ("<hands_implementation_task>\n"
            "  validation_phase context_phase execution_phase bash_phase\n"
            "  documentation_phase summary_phase\n"
            "</hands_implementation_task>")
    problems = bridge.validate_hands_xml_blocks([bare])
    assert problems
    assert any("<context_phase>" in p for p in problems)


def test_validate_hands_xml_rejects_comment_only_phases():
    commented = ("<hands_implementation_task>\n"
                 "<!-- validation_phase context_phase execution_phase -->\n"
                 "<!-- bash_phase documentation_phase summary_phase -->\n"
                 "please implement the thing\n"
                 "</hands_implementation_task>")
    problems = bridge.validate_hands_xml_blocks([commented])
    assert problems


def test_validate_hands_xml_rejects_post_close_phases():
    after = ("<hands_implementation_task><summary_phase>z</summary_phase>"
             "</hands_implementation_task>\n"
             "<context_phase>x</context_phase>"
             "<execution_phase>y</execution_phase>")
    problems = bridge.validate_hands_xml_blocks([after])
    assert problems
    assert any("context_phase" in p for p in problems)


def test_brain_turn_semantic_reject_reports(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    incomplete = ("<hands_implementation_task>"
                  "<context_phase>x</context_phase>"
                  "</hands_implementation_task>")
    _mk_bridge_client(
        monkeypatch, [_FakeResp(200, "fine", _ok_payload(incomplete))])
    call = bridge.brain_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target("q", include_bundle=False)
    assert result["status"] == "REPORT"
    assert "[xml-semantic-reject]" in result["output"]
    assert result["xml_blocks"] == []


# --- Task 215: reviewer hotfix XML must extract (bare + xml-fenced) ---

def test_extract_hotfix_bare_block():
    # Incident: Code Reviewer emitted a hotfix instruction block, but the
    # allowlist had no hotfix tag, so brain_turn returned REPORT.
    out = "[Code Reviewer] verdict below:\n<hotfix>fix F8 first</hotfix>\ntail"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert blocks[0].startswith("<hotfix>")


def test_extract_known_tag_inside_xml_fence():
    # Incident variant: operative XML wrapped in an explicit ```xml fence
    # was stripped as documentation before scanning.
    out = "notes\n```xml\n<failure_report>root cause</failure_report>\n```\ntail"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert blocks[0].startswith("<failure_report>")


def test_extract_hotfix_inside_xml_fence():
    out = "```xml\n<hotfix>apply A1-A8</hotfix>\n```"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert blocks[0].startswith("<hotfix>")


def test_extract_unclosed_xml_fence_to_eof():
    out = "notes\n```xml\n<hotfix>apply A1</hotfix>\n"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert blocks[0].startswith("<hotfix>")


def test_extract_ignores_hotfix_in_non_xml_fences():
    # No over-extraction: json/python/bare/tilde fences stay documentation.
    for fenced in (
        "```json\n<hotfix>x</hotfix>\n```",
        "```python\n<hotfix>x</hotfix>\n```",
        "````\n<hotfix>x</hotfix>\n````",
        "~~~\n<hotfix>x</hotfix>\n~~~",
    ):
        assert bridge.extract_xml_blocks(fenced) == [], fenced


def test_extract_unknown_tag_inside_xml_fence_stays_ignored():
    # Allowlist discipline holds inside the fallback: reasoning prose is
    # never instructions, fenced or not.
    out = "```xml\n<reasoning_log>thinking</reasoning_log>\n```"
    assert bridge.extract_xml_blocks(out) == []


def test_extract_unfenced_wins_over_fenced_xml():
    # Precedence lock: when unfenced blocks exist, current behavior is
    # preserved and the fenced copy is not double-counted.
    out = "<failure_report>live</failure_report>\n```xml\n<hotfix>doc</hotfix>\n```"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert blocks[0].startswith("<failure_report>")


# --- Task 215 QA follow-ups (A1-A4 + attribute lock) ---

def test_extract_multiple_xml_fences_in_order():
    out = "```xml\n<hotfix>first</hotfix>\n```\ntext\n```xml\n<failure_report>second</failure_report>\n```"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 2
    assert blocks[0].startswith("<hotfix>")
    assert blocks[1].startswith("<failure_report>")


def test_extract_uppercase_fence_lowercase_tag():
    out = "```XML\n<hotfix>loud fence</hotfix>\n```"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert blocks[0].startswith("<hotfix>")


def test_extract_uppercase_tag_tolerated():
    # Task 238 fix loop (supersedes the lowercase-only lock): model output
    # varies in case; an operative tag in any case still extracts.
    blocks = bridge.extract_xml_blocks("<HOTFIX>x</HOTFIX>")
    assert len(blocks) == 1
    assert bridge.extract_xml_blocks("```xml\n<HOTFIX>x</HOTFIX>\n```") != []


def test_extract_fence_without_newline_ignored():
    # Fail-closed: marker must be followed by newline; otherwise docs.
    assert bridge.extract_xml_blocks("```xml<hotfix>x</hotfix>```") == []


def test_extract_empty_hotfix_block():
    blocks = bridge.extract_xml_blocks("<hotfix></hotfix>")
    assert len(blocks) == 1


def test_extract_tag_with_attributes_tolerated():
    # Task 238 fix loop (supersedes the bare-names-only lock): attribute
    # and whitespace forms of operative tags still extract.
    for variant in (
        '<hotfix id="1">x</hotfix>',
        "<hotfix >x</hotfix>",
        '<HANDS_IMPLEMENTATION_TASK retry="2">y</HANDS_IMPLEMENTATION_TASK>',
    ):
        blocks = bridge.extract_xml_blocks(variant)
        assert len(blocks) == 1, variant


def test_extract_quad_xml_fence_stays_ignored():
    # Reviewer follow-up A1: without the (?<!`) guard the fence pattern
    # matched at offset 1 inside ````xml. Quad fences stay documentation.
    out = "````xml\n<hotfix>x</hotfix>\n````"
    assert bridge.extract_xml_blocks(out) == []


# --- Task 238 fix loop: tolerance + truncation fallback ---

def test_extract_mismatched_close_stays_ignored():
    # Mid-line so the truncation fallback (line-start only) stays out.
    assert bridge.extract_xml_blocks("note <hotfix>x</failure_report> tail") == []


def test_extract_non_allowlisted_tag_never_extracts():
    # reasoning_log is conversation, never instructions — any case, attrs,
    # fenced or bare, closed or line-start unclosed.
    assert bridge.extract_xml_blocks("<reasoning_log>x</reasoning_log>") == []
    assert bridge.extract_xml_blocks("<REASONING_LOG>x</REASONING_LOG>") == []
    assert bridge.extract_xml_blocks('<reasoning_log tone="t">x</reasoning_log>') == []
    assert bridge.extract_xml_blocks("```xml\n<reasoning_log>x</reasoning_log>\n```") == []
    assert bridge.extract_xml_blocks("notes\n<reasoning_log>truncated") == []


def test_extract_truncated_trailing_block_surfaced():
    out = "thinking\n<hotfix>apply A1-A8"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert blocks[0].startswith("<hotfix>")


def test_extract_truncated_tail_cuts_trailing_prose():
    # QA hotfix M1: prose after the broken block must stay conversation,
    # never become instructions the Hands executes.
    out = "notes\n<hotfix>apply A1\n\nC1 explains why this is safe"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert "explains" not in blocks[0]
    assert blocks[0].startswith("<hotfix>")


def test_extract_plain_prose_angle_brackets_never_extracts():
    # QA hotfix M2: angle brackets with no allowlisted tag yield nothing.
    assert bridge.extract_xml_blocks("compare a < b and c > d, done") == []
    assert bridge.extract_xml_blocks("price <10> and <20> ok") == []


def test_extract_unclosed_uppercase_with_attrs_surfaced():
    # QA hotfix V2: case and attributes never affect the allowlist
    # decision — the tag NAME alone decides.
    out = "notes\n<HOTFIX ID=\"7\">do step 1"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert blocks[0].startswith("<HOTFIX")


def test_extract_truncated_block_with_attributes_surfaced():
    out = "thinking\n<HANDS_IMPLEMENTATION_TASK retry=\"2\">do step 1"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1


def test_extract_mid_sentence_unclosed_mention_ignored():
    # Line-start required: prose mentions never trigger the fallback.
    assert bridge.extract_xml_blocks("use <hotfix> for urgent fixes") == []


def test_extract_truncated_inside_xml_fence_surfaced():
    out = "notes\n```xml\n<hotfix>apply A1"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert blocks[0].startswith("<hotfix>")


def test_extract_closed_block_wins_over_truncated_tail():
    out = "<failure_report>live</failure_report>\n<hotfix>truncated"
    blocks = bridge.extract_xml_blocks(out)
    assert len(blocks) == 1
    assert blocks[0].startswith("<failure_report>")

# --- Task-number gate: task_id is a bare number, never suffixed ---
# (Session finding: "215qa"/"215rev"/"215plan" forked one task's history
# into separate transcript dirs. The tool entry now rejects them.)

def test_require_task_number_accepts_bare_digits():
    assert bridge._require_task_number("215") == "215"
    assert bridge._require_task_number("01") == "01"


def test_require_task_number_rejects_session_suffixes():
    import pytest as _pt
    for bad in ("215qa", "215rev", "215plan", "224qa", "219rev"):
        with _pt.raises(ValueError, match="bare task number"):
            bridge._require_task_number(bad)


def test_require_task_number_rejects_slugs_and_empty():
    import pytest as _pt
    for bad in ("200-foo", "nope-no-file", "", "   ", "21 5", None, 215):
        with _pt.raises(ValueError, match="bare task number"):
            bridge._require_task_number(bad)


def test_brain_turn_rejects_suffixed_id_before_any_work(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    import pytest as _pt
    target = bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn") else bridge.brain_turn
    with _pt.raises(ValueError, match="identical number on every"):
        target("q", task_id="215qa")
    assert not (tmp_path / "sessions").exists()


# --- Task 232: empty-output retry hint (mocked httpx only) ---


def test_empty_output_hint_contract():
    hint = bridge._empty_output_hint("232")
    assert bridge.EMPTY_OUTPUT_RETRY in hint
    assert "232" in hint
    assert "include_bundle=false" in hint
    assert "same task_id" in hint
    bare = bridge._empty_output_hint(None)
    assert bridge.EMPTY_OUTPUT_RETRY in bare
    assert "escalate" in bare
    assert "stale" in hint  # lean retries drop context; stale answers re-run full
    noted = bridge._empty_output_hint("232", "tasks/qa/x.md | status=open | diff=abc123")
    assert "Current state: tasks/qa/x.md" in noted
    assert bridge._task_state_note("no-such-task-xyz") == "unknown"
    assert bridge._task_state_note(None) == "unknown"


def _run_turn(monkeypatch, tmp_path, payload, prompt="q", task_id="232"):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", payload)])
    target = bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn") else bridge.brain_turn
    return target(prompt, task_id=task_id)


def test_brain_turn_missing_output_returns_retry_hint(tmp_path, monkeypatch):
    result = _run_turn(monkeypatch, tmp_path, {})
    assert result["status"] == "REPORT"
    assert result["xml_blocks"] == []
    assert bridge.EMPTY_OUTPUT_RETRY in result["output"]
    assert "232" in result["output"]


def test_brain_turn_none_output_returns_retry_hint(tmp_path, monkeypatch):
    result = _run_turn(monkeypatch, tmp_path, {"output": None})
    assert result["status"] == "REPORT"
    assert bridge.EMPTY_OUTPUT_RETRY in result["output"]


def test_brain_turn_whitespace_output_returns_retry_hint(tmp_path, monkeypatch):
    result = _run_turn(monkeypatch, tmp_path, _ok_payload("  \n  "))
    assert result["status"] == "REPORT"
    assert bridge.EMPTY_OUTPUT_RETRY in result["output"]


def test_brain_turn_normal_output_has_no_retry_hint(tmp_path, monkeypatch):
    result = _run_turn(monkeypatch, tmp_path, _ok_payload("a real verdict"))
    assert result["status"] == "REPORT"
    assert result["output"] == "a real verdict"
    assert bridge.EMPTY_OUTPUT_RETRY not in result["output"]


# --- Task 259: provider-diagnosis triage (budget exhaustion != flake) ------


def test_parse_responses_diagnostics_full_payload():
    data = {
        "status": "incomplete",
        "incomplete_details": {"reason": "max_output_tokens"},
        "usage": {
            "input_tokens": 100,
            "output_tokens": 16384,
            "total_tokens": 16484,
            "output_tokens_details": {"reasoning_tokens": 16384},
        },
        "output": [{"type": "reasoning", "summary": []}],
    }
    diag = bridge.parse_responses_diagnostics(data)
    assert diag["status"] == "incomplete"
    assert diag["incomplete_reason"] == "max_output_tokens"
    assert diag["usage"] == {
        "input_tokens": 100,
        "output_tokens": 16384,
        "reasoning_tokens": 16384,
        "total_tokens": 16484,
    }
    assert diag["error"] is None
    assert diag["refusal"] is None


def test_parse_responses_diagnostics_tolerates_malformed():
    for bad in ({}, {"output": None}, {"usage": "nope"}, {"error": {}}, []):
        diag = bridge.parse_responses_diagnostics(bad)
        assert set(diag) == {
            "status", "incomplete_reason", "usage", "error", "refusal"}
        assert set(diag["usage"]) == {
            "input_tokens", "output_tokens", "reasoning_tokens",
            "total_tokens"}
    assert bridge.parse_responses_diagnostics(None)["status"] is None


def test_parse_responses_diagnostics_refusal_direct_and_nested():
    direct = bridge.parse_responses_diagnostics(
        {"output": [{"type": "refusal", "refusal": "I cannot help."}]})
    assert direct["refusal"] == "I cannot help."
    nested = bridge.parse_responses_diagnostics(
        {"output": [{"type": "message", "content": [
            {"type": "refusal", "refusal": "Nested refusal text"}]}]})
    assert nested["refusal"] == "Nested refusal text"


def test_parse_responses_diagnostics_error_shapes():
    assert bridge.parse_responses_diagnostics(
        {"error": "boom"})["error"] == "boom"
    assert bridge.parse_responses_diagnostics(
        {"error": {"message": "boom2", "type": "x"}})["error"] == "boom2"


def test_output_budget_hint_contract():
    diag = bridge.parse_responses_diagnostics({
        "status": "incomplete",
        "incomplete_details": {"reason": "max_output_tokens"},
        "usage": {"input_tokens": 10, "output_tokens": 20,
                  "total_tokens": 30,
                  "output_tokens_details": {"reasoning_tokens": 18}},
    })
    hint = bridge._output_budget_hint(
        diag, "259", "tasks/qa/x.md | status=open")
    assert bridge.OUTPUT_BUDGET_EXHAUSTED in hint
    assert bridge.EMPTY_OUTPUT_RETRY not in hint
    assert "include_bundle=false" not in hint
    assert "lean-retry" in hint
    assert "BRAIN_MAX_TOKENS" in hint
    assert "BRAIN_REASONING_EFFORT" in hint
    assert "259" in hint
    assert "reasoning=18" in hint


def test_brain_turn_budget_exhaustion_is_terminal(tmp_path, monkeypatch, capsys):
    payload = {
        "status": "incomplete",
        "incomplete_details": {"reason": "max_output_tokens"},
        "usage": {"input_tokens": 500, "output_tokens": 16384,
                  "total_tokens": 16884,
                  "output_tokens_details": {"reasoning_tokens": 16000}},
        "output": [{"type": "reasoning", "summary": []}],
    }
    result = _run_turn(monkeypatch, tmp_path, payload)
    assert result["status"] == "REPORT"
    assert bridge.OUTPUT_BUDGET_EXHAUSTED in result["output"]
    assert bridge.EMPTY_OUTPUT_RETRY not in result["output"]
    assert "include_bundle=false" not in result["output"]
    provider = result["debug"]["provider"]
    assert provider["incomplete_reason"] == "max_output_tokens"
    assert provider["usage"]["reasoning_tokens"] == 16000
    err = capsys.readouterr().err
    assert "provider diag" in err
    assert "reasoning_tokens=16000" in err


def test_brain_turn_refusal_surfaced_verbatim(tmp_path, monkeypatch):
    payload = {"output": [{"type": "refusal", "refusal": "I must decline."}]}
    result = _run_turn(monkeypatch, tmp_path, payload)
    assert bridge.PROVIDER_REFUSAL in result["output"]
    assert "I must decline." in result["output"]
    assert bridge.EMPTY_OUTPUT_RETRY not in result["output"]
    assert result["debug"]["provider"]["refusal"] == "I must decline."


def test_brain_turn_provider_error_surfaced_verbatim(tmp_path, monkeypatch):
    payload = {"error": "upstream exploded", "output": []}
    result = _run_turn(monkeypatch, tmp_path, payload)
    assert bridge.PROVIDER_ERROR in result["output"]
    assert "upstream exploded" in result["output"]
    assert bridge.EMPTY_OUTPUT_RETRY not in result["output"]
    assert result["debug"]["provider"]["error"] == "upstream exploded"


def test_brain_turn_debug_provider_on_success(tmp_path, monkeypatch):
    result = _run_turn(monkeypatch, tmp_path, _ok_payload("a real verdict"))
    assert result["output"] == "a real verdict"
    assert set(result["debug"]["provider"]) == {
        "status", "incomplete_reason", "usage", "error", "refusal"}


def test_brain_turn_high_effort_budget_warning(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("BRAIN_MAX_TOKENS", "16384")
    for effort in ("high", "xhigh"):
        monkeypatch.setenv("BRAIN_REASONING_EFFORT", effort)
        result = _run_turn(monkeypatch, tmp_path, _ok_payload("ok"))
        assert result["output"] == "ok"
    err = capsys.readouterr().err
    # Both high-effort values must warn at the small cap (QA F4).
    assert "'high'" in err
    assert "'xhigh'" in err
    assert "BRAIN_MAX_TOKENS" in err


def test_brain_turn_low_effort_skips_budget_warning(tmp_path, monkeypatch,
                                                    capsys):
    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "low")
    monkeypatch.setenv("BRAIN_MAX_TOKENS", "16384")
    result = _run_turn(monkeypatch, tmp_path, _ok_payload("ok"))
    assert result["output"] == "ok"
    assert "reasoning effort" not in capsys.readouterr().err


def test_parse_responses_diagnostics_scalar_content_does_not_raise():
    # A malformed nested "content" scalar must not abort diagnosis (QA F1).
    for bad_content in (1, "text", {"type": "refusal"}, True):
        diag = bridge.parse_responses_diagnostics(
            {"output": [{"type": "message", "content": bad_content}]})
        assert set(diag) == {
            "status", "incomplete_reason", "usage", "error", "refusal"}
        assert diag["refusal"] is None


def test_parse_responses_diagnostics_non_finite_usage_is_none():
    # nan/inf raise inside int(); the parser must swallow them (QA F2).
    diag = bridge.parse_responses_diagnostics({
        "usage": {
            "input_tokens": float("nan"),
            "output_tokens": float("inf"),
            "total_tokens": float("-inf"),
            "output_tokens_details": {"reasoning_tokens": float("nan")},
        },
    })
    assert diag["usage"] == {
        "input_tokens": None, "output_tokens": None,
        "reasoning_tokens": None, "total_tokens": None}


def test_brain_turn_large_prompt_warns_on_stderr(tmp_path, monkeypatch, capsys):
    big = "x" * (bridge._PROMPT_WARN_CHARS + 1)
    result = _run_turn(monkeypatch, tmp_path, _ok_payload("ok"), prompt=big)
    assert result["output"] == "ok"
    err = capsys.readouterr().err
    assert "prompt is large" in err
    assert "include_bundle=false" in err


def test_brain_turn_writes_context_ledger_with_util(tmp_path, monkeypatch, capsys):
    import json

    big = "x" * (bridge._PROMPT_WARN_CHARS + 1)
    result = _run_turn(monkeypatch, tmp_path, _ok_payload("ok"), prompt=big)
    assert result["output"] == "ok"
    assert "util~" in capsys.readouterr().err
    ledger = tmp_path / "sessions" / bridge._CONTEXT_LEDGER_NAME
    row = json.loads(ledger.read_text(encoding="utf-8").strip().split("\n")[-1])
    assert row["task_id"] == "232"
    assert row["budget_chars"] > bridge._PROMPT_WARN_CHARS
    assert row["util_pct"] == row["budget_chars"] * 100 // bridge._MODEL_WINDOW_CHARS
    assert row["truncated"] == 0


def test_bundle_total_cap_bounds_oversize_workspace(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "a.md").write_text("A" * 2000, encoding="utf-8")
    (ws / "b.md").write_text("B" * 2000, encoding="utf-8")
    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
    monkeypatch.setattr(bridge, "_BUNDLE_FILES", ("a.md", "b.md"))
    monkeypatch.setattr(bridge, "_BUNDLE_TOTAL_CAP", 500)
    out = bridge._build_context_bundle()
    assert "bundle total cap" in out
    assert "B" * 2000 not in out


def test_fed_context_persists_across_second_turn(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    bridge.save_fed_context("t9", "CTX turn one")
    assert bridge.load_fed_context("t9") == "CTX turn one"
    bridge.save_fed_context("t9", "CTX turn one\nCTX turn two")
    assert bridge.load_fed_context("t9") == "CTX turn one\nCTX turn two"


def test_plan_verdict_valid():
    plan = ("verdict: PLAN APPROVED\nseats: Architect\npath: implement\n"
            "steps: edit files\ncites: server.py:100, skill.md:20")
    assert bridge.validate_plan_verdict(plan) == []


def test_plan_verdict_missing_fields():
    problems = bridge.validate_plan_verdict("looks good, ship it")
    assert any("seats" in p for p in problems)
    assert any("cites" in p for p in problems)


def test_plan_verdict_cites_without_lines():
    plan = "verdict: ok\nseats: A\npath: p\nsteps: s\ncites: some files somewhere"
    problems = bridge.validate_plan_verdict(plan)
    assert any("file path with lines" in p for p in problems)


def _close_ready_task():
    return ("VERDICT: QA_PASSED\nstate PO_REVIEW_PENDING\n"
            "Manager wrote: \"Approved for closure\".\n"
            "Ran extract_session_decisions(241): [] loudly, nothing queued.\n"
            "<!-- BEGIN_GIT_DIFF -->\n```diff\n"
            "diff --git a/f.py b/f.py\n+fix\n"
            "```\n<!-- END_GIT_DIFF -->")


def test_closure_checklist_ready():
    assert bridge.validate_closure_checklist(_close_ready_task()) == []


def test_closure_checklist_missing_each():
    base = _close_ready_task()
    assert any("QA_PASSED" in p for p in
               bridge.validate_closure_checklist("no verdict here"))
    assert any("PO_REVIEW_PENDING" in p for p in
               bridge.validate_closure_checklist(
                   base.replace("PO_REVIEW_PENDING", "review done")))
    # Bare "approved" never counts — only the exact approval words.
    assert any("approval-word" in p for p in
               bridge.validate_closure_checklist(
                   base.replace('"Approved for closure"',
                                'manager said approved')))
    assert any("Diff block is empty" in p for p in
               bridge.validate_closure_checklist(
                   base.replace("diff --git a/f.py b/f.py\n+fix",
                                "_(Git diff will be automatically "
                                "injected here)_")))
    assert any("extract_session_decisions" in p for p in
               bridge.validate_closure_checklist(
                   base.replace("Ran extract_session_decisions(241): "
                                "[] loudly, nothing queued.\n", "")))



def _mk_project(tmp_path, name):
    proj = tmp_path / name
    (proj / "tasks").mkdir(parents=True)
    return proj


def _clean_session_env(monkeypatch):
    for key in ("BRAIN_SESSIONS_ROOT", "BRAIN_PROJECT_ROOT",
                "BRAIN_WORKSPACE_ROOT"):
        monkeypatch.delenv(key, raising=False)


def test_per_project_roots_differ_by_project(tmp_path, monkeypatch):
    _clean_session_env(monkeypatch)
    proj_a = _mk_project(tmp_path, "proj_a")
    proj_b = _mk_project(tmp_path, "proj_b")
    root_a = bridge._sessions_root(project_root=str(proj_a))
    root_b = bridge._sessions_root(project_root=str(proj_b))
    assert root_a == proj_a / "tasks" / ".sessions"
    assert root_b == proj_b / "tasks" / ".sessions"
    assert root_a != root_b


def test_no_tasks_dir_falls_back_to_legacy(tmp_path, monkeypatch):
    _clean_session_env(monkeypatch)
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.chdir(bare)
    assert bridge._sessions_root() == bridge._legacy_sessions_root()


def test_legacy_global_transcript_read_through(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    _clean_session_env(monkeypatch)
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.chdir(bare)
    # Plant a pre-migration global file directly: append_turn now refuses
    # to write to the legacy global dir (no-global-write rule), so the
    # legacy fixture must be written by hand.
    planted = (fake_home / ".config" / "opencode" / "brain-sessions"
               / "t3legacy" / "transcript.jsonl")
    planted.parent.mkdir(parents=True, exist_ok=True)
    planted.write_text(
        '{"role": "user", "content": "legacy hello", "model": null, '
        '"prompt_hash": null, "truncated": 0}\n', encoding="utf-8")
    assert planted.is_file()
    # Read from the bare dir: no per-project root resolves there, so the
    # legacy global fallback (pre-migration read path) still applies.
    turns = bridge.load_history("t3legacy")
    assert any(t.get("content") == "legacy hello" for t in turns)


def test_no_cross_project_bleed_for_project_with_sessions_dir(
        tmp_path, monkeypatch):
    # Task 241 Bug 2: a project with its own sessions dir must NEVER read
    # another project's turns or pin from the legacy global store — the
    # fallback applies only when no per-project root resolves.
    fake_home = tmp_path / "home_bleed"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    _clean_session_env(monkeypatch)
    legacy_dir = (fake_home / ".config" / "opencode" / "brain-sessions"
                  / "bleed")
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "transcript.jsonl").write_text(
        '{"role": "user", "content": "foreign hello", "model": null, '
        '"prompt_hash": null, "truncated": 0}\n', encoding="utf-8")
    (legacy_dir / "fed_context.md").write_text(
        "foreign pin\n", encoding="utf-8")
    proj = _mk_project(tmp_path, "proj_bleed")
    monkeypatch.chdir(proj)
    assert bridge.load_history("bleed") == []
    assert bridge.load_fed_context("bleed") == ""


def test_fresh_write_goes_per_project(tmp_path, monkeypatch):
    _clean_session_env(monkeypatch)
    proj = _mk_project(tmp_path, "proj_write")
    monkeypatch.chdir(proj)
    bridge.append_turn("t4fresh", "user", "fresh hello")
    fresh = (proj / "tasks" / ".sessions" / "t4fresh" / "transcript.jsonl")
    assert fresh.is_file()
    assert "fresh hello" in fresh.read_text(encoding="utf-8")


def test_writes_avoid_legacy_global_when_no_root(tmp_path, monkeypatch, capsys):
    # T5: bare cwd (no tasks/ anywhere up except tmp freshness) + fake
    # HOME: append_turn must land in cwd/tasks/.sessions, never global.
    fake_home = tmp_path / "home5"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    _clean_session_env(monkeypatch)
    bare = tmp_path / "bare5"
    bare.mkdir()
    monkeypatch.chdir(bare)
    bridge.append_turn("t5noglobal", "user", "no bleed")
    local = bare / "tasks" / ".sessions" / "t5noglobal" / "transcript.jsonl"
    assert local.is_file()
    legacy = (fake_home / ".config" / "opencode" / "brain-sessions"
              / "t5noglobal" / "transcript.jsonl")
    assert not legacy.exists()
    assert "instead of legacy global" in capsys.readouterr().err


def test_loop_guard_isolation_by_project(tmp_path, monkeypatch):
    # T6: same task id in two projects keeps separate spin state.
    from loop_guard import record_attempt
    _clean_session_env(monkeypatch)
    proj_a = _mk_project(tmp_path, "proj_ga")
    proj_b = _mk_project(tmp_path, "proj_gb")
    ra = record_attempt("t6spin", "aaa", project_root=str(proj_a))
    rb = record_attempt("t6spin", "bbb", project_root=str(proj_b))
    assert ra == {"stop": False, "history": ["aaa"]}
    assert rb == {"stop": False, "history": ["bbb"]}
    assert (proj_a / "tasks" / ".sessions" / "t6spin" / "loop_hashes.jsonl").is_file()
    assert (proj_b / "tasks" / ".sessions" / "t6spin" / "loop_hashes.jsonl").is_file()


def test_sibling_missing_still_resolves_per_project(tmp_path, monkeypatch):
    # T7: even when the loop_guard sibling import fails, the local
    # walk-up fallback resolves a project holding tasks/.
    _clean_session_env(monkeypatch)
    proj = _mk_project(tmp_path, "proj_pkg")
    monkeypatch.chdir(proj)
    monkeypatch.setattr(bridge, "_shared_project_root", None)
    monkeypatch.setattr(bridge, "_shared_legacy_root", None)
    assert bridge._sessions_root() == proj / "tasks" / ".sessions"
    assert bridge._sessions_root(project_root=str(proj)) == (
        proj / "tasks" / ".sessions")


# --- Risk-aware routing (RED: resolver + wiring do not exist yet) ---

def _clean_routing_env(monkeypatch):
    for var in ("BRAIN_RISK_ROUTING_ENABLED", "BRAIN_MODEL_LOW",
                "BRAIN_MODEL_HIGH", "BRAIN_MODEL"):
        monkeypatch.delenv(var, raising=False)


def _run_turn_capture(monkeypatch, tmp_path, payload, prompt="q",
                      task_id="232", **kwargs):
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", payload)],
                      holder=holder)
    target = (bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn")
              else bridge.brain_turn)
    result = target(prompt, task_id=task_id, **kwargs)
    return result, holder


def test_routed_model_resolution_table(monkeypatch):
    _clean_routing_env(monkeypatch)
    r = bridge.resolve_routed_model
    # Disabled: every tier falls back to the current default model.
    for tier in ("T0", "T1", "T2", None, "", "t0", "bogus"):
        assert r(False, tier, "gpt-6-astra", "low-m", "high-m") == "gpt-6-astra"
    # Enabled: T0 -> low, T1/T2 -> high, missing/invalid -> default.
    assert r(True, "T0", "gpt-6-astra", "low-m", "high-m") == "low-m"
    assert r(True, "T1", "gpt-6-astra", "low-m", "high-m") == "high-m"
    assert r(True, "T2", "gpt-6-astra", "low-m", "high-m") == "high-m"
    assert r(True, None, "gpt-6-astra", "low-m", "high-m") == "gpt-6-astra"
    assert r(True, "", "gpt-6-astra", "low-m", "high-m") == "gpt-6-astra"
    assert r(True, "t0", "gpt-6-astra", "low-m", "high-m") == "gpt-6-astra"
    assert r(True, "bogus", "gpt-6-astra", "low-m", "high-m") == "gpt-6-astra"
    # Blank overrides fall back to the default model per tier.
    assert r(True, "T0", "gpt-6-astra", "", "high-m") == "gpt-6-astra"
    assert r(True, "T1", "gpt-6-astra", "low-m", "  ") == "gpt-6-astra"


def test_routing_disabled_by_default_preserves_behavior(tmp_path, monkeypatch):
    _clean_routing_env(monkeypatch)
    assert bridge._routing_enabled() is False
    result, holder = _run_turn_capture(monkeypatch, tmp_path, _ok_payload("ok"))
    assert result["output"] == "ok"
    assert holder["body"]["model"] == "gpt-6-astra"
    assert holder["body"]["reasoning"] == {"effort": "xhigh"}
    assert holder["body"]["max_output_tokens"] == 16384
    # Disabled + explicit tier: wiring must stay on the default model.
    result, holder = _run_turn_capture(
        monkeypatch, tmp_path, _ok_payload("ok"), task_id="233",
        risk_tier="T0")
    assert holder["body"]["model"] == "gpt-6-astra"


def test_routing_env_overrides_stripped_and_blank(monkeypatch):
    _clean_routing_env(monkeypatch)
    monkeypatch.setenv("BRAIN_RISK_ROUTING_ENABLED", "  true  ")
    assert bridge._routing_enabled() is True
    monkeypatch.setenv("BRAIN_RISK_ROUTING_ENABLED", "0")
    assert bridge._routing_enabled() is False
    monkeypatch.setenv("BRAIN_MODEL_LOW", "  low-m  ")
    monkeypatch.setenv("BRAIN_MODEL_HIGH", "   ")
    assert bridge._get_model_low() == "low-m"
    assert bridge._get_model_high() == ""


def test_model_low_only_affects_T0(monkeypatch):
    _clean_routing_env(monkeypatch)
    r = bridge.resolve_routed_model
    assert r(True, "T0", "d", "low-m", "high-m") == "low-m"
    assert r(True, "T1", "d", "low-m", "high-m") == "high-m"
    assert r(True, "T2", "d", "low-m", "high-m") == "high-m"


def test_model_high_only_affects_T1_T2(monkeypatch):
    _clean_routing_env(monkeypatch)
    r = bridge.resolve_routed_model
    assert r(True, "T0", "d", "low-m", "high-m") == "low-m"
    assert r(True, "T1", "d", "low-m", "") == "d"
    assert r(True, "T2", "d", "low-m", "") == "d"


def test_routed_body_uses_selected_model(tmp_path, monkeypatch):
    _clean_routing_env(monkeypatch)
    monkeypatch.setenv("BRAIN_RISK_ROUTING_ENABLED", "true")
    monkeypatch.setenv("BRAIN_MODEL_LOW", "low-m")
    monkeypatch.setenv("BRAIN_MODEL_HIGH", "high-m")
    result, holder = _run_turn_capture(
        monkeypatch, tmp_path, _ok_payload("ok"), risk_tier="T0")
    assert result["output"] == "ok"
    assert result["model"] == "low-m"
    assert holder["body"]["model"] == "low-m"
    assert holder["body"]["reasoning"] == {"effort": "xhigh"}
    assert holder["body"]["max_output_tokens"] == 16384
    result, holder = _run_turn_capture(
        monkeypatch, tmp_path, _ok_payload("ok"), task_id="233",
        risk_tier="T2")
    assert holder["body"]["model"] == "high-m"


def test_ledger_carries_model_tier_and_cache_split(tmp_path, monkeypatch):
    import json
    _clean_routing_env(monkeypatch)
    monkeypatch.setenv("BRAIN_RISK_ROUTING_ENABLED", "true")
    monkeypatch.setenv("BRAIN_MODEL_LOW", "low-m")
    secret_prompt = "ledger-leak-probe-zz9"
    result, _ = _run_turn_capture(monkeypatch, tmp_path, _ok_payload("ok"),
                                  prompt=secret_prompt, risk_tier="T0")
    ledger = tmp_path / "sessions" / bridge._CONTEXT_LEDGER_NAME
    blob = ledger.read_text(encoding="utf-8").strip().split("\n")[-1]
    row = json.loads(blob)
    assert row["model"] == "low-m"
    assert row["risk_tier"] == "T0"
    assert row["prompt_cache_split"] == result["prompt_cache_split"]
    assert set(row["prompt_cache_split"]) == {
        "schema_version", "split_boundary", "static_prefix_sha256",
        "dynamic_suffix_sha256"}
    assert secret_prompt not in blob
    assert "sk-test-key" not in blob
    assert set(row) == {"task_id", "budget_chars", "est_tokens",
                        "util_pct", "truncated", "model", "risk_tier",
                        "prompt_cache_split"}


def test_resolver_takes_no_prompt_diff_or_key():
    import inspect
    params = set(inspect.signature(bridge.resolve_routed_model).parameters)
    assert params == {"enabled", "risk_tier", "default_model",
                      "model_low", "model_high"}


def _split_kwargs(**over):
    base = dict(system_prompt="sys", bundle_text="bundle",
                task_attach_text="attach", user_prompt="q",
                paths_text="", diff_text="", failsafe_text="",
                fed_text="", history=[])
    base.update(over)
    return base


def test_cache_split_static_stable_dynamic_varies():
    a = bridge.build_prompt_cache_split(**_split_kwargs())
    b = bridge.build_prompt_cache_split(**_split_kwargs(
        user_prompt="q2", paths_text="p", diff_text="d",
        failsafe_text="f", fed_text="fed",
        history=[{"role": "user", "content": "h"}]))
    assert a["schema_version"] == bridge._CACHE_SPLIT_SCHEMA_VERSION
    assert (a["split_boundary"]
            == "after_system_bundle_task_attach")
    assert a["static_prefix_sha256"] == b["static_prefix_sha256"]
    assert a["dynamic_suffix_sha256"] != b["dynamic_suffix_sha256"]
    assert len(a["static_prefix_sha256"]) == 64
    assert len(a["dynamic_suffix_sha256"]) == 64


def test_cache_split_each_dynamic_segment_flips_dynamic():
    base = bridge.build_prompt_cache_split(**_split_kwargs())
    for field, val in (("user_prompt", "x"), ("paths_text", "x"),
                       ("diff_text", "x"), ("failsafe_text", "x"),
                       ("fed_text", "x")):
        other = bridge.build_prompt_cache_split(
            **_split_kwargs(**{field: val}))
        assert (other["dynamic_suffix_sha256"]
                != base["dynamic_suffix_sha256"])
        assert (other["static_prefix_sha256"]
                == base["static_prefix_sha256"])
    hist = bridge.build_prompt_cache_split(**_split_kwargs(
        history=[{"role": "assistant", "content": "x"}]))
    assert hist["dynamic_suffix_sha256"] != base["dynamic_suffix_sha256"]
    assert hist["static_prefix_sha256"] == base["static_prefix_sha256"]


def test_cache_split_static_change_flips_static_only():
    base = bridge.build_prompt_cache_split(**_split_kwargs())
    for field in ("system_prompt", "bundle_text", "task_attach_text"):
        other = bridge.build_prompt_cache_split(
            **_split_kwargs(**{field: "changed"}))
        assert (other["static_prefix_sha256"]
                != base["static_prefix_sha256"])


def test_cache_split_memoizes_static_computation(monkeypatch):
    bridge._STATIC_SPLIT_CACHE.clear()
    monkeypatch.setattr(bridge, "_STATIC_SPLIT_COMPUTES", 0)
    kw = _split_kwargs()
    bridge.build_prompt_cache_split(**kw)
    bridge.build_prompt_cache_split(**kw)
    assert bridge._STATIC_SPLIT_COMPUTES == 1
    kw["bundle_text"] = "other-bundle"
    bridge.build_prompt_cache_split(**kw)
    assert bridge._STATIC_SPLIT_COMPUTES == 2


def test_cache_split_result_and_ledger(tmp_path, monkeypatch):
    import json
    _clean_routing_env(monkeypatch)
    result, holder = _run_turn_capture(
        monkeypatch, tmp_path, _ok_payload("ok"), prompt="cache-q")
    split = result["prompt_cache_split"]
    assert split["schema_version"] == bridge._CACHE_SPLIT_SCHEMA_VERSION
    assert split["split_boundary"] == "after_system_bundle_task_attach"
    assert len(split["static_prefix_sha256"]) == 64
    assert len(split["dynamic_suffix_sha256"]) == 64
    assert set(split) == {"schema_version", "split_boundary",
                          "static_prefix_sha256",
                          "dynamic_suffix_sha256"}
    # Wire untouched: no cache params on the provider body.
    assert set(holder["body"]) == {"model", "input", "reasoning",
                                   "max_output_tokens"}
    ledger = tmp_path / "sessions" / bridge._CONTEXT_LEDGER_NAME
    row = json.loads(ledger.read_text(encoding="utf-8").strip()
                     .split("\n")[-1])
    assert row["prompt_cache_split"] == split
    assert set(row) == {"task_id", "budget_chars", "est_tokens",
                        "util_pct", "truncated", "model", "risk_tier",
                        "prompt_cache_split"}


def test_cache_split_stable_across_turns(tmp_path, monkeypatch):
    _clean_routing_env(monkeypatch)
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT",
                       str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "a", _ok_payload("a")),
                                    _FakeResp(200, "b", _ok_payload("b"))],
                      holder=holder)
    target = (bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn")
              else bridge.brain_turn)
    first = target("first-question", task_id="234")
    second = target("second-question", task_id="234")
    assert (first["prompt_cache_split"]["static_prefix_sha256"]
            == second["prompt_cache_split"]["static_prefix_sha256"])
    assert (first["prompt_cache_split"]["dynamic_suffix_sha256"]
            != second["prompt_cache_split"]["dynamic_suffix_sha256"])


def test_cache_split_leaks_nothing(tmp_path, monkeypatch):
    import json
    _clean_routing_env(monkeypatch)
    sentinel = "cache-leak-sentinel-zz7"
    result, _ = _run_turn_capture(
        monkeypatch, tmp_path, _ok_payload("ok"), prompt=sentinel)
    assert sentinel not in json.dumps(result["prompt_cache_split"])
    ledger = tmp_path / "sessions" / bridge._CONTEXT_LEDGER_NAME
    blob = ledger.read_text(encoding="utf-8")
    assert sentinel not in blob
    assert "sk-test-key" not in blob


# --- Prompt-cache split hotfix (QA_REJECTED F1-F4 -> M1-M4, Task 247) ---

def _failsafe_turn_setup(monkeypatch, tmp_path):
    _clean_routing_env(monkeypatch)
    _mk_tasks_root(tmp_path)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)


def test_cache_split_failsafe_wires_own_slot(tmp_path, monkeypatch):
    # M1: the failsafe branch must hash its attach in the failsafe
    # slot, never merged into the diff slot (F1).
    _failsafe_turn_setup(monkeypatch, tmp_path)
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))],
                      holder=holder)
    target = (bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn")
              else bridge.brain_turn)
    prompt = "qa engineer, adversarial review please"
    # Preflight seam (issue 18): the turn must resolve the same fixture
    # root the direct attach call below sees via the mocked workspace.
    result = target(prompt, task_id="200", include_bundle=False,
                    project_root=str(tmp_path))
    hunks = bridge._failsafe_qa_attach(prompt, "200")
    assert hunks  # guard: the failsafe really fired for this prompt
    expected = bridge.build_prompt_cache_split(
        "sys", "", "", prompt, diff_text="", failsafe_text=hunks,
        history=[])
    assert (result["prompt_cache_split"]["dynamic_suffix_sha256"]
            == expected["dynamic_suffix_sha256"])
    swapped = bridge.build_prompt_cache_split(
        "sys", "", "", prompt, diff_text=hunks, failsafe_text="",
        history=[])
    assert (swapped["dynamic_suffix_sha256"]
            != expected["dynamic_suffix_sha256"])


def test_cache_split_nul_role_cannot_collide():
    # M2: NUL-bearing history roles must not alias another segment
    # list (F2). Old framing hashed both histories below to the same
    # dynamic bytes: label "history[0].r" + content "q\x001\x00Y"
    # framed identically to role "r\x005\x00q" + content "Y".
    assert len("q\x001\x00Y") == 5  # honest length the collision pivots on
    a = bridge.build_prompt_cache_split(**_split_kwargs(
        history=[{"role": "r", "content": "q\x001\x00Y"}]))
    b = bridge.build_prompt_cache_split(**_split_kwargs(
        history=[{"role": "r\x005\x00q", "content": "Y"}]))
    assert (a["dynamic_suffix_sha256"]
            != b["dynamic_suffix_sha256"])


def test_cache_split_descriptor_matches_post_truncation_wire(
        tmp_path, monkeypatch):
    # M3: the descriptor must describe the SHIPPED (post-truncation)
    # wire, never the pre-truncation assembly (F3).
    _clean_routing_env(monkeypatch)
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
    _mk_sys_prompt(tmp_path, monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    monkeypatch.setattr(bridge, "_INPUT_BUDGET", 20)
    holder = {}
    _mk_bridge_client(monkeypatch, [_FakeResp(200, "a", _ok_payload("a")),
                                    _FakeResp(200, "b", _ok_payload("b"))],
                      holder=holder)
    target = (bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn")
              else bridge.brain_turn)
    target("first-question", task_id="234", include_bundle=False)
    second = target("second-question", task_id="234", include_bundle=False)
    shipped = holder["body"]["input"]
    shipped_history = [t for t in shipped[1:-1]]
    assert len(shipped_history) < 2  # the middle drop really fired
    expected = bridge.build_prompt_cache_split(
        "sys", "", "", "second-question", history=shipped_history)
    assert (second["prompt_cache_split"]["dynamic_suffix_sha256"]
            == expected["dynamic_suffix_sha256"])
    assert (second["prompt_cache_split"]["static_prefix_sha256"]
            == expected["static_prefix_sha256"])


def test_cache_split_static_lookup_skips_hash(monkeypatch):
    # M4: memoization must key on the static INPUTS, not hash-then-
    # lookup — a repeat static input must cost zero new static hashes
    # (F4). Two identical builds: miss (static + dynamic) then hit
    # (dynamic only) = exactly 3 sha256 calls.
    bridge._STATIC_SPLIT_CACHE.clear()
    real_sha256 = bridge.hashlib.sha256
    calls = []

    def counting(data=b""):
        calls.append(1)
        return real_sha256(data)

    monkeypatch.setattr(bridge.hashlib, "sha256", counting)
    kw = _split_kwargs()
    first = bridge.build_prompt_cache_split(**kw)
    second = bridge.build_prompt_cache_split(**kw)
    assert (first["static_prefix_sha256"]
            == second["static_prefix_sha256"])
    assert len(calls) == 3
