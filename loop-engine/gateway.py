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
from datetime import datetime, timezone
from pathlib import Path
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
        # Dedup store (HOTFIX-06): callback query ids already answered/processed
        # so duplicate clicks (Telegram re-delivery, double taps) are ignored.
        self._processed_callback_ids: set[str] = set()

    def set_daemon(self, daemon):
        """Register the daemon instance for trigger callbacks."""
        self._daemon = daemon

    def set_state(self, state):
        """Register the state machine for /tasks queries."""
        self._state = state

    async def _send_with_retry(self, send_coroutine_fn, max_retries: int = 3,
                               base_delay: float = 1.0, task_id=None,
                               stage: str = "", content: str = "") -> bool:
        """Exponential backoff retry for Telegram sends (Task 144).

        Transient: NetworkError, TimedOut, RetryAfter (incl. asyncio.TimeoutError)
        -> sleep base_delay*(2**attempt) and retry.
        Fatal: InvalidToken -> fail fast, no retry, no DLQ.
        Exhausted: enqueue DLQ via self._state when task_id is provided.
        """
        last_err: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                await send_coroutine_fn()
                return True
            except Exception as e:  # noqa: BLE001 - telegram error surface is broad
                last_err = e
                err_name = type(e).__name__
                if "InvalidToken" in err_name:
                    return False
                is_transient = (
                    any(k in err_name for k in (
                        "NetworkError", "TimedOut", "RetryAfter",
                        "Timeout", "Network", "TimeoutError"))
                    or isinstance(e, (TimeoutError, asyncio.TimeoutError))
                )
                # Unknown errors are retried as transient to survive flaky
                # transports, except auth which already returned above.
                _ = is_transient
                if attempt >= max_retries:
                    if task_id is not None and self._state is not None:
                        enqueue = getattr(self._state, "enqueue_dead_letter", None)
                        if callable(enqueue):
                            try:
                                enqueue(int(task_id), str(stage), str(content), str(e))
                            except Exception:
                                pass
                    return False
                await asyncio.sleep(base_delay * (2 ** attempt))
        if last_err is not None and task_id is not None and self._state is not None:
            enqueue = getattr(self._state, "enqueue_dead_letter", None)
            if callable(enqueue):
                try:
                    enqueue(int(task_id), str(stage), str(content), str(last_err))
                except Exception:
                    pass
        return False

    def _log_event(self, event: str) -> None:
        """Append a Telegram event to loop-engine/logs/telegram_events.log.

        Debug telemetry (HOTFIX-03): opt-in ONLY via LOOP_ENGINE_DEBUG=1.
        Never raises — telemetry must not affect gateway operation.
        """
        if os.environ.get("LOOP_ENGINE_DEBUG") != "1":
            return
        try:
            log_dir = Path(__file__).resolve().parent / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            with open(log_dir / "telegram_events.log", "a", encoding="utf-8") as f:
                f.write(
                    f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}Z] "
                    f"{event}\n"
                )
        except Exception as e:
            print(f"[gateway] debug telemetry log error: {e}")

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
                    cq_id = str(getattr(cq, "id", "") or "")
                    # Dedup (HOTFIX-06): ignore duplicate clicks on the same
                    # callback query id (double taps / Telegram re-delivery).
                    if cq_id and cq_id in self._processed_callback_ids:
                        continue
                    # Instant acknowledgment (HOTFIX-06): answer BEFORE any
                    # processing so Telegram never rejects the query as
                    # "too old". The ack toast is intentionally skipped (a
                    # second answer with text would be rejected by Telegram).
                    try:
                        await cq.answer()
                    except Exception as e:
                        print(f"[gateway] callback answer failed: {e}")
                    if cq_id:
                        self._processed_callback_ids.add(cq_id)
                    self.handle_callback(cq.data)
                    continue

                # Text command parsing — contained so a network timeout in a
                # handler never kills the poller loop (HOTFIX-06).
                msg = getattr(u, "message", None)
                if msg is not None and msg.text:
                    try:
                        await self._handle_text_command(msg)
                    except Exception as e:
                        print(f"[gateway] text command error: {e}")

    def _ensure_poller(self):
        """Start the update poller if it is not already running."""
        if self._poller_task is None or self._poller_task.done():
            self._poller_task = asyncio.get_running_loop().create_task(self._poll_loop())

    async def request_approval(self, task_id: int, stage: str, content: str,
                               message_thread_id: Optional[int] = None) -> bool:
        """Send approval request with inline keyboard. Blocks until response."""
        # Defensive string guard (HOTFIX-05): LLM/other callers may pass None or
        # blank content — never let a NoneType reach len()/format paths.
        content_str = str(content) if content is not None else ""
        if not content_str.strip():
            content_str = f"[{stage} for Task #{task_id}] (No text body provided)"
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

            if len(content_str) > 3000:
                # Long plan/blueprint content (HOTFIX-02): inline text would be
                # unreadable and hit Telegram's message cap. Send the FULL
                # Markdown as a document attachment with a short summary caption
                # plus the same Approve/Reject buttons.
                tmp_path = Path(f"/tmp/plan_task_{task_id}.md")
                send_method = "document"
                tmp_path.write_text(content_str, encoding="utf-8")
                try:
                    # No parse_mode for the caption: keep it plain (consistent
                    # with the inline path — LLM content breaks Markdown parsing).
                    async def _send_doc():
                        await bot.send_document(
                            chat_id=self.config.approval.chat_id,
                            document=str(tmp_path),
                            caption=(
                                f"{stage} — Task #{task_id} "
                                f"(plan attached as file)\n\n"
                                f"Approve or Reject?"
                            ),
                            reply_markup=keyboard,
                            message_thread_id=message_thread_id,
                        )
                    ok = await self._send_with_retry(
                        _send_doc, task_id=task_id, stage=stage, content=content_str)
                    if not ok:
                        return False
                finally:
                    tmp_path.unlink(missing_ok=True)
            else:
                send_method = "inline"
                msg = (
                    f"{stage} — Task #{task_id}\n\n"
                    f"{content_str[:1500]}\n\n"
                    f"Approve or Reject?"
                )

                # No parse_mode: LLM-generated content routinely breaks Markdown
                # entity parsing, which would fail the whole approval request.
                async def _send_msg():
                    await bot.send_message(
                        chat_id=self.config.approval.chat_id,
                        text=msg,
                        reply_markup=keyboard,
                        message_thread_id=message_thread_id,
                    )
                ok = await self._send_with_retry(
                    _send_msg, task_id=task_id, stage=stage, content=content_str)
                if not ok:
                    return False

            self._log_event(
                f"approval_request stage={stage!r} task={task_id} "
                f"content_len={len(content_str)} via={send_method}")

        except (ImportError, ValueError) as e:
            print(f"[gateway] Telegram unavailable: {e}")
            print(f"[gateway] SECURITY: Approval for task {task_id} DENIED (no auto-grant)")
            return False

        except Exception as e:
            print(f"[gateway] Telegram error: {e}")
            print(f"[gateway] SECURITY: Approval for task {task_id} DENIED (no auto-grant)")
            if self._state is not None:
                enqueue = getattr(self._state, "enqueue_dead_letter", None)
                if callable(enqueue):
                    try:
                        enqueue(int(task_id), str(stage), str(content_str), str(e))
                    except Exception:
                        pass
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
        self._log_event(f"callback_received data={callback_data!r}")
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
                                     file_path: str,
                                     message_thread_id: Optional[int] = None) -> bool:
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

            async def _send_card():
                await bot.send_message(
                    chat_id=self.config.approval.chat_id,
                    text=msg,
                    reply_markup=keyboard,
                    message_thread_id=message_thread_id,
                )
            ok = await self._send_with_retry(
                _send_card, task_id=task_id, stage="trigger",
                content=f"{title} {file_path}")
            if not ok:
                return False
            self._log_event(
                f"trigger_card_sent task={task_id} title={title!r} file={file_path}")
            return True

        except (ImportError, ValueError) as e:
            print(f"[gateway] Telegram unavailable for trigger card: {e}")
            return False
        except Exception as e:
            self._log_event(f"trigger_card_error task={task_id} error={e!r}")
            print(f"[gateway] Trigger card error: {e}")
            return False

    async def send_progress(self, task_id: int, message: str,
                              message_thread_id: Optional[int] = None) -> bool:
        """Send a brief real-time status update for a task to the Telegram chat.

        Non-fatal by design: pipeline progress notifications must never crash
        task processing, so every Telegram failure is logged and swallowed.
        """
        try:
            bot = self._get_bot()
            await bot.send_message(
                chat_id=self.config.approval.chat_id,
                text=f"⏳ Task #{task_id}: {message}",
                message_thread_id=message_thread_id,
            )
            return True
        except (ImportError, ValueError) as e:
            print(f"[gateway] Telegram unavailable for progress: {e}")
            return False
        except Exception as e:
            print(f"[gateway] Progress notification error: {e}")
            return False

    async def send_boot_scan_summary(self, tasks: list[dict], top_n: int = 4,
                                       message_thread_id: Optional[int] = None) -> bool:
        """Send ONE consolidated trigger summary for all pending backlog tasks.

        Anti-flood replacement (HOTFIX-02) for the per-task trigger-card
        fan-out during boot scans: lists every pending task in a single message
        and attaches inline Start buttons for the top `top_n` tasks. Each task
        record is expected to carry ``task_id`` and ``title``.
        """
        try:
            bot = self._get_bot()
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            lines = [
                f"📋 Boot Scan — {len(tasks)} task(s) awaiting trigger:"
            ]
            for t in tasks:
                lines.append(f"  • #{t['task_id']} — {t.get('title', '')}")
            lines.append("\nTap Start on a task to run it now.")

            buttons = [
                InlineKeyboardButton(
                    f"🚀 #{t['task_id']} Start",
                    callback_data=f"trigger_task:{t['task_id']}",
                )
                for t in tasks[:top_n]
            ]
            keyboard = InlineKeyboardMarkup([buttons]) if buttons else None

            await bot.send_message(
                chat_id=self.config.approval.chat_id,
                text="\n".join(lines),
                reply_markup=keyboard,
                message_thread_id=message_thread_id,
            )
            self._log_event(
                f"boot_summary_sent tasks={len(tasks)} "
                f"ids={[t['task_id'] for t in tasks]} buttons={top_n}")
            return True

        except (ImportError, ValueError) as e:
            print(f"[gateway] Telegram unavailable for boot scan summary: {e}")
            return False
        except Exception as e:
            self._log_event(f"boot_summary_error tasks={len(tasks)} error={e!r}")
            print(f"[gateway] Boot scan summary error: {e}")
            return False

    async def _handle_text_command(self, message) -> None:
        """Parse /run, /start, /tasks, /backlog, /status text commands."""
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

        elif text == "/status":
            # Status summary (HOTFIX-02): active tasks + pending-trigger tasks.
            if self._state is None:
                await self._bot.send_message(
                    chat_id=chat_id,
                    text="State machine not initialized.")
                return
            active = self._state.get_active_tasks()
            pending = self._state.get_pending_trigger_tasks()
            if not active and not pending:
                await self._bot.send_message(
                    chat_id=chat_id,
                    text="📊 Status: no active tasks.")
                return
            lines = ["📊 Status Summary"]
            lines.append(f"\n🔄 Active tasks ({len(active)}):")
            for t in active:
                lines.append(
                    f"  • #{t['task_id']} — {t.get('state', '?')} — {t['task_file']}")
            lines.append(f"\n⏸ Pending trigger ({len(pending)}):")
            for t in pending:
                lines.append(f"  • #{t['task_id']} — {t['task_file']}")
            await self._bot.send_message(
                chat_id=chat_id,
                text="\n".join(lines))
