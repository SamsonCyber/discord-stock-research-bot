"""Offline natural-language research demo (no Discord)."""

from __future__ import annotations

import argparse
import json

from .agent import run_turn


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Equity Research Agent — offline NL demo. "
            "Pass a normal research question; the agent runs tools."
        )
    )
    parser.add_argument(
        "message",
        nargs="+",
        help='Natural language, e.g. research AAPL  OR  levels on NVDA',
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured turn result (text + tool_calls + intent)",
    )
    args = parser.parse_args(argv)
    user_text = " ".join(args.message)
    result = run_turn(user_text)
    if args.json:
        print(
            json.dumps(
                {
                    "intent": result.intent,
                    "tickers": result.tickers,
                    "tool_calls": result.tool_calls,
                    "text": result.text,
                    "embeds": result.embeds,
                },
                indent=2,
            )
        )
    else:
        # Terminal: boxed plain-text cards (no markdown). Discord uses embeds.
        print(result.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
