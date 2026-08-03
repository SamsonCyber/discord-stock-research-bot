"""
Discord adapter: natural-language DMs → research agent → tools.

Primary UX matches production agentic research mode:
  allowlisted user DMs the bot in plain English
  bot runs research tools
  bot replies with the research answer

Not a slash-command first product.
"""

from __future__ import annotations

import os

import discord
from discord.ext import commands

from .agent import run_turn
from .auth import allowed_user_ids, is_allowed

# Discord requires message content intent for reading DM text.
_INTENTS = discord.Intents.none()
_INTENTS.guilds = True
_INTENTS.dm_messages = True
_INTENTS.message_content = True


class StockResearchBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=commands.when_mentioned, intents=_INTENTS)
        self.allowed = allowed_user_ids()

    async def on_ready(self) -> None:
        print(
            f"Connected as {self.user}; "
            f"allowlisted users: {len(self.allowed)}; "
            f"mode: NL DM research agent"
        )
        print("Chat the bot in DMs with natural language (not slash commands).")


bot = StockResearchBot()


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return
    # DMs only — same posture as production agentic research gateway.
    if message.guild is not None:
        return
    if not is_allowed(message.author.id):
        await message.channel.send("Not authorized.")
        return

    content = (message.content or "").strip()
    if not content:
        return

    async with message.channel.typing():
        result = run_turn(content)

    # Production agent posture: Discord markdown text (section headers +
    # epistemic tags), not ASCII boxes and not embed-first cosplay.
    # Optional STOCK_RESEARCH_REPLY_AS_EMBED=1 keeps Embed payloads available.
    use_embed = os.environ.get("STOCK_RESEARCH_REPLY_AS_EMBED", "").strip() in (
        "1", "true", "True", "yes", "YES",
    )
    if use_embed and result.embeds:
        embeds: list[discord.Embed] = []
        for payload in result.embeds[:10]:
            embeds.append(discord.Embed.from_dict(payload))
        names = ", ".join(c["name"] for c in result.tool_calls) if result.tool_calls else ""
        content_note = f"_tools used: {names}_" if names else None
        await message.channel.send(content=content_note, embeds=embeds)
        return

    text = result.text
    if len(text) > 1900:
        text = text[:1900] + "\n...(truncated)"
    await message.channel.send(text)


def main() -> None:
    token = os.environ.get("STOCK_RESEARCH_DISCORD_TOKEN", "").strip()
    if not token:
        raise SystemExit("STOCK_RESEARCH_DISCORD_TOKEN is required; refusing to start")
    if not allowed_user_ids():
        raise SystemExit(
            "STOCK_RESEARCH_ALLOWED_USER_IDS is empty; refusing to start (fail-closed)"
        )
    print("Equity Research Agent")
    print("  UX: natural language DMs → agent → research tools")
    print("  Enable Message Content Intent in the Discord developer portal.")
    bot.run(token)


if __name__ == "__main__":
    main()
