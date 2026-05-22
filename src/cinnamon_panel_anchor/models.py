from __future__ import annotations

from dataclasses import dataclass


VALID_EDGES = {"top", "bottom", "left", "right"}


@dataclass(frozen=True)
class PanelEntry:
    panel_id: str
    monitor: int
    edge: str

    @classmethod
    def parse(cls, value: str) -> "PanelEntry":
        parts = value.split(":")
        if len(parts) != 3:
            raise ValueError(f"invalid panel entry {value!r}")
        panel_id, monitor, edge = parts
        if not panel_id:
            raise ValueError("panel id is required")
        try:
            monitor_index = int(monitor)
        except ValueError as exc:
            raise ValueError(f"invalid monitor index {monitor!r}") from exc
        if monitor_index < 0:
            raise ValueError("monitor index must be non-negative")
        if edge not in VALID_EDGES:
            raise ValueError(f"invalid panel edge {edge!r}")
        return cls(panel_id=panel_id, monitor=monitor_index, edge=edge)

    def format(self) -> str:
        return f"{self.panel_id}:{self.monitor}:{self.edge}"


@dataclass(frozen=True)
class Monitor:
    index: int
    connector: str
    primary: bool = False
    geometry: str = ""


@dataclass(frozen=True)
class Anchor:
    panel_id: str
    connector: str
    edge: str


@dataclass(frozen=True)
class RestorePlan:
    desired: list[PanelEntry]
    changed: bool
    notes: list[str]
