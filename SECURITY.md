# Security model

Discord Stock Research Bot is an **allowlisted natural-language research agent** on Discord DMs.

## Guarantees

- **DM-only** research path (guild messages ignored)
- **Fail-closed allowlist** before any agent turn
- Empty allowlist → process refuses to start
- No brokerage, order router, or wallet code in this package
- No secrets in git

## Discord intents

Message Content Intent must be enabled so the bot can read DM text. Do not grant unused privileged intents.

## Demo engine

Public tool handlers are offline / deterministic. They are not live market feeds. Production agents that use live data must keep credentials out of the repo and out of chat logs.

## Not financial advice

Research tooling only. You own your risk.
