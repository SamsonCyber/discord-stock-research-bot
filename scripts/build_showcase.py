"""Generate showcase assets from the live offline research engine."""

from __future__ import annotations

import html
import json
from pathlib import Path

from equity_research_agent.agent import run_turn
from equity_research_agent.research import research_brief

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SAMPLES = ROOT / "docs" / "samples"


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    SAMPLES.mkdir(parents=True, exist_ok=True)

    for msg, name in [
        ("research AAPL", "aapl-research.txt"),
        ("levels on NVDA", "nvda-levels.txt"),
        ("risk for TSLA", "tsla-risk.txt"),
    ]:
        text = run_turn(msg).text.rstrip() + "\n"
        (SAMPLES / name).write_text(text, encoding="utf-8")

    aapl = run_turn("research AAPL").text
    brief = research_brief("AAPL")
    # GitHub (and most SVG sanitizers) strip foreignObject / XHTML. Render
    # engine output as pure <text> so the DM mock is real, not empty chrome.
    body_lines = aapl.splitlines()
    line_h = 15.2
    body_pad_top = 14
    body_pad_bot = 18
    body_h = max(360, int(body_pad_top + len(body_lines) * line_h + body_pad_bot))
    panel_top = 70
    panel_h = 48 + 90 + 40 + body_h + 28  # title + user + bot head + body + pad
    svg_h = panel_top + panel_h + 40
    body_y0 = panel_top + 48 + 90 + 40  # start of reply card
    text_nodes: list[str] = []
    y = body_y0 + body_pad_top + 12
    for raw in body_lines:
        # Keep Discord markdown markers visible (matches CLI/sample), escape XML.
        safe = html.escape(raw) if raw else " "
        # Section headers / tags get a slight accent; body stays Discord gray.
        fill = "#e2e8f0"
        weight = "600" if raw.startswith("**") else "400"
        if raw.startswith("_") or raw.startswith("`"):
            fill = "#94a3b8"
            weight = "400"
        if "INFERRED" in raw or "VERIFIED" in raw or "PROBABLE" in raw:
            fill = "#cbd5e1"
        text_nodes.append(
            f'<text x="128" y="{y:.1f}" fill="{fill}" '
            f'font-family="Consolas, ui-monospace, monospace" font-size="12.5" '
            f'font-weight="{weight}">{safe}</text>'
        )
        y += line_h
    body_svg = "\n    ".join(text_nodes)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 {svg_h}" role="img" aria-label="Discord DM research demo: research AAPL structured brief">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0c0e16"/>
      <stop offset="50%" stop-color="#12141f"/>
      <stop offset="100%" stop-color="#0b1020"/>
    </linearGradient>
    <linearGradient id="blurble" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#5865F2"/>
      <stop offset="100%" stop-color="#00D4FF"/>
    </linearGradient>
    <filter id="soft" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#000" flood-opacity="0.45"/>
    </filter>
    <clipPath id="round">
      <rect x="40" y="{panel_top}" width="900" height="{panel_h}" rx="18"/>
    </clipPath>
  </defs>
  <rect width="980" height="{svg_h}" fill="url(#bg)"/>
  <circle cx="120" cy="80" r="160" fill="#5865F2" opacity="0.12"/>
  <circle cx="860" cy="{svg_h - 80}" r="200" fill="#00D4FF" opacity="0.08"/>

  <text x="48" y="42" fill="#f1f5f9" font-family="Segoe UI, system-ui, sans-serif" font-size="22" font-weight="700">
    Natural language. Tools run. Research lands.
  </text>
  <text x="48" y="62" fill="#94a3b8" font-family="Segoe UI, system-ui, sans-serif" font-size="13">
    Offline demo engine | deterministic | no API keys | same path as CLI
  </text>

  <g filter="url(#soft)" clip-path="url(#round)">
    <rect x="40" y="{panel_top}" width="900" height="{panel_h}" rx="18" fill="#313338"/>
    <rect x="40" y="{panel_top}" width="900" height="48" fill="#2b2d31"/>
    <circle cx="68" cy="{panel_top + 24}" r="12" fill="#5865F2"/>
    <text x="88" y="{panel_top + 29}" fill="#f2f3f5" font-family="Segoe UI, system-ui, sans-serif" font-size="15" font-weight="700">Research Bot</text>
    <text x="200" y="{panel_top + 29}" fill="#b5bac1" font-family="Segoe UI, system-ui, sans-serif" font-size="12">Direct Message | allowlisted</text>
    <text x="900" y="{panel_top + 29}" text-anchor="end" fill="#23a559" font-family="Segoe UI, system-ui, sans-serif" font-size="12">online</text>

    <circle cx="78" cy="{panel_top + 90}" r="18" fill="#ed4245"/>
    <text x="78" y="{panel_top + 95}" text-anchor="middle" fill="#fff" font-family="Segoe UI, system-ui, sans-serif" font-size="12" font-weight="700">U</text>
    <text x="110" y="{panel_top + 82}" fill="#f2f3f5" font-family="Segoe UI, system-ui, sans-serif" font-size="14" font-weight="700">you</text>
    <text x="150" y="{panel_top + 82}" fill="#949ba4" font-family="Segoe UI, system-ui, sans-serif" font-size="11">Today at 9:41 AM</text>
    <text x="110" y="{panel_top + 106}" fill="#dbdee1" font-family="Segoe UI, system-ui, sans-serif" font-size="15">research AAPL</text>

    <circle cx="78" cy="{panel_top + 160}" r="18" fill="url(#blurble)"/>
    <text x="78" y="{panel_top + 165}" text-anchor="middle" fill="#0b1020" font-family="Segoe UI, system-ui, sans-serif" font-size="11" font-weight="800">RB</text>
    <text x="110" y="{panel_top + 152}" fill="#f2f3f5" font-family="Segoe UI, system-ui, sans-serif" font-size="14" font-weight="700">Research Bot</text>
    <text x="220" y="{panel_top + 152}" fill="#5865F2" font-family="Segoe UI, system-ui, sans-serif" font-size="10" font-weight="700">APP</text>
    <text x="255" y="{panel_top + 152}" fill="#949ba4" font-family="Segoe UI, system-ui, sans-serif" font-size="11">Today at 9:41 AM</text>

    <rect x="110" y="{body_y0}" width="780" height="{body_h}" rx="8" fill="#2b2d31"/>
    <rect x="110" y="{body_y0}" width="6" height="{body_h}" rx="3" fill="url(#blurble)"/>
    {body_svg}
  </g>
</svg>
"""
    (ASSETS / "hero-discord.svg").write_text(svg, encoding="utf-8")

    banner = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0a0c14"/>
      <stop offset="40%" stop-color="#12182b"/>
      <stop offset="100%" stop-color="#0d1528"/>
    </linearGradient>
    <linearGradient id="a" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#5865F2"/>
      <stop offset="100%" stop-color="#22d3ee"/>
    </linearGradient>
  </defs>
  <rect width="1280" height="640" fill="url(#g)"/>
  <circle cx="200" cy="120" r="220" fill="#5865F2" opacity="0.15"/>
  <circle cx="1100" cy="520" r="260" fill="#22d3ee" opacity="0.10"/>
  <text x="80" y="200" fill="#e2e8f0" font-family="Segoe UI, system-ui, sans-serif" font-size="54" font-weight="800">Equity Research Agent</text>
  <text x="80" y="270" fill="#94a3b8" font-family="Segoe UI, system-ui, sans-serif" font-size="28">Talk like a desk. Tools run. Research lands.</text>
  <rect x="80" y="320" width="420" height="56" rx="14" fill="url(#a)"/>
  <text x="290" y="356" text-anchor="middle" fill="#0b1020" font-family="Consolas, monospace" font-size="20" font-weight="700">research AAPL</text>
  <text x="80" y="420" fill="#cbd5e1" font-family="Segoe UI, system-ui, sans-serif" font-size="20">Natural language DMs | allowlist | offline demo engine</text>
  <text x="80" y="460" fill="#64748b" font-family="Segoe UI, system-ui, sans-serif" font-size="16">No slash-menu tax. No brokerage. Clone and run in 10 seconds.</text>
  <text x="80" y="560" fill="#67e8f9" font-family="Consolas, monospace" font-size="18">{brief.ticker} | {brief.sector} | {brief.bias} | conviction {brief.conviction}/5 | ${brief.last_price:.2f}</text>
</svg>
"""
    (ASSETS / "banner.svg").write_text(banner, encoding="utf-8")

    tickers = ["AAPL", "NVDA", "TSLA", "MSFT", "AMD"]
    payload: dict[str, dict[str, str]] = {}
    for t in tickers:
        payload[t] = {
            "research": run_turn(f"research {t}").text,
            "levels": run_turn(f"levels on {t}").text,
            "risk": run_turn(f"risk for {t}").text,
        }
    data_json = json.dumps(payload, ensure_ascii=False)

    demo_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Equity Research Agent - Interactive Demo</title>
<style>
  :root {{
    --bg: #0b1020;
    --panel: #12182b;
    --discord: #313338;
    --discord-2: #2b2d31;
    --text: #dbdee1;
    --muted: #949ba4;
    --accent: #5865F2;
    --cyan: #22d3ee;
    --green: #23a559;
    --border: #1e293b;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; min-height: 100vh;
    font-family: "Segoe UI", system-ui, sans-serif;
    background: radial-gradient(1200px 600px at 10% -10%, #1e293b 0%, transparent 50%),
                radial-gradient(900px 500px at 100% 100%, #164e63 0%, transparent 40%),
                var(--bg);
    color: var(--text);
  }}
  .wrap {{ max-width: 980px; margin: 0 auto; padding: 28px 18px 60px; }}
  h1 {{ font-size: 1.75rem; margin: 0 0 6px; letter-spacing: -0.02em; }}
  .sub {{ color: var(--muted); margin: 0 0 22px; }}
  .bar {{
    display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
    margin-bottom: 16px;
  }}
  button {{
    border: 1px solid var(--border); background: var(--panel); color: var(--text);
    border-radius: 999px; padding: 8px 14px; cursor: pointer; font-weight: 600;
    transition: border-color .15s, transform .1s, background .15s;
  }}
  button:hover {{ border-color: var(--cyan); }}
  button.active {{ background: linear-gradient(90deg, var(--accent), #0ea5e9); color: #041018; border-color: transparent; }}
  .modes button {{ border-radius: 10px; }}
  .window {{
    background: var(--discord); border-radius: 16px; overflow: hidden;
    box-shadow: 0 24px 80px rgba(0,0,0,.45); border: 1px solid #1f2937;
  }}
  .title {{
    background: var(--discord-2); padding: 12px 16px; display: flex; align-items: center; gap: 10px;
  }}
  .dot {{ width: 10px; height: 10px; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px var(--green); }}
  .title strong {{ font-size: .95rem; }}
  .title span {{ color: var(--muted); font-size: .8rem; }}
  .chat {{ padding: 18px 16px 22px; min-height: 420px; }}
  .msg {{ display: flex; gap: 12px; margin-bottom: 18px; }}
  .av {{
    width: 40px; height: 40px; border-radius: 50%; flex: 0 0 40px;
    display: grid; place-items: center; font-weight: 800; font-size: .85rem;
  }}
  .av.user {{ background: #ed4245; color: #fff; }}
  .av.bot {{ background: linear-gradient(135deg, var(--accent), var(--cyan)); color: #041018; }}
  .meta {{ font-size: .78rem; color: var(--muted); margin-bottom: 4px; }}
  .meta b {{ color: #f2f3f5; font-size: .92rem; margin-right: 6px; }}
  .bubble {{
    background: var(--discord-2); border-radius: 8px; padding: 12px 14px;
    border-left: 4px solid var(--accent);
    white-space: pre-wrap; font-family: ui-monospace, Consolas, monospace;
    font-size: .86rem; line-height: 1.45; max-width: 100%;
  }}
  .userline {{ font-family: "Segoe UI", system-ui, sans-serif; font-size: .98rem; }}
  .foot {{ margin-top: 16px; color: var(--muted); font-size: .82rem; }}
  code {{ background: #0f172a; padding: 2px 6px; border-radius: 6px; color: var(--cyan); }}
  a {{ color: var(--cyan); }}
</style>
</head>
<body>
  <div class="wrap">
    <h1>Interactive offline demo</h1>
    <p class="sub">Same engine as <code>python -m equity_research_agent.demo</code>. No network. No token. Pick a ticker and tool.</p>
    <div class="bar" id="tickers"></div>
    <div class="bar modes" id="modes"></div>
    <div class="window">
      <div class="title">
        <div class="dot"></div>
        <strong>Research Bot</strong>
        <span>Direct Message | allowlisted | offline-demo</span>
      </div>
      <div class="chat">
        <div class="msg">
          <div class="av user">U</div>
          <div>
            <div class="meta"><b>you</b> today</div>
            <div class="userline" id="userMsg">research AAPL</div>
          </div>
        </div>
        <div class="msg">
          <div class="av bot">RB</div>
          <div style="flex:1;min-width:0">
            <div class="meta"><b>Research Bot</b> APP | today</div>
            <div class="bubble" id="botMsg"></div>
          </div>
        </div>
      </div>
    </div>
    <p class="foot">
      Demo data is deterministic per ticker - not live markets.
      Source: <a href="https://github.com/SamsonCyber/equity-research-agent">SamsonCyber/equity-research-agent</a>
    </p>
  </div>
  <script>
    const DATA = {data_json};
    const tickers = Object.keys(DATA);
    let ticker = 'AAPL';
    let mode = 'research';
    const prompts = {{
      research: t => `research ${{t}}`,
      levels: t => `levels on ${{t}}`,
      risk: t => `risk for ${{t}}`,
    }};
    const tEl = document.getElementById('tickers');
    const mEl = document.getElementById('modes');
    function renderButtons() {{
      tEl.innerHTML = '';
      tickers.forEach(t => {{
        const b = document.createElement('button');
        b.textContent = t;
        b.className = t === ticker ? 'active' : '';
        b.onclick = () => {{ ticker = t; paint(); }};
        tEl.appendChild(b);
      }});
      mEl.innerHTML = '';
      ['research','levels','risk'].forEach(m => {{
        const b = document.createElement('button');
        b.textContent = m;
        b.className = m === mode ? 'active' : '';
        b.onclick = () => {{ mode = m; paint(); }};
        mEl.appendChild(b);
      }});
    }}
    function paint() {{
      renderButtons();
      document.getElementById('userMsg').textContent = prompts[mode](ticker);
      document.getElementById('botMsg').textContent = DATA[ticker][mode];
    }}
    paint();
  </script>
</body>
</html>
"""
    (ASSETS / "interactive-demo.html").write_text(demo_html, encoding="utf-8")
    print("showcase assets written")
    print(f"AAPL: {brief.ticker} {brief.sector} {brief.bias} {brief.conviction}/5 ${brief.last_price:.2f}")


if __name__ == "__main__":
    main()
