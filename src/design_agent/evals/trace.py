"""A run's trace: the person's turns, the agent's replies and every tool call, in order."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage


@dataclass(frozen=True)
class Call:
    index: int
    name: str
    args: dict[str, Any]
    ok: bool
    result: str

    @property
    def command(self) -> str:
        return str(self.args.get("command") or "") if self.name == "execute" else ""


@dataclass
class Trace:
    calls: list[Call] = field(default_factory=list)
    replies: list[str] = field(default_factory=list)
    """The agent's final words of each turn the person saw (wake-up replies included)."""

    @classmethod
    def from_messages(
        cls, messages: Sequence[BaseMessage], extra_replies: Sequence[str] = ()
    ) -> Trace:
        results = {m.tool_call_id: m for m in messages if isinstance(m, ToolMessage)}
        trace = cls()
        index = 0
        for position, message in enumerate(messages):
            if isinstance(message, AIMessage):
                for call in message.tool_calls:
                    result = results.get(str(call.get("id")))
                    trace.calls.append(
                        Call(
                            index=index,
                            name=str(call.get("name")),
                            args=dict(call.get("args") or {}),
                            ok=result is not None
                            and result.status != "error"
                            and "exit code 1" not in str(result.content)[-200:],
                            result=str(result.content) if result is not None else "",
                        )
                    )
                    index += 1
                following = messages[position + 1] if position + 1 < len(messages) else None
                if (
                    not message.tool_calls
                    and message.text.strip()
                    and (following is None or isinstance(following, HumanMessage))
                ):
                    trace.replies.append(message.text.strip())
        trace.replies.extend(extra_replies)
        return trace

    def first(self, predicate: Any) -> int | None:
        return next((c.index for c in self.calls if predicate(c)), None)

    def named(self, name: str) -> list[Call]:
        return [c for c in self.calls if c.name == name]
