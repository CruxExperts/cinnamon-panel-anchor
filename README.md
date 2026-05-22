# cinnamon-panel-anchor

`cinnamon-panel-anchor` keeps Cinnamon panel placement tied to the physical connector and edge you intended, instead of trusting Cinnamon's numeric monitor indexes after dock, wake, or hotplug changes.

It reads Cinnamon's `org.cinnamon panels-enabled` setting, maps monitor indexes through `xrandr --listmonitors`, and restores panel entries when the same connector appears at a different numeric index. It does not change the display primary monitor.

## Install For Development

```bash
uv sync --python /usr/bin/python3
uv run pytest
uv run cinnamon-panel-anchor --help
```

For an editable user install from a checkout:

```bash
uv tool install --python /usr/bin/python3 --editable .
```

The runtime uses system PyGObject/GTK/Gio from the desktop session. No GTK Python wheels are vendored by this project. On Debian, Ubuntu, and Linux Mint systems, install the distribution package that provides `gi` for Python, usually `python3-gi`.

Use `/usr/bin/python3` for the `uv` environment on Mint so the venv Python version matches the system PyGObject extension. The CLI checks the standard system `dist-packages` path only when the ABI matches the running Python.

## Basic Use

Capture the current panel locations as anchors:

```bash
cinnamon-panel-anchor capture
```

Show current monitors, Cinnamon panel entries, saved anchors, and pending decisions:

```bash
cinnamon-panel-anchor status
cinnamon-panel-anchor status --json
```

Preview or restore panel placement:

```bash
cinnamon-panel-anchor apply --dry-run
cinnamon-panel-anchor restore --dry-run
cinnamon-panel-anchor restore
```

Install the login watcher:

```bash
cinnamon-panel-anchor install-autostart
```

Remove it:

```bash
cinnamon-panel-anchor uninstall-autostart
```

Collect read-only diagnostics:

```bash
cinnamon-panel-anchor diagnose --json
```

## Files

- Config: `$XDG_CONFIG_HOME/cinnamon-panel-anchor/config.json`
- State and logs: `$XDG_STATE_HOME/cinnamon-panel-anchor/`
- Autostart entry: `$XDG_CONFIG_HOME/autostart/cinnamon-panel-anchor.desktop`

If `XDG_CONFIG_HOME` is unset, `~/.config` is used. If `XDG_STATE_HOME` is unset, `~/.local/state` is used.
