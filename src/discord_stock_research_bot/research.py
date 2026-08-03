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

# Famous symbols get real sectors + company names so demos look intentional.
# Prices stay synthetic (offline-demo); bases only anchor the card aesthetics.
_KNOWN: dict[str, dict[str, object]] = {
    "AAPL": {"name": "Apple", "sector": "Technology", "base": 198.0},
    "MSFT": {"name": "Microsoft", "sector": "Technology", "base": 425.0},
    "NVDA": {"name": "NVIDIA", "sector": "Technology", "base": 128.0},
    "TSLA": {"name": "Tesla", "sector": "Consumer", "base": 248.0},
    "AMZN": {"name": "Amazon", "sector": "Consumer", "base": 185.0},
    "GOOGL": {"name": "Alphabet", "sector": "Communications", "base": 168.0},
    "META": {"name": "Meta Platforms", "sector": "Communications", "base": 520.0},
    "AMD": {"name": "Advanced Micro Devices", "sector": "Technology", "base": 142.0},
    "JPM": {"name": "JPMorgan Chase", "sector": "Financials", "base": 210.0},
    "XOM": {"name": "Exxon Mobil", "sector": "Energy", "base": 112.0},
    "UNH": {"name": "UnitedHealth", "sector": "Healthcare", "base": 520.0},
    "CAT": {"name": "Caterpillar", "sector": "Industrials", "base": 340.0},
}

_DISCLAIMER = (
    "Demo research data only. Offline / deterministic. "
    "Not live market data. Not financial advice."
)

_SPARK = "▁▂▃▄▅▆▇█"


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
    known = _KNOWN.get(ticker.upper())
    if known and isinstance(known.get("base"), (int, float)):
        base = float(known["base"])
        # Small deterministic wobble so cards are not perfectly static numbers.
        wobble = float(_rng_for(ticker, 0).uniform(0.97, 1.03))
        return base * wobble
    return float(_rng_for(ticker, 0).uniform(15, 420))


def _company_meta(ticker: str) -> tuple[str, str]:
    known = _KNOWN.get(ticker.upper())
    if known:
        name = str(known.get("name") or ticker)
        sector = str(known.get("sector") or "Technology")
        return name, sector
    rng = _rng_for(ticker, 7)
    sector = SECTORS[int(rng.integers(0, len(SECTORS)))]
    return ticker, sector


def _conviction_bar(n: int, width: int = 5) -> str:
    n = max(0, min(int(n), width))
    return "█" * n + "░" * (width - n)


def _sparkline(ticker: str, last: float, n: int = 16) -> str:
    rng = _rng_for(ticker, 11)
    rets = rng.normal(0.001, 0.012, size=n)
    path = last * np.exp(np.cumsum(rets[::-1]))[::-1]
    path = path * (last / path[-1])
    lo, hi = float(path.min()), float(path.max())
    span = max(hi - lo, 1e-9)
    chars: list[str] = []
    for p in path:
        idx = int((float(p) - lo) / span * (len(_SPARK) - 1))
        chars.append(_SPARK[max(0, min(idx, len(_SPARK) - 1))])
    return "".join(chars)


def _level_ladder(last: float, supports: list[float], resistances: list[float]) -> str:
    rows: list[tuple[float, str]] = []
    for r in sorted(resistances, reverse=True):
        rows.append((r, "R"))
    rows.append((last, "▶"))
    for s in sorted(supports, reverse=True):
        rows.append((s, "S"))
    lines = ["```"]
    for price, tag in rows:
        if tag == "▶":
            lines.append(f"  {tag} ${price:>8.2f}  ← last")
        elif tag == "R":
            lines.append(f"  ▲ ${price:>8.2f}  resistance")
        else:
            lines.append(f"  ▼ ${price:>8.2f}  support")
    lines.append("```")
    return "\n".join(lines)


@dataclass(frozen=True)
class ResearchBrief:
    ticker: str
    company: str
    mode: str
    sector: str
    bias: str
    conviction: int
    last_price: float
    change_pct: float
    volume_vs_avg: float
    sparkline: str
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
        bias_emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "🟡"}.get(self.bias, "⚪")
        bar = _conviction_bar(self.conviction)
        chg = f"{self.change_pct:+.2f}%"
        return (
            f"**{self.ticker}** · {self.company}\n"
            f"`{self.mode}` · {self.sector}\n"
            f"{bias_emoji} **{self.bias.upper()}** · conviction `{bar}` {self.conviction}/5\n"
            f"**${self.last_price:.2f}** ({chg}) · vol `{self.volume_vs_avg:.2f}x` avg\n"
            f"tape `{self.sparkline}`\n\n"
            f"**Thesis**\n{self.thesis}\n\n"
            f"**Catalysts**\n{cats}\n\n"
            f"**Risks**\n{risks}\n\n"
            f"**Invalidation:** {self.invalidation}\n\n"
            f"_{self.disclaimer}_"
        )


@dataclass(frozen=True)
class LevelMap:
    ticker: str
    company: str
    mode: str
    last_price: float
    supports: list[float]
    resistances: list[float]
    pivot: float
    disclaimer: str

    def as_dict(self) -> dict:
        return asdict(self)

    def format_message(self) -> str:
        ladder = _level_ladder(self.last_price, self.supports, self.resistances)
        return (
            f"**{self.ticker}** levels · {self.company}\n"
            f"`{self.mode}` · last **${self.last_price:.2f}** · pivot **${self.pivot:.2f}**\n"
            f"{ladder}\n"
            f"_{self.disclaimer}_"
        )


@dataclass(frozen=True)
class RiskSnapshot:
    ticker: str
    company: str
    mode: str
    last_price: float
    atr_pct: float
    beta: float
    suggested_stop: float
    risk_per_share: float
    r_multiple_1r: float
    position_note: str
    disclaimer: str

    def as_dict(self) -> dict:
        return asdict(self)

    def format_message(self) -> str:
        heat = "hot" if self.atr_pct >= 3.5 else "calm" if self.atr_pct <= 2.0 else "normal"
        return (
            f"**{self.ticker}** risk · {self.company}\n"
            f"`{self.mode}` · last **${self.last_price:.2f}**\n"
            f"ATR% `{self.atr_pct:.2f}` ({heat}) · beta `{self.beta:.2f}`\n"
            f"Demo stop **${self.suggested_stop:.2f}** · risk/share **${self.risk_per_share:.2f}**\n"
            f"1R target (demo) **${self.r_multiple_1r:.2f}**\n"
            f"{self.position_note}\n\n"
            f"_{self.disclaimer}_"
        )


def research_brief(ticker: str) -> ResearchBrief:
    symbol = normalize_ticker(ticker)
    company, sector = _company_meta(symbol)
    rng = _rng_for(symbol, 1)
    last = _ref_price(symbol)
    change = float(rng.normal(0.2, 1.8))
    # Known names lean constructive so the public demo doesn't look random-garbage.
    if symbol in _KNOWN:
        weights = np.array([0.55, 0.25, 0.20])  # bullish, neutral, bearish
        bias = str(rng.choice(BIASES, p=weights / weights.sum()))
    else:
        bias = BIASES[int(rng.integers(0, len(BIASES)))]
    conviction = int(rng.integers(2, 6))
    vol = float(rng.uniform(0.6, 2.4))
    spark = _sparkline(symbol, last)

    if bias == "bullish":
        thesis = (
            f"{company} ({symbol}) prints constructive structure in this offline model: "
            f"relative strength holds while {sector.lower()} stays bid. "
            f"Lean long only if price defends near support and volume stays above average."
        )
        catalysts = [
            f"{sector} leadership continuing into the next catalyst window",
            "Multiple expansion if guidance / narrative holds",
            "Technical reclaim of the recent range high on expanding volume",
        ]
        risks = [
            "Earnings or guidance miss vs quiet tape",
            f"Sector rotation out of {sector.lower()}",
            "Break of structure under nearest support with volume",
        ]
        invalidation = f"Daily close below ${last * 0.94:.2f} (demo level)"
    elif bias == "bearish":
        thesis = (
            f"{company} ({symbol}) looks under distribution in this offline model. "
            f"Rallies into resistance are sold unless breadth and volume improve. "
            f"Prefer fades or stay flat until structure repairs."
        )
        catalysts = [
            "Failed bounce into declining moving averages",
            "Margin or demand softness showing up in the story",
            f"Relative weakness vs the {sector.lower()} book",
        ]
        risks = [
            "Short squeeze on a positive surprise",
            "Buyback / capital-return headline",
            "Broad risk-on that lifts weak names",
        ]
        invalidation = f"Daily close above ${last * 1.06:.2f} (demo level)"
    else:
        thesis = (
            f"{company} ({symbol}) is range-bound in this offline model. "
            f"No edge until a clean break with volume. "
            f"Size small or wait; fake breaks are the default."
        )
        catalysts = [
            "Range break with expanding volume",
            "Catalyst calendar (earnings / product / event)",
            f"{sector} leadership change that pulls the name",
        ]
        risks = [
            "Whipsaw inside the range",
            "Low-liquidity fake break",
            "Macro headline risk that rewrites the tape",
        ]
        invalidation = f"Two closes outside ${last * 0.97:.2f}-${last * 1.03:.2f} (demo band)"

    return ResearchBrief(
        ticker=symbol,
        company=company,
        mode="offline-demo",
        sector=sector,
        bias=bias,
        conviction=conviction,
        last_price=round(last, 2),
        change_pct=round(change, 2),
        volume_vs_avg=round(vol, 2),
        sparkline=spark,
        thesis=thesis,
        catalysts=catalysts,
        risks=risks,
        invalidation=invalidation,
        disclaimer=_DISCLAIMER,
    )


def level_map(ticker: str) -> LevelMap:
    symbol = normalize_ticker(ticker)
    company, _sector = _company_meta(symbol)
    rng = _rng_for(symbol, 2)
    last = _ref_price(symbol)
    step = last * float(rng.uniform(0.015, 0.04))
    supports = [round(last - step * k, 2) for k in (1, 2, 3)]
    resistances = [round(last + step * k, 2) for k in (1, 2, 3)]
    pivot = round((supports[0] + resistances[0] + last) / 3.0, 2)
    return LevelMap(
        ticker=symbol,
        company=company,
        mode="offline-demo",
        last_price=round(last, 2),
        supports=supports,
        resistances=resistances,
        pivot=pivot,
        disclaimer=_DISCLAIMER,
    )


def risk_snapshot(ticker: str) -> RiskSnapshot:
    symbol = normalize_ticker(ticker)
    company, _sector = _company_meta(symbol)
    rng = _rng_for(symbol, 3)
    last = _ref_price(symbol)
    atr_pct = float(rng.uniform(1.2, 5.5))
    beta = float(rng.uniform(0.7, 1.8))
    stop = last * (1.0 - atr_pct / 100.0 * 1.5)
    risk = last - stop
    r1 = last + risk
    note = (
        "Demo sizing: risk a fixed fraction of capital against the stop distance. "
        "Do not size from conviction alone."
    )
    return RiskSnapshot(
        ticker=symbol,
        company=company,
        mode="offline-demo",
        last_price=round(last, 2),
        atr_pct=round(atr_pct, 2),
        beta=round(beta, 2),
        suggested_stop=round(stop, 2),
        risk_per_share=round(risk, 2),
        r_multiple_1r=round(r1, 2),
        position_note=note,
        disclaimer=_DISCLAIMER,
    )


TOOL_HELP = """**Discord Stock Research Bot — tools**

Talk in natural language (preferred):
• `research AAPL`
• `levels on NVDA`
• `risk for TSLA`
• `help`

This public package uses an **offline demo research engine** (deterministic per ticker).
Wire your own market-data and model backends for production research.

Not financial advice. Allowlisted users only.
"""
