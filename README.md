<div align="center">
  <p>
    <a href="https://www.langchain.com/?utm_source=github&utm_medium=readme&utm_campaign=design-agent">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langchain-company-dark.svg">
        <img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langchain-company-light.svg" alt="LangChain" width="152">
      </picture>
    </a>
  </p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/header-dark.png">
    <img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/header-light.png" alt="Design Agent: one design brain for your whole company" width="100%">
  </picture>
  <p>
    <a href="LICENSE"><picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/license-Apache%202.0-7FC8FF.svg?variant=outline&logo=lu:Scale&mode=dark"><img src="https://shieldcn.dev/badge/license-Apache%202.0-006DDD.svg?variant=outline&logo=lu:Scale&mode=light" alt="License: Apache 2.0"></picture></a>
    <a href="https://www.python.org"><picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/python-3.11%2B-7FC8FF.svg?variant=outline&logo=python&mode=dark"><img src="https://shieldcn.dev/badge/python-3.11%2B-006DDD.svg?variant=outline&logo=python&mode=light" alt="Python 3.11+"></picture></a>
    <a href="https://github.com/langchain-ai/deepagents"><picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/built%20on-Deep%20Agents-7FC8FF.svg?variant=outline&logo=lu:Layers&mode=dark"><img src="https://shieldcn.dev/badge/built%20on-Deep%20Agents-006DDD.svg?variant=outline&logo=lu:Layers&mode=light" alt="Built on Deep Agents"></picture></a>
    <a href="https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent"><picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/deploy-Managed%20Deep%20Agents-7FC8FF.svg?variant=outline&logo=lu:Rocket&mode=dark"><img src="https://shieldcn.dev/badge/deploy-Managed%20Deep%20Agents-006DDD.svg?variant=outline&logo=lu:Rocket&mode=light" alt="Deploy with Managed Deep Agents"></picture></a>
  </p>
  <p>
    <b><a href="#deploy-it">Put it in your team's Slack →</a></b> ·
    <a href="#get-started">Try the demo, no keys needed</a> ·
    <a href="docs/README.md">Docs</a>
  </p>
</div>

**The design agent LangChain runs, open source.** Add your brand and deploy it to your team's Slack
with Managed Deep Agents. Anyone can ask it like they'd ask a designer, attach what they have, and
get finished, on-brand files back, from a resized ad to a launch film.

Since August it has shipped over 3,000 assets for us, posts with its work drew about 4.5M views on
X, and three in four requests come from outside marketing.

## See it work

https://github.com/user-attachments/assets/0664d09d-2ab2-41fd-b2ba-f91c96121e20

<p align="center"><sub>One Slack request for a launch film: the plan, the storyboard, helpers rendering in parallel, the checks and the final cut.</sub></p>

| Building it yourself | Starting here |
| --- | --- |
| Months on a harness, a sandbox, skills and a Slack UX | Fork it, add your brand, deploy with one command |
| Polished work that looks like a hundred others | Work that follows your brand, checked on every render |
| Design requests wait in a queue | Anyone asks in Slack: a graphic in minutes, a long deck overnight |
| Every team fixes the same mistakes | Fix a skill once, and every asset after it follows |

## What's already built

- **Your designers' judgment:** 35 skills and a design wiki for stills, decks, charts, diagrams,
  storyboards, motion, sound and thumbnails, and your brand as one pack of colours, fonts, logos
  and voice, checked in code on every render.
- **A designer's computer for every thread,** with Chrome, FFmpeg,
  [HyperFrames](https://hyperframes.heygen.com), D2 and your fonts, plus a shared
  [Paper](https://paper.design) canvas for storyboards and layouts. Keys stay outside it.
- **Slack that holds up on long jobs:** a lead that plans and gives an ETA, takes notes mid-job,
  hands long work to helpers (subagents) running in parallel, and asks before anything goes
  public.
- **Everything to run it:** one-command deploy to Managed Deep Agents or self-hosting with Docker,
  evals built from real requests, and every run traced in LangSmith.

## Get started

Open the repo in Claude Code, Codex or Cursor and ask for what you want. [AGENTS.md](AGENTS.md)
routes each request to a step-by-step [skill](.agents/skills/):

| Say | It will |
| --- | --- |
| "Set up Design Agent and run the demo." | install it, build its computer, and render a demo with no API keys |
| "Build our brand pack from our website and brand guide." | draft the pack, validate it, and ask you to review it |
| "Deploy it to our Slack." | publish the sandbox, show you what ships, and deploy after your yes |
| "Teach it to make our weekly newsletter header." | add a skill for it and try it on a real request |
| "Did that change make it better?" | run the evals before and after, and show you the numbers |

**Or set it up by hand.** You need **Python 3.11+**, [uv](https://docs.astral.sh/uv/) and **Docker**. The demo
runs the real agent, sandbox and checks with a scripted model, and leaves a launch card in three
sizes and a 4-second teaser in `workspace/out/demo/`:

```bash
git clone https://github.com/langchain-ai/design-agent.git && cd design-agent
uv sync
uv run design-agent sandbox build
uv run design-agent demo
```

Then put `ANTHROPIC_API_KEY=…` in `.env` and ask for something real. Files land in
`workspace/out/<thread>/`, and the last line tells you what the run cost:

```bash
uv run design-agent ask "A LinkedIn card announcing our design review service, 1200x627."
```

## Why it doesn't look like AI

- **It looks at its work.** It renders, then looks at the image before it posts anything.
- **Your brand is code.** Layouts only take your tokens: your colours, fonts and spacing.
- **It checks what a machine can count.** Colours, fonts, contrast, sizes and chart math are checked
  in code on every render. Taste stays with your designers.
- **Big pieces start cheap.** A film starts as a plan and a storyboard, and nothing renders until you
  say yes.

<p align="center">
  <img src="docs/assets/readme/hero.png" alt="The agent's computer: a Slack request for a launch film, project folders, a HyperFrames render in the terminal, the film preview, layers and references" width="100%">
</p>

## Make it yours

| Want | Add | Guide |
| --- | --- | --- |
| Your brand | `workspace/brand/` (until then, a neutral sample brand) | [brand-onboarding skill](.agents/skills/brand-onboarding/SKILL.md) |
| Generated images | `OPENAI_API_KEY` | [Models](docs/models.md) |
| Voice, music, sound effects | `ELEVENLABS_API_KEY` | [sound skill](skills/sound/SKILL.md) |
| The Paper canvas | `PAPER_MODE=local` with Paper Desktop, or `bridged` when deployed | [Paper](docs/partners/paper.md) |
| Web search, your docs, other tools | MCP servers in `config/mcp.toml` | [Customization](docs/customization.md) |

Everything on this page uses LangChain's brand, because that's the one we run. Licensed fonts go in
`private-fonts/`, which Git ignores.

## Deploy it

Open the repo in Claude Code, Codex or Cursor and say "Deploy it to our Slack." The
[deploy skill](.agents/skills/design-agent-deploy/SKILL.md) publishes the sandbox, shows you exactly
what will ship and deploys after your yes. It's how we run ours at LangChain.

| | Managed Deep Agents (recommended) | Self-hosted |
| --- | --- | --- |
| Start | `uv run design-agent sandbox publish`, then `uv run design-agent deploy` | `docker compose -f deploy/self-host/compose.yaml up -d --build` |
| Who runs it | LangSmith: the agent, a sandbox per thread, the Slack app and the schedules, with secrets and tracing | you: the API, Postgres, a Docker host for the sandboxes and your own Slack app |
| Guide | [Deploy with MDA](docs/deploy-mda.md) | [Self-hosting](docs/self-hosting.md) |

Try it before your team depends on it: the demo needs no keys, and `deploy --name design-agent-test`
gives you a separate copy to try changes on. It's Apache 2.0, so you can move to self-hosting at any
time.

## Questions

**What does it cost?** The code is free (Apache 2.0). You pay your model provider: at LangChain the
median request costs about 50 cents in model spend, and long films and decks cost more. Managed Deep
Agents [hosting is paid](https://www.langchain.com/pricing?utm_source=github&utm_medium=readme&utm_campaign=design-agent); it runs the agent, the sandboxes,
the Slack app and the schedules that you'd otherwise build and operate yourself.

**Will it use my brand?** Yes. Add your brand pack and every file follows it. The
[brand-onboarding skill](.agents/skills/brand-onboarding/SKILL.md) builds the pack with you from
your brand guide, website, files or a Paper file.

**Where do I start?** With the graphic your team asks for every week. Let people brief the agent,
review the work and ask for changes in Slack, then teach it the next thing.

**Do I need Slack?** No. Use the terminal (`design-agent ask`), the self-hosted HTTP API, or a
deployment's API.

**Is it safe with my keys?** The sandbox never holds a credential and has no network by default.
Host tools do the fetching, generating and delivering, and drop results in as files.

**Which models?** Claude Opus 5.5 by default. OpenAI and Google models, any OpenAI-compatible
endpoint and the LangSmith Gateway work too. See [Models](docs/models.md).

**Does it replace a designer?** No. It takes the repetitive requests, so designers spend their time on
the work only they can do, and their judgment lives on in its skills and checks.

## How it works

The model makes the creative calls. Code does everything that has to be exactly right: rendering,
measuring, checking, delivering files and holding your keys. It's built on the
[Deep Agents](https://github.com/langchain-ai/deepagents) harness and runs on
[Managed Deep Agents](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent) or
your own infrastructure.

Read the [architecture](docs/architecture/README.md), or start changing it:
[instructions.md](instructions.md) · [skills/](skills/) · [Customization](docs/customization.md) ·
[Evals](docs/evals.md) · [Operations](OPERATIONS.md) · [Contributing](CONTRIBUTING.md).

**Build your own.** Fork it, add your brand tokens, fonts and skills, and deploy it to your team's
Slack. [Get started](#get-started). If it's useful, a star helps other teams find it.

## Built with

<p>
  <a href="https://github.com/langchain-ai/deepagents"><picture><source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/deep-agents-dark.svg"><img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/deep-agents-light.svg" alt="Deep Agents" height="28"></picture></a>
  &nbsp;&nbsp;
  <a href="https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent"><picture><source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langsmith-deployment-dark.svg"><img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langsmith-deployment-light.svg" alt="LangSmith Deployment" height="28"></picture></a>
  &nbsp;&nbsp;
  <a href="https://hyperframes.heygen.com"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/heygen-com/hyperframes/main/docs/logo/dark.svg"><img src="https://raw.githubusercontent.com/heygen-com/hyperframes/main/docs/logo/light.svg" alt="HyperFrames" height="28"></picture></a>
  &nbsp;&nbsp;
  <a href="https://paper.design"><img src="https://avatars.githubusercontent.com/u/178361271?s=56" alt="Paper" height="28" align="absmiddle"> <b>Paper</b></a>
</p>

Also: [LangSmith](https://smith.langchain.com/?utm_source=github&utm_medium=readme&utm_campaign=design-agent) ·
[Chrome Headless Shell](https://developer.chrome.com/blog/chrome-headless-shell) ·
[FFmpeg](https://ffmpeg.org) · [D2](https://d2lang.com) · [Apache ECharts](https://echarts.apache.org) ·
[sharp](https://sharp.pixelplumbing.com). Logos belong to their owners. HyperFrames and Paper are
partner projects we build on.

---

[Apache 2.0](LICENSE) · [Notices](NOTICE.md) · [Changelog](CHANGELOG.md) · [Security](SECURITY.md) · [Code of conduct](CODE_OF_CONDUCT.md)
