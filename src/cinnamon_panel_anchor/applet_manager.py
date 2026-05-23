from __future__ import annotations

import json
import os
import shlex
import shutil
import sys
from importlib import resources
from pathlib import Path

from .settings import CinnamonSettings, CinnamonSettingsError
from .storage import xdg_config_home
from .version import get_version


APPLET_UUID = "cinnamon-panel-anchor@cruxexperts.com"
APPLET_ENTRY = f"panel1:right:0:{APPLET_UUID}:0:orient"
LEGACY_AUTOSTART_DESKTOP_ID = "cinnamon-panel-anchor.desktop"


def cinnamon_applets_dir() -> Path:
    value = os.environ.get("XDG_DATA_HOME")
    data_home = Path(value) if value else None
    if data_home is None or not data_home.is_absolute():
        data_home = Path.home() / ".local" / "share"
    return data_home / "cinnamon" / "applets"


def installed_applet_path() -> Path:
    return cinnamon_applets_dir() / APPLET_UUID


def applet_resource_root() -> resources.abc.Traversable:
    return resources.files("cinnamon_panel_anchor.applet") / APPLET_UUID


def _copy_resource_tree(source: resources.abc.Traversable, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            _copy_resource_tree(item, target)
        else:
            target.write_bytes(item.read_bytes())


def install_applet(backend_source: Path | None = None) -> Path:
    if backend_source is not None:
        backend_source = validate_backend_source(backend_source)
    destination = installed_applet_path()
    _copy_resource_tree(applet_resource_root(), destination)
    _write_backend_launcher(destination, backend_source=backend_source)
    remove_legacy_autostart_file()
    return destination


def legacy_autostart_path() -> Path:
    return xdg_config_home() / "autostart" / LEGACY_AUTOSTART_DESKTOP_ID


def remove_legacy_autostart_file() -> bool:
    path = legacy_autostart_path()
    if not path.exists():
        return False
    path.unlink()
    return True


def validate_backend_source(path: Path) -> Path:
    if not path.is_absolute():
        raise ValueError("--backend-source must be an absolute path")
    package_dir = path / "cinnamon_panel_anchor"
    if not package_dir.is_dir() or not (package_dir / "__init__.py").is_file():
        raise ValueError("--backend-source must contain importable cinnamon_panel_anchor source")
    return path


def _write_backend_launcher(destination: Path, *, backend_source: Path | None = None) -> Path:
    launcher = destination / "cinnamon-panel-anchor-backend"
    lines = ["#!/bin/sh"]
    if backend_source is not None:
        source = validate_backend_source(backend_source)
        lines.append(f"export PYTHONPATH={shlex.quote(str(source))}${{PYTHONPATH:+:$PYTHONPATH}}")
        lines.append("exec /usr/bin/python3 -m cinnamon_panel_anchor.cli \"$@\"")
    else:
        lines.append(f"exec {shlex.quote(sys.executable)} -m cinnamon_panel_anchor.cli \"$@\"")
    launcher.write_text("\n".join([*lines, ""]), encoding="utf-8")
    launcher.chmod(0o755)
    return launcher


def enable_applet(settings: CinnamonSettings | None = None) -> bool:
    settings = settings or CinnamonSettings()
    values = settings.get_enabled_applets()
    if any(f":{APPLET_UUID}:" in value or value.endswith(f":{APPLET_UUID}") for value in values):
        return False
    applet_id = settings.get_next_applet_id()
    settings.set_next_applet_id(applet_id + 1)
    settings.set_enabled_applets([*values, _applet_entry(values, applet_id)])
    return True


def _applet_entry(values: list[str], applet_id: int) -> str:
    order = 0
    for value in values:
        parts = value.split(":")
        if len(parts) >= 3 and parts[0] == "panel1" and parts[1] == "right":
            try:
                order = max(order, int(parts[2]) + 1)
            except ValueError:
                continue
    return f"panel1:right:{order}:{APPLET_UUID}:{applet_id}:orient"


def disable_applet(settings: CinnamonSettings | None = None) -> bool:
    settings = settings or CinnamonSettings()
    values = settings.get_enabled_applets()
    filtered = [
        value
        for value in values
        if f":{APPLET_UUID}:" not in value and not value.endswith(f":{APPLET_UUID}")
    ]
    if filtered == values:
        return False
    settings.set_enabled_applets(filtered)
    return True


def uninstall_applet(settings: CinnamonSettings | None = None) -> bool:
    try:
        disable_applet(settings)
    except CinnamonSettingsError:
        pass
    path = installed_applet_path()
    if not path.exists():
        return False
    shutil.rmtree(path)
    return True


def export_spice(output_dir: Path) -> Path:
    root = output_dir / APPLET_UUID
    files_root = root / "files" / APPLET_UUID
    if root.exists():
        shutil.rmtree(root)
    files_root.mkdir(parents=True)
    _copy_resource_tree(applet_resource_root(), files_root)
    metadata = json.loads((files_root / "metadata.json").read_text(encoding="utf-8"))
    metadata["version"] = get_version()
    (files_root / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / "info.json").write_text(
        json.dumps(
            {
                "uuid": APPLET_UUID,
                "name": metadata["name"],
                "description": metadata["description"],
                "version": metadata["version"],
                "author": "Crux Experts LLC",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "\n".join(
            [
                "# Cinnamon Panel Anchor",
                "",
                "Cinnamon Panel Anchor keeps Linux Mint Cinnamon/X11 panels tied to the monitor connector and edge you saved.",
                "",
                "This export is generated from the Python package's canonical applet assets.",
                "It restores Cinnamon panel placement when monitor indexes drift without changing the primary monitor.",
                "Generated documentation visuals are not real Cinnamon screenshots; add a real Cinnamon/X11 screenshot before Spices submission.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return root
