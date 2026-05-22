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
uv run cinnamon-panel-anchor enable-applet --json
uv run cinnamon-panel-anchor disable-applet --json
uv run cinnamon-panel-anchor uninstall-applet --json
```

The applet starts with Cinnamon because Cinnamon stores it in `enabled-applets`. Do not install the legacy XDG autostart watcher for normal applet startup.

## Optional Legacy Autostart Watcher

The legacy watcher remains available for compatibility and migration testing:

```bash
uv run cinnamon-panel-anchor autostart-status --json
uv run cinnamon-panel-anchor install-autostart --json
uv run cinnamon-panel-anchor uninstall-autostart --json
```

It is off by default. The applet settings switch named **Run legacy autostart watcher at login** creates or removes the desktop autostart file.

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
