# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Free-tier bash gate guard.

Custom primary agents must keep bash in the allowlist when free-tier use is intended.
Upstream free-tier models classify the caller by the request-body tool list; a call
without bash is treated as outside the host and fails with FreeTierError on free models.

Upstream evidence:
- https://github.com/anomalyco/opencode/issues/50627 : shell deny-all breaks every free-tier request.
- https://github.com/anomalyco/opencode/issues/54744 : restricted subagent shape can fail even with bash allowed.
  Bash presence is necessary but not sufficient for restricted shapes. Docs note only, not a code fix.

Exemption:
- cognitive-discovery is a read-only subagent that denies edit plus bash by design; it is asserted as deny with reason.
"""

from pathlib import Path
import re

AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"
READ_ONLY_EXEMPT = {"cognitive-discovery.md"}


def _read_text(agent_path: Path) -> str:
    """Read agent markdown as text for frontmatter parsing. Args: agent_path path to agent file. Returns: file text. Assumes UTF-8."""
    return agent_path.read_text(encoding="utf-8")


def _extract_frontmatter(markdown_text: str) -> str:
    """Extract YAML frontmatter between first two triple-dash markers. Args: markdown_text full file text. Returns: frontmatter text or empty string when markers absent."""
    # Split on lines to avoid matching body separators.
    lines = markdown_text.splitlines()
    # Frontmatter must start at first line.
    if not lines or lines[0].strip() != "---":
        return ""
    # Find closing marker.
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return "\n".join(lines[1:idx])
    return ""


def _permission_allows_bash(frontmatter: str) -> bool:
    """Return True when permission block allows bash. Args: frontmatter extracted frontmatter text. Returns: True for allow, False for missing or deny."""
    low = frontmatter.lower()
    # Bash must be mentioned at all.
    if "bash" not in low:
        return False
    # Explicit deny patterns fail closed.
    if re.search(r"bash\s*:\s*deny", low):
        return False
    if re.search(r"bash.*deny\s*-\s*all", low):
        return False
    # Direct allow patterns pass.
    if re.search(r"bash\s*:\s*allow", low):
        return True
    if re.search(r'"bash"\s*:\s*"allow', low):
        return True
    # Nested shape with bash key plus allow token in permission scope passes.
    perm = low.split("permission", 1)[-1] if "permission" in low else low
    return "allow" in perm


def _permission_denies(frontmatter: str, tool: str) -> bool:
    """Return True when permission block denies the named tool. Args: frontmatter extracted text; tool tool name. Returns: True for deny."""
    low = frontmatter.lower()
    return bool(re.search(rf"{re.escape(tool)}\s*:\s*deny", low))


def _agent_files():
    """List agent definition files sorted by name. Returns: sorted list of Path objects."""
    # Only files carrying YAML frontmatter count as agent definitions; slice docs stay out.
    return sorted(
        p for p in AGENTS_DIR.glob("*.md") if _extract_frontmatter(_read_text(p)) != ""
    )


def test_free_tier_agents_keep_bash():
    """Free-tier-intended agents must allow bash; discovery exempt is skipped here."""
    # Collect failures for one clear assertion message.
    missing = []
    # Iterate every agent file to prevent silent additions without the gate.
    for agent_path in _agent_files():
        if agent_path.name in READ_ONLY_EXEMPT:
            continue
        text = _read_text(agent_path)
        front = _extract_frontmatter(text)
        if not _permission_allows_bash(front):
            missing.append(agent_path.name)
    assert not missing, f"free-tier-intended agents must allow bash, missing: {missing}"


def test_read_only_agent_stays_deny():
    """Read-only subagent must stay deny for edit plus bash by design."""
    target = AGENTS_DIR / "cognitive-discovery.md"
    assert target.exists(), "read-only discovery agent file must exist"
    text = _read_text(target)
    front = _extract_frontmatter(text)
    # Discovery denies edit by design as read-only.
    assert _permission_denies(front, "edit"), "discovery must deny edit"
    # Discovery denies bash by design as read-only.
    assert _permission_denies(front, "bash"), "discovery must deny bash"
