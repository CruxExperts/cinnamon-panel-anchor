from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPLET_UUID = "cinnamon-panel-anchor@cruxexperts.com"
PRIVATE_PATTERNS = [
    re.compile("/home/" + "cptnfren"),
    re.compile("/mnt/data/" + "devzone"),
    re.compile(r"BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY"),
]


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    check(version == "0.2.1", "VERSION must be 0.2.1", failures)

    for path in [
        ROOT / "src/cinnamon_panel_anchor/applet" / APPLET_UUID / "metadata.json",
        ROOT / APPLET_UUID / "info.json",
        ROOT / APPLET_UUID / "files" / APPLET_UUID / "metadata.json",
        ROOT / "src/cinnamon_panel_anchor/applet" / APPLET_UUID / "settings-schema.json",
    ]:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "version" in data:
            check(data["version"] == version, f"{path.relative_to(ROOT)} version mismatch", failures)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check("0.2.1" in readme, "README must mention visible version 0.2.1", failures)
    check("Crux Experts LLC" in readme, "README must include Crux Experts LLC", failures)
    check("Slavic Kozyuk" in readme, "README must include maintainer", failures)
    check("https://github.com/CruxExperts" in readme, "README must include GitHub profile", failures)
    check("https://www.cruxexperts.com" in readme, "README must include company backlink", failures)
    check("docs/assets/brand/panel-anchor-logo.svg" in readme, "README must include project logo", failures)

    for path in [
        ROOT / "SECURITY.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "docs/VERSIONING.md",
        ROOT / "docs/PUBLISHING_CHECKLIST.md",
        ROOT / "docs/assets/brand/panel-anchor-logo.svg",
        ROOT / "docs/assets/brand/anchor-icon.svg",
        ROOT / ".github/workflows/ci.yml",
        ROOT / ".github/dependabot.yml",
        ROOT / ".github/pull_request_template.md",
    ]:
        check(path.exists(), f"missing {path.relative_to(ROOT)}", failures)

    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, stdout=subprocess.PIPE, check=True).stdout.splitlines()
    for name in tracked:
        path = ROOT / name
        if not path.is_file() or path.suffix in {".png", ".svg"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in PRIVATE_PATTERNS:
            check(not pattern.search(text), f"private pattern in {name}", failures)
        if name.endswith(".py") or name.endswith(".js"):
            forbidden = "xrandr --" + "primary"
            check(forbidden not in text, f"forbidden xrandr primary call in {name}", failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
