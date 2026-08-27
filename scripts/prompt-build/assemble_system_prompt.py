#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Assemble system-prompt.md from per-section fragments under prompts/fragments/.

Design rationale (round-trip verification):
  system-prompt.md is a GENERATED build artifact. This script is the
  "assembler": it reads prompts/manifest.txt (the ordered list of fragment
  filenames), concatenates the corresponding fragment files in order, resolves
  any <!--INCLUDE:path|PARAM=value--> markers by substituting {{PARAM}}
  placeholders in the referenced shared partial, and writes the result to the
  caller-specified output path.

  The default output path is the real system-prompt.md. During verification
  (the round-trip diff check), callers pass --output /tmp/... so the real file
  is never overwritten before the byte-identity check passes.

  Byte-identity contract (enforced with split_system_prompt.py):
    - Fragments are joined with exactly one blank line ('\\n\\n') and terminated
      with a single trailing newline ('\\n'), reproducing the pristine file's
      structure.
    - Include markers replace entire blocks (e.g. the 3 <validation_phase>
      blocks in hands_protocols) with <!--INCLUDE:shared/validation-phase.md|...>
      markers. The referenced shared file contains the full original block
      (wrapper tags + indentation) with only the phase name parameterized as
      {{NEXT_PHASE}}, so substitution reproduces the original bytes exactly.

Include-marker format:
    <!--INCLUDE:<path>|<PARAM1>=<value1>|<PARAM2>=<value2>-->
    The <path> is relative to the prompts/ directory (e.g.
    "shared/validation-phase.md" resolves to prompts/shared/validation-phase.md).
    Each {{PARAM}} placeholder in the shared file is replaced by its value.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List

# ---------------------------------------------------------------------------
# Include-marker resolution
# ---------------------------------------------------------------------------

# Matches an include-marker comment, e.g.:
#   <!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->
# Group 1 = path (relative to prompts/), group 2 = pipe-separated params.
_INCLUDE_RE = re.compile(
    r"<!--INCLUDE:([^|]+?)(?:\|([^>]*))?-->"
)
# Matches a {{PARAM}} placeholder in shared-file content.
_PARAM_RE = re.compile(r"\{\{([A-Z_]+)\}\}")


def _safe_include_path(rel_path: str, prompts_dir: Path) -> Path:
    """Resolve an include-marker path and enforce the prompts/ security boundary.

    The include-path contract is:
      1. Absolute include paths are rejected outright — the assembler never
         reads from outside the prompt source tree based on a marker-supplied
         absolute path. The file system root is not part of the include API.
      2. The candidate path is resolved to its canonical absolute form
         (collapsing any '..' segments, symlinks, and redundant separators)
         via Path.resolve().
      3. The resolved path MUST remain inside the resolved prompts_dir.
         A marker like ``../outside.md`` resolves to a sibling of prompts/ and
         is therefore a path-traversal attempt — it is rejected with a
         ValueError. This is the same trust boundary pattern used by the
         custom_context MCP server (path traversal prevention).

    Why this enforcement matters: fragments/shared partials are machine-
    authored and may come from third-party skills or user paste operations.
    A malicious or buggy include marker must never be able to read arbitrary
    files from the host file system and inject their content into the
    generated system-prompt.md (which is subsequently pasted into AI chat
    interfaces). Failing loudly with ValueError (rather than silently reading
    or silently skipping) keeps the failure visible and actionable.

    Args:
        rel_path: The include-marker path fragment, stripped of surrounding
            whitespace (relative to prompts_dir by contract).
        prompts_dir: The resolved prompts/ directory that include paths must
            stay inside.

    Returns:
        The resolved, validated absolute Path of the shared file.

    Raises:
        ValueError: if the path is absolute or resolves outside prompts_dir.
    """
    # Reject absolute include paths: only relative paths are part of the API.
    stripped = rel_path.strip()
    if Path(stripped).is_absolute():
        raise ValueError(
            f"Unsafe include path {rel_path!r}: absolute include paths are not "
            f"allowed; include paths must be relative to prompts/."
        )

    # Resolve the candidate to its canonical absolute form (collapses '..').
    resolved_prompts = prompts_dir.resolve()
    candidate = (resolved_prompts / stripped).resolve()

    # Enforce the security boundary: candidate must remain inside prompts/.
    if candidate != resolved_prompts and resolved_prompts not in candidate.parents:
        raise ValueError(
            f"Unsafe include path {rel_path!r}: resolves to {candidate}, outside "
            f"the prompts/ directory ({resolved_prompts}). Include paths must "
            f"stay inside prompts/."
        )

    return candidate


def _safe_fragment_path(filename: str, fragments_dir: Path) -> Path:
    """Resolve a manifest entry and enforce the fragments/ security boundary.

    The manifest is an UNTRUSTED INPUT SURFACE: it is a plain text list of
    fragment filenames that the assembler then reads from fragments_dir. Like
    the shared-include path, the manifest must never be able to point the
    assembler at an arbitrary file outside prompts/fragments/.

    The manifest-entry contract is:
      1. Empty entries (after stripping) are rejected outright — a blank
         manifest line is a configuration error, not something to silently
         skip.
      2. Absolute manifest entries are rejected — the manifest API only
         contains filenames relative to fragments_dir.
      3. The candidate is resolved to its canonical absolute form (collapsing
         any '..' segments, symlinks, and redundant separators) via
         Path.resolve().
      4. The resolved path MUST remain inside the resolved fragments_dir.
         A manifest entry like ``../outside.md`` resolves to a sibling of
         fragments/ and is a path-traversal attempt — rejected with ValueError.

    Why this enforcement matters: the same threat model as _safe_include_path()
    applies — machine-authored manifests (from skills, user paste operations,
    or task-generated content) must never trick the assembler into reading and
    inlining arbitrary host files into the generated system-prompt.md. Failing
    loudly with ValueError keeps the failure visible and actionable.

    Args:
        filename: A manifest entry, already stripped of surrounding whitespace.
        fragments_dir: The fragments directory that manifest entries must stay
            inside.

    Returns:
        The resolved, validated absolute Path of the fragment file.

    Raises:
        ValueError: if the entry is empty, absolute, or resolves outside
            fragments_dir.
    """
    # Reject empty manifest entries after stripping.
    stripped = filename.strip()
    if not stripped:
        raise ValueError(
            "Unsafe manifest entry: empty manifest entry is not allowed; "
            "each manifest line must name a fragment file."
        )

    # Reject absolute manifest entries: only relative filenames are part of
    # the manifest API.
    if Path(stripped).is_absolute():
        raise ValueError(
            f"Unsafe manifest entry {stripped!r}: absolute manifest entries are "
            f"not allowed; manifest entries must be relative to fragments/."
        )

    # Resolve the candidate to its canonical absolute form (collapses '..').
    resolved_fragments = fragments_dir.resolve()
    candidate = (resolved_fragments / stripped).resolve()

    # Enforce the security boundary: candidate must remain inside fragments/.
    if candidate != resolved_fragments and resolved_fragments not in candidate.parents:
        raise ValueError(
            f"Unsafe manifest entry {stripped!r}: resolves to {candidate}, "
            f"outside the fragments/ directory ({resolved_fragments}). Manifest "
            f"entries must stay inside fragments/."
        )

    return candidate


def _resolve_includes(text: str, prompts_dir: Path) -> str:
    """Resolve all <!--INCLUDE:--> markers in *text*.

    For each marker, validates the include path via _safe_include_path()
    (rejecting absolute paths and parent-directory traversal outside
    prompts/), reads the referenced shared file, substitutes {{PARAM}}
    placeholders with the values supplied in the marker, and replaces the
    marker with the resulting text.

    The shared file is read AS-IS (including any indentation or wrapper tags)
    so that include resolution is byte-identical to the original embedded text.

    Args:
        text: Text that may contain include-marker comments.
        prompts_dir: The prompts/ directory that include paths are
            resolved against (e.g. "shared/validation-phase.md" ->
            prompts_dir / "shared" / "validation-phase.md").

    Returns:
        The text with all include markers substituted by their resolved
        content.
    """
    def _replace(match: re.Match) -> str:
        rel_path = match.group(1)
        params_str = match.group(2) or ""

        # Parse the pipe-separated params: "PARAM1=value1|PARAM2=value2"
        params: dict[str, str] = {}
        if params_str:
            for token in params_str.split("|"):
                if "=" in token:
                    key, value = token.split("=", 1)
                    params[key] = value

        # Read the shared file (path relative to prompts/). The path is
        # validated against the prompts/ security boundary before reading —
        # path traversal via '..' or absolute paths is rejected here.
        shared_path = _safe_include_path(rel_path, prompts_dir)
        shared_content = shared_path.read_text(encoding="utf-8")

        # Substitute each {{PARAM}} placeholder with its value.
        for key, value in params.items():
            shared_content = shared_content.replace(f"{{{{{key}}}}}", value)

        return shared_content

    return _INCLUDE_RE.sub(_replace, text)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def assemble(
    output_path: str = "system-prompt.md",
    fragments_dir: str = "prompts/fragments",
    shared_dir: str = "prompts/shared",
    manifest_path: str = "prompts/manifest.txt",
) -> str:
    """Assemble system-prompt.md from fragments and include markers.

    Reads the manifest (ordered fragment filenames), reads each fragment from
    fragments_dir, resolves any include markers, and joins all fragments with
    a single blank line. A trailing newline is appended so the output is
    byte-identical to the pristine monolith.

    Args:
        output_path: Where to write the assembled prompt (default: the real
            system-prompt.md; pass a temp path for verification).
        fragments_dir: Directory containing per-tag fragment files.
        shared_dir: Directory containing shared partials (used by include
            resolution; the manifest's include paths are relative to the
            parent prompts/ dir).
        manifest_path: Path to the assembly-order manifest.

    Returns:
        The assembled system-prompt text (also written to output_path).
    """
    frag_dir = Path(fragments_dir)
    prompts_dir = frag_dir.parent  # fragments/ lives under prompts/, so parent is prompts/

    # Read the ordered manifest.
    manifest = Path(manifest_path).read_text(encoding="utf-8").splitlines()
    filenames = [line.strip() for line in manifest if line.strip()]

    # Read each fragment and resolve include markers inline.
    parts: List[str] = []
    # Regex to detect any unresolved {{PLACEHOLDER}} patterns (uppercase
    # alphanumeric/underscore inside double braces) after include resolution.
    _UNRESOLVED_PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}")
    for filename in filenames:
        # The manifest is an untrusted input surface: validate every entry
        # against the fragments/ security boundary BEFORE reading (rejects
        # empty, absolute, and path-traversal entries like '../outside.md').
        fragment_path = _safe_fragment_path(filename, frag_dir)
        fragment = fragment_path.read_text(encoding="utf-8")
        fragment = _resolve_includes(fragment, prompts_dir)
        # Guard 1: fail loudly if any literal include marker remains after
        # resolution. A marker that _resolve_includes() could not match (e.g.
        # a malformed closing sequence like `--!>` instead of `-->`, a broken
        # `<!--INCLUDE:` prefix, or a typo) would otherwise leak verbatim into
        # the generated system-prompt.md — and from there into every chat
        # session's context. Detecting the literal `<!--INCLUDE:` substring
        # catches ALL unresolved/malformed markers regardless of their exact
        # corruption, and naming the fragment makes the failure actionable.
        # This check intentionally runs BEFORE the placeholder guard below so
        # a malformed marker is reported as what it is (a marker problem), not
        # misdiagnosed as a missing placeholder parameter.
        if "<!--INCLUDE:" in fragment:
            raise ValueError(
                f"Unresolved include marker in fragment {filename}: a fragment "
                f"still contains the literal '<!--INCLUDE:' marker after "
                f"resolution. The marker is malformed or unresolved and must "
                f"never leak into the generated system-prompt.md."
            )
        # Guard 2: fail loudly if any {{PLACEHOLDER}} remains unresolved.
        # This catches cases where a shared partial contains a placeholder
        # that no include marker supplies a value for — a silent pass-through
        # would produce a corrupted system-prompt.md with literal placeholder
        # text. Raising ValueError here is a loud, named failure rather than
        # a silent data corruption or a bare assert.
        unresolved = _UNRESOLVED_PLACEHOLDER_RE.search(fragment)
        if unresolved:
            raise ValueError(
                f"Unresolved placeholder {unresolved.group(0)} in fragment {filename} "
                f"— an include marker is missing a required PARAM."
            )
        # Strip trailing whitespace from each fragment to match the
        # splitter's extraction: split_system_prompt.py produces fragments
        # without trailing newlines (lines[start:end+1] joined with '\n').
        # The Write tool adds trailing newlines to fragment files, so we
        # must strip them before joining to avoid extra blank lines in the
        # assembled output.
        parts.append(fragment.rstrip("\n"))

    # Join with one blank line between fragments, terminate with a single
    # trailing newline — this reproduces the pristine file's structure.
    assembled = "\n\n".join(parts) + "\n"

    # Write the assembled output.
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(assembled, encoding="utf-8")

    return assembled


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Command-line entry point for assembling system-prompt.md.

    Usage:
      python3 assemble_system_prompt.py                       # writes system-prompt.md
      python3 assemble_system_prompt.py --output /tmp/assembled.md  # writes to temp
    """
    parser = argparse.ArgumentParser(
        description="Assemble system-prompt.md from prompts/fragments/.",
    )
    parser.add_argument(
        "--output",
        default="system-prompt.md",
        help="Output path (default: system-prompt.md). Use a temp path for "
        "verification before overwriting the real file.",
    )
    args = parser.parse_args()

    result = assemble(output_path=args.output)
    out = Path(args.output)
    print(f"Assembled {len(result)} bytes -> {out}")


if __name__ == "__main__":
    main()
