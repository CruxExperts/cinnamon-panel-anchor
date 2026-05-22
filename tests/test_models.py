import pytest

from cinnamon_panel_anchor.models import PanelEntry
from cinnamon_panel_anchor.planner import format_panels, parse_panels


def test_parse_and_format_panel_entry():
    entry = PanelEntry.parse("12:3:bottom")

    assert entry.panel_id == "12"
    assert entry.monitor == 3
    assert entry.edge == "bottom"
    assert entry.format() == "12:3:bottom"


def test_parse_panel_entry_rejects_invalid_edge():
    with pytest.raises(ValueError):
        PanelEntry.parse("1:0:center")


def test_parse_and_format_panel_list():
    entries = parse_panels(["1:0:top", "2:1:left"])

    assert format_panels(entries) == ["1:0:top", "2:1:left"]
