# Troubleshooting

## Applet Not Visible

Run:

```bash
uv run cinnamon-panel-anchor install-applet --enable
gsettings get org.cinnamon enabled-applets
```

Confirm the output contains `cinnamon-panel-anchor@cruxexperts.com`. If not, run `enable-applet` again and restart Cinnamon.

## Missing Gio Or PyGObject

Use a Python environment based on `/usr/bin/python3`:

```bash
uv sync --python /usr/bin/python3
```

On Linux Mint, install the distribution package that provides `gi` for Python if it is missing.

## XRandR Map Failures

Run diagnostics:

```bash
uv run cinnamon-panel-anchor diagnose --json
```

If `xrandr --listmonitors` returns no parseable monitors, the backend will avoid writing panel settings.

## Cinnamon Reload

On X11, press `Alt+F2`, enter `r`, and press `Enter`.

## Panel Still Moves

Open the applet and capture the intended layout again. If a connector is disconnected, fallback keeps the panel reachable until the connector returns.
