"""Allowlist importer from the private reference agent. Internal-only: deleted before release.

Copies only the paths listed in ALLOWLIST (docs/prep/extraction-map.md), from one pinned commit,
through name rewrites and the public-hygiene scan. Every import is logged with source path and
checksums to a file outside the repository, never in the public tree.

    uv run python scripts/import_from_reference.py list
    uv run python scripts/import_from_reference.py import harness/events.py [...] [--force]
    uv run python scripts/import_from_reference.py show harness/events.py   # scrubbed text, no write

A scrubbed file that still trips the hygiene scan is refused unless `--allow-findings`, which
writes it and records the findings; tests/unit/test_public_hygiene.py stays red until it is fixed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import functools
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path(
    os.environ.get("DESIGN_AGENT_REFERENCE_REPO", "~/Desktop/agents/content-studio")
).expanduser()
REVISION = "f87d6449f4cd5300ed5d3219178fec11e9aaa5d7"
LOG = (
    Path(os.environ.get("XDG_STATE_HOME", "~/.local/state")).expanduser()
    / "design-agent"
    / "reference-import.jsonl"
)


@dataclass(frozen=True)
class Entry:
    target: str
    action: (
        str  # KEEP or GENERALIZE (extraction-map.md); REWRITE work is written fresh, not imported
    )
    mit_lineage: bool = False


def _harness(name: str) -> tuple[str, Entry]:
    return f"harness/{name}.py", Entry(f"src/design_agent/harness/{name}.py", "KEEP")


ALLOWLIST: dict[str, Entry] = dict(
    [
        *(
            _harness(n)
            for n in (
                "__init__",
                "events",
                "policy",
                "inbox",
                "notices",
                "tasks",
                "ledger",
                "wakeups",
                "protocols",
                "durable",
                "workflow",
                "branches",
                "offload",
                "watch",
                "cache",
                "context",
                "learning",
            )
        ),
        ("harness/meter.py", Entry("src/design_agent/harness/meter.py", "GENERALIZE")),
        *(
            (f"tests/harness/test_{n}.py", Entry(f"tests/unit/harness/test_{n}.py", "KEEP"))
            for n in (
                "branches",
                "cache",
                "context",
                "durable",
                "inbox",
                "learning",
                "meter",
                "offload",
                "watch",
                "workflow",
            )
        ),
        *(
            (f"middleware/{n}.py", Entry(f"src/design_agent/middleware/{n}.py", "KEEP"))
            for n in (
                "model_retry",
                "step_budget",
                "image_clamp",
                "tool_error_boundary",
                "tool_history",
                "drop_base_prompt",
                "today",
            )
        ),
        *(
            (f"middleware/{n}.py", Entry(f"src/design_agent/middleware/{n}.py", "GENERALIZE"))
            for n in (
                "background",
                "watch_tools",
                "pipeline_tools",
                "looks_tools",
                "learning_tools",
                "look",
                "meter",
                "progress",
                "phrasebook",
                "footer",
                "agent_session",
                "steering",
                "workspace",
                "paper_scope",
                "memory_policy",
                "memory_hot_cap",
                "memory_learnings",
                "owner_memory",
                "tracing",
            )
        ),
        (
            "tools/disclosure.py",
            Entry("src/design_agent/middleware/tool_disclosure.py", "GENERALIZE"),
        ),
        ("tools/media.py", Entry("src/design_agent/tools/media.py", "GENERALIZE")),
        ("tools/files.py", Entry("src/design_agent/tools/files.py", "KEEP")),
        ("tools/projects.py", Entry("src/design_agent/tools/projects.py", "KEEP")),
        ("tools/mcp.py", Entry("src/design_agent/tools/mcp.py", "GENERALIZE")),
        ("tools/paper.py", Entry("src/design_agent/tools/paper.py", "GENERALIZE")),
        (
            "scripts/paper_mcp_bridge.py",
            Entry("src/design_agent/paper_bridge/app.py", "GENERALIZE"),
        ),
        ("tools/slack.py", Entry("src/design_agent/tools/slack.py", "GENERALIZE")),
        ("tools/slack_read.py", Entry("src/design_agent/surfaces/slack/read.py", "GENERALIZE")),
        ("tools/slack_ui.py", Entry("src/design_agent/surfaces/slack/ui.py", "GENERALIZE")),
        ("pipelines/__init__.py", Entry("src/design_agent/pipelines/__init__.py", "GENERALIZE")),
        (
            "pipelines/launch_film.py",
            Entry("src/design_agent/pipelines/launch_film.py", "GENERALIZE"),
        ),
        ("schedules/housekeeping.py", Entry("schedules/housekeeping.py", "KEEP", mit_lineage=True)),
        ("identity.py", Entry("identity.py", "KEEP", mit_lineage=True)),
        ("subagents.py", Entry("src/design_agent/subagents.py", "GENERALIZE")),
        *(
            (f"workspace/tools/{n}.mjs", Entry(f"workspace/tools/{n}.mjs", "GENERALIZE"))
            for n in (
                "video-gate",
                "artifact-contract",
                "text-fidelity",
                "audio-lint",
                "fetch-asset",
                "html2pdf",
                "review-thumb",
                "film-analysis",
                "film-probe",
                "video-score",
                "brand-lint",
            )
        ),
        *(
            (f"tests/{n}.py", Entry(f"tests/unit/{n}.py", "GENERALIZE"))
            for n in (
                "test_background",
                "test_look",
                "test_looks_tools",
                "test_learning_tools",
                "test_watch_tools",
                "test_pipeline_launch_film",
                "test_harness_surface",
                "test_subagents",
                "test_middleware_retry",
                "test_middleware_step_budget",
                "test_middleware_tool_history",
                "test_middleware_task_boundary",
                "test_middleware_drop_base_prompt",
                "test_paper_scope",
                "test_paper_mcp_bridge",
                "test_phrasebook",
                "test_progress",
                "test_footer",
                "test_steering",
                "test_workspace",
                "test_media",
                "test_mcp",
                "test_memory_policy",
                "test_memory_hot_cap",
                "test_projects",
            )
        ),
    ]
)

#: Whole skill folders, source prefix -> (target prefix, action, excluded source paths). A file
#: under an excluded prefix is never importable: internal channels, unlicensed galleries,
#: excluded providers, vendored libraries and examples about real people or company diagrams.
SKILL_DIRECTORIES: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "skills/image-ops/": ("skills/image-ops/", "KEEP", ()),
    "skills/gif-edit/": ("skills/gif-edit/", "KEEP", ()),
    "skills/visual-verify/": ("skills/visual-verify/", "KEEP", ()),
    "skills/film-breakdown/": ("skills/film-breakdown/", "KEEP", ()),
    "skills/data-viz/": (
        "skills/data-viz/",
        "GENERALIZE",
        ("skills/data-viz/vendor/", "skills/data-viz/examples/"),
    ),
    "skills/ad-creative/": (
        "skills/stills/",
        "GENERALIZE",
        ("skills/ad-creative/scripts/html2png.mjs",),
    ),
    "skills/youtube-thumbnail/": (
        "skills/thumbnails/",
        "GENERALIZE",
        (
            "skills/youtube-thumbnail/references/channel-today.md",
            "skills/youtube-thumbnail/references/reference-library.md",
        ),
    ),
    "skills/gpt-image/": (
        "skills/image-generation/",
        "GENERALIZE",
        ("skills/gpt-image/references/gallery",),
    ),
    "skills/score-video/": (
        "skills/sound/",
        "GENERALIZE",
        ("skills/score-video/lib/epidemic-mcp.mjs", "skills/score-video/lib/gemini-critique.mjs"),
    ),
    "skills/video-storyboard/": ("skills/storyboard/", "GENERALIZE", ()),
}


def _directory_entry(path: str) -> Entry | None:
    for prefix, (target, action, excluded) in SKILL_DIRECTORIES.items():
        if path.startswith(prefix):
            if any(path.startswith(e) for e in excluded):
                return None
            return Entry(target + path[len(prefix) :], action)
    return None


#: Ordered rewrites applied to every imported file. Each is a public rename of an internal name.
REWRITES: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(p, re.MULTILINE), r)
    for p, r in (
        (r"\bContent Studio's\b", "Design Agent's"),
        (r"\bContent Studio\b", "Design Agent"),
        (r"\bcontent_studio\b", "design_agent"),
        (r"\bcontent-studio\b", "design-agent"),
        (r"\bCONTENT_STUDIO_", "DESIGN_AGENT_"),
        (r"\bMEDIA_MODEL", "DESIGN_AGENT_MODEL"),
        (r"\bMEDIA_CACHE_TTL\b", "DESIGN_AGENT_CACHE_TTL"),
        (r"--lc-", "--brand-"),
        (r"langchain-tokens", "tokens"),
        (
            r"^(\s*)from (harness|middleware|tools|pipelines)(\.| import)",
            r"\1from design_agent.\2\3",
        ),
        (r"^(\s*)import (harness|middleware|tools|pipelines)\b", r"\1import design_agent.\2"),
        (r"^(\s*)from (models|subagents) import", r"\1from design_agent.\2 import"),
    )
)


@functools.cache
def _hygiene() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "hygiene", ROOT / "tests/unit/test_public_hygiene.py"
    )
    if spec is None or spec.loader is None:
        raise SystemExit("tests/unit/test_public_hygiene.py is missing")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


def entry_for(path: str) -> Entry:
    entry = ALLOWLIST.get(path) or _directory_entry(path)
    if entry is None:
        raise SystemExit(f"not on the allowlist: {path}")
    return entry


def read_source(path: str) -> bytes:
    entry_for(path)
    return subprocess.run(
        ["git", "-C", str(REFERENCE), "show", f"{REVISION}:{path}"], capture_output=True, check=True
    ).stdout


def allowlisted_under(prefix: str) -> list[str]:
    """Every file at the pinned revision under `prefix` that the allowlist admits."""
    listed = subprocess.run(
        ["git", "-C", str(REFERENCE), "ls-tree", "-r", "--name-only", REVISION, "--", prefix],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.splitlines()
    return [path for path in listed if path in ALLOWLIST or _directory_entry(path) is not None]


def scrub(text: str) -> str:
    for pattern, replacement in REWRITES:
        text = pattern.sub(replacement, text)
    return text


def findings_for(text: str, target: str) -> list[str]:
    hygiene = _hygiene()
    found: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for rule in hygiene.RULES:
            if rule.pattern.search(line) and not hygiene._matches(target, rule.allowed):
                found.append(f"{target}:{number}: {rule.category}")
        found.extend(f"{target}:{number}: {hit}" for hit in hygiene._identity_hits(line))
    return found


def log(record: dict[str, object]) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def import_one(path: str, *, force: bool, allow_findings: bool) -> int:
    entry = entry_for(path)
    raw = read_source(path)
    target = ROOT / entry.target
    if b"\0" in raw[:8192]:
        found = []  # binary: copied as is after the allowlist and path checks
        if target.exists() and not force:
            print(f"skip {path}: {entry.target} exists (use --force)")
            return 0
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        log(
            {
                "at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
                "source": path,
                "revision": REVISION,
                "source_sha256": hashlib.sha256(raw).hexdigest(),
                "target": entry.target,
                "action": entry.action,
                "binary": True,
            }
        )
        print(f"imported {path} -> {entry.target} (binary)")
        return 0
    text = scrub(raw.decode("utf-8"))
    if target.exists() and not force:
        print(f"skip {path}: {entry.target} exists (use --force)")
        return 0
    found = findings_for(text, entry.target)
    if found and not allow_findings:
        print(f"refused {path}: the scrubbed text still trips the hygiene scan:", file=sys.stderr)
        print("\n".join(f"  {f}" for f in found), file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    log(
        {
            "at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            "source": path,
            "revision": REVISION,
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "target": entry.target,
            "target_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "action": entry.action,
            "mit_lineage": entry.mit_lineage,
            "findings": found,
        }
    )
    print(
        f"imported {path} -> {entry.target} ({entry.action}{', findings recorded' if found else ''})"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    show = sub.add_parser("show")
    show.add_argument("path")
    run = sub.add_parser("import")
    run.add_argument("paths", nargs="+")
    run.add_argument("--force", action="store_true")
    run.add_argument("--allow-findings", action="store_true")
    tree = sub.add_parser("import-dir", help="import every allowlisted file under a skill folder")
    tree.add_argument("prefix")
    tree.add_argument("--force", action="store_true")
    tree.add_argument("--allow-findings", action="store_true")
    args = parser.parse_args()
    if args.command == "list":
        for path, entry in sorted(ALLOWLIST.items()):
            state = "present" if (ROOT / entry.target).exists() else "-"
            print(f"{entry.action:10} {state:8} {path} -> {entry.target}")
        for prefix, (target, action, excluded) in sorted(SKILL_DIRECTORIES.items()):
            print(
                f"{action:10} {'dir':8} {prefix} -> {target} (excluding {', '.join(excluded) or 'nothing'})"
            )
        return 0
    if args.command == "show":
        sys.stdout.write(scrub(read_source(args.path).decode("utf-8")))
        return 0
    paths = allowlisted_under(args.prefix) if args.command == "import-dir" else args.paths
    if not paths:
        print(f"nothing allowlisted under {args.prefix}", file=sys.stderr)
        return 1
    return max(import_one(p, force=args.force, allow_findings=args.allow_findings) for p in paths)


if __name__ == "__main__":
    raise SystemExit(main())
