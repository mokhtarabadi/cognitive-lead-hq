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
import re
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


def test_sanitize_env_style_assignment_names(red):
    # Task 242 B1: ENV-style names (BRAIN_API_KEY=, FOO_SECRET=) must redact —
    # the leading \b missed names joined by underscore.
    dirty = "BRAIN_API_KEY=abc123XYZ and FOO_SECRET=hunter2 and my-auth-token: zz99x"
    clean = red.sanitize_text(dirty)
    assert "abc123XYZ" not in clean
    assert "hunter2" not in clean
    assert "zz99x" not in clean
    assert red.verify_clean(clean) is True


def test_sanitize_short_bearer_with_digit(red):
    # Task 242 B1: short digit-bearing Bearer tokens must redact.
    dirty = "Authorization: Bearer abc123"
    clean = red.sanitize_text(dirty)
    assert "abc123" not in clean
    assert red.verify_clean(clean) is True


def test_no_false_positive_on_prose(red):
    # Guard: plain prose and letter-joined names must pass through untouched.
    assert red.sanitize_text("Bearer tokens are standard") == "Bearer tokens are standard"
    assert red.sanitize_text("topsecret=x") == "topsecret=x"
    assert red.verify_clean("Bearer tokens are standard") is True


def test_verify_detects_env_style_raw(red):
    assert red.verify_clean("FOO_SECRET=hunter2") is False
    assert red.verify_clean("Authorization: Bearer abc123") is False


def test_sanitize_short_bearer_punctuation_no_suffix_leak(red):
    # QA hotfix: `Bearer abcd-1` must fully redact — no `-1` suffix may leak.
    dirty = "Authorization: Bearer abcd-1"
    clean = red.sanitize_text(dirty)
    assert "abcd-1" not in clean
    assert "-1" not in clean
    assert red.verify_clean(clean) is True


def test_sanitize_quoted_assignment_value(red):
    # QA hotfix: quoted assignment values must redact end to end.
    dirty = 'FOO_SECRET="hunter2"'
    assert red.verify_clean(dirty) is False
    assert red.verify_clean(red.sanitize_text(dirty)) is True


def test_sanitize_quoted_colon_assignment_value(red):
    # QA hotfix: quoted colon-form values must redact end to end.
    dirty = "API_KEY: 'abc123'"
    assert red.verify_clean(dirty) is False
    assert red.verify_clean(red.sanitize_text(dirty)) is True


def test_letter_joined_name_passes_verify(red):
    # QA hotfix: letter-joined names are not credential assignments.
    assert red.sanitize_text("topsecret=x") == "topsecret=x"
    assert red.verify_clean("topsecret=x") is True


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


def test_query_hits_term_only_in_alternatives(srv, repo):
    """Regression: a keyword present only in alternatives[] must hit."""
    cand = _candidate()
    cand["extracted_decision"] = {
        "summary": "Adopt the new runner",
        "category": "tooling",
        "rationale": "Faster feedback on every push",
        "alternatives": ["keep the legacy zebracorn runner"],
        "tradeoffs": "Migration effort",
    }
    _record(srv.record_manager_decision, cand)
    call = srv.query_manager_decisions
    target = call.fn if hasattr(call, "fn") else call
    found = target("zebracorn")
    assert "No manager decisions match" not in found
    assert "Adopt the new runner" in found


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


# --- hardening (fidelity/mode/scope/fingerprint/ranked/sync) ---------------------

def test_record_sets_hardening_defaults(srv, repo):
    _record(srv.record_manager_decision, _candidate())
    record = json.loads(next((repo / "decisions").rglob("DEC-*.json")).read_text(encoding="utf-8"))
    assert record["fidelity"] == "verbatim"
    assert record["mode"] == "manual"
    assert record["scope"] == "episode"
    assert record["goal_ref"] == ""
    assert re.fullmatch(r"[0-9a-f]{64}", record["fingerprint"])


def test_record_rejects_bad_optionals(srv, repo):
    call = srv.record_manager_decision
    target = call.fn if hasattr(call, "fn") else call
    bad = _candidate()
    bad["fidelity"] = "telepathic"
    with pytest.raises(ValueError, match="schema violations"):
        target(bad)
    assert list((repo / "decisions").rglob("DEC-*.json")) == []


def test_record_duplicate_warns_not_blocks(srv, repo):
    call = srv.record_manager_decision
    target = call.fn if hasattr(call, "fn") else call
    first = target(_candidate())
    second = target(_candidate())
    assert "Recorded DEC-" in first and "Recorded DEC-" in second
    assert "Possible duplicate" in second


def test_query_ranked_summary_first(srv, repo):
    first = _candidate()
    first["extracted_decision"] = {
        "summary": "Adopt the zebracorn runner",
        "category": "tooling",
        "rationale": "Unrelated reason",
        "alternatives": [],
        "tradeoffs": "Unrelated cost",
    }
    second = _candidate()
    second["extracted_decision"] = {
        "summary": "Unrelated change",
        "category": "tooling",
        "rationale": "Unrelated reason",
        "alternatives": [],
        "tradeoffs": "Mentions zebracorn once",
    }
    _record(srv.record_manager_decision, first)
    _record(srv.record_manager_decision, second)
    call = srv.query_manager_decisions
    target = call.fn if hasattr(call, "fn") else call
    found = target("zebracorn")
    assert found.index("Adopt the zebracorn runner") < found.index("Unrelated change")


def test_sync_status_reports_debt(srv, repo):
    call = srv.get_sync_status
    target = call.fn if hasattr(call, "fn") else call
    status = target()
    assert "personal repo" in status
    assert "sync debt" in status or "not a git checkout" in status


def test_fingerprint_tolerates_string_quote(srv):
    fp = srv._decision_fingerprint({"verbatim_quote": "stray string",
                                    "extracted_decision": {"summary": "s"}})
    assert re.fullmatch(r"[0-9a-f]{64}", fp)


def test_fingerprint_scan_skips_nondict_file(srv, repo):
    bad = repo / "decisions" / "2026" / "09" / "DEC-20260914-099.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("[1, 2, 3]", encoding="utf-8")
    assert srv._find_fingerprint_hit(repo, "0" * 64) is None
    assert srv._rewrite_index(repo) == 0  # same H2 class, must not crash


def test_record_explicit_none_gets_defaults(srv, repo):
    call = srv.record_manager_decision
    target = call.fn if hasattr(call, "fn") else call
    cand = _candidate()
    cand["fidelity"] = None
    cand["mode"] = None
    cand["scope"] = None
    cand["goal_ref"] = None
    target(cand)
    record = json.loads(next((repo / "decisions").rglob("DEC-*.json")).read_text(encoding="utf-8"))
    assert record["fidelity"] == "verbatim"
    assert record["mode"] == "manual"
    assert record["scope"] == "episode"
    assert record["goal_ref"] == ""


# --- extract (stubbed LLM) ---------------------------------------------------------

def test_extract_missing_transcript_returns_empty(srv, tmp_path):
    call = srv.extract_session_decisions
    target = call.fn if hasattr(call, "fn") else call
    assert target(424242, transcript_path=str(tmp_path / "nope.jsonl")) == []


def test_extract_parses_stubbed_llm_json(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        json.dumps({"role": "user", "content": "ship it", "name": "m",
                    "timestamp": "2026-09-08T00:00:00+00:00"}) + "\n",
        encoding="utf-8",
    )
    candidates = [{
        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
        "extracted_decision": {"summary": "s", "category": "architecture",
                               "rationale": "r", "alternatives": [], "tradeoffs": "t"},
    }]
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


def test_decision_model_split_no_persona_fallback(srv, monkeypatch):
    call = srv._get_decision_model
    monkeypatch.delenv("DECISION_MODEL", raising=False)
    monkeypatch.setenv("PERSONA_MODEL", "openrouter/custom/persona")
    assert call() == "gpt-6-astra"  # Stale persona value never hijacks.
    monkeypatch.setenv("DECISION_MODEL", "openrouter/custom/extractor")
    assert call() == "openrouter/custom/extractor"
    monkeypatch.setenv("DECISION_MODEL", "   ")
    assert call() == "gpt-6-astra"  # Blank means unset.


def test_decision_env_precedence_over_brain_fallbacks(srv, monkeypatch):
    monkeypatch.setenv("BRAIN_API_BASE", "http://brain-base")
    monkeypatch.setenv("BRAIN_API_KEY", "sk-brain")
    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "low")
    monkeypatch.setenv("DECISION_API_BASE", "https://decisions-base")
    monkeypatch.setenv("DECISION_API_KEY", "sk-decisions")
    monkeypatch.setenv("DECISION_REASONING_EFFORT", "xhigh")
    assert srv._get_api_base() == "https://decisions-base"
    assert srv._get_api_key() == "sk-decisions"
    assert srv._get_decision_effort() == "xhigh"


def test_decision_env_blank_falls_back_to_brain(srv, monkeypatch):
    monkeypatch.setenv("BRAIN_API_BASE", "http://brain-base")
    monkeypatch.setenv("BRAIN_API_KEY", "sk-brain")
    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "low")
    monkeypatch.setenv("DECISION_API_BASE", "   ")
    monkeypatch.setenv("DECISION_API_KEY", "   ")
    monkeypatch.setenv("DECISION_REASONING_EFFORT", "   ")
    assert srv._get_api_base() == "http://brain-base"
    assert srv._get_api_key() == "sk-brain"
    assert srv._get_decision_effort() == "low"


def test_decision_api_key_fail_closed_names_both(srv, monkeypatch):
    monkeypatch.delenv("DECISION_API_KEY", raising=False)
    monkeypatch.delenv("BRAIN_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="DECISION_API_KEY/BRAIN_API_KEY"):
        srv._get_api_key()


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


# --- hotfix hardening (QA_REJECTED follow-up, mocked HTTP only) ---

import time as _time


def _write_min_transcript(path):
    path.write_text(
        json.dumps({"role": "user", "content": "ship it", "name": "m",
                    "timestamp": "2026-09-08T00:00:00+00:00"}) + "\n",
        encoding="utf-8",
    )


def _decision_resp(status_code=200, text="", payload=None, ctype="application/json"):
    def _json():
        if isinstance(payload, Exception):
            raise payload
        return payload
    return types.SimpleNamespace(
        status_code=status_code, text=text, headers={"content-type": ctype},
        raise_for_status=lambda: None, json=_json,
    )


def _stub_decision_http(monkeypatch, stub_resp):
    class _FakeClient:
        def __init__(self, *a, **k):
            self.kwargs = k

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


def _extract(srv):
    call = srv.extract_session_decisions
    return call.fn if hasattr(call, "fn") else call


def test_extract_empty_key_raises(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.delenv("BRAIN_API_KEY", raising=False)
    monkeypatch.delenv("DECISION_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="empty"):
        _extract(srv)(7, transcript_path=str(transcript))


def test_extract_500_final_raises(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setattr(_time, "sleep", lambda s: None)
    _stub_decision_http(monkeypatch, _decision_resp(500, "boom", {}))
    with pytest.raises(RuntimeError, match="500"):
        _extract(srv)(7, transcript_path=str(transcript))


def test_extract_non_json_raises(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    _stub_decision_http(
        monkeypatch, _decision_resp(200, "nope", ValueError("bad"), "text/plain"))
    with pytest.raises(RuntimeError, match="non-JSON"):
        _extract(srv)(7, transcript_path=str(transcript))


def test_extract_dict_wrapped_in_list(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    one = {
        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
        "extracted_decision": {"summary": "s", "category": "architecture",
                               "rationale": "r", "alternatives": [], "tradeoffs": "t"},
    }
    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", one))
    assert _extract(srv)(7, transcript_path=str(transcript)) == [one]


def test_extract_scalar_raises(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    _stub_decision_http(monkeypatch, _decision_resp(200, "42", 42))
    with pytest.raises(RuntimeError):
        _extract(srv)(7, transcript_path=str(transcript))


def test_extract_fenced_envelope_parsed(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    one = {
        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
        "extracted_decision": {"summary": "s", "category": "architecture",
                               "rationale": "r", "alternatives": [], "tradeoffs": "t"},
    }
    fenced = "```json\n" + json.dumps([one]) + "\n```"
    envelope = {"output": [{"type": "message",
                            "content": [{"type": "output_text", "text": fenced}]}]}
    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", envelope))
    assert _extract(srv)(7, transcript_path=str(transcript)) == [one]


# --- Hotfix-2 new tests (mocked httpx only) ---

def _script_client(script):
    class _ScriptClient:
        def __init__(self):
            self.calls = 0

        def post(self, *a, **k):
            self.calls += 1
            item = script.pop(0) if len(script) > 1 else script[0]
            if isinstance(item, Exception):
                raise item
            return item

    return _ScriptClient()


def test_post_overall_deadline_fast_fail(srv, monkeypatch):
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setattr(_time, "sleep", lambda s: None)
    monkeypatch.setattr(srv, "_OVERALL_DEADLINE_S", 0)
    with pytest.raises(RuntimeError, match="deadline"):
        srv._post_with_retry(
            _script_client([_decision_resp(500, "boom", {})]),
            "http://x/responses", {})


def test_post_retry_after_honored(srv, monkeypatch):
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    sleeps = []
    monkeypatch.setattr(_time, "sleep", lambda s: sleeps.append(s))
    r429 = _decision_resp(429, "slow down", {})
    r429.headers["Retry-After"] = "3"
    resp, _ = srv._post_with_retry(
        _script_client([r429, _decision_resp(200, "fine", {})]),
        "http://x/responses", {})
    assert resp.status_code == 200
    assert sleeps and sleeps[0] >= 3


def test_extract_rejects_candidates_envelope(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    envelope = {"output": [{"type": "message", "content": [
        {"type": "output_text",
         "text": json.dumps({"candidates": [{"verbatim_quote": {}, "extracted_decision": {}}]})}]}]}
    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", envelope))
    with pytest.raises(RuntimeError, match="candidates"):
        _extract(srv)(7, transcript_path=str(transcript))


def test_extract_missing_fields_rejected_with_index(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    bad = [{"verbatim_quote": {"original": "ship it", "english_translation": "y"}}]
    envelope = {"output": [{"type": "message", "content": [
        {"type": "output_text", "text": json.dumps(bad)}]}]}
    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", envelope))
    with pytest.raises(RuntimeError, match="0"):
        _extract(srv)(7, transcript_path=str(transcript))


def test_extract_empty_list_warns_not_errors(srv, tmp_path, monkeypatch, capsys):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    envelope = {"output": [{"type": "message", "content": [
        {"type": "output_text", "text": "[]"}]}]}
    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", envelope))
    assert _extract(srv)(7, transcript_path=str(transcript)) == []
    assert "non-empty" in capsys.readouterr().err


def test_extract_tries_each_fenced_block(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    one = {
        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
        "extracted_decision": {"summary": "s", "category": "architecture",
                               "rationale": "r", "alternatives": [], "tradeoffs": "t"},
    }
    text = ("```text\nnot json at all\n```\n"
            "```json\n" + json.dumps([one]) + "\n```")
    envelope = {"output": [{"type": "message", "content": [
        {"type": "output_text", "text": text}]}]}
    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", envelope))
    assert _extract(srv)(7, transcript_path=str(transcript)) == [one]


def test_temperature_pinned_zero_unless_set(srv, tmp_path, monkeypatch):
    # Task 191: the extraction call pins temperature 0 by default; an
    # explicitly set BRAIN_TEMPERATURE still wins (explicit override).
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    seen = {}

    def _stub_capture(resp_holder):
        class _FakeClient:
            def __init__(self, *a, **k):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def post(self, url, json=None, headers=None, **k):
                seen["body"] = json
                return resp_holder

        stub = types.ModuleType("httpx")
        stub.Client = _FakeClient
        stub.TimeoutException = type("TimeoutException", (Exception,), {})
        stub.TransportError = type("TransportError", (Exception,), {})

        class _Timeout:
            def __init__(self, *a, **k):
                pass

        stub.Timeout = _Timeout
        monkeypatch.setitem(sys.modules, "httpx", stub)

    one = {
        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
        "extracted_decision": {"summary": "s", "category": "architecture",
                               "rationale": "r", "alternatives": [], "tradeoffs": "t"},
    }
    envelope = {"output": [{"type": "message", "content": [
        {"type": "output_text", "text": json.dumps([one])}]}]}
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    monkeypatch.delenv("DECISION_TEMPERATURE", raising=False)
    _stub_capture(_decision_resp(200, "fine", envelope))
    _extract(srv)(7, transcript_path=str(transcript))
    assert "temperature" not in seen["body"]
    assert seen["body"]["reasoning"] == {"effort": "xhigh"}
    assert "reasoning_effort" not in seen["body"]
    srv._EXTRACT_CACHE.clear()
    monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
    monkeypatch.delenv("DECISION_TEMPERATURE", raising=False)
    _stub_capture(_decision_resp(200, "fine", envelope))
    _extract(srv)(7, transcript_path=str(transcript))
    assert seen["body"]["temperature"] == 0.7
    srv._EXTRACT_CACHE.clear()
    monkeypatch.setenv("BRAIN_TEMPERATURE", "1")
    monkeypatch.setenv("DECISION_TEMPERATURE", "0.5")
    _stub_capture(_decision_resp(200, "fine", envelope))
    _extract(srv)(7, transcript_path=str(transcript))
    assert seen["body"]["temperature"] == 0.5
    assert "reasoning_effort" not in seen["body"]


def test_invalid_effort_value_raises(srv, monkeypatch):
    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "bad effort!!")
    monkeypatch.delenv("DECISION_REASONING_EFFORT", raising=False)
    with pytest.raises(ValueError):
        srv._get_decision_effort()


# --- Task 191: deterministic extraction (mocked httpx only) ---

@pytest.fixture(autouse=True)
def _clear_extract_cache(srv):
    # The extract cache is module-level by design (same transcript +
    # same model => same key); isolate tests from each other.
    srv._EXTRACT_CACHE.clear()
    srv._last_cache_hits = 0
    srv._REPAIR_COUNT = 0
    yield
    srv._EXTRACT_CACHE.clear()


def _valid_one_191():
    return {
        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
        "extracted_decision": {"summary": "s", "category": "architecture",
                               "rationale": "r", "alternatives": [],
                               "tradeoffs": "t"},
    }


def _envelope_191(payload_text):
    return {"output": [{"type": "message", "content": [
        {"type": "output_text", "text": payload_text}]}]}


def _stub_counting_http(monkeypatch, resp_factory):
    """Fake httpx module whose client counts post() calls + bodies."""
    calls = {"n": 0, "bodies": []}

    class _FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, json=None, headers=None, **k):
            calls["n"] += 1
            calls["bodies"].append(json)
            return resp_factory()

    stub = types.ModuleType("httpx")
    stub.Client = _FakeClient
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            pass

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)
    return calls


def test_extract_repeat_determinism_five_times(srv, tmp_path, monkeypatch, capsys):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    monkeypatch.delenv("DECISION_TEMPERATURE", raising=False)
    one = _valid_one_191()
    calls = _stub_counting_http(
        monkeypatch,
        lambda: _decision_resp(200, "fine", _envelope_191(json.dumps([one]))),
    )
    results = [_extract(srv)(7, transcript_path=str(transcript)) for _ in range(5)]
    assert calls["n"] == 1  # Cache serves repeats: exactly one HTTP hit.
    blobs = [json.dumps(r, sort_keys=True) for r in results]
    assert all(b == blobs[0] for b in blobs)  # Byte-identical 5x.
    assert calls["bodies"][0]["reasoning"] == {"effort": "xhigh"}  # Max-effort default.
    assert capsys.readouterr().err.count("cache hit") == 4


def test_extract_cache_hit_zero_tokens(srv, tmp_path, monkeypatch, capsys):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    monkeypatch.delenv("DECISION_TEMPERATURE", raising=False)
    one = _valid_one_191()
    calls = _stub_counting_http(
        monkeypatch,
        lambda: _decision_resp(200, "fine", _envelope_191(json.dumps([one]))),
    )
    first = _extract(srv)(7, transcript_path=str(transcript))
    second = _extract(srv)(7, transcript_path=str(transcript))
    assert calls["n"] == 1
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert "cache hit" in capsys.readouterr().err


def test_extract_regex_fallback_salvages_exact_lines(srv, tmp_path, monkeypatch):
    line = "the manager ruled to prefer composition over inheritance"
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        json.dumps({"role": "manager", "content": line, "name": "m",
                    "timestamp": "2026-09-08T00:00:00+00:00"}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    text = ("My take:\n- " + line + "\n"
            "- something not in the transcript at all\n")
    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", _envelope_191(text)))
    result = _extract(srv)(7, transcript_path=str(transcript))
    assert len(result) == 1  # Only the exact-substring line salvages.
    assert result[0]["verbatim_quote"]["original"] == line
    assert line in open(transcript, encoding="utf-8").read()
    assert set(result[0]["extracted_decision"]) >= {
        "summary", "category", "rationale", "alternatives", "tradeoffs"}


def test_extract_garbage_raises_loudly(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    _stub_decision_http(
        monkeypatch,
        _decision_resp(
            200, "fine",
            _envelope_191("just some rambling prose with no structure whatsoever")),
    )
    with pytest.raises(RuntimeError):
        _extract(srv)(7, transcript_path=str(transcript))


def test_extract_auto_repair_once(srv, tmp_path, monkeypatch, capsys):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    one = _valid_one_191()
    # Fences are pre-handled: parse with no extra repair.
    _stub_decision_http(
        monkeypatch,
        _decision_resp(
            200, "fine",
            _envelope_191("```json\n" + json.dumps([one]) + "\n```")),
    )
    assert _extract(srv)(7, transcript_path=str(transcript)) == [one]
    assert capsys.readouterr().err.count("auto-repair") == 0
    # Fixable flaw: valid JSON embedded in prose (no fences) -> repaired.
    srv._EXTRACT_CACHE.clear()
    embedded = ("Here are the extracted decisions:\n" + json.dumps([one])
                + "\nThat is all.")
    _stub_decision_http(
        monkeypatch, _decision_resp(200, "fine", _envelope_191(embedded)))
    assert _extract(srv)(7, transcript_path=str(transcript)) == [one]
    assert capsys.readouterr().err.count("auto-repair") == 1
    # Unfixable garbage -> loud error, still at most one repair.
    srv._EXTRACT_CACHE.clear()
    _stub_decision_http(
        monkeypatch,
        _decision_resp(
            200, "fine",
            _envelope_191("total garbage with no json at all")),
    )
    with pytest.raises(RuntimeError):
        _extract(srv)(7, transcript_path=str(transcript))
    assert capsys.readouterr().err.count("auto-repair") == 1


def test_extract_strips_nonverbatim_evidence_links(srv, tmp_path, monkeypatch):
    # E4: evidence keys must be verbatim in the transcript; others are stripped.
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    one = {
        "verbatim_quote": {"original": "ship it",
                           "english_translation": "ship it"},
        "extracted_decision": {"summary": "ship it", "category": "architecture",
                               "rationale": "r", "alternatives": [], "tradeoffs": "t"},
        "evidence_links": ["nowhere in transcript", "ship it"],
    }
    _stub_decision_http(
        monkeypatch,
        _decision_resp(200, "fine", _envelope_191(json.dumps([one]))),
    )
    out = _extract(srv)(7, transcript_path=str(transcript))
    assert out[0]["evidence_links"] == ["ship it"]


# --- Task-191 hotfix round 2 (QA_REJECTED V1-V5/M1-M5, mocked HTTP only) ---

def _stub_capture(monkeypatch, stub_resp, seen):
    class _CapClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, json=None, headers=None, **k):
            seen.append(json)
            return stub_resp

    stub = types.ModuleType("httpx")
    stub.Client = _CapClient
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            pass

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)


def _ship_candidates():
    return [{
        "verbatim_quote": {"original": "ship it",
                           "english_translation": "ship it"},
        "extracted_decision": {"summary": "ship it", "category": "architecture",
                               "rationale": "r", "alternatives": [],
                               "tradeoffs": "t"},
    }]


def test_extract_temp_wire_default_zero(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
    monkeypatch.delenv("DECISION_TEMPERATURE", raising=False)
    seen = []
    _stub_capture(monkeypatch,
                  _decision_resp(200, "fine", _envelope_191(json.dumps(_ship_candidates()))),
                  seen)
    _extract(srv)(21, transcript_path=str(transcript))
    assert "temperature" not in seen[0]
    assert seen[0]["reasoning"] == {"effort": "xhigh"}
    assert "reasoning_effort" not in seen[0]


def test_extract_override_wins_and_key_changes(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
    seen = []
    _stub_capture(monkeypatch,
                  _decision_resp(200, "fine", _envelope_191(json.dumps(_ship_candidates()))),
                  seen)
    _extract(srv)(22, transcript_path=str(transcript))
    assert seen[0]["temperature"] == 0.7
    raw = transcript.read_bytes()
    assert (srv._extract_cache_key(raw, "m", 0.7)
            != srv._extract_cache_key(raw, "m", 0.0))


def test_extract_effort_absent_both_legs(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    for temp in (None, "0.7"):
        if temp is None:
            monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
        else:
            monkeypatch.setenv("BRAIN_TEMPERATURE", temp)
        seen = []
        _stub_capture(
            monkeypatch,
            _decision_resp(200, "fine", _envelope_191(json.dumps(_ship_candidates()))),
            seen)
        _extract(srv)(23, transcript_path=str(transcript))
        body = seen[-1]
        if temp is None:
            assert "temperature" not in body
            assert body["reasoning"] == {"effort": "xhigh"}
        else:
            assert body["temperature"] == 0.7
            assert "reasoning" not in body
        assert "reasoning_effort" not in body


def test_extract_cache_hit_logs_and_zero_hits(srv, tmp_path, monkeypatch, capsys):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    posts = []

    class _CountClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, *a, **k):
            posts.append(1)
            return _decision_resp(
                200, "fine", _envelope_191(json.dumps(_ship_candidates())))

    stub = types.ModuleType("httpx")
    stub.Client = _CountClient
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            pass

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)
    _extract(srv)(24, transcript_path=str(transcript))
    _extract(srv)(24, transcript_path=str(transcript))
    assert len(posts) == 1
    assert "cache hit" in capsys.readouterr().err


def test_extract_cache_evicts_oldest(srv, tmp_path, monkeypatch):
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    posts = []

    class _CountClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, *a, **k):
            posts.append(1)
            return _decision_resp(
                200, "fine", _envelope_191(json.dumps(_ship_candidates())))

    stub = types.ModuleType("httpx")
    stub.Client = _CountClient
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            pass

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)
    first = None
    for i in range(65):
        path = tmp_path / f"t{i}.jsonl"
        path.write_text(
            json.dumps({"role": "user", "content": f"ship it batch {i}",
                        "name": "m",
                        "timestamp": "2026-09-08T00:00:00+00:00"}) + "\n",
            encoding="utf-8",
        )
        if i == 0:
            first = str(path)
        _extract(srv)(25, transcript_path=str(path))
    assert len(srv._EXTRACT_CACHE) == 64
    _extract(srv)(25, transcript_path=first)
    assert len(posts) == 66


def test_extract_empty_transcript_raises(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("", encoding="utf-8")
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    with pytest.raises(RuntimeError):
        _extract(srv)(26, transcript_path=str(transcript))


def test_extract_multi_blob_largest_wins_repair_once(
        srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    # Case 1: invalid fence + valid fence → block-skipping suffices, no repair.
    fence1 = "```json\n{not valid json\n```"
    fence2 = "```json\n" + json.dumps(_ship_candidates()) + "\n```"
    before = srv._REPAIR_COUNT
    _stub_decision_http(
        monkeypatch, _decision_resp(200, "fine", _envelope_191(fence1 + "\n" + fence2)))
    out = _extract(srv)(27, transcript_path=str(transcript))
    assert out == _ship_candidates()
    assert srv._REPAIR_COUNT - before == 0
    # Case 2: prose-wrapped JSON needs exactly one largest-span repair.
    # NOTE: a fresh transcript file — same bytes would be a cache hit
    # and skip the pipeline entirely (counter stays 0 by design).
    transcript2 = tmp_path / "transcript2.jsonl"
    transcript2.write_text(
        json.dumps({"role": "user", "content": "ship it twice", "name": "m",
                    "timestamp": "2026-09-08T00:00:00+00:00"}) + "\n",
        encoding="utf-8",
    )
    wrapped = ("Here you go:\n" + json.dumps(_ship_candidates())
               + "\nhope this helps")
    before = srv._REPAIR_COUNT
    _stub_decision_http(
        monkeypatch, _decision_resp(200, "fine", _envelope_191(wrapped)))
    out = _extract(srv)(27, transcript_path=str(transcript2))
    assert out == _ship_candidates()
    assert srv._REPAIR_COUNT - before == 1


def test_extract_whitespace_only_raises(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("   \n\n  \n", encoding="utf-8")
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    with pytest.raises(RuntimeError):
        _extract(srv)(7, transcript_path=str(transcript))


def test_extract_invalid_temp_raises_loudly(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setenv("BRAIN_TEMPERATURE", "abc")
    with pytest.raises(ValueError):
        _extract(srv)(7, transcript_path=str(transcript))


# --- Task-198 error taxonomy (per-class, scripted HTTP) ---

_VALID_TAXONOMY_CAND = {
    "verbatim_quote": {"original": "ship it", "english_translation": "ship it"},
    "extracted_decision": {"summary": "s", "category": "architecture",
                           "rationale": "r", "alternatives": [], "tradeoffs": "t"},
}


class _SeqClient:
    """Scripted HTTP client: pops responses in order, counts posts."""

    def __init__(self, script):
        self._script = list(script)
        self.calls = 0

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def post(self, *a, **k):
        self.calls += 1
        item = self._script.pop(0) if len(self._script) > 1 else self._script[0]
        if isinstance(item, Exception):
            raise item
        return item


def _stub_seq_http(monkeypatch, script):
    client = _SeqClient(script)
    stub = types.ModuleType("httpx-seq")
    stub.Client = lambda *a, **k: client
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            pass

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)
    return client


def test_taxonomy_fatal_400_no_retry_decision(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    client = _stub_seq_http(monkeypatch, [_decision_resp(400, "bad request", {})])
    with pytest.raises(RuntimeError, match="no retry"):
        _extract(srv)(7, transcript_path=str(transcript))
    assert client.calls == 1


def test_taxonomy_fatal_401_no_retry_decision(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    client = _stub_seq_http(monkeypatch, [_decision_resp(401, "unauthorized", {})])
    with pytest.raises(RuntimeError, match="401"):
        _extract(srv)(7, transcript_path=str(transcript))
    assert client.calls == 1


def test_taxonomy_retryable_503_then_200_decision(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    monkeypatch.setattr(_time, "sleep", lambda s: None)
    script = [_decision_resp(503, "busy", {}),
              _decision_resp(200, "fine", [_VALID_TAXONOMY_CAND])]
    client = _stub_seq_http(monkeypatch, script)
    assert _extract(srv)(7, transcript_path=str(transcript)) == [_VALID_TAXONOMY_CAND]
    assert client.calls == 2


# --- hotfix taxonomy per-class tests (Step 4-9, direct _post unit) ---

class _TaxSeqClient:
    def __init__(self, script):
        self._script = list(script)
        self.calls = 0

    def post(self, url, json=None, headers=None, **k):
        self.calls += 1
        item = self._script.pop(0) if len(self._script) > 1 else self._script[0]
        if isinstance(item, Exception):
            raise item
        return item


def _tax_resp(status, text="x"):
    return types.SimpleNamespace(status_code=status, text=text, headers={})


def _tax_env(monkeypatch):
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    stub = types.ModuleType("httpx")
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})
    monkeypatch.setitem(sys.modules, "httpx", stub)
    return stub


def test_taxonomy_fatal_403_no_retry_post(srv, monkeypatch):
    _tax_env(monkeypatch)
    client = _TaxSeqClient([_tax_resp(403, "forbidden")])
    with pytest.raises(RuntimeError, match="no retry"):
        srv._post_with_retry(client, "http://x/responses", {})
    assert client.calls == 1


def test_taxonomy_fatal_404_no_retry_post(srv, monkeypatch):
    _tax_env(monkeypatch)
    client = _TaxSeqClient([_tax_resp(404, "not here")])
    with pytest.raises(RuntimeError, match="no retry"):
        srv._post_with_retry(client, "http://x/responses", {})
    assert client.calls == 1


def test_taxonomy_fatal_422_no_retry_post(srv, monkeypatch):
    _tax_env(monkeypatch)
    client = _TaxSeqClient([_tax_resp(422, "unprocessable")])
    with pytest.raises(RuntimeError, match="no retry"):
        srv._post_with_retry(client, "http://x/responses", {})
    assert client.calls == 1


def test_taxonomy_retryable_429_then_200_post(srv, monkeypatch):
    _tax_env(monkeypatch)
    monkeypatch.setattr(_time, "sleep", lambda s: None)
    client = _TaxSeqClient([_tax_resp(429, "slow"), _tax_resp(200, "fine")])
    resp, attempts = srv._post_with_retry(client, "http://x/responses", {})
    assert resp.status_code == 200
    assert attempts == 2


def test_taxonomy_timeout_then_200_post(srv, monkeypatch):
    stub = _tax_env(monkeypatch)
    monkeypatch.setattr(_time, "sleep", lambda s: None)
    client = _TaxSeqClient([stub.TimeoutException("timed out"),
                            _tax_resp(200, "fine")])
    resp, attempts = srv._post_with_retry(client, "http://x/responses", {})
    assert resp.status_code == 200
    assert attempts == 2


def test_taxonomy_message_contract_post(srv, monkeypatch):
    _tax_env(monkeypatch)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-SECRET-XYZ")
    client = _TaxSeqClient([_tax_resp(403, "denied detail")])
    with pytest.raises(RuntimeError) as exc:
        srv._post_with_retry(client, "http://x/responses", {})
    msg = str(exc.value)
    assert "403" in msg and "responses" in msg and "denied detail" in msg
    assert "SECRET" not in msg


def test_taxonomy_sleep_skipped_on_fatal_post(srv, monkeypatch):
    _tax_env(monkeypatch)
    sleeps = []
    monkeypatch.setattr(_time, "sleep", lambda s: sleeps.append(s))
    client = _TaxSeqClient([_tax_resp(404, "gone")])
    with pytest.raises(RuntimeError, match="no retry"):
        srv._post_with_retry(client, "http://x/responses", {})
    assert sleeps == []
    assert client.calls == 1


def test_taxonomy_non_httpx_error_propagates_post(srv, monkeypatch):
    _tax_env(monkeypatch)
    client = _TaxSeqClient([ValueError("boom")])
    with pytest.raises(ValueError, match="boom"):
        srv._post_with_retry(client, "http://x/responses", {})


# --- Task 213: decision-moment detector (mcp-decision-server/detector.py) ---

@pytest.fixture(scope="module")
def det():
    return _load("decision_detector", "detector.py")


def test_detector_flags_manager_ruling(det):
    turns = [
        {"speaker": "manager",
         "text": "We decided to use composition over inheritance for the auth "
                 "schema; the tradeoff is more boilerplate instead of magic."},
    ]
    out = det.detect_decision_moments(turns)
    assert len(out) == 1
    assert out[0]["turn_index"] == 0
    assert out[0]["passes"] is True
    assert "owner:manager" in out[0]["signals"]
    assert "strong-ruling" in out[0]["signals"]
    assert len(out[0]["excerpt"]) <= 200


def test_detector_ignores_agent_spoken_ruling(det):
    turns = [
        {"speaker": "agent",
         "text": "We decided to use composition over inheritance for the auth "
                 "schema; the tradeoff is more boilerplate instead of magic."},
        {"speaker": "Assistant",
         "text": "Approved: migrate the database instead of patching it."},
    ]
    assert det.detect_decision_moments(turns) == []


def test_detector_approved_alone_not_queued(det):
    turns = [
        {"speaker": "manager", "text": "approved"},
        {"speaker": "manager", "text": "thanks, looks good"},
        {"speaker": "agent", "text": "ok, continuing with the build"},
    ]
    assert det.detect_decision_moments(turns) == []


def test_detector_substring_lookalikes_not_queued(det):
    turns = [
        {"speaker": "manager",
         "text": "Add mustard to the dropdown; use a ruler for the layout."},
    ]
    assert det.detect_decision_moments(turns) == []


def test_detector_non_manager_owner_fails_bar(det):
    # Mixed-case non-manager speaker with ruling + scope content: skipped.
    turns = [
        {"speaker": "Agent",
         "text": "Approved: migrate the database instead of patching it."},
        {"speaker": " Manager ",
         "text": "Approved: migrate the database instead of patching it."},
    ]
    out = det.detect_decision_moments(turns)
    assert [c["turn_index"] for c in out] == [1]


def test_detector_weak_signals_need_strong_pairing(det):
    # Owner + weak modal + lone scope noun, no strong verb or tradeoff:
    # weak categories are dropped, bar fails, nothing queued.
    turns = [
        {"speaker": "manager",
         "text": "We must keep the api scope unchanged for now."},
    ]
    assert det.detect_decision_moments(turns) == []
    # Same weak signals + a tradeoff phrase: paired, queued.
    turns2 = [
        {"speaker": "manager",
         "text": "We must keep the api scope unchanged instead of expanding it."},
    ]
    out = det.detect_decision_moments(turns2)
    assert len(out) == 1 and out[0]["passes"] is True


def test_detector_long_unicode_truncates_on_word_edge(det):
    text = "Manager ruling: " + "تصمیم " * 60 + "approved: migrate the database instead."
    out = det.detect_decision_moments([{"speaker": "manager", "text": text}])
    assert len(out) == 1
    assert len(out[0]["excerpt"]) <= 200
    assert not out[0]["excerpt"].endswith(" ")


def test_detector_bar_requires_owner_and_two_categories(det):
    assert det.passes_precision_bar(["owner:manager", "strong-ruling", "scope-noun"]) is True
    assert det.passes_precision_bar([" Owner:Manager ", "strong-ruling", "scope-noun"]) is True
    assert det.passes_precision_bar([" Manager ", "strong-ruling", "scope-noun"]) is False  # raw speaker name is not an owner signal
    assert det.passes_precision_bar(["owner:manager", "strong-ruling"]) is False
    assert det.passes_precision_bar(["owner:manager", "weak-ruling", "scope-noun"]) is True  # paired upstream
    assert det.passes_precision_bar(["strong-ruling", "scope-noun", "tradeoff-marker"]) is False
    assert det.passes_precision_bar([]) is False
    assert det.passes_precision_bar("owner:manager") is False


def test_detector_never_raises_on_bad_input(det):
    assert det.detect_decision_moments([]) == []
    assert det.detect_decision_moments("not a list") == []
    valid = {"speaker": "manager",
             "text": "Decided: use X over Y for the auth schema."}
    out = det.detect_decision_moments(
        [None, {"speaker": "manager", "text": ""},
         {"speaker": "manager", "text": 123}, valid])
    assert [c["turn_index"] for c in out] == [3]


# --- Task 216: personal-repo provenance + fail-closed scrub on explicit path ---
# (uses the existing _record(call, cand) helper from line 174)

def test_active_root_info_names_personal_repo(srv, tmp_path, monkeypatch):
    monkeypatch.setenv("DECISION_REPO_PATH", str(tmp_path / "personal"))
    info = srv._active_root_info(tmp_path / "personal")
    assert "personal repo" in info
    assert "DECISION_REPO_PATH" in info


def test_active_root_info_names_project_fallback(srv, tmp_path, monkeypatch):
    monkeypatch.delenv("DECISION_REPO_PATH", raising=False)
    info = srv._active_root_info(tmp_path / ".opencode" / "decisions")
    assert "project fallback" in info


def test_personal_path_scrubs_secrets_before_write(srv, tmp_path, monkeypatch):
    # Task 216 public-default guard: on an explicit personal repo, secrets
    # are scrubbed before they touch the store — nothing sensitive persists.
    # (The scrub gate replaces recognized patterns; the schema gate rejects
    # malformed records. Both run on every root, personal included.)
    personal = tmp_path / "manager-decisions"
    monkeypatch.setenv("DECISION_REPO_PATH", str(personal))
    sneaky = _candidate()
    sneaky["extracted_decision"]["rationale"] = "approved, key sk-proj-SECRET1234567890 ok"
    _record(srv.record_manager_decision, sneaky)
    stored = json.loads(next(personal.rglob("DEC-*.json")).read_text(encoding="utf-8"))
    assert "SECRET1234567890" not in json.dumps(stored)
    assert stored["redaction_verified"] is True


def test_record_creates_store_on_fresh_personal_repo(srv, tmp_path, monkeypatch):
    # Fresh clone / first run: no decisions/ dir yet — record still works.
    personal = tmp_path / "fresh-personal"
    monkeypatch.setenv("DECISION_REPO_PATH", str(personal))
    assert not (personal / "decisions").exists()
    out = _record(srv.record_manager_decision, _candidate())
    assert "Recorded DEC-" in out
    assert (personal / "decisions").is_dir()


# --- Task 216 QA hotfix (F1-F5): provenance, fail-closed, stderr secrecy ---

def test_record_fail_closed_when_scrub_cannot_clean(srv, tmp_path, monkeypatch, capsys):
    # Gate ordering proof: with sanitizing disabled, a key-shaped input must
    # raise ValueError BEFORE any write — no JSON, no .md, no index entry.
    personal = tmp_path / "personal"
    monkeypatch.setenv("DECISION_REPO_PATH", str(personal))
    monkeypatch.setattr(srv, "sanitize_text", lambda t: t if isinstance(t, str) else str(t))
    sneaky = _candidate()
    sneaky["extracted_decision"]["rationale"] = "approved, key sk-proj-FAILCLOSED1 ok"
    with pytest.raises(ValueError, match="redaction failed"):
        _record(srv.record_manager_decision, sneaky)
    assert list(personal.rglob("DEC-*.json")) == []
    assert list(personal.rglob("DEC-*.md")) == []


def test_record_stderr_never_carries_secrets(srv, tmp_path, monkeypatch, capsys):
    personal = tmp_path / "personal"
    monkeypatch.setenv("DECISION_REPO_PATH", str(personal))
    secret = "sk-proj-STDERRPROOF12345678"
    sneaky = _candidate()
    sneaky["extracted_decision"]["rationale"] = f"approved, key {secret} ok"
    _record(srv.record_manager_decision, sneaky)
    captured = capsys.readouterr()
    assert "active store" in captured.err
    assert secret not in captured.err
    assert "SECRET" not in captured.err


def test_record_persists_queryable_provenance(srv, tmp_path, monkeypatch):
    personal = tmp_path / "personal"
    monkeypatch.setenv("DECISION_REPO_PATH", str(personal))
    _record(srv.record_manager_decision, _candidate())
    stored = json.loads(next(personal.rglob("DEC-*.json")).read_text(encoding="utf-8"))
    assert stored["active_root"] == personal.name  # display name only: no abs path leaks into public-default repos
    assert stored["store_mode"] == "personal"


def test_record_empty_env_falls_back_with_provenance(srv, tmp_path, monkeypatch):
    monkeypatch.setenv("DECISION_REPO_PATH", "")
    monkeypatch.chdir(tmp_path)
    _record(srv.record_manager_decision, _candidate())
    stored = json.loads(next((tmp_path / ".opencode" / "decisions").rglob("DEC-*.json")).read_text(encoding="utf-8"))
    assert stored["store_mode"] == "project-fallback"
    assert stored["active_root"] == "decisions"  # basename only (R1 privacy fix)


def test_record_nested_personal_path_created(srv, tmp_path, monkeypatch):
    deep = tmp_path / "a" / "b" / "personal"
    monkeypatch.setenv("DECISION_REPO_PATH", str(deep))
    out = _record(srv.record_manager_decision, _candidate())
    assert "Recorded DEC-" in out
    assert (deep / "decisions").is_dir()


def test_record_file_as_path_fails_closed_and_clear(srv, tmp_path, monkeypatch):
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setenv("DECISION_REPO_PATH", str(blocker))
    with pytest.raises(RuntimeError, match="DECISION_REPO_PATH"):
        _record(srv.record_manager_decision, _candidate())
    assert list(tmp_path.rglob("DEC-*.json")) == []


def test_record_double_write_sequential_ids(srv, tmp_path, monkeypatch):
    personal = tmp_path / "personal"
    monkeypatch.setenv("DECISION_REPO_PATH", str(personal))
    _record(srv.record_manager_decision, _candidate())
    _record(srv.record_manager_decision, _candidate())
    ids = sorted(p.name for p in personal.rglob("DEC-*.json"))
    assert len(ids) == 2 and ids[0] != ids[1]


# --- Task 219 (218 scope): auto-sync personal repo (pull on read, debt visible) ---

import shutil as _shutil

_HAS_GIT = _shutil.which("git") is not None
needs_git = pytest.mark.skipif(not _HAS_GIT, reason="git CLI not available")


def _git(repo, *args, env=None):
    import subprocess
    e = dict(os.environ)
    e["GIT_CONFIG_NOSYSTEM"] = "1"
    e["HOME"] = str(repo)
    if env:
        e.update(env)
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True, timeout=60, env=e)
    return r


def _git_repo(path, branch="main"):
    r = _git(path, "init", "-b", branch)
    assert r.returncode == 0, r.stderr
    _git(path, "config", "user.email", "t@t.t")
    _git(path, "config", "user.name", "t")
    (path / "seed.txt").write_text("seed")
    _git(path, "add", "-A")
    r = _git(path, "commit", "-m", "docs: seed")
    assert r.returncode == 0, r.stderr
    return path


def _no_pull_env(monkeypatch):
    monkeypatch.delenv("DECISION_NO_PULL", raising=False)


def test_sync_skipped_not_git_checkout(srv, tmp_path, monkeypatch):
    _no_pull_env(monkeypatch)
    assert srv._pull_latest(tmp_path) == "sync skipped (not a git checkout)"


@needs_git
def test_sync_skipped_no_upstream(srv, tmp_path, monkeypatch):
    _no_pull_env(monkeypatch)
    _git_repo(tmp_path)
    assert srv._pull_latest(tmp_path) == "sync skipped (no upstream configured)"


@needs_git
def test_sync_kill_switch(srv, tmp_path, monkeypatch):
    monkeypatch.setenv("DECISION_NO_PULL", "1")
    _git_repo(tmp_path)
    assert srv._ensure_fresh(tmp_path) == "sync skipped (DECISION_NO_PULL=1)"


@needs_git
def test_sync_pulls_latest(srv, tmp_path, monkeypatch):
    _no_pull_env(monkeypatch)
    origin = tmp_path / "origin.git"
    assert _git(tmp_path, "init", "--bare", "origin.git").returncode == 0
    other = tmp_path / "other"
    assert _git(tmp_path, "clone", str(origin), "other").returncode == 0
    _git(other, "config", "user.email", "t@t.t")
    _git(other, "config", "user.name", "t")
    (other / "seed.txt").write_text("seed")
    _git(other, "add", "-A")
    assert _git(other, "commit", "-m", "docs: seed").returncode == 0
    assert _git(other, "push", "-u", "origin", "HEAD:main").returncode == 0
    assert _git(origin, "symbolic-ref", "HEAD",
                "refs/heads/main").returncode == 0
    store = tmp_path / "store"
    assert _git(tmp_path, "clone", str(origin), "store").returncode == 0
    _git(store, "config", "user.email", "t@t.t")
    _git(store, "config", "user.name", "t")
    (other / "fresh.md").write_text("latest")
    _git(other, "add", "-A")
    assert _git(other, "commit", "-m", "docs: fresh").returncode == 0
    assert _git(other, "push", "origin", "HEAD:main").returncode == 0
    status = srv._pull_latest(store)
    assert status == "store pulled to latest"
    assert (store / "fresh.md").read_text() == "latest"


@needs_git
def test_sync_diverged_fails_closed(srv, tmp_path, monkeypatch):
    _no_pull_env(monkeypatch)
    origin = tmp_path / "origin.git"
    assert _git(tmp_path, "init", "--bare", "origin.git").returncode == 0
    store = tmp_path / "store"
    assert _git(tmp_path, "clone", str(origin), "store").returncode == 0
    _git(store, "config", "user.email", "t@t.t")
    _git(store, "config", "user.name", "t")
    (store / "a.txt").write_text("v1")
    _git(store, "add", "-A")
    assert _git(store, "commit", "-m", "docs: seed").returncode == 0
    assert _git(store, "push", "-u", "origin", "HEAD:main").returncode == 0
    assert _git(origin, "symbolic-ref", "HEAD",
                "refs/heads/main").returncode == 0
    other = tmp_path / "other"
    assert _git(tmp_path, "clone", str(origin), "other").returncode == 0
    _git(other, "config", "user.email", "t@t.t")
    _git(other, "config", "user.name", "t")
    (other / "a.txt").write_text("remote-change")
    _git(other, "add", "-A")
    assert _git(other, "commit", "-m", "docs: remote").returncode == 0
    assert _git(other, "push", "origin", "HEAD:main").returncode == 0
    (store / "a.txt").write_text("local-change")
    _git(store, "add", "-A")
    assert _git(store, "commit", "-m", "docs: local").returncode == 0
    with pytest.raises(RuntimeError):
        srv._pull_latest(store)
    assert _git(store, "status", "--porcelain").stdout.strip() == ""


@needs_git
def test_sync_offline_tolerant(srv, tmp_path, monkeypatch):
    _no_pull_env(monkeypatch)
    origin = tmp_path / "origin.git"
    assert _git(tmp_path, "init", "--bare", "origin.git").returncode == 0
    store = tmp_path / "store"
    assert _git(tmp_path, "clone", str(origin), "store").returncode == 0
    _git(store, "config", "user.email", "t@t.t")
    _git(store, "config", "user.name", "t")
    (store / "a.txt").write_text("v1")
    _git(store, "add", "-A")
    assert _git(store, "commit", "-m", "docs: seed").returncode == 0
    assert _git(store, "push", "-u", "origin", "HEAD:main").returncode == 0
    _shutil.rmtree(origin)
    status = srv._pull_latest(store)
    assert status == "sync warning (remote unreachable; reading local state)"


@needs_git
def test_record_reports_sync_debt(srv, tmp_path, monkeypatch):
    _no_pull_env(monkeypatch)
    monkeypatch.setenv("DECISION_REPO_PATH", str(tmp_path))
    _git_repo(tmp_path)
    (tmp_path / "decisions").mkdir(exist_ok=True)
    out = srv.record_manager_decision(_candidate())
    assert "Recorded DEC-" in out
    assert "sync debt:" in out
    assert "git push" in out


@needs_git
def test_sync_untracked_file_blocks_pull(srv, tmp_path, monkeypatch):
    # QA T3: untracked (??) files also trip the dirty-tree guard.
    _no_pull_env(monkeypatch)
    _git_repo(tmp_path)
    (tmp_path / "scratch.txt").write_text("untracked")
    assert srv._pull_latest(tmp_path) == "sync skipped (dirty tree)"


def test_run_git_sets_network_timeout(srv, tmp_path, monkeypatch):
    # QA T3: every git call carries a timeout so hung remotes fail, not hang.
    import subprocess as _sp
    seen = {}

    def fake_run(cmd, **kw):
        seen.update(kw)
        return _sp.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(srv.subprocess, "run", fake_run)
    srv._run_git(tmp_path, "rev-parse", "--git-dir")
    assert seen.get("timeout") == 60


@needs_git
def test_sync_diverged_reads_serve_stale_local_state(srv, tmp_path, monkeypatch):
    # Reviewer follow-up A1: a diverged personal repo must not take reads
    # offline. query + profile serve stale local state with a loud note
    # instead of raising; writes (record) stay fail-closed.
    _no_pull_env(monkeypatch)
    origin = tmp_path / "origin.git"
    assert _git(tmp_path, "init", "--bare", "origin.git").returncode == 0
    store = tmp_path / "store"
    assert _git(tmp_path, "clone", str(origin), "store").returncode == 0
    _git(store, "config", "user.email", "t@t.t")
    _git(store, "config", "user.name", "t")
    (store / "a.txt").write_text("v1")
    _git(store, "add", "-A")
    assert _git(store, "commit", "-m", "docs: seed").returncode == 0
    assert _git(store, "push", "-u", "origin", "HEAD:main").returncode == 0
    assert _git(origin, "symbolic-ref", "HEAD",
                "refs/heads/main").returncode == 0
    other = tmp_path / "other"
    assert _git(tmp_path, "clone", str(origin), "other").returncode == 0
    _git(other, "config", "user.email", "t@t.t")
    _git(other, "config", "user.name", "t")
    (other / "a.txt").write_text("remote-change")
    _git(other, "add", "-A")
    assert _git(other, "commit", "-m", "docs: remote").returncode == 0
    assert _git(other, "push", "origin", "HEAD:main").returncode == 0
    (store / "a.txt").write_text("local-change")
    _git(store, "add", "-A")
    assert _git(store, "commit", "-m", "docs: local").returncode == 0
    decs = store / "decisions"
    decs.mkdir(parents=True, exist_ok=True)
    (decs / "DEC-20260913-001.json").write_text(json.dumps({
        "decision_id": "DEC-20260913-001",
        "extracted_decision": {
            "summary": "use pull-before-read with stale fallback",
            "category": "architecture",
            "rationale": "reads must survive divergence",
        },
        "verbatim_quote": {"original": "x", "english_translation": "y"},
    }))
    (store / "samples").mkdir(exist_ok=True)
    (store / "samples" / "manager_profile.md").write_text("# profile\n")
    monkeypatch.setenv("DECISION_REPO_PATH", str(store))
    out = srv.query_manager_decisions("stale fallback")
    assert "DEC-20260913-001" in out
    assert "profile" in srv.get_manager_profile().lower()


# --- Task 248: malformed-shape hardening (RED first, GREEN after fix) ---

def _ship_pair():
    valid = {
        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
        "extracted_decision": {"summary": "s", "category": "architecture",
                               "rationale": "r", "alternatives": [],
                               "tradeoffs": "t"},
    }
    bad_tradeoffs = {
        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
        "extracted_decision": {"summary": "s2", "category": "architecture",
                               "rationale": "r2", "alternatives": [],
                               "tradeoffs": ["not", "a", "string"]},
    }
    return valid, bad_tradeoffs


def test_extract_drops_nonstring_tradeoffs_keeps_valid(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    valid, bad_tradeoffs = _ship_pair()
    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", [valid, bad_tradeoffs]))
    assert _extract(srv)(7, transcript_path=str(transcript)) == [valid]


def test_extract_all_bad_tradeoffs_returns_empty(srv, tmp_path, monkeypatch):
    transcript = tmp_path / "transcript.jsonl"
    _write_min_transcript(transcript)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    _, bad_tradeoffs = _ship_pair()
    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", [bad_tradeoffs]))
    assert _extract(srv)(7, transcript_path=str(transcript)) == []


def test_record_rejects_string_verbatim_quote(srv, repo):
    call = srv.record_manager_decision
    target = call.fn if hasattr(call, "fn") else call
    bad = _candidate()
    bad["verbatim_quote"] = "flat string, not a mapping"
    with pytest.raises(ValueError, match="verbatim_quote"):
        target(bad)
    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.


def test_record_rejects_string_extracted_decision(srv, repo):
    call = srv.record_manager_decision
    target = call.fn if hasattr(call, "fn") else call
    bad = _candidate()
    bad["extracted_decision"] = "flat string, not a mapping"
    with pytest.raises(ValueError, match="extracted_decision"):
        target(bad)
    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.


def test_record_rejects_string_alternatives(srv, repo):
    call = srv.record_manager_decision
    target = call.fn if hasattr(call, "fn") else call
    bad = _candidate()
    bad["extracted_decision"]["alternatives"] = "not-a-list"
    with pytest.raises(ValueError, match="alternatives"):
        target(bad)
    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.


def test_query_skips_tampered_record(srv, repo):
    _record(srv.record_manager_decision, _candidate())
    stored = next((repo / "decisions").rglob("DEC-*.json"))
    record = json.loads(stored.read_text(encoding="utf-8"))
    tampered_id = record["decision_id"]
    record["extracted_decision"] = "flat string, not a mapping"
    stored.write_text(json.dumps(record), encoding="utf-8")
    out = srv.query_manager_decisions("composition")
    assert isinstance(out, str)  # Never raises AttributeError.
    assert tampered_id not in out  # Tampered record is skipped, not scored.


# --- Task 248 QA hotfix: profile contract + nested leaf validation ---

def test_profile_absent_returns_stable_message(srv, repo):
    assert srv.get_manager_profile() == "No manager profile sample exists yet."


def test_profile_present_returns_content(srv, repo):
    samples = repo / "samples"
    samples.mkdir(exist_ok=True)
    (samples / "manager_profile.md").write_text("# Baseline\nPrefer composition.\n")
    out = srv.get_manager_profile()
    assert "Prefer composition." in out


_LEAF_CASES = [
    ("verbatim_quote", "original", "quote-original"),
    ("verbatim_quote", "english_translation", "quote-english"),
    ("extracted_decision", "summary", "decision-summary"),
    ("extracted_decision", "rationale", "decision-rationale"),
    ("extracted_decision", "tradeoffs", "decision-tradeoffs"),
]


@pytest.mark.parametrize("section,key,field", _LEAF_CASES)
def test_record_rejects_nonstring_leaf(srv, repo, section, key, field):
    call = srv.record_manager_decision
    target = call.fn if hasattr(call, "fn") else call
    bad = _candidate()
    bad[section][key] = ["not", "a", "string"]
    with pytest.raises(ValueError, match=field.split("-")[-1]):
        target(bad)
    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.


def test_record_rejects_nonstring_alternative_item(srv, repo):
    call = srv.record_manager_decision
    target = call.fn if hasattr(call, "fn") else call
    bad = _candidate()
    bad["extracted_decision"]["alternatives"] = ["fine", 123]
    with pytest.raises(ValueError, match="alternatives"):
        target(bad)
    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.


@pytest.mark.parametrize("falsey", [None, "", 0, False])
def test_query_skips_falsey_nonlist_alternatives(srv, repo, falsey):
    _record(srv.record_manager_decision, _candidate())
    stored = next((repo / "decisions").rglob("DEC-*.json"))
    record = json.loads(stored.read_text(encoding="utf-8"))
    tampered_id = record["decision_id"]
    record["extracted_decision"]["alternatives"] = falsey
    stored.write_text(json.dumps(record), encoding="utf-8")
    out = srv.query_manager_decisions("composition")
    assert isinstance(out, str)  # Never raises.
    assert tampered_id not in out  # Falsey non-list must not validate as [].


# --- Task 259: provider diagnostics + terminal failure surfacing ----------


def _write_transcript_text(path, text):
    """Write a one-turn transcript whose content varies per test.

    The extraction cache keys on transcript bytes, so tests must use
    distinct content to avoid cross-test cache hits. The quote ``ship it``
    is kept so candidate verbatim checks (exact-substring rule) pass.
    """
    path.write_text(
        json.dumps({"role": "user", "content": f"ship it {text}", "name": "m",
                    "timestamp": "2026-09-19T00:00:00+00:00"}) + "\n",
        encoding="utf-8",
    )


def _stub_and_extract(srv, monkeypatch, tmp_path, payload, tag):
    transcript = tmp_path / f"{tag}.jsonl"
    _write_transcript_text(transcript, tag)
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", payload))
    return _extract(srv)(tag, transcript_path=str(transcript))


def test_responses_diagnostics_full_payload(srv):
    payload = {
        "status": "incomplete",
        "incomplete_details": {"reason": "max_output_tokens"},
        "usage": {
            "input_tokens": 10, "output_tokens": 16384, "total_tokens": 16394,
            "output_tokens_details": {"reasoning_tokens": 16380},
        },
    }
    diag = srv._responses_diagnostics(payload)
    assert diag["status"] == "incomplete"
    assert diag["incomplete_reason"] == "max_output_tokens"
    assert diag["usage"] == {
        "input_tokens": 10, "output_tokens": 16384,
        "reasoning_tokens": 16380, "total_tokens": 16394,
    }
    assert diag["error"] is None and diag["refusal"] is None


def test_responses_diagnostics_tolerates_malformed(srv):
    for bad in (None, [], "text", 7, {"usage": "nope", "output": "nope",
                                      "incomplete_details": 5}):
        diag = srv._responses_diagnostics(bad)
        assert set(diag) == {
            "status", "incomplete_reason", "usage", "error", "refusal"}
        assert set(diag["usage"]) == {
            "input_tokens", "output_tokens", "reasoning_tokens", "total_tokens"}
        assert diag["error"] is None and diag["refusal"] is None


def test_responses_diagnostics_refusal_direct_and_nested(srv):
    direct = {"output": [{"type": "refusal", "refusal": "I cannot do that"}]}
    assert srv._responses_diagnostics(direct)["refusal"] == "I cannot do that"
    nested = {"output": [{"type": "message", "content": [
        {"type": "refusal", "refusal": "no thanks"}]}]}
    assert srv._responses_diagnostics(nested)["refusal"] == "no thanks"


def test_provider_failure_message_precedence(srv):
    err = {"error": "boom", "output": []}
    msg = srv._provider_failure_message(srv._responses_diagnostics(err))
    assert msg.startswith("decision model returned no text: PROVIDER_ERROR")
    assert "boom" in msg

    refusal = {"output": [{"type": "refusal", "refusal": "nope"}]}
    msg = srv._provider_failure_message(srv._responses_diagnostics(refusal))
    assert "PROVIDER_REFUSAL" in msg and "nope" in msg

    budget = {"status": "incomplete",
              "incomplete_details": {"reason": "max_output_tokens"},
              "usage": {"output_tokens": 5}, "output": []}
    msg = srv._provider_failure_message(srv._responses_diagnostics(budget))
    assert msg.startswith("decision model returned no text: OUTPUT_BUDGET_EXHAUSTED")
    assert "NOT a model blank" in msg

    # No cause => None so the caller keeps the generic non-JSON error.
    assert srv._provider_failure_message(
        srv._responses_diagnostics({"output": []})) is None


def test_extract_budget_exhaustion_terminal(srv, tmp_path, monkeypatch):
    payload = {
        "status": "incomplete",
        "incomplete_details": {"reason": "max_output_tokens"},
        "usage": {"output_tokens": 16384,
                  "output_tokens_details": {"reasoning_tokens": 16380}},
        "output": [{"type": "reasoning"}],
    }
    with pytest.raises(RuntimeError, match="OUTPUT_BUDGET_EXHAUSTED") as exc:
        _stub_and_extract(srv, monkeypatch, tmp_path, payload, "budget")
    # Terminal diagnosis must not masquerade as a transcript/model blank.
    assert "non-JSON" not in str(exc.value)
    assert "max_output_tokens" in str(exc.value)


def test_extract_provider_error_terminal(srv, tmp_path, monkeypatch):
    payload = {"error": {"message": "upstream exploded"}, "output": []}
    with pytest.raises(RuntimeError, match="PROVIDER_ERROR") as exc:
        _stub_and_extract(srv, monkeypatch, tmp_path, payload, "perr")
    assert "upstream exploded" in str(exc.value)


def test_extract_refusal_terminal(srv, tmp_path, monkeypatch):
    payload = {"output": [{"type": "refusal", "refusal": "I will not"}]}
    with pytest.raises(RuntimeError, match="PROVIDER_REFUSAL") as exc:
        _stub_and_extract(srv, monkeypatch, tmp_path, payload, "pref")
    assert "I will not" in str(exc.value)


def test_extract_genuine_blank_stays_generic(srv, tmp_path, monkeypatch):
    # No provider cause: the ordinary empty envelope keeps its old error.
    with pytest.raises(RuntimeError, match="non-JSON"):
        _stub_and_extract(srv, monkeypatch, tmp_path, {"output": []}, "blank")


def test_extract_logs_provider_diag_on_success(srv, tmp_path, monkeypatch, capsys):
    one = {
        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
        "extracted_decision": {"summary": "s", "category": "architecture",
                               "rationale": "r", "alternatives": [],
                               "tradeoffs": "t"},
    }
    payload = {"status": "completed", "usage": {"output_tokens": 3},
               "output": [{"type": "message", "content": [
                   {"type": "output_text", "text": json.dumps(one)}]}]}
    assert _stub_and_extract(
        srv, monkeypatch, tmp_path, payload, "diagnostics") == [one]
    err = capsys.readouterr().err
    assert "provider diag" in err
    assert "status=completed" in err


def test_responses_diagnostics_scalar_content_does_not_raise(srv):
    # A malformed nested "content" scalar must not abort diagnosis (QA F1).
    for bad_content in (1, "text", {"type": "refusal"}, True):
        diag = srv._responses_diagnostics(
            {"output": [{"type": "message", "content": bad_content}]})
        assert set(diag) == {
            "status", "incomplete_reason", "usage", "error", "refusal"}
        assert diag["refusal"] is None


def test_responses_diagnostics_non_finite_usage_is_none(srv):
    # nan/inf raise inside int(); the parser must swallow them (QA F2).
    diag = srv._responses_diagnostics({
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


def test_provider_failure_message_scalar_usage_still_terminal(srv):
    # A hand-built diagnostic with a scalar usage must not raise in the
    # budget branch; terminal classification survives with null usage (QA F3).
    diag = {
        "status": "incomplete",
        "incomplete_reason": "max_output_tokens",
        "usage": 5,
        "error": None,
        "refusal": None,
    }
    msg = srv._provider_failure_message(diag)
    assert msg.startswith("decision model returned no text: OUTPUT_BUDGET_EXHAUSTED")
    assert "input=None" in msg
