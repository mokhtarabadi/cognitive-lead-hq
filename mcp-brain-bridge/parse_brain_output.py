# Sibling Docs: mcp-brain-bridge/README.md | Decisions: mcp-brain-bridge/DECISIONS.md
"""Deterministically parse one Brain output artifact for Hands.

The bridge and Hands share this helper so control payloads are never parsed
by per-turn improvised Python. It reports complete validated blocks but does
not execute them; malformed or partial XML remains visible and non-executable.
"""

import importlib.util
import json
import os
import sys
from pathlib import Path


def _ensure_mcp_runtime():
    """Re-exec once with the bridge venv when the caller's Python lacks MCP."""
    if importlib.util.find_spec("mcp") is not None:
        return
    if os.environ.get("BRAIN_PARSE_BOOTSTRAPPED") == "1":
        return
    venv_python = Path(__file__).with_name(".venv") / "bin" / "python"
    if not venv_python.is_file():
        return
    env = dict(os.environ)
    env["BRAIN_PARSE_BOOTSTRAPPED"] = "1"
    os.execve(
        str(venv_python), [str(venv_python), str(Path(__file__)), *sys.argv[1:]], env
    )


_ensure_mcp_runtime()


def _load_bridge():
    path = Path(__file__).with_name("server.py")
    spec = importlib.util.spec_from_file_location("brain_bridge_server", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Brain Bridge module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print(
            json.dumps(
                {"error": "usage: parse_brain_output.py <artifact-path>"},
                ensure_ascii=False,
            )
        )
        return 2
    artifact_path = Path(args[0])
    try:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {"error": f"unreadable artifact: {exc}"},
                ensure_ascii=False,
            )
        )
        return 2
    if not isinstance(artifact, dict):
        print(json.dumps({"error": "artifact root must be an object"}))
        return 2

    bridge = _load_bridge()
    raw = artifact.get("full_output") or ""
    strict_error = None
    try:
        blocks = bridge.extract_xml_blocks(raw)
    except ValueError as exc:
        blocks = []
        strict_error = str(exc)

    if blocks:
        problems = bridge.validate_hands_xml_blocks(blocks)
    else:
        problems = [strict_error] if strict_error else ["no xml blocks to validate"]

    report = {
        "block_count": int(artifact.get("block_count", len(blocks))),
        "blocks": blocks,
        "validation_problems": problems,
        "executable": bool(blocks) and not problems,
    }
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
