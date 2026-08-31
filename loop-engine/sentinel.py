"""
Type Drift Sentinel (LE-7 / Task 139).

Deterministic regex-based scanner that detects hand-authored duplicate
interface models, request/response DTOs, and data classes in consumer
application paths during the toolchain verification gate — BEFORE LLM QA.

Complements the No-Manual-DTO Mandate (prompts/fragments/20-no_manual_dto_mandate.md):
the prompt fragment is the cognitive rule; this module is the deterministic
enforcement layer. When a diff introduces a manual DTO/interface/model
declaration into a consumer path while a source-of-truth contract or shared
schema governs those types, check_diff() returns a failing DriftCheckResult
with an actionable Markdown report instructing the agent to import from the
shared package or run the stack's code-generation toolchain.

The sentinel is intentionally side-effect free and unit-testable, mirroring
the pure-helper design of loop-engine/contracts.py.
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field


@dataclass
class DriftCheckResult:
    """Outcome of a type-drift scan over a task diff."""

    passed: bool
    violations: list[str] = field(default_factory=list)
    report_md: str = ""


# Regexes matching hand-authored model/DTO declarations per language family.
# TypeScript/JavaScript: interfaces and type aliases whose name carries a
# DTO/model marker (e.g. `export interface CreateUserDTO {`, `type UserResponse = ...`).
_TS_JS_RE = re.compile(
    r"\b(?:export\s+)?(?:interface|type)\s+"
    r"([A-Za-z0-9_]*(?:Dto|DTO|Request|Response|Payload|Model|Schema))\b"
)
# Kotlin: data classes and plain classes with a DTO/model marker
# (e.g. `data class CreateUserRequest(`, `class OrderResponse(`).
_KOTLIN_RE = re.compile(
    r"\b(?:data\s+)?class\s+"
    r"([A-Za-z0-9_]*(?:Dto|DTO|Request|Response|Payload|Model))\b"
)
# Python: classes deriving from BaseModel/BaseDTO/dict with a DTO/model marker
# (e.g. `class CreateUserDTO(BaseModel):`).
_PYTHON_RE = re.compile(
    r"\bclass\s+"
    r"([A-Za-z0-9_]*(?:Dto|DTO|Request|Response|Payload|Schema))"
    r"\s*\((?:BaseModel|BaseDTO|dict)?\)"
)

# Default consumer paths where hand-authored DTOs are forbidden when a
# governing contract exists.
DEFAULT_CONSUMER_PATTERNS = [
    "apps/**",
    "services/**",
    "client/**",
    "frontend/**",
    "mobile/**",
    "src/**",
]

# Default paths where DTO/interface/model declarations are the canonical
# source of truth (contract definitions) or generated artifacts — exempt.
DEFAULT_ALLOWED_PATTERNS = [
    "packages/shared-schema/**",
    "contracts/**",
    "openapi/**",
    "proto/**",
    "**/generated/**",
    "**/build/**",
    "**/dist/**",
    "**/*.gen.*",
]

# Comment prefixes that mark a line as a comment (skipped by the scanner).
_COMMENT_PREFIXES = ("//", "#", "/*", "*", "<!--", "--", "'''", '"""')


class TypeDriftSentinel:
    """Scan git diffs for hand-authored duplicate DTO declarations.

    Args:
        consumer_patterns: fnmatch globs for consumer application paths where
            manual DTO declarations are forbidden (defaults to
            DEFAULT_CONSUMER_PATTERNS).
        allowed_patterns: fnmatch globs for contract/generated paths that are
            exempt from the mandate (defaults to DEFAULT_ALLOWED_PATTERNS).
    """

    def __init__(
        self,
        consumer_patterns: list[str] | None = None,
        allowed_patterns: list[str] | None = None,
    ):
        self.consumer_patterns = (
            list(consumer_patterns)
            if consumer_patterns is not None
            else list(DEFAULT_CONSUMER_PATTERNS)
        )
        self.allowed_patterns = (
            list(allowed_patterns)
            if allowed_patterns is not None
            else list(DEFAULT_ALLOWED_PATTERNS)
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_diff(self, diff_text: str) -> DriftCheckResult:
        """Scan a git diff for manual DTO declarations in consumer paths.

        Non-contract/no-drift diffs return ``DriftCheckResult(passed=True)``.
        On violation, returns ``passed=False`` plus an actionable Markdown
        report telling the agent to import from the shared package or run the
        code-generation toolchain.
        """
        violations: list[str] = []
        for path, added_lines in self._iter_added_lines(diff_text):
            if self._matches_any(path, self.allowed_patterns):
                continue
            if not self._matches_any(path, self.consumer_patterns):
                continue
            for line_no, line in added_lines:
                if self._is_ignored(line):
                    continue
                self._scan_line(path, line_no, line, violations)

        if violations:
            return DriftCheckResult(
                passed=False,
                violations=violations,
                report_md=self._build_report(violations),
            )
        return DriftCheckResult(passed=True, violations=[])

    # ------------------------------------------------------------------
    # Diff parsing
    # ------------------------------------------------------------------

    def _iter_added_lines(self, diff_text: str):
        """Yield ``(path, [(line_no, content), ...])`` for files with additions.

        Parses ``diff --git a/<a> b/<b>`` headers (b-side path wins, refined by
        ``+++ b/<path>`` lines) and ``@@ -a,b +c,d @@`` hunk headers so each
        added line carries its approximate new-file line number.
        """
        current_path: str | None = None
        current_added: list[tuple[int, str]] = []
        new_line: int | None = None
        in_hunk = False

        # Accumulate files explicitly (a closure with yield would turn this
        # into a double-generator and is invalid inside this generator body).
        files: list[tuple[str, list[tuple[int, str]]]] = []

        for raw in diff_text.splitlines():
            line = raw
            header = re.match(r"^diff --git a/(.*) b/(.*)$", line)
            if header:
                if current_path is not None:
                    files.append((current_path, current_added))
                current_path = header.group(2).strip()
                current_added = []
                new_line = None
                in_hunk = False
                continue

            plus_path = re.match(r"^\+\+\+ b/(.*)$", line)
            if plus_path:
                current_path = plus_path.group(1).strip()
                continue

            hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if hunk:
                new_line = int(hunk.group(1))
                in_hunk = True
                continue

            if current_path is None or not in_hunk:
                continue

            if line.startswith("+"):
                if new_line is not None:
                    current_added.append((new_line, line[1:]))
                    new_line += 1
            elif line.startswith("-"):
                # Removed lines do not advance the new-file line counter.
                pass
            elif line.startswith(" "):
                if new_line is not None:
                    new_line += 1
            # "\ No newline at end of file" and other metadata are skipped.

        if current_path is not None:
            files.append((current_path, current_added))

        yield from files

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------

    def _matches_any(self, path: str, patterns: list[str]) -> bool:
        return any(fnmatch.fnmatch(path, pat) for pat in patterns)

    def _is_ignored(self, line: str) -> bool:
        """True for comment-only lines or lines carrying an explicit `drift-ignore` bypass."""
        if "drift-ignore" in line:
            return True
        stripped = line.strip()
        if not stripped:
            return True
        return stripped.startswith(_COMMENT_PREFIXES)

    def _scan_line(self, path: str, line_no: int, line: str, violations: list[str]) -> None:
        # Dispatch by file extension so a Python `class XxxDTO(BaseModel):`
        # line is labeled Python (not Kotlin, whose generic `class` regex also
        # matches). Unknown extensions fall back to a specificity-ordered
        # cascade (Python → TypeScript/JavaScript → Kotlin).
        _BY_EXTENSION = {
            ".py": ("Python", _PYTHON_RE),
            ".kt": ("Kotlin", _KOTLIN_RE),
            ".kts": ("Kotlin", _KOTLIN_RE),
            ".ts": ("TypeScript/JavaScript", _TS_JS_RE),
            ".tsx": ("TypeScript/JavaScript", _TS_JS_RE),
            ".js": ("TypeScript/JavaScript", _TS_JS_RE),
            ".jsx": ("TypeScript/JavaScript", _TS_JS_RE),
            ".mjs": ("TypeScript/JavaScript", _TS_JS_RE),
            ".cjs": ("TypeScript/JavaScript", _TS_JS_RE),
        }
        lowered = path.lower()
        match = None
        for ext, (lang, regex) in _BY_EXTENSION.items():
            if lowered.endswith(ext):
                match = regex.search(line)
                if match:
                    self._record_violation(path, line_no, lang, match.group(1), violations)
                    return
                return  # known language, no match -> not a violation of this language

        # Unknown extension: cascade by specificity (Python is most specific,
        # TS/JS next, Kotlin generic last). Only the first match labels the line.
        for lang, regex in (
            ("Python", _PYTHON_RE),
            ("TypeScript/JavaScript", _TS_JS_RE),
            ("Kotlin", _KOTLIN_RE),
        ):
            match = regex.search(line)
            if match:
                self._record_violation(path, line_no, lang, match.group(1), violations)
                return

    def _record_violation(
        self, path: str, line_no: int, lang: str, type_name: str, violations: list[str]
    ) -> None:
        violations.append(
            f"- `{path}` — manual {lang} model declaration `{type_name}` "
            f"(added line {line_no}). Import it from the shared/contract "
            f"package (`@repo/shared-schema`, `packages/shared-schema`) or run "
            f"the stack codegen (`pnpm generate`, `prisma generate`, `protoc`, "
            f"`./gradlew generateProto`) instead of hand-authoring a duplicate."
        )

    def _build_report(self, violations: list[str]) -> str:
        lines = [
            "# Type Drift Sentinel Report",
            "",
            "**Overall:** FAILED",
            "",
            "Hand-authored DTO/interface/model declarations were detected in consumer "
            "paths while a source-of-truth contract or shared schema governs these types.",
            "",
            "## Violations",
            "",
        ]
        lines.extend(violations)
        lines.extend(
            [
                "",
                "## Required Action",
                "",
                "- **Import** the type directly from the shared/contract package "
                "(`@repo/shared-schema`, `packages/shared-schema`) where it is defined, OR",
                "- **Run the stack's code-generation toolchain** (`pnpm generate`, "
                "`prisma generate`, `protoc`, `./gradlew generateProto`) to produce the "
                "type from the contract.",
                "",
                "Hand-written duplicates create silent type drift. Do NOT re-run QA "
                "until the violation is resolved (or justified with an explicit "
                "`drift-ignore` comment).",
            ]
        )
        return "\n".join(lines)