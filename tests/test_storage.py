from pathlib import Path

from cinnamon_panel_anchor.storage import config_dir, config_path, state_dir, state_path


def test_xdg_paths_use_environment(monkeypatch, tmp_path):
    config = tmp_path / "config-home"
    state = tmp_path / "state-home"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config))
    monkeypatch.setenv("XDG_STATE_HOME", str(state))

    assert config_dir() == config / "cinnamon-panel-anchor"
    assert state_dir() == state / "cinnamon-panel-anchor"
    assert config_path() == config / "cinnamon-panel-anchor" / "config.json"
    assert state_path() == state / "cinnamon-panel-anchor" / "state.json"


def test_xdg_paths_default_to_home(monkeypatch, tmp_path):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert config_dir() == tmp_path / ".config" / "cinnamon-panel-anchor"
    assert state_dir() == tmp_path / ".local" / "state" / "cinnamon-panel-anchor"


def test_xdg_paths_ignore_empty_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", "")
    monkeypatch.setenv("XDG_STATE_HOME", "")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert config_dir() == tmp_path / ".config" / "cinnamon-panel-anchor"
    assert state_dir() == tmp_path / ".local" / "state" / "cinnamon-panel-anchor"


def test_xdg_paths_ignore_relative_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", "relative-config")
    monkeypatch.setenv("XDG_STATE_HOME", "relative-state")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert config_dir() == tmp_path / ".config" / "cinnamon-panel-anchor"
    assert state_dir() == tmp_path / ".local" / "state" / "cinnamon-panel-anchor"
