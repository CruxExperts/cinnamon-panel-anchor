# Migration Guide

## From Primary-Forcing Scripts

Older display helper scripts often fixed hybrid-display problems by forcing a laptop panel such as `eDP-1` to primary:

```bash
xrandr --output eDP-1 --primary
```

That approach solves a different problem and can create new ones. Cinnamon panel placement is stored by numeric monitor index, while XRandR primary status is a display preference. Changing primary to move a panel couples two unrelated behaviors.

Cinnamon Panel Anchor stores the intended panel connector and edge, then restores only Cinnamon's panel setting when monitor indexes drift. It never changes primary.

## From The CLI Prototype

Earlier versions centered the `watch` command. The applet-first release makes the Cinnamon applet the default resident UI and controller.

Running `install-applet` removes the old pre-release desktop startup file named `cinnamon-panel-anchor.desktop` if that file exists.

Use this migration path:

1. Install and enable the release applet:

   ```bash
   cinnamon-panel-anchor install-applet --enable
   ```

2. Open the applet and choose **Save Current Layout**.
3. Use the applet popup for restore, pending keep-or-restore decisions, and diagnostics actions.

For a source checkout, use:

```bash
uv run cinnamon-panel-anchor install-applet --enable
```

Do not delete unrelated display scripts unless you know what they control.
