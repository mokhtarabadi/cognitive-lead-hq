# Setup Guide

This document covers installation and setup for all platform tools and dependencies.

## Prerequisites

- [Node.js](https://nodejs.org/) (v18+) and npm
- [OpenCode](https://opencode.ai) (latest version)
- [uv](https://docs.astral.sh/uv/) (for Python-based MCP servers)
- [GitHub CLI](https://cli.github.com/) (`gh`) — for GitHub operations

## GitHub CLI (gh)

The [GitHub CLI](https://cli.github.com/) (`gh`) is required for GitHub operations — pull request triage, issue management, CI/CD run analysis, and API queries. See the [`github` skill](../skill-templates/github/SKILL.md) for the canonical workflow reference.

### Verify Installation

```bash
gh --version
gh auth status
```

### Install (if missing)

**Debian/Ubuntu:**

```bash
(type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
&& sudo mkdir -p -m 755 /etc/apt/keyrings \
&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y
```

**macOS:**

```bash
brew install gh
```

### Authenticate

```bash
gh auth login
```

## MCP Servers

The project uses five FastMCP Python servers, all running as supervised singletons (one process each, shared across sessions) on loopback HTTP (`MCP_TRANSPORT=streamable-http`, ports 8101–8105; telegram 8106, blowsh 8107 — see `docs/services.md`). `opencode.json` points at them via `type: "remote"` — no stdio entries remain.

| Server                                        | Purpose                                                                       | Singleton (port)              |
| --------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------- |
| `mcp-context-server`                          | `.gitignore`-aware file reading, tree exploration                             | 8102 (`mcp-context.service`)  |
| `mcp-memory-server`                           | Persistent project memory (namespaces + index)                                | 8103 (`mcp-memory.service`)   |
| `mcp-lint-server`                             | Task file linting and Markdown validation                                     | 8101 (`mcp-lint.service`)     |
| [`mcp-decision-server`](manager-decisions.md) | Manager-decision capture and consultation                                     | 8104 (`mcp-decision.service`) |
| `mcp-brain-bridge`                            | Unified Brain bridge: `brain_turn` (system-prompt loader + LLM + XML extract) | 8105 (`mcp-brain.service`)    |

Each unit launches its server via the persistent venv interpreter (`<dir>/.venv/bin/python <dir>/server.py`, never `uv run` — `uv` startup exceeds the V2 connect timeout under multi-session spawn load, 2026-09-29 fix), with `MCP_TRANSPORT=streamable-http` plus `MCP_HOST`/`MCP_PORT` in the unit environment.

> **Brain Bridge active:** QA/review run through one MCP
> (`brain_turn`).
> Global installs additionally run `blowsh` + `telegram`.

### Environment: MCP servers vs the managed OpenCode server

Two separate env paths — don't mix them:

**1. MCP servers self-load `.env`.** Each Python server reads
`<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env` at import
(first match wins; real process env wins over files; blank = unset). For a
global install that effective file is **`~/.config/opencode/.env`**; for
repo runs it is the repo-root `.env`. So keep `BRAIN_*`/`DECISION_*`/
`TELEGRAM_*` in that file (`chmod 600`) and no unit needs an
`EnvironmentFile=`. Full detail: `docs/services.md` §Credentials.

```bash
# seed/refresh the global MCP credentials file
install -m 600 .env ~/.config/opencode/.env
systemctl --user restart mcp-brain mcp-decision mcp-telegram   # after key changes
```

**2. The OpenChamber-managed OpenCode server** inherits the environment of
the shell that started it. `openchamber startup enable` snapshots that env
into the service, so export anything you want the OpenCode process itself
to see (used by `{env:VAR}` forwarding) before enabling:

```bash
export DECISION_REPO_PATH="$HOME/Develop/Projects/manager-decisions"
export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"
openchamber startup enable --port 3005 --host 127.0.0.1
```

Re-run `openchamber startup enable` after changing any env var. If you run
OpenCode as your own daemon instead, give that unit an `EnvironmentFile=`
(e.g. `EnvironmentFile=%h/.config/opencode/.env`) and restart it; the
manager runs that restart, never the Hands.

## Development Tools

```bash
# Format all Markdown files
npx prettier --write "**/*.md"

# Run tests (RTK-first: passing suites collapse to a verdict summary)
rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
```
