# Security model

Equity Research Agent is an **allowlisted natural-language research agent** on Discord DMs.

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

## CI security scanning

GitHub Actions runs three security jobs on every push/PR to `main` (see `.github/workflows/security.yml`):

- **SAST**: Bandit static analysis over `src/` (medium+ findings fail the job; report artifact `sast-bandit`).
- **SCA**: `pip-audit` after `pip install -e ".[dev]"` (any known dependency vulnerability fails the job; report artifact `sca-pip-audit`).
- **DAST**: local serve of `assets/interactive-demo.html`, then OWASP ZAP baseline against `http://127.0.0.1:8765` (scan cannot start: job fails; report artifact `dast-zap-report`).

Unit tests and offline demos stay in `.github/workflows/ci.yml` so scanner issues never hide pytest failures.

## Not financial advice

Research tooling only. You own your risk.
