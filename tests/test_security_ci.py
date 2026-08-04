"""Structural checks that SAST / SCA / DAST stay wired into git CI."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECURITY_WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
DEMO_TARGET = ROOT / "assets" / "interactive-demo.html"


def _load_yaml(path: Path) -> dict:
    assert path.is_file(), f"missing workflow: {path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"workflow is not a mapping: {path}"
    # PyYAML 1.1 treats bare key "on" as boolean True. GitHub Actions needs "on".
    if True in data and "on" not in data:
        data["on"] = data.pop(True)
    return data


def test_security_workflow_defines_sast_sca_dast_jobs() -> None:
    data = _load_yaml(SECURITY_WORKFLOW)
    jobs = data.get("jobs") or {}
    assert set(jobs) >= {"sast", "sca", "dast"}

    sast_steps = "\n".join(
        str(step.get("run", "") or step.get("uses", "") or step.get("name", ""))
        for step in jobs["sast"]["steps"]
    )
    assert "bandit" in sast_steps.lower()
    assert "src/" in sast_steps or "src" in sast_steps

    sca_steps = "\n".join(
        str(step.get("run", "") or step.get("uses", "") or step.get("name", ""))
        for step in jobs["sca"]["steps"]
    )
    assert "pip-audit" in sca_steps.lower()
    assert '."[dev]"' in sca_steps or ".[dev]" in sca_steps

    dast_job = jobs["dast"]
    dast_blob = yaml.safe_dump(dast_job)
    assert "interactive-demo.html" in dast_blob
    assert "zaproxy/action-baseline" in dast_blob
    assert "127.0.0.1" in dast_blob or "localhost" in dast_blob


def test_security_workflow_triggers_match_main_ci() -> None:
    security = _load_yaml(SECURITY_WORKFLOW)
    ci = _load_yaml(CI_WORKFLOW)
    for event in ("push", "pull_request"):
        assert event in security["on"]
        assert event in ci["on"]
        assert security["on"][event]["branches"] == ci["on"][event]["branches"]


def test_security_workflow_permissions_are_read_only_contents() -> None:
    data = _load_yaml(SECURITY_WORKFLOW)
    perms = data.get("permissions") or {}
    assert perms.get("contents") == "read"
    # No write grants beyond what free public defaults need for these tools.
    assert "security-events" not in perms


def test_dast_http_target_exists_and_is_nonempty() -> None:
    assert DEMO_TARGET.is_file()
    body = DEMO_TARGET.read_text(encoding="utf-8", errors="replace")
    assert len(body) > 100
    assert "<html" in body.lower() or "<!doctype" in body.lower()


def test_existing_unit_ci_still_present() -> None:
    data = _load_yaml(CI_WORKFLOW)
    jobs = data.get("jobs") or {}
    assert "test" in jobs
    blob = yaml.safe_dump(jobs["test"])
    assert "pytest" in blob
    assert "equity_research_agent.demo" in blob
