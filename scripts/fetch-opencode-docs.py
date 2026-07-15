#!/usr/bin/env python3
"""Fetch all OpenCode docs pages from opencode.ai and save as markdown files."""

import httpx
import re
import os
import sys
from pathlib import Path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor, as_completed

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs" / "opencode"
BASE_URL = "https://opencode.ai"

PAGES = [
    ("intro", "/docs/"),
    ("config", "/docs/config/"),
    ("providers", "/docs/providers/"),
    ("network", "/docs/network/"),
    ("enterprise", "/docs/enterprise/"),
    ("troubleshooting", "/docs/troubleshooting/"),
    ("windows-wsl", "/docs/windows-wsl"),
    ("go", "/docs/go/"),
    ("tui", "/docs/tui/"),
    ("cli", "/docs/cli/"),
    ("web", "/docs/web/"),
    ("ide", "/docs/ide/"),
    ("zen", "/docs/zen/"),
    ("share", "/docs/share/"),
    ("github", "/docs/github/"),
    ("gitlab", "/docs/gitlab/"),
    ("tools", "/docs/tools/"),
    ("rules", "/docs/rules/"),
    ("agents", "/docs/agents/"),
    ("models", "/docs/models/"),
    ("themes", "/docs/themes/"),
    ("keybinds", "/docs/keybinds/"),
    ("commands", "/docs/commands/"),
    ("formatters", "/docs/formatters/"),
    ("permissions", "/docs/permissions/"),
    ("policies", "/docs/policies/"),
    ("lsp", "/docs/lsp/"),
    ("mcp-servers", "/docs/mcp-servers/"),
    ("acp", "/docs/acp/"),
    ("skills", "/docs/skills/"),
    ("references", "/docs/references/"),
    ("custom-tools", "/docs/custom-tools/"),
    ("sdk", "/docs/sdk/"),
    ("server", "/docs/server/"),
    ("plugins", "/docs/plugins/"),
    ("ecosystem", "/docs/ecosystem/"),
]

class MarkdownExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main = False
        self.main_depth = 0
        self.in_code = False
        self.in_heading = False
        self.in_paragraph = False
        self.in_list_item = False
        self.in_link = False
        self.skip_tags = 0
        self.output = []
        self.buffer = []
        self.code_buffer = []
        self.skip_tag_stack = []
        self.heading_level = 0
        self.list_level = 0
        self.in_ordered_list = False
        self.list_counter = 0
        self.table_mode = False
        self.in_table_row = False
        self.in_table_cell = False
        self.table_cells = []
        self.cell_idx = 0
        self.in_nav = False
        self.in_header = False
        self.in_footer = False
        self.in_aside = False
        self.in_figure = False
        self.figure_code = False
        self.skip_depth = 0
        self.title = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get("class", "")
        id_attr = attrs_dict.get("id", "")

        skip_classes = ["sidebar", "nav", "navbar", "pagination", "edit-link", "footer", "header-wrapper"]
        if any(c in class_name for c in skip_classes):
            self.skip_tag_stack.append(tag)
            self.skip_depth += 1
            if tag in ("nav", "header", "footer", "aside"):
                setattr(self, f"in_{tag}", True)
            return

        if tag in ("nav", "header", "footer", "aside") and self.skip_depth == 0:
            setattr(self, f"in_{tag}", True)
            self.skip_tag_stack.append(tag)
            self.skip_depth += 1
            return

        if self.skip_depth > 0:
            if not self.skip_tag_stack or self.skip_tag_stack[-1] != tag:
                self.skip_tag_stack.append("inner")
            return

        if tag == "main":
            self.in_main = True
            self.main_depth = 1
            return

        if not self.in_main:
            return

        if tag in ("script", "style"):
            self.skip_tag_stack.append(tag)
            self.skip_depth += 1
            return

        if tag == "h1":
            self.in_heading = True
            self.heading_level = 1
            self._flush_buffer()
        elif tag == "h2":
            self.in_heading = True
            self.heading_level = 2
            self._flush_buffer()
        elif tag == "h3":
            self.in_heading = True
            self.heading_level = 3
            self._flush_buffer()
        elif tag == "h4":
            self.in_heading = True
            self.heading_level = 4
            self._flush_buffer()
        elif tag == "p":
            self.in_paragraph = True
        elif tag == "code":
            parent = attrs_dict.get("class", "")
            if "language" in parent or parent.startswith("lang-"):
                self.in_code = True
                self.code_buffer = []
                lang = parent.replace("language-", "").replace("lang-", "")
                self.code_lang = lang
        elif tag in ("pre",):
            self.in_code = True
            self.code_buffer = []
            self.code_lang = ""
        elif tag == "a":
            self.in_link = True
            href = attrs_dict.get("href", "")
            self.link_href = href
        elif tag == "li":
            self.in_list_item = True
        elif tag == "ul":
            self.output.append("\n")
        elif tag == "ol":
            self.output.append("\n")
            self.list_counter = 0
        elif tag == "hr":
            self._flush_buffer()
            self.output.append("\n---\n")
        elif tag == "br":
            self.output.append("\n")
        elif tag == "img":
            alt = attrs_dict.get("alt", "image")
            src = attrs_dict.get("src", "")
            self.output.append(f"![{alt}]({src})")
        elif tag == "strong" or tag == "b":
            self.buffer.append("**")
        elif tag == "em" or tag == "i":
            self.buffer.append("*")
        elif tag == "table":
            self.table_mode = True
        elif tag == "tr":
            self.in_table_row = True
            self.table_cells = []
        elif tag in ("td", "th"):
            self.in_table_cell = True
            self.cell_buffer = []
        elif tag == "figure":
            self.in_figure = True
        elif tag == "details":
            pass
        elif tag == "summary":
            pass

    def handle_endtag(self, tag):
        if self.skip_depth > 0:
            if self.skip_tag_stack:
                popped = self.skip_tag_stack.pop()
                if popped == tag or popped == "inner":
                    self.skip_depth -= 1
                if self.skip_depth == 0:
                    if tag in ("nav", "header", "footer", "aside"):
                        setattr(self, f"in_{tag}", False)
            return

        if tag == "main":
            self.in_main = False
            return

        if not self.in_main:
            return

        if tag in ("script", "style"):
            return

        if tag == "h1" or tag == "h2" or tag == "h3" or tag == "h4":
            text = "".join(self.buffer).strip()
            if text:
                prefix = "#" * self.heading_level
                self.output.append(f"\n\n{prefix} {text}\n")
            self.buffer = []
            self.in_heading = False
        elif tag == "p":
            text = "".join(self.buffer).strip()
            if text:
                self.output.append(f"\n\n{text}\n")
            self.buffer = []
            self.in_paragraph = False
        elif tag in ("pre",):
            if self.code_buffer:
                code = "".join(self.code_buffer)
                lang = getattr(self, "code_lang", "")
                if not lang:
                    lang = ""
                self.output.append(f"\n\n```{lang}\n{code}\n```\n")
                self.code_buffer = []
            self.in_code = False
        elif tag == "code" and self.in_code:
            if self.code_buffer:
                code = "".join(self.code_buffer)
                lang = getattr(self, "code_lang", "")
                self.output.append(f"\n\n```{lang}\n{code}\n```\n")
                self.code_buffer = []
            self.in_code = False
        elif tag == "a":
            self.in_link = False
        elif tag == "li":
            text = "".join(self.buffer).strip()
            if text:
                self.output.append(f"\n- {text}")
            self.buffer = []
            self.in_list_item = False
        elif tag == "ul":
            pass
        elif tag == "ol":
            pass
        elif tag in ("strong", "b"):
            self.buffer.append("**")
        elif tag in ("em", "i"):
            self.buffer.append("*")
        elif tag == "table":
            self.table_mode = False
        elif tag == "tr":
            self.in_table_row = False
            if self.table_cells:
                header = "| " + " | ".join(self.table_cells[0]) + " |"
                sep = "| " + " | ".join(["---"] * len(self.table_cells[0])) + " |"
                self.output.append(f"\n\n{header}\n{sep}\n")
                for row in self.table_cells[1:]:
                    self.output.append(f"| {' | '.join(row)} |\n")
                self.table_cells = []
        elif tag in ("td", "th"):
            self.in_table_cell = False
            text = "".join(self.cell_buffer).strip()
            if self.table_cells and len(self.table_cells[-1]) <= self.cell_idx:
                self.table_cells[-1].append(text)
            elif not self.table_cells:
                self.table_cells.append([text])
            else:
                self.table_cells[-1].append(text)
            self.cell_buffer = []
            self.cell_idx += 1
        elif tag == "figure":
            self.in_figure = False
        elif tag == "details":
            pass

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        if not self.in_main:
            return
        stripped = data.strip()
        if not stripped and not self.in_code:
            return

        if self.in_code:
            self.code_buffer.append(data)
        elif self.in_table_cell:
            self.cell_buffer.append(data)
        elif self.in_heading or self.in_paragraph or self.in_list_item or self.in_link:
            self.buffer.append(data)
        elif self.in_figure:
            pass
        else:
            self.buffer.append(data)

    def handle_entityref(self, name):
        if self.skip_depth == 0 and self.in_main:
            char = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}.get(name, f"&{name};")
            if self.in_code:
                self.code_buffer.append(char)
            else:
                self.buffer.append(char)

    def _flush_buffer(self):
        if self.buffer:
            self.output.append("".join(self.buffer))
            self.buffer = []

    def get_markdown(self):
        return "".join(self.output).strip()


def fetch_page(name, path):
    url = f"{BASE_URL}{path}"
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        html = resp.text

        extractor = MarkdownExtractor()
        extractor.feed(html)
        content = extractor.get_markdown()

        title = path.rstrip("/").split("/")[-1] or "intro"
        safe_name = name.replace("/", "-")

        md = f"# {title.capitalize()}\n\n"
        md += f"> Source: {url}\n\n"
        md += content

        filepath = DOCS_DIR / f"{safe_name}.md"
        filepath.write_text(md, encoding="utf-8")
        return (name, "ok", len(md))
    except Exception as e:
        return (name, "error", str(e))


def main():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    total = len(PAGES)
    print(f"Fetching {total} pages into {DOCS_DIR}...")

    results = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        fut_map = {pool.submit(fetch_page, name, path): name for name, path in PAGES}
        for fut in as_completed(fut_map):
            name, status, detail = fut.result()
            results.append((name, status, detail))
            icon = "✓" if status == "ok" else "✗"
            print(f"  {icon} {name} ({detail})")

    ok_count = sum(1 for _, s, _ in results if s == "ok")
    err_count = sum(1 for _, s, _ in results if s == "error")
    print(f"\nDone: {ok_count} ok, {err_count} errors out of {total}")
    return 0 if err_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
