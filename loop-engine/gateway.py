"""
Approval Gateway — Telegram inline keyboard for Manager sign-off.

ZAC enforced: no task proceeds without explicit Manager approval.
Uses inline keyboard with Approve/Reject buttons.
Handles callback queries from Telegram.

Extended with Task Entry Trigger Gate:
- Sends trigger cards with [🚀 Start Execution] / [⏸️ Hold] buttons.
- Parses /run, /start, /tasks, /backlog text commands.
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
        self._poller_task: Optional[asyncio.Task] = None
        self._daemon = None  # set by daemon.py after init
        self._state = None   # set by daemon.py after init

    def set_daemon(self, daemon):
        """Register the daemon instance for trigger callbacks."""
        self._daemon = daemon

    def set_state(self, state):
        """Register the state machine for /tasks queries."""
        self._state = state

    def _get_bot(self):
        """Lazy-init Telegram bot."""
        if self._bot is None:
            token = os.environ.get(self.config.approval.bot_token_env, "")
            if not token:
                raise ValueError(f"Env var {self.config.approval.bot_token_env} not set")
            from telegram import Bot
            self._bot = Bot(token=token)
        return self._bot

    async def _poll_loop(self):
        """Poll Telegram for callback queries and text commands, dispatching to handlers.

        Without this loop, inline Approve/Reject/Trigger buttons are dead UI.
        Also parses /run, /start, /tasks, /backlog text commands.
        Runs while any approval is pending or daemon is active.
        """
        offset = None
        while self.pending or self._daemon is not None:
            try:
                updates = await self._bot.get_updates(offset=offset, timeout=10)
            except Exception as e:
                print(f"[gateway] Update poll error: {e}")
                await asyncio.sleep(3)
                continue
            for u in updates:
                offset = u.update_id + 1
                cq = getattr(u, "callback_query", None)
                if cq is not None and cq.data:
                    ack = self.handle_callback(cq.data)
                    if ack:
                        try:
                            await self._bot.answer_callback_query(cq.id, text=ack)
                        except Exception as e:
                            print(f"[gateway] answer_callback_query failed: {e}")
                    continue

                # Text command parsing
                msg = getattr(u, "message", None)
                if msg is not None and msg.text:
                    await self._handle_text_command(msg)

    def _ensure_poller(self):
        """Start the update poller if it is not already running."""
        if self._poller_task is None or self._poller_task.done():
            self._poller_task = asyncio.get_running_loop().create_task(self._poll_loop())

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
                f"{stage} — Task #{task_id}\n\n"
                f"{content[:1500]}\n\n"
                f"Approve or Reject?"
            )

            # No parse_mode: LLM-generated content routinely breaks Markdown
            # entity parsing, which would fail the whole approval request.
            await bot.send_message(
                chat_id=self.config.approval.chat_id,
                text=msg,
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
        self._ensure_poller()

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
        # --- Approval callbacks (existing) ---
        if callback_data.startswith(("approve:", "reject:")):
            action, key = callback_data.split(":", 1)
            if key in self.pending:
                if action == "approve":
                    self.results[key] = True
                    self.pending[key].set()
                    return "Approved. Task will proceed."
                else:
                    self.results[key] = False
                    self.pending[key].set()
                    return "Rejected. Task will not proceed."
            return None  # stale callback

        # --- Trigger gate callbacks ---
        if callback_data.startswith("trigger_task:"):
            task_id = int(callback_data.split(":", 1)[1])
            if self._daemon is not None:
                asyncio.get_running_loop().create_task(
                    self._daemon.trigger_task(task_id))
                return f"🚀 Task #{task_id} triggered for execution."
            return "Daemon not ready."

        if callback_data.startswith("hold_task:"):
            task_id = int(callback_data.split(":", 1)[1])
            return f"⏸️ Task #{task_id} held. Use /run {task_id} when ready."

        return None

    # --- Task Entry Trigger Gate ---

    async def send_task_trigger_card(self, task_id: int, title: str,
                                     file_path: str) -> bool:
        """Send a Telegram message with [🚀 Start Execution] / [⏸️ Hold] buttons."""
        try:
            bot = self._get_bot()
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🚀 Start Execution",
                        callback_data=f"trigger_task:{task_id}"),
                    InlineKeyboardButton(
                        "⏸️ Hold",
                        callback_data=f"hold_task:{task_id}"),
                ]
            ])

            msg = (
                f"📋 *Task [{task_id}] Staged for Review:* {title}\n"
                f"_File: {file_path}_\n\n"
                f"Edit or refine the task in backlog, then tap below when ready."
            )

            await bot.send_message(
                chat_id=self.config.approval.chat_id,
                text=msg,
                reply_markup=keyboard,
            )
            return True

        except (ImportError, ValueError) as e:
            print(f"[gateway] Telegram unavailable for trigger card: {e}")
            return False
        except Exception as e:
            print(f"[gateway] Trigger card error: {e}")
            return False

    async def _handle_text_command(self, message) -> None:
        """Parse /run, /start, /tasks, /backlog text commands."""
        text = message.text.strip()
        chat_id = message.chat.id

        if text.startswith(("/run ", "/start ")):
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                await self._bot.send_message(
                    chat_id=chat_id,
                    text="Usage: /run <task_id>  or  /start <task_id>")
                return
            try:
                task_id = int(parts[1].strip())
            except ValueError:
                await self._bot.send_message(
                    chat_id=chat_id,
                    text="Invalid task ID. Usage: /run <task_id>")
                return
            if self._daemon is not None:
                asyncio.get_running_loop().create_task(
                    self._daemon.trigger_task(task_id))
                await self._bot.send_message(
                    chat_id=chat_id,
                    text=f"🚀 Triggering task #{task_id}...")
            else:
                await self._bot.send_message(
                    chat_id=chat_id,
                    text="Daemon not ready.")

        elif text in ("/tasks", "/backlog"):
            if self._state is None:
                await self._bot.send_message(
                    chat_id=chat_id,
                    text="State machine not initialized.")
                return
            from models import TaskState
            pending = self._state.get_pending_trigger_tasks()
            if not pending:
                await self._bot.send_message(
                    chat_id=chat_id,
                    text="No tasks in PENDING_TRIGGER status.")
                return
            lines = ["📋 *Tasks awaiting trigger:*\n"]
            for t in pending:
                lines.append(f"• #{t['task_id']} — {t['task_file']}")
            await self._bot.send_message(
                chat_id=chat_id,
                text="\n".join(lines))
