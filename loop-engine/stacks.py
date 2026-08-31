"""
Stack Profile Engine — declarative YAML stack definitions, detection, and preflight.

Implements:
- StackProfile: thin wrapper around StackProfileConfig with helpers
- StackRegistry: scans stacks_dir, loads/caches .yaml/.json definitions
- StackDetector: two-tier heuristic (header > marker_files/extensions > keywords > generic)
- PreflightRunner: async validation of toolchain commands with timeout
"""

import asyncio
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Try to import yaml, fallback to safe parsing if unavailable
try:
    import yaml  # type: ignore

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from models import StackProfileConfig


# ---------------------------------------------------------------------------
# StackProfile — thin wrapper
# ---------------------------------------------------------------------------

class StackProfile:
    """Encapsulates a StackProfileConfig with validation and serialization."""

    def __init__(self, config: StackProfileConfig):
        self.config = config

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def display_name(self) -> str:
        return self.config.display_name

    @property
    def detection(self):
        return self.config.detection

    @property
    def skills(self) -> list[str]:
        return self.config.skills

    @property
    def preflight(self) -> list[str]:
        return self.config.preflight

    @property
    def toolchain(self):
        return self.config.toolchain

    @property
    def model_preferences(self) -> dict[str, list[str]]:
        return self.config.model_preferences

    def to_dict(self) -> dict:
        return self.config.model_dump()

    def __repr__(self) -> str:
        return f"StackProfile(name={self.name!r}, display_name={self.display_name!r})"


# ---------------------------------------------------------------------------
# StackRegistry — scan + cache
# ---------------------------------------------------------------------------

class StackRegistry:
    """Scans stacks_dir, loads/caches all .yaml and .json profile definitions."""

    def __init__(self, stacks_dir: str = "stacks", repo_root: str | Path | None = None):
        # Resolve stacks_dir relative to repo_root if needed
        if repo_root is None:
            # default: parent of loop-engine/ (REPO_ROOT)
            from pathlib import Path as _P

            repo_root = _P(__file__).resolve().parent.parent
        else:
            repo_root = Path(repo_root)

        p = Path(stacks_dir)
        if not p.is_absolute():
            p = Path(repo_root) / stacks_dir
        self.stacks_dir = p
        self._cache: dict[str, StackProfile] = {}
        self._loaded = False

    def _parse_file(self, path: Path) -> dict:
        text = path.read_text(encoding="utf-8")
        if path.suffix in (".yaml", ".yml"):
            if HAS_YAML:
                data = yaml.safe_load(text)
                if data is None:
                    return {}
                if not isinstance(data, dict):
                    raise ValueError(f"YAML root must be a mapping in {path}")
                return data
            else:
                # Fallback: try JSON parse if yaml not available
                try:
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    raise ImportError(f"PyYAML not installed and {path} is not JSON: {e}")
        elif path.suffix == ".json":
            return json.loads(text)
        else:
            raise ValueError(f"Unsupported profile extension: {path.suffix}")

    def _load_all(self) -> None:
        if self._loaded:
            return
        self._cache.clear()
        if not self.stacks_dir.exists():
            self._loaded = True
            return
        for f in sorted(self.stacks_dir.iterdir()):
            if f.suffix not in (".yaml", ".yml", ".json"):
                continue
            if f.is_dir():
                continue
            try:
                data = self._parse_file(f)
                cfg = StackProfileConfig(**data)
                # Ensure name matches filename if not explicitly consistent — but allow explicit name to win
                # Validate that name is filesystem-safe
                self._cache[cfg.name] = StackProfile(cfg)
            except Exception as e:
                # Re-raise with context for caller/test to assert on invalid schema
                raise ValueError(f"Failed to load stack profile {f.name}: {e}") from e
        self._loaded = True

    def list_profiles(self) -> list[StackProfile]:
        self._load_all()
        return list(self._cache.values())

    def get_profile(self, name: str) -> Optional[StackProfile]:
        self._load_all()
        return self._cache.get(name)

    def reload(self) -> None:
        """Force re-scan (useful in tests)."""
        self._loaded = False
        self._load_all()

    @property
    def names(self) -> list[str]:
        self._load_all()
        return sorted(self._cache.keys())


# ---------------------------------------------------------------------------
# StackDetector — two-tier heuristic
# ---------------------------------------------------------------------------

class StackDetector:
    """Two-tier detection logic.

    Precedence (highest to lowest):
      1. Explicit `**Stack:** <name>` header in task content
      2. Workspace marker_files or extension scan
      3. Task keywords (task_keywords substring match, case-insensitive)
      4. Fallback to default_stack ("generic")
    """

    # Matches: **Stack:** node-ts  or  **Stacks:** python-fastapi  etc.
    _HEADER_RE = re.compile(r"\*\*Stack:\*\*\s*([a-zA-Z0-9._\-/]+)", re.IGNORECASE)
    # Also allow Stack: without bold, case-insensitive
    _HEADER_RE_PLAIN = re.compile(r"^\s*Stack\s*:\s*([a-zA-Z0-9._\-/]+)", re.IGNORECASE | re.MULTILINE)

    @staticmethod
    def detect(
        task_content: str,
        workspace_root: str | Path,
        registry: StackRegistry,
        default_stack: str = "generic",
    ) -> StackProfile:
        # 1. Explicit header
        m = StackDetector._HEADER_RE.search(task_content)
        if m:
            name = m.group(1).strip().lower()
            profile = registry.get_profile(name)
            if profile is not None:
                return profile
            # Also try without lower? registry is case-sensitive lower
            profile = registry.get_profile(name)
            if profile:
                return profile

        m2 = StackDetector._HEADER_RE_PLAIN.search(task_content)
        if m2:
            name = m2.group(1).strip().lower()
            profile = registry.get_profile(name)
            if profile is not None:
                return profile

        workspace_root = Path(workspace_root)

        # 2. Marker files / extensions
        # First check marker_files existence
        for profile in registry.list_profiles():
            if profile.name == default_stack:
                continue  # skip generic in this phase; it's fallback
            for marker in profile.detection.marker_files:
                if (workspace_root / marker).exists():
                    return profile
            # Also scan for matching extensions in workspace (non-recursive top-level + one level?)
            # We walk up to 2 levels deep to avoid full repo scan cost
            if profile.detection.extensions:
                # Quick scan: list files at root and subdirs one level
                try:
                    # Root files
                    for f in workspace_root.iterdir():
                        if f.is_file() and any(f.name.endswith(ext) for ext in profile.detection.extensions):
                            return profile
                    # One level deep
                    for sub in workspace_root.iterdir():
                        if sub.is_dir() and not sub.name.startswith(".") and sub.name not in ("node_modules", "__pycache__", ".git", "loop-engine", "stacks", "tasks", ".venv", "venv"):
                            for f in sub.iterdir():
                                if f.is_file() and any(f.name.endswith(ext) for ext in profile.detection.extensions):
                                    return profile
                except (PermissionError, OSError):
                    pass

        # 3. Task keywords (case-insensitive substring)
        lower_content = task_content.lower()
        for profile in registry.list_profiles():
            if profile.name == default_stack:
                continue
            for kw in profile.detection.task_keywords:
                if kw.lower() in lower_content:
                    return profile

        # 4. Fallback
        generic = registry.get_profile(default_stack)
        if generic is not None:
            return generic
        # If even generic missing, return first available or synthesize generic
        profiles = registry.list_profiles()
        if profiles:
            return profiles[0]
        # Synthetic generic
        return StackProfile(StackProfileConfig(name="generic", display_name="Generic"))


# ---------------------------------------------------------------------------
# PreflightRunner — async toolchain validation
# ---------------------------------------------------------------------------

@dataclass
class PreflightResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


class PreflightRunner:
    """Asynchronously executes profile.preflight commands with timeouts."""

    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds

    async def run(self, profile: StackProfile, cwd: str | Path | None = None) -> PreflightResult:
        """Run all preflight commands sequentially. Return PreflightResult.

        Each command is executed via shell (so `||` works). Non-zero exit → error.
        Timeout → error. Empty preflight → passed.
        """
        if not profile.preflight:
            return PreflightResult(passed=True)

        errors: list[str] = []
        outputs: list[str] = []
        cwd_path = Path(cwd) if cwd else None

        for cmd in profile.preflight:
            try:
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(cwd_path) if cwd_path else None,
                )
                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(), timeout=self.timeout_seconds
                    )
                except asyncio.TimeoutError:
                    try:
                        proc.kill()
                    except ProcessLookupError:
                        pass
                    errors.append(f"Preflight timeout ({self.timeout_seconds}s): {cmd}")
                    continue

                out = stdout.decode(errors="replace").strip()
                err = stderr.decode(errors="replace").strip()
                combined = out
                if err:
                    combined = f"{out}\n{err}" if out else err
                outputs.append(combined)

                if proc.returncode != 0:
                    errors.append(f"Preflight failed ({proc.returncode}): {cmd} → {err or out or 'no output'}")

            except FileNotFoundError as e:
                errors.append(f"Preflight spawn failed: {cmd} → {e}")
            except Exception as e:
                errors.append(f"Preflight error: {cmd} → {e}")

        passed = len(errors) == 0
        return PreflightResult(passed=passed, errors=errors, outputs=outputs)

    def run_sync(self, profile: StackProfile, cwd: str | Path | None = None) -> PreflightResult:
        """Synchronous wrapper for tests and sync callers."""
        return asyncio.run(self.run(profile, cwd=cwd))
