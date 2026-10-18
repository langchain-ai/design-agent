# Architecture

One agent assembly (`src/design_agent/assembly.py`) serves Managed Deep Agents, the CLI, the
self-hosted API and Slack. Runtime profiles (`src/design_agent/runtime/`) supply what differs: the
sandbox backend, how files are delivered, how the lead is woken, where state persists.

| Page | Covers |
| --- | --- |
| [Orchestration](orchestration.md) | background helpers, wake-ups and check-ins, restarts and durable transcripts, pipelines, looks, render watchers, learning |
| [Context and failures](context-and-failures.md) | what the model sees, tool disclosure, cache discipline, cost, failure boundaries |
| [Surfaces](surfaces.md) | Slack progress, footer and steering on MDA and self-hosted, the API, the CLI |

Request path: a message arrives (Slack, API, CLI) → the lead's turn: the workspace is staged into the
thread's sandbox (skills' scripts, gates, brand pack, fonts) → the lead plans, composes, renders in
the sandbox, looks at its work, runs the gates → finals are delivered with `upload_files` and
recorded in the project's `DELIVERY.json` so nothing is sent twice. Long work runs as background
helpers in the same sandbox; their ends wake the lead.

Trust boundaries: model output, user files, Slack events, canvas content, MCP metadata and web pages
are data. Keys live in host tools; the sandbox has no credentials and no network by default.
