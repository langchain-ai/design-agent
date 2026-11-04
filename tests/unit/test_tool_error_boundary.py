"""Unit tests for tool error boundaries (SPEC §7.10).

Covers HostMediaErrorBoundary, DelegatedTaskErrorBoundary, and FileDeliveryErrorBoundary:
exception conversion, bubble-up preservation, tool filtering, and guards registration.
"""

from __future__ import annotations

import ssl

import pytest
from langchain.agents.middleware import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.errors import GraphBubbleUp

from design_agent.middleware.guards import model_guards
from design_agent.middleware.tool_error_boundary import (
    HOST_MEDIA_TOOLS,
    DelegatedTaskErrorBoundary,
    FileDeliveryErrorBoundary,
    HostMediaErrorBoundary,
)


def _request(tool_name: str, call_id: str = "call_123") -> ToolCallRequest:
    return ToolCallRequest(
        tool_call={"name": tool_name, "args": {"sample": "arg"}, "id": call_id},
        tool=None,
        state={"messages": []},
        runtime=None,  # type: ignore[arg-type]
    )


def test_host_media_tools_contains_expected_set() -> None:
    expected = {
        "generate_image",
        "generate_voiceover",
        "generate_sound_effect",
        "generate_music",
        "transcribe_audio",
        "fetch_asset",
    }
    assert HOST_MEDIA_TOOLS == expected


@pytest.mark.parametrize("tool_name", sorted(HOST_MEDIA_TOOLS))
async def test_host_media_error_boundary_catches_unhandled_exceptions_async(tool_name: str) -> None:
    boundary = HostMediaErrorBoundary()
    req = _request(tool_name, call_id=f"id_{tool_name}")

    async def failing_handler(_req: ToolCallRequest) -> ToolMessage:
        raise TimeoutError("connection timed out after 30s")

    result = await boundary.awrap_tool_call(req, failing_handler)
    assert isinstance(result, ToolMessage)
    assert result.status == "error"
    assert result.name == tool_name
    assert result.tool_call_id == f"id_{tool_name}"
    assert f"The {tool_name} call failed (TimeoutError)" in result.content
    assert "connection timed out" not in result.content


@pytest.mark.parametrize(
    ("error", "kind"),
    [
        (TimeoutError("socket timeout"), "TimeoutError"),
        (ssl.SSLError("handshake failed"), "SSLError"),
        (ConnectionResetError("peer reset connection"), "ConnectionResetError"),
        (OSError("network unreachable"), "OSError"),
        (RuntimeError("byte corruption"), "RuntimeError"),
        (ValueError("malformed response"), "ValueError"),
    ],
)
async def test_host_media_error_boundary_formats_exception_classes(
    error: Exception, kind: str
) -> None:
    boundary = HostMediaErrorBoundary()
    req = _request("generate_image", call_id="c_img")

    async def failing_handler(_req: ToolCallRequest) -> ToolMessage:
        raise error

    result = await boundary.awrap_tool_call(req, failing_handler)
    assert isinstance(result, ToolMessage)
    assert result.status == "error"
    assert result.content == (
        f"The generate_image call failed ({kind}). Other tools still work; "
        "retry if the failure could be transient, or carry on without it."
    )


async def test_host_media_error_boundary_ignores_untracked_tools() -> None:
    boundary = HostMediaErrorBoundary()
    req = _request("render_video", call_id="c_render")

    async def failing_handler(_req: ToolCallRequest) -> ToolMessage:
        raise RuntimeError("render failed")

    with pytest.raises(RuntimeError, match="render failed"):
        await boundary.awrap_tool_call(req, failing_handler)

    success_msg = ToolMessage(content="ok", tool_call_id="c_render", name="render_video")

    async def success_handler(_req: ToolCallRequest) -> ToolMessage:
        return success_msg

    result = await boundary.awrap_tool_call(req, success_handler)
    assert result is success_msg


async def test_host_media_error_boundary_reraises_graph_bubble_up() -> None:
    boundary = HostMediaErrorBoundary()
    req = _request("generate_image")

    async def bubble_handler(_req: ToolCallRequest) -> ToolMessage:
        raise GraphBubbleUp()

    with pytest.raises(GraphBubbleUp):
        await boundary.awrap_tool_call(req, bubble_handler)


def test_host_media_error_boundary_sync_wrap() -> None:
    boundary = HostMediaErrorBoundary()
    req = _request("fetch_asset", call_id="c_fetch")

    def failing_handler(_req: ToolCallRequest) -> ToolMessage:
        raise TimeoutError("sync timeout")

    result = boundary.wrap_tool_call(req, failing_handler)
    assert isinstance(result, ToolMessage)
    assert result.status == "error"
    assert "The fetch_asset call failed (TimeoutError)" in result.content

    def bubble_handler(_req: ToolCallRequest) -> ToolMessage:
        raise GraphBubbleUp()

    with pytest.raises(GraphBubbleUp):
        boundary.wrap_tool_call(req, bubble_handler)


def test_host_media_error_boundary_custom_config() -> None:
    boundary = HostMediaErrorBoundary(
        tools=["custom_tool"],
        reply="Custom {tool} failed: {kind}",
    )
    assert boundary.target_tools == frozenset({"custom_tool"})

    req = _request("custom_tool", call_id="custom_1")

    def failing_handler(_req: ToolCallRequest) -> ToolMessage:
        raise ValueError("bad parameter")

    result = boundary.wrap_tool_call(req, failing_handler)
    assert isinstance(result, ToolMessage)
    assert result.status == "error"
    assert result.content == "Custom custom_tool failed: ValueError"


def test_guards_registers_host_media_error_boundary_for_lead() -> None:
    lead_guards = model_guards(
        role="lead",
        lead=True,
        summaries={},
        disclosure=None,
        servers=(),
    )
    media_boundaries = [g for g in lead_guards if isinstance(g, HostMediaErrorBoundary)]
    assert len(media_boundaries) == 1

    task_boundaries = [g for g in lead_guards if isinstance(g, DelegatedTaskErrorBoundary)]
    assert len(task_boundaries) == 1

    delivery_boundaries = [g for g in lead_guards if isinstance(g, FileDeliveryErrorBoundary)]
    assert len(delivery_boundaries) == 1


def test_guards_registers_host_media_error_boundary_for_helpers() -> None:
    helper_guards = model_guards(
        role="helper",
        lead=False,
        summaries={},
        disclosure=None,
        servers=(),
    )
    media_boundaries = [g for g in helper_guards if isinstance(g, HostMediaErrorBoundary)]
    assert len(media_boundaries) == 1

    # Task and delivery are lead-only
    assert not any(isinstance(g, DelegatedTaskErrorBoundary) for g in helper_guards)
    assert not any(isinstance(g, FileDeliveryErrorBoundary) for g in helper_guards)


async def test_host_media_error_boundary_handles_missing_call_id() -> None:
    boundary = HostMediaErrorBoundary()
    req = ToolCallRequest(
        tool_call={"name": "generate_image", "args": {}},
        tool=None,
        state={"messages": []},
        runtime=None,  # type: ignore[arg-type]
    )

    async def failing_handler(_req: ToolCallRequest) -> ToolMessage:
        raise OSError("network down")

    result = await boundary.awrap_tool_call(req, failing_handler)
    assert isinstance(result, ToolMessage)
    assert result.status == "error"
    assert result.tool_call_id == ""
    assert "The generate_image call failed (OSError)" in result.content
