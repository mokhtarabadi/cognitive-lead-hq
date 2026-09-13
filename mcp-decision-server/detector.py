"""Decision-moment detector for manager-decision auto-extraction (Task 213).

Pure standard library — deterministic, no LLM call, unit-testable offline.
Sits BEFORE `extract_session_decisions` (server.py:686): it flags candidate
turns cheaply; only flagged turns go to the LLM extractor, and every
persist still passes the mandatory human confirm gate + `record_manager_decision`
(server.py:909). It never writes anything itself, and its output must pass
human confirm before any `record_manager_decision` call — there is no code
path from this module to the decision store (auto-record is forbidden).

Precision bar (plan verdict A3, hardened per QA hotfix): a candidate is
QUEUED only with a named owner (the manager speaking — agent/assistant/
system/tool turns are skipped) PLUS two or more DISTINCT content-signal
categories. Weak categories (bare modal verbs, lone scope nouns) count only
when paired with a strong category (explicit ruling verb or tradeoff phrase).

Redaction boundary: queued excerpts are RAW session text (truncated to 200
chars on a word edge). They must pass `sanitize_text` + `verify_clean`
(redactor.py) before persistence or mirror write.
"""

from __future__ import annotations

import re

# Strong ruling verbs/phrases — an explicit human call. Counts toward the
# bar on its own. All patterns are case-insensitive with word boundaries so
# substrings ("mustard", "dropdown", "ruler") never match.
_STRONG_RULING = (
    re.compile(
        r"\b(decided?|decide on|approved?|use \w+ over|go with|rule:?|ruling|"
        r"never do|always do|forbidden|required)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(let'?s (?:use|go with|drop|keep|adopt|stick with))\b", re.IGNORECASE),
)

# Weak ruling verbs — too generic alone ("we must fix tests" is not a macro
# decision). Count only when a strong category is also present.
_WEAK_RULING = (
    re.compile(r"\b(must|keep|drop)\b", re.IGNORECASE),
)

# Trade-off markers — weighing alternatives is a decision smell. Strong:
# it pairs weak signals into a passing candidate.
_TRADEOFF = (
    re.compile(r"\btrade-?offs?\b", re.IGNORECASE),
    re.compile(r"\b(instead of|rather than|on the other hand|alternative(?:ly|s)?)\b", re.IGNORECASE),
)

# Reversible-scope nouns — the call touches something with blast radius.
# Weak alone ("the api timed out" is a status, not a decision): counts only
# when a strong category is also present.
_SCOPE = re.compile(
    r"\b(architectur\w*|schemas?|database|api|auth\w*|deploy\w*|releas\w*|polic\w*|"
    r"workflow|pipeline|migration|quota|ratelimit|rate.?limit|scope|deadline|budget)\b",
    re.IGNORECASE,
)

#: Minimum DISTINCT content-signal categories to queue a candidate.
MIN_CONTENT_SIGNALS = 2

#: Excerpt cap. Truncation lands on a word edge, never mid-word.
_EXCERPT_LEN = 200


def _content_categories(text: str) -> set[str]:
    """Return the distinct content-signal categories present in `text`."""
    cats: set[str] = set()
    if any(p.search(text) for p in _STRONG_RULING):
        cats.add("strong-ruling")
    if any(p.search(text) for p in _WEAK_RULING):
        cats.add("weak-ruling")
    if any(p.search(text) for p in _TRADEOFF):
        cats.add("tradeoff-marker")
    if _SCOPE.search(text):
        cats.add("scope-noun")
    # Weak categories ride along only: without a strong category they are
    # ordinary chatter ("must", "api", "scope"), so drop them unless a
    # strong ruling or tradeoff phrase is present.
    if not ({"strong-ruling", "tradeoff-marker"} & cats):
        cats -= {"weak-ruling", "scope-noun"}
    return cats


def _truncate_words(text: str, limit: int = _EXCERPT_LEN) -> str:
    """Cap `text` at `limit` chars, breaking on a word edge when possible."""
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut if cut else text[:limit]


def detect_decision_moments(turns: list[dict]) -> list[dict]:
    """Flag candidate decision turns. Only PASSING candidates are queued.

    `turns`: list of {"speaker": str, "text": str, "manager_confirmed": bool
    (optional)}. Speaker is normalized (trim + lower); non-owner speakers are
    skipped unless the turn carries explicit `manager_confirmed=True`.
    Returns [{"turn_index", "excerpt" (raw, word-edge truncated to 200
    chars), "signals", "passes": True}]. Non-list input or malformed turns
    yield [] — never raises; one bad element never drops valid turns.
    """
    if not isinstance(turns, list):
        return []
    out: list[dict] = []
    for i, turn in enumerate(turns):
        if not isinstance(turn, dict):
            continue
        text = turn.get("text", "")
        if not isinstance(text, str):
            text = str(text)
        if not text.strip():
            continue
        speaker = str(turn.get("speaker", "")).strip().lower()
        # Only "manager" or an explicitly manager-confirmed turn owns a
        # decision — agent/assistant/system/tool proposals never queue.
        if speaker != "manager" and not bool(turn.get("manager_confirmed")):
            continue
        cats = _content_categories(text)
        signals = ["owner:manager"] + sorted(cats)
        if not passes_precision_bar(signals):
            continue
        out.append(
            {
                "turn_index": i,
                "excerpt": _truncate_words(text),
                "signals": signals,
                "passes": True,
            }
        )
    return out


def passes_precision_bar(signals: list[str]) -> bool:
    """True only with named owner + MIN_CONTENT_SIGNALS distinct categories.

    Owner entry is matched after trim + lower-casing ("Manager", " manager "
    both count; missing owner fails). Content entries exclude the owner
    signal; weak categories must already be paired (see _content_categories).
    Non-list input returns False — never raises.
    """
    if not isinstance(signals, list):
        return False
    norm = [str(s).strip().lower() for s in signals]
    if "owner:manager" not in norm:
        return False
    content = {s for s in norm if s != "owner:manager"}
    return len(content) >= MIN_CONTENT_SIGNALS
