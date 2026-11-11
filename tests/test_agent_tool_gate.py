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
- cognitive-discovery is a read-only subagent that denies edit plus the shell action by design; it is asserted as deny with reason.
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


def _parse_rules(frontmatter: str) -> list:
    """Parse a V2 `permissions` array into ordered rule dicts.

    Args: frontmatter extracted frontmatter text.
    Returns: list of {action, resource, effect} dicts in declaration order.
    """
    rules = []
    current = {}
    in_permissions = False
    for raw in frontmatter.splitlines():
        line = raw.strip()
        if line.startswith("permissions:"):
            in_permissions = True
            continue
        if not in_permissions:
            continue
        if line.startswith("- "):
            if current:
                rules.append(current)
            current = {}
            line = line[2:].strip()
        match = re.match(r"(action|resource|effect):\s*(.+)$", line)
        if match:
            current[match.group(1)] = match.group(2).strip().strip('"').strip("'")
    if current:
        rules.append(current)
    return rules


def _effective_effect(frontmatter: str, action: str, resource: str = "*"):
    """Return the effective effect for an action after last-match resolution.

    OpenCode evaluates permission rules in order and the last match wins, so
    this mirrors that instead of scanning for the first allow or deny.

    Args: frontmatter extracted text; action permission action; resource
    concrete resource, defaulting to the wildcard.
    Returns: "allow", "deny", "ask", or None when no rule matches.
    """
    effect = None
    for rule in _parse_rules(frontmatter):
        rule_action = rule.get("action", "")
        rule_resource = rule.get("resource", "")
        if rule_action not in ("*", action):
            continue
        if rule_resource not in ("*", resource):
            continue
        effect = rule.get("effect")
    return effect


def _permission_allows_shell(frontmatter: str) -> bool:
    """True when the shell action resolves to allow under V2 last-match rules."""
    return _effective_effect(frontmatter, "shell") == "allow"


def _permission_denies(frontmatter: str, tool: str) -> bool:
    """True when the named action resolves to deny under V2 last-match rules."""
    return _effective_effect(frontmatter, tool) == "deny"


def _agent_files():
    """List agent definition files sorted by name. Returns: sorted list of Path objects."""
    # Only files carrying YAML frontmatter count as agent definitions; slice docs stay out.
    return sorted(
        p for p in AGENTS_DIR.glob("*.md") if _extract_frontmatter(_read_text(p)) != ""
    )


def test_free_tier_agents_keep_bash():
    """Free-tier-intended agents must expose the shell tool; discovery exempt is skipped here."""
    # Collect failures for one clear assertion message.
    missing = []
    # Iterate every agent file to prevent silent additions without the gate.
    for agent_path in _agent_files():
        if agent_path.name in READ_ONLY_EXEMPT:
            continue
        text = _read_text(agent_path)
        front = _extract_frontmatter(text)
        if not _permission_allows_shell(front):
            missing.append(agent_path.name)
    assert not missing, (
        f"free-tier-intended agents must allow shell, missing: {missing}"
    )


def test_read_only_agent_stays_deny():
    """Read-only subagent must stay deny for edit plus shell by design."""
    target = AGENTS_DIR / "cognitive-discovery.md"
    assert target.exists(), "read-only discovery agent file must exist"
    text = _read_text(target)
    front = _extract_frontmatter(text)
    # Discovery denies edit by design as read-only.
    assert _permission_denies(front, "edit"), "discovery must deny edit"
    # Discovery denies the shell action by design as read-only.
    assert _permission_denies(front, "shell"), "discovery must deny shell"
