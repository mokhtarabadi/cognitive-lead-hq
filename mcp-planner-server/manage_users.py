#!/usr/bin/env python3
# Sibling Docs: mcp-planner-server/README.md | Decisions: mcp-planner-server/DECISIONS.md
"""Manage planner users stored in ~/.config/opencode/planner-users.json.

Stdlib only (argparse, getpass, hashlib, secrets) so it runs with a bare
``python3`` — no venv, no third-party packages. Passwords are stored as
PBKDF2-HMAC-SHA256 with a per-user 16-byte salt; the same scheme the server
verifies against.

Usage:
    python3 manage_users.py add --username admin --role admin --projects "*"
    python3 manage_users.py add --username friend --role viewer --projects /path/to/shared-project
    python3 manage_users.py list
    python3 manage_users.py update --username friend --role viewer --projects /new/path
    python3 manage_users.py remove --username friend
    python3 manage_users.py enable
    python3 manage_users.py disable

The config path comes from ``--config`` or ``PLANNER_USERS_CONFIG``, falling
back to ``~/.config/opencode/planner-users.json``. The planner picks the same
path, so no server-side change is needed after adding a user.
"""

import argparse
import getpass
import hashlib
import json
import os
import secrets
import sys
from pathlib import Path

PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 600_000

DEFAULT_RELATIVE = Path(".config") / "opencode" / "planner-users.json"


def _config_path(override: str | None = None) -> Path:
    """Resolve the users config path (flag, env, then home default)."""
    if override:
        return Path(override).expanduser()
    env = os.environ.get("PLANNER_USERS_CONFIG", "").strip()
    if env:
        return Path(env).expanduser()
    return Path.home() / DEFAULT_RELATIVE


def _load(path: Path) -> dict:
    """Load the config, defaulting to a disabled, user-less document."""
    if not path.is_file():
        return {"auth_enabled": False, "users": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"❌ Cannot read {path}: {exc}")
    if not isinstance(data, dict):
        sys.exit(f"❌ {path} must contain a JSON object.")
    if not isinstance(data.get("users"), list):
        data["users"] = []
    data.setdefault("auth_enabled", False)
    return data


def _save(path: Path, data: dict) -> None:
    """Write the config with owner-only permissions (it holds password hashes)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass  # Non-POSIX filesystems: the file is still written.


def _hash_password(password: str) -> tuple[str, str]:
    """Return ``(salt_hex, hash_hex)`` for ``password`` (PBKDF2-HMAC-SHA256)."""
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM, password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return salt.hex(), derived.hex()


def _find(data: dict, username: str) -> int:
    """Return the index of ``username`` in the users list, or -1."""
    for index, user in enumerate(data.get("users", [])):
        if user.get("username") == username:
            return index
    return -1


def _parse_projects(raw) -> list[str]:
    """Normalize repeated ``--projects`` values into a de-duplicated list."""
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = [raw]
    out: list[str] = []
    for entry in raw:
        value = str(entry).strip()
        if value and value not in out:
            out.append(value)
    return out


def _read_password(username: str) -> str:
    """Prompt twice for a new password and confirm the two match.

    Fails fast with a clear message when there is no TTY (CI, pipes, agent
    shells) instead of raising ``EOFError`` out of getpass.
    """
    try:
        password = getpass.getpass(f"Password for {username}: ")
        if not password:
            sys.exit("❌ Password required.")
        confirm = getpass.getpass("Confirm password: ")
    except (EOFError, OSError):
        sys.exit("❌ No TTY for a password prompt — pass --password instead.")
    if password != confirm:
        sys.exit("❌ Passwords do not match.")
    return password


def _project_summary(projects: list[str]) -> str:
    """Human-readable allowed-projects summary."""
    if "*" in projects:
        return "* (all projects)"
    return ", ".join(projects) if projects else "(none)"


def cmd_add(args) -> int:
    path = _config_path(args.config)
    data = _load(path)
    if _find(data, args.username) >= 0:
        print(f"❌ User '{args.username}' already exists.", file=sys.stderr)
        return 1

    password = args.password or _read_password(args.username)
    salt, hash_hex = _hash_password(password)
    allowed = _parse_projects(args.projects)

    data["users"].append(
        {
            "username": args.username,
            "role": args.role.lower(),
            "password_salt": salt,
            "password_hash": hash_hex,
            "allowed_projects": allowed,
        }
    )
    data["auth_enabled"] = True
    _save(path, data)
    print(
        f"✅ Added user '{args.username}' (role={args.role.lower()}, "
        f"projects={_project_summary(allowed)})."
    )
    print(f"   Config: {path}")
    print("   Auth is now ENABLED — restart mcp-planner to apply.")
    return 0


def cmd_update(args) -> int:
    path = _config_path(args.config)
    data = _load(path)
    index = _find(data, args.username)
    if index < 0:
        print(f"❌ User '{args.username}' not found.", file=sys.stderr)
        return 1

    user = data["users"][index]
    if args.role:
        user["role"] = args.role.lower()

    if args.projects:
        user["allowed_projects"] = _parse_projects(args.projects)
    else:
        current = list(user.get("allowed_projects") or [])
        for entry in _parse_projects(args.add_project):
            if entry not in current:
                current.append(entry)
        for entry in _parse_projects(args.remove_project):
            if entry in current:
                current.remove(entry)
        user["allowed_projects"] = current

    if args.password:
        salt, hash_hex = _hash_password(args.password)
        user["password_salt"] = salt
        user["password_hash"] = hash_hex

    _save(path, data)
    print(
        f"✅ Updated user '{args.username}': role={user.get('role')}, "
        f"projects={_project_summary(list(user.get('allowed_projects') or []))}."
    )
    return 0


def cmd_remove(args) -> int:
    path = _config_path(args.config)
    data = _load(path)
    index = _find(data, args.username)
    if index < 0:
        print(f"❌ User '{args.username}' not found.", file=sys.stderr)
        return 1
    removed = data["users"].pop(index)
    _save(path, data)
    print(f"✅ Removed user '{removed.get('username')}'.")
    if not data["users"]:
        print("   No users left — auth is effectively disabled.")
    return 0


def cmd_list(args) -> int:
    path = _config_path(args.config)
    data = _load(path)
    users = data.get("users", [])
    print(f"Auth enabled: {bool(data.get('auth_enabled'))}")
    print(f"Config: {path}")
    if not users:
        print("\nNo users configured — the server runs in open local mode.")
        return 0
    print()
    print(f"{'Username':<18} {'Role':<8} Projects")
    print("-" * 70)
    for user in users:
        projects = list(user.get("allowed_projects") or [])
        print(
            f"{user.get('username', '?')!s:<18} "
            f"{user.get('role', '?')!s:<8} {_project_summary(projects)}"
        )
    return 0


def cmd_set_enabled(args, enabled: bool) -> int:
    path = _config_path(args.config)
    data = _load(path)
    data["auth_enabled"] = enabled
    _save(path, data)
    if enabled and not data.get("users"):
        print("⚠️  auth_enabled is true but no users exist — the server stays open.")
        return 0
    print(
        f"✅ Auth {'ENABLED' if enabled else 'DISABLED'} in {path}. "
        "Restart mcp-planner to apply."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser (subcommands: add/update/remove/list/enable/disable)."""
    parser = argparse.ArgumentParser(
        description="Manage planner authentication users.",
    )
    parser.add_argument(
        "--config",
        help="Users config path (default: $PLANNER_USERS_CONFIG or "
        "~/.config/opencode/planner-users.json).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Add a user with a password prompt.")
    add.add_argument("--username", required=True)
    add.add_argument(
        "--role", default="viewer", choices=["admin", "viewer"], type=str.lower
    )
    add.add_argument(
        "--projects",
        action="append",
        default=[],
        help="Allowed project root; repeat for several. Use '*' for all.",
    )
    add.add_argument(
        "--password",
        help="Password (non-interactive use; otherwise prompted).",
    )
    add.set_defaults(func=cmd_add)

    update = sub.add_parser("update", help="Update role, projects, or password.")
    update.add_argument("--username", required=True)
    update.add_argument("--role", choices=["admin", "viewer"], type=str.lower)
    update.add_argument(
        "--projects",
        action="append",
        default=[],
        help="Replace the allowed project list; repeat for several.",
    )
    update.add_argument("--add-project", action="append", default=[])
    update.add_argument("--remove-project", action="append", default=[])
    update.add_argument("--password", help="Set a new password.")
    update.set_defaults(func=cmd_update)

    remove = sub.add_parser("remove", help="Remove a user.")
    remove.add_argument("--username", required=True)
    remove.set_defaults(func=cmd_remove)

    listing = sub.add_parser("list", help="List users (no secrets shown).")
    listing.set_defaults(func=cmd_list)

    enable = sub.add_parser("enable", help="Turn authentication on.")
    enable.set_defaults(func=lambda args: cmd_set_enabled(args, True))

    disable = sub.add_parser("disable", help="Turn authentication off (open mode).")
    disable.set_defaults(func=lambda args: cmd_set_enabled(args, False))

    return parser


def main(argv=None) -> int:
    """Parse arguments and dispatch; returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
