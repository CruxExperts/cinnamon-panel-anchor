from __future__ import annotations

import argparse
import gzip
import hashlib
import shutil
import stat
import subprocess
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = "CruxExperts/cinnamon-panel-anchor"
TEMPLATE = ROOT / "tools" / "templates" / "install-cinnamon-panel-anchor.sh.in"


def version() -> str:
    return (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bundle_members() -> list[Path]:
    tracked = [
        Path(line)
        for line in subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.splitlines()
        if line
    ]
    included_files = {"VERSION", "LICENSE", "pyproject.toml"}
    included_prefixes = ("src/",)
    return [
        path
        for path in tracked
        if path.as_posix() in included_files
        or any(path.as_posix().startswith(prefix) for prefix in included_prefixes)
    ]


def write_bundle(output_dir: Path, release_version: str) -> Path:
    bundle_name = f"cinnamon-panel-anchor-{release_version}.tar.gz"
    bundle_path = output_dir / bundle_name
    root_name = f"cinnamon-panel-anchor-{release_version}"
    with bundle_path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tar:
                for relative in bundle_members():
                    source = ROOT / relative
                    info = tar.gettarinfo(source, arcname=f"{root_name}/{relative.as_posix()}")
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mtime = 0
                    with source.open("rb") as handle:
                        tar.addfile(info, handle)
    return bundle_path


def render_installer(output_dir: Path, release_version: str, bundle_hash: str) -> Path:
    name = f"install-cinnamon-panel-anchor-{release_version}.sh"
    path = output_dir / name
    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("@@VERSION@@", release_version).replace("@@BUNDLE_SHA256@@", bundle_hash)
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def write_sha256s(output_dir: Path, paths: list[Path]) -> Path:
    sha_path = output_dir / "SHA256SUMS"
    sha_path.write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in sorted(paths, key=lambda item: item.name)),
        encoding="utf-8",
    )
    return sha_path


def install_snippet(release_version: str, installer_hash: str) -> str:
    installer = f"install-cinnamon-panel-anchor-{release_version}.sh"
    url = f"https://github.com/{REPO}/releases/download/v{release_version}/{installer}"
    return "\n".join(
        [
            "```bash",
            "tmp=\"$(mktemp)\"",
            f"curl -fL --proto '=https' --tlsv1.2 -o \"$tmp\" {url}",
            f"printf '%s  %s\\n' '{installer_hash}' \"$tmp\" | sha256sum -c - && sh \"$tmp\"",
            "rm -f \"$tmp\"",
            "```",
            "",
        ]
    )


def build(output_dir: Path) -> dict[str, Path]:
    release_version = version()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    bundle = write_bundle(output_dir, release_version)
    installer = render_installer(output_dir, release_version, sha256(bundle))
    sums = write_sha256s(output_dir, [bundle, installer])
    snippet = output_dir / "README-install-snippet.md"
    snippet.write_text(install_snippet(release_version, sha256(installer)), encoding="utf-8")
    return {"bundle": bundle, "installer": installer, "sha256s": sums, "snippet": snippet}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "release-assets")
    args = parser.parse_args()
    outputs = build(args.output_dir)
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
