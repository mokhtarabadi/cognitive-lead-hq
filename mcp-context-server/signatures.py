# Sibling Docs: README.md | Decisions: DECISIONS.md


"""Structural signature extraction via tree-sitter AST with regex fallback. Stdlib-pure: no MCP imports, no registration, no import back to server."""

import importlib
from pathlib import Path
from typing import Optional


_EXTENSION_LANG_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".go": "go",
    ".java": "java",
    ".jsp": "java",
    ".rs": "rust",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".swift": "swift",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "c_sharp",
}


_TS_QUERIES: dict[str, list[str]] = {
    "python": [
        "(function_definition name: (identifier) @name parameters: (parameters) @params) @sig",
        "(class_definition name: (identifier) @name) @sig",
    ],
    "javascript": [
        "(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
        "(class_declaration name: (identifier) @name) @sig",
        "(method_definition name: (property_identifier) @name) @sig",
        "(arrow_function) @sig",
        "(generator_function_declaration name: (identifier) @name) @sig",
    ],
    "typescript": [
        "(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
        "(class_declaration name: (type_identifier) @name) @sig",
        "(interface_declaration name: (type_identifier) @name) @sig",
        "(method_definition name: (property_identifier) @name) @sig",
        "(type_alias_declaration name: (type_identifier) @name) @sig",
        "(enum_declaration name: (identifier) @name) @sig",
        "(arrow_function) @sig",
    ],
    "go": [
        "(function_declaration name: (identifier) @name parameters: (parameter_list) @params) @sig",
        "(method_declaration receiver: (parameter_list) @receiver name: (field_identifier) @name) @sig",
        "(type_declaration (type_spec name: (type_identifier) @name)) @sig",
    ],
    "java": [
        "(method_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig",
        "(class_declaration name: (identifier) @name) @sig",
        "(interface_declaration name: (identifier) @name) @sig",
        "(enum_declaration name: (identifier) @name) @sig",
        "(record_declaration name: (identifier) @name) @sig",
    ],
    "rust": [
        "(function_item name: (identifier) @name parameters: (parameters) @params) @sig",
        "(struct_item name: (type_identifier) @name) @sig",
        "(enum_item name: (type_identifier) @name) @sig",
        "(trait_item name: (type_identifier) @name) @sig",
        "(type_item name: (type_identifier) @name) @sig",
        "(impl_item trait: (type_identifier) @name) @sig",
    ],
    "kotlin": [
        "(function_declaration name: (identifier) @name) @sig",
        "(class_declaration name: (identifier) @name) @sig",
    ],
}


_ts_language_cache: dict[str, object] = {}


def _get_ts_language(lang_id: str) -> object:
    if lang_id in _ts_language_cache:
        return _ts_language_cache[lang_id]
    pkg_name = f"tree_sitter_{lang_id}"
    try:
        mod = importlib.import_module(pkg_name)
        from tree_sitter import Language as TSLanguage

        if lang_id == "typescript":
            lang = TSLanguage(mod.language_typescript())
        else:
            lang = TSLanguage(mod.language())
        _ts_language_cache[lang_id] = lang
        return lang
    except Exception:
        _ts_language_cache[lang_id] = None
        return None


def _extract_signature_line(source_lines: list[str], start_row: int) -> str:
    first = source_lines[start_row].rstrip("\n").rstrip("\r")
    if not first.rstrip().endswith(",") and first.count("(") == first.count(")"):
        return first
    parts: list[str] = [first]
    for line in source_lines[start_row + 1 :]:
        stripped = line.rstrip("\n").rstrip("\r")
        parts.append(stripped)
        if ":" in stripped and not stripped.rstrip().endswith(","):
            break
        if stripped.rstrip().endswith("{"):
            break
        if stripped.rstrip().endswith("):") or stripped.rstrip().endswith(") {"):
            break
    return "\n".join(parts)


def _extract_via_tree_sitter(file_path: Path) -> Optional[str]:
    ext = file_path.suffix.lower()
    lang_id = _EXTENSION_LANG_MAP.get(ext)
    if not lang_id:
        return None
    lang = _get_ts_language(lang_id)
    if lang is None:
        return None
    queries = _TS_QUERIES.get(lang_id)
    if not queries:
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None
    source_bytes = content.encode("utf-8")
    from tree_sitter import Parser, Query, QueryCursor

    parser = Parser(lang)
    tree = parser.parse(source_bytes)
    source_lines = content.split("\n")
    seen: set[str] = set()
    signatures: list[str] = []
    for query_str in queries:
        try:
            q = Query(lang, query_str)
            qc = QueryCursor(q)
            matches = qc.matches(tree.root_node)
            for _pattern_index, captures in matches:
                sig_nodes = captures.get("sig", [])
                for node in sig_nodes:
                    start_row = node.start_point[0]
                    sig_line = _extract_signature_line(source_lines, start_row).strip()
                    if sig_line and sig_line not in seen:
                        seen.add(sig_line)
                        signatures.append(sig_line)
        except Exception:
            continue
    if not signatures:
        return None
    return f"### Signatures in {file_path}\n" + "\n".join(signatures)


# --- End tree-sitter ---

# Runaway-traversal guards (Task 177): a single wedged request (e.g. tree of
# "/") used to burn minutes of CPU on the single-threaded stdio server and
# starve every later tool call. These caps bound any single walk.
