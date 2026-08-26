"""Characterization tests for Task 115 — full persona coverage + brainstorming.

Covers:
- personas loader: 7 operational personas + 6 swarm personas + output schema
- router: fragment-derived context (zero hardcoded persona bodies), unknown
  persona fails loudly, route_with_persona invocable for all 7
- qa_engine.decide: persona-defined token vocabularies
- BrainstormStage: trigger detection, six INDEPENDENT parallel calls,
  schema-enforced synthesis
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

REPO_ROOT = str(Path(__file__).resolve().parent.parent)

from models import LoopEngineConfig

EXPECTED_PERSONAS = {
    "Software Architect", "UI/UX Designer", "Senior Programmer",
    "Project Planner", "Sprint Strategist", "QA Engineer", "Code Reviewer",
}
EXPECTED_SWARM = {
    "system_architect", "security_engineer", "product_manager",
    "business_strategist", "legal_advisor", "critical_thinker",
}


def _cfg():
    return LoopEngineConfig(approval={"chat_id": 123})


# --- personas loader ---

def test_load_personas_seven_defined():
    from personas import load_personas
    personas = load_personas(REPO_ROOT)
    assert set(personas.keys()) == EXPECTED_PERSONAS
    for p in personas.values():
        assert p["trigger"] and p["duty"] and p["behavior"]


def test_load_swarm_six():
    from personas import load_swarm_personas
    swarm = load_swarm_personas(REPO_ROOT)
    assert set(swarm.keys()) == EXPECTED_SWARM
    for s in swarm.values():
        assert s["focus"] and s["output"]


def test_load_brainstorm_schema():
    from personas import load_brainstorm_schema
    schema = load_brainstorm_schema(REPO_ROOT)
    assert "<brainstorming_session>" in schema
    assert "final_recommendation" in schema
    assert "conflict_resolution" in schema


# --- router fragment-derivation ---

def test_router_context_uses_fragment_verbatim():
    from router import LLMRouter
    router = LLMRouter(_cfg(), workspace_root=REPO_ROOT)
    ctx = router._build_system_context("qa_engineer")
    # Verbatim duty text from prompts/fragments/12-personas.md
    assert "Adversarial testing, boundary analysis" in ctx
    assert "QA Engineer" in ctx


def test_router_unknown_persona_raises():
    from router import LLMRouter
    router = LLMRouter(_cfg(), workspace_root=REPO_ROOT)
    try:
        router._build_system_context("PO Closure")
        assert False, "Should have raised: PO Closure is not a defined persona"
    except ValueError:
        pass


def test_router_source_has_zero_hardcoded_persona_bodies():
    source = (Path(__file__).parent / "router.py").read_text(encoding="utf-8")
    for marker in [
        "You are the Architect persona",
        "You are the QA Engineer persona",
        "You are the Code Reviewer persona",
        "You are the PO Closure persona",
        "PERSONA_INSTRUCTIONS",
    ]:
        assert marker not in source, f"Hardcoded persona remnant: {marker}"


def test_route_with_persona_all_seven_invocable():
    from router import LLMRouter
    router = LLMRouter(_cfg(), workspace_root=REPO_ROOT)
    for name in EXPECTED_PERSONAS:
        routing = router.route_with_persona(name, "Do the thing")
        assert routing["model"]
        assert "Do the thing" in routing["user"]


def test_stage_map_resolves():
    from router import STAGE_PERSONAS
    assert STAGE_PERSONAS["architect"] == "Software Architect"
    assert STAGE_PERSONAS["qa_engineer"] == "QA Engineer"
    assert STAGE_PERSONAS["code_reviewer"] == "Code Reviewer"
    # G1 resolution: closure reuses Code Reviewer, no invented persona
    assert STAGE_PERSONAS["po_closure"] == "Code Reviewer"


# --- decision tokens (G2 alignment) ---

def test_decide_persona_qa_tokens():
    from qa_engine import decide
    assert decide("Status: QA_PASSED. All boundaries hold.") == "PASS"
    assert decide("Status: QA_REJECTED. Race condition found.") == "FAIL"


def test_decide_persona_reviewer_tokens():
    from qa_engine import decide
    assert decide("APPROVED_WITH_CHANGES: minor naming issues.") == "PASS"
    assert decide("REJECTED_NEEDS_FIXES: blueprint divergence.") == "FAIL"
    assert decide("PO_REVIEW_PENDING — technically approved.") == "PASS"


def test_decide_quoted_token_still_first_occurrence_wins():
    from qa_engine import decide
    report = ("FAILED: criteria demand APPROVED_WITH_CHANGES at minimum, "
              "but tests crash.")
    assert decide(report) == "FAIL"


# --- BrainstormStage ---

def test_brainstorm_should_trigger():
    from brainstorm import BrainstormStage
    assert BrainstormStage.should_trigger("let's brainstorm on caching")
    assert BrainstormStage.should_trigger("See <brainstorming_session> guidelines")
    assert not BrainstormStage.should_trigger("Fix the login null pointer")


class _RecordingRouter:
    """Sync stub — records every call_llm routing; called via to_thread."""

    def __init__(self):
        self.calls = []

    def _resolve_model(self, category):
        return "stub/model", None

    def call_llm(self, routing):
        self.calls.append(routing)
        if "Orchestrator synthesizing" in routing["system"]:
            return ("<brainstorming_session><summary>ok</summary>"
                    "<final_recommendation>do X</final_recommendation>"
                    "</brainstorming_session>")
        # Persona call — extract own name from role line
        for name in EXPECTED_SWARM:
            if f"the {name} persona" in routing["system"]:
                return f"analysis-by-{name}"
        return "unknown-analysis"


def test_brainstorm_run_six_independent_calls_plus_synthesis():
    from brainstorm import BrainstormStage
    stub = _RecordingRouter()
    stage = BrainstormStage(_cfg(), stub, workspace_root=REPO_ROOT)
    result = asyncio.run(stage.run("Should we add Redis caching?"))

    persona_calls = [c for c in stub.calls
                     if "Orchestrator synthesizing" not in c["system"]]
    synth_calls = [c for c in stub.calls
                   if "Orchestrator synthesizing" in c["system"]]

    assert len(stub.calls) == 7          # 6 personas + 1 synthesis
    assert len(persona_calls) == 6
    assert len(synth_calls) == 1
    assert set(result["responses"].keys()) == EXPECTED_SWARM
    assert "<brainstorming_session>" in result["session"]

    # Independence: no persona call sees another persona's analysis
    for c in persona_calls:
        assert "analysis-by-" not in c["user"]

    # Synthesis receives ALL six analyses + the verbatim schema
    synth_user = synth_calls[0]["user"]
    for name in EXPECTED_SWARM:
        assert f'persona="{name}"' in synth_user
        assert f"analysis-by-{name}" in synth_user
    assert "<output_schema>" in synth_calls[0]["system"]


def test_brainstorm_missing_swarm_fails_loudly():
    import tempfile
    from brainstorm import BrainstormStage
    import personas as personas_mod
    with tempfile.TemporaryDirectory() as tmp:
        # Simulate genuinely missing fragments: re-anchor both lookup roots
        original_root = personas_mod._REPO_ROOT
        personas_mod._REPO_ROOT = Path(tmp)
        try:
            stage = BrainstormStage(_cfg(), _RecordingRouter(), workspace_root=tmp)
            try:
                asyncio.run(stage.run("topic"))
                assert False, "Should have raised: no swarm personas loaded"
            except RuntimeError:
                pass
        finally:
            personas_mod._REPO_ROOT = original_root


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
