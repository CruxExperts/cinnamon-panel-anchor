from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .models import Anchor


APP_ID = "cinnamon-panel-anchor"


def xdg_config_home() -> Path:
    value = os.environ.get("XDG_CONFIG_HOME")
    path = Path(value) if value else None
    if path is None or not path.is_absolute():
        return Path.home() / ".config"
    return path


def xdg_state_home() -> Path:
    value = os.environ.get("XDG_STATE_HOME")
    path = Path(value) if value else None
    if path is None or not path.is_absolute():
        return Path.home() / ".local" / "state"
    return path


def config_dir() -> Path:
    return xdg_config_home() / APP_ID


def state_dir() -> Path:
    return xdg_state_home() / APP_ID


def config_path() -> Path:
    return config_dir() / "config.json"


def state_path() -> Path:
    return state_dir() / "state.json"


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)


def load_anchors() -> list[Anchor]:
    data = load_json(config_path(), {"anchors": []})
    anchors = []
    for item in data.get("anchors", []):
        anchors.append(
            Anchor(
                panel_id=str(item["panel_id"]),
                connector=str(item["connector"]),
                edge=str(item["edge"]),
            )
        )
    return anchors


def save_anchors(anchors: list[Anchor]) -> None:
    save_json(
        config_path(),
        {
            "version": 1,
            "anchors": [
                {
                    "panel_id": anchor.panel_id,
                    "connector": anchor.connector,
                    "edge": anchor.edge,
                }
                for anchor in anchors
            ],
        },
    )


def load_state() -> dict[str, Any]:
    return load_json(state_path(), {})


def save_state(state: dict[str, Any]) -> None:
    save_json(state_path(), state)
