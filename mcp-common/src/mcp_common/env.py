"""Explicit `.env` file loading for MCP servers (Task 170, extracted).

Single home for the loader previously duplicated in mcp-persona-server and
mcp-decision-server. Standard library only — no third-party imports.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional


def load_env_files(server_dir: Optional[Path] = None) -> Optional[str]:
    """Load `.env` files explicitly; real process env always wins.

    Empty-string values count as UNSET (OpenCode's `environment: {env:…}`
    blocks inject empty strings when the parent env lacks the var — those
    must not shadow real file values, otherwise litellm sends blank auth).
    Search order (first file holding a key wins):
    1. `<server-dir>/.env` (sidecar, mirrors telegram-mcp layout).
    2. `<server-dir>/../.env` (project root for repo installs, or the
       `~/.config/opencode/.env` backup for global installs).
    3. `<cwd>/.env` (project root when opencode launches us in a project).

    Args:
        server_dir: Owning server's directory (defaults to the caller's
            file directory — pass explicitly; ``__file__`` here points at
            this shared module, not the server).

    Returns:
        Path of the first `.env` file actually loaded, or None.
    """
    if server_dir is None:
        raise ValueError("server_dir is required (shared module has no server home)")
    base = Path(server_dir).resolve()
    candidates = [base / ".env", base.parent / ".env", Path.cwd() / ".env"]
    seen: set[Path] = set()
    first_loaded: Optional[str] = None
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen or not resolved.is_file():
            continue
        seen.add(resolved)
        try:
            # utf-8-sig transparently strips a BOM; without it the first
            # key would carry a "\ufeff" prefix and silently never match.
            text = resolved.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if key.startswith("export "):
                key = key[len("export ") :].strip()
            if not key or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
                continue
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            if not os.environ.get(key):
                # Unset OR empty (e.g. blank {env:} injection): file wins.
                if first_loaded is None:
                    first_loaded = str(resolved)
                os.environ[key] = value
    return first_loaded
