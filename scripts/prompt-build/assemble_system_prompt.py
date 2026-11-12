#!/usr/bin/env python3
# Sibling Docs: scripts/README.md | Decisions: scripts/DECISIONS.md
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

Stage mode (per-stage prompt artifacts):
    The Brain prompt ships a shared COMMON core plus a stage-scoped persona
    roster. The always-shipping part lives in the personas catalog fragment
    (06-personas-catalog.md: the <personas> wrapper plus the <auto_load>
    block); the seven <persona> blocks live as verbatim slices in
    prompts/fragments/personas/<slug>.md, listed in canonical catalog order
    by prompts/fragments/personas/manifest.txt.

    The assembler splices the persona blocks into the catalog at build time:
    <personas> + <persona block> ... + <auto_load> ... + </personas>. The
    persona order for the FULL prompt comes from the personas manifest; the
    persona order for a STAGE artifact comes from the stage routing manifest
    (prompts/stage-manifest.json), which is the single source of truth shared
    with the Brain bridge (mcp-brain-bridge/server.py).

    Byte-identity contract (stage mode):
      - A stage artifact is the common fragments verbatim plus the stage's
        own persona roster, so the "brainstorm" stage (all seven personas)
        is byte-identical to the full prompt.
      - The output is byte-stable: the same inputs always produce the same
        bytes (no timestamps, no dict-order dependence, no random ids).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Include-marker resolution
# ---------------------------------------------------------------------------

# Matches an include-marker comment, e.g.:
#   <!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->
# Group 1 = path (relative to prompts/), group 2 = pipe-separated params.
_INCLUDE_RE = re.compile(r"<!--INCLUDE:([^|]+?)(?:\|([^>]*))?-->")
# Matches a {{PARAM}} placeholder in shared-file content.
_PARAM_RE = re.compile(r"\{\{([A-Z_]+)\}\}")

# Regex to detect any unresolved {{PLACEHOLDER}} patterns (uppercase
# alphanumeric/underscore inside double braces) after include resolution.
_UNRESOLVED_PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}")

# ---------------------------------------------------------------------------
# Stage routing constants
# ---------------------------------------------------------------------------

#: Always-shipping personas catalog fragment: the <personas> wrapper plus the
#: <auto_load> block. The <persona> blocks themselves are slice files.
PERSONAS_CATALOG_FILENAME = "06-personas-catalog.md"

#: Directory (relative to the fragments dir) holding the persona slice files.
PERSONAS_DIR_NAME = "personas"

#: Ordered index of the persona slice files inside the personas directory.
#: It mirrors prompts/manifest.txt for the slice level and keeps the full
#: prompt byte-identical to the monolith (persona order is not alphabetical).
PERSONAS_MANIFEST_NAME = "manifest.txt"

#: Routing manifest (stage -> persona roster -> artifact) inside prompts/.
STAGE_MANIFEST_FILENAME = "stage-manifest.json"

#: Stage routing manifest schema version this assembler understands.
STAGE_MANIFEST_SCHEMA_VERSION = 1

#: Default directory for the generated per-stage artifacts.
DEFAULT_STAGE_ARTIFACT_DIR = "build/stage-prompts"


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
# Persona slices and stage routing
# ---------------------------------------------------------------------------


def _assert_resolved(fragment: str, label: str) -> None:
    """Fail loudly when a fragment still carries an include marker or a placeholder.

    Two guards, both applied to every assembled fragment AND to every persona
    slice file:

      1. A literal ``<!--INCLUDE:`` substring means an include marker was
         malformed or unresolved. It would otherwise leak verbatim into the
         generated prompt. The literal-substring check catches every malformed
         variant (broken prefix, corrupted closing sequence, typo).
      2. A surviving ``{{PLACEHOLDER}}`` means a shared partial was included
         without one of its required PARAM values — a silent pass-through
         would corrupt the generated prompt with literal placeholder text.

    Args:
        fragment: The resolved fragment text.
        label: Human-readable name of the source (used in the error message).

    Raises:
        ValueError: if an include marker or a placeholder survives.
    """
    # Guard 1: any surviving include marker is a marker problem, not a
    # placeholder problem — report it as such.
    if "<!--INCLUDE:" in fragment:
        raise ValueError(
            f"Unresolved include marker in fragment {label}: a fragment "
            f"still contains the literal '<!--INCLUDE:' marker after "
            f"resolution. The marker is malformed or unresolved and must "
            f"never leak into the generated system-prompt.md."
        )
    # Guard 2: any surviving placeholder is a missing include parameter.
    unresolved = _UNRESOLVED_PLACEHOLDER_RE.search(fragment)
    if unresolved:
        raise ValueError(
            f"Unresolved placeholder {unresolved.group(0)} in fragment {label} "
            f"— an include marker is missing a required PARAM."
        )


def _personas_dir(fragments_dir: Path) -> Path:
    """Return the persona-slice directory for a fragments directory."""
    return fragments_dir / PERSONAS_DIR_NAME


def persona_slice_order(personas_dir: Path) -> List[str]:
    """Return the persona slice filenames in canonical catalog order.

    The order is declared by the personas manifest (``manifest.txt`` inside
    the personas directory), NOT by the filesystem listing: the committed
    prompt ships the personas in a fixed narrative order, and an alphabetical
    listing would silently reorder them and break byte-identity.

    Args:
        personas_dir: Directory holding the persona slice files.

    Returns:
        The slice filenames in catalog order.

    Raises:
        FileNotFoundError: if the personas manifest or a listed slice is
            missing.
        ValueError: if the personas manifest is empty, or if a slice file on
            disk is not listed (an orphan slice would ship nowhere).
    """
    manifest = personas_dir / PERSONAS_MANIFEST_NAME
    if not manifest.is_file():
        raise FileNotFoundError(
            f"Personas manifest not found: {manifest}. The personas catalog "
            f"needs the ordered persona slice index."
        )

    names = [
        line.strip()
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not names:
        raise ValueError(f"Personas manifest {manifest} lists no persona slices.")

    # Guard: every slice file on disk must be listed. An unlisted slice would
    # ship in no artifact at all — a silent content loss.
    on_disk = sorted(p.name for p in personas_dir.glob("*.md"))
    orphans = [name for name in on_disk if name not in names]
    if orphans:
        raise ValueError(
            f"Persona slice file(s) not listed in {manifest}: {orphans}. Every "
            f"slice must be declared in the personas manifest."
        )

    # Guard: every listed slice must exist on disk.
    missing = [name for name in names if not (personas_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(
            f"Persona slice file(s) listed in {manifest} but missing on disk: "
            f"{missing}."
        )

    return names


def _read_persona_blocks(personas_dir: Path, filenames: Sequence[str]) -> List[str]:
    """Read persona slice files and return their verbatim block texts.

    Each slice holds exactly one ``<persona name="...">...</persona>`` block.
    The text is kept VERBATIM (only trailing newlines are stripped, because
    the assembler joins fragments with a single blank line). A single changed
    byte inside a persona body would change the shipped prompt, so the
    include/placeholder guards run on every slice too.

    Args:
        personas_dir: Directory holding the persona slice files.
        filenames: Slice filenames to read, in the order they must ship.

    Returns:
        The persona block texts, in the requested order.
    """
    blocks: List[str] = []
    for name in filenames:
        # The slice index is machine-authored content: keep it inside the
        # personas directory (no absolute paths, no '..' traversal).
        path = _safe_fragment_path(name, personas_dir)
        text = path.read_text(encoding="utf-8")
        _assert_resolved(text, f"{PERSONAS_DIR_NAME}/{name}")
        blocks.append(text.rstrip("\n"))
    return blocks


def _splice_persona_blocks(catalog_text: str, blocks: Sequence[str]) -> str:
    """Insert persona blocks into the personas catalog.

    The catalog holds the ``<personas>`` wrapper, the ``<auto_load>`` block
    and the closing tag — the part that always ships. The persona blocks go
    right after the ``<personas>`` opening line, separated by a single blank
    line, so the result reproduces the monolith byte-for-byte:

        <personas>
        <persona block 1>

        <persona block 2>

        <auto_load>
        ...

    Args:
        catalog_text: The catalog fragment text (without trailing newline).
        blocks: The persona block texts to splice in, in shipping order.

    Returns:
        The catalog text with the persona blocks inserted.

    Raises:
        ValueError: if the catalog does not start with the ``<personas>``
            opening line (the splice point would be ambiguous).
    """
    if not blocks:
        # No persona for this stage: ship the catalog as-is.
        return catalog_text

    opening = "<personas>\n"
    if not catalog_text.startswith(opening):
        raise ValueError(
            "The personas catalog must start with the '<personas>' opening "
            "line; the persona blocks are spliced in directly after it."
        )

    # One blank line between persona blocks and one blank line before the
    # <auto_load> block — the exact spacing of the committed monolith.
    return opening + "\n\n".join(blocks) + "\n\n" + catalog_text[len(opening) :]


def load_stage_manifest(stage_manifest_path: str | Path) -> Dict[str, object]:
    """Load the stage routing manifest and validate its shape.

    The manifest is the single routing table for the assembler and for the
    Brain bridge: it declares the common fragments, the personas catalog, the
    persona roster, and the per-stage persona list plus artifact filename.

    Args:
        stage_manifest_path: Path to the routing manifest JSON file.

    Returns:
        The parsed manifest dictionary.

    Raises:
        FileNotFoundError: if the manifest file does not exist.
        ValueError: if the manifest is not a JSON object, carries an unknown
            schema version, or misses a required section.
    """
    path = Path(stage_manifest_path)
    if not path.is_file():
        raise FileNotFoundError(f"Stage manifest not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Stage manifest {path} must contain a JSON object.")

    version = data.get("schema_version")
    if version != STAGE_MANIFEST_SCHEMA_VERSION:
        raise ValueError(
            f"Stage manifest {path} declares schema_version {version!r}; this "
            f"assembler understands {STAGE_MANIFEST_SCHEMA_VERSION}. Refusing "
            f"to guess the schema."
        )

    for key in ("common_fragments", "personas", "stages"):
        if key not in data:
            raise ValueError(f"Stage manifest {path} is missing the {key!r} section.")

    return data


def resolve_stage_manifest_path(
    prompts_dir: Path, stage_manifest_path: Optional[str] = None
) -> Optional[Path]:
    """Resolve the routing manifest path, or None when there is no manifest.

    An explicit override always wins. Otherwise the manifest is looked up
    next to the fragments (prompts/stage-manifest.json). A missing manifest is
    NOT an error for the full-prompt assembly (the personas order comes from
    the personas manifest); stage mode requires the manifest and fails loudly.

    Args:
        prompts_dir: The prompts/ directory that owns the manifest.
        stage_manifest_path: Optional explicit override path.

    Returns:
        The manifest path, or None when it does not exist.
    """
    if stage_manifest_path:
        return Path(stage_manifest_path)
    candidate = prompts_dir / STAGE_MANIFEST_FILENAME
    return candidate if candidate.is_file() else None


def stage_artifact_path(
    stage: str,
    stage_manifest: Dict[str, object],
    artifact_dir: Optional[str] = None,
) -> Path:
    """Return the artifact path of a stage.

    The bridge resolves the same path from the same manifest, so the
    assembler and the bridge never disagree about where a stage artifact
    lives.

    Args:
        stage: The stage key (e.g. "qa").
        stage_manifest: The parsed routing manifest.
        artifact_dir: Optional override of the artifact directory.

    Returns:
        The path of the stage artifact.

    Raises:
        KeyError: if the stage is not declared in the manifest.
    """
    stages = stage_manifest.get("stages") or {}
    if stage not in stages:
        raise KeyError(f"Unknown stage {stage!r}; declared stages: {sorted(stages)}.")
    entry = stages[stage]  # type: ignore[index]
    filename = entry["artifact"]  # type: ignore[index]
    directory = artifact_dir or entry.get("artifact_dir") or DEFAULT_STAGE_ARTIFACT_DIR
    return Path(directory) / filename  # type: ignore[operator]


def _persona_filenames_for_slugs(
    slugs: Sequence[str], personas: Dict[str, object]
) -> List[str]:
    """Map persona slugs to their slice filenames.

    Args:
        slugs: The persona slugs, in shipping order.
        personas: The manifest's personas map (slug -> {name, file}).

    Returns:
        The persona slice filenames in the given order.

    Raises:
        ValueError: if a slug is not declared in the personas map.
    """
    filenames: List[str] = []
    for slug in slugs:
        meta = personas.get(slug)
        if meta is None:
            raise ValueError(
                f"Persona slug {slug!r} is not declared in the personas map."
            )
        filenames.append(meta.get("file") or f"{slug}.md")  # type: ignore[union-attr]
    return filenames


def _stage_persona_filenames(
    stage: str, stage_manifest: Dict[str, object]
) -> List[str]:
    """Return the persona slice filenames a stage carries, in shipping order.

    Args:
        stage: The stage key.
        stage_manifest: The parsed routing manifest.

    Returns:
        The persona slice filenames in the order declared for the stage.

    Raises:
        KeyError: if the stage is not declared.
        ValueError: if the stage references a persona slug the manifest does
            not declare.
    """
    stages = stage_manifest.get("stages") or {}
    if stage not in stages:
        raise KeyError(f"Unknown stage {stage!r}; declared stages: {sorted(stages)}.")
    entry = stages[stage]  # type: ignore[index]
    slugs = entry.get("personas") or []  # type: ignore[union-attr]
    if not slugs:
        # A stage with an empty roster would assemble an artifact whose
        # <personas> block holds no seat at all. That is a manifest authoring
        # error, not a valid configuration: every declared stage must carry
        # at least one persona, otherwise the Brain would receive a prompt
        # with no role definition.
        raise ValueError(
            f"Stage {stage!r} declares an empty persona roster; "
            f"every stage must carry at least one persona."
        )
    personas = stage_manifest.get("personas") or {}
    return _persona_filenames_for_slugs(slugs, personas)  # type: ignore[arg-type]


def _validate_stage_manifest(
    stage_manifest: Dict[str, object],
    manifest_filenames: Sequence[str],
    personas_dir: Path,
) -> None:
    """Cross-check the routing manifest against the fragment sources.

    Two drift sources are checked, both loudly:

      1. ``common_fragments`` must equal the assembly order in
         prompts/manifest.txt. A divergence means the stage artifacts and the
         full prompt would ship different fragments — silent behavior drift.
      2. ``personas_order`` must equal the persona order in the personas
         manifest. A divergence means the stage artifacts and the full prompt
         would ship the personas in a different order.

    Args:
        stage_manifest: The parsed routing manifest.
        manifest_filenames: The fragment filenames in assembly order.
        personas_dir: Directory holding the persona slice files.

    Raises:
        ValueError: on any divergence.
    """
    common = stage_manifest.get("common_fragments")
    if common is not None and list(common) != list(manifest_filenames):
        raise ValueError(
            "Stage manifest 'common_fragments' does not match the assembly "
            f"order in the fragment manifest: {list(common)} != "
            f"{list(manifest_filenames)}. The stage artifacts and the full "
            "prompt would ship different fragments."
        )

    declared_order = stage_manifest.get("personas_order")
    if declared_order is not None:
        slice_order = [Path(name).stem for name in persona_slice_order(personas_dir)]
        if list(declared_order) != slice_order:
            raise ValueError(
                "Stage manifest 'personas_order' does not match the persona "
                f"order in the personas manifest: {list(declared_order)} != "
                f"{slice_order}. The stage artifacts and the full prompt would "
                "ship the personas in a different order."
            )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _resolve_catalog_filename(
    stage_manifest: Optional[Dict[str, object]], filenames: Sequence[str]
) -> str:
    """Resolve the name of the personas catalog fragment.

    The catalog is the fragment that carries the always-shipping personas
    wrapper; the persona blocks are spliced into it at build time.

    Args:
        stage_manifest: The parsed routing manifest (or None).
        filenames: The fragment filenames in assembly order.

    Returns:
        The catalog fragment filename.
    """
    catalog = PERSONAS_CATALOG_FILENAME
    if stage_manifest is not None:
        declared = stage_manifest.get("catalog")
        if declared:
            catalog = str(declared)
    return catalog


def _build_prompt(
    frag_dir: Path,
    prompts_dir: Path,
    filenames: Sequence[str],
    catalog_filename: str,
    persona_loader: Callable[[], Sequence[str]],
) -> str:
    """Assemble the prompt text from the fragment manifest (no file writes).

    Shared by the full prompt and the stage artifacts: the only difference
    between the two is the persona roster spliced into the catalog.

    Args:
        frag_dir: Directory holding the fragment files.
        prompts_dir: The prompts/ directory (include paths are relative to it).
        filenames: The fragment filenames in assembly order.
        catalog_filename: The personas catalog fragment filename.
        persona_loader: Zero-argument callable returning the persona blocks to
            splice into the catalog. It is called lazily (only when the
            catalog fragment is actually part of the manifest), so a fragment
            tree without a personas section assembles without touching the
            persona slices — and the per-fragment guards still fire first.

    Returns:
        The assembled prompt text, terminated with a single trailing newline.

    Raises:
        ValueError: on an unresolved include marker or placeholder, on an
            unsafe manifest entry, on a drifted closing tag, or when the
            personas catalog is missing from the manifest.
    """
    # Read each fragment and resolve include markers inline.
    parts: List[str] = []
    catalog_seen = False
    for filename in filenames:
        # The manifest is an untrusted input surface: validate every entry
        # against the fragments/ security boundary BEFORE reading (rejects
        # empty, absolute, and path-traversal entries like '../outside.md').
        fragment_path = _safe_fragment_path(filename, frag_dir)
        fragment = fragment_path.read_text(encoding="utf-8")
        fragment = _resolve_includes(fragment, prompts_dir)
        # Fail loudly on an unresolved include marker or placeholder — both
        # would otherwise leak into the generated prompt.
        _assert_resolved(fragment, filename)
        # Strip trailing whitespace from each fragment to match the
        # splitter's extraction: split_system_prompt.py produces fragments
        # without trailing newlines (lines[start:end+1] joined with '\n').
        # The Write tool adds trailing newlines to fragment files, so we
        # must strip them before joining to avoid extra blank lines in the
        # assembled output.
        fragment = fragment.rstrip("\n")
        # The personas catalog ships the <personas> wrapper and the
        # <auto_load> block; the persona blocks themselves are spliced in
        # here from the slice files, so a stage artifact can carry a
        # scoped roster while the full prompt carries all of them.
        if filename == catalog_filename:
            catalog_seen = True
            fragment = _splice_persona_blocks(fragment, persona_loader())
        parts.append(fragment)

    # The personas catalog MUST be part of the manifest: a missing catalog
    # would ship a prompt without any persona at all. The check runs after
    # the fragment loop so a broken fragment is reported as the broken
    # fragment, not as a missing catalog.
    if not catalog_seen:
        raise ValueError(
            f"The personas catalog fragment {catalog_filename!r} is not listed "
            f"in the fragment manifest ({list(filenames)})."
        )

    # Join with one blank line between fragments, terminate with a single
    # trailing newline — this reproduces the pristine file's structure.
    assembled = "\n\n".join(parts) + "\n"

    # Normalize closing-tag indentation (Task 131): Prettier passes on the
    # source fragments can indent pure closing tags (e.g. "  </constraints>")
    # which would otherwise drift into the generated artifact. This single
    # normalization point strips leading/trailing whitespace from any line
    # that consists ONLY of a closing tag, so the artifact is correct
    # regardless of whatever indentation the source fragments carry.
    _CLOSING_TAG_ONLY_RE = re.compile(r"^\s*(</[a-zA-Z_][a-zA-Z0-9_]*>)\s*$")
    normalized_lines = []
    for line in assembled.splitlines():
        match = _CLOSING_TAG_ONLY_RE.match(line)
        if match:
            normalized_lines.append(match.group(1))
        else:
            normalized_lines.append(line)
    assembled = "\n".join(normalized_lines) + "\n"

    # Self-check (Task 131): after normalization, any remaining line that is
    # an indented pure closing tag means the regex above missed a case (e.g.
    # a tag with unusual characters). Fail loudly instead of silently writing
    # a still-drifted artifact.
    _DRIFTED_CLOSING_TAG_RE = re.compile(r"^\s+</[a-zA-Z_][a-zA-Z0-9_]*>\s*$")
    for line in assembled.splitlines():
        if _DRIFTED_CLOSING_TAG_RE.match(line):
            raise ValueError(
                f"Drifted closing tag detected after normalization: {line!r}. "
                f"The closing-tag normalization regex in assemble() missed this "
                f"case — fix the regex before writing system-prompt.md."
            )

    return assembled


def assemble(
    output_path: str = "system-prompt.md",
    fragments_dir: str = "prompts/fragments",
    shared_dir: str = "prompts/shared",
    manifest_path: str = "prompts/manifest.txt",
    stage_manifest_path: Optional[str] = None,
) -> str:
    """Assemble system-prompt.md from fragments and include markers.

    Reads the manifest (ordered fragment filenames), reads each fragment from
    fragments_dir, resolves any include markers, splices the persona slices
    into the personas catalog, and joins all fragments with a single blank
    line. A trailing newline is appended so the output is byte-identical to
    the pristine monolith.

    Args:
        output_path: Where to write the assembled prompt (default: the real
            system-prompt.md; pass a temp path for verification).
        fragments_dir: Directory containing per-tag fragment files.
        shared_dir: Directory containing shared partials (used by include
            resolution; the manifest's include paths are relative to the
            parent prompts/ dir).
        manifest_path: Path to the assembly-order manifest.
        stage_manifest_path: Optional path to the stage routing manifest.
            When absent it is looked up next to the fragments; when it is
            missing entirely the full prompt still assembles (the routing
            manifest only adds cross-checks there).

    Returns:
        The assembled system-prompt text (also written to output_path).
    """
    frag_dir = Path(fragments_dir)
    prompts_dir = (
        frag_dir.parent
    )  # fragments/ lives under prompts/, so parent is prompts/
    personas_dir = _personas_dir(frag_dir)

    # The routing manifest is optional for the full prompt (it only adds
    # cross-checks) and mandatory for stage mode.
    manifest_file = resolve_stage_manifest_path(prompts_dir, stage_manifest_path)
    stage_manifest = load_stage_manifest(manifest_file) if manifest_file else None

    # The persona roster of the FULL prompt: every persona, in the order the
    # routing manifest declares. The personas manifest (the slice index) is
    # the fallback when no routing manifest is available.
    def _load_persona_blocks() -> List[str]:
        if stage_manifest is not None:
            order = stage_manifest.get("personas_order")
            if order:
                personas = stage_manifest.get("personas") or {}
                return _read_persona_blocks(
                    personas_dir,
                    _persona_filenames_for_slugs(
                        list(order),
                        personas,  # type: ignore[arg-type]
                    ),
                )
        return _read_persona_blocks(personas_dir, persona_slice_order(personas_dir))

    # Read the ordered manifest.
    manifest = Path(manifest_path).read_text(encoding="utf-8").splitlines()
    filenames = [line.strip() for line in manifest if line.strip()]

    if stage_manifest is not None:
        _validate_stage_manifest(stage_manifest, filenames, personas_dir)
    catalog_filename = _resolve_catalog_filename(stage_manifest, filenames)

    assembled = _build_prompt(
        frag_dir, prompts_dir, filenames, catalog_filename, _load_persona_blocks
    )

    # Write the assembled output.
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(assembled, encoding="utf-8")

    return assembled


def assemble_stage(
    stage: str,
    fragments_dir: str = "prompts/fragments",
    shared_dir: str = "prompts/shared",
    manifest_path: str = "prompts/manifest.txt",
    stage_manifest_path: Optional[str] = None,
    artifact_dir: Optional[str] = None,
) -> Tuple[Path, str]:
    """Assemble one stage artifact (common fragments + the stage's personas).

    The artifact carries the shared COMMON core verbatim and exactly the
    persona roster the stage declares. The output is byte-stable: the same
    sources always produce the same bytes.

    Args:
        stage: The stage key (e.g. "qa").
        fragments_dir: Directory containing per-tag fragment files.
        shared_dir: Directory containing shared partials.
        manifest_path: Path to the assembly-order manifest.
        stage_manifest_path: Optional path to the stage routing manifest.
        artifact_dir: Optional override of the artifact directory.

    Returns:
        A tuple of (artifact path, artifact text).

    Raises:
        FileNotFoundError: if the routing manifest or a persona slice is
            missing.
        KeyError: if the stage is not declared in the routing manifest.
        ValueError: on a manifest drift or an unresolved fragment marker.
    """
    frag_dir = Path(fragments_dir)
    prompts_dir = frag_dir.parent
    personas_dir = _personas_dir(frag_dir)

    manifest_file = resolve_stage_manifest_path(prompts_dir, stage_manifest_path)
    if manifest_file is None:
        raise FileNotFoundError(
            f"No stage manifest found at {prompts_dir / STAGE_MANIFEST_FILENAME}; "
            f"stage mode needs the routing manifest."
        )
    stage_manifest = load_stage_manifest(manifest_file)

    manifest = Path(manifest_path).read_text(encoding="utf-8").splitlines()
    filenames = [line.strip() for line in manifest if line.strip()]
    _validate_stage_manifest(stage_manifest, filenames, personas_dir)
    catalog_filename = _resolve_catalog_filename(stage_manifest, filenames)

    # Only the stage's own persona roster ships in this artifact.
    stage_filenames = _stage_persona_filenames(stage, stage_manifest)

    def _load_persona_blocks() -> List[str]:
        return _read_persona_blocks(personas_dir, stage_filenames)

    assembled = _build_prompt(
        frag_dir, prompts_dir, filenames, catalog_filename, _load_persona_blocks
    )

    out = stage_artifact_path(stage, stage_manifest, artifact_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(assembled, encoding="utf-8")

    return out, assembled


def assemble_stages(
    stages: Optional[Sequence[str]] = None,
    fragments_dir: str = "prompts/fragments",
    shared_dir: str = "prompts/shared",
    manifest_path: str = "prompts/manifest.txt",
    stage_manifest_path: Optional[str] = None,
    artifact_dir: Optional[str] = None,
) -> List[Tuple[Path, str]]:
    """Assemble the artifacts of every declared stage (or of a subset).

    Args:
        stages: Stage keys to build; None builds every declared stage.
        fragments_dir: Directory containing per-tag fragment files.
        shared_dir: Directory containing shared partials.
        manifest_path: Path to the assembly-order manifest.
        stage_manifest_path: Optional path to the stage routing manifest.
        artifact_dir: Optional override of the artifact directory.

    Returns:
        A list of (artifact path, artifact text) tuples, in manifest order.
    """
    frag_dir = Path(fragments_dir)
    prompts_dir = frag_dir.parent

    manifest_file = resolve_stage_manifest_path(prompts_dir, stage_manifest_path)
    if manifest_file is None:
        raise FileNotFoundError(
            f"No stage manifest found at {prompts_dir / STAGE_MANIFEST_FILENAME}; "
            f"stage mode needs the routing manifest."
        )
    stage_manifest = load_stage_manifest(manifest_file)
    declared = list((stage_manifest.get("stages") or {}).keys())

    selected = list(stages) if stages else declared
    unknown = [stage for stage in selected if stage not in declared]
    if unknown:
        raise KeyError(
            f"Unknown stage(s) {unknown}; declared stages: {sorted(declared)}."
        )

    return [
        assemble_stage(
            stage,
            fragments_dir=fragments_dir,
            shared_dir=shared_dir,
            manifest_path=manifest_path,
            stage_manifest_path=str(manifest_file),
            artifact_dir=artifact_dir,
        )
        for stage in selected
    ]


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Command-line entry point for assembling system-prompt.md.

    Usage:
      python3 assemble_system_prompt.py                       # writes system-prompt.md
      python3 assemble_system_prompt.py --output /tmp/assembled.md  # writes to temp
      python3 assemble_system_prompt.py --stages               # writes every stage artifact
      python3 assemble_system_prompt.py --stage qa             # writes one stage artifact
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
    parser.add_argument(
        "--fragments-dir",
        default="prompts/fragments",
        help="Directory holding the fragment files (default: prompts/fragments).",
    )
    parser.add_argument(
        "--shared-dir",
        default="prompts/shared",
        help="Directory holding the shared partials (default: prompts/shared).",
    )
    parser.add_argument(
        "--manifest",
        default="prompts/manifest.txt",
        help="Assembly-order manifest (default: prompts/manifest.txt).",
    )
    parser.add_argument(
        "--stages",
        action="store_true",
        help="Emit one artifact per declared stage into the stage artifact "
        "directory (default: build/stage-prompts).",
    )
    parser.add_argument(
        "--stage",
        metavar="KEY",
        help="Emit only the artifact of the given stage key (e.g. qa).",
    )
    parser.add_argument(
        "--stage-dir",
        metavar="DIR",
        help="Override the stage artifact directory (default: from the routing "
        "manifest).",
    )
    parser.add_argument(
        "--stage-manifest",
        metavar="PATH",
        help="Path to the stage routing manifest (default: "
        "prompts/stage-manifest.json).",
    )
    args = parser.parse_args()

    if args.stage and args.stages:
        parser.error("--stage and --stages are mutually exclusive.")

    # Stage mode: build the per-stage artifacts. The full prompt keeps its
    # own invocation (no flags) so the committed artifact stays untouched.
    if args.stage or args.stages:
        written = assemble_stages(
            stages=[args.stage] if args.stage else None,
            fragments_dir=args.fragments_dir,
            shared_dir=args.shared_dir,
            manifest_path=args.manifest,
            stage_manifest_path=args.stage_manifest,
            artifact_dir=args.stage_dir,
        )
        for path, text in written:
            print(f"Assembled stage artifact {len(text)} bytes -> {path}")
        return

    result = assemble(
        output_path=args.output,
        fragments_dir=args.fragments_dir,
        shared_dir=args.shared_dir,
        manifest_path=args.manifest,
        stage_manifest_path=args.stage_manifest,
    )
    out = Path(args.output)
    print(f"Assembled {len(result)} bytes -> {out}")


if __name__ == "__main__":
    main()
