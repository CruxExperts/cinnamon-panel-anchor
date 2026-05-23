from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPLET_UUID = "cinnamon-panel-anchor@cruxexperts.com"
VERSION_PATH = ROOT / "VERSION"
VERSION_FILES = [
    ROOT / "src/cinnamon_panel_anchor/_version.txt",
    ROOT / "src/cinnamon_panel_anchor/applet" / APPLET_UUID / "metadata.json",
    ROOT / APPLET_UUID / "info.json",
    ROOT / APPLET_UUID / "files" / APPLET_UUID / "metadata.json",
]
APPLET_JS_FILES = [
    ROOT / "src/cinnamon_panel_anchor/applet" / APPLET_UUID / "applet.js",
    ROOT / APPLET_UUID / "files" / APPLET_UUID / "applet.js",
]


def version() -> str:
    return VERSION_PATH.read_text(encoding="utf-8").strip()


def update_pyproject(expected: str, write: bool) -> bool:
    path = ROOT / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r'^version = "[^"]+"', f'version = "{expected}"', text, count=1, flags=re.MULTILINE)
    if write and updated != text:
        path.write_text(updated, encoding="utf-8")
    return updated == text


def update_json_version(path: Path, expected: str, write: bool) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    old = data.get("version")
    data["version"] = expected
    if write and old != expected:
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return old == expected


def update_text(path: Path, expected: str, write: bool) -> bool:
    old = path.read_text(encoding="utf-8").strip()
    if write and old != expected:
        path.write_text(expected + "\n", encoding="utf-8")
    return old == expected


def update_applet_js(path: Path, expected: str, write: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r'const VERSION = "[^"]+";', f'const VERSION = "{expected}";', text, count=1)
    if write and updated != text:
        path.write_text(updated, encoding="utf-8")
    return updated == text


def update_default_version(expected: str, write: bool) -> bool:
    path = ROOT / "src/cinnamon_panel_anchor/version.py"
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(r'^DEFAULT_VERSION = "[^"]+"', f'DEFAULT_VERSION = "{expected}"', text, count=1, flags=re.MULTILINE)
    if count != 1:
        return False
    if write and updated != text:
        path.write_text(updated, encoding="utf-8")
    return updated == text


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()

    expected = version()
    checks = [("pyproject.toml", update_pyproject(expected, args.write)), ("src/cinnamon_panel_anchor/version.py", update_default_version(expected, args.write))]
    for path in VERSION_FILES:
        if path.suffix == ".json":
            checks.append((str(path.relative_to(ROOT)), update_json_version(path, expected, args.write)))
        else:
            checks.append((str(path.relative_to(ROOT)), update_text(path, expected, args.write)))
    for path in APPLET_JS_FILES:
        checks.append((str(path.relative_to(ROOT)), update_applet_js(path, expected, args.write)))

    failed = [name for name, ok in checks if not ok]
    if failed and args.check:
        for name in failed:
            print(f"version mismatch: {name}")
        return 1
    if failed:
        print(f"updated {len(failed)} version surface(s) to {expected}")
    else:
        print(f"all version surfaces match {expected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
