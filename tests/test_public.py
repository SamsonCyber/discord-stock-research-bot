"""Public package tests - no network, no Discord token required."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from equity_research_agent.agent import classify_intent, extract_tickers, run_turn
from equity_research_agent.auth import is_allowed
from equity_research_agent.research import research_brief, session_aware_quote, us_equity_session

PKG = Path(__file__).resolve().parents[1] / "src" / "equity_research_agent"

# Freeze US session so tape labels and samples are deterministic in CI.
_FIXED_SESSION = {
    "phase": "afterhours",
    "is_rth": False,
    "is_extended_hours": True,
    "et_now": "2026-08-05 17:30:00 EDT",
    "weekday": "Wednesday",
    "windows_et": {
        "premarket": "04:00-09:30",
        "rth": "09:30-16:00",
        "afterhours": "16:00-20:00",
    },
    "note": (
        "Demo session clock only. Public package has no live quotes; "
        "production deployments wire live pre/post market fields the same way."
    ),
}


@pytest.fixture(autouse=True)
def _freeze_afterhours_session(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fixed(_now=None):
        return dict(_FIXED_SESSION)

    monkeypatch.setattr(
        "equity_research_agent.research.us_equity_session",
        _fixed,
    )
    monkeypatch.setattr(
        "equity_research_agent.tools.us_equity_session",
        _fixed,
    )

FORBIDDEN_IMPORT_ROOTS = frozenset(
    {
        "requests",
        "httpx",
        "aiohttp",
        "urllib3",
        "yfinance",
        "alpaca",
        "ccxt",
        "web3",
        "boto3",
        "openai",
        "anthropic",
        "sqlalchemy",
        "psycopg2",
        "redis",
        "docker",
        "paramiko",
    }
)


def test_nl_research_turn_runs_tool() -> None:
    result = run_turn("research AAPL")
    assert result.ok
    assert result.intent == "research"
    assert result.tickers == ["AAPL"]
    assert result.tool_calls and result.tool_calls[0]["name"] == "research"
    assert "AAPL" in result.text
    assert "tools used" in result.text.lower()


def test_nl_levels_and_risk() -> None:
    levels = run_turn("levels on NVDA")
    assert levels.intent == "levels"
    assert levels.tool_calls[0]["name"] == "levels"
    risk = run_turn("what's the risk for TSLA")
    assert risk.intent == "risk"
    assert risk.tool_calls[0]["name"] == "risk"


def test_nl_help() -> None:
    result = run_turn("help")
    assert result.intent == "help"
    assert "research" in result.text.lower()


def test_extract_tickers_skips_noise() -> None:
    assert extract_tickers("what do you think about AAPL?") == ["AAPL"]
    assert "WHAT" not in extract_tickers("what about MSFT")
    assert "HOURS" not in extract_tickers("after hours pricing")
    assert extract_tickers("after hours AAPL") == ["AAPL"]


def test_research_stable() -> None:
    assert research_brief("AAPL").as_dict() == research_brief("aapl").as_dict()


def test_session_aware_quote_afterhours_fields() -> None:
    q = session_aware_quote("AAPL")
    assert q["price_label"] == "AFTER-HOURS"
    assert q["price_session"] == "afterhours"
    assert q["current_price"] == q["post_market_price"]
    assert q["regular_market_price"] is not None
    assert q["previous_close"] is not None
    brief = research_brief("AAPL")
    assert "AFTER-HOURS" in brief.format_message()
    assert "session-aware" in brief.format_message()
    assert "RTH regular" in brief.format_message()


def test_session_tool_turn() -> None:
    result = run_turn("is market open")
    assert result.intent == "session"
    assert result.tool_calls and result.tool_calls[0]["name"] == "session"
    assert "afterhours" in result.text.lower() or "AFTER-HOURS" in result.text or "Phase" in result.text


def test_classify_intent() -> None:
    assert classify_intent("levels on AAPL") == "levels"
    assert classify_intent("risk for AAPL") == "risk"
    assert classify_intent("research AAPL") == "research"
    assert classify_intent("session") == "session"
    assert classify_intent("after hours?") == "session"


def test_empty_allowlist_denies(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STOCK_RESEARCH_ALLOWED_USER_IDS", raising=False)
    monkeypatch.delenv("STOCK_RESEARCH_ALLOWED_USER_IDS_FILE", raising=False)
    assert not is_allowed(123)


def test_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STOCK_RESEARCH_ALLOWED_USER_IDS", "123,456")
    assert is_allowed(123)
    assert not is_allowed(999)


def test_package_has_no_forbidden_imports() -> None:
    found: list[str] = []
    for path in PKG.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in FORBIDDEN_IMPORT_ROOTS:
                        found.append(f"{path.name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root in FORBIDDEN_IMPORT_ROOTS:
                    found.append(f"{path.name}: from {node.module}")
    assert found == []


def test_showcase_assets_exist() -> None:
    """Front door is real engine text + samples, not a screenshot mock."""
    root = Path(__file__).resolve().parents[1]
    for rel in (
        "assets/architecture.svg",
        "assets/banner.png",
        "assets/interactive-demo.html",
        "docs/samples/aapl-research.txt",
    ):
        path = root / rel
        assert path.is_file(), f"missing {rel}"
    demo = (root / "assets" / "interactive-demo.html").read_text(encoding="utf-8")
    assert "const DATA" in demo
    assert "AAPL" in demo
    body = (root / "docs" / "samples" / "aapl-research.txt").read_text(encoding="utf-8")
    assert "AAPL" in body
    assert "Apple" in body
    assert "Technology" in body
    assert "tools used" in body.lower()
    assert "offline-demo" in body
    assert "AAPL | research" in body
    # README embeds the sample as text (not a Discord screenshot image)
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "hero-discord.svg" not in readme
    assert "AAPL | research" in readme
    assert "range-bound" in readme
    assert "python -m equity_research_agent.demo research AAPL" in readme


def test_sample_reply_matches_live_demo_engine() -> None:
    """Checked-in sample must match the real agent path (not free-written fiction)."""
    root = Path(__file__).resolve().parents[1]
    sample = (root / "docs" / "samples" / "aapl-research.txt").read_text(encoding="utf-8")
    live = run_turn("research AAPL").text
    assert sample.strip() == live.strip()
    again = run_turn("research AAPL").text
    assert again.strip() == live.strip()


def test_known_ticker_meta_is_intentional() -> None:
    """Famous symbols must not look randomly sector-labeled in the public demo."""
    brief = research_brief("AAPL")
    assert brief.company == "Apple"
    assert brief.sector == "Technology"
    msg = brief.format_message()
    # Production-shaped Discord markdown (not ASCII box cards)
    assert "┌" not in msg and "└" not in msg
    assert "**AAPL | research**" in msg
    assert "**Read**" in msg
    assert "**1 | Tape**" in msg
    assert "INFERRED" in msg
    assert "VERIFIED" in msg
    assert "█" not in msg and "░" not in msg
    assert "▁" not in msg and "▇" not in msg
    assert "Invalidation" in msg
    assert "conviction **med**" in msg or "conviction **low**" in msg or "conviction **high**" in msg
    levels = run_turn("levels on NVDA")
    assert "NVIDIA" in levels.text
    assert "**NVDA | levels**" in levels.text
    assert "Support:" in levels.text or "support" in levels.text.lower()


def test_research_embed_payload_for_discord() -> None:
    """Optional Embed path still works; body is markdown description."""
    result = run_turn("research AAPL")
    assert result.embeds
    emb = result.embeds[0]
    assert emb["title"].startswith("AAPL")
    assert "description" in emb
    assert "**AAPL | research**" in emb["description"]
    brief = research_brief("AAPL")
    assert emb["color"] in {0x57F287, 0xED4245, 0xFEE75C, 0x99AAB5}
    assert brief.bias in {"bullish", "bearish", "neutral"}


def test_agent_text_is_production_shaped_markdown() -> None:
    """Primary agent reply matches production markdown shape, not box art."""
    text = run_turn("research AAPL").text
    assert "┌" not in text
    assert "█" not in text and "░" not in text
    assert "▁" not in text and "▇" not in text
    assert "**AAPL | research**" in text
    assert "paper research only" in text
    assert "**3 | Catalysts**" in text
    assert "_tools used: research_" in text


def test_readme_points_at_showcase_assets() -> None:
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "assets/banner.png" in readme
    assert "assets/interactive-demo.html" in readme
    assert "assets/architecture.svg" in readme
    assert "docs/samples/aapl-research.txt" in readme
    assert "docs/PRODUCTION_TOOLS.md" in readme
    assert "python -m equity_research_agent.demo" in readme
    assert "scripts/build_showcase.py" in readme
    # Proof is text from the engine, not a hero screenshot SVG
    assert "hero-discord.svg" not in readme


def test_source_has_no_lab_markers() -> None:
    markers = (
        "finbot",
        "codebot",
        ".secrets",
        "192.168",
        "market-maker",
        "alpaca",
        "private_key",
        "BEGIN RSA",
    )
    hits: list[str] = []
    roots = [
        PKG,
        Path(__file__).resolve().parents[1] / "scripts",
        Path(__file__).resolve().parents[1] / "docs",
    ]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {
                ".py",
                ".md",
                ".toml",
                ".yml",
                ".example",
            }:
                continue
            text = path.read_text(encoding="utf-8").lower()
            for marker in markers:
                if marker.lower() in text:
                    hits.append(f"{path.relative_to(root.parents[0])}: {marker}")
    assert hits == []
