from cinnamon_panel_anchor.models import Anchor, Monitor, PanelEntry
from cinnamon_panel_anchor.planner import (
    capture_anchors,
    format_panels,
    likely_manual_move,
    plan_restore,
    topology_fingerprint,
)


def test_capture_anchors_uses_current_monitor_connector():
    anchors = capture_anchors(
        [PanelEntry("1", 1, "bottom")],
        [Monitor(0, "eDP-1", True), Monitor(1, "HDMI-1")],
    )

    assert anchors == [Anchor("1", "HDMI-1", "bottom")]


def test_restore_updates_monitor_index_when_connector_moves():
    current = [PanelEntry("1", 0, "bottom")]
    anchors = [Anchor("1", "HDMI-1", "bottom")]
    monitors = [Monitor(0, "eDP-1", True), Monitor(2, "HDMI-1")]

    plan = plan_restore(current, anchors, monitors)

    assert plan.changed is True
    assert format_panels(plan.desired) == ["1:2:bottom"]


def test_restore_falls_back_to_primary_when_connector_absent():
    current = [PanelEntry("1", 7, "bottom")]
    anchors = [Anchor("1", "DP-1", "bottom")]
    monitors = [Monitor(0, "eDP-1"), Monitor(1, "HDMI-1", True)]

    plan = plan_restore(current, anchors, monitors)

    assert format_panels(plan.desired) == ["1:1:bottom"]
    assert "connector DP-1 absent" in plan.notes[0]


def test_restore_preserves_unanchored_panel_entries():
    current = [PanelEntry("1", 0, "bottom"), PanelEntry("2", 1, "top")]
    anchors = [Anchor("1", "HDMI-1", "bottom")]
    monitors = [Monitor(0, "eDP-1", True), Monitor(1, "HDMI-1")]

    plan = plan_restore(current, anchors, monitors)

    assert format_panels(plan.desired) == ["1:1:bottom", "2:1:top"]


def test_likely_manual_move_when_topology_stable_and_user_changes_panel():
    topology = topology_fingerprint([Monitor(0, "eDP-1", True)])

    assert likely_manual_move(
        previous_panels=["1:0:bottom"],
        current_panels=["1:0:top"],
        last_written_panels=["1:0:bottom"],
        previous_topology=topology,
        current_topology=topology,
    )


def test_not_manual_move_when_topology_changes():
    assert not likely_manual_move(
        previous_panels=["1:0:bottom"],
        current_panels=["1:1:bottom"],
        last_written_panels=["1:0:bottom"],
        previous_topology="old",
        current_topology="new",
    )
