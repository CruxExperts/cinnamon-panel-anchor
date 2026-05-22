from __future__ import annotations

from pathlib import Path

from .storage import xdg_config_home


DESKTOP_ID = "cinnamon-panel-anchor.desktop"


def autostart_path() -> Path:
    return xdg_config_home() / "autostart" / DESKTOP_ID


def render_desktop_entry(command: str = "cinnamon-panel-anchor watch") -> str:
    return "\n".join(
        [
            "[Desktop Entry]",
            "Type=Application",
            "Name=Cinnamon Panel Anchor",
            "Comment=Restore Cinnamon panel placement by connector",
            f"Exec={command}",
            "Terminal=false",
            "OnlyShowIn=X-Cinnamon;",
            "X-GNOME-Autostart-enabled=true",
            "",
        ]
    )


def install_autostart(command: str = "cinnamon-panel-anchor watch") -> Path:
    path = autostart_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_desktop_entry(command), encoding="utf-8")
    return path


def uninstall_autostart() -> bool:
    path = autostart_path()
    if not path.exists():
        return False
    path.unlink()
    return True
