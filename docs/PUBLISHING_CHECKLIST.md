# Publishing Checklist

- Run `uv run python tools/version_sync.py --check`.
- Run `uv run python tools/validate.py`.
- Run `uv run pytest`.
- Run `git diff --check`.
- Confirm README and Spices docs describe startup, session quit, and persistent disable behavior.
- Reinstall once with `uv run cinnamon-panel-anchor install-applet --enable`.
- Confirm Cinnamon shows one enabled applet entry for `cinnamon-panel-anchor@cruxexperts.com`.
- Confirm `Quit for Session` hides the applet without changing `enabled-applets`.
- Confirm `Disable Applet` removes the persistent Cinnamon `enabled-applets` entry.
- Confirm generated mockups are labeled and no Spices screenshot is shipped until replaced by a real Cinnamon screenshot.
