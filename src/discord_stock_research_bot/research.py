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


def _sparkline(ticker: str, last: float, n: int = 20) -> str:
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


def _pct_bar(value: float, lo: float, hi: float, width: int = 10) -> str:
    """Map value into a fixed-width bar between lo and hi."""
    if hi <= lo:
        return "░" * width
    t = (float(value) - lo) / (hi - lo)
    t = max(0.0, min(1.0, t))
    filled = int(round(t * width))
    return "█" * filled + "░" * (width - filled)


# Terminal cards: no markdown. Discord uses Embeds (see as_embed_dict).
_CARD_W = 46

_BIAS_COLOR = {
    "bullish": 0x57F287,  # Discord green
    "bearish": 0xED4245,  # Discord red
    "neutral": 0xFEE75C,  # Discord yellow
}
_LEVEL_COLOR = 0x5865F2
_RISK_COLOR = 0xEB459E


def _wrap(text: str, width: int) -> list[str]:
    words = (text or "").split()
    if not words:
        return [""]
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        if len(cur) + 1 + len(w) <= width:
            cur = f"{cur} {w}"
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def _box(title: str, body_lines: list[str], *, width: int = _CARD_W) -> str:
    """Monospace card that looks right in a terminal (no Discord markdown)."""
    inner = width - 2
    top = "┌" + "─" * inner + "┐"
    mid = "├" + "─" * inner + "┤"
    bot = "└" + "─" * inner + "┘"

    def row(text: str = "") -> str:
        t = text[:inner]
        return "│" + t.ljust(inner) + "│"

    out = [top]
    # Title can be two lines
    for part in title.split("\n"):
        out.append(row(f" {part}"))
    out.append(mid)
    for line in body_lines:
        if line == "---":
            out.append(mid)
            continue
        if not line:
            out.append(row(""))
            continue
        # Section headers flush left
        if line.endswith(":") and line.upper() == line:
            out.append(row(f" {line}"))
            continue
        # Pre-aligned rows (kv / ladder): keep spacing, do not strip
        if line.startswith("  "):
            if len(line) <= inner:
                out.append(row(line))
            else:
                # Long catalyst/risk lines: hang under the number
                prefix = "   "
                chunks = _wrap(line.strip(), inner - len(prefix))
                for chunk in chunks:
                    out.append(row(f"{prefix}{chunk}"))
            continue
        for chunk in _wrap(line, inner - 1):
            out.append(row(f" {chunk}"))
    out.append(bot)
    return "\n".join(out)


def _level_ladder_lines(last: float, supports: list[float], resistances: list[float]) -> list[str]:
    rows: list[tuple[float, str, str]] = []
    for i, r in enumerate(sorted(resistances, reverse=True), start=1):
        dist = (r - last) / last * 100.0
        rows.append((r, "R", f"R{i} +{dist:.1f}%"))
    rows.append((last, "P", "LAST"))
    for i, s in enumerate(sorted(supports, reverse=True), start=1):
        dist = (s - last) / last * 100.0
        rows.append((s, "S", f"S{i} {dist:.1f}%"))

    prices = [p for p, _, _ in rows]
    lo, hi = min(prices), max(prices)
    span = max(hi - lo, 1e-9)
    lines: list[str] = []
    for price, kind, label in rows:
        pos = int(round((price - lo) / span * 10))
        track = list("·" * 11)
        track[pos] = "●" if kind == "P" else ("▲" if kind == "R" else "▼")
        rail = "".join(track)
        if kind == "P":
            lines.append(f"  {rail} ${price:>8.2f}  << LAST")
        else:
            lines.append(f"  {rail} ${price:>8.2f}  {label}")
    return lines


def _kv_lines(rows: list[tuple[str, str]]) -> list[str]:
    key_w = max(len(k) for k, _ in rows)
    return [f"  {k:<{key_w}}  {v}" for k, v in rows]


def _bias_label(bias: str) -> str:
    return {
        "bullish": "BULL  ▲",
        "bearish": "BEAR  ▼",
        "neutral": "NEUTRAL  ◆",
    }.get(bias, bias.upper())


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
        """Terminal / plain-text card. No markdown (looks correct in CLI)."""
        chg_s = f"{self.change_pct:+.2f}%"
        direction = "up" if self.change_pct >= 0 else "down"
        bar = _conviction_bar(self.conviction)
        vol_bar = _pct_bar(self.volume_vs_avg, 0.5, 2.5, width=8)
        body: list[str] = []
        body.extend(
            _kv_lines(
                [
                    ("BIAS", _bias_label(self.bias)),
                    ("CONVICTION", f"{bar}  {self.conviction}/5"),
                    ("PRICE", f"${self.last_price:.2f}  {chg_s}  ({direction})"),
                    ("VOLUME", f"{vol_bar}  {self.volume_vs_avg:.2f}x avg"),
                    ("TAPE", self.sparkline),
                ]
            )
        )
        body.append("---")
        body.append("THESIS:")
        body.append(f"  {self.thesis}")
        body.append("")
        body.append("CATALYSTS:")
        for i, c in enumerate(self.catalysts, 1):
            body.append(f"  {i}. {c}")
        body.append("")
        body.append("RISKS:")
        for i, r in enumerate(self.risks, 1):
            body.append(f"  {i}. {r}")
        body.append("")
        body.append("INVALIDATION:")
        body.append(f"  {self.invalidation}")
        body.append("---")
        body.append(f"  {self.disclaimer}")
        title = f"{self.ticker}  ·  {self.company}\n{self.sector}  ·  {self.mode}"
        return _box(title, body)

    def as_embed_dict(self) -> dict:
        """Discord Embed payload (render as a real embed, not raw markdown)."""
        bar = _conviction_bar(self.conviction)
        chg_s = f"{self.change_pct:+.2f}%"
        cats = "\n".join(f"**{i}.** {c}" for i, c in enumerate(self.catalysts, 1))
        risks = "\n".join(f"**{i}.** {r}" for i, r in enumerate(self.risks, 1))
        return {
            "title": f"{self.ticker}  ·  {self.company}",
            "description": f"**{self.sector}** · `{self.mode}`\n`{self.sparkline}`",
            "color": _BIAS_COLOR.get(self.bias, 0x99AAB5),
            "fields": [
                {"name": "Bias", "value": _bias_label(self.bias), "inline": True},
                {
                    "name": "Conviction",
                    "value": f"{bar}  **{self.conviction}/5**",
                    "inline": True,
                },
                {
                    "name": "Price",
                    "value": f"**${self.last_price:.2f}**  ({chg_s})",
                    "inline": True,
                },
                {
                    "name": "Volume",
                    "value": f"**{self.volume_vs_avg:.2f}x** avg",
                    "inline": True,
                },
                {"name": "Thesis", "value": self.thesis[:1024], "inline": False},
                {"name": "Catalysts", "value": cats[:1024], "inline": False},
                {"name": "Risks", "value": risks[:1024], "inline": False},
                {"name": "Invalidation", "value": self.invalidation[:1024], "inline": False},
            ],
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

    def as_dict(self) -> dict:
        return asdict(self)

    def format_message(self) -> str:
        nearest_s = min(self.supports, key=lambda x: abs(x - self.last_price))
        nearest_r = min(self.resistances, key=lambda x: abs(x - self.last_price))
        room_up = (nearest_r - self.last_price) / self.last_price * 100.0
        room_dn = (self.last_price - nearest_s) / self.last_price * 100.0
        body: list[str] = []
        body.extend(
            _kv_lines(
                [
                    ("LAST", f"${self.last_price:.2f}"),
                    ("PIVOT", f"${self.pivot:.2f}"),
                    ("NEAREST R", f"${nearest_r:.2f}  (+{room_up:.1f}%)"),
                    ("NEAREST S", f"${nearest_s:.2f}  (-{room_dn:.1f}%)"),
                ]
            )
        )
        body.append("---")
        body.append("LADDER:")
        body.extend(_level_ladder_lines(self.last_price, self.supports, self.resistances))
        body.append("---")
        body.append(f"  {self.disclaimer}")
        title = f"{self.ticker}  ·  LEVELS\n{self.company}  ·  {self.mode}"
        return _box(title, body)

    def as_embed_dict(self) -> dict:
        nearest_s = min(self.supports, key=lambda x: abs(x - self.last_price))
        nearest_r = min(self.resistances, key=lambda x: abs(x - self.last_price))
        room_up = (nearest_r - self.last_price) / self.last_price * 100.0
        room_dn = (self.last_price - nearest_s) / self.last_price * 100.0
        ladder = "\n".join(
            _level_ladder_lines(self.last_price, self.supports, self.resistances)
        )
        return {
            "title": f"{self.ticker}  ·  Levels",
            "description": f"**{self.company}** · `{self.mode}`",
            "color": _LEVEL_COLOR,
            "fields": [
                {
                    "name": "Last",
                    "value": f"**${self.last_price:.2f}**",
                    "inline": True,
                },
                {"name": "Pivot", "value": f"**${self.pivot:.2f}**", "inline": True},
                {
                    "name": "Nearest R / S",
                    "value": (
                        f"R **${nearest_r:.2f}** (+{room_up:.1f}%)\n"
                        f"S **${nearest_s:.2f}** (-{room_dn:.1f}%)"
                    ),
                    "inline": False,
                },
                {
                    "name": "Ladder",
                    "value": f"```\n{ladder}\n```"[:1024],
                    "inline": False,
                },
            ],
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

    def as_dict(self) -> dict:
        return asdict(self)

    def format_message(self) -> str:
        if self.atr_pct >= 3.5:
            heat = "HOT"
        elif self.atr_pct <= 2.0:
            heat = "CALM"
        else:
            heat = "NORMAL"
        atr_bar = _pct_bar(self.atr_pct, 1.0, 6.0, width=8)
        beta_bar = _pct_bar(self.beta, 0.5, 2.0, width=8)
        risk_pct = self.risk_per_share / self.last_price * 100.0 if self.last_price else 0.0
        body: list[str] = []
        body.extend(
            _kv_lines(
                [
                    ("LAST", f"${self.last_price:.2f}"),
                    ("ATR%", f"{atr_bar}  {self.atr_pct:.2f}%  [{heat}]"),
                    ("BETA", f"{beta_bar}  {self.beta:.2f}"),
                    ("STOP", f"${self.suggested_stop:.2f}  (demo)"),
                    ("RISK/SH", f"${self.risk_per_share:.2f}  ({risk_pct:.1f}% of last)"),
                    ("1R TGT", f"${self.r_multiple_1r:.2f}  (demo)"),
                ]
            )
        )
        body.append("---")
        body.append("NOTE:")
        body.append(f"  {self.position_note}")
        body.append("---")
        body.append(f"  {self.disclaimer}")
        title = f"{self.ticker}  ·  RISK\n{self.company}  ·  {self.mode}"
        return _box(title, body)

    def as_embed_dict(self) -> dict:
        if self.atr_pct >= 3.5:
            heat = "HOT"
        elif self.atr_pct <= 2.0:
            heat = "CALM"
        else:
            heat = "NORMAL"
        atr_bar = _pct_bar(self.atr_pct, 1.0, 6.0, width=8)
        beta_bar = _pct_bar(self.beta, 0.5, 2.0, width=8)
        risk_pct = self.risk_per_share / self.last_price * 100.0 if self.last_price else 0.0
        return {
            "title": f"{self.ticker}  ·  Risk",
            "description": f"**{self.company}** · `{self.mode}`",
            "color": _RISK_COLOR,
            "fields": [
                {
                    "name": "Last",
                    "value": f"**${self.last_price:.2f}**",
                    "inline": True,
                },
                {
                    "name": "ATR%",
                    "value": f"{atr_bar}\n**{self.atr_pct:.2f}%** [{heat}]",
                    "inline": True,
                },
                {
                    "name": "Beta",
                    "value": f"{beta_bar}\n**{self.beta:.2f}**",
                    "inline": True,
                },
                {
                    "name": "Stop (demo)",
                    "value": f"**${self.suggested_stop:.2f}**",
                    "inline": True,
                },
                {
                    "name": "Risk / share",
                    "value": f"**${self.risk_per_share:.2f}** ({risk_pct:.1f}%)",
                    "inline": True,
                },
                {
                    "name": "1R target (demo)",
                    "value": f"**${self.r_multiple_1r:.2f}**",
                    "inline": True,
                },
                {"name": "Note", "value": self.position_note[:1024], "inline": False},
            ],
            "footer": {"text": self.disclaimer[:2048]},
        }


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
