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

| Tool | What it returns |
|---|---|
| `research` | Bias, conviction, thesis, catalysts, risks, invalidation |
| `levels` | Support / resistance map + pivot |
| `risk` | ATR%, beta, demo stop distance, risk per share |
| `list_tools` | Tool catalog (also used by `help`) |

Every public-package tool response is labeled **offline-demo**: deterministic per ticker, not live quotes. Swap `research.py` / tool handlers for live data and models in production; keep the NL Discord gateway.

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
