# Status

**Product:** Discord Stock Research Bot  
**UX:** Natural language DMs → agent → research tools  
**Package:** `discord-stock-research-bot` `0.3.0`

## Shipped

- DM gateway (`on_message`, allowlist, DM-only)
- Research agent (`run_turn`: intent → tools → reply)
- Tools: `research`, `levels`, `risk`, `list_tools`
- Offline NL CLI demo
- Fail-closed auth

## Not this package

- Full LLM ReAct production agent
- Live market-data vendor wiring
- Slash-command-first UX
- Paper-trading product framing
