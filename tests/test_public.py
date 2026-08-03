"""Public package tests — no network, no Discord token required."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from discord_stock_research_bot.agent import classify_intent, extract_tickers, run_turn
from discord_stock_research_bot.auth import is_allowed
from discord_stock_research_bot.research import research_brief

PKG = Path(__file__).resolve().parents[1] / "src" / "discord_stock_research_bot"

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


def test_research_stable() -> None:
    assert research_brief("AAPL").as_dict() == research_brief("aapl").as_dict()


def test_classify_intent() -> None:
    assert classify_intent("levels on AAPL") == "levels"
    assert classify_intent("risk for AAPL") == "risk"
    assert classify_intent("research AAPL") == "research"


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
    """GitHub front door needs in-repo visual + sample reply without running a server."""
    root = Path(__file__).resolve().parents[1]
    arch = root / "assets" / "architecture.svg"
    sample = root / "docs" / "samples" / "aapl-research.txt"
    assert arch.is_file(), "assets/architecture.svg missing"
    svg = arch.read_text(encoding="utf-8")
    assert "<svg" in svg
    assert "Discord" in svg or "research" in svg.lower()
    assert sample.is_file(), "docs/samples/aapl-research.txt missing"
    body = sample.read_text(encoding="utf-8")
    assert "AAPL" in body
    assert "tools used" in body.lower()
    assert "offline-demo" in body


def test_sample_reply_matches_live_demo_engine() -> None:
    """Checked-in sample must match the real agent path (not free-written fiction)."""
    root = Path(__file__).resolve().parents[1]
    sample = (root / "docs" / "samples" / "aapl-research.txt").read_text(encoding="utf-8")
    live = run_turn("research AAPL").text
    assert sample.strip() == live.strip()
    # Second call stays stable (deterministic offline engine)
    again = run_turn("research AAPL").text
    assert again.strip() == live.strip()


def test_readme_points_at_showcase_assets() -> None:
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "assets/architecture.svg" in readme
    assert "docs/samples/aapl-research.txt" in readme
    assert "docs/PRODUCTION_TOOLS.md" in readme
    assert "python -m discord_stock_research_bot.demo" in readme


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
