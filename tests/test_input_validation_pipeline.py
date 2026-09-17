"""Input-validation pipeline and English-only gates.

Source fragments, the executor, and conventions must route every
non-English or noisy Manager input through validate, normalize,
translate, enrich, and prompt-refactor steps, and every clarification
or response must stay in simple English.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FRAGMENT_05 = REPO / "prompts" / "fragments" / "05-user_input_processing.md"
FRAGMENT_13 = REPO / "prompts" / "fragments" / "13-constraints.md"
EXECUTOR = REPO / "agents" / "cognitive-executor.md"
CONVENTIONS = REPO / "docs" / "conventions.md"
AGENTS = REPO / "AGENTS.md"


def _read(path):
    return path.read_text(encoding="utf-8")


def test_no_manager_language_rule_in_fragments():
    for path in (FRAGMENT_05, CONVENTIONS, AGENTS, EXECUTOR):
        text = _read(path)
        assert "in the Manager's language" not in text, path
        assert "Manager's own language or English" not in text, path


def test_english_only_clarification_required():
    text_05 = _read(FRAGMENT_05)
    assert "clarification request in simple English" in text_05
    text_conv = _read(CONVENTIONS)
    assert "simple English" in text_conv


def test_validation_runs_before_topic_shift():
    text = _read(FRAGMENT_05)
    validation = text.index("Input Validation Gate")
    topic_shift = text.index("Topic Shift Detection")
    assert validation < topic_shift


def test_pipeline_stage_order_in_fragment():
    text = _read(FRAGMENT_05)
    stages = [
        "Input Validation Gate",
        "Voice-to-Text Normalization",
        "Bilingual Translation",
        "Intent Expansion",
        "Prompt Refactor Gate",
    ]
    positions = [text.index(stage) for stage in stages]
    assert positions == sorted(positions), positions


def test_prompt_refactor_in_executor_matrix():
    text = _read(EXECUTOR)
    assert "prompt-refactor" in text


def test_executor_clarification_stays_english():
    text = _read(EXECUTOR)
    assert "Never answer the Manager in another language" in text
