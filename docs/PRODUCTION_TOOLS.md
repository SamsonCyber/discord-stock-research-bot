# Production research tool surface (private deploy)

This public package ships **four offline-demo tools**. A private production agent
can use the same natural-language Discord UX with a larger tool graph (LLM loop).

**Important:** none of the tools below are live handlers in this clone. They document
what a full research agent surface can look like. Data quality tags (PROBABLE / VERIFIED)
and EDGAR link formatting apply only in that private deploy.

Total owner-visible tools in a full agent catalog: **72**. Friends typically see a subset.

## Price and session

| Tool | What it does |
|---|---|
| `chase_guard` | Extension and chase flags from recent move + RSI-style stress. |
| `get_ohlcv` | OHLCV snapshot (price, volume, window high/low). |
| `project_price` | Monte Carlo price projection (research, not a promise). |

## Technicals

| Tool | What it does |
|---|---|
| `explain_ta` | Short TA bullets grounded in OHLCV + technicals. |
| `get_technicals` | Technicals + model scalars (no full series dumps). |

## Fundamentals

| Tool | What it does |
|---|---|
| `get_analyst_ratings` | Analyst consensus and price targets. |
| `get_customer_concentration` | Scan latest 10-K/10-Q for concentration language. |
| `get_fundamentals` | Revenue, margins, FCF, leverage, dual-layer balance sheet. |
| `get_value_factor` | Value-factor scores for the ticker. |

## Flow, short interest, options, GEX

| Tool | What it does |
|---|---|
| `get_congressional_trades` | Congressional trades linked to ticker. |
| `get_gex_profile` | Dealer gamma / GEX estimate. |
| `get_insider_trades` | Recent insider (Form 4 style) trades. |
| `get_options_summary` | Options summary and put-call bias. |
| `get_short_interest` | Short % float and days-to-cover (PROBABLE). |

## Research packs

| Tool | What it does |
|---|---|
| `deep_research` | Planned multi-phase pack for one ticker. |
| `dossier_deep` | Deep multi-source dossier. |
| `dossier_quick` | Quick multi-source pack + SI + fundamentals + quant line. |
| `get_full_dossier` | Legacy raw multi-source pack. |

## SEC / EDGAR

| Tool | What it does |
|---|---|
| `audit_claim` | Phrase-match a claim against filing body. |
| `get_sec_filing_body` | Fetch EDGAR body text. |
| `get_sec_filings` | Recent EDGAR filings list (brief summary + URL). |
| `macro_sec_pack` | Aggregate filings for rate-sensitive issuers + snippets. |

SEC rows are cited as brief markdown EDGAR links when a URL is present, for example:

```text
[8-K 2026-06-26 — Closing 8-K (debt/notes related)](https://www.sec.gov/...) [PROBABLE]
```

## News, web, social

| Tool | What it does |
|---|---|
| `catalyst_pack` | Catalyst pack (news / SEC / X when available). |
| `get_news` | Recent headlines (PROBABLE). |
| `web_news_search` | Google News RSS search (keyless). |
| `web_fetch` | Allowlisted HTTPS page text (egress-gated). |
| `web_search` | Web/news search by free-text query. |
| `web_search_ticker` | News search scoped to ticker + angle. |
| `x_search` | X/Twitter search (read-only). |
| `x_search_ticker` | X cashtag search. |
| `x_user_lookup` | Public X profile lookup. |

## Charts and levels

| Tool | What it does |
|---|---|
| `chart` | Chart image (TV or matplotlib race). |
| `chart_tv` | Alias of chart. |
| `chart_quick` | Deprecated local-only alias. |
| `compare_tickers` | Side-by-side snapshot for 2-6 tickers. |
| `get_chart_history` | Recent charts this user pulled. |
| `tv_levels` | Support / resistance style levels. |

## Macro, session, scanner

| Tool | What it does |
|---|---|
| `get_macro_context` | Macro indices / VIX pack. |
| `get_fed_odds` | FOMC / fed funds probabilities (public source). |
| `index_snapshot` | SPY QQQ IWM DIA VIX snapshot. |
| `market_session` | US session phase (ET). |
| `run_scan` | Screener presets (volume_surge, oversold, ...). |

## Thesis, board, prefs, Pine

| Tool | What it does |
|---|---|
| `get_thesis` / `save_thesis` / `list_theses` / `delete_thesis` | Per-user thesis cards. |
| `add_thesis_note` / `list_thesis_notes` / `delete_thesis_note` | Lazy scrapbook notes. |
| `compile_thesis_report` / `record_thesis_outcome` / `list_thesis_outcomes` | Report pack + outcomes. |
| `board_list` / `board_add` / `board_addon` / `board_get` / `board_stale` | Shared thesis board. |
| `get_user_prefs` / `set_user_pref` / `session_return_brief` | Prefs + catch-up pack. |
| `list_pine_scripts` / `get_pine_script` / `save_pine_script` / `delete_pine_script` | Per-user Pine library. |
| `pine_validate_snippet` / `pine_compile` / `pine_get_errors` / `pine_explain` | Owner Pine tooling. |

## Meta

| Tool | What it does |
|---|---|
| `extract_tickers` | Extract US equity tickers from free text. |
| `resolve_company` | Company name to liquid US ticker. |
| `glossary` | Local trading-term glossary. |
| `list_tools` | Live tool graph for the running agent. |
