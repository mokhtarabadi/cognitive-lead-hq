# Slice: prompt-composer

## Duties

Static browser tool for composing and previewing system-prompt builds from fragment sources. Deploy artifact served via GitHub Pages.

## Files

- `index.html` — Self-contained composer UI (fragment loading, ordering, preview, export).

## Key Risks & Invariants

- Single-file invariant: no build step; keep everything in `index.html`.
- Must track `prompts/manifest.txt` order and `prompts/README.md` authoring workflow.
- Deploy workflow (`.github/workflows/deploy-prompt-composer.yml`) serves this directory; path moves break Pages.
