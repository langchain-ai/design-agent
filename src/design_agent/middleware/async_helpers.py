"""Background helpers on Managed Deep Agents: MDA's async subagents, on the model the lead picks.

MDA 0.10 runs each subagent declared `"async": True` as its own graph on the Agent Server, on a
thread of its own that shares the lead's sandbox, and gives the lead deepagents' tools for it:
`start_async_task`, `check_async_task`, `update_async_task`, `cancel_async_task` and
`list_async_tasks`. A task survives a deploy, and deepagents wakes an idle lead when one ends.
This agent declares one such subagent, `worker` (`agent.py`), and the lead picks each task's model
and effort:

- `AsyncHelpersMiddleware` (the lead's) shows `start_async_task` with `model` and `effort` in place
  of `subagent_type`, checks the choice (`choose`), and stamps it on the run context deepagents
  forwards to the task's run. That context goes without MDA's routing (`mda_*` keys), so nothing
  the worker sends carries the lead's Slack binding. `update_async_task` runs a task on again on
  the choice it started with, kept on the task's record in `async_tasks`.
- `WorkerModelMiddleware` (first in the worker's own stack) swaps the stamped model in on every
  call. A run with no stamp, such as one the lead did not start, keeps the worker's own model.

MDA builds an async subagent's graph from a static spec, so a model cannot be declared per task;
the choice travels on the run context instead. Middleware that reads `request.model` per call
follows the swap; what deepagents settled at build time from the spec's model (its summarization
trigger) does not. The self-hosted runtime has no Agent Server, so it keeps `start_task`
(`middleware/background.py`).
"""

from __future__ import annotations

import dataclasses
import logging
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from typing import Any

from deepagents.middleware.async_subagents import StartAsyncTaskSchema
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.agents.middleware.types import ModelCallResult
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from langgraph.types import Command
from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

from design_agent.config import ModelSpec, Settings
from design_agent.models.factory import build_chat_model, resolve_model
from design_agent.models.registry import ModelConfigurationError, ToolDisclosure, capabilities_for
from design_agent.subagents import EFFORT_ORDER, WORKERS, capped

_LOGGER = logging.getLogger(__name__)

#: The async subagent every task the lead starts runs on (`agent.py` declares it by this name).
WORKER = "worker"
#: Where the lead's choice travels on the task's run context: `{"model": ..., "effort": ...}`.
CHOICE_KEY = "design_agent_helper"
START, UPDATE = "start_async_task", "update_async_task"
#: deepagents' key for an async run's parent reference, which it adds itself.
_PARENT_KEY = "deepagents_parent"
#: MDA's routing keys on a run context: a Slack binding the worker must not carry.
_ROUTING_PREFIX = "mda_"
#: The stall ceiling by effort: a call at xhigh or max may think for a long time before it streams.
TIMEOUT_BY_EFFORT = {worker.effort: worker.timeout_seconds for worker in WORKERS}
#: Where deepagents' description lists its agent types, which the lead sees as a choice instead.
_TYPES_HEAD, _USAGE_HEAD = "Available async agent types:", "## Usage notes:"

Choose = Callable[[str, str], "tuple[str, str] | str"]
BuildModel = Callable[[str, str], BaseChatModel]


def build_helper_model(
    settings: Settings, model: str, effort: str, *, project_root: Path | None = None
) -> BaseChatModel:
    """The chat model a helper runs on: `model` at `effort` ("" for the model's default), built
    as the helper role is, so it gets the same provider fixes, gateway routing and keys."""
    chosen = settings.model_copy(update={"helper_model": model})
    kwargs: dict[str, Any] = {"streaming": True}
    if timeout := TIMEOUT_BY_EFFORT.get(effort):
        kwargs["timeout"] = timeout
    return build_chat_model(
        chosen, "helper", effort=effort or None, project_root=project_root, **kwargs
    )


def choose(settings: Settings, build: BuildModel, model: str, effort: str) -> tuple[str, str] | str:
    """The lead's choice as `(model, effort)`, or what to fix: any `provider:model` LangChain can
    build here (empty for the helper default), at an effort that model takes, under the
    deployment's cap. Building it checks the provider package and key, with no network call."""
    raw = model.strip() or str(settings.role_model("helper"))
    try:
        spec = str(ModelSpec.parse(raw, setting="model"))
    except ValueError as error:
        return f"Not started: {error}, like anthropic:claude-opus-5-5 or openai:gpt-5.5."
    asked = effort.strip().lower()
    if asked and asked not in EFFORT_ORDER:
        return f"Not started: effort is one of {', '.join(EFFORT_ORDER)}, or empty."
    try:
        asked = capped(asked, settings.helper_effort_cap) if asked else ""
        on = settings.model_copy(update={"helper_model": spec})
        effort = resolve_model(on, "helper", effort=asked or None).effort or ""
        build(spec, effort)
    except ModelConfigurationError as error:
        return f"Not started: {error}."
    except Exception as error:  # noqa: BLE001 - a provider package or key may be missing
        return f"Not started: {spec} does not build here ({type(error).__name__}: {error})."
    return spec, effort


def stamped(context: object) -> tuple[str, str] | None:
    """The model and effort stamped on a run context or a task record, or None."""
    data = _as_mapping(context)
    chosen = data.get(CHOICE_KEY) if data is not None else None
    if not isinstance(chosen, Mapping):
        return None
    model, effort = chosen.get("model"), chosen.get("effort")
    return (model, effort) if isinstance(model, str) and isinstance(effort, str) else None


def forwarded(context: object) -> dict[str, Any]:
    """A run context as data for a task's run: without deepagents' parent reference, MDA's
    routing, or a choice that came back on a finished task's notification."""
    data = _as_mapping(context) or {}
    return {
        str(key): value
        for key, value in data.items()
        if key not in {_PARENT_KEY, CHOICE_KEY} and not str(key).startswith(_ROUTING_PREFIX)
    }


def _as_mapping(context: object) -> Mapping[str, Any] | None:
    if isinstance(context, BaseModel):
        return context.model_dump(mode="json")
    if dataclasses.is_dataclass(context) and not isinstance(context, type):
        return dataclasses.asdict(context)
    return context if isinstance(context, Mapping) else None


class _StartSchema(StartAsyncTaskSchema):
    # Every task runs on `worker`, so the lead is not shown a type.
    subagent_type: SkipJsonSchema[str] = WORKER
    model: str = Field(
        default="",
        description=(
            "The model this helper runs on: any LangChain `provider:model`. Empty for the default."
        ),
    )
    effort: str = Field(
        default="",
        description=(
            "Its reasoning effort: low, medium, high, xhigh or max, as the model takes it. Empty "
            "for the model's default."
        ),
    )


def listing(settings: Settings) -> str:
    """What the lead reads in place of deepagents' agent types."""
    uses = "\n".join(f"- `{worker.effort}`: {worker.use}" for worker in WORKERS)
    return (
        "Every task runs on a helper with the same tools and skills as you. Pick its `model`: any "
        f"LangChain `provider:model` (default {settings.role_model('helper')}), and its "
        f"`effort`, matched to the work:\n{uses}\nIts whole prompt is your `description`: send a "
        "complete brief."
    )


class AsyncHelpersMiddleware(AgentMiddleware[Any, Any, Any]):
    """The lead's side: `start_async_task` with `model` and `effort` (module doc)."""

    def __init__(self, settings: Settings, choose_for: Choose) -> None:
        super().__init__()
        self._listing = listing(settings)
        self._choose = choose_for

    def _shown(self, tool: Any) -> Any:
        if not isinstance(tool, BaseTool) or tool.name != START:
            return tool
        head, found, rest = (tool.description or "").partition(_TYPES_HEAD)
        _, usage, notes = rest.partition(_USAGE_HEAD)
        text = f"{head}{self._listing}\n\n{usage}{notes}" if found and usage else tool.description
        return tool.model_copy(update={"args_schema": _StartSchema, "description": text})

    def _with_start(self, request: ModelRequest[Any]) -> ModelRequest[Any]:
        tools = [self._shown(tool) for tool in request.tools]
        changed = any(new is not old for new, old in zip(tools, request.tools, strict=True))
        return request.override(tools=tools) if changed else request

    def wrap_model_call(
        self, request: ModelRequest[Any], handler: Callable[[ModelRequest[Any]], ModelResponse[Any]]
    ) -> ModelResponse[Any]:
        return handler(self._with_start(request))

    async def awrap_model_call(
        self,
        request: ModelRequest[Any],
        handler: Callable[[ModelRequest[Any]], Awaitable[ModelResponse[Any]]],
    ) -> ModelResponse[Any]:
        return await handler(self._with_start(request))

    async def awrap_tool_call(
        self, request: Any, handler: Callable[[Any], Awaitable[Any]]
    ) -> ToolMessage | Command[Any]:
        call = request.tool_call
        name = call.get("name")
        if name == START:
            args = dict(call.get("args") or {})
            picked = self._choose(
                str(args.pop("model", "") or ""), str(args.pop("effort", "") or "")
            )
            if isinstance(picked, str):
                return ToolMessage(picked, tool_call_id=call["id"], status="error")
            chosen: Mapping[str, str] | None = {"model": picked[0], "effort": picked[1]}
            request = request.override(
                tool_call={**call, "args": {**args, "subagent_type": WORKER}}
            )
        elif name == UPDATE:
            chosen = _chosen_for(request, str((call.get("args") or {}).get("task_id") or ""))
        else:
            result: ToolMessage | Command[Any] = await handler(request)
            return result
        result = await handler(_with_choice(request, chosen))
        return _marked(result, chosen) if name == START and chosen is not None else result


def _with_choice(request: Any, chosen: Mapping[str, str] | None) -> Any:
    """`request` with a runtime whose context is what the task's run gets (`forwarded`), plus the
    model and effort it runs on."""
    runtime = getattr(request, "runtime", None)
    if not dataclasses.is_dataclass(runtime) or isinstance(runtime, type):
        return request
    context = forwarded(getattr(runtime, "context", None))
    if chosen is not None:
        context[CHOICE_KEY] = dict(chosen)
    return request.override(runtime=dataclasses.replace(runtime, context=context or None))


def _chosen_for(request: Any, task_id: str) -> Mapping[str, str] | None:
    """The choice a task started on, from its record: a follow-up keeps its model and its cache."""
    state = getattr(request, "state", None)
    tasks = state.get("async_tasks") if isinstance(state, Mapping) else None
    task = tasks.get(task_id) if isinstance(tasks, Mapping) else None
    chosen = stamped(task)
    return {"model": chosen[0], "effort": chosen[1]} if chosen is not None else None


def _marked(result: Any, chosen: Mapping[str, str]) -> Any:
    """The started task's record carrying its choice; deepagents' later updates keep the key."""
    update = getattr(result, "update", None)
    if not isinstance(update, Mapping):
        return result
    tasks = update.get("async_tasks")
    if not isinstance(tasks, Mapping) or len(tasks) != 1:
        return result
    ((task_id, task),) = tasks.items()
    marked = {**task, CHOICE_KEY: dict(chosen)}
    return dataclasses.replace(result, update={**update, "async_tasks": {task_id: marked}})


class WorkerModelMiddleware(AgentMiddleware[Any, Any, Any]):
    """The worker's side: each model call runs on the stamped model and effort (module doc)."""

    def __init__(self, build: BuildModel) -> None:
        super().__init__()
        self._build = build
        self._built: dict[tuple[str, str], BaseChatModel | None] = {}

    def _swapped(self, request: ModelRequest[Any]) -> ModelRequest[Any]:
        chosen = stamped(getattr(request.runtime, "context", None))
        if chosen is None:
            return request
        if chosen not in self._built:
            try:
                self._built[chosen] = self._build(*chosen)
            except Exception:  # noqa: BLE001 - the lead checked it; a later deploy may not build it
                _LOGGER.warning("[worker] %s at %s no longer builds; using the default", *chosen)
                self._built[chosen] = None
        model = self._built[chosen]
        return request if model is None else request.override(model=model)

    def wrap_model_call(
        self, request: ModelRequest[Any], handler: Callable[[ModelRequest[Any]], ModelResponse[Any]]
    ) -> ModelResponse[Any]:
        return handler(self._swapped(request))

    async def awrap_model_call(
        self,
        request: ModelRequest[Any],
        handler: Callable[[ModelRequest[Any]], Awaitable[ModelResponse[Any]]],
    ) -> ModelResponse[Any]:
        return await handler(self._swapped(request))


class WorkerDisclosure(AgentMiddleware[Any, Any, Any]):
    """MCP tool disclosure for the model each call runs on. The worker's model changes per task,
    and provider-native tool search fails on a model without it (`middleware/tool_disclosure.py`),
    so the disclosure is picked per call, by the stamped model or else the worker's default."""

    def __init__(
        self,
        default: str,
        for_disclosure: Callable[[ToolDisclosure], AgentMiddleware[Any, Any, Any] | None],
    ) -> None:
        super().__init__()
        self._default = default
        self._for = for_disclosure
        self._made: dict[ToolDisclosure, AgentMiddleware[Any, Any, Any] | None] = {}

    def _pick(self, request: ModelRequest[Any]) -> AgentMiddleware[Any, Any, Any] | None:
        chosen = stamped(getattr(request.runtime, "context", None))
        spec = ModelSpec.parse(chosen[0] if chosen is not None else self._default, setting="model")
        disclosure = capabilities_for(spec).disclosure
        if disclosure not in self._made:
            self._made[disclosure] = self._for(disclosure)
        return self._made[disclosure]

    def wrap_model_call(
        self, request: ModelRequest[Any], handler: Callable[[ModelRequest[Any]], ModelResponse[Any]]
    ) -> ModelCallResult[Any]:
        inner = self._pick(request)
        return handler(request) if inner is None else inner.wrap_model_call(request, handler)

    async def awrap_model_call(
        self,
        request: ModelRequest[Any],
        handler: Callable[[ModelRequest[Any]], Awaitable[ModelResponse[Any]]],
    ) -> ModelCallResult[Any]:
        inner = self._pick(request)
        if inner is None:
            return await handler(request)
        return await inner.awrap_model_call(request, handler)
