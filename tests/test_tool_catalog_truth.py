# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Tool-catalog truth gates for the live instruction artifacts.

Every instruction artifact the Hands reads must name only tools that exist
in an OpenCode 2 session. A phantom name is a hard failure, not a style
nit: the agent cannot call what does not exist, so it improvises with the
only always-available writer (the shell), which is exactly the python-patch
drift this gate exists to stop.

The scan deliberately skips `DECISIONS.md` files and archive/history
directories: those are historical evidence and must keep their verbatim
records of retired tool names.
"""

from pathlib import Path
import re

REPO = Path(__file__).resolve().parent.parent
EXECUTOR = REPO / "agents" / "cognitive-executor.md"
DISCOVERY = REPO / "agents" / "cognitive-discovery.md"
OPENCHAMBER = REPO / "docs" / "openchamber.md"

# Every live instruction surface that a model may read as operating rules.
SCAN_ROOTS = [
    REPO / "skill-templates",
    REPO / "AGENTS.md",
    REPO / "README.md",
    REPO / "prompts",
    REPO / "agents",
    REPO / "docs",
]

# Historical evidence keeps its own text; never rewrite an ADR to satisfy a gate.
SKIP_DIR_NAMES = {"archive", "history", ".sessions"}
SKIP_FILE_NAMES = {"DECISIONS.md"}

# Tokens that resolve to no callable tool in this session.
PHANTOM_TOKENS = (
    "apply_patch",
    "`bash` tool",
    "@explore",
    "@general",
    "view_file",
    "multiedit",
    "str_replace_editor",
    "create_file",
)


def _read(path: Path) -> str:
    """Return a file's text as UTF-8."""
    return path.read_text(encoding="utf-8")


def _is_skipped(path: Path) -> bool:
    """True when the path is historical evidence rather than live instruction."""
    if path.name in SKIP_FILE_NAMES:
        return True
    return any(part in SKIP_DIR_NAMES for part in path.parts)


def _iter_scan_files():
    """Yield every live Markdown artifact under SCAN_ROOTS, sorted for stability."""
    for root in SCAN_ROOTS:
        if root.is_file():
            if not _is_skipped(root):
                yield root
            continue
        for path in sorted(root.rglob("*.md")):
            if not _is_skipped(path):
                yield path


def test_no_phantom_tool_names_in_live_artifacts():
    """No live artifact may name a tool the session cannot call."""
    offenders = []
    for path in _iter_scan_files():
        text = _read(path)
        for token in PHANTOM_TOKENS:
            if token in text:
                offenders.append(f"{path.relative_to(REPO)} -> {token}")
    assert offenders == [], "phantom tool names in live artifacts:\n" + "\n".join(
        offenders
    )


def test_executor_states_tool_surface():
    """The executor must name its real writers and carry no tool archaeology.

    A lean operator guide says what exists. It does not explain which model
    gets which tool, and it never names a tool that cannot be called.
    """
    text = _read(EXECUTOR)
    assert "`edit`" in text and "`write`" in text
    assert "Your Tool Surface" in text
    assert "Edit Recovery Protocol" in text
    assert "`shell`" in text
    assert "`subagent`" in text
    # The topic is retired: no patch archaeology, no model-identity prose.
    for retired in ("apply_patch", "GPT", "non-GPT", "patch parser"):
        assert retired not in text, f"retired tool prose still in executor: {retired}"


def test_openchamber_lists_session_tools():
    """The OpenChamber doc must list what the session exposes and what it does not."""
    text = _read(OPENCHAMBER)
    for exposed in (
        "openchamber_render",
        "openchamber_secret",
        "openchamber_notify",
        "openchamber_web",
    ):
        assert exposed in text, f"exposed tool missing from docs: {exposed}"
    assert "opencode" in text and "namespace" in text
    assert "openchamber_schedule" in text
    assert "Not exposed in this session" in text


def test_no_scripted_edit_instructions():
    """No live artifact may instruct a `sed -i` edit.

    Naming the ban is fine ("`sed -i` is forbidden"); *instructing* the shape
    is not. The discriminator is a quote directly after the flag, which only
    appears in a real substitution command.
    """
    pattern = re.compile(r"sed\s+-i\s+['\"]")
    offenders = []
    for path in _iter_scan_files():
        for lineno, line in enumerate(_read(path).splitlines(), 1):
            if pattern.search(line):
                offenders.append(f"{path.relative_to(REPO)}:{lineno}")
    assert offenders == [], "scripted edit instructions:\n" + "\n".join(offenders)


def test_agent_frontmatter_uses_v2_permissions():
    """Agent frontmatter must use the V2 `permissions` array, not V1 fields.

    V1 `permission` (singular map), `tools`, `temperature`, and action-scoped
    `bash` entries are deprecated. A frontmatter that keeps them is read
    through a compatibility path, so the rules silently stop matching the
    live tool names.
    """
    for agent in (EXECUTOR, DISCOVERY):
        text = _read(agent)
        parts = text.split("---")
        assert len(parts) >= 3, f"no frontmatter block in {agent.name}"
        frontmatter = parts[1]
        assert "permissions:" in frontmatter, f"missing V2 permissions in {agent.name}"
        assert "action:" in frontmatter, f"no action rules in {agent.name}"
        assert "effect:" in frontmatter, f"no effect values in {agent.name}"
        for legacy in ("permission:", "tools:", "temperature", "bash:"):
            assert legacy not in frontmatter, (
                f"legacy V1 field {legacy!r} in {agent.name} frontmatter"
            )


def test_executor_keeps_zac_denies():
    """The ZAC deny rules must survive the V2 rewrite, or staging is unguarded."""
    frontmatter = _read(EXECUTOR).split("---")[1]
    for command in ("git add", "git checkout", "git commit", "git push"):
        assert f'resource: "{command}*"' in frontmatter, (
            f"missing ZAC deny for {command}"
        )
    assert frontmatter.count("effect: deny") >= 4
