"""
QA Loop Engine v2 — evidence-bound review with trace sanitization.

Inspired by OMO's evidence rule: no evidence = no commit.
Writes to loop-engine/evidence/<task-id>-<slug>/.
"""

import re
import time
from pathlib import Path

from models import LoopEngineConfig, TaskState
from state import StateMachine
from router import LLMRouter


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
        if "PASSED" in qa_report.upper() or "APPROVED" in qa_report.upper():
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

        if "APPROVED" in review.upper():
            result = "APPROVED"
        else:
            result = "REJECTED"

        (evidence_path / "review_result.txt").write_text(result, encoding="utf-8")
        return {"result": result, "review": review}
