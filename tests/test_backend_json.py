import argparse
import json

from cinnamon_panel_anchor import cli
from cinnamon_panel_anchor.models import Anchor, Monitor


class FakeSettings:
    writes = []

    def get_panels(self):
        return ["1:0:bottom"]

    def set_panels(self, values):
        self.writes.append(values)


def _json_output(capsys):
    return json.loads(capsys.readouterr().out)


def test_status_json_uses_standard_contract(monkeypatch, capsys):
    monkeypatch.setattr(cli, "CinnamonSettings", FakeSettings)
    monkeypatch.setattr(cli, "list_monitors", lambda: ([Monitor(0, "HDMI-1", True, "1920x1080+0+0")], None))
    monkeypatch.setattr(cli, "load_anchors", lambda: [Anchor("1", "HDMI-1", "bottom")])
    monkeypatch.setattr(cli, "load_state", lambda: {})

    result = cli.cmd_status(argparse.Namespace(json=True))
    payload = _json_output(capsys)

    assert result == 0
    assert {"ok", "severity", "summary", "monitors", "panels", "anchors", "pending_decision", "plan", "messages", "error"} <= set(payload)
    assert payload["ok"] is True
    assert payload["plan"]["desired_panels"] == ["1:0:bottom"]


def test_capture_json_saves_anchors_and_state(monkeypatch, capsys):
    saved = {}
    monkeypatch.setattr(cli, "CinnamonSettings", FakeSettings)
    monkeypatch.setattr(cli, "list_monitors", lambda: ([Monitor(0, "HDMI-1", True, "1920x1080+0+0")], None))
    monkeypatch.setattr(cli, "save_anchors", lambda anchors: saved.setdefault("anchors", anchors))
    monkeypatch.setattr(cli, "load_state", lambda: {})
    monkeypatch.setattr(cli, "save_state", lambda state: saved.setdefault("state", state))

    result = cli.cmd_capture_json(argparse.Namespace(json=True))
    payload = _json_output(capsys)

    assert result == 0
    assert payload["ok"] is True
    assert saved["anchors"] == [Anchor("1", "HDMI-1", "bottom")]
    assert "last_topology" in saved["state"]


def test_restore_json_dry_run_reports_plan(monkeypatch, capsys):
    FakeSettings.writes = []
    monkeypatch.setattr(cli, "CinnamonSettings", FakeSettings)
    monkeypatch.setattr(cli, "list_monitors", lambda: ([Monitor(1, "HDMI-1", True, "1920x1080+0+0")], None))
    monkeypatch.setattr(cli, "load_anchors", lambda: [Anchor("1", "HDMI-1", "bottom")])
    monkeypatch.setattr(cli, "load_state", lambda: {})

    result = cli.cmd_restore(argparse.Namespace(json=True, dry_run=True))
    payload = _json_output(capsys)

    assert result == 0
    assert FakeSettings.writes == []
    assert payload["plan"]["changed"] is True
    assert payload["plan"]["desired_panels"] == ["1:1:bottom"]


def test_diagnose_json_uses_standard_contract(monkeypatch, capsys):
    monkeypatch.setattr(cli, "CinnamonSettings", FakeSettings)
    monkeypatch.setattr(cli, "list_monitors", lambda: ([Monitor(0, "HDMI-1")], None))
    monkeypatch.setattr(cli, "query_verbose", lambda: ("verbose", None))
    monkeypatch.setattr(cli, "load_anchors", lambda: [])
    monkeypatch.setattr(cli, "load_state", lambda: {})

    result = cli.cmd_diagnose(argparse.Namespace(json=True))
    payload = _json_output(capsys)

    assert result == 0
    assert payload["ok"] is True
    assert payload["xrandr_verbose"] == "verbose"
