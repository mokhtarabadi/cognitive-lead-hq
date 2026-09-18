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
        PreflightError,
        require_bare_task_id,
        validate_request as _validate_request,
    )
except ImportError:
    from preflight import (  # type: ignore[import-not-found]
        PreflightError,
        require_bare_task_id,
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

# Transport-failure learning lives in transport_learning (stdlib-only,
# zero coupling back to this module). Same guarded REQUIRED import.
try:
    from mcp_brain_bridge.transport_learning import (  # type: ignore[import-not-found]
        CorrectionMemory as _CorrectionMemory,
        TransportEscalationError,
        classify_transport_error as _classify_transport_error,
        escalation_message as _escalation_message,
        failure_signature as _failure_signature,
    )
except ImportError:
    from transport_learning import (  # type: ignore[import-not-found]
        CorrectionMemory as _CorrectionMemory,
        TransportEscalationError,
        classify_transport_error as _classify_transport_error,
        escalation_message as _escalation_message,
        failure_signature as _failure_signature,
    )

mcp = FastMCP("BrainBridge")

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
# Runs to the next closing fence or \Z so an unclosed fence still yields.
# The (?<!`) guard keeps ````quad```` fences out: without it the pattern
# would match at offset 1 inside ````xml (reviewer follow-up A1).
_XML_FENCE_RE = re.compile(r"(?<!`)```xml[^\S\n]*\n([\s\S]*?)(?:```|\Z)", re.IGNORECASE)
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

# Text extensions readable via read_file / searchable via grep_files.
_ALLOWED_READ_SUFFIXES = frozenset(
    {".md", ".txt", ".json", ".yaml", ".yml", ".toml"}
)

# Directories never descended into by grep_files.
_SKIP_DIRS = frozenset(
    {".git", "__pycache__", ".venv", "node_modules", ".pytest_cache"}
)

# Guardrails for the file-pull tools (state-machine hotfix round).
_READ_MAX_LINES = 2000        # read_file limit clamp — pulls stay pull-sized
_READ_MAX_BYTES = 2_000_000   # read_file refuses bigger files outright
_GREP_PATTERN_MAX = 500       # Brain-supplied regex length cap (ReDoS bound)
_GREP_MAX_LINE_CHARS = 4000   # overlong lines are skipped, never searched


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
_TASK_KANBAN_DIRS = ("in-progress", "qa", "backlog", "completed", "archive")
_TASK_ATTACH_CAP = 12000
_TASK_DIFF_CAP = 20000


def _task_id_ok(tid: object) -> bool:
    """Allowlist for task ids (mirrors loop_guard): letters, digits,
    underscore, hyphen; must start alnum; max 64 chars. Blocks
    traversal (../), separators (/), and glob metacharacters (*?[]).
    Uses the module-level compiled _TASK_ID_RE (shared with the
    history-path sanitizer — do NOT redefine it here)."""
    return isinstance(tid, str) and bool(_TASK_ID_RE.match(tid))


def _resolve_task_file(
    task_id: str, project_root: Optional[str] = None
) -> Path | None:
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
        for _suffix in ("-qa", "-backlog", "-in-progress", "-completed",
                        "-archive"):
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
        f"[Factual Git Diff omitted — {omitted} lines. You have no file "
        + "tools in this turn: quote the paths you need in your verdict "
        + "and the Hands will feed them as fed-context under the same "
        + "task_id.]"
    )
    if truncated:
        note += (" [diff truncated: unclosed block cut to EOF — scope past "
                 "the cut is UNVERIFIABLE, never REJECTED]")
    return "".join(parts) + note, omitted, truncated


def _build_task_attach(
    task_id: str, project_root: Optional[str] = None
) -> str:
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
            rel = path.resolve().relative_to(
                _workspace_root().resolve()).as_posix()
        except (OSError, ValueError):
            rel = path.name
        cleaned, _omitted, _truncated = _strip_task_diff(text, rel)
        if len(cleaned) > _TASK_ATTACH_CAP:
            cleaned = (
                cleaned[:_TASK_ATTACH_CAP]
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
            f"{_TASK_FILE_MARKER}{tid}: {rel}]\n"
            + "```markdown\n" + cleaned + "\n```"
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
        tail = rest[start + len(_TASK_DIFF_BEGIN):]
        end = tail.find(_TASK_DIFF_END)
        if end < 0:
            bodies.append(tail)
            break
        bodies.append(tail[:end])
        rest = tail[end + len(_TASK_DIFF_END):]
    return "\n".join(bodies)


def build_diff_attach(
    task_id: str, project_root: Optional[str] = None
) -> str:
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
            print(f"brain-bridge: diff attach skipped "
                  f"(task file unresolvable for {task_id!r})",
                  file=sys.stderr)
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
            print(f"brain-bridge: diff attach skipped "
                  f"(no Factual Git Diff block in {path.name})",
                  file=sys.stderr)
            return (
                f"[changed-hunks:{tid}: EMPTY — no Factual Git Diff "
                f"block in {path.name} yet. Stage the diff first "
                f"(stage_and_inject_diff), then re-run this turn. "
                f"Do NOT reject blind on missing hunks."
            )
        try:
            rel = path.resolve().relative_to(
                _workspace_root().resolve()).as_posix()
        except (OSError, ValueError):
            rel = path.name
        if len(diff) > _TASK_DIFF_CAP:
            diff = (
                diff[:_TASK_DIFF_CAP]
                + f"\n[...diff truncated at {_TASK_DIFF_CAP} chars — "
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
        return (
            f"[changed-hunks:{tid}: {rel}]\n"
            + "```diff\n" + diff + "\n```"
        )
    except Exception as exc:  # never fail a turn on attach problems
        print(f"brain-bridge: diff attach skipped ({exc})", file=sys.stderr)
        tid = (task_id.strip() if isinstance(task_id, str)
               else "task")
        return (
            f"[changed-hunks:{tid}: UNAVAILABLE — attach raised "
            f"({exc}). Retry the turn; if it persists, paste the "
            f"Factual Git Diff hunks inline. Do NOT reject blind "
            f"on missing hunks."
        )


def _failsafe_qa_attach(
    user_prompt: object, task_id: object,
    project_root: Optional[str] = None,
) -> str:
    """Return the diff-attach block for QA-like prompts ('' otherwise).

    Keyword gate only: fires when the prompt reads like a QA/reviewer
    turn ("qa engineer", "code reviewer", "adversarial"). Lets QA turns
    carry the changed hunks even when the caller forgot include_diff.
    Never raises (build_diff_attach never raises).
    """
    lowered = user_prompt.lower() if isinstance(user_prompt, str) else ""
    if ("qa engineer" in lowered or "code reviewer" in lowered
            or "adversarial" in lowered):
        return build_diff_attach(
            task_id.strip() if isinstance(task_id, str) else "",
            project_root=project_root)
    return ""


def _build_context_bundle() -> str:
    """Assemble the labeled small-file bundle (never raises on Absent-File).

    The per-file cap applies first; the total cap applies across files so
    five full files can never stuff 300k into one turn. Files past the
    total budget are marked skipped, never silently dropped. The truncation
    suffix length is reserved before slicing, so the appended marker can
    never push the total past the cap (off-by-suffix overflow).
    """
    root = _workspace_root()
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
                parts.append(chunk[:room - len(suffix)] + suffix)
            else:
                parts.append(header + "\n[skipped: bundle total cap]")
            total = _BUNDLE_TOTAL_CAP
            capped = True
            continue
        parts.append(chunk)
        total += len(chunk)
    if missing:
        print(
            f"brain-bridge: context bundle skipped {missing} missing files",
            file=sys.stderr,
        )
    return "\n\n".join(parts)


def _read_file_impl(path: str, offset: int = 1, limit: int = 200) -> dict[str, Any]:
    """Numbered-line slice of a workspace text file (1-indexed offset).

    The ``limit`` clamps to ``_READ_MAX_LINES`` and files over
    ``_READ_MAX_BYTES`` are refused — pulls stay pull-sized and can
    never drag a giant file into context.
    """
    if not isinstance(path, str) or not path.strip():
        raise ValueError(f"bad path: {path!r}")
    if offset < 1:
        raise ValueError(f"bad offset (1-indexed): {offset!r}")
    if limit < 1:
        raise ValueError(f"bad limit: {limit!r}")
    limit = min(limit, _READ_MAX_LINES)
    resolved = _resolve_under_root(path)
    if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
        raise ValueError(f"unsupported extension: {path!r}")
    try:
        if resolved.stat().st_size > _READ_MAX_BYTES:
            raise ValueError(
                f"file too large for read_file: {path!r} "
                f"(>{_READ_MAX_BYTES} bytes)")
    except OSError:
        pass  # stat failed — the read below raises the real error
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
    """Python-regex search over workspace text files (max 30 hits).

    Hardening: the Brain-supplied pattern caps at ``_GREP_PATTERN_MAX``
    chars (``re`` has no timeout, so length is the ReDoS bound), each hit
    line truncates at 200 chars, lines over ``_GREP_MAX_LINE_CHARS`` are
    skipped unsearched, and every candidate resolves against the root
    BEFORE it is read — a symlink escaping the workspace is skipped,
    never opened.
    """
    if not isinstance(pattern, str) or not pattern:
        raise ValueError(f"bad regex: {pattern!r}")
    if len(pattern) > _GREP_PATTERN_MAX:
        raise ValueError(
            f"regex too long ({len(pattern)} > {_GREP_PATTERN_MAX})")
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
                resolved = fpath.resolve()
                resolved.relative_to(root)
            except (OSError, ValueError):
                continue  # symlink escape — skip before any read
            try:
                text = resolved.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = resolved.relative_to(root).as_posix()
            for lineno, line in enumerate(text.splitlines(), 1):
                if len(line) > _GREP_MAX_LINE_CHARS:
                    continue
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
        lines = text[m.start():].split("\n")
        cut = len(lines)
        for i, line in enumerate(lines):
            if line.strip():
                continue
            # Blank line: peek at the next non-blank line. XML continues
            # only when it opens another tag; prose ends the block here.
            for nxt in lines[i + 1:]:
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


def extract_xml_blocks(output: str) -> list[str]:
    """Return verbatim XML control blocks in document order. Fenced code
    blocks are stripped first (XML inside backticks is documentation, not
    instructions — fence-only output means REPORT), EXCEPT explicit
    ```xml fences: the info string marks real XML, so when the unfenced
    scan finds nothing, allowlist tags inside ```xml bodies are returned
    as a fallback (Task 215: reviewer hotfix XML arrived fenced). Tag
    matching tolerates attributes, whitespace, and case (Task 238 fix
    loop). A trailing line-start opener with no close tag is surfaced
    with trailing prose cut (truncation) instead of dropped. Empty list
    means plain conversation — the Hands takes the whole output."""
    clean, _ = _strip_fences(output)
    blocks = [m.group(0) for m in _XML_RE.finditer(clean)]
    if blocks:
        return blocks
    tail = _extract_unclosed_tail(clean)
    if tail:
        return [tail]
    out: list[str] = []
    for body in _XML_FENCE_RE.finditer(output):
        content = body.group(1)
        out.extend(m.group(0) for m in _XML_RE.finditer(content))
        tail = _extract_unclosed_tail(content)
        if tail:
            out.append(tail)
    return out


#: Required phase markers per Hands block type (Task 245: semantic gate).
#: Mirrors the templates in ``prompts/fragments/09-hands_protocols.md``.
#: ``failure_report``/``hotfix`` are free-form — only non-empty bodies
#: are required. Matching is word-bound (like ``validate_plan_verdict``)
#: so prose mentions count and only genuinely phaseless blocks fail.
_HANDS_REQUIRED_PHASES = {
    "hands_discovery_task": (
        "validation_phase", "context_phase", "execution_phase",
        "summary_phase"),
    "hands_implementation_task": (
        "validation_phase", "context_phase", "execution_phase",
        "bash_phase", "documentation_phase", "summary_phase"),
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
    return bool(re.search(
        rf"<\s*{re.escape(phase)}(?:\s[^>]*)?>", body, re.IGNORECASE))


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
            problems.append(
                f"block {i}: unexpected root <{root or '?'}>")
            continue
        tag = m.group(1) if m else root
        close_m = re.search(rf"</\s*{re.escape(tag)}\s*>",
                            block, re.IGNORECASE)
        if not close_m:
            problems.append(
                f"block {i} <{root}>: missing close tag (truncated?)")
            continue
        open_m = re.search(rf"<\s*{re.escape(tag)}(?:\s[^>]*)?>",
                           block, re.IGNORECASE)
        raw_body = (block[open_m.end():close_m.start()]
                    if open_m and close_m.start() >= open_m.end()
                    else "")
        body = _COMMENT_RE.sub("", raw_body)
        if not body.strip():
            problems.append(f"block {i} <{root}>: empty body")
            continue
        for phase in _HANDS_REQUIRED_PHASES[root]:
            if not _phase_element_present(body, phase):
                problems.append(
                    f"block {i} <{root}>: missing required "
                    f"<{phase}> element")
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
    problems = [f"plan text missing {field!r} field"
                for field in _PLAN_VERDICT_FIELDS
                if not re.search(rf"\b{re.escape(field)}\b", lowered)]
    if ("cites" not in problems
            and not re.search(r"\S+\.\w+:\d+", plan_text)):
        problems.append("plan cites carry no file path with lines")
    return problems


_CLOSURE_APPROVAL_WORDS = ("approved for closure", "close task")


def validate_closure_checklist(task_text: object) -> list[str]:
    """Check task text is close-ready (pure, offline).

    Returns problem strings; empty means ready. Closeout needs a
    ``QA_PASSED`` verdict line, a ``PO_REVIEW_PENDING`` reviewer state,
    the exact approval-word quote (only "Approved for closure" or
    "Close task" count — bare "approved" never does), a non-empty
    Factual Git Diff block (content between the markers, not the empty
    placeholder), and evidence that ``extract_session_decisions`` ran
    for the close (the auto-extract rule never fires unless closeout
    verifies it). Anything missing must be fixed before the closure
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
    if not re.search(r"\bextract_session_decisions\b", task_text):
        problems.append("task text shows no extract_session_decisions run")
    diff_match = re.search(
        r"<!-- BEGIN_GIT_DIFF -->(.*?)<!-- END_GIT_DIFF -->",
        task_text, re.DOTALL)
    if diff_match is None:
        problems.append("task text missing Factual Git Diff block")
    else:
        inner = diff_match.group(1).strip()
        inner = re.sub(r"```diff|```", "", inner).strip()
        if (not inner or "will be automatically injected" in inner):
            problems.append("Factual Git Diff block is empty")
    return problems


def _get_brain_model() -> str:
    """LLM model for Brain turns; override via ``BRAIN_MODEL``."""
    default = "gpt-6-astra"
    return os.environ.get("BRAIN_MODEL", default).strip() or default


def _routing_enabled() -> bool:
    """Risk-aware routing master switch; default OFF (Task 246).

    Accepts ``1/true/yes/on`` (case-insensitive); anything else —
    including blank — keeps today's single-model behavior exactly."""
    return os.environ.get(
        "BRAIN_RISK_ROUTING_ENABLED", "").strip().lower() in (
            "1", "true", "yes", "on")


def _get_model_low() -> str:
    """Override model for T0 turns; blank means fall back to the
    current model (``BRAIN_MODEL``). Stripped, never defaulted here —
    the pure resolver below owns the fallback."""
    return os.environ.get("BRAIN_MODEL_LOW", "").strip()


def _get_model_high() -> str:
    """Override model for T1/T2 turns; blank means fall back to the
    current model (``BRAIN_MODEL``). Stripped, never defaulted here."""
    return os.environ.get("BRAIN_MODEL_HIGH", "").strip()


#: Tier sets for routing. Case-sensitive on purpose: a lowercase
#: ``t0`` is an invalid tier and must fail safe to the default model.
_ROUTED_LOW_TIERS = frozenset({"T0"})
_ROUTED_HIGH_TIERS = frozenset({"T1", "T2"})


def resolve_routed_model(enabled: bool, risk_tier: Optional[str],
                         default_model: str, model_low: str,
                         model_high: str) -> str:
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
    return (str(len(lab)).encode() + b"\x00" + lab + b"\x00"
            + str(len(data)).encode() + b"\x00" + data)


def _static_prefix_hash(system_prompt: str, bundle_text: str,
                        task_attach_text: str) -> str:
    """SHA-256 over the framed static segments, memoized (Task 247).

    The lookup key is the static input tuple itself, so a repeat
    input costs zero new static hashes — the digest is computed only
    on a miss."""
    global _STATIC_SPLIT_COMPUTES
    key = (system_prompt, bundle_text, task_attach_text)
    cached = _STATIC_SPLIT_CACHE.get(key)
    if cached is not None:
        return cached
    framed = (b"".join((
        _frame_segment("system_prompt", system_prompt),
        _frame_segment("bundle_prepend", bundle_text),
        _frame_segment("task_attach_prepend", task_attach_text),
    )))
    digest = hashlib.sha256(framed).hexdigest()
    _STATIC_SPLIT_COMPUTES += 1
    if len(_STATIC_SPLIT_CACHE) >= _STATIC_SPLIT_CACHE_MAX:
        _STATIC_SPLIT_CACHE.pop(next(iter(_STATIC_SPLIT_CACHE)))
    _STATIC_SPLIT_CACHE[key] = digest
    return digest


def build_prompt_cache_split(
        system_prompt: str, bundle_text: str, task_attach_text: str,
        user_prompt: str, paths_text: str = "", diff_text: str = "",
        failsafe_text: str = "", fed_text: str = "",
        history: Optional[list] = None) -> dict[str, str]:
    """Pure static/dynamic split descriptor (Task 247).

    Provider-neutral sidecar metadata: hashes and fixed labels only —
    never prompt text, keys, diffs, paths, or history content. The
    static half covers the stable prefix (system + bundle + task
    attach); the dynamic half covers everything that may vary per
    turn (user input, path/diff/failsafe/fed-context appends, and
    the shipped history). Takes values only — no environment reads,
    no network, no mutation of the prompt."""
    static_hash = _static_prefix_hash(
        system_prompt, bundle_text, task_attach_text)
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

# Empty-output contract (Task 232): a REPORT with blank output is a
# transport/model flake, never a verdict. The bridge MUST NOT return it
# silently — it substitutes the EMPTY_OUTPUT_RETRY hint so the caller
# knows to retry lean once instead of acting on (or stalling on) nothing.
#: Machine-readable token callers assert on. NEVER rename without a task:
#: the Hands executor and regression tests match this exact string.
EMPTY_OUTPUT_RETRY = "EMPTY_OUTPUT_RETRY"

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


def _transport_fail(message: str, attempts: int) -> RuntimeError:
    """Build a transport RuntimeError carrying its attempt count.

    WS3 seam (GitHub issue 17): the learning send path accounts
    attempts across the failed round and the corrected retry.
    Message text is unchanged — existing message matches keep passing.
    """
    err = RuntimeError(message)
    err.transport_attempts = attempts  # type: ignore[attr-defined]
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

    deadline = time.monotonic() + _OVERALL_DEADLINE_S
    last_status: int = -1
    last_snippet: str = "no attempt made"
    attempts = 0
    for attempt in range(3):
        if time.monotonic() >= deadline:
            raise _transport_fail(
                f"provider overall deadline hit ({_OVERALL_DEADLINE_S}s) at "
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
            if resp.status_code not in _RETRYABLE_STATUS:
                if 400 <= resp.status_code < 500:
                    raise _transport_fail(
                        f"fatal provider error {resp.status_code} (no retry) at "
                        f"{url.rsplit('/', 1)[-1]}: {last_snippet}",
                        attempts,
                    )
                raise _transport_fail(
                    f"provider error {resp.status_code} at "
                    f"{url.rsplit('/', 1)[-1]}: {last_snippet}",
                    attempts,
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
                f"provider overall deadline hit ({_OVERALL_DEADLINE_S}s) at "
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


def _make_client() -> Any:
    """Build the provider HTTP client (lazy httpx: imports stay offline)."""
    import httpx

    return httpx.Client(
        timeout=httpx.Timeout(connect=10, read=120, write=30, pool=10)
    )


def _send_with_learning(
    make_client: Any,
    url: str,
    body: dict[str, Any],
    *,
    task_key: Optional[str] = None,
    task_id: Optional[str] = None,
    session_id: Optional[str] = None,
    project_root: Optional[str] = None,
) -> tuple[Any, int]:
    """POST with transport-failure learning (GitHub issue 17).

    One correctable round: a 400 naming an unsupported top-level body
    key is classified, recorded to the session ledger, and retried once
    with the key dropped. The same failure class twice in one saga
    escalates via ``TransportEscalationError`` — never a verdict, never
    a silent loop. Non-correctable failures propagate untouched, and
    the returned attempt count spans the failed round plus the retry.
    """
    memory = _CorrectionMemory(task_key)
    attempts_total = 0
    while True:
        with make_client() as client:
            try:
                resp, attempts = _post_with_retry(client, url, body)
            except RuntimeError as exc:
                attempts_total += int(
                    getattr(exc, "transport_attempts", 0) or 0)
                correction = _classify_transport_error(exc, body)
                if correction is None:
                    # Repeat of an already-applied correction (provider
                    # echoing the same rejection after the key was
                    # dropped): the fix did not stick — escalate.
                    repeat_sig = _failure_signature(exc)
                    if (repeat_sig is not None
                            and memory.already_corrected(repeat_sig)):
                        message = _escalation_message(
                            task_key, repeat_sig, repeats=2)
                        if project_root is not None:
                            try:
                                _append_ledger_event(
                                    "transport_escalation",
                                    task_id=task_id,
                                    session_id=session_id,
                                    data={"task_key": task_key,
                                          "class": repeat_sig,
                                          "fingerprint": repeat_sig},
                                    project_root=project_root)
                            except Exception as ledger_exc:
                                print("brain-bridge: ledger event skipped "
                                      f"({ledger_exc})", file=sys.stderr)
                        _note_checkpoint("transport_correction_or_escalation",
                                         task_id=task_id,
                                         session_id=session_id,
                                         project_root=project_root)
                        raise TransportEscalationError(message) from exc
                    raise
                if memory.seen(correction.fingerprint):
                    message = _escalation_message(
                        task_key, correction.fingerprint, repeats=2)
                    if project_root is not None:
                        try:
                            _append_ledger_event(
                                "transport_escalation",
                                task_id=task_id, session_id=session_id,
                                data={"task_key": task_key,
                                      "class": correction.failure_class,
                                      "param": correction.param,
                                      "fingerprint":
                                          correction.fingerprint},
                                project_root=project_root)
                        except Exception as ledger_exc:
                            print("brain-bridge: ledger event skipped "
                                  f"({ledger_exc})", file=sys.stderr)
                    _note_checkpoint("transport_correction_or_escalation",
                                     task_id=task_id,
                                     session_id=session_id,
                                     project_root=project_root)
                    raise TransportEscalationError(message) from exc
                body = correction.apply(body)
                memory.record(
                    correction, task_id=task_id, session_id=session_id,
                    project_root=project_root)
                _note_checkpoint("transport_correction_or_escalation",
                                 task_id=task_id,
                                 session_id=session_id,
                                 project_root=project_root)
                print("brain-bridge: transport correction applied "
                      f"({correction.fingerprint}); retrying once with "
                      "corrected body", file=sys.stderr)
                continue
            return resp, attempts_total + attempts


# Max prior messages re-sent per turn. Bounds context for long tasks.
_HISTORY_LIMIT = 40

# Max prompt + history chars per turn. Oldest history drops first.
_INPUT_BUDGET = 100000

# Assumed model window (chars) for the utilization monitor below.
# Informational only — providers differ; the send cap stays _INPUT_BUDGET.
_MODEL_WINDOW_CHARS = 200000

# Per-session context ledger filename (one JSON object per line per turn).
_CONTEXT_LEDGER_NAME = "context_ledger.jsonl"


def _append_context_ledger(
    task_id: Optional[str],
    project_root: Optional[str],
    budget_chars: int,
    truncated_count: int,
    model: Optional[str] = None,
    risk_tier: Optional[str] = None,
    prompt_cache_split: Optional[dict] = None,
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
            "util_pct": budget_chars * 100 // _MODEL_WINDOW_CHARS,
            "truncated": truncated_count,
            "model": model,
            "risk_tier": (risk_tier or "").strip() or None,
            "prompt_cache_split": prompt_cache_split,
        }
        ledger = _sessions_root(project_root) / _CONTEXT_LEDGER_NAME
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with open(ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
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
        _sessions_root(project_root)
        / _sanitize_task_id(task_id)
        / "transcript.jsonl"
    )


def _write_transcript_path(task_id: str,
                           project_root: Optional[str] = None) -> Path:
    """Transcript path for WRITES (per-project; never legacy global)."""
    return (
        _write_sessions_root(project_root)
        / _sanitize_task_id(task_id)
        / "transcript.jsonl"
    )


def _legacy_transcript_path(task_id: str) -> Path:
    """Legacy global transcript (read fallback until migration copies it)."""
    return (
        _legacy_sessions_root()
        / _sanitize_task_id(task_id)
        / "transcript.jsonl"
    )


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


def load_history(task_id: str, limit: int = _HISTORY_LIMIT,
                  project_root: Optional[str] = None) -> list[dict[str, str]]:
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
    path = _transcript_path(task_id, project_root)
    if not path.is_file():
        # Cross-project bleed guard: the legacy global fallback
        # applies ONLY when no per-project root resolves. A project
        # with its own sessions dir but no file for this id gets a
        # fresh history — never another project's turns.
        legacy = _legacy_transcript_path(task_id)
        if (_sessions_root(project_root) == _legacy_sessions_root()
                and legacy.is_file()):
            print("brain-bridge: reading legacy global session "
                  f"({task_id}); migrate it under tasks/.sessions/",
                  file=sys.stderr)
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
                prompt_hash: Optional[str] = None, truncated: int = 0,
                project_root: Optional[str] = None) -> None:
    """Append one turn to the task transcript (creates dirs as needed).

    Traceability keys ride on every record; unset stays None/0 so
    older callers keep working unchanged. Writes always go to the
    per-project path, never to the legacy global dir."""
    path = _write_transcript_path(task_id, project_root)
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


def _fed_context_path(task_id: str,
                        project_root: Optional[str] = None) -> Path:
    """Pinned fed-context file for a task (raises ValueError on bad id)."""
    return (
        _sessions_root(project_root)
        / _sanitize_task_id(task_id)
        / _FED_CONTEXT_FILE
    )


def _legacy_fed_context_path(task_id: str) -> Path:
    """Legacy global fed-context file (read fallback until migrated)."""
    return (
        _legacy_sessions_root()
        / _sanitize_task_id(task_id)
        / _FED_CONTEXT_FILE
    )


def _write_fed_context_path(task_id: str,
                              project_root: Optional[str] = None) -> Path:
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


def save_fed_context(task_id: str, content: str,
                     project_root: Optional[str] = None) -> None:
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
            print(f"brain-bridge: fed-context clear skipped ({exc})",
                  file=sys.stderr)
        return
    if len(content) > _FED_CONTEXT_CAP:
        content = (content[:_FED_CONTEXT_CAP]
                   + f"\n[...fed context truncated at {_FED_CONTEXT_CAP} "
                   + "chars]")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    try:
        with tmp.open("w", encoding="utf-8") as fh:
            fh.write(content + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except OSError as exc:
        print(f"brain-bridge: fed-context save skipped ({exc})",
              file=sys.stderr)


def load_fed_context(task_id: str,
                     project_root: Optional[str] = None) -> str:
    """Read pinned fed context ('' when none; never raises).

    Falls back to the legacy global file ONLY when no per-project
    root resolves; a project with its own sessions dir but no pin
    gets '' — never another project's pin. New pins are always
    written per-project."""
    try:
        return _fed_context_path(task_id, project_root).read_text(
            encoding="utf-8", errors="replace").strip()
    except (OSError, ValueError):
        pass
    if _sessions_root(project_root) != _legacy_sessions_root():
        return ""
    try:
        return _legacy_fed_context_path(task_id).read_text(
            encoding="utf-8", errors="replace").strip()
    except (OSError, ValueError):
        return ""


#: Per-file cap for path-injected context (chars). Truncated with a note.
_CTX_PATHS_PER_FILE = 20000

#: Total cap across all path-injected files per turn (chars). Files past
#: the total are skipped with an explicit skipped note — stacked files
#: must never overflow the turn budget on their own.
_CTX_PATHS_TOTAL = 40000


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
                    f"project_root is not path-like: {type(project_root)!r}")
            pr = Path(project_root).expanduser()
            if pr.is_dir():
                return pr.resolve()
        except (OSError, TypeError):
            pass
    return _workspace_root()


def build_paths_attach(
    paths: object, project_root: Optional[str] = None
) -> str:
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
        try:
            resolved = _resolve_under_root(rel, root=base)
        except ValueError:
            blocks.append(f"[unavailable: {rel.strip()} — outside workspace]")
            continue
        if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
            blocks.append(
                f"[unavailable: {rel.strip()} — unsupported extension]")
            continue
        try:
            if resolved.stat().st_size > _READ_MAX_BYTES:
                blocks.append(
                    f"[unavailable: {rel.strip()} — file too large]")
                continue
            text = resolved.read_text(encoding="utf-8", errors="replace")
        except OSError:
            blocks.append(f"[unavailable: {rel.strip()} — unreadable]")
            continue
        if not text.strip():
            blocks.append(f"[unavailable: {rel.strip()} — empty file]")
            continue
        if len(text) > _CTX_PATHS_PER_FILE:
            text = (text[:_CTX_PATHS_PER_FILE]
                    + f"\n[...truncated at {_CTX_PATHS_PER_FILE} chars]")
        if used + len(text) > _CTX_PATHS_TOTAL:
            blocks.append(
                f"[skipped: {rel.strip()} — total budget "
                f"{_CTX_PATHS_TOTAL} chars reached]")
            continue
        used += len(text)
        blocks.append(f"[path-injected: {rel.strip()}]\n{text}")
    if not blocks:
        return ""
    return "\n\n---\n\n".join(blocks)


@mcp.tool()
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
        _ledger_checkpoint(
            scope, name, task_id=task_id, project_root=project_root)
    except Exception as exc:  # never fail a turn on ledger problems
        print(f"brain-bridge: checkpoint skipped ({exc})", file=sys.stderr)


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
            or "215plan". When given, the task's transcript is loaded
            and sent along (chat-style history), and this turn is
            appended to it. History is keyed by this exact string, so
            EVERY turn for one task (plan, implement, QA, review) MUST
            pass the identical number: a different id starts a
            separate, empty history and the Brain loses all prior
            context. Non-numeric input is rejected before anything
            runs. Omit for one-off turns with no memory.
        system_prompt_path: Optional override; default is the global
            install copy of system-prompt.md.
        include_bundle: When True (default), prepend the small-file
            context bundle unless the prompt already carries its marker,
            plus the task file's working content (Goal/Notes/TODOs/AC/
            evidence/log minus the Factual Git Diff block, with a
            read_file pull path) whenever task_id resolves to a file.
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
        session_id: Optional taskless saga key (e.g. "cando-828") —
            mutually exclusive with task_id. Pass exactly one of the two
            on memory-bearing turns; omit both for one-off turns with no
            memory. The session transcript continues under this key the
            same way a task transcript continues under task_id.
        stage: Optional turn stage, one of plan / implement / qa /
            review / closure. Unknown stages are rejected so a typo can
            never run as an unscoped turn.
        kanban_path: Optional task-file path under
            ``<project_root>/tasks/`` (e.g. "tasks/qa/257-x.md").
            Paths escaping the tasks/ lanes are rejected.
        required_tools: Optional list of tool names the turn's stage
            requires (e.g. ["question"]). Missing-required tools gate
            the turn before transport (see capability).

    Returns:
        {"status": "XML_EXTRACTED"|"REPORT", "xml_blocks": [...],
         "output": <full text>, "model": <model id>}.
        Hands rule: take ``xml_blocks`` when non-empty, else ``output``.
        Questions for the admin travel inside ``output`` — relay them to
        the Manager and feed the answer back as the next ``user_prompt``
        (with the same ``task_id`` so history continues).
    """
    # Request preflight FIRST (GitHub issue 18): local validation before
    # any load, attach, import, or model call. An explicit project_root
    # without tasks/ raises here instead of silently substituting the
    # workspace root; suffixed task_ids are rejected; task_id and
    # session_id are mutually exclusive (exactly one binds history,
    # neither means a one-off turn). The resolved root feeds every
    # downstream resolver so attaches and history share one root.
    _pre = _validate_request(
        project_root=project_root, task_id=task_id, session_id=session_id,
        kanban_path=kanban_path, stage=stage,
        include_bundle=include_bundle, include_diff=include_diff,
        required_tools=required_tools)
    task_id = _pre.task_id
    session_id = _pre.session_id
    project_root = (str(_pre.project_root)
                    if _pre.project_root is not None else None)
    history_key = _pre.history_key
    _note_checkpoint("request_accepted", task_id=task_id,
                     session_id=session_id, project_root=project_root)
    _note_checkpoint("preflight_completed", task_id=task_id,
                     session_id=session_id, project_root=project_root)

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
        stage=stage)
    print(
        "capability-manifest: task=%s session=%s stage=%s %s"
        % (task_id, session_id, stage,
           " ".join(f"{k}={v}" for k, v in sorted(manifest.items()))
           or "(no tools referenced)"),
        file=sys.stderr)
    try:
        _append_ledger_event(
            "capability_manifest", task_id=task_id, session_id=session_id,
            data={"stage": stage, "manifest": manifest},
            project_root=project_root)
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
            "truncated_count": 0,
            "budget_chars": 0,
            "retry_count": 0,
            "prompt_cache_split": None,
        }
    _note_checkpoint("capability_completed", task_id=task_id,
                     session_id=session_id, project_root=project_root)

    system_prompt = load_system_prompt(system_prompt_path)
    effective_prompt = user_prompt
    # Segment captures for the prompt-cache split descriptor (Task 247):
    # static pieces are hashed for stability, dynamic pieces per turn.
    bundle_text = ""
    task_attach_text = ""
    paths_text = ""
    diff_append_text = ""
    failsafe_text = ""
    fed_text = ""
    if include_bundle and _BUNDLE_MARKER not in user_prompt:
        bundle_text = _build_context_bundle()
        effective_prompt = bundle_text + "\n\n---\n\n" + user_prompt
    if include_bundle and task_id:
        try:
            attach = _build_task_attach(task_id, project_root=project_root)
            _ns = (
                f"{_TASK_FILE_MARKER}{task_id.strip()}: "
                if isinstance(task_id, str)
                else _TASK_FILE_MARKER
            )
            if attach and _ns not in user_prompt:
                task_attach_text = attach
                effective_prompt = attach + "\n\n---\n\n" + effective_prompt
        except Exception as exc:  # never fail a turn on attach problems
            print(f"brain-bridge: task attach skipped ({exc})", file=sys.stderr)
    if context_paths:
        # File-path injection: the server reads big artifacts (context,
        # tree, signature reports) from disk instead of the Hands pasting
        # them. Counts toward the input budget below like any prompt text.
        try:
            paths_attach = build_paths_attach(
                context_paths, project_root=project_root)
            if paths_attach:
                paths_text = paths_attach
                effective_prompt = (
                    effective_prompt + "\n\n---\n\n" + paths_attach)
        except Exception as exc:  # never fail a turn on attach problems
            print(f"brain-bridge: paths attach skipped ({exc})",
                  file=sys.stderr)
    # Explicit flag stands alone: a lean turn (include_bundle=False,
    # the documented EMPTY_OUTPUT_RETRY shape) with include_diff=True
    # MUST still carry the hunks — gating the diff on the bundle
    # silently dropped QA diffs on every lean retry.
    if include_diff and task_id:
        try:
            dattach = build_diff_attach(
                task_id.strip() if isinstance(task_id, str) else "",
                project_root=project_root)
            if dattach:
                diff_append_text = dattach
                effective_prompt = effective_prompt + "\n\n---\n\n" + dattach
            else:
                print("brain-bridge: include_diff=True but no hunks "
                      "attached (see reason above)", file=sys.stderr)
        except Exception as exc:  # never fail a turn on attach problems
            print(f"brain-bridge: diff attach skipped ({exc})", file=sys.stderr)
    if not include_diff and task_id:
        # Fail-safe: QA/reviewer-like prompts carry the changed hunks even
        # when the caller forgot the flag — a silent drop would let the
        # Brain judge a summary instead of the changes. Keyword gate only;
        # normal turns are untouched when the flag is False.
        try:
            dattach = _failsafe_qa_attach(
                user_prompt, task_id, project_root=project_root)
            if dattach:
                print("brain-bridge: QA turn without include_diff, "
                      "auto-attaching diff", file=sys.stderr)
                failsafe_text = dattach
                effective_prompt = (effective_prompt + "\n\n---\n\n"
                                    + dattach)
        except Exception as exc:  # never fail a turn on attach problems
            print(f"brain-bridge: diff attach skipped ({exc})",
                  file=sys.stderr)
    model = resolve_routed_model(
        _routing_enabled(), risk_tier, _get_brain_model(),
        _get_model_low(), _get_model_high())
    if history_key:
        # Sessions-root visibility: one debug line per turn so a
        # misrouted project is observable in stderr, never silent.
        _scope = "task" if task_id is not None else "session"
        print(f"brain-bridge: sessions root {_sessions_root(project_root)} "
              f"({_scope} {history_key})", file=sys.stderr)
    history = (load_history(history_key, project_root=project_root)
               if history_key else [])
    if history_key:
        # Discovery-fed planning: a [fed-context] block in this prompt is
        # pinned to the session, then the pin (not just this turn's copy)
        # rides every later turn until session end. The pin lives outside
        # the transcript, so compaction and the middle drop below can never
        # silently remove it; it still counts toward the input budget.
        try:
            fed = extract_fed_context(effective_prompt)
            if fed:
                save_fed_context(history_key, fed, project_root=project_root)
            pinned = load_fed_context(history_key, project_root=project_root)
            if pinned and "[pinned-fed-context]" not in effective_prompt:
                fed_text = pinned
                effective_prompt = (
                    "[pinned-fed-context]\n" + pinned
                    + "\n[/pinned-fed-context]\n\n---\n\n"
                    + effective_prompt)
        except Exception as exc:  # never fail a turn on pin problems
            print(f"brain-bridge: fed-context skipped ({exc})",
                  file=sys.stderr)
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
    util_pct = budget_chars * 100 // _MODEL_WINDOW_CHARS
    # Sidecar only: the split descriptor never touches wire bytes —
    # effective_prompt, chat payload, and prompt_hash stay identical.
    cache_split = build_prompt_cache_split(
        system_prompt, bundle_text, task_attach_text, user_prompt,
        paths_text=paths_text, diff_text=diff_append_text,
        failsafe_text=failsafe_text, fed_text=fed_text,
        history=history)
    _append_context_ledger(history_key, project_root, budget_chars,
                           truncated_count, model=model,
                           risk_tier=risk_tier,
                           prompt_cache_split=cache_split)
    if budget_chars > _PROMPT_WARN_CHARS:
        print(
            f"brain-bridge: prompt is large (budget_chars={budget_chars} "
            f"est_tokens~{budget_chars // 4} util~{util_pct}% of "
            f"{_MODEL_WINDOW_CHARS}ch window); oversized prompts have returned "
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
    chat: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    chat.extend({"role": t["role"], "content": t["content"]} for t in history)
    chat.append({"role": "user", "content": effective_prompt})
    body: dict[str, Any] = {
        "model": model,
        "input": chat,
        # Responses API shape: effort nests under reasoning (flat
        # reasoning_effort is rejected by strict providers, e.g.
        # OpenAI/OpenRouter 400 unsupported_parameter).
        "reasoning": {"effort": _get_reasoning_effort()},
        "max_output_tokens": _get_max_tokens(),
    }
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
    _note_checkpoint("transport_started", task_id=task_id,
                     session_id=session_id, project_root=project_root)
    resp, attempts = _send_with_learning(
        _make_client, _responses_url(), body,
        task_key=history_key, task_id=task_id, session_id=session_id,
        project_root=project_root)
    output = parse_responses_text(_resp_json(resp))
    _note_checkpoint("response_parsed", task_id=task_id,
                     session_id=session_id, project_root=project_root)
    xml_blocks = extract_xml_blocks(output)
    if xml_blocks:
        # Semantic gate (Task 245): syntactically valid but contract-
        # incomplete XML must triage as REPORT with explicit reasons —
        # the Hands executes only whole contracts, never fragments.
        sem_problems = validate_hands_xml_blocks(xml_blocks)
        if sem_problems:
            print("brain-bridge: xml failed semantic validation "
                  f"({len(sem_problems)} problems)", file=sys.stderr)
            output = ("[xml-semantic-reject]\n"
                      + "\n".join(f"- {p}" for p in sem_problems)
                      + "\n[/xml-semantic-reject]\n" + output)
            xml_blocks = []
    if not xml_blocks and not output.strip():
        # Empty-output guard (Task 232): never return a silent blank
        # REPORT. Substitute the retry hint; status stays REPORT so old
        # callers keep working. The transcript below records the hint,
        # not a verdict.
        output = _empty_output_hint(
            task_id, _task_state_note(history_key, project_root))
    fence_drops = list(_last_fence_drops)
    if history_key:
        prompt_hash = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
        append_turn(history_key, "user", effective_prompt, model=model,
                    prompt_hash=prompt_hash, truncated=truncated_count,
                    project_root=project_root)
        append_turn(history_key, "assistant", output, model=model,
                    prompt_hash=prompt_hash, truncated=truncated_count,
                    project_root=project_root)
    result: dict[str, Any] = {
        "status": "XML_EXTRACTED" if xml_blocks else "REPORT",
        "xml_blocks": xml_blocks,
        "output": output,
        "model": model,
        "truncated_count": truncated_count,
        "budget_chars": budget_chars,
        "retry_count": attempts,
        "prompt_cache_split": cache_split,
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


def _task_state_note(
    task_id: Optional[str], project_root: Optional[str] = None
) -> str:
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
            rel = path.resolve().relative_to(
                _workspace_root().resolve()).as_posix()
        except (OSError, ValueError):
            rel = path.name
        text = path.read_text(encoding="utf-8", errors="replace")
        status = "unknown"
        m = re.search(r"^\*\*Status:\*\*\s*(.+?)\s*$", text, re.M)
        if m:
            status = m.group(1)[:32]
        diff = extract_task_diff(text)
        dh = (hashlib.sha256(diff.encode("utf-8")).hexdigest()[:8]
              if diff.strip() else "no-diff")
        return f"{rel} | status={status} | diff={dh}"
    except Exception:
        return "unknown"


def _empty_output_hint(task_id: Optional[str] = None,
                       state: Optional[str] = None) -> str:
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
        "If the full-context call is still empty, escalate to the Manager."
        + note
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
    return "\n".join(parts)


if __name__ == "__main__":
    mcp.run()
