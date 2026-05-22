from __future__ import annotations

import hashlib
from collections.abc import Iterable

from .models import Anchor, Monitor, PanelEntry, RestorePlan


def parse_panels(values: Iterable[str]) -> list[PanelEntry]:
    return [PanelEntry.parse(value) for value in values]


def format_panels(entries: Iterable[PanelEntry]) -> list[str]:
    return [entry.format() for entry in entries]


def topology_fingerprint(monitors: Iterable[Monitor]) -> str:
    parts = [
        f"{monitor.index}:{monitor.connector}:{monitor.primary}:{monitor.geometry}"
        for monitor in sorted(monitors, key=lambda item: item.index)
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def capture_anchors(panels: list[PanelEntry], monitors: list[Monitor]) -> list[Anchor]:
    by_index = {monitor.index: monitor for monitor in monitors}
    anchors: list[Anchor] = []
    for panel in panels:
        monitor = by_index.get(panel.monitor)
        if monitor is None:
            continue
        anchors.append(Anchor(panel_id=panel.panel_id, connector=monitor.connector, edge=panel.edge))
    return anchors


def fallback_monitor_index(monitors: list[Monitor], current: PanelEntry | None = None) -> int | None:
    if not monitors:
        return current.monitor if current is not None else None
    primary = next((monitor for monitor in monitors if monitor.primary), None)
    return (primary or sorted(monitors, key=lambda item: item.index)[0]).index


def plan_restore(
    current: list[PanelEntry],
    anchors: list[Anchor],
    monitors: list[Monitor],
) -> RestorePlan:
    by_connector = {monitor.connector: monitor for monitor in monitors}
    by_panel = {panel.panel_id: panel for panel in current}
    anchor_by_panel = {anchor.panel_id: anchor for anchor in anchors}
    desired_by_panel = dict(by_panel)
    notes: list[str] = []

    for anchor in anchors:
        current_panel = by_panel.get(anchor.panel_id)
        monitor = by_connector.get(anchor.connector)
        if monitor is not None:
            desired_by_panel[anchor.panel_id] = PanelEntry(anchor.panel_id, monitor.index, anchor.edge)
            continue

        fallback = fallback_monitor_index(monitors, current_panel)
        if fallback is None:
            notes.append(f"panel {anchor.panel_id}: no visible monitor available")
            continue
        desired_by_panel[anchor.panel_id] = PanelEntry(anchor.panel_id, fallback, anchor.edge)
        notes.append(
            f"panel {anchor.panel_id}: connector {anchor.connector} absent; using monitor {fallback}"
        )

    desired: list[PanelEntry] = []
    seen: set[str] = set()
    for panel in current:
        desired.append(desired_by_panel[panel.panel_id])
        seen.add(panel.panel_id)
    for anchor in anchors:
        if anchor.panel_id not in seen and anchor.panel_id in desired_by_panel:
            desired.append(desired_by_panel[anchor.panel_id])

    changed = format_panels(desired) != format_panels(current)
    if not anchor_by_panel:
        notes.append("no anchors saved")
    return RestorePlan(desired=desired, changed=changed, notes=notes)


def likely_manual_move(
    previous_panels: list[str] | None,
    current_panels: list[str],
    last_written_panels: list[str] | None,
    previous_topology: str | None,
    current_topology: str,
) -> bool:
    if previous_panels is None or previous_panels == current_panels:
        return False
    if current_panels == last_written_panels:
        return False
    return previous_topology == current_topology
