# Migration Guide

## From Primary-Forcing Scripts

Older display helper scripts often fixed hybrid-display problems by forcing a laptop panel such as `eDP-1` to primary:

```bash
xrandr --output eDP-1 --primary
```

That approach solves a different problem and can create new ones. Cinnamon panel placement is stored by numeric monitor index, while XRandR primary status is a display preference. Changing primary to move a panel couples two unrelated behaviors.

Cinnamon Panel Anchor stores the intended panel connector and edge, then restores only Cinnamon's panel setting when monitor indexes drift. It never changes primary.

## From The CLI/Autostart Prototype

Earlier versions centered the `watch` command and an XDG autostart entry. The applet-first release makes the Cinnamon applet the default resident UI and controller.

Use this migration path:

1. Remove the old autostart entry:

   ```bash
   cinnamon-panel-anchor uninstall-autostart --json
   ```

2. Install and enable the applet:

   ```bash
   cinnamon-panel-anchor install-applet --enable
   ```

3. Open the applet and choose **Capture Current Layout**.
4. Use the applet dashboard for restore, keep-current, and diagnostics actions.

Do not delete unrelated display scripts unless you know what they control.

In v0.2.1, Cinnamon's enabled applet entry is the normal startup path. Keep the legacy autostart watcher off unless you intentionally need the old background `watch` workflow.
