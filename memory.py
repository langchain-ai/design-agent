"""MDA memory: a team layer every caller shares, and a personal layer per person.

`/memories/agent/` holds team rules (anyone who mentions the agent can add to it, so it is never a
place for private data). `/memories/user/` belongs to the verified person who asked; MDA mounts it
only for a run with a person behind it.

Declared here, the personal layer mounts where MDA's defaults put it: the person's Slack DM and
Studio. People ask for work in channel threads, so `agent.py` selects both layers for every Slack
run (`slack_run`) and their preferences follow them there. The cost: their hot `AGENTS.md` is in
context in a shared thread, which is why `instructions.md` says never to repeat it there.
"""

from managed_deepagents import ManagedServerRuntime, MemoryLayer, define_memory

memory = define_memory(agent=MemoryLayer(), user=MemoryLayer())


def slack_run(runtime: ManagedServerRuntime) -> bool:
    """A run a Slack event started (a mention, a DM, a thread reply or an approval click).

    MDA sets the runtime's channel only for a channel run, from its own routing, never from the
    context a caller sends; inspection, Studio, API and scheduled runs have none.
    """
    return runtime.channel is not None and runtime.channel.provider == "slack"
