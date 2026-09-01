"""
LLM Router v2 — category-based model routing via litellm.

XML-structured system prompts following best practices from OpenAI, Anthropic, and Google:
- System prompt = identity + rules + context (the "who" and "how")
- User message = task + data (the "what")
- XML tags for clear structure (<role>, <project_rules>, <conventions>, <context>, <instructions>)
- FULL files sent — no truncation (higher token cost < hallucination cost)

Reads system-prompt.md + AGENTS.md + docs/conventions.md on every invocation.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from models import LoopEngineConfig
from personas import load_personas


def _load_file_if_exists(path: str) -> str:
    p = Path(path)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


# Pipeline stage → Manager-defined persona (prompts/fragments/06-personas.md).
# PO Closure is NOT a separate persona (G1 resolution): closure review reuses
# the Code Reviewer persona, whose behavior defines the PO-review step.
STAGE_PERSONAS = {
    "architect": "Software Architect",
    "qa_engineer": "QA Engineer",
    "code_reviewer": "Code Reviewer",
    "po_closure": "Code Reviewer",
}


class LLMRouter:
    """Routes LLM calls to the right model based on task category.

    Persona instructions are derived at runtime from the Manager's prompt
    fragments — zero hardcoded persona bodies in this file. Editing a fragment
    changes engine behavior on next start.
    """

    def __init__(self, config: LoopEngineConfig, workspace_root: str = "."):
        self.config = config
        self.workspace_root = Path(workspace_root)
        # Load FULL files — no truncation (higher token cost < hallucination cost)
        self.system_prompt = _load_file_if_exists(
            str(self.workspace_root / config.system_prompt_path))
        self.agents_md = _load_file_if_exists(
            str(self.workspace_root / config.agmd_path))
        self.conventions = _load_file_if_exists(
            str(self.workspace_root / config.conventions_path))
        # All 7 operational personas from prompts/fragments/06-personas.md
        self.personas = load_personas(str(self.workspace_root))

    def _resolve_model(self, category: str,
                       stack_profile: Optional[Any] = None) -> tuple[str, Optional[str]]:
        """Resolve a model for a category via the 3-tier hierarchy (LE-3).

        Tier 1 — Stack-Preferred Models: consult ``stack_profile.model_preferences``
        (or a dict's ``"model_preferences"`` key). Match the exact category first,
        then the wildcard ``"*"``. The first model whose ``{PROVIDER}_API_KEY`` env
        var is present wins; reasoning level comes from the global category config.
        Tier 2 — Global Category Models: existing category fallback chain.
        Tier 3 — Global Default: ``(default_provider, None)``.
        """
        # Tier 1: Stack-Preferred Models
        prefs: dict = {}
        if stack_profile is not None:
            if isinstance(stack_profile, dict):
                prefs = stack_profile.get("model_preferences", {}) or {}
            else:
                prefs = getattr(stack_profile, "model_preferences", {}) or {}
        if prefs:
            candidate_models = prefs.get(category) or prefs.get("*") or []
            for model in candidate_models:
                provider = model.split("/")[0]
                env_key = f"{provider.upper()}_API_KEY"
                if os.environ.get(env_key):
                    cat_config = self.config.categories.get(category)
                    if not cat_config:
                        cat_config = self.config.categories.get("unspecified")
                    reasoning = cat_config.reasoning if cat_config else None
                    return model, reasoning

        # Tier 2: Global Category Models
        cat_config = self.config.categories.get(category)
        if not cat_config:
            cat_config = self.config.categories.get("unspecified")
        for model in cat_config.models:
            provider = model.split("/")[0]
            env_key = f"{provider.upper()}_API_KEY"
            if os.environ.get(env_key):
                return model, cat_config.reasoning

        # Tier 3: Global Default
        return self.config.default_provider, None

    def _load_memory_context(self) -> str:
        """Load project memory shards via direct file read.

        Replicates agents/cognitive-executor.md 'Context Bootstrapping & Memory Protocol':
        - scans .opencode/memory/{namespace}/{key}.md (mirrors mcp-memory-server shards)
        - uses index.md implicitly via glob (index is derived state)
        - returns XML-serialized entries for system context injection
        - caps per-entry at 3000 chars to avoid token bloat
        """
        memory_dir = self.workspace_root / ".opencode" / "memory"
        if not memory_dir.exists():
            return ""
        parts: list[str] = []
        for mem_file in memory_dir.rglob("*.md"):
            if mem_file.name == "index.md":
                continue
            try:
                content = mem_file.read_text(encoding="utf-8").strip()
                if not content:
                    continue
                rel = mem_file.relative_to(memory_dir)
                namespace = rel.parent.name if len(rel.parts) > 1 else "unknown"
                key = mem_file.stem
                if len(content) > 3000:
                    content = content[:3000] + "\n...[truncated]"
                parts.append(f'<memory namespace="{namespace}" key="{key}">\n{content}\n</memory>')
            except Exception:
                continue
        return "\n\n".join(parts)

    def _build_system_context(self, persona: str = "architect") -> str:
        """Build XML-structured system prompt.

        Persona identity + instructions come verbatim from the Manager's
        fragments; this method only supplies structural glue.
        """
        persona_name = STAGE_PERSONAS.get(persona, persona)
        data = self.personas.get(persona_name)

        if data:
            role = (
                f"You are {persona_name} for the Cognitive Lead AI system, "
                f"operating under the Manager's system prompt."
            )
            instructions = (
                f"<trigger>{data['trigger']}</trigger>\n"
                f"<duty>{data['duty']}</duty>\n"
                f"<behavior>{data['behavior']}</behavior>"
            )
        else:
            # Unknown persona requested — fail loudly rather than impersonate.
            raise ValueError(
                f"Persona '{persona_name}' not found in "
                f"prompts/fragments/06-personas.md. Available: "
                f"{sorted(self.personas)}")

        parts = [f"<role>{role}</role>"]

        # Project rules: FULL AGENTS.md
        if self.agents_md:
            parts.append(f"<project_rules>\n{self.agents_md}\n</project_rules>")

        # Conventions: FULL conventions
        if self.conventions:
            parts.append(f"<conventions>\n{self.conventions}\n</conventions>")

        # Context: system prompt (full — no truncation)
        if self.system_prompt:
            parts.append(f"<context>\n{self.system_prompt}\n</context>")

        # Memory: project-mandatory context from .opencode/memory
        # Replicates Context Bootstrapping & Memory Protocol in agents/cognitive-executor.md
        memory_context = self._load_memory_context()
        if memory_context:
            parts.append(f"<memory_context>\n{memory_context}\n</memory_context>")

        # Instructions: persona definition verbatim from the fragment
        parts.append(f"<instructions>\n{instructions}\n</instructions>")

        return "\n\n".join(parts)

    def route_with_persona(self, persona_name: str, user_content: str,
                           temperature: float = 0.3,
                           category: str = "deep",
                           stack_profile: Optional[Any] = None) -> dict:
        """Route a call as ANY Manager-defined persona (all 7 invocable)."""
        model, reasoning = self._resolve_model(category, stack_profile=stack_profile)
        return {
            "model": model, "reasoning": reasoning,
            "system": self._build_system_context(persona_name),
            "user": user_content,
            "temperature": temperature,
        }

    def route_plan(self, task_content: str, category: str = "unspecified",
                   extra_context: str = "",
                   stack_profile: Optional[Any] = None) -> dict:
        user = (
            f"Generate the DIRECT, complete implementation blueprint for this task.\n"
            f"RULES:\n"
            f"- Keep reasoning log brief (< 150 words).\n"
            f"- Provide concrete, file-level implementation steps with exact code/commands.\n"
            f"- Do not exceed token limits or output placeholder stubs.\n\n"
            f"## Task Content:\n{task_content}"
        )
        if extra_context:
            user += f"\n\nIncorporate this brainstorming session output:\n\n{extra_context}"
        model, reasoning = self._resolve_model(category, stack_profile=stack_profile)
        system = self._build_system_context("architect")
        system += (
            "\n\n<deliverable>\n"
            "PLANNING output MUST be the direct implementation blueprint: "
            "concrete file-level steps, exact symbols, and verification "
            "commands. Never respond with meta-requests for discovery or "
            "clarification questions to the caller — produce the blueprint "
            "itself.\n"
            "</deliverable>"
        )
        return {
            "model": model, "reasoning": reasoning,
            "system": system,
            "user": user,
            "temperature": 0.3,
        }

    def route_qa(self, task_content: str, diff: str = "", toolchain_evidence: str = "",
                 stack_profile: Optional[Any] = None) -> dict:
        model, reasoning = self._resolve_model("deep", stack_profile=stack_profile)
        user = f"Review this task and changes:\n\n{task_content}\n\n## Diff\n\n{diff}"
        if toolchain_evidence:
            user += f"\n\n## Toolchain Verification\n\n{toolchain_evidence}"
        return {
            "model": model, "reasoning": reasoning,
            "system": self._build_system_context("qa_engineer"),
            "user": user,
            "temperature": 0.1,
        }

    def route_review(self, task_content: str, qa_report: str = "",
                     stack_profile: Optional[Any] = None) -> dict:
        model, reasoning = self._resolve_model("deep", stack_profile=stack_profile)
        return {
            "model": model, "reasoning": reasoning,
            "system": self._build_system_context("code_reviewer"),
            "user": f"Review this task:\n\n{task_content}\n\n## QA Report\n\n{qa_report}",
            "temperature": 0.2,
        }

    def call_llm(self, routing: dict) -> str:
        """Call LLM via litellm with fallback chain.

        Raises RuntimeError on failure — an error string returned as a plan
        would flow downstream and get approved/reviewed as if it were real
        output. Callers (pipeline guard) convert the exception into CRASHED.
        """
        try:
            import litellm
            kwargs = {
                "model": routing["model"],
                "messages": [
                    {"role": "system", "content": routing["system"]},
                    {"role": "user", "content": routing["user"]},
                ],
                "temperature": routing.get("temperature", 0.3),
                "max_tokens": 8192,
            }
            reasoning = routing.get("reasoning")
            if reasoning:
                kwargs["reasoning_effort"] = reasoning
            response = litellm.completion(**kwargs)
            msg = response.choices[0].message
            # Extract content or fallback to reasoning_content for thinking models
            content = getattr(msg, "content", None) or ""
            if not content:
                reasoning = getattr(msg, "reasoning_content", None) or getattr(msg, "reasoning", None)
                if reasoning:
                    content = str(reasoning)
                else:
                    content = str(msg)
            content = content.strip()

            # Debug telemetry (HOTFIX-03): raw request/response logging.
            # Opt-in ONLY via LOOP_ENGINE_DEBUG=1 — zero impact in normal runs.
            if os.environ.get("LOOP_ENGINE_DEBUG") == "1":
                try:
                    log_dir = Path(__file__).resolve().parent / "logs"
                    log_dir.mkdir(parents=True, exist_ok=True)
                    entry = (
                        f"\n===== [{datetime.now(timezone.utc).isoformat(timespec='seconds')}Z] "
                        f"model={routing.get('model')} =====\n"
                        f"--- SYSTEM ---\n{routing.get('system')}\n"
                        f"--- USER ---\n{routing.get('user')}\n"
                        f"--- RESPONSE ---\n{content}\n"
                        f"===== END =====\n"
                    )
                    with open(log_dir / "llm_requests.log", "a", encoding="utf-8") as f:
                        f.write(entry)
                except Exception as log_e:
                    print(f"[router] debug telemetry log error: {log_e}")

            return content
        except ImportError as e:
            raise RuntimeError(
                f"litellm not installed. Run: pip install litellm ({e})") from e
        except Exception as e:
            raise RuntimeError(f"LLM call failed for model "
                               f"{routing.get('model')}: {e}") from e
