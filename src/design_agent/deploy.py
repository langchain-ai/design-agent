"""`design-agent deploy`: preflight, a minimal staged project, then `mda deploy` on it.

`mda deploy` archives the project directory as it is, Git-ignored files included, and forwards
every key in its `.env` as a deployment secret. So the deploy never runs on the working tree: it
stages exactly what the agent needs into `.mda/deploy-src/` (code, skills, the gates, the brand
pack, licensed fonts, the sandbox recipe and declarations) with an `.env` holding only the keys the
deployed agent uses, shows what will be shipped, and deploys that after a yes.

Preflight problems stop the deploy; warnings are shown and the person decides.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values

from design_agent.brand.schema import BrandPackError, load_brand_pack
from design_agent.config import Settings
from design_agent.runtime.sandbox.publish import declared_base
from design_agent.skills_lock import verify
from design_agent.tools.mcp import McpConfigError, declared_servers
from design_agent.workspace.manifest import build_manifest

STAGE = Path(".mda") / "deploy-src"
#: What a deployment needs, relative to the project root. Everything else stays home.
SHIPPED = (
    "agent.py",
    "identity.py",
    "instructions.md",
    "pyproject.toml",
    "uv.lock",
    ".python-version",
    "LICENSE",
    "NOTICE.md",
    "README.md",
    "channels",
    "sandbox",
    "schedules",
    "tools",
    "skills",
    "src",
    "config",
    "examples/brands",
    "fonts",
    "licenses",
    "workspace/tools",
)
#: Operator-supplied, Git-ignored, and needed by the deployment when present.
SHIPPED_IF_PRESENT = ("workspace/brand", "private-fonts", "channels/slack-icon.png")
#: `.env` keys the deployed agent reads. Self-hosted transport keys never ship to MDA.
ENV_PREFIXES = ("DESIGN_AGENT_", "PAPER_")
ENV_KEYS = frozenset(
    {
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
        "ELEVENLABS_API_KEY",
        "GROQ_API_KEY",
        "LANGSMITH_GATEWAY_API_KEY",
        "MDA_MAX_AGENT_SCHEDULES",
    }
)
#: What the `mda` command itself needs to reach LangSmith: passed in its environment, not shipped.
DEPLOY_CREDENTIALS = ("LANGSMITH_API_KEY", "LANGSMITH_ENDPOINT", "LANGSMITH_WORKSPACE_ID")
NEVER_SHIPPED = frozenset(
    {
        "SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN",
        "SLACK_SIGNING_SECRET",
        "DATABASE_URL",
        "DESIGN_AGENT_API_TOKENS",
        *DEPLOY_CREDENTIALS,
    }
)
IGNORED_NAMES = frozenset({"__pycache__", ".DS_Store", "node_modules", ".pytest_cache"})


@dataclass
class Preflight:
    problems: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    shipped_env: list[str] = field(default_factory=list)
    held_env: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def env_split(values: Mapping[str, str | None]) -> tuple[dict[str, str], list[str]]:
    """The `.env` entries a deployment ships, and the names it holds back. Blank entries are
    neither: they are unset, and shipping them would only list empty secrets."""
    shipped: dict[str, str] = {}
    held: list[str] = []
    for key, value in values.items():
        if value is not None and not value.strip():
            continue
        if value is None or key in NEVER_SHIPPED:
            held.append(key)
        elif key in ENV_KEYS or key.startswith(ENV_PREFIXES):
            shipped[key] = value
        else:
            held.append(key)
    return shipped, sorted(held)


def preflight(
    root: Path, settings: Settings, *, allow_docker_base: bool = False, require_keys: bool = True
) -> Preflight:
    report = Preflight()
    try:
        pack = load_brand_pack(settings.resolved_brand_path(root), project_root=root)
        build_manifest(root, pack)
    except BrandPackError as error:
        report.problems.append(f"brand pack: {error}")
    except ValueError as error:
        report.problems.append(f"workspace manifest: {error}")
    lock = verify(root)
    if not lock.ok:
        report.problems.append(
            "vendored skills differ from skills-lock.json: run `design-agent skills verify`"
        )
    if declared_base(root) == "docker_image":
        message = (
            "sandbox/__init__.py still bakes on the Docker image, whose 1 GiB filesystem cannot hold "
            "the computer: run `design-agent sandbox publish` first"
        )
        (report.warnings if allow_docker_base else report.problems).append(message)
    for name in (
        "agent.py",
        "identity.py",
        "channels/slack.py",
        "sandbox/setup.sh",
        "instructions.md",
    ):
        if not (root / name).is_file():
            report.problems.append(f"{name} is missing")
    try:
        for server in declared_servers(root):
            if server.headers_env and server.connection is None:
                report.warnings.append(
                    f"MCP server {server.name} has no workspace connection, so MDA leaves it out"
                )
    except McpConfigError as error:
        report.problems.append(f"config/mcp.toml: {error}")
    env_file = root / ".env"
    values = dotenv_values(env_file) if env_file.is_file() else {}
    shipped, held = env_split(values)
    report.shipped_env, report.held_env = sorted(shipped), held
    lead = settings.lead_model().upstream.provider
    needed = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google_genai": "GOOGLE_API_KEY",
    }.get(lead)
    if needed is not None and needed not in shipped:
        message = f"the lead model ({lead}) needs {needed} in .env"
        (report.problems if require_keys else report.warnings).append(message)
    if shutil.which("mda") is None and not (root / ".venv" / "bin" / "mda").exists():
        report.problems.append("the `mda` command is not installed: run `uv sync`")
    return report


def _copy(source: Path, target: Path) -> None:
    if source.is_dir():
        shutil.copytree(
            source, target, ignore=lambda _d, names: [n for n in names if n in IGNORED_NAMES]
        )
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def stage(root: Path, *, destination: Path | None = None) -> Path:
    """Copy what ships into a fresh staging directory and write its filtered `.env`."""
    target = destination or root / STAGE
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    for relative in (*SHIPPED, *SHIPPED_IF_PRESENT):
        source = root / relative
        if source.exists():
            _copy(source, target / relative)
    env_file = root / ".env"
    if env_file.is_file():
        shipped, _ = env_split(dotenv_values(env_file))
        lines = [f"{key}={_quoted(value)}" for key, value in sorted(shipped.items())]
        (target / ".env").write_text("\n".join(lines) + "\n")
        (target / ".env").chmod(0o600)
    return target


def _quoted(value: str) -> str:
    return (
        '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
        if any(c in value for c in " #\"'")
        else value
    )


def deploy_main(
    root: Path,
    *,
    yes: bool = False,
    build_only: bool = False,
    allow_docker_base: bool = False,
    name: str = "design-agent",
    confirm: Callable[[str], bool] | None = None,
    run: Callable[[list[str], dict[str, str]], int] | None = None,
) -> int:
    settings = Settings()
    # A build-only run inspects what would ship, so it needs neither keys nor a published snapshot.
    report = preflight(
        root,
        settings,
        allow_docker_base=allow_docker_base or build_only,
        require_keys=not build_only,
    )
    for warning in report.warnings:
        print(f"warning: {warning}")
    if not report.ok:
        for problem in report.problems:
            print(f"problem: {problem}")
        print("Nothing was deployed.")
        return 1
    staged = stage(root)
    print(f"Staged the deployment in {staged}.")
    print("Secrets it ships (.env keys): " + (", ".join(report.shipped_env) or "none"))
    if report.held_env:
        print("Kept out of the deployment: " + ", ".join(report.held_env))
    runner = run or (lambda argv, env: subprocess.run(argv, env=env, check=False).returncode)  # noqa: S603 - fixed argv
    mda = shutil.which("mda") or str(root / ".venv" / "bin" / "mda")
    env_file = root / ".env"
    local = dotenv_values(env_file) if env_file.is_file() else {}
    env = {
        **os.environ,
        **{k: v for k in DEPLOY_CREDENTIALS if (v := os.environ.get(k) or local.get(k))},
    }
    if build_only:
        return runner([mda, "build", str(staged)], env)
    ask = confirm or (lambda question: input(f"{question} [y/N] ").strip().lower() in {"y", "yes"})
    if not yes and not ask(f"Deploy this to your LangSmith workspace now as {name!r}?"):
        print("Not deployed.")
        return 1
    if not env.get("LANGSMITH_API_KEY"):
        print(
            "problem: LANGSMITH_API_KEY is not set (in .env or the environment). Nothing was deployed."
        )
        return 1
    return runner([mda, "deploy", str(staged), "--name", name], env)
