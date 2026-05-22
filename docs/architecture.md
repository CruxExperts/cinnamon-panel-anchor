# Architecture

## Cinnamon Panel Setting

Cinnamon stores enabled panel placement in the `org.cinnamon panels-enabled` string-vector setting. Each entry has the shape:

```text
panel_id:monitor_index:edge
```

For example, `1:0:bottom` means panel `1` is on Cinnamon monitor index `0` at the bottom edge.

The problem is that the numeric monitor index can drift after login, dock changes, wake, or hotplug events. `cinnamon-panel-anchor` treats that index as transient and stores the user's intent as connector plus edge.

## XRandR Mapping

The primary monitor-index-to-connector source is:

```bash
xrandr --listmonitors
```

The utility parses the monitor index, optional primary marker, geometry, and connector name. It assumes those indexes match Cinnamon's `panels-enabled` monitor indexes for the X11 session. The parsing is isolated so this can be adjusted later if Cinnamon-specific evidence requires a different mapping.

`xrandr --query --verbose` is used only by diagnostics.

## Restore Planning

For each saved anchor:

1. If the saved connector is present, write the panel entry with that connector's current monitor index and the saved edge.
2. If the saved connector is absent, keep the panel reachable on a visible monitor. The fallback prefers the current primary monitor index and otherwise uses the first visible monitor.
3. Existing unanchored panel entries are left alone.

The tool records the exact `panels-enabled` value it writes in state. That lets it distinguish its own restore from later user edits.

## Manual Move Detection

When topology is stable and `panels-enabled` changes to a value not written by this utility, the watcher treats that as likely user intent. It attempts to show a GTK confirmation dialog:

- Keep: update the saved anchor to match the new connector and edge.
- Restore: reapply the saved anchor.

If GTK cannot display a prompt, the tool records a pending decision in state and keeps the panel accessible instead of silently overwriting the likely manual move.

## Primary Monitor

This utility never changes the display primary. It does not call `xrandr --primary` or any equivalent display-configuration API.

Primary status is used only as a fallback preference when an anchored connector is absent and the panel must remain reachable.
