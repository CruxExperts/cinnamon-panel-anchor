from __future__ import annotations

from importlib import resources


DEFAULT_VERSION = "0.2.1"


def get_version() -> str:
    try:
        return resources.files("cinnamon_panel_anchor").joinpath("_version.txt").read_text(encoding="utf-8").strip()
    except Exception:
        return DEFAULT_VERSION
