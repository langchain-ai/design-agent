# Typography

Type roles and families come from the brand pack (`fontStacks` in `tokens.json`, the
`--brand-font-*` properties in `tokens.css`, `fonts.toml` for the files). This page is how to use
them. Each rule names its evidence or is marked as a default to weigh.

## Roles

| Role | Use for | Notes |
| --- | --- | --- |
| Display | Headlines, the one big number, the end card line | The pack's display stack and weight. One display size per frame |
| Text | Everything else a person reads: labels, body, captions the ask supplied | The pack's text stack |
| Mono | Literal values only: code, commands, file names, data values, ids | Letter-spacing as the pack says (`creativeTypography.monoLetterSpacing`); never for prose or labels, never forced to capitals |

A frame uses two families at most (display and text), plus mono where something is literally code
or data. Default to weigh; the pack can say otherwise.

## Sizes at the delivered size

Type is sized for the smallest view the piece gets, not for the canvas you author on.

- **Text a person must read is legible at the smallest view.** A 1080 px wide social image is often
  seen about 360-400 px wide on a phone, so text set at 36 px on the canvas is about 12-13 px on the
  screen. Measure on the render, downscaled to the view's width (`review-thumb.mjs`, then `look`).
  Default to weigh.
- **Thumbnails** are judged at the smallest rail (about 215 px wide on desktop); `thumbnails` has the
  small-size gates.
- **Video overlay text** is checked by `video-score`: a body set below its legible floor for video
  is a finding (`hierarchy.illegible`), and one size for everything is another (`hierarchy.flat`).
- **Charts** must clear 12 px at the delivered size; `data-viz` fails a chart that does not.
- **Contrast scales with size.** WCAG 2.1 asks 4.5:1 for normal text and 3:1 for large text, defined as
  at least 18 pt or 14 pt bold (SC 1.4.3, <https://www.w3.org/TR/WCAG21/#contrast-minimum>). Thin
  display weights read smaller than their point size; give them the normal-text ratio.

## Measure and leading

- **Line length for reading.** Aim for an average of 45-90 characters per line, spaces included
  (Butterick, Practical Typography, <https://practicaltypography.com/line-length.html>). On graphics,
  lines are much shorter: a headline is a phrase, not a paragraph.
- **Leading.** Headlines are set tight (around 1.0-1.15 of the size) because they are read as one
  shape; body text opens up (around 1.3-1.5). Default to weigh; the pack's graphic language may fix it.
- **No `<br>` for layout in compositions that reflow**: wrap by width so every size recomposes
  (HyperFrames also asks for no `<br>` in body text, `hyperframes-core`).

## Casing and punctuation

- **Casing comes from the pack** (`copy.casingRules`, `voice.md`). Never force it with CSS
  `text-transform`; author the text in its final case. `brand-lint` checks it.
- **Headlines carry no trailing full stop** unless the pack says otherwise; real multi-sentence body
  copy keeps its punctuation. Default to weigh.
- **No decorative separators.** Middle dots, bullets and pipes between words are ornament; use space,
  a line break or real punctuation. Dots that mean something stay: decimals, versions, URLs, code.
  (`brand-lint` rejects the decorative characters and marker classes the pack lists.)
- **Proper nouns and product names are exact**, including their own casing.
- **Numbers are figures with units** ("3 hours", "40%") unless the pack's voice says otherwise.

## Finish

- **No one-word last lines** (widows) in body copy or multi-line headlines: rewrap or rebalance.
  Default to weigh.
- **No type effects**: no stroke, outline, shadow or glow on text, no justified text. Default to weigh;
  most packs make it a rule.
- **Align icons by their ink, not their box**: a glyph's optical centre is rarely its box centre.
  Default to weigh.
- **Measure, don't estimate.** Fit text by measuring it after fonts load, never by counting characters:
  "Ill" and "WWW" are not the same width.
- **The font must actually paint.** A browser silently falls back when a face is missing; render with
  `--brand-fonts` or `--require-font` so a missing face fails (`html2png.mjs`, `html2pdf.mjs`).

## Type on screen over time (motion)

How long text must hold is set by reading speed, not by the music.

- A published ceiling for subtitles is 20 characters per second for adult viewers and 17 for
  children, at most 42 characters per line (Netflix English Timed Text Style Guide,
  <https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide>).
  So a line of N characters a viewer must read needs at least N ÷ 20 seconds on screen once it has
  settled (a 40-character line, 2 s), plus a beat; a typed command or a dense label needs more.
- A word or line counts as readable only once it has settled: at its final size and position, not
  moving fast. Time the hold from the end of its entrance (`motion-direction`).
