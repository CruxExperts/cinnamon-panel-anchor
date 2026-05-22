import subprocess

from cinnamon_panel_anchor.xrandr import list_monitors, parse_listmonitors


def test_parse_listmonitors():
    output = """Monitors: 2
 0: +*eDP-1 1920/344x1080/194+0+0  eDP-1
 1: +HDMI-1 2560/597x1440/336+1920+0  HDMI-1
"""

    monitors = parse_listmonitors(output)

    assert [monitor.index for monitor in monitors] == [0, 1]
    assert [monitor.connector for monitor in monitors] == ["eDP-1", "HDMI-1"]
    assert monitors[0].primary is True
    assert monitors[1].primary is False
    assert monitors[1].geometry == "2560/597x1440/336+1920+0"


def test_list_monitors_reports_error_when_output_has_no_parseable_monitors(monkeypatch):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout="Monitors: 1\nnot a monitor line\n",
            stderr="",
        ),
    )

    monitors, error = list_monitors()

    assert monitors == []
    assert error == "xrandr reported no parseable monitors"
