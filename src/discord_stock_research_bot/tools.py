"""Tool registry the research agent can call.

Public package ships offline demo implementations. Production deployments swap
these for live market-data / model-backed tools while keeping the same names
and natural-language UX.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .research import level_map, research_brief, risk_snapshot


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    handler: Callable[..., Any]


def _tool_research(ticker: str) -> dict[str, Any]:
    return research_brief(ticker).as_dict()


def _tool_levels(ticker: str) -> dict[str, Any]:
    return level_map(ticker).as_dict()


def _tool_risk(ticker: str) -> dict[str, Any]:
    return risk_snapshot(ticker).as_dict()


def _tool_list_tools() -> dict[str, Any]:
    return {
        "tools": [
            {"name": t.name, "description": t.description}
            for t in TOOLS.values()
            if t.name != "list_tools"
        ]
    }


TOOLS: dict[str, ToolSpec] = {
    "research": ToolSpec(
        name="research",
        description="Stock research brief: bias, thesis, catalysts, risks, invalidation",
        handler=_tool_research,
    ),
    "levels": ToolSpec(
        name="levels",
        description="Support / resistance map and pivot for a ticker",
        handler=_tool_levels,
    ),
    "risk": ToolSpec(
        name="risk",
        description="Risk snapshot: ATR%, beta, demo stop, risk per share",
        handler=_tool_risk,
    ),
    "list_tools": ToolSpec(
        name="list_tools",
        description="List available research tools",
        handler=_tool_list_tools,
    ),
}


def run_tool(name: str, **kwargs: Any) -> dict[str, Any]:
    spec = TOOLS.get(name)
    if spec is None:
        raise ValueError(f"unknown tool: {name}")
    result = spec.handler(**kwargs)
    if not isinstance(result, dict):
        return {"result": result}
    return result
