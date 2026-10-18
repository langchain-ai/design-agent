# Source inventory

> Internal build note. Lists the private and public sources this build extracts from and the
> versions it targets. Delete `docs/prep/` before the first public push; move surviving version
> facts into `CHANGELOG.md` and `docs/architecture/`.

## Sources to extract from

| Source | Revision | Role | Access |
| --- | --- | --- | --- |
| Internal design agent ("Content Studio"), MDA app | `origin/main` @ `f87d644` (2026-10-16) | primary source for harness, middleware, tools, skills, sandbox recipe, tests | private repo `content-studio` on the builder's machine (`~/Desktop/agents/content-studio`). Read committed code with `git show origin/main:<path>`; the local working tree can lag `origin/main` |
| Internal source assets (pre-MDA app) | `origin/main` @ `ccc0eec`; asset snapshot `a94f68e` | `Dockerfile.sandbox` base-image recipe, original renderers and skills | private repo `langchain-media` (`~/Desktop/agents/langchain-media`) |
| MDA SDK example lineage | `managed-deepagents-sdk` `examples/content-studio` @ `18a218a` (MIT) | origin of the internal MDA app; its MIT notice must be preserved for any code that descends from it | private SDK repo (LangChain staff); the published package is public |
| Paid Media Agent (open source) | `4b47399` | the pattern to follow: repository shape, docs, onboarding, two deploy paths, CI, release discipline | public `github.com/langchain-ai/paid-media-agent`; local `~/Desktop/agents/paid-media-agent-open-source` |
| HyperFrames | release `v0.8.169` (2026-10-17); Apache-2.0 | video engine CLI and agent skills | public `github.com/heygen-com/hyperframes`, npm `hyperframes` |
| Paper Desktop MCP | current Desktop release | shared canvas | `paper mcp` stdio CLI or `http://127.0.0.1:29979/mcp` |

The internal agent was the subject of the "How we built our Design Agent" launch post. The public
name is **Design Agent**; "Content Studio" is the internal codename and may appear only in
`NOTICE.md` provenance.

## Baseline health of the source (measured 2026-10-17)

- `origin/main` exported with `git archive`, `uv sync --frozen --all-extras --dev`, then
  `uv run --frozen pytest -q`: **2,441 passed** in 106 s, offline, no `.env`.
- 2,190 tracked files: skills 977, workspace 868, tests 140 (122 Python files, 44,822 lines,
  1,589 test functions before parametrization), tools 57, middleware 39, docs 26, scripts 24,
  harness 18 (6,438 lines, no MDA imports), fonts 10.
- No `Makefile`, `langgraph.json`, Dockerfile, CI workflow or top-level `LICENSE` on `main`. Gates
  are listed in its `AGENTS.md` (`ruff check`, `ruff format --check`, `basedpyright`, `pytest`,
  `scripts/check_deploy_tree.py`).
- The sandbox base snapshot is built outside the repo (from `langchain-media/Dockerfile.sandbox`)
  and carries licensed fonts, the internal brand package, the video-kit and June copies of the
  HyperFrames skills. The open-source build must replace it with a public, reproducible recipe.

## Target framework versions (verify on Slice 0)

| Package | Latest stable on 2026-10-17 | Internal pin | Paid Media pin | Target |
| --- | --- | --- | --- | --- |
| `managed-deepagents` | **0.9.3** (dev: 0.10.0.dev9) | `==0.9.0.dev2` (dev build) | `>=0.6.1,<0.7` | latest stable at build time, `>=0.9.3,<0.10`; never a `.devN` pin in a release |
| `deepagents` | **0.7.28** | `>=0.7.5,<0.8` | `>=0.7.12,<0.8` | `>=0.7.28,<0.8` |
| `langchain`, `langgraph`, `langchain-anthropic`, `langchain-openai`, `langchain-mcp-adapters`, `mcp` | resolve at build | | | current compatible, explicit upper bounds on pre-1.0 packages |
| `hyperframes` (npm) | `0.8.169` | `@latest` at bake | n/a | exact pin in `sandbox/setup.sh`, upgrade through the weekly compatibility job |
| HyperFrames skills | upstream `main` at a pinned commit | June 2026 pull, hash-only lock, 93 local edits | n/a | pinned commit + per-file sha256 in `skills-lock.json`, unmodified |

The internal agent depends on private MDA modules in two places (`middleware/boundary.py` for
background wake-ups through MDA's private ingress and loopback, and `tools/connect.py` for Agent
Auth). The open-source build must use only public APIs from the latest stable release; see SPEC §7.

## Slice 0 compatibility table (verified 2026-10-17)

Installed and resolved by `uv lock` (Python 3.13.15): managed-deepagents 0.9.3, deepagents 0.7.28,
langchain 1.4.6, langchain-core 1.6.12, langgraph 1.2.16, langchain-anthropic 1.7.6,
langchain-openai 1.7.2, langsmith 0.14.11, fastmcp 4.1.0, mcp 2.3.0. Evidence is the installed
package source unless noted; "SDK source" means the private SDK repository at tag `v0.9.3`, read
for behavior only.

| Contract | Verified behavior | Design consequence |
| --- | --- | --- |
| `define_deep_agent` | keyword surface of `create_deep_agent` minus `backend`, `store`, `checkpointer`, `system_prompt`, `state_schema`; accepts `SubAgent`, `CompiledSubAgent`, `AsyncSubAgent`; `instructions`/`mcp`/`sandbox`/`skills`/`memory` selections only from a factory entry; `metadata` lands on the root run | `agent.py` stays a static definition; the static prompt is `instructions.md` |
| `define_sandbox` | typed `idle_ttl_seconds`, `default_timeout`, `snapshot_name`/`snapshot_id`/`docker_image` (mutually exclusive), `registry`, `proxy_config`; unmodeled keys pass through as LangSmith create options; `scope` must be `thread` | `vcpus`, `mem_bytes`, `fs_capacity_bytes` pass through (they are `langsmith.sandbox` create parameters) |
| `docker_image` bake | SDK source `deploy/bake.rs`: a snapshot built from a Docker image gets a fixed 1 GiB filesystem; `setup.sh` runs in a builder sandbox, then the snapshot is captured | the recipe unpacks to 1,351 MB (below), so `docker_image` cannot hold it: publish a snapshot with `--fs-gib` and declare it as the bake base |
| Declaring a sandbox | MDA sets `permissions=[]` when a sandbox backend is present (deepagents drops route prefixes at `execute` time); skills mount read-only at `/skills/` from Context Hub | read-only enforcement relies on the mount; the stager copies runnable skill files into `/workspace/skills/` |
| Slack file delivery | `SlackFileTransferMiddleware` (installed by MDA on the parent when the Slack channel is declared) adds `upload_files(paths)` (1-10 files, 200 MiB each, `/workspace` paths only) and stages inbound files to `/workspace/attachments/`; hidden when the run has no Slack destination | the agent delivers with `upload_files`; a declared subagent does not inherit it (deliver from the lead) |
| `connections.get` | public; `connections.get("mda/slack-bot-token", {"type": "agent"})` is how MDA's own file transfer reads the bot token | live progress and footer use the Slack Web API with that reserved connection |
| `runtime.channel` | `RuntimeChannel(name, provider, event, raw_event, post)`; `post` sends one extra message; no update or streaming | progress messages need the Web API (`chat.update`/streaming) |
| `runtime.schedules.create` | needs an active run's runtime (reads `assistant_id`, `thread_id`); `at` is rounded **up** to the next whole minute and must be ≥ 1 minute ahead (`_schedule_time.py`); agent-owned same-thread schedules need a channel binding, otherwise use `new_thread=True` or a user owner; per-owner cap 20 via `MDA_MAX_AGENT_SCHEDULES` / `MDA_MAX_USER_SCHEDULES`; a one-time schedule expires 5 minutes after `at` | MDA wake latency is 60-120 s plus scheduler lag by construction: the coalescing inbox batches into one schedule; documented, upstream ask recorded (SPEC §24 #1) |
| `define_mcp` | HTTP/SSE only (stdio rejected); `prefix_tool_name_with_server_name` removed in 0.9: native names are `{server}_{tool}` | the internal `{server}__{tool}` rules would silently miss; scope and deferral rules use `{server}_` |
| MCP client (local, self-host) | `langchain.mcp.MCPAdapter` (FastMCP 4, MCP 2) is the client MDA uses and names tools `{server}_{tool}`; `langchain-mcp-adapters` 0.3.2 still requires `mcp<2` | use `langchain[mcp]` everywhere; do not add `langchain-mcp-adapters` |
| `define_memory` | `define_memory(agent=MemoryLayer(), user=MemoryLayer())`; `scope=` raises in 0.9.3 | `memory.py.example` uses layers |
| Async subagents | deepagents `AsyncSubAgent` specs (`graph_id`) pass through MDA unwrapped; MDA builds one graph per deployment and does not run them against the lead's sandbox | `HelperRunner` runs helpers in-process (SPEC §7.2); re-check at Slice 10 |
| Model profiles | langchain-anthropic 1.7.6 ships a `claude-opus-5-5` profile (1M input, 128k output, effort low/medium/high/xhigh/max); `ChatAnthropic(model="claude-opus-5-5").max_tokens == 128000`. deepagents 0.7.28 harness profiles stop at Opus 4.7 | the local Opus 5.5 fallback profile is no longer needed (SPEC §6.2 retire rule); the registry keeps effort and output-floor rules |
| Gateway | `init_chat_model("langsmith:provider/model")` builds `ChatOpenAI` (Responses API) against the LangSmith Gateway with `LANGSMITH_GATEWAY_API_KEY` or `LANGSMITH_API_KEY` | `langsmith:` is the optional preset; never required |
| `mda` CLI | `init`, `build`, `dev`, `chat`, `deploy` (`--no-wait`, `--push-to`, `--deployment-type`), `connections`, `channels`, `logs`, `delete`, `evals`; hidden `prepare` for GitHub-sourced builds; `mda dev` also bakes the recipe and needs `LANGSMITH_API_KEY`; `[tool.mda] python-version` is read from `pyproject.toml` | `design-agent deploy` wraps `mda deploy .` |

HyperFrames 0.8.169 (npm `hyperframes`, Apache-2.0, `gitHead` = upstream release commit
`7735338b49ed6e11c227b0710da3bd35c3366b9c`, Node ≥ 22):

| Item | Verified |
| --- | --- |
| Commands | `init --example <name> --non-interactive [--resolution]`, `lint [--json]`, `check` (lint + runtime + layout + motion + WCAG contrast; replaces the deprecated `validate` and `inspect`), `snapshot --at t[,t…] [--frames N] [-o dir]`, `render [-o file] [--fps] [--quality draft|looks|delivery|standard|high] [--format mp4|webm|mov|gif|png-sequence|hls] [--variables-file] [--batch] [--workers] [--strict]`, `transcribe`, `tts` (local Kokoro), `remove-background`, `browser ensure|path|clear`, `doctor`, `telemetry enable|disable|status`, `skills check|update` |
| Not present | `--resolution square-4k` on render (the internal flag); use `--resolution` presets listed by `render --help` |
| Browser | pins Chrome Headless Shell 152.0.7977.30 for linux64; honors `HYPERFRAMES_BROWSER_PATH`; Chrome for Testing has no linux-arm64 build, and the amd64 build crashes (SIGTRAP) under emulation on Apple Silicon unless run single-process |
| Environment | `HYPERFRAMES_NO_TELEMETRY`/`DO_NOT_TRACK`, `HYPERFRAMES_NO_UPDATE_CHECK`, `HYPERFRAMES_NO_AUTO_INSTALL`, `HYPERFRAMES_SKIP_SKILLS`; the sandbox wrapper sets all of them |
| `init` default | loads GSAP from a CDN; sandbox egress is default-deny, so compositions use the GSAP the image installs (copied into the project) |
| Upstream skills at the release commit | 21 skills, 944 files, ~16.5 MB; `music-to-video` and `talking-head-recut` each vendor `gsap.min.js`; `embedded-captions` ships 57 woff2 fonts (license to confirm, partner question) |

Paper: Paper Desktop installs `~/.paper/bin/paper`; `paper mcp` is the stdio relay; the legacy HTTP
endpoint `http://127.0.0.1:29979/mcp` answers MCP POSTs while a file is open (a bare GET returns
404). The live tool list on 2026-10-17 has 37 tools, including `list_resources` (formerly
`list_files`), `get_font_family_info`, `export`, `export_combined_pdf`, `write_html`,
`delete_nodes`, `set_tokens`, `create_tokens`, `rename_resource`, `arrange_pages`, `update_pages`.

### Sandbox recipe measurement

`sandbox/setup.sh` on `node:22.23.3-bookworm-slim@sha256:c3de60bf…` (Debian 12.15, Node 22.23.3):
ffmpeg 5.1.9 (Debian), D2 0.9.0, HyperFrames 0.8.169 with sharp 0.35.5, ECharts 6.1.0, GSAP 3.15.0
and puppeteer-core 25.14.0 from a lockfile, nine OFL fonts from `google/fonts@47d54ca`.

| Build | Result |
| --- | --- |
| linux/arm64, native (Apple Silicon, Docker Desktop 29.7) | 88 s; probe passes (fonts resolve, Chrome screenshot, `hyperframes lint`, 2 s 1920×1080 draft render with ffprobe duration and size, D2 SVG, sharp and ECharts load); Chromium 149.0.7827 (Playwright build 1228) |
| linux/amd64, emulated on the same host | installs in 197 s; probe fails: Chrome Headless Shell 152 SIGTRAPs under emulation. Verified in CI on native amd64 instead |
| Unpacked root filesystem | 1,351 MB (`/usr` 723 MB, Chrome 334 MB, render `node_modules` 214 MB) |

Decision: MDA's `docker_image` bake (1 GiB) cannot hold the computer, before any render scratch
space. Ship `design-agent sandbox publish --fs-gib 16` (LangSmith SDK `create_snapshot`, as the Paid
Media Agent does) and declare the published snapshot as the bake base; MDA then re-runs
`setup.sh`, which only re-probes because the recipe stamp matches. A live MDA bake is not run in
this build: it needs a LangSmith workspace and the person's approval.

### Conflicts recorded

- SPEC §21.1 asks for the LangChain OSS mark in the README; AGENTS.md (higher precedence) bans
  LangChain brand assets. The README ships without it; marketing and legal decide at release.
- SPEC §8.1 lists `hyperframes validate`; 0.8.169 deprecates it and `inspect` in favor of `check`.
- SPEC §13 and the internal code assume `{server}__{tool}`; MDA 0.9.3 produces `{server}_{tool}`.
- SPEC §6.2 asks the registry to supply an Opus 5.5 profile; langchain-anthropic 1.7.6 already does.

## Identifiers that must never reach the public repository

Scrub by category, enforced by a CI ban-list scan (SPEC §18.4):

- LangChain brand: logos, icons, marks, palettes, the token files, construction specs, graphic
  language images, brand-book Paper file ids, the internal brand package.
- People: employee names, Slack user ids, emails, voice profiles, the people roster, approver
  principals.
- Workspace and infrastructure: Slack channel and team ids, LangSmith workspace, project and
  deployment ids and URLs, snapshot names, Paper team id, Okta and sign-in hand-off details,
  managed-tool server ids, Buffer channel ids, S3/R2 hosts.
- Internal agents and programs: peer agents and their bot ids, the quote-post copilot, the launch
  ledger and its guards, internal campaigns, product glossaries, analytics workspaces.
- Licensed or third-party media: TWK Lausanne and Aeonik Mono fonts, the remocn-ported component
  library, the 70 reference-film contact sheets and teardowns, frames of LangChain films, the
  Cyberpunk fan-kit asset and terms, vendored GSAP files, third-party brand imagery in examples,
  externally sourced image galleries without a clear license.
- History: `MIGRATION.md`, `migration-notes/`, internal runbooks, trace skills, research notes.
