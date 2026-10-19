"""Vendored upstream skills match their lock, and no repo tooling rewrites them."""

from __future__ import annotations

import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

from design_agent.skills_lock import load_lock, vendored_folders, verify

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
        [git, "-C", str(ROOT), "ls-files", "skills", ".agents/skills"],
        capture_output=True,
        text=True,
        check=True,
    )
    tracked = set(listed.stdout.splitlines())
    untracked = [
        f"{folder}/{relative}"
        for folder, entry in vendored_folders(load_lock(ROOT))
        for relative in entry["files"]
        if f"{folder}/{relative}" not in tracked
    ]
    assert not untracked, f"git add -f these: {untracked}"


def test_lint_skips_exactly_the_vendored_skills() -> None:
    excluded = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["ruff"][
        "extend-exclude"
    ]
    vendored = {folder for folder, _ in vendored_folders(load_lock(ROOT))}
    assert {path for path in excluded if path.startswith(("skills/", ".agents/"))} == vendored
