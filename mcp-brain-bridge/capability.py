"""Capability preflight for mcp-brain-bridge (GitHub issue 16).

Stdlib-only, mirroring ``loop_guard``: importable without the MCP
runtime so unit tests stay offline.

A capability manifest maps every tool a turn references to exactly one
of three statuses — no silent fourth state:

- ``AVAILABLE`` — the Hands toolset provides it.
- ``UNAVAILABLE_REQUIRED`` — missing AND required: approval-sensitive
  work must stop (never silently skip) and emit the relay block.
- ``UNAVAILABLE_OPTIONAL`` — missing but not required: noted, skipped
  openly.

Availability registry grounding (read 2026-09-18): the granted tool
surface is ``opencode.json`` ``permission`` — families
``custom_context_*``, ``project_memory_*``, ``lint_*``, ``blowsh_*``,
``telegram_*``, plus ``brain_turn``, the manager-decision tools, the
context tools (``get_directory_tree``, ``read_source_files``,
``bundle_tasks``), and the native core (``task``, ``skill``,
``todowrite``, ``read``, ``edit``, ``write``, ``bash``, ``grep``,
``glob``). ``question`` is absent from ``opencode.json`` AND has zero
definitions anywhere in the repo, while two live references demand it
(``skill-templates/telegram-issue-sync/SKILL.md:79``,
``prompts/fragments/09-hands_protocols.md:66``) — hence
``KNOWN_UNAVAILABLE = {'question'}``. Unknown names fail closed
(``UNAVAILABLE_REQUIRED`` when required); the caller ``available`` /
``unavailable`` overrides are the documented escape hatch.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Optional

STATUSES = (
    "AVAILABLE",
    "UNAVAILABLE_REQUIRED",
    "UNAVAILABLE_OPTIONAL",
)

# Wildcard families granted in opencode.json `permission`.
AVAILABLE_FAMILIES = (
    "custom_context_",
    "project_memory_",
    "lint_",
    "blowsh_",
    "telegram_",
)

# Exact tool names outside those families: the bridge itself, the
# manager-decision tools, the context tools, and the native core.
AVAILABLE_EXACT = frozenset({
    "brain_turn",
    "get_sync_status",
    "query_manager_decisions",
    "get_manager_profile",
    "extract_session_decisions",
    "record_manager_decision",
    "propose_profile_evolution",
    "get_directory_tree",
    "read_source_files",
    "bundle_tasks",
    "task",
    "skill",
    "todowrite",
    "read",
    "edit",
    "write",
    "bash",
    "grep",
    "glob",
})

# Tools referenced by live prompts/skills but absent from the granted
# toolset (see module docstring). Listed explicitly so the manifest can
# name them instead of failing open on unknown names.
KNOWN_UNAVAILABLE = frozenset({
    "question",
})

# Approval-sensitive stages imply required tools even when the caller
# does not list them: QA always needs the task linter, closure always
# needs the commit path, planning/review always need the bridge.
STAGE_REQUIRED_TOOLS: Mapping[str, tuple[str, ...]] = {
    "plan": ("brain_turn",),
    "implement": (),
    "qa": ("lint_task_file",),
    "review": ("brain_turn",),
    "closure": ("custom_context_commit_and_clean_task",),
}

# The single approval rule (reconciles the contradictory handoff lines:
# autonomy "questions ride along" covers informational Q1/Q2 only —
# approval gates below are explicit blocking exceptions, collected
# through the mode-appropriate channel).
_PLAN_APPROVALS = frozenset({"approved", "approved for closure"})
_CLOSURE_APPROVALS = frozenset({"approved for closure", "close task"})


class CapabilityBlockedError(RuntimeError):
    """A required tool is unavailable for this stage."""

    def __init__(self, missing: Iterable[str], stage: Optional[str]) -> None:
        self.missing = tuple(missing)
        self.stage = stage
        names = ", ".join(self.missing)
        super().__init__(
            f"capability preflight: required tool(s) unavailable "
            f"for stage {stage!r}: {names}"
        )


def _is_available(name: str, available: frozenset,
                  unavailable: frozenset) -> bool:
    if name in unavailable:
        return False
    if name in available:
        return True
    if name in KNOWN_UNAVAILABLE:
        return False
    if name in AVAILABLE_EXACT:
        return True
    return any(name.startswith(fam) for fam in AVAILABLE_FAMILIES)


def build_manifest(
    referenced: Iterable[str],
    required: Iterable[str] = (),
    available: Iterable[str] = (),
    unavailable: Iterable[str] = (),
) -> dict:
    """Map each referenced tool to exactly one of ``STATUSES``."""
    required_set = frozenset(required)
    available_set = frozenset(available)
    unavailable_set = frozenset(unavailable)
    manifest: dict = {}
    for name in referenced:
        if _is_available(name, available_set, unavailable_set):
            manifest[name] = "AVAILABLE"
        elif name in required_set:
            manifest[name] = "UNAVAILABLE_REQUIRED"
        else:
            manifest[name] = "UNAVAILABLE_OPTIONAL"
    return manifest


def evaluate(
    referenced: Iterable[str] = (),
    required: Iterable[str] = (),
    stage: Optional[str] = None,
    available: Iterable[str] = (),
    unavailable: Iterable[str] = (),
) -> dict:
    """Build the manifest, merging stage-implied requirements first."""
    refs = list(referenced)
    reqs = list(required)
    if stage is not None:
        for implied in STAGE_REQUIRED_TOOLS.get(stage, ()):
            if implied not in refs:
                refs.append(implied)
            if implied not in reqs:
                reqs.append(implied)
    return build_manifest(refs, reqs, available, unavailable)


def gate(manifest: Mapping[str, str], stage: Optional[str] = None) -> None:
    """Raise ``CapabilityBlockedError`` when a required tool is missing."""
    missing = sorted(
        name for name, status in manifest.items()
        if status == "UNAVAILABLE_REQUIRED"
    )
    if missing:
        raise CapabilityBlockedError(missing, stage)


def format_relay_block(error: CapabilityBlockedError) -> str:
    """The single relay rule: missing tool → narrow question + answer slot.

    Carries only the missing names, the stage, and the question the
    human (manual mode) or the manager-decision replay (autopilot)
    must answer. Never carries file content.
    """
    names = ", ".join(error.missing)
    return (
        "[capability-blocked] Required tool(s) unavailable "
        f"for stage {error.stage!r}: {names}.\n"
        f"Question: how should this turn proceed without {names} "
        f"(provide an alternative tool, defer the step, or abort)?\n"
        "Answer slot: <manager answer here — the Hands resumes from it>."
    )


def is_approval(text: object, gate_name: object) -> bool:
    """Single approval rule. Closure accepts only the two exact phrases
    (case-insensitive; bare 'approved' never counts). The plan gate
    accepts 'approved' (any case) and 'approved for closure'. Blanket
    acknowledgements ('ok', 'yes', 'looks good', emoji) never count.
    Unknown gates never approve."""
    if not isinstance(text, str) or not isinstance(gate_name, str):
        return False
    normalized = " ".join(text.split()).casefold()
    if gate_name == "closure":
        return normalized in _CLOSURE_APPROVALS
    if gate_name == "plan":
        return normalized in _PLAN_APPROVALS
    return False
