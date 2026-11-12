# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Stage-aware Brain prompt routing — bridge lane (Task 396).

The Brain used to ship the FULL system prompt (all seven personas) on
every turn, whatever the stage. The stage artifacts split it into a shared
COMMON core plus ONE persona slice per stage, and the bridge routes a turn
to the artifact that serves its stage.

This file covers the BRIDGE side of that contract:

* the pure stage resolver (``resolve_stage_prompt_path``);
* the stage-aware prompt loader (explicit path → stage artifact → env
  override → full prompt), including the never-empty fallback;
* the preflight stage gate (``brainstorm`` admitted, typos still loud);
* the content contracts of the generated artifacts (manifest stage set,
  per-stage persona slices, plugin-blindness).

The stage manifest and the generated artifacts belong to the prompt lane.
Every test that needs them SKIPS cleanly while they are still missing, so
the bridge lane stays verifiable on its own.
"""

import json
import re
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BRIDGE_DIR = REPO / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

import preflight
import server as bridge

#: The stage manifest the prompt lane writes (the shared routing table).
MANIFEST = REPO / "prompts" / "stage-manifest.json"

#: Contract stage set (the task's stage-to-persona table).
CONTRACT_STAGES = ("plan", "implement", "qa", "review", "closure", "brainstorm")

#: Persona slugs per stage, per the same contract table.
CONTRACT_PERSONAS = {
    "plan": (
        "software-architect",
        "ui-ux-designer",
        "senior-programmer",
        "project-planner",
        "sprint-strategist",
    ),
    "implement": ("senior-programmer",),
    "qa": ("qa-engineer",),
    "review": ("code-reviewer",),
    "closure": ("senior-programmer",),
    "brainstorm": (
        "software-architect",
        "ui-ux-designer",
        "senior-programmer",
        "project-planner",
        "sprint-strategist",
        "qa-engineer",
        "code-reviewer",
    ),
}

#: Every persona seat in the catalog.
ALL_PERSONAS = CONTRACT_PERSONAS["brainstorm"]

#: Display names the persona slices carry in their ``<persona name="...">``.
PERSONA_NAMES = {
    "software-architect": "Software Architect",
    "ui-ux-designer": "UI/UX Designer",
    "senior-programmer": "Senior Programmer",
    "project-planner": "Project Planner",
    "sprint-strategist": "Sprint Strategist",
    "qa-engineer": "QA Engineer",
    "code-reviewer": "Code Reviewer",
}

#: Plugin-lane literals that must never reach a generated prompt artifact.
PLUGIN_LITERALS = (
    "goal_set",
    "compact_context",
    "read_omitted_content",
    "smart-compact",
    "magic-compact",
    "keepTurns",
    ".opencode/STOP_GOAL",
    "<compaction_protocol>",
)

#: Persona declaration inside an artifact's ``<personas>`` block.
_PERSONA_NAME_RE = re.compile(r'<persona name="([^"]+)"')


# --- hermetic bridge root ---------------------------------------------------


@pytest.fixture
def fake_bridge_root(tmp_path, monkeypatch):
    """Install a throwaway bridge root carrying its own stage manifest.

    The root lives under a patched ``$HOME/.config/opencode`` so the
    prompt-home rules accept the artifacts inside it, exactly like the
    global install does. Patching ``_bridge_root`` keeps every expectation
    hermetic: the repo's real manifest (written by the prompt lane) can
    never leak into a bridge-lane assertion.
    """
    home = tmp_path / "home"
    root = home / ".config" / "opencode"
    (root / "prompts").mkdir(parents=True)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    monkeypatch.setattr(bridge, "_bridge_root", lambda: root)
    return root


def _write_manifest(root, stages=None, artifact_dir="stage-prompts"):
    """Write a stage manifest shaped like the prompt lane's contract."""
    if stages is None:
        stages = {
            stage: {
                "personas": list(slugs),
                "artifact": f"system-prompt.{stage}.md",
            }
            for stage, slugs in CONTRACT_PERSONAS.items()
        }
    manifest = {
        "schema_version": 1,
        "common_fragments": ["01-system_version.md", "02-role.md"],
        "personas_dir": "prompts/fragments/personas",
        "catalog": "prompts/fragments/06-personas-catalog.md",
        "personas": {
            slug: f"prompts/fragments/personas/{slug}.md" for slug in ALL_PERSONAS
        },
        "stages": stages,
        "artifacts": {"dir": artifact_dir},
    }
    path = root / "prompts" / "stage-manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def _write_artifact(root, stage, text, artifact_dir="stage-prompts"):
    """Write the generated artifact that serves ``stage``."""
    path = root / artifact_dir / f"system-prompt.{stage}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _persona_slugs(entry):
    """Extract the persona slugs a manifest stage entry declares."""
    if isinstance(entry, list):
        return [str(item) for item in entry]
    if isinstance(entry, dict):
        for key in ("personas", "persona_slugs", "persona_slices", "slices"):
            value = entry.get(key)
            if isinstance(value, list):
                return [str(item) for item in value]
    raise AssertionError(f"stage entry declares no persona list: {entry!r}")


def _stage_artifact_files():
    """Every generated stage artifact on disk (empty list when none exist)."""
    artifact_dir = REPO / "build" / "stage-prompts"
    if MANIFEST.is_file():
        try:
            data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except ValueError:
            data = {}
        artifacts = data.get("artifacts") if isinstance(data, dict) else None
        if isinstance(artifacts, dict):
            for key in ("dir", "artifact_dir", "output_dir", "directory", "path"):
                value = artifacts.get(key)
                if isinstance(value, str) and value.strip():
                    artifact_dir = REPO / value.strip()
                    break
    if not artifact_dir.is_dir():
        return []
    return sorted(artifact_dir.glob("system-prompt.*.md"))


# --- the pure stage resolver ------------------------------------------------


def test_resolve_stage_prompt_path_covers_every_contract_stage(fake_bridge_root):
    """Every contract stage resolves to its own artifact path.

    The resolver is pure and manifest-driven: the path comes from the
    manifest's artifact directory plus the stage's artifact filename, so
    a stage never resolves to another stage's file.
    """
    _write_manifest(fake_bridge_root)
    for stage in CONTRACT_STAGES:
        resolved = bridge.resolve_stage_prompt_path(stage)
        assert resolved is not None, f"stage {stage!r} resolved to None"
        # The contract artifact name is system-prompt.<stage>.md.
        assert resolved.name == f"system-prompt.{stage}.md"
        # Containment: the artifact must stay inside the bridge root.
        assert resolved.is_relative_to(fake_bridge_root.resolve())


def test_resolve_stage_prompt_path_rejects_unknown_and_missing_stage(fake_bridge_root):
    """An unknown, empty, or missing stage resolves to None.

    None is the signal for "no stage artifact" — the loader then serves
    the full prompt. A typo must never resolve to some other stage's file.
    """
    _write_manifest(fake_bridge_root)
    assert bridge.resolve_stage_prompt_path("nonsense") is None
    assert bridge.resolve_stage_prompt_path("qa_") is None  # typo shape
    assert bridge.resolve_stage_prompt_path("") is None
    assert bridge.resolve_stage_prompt_path(None) is None


def test_resolve_stage_prompt_path_follows_the_manifest_not_a_hardcoded_table(
    fake_bridge_root,
):
    """The manifest IS the routing table.

    A non-default artifact directory declared by the manifest must win
    over the built-in default — otherwise the assembler and the bridge
    would look in different directories and the routing would silently
    degrade to the full prompt.
    """
    _write_manifest(fake_bridge_root, artifact_dir="generated/prompts")
    resolved = bridge.resolve_stage_prompt_path("qa")
    assert (
        resolved
        == (
            fake_bridge_root / "generated" / "prompts" / "system-prompt.qa.md"
        ).resolve()
    )


def test_resolve_stage_prompt_path_survives_a_missing_manifest(tmp_path, monkeypatch):
    """A missing manifest must not break the routing.

    The preflight gate defines the known stage set, so every known stage
    still resolves to its default artifact path; an unknown stage still
    resolves to None. Nothing raises.
    """
    home = tmp_path / "home"
    root = home / ".config" / "opencode"
    root.mkdir(parents=True)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    monkeypatch.setattr(bridge, "_bridge_root", lambda: root)
    assert not (root / "prompts" / "stage-manifest.json").exists()
    resolved = bridge.resolve_stage_prompt_path("qa")
    assert resolved is not None
    assert resolved.name == "system-prompt.qa.md"
    assert bridge.resolve_stage_prompt_path("nonsense") is None


# --- the stage-aware prompt loader ------------------------------------------


def test_load_system_prompt_serves_the_stage_artifact_when_it_exists(
    fake_bridge_root, monkeypatch
):
    """A known stage with a generated artifact serves THAT artifact."""
    _write_manifest(fake_bridge_root)
    _write_artifact(fake_bridge_root, "qa", "STAGE QA PROMPT")
    monkeypatch.delenv("BRAIN_SYSTEM_PROMPT", raising=False)
    assert bridge.load_system_prompt(stage="qa") == "STAGE QA PROMPT"


def test_load_system_prompt_falls_back_to_the_full_prompt_when_artifact_is_missing(
    fake_bridge_root, monkeypatch
):
    """A known stage whose artifact was never generated degrades to the
    full prompt: never empty, never an exception.

    The scope loss is silent by design (the Brain must not see a broken
    turn), but it is never a blank prompt.
    """
    _write_manifest(fake_bridge_root)
    monkeypatch.delenv("BRAIN_SYSTEM_PROMPT", raising=False)
    full = fake_bridge_root / "system-prompt.md"
    full.write_text("FULL PROMPT", encoding="utf-8")
    served = bridge.load_system_prompt(stage="qa")
    assert served == "FULL PROMPT"
    assert served.strip() != ""


def test_load_system_prompt_prefers_an_explicit_path_over_the_stage_artifact(
    fake_bridge_root, monkeypatch
):
    """An explicit system_prompt_path outranks the stage artifact."""
    _write_manifest(fake_bridge_root)
    _write_artifact(fake_bridge_root, "qa", "STAGE QA PROMPT")
    monkeypatch.delenv("BRAIN_SYSTEM_PROMPT", raising=False)
    explicit = fake_bridge_root / "explicit.md"
    explicit.write_text("EXPLICIT PROMPT", encoding="utf-8")
    assert bridge.load_system_prompt(str(explicit), stage="qa") == "EXPLICIT PROMPT"


def test_load_system_prompt_prefers_the_stage_artifact_over_the_env_override(
    fake_bridge_root, monkeypatch
):
    """Contract order: stage artifact → env override → full prompt.

    The stage artifact outranks the env override (the env var is the
    fallback for a stage with no artifact), and the env override still
    outranks the full prompt when no stage is requested.
    """
    _write_manifest(fake_bridge_root)
    _write_artifact(fake_bridge_root, "qa", "STAGE QA PROMPT")
    env_prompt = fake_bridge_root / "env-prompt.md"
    env_prompt.write_text("ENV PROMPT", encoding="utf-8")
    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(env_prompt))
    assert bridge.load_system_prompt(stage="qa") == "STAGE QA PROMPT"
    # Without a stage the env override still wins over the full prompt.
    assert bridge.load_system_prompt() == "ENV PROMPT"


# --- the preflight stage gate -----------------------------------------------


def test_preflight_stage_gate_admits_brainstorm_and_rejects_unknown(tmp_path):
    """``brainstorm`` joins the gate; an unknown stage string is still a
    loud rejection.

    A silently typo'd stage is worse than a refused turn, so the gate
    keeps raising ``PreflightError`` for anything outside the contract
    set (deviation D2).
    """
    assert "brainstorm" in preflight.ALLOWED_STAGES
    # The gate's set is exactly the contract stage set.
    assert set(preflight.ALLOWED_STAGES) == set(CONTRACT_STAGES)
    proj = tmp_path / "proj"
    (proj / "tasks").mkdir(parents=True)
    req = preflight.validate_request(
        task_id="1", project_root=str(proj), stage="brainstorm"
    )
    assert req.stage == "brainstorm"
    with pytest.raises(preflight.PreflightError, match="stage"):
        preflight.validate_request(task_id="1", project_root=str(proj), stage="bogus")


# --- the generated artifacts (prompt lane) ----------------------------------


def test_manifest_declares_the_contract_stage_set():
    """The manifest lists exactly the contract stages, and each stage
    carries exactly its contracted persona slice.

    QA sees the QA persona alone; planning sees the five planning seats
    (no QA, no Reviewer); brainstorming sees all seven.
    """
    if not MANIFEST.is_file():
        pytest.skip("prompts/stage-manifest.json not generated yet (prompt lane)")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    stages = data.get("stages") if isinstance(data, dict) else None
    assert isinstance(stages, dict), f"manifest declares no stage map: {sorted(data)}"
    assert set(stages) == set(CONTRACT_STAGES)
    # QA-only slice.
    assert set(_persona_slugs(stages["qa"])) == {"qa-engineer"}
    # The other single-seat stages.
    assert set(_persona_slugs(stages["implement"])) == {"senior-programmer"}
    assert set(_persona_slugs(stages["review"])) == {"code-reviewer"}
    assert set(_persona_slugs(stages["closure"])) == {"senior-programmer"}
    # Planning carries the five planning seats and neither QA nor Reviewer.
    assert set(_persona_slugs(stages["plan"])) == set(CONTRACT_PERSONAS["plan"])
    assert "qa-engineer" not in _persona_slugs(stages["plan"])
    assert "code-reviewer" not in _persona_slugs(stages["plan"])
    # Brainstorming carries all seven.
    assert set(_persona_slugs(stages["brainstorm"])) == set(ALL_PERSONAS)
    assert len(_persona_slugs(stages["brainstorm"])) == 7


def _artifact_persona_names(text):
    """Persona display names declared inside an artifact's ``<personas>`` block.

    Only the block counts: the prose around it names seats ("the seven
    seats") without declaring them, and a prose mention must not look
    like a shipped persona slice.
    """
    start = text.find("<personas>")
    end = text.find("</personas>")
    if start == -1 or end == -1 or end < start:
        return []
    block = text[start:end]
    return [match.split('"')[0] for match in _PERSONA_NAME_RE.findall(block)]


def test_stage_artifacts_carry_only_their_contract_personas():
    """The QA artifact ships the QA persona alone; planning ships the five
    planning seats and neither QA nor Reviewer; brainstorming ships all
    seven.

    This is the point of the split: a scoped artifact must not leak the
    other personas' instructions back into the turn.
    """
    artifacts = _stage_artifact_files()
    if not artifacts:
        pytest.skip("no stage artifacts generated yet (prompt lane)")
    by_stage = {}
    for path in artifacts:
        name = path.name
        if name.startswith("system-prompt.") and name.endswith(".md"):
            by_stage[name[len("system-prompt.") : -len(".md")]] = path
    assert set(by_stage) == set(CONTRACT_STAGES), (
        f"generated artifacts cover {sorted(by_stage)}, "
        f"expected {sorted(CONTRACT_STAGES)}"
    )
    for stage, slugs in CONTRACT_PERSONAS.items():
        names = _artifact_persona_names(by_stage[stage].read_text(encoding="utf-8"))
        expected = {PERSONA_NAMES[slug] for slug in slugs}
        assert set(names) == expected, (
            f"stage {stage!r} declares personas {sorted(names)}, "
            f"expected {sorted(expected)}"
        )


def test_generated_stage_artifacts_are_plugin_blind():
    """No stage artifact may name a plugin-lane tool.

    The Brain runs outside the plugin lane: a prompt that names
    ``goal_set`` or ``compact_context`` teaches the model to call tools
    it does not have.
    """
    artifacts = _stage_artifact_files()
    if not artifacts:
        pytest.skip("no stage artifacts generated yet (prompt lane)")
    for path in artifacts:
        text = path.read_text(encoding="utf-8")
        for literal in PLUGIN_LITERALS:
            assert literal not in text, (
                f"{path.name} leaks the plugin literal {literal!r}"
            )


# --- end-to-end: the stage reaches the wire --------------------------------


class _FakeResp:
    """Minimal stand-in for the httpx response object."""

    def __init__(self, status_code, text, payload):
        self.status_code = status_code
        self.text = text
        self._payload = payload
        self.headers = {"content-type": "application/json"}

    def json(self):
        return self._payload


class _FakeClient:
    """Minimal stand-in for httpx.Client that records the request body."""

    def __init__(self, payload, holder):
        self._payload = payload
        self._holder = holder

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def post(self, url, json=None, headers=None, **kwargs):
        self._holder["body"] = json
        return _FakeResp(200, "fine", self._payload)


def _stub_httpx(monkeypatch, payload, holder):
    """Install a fake httpx module so the turn never touches the network."""
    stub = types.ModuleType("httpx")
    stub.Client = lambda *a, **k: _FakeClient(payload, holder)
    stub.TimeoutException = type("TimeoutException", (Exception,), {})
    stub.TransportError = type("TransportError", (Exception,), {})

    class _Timeout:
        def __init__(self, *a, **k):
            self.args, self.kwargs = a, k

    stub.Timeout = _Timeout
    monkeypatch.setitem(sys.modules, "httpx", stub)


def _ok_payload(text="ok"):
    """Provider payload shaped like a Responses-API message."""
    return {
        "output": [
            {"type": "message", "content": [{"type": "output_text", "text": text}]}
        ]
    }


def test_preflight_rejects_unknown_stage_loudly_while_loader_degrades_to_full(
    fake_bridge_root, monkeypatch, capsys
):
    """The two unknown-stage layers must BOTH hold, and they are consistent.

    The preflight gate is the public API: an unknown stage string raises
    ``PreflightError`` so a typo fails visible instead of silently running
    unscoped. The loader is the internal API and is total: an unknown stage
    returns the full prompt and never raises. A caller that reaches the
    loader without passing the gate still gets a working prompt.
    """
    _write_manifest(fake_bridge_root)
    full = fake_bridge_root / "system-prompt.md"
    full.write_text("FULL PROMPT", encoding="utf-8")
    monkeypatch.delenv("BRAIN_SYSTEM_PROMPT", raising=False)

    # Layer 1 — the public gate rejects the unknown stage.
    with pytest.raises(preflight.PreflightError):
        preflight._check_stage("definitely-not-a-stage")

    # Layer 2 — the internal loader degrades to the full prompt.
    text = bridge.load_system_prompt(None, stage="definitely-not-a-stage")
    assert text.strip() != ""
    assert "FULL PROMPT" in text
    # The degradation is reported, not silent.
    assert capsys.readouterr().err.strip() != ""


def test_corrupt_stage_manifest_reports_on_stderr_and_degrades_to_full(
    fake_bridge_root, monkeypatch, capsys
):
    """A corrupt routing table must announce itself, not degrade silently.

    A silent degradation is indistinguishable from "this stage simply has
    no artifact", which would hide a broken manifest behind a
    working-looking turn. The turn must still succeed with the full prompt.
    """
    manifest = fake_bridge_root / "prompts" / "stage-manifest.json"
    manifest.write_text("{ this is not json", encoding="utf-8")
    full = fake_bridge_root / "system-prompt.md"
    full.write_text("FULL PROMPT", encoding="utf-8")
    monkeypatch.delenv("BRAIN_SYSTEM_PROMPT", raising=False)

    text = bridge.load_system_prompt(None, stage="qa")

    # The turn still works.
    assert "FULL PROMPT" in text
    # And the corruption is reported on stderr.
    err = capsys.readouterr().err
    assert err.strip() != ""
    assert "stage manifest" in err


def test_assembler_rejects_a_stage_with_an_empty_persona_roster(tmp_path, monkeypatch):
    """A stage that declares no persona must fail loudly, not ship a stub.

    An empty roster would produce an artifact whose ``<personas>`` block
    holds no seat at all — a prompt with no role definition. That is a
    manifest authoring error, so the assembler must refuse it.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "assemble_system_prompt",
        REPO / "scripts" / "prompt-build" / "assemble_system_prompt.py",
    )
    assembler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assembler)

    manifest = {
        "schema_version": 1,
        "common_fragments": [],
        "personas": {slug: f"personas/{slug}.md" for slug in ALL_PERSONAS},
        "stages": {"hollow": {"personas": []}},
    }
    manifest_path = tmp_path / "stage-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        assembler._stage_persona_filenames("hollow", manifest)
    assert "empty persona roster" in str(excinfo.value)


def test_every_stage_artifact_ships_the_catalog_and_the_common_core():
    """Each artifact must carry the catalog (``<auto_load>``) plus the core.

    A stage artifact is the COMMON core plus its own persona slice. If the
    catalog or a common fragment went missing during the split, the Brain
    would receive a prompt without the persona-loading rules or without its
    shared instructions — a silent capability loss that no size check
    would catch.
    """
    artifacts = _stage_artifact_files()
    if not artifacts:
        pytest.skip("stage artifacts not generated yet")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    common = manifest.get("common_fragments") or []

    for artifact in artifacts:
        text = artifact.read_text(encoding="utf-8")
        # The catalog always ships: its <auto_load> rules are the
        # persona-loading contract and must survive every stage.
        assert "<auto_load>" in text, f"{artifact.name} lost the catalog block"
        assert text.count("<auto_load>") == 1, f"{artifact.name} duplicated the catalog"
        # Every declared common fragment contributes its content. The
        # fragments are checked by their distinctive content rather than by
        # filename, because the assembler renames nothing but resolves
        # fragments by path.
        assert "<personas>" in text and "</personas>" in text
        # A common fragment that carries a top-level XML tag must be
        # present in the artifact.
        for fragment in common:
            tag = _top_level_tag(fragment)
            if tag and f"<{tag}>" in _fragment_text(fragment):
                assert f"<{tag}>" in text, (
                    f"{artifact.name} lost common fragment {fragment}"
                )
        # The artifact is never empty and never catalog-only.
        assert len(text.strip()) > 0
        assert _PERSONA_NAME_RE.search(text), f"{artifact.name} carries no persona"


def _top_level_tag(fragment_name):
    """The top-level XML tag a fragment contributes, if it has one."""
    fragment = REPO / "prompts" / "fragments" / fragment_name
    if not fragment.is_file():
        return None
    for line in fragment.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("<") and not stripped.startswith("</"):
            name = stripped[1:].split()[0].rstrip(">")
            if name and name.isidentifier():
                return name
    return None


def _fragment_text(fragment_name):
    """The content of a fragment, or an empty string when it is absent."""
    fragment = REPO / "prompts" / "fragments" / fragment_name
    if not fragment.is_file():
        return ""
    return fragment.read_text(encoding="utf-8")


def test_brain_turn_serves_the_stage_scoped_prompt(fake_bridge_root, monkeypatch):
    """End-to-end: ``brain_turn(stage="qa")`` puts the QA artifact on the
    wire.

    This is the wiring proof — the stage really reaches the loader, and
    the stage-scoped prompt (not the full prompt) is what the provider
    receives.
    """
    _write_manifest(fake_bridge_root)
    _write_artifact(fake_bridge_root, "qa", "STAGE QA PROMPT")
    full = fake_bridge_root / "system-prompt.md"
    full.write_text("FULL PROMPT", encoding="utf-8")
    monkeypatch.delenv("BRAIN_SYSTEM_PROMPT", raising=False)
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(fake_bridge_root / "sessions"))
    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
    holder = {}
    _stub_httpx(monkeypatch, _ok_payload("ok"), holder)
    target = (
        bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn") else bridge.brain_turn
    )
    result = target("adversarial QA please", stage="qa", include_bundle=False)
    assert result["output"] == "ok"
    body = json.dumps(holder["body"])
    # The stage artifact is served; the full prompt is not.
    assert "STAGE QA PROMPT" in body
    assert "FULL PROMPT" not in body
