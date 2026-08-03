"""
Natural-language research agent.

Production shape: user chats in Discord DMs → LLM ReAct loop → tool registry
(charts, fundamentals, SEC, thesis, …) → answer.

This public package keeps the same interaction model with a lightweight local
agent: classify intent from the user message, run the matching tools, compose
a research reply. No LLM key required for the demo engine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .research import (
    level_map,
    normalize_ticker,
    research_brief,
    risk_snapshot,
)
from .tools import TOOLS, run_tool

_TICKER_TOKEN = re.compile(r"\b([A-Za-z][A-Za-z0-9.\-]{0,9})\b")

# Words that look like tickers but are English noise in research chat.
_STOP = frozenset(
    {
        "A",
        "I",
        "THE",
        "AND",
        "OR",
        "FOR",
        "ON",
        "IN",
        "OF",
        "TO",
        "IS",
        "IT",
        "ME",
        "MY",
        "WHAT",
        "WHATS",
        "ABOUT",
        "SHOW",
        "GIVE",
        "GET",
        "RUN",
        "DO",
        "CAN",
        "YOU",
        "PLEASE",
        "HELP",
        "TOOLS",
        "LIST",
        "LEVEL",
        "LEVELS",
        "RISK",
        "RISKS",
        "RESEARCH",
        "BRIEF",
        "STOCK",
        "STOCKS",
        "PRICE",
        "CHART",
        "LOOK",
        "AT",
        "HOW",
        "WHY",
        "WITH",
        "THIS",
        "THAT",
        "NEED",
        "WANT",
        "THINK",
        "TELL",
        "CHECK",
        "ANALYZE",
        "ANALYSIS",
        "SUPPORT",
        "RESISTANCE",
        "STOP",
        "SIZING",
        "COMPARE",
        "VS",
        "VERSUS",
    }
)


@dataclass
class AgentTurnResult:
    text: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    intent: str = ""
    tickers: list[str] = field(default_factory=list)
    # Discord Embed payloads (dict form). CLI ignores these; bot renders them.
    embeds: list[dict[str, Any]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.text) or bool(self.embeds)


def extract_tickers(text: str) -> list[str]:
    found: list[str] = []
    for match in _TICKER_TOKEN.finditer(text or ""):
        token = match.group(1).upper()
        if token in _STOP:
            continue
        try:
            ticker = normalize_ticker(token)
        except ValueError:
            continue
        if ticker not in found:
            found.append(ticker)
    return found


def classify_intent(text: str) -> str:
    raw = (text or "").strip().lower()
    if not raw:
        return "empty"
    if raw in {"help", "?", "tools", "list tools", "what can you do"}:
        return "help"
    if re.search(r"\b(level|levels|support|resistance|pivot)\b", raw):
        return "levels"
    if re.search(r"\b(risk|atr|stop|sizing|beta)\b", raw):
        return "risk"
    if re.search(r"\b(research|thesis|catalyst|analyze|analysis|brief|outlook)\b", raw):
        return "research"
    if extract_tickers(text):
        return "research"
    return "help"


def _format_tool_footer(calls: list[dict[str, Any]]) -> str:
    if not calls:
        return ""
    names = ", ".join(c["name"] for c in calls)
    return f"\n\n_tools used: {names}_"


def _help_text() -> str:
    lines = [
        "I'm a **stock research** bot. Talk to me in normal language — I run tools for you.",
        "",
        "Examples:",
        "• `research AAPL`",
        "• `what do you think about NVDA?`",
        "• `levels on TSLA`",
        "• `risk for MSFT`",
        "• `help`",
        "",
        "Tools I can run:",
    ]
    for name, spec in TOOLS.items():
        if name == "list_tools":
            continue
        lines.append(f"• **{name}** — {spec.description}")
    lines.append("")
    lines.append(
        "This public package uses an offline demo research engine (deterministic). "
        "Not live market data. Not financial advice."
    )
    return "\n".join(lines)


def run_turn(user_text: str) -> AgentTurnResult:
    """One NL research turn: intent → tools → answer."""
    text = (user_text or "").strip()
    intent = classify_intent(text)
    tickers = extract_tickers(text)
    calls: list[dict[str, Any]] = []

    if intent == "empty":
        return AgentTurnResult(
            text="Send a research question, e.g. `research AAPL` or `levels on NVDA`.",
            intent=intent,
        )

    if intent == "help" and not tickers:
        calls.append({"name": "list_tools", "args": {}})
        run_tool("list_tools")
        return AgentTurnResult(
            text=_help_text(),
            tool_calls=calls,
            intent=intent,
        )

    if not tickers:
        return AgentTurnResult(
            text=(
                "I need a ticker. Try:\n"
                "• `research AAPL`\n"
                "• `levels on NVDA`\n"
                "• `risk for TSLA`"
            ),
            intent=intent,
            tickers=tickers,
        )

    # Cap multi-ticker turns in the public package.
    tickers = tickers[:3]
    parts: list[str] = []
    embeds: list[dict[str, Any]] = []

    for ticker in tickers:
        if intent == "levels":
            calls.append({"name": "levels", "args": {"ticker": ticker}})
            card = level_map(ticker)
            parts.append(card.format_message())
            embeds.append(card.as_embed_dict())
        elif intent == "risk":
            calls.append({"name": "risk", "args": {"ticker": ticker}})
            card = risk_snapshot(ticker)
            parts.append(card.format_message())
            embeds.append(card.as_embed_dict())
        else:
            calls.append({"name": "research", "args": {"ticker": ticker}})
            card = research_brief(ticker)
            parts.append(card.format_message())
            embeds.append(card.as_embed_dict())

    # CLI gets boxed plain text; Discord prefers embeds (bot sends those).
    body = "\n\n".join(parts) + _format_tool_footer(calls)
    return AgentTurnResult(
        text=body,
        tool_calls=calls,
        intent=intent,
        tickers=tickers,
        embeds=embeds,
    )
