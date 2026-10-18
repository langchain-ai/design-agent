"""Small CLI commands: brand init, fonts verify, sandbox use, test db."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from design_agent import cli

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    shutil.copytree(ROOT / "examples" / "brands", tmp_path / "examples" / "brands")
    shutil.copytree(ROOT / "fonts", tmp_path / "fonts")
    shutil.copy(ROOT / ".env.example", tmp_path / ".env.example")
    monkeypatch.setattr(cli, "_root", lambda: tmp_path)
    monkeypatch.setenv("DESIGN_AGENT_WORKSPACE_ROOT", str(tmp_path / "workspace"))
    return tmp_path


def test_brand_init_copies_the_sample_once(project: Path) -> None:
    first = CliRunner().invoke(cli.main, ["brand", "init"])
    assert first.exit_code == 0 and (project / "workspace/brand/brand.toml").is_file()
    assert CliRunner().invoke(cli.main, ["brand", "init"]).exit_code == 1


def test_fonts_verify_checks_checksums_and_licenses(project: Path) -> None:
    assert CliRunner().invoke(cli.main, ["fonts", "verify"]).exit_code == 0
    (project / "fonts" / "Unlisted-Regular.ttf").write_bytes(b"x")
    result = CliRunner().invoke(cli.main, ["fonts", "verify"])
    assert result.exit_code == 1 and "Unlisted-Regular.ttf is not listed" in result.output


def test_sandbox_use_points_local_runs_at_a_snapshot(project: Path) -> None:
    assert (
        CliRunner().invoke(cli.main, ["sandbox", "use", "design-agent-computer-abc"]).exit_code == 0
    )
    env = (project / ".env").read_text()
    assert (
        "DESIGN_AGENT_SANDBOX=langsmith" in env
        and "DESIGN_AGENT_SANDBOX_SNAPSHOT=design-agent-computer-abc" in env
    )


def test_test_db_writes_and_removes_a_row(project: Path) -> None:
    result = CliRunner().invoke(cli.main, ["test", "db"])
    assert result.exit_code == 0 and "SQLite" in result.output
