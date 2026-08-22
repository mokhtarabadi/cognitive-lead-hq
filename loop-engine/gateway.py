"""
Approval Gateway — Telegram inline keyboard for Manager sign-off.

ZAC enforced: no task proceeds without explicit Manager approval.
Uses inline keyboard with Approve/Reject buttons.
Handles callback queries from Telegram.
"""

import asyncio
import os
from typing import Optional

from models import LoopEngineConfig


class ApprovalGateway:
    """Telegram-based approval gate for Plan and Closure."""

    def __init__(self, config: LoopEngineConfig):
        self.config = config
        self.pending: dict[str, asyncio.Event] = {}
        self.results: dict[str, bool] = {}
        self._bot = None

    def _get_bot(self):
        """Lazy-init Telegram bot."""
        if self._bot is None:
            token = os.environ.get(self.config.approval.bot_token_env, "")
            if not token:
                raise ValueError(f"Env var {self.config.approval.bot_token_env} not set")
            from telegram import Bot
            self._bot = Bot(token=token)
        return self._bot

    async def request_approval(self, task_id: int, stage: str, content: str) -> bool:
        """Send approval request with inline keyboard. Blocks until response."""
        key = f"{task_id}:{stage}"

        try:
            bot = self._get_bot()
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Approve", callback_data=f"approve:{key}"),
                    InlineKeyboardButton("Reject", callback_data=f"reject:{key}"),
                ]
            ])

            msg = (
                f"**{stage}** — Task #{task_id}\n\n"
                f"{content[:1500]}\n\n"
                f"Approve or Reject?"
            )

            await bot.send_message(
                chat_id=self.config.approval.chat_id,
                text=msg,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )

        except (ImportError, ValueError) as e:
            print(f"[gateway] Telegram unavailable: {e}")
            print(f"[gateway] SECURITY: Approval for task {task_id} DENIED (no auto-grant)")
            return False

        except Exception as e:
            print(f"[gateway] Telegram error: {e}")
            print(f"[gateway] SECURITY: Approval for task {task_id} DENIED (no auto-grant)")
            return False

        # Wait for Manager response
        event = asyncio.Event()
        self.pending[key] = event
        self.results[key] = False  # default: rejected

        try:
            await asyncio.wait_for(event.wait(), timeout=self.config.approval.timeout_seconds)
        except asyncio.TimeoutError:
            print(f"[gateway] Approval timeout for task {task_id} ({stage})")
            self.pending.pop(key, None)
            return False

        result = self.results.pop(key, False)
        self.pending.pop(key, None)
        return result

    def handle_callback(self, callback_data: str) -> Optional[str]:
        """Handle Telegram callback query. Returns acknowledgment message."""
        if not callback_data.startswith(("approve:", "reject:")):
            return None

        action, key = callback_data.split(":", 1)

        if key in self.pending:
            if action == "approve":
                self.results[key] = True
                self.pending[key].set()
                return f"Approved. Task will proceed."
            else:
                self.results[key] = False
                self.pending[key].set()
                return f"Rejected. Task will not proceed."

        return None  # stale callback
