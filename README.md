<div align="center">
  <p>
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langchain-company-dark.svg">
      <a href="https://www.langchain.com/?utm_source=github&utm_medium=readme&utm_campaign=design-agent"><img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langchain-company-light.svg" alt="LangChain" width="152"></a>
    </picture>
  </p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/header-dark.png">
    <img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/header-light.png" alt="Content Studio: one design brain for your whole company" width="100%">
  </picture>
  <p>
    <picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/license-Apache%202.0-7FC8FF.svg?variant=outline&logo=lu:Scale&mode=dark"><a href="LICENSE"><img src="https://shieldcn.dev/badge/license-Apache%202.0-006DDD.svg?variant=outline&logo=lu:Scale&mode=light" alt="License: Apache 2.0"></a></picture>
    <picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/python-3.11%2B-7FC8FF.svg?variant=outline&logo=python&mode=dark"><a href="https://www.python.org"><img src="https://shieldcn.dev/badge/python-3.11%2B-006DDD.svg?variant=outline&logo=python&mode=light" alt="Python 3.11+"></a></picture>
    <picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/built%20on-Deep%20Agents-7FC8FF.svg?variant=outline&logo=lu:Layers&mode=dark"><a href="https://github.com/langchain-ai/deepagents"><img src="https://shieldcn.dev/badge/built%20on-Deep%20Agents-006DDD.svg?variant=outline&logo=lu:Layers&mode=light" alt="Built on Deep Agents"></a></picture>
    <picture><source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/badge/deploy-Managed%20Deep%20Agents-7FC8FF.svg?variant=outline&logo=lu:Rocket&mode=dark"><a href="https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent"><img src="https://shieldcn.dev/badge/deploy-Managed%20Deep%20Agents-006DDD.svg?variant=outline&logo=lu:Rocket&mode=light" alt="Deploy with Managed Deep Agents"></a></picture>
  </p>
  <p>
    <b><a href="#quickstart">Distribute Content Studio to your team →</a></b> ·
    <a href="#try-it-locally">Try it locally, no keys needed</a> ·
    <a href="https://www.langchain.com/blog/how-we-built-our-design-agent?utm_source=github&utm_medium=readme&utm_campaign=design-agent">How we built it</a> ·
    <a href="docs/README.md">Docs</a>
  </p>
</div>

**Content Studio is the design agent LangChain runs, now open source.** Add your brand and deploy it
to your team's Slack with Managed Deep Agents. Anyone can ask it like they'd ask a designer, attach what they have, and
get finished, on-brand files back, from a resized ad to a launch film.

Since August it has shipped over 3,000 assets for us, posts with its work drew about 4.5M views on
X, and three in four requests come from outside marketing. [How we built it](https://www.langchain.com/blog/how-we-built-our-design-agent?utm_source=github&utm_medium=readme&utm_campaign=design-agent) goes deeper
into each part.

## See it work

We asked Content Studio for its own launch film. It went full Rocky.

LAUNCH_FILM_URL

<p align="center"><sub>From a 1-bit chick to champion in 50 seconds.</sub></p>

## How it works

Content Studio runs on a **media harness**: what a designer has, rebuilt for an agent.
[Deep Agents](https://github.com/langchain-ai/deepagents) supplies the agent loop, planning, files and
subagents.
[Managed Deep Agents](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent)
runs it in production, and this repo adds the design layer on top. The model makes the creative
calls; code renders, checks, delivers files and holds your keys.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/architecture-dark.png">
    <img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/architecture-light.png" alt="Content Studio on Managed Deep Agents: a Slack thread goes to the main agent, which reads skills and the wiki, keeps team and personal memory, uses managed tools and MCP servers with each person's own account, and works in a sandbox per thread with Chromium, ffmpeg, HyperFrames, motion-studio and async subagents in parallel, then posts the film back to the same thread" width="100%">
  </picture>
</p>

<p align="center"><sub>How we run it at LangChain. Your copy starts with the integrations you turn on (<a href="docs/integrations.md">Integrations</a>).</sub></p>

| Layer | Managed Deep Agents gives you | This repo adds |
| --- | --- | --- |
| **Slack**<br>Ask in a thread, get files back there | The Slack app, attachments into the sandbox, files back to the thread | Live progress for each step, a footer with what's running and its cost, notes folded into running work |
| **Designer's computer**<br>A Linux machine per thread | A LangSmith sandbox per thread, cloned from your snapshot, files kept between turns | The recipe: Chrome, FFmpeg, HyperFrames, D2 and your fonts, pinned and tested. Keys stay outside |
| **Designer's brain**<br>Know-how loaded only when needed | Skills synced to Context Hub, mounted read-only, loaded on demand | 35 skills, a router skill that picks one, a design wiki, and your brand pack checked in code |
| **Tools**<br>Works with what your team uses | MCP servers through connections, signed in as each person or one shared account | Presets for Notion, Linear, GitHub, Figma and more; HyperFrames for video; [Paper](https://paper.design) as a shared canvas; image, voice and music tools |
| **Async subagents**<br>Long jobs run, the thread stays open | Subagents, durable runs, and schedules that wake the agent | A chief-of-staff lead with `start_task`, `check_tasks`, `steer_task` and `resume_task`; render watchers; pipelines that enforce review |
| **Memory**<br>Say a rule once | Team memory and per-person memory as files, loaded into every run | Off until you add `memory.py` |
| **Self-improvement**<br>Better with every job | A durable store and a trace for every run | `learn_from_job` files notes against the skills a job used; later jobs rate them, and weak ones are dropped |
| **Shipping it**<br>One command to your team | `mda deploy`, tracing in LangSmith | Evals built from real requests, cost per job, `design-agent doctor` |

### Watch it explain itself

We asked it to explain its own harness as a nature documentary. The same parrot walks through the
computer, the tools and the context behind its work.

EXPLAINER_FILM_URL

<p align="center"><sub>Storyboarded, built and narrated by the agent, in one Slack thread.</sub></p>

<details>
<summary>The prompt that made this film</summary>

The agent made it from this ask and a few rounds of notes:

> Make a short explainer of how you create videos in code, end to end, for our blog post on the
> media harness we built on Deep Agents. Narrate it like a David Attenborough nature documentary,
> starring the pixel parrot from our promo, with your subagents as its flock. Keep it technical
> enough for an engineer, in real terms: skills, wiki, tools, apps. Storyboard it before you build,
> and end on "Built on Managed Deep Agents".

</details>

Read the [architecture](docs/architecture/README.md), or start changing it:
[instructions.md](instructions.md) · [skills/](skills/) · [Customization](docs/customization.md) ·
[Evals](docs/evals.md) · [Operations](OPERATIONS.md) · [Contributing](CONTRIBUTING.md).

## Why it doesn't look like AI

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/same-prompt-dark.png">
    <img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/same-prompt-light.png" alt="The same prompt for a hiring chart to a local coding agent with a brand skill and to Content Studio: a broken logo lockup, a generic font, no axis and an off-brand bar on the left; a clean lockup, the brand typeface, an axis with gridlines and brand-blue bars on the right" width="100%">
  </picture>
</p>

<p align="center"><sub>The same prompt to a local coding agent with a brand skill, and to Content Studio.</sub></p>

- **It looks at its work.** It renders, then looks at the image before it posts anything.
- **Your brand is code.** Layouts only take your tokens: your colours, fonts and spacing.
- **It checks what a machine can count.** Colours, fonts, contrast, sizes and chart math are checked
  in code on every render. Taste stays with your designers.

<p align="center">
  <img src="docs/assets/readme/hero.png" alt="The agent's computer: a Slack request for a launch film, project folders, a HyperFrames render in the terminal, the film preview, layers and references" width="100%">
</p>

## Quickstart

| Building it yourself | Starting here |
| --- | --- |
| Months on a harness, a sandbox, skills and a Slack UX | Fork it, add your brand, deploy with one command |
| Polished work that looks like a hundred others | Work that follows your brand, checked on every render |
| Design requests wait in a queue | Anyone asks in Slack: a graphic in minutes, a long deck overnight |
| Every team fixes the same mistakes | Fix a skill once, and every asset after it follows |

This repository is a [Managed Deep Agents](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent) project, so it deploys to your LangSmith
workspace as it is. You need MDA access and a model key:

```bash
curl -fsSL https://raw.githubusercontent.com/langchain-ai/design-agent/main/install.sh | bash
cd design-agent
uv run design-agent config set LANGSMITH_API_KEY=lsv2_… ANTHROPIC_API_KEY=sk-ant-…
uv run design-agent sandbox publish   # once per workspace: the agent's computer
uv run mda deploy
```

The installer gets [uv](https://docs.astral.sh/uv/) if you don't have it, clones the repository and
installs its dependencies; `git clone` and `uv sync` do the same.

The first deploy sets up the agent's Slack app. Authorize it in your workspace, then mention the
agent in a channel. It's how we run ours at LangChain. Try changes on a separate copy with
`uv run mda deploy --name design-agent-test`; [Deploy with MDA](docs/deploy-mda.md) covers keys,
what ships and checking it works.

**Or ask your coding agent.** Open the repo in Claude Code, Codex or Cursor and say what you want.
[AGENTS.md](AGENTS.md) routes each request to a step-by-step [skill](.agents/skills/):

| Say | It will |
| --- | --- |
| "Deploy it to our Slack." | publish the sandbox, check what ships, and deploy after your yes |
| "Build our brand pack from our website and brand guide." | draft the pack, validate it, and ask you to review it |
| "Teach it to make our weekly newsletter header." | add a skill for it and try it on a real request |
| "Did that change make it better?" | run the evals before and after, and show you the numbers |

## Try it locally

The demo runs the real agent, sandbox and checks with a scripted model and no API keys. It needs
**Docker**, and leaves a launch card in three sizes and a 4-second teaser in `workspace/out/demo/`:

```bash
uv run design-agent sandbox build
uv run design-agent demo
```

With a model key in `.env`, ask for something real. Files land in `workspace/out/<thread>/`, and the
last line tells you what the run cost:

```bash
uv run design-agent ask "A LinkedIn card announcing our design review service, 1200x627."
```

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

**Do I need Slack?** No. Call the deployment's API, open it in LangSmith Studio, or use the
terminal (`design-agent ask`). On Managed Deep Agents, long jobs that work in the background
(films, parallel looks) report back in Slack; over the API, keep to requests that finish in one
turn.

**Is it safe with my keys?** The sandbox never holds a credential and has no network by default.
Host tools do the fetching, generating and delivering, and drop results in as files.

**Which models?** Claude Opus 5.5 by default. OpenAI and Google models, any OpenAI-compatible
endpoint and the LangSmith Gateway work too. See [Models](docs/models.md).

**Can I run it on my own servers?** Yes. It's Apache 2.0, and [Self-hosting](docs/self-hosting.md)
runs the same agent with Docker, an HTTP API and your own Slack app.

**Why two names?** Content Studio is what we call the agent at LangChain, and the name its Slack app
gets unless you set `DESIGN_AGENT_SLACK_NAME`. The repository, package and command are `design-agent`.

**Does it replace a designer?** No. It takes the repetitive requests, so designers spend their time on
the work only they can do, and their judgment lives on in its skills and checks.

**Build your own.** Fork it, add your brand tokens, fonts and skills, and deploy it to your team's
Slack. [Quickstart](#quickstart). If it's useful, a star helps other teams find it.

## Built with

<p>
  <a href="https://github.com/langchain-ai/deepagents"><img src="docs/assets/readme/logos/deep-agents-symbol.svg" alt="" height="24" align="absmiddle"> <b>Deep Agents</b></a>
  &nbsp;&nbsp;
  <a href="https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent"><img src="docs/assets/readme/logos/langsmith-deployment-symbol.svg" alt="" height="24" align="absmiddle"> <b>Managed Deep Agents</b></a>
  &nbsp;&nbsp;
  <a href="https://hyperframes.heygen.com"><img src="https://raw.githubusercontent.com/heygen-com/hyperframes/main/docs/logo/symbol-dark.svg" alt="" height="24" align="absmiddle"> <b>HyperFrames</b></a>
  &nbsp;&nbsp;
  <a href="https://paper.design"><img src="https://avatars.githubusercontent.com/u/178361271?s=48" alt="" height="24" align="absmiddle"> <b>Paper</b></a>
</p>

Also: [LangSmith](https://smith.langchain.com/?utm_source=github&utm_medium=readme&utm_campaign=design-agent) ·
[Chrome Headless Shell](https://developer.chrome.com/blog/chrome-headless-shell) ·
[FFmpeg](https://ffmpeg.org) · [D2](https://d2lang.com) · [Apache ECharts](https://echarts.apache.org) ·
[sharp](https://sharp.pixelplumbing.com). Logos belong to their owners. HyperFrames and Paper are
partner projects we build on.

---

[Apache 2.0](LICENSE) · [Notices](NOTICE.md) · [Changelog](CHANGELOG.md) · [Security](SECURITY.md) · [Code of conduct](CODE_OF_CONDUCT.md)
