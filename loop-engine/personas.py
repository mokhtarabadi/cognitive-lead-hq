"""
Runtime Persona Loader — derives ALL personas from the Manager's prompt fragments.

Single source of truth: prompts/fragments/*.md (compiled into system-prompt.md).
Editing a fragment changes engine behavior on next start — no code edits needed.

Parses:
- 12-personas.md            → operational personas (<trigger>/<duty>/<behavior>)
- 16-brainstorming_protocol.md → six swarm personas (<focus>/<output>) + output schema
"""

import re
from pathlib import Path

PERSONAS_FRAGMENT = "prompts/fragments/12-personas.md"
BRAINSTORM_FRAGMENT = "prompts/fragments/16-brainstorming_protocol.md"

_PERSONA_RE = re.compile(r'<persona\s+name="([^"]+)">\s*(.*?)</persona>', re.DOTALL)

# Repo root = parent of loop-engine/ — fallback anchor so fragment loading
# works regardless of the process CWD (same class of fix as daemon REPO_ROOT).
_REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(root: Path, rel: str) -> str:
    p = root / rel
    if not p.exists():
        p = _REPO_ROOT / rel
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def _tag(block: str, tag_name: str) -> str:
    m = re.search(rf"<{tag_name}>(.*?)</{tag_name}>", block, re.DOTALL)
    return m.group(1).strip() if m else ""


def load_personas(workspace_root: str = ".") -> dict[str, dict]:
    """Load operational personas: {name: {trigger, duty, behavior}}."""
    raw = _read(Path(workspace_root), PERSONAS_FRAGMENT)
    personas: dict[str, dict] = {}
    for name, block in _PERSONA_RE.findall(raw):
        personas[name] = {
            "name": name,
            "trigger": _tag(block, "trigger"),
            "duty": _tag(block, "duty"),
            "behavior": _tag(block, "behavior"),
        }
    return personas


def load_swarm_personas(workspace_root: str = ".") -> dict[str, dict]:
    """Load brainstorming swarm personas: {name: {focus, output}}."""
    raw = _read(Path(workspace_root), BRAINSTORM_FRAGMENT)
    swarm: dict[str, dict] = {}
    for name, block in _PERSONA_RE.findall(raw):
        swarm[name] = {
            "name": name,
            "focus": _tag(block, "focus"),
            "output": _tag(block, "output"),
        }
    return swarm


def load_brainstorm_schema(workspace_root: str = ".") -> str:
    """Return the verbatim <brainstorming_session> output schema block."""
    raw = _read(Path(workspace_root), BRAINSTORM_FRAGMENT)
    m = re.search(r"<output_schema>(.*?)</output_schema>", raw, re.DOTALL)
    return m.group(1).strip() if m else ""
