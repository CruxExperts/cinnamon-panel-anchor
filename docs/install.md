# Install Guide

## Requirements

- Linux Mint Cinnamon on X11.
- `uv` for Python workflow.
- System PyGObject/Gio available to `/usr/bin/python3`.
- XRandR command-line tools.

## Development Setup

```bash
uv sync --python /usr/bin/python3
uv run pytest
uv run cinnamon-panel-anchor --help
```

## Install And Enable The Applet

```bash
uv run cinnamon-panel-anchor install-applet --enable
```

The applet is installed to:

```text
~/.local/share/cinnamon/applets/cinnamon-panel-anchor@cruxexperts.com/
```

The install command also writes `cinnamon-panel-anchor-backend` into that directory. The applet uses this launcher first, so a source checkout installed with `uv run` does not depend on Cinnamon inheriting your shell `PATH`.

Enable and disable commands are also available:

```bash
uv run cinnamon-panel-anchor enable-applet
uv run cinnamon-panel-anchor disable-applet
uv run cinnamon-panel-anchor uninstall-applet
```

Restart Cinnamon if the applet list does not refresh:

```bash
Alt+F2
r
Enter
```

## Validate Backend Commands

```bash
uv run cinnamon-panel-anchor status --json
uv run cinnamon-panel-anchor diagnose --json
uv run cinnamon-panel-anchor restore --json --dry-run
```

## Export Spices Layout

```bash
uv run cinnamon-panel-anchor export-spice dist
```

The export contains metadata and files, but no final `screenshot.png` until a real Cinnamon screenshot is captured.
