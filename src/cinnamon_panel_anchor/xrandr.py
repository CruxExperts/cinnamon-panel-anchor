from __future__ import annotations

import re
import subprocess

from .models import Monitor


_MONITOR_RE = re.compile(
    r"^\s*(?P<index>\d+):\s+(?P<name>\S+)\s+(?P<geometry>\S+)\s+(?P<connector>\S+)\s*$"
)


def parse_listmonitors(output: str) -> list[Monitor]:
    monitors: list[Monitor] = []
    for line in output.splitlines():
        if not line.strip() or line.lstrip().startswith("Monitors:"):
            continue
        match = _MONITOR_RE.match(line)
        if not match:
            continue
        monitors.append(
            Monitor(
                index=int(match.group("index")),
                connector=match.group("connector"),
                primary="*" in match.group("name"),
                geometry=match.group("geometry"),
            )
        )
    return monitors


def list_monitors() -> tuple[list[Monitor], str | None]:
    try:
        proc = subprocess.run(
            ["xrandr", "--listmonitors"],
            check=False,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError:
        return [], "xrandr not found"
    if proc.returncode != 0:
        return [], proc.stderr.strip() or f"xrandr exited {proc.returncode}"
    monitors = parse_listmonitors(proc.stdout)
    if not monitors:
        return [], "xrandr reported no parseable monitors"
    return monitors, None


def query_verbose() -> tuple[str, str | None]:
    try:
        proc = subprocess.run(
            ["xrandr", "--query", "--verbose"],
            check=False,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError:
        return "", "xrandr not found"
    if proc.returncode != 0:
        return proc.stdout, proc.stderr.strip() or f"xrandr exited {proc.returncode}"
    return proc.stdout, None
