"""Fail-closed authorization helpers."""

from __future__ import annotations

import os
from pathlib import Path


def _ids_from_text(value: str) -> frozenset[int]:
    result: set[int] = set()
    for part in value.replace("\n", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            result.add(int(part))
        except ValueError:
            continue
    return frozenset(result)


def _ids_from_env_or_file(env_name: str, file_env: str | None = None) -> frozenset[int]:
    raw = os.environ.get(env_name, "").strip()
    if raw:
        return _ids_from_text(raw)
    if file_env:
        path = os.environ.get(file_env, "").strip()
        if path and Path(path).is_file():
            return _ids_from_text(Path(path).read_text(encoding="utf-8"))
    return frozenset()


def allowed_user_ids() -> frozenset[int]:
    """Comma/newline-separated Discord user IDs. Empty = nobody authorized."""
    return _ids_from_env_or_file(
        "STOCK_RESEARCH_ALLOWED_USER_IDS",
        file_env="STOCK_RESEARCH_ALLOWED_USER_IDS_FILE",
    )


def is_allowed(user_id: int) -> bool:
    return int(user_id) in allowed_user_ids()
