# User Guide

Design intent for future UI changes is tracked in [UI design patterns](ui-design-patterns.md). This guide stays focused on user workflows.

## Dashboard

The Cinnamon applet is the primary interface. Its popup dashboard shows:

- Health: protected, working, attention, or error.
- Saved anchors: panel connector and edge records captured from the current layout.
- Current monitors: monitor indexes and connector names reported by XRandR.
- Current panel entries: raw Cinnamon `panels-enabled` entries.
- Pending decisions: manual moves that need a keep-or-restore choice.
- Diagnostics summary: backend errors, missing Gio bindings, or XRandR mapping failures.

The applet can be placed on top, bottom, left, or right Cinnamon panels.

## Capture Current Layout

Use **Capture Current Layout** after arranging panels where you want them. The backend stores each panel as connector plus edge.

## Restore Saved Anchors

Use **Restore Saved Anchors** when panels appear on the wrong monitor after login, wake, dock, or hotplug. Restore changes only Cinnamon panel placement.

## Keep Current Move

Use **Keep Current Move** when you intentionally moved a panel and want the new placement to become the saved anchor.

## Notifications

The applet uses Cinnamon notifications only for attention cases:

- Restored drift.
- Missing connector fallback.
- Manual-move decision needed.
- Backend or applet failure.

## Fallback Meaning

If a saved connector is missing, the panel is kept reachable on a visible monitor. Primary status may be used as a read-only fallback preference, but the project never changes display primary.
