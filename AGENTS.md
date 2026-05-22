# AGENTS.md

## Project Instructions

- Use `uv` for Python environment, dependency, lockfile, and command execution workflows in this repository.
- Do not use pip-based workflows unless there is a clear compatibility reason, and document that reason.
- Keep changes surgical. Do not create repo-local Codex adapter, skill, or agent directories.
- The project is GUI-first: the Cinnamon applet is the primary product, and the CLI is backend/install/support tooling only.
- Do not make an invisible autostart watcher the default release path.
- The stable public UUID is `cinnamon-panel-anchor@cruxexperts.com`; directory names, metadata, installer behavior, docs, tests, and Spices export layout must match.
- README and Spices documentation are release-critical.
- Generated mockups must be labeled until replaced by real Cinnamon screenshots.
- Prefer native Cinnamon-style visuals over generic marketing art.
- The utility targets Linux Mint Cinnamon on X11. Wayland support is out of scope for the initial release.
- Never add behavior that calls `xrandr --primary` or otherwise changes the display primary monitor.
- Localsetup must remain global-only with `adapters: []`.
