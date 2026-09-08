"""Unit tests for mcp-decision-server (Task 168).

Covers:
- `redactor.sanitize_text` / `verify_clean`: provider keys, bearer tokens,
  private IPs, credential assignments, idempotency, clean-text passthrough.
- Schema validation: valid record accepted, violations rejected.
- `record_manager_decision`: JSON + Markdown creation, daily sequencing,
  INDEX regeneration, schema-gate rejection — all inside a tmp decision
  repo via `DECISION_REPO_PATH` (never touches the real package).
- `query_manager_decisions`: keyword, category filter, no-match message.
- `get_manager_profile` / `propose_profile_evolution`: missing/empty/draft.
- `extract_session_decisions`: missing transcript → [], stubbed-LLM parse.

Run: `pytest tests/test_decision_server.py -v` (repo root).
"""

import importlib
import json
import os
import shutil
import sys
import types
from pathlib import Path

import pytest

DECISION_DIR = Path(__file__).parent.parent / "mcp-decision-server"
REAL_SCRIPTS = (
    Path(__file__).parent.parent
    / ".opencode" / "decisions" / "scripts"
)
sys.path.insert(0, str(DECISION_DIR))


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, DECISION_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def red():
    return _load("decision_redactor", "redactor.py")


@pytest.fixture(scope="module")
def srv():
    sys.modules["redactor"] = _load("decision_redactor", "redactor.py")
    return _load("decision_server", "server.py")


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    """Isolated decision repo (decisions/ + scripts/) per test."""
    monkeypatch.setenv("DECISION_REPO_PATH", str(tmp_path))
    (tmp_path / "decisions").mkdir()
    shutil.copytree(REAL_SCRIPTS, tmp_path / "scripts")
    return tmp_path


def _candidate(**overrides):
    base = {
        "project_name": "cognitive-lead-hq",
        "session_id": "168",
        "verbatim_quote": {
            "original": "از composition استفاده کن",
            "english_translation": "Use composition over inheritance",
        },
        "extracted_decision": {
            "summary": "Prefer composition over inheritance",
            "category": "architecture",
            "rationale": "Manager stated it as a standing rule",
            "alternatives": ["deep inheritance hierarchies"],
            "tradeoffs": "Slightly more wiring code",
        },
    }
    base.update(overrides)
    return base


# --- redactor ---------------------------------------------------------------

def test_sanitize_api_keys(red):
    dirty = "key=sk-proj-abc123XYZ456 and ghp_0123456789abcdef plus AIzaSyB1234567890abcd"
    clean = red.sanitize_text(dirty)
    assert "sk-proj-abc123XYZ456" not in clean
    assert "ghp_0123456789abcdef" not in clean
    assert "AIzaSyB1234567890abcd" not in clean
    assert red.verify_clean(clean) is True


def test_sanitize_bearer_and_ips(red):
    dirty = "Authorization: Bearer abcdef123456 sent from 10.0.3.7 via 192.168.1.1"
    clean = red.sanitize_text(dirty)
    assert "abcdef123456" not in clean
    assert "10.0.3.7" not in clean and "192.168.1.1" not in clean
    assert red.verify_clean(clean) is True


def test_sanitize_credential_assignment(red):
    dirty = 'config has password = "s3cr3t-hunter2" inside'
    clean = red.sanitize_text(dirty)
    assert "s3cr3t-hunter2" not in clean
    assert red.verify_clean(clean) is True


def test_verify_detects_raw_secrets(red):
    assert red.verify_clean("token sk-live-ABCDEF123456") is False
    assert red.verify_clean("server at 172.20.0.5") is False
    assert red.verify_clean("password=hunter2") is False


def test_sanitize_clean_text_passthrough_and_idempotent(red):
    text = "Prefer composition over inheritance for testability."
    assert red.sanitize_text(text) == text
    assert red.verify_clean(text) is True
    once = red.sanitize_text("key sk-proj-abc123XYZ456 here")
    assert red.sanitize_text(once) == once  # Fixed point: markers never re-match.
    assert red.verify_clean(once) is True


# --- record / validate ---------------------------------------------------------

def test_record_creates_json_md_and_index(srv, repo):
    result = srv.record_manager_decision.fn(_candidate()) \
        if hasattr(srv.record_manager_decision, "fn") else srv.record_manager_decision(_candidate())
    assert "Recorded DEC-" in result
    day_files = sorted((repo / "decisions").rglob("DEC-*.json"))
    assert len(day_files) == 1
    record = json.loads(day_files[0].read_text(encoding="utf-8"))
    assert record["redaction_verified"] is True
    assert record["verbatim_quote"]["original"] == "از composition استفاده کن"
    assert day_files[0].with_suffix(".md").is_file()
    index = (repo / "decisions" / "INDEX.md").read_text(encoding="utf-8")
    assert record["decision_id"] in index


def test_record_daily_sequence_increments(srv, repo):
    call = srv.record_manager_decision
    target = call.fn if hasattr(call, "fn") else call
    first = target(_candidate())
    second = target(_candidate())
    id1 = first.split("Recorded ")[1].split(" ")[0]
    id2 = second.split("Recorded ")[1].split(" ")[0]
    assert id1 != id2 and id1[:-3] == id2[:-3]  # Same day, next sequence.
    assert int(id2[-3:]) == int(id1[-3:]) + 1


def test_record_rejects_schema_violations(srv, repo):
    call = srv.record_manager_decision
    target = call.fn if hasattr(call, "fn") else call
    bad = _candidate()
    bad["extracted_decision"]["category"] = "not-a-category"
    with pytest.raises(ValueError, match="schema violations"):
        target(bad)
    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.


def test_record_scrubs_secrets_before_write(srv, repo):
    call = srv.record_manager_decision
    target = call.fn if hasattr(call, "fn") else call
    sneaky = _candidate()
    sneaky["extracted_decision"]["rationale"] = "approved, key sk-proj-SECRET1234567890 ok"
    target(sneaky)
    stored = json.loads(next((repo / "decisions").rglob("DEC-*.json")).read_text(encoding="utf-8"))
    assert "SECRET1234567890" not in json.dumps(stored)
    assert stored["redaction_verified"] is True


# --- query / profile / propose ---------------------------------------------------

def _record(call, cand):
    target = call.fn if hasattr(call, "fn") else call
    return target(cand)


def test_query_keyword_and_category(srv, repo):
    _record(srv.record_manager_decision, _candidate())
    other = _candidate()
    other["extracted_decision"] = {
        "summary": "QA gate needs two reviewers",
        "category": "quality-gate",
        "rationale": "Manager ruling after flaky release",
        "alternatives": [],
        "tradeoffs": "Slower merges",
    }
    _record(srv.record_manager_decision, other)
    call = srv.query_manager_decisions
    target = call.fn if hasattr(call, "fn") else call
    assert "composition" in target("composition").lower()
    assert "quality-gate" in target("", category="quality-gate")
    assert "No manager decisions match" in target("zzz-no-such-thing")


def test_get_manager_profile_missing_and_present(srv, repo, monkeypatch):
    call = srv.get_manager_profile
    target = call.fn if hasattr(call, "fn") else call
    assert "No manager profile" in target()
    samples = repo / "samples"
    samples.mkdir()
    (samples / "manager_profile.md").write_text("# Manager Profile\nBaseline.", encoding="utf-8")
    assert "Baseline" in target()


def test_propose_profile_empty_then_draft(srv, repo):
    call = srv.propose_profile_evolution
    target = call.fn if hasattr(call, "fn") else call
    assert target()["status"] == "EMPTY"
    _record(srv.record_manager_decision, _candidate())
    ready = target()
    assert ready["status"] == "DRAFT_READY"
    assert "Category distribution" in ready["draft"]


# --- extract (stubbed LLM) ---------------------------------------------------------

def test_extract_missing_transcript_returns_empty(srv, tmp_path):
    call = srv.extract_session_decisions
    target = call.fn if hasattr(call, "fn") else call
    assert target(424242, transcript_path=str(tmp_path / "nope.jsonl")) == []


def test_extract_parses_stubbed_llm_json(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        json.dumps({"role": "user", "content": "use composition", "name": "m",
                    "timestamp": "2026-09-08T00:00:00+00:00"}) + "\n",
        encoding="utf-8",
    )
    candidates = [{
        "verbatim_quote": {"original": "x", "english_translation": "y"},
        "extracted_decision": {"summary": "s", "category": "architecture",
                               "rationale": "r", "alternatives": [], "tradeoffs": "t"},
    }]
    message = types.SimpleNamespace(content=json.dumps(candidates))
    stub = types.ModuleType("litellm")
    stub.completion = lambda **kwargs: types.SimpleNamespace(
        choices=[types.SimpleNamespace(message=message)])
    monkeypatch.setitem(sys.modules, "litellm", stub)
    call = srv.extract_session_decisions
    target = call.fn if hasattr(call, "fn") else call
    assert target(1, transcript_path=str(transcript)) == candidates


def test_load_env_files_from_cwd_and_never_overrides(srv, tmp_path, monkeypatch):
    (tmp_path / ".env").write_text(
        "DECISION_TEST_PROBE=probe-value-456\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DECISION_TEST_PROBE", raising=False)
    srv._load_env_files()
    assert os.environ.get("DECISION_TEST_PROBE") == "probe-value-456"
    monkeypatch.setenv("DECISION_TEST_PROBE", "keep-me")
    srv._load_env_files()
    assert os.environ.get("DECISION_TEST_PROBE") == "keep-me"


def test_load_env_files_parent_fallback_without_cwd(srv, tmp_path, monkeypatch):
    # Same regression as persona server: no cwd .env → install-root .env.
    fake_root = tmp_path / "install"
    fake_server = fake_root / "mcp-decision-server"
    fake_server.mkdir(parents=True)
    (fake_root / ".env").write_text("DECISION_PARENT_PROBE=from-parent\n", encoding="utf-8")
    empty_cwd = tmp_path / "elsewhere"
    empty_cwd.mkdir()
    monkeypatch.chdir(empty_cwd)
    monkeypatch.delenv("DECISION_PARENT_PROBE", raising=False)
    loaded = srv._load_env_files(server_dir=fake_server)
    assert loaded is not None and loaded.endswith(".env")
    assert os.environ.get("DECISION_PARENT_PROBE") == "from-parent"


def test_decision_model_split_and_fallback(srv, monkeypatch):
    call = srv._get_decision_model
    monkeypatch.delenv("DECISION_MODEL", raising=False)
    monkeypatch.delenv("PERSONA_MODEL", raising=False)
    assert call() == "openrouter/deepseek/deepseek-v4-flash-0731"
    monkeypatch.setenv("PERSONA_MODEL", "openrouter/custom/persona")
    assert call() == "openrouter/custom/persona"
    monkeypatch.setenv("DECISION_MODEL", "openrouter/custom/extractor")
    assert call() == "openrouter/custom/extractor"
    monkeypatch.setenv("DECISION_MODEL", "   ")
    assert call() == "openrouter/custom/persona"  # Blank means unset.


def test_repo_root_prefers_cwd_project_store(srv, tmp_path, monkeypatch):
    # Project-aware resolution: <cwd>/.opencode/decisions wins without any env.
    monkeypatch.delenv("DECISION_REPO_PATH", raising=False)
    monkeypatch.chdir(tmp_path)
    root = srv._repo_root()
    assert root == tmp_path / ".opencode" / "decisions"
    assert root.is_dir()


def test_repo_root_explicit_override_wins(srv, tmp_path, monkeypatch):
    # Explicit DECISION_REPO_PATH beats the cwd convention.
    custom = tmp_path / "shared-store"
    monkeypatch.setenv("DECISION_REPO_PATH", str(custom))
    monkeypatch.chdir(tmp_path)
    assert srv._repo_root() == custom
    assert custom.is_dir()


def test_decision_temperature_default_and_overrides(srv, monkeypatch):
    monkeypatch.delenv("DECISION_TEMPERATURE", raising=False)
    assert srv._get_decision_temperature() == 1.0
    monkeypatch.setenv("DECISION_TEMPERATURE", "0.2")
    assert srv._get_decision_temperature() == 0.2
    monkeypatch.setenv("DECISION_TEMPERATURE", "not-a-float")
    assert srv._get_decision_temperature() == 1.0
    monkeypatch.setenv("DECISION_TEMPERATURE", "9.9")
    assert srv._get_decision_temperature() == 1.0  # Clamped, never crashes.


def test_repo_root_falls_back_when_cwd_blocked(srv, tmp_path, monkeypatch):
    # A FILE masquerading as .opencode makes mkdir raise (OSError subclass)
    # deterministically — resolution must fall through, not crash.
    (tmp_path / ".opencode").write_text("not a dir\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DECISION_REPO_PATH", raising=False)
    root = srv._repo_root()
    assert root != tmp_path / ".opencode" / "decisions"
    assert root.is_dir()


def test_tool_docstrings_carry_when_to_call(srv):
    # F8 guard (decision side): every MCP tool description must tell
    # OpenCode when to call it.
    tools = [
        srv.extract_session_decisions, srv.record_manager_decision,
        srv.query_manager_decisions, srv.get_manager_profile,
        srv.propose_profile_evolution,
    ]
    for tool in tools:
        fn = tool.fn if hasattr(tool, "fn") else tool
        assert "WHEN TO CALL" in (fn.__doc__ or ""), getattr(fn, "__name__", tool)
