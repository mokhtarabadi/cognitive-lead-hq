"""Tests for No-Manual-DTO Mandate & Type Drift Sentinel (LE-7 / Task 139).

Covers:
1. Prompt assembly — ``assemble_system_prompt.py`` includes
   ``<no_manual_dto_mandate>`` with ``<system_version>9.3.0</system_version>``
   and passes the closing-tag normalization self-check; manifest registration
   precedes ``18-initialization.md``.
2. ``TypeDriftSentinel.check_diff`` — detects manual TypeScript interfaces,
   Kotlin data/plain classes, and Python Pydantic models in consumer paths.
3. Exemptions — DTO declarations in ``packages/shared-schema/**`` and
   ``**/generated/**`` are allowed; clean imports produce no false positives.
4. Bypass — explicit ``drift-ignore`` comments (line-level and trailing).
5. Integration — ``ToolchainRunner`` fail-fast with drift present; clean diff
   leaves the toolchain untouched; ``daemon._execute_and_qa`` forwards
   ``diff_text=diff`` into the runner.
"""
import asyncio
import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(__file__))

from sentinel import DriftCheckResult, TypeDriftSentinel
from verifier import CommandResult, ToolchainResult

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _diff(path: str, *added_lines: str, start: int = 1) -> str:
    """Build a minimal git diff with *added_lines* under one new-file hunk."""
    hunks = "".join(f"+{line}\n" for line in added_lines)
    return (
        f"diff --git a/{path} b/{path}\n"
        f"--- a/{path}\n"
        f"+++ b/{path}\n"
        f"@@ -1,1 +{start},{len(added_lines)} @@\n"
        f"{hunks}"
    )


_TS_DIFF = _diff(
    "apps/api/src/user.ts",
    "export interface CreateUserDTO {",
    "  name: string;",
    "}",
)

_KT_DATA_DIFF = _diff(
    "services/orders/Order.kt",
    "data class OrderResponse(",
    "    val id: Long,",
    ")",
)

_KT_PLAIN_DIFF = _diff("services/orders/Invoice.kt", "class InvoiceRequest(")

_PY_DIFF = _diff(
    "src/models/user.py",
    "class CreateUserDTO(BaseModel):",
    "    name: str",
)


def _load_assembler():
    """Import scripts/prompt-build/assemble_system_prompt.py from the repo root."""
    spec = importlib.util.spec_from_file_location(
        "assemble_system_prompt",
        REPO_ROOT / "scripts/prompt-build/assemble_system_prompt.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


class _Toolchain:
    def __init__(self, lint=None, build=None, test=None):
        self.lint_cmd = lint
        self.build_cmd = build
        self.test_cmd = test


class _Profile:
    def __init__(self, toolchain=None):
        self.toolchain = toolchain


# ---------------------------------------------------------------------------
# 1. Prompt assembly (mandate fragment + version)
# ---------------------------------------------------------------------------


def test_assembler_includes_no_manual_dto_mandate_with_version_930(tmp_path):
    mod = _load_assembler()
    out = tmp_path / "assembled.md"
    result = mod.assemble(
        output_path=str(out),
        fragments_dir=str(REPO_ROOT / "prompts/fragments"),
        manifest_path=str(REPO_ROOT / "prompts/manifest.txt"),
    )

    # Mandate block present with both open and close tags.
    assert "<no_manual_dto_mandate>" in result
    assert "</no_manual_dto_mandate>" in result

    # Version fragment bumped to 9.3.0 and reflected in the artifact.
    version_frag = (REPO_ROOT / "prompts/fragments/01-system_version.md").read_text(
        encoding="utf-8"
    )
    assert "9.3.0" in version_frag
    assert "<system_version>9.3.0</system_version>" in result

    # Closing-tag normalization: no indented pure closing tags survive.
    drifted = [
        line
        for line in result.splitlines()
        if line.startswith(" ") and line.lstrip().startswith("</")
    ]
    assert not drifted, f"Drifted closing tags found: {drifted}"


def test_manifest_registers_mandate_before_initialization():
    manifest = (REPO_ROOT / "prompts/manifest.txt").read_text(encoding="utf-8").splitlines()
    assert "20-no_manual_dto_mandate.md" in manifest
    assert manifest.index("20-no_manual_dto_mandate.md") < manifest.index(
        "18-initialization.md"
    )


# ---------------------------------------------------------------------------
# 2. Detection of manual declarations in consumer paths
# ---------------------------------------------------------------------------


def test_detects_typescript_interface():
    result = TypeDriftSentinel().check_diff(_TS_DIFF)
    assert result.passed is False
    assert any("CreateUserDTO" in v for v in result.violations)
    assert any("apps/api/src/user.ts" in v for v in result.violations)


def test_detects_kotlin_data_class():
    result = TypeDriftSentinel().check_diff(_KT_DATA_DIFF)
    assert result.passed is False
    assert any("OrderResponse" in v for v in result.violations)


def test_detects_kotlin_plain_class():
    result = TypeDriftSentinel().check_diff(_KT_PLAIN_DIFF)
    assert result.passed is False
    assert any("InvoiceRequest" in v for v in result.violations)


def test_detects_python_pydantic_model():
    result = TypeDriftSentinel().check_diff(_PY_DIFF)
    assert result.passed is False
    assert any("CreateUserDTO" in v for v in result.violations)
    assert any("Python" in v for v in result.violations)


def test_multiple_language_violations_captured():
    combined = _TS_DIFF + _KT_DATA_DIFF + _PY_DIFF
    result = TypeDriftSentinel().check_diff(combined)
    assert result.passed is False
    assert len(result.violations) == 3


# ---------------------------------------------------------------------------
# 3. Exemptions (allowed/contract paths, clean imports)
# ---------------------------------------------------------------------------


def test_allows_dto_in_shared_schema():
    diff = _diff(
        "packages/shared-schema/v1/types.ts",
        "export interface UserDTO { id: string; }",
    )
    result = TypeDriftSentinel().check_diff(diff)
    assert result.passed is True


def test_allows_dto_in_generated_dir():
    diff = _diff(
        "apps/web/src/generated/api.ts",
        "export interface CreateUserDTO { id: string; }",
    )
    result = TypeDriftSentinel().check_diff(diff)
    assert result.passed is True


def test_allows_dto_in_gen_file():
    diff = _diff(
        "apps/web/src/client.gen.ts",
        "export interface UserResponse { ok: boolean; }",
    )
    result = TypeDriftSentinel().check_diff(diff)
    assert result.passed is True


def test_allows_clean_imports():
    diff = _diff(
        "apps/web/src/api.ts",
        "import { ShiftDTO, exactOptionalPropertyTypes } from '@repo/shared-schema';",
        "import type { UserDTO } from '@repo/shared-schema';",
    )
    result = TypeDriftSentinel().check_diff(diff)
    assert result.passed is True


def test_allows_type_reexport():
    diff = _diff(
        "apps/web/src/barrel.ts",
        "export type { UserDTO, OrderResponse } from '@repo/shared-schema';",
    )
    result = TypeDriftSentinel().check_diff(diff)
    assert result.passed is True


def test_non_consumer_path_not_flagged():
    diff = _diff(
        "config/settings.ts",
        "export interface SettingsDTO { theme: string; }",
    )
    result = TypeDriftSentinel().check_diff(diff)
    assert result.passed is True


def test_empty_diff_passes():
    assert TypeDriftSentinel().check_diff("").passed is True


def test_context_only_diff_passes():
    diff = (
        "diff --git a/apps/api/src/user.ts b/apps/api/src/user.ts\n"
        "--- a/apps/api/src/user.ts\n"
        "+++ b/apps/api/src/user.ts\n"
        "@@ -10,3 +10,3 @@\n"
        " export function getUser() {\n"
        "-  return git;\n"
        "+  return branch;\n"
        " }\n"
    )
    assert TypeDriftSentinel().check_diff(diff).passed is True


# ---------------------------------------------------------------------------
# 4. drift-ignore bypass
# ---------------------------------------------------------------------------


def test_drift_ignore_trailing_comment_bypass():
    diff = _diff(
        "apps/web/src/legacy.ts",
        "export interface LegacyDTO { x: string } // drift-ignore: legacy mirror",
    )
    assert TypeDriftSentinel().check_diff(diff).passed is True


def test_drift_ignore_comment_line_bypass():
    diff = _diff(
        "apps/web/src/adapters.ts",
        "// drift-ignore: generated adapter, mirror kept in sync by tooling",
        "export interface AdapterDTO { x: string } // drift-ignore: kept in sync",
    )
    assert TypeDriftSentinel().check_diff(diff).passed is True


# ---------------------------------------------------------------------------
# 5. Report quality
# ---------------------------------------------------------------------------


def test_report_contains_actionable_instructions():
    result = TypeDriftSentinel().check_diff(_PY_DIFF)
    assert not result.passed
    assert "Required Action" in result.report_md
    assert "@repo/shared-schema" in result.report_md
    assert "prisma generate" in result.report_md
    assert "protoc" in result.report_md
    assert "drift-ignore" in result.report_md


def test_line_numbers_tracked():
    diff = _diff("apps/api/src/user.ts", "export interface CreateUserDTO {", start=7)
    result = TypeDriftSentinel().check_diff(diff)
    assert any("added line 7" in v for v in result.violations)


def test_custom_patterns():
    sentinel = TypeDriftSentinel(
        consumer_patterns=["packages/mobile/**"],
        allowed_patterns=["packages/mobile/generated/**"],
    )
    # Consumer in custom pattern.
    bad = _diff("packages/mobile/src/api.kt", "data class UserModel(")
    assert sentinel.check_diff(bad).passed is False
    # Allowed under custom pattern.
    good = _diff("packages/mobile/generated/api.kt", "data class UserModel(")
    assert sentinel.check_diff(good).passed is True


# ---------------------------------------------------------------------------
# 6. ToolchainRunner / daemon integration
# ---------------------------------------------------------------------------


def test_toolchain_runner_failfast_on_drift():
    from verifier import ToolchainRunner

    profile = _Profile(_Toolchain(lint="echo lint", build="echo build", test="echo test"))
    result = ToolchainRunner().run_sync(profile, diff_text=_TS_DIFF)

    assert result.passed is False
    assert len(result.commands) == 1, "fail-fast: no toolchain commands ran"
    cmd = result.commands[0]
    assert cmd.command == "type-drift-sentinel"
    assert cmd.cmd_type == "lint"
    assert cmd.passed is False
    assert "CreateUserDTO" in cmd.stderr


def test_toolchain_runner_passes_without_drift():
    from verifier import ToolchainRunner

    diff = _diff(
        "apps/api/src/user.ts",
        "import { UserDTO } from '@repo/shared-schema';",
    )
    profile = _Profile(_Toolchain())
    result = ToolchainRunner().run_sync(profile, diff_text=diff)

    assert result.passed is True
    # Sentinel passed silently — no sentinel command recorded, toolchain ran
    # as usual (3 nullable commands -> skipped).
    assert all(c.skipped for c in result.commands)
    assert all(c.command != "type-drift-sentinel" for c in result.commands)


def test_toolchain_runner_without_diff_text_unchanged():
    from verifier import ToolchainRunner

    profile = _Profile(_Toolchain())
    result = ToolchainRunner().run_sync(profile)
    assert result.passed is True
    assert len(result.commands) == 3


def test_daemon_passes_diff_text_to_runner(tmp_path):
    import daemon as daemon_mod

    diff_body = (
        "diff --git a/apps/api/src/user.ts b/apps/api/src/user.ts\n"
        "@@ -1 +1,2 @@\n"
        "+export interface CreateUserDTO {\n"
    )
    task_file = tmp_path / "99-foo.md"
    task_file.write_text(
        "# Task 99: Foo\n\n## Factual Git Diff\n\n"
        "<!-- BEGIN_GIT_DIFF -->\n" + diff_body + "<!-- END_GIT_DIFF -->\n",
        encoding="utf-8",
    )

    state = MagicMock()
    executor = MagicMock()
    executor.execute = AsyncMock(return_value={"status": "complete"})
    qa = MagicMock()
    qa.run_qa.return_value = {"result": "PASSED"}

    with patch.object(daemon_mod, "ToolchainRunner") as toolchain_cls:
        toolchain_cls.return_value.run = AsyncMock(
            return_value=ToolchainResult(passed=True, summary="ok", report_md="")
        )
        asyncio.run(
            daemon_mod._execute_and_qa(
                99,
                str(task_file),
                task_file.read_text(encoding="utf-8"),
                task_file,
                state,
                executor,
                qa,
            )
        )

    call = toolchain_cls.return_value.run.await_args
    assert call is not None
    assert call.kwargs["diff_text"] == diff_body.strip()
    qa.run_qa.assert_called_once()