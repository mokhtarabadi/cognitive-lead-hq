#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.0,<2.0",
#     "litellm",
# ]
# ///

"""Manager-decision capture MCP server (Task 168).

Learning half of the persona pipeline: per-session manager trade-offs and
rulings are extracted (LiteLLM, default Gemini Flash), redacted, and
persisted append-only into the decision repo
(`packages/cognitive-lead-decisions/`, overridable via DECISION_REPO_PATH).
Stored decisions feed `query_manager_decisions` (consultation) and
`propose_profile_evolution` (gated sample updates — the script drafts, a
human approves; this server never rewrites the sample itself).

Transport: stdio FastMCP, mirroring mcp-persona-server. `litellm` is lazy so
import and unit tests never need network or credentials.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from redactor import sanitize_text, verify_clean

# Decision repo root: standalone checkout via env, else the in-repo package.
REPO_ROOT = Path(
    os.environ.get("DECISION_REPO_PATH", Path(__file__).resolve().parent.parent
                   / "packages" / "cognitive-lead-decisions")
)

mcp = FastMCP("ManagerDecisions")

# Free-text fields that must pass verify_clean before any write.
_SCRUB_FIELDS = ("original", "english_translation", "summary", "rationale", "tradeoffs")


def _repo_root() -> Path:
    """Resolve (creating) the decision repo root."""
    root = Path(os.environ.get("DECISION_REPO_PATH", str(REPO_ROOT)))
    root.mkdir(parents=True, exist_ok=True)
    return root


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


@mcp.tool()
def extract_session_decisions(
    task_id: int, transcript_path: Optional[str] = None
) -> list[dict[str, Any]]:
    """Extract manager trade-offs/rulings from a session transcript.

    Reads `transcript.jsonl` from `tasks/.sessions/{task_id}/` (or the given
    path) and prompts the light LLM (PERSONA_MODEL) to isolate manager
    decisions as structured objects. Raw output is returned UNSCRUBBED and
    UNVALIDATED — callers must pass candidates through
    `record_manager_decision` (which redacts + validates) before persistence.

    Args:
        task_id: Session scope (`tasks/.sessions/{task_id}/transcript.jsonl`).
        transcript_path: Explicit transcript override (tests / replays).

    Returns:
        List of candidate decision dicts (may be empty when the session
        holds no manager rulings). Never raises on missing transcripts —
        returns [] so the pipeline degrades gracefully.
    """
    path = Path(transcript_path) if transcript_path else (
        Path.cwd() / "tasks" / ".sessions" / str(int(task_id)) / "transcript.jsonl"
    )
    if not path.is_file():
        return []  # Graceful path needs no LLM: check BEFORE the lazy import.
    import litellm  # Lazy: import stays side-effect free.
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
        return []
    prompt = (
        "Extract the MANAGER's decisions, trade-offs, and rulings from this session "
        "transcript. Preserve each ruling's verbatim quote. Reply with a JSON array; "
        "each item: {verbatim_quote: {original, english_translation}, "
        "extracted_decision: {summary, category, rationale, alternatives[], tradeoffs}}. "
        "Use categories: architecture/process/scope/quality-gate/tooling/release/other. "
        "Empty array when the session holds no manager rulings.\n\n" + "\n".join(turns)
    )
    response = litellm.completion(
        model=os.environ.get("PERSONA_MODEL", "openrouter/google/gemini-3.8-flash"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        drop_params=True,
    )
    text = str(response.choices[0].message.content or "").strip()
    # Tolerate code-fenced replies from the model.
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fenced:
        text = fenced.group(1).strip()
    try:
        candidates = json.loads(text)
    except json.JSONDecodeError:
        return []
    return candidates if isinstance(candidates, list) else []


@mcp.tool()
def record_manager_decision(decision: dict[str, Any]) -> str:
    """Redact, validate, and persist one manager decision; return its id.

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

    Case-insensitive substring match over summaries, rationales, trade-offs,
    and both verbatim-quote languages. Returns formatted summaries with
    verbatim quotes, or a no-match message (never an error) when empty.

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
        haystack = " ".join([
            str(extracted.get("summary", "")), str(extracted.get("rationale", "")),
            str(extracted.get("tradeoffs", "")), str(quote.get("original", "")),
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
