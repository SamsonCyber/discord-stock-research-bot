# Reproducibility

Natural-language turns are deterministic for the public offline tools.

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m equity_research_agent.demo research AAPL
python -m equity_research_agent.demo levels on NVDA
python -m equity_research_agent.demo "risk for TSLA" --json
```

Same message → same tool selection and same demo research card for a ticker.
