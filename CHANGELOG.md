# Changelog

## 0.4.3

- Session-aware after-hours / premarket tape: research, levels, and risk cards label **RTH** / **PRE-MARKET** / **AFTER-HOURS** and expose regular vs extended demo prints (`current_price`, `regular_market_price`, `pre_market_price`, `post_market_price`, `extended_vs_rth_pct`).
- New `session` tool + NL intents (`is market open`, `after hours`, `session`).
- Stop-list: `HOURS` / session English no longer extracted as tickers.

## 0.4.2

- Split rendering: CLI prints boxed plain-text cards (no raw markdown). Discord sends Embeds (color by bias, fields for thesis/catalysts/risks).
- Bot stopped dumping markdown walls into DMs.

## 0.4.1

- Research card redesign: snapshot key/value board, blockquote thesis/invalidation, numbered catalysts/risks, level ladder with distance %, risk sizing card with heat bars.

## 0.4.0

- Research engine: company names, real sectors for known tickers, conviction bars, sparklines, level ladders, richer risk cards.
- Front door: Discord DM hero mock, social banner, interactive offline demo HTML (baked engine payloads).
- `scripts/build_showcase.py` regenerates samples and visuals from the live agent path.
- Showcase tests cover hero assets, known-ticker meta, and sample lock to `run_turn`.

## 0.3.1

- Presentation: hero README, architecture SVG, sample reply from offline demo.
- Production tool inventory moved to `docs/PRODUCTION_TOOLS.md` (offline vs private-deploy split).
- Showcase tests: assets exist; sample reply matches live `run_turn("research AAPL")`.

## 0.3.0

- Product model: natural language DMs -> agent -> tools.
- Removed slash-command-first UX.
- Agent module + tool registry. README rewritten for actual use.

## 0.2.0

- Research tools (brief, levels, risk) with offline engine.

## 0.1.1

- Public shell and security baseline.
