<div align="center">
  <p>
    <a href="https://www.langchain.com/">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langchain-company-dark.svg">
        <img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langchain-company-light.svg" alt="LangChain" width="152">
      </picture>
    </a>
  </p>
  <h1>Design Agent</h1>
  <p><strong>An open-source AI design agent.</strong> Ask for a launch card, a deck, a diagram, a chart or a<br>short film in Slack, and get finished, on-brand files back in the thread.</p>
  <p>
    <a href="https://github.com/langchain-ai/design-agent/actions/workflows/ci.yml"><img src="https://github.com/langchain-ai/design-agent/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License: Apache 2.0"></a>
    <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&amp;logoColor=white" alt="Python 3.11+">
    <a href="https://github.com/langchain-ai/deepagents"><img src="https://img.shields.io/badge/built%20on-Deep%20Agents-1C3C3C?logo=langchain&amp;logoColor=white" alt="Built on Deep Agents"></a>
    <a href="https://docs.langchain.com/langsmith/python/managed-deep-agents-overview"><img src="https://img.shields.io/badge/deploy-Managed%20Deep%20Agents-006DDD" alt="Deploy with Managed Deep Agents"></a>
    <a href="https://hyperframes.heygen.com"><img src="https://img.shields.io/badge/video-HyperFrames-111111" alt="Video with HyperFrames"></a>
    <a href="https://paper.design"><img src="https://img.shields.io/badge/canvas-Paper-111111" alt="Canvas in Paper"></a>
  </p>
  <p>
    <a href="#get-started">Get started</a> ·
    <a href="#how-it-works">How it works</a> ·
    <a href="#deploy-it">Deploy</a> ·
    <a href="OPERATIONS.md">Docs</a> ·
    <a href="CONTRIBUTING.md">Contributing</a>
  </p>
</div>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/hero-dark.png">
  <img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/hero-light.png" alt="Design Agent at work: a Slack request for a launch film, and the agent's computer with its project folders, a HyperFrames render in the terminal, the film preview, layers and references" width="100%">
</picture>

We built Design Agent as our own design teammate at LangChain, and now it's open source.

You ask for something the way you'd ask a designer: "a LinkedIn card for Thursday's launch", "turn
this into a 2x2", "a 30-second teaser for the new release". It picks a concept, lays the piece out,
builds it on its own computer, checks it against your brand, and posts the files back to you. For
anything big, like a film, it shows you a storyboard first, and you approve it before it renders.

> [!NOTE]
> Everything you see here uses LangChain's brand, because that's the brand we run it with. Out of
> the box Design Agent uses a neutral sample brand, and it switches to yours as soon as you add
> your brand pack (see [Make it yours](#make-it-yours)).

## See it work

<p align="center">
  <a href="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/design-agent-explainer.mp4"><img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/explainer-preview.gif" alt="From the explainer film: the lead hands out a film in three acts, and a flock of helper parrots works the act folders in parallel" width="100%"></a>
  <br><sub><b><a href="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/design-agent-explainer.mp4">▶ Watch the 2-minute film</a></b>: one Slack request, from the sandbox to skills, Paper, the helpers, HyperFrames, the checks and the sound.</sub>
</p>

## What you can ask for

- **Social cards and ad sets:** one layout, recomposed for every size you need. It doesn't just
  scale it down.
- **Slides, one-pagers and decks**, as PNG or PDF.
- **Diagrams and charts**, drawn from your data. The numbers are computed in code, never
  eyeballed.
- **Thumbnails, banners and GIFs.**
- **Short films and motion graphics:** storyboard first, then a
  [HyperFrames](https://hyperframes.heygen.com) render, with voice, music and sound if you add
  the keys.
- **Work on a shared canvas:** layouts and storyboards land in [Paper](https://paper.design) as
  editable layers, if you connect it.

## Get started

You need **Python 3.11+**, [uv](https://docs.astral.sh/uv/) and **Docker**. Setup takes about five
minutes, plus a few more the first time Docker builds the agent's computer.

**1. Install it and watch the demo.** The demo needs no API keys. It runs the real agent,
sandbox and checks with a scripted model, and renders a launch card in three sizes plus a
4-second teaser into `workspace/out/demo/`.

```bash
git clone https://github.com/langchain-ai/design-agent.git
cd design-agent
uv sync
uv run design-agent sandbox build
uv run design-agent demo
```

**2. Connect a model.** Put `ANTHROPIC_API_KEY=…` in `.env` yourself, so the key stays out of your
shell history. Then:

```bash
uv run design-agent config set DESIGN_AGENT_MODEL=anthropic:claude-opus-5-5
uv run design-agent test model
```

**3. Ask for something.**

```bash
uv run design-agent ask "A LinkedIn card announcing our design review service, 1200x627."
```

Your files land in `workspace/out/<thread>/`, and the last line tells you roughly what the run
cost. Add `--thread <id>` to keep a conversation going.

**Rather have your coding agent set it up?** Open Claude Code, Codex or Cursor in the repo and
paste this:

> Read AGENTS.md and .agents/skills/design-agent-onboarding/SKILL.md. Help me connect a model, add
> my brand, connect Paper, and choose a deployment path.

## Make it yours

Your brand lives in `workspace/brand/`. It holds your colours and the role each one plays, fonts,
logos, voice and graphic language, and it's the only place the agent learns your brand from. The
[brand-onboarding skill](.agents/skills/brand-onboarding/SKILL.md) builds it from your brand guide,
your website, a folder of files or a Paper file. Then `brand validate` and `fonts verify` check it.

| Want | Add | More |
| --- | --- | --- |
| Your brand | `workspace/brand/` (until then, the sample brand) | [brand-onboarding skill](.agents/skills/brand-onboarding/SKILL.md) |
| Generated images | `OPENAI_API_KEY` | [Models](docs/models.md) |
| Voice, music, sound effects | `ELEVENLABS_API_KEY` | [sound skill](skills/sound/SKILL.md) |
| The Paper canvas | `PAPER_MODE=local` with Paper Desktop, or `bridged` for a deployed agent | [Paper](docs/partners/paper.md) |
| Web search, your docs, other tools | MCP servers in `config/mcp.toml` | [Customization](docs/customization.md) |

Licensed fonts go in `private-fonts/`. Git ignores that folder, so they never get committed.

## Deploy it

Same agent, two ways to run it.

| | Managed Deep Agents (recommended) | Self-hosted |
| --- | --- | --- |
| Get going | `uv run design-agent sandbox publish`, then `uv run design-agent deploy` | `docker compose -f deploy/self-host/compose.yaml up -d --build` |
| Who runs it | LangSmith | you: the API, Postgres and a Docker host |
| Slack | a managed app you authorize | your own Slack app |
| Guide | [Deploy with MDA](docs/deploy-mda.md) | [Self-hosting](docs/self-hosting.md) |

`deploy` shows you exactly which settings it will ship and asks before it deploys anything. Want
to try a change without touching your team's agent? Run `deploy --name design-agent-test` and you
get a separate copy. Managed Deep Agents needs a LangSmith organization with MDA access, and
[hosting is paid](https://www.langchain.com/pricing). Model, image and audio usage is billed by your
providers either way.

## How it works

Under the hood there are three parts we built for design work, sitting on top of parts we didn't
have to build:

- **The lead and its helpers.** The lead reads your brief, picks the concept and writes a plan.
  It does small jobs itself. Big ones it hands to helpers that work in parallel: three directions
  to compare, or one act each of a film.
- **The context.** Skills, a design wiki, your brand pack and memory. It loads only what the job
  in front of it needs.
- **The designer's computer.** A sandbox with real tools: Chrome, FFmpeg, HyperFrames, D2 and
  your fonts. Everything is built and checked there.
- **Off the shelf:** the [Deep Agents](https://github.com/langchain-ai/deepagents) harness,
  [Managed Deep Agents](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview)
  (or your own infrastructure) and a frontier model.

The split that matters: **the model makes the creative calls, and code does everything that has
to be exactly right.** That means rendering, measuring, checking, delivering files and holding
your keys.

<details>
<summary><b>The architecture, in more detail</b></summary>

One assembly (`src/design_agent/assembly.py`) builds the model, tools, middleware and helpers.
Runtime profiles plug it into Managed Deep Agents, the CLI, the self-hosted API, Slack and
schedules.

**The lead and its helpers**

- Each thread gets one lead. It writes a plan in the thread's project folder and decides what to
  delegate.
- Helpers run in the background on the same sandbox and files. Each one has a heartbeat, a
  durable transcript, and a lead that can steer it.
- Nobody sits and waits. Render watchers and check-ins wake the lead when work lands, fails or
  stalls: one-time schedules on Managed Deep Agents, an in-process waker everywhere else.
- Before anything ships, the lead and helpers look at their own renders with a vision `look`
  tool.

**The context**

- The always-on prompt is small, about 4k tokens. Workflows live in [skills](skills/)
  (`skills/<name>/SKILL.md`) and load on demand. On Managed Deep Agents they mount read-only from
  Context Hub.
- Brand facts come only from the brand pack. It's staged into the sandbox with its fonts and logos.
- Context stays bounded:
  - Long tool results go to files, with a short summary in the conversation.
  - Provider tool search loads MCP tools only when they're needed.
  - Helpers can clear old tool results server-side.
  - Prompt caching keeps the lead's prefix warm for an hour.

**The designer's computer**

- One recipe, [`sandbox/setup.sh`](sandbox/), pins Chrome Headless Shell, FFmpeg, HyperFrames,
  sharp, ECharts, D2 and open fonts by version and sha256. It ends with a probe that renders a
  page, a film and a diagram. The same recipe builds:
  - the local and self-hosted Docker image;
  - the LangSmith snapshot that Managed Deep Agents clones for each thread;
  - the CI image.
- Every thread gets its own sandbox, and its files persist in `/workspace/projects/` between turns.
  - Locally, it's a container with no network, dropped capabilities, an unprivileged user, and
    limits capped to your machine.
  - On Managed Deep Agents, it's a LangSmith sandbox (16 GiB disk, 8 vCPU) with default-deny
    egress.
- Before a run, a manifest with a sha256 checklist stages skills, the checks, your brand pack and
  its fonts into `/workspace`, read-only.

**The checks** ([`workspace/tools/`](workspace/tools/README.md)) run before anything is delivered:

| Check | What it catches |
| --- | --- |
| `brand-lint` | off-brand colours, fonts, radii and copy |
| `video-gate`, `hyperframes check` | non-deterministic animation, layout, motion and contrast problems |
| `artifact-contract` | a wrong size or duration, a missing file, a blank first frame |
| font check | a brand font that silently fell back, web fonts included |
| chart and graph contracts | truncated baselines, mixed units, shares that don't add up to 100%, a diagram that changed shape |

**Keys stay outside.** The sandbox never holds a credential. Host tools run next to the agent,
keep the keys, and drop their results in as files:

- image generation;
- voice, music and sound effects;
- transcription;
- an asset fetcher with SSRF protection;
- Paper, scoped by a policy;
- your MCP servers;
- delivery: to Slack, to `workspace/out/` locally, or attached to the LangSmith trace for API
  runs.

**Where each piece runs**

| | Managed Deep Agents | Self-hosted |
| --- | --- | --- |
| Agent | `agent.py` (`define_deep_agent`), `identity.py`, `tools/mcp.py` | the same assembly in a FastAPI app |
| Threads and memory | LangSmith | Postgres checkpointer and store |
| Sandboxes | LangSmith sandboxes from your snapshot (`sandbox/__init__.py`) | containers on your Docker host |
| Slack | managed app (`channels/slack.py`) | your Bolt app, Socket Mode or signed HTTP |
| Wake-ups and housekeeping | runtime schedules; `schedules/housekeeping.py` every 15 minutes | in-process waker and maintenance loop |
| Skills | synced to Context Hub; binary files ship as deployment files | read from the checkout |

**Models.** Claude Opus 5.5 is the default, and any tool-calling model with vision works. A
registry keyed by exact model id sets effort, tool search and output limits per role: lead,
helper, look, tool selector and learning. The optional [LangSmith Gateway](docs/models.md) uses
each provider's native route, so caching and context editing keep working. Every call is metered
per job, helper and role, and LangSmith traces every run.

Go deeper: [Architecture](docs/architecture/README.md) ·
[Orchestration](docs/architecture/orchestration.md) ·
[Context and failures](docs/architecture/context-and-failures.md).

</details>

## FAQ

**Can it use my brand instead of LangChain's?** Yes, that's the whole point of the brand pack. Add
yours and every output follows it.

**Which models does it work with?** Claude Opus 5.5 by default. OpenAI and Google models work
through the same registry, and so do any OpenAI-compatible endpoint and the LangSmith Gateway.
See [Models](docs/models.md).

**Do I need Slack?** No. You can use the terminal (`design-agent ask`), the self-hosted HTTP API,
or a Managed Deep Agents deployment's API.

**Can the agent reach the internet or my keys?** No. The sandbox has no network by default and
never holds a credential. Host tools do the fetching, generating and delivering for it.

**How do I know the output is any good?** Every file goes through the checks before you get it,
and the [eval set](docs/evals.md) grades outputs, copy and behaviour without a model judging taste.

## Built with

<p>
  <a href="https://github.com/langchain-ai/deepagents"><picture><source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/deep-agents-dark.svg"><img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/deep-agents-light.svg" alt="Deep Agents" height="28"></picture></a>
  &nbsp;&nbsp;
  <a href="https://docs.langchain.com/langsmith/python/managed-deep-agents-overview"><picture><source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langsmith-deployment-dark.svg"><img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langsmith-deployment-light.svg" alt="LangSmith Deployment" height="28"></picture></a>
  &nbsp;&nbsp;
  <a href="https://hyperframes.heygen.com"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/heygen-com/hyperframes/main/docs/logo/dark.svg"><img src="https://raw.githubusercontent.com/heygen-com/hyperframes/main/docs/logo/light.svg" alt="HyperFrames" height="28"></picture></a>
  &nbsp;&nbsp;
  <a href="https://paper.design"><img src="https://avatars.githubusercontent.com/u/178361271?s=56" alt="Paper" height="28" align="absmiddle"> <b>Paper</b></a>
</p>

Also: [LangSmith](https://smith.langchain.com) ·
[Chrome Headless Shell](https://developer.chrome.com/blog/chrome-headless-shell) ·
[FFmpeg](https://ffmpeg.org) · [D2](https://d2lang.com) · [Apache ECharts](https://echarts.apache.org) ·
[sharp](https://sharp.pixelplumbing.com). Logos belong to their owners. HyperFrames and Paper are
partner projects we build on.

## Build on it

| Want to change or explore | Start here |
| --- | --- |
| Instructions, skills and taste | [instructions.md](instructions.md) · [skills/](skills/) · [Customization](docs/customization.md) |
| Models and cost | [Models](docs/models.md) · [Context and failures](docs/architecture/context-and-failures.md) |
| Background work, wake-ups, pipelines | [Orchestration](docs/architecture/orchestration.md) |
| The sandbox and the checks | [sandbox/](sandbox/) · [workspace/tools/](workspace/tools/README.md) |
| Evals | [Evals](docs/evals.md) |
| Running it day to day | [Operations](OPERATIONS.md) |
| Contributing | [Contributing](CONTRIBUTING.md) · [Agent instructions](AGENTS.md) · [Coding-agent skills](.agents/skills/) |

---

[Apache 2.0](LICENSE) · [Notices](NOTICE.md) · [Changelog](CHANGELOG.md) · [Security](SECURITY.md) · [Code of conduct](CODE_OF_CONDUCT.md)
