"""Validate a generated opencode.json against the V1 runtime contract.

Usage: python3 validate-opencode.py <path-to-opencode.json>
Exit 0 = valid. Exit 1 = errors printed, one per line.

Checks (stdlib only):
  1. File parses as JSON (rejects trailing commas, bad types).
  2. Top-level shape: default_agent non-empty; mcp/permission objects.
  3. V1 permission form: flat string map; V2 `permissions[]` array rejected.
  4. ZAC bash deny set present (all 8 patterns must be "deny").
  5. Each MCP server: type/command/enabled/timeout present, correct types.
  6. No literal secrets: any environment value not starting with "{env:"
     fails (secrets travel as placeholders only).
  7. LSP is V1-only: a `language-server` map of {name: {command: [...]}};
     V2 `enabled`/`extensions` keys and unknown lsp keys are rejected.
  8. Plugin entries are strings or dicts; dict environments obey the same
     {env:} + literal-secret rule as MCP environments.
  9. No invented values: TODO/changeme/xxx/your-value-here/foo/bar/dummy/
     placeholder (any case) and standalone "example"/"sample" are
     rejected in default_agent, MCP commands and env names, plugin
     sources, instructions, formatter, agents_dir, theme, keybinds.
     "{env:}" references are never treated as invented.
  10. Optional `$schema` must be a string when present.
"""

from __future__ import annotations

import json
import re
import sys

ZAC_DENIES = (
    "git add",
    "git add *",
    "git checkout",
    "git checkout *",
    "git commit",
    "git commit *",
    "git push",
    "git push *",
)

SECRET_LIKE = re.compile(
    r"(sk-|ghp_|gho_|AIza|xox|-----BEGIN |^[A-Za-z0-9+/]{32,}={0,2}$)"
)

# Secret-like KEY names. An env-less plugin entry naming one of these has
# nowhere safe to store the value, so it must declare an environment.
SECRET_KEY_NAME = re.compile(
    r"(token|password|passwd|secret|api[-_]?key|auth)", re.IGNORECASE
)

# Invented-value markers. Bare substrings are unambiguous placeholders;
# "example"/"sample" need a word edge so only standalone words trip them
# ("examples", "samples", "sampling", "exemplary" pass; hyphenated
# "my-example" still fails). "{env:...}" references are never scanned —
# an env name like FOO_PATH is a declaration, not an invention.
PLACEHOLDER_SUBSTRINGS = (
    "todo",
    "changeme",
    "xxx",
    "your-value-here",
    "foo",
    "bar",
    "dummy",
    "placeholder",
)
PLACEHOLDER_WORDEDGE = re.compile(r"\bexample\b|\bsample\b", re.IGNORECASE)


def _has_placeholder(*values: object) -> bool:
    for value in values:
        if not isinstance(value, str):
            continue
        if value.startswith("{env:"):
            continue
        lowered = value.lower()
        if any(marker in lowered for marker in PLACEHOLDER_SUBSTRINGS):
            return True
        if PLACEHOLDER_WORDEDGE.search(value):
            return True
    return False


def validate(cfg: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(cfg, dict):
        return ["top level must be a JSON object"]
    if "$schema" in cfg and not isinstance(cfg["$schema"], str):
        errors.append("$schema must be a string")
    if not cfg.get("default_agent") or not isinstance(cfg["default_agent"], str):
        errors.append("default_agent must be a non-empty string")
    elif _has_placeholder(cfg["default_agent"]):
        errors.append("default_agent looks invented; use an existing agent name")
    if "permissions" in cfg:
        errors.append("V2 'permissions[]' array forbidden; use V1 'permission{}' map")
    perm = cfg.get("permission")
    if not isinstance(perm, dict):
        errors.append("permission must be a V1 string map object")
    else:
        for tool, decision in perm.items():
            if tool == "bash":
                continue
            if isinstance(decision, dict):
                # Scoped sub-map (e.g. external_directory): leaves must be
                # allow|ask|deny. The golden file proves this V1 shape.
                for scope, leaf in decision.items():
                    if leaf not in ("allow", "ask", "deny"):
                        errors.append(
                            f"permission[{tool}][{scope!r}] must be allow|ask|deny"
                        )
            elif decision not in ("allow", "ask", "deny"):
                errors.append(f"permission[{tool!r}] must be allow|ask|deny")
        bash = perm.get("bash")
        if not isinstance(bash, dict):
            errors.append("permission.bash must be a command-pattern map")
        else:
            for pattern in ZAC_DENIES:
                if bash.get(pattern) != "deny":
                    errors.append(f"permission.bash[{pattern!r}] must be 'deny'")
    mcp = cfg.get("mcp")
    if not isinstance(mcp, dict):
        errors.append("mcp must be an object of server entries")
    else:
        for name, srv in mcp.items():
            if not isinstance(srv, dict):
                errors.append(f"mcp[{name}] must be an object")
                continue
            for key, typ in (("type", str), ("command", list), ("enabled", bool), ("timeout", int)):
                if not isinstance(srv.get(key), typ):
                    errors.append(f"mcp[{name}].{key} must be {typ.__name__}")
            if _has_placeholder(*srv.get("command", [])):
                errors.append(
                    f"mcp[{name}].command looks invented; use real paths/commands"
                )
            env = srv.get("environment", {})
            if not isinstance(env, dict):
                errors.append(f"mcp[{name}].environment must be an object")
                continue
            for var, val in env.items():
                if not isinstance(val, str) or not val.startswith("{env:"):
                    errors.append(
                        f"mcp[{name}].environment[{var}] must be an '{{env:}}' placeholder"
                    )
                if _has_placeholder(var):
                    errors.append(
                        f"mcp[{name}].environment var name looks invented"
                    )
                if isinstance(val, str) and SECRET_LIKE.search(val):
                    errors.append(
                        f"mcp[{name}].environment[{var}] looks like a literal secret"
                    )
    invented_scope = {
        "instructions": cfg.get("instructions"),
        "formatter": cfg.get("formatter"),
        "agents_dir": cfg.get("agents_dir"),
        "theme": cfg.get("theme"),
        "keybinds": cfg.get("keybinds"),
    }
    for field, val in invented_scope.items():
        if val is None:
            continue
        strings = (
            [item for item in val if isinstance(item, str)]
            if isinstance(val, list)
            else [val]
            if isinstance(val, str)
            else []
        )
        if _has_placeholder(*strings):
            errors.append(
                f"{field} looks invented; use project-declared values"
            )
    plugins = cfg.get("plugin")
    if plugins is not None:
        if not isinstance(plugins, list):
            errors.append("plugin must be a list of entries")
        else:
            for entry in plugins:
                if isinstance(entry, str):
                    if _has_placeholder(entry):
                        errors.append(
                            "plugin entry looks invented; use a declared plugin"
                        )
                    continue
                if not isinstance(entry, dict):
                    errors.append("plugin entries must be strings or objects")
                    continue
                if _has_placeholder(entry.get("source"), entry.get("command")):
                    errors.append(
                        "plugin entry looks invented; use a declared plugin"
                    )
                if "environment" not in entry:
                    # Env-less entries are fine unless they name secret-like
                    # keys with nowhere safe to store the value.
                    for key in entry:
                        if isinstance(key, str) and SECRET_KEY_NAME.search(key):
                            errors.append(
                                "plugin entry names a secret-like key without "
                                "environment; use an {env:} placeholder"
                            )
                            break
                    continue
                env = entry.get("environment")
                if not isinstance(env, dict):
                    errors.append("plugin environment must be an object")
                    continue
                for var, val in env.items():
                    if not isinstance(val, str) or not val.startswith("{env:"):
                        errors.append(
                            f"plugin.environment[{var}] must be an '{{env:}}' placeholder"
                        )
                    if _has_placeholder(var):
                        errors.append(
                            "plugin.environment var name looks invented"
                        )
                    if isinstance(val, str) and SECRET_LIKE.search(val):
                        errors.append(
                            f"plugin.environment[{var}] looks like a literal secret"
                        )
    lsp = cfg.get("lsp")
    if lsp is not None:
        if not isinstance(lsp, dict):
            errors.append("lsp must be an object")
        elif "enabled" in lsp or "extensions" in lsp:
            errors.append(
                "V2 lsp keys forbidden; use V1 'language-server' map"
            )
        else:
            for lsp_name, spec in lsp.items():
                if lsp_name != "language-server" or not isinstance(spec, dict):
                    errors.append(
                        "lsp allows only a V1 'language-server' map of servers"
                    )
                    break
                for srv_name, srv_spec in spec.items():
                    if not isinstance(srv_spec, dict):
                        errors.append(
                            f"lsp language-server[{srv_name}] must be an object"
                        )
                        continue
                    cmd = srv_spec.get("command")
                    if not isinstance(cmd, list) or not cmd:
                        errors.append(
                            f"lsp language-server[{srv_name}] needs a non-empty command list"
                        )
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate-opencode.py <path-to-opencode.json>")
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"parse error: {exc}")
        return 1
    errors = validate(cfg)
    for err in errors:
        print(f"error: {err}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
