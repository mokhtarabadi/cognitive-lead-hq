#!/usr/bin/env bash
# Sibling Docs: scripts/README.md | Decisions: scripts/DECISIONS.md
# OpenCode formatter guard: auto-format code and docs, skip byte-sensitive harness artifacts.
# Invoked by the opencode.json formatter with $FILE as the only argument. $FILE may be
# absolute or repo-relative; it is normalized below so the exclusion match cannot be
# bypassed by path shape.
set -euo pipefail

# Fail loud when a dispatcher is missing. The previous formatter entry referenced a
# binary absent from PATH and failed silently; a named error on stderr is the replacement.
require() {
	command -v "$1" >/dev/null 2>&1 || {
		echo "format-guard: required tool '$1' not found on PATH" >&2
		exit 1
	}
}

FILE="${1:-}"
[ -n "$FILE" ] || exit 0

# Resolve the repo root from this script's own location, never from the caller's cwd.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname -- "$SCRIPT_DIR")"

# Normalize $FILE to a canonical absolute path so a repo-relative argument still
# matches and a `..` segment cannot survive the containment check below.
require realpath
case "$FILE" in
/*) ;;
*) FILE="$REPO_ROOT/$FILE" ;;
esac
FILE="$(realpath -m -- "$FILE")"

# Byte-sensitive artifacts excluded from auto-format by Manager decision (META 417 reopen).
# The same list lives in .prettierignore, which the prettier --check gate reads, so the
# guard and the gate cannot drift apart: test_format_guard_matches_prettierignore pins it.
# The exclusion is defense in depth. Prettier has already run over these files in earlier
# rounds and their current shape is stable, so this guard keeps that shape rather than
# repairing it. - prompts/fragments/* and prompts/shared/*: source of system-prompt.md.
# - system-prompt.md and build/stage-prompts/*: assembler output, pinned by the
#   byte-identity gate. - tasks/*: files carry an injected Factual Git Diff block.
# Refuse anything that resolves outside the repo. A `..` segment or a symlinked
# root would otherwise survive the prefix strip below, match no exclusion arm,
# and reach prettier. Skip rather than fail: an out-of-workspace edit is
# already a Workspace Security violation upstream.
case "$FILE" in
"$REPO_ROOT"/*) ;;
*)
	echo "format-guard: skipping a path outside the repo: $FILE" >&2
	exit 0
	;;
esac
REL="${FILE#"$REPO_ROOT"/}"
case "$REL" in
prompts/fragments/* | prompts/shared/* | system-prompt.md | build/stage-prompts/* | tasks/*)
	exit 0
	;;
esac

case "${FILE##*.}" in
md | mdx | json | jsonc | yaml | yml | toml | xml | html | css | scss | sass | less | graphql | gql | vue | svelte)
	require npx
	npx --no-install prettier --write "$FILE"
	;;
py | pyi)
	require uvx
	uvx ruff format "$FILE"
	;;
sh | bash)
	require shfmt
	shfmt -w "$FILE"
	;;
*)
	exit 0
	;;
esac
