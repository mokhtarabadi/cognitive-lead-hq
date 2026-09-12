#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.0,<2.0",
#     "httpx>=0.28",
# ]
# ///

"""Manager-decision capture MCP server (Task 168).

Learning half of the persona pipeline: per-session manager trade-offs and
rulings are extracted (httpx Responses-API call, default local Spark
model), redacted, and
persisted append-only into the decision store (per-project
`.opencode/decisions/`, overridable via DECISION_REPO_PATH).
Stored decisions feed `query_manager_decisions` (consultation) and
`propose_profile_evolution` (gated sample updates — the script drafts, a
human approves; this server never rewrites the sample itself).

Transport: stdio FastMCP. The extraction model is called over the
OpenAI Responses API (``{api_base}/responses``) via ``httpx`` — plain
HTTPS POST, no SDK needed. ``httpx`` is lazy so import and unit tests
never need network or credentials.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from redactor import sanitize_text, verify_clean

# Shared env loader lives in mcp-common (Task 170). Prefer the installed
# package; fall back to the sibling source tree so plain `uv run <path>`
# and direct test imports keep working without a workspace install.
# NOTE: file.parent = server dir, so parent.parent = install root (repo root
# for repo installs, ~/.config/opencode for global installs). Correct.
try:
    from mcp_common.env import load_env_files as _shared_load_env_files
except ImportError:  # pragma: no cover - workspace/normal path first
    _COMMON_SRC = Path(__file__).resolve().parent.parent / "mcp-common" / "src"
    if _COMMON_SRC.is_dir():
        sys.path.insert(0, str(_COMMON_SRC))
    from mcp_common.env import load_env_files as _shared_load_env_files


def _load_env_files(server_dir: Optional[Path] = None) -> Optional[str]:
    """Load `.env` files via the shared loader (thin wrapper, stable entry point).
    Empty env values count as unset, so blank `{env:…}` injections never
    shadow file values."""
    return _shared_load_env_files(
        server_dir if server_dir is not None else Path(__file__).resolve().parent
    )


_loaded_from = _load_env_files()
if _loaded_from is not None:
    print(f"decision-server: loaded env from {_loaded_from}", file=sys.stderr)

# Install root: repo root for repo installs, ~/.config/opencode globally.
INSTALL_ROOT = Path(__file__).resolve().parent.parent


def _repo_root() -> Path:
    """Resolve (creating) the decision store — project-aware.

    Order: explicit ``DECISION_REPO_PATH`` env, then
    ``<cwd>/.opencode/decisions`` (each project keeps its OWN manager
    notes — opencode launches servers with the project as cwd), then
    ``<install-root>/.opencode/decisions`` as fallback. Creation failures
    (e.g. read-only cwd) fall through to the next candidate.
    """
    explicit = os.environ.get("DECISION_REPO_PATH", "").strip()
    if explicit:
        root = Path(explicit)
        root.mkdir(parents=True, exist_ok=True)
        return root
    for base in (Path.cwd(), INSTALL_ROOT):
        candidate = base / ".opencode" / "decisions"
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            continue
    raise RuntimeError("cannot create a decision store: no writable location found")

mcp = FastMCP("ManagerDecisions")

# Free-text fields that must pass verify_clean before any write.
_SCRUB_FIELDS = ("original", "english_translation", "summary", "rationale", "tradeoffs")

#: Built-in extraction model when DECISION_MODEL is not set.
DEFAULT_DECISION_MODEL = "gpt-6-astra"


def _get_decision_temperature() -> float:
    """Extraction sampling temperature; override via ``DECISION_TEMPERATURE``.

    Defaults to 1.0 (matches the house temperature policy; the old hardcoded
    0.2 was a Gemini-era leftover). Out-of-range or unparsable values clamp
    to 1.0 instead of crashing a live turn.
    """
    try:
        value = float(os.environ.get("DECISION_TEMPERATURE", "1.0") or 1.0)
    except ValueError:
        return 1.0
    return value if 0.0 <= value <= 2.0 else 1.0


def _get_decision_model() -> str:
    """Extraction LLM: ``DECISION_MODEL``, else the built-in default.

    No fallback to ``PERSONA_MODEL`` exists on purpose: a stale persona
    model value once hijacked extraction calls and caused 401s. Blank
    DECISION_MODEL means unset — the default wins.
    """
    explicit = os.environ.get("DECISION_MODEL", "").strip()
    if explicit:
        return explicit
    return DEFAULT_DECISION_MODEL


def _get_decision_effort() -> str:
    """Reasoning effort for extraction; override via ``BRAIN_REASONING_EFFORT``."""
    val = os.environ.get("BRAIN_REASONING_EFFORT", "xhigh").strip() or "xhigh"
    if not re.fullmatch(r"[\w.-]{1,64}", val):
        raise ValueError(f"bad reasoning effort: {val!r}")
    return val


def _get_api_key() -> str:
    """Provider key. Fail-closed: an empty key cannot authenticate, so
    raise instead of sending a bare ``Bearer `` header."""
    key = os.environ.get("BRAIN_API_KEY", "").strip()
    if not key:
        raise RuntimeError("BRAIN_API_KEY is empty; set it in .env")
    return key


# Retry policy for provider calls: 3 attempts, exponential backoff.
# (Duplicated from the brain bridge on purpose — each server dir ships
# self-contained to the global install.)
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


def _responses_text(data: dict) -> str:
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


def _utc_today() -> str:
    """UTC date as YYYYMMDD for decision ids."""
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def _next_decision_id(repo: Path) -> str:
    """Next id of the form DEC-YYYYMMDD-NNN (daily zero-padded sequence)."""
    prefix = f"DEC-{_utc_today()}-"
    taken = sorted(
        p.name for p in (repo / "decisions").rglob(f"{prefix}*.json")
    ) if (repo / "decisions").exists() else []
    seq = 0
    for name in taken:
        match = re.fullmatch(r"DEC-\d{8}-(\d{3})\.json", name)
        if match:
            seq = max(seq, int(match.group(1)))
    return f"{prefix}{seq + 1:03d}"


def _scrub_free_text(decision: dict[str, Any]) -> dict[str, Any]:
    """Return a copy with every free-text field sanitized + verified.

    Raises:
        ValueError: If any field still holds sensitive patterns after
            sanitizing (write must not proceed).
    """
    scrubbed = json.loads(json.dumps(decision))  # Deep copy via round-trip.
    quote = scrubbed.setdefault("verbatim_quote", {})
    extracted = scrubbed.setdefault("extracted_decision", {})
    targets = [quote.get("original", ""), quote.get("english_translation", ""),
               extracted.get("summary", ""), extracted.get("rationale", ""),
               extracted.get("tradeoffs", "")]
    cleaned = [sanitize_text(t) for t in targets]
    if not all(verify_clean(t) for t in cleaned):
        raise ValueError("redaction failed: sensitive patterns remain after sanitize_text")
    (quote["original"], quote["english_translation"], extracted["summary"],
     extracted["rationale"], extracted["tradeoffs"]) = cleaned
    # Alternatives list items are manager-authored too — scrub each.
    extracted["alternatives"] = [
        sanitize_text(a) for a in extracted.get("alternatives", [])
    ]
    if not all(verify_clean(a) for a in extracted["alternatives"]):
        raise ValueError("redaction failed in alternatives list")
    scrubbed["redaction_verified"] = True
    return scrubbed


def _validate_against_schema(decision: dict[str, Any]) -> list[str]:
    """Structural validation mirroring scripts/validate_decisions.py.

    Kept import-light (no jsonschema dep): required fields, id shape,
    ISO timestamp, non-empty verbatim quote, known category, and the
    redaction_verified flag. Returns violation strings (empty = valid).
    """
    issues: list[str] = []
    for field in ("decision_id", "timestamp", "project_name", "verbatim_quote",
                  "extracted_decision", "redaction_verified"):
        if field not in decision:
            issues.append(f"missing required field: {field}")
    if issues:
        return issues
    if not re.fullmatch(r"DEC-\d{8}-\d{3}", str(decision["decision_id"])):
        issues.append(f"bad decision_id: {decision['decision_id']!r}")
    try:
        datetime.fromisoformat(str(decision["timestamp"]).replace("Z", "+00:00"))
    except ValueError:
        issues.append(f"bad timestamp: {decision['timestamp']!r}")
    quote = decision["verbatim_quote"]
    if not isinstance(quote, dict) or not all(
        isinstance(quote.get(k), str) and quote[k].strip()
        for k in ("original", "english_translation")
    ):
        issues.append("verbatim_quote.original/english_translation must be non-empty strings")
    extracted = decision["extracted_decision"]
    valid_categories = {"architecture", "process", "scope", "quality-gate",
                        "tooling", "release", "other"}
    if not isinstance(extracted, dict) or extracted.get("category") not in valid_categories:
        issues.append(f"bad category: {extracted.get('category') if isinstance(extracted, dict) else extracted!r}")
    if decision["redaction_verified"] is not True:
        issues.append("redaction_verified must be true")
    return issues


def _index_path(repo: Path) -> Path:
    """Markdown index listing every stored decision (regenerated on write)."""
    return repo / "decisions" / "INDEX.md"


def _rewrite_index(repo: Path) -> int:
    """Regenerate INDEX.md from all stored records; return record count."""
    rows = []
    for path in sorted((repo / "decisions").rglob("DEC-*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        extracted = record.get("extracted_decision", {})
        rows.append(
            f"| {record.get('decision_id')} | {extracted.get('category', '?')} | "
            f"{extracted.get('summary', '')[:100]} | `{path.relative_to(repo).as_posix()}` |"
        )
    _index_path(repo).write_text(
        "# Manager Decisions Index\n\n"
        "> Auto-generated on every `record_manager_decision` call. Do not edit directly.\n\n"
        "| ID | Category | Summary | Path |\n|---|---|---|---|\n"
        + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    return len(rows)


# --- Task 191: deterministic extraction ---------------------------------------

#: In-memory LRU cache for extraction results (Task 191).
_EXTRACT_CACHE_MAX = 64
_EXTRACT_CACHE: dict[str, list[dict[str, Any]]] = {}
#: Serializes cache lookup/store so concurrent extracts never corrupt it.
_CACHE_LOCK = threading.Lock()
#: Total extraction cache hits since import (every hit is logged to stderr).
_last_cache_hits = 0
#: Total auto-repair attempts since import (at most one per extract call).
_REPAIR_COUNT = 0

_VALID_CATEGORIES = {
    "architecture", "process", "scope", "quality-gate",
    "tooling", "release", "other",
}
_REQUIRED_DECISION_FIELDS = (
    "summary", "category", "rationale", "alternatives", "tradeoffs",
)

_BULLET_RE = re.compile(r"^\s*(?:[-*\u2022]|\d+[.)])\s+(.+?)\s*$")


def _extract_cache_key(
    transcript_bytes: bytes, model: str, effective_temp: float
) -> str:
    """Cache key: sha256(transcript bytes + model id + effective temp).

    The temp is part of the key because an explicit BRAIN_TEMPERATURE
    override changes the model's output distribution — serving a
    temp-0 cached result to a temp-0.7 call would be wrong.
    Fields join with NUL bytes so concatenations can't collide (R2).
    """
    digest = hashlib.sha256()
    digest.update(transcript_bytes)
    digest.update(b"\0")
    digest.update(model.encode("utf-8"))
    digest.update(b"\0")
    digest.update(repr(float(effective_temp)).encode("utf-8"))
    return digest.hexdigest()


def _validate_extracted_candidates(
    candidates: list[dict[str, Any]], transcript_text: Optional[str] = None
) -> None:
    """Strict schema check on extracted candidates (Task 191 + N1).

    Extends the original per-item dict check: verbatim_quote needs
    non-empty original/english_translation strings; extracted_decision
    needs summary/category/rationale/alternatives/tradeoffs with a known
    category. Raises RuntimeError naming the offender index.

    When transcript_text is given, two extra guards apply: the
    verbatim original must be an exact substring of the transcript
    (verbatim means verbatim — paraphrases belong in summary, never in
    the quote), and any extra key whose name contains "evidence" has
    non-verbatim values STRIPPED (with an stderr log) instead of
    failing the whole candidate — a hallucinated link must never
    persist, but one bad link must not nuke a valid ruling.
    """
    for idx, item in enumerate(candidates):
        quote = item.get("verbatim_quote") if isinstance(item, dict) else None
        if not isinstance(quote, dict):
            raise RuntimeError(
                f"decision candidate {idx} missing required dict fields "
                f"verbatim_quote/extracted_decision: {str(item)[:300]}"
            )
        for key in ("original", "english_translation"):
            value = quote.get(key)
            if not isinstance(value, str) or not value.strip():
                raise RuntimeError(
                    f"decision candidate {idx} has bad verbatim_quote.{key} "
                    f"(non-empty string required): {str(item)[:300]}"
                )
        extracted = item.get("extracted_decision")
        if not isinstance(extracted, dict):
            raise RuntimeError(
                f"decision candidate {idx} missing required dict fields "
                f"verbatim_quote/extracted_decision: {str(item)[:300]}"
            )
        for key in _REQUIRED_DECISION_FIELDS:
            if key not in extracted:
                raise RuntimeError(
                    f"decision candidate {idx} missing extracted_decision.{key}: "
                    f"{str(item)[:300]}"
                )
        if not isinstance(extracted["summary"], str) or not extracted["summary"].strip():
            raise RuntimeError(
                f"decision candidate {idx} has bad summary "
                f"(non-empty string required): {str(item)[:300]}"
            )
        if extracted["category"] not in _VALID_CATEGORIES:
            raise RuntimeError(
                f"decision candidate {idx} has bad category "
                f"{extracted['category']!r}: {str(item)[:300]}"
            )
        if not isinstance(extracted["rationale"], str) or not extracted["rationale"].strip():
            raise RuntimeError(
                f"decision candidate {idx} has bad rationale "
                f"(non-empty string required): {str(item)[:300]}"
            )
        if not isinstance(extracted["alternatives"], list):
            raise RuntimeError(
                f"decision candidate {idx} has bad alternatives "
                f"(list required): {str(item)[:300]}"
            )
        if not isinstance(extracted["tradeoffs"], str):
            raise RuntimeError(
                f"decision candidate {idx} has bad tradeoffs "
                f"(string required): {str(item)[:300]}"
            )
        if transcript_text is not None:
            if quote["original"] not in transcript_text:
                raise RuntimeError(
                    f"decision candidate {idx} verbatim original is not an "
                    f"exact substring of the transcript (quotes must be "
                    f"verbatim): {quote['original'][:200]}"
                )
            for extra_key in [
                key for key in item
                if "evidence" in key.lower() and key not in ("verbatim_quote",)
            ]:
                value = item[extra_key]
                raw = value if isinstance(value, list) else [value]
                kept = [
                    text for text in raw
                    if isinstance(text, str) and text in transcript_text
                ]
                if len(kept) < len(raw) or not kept:
                    print(
                        f"decision-server: stripped {len(raw) - len(kept)} "
                        f"non-verbatim '{extra_key}' link(s) from candidate "
                        f"{idx}",
                        file=sys.stderr,
                    )
                if not kept:
                    del item[extra_key]
                elif not isinstance(value, list):
                    item[extra_key] = kept[0]
                else:
                    item[extra_key] = kept


def _extract_largest_json(text: str) -> Any:
    """Return the largest JSON list/dict embedded in text.

    Balanced-bracket scan that respects JSON strings/escapes; every
    balanced span is tried with json.loads and the longest parse wins.
    Raises ValueError when nothing parses (caller falls back or raises).
    """
    best: Any = None
    best_len = -1
    ties = 0
    n = len(text)
    for start in range(n):
        if text[start] not in "[{":
            continue
        depth = 0
        in_str = False
        escaped = False
        for end in range(start, n):
            char = text[end]
            if in_str:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_str = False
                continue
            if char == '"':
                in_str = True
            elif char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
                if depth == 0:
                    span = text[start : end + 1]
                    try:
                        value = json.loads(span)
                    except (json.JSONDecodeError, ValueError):
                        pass
                    else:
                        if isinstance(value, (list, dict)):
                            if len(span) > best_len:
                                best, best_len = value, len(span)
                            elif len(span) == best_len and best is not None:
                                # Tie: keep the FIRST valid largest span
                                # (deterministic) and log the ambiguity.
                                ties += 1
                    break
                if depth < 0:
                    break
    if ties:
        print(
            f"decision-server: largest-JSON tie ({ties} equal spans); "
            f"kept the first valid largest",
            file=sys.stderr,
        )
    if best is None:
        raise ValueError("no JSON list/dict span found in model text")
    return best


def _regex_fallback_candidates(
    snippet: str, transcript_text: str
) -> list[dict[str, Any]]:
    """Salvage explicit bullet/numbered lines (Task 191).

    NEVER invents content: a line is kept only when its stripped text is
    an exact substring of the transcript. Both sides are NFC-normalized
    first so visually identical text in different Unicode forms still
    matches. Returns [] when nothing salvages (the caller then raises
    loudly).
    """
    norm_transcript = unicodedata.normalize("NFC", transcript_text)
    salvaged: list[dict[str, Any]] = []
    for line in snippet.splitlines():
        match = _BULLET_RE.match(line)
        if not match:
            continue
        content = unicodedata.normalize("NFC", match.group(1)).strip()
        if not content or content not in norm_transcript:
            continue
        salvaged.append(
            {
                "verbatim_quote": {
                    "original": content,
                    "english_translation": content,
                },
                "extracted_decision": {
                    "summary": content[:200],
                    "category": "other",
                    "rationale": "salvaged via regex fallback",
                    "alternatives": [],
                    "tradeoffs": "",
                },
            }
        )
    return salvaged


def _parse_model_text(text: str, transcript_text: str, note_repair: Any) -> Any:
    """Parse Responses-API message text into candidates (Task 191 + N1).

    Order: each fenced block in turn (pre-handled, no repair logged),
    then the raw text as JSON. On plain-parse failure exactly ONE
    auto-repair runs (largest embedded JSON span); when that also fails
    the regex fallback salvages explicit bullet/numbered lines that are
    exact substrings of the transcript. Raises RuntimeError otherwise.
    """
    fenced_blocks = re.findall(
        r"`{3,}[^\n]*\n([\s\S]*?)(?:`{3,}|\Z)", text
    ) + re.findall(r"~{3,}[^\n]*\n([\s\S]*?)(?:~{3,}|\Z)", text)
    for block in fenced_blocks:
        try:
            return json.loads(block.strip())
        except (json.JSONDecodeError, ValueError):
            continue
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        direct_err = exc
    note_repair("model text is not plain JSON; extracting largest JSON span")
    try:
        return _extract_largest_json(text)
    except ValueError:
        pass
    salvaged = _regex_fallback_candidates(text, transcript_text)
    if salvaged:
        print(
            f"decision-server: regex fallback salvaged {len(salvaged)} candidate(s)",
            file=sys.stderr,
        )
        return salvaged
    raise RuntimeError(
        f"decision model returned non-JSON: {text[:500]}"
    ) from direct_err


@mcp.tool()
def extract_session_decisions(
    task_id: int, transcript_path: Optional[str] = None
) -> list[dict[str, Any]]:
    """Extract manager trade-offs/rulings from a session transcript.

    WHEN TO CALL (automatic): at the end of every session in which the
    manager ruled, chose, or constrained something — before closing the
    task. Feed its output into `record_manager_decision` (never persist
    raw output: it is UNSCRUBBED and UNVALIDATED).

    Reads `transcript.jsonl` from `tasks/.sessions/{task_id}/` (or the given
    path) and prompts the light LLM (DECISION_MODEL) to isolate manager
    decisions as structured objects. Raw output is returned UNSCRUBBED and
    UNVALIDATED — callers must pass candidates through
    `record_manager_decision` (which redacts + validates) before persistence.

    Args:
        task_id: Session scope (`tasks/.sessions/{task_id}/transcript.jsonl`).
        transcript_path: Explicit transcript override (tests / replays).

    Returns:
        List of candidate decision dicts (may be empty when the session
        holds no manager rulings). Never raises on missing transcripts —
        returns [] so the pipeline degrades gracefully. Raises
        RuntimeError on malformed model output (fail-loud beats a silent
        [] that downstream mistakes for "no rulings") and on present-but-
        empty transcripts (an existing file with zero turns is a broken
        pipeline, not a quiet session).
    """
    path = Path(transcript_path) if transcript_path else (
        Path.cwd() / "tasks" / ".sessions" / str(int(task_id)) / "transcript.jsonl"
    )
    if not path.is_file():
        return []  # Graceful path needs no LLM: check BEFORE the lazy import.
    turns: list[str] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            turns.append(f"[{record.get('role', '?')}] {record.get('content', '')}")
    if not turns:
        raise RuntimeError(
            f"decision transcript {path} exists but holds zero turns — "
            f"refusing to treat a broken pipeline as 'no rulings'"
        )
    prompt = (
        "Extract the MANAGER's decisions, trade-offs, and rulings from this session "
        "transcript. Preserve each ruling's verbatim quote. Reply with a JSON array; "
        "each item: {verbatim_quote: {original, english_translation}, "
        "extracted_decision: {summary, category, rationale, alternatives[], tradeoffs}}. "
        "Use categories: architecture/process/scope/quality-gate/tooling/release/other. "
        "Empty array when the session holds no manager rulings.\n\n" + "\n".join(turns)
    )
    transcript_bytes = path.read_bytes()
    transcript_text = "\n".join(turns)
    _get_decision_effort()  # Validate only; the value is dropped below.
    # Task 191: pin the EXTRACTION temperature to 0 unless the manager
    # explicitly sets BRAIN_TEMPERATURE (explicit wins, blank-means-unset
    # house rule). Scoped to this extraction call only — brainstorm and
    # other paths are untouched. Temperature is therefore ALWAYS sent
    # here, so reasoning_effort is always dropped (Responses models
    # reject the combination). Computed BEFORE the cache key so the key
    # covers (transcript, model, effective_temp) — an explicit override
    # never serves temp-0 results.
    raw_brain_temp = os.environ.get("BRAIN_TEMPERATURE", "").strip()
    raw_decision_temp = os.environ.get("DECISION_TEMPERATURE", "").strip()
    if raw_brain_temp:
        if raw_decision_temp:
            temp_to_send = _get_decision_temperature()
        else:
            try:
                explicit_temp = float(raw_brain_temp)
            except ValueError:
                raise ValueError(
                    f"BRAIN_TEMPERATURE={raw_brain_temp!r} is not a number; "
                    "set a numeric value or leave it blank"
                )
            if not 0.0 <= explicit_temp <= 2.0:
                raise ValueError(
                    f"BRAIN_TEMPERATURE={raw_brain_temp!r} out of range; "
                    "use 0.0-2.0 or leave it blank"
                )
            temp_to_send = explicit_temp
    else:
        temp_to_send = 0
    model = _get_decision_model()
    cache_key = _extract_cache_key(transcript_bytes, model, temp_to_send)
    global _last_cache_hits
    with _CACHE_LOCK:
        if cache_key in _EXTRACT_CACHE:
            _last_cache_hits += 1
            print(
                "decision-server: cache hit for transcript "
                f"{cache_key[:12]} (hits={_last_cache_hits})",
                file=sys.stderr,
            )
            hit = _EXTRACT_CACHE.pop(cache_key)
            _EXTRACT_CACHE[cache_key] = hit  # LRU touch: recent hits stay.
            return copy.deepcopy(hit)
    import httpx  # Lazy: import stays side-effect free.
    api_base = os.environ.get("BRAIN_API_BASE", "http://127.0.0.1:8081/zen/resp").strip() or "http://127.0.0.1:8081/zen/resp"
    body: dict[str, Any] = {
        "model": model,
        "input": [{"role": "user", "content": prompt}],
        "temperature": temp_to_send,
    }
    with httpx.Client(
        timeout=httpx.Timeout(connect=10, read=120, write=30, pool=10)
    ) as client:
        resp, _attempts = _post_with_retry(
            client, api_base.rstrip("/") + "/responses", body
        )
        data = _resp_json(resp)
    candidates: Any = None
    snippet = ""
    snippet_is_model_text = False
    repairs_this_call = 0

    def _note_repair(reason: str) -> None:
        """Log + count one repair (never more than one per call)."""
        global _REPAIR_COUNT
        nonlocal repairs_this_call
        repairs_this_call += 1
        _REPAIR_COUNT += 1
        print(
            f"decision-server: auto-repair attempt {repairs_this_call} ({reason})",
            file=sys.stderr,
        )
    if isinstance(data, list):
        # Already a candidate list (direct-JSON transport): use as-is.
        # Bare list payloads pass through (existing behavior).
        candidates = data
        snippet = json.dumps(data)[:500]
    elif isinstance(data, dict) and isinstance(data.get("output"), list):
        # Responses-API envelope: pull the message text, trying EACH
        # fenced block until one parses as JSON (models often emit
        # several blocks; only one is the payload). Non-JSON text falls
        # through to exactly-one auto-repair, then the regex fallback
        # (Task 191).
        snippet = _responses_text(data).strip()
        snippet_is_model_text = True
        candidates = _parse_model_text(snippet, transcript_text, _note_repair)
        if isinstance(candidates, dict):
            if "candidates" in candidates:
                raise RuntimeError(
                    "decision model returned an envelope dict with "
                    f"'candidates' key, not a candidate: {snippet[:500]}"
                )
            # Bare decision object inside the envelope: wrap it.
            candidates = [candidates]
    elif isinstance(data, dict):
        if "candidates" in data:
            raise RuntimeError(
                "decision model returned an envelope dict with "
                f"'candidates' key, not a candidate: {str(data)[:500]}"
            )
        # Bare decision object (direct-JSON transport): wrap it.
        candidates = [data]
        snippet = json.dumps(data)[:500]
    else:
        # null/bool/number/string payloads are never valid candidates.
        raise RuntimeError(
            f"decision model returned a non-list of dicts: {str(data)[:500]}"
        )
    if isinstance(candidates, (str, int, float, bool)) or candidates is None:
        raise RuntimeError(
            f"decision model returned a non-list of dicts: {snippet[:500]}"
        )
    if not isinstance(candidates, list) or not all(
        isinstance(item, dict) for item in candidates
    ):
        raise RuntimeError(
            f"decision model returned a non-list of dicts: {snippet[:500]}"
        )
    try:
        _validate_extracted_candidates(candidates, transcript_text)
    except RuntimeError as schema_exc:
        # N1: exactly one auto-repair on validation fail — and only when
        # the snippet is model text worth re-mining (direct-JSON
        # transports re-parse to the identical object, so skip them).
        if repairs_this_call >= 1 or not snippet_is_model_text:
            raise
        _note_repair(f"schema validation failed ({schema_exc}); re-mining largest JSON span")
        try:
            remined: Any = _extract_largest_json(snippet)
        except ValueError:
            remined = None
        if isinstance(remined, dict):
            if "candidates" in remined:
                raise RuntimeError(
                    "decision model returned an envelope dict with "
                    f"'candidates' key, not a candidate: {snippet[:500]}"
                )
            remined = [remined]
        if isinstance(remined, list):
            # Raises loudly when still invalid — one repair only.
            _validate_extracted_candidates(remined, transcript_text)
            candidates = remined
        else:
            salvaged = _regex_fallback_candidates(snippet, transcript_text)
            if not salvaged:
                raise
            _validate_extracted_candidates(salvaged, transcript_text)
            candidates = salvaged
    if not candidates and turns:
        print(
            "decision-server: model returned [] for a non-empty transcript",
            file=sys.stderr,
        )
    # Cache only validated candidates (LRU, capped, lock-guarded).
    with _CACHE_LOCK:
        _EXTRACT_CACHE[cache_key] = copy.deepcopy(candidates)
        while len(_EXTRACT_CACHE) > _EXTRACT_CACHE_MAX:
            _EXTRACT_CACHE.pop(next(iter(_EXTRACT_CACHE)))
    return candidates


@mcp.tool()
def record_manager_decision(decision: dict[str, Any]) -> str:
    """Redact, validate, and persist one manager decision; return its id.

    WHEN TO CALL (automatic): immediately after `extract_session_decisions`
    returns candidates, or whenever the manager states a ruling mid-session
    (don't wait for session end — capture rulings while verbatim). This is
    the ONLY write path into the learning repo.

    Pipeline: `sanitize_text` every free-text field → `verify_clean` gate →
    schema validation → write `decisions/YYYY/MM/DEC-*.json` + matching `.md`
    (verbatim quote + summary for humans) → regenerate `INDEX.md`.

    Args:
        decision: Candidate object (verbatim_quote + extracted_decision;
            decision_id/timestamp assigned here when absent).

    Returns:
        Human-readable confirmation including the decision id and paths.

    Raises:
        ValueError: On redaction failure or schema violations — nothing is
            written in that case (append-only store stays clean).
    """
    repo = _repo_root()
    scrubbed = _scrub_free_text(decision)
    scrubbed.setdefault("decision_id", _next_decision_id(repo))
    scrubbed.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    problems = _validate_against_schema(scrubbed)
    if problems:
        raise ValueError(f"decision schema violations: {'; '.join(problems)}")
    date_part = scrubbed["decision_id"][4:12]  # YYYYMMDD from DEC-YYYYMMDD-NNN.
    day_dir = repo / "decisions" / date_part[:4] / date_part[4:6]
    day_dir.mkdir(parents=True, exist_ok=True)
    json_path = day_dir / f"{scrubbed['decision_id']}.json"
    json_path.write_text(json.dumps(scrubbed, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    quote = scrubbed["verbatim_quote"]
    extracted = scrubbed["extracted_decision"]
    md_path = day_dir / f"{scrubbed['decision_id']}.md"
    md_path.write_text(
        f"# {scrubbed['decision_id']} — {extracted.get('summary', '')}\n\n"
        f"- Category: {extracted.get('category')}\n"
        f"- Session: {scrubbed.get('session_id', '?')}\n"
        f"- Project: {scrubbed.get('project_name', '?')}\n\n"
        f"## Verbatim (original)\n\n> {quote.get('original', '')}\n\n"
        f"## Verbatim (English)\n\n> {quote.get('english_translation', '')}\n\n"
        f"## Rationale\n\n{extracted.get('rationale', '')}\n",
        encoding="utf-8",
    )
    count = _rewrite_index(repo)
    return (f"Recorded {scrubbed['decision_id']} "
            f"(`{json_path.relative_to(repo)}` + `.md`; index now holds {count}).")


@mcp.tool()
def query_manager_decisions(query: str, category: Optional[str] = None) -> str:
    """Search stored decisions by keyword (+ optional category).

    WHEN TO CALL (automatic): BEFORE paging the human manager with a
    question — if a past ruling covers it, decide from the record instead.
    Also call it during discovery when the task touches architecture,
    process, scope, or quality gates.

    Case-insensitive substring match over summaries, rationales, trade-offs,
    alternatives, and both verbatim-quote languages. Returns formatted
    summaries with verbatim quotes, or a no-match message (never an error)
    when empty.

    Args:
        query: Keyword(s); blank returns everything in the category.
        category: Optional category filter (see schema enum).
    """
    repo = _repo_root()
    needle = (query or "").strip().lower()
    hits: list[str] = []
    for path in sorted((repo / "decisions").rglob("DEC-*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        extracted = record.get("extracted_decision", {})
        if category and extracted.get("category") != category:
            continue
        quote = record.get("verbatim_quote", {})
        alternatives = extracted.get("alternatives", []) or []
        haystack = " ".join([
            str(extracted.get("summary", "")), str(extracted.get("rationale", "")),
            str(extracted.get("tradeoffs", "")), " ".join(str(a) for a in alternatives),
            str(quote.get("original", "")),
            str(quote.get("english_translation", "")),
        ]).lower()
        if needle and needle not in haystack:
            continue
        hits.append(
            f"### {record.get('decision_id')} [{extracted.get('category')}] "
            f"{extracted.get('summary', '')}\n"
            f"> {quote.get('english_translation', '')}\n"
            f"Rationale: {extracted.get('rationale', '')}"
        )
    if not hits:
        return f"No manager decisions match query={query!r} category={category!r}."
    return f"{len(hits)} decision(s) match:\n\n" + "\n\n".join(hits)


@mcp.tool()
def get_manager_profile() -> str:
    """Return `samples/manager_profile.md` for agent context injection.

    WHEN TO CALL (automatic): inject its output into your reasoning whenever
    resolving an architectural ambiguity or applying a house rule — the
    profile IS the manager's standing judgment. Cheap, read-only, no
    side effects.

    The baseline section is curated; the generated aggregate (if any) comes
    from reviewed compilations only — this tool never synthesizes guidance.
    Returns an explanatory message (not an error) when the sample is absent.
    """
    profile = _repo_root() / "samples" / "manager_profile.md"
    if not profile.is_file():
        return "No manager profile sample exists yet."
    return profile.read_text(encoding="utf-8")


@mcp.tool()
def propose_profile_evolution() -> dict[str, Any]:
    """Draft a profile update for MANAGER approval (review gate enforced).

    WHEN TO CALL (automatic): only when new recorded decisions exist that
    the current sample does not reflect — roughly once per sprint, never
    per session. Present the DRAFT_READY payload to the manager; merge
    nothing without an explicit approve.

    Executes `scripts/compile_profile.py` in a subprocess and returns the
    draft as a staged diff-like payload. NOTHING is written to the sample:
    the manager must approve the draft before any identity update lands.

    Returns:
        Dict with `status` (`"DRAFT_READY"` / `"EMPTY"` / `"ERROR"`) and the
        `draft` text (or reason). Never raises — failures arrive as ERROR.
    """
    repo = _repo_root()
    script = repo / "scripts" / "compile_profile.py"
    if not script.is_file():
        return {"status": "ERROR", "draft": f"compile script missing: {script}"}
    try:
        completed = subprocess.run(
            [sys.executable, str(script), "--repo", str(repo)],
            capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"status": "ERROR", "draft": f"compile failed: {exc}"}
    if completed.returncode != 0:
        return {"status": "ERROR", "draft": completed.stderr.strip() or "unknown error"}
    draft = completed.stdout.strip()
    if not draft or draft.startswith("No decisions found"):
        return {"status": "EMPTY", "draft": draft or "No decisions found."}
    return {"status": "DRAFT_READY", "draft": draft}


if __name__ == "__main__":
    mcp.run(transport="stdio")
