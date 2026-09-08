"""Dual-dispatch helpers for the persona MCP engine (Task 167).

This module classifies raw persona-LLM output into two lanes:

1. **XML lane** — the model emitted a structured ``<hands_*_task>`` (or
   ``<failure_report>``) block. The block is isolated verbatim and handed
   back to the caller as machine-readable instructions.
2. **Question lane** — the model produced no XML but is asking for missing
   context or clarification. The caller must relay the question instead of
   treating the text as an actionable report.

Anything that is neither XML nor a question is treated as a free-form
evaluation report (``REPORT`` status at the server layer).

Pure standard library — no third-party imports — so this module is trivially
unit-testable without network access or LLM credentials.
"""

from __future__ import annotations

import re
from typing import Optional

# Matches one structured control block, e.g. <hands_implementation_task> ...
# </hands_implementation_task> or <failure_report> ... </failure_report>.
# The back-reference (\\1) guarantees the closing tag matches the opening tag.
# DOTALL lets a single block span multiple lines.
XML_BLOCK_RE = re.compile(
    r"<(hands_[a-z_]+_task|failure_report)\b[^>]*>([\s\S]*?)</\1>",
    re.DOTALL,
)

# Heuristics for "the model is asking something / needs input".
# Applied to text AFTER all XML blocks have been stripped out.
QUESTION_RE = re.compile(
    r"\b(what|which|who|whom|whose|when|where|why|how\b.*\?|clarif\w*|"
    r"missing|need(?:ed|s)?|require[sd]?|awaiting|blocked on|unclear|"
    r"please\s+(provide|specify|confirm|clarify|share|send|explain))\b",
    re.IGNORECASE,
)

# Decision tokens: when any of these appear in the non-XML remainder, the
# output is an evaluation report — even if it also contains diagnostic or
# rhetorical questions. Reports must never be misrouted to the question lane.
DECISION_TOKENS = (
    "QA_PASSED",
    "QA_REJECTED",
    "APPROVED",
    "APPROVED_WITH_CHANGES",
    "REJECTED_NEEDS_FIXES",
    "PO_REVIEW_PENDING",
    "PASSED",
    "FAILED",
)

# Explicit interrogative openers: a remainder STARTING with one of these is a
# question even without a trailing question mark (e.g. "Please provide the
# missing criteria."). Anchored at the start to avoid matching reports that
# merely mention such phrasing mid-sentence.
LEADING_QUESTION_RE = re.compile(
    r"^(what|which|who|whom|whose|when|where|why|how|can you confirm|"
    r"please\s+(provide|specify|confirm|clarify|share|send|explain))\b",
    re.IGNORECASE,
)


def extract_xml(text: str) -> tuple[bool, Optional[str], str]:
    """Detect and isolate the outermost XML control block in ``text``.

    Args:
        text: Raw persona-LLM output, possibly with conversational preamble
            and/or trailing commentary around the structured block.

    Returns:
        A ``(has_xml, xml_content, clean_text)`` triple where:
        - ``has_xml`` is True when a well-formed block was found.
        - ``xml_content`` is the full matched block (opening tag through
          closing tag) verbatim, or None when absent/malformed.
        - ``clean_text`` is the input with the extracted block removed and
          surrounding whitespace stripped (the human-readable remainder).

    Notes:
        - Malformed XML (opening tag with no matching close) is NOT treated
          as XML: ``has_xml`` is False and the text is returned unchanged so
          the caller can fall through to question/report classification.
        - Only the FIRST (outermost) block is extracted; any additional
          blocks stay in ``clean_text`` for downstream handling.
    """
    if not text:
        return False, None, ""
    match = XML_BLOCK_RE.search(text)
    if match is None:
        # No well-formed block: opening tag without a matching close tag
        # (or no tags at all) falls through here unchanged.
        return False, None, text.strip()
    xml_content = match.group(0)
    # Remove just the extracted block; keep preamble + trailing commentary.
    clean_text = (text[: match.start()] + text[match.end() :]).strip()
    return True, xml_content, clean_text


def strip_all_xml(text: str) -> str:
    """Remove every well-formed XML control block from ``text``.

    Helper for question detection: classification must run on the
    human-readable remainder, never on structured tag contents.
    """
    if not text:
        return ""
    return XML_BLOCK_RE.sub("", text).strip()


def is_clarification_question(text: str) -> bool:
    """Return True when ``text`` (ignoring XML) asks for missing context.

    Precision-first, deterministic classification (V1 fix):

    1. Strip all XML control blocks first.
    2. If a decision token (``QA_PASSED``, ``APPROVED``, ``FAILED``, ...)
       appears anywhere in the remainder, return False immediately — it is
       an evaluation report, even when it embeds diagnostic or rhetorical
       questions.
    3. Otherwise True only when the remainder matches ``QUESTION_RE`` AND
       contains a ``?``, or starts with an explicit interrogative phrase
       (``what``/``which``/``please provide``/``can you confirm``/...).
       A bare ``?`` alone is NOT enough (the old naive rule).

    Args:
        text: Raw persona-LLM output (may still contain XML blocks).

    Returns:
        True if the non-XML remainder genuinely requests missing context;
        False for reports, statements, and empty input.
    """
    remainder = strip_all_xml(text)
    if not remainder:
        return False
    upper = remainder.upper()
    if any(token in upper for token in DECISION_TOKENS):
        return False
    if QUESTION_RE.search(remainder) is not None and "?" in remainder:
        return True
    return LEADING_QUESTION_RE.match(remainder) is not None
