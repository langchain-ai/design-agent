---
name: design-agent-onboarding
description: Install and configure Design Agent, add a brand, connect Paper, choose MDA or self-hosting, and diagnose setup without exposing credentials.
---

# Set up Design Agent

Work through these with the person, in order. Never print a key or token; report missing settings
by name. Do not deploy, connect accounts or publish anything until the person asks.

1. **Install and prove the computer.** `uv sync`, then `uv run design-agent sandbox build` (Docker)
   and `uv run design-agent demo`: a scripted run renders a launch card in three sizes and a 4-second
   teaser with no keys. If it fails, `uv run design-agent doctor` says what is missing.
2. **Model.** `uv run design-agent config set DESIGN_AGENT_MODEL=provider:model` and the provider's
   key (`ANTHROPIC_API_KEY=…`, typed by the person, or set in `.env` by hand). Defaults and other
   roles: `docs/models.md`. Re-run `doctor`.
3. **Media keys (optional).** `OPENAI_API_KEY` (image generation), `ELEVENLABS_API_KEY` (voice,
   music, sound effects), `GROQ_API_KEY` (fast transcription). Each tool says plainly when its key
   is missing.
4. **Brand.** Follow the `brand-onboarding` skill to build `workspace/brand/` from what the person
   has (a brand guide, a website, files, or a Paper file). Until then the sample brand is used.
5. **Paper (optional).** `PAPER_MODE=local` when Paper Desktop runs on this machine; `bridged` for a
   deployed agent (see `docs/partners/paper.md`). `off` is fine: boards render in the sandbox.
6. **Try it.** `uv run design-agent ask "Make a LinkedIn card announcing …"`. Finals land in
   `workspace/out/<thread>/`; `--thread <id>` continues a conversation.
7. **Choose where it runs.** Explain `docs/deploy-mda.md` (managed: runtime, sandbox, Slack,
   schedules; one command) and `docs/self-hosting.md` (Docker Compose with Postgres, your Slack app,
   your machine). For MDA: `uv run design-agent sandbox publish` once, then
   `uv run design-agent deploy --build-only` to inspect exactly what ships, then `deploy` when the
   person says so. For self-hosting: `config generate DESIGN_AGENT_API_TOKENS POSTGRES_PASSWORD`,
   then `docker compose -f deploy/self-host/compose.yaml up --build`.
8. **Verify the deployment** with a real message in Slack (or `POST /threads/{id}/messages`): a
   quick still, then a short storyboarded teaser. A local preflight does not prove a deployment.
