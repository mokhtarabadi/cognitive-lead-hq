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
from pathlib import Path
from typing import Optional

from models import LoopEngineConfig


def _load_file_if_exists(path: str) -> str:
    p = Path(path)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


# Persona-specific instructions — the "what to do" for each role
PERSONA_INSTRUCTIONS = {
    "architect": """You are the Architect persona for the Cognitive Lead AI system.

Your job is to:
1. Read the task file and understand the requirements
2. Generate a detailed implementation plan (Architect's Blueprint)
3. Break down into specific file changes with acceptance criteria
4. Output a <hands_implementation_task> XML block for execution

Be specific. Every file path, every function name, every change.
Follow the project's AGENTS.md rules and conventions exactly.
Output format: XML block starting with <hands_implementation_task>.""",

    "qa_engineer": """You are the QA Engineer persona for the Cognitive Lead AI system.

Your job is to:
1. Read the task file and the code changes
2. Run tests if applicable
3. Check acceptance criteria
4. Output either PASSED or FAILED with specific feedback
5. If FAILED, describe exactly what needs to change

Be adversarial. Try to break the code. Find edge cases.
Follow the project's AGENTS.md rules and conventions exactly.
Output format: Start with PASSED or FAILED, then detailed feedback.""",

    "code_reviewer": """You are the Code Reviewer persona for the Cognitive Lead AI system.

Your job is to:
1. Review the architectural decisions
2. Check SOLID principles, naming conventions, code quality
3. Output either APPROVED or REJECTED with specific reasons
4. Focus on long-term maintainability, not just "it works"

Think like a senior engineer reviewing a PR.
Follow the project's AGENTS.md rules and conventions exactly.
Output format: Start with APPROVED or REJECTED, then detailed review.""",

    "po_closure": """You are the PO Closure persona for the Cognitive Lead AI system.

Your job is to:
1. Summarize what was accomplished
2. Verify all acceptance criteria are met
3. Generate the closure summary
4. Output READY_FOR_CLOSURE or NEEDS_WORK

Be concise and factual.
Output format: Start with READY_FOR_CLOSURE or NEEDS_WORK, then summary.""",
}


class LLMRouter:
    """Routes LLM calls to the right model based on task category."""

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

    def _resolve_model(self, category: str) -> tuple[str, Optional[str]]:
        cat_config = self.config.categories.get(category)
        if not cat_config:
            cat_config = self.config.categories.get("unspecified")
        for model in cat_config.models:
            provider = model.split("/")[0]
            env_key = f"{provider.upper()}_API_KEY"
            if os.environ.get(env_key):
                return model, cat_config.reasoning
        return self.config.default_provider, None

    def _build_system_context(self, persona: str = "architect") -> str:
        """Build XML-structured system prompt following LLM best practices.

        Structure:
        - <role>: Who the AI is (persona identity)
        - <project_rules>: Full AGENTS.md (project-specific rules)
        - <conventions>: Full conventions (coding standards)
        - <context>: System prompt excerpt (manager profile, operating principles)
        - <instructions>: What to do for this specific persona
        """
        parts = []

        # Role: who the AI is
        role_map = {
            "architect": "the Architect — a senior software architect who generates implementation plans",
            "qa_engineer": "the QA Engineer — an adversarial tester who tries to break code",
            "code_reviewer": "the Code Reviewer — a senior engineer who checks architecture and quality",
            "po_closure": "the PO Closure — a product owner who summarizes and verifies completion",
        }
        role = role_map.get(persona, role_map["architect"])
        parts.append(f"<role>You are {role} for the Cognitive Lead AI system.</role>")

        # Project rules: FULL AGENTS.md
        if self.agents_md:
            parts.append(f"<project_rules>\n{self.agents_md}\n</project_rules>")

        # Conventions: FULL conventions
        if self.conventions:
            parts.append(f"<conventions>\n{self.conventions}\n</conventions>")

        # Context: system prompt (full — no truncation)
        if self.system_prompt:
            parts.append(f"<context>\n{self.system_prompt}\n</context>")

        # Instructions: persona-specific
        instructions = PERSONA_INSTRUCTIONS.get(persona, PERSONA_INSTRUCTIONS["architect"])
        parts.append(f"<instructions>\n{instructions}\n</instructions>")

        return "\n\n".join(parts)

    def route_plan(self, task_content: str, category: str = "unspecified") -> dict:
        model, reasoning = self._resolve_model(category)
        return {
            "model": model, "reasoning": reasoning,
            "system": self._build_system_context("architect"),
            "user": f"Generate implementation plan:\n\n{task_content}",
            "temperature": 0.3,
        }

    def route_qa(self, task_content: str, diff: str = "") -> dict:
        model, reasoning = self._resolve_model("deep")
        return {
            "model": model, "reasoning": reasoning,
            "system": self._build_system_context("qa_engineer"),
            "user": f"Review this task and changes:\n\n{task_content}\n\n## Diff\n\n{diff}",
            "temperature": 0.1,
        }

    def route_review(self, task_content: str, qa_report: str = "") -> dict:
        model, reasoning = self._resolve_model("deep")
        return {
            "model": model, "reasoning": reasoning,
            "system": self._build_system_context("code_reviewer"),
            "user": f"Review this task:\n\n{task_content}\n\n## QA Report\n\n{qa_report}",
            "temperature": 0.2,
        }

    def call_llm(self, routing: dict) -> str:
        """Call LLM via litellm with fallback chain."""
        try:
            import litellm
            response = litellm.completion(
                model=routing["model"],
                messages=[
                    {"role": "system", "content": routing["system"]},
                    {"role": "user", "content": routing["user"]},
                ],
                temperature=routing.get("temperature", 0.3),
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except ImportError:
            return f"[LLM ERROR] litellm not installed. Run: pip install litellm"
        except Exception as e:
            return f"[LLM ERROR] {str(e)}"
