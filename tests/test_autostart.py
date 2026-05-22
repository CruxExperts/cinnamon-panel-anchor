import json

from cinnamon_panel_anchor import cli
from cinnamon_panel_anchor.autostart import autostart_path, render_desktop_entry


def test_render_desktop_entry():
    entry = render_desktop_entry("cinnamon-panel-anchor watch --once")

    assert "[Desktop Entry]" in entry
    assert "Type=Application" in entry
    assert "Exec=cinnamon-panel-anchor watch --once" in entry
    assert "OnlyShowIn=X-Cinnamon;" in entry
    assert entry.endswith("\n")


def test_autostart_json_status_install_uninstall(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path / "runtime"))
    (tmp_path / "runtime").mkdir()

    assert cli.main(["autostart-status", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["installed"] is False

    assert cli.main(["install-autostart", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["installed"] is True
    assert autostart_path().exists()

    assert cli.main(["uninstall-autostart", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["installed"] is False
    assert not autostart_path().exists()
