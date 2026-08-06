"""Offline stock research helpers (deterministic demo data, no market APIs).

Includes US equity session awareness (premarket / RTH / after-hours) so tape
lines label which print is being shown. Prices stay offline-demo (no yfinance).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime, time
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np

_TICKER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9.\-]{0,9}$")
_ET = ZoneInfo("America/New_York")

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
    """Shared RTH reference price so brief / levels / risk agree on the same symbol."""
    known = _KNOWN.get(ticker.upper())
    if known and isinstance(known.get("base"), (int, float)):
        base = float(known["base"])
        # Small deterministic wobble so cards are not perfectly static numbers.
        wobble = float(_rng_for(ticker, 0).uniform(0.97, 1.03))
        return base * wobble
    return float(_rng_for(ticker, 0).uniform(15, 420))


def us_equity_session(now: datetime | None = None) -> dict[str, Any]:
    """US cash equity session phase in America/New_York.

    Phases: weekend | closed | premarket | rth | afterhours
    Extended hours windows: 04:00-09:30 premarket, 16:00-20:00 afterhours (ET).
    """
    now = now or datetime.now(_ET)
    if now.tzinfo is None:
        now = now.replace(tzinfo=_ET)
    else:
        now = now.astimezone(_ET)
    t = now.time()
    wd = now.weekday()
    if wd >= 5:
        phase = "weekend"
        is_rth = False
        is_extended = False
    elif time(4, 0) <= t < time(9, 30):
        phase = "premarket"
        is_rth = False
        is_extended = True
    elif time(9, 30) <= t < time(16, 0):
        phase = "rth"
        is_rth = True
        is_extended = False
    elif time(16, 0) <= t < time(20, 0):
        phase = "afterhours"
        is_rth = False
        is_extended = True
    else:
        phase = "closed"
        is_rth = False
        is_extended = False
    return {
        "phase": phase,
        "is_rth": is_rth,
        "is_extended_hours": is_extended,
        "et_now": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "weekday": now.strftime("%A"),
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


def session_aware_quote(ticker: str, now: datetime | None = None) -> dict[str, Any]:
    """Deterministic demo quote with RTH + pre/post market prints.

    Mirrors production field names so agents learn to label AFTER-HOURS /
    PRE-MARKET instead of treating the last RTH close as 'current' forever.
    """
    symbol = normalize_ticker(ticker)
    sess = us_equity_session(now)
    phase = str(sess["phase"])
    regular = round(_ref_price(symbol), 2)
    rng = _rng_for(symbol, 11)
    previous_close = round(regular / float(rng.uniform(0.992, 1.012)), 2)
    pre = round(regular * float(rng.uniform(0.994, 1.01)), 2)
    post = round(regular * float(rng.uniform(0.99, 1.015)), 2)

    # Which print is 'current' for this session
    if phase == "premarket":
        live, price_session, label = pre, "premarket", "PRE-MARKET"
    elif phase in {"afterhours", "closed"}:
        # After 20:00 ET still surface last AH print when we have one
        live, price_session, label = post, "afterhours", "AFTER-HOURS"
    elif phase == "weekend":
        live, price_session, label = post, "afterhours", "AFTER-HOURS"
    else:
        live, price_session, label = regular, "rth", "RTH"

    change_pct = (
        round(((live - previous_close) / previous_close) * 100.0, 2)
        if previous_close
        else 0.0
    )
    rth_change_pct = (
        round(((regular - previous_close) / previous_close) * 100.0, 2)
        if previous_close
        else 0.0
    )
    extended_vs_rth_pct = (
        round(((live - regular) / regular) * 100.0, 2)
        if regular and price_session != "rth"
        else None
    )
    return {
        "ticker": symbol,
        "session": sess,
        "price_session": price_session,
        "price_label": label,
        "current_price": live,
        "regular_market_price": regular,
        "previous_close": previous_close,
        "pre_market_price": pre,
        "post_market_price": post,
        "change_pct": change_pct,
        "rth_change_pct": rth_change_pct,
        "extended_vs_rth_pct": extended_vs_rth_pct,
        "mode": "offline-demo",
        "note": (
            f"{label} print is the session-aware current price. "
            "regular_market_price is the last RTH print. "
            "change_pct is vs previous close."
        ),
    }


def _tape_line(quote: dict[str, Any], volume_vs_avg: float | None = None) -> str:
    """One Discord tape line with session label."""
    label = str(quote.get("price_label") or "RTH")
    live = float(quote["current_price"])
    chg = float(quote.get("change_pct") or 0.0)
    chg_s = f"{chg:+.2f}%"
    reg = quote.get("regular_market_price")
    ext = quote.get("extended_vs_rth_pct")
    vol = ""
    if volume_vs_avg is not None:
        vol = _vol_note(float(volume_vs_avg))
    if label in {"AFTER-HOURS", "PRE-MARKET"}:
        extra = ""
        if reg is not None:
            extra = f" | RTH regular **${float(reg):.2f}**"
            if ext is not None:
                extra += f" (ext vs RTH {float(ext):+.2f}%)"
        return f"{label} **${live:.2f}** ({chg_s} vs prior close){extra}{vol}"
    return f"Last **${live:.2f}** (RTH) ({chg_s}){vol}"


def _company_meta(ticker: str) -> tuple[str, str]:
    known = _KNOWN.get(ticker.upper())
    if known:
        name = str(known.get("name") or ticker)
        sector = str(known.get("sector") or "Technology")
        return name, sector
    rng = _rng_for(ticker, 7)
    sector = SECTORS[int(rng.integers(0, len(SECTORS)))]
    return ticker, sector


def _conviction_word(n: int) -> str:
    """Map 1-5 demo score to production low/med/high words (no bar graphs)."""
    n = max(1, min(int(n), 5))
    if n <= 2:
        return "low"
    if n <= 3:
        return "med"
    return "high"


# Discord-native markdown (matches production agent shape: section headers
# + epistemic tags). No ASCII bars, sparklines, or box cards.

_BIAS_COLOR = {
    "bullish": 0x57F287,  # Discord green
    "bearish": 0xED4245,  # Discord red
    "neutral": 0xFEE75C,  # Discord yellow
}
_LEVEL_COLOR = 0x5865F2
_RISK_COLOR = 0xEB459E


def _bias_label(bias: str) -> str:
    return {
        "bullish": "bullish",
        "bearish": "bearish",
        "neutral": "neutral / range",
    }.get(bias, bias)


def _lean_tag(bias: str) -> str:
    return f"{_bias_label(bias)} (INFERRED)"


def _vol_note(volume_vs_avg: float) -> str:
    vr = float(volume_vs_avg)
    if vr >= 1.5:
        return f" | heavy volume (~{vr:.1f}x avg)"
    if vr <= 0.7:
        return f" | light volume (~{vr:.1f}x avg)"
    return f" | volume ~{vr:.1f}x avg"


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
    thesis: str
    catalysts: list[str]
    risks: list[str]
    invalidation: str
    disclaimer: str
    price_session: str = "rth"
    price_label: str = "RTH"
    regular_market_price: float | None = None
    previous_close: float | None = None
    pre_market_price: float | None = None
    post_market_price: float | None = None
    extended_vs_rth_pct: float | None = None
    tape_line: str = ""

    def as_dict(self) -> dict:
        return asdict(self)

    def format_message(self) -> str:
        """Discord markdown research reply (production agent shape).

        Summary-first sections + epistemic tags. Plain words only - no bars
        or sparkline cosplay. Tape line labels AFTER-HOURS / PRE-MARKET when
        outside RTH so demo agents practice session-aware pricing.
        """
        conv = _conviction_word(self.conviction)
        tape = self.tape_line or (
            f"Last **${self.last_price:.2f}** ({self.change_pct:+.2f}%)"
            f"{_vol_note(self.volume_vs_avg)}"
        )
        lines: list[str] = [
            f"**{self.ticker} | research**",
            f"`as_of {self.mode}` | {self.company} | {self.sector} | paper research only",
            "",
            "**Read** | INFERRED",
            self.thesis,
            "",
            "**1 | Tape** | VERIFIED (demo OHLCV, session-aware)",
            tape,
            "",
            "**2 | Lean** | INFERRED",
            f"**{_lean_tag(self.bias)}** | conviction **{conv}**",
            "",
            "**3 | Catalysts** | PROBABLE",
        ]
        for c in self.catalysts:
            lines.append(f"- {c}")
        lines.append("")
        lines.append("**4 | Risks** | PROBABLE")
        for r in self.risks:
            lines.append(f"- {r}")
        lines.append("")
        lines.append("**Invalidation**")
        lines.append(self.invalidation)
        lines.append("")
        lines.append(f"_{self.disclaimer}_")
        return "\n".join(lines)

    def as_embed_dict(self) -> dict:
        """Optional Embed wrapper; production path prefers plain markdown."""
        body = self.format_message()
        # Discord embed description hard limit ~4096
        return {
            "title": f"{self.ticker}  |  {self.company}",
            "description": body[:4000],
            "color": _BIAS_COLOR.get(self.bias, 0x99AAB5),
            "footer": {"text": self.disclaimer[:2048]},
        }


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
    price_label: str = "RTH"
    tape_line: str = ""

    def as_dict(self) -> dict:
        return asdict(self)

    def format_message(self) -> str:
        """Discord markdown levels reply (chart-read style)."""
        nearest_s = min(self.supports, key=lambda x: abs(x - self.last_price))
        nearest_r = min(self.resistances, key=lambda x: abs(x - self.last_price))
        room_up = (nearest_r - self.last_price) / self.last_price * 100.0
        room_dn = (self.last_price - nearest_s) / self.last_price * 100.0
        s_str = ", ".join(f"${s:.2f}" for s in sorted(self.supports, reverse=True))
        r_str = ", ".join(f"${r:.2f}" for r in sorted(self.resistances))
        px_note = self.tape_line or f"**${self.last_price:.2f}** ({self.price_label})"
        lines = [
            f"**{self.ticker} | levels**",
            f"`as_of {self.mode}` | {self.company} | paper research only",
            "",
            "**Take** | INFERRED",
            (
                f"Price sits near {px_note} with pivot **${self.pivot:.2f}**. "
                f"Nearest resistance **${nearest_r:.2f}** (+{room_up:.1f}%); "
                f"nearest support **${nearest_s:.2f}** (-{room_dn:.1f}%)."
            ),
            "",
            "**Levels that matter** | VERIFIED (demo)",
            f"Support: {s_str}",
            f"Resistance: {r_str}",
            f"Pivot: **${self.pivot:.2f}**",
            "",
            "**What I'm watching**",
            f"- Clean hold above **${nearest_s:.2f}** with volume",
            f"- Break / reclaim of **${nearest_r:.2f}**",
            "",
            f"_{self.disclaimer}_",
        ]
        return "\n".join(lines)

    def as_embed_dict(self) -> dict:
        body = self.format_message()
        return {
            "title": f"{self.ticker}  |  Levels",
            "description": body[:4000],
            "color": _LEVEL_COLOR,
            "footer": {"text": self.disclaimer[:2048]},
        }


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
    price_label: str = "RTH"
    tape_line: str = ""

    def as_dict(self) -> dict:
        return asdict(self)

    def format_message(self) -> str:
        """Discord markdown risk reply (production agent shape)."""
        if self.atr_pct >= 3.5:
            heat = "hot"
        elif self.atr_pct <= 2.0:
            heat = "calm"
        else:
            heat = "normal"
        risk_pct = self.risk_per_share / self.last_price * 100.0 if self.last_price else 0.0
        px = self.tape_line or f"Last **${self.last_price:.2f}** ({self.price_label})"
        lines = [
            f"**{self.ticker} | risk**",
            f"`as_of {self.mode}` | {self.company} | paper research only",
            "",
            "**Read** | INFERRED",
            (
                f"{px}. ATR **{self.atr_pct:.2f}%** ({heat}), "
                f"beta **{self.beta:.2f}**. Demo stop **${self.suggested_stop:.2f}** "
                f"(~{risk_pct:.1f}% risk/share); 1R target **${self.r_multiple_1r:.2f}**."
            ),
            "",
            "**Sizing note** | PROBABLE",
            self.position_note,
            "",
            f"_{self.disclaimer}_",
        ]
        return "\n".join(lines)

    def as_embed_dict(self) -> dict:
        body = self.format_message()
        return {
            "title": f"{self.ticker}  |  Risk",
            "description": body[:4000],
            "color": _RISK_COLOR,
            "footer": {"text": self.disclaimer[:2048]},
        }


def research_brief(ticker: str, now: datetime | None = None) -> ResearchBrief:
    symbol = normalize_ticker(ticker)
    company, sector = _company_meta(symbol)
    rng = _rng_for(symbol, 1)
    quote = session_aware_quote(symbol, now=now)
    last = float(quote["current_price"])
    change = float(quote["change_pct"])
    # Known names lean constructive so the public demo does not look random-garbage.
    if symbol in _KNOWN:
        weights = np.array([0.55, 0.25, 0.20])  # bullish, neutral, bearish
        bias = str(rng.choice(BIASES, p=weights / weights.sum()))
    else:
        bias = BIASES[int(rng.integers(0, len(BIASES)))]
    conviction = int(rng.integers(2, 6))
    vol = float(rng.uniform(0.6, 2.4))
    tape = _tape_line(quote, vol)

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
        thesis=thesis,
        catalysts=catalysts,
        risks=risks,
        invalidation=invalidation,
        disclaimer=_DISCLAIMER,
        price_session=str(quote["price_session"]),
        price_label=str(quote["price_label"]),
        regular_market_price=quote.get("regular_market_price"),
        previous_close=quote.get("previous_close"),
        pre_market_price=quote.get("pre_market_price"),
        post_market_price=quote.get("post_market_price"),
        extended_vs_rth_pct=quote.get("extended_vs_rth_pct"),
        tape_line=tape,
    )


def level_map(ticker: str, now: datetime | None = None) -> LevelMap:
    symbol = normalize_ticker(ticker)
    company, _sector = _company_meta(symbol)
    rng = _rng_for(symbol, 2)
    quote = session_aware_quote(symbol, now=now)
    last = float(quote["current_price"])
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
        price_label=str(quote["price_label"]),
        tape_line=_tape_line(quote),
    )


def risk_snapshot(ticker: str, now: datetime | None = None) -> RiskSnapshot:
    symbol = normalize_ticker(ticker)
    company, _sector = _company_meta(symbol)
    rng = _rng_for(symbol, 3)
    quote = session_aware_quote(symbol, now=now)
    last = float(quote["current_price"])
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
        price_label=str(quote["price_label"]),
        tape_line=_tape_line(quote),
    )


TOOL_HELP = """**Equity Research Agent - tools**

Talk in natural language (preferred):
- `research AAPL`
- `levels on NVDA`
- `risk for TSLA`
- `session` / `is market open`
- `help`

This public package uses an **offline demo research engine** (deterministic per ticker)
with **session-aware** tape labels (RTH / PRE-MARKET / AFTER-HOURS).
Wire live market-data backends for production research.

Not financial advice. Allowlisted users only.
"""
