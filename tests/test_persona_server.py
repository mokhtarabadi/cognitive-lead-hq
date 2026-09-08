"""Unit tests for mcp-persona-server (Task 167).

Covers:
- ``dual_dispatch.extract_xml``: valid XML, malformed XML, conversational
  preamble/trailing text, and pure question text.
- ``dual_dispatch.is_clarification_question``: questions vs reports.
- ``session`` transcript serialization + persistence (isolated via a tmp
  sessions dir) and lineage message assembly.
- ``server`` environment variable fallbacks and dispatch status
  classification (``XML_EXTRACTED`` / ``QUESTION`` / ``REPORT`` /
  ``RETRY_NEEDED``) with a stubbed ``litellm`` module — no network.
- ``telegram`` approval flow via stub transport + missing-credential
  degradation.

Run: ``pytest tests/test_persona_server.py -v`` (repo root).
"""

import importlib
import json
import os
import sys
import types
from pathlib import Path

import pytest

PERSONA_DIR = Path(__file__).parent.parent / "mcp-persona-server"
sys.path.insert(0, str(PERSONA_DIR))


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, PERSONA_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # So cross-imports (server -> session) resolve.
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def dual():
    return _load("persona_dual_dispatch", "dual_dispatch.py")


@pytest.fixture(scope="module")
def sess(tmp_path_factory):
    mod = _load("persona_session", "session.py")
    mod.SESSIONS_ROOT = tmp_path_factory.mktemp("sessions")
    return mod


@pytest.fixture(scope="module")
def server_mod(sess):
    # server.py does `from session import ...` — alias our loaded module.
    sys.modules["session"] = sess
    sys.modules["dual_dispatch"] = _load("persona_dual_dispatch", "dual_dispatch.py")
    sys.modules["telegram"] = _load("persona_telegram", "telegram.py")
    return _load("persona_server", "server.py")


# --- extract_xml -----------------------------------------------------------

VALID_XML = """<hands_implementation_task>
  <validation_phase>check rules</validation_phase>
</hands_implementation_task>"""


def test_extract_xml_valid_block(dual):
    has_xml, xml, clean = dual.extract_xml(VALID_XML)
    assert has_xml is True
    assert xml == VALID_XML
    assert clean == ""


def test_extract_xml_with_preamble_and_trailing(dual):
    text = "Here is your next instruction:\n\n" + VALID_XML + "\n\nGood luck!"
    has_xml, xml, clean = dual.extract_xml(text)
    assert has_xml is True
    assert xml == VALID_XML
    assert "Here is your next instruction" in clean
    assert "Good luck!" in clean
    assert "<hands_implementation_task>" not in clean


def test_extract_xml_malformed_missing_close(dual):
    text = "<hands_implementation_task>\n  <validation_phase>oops, no close tag"
    has_xml, xml, clean = dual.extract_xml(text)
    assert has_xml is False
    assert xml is None
    # Malformed input falls through unchanged (stripped) for downstream handling.
    assert clean == text.strip()


def test_extract_xml_pure_question_text(dual):
    text = "Which model should I use for the QA persona?"
    has_xml, xml, clean = dual.extract_xml(text)
    assert has_xml is False
    assert xml is None
    assert clean == text


def test_extract_xml_failure_report_tag(dual):
    text = "<failure_report>\nBuild failed.\n</failure_report>"
    has_xml, xml, clean = dual.extract_xml(text)
    assert has_xml is True
    assert xml == text


def test_extract_xml_empty_input(dual):
    assert dual.extract_xml("") == (False, None, "")


def test_extract_xml_mismatched_tags_not_matched(dual):
    text = "<hands_implementation_task>\nbody\n</hands_qa_task>"
    has_xml, xml, clean = dual.extract_xml(text)
    assert has_xml is False
    assert xml is None


# --- is_clarification_question ----------------------------------------------

def test_question_mark_detected(dual):
    # V1 precision rule: interrogative match (which) + "?" counts.
    assert dual.is_clarification_question("Which test suite should I run?") is True


def test_request_for_missing_context_detected(dual):
    # V1 precision rule: leading "please provide" counts even without "?".
    assert dual.is_clarification_question(
        "Please provide the missing acceptance criteria."
    ) is True


def test_bare_question_mark_not_a_question(dual):
    # V1 precision rule: the naive "any ? means question" rule is removed.
    # "Deploy at dawn?" matches no interrogative pattern and leads with no
    # interrogative phrase, so it is a statement, not a clarification request.
    assert dual.is_clarification_question("Deploy at dawn?") is False


def test_is_clarification_question_ignores_questions_in_reports(dual):
    # T1: decision tokens win over embedded diagnostic/rhetorical questions.
    assert dual.is_clarification_question(
        "Did boundary test pass? Yes. Status: QA_PASSED."
    ) is False
    assert dual.is_clarification_question(
        "FAILED: 2 checks red. Why did the gateway test fail? Timeout."
    ) is False
    assert dual.is_clarification_question(
        "Review verdict: APPROVED_WITH_CHANGES. Can you confirm the two nits?"
    ) is False


def test_report_not_a_question(dual):
    assert dual.is_clarification_question(
        "All 55 tests pass. The implementation is complete and verified."
    ) is False


def test_empty_not_a_question(dual):
    assert dual.is_clarification_question("") is False


def test_xml_contents_ignored_for_question_check(dual):
    # The XML block itself contains no question; trailing text is a statement.
    text = VALID_XML + "\n\nDispatch acknowledged, proceeding."
    assert dual.is_clarification_question(text) is False


# --- session transcript ------------------------------------------------------

def test_session_append_and_read_round_trip(sess):
    sess.append_turn(167, "user", "Run QA", name="executor")
    sess.append_turn(167, "assistant", "QA passed", name="QA Engineer")
    turns = sess.read_transcript(167)
    assert len(turns) == 2
    assert turns[0]["role"] == "user" and turns[0]["content"] == "Run QA"
    assert turns[0]["name"] == "executor"
    assert turns[1]["role"] == "assistant" and turns[1]["name"] == "QA Engineer"
    assert all(t["timestamp"] for t in turns)


def test_session_transcript_is_jsonl(sess):
    path = sess.transcript_path(167)
    assert path.is_file()
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)  # Must not raise: one JSON object per line.
        assert {"role", "content", "name", "timestamp"} <= set(record)


def test_session_read_missing_transcript_empty(sess):
    assert sess.read_transcript(999999) == []


def test_session_invalid_task_id_rejected(sess):
    with pytest.raises(ValueError):
        sess.session_dir("not-an-int")


def test_session_build_messages_lineage_order(sess, tmp_path):
    # Lineage files resolve against repo_root; transcript replays in the middle.
    (tmp_path / "system-prompt.md").write_text("GLOBAL-SYSTEM", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("REPO-RULES", encoding="utf-8")
    (tmp_path / "prompts").mkdir()
    (tmp_path / "prompts" / "fragments").mkdir(parents=True)
    (tmp_path / "prompts" / "fragments" / "06-personas.md").write_text(
        "PERSONA-DEFS", encoding="utf-8"
    )
    task_file = tmp_path / "task.md"
    task_file.write_text("TASK-BODY", encoding="utf-8")

    sess.append_turn(168, "user", "prior instruction")
    sess.append_turn(168, "assistant", "prior answer")
    messages = sess.build_persona_messages(
        168, "QA Engineer", "new instruction", str(task_file), repo_root=tmp_path
    )
    roles = [m["role"] for m in messages]
    assert roles[0] == "system"  # Global lineage first.
    assert "GLOBAL-SYSTEM" in messages[0]["content"]
    assert "REPO-RULES" in messages[0]["content"]
    assert any("PERSONA-DEFS" in m["content"] for m in messages)  # Persona brief.
    assert any("TASK-BODY" in m["content"] for m in messages)  # Task file.
    assert messages[-1] == {"role": "user", "content": "new instruction"}  # Newest last.
    assert set(messages[-1]) == {"role", "content"}  # LiteLLM fields only.


def test_session_summary_ledger(sess):
    summary = sess.summarize_session(167)
    assert summary["task_id"] == 167
    assert summary["turn_count"] == 2
    assert summary["turns_by_role"] == {"user": 1, "assistant": 1}
    assert summary["first_turn_at"] and summary["last_turn_at"]
    assert "QA passed" in (summary["latest_assistant_excerpt"] or "")


# --- server env fallbacks -----------------------------------------------------

def test_env_fallback_defaults(server_mod, monkeypatch):
    for var in (
        "PERSONA_MODEL",
        "PERSONA_REASONING_EFFORT",
        "PERSONA_TEMPERATURE",
        "PERSONA_MAX_TOKENS",
    ):
        monkeypatch.delenv(var, raising=False)
    assert server_mod._get_persona_model() == "openrouter/deepseek/deepseek-v4-flash-0731"
    assert server_mod._get_reasoning_effort() == "high"
    assert server_mod._get_temperature() == 1.0
    assert server_mod._get_max_tokens() == 16384


def test_env_overrides_respected(server_mod, monkeypatch):
    monkeypatch.setenv("PERSONA_MODEL", "openrouter/custom/model")
    monkeypatch.setenv("PERSONA_REASONING_EFFORT", "low")
    monkeypatch.setenv("PERSONA_TEMPERATURE", "0.7")
    monkeypatch.setenv("PERSONA_MAX_TOKENS", "4096")
    assert server_mod._get_persona_model() == "openrouter/custom/model"
    assert server_mod._get_reasoning_effort() == "low"
    assert server_mod._get_temperature() == 0.7
    assert server_mod._get_max_tokens() == 4096


def test_env_invalid_numeric_falls_back(server_mod, monkeypatch):
    monkeypatch.setenv("PERSONA_TEMPERATURE", "not-a-float")
    monkeypatch.setenv("PERSONA_MAX_TOKENS", "not-an-int")
    assert server_mod._get_temperature() == 1.0
    assert server_mod._get_max_tokens() == 16384


# --- dispatch classification (stubbed LLM) -------------------------------------

def _stub_litellm(text):
    """Fake litellm module whose completion returns ``text`` as the reply."""
    message = types.SimpleNamespace(content=text)
    choice = types.SimpleNamespace(message=message)
    response = types.SimpleNamespace(choices=[choice])
    stub = types.ModuleType("litellm")
    stub.completion = lambda **kwargs: response
    return stub


def test_dispatch_xml_extracted(server_mod, sess, monkeypatch):
    monkeypatch.setitem(sys.modules, "litellm", _stub_litellm("Preamble\n" + VALID_XML))
    result = server_mod.dispatch_session_turn.fn(
        171, "QA Engineer", "review this", task_file_path=None
    ) if hasattr(server_mod.dispatch_session_turn, "fn") else server_mod.dispatch_session_turn(
        171, "QA Engineer", "review this", task_file_path=None
    )
    assert result["status"] == "XML_EXTRACTED"
    assert result["xml_content"] == VALID_XML
    assert result["task_id"] == 171


def test_dispatch_question(server_mod, monkeypatch):
    monkeypatch.setitem(
        sys.modules, "litellm", _stub_litellm("Which files should I review?")
    )
    call = server_mod.dispatch_session_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target(172, "Code Reviewer", "review this")
    assert result["status"] == "QUESTION"
    assert "Which files" in result["question"]


def test_dispatch_report(server_mod, monkeypatch):
    monkeypatch.setitem(
        sys.modules, "litellm", _stub_litellm("All checks pass. No blocking findings.")
    )
    call = server_mod.dispatch_session_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target(173, "QA Engineer", "test this")
    assert result["status"] == "REPORT"
    assert "No blocking findings" in result["report"]


def test_dispatch_force_xml_retry(server_mod, monkeypatch):
    monkeypatch.setitem(sys.modules, "litellm", _stub_litellm("Just a plain report."))
    call = server_mod.dispatch_session_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target(174, "QA Engineer", "test this", force_xml=True)
    assert result["status"] == "RETRY_NEEDED"
    assert "hint" in result


# --- telegram transport ---------------------------------------------------------

def _queue_transport(queue, calls):
    """Fake Bot API transport backed by a FIFO update queue.

    - ``sendMessage`` records the payload and returns a message id.
    - ``answerCallbackQuery`` records the ack and returns ok.
    - ``getUpdates`` with ``offset=-1`` peeks at the newest queued update
      WITHOUT consuming it (mirrors the real discard probe); any other
      offset consumes and returns updates with ``update_id >= offset``.
    """
    def fake(method, payload):
        calls.append((method, payload))
        if method == "sendMessage":
            return {"ok": True, "result": {"message_id": len(calls)}}
        if method == "answerCallbackQuery":
            return {"ok": True, "result": True}
        if method == "getUpdates":
            if payload.get("offset") == -1:
                newest = queue[-1:] if queue else []
                return {"ok": True, "result": list(newest)}
            offset = payload.get("offset", 0)
            due = [u for u in queue if u.get("update_id", 0) >= offset]
            del queue[:]
            return {"ok": True, "result": due}
        raise AssertionError(method)
    return fake


def _approval_update(update_id, chat_id, data):
    return {
        "update_id": update_id,
        "callback_query": {
            "id": f"cb-{update_id}",
            "data": data,
            "message": {"chat": {"id": chat_id}},
        },
    }


def test_telegram_approval_approve_flow(server_mod, monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    monkeypatch.setenv("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "10")
    # The manager can only press the button AFTER the gate message exists,
    # so the decision is staged on send (queuing it earlier would model a
    # stale update, which the discard probe must skip).
    queue = []
    calls = []
    base = _queue_transport(queue, calls)

    def staged(method, payload):
        if method == "sendMessage":
            queue.append(_approval_update(7, 12345, "approve:175:QA"))
        return base(method, payload)

    telegram = sys.modules["telegram"]
    result = telegram.send_approval_request(
        175, "QA", "All green.", transport=staged, ask_note=False
    )
    assert result["sent"] is True
    assert result["decision"] == "approve"
    assert result["note"] is None
    assert result["update_id"] == 7
    methods = [m for m, _ in calls]
    assert "sendMessage" in methods and "getUpdates" in methods


def test_telegram_approval_with_manager_note(server_mod, monkeypatch):
    # Manager approves, then types a note at the force-reply prompt.
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    monkeypatch.setenv("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "10")
    queue = []
    calls = []
    base = _queue_transport(queue, calls)
    sends = []

    def staged(method, payload):
        if method == "sendMessage":
            sends.append(payload)
            if len(sends) == 1:  # Gate message → decision press.
                queue.append(_approval_update(7, 12345, "approve:175:QA"))
            elif len(sends) == 2:  # Note prompt → typed note.
                queue.append({
                    "update_id": 8,
                    "message": {"chat": {"id": 12345}, "text": "ship it, then tag"},
                })
        return base(method, payload)

    telegram = sys.modules["telegram"]
    result = telegram.send_approval_request(175, "QA", "All green.", transport=staged)
    assert result["sent"] is True
    assert result["decision"] == "approve"
    assert result["note"] == "ship it, then tag"
    # The note prompt used a force-reply keyboard.
    assert sends[1].get("reply_markup", {}).get("force_reply") is True


def test_telegram_approval_note_silence_never_blocks(server_mod, monkeypatch):
    # Manager decides, then goes silent: gate still resolves, note is None.
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    monkeypatch.setenv("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "10")
    queue = []
    calls = []
    base = _queue_transport(queue, calls)

    def staged(method, payload):
        if method == "sendMessage" and not queue:
            # Only the decision ever arrives; the note prompt goes unanswered.
            queue.append(_approval_update(7, 12345, "reject:175:QA"))
        return base(method, payload)

    telegram = sys.modules["telegram"]
    result = telegram.send_approval_request(
        175, "QA", "All green.", transport=staged, note_timeout_s=0
    )
    assert result["sent"] is True
    assert result["decision"] == "reject"
    assert result["note"] is None


def test_telegram_approval_scopes_callback_and_answers_query(server_mod, monkeypatch):
    # T2: scoped callback_data, stale-replay discard, spinner ack.
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    monkeypatch.setenv("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "10")
    telegram = sys.modules["telegram"]

    # A stale press from an older gate sits in the queue before the new send.
    queue = [_approval_update(3, 12345, "approve:100:OLD")]
    calls = []
    transport = _queue_transport(queue, calls)

    keyboard = telegram._approval_keyboard(175, "QA")
    buttons = keyboard["inline_keyboard"][0]
    assert buttons[0]["callback_data"] == "approve:175:QA"
    assert buttons[1]["callback_data"] == "reject:175:QA"

    # The fresh decision arrives after the gate message is posted.
    orig_fake = transport
    def staged(method, payload):
        if method == "sendMessage":
            queue.append(_approval_update(9, 12345, "approve:175:QA"))
        return orig_fake(method, payload)
    result = telegram.send_approval_request(
        175, "QA", "All green.", transport=staged, ask_note=False
    )
    # Stale approve:100:OLD (id 3) was discarded by the offset=-1 probe;
    # only the scoped approve:175:QA (id 9) resolved the gate.
    assert result["sent"] is True
    assert result["decision"] == "approve"
    assert result["update_id"] == 9
    acked = [
        p for m, p in calls
        if m == "answerCallbackQuery" and p.get("callback_query_id") == "cb-9"
    ]
    assert acked, "matching callback must be acked via answerCallbackQuery"
    # The stale callback must NOT have been acked.
    assert not [
        p for m, p in calls
        if m == "answerCallbackQuery" and p.get("callback_query_id") == "cb-3"
    ]


def test_telegram_missing_credentials_degrade(server_mod, monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    telegram = sys.modules["telegram"]
    result = telegram.send_approval_request(175, "QA", "summary")
    assert result["sent"] is False
    assert "missing" in result["reason"].lower()
    assert telegram.send_admin_question(175, "Proceed?").startswith("ERROR:")


def test_telegram_long_summary_chunked_not_truncated(server_mod, monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    monkeypatch.setenv("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "10")
    telegram = sys.modules["telegram"]
    long_summary = "X" * (telegram.MAX_TEXT_LEN + 500)
    queue = []
    calls = []
    sent_texts = []
    base = _queue_transport(queue, calls)

    def staged(method, payload):
        if method == "sendMessage":
            sent_texts.append(payload["text"])
            if len(sent_texts) == 2:  # Keyboard rides the last chunk; decide then.
                queue.append(_approval_update(11, 12345, "reject:176:closure"))
        return base(method, payload)

    result = telegram.send_approval_request(
        176, "closure", long_summary, transport=staged, ask_note=False
    )
    assert result["sent"] is True
    assert result["decision"] == "reject"
    # Chunked delivery: every char sent, keyboard on the last message.
    assert sum(len(t) for t in sent_texts) >= len(long_summary)
    assert len(sent_texts) >= 2


def test_session_lineage_no_duplicate_instruction(sess, tmp_path):
    # T3: when the replay already ends with the instruction (the normal
    # server flow appends it to the transcript first), LiteLLM must
    # receive it exactly once.
    sess.append_turn(180, "user", "do the thing")
    messages = sess.build_persona_messages(
        180, "QA Engineer", "do the thing", None, repo_root=tmp_path
    )
    user_texts = [m["content"] for m in messages if m["role"] == "user"]
    assert user_texts.count("do the thing") == 1
    # A genuinely new instruction is still appended last.
    messages2 = sess.build_persona_messages(
        180, "QA Engineer", "do the other thing", None, repo_root=tmp_path
    )
    assert messages2[-1] == {"role": "user", "content": "do the other thing"}


def test_load_env_files_from_cwd_and_never_overrides(server_mod, tmp_path, monkeypatch):
    (tmp_path / ".env").write_text(
        "# comment\nPERSONA_TEST_PROBE=probe-value-123\n"
        "QUOTED='spaced value'\nMALFORMED-LINE\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("PERSONA_TEST_PROBE", raising=False)
    monkeypatch.delenv("QUOTED", raising=False)
    server_mod._load_env_files()
    assert os.environ.get("PERSONA_TEST_PROBE") == "probe-value-123"
    assert os.environ.get("QUOTED") == "spaced value"
    # Real process env always wins: files never override it.
    monkeypatch.setenv("PERSONA_TEST_PROBE", "keep-me")
    server_mod._load_env_files()
    assert os.environ.get("PERSONA_TEST_PROBE") == "keep-me"


def test_load_env_files_parent_fallback_without_cwd(server_mod, tmp_path, monkeypatch):
    # Regression: opencode may launch servers with a cwd that holds no .env
    # (this exact gap caused the post-restart 401). The file next to the
    # install root (<server-dir>/../.env) must still be found.
    fake_root = tmp_path / "install"
    fake_server = fake_root / "mcp-persona-server"
    fake_server.mkdir(parents=True)
    (fake_root / ".env").write_text("PERSONA_PARENT_PROBE=from-parent\n", encoding="utf-8")
    empty_cwd = tmp_path / "elsewhere"
    empty_cwd.mkdir()
    monkeypatch.chdir(empty_cwd)
    monkeypatch.delenv("PERSONA_PARENT_PROBE", raising=False)
    loaded = server_mod._load_env_files(server_dir=fake_server)
    assert loaded is not None and loaded.endswith(".env")
    assert os.environ.get("PERSONA_PARENT_PROBE") == "from-parent"


def test_load_env_files_empty_env_loses_to_file(server_mod, tmp_path, monkeypatch):
    # Regression: OpenCode {env:} blocks inject EMPTY strings when the parent
    # env lacks the var — those must not shadow real file values (the 401).
    (tmp_path / ".env").write_text("PERSONA_EMPTY_PROBE=file-value\n", encoding="utf-8")
    empty_cwd = tmp_path / "empty"
    empty_cwd.mkdir()
    monkeypatch.chdir(empty_cwd)
    monkeypatch.setenv("PERSONA_EMPTY_PROBE", "")
    server_mod._load_env_files(server_dir=tmp_path)
    assert os.environ.get("PERSONA_EMPTY_PROBE") == "file-value"


def test_dispatch_task_file_not_duplicated_in_transcript(server_mod, tmp_path, monkeypatch):
    # Regression: dispatch must NOT append full task bodies to the transcript
    # (unbounded growth → 1.5M-token requests → endpoint 400s). The body goes
    # to the LLM messages once; the transcript keeps the instruction only.
    # NOTE: server.py binds the top-level `session` module (== mcp-persona-server
    # via sys.path), so patch SESSIONS_ROOT on THAT object, not the fixture's.
    import session as real_session

    monkeypatch.setitem(
        sys.modules, "litellm",
        _stub_litellm("All checks pass. No blocking findings."),
    )
    monkeypatch.setattr(real_session, "SESSIONS_ROOT", tmp_path / "sessions")
    task_file = tmp_path / "task-171.md"
    task_file.write_text("# Task 171\n\n" + "BODY-LINE\n" * 200, encoding="utf-8")
    call = server_mod.dispatch_session_turn
    target = call.fn if hasattr(call, "fn") else call
    result = target(177, "QA Engineer", "review this", task_file_path=str(task_file))
    assert result["status"] == "REPORT"
    turns = real_session.read_transcript(177)
    assert len(turns) == 2  # instruction + assistant reply, nothing else
    assert turns[0]["content"] == "review this"
    assert "BODY-LINE" not in turns[0]["content"]


def test_env_loader_bom_crlf_and_literal_hash(server_mod, tmp_path, monkeypatch):
    # BOM stripped; CRLF tolerated; inline '#' stays literal (values with
    # hashes are kept whole — we never shell-split values).
    (tmp_path / ".env").write_bytes(
        '﻿BOM_KEY=bom-value\r\nCRLF_KEY=crlf-value\r\nHASH_KEY=abc#def\n'.encode("utf-8")
    )
    empty_cwd = tmp_path / "empty"
    empty_cwd.mkdir()
    monkeypatch.chdir(empty_cwd)
    for var in ("BOM_KEY", "CRLF_KEY", "HASH_KEY"):
        monkeypatch.delenv(var, raising=False)
    server_mod._load_env_files(server_dir=tmp_path)
    assert os.environ.get("BOM_KEY") == "bom-value"
    assert os.environ.get("CRLF_KEY") == "crlf-value"
    assert os.environ.get("HASH_KEY") == "abc#def"


def test_tool_docstrings_carry_when_to_call(server_mod):
    # F8 guard: every MCP tool description must tell OpenCode when to call it,
    # or the triggers degrade silently with each edit.
    tools = [
        server_mod.dispatch_session_turn, server_mod.get_session_summary,
        server_mod.escalate_to_admin, server_mod.request_admin_approval,
    ]
    for tool in tools:
        fn = tool.fn if hasattr(tool, "fn") else tool
        assert "WHEN TO CALL" in (fn.__doc__ or ""), getattr(fn, "__name__", tool)


def test_telegram_empty_note_resolves_none(server_mod, monkeypatch):
    # Empty-string replies are not notes (whitespace-only included).
    telegram = sys.modules["telegram"]
    assert telegram._extract_answer({"message": {"chat": {"id": 1}, "text": "   "}}).strip() == ""


def test_env_loader_export_spaced_equals_unclosed_quote(server_mod, tmp_path, monkeypatch):
    # B7 coverage: export prefix, whitespace around '=', unclosed quote stays literal.
    (tmp_path / ".env").write_text(
        'export EXPORTED=exported-value\nSPACED = spaced-value\nUNCLOSED="oops\n',
        encoding="utf-8",
    )
    empty_cwd = tmp_path / "empty2"
    empty_cwd.mkdir()
    monkeypatch.chdir(empty_cwd)
    for var in ("EXPORTED", "SPACED", "UNCLOSED"):
        monkeypatch.delenv(var, raising=False)
    server_mod._load_env_files(server_dir=tmp_path)
    assert os.environ.get("EXPORTED") == "exported-value"
    assert os.environ.get("SPACED") == "spaced-value"
    assert os.environ.get("UNCLOSED") == '"oops'  # Unclosed: literal, deterministic.


def test_telegram_explicit_skip_resolves_none(server_mod, monkeypatch):
    # /skip is an explicit no-note (same None outcome as silence, by design —
    # the note is garnish; the decision is the gate).
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    monkeypatch.setenv("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "10")
    queue = []
    calls = []
    base = _queue_transport(queue, calls)
    sends = []

    def staged(method, payload):
        if method == "sendMessage":
            sends.append(payload)
            if len(sends) == 1:
                queue.append(_approval_update(7, 12345, "reject:175:QA"))
            elif len(sends) == 2:
                queue.append({
                    "update_id": 8,
                    "message": {"chat": {"id": 12345}, "text": "/skip"},
                })
        return base(method, payload)

    telegram = sys.modules["telegram"]
    result = telegram.send_approval_request(175, "QA", "All green.", transport=staged)
    assert result["sent"] is True
    assert result["decision"] == "reject"
    assert result["note"] is None
