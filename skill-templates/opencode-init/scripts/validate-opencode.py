"""Validate a generated opencode.json against the project-only contract.

Matches the public schema https://opencode.ai/config.json
(verified 2026-09-16 via `opencode debug config`):

  formatter: true | false | {<name>: {command?, extensions?,
             environment?, disabled?}}
  lsp:       true | false | {<name>: {command (required), extensions?,
             env?, initialization?, disabled?} | {disabled: true}}

Usage: python3 validate-opencode.py <path-to-opencode.json>
Exit 0 = valid. Exit 1 = errors printed, one per line.

Project allowlist: $schema, default_agent, instructions, formatter,
lsp, permission. `mcp` and `plugin` are GLOBAL-ONLY
(installed in ~/.config/opencode/opencode.json or a plugins directory)
and are REJECTED in project output.

Checks (stdlib only):
  1. File parses as JSON (rejects trailing commas, bad types).
  2. Top-level shape: default_agent non-empty; permission object present.
  3. V1 permission form: flat string map; V2 `permissions[]` array rejected.
  4. ZAC bash deny set present (all 8 patterns must be "deny").
  5. Project-only keys: `mcp` and `plugin` keys rejected with a
     global-path error (shared servers/plugins belong in global config).
  6. No literal secrets: any lsp `env` / formatter `environment` value not
     starting with "{env:" fails (secrets travel as placeholders only).
  7. LSP is a flat map of {name: {command: [...]}}; a `language-server`
     wrapper, `enabled`, and unknown keys are rejected. `env` is the
     only env key (LSP uses `env`, NOT `environment`).
  7b. Formatter is true|false|named map; a flat {command, extensions}
     object without a name key is rejected.
  8. Plugin entries forbidden: any `plugin` key fails (global-only).
  9. No invented values: TODO/changeme/xxx/your-value-here/foo/bar/dummy/
     placeholder (any case) and standalone "example"/"sample" are
     rejected in default_agent, instructions, formatter, lsp commands,
     agents_dir, theme, keybinds.
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
    if "mcp" in cfg:
        errors.append(
            "mcp is global-only (install in ~/.config/opencode/opencode.json); "
            "remove it from project output"
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
    if "plugin" in cfg:
        errors.append(
            "plugin is global-only (declare in ~/.config/opencode/opencode.json "
            "or a plugins directory); remove it from project output"
        )
    lsp = cfg.get("lsp")
    if lsp is not None:
        if isinstance(lsp, bool):
            pass
        elif not isinstance(lsp, dict):
            errors.append("lsp must be an object or boolean")
        else:
            if "language-server" in lsp:
                errors.append(
                    "lsp must be a flat map of servers "
                    "(e.g. {\"typescript\": {\"command\": [...]}}); "
                    "the 'language-server' wrapper is forbidden"
                )
            else:
                for srv_name, srv_spec in lsp.items():
                    if srv_spec == {"disabled": True}:
                        continue
                    if not isinstance(srv_spec, dict):
                        errors.append(
                            f"lsp[{srv_name}] must be an object"
                        )
                        continue
                    if "enabled" in srv_spec:
                        errors.append(
                            f"lsp[{srv_name}] uses unknown key 'enabled'; "
                            "use 'disabled' instead"
                        )
                    if "environment" in srv_spec:
                        errors.append(
                            f"lsp[{srv_name}] uses unknown key 'environment'; "
                            "LSP uses 'env'"
                        )
                    allowed = {"command", "extensions", "disabled", "env",
                               "initialization"}
                    for key in srv_spec:
                        if key not in allowed:
                            errors.append(
                                f"lsp[{srv_name}] has unknown key {key!r}"
                            )
                    cmd = srv_spec.get("command")
                    if not isinstance(cmd, list) or not cmd:
                        errors.append(
                            f"lsp[{srv_name}] needs a non-empty command list"
                        )
                    elif _has_placeholder(*cmd):
                        errors.append(
                            f"lsp[{srv_name}].command looks invented"
                        )
                    env = srv_spec.get("env", {})
                    if not isinstance(env, dict):
                        errors.append(
                            f"lsp[{srv_name}].env must be an object"
                        )
                    else:
                        for var, val in env.items():
                            if not isinstance(val, str) or not val.startswith("{env:"):
                                errors.append(
                                    f"lsp[{srv_name}].env[{var}] must be an '{{env:}}' placeholder"
                                )
                            if isinstance(val, str) and SECRET_LIKE.search(val):
                                errors.append(
                                    f"lsp[{srv_name}].env[{var}] looks like a literal secret"
                                )
    formatter = cfg.get("formatter")
    if formatter is not None:
        if isinstance(formatter, bool):
            pass
        elif not isinstance(formatter, dict):
            errors.append("formatter must be an object or boolean")
        elif "command" in formatter or "extensions" in formatter:
            errors.append(
                "formatter must be a named map "
                "(e.g. {\"spotless-java\": {\"command\": [...], "
                "\"extensions\": [\".java\"]}}); flat {command, extensions} "
                "without a name key is forbidden"
            )
        else:
            for fmt_name, fmt_spec in formatter.items():
                if not isinstance(fmt_spec, dict):
                    errors.append(
                        f"formatter[{fmt_name}] must be an object"
                    )
                    continue
                allowed = {"command", "extensions", "environment", "disabled"}
                for key in fmt_spec:
                    if key not in allowed:
                        errors.append(
                            f"formatter[{fmt_name}] has unknown key {key!r}"
                        )
                cmd = fmt_spec.get("command")
                if cmd is not None:
                    if not isinstance(cmd, list) or not cmd:
                        errors.append(
                            f"formatter[{fmt_name}].command must be a non-empty list"
                        )
                    elif _has_placeholder(*cmd):
                        errors.append(
                            f"formatter[{fmt_name}].command looks invented"
                        )
                env = fmt_spec.get("environment", {})
                if not isinstance(env, dict):
                    errors.append(
                        f"formatter[{fmt_name}].environment must be an object"
                    )
                else:
                    for var, val in env.items():
                        if not isinstance(val, str) or not val.startswith("{env:"):
                            errors.append(
                                f"formatter[{fmt_name}].environment[{var}] must be an '{{env:}}' placeholder"
                            )
                        if isinstance(val, str) and SECRET_LIKE.search(val):
                            errors.append(
                                f"formatter[{fmt_name}].environment[{var}] looks like a literal secret"
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
