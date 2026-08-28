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

The project uses three FastMCP Python servers, all run via `uv`:

| Server | Purpose | Start Command |
|--------|---------|---------------|
| `mcp-context-server` | `.gitignore`-aware file reading, tree exploration | `uv run mcp-context-server/server.py` |
| `mcp-lint-server` | Task file linting and Markdown validation | `uv run mcp-lint-server/server.py` |
| `mcp-memory-server` | Persistent project memory bank | `uv run mcp-memory-server/server.py` |

These are configured in `opencode.json` and auto-start with OpenCode.

## Development Tools

```bash
# Format all Markdown files
npx prettier --write "**/*.md"

# Run tests
uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
```
