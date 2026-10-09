# Sibling Docs: README.md | Decisions: DECISIONS.md


"""Lite knowledge-graph: constants, parsers, build, query primitives. Stdlib-pure: no MCP imports, no registration, no import back to server."""

import json
import re
import time
import uuid
from pathlib import Path

from fsutil import GitIgnoreFilter, collect_files


GRAPH_SCHEMA_VERSION = 2


GRAPH_MAX_FILES = 300


GRAPH_MAX_NODES = 5000


GRAPH_MAX_DOCS = 300


GRAPH_DOC_LINES = 500


GRAPH_DOC_SECTIONS = 60


_GRAPH_CODE_EXTS = frozenset(
    {
        ".py",
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".ts",
        ".tsx",
        ".mts",
        ".cts",
        ".go",
        ".java",
        ".rs",
        ".kt",
        ".kts",
        ".rb",
        ".php",
        ".cs",
        ".swift",
        ".lua",
        ".zig",
        ".sh",
        ".bash",
        ".sql",
        ".vue",
        ".svelte",
        ".astro",
        ".html",
        ".htm",
        ".xml",
        ".dart",
        ".m",
        ".mm",
        ".gradle",
        ".prisma",
        ".properties",
        ".css",
        ".scss",
        ".less",
    }
)


_GRAPH_SYMBOL_RE = re.compile(
    r"^\s*(?:export\s+|default\s+|public\s+|private\s+|protected\s+|static\s+|async\s+|fun\s+|def\s+|class\s+|interface\s+|type\s+|enum\s+|struct\s+|trait\s+|func(?:tion)?\s+)?"
    r"(?:class|interface|type|enum|struct|trait|def|fun|func(?:tion)?)\s+([A-Za-z_]\w*)"
)


_GRAPH_CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")


_GRAPH_KT_FUN_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|open|override|suspend|inline|tailrec|operator|infix|external)\s+)*fun\s+(?:<[^>]*>\s*)?([A-Za-z_]\w*)"
)


_GRAPH_TYPE_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|open|abstract|final|sealed|data|object|export|default)\s+)*(?:class|object|interface)\s+([A-Za-z_]\w*)"
)


_GRAPH_SWIFT_RE = re.compile(
    r"^\s*(?:(?:public|private|fileprivate|internal|open|override|static|class|mutating|required|convenience)\s+)*(?:func\s+([A-Za-z_]\w*)|(class|struct|enum|protocol)\s+([A-Za-z_]\w*))"
)


_GRAPH_JAVA_METHOD_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|static|final|synchronized|abstract|native|default|volatile|transient)\s+)+[\w<>\[\]?.,\s]+\s+(\w+)\s*\("
)


_GRAPH_JAVA_CTOR_RE = re.compile(r"^\s*(?:public|private|protected)\s+([A-Z]\w*)\s*\(")


_GRAPH_DART_RE = re.compile(r"^\s*(?:[\w<>?,\s]+\s+)?(\w+)\s*\([^;{}]*\)\s*(?:\{|=>|;)")


_GRAPH_DART_KEYWORDS = frozenset(
    {
        "return",
        "if",
        "for",
        "while",
        "switch",
        "assert",
        "new",
        "const",
        "final",
        "var",
        "late",
        "import",
        "export",
        "throw",
        "else",
        "do",
    }
)


_GRAPH_ARROW_RE = re.compile(
    r"^\s*(?:export\s+)?(?:const|let)\s+([A-Za-z_]\w*)\s*(?::[^=;]+)?=\s*(?:async\s*)?(?:\([^)]*\)\s*=>|function)"
)


_GRAPH_ANDROID_ID_RE = re.compile(r'android:id="@\+id/([\w]+)"')


_GRAPH_DOM_ID_RE = re.compile(r'(?:id|@\+id)="([\w-]+)"')


_GRAPH_R_ID_RE = re.compile(r"R\.id\.([\w]+)")


_GRAPH_GET_ID_RE = re.compile(r"getElementById\(\s*['\"]([\w-]+)['\"]\)")


_GRAPH_SCRIPT_BLOCK_RE = re.compile(
    r"<script\b[^>]*>(.*?)</script>", re.DOTALL | re.IGNORECASE
)


_GRAPH_OBJC_METHOD_RE = re.compile(r"^\s*[-+]\s*\([^)]*\)\s*([A-Za-z_]\w*)")


_GRAPH_OBJC_IMPL_RE = re.compile(r"^\s*@implementation\s+([A-Za-z_]\w*)")


_GRAPH_PRISMA_RE = re.compile(r"^\s*(model|enum)\s+([A-Za-z_]\w*)")


_GRAPH_PROP_RE = re.compile(r"^\s*([A-Za-z_][\w.\-]*)\s*[=:]")


_GRAPH_CSS_RE = re.compile(r"^\s*\.([\w-]+)\s*\{")


_GRAPH_SQL_TABLE_RE = re.compile(
    r"^\s*CREATE\s+(?:TEMP(?:ORARY)?\s+)?(?:TABLE|VIEW)\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"\[]?([\w\.]+)[`\"\]]?",
    re.IGNORECASE,
)


_GRAPH_SQL_REF_RE = re.compile(r"REFERENCES\s+[`\"\[]?([\w\.]+)[`\"\]]?", re.IGNORECASE)


_GRAPH_MD_HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$")


_GRAPH_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+\.md)(?:#[^)\s]*)?\)")


_GRAPH_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]]*)?(?:\|[^\]]*)?\]\]")


_GRAPH_TOKEN_SPLIT_RE = re.compile(r"(?<=[a-z])(?=[A-Z])")


_GRAPH_TASK_REF_RE = re.compile(r"\bTask\s+(\d{1,4})\b")


_GRAPH_ADR_REF_RE = re.compile(r"\bADR-(\d{1,3})\b", re.IGNORECASE)


_GRAPH_GOD_NOISE = frozenset({"run", "json", "post", "data"})


_GRAPH_MAX_SCAN_BYTES = 1048576


def _read_text_capped(file_path: Path, cap: int = _GRAPH_MAX_SCAN_BYTES) -> str | None:
    """Read text bounded by cap bytes so huge generated files cannot wedge the server."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="strict") as f:
            return f.read(cap + 1)[:cap]
    except Exception:
        return None


def _push_graph_symbol(
    out: list[tuple[str, str, int]], seen: set[str], name: str, kind: str, lineno: int
) -> None:
    if len(out) >= 200 or len(name) < 2 or name in seen:
        return
    seen.add(name)
    out.append((name, kind, lineno))


def _scan_js_like_symbols(
    text: str, base_line: int, out: list[tuple[str, str, int]], seen: set[str]
) -> None:
    for i, line in enumerate(text.split("\n")):
        if len(out) >= 200:
            return
        lineno = base_line + i
        m = _GRAPH_SYMBOL_RE.match(line)
        if m:
            lowered = line.lower()
            _push_graph_symbol(
                out, seen, m.group(1), "class" if "class" in lowered else "func", lineno
            )
            continue
        m = _GRAPH_ARROW_RE.match(line)
        if m:
            _push_graph_symbol(out, seen, m.group(1), "func", lineno)


def _extract_graph_symbols(file_path: Path) -> list[tuple[str, str, int]]:
    """Return [(name, kind, line_no)] capped per file. Regex-based, deterministic.

    Covers backend (Python/JS/TS/Go/Java...), mobile (Kotlin fun/class/object,
    Swift func/types, Java methods/ctors, Dart classes/members), frontend
    (Vue/Svelte script blocks, arrow components), and markup (HTML/XML element
    ids incl. android:id). Markup node labels keep raw ids (dashes included).
    """
    out: list[tuple[str, str, int]] = []
    seen: set[str] = set()
    text = _read_text_capped(file_path)
    if text is None:
        return out
    lines = text.split("\n")
    suffix = file_path.suffix.lower()
    if suffix in (".vue", ".svelte", ".astro", ".html", ".htm"):
        text = "\n".join(lines)
        for m in _GRAPH_SCRIPT_BLOCK_RE.finditer(text):
            base_line = text[: m.start(1)].count("\n") + 1
            _scan_js_like_symbols(m.group(1), base_line, out, seen)
    if suffix in (".vue", ".svelte", ".astro", ".html", ".htm", ".xml"):
        for i, line in enumerate(lines, 1):
            if len(out) >= 200:
                break
            for m in _GRAPH_ANDROID_ID_RE.finditer(line):
                _push_graph_symbol(out, seen, m.group(1), "view_id", i)
            for m in _GRAPH_DOM_ID_RE.finditer(line):
                _push_graph_symbol(out, seen, m.group(1), "element_id", i)
        return out
    if suffix in (".kt", ".kts", ".java", ".swift", ".dart", ".m", ".mm", ".gradle"):
        for i, line in enumerate(lines, 1):
            if len(out) >= 200:
                break
            if suffix in (".m", ".mm"):
                m = _GRAPH_OBJC_IMPL_RE.match(line)
                if m:
                    _push_graph_symbol(out, seen, m.group(1), "class", i)
                    continue
                m = _GRAPH_OBJC_METHOD_RE.match(line)
                if m:
                    _push_graph_symbol(out, seen, m.group(1), "method", i)
                    continue
                continue
            m = _GRAPH_KT_FUN_RE.match(line)
            if m:
                _push_graph_symbol(out, seen, m.group(1), "func", i)
                continue
            m = _GRAPH_TYPE_RE.match(line)
            if m:
                _push_graph_symbol(out, seen, m.group(1), "class", i)
                continue
            m = _GRAPH_SWIFT_RE.match(line)
            if m:
                if m.group(1):
                    _push_graph_symbol(out, seen, m.group(1), "func", i)
                else:
                    _push_graph_symbol(out, seen, m.group(3), "class", i)
                continue
            m = _GRAPH_JAVA_METHOD_RE.match(line)
            if m and m.group(1) not in (
                "if",
                "for",
                "while",
                "switch",
                "catch",
                "return",
            ):
                _push_graph_symbol(out, seen, m.group(1), "method", i)
                continue
            m = _GRAPH_JAVA_CTOR_RE.match(line)
            if m:
                _push_graph_symbol(out, seen, m.group(1), "method", i)
                continue
            if suffix == ".dart":
                m = _GRAPH_DART_RE.match(line)
                if m and m.group(1) not in _GRAPH_DART_KEYWORDS:
                    _push_graph_symbol(out, seen, m.group(1), "method", i)
                    continue
            m = _GRAPH_ARROW_RE.match(line)
            if m:
                _push_graph_symbol(out, seen, m.group(1), "func", i)
        return out
    if suffix == ".prisma":
        for i, line in enumerate(lines, 1):
            if len(out) >= 200:
                break
            m = _GRAPH_PRISMA_RE.match(line)
            if m:
                _push_graph_symbol(
                    out,
                    seen,
                    m.group(2),
                    "model" if m.group(1) == "model" else "enum",
                    i,
                )
        return out
    if suffix == ".properties":
        for i, line in enumerate(lines, 1):
            if len(out) >= 200:
                break
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "!")):
                continue
            m = _GRAPH_PROP_RE.match(line)
            if m:
                _push_graph_symbol(out, seen, m.group(1), "config", i)
        return out
    if suffix in (".css", ".scss", ".less"):
        for i, line in enumerate(lines, 1):
            if len(out) >= 200:
                break
            m = _GRAPH_CSS_RE.match(line)
            if m:
                _push_graph_symbol(out, seen, m.group(1), "style", i)
        return out
    for i, line in enumerate(lines, 1):
        if len(out) >= 200:
            break
        m = _GRAPH_SYMBOL_RE.match(line)
        if m:
            name = m.group(1)
            lowered = line.lower()
            if "interface" in lowered:
                kind = "interface"
            elif "enum" in lowered:
                kind = "enum"
            elif re.search(r"\btype\b", lowered):
                kind = "type"
            elif "class" in lowered:
                kind = "class"
            else:
                kind = "func"
            _push_graph_symbol(out, seen, name, kind, i)
            continue
        m = _GRAPH_ARROW_RE.match(line)
        if m:
            _push_graph_symbol(out, seen, m.group(1), "func", i)
            continue
    return out


def _extract_sql_symbols(
    file_path: Path,
) -> tuple[list[tuple[str, str, int]], list[str]]:
    """Return ([(table, kind, line_no)], [referenced_table, ...]). Deterministic."""
    tables: list[tuple[str, str, int]] = []
    refs: list[str] = []
    text = _read_text_capped(file_path)
    if text is None:
        return tables, refs
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        m = _GRAPH_SQL_TABLE_RE.match(line)
        if m and len(tables) < 200:
            name = m.group(1).split(".")[-1]
            kind = "view" if "view" in line.lower() else "table"
            if name not in {n for n, _, _ in tables}:
                tables.append((name, kind, i))
        for r in _GRAPH_SQL_REF_RE.finditer(line):
            ref = r.group(1).split(".")[-1]
            if ref and ref not in refs:
                refs.append(ref)
                if len(refs) >= 40:
                    break
    return tables, refs


def _extract_md_sections(abs_path: Path) -> list[tuple[str, int, int]]:
    """Return [(heading_text, level, line_no)] capped. Deterministic."""
    out: list[tuple[str, int, int]] = []
    text = _read_text_capped(abs_path)
    if text is None:
        return out
    lines = text.split("\n")[:GRAPH_DOC_LINES]
    for i, line in enumerate(lines, 1):
        if len(out) >= GRAPH_DOC_SECTIONS:
            break
        m = _GRAPH_MD_HEADING_RE.match(line)
        if not m:
            continue
        text = m.group(2).strip()[:80]
        if len(text) >= 2:
            out.append((text, len(m.group(1)), i))
    return out


def _extract_md_link_targets(content: str) -> list[str]:
    """Return raw Markdown link targets (./other.md, [[wikilinks]]). Deterministic."""
    targets: list[str] = []
    for m in _GRAPH_MD_LINK_RE.finditer(content):
        t = m.group(1).strip()
        if t and t not in targets and not re.match(r"https?://", t):
            targets.append(t)
    for m in _GRAPH_WIKILINK_RE.finditer(content):
        t = m.group(1).strip()
        if t and t not in targets:
            targets.append(t if t.lower().endswith(".md") else t + ".md")
    return targets[:40]


def _resolve_doc_link(target: str, from_rel: str, doc_set: set[str]) -> str | None:
    if target.startswith("/"):
        cand = target.lstrip("/")
    else:
        from_dir = from_rel.rsplit("/", 1)[0] if "/" in from_rel else ""
        parts = (from_dir + "/" + target).split("/")
        stack: list[str] = []
        for part in parts:
            if part in ("", "."):
                continue
            if part == "..":
                if stack:
                    stack.pop()
            else:
                stack.append(part)
        cand = "/".join(stack)
    if cand in doc_set:
        return cand
    base = cand.rsplit("/", 1)[-1]
    for d in doc_set:
        if d.rsplit("/", 1)[-1].lower() == base.lower():
            return d
    return None


def _slugify_section(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or "section"


def _parse_graph_imports(rel_suffix: str, content: str) -> list[str]:
    imps: list[str] = []
    try:
        if rel_suffix == ".py":
            for m in re.finditer(
                r"^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))",
                content,
                re.MULTILINE,
            ):
                mod = m.group(1) or m.group(2)
                if mod and mod not in imps:
                    imps.append(mod)
        elif rel_suffix in {
            ".js",
            ".jsx",
            ".mjs",
            ".cjs",
            ".ts",
            ".tsx",
            ".mts",
            ".cts",
        }:
            for m in re.finditer(
                r"""(?:from\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]|import\(\s*['"]([^'"]+)['"])""",
                content,
            ):
                mod = m.group(1) or m.group(2) or m.group(3)
                if mod and mod not in imps and mod.startswith("."):
                    imps.append(mod)
        elif rel_suffix == ".go":
            for m in re.finditer(r'"([\w\.\-/]+)"', content):
                mod = m.group(1)
                if "/" in mod and mod not in imps:
                    imps.append(mod)
                    if len(imps) >= 20:
                        break
        elif rel_suffix in {".kt", ".kts", ".java", ".gradle"}:
            for m in re.finditer(
                r"^\s*import\s+(?:static\s+)?([\w\.]+)", content, re.MULTILINE
            ):
                mod = m.group(1)
                if mod and mod not in imps:
                    imps.append(mod)
        elif rel_suffix in {".swift", ".m", ".mm"}:
            for m in re.finditer(r"^\s*import\s+(\w+)", content, re.MULTILINE):
                mod = m.group(1)
                if mod and mod not in imps:
                    imps.append(mod)
    except Exception:
        return imps
    return imps[:20]


def _resolve_import_to_rel(mod: str, from_rel: str, rel_set: set[str]) -> str | None:
    if not mod.startswith(".") and "." not in mod and "/" not in mod:
        return None
    cand_base = mod.replace(".", "/").strip("/")
    from_dir = from_rel.rsplit("/", 1)[0] if "/" in from_rel else ""
    tried: list[str] = []
    if mod.startswith("."):
        level = len(mod) - len(mod.lstrip("."))
        rest = mod.lstrip(".").replace(".", "/")
        parts = from_dir.split("/") if from_dir else []
        base = "/".join(parts[: max(0, len(parts) - level + 1)])
        tried.append(f"{base}/{rest}".strip("/"))
    else:
        tried.append(cand_base)
    exts = [
        ".py",
        "/__init__.py",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".go",
        ".java",
        ".rs",
        ".kt",
        ".kts",
        ".swift",
        ".dart",
        ".vue",
        ".m",
        ".mm",
    ]
    for t in tried:
        for e in exts:
            c = (t + e).strip("/")
            if c in rel_set:
                return c
        if t in rel_set:
            return t
    return None


def _build_graph_data(workspace_root: Path, target: Path) -> dict:
    filt = GitIgnoreFilter()
    all_found = collect_files(str(target), filt)
    files = [
        p
        for p in all_found
        if p.suffix.lower() in _GRAPH_CODE_EXTS and "context-reports" not in p.parts
    ]
    files.sort(key=lambda p: (len(p.parts), p.as_posix()))
    files = files[:GRAPH_MAX_FILES]
    docs = [
        p
        for p in all_found
        if p.suffix.lower() == ".md" and "context-reports" not in p.parts
    ]
    docs.sort(key=lambda p: (len(p.parts), p.as_posix()))
    docs = docs[:GRAPH_MAX_DOCS]
    rels: list[str] = []
    rel_set: set[str] = set()
    resolved: list[Path] = []
    doc_rels: list[str] = []
    doc_set: set[str] = set()
    doc_resolved: list[Path] = []
    for p in files:
        try:
            rel = p.resolve().relative_to(workspace_root).as_posix()
        except ValueError:
            continue
        if rel not in rel_set:
            rel_set.add(rel)
            rels.append(rel)
            resolved.append(p.resolve())
    for p in docs:
        try:
            rel = p.resolve().relative_to(workspace_root).as_posix()
        except ValueError:
            continue
        if rel not in doc_set and rel not in rel_set:
            doc_set.add(rel)
            doc_rels.append(rel)
            doc_resolved.append(p.resolve())
    nodes: list[dict] = []
    links: list[dict] = []
    sym_index: dict[str, list[str]] = {}
    file_contents: dict[str, str] = {}
    for rel, abs_p in zip(rels, resolved):
        nodes.append(
            {"id": f"file:{rel}", "label": rel, "file_type": "code", "source_file": rel}
        )
        try:
            with open(abs_p, "r", encoding="utf-8", errors="strict") as f:
                content = f.read()[:200000]
        except Exception:
            content = ""
        file_contents[rel] = content
        if Path(rel).suffix.lower() == ".sql":
            symbols, sql_refs = _extract_sql_symbols(abs_p)
            for t in sql_refs:
                links.append(
                    {
                        "source": f"file:{rel}",
                        "target": f"sqlref:{t}",
                        "relation": "references",
                        "confidence": "EXTRACTED",
                        "source_file": rel,
                    }
                )
        else:
            symbols = _extract_graph_symbols(abs_p)
        for name, kind, lineno in symbols:
            if len(nodes) >= GRAPH_MAX_NODES:
                break
            sid = f"sym:{rel}#{name}"
            nodes.append(
                {
                    "id": sid,
                    "label": name,
                    "file_type": "code",
                    "source_file": rel,
                    "source_location": f"L{lineno}",
                    "kind": kind,
                }
            )
            links.append(
                {
                    "source": f"file:{rel}",
                    "target": sid,
                    "relation": "contains",
                    "confidence": "EXTRACTED",
                    "source_file": rel,
                }
            )
            sym_index.setdefault(name, []).append(sid)
    doc_contents: dict[str, str] = {}
    for rel, abs_p in zip(doc_rels, doc_resolved):
        if len(nodes) >= GRAPH_MAX_NODES:
            break
        nodes.append(
            {
                "id": f"file:{rel}",
                "label": rel,
                "file_type": "document",
                "source_file": rel,
            }
        )
        try:
            with open(abs_p, "r", encoding="utf-8", errors="strict") as f:
                content = f.read()[:200000]
        except Exception:
            content = ""
        doc_contents[rel] = content
        for heading, _level, lineno in _extract_md_sections(abs_p):
            if len(nodes) >= GRAPH_MAX_NODES:
                break
            sec_id = f"sec:{rel}#{_slugify_section(heading)}"
            if sec_id not in {n["id"] for n in nodes}:
                nodes.append(
                    {
                        "id": sec_id,
                        "label": heading,
                        "file_type": "document",
                        "source_file": rel,
                        "source_location": f"L{lineno}",
                        "kind": "section",
                    }
                )
                links.append(
                    {
                        "source": f"file:{rel}",
                        "target": sec_id,
                        "relation": "contains",
                        "confidence": "EXTRACTED",
                        "source_file": rel,
                    }
                )
    for rel, content in doc_contents.items():
        if not content or len(links) >= GRAPH_MAX_NODES * 2:
            break
        for tgt in _extract_md_link_targets(content):
            resolved_tgt = _resolve_doc_link(tgt, rel, doc_set)
            if resolved_tgt and resolved_tgt != rel:
                links.append(
                    {
                        "source": f"file:{rel}",
                        "target": f"file:{resolved_tgt}",
                        "relation": "references",
                        "confidence": "EXTRACTED",
                        "source_file": rel,
                    }
                )
        seen_doc_refs: set[str] = set()
        for pat in (r"\b([A-Za-z_]\w{3,})\b", r"\b([\w]+-[\w-]+)\b"):
            for m in re.finditer(pat, content):
                name = m.group(1)
                if name in seen_doc_refs:
                    continue
                targets = sym_index.get(name, [])
                if not targets:
                    continue
                seen_doc_refs.add(name)
                for tid in targets[:3]:
                    links.append(
                        {
                            "source": f"file:{rel}",
                            "target": tid,
                            "relation": "references",
                            "confidence": "INFERRED",
                            "source_file": rel,
                        }
                    )
                if len(seen_doc_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
                    break
    for rel in rels:
        content = file_contents.get(rel, "")
        if not content:
            continue
        suffix = Path(rel).suffix.lower()
        for mod in _parse_graph_imports(suffix, content):
            tgt = _resolve_import_to_rel(mod, rel, rel_set)
            if tgt and tgt != rel:
                links.append(
                    {
                        "source": f"file:{rel}",
                        "target": f"file:{tgt}",
                        "relation": "imports",
                        "confidence": "EXTRACTED",
                        "source_file": rel,
                    }
                )
        if len(links) >= GRAPH_MAX_NODES * 2:
            break
        seen_refs: set[str] = set()
        for id_re in (_GRAPH_R_ID_RE, _GRAPH_GET_ID_RE):
            for m in id_re.finditer(content):
                name = m.group(1)
                if (rel, name) in seen_refs:
                    continue
                for tid in sym_index.get(name, []):
                    if tid.startswith(f"sym:{rel}#"):
                        continue
                    seen_refs.add((rel, name))
                    links.append(
                        {
                            "source": f"file:{rel}",
                            "target": tid,
                            "relation": "references",
                            "confidence": "INFERRED",
                            "source_file": rel,
                        }
                    )
                    break
        for m in _GRAPH_CALL_RE.finditer(content):
            name = m.group(1)
            if len(name) < 3 or name in {
                "def",
                "class",
                "return",
                "import",
                "from",
                "for",
                "while",
                "with",
            }:
                continue
            targets = sym_index.get(name, [])
            for tid in targets:
                if tid.startswith(f"sym:{rel}#") or (rel, name) in seen_refs:
                    continue
                seen_refs.add((rel, name))
                links.append(
                    {
                        "source": f"file:{rel}",
                        "target": tid,
                        "relation": "references",
                        "confidence": "INFERRED",
                        "source_file": rel,
                    }
                )
                if len(seen_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
                    break
            if len(seen_refs) >= 40 or len(links) >= GRAPH_MAX_NODES * 2:
                break
    rationale_refs: list[tuple[str, str, str]] = []
    for rel in rels:
        content = file_contents.get(rel, "")
        if not content:
            continue
        for m in _GRAPH_TASK_REF_RE.finditer(content):
            rationale_refs.append((rel, "task", m.group(1)))
            if len(rationale_refs) >= 200:
                break
        for m in _GRAPH_ADR_REF_RE.finditer(content):
            rationale_refs.append((rel, "adr", m.group(1)))
            if len(rationale_refs) >= 200:
                break
    task_rel_by_id: dict[str, str] = {}
    for cand_dir in ("backlog", "in-progress", "qa", "completed", "archive"):
        tdir = workspace_root / "tasks" / cand_dir
        if not tdir.is_dir():
            continue
        try:
            for md in tdir.glob("*.md"):
                mm = re.match(r"^(\d+)-", md.name)
                if mm:
                    task_rel_by_id.setdefault(
                        mm.group(1).lstrip("0") or "0",
                        md.resolve().relative_to(workspace_root).as_posix(),
                    )
        except OSError:
            continue
    node_ids = {n["id"] for n in nodes}
    seen_rat: set[tuple[str, str]] = set()
    for rel, kind, num in rationale_refs:
        target: str | None = None
        if kind == "task":
            trel = task_rel_by_id.get(num.lstrip("0") or "0")
            if trel:
                target = f"file:{trel}"
        else:
            needle = f"adr-{int(num):03d}"
            for n in nodes:
                if n["id"].startswith("sec:") and needle in n["label"].lower():
                    target = n["id"]
                    break
        if target and target in node_ids and len(links) < GRAPH_MAX_NODES * 2:
            if (rel, target) in seen_rat:
                continue
            seen_rat.add((rel, target))
            links.append(
                {
                    "source": f"file:{rel}",
                    "target": target,
                    "relation": "rationale_for",
                    "confidence": "INFERRED",
                    "source_file": rel,
                }
            )
    table_ids: dict[str, str] = {}
    for n in nodes:
        if n.get("kind") in ("table", "view"):
            table_ids.setdefault(n["label"], n["id"])
    pruned: list[dict] = []
    for e in links:
        if e["target"].startswith("sqlref:"):
            tname = e["target"][len("sqlref:") :]
            tid = table_ids.get(tname)
            if tid is None:
                continue
            e = {**e, "target": tid}
        pruned.append(e)
    return {"nodes": nodes, "links": pruned}


def _graph_degrees(data: dict) -> dict[str, int]:
    deg: dict[str, int] = {}
    for n in data.get("nodes", []):
        deg[n["id"]] = 0
    for e in data.get("links", []):
        deg[e["source"]] = deg.get(e["source"], 0) + 1
        deg[e["target"]] = deg.get(e["target"], 0) + 1
    return deg


def _save_graph(
    workspace_root: Path, data: dict, target_label: str
) -> tuple[Path, Path]:
    report_dir = workspace_root / "context-reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    unique = uuid.uuid4().hex[:8]
    json_path = report_dir / f"graph_{timestamp}_{unique}.json"
    md_path = report_dir / f"graph_report_{timestamp}_{unique}.md"
    envelope = {
        "nodes": sorted(data.get("nodes", []), key=lambda n: n["id"]),
        "links": sorted(
            data.get("links", []),
            key=lambda e: (e["source"], e["target"], e["relation"]),
        ),
        "graph": {
            "schema_version": GRAPH_SCHEMA_VERSION,
            "graphify_version": None,
            "root": target_label,
        },
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(envelope, f, indent=1, sort_keys=False)
    deg = _graph_degrees(envelope)
    id2node = {n["id"]: n for n in envelope["nodes"]}
    sym_rank = sorted(
        ((d, nid) for nid, d in deg.items() if nid.startswith("sym:")), reverse=True
    )[:10]
    ext = sum(1 for e in envelope["links"] if e.get("confidence") == "EXTRACTED")
    inf = sum(1 for e in envelope["links"] if e.get("confidence") == "INFERRED")
    amb = len(envelope["links"]) - ext - inf
    n_docs = sum(1 for n in envelope["nodes"] if n.get("file_type") == "document")
    n_code = len(envelope["nodes"]) - n_docs
    lines = [
        f"# Graph Report - {target_label}",
        "",
        f"- **Generated:** {timestamp}",
        f"- **Schema:** {GRAPH_SCHEMA_VERSION}",
        f"- **Nodes:** {len(envelope['nodes'])} **Edges:** {len(envelope['links'])}",
        f"- **Documents:** {n_docs} doc nodes ({n_code} code)",
        f"- **Confidence:** EXTRACTED {ext} / INFERRED {inf} / AMBIGUOUS {amb}",
        "",
        "## God nodes (top by degree)",
        "",
    ]
    for d, nid in sym_rank:
        n = id2node.get(nid, {})
        lines.append(
            f"- {n.get('label', nid)} (degree {d}, {n.get('source_file', '?')})"
        )
    lines += [
        "",
        "## How to query",
        "",
        "- `query_graph` for scoped subgraphs",
        "- `explain_node` for one concept",
        "- `shortest_path` to trace two concepts",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def _resolve_graph_file(workspace_root: Path, graph_path: str | None) -> Path | None:
    report_dir = workspace_root / "context-reports"
    if graph_path:
        p = Path(graph_path)
        cand = p if p.is_absolute() else workspace_root / p
        try:
            cand.resolve().relative_to(workspace_root)
        except ValueError:
            return None
        if cand.is_file():
            return cand
        alt = report_dir / p.name
        if alt.is_file():
            return alt
        return None
    if not report_dir.is_dir():
        return None
    cands = sorted(
        report_dir.glob("graph_*.json"), key=lambda q: q.stat().st_mtime, reverse=True
    )
    return cands[0] if cands else None


def _load_graph_data(
    workspace_root: Path, graph_path: str | None
) -> tuple[dict | None, Path | None, str | None]:
    gp = _resolve_graph_file(workspace_root, graph_path)
    if gp is None:
        return None, None, "No graph found. Run build_graph first."
    try:
        data = json.loads(gp.read_text(encoding="utf-8"))
        return data, gp, None
    except Exception as e:
        return None, gp, f"Error reading graph {gp}: {e}"


def _graph_tokens(text: str) -> set[str]:
    """Split identifiers so natural words match code: snake_case parts plus
    camelCase parts, lowercased, minimum length 3. Deterministic."""
    toks: set[str] = set()
    for raw in re.findall(r"[A-Za-z0-9]+", text):
        for part in _GRAPH_TOKEN_SPLIT_RE.split(raw):
            for sub in part.split("_"):
                t = sub.lower()
                if len(t) >= 3:
                    toks.add(t)
    return toks


def _find_graph_nodes(nodes: list[dict], label: str) -> list[dict]:
    ll = label.lower()
    exact = [n for n in nodes if n.get("label", "").lower() == ll]
    if exact:
        return exact
    return [n for n in nodes if ll in n.get("label", "").lower()][:5]


def _graph_neighbors(
    data: dict, nid: str
) -> tuple[list[tuple[dict, dict]], list[tuple[dict, dict]]]:
    id2n = {n["id"]: n for n in data.get("nodes", [])}
    out: list[tuple[dict, dict]] = []
    inc: list[tuple[dict, dict]] = []
    for e in data.get("links", []):
        if e["source"] == nid and e["target"] in id2n:
            out.append((e, id2n[e["target"]]))
        elif e["target"] == nid and e["source"] in id2n:
            inc.append((e, id2n[e["source"]]))
    return out, inc


def _graph_bfs_path(
    data: dict, src: str, tgt: str, directed: bool = True
) -> list[tuple[str, dict, str]] | None:
    from collections import deque

    adj: dict[str, list[tuple[str, dict]]] = {}
    for e in data.get("links", []):
        adj.setdefault(e["source"], []).append((e["target"], e))
        if not directed:
            adj.setdefault(e["target"], []).append((e["source"], e))
    if src not in adj and src not in {n["id"] for n in data.get("nodes", [])}:
        return None
    prev: dict[str, tuple[str, dict]] = {src: ("", {})}
    dq = deque([src])
    while dq:
        cur = dq.popleft()
        if cur == tgt:
            break
        for nxt, e in sorted(adj.get(cur, []), key=lambda x: x[0]):
            if nxt not in prev:
                prev[nxt] = (cur, e)
                dq.append(nxt)
    if tgt not in prev:
        return None
    path: list[tuple[str, dict, str]] = []
    cur = tgt
    while cur != src:
        pc, e = prev[cur]
        path.append((pc, e, cur))
        cur = pc
    path.reverse()
    return path


def _graph_vocab(data: dict, limit: int = 500) -> list[str]:
    """Sorted vocabulary tokens from node labels. Powers zero-hit hints."""
    vocab: set[str] = set()
    for n in data.get("nodes", []):
        vocab |= _graph_tokens(n.get("label", ""))
        if len(vocab) >= limit:
            break
    return sorted(vocab)


def _suggest_vocab_tokens(
    vocab: list[str], toks: set[str], limit: int = 8
) -> list[str]:
    hints: list[str] = []
    for t in sorted(toks):
        for v in vocab:
            if v.startswith(t) or t in v or t.startswith(v):
                if v not in hints:
                    hints.append(v)
                if len(hints) >= limit:
                    return hints
    return hints
