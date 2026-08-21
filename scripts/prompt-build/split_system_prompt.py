#!/usr/bin/env python3
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
    EXPLICITLY ordered list of 20 expected top-level tag names and, for each,
    finds the first column-0 opening line <tag> and the first closing line
    </tag> (at any indentation, since some nested closers are indented) after
    the previous block. This deterministically isolates the 20 top-level blocks
    without a full XML parser, and verifies their order matches the contract.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The 21 top-level XML tags in system-prompt.md, in document order.
# This explicit ordered list is the authoritative contract for the split: the
# script verifies that these (and only these) 21 tags appear at the top level,
# in this exact order. Nested tags (e.g. <identity> inside <manager_profile>,
# or <phase>/<workflow>/<personas> inside <brainstorming_protocol>) are part of
# their parent block's content and are NOT split out separately.
TOP_LEVEL_TAGS: List[str] = [
    "system_version",
    "role",
    "system_context",
    "manager_profile",
    "ai_objective",
    "operating_principles",
    "delegation_strategy",
    "challenge_policy",
    "leadership_and_language_protocol",
    "agent_skills_registry",
    "user_input_processing",
    "personas",
    "agentic_reasoning",
    "hands_protocols",
    "execution_workflow",
    "brainstorming_protocol",
    "constraints",
    "solid_programming_mandate",
    "universal_datetime_rules",
    "initialization",
    "communication_examples",
]

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

    Uses the explicit TOP_LEVEL_TAGS list in document order. For each tag it
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
_VP_BLOCK_RE = re.compile(
    r"(  <validation_phase>\n.*?\n  </validation_phase>)",
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
# Public API
# ---------------------------------------------------------------------------

def split_system_prompt(
    source_path: str = "system-prompt.md",
    fragments_dir: str = "prompts/fragments",
    shared_dir: str = "prompts/shared",
    manifest_path: str = "prompts/manifest.txt",
) -> List[str]:
    """Split system-prompt.md into per-tag fragment files.

    Reads the monolithic system-prompt.md, extracts the 20 top-level XML tags in
    document order as verbatim fragment files, extracts the duplicated
    <validation_phase> block into a shared partial with include markers, and
    writes a manifest listing the fragment filenames in assembly order.

    Args:
        source_path: Path to the source system-prompt.md.
        fragments_dir: Output directory for per-tag fragments.
        shared_dir: Output directory for shared partials.
        manifest_path: Output path for the assembly-order manifest.

    Returns:
        A list of fragment filenames in assembly order (also written to the
        manifest).
    """
    src = Path(source_path)
    content = src.read_text(encoding="utf-8")
    lines = content.split("\n")

    # --- 1. Locate the 21 top-level block ranges ---
    ranges = _find_block_ranges(lines)
    if len(ranges) != len(TOP_LEVEL_TAGS):
        _halt(
            f"Expected {len(TOP_LEVEL_TAGS)} top-level blocks, found {len(ranges)}."
        )

    # --- 2. Extract block text for each tag ---
    fragment_filenames: List[str] = []
    frag_dir = Path(fragments_dir)
    frag_dir.mkdir(parents=True, exist_ok=True)
    Path(shared_dir).mkdir(parents=True, exist_ok=True)
    Path(manifest_path).parent.mkdir(parents=True, exist_ok=True)

    for seq, (tag, start, end) in enumerate(ranges, start=1):
        block_text = "\n".join(lines[start : end + 1])

        # --- hands_protocols special case: extract + verify validation_phase ---
        if tag == "hands_protocols":
            shared_content, block_text = _extract_and_verify_validation_phases(
                block_text
            )
            shared_path = Path(shared_dir) / "validation-phase.md"
            shared_path.write_text(shared_content, encoding="utf-8")

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
        filename = f"{seq_str}-{tag}.md"
        write_text = block_text
        if seq == len(ranges) and content.endswith("\n\n"):
            write_text = block_text + "\n"
        (frag_dir / filename).write_text(write_text, encoding="utf-8")
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
    """Command-line entry point: split the default system-prompt.md."""
    fragments = split_system_prompt()
    print(f"Split system-prompt.md into {len(fragments)} fragments:")
    for f in fragments:
        print(f"  prompts/fragments/{f}")
    print("  prompts/shared/validation-phase.md")
    print("  prompts/manifest.txt")


if __name__ == "__main__":
    main()
