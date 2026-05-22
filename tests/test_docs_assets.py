import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UUID = "cinnamon-panel-anchor@cruxexperts.com"


def test_json_files_are_valid():
    for path in ROOT.rglob("*.json"):
        if ".pytest_cache" in path.parts:
            continue
        json.loads(path.read_text(encoding="utf-8"))


def test_readme_image_links_resolve():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme):
        if target.startswith("https://"):
            continue
        assert (ROOT / target).exists(), target


def test_required_docs_exist_and_are_linked():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for relative in (
        "docs/user-guide.md",
        "docs/install.md",
        "docs/troubleshooting.md",
        "docs/architecture.md",
        "docs/ui-design-patterns.md",
        "docs/migration.md",
        "docs/spices-submission.md",
    ):
        assert (ROOT / relative).exists()
        assert relative in readme


def test_ui_design_patterns_reference_required_sources():
    doc = (ROOT / "docs" / "ui-design-patterns.md").read_text(encoding="utf-8")
    for url in (
        "https://developer.gnome.org/hig/guidelines/ui-icons.html",
        "https://developer.gnome.org/hig/patterns/controls/buttons.html",
        "https://developer.gnome.org/hig/patterns/feedback/notifications.html",
        "https://projects.linuxmint.com/reference/git/cinnamon-tutorials/xlet-settings.html",
        "https://projects.linuxmint.com/reference/git/cinnamon-tutorials/write-applet.html",
    ):
        assert url in doc


def test_uuid_consistency_in_release_files():
    paths = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "docs" / "install.md",
        ROOT / "docs" / "spices-submission.md",
        ROOT / "src" / "cinnamon_panel_anchor" / "applet_manager.py",
        ROOT / "src" / "cinnamon_panel_anchor" / "applet" / UUID / "metadata.json",
        ROOT / UUID / "info.json",
    ]
    for path in paths:
        assert UUID in path.read_text(encoding="utf-8")


def test_versions_are_consistent():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    metadata = json.loads((ROOT / "src" / "cinnamon_panel_anchor" / "applet" / UUID / "metadata.json").read_text(encoding="utf-8"))
    info = json.loads((ROOT / UUID / "info.json").read_text(encoding="utf-8"))

    assert f'version = "{metadata["version"]}"' in pyproject
    assert info["version"] == metadata["version"]


def test_applet_metadata_does_not_claim_reserved_launcher_role():
    for path in (
        ROOT / "src" / "cinnamon_panel_anchor" / "applet" / UUID / "metadata.json",
        ROOT / UUID / "files" / UUID / "metadata.json",
    ):
        metadata = json.loads(path.read_text(encoding="utf-8"))
        assert metadata.get("role") != "panellauncher"


def test_generated_mockups_are_labeled_and_no_spices_screenshot_exists():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    spices = (ROOT / "docs" / "spices-submission.md").read_text(encoding="utf-8")

    assert "Generated mockup" in readme
    assert "Do not submit generated mockups" in spices
    assert not (ROOT / UUID / "screenshot.png").exists()


def test_checked_in_spices_files_match_packaged_applet_assets():
    package_root = ROOT / "src" / "cinnamon_panel_anchor" / "applet" / UUID
    spices_root = ROOT / UUID / "files" / UUID
    for relative in ("metadata.json", "applet.js", "settings-schema.json", "stylesheet.css", "icons/anchor-icon.svg"):
        assert (spices_root / relative).read_text(encoding="utf-8") == (package_root / relative).read_text(encoding="utf-8")


def test_applet_declares_vertical_panel_support():
    applet = (ROOT / "src" / "cinnamon_panel_anchor" / "applet" / UUID / "applet.js").read_text(encoding="utf-8")
    assert "setAllowedLayout(Applet.AllowedLayout.BOTH)" in applet


def test_source_never_sets_xrandr_primary():
    offenders = []
    forbidden = "xrandr --" + "primary"
    allowed = {ROOT / "docs" / "migration.md", ROOT / "AGENTS.md", ROOT / "README.md", ROOT / "docs" / "architecture.md"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".venv" in path.parts or ".codex" in path.parts:
            continue
        if path.suffix not in {".py", ".js", ".md", ".toml", ".json"}:
            continue
        if path in allowed:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if forbidden in text:
            offenders.append(path.relative_to(ROOT))
    assert offenders == []
