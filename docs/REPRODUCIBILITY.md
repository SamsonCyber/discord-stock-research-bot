# Reproducibility

Natural-language turns are deterministic for the public offline tools.

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m discord_stock_research_bot.demo research AAPL
python -m discord_stock_research_bot.demo levels on NVDA
python -m discord_stock_research_bot.demo "risk for TSLA" --json
```

Same message → same tool selection and same demo research card for a ticker.
