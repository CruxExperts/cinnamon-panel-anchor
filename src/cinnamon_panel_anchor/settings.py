from __future__ import annotations

import sys
import sysconfig
from pathlib import Path


class CinnamonSettingsError(RuntimeError):
    pass


def _include_system_gi_path() -> None:
    soabi = sysconfig.get_config_var("SOABI") or ""
    for path in (Path("/usr/lib/python3/dist-packages"), Path("/usr/local/lib/python3/dist-packages")):
        if not (path / "gi").exists():
            continue
        if soabi and not any((path / "gi").glob(f"_gi.{soabi}.so")):
            continue
        if str(path) not in sys.path:
            sys.path.append(str(path))


class CinnamonSettings:
    schema = "org.cinnamon"
    key = "panels-enabled"

    def __init__(self) -> None:
        _include_system_gi_path()
        try:
            import gi  # type: ignore

            gi.require_version("Gio", "2.0")
            from gi.repository import Gio  # type: ignore
        except (ImportError, ValueError) as exc:
            raise CinnamonSettingsError("PyGObject Gio is not available") from exc
        source = Gio.SettingsSchemaSource.get_default()
        if source is None or source.lookup(self.schema, True) is None:
            raise CinnamonSettingsError(f"Gio schema {self.schema!r} is not available")
        self._settings = Gio.Settings.new(self.schema)

    def get_panels(self) -> list[str]:
        return list(self._settings.get_strv(self.key))

    def set_panels(self, values: list[str]) -> None:
        self._settings.set_strv(self.key, values)
