# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Shipped-prompt content gates (Task 241 Gap 4).

The rtk mandate must survive in the assembled system prompt, the shipped
version must match the fragment source, and the assembler output must
equal the committed file (same contract as lint_system_prompt_sync).
"""

import json
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
TASKGEN_SKILL = REPO / "skill-templates" / "kanban-lifecycle" / "SKILL.md"


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
    assert shipped == "9.97.0"


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
    assert "block_count" in text
    assert re.search(r"return the whole\s+payload", text, re.IGNORECASE)


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
    assert "per-message requested language" not in text
    assert "clarification request in simple English" in text


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
    assert (
        "manual review MUST reject a diff that hand-copies a governed type" in executor
    )
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


def test_shipped_prompt_version_is_9_97_0():
    prompt = _read_shipped_prompt_for_approval_contract()
    assert "9.97.0" in prompt


def test_openui_validity_gate_in_executor_and_fragment():
    """The render contract must carry signatures and a pre-render self-check."""
    executor = _read(EXECUTOR)
    assert (
        "OpenUI validity gate (mandatory before every `openchamber_render` call)"
        in executor
    )
    assert "`Table(columns: string[], rows: (string | number)[][])`" in executor
    assert "Never wrap a cell in its own brackets" in executor
    assert "never `name: value`" in executor
    assert (
        "Read a render diagnostic from the submitted source, not from its wording"
        in executor
    )

    fragment = _read(FRAGMENT_09)
    assert "MANAGER-FACING RENDER CONTRACT" in fragment
    assert "`Table(columns: string[], rows: (string | number)[][])`" in fragment
    assert "never wrap a `Table` cell in brackets" in fragment
    assert "Arity-style render diagnostics mean a source defect" in fragment


def test_render_call_envelope_in_executor_and_fragment():
    """The tool-call shape must be pinned as strictly as the program itself."""
    executor = _read(EXECUTOR)
    assert (
        "`openchamber_render` call envelope (mandatory before the program check)"
        in executor
    )
    assert '"action": "render.page"' in executor
    assert "`parameters` is a real object" in executor
    assert "Never pass a JSON-encoded string" in executor
    assert "Exactly one payload lives inside `parameters`" in executor
    assert "Never resend the same stringified arguments" in executor

    fragment = _read(FRAGMENT_09)
    assert 'Build the `openchamber_render` call as `action: "render.page"`' in fragment
    assert "with `parameters` as a real object, never a JSON-encoded string" in fragment
    assert "`parameters: Expected object` validation error" in fragment


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
    assert 'resource: "git checkout*"' in executor
    assert "effect: deny" in executor


def test_executor_verification_gate_and_documentation_rule():
    """CRITICAL GATE FUNCTION and full documentation rule live in executor."""
    executor = _read(EXECUTOR)
    assert "CRITICAL GATE FUNCTION" in executor
    assert "testing-verification" in executor
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
    tpl_dir = TASKGEN_SKILL.parent / "templates"
    if tpl_dir.is_dir():
        for f in sorted(tpl_dir.glob("*.md")):
            text += "\n" + f.read_text(encoding="utf-8")
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


def test_unified_brain_turn_topology():
    role_text = (REPO / "prompts" / "fragments" / "02-role.md").read_text(
        encoding="utf-8"
    )
    assert "never as a manual copy-paste courier" in role_text
    assert "exclusively via `mcp-brain-bridge` (`brain_turn`)" in role_text
    for path in (REPO / "prompts" / "fragments").glob("*.md"):
        content = path.read_text(encoding="utf-8")
        assert "External Brain in web chat" not in content, (
            f"Manual courier remnant in {path.name}"
        )
        assert "Manager acts as the human courier" not in content, (
            f"Manual courier remnant in {path.name}"
        )


def test_capability_exact_grants_memory_tools():
    """Memory tools are in AVAILABLE_EXACT (capability.py)."""
    import re

    cap = (REPO / "mcp-brain-bridge" / "capability.py").read_text(encoding="utf-8")
    for tool in (
        "search_memory",
        "read_memory",
        "store_memory",
        "list_namespaces",
        "rebuild_memory_index",
        "delete_memory",
        "execute",
    ):
        assert f'"{tool}"' in cap, f"{tool} missing from AVAILABLE_EXACT"


def test_skill_templates_no_dsp_violations():
    """No 2>/dev/null on data/inspection commands in skill templates."""
    import re

    violations = []
    for path in (REPO / "skill-templates").rglob("*.md"):
        if "governance" in str(path):
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "2>/dev/null" in line:
                violations.append(f"{path.relative_to(REPO)}:{i}")
    assert not violations, f"DSP violations found: {violations}"


def test_no_template_preservation_rule_in_prompts():
    """Template Preservation was deleted (W2); the Placeholder Ban covers it."""
    for path in (REPO / "prompts" / "fragments").glob("*.md"):
        content = path.read_text(encoding="utf-8")
        assert "Template Preservation" not in content, (
            f"Template Preservation remnant in {path.name}"
        )


def test_fragment_09_has_worked_examples():
    """09 carries two worked example blocks plus two templates (G1)."""
    text = _read(FRAGMENT_09)
    assert "<worked_examples>" in text
    lines = [
        line for line in text.splitlines() if "<hands_implementation_task>" in line
    ]
    assert len(lines) >= 4, f"expected 4+ template/example lines, got {len(lines)}"


def test_role_fragment_has_precedence_ladder():
    """02-role.md carries the conflict-resolving precedence ladder (G2)."""
    text = (REPO / "prompts" / "fragments" / "02-role.md").read_text(encoding="utf-8")
    assert "precedence" in text
    assert "ZAC and approval literals" in text


def test_no_mutable_year_in_system_context():
    """03-system_context.md carries no mutable year line (A3)."""
    text = (REPO / "prompts" / "fragments" / "03-system_context.md").read_text(
        encoding="utf-8"
    )
    assert "Remember it is 2026" not in text


def test_executor_carries_context_map_contract():
    """Executor owns the Context Map contract with per-site classes."""
    text = _read(EXECUTOR)
    assert "## Context Map Before Brain Calls" in text
    count = sum(1 for line in text.splitlines() if "Context-Map" in line)
    assert count >= 15, f"expected 15+ Context-Map lines, got {count}"


def test_fragment_09_carries_context_map_classes():
    """09 documents the Context-Map class of each template turn."""
    text = _read(FRAGMENT_09)
    count = sum(1 for line in text.splitlines() if "Context-Map" in line)
    assert count >= 5, f"expected 5+ Context-Map lines, got {count}"


def test_no_bare_context_paths_label():
    """A bare label in context_paths is rejected (forbidden shape)."""
    for base in (REPO / "agents", REPO / "prompts" / "fragments"):
        for path in base.rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            assert 'context_paths=["' not in content, (
                f"bare context_paths label in {path.relative_to(REPO)}"
            )


def test_approval_never_count_canonical_in_constraints():
    """The negative-case list lives in the 13-constraints guard (P3)."""
    text = (REPO / "prompts" / "fragments" / "13-constraints.md").read_text(
        encoding="utf-8"
    )
    assert "These never count:" in text


def test_qa_persona_uses_verdict_format():
    """qa-engineer orders VERDICT form, never the bare Status form (W13)."""
    text = (REPO / "prompts" / "fragments" / "personas" / "qa-engineer.md").read_text(
        encoding="utf-8"
    )
    assert "Status (QA_PASSED" not in text
    assert "VERDICT: QA_PASSED" in text


def test_communication_examples_language_rule():
    """Example 4 is a translation example; the per-message clause is gone (W8)."""
    text = (REPO / "prompts" / "fragments" / "20-communication_examples.md").read_text(
        encoding="utf-8"
    )
    assert "follows the per-message request" not in text
    assert "Translation example" in text


def test_assembled_prompt_tags_balance():
    """Every XML tag opened in the shipped prompt is closed (V1)."""
    import re

    pairs = REPO / "tests" / "fixtures" / "prompt_tag_pairs.txt"
    shipped = _read(SHIPPED)
    code_free = re.sub(r"`[^`\n]*`", "", shipped)
    for line in pairs.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        open_tag, close_tag = line.split("|")
        assert code_free.count(open_tag) == code_free.count(close_tag), (
            f"tag imbalance: {open_tag} x{code_free.count(open_tag)} "
            f"vs {close_tag} x{code_free.count(close_tag)}"
        )
        assert code_free.count(open_tag) >= 1, f"tag absent: {open_tag}"


def test_approval_literal_single_home():
    """The full approval-literal block lives only in 13-constraints (V3)."""
    constraint = (REPO / "prompts" / "fragments" / "13-constraints.md").read_text(
        encoding="utf-8"
    )
    policy = (REPO / "prompts" / "fragments" / "24-language_policy.md").read_text(
        encoding="utf-8"
    )
    assert constraint.count("Approved for closure") >= 1
    assert "Approved for closure" not in policy
    assert "constraints fragment" in policy


def test_worked_examples_contain_literal_task_block():
    """The G1 examples are real blocks, not a description of blocks (V2)."""
    text = _read(FRAGMENT_09)
    assert "<worked_examples>" in text
    section = text.split("<worked_examples>")[1].split("</worked_examples>")[0]
    assert section.count("<hands_implementation_task>") == 2
    assert section.count("</hands_implementation_task>") == 2
    assert "require_recipient" in section


def test_executor_has_no_hand_move_of_backlog_task():
    """Taking a task goes through claim_next, never git mv (V6)."""
    text = _read(EXECUTOR)
    assert "git mv tasks/backlog" not in text
    assert "call `claim_next(project_root, task_id)`" in text


def test_assembled_prompt_has_no_fragment_paths():
    """No fragment path or roster pointer reaches the shipped prompt (V14)."""
    shipped = _read(SHIPPED)
    assert "prompts/fragments/personas" not in shipped
    assert "Personas Roster" not in shipped


def test_qa_transition_absent_from_closure_step():
    """The closure step orders commit, never lint or qa_transition (V13)."""
    text = (REPO / "prompts" / "fragments" / "11-execution_workflow.md").read_text(
        encoding="utf-8"
    )
    step8 = text.split("Step 8:")[1].split("Step 9:")[0]
    assert step8.count("Closure sequence") == 1
    assert (
        "Do NOT call `lint_task_file` or `custom_context_qa_transition` again at this step."
        in step8
    )
    assert step8.count("custom_context_commit_and_clean_task") == 1


def test_validation_blocks_not_collapsed():
    """Validation blocks keep the expanded five-step list (V15)."""
    fragment = (REPO / "prompts" / "shared" / "validation-phase.md").read_text(
        encoding="utf-8"
    )
    shipped = _read(SHIPPED)
    assert "MANDATORY FIRST STEP): 1." not in fragment
    assert "MANDATORY FIRST STEP): 1." not in shipped
    assert "5. If no violations are found" in fragment
    assert "BUFFER ISOLATION (MANDATORY):" in fragment


def test_adr_test_counts_agree():
    """ADR-012 Decision and Rollback name the same assertion count (V17)."""
    import re

    text = (REPO / "prompts" / "fragments" / "DECISIONS.md").read_text(encoding="utf-8")
    adr = text.split("ADR-012")[1]
    counts = re.findall(r"(\d+) new regression assertions", adr)
    assert counts, "ADR-012 names no assertion count"
    assert len(set(counts)) == 1, f"ADR-012 counts disagree: {counts}"


def test_every_worked_example_has_validation_phase():
    """Every worked example carries one validation block (V24)."""
    text = _read(FRAGMENT_09)
    section = text.split("<worked_examples>")[1].split("</worked_examples>")[0]
    assert section.count("<validation_phase>") == 2
    assert section.count("</validation_phase>") == 2


def test_fragment_closing_tags_at_column_zero():
    """Each fragment's root closing tag starts at column zero (V25)."""
    import re

    for path in (REPO / "prompts" / "fragments").glob("*.md"):
        lines = path.read_text(encoding="utf-8").splitlines()
        root = None
        for line in lines:
            m = re.match(r"^<([a-z_]+)>$", line.strip())
            if m and not line.startswith((" ", "\t")):
                root = m.group(1)
                break
        if root is None:
            continue
        assert f"</{root}>" in lines, f"missing root close in {path.name}"
        idx = lines.index(f"</{root}>")
        assert not lines[idx][:1].isspace(), (
            f"indented root close in {path.name}:{idx + 1}"
        )


def test_approval_exclusion_list_single_home():
    """The exclusion list appears exactly once in the shipped prompt (V27)."""
    shipped = _read(SHIPPED)
    assert shipped.count("These never count:") == 1


def test_stage_tool_only_reruns_hunks():
    """stage_and_inject_diff appears only in its hunk-restaging role (V26)."""
    text = _read(EXECUTOR)
    assert "hunk-level re-staging" in text
    assert "Keep `custom_context_stage_and_inject_diff` only for hunk-level" in text


def test_format_guard_matches_prettierignore() -> None:
    """Every path class the prettier gate ignores must be skipped by the guard.

    Guard and gate share one exclusion source by design. If they drift, a
    fragment gets auto-formatted while the gate still checks it, or the
    reverse, and the assembler byte-identity gate breaks with no obvious cause.
    """
    root = Path(__file__).resolve().parent.parent
    ignored = [
        line.strip()
        for line in (root / ".prettierignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    guard = (root / "scripts" / "format-guard.sh").read_text(encoding="utf-8")
    missing = [entry for entry in ignored if entry not in guard]
    assert not missing, f"guard skips no arm for: {missing}"


def test_format_guard_extensions_match_config() -> None:
    """The guard's dispatch arms and opencode.json's extension list must be identical.

    The two lists are maintained by hand in different files. Parity here means a
    new extension lands in both or in neither.
    """
    root = Path(__file__).resolve().parent.parent
    config = json.loads((root / "opencode.json").read_text(encoding="utf-8"))
    configured = {
        ext.lstrip(".")
        for formatter in config["formatter"].values()
        for ext in formatter["extensions"]
    }
    guard = (root / "scripts" / "format-guard.sh").read_text(encoding="utf-8")
    dispatch = guard.split('case "${FILE##*.}" in', 1)[1].split("esac", 1)[0]
    armed = set()
    for line in dispatch.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("require"):
            continue
        armed.update(
            token.strip()
            for token in stripped.replace(")", "").split("|")
            if token.strip()
            and not token.strip().startswith("*")
            and " " not in token.strip()
            and token.strip() != ";;"
        )
    assert armed == configured, (
        f"drift: guard-only={armed - configured} config-only={configured - armed}"
    )


def test_script_sibling_decisions_exist() -> None:
    """Every `Decisions:` sibling path cited by a script must resolve on disk.

    A phantom sibling pointer sends a reader to a file that does not exist.
    """
    root = Path(__file__).resolve().parent.parent
    pattern = re.compile(r"Decisions:\s*(\S+?)\s*$")
    missing = []
    for script in sorted((root / "scripts").glob("*.sh")):
        for line in script.read_text(encoding="utf-8").splitlines()[:5]:
            match = pattern.search(line)
            if match and not (root / match.group(1)).exists():
                missing.append(f"{script.name}: {match.group(1)}")
    assert not missing, f"phantom sibling docs: {missing}"


def test_prettierignore_covers_guard_arms() -> None:
    """Every path class the guard skips must also be ignored by the prettier gate.

    The companion test proves the ignore file is covered by the guard. This one
    proves the reverse, so neither list can grow an entry the other lacks. The
    guard cannot read `.prettierignore` portably in Bash, so the two lists are
    duplicated by necessity and pinned here in both directions.
    """
    root = Path(__file__).resolve().parent.parent
    guard = (root / "scripts" / "format-guard.sh").read_text(encoding="utf-8")
    block = guard.split('case "$REL" in', 1)[1]
    arm_line = next(line for line in block.splitlines() if "|" in line and ")" in line)
    armed = [
        token.strip().rstrip("/*")
        for token in arm_line.replace(")", "").split("|")
        if token.strip()
    ]
    ignored = [
        line.strip()
        for line in (root / ".prettierignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    missing = [entry for entry in armed if not any(entry in line for line in ignored)]
    assert armed, "could not parse the exclusion arm from scripts/format-guard.sh"
    assert not missing, f"ignore file covers no entry for: {missing}"


def test_concision_contract_mirrored_in_all_surfaces():
    """Pin the full canonical concision body across every shipped surface.

    AC1 and AC2 claim one identical rule in the fragment, the assembled
    prompt, and both cognitive agents. An opening-clause needle passes after
    a partial body edit, so this test lifts the complete sentence set from
    the canonical bullet, strips the fragment-only closing sentence, and
    demands exactly one occurrence of the full string on every surface.
    The fragments-tree scan still rejects a fifth copy anywhere.
    """
    marker = "- **Manager-Facing Concision Contract:** "
    fragment = (REPO / "prompts/fragments/13-constraints.md").read_text(
        encoding="utf-8"
    )
    line = next(l for l in fragment.splitlines() if l.startswith(marker))
    body = line[len(marker) :]
    tail = (
        " It replaces every earlier length budget in this prompt and in "
        "both cognitive agents."
    )
    assert body.endswith(tail), "canonical body lost its fragment-only tail"
    shared = body[: -len(tail)]
    assert shared.startswith("Every user-facing response MUST answer first")
    assert len(shared) > 400, "canonical body extraction failed"

    surfaces = (
        "prompts/fragments/13-constraints.md",
        "system-prompt.md",
        "agents/cognitive-executor.md",
        "agents/cognitive-discovery.md",
    )
    for surface in surfaces:
        text = (REPO / surface).read_text(encoding="utf-8")
        assert text.count(shared) == 1, f"full-copy drift in {surface}"

    needle = "Every user-facing response MUST answer first"
    hits = sorted(
        path.name
        for path in (REPO / "prompts" / "fragments").rglob("*.md")
        if needle in path.read_text(encoding="utf-8")
    )
    assert hits == ["13-constraints.md"], f"unexpected concision copies: {hits}"
