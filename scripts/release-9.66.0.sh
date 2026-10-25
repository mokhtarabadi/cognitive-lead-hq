#!/usr/bin/env bash
# Release v9.66.0 — Planner cockpit, design system, board hardening.
# Run from anywhere: the script resolves the repo root itself.
#
# ZAC lives with the agent, not with you: this script is the human path and the
# only place git add/commit/tag/push are allowed to happen for this release.
set -euo pipefail

VERSION="9.66.0"
TAG="v${VERSION}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

echo "==> repo: $REPO (branch: $(git rev-parse --abbrev-ref HEAD))"

echo "==> 1/7 bump system prompt version to ${VERSION}"
sed -i "s#<system_version>9\.65\.0</system_version>#<system_version>${VERSION}</system_version>#" \
  prompts/fragments/01-system_version.md
sed -i "s#assert shipped == \"9\.65\.0\"#assert shipped == \"${VERSION}\"#" \
  tests/test_prompt_sync.py

echo "==> 2/7 reassemble system-prompt.md"
uv run scripts/prompt-build/assemble_system_prompt.py
grep -q "<system_version>${VERSION}</system_version>" system-prompt.md

echo "==> 3/7 prompt + splitter tests"
uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette \
  python -m pytest tests/test_prompt_sync.py tests/test_mcp_servers.py -q

echo "==> 4/7 planner tests"
uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette \
  python -m pytest tests/test_planner_server.py -q

echo "==> 5/7 docs sync"
python3 scripts/check_docs_sync.py

echo "==> 6/7 deploy prompt and restart the Brain bridge"
cp system-prompt.md "$HOME/.config/opencode/system-prompt.md"
cmp -s system-prompt.md "$HOME/.config/opencode/system-prompt.md" && echo "    deployed byte-identical"
systemctl --user restart mcp-brain || true

echo "==> 7/7 commit, tag, push"
git add -A
git commit -m "release: v${VERSION} — planner cockpit, design system, board hardening" \
  -m "Closes milestone M02: Brain extraction and prompt pipeline exactness (342), planner protocol in the system prompt (340), Bootstrap/Graphite Desk surfaces with live-board hardening and jalaali-js (344), day/week/month cockpit (345), saved weekly plan state (347), ownership and nudges (346). Tasks archived under tasks/archive/, milestone recorded in tasks/milestones/M02-planner-cockpit-and-design-system.md."
git tag -a "$TAG" -m "v${VERSION} — planner cockpit and design system"
git push origin HEAD
git push origin "$TAG"

echo "==> done: ${TAG} pushed"
