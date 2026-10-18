"""Vendored HyperFrames skills match their lock, and no repo tooling rewrites them."""

from __future__ import annotations

import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

from design_agent.skills_lock import load_lock, verify

ROOT = Path(__file__).resolve().parents[2]


def test_vendored_skills_match_the_lock() -> None:
    result = verify(ROOT)
    assert result.ok, result


def test_git_tracks_every_locked_file() -> None:
    """Upstream skills ship their own `.gitignore`s, which can hide a locked file from `git add`."""
    git = shutil.which("git")
    if git is None or not (ROOT / ".git").exists():
        pytest.skip("not a Git checkout")
    listed = subprocess.run(
        [git, "-C", str(ROOT), "ls-files", "skills"], capture_output=True, text=True, check=True
    )
    tracked = set(listed.stdout.splitlines())
    untracked = [
        f"skills/{name}/{relative}"
        for name, entry in load_lock(ROOT)["skills"].items()
        for relative in entry["files"]
        if f"skills/{name}/{relative}" not in tracked
    ]
    assert not untracked, f"git add -f these: {untracked}"


def test_lint_skips_exactly_the_vendored_skills() -> None:
    excluded = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["ruff"][
        "extend-exclude"
    ]
    vendored = {f"skills/{name}" for name in load_lock(ROOT)["skills"]}
    assert {path for path in excluded if path.startswith("skills/")} == vendored
