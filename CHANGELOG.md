# Changelog

## 0.4.0

- Research engine upgrade: company names, real sectors for known tickers, conviction bars, sparklines, level ladders, richer risk cards.
- Product front door: Discord DM hero mock, social banner, interactive offline demo HTML (baked engine payloads).
- `scripts/build_showcase.py` regenerates samples + visuals from the live agent path.
- Showcase tests cover hero assets, known-ticker meta, and sample lock to `run_turn`.

## 0.3.1

- Presentation pass: hero README, architecture SVG, real sample reply from offline demo.
- Collapsed production tool inventory into `docs/PRODUCTION_TOOLS.md` (honest offline vs private-deploy split).
- Showcase tests: assets exist; sample reply matches live `run_turn("research AAPL")`.

## 0.3.0

- Correct product model: **natural language DMs → agent → tools**.
- Removed slash-command-first UX.
- Agent module + tool registry; README rewritten for how you actually use it.

## 0.2.0

- Research tools (brief, levels, risk) with offline engine.

## 0.1.1

- Public shell and security baseline.
