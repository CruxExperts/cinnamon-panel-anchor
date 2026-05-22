import sys
import types

import pytest

from cinnamon_panel_anchor.settings import CinnamonSettings, CinnamonSettingsError
from cinnamon_panel_anchor import settings


class MissingSchemaSource:
    def lookup(self, schema, recursive):
        return None


class FakeGio:
    class SettingsSchemaSource:
        @staticmethod
        def get_default():
            return MissingSchemaSource()

    class Settings:
        @staticmethod
        def new(schema):
            raise AssertionError("Settings.new should not be called without schema")


def test_missing_gio_schema_raises_settings_error(monkeypatch):
    fake_gi = types.ModuleType("gi")
    fake_gi.require_version = lambda name, version: None
    fake_repository = types.ModuleType("gi.repository")
    fake_repository.Gio = FakeGio
    monkeypatch.setitem(sys.modules, "gi", fake_gi)
    monkeypatch.setitem(sys.modules, "gi.repository", fake_repository)

    with pytest.raises(CinnamonSettingsError, match="org.cinnamon"):
        CinnamonSettings()


def test_system_gi_path_requires_matching_abi(monkeypatch, tmp_path):
    dist = tmp_path / "dist-packages"
    gi_dir = dist / "gi"
    gi_dir.mkdir(parents=True)
    (gi_dir / "_gi.cpython-999-x86_64-linux-gnu.so").write_text("", encoding="utf-8")
    monkeypatch.setattr(settings, "Path", lambda value: dist if "dist-packages" in value else tmp_path / value)
    monkeypatch.setattr(settings.sysconfig, "get_config_var", lambda name: "cpython-312-x86_64-linux-gnu")

    settings._include_system_gi_path()

    assert str(dist) not in sys.path
