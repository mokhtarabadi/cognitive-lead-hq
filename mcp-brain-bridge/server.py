#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.0,<2.0",
#     "httpx>=0.28",
# ]
# ///

"""Unified Brain bridge MCP server (Task 190).

One tool, ``brain_turn``: the Hands builds a user prompt from its current
machine state (e.g. "QA engineer please make the adversarial testing" +
the task file), the server prepends the latest system prompt (read from
the global install) as the system message, calls the LLM over the
OpenAI Responses API via httpx,
and returns the output — with any machine XML blocks extracted.

Manager rule: if the output has XML, the Hands takes only the XML; if
no XML, the Hands takes the whole output. Admin questions inside the
output are relayed by the Hands to the Manager; the answer goes back
in as the next ``brain_turn`` user prompt. No gates, no per-persona
commands — the auto-load persona + current modes in the system prompt
cover identity.

Per-task chat history (manager order, Task 190): the LLM is stateless,
so every ``brain_turn`` with a ``task_id`` loads that task's prior
user/assistant messages from its transcript file and sends them along
— like a chat interface, first message to last, until the task closes.
Each task keeps its own conversation under the sessions root
(``BRAIN_SESSIONS_ROOT``, default ``~/.config/opencode/brain-sessions``,
``<task_id>/transcript.jsonl``, JSON lines). History is bounded (last
40 messages) so long tasks cannot overflow the context.

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
from pathlib import Path
from typing import Any, Optional

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

mcp = FastMCP("BrainBridge")

# XML blocks the Brain may emit. Hands executes these; everything else
# is conversation. Kept as plain names (no angle brackets) for the regex.
XML_BLOCK_TAGS = (
    "hands_discovery_task",
    "hands_implementation_task",
    "hands_combined_task",
    "failure_report",
)

_XML_RE = re.compile(
    r"<(" + "|".join(XML_BLOCK_TAGS) + r")>.*?</\1>", re.DOTALL
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

# Task ids become directory names. Strict allowlist: anything else
# (``..``, separators, empty) raises instead of being mangled.
_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

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

# Text extensions readable via read_file / searchable via grep_files.
_ALLOWED_READ_SUFFIXES = frozenset(
    {".md", ".txt", ".json", ".yaml", ".yml", ".toml"}
)

# Directories never descended into by grep_files.
_SKIP_DIRS = frozenset(
    {".git", "__pycache__", ".venv", "node_modules", ".pytest_cache"}
)


def _workspace_root() -> Path:
    """Repo root for context reads; override via ``BRAIN_WORKSPACE_ROOT``."""
    override = os.environ.get("BRAIN_WORKSPACE_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


def _resolve_under_root(rel: str, root: Optional[Path] = None) -> Path:
    """Resolve ``rel`` under the workspace root; raise ValueError on escape."""
    base = (root if root is not None else _workspace_root()).resolve()
    candidate = (base / rel).resolve()  # realpath: kills symlink escape
    if candidate != base and base not in candidate.parents:
        raise ValueError(f"path outside workspace root: {rel!r}")
    return candidate


_TASK_DIFF_BEGIN = "<!-- BEGIN_GIT_DIFF -->"
_TASK_DIFF_END = "<!-- END_GIT_DIFF -->"
_TASK_FILE_MARKER = "[task-file:"
_TASK_KANBAN_DIRS = ("backlog", "in-progress", "qa", "completed", "archive")
_TASK_ATTACH_CAP = 12000
_TASK_ATTACH_CAP = 12000


def _task_id_ok(tid: object) -> bool:
    """Allowlist for task ids (mirrors loop_guard): letters, digits,
    underscore, hyphen; must start alnum; max 64 chars. Blocks
    traversal (../), separators (/), and glob metacharacters (*?[]).
    Uses the module-level compiled _TASK_ID_RE (shared with the
    history-path sanitizer — do NOT redefine it here)."""
    return isinstance(tid, str) and bool(_TASK_ID_RE.match(tid))


def _resolve_task_file(task_id: str) -> Path | None:
    """Resolve a Brain task_id to its task file (None when unresolvable).

    Tries `<task_id>-*.md` in each Kanban dir (lane order: backlog,
    in-progress, qa, completed, archive — first match wins), then
    progressively strips trailing `-segment`s (so session id `194-qa`
    finds task file `194-*.md`). The allowlist rejects traversal,
    separators, and glob metacharacters before any filesystem touch.
    Never raises — returns None instead.
    """
    try:
        if not _task_id_ok(task_id):
            return None
        tid = task_id.strip()
        root = _workspace_root() / "tasks"
        candidates = [tid]
        while "-" in candidates[-1]:
            candidates.append(candidates[-1].rsplit("-", 1)[0])
        for cand in candidates:
            for lane in _TASK_KANBAN_DIRS:
                matches = sorted((root / lane).glob(cand + "-*.md"))
                if matches:
                    return matches[0]
        return None
    except Exception:
        return None


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
        tail = rest[start + len(_TASK_DIFF_BEGIN):]
        end = tail.find(_TASK_DIFF_END)
        if end < 0:
            omitted += tail.count("\n") + 1
            truncated = True
            break
        omitted += tail.count("\n", 0, end) + 1
        rest = tail[end + len(_TASK_DIFF_END):]
    if not omitted:
        return text, 0, False
    note = (
        f"[Factual Git Diff omitted — {omitted} lines; "
        + f"pull ranges via read_file({rel!r}, offset, limit)]"
    )
    if truncated:
        note += " [diff truncated: unclosed block cut to EOF]"
    return "".join(parts) + note, omitted, truncated


def _build_task_attach(task_id: str) -> str:
    """Assemble the labeled task-file block ('' when unresolvable).

    Contains the task file's working content (Goal/Notes/TODOs/AC/
    evidence/log) minus the Factual Git Diff block, fenced so the
    XML extractor never mistakes task prose for Brain output blocks.
    Content caps at _TASK_ATTACH_CAP chars. Never raises.
    """
    try:
        path = _resolve_task_file(task_id)
        if path is None:
            return ""
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.name
        cleaned, _omitted, _truncated = _strip_task_diff(text, rel)
        if len(cleaned) > _TASK_ATTACH_CAP:
            cleaned = cleaned[:_TASK_ATTACH_CAP] + "\n[...truncated]"
        tid = task_id.strip() if isinstance(task_id, str) else "task"
        return (
            f"{_TASK_FILE_MARKER}{tid}: {rel}]\n"
            + "```markdown\n" + cleaned + "\n```"
        )
    except Exception as exc:  # never fail a turn on attach problems
        print(f"brain-bridge: task attach skipped ({exc})", file=sys.stderr)
        return ""


def _build_context_bundle() -> str:
    """Assemble the labeled small-file bundle (never raises on Absent-File)."""
    root = _workspace_root()
    parts: list[str] = []
    missing = 0
    for rel in _BUNDLE_FILES:
        header = f"=== {rel} ==="
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except (FileNotFoundError, NotADirectoryError, OSError):
            parts.append(header + f"\n[missing: {rel}]")
            missing += 1
            continue
        if len(text) > _BUNDLE_FILE_CAP:
            text = text[:_BUNDLE_FILE_CAP] + "\n[truncated]"
        parts.append(header + "\n" + text)
    if missing:
        print(
            f"brain-bridge: context bundle skipped {missing} missing files",
            file=sys.stderr,
        )
    return "\n\n".join(parts)


def _read_file_impl(path: str, offset: int = 1, limit: int = 200) -> dict[str, Any]:
    """Numbered-line slice of a workspace text file (1-indexed offset)."""
    if not isinstance(path, str) or not path.strip():
        raise ValueError(f"bad path: {path!r}")
    if offset < 1:
        raise ValueError(f"bad offset (1-indexed): {offset!r}")
    if limit < 1:
        raise ValueError(f"bad limit: {limit!r}")
    resolved = _resolve_under_root(path)
    if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
        raise ValueError(f"unsupported extension: {path!r}")
    text = resolved.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    total = len(lines)
    end = min(offset - 1 + limit, total)
    numbered = [f"{n}: {lines[n - 1]}" for n in range(offset, end + 1)]
    return {
        "path": path,
        "offset": offset,
        "limit": limit,
        "total_lines": total,
        "lines": numbered,
    }


def _grep_files_impl(pattern: str, subdir: str = ".") -> list[str]:
    """Python-regex search over workspace text files (max 30 hits)."""
    try:
        rx = re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"bad regex: {pattern!r} ({exc})") from exc
    root = _workspace_root().resolve()
    base = _resolve_under_root(subdir, root)
    if not base.is_dir():
        return []
    hits: list[str] = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            if Path(name).suffix.lower() not in _ALLOWED_READ_SUFFIXES:
                continue
            fpath = Path(dirpath) / name
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = fpath.resolve().relative_to(root).as_posix()
            for lineno, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    hits.append(f"{rel}:{lineno}: {line.strip()[:200]}")
                    if len(hits) >= 30:
                        return hits
    return hits


@mcp.tool()
def get_context_bundle() -> str:
    """Return the labeled small-file context bundle from the workspace root.

    Missing files become ``[missing: path]`` marker lines (never raise);
    each file caps at 60000 chars with a ``[truncated]`` marker.
    """
    return _build_context_bundle()


@mcp.tool()
def read_file(path: str, offset: int = 1, limit: int = 200) -> dict[str, Any]:
    """Read numbered lines from a workspace text file (1-indexed offset)."""
    return _read_file_impl(path, offset, limit)


@mcp.tool()
def grep_files(pattern: str, subdir: str = ".") -> list[str]:
    """Regex-search workspace text files; up to 30 ``path:line: excerpt`` hits."""
    return _grep_files_impl(pattern, subdir)

# Prompt overrides must be real prompt files: .md only, resolved under
# the repo root or ~/.config/opencode (the two legitimate homes).
_PROMPT_SUFFIX = ".md"


def _check_prompt_path(path: Path) -> Path:
    """Resolve an override path and reject anything outside the two
    legitimate prompt homes or without a .md suffix."""
    resolved = path.expanduser().resolve()  # realpath: kills symlink escape
    roots = [
        Path(__file__).resolve().parent.parent,
        Path.home() / ".config" / "opencode",
    ]
    if resolved.suffix.lower() != _PROMPT_SUFFIX or not any(
        resolved == root or root in resolved.parents for root in roots
    ):
        raise ValueError(f"system prompt override outside allowed roots: {path}")
    return resolved


def load_system_prompt(explicit_path: Optional[str] = None) -> str:
    """Read the system prompt text. Order: explicit arg, BRAIN_SYSTEM_PROMPT
    env, global install copy. Raises FileNotFoundError when missing.
    Overrides are constrained to the two legitimate prompt homes
    (repo root, ~/.config/opencode) with a .md suffix."""
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(_check_prompt_path(Path(explicit_path)))
    env_path = os.environ.get("BRAIN_SYSTEM_PROMPT", "").strip()
    if env_path:
        candidates.append(_check_prompt_path(Path(env_path)))
    candidates.append(Path.home() / ".config" / "opencode" / "system-prompt.md")
    for path in candidates:
        if path.is_file():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(
        "No system prompt found; checked: "
        + ", ".join(str(p) for p in candidates)
    )


def extract_xml_blocks(output: str) -> list[str]:
    """Return verbatim XML control blocks in document order. Fenced code
    blocks are stripped first (XML inside backticks is documentation, not
    instructions — fence-only output means REPORT). Empty list means plain
    conversation — the Hands takes the whole output."""
    clean, _ = _strip_fences(output)
    return [m.group(0) for m in _XML_RE.finditer(clean)]


def _get_brain_model() -> str:
    """LLM model for Brain turns; override via ``BRAIN_MODEL``."""
    default = "muse-spark-1.3-contributor-free"
    return os.environ.get("BRAIN_MODEL", default).strip() or default


def _get_max_tokens() -> int:
    """Cap for Brain turns; override via ``BRAIN_MAX_TOKENS``."""
    try:
        return int(os.environ.get("BRAIN_MAX_TOKENS", "16384").strip() or "16384")
    except ValueError:
        return 16384


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
_FATAL_STATUS = {400, 401, 403, 404, 422}

# Overall deadline (seconds) for the whole retry sequence. Sleeps are
# capped by the remaining budget; hitting the deadline fast-fails instead
# of sleeping past it.
_OVERALL_DEADLINE_S = 500.0


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

    deadline = time.monotonic() + _OVERALL_DEADLINE_S
    last_status: int = -1
    last_snippet: str = "no attempt made"
    attempts = 0
    for attempt in range(3):
        if time.monotonic() >= deadline:
            raise RuntimeError(
                f"provider overall deadline hit ({_OVERALL_DEADLINE_S}s) at "
                f"{url.rsplit('/', 1)[-1]}: {last_snippet}"
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
            if resp.status_code not in _RETRYABLE_STATUS:
                if 400 <= resp.status_code < 500:
                    raise RuntimeError(
                        f"fatal provider error {resp.status_code} (no retry) at "
                        f"{url.rsplit('/', 1)[-1]}: {last_snippet}"
                    )
                raise RuntimeError(
                    f"provider error {resp.status_code} at "
                    f"{url.rsplit('/', 1)[-1]}: {last_snippet}"
                )
            if resp.status_code == 429:
                retry_after = _retry_after_s(resp)
        base = 2**attempt
        if retry_after > 0:
            base = max(base, retry_after)
        delay = base + random.uniform(0, 0.25)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(
                f"provider overall deadline hit ({_OVERALL_DEADLINE_S}s) at "
                f"{url.rsplit('/', 1)[-1]}: {last_snippet}"
            )
        time.sleep(min(delay, remaining))
    raise RuntimeError(
        f"provider failed after 3 attempts ({last_status}) at "
        f"{url.rsplit('/', 1)[-1]}: {last_snippet}"
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


# Max prior messages re-sent per turn. Bounds context for long tasks.
_HISTORY_LIMIT = 40

# Max prompt + history chars per turn. Oldest history drops first.
_INPUT_BUDGET = 100000


def _sessions_root() -> Path:
    """Sessions root; override via ``BRAIN_SESSIONS_ROOT``."""
    override = os.environ.get("BRAIN_SESSIONS_ROOT", "").strip()
    if override:
        return Path(override).expanduser()
    return Path.home() / ".config" / "opencode" / "brain-sessions"


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


def _transcript_path(task_id: str) -> Path:
    return _sessions_root() / _sanitize_task_id(task_id) / "transcript.jsonl"


#: Per-line size guard (R5): one monster line can't blow memory on read.
_LINE_CAP_CHARS = 200_000

#: Transcript compaction (Task 194): when a task transcript grows past
#: this many valid records, the next load rewrites the file as one
#: extractive digest record plus the newest records below. No model
#: call — the digest is deterministic (counts, ranges, models seen).
_COMPACT_AFTER_MESSAGES = 30
_COMPACT_KEEP_LAST = 10
_SUMMARY_MAX_CHARS = 4000
#: Byte-size backstop: compact whenever the transcript file exceeds this,
#: even when the turn count is below the threshold (bounds huge turns).
_COMPACT_FILE_BYTES = 200_000

#: Record keys preserved across load/compact cycles (traceability).
_META_KEYS = ("model", "prompt_hash", "truncated", "compacted", "models",
              "truncated_total", "compacted_count")


def _parse_turns(raw: str) -> tuple[list[dict[str, Any]], int]:
    """Parse transcript text into turns, skipping corrupt lines.

    Shared by ``load_history`` and the locked compaction path so both
    apply identical rules: blank lines ignored, monster lines over
    ``_LINE_CAP_CHARS`` dropped with count, malformed JSON skipped,
    non-turn dicts skipped, traceability keys preserved. Returns
    ``(turns, skipped)``."""
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
            turn: dict[str, Any] = {
                "role": entry["role"], "content": entry["content"]}
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
    chain = " | ".join(
        str(p.get("content", ""))[:500] for p in prior[-2:])
    digest = (
        f"[compacted {total} turns: {users} user + "
        f"{len(fresh) - users} assistant; models={sorted(models)}; "
        f"truncated_total={trunc}]"
    )
    if chain:
        digest += f" prior: {chain}"
    digest = digest[:_SUMMARY_MAX_CHARS]
    summary: dict[str, Any] = {
        "role": "assistant", "content": digest, "compacted": True,
        "compacted_count": total, "models": sorted(models),
        "truncated_total": trunc,
    }
    return [summary] + fresh[-_COMPACT_KEEP_LAST:]


def _atomic_write_turns(path: Path, turns: list[dict[str, Any]]) -> None:
    """Replace a transcript atomically: temp file + fsync + rename.

    A crash mid-write leaves either the old or the new file — never a
    half-written transcript."""
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    with tmp.open("w", encoding="utf-8") as fh:
        for turn in turns:
            fh.write(json.dumps(turn) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _compact_locked(path: Path) -> tuple[list[dict[str, Any]], int]:
    """Compact under an exclusive lock (read + build + write, one hold).

    Re-reading inside the lock closes the TOCTOU window: appends from
    other processes queue on the lock and land after the atomic
    replace, so no turn is ever lost. Returns ``(kept, skipped)``."""
    with path.open("r+", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            fh.seek(0)
            turns, skipped = _parse_turns(fh.read())
            kept = _build_compacted(turns)
            _atomic_write_turns(path, kept)
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
    print(
        f"brain-bridge: compacted {len(turns)} turns -> {len(kept)} records",
        file=sys.stderr,
    )
    return kept, skipped


def load_history(task_id: str, limit: int = _HISTORY_LIMIT) -> list[dict[str, str]]:
    """Read a task's prior turns (oldest first), capped at ``limit``.
    Missing file means a fresh task — returns []. Corrupt lines are
    skipped, never fatal; per-load stats land in ``_last_load_stats``
    (``kept``/``skipped``) for tests and debugging. Traceability keys
    (model/prompt_hash/truncated/...) survive the round trip.
    Transcripts past the count threshold — or the byte-size backstop
    for huge turns — are compacted under one exclusive lock: prior
    summaries merge into the new digest (never swallowed), the write
    is atomic, and concurrent appends queue behind the lock instead
    of being lost (see ``_build_compacted``)."""
    path = _transcript_path(task_id)
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
    if (
        len(turns) > _COMPACT_AFTER_MESSAGES
        or path.stat().st_size > _COMPACT_FILE_BYTES
    ):
        turns, lock_skipped = _compact_locked(path)
        skipped += lock_skipped
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


def append_turn(task_id: str, role: str, content: str, model: Optional[str] = None,
               prompt_hash: Optional[str] = None, truncated: int = 0) -> None:
    """Append one turn to the task transcript (creates dirs as needed).

    Traceability keys ride on every record; unset stays None/0 so
    older callers keep working unchanged."""
    path = _transcript_path(task_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "role": role, "content": content, "model": model,
        "prompt_hash": prompt_hash, "truncated": truncated,
    }
    with path.open("a", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            fh.write(json.dumps(record) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


@mcp.tool()
def brain_turn(
    user_prompt: str,
    task_id: Optional[str] = None,
    system_prompt_path: Optional[str] = None,
    include_bundle: bool = True,
) -> dict[str, Any]:
    """Send one Brain turn.

    Args:
        user_prompt: Built by the Hands from its current machine state
            (instruction + task file content + prior answers).
        task_id: When given, the task's transcript is loaded and sent
            along (chat-style history), and this turn is appended to it.
            Omit for one-off turns with no memory.
        system_prompt_path: Optional override; default is the global
            install copy of system-prompt.md.
        include_bundle: When True (default), prepend the small-file
            context bundle unless the prompt already carries its marker,
            plus the task file's working content (Goal/Notes/TODOs/AC/
            evidence/log minus the Factual Git Diff block, with a
            read_file pull path) whenever task_id resolves to a file.
            Pass False for tiny calls. The system prompt is untouched.

    Returns:
        {"status": "XML_EXTRACTED"|"REPORT", "xml_blocks": [...],
         "output": <full text>, "model": <model id>}.
        Hands rule: take ``xml_blocks`` when non-empty, else ``output``.
        Questions for the admin travel inside ``output`` — relay them to
        the Manager and feed the answer back as the next ``user_prompt``
        (with the same ``task_id`` so history continues).
    """
    import httpx  # lazy: import/tests stay offline

    system_prompt = load_system_prompt(system_prompt_path)
    effective_prompt = user_prompt
    if include_bundle and _BUNDLE_MARKER not in user_prompt:
        effective_prompt = _build_context_bundle() + "\n\n---\n\n" + user_prompt
    if include_bundle and task_id:
        try:
            attach = _build_task_attach(task_id)
            _ns = (
                f"{_TASK_FILE_MARKER}{task_id.strip()}: "
                if isinstance(task_id, str)
                else _TASK_FILE_MARKER
            )
            if attach and _ns not in user_prompt:
                effective_prompt = attach + "\n\n---\n\n" + effective_prompt
        except Exception as exc:  # never fail a turn on attach problems
            print(f"brain-bridge: task attach skipped ({exc})", file=sys.stderr)
    model = _get_brain_model()
    history = load_history(task_id) if task_id else []
    # Input budget: system + user + history chars count against
    # _INPUT_BUDGET. The FIRST history turn is grounding and survives;
    # oldest MIDDLE turns truncate first. Token estimate (chars//4) is
    # informational in the stderr log; counts (never content) are logged.
    def _hist_chars() -> int:
        return sum(len(turn["content"]) for turn in history)

    truncated_count = 0
    while (
        history
        and len(history) > 1
        and len(system_prompt) + len(effective_prompt) + _hist_chars() > _INPUT_BUDGET
    ):
        history.pop(1)
        truncated_count += 1
    budget_chars = len(system_prompt) + len(effective_prompt) + _hist_chars()
    if truncated_count:
        print(
            f"brain-bridge: truncated {truncated_count} middle history turns "
            f"(budget_chars={budget_chars} est_tokens~{budget_chars // 4})",
            file=sys.stderr,
        )
    chat: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    chat.extend({"role": t["role"], "content": t["content"]} for t in history)
    chat.append({"role": "user", "content": effective_prompt})
    body: dict[str, Any] = {
        "model": model,
        "input": chat,
        "reasoning_effort": _get_reasoning_effort(),
        "max_output_tokens": _get_max_tokens(),
    }
    # Blank-means-unset: only send temperature when explicitly set. A
    # non-blank temperature conflicts with reasoning_effort on Responses
    # models, so drop the effort key when temperature is present.
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
            del body["reasoning_effort"]
    with httpx.Client(
        timeout=httpx.Timeout(connect=10, read=120, write=30, pool=10)
    ) as client:
        resp, attempts = _post_with_retry(client, _responses_url(), body)
        output = parse_responses_text(_resp_json(resp))
    xml_blocks = extract_xml_blocks(output)
    fence_drops = list(_last_fence_drops)
    if task_id:
        prompt_hash = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
        append_turn(task_id, "user", effective_prompt, model=model,
                    prompt_hash=prompt_hash, truncated=truncated_count)
        append_turn(task_id, "assistant", output, model=model,
                    prompt_hash=prompt_hash, truncated=truncated_count)
    result: dict[str, Any] = {
        "status": "XML_EXTRACTED" if xml_blocks else "REPORT",
        "xml_blocks": xml_blocks,
        "output": output,
        "model": model,
        "truncated_count": truncated_count,
        "budget_chars": budget_chars,
        "retry_count": attempts,
    }
    if fence_drops:
        result["debug"] = {
            "fenced_blocks": len(fence_drops),
            "snippets": fence_drops,
        }
    return result


def _responses_url() -> str:
    """Responses endpoint; override via ``BRAIN_API_BASE``."""
    default = "http://127.0.0.1:8081/zen/resp"
    base = os.environ.get("BRAIN_API_BASE", default).strip() or default
    return base.rstrip("/") + "/responses"


def _get_reasoning_effort() -> str:
    """Reasoning effort; override via ``BRAIN_REASONING_EFFORT``."""
    val = os.environ.get("BRAIN_REASONING_EFFORT", "xhigh").strip() or "xhigh"
    if not re.fullmatch(r"[\w.-]{1,64}", val):
        raise ValueError(f"bad reasoning effort: {val!r}")
    return val


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
    return "\n".join(parts)


if __name__ == "__main__":
    mcp.run()
