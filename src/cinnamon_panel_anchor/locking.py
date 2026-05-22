from __future__ import annotations

import json
import os
import fcntl
import time
from pathlib import Path
from typing import Any

from .storage import state_dir


class LockRefused(RuntimeError):
    def __init__(self, path: Path, metadata: dict[str, Any]):
        self.path = path
        self.metadata = metadata
        super().__init__(f"another cinnamon-panel-anchor action is running: {metadata}")


class CommandLock:
    def __init__(self, command: str):
        self.command = command
        self.path = lock_path()
        self.acquired = False

    def __enter__(self) -> "CommandLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        metadata = {"pid": os.getpid(), "command": self.command, "timestamp": time.time()}
        self._handle = self.path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(self._handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            current = _read_metadata(self.path)
            self._handle.close()
            raise LockRefused(self.path, current) from exc
        self._handle.seek(0)
        self._handle.truncate()
        json.dump(metadata, self._handle, sort_keys=True)
        self._handle.write("\n")
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self.acquired = True
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self.acquired:
            return
        fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
        self._handle.close()


def lock_path() -> Path:
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if runtime and Path(runtime).is_absolute():
        return Path(runtime) / "cinnamon-panel-anchor.lock"
    return state_dir() / "cinnamon-panel-anchor.lock"


def _read_metadata(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"pid": None, "command": "unknown", "timestamp": 0}
    return data if isinstance(data, dict) else {"pid": None, "command": "unknown", "timestamp": 0}
