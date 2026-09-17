"""Authority-ranked retrieval over decision, memory, repo, and web candidates.

Pure and offline: source adapters supply candidates, this module only
normalizes, ranks, gathers, and narrows. Existing store ranking stays
local to each server; authority weight always precedes local relevance.
"""

import re

AUTHORITY_WEIGHTS = {
    "decision": 4,
    "memory": 3,
    "repo": 2,
    "web": 1,
}

_REQUIRED_FIELDS = ("candidate_id", "source", "text", "local_score", "chunk_id")

_WORD_RE = re.compile(r"\w+", re.UNICODE)


def normalize_candidate(raw):
    """Validate one raw candidate dict into a canonical mapping."""
    if not isinstance(raw, dict):
        raise ValueError(f"candidate must be a mapping, got {type(raw).__name__}")
    missing = [f for f in _REQUIRED_FIELDS if f not in raw]
    if missing:
        raise ValueError(f"candidate missing required fields {missing}: {raw!r:.120}")
    source = raw["source"]
    if source not in AUTHORITY_WEIGHTS:
        raise ValueError(f"unknown candidate source {source!r}: {raw!r:.120}")
    try:
        score = float(raw["local_score"])
    except (TypeError, ValueError):
        raise ValueError(f"candidate local_score must be numeric: {raw!r:.120}")
    return {
        "candidate_id": str(raw["candidate_id"]),
        "source": source,
        "text": str(raw["text"]),
        "local_score": score,
        "chunk_id": str(raw["chunk_id"]),
        "metadata": dict(raw.get("metadata") or {}),
    }


def rank_key(candidate):
    """Lexicographic key: authority first, then local score, then id."""
    return (
        -AUTHORITY_WEIGHTS[candidate["source"]],
        -candidate["local_score"],
        candidate["candidate_id"],
    )


def gather_top_candidates(query, adapters, gather_limit=20):
    """Call each adapter once, rank combined candidates, cap at the limit.

    Returns ``(top, gathered_count)`` where ``gathered_count`` is the
    pre-cap total so callers can prove gathering happened before narrowing.
    """
    gathered = []
    for source in ("decision", "memory", "repo", "web"):
        adapter = (adapters or {}).get(source)
        if adapter is None:
            continue
        for raw in adapter(query) or []:
            gathered.append(normalize_candidate(raw))
    gathered.sort(key=rank_key)
    return gathered[:gather_limit], len(gathered)


def tokenize(text):
    """Case-folded Unicode word tokens; empty text yields an empty set."""
    return set(_WORD_RE.findall((text or "").casefold()))


def overlap(text_a, text_b):
    """Overlap coefficient over token sets; 0.0 when either side is empty."""
    tokens_a, tokens_b = tokenize(text_a), tokenize(text_b)
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / min(len(tokens_a), len(tokens_b))


def narrow_with_chunk_overlap(ranked, narrow_limit=5, overlap_threshold=0.20):
    """Seed with the top candidate, prefer overlapping chunks, fill the rest.

    Returns ``(selected, overlap_pairs)``; ``selected`` stays in
    authority-ranked order.
    """
    if not ranked or narrow_limit <= 0:
        return [], []
    selected = [ranked[0]]
    pairs = []
    for cand in ranked[1:]:
        if len(selected) >= narrow_limit:
            break
        for kept in selected:
            if overlap(cand["text"], kept["text"]) >= overlap_threshold:
                pairs.append((kept["candidate_id"], cand["candidate_id"]))
                selected.append(cand)
                break
    for cand in ranked[1:]:
        if len(selected) >= narrow_limit:
            break
        if cand not in selected:
            selected.append(cand)
    selected.sort(key=rank_key)
    return selected, pairs


def retrieve(query, adapters, gather_limit=20, narrow_limit=5, overlap_threshold=0.20):
    """Gather the top candidates across sources, then narrow with overlap."""
    top, gathered_count = gather_top_candidates(query, adapters, gather_limit)
    selected, pairs = narrow_with_chunk_overlap(top, narrow_limit, overlap_threshold)
    return {
        "candidates": selected,
        "gathered_count": gathered_count,
        "returned_count": len(selected),
        "gather_limit": gather_limit,
        "narrow_limit": narrow_limit,
        "overlap_threshold": overlap_threshold,
        "overlap_pairs": pairs,
    }
