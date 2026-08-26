"""Characterization tests for Task 114 pre-production audit fixes.

Covers:
- daemon.strip_jsonc: quote-aware comment stripping (URLs survive), trailing
  commas, ${VAR} env resolution
- qa_engine.decide: first-occurrence verdict logic
- gateway.ApprovalGateway.handle_callback: approve / reject / stale flows
- QAEngine.run_qa with a stubbed router: verdict + qa_retry_count increment
"""
import asyncio
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from models import LoopEngineConfig


# --- strip_jsonc ---

def test_strip_jsonc_preserves_urls():
    from daemon import strip_jsonc
    raw = '{\n  // comment\n  "url": "https://api.example.com/v1"\n}'
    assert "https://api.example.com/v1" in strip_jsonc(raw)


def test_strip_jsonc_trailing_commas_and_comments():
    from daemon import strip_jsonc
    raw = '{\n  /* block */ "a": 1,\n  // line\n  "b": 2,\n}'
    import json
    assert json.loads(strip_jsonc(raw)) == {"a": 1, "b": 2}


def test_strip_jsonc_env_resolution(monkeypatch=None):
    from daemon import strip_jsonc
    os.environ["AUDIT_TEST_VAR"] = "resolved"
    raw = '{"k": "${AUDIT_TEST_VAR}"}'
    assert strip_jsonc(raw) == '{"k": "resolved"}'
    del os.environ["AUDIT_TEST_VAR"]


def test_load_config_from_repo_root():
    """Config loads regardless of CWD (repo-root anchoring fix)."""
    from daemon import load_config
    cfg = load_config()
    assert cfg.approval.chat_id == 0  # placeholder in committed jsonc
    assert "quick" in cfg.categories


# --- decide() ---

def test_decide_failed_report_quoting_pass_is_not_positive():
    """Regression: FAILED report that mentions 'tests must pass' must stay FAILED."""
    from qa_engine import decide
    report = ("FAILED: acceptance criterion says tests must be APPROVED, "
              "but the build is broken.")
    assert decide(report) == "FAIL"


def test_decide_pass_first_wins():
    from qa_engine import decide
    assert decide("PASSED. All criteria met. Nothing REJECTED.") == "PASS"


def test_decide_fail_first_wins():
    from qa_engine import decide
    assert decide("REJECTED after initial PASSED-looking noise.") == "FAIL"


def test_decide_no_verdict_defaults_to_fail():
    from qa_engine import decide
    assert decide("The build produced no clear verdict.") == "FAIL"


# --- gateway handle_callback ---

def _gateway_with_pending(key):
    from gateway import ApprovalGateway
    gw = ApprovalGateway(LoopEngineConfig(approval={"chat_id": 1}))
    gw.pending[key] = asyncio.Event()
    gw.results[key] = False
    return gw


def test_handle_callback_approve():
    gw = _gateway_with_pending("7:Plan Approval")
    ack = gw.handle_callback("approve:7:Plan Approval")
    assert ack is not None
    assert gw.results["7:Plan Approval"] is True


def test_handle_callback_reject():
    gw = _gateway_with_pending("7:Plan Approval")
    ack = gw.handle_callback("reject:7:Plan Approval")
    assert ack is not None
    assert gw.results["7:Plan Approval"] is False


def test_handle_callback_stale_returns_none():
    from gateway import ApprovalGateway
    gw = ApprovalGateway(LoopEngineConfig(approval={"chat_id": 1}))
    assert gw.handle_callback("approve:999:Plan Approval") is None
    assert gw.handle_callback("nonsense") is None


# --- QAEngine with stubbed router ---

class _StubRouter:
    def __init__(self, report):
        self.report = report
        self.called = False

    def route_qa(self, task_content, diff=""):
        return {}

    def route_review(self, task_content, qa_report=""):
        return {}

    def call_llm(self, routing):
        self.called = True
        return self.report


def _qa_engine(report):
    from qa_engine import QAEngine
    from state import StateMachine
    tmp = tempfile.TemporaryDirectory()
    sm = StateMachine(os.path.join(tmp.name, "t.db"))
    cfg = LoopEngineConfig(approval={"chat_id": 1},
                           evidence_dir=os.path.join(tmp.name, "evidence"))
    stub = _StubRouter(report)
    return QAEngine(cfg, sm, stub), sm, tmp


def test_run_qa_failed_increments_retry_counter():
    qa, sm, tmp = _qa_engine(
        "FAILED: edge case unhandled — criteria mention APPROVED output only.")
    tid = sm.register_task("tasks/backlog/42-audit.md")  # pipeline registers before QA
    result = qa.run_qa(tid, "task content", "diff")
    assert result["result"] == "FAILED"
    assert sm.get_qa_retry_count(tid) == 1
    sm.close()
    tmp.cleanup()


def test_run_qa_passed_does_not_increment():
    qa, sm, tmp = _qa_engine("PASSED. All acceptance criteria verified.")
    tid = sm.register_task("tasks/backlog/43-audit.md")
    result = qa.run_qa(tid, "task content", "diff")
    assert result["result"] == "PASSED"
    assert sm.get_qa_retry_count(tid) == 0
    sm.close()
    tmp.cleanup()


def test_run_review_rejected_on_ambiguous_report():
    qa, sm, tmp = _qa_engine("")
    tid = sm.register_task("tasks/backlog/44-audit.md")
    result = qa.run_review(tid, "task content",
                           "QA report says PASSED but review finds NEEDS_WORK.")
    assert result["result"] == "REJECTED"
    sm.close()
    tmp.cleanup()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
