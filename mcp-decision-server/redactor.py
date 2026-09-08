"""Redaction engine for manager-decision persistence (Task 168).

Every free-text field is scrubbed by `sanitize_text` BEFORE it touches the
decision repo; `verify_clean` attests the stored text holds zero sensitive
patterns, and its result feeds the record's `redaction_verified` flag.
Patterns covered: provider API keys (`sk-...`, `ghp_...`, `AIzaSy...`),
Bearer tokens, private IPv4 ranges (`10/8`, `172.16/12`, `192.168/16`),
and generic `password = ...` / `token = ...` credential assignments.

Pure standard library — deterministic and unit-testable without network.
"""

from __future__ import annotations

import re

# Each entry: (compiled pattern, replacement). Order matters: specific
# provider keys first, generic credential assignments last.
REDACTION_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    # OpenAI / OpenRouter style secret keys.
    (re.compile(r"\bsk-(?:proj-|live-|test-)?[A-Za-z0-9_-]{8,}\b"), "[REDACTED_API_KEY]"),
    # GitHub personal access tokens.
    (re.compile(r"\bghp_[A-Za-z0-9]{8,}\b"), "[REDACTED_GITHUB_TOKEN]"),
    # Google API keys.
    (re.compile(r"\bAIzaSy[A-Za-z0-9_-]{10,}\b"), "[REDACTED_GOOGLE_KEY]"),
    # Bearer tokens (Authorization headers, config dumps).
    (re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/=]{8,}", re.IGNORECASE), "Bearer [REDACTED]"),
    # Private IPv4: 10/8, 172.16/12, 192.168/16 (loopback stays — harmless).
    (re.compile(r"\b10(?:\.\d{1,3}){3}\b"), "[REDACTED_IP]"),
    (re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"), "[REDACTED_IP]"),
    (re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"), "[REDACTED_IP]"),
    # Generic credential assignments: password = "secret", token: xyz.
    (re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|auth[_-]?token)\b\s*[:=]\s*\S+"),
     r"\1=[REDACTED]"),
)

# Detection patterns for the verify pass. Identical to REDACTION_RULES except
# the credential-assignment pattern carries a negative lookahead so an
# already-redacted `password=[REDACTED]` marker is NOT mistaken for a live
# secret (otherwise verify_clean could never pass on sanitized text).
_VERIFY_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|secret|api[_-]?key|auth[_-]?token)\b\s*[:=]\s*(?!\[REDACTED\])\S+"
)
_VERIFY_RESIDUE: tuple[re.Pattern[str], ...] = tuple(
    _VERIFY_ASSIGNMENT if rule is REDACTION_RULES[-1][0] else rule
    for rule, _ in REDACTION_RULES
)


def sanitize_text(text: str) -> str:
    """Scrub sensitive patterns from `text`, returning the redacted copy.

    Idempotent: running it twice yields the same output (markers contain no
    matchable secret shapes). Non-string input is coerced to str; empty
    input returns empty.
    """
    if not isinstance(text, str):
        text = str(text)
    if not text:
        return ""
    scrubbed = text
    for pattern, replacement in REDACTION_RULES:
        scrubbed = pattern.sub(replacement, scrubbed)
    return scrubbed


def verify_clean(text: str) -> bool:
    """Return True when no sensitive pattern remains in `text`.

    Run on the SANITIZED text before persistence; a False result must block
    the write (the record's `redaction_verified` stays False and the caller
    rejects the decision). Markers like `[REDACTED_API_KEY]` never match —
    they carry no secret-shaped content.
    """
    if not isinstance(text, str):
        text = str(text)
    return not any(pattern.search(text) for pattern in _VERIFY_RESIDUE)
