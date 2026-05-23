# Cinnamon Panel Anchor

![Cinnamon Panel Anchor logo](docs/assets/brand/panel-anchor-logo.svg)

![Generated Cinnamon Panel Anchor hero mockup](docs/assets/readme/hero.png)

Generated visual, not a real Cinnamon screenshot.

[![Python](https://img.shields.io/badge/python-3.10%2B-16324f)](pyproject.toml)
[![Desktop](https://img.shields.io/badge/Linux%20Mint-Cinnamon%20X11-47b39c)](docs/install.md)
[![License](https://img.shields.io/badge/license-MIT-16324f)](LICENSE)

Cinnamon Panel Anchor v0.2.2 keeps Linux Mint Cinnamon/X11 panels attached to the monitor connector and edge you saved. It fixes Cinnamon panel drift caused by monitor index changes without changing your primary monitor.

Public applet UUID: `cinnamon-panel-anchor@cruxexperts.com`.

Project repository: https://github.com/CruxExperts/cinnamon-panel-anchor

## Problem

Cinnamon stores panel placement by monitor index. XRandR monitor indexes can change after login, wake, dock, HDMI hotplug, or laptop lid changes. When that happens, the panel can move to the wrong screen or edge even though your physical monitor setup is the same.

Forcing a primary monitor with `xrandr --primary` solves a different problem and changes display preference. Cinnamon Panel Anchor restores only Cinnamon panel placement.

## Solution

1. Reads Cinnamon's `org.cinnamon panels-enabled` entries.
2. Maps Cinnamon monitor indexes to stable XRandR connector names.
3. Saves each panel as connector plus edge.
4. Shows status and actions in a native Cinnamon panel applet.
5. Restores Cinnamon panel placement when the saved connector appears at a different index.

## Install

The release installer is checksum-verified. It downloads the versioned installer asset, verifies the installer SHA256 before execution, then the installer verifies the versioned app bundle before extracting it.

```bash
tmp="$(mktemp)"
curl -fL --proto '=https' --tlsv1.2 -o "$tmp" https://github.com/CruxExperts/cinnamon-panel-anchor/releases/download/v0.2.2/install-cinnamon-panel-anchor-0.2.2.sh
printf '%s  %s\n' '9f64c4079e51fb1dc7d8994e81adb15832e67444e8f96f1d65f068a279dda0dc' "$tmp" | sha256sum -c - && sh "$tmp"
rm -f "$tmp"
```

The release install writes:

```text
~/.local/share/cinnamon-panel-anchor/versions/0.2.2/
~/.local/share/cinnamon-panel-anchor/current
~/.local/bin/cinnamon-panel-anchor
~/.local/share/cinnamon/applets/cinnamon-panel-anchor@cruxexperts.com/
```

It does not require `sudo`.

## First Run

1. Arrange your Cinnamon panels where you want them.
2. Install and enable the applet with the release command above.
3. Open the Cinnamon Panel Anchor applet from the Cinnamon panel.
4. Choose **Save Current Layout**.
5. Use **Restore Saved Layout** after monitor index drift, or let the applet surface attention states.

## What Changes

- Installs a Cinnamon applet under your user data directory.
- Installs a user launcher at `~/.local/bin/cinnamon-panel-anchor`.
- Saves panel anchors under your normal XDG config/state paths.
- Removes the old pre-release `cinnamon-panel-anchor.desktop` autostart file if present.

## What Does Not Change

- No `sudo`.
- No system files.
- No hidden background process as the default path.
- No display primary changes. The project never calls `xrandr --primary`.
- No Wayland support in this release; Linux Mint Cinnamon on X11 is the target.

## Visuals

![Generated applet popup mockup](docs/assets/readme/dashboard-mockup.png)

Generated mockup, not a real Cinnamon screenshot.

![Generated notification mockup](docs/assets/readme/notification-mockup.png)

Generated mockup, not a real Cinnamon screenshot.

Additional project-owned graphics and provenance live in [docs/assets](docs/assets/README.md). Generated images are tracked in [docs/assets/manifest.json](docs/assets/manifest.json). Do not submit generated mockups as Cinnamon Spices screenshots.

## Source Checkout

Source installs are for development and packaging work. Use `/usr/bin/python3` on Linux Mint so the virtual environment matches the system PyGObject extension ABI.

```bash
git clone https://github.com/CruxExperts/cinnamon-panel-anchor.git
cd cinnamon-panel-anchor
uv sync --python /usr/bin/python3
uv run pytest
uv run cinnamon-panel-anchor install-applet --enable
```

## Backend CLI

Release install:

```bash
cinnamon-panel-anchor status --json
cinnamon-panel-anchor capture --json
cinnamon-panel-anchor restore --json --dry-run
cinnamon-panel-anchor restore --json
cinnamon-panel-anchor diagnose --json
```

Source checkout:

```bash
uv run cinnamon-panel-anchor status --json
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

## Maintainer And Release

Current release: `v0.2.2`.

See [CHANGELOG.md](CHANGELOG.md) for release notes.

Copyright 2026 Crux Experts LLC.

Maintainer: Slavic Kozyuk.

GitHub: https://github.com/CruxExperts

Company: https://www.cruxexperts.com
