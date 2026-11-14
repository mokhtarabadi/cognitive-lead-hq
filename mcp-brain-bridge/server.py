#!/usr/bin/env -S uv run
# Sibling Docs: mcp-brain-bridge/README.md | Decisions: mcp-brain-bridge/DECISIONS.md
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.0,<2.0",
#     "httpx>=0.28",
# ]
# ///

"""Unified Brain bridge MCP server (Task 190, lean session-first gateway).

One tool. ``brain_turn`` is the automation path: the Hands builds a user
prompt from its current machine state (e.g. "QA engineer please make
the adversarial testing" + the task file), the server prepends the
latest system prompt (read from the global install) as the system
message, calls the LLM over the OpenAI Responses API via httpx, and
returns the output — with any machine XML blocks extracted. The Hands
locates files and pulls ranges with its own native OpenCode tools; the
bridge exposes no file tools.

``brain_turn``: the Hands builds a user prompt from its current machine
state (e.g. "QA engineer please make the adversarial testing" + the task
file), the server prepends the latest system prompt (read from the global
install) as the system message, calls the LLM over the OpenAI Responses
API via httpx, and returns the output — with any machine XML blocks
extracted.

Manager rule: if the output has XML, the Hands takes only the XML; if
no XML, the Hands takes the whole output. Admin questions inside the
output are relayed by the Hands to the Manager; the answer goes back
in as the next ``brain_turn`` user prompt. No gates, no per-persona
commands — the auto-load persona + current modes in the system prompt
cover identity.

Per-session chat history (manager order, Task 190; session-first since
Task 292): the LLM is stateless, so every ``brain_turn`` with a
``session_id`` loads that session's prior user/assistant messages from
its transcript file and sends them along — like a chat interface, first
message to last. One session thread spans every task in the work
session. Each session keeps its own conversation under the project's
sessions root
(``<project>/tasks/.sessions/<session_id>/transcript.jsonl``, JSON
lines). A bare ``task_id`` with no ``session_id`` falls back to the
task-keyed transcript for backward compatibility.
``BRAIN_SESSIONS_ROOT`` overrides that location. The old global directory
(``~/.config/opencode/brain-sessions``) is a read-only fallback for
history written before the per-project move; writes never land there.
History is bounded (last 40 messages) so long sessions cannot overflow
the context.

Transport: stdio FastMCP, mirroring the other servers. The model is
called over the OpenAI Responses API (``{api_base}/responses``) via
``httpx`` — plain HTTPS POST, no SDK needed. ``httpx`` is imported
lazily inside the call path so module import (and unit tests) never
need network access or provider credentials.
"""

from __future__ import annotations

import fcntl
import hashlib
import os
import re
import sys
import json
import logging
import tempfile
import threading
import time
import unicodedata
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Optional
from urllib.parse import urlsplit

from mcp.server.fastmcp import FastMCP

# Shared env loader lives in mcp-common. Prefer the installed package;
# fall back to the sibling source tree so plain `uv run <path>` and
# direct test imports keep working without a workspace install.
try:
    from mcp_common.env import load_env_files as _shared_load_env_files
except ImportError:
    _COMMON_SRC = Path(__file__).resolve().parent.parent / "mcp-common" / "src"
    if _COMMON_SRC.is_dir():
        sys.path.insert(0, str(_COMMON_SRC))
    from mcp_common.env import load_env_files as _shared_load_env_files


def _load_env_files(server_dir: Optional[Path] = None) -> Optional[str]:
    """Load `.env` files via the shared loader. Empty values count as
    unset, so blank `{env:…}` injections never shadow file values."""
    return _shared_load_env_files(
        server_dir if server_dir is not None else Path(__file__).resolve().parent
    )


_loaded_from = _load_env_files()
if _loaded_from is not None:
    print(f"brain-bridge: loaded env from {_loaded_from}", file=sys.stderr)

logger = logging.getLogger(__name__)

# Shared per-project sessions resolver lives in loop_guard (stdlib-only,
# zero coupling back to this module). Guarded import so the server never
# fails to load when run from an installed package without the sibling.
try:
    from mcp_brain_bridge.loop_guard import (  # type: ignore[import-not-found]
        legacy_sessions_root as _shared_legacy_root,
        project_sessions_root as _shared_project_root,
    )
except ImportError:
    try:
        from loop_guard import (  # type: ignore[import-not-found]
            legacy_sessions_root as _shared_legacy_root,
            project_sessions_root as _shared_project_root,
        )
    except ImportError:  # pragma: no cover - sibling missing
        print(
            "brain-bridge: loop_guard sibling missing under both import names; "
            "per-project sessions disabled, legacy global applies",
            file=sys.stderr,
        )
        _shared_project_root = None  # type: ignore[assignment]
        _shared_legacy_root = None  # type: ignore[assignment]

# Request preflight lives in preflight (stdlib-only, zero coupling back
# to this module). Same guarded import as loop_guard above: installed
# package first, sibling source tree second. Unlike loop_guard the
# import is REQUIRED — without it brain_turn cannot validate, so both
# names failing raises ImportError loudly instead of running unguarded.
try:
    from mcp_brain_bridge.preflight import (  # type: ignore[import-not-found]
        ALLOWED_STAGES as _ALLOWED_STAGES,
        PreflightError,
        require_bare_task_id,
        resolve_project_root as _resolve_project_root,
        validate_request as _validate_request,
    )
except ImportError:
    from preflight import (  # type: ignore[import-not-found]
        ALLOWED_STAGES as _ALLOWED_STAGES,
        PreflightError,
        require_bare_task_id,
        resolve_project_root as _resolve_project_root,
        validate_request as _validate_request,
    )

# Capability preflight lives in capability, the session ledger in
# session_ledger (both stdlib-only, zero coupling back to this module).
# Same guarded import as preflight above; REQUIRED for the same reason.
try:
    from mcp_brain_bridge.capability import (  # type: ignore[import-not-found]
        CapabilityBlockedError,
        evaluate as _evaluate_capability,
        format_relay_block as _format_relay_block,
        gate as _gate_capability,
    )
    from mcp_brain_bridge.session_ledger import (  # type: ignore[import-not-found]
        append_event as _append_ledger_event,
        checkpoint as _ledger_checkpoint,
    )
except ImportError:
    from capability import (  # type: ignore[import-not-found]
        CapabilityBlockedError,
        evaluate as _evaluate_capability,
        format_relay_block as _format_relay_block,
        gate as _gate_capability,
    )
    from session_ledger import (  # type: ignore[import-not-found]
        append_event as _append_ledger_event,
        checkpoint as _ledger_checkpoint,
    )

mcp = FastMCP("BrainBridge", host="127.0.0.1", port=8105)

# XML blocks the Brain may emit. Hands executes these; everything else
# is conversation. Kept as plain names (no angle brackets) for the regex.
# ``hotfix`` added per Task 215: the Code Reviewer emits hotfix instruction
# blocks on REJECTED_NEEDS_FIXES, and the old allowlist silently dropped
# them to REPORT.
XML_BLOCK_TAGS = (
    "hands_discovery_task",
    "hands_implementation_task",
    "hands_combined_task",
    "failure_report",
    "hotfix",
)

# Tolerance (Task 238 fix loop, Manager order: extraction must handle every
# operative tag form): real model output varies — attributes
# (``<hotfix id="1">``), any case (``<HOTFIX>``), whitespace
# (``<hotfix >``). All still mean the same instruction, so the matcher
# tolerates them instead of silently dropping to REPORT. Non-allowlisted
# tags (``reasoning_log`` etc.) never extract, in any case or form.
_XML_RE = re.compile(
    r"<(" + "|".join(XML_BLOCK_TAGS) + r")(?:\s[^>]*)?>.*?</\1\s*>",
    re.DOTALL | re.IGNORECASE,
)

# Truncation fallback: a transport cut can leave the trailing block without
# its close tag. A line-start allowlisted opener with no matching close is
# surfaced (opener onward, trailing prose cut at the first blank line
# followed by a non-XML line) instead of dropped — the Hands then sees
# broken XML and re-prompts rather than silently ignoring instructions.
# Line-start required so mid-sentence prose mentions never trigger it.
_XML_UNCLOSED_RE = re.compile(
    r"(?m)^[ \t]*<(" + "|".join(XML_BLOCK_TAGS) + r")(?:\s[^>]*)?>",
    re.IGNORECASE,
)

# Explicit ```xml fences hold REAL xml, not documentation — the info string
# is the author's own language tag. Only this fence type feeds the
# extraction fallback (Task 215); json/bare/tilde fences stay stripped.
# Line based, not a regex: CommonMark closes a fence only with a bare run of
# at least the opener's length, so a four-backtick ````xml body may safely
# contain three-backtick samples (the canonical way to wrap a Hands XML block
# that carries code), and a three-backtick body is closed by the first inner
# bare run — the case the rescue pass below repairs.
_XML_FENCE_OPEN_RE = re.compile(r"^[ \t]*(`{3,})xml[ \t]*$", re.IGNORECASE)
_FENCE_BARE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})[ \t]*$")
# Line-start allowlisted opener, used by the rescue scan. Anchoring matters:
# a literal ``<hotfix>`` inside a code sample sits mid-line, so the rescue
# picks the real control block instead of the sample.
_XML_START_RE = re.compile(
    r"(?m)^[ \t]*<(" + "|".join(XML_BLOCK_TAGS) + r")(?:\s[^>]*)?>",
    re.IGNORECASE,
)
# Fenced code blocks are documentation, not instructions — strip them
# before scanning, or a pasted XML example would false-positive.
# Covers ``` fences (any length 3+, closed OR unclosed to EOF) and
# ~~~ fences. Each pattern runs to the next matching close or \Z so an
# unclosed fence still strips to EOF instead of leaking.
_FENCE_RES = (
    re.compile(r"`{3,}[\s\S]*?(?:`{3,}|\Z)"),
    re.compile(r"~{3,}[\s\S]*?(?:~{3,}|\Z)"),
)

# Drops from the most recent _strip_fences call (first-200-char snippets).
# Informational only — lets brain_turn report fence-only output via debug.
_last_fence_drops: list[str] = []


def _strip_fences(text: str) -> tuple[str, list[str]]:
    """Remove ALL fenced blocks; record each dropped block's first 200 chars."""
    global _last_fence_drops
    dropped: list[str] = []
    clean = text
    for pat in _FENCE_RES:

        def _collect(m: re.Match) -> str:
            dropped.append(m.group(0)[:200])
            return ""

        clean = pat.sub(_collect, clean)
    _last_fence_drops = list(dropped)
    return clean, dropped


# Line-accurate fence recognition for the bare-block scan. `_strip_fences`
# removes spans with a non-nesting regex, so a fenced body that carries its
# own fenced samples is sliced mid-body and the leftover fragment reads like
# bare prose — an operator-shaped tag parked in a documentation sample then
# extracted as a real instruction. This scanner only drops what CommonMark
# treats as a fence: an opener line (run of 3+ backticks or tildes with an
# optional info string) through the next bare run of at least the same
# character and length.
_FENCE_OPEN_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")


def _mask_fenced_code(text: str) -> str:
    """Return the text with every fenced code block dropped, line-accurately.

    Only used to decide whether a *bare* (unfenced) control block exists, so
    dropping the masked lines instead of replacing them is fine: the caller
    re-scans the result and needs no offsets.
    """
    kept: list[str] = []
    fence_char = ""
    fence_len = 0
    for line in text.splitlines():
        if fence_char:
            stripped = line.strip()
            if (
                stripped
                and set(stripped) == {fence_char}
                and len(stripped) >= fence_len
            ):
                fence_char = ""
                fence_len = 0
            continue
        opener = _FENCE_OPEN_RE.match(line)
        if opener:
            run = opener.group(1)
            fence_char = run[0]
            fence_len = len(run)
            continue
        kept.append(line)
    return "\n".join(kept)


def _xml_fence_segments(output: str) -> list[tuple[int, int, int, str]]:
    """Locate every ```xml fence and return its slices, in document order.

    Line based on purpose: a fence closes only on a bare run of the same
    character at least as long as the opener, which is what lets a
    four-backtick ``xml fence carry three-backtick code samples. A
    three-backtick body that contains its own bare fence closes early, which
    the caller repairs with the forward rescue scan.

    Returns:
        ``(opener_start, body_start, body_end, body)`` per fence, where the
        offsets index ``output`` and ``body`` is the fenced text itself. An
        unclosed fence yields a body that runs to EOF.
    """
    lines = output.splitlines(keepends=True)
    offsets: list[int] = []
    cursor = 0
    for line in lines:
        offsets.append(cursor)
        cursor += len(line)

    segments: list[tuple[int, int, int, str]] = []
    index = 0
    while index < len(lines):
        opener = _XML_FENCE_OPEN_RE.match(lines[index].rstrip("\r\n"))
        if not opener:
            index += 1
            continue
        run = len(opener.group(1))
        scan = index + 1
        while scan < len(lines):
            closer = _FENCE_BARE_RE.match(lines[scan].rstrip("\r\n"))
            if closer and closer.group(1)[0] == "`" and len(closer.group(1)) >= run:
                break
            scan += 1
        if scan < len(lines):
            body_end = offsets[scan]
            body = "".join(lines[index + 1 : scan])
            next_index = scan + 1
        else:
            body_end = len(output)
            body = "".join(lines[index + 1 :])
            next_index = len(lines)
        segments.append(
            (offsets[index], offsets[index] + len(lines[index]), body_end, body)
        )
        index = next_index
    return segments


def _rescue_fenced_block(fragment: str) -> list[str]:
    """Recover the block a truncated fence body was wrapping.

    A three-backtick fence whose body carries its own fenced samples is closed
    early, so the complete block lives past the body. Take the first
    line-start allowlisted opener in the fragment and the first matching close
    tag after it. Line-start anchoring keeps operator-shaped literals inside
    code samples from winning the race.

    Args:
        fragment: Raw text from the fence opener to the next opener or EOF.

    Returns:
        A one-item list with the recovered block, or an empty list when no
        complete block exists (a genuinely truncated turn still rejects).
    """
    opener = _XML_START_RE.search(fragment)
    if not opener:
        return []
    return _extract_complete_blocks(fragment)[:1]


def _bare_blocks(text: str) -> list[str]:
    """Return bare blocks, skipping literals quoted inside an inline code span.

    The bare path tolerates a control block that starts mid-line (pinned by
    ``test_extract_multiple_blocks_in_order``). That tolerance also made a
    *quoted* sample extract as an instruction: a QA reply containing
    ``sample = "<hotfix>…</hotfix>"`` came back as ``XML_EXTRACTED`` with the
    fragment as its block. An odd number of backticks earlier on the same line
    means the match sits inside an inline code span, so it is prose, not an
    instruction; fenced code never reaches here (it is masked out first).
    """
    blocks: list[str] = []
    for match in _XML_RE.finditer(text):
        line_start = text.rfind("\n", 0, match.start()) + 1
        if text[line_start : match.start()].count("`") % 2 == 1:
            continue
        blocks.append(match.group(0))
    return blocks


def _extract_complete_blocks(text: str) -> list[str]:
    """Return complete allowlisted blocks whose opener starts a line.

    The fence path uses this instead of the mid-line tolerant ``_XML_RE``
    because a fenced body can hold code samples that mention an operator tag
    as a literal (``sample = "<hotfix>…</hotfix>"``): line-start anchoring
    keeps those samples out while every real block still matches, since the
    templates always start the root element at a line start.

    Args:
        text: A fence body or a forward rescue fragment.

    Returns:
        Verbatim blocks in document order.
    """
    blocks: list[str] = []
    cursor = 0
    while True:
        opener = _XML_START_RE.search(text, cursor)
        if not opener:
            return blocks
        tag = opener.group(1)
        closer = re.search(
            rf"</\s*{re.escape(tag)}\s*>", text[opener.end() :], re.IGNORECASE
        )
        if not closer:
            cursor = opener.end()
            continue
        end = opener.end() + closer.end()
        blocks.append(text[opener.start() : end])
        cursor = end


# Task ids become directory names. Strict allowlist: anything else
# (``..``, separators, empty) raises instead of being mangled.
_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

# Brain history ids are BARE task numbers (digits only, e.g. "215").
# Suffixed variants ("215qa", "215rev", "215plan") would key separate
# transcript directories and split one task's history — the tool entry
# rejects them (see _require_task_number, implemented in preflight).


def _require_task_number(task_id: object) -> str:
    """Fail-closed gate for the ``brain_turn`` task_id input.

    Delegates to ``preflight.require_bare_task_id`` (single
    implementation). Returns the stripped bare number. Raises ValueError
    for anything else (slugs, suffixed variants, empty, non-strings)
    BEFORE any history load, file attach, or model call — a wrong id
    must never silently start a second, empty history next to the real
    one.
    """
    return require_bare_task_id(task_id)


# Small context files bundled into every brain_turn (unless opted out).
# Task files can be huge — never stuffed whole; pulled via tools instead.
_BUNDLE_FILES = (
    "agents/cognitive-executor.md",
    "docs/conventions.md",
    "docs/architecture.md",
    "docs/data_model.md",
    "DESIGN.md",
)
_BUNDLE_MARKER = "=== agents/cognitive-executor.md ==="
_BUNDLE_FILE_CAP = 60000

#: Total cap for the assembled bundle (chars). Five files at the per-file
#: cap would reach 300k — this bounds the worst case so planning turns
#: stay lean and never time out on context size.
_BUNDLE_TOTAL_CAP = 150000

# Structural context pack: the newest generated tree report (written by the
# Hands via ``custom_context.create_tree_report``) is auto-appended to the
# bundle so a planning turn always starts with a real codebase map instead
# of guessing. The section is included ONLY when at least one report exists
# — an absent pack contributes nothing, never a noisy marker on every turn.
# ``_STRUCTURAL_FILE_CAP`` bounds the section; the shared
# ``_BUNDLE_TOTAL_CAP`` still bounds the whole bundle.
_STRUCTURAL_REPORT_GLOB = "context-reports/tree_report_*.md"
_STRUCTURAL_FILE_CAP = 40000
_STRUCTURAL_MARKER = "=== context-reports/tree_report (latest) ==="

# Text extensions readable for server-side path injection (task 0372:
# docs/reports AND source files — the Brain plans/reviews code, so code
# suffixes must inject; binaries stay rejected).
_ALLOWED_READ_SUFFIXES = frozenset(
    {
        # Docs / data (original task-210 scope).
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        # Source (task 0372): JVM, JS/TS, Python, Go, Apple, C/C++, misc.
        ".java",
        ".kt",
        ".kts",
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".ts",
        ".tsx",
        ".py",
        ".pyi",
        ".go",
        ".swift",
        ".m",
        ".mm",
        ".c",
        ".h",
        ".hpp",
        ".cpp",
        ".cc",
        ".cxx",
        ".cs",
        ".rb",
        ".php",
        ".scala",
        ".rs",
        ".dart",
        ".lua",
        ".r",
        ".ex",
        ".exs",
        ".sql",
        ".sh",
        ".bash",
        ".zsh",
        ".xml",
        ".gradle",
        ".css",
        ".scss",
        ".less",
        ".html",
        ".htm",
        # Config / data (skill-template sweep, task 0378 follow-up).
        ".properties",
        ".ini",
        ".cfg",
        ".conf",
        # Mobile resources (iOS skill).
        ".plist",
        ".strings",
        ".xcconfig",
        # Go modules (go skills reference go.mod/go.sum by name).
        ".mod",
        ".sum",
        # SQLDelight (android-kotlin skill).
        ".sqm",
        # Web / docs extras referenced across skills.
        ".mdx",
        ".csv",
        ".rst",
        ".fish",
        ".ejs",
        ".vue",
        ".svelte",
    }
)

#: Suffixes that are never sniffed for text, even when undecodable-safe:
#: known binary containers where content sniffing would only waste I/O.
#: Everything else unlisted falls through to the UTF-8/NUL sniff below.
_UNREADABLE_SUFFIXES = frozenset(
    {
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".zip",
        ".tar",
        ".gz",
        ".tgz",
        ".rar",
        ".7z",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".webp",
        ".ico",
        ".mp3",
        ".mp4",
        ".pdf",
        ".aar",
        ".keystore",
        ".jks",
    }
)


def _sniff_text_file(resolved: "Path") -> Optional[str]:
    """Best-effort bounded text read for paths with unlisted suffixes.

    Dotfiles, extensionless files, and other unlisted names may contain
    plain text. Read at most one byte beyond the configured cap so an
    oversized file can be rejected without reading its full contents.
    Return ``None`` for oversized, NUL-containing, unreadable, or
    non-UTF-8 content so the caller labels the path unavailable.
    """
    try:
        with resolved.open("rb") as stream:
            raw = stream.read(_READ_MAX_BYTES + 1)
    except OSError:
        return None
    if len(raw) > _READ_MAX_BYTES or b"\x00" in raw:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    # Reject binary-like control payloads that are valid UTF-8 and contain
    # no NUL. Preserve the whitespace controls routinely used in text files.
    if any(
        unicodedata.category(character) == "Cc" and character not in "\t\n\r\f"
        for character in text
    ):
        return None
    return text


# Per-turn Brain-output persistence (Task: brain-output-persistence).
# Every brain_turn writes one JSON artifact holding its extracted
# xml_blocks plus the full raw output, and the turn result carries the
# artifact's relative address as ``output_address`` so the Hands can
# read the tail with native tools when the inline payload is truncated.
# Directory is per-session scratch under the project's sessions root
# (regenerable, never source of truth). Retention is enforced at write
# time: at most BRAIN_OUTPUTS_MAX_FILES artifacts and
# BRAIN_OUTPUTS_MAX_BYTES total per session, oldest-first by mtime.
# The just-written file is never pruned by its own write. Temp files
# (``.tmp-`` prefix) never count toward the caps and are removed on
# any write failure, so a crash cannot leave a half-written artifact
# that a later read mistakes for a complete one.
BRAIN_OUTPUTS_MAX_FILES = 50
BRAIN_OUTPUTS_MAX_BYTES = 5242880

_BRAIN_OUTPUTS_LOCK = threading.RLock()


def _brain_outputs_dir(project_root, session_key):
    """Resolve (creating) the per-session brain-outputs directory.

    Deliberately narrower than the transcript resolver: ONLY the turn's
    explicit ``project_root`` is honored — never ambient env vars and
    never a cwd walk-up. That keeps unit tests (cwd = repo root) and
    stray environments from ever writing into a real ``tasks/`` tree,
    and it keeps persistence scoped to the project the turn declared.
    Raises OSError when no explicit root holding ``tasks/`` is given;
    the caller degrades to ``output_address = None`` instead of failing
    the turn.
    """
    key = str(session_key) if session_key else "unknown"
    # Collision-resistant: sanitize for filesystem safety AND append a short
    # hash of the original key so distinct keys that sanitize identically
    # (e.g. "ses/a" vs "ses?a") can never alias into one directory.
    safe_key = "".join(c if (c.isalnum() or c in ("-", "_")) else "_" for c in key)
    safe_key = safe_key.strip("_") or "unknown"
    try:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:8]
    except (UnicodeEncodeError, UnicodeDecodeError):
        raise OSError("brain-output session key is not encodable")
    safe_key = f"{safe_key}_{digest}"
    base = None
    if project_root:
        try:
            cand = Path(project_root).expanduser().resolve()
        except (OSError, RuntimeError):
            cand = None
        if cand is not None and (cand / "tasks").is_dir():
            base = cand / "tasks" / ".sessions"
    if base is None:
        raise OSError(
            "brain-output persistence needs an explicit project_root holding tasks/"
        )
    out_dir = base / safe_key / "brain_outputs"
    # Security: reject if the resolved path escapes project_root (symlink
    # escape). The resolved out_dir must stay under the resolved root.
    try:
        root_resolved = Path(project_root).expanduser().resolve()
        out_resolved = out_dir.resolve()
        out_resolved.relative_to(root_resolved)
    except (OSError, RuntimeError, ValueError):
        raise OSError("brain-output path escapes project_root (symlink or traversal)")
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def _sanitize_response_id(response_id):
    """Filesystem-safe prefix from a provider response id (or fallback)."""
    text = str(response_id or "noresp")
    safe = "".join(c if c.isalnum() else "_" for c in text)
    return safe[:32] or "noresp"


def persist_brain_turn_output(
    project_root,
    session_key,
    task_id,
    response_id,
    xml_blocks,
    full_output,
    truncated,
    clock,
):
    """Serialize each process-local artifact write and retention pass.

    The lock prevents concurrent bridge turns from pruning against stale
    directory snapshots. The private helper retains atomic temp-file
    replacement and the existing result-address contract.
    """
    with _BRAIN_OUTPUTS_LOCK:
        return _persist_brain_turn_output_locked(
            project_root=project_root,
            session_key=session_key,
            task_id=task_id,
            response_id=response_id,
            xml_blocks=xml_blocks,
            full_output=full_output,
            truncated=truncated,
            clock=clock,
        )


def _persist_brain_turn_output_locked(
    project_root,
    session_key,
    task_id,
    response_id,
    xml_blocks,
    full_output,
    truncated,
    clock,
):
    """Write one per-turn artifact atomically and enforce retention.

    Writes JSON via temp file plus ``os.replace`` (readers never see a
    partial file; ``uuid`` filenames keep concurrent turns collision-free),
    prunes oldest-first to the file/byte caps without ever deleting the
    just-written file, and returns the repo-relative POSIX address string
    stored as ``output_address``. Persistence is best-effort for the turn
    itself: callers must never let a persistence failure fail the turn —
    wrap the call so an OSError degrades to ``output_address = None``
    instead of raising.
    """
    out_dir = _brain_outputs_dir(project_root, session_key)
    for stale_temp in out_dir.glob(".tmp-*.json"):
        try:
            stale_temp.unlink()
        except FileNotFoundError:
            continue
    safe = _sanitize_response_id(response_id)
    filename = safe + "_" + uuid.uuid4().hex + ".json"
    target = out_dir / filename
    created = time.strftime("%Y-%m-%dT%H:%M:%SZ", clock())
    full_text = str(full_output or "")
    blocks = list(xml_blocks or [])
    # Byte counts use strict encoding; compute them inside the guard
    # below so a lone surrogate raises OSError instead of escaping.
    try:
        output_byte_count = len(full_text.encode("utf-8"))
        xml_byte_count = len(json.dumps(blocks).encode("utf-8"))
    except (TypeError, ValueError):
        raise OSError("brain-output artifact contains non-encodable text")
    payload = {
        "task_id": str(task_id or ""),
        "session_key": str(session_key or ""),
        "response_id": str(response_id or ""),
        "created_at_utc": created,
        "truncated": bool(truncated),
        "byte_counts": {
            "output": output_byte_count,
            "xml_blocks": xml_byte_count,
        },
        "xml_blocks": blocks,
        "full_output": full_text,
    }
    # Address is repo-relative POSIX so the Hands can open it from the
    # project root with native tools; never an absolute path (no leak
    # of machine layout into results or transcripts). project_root is
    # guaranteed truthy here: _brain_outputs_dir above raised otherwise.
    try:
        rel = target.relative_to(Path(project_root).expanduser().resolve())
        payload["address"] = str(rel).replace(os.sep, "/")
    except (OSError, RuntimeError, ValueError, TypeError):
        payload["address"] = str(
            Path("tasks")
            / ".sessions"
            / out_dir.parent.name
            / "brain_outputs"
            / filename
        ).replace(os.sep, "/")
    try:
        serialized_payload = json.dumps(payload, ensure_ascii=False)
        serialized_bytes = serialized_payload.encode("utf-8")
    except (TypeError, ValueError):
        raise OSError("brain-output artifact contains non-encodable text")
    if len(serialized_bytes) > BRAIN_OUTPUTS_MAX_BYTES:
        raise OSError("brain-output artifact exceeds the per-session byte cap")

    fd, tmp_name = tempfile.mkstemp(dir=str(out_dir), prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(serialized_bytes)
        os.replace(tmp_name, target)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    try:
        entries = [
            p
            for p in out_dir.iterdir()
            if p.is_file() and p.suffix == ".json" and not p.name.startswith(".tmp-")
        ]
        entries.sort(key=lambda p: p.stat().st_mtime)
        total = sum(p.stat().st_size for p in entries)
        while (
            len(entries) > BRAIN_OUTPUTS_MAX_FILES or total > BRAIN_OUTPUTS_MAX_BYTES
        ) and len(entries) > 1:
            # Never remove the just-written file, even if it sorts oldest
            # by mtime (clock skew, explicit utime in tests). Pick the
            # oldest *other* entry; if the only candidate is the target
            # itself, stop rather than delete it or miscount the cap.
            try:
                target_resolved = target.resolve()
            except (OSError, RuntimeError):
                target_resolved = None
            candidate = None
            for entry in entries:
                if entry == target:
                    continue
                if target_resolved is not None:
                    try:
                        if entry.resolve() == target_resolved:
                            continue
                    except (OSError, RuntimeError):
                        pass
                candidate = entry
                break
            if candidate is None:
                # Only the target remains; cannot prune further.
                break
            entries.remove(candidate)
            try:
                total -= candidate.stat().st_size
                candidate.unlink()
            except OSError:
                break
    except OSError:
        pass
    return payload["address"]


# Guardrail for path injection (state-machine hotfix round).
_READ_MAX_BYTES = 2_000_000  # oversized files are refused outright


def _workspace_root() -> Path:
    """Repo root for context reads; override via ``BRAIN_WORKSPACE_ROOT``.

    Resolution order (issue #24): an explicit ``BRAIN_WORKSPACE_ROOT``
    override wins outright; otherwise auto-resolve the ACTIVE project root
    (``BRAIN_PROJECT_ROOT``, then a cwd ``tasks/`` walk-up) so the bundle and
    the file-pull tools read the project the turn actually runs in, never the
    directory this bridge happens to be installed into. Only when both fail
    does it fall back to the install dir, with a loud stderr note naming the
    remedy.
    """
    override = os.environ.get("BRAIN_WORKSPACE_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    try:
        return _resolve_project_root(None, env=os.environ, cwd=Path.cwd()).resolve()
    except Exception as exc:  # defensive last resort: never break a read
        install_root = Path(__file__).resolve().parent.parent
        print(
            "brain-bridge: could not resolve the active project root "
            f"({exc}); falling back to the bridge install dir {install_root}. "
            "Set BRAIN_PROJECT_ROOT (or BRAIN_WORKSPACE_ROOT) to silence this.",
            file=sys.stderr,
        )
        return install_root


def _resolve_under_root(rel: str, root: Optional[Path] = None) -> Path:
    """Resolve ``rel`` under the workspace root; raise ValueError on escape."""
    base = (root if root is not None else _workspace_root()).resolve()
    candidate = (base / rel).resolve()  # realpath: kills symlink escape
    if candidate != base and base not in candidate.parents:
        raise ValueError(f"path outside workspace root: {rel!r}")
    return candidate


def _explicit_root(project_root: Optional[str]) -> Optional[Path]:
    """Coerce an optional project-root string to a resolved Path.

    ``None`` stays ``None`` so callers fall back to ``_workspace_root()``;
    this is the shared coercion for the file-pull tools so an explicitly
    passed root always beats ambient resolution (issue #24).
    """
    if project_root is None:
        return None
    return Path(project_root).expanduser().resolve()


_TASK_DIFF_BEGIN = "<!-- BEGIN_GIT_DIFF -->"
_TASK_DIFF_END = "<!-- END_GIT_DIFF -->"
_TASK_FILE_MARKER = "[task-file:"
_TASK_KANBAN_DIRS = ("in-progress", "qa", "backlog", "completed", "archive")
# Defaults only — both are overridable at runtime via environment
# variables (see _task_attach_cap / _task_diff_cap below). These caps
# bound a single attachment; the shared allocator bounds the whole turn.
_TASK_ATTACH_CAP = 60000
_TASK_DIFF_CAP = 200000


def _task_id_ok(tid: object) -> bool:
    """Allowlist for task ids (mirrors loop_guard): letters, digits,
    underscore, hyphen; must start alnum; max 64 chars. Blocks
    traversal (../), separators (/), and glob metacharacters (*?[]).
    Uses the module-level compiled _TASK_ID_RE (shared with the
    history-path sanitizer — do NOT redefine it here)."""
    return isinstance(tid, str) and bool(_TASK_ID_RE.match(tid))


def _resolve_task_file(task_id: str, project_root: Optional[str] = None) -> Path | None:
    """Resolve a Brain task_id to its task file (None when unresolvable).

    Tries `<task_id>-*.md` in each Kanban dir (lane order: in-progress,
    qa, backlog, completed, archive — first match wins; active work
    beats backlog), then
    progressively strips one known lane suffix (`-qa`, `-backlog`,
    `-in-progress`, `-completed`, `-archive`) so session id `194-qa`
    finds task file `194-*.md`, then falls back to the leading numeric
    id (`200-foo` → `200`) because task ids in this repo are numeric
    while callers often pass the full filename stem including the
    slug; hyphenated ids without a lane suffix or numeric head never
    over-strip. The allowlist rejects traversal,
    separators, and glob metacharacters before any filesystem touch.
    Roots tried in order: explicit ``project_root`` (when it holds a
    ``tasks/`` dir — the sessions resolver already honors it, the task
    resolver must too), then the workspace root. Never raises —
    returns None instead.
    """
    try:
        if not _task_id_ok(task_id):
            return None
        tid = task_id.strip()
        roots: list[Path] = []
        if project_root:
            _pr = Path(project_root).expanduser()
            try:
                if (_pr / "tasks").is_dir():
                    roots.append(_pr / "tasks")
            except OSError:
                pass
        roots.append(_workspace_root() / "tasks")
        candidates = [tid]
        for _suffix in ("-qa", "-backlog", "-in-progress", "-completed", "-archive"):
            if candidates[-1].endswith(_suffix) and len(candidates[-1]) > len(_suffix):
                candidates.append(candidates[-1][: -len(_suffix)])
        _head = candidates[-1].split("-", 1)[0]
        if _head.isdigit() and _head != candidates[-1]:
            candidates.append(_head)
        for cand in candidates:
            for root in roots:
                for lane in _TASK_KANBAN_DIRS:
                    matches = sorted((root / lane).glob(cand + "-*.md"))
                    if matches:
                        return matches[0]
        return None
    except Exception:
        return None


def _diff_block_end(tail: str) -> int:
    """Index of the closing marker in ``tail`` (the text after BEGIN).

    The marker string can appear INSIDE a diff body — a task that edits
    this very module defines ``_TASK_DIFF_END`` in its own source — so
    the FIRST occurrence is not reliably the block end. That made the
    diff attach stop a few lines into ``server.py`` and left the seat
    judging a change set it could not see.

    The injected shape is a fenced ```diff body followed by the marker,
    so when the body opens a fence the block ends at the first marker
    AFTER that fence closes. Blocks without a fence (hand-written, or
    the template placeholder) fall back to the first marker.
    """
    lead = len(tail) - len(tail.lstrip())
    body = tail[lead:]
    if body.startswith("```"):
        open_end = body.find("\n")
        if open_end >= 0:
            close = body.find("\n```", open_end)
            if close >= 0:
                line_end = body.find("\n", close + 1)
                if line_end < 0:
                    line_end = len(body)
                marker = tail.find(_TASK_DIFF_END, lead + line_end)
                if marker >= 0:
                    return marker
    return tail.find(_TASK_DIFF_END)


def _strip_task_diff(text: str, rel: str) -> tuple[str, int, bool]:
    """Cut ALL Factual Git Diff blocks; return (cleaned, omitted, truncated).

    An unclosed BEGIN (no END after it) cuts to EOF and sets
    truncated=True; a lone END marker is left untouched.
    """
    parts: list[str] = []
    rest = text
    omitted = 0
    truncated = False
    while True:
        start = rest.find(_TASK_DIFF_BEGIN)
        if start < 0:
            parts.append(rest)
            break
        parts.append(rest[:start])
        tail = rest[start + len(_TASK_DIFF_BEGIN) :]
        end = _diff_block_end(tail)
        if end < 0:
            omitted += tail.count("\n") + 1
            truncated = True
            break
        omitted += tail.count("\n", 0, end) + 1
        rest = tail[end + len(_TASK_DIFF_END) :]
    if not omitted:
        return text, 0, False
    note = (
        f"[Factual Git Diff omitted — {omitted} lines. You have no file "
        + "tools in this turn: quote the paths you need in your verdict "
        + "and the Hands will feed them as fed-context under the same "
        + "task_id.]"
    )
    if truncated:
        note += (
            " [diff truncated: unclosed block cut to EOF — scope past "
            "the cut is UNVERIFIABLE, never REJECTED]"
        )
    return "".join(parts) + note, omitted, truncated


def _build_task_attach(task_id: str, project_root: Optional[str] = None) -> str:
    """Assemble the labeled task-file block ('' when unresolvable).

    Contains the task file's working content (Goal/Notes/TODOs/AC/
    evidence/log) minus the Factual Git Diff block, fenced so the
    XML extractor never mistakes task prose for Brain output blocks.
    Content caps at _TASK_ATTACH_CAP chars. Never raises.
    """
    try:
        path = _resolve_task_file(task_id, project_root=project_root)
        if path is None:
            return ""
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            rel = path.resolve().relative_to(_workspace_root().resolve()).as_posix()
        except (OSError, ValueError):
            rel = path.name
        cleaned, _omitted, _truncated = _strip_task_diff(text, rel)
        _cap = _task_attach_cap()
        if len(cleaned) > _cap:
            cleaned = (
                cleaned[:_cap]
                + "\n[...truncated — remainder NOT sent. Judge visible "
                + "only; mark unseen UNVERIFIABLE, NEVER REJECTED. You "
                + "have no file tools: quote needed paths and the Hands "
                + "will feed them as fed-context under the same task_id.]"
            )
        tid = task_id.strip() if isinstance(task_id, str) else "task"
        # V1 guard: break fence parsing invisibly so embedded fences in
        # task content cannot close our block early.
        cleaned = cleaned.replace(chr(96) * 3, chr(96) * 2 + chr(8203) + chr(96))
        return (
            f"{_TASK_FILE_MARKER}{tid}: {rel}]\n" + "```markdown\n" + cleaned + "\n```"
        )
    except Exception as exc:  # never fail a turn on attach problems
        print(f"brain-bridge: task attach skipped ({exc})", file=sys.stderr)
        return ""


def extract_task_diff(text: str) -> str:
    """Return the raw Factual Git Diff block bodies, joined ('' when none).

    Pure: no filesystem touch. An unclosed BEGIN cuts to EOF.
    """
    bodies: list[str] = []
    rest = text
    while True:
        start = rest.find(_TASK_DIFF_BEGIN)
        if start < 0:
            break
        tail = rest[start + len(_TASK_DIFF_BEGIN) :]
        end = _diff_block_end(tail)
        if end < 0:
            bodies.append(tail)
            break
        bodies.append(tail[:end])
        rest = tail[end + len(_TASK_DIFF_END) :]
    return "\n".join(bodies)


def build_diff_attach(task_id: str, project_root: Optional[str] = None) -> str:
    """Assemble the labeled changed-hunks block.

    Contains the task file's Factual Git Diff content verbatim so QA and
    reviewer turns judge the actual changes, never a summary. Content
    caps at _TASK_DIFF_CAP chars with a truncation note that orders
    UNVERIFIABLE-not-REJECTED for unseen scope (the Brain has no file
    tools, so the note addresses pulls to the Hands, never to the Brain). When the hunks
    cannot attach, an inline UNAVAILABLE/EMPTY note is returned INSTEAD
    of "" — stderr is invisible to the model, so a silent "" made the
    Brain reject blind ("no diff present, cannot judge"); the inline
    note tells it WHY (unresolvable file vs empty diff block) and the
    remedy (pass project_root, or paste hunks inline). Never raises.
    """
    try:
        tid = task_id.strip() if isinstance(task_id, str) else "task"
        path = _resolve_task_file(task_id, project_root=project_root)
        if path is None:
            print(
                f"brain-bridge: diff attach skipped "
                f"(task file unresolvable for {task_id!r})",
                file=sys.stderr,
            )
            return (
                f"[changed-hunks:{tid}: UNAVAILABLE — task file "
                f"unresolvable for {task_id!r}. The server could not "
                f"find the task file (wrong project_root, or the task "
                f"lives in another install). Remedy: retry with the "
                f"correct project_root, or paste the Factual Git Diff "
                f"hunks inline. Do NOT reject blind on missing hunks."
            )
        text = path.read_text(encoding="utf-8", errors="replace")
        diff = extract_task_diff(text)
        if not diff.strip():
            print(
                f"brain-bridge: diff attach skipped "
                f"(no Factual Git Diff block in {path.name})",
                file=sys.stderr,
            )
            return (
                f"[changed-hunks:{tid}: EMPTY — no Factual Git Diff "
                f"block in {path.name} yet. Stage the diff first "
                f"(stage_and_inject_diff), then re-run this turn. "
                f"Do NOT reject blind on missing hunks."
            )
        try:
            rel = path.resolve().relative_to(_workspace_root().resolve()).as_posix()
        except (OSError, ValueError):
            rel = path.name
        _cap = _task_diff_cap()
        if len(diff) > _cap:
            diff = (
                diff[:_cap]
                + f"\n[...diff truncated at {_cap} chars — "
                + "hunks past this point were NOT sent. Judge only what "
                + "is visible above: pass visible scope, mark the unseen "
                + "remainder UNVERIFIABLE, and NEVER emit REJECTED on "
                + "evidence past the truncation point. You have no file "
                + "tools in this turn, so do NOT attempt to pull the "
                + "remainder yourself. If you need specific paths to "
                + "finish, quote them in your verdict and the Hands will "
                + "pull them via read_file and re-run QA.]"
            )
        # Same V1 guard as the task attach: break fence parsing invisibly
        # so embedded fences in diff content cannot close our block early.
        diff = diff.replace(chr(96) * 3, chr(96) * 2 + chr(8203) + chr(96))
        return f"[changed-hunks:{tid}: {rel}]\n" + "```diff\n" + diff + "\n```"
    except Exception as exc:  # never fail a turn on attach problems
        print(f"brain-bridge: diff attach skipped ({exc})", file=sys.stderr)
        tid = task_id.strip() if isinstance(task_id, str) else "task"
        return (
            f"[changed-hunks:{tid}: UNAVAILABLE — attach raised "
            f"({exc}). Retry the turn; if it persists, paste the "
            f"Factual Git Diff hunks inline. Do NOT reject blind "
            f"on missing hunks."
        )


def _failsafe_qa_attach(
    user_prompt: object,
    task_id: object,
    project_root: Optional[str] = None,
) -> str:
    """Return the diff-attach block for QA-like prompts ('' otherwise).

    Keyword gate only: fires when the prompt reads like a QA/reviewer
    turn ("qa engineer", "code reviewer", "adversarial"). Lets QA turns
    carry the changed hunks even when the caller forgot include_diff.
    Never raises (build_diff_attach never raises).
    """
    if _qa_like_prompt(user_prompt):
        return build_diff_attach(
            task_id.strip() if isinstance(task_id, str) else "",
            project_root=project_root,
        )
    return ""


def _latest_report_path(root: object, pattern: str) -> Optional[Path]:
    """Newest file matching ``pattern`` under ``root`` (mtime, then name).

    Accepts a ``Path`` OR a path-like/``str`` root (normalized here, so a
    caller passing a string never hits ``str.glob``). Returns ``None`` when
    nothing matches or the glob/stat fails. Never raises — a broken
    workspace must not fail a bundle build.
    """
    try:
        base = root if isinstance(root, Path) else Path(root)  # type: ignore[arg-type]
        matches = [p for p in base.glob(pattern) if p.is_file()]
        if not matches:
            return None
        return max(matches, key=lambda p: (p.stat().st_mtime, p.name))
    except Exception:  # never raise on a malformed/racing workspace
        return None


def _build_structural_pack(root: Optional[object] = None) -> str:
    """Labeled newest tree report for the Brain bundle ('' when none).

    The Hands generate the tree with
    ``custom_context.create_tree_report``; carrying it in the bundle gives
    the Brain a codebase map on the first planning turn without ever
    handing it code file tools — the ask-the-Hands loop stays intact.

    Robustness contract (never raises, and never leaks outside content):
    a ``str``/path-like root is normalized; a report that resolves outside
    the workspace root (symlink escape) is skipped, mirroring the file-pull
    tools; a zero-byte or whitespace-only report is treated as no grounding
    (''); the read is capped at ``_STRUCTURAL_FILE_CAP`` chars so an
    oversized report can never be slurped whole; triple backticks are
    neutralized with an invisible break so report fences cannot close a
    surrounding fence downstream. A present, non-empty report returns the
    labeled section with an honest ``[truncated]`` marker when it exceeds
    the cap.
    """
    try:
        base = root if root is not None else _workspace_root()
        base = base if isinstance(base, Path) else Path(base)  # type: ignore[arg-type]
        root_resolved = base.resolve()
        path = _latest_report_path(base, _STRUCTURAL_REPORT_GLOB)
        if path is None:
            return ""
        resolved = path.resolve()
        if resolved != root_resolved and root_resolved not in resolved.parents:
            return ""  # symlink escaped the workspace root — skip, never read
        try:
            if resolved.stat().st_size == 0:
                return ""
        except OSError:
            return ""
        with open(resolved, "r", encoding="utf-8", errors="replace") as handle:
            text = handle.read(_STRUCTURAL_FILE_CAP + 1)
        if not text.strip():
            return ""
        if len(text) > _STRUCTURAL_FILE_CAP:
            text = text[:_STRUCTURAL_FILE_CAP] + "\n[truncated: structural pack cap]"
        # Fence guard: same invisible-break trick the task and diff attaches
        # use, so an embedded ``` cannot close a fence in a later consumer.
        text = text.replace(chr(96) * 3, chr(96) * 2 + chr(8203) + chr(96))
        rel = resolved.relative_to(root_resolved).as_posix()
        return f"{_STRUCTURAL_MARKER} ({rel})\n{text}"
    except Exception:  # never raise: a bad report must not fail a bundle
        return ""


def _build_context_bundle(root: Optional[str] = None) -> str:
    """Assemble the labeled small-file bundle (never raises on Absent-File).

    ``root`` pins the project the bundle is read from (issue #24): when the
    caller already resolved the turn's project root it MUST pass it here, so
    the bundle follows the active project instead of the bridge install dir.
    ``None`` keeps the historical behaviour and falls back to
    ``_workspace_root()``.

    The per-file cap applies first; the total cap applies across files so
    five full files can never stuff 300k into one turn. Files past the
    total budget are marked skipped, never silently dropped. The truncation
    suffix length is reserved before slicing, so the appended marker can
    never push the total past the cap (off-by-suffix overflow).
    """
    _pinned = _explicit_root(root)
    root = _pinned if _pinned is not None else _workspace_root()
    parts: list[str] = []
    missing = 0
    total = 0
    capped = False
    suffix = "\n[truncated: bundle total cap]"
    for rel in _BUNDLE_FILES:
        header = f"=== {rel} ==="
        if capped:
            parts.append(header + "\n[skipped: bundle total cap]")
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except (FileNotFoundError, NotADirectoryError, OSError):
            parts.append(header + f"\n[missing: {rel}]")
            missing += 1
            continue
        if len(text) > _BUNDLE_FILE_CAP:
            text = text[:_BUNDLE_FILE_CAP] + "\n[truncated]"
        chunk = header + "\n" + text
        if total + len(chunk) > _BUNDLE_TOTAL_CAP:
            room = _BUNDLE_TOTAL_CAP - total
            if room > len(header) + 64 + len(suffix):
                parts.append(chunk[: room - len(suffix)] + suffix)
            else:
                parts.append(header + "\n[skipped: bundle total cap]")
            total = _BUNDLE_TOTAL_CAP
            capped = True
            continue
        parts.append(chunk)
        total += len(chunk)
    # Structural context pack appended LAST so the stable doc files keep
    # their positions in the prefix. Absent pack contributes nothing; the
    # shared total cap still bounds the whole bundle, with an honest
    # skip/truncate marker when the pack does not fit.
    _struct_text = _build_structural_pack(root)
    if _struct_text:
        _struct_header = _STRUCTURAL_MARKER
        _room = _BUNDLE_TOTAL_CAP - total
        # A skipped pack must NOT carry the grounding marker: the marker is
        # the signal `context_sufficiency_gaps` keys on, so emitting it with
        # no tree content would falsely report the turn as grounded.
        if capped or _room <= 0:
            parts.append("[structural pack skipped: bundle total cap]")
        elif len(_struct_text) <= _room:
            parts.append(_struct_text)
        elif _room > len(_struct_header) + 64 + len(suffix):
            parts.append(_struct_text[: _room - len(suffix)] + suffix)
        else:
            parts.append("[structural pack skipped: bundle total cap]")
        # The structural section is appended LAST, so pin the running total
        # to the cap and keep the "never exceeds the cap" invariant honest.
        total = _BUNDLE_TOTAL_CAP
    if missing:
        print(
            f"brain-bridge: context bundle skipped {missing} missing files",
            file=sys.stderr,
        )
    return "\n\n".join(parts)


# Prompt overrides must be real prompt files: .md only, resolved under
# the repo root or ~/.config/opencode (the two legitimate homes).
_PROMPT_SUFFIX = ".md"


def _bridge_root() -> Path:
    """Root that holds this bridge install (the repo root in a checkout).

    ``server.py`` lives at ``<root>/mcp-brain-bridge/server.py``, so the root
    is the parent's parent. In the global install that root is
    ``~/.config/opencode`` — the home that also carries the deployed prompt
    artifacts. One definition, so the prompt-home rules and the stage
    routing can never disagree about where "the repo" is.
    """
    return Path(__file__).resolve().parent.parent


def _check_prompt_path(path: Path) -> Path:
    """Resolve an override path and reject anything outside the two
    legitimate prompt homes or without a .md suffix."""
    resolved = path.expanduser().resolve()  # realpath: kills symlink escape
    roots = [
        _bridge_root(),
        Path.home() / ".config" / "opencode",
    ]
    if resolved.suffix.lower() != _PROMPT_SUFFIX or not any(
        resolved == root or root in resolved.parents for root in roots
    ):
        raise ValueError(f"system prompt override outside allowed roots: {path}")
    return resolved


# ---------------------------------------------------------------------------
# Stage-aware prompt routing (Task 396)
# ---------------------------------------------------------------------------
# The Brain used to ship the FULL system prompt (all seven personas) on
# every turn. The stage artifacts split it into a shared COMMON core plus
# ONE persona slice per stage, so a QA turn carries the QA persona alone
# and a planning turn carries the five planning seats.
#
# The routing table is NOT hard-coded here: the stage manifest
# (``prompts/stage-manifest.json``) is the single source of truth for both
# the assembler and this bridge, and this module only READS it.
#
# Degradation is one-directional: a known stage whose artifact is missing
# falls back to the full prompt. The Brain never sees an empty prompt
# because of a routing miss, and a routing miss never raises.

#: Repo-relative location of the stage routing table.
_STAGE_MANIFEST_RELPATH = Path("prompts") / "stage-manifest.json"

#: Artifact directory used when the manifest declares none.
_DEFAULT_STAGE_ARTIFACT_DIR = "build/stage-prompts"

#: Per-stage artifact filename template used when the manifest declares none.
_STAGE_ARTIFACT_FILENAME_TEMPLATE = "system-prompt.{stage}.md"

#: Manifest keys that may hold the artifact directory.
_ARTIFACT_DIR_KEYS = (
    "dir",
    "artifact_dir",
    "output_dir",
    "directory",
    "path",
    "stage_dir",
)

#: Manifest keys that may hold the per-stage artifact filename.
_ARTIFACT_NAME_KEYS = (
    "artifact",
    "artifact_file",
    "artifact_path",
    "filename",
    "file",
    "output",
)


def _load_stage_manifest() -> Optional[dict]:
    """Read the stage routing table (``prompts/stage-manifest.json``).

    Returns the parsed manifest, or None when it is absent, unreadable,
    malformed, or not a JSON object. A missing manifest must never break a
    turn: the caller degrades to the full prompt instead.

    Every degraded path reports itself on stderr. A silent degradation is
    indistinguishable from "this stage simply has no artifact", which would
    hide a corrupt routing table behind a working-looking turn.
    """
    path = _bridge_root() / _STAGE_MANIFEST_RELPATH
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as exc:
        print(
            f"[brain-bridge] stage manifest {path} is unreadable ({exc}); "
            "serving the full prompt.",
            file=sys.stderr,
        )
        return None
    try:
        data = json.loads(raw)
    except ValueError as exc:
        print(
            f"[brain-bridge] stage manifest {path} is not valid JSON ({exc}); "
            "serving the full prompt.",
            file=sys.stderr,
        )
        return None
    if not isinstance(data, dict):
        print(
            f"[brain-bridge] stage manifest {path} is not a JSON object; "
            "serving the full prompt.",
            file=sys.stderr,
        )
        return None
    return data


def _manifest_stages(manifest: Optional[dict]) -> dict:
    """Return the manifest's stage map (empty when it declares none).

    The canonical key is ``stages``. A manifest that names the map
    differently is still honoured when every entry looks like a stage
    declaration (it carries personas and/or an artifact name) — the bridge
    must not fall back to a hard-coded table just because the manifest
    picked another key.
    """
    if not isinstance(manifest, dict):
        return {}
    stages = manifest.get("stages")
    if isinstance(stages, dict):
        return stages
    for key, value in manifest.items():
        if key in ("artifacts", "personas", "common_fragments", "catalog"):
            continue
        if not isinstance(value, dict) or not value:
            continue
        if all(
            isinstance(entry, dict) and ("personas" in entry or "artifact" in entry)
            for entry in value.values()
        ):
            return value
    return {}


def _known_stages(manifest: Optional[dict]) -> tuple[str, ...]:
    """Stages this bridge can route, sorted.

    The manifest owns the ROUTING (which artifact serves which stage); the
    preflight gate owns the ADMISSION (which stage a caller may request).
    The union keeps the two from drifting: every stage the gate admits has
    a resolvable artifact path, even before the manifest is generated.
    """
    stages = set(_manifest_stages(manifest))
    stages.update(_ALLOWED_STAGES)
    return tuple(sorted(stages))


def _manifest_artifact_dir(manifest: Optional[dict]) -> str:
    """Repo-relative directory that holds the generated stage artifacts."""
    if isinstance(manifest, dict):
        artifacts = manifest.get("artifacts")
        if isinstance(artifacts, str) and artifacts.strip():
            return artifacts.strip()
        if isinstance(artifacts, dict):
            for key in _ARTIFACT_DIR_KEYS:
                value = artifacts.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        # A per-stage declaration is the fallback when the top-level
        # artifacts block names no directory.
        for entry in _manifest_stages(manifest).values():
            if isinstance(entry, dict):
                for key in _ARTIFACT_DIR_KEYS:
                    value = entry.get(key)
                    if isinstance(value, str) and value.strip():
                        return value.strip()
    return _DEFAULT_STAGE_ARTIFACT_DIR


def _manifest_artifact_name(manifest: Optional[dict], stage: str) -> Optional[str]:
    """Artifact path (or filename) the manifest declares for a stage."""
    entry = _manifest_stages(manifest).get(stage)
    if isinstance(entry, str) and entry.strip():
        return entry.strip()
    if isinstance(entry, dict):
        for key in _ARTIFACT_NAME_KEYS:
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _stage_artifact_relpath(manifest: Optional[dict], stage: str) -> str:
    """Repo-relative path of the artifact that serves ``stage``.

    The manifest may declare the artifact with its own directory
    (``build/stage-prompts/system-prompt.qa.md``) or with a bare filename
    (the directory then comes from the manifest's artifacts block). An
    absolute or escaping declaration is ignored: the artifact must stay
    inside the bridge root.
    """
    default = str(
        PurePosixPath(_manifest_artifact_dir(manifest))
        / _STAGE_ARTIFACT_FILENAME_TEMPLATE.format(stage=stage)
    )
    declared = _manifest_artifact_name(manifest, stage)
    if not declared:
        return default
    candidate = PurePosixPath(declared.replace("\\", "/"))
    if candidate.is_absolute() or ".." in candidate.parts:
        return default
    if len(candidate.parts) > 1:
        return str(candidate)
    return str(PurePosixPath(_manifest_artifact_dir(manifest)) / candidate)


def resolve_stage_prompt_path(stage: Optional[str]) -> Optional[Path]:
    """Resolve the prompt artifact that serves ``stage``.

    PURE and side-effect free: it reads the stage manifest (the single
    routing table shared with the assembler) and returns the path of the
    artifact carrying this stage's persona slice. Returns None for an
    unknown stage, an empty stage, or None — the caller then falls back to
    the full prompt.

    The returned path is not guaranteed to exist: a known stage whose
    artifact was never generated resolves here and falls back at load time.
    """
    if not isinstance(stage, str):
        return None
    name = stage.strip()
    if not name:
        return None
    manifest = _load_stage_manifest()
    if name not in _known_stages(manifest):
        return None
    root = _bridge_root()
    try:
        candidate = (root / _stage_artifact_relpath(manifest, name)).resolve()
        resolved_root = root.resolve()
    except OSError:
        return None
    # Containment: the artifact must stay inside the bridge root, so a
    # tampered manifest cannot point the loader at an arbitrary file.
    if candidate != resolved_root and resolved_root not in candidate.parents:
        return None
    return candidate


def _stage_prompt_candidates(stage: Optional[str]) -> list[Path]:
    """Ordered candidate paths for the artifact that serves ``stage``.

    Two homes hold the artifact: the bridge root (the generated
    ``build/stage-prompts/`` output the manifest points at) and the global
    install (``~/.config/opencode/<artifact>``), where the deployed bridge
    runs. The first candidate that exists wins.

    An unknown stage yields an empty list, and a candidate the prompt-home
    rules reject is skipped with a stderr note instead of raising: a
    routing miss must never turn a turn into an error.
    """
    resolved = resolve_stage_prompt_path(stage)
    if resolved is None:
        return []
    out: list[Path] = []
    for candidate in (resolved, Path.home() / ".config" / "opencode" / resolved.name):
        try:
            checked = _check_prompt_path(candidate)
        except ValueError as exc:
            print(
                f"brain-bridge: stage artifact rejected ({exc})",
                file=sys.stderr,
            )
            continue
        if checked not in out:
            out.append(checked)
    return out


def load_system_prompt(
    explicit_path: Optional[str] = None, stage: Optional[str] = None
) -> str:
    """Read the system prompt text.

    Resolution order:
      1. an explicit ``system_prompt_path`` override (highest priority);
      2. the STAGE artifact for a known stage, when it exists on disk
         (bridge-root artifact first, then the global install copy);
      3. the ``BRAIN_SYSTEM_PROMPT`` env override;
      4. the full committed prompt from the global install dir.

    A known stage whose artifact is missing degrades to the full prompt —
    never to an empty prompt, and never to an exception. Overrides are
    constrained to the two legitimate prompt homes (bridge root,
    ~/.config/opencode) with a .md suffix.
    """
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(_check_prompt_path(Path(explicit_path)))
    stage_candidates = _stage_prompt_candidates(stage)
    candidates.extend(stage_candidates)
    env_path = os.environ.get("BRAIN_SYSTEM_PROMPT", "").strip()
    if env_path:
        candidates.append(_check_prompt_path(Path(env_path)))
    candidates.append(Path.home() / ".config" / "opencode" / "system-prompt.md")
    for path in candidates:
        if path.is_file():
            # A known stage whose artifact never made it to disk fell back
            # to a lower-priority candidate. The note says so, because a
            # silent scope loss looks exactly like a routing bug to
            # whoever measures the per-stage token cost.
            if stage_candidates and path not in stage_candidates:
                print(
                    f"brain-bridge: no stage artifact for {stage!r}; "
                    "served the full system prompt",
                    file=sys.stderr,
                )
            # An UNKNOWN stage also degrades to the full prompt, but it
            # carries no warning at all today. The preflight gate rejects
            # an unknown stage before this point, so reaching here means an
            # internal caller bypassed the gate. Say so rather than let the
            # scope loss pass unnoticed.
            if stage and not stage_candidates:
                print(
                    f"brain-bridge: unknown stage {stage!r}; "
                    "served the full system prompt",
                    file=sys.stderr,
                )
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(
        "No system prompt found; checked: " + ", ".join(str(p) for p in candidates)
    )


def _extract_unclosed_tail(text: str) -> str | None:
    """Return the truncated trailing block for the first line-start
    allowlisted opener with no matching close tag after it, else None.
    Pure helper for the truncation fallback in ``extract_xml_blocks``.

    Two QA-hotfix guards keep broken output from becoming live
    instructions. First, the tag NAME alone decides allowlist membership:
    it is lowercased before the close-tag check, and attributes never
    participate (the opener regex already captures only the name). Second,
    trailing PROSE is cut: a blank line followed by a line that does not
    open XML ends the block, because prose after a broken block is
    conversation, not instructions — the Hands executes whatever lands in
    ``xml_blocks``. Pretty-printed XML (blank line followed by another
    ``<`` line) passes through untouched. Empty remainder means None.
    """
    for m in _XML_UNCLOSED_RE.finditer(text):
        # Lowercase: the close-tag search below is case-insensitive, and
        # the allowlist match above already ignored case — the name, not
        # its surface form or attributes, carries the decision.
        name = m.group(1).lower()
        close_re = re.compile(r"</" + name + r"\s*>", re.IGNORECASE)
        if close_re.search(text, m.end()):
            continue
        lines = text[m.start() :].split("\n")
        cut = len(lines)
        for i, line in enumerate(lines):
            if line.strip():
                continue
            # Blank line: peek at the next non-blank line. XML continues
            # only when it opens another tag; prose ends the block here.
            for nxt in lines[i + 1 :]:
                if not nxt.strip():
                    continue
                if not nxt.lstrip().startswith("<"):
                    cut = i
                break
            if cut != len(lines):
                break
        tail = "\n".join(lines[:cut]).rstrip()
        if tail:
            return tail
    return None


#: Strict XML reject codes. Bare unclosed trailing blocks and truncated
#: ```xml fences (no closed block inside) raise instead of extracting.
#: Non-string input raises the contract code. Explicit ```xml fences
#: holding complete allowlisted blocks extract via the fallback below
#: (manual copy-paste mode); other fences stay documentation-only.
STRICT_XML_FENCE_FALLBACK_CODE = "XML_STRICT_REJECT_FENCE_FALLBACK"
STRICT_XML_UNCLOSED_CODE = "XML_STRICT_REJECT_UNCLOSED_TAIL"
STRICT_XML_CONTRACT_CODE = "XML_STRICT_REJECT_CONTRACT"


def _strict_reject(code: str, msg: str) -> None:
    """Fail closed on lenient XML input with an explicit code.

    Never returns: raises ValueError carrying the code so the caller
    reports instead of executing repaired instructions.
    """
    raise ValueError(f"{code}: {msg}")


def extract_xml_blocks(output: str) -> list[str]:
    """Return verbatim XML control blocks in document order. Bare
    unfenced blocks extract first (automatic mode); when none exist,
    allowlisted blocks inside explicit ```xml fences extract as the
    manual copy-paste fallback (other fences stay documentation-only).
    Bare unclosed trailing openers are rejected, never repaired.
    Empty list means plain conversation — the Hands takes the whole
    output. Input contract is ``str``: non-string input raises
    ``ValueError`` with a strict code instead of a bare ``TypeError``."""
    if not isinstance(output, str):
        _strict_reject(
            STRICT_XML_CONTRACT_CODE,
            f"expected str input, got {type(output).__name__}",
        )
    _strip_fences(output)  # diagnostics only: populates _last_fence_drops
    # The bare scan runs on the line-accurate mask, never on the regex strip:
    # the strip mis-slices nested fences and would let a documentation sample
    # extract as a real block.
    clean = _mask_fenced_code(output)
    blocks = _bare_blocks(clean)
    if blocks:
        return blocks
    tail = _extract_unclosed_tail(clean)
    if tail:
        _strict_reject(
            STRICT_XML_UNCLOSED_CODE,
            "unclosed trailing block: re-emit the complete block bare or inside a four-backtick ```xml fence",
        )
    fence_blocks: list[str] = []
    segments = _xml_fence_segments(output)
    for index, (opener_start, body_start, body_end, body) in enumerate(segments):
        found = _extract_complete_blocks(body)
        if not found:
            # Rescue: a three-backtick fence cannot hold a body with its own
            # fenced samples (the inner bare run closes it), so the complete
            # block sits past the truncated body and the turn used to be
            # rejected outright (whole answer withheld, forcing a costly full
            # re-emit). Look forward from the opener, bounded by the next one;
            # a genuinely truncated block finds nothing and still falls
            # through to the strict reject.
            scan_end = (
                segments[index + 1][0] if index + 1 < len(segments) else len(output)
            )
            found = _rescue_fenced_block(output[opener_start:scan_end])
        fence_blocks.extend(found)
    if fence_blocks:
        return fence_blocks
    for _opener_start, _body_start, _body_end, body in segments:
        if _extract_unclosed_tail(body):
            _strict_reject(
                STRICT_XML_FENCE_FALLBACK_CODE,
                "truncated fenced block: re-emit the complete block bare or inside a four-backtick ```xml fence",
            )
    return []


#: Required phase markers per Hands block type (Task 245: semantic gate).
#: Mirrors the templates in ``prompts/fragments/09-hands_protocols.md``.
#: ``failure_report``/``hotfix`` are free-form — only non-empty bodies
#: are required. Matching is word-bound (like ``validate_plan_verdict``)
#: so prose mentions count and only genuinely phaseless blocks fail.
_HANDS_REQUIRED_PHASES = {
    "hands_discovery_task": (
        "validation_phase",
        "context_phase",
        "execution_phase",
        "summary_phase",
    ),
    "hands_implementation_task": (
        "validation_phase",
        "context_phase",
        "execution_phase",
        "bash_phase",
        "documentation_phase",
        "summary_phase",
    ),
    "hands_combined_task": ("validation_phase", "discovery_phase"),
    "failure_report": (),
    "hotfix": (),
}

_ROOT_RE = re.compile(r"\s*<\s*([A-Za-z_][\w.-]*)")

_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _phase_element_present(body: str, phase: str) -> bool:
    """True when ``body`` holds ``phase`` as an opening element.

    Bare words, HTML comments, closing tags, and text outside the root
    body never satisfy the gate — only ``<phase>`` or ``<phase ...>``
    inside the root counts.
    """
    return bool(re.search(rf"<\s*{re.escape(phase)}(?:\s[^>]*)?>", body, re.IGNORECASE))


def validate_hands_xml_blocks(blocks: object) -> list[str]:
    """Check extracted Brain XML against the Hands contract (pure, offline).

    Returns problem strings; empty means semantically valid. The tolerant
    syntax parser (``extract_xml_blocks``) stays unchanged — this runs
    after it and rejects only blocks that are structurally incomplete:
    unknown roots, missing close tags (truncation), empty bodies, or
    missing required phase markers. Valid existing outputs always pass.
    """
    if not isinstance(blocks, (list, tuple)) or not blocks:
        return ["no xml blocks to validate"]
    problems: list[str] = []
    for i, block in enumerate(blocks):
        if not isinstance(block, str) or not block.strip():
            problems.append(f"block {i}: empty block")
            continue
        m = _ROOT_RE.match(block)
        root = m.group(1).lower() if m else ""
        if root not in _HANDS_REQUIRED_PHASES:
            problems.append(f"block {i}: unexpected root <{root or '?'}>")
            continue
        tag = m.group(1) if m else root
        close_m = re.search(rf"</\s*{re.escape(tag)}\s*>", block, re.IGNORECASE)
        if not close_m:
            problems.append(f"block {i} <{root}>: missing close tag (truncated?)")
            continue
        open_m = re.search(rf"<\s*{re.escape(tag)}(?:\s[^>]*)?>", block, re.IGNORECASE)
        raw_body = (
            block[open_m.end() : close_m.start()]
            if open_m and close_m.start() >= open_m.end()
            else ""
        )
        body = _COMMENT_RE.sub("", raw_body)
        if not body.strip():
            problems.append(f"block {i} <{root}>: empty body")
            continue
        for phase in _HANDS_REQUIRED_PHASES[root]:
            if not _phase_element_present(body, phase):
                problems.append(
                    f"block {i} <{root}>: missing required <{phase}> element"
                )
    return problems


#: Required fields of a Brain plan verdict. Hands-side plan review checks
#: plan text for these before executing — a plan with no cites is
#: ungrounded and must be re-prompted, never executed.
_PLAN_VERDICT_FIELDS = ("verdict", "seats", "path", "steps", "cites")


def validate_plan_verdict(plan_text: object) -> list[str]:
    """Check Brain plan text for the five verdict fields (pure, offline).

    Returns problem strings; empty means valid. ``cites`` additionally
    requires at least one ``path:line``-shaped file reference, otherwise
    the plan is ungrounded.

    Field presence uses word-bound matching (``\\b``), not substring
    matching: a bare ``in`` check would accept ``path`` inside ``paths``
    or ``footpath`` and ``steps`` inside ``missteps``, letting a stub
    plan pass review. Word bounds force each field to appear as its own
    word, so only a genuinely sectioned verdict validates.
    """
    if not isinstance(plan_text, str) or not plan_text.strip():
        return ["plan text is empty"]
    lowered = plan_text.lower()
    problems = [
        f"plan text missing {field!r} field"
        for field in _PLAN_VERDICT_FIELDS
        if not re.search(rf"\b{re.escape(field)}\b", lowered)
    ]
    if "cites" not in problems and not re.search(r"\S+\.\w+:\d+", plan_text):
        problems.append("plan cites carry no file path with lines")
    return problems


#: Stages whose output is a plan the Brain must ground in repo context.
#: Only ``plan`` is gated; every other stage stays silent.
_PLAN_STAGE = "plan"

#: Markers that prove the Brain carries grounding this turn: the structural
#: pack section and the discovery-fed context block.
_FED_CONTEXT_MARKER = "[fed-context]"
_PINNED_FED_MARKER = "[pinned-fed-context]"


def context_sufficiency_gaps(
    stage: Optional[str],
    user_prompt: object,
    bundle_text: object,
    bundle_included: bool = True,
    has_server_paths: bool = False,
) -> list[str]:
    """Pure: grounding gaps for a planning turn ([] when sufficient).

    A ``plan``-stage turn is grounded only when BOTH hold: the bundle
    carries the structural pack, and the prompt/rendered text carries a
    fed-context block. Only ``plan`` is gated; every other stage (and a
    missing stage) returns ``[]`` so unrelated turns never warn.

    ``bundle_included`` reflects the caller's ``include_bundle`` choice:
    when the caller opted out of the bundle, the structural requirement is
    suppressed (there was never going to be a pack) instead of producing a
    false positive. Takes values only — no environment, no filesystem, no
    network, and never the diff or the API key.

    ``has_server_paths`` is set by the caller when the bridge rendered the
    ``paths`` slot this turn. A literal ``[path-injected:`` string inside
    user text never counts — only server-rendered path context grounds —
    so a typed marker cannot spoof the check.
    """
    if (stage or "").strip().lower() != _PLAN_STAGE:
        return []
    bundle = bundle_text if isinstance(bundle_text, str) else ""
    prompt = user_prompt if isinstance(user_prompt, str) else ""
    gaps: list[str] = []
    if bundle_included and _STRUCTURAL_MARKER not in bundle:
        gaps.append(
            "no structural pack (run create_tree_report, or ask the Hands "
            "for repo context before planning)"
        )
    if (
        _FED_CONTEXT_MARKER not in prompt
        and _PINNED_FED_MARKER not in prompt
        and not has_server_paths
    ):
        gaps.append("no fed-context block")
    return gaps


_CLOSURE_APPROVAL_WORDS = ("approved for closure", "close task")


def validate_closure_checklist(task_text: object) -> list[str]:
    """Check task text is close-ready (pure, offline).

    Returns problem strings; empty means ready. Closeout needs a
    ``QA_PASSED`` verdict line, a ``PO_REVIEW_PENDING`` reviewer state,
    the exact approval-word quote (only "Approved for closure" or
    "Close task" count — bare "approved" never does), and a non-empty
    Factual Git Diff block (content between the markers, not the empty
    placeholder). Anything missing must be fixed before the closure
    commit, never closed around.
    """
    if not isinstance(task_text, str) or not task_text.strip():
        return ["task text is empty"]
    lowered = task_text.lower()
    problems = []
    if not re.search(r"\bQA_PASSED\b", task_text):
        problems.append("task text missing QA_PASSED verdict")
    if not re.search(r"\bPO_REVIEW_PENDING\b", task_text):
        problems.append("task text missing PO_REVIEW_PENDING reviewer state")
    if not any(word in lowered for word in _CLOSURE_APPROVAL_WORDS):
        problems.append("task text missing exact approval-word quote")
    diff_match = re.search(
        r"<!-- BEGIN_GIT_DIFF -->(.*?)<!-- END_GIT_DIFF -->", task_text, re.DOTALL
    )
    if diff_match is None:
        problems.append("task text missing Factual Git Diff block")
    else:
        inner = diff_match.group(1).strip()
        inner = re.sub(r"```diff|```", "", inner).strip()
        if not inner or "will be automatically injected" in inner:
            problems.append("Factual Git Diff block is empty")
    return problems


def _get_brain_model() -> str:
    """LLM model for Brain turns; override via ``BRAIN_MODEL``."""
    default = "gpt-6-astra"
    return os.environ.get("BRAIN_MODEL", default).strip() or default


def _routing_enabled() -> bool:
    """Risk-aware routing master switch; default ON (Task 261).

    Blank/unset means enabled, so the routing baseline works with no
    ``.env`` entry at all. An explicit falsy value (``0/false/no/off``
    or anything unrecognized) turns routing off and restores the
    single-model behavior exactly; ``1/true/yes/on`` keeps it on."""
    raw = os.environ.get("BRAIN_RISK_ROUTING_ENABLED", "").strip().lower()
    if not raw:
        return True
    return raw in ("1", "true", "yes", "on")


#: Built-in per-tier model defaults (Task 261). They apply only when the
#: corresponding ``.env`` key is UNSET; an explicitly BLANK value falls
#: back to ``BRAIN_MODEL`` instead (see ``_get_model_low``).
_MODEL_LOW_DEFAULT = "deepseek/deepseek-v4.1-flash"
_MODEL_HIGH_DEFAULT = "openai/gpt-5.6-luna"


def _get_model_low() -> str:
    """Model for light turns; override via ``BRAIN_MODEL_LOW``.

    Three-state contract (Task 261): UNSET uses the built-in default so
    the routing baseline works with no ``.env`` entry; set-but-BLANK
    returns an empty string, which the pure resolver below maps back to
    ``BRAIN_MODEL``. The distinction is deliberate — an operator who
    clears the override gets the ``BRAIN_MODEL`` fallback, never a
    silent switch to the built-in routed model."""
    raw = os.environ.get("BRAIN_MODEL_LOW")
    if raw is None:
        return _MODEL_LOW_DEFAULT
    return raw.strip()


def _get_model_high() -> str:
    """Model for hard turns; override via ``BRAIN_MODEL_HIGH``.

    Same three-state contract as ``_get_model_low``: UNSET uses the
    built-in default, set-but-BLANK falls back to ``BRAIN_MODEL``."""
    raw = os.environ.get("BRAIN_MODEL_HIGH")
    if raw is None:
        return _MODEL_HIGH_DEFAULT
    return raw.strip()


#: Tier sets for routing. Case-sensitive on purpose: a lowercase
#: ``t0`` is an invalid tier and must fail safe to the default model.
_ROUTED_LOW_TIERS = frozenset({"T0"})
_ROUTED_HIGH_TIERS = frozenset({"T1", "T2"})

#: Default stage-to-tier map (Task 261): the hard turns get the strong
#: model, the light turns the cheap one. Overridable per stage through
#: ``BRAIN_STAGE_TIERS`` so no value is hardcoded beyond its default.
_DEFAULT_STAGE_TIERS: dict[str, str] = {
    "plan": "T2",
    "review": "T2",
    "implement": "T0",
    "qa": "T0",
    "closure": "T0",
}


def _get_stage_tiers() -> dict[str, str]:
    """Stage-to-tier map; override entries via ``BRAIN_STAGE_TIERS``.

    Format: ``stage:Tier`` pairs, comma-separated, e.g.
    ``plan:T2,qa:T0``. Overrides merge onto the built-in default, and
    an unusable pair (bad stage or unknown tier) is ignored rather
    than failing a turn."""
    mapping = dict(_DEFAULT_STAGE_TIERS)
    raw = os.environ.get("BRAIN_STAGE_TIERS", "").strip()
    if not raw:
        return mapping
    valid_tiers = _ROUTED_LOW_TIERS | _ROUTED_HIGH_TIERS
    for pair in raw.split(","):
        stage, _, tier = pair.partition(":")
        stage = stage.strip().lower()
        tier = tier.strip()
        if stage and tier in valid_tiers:
            mapping[stage] = tier
    return mapping


def resolve_stage_tier(
    stage: Optional[str], stage_tiers: dict[str, str]
) -> Optional[str]:
    """Pure stage-to-tier resolver (Task 261).

    Takes values only — no environment reads. Returns ``None`` for a
    missing or unknown stage, which the model resolver then treats as
    "no tier" and falls back to ``BRAIN_MODEL``."""
    key = (stage or "").strip().lower()
    if not key:
        return None
    return stage_tiers.get(key)


def resolve_routed_model(
    enabled: bool,
    risk_tier: Optional[str],
    default_model: str,
    model_low: str,
    model_high: str,
) -> str:
    """Pure tier-to-model resolver (Task 246).

    Takes values only — no environment reads, no network, and never
    the prompt, the task diff, or the API key (asserted by test: the
    signature is exactly these five parameters). Fail-safe: disabled,
    missing, or invalid tiers return ``default_model``; a blank
    per-tier override falls back to ``default_model`` for that tier."""
    if not enabled:
        return default_model
    tier = (risk_tier or "").strip()
    if tier in _ROUTED_LOW_TIERS:
        return (model_low or "").strip() or default_model
    if tier in _ROUTED_HIGH_TIERS:
        return (model_high or "").strip() or default_model
    return default_model


#: Prompt-cache split descriptor version. Bump only when the segment
#: framing below changes; consumers key stability on this number.
_CACHE_SPLIT_SCHEMA_VERSION = 2

#: Logical split boundary: everything up to and including the task
#: attach is the stable prefix; user input, injected paths, diffs,
#: fed context, and history form the dynamic suffix (Task 247).
_CACHE_SPLIT_BOUNDARY = "after_system_bundle_task_attach"

#: Memoized static-prefix hashes, keyed by the static INPUTS (the
#: three texts, held by reference — no copies). A hit means identical
#: static bytes, so the stored hash is the answer without re-hashing.
#: Bounded: oldest entry evicted past the cap.
_STATIC_SPLIT_CACHE: dict[tuple[str, str, str], str] = {}
_STATIC_SPLIT_CACHE_MAX = 64

#: Guard for cache lookup plus mutation (Task 305 C5). The bridge serves
#: concurrent turns, so check-then-set races without this lock.
_STATIC_SPLIT_LOCK = threading.Lock()

#: Test hook: counts static-hash computations (cache misses). Never
#: read on the hot path for logic — informational only.
_STATIC_SPLIT_COMPUTES = 0


def _frame_segment(label: str, text: str) -> bytes:
    """Deterministic framing: len + NUL + label + NUL + len + NUL + bytes.

    Both halves are length-prefixed so concatenation stays injective:
    labels are caller-controlled (history roles come from transcripts
    and may carry NULs), and an unprefixed label lets one segment
    list alias another's bytes. Lengths are always honest (computed
    here, never caller-supplied), so parsing left-to-right is unique
    and two different segment lists can never frame identically."""
    lab = label.encode("utf-8")
    data = text.encode("utf-8")
    return (
        str(len(lab)).encode()
        + b"\x00"
        + lab
        + b"\x00"
        + str(len(data)).encode()
        + b"\x00"
        + data
    )


def _static_prefix_hash(
    system_prompt: str, bundle_text: str, task_attach_text: str
) -> str:
    """SHA-256 over the framed static segments, memoized (Task 247).

    The lookup key is the static input tuple itself, so a repeat
    input costs zero new static hashes — the digest is computed only
    on a miss."""
    global _STATIC_SPLIT_COMPUTES
    key = (system_prompt, bundle_text, task_attach_text)
    with _STATIC_SPLIT_LOCK:
        cached = _STATIC_SPLIT_CACHE.get(key)
        if cached is not None:
            return cached
    framed = b"".join(
        (
            _frame_segment("system_prompt", system_prompt),
            _frame_segment("bundle_prepend", bundle_text),
            _frame_segment("task_attach_prepend", task_attach_text),
        )
    )
    digest = hashlib.sha256(framed).hexdigest()
    with _STATIC_SPLIT_LOCK:
        _STATIC_SPLIT_COMPUTES += 1
        if len(_STATIC_SPLIT_CACHE) >= _STATIC_SPLIT_CACHE_MAX:
            _STATIC_SPLIT_CACHE.pop(next(iter(_STATIC_SPLIT_CACHE)))
        _STATIC_SPLIT_CACHE[key] = digest
    return digest


def build_prompt_cache_split(
    system_prompt: str,
    bundle_text: str,
    task_attach_text: str,
    user_prompt: str,
    paths_text: str = "",
    diff_text: str = "",
    failsafe_text: str = "",
    fed_text: str = "",
    history: Optional[list] = None,
) -> dict[str, str]:
    """Pure static/dynamic split descriptor (Task 247).

    Provider-neutral sidecar metadata: hashes and fixed labels only —
    never prompt text, keys, diffs, paths, or history content. The
    static half covers the stable prefix (system + bundle + task
    attach); the dynamic half covers everything that may vary per
    turn (user input, path/diff/failsafe/fed-context appends, and
    the shipped history). Takes values only — no environment reads,
    no network, no mutation of the prompt."""
    static_hash = _static_prefix_hash(system_prompt, bundle_text, task_attach_text)
    frames = [
        _frame_segment("user_prompt", user_prompt),
        _frame_segment("paths_attach", paths_text),
        _frame_segment("diff_append", diff_text),
        _frame_segment("failsafe_append", failsafe_text),
        _frame_segment("fed_context", fed_text),
    ]
    for idx, turn in enumerate(history or []):
        role = turn.get("role", "") if isinstance(turn, dict) else ""
        content = turn.get("content", "") if isinstance(turn, dict) else ""
        frames.append(_frame_segment(f"history[{idx}].{role}", content))
    dynamic_hash = hashlib.sha256(b"".join(frames)).hexdigest()
    return {
        "schema_version": _CACHE_SPLIT_SCHEMA_VERSION,
        "split_boundary": _CACHE_SPLIT_BOUNDARY,
        "static_prefix_sha256": static_hash,
        "dynamic_suffix_sha256": dynamic_hash,
    }


def _env_flag(name: str) -> bool:
    """Read a boolean env switch (Task 329: request-shape opt-ins).

    Truthy values are ``1``/``true``/``yes``/``on`` (case-insensitive);
    everything else — including blank/unset — is off. Every new
    Responses parameter ships behind one of these switches defaulting
    to off, so wire bytes stay identical to the pre-329 shape until
    the operator opts in.
    """
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _prompt_cache_key(system_prompt: str) -> str:
    """Stable prompt-cache key from the static system prefix (Task 329 F4).

    The system prompt is byte-identical across turns, which is the ideal
    cache prefix. The key carries only a hash — never prompt text.
    """
    digest = hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()[:32]
    return "brain-" + digest


def _compaction_threshold() -> int:
    """Compaction token threshold for ``context_management`` (Task 329 F3).

    Override via ``BRAIN_COMPACTION_THRESHOLD`` (default 100000).
    Malformed or non-positive values fail loud.
    """
    raw = os.environ.get("BRAIN_COMPACTION_THRESHOLD", "100000").strip() or "100000"
    try:
        val = int(raw)
    except ValueError:
        raise ValueError(
            f"BRAIN_COMPACTION_THRESHOLD={raw!r} is not an integer; "
            "set a positive integer or leave it blank"
        )
    if val <= 0:
        raise ValueError(
            f"BRAIN_COMPACTION_THRESHOLD={raw!r} must be > 0; "
            "set a positive integer or leave it blank"
        )
    return val


#: Fallback chars-per-token before any provider measurement (Task 329 F3).
_CHARS_PER_TOKEN_DEFAULT = 4.0
#: Calibrated ratio from observed usage (module-global, updated per turn).
_calibrated_chars_per_token: Optional[float] = None


def _chars_per_token() -> float:
    """Chars-per-token ratio for the pre-send estimate (Task 329 F3).

    Explicit ``BRAIN_CHARS_PER_TOKEN`` wins (fail loud on malformed);
    otherwise the calibrated ratio from observed usage; otherwise 4.0.
    """
    raw = os.environ.get("BRAIN_CHARS_PER_TOKEN", "").strip()
    if raw:
        try:
            val = float(raw)
        except ValueError:
            raise ValueError(
                f"BRAIN_CHARS_PER_TOKEN={raw!r} is not a number; "
                "set a positive number or leave it blank"
            )
        if val <= 0:
            raise ValueError(
                f"BRAIN_CHARS_PER_TOKEN={raw!r} must be > 0; "
                "set a positive number or leave it blank"
            )
        return val
    if _calibrated_chars_per_token is not None:
        return _calibrated_chars_per_token
    return _CHARS_PER_TOKEN_DEFAULT


def _note_observed_ratio(chars: int, input_tokens: int) -> None:
    """Calibrate the estimator from one observed turn (Task 329 F3).

    Pure bookkeeping: a plausible observation (ratio inside [1, 8])
    replaces the ratio; garbage (non-positive inputs, absurd ratios)
    is ignored so a corrupt usage payload can never corrupt the guard.
    """
    global _calibrated_chars_per_token
    try:
        if chars <= 0 or input_tokens <= 0:
            return
        ratio = chars / input_tokens
    except (TypeError, ZeroDivisionError):
        return
    if 1.0 <= ratio <= 8.0:
        _calibrated_chars_per_token = ratio


#: Volatile execution-state keys that providers attach to response output
#: items but reject on input. Observed 2026-10-22: the Go gateway's
#: gpt-6-luna endpoint 400s with "Unknown parameter: 'input[N].status'"
#: when a replayed reasoning item still carries the status of the turn
#: that produced it (e.g. "completed"). muse-spark-1.3-contributor
#: silently accepts it, which is why this only surfaced after the model
#: switch. Sanitized at SEND time (not capture time) so transcripts
#: already on disk are fixed without migration; capture stays verbatim
#: for audit value.
_REPLAY_DROPPED_KEYS = frozenset({"status"})


#: Maximum input-item id length enforced by strict Responses providers
#: (observed 2026-10-22: gpt-6-luna 400s with "Invalid 'input[N].id':
#: string too long", length 67 vs cap 64). The platform itself mints
#: longer ids (e.g. rs_ + 64 hex chars), so over-long ids must be
#: dropped whole, never truncated — the id is bound to the item's
#: encrypted_content and editing it breaks decryption. Dropping only
#: loses encrypted-context continuity for that turn, never the turn.
_REPLAY_MAX_ID_LEN = 64


def _sanitize_replay_item(item: Any) -> Any:
    """Strip volatile execution-state keys from a replayed provider item.

    Keeps the item byte-identical (same object) when nothing needs
    stripping, so the F2 "replay verbatim" contract holds for the common
    case; returns a filtered copy only when a dropped key is present.
    Returns None when the whole item must be skipped: an ``id`` longer
    than the provider's input cap (strict providers 400 the turn).
    Non-dict items pass through untouched.
    """
    if not isinstance(item, dict):
        return item
    item_id = item.get("id")
    if isinstance(item_id, str) and len(item_id) > _REPLAY_MAX_ID_LEN:
        print(
            f"brain-bridge: dropping replayed item with "
            f"{len(item_id)}-char id (provider cap {_REPLAY_MAX_ID_LEN}); "
            f"continuity for that block is skipped, the turn proceeds",
            file=sys.stderr,
        )
        return None
    if not any(k in _REPLAY_DROPPED_KEYS for k in item):
        return item
    return {k: v for k, v in item.items() if k not in _REPLAY_DROPPED_KEYS}


def _build_request_body(
    system_prompt: str,
    history: Optional[list],
    effective_prompt: str,
    *,
    model: Optional[str] = None,
    effort: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> dict[str, Any]:
    """Assemble the Responses request body (Task 329 request-shape work).

    The base shape is the pre-329 contract — ``model``, ``input``,
    ``reasoning.effort``, ``max_output_tokens`` — plus ``temperature``
    when explicitly set (which still deletes ``reasoning``). Every new
    Responses parameter is opt-in behind an env switch defaulting to
    off, so the default wire bytes are byte-identical to before:

    - ``BRAIN_SEND_STORE`` → ``store: false`` (F1)
    - ``BRAIN_SEND_INCLUDE_ENCRYPTED`` → ``include:
      ["reasoning.encrypted_content"]`` (F1/F2)
    - ``BRAIN_SEND_CACHE_KEY`` → ``prompt_cache_key`` from the system
      prefix hash (F4)
    - ``BRAIN_SEND_TRUNCATION`` → ``truncation: "auto"`` (F3)
    - ``BRAIN_SEND_CONTEXT_MANAGEMENT`` → compaction entry (F3,
      record-only unless probed)
    - ``BRAIN_USE_INSTRUCTIONS`` → system prompt moves to top-level
      ``instructions`` instead of a ``role: system`` input item (F10)

    History items may carry ``phase`` (assistant only — replayed on the
    item per the official guidance) and ``provider_items`` (non-message
    output items such as reasoning blocks with encrypted content,
    replayed after their turn — F2; volatile execution-state keys like
    ``status`` are stripped at send time since strict providers reject
    them on input). Old text-only transcripts
    carry neither key and replay exactly as before.
    """
    if model is None:
        model = _get_brain_model()
    if effort is None:
        effort = _get_reasoning_effort()
    if max_tokens is None:
        max_tokens = _get_max_tokens()
    use_instructions = _env_flag("BRAIN_USE_INSTRUCTIONS")
    if use_instructions:
        chat: list[dict[str, Any]] = []
    else:
        chat = [{"role": "system", "content": system_prompt}]
    for turn in history or []:
        if not isinstance(turn, dict):
            continue
        item: dict[str, Any] = {
            "role": turn.get("role", "user"),
            "content": turn.get("content", ""),
        }
        phase = turn.get("phase")
        if item["role"] == "assistant" and isinstance(phase, str) and phase:
            item["phase"] = phase
        chat.append(item)
        for extra in turn.get("provider_items") or []:
            if isinstance(extra, dict):
                sanitized = _sanitize_replay_item(extra)
                if sanitized is not None:
                    chat.append(sanitized)
    chat.append({"role": "user", "content": effective_prompt})
    body: dict[str, Any] = {
        "model": model,
        "input": chat,
        # Responses API shape: effort nests under reasoning (flat
        # reasoning_effort is rejected by strict providers, e.g.
        # OpenAI/OpenRouter 400 unsupported_parameter).
        "reasoning": {"effort": effort},
        "max_output_tokens": max_tokens,
    }
    if use_instructions:
        body["instructions"] = system_prompt
    if _env_flag("BRAIN_SEND_STORE"):
        body["store"] = False
    if _env_flag("BRAIN_SEND_INCLUDE_ENCRYPTED"):
        body["include"] = ["reasoning.encrypted_content"]
    if _env_flag("BRAIN_SEND_CACHE_KEY"):
        body["prompt_cache_key"] = _prompt_cache_key(system_prompt)
    if _env_flag("BRAIN_SEND_TRUNCATION"):
        body["truncation"] = "auto"
    if _env_flag("BRAIN_SEND_CONTEXT_MANAGEMENT"):
        body["context_management"] = [
            {"type": "compaction", "compact_threshold": _compaction_threshold()}
        ]
    # Blank-means-unset: only send temperature when explicitly set. A
    # non-blank temperature conflicts with reasoning effort on Responses
    # models, so drop the reasoning key when temperature is present.
    _temp_raw = os.environ.get("BRAIN_TEMPERATURE", "")
    if _temp_raw.strip():
        try:
            body["temperature"] = float(_temp_raw.strip())
        except ValueError:
            raise ValueError(
                f"BRAIN_TEMPERATURE={_temp_raw.strip()!r} is not a number; "
                "set a numeric value or leave it blank"
            )
        else:
            del body["reasoning"]
    return body


def _get_max_tokens() -> int:
    """Cap for Brain turns; override via ``BRAIN_MAX_TOKENS``.

    Defaults to 32768 rather than 16384: reasoning tokens are billed as
    output and count against this cap on most providers, so a smaller cap
    lets high-effort reasoning starve the visible answer (blank or
    truncated replies while the reasoning tokens are still charged).

    Fail-loud (Task 329 F9): a non-numeric or non-positive value raises
    instead of silently falling back — a quiet 32768 would change the
    output budget and the reasoning-budget warning threshold.
    """
    raw = os.environ.get("BRAIN_MAX_TOKENS", "32768").strip() or "32768"
    try:
        val = int(raw)
    except ValueError:
        raise ValueError(
            f"BRAIN_MAX_TOKENS={raw!r} is not an integer; "
            "set a positive integer or leave it blank"
        )
    if val <= 0:
        raise ValueError(
            f"BRAIN_MAX_TOKENS={raw!r} must be > 0; "
            "set a positive integer or leave it blank"
        )
    return val


# Pre-send token budget guard: values are operator-tunable via env
# (BRAIN_CONTEXT_WINDOW_TOKENS, BRAIN_BUDGET_MARGIN_TOKENS — see
# _provider_window_tokens/_budget_margin_tokens); built-in defaults match
# the provider 400 context length. Margin absorbs tokenizer drift.
_PROVIDER_CONTEXT_WINDOW_DEFAULT = 1048576
_BUDGET_SAFETY_MARGIN_DEFAULT = 8192


def _estimate_input_tokens_from_chars(budget_chars: int) -> int:
    """Estimate input tokens from character count for pre-send budget check. Why this exists: provider bills tokens while bridge only sees chars, so the calibrated ratio gives a fast estimate matching existing lines 3030 and 3056. Args budget_chars total chars of system plus effective plus history plus diffs plus context plus bundle. Returns integer token estimate. Edge: zero or negative input returns zero, never negative."""
    # Guard trivial input first so downstream math never sees negative totals.
    if budget_chars <= 0:
        return 0
    # Calibrated ratio (Task 329 F3): explicit BRAIN_CHARS_PER_TOKEN,
    # else measured from observed usage, else 4.0 — identical to the old
    # integer division when uncalibrated.
    return int(budget_chars / _chars_per_token())


def _pre_send_budget_fits(
    est_input_tokens: int,
    reserved_output_tokens: int,
    window: Optional[int] = None,
    margin: Optional[int] = None,
) -> bool:
    """Decide if estimated input plus reserved output fits inside provider window minus margin. Why: prevents provider 400 by blocking or trimming before send. Window and margin resolve from env when omitted so operators tune without code edits. Returns True when total fits, False when over."""
    # Resolve env-tunable numbers late so tests and operators override freely.
    if window is None:
        window = _provider_window_tokens()
    if margin is None:
        margin = _budget_margin_tokens()
    # Add first so overflow is visible in one total, then compare against window minus margin.
    total = est_input_tokens + reserved_output_tokens
    limit = window - margin
    return total <= limit


def _get_api_key() -> str:
    """Provider key. Fail-closed: an empty key cannot authenticate, so
    raise instead of sending a bare ``Bearer `` header."""
    key = os.environ.get("BRAIN_API_KEY", "").strip()
    if not key:
        raise RuntimeError("BRAIN_API_KEY is empty; set it in .env")
    return key


# Retry policy for provider calls: 3 attempts, exponential backoff.
#: Retryable statuses. INTENTIONALLY NARROW: only these 5xx (plus 429
#: and network timeouts) are retried. Other 5xx (501, 505, …) fall
#: through to the generic provider error. Do NOT expand this set
#: without a task: broadening retries burns latency on hopeless calls.
#: DOCUMENTATION ONLY — the branch below checks membership directly.
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}

# Fatal client errors: never retried — the request itself is wrong
# (bad auth, bad route, bad payload). Other 4xx fail fast the same way.
# NOTE (Task 329 F9): the old ``_FATAL_STATUS`` constant listed
# {400, 401, 403, 404, 422} but was never referenced — the branch below
# is range-based, so the constant was deleted rather than kept in sync.

# Overall deadline (seconds) for the whole retry sequence. Sleeps are
# capped by the remaining budget; hitting the deadline fast-fails instead
# of sleeping past it.
# 2026-10-22: was hard-coded 500, which fired before a single deep
# xhigh/max turn could finish (gpt-6-luna spends 14-19K reasoning tokens
# on a large prompt = 5-10 min), so long turns failed as
# "provider overall deadline hit (500.0s)" no matter the read timeout.
# Env-tunable; must stay above the proxy's upstream timeout when one is
# in the path (zen-proxy defaults to 900).
_DEFAULT_OVERALL_DEADLINE_S = 900.0


def _overall_deadline_s() -> float:
    """Whole-sequence provider deadline; override via BRAIN_OVERALL_DEADLINE_S.

    Fail-loud on a non-numeric or non-positive value: a silent fallback
    would change the timeout contract without saying so.
    """
    raw = os.environ.get("BRAIN_OVERALL_DEADLINE_S", "").strip()
    if not raw:
        return _DEFAULT_OVERALL_DEADLINE_S
    try:
        val = float(raw)
    except ValueError:
        raise RuntimeError(f"BRAIN_OVERALL_DEADLINE_S must be a number, got {raw!r}")
    if val <= 0:
        raise RuntimeError(f"BRAIN_OVERALL_DEADLINE_S must be > 0, got {raw!r}")
    return val


#: Billing/spend/quota 429 codes that must NEVER be retried (Task 329
#: F6, per the official error-codes guide): "Retrying billing, spend, or
#: quota errors won't restore API access." These fail terminal with an
#: actionable hint instead of burning three attempts plus backoff.
_TERMINAL_429_CODES = frozenset(
    {
        "credit_balance_exhausted",
        "organization_spend_limit_exceeded",
        "project_spend_limit_exceeded",
        "organization_usage_limit_exceeded",
        "insufficient_quota",
        "billing_hard_limit_exceeded",
    }
)


def _terminal_429_code(status: Any, data: Any) -> Optional[str]:
    """Return the terminal billing/spend/quota code, or None (pure).

    Only 429 responses are examined; anything else returns None so the
    existing retry/fatal branches keep their behavior. Unknown 429 codes
    and unparseable bodies return None — current retry behavior is the
    safe default against false-terminal classification.
    """
    if status != 429:
        return None
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            code = error.get("code")
            if isinstance(code, str) and code.strip().lower() in _TERMINAL_429_CODES:
                return code.strip().lower()
    return None


def _error_code_from_body(text: Any) -> Optional[str]:
    """Best-effort ``error.code`` extraction from a response body (pure).

    Never raises: non-JSON or misshapen bodies yield None.
    """
    try:
        if not isinstance(text, str) or not text.strip():
            return None
        data = json.loads(text)
    except (ValueError, TypeError):
        return None
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            code = error.get("code")
            if isinstance(code, str) and code.strip():
                return code.strip()
    return None


# Empty-output contract (Task 232): a REPORT with blank output is a
# transport/model flake, never a verdict. The bridge MUST NOT return it
# silently — it substitutes the EMPTY_OUTPUT_RETRY hint so the caller
# knows to retry lean once instead of acting on (or stalling on) nothing.
#: Machine-readable token callers assert on. NEVER rename without a task:
#: the Hands executor and regression tests match this exact string.
EMPTY_OUTPUT_RETRY = "EMPTY_OUTPUT_RETRY"

# Provider-diagnosis contract (Task 259): the Responses API can return a
# blank visible text while carrying a precise cause — a top-level error, a
# refusal content item, or ``status=incomplete`` with reason
# ``max_output_tokens`` (the reasoning trace consumed the whole output
# budget). Those are terminal for the turn and MUST NOT be misreported as
# the EMPTY_OUTPUT_RETRY transport flake: a lean retry keeps the identical
# effort and cap, so it can never fix an output-budget exhaustion.
#: Machine token: output budget exhausted by reasoning (not a flake).
OUTPUT_BUDGET_EXHAUSTED = "OUTPUT_BUDGET_EXHAUSTED"
#: Machine token: the provider returned a top-level error.
PROVIDER_ERROR = "PROVIDER_ERROR"
#: Machine token: the provider returned a refusal content item.
PROVIDER_REFUSAL = "PROVIDER_REFUSAL"
#: Reasoning efforts that realistically exhaust a small output cap.
_HIGH_EFFORT = {"high", "xhigh"}
#: Below this cap, high/xhigh effort risks a reasoning-only (blank) finish.
_REASONING_BUDGET_FLOOR = 32768

# Prompt-size advisory threshold (chars). Pure hint, never a cap: past
# this size the model has been observed returning empty output, so the
# bridge logs a lean-retry suggestion to stderr BEFORE the call.
_PROMPT_WARN_CHARS = 60000


def _retry_after_s(resp: Any) -> float:
    """Seconds from the Retry-After header (cap 120). 0 when missing/invalid."""
    try:
        raw = resp.headers.get("Retry-After", "")
    except Exception:
        return 0.0
    try:
        val = float(str(raw).strip().split(",")[0])
    except (ValueError, TypeError):
        return 0.0
    if val < 0:
        return 0.0
    return min(val, 120.0)


def _transport_fail(
    message: str,
    attempts: int,
    *,
    provider_status: Optional[int] = None,
    provider_code: Optional[str] = None,
    provider_type: Optional[str] = None,
) -> RuntimeError:
    """Build a transport RuntimeError carrying its attempt count.

    WS3 seam (GitHub issue 17): the learning send path accounts
    attempts across the failed round and the corrected retry.
    Message text is unchanged — existing message matches keep passing.

    Task 329 F6/F7: the provider status/code/type ride along as
    attributes so the caller can build a structured REPORT instead of
    re-parsing the message text. Attributes default to None.
    """
    err = RuntimeError(message)
    err.transport_attempts = attempts  # type: ignore[attr-defined]
    err.provider_status = provider_status  # type: ignore[attr-defined]
    err.provider_code = provider_code  # type: ignore[attr-defined]
    err.provider_type = provider_type  # type: ignore[attr-defined]
    return err


def _post_with_retry(client: Any, url: str, payload: dict[str, Any]) -> tuple[Any, int]:
    """POST with retries on transient failures (429/5xx + network
    timeouts). Returns (resp, attempts). Honors Retry-After on 429
    (plus small jitter) before exponential backoff. Final failure
    raises RuntimeError with status + URL path + a 500-char body
    snippet. Fatal client errors (400/401/403/404/422 and other 4xx)
    fail fast with a no-retry error. Headers (and the key) never
    enter error strings."""
    import random
    import time

    import httpx

    _deadline_s = _overall_deadline_s()
    deadline = time.monotonic() + _deadline_s
    last_status: int = -1
    last_snippet: str = "no attempt made"
    attempts = 0
    for attempt in range(3):
        if time.monotonic() >= deadline:
            raise _transport_fail(
                f"provider overall deadline hit ({_deadline_s}s) at "
                f"{url.rsplit('/', 1)[-1]}: {last_snippet}",
                attempts,
            )
        attempts += 1
        retry_after = 0.0
        try:
            resp = client.post(
                url,
                json=payload,
                headers={"Authorization": "Bearer " + _get_api_key()},
            )
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            last_status, last_snippet = -1, f"{type(exc).__name__}: {exc}"[:500]
        else:
            if resp.status_code < 400:
                return resp, attempts
            last_status, last_snippet = resp.status_code, resp.text[:500]
            if resp.status_code == 429:
                # Terminal billing/spend/quota codes (Task 329 F6): the
                # official guide says retrying these cannot restore
                # access, so fail at once with an actionable hint. The
                # body parse is best-effort — an unparseable body keeps
                # the current retry behavior.
                try:
                    _terminal_data = json.loads(resp.text) if resp.text else None
                except (ValueError, TypeError):
                    _terminal_data = None
                _terminal_code = _terminal_429_code(resp.status_code, _terminal_data)
                if _terminal_code is not None:
                    raise _transport_fail(
                        f"provider billing/quota error 429 "
                        f"({_terminal_code}, no retry) at "
                        f"{url.rsplit('/', 1)[-1]}: {last_snippet}. "
                        "Add credits or raise the organization/project "
                        "spend or usage limit before sending another request.",
                        attempts,
                        provider_status=resp.status_code,
                        provider_code=_terminal_code,
                    )
            if resp.status_code not in _RETRYABLE_STATUS:
                if 400 <= resp.status_code < 500:
                    raise _transport_fail(
                        f"fatal provider error {resp.status_code} (no retry) at "
                        f"{url.rsplit('/', 1)[-1]}: {last_snippet}",
                        attempts,
                        provider_status=resp.status_code,
                        provider_code=_error_code_from_body(resp.text),
                    )
                raise _transport_fail(
                    f"provider error {resp.status_code} at "
                    f"{url.rsplit('/', 1)[-1]}: {last_snippet}",
                    attempts,
                    provider_status=resp.status_code,
                    provider_code=_error_code_from_body(resp.text),
                )
            if resp.status_code == 429:
                retry_after = _retry_after_s(resp)
        base = 2**attempt
        if retry_after > 0:
            base = max(base, retry_after)
        delay = base + random.uniform(0, 0.25)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise _transport_fail(
                f"provider overall deadline hit ({_deadline_s}s) at "
                f"{url.rsplit('/', 1)[-1]}: {last_snippet}",
                attempts,
            )
        time.sleep(min(delay, remaining))
    raise _transport_fail(
        f"provider failed after 3 attempts ({last_status}) at "
        f"{url.rsplit('/', 1)[-1]}: {last_snippet}",
        attempts,
    )


def _resp_json(resp: Any) -> Any:
    """Parse a provider response. Raises RuntimeError with status +
    content-type + snippet on malformed bodies instead of leaking a
    bare decode error."""
    try:
        return resp.json()
    except (json.JSONDecodeError, ValueError) as exc:
        ctype = "?"
        try:
            ctype = resp.headers.get("content-type", "?")
        except Exception:
            pass
        raise RuntimeError(
            f"provider returned non-JSON (status {resp.status_code}, "
            f"{ctype}): {resp.text[:500]}"
        ) from exc


def _https_guard(base: str, env_key: str) -> str:
    """Fail closed on a provider base that would leak the Bearer key.

    HTTPS is always allowed. Plain HTTP is allowed ONLY for loopback hosts
    (a local proxy), where the bytes never leave the machine. Anything else
    raises instead of shipping the API key in cleartext over the network.
    """
    parsed = urlsplit(base)
    if parsed.scheme == "https":
        return base
    host = (parsed.hostname or "").lower()
    if parsed.scheme == "http" and host in {"localhost", "127.0.0.1", "::1"}:
        return base
    raise RuntimeError(
        f"{env_key}={base!r} must use https:// (http:// is allowed only for "
        f"localhost); refusing to send the API key in cleartext"
    )


def _get_read_timeout() -> float:
    """Read timeout (seconds) for the non-streaming provider call.

    Override via ``BRAIN_HTTP_READ_TIMEOUT`` (default 600). Reasoning models
    can think for minutes before the single response body arrives, so a fixed
    120s ceiling aborted valid high-effort turns. Malformed or non-positive
    values fail loud rather than silently falling back.
    """
    raw = os.environ.get("BRAIN_HTTP_READ_TIMEOUT", "600").strip() or "600"
    try:
        val = float(raw)
    except ValueError:
        raise RuntimeError(f"BRAIN_HTTP_READ_TIMEOUT must be a number, got {raw!r}")
    if val <= 0:
        raise RuntimeError(f"BRAIN_HTTP_READ_TIMEOUT must be > 0, got {raw!r}")
    return val


def _make_client() -> Any:
    """Build the provider HTTP client (lazy httpx: imports stay offline)."""
    import httpx

    return httpx.Client(
        timeout=httpx.Timeout(connect=10, read=_get_read_timeout(), write=30, pool=10)
    )


def _send_with_retry(
    make_client: Any,
    url: str,
    body: dict[str, Any],
) -> tuple[Any, int]:
    """POST with stateless retry (429/5xx + timeouts via _post_with_retry).

    No correction memory and no escalation: 4xx fails fast inside
    ``_post_with_retry`` and propagates to the caller. Renamed from
    ``_send_with_learning`` (Task 329 F9) — the old name promised a
    learning seam whose kwargs (task_key/task_id/session_id/project_root)
    the body never used.
    """
    with make_client() as client:
        resp, attempts = _post_with_retry(client, url, body)
    return resp, attempts


# Max prior messages re-sent per turn. Bounds context for long tasks.
_HISTORY_LIMIT = 40

# Max prompt + history chars per turn. History is never dropped to fit:
# the shipped transcript is bounded at load (``_HISTORY_LIMIT``), so this
# ceiling only bounds fresh attachments against modern long-context
# windows. At ~4.6 chars/token, 1M chars is ~217k input tokens.
# Operators who want a tighter ceiling set BRAIN_INPUT_BUDGET.
_INPUT_BUDGET = 1000000

# Assumed model window (chars) for the utilization monitor below.
# Informational only — providers differ; the send cap stays _INPUT_BUDGET.
_MODEL_WINDOW_CHARS = 200000

# Per-session context ledger filename (one JSON object per line per turn).
_CONTEXT_LEDGER_NAME = "context_ledger.jsonl"


# --- Configurable caps (blank-means-unset, mirrors mcp_common.env) ---
# Every reader below resolves the module global AT CALL TIME so tests
# (and callers) can monkeypatch the constant, and a blank env var means
# "use the documented default" — never zero, never a crash at import.


def _env_positive_int(name: str, default: int) -> int:
    """Read a positive integer env var; blank/unset yields ``default``.

    A malformed or non-positive value is a configuration error the
    operator must see, never a silently clamped cap.
    """
    raw = os.environ.get(name, "")
    if not raw.strip():
        return default
    try:
        value = int(raw.strip())
    except ValueError:
        raise ValueError(
            f"{name}={raw.strip()!r} is not an integer; set a positive "
            "integer or leave it blank"
        ) from None
    if value <= 0:
        raise ValueError(f"{name}={value} must be positive")
    return value


def _task_attach_cap() -> int:
    """Configured task-attachment cap (chars)."""
    return _env_positive_int("BRAIN_TASK_ATTACH_CAP", _TASK_ATTACH_CAP)


def _provider_window_tokens() -> int:
    """Provider context window (tokens) for the pre-send budget guard."""
    return _env_positive_int(
        "BRAIN_CONTEXT_WINDOW_TOKENS", _PROVIDER_CONTEXT_WINDOW_DEFAULT
    )


def _budget_margin_tokens() -> int:
    """Safety margin (tokens) for the pre-send budget guard."""
    return _env_positive_int(
        "BRAIN_BUDGET_MARGIN_TOKENS", _BUDGET_SAFETY_MARGIN_DEFAULT
    )


def _task_diff_cap() -> int:
    """Configured diff-attachment cap (chars)."""
    return _env_positive_int("BRAIN_TASK_DIFF_CAP", _TASK_DIFF_CAP)


def _ctx_paths_per_file_cap() -> int:
    """Configured per-file cap for ``context_paths`` (chars)."""
    return _env_positive_int("BRAIN_CTX_PER_FILE_CAP", _CTX_PATHS_PER_FILE)


def _ctx_paths_total_cap() -> int:
    """Configured total cap across ``context_paths`` (chars)."""
    return _env_positive_int("BRAIN_CTX_TOTAL_CAP", _CTX_PATHS_TOTAL)


def _input_budget_cap() -> int:
    """Configured hard send ceiling for system+prompt+history (chars)."""
    return _env_positive_int("BRAIN_INPUT_BUDGET", _INPUT_BUDGET)


def _model_window_chars() -> int:
    """Configured model-window estimate (chars), utilization monitor only."""
    return _env_positive_int("BRAIN_MODEL_WINDOW_CHARS", _MODEL_WINDOW_CHARS)


def _append_context_ledger(
    task_id: Optional[str],
    project_root: Optional[str],
    budget_chars: int,
    truncated_count: int,
    model: Optional[str] = None,
    risk_tier: Optional[str] = None,
    prompt_cache_split: Optional[dict] = None,
    paths: Optional[list] = None,
) -> None:
    """Best-effort utilization ledger: one JSON line per turn under the
    sessions root (Task 241 context-gap fix). Never raises — a ledger
    failure must not break the Brain turn it measures. Additive
    ``model``/``risk_tier`` (Task 246) and ``prompt_cache_split``
    (Task 247, hashes only) metadata — never prompt text, diffs,
    or keys."""
    try:
        row = {
            "task_id": task_id or "noid",
            "budget_chars": budget_chars,
            "est_tokens": budget_chars // 4,
            "util_pct": budget_chars * 100 // _model_window_chars(),
            "truncated": truncated_count,
            "model": model,
            "risk_tier": (risk_tier or "").strip() or None,
            "prompt_cache_split": prompt_cache_split,
            "paths": paths,
        }
        ledger = _sessions_root(project_root) / _CONTEXT_LEDGER_NAME
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with open(ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


# --- Monthly provider-usage counter (Task 374): quota watch. ---------------
# The Go-plan quota (~21k requests/month) is the binding constraint on the
# Brain, so every completed provider round-trip increments a tiny monthly
# JSON counter and warns on stderr past a configurable threshold. Read-only
# w.r.t. turn execution: best-effort writes, never raises, never blocks.
_USAGE_DIRNAME = "brain-usage"
_USAGE_CAP_DEFAULT = 21000
_USAGE_WARN_DEFAULT = 16800


def _usage_root() -> Path:
    """Dir holding monthly usage counters; overridable for tests."""
    override = os.environ.get("BRAIN_USAGE_ROOT", "").strip()
    if override:
        return Path(override).expanduser()
    return Path.home() / ".config" / "opencode" / _USAGE_DIRNAME


def _quota_cap() -> int:
    """Monthly request quota the warning is measured against."""
    return _env_positive_int("BRAIN_QUOTA_CAP", _USAGE_CAP_DEFAULT)


def _quota_warn_at() -> int:
    """Usage count at which the bridge starts warning on stderr."""
    return _env_positive_int("BRAIN_QUOTA_WARN_AT", _USAGE_WARN_DEFAULT)


def _usage_month_key() -> str:
    import time as _time

    return _time.strftime("%Y-%m", _time.gmtime())


def _record_brain_use(
    model: Optional[str] = None, usage: Optional[dict] = None
) -> Optional[dict]:
    """Increment this UTC month's turn counter; return usage summary.

    Returns ``{"count", "cap", "warn_at", "warn", "model"}`` plus one key per
    usage counter actually reported by the upstream (``input_tokens``,
    ``output_tokens``, ``total_tokens``, ``cached_tokens``). Counters the
    upstream omitted are absent from the return value, never ``None``, because
    this dict feeds quota and budget arithmetic where ``None`` raises or voids
    the total. The persisted monthly file stores the same counters under
    ``last_usage`` and is rewritten every turn, so that key is the most recent
    turn only, never a monthly sum. Returns ``None``
    when the counter cannot be maintained. File locking keeps concurrent
    turns from losing increments; every failure mode returns ``None``
    instead of raising so a broken counter can never break a turn.
    """
    try:
        # Usage counters are copied only when present as integers. A missing or
        # null counter must stay absent rather than become None, because this dict
        # feeds quota and budget arithmetic where None raises or voids the total.
        safe_usage: dict[str, int] = {}
        for key in ("input_tokens", "output_tokens", "total_tokens", "cached_tokens"):
            value = usage.get(key) if isinstance(usage, dict) else None
            if isinstance(value, int):
                safe_usage[key] = value

        root = _usage_root()
        root.mkdir(parents=True, exist_ok=True)
        path = root / (_usage_month_key() + ".json")
        import fcntl as _fcntl

        with open(path, "a+", encoding="utf-8") as f:
            _fcntl.flock(f.fileno(), _fcntl.LOCK_EX)
            try:
                f.seek(0)
                raw = f.read().strip()
                try:
                    data = json.loads(raw) if raw else {}
                except Exception:
                    data = {}
                count = int(data.get("count", 0) or 0) + 1
                f.seek(0)
                f.truncate()
                payload_to_store: dict[str, Any] = {"count": count, "model": model}
                # Named last_usage, not usage: this file is rewritten every
                # turn, so a bare "usage" key reads as a monthly total when it
                # only ever holds the most recent turn.
                if safe_usage:
                    payload_to_store["last_usage"] = safe_usage
                f.write(json.dumps(payload_to_store))
            finally:
                _fcntl.flock(f.fileno(), _fcntl.LOCK_UN)
        cap = _quota_cap()
        warn_at = _quota_warn_at()
        result_dict: dict[str, Any] = {
            "count": count,
            "cap": cap,
            "warn_at": warn_at,
            "warn": count >= warn_at,
            "model": model,
        }
        if safe_usage:
            result_dict.update(safe_usage)
        return result_dict
    except Exception:
        return None


def _warn_brain_quota(usage: Optional[dict]) -> None:
    """Stderr quota warning; silent unless the threshold is reached."""
    try:
        if not usage or not usage.get("warn"):
            return
        print(
            "brain-bridge: monthly Brain usage "
            f"{usage['count']}/{usage['cap']} requests reached "
            f"(warn at {usage['warn_at']}) — plan the remaining month "
            "or expect provider quota errors.",
            file=sys.stderr,
        )
    except Exception:
        pass


def _sessions_root(project_root: Optional[str] = None) -> Path:
    """Per-project sessions root: ``<project>/tasks/.sessions``.

    Resolution lives in ``loop_guard.project_sessions_root`` (single
    resolver, no duplicated logic): explicit ``BRAIN_SESSIONS_ROOT``
    wins, then project-root candidates holding ``tasks/``, then a cwd
    walk-up, then the legacy global dir. When the sibling is
    unavailable, fall back to the legacy global path so old projects
    keep working.
    """
    if _shared_project_root is not None:
        return _shared_project_root(project_root=project_root)
    override = os.environ.get("BRAIN_SESSIONS_ROOT", "").strip()
    if override:
        return Path(override).expanduser()
    # Sibling missing: best-effort per-project walk-up mirroring the
    # resolver order (param, env roots, cwd walk-up), else legacy global.
    cands: list[Path] = []
    if project_root:
        cands.append(Path(project_root).expanduser())
    for _key in ("BRAIN_PROJECT_ROOT", "BRAIN_WORKSPACE_ROOT"):
        _val = os.environ.get(_key, "").strip()
        if _val:
            cands.append(Path(_val).expanduser())
    try:
        cands.append(Path.cwd())
    except OSError:
        pass
    for _cand in cands:
        try:
            _node = _cand.resolve()
        except OSError:
            continue
        for _ in range(6):
            try:
                if (_node / "tasks").is_dir():
                    return _node / "tasks" / ".sessions"
            except OSError:
                break
            if _node.parent == _node:
                break
            _node = _node.parent
    return Path.home() / ".config" / "opencode" / "brain-sessions"


def _legacy_sessions_root() -> Path:
    """Pre-per-project global root (read fallback for unmigrated history)."""
    if _shared_legacy_root is not None:
        return _shared_legacy_root()
    return Path.home() / ".config" / "opencode" / "brain-sessions"


def _write_sessions_root(project_root: Optional[str] = None) -> Path:
    """Sessions root for WRITES: per-project, never the legacy global.

    An explicit ``BRAIN_SESSIONS_ROOT`` override is honored as-is (the
    operator chose it). Otherwise, when the resolver can only offer the
    legacy global fallback, writes go to ``cwd/tasks/.sessions`` with a
    loud stderr warn instead — a new write must never reintroduce
    cross-project bleed into the global dir. Reads keep the legacy
    fallback (see ``load_history``/``load_fed_context``).
    """
    override = os.environ.get("BRAIN_SESSIONS_ROOT", "").strip()
    if override:
        return Path(override).expanduser()
    root = _sessions_root(project_root)
    if root != _legacy_sessions_root():
        return root
    print(
        "brain-bridge: no project root found; writing to "
        "cwd/tasks/.sessions instead of legacy global",
        file=sys.stderr,
    )
    try:
        return Path.cwd() / "tasks" / ".sessions"
    except OSError:
        print(
            "brain-bridge: cwd unavailable; keeping legacy global write",
            file=sys.stderr,
        )
        return root


def _sanitize_task_id(task_id: str) -> str:
    """Strict allowlist — task ids become directory names, so anything
    outside ``^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`` (``..``, separators,
    empty) raises instead of being mangled."""
    if not _TASK_ID_RE.fullmatch(task_id):
        raise ValueError(
            f"bad task_id: {task_id!r} "
            "(legacy long IDs >64 chars: shorten/migrate to the <=64 allowlist)"
        )
    return task_id


def _transcript_path(task_id: str, project_root: Optional[str] = None) -> Path:
    return (
        _sessions_root(project_root) / _sanitize_task_id(task_id) / "transcript.jsonl"
    )


def _write_transcript_path(task_id: str, project_root: Optional[str] = None) -> Path:
    """Transcript path for WRITES (per-project; never legacy global)."""
    return (
        _write_sessions_root(project_root)
        / _sanitize_task_id(task_id)
        / "transcript.jsonl"
    )


def _legacy_transcript_path(task_id: str) -> Path:
    """Legacy global transcript (read fallback until migration copies it)."""
    return _legacy_sessions_root() / _sanitize_task_id(task_id) / "transcript.jsonl"


#: Per-line size guard (R5): one monster line can't blow memory on read.
_LINE_CAP_CHARS = 200_000

#: Transcript send-view compaction (Task 194): when a task transcript
#: grows past this many valid records, the load view becomes one
#: extractive digest record plus the newest records below. No model
#: call — the digest is deterministic (counts, ranges, models seen).
#:
#: This bounds ONLY what is sent to the model. The transcript file is
#: append-only and keeps every turn forever: the industry pattern
#: (OpenCode and other agentic clients) is to persist the full transcript and
#: compact the sent context, never to discard stored history.
_COMPACT_AFTER_MESSAGES = 30
_COMPACT_KEEP_LAST = 10
_SUMMARY_MAX_CHARS = 4000
#: Byte-size backstop: apply the compacted view whenever the transcript
#: file exceeds this, even when the turn count is below the threshold
#: (bounds huge turns on the SEND path only).
_COMPACT_FILE_BYTES = 200_000

#: Record keys preserved across load/compact cycles (traceability).
_META_KEYS = (
    "model",
    "prompt_hash",
    "truncated",
    "compacted",
    "models",
    "truncated_total",
    "compacted_count",
    # Task 329 F2 continuity: assistant phase, provider response id, and
    # replayable non-message output items (reasoning blocks with
    # encrypted content). Old records lack these keys and replay exactly
    # as before — the transcript format is backward compatible by key
    # presence, no version flag needed.
    "phase",
    "response_id",
    "provider_items",
)


def _parse_turns(raw: str) -> tuple[list[dict[str, Any]], int]:
    """Parse transcript text into turns, skipping corrupt lines.

    The single reader for stored transcripts: blank lines ignored,
    monster lines over ``_LINE_CAP_CHARS`` dropped with count,
    malformed JSON skipped, non-turn dicts skipped, traceability keys
    preserved. Returns ``(turns, skipped)``."""
    turns: list[dict[str, Any]] = []
    skipped = 0
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if len(line) > _LINE_CAP_CHARS:
            skipped += 1
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if (
            isinstance(entry, dict)
            and entry.get("role") in ("user", "assistant")
            and isinstance(entry.get("content"), str)
        ):
            turn: dict[str, Any] = {"role": entry["role"], "content": entry["content"]}
            for key in _META_KEYS:
                if key in entry:
                    turn[key] = entry[key]
            turns.append(turn)
        else:
            skipped += 1
    return turns, skipped


def _build_compacted(turns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build the compacted record list (pure: no I/O, no locks).

    Merges prior summary records instead of swallowing them: counts
    accumulate (``compacted_count``), model sets union, truncation
    totals sum, and the newest prior digests chain into the new digest
    text (clamped to ``_SUMMARY_MAX_CHARS``). Idempotent — the result
    holds 1 summary + the newest records, below the trigger."""
    prior = [t for t in turns if t.get("compacted") is True]
    fresh = [t for t in turns if not t.get("compacted")]
    prior_count = sum(int(t.get("compacted_count") or 0) for t in prior)
    total = prior_count + len(fresh)
    users = sum(1 for t in fresh if t.get("role") == "user")
    models: set[str] = set()
    for t in fresh:
        if t.get("model"):
            models.add(t["model"])
    for p in prior:
        for m in p.get("models") or []:
            models.add(m)
    trunc = sum(int(t.get("truncated") or 0) for t in fresh)
    trunc += sum(int(p.get("truncated_total") or 0) for p in prior)
    chain = " | ".join(str(p.get("content", ""))[:500] for p in prior[-2:])
    digest = (
        f"[compacted {total} turns: {users} user + "
        f"{len(fresh) - users} assistant; models={sorted(models)}; "
        f"truncated_total={trunc}]"
    )
    if chain:
        digest += f" prior: {chain}"
    digest = digest[:_SUMMARY_MAX_CHARS]
    summary: dict[str, Any] = {
        "role": "assistant",
        "content": digest,
        "compacted": True,
        "compacted_count": total,
        "models": sorted(models),
        "truncated_total": trunc,
    }
    return [summary] + fresh[-_COMPACT_KEEP_LAST:]


def load_history(
    task_id: str, limit: int = _HISTORY_LIMIT, project_root: Optional[str] = None
) -> list[dict[str, str]]:
    """Read a task's prior turns (oldest first), capped at ``limit``.
    Missing file means a fresh task — returns []. Corrupt lines are
    skipped, never fatal; per-load stats land in ``_last_load_stats``
    (``kept``/``skipped``) for tests and debugging. Traceability keys
    (model/prompt_hash/truncated/...) survive the round trip.
    The file itself is append-only — every turn ever written stays on
    disk. Transcripts past the count threshold (or the byte-size
    backstop) only have their LOAD VIEW compacted in memory: one
    digest record plus the newest records (see ``_build_compacted``),
    so storage keeps the full history while the send path stays
    bounded."""
    path = _transcript_path(task_id, project_root)
    if not path.is_file():
        # Cross-project bleed guard: the legacy global fallback
        # applies ONLY when no per-project root resolves. A project
        # with its own sessions dir but no file for this id gets a
        # fresh history — never another project's turns.
        legacy = _legacy_transcript_path(task_id)
        if _sessions_root(project_root) == _legacy_sessions_root() and legacy.is_file():
            print(
                "brain-bridge: reading legacy global session "
                f"({task_id}); migrate it under tasks/.sessions/",
                file=sys.stderr,
            )
            path = legacy
    if not path.is_file():
        _last_load_stats.update({"kept": 0, "skipped": 0})
        return []
    with path.open("r", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_SH)
        try:
            raw = fh.read()
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
    turns, skipped = _parse_turns(raw)
    # The file is append-only: every turn stays on disk. Only the view
    # handed to the model is bounded (see _build_compacted) — storage
    # keeps all history for the task, the send path stays inside budget.
    if (
        len(turns) > _COMPACT_AFTER_MESSAGES
        or path.stat().st_size > _COMPACT_FILE_BYTES
    ):
        turns = _build_compacted(turns)
    turns = turns[-limit:]
    _last_load_stats.update({"kept": len(turns), "skipped": skipped})
    if skipped:
        print(
            f"brain-bridge: load_history skipped {skipped} malformed lines",
            file=sys.stderr,
        )
    return turns


# Stats from the most recent load_history call (tests + debugging).
_last_load_stats: dict[str, int] = {"kept": 0, "skipped": 0}


def _transcript_form(user_prompt: str, rendered: list) -> str:
    """Compact storage form of a turn: own prompt + per-segment markers.

    The transcript is REPLAYED on every later turn, so persisting the
    assembled prompt with every attachment body inside it meant each
    turn re-sent the previous turn's attachments — one QA turn stored
    a 64,547-char user turn and every turn after it paid that cost
    again and again.

    Attachments are re-derived from disk on each turn (task file,
    diff, ``context_paths``, bundle), so nothing is lost by storing a
    marker line instead of the body: kind, path, sizes and part
    number keep the turn auditable. The live provider request still
    carries the full ``effective_prompt`` — this is storage only.
    """
    markers: list[str] = []
    for cand, _block, meta in rendered:
        kind = cand.get("kind", "attachment")
        path = cand.get("path", "")
        total = len(cand.get("text", ""))
        shown = total
        part = 1
        parts = 1
        if meta is not None:
            shown = meta.get("shown_chars", total)
            total = meta.get("total_chars", total)
            part = meta.get("part", 1)
            parts = meta.get("parts", 1)
        markers.append(
            f"[stored-attachment kind={kind} path={path} "
            f"shown_chars={shown} total_chars={total} part={part}/{parts}]"
        )
    if not markers:
        return user_prompt
    return "\n".join(markers) + "\n\n---\n\n" + user_prompt


def append_turn(
    task_id: str,
    role: str,
    content: str,
    model: Optional[str] = None,
    prompt_hash: Optional[str] = None,
    truncated: int = 0,
    project_root: Optional[str] = None,
    phase: Optional[str] = None,
    response_id: Optional[str] = None,
    provider_items: Optional[list] = None,
) -> None:
    """Append one turn to the task transcript (creates dirs as needed).

    Traceability keys ride on every record; unset stays None/0 so
    older callers keep working unchanged. Writes always go to the
    per-project path, never to the legacy global dir.

    Task 329 F2: assistant records may carry ``phase`` (commentary vs
    final answer, replayed on the item per the official guidance),
    ``response_id``, and ``provider_items`` (non-message output items
    such as reasoning blocks, replayed verbatim after their turn).
    """
    path = _write_transcript_path(task_id, project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "role": role,
        "content": content,
        "model": model,
        "prompt_hash": prompt_hash,
        "truncated": truncated,
    }
    if isinstance(phase, str) and phase:
        record["phase"] = phase
    if isinstance(response_id, str) and response_id:
        record["response_id"] = response_id
    if isinstance(provider_items, list) and provider_items:
        record["provider_items"] = provider_items
    with path.open("a", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            fh.write(json.dumps(record) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


#: Marker opening a fed discovery block inside a user prompt. Everything
#: after the marker line (up to an optional ``[/fed-context]`` line) is
#: pinned to the session and prepended to later turns until session end,
#: so planning always reasons from executed discovery, never memory.
_FED_CONTEXT_MARKER = "[fed-context]"
_FED_CONTEXT_END = "[/fed-context]"
_FED_CONTEXT_FILE = "fed_context.md"

#: Cap for pinned fed context (chars). Truncated with a note, never
#: silently dropped by history compaction or the input-budget middle drop
#: (it lives in its own file, outside the transcript window).
_FED_CONTEXT_CAP = 20000


def _fed_context_path(task_id: str, project_root: Optional[str] = None) -> Path:
    """Pinned fed-context file for a task (raises ValueError on bad id)."""
    return _sessions_root(project_root) / _sanitize_task_id(task_id) / _FED_CONTEXT_FILE


def _legacy_fed_context_path(task_id: str) -> Path:
    """Legacy global fed-context file (read fallback until migrated)."""
    return _legacy_sessions_root() / _sanitize_task_id(task_id) / _FED_CONTEXT_FILE


def _write_fed_context_path(task_id: str, project_root: Optional[str] = None) -> Path:
    """Fed-context path for WRITES (per-project; never legacy global)."""
    return (
        _write_sessions_root(project_root)
        / _sanitize_task_id(task_id)
        / _FED_CONTEXT_FILE
    )


def extract_fed_context(prompt: object) -> str:
    """Return the fed discovery block in ``prompt`` ('' when none).

    Pure: no filesystem touch. Takes text after the first ``[fed-context]``
    line, cuts at ``[/fed-context]`` when present, strips blank edges.
    """
    if not isinstance(prompt, str):
        return ""
    lines = prompt.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == _FED_CONTEXT_MARKER:
            start = i + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].strip() == _FED_CONTEXT_END:
            end = j
            break
    return "\n".join(lines[start:end]).strip()


def save_fed_context(
    task_id: str, content: str, project_root: Optional[str] = None
) -> None:
    """Pin fed discovery context (atomic write, capped).

    Raises ValueError on invalid task id; IO problems are logged and
    skipped, never raised. Empty content deletes the pin. Oversize
    content truncates with a note. Writes always go per-project.
    """
    path = _write_fed_context_path(task_id, project_root)
    if not content.strip():
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            print(f"brain-bridge: fed-context clear skipped ({exc})", file=sys.stderr)
        return
    if len(content) > _FED_CONTEXT_CAP:
        content = (
            content[:_FED_CONTEXT_CAP]
            + f"\n[...fed context truncated at {_FED_CONTEXT_CAP} "
            + "chars]"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    try:
        with tmp.open("w", encoding="utf-8") as fh:
            fh.write(content + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except OSError as exc:
        print(f"brain-bridge: fed-context save skipped ({exc})", file=sys.stderr)


def load_fed_context(task_id: str, project_root: Optional[str] = None) -> str:
    """Read pinned fed context ('' when none; never raises).

    Falls back to the legacy global file ONLY when no per-project
    root resolves; a project with its own sessions dir but no pin
    gets '' — never another project's pin. New pins are always
    written per-project."""
    try:
        return (
            _fed_context_path(task_id, project_root)
            .read_text(encoding="utf-8", errors="replace")
            .strip()
        )
    except (OSError, ValueError):
        pass
    if _sessions_root(project_root) != _legacy_sessions_root():
        return ""
    try:
        return (
            _legacy_fed_context_path(task_id)
            .read_text(encoding="utf-8", errors="replace")
            .strip()
        )
    except (OSError, ValueError):
        return ""


#: Default per-file cap for path-injected context (chars). Overridable via
#: ``BRAIN_CTX_PER_FILE_CAP``. Rendering truncates with a resume marker.
#: Raised 60k -> 150k (task 0375): the largest observed single artifact
#: (~181 KB context report) was cut to 60 KB; 150 KB covers that class with
#: headroom while staying a fraction of the 1M input budget.
_CTX_PATHS_PER_FILE = 150000

#: Default total cap across all path-injected files per turn (chars).
#: Overridable via ``BRAIN_CTX_TOTAL_CAP``. Files past the total are
#: skipped with an explicit skipped note — stacked files must never
#: overflow the turn budget on their own. Raised 200k -> 400k alongside
#: the per-file cap so two large files plus the task attach fit one turn.
_CTX_PATHS_TOTAL = 400000


def _paths_base(project_root: Optional[str] = None) -> Path:
    """Base dir for ``context_paths`` reads (cross-install fix).

    An explicit ``project_root`` pointing at an existing directory wins;
    otherwise the workspace root applies. This mirrors the task-file
    resolver's root order (``_resolve_task_file``) so path injection and
    task attach agree on the project instead of diverging when the
    server runs from another install. Invalid values fall back silently
    to the workspace root — resolution failure is reported per file,
    never raised.
    """
    if project_root:
        try:
            if not isinstance(project_root, (str, os.PathLike)):
                raise TypeError(
                    f"project_root is not path-like: {type(project_root)!r}"
                )
            pr = Path(project_root).expanduser()
            if pr.is_dir():
                return pr.resolve()
        except (OSError, TypeError):
            pass
    return _workspace_root()


def build_paths_attach(paths: object, project_root: Optional[str] = None) -> str:
    """Read workspace files for path injection ('' when none).

    Relative paths resolve under the explicit ``project_root`` when one
    is supplied, else under the workspace root (escapes, missing files,
    and unsupported suffixes become explicit ``[unavailable: ...]``
    labels, never silent drops). Files truncate at ``_CTX_PATHS_PER_FILE``
    chars; injection stops at ``_CTX_PATHS_TOTAL`` with a skipped note.
    Pure apart from disk reads; never raises.
    """
    if not isinstance(paths, (list, tuple)):
        return ""
    wanted = [p for p in paths if isinstance(p, str) and p.strip()]
    if not wanted:
        return ""
    blocks: list[str] = []
    used = 0
    base = _paths_base(project_root)
    for rel in wanted:
        # Same range handling as the allocator path (_path_candidates): strip
        # `#Lstart[-end]` before resolution so the fragment breaks neither the
        # root check nor the suffix allowlist. Both entry points share
        # _split_line_range/_slice_text_lines so they cannot drift apart.
        path_part, range_start, range_end, range_error = _split_line_range(rel)
        if range_error is not None:
            blocks.append(f"[unavailable: {rel.strip()} — bad range]")
            continue
        try:
            resolved = _resolve_under_root(path_part, root=base)
        except ValueError:
            blocks.append(f"[unavailable: {rel.strip()} — outside workspace]")
            continue
        sniffed: Optional[str] = None
        sniff_note = ""
        if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
            # Unlisted suffix (dotfiles like `.env.example`, extensionless
            # files like `Dockerfile`): sniff for plain text instead of
            # refusing outright. Known binaries skip the sniff.
            if resolved.suffix.lower() in _UNREADABLE_SUFFIXES:
                blocks.append(f"[unavailable: {rel.strip()} — unsupported extension]")
                continue
            sniffed = _sniff_text_file(resolved)
            if sniffed is None:
                blocks.append(f"[unavailable: {rel.strip()} — unsupported extension]")
                continue
            sniff_note = " — sniffed text, unlisted extension"
        try:
            if sniffed is None:
                if resolved.stat().st_size > _READ_MAX_BYTES:
                    blocks.append(f"[unavailable: {rel.strip()} — file too large]")
                    continue
                text = resolved.read_text(encoding="utf-8", errors="replace")
            else:
                text = sniffed
        except OSError:
            blocks.append(f"[unavailable: {rel.strip()} — unreadable]")
            continue
        if not text.strip():
            blocks.append(f"[unavailable: {rel.strip()} — empty file]")
            continue
        open_line = f"[path-injected: {rel.strip()}{sniff_note}]"
        if range_start is not None:
            sliced, lo, hi, total = _slice_text_lines(text, range_start, range_end)
            # Empty-selection sentinel is lo == 0: a valid slice can itself
            # be blank (sliced == ""), which must still inject.
            if lo == 0:
                blocks.append(f"[unavailable: {rel.strip()} — empty range]")
                continue
            text = sliced
            open_line = f"[path-injected: {rel.strip()}{sniff_note} — lines {lo}-{hi} of {total}]"
        _per_file = _ctx_paths_per_file_cap()
        _total_cap = _ctx_paths_total_cap()
        if len(text) > _per_file:
            text = text[:_per_file] + f"\n[...truncated at {_per_file} chars]"
        if used + len(text) > _total_cap:
            blocks.append(
                f"[skipped: {rel.strip()} — total budget {_total_cap} chars reached]"
            )
            continue
        used += len(text)
        blocks.append(f"{open_line}\n{text}")
    if not blocks:
        return ""
    return "\n\n---\n\n".join(blocks)


# --- Direct attachment rendering ------------------------------------
# No allocator, no chunking, no part markers: every attachment enters
# whole, bounded only by its own configured cap. Caps still apply
# (task/diff per-attachment caps, ``context_paths`` per-file + shared
# total caps) with an inline truncation note — the Brain judges visible
# scope only and quotes needed paths for follow-ups.


def _fence_guard(text: str) -> str:
    """Break embedded fences invisibly so content cannot close our block."""
    return text.replace(chr(96) * 3, chr(96) * 2 + chr(8203) + chr(96))


def _qa_like_prompt(user_prompt: object) -> bool:
    """Keyword gate for QA/reviewer-shaped prompts (never raises)."""
    lowered = user_prompt.lower() if isinstance(user_prompt, str) else ""
    return (
        "qa engineer" in lowered
        or "code reviewer" in lowered
        or "adversarial" in lowered
    )


def _render_direct(
    candidates: list[dict],
) -> tuple[list[tuple[dict, str, None]], list[dict], dict]:
    """Render every attachment whole (no slicing, no part markers).

    Precedence is candidate order: bundle, task, paths, diff, fed.
    Cap cuts render inline with kept and dropped counts, so no cut is
    silent. Absent blocks render nothing.

    Returns ``(rendered, truncated, info)`` in the allocator's shape so
    downstream assembly (``_slot``, ordering, transcript markers, result
    payload) keeps working unchanged: ``rendered`` is ``(candidate,
    block, None)`` in candidate order, ``truncated`` is always ``[]``
    (cap cuts are noted inline in the block, never as resume tokens),
    and ``info`` carries the used-char accounting.
    """
    rendered: list[tuple[dict, str, None]] = []
    used = 0
    group_used: dict[str, int] = {}
    for cand in candidates:
        if cand.get("inline"):
            block = cand.get("open_line", "")
            rendered.append((cand, block, None))
            used += len(block)
            continue
        text = cand.get("text", "")
        cap = cand.get("cap")
        if cap and len(text) > int(cap):
            text = (
                text[: int(cap)]
                + f"\n[...truncated at {cap} chars — remainder NOT sent. "
                + "Judge visible only; mark unseen UNVERIFIABLE, NEVER "
                + "REJECTED.]"
            )
        group = cand.get("group")
        gcap = cand.get("group_cap")
        if group and gcap:
            left = max(0, int(gcap) - group_used.get(group, 0))
            if len(text) > left:
                text = (
                    text[:left]
                    + f"\n[...truncated: shared {group} budget "
                    + f"{gcap} chars reached]"
                )
            group_used[group] = group_used.get(group, 0) + len(text)
        open_line = cand.get("open_line", "")
        fence_lang = cand.get("fence_lang")
        if fence_lang:
            block = open_line + "\n```" + fence_lang + "\n" + text + "\n```"
        elif text:
            block = open_line + "\n" + text
        else:
            block = open_line
        rendered.append((cand, block, None))
        used += len(block)
    info = {
        "attachment_budget_chars": used,
        "attachment_chars_used": used,
        "attachment_chars_remaining": 0,
    }
    return rendered, [], info


def _paths_ledger_summary(
    rendered: list[tuple[dict, str, None]],
) -> list[dict]:
    """Per-path attach outcomes for the ledger (Task 374, file-log-half).

    Derives, from already-rendered ``context_path`` blocks, one small row
    per requested path: which file, what happened (injected / truncated /
    skipped-budget / unavailable-<reason>), and how many chars went into
    the prompt. Paths and sizes only — never file text, prompt text, or
    keys. Never raises; an unparseable block reports ``unknown``.
    """
    out: list[dict] = []
    for cand, block, _meta in rendered:
        try:
            if not isinstance(cand, dict) or cand.get("kind") != "context_path":
                continue
            path = str(cand.get("path", ""))
            text = block if isinstance(block, str) else ""
            if "[path-injected:" in text:
                status = (
                    "truncated"
                    if ("truncated" in text or "[skipped:" in text)
                    else "injected"
                )
            elif "[skipped:" in text:
                status = "skipped-budget"
            elif "[unavailable:" in text:
                reason = text.split("[unavailable:", 1)[1].split("]", 1)[0]
                reason = (
                    reason.split("—", 1)[-1].strip()
                    if "—" in reason
                    else reason.strip()
                )
                status = "unavailable:" + (reason or "unknown")
            else:
                status = "unknown"
            out.append({"path": path, "status": status, "chars": len(text)})
        except Exception:
            continue
    return out


def _task_candidate(
    task_id: object, project_root: Optional[str] = None
) -> Optional[dict]:
    """Full task-file attachment candidate (diff stripped).

    ``None`` when the task file is unresolvable — the caller then sends no
    task attachment, exactly as before. Raises ``ValueError`` when the
    configured cap environment value is malformed: a bad configuration
    must fail loudly, never be reported as an unavailable attachment.
    """
    # Read the configured cap OUTSIDE the try: a malformed environment
    # value is a configuration error and must propagate out of the turn.
    cap = _task_attach_cap()
    try:
        path = _resolve_task_file(task_id, project_root=project_root)
        if path is None:
            return None
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            rel = path.resolve().relative_to(_workspace_root().resolve()).as_posix()
        except (OSError, ValueError):
            rel = path.name
        cleaned, _omitted, _truncated = _strip_task_diff(text, rel)
        tid = task_id.strip() if isinstance(task_id, str) else "task"
        return {
            "kind": "task",
            "path": rel,
            "open_line": f"{_TASK_FILE_MARKER}{tid}: {rel}]",
            "fence_lang": "markdown",
            "text": _fence_guard(cleaned),
            "cap": cap,
        }
    except Exception as exc:  # never fail a turn on attach problems
        print(f"brain-bridge: task attach skipped ({exc})", file=sys.stderr)
        return None


def _diff_candidate(task_id: object, project_root: Optional[str] = None) -> dict:
    """Full changed-hunks candidate; an inline note when unresolved/empty.

    The inline notes matter: stderr is invisible to the model, so a silent
    "" made the Brain reject blind. ``inline`` marks an unbreakable label
    whose text lives in ``open_line``. Raises ``ValueError`` when the
    configured cap environment value is malformed; otherwise never raises.
    """
    tid = task_id.strip() if isinstance(task_id, str) else "task"
    # Same rule as _task_candidate: a malformed cap env value is a
    # configuration error and must propagate out of the turn.
    cap = _task_diff_cap()
    try:
        path = _resolve_task_file(task_id, project_root=project_root)
        if path is None:
            print(
                f"brain-bridge: diff attach skipped "
                f"(task file unresolvable for {task_id!r})",
                file=sys.stderr,
            )
            return {
                "kind": "diff",
                "path": str(task_id),
                "open_line": (
                    f"[changed-hunks:{tid}: UNAVAILABLE — task file "
                    f"unresolvable for {task_id!r}. The server could not "
                    "find the task file (wrong project_root, or the task "
                    "lives in another install). Remedy: retry with the "
                    "correct project_root, or paste the Factual Git Diff "
                    "hunks inline. Do NOT reject blind on missing hunks."
                ),
                "fence_lang": None,
                "text": "",
                "inline": True,
            }
        text = path.read_text(encoding="utf-8", errors="replace")
        diff = extract_task_diff(text)
        if not diff.strip():
            print(
                f"brain-bridge: diff attach skipped "
                f"(no Factual Git Diff block in {path.name})",
                file=sys.stderr,
            )
            return {
                "kind": "diff",
                "path": path.name,
                "open_line": (
                    f"[changed-hunks:{tid}: EMPTY — no Factual Git Diff "
                    f"block in {path.name} yet. Stage the diff first "
                    "(stage_and_inject_diff), then re-run this turn. "
                    "Do NOT reject blind on missing hunks."
                ),
                "fence_lang": None,
                "text": "",
                "inline": True,
            }
        try:
            rel = path.resolve().relative_to(_workspace_root().resolve()).as_posix()
        except (OSError, ValueError):
            rel = path.name
        return {
            "kind": "diff",
            "path": rel,
            "open_line": f"[changed-hunks:{tid}: {rel}]",
            "fence_lang": "diff",
            "text": _fence_guard(diff),
            "cap": cap,
        }
    except Exception as exc:  # never fail a turn on attach problems
        print(f"brain-bridge: diff attach skipped ({exc})", file=sys.stderr)
        return {
            "kind": "diff",
            "path": str(task_id),
            "open_line": (
                f"[changed-hunks:{tid}: UNAVAILABLE — attach raised "
                f"({exc}). Retry the turn; if it persists, paste the "
                "Factual Git Diff hunks inline. Do NOT reject blind "
                "on missing hunks."
            ),
            "fence_lang": None,
            "text": "",
            "inline": True,
        }


def _inline_path_candidate(rel: str, note: str) -> dict:
    """An unbreakable one-line label candidate for ``context_paths``."""
    return {
        "kind": "context_path",
        "path": rel.strip(),
        "open_line": note,
        "fence_lang": None,
        "text": "",
        "inline": True,
    }


def _split_line_range(rel: str) -> tuple[str, object, object, object]:
    """Split a trailing ``#L<start>[-<end>]`` range off a context path.

    Returns ``(path_part, start, end, error)`` where ``start``/``end`` are
    1-based ints (``end`` is None for the open-ended ``#Lstart-`` form and
    ``None``/``None`` when no range suffix is present). ``error`` is a short
    label fragment (``"bad range"``) when the fragment looks like a range
    but does not parse — the caller turns it into an explicit unavailable
    label, never a silent drop.

    Only a *trailing* ``#L<digits>`` pattern is treated as a range, so a
    literal ``#`` anywhere else in a filename flows through untouched.
    A trailing ``#L`` fragment that does not parse (e.g. ``code.py#Lbad``)
    on a path with a supported readable extension is a caller error and
    returns the ``"bad range"`` error instead of falling through to path
    resolution — the caller labels it explicitly, never silently drops
    it. The same malformed fragment on an unsupported extension flows
    through unchanged so the existing unsupported-extension label wins.
    """
    match = re.search(r"#L(\d+)(?:-(\d*))?$", rel)
    if not match:
        malformed = re.search(r"#L[^/]*$", rel)
        if malformed:
            from pathlib import PurePath as _PurePath

            if (
                _PurePath(rel[: malformed.start()]).suffix.lower()
                in _ALLOWED_READ_SUFFIXES
            ):
                return rel, None, None, "bad range"
        return rel, None, None, None
    try:
        start = int(match.group(1))
    except (TypeError, ValueError):
        return rel, None, None, "bad range"
    end_raw = match.group(2)
    if end_raw is None:
        return rel[: match.start()], start, start, None
    if end_raw == "":
        return rel[: match.start()], start, None, None
    try:
        end = int(end_raw)
    except (TypeError, ValueError):
        return rel, None, None, "bad range"
    return rel[: match.start()], start, end, None


def _slice_text_lines(text: str, start: int, end: object) -> tuple[str, int, int, int]:
    """Slice ``text`` to 1-based ``[start, end]`` (``end=None`` means EOF).

    Clamps out-of-range ends to the file instead of failing, so a stale line
    number from an older revision still yields the nearest content. Returns
    ``(sliced, start, end, total)`` with the *effective* bounds, or
    ``("", 0, 0, total)`` when the range selects nothing (start > end, or
    start past EOF) — the caller turns that into an explicit empty-range
    label, never a silent drop.
    """
    lines = text.splitlines()
    total = len(lines)
    lo = max(start, 1)
    hi = total if end is None else min(end, total)
    if lo > hi or lo > total:
        return "", 0, 0, total
    return "\n".join(lines[lo - 1 : hi]), lo, hi, total


def _path_candidates(paths: object, project_root: Optional[str] = None) -> list[dict]:
    """Full-text candidates for ``context_paths`` ('' labels kept explicit).

    Escapes, missing files, and unsupported suffixes become explicit
    ``[unavailable: ...]`` labels, never silent drops. Raises
    ``ValueError`` when a configured cap environment value is malformed;
    otherwise never raises.
    """
    if not isinstance(paths, (list, tuple)):
        return []
    wanted = [p for p in paths if isinstance(p, str) and p.strip()]
    if not wanted:
        return []
    # Configuration is read once, OUTSIDE the per-file I/O handling: a
    # malformed or non-positive cap must fail loudly, never be reported
    # as an unavailable attachment.
    per_file = _ctx_paths_per_file_cap()
    total_cap = _ctx_paths_total_cap()
    out: list[dict] = []
    base = _paths_base(project_root)
    for rel in wanted:
        # Line-range suffix: strip `#Lstart[-end]` BEFORE workspace resolution,
        # otherwise the fragment breaks both the root check and the suffix
        # allowlist (`file.py#L10-20` has no recognized extension).
        path_part, range_start, range_end, range_error = _split_line_range(rel)
        if range_error is not None:
            out.append(
                _inline_path_candidate(rel, f"[unavailable: {rel.strip()} — bad range]")
            )
            continue
        try:
            resolved = _resolve_under_root(path_part, root=base)
        except ValueError:
            out.append(
                _inline_path_candidate(
                    rel, f"[unavailable: {rel.strip()} — outside workspace]"
                )
            )
            continue
        sniffed: Optional[str] = None
        sniff_note = ""
        if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
            # Same sniff fallback as the helper path: dotfiles and
            # extensionless text inject; known binaries stay rejected.
            if resolved.suffix.lower() not in _UNREADABLE_SUFFIXES:
                sniffed = _sniff_text_file(resolved)
            if sniffed is None:
                out.append(
                    _inline_path_candidate(
                        rel, f"[unavailable: {rel.strip()} — unsupported extension]"
                    )
                )
                continue
            sniff_note = " — sniffed text, unlisted extension"
        try:
            if sniffed is None:
                if resolved.stat().st_size > _READ_MAX_BYTES:
                    out.append(
                        _inline_path_candidate(
                            rel, f"[unavailable: {rel.strip()} — file too large]"
                        )
                    )
                    continue
                text = resolved.read_text(encoding="utf-8", errors="replace")
            else:
                text = sniffed
        except OSError:
            out.append(
                _inline_path_candidate(
                    rel, f"[unavailable: {rel.strip()} — unreadable]"
                )
            )
            continue
        if not text.strip():
            out.append(
                _inline_path_candidate(
                    rel, f"[unavailable: {rel.strip()} — empty file]"
                )
            )
            continue
        open_line = f"[path-injected: {rel.strip()}{sniff_note}]"
        if range_start is not None:
            sliced, lo, hi, total = _slice_text_lines(text, range_start, range_end)
            # Same sentinel as the helper path above: lo == 0 means no
            # selection; a blank but valid slice still injects.
            if lo == 0:
                out.append(
                    _inline_path_candidate(
                        rel, f"[unavailable: {rel.strip()} — empty range]"
                    )
                )
                continue
            text = sliced
            open_line = f"[path-injected: {rel.strip()}{sniff_note} — lines {lo}-{hi} of {total}]"
        out.append(
            {
                "kind": "context_path",
                "path": rel.strip(),
                "open_line": open_line,
                "fence_lang": None,
                "text": text,
                "cap": per_file,
                # Every context_paths file shares one configured total budget;
                # the allocator enforces the aggregate because the candidates
                # are allocated independently.
                "group": "context_path",
                "group_cap": total_cap,
            }
        )
    return out


def _note_checkpoint(
    name: str,
    task_id: Optional[str] = None,
    session_id: Optional[str] = None,
    project_root: Optional[str] = None,
) -> None:
    """Best-effort session-ledger checkpoint (GitHub issue 19, P5).

    One-off turns (no scope or no root) skip silently — there is no
    sessions dir to record in. Ledger problems never fail a turn.
    """
    scope = session_id or task_id
    if scope is None or project_root is None:
        return
    try:
        _ledger_checkpoint(scope, name, task_id=task_id, project_root=project_root)
    except Exception as exc:  # never fail a turn on ledger problems
        print(f"brain-bridge: checkpoint skipped ({exc})", file=sys.stderr)


@mcp.tool()
def brain_turn(
    user_prompt: str,
    task_id: Optional[str] = None,
    system_prompt_path: Optional[str] = None,
    include_bundle: bool = True,
    include_diff: bool = False,
    context_paths: Optional[list[str]] = None,
    project_root: Optional[str] = None,
    risk_tier: Optional[str] = None,
    session_id: Optional[str] = None,
    stage: Optional[str] = None,
    kanban_path: Optional[str] = None,
    required_tools: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Send one Brain turn.

    Args:
        user_prompt: Built by the Hands from its current machine state
            (instruction + task file content + prior answers).
        task_id: The BARE task number (digits only, e.g. "215") — never
            a slug, never a suffixed variant like "215qa", "215rev",
            or "215plan". When given, the task file is resolved for the
            task attach and the diff attach (see ``include_bundle`` /
            ``include_diff``). Non-numeric input is rejected before
            anything runs. Omit for one-off turns with no memory.
        system_prompt_path: Optional override; default is the global
            install copy of system-prompt.md.
        include_bundle: When True (default), prepend the small-file
            context bundle unless the prompt already carries its marker,
            plus the task file's working content (Goal/Notes/TODOs/AC/
            evidence/log minus the Factual Git Diff block, with a
            quoted-paths follow-up) whenever task_id resolves to a file.
            Pass False for tiny calls. The system prompt is untouched.
        include_diff: When True, append the task file's changed hunks
            (Factual Git Diff content, verbatim, capped) whenever
            task_id resolves to a file that carries a diff block.
            Stands alone: honored even on lean turns with
            include_bundle=False (the EMPTY_OUTPUT_RETRY shape) — the
            old bundle gate silently dropped QA diffs on every lean
            retry. When True but nothing attaches, a stderr reason
            says why (unresolvable file vs empty diff block).
            QA and reviewer turns MUST pass True — the Brain judges
            the actual changes, never a summary. Fail-safe: when the
            flag is False but the prompt reads like a QA/reviewer turn
            ("qa engineer", "code reviewer", "adversarial"), the hunks
            still auto-attach with a stderr warning.
        context_paths: Optional workspace file paths to inject server-side
            (e.g. context/tree/signature reports). Each path resolves
            under the workspace root with the read suffix allowlist;
            per-file cap plus total budget apply, problems become explicit
            unavailable labels. Default off. Small pulls stay inline.
        project_root: Optional project dir holding ``tasks/``. Its
            ``tasks/.sessions/`` stores this turn's history (per-project
            sessions), and its ``tasks/`` lanes resolve the task file
            for the task attach and the diff attach. An EXPLICIT root
            must hold ``tasks/`` — otherwise preflight raises instead of
            silently falling back to the workspace root (that silent
            substitution failed whole sagas as "unavailable"). When
            omitted the resolver tries ``BRAIN_PROJECT_ROOT`` /
            ``BRAIN_WORKSPACE_ROOT`` / cwd walk-up; exhaustion raises
            with ``project_root=`` as the remedy. One-off turns (no
            task_id, no session_id) need no root.
        risk_tier: Optional explicit risk tier for model routing
            (``T0``/``T1``/``T2`` per ``docs/conventions.md``). Only
            takes effect when ``BRAIN_RISK_ROUTING_ENABLED`` is set;
            missing or invalid values fail safe to the current model.
            Default None (unrouted, today's behavior).
        session_id: Optional session key (e.g. "cando-828") — the
            PRIMARY history key (session-first). Pass it alongside
            ``task_id`` so one thread spans every task in the work
            session; pass it alone for taskless turns. When omitted, the
            bridge auto-detects ambient ``OPENCODE_SESSION_ID`` from the
            environment (explicit wins); with neither explicit nor
            ambient session id, a lone ``task_id`` falls back to the
            task-keyed transcript for backward compatibility. Omit both
            (and unset the env var) for one-off turns with no memory.
        stage: Optional turn stage, one of plan / implement / qa /
            review / closure / brainstorm. Unknown stages are rejected so
            a typo can never run as an unscoped turn. The stage also
            selects the prompt artifact: a known stage loads its
            stage-scoped system prompt (the shared COMMON core plus that
            stage's persona slice) when the artifact exists, and falls
            back to the full prompt otherwise.
        kanban_path: Optional task-file path under
            ``<project_root>/tasks/`` (e.g. "tasks/qa/257-x.md").
            Paths escaping the tasks/ lanes are rejected.
        required_tools: Optional list of tool names the turn's stage
            requires (e.g. ["default.question"]). Missing-required tools gate
            the turn before transport (see capability).

    Returns:
        {"status": "XML_EXTRACTED"|"REPORT", "xml_blocks": [...],
         "output": <full text>, "model": <model id>}.
        Hands rule: take ``xml_blocks`` when non-empty, else ``output``.
        Questions for the admin travel inside ``output`` — relay them to
        the Manager and feed the answer back as the next ``user_prompt``
        (with the same ``task_id`` so history continues).
        Recovery (Task 291): a partial truncation (non-empty model text,
        status=incomplete/reason=max_output_tokens, no usable XML) is
        re-issued ONCE server-side with stepped-down reasoning effort;
        if that also truncates, ``output`` carries
        TRUNCATION_UNRECOVERABLE and the caller must not retry as-is.
    """
    # Request preflight FIRST (GitHub issue 18): local validation before
    # any load, attach, import, or model call. An explicit project_root
    # without tasks/ raises here instead of silently substituting the
    # workspace root; suffixed task_ids are rejected; session_id is the
    # primary history key and coexists with task_id (session-first:
    # history continues under the session while the task file and diff
    # still resolve from task_id); neither id means a one-off turn.
    # The resolved root feeds every downstream resolver so attaches and
    # history share one root.
    _requested_root = project_root
    _pre = _validate_request(
        project_root=project_root,
        task_id=task_id,
        session_id=session_id,
        kanban_path=kanban_path,
        stage=stage,
        include_bundle=include_bundle,
        include_diff=include_diff,
        required_tools=required_tools,
    )
    task_id = _pre.task_id
    session_id = _pre.session_id
    project_root = str(_pre.project_root) if _pre.project_root is not None else None
    # One-off turns intentionally keep no project binding (they persist
    # nothing), so preflight drops an explicit project_root. An explicitly
    # passed root must still pin the BUNDLE and file-pull attaches to the
    # caller's project (issue #24) — otherwise a one-off turn reads the
    # bridge install dir. Existing-dir guard only: a bad root falls back
    # to ambient resolution instead of silently reporting all-missing.
    if project_root is None and _pre.binding == "one-off":
        _pinned = _explicit_root(_requested_root)
        if _pinned is not None and _pinned.is_dir():
            project_root = str(_pinned)
    history_key = _pre.history_key
    _note_checkpoint(
        "request_accepted",
        task_id=task_id,
        session_id=session_id,
        project_root=project_root,
    )
    _note_checkpoint(
        "preflight_completed",
        task_id=task_id,
        session_id=session_id,
        project_root=project_root,
    )

    # Capability preflight SECOND (GitHub issue 16): the manifest maps
    # every required tool (caller-declared plus stage-implied) to
    # AVAILABLE / UNAVAILABLE_REQUIRED / UNAVAILABLE_OPTIONAL. The
    # manifest is printed as the session-start diagnostic and stored
    # as a session-ledger event BEFORE the gate, so a blocked turn is
    # still recorded. A missing required tool returns a non-verdict
    # REPORT carrying the relay block with zero transport calls —
    # silent skipping is forbidden, and transport failures never
    # surface as verdicts.
    manifest = _evaluate_capability(
        referenced=list(_pre.required_tools),
        required=list(_pre.required_tools),
        stage=stage,
    )
    print(
        "capability-manifest: task=%s session=%s stage=%s %s"
        % (
            task_id,
            session_id,
            stage,
            " ".join(f"{k}={v}" for k, v in sorted(manifest.items()))
            or "(no tools referenced)",
        ),
        file=sys.stderr,
    )
    try:
        _append_ledger_event(
            "capability_manifest",
            task_id=task_id,
            session_id=session_id,
            data={"stage": stage, "manifest": manifest},
            project_root=project_root,
        )
    except Exception as exc:  # never fail a turn on ledger problems
        print(f"brain-bridge: ledger event skipped ({exc})", file=sys.stderr)
    try:
        _gate_capability(manifest, stage=stage)
    except CapabilityBlockedError as exc:
        return {
            "status": "REPORT",
            "xml_blocks": [],
            "output": _format_relay_block(exc),
            "model": _get_brain_model(),
            # Same field set as a successful turn so callers never face
            # two incompatible response schemas.
            "history_turns_dropped": 0,
            "truncated_count": 0,
            "attachments_truncated": [],
            "attachment_parts": [],
            "attachment_budget_chars": 0,
            "attachment_chars_used": 0,
            "attachment_chars_remaining": 0,
            "budget_chars": 0,
            "retry_count": 0,
            "prompt_cache_split": None,
        }
    _note_checkpoint(
        "capability_completed",
        task_id=task_id,
        session_id=session_id,
        project_root=project_root,
    )

    # Stage-aware prompt routing: the validated stage selects the prompt
    # artifact (the shared COMMON core plus that stage's persona slice).
    # A known stage whose artifact is missing falls back to the full
    # prompt inside the loader — never to an empty prompt.
    system_prompt = load_system_prompt(system_prompt_path, stage=_pre.stage)
    effective_prompt = user_prompt
    # Segment captures for the prompt-cache split descriptor (Task 247):
    # static pieces are hashed for stability, dynamic pieces per turn.
    bundle_text = ""
    task_attach_text = ""
    paths_text = ""
    diff_append_text = ""
    failsafe_text = ""
    fed_text = ""

    # Attachment candidates are gathered here WITHOUT final budgeting.
    # One shared allocator below renders them against the chars actually
    # left in the input budget, so stacked attachments can never each
    # assume the whole window and starve the rest of the turn.
    candidates: list[dict] = []
    if include_bundle and _BUNDLE_MARKER not in user_prompt:
        # Read the bundle from the SAME project root this turn resolved for
        # the task file and context paths (issue #24): without the explicit
        # root the bundle silently fell back to the bridge install dir.
        candidates.append(
            {
                "kind": "bundle",
                "path": "small-file bundle",
                "slot": "bundle",
                "open_line": "",
                "fence_lang": None,
                "text": _build_context_bundle(project_root),
            }
        )
    if include_bundle and task_id:
        _ns = (
            f"{_TASK_FILE_MARKER}{task_id.strip()}: "
            if isinstance(task_id, str)
            else _TASK_FILE_MARKER
        )
        _task_cand = _task_candidate(task_id, project_root=project_root)
        if _task_cand is not None and _ns not in user_prompt:
            _task_cand["slot"] = "task"
            candidates.append(_task_cand)
    if context_paths:
        # File-path injection: the server reads big artifacts (context,
        # tree, signature reports) from disk instead of the Hands pasting
        # them. Explicitly requested files outrank the small-file bundle
        # on review/QA turns.
        try:
            for _pcand in _path_candidates(context_paths, project_root=project_root):
                _pcand["slot"] = "paths"
                candidates.append(_pcand)
        except OSError as exc:  # I/O only: a bad cap value fails loudly
            print(f"brain-bridge: paths attach skipped ({exc})", file=sys.stderr)
    if task_id:
        # Explicit flag stands alone: a lean turn (include_bundle=False,
        # the documented EMPTY_OUTPUT_RETRY shape) with include_diff=True
        # MUST still carry the hunks — gating the diff on the bundle
        # silently dropped QA diffs on every lean retry. The fail-safe
        # adds them for QA/reviewer-like prompts even when the caller
        # forgot the flag (keyword gate only).
        _failsafe = (not include_diff) and _qa_like_prompt(user_prompt)
        if include_diff or _failsafe:
            _diff_cand = _diff_candidate(task_id, project_root=project_root)
            if _diff_cand is not None:
                # The failsafe attach hashes into its OWN cache-split slot
                # so it is never confused with an explicitly requested diff.
                _diff_cand["slot"] = "failsafe" if _failsafe else "diff"
                candidates.append(_diff_cand)
                if _failsafe:
                    print(
                        "brain-bridge: QA turn without include_diff, "
                        "auto-attaching diff",
                        file=sys.stderr,
                    )
                elif _diff_cand.get("inline"):
                    print(
                        "brain-bridge: include_diff=True but no hunks "
                        "attached (see reason above)",
                        file=sys.stderr,
                    )

    # Tier precedence: an explicit ``risk_tier`` wins; otherwise the
    # tier is derived from the turn stage (Task 261). A missing or
    # unknown stage leaves the tier empty, and the resolver returns
    # ``BRAIN_MODEL`` for it.
    effective_tier = (risk_tier or "").strip() or resolve_stage_tier(
        stage, _get_stage_tiers()
    )
    model = resolve_routed_model(
        _routing_enabled(),
        effective_tier,
        _get_brain_model(),
        _get_model_low(),
        _get_model_high(),
    )
    if history_key:
        # Sessions-root visibility: one debug line per turn so a
        # misrouted project is observable in stderr, never silent.
        _scope = "session" if session_id is not None else "task"
        print(
            f"brain-bridge: sessions root {_sessions_root(project_root)} "
            f"({_scope} {history_key})",
            file=sys.stderr,
        )
    history = (
        load_history(history_key, project_root=project_root) if history_key else []
    )
    if history_key:
        # Discovery-fed planning: a [fed-context] block in this prompt is
        # pinned to the session, then the pin (not just this turn's copy)
        # rides every later turn until session end. The pin lives outside
        # the transcript, so compaction and the middle drop below can never
        # silently remove it; it still counts toward the input budget.
        try:
            fed = extract_fed_context(user_prompt)
            if fed:
                save_fed_context(history_key, fed, project_root=project_root)
            pinned = load_fed_context(history_key, project_root=project_root)
            if pinned and "[pinned-fed-context]" not in user_prompt:
                candidates.append(
                    {
                        "kind": "fed_context",
                        "path": "pinned fed-context",
                        "slot": "fed",
                        "open_line": "[pinned-fed-context]",
                        "fence_lang": None,
                        "text": pinned + "\n[/pinned-fed-context]",
                        "cap": _FED_CONTEXT_CAP,
                    }
                )
        except Exception as exc:  # never fail a turn on pin problems
            print(f"brain-bridge: fed-context skipped ({exc})", file=sys.stderr)

    def _hist_chars() -> int:
        return sum(len(turn["content"]) for turn in history)

    # Direct rendering: every attachment enters whole against the 1M
    # input budget — no allocator, no chunking, no part markers. History
    # is deliberately NOT subtracted here — the shipped transcript is the
    # LAST fallback, so its length can never shrink an attachment and the
    # static prompt-cache prefix stays stable across turns.
    rendered, attachments_truncated, budget_info = _render_direct(candidates)
    # Task 374: per-path attach outcomes for the ledger (file-log-half).
    # Paths + statuses + sizes only — never file or prompt text.
    _paths_summary = _paths_ledger_summary(rendered)

    def _slot(name: str) -> str:
        return "\n\n---\n\n".join(
            block for cand, block, _meta in rendered if cand.get("slot") == name
        )

    # Context-sufficiency diagnostic (plan turns only): make a blind plan
    # observable instead of silent. Non-blocking by design — stderr only,
    # never a status or xml_blocks change, so no caller behavior shifts. It
    # reads the FINAL rendered bundle (post-allocation, so a cap-truncated
    # pack is seen as absent) and the combined prompt text including any
    # pinned fed-context block, so a turn that reloads fed context from
    # history is never falsely reported as ungrounded.
    _rendered_bundle = _slot("bundle")
    _rendered_fed = _slot("fed")
    _rendered_paths = _slot("paths")
    _combined_prompt = (
        user_prompt
        + ("\n" + _rendered_fed if _rendered_fed else "")
        + ("\n" + _rendered_paths if _rendered_paths else "")
    )
    _sufficiency_gaps = context_sufficiency_gaps(
        stage,
        _combined_prompt,
        _rendered_bundle,
        bundle_included=bool(include_bundle),
        has_server_paths=bool(_rendered_paths),
    )
    if _sufficiency_gaps:
        print(
            "brain-bridge: context-sufficiency warning (stage=plan): "
            + "; ".join(_sufficiency_gaps)
            + " — Brain must request the missing context from the Hands "
            "before committing to a plan",
            file=sys.stderr,
        )

    before_blocks: list[str] = []
    for _kind in ("fed_context", "task", "bundle"):
        before_blocks.extend(
            block for cand, block, _meta in rendered if cand.get("kind") == _kind
        )
    after_blocks: list[str] = []
    for _kind in ("context_path", "diff"):
        after_blocks.extend(
            block for cand, block, _meta in rendered if cand.get("kind") == _kind
        )
    # Prompt-cache split segments reflect what actually landed in the
    # prompt, including any truncated rendering.
    bundle_text = _slot("bundle")
    task_attach_text = _slot("task")
    fed_text = _slot("fed")
    paths_text = _slot("paths")
    diff_append_text = _slot("diff")
    failsafe_text = _slot("failsafe")
    _blocks = [b for b in before_blocks if b] + [user_prompt]
    _blocks.extend(b for b in after_blocks if b)
    effective_prompt = "\n\n---\n\n".join(_blocks)

    # Input budget: system + prompt + history chars count against the
    # configured ceiling. The shipped transcript is bounded at load
    # (``_HISTORY_LIMIT``), and the pre-send guard below may additionally
    # drop oldest history turns to fit the provider window. History loss
    # is reported separately from attachment loss.
    history_turns_dropped = 0
    truncated_count = history_turns_dropped
    budget_chars = len(system_prompt) + len(effective_prompt) + _hist_chars()
    util_pct = budget_chars * 100 // _model_window_chars()
    # Pre-send token budget guard: estimate input tokens, add the live
    # reserved output, and trim in fixed order before any provider call so
    # an oversize turn returns a REPORT hint instead of a provider 400.
    # Diffs, context, and bundle already ride inside effective_prompt, so
    # the estimate covers them with zero extras and no double count.
    _est_input_tokens = _estimate_input_tokens_from_chars(budget_chars)
    _reserved_output_tokens = _get_max_tokens()
    _trimmed_history = 0
    _trimmed_diffs = 0
    _trimmed_context = 0
    _trimmed_bundle = 0
    while (
        not _pre_send_budget_fits(_est_input_tokens, _reserved_output_tokens)
        and history
    ):
        # Oldest first: index zero is the oldest turn; the current turn
        # lives in effective_prompt and is never touched here.
        history.pop(0)
        _trimmed_history += 1
        budget_chars = len(system_prompt) + len(effective_prompt) + _hist_chars()
        _est_input_tokens = _estimate_input_tokens_from_chars(budget_chars)
    if not _pre_send_budget_fits(_est_input_tokens, _reserved_output_tokens) and (
        diff_append_text or paths_text
    ):
        # Diffs and context travel in after_blocks; drop the whole tail.
        after_blocks = []
        _blocks = [b for b in before_blocks if b] + [user_prompt]
        effective_prompt = "\n\n---\n\n".join(_blocks)
        diff_append_text = ""
        paths_text = ""
        _trimmed_diffs = 1
        _trimmed_context = 1
        budget_chars = len(system_prompt) + len(effective_prompt) + _hist_chars()
        _est_input_tokens = _estimate_input_tokens_from_chars(budget_chars)
    if (
        not _pre_send_budget_fits(_est_input_tokens, _reserved_output_tokens)
        and bundle_text
    ):
        # Bundle travels in before_blocks; rebuild without the bundle kind.
        before_blocks = [
            block
            for cand, block, _meta in rendered
            if cand.get("kind") in ("fed_context", "task") and block
        ]
        _blocks = [b for b in before_blocks if b] + [user_prompt]
        _blocks.extend(b for b in after_blocks if b)
        effective_prompt = "\n\n---\n\n".join(_blocks)
        bundle_text = ""
        _trimmed_bundle = 1
        budget_chars = len(system_prompt) + len(effective_prompt) + _hist_chars()
        _est_input_tokens = _estimate_input_tokens_from_chars(budget_chars)
    history_turns_dropped = _trimmed_history
    truncated_count = history_turns_dropped
    util_pct = budget_chars * 100 // _model_window_chars()
    _budget_over_hint_text: Optional[str] = None
    if not _pre_send_budget_fits(_est_input_tokens, _reserved_output_tokens):
        _budget_state = _task_state_note(history_key, project_root)
        _budget_over_hint_text = _over_budget_hint(
            _est_input_tokens,
            _reserved_output_tokens,
            trimmed_history=_trimmed_history,
            trimmed_diffs=_trimmed_diffs,
            trimmed_context=_trimmed_context,
            trimmed_bundle=_trimmed_bundle,
            task_id=task_id,
            state=_budget_state,
        )
        print(
            "brain-bridge: pre-send budget over "
            f"(est_input~{_est_input_tokens} reserved={_reserved_output_tokens} "
            f"trimmed_history={_trimmed_history} trimmed_diffs={_trimmed_diffs} "
            f"trimmed_context={_trimmed_context} "
            f"trimmed_bundle={_trimmed_bundle}); provider skipped",
            file=sys.stderr,
        )
    # Sidecar only: the split descriptor never touches wire bytes —
    # effective_prompt, chat payload, and prompt_hash stay identical.
    cache_split = build_prompt_cache_split(
        system_prompt,
        bundle_text,
        task_attach_text,
        user_prompt,
        paths_text=paths_text,
        diff_text=diff_append_text,
        failsafe_text=failsafe_text,
        fed_text=fed_text,
        history=history,
    )
    _append_context_ledger(
        history_key,
        project_root,
        budget_chars,
        truncated_count,
        model=model,
        risk_tier=effective_tier,
        prompt_cache_split=cache_split,
        paths=_paths_summary,
    )
    if budget_chars > _PROMPT_WARN_CHARS:
        print(
            f"brain-bridge: prompt is large (budget_chars={budget_chars} "
            f"est_tokens~{budget_chars // 4} util~{util_pct}% of "
            f"{_model_window_chars()}ch window); oversized prompts have returned "
            "empty output before — if this turn comes back empty, retry lean "
            "(include_bundle=false, same task_id, short prompt)",
            file=sys.stderr,
        )
    if truncated_count:
        print(
            f"brain-bridge: truncated {truncated_count} middle history turns "
            f"(budget_chars={budget_chars} est_tokens~{budget_chars // 4})",
            file=sys.stderr,
        )
    body = _build_request_body(system_prompt, history, effective_prompt, model=model)
    if "reasoning" in body:
        # Guard the risky default (Task 259): reasoning tokens count
        # against max_output_tokens, so high/xhigh effort with a small cap
        # can exhaust the budget and finish with reasoning-only output.
        _maybe_warn_reasoning_budget(
            body["reasoning"]["effort"], body["max_output_tokens"]
        )
    _total_attempts = 0
    _recovery_used = False
    _recovery_effort: Optional[str] = None
    _reasoning_cfg = body.get("reasoning")
    _first_effort: Optional[str] = (
        _reasoning_cfg.get("effort") if isinstance(_reasoning_cfg, dict) else None
    )
    # Transport loop (Task 291): at most TWO provider calls. Pass 0 is the
    # normal turn. When pass 0 returns a PARTIAL truncation (non-empty
    # output, status=incomplete/reason=max_output_tokens, no usable XML),
    # the fragment is discarded and pass 1 re-issues the whole turn once
    # server-side with stepped-down reasoning effort. Structured output
    # must never stitch a fragment — the whole call is retried with more
    # visible-answer headroom instead. resp_data stays None on paths that
    # never reach the provider (budget-over) or that fail before parsing
    # (structured fatal) — the continuity capture below treats None as
    # empty, never a crash.
    resp_data: Any = None
    for _transport_pass in (0, 1):
        if _budget_over_hint_text is not None:
            # Pre-send budget guard tripped: skip the provider entirely and
            # ride the normal REPORT tail below with the hint text.
            output = _budget_over_hint_text
            xml_blocks = []
            _raw_text_present = False
            diag = {
                "status": "complete",
                "incomplete_reason": None,
                "error": None,
                "refusal": None,
            }
            break
        _note_checkpoint(
            "transport_started",
            task_id=task_id,
            session_id=session_id,
            project_root=project_root,
        )
        try:
            mode = _upstream_mode()
            target_url = _upstream_url()
            wire_body = (
                _convert_responses_to_chat_completions_body(body)
                if mode == "chat_completions"
                else body
            )
            resp, attempts = _send_with_retry(
                _make_client,
                target_url,
                wire_body,
            )
            _total_attempts += attempts
            raw_data = _resp_json(resp)
            resp_data = (
                _convert_chat_completions_to_responses_data(raw_data)
                if mode == "chat_completions"
                else raw_data
            )
            # A translated response can carry status=failed or status=incomplete
            # with an empty output list. parse_responses_text() would reduce that
            # to "" and the session would be recorded as an ordinary report, so
            # the failure has to be captured here, before any text parsing.
            upstream_failure = _upstream_failure_message(resp_data)
            if upstream_failure:
                raise RuntimeError(upstream_failure)
            # Task 374: a completed HTTP round-trip counts against the
            # monthly quota (retries included — each pass is a real call).
            _usage_payload = (
                resp_data.get("usage") if isinstance(resp_data, dict) else None
            )
            _warn_brain_quota(_record_brain_use(model, _usage_payload))
        except RuntimeError as exc:
            # Structured fatal (Task 329 F7): a transport failure, a
            # malformed body, or a fatal 4xx must surface as a REPORT
            # carrying debug.provider — never as a raw tool exception.
            # Genuine bugs still raise: only RuntimeError from the send
            # path converts; anything else propagates untouched.
            _total_attempts += int(getattr(exc, "transport_attempts", 0) or 0)
            _fatal_code = getattr(exc, "provider_code", None)
            if not isinstance(_fatal_code, str):
                _fatal_code = None
            _fatal_status = getattr(exc, "provider_status", None)
            diag = parse_responses_diagnostics(
                {"error": {"message": str(exc), "code": _fatal_code}}
            )
            if isinstance(_fatal_status, int):
                diag["provider_status_code"] = _fatal_status
            diag["requested_model"] = model
            _log_provider_diagnostics(diag)
            output = _provider_error_hint(
                diag["error"] or str(exc), diag.get("error_code")
            )
            xml_blocks = []
            _raw_text_present = False
            break
        _raw_text = parse_responses_text(resp_data)
        _raw_text_present = bool(_raw_text.strip())
        output = _raw_text
        _incomplete_reason = None
        if isinstance(resp_data, dict):
            _details = resp_data.get("incomplete_details")
            if isinstance(_details, dict):
                _candidate = _details.get("reason")
                if isinstance(_candidate, str) and _candidate:
                    _incomplete_reason = _candidate
        if _incomplete_reason and _raw_text_present:
            output = f"[upstream incomplete: {_incomplete_reason}]\n{output}"
        # Eligibility is judged on the RAW model text: the triage below
        # rewrites blank output into hint text, and a rewritten hint must
        # never qualify as a "partial" truncation (Task 259 stays terminal).
        _raw_text_present = bool(output.strip())
        _note_checkpoint(
            "response_parsed",
            task_id=task_id,
            session_id=session_id,
            project_root=project_root,
        )
        # Broad catch would mislabel unrelated bugs as strict
        # rejects, so only strict codes convert to REPORT. Anything
        # else re-raises. None output yields REPORT, never a crash.
        # REPORT text is bounded: first 2000 chars ride along, the
        # remainder is named by a marker instead of pasted whole.
        output_text = output or ""
        try:
            xml_blocks = extract_xml_blocks(output_text)
        except ValueError as exc:
            msg = str(exc)
            if msg.startswith(
                (
                    STRICT_XML_FENCE_FALLBACK_CODE,
                    STRICT_XML_UNCLOSED_CODE,
                    STRICT_XML_CONTRACT_CODE,
                )
            ):
                # Strict XML gate (Task 305 C1): lenient input never
                # extracts. Report with the explicit code so the Hands
                # re-emits bare unfenced XML instead of executing repair.
                shown = output_text[:2000]
                rest = (
                    f"\n[xml-strict-reject-remainder: "
                    f"{len(output_text) - 2000} chars withheld]"
                    if len(output_text) > 2000
                    else ""
                )
                output = (
                    f"[xml-strict-reject]\n- {exc}\n[/xml-strict-reject]\n"
                    + shown
                    + rest
                )
                xml_blocks = []
            else:
                raise
        if xml_blocks:
            # Semantic gate (Task 245): syntactically valid but contract-
            # incomplete XML must triage as REPORT with explicit reasons —
            # the Hands executes only whole contracts, never fragments.
            sem_problems = validate_hands_xml_blocks(xml_blocks)
            if sem_problems:
                print(
                    "brain-bridge: xml failed semantic validation "
                    f"({len(sem_problems)} problems)",
                    file=sys.stderr,
                )
                output = (
                    "[xml-semantic-reject]\n"
                    + "\n".join(f"- {p}" for p in sem_problems)
                    + "\n[/xml-semantic-reject]\n"
                    + output
                )
                xml_blocks = []
        diag = parse_responses_diagnostics(resp_data)
        diag["requested_model"] = model
        _log_provider_diagnostics(diag)
        _note = _model_substitution_note(diag, model)
        if _note is not None:
            print(f"brain-bridge: {_note}", file=sys.stderr)
        if not xml_blocks and not output.strip():
            # Empty-output triage (Task 259): classify the provider diagnosis
            # BEFORE falling back to the flake hint. Order is load-bearing:
            # top-level error -> refusal -> output-budget exhaustion -> flake.
            state = _task_state_note(history_key, project_root)
            if diag["error"]:
                output = _provider_error_hint(diag["error"], diag.get("error_code"))
            elif diag["refusal"]:
                output = _provider_refusal_hint(diag["refusal"])
            elif (
                diag["status"] == "incomplete"
                and diag["incomplete_reason"] == "max_output_tokens"
            ):
                output = _output_budget_hint(diag, task_id, state)
            else:
                # Transport/model flake (Task 232): never return a silent
                # blank REPORT. Substitute the retry hint; status stays
                # REPORT so old callers keep working. The transcript below
                # records the hint, not a verdict.
                output = _empty_output_hint(task_id, state)
        if (
            _transport_pass == 0
            and _raw_text_present
            and not xml_blocks
            and diag["status"] == "incomplete"
            and diag["incomplete_reason"] == "max_output_tokens"
            and isinstance(body.get("reasoning"), dict)
        ):
            _current_effort = body["reasoning"].get("effort")
            _next_effort = _step_down_effort(_current_effort)
            _current_norm = (
                _current_effort.strip().lower()
                if isinstance(_current_effort, str) and _current_effort.strip()
                else _current_effort
            )
            # Case-insensitive floor guard (Task 291 hotfix): a normalized
            # equal means the floor is reached — re-issuing would bill a
            # full turn for an identical shape.
            if _next_effort != _current_norm:
                _recovery_effort = _next_effort
                body["reasoning"]["effort"] = _next_effort
                _maybe_warn_reasoning_budget(_next_effort, body["max_output_tokens"])
                print(
                    "brain-bridge: partial truncation "
                    "(status=incomplete, reason=max_output_tokens, no "
                    "usable XML); discarding fragment and re-issuing once "
                    "server-side with reasoning effort "
                    f"{_next_effort!r} (was {_first_effort!r})",
                    file=sys.stderr,
                )
                _recovery_used = True
                continue
        break
    if (
        not xml_blocks
        and _raw_text_present
        and diag["status"] == "incomplete"
        and diag["incomplete_reason"] == "max_output_tokens"
        and TRUNCATION_UNRECOVERABLE not in output
    ):
        # Terminal for ANY unrecovered partial truncation (Task 291
        # hotfix): floor and temperature-mode first passes never recover,
        # so gating on _recovery_used alone would return a silent
        # fragment. Empty-output keeps _raw_text_present false, so the
        # Task 259 budget/flake hints stay terminal as before; usable
        # XML keeps xml_blocks non-empty, so complete-XML never converts.
        # Only the transcript below records this.
        _exhaust_state = _task_state_note(history_key, project_root)
        output = _truncation_exhausted_hint(
            diag, task_id, _exhaust_state, _first_effort, _recovery_effort
        )
        xml_blocks = []
    fence_drops = list(_last_fence_drops)
    # Continuity capture (Task 329 F2/F3): replayable provider items
    # plus estimator calibration from this turn's observed usage. The
    # fatal-error path leaves resp_data None, which yields empty
    # continuity and skips calibration — never a crash.
    _replay_phase, _replay_response_id, _replay_items = _replayable_provider_items(
        resp_data
    )
    if isinstance(resp_data, dict):
        _seen_usage = resp_data.get("usage")
        if isinstance(_seen_usage, dict):
            _seen_input = _as_int(_seen_usage.get("input_tokens"))
            if _seen_input is not None:
                _note_observed_ratio(budget_chars, _seen_input)
    if history_key:
        prompt_hash = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
        # Store the compact form: attachment markers, not attachment
        # bodies. The transcript is replayed every turn, so the full
        # assembled prompt here would make each turn re-send the last
        # turn's attachments (see _transcript_form).
        append_turn(
            history_key,
            "user",
            _transcript_form(user_prompt, rendered),
            model=model,
            prompt_hash=prompt_hash,
            truncated=truncated_count,
            project_root=project_root,
        )
        append_turn(
            history_key,
            "assistant",
            output,
            model=model,
            prompt_hash=prompt_hash,
            truncated=truncated_count,
            project_root=project_root,
            phase=_replay_phase,
            response_id=_replay_response_id,
            provider_items=_replay_items,
        )
    result: dict[str, Any] = {
        "status": "XML_EXTRACTED" if xml_blocks else "REPORT",
        "xml_blocks": xml_blocks,
        "output": output,
        "model": model,
        # History loss and attachment loss are two different failures and
        # are reported separately. ``history_turns_dropped`` is canonical;
        # ``truncated_count`` stays as the back-compat alias (older
        # callers and the ledger keep reading it).
        "history_turns_dropped": history_turns_dropped,
        "truncated_count": truncated_count,
        "attachments_truncated": attachments_truncated,
        "attachment_parts": [
            meta for _cand, _block, meta in rendered if meta is not None
        ],
        "attachment_budget_chars": budget_info["attachment_budget_chars"],
        "attachment_chars_used": budget_info["attachment_chars_used"],
        "attachment_chars_remaining": budget_info["attachment_chars_remaining"],
        "budget_chars": budget_chars,
        "retry_count": _total_attempts,
        "prompt_cache_split": cache_split,
    }
    # Per-turn persistence (best-effort by design): the artifact holds
    # xml_blocks plus the full raw output so a truncated inline payload
    # can be recovered from ``output_address`` with native tools. A
    # persistence failure must never fail the turn itself. The clock is
    # injected (universal datetime rule) rather than read from the
    # wall clock inside the helper.
    try:
        result["output_address"] = persist_brain_turn_output(
            project_root,
            history_key,
            task_id,
            diag.get("response_id"),
            xml_blocks,
            output,
            diag.get("status") == "incomplete",
            clock=time.gmtime,
        )
    except OSError as exc:
        print(f"brain-bridge: output persistence skipped ({exc})", file=sys.stderr)
        result["output_address"] = None
    debug: dict[str, Any] = {"provider": diag}
    if fence_drops:
        debug["fenced_blocks"] = len(fence_drops)
        debug["snippets"] = fence_drops
    result["debug"] = debug
    return result


def _upstream_mode() -> str:
    """Upstream protocol mode; override via ``BRAIN_UPSTREAM_MODE``.

    Defaults to ``responses`` (OpenAI Responses API /responses endpoint).
    Set to ``chat_completions`` to connect to OpenAI-compatible
    /chat/completions endpoints (such as MiniMax Flash or custom gateways).
    """
    mode = (
        os.environ.get("BRAIN_UPSTREAM_MODE", "responses").strip().lower()
        or "responses"
    )
    if mode not in ("responses", "chat_completions"):
        raise ValueError(
            f"BRAIN_UPSTREAM_MODE={mode!r} is invalid; expected 'responses' or 'chat_completions'"
        )
    return mode


def _upstream_url() -> str:
    """Upstream endpoint URL resolved based on ``BRAIN_UPSTREAM_MODE``."""
    default = "https://api.openai.com/v1"
    base = os.environ.get("BRAIN_API_BASE", default).strip() or default
    base = _https_guard(base, "BRAIN_API_BASE")
    mode = _upstream_mode()
    if mode == "chat_completions":
        return base.rstrip("/") + "/chat/completions"
    return base.rstrip("/") + "/responses"


def _responses_url() -> str:
    """Responses endpoint; override via ``BRAIN_API_BASE``."""
    return _upstream_url()


def _convert_responses_to_chat_completions_body(body: dict[str, Any]) -> dict[str, Any]:
    """Translate a Responses API request body into a Chat Completions request body.

    Handles:
    - Flattening Responses 'input' and 'instructions' into 'messages' array
    - Converting 'max_output_tokens' to 'max_tokens'
    - Preserving 'model', 'temperature'
    - Mapping 'reasoning.effort' to top-level 'reasoning_effort' when present
    """
    # Responses-only fields with no Chat Completions counterpart. Dropping one
    # silently is worse than saying so: `previous_response_id` in particular
    # carries multi-turn history, so a quiet drop ships the next turn without
    # its context and the model answers blind.
    _CHAT_UNSUPPORTED_FIELDS: tuple[str, ...] = (
        "store",
        "previous_response_id",
        "metadata",
        "include",
        "truncation",
        "service_tier",
        "text",
    )

    chat_body: dict[str, Any] = {
        "model": body.get("model", ""),
    }
    for _dropped in _CHAT_UNSUPPORTED_FIELDS:
        if body.get(_dropped) is not None:
            logger.warning(
                "BRAIN_UPSTREAM_MODE=chat_completions dropped unsupported "
                "Responses field %s; the chat completions wire format has no "
                "equivalent",
                _dropped,
            )
    messages: list[dict[str, Any]] = []

    # System instruction handling
    instructions = body.get("instructions")
    if isinstance(instructions, str) and instructions.strip():
        messages.append({"role": "system", "content": instructions})

    # `input` is a string on the most common single-turn call. Iterating a
    # str yields characters, every one of which fails the dict guard below,
    # so the user turn would vanish without this branch.
    raw_input = body.get("input")
    if isinstance(raw_input, str):
        if raw_input.strip():
            messages.append({"role": "user", "content": raw_input})
        raw_input = []

    for item in raw_input or []:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        # If the item is already a message role
        if role in ("system", "user", "assistant"):
            if isinstance(content, str):
                messages.append({"role": role, "content": content})
            elif isinstance(content, list):
                # Flatten text parts if structured content
                text_parts = []
                for part in content:
                    if isinstance(part, dict):
                        if (
                            part.get("type") in ("text", "output_text")
                            or "text" in part
                        ):
                            text_parts.append(part.get("text", ""))
                    elif isinstance(part, str):
                        text_parts.append(part)
                messages.append({"role": role, "content": "\n".join(text_parts)})
        elif item.get("type") == "message":
            # Responses item format
            msg_role = item.get("role", "assistant")
            item_content = item.get("content")
            if isinstance(item_content, list):
                text_parts = []
                for chunk in item_content:
                    if isinstance(chunk, dict):
                        if (
                            chunk.get("type") in ("text", "output_text")
                            or "text" in chunk
                        ):
                            text_parts.append(chunk.get("text", ""))
                    elif isinstance(chunk, str):
                        text_parts.append(chunk)
                messages.append({"role": msg_role, "content": "\n".join(text_parts)})
            elif isinstance(item_content, str):
                messages.append({"role": msg_role, "content": item_content})
        elif item.get("type") == "function_call":
            # An assistant tool call has no "role" key, so the two branches
            # above cannot see it. Dropping it silently severs a multi-turn
            # tool chain: the model's own call disappears and the next turn
            # shows a tool result with no request behind it.
            call_id = item.get("call_id")
            call_name = item.get("name")
            call_args = item.get("arguments")
            if isinstance(call_name, str) and call_name:
                call_entry: dict[str, Any] = {
                    "id": call_id if isinstance(call_id, str) else call_name,
                    "type": "function",
                    "function": {
                        "name": call_name,
                        # Arguments travel as a JSON string on the chat
                        # completions wire, never as a dict.
                        "arguments": call_args
                        if isinstance(call_args, str)
                        else json.dumps(call_args if call_args is not None else {}),
                    },
                }
                messages.append(
                    {"role": "assistant", "content": None, "tool_calls": [call_entry]}
                )
        elif item.get("type") == "function_call_output":
            # The matching tool result. Chat completions pairs a tool result
            # with role="tool" plus the originating call id, so the id must
            # survive the crossing or the provider rejects the whole request.
            output_payload = item.get("output")
            if isinstance(output_payload, (dict, list)):
                output_payload = json.dumps(output_payload)
            if not isinstance(output_payload, str):
                output_payload = "" if output_payload is None else str(output_payload)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": item.get("call_id"),
                    "content": output_payload,
                }
            )

    chat_body["messages"] = messages

    if "max_output_tokens" in body:
        chat_body["max_tokens"] = body["max_output_tokens"]
    elif "max_tokens" in body:
        chat_body["max_tokens"] = body["max_tokens"]

    if "temperature" in body:
        chat_body["temperature"] = body["temperature"]

    reasoning = body.get("reasoning")
    if isinstance(reasoning, dict) and "effort" in reasoning:
        chat_body["reasoning_effort"] = reasoning["effort"]

    # Tool definitions must survive the crossing, otherwise a
    # chat-completions-only model can never call a tool and the Brain's
    # hands protocol dead-ends. Responses uses a flat function list; chat
    # completions nests the same fields under "function".
    tools = body.get("tools")
    if isinstance(tools, list) and tools:
        mapped_tools: list[dict[str, Any]] = []
        for tool in tools:
            if not isinstance(tool, dict):
                continue
            if tool.get("type") == "function" and isinstance(
                tool.get("function"), dict
            ):
                # Already chat-completions shaped; pass through unchanged.
                mapped_tools.append(tool)
                continue
            name = tool.get("name")
            if not isinstance(name, str) or not name:
                continue
            parameters = tool.get("parameters")
            mapped_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": tool.get("description", ""),
                        "parameters": parameters
                        if isinstance(parameters, dict)
                        else {"type": "object", "properties": {}},
                    },
                }
            )
        if mapped_tools:
            chat_body["tools"] = mapped_tools

    # tool_choice: Responses accepts a bare string or a named-function dict;
    # chat completions needs the nested {"type":"function","function":{"name":..}}.
    tool_choice = body.get("tool_choice")
    if isinstance(tool_choice, str):
        chat_body["tool_choice"] = tool_choice
    elif isinstance(tool_choice, dict) and isinstance(tool_choice.get("name"), str):
        chat_body["tool_choice"] = {
            "type": "function",
            "function": {"name": tool_choice["name"]},
        }

    # Only forward parallel_tool_calls when tools are actually present; sending
    # it without a tools array is a 400 on strict OpenAI-compatible gateways.
    if "tools" in chat_body and "parallel_tool_calls" in body:
        chat_body["parallel_tool_calls"] = body["parallel_tool_calls"]

    return chat_body


def _build_responses_output(
    output_text: str,
    reasoning_text: str,
    tool_calls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Assemble a Responses-shaped ``output`` list from Chat Completions parts.

    Order is deliberate and matches how the Brain scans output: reasoning
    first (diagnostics), then the assistant message, then function calls.
    Sections with no content are omitted rather than emitted empty, because
    an empty ``output_text`` block makes ``parse_responses_text`` return ""
    and the caller cannot tell "no answer" from "empty answer".
    """
    items: list[dict[str, Any]] = []
    if reasoning_text:
        items.append(
            {
                "type": "reasoning",
                "summary": [{"type": "summary_text", "text": reasoning_text}],
            }
        )
    if output_text:
        items.append(
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": output_text}],
            }
        )
    for call in tool_calls:
        function = call.get("function")
        if not isinstance(function, dict):
            continue
        items.append(
            {
                "type": "function_call",
                "call_id": call.get("id"),
                "name": function.get("name"),
                "arguments": function.get("arguments"),
            }
        )
    return items


# Chat Completions finish_reason -> Responses API status/incomplete_reason.
# The Brain branches on `status`, so an unmapped or unknown reason must never
# be reported as a clean completion.
_FINISH_REASON_TO_STATUS: dict[str, tuple[str, str | None]] = {
    "stop": ("completed", None),
    "length": ("incomplete", "max_output_tokens"),
    "content_filter": ("incomplete", "content_filter"),
    "tool_calls": ("completed", None),
    "function_call": ("completed", None),
}


def _responses_status_from_finish(finish_reason: Any) -> tuple[str, str | None]:
    """Map a Chat Completions ``finish_reason`` to (status, incomplete_reason).

    Returns ``("completed", None)`` only for reasons that mean the model
    produced a final answer. An absent or unrecognised reason returns
    ``("incomplete", "unknown_finish_reason")`` so a truncated or filtered
    response is never mistaken for success.
    """
    if isinstance(finish_reason, str):
        mapped = _FINISH_REASON_TO_STATUS.get(finish_reason.strip().lower())
        if mapped is not None:
            return mapped
    return ("incomplete", "unknown_finish_reason")


def _upstream_failure_message(resp_data: Any) -> str | None:
    """Return a human-readable failure reason when a response is not usable.

    Only a terminal failure returns a message. ``status=incomplete`` is NOT a
    failure: a length-truncated answer is still a real answer the Brain can
    parse, and treating it as an error would discard usable output. An
    incomplete response is annotated instead (see the caller).

    Returns ``None`` when the response is usable, so the caller can proceed
    with normal parsing.
    """
    if not isinstance(resp_data, dict):
        return None
    status = resp_data.get("status")
    if not isinstance(status, str):
        return None
    if status == "failed":
        error = resp_data.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message.strip():
                return f"brain upstream failed: {message.strip()}"
        return "brain upstream failed: no error message provided"
    return None


def _convert_chat_completions_to_responses_data(
    chat_resp: dict[str, Any],
) -> dict[str, Any]:
    """Translate a Chat Completions response JSON into the Responses API structure.

    Normalizes choices[0].message.content into output[type=message] and usage fields.
    """
    if not isinstance(chat_resp, dict):
        return {"output": []}

    # Upstream errors arrive as a 200-with-error body on some gateways and as a
    # non-2xx body on others. Surface both as status=failed with the message
    # preserved, so the Brain reports a failure instead of empty output.
    upstream_error = chat_resp.get("error")
    if upstream_error:
        err_message = (
            upstream_error.get("message")
            if isinstance(upstream_error, dict)
            else str(upstream_error)
        )
        return {
            "id": chat_resp.get("id"),
            "model": chat_resp.get("model"),
            "status": "failed",
            "error": {"message": err_message or "upstream error"},
            "output": [],
        }

    output_text = ""
    _finish_reason: Any = None
    # Tool calls and reasoning are first-class outputs for an agent brain: a
    # chat-completions model that answers with a tool call has no message
    # content at all, so reading content alone silently returns empty output.
    tool_calls: list[dict[str, Any]] = []
    reasoning_text = ""
    choices = chat_resp.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            _finish_reason = first.get("finish_reason")
            msg = first.get("message")
            if isinstance(msg, dict):
                # Some gateways return content as a list of parts; flatten it
                # with the same rule the request converter uses.
                raw_content = msg.get("content")
                if isinstance(raw_content, str):
                    output_text = raw_content
                elif isinstance(raw_content, list):
                    parts = [
                        p.get("text", "")
                        for p in raw_content
                        if isinstance(p, dict) and isinstance(p.get("text"), str)
                    ]
                    output_text = "\n".join(parts)
                # MiniMax and DeepSeek-style gateways name it reasoning_content;
                # OpenAI-compatible ones use message.reasoning.
                for key in ("reasoning_content", "reasoning"):
                    candidate = msg.get(key)
                    if isinstance(candidate, str) and candidate.strip():
                        reasoning_text = candidate
                        break
                raw_calls = msg.get("tool_calls")
                if isinstance(raw_calls, list):
                    tool_calls = [c for c in raw_calls if isinstance(c, dict)]

    # Status comes from the finish reason, never hardcoded: downstream
    # session classification reads this field to decide XML_EXTRACTED vs REPORT.
    _status, _incomplete_reason = _responses_status_from_finish(_finish_reason)

    resp_data: dict[str, Any] = {
        "id": chat_resp.get("id"),
        "model": chat_resp.get("model"),
        "status": _status,
        "output": _build_responses_output(output_text, reasoning_text, tool_calls),
    }

    if _incomplete_reason is not None:
        resp_data_incomplete: dict[str, Any] = {"reason": _incomplete_reason}
        resp_data["incomplete_details"] = resp_data_incomplete

    # Usage mapping: a counter that the upstream omitted stays OMITTED.
    # Storing None here would leak into quota accounting and budget math,
    # where None inside an arithmetic expression raises or silently voids
    # the total. Presence of the key means "the provider reported a number".
    usage = chat_resp.get("usage")
    if isinstance(usage, dict):
        mapped_usage: dict[str, int] = {}
        if isinstance(usage.get("prompt_tokens"), int):
            mapped_usage["input_tokens"] = usage["prompt_tokens"]
        if isinstance(usage.get("completion_tokens"), int):
            mapped_usage["output_tokens"] = usage["completion_tokens"]
        if isinstance(usage.get("total_tokens"), int):
            mapped_usage["total_tokens"] = usage["total_tokens"]
        # Derived total only when the provider omitted it but both halves exist.
        if "total_tokens" not in mapped_usage and (
            "input_tokens" in mapped_usage and "output_tokens" in mapped_usage
        ):
            mapped_usage["total_tokens"] = (
                mapped_usage["input_tokens"] + mapped_usage["output_tokens"]
            )
        if mapped_usage:
            resp_data["usage"] = mapped_usage

    return resp_data


def _get_reasoning_effort() -> str:
    """Reasoning effort; override via ``BRAIN_REASONING_EFFORT``.

    Defaults to ``medium`` — the default the Luna model itself advertises.
    ``xhigh`` (and ``max``) allocate roughly 95% of ``max_output_tokens`` to
    reasoning, so a modest cap leaves almost nothing for the visible answer
    while the reasoning tokens are still billed.

    Validated against the official Responses vocabulary (Task 329 F8):
    none/minimal/low/medium/high/xhigh/max. Anything else raises instead
    of reaching the provider as a 400.
    """
    val = os.environ.get("BRAIN_REASONING_EFFORT", "medium").strip() or "medium"
    if not re.fullmatch(r"[\w.-]{1,64}", val):
        raise ValueError(f"bad reasoning effort: {val!r}")
    if val.lower() not in _EFFORT_VOCABULARY:
        raise ValueError(
            f"BRAIN_REASONING_EFFORT={val!r} is not a Responses effort; "
            f"expected one of {sorted(_EFFORT_VOCABULARY)}"
        )
    # Normalized to lower (Task 329 QA F4): the provider vocabulary is
    # lowercase, and a preserved `LOW`/`XHigh` would ship an invalid
    # effort string after passing validation.
    return val.lower()


def _task_state_note(task_id: Optional[str], project_root: Optional[str] = None) -> str:
    """One-line state note for the empty-output retry hint (never raises).

    Format: ``path | status | diff-hash``. Lets the retry-er judge whether
    the next answer sees the same file version instead of a stale one.
    Unresolvable task → "unknown".
    """
    try:
        if not task_id or not isinstance(task_id, str):
            return "unknown"
        path = _resolve_task_file(task_id, project_root=project_root)
        if path is None:
            return "unknown"
        try:
            rel = path.resolve().relative_to(_workspace_root().resolve()).as_posix()
        except (OSError, ValueError):
            rel = path.name
        text = path.read_text(encoding="utf-8", errors="replace")
        status = "unknown"
        m = re.search(r"^\*\*Status:\*\*\s*(.+?)\s*$", text, re.M)
        if m:
            status = m.group(1)[:32]
        diff = extract_task_diff(text)
        dh = (
            hashlib.sha256(diff.encode("utf-8")).hexdigest()[:8]
            if diff.strip()
            else "no-diff"
        )
        return f"{rel} | status={status} | diff={dh}"
    except Exception:
        return "unknown"


def _over_budget_hint(
    est_input_tokens: int,
    reserved_output_tokens: int,
    window: Optional[int] = None,
    margin: Optional[int] = None,
    trimmed_history: int = 0,
    trimmed_diffs: int = 0,
    trimmed_context: int = 0,
    trimmed_bundle: int = 0,
    task_id: Optional[str] = None,
    state: Optional[str] = None,
) -> str:
    """Retry hint substituted when the pre-send budget guard trips.

    Pure function (no I/O) so tests can assert the contract directly.
    The bridge MUST NOT invent verdict content here — hint only.
    ``state`` is a precomputed task path/status/diff note (see
    ``_task_state_note``); the hint stays pure, the caller does the I/O.
    Window and margin resolve from env when omitted.
    """
    if window is None:
        window = _provider_window_tokens()
    if margin is None:
        margin = _budget_margin_tokens()
    where = f" for task {task_id}" if task_id else ""
    note = f" Current state: {state}." if state else ""
    return (
        f"BRAIN_BUDGET_OVER: estimated input ~{est_input_tokens} tokens plus "
        f"reserved output {reserved_output_tokens} tokens exceeds the "
        f"{window}-token provider window minus {margin} margin{where} "
        f"(trimmed history turns={trimmed_history}, diffs={trimmed_diffs}, "
        f"context={trimmed_context}, bundle={trimmed_bundle}). "
        "The provider was NOT called, so retrying as-is will fail the same "
        "way. Retry leaner: same task_id, include_bundle=false, short "
        "prompt, or narrower context_paths — never raise the output cap "
        "to fix this." + note
    )


def _empty_output_hint(
    task_id: Optional[str] = None, state: Optional[str] = None
) -> str:
    """Retry instruction substituted for a blank model output.

    Pure function (no I/O) so tests can assert the contract directly.
    The bridge MUST NOT invent verdict content here — hint only.
    ``state`` is a precomputed task path/status/diff note (see
    ``_task_state_note``); the hint stays pure, the caller does the I/O.
    """
    where = f" for task {task_id}" if task_id else ""
    note = f" Current state: {state}." if state else ""
    return (
        f"{EMPTY_OUTPUT_RETRY}: the model returned no text{where} "
        "(transport/model flake, never a verdict). "
        "Do NOT act on this result and do NOT count it as a rejection. "
        "Retry ONCE, lean: same task_id, include_bundle=false, short prompt. "
        "State check on the retry: the lean call drops the bundle, so if its "
        "answer judges stale or missing context (wrong file version, no diff "
        "seen), re-run ONCE with the full bundle plus diff "
        "(include_bundle=true, include_diff=true) before escalating. "
        "If the full-context call is still empty, escalate to the Manager." + note
    )


def _as_int(value: Any) -> Optional[int]:
    """Coerce a usage counter to int; ``None`` when absent/unparseable.

    Non-finite floats (``nan``/``inf``) raise inside ``int()`` — they are
    swallowed here so malformed provider usage can never abort diagnosis
    (Task 259 hotfix, QA F2).
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        try:
            return int(value)
        except (ValueError, OverflowError):
            return None
    return None


def parse_responses_diagnostics(data: Any) -> dict:
    """Extract provider diagnostics from a Responses payload (pure).

    Never raises on missing or malformed fields: every key is present with
    a ``None`` or zeroed value so the caller can return a stable shape on
    every turn (Task 259 contract). ``refusal`` collects refusal text from
    both direct ``type=="refusal"`` output items and nested content chunks,
    so it does not depend on a ``type=="message"`` item existing.
    """
    diag: dict[str, Any] = {
        "status": None,
        "incomplete_reason": None,
        "usage": {
            "input_tokens": None,
            "output_tokens": None,
            "reasoning_tokens": None,
            "cached_tokens": None,
            "total_tokens": None,
        },
        "error": None,
        "error_code": None,
        "error_type": None,
        "refusal": None,
        # Response identity (Task 329 F5): echoed by the provider, read
        # so a silent model substitution by a routing gateway is visible.
        # provider_status_code is set only on the fatal-transport path
        # (Task 329 QA F5): the HTTP status that produced the structured
        # REPORT, so debug.provider never hides it as status=None.
        "response_model": None,
        "response_id": None,
        "service_tier": None,
        "provider_status_code": None,
    }
    if not isinstance(data, dict):
        return diag

    response_model = data.get("model")
    if isinstance(response_model, str) and response_model:
        diag["response_model"] = response_model

    response_id = data.get("id")
    if isinstance(response_id, str) and response_id:
        diag["response_id"] = response_id

    service_tier = data.get("service_tier")
    if isinstance(service_tier, str) and service_tier:
        diag["service_tier"] = service_tier

    status = data.get("status")
    if isinstance(status, str) and status:
        diag["status"] = status

    incomplete = data.get("incomplete_details")
    if isinstance(incomplete, dict):
        reason = incomplete.get("reason")
        if isinstance(reason, str) and reason:
            diag["incomplete_reason"] = reason

    usage = data.get("usage")
    if isinstance(usage, dict):
        diag["usage"]["input_tokens"] = _as_int(usage.get("input_tokens"))
        diag["usage"]["output_tokens"] = _as_int(usage.get("output_tokens"))
        diag["usage"]["total_tokens"] = _as_int(usage.get("total_tokens"))
        in_details = usage.get("input_tokens_details")
        if isinstance(in_details, dict):
            # Prompt-cache visibility (Task 329 F4): a populated value
            # proves the cache key is working; None means unreported.
            diag["usage"]["cached_tokens"] = _as_int(in_details.get("cached_tokens"))
        details = usage.get("output_tokens_details")
        if isinstance(details, dict):
            diag["usage"]["reasoning_tokens"] = _as_int(details.get("reasoning_tokens"))

    error = data.get("error")
    if isinstance(error, str) and error.strip():
        diag["error"] = error.strip()
    elif isinstance(error, dict):
        message = error.get("message")
        if isinstance(message, str) and message.strip():
            diag["error"] = message.strip()
        elif error:
            # Serialization must never raise on exotic scalar types inside the
            # error object (Task 259 hotfix) — fall back to repr.
            try:
                diag["error"] = json.dumps(error, ensure_ascii=False)
            except (TypeError, ValueError):
                diag["error"] = str(error)
        # Machine-readable billing/spend/quota classification (Task 329
        # F6): the detail lives in error.code, not in error.type or the
        # message text.
        code = error.get("code")
        if isinstance(code, str) and code.strip():
            diag["error_code"] = code.strip()
        err_type = error.get("type")
        if isinstance(err_type, str) and err_type.strip():
            diag["error_type"] = err_type.strip()
    elif error is not None and not isinstance(error, list):
        diag["error"] = str(error)

    output = data.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "refusal":
                text = item.get("refusal")
                if isinstance(text, str) and text.strip():
                    diag["refusal"] = text.strip()
                    break
            if item.get("type") == "message":
                # "content" may be absent, null, or a malformed scalar; only a
                # real list is iterable (Task 259 hotfix, QA F1).
                content = item.get("content")
                if not isinstance(content, list):
                    continue
                for chunk in content:
                    if isinstance(chunk, dict) and chunk.get("type") == "refusal":
                        text = chunk.get("refusal")
                        if isinstance(text, str) and text.strip():
                            diag["refusal"] = text.strip()
                            break
                if diag["refusal"]:
                    break
    return diag


def _replayable_provider_items(resp_data: Any) -> tuple[Any, Any, list]:
    """Extract continuity items from a Responses payload (Task 329 F2).

    Pure (no I/O): returns ``(phase, response_id, provider_items)``.
    ``phase`` comes from the first assistant message item that carries
    one (commentary vs final answer); ``response_id`` is the provider
    response id; ``provider_items`` are the non-message output items
    (reasoning blocks with encrypted content) replayed verbatim after
    their turn. Message items are NOT replayed — their text already
    rides the transcript content rows, and replaying both would
    duplicate them. Anything malformed yields ``(None, None, [])``.
    """
    if not isinstance(resp_data, dict):
        return None, None, []
    response_id = resp_data.get("id")
    if not isinstance(response_id, str) or not response_id:
        response_id = None
    phase: Any = None
    items: list = []
    output = resp_data.get("output")
    if isinstance(output, list):
        for entry in output:
            if not isinstance(entry, dict):
                continue
            if entry.get("type") == "message":
                if phase is None:
                    maybe_phase = entry.get("phase")
                    if isinstance(maybe_phase, str) and maybe_phase:
                        phase = maybe_phase
                continue
            items.append(entry)
    return phase, response_id, items


def _model_substitution_note(diag: dict, requested: str) -> Optional[str]:
    """Warn when the provider served a different model than requested.

    Pure (no I/O): returns the warning text or None. The bridge points
    at a routing gateway that may fall back or downgrade tiers, so a
    silent substitution would invalidate the tier routing that chose
    the requested id. A mismatch warns — it never fails the turn.
    """
    response_model = diag.get("response_model")
    if (
        isinstance(response_model, str)
        and response_model
        and isinstance(requested, str)
        and requested
        and response_model != requested
    ):
        return (
            f"model substitution: requested {requested!r} but provider "
            f"served {response_model!r} — tier routing assumed the "
            "requested id"
        )
    return None


def _log_provider_diagnostics(diag: dict) -> None:
    """Emit one compact diagnostics line to stderr on every turn (AC1).

    Includes the visible-token count (output minus reasoning). Reasoning
    tokens are billed as output and count against ``max_output_tokens``, so
    a near-zero visible count is the signature of a starved answer.
    """
    usage = diag.get("usage")
    if not isinstance(usage, dict):
        usage = {}
    out_tokens = usage.get("output_tokens")
    reasoning_tokens = usage.get("reasoning_tokens")
    visible_tokens: Optional[int] = None
    if isinstance(out_tokens, int) and isinstance(reasoning_tokens, int):
        visible_tokens = out_tokens - reasoning_tokens
    print(
        "brain-bridge: provider diag "
        f"status={diag.get('status')} "
        f"incomplete_reason={diag.get('incomplete_reason')} "
        f"input_tokens={usage.get('input_tokens')} "
        f"output_tokens={out_tokens} "
        f"reasoning_tokens={reasoning_tokens} "
        f"visible_tokens={visible_tokens} "
        f"cached_tokens={usage.get('cached_tokens')} "
        f"total_tokens={usage.get('total_tokens')} "
        f"model={diag.get('response_model')} "
        f"tier={diag.get('service_tier')} "
        f"http_status={diag.get('provider_status_code')} "
        f"error={diag.get('error')!r} error_code={diag.get('error_code')!r} "
        f"refusal={diag.get('refusal')!r}",
        file=sys.stderr,
    )


def _provider_error_hint(error: str, code: Optional[str] = None) -> str:
    """Surface a top-level provider error verbatim (Task 259, terminal).

    Task 329 F6: a terminal billing/spend/quota code appends the
    actionable remedy — retrying those can never restore access.
    """
    hint = (
        f"{PROVIDER_ERROR}: the provider returned an error "
        "(terminal for this turn, never a verdict):\n"
        f"{error}"
    )
    if isinstance(code, str) and code.strip().lower() in _TERMINAL_429_CODES:
        hint += (
            "\nThis is a billing, spend, or quota error: do NOT retry — "
            "add credits or raise the organization/project spend or usage "
            "limit before sending another request."
        )
    return hint


def _provider_refusal_hint(refusal: str) -> str:
    """Surface a refusal content item verbatim (Task 259, terminal)."""
    return (
        f"{PROVIDER_REFUSAL}: the model refused this request "
        "(terminal for this turn, never a verdict):\n"
        f"{refusal}"
    )


def _output_budget_hint(
    diag: dict, task_id: Optional[str] = None, state: Optional[str] = None
) -> str:
    """Terminal hint for a reasoning-exhausted output budget (Task 259).

    Deliberately NOT ``EMPTY_OUTPUT_RETRY``: a lean retry reuses the same
    effort and cap, so it can never recover a ``max_output_tokens``
    finish. Pure function (no I/O), so tests assert the contract directly.
    """
    where = f" for task {task_id}" if task_id else ""
    note = f" Current state: {state}." if state else ""
    usage = diag.get("usage") or {}
    return (
        f"{OUTPUT_BUDGET_EXHAUSTED}: the model produced no visible text{where} "
        "because its reasoning trace exhausted the output-token budget "
        "(status=incomplete, reason=max_output_tokens). "
        "This is NOT a transport flake: do NOT lean-retry and do NOT count "
        "it as a rejection — the same effort/cap would fail identically. "
        "Remediate by lowering BRAIN_REASONING_EFFORT (e.g. to medium or low) "
        "or raising BRAIN_MAX_TOKENS (recommend 32768 or higher when the "
        "model supports it), then re-run the turn with full context. "
        f"Usage: input={usage.get('input_tokens')} "
        f"output={usage.get('output_tokens')} "
        f"reasoning={usage.get('reasoning_tokens')} "
        f"total={usage.get('total_tokens')}." + note
    )


#: Machine token: partial truncation still unrecovered after the single
#: server-side re-issue (Task 291). Terminal for the turn: the caller
#: MUST NOT retry as-is — a same-shape retry re-bills the full input +
#: reasoning budget and fails identically. Remediate via config (lower
#: effort / smaller prompt), then re-run. NEVER rename without a task:
#: callers and regression tests match this exact string.
TRUNCATION_UNRECOVERABLE = "TRUNCATION_UNRECOVERABLE"

#: Official Responses reasoning-effort vocabulary (Task 329 F8).
#: Model-dependent subset applies per model; the bridge accepts the full
#: vocabulary and lets the provider reject per-model unsupported values
#: (surfaced as a structured REPORT via the fatal-error path, never a
#: raw exception).
_EFFORT_VOCABULARY = frozenset(
    {"none", "minimal", "low", "medium", "high", "xhigh", "max"}
)

#: One-notch reasoning-effort step-down for truncation recovery (Task
#: 291). Lower effort frees visible-answer share inside the same
#: ``max_output_tokens`` cap — the only headroom source once the cap
#: already sits at the model ceiling. Unknown/non-string values keep
#: the current effort (``low`` when there is none to keep): the floor
#: guard treats equality as no-recovery, so an unknown value can never
#: RAISE effort the way the old ``medium`` fallback did (Task 329 F8).
_EFFORT_STEPDOWN = {
    "max": "xhigh",
    "xhigh": "high",
    "high": "medium",
    "medium": "low",
    "low": "minimal",
    "minimal": "minimal",
}


def _step_down_effort(effort: object) -> str:
    """Return one notch below ``effort`` (pure, offline).

    A value already in the ladder maps down it; an unknown string keeps
    itself (recovery is then a no-op via the floor guard); a missing or
    non-string value falls to ``low``.
    """
    if isinstance(effort, str) and effort.strip():
        key = effort.strip().lower()
        if key in _EFFORT_STEPDOWN:
            return _EFFORT_STEPDOWN[key]
        return effort
    return "low"


def _truncation_exhausted_hint(
    diag: dict,
    task_id: Optional[str] = None,
    state: Optional[str] = None,
    first_effort: Optional[str] = None,
    recovery_effort: Optional[str] = None,
) -> str:
    """Terminal hint after recovery also truncated (Task 291).

    Pure function (no I/O) so tests assert the contract directly. The
    bridge already spent its one bounded re-issue — the caller must not
    spend more turns looping on this shape.
    """
    where = f" for task {task_id}" if task_id else ""
    note = f" Current state: {state}." if state else ""
    usage = diag.get("usage") or {}
    return (
        f"{TRUNCATION_UNRECOVERABLE}: the turn truncated twice{where} "
        "(status=incomplete, reason=max_output_tokens, no usable XML even "
        "after one server-side re-issue with stepped-down reasoning effort). "
        "This is NOT a transport flake: do NOT retry this turn as-is and do "
        "NOT count it as a rejection — the same shape would fail identically "
        "while re-billing the full input + reasoning budget. Remediate by "
        "lowering BRAIN_REASONING_EFFORT (e.g. to medium or low) or shrinking "
        "the prompt (include_bundle=false, shorter instruction), then re-run "
        "the turn with full context. "
        f"First effort={first_effort} recovery effort={recovery_effort}. "
        f"Usage: input={usage.get('input_tokens')} "
        f"output={usage.get('output_tokens')} "
        f"reasoning={usage.get('reasoning_tokens')} "
        f"total={usage.get('total_tokens')}." + note
    )


def _maybe_warn_reasoning_budget(effort: str, max_tokens: int) -> None:
    """Warn (non-breaking) when high effort runs with a small cap (C6).

    Reasoning tokens count against ``max_output_tokens``; ``xhigh`` claims
    roughly 95% of the cap, so a small cap leaves almost nothing for the
    visible answer. The 32768 default keeps the risky combination out of
    the way, but an explicit ``BRAIN_MAX_TOKENS`` can still reintroduce it,
    so the warning fires before the provider request rather than failing
    silently.
    """
    if effort in _HIGH_EFFORT and max_tokens < _REASONING_BUDGET_FLOOR:
        print(
            f"brain-bridge: warning: reasoning effort {effort!r} with "
            f"max_output_tokens={max_tokens} (< {_REASONING_BUDGET_FLOOR}) "
            "can exhaust the output budget and return blank text; raise "
            "BRAIN_MAX_TOKENS or lower BRAIN_REASONING_EFFORT.",
            file=sys.stderr,
        )


def parse_responses_text(data: dict) -> str:
    """Pull plain text out of a Responses-API payload (pure, offline)."""
    parts: list[str] = []
    output = data.get("output") if isinstance(data, dict) else None
    if not isinstance(output, list):
        return ""
    for item in output:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "message":
            for chunk in item.get("content") or []:
                if isinstance(chunk, dict) and chunk.get("type") == "output_text":
                    text = chunk.get("text")
                    if isinstance(text, str) and text:
                        parts.append(text)
        elif item.get("type") == "output_text":
            text = item.get("text")
            if isinstance(text, str) and text:
                parts.append(text)
        elif item.get("type") == "function_call":
            name = item.get("name")
            args = item.get("arguments")
            if isinstance(name, str):
                parts.append(f"{name}({args or ''})")
    return "\n".join(parts)


if __name__ == "__main__":
    _transport = os.environ.get("MCP_TRANSPORT", "streamable-http")
    # Singleton default (Task 279 V3): all callers consume these servers as
    # remote http singletons, so an unset MCP_TRANSPORT must not silently
    # drop into stdio while the unit reports active. Explicit "stdio"
    # still works for local debugging.
    mcp.run(transport=_transport)
