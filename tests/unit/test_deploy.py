"""`design-agent deploy`: what ships, what stays home, and when it refuses."""

from __future__ import annotations

from pathlib import Path

import pytest

from design_agent import deploy
from design_agent.config import Settings

ROOT = Path(__file__).resolve().parents[2]


def test_env_ships_agent_keys_and_holds_everything_else() -> None:
    shipped, held = deploy.env_split(
        {
            "ANTHROPIC_API_KEY": "a",
            "DESIGN_AGENT_MODEL": "anthropic:claude-opus-5-5",
            "PAPER_MODE": "bridged",
            "SLACK_BOT_TOKEN": "xoxb",
            "DATABASE_URL": "postgres://",
            "LANGSMITH_API_KEY": "ls",
            "MY_OTHER_PROJECT_KEY": "x",
            "EMPTY": None,
            "OPENAI_API_KEY": "",
            "DESIGN_AGENT_HELPER_MODEL": "  ",
        }
    )
    assert set(shipped) == {"ANTHROPIC_API_KEY", "DESIGN_AGENT_MODEL", "PAPER_MODE"}, (
        "blanks are unset"
    )
    assert held == [
        "DATABASE_URL",
        "EMPTY",
        "LANGSMITH_API_KEY",
        "MY_OTHER_PROJECT_KEY",
        "SLACK_BOT_TOKEN",
    ]


def test_staging_ships_only_what_the_deployment_needs(tmp_path: Path) -> None:
    staged = deploy.stage(ROOT, destination=tmp_path / "stage")
    for needed in (
        "agent.py",
        "identity.py",
        "instructions.md",
        "README.md",
        "sandbox/setup.sh",
        "schedules/housekeeping.py",
        "tools/mcp.py",
        "skills/stills/SKILL.md",
        "src/design_agent/assembly.py",
        "workspace/tools/brand-lint.mjs",
        "examples/brands/example-studio/tokens.json",
        "fonts/LICENSES.md",
        "config/vendored-skills.toml",
    ):
        assert (staged / needed).exists(), needed
    for left_out in (
        "tests",
        "docs",
        "SPEC.md",
        "IMPLEMENTATION_PROMPT.md",
        "workspace/out",
        "workspace/state",
        ".venv",
        ".github",
    ):
        assert not (staged / left_out).exists(), left_out
    assert not list(staged.rglob("__pycache__"))


def test_staging_writes_a_filtered_env(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "agent.py").write_text("agent = None\n")
    (project / ".env").write_text(
        'ANTHROPIC_API_KEY=sk-test\nSLACK_BOT_TOKEN=xoxb-test\nDESIGN_AGENT_SLACK_NAME="Design Agent"\n'
    )
    staged = deploy.stage(project, destination=tmp_path / "stage")
    env = (staged / ".env").read_text()
    assert "ANTHROPIC_API_KEY=sk-test" in env and 'DESIGN_AGENT_SLACK_NAME="Design Agent"' in env
    assert "SLACK_BOT_TOKEN" not in env
    assert (staged / ".env").stat().st_mode & 0o077 == 0


def test_preflight_refuses_the_docker_base_and_a_missing_model_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for key in ("ANTHROPIC_API_KEY", "DESIGN_AGENT_MODEL"):
        monkeypatch.delenv(key, raising=False)
    # An operator's checkout may already declare its published snapshot.
    monkeypatch.setattr(deploy, "declared_base", lambda _root: "docker_image")
    report = deploy.preflight(ROOT, Settings(_env_file=None))  # type: ignore[call-arg]
    assert any("sandbox publish" in p for p in report.problems)
    assert any("ANTHROPIC_API_KEY" in p for p in report.problems) or (ROOT / ".env").is_file()
    relaxed = deploy.preflight(
        ROOT, Settings(_env_file=None), allow_docker_base=True, require_keys=False
    )  # type: ignore[call-arg]
    assert relaxed.ok, relaxed.problems


def test_deploy_asks_first_and_passes_langsmith_credentials_only_in_the_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[list[str], dict[str, str]]] = []
    monkeypatch.setattr(deploy, "preflight", lambda *a, **k: deploy.Preflight())
    monkeypatch.setattr(deploy, "stage", lambda _root: tmp_path)
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")

    def run(argv: list[str], env: dict[str, str]) -> int:
        calls.append((argv, env))
        return 0

    assert deploy.deploy_main(ROOT, confirm=lambda _q: False, run=run) == 1 and calls == []
    assert deploy.deploy_main(ROOT, confirm=lambda _q: True, run=run) == 0
    argv, env = calls[-1]
    assert (
        argv[1:] == ["deploy", str(tmp_path), "--name", "design-agent"]
        and env["LANGSMITH_API_KEY"] == "ls-test"
    )


def test_a_gateway_model_needs_the_gateway_key_shipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(deploy, "declared_base", lambda _root: "snapshot")
    settings = Settings(_env_file=None, model="langsmith:anthropic/claude-opus-5-5")  # type: ignore[call-arg]
    monkeypatch.setattr(deploy, "env_values", lambda _root: {"ANTHROPIC_API_KEY": "sk"})
    report = deploy.preflight(ROOT, settings)
    assert any("needs LANGSMITH_GATEWAY_API_KEY" in p for p in report.problems)
    monkeypatch.setattr(deploy, "env_values", lambda _root: {"LANGSMITH_GATEWAY_API_KEY": "lsv2"})
    assert not any("needs" in p for p in deploy.preflight(ROOT, settings).problems)


def test_staging_moves_binary_skill_files_out_of_context_hub(tmp_path: Path) -> None:
    from design_agent.brand.schema import load_brand_pack
    from design_agent.workspace.manifest import build_manifest

    staged = deploy.stage(ROOT, destination=tmp_path / "stage")
    for path in (p for p in (staged / "skills").rglob("*") if p.is_file()):
        path.read_bytes().decode("utf-8")  # Context Hub takes only UTF-8 text
    moved = sorted((staged / "skill-binaries").rglob("*.woff2"))
    assert moved, "the vendored frame-preset fonts ship as deployment files"
    pack = load_brand_pack(ROOT / "examples/brands/example-studio", project_root=ROOT)
    staged_paths = {str(a.destination) for a in build_manifest(staged, pack).assets}
    rel = moved[0].relative_to(staged / "skill-binaries").as_posix()
    assert f"/workspace/skills/{rel}" in staged_paths, "and still reach the sandbox's skills"
