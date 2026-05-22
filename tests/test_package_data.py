from importlib import resources

from cinnamon_panel_anchor.applet_manager import APPLET_UUID


def test_applet_assets_are_packaged():
    root = resources.files("cinnamon_panel_anchor.applet") / APPLET_UUID

    for name in ("metadata.json", "applet.js", "settings-schema.json", "stylesheet.css"):
        assert (root / name).is_file()
