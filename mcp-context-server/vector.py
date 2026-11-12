"""Sibling docs: mcp-context-server/README.md, DECISIONS.md — Vector sidecar for docs/tasks/archive/comments hybrid retrieval.

Tiny vector sidecar for hybrid retrieval.

Fastembed CPU ONNX + Chroma in-memory. Lean: no torch, no CUDA, 384-d.
Not a replacement for the deterministic graph — fallback/reranker only.
"""

from __future__ import annotations

import re
from typing import List, Dict, Any

_CHUNK_TOKENS = 512
_CHUNK_OVERLAP = 50
_MAX_CHUNKS_TOTAL = 2000


def _chunk_text(text: str) -> List[str]:
    toks = text.split()
    if not toks:
        return []
    out: List[str] = []
    i = 0
    while i < len(toks):
        chunk = " ".join(toks[i : i + _CHUNK_TOKENS])
        if chunk.strip():
            out.append(chunk)
        if i + _CHUNK_TOKENS >= len(toks):
            break
        i += _CHUNK_TOKENS - _CHUNK_OVERLAP
    return out


def build_vector_index(pairs: List[Dict[str, Any]]):
    """Build in-memory Chroma collection from doc/code pairs.

    pairs: list of {path, content} from graph builder.
    Returns (collection, embeds) or (None, []) when deps missing.
    """
    try:
        import chromadb  # type: ignore
        from fastembed import TextEmbedding  # type: ignore
    except Exception as e:
        import sys

        print(f"vector sidecar unavailable: {e}", file=sys.stderr)
        return None, []
    try:
        client = chromadb.Client()
        col = client.get_or_create_collection("hq_docs_tasks_comments")
        docs: List[str] = []
        ids: List[str] = []
        metas: List[Dict[str, Any]] = []
        for idx, p in enumerate(pairs):
            content = p.get("content", "") if isinstance(p, dict) else str(p)
            path = p.get("path", f"doc_{idx}") if isinstance(p, dict) else f"doc_{idx}"
            for cidx, chunk in enumerate(_chunk_text(content)):
                docs.append(chunk)
                ids.append(f"{path}#{cidx}")
                metas.append({"path": path})
        if len(docs) > _MAX_CHUNKS_TOTAL:
            import sys

            print(
                f"vector sidecar capped {len(docs)} chunks to {_MAX_CHUNKS_TOTAL}",
                file=sys.stderr,
            )
            docs = docs[:_MAX_CHUNKS_TOTAL]
            ids = ids[:_MAX_CHUNKS_TOTAL]
            metas = metas[:_MAX_CHUNKS_TOTAL]
        if docs:
            col.add(documents=docs, ids=ids, metadatas=metas)
        return col, docs
    except Exception as e:
        import sys

        print(f"vector sidecar build failed: {e}", file=sys.stderr)
        return None, []


def query_vector(collection, query: str, k: int = 8):
    """Query vector collection, returns list of (path, score)."""
    if collection is None or not query.strip():
        return []
    try:
        res = collection.query(query_texts=[query], n_results=k)
        out: List[tuple] = []
        ids = (res.get("ids") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        for pid, dist in zip(ids, dists):
            # distance -> score (smaller distance = higher score)
            score = 1.0 / (1.0 + float(dist)) if dist is not None else 0.0
            path = pid.split("#")[0]
            out.append((path, score))
        return out
    except Exception:
        return []


def rrf_fuse(lexical: List[tuple], vector: List[tuple], k: int = 60) -> List[str]:
    """Reciprocal Rank Fusion of lexical (path, score) and vector (path, score)."""
    ranks: Dict[str, float] = {}
    for rank, (path, _s) in enumerate(lexical, 1):
        ranks[path] = ranks.get(path, 0.0) + 1.0 / (k + rank)
    for rank, (path, _s) in enumerate(vector, 1):
        ranks[path] = ranks.get(path, 0.0) + 1.0 / (k + rank)
    # Preserve vector score for debugging, but sort by fused rank
    sorted_paths = sorted(ranks.items(), key=lambda x: -x[1])
    return [p for p, _ in sorted_paths]
