# Migration From Primary-Forcing Scripts

Older display helper scripts often fixed hybrid-display problems by forcing a laptop panel such as `eDP-1` to primary:

```bash
xrandr --output eDP-1 --primary
```

That approach solves a different problem and can create new ones. Cinnamon panel placement is stored by numeric monitor index, while XRandR primary status is a display preference. Changing primary to move a panel couples two unrelated behaviors.

`cinnamon-panel-anchor` instead stores the intended panel connector and edge, then restores only Cinnamon's panel setting when monitor indexes drift. It never changes primary.

## Safe Disable Strategy

If you have an older script or autostart entry that changes primary:

1. Find it without assuming a fixed path. Check your session startup applications, `~/.config/autostart/`, shell profile files, and any local helper directories you maintain.
2. Disable the startup entry first rather than deleting it.
3. Log out and back in, then confirm display primary behavior is still acceptable.
4. Run `cinnamon-panel-anchor capture` with panels where you want them.
5. Run `cinnamon-panel-anchor install-autostart`.
6. Archive the old script only after the new workflow survives login, wake, and dock or hotplug changes.

Do not remove unrelated display scripts unless you know what they control.
