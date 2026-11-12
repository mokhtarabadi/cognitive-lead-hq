"""Behavioral hybrid tests: fail if hybrid/ comment/ caps revert."""

from pathlib import Path
import importlib.util
import sys


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def test_comment_extractor_gated_by_extension(tmp_path: Path):
    import unittest.mock as _mock

    sys.path.insert(0, "mcp-context-server")
    if "pathspec" not in sys.modules:
        sys.modules["pathspec"] = _mock.MagicMock()
        sys.modules["pathspec"].PathSpec = _mock.MagicMock()
    _spec = importlib.util.spec_from_file_location(
        "graph", Path("mcp-context-server/graph.py")
    )
    GraphMod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
    assert _spec and _spec.loader
    _spec.loader.exec_module(GraphMod)  # type: ignore[union-attr]
    py_path = tmp_path / "a.py"
    py_path.write_text("# hello comment\nx = 1\n", encoding="utf-8")
    syms = GraphMod._extract_graph_symbols(py_path)
    assert any(t[0].strip() == "hello comment" and t[1] == "comment" for t in syms)
    b = tmp_path / "b.md"
    b.write_text("# Heading not comment\n", encoding="utf-8")
    syms2 = GraphMod._extract_graph_symbols(b)
    assert not any(
        len(t) > 2 and "Heading" in t[0] and t[1] == "comment" for t in syms2
    )


def test_vector_max_chunks_cap_exists():
    """Vector must cap at 2000 chunks with stderr log."""
    vtext = _read(Path("mcp-context-server/vector.py"))
    assert "_MAX_CHUNKS_TOTAL = 2000" in vtext
    assert "vector sidecar capped" in vtext
    assert "Sibling docs:" in vtext


def test_server_hybrid_uses_cached_model_and_30_cap():
    """Hybrid must cache model and rank top 30 not 200."""
    stext = _read(Path("mcp-context-server/server.py"))
    assert "_VEC_MODEL = None" in stext
    assert "_get_vec_model" in stext
    assert "scored[:30]" in stext
    assert "scored[:200]" not in stext
    assert 'data.get("nodes", [])[:30]' in stext


def test_server_hybrid_import_and_logging():
    """Must try absolute then relative import and log on failure, not silent pass."""
    stext = _read(Path("mcp-context-server/server.py"))
    assert "from vector import rrf_fuse" in stext
    assert "from .vector import rrf_fuse" in stext
    assert "hybrid vector re-rank unavailable" in stext
    assert "file=sys.stderr" in stext


def test_vector_rrf_fuse_is_behavioral():
    """RRF fuse must actually reorder by rank, not tautology."""
    spec = importlib.util.spec_from_file_location(
        "vector_hybrid", Path("mcp-context-server/vector.py")
    )
    m = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader
    spec.loader.exec_module(m)  # type: ignore[union-attr]
    lex = [("a", 1.0), ("b", 0.9)]
    vec = [("b", 0.95), ("c", 0.8)]
    fused = m.rrf_fuse(lex, vec, k=60)
    assert fused[0] == "b"
    assert "c" in fused
