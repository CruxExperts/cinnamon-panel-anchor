# Install Guide

## Requirements

- Linux Mint Cinnamon on X11.
- `/usr/bin/python3`.
- `curl`, `sha256sum`, and `tar`.
- Cinnamon GSettings schema `org.cinnamon`.
- XRandR command-line tools.

Wayland is out of scope for this release.

## Release Install

The release path is checksum-verified and does not require `sudo`.

```bash
tmp="$(mktemp)"
curl -fL --proto '=https' --tlsv1.2 -o "$tmp" https://github.com/CruxExperts/cinnamon-panel-anchor/releases/download/v0.2.2/install-cinnamon-panel-anchor-0.2.2.sh
printf '%s  %s\n' '092ed23b33805396536aec3411ac52d4d8891e1451a1cc819e4126dcd8d4a64a' "$tmp" | sha256sum -c - && sh "$tmp"
rm -f "$tmp"
```

The installer verifies the downloaded app bundle before extracting it, then installs:

```text
~/.local/share/cinnamon-panel-anchor/versions/0.2.2/
~/.local/share/cinnamon-panel-anchor/current
~/.local/bin/cinnamon-panel-anchor
~/.local/share/cinnamon/applets/cinnamon-panel-anchor@cruxexperts.com/
```

The applet backend launcher points at the persistent extracted `src/` directory. It does not reference a temporary download directory.

Restart Cinnamon if the applet list does not refresh:

```text
Alt+F2
r
Enter
```

## First Run

1. Arrange your Cinnamon panels where you want them.
2. Open the Cinnamon Panel Anchor applet.
3. Choose **Save Current Layout**.
4. Use **Restore Saved Layout** after monitor index drift.

## Release Commands

```bash
cinnamon-panel-anchor status --json
cinnamon-panel-anchor diagnose --json
cinnamon-panel-anchor restore --json --dry-run
cinnamon-panel-anchor disable-applet --json
cinnamon-panel-anchor uninstall-applet --json
```

## Source Checkout

Source checkout installs are for development and packaging. Use `/usr/bin/python3` on Linux Mint so the virtual environment matches the system PyGObject extension ABI.

```bash
git clone https://github.com/CruxExperts/cinnamon-panel-anchor.git
cd cinnamon-panel-anchor
uv sync --python /usr/bin/python3
uv run pytest
uv run cinnamon-panel-anchor --help
uv run cinnamon-panel-anchor install-applet --enable
```

Without `--backend-source`, `install-applet` preserves source-checkout behavior and writes a backend launcher for the Python interpreter used during installation.

## Export Spices Layout

```bash
uv run cinnamon-panel-anchor export-spice dist
```

The export contains metadata and files, but no final `screenshot.png` until a real Cinnamon/X11 screenshot is captured.
