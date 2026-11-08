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
DISCOVERY = REPO / "agents" / "cognitive-discovery.md"
FRAGMENT_09 = REPO / "prompts" / "fragments" / "09-hands_protocols.md"
ROOT_AGENTS = REPO / "AGENTS.md"
TASKGEN_SKILL = REPO / "skill-templates" / "task-generator" / "SKILL.md"


def _read(path):
    return path.read_text(encoding="utf-8")


def test_rtk_mandate_in_executor():
    text = _read(EXECUTOR)
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
    assert shipped == "9.76.0"


def test_shipped_prompt_documents_context_path_line_ranges():
    """The shipped prompt must name the #L slice forms, not just narrowing.

    Regression (META 377 QA round): the parser accepted `path#Lstart-end`
    and `path#Lstart-` but the No-Hallucination contract only said "name a
    smaller path", so the Brain was never told the slice syntax exists.
    """
    shipped = _read(SHIPPED)
    assert "path#Lstart-end" in shipped
    assert "path#Lstart-" in shipped


def test_shipped_prompt_bans_rerequesting_unavailable_paths():
    """An [unavailable] label must end the loop, not restart it.

    Regression (1046-loop): `.env.example` is not injectable (unlisted
    suffix, pre-sniff). The bridge labeled it `[unavailable: ...
    unsupported extension]` twice and the model re-requested the same
    path twice — the contract only banned re-requesting *visible*
    content, never uninjectable paths.
    """
    shipped = _read(SHIPPED)
    assert "never re-request the same path" in shipped
    assert "[unavailable: ...]" in shipped


def test_parallel_mandate_covers_implementation_triggers():
    """The mandate must name implementation/R&D triggers, not discovery only.

    Regression: the mandate fired only on file scans and signature
    extraction, leaving R&D and implementation splits to guesswork.
    """
    text = _read(SHIPPED)
    assert "Implementation & R&D triggers" in text
    assert "Disjoint ownership" in text
    assert "Verify-and-merge" in text


def test_shipped_prompt_names_only_catalog_tools():
    """The shipped prompt must not name tools outside the session toolset.

    Regression (night sweep): fragments named `nodejs-express` (no such
    skill), `@explore`/`@general` (no such subagents), and `view_file` /
    `apply_patch` (no such native tools). The Hands cannot call what does
    not exist, so phantom names are a hard failure, not style.
    """
    text = _read(SHIPPED)
    for phantom in (
        "nodejs-express",
        "@explore",
        "@general",
        "view_file",
        "apply_patch",
    ):
        assert phantom not in text, f"phantom tool name in shipped prompt: {phantom}"
    assert "node-hexagonal-api" in text
    assert "cognitive-discovery" in text


def test_executor_carries_compaction_guidance():
    text = _read(EXECUTOR)
    assert "compaction" in text.lower()
    assert "smart-compact" in text


def test_executor_never_trims_brain_results():
    """A brain_turn result is evidence: the Hands returns it whole, always.

    Regression: the executor told the Hands to return
    ``{status, block_count, model}``, which dropped ``output`` and
    ``xml_blocks`` from the transcript and from the next turn.
    """
    text = _read(EXECUTOR)
    assert "return the whole" in text.lower()
    assert "payload" in text.lower()
    assert "field-shape" in text
    assert "exactly as received" in text
    assert "summarize `output` only after" not in text
    assert "range through the tool again" in text
    assert "block_count" not in text


def test_executor_shows_plan_before_asking_for_approval():
    """A plan-approval ask is invalid without the plan visible to the Manager.

    Regression: the executor told the Hands that in autopilot the Manager
    sees only Relay questions, and to collect plan approval with one narrow
    question, so the approval card arrived with no plan body to approve.
    """
    text = _read(EXECUTOR)
    assert "Plan presentation contract" in text
    assert "before calling `question`" in text
    assert "The `question` body carries the same" in text
    assert "carries the full plan text" in text
    assert "is a plan, not a verdict" in text
    assert "sees the full plan at the approval" in text
    assert "bare ask is a protocol bug" in text
    assert "Revision rounds keep the contract" in text
    assert "sees only Relay questions" not in text


def test_executor_fed_context_requires_verbatim_or_paths():
    """A discovery-fed retry without bodies starves the Brain by contract.

    Regression: the executor told the Hands to feed discovery back as a
    prose `[fed-context]` block. Prose-about-code cannot satisfy the
    Brain's No-Hallucination + Strict Grounding rules, so the retry
    correctly returns a second `missing_context` and the loop stalls.
    """
    text = _read(EXECUTOR)
    normalized_text = " ".join(text.split())
    assert "prose-only `[fed-context]` is a protocol violation" in normalized_text
    assert (
        "The fed retry MUST carry verbatim code (capped ranges, pasted inline) "
        "and/or pass `context_paths=[paths]` on the `brain_turn` call"
    ) in normalized_text
    assert (
        "**Mirror of the Discovery-fed grounding rule:** paste the ranges verbatim "
        "(capped) and/or pass the same paths via `context_paths`"
    ) in normalized_text
    assert (
        "A retry that carries only summaries predicts its own second `missing_context`"
    ) in normalized_text


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


def _read_shipped_prompt_for_approval_contract() -> str:
    """Read the generated prompt that defines the runtime approval contract."""
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    return (project_root / "system-prompt.md").read_text(encoding="utf-8")


def test_closure_question_tool_envelope_acceptance_is_pinned():
    prompt = _read_shipped_prompt_for_approval_contract()

    assert (
        "either exact phrase as the answer value in an unmodified question-tool result"
        in prompt
    )
    assert 'User has answered your questions: "<question>"="<answer>"' in prompt
    assert "immediately preceding relayed closure-approval question" in prompt
    assert "Compare only the answer value, not the quoted question/header" in prompt
    assert "do not require the approval phrase to be the entire Hands message" in prompt
    assert 'The existing bare "approved" exception remains limited' in prompt


def test_closure_approval_keeps_existing_negative_cases():
    """Prevent envelope support from broadening unrelated closure approvals.

    Deviation D1 from the QA-prescribed test: the QA hotfix listed the
    pre-0381 sentence 'A bare "approved" counts only when ... anywhere else
    never counts', but the approved plan replaced that sentence with the
    'remains limited' formulation (direct answer + question-tool answer
    value), already pinned above. Re-adding the removed sentence would be a
    prompt change, which the hotfix forbids — so this pins the negative
    cases exactly as shipped.
    """
    prompt = _read_shipped_prompt_for_approval_contract()

    preserved_contract = (
        'These never count: "good", "thanks", "ok", "okay", "yes", "done", '
        '"fine", "looks good", emoji-only replies, silence, or any autopilot self-decision.',
        "Blanket acknowledgements never count at any gate.",
        (
            'The existing bare "approved" exception remains limited to the '
            "Manager's direct answer to that immediately preceding "
            "closure-approval question, including the exact answer value "
            '"approved" in its question-tool result.'
        ),
    )

    for contract in preserved_contract:
        assert contract in prompt


def test_executor_capability_preflight_matches_closure_answer_contract():
    """Keep startup approval guidance aligned with the operational closure relay.

    Deviation D2 from the reviewer-prescribed test: it called
    `_read("agents/cognitive-executor.md")` with a str, but `_read` needs a
    Path — so this uses the existing EXECUTOR constant instead. Same
    assertions otherwise.
    """
    executor = _read(EXECUTOR)
    capability_preflight = executor.split("## Capability Preflight (session start)", 1)[
        1
    ].split("## Subagent Delegation for Context Discovery", 1)[0]

    assert (
        "either exact phrase as the answer value in an unmodified question-tool result"
        in capability_preflight
    )
    assert (
        "Compare only the answer value, not the quoted question/header"
        in capability_preflight
    )
    assert (
        'The existing bare "approved" exception remains limited to the Manager\'s direct answer'
        in capability_preflight
    )
    assert (
        'including the exact answer value "approved" in its question-tool result'
        in capability_preflight
    )
    assert 'a bare "approved" never counts' not in capability_preflight


def test_executor_review_relay_accepts_closure_answer_envelope():
    """Keep the operational review relay aligned with closure approval rules."""
    executor = _read(EXECUTOR)
    review_relay = executor.split("### Review-approval relay (manual mode)", 1)[
        1
    ].split("### Autopilot mode", 1)[0]

    assert (
        'Accept ONLY the exact standalone Manager answers "Approved for closure" or "Close task"'
        in review_relay
    )
    assert (
        "or either exact phrase as the answer value in an unmodified question-tool result"
        in review_relay
    )
    assert '`User has answered your questions: "<question>"="<answer>"`' in review_relay
    assert (
        "when that result answers the immediately preceding relayed closure-approval question"
        in review_relay
    )
    assert (
        "Compare only the answer value, not the quoted question/header" in review_relay
    )
    assert (
        "do not require the approval phrase to be the entire Hands message"
        in review_relay
    )
    assert (
        'The existing bare "approved" exception remains limited to the Manager\'s direct answer'
        in review_relay
    )


def test_executor_contains_full_dto_mandate():
    """The full No-Manual-DTO mandate lives in the executor, not the prompt."""
    executor = _read(EXECUTOR)
    assert "No-Manual-DTO Mandate (full rule text, owned by Hands)" in executor
    assert "Hand-written duplicates create silent type drift" in executor
    assert "If NO source-of-truth contract exists" in executor
    assert "Type Drift Sentinel" in executor
    conventions = (REPO / "docs" / "conventions.md").read_text(encoding="utf-8")
    assert "agents/cognitive-executor.md" in conventions
    assert (
        "system-prompt.md"
        not in conventions.split("No-Manual-DTO", 1)[1].split("##", 1)[0]
    )
    executor = (REPO / "agents" / "cognitive-executor.md").read_text(encoding="utf-8")

    assert (
        "complete result envelope verbatim in a clearly labeled "
        "`Question-tool answer (verbatim)` block" in executor
    )
    assert (
        "Do not paraphrase, summarize, normalize, truncate, or strip the envelope"
        in executor
    )
    assert (
        "Keep the required mode line, full active task context, and the Brain "
        "instruction outside the unchanged block" in executor
    )


def test_shipped_prompt_version_is_9_76_0():
    prompt = _read_shipped_prompt_for_approval_contract()
    assert "9.76.0" in prompt


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


def test_executor_manual_implementation_review_chain_is_explicit():
    """Manual implementation handoffs must explicitly chain QA/review."""
    executor = _read(EXECUTOR)
    manual = executor.split("## Manual Workflow (Active Default)", 1)[1].split(
        "## Code Mode Tool Calling Protocol", 1
    )[0]

    assert "Mandatory manual review chain" in manual
    assert "same `task_id` and `session_id`" in manual
    assert "`include_diff=True`" in manual
    assert "logic, backend, or state changes" in manual
    assert "`[QA Engineer]`" in manual
    assert "documentation, CSS, or trivial changes" in manual
    assert "`[Code Reviewer]`" in manual
    assert "After `QA_PASSED`" in manual
    assert "Do not claim QA/review was chained" in manual


def test_executor_owns_shell_precommit_docs_syntax_discipline():
    """Hands-only shell/pre-commit/docs/syntax rules live in the executor."""
    executor = _read(EXECUTOR)
    assert "Shell, Pre-commit, Documentation & Syntax Discipline" in executor
    assert "non-interactive only" in executor
    assert "registry authentication" in executor
    assert "token scope validation" in executor
    assert "network access" in executor
    assert "maximum docstrings" in executor
    assert "inline comments on non-obvious logic" in executor
    assert "Verify types and syntax with the language/type-check tooling" in executor
    assert "Terminal output over 2000 lines or 50KB is truncated" in executor
    assert "pipe through grep or tail" in executor
    assert "maximum of 3 repair attempts" in executor
    assert "detailing the exact errors for the Manager" in executor


def test_executor_rule_validation_and_git_restriction():
    """Rule validation covers skill files; other Git cmds need listing."""
    executor = _read(EXECUTOR)
    assert (
        "cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files"
        in executor
    )
    assert "run no bash commands before validation passes" in executor
    assert (
        "You may ONLY run other Git commands if they are explicitly listed" in executor
    )
    assert "never run destructive Git operations" in executor


def test_executor_frontmatter_denies_checkout():
    """Permission layer denies git checkout*, matching the ZAC claim."""
    executor = _read(EXECUTOR)
    assert '"git checkout*": "deny"' in executor


def test_executor_verification_gate_and_documentation_rule():
    """CRITICAL GATE FUNCTION and full documentation rule live in executor."""
    executor = _read(EXECUTOR)
    assert "CRITICAL GATE FUNCTION" in executor
    assert "verification-before-completion" in executor
    assert "architectural notes" in executor
    assert "what you changed, and why" in executor
    assert "MUST be written in English" in executor
    assert "Check off any local TODOs" in executor
    assert "NEVER write task numbers into prompt-facing Markdown" in executor
    assert "Living Folder Docs Sync" in executor


def test_executor_names_rtk_default_runner():
    text = _read(EXECUTOR)
    assert "rtk test" in text
    assert "default" in text.lower()
    assert "first" in text.lower()


def test_executor_has_implementation_delegation_lane():
    """The executor must own an implementation-delegation lane beside discovery.

    Regression: delegation covered read-only discovery only, so parallel
    implementation splits had no ownership or verification contract.
    """
    text = _read(EXECUTOR)
    assert "Subagent Delegation for Implementation" in text
    assert "disjoint file list" in text
    assert "verify every lane" in text
    assert "`task` tool" not in text


def test_code_search_names_only_subagent_tool():
    """No stale `task`-tool reference may survive in the code-search skill."""
    text = (REPO / "skill-templates" / "code-search" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "`task`/subagent" not in text
    assert "`subagent` calls" in text


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


def test_discovery_defines_context_paths_manifest():
    """Discovery must emit one canonical machine-readable manifest.

    Regression: discovery returned prose summaries only, so the Hands fed
    prose `[fed-context]` and the Brain correctly re-emitted
    `missing_context`. The manifest binds discovery output to
    `brain_turn(context_paths=[...])`. A QA round found two competing
    formats (bullet entries vs a bracketed inline list); exactly one
    structure is canonical and the discovery summary must repeat it.
    """
    text = DISCOVERY.read_text(encoding="utf-8")
    heading = text.index("### Context Manifest")
    paths_line = text.index("Context-Paths:", heading)
    entry = text.index("- path/to/file", paths_line)
    assert heading < paths_line < entry
    assert "#Lstart-end" in text[heading : heading + 600]
    manifest_instructions = text[heading : heading + 600]
    assert (
        "Every `Context-Paths` entry MUST use a concrete `#Lstart-end` range."
        in manifest_instructions
    )
    assert "plain paths for small ones" not in text
    summary = _read(FRAGMENT_09)
    assert "### Context Manifest" in summary
    assert "Context-Paths:" in summary
    assert "- path/to/file.ext#Lstart-end" in summary
    assert "[path#Lstart-end, ...]" not in summary


def test_executor_documents_code_mode_tool_calling():
    """The executor must document Code Mode tool routing via execute."""
    text = _read(EXECUTOR)
    assert "Code Mode Tool Calling Protocol" in text
    assert "tools.<server>.<tool>" in text
    assert "tools.brain.brain_turn" in text
    assert "project_root" in text


def test_manual_handoff_assigns_brain_turn_to_hands():
    """Manual mode must not route task text through the Manager.

    Regression: manual summaries and persona behaviors told the Manager
    to copy task files and QA/review prompts between the Hands and the
    Brain, contradicting the Bridge protocol — the Hands invokes
    `brain_turn` directly in both modes and the Manager only gates
    approvals and Relay questions.
    """
    shipped = _read(SHIPPED)
    for forbidden in (
        "Please copy the entire contents of `tasks/qa/",
        "Manager ferries task files",
        "ferries task files and XML",
        "ferries task files by hand",
        "copies it to the Hands",
        "brings the result back",
        "paste the file tree and code context back",
        "pastes the Hands",
        "where to paste it",
        "hand over to the Code Reviewer",
        "copy-paste relay instructions expected",
    ):
        assert forbidden not in shipped, f"manual ferrying instruction: {forbidden}"
    assert "only gates approvals" in shipped
    impl_line = (
        '"Task implemented, reasoning logged, Git diff injected, '
        'and QA/review chained via `brain_turn`."'
    )
    combined_line = (
        '"Combined task complete: discovery verified, implementation applied, '
        'Git diff injected, and QA/review chained via `brain_turn`."'
    )
    assert shipped.count(impl_line) == 1, "impl handoff line must appear exactly once"
    assert shipped.count(combined_line) == 1, "combined handoff line must differ"
    agents = _read(ROOT_AGENTS)
    assert "please copy the contents of `tasks/qa/" not in agents
    assert "QA/review chained via `brain_turn`" in agents
    assert "do NOT emit copy-paste task ferrying instructions" in _read(EXECUTOR)
    assert "Revised-plan `brain_turn` chained with the discovery manifest." in shipped
    assert "A revised-plan `brain_turn` is chained" not in shipped
    assert "invoke a revised-plan `brain_turn` yourself" in shipped
    assert (
        "HALT after discovery and invoke a revised-plan `brain_turn` yourself"
        in shipped
    )
    assert "output the context report path for Orchestrator review" not in shipped
    assert "feeding the discovery report manifest via `context_paths=[...]`" in shipped
    hands_call = shipped.index("invokes the QA/review `brain_turn` itself")
    done_mark = shipped.index("you are DONE")
    assert hands_call < done_mark, "DONE must not precede the QA/review chain"
    assert "chain the next `brain_turn` yourself" not in shipped
    assert "chain the fix/review `brain_turn` calls yourself" not in shipped
    assert "the Hands invokes each next `brain_turn`" in shipped
    assert "the Hands invokes fix/re-review `brain_turn` calls" in shipped
    assert "XX-task-name.md" not in agents
    assert "Read the active task file's `**File:**` path" in agents
    changelog = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    assert (
        "a literal `[path-injected:` marker typed in user text "
        "never counts as server-rendered path context"
    ) in changelog
    assert "a literal marker typed in user text never counts" not in changelog


def test_dual_mode_topology_separation():
    role_text = (REPO / "prompts" / "fragments" / "02-role.md").read_text(
        encoding="utf-8"
    )
    assert "MODE: manual (External Brain)" in role_text
    assert "MODE: automatic (MCP Brain Bridge)" in role_text
    for path in (REPO / "prompts" / "fragments").glob("*.md"):
        content = path.read_text(encoding="utf-8")
        assert "in both manual and automatic modes" not in content, (
            f"Contradictory phrase found in {path.name}"
        )
