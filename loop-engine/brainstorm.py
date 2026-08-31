"""
BrainstormStage — first-class Phase 1.5 Multi-Agent Brainstorming Loop.

Implements prompts/fragments/12-brainstorming_protocol.md + the brainstorm-swarm
skill execution rules:
1. Independent analysis — six parallel persona calls, zero cross-contamination.
2. Conflict resolution — synthesis MUST document contradictions explicitly.
3. Minimum output — each persona produces >= 3 concrete observations.
4. Grounding — reasoning anchored in the task content.
5. Output format — verbatim <brainstorming_session> schema from the fragment.
"""

import asyncio
from pathlib import Path

from models import LoopEngineConfig
from router import LLMRouter
from personas import load_swarm_personas, load_brainstorm_schema

# Protocol mechanics from the brainstorm-swarm skill (not persona definitions).
_INDEPENDENCE_RULE = (
    "You are one of six expert personas in an independent brainstorming swarm. "
    "Produce your OWN analysis without reference to any other persona. "
    "Ground every point in the problem description — no invented scenarios. "
    "Provide at least 3 concrete observations or recommendations."
)

_SYNTHESIS_RULE = (
    "Synthesize the six independent persona analyses below into a single "
    "<brainstorming_session> report that EXACTLY follows the provided schema. "
    "Where two personas give contradictory advice, you MUST document the "
    "conflict explicitly under <conflict_resolution> and explain the resolution."
)


class BrainstormStage:
    """Six-persona parallel brainstorm with schema-enforced synthesis."""

    def __init__(self, config: LoopEngineConfig, router: LLMRouter,
                 workspace_root: str = "."):
        self.config = config
        self.router = router
        self.swarm = load_swarm_personas(workspace_root)
        self.schema = load_brainstorm_schema(workspace_root)

    @staticmethod
    def should_trigger(task_content: str) -> bool:
        """Trigger on explicit brainstorming requests (Manager rule)."""
        lowered = task_content.lower()
        return "brainstorm" in lowered or "<brainstorming_session>" in lowered

    def _persona_routing(self, name: str, meta: dict, topic: str) -> dict:
        model, reasoning = self.router._resolve_model("deep")
        system = (
            f"<role>You are the {name} persona of a multi-expert brainstorming "
            f"swarm for the Cognitive Lead AI system.</role>\n"
            f"<focus>{meta.get('focus', '')}</focus>\n"
            f"<output_requirements>{meta.get('output', '')}</output_requirements>\n"
            f"<rules>{_INDEPENDENCE_RULE}</rules>"
        )
        return {
            "model": model, "reasoning": reasoning,
            "system": system,
            "user": f"Brainstorm topic / problem description:\n\n{topic}",
            "temperature": 0.4,
        }

    async def _call(self, name: str, meta: dict, topic: str):
        routing = self._persona_routing(name, meta, topic)
        text = await asyncio.to_thread(self.router.call_llm, routing)
        return name, text

    async def run(self, topic: str) -> dict:
        """Run six independent persona calls in parallel, then synthesize."""
        if not self.swarm:
            raise RuntimeError(
                "Swarm personas not loaded — brainstorm fragment missing?")

        responses = await asyncio.gather(
            *(self._call(name, meta, topic) for name, meta in self.swarm.items())
        )
        responses_dict = dict(responses)

        synthesis_system = (
            f"<role>You are the Orchestrator synthesizing a multi-persona "
            f"brainstorming session.</role>\n"
            f"<rules>{_SYNTHESIS_RULE}</rules>\n"
            f"<output_schema>\n{self.schema}\n</output_schema>"
        )
        persona_blocks = "\n".join(
            f"<response persona=\"{name}\">\n{text}\n</response>"
            for name, text in responses_dict.items()
        )
        synthesis_routing = {
            "model": self.router._resolve_model("deep")[0],
            "reasoning": self.router._resolve_model("deep")[1],
            "system": synthesis_system,
            "user": (f"Topic:\n{topic}\n\nIndependent persona analyses:\n"
                     f"{persona_blocks}"),
            "temperature": 0.2,
        }
        session_xml = await asyncio.to_thread(
            self.router.call_llm, synthesis_routing)

        return {
            "session": session_xml,
            "responses": responses_dict,
            "personas": list(responses_dict.keys()),
        }
