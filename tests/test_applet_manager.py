from cinnamon_panel_anchor import applet_manager


class FakeAppletSettings:
    def __init__(self, values=None):
        self.values = list(values or [])
        self.writes = []
        self.next_applet_id = 12

    def get_enabled_applets(self):
        return self.values

    def set_enabled_applets(self, values):
        self.writes.append(values)
        self.values = values

    def get_next_applet_id(self):
        return self.next_applet_id

    def set_next_applet_id(self, value):
        self.next_applet_id = value


def test_enable_and_disable_applet_updates_enabled_applets():
    settings = FakeAppletSettings(["panel1:left:0:menu@cinnamon.org:0"])

    assert applet_manager.enable_applet(settings) is True
    assert settings.values[-1] == f"panel1:right:0:{applet_manager.APPLET_UUID}:12:orient"
    assert settings.next_applet_id == 13
    assert applet_manager.enable_applet(settings) is False

    assert applet_manager.disable_applet(settings) is True
    assert all(applet_manager.APPLET_UUID not in value for value in settings.values)


def test_enable_applet_appends_after_existing_right_panel_entries():
    settings = FakeAppletSettings(
        [
            "panel1:right:0:systray@cinnamon.org:3",
            "panel1:right:4:calendar@cinnamon.org:13",
            "panel1:left:2:menu@cinnamon.org:0",
        ]
    )

    assert applet_manager.enable_applet(settings) is True

    assert settings.values[-1] == f"panel1:right:5:{applet_manager.APPLET_UUID}:12:orient"


def test_install_applet_copies_packaged_assets(monkeypatch, tmp_path):
    monkeypatch.setattr(applet_manager, "cinnamon_applets_dir", lambda: tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))

    path = applet_manager.install_applet()

    assert path == tmp_path / applet_manager.APPLET_UUID
    assert (path / "metadata.json").exists()
    assert (path / "applet.js").exists()
    launcher = path / "cinnamon-panel-anchor-backend"
    assert launcher.exists()
    assert launcher.stat().st_mode & 0o111
    assert "-m cinnamon_panel_anchor.cli" in launcher.read_text(encoding="utf-8")


def test_install_applet_removes_pre_release_autostart_file(monkeypatch, tmp_path):
    monkeypatch.setattr(applet_manager, "cinnamon_applets_dir", lambda: tmp_path / "applets")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    legacy_path = applet_manager.legacy_autostart_path()
    legacy_path.parent.mkdir(parents=True)
    legacy_path.write_text("[Desktop Entry]\nExec=cinnamon-panel-anchor watch\n", encoding="utf-8")

    applet_manager.install_applet()

    assert not legacy_path.exists()


def test_export_spice_writes_expected_layout(tmp_path):
    root = applet_manager.export_spice(tmp_path)

    assert root == tmp_path / applet_manager.APPLET_UUID
    assert (root / "info.json").exists()
    assert (root / "README.md").exists()
    assert (root / "files" / applet_manager.APPLET_UUID / "metadata.json").exists()
    assert not (root / "screenshot.png").exists()


def test_cinnamon_applets_dir_uses_xdg_data_home(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

    assert applet_manager.cinnamon_applets_dir() == tmp_path / "data" / "cinnamon" / "applets"


def test_uninstall_applet_disables_before_removing_files(monkeypatch, tmp_path):
    monkeypatch.setattr(applet_manager, "cinnamon_applets_dir", lambda: tmp_path)
    applet_manager.install_applet()
    settings = FakeAppletSettings([applet_manager.APPLET_ENTRY])

    assert applet_manager.uninstall_applet(settings) is True

    assert settings.values == []
    assert not (tmp_path / applet_manager.APPLET_UUID).exists()
