# Publishing Checklist

## Validation

- Run `uv run python tools/version_sync.py --check`.
- Run `uv run python tools/validate.py`.
- Run `uv run pytest`.
- Run `git diff --check`.

## Public Documentation

- Confirm README and Spices docs describe startup, session quit, and persistent disable behavior.
- Confirm README explains the monitor-index drift problem and why the applet exists.
- Confirm README links to the public GitHub repo, install guide, user guide, architecture docs, and changelog.
- Confirm generated graphics are labeled and no final Cinnamon Spices screenshot is claimed until a real Cinnamon/X11 screenshot exists.

## Local Install Smoke

- Reinstall once with `uv run cinnamon-panel-anchor install-applet --enable`.
- Confirm Cinnamon shows one enabled applet entry for `cinnamon-panel-anchor@cruxexperts.com`.
- Confirm `Quit for Session` hides the applet without changing `enabled-applets`.
- Confirm `Disable Applet` removes the persistent Cinnamon `enabled-applets` entry.

## GitHub Publication

- Create the public repo at `https://github.com/CruxExperts/cinnamon-panel-anchor`.
- Set the default branch to `main`.
- Add description: `Native Cinnamon applet that keeps Linux Mint panels anchored to monitor connectors on X11.`
- Add topics: `cinnamon`, `linux-mint`, `x11`, `xrandr`, `panel`, `applet`.
- Push the release tag for the current `VERSION`.
