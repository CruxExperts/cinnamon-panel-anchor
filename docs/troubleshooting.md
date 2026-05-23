# Troubleshooting

## Applet Not Visible

Run:

```bash
cinnamon-panel-anchor install-applet --enable
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

## Applet Comes Back After Hiding

**Quit for Session** is temporary. Cinnamon will load the applet again next session because the UUID remains in `enabled-applets`.

Use **Disable Applet** or:

```bash
cinnamon-panel-anchor disable-applet --json
```

when you want the persistent Cinnamon enabled-applet entry removed.

## Inspect Local Logs

The latest 1000 diagnostic records are stored in:

```text
~/.local/state/cinnamon-panel-anchor/debug.jsonl
```

For a source checkout, prefix backend commands with `uv run`.
