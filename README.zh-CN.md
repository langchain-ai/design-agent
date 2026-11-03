<div align="center">
  <p>
    <a href="https://www.langchain.com/?utm_source=github&utm_medium=readme&utm_campaign=design-agent#gh-light-mode-only"><img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langchain-company-light.svg" alt="LangChain" width="152"></a><a href="https://www.langchain.com/?utm_source=github&utm_medium=readme&utm_campaign=design-agent#gh-dark-mode-only"><img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/logos/langchain-company-dark.svg" alt="LangChain" width="152"></a>
  </p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/header-dark.png">
    <img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/header-light.png" alt="Content Studio: one design brain for your whole company" width="100%">
  </picture>
  <p>
    <a href="LICENSE#gh-light-mode-only"><img src="https://shieldcn.dev/badge/license-Apache%202.0-006DDD.svg?variant=outline&logo=lu:Scale&mode=light" alt="License: Apache 2.0"></a><a href="LICENSE#gh-dark-mode-only"><img src="https://shieldcn.dev/badge/license-Apache%202.0-7FC8FF.svg?variant=outline&logo=lu:Scale&mode=dark" alt="License: Apache 2.0"></a>
    <a href="https://www.python.org#gh-light-mode-only"><img src="https://shieldcn.dev/badge/python-3.11%2B-006DDD.svg?variant=outline&logo=python&mode=light" alt="Python 3.11+"></a><a href="https://www.python.org#gh-dark-mode-only"><img src="https://shieldcn.dev/badge/python-3.11%2B-7FC8FF.svg?variant=outline&logo=python&mode=dark" alt="Python 3.11+"></a>
    <a href="https://github.com/langchain-ai/deepagents#gh-light-mode-only"><img src="https://shieldcn.dev/badge/built%20on-Deep%20Agents-006DDD.svg?variant=outline&logo=lu:Layers&mode=light" alt="Built on Deep Agents"></a><a href="https://github.com/langchain-ai/deepagents#gh-dark-mode-only"><img src="https://shieldcn.dev/badge/built%20on-Deep%20Agents-7FC8FF.svg?variant=outline&logo=lu:Layers&mode=dark" alt="Built on Deep Agents"></a>
    <a href="https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent#gh-light-mode-only"><img src="https://shieldcn.dev/badge/deploy-Managed%20Deep%20Agents-006DDD.svg?variant=outline&logo=lu:Rocket&mode=light" alt="Deploy with Managed Deep Agents"></a><a href="https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent#gh-dark-mode-only"><img src="https://shieldcn.dev/badge/deploy-Managed%20Deep%20Agents-7FC8FF.svg?variant=outline&logo=lu:Rocket&mode=dark" alt="Deploy with Managed Deep Agents"></a>
  </p>
  <p>
    <b><a href="#quickstart">把 Content Studio 带给你的团队 →</a></b> ·
    <a href="#try-it-locally">本地试用，无需任何密钥</a> ·
    <a href="https://www.langchain.com/blog/design-agent?utm_source=github&utm_medium=readme&utm_campaign=design-agent">我们是如何构建它的</a> ·
    <a href="docs/README.md">文档</a>
  </p>
  <p>
    <a href="README.md">English</a> · <b>简体中文</b> · <a href="README.ja.md">日本語</a>
    <br><sub>本译文以英文 README 为准，可能未及时同步。</sub>
  </p>
</div>

**Content Studio 是 LangChain 内部使用的设计智能体，现已开源。** 加入你的品牌，用 Managed Deep Agents
把它部署到团队的 Slack。任何人都可以像找设计师一样向它提需求、附上手头的素材，然后拿回完成且符合品牌规范的文件，
从调整尺寸的广告到发布宣传片都能做。

自 8 月以来，它已为我们交付了 3,000 多个设计资产，带有它作品的帖子在 X 上获得了约 450 万次浏览，
四分之三的需求来自市场部以外的团队。[我们是如何构建它的](https://www.langchain.com/blog/design-agent?utm_source=github&utm_medium=readme&utm_campaign=design-agent)一文对每个部分都有更深入的介绍。

## 看看效果

我们请 Content Studio 为自己做一部发布宣传片，它直接拍成了《洛奇》风格。

https://github.com/user-attachments/assets/ee5b98e0-7ec6-4b24-ada6-1f27087947a3

<p align="center"><sub>47 秒，从 1 比特小鸡成长为冠军。</sub></p>

## 工作原理

Content Studio 是一个 [Deep Agents](https://github.com/langchain-ai/deepagents) 智能体，部署在
[Managed Deep Agents](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent) 上。
Managed Deep Agents 负责基础设施：Slack、沙箱、记忆、定时任务和追踪。本仓库是构建在其上的设计智能体。
模型负责创意决策，代码负责渲染、检查和交付。

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/architecture-dark.png">
    <img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/architecture-light.png" alt="Content Studio on Managed Deep Agents: a Slack thread goes to the main agent, which reads skills and the wiki, keeps team and personal memory, uses managed tools and MCP servers with each person's own account, and works in a sandbox per thread with Chromium, ffmpeg, HyperFrames, motion-studio and async subagents in parallel, then posts the film back to the same thread" width="100%">
  </picture>
</p>

<p align="center"><sub>这是我们在 LangChain 的运行方式。你的副本从你启用的集成开始（<a href="docs/integrations.md">集成</a>）。</sub></p>

- **Slack。** 在线程中 @ 它，附上需求说明和任意文件。MDA 的 Slack 应用会把消息和附件交给智能体，
  完成的文件会发回同一个线程。工作期间，一条消息会逐步更新，页脚显示正在运行的任务和目前的花费，
  你在中途补充的任何内容都会传达给正在进行的工作。
- **每个线程一台电脑。** 每个线程都有自己的 LangSmith 沙箱：一台装有 Chrome、FFmpeg、
  [HyperFrames](https://hyperframes.heygen.com)、D2 和你的字体的 Linux 机器，由一份固定版本的配置
  （[`sandbox/setup.sh`](sandbox/)）构建。它产出的一切都是项目文件夹中的代码（幻灯片是 HTML，影片是动画时间轴），
  所以修改只需编辑后重新渲染，而不必从头再来。API 密钥永远不会进入沙箱。
- **技能和设计知识库。** 常驻提示词很短。每个需求它都会先读取一个路由技能，从 35 个
  [技能](skills/)中挑选合适的工作流，从调整尺寸的广告到发布宣传片。知识库存放设计功底（字体、颜色、
  版式、图表），品牌包存放品牌事实。技能只在任务需要时加载，由 MDA 通过 Context Hub 提供。
- **你的工具。** 视频用 HyperFrames 制作，它把影片当作时间轴上的网页来处理。
  [Paper](https://paper.design) 是一个共享画布，你可以直接在上面编辑分镜或版式。图像、语音和音乐模型
  作为沙箱外的工具运行，Notion、Linear、GitHub 和 Figma 等 MCP 服务器通过 MDA 接入，每个人都以自己的身份登录。
- **异步子智能体。** 遇到大型任务时，主智能体会制定计划、拆分工作，并在同一个沙箱和文件上于后台启动
  子智能体。某个子智能体完成、失败或卡住时，MDA 会唤醒主智能体，因此它从不空等，可以继续和你对话。
  影片按分镜、动态分镜（animatic）、正式制作的顺序推进，代码会确保每个部分在合成前都通过审核。
- **记忆。** 一条规则只需说一次（“LinkedIn 上永远不要用橙色”），它会在当轮保存下来。MDA 为它提供两层文件：
  所有人共享的团队记忆，以及每个人自己的个人记忆，每层的索引都会在每次运行时加载。
- **越用越好。** 每完成一个任务，`learn_from_job` 会针对所用的技能记录哪些做法有效。之后的任务会读取并
  评价这些笔记，站不住脚的会被删除。

### 看它自己讲解

我们请它以自然纪录片的形式讲解自己的工作框架（harness），主角是一只像素鹦鹉。它带你走过它的电脑、工具，
以及工作背后的上下文。

https://github.com/user-attachments/assets/65eac8e4-0fac-4a5a-9cca-02e26a0a8baa

<p align="center"><sub>分镜、制作和旁白均由智能体在一个 Slack 线程中完成。</sub></p>

<details>
<summary>生成这部影片的提示词</summary>

智能体根据下面的需求和几轮修改意见完成了它：

> Make a short explainer of how you create videos in code, end to end, for our blog post on the
> media harness we built on Deep Agents. Narrate it like a David Attenborough nature documentary,
> starring the pixel parrot from our promo, with your subagents as its flock. Keep it technical
> enough for an engineer, in real terms: skills, wiki, tools, apps. Storyboard it before you build,
> and end on "Built on Managed Deep Agents".

</details>

阅读[架构说明](docs/architecture/README.md)，或者开始修改它：
[instructions.md](instructions.md) · [skills/](skills/) · [定制](docs/customization.md) ·
[评估](docs/evals.md) · [运维](OPERATIONS.md) · [贡献指南](CONTRIBUTING.md)。

## 为什么它的作品不像 AI 生成的

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/same-prompt-dark.png">
    <img src="https://github.com/langchain-ai/design-agent/raw/main/docs/assets/readme/same-prompt-light.png" alt="The same prompt for a hiring chart to a local coding agent with a brand skill and to Content Studio: a broken logo lockup, a generic font, no axis and an off-brand bar on the left; a clean lockup, the brand typeface, an axis with gridlines and brand-blue bars on the right" width="100%">
  </picture>
</p>

<p align="center"><sub>同一个提示词，分别交给带品牌技能的本地编程智能体和 Content Studio。</sub></p>

- **它会检查自己的作品。** 它先渲染，再查看图像，然后才发布任何内容。
- **你的品牌就是代码。** 版式只使用你的设计令牌（tokens）：你的颜色、字体和间距。
- **能用机器计数的，它都会检查。** 颜色、字体、对比度、尺寸和图表数据在每次渲染时都由代码检查。
  审美判断仍交给你的设计师。

<p align="center">
  <img src="docs/assets/readme/hero.png" alt="The agent's computer: a Slack request for a launch film, project folders, a HyperFrames render in the terminal, the film preview, layers and references" width="100%">
</p>

<a name="quickstart"></a>

## 快速开始

| 自己从零搭建 | 从这里开始 |
| --- | --- |
| 花几个月构建框架、沙箱、技能和 Slack 体验 | Fork 仓库，加入你的品牌，一条命令部署 |
| 作品精致，却和其他上百个看起来一样 | 作品遵循你的品牌，每次渲染都经过检查 |
| 设计需求在队列里排队 | 任何人都能在 Slack 里提需求：几分钟出图，长篇幻灯片一夜完成 |
| 每个团队都在修同样的错误 | 一个技能修一次，之后的每个资产都会遵循 |

本仓库是一个 [Managed Deep Agents](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent) 项目，可以原样部署到你的 LangSmith 工作区。
你需要一个 LangSmith 账号（Managed Deep Agents 目前在 LangSmith Cloud 上公开测试）和一个模型密钥：

```bash
curl -fsSL https://raw.githubusercontent.com/langchain-ai/design-agent/main/install.sh | bash
cd design-agent
uv run design-agent config set LANGSMITH_API_KEY=lsv2_… ANTHROPIC_API_KEY=sk-ant-…
uv run design-agent sandbox publish   # once per workspace, 10-15 min: the agent's computer
uv run mda deploy                     # the agent itself, and its Slack app
```

安装脚本会在你没有 [uv](https://docs.astral.sh/uv/) 时自动安装它，然后克隆仓库并安装依赖；
`git clone` 加 `uv sync` 效果相同。

最后两条命令的作用不同。`sandbox publish` 会构建每个线程工作所用的 Linux 机器，作为快照保存在你的
LangSmith 工作区；此时还没有任何可以对话的东西。`mda deploy` 才会部署智能体，它会为每个线程克隆那台机器。
只有在 `sandbox/setup.sh` 变化时才需要重新发布。

**使用 LangSmith Gateway？** 跳过模型服务商的密钥，运行
`uv run design-agent config set DESIGN_AGENT_MODEL=langsmith:anthropic/claude-opus-5-5`。之后智能体会使用
`LANGSMITH_GATEWAY_API_KEY`，没有则使用 `LANGSMITH_API_KEY`；在没有 `OPENAI_API_KEY` 时，图像生成也会经过网关。
对于其他 OpenAI 兼容的端点，设置 `DESIGN_AGENT_MODEL_BASE_URL` 和 `DESIGN_AGENT_MODEL_API_KEY_ENV`
（[模型](docs/models.md)）。

首次部署会设置智能体的 Slack 应用。在你的工作区授权后，在频道中 @ 它即可。这也是我们在 LangChain 的用法。
可以用 `uv run mda deploy --name design-agent-test` 在单独的副本上试验修改。在开启了 agent 模式的工作区中，
`uv run mda deploy --agent-environment production`（或 `staging`、`development`）会部署到该智能体的对应环境，
每个环境都有各自的追踪记录：在 LangSmith 中打开智能体并选择环境即可。`uv run mda dev` 的追踪会记录到它的 Local 环境。
[用 MDA 部署](docs/deploy-mda.md)介绍了密钥、部署内容以及如何验证部署。

**或者让你的编程智能体来做。** 在 Claude Code、Codex 或 Cursor 中打开仓库，说出你想做什么。
[AGENTS.md](AGENTS.md) 会把每个请求交给一个分步骤的[技能](.agents/skills/)：

| 你说 | 它会 |
| --- | --- |
| “把它部署到我们的 Slack。” | 发布沙箱，检查要部署的内容，在你确认后部署 |
| “根据我们的网站和品牌指南创建品牌包。” | 起草品牌包，验证它，并请你审阅 |
| “教它制作我们的每周通讯头图。” | 为此添加一个技能，并在真实需求上试用 |
| “这次修改让它变好了吗？” | 在修改前后运行评估，并给你看数据 |

<a name="try-it-locally"></a>

## 本地试用

演示会用脚本化的模型、在无需 API 密钥的情况下运行真实的智能体、沙箱和检查。它需要 **Docker**，
并会在 `workspace/out/demo/` 中留下三种尺寸的发布卡片和一段 4 秒的预告片：

```bash
uv run design-agent sandbox build
uv run design-agent demo
```

在 `.env` 中配置模型密钥后，就可以提真实的需求。文件会保存在 `workspace/out/<thread>/`，
最后一行会告诉你这次运行花了多少钱：

```bash
uv run design-agent ask "A LinkedIn card announcing our design review service, 1200x627."
```

## 打造你自己的版本

本仓库有两类技能。[`.agents/skills/`](.agents/skills/) 中的技能给你的编程智能体用，用于设置、加入品牌、
部署和修改本仓库。[`skills/`](skills/) 中的技能是 Content Studio 工作时读取的。[定制](docs/customization.md)
对两者都有介绍。

| 想要 | 添加 | 指南 |
| --- | --- | --- |
| 你的品牌 | `workspace/brand/`（在此之前使用中性的示例品牌），然后重新部署 | [brand-onboarding 技能](.agents/skills/brand-onboarding/SKILL.md) |
| 生成图像 | `OPENAI_API_KEY`、`GOOGLE_API_KEY` 或 LangSmith Gateway | [模型](docs/models.md) |
| 语音、音乐、音效 | `ELEVENLABS_API_KEY` | [sound 技能](skills/sound/SKILL.md) |
| Paper 画布 | 搭配 Paper Desktop 使用 `PAPER_MODE=local`，部署后使用 `bridged` | [Paper](docs/partners/paper.md) |
| 网页搜索、你的文档、其他工具 | `config/mcp.toml` 中的 MCP 服务器 | [定制](docs/customization.md) |

部署好之后，就像找设计师一样在 Slack 里向它提需求：

- “为我们的新功能做一张发布卡片，要 LinkedIn、X 和 Instagram 三种尺寸。”
- “为我们的发布做一部《洛奇》风格的宣传片，配上音乐和音效。”
- “用这个 CSV 做一张每周注册人数的图表。”（附上文件）
- “为这个视频做一张 YouTube 缩略图。”
- “给这段网络研讨会片段加字幕。”（附上片段）

本页所有内容都使用 LangChain 的品牌，因为我们运行的就是它。授权字体放在 `private-fonts/`，Git 会忽略该目录。

## 常见问题

**要花多少钱？** 代码免费（Apache 2.0）。你需要向模型服务商付费：在 LangChain，单个请求的模型花费中位数
约为 50 美分，长影片和长篇幻灯片会更贵。Managed Deep Agents 的[托管是收费的](https://www.langchain.com/pricing?utm_source=github&utm_medium=readme&utm_campaign=design-agent)；它运行智能体、沙箱、Slack 应用和定时任务，
否则这些都需要你自己搭建和运维。

**它会使用我的品牌吗？** 会。加入你的品牌包后，每个文件都会遵循它。
[brand-onboarding 技能](.agents/skills/brand-onboarding/SKILL.md)会和你一起，根据你的品牌指南、网站、文件或
Paper 文件构建品牌包。

**从哪里开始？** 从你的团队每周都会要的那张图开始。让大家在 Slack 里向智能体提需求、审阅作品并要求修改，
然后再教它下一件事。

**一定要用 Slack 吗？** 不用。你可以调用部署的 API、在 LangSmith Studio 中打开它，或者使用终端
（`design-agent ask`）。在 Managed Deep Agents 上，在后台运行的长任务（影片、并行的多个方案）会在 Slack 中汇报；
通过 API 使用时，请只提能在一轮内完成的需求。

**我的密钥安全吗？** 沙箱从不保存任何凭证，默认也没有网络访问。获取、生成和交付都由宿主机上的工具完成，
结果以文件形式放入沙箱。

**支持哪些模型？** 默认是 Claude Opus 5.5。OpenAI 和 Google 的模型、任何 OpenAI 兼容端点以及
LangSmith Gateway 也都可以使用。参见[模型](docs/models.md)。

**能在自己的服务器上运行吗？** 可以。它采用 Apache 2.0 协议，[自托管](docs/self-hosting.md)可以用 Docker、
HTTP API 和你自己的 Slack 应用运行同一个智能体。

**为什么有两个名字？** Content Studio 是我们在 LangChain 对这个智能体的称呼，也是它的 Slack 应用的默认名称
（除非你设置了 `DESIGN_AGENT_SLACK_NAME`）。仓库、软件包和命令的名字是 `design-agent`。

**它会取代设计师吗？** 不会。它承担重复性的需求，让设计师把时间花在只有他们才能做的工作上，而他们的判断
会体现在它的技能和检查中。

**打造你自己的。** Fork 它，加入你的品牌令牌、字体和技能，然后部署到你团队的 Slack。
[快速开始](#quickstart)。如果觉得有用，点个 star 可以帮助其他团队发现它。

## 构建于

<p>
  <a href="https://github.com/langchain-ai/deepagents"><img src="docs/assets/readme/logos/deep-agents-symbol.svg" alt="" height="24" align="absmiddle"> <b>Deep Agents</b></a>
  &nbsp;&nbsp;
  <a href="https://docs.langchain.com/langsmith/python/managed-deep-agents-overview?utm_source=github&utm_medium=readme&utm_campaign=design-agent"><img src="docs/assets/readme/logos/langsmith-deployment-symbol.svg" alt="" height="24" align="absmiddle"> <b>Managed Deep Agents</b></a>
  &nbsp;&nbsp;
  <a href="https://hyperframes.heygen.com"><img src="https://raw.githubusercontent.com/heygen-com/hyperframes/main/docs/logo/symbol-dark.svg" alt="" height="24" align="absmiddle"> <b>HyperFrames</b></a>
  &nbsp;&nbsp;
  <a href="https://paper.design"><img src="https://avatars.githubusercontent.com/u/178361271?s=48" alt="" height="24" align="absmiddle"> <b>Paper</b></a>
</p>

另外：[LangSmith](https://smith.langchain.com/?utm_source=github&utm_medium=readme&utm_campaign=design-agent) ·
[Chrome Headless Shell](https://developer.chrome.com/blog/chrome-headless-shell) ·
[FFmpeg](https://ffmpeg.org) · [D2](https://d2lang.com) · [Apache ECharts](https://echarts.apache.org) ·
[sharp](https://sharp.pixelplumbing.com)。徽标归其各自所有者所有。HyperFrames 和 Paper 是我们所依托的合作伙伴项目。

---

[Apache 2.0](LICENSE) · [声明](NOTICE.md) · [更新日志](CHANGELOG.md) · [安全](SECURITY.md) · [行为准则](CODE_OF_CONDUCT.md)
