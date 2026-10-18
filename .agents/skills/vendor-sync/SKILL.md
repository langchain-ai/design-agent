---
name: vendor-sync
description: Move the pinned HyperFrames version and its vendored skills forward, verify them, and update everything that depends on the pin.
---

# Update HyperFrames

Vendored skills under `skills/` are never edited; they are replaced from upstream at a commit and
checked against `skills-lock.json` in CI.

1. Pick the release: the latest stable HyperFrames tag (never a prerelease) and its commit. Read its
   changelog for CLI changes (flags, renamed or deprecated commands such as `validate` → `check`).
2. Bump `UPSTREAM_COMMIT` and `UPSTREAM_RELEASE` in `src/design_agent/skills_lock.py`, the
   `hyperframes` version in `sandbox/render/package.json`, then `npm install --package-lock-only`
   in `sandbox/render/` and `uv run python scripts/sync_sandbox_recipe.py` (embeds the lock in
   `setup.sh`).
3. `uv run design-agent skills sync-vendor`; review `git diff skills/ skills-lock.json`. Check the
   exclusion list still catches third-party media, unlicensed fonts and bundled libraries.
   Upstream skills carry their own `.gitignore`s: `git add -f` any locked file they hide
   (`test_git_tracks_every_locked_file` names them).
4. New or renamed vendored skills: add a one-line summary to `config/vendored-skills.toml`, and the
   folder to `extend-exclude` in `pyproject.toml` (tests fail until both match the lock).
5. Rebuild and prove: `uv run design-agent sandbox build`, `sandbox test`,
   `uv run pytest -q -m render`, `uv run design-agent demo`.
6. Record the new pin and anything that changed in `docs/sources/` and `CHANGELOG.md`. MDA
   deployments need `sandbox publish` again, since the recipe changed.
