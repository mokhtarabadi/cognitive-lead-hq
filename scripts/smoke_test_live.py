"""Live smoke test for mcp-persona-server and mcp-decision-server (Task 167/168).

Reads credentials ONLY from `.env` (never hardcodes secrets). Exit 0 means
all four live checks passed; any failure raises with a clear message.

Usage (repo root):
    uv run --with litellm --with python-dotenv --with "mcp[cli]>=1.0,<2.0" \\
        python scripts/smoke_test_live.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)


def _excerpt(turn_result: dict) -> str:
    """Status-aware excerpt: real dispatch statuses carry no 'text_content'."""
    status = turn_result.get("status", "?")
    body = (
        turn_result.get("report")
        or turn_result.get("question")
        or turn_result.get("hint")
        or turn_result.get("remainder")
        or (turn_result.get("xml_content") or "")[:500]
    )
    return f"[{status}] {str(body)[:150]}"


def check_telegram() -> None:
    """[1/4] Bot identity + real greeting ping to the manager chat."""
    print("\n[1/4] Verifying Telegram Bot API...")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    assert token and chat_id, "TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID missing from .env"
    with urllib.request.urlopen(
        urllib.request.Request(
            f"https://api.telegram.org/bot{token}/getMe",
            headers={"User-Agent": "CognitiveLead/1.0"},
        ),
        timeout=15,
    ) as resp:
        username = json.loads(resp.read().decode())["result"]["username"]
    print(f"  PASS Bot connected: @{username}")
    payload = json.dumps({
        "chat_id": chat_id,
        "text": "Cognitive Lead AI System Online! "
                "Both mcp-persona-server and mcp-decision-server are active and verified.",
    }).encode("utf-8")
    with urllib.request.urlopen(
        urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "CognitiveLead/1.0"},
        ),
        timeout=15,
    ):
        pass
    print(f"  PASS Test ping delivered to chat_id={chat_id}")


def check_llm() -> None:
    """[2/4] Light-model round trip via OpenRouter."""
    print("\n[2/4] Verifying Gemini 3.8 Flash via OpenRouter...")
    import litellm  # Lazy: only needed for the live path.

    model = os.environ.get("PERSONA_MODEL", "openrouter/google/gemini-3.8-flash")
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": "Respond with the single word: CONFIRMED"}],
        temperature=0.1,
        drop_params=True,
    )
    reply = str(response.choices[0].message.content or "").strip()
    assert reply, "Empty model reply"
    print(f"  PASS Model response: {reply}")


def check_persona_dispatch() -> None:
    """[3/4] Real persona turn (writes a scratch transcript under task 999)."""
    print("\n[3/4] Testing mcp-persona-server dispatch turn...")
    sys.path.insert(0, str((REPO_ROOT / "mcp-persona-server").resolve()))
    from server import dispatch_session_turn  # noqa: E402

    call = dispatch_session_turn.fn if hasattr(dispatch_session_turn, "fn") else dispatch_session_turn
    result = call(
        task_id=999,
        persona_name="Software Architect",
        instruction="Confirm system architecture status in one sentence.",
    )
    assert result.get("status") in ("XML_EXTRACTED", "QUESTION", "REPORT", "RETRY_NEEDED"), result
    print(f"  PASS Status: {result['status']}")
    print(f"  PASS Persona excerpt: {_excerpt(result)}...")


def check_decision_store() -> None:
    """[4/4] Record + query a smoke decision in the configured repo."""
    print("\n[4/4] Testing mcp-decision-server storage & query...")
    # NOTE: both servers are named server.py — import by path under a unique
    # module name instead of plain `from server import ...`, which would
    # resolve to the already-imported persona server via sys.modules.
    import importlib.util

    decision_dir = (REPO_ROOT / "mcp-decision-server").resolve()
    sys.path.insert(0, str(decision_dir))
    spec = importlib.util.spec_from_file_location(
        "decision_server_live", decision_dir / "server.py"
    )
    decision_mod = importlib.util.module_from_spec(spec)
    sys.modules["decision_server_live"] = decision_mod
    spec.loader.exec_module(decision_mod)
    record_manager_decision = decision_mod.record_manager_decision
    query_manager_decisions = decision_mod.query_manager_decisions

    rec = record_manager_decision.fn if hasattr(record_manager_decision, "fn") else record_manager_decision
    qry = query_manager_decisions.fn if hasattr(query_manager_decisions, "fn") else query_manager_decisions
    sample = {
        "project_name": "cognitive-lead-hq",
        "session_id": "999",
        "verbatim_quote": {
            "original": "تست زنده سیستم با جمینای و تلگرام انجام شد",
            "english_translation": "Live system test with Gemini and Telegram completed successfully",
        },
        "extracted_decision": {
            "summary": "Live smoke verification of FastMCP servers",
            "category": "tooling",
            "rationale": "Verify bot and OpenRouter credentials",
            "alternatives": [],
            "tradeoffs": "None",
        },
    }
    confirmation = rec(sample)
    print(f"  PASS {confirmation}")
    matches = qry("Gemini")
    assert "DEC-" in matches, f"Query missed the recorded decision: {matches[:200]}"
    print(f"  PASS Query match verified: {matches[:100]}...")


def main() -> int:
    """Run all four live checks in order; return exit code."""
    print("=" * 60)
    print("  Cognitive Lead AI — Live System Verification")
    print("=" * 60)
    check_telegram()
    check_llm()
    check_persona_dispatch()
    check_decision_store()
    print("\n" + "=" * 60)
    print("  ALL LIVE TESTS PASSED SUCCESSFULLY! (Exit 0)")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
