# Architecture

## Product Shape

Cinnamon Panel Anchor is GUI-first. The Cinnamon applet is the resident controller, status surface, and action launcher. The Python CLI is backend, installer, diagnostics, and packaging support tooling.

The default release path is not an invisible autostart watcher. Legacy watcher commands remain available for migration and development only.

The applet popup should follow the documented [UI design patterns](ui-design-patterns.md): a guided status header, one primary next action, grouped secondary actions, disabled reasons for invalid actions, and attention-only notifications.

## Applet To Backend Contract

The applet invokes the Python backend through JSON commands:

```bash
cinnamon-panel-anchor status --json
cinnamon-panel-anchor capture --json
cinnamon-panel-anchor restore --json
cinnamon-panel-anchor restore --json --dry-run
cinnamon-panel-anchor diagnose --json
```

All applet-facing JSON results use these top-level keys:

```text
ok, severity, summary, monitors, panels, anchors, pending_decision, plan, messages, error
```

## Cinnamon Panel Setting

Cinnamon stores enabled panel placement in the `org.cinnamon panels-enabled` string-vector setting. Each entry has this shape:

```text
panel_id:monitor_index:edge
```

For example, `1:0:bottom` means panel `1` is on Cinnamon monitor index `0` at the bottom edge.

## XRandR Mapping

The backend maps monitor indexes to connectors with:

```bash
xrandr --listmonitors
```

The utility parses monitor index, optional primary marker, geometry, and connector name. `xrandr --query --verbose` is used only by diagnostics.

## Restore Planning

For each saved anchor:

1. If the saved connector is present, write the panel entry with that connector's current monitor index and saved edge.
2. If the saved connector is absent, keep the panel reachable on a visible monitor. The fallback prefers the current primary monitor index and otherwise uses the first visible monitor.
3. Existing unanchored panel entries are left alone.

The backend records the exact `panels-enabled` value it writes in state, which lets it distinguish its own restore from later user edits.

## Notifications

The applet uses Cinnamon notifications for attention-only events: restored drift, missing connector fallback, manual-move decisions, and backend failures.

## Primary Monitor

This utility never changes display primary. It does not call `xrandr --primary` or any equivalent display-configuration API.

Primary status is read-only metadata used only as a fallback preference when an anchored connector is absent.
