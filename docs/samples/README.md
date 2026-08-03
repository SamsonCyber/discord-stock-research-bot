# Sample research replies

These files are **exact** stdout from the offline demo agent, not hand-written fiction.

Regenerate after engine changes:

```bash
python -m discord_stock_research_bot.demo research AAPL > docs/samples/aapl-research.txt
```

Or:

```bash
python -c "from discord_stock_research_bot.agent import run_turn; print(run_turn('research AAPL').text)"
```

| File | Command |
|---|---|
| [aapl-research.txt](aapl-research.txt) | `research AAPL` |
| [nvda-levels.txt](nvda-levels.txt) | `levels on NVDA` |
| [tsla-risk.txt](tsla-risk.txt) | `risk for TSLA` |

Deterministic offline engine: same ticker always yields the same brief.

```bash
python scripts/build_showcase.py
```
