import hashlib
import importlib.util
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_release_assets", ROOT / "tools" / "build_release_assets.py")
build_release_assets = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(build_release_assets)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def test_release_assets_are_versioned_and_checksummed(tmp_path):
    outputs = build_release_assets.build(tmp_path)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

    assert outputs["bundle"].name == f"cinnamon-panel-anchor-{version}.tar.gz"
    assert outputs["installer"].name == f"install-cinnamon-panel-anchor-{version}.sh"
    assert outputs["sha256s"].name == "SHA256SUMS"

    sums = outputs["sha256s"].read_text(encoding="utf-8")
    for path in (outputs["bundle"], outputs["installer"]):
        assert f"{_sha256(path)}  {path.name}" in sums


def test_readme_install_snippet_matches_generated_installer_checksum(tmp_path):
    outputs = build_release_assets.build(tmp_path)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs_install = (ROOT / "docs" / "install.md").read_text(encoding="utf-8")
    installer_hash = _sha256(outputs["installer"])

    assert installer_hash in readme
    assert installer_hash in docs_install
    assert "sha256sum -c - && sh \"$tmp\"" in readme
    assert "sha256sum -c - && sh \"$tmp\"" in docs_install


def test_install_snippet_gates_execution_on_checksum_success(tmp_path):
    snippet = build_release_assets.install_snippet("0.2.2", "expected")
    script = "\n".join(line for line in snippet.splitlines() if line and not line.startswith("```"))
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    marker = tmp_path / "ran"
    (fake_bin / "curl").write_text(
        "#!/bin/sh\nout=''\nwhile [ $# -gt 0 ]; do if [ \"$1\" = '-o' ]; then shift; out=\"$1\"; fi; shift || exit 1; done\nprintf bad > \"$out\"\n",
        encoding="utf-8",
    )
    (fake_bin / "curl").chmod(0o755)
    (fake_bin / "sha256sum").write_text("#!/bin/sh\ncat >/dev/null\nexit 1\n", encoding="utf-8")
    (fake_bin / "sha256sum").chmod(0o755)
    (fake_bin / "sh").write_text(f"#!/bin/sh\nprintf ran > {marker}\n", encoding="utf-8")
    (fake_bin / "sh").chmod(0o755)

    subprocess.run(
        ["/bin/sh", "-c", script],
        env={"PATH": f"{fake_bin}:/usr/bin:/bin"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert not marker.exists()


def test_installer_template_uses_fixed_release_urls_and_safe_install_shape():
    text = (ROOT / "tools" / "templates" / "install-cinnamon-panel-anchor.sh.in").read_text(encoding="utf-8")

    assert "set -eu" in text
    assert "trap cleanup EXIT HUP INT TERM" in text
    assert "sudo" not in text
    assert "curl | sh" not in text
    assert "latest/download" not in text
    assert "raw.githubusercontent.com" not in text
    assert "refs/heads" not in text
    assert "releases/download/v${VERSION}" in text
    assert "sha256sum -c -" in text
    assert "install-applet --backend-source \"$VERSION_DIR/src\" --enable" in text
    assert "CINNAMON_PANEL_ANCHOR_BACKEND_SOURCE" in text


def test_generated_installer_rejects_wrong_version_bundle(tmp_path):
    outputs = build_release_assets.build(tmp_path)
    installer = outputs["installer"]
    bundle_name = outputs["bundle"].name
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    download_dir = tmp_path / "download"
    download_dir.mkdir()
    bad_root = download_dir / "bundle-root"
    bad_root.mkdir()
    (bad_root / "VERSION").write_text("0.0.0\n", encoding="utf-8")
    (bad_root / "src").mkdir()
    (download_dir / "src").mkdir(exist_ok=True)
    bad_bundle = download_dir / bundle_name
    subprocess.run(["tar", "-czf", str(bad_bundle), "-C", str(download_dir), "bundle-root"], check=True)

    gsettings = fake_bin / "gsettings"
    gsettings.write_text("#!/bin/sh\nprintf '%s\\n' org.cinnamon\n", encoding="utf-8")
    gsettings.chmod(0o755)
    xrandr = fake_bin / "xrandr"
    xrandr.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    xrandr.chmod(0o755)
    curl = fake_bin / "curl"
    curl.write_text(
        "#!/bin/sh\nout=''\nwhile [ $# -gt 0 ]; do if [ \"$1\" = '-o' ]; then shift; out=\"$1\"; fi; shift || exit 1; done\ncp '%s' \"$out\"\n"
        % bad_bundle,
        encoding="utf-8",
    )
    curl.chmod(0o755)

    patched = tmp_path / installer.name
    text = installer.read_text(encoding="utf-8")
    text = text.replace(build_release_assets.sha256(outputs["bundle"]), build_release_assets.sha256(bad_bundle))
    patched.write_text(text, encoding="utf-8")
    patched.chmod(0o755)

    result = subprocess.run(
        ["sh", str(patched)],
        env={"PATH": f"{fake_bin}:/usr/bin:/bin", "HOME": str(tmp_path / "home")},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode != 0
    assert "expected version" in result.stderr


def test_generated_installer_rejects_checksum_mismatch(tmp_path):
    outputs = build_release_assets.build(tmp_path)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    bad_bundle = tmp_path / "bad.tar.gz"
    bad_bundle.write_text("not the release bundle", encoding="utf-8")

    _write_fake_prereq_commands(fake_bin)
    _write_fake_curl(fake_bin / "curl", bad_bundle)

    result = subprocess.run(
        ["sh", str(outputs["installer"])],
        env={"PATH": f"{fake_bin}:/usr/bin:/bin", "HOME": str(tmp_path / "home")},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode != 0
    assert "sha256sum" in result.stderr or "FAILED" in result.stderr


def test_generated_installer_fails_when_bundle_download_is_missing(tmp_path):
    outputs = build_release_assets.build(tmp_path)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_fake_prereq_commands(fake_bin)
    curl = fake_bin / "curl"
    curl.write_text("#!/bin/sh\nexit 22\n", encoding="utf-8")
    curl.chmod(0o755)

    result = subprocess.run(
        ["sh", str(outputs["installer"])],
        env={"PATH": f"{fake_bin}:/usr/bin:/bin", "HOME": str(tmp_path / "home")},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode != 0


def _write_fake_prereq_commands(fake_bin: Path) -> None:
    gsettings = fake_bin / "gsettings"
    gsettings.write_text("#!/bin/sh\nprintf '%s\\n' org.cinnamon\n", encoding="utf-8")
    gsettings.chmod(0o755)
    xrandr = fake_bin / "xrandr"
    xrandr.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    xrandr.chmod(0o755)


def _write_fake_curl(path: Path, source: Path) -> None:
    path.write_text(
        "#!/bin/sh\nout=''\nwhile [ $# -gt 0 ]; do if [ \"$1\" = '-o' ]; then shift; out=\"$1\"; fi; shift || exit 1; done\ncp '%s' \"$out\"\n"
        % source,
        encoding="utf-8",
    )
    path.chmod(0o755)
