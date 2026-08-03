# Discord Stock Research Bot

**Talk to it in normal language. It runs stock research tools for you.**

This is a Discord research bot, not a slash-command toy and not a paper-trading app. You DM it like a desk analyst:

```text
research AAPL
what do you think about NVDA?
levels on TSLA
risk for MSFT
help
```

The bot classifies your ask, calls the matching tools, and replies with the research.

[![CI](https://github.com/SamsonCyber/discord-stock-research-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/SamsonCyber/discord-stock-research-bot/actions/workflows/ci.yml)

---

## What it is

An **allowlisted natural-language stock research agent on Discord**.

| Layer | Job |
|---|---|
| Discord DMs | You chat in plain English |
| Allowlist | Only authorized users get a turn |
| Agent | Reads your message, picks tools, runs them |
| Tools | Research brief, levels, risk, list_tools |
| Reply | Structured research answer back in the DM |

Full production agentic research bots use an LLM ReAct loop over a large tool graph (charts, fundamentals, SEC, thesis, …). **This public package keeps the same UX shape** — natural language in, tools run, research out — with an offline demo engine so you can clone and use it without brokerage keys.

---

## How you use it

### In Discord (primary)

1. Allowlist your Discord user ID.
2. Enable **Message Content Intent** on the bot application.
3. Start the bot.
4. **Open a DM** with the bot (guild chat is ignored on purpose).
5. Type research questions in normal language.

Examples that work out of the box:

| You say | Tools run |
|---|---|
| `research AAPL` | `research` |
| `what's the outlook on NVDA?` | `research` |
| `levels on TSLA` | `levels` |
| `support and resistance for MSFT` | `levels` |
| `risk for AMD` | `risk` |
| `help` / `what can you do` | `list_tools` |

You do **not** need slash commands. Natural language is the interface.

### Offline (no Discord, no token)

Same agent, same tools, terminal only:

```bash
python -m discord_stock_research_bot.demo research AAPL
python -m discord_stock_research_bot.demo levels on NVDA
python -m discord_stock_research_bot.demo "risk for TSLA"
python -m discord_stock_research_bot.demo help
python -m discord_stock_research_bot.demo research AAPL --json
```

---

## Tools the agent can run

### Public package (this repo)

Offline demo tools so you can clone without brokerage or market-data keys:

| Tool | What it returns |
|---|---|
| `research` | Bias, conviction, thesis, catalysts, risks, invalidation |
| `levels` | Support / resistance map + pivot |
| `risk` | ATR%, beta, demo stop distance, risk per share |
| `list_tools` | Tool catalog (also used by `help`) |

Every public-package tool response is labeled **offline-demo**: deterministic per ticker, not live quotes. Swap `research.py` / tool handlers for live data and models in production; keep the NL Discord gateway.

### Production Finbot research tools (live Discord agent)

The production agent (private deploy) uses an LLM tool loop over a larger research surface. Owner-visible catalog (from `ToolRegistry` + `tool_catalog`):


Total registered tools (owner view): **72**.

Friends see a subset (no owner-only Pine compile / some hygiene). Call list_tools at runtime for the live graph.

### Price and session

| Tool | What it does |
|---|---|
| chase_guard | Extension and chase flags from recent move + RSI-style stress. |
| get_ohlcv | OHLCV snapshot (price, volume, window high/low). |
| project_price | Monte Carlo price projection (research, not a promise). |

### Technicals

| Tool | What it does |
|---|---|
| explain_ta | Short TA bullets grounded in OHLCV + technicals. |
| get_technicals | Technicals + Raven model scalars (no full series dumps). |

### Fundamentals

| Tool | What it does |
|---|---|
| get_analyst_ratings | Analyst consensus and price targets. |
| get_customer_concentration | Scan latest 10-K (else 10-Q) for customer concentration % language. |
| get_fundamentals | Fundamentals pack: revenue, gross profit, margins, FCF, leverage, YoY growth, dual-layer balance sheet (technical + plain). |
| get_value_factor | Value-factor scores for the ticker. |

### Flow, short interest, options, GEX

| Tool | What it does |
|---|---|
| get_congressional_trades | Congressional trades linked to ticker. |
| get_gex_profile | Dealer gamma / GEX estimate. |
| get_insider_trades | Recent insider (Form 4 style) trades. |
| get_options_summary | Options summary and put-call bias. |
| get_short_interest | Short % float and days-to-cover style fields (PROBABLE). |

### Research packs

| Tool | What it does |
|---|---|
| deep_research | Planned multi-phase pack for ONE ticker. |
| dossier_deep | Deep multi-source dossier (heavier than quick). |
| dossier_quick | Quick multi-source pack + SI + fundamentals ratios + dual balance sheet + customer concentration + quant_line (SI/GEX/chase when present). |
| get_full_dossier | Legacy raw multi-source pack. |

### SEC / EDGAR

| Tool | What it does |
|---|---|
| audit_claim | Phrase-match a claim against filing body. |
| get_sec_filing_body | Fetch EDGAR body text (sec.gov URL or latest form for ticker). |
| get_sec_filings | Recent EDGAR filings list for ticker. |
| macro_sec_pack | Aggregate EDGAR 10-K/10-Q/8-K for rate-sensitive issuers (banks, mREITs, consumer finance, homebuilders) + interest-rate risk snippets. |

### News

| Tool | What it does |
|---|---|
| catalyst_pack | Catalyst pack (news / SEC / X signals when available). |
| get_news | Recent headlines for ticker (PROBABLE). |
| web_news_search | Google News RSS search (keyless). |

### Web fetch and search

| Tool | What it does |
|---|---|
| web_fetch | Fetch allowlisted HTTPS page text (egress-gated). |
| web_search | Web/news search by free-text query. |
| web_search_ticker | News search scoped to ticker + optional angle. |

### X / social (read-only)

| Tool | What it does |
|---|---|
| x_search | X/Twitter search (read-only SuperGrok path). |
| x_search_ticker | X cashtag search for ticker. |
| x_user_lookup | Public X profile lookup. |

### Charts and levels

| Tool | What it does |
|---|---|
| chart | One chart tool: TV||matplotlib race, first PNG attaches. |
| chart_quick | Deprecated local-only alias. |
| chart_tv | Same as chart: TV||matplotlib race, first PNG wins. |
| compare_tickers | Side-by-side snapshot for 2-6 tickers (price, day%, range, RSI if cheap). |
| get_chart_history | Recent charts this user pulled (ticker@TF). |
| tv_levels | Key levels from OHLCV (S/R style). |

### Macro and rates

| Tool | What it does |
|---|---|
| get_macro_context | Macro indices / VIX context pack. |
| index_snapshot | SPY QQQ IWM DIA VIX snapshot. |
| market_session | US session phase (ET). |

### Scanner

| Tool | What it does |
|---|---|
| run_scan | TradingView screener preset (volume_surge, oversold, sc_breakout, ...). |

### Thesis memory (per user)

| Tool | What it does |
|---|---|
| add_thesis_note | Lazy scrapbook note (you distill). |
| compile_thesis_report | Card + notes + chat hits pack + local markdown export_path + paper research stub. |
| delete_thesis | Delete thesis card for a ticker. |
| delete_thesis_note | Delete one scrapbook note by id. |
| get_thesis | Load saved thesis card (stance, levels, invalidation). |
| list_theses | List this user's thesis card summaries. |
| list_thesis_notes | List recent scrapbook notes for ticker (or all). |
| list_thesis_outcomes | List this user's thesis outcomes (optional ticker filter). |
| record_thesis_outcome | Record hit|miss|partial + reason for this user. |
| save_thesis | Save/update thesis card (merge by default). |

### Shared agent thesis board

| Tool | What it does |
|---|---|
| board_add | Add novel thesis to shared board (deduped). |
| board_addon | Append bear|support|update|note onto board thesis id. |
| board_get | Full board thesis by id including add_ons. |
| board_list | Shared agent-board theses for ticker (cross-session memory). |
| board_stale | List or mark stale board theses. |

### User prefs and session memory

| Tool | What it does |
|---|---|
| get_user_prefs | Load this user's format/persona/chart prefs + pine names. |
| session_return_brief | Since-last-talk pack: watchlist/thesis moves, macro, last charts. |
| set_user_pref | Save one preference (output_format, persona, chart_timeframe, ...). |

### Pine scripts (mostly owner)

| Tool | What it does |
|---|---|
| delete_pine_script | Delete named Pine for this user only. |
| get_pine_script | Load agent-authored Pine for a saved name (data plane). |
| list_pine_scripts | List this user's saved Pine names (no source). |
| pine_compile | Compile Pine (static + optional TV bridge). |
| pine_explain | Outline Pine source (inputs/functions) without compiling. |
| pine_get_errors | Last pine_compile result for this owner. |
| pine_validate_snippet | Static Pine checks (version, decls, v6 footguns). |
| save_pine_script | Save Pine YOU authored from their words. |

### Meta / routing

| Tool | What it does |
|---|---|
| extract_tickers | Extract US equity tickers from free text. |
| glossary | Local glossary definition for a term. |
| list_tools | Return tool graph: families, paths, short when/next for each tool. |
| resolve_company | Map company name to liquid US ticker. |

### Other

| Tool | What it does |
|---|---|
| get_fed_odds | Live FOMC / fed funds target-range probabilities (public CME FedWatch-style source). |

SEC rows in production are always shown as brief markdown EDGAR links when a URL is present, for example:

```text
[8-K 2026-06-26 — Closing 8-K (debt/notes related)](https://www.sec.gov/...) [PROBABLE]
```

---

## Architecture

```text
  you (Discord DM, natural language)
              │
              ▼
     allowlist + DM-only gate
              │
              ▼
         research agent
         (intent → tools)
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
  research  levels   risk
      │       │        │
      └───────┴────────┘
              │
              ▼
     research answer in DM
     (+ tools used footer)
```

| Module | Role |
|---|---|
| `bot.py` | Discord DM gateway (`on_message`) |
| `agent.py` | NL turn: classify intent, call tools, compose reply |
| `tools.py` | Tool registry |
| `research.py` | Offline research implementations |
| `auth.py` | Fail-closed allowlist |
| `demo.py` | Offline NL CLI |

---

## Setup

### Install

```bash
git clone https://github.com/SamsonCyber/discord-stock-research-bot.git
cd discord-stock-research-bot
python -m venv .venv
# Windows: .venv\Scripts\activate
# POSIX:   source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
```

### Discord application

1. [Discord Developer Portal](https://discord.com/developers/applications) → New Application → Bot.
2. Enable **Message Content Intent** (required to read DM text).
3. Invite the bot (DMs work once you share a server or allow DMs).
4. Copy bot token and your user ID (Developer Mode → Copy User ID).

### Environment

```bash
cp .env.example .env
```

| Variable | Required | Purpose |
|---|---|---|
| `STOCK_RESEARCH_DISCORD_TOKEN` | yes | Bot token |
| `STOCK_RESEARCH_ALLOWED_USER_IDS` | yes | Who may chat (comma-separated IDs) |
| `STOCK_RESEARCH_ALLOWED_USER_IDS_FILE` | no | File of IDs |

Empty allowlist → **process refuses to start**.

### Run

```bash
python -m discord_stock_research_bot.bot
# or: discord-stock-research-bot
```

Then DM the bot:

```text
research AAPL
levels on AAPL
risk for AAPL
help
```

Optional live connect check (env only; never prints the token):

```bash
python scripts/live_smoke.py
```

---

## Security

- **DM-only** research path (guild messages ignored)
- **Fail-closed allowlist** on every turn
- No brokerage / order router / wallet code in this package
- No secrets in git

See [SECURITY.md](SECURITY.md).

---

## Demo data vs production research

| | Public package | Full agentic research bot |
|---|---|---|
| UX | Natural language DMs | Natural language DMs |
| Agent | Lightweight intent → tools | LLM ReAct + large tool graph |
| Data | Offline deterministic demo | Live market data + models |
| Auth | Allowlist | Allowlist + stronger gateway |

Same idea either way: **you talk, tools run, research comes back.**

---

## License

MIT. See [LICENSE](LICENSE).

**Not financial advice.** You own your risk.
