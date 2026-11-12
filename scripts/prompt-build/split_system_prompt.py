#!/usr/bin/env python3
# Sibling Docs: scripts/README.md | Decisions: scripts/DECISIONS.md
# /// script
# requires-python = ">=3.10"
# ///
"""
Split system-prompt.md into per-section fragments under prompts/fragments/.

Design rationale (round-trip verification):
  system-prompt.md is a generated build artifact assembled from the fragments
  in prompts/fragments/ plus shared partials in prompts/shared/. This script
  is the "disassembler": it reads the monolithic system-prompt.md and emits one
  fragment file per top-level XML tag, preserving verbatim content so that
  assemble_system_prompt.py can reconstruct a byte-identical file.

  Byte-identity contract:
    1. Every top-level tag in system-prompt.md is written to its own fragment
       file (verbatim, including its <tag>...</tag> wrapper lines).
    2. Fragments are joined with exactly one blank line ('\\n\\n') and the
       assembled output is terminated with a single trailing newline ('\\n').
       This matches the pristine file's structure (verified at authoring time).
    3. The hands_protocols fragment contains three occurrences of the
       <validation_phase>...</validation_phase> block. Rather than duplicating
       this block 3x, it is extracted to prompts/shared/validation-phase.md and
       each occurrence is replaced with an <!--INCLUDE:...--> marker. The
       shared file reproduces the block verbatim (including the wrapper tags
       and original indentation) so that include resolution is byte-identical.

Why the shared file includes the <validation_phase>...</validation_phase>
  wrapper tags and original indentation:
    The include marker replaces the ENTIRE block from <validation_phase> to
    </validation_phase> (inclusive). For the assembler to reproduce the
    original bytes, the shared file MUST contain the full block — wrapper tags
    and indentation — with only the phase name parameterized as {{NEXT_PHASE}}.
    This is the only way to satisfy the acceptance criterion that the
    assembled output is byte-identical to the pristine system-prompt.md.

Why a stack-free explicit-tag-list approach is used for parsing:
    A naive "all column-0 tags are top-level" scan is incorrect because the
    <brainstorming_protocol> block contains nested column-0 block tags
    (<workflow>, <personas>, <output_schema>, <brainstorming_session>, etc.)
    and the <personas> tag name recurs at column 0 both as a top-level tag and
    nested inside brainstorming_protocol. Instead this script uses the
    EXPLICITLY ordered list of 19 expected top-level tag names and, for each,
    finds the first column-0 opening line <tag> and the first closing line
    </tag> (at any indentation, since some nested closers are indented) after
    the previous block. This     deterministically isolates the 19 top-level blocks
    without a full XML parser, and verifies their order matches the contract.

Personas layout (stage-aware prompt routing):
    The <personas> block is special: the roster is stage-dependent, so the
    block is decomposed on split. The always-shipping part (the <personas>
    wrapper plus the <auto_load> block) is written to
    prompts/fragments/06-personas-catalog.md, and every <persona> block is
    written verbatim to prompts/fragments/personas/<slug>.md. The slice order
    is written to prompts/fragments/personas/manifest.txt, because the
    committed prompt ships the personas in a fixed narrative order (not
    alphabetical). The assembler splices the slices back into the catalog, so
    assemble(split(monolith)) stays byte-identical to the monolith.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The 19 top-level XML tags in system-prompt.md, in document order.
# This explicit ordered list is the authoritative contract for the split: the
# script verifies that these (and only these) 19 tags appear at the top level,
# in this exact order. Nested tags (e.g. <phase>/<workflow>/<personas> inside
# <brainstorming_protocol>) are part of their parent block's content and are
# NOT split out separately. Text after the last tag (the Markdown language
# policy) is captured as a final tail fragment so the round trip stays
# byte-identical.
TOP_LEVEL_TAGS: List[str] = [
    "system_version",
    "role",
    "system_context",
    "ai_objective",
    "user_input_processing",
    "personas",
    "agent_skills_registry",
    "agentic_reasoning",
    "hands_protocols",
    "execution_workflow",
    "brainstorming_protocol",
    "constraints",
    "solid_programming_mandate",
    "universal_datetime_rules",
    "immutable_financial_ledger_mandate",
    "no_manual_dto_mandate",
    "initialization",
    "communication_examples",
    "self_improvement_protocol",
]

# The top-level tag whose block is decomposed into a catalog plus slices.
PERSONAS_TAG = "personas"

# Fragment filename of the always-shipping personas catalog. The persona
# blocks themselves live in the personas slice directory.
PERSONAS_CATALOG_FILENAME = "06-personas-catalog.md"

# Directory (relative to the fragments dir) holding the persona slice files.
PERSONAS_DIR_NAME = "personas"

# Ordered index of the persona slice files inside the personas directory.
PERSONAS_MANIFEST_NAME = "manifest.txt"

# Regex patterns for locating top-level tag boundaries.
# Opening tag at column 0 (no leading whitespace), no attributes, no content:
#   e.g. "<role>", "<hands_protocols>".
_OPEN_RE = re.compile(r"^<([a-zA-Z_][a-zA-Z0-9_]*)>$")
# Closing tag at ANY indentation level — some nested closers are indented
#   e.g. "</role>" (col 0) and "  </operating_principles>" (2-space indent).
_CLOSE_RE = re.compile(r"^\s*</([a-zA-Z_][a-zA-Z0-9_]*)>$")
# Self-contained single-line tag at column 0:
#   e.g. "<system_version>8.4.5</system_version>", "<phase>...</phase>".
_SELF_RE = re.compile(r"^<([a-zA-Z_][a-zA-Z0-9_]*)>.*</\1>$")
# A persona block opener: two-space indent plus the seat name in the attribute.
#   e.g. '  <persona name="Software Architect">'.
_PERSONA_OPEN_RE = re.compile(r'^  <persona name="([^"]+)">$')
# A persona block closer: column 0, matching the opener's indentation contract.
#   e.g. "</persona>".
_PERSONA_CLOSE_RE = re.compile(r"^</persona>$")


# ---------------------------------------------------------------------------
# Core parsing
# ---------------------------------------------------------------------------


def _halt(msg: str) -> None:
    """Print a HALT message to stderr and exit non-zero.

    Used for any structural mismatch that cannot be resolved without guessing —
    the script must never silently produce a non-byte-identical split.
    """
    print(f"HALT: {msg}", file=sys.stderr)
    sys.exit(1)


def _find_block_ranges(lines: List[str]) -> List[Tuple[str, int, int]]:
    """Locate the (tag_name, start_index, end_index) for each top-level tag.

    Uses the explicit TOP_LEVEL_TAGS list in document order (19 tags). For each tag it
    finds the first column-0 opening line `<tag>` after the previous tag's
    closing line, then the first closing line `</tag>` (at any indentation)
    after that opening. This correctly handles tags whose closing lines are
    indented (e.g. `</operating_principles>` appears at 2-space indent).

    The <system_version> tag is a self-contained single-line tag and is
    handled as a special case.

    Returns:
        A list of (tag_name, start_idx, end_idx) tuples (0-indexed into *lines*).
    """
    ranges: List[Tuple[str, int, int]] = []
    pos = 0  # search cursor: never look before the previous block's end

    for tag in TOP_LEVEL_TAGS:
        if tag == "system_version":
            # Self-contained single-line tag, e.g. <system_version>8.4.5</system_version>
            found = None
            for i in range(pos, len(lines)):
                m = _SELF_RE.match(lines[i])
                if m and m.group(1) == tag:
                    found = i
                    break
            if found is None:
                _halt(f"<{tag}> self-line not found from line {pos + 1}.")
            ranges.append((tag, found, found))
            pos = found + 1
        else:
            # Opening tag at column 0 (no leading whitespace, no attributes).
            open_idx = None
            for i in range(pos, len(lines)):
                m = _OPEN_RE.match(lines[i])
                if m and m.group(1) == tag:
                    open_idx = i
                    break
            if open_idx is None:
                _halt(f"<{tag}> opening line not found from line {pos + 1}.")

            # Matching closing tag (any indentation — nested closers may be
            # indented, e.g. "  </operating_principles>").
            close_idx = None
            for i in range(open_idx + 1, len(lines)):
                m = _CLOSE_RE.match(lines[i])
                if m and m.group(1) == tag:
                    close_idx = i
                    break
            if close_idx is None:
                _halt(f"</{tag}> closing line not found after line {open_idx + 1}.")

            ranges.append((tag, open_idx, close_idx))
            pos = close_idx + 1

    return ranges


# ---------------------------------------------------------------------------
# Validation-phase extraction (hands_protocols special case)
# ---------------------------------------------------------------------------

# Matches the ENTIRE <validation_phase> ... </validation_phase> block, including
# its 2-space indentation (as it appears inside the XML code fences of the task
# templates). The content is captured verbatim so it can be written to the shared
# partial with zero text changes — guaranteeing byte-identity after include
# resolution.
#
# The closing tag is matched at ANY indentation (\s*) because the assembler
# (Task 131) normalizes pure closing-tag lines to column 0 in the generated
# artifact — the splitter must accept both the pre-normalization (indented)
# and post-normalization (column-0) forms to keep the round-trip lossless.
_VP_BLOCK_RE = re.compile(
    r"(  <validation_phase>\n.*?\n\s*</validation_phase>)",
    re.DOTALL,
)
# Extracts the phase name from the final line of a block, e.g. "Context" or
# "Discovery" from "...proceed to the Context Phase.\n".
_VP_PHASE_RE = re.compile(r"proceed to the (\w+) Phase\.\n")


def _extract_and_verify_validation_phases(
    hands_block: str,
) -> Tuple[str, str]:
    """Find the 3 validation_phase blocks inside the hands_protocols fragment.

    Performs the mandatory verification (HALT if it fails — never guess):
      - Exactly 3 occurrences exist.
      - All 3 are byte-identical EXCEPT for the final line's phase name
        (two say "Context Phase", one says "Discovery Phase" inside the
        <hands_combined_task_template>).

    Returns:
        A tuple of (shared_file_content, rewritten_hands_block) where:
          - shared_file_content is the canonical block with the phase name
            replaced by {{NEXT_PHASE}} (includes wrapper tags + indentation
            for byte-identity — see module docstring).
          - rewritten_hands_block is the hands_protocols text with each
            validation_phase block replaced by an include marker.
    """
    blocks = _VP_BLOCK_RE.findall(hands_block)
    if len(blocks) != 3:
        _halt(
            f"Expected exactly 3 <validation_phase> blocks inside "
            f"<hands_protocols>, found {len(blocks)}."
        )

    # Normalize: replace the phase name in each block's final line with a
    # placeholder so we can compare the blocks structurally (ignoring the
    # single-word phase-name difference).
    def _normalize(block: str) -> str:
        return re.sub(
            r"proceed to the \w+ Phase\.",
            "proceed to the {{PHASE}} Phase.",
            block,
        )

    normalized = [_normalize(b) for b in blocks]
    if not (normalized[0] == normalized[1] == normalized[2]):
        _halt(
            "<validation_phase> blocks are NOT identical apart from the phase name. "
            "Halting rather than guessing."
        )

    # Build the canonical shared-file content from the FIRST block: replace its
    # phase name with the {{NEXT_PHASE}} placeholder. This preserves the
    # wrapper tags and original indentation so include resolution is byte-identical.
    shared_content = re.sub(
        r"proceed to the \w+ Phase\.",
        "proceed to the {{NEXT_PHASE}} Phase.",
        blocks[0],
    )

    # Replace each validation_phase block in the hands_protocols text with an
    # include marker carrying the correct phase name. A single-pass regex
    # substitution avoids any ordering issues when two blocks share the same
    # phase name (Context appears twice).
    def _replace_vp(match: re.Match) -> str:
        block = match.group(0)
        phase_match = _VP_PHASE_RE.search(block)
        if not phase_match:
            _halt("Could not extract phase name from a <validation_phase> block.")
        phase = phase_match.group(1)
        return f"<!--INCLUDE:shared/validation-phase.md|NEXT_PHASE={phase}-->"

    rewritten = _VP_BLOCK_RE.sub(_replace_vp, hands_block)
    return shared_content, rewritten


# ---------------------------------------------------------------------------
# Personas decomposition (stage-aware prompt routing)
# ---------------------------------------------------------------------------


def _slugify_persona(name: str) -> str:
    """Turn a persona seat name into its slice-file slug.

    The slug is the routing key used by the stage manifest, so it must be
    derived deterministically from the seat name:

        "Software Architect" -> "software-architect"
        "UI/UX Designer"     -> "ui-ux-designer"
        "QA Engineer"        -> "qa-engineer"

    Args:
        name: The persona seat name (the ``name`` attribute).

    Returns:
        The lowercase kebab-case slug.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        _halt(f"Cannot derive a slice slug from the persona name {name!r}.")
    return slug


def _split_personas_block(block_text: str) -> Tuple[List[Tuple[str, List[str]]], str]:
    """Split a <personas> block into its persona blocks and the catalog.

    The block looks like this in the monolith::

        <personas>
          <persona name="Software Architect">
            ...
        </persona>

          <persona name="UI/UX Designer">
            ...
        </persona>

        <auto_load>
        ...
        </auto_load>
        </personas>

    It is decomposed into:
      - the persona blocks, VERBATIM (their lines are never reformatted), and
      - the catalog text: the <personas> wrapper plus the <auto_load> block
        plus the closing tag — the part that always ships.

    The blank lines that separate the persona blocks belong to the roster
    spacing, not to the catalog: the assembler re-creates them when it
    splices the slices back in, so the catalog starts directly with the
    <auto_load> block.

    Args:
        block_text: The verbatim <personas> block text.

    Returns:
        A tuple of (persona blocks, catalog text) where each persona block is
        a (seat name, block lines) pair.

    Raises:
        SystemExit: via _halt() when the block does not match the expected
            <personas> ... </personas> shape.
    """
    lines = block_text.split("\n")
    if not lines or lines[0] != "<personas>" or lines[-1] != "</personas>":
        _halt(
            "The <personas> block must start with '<personas>' and end with "
            "'</personas>'."
        )

    blocks: List[Tuple[str, List[str]]] = []
    tail: List[str] = []
    index = 1
    while index < len(lines) - 1:
        line = lines[index]
        opener = _PERSONA_OPEN_RE.match(line)
        if opener is None:
            # Not a persona block: this line belongs to the always-shipping
            # tail (the <auto_load> block).
            tail.append(line)
            index += 1
            continue

        # Collect the persona block up to its closing tag.
        end = index + 1
        while end < len(lines) - 1 and not _PERSONA_CLOSE_RE.match(lines[end]):
            end += 1
        if end >= len(lines) - 1:
            _halt(f"The <persona> block for {opener.group(1)!r} has no closing tag.")
        blocks.append((opener.group(1), lines[index : end + 1]))
        index = end + 1

        # Skip the blank separator lines that follow a persona block: the
        # assembler re-creates the roster spacing when it splices the slices.
        while index < len(lines) - 1 and not lines[index].strip():
            index += 1

    if not blocks:
        _halt("The <personas> block carries no <persona> block.")

    catalog = "<personas>\n" + "\n".join(tail) + "\n</personas>"
    return blocks, catalog


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _slugify_heading(line: str) -> str:
    """Turn a Markdown heading into a snake_case fragment slug.

    Only used for the trailing Markdown section, which has no tag name to
    borrow. The heading's leading ``#`` and any subtitle after ``:`` are
    dropped, and only the first three words survive, so the slug stays short
    and stable (``# Language Policy: English Inside…`` -> ``language_policy``).

    Args:
        line: The first non-empty line of the tail section.

    Returns:
        A lowercase snake_case slug, or ``"tail"`` when nothing survives.
    """
    text = line.lstrip("#").split(":", 1)[0]
    words = [re.sub(r"[^a-z0-9]+", "", word.lower()) for word in text.split()]
    words = [word for word in words if word][:3]
    return "_".join(words) or "tail"


def _verify_persona_routing(
    slice_filenames: Sequence[str], stage_manifest_path: Optional[str]
) -> None:
    """Check the split persona slices against the stage routing manifest.

    The routing manifest names the persona slice files per stage. A renamed
    seat (or a slice added/removed without touching the manifest) must fail
    loudly here: a silent drift would make the stage artifacts ship a roster
    the routing table does not know about.

    Args:
        slice_filenames: The slice filenames written by the split.
        stage_manifest_path: Path to the routing manifest, or None.

    Raises:
        SystemExit: via _halt() when the two sides disagree.
    """
    if not stage_manifest_path:
        return
    path = Path(stage_manifest_path)
    if not path.is_file():
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    declared = data.get("personas") or {}
    declared_files = {
        meta.get("file") for meta in declared.values() if isinstance(meta, dict)
    }
    declared_files.discard(None)

    missing = [name for name in slice_filenames if name not in declared_files]
    if missing:
        _halt(
            f"Persona slice file(s) {missing} are not declared in the stage "
            f"routing manifest {path}."
        )
    extra = sorted(name for name in declared_files if name not in slice_filenames)
    if extra:
        _halt(
            f"Persona slice file(s) {extra} are declared in the stage routing "
            f"manifest {path} but are missing from the <personas> block."
        )


def split_system_prompt(
    source_path: str = "system-prompt.md",
    fragments_dir: str = "prompts/fragments",
    shared_dir: str = "prompts/shared",
    manifest_path: str = "prompts/manifest.txt",
    stage_manifest_path: Optional[str] = None,
) -> List[str]:
    """Split system-prompt.md into per-tag fragment files.

    Reads the monolithic system-prompt.md, extracts the 20 top-level XML tags in
    document order as verbatim fragment files, extracts the duplicated
    <validation_phase> block into a shared partial with include markers, and
    writes a manifest listing the fragment filenames in assembly order.

    The <personas> block is decomposed: the always-shipping catalog (the
    <personas> wrapper plus the <auto_load> block) becomes
    06-personas-catalog.md, and every <persona> block becomes a verbatim
    slice in prompts/fragments/personas/<slug>.md, listed in order in
    prompts/fragments/personas/manifest.txt. The assembler splices the
    slices back in, so assemble(split(monolith)) stays byte-identical.

    Args:
        source_path: Path to the source system-prompt.md.
        fragments_dir: Output directory for per-tag fragments.
        shared_dir: Output directory for shared partials.
        manifest_path: Output path for the assembly-order manifest.
        stage_manifest_path: Optional path to the stage routing manifest.
            When present, the persona seat names found in the monolith are
            checked against the declared personas, so a renamed seat fails
            loudly instead of drifting from the routing table.

    Returns:
        A list of fragment filenames in assembly order (also written to the
        manifest).
    """
    src = Path(source_path)
    content = src.read_text(encoding="utf-8")
    lines = content.split("\n")

    # --- 1. Locate the 20 top-level block ranges ---
    ranges = _find_block_ranges(lines)
    if len(ranges) != len(TOP_LEVEL_TAGS):
        _halt(
            f"Expected {len(TOP_LEVEL_TAGS)} top-level blocks, found {len(ranges)}."  # 19 tags
        )

    # --- 2. Extract block text for each tag ---
    fragment_filenames: List[str] = []
    frag_dir = Path(fragments_dir)
    frag_dir.mkdir(parents=True, exist_ok=True)
    Path(shared_dir).mkdir(parents=True, exist_ok=True)
    Path(manifest_path).parent.mkdir(parents=True, exist_ok=True)
    personas_dir = frag_dir / PERSONAS_DIR_NAME

    # The routing manifest is optional: when it sits next to the fragments it
    # is used to verify the split persona roster against the declared
    # personas. An explicit override always wins.
    if stage_manifest_path is None:
        candidate = frag_dir.parent / "stage-manifest.json"
        stage_manifest_path = str(candidate) if candidate.is_file() else None

    # Reuse filenames already listed in an existing manifest, matched by the
    # part after the numeric prefix ("24-language_policy.md" -> "language_policy"), so a
    # rebuild does not renumber and rename every fragment on disk.
    existing_names: dict[str, str] = {}
    manifest_file = Path(manifest_path)
    if manifest_file.is_file():
        for entry in manifest_file.read_text(encoding="utf-8").splitlines():
            entry = entry.strip()
            if entry.endswith(".md") and "-" in entry:
                existing_names.setdefault(entry[:-3].split("-", 1)[1], entry)

    # Trailing Markdown after the last tagged block (the language policy) has
    # no tag of its own; capture it as a final fragment so a rebuild does not
    # silently drop the whole section.
    tail_lines = lines[ranges[-1][2] + 1 :]
    while tail_lines and not tail_lines[0].strip():
        tail_lines.pop(0)
    while tail_lines and not tail_lines[-1].strip():
        tail_lines.pop()
    has_tail = bool(tail_lines)

    for seq, (tag, start, end) in enumerate(ranges, start=1):
        block_text = "\n".join(lines[start : end + 1])

        # --- hands_protocols special case: extract + verify validation_phase ---
        if tag == "hands_protocols":
            shared_content, block_text = _extract_and_verify_validation_phases(
                block_text
            )
            shared_path = Path(shared_dir) / "validation-phase.md"
            shared_path.write_text(shared_content, encoding="utf-8")

        # --- personas special case: catalog + per-persona slices ---
        slice_filenames: List[str] = []
        if tag == PERSONAS_TAG:
            persona_blocks, block_text = _split_personas_block(block_text)
            personas_dir.mkdir(parents=True, exist_ok=True)
            for seat, block_lines in persona_blocks:
                slug = _slugify_persona(seat)
                slice_name = f"{slug}.md"
                # Verbatim block text, no trailing newline: the assembler
                # strips trailing newlines when it splices the slices in.
                (personas_dir / slice_name).write_text(
                    "\n".join(block_lines), encoding="utf-8"
                )
                slice_filenames.append(slice_name)
            # The slice order is part of the contract: the committed prompt
            # ships the personas in a fixed narrative order, so the order is
            # written to its own index file instead of being left to the
            # filesystem listing order.
            (personas_dir / PERSONAS_MANIFEST_NAME).write_text(
                "\n".join(slice_filenames) + "\n", encoding="utf-8"
            )
            _verify_persona_routing(slice_filenames, stage_manifest_path)

        # --- Write the fragment file (verbatim block text, no trailing newline) ---
        # No trailing newline: the assembler joins fragments with '\n\n' and
        # appends the file's single trailing '\n', reproducing byte-identical
        # output. A trailing newline here would create an extra blank line.
        #
        # Exception: if the source file ends with '\n\n' (a trailing blank
        # line after the last closing tag), the last fragment needs a trailing
        # '\n' so the assembler's single '\n' produces the correct '\n\n'
        # termination.
        seq_str = str(seq).zfill(2)
        if tag == PERSONAS_TAG:
            # The personas block always splits into the catalog fragment, so
            # the name never depends on the tag or the sequence number.
            filename = PERSONAS_CATALOG_FILENAME
        else:
            filename = existing_names.get(tag) or f"{seq_str}-{tag}.md"
        write_text = block_text
        if seq == len(ranges) and not has_tail and content.endswith("\n\n"):
            write_text = block_text + "\n"
        (frag_dir / filename).write_text(write_text, encoding="utf-8")
        fragment_filenames.append(filename)

    # --- 2b. The trailing Markdown fragment ---
    if has_tail:
        slug = _slugify_heading(tail_lines[0])
        seq_str = str(len(fragment_filenames) + 1).zfill(2)
        filename = existing_names.get(slug) or f"{seq_str}-{slug}.md"
        tail_text = "\n".join(tail_lines)
        if content.endswith("\n\n"):
            tail_text += "\n"
        (frag_dir / filename).write_text(tail_text, encoding="utf-8")
        fragment_filenames.append(filename)

    # --- 3. Emit the manifest (one filename per line, assembly order) ---
    Path(manifest_path).write_text(
        "\n".join(fragment_filenames) + "\n", encoding="utf-8"
    )

    return fragment_filenames


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Command-line entry point: split the default system-prompt.md.

    Usage:
      python3 split_system_prompt.py
      python3 split_system_prompt.py --source /tmp/pristine.md \
          --fragments-dir /tmp/fragments --shared-dir /tmp/shared \
          --manifest /tmp/manifest.txt
    """
    parser = argparse.ArgumentParser(
        description="Split system-prompt.md into per-tag fragments.",
    )
    parser.add_argument(
        "--source",
        default="system-prompt.md",
        help="Source monolith to split (default: system-prompt.md).",
    )
    parser.add_argument(
        "--fragments-dir",
        default="prompts/fragments",
        help="Output directory for per-tag fragments (default: prompts/fragments).",
    )
    parser.add_argument(
        "--shared-dir",
        default="prompts/shared",
        help="Output directory for shared partials (default: prompts/shared).",
    )
    parser.add_argument(
        "--manifest",
        default="prompts/manifest.txt",
        help="Output path for the assembly-order manifest (default: "
        "prompts/manifest.txt).",
    )
    parser.add_argument(
        "--stage-manifest",
        default=None,
        help="Path to the stage routing manifest used to verify the persona "
        "roster (default: prompts/stage-manifest.json when present).",
    )
    args = parser.parse_args()

    fragments = split_system_prompt(
        source_path=args.source,
        fragments_dir=args.fragments_dir,
        shared_dir=args.shared_dir,
        manifest_path=args.manifest,
        stage_manifest_path=args.stage_manifest,
    )
    print(f"Split system-prompt.md into {len(fragments)} fragments:")
    for f in fragments:
        print(f"  {Path(args.fragments_dir) / f}")
    personas_dir = Path(args.fragments_dir) / PERSONAS_DIR_NAME
    for slice_name in sorted(p.name for p in personas_dir.glob("*.md")):
        print(f"  {personas_dir / slice_name}")
    print(f"  {Path(args.shared_dir) / 'validation-phase.md'}")
    print(f"  {args.manifest}")


if __name__ == "__main__":
    main()
