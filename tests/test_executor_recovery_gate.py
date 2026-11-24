# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Mandatory omitted-output recovery gate in the executor (Task 423)."""

from pathlib import Path

EXECUTOR = Path(__file__).resolve().parent.parent / "agents" / "cognitive-executor.md"

REQUIRED = [
    "## Omitted-Output Recovery Gate (mandatory)",
    "Never act on important omitted output before recovery",
    'tools.read_omitted_content({contentId: "omitted-0001"})',
    "capped at 20,000 characters",
    "possibly stale",
    "re-run the source tool once",
    "Smart Compact omission notice (`omitted-NNNN`)",
    "Code Mode truncated return (`truncated: true`",
    "Brain oversized-turn stub (`[brain-output]` pointer with `output_address`)",
    "Bounded-retry rule: at most two recovery attempts",
    "never assume the tail",
]


def test_recovery_gate_text():
    text = EXECUTOR.read_text(encoding="utf-8")
    for token in REQUIRED:
        assert token in text, f"recovery contract text missing: {token}"


def test_gate_is_cross_referenced_from_compaction_and_codemode():
    text = EXECUTOR.read_text(encoding="utf-8")
    assert text.count("Omitted-Output Recovery Gate") >= 3, (
        "gate must be named once plus referenced from the compaction and code-mode sections"
    )


def test_three_paths_stay_distinct():
    text = EXECUTOR.read_text(encoding="utf-8")
    gate_start = text.index("## Omitted-Output Recovery Gate")
    gate = text[
        gate_start : text.index("## Capability Preflight (session start)", gate_start)
    ]
    for ordered in (
        "1. Smart Compact omission notice",
        "2. Code Mode truncated return",
        "3. Brain oversized-turn stub",
    ):
        assert ordered in gate, f"numbered route missing: {ordered}"
