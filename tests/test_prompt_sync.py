"""Shipped-prompt content gates (Task 241 Gap 4).

The rtk mandate must survive in the assembled system prompt, the shipped
version must match the fragment source, and the assembler output must
equal the committed file (same contract as lint_system_prompt_sync).
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHIPPED = REPO / "system-prompt.md"
FRAGMENT_01 = REPO / "prompts" / "fragments" / "01-system_version.md"
ASSEMBLER = REPO / "scripts" / "prompt-build" / "assemble_system_prompt.py"
EXECUTOR = REPO / "agents" / "cognitive-executor.md"
TASKGEN_SKILL = (REPO / "skill-templates" / "task-generator" / "SKILL.md")


def _read(path):
    return path.read_text(encoding="utf-8")


def test_rtk_mandate_in_shipped_prompt():
    text = _read(SHIPPED)
    assert "CRITICAL RULE 3b (Token trimming)" in text
    assert "rtk test" in text
    assert "never collapse failing output" in text


def test_shipped_version_matches_fragment():
    shipped = re.search(r"<system_version>(.*?)</system_version>",
                        _read(SHIPPED)).group(1)
    source = re.search(r"<system_version>(.*?)</system_version>",
                       _read(FRAGMENT_01)).group(1)
    assert shipped == source


def test_shipped_version_is_expected_minor_bump():
    shipped = re.search(r"<system_version>(.*?)</system_version>",
                        _read(SHIPPED)).group(1)
    assert shipped == "9.41.0"


def test_no_manager_language_rule_in_shipped_prompt():
    text = _read(SHIPPED)
    assert "in the Manager's language" not in text
    assert "Manager's own language or English" not in text
    assert "clarification request in simple English" in text


def test_assembler_output_matches_shipped(tmp_path):
    out = tmp_path / "check.md"
    proc = subprocess.run(
        [sys.executable, str(ASSEMBLER), "--output", str(out)],
        capture_output=True, text=True, cwd=str(REPO))
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert out.read_text(encoding="utf-8") == _read(SHIPPED)


def test_executor_names_rtk_default_runner():
    text = _read(EXECUTOR)
    assert "rtk test" in text
    assert "default" in text.lower()
    assert "first" in text.lower()


def test_executor_evidence_records_rtk_command():
    text = _read(EXECUTOR)
    assert "Verification Evidence" in text
    assert "rtk test" in text


def test_task_generator_template_prescribes_rtk():
    text = _read(TASKGEN_SKILL)
    assert "rtk test [exact command]" in text
