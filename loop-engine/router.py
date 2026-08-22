"""
LLM Router v2 — category-based model routing via litellm.

Inspired by OMO's visual-engineering/deep/quick/ultrabrain category system:
- Category routing: quick -> kimi-k3, deep -> gpt-5.6-sol, visual -> opus-5
- Fallback chains: ordered model list per category
- Provider concurrency caps: prevents cost spiral

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


class LLMRouter:
    """Routes LLM calls to the right model based on task category."""

    def __init__(self, config: LoopEngineConfig, workspace_root: str = "."):
        self.config = config
        self.workspace_root = Path(workspace_root)
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
        parts = []
        # Send FULL AGENTS.md and conventions — they're the project rules
        if self.agents_md:
            parts.append(f"# Project Rules (AGENTS.md)\n\n{self.agents_md}")
        if self.conventions:
            parts.append(f"# Conventions\n\n{self.conventions}")
        # System prompt: send first 10k chars (role + manager profile + key rules)
        # The full 75k is for the Brain, not for daemon LLM calls
        if self.system_prompt:
            parts.append(f"# System Context\n\n{self.system_prompt[:10000]}")

        personas = {
            "architect": "You are the Architect. Generate a detailed implementation plan with specific file changes, functions, and acceptance criteria. Output a <hands_implementation_task> XML block.",
            "qa_engineer": "You are the QA Engineer. Be adversarial. Try to break the code. Output PASSED or FAILED with specific feedback.",
            "code_reviewer": "You are the Code Reviewer. Check SOLID, naming, quality. Output APPROVED or REJECTED.",
            "po_closure": "You are the PO. Summarize what was done. Output READY_FOR_CLOSURE or NEEDS_WORK.",
        }
        parts.append(personas.get(persona, personas["architect"]))
        return "\n\n---\n\n".join(parts)

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
