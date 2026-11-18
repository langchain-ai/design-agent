"""A tool call that raises comes back to the model as a tool error, not a dead run.

Three categories of tools get this, each for its own reason:

- **`task`** (the lead's synchronous delegation). A subagent is a whole agent run inside one tool
  call; an exception it raises would propagate through the lead's tool node and end the lead's run
  with its progress. The lead gets a tool error instead and can do the step itself or delegate a
  smaller piece.
- **`upload_files`** (delivery). A send is usually the last step of a long job; if the platform's
  file transfer raises (for example when the channel credential cannot be read), ending the run
  there would lose the finished work and the reply, so the run goes on to say the file was not sent.
- **Host media tools** (`generate_image`, `generate_voiceover`, `generate_sound_effect`,
  `generate_music`, `transcribe_audio`, `fetch_asset`). Network or I/O failures from external
  media provider APIs (timeouts, SSL errors, byte corruption) return as tool errors so the run can
  fall back or notify the person rather than crashing midway through work.

Interrupts (`GraphBubbleUp`) keep their normal handling, and argument errors never get here (the
tool node converts them first). Only the exception class reaches the model: a subagent's message
can hold provider request text.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, ClassVar

from langchain.agents.middleware import AgentMiddleware, ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.errors import GraphBubbleUp
from langgraph.types import Command

_LOGGER = logging.getLogger(__name__)

HOST_MEDIA_TOOLS: frozenset[str] = frozenset(
    {
        "generate_image",
        "generate_voiceover",
        "generate_sound_effect",
        "generate_music",
        "transcribe_audio",
        "fetch_asset",
    }
)


class ToolErrorBoundary(AgentMiddleware):
    """Return a raised call to `tool` as a tool error saying `reply`, instead of ending the run.

    One subclass per tool, so each has its own middleware name and an agent can carry several.
    """

    tool: ClassVar[str]
    #: What the model is told, with `{kind}` for the exception class.
    reply: ClassVar[str]

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command[Any]]],
    ) -> ToolMessage | Command[Any]:
        if request.tool_call.get("name") != self.tool:
            return await handler(request)
        try:
            return await handler(request)
        except GraphBubbleUp:
            raise
        except Exception as error:  # noqa: BLE001 - this one tool's failure must not end the run
            kind = type(error).__name__
            _LOGGER.warning("[%s] call raised (%s); returned as a tool error", self.tool, kind)
            return ToolMessage(
                content=self.reply.format(kind=kind),
                tool_call_id=str(request.tool_call["id"]),
                name=self.tool,
                status="error",
            )


class DelegatedTaskErrorBoundary(ToolErrorBoundary):
    """A failed `task` delegation comes back to the parent as a tool error."""

    tool = "task"
    reply = (
        "The delegated task stopped before finishing ({kind}), so none of its result is available. "
        "Do that step directly, or delegate a smaller piece."
    )


class FileDeliveryErrorBoundary(ToolErrorBoundary):
    """An `upload_files` call that raised comes back to whichever agent made it."""

    tool = "upload_files"
    reply = (
        "The files were not sent ({kind}): the delivery channel could not be used, so nothing was "
        "attached, and whoever runs this deployment may need to reconnect it. Say they were not "
        "sent; never say they were."
    )


class HostMediaErrorBoundary(AgentMiddleware):
    """An unhandled error in a host media or asset-fetch tool comes back as a tool error."""

    reply: str
    _tools: frozenset[str]

    DEFAULT_TOOLS: ClassVar[frozenset[str]] = HOST_MEDIA_TOOLS
    DEFAULT_REPLY: ClassVar[str] = (
        "The {tool} call failed ({kind}). Other tools still work; "
        "retry if the failure could be transient, or carry on without it."
    )

    def __init__(
        self,
        tools: Sequence[str] | frozenset[str] | None = None,
        *,
        reply: str | None = None,
    ) -> None:
        super().__init__()
        self._tools = frozenset(tools) if tools is not None else self.DEFAULT_TOOLS
        self.reply = reply if reply is not None else self.DEFAULT_REPLY

    @property
    def target_tools(self) -> frozenset[str]:
        return self._tools

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command[Any]],
    ) -> ToolMessage | Command[Any]:
        tool_name = str(request.tool_call.get("name") or "")
        if tool_name not in self._tools:
            return handler(request)
        try:
            return handler(request)
        except GraphBubbleUp:
            raise
        except Exception as error:  # noqa: BLE001 - host media failure must not end the run
            kind = type(error).__name__
            _LOGGER.warning("[%s] call raised (%s); returned as a tool error", tool_name, kind)
            return ToolMessage(
                content=self.reply.format(tool=tool_name, kind=kind),
                tool_call_id=str(request.tool_call.get("id") or ""),
                name=tool_name,
                status="error",
            )

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command[Any]]],
    ) -> ToolMessage | Command[Any]:
        tool_name = str(request.tool_call.get("name") or "")
        if tool_name not in self._tools:
            return await handler(request)
        try:
            return await handler(request)
        except GraphBubbleUp:
            raise
        except Exception as error:  # noqa: BLE001 - host media failure must not end the run
            kind = type(error).__name__
            _LOGGER.warning("[%s] call raised (%s); returned as a tool error", tool_name, kind)
            return ToolMessage(
                content=self.reply.format(tool=tool_name, kind=kind),
                tool_call_id=str(request.tool_call.get("id") or ""),
                name=tool_name,
                status="error",
            )
