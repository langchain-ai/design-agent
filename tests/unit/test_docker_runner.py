"""The Docker sandbox runner's isolation flags and path policy (docker calls are recorded, not run)."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from typing import Any

import pytest

from design_agent.runtime.sandbox.docker import DockerSandboxBackend, DockerSandboxRunner


class RecordingRunner(DockerSandboxRunner):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(image="design-agent-sandbox:test", **kwargs)
        self.calls: list[list[str]] = []
        self.running: set[str] = set()

    def _run(
        self,
        args: Sequence[str],
        *,
        input_bytes: bytes | None = None,
        timeout: float | None = 120,
        check: bool = True,
    ) -> subprocess.CompletedProcess[bytes]:
        self.calls.append(list(args))
        if args[0] == "container":
            name = args[-1]
            return subprocess.CompletedProcess(
                args,
                0 if name in self.running else 1,
                b"true" if name in self.running else b"",
                b"",
            )
        if args[0] == "run":
            self.running.add(args[args.index("--name") + 1])
        if args[0] == "exec" and args[-2:-1] == ["cat"]:
            return subprocess.CompletedProcess(args, 0, b"content", b"")
        return subprocess.CompletedProcess(args, 0, b"ok", b"")


def test_container_runs_isolated() -> None:
    runner = RecordingRunner()
    runner.container_for("thread-a")
    run = next(c for c in runner.calls if c[0] == "run")
    flag = lambda name: run[run.index(name) + 1]  # noqa: E731
    assert flag("--network") == "none"
    assert flag("--cap-drop") == "ALL"
    assert flag("--security-opt") == "no-new-privileges"
    assert "/var/run/docker.sock" not in " ".join(run)
    assert flag("--mount").startswith("type=volume,") and flag("--mount").endswith(
        "target=/workspace"
    )


def test_threads_get_their_own_container_and_volume() -> None:
    runner = RecordingRunner()
    assert runner.container_for("a") != runner.container_for("b")
    assert runner.names_for("a")[1] != runner.names_for("b")[1]
    assert sum(1 for c in runner.calls if c[0] == "run") == 2
    runner.container_for("a")
    assert sum(1 for c in runner.calls if c[0] == "run") == 2, "a running container is reused"


def test_agent_commands_run_unprivileged_and_staging_runs_as_root() -> None:
    runner = RecordingRunner()
    runner.exec("t", "echo hi")
    agent = [c for c in runner.calls if c[0] == "exec"][-1]
    assert agent[agent.index("--user") + 1] == "1000:1000"
    runner.exec("t", "fc-cache", root=True)
    staged = [c for c in runner.calls if c[0] == "exec"][-1]
    assert staged[staged.index("--user") + 1] == "0:0"


def test_commands_are_killed_inside_the_container_on_timeout() -> None:
    runner = RecordingRunner()
    runner.exec("t", "sleep 100", timeout=7)
    script = [c for c in runner.calls if c[0] == "exec"][-1][-1]
    assert "timeout --kill-after=10 7 bash -c" in script


def test_uploads_outside_writable_folders_are_refused() -> None:
    runner = RecordingRunner()
    backend = DockerSandboxBackend(runner, thread_id=lambda: "t")
    results = backend.upload_files(
        [("/workspace/brand/tokens.json", b"{}"), ("/workspace/projects/x/a.txt", b"a")]
    )
    assert [r.error for r in results] == ["permission_denied", None]


@pytest.mark.parametrize("path", ["/etc/passwd", "/workspace/../etc/shadow", "/root/.ssh/id_rsa"])
def test_downloads_outside_readable_folders_are_refused(path: str) -> None:
    backend = DockerSandboxBackend(RecordingRunner(), thread_id=lambda: "t")
    assert backend.download_files([path])[0].error == "permission_denied"


def test_idle_containers_are_stopped_but_volumes_kept() -> None:
    now = [0.0]
    runner = RecordingRunner(idle_ttl_seconds=60, clock=lambda: now[0])
    runner.container_for("t")
    now[0] = 61
    assert runner.reap_idle() == [runner.names_for("t")[0]]
    assert not any(c[0] in {"rm", "volume"} for c in runner.calls)
