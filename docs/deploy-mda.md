# Deploy with Managed Deep Agents

Managed Deep Agents (MDA) runs the agent, its sandbox computers, its Slack app and its schedules in
your LangSmith workspace. One command deploys it.

## What you need

- A LangSmith organization with MDA access and an API key with deployment permission
  (`LANGSMITH_API_KEY`; region via `LANGSMITH_ENDPOINT`). [Hosting is paid](https://www.langchain.com/pricing).
- A model key for your configured model ([Models](models.md)).
- Docker, to build and test the sandbox recipe locally first.

## 1. Publish the computer once

Each thread gets its own sandbox cloned from a snapshot of the recipe in `sandbox/setup.sh`
(Chrome, ffmpeg, HyperFrames, D2, sharp, ECharts, fonts). The computer is about 1.3 GiB, more than
the 1 GiB filesystem MDA gives a sandbox baked from a Docker image, so publish it as a snapshot with
room for renders:

```bash
uv run design-agent sandbox build && uv run design-agent sandbox test    # local proof
uv run design-agent sandbox publish --fs-gib 16
```

`publish` builds the snapshot in your workspace (sandbox time is billed), runs the recipe's probe
in it, and rewrites `sandbox/__init__.py` to declare it. Publish again whenever the recipe changes;
the snapshot name follows the recipe's hash. Sizes and egress for MDA sandboxes are the constants in
`sandbox/__init__.py` (MDA reads that file statically). Egress is default-deny: the agent's host
tools fetch and generate, the sandbox only renders.

## 2. Check what ships

```bash
uv run design-agent deploy --build-only
```

`mda deploy` would archive the whole project directory, Git-ignored files included, and send every
key in `.env` as a deployment secret. So `design-agent deploy` never deploys the working tree: it
runs a preflight (brand pack, workspace manifest, vendored skills, the sandbox declaration, the
model key, MCP declarations), stages only what the agent needs into `.mda/deploy-src/` with an `.env`
holding only the keys the agent reads, and compiles that. It prints which secrets ship and which
stay home (Slack tokens for self-hosting, `DATABASE_URL`, your LangSmith key). Inspect
`.mda/deploy-src/` before going further.

What ships: code, `instructions.md`, `skills/`, `workspace/tools/`, `config/`, the sample brand and
your `workspace/brand/`, open fonts and your `private-fonts/` (licensed fonts reach the sandbox as
deployment files, never through Git), the sandbox recipe and the MDA declarations
(`agent.py`, `identity.py`, `channels/`, `schedules/`, `sandbox/`, `tools/mcp.py`). MDA syncs
`skills/` to Context Hub, which takes only UTF-8 text, so the few binary skill files (a vendored
preset's fonts) move to `skill-binaries/` and reach `/workspace/skills/` through the stager.

To try a change without touching the deployment people use, deploy under another name:
`uv run design-agent deploy --name design-agent-test`.

## 3. Deploy

```bash
uv run design-agent deploy
```

It asks before deploying, then runs `mda deploy` on the staged project. On the first deploy MDA
provisions the Slack app; authorize it in your Slack workspace when prompted. Channels require
`identity.py` (LangSmith API-key authentication by default; see MDA's identity docs for per-person
identities).

## 4. Verify

In Slack, mention the agent with a quick ask ("a square card announcing …"), then a short
storyboarded teaser. You should see live progress in the thread, the files attached at the end,
and, for the teaser, a check-in while it renders. `uv run mda logs` tails the deployment.

## How it behaves on MDA

In Slack the agent streams its steps into one message per turn, ends replies with a short footer
(agents running, time, estimated cost; a trace link with `DESIGN_AGENT_TRACE_HOST`), and takes
follow-ups while a job runs ([surfaces](architecture/surfaces.md)).

- **Background work.** Helpers run inside the deployment process; the lead is woken with a
  one-time schedule on its own thread, which lands 60–120 s after the event (MDA rounds a
  schedule to the next minute). See [orchestration](architecture/orchestration.md).
- **Restarts.** A redeploy stops running helpers. Each thread with background work keeps a
  sentinel schedule 15 minutes ahead that the running process keeps pushing back; after a restart
  it fires, and the agent tells the thread what stopped and offers to resume it from its saved
  transcript.
- **Quiet check-ins.** MDA posts every scheduled run's reply, so a check-in with nothing new posts
  one status line ("Still working: act 2 (12 min).") rather than nothing.
- **Housekeeping.** `schedules/housekeeping.py` runs every 15 minutes, sweeps what a restart killed
  and tidies expired schedules, with no model call.
- **MCP servers** come from `config/mcp.toml` through `tools/mcp.py`. A server that needs
  credentials names an agent-owned workspace connection (`connection = "slug"`); header values are
  never compiled into the deployment.
- **Studio.** `uv run mda dev .mda/deploy-src` runs the staged project locally in LangSmith Studio.

## Upstream asks

- A public "start a run on this thread now" API, to wake the lead in seconds instead of 60–120 s.
- A way for a scheduled run to end without posting.
- Async subagents that share the lead's sandbox, to replace the in-process helper runner.
