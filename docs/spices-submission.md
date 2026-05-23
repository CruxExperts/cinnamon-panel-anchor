# Cinnamon Spices Submission

## UUID

The public UUID is:

```text
cinnamon-panel-anchor@cruxexperts.com
```

The directory name, `metadata.json`, installer, tests, docs, and export layout must match this value.

## Export Layout

Run:

```bash
uv run cinnamon-panel-anchor export-spice dist
```

Expected layout:

```text
dist/cinnamon-panel-anchor@cruxexperts.com/
  info.json
  README.md
  files/cinnamon-panel-anchor@cruxexperts.com/
    applet.js
    metadata.json
    settings-schema.json
    stylesheet.css
```

## Screenshot Requirement

Do not submit generated mockups as final Spices screenshots. Add `screenshot.png` only after capturing the running applet on Linux Mint Cinnamon/X11.

## Validation Checklist

- `uv run python tools/version_sync.py --check` passes.
- `uv run python tools/validate.py` passes.
- `uv run pytest` passes.
- JSON files validate.
- README image links resolve to committed files.
- UUID is consistent across code, docs, metadata, and export layout.
- Version is synchronized to `0.2.1` from `VERSION`.
- Startup text describes Cinnamon enabled applet state as the normal startup path.
- **Quit for Session** and **Disable Applet** are documented as temporary versus persistent actions.
- Source does not mutate the XRandR primary monitor.
- Real Cinnamon screenshot exists for submission.
