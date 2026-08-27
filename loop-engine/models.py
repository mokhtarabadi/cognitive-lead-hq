"""
Pydantic models for the Cognitive Loop Engine.

Validates all configuration and runtime data structures.
Inspired by OMO's Zod schema system (36 schema files) but using Pydantic for Python.
"""

from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field


# --- Enums ---

class TaskState(str, Enum):
    """Pipeline states for a task. Mirrors the state machine in AGENTS.md."""
    BACKLOG = "backlog"
    PENDING_TRIGGER = "pending_trigger"
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    IMPLEMENTING = "implementing"
    QA = "qa"
    REVIEW = "review"
    AWAITING_CLOSURE = "awaiting_closure"
    CLOSED = "closed"
    QA_REJECTED = "qa_rejected"
    CRASHED = "crashed"
    ABORTED = "aborted"


class ProviderPriority(BaseModel):
    """Priority-ordered model chain for a category."""
    models: list[str] = Field(..., min_length=1, description="Ordered fallback models: provider/model")
    reasoning: Optional[str] = Field(None, description="Reasoning level override")


class CategoryConfig(BaseModel):
    """Category-based model routing — ported from OMO's visual-engineering/deep/quick/ultrabrain."""
    models: list[str] = Field(..., min_length=1)
    reasoning: Optional[str] = None
    description: Optional[str] = None


class ProviderConcurrency(BaseModel):
    """Max concurrent requests per provider — prevents cost spiral."""
    anthropic: int = 3
    openai: int = 3
    opencode: int = 10
    zai: int = 10
    kimi: int = 5


class ApprovalConfig(BaseModel):
    """Telegram approval gateway settings."""
    bot_token_env: str = Field("TELEGRAM_BOT_TOKEN", description="Env var name for bot token")
    chat_id: int = Field(..., description="Telegram chat ID for Manager")
    timeout_seconds: int = 3600  # 1 hour to respond


class IdleConfig(BaseModel):
    """Auto-continue settings — inspired by OpenCode Goal Plugin's no-progress detection."""
    thinking_timeout_seconds: int = 60  # Phase 1: thinking (no bash running)
    executing_timeout_seconds: int = 900  # Phase 2: bash running (15 min)
    max_retries: int = 5
    no_progress_threshold: int = 50  # token threshold for no-progress
    no_progress_turns_before_pause: int = 2
    min_delay_seconds: float = 2.0  # cooldown between continue attempts


class LoopEngineConfig(BaseModel):
    """Root configuration — loop-engine.jsonc."""
    # Providers
    default_provider: str = "gemini/gemini-2.5-flash"
    categories: dict[str, CategoryConfig] = Field(default_factory=lambda: {
        "quick": CategoryConfig(
            models=["kimi/kimi-k3"],
            description="Single-file changes, typos, quick fixes"
        ),
        "deep": CategoryConfig(
            models=["openai/gpt-5.6-sol", "gemini/gemini-2.5-pro"],
            reasoning="medium",
            description="Autonomous research + execution"
        ),
        "visual": CategoryConfig(
            models=["anthropic/claude-opus-5", "kimi/kimi-k3"],
            reasoning="max",
            description="Frontend, UI/UX, design"
        ),
        "unspecified": CategoryConfig(
            models=["gemini/gemini-2.5-flash", "kimi/kimi-k3"],
            description="Default — anything not matched"
        ),
    })
    provider_concurrency: ProviderConcurrency = Field(default_factory=ProviderConcurrency)

    # Executor
    max_parallel_tasks: int = Field(1, ge=1, le=4, description="Max concurrent Hands sessions")
    idle: IdleConfig = Field(default_factory=IdleConfig)

    # Approval
    approval: ApprovalConfig

    # QA
    max_qa_retries: int = Field(3, ge=1, le=10)
    evidence_dir: str = "loop-engine/evidence"

    # Task Entry Trigger Gate
    trigger_mode: Literal["telegram_button", "command_only", "auto"] = Field(
        "telegram_button",
        description="How tasks enter the execution loop: "
                    "'telegram_button' = admin taps Start in Telegram; "
                    "'command_only' = admin runs /run <id>; "
                    "'auto' = legacy auto-pickup on file detection."
    )
    auto_start_on_boot: bool = Field(
        False,
        description="If True, existing backlog tasks run immediately on daemon boot. "
                    "If False, they are registered as PENDING_TRIGGER and await admin action."
    )

    # Paths
    system_prompt_path: str = "system-prompt.md"
    tasks_dir: str = "tasks"
    agmd_path: str = "AGENTS.md"
    conventions_path: str = "docs/conventions.md"
