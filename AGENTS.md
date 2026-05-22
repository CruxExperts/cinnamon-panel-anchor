# AGENTS.md

## Project Instructions

- Use `uv` for Python environment, dependency, lockfile, and command execution workflows in this repository.
- Do not use pip-based workflows unless there is a clear compatibility reason, and document that reason.
- Keep changes surgical. Do not create repo-local Codex adapter, skill, or agent directories.
- The utility targets Linux Mint Cinnamon on X11. Wayland support is out of scope for the initial release.
- Never add behavior that calls `xrandr --primary` or otherwise changes the display primary monitor.
