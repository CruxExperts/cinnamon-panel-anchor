import argparse
import pytest

from cinnamon_panel_anchor import cli
from cinnamon_panel_anchor.models import Anchor, Monitor


class FakeSettings:
    writes = []

    def get_panels(self):
        return ["1:0:bottom"]

    def set_panels(self, values):
        self.writes.append(values)


def test_restore_does_not_write_when_monitor_mapping_fails(monkeypatch):
    FakeSettings.writes = []
    monkeypatch.setattr(cli, "CinnamonSettings", FakeSettings)
    monkeypatch.setattr(cli, "list_monitors", lambda: ([], "xrandr failed"))

    result = cli.cmd_restore(argparse.Namespace(dry_run=False))

    assert result == 2
    assert FakeSettings.writes == []


def test_capture_clears_pending_decision(monkeypatch):
    saved = {}
    monkeypatch.setattr(cli, "CinnamonSettings", FakeSettings)
    monkeypatch.setattr(cli, "list_monitors", lambda: ([Monitor(0, "HDMI-1", True, "1920x1080+0+0")], None))
    monkeypatch.setattr(cli, "save_anchors", lambda anchors: saved.setdefault("anchors", anchors))
    monkeypatch.setattr(cli, "load_state", lambda: {"pending_decision": {"reason": "manual move"}})
    monkeypatch.setattr(cli, "save_state", lambda state: saved.setdefault("state", state))

    result = cli.cmd_capture(argparse.Namespace())

    assert result == 0
    assert saved["state"]["pending_decision"] is None


@pytest.mark.parametrize("command", ["autostart-status", "install-autostart", "uninstall-autostart"])
def test_cli_parser_does_not_expose_autostart_commands(command):
    parser = cli.build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args([command])


def test_install_applet_parser_accepts_backend_source():
    parser = cli.build_parser()

    args = parser.parse_args(["install-applet", "--backend-source", "/opt/cinnamon-panel-anchor/src", "--enable"])

    assert args.backend_source == "/opt/cinnamon-panel-anchor/src"
    assert args.enable is True


def test_install_applet_uses_release_backend_source_env(monkeypatch, tmp_path):
    backend_source = tmp_path / "release" / "src"
    package = backend_source / "cinnamon_panel_anchor"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    calls = {}
    monkeypatch.setenv("CINNAMON_PANEL_ANCHOR_BACKEND_SOURCE", str(backend_source))
    monkeypatch.setattr(cli, "install_applet", lambda backend_source=None: calls.setdefault("backend_source", backend_source) or tmp_path / "applet")

    result = cli.cmd_install_applet(argparse.Namespace(backend_source=None, enable=False, json=False))

    assert result == 0
    assert calls["backend_source"] == backend_source


def test_restore_does_not_write_when_monitor_mapping_is_empty(monkeypatch):
    FakeSettings.writes = []
    monkeypatch.setattr(cli, "CinnamonSettings", FakeSettings)
    monkeypatch.setattr(cli, "list_monitors", lambda: ([], None))
    monkeypatch.setattr(cli, "load_anchors", lambda: [Anchor("1", "HDMI-1", "top")])

    result = cli.cmd_restore(argparse.Namespace(dry_run=False))

    assert result == 2
    assert FakeSettings.writes == []


def test_restore_dry_run_does_not_fail_without_monitor_mapping(monkeypatch, capsys):
    FakeSettings.writes = []
    monkeypatch.setattr(cli, "CinnamonSettings", FakeSettings)
    monkeypatch.setattr(cli, "list_monitors", lambda: ([], "xrandr failed"))

    result = cli.cmd_restore(argparse.Namespace(dry_run=True))

    assert result == 0
    assert FakeSettings.writes == []
    assert "monitor mapping unavailable" in capsys.readouterr().out


def test_watch_does_not_write_when_monitor_mapping_fails(monkeypatch):
    FakeSettings.writes = []
    monkeypatch.setattr(cli, "CinnamonSettings", FakeSettings)
    monkeypatch.setattr(cli, "list_monitors", lambda: ([], "xrandr failed"))

    result = cli._watch_once()

    assert result == 2
    assert FakeSettings.writes == []


def test_watch_does_not_write_when_monitor_mapping_is_empty(monkeypatch):
    FakeSettings.writes = []
    monkeypatch.setattr(cli, "CinnamonSettings", FakeSettings)
    monkeypatch.setattr(cli, "list_monitors", lambda: ([], None))
    monkeypatch.setattr(cli, "load_anchors", lambda: [Anchor("1", "HDMI-1", "top")])

    result = cli._watch_once()

    assert result == 2
    assert FakeSettings.writes == []
