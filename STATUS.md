# Status

**Product:** Equity Research Agent  
**UX:** Natural language DMs -> agent -> research tools  
**Package:** `equity-research-agent` `0.4.3`

## Shipped

- DM gateway (`on_message`, allowlist, DM-only)
- Research agent (`run_turn`: intent -> tools -> reply)
- Tools: `research`, `levels`, `risk`, `list_tools`
- Offline NL CLI demo with Discord-shaped research briefs
- Known-ticker meta (AAPL -> Apple / Technology, and similar)
- Fail-closed auth
- Front door assets: banner, Discord mock, interactive demo, architecture diagram
- Production tool catalog documented (not live in this clone): `docs/PRODUCTION_TOOLS.md`

## Out of scope for this package

- Full LLM ReAct production agent as runnable code here
- Live market-data vendor wiring
- Slash-command-first UX
- Paper-trading product framing
