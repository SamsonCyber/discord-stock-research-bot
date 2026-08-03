"""Offline stock research helpers (deterministic demo data, no market APIs)."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

import numpy as np

_TICKER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9.\-]{0,9}$")

SECTORS = (
    "Technology",
    "Healthcare",
    "Financials",
    "Energy",
    "Consumer",
    "Industrials",
    "Communications",
)

BIASES = ("bullish", "neutral", "bearish")


def normalize_ticker(raw: str) -> str:
    ticker = (raw or "").strip().upper()
    if not _TICKER_RE.match(ticker):
        raise ValueError("ticker must be 1-10 chars: letters, digits, '.', or '-'")
    return ticker


def _rng_for(ticker: str, salt: int = 0) -> np.random.Generator:
    # Stable per-ticker seed so the same symbol always returns the same demo card.
    seed = (sum(ord(c) * (i + 1) for i, c in enumerate(ticker)) + salt * 9973) % (2**32 - 1)
    return np.random.default_rng(seed or 1)


def _ref_price(ticker: str) -> float:
    """Shared reference price so brief / levels / risk agree on the same symbol."""
    return float(_rng_for(ticker, 0).uniform(15, 420))


@dataclass(frozen=True)
class ResearchBrief:
    ticker: str
    mode: str
    sector: str
    bias: str
    conviction: int
    last_price: float
    change_pct: float
    volume_vs_avg: float
    thesis: str
    catalysts: list[str]
    risks: list[str]
    invalidation: str
    disclaimer: str

    def as_dict(self) -> dict:
        return asdict(self)

    def format_message(self) -> str:
        cats = "\n".join(f"  • {c}" for c in self.catalysts)
        risks = "\n".join(f"  • {r}" for r in self.risks)
        return (
            f"**{self.ticker}** research brief (`{self.mode}`)\n"
            f"Sector: {self.sector} · Bias: **{self.bias}** · Conviction: {self.conviction}/5\n"
            f"Ref price: `${self.last_price:.2f}` ({self.change_pct:+.2f}%) · "
            f"Vol vs avg: `{self.volume_vs_avg:.2f}x`\n\n"
            f"**Thesis**\n{self.thesis}\n\n"
            f"**Catalysts**\n{cats}\n\n"
            f"**Risks**\n{risks}\n\n"
            f"**Invalidation:** {self.invalidation}\n\n"
            f"_{self.disclaimer}_"
        )


@dataclass(frozen=True)
class LevelMap:
    ticker: str
    mode: str
    last_price: float
    supports: list[float]
    resistances: list[float]
    pivot: float
    disclaimer: str

    def as_dict(self) -> dict:
        return asdict(self)

    def format_message(self) -> str:
        sup = ", ".join(f"${x:.2f}" for x in self.supports)
        res = ", ".join(f"${x:.2f}" for x in self.resistances)
        return (
            f"**{self.ticker}** levels (`{self.mode}`)\n"
            f"Ref price: `${self.last_price:.2f}` · Pivot: `${self.pivot:.2f}`\n"
            f"Support: {sup}\n"
            f"Resistance: {res}\n\n"
            f"_{self.disclaimer}_"
        )


@dataclass(frozen=True)
class RiskSnapshot:
    ticker: str
    mode: str
    last_price: float
    atr_pct: float
    beta: float
    suggested_stop: float
    risk_per_share: float
    position_note: str
    disclaimer: str

    def as_dict(self) -> dict:
        return asdict(self)

    def format_message(self) -> str:
        return (
            f"**{self.ticker}** risk snapshot (`{self.mode}`)\n"
            f"Ref price: `${self.last_price:.2f}`\n"
            f"ATR%: `{self.atr_pct:.2f}%` · Beta: `{self.beta:.2f}`\n"
            f"Suggested stop (demo): `${self.suggested_stop:.2f}` "
            f"(risk/share `${self.risk_per_share:.2f}`)\n"
            f"{self.position_note}\n\n"
            f"_{self.disclaimer}_"
        )


_DISCLAIMER = (
    "Demo research data only. Offline / deterministic. "
    "Not live market data. Not financial advice."
)


def research_brief(ticker: str) -> ResearchBrief:
    symbol = normalize_ticker(ticker)
    rng = _rng_for(symbol, 1)
    last = _ref_price(symbol)
    change = float(rng.normal(0.2, 1.8))
    bias = BIASES[int(rng.integers(0, len(BIASES)))]
    conviction = int(rng.integers(2, 6))
    sector = SECTORS[int(rng.integers(0, len(SECTORS)))]
    vol = float(rng.uniform(0.6, 2.4))

    if bias == "bullish":
        thesis = (
            f"{symbol} shows constructive relative strength in this demo model. "
            f"Watch for continuation if price holds above near support and volume stays elevated."
        )
        catalysts = [
            "Product or segment growth narrative improving",
            "Multiple expansion if guidance holds",
            "Technical reclaim of recent range high",
        ]
        risks = [
            "Earnings or guidance miss",
            "Sector rotation away from growth",
            "Break of structure under nearest support",
        ]
        invalidation = f"Daily close below ${last * 0.94:.2f} (demo level)"
    elif bias == "bearish":
        thesis = (
            f"{symbol} is under distribution in this demo model. "
            f"Rallies into resistance may be sold unless breadth and volume improve."
        )
        catalysts = [
            "Failed bounce into declining moving averages",
            "Margin or demand softness in the story",
            "Relative weakness vs sector benchmark",
        ]
        risks = [
            "Short squeeze on positive surprise",
            "Buyback or capital-return headline",
            "Broad market risk-on that lifts weak names",
        ]
        invalidation = f"Daily close above ${last * 1.06:.2f} (demo level)"
    else:
        thesis = (
            f"{symbol} is range-bound in this demo model. "
            f"Wait for a clean break with volume before upgrading bias."
        )
        catalysts = [
            "Range break with expanding volume",
            "Catalyst calendar (earnings / event)",
            "Sector leadership change",
        ]
        risks = [
            "Whipsaw inside the range",
            "Low-liquidity fake break",
            "Macro headline risk",
        ]
        invalidation = f"Two closes outside ${last * 0.97:.2f}–${last * 1.03:.2f} (demo band)"

    return ResearchBrief(
        ticker=symbol,
        mode="offline-demo",
        sector=sector,
        bias=bias,
        conviction=conviction,
        last_price=round(last, 2),
        change_pct=round(change, 2),
        volume_vs_avg=round(vol, 2),
        thesis=thesis,
        catalysts=catalysts,
        risks=risks,
        invalidation=invalidation,
        disclaimer=_DISCLAIMER,
    )


def level_map(ticker: str) -> LevelMap:
    symbol = normalize_ticker(ticker)
    rng = _rng_for(symbol, 2)
    last = _ref_price(symbol)
    step = last * float(rng.uniform(0.015, 0.04))
    supports = [round(last - step * k, 2) for k in (1, 2, 3)]
    resistances = [round(last + step * k, 2) for k in (1, 2, 3)]
    pivot = round((supports[0] + resistances[0] + last) / 3.0, 2)
    return LevelMap(
        ticker=symbol,
        mode="offline-demo",
        last_price=round(last, 2),
        supports=supports,
        resistances=resistances,
        pivot=pivot,
        disclaimer=_DISCLAIMER,
    )


def risk_snapshot(ticker: str) -> RiskSnapshot:
    symbol = normalize_ticker(ticker)
    rng = _rng_for(symbol, 3)
    last = _ref_price(symbol)
    atr_pct = float(rng.uniform(1.2, 5.5))
    beta = float(rng.uniform(0.7, 1.8))
    stop = last * (1.0 - atr_pct / 100.0 * 1.5)
    risk = last - stop
    note = (
        "Demo sizing note: risk a fixed fraction of capital against the stop distance; "
        "do not size from conviction alone."
    )
    return RiskSnapshot(
        ticker=symbol,
        mode="offline-demo",
        last_price=round(last, 2),
        atr_pct=round(atr_pct, 2),
        beta=round(beta, 2),
        suggested_stop=round(stop, 2),
        risk_per_share=round(risk, 2),
        position_note=note,
        disclaimer=_DISCLAIMER,
    )


TOOL_HELP = """**Discord Stock Research Bot — tools**

`/research ticker` — research brief (thesis, catalysts, risks, invalidation)
`/levels ticker` — support / resistance map
`/risk ticker` — volatility + demo stop distance
`/research-json ticker` — research brief as JSON
`/help` — this list
`/status` — bot health and auth mode

All research output in this public package is **offline demo data** (deterministic per ticker). Wire your own market-data and model backends for production research.

Not financial advice. Allowlisted users only.
"""
