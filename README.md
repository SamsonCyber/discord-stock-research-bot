<p align="center">
  <img src="assets/banner.png" alt="Equity Research Agent banner" width="100%"/>
</p>

<p align="center">
  <strong>Equity Research Agent</strong> - natural-language equity research over Discord DMs.<br/>
  You type a message. The agent runs tools and returns a structured brief (thesis, levels, risk).<br/>
  Discord DM adapter included. Slash commands and brokerage order routing are out of scope.
</p>

<p align="center">
  <a href="https://github.com/SamsonCyber/equity-research-agent/actions/workflows/ci.yml"><img src="https://github.com/SamsonCyber/equity-research-agent/actions/workflows/ci.yml/badge.svg" alt="CI"/></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&amp;logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/license-MIT-emerald" alt="MIT"/>
  <img src="https://img.shields.io/badge/UX-natural%20language%20DMs-5865F2?logo=discord&amp;logoColor=white" alt="Discord DMs"/>
  <img src="https://img.shields.io/badge/offline%20demo-no%20API%20keys-22d3ee" alt="Offline demo"/>
</p>

<p align="center">
  <a href="#try-it-in-10-seconds"><strong>Try offline</strong></a> |
  <a href="assets/interactive-demo.html"><strong>Interactive demo</strong></a> |
  <a href="#discord-setup">Discord setup</a> |
  <a href="docs/PRODUCTION_TOOLS.md">Production tool catalog</a>
</p>

---

## Product

You type in a DM:

```text
research AAPL
```

The agent returns this structured brief. Same offline engine as the CLI:

```bash
python -m equity_research_agent.demo research AAPL
```

~~~~text
**AAPL | research**
`as_of offline-demo` | Apple | Technology | paper research only

**Read** | INFERRED
Apple (AAPL) is range-bound in this offline model. No edge until a clean break with volume. Size small or wait; fake breaks are the default.

**1 | Tape** | VERIFIED (demo OHLCV, session-aware)
AFTER-HOURS **$203.57** (+1.78% vs prior close) | RTH regular **$200.99** (ext vs RTH +1.28%) | volume ~1.5x avg

**2 | Lean** | INFERRED
**neutral / range (INFERRED)** | conviction **med**

**3 | Catalysts** | PROBABLE
- Range break with expanding volume
- Catalyst calendar (earnings / product / event)
- Technology leadership change that pulls the name

**4 | Risks** | PROBABLE
- Whipsaw inside the range
- Low-liquidity fake break
- Macro headline risk that rewrites the tape

**Invalidation**
Two closes outside $194.96-$207.02 (demo band)

_Demo research data only. Offline / deterministic. Not live market data. Not financial advice._

_tools used: research_
~~~~

Checked-in copy of that reply: [`docs/samples/aapl-research.txt`](docs/samples/aapl-research.txt). Regenerate with:

```bash
python scripts/build_showcase.py
```

| You say | What happens |
|---|---|
| `research AAPL` | Thesis, bias, conviction, catalysts, risks, invalidation |
| `levels on NVDA` | Support / resistance ladder around a shared ref price |
| `risk for TSLA` | ATR%, beta, demo stop, risk/share, 1R target |
| `help` | Tool catalog |

Research runs on DMs only. The allowlist is fail-closed. Guild channel messages are ignored.

---

## Try it in 10 seconds

No Discord token. No market API keys. No account.

```bash
git clone https://github.com/SamsonCyber/equity-research-agent.git
cd equity-research-agent
python -m venv .venv
# Windows: .venv\Scripts\activate
# POSIX:   source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
python -m equity_research_agent.demo research AAPL
```

Also:

```bash
python -m equity_research_agent.demo levels on NVDA
python -m equity_research_agent.demo "risk for TSLA"
python -m equity_research_agent.demo help
```

### Click-through demo (no install)

Open the in-repo UI (self-contained HTML, engine payloads baked in):

**[assets/interactive-demo.html](assets/interactive-demo.html)**

Pick AAPL / NVDA / TSLA / MSFT / AMD and flip research | levels | risk. Same deterministic engine as the CLI.

---

## Architecture

<p align="center">
  <img src="assets/architecture.svg" alt="Flow: DM to allowlist to agent to tools to research reply" width="900"/>
</p>

```text
  natural language  ->  allowlist gate  ->  intent classify  ->  tools  ->  research reply
       DM only           fail-closed         research|levels|risk         + tools footer
```

| Module | Role |
|---|---|
| [`bot.py`](src/equity_research_agent/bot.py) | Discord DM gateway |
| [`agent.py`](src/equity_research_agent/agent.py) | NL turn: intent -> tools -> reply |
| [`tools.py`](src/equity_research_agent/tools.py) | Tool registry |
| [`research.py`](src/equity_research_agent/research.py) | Offline deterministic engine |
| [`auth.py`](src/equity_research_agent/auth.py) | Fail-closed allowlist |
| [`demo.py`](src/equity_research_agent/demo.py) | Offline CLI |

---

## Tools in this package

| Tool | Card you get |
|---|---|
| `research` | Company, sector, bias, conviction, price, thesis, catalysts, risks, invalidation |
| `levels` | Shared ref price, pivot, support/resistance ladder |
| `risk` | ATR heat, beta, demo stop, risk/share, 1R target |
| `list_tools` | Catalog (`help`) |

Every card is tagged `offline-demo`: deterministic per ticker, not live market data.

Famous symbols (AAPL, NVDA, TSLA, ...) resolve to real sectors and company names so demos look intentional. Prices stay synthetic.

### Private production surface

A private deploy can keep this UX and attach a larger research tool graph (charts, fundamentals, SEC/EDGAR, thesis memory, macro packs, and similar).

That inventory is documented here, not shipped as live handlers in this clone:

**[docs/PRODUCTION_TOOLS.md](docs/PRODUCTION_TOOLS.md)** (~72 tools, owner view)

---

## Discord setup

1. [Discord Developer Portal](https://discord.com/developers/applications) -> bot
2. Enable **Message Content Intent**
3. Allowlist your Discord user ID
4. DM the bot (guild messages ignored on purpose)

```bash
cp .env.example .env
# STOCK_RESEARCH_DISCORD_TOKEN=...
# STOCK_RESEARCH_ALLOWED_USER_IDS=your_id
python -m equity_research_agent.bot
```

| Variable | Required | Purpose |
|---|---|---|
| `STOCK_RESEARCH_DISCORD_TOKEN` | yes | Bot token |
| `STOCK_RESEARCH_ALLOWED_USER_IDS` | yes | Comma-separated user IDs |
| `STOCK_RESEARCH_ALLOWED_USER_IDS_FILE` | no | File of IDs |

If the allowlist is empty, the process refuses to start.

```bash
python scripts/live_smoke.py   # connect check; never prints the token
```

---

## Compared with a typical Discord stock bot

| Typical Discord bot | This package |
|---|---|
| `/price AAPL` | free-text like `what do you think about AAPL?` |
| Fixed slash surface | Intent maps to a tool registry |
| Guild channel noise | DM-only research path |
| Open to everyone | Fail-closed allowlist |
| Live quote styling without honest labels | Offline-demo labels on public tools |

You talk in a DM. The agent runs tools and returns research.

---

## License

MIT. See [LICENSE](LICENSE).
