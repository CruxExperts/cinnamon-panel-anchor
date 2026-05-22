from __future__ import annotations

import json
import fcntl
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .storage import state_dir
from .version import get_version


MAX_RECORDS = 1000


def log_path() -> Path:
    return state_dir() / "debug.jsonl"


def _log_lock_path() -> Path:
    return state_dir() / "debug.lock"


def _json_default(value: Any) -> str:
    return str(value)


def write_log(
    *,
    level: str,
    component: str,
    event: str,
    command: str | None = None,
    action: str | None = None,
    outcome: str | None = None,
    message: str | None = None,
    context: dict[str, Any] | None = None,
    exception: BaseException | None = None,
) -> Path:
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "level": level,
        "component": component,
        "event": event,
        "version": get_version(),
        "command": command,
        "action": action,
        "outcome": outcome,
        "message": message,
        "context": context or {},
        "exception": None,
    }
    if exception is not None:
        record["exception"] = {
            "type": type(exception).__name__,
            "message": str(exception),
            "traceback": traceback.format_exception_only(type(exception), exception),
        }
    line = json.dumps(record, sort_keys=True, default=_json_default)
    lock = _log_lock_path()
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        existing: list[str] = []
        if path.exists():
            existing = path.read_text(encoding="utf-8").splitlines()
        existing.append(line)
        retained = existing[-MAX_RECORDS:]
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text("\n".join(retained) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    return path


def error_details(exc: BaseException | str | None) -> dict[str, Any] | None:
    if exc is None:
        return None
    if isinstance(exc, BaseException):
        return {"type": type(exc).__name__, "message": str(exc)}
    return {"type": "Error", "message": str(exc)}
