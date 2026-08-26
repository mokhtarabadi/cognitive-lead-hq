"""
QA Loop Engine v2 — evidence-bound review with trace sanitization.

Inspired by OMO's evidence rule: no evidence = no commit.
Writes to loop-engine/evidence/<task-id>/.
"""

import re
import time
from pathlib import Path

from models import LoopEngineConfig, TaskState
from state import StateMachine
from router import LLMRouter

# Decision tokens — aligned with the Manager's persona definitions
# (12-personas.md): QA Engineer emits QA_PASSED/QA_REJECTED, Code Reviewer
# emits APPROVED/APPROVED_WITH_CHANGES/REJECTED_NEEDS_FIXES/PO_REVIEW_PENDING.
# Engine shorthand (PASSED/FAILED/READY_FOR_CLOSURE/NEEDS_WORK) stays accepted.
# First occurrence in the report wins: naive substring matching false-positives
# when a FAILED report quotes acceptance criteria like "tests must be approved".
_PASS_RE = re.compile(
    r"\b(QA_PASSED|PASSED|APPROVED_WITH_CHANGES|APPROVED|PO_REVIEW_PENDING|READY_FOR_CLOSURE)\b")
_FAIL_RE = re.compile(
    r"\b(QA_REJECTED|REJECTED_NEEDS_FIXES|FAILED|REJECTED|NEEDS_WORK)\b")


def decide(report: str, default: str = "FAIL") -> str:
    """Return PASS-side or FAIL-side verdict based on first match in report."""
    p = _PASS_RE.search(report.upper())
    f = _FAIL_RE.search(report.upper())
    if p and (not f or p.start() < f.start()):
        return "PASS"
    if f:
        return "FAIL"
    return default


class QAEngine:
    """Runs QA and Code Review via LLM, writes evidence."""

    def __init__(self, config: LoopEngineConfig, state: StateMachine, router: LLMRouter):
        self.config = config
        self.state = state
        self.router = router
        self.evidence_dir = Path(config.evidence_dir)

    def run_qa(self, task_id: int, task_content: str, diff: str = "") -> dict:
        """Run QA Engineer review. Returns PASSED or FAILED."""
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        evidence_path = self.evidence_dir / f"{task_id}"
        evidence_path.mkdir(exist_ok=True)

        routing = self.router.route_qa(task_content, diff)
        qa_report = self.router.call_llm(routing)

        # Write evidence
        (evidence_path / "qa_report.md").write_text(qa_report, encoding="utf-8")

        # Determine result
        if decide(qa_report) == "PASS":
            result = "PASSED"
        else:
            result = "FAILED"
            self.state.set_qa_feedback(task_id, qa_report)

        (evidence_path / "result.txt").write_text(result, encoding="utf-8")
        return {"result": result, "report": qa_report, "evidence_dir": str(evidence_path)}

    def run_review(self, task_id: int, task_content: str, qa_report: str = "") -> dict:
        """Run Code Reviewer. Returns APPROVED or REJECTED."""
        evidence_path = self.evidence_dir / f"{task_id}"
        evidence_path.mkdir(parents=True, exist_ok=True)

        routing = self.router.route_review(task_content, qa_report)
        review = self.router.call_llm(routing)

        (evidence_path / "review.md").write_text(review, encoding="utf-8")

        if decide(review) == "PASS":
            result = "APPROVED"
        else:
            result = "REJECTED"

        (evidence_path / "review_result.txt").write_text(result, encoding="utf-8")
        return {"result": result, "review": review}
