"""Host tools: SSRF hardening, media tools without keys, provider calls with a mocked transport."""

from __future__ import annotations

import base64
import json
import struct
import zlib
from typing import Any

import httpx
import pytest
from deepagents.backends.protocol import FileDownloadResponse, FileUploadResponse

from design_agent.config import Settings
from design_agent.tools.fetch import FetchRefused, build_fetch_tool, check_url, public_address
from design_agent.tools.media import _png_alpha_report, build_media_tools


class MemoryBackend:
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    async def aupload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        self.files.update(files)
        return [FileUploadResponse(path=p) for p, _ in files]

    async def adownload_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        return [
            FileDownloadResponse(
                path=p,
                content=self.files.get(p),
                error=None if p in self.files else "file_not_found",
            )
            for p in paths
        ]


def resolver_for(mapping: dict[str, list[str]]):  # type: ignore[no-untyped-def]
    async def resolve(host: str, port: int) -> list[str]:
        return mapping[host]

    return resolve


@pytest.mark.parametrize(
    "address",
    [
        "10.0.0.5",
        "127.0.0.1",
        "169.254.169.254",
        "::1",
        "fe80::1",
        "100.64.1.1",
        "::ffff:10.0.0.1",
        "0.0.0.0",
    ],
)
def test_private_and_metadata_addresses_are_not_public(address: str) -> None:
    assert not public_address(address)


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com/a.png",
        "https://user:pw@example.com/a.png",
        "https://example.com:8443/a.png",
        "http://localhost/a.png",
        "http://metadata.google.internal/computeMetadata/v1/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/a.png",
        "https://rebind.example/a.png",
    ],
)
async def test_unsafe_urls_are_refused(url: str) -> None:
    with pytest.raises(FetchRefused):
        await check_url(url, resolver_for({"rebind.example": ["93.184.216.34", "192.168.1.10"]}))


async def test_fetch_rechecks_redirects_and_writes_the_file() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "cdn.example":
            return httpx.Response(302, headers={"location": "https://internal.example/secret.png"})
        return httpx.Response(200, content=b"x", headers={"content-type": "image/png"})

    backend = MemoryBackend()
    tool = build_fetch_tool(
        lambda _rt: backend,  # type: ignore[arg-type,return-value]
        resolver=resolver_for({"cdn.example": ["93.184.216.34"], "internal.example": ["10.1.2.3"]}),
        transport=httpx.MockTransport(handler),
    )
    result = await tool.coroutine(
        url="https://cdn.example/a.png", sandbox_path="/workspace/attachments/a.png", runtime=None
    )  # type: ignore[misc]
    assert "private or reserved" in result and not backend.files


async def test_fetch_refuses_web_pages_and_svg() -> None:
    backend = MemoryBackend()
    for kind in ("text/html", "image/svg+xml"):
        tool = build_fetch_tool(
            lambda _rt: backend,  # type: ignore[arg-type,return-value]
            resolver=resolver_for({"cdn.example": ["93.184.216.34"]}),
            transport=httpx.MockTransport(
                lambda _r, kind=kind: httpx.Response(
                    200, content=b"<x>", headers={"content-type": kind}
                )
            ),
        )
        result = await tool.coroutine(
            url="https://cdn.example/a", sandbox_path="/workspace/attachments/a", runtime=None
        )  # type: ignore[misc]
        assert "not fetched" in result
    assert not backend.files


async def test_media_tools_explain_missing_keys_without_calling_out() -> None:
    backend = MemoryBackend()
    tools = {t.name: t for t in build_media_tools(Settings(_env_file=None), lambda _rt: backend)}  # type: ignore[call-arg,arg-type,return-value]
    image = await tools["generate_image"].coroutine(
        prompt="a lamp", sandbox_path="/workspace/projects/p/lamp.png", runtime=None
    )  # type: ignore[misc]
    assert "no OPENAI_API_KEY" in image
    voice = await tools["generate_voiceover"].coroutine(
        text="Hi",
        voice_id="abcdefghij12",
        sandbox_path="/workspace/projects/p/vo.mp3",
        runtime=None,
    )  # type: ignore[misc]
    assert "no ELEVENLABS_API_KEY" in voice
    assert "under /workspace" in await tools["generate_image"].coroutine(
        prompt="x", sandbox_path="/etc/x.png", runtime=None
    )  # type: ignore[misc]


def _png(width: int, height: int, alpha: int) -> bytes:
    raw = b"".join(b"\x00" + bytes([255, 0, 0, alpha]) * width for _ in range(height))

    def chunk(kind: bytes, body: bytes) -> bytes:
        return (
            struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def test_alpha_report_measures_pixels_not_the_request_flag() -> None:
    assert _png_alpha_report(_png(4, 4, 0)) == (True, 1.0)
    assert _png_alpha_report(_png(4, 4, 255)) == (True, 0.0)
    assert _png_alpha_report(b"not a png") == (None, None)


async def test_generate_image_writes_b64_output_and_reports_alpha(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {"data": [{"b64_json": base64.b64encode(_png(2, 2, 0)).decode()}]}
    seen: dict[str, Any] = {}

    async def fake_post(self: httpx.AsyncClient, url: str, **kwargs: Any) -> httpx.Response:
        seen.update(url=url, body=kwargs["json"])
        return httpx.Response(
            200, content=json.dumps(payload).encode(), request=httpx.Request("POST", url)
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    backend = MemoryBackend()
    tools = {
        t.name: t
        for t in build_media_tools(
            Settings(_env_file=None, openai_api_key="sk-test"), lambda _rt: backend
        )
    }  # type: ignore[call-arg,arg-type,return-value]
    result = await tools["generate_image"].coroutine(
        prompt="a lamp",
        sandbox_path="/workspace/projects/p/lamp.png",
        runtime=None,
        background="transparent",
        output_format="png",
    )  # type: ignore[misc]
    assert "wrote /workspace/projects/p/lamp.png" in result and "alpha verified" in result
    assert seen["body"]["model"] == "gpt-image-2.5-flare"
    assert seen["url"].startswith("https://api.openai.com/")
