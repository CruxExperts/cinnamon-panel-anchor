# Publishing Checklist

## Validation

- Run `uv run python tools/version_sync.py --check`.
- Run `uv run python tools/validate.py`.
- Run `uv run pytest`.
- Run `git diff --check`.
- Run `localsetup adapters --target-directory . --provenance`.

## Public Documentation

- Confirm README leads with the monitor-index drift problem and the checksum-verified release installer.
- Confirm source checkout and `uv` setup are secondary to the release installer path.
- Confirm release docs use checksum-verified or integrity-checked wording only.
- Confirm README and Spices docs describe startup, session quit, and persistent disable behavior.
- Confirm README links to the public GitHub repo, install guide, user guide, architecture docs, and changelog.
- Confirm generated graphics are labeled and no final Cinnamon Spices screenshot is claimed until a real Cinnamon/X11 screenshot exists.
- Confirm `docs/assets/manifest.json` lists all public PNG images and marks generated mockups as `real_cinnamon_screenshot: false`.

## Local Install Smoke

- Reinstall once with the release installer.
- Confirm Cinnamon shows one enabled applet entry for `cinnamon-panel-anchor@cruxexperts.com`.
- Confirm `~/.local/bin/cinnamon-panel-anchor` points at `~/.local/share/cinnamon-panel-anchor/versions/0.2.2/src`.
- Confirm the installed applet backend launcher contains a stable `PYTHONPATH`, not a temporary path.
- Confirm **Quit for Session** hides the applet without changing `enabled-applets`.
- Confirm **Disable Applet** removes the persistent Cinnamon `enabled-applets` entry.

## GitHub Publication

- Push tag `v0.2.2`.
- Confirm the release workflow uploads:
  - `cinnamon-panel-anchor-0.2.2.tar.gz`
  - `install-cinnamon-panel-anchor-0.2.2.sh`
  - `SHA256SUMS`
  - `README-install-snippet.md`
- After publication, run:

  ```bash
  gh release view v0.2.2 --repo CruxExperts/cinnamon-panel-anchor --json assets
  ```

- Download the assets and verify checksums against `SHA256SUMS`.
