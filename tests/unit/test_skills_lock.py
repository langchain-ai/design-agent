"""Vendored HyperFrames skills match their lock, and no repo tooling rewrites them."""

from __future__ import annotations

import tomllib
from pathlib import Path

from design_agent.skills_lock import load_lock, verify

ROOT = Path(__file__).resolve().parents[2]


def test_vendored_skills_match_the_lock() -> None:
    result = verify(ROOT)
    assert result.ok, result


def test_lint_skips_exactly_the_vendored_skills() -> None:
    excluded = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["ruff"][
        "extend-exclude"
    ]
    vendored = {f"skills/{name}" for name in load_lock(ROOT)["skills"]}
    assert {path for path in excluded if path.startswith("skills/")} == vendored
