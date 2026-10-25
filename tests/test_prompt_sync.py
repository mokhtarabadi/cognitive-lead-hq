# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
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
TASKGEN_SKILL = REPO / "skill-templates" / "task-generator" / "SKILL.md"


def _read(path):
    return path.read_text(encoding="utf-8")


def test_rtk_mandate_in_shipped_prompt():
    text = _read(SHIPPED)
    assert "CRITICAL RULE 3b (Token trimming)" in text
    assert "rtk test" in text
    assert "never collapse failing output" in text


def test_shipped_version_matches_fragment():
    shipped = re.search(
        r"<system_version>(.*?)</system_version>", _read(SHIPPED)
    ).group(1)
    source = re.search(
        r"<system_version>(.*?)</system_version>", _read(FRAGMENT_01)
    ).group(1)
    assert shipped == source


def test_shipped_version_is_expected_minor_bump():
    shipped = re.search(
        r"<system_version>(.*?)</system_version>", _read(SHIPPED)
    ).group(1)
    assert shipped == "9.67.0"


def test_executor_carries_compaction_guidance():
    text = _read(EXECUTOR)
    assert "compaction" in text.lower()
    assert "smart-compact" in text


def test_shipped_prompt_is_plugin_blind():
    """The system prompt carries no plugin knowledge (separation).

    The Brain stays plugin-blind and only emits a plan and checklist; every
    plugin lane lives in the context executor. No tool name, plugin name,
    state path, or channel tag may leak into the assembled artifact.
    """
    text = _read(SHIPPED)
    for literal in (
        "goal_set",
        "goal_block",
        "goal_evidence",
        "goal_complete",
        "goal_resume",
        "todowrite",
        "todoread",
        "compact_context",
        "read_omitted_content",
        "keepTurns",
        "plugin_directives",
        "smart-compact",
        "magic-compact",
        "tool_channel",
        "goal-state.json",
        "goal-evidence.json",
        ".opencode/STOP_GOAL",
        "<compaction_protocol>",
        "src/loop.ts:458-492",
        "src/loop.ts:552-853",
    ):
        assert literal not in text, f"plugin leak in shipped prompt: {literal}"
    # The Brain-side vocabulary that remains: plan, checklist, micro-list.
    assert "micro-list" in text
    assert "MICRO-TASK CHECKLIST" in text


def test_no_manager_language_rule_in_shipped_prompt():
    text = _read(SHIPPED)
    assert "in the Manager's language" not in text
    assert "Manager's own language or English" not in text
    assert "clarification request in the per-message requested language" in text


def test_approval_literals_match_english_only():
    text = _read(SHIPPED)
    assert "Never translate-then-compare" in text
    assert "Approval Literals Guard" in text


def test_assembler_output_matches_shipped(tmp_path):
    out = tmp_path / "check.md"
    proc = subprocess.run(
        [sys.executable, str(ASSEMBLER), "--output", str(out)],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
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


def test_handoff_contract_requires_complete_code_samples():
    text = _read(SHIPPED)
    assert "complete code sample or unified diff" in text
    assert "PLACEHOLDER BAN" in text


def test_handoff_contract_forbids_placeholder_only_instructions():
    text = _read(SHIPPED)
    assert "placeholder-only instructions" in text
    assert "omitted code are forbidden" in text


def test_code_block_ban_removed_from_shipped_prompt():
    text = _read(SHIPPED)
    assert "Do NOT paste full code blocks for the Hands to copy" not in text


def test_executor_owns_all_three_plugin_lanes():
    """The context executor must carry every plugin lane, not the prompt.

    Goal, todolist, and smart-compact are the Hands' only tool lanes. The
    goal lane needs its create trigger (goal_set) or it never fires, so the
    tool names are pinned here alongside the corrected idle-loop citations.
    """
    text = _read(EXECUTOR)
    for literal in (
        "goal_set",
        "goal_block",
        "goal_evidence",
        "goal_complete",
        "goal_resume",
        "goal_set(title)",
        "todowrite",
        "todoread",
        "100 todos",
        "compact_context",
        "read_omitted_content",
        "keepTurns",
        ".opencode/STOP_GOAL",
        "compact_stats",
    ):
        assert literal in text, f"missing plugin-lane literal: {literal}"


def test_executor_has_no_code_references():
    """The context executor is a prompt for the LLM, not an audit trail.

    File and line citations belong in task files, DECISIONS records, and the
    CHANGELOG — never in the instructions the agent reads every turn. The
    lane behavior (tools, triggers, error strings) stays; the pointers go.
    """
    text = _read(EXECUTOR)
    for literal in (
        "src/loop.ts",
        "src/index.ts",
        "src/goal.ts",
        "src/tools.ts",
        "src/state.ts",
        "src/verifier.ts",
        "src/evidence.ts",
        "server.py",
        "205-437",
        "no Brain mention is added",
    ):
        assert literal not in text, f"code reference in executor: {literal}"
    assert "goal_set" in text
    assert ".opencode/STOP_GOAL" in text
