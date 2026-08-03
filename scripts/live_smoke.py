"""
Optional live Discord connectivity check (env only).

  STOCK_RESEARCH_DISCORD_TOKEN
  STOCK_RESEARCH_ALLOWED_USER_IDS

Connects as the bot, confirms NL research agent posture, runs offline agent
turn for "research AAPL", disconnects. Does not print the token.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from discord_stock_research_bot.agent import run_turn  # noqa: E402
from discord_stock_research_bot.auth import allowed_user_ids  # noqa: E402


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"{name} is required for live_smoke")
    return value


async def _smoke() -> dict:
    from discord_stock_research_bot.bot import bot

    token = _require_env("STOCK_RESEARCH_DISCORD_TOKEN")
    allowed = allowed_user_ids()
    if not allowed:
        raise SystemExit("STOCK_RESEARCH_ALLOWED_USER_IDS is empty (fail-closed)")

    turn = run_turn("research AAPL")
    ready = asyncio.Event()
    info: dict = {
        "agent_intent": turn.intent,
        "agent_tools": [c["name"] for c in turn.tool_calls],
        "allowlist": len(allowed),
    }

    @bot.event
    async def on_ready() -> None:  # type: ignore[no-redef]
        info["user"] = str(bot.user)
        info["guild_count"] = len(bot.guilds)
        ready.set()

    async def runner() -> None:
        try:
            await asyncio.wait_for(bot.start(token), timeout=45)
        except asyncio.TimeoutError:
            pass

    task = asyncio.create_task(runner())
    try:
        await asyncio.wait_for(ready.wait(), timeout=30)
        info["connected"] = True
        info["intents_message_content"] = bool(bot.intents.message_content)
        info["intents_dm_messages"] = bool(bot.intents.dm_messages)
    finally:
        await bot.close()
        try:
            await asyncio.wait_for(task, timeout=10)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            task.cancel()

    info["ok"] = (
        bool(info.get("connected"))
        and info.get("agent_intent") == "research"
        and "research" in (info.get("agent_tools") or [])
        and info.get("intents_message_content") is True
    )
    return info


def main() -> int:
    turn = run_turn("research AAPL")
    print(f"agent ok intent={turn.intent} tools={[c['name'] for c in turn.tool_calls]}")
    print(f"allowlist_count={len(allowed_user_ids())}")

    info = asyncio.run(_smoke())
    print("live_smoke:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    if not info.get("ok"):
        raise SystemExit(1)
    print("SMOKE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
