---
name: brand-onboarding
description: Build the active brand pack in workspace/brand/ from a brand guide, website, files or a Paper file, validate it, and have a person review it.
---

# Build a brand pack

The pack is the agent's only source of brand facts: tokens, logos, fonts, voice and graphic
language. Schema: `src/design_agent/brand/schema.py`; a complete example:
`examples/brands/example-studio/`. Never invent a rule, colour, font or logo the sources do not show:
leave it out and list it as a question for the person.

1. Copy the example pack's layout into `workspace/brand/` (Git-ignored) and replace its content.
2. **Sources, best first:** the brand's own guide (PDF), its design files (Paper: read tokens,
   palette and type nodes with `get_tokens`, `get_computed_styles`, `get_jsx`; never write to the
   brand file), the live website's CSS, then existing marketing files.
3. `tokens.json`: palette with roles (ground, text, accent), font stacks for display, text and mono,
   radii, stroke, spacing, and the copy rules the guide states. Check every text/ground pair you list
   for WCAG contrast; mark accents that fail on light grounds as non-text.
4. `logos/`: SVG where the brand provides it; every variant the guide allows (mark, lockup,
   reversed). Do not redraw or trace a logo; ask for files.
5. `fonts.toml`: for each family, an open font in `fonts/` or a licensed file the person supplies in
   `private-fonts/` (Git-ignored; it reaches the sandbox as deployment files or a mount). Never
   commit licensed fonts. If a licensed face is unavailable, name the closest open fallback and say
   so in `graphic-language.md`.
6. `voice.md` and `graphic-language.md`: short, concrete, sourced ("headlines in sentence case",
   "one accent per frame"), no generic advice.
7. `uv run design-agent brand validate`, then `uv run design-agent brand css` regenerates
   `tokens.css`. Render a test card with `uv run design-agent demo` against the new brand
   (`DESIGN_AGENT_BRAND_PATH=workspace/brand`) and look at it with the person.
8. Hand the person the open questions; the pack is done when they have reviewed it.
