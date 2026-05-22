from cinnamon_panel_anchor.autostart import render_desktop_entry


def test_render_desktop_entry():
    entry = render_desktop_entry("cinnamon-panel-anchor watch --once")

    assert "[Desktop Entry]" in entry
    assert "Type=Application" in entry
    assert "Exec=cinnamon-panel-anchor watch --once" in entry
    assert "OnlyShowIn=X-Cinnamon;" in entry
    assert entry.endswith("\n")
