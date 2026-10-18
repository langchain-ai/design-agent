"""Vendored HyperFrames skills: the lock, verification and the vendoring sync.

Vendored skills keep their upstream names at `skills/<name>/` (MDA discovers skills one level
deep) and are byte-identical to upstream at the pinned commit. `skills-lock.json` records the
upstream repository, commit, license and every file's sha256, plus files deliberately left out
with the reason. CI fails if a vendored file differs, an unlisted file appears, or an excluded
file is present. Local routing and brand guidance live in our own sibling skills, never as edits.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

UPSTREAM_REPO = "heygen-com/hyperframes"
UPSTREAM_COMMIT = "7735338b49ed6e11c227b0710da3bd35c3366b9c"
UPSTREAM_RELEASE = "v0.8.169"
LICENSE_FILE = "licenses/hyperframes-LICENSE.txt"

#: The upstream skills v0.1 routes to. Left out: figma (needs a Figma connection),
#: hyperframes-studio (the desktop app), product-launch-video (overlaps the launch_film
#: pipeline's routing), talking-head-recut (MIT-derived; not in the v0.1 skill set).
VENDORED_SKILLS = (
    "hyperframes",
    "hyperframes-core",
    "hyperframes-cli",
    "hyperframes-animation",
    "hyperframes-creative",
    "hyperframes-audio",
    "hyperframes-keyframes",
    "hyperframes-registry",
    "media-use",
    "slideshow",
    "pr-to-video",
    "music-to-video",
    "embedded-captions",
    "faceless-explainer",
    "general-video",
    "motion-graphics",
    "remotion-to-hyperframes",
)

#: Upstream files not vendored, with the reason. Third-party assets whose license is not
#: recorded beside them stay out until the partner confirms terms (docs/prep partner questions).
EXCLUDED: tuple[tuple[str, str], ...] = (
    ("*/gsap*.js", "vendored GSAP: the sandbox installs GSAP; compositions copy it from there"),
    (
        "media-use/audio/assets/sfx/*.mp3",
        "Pixabay Content License audio, pending partner and legal review",
    ),
    (
        "embedded-captions/modes/standard/fonts/files/*",
        "font binaries without license text beside them",
    ),
    (
        "embedded-captions/modes/standard/fonts/fonts.css",
        "inlines the excluded font binaries as base64",
    ),
    ("embedded-captions/assets/strokefonts/*", "assets without recorded provenance"),
    # fnmatch's `*` crosses `/`, so this covers every depth under a template's assets.
    (
        "music-to-video/references/templates/*/assets/*",
        "template assets without recorded provenance",
    ),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exclusion_reason(relative: str) -> str | None:
    """Why `relative` (``<skill>/<path>``) is not vendored, or None when it is."""
    for pattern, reason in EXCLUDED:
        if fnmatch.fnmatchcase(relative, pattern):
            return reason
    return None


def load_lock(root: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((root / "skills-lock.json").read_text())
    return data


@dataclass(frozen=True)
class VerifyResult:
    problems: tuple[str, ...]
    files: int

    @property
    def ok(self) -> bool:
        return not self.problems


def verify(root: Path) -> VerifyResult:
    """Every vendored file matches the lock; nothing extra; nothing excluded is present."""
    lock = load_lock(root)
    problems: list[str] = []
    count = 0
    if not (root / lock["upstream"]["license_file"]).is_file():
        problems.append(f"missing upstream license {lock['upstream']['license_file']}")
    for name, entry in sorted(lock["skills"].items()):
        folder = root / "skills" / name
        if not folder.is_dir():
            problems.append(f"skills/{name}: missing")
            continue
        expected: dict[str, str] = entry["files"]
        present = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}
        for relative in sorted(present - expected.keys()):
            problems.append(f"skills/{name}/{relative}: not in skills-lock.json")
        for relative, digest in sorted(expected.items()):
            path = folder / relative
            if not path.is_file():
                problems.append(f"skills/{name}/{relative}: missing")
            elif sha256(path) != digest:
                problems.append(
                    f"skills/{name}/{relative}: differs from upstream {lock['upstream']['commit'][:12]}"
                )
            count += 1
        for relative in entry.get("excluded", {}):
            if (folder / relative).exists():
                problems.append(f"skills/{name}/{relative}: excluded file is present")
    return VerifyResult(problems=tuple(problems), files=count)


def fetch_upstream(commit: str, destination: Path) -> Path:
    """Sparse-checkout `skills/` and LICENSE at `commit` into `destination`; returns the checkout."""
    url = f"https://github.com/{UPSTREAM_REPO}.git"
    checkout = destination / "hyperframes"
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git is required to vendor upstream skills")
    for args in (
        ["clone", "--filter=blob:none", "--no-checkout", "--sparse", url, str(checkout)],
        ["-C", str(checkout), "sparse-checkout", "set", "--no-cone", "/skills/", "/LICENSE"],
        ["-C", str(checkout), "checkout", "--quiet", commit],
    ):
        subprocess.run([git, *args], check=True, capture_output=True)  # noqa: S603 - fixed argv
    return checkout


def sync(
    root: Path, *, commit: str = UPSTREAM_COMMIT, release: str = UPSTREAM_RELEASE
) -> dict[str, Any]:
    """Replace the vendored skills with upstream at `commit` and rewrite skills-lock.json."""
    with tempfile.TemporaryDirectory() as scratch:
        upstream = fetch_upstream(commit, Path(scratch))
        lock: dict[str, Any] = {
            "version": 1,
            "upstream": {
                "repo": UPSTREAM_REPO,
                "commit": commit,
                "release": release,
                "license": "Apache-2.0",
                "license_file": LICENSE_FILE,
            },
            "skills": {},
        }
        (root / LICENSE_FILE).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(upstream / "LICENSE", root / LICENSE_FILE)
        for name in VENDORED_SKILLS:
            source = upstream / "skills" / name
            if not source.is_dir():
                raise RuntimeError(f"upstream {commit[:12]} has no skills/{name}")
            target = root / "skills" / name
            shutil.rmtree(target, ignore_errors=True)
            files: dict[str, str] = {}
            excluded: dict[str, str] = {}
            for path in sorted(p for p in source.rglob("*") if p.is_file()):
                relative = path.relative_to(source).as_posix()
                if reason := exclusion_reason(f"{name}/{relative}"):
                    excluded[relative] = reason
                    continue
                destination = target / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination)
                files[relative] = sha256(destination)
            lock["skills"][name] = {"files": files, "excluded": excluded}
        (root / "skills-lock.json").write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n")
    return lock
