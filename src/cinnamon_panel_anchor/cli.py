from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

from .autostart import autostart_path, install_autostart, uninstall_autostart
from .planner import (
    capture_anchors,
    format_panels,
    likely_manual_move,
    parse_panels,
    plan_restore,
    topology_fingerprint,
)
from .prompt import ask_keep_or_restore
from .settings import CinnamonSettings, CinnamonSettingsError
from .storage import (
    config_path,
    load_anchors,
    load_state,
    save_anchors,
    save_state,
    state_path,
)
from .xrandr import list_monitors, query_verbose


def _json(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def _settings() -> CinnamonSettings | None:
    try:
        return CinnamonSettings()
    except CinnamonSettingsError:
        return None


def _read_panels() -> tuple[list[str], str | None]:
    settings = _settings()
    if settings is None:
        return [], "Gio org.cinnamon settings unavailable"
    return settings.get_panels(), None


def _write_panels(values: list[str]) -> str | None:
    settings = _settings()
    if settings is None:
        return "Gio org.cinnamon settings unavailable"
    settings.set_panels(values)
    return None


def _monitor_mapping_error(monitors: list[Any], monitor_error: str | None) -> str | None:
    if monitor_error:
        return monitor_error
    if not monitors:
        return "xrandr reported no parseable monitors"
    return None


def cmd_capture(_: argparse.Namespace) -> int:
    panel_values, panel_error = _read_panels()
    monitors, monitor_error = list_monitors()
    if panel_error:
        print(panel_error, file=sys.stderr)
        return 2
    mapping_error = _monitor_mapping_error(monitors, monitor_error)
    if mapping_error:
        print(mapping_error, file=sys.stderr)
        return 2
    panels = parse_panels(panel_values)
    anchors = capture_anchors(panels, monitors)
    save_anchors(anchors)
    state = load_state()
    state["last_seen_panels"] = panel_values
    state["last_topology"] = topology_fingerprint(monitors)
    save_state(state)
    print(f"saved {len(anchors)} anchor(s) to {config_path()}")
    return 0


def _status_payload() -> dict[str, Any]:
    panel_values, panel_error = _read_panels()
    monitors, monitor_error = list_monitors()
    anchors = load_anchors()
    state = load_state()
    pending = state.get("pending_decision")
    plan = None
    try:
        plan = plan_restore(parse_panels(panel_values), anchors, monitors)
    except ValueError as exc:
        pending = pending or {"reason": str(exc)}
    return {
        "monitors": [monitor.__dict__ for monitor in monitors],
        "monitor_error": monitor_error,
        "panels": panel_values,
        "panel_error": panel_error,
        "anchors": [anchor.__dict__ for anchor in anchors],
        "pending_decision": pending,
        "planned_panels": format_panels(plan.desired) if plan else None,
        "plan_notes": plan.notes if plan else [],
        "config_path": str(config_path()),
        "state_path": str(state_path()),
    }


def cmd_status(args: argparse.Namespace) -> int:
    payload = _status_payload()
    if args.json:
        _json(payload)
        return 0
    print(f"config: {payload['config_path']}")
    print(f"state: {payload['state_path']}")
    if payload["monitor_error"]:
        print(f"monitors: unavailable ({payload['monitor_error']})")
    else:
        print("monitors:")
        for monitor in payload["monitors"]:
            primary = " primary" if monitor["primary"] else ""
            print(f"  {monitor['index']}: {monitor['connector']} {monitor['geometry']}{primary}")
    if payload["panel_error"]:
        print(f"panels: unavailable ({payload['panel_error']})")
    else:
        print("panels:")
        for panel in payload["panels"]:
            print(f"  {panel}")
    print("anchors:")
    for anchor in payload["anchors"]:
        print(f"  {anchor['panel_id']}: {anchor['connector']} {anchor['edge']}")
    if payload["pending_decision"]:
        print(f"pending decision: {payload['pending_decision']}")
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    panel_values, panel_error = _read_panels()
    monitors, monitor_error = list_monitors()
    anchors = load_anchors()
    if panel_error:
        if args.dry_run:
            print(panel_error)
            return 0
        print(panel_error, file=sys.stderr)
        return 2
    mapping_error = _monitor_mapping_error(monitors, monitor_error)
    if mapping_error:
        if args.dry_run:
            print(f"monitor mapping unavailable: {mapping_error}")
            return 0
        print(f"monitor mapping unavailable: {mapping_error}", file=sys.stderr)
        return 2
    current = parse_panels(panel_values)
    plan = plan_restore(current, anchors, monitors)
    desired_values = format_panels(plan.desired)
    for note in plan.notes:
        print(note)
    if not plan.changed:
        print("panels already match saved anchors")
        return 0
    if args.dry_run:
        print("would write panels-enabled:")
        for value in desired_values:
            print(f"  {value}")
        return 0
    error = _write_panels(desired_values)
    if error:
        print(error, file=sys.stderr)
        return 2
    state = load_state()
    state["last_written_panels"] = desired_values
    state["last_seen_panels"] = desired_values
    state["last_topology"] = topology_fingerprint(monitors)
    save_state(state)
    print("restored panel anchors")
    return 0


def _record_pending(panel_values: list[str], monitors: list[Any]) -> None:
    state = load_state()
    state["pending_decision"] = {
        "reason": "likely manual panel move; prompt unavailable",
        "panels": panel_values,
        "topology": topology_fingerprint(monitors),
    }
    state["last_seen_panels"] = panel_values
    state["last_topology"] = topology_fingerprint(monitors)
    save_state(state)


def _watch_once() -> int:
    panel_values, panel_error = _read_panels()
    monitors, monitor_error = list_monitors()
    if panel_error:
        print(panel_error, file=sys.stderr)
        return 2
    mapping_error = _monitor_mapping_error(monitors, monitor_error)
    if mapping_error:
        print(f"monitor mapping unavailable: {mapping_error}", file=sys.stderr)
        return 2
    state = load_state()
    current_topology = topology_fingerprint(monitors)
    last_seen = state.get("last_seen_panels")
    last_written = state.get("last_written_panels")
    last_topology = state.get("last_topology")
    anchors = load_anchors()

    if likely_manual_move(last_seen, panel_values, last_written, last_topology, current_topology):
        decision = ask_keep_or_restore("Cinnamon panel placement changed. Keep it or restore saved anchors?")
        if decision == "keep":
            save_anchors(capture_anchors(parse_panels(panel_values), monitors))
            state["pending_decision"] = None
            print("kept manual panel placement")
        elif decision == "restore":
            plan = plan_restore(parse_panels(panel_values), anchors, monitors)
            values = format_panels(plan.desired)
            error = _write_panels(values)
            if error:
                print(error, file=sys.stderr)
                return 2
            state["last_written_panels"] = values
            panel_values = values
            print("restored saved panel anchors")
        else:
            _record_pending(panel_values, monitors)
            print("recorded pending manual-move decision")
            return 0
    else:
        plan = plan_restore(parse_panels(panel_values), anchors, monitors)
        if plan.changed:
            values = format_panels(plan.desired)
            error = _write_panels(values)
            if error:
                print(error, file=sys.stderr)
                return 2
            state["last_written_panels"] = values
            panel_values = values
            print("restored panel anchors")

    state["last_seen_panels"] = panel_values
    state["last_topology"] = current_topology
    save_state(state)
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    if args.once:
        return _watch_once()
    while True:
        code = _watch_once()
        if code != 0:
            return code
        time.sleep(args.interval)


def cmd_install_autostart(_: argparse.Namespace) -> int:
    path = install_autostart()
    print(f"installed {path}")
    return 0


def cmd_uninstall_autostart(_: argparse.Namespace) -> int:
    removed = uninstall_autostart()
    print(f"removed {autostart_path()}" if removed else f"not installed: {autostart_path()}")
    return 0


def cmd_diagnose(args: argparse.Namespace) -> int:
    panels, panel_error = _read_panels()
    monitors, monitor_error = list_monitors()
    verbose, verbose_error = query_verbose()
    payload = {
        "panels": panels,
        "panel_error": panel_error,
        "monitors": [monitor.__dict__ for monitor in monitors],
        "monitor_error": monitor_error,
        "anchors": [anchor.__dict__ for anchor in load_anchors()],
        "config_path": str(config_path()),
        "state_path": str(state_path()),
        "xrandr_verbose_error": verbose_error,
        "xrandr_verbose": verbose,
    }
    if args.json:
        _json(payload)
    else:
        print(f"config: {payload['config_path']}")
        print(f"state: {payload['state_path']}")
        print(f"panels: {panels if not panel_error else panel_error}")
        print(f"monitors: {len(monitors) if not monitor_error else monitor_error}")
        print(f"xrandr verbose: {'available' if not verbose_error else verbose_error}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cinnamon-panel-anchor")
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture", help="save current panel placements as anchors")
    capture.set_defaults(func=cmd_capture)

    status = sub.add_parser("status", help="show monitors, panels, anchors, and pending decisions")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=cmd_status)

    for name in ("apply", "restore"):
        restore = sub.add_parser(name, help="reconcile Cinnamon panels with saved anchors")
        restore.add_argument("--dry-run", action="store_true")
        restore.set_defaults(func=cmd_restore)

    watch = sub.add_parser("watch", help="watch for login, wake, hotplug, or settings drift")
    watch.add_argument("--once", action="store_true")
    watch.add_argument("--interval", type=float, default=5.0)
    watch.set_defaults(func=cmd_watch)

    install = sub.add_parser("install-autostart", help="install XDG autostart entry")
    install.set_defaults(func=cmd_install_autostart)

    uninstall = sub.add_parser("uninstall-autostart", help="remove XDG autostart entry")
    uninstall.set_defaults(func=cmd_uninstall_autostart)

    diagnose = sub.add_parser("diagnose", help="collect read-only diagnostics")
    diagnose.add_argument("--json", action="store_true")
    diagnose.set_defaults(func=cmd_diagnose)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
