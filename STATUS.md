# Status

**Product:** Equity Research Agent  
**UX:** Natural language DMs → agent → research tools  
**Package:** `equity-research-agent` `0.4.2`

## Shipped

- DM gateway (`on_message`, allowlist, DM-only)
- Research agent (`run_turn`: intent → tools → reply)
- Tools: `research`, `levels`, `risk`, `list_tools`
- Offline NL CLI demo with production-shaped Discord markdown briefs
- Known-ticker meta (AAPL → Apple / Technology, etc.)
- Fail-closed auth
- Front door assets: banner, Discord mock, interactive demo, architecture diagram
- Production tool catalog documented (not live in this clone): `docs/PRODUCTION_TOOLS.md`

## Not this package

- Full LLM ReAct production agent as runnable code here
- Live market-data vendor wiring
- Slash-command-first UX
- Paper-trading product framing
