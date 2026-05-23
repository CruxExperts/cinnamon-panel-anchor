# Cinnamon Panel Anchor

![Cinnamon Panel Anchor logo](docs/assets/brand/panel-anchor-logo.svg)

![Cinnamon Panel Anchor hero](docs/assets/readme/hero.png)

[![Python](https://img.shields.io/badge/python-3.10%2B-16324f)](pyproject.toml)
[![Desktop](https://img.shields.io/badge/Linux%20Mint-Cinnamon%20X11-47b39c)](docs/install.md)
[![License](https://img.shields.io/badge/license-MIT-16324f)](LICENSE)

Cinnamon Panel Anchor v0.2.1 is a native Cinnamon applet backed by a small Python utility. It keeps Cinnamon panels attached to the monitor connector and edge you chose, even when XRandR monitor indexes change after login, dock, wake, or hotplug events.

The applet is the resident UI and controller. The CLI remains backend, installer, diagnostics, and release tooling.

Public applet UUID: `cinnamon-panel-anchor@cruxexperts.com`.

Project repository: https://github.com/CruxExperts/cinnamon-panel-anchor

## Problem

Linux Mint Cinnamon stores panel placement by monitor index, but XRandR monitor indexes are not stable. A laptop panel, dock, HDMI monitor, or wake-from-sleep event can reorder displays, which can leave your Cinnamon panel on the wrong screen or edge even though your physical monitor setup did not really change.

Common workarounds force a primary monitor with `xrandr --primary`, but that changes display preference to solve a panel-placement problem. Cinnamon Panel Anchor solves the narrower problem directly: it remembers the monitor connector and panel edge you intended, then restores Cinnamon's panel setting when monitor indexes drift.

## What It Does

1. Reads Cinnamon's `org.cinnamon panels-enabled` entries.
2. Maps Cinnamon monitor indexes to stable XRandR connector names.
3. Saves each panel as connector plus edge.
4. Shows status and one clear next action in a Cinnamon panel applet.
5. Restores only Cinnamon panel placement when the saved connector is found at a different index.

## Features

- Native Cinnamon panel applet with protected, working, attention, and error states.
- Custom panel-anchor logo and state icons, so the panel icon is recognizable instead of a generic theme checkmark.
- Guided status popup with a concise layout summary, one obvious next action, and compact secondary actions.
- Actions for refresh, save current layout, restore saved layout, display settings, diagnostics copy, and applet settings.
- Explicit lifecycle controls: **Quit for Session** hides the applet until Cinnamon reloads; **Disable Applet** removes the persistent Cinnamon enabled-applet entry.
- JSON backend commands for applet integration: `status`, `capture`, `restore`, `diagnose`, `disable-applet`, and `log-event`.
- Local diagnostic log at `$XDG_STATE_HOME/cinnamon-panel-anchor/debug.jsonl` with the latest 1000 records retained.
- Source installer and Cinnamon Spices export tooling.
- No display-primary changes. The project never calls `xrandr --primary`.

## Screenshots And Graphics

![Generated dashboard mockup](docs/assets/readme/dashboard-mockup.png)

Generated mockup for development documentation. Replace with a real Cinnamon screenshot before Spices submission.

![Generated notification mockup](docs/assets/readme/notification-mockup.png)

Additional project-owned graphics live in [docs/assets](docs/assets/README.md), including the social preview, logo, icon, and monitor-drift diagrams.

## Install From Source

```bash
git clone https://github.com/CruxExperts/cinnamon-panel-anchor.git
cd cinnamon-panel-anchor
uv sync --python /usr/bin/python3
uv run pytest
uv run cinnamon-panel-anchor install-applet --enable
```

Use `/usr/bin/python3` on Linux Mint so the virtual environment matches the system PyGObject extension ABI. The runtime uses Cinnamon's system Gio bindings; no GTK Python wheels are vendored.

`install-applet` copies the applet and writes a small backend launcher inside the installed applet directory so Cinnamon can call the same Python environment used for installation.

## First Run

1. Arrange your Cinnamon panels where you want them.
2. Install and enable the applet:

   ```bash
   uv run cinnamon-panel-anchor install-applet --enable
   ```

3. Open the applet from the Cinnamon panel.
4. Choose **Save Current Layout**.
5. Use **Restore Saved Layout** after monitor index drift or let the applet surface attention states.

## Backend CLI

```bash
uv run cinnamon-panel-anchor status --json
uv run cinnamon-panel-anchor capture --json
uv run cinnamon-panel-anchor restore --json --dry-run
uv run cinnamon-panel-anchor restore --json
uv run cinnamon-panel-anchor diagnose --json
uv run cinnamon-panel-anchor export-spice dist
```

## Documentation

- [Install guide](docs/install.md)
- [User guide](docs/user-guide.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Architecture](docs/architecture.md)
- [UI design patterns](docs/ui-design-patterns.md)
- [Migration guide](docs/migration.md)
- [Spices submission notes](docs/spices-submission.md)
- [Versioning](docs/VERSIONING.md)
- [Publishing checklist](docs/PUBLISHING_CHECKLIST.md)

## Release

Current release: `v0.2.1`.

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## How It Works

![Monitor index drift diagram](docs/assets/diagrams/monitor-index-drift.svg)

The backend reads Cinnamon's `org.cinnamon panels-enabled` entries and maps their monitor indexes through `xrandr --listmonitors`. Saved anchors store connector plus edge, not transient monitor index.

## Maintainer

Copyright 2026 Crux Experts LLC.

Maintainer: Slavic Kozyuk.

GitHub: https://github.com/CruxExperts/cinnamon-panel-anchor

Company: https://www.cruxexperts.com
