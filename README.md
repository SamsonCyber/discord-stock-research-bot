# Discord Stock Research Bot

### Talk to it like a desk analyst. It runs the tools.

[![CI](https://github.com/SamsonCyber/discord-stock-research-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/SamsonCyber/discord-stock-research-bot/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/UX-natural%20language%20DMs-5865F2.svg)](https://github.com/SamsonCyber/discord-stock-research-bot)

**A natural-language stock research agent for Discord.**  
You type English. It classifies intent, runs research tools, and answers with a structured brief. No slash-command menu. No brokerage. No fake live quotes pretending to be production.

```bash
# try it in 10 seconds (no Discord token, no market API keys)
pip install -e ".[dev]"
python -m discord_stock_research_bot.demo research AAPL
```

---

<p align="center">
  <img src="assets/architecture.svg" alt="Architecture: Discord DM to allowlist to agent to tools to research reply" width="920"/>
</p>

---

## Why this exists

Most Discord "stock bots" are slash menus and price tickers. This one is different:

| Most bots | This bot |
|---|---|
| `/price AAPL` | `what do you think about AAPL?` |
| Fixed command surface | Intent → tool registry |
| Guild channel noise | **DM-only** research path |
| Open to everyone | **Fail-closed allowlist** |

Same product shape as a serious research agent: **you talk, tools run, research comes back.**  
This public package ships a deterministic offline engine so anyone can clone, run, and learn the architecture without keys.

---

## Try it offline (primary demo path)

```bash
git clone https://github.com/SamsonCyber/discord-stock-research-bot.git
cd discord-stock-research-bot
python -m venv .venv
# Windows: .venv\Scripts\activate
# POSIX:   source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q

python -m discord_stock_research_bot.demo research AAPL
python -m discord_stock_research_bot.demo levels on NVDA
python -m discord_stock_research_bot.demo "risk for TSLA"
python -m discord_stock_research_bot.demo help
```

---

## Real sample reply

Exact output from `python -m discord_stock_research_bot.demo research AAPL`  
(checked in under [`docs/samples/aapl-research.txt`](docs/samples/aapl-research.txt); deterministic per ticker):

```text
**AAPL** research brief (`offline-demo`)
Sector: Energy · Bias: **bullish** · Conviction: 4/5
Ref price: `$319.46` (-1.75%) · Vol vs avg: `1.79x`

**Thesis**
AAPL shows constructive relative strength in this demo model. Watch for continuation if price holds above near support and volume stays elevated.

**Catalysts**
  • Product or segment growth narrative improving
  • Multiple expansion if guidance holds
  • Technical reclaim of recent range high

**Risks**
  • Earnings or guidance miss
  • Sector rotation away from growth
  • Break of structure under nearest support

**Invalidation:** Daily close below $300.29 (demo level)

_Demo research data only. Offline / deterministic. Not live market data. Not financial advice._

_tools used: research_
```

Same shape lands in a Discord DM when the bot is running.

---

## How a turn works

```text
  "research AAPL"  or  "levels on TSLA"  or  "risk for MSFT"
              │
              ▼
     ┌─────────────────┐
     │  allowlist gate │  fail-closed; guild chat ignored
     └────────┬────────┘
              ▼
     ┌─────────────────┐
     │  research agent │  classify intent · extract tickers
     └────────┬────────┘
              ▼
     ┌──────────────────────────────────┐
     │  tools: research · levels · risk │
     └────────┬─────────────────────────┘
              ▼
     structured brief + "tools used" footer
```

| Module | Role |
|---|---|
| [`bot.py`](src/discord_stock_research_bot/bot.py) | Discord DM gateway |
| [`agent.py`](src/discord_stock_research_bot/agent.py) | NL turn: intent → tools → reply |
| [`tools.py`](src/discord_stock_research_bot/tools.py) | Tool registry |
| [`research.py`](src/discord_stock_research_bot/research.py) | Offline deterministic engine |
| [`auth.py`](src/discord_stock_research_bot/auth.py) | Fail-closed allowlist |
| [`demo.py`](src/discord_stock_research_bot/demo.py) | Offline NL CLI |

---

## Tools in this package

| Tool | What you get |
|---|---|
| `research` | Bias, conviction, thesis, catalysts, risks, invalidation |
| `levels` | Support / resistance map + pivot |
| `risk` | ATR%, beta, demo stop distance, risk per share |
| `list_tools` | Catalog (also used by `help`) |

Every response is labeled **`offline-demo`**: deterministic per ticker, not live market data.

### Production-scale surface (private deploy)

A full private research agent can grow to **~72 tools** (charts, fundamentals, SEC/EDGAR, thesis memory, macro packs, and more) while keeping the same NL Discord UX.

That catalog is **not** live in this clone. See the honest inventory:

**[docs/PRODUCTION_TOOLS.md](docs/PRODUCTION_TOOLS.md)**

---

## Discord (when you want DMs)

1. Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Enable **Message Content Intent**.
3. Allowlist your Discord user ID.
4. Start the bot and **open a DM** (guild messages are ignored on purpose).

```bash
cp .env.example .env
# set STOCK_RESEARCH_DISCORD_TOKEN and STOCK_RESEARCH_ALLOWED_USER_IDS
python -m discord_stock_research_bot.bot
```

| Variable | Required | Purpose |
|---|---|---|
| `STOCK_RESEARCH_DISCORD_TOKEN` | yes | Bot token |
| `STOCK_RESEARCH_ALLOWED_USER_IDS` | yes | Comma-separated Discord user IDs |
| `STOCK_RESEARCH_ALLOWED_USER_IDS_FILE` | no | File of IDs (one per line) |

Empty allowlist → **process refuses to start**.

Optional connect check (never prints the token):

```bash
python scripts/live_smoke.py
```

### What you can say

| You say | Tools run |
|---|---|
| `research AAPL` | `research` |
| `what's the outlook on NVDA?` | `research` |
| `levels on TSLA` | `levels` |
| `risk for AMD` | `risk` |
| `help` | `list_tools` |

---

## Security posture

- **DM-only** research path
- **Fail-closed allowlist** on every turn
- No brokerage, order router, or wallet code
- No secrets in git
- Public package stays offline-first for research data

Details: [SECURITY.md](SECURITY.md) · [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)

---

## Public package vs private production agent

| | This repo (public) | Private production agent |
|---|---|---|
| UX | Natural language DMs | Natural language DMs |
| Agent | Lightweight intent → tools | LLM tool loop over large graph |
| Data | Offline deterministic demo | Live market data + models |
| Auth | Allowlist | Allowlist + stronger gateway |
| Tools | 4 offline tools | ~72 research tools (see [catalog](docs/PRODUCTION_TOOLS.md)) |

Same idea either way: **you talk, tools run, research comes back.**

---

## Project status

See [STATUS.md](STATUS.md) and [CHANGELOG.md](CHANGELOG.md).

---

## License

MIT. See [LICENSE](LICENSE).

**Not financial advice.** Demo data is not live market data. You own your risk.
