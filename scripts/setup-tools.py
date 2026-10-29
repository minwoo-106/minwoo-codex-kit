#!/usr/bin/env python3
"""선택 도구를 별도 런타임에 설치한다. 기존 프로젝트·전역 설정은 수정하지 않는다."""
from __future__ import annotations
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from install import check_path, InstallError

SOURCE = Path(__file__).absolute().parent.parent / "tooling"
NPM_URL = "https://registry.npmjs.org/npm/-/npm-11.6.2.tgz"
NPM_SHA512 = "7iKzNfy8lWYs3zq4oFPa8EXZz5xt9gQNKJZau3B1ErLBb6bF7sBJ00x09485DOvRT2l5Gerbl3VlZNT57MxJVA=="


def source_files():
    result = {}
    for path in sorted(SOURCE.rglob("*")):
        check_path(path)
        if path.is_file():
            relative = path.relative_to(SOURCE).as_posix()
            if any(x in path.parts for x in ("node_modules", "__pycache__", ".pytest_cache")):
                raise InstallError("tooling에 실행 결과/의존성 폴더가 섞여 있음")
            result[relative] = path.read_bytes()
    if "package-lock.json" not in result or "requirements.txt" not in result:
        raise InstallError("도구 잠금 파일 없음")
    return result


def file_hashes(files):
    return {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}


def identity(hashes, node_version):
    payload = {"files": hashes, "python": list(sys.version_info[:2]),
               "platform": sys.platform, "node": node_version, "npm": NPM_SHA512}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:20]


def extract_npm(blob, target):
    if base64.b64encode(hashlib.sha512(blob).digest()).decode() != NPM_SHA512:
        raise InstallError("npm 다운로드 무결성 불일치")
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or ".." in path.parts or not path.parts
                    or path.parts[0] != "package" or "\\" in member.name
                    or ":" in member.name or not (member.isdir() or member.isfile())):
                raise InstallError("npm 압축에 허용하지 않은 경로/링크가 있음")
        for member in members:
            path = target.joinpath(*PurePosixPath(member.name).parts[1:])
            check_path(path)
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb") as stream:
                    stream.write(archive.extractfile(member).read())


def run(command, cwd):
    subprocess.run([str(x) for x in command], cwd=cwd, check=True)


def verify_existing(dest, hashes):
    receipt = dest / "installed.json"
    if not receipt.is_file():
        raise InstallError("기존 런타임이 미완료/미관리 상태임. 덮어쓰지 않음: " + str(dest))
    check_path(receipt)
    state = json.loads(receipt.read_text(encoding="utf-8"))
    if state.get("files") != hashes:
        raise InstallError("기존 런타임 영수증과 원본이 다름")
    for name, expected in hashes.items():
        path = dest / name
        check_path(path)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise InstallError("런타임 파일의 로컬 수정 발견: " + name)


def check_runtime_files(dest):
    required = [dest / "npm/bin/npm-cli.js",
                dest / ("python/Scripts/python.exe" if os.name == "nt" else "python/bin/python")]
    for path in required:
        # A POSIX venv may intentionally link its interpreter.
        if not path.is_file():
            raise InstallError("설치 도구 누락: " + str(path))
    dependencies = json.loads((dest / "package.json").read_text(encoding="utf-8"))["dependencies"]
    for name, version in dependencies.items():
        path = dest / "node_modules" / name / "package.json"
        check_path(path)
        if not path.is_file() or json.loads(path.read_text(encoding="utf-8")).get("version") != version:
            raise InstallError("설치 패키지 누락/버전 변경: " + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error("선택 도구에는 Python 3.11 이상이 필요함")
    node = shutil.which("node")
    if not node:
        parser.error("Node.js 22 이상이 필요함")
    version = subprocess.check_output([node, "--version"], text=True).strip()
    if int(version.lstrip("v").split(".")[0]) < 22:
        parser.error("Node.js 22 이상이 필요함")
    files = source_files()
    hashes = file_hashes(files)
    codex = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    root = (args.runtime_root or codex / ".minwoo-codex-kit" / "runtimes").expanduser().absolute()
    check_path(root)
    dest = root / identity(hashes, version)
    check_path(dest)
    if dest.exists():
        verify_existing(dest, hashes)
        check_runtime_files(dest)
        print("UNCHANGED " + str(dest))
        return
    print(("PLAN " if args.dry_run else "INSTALL ") + str(dest), flush=True)
    if args.dry_run:
        return
    # mkdir is exclusive: concurrent installs cannot both own this destination.
    root.mkdir(parents=True, exist_ok=True)
    dest.mkdir()
    (dest / "incomplete.json").write_text(json.dumps({"files": hashes}), encoding="utf-8")
    for name, data in files.items():
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    with urllib.request.urlopen(NPM_URL, timeout=90) as response:
        blob = response.read()
    extract_npm(blob, dest / "npm")
    # Use a private, empty npm user config; do not alter the user's config.
    npm_config = dest / "empty.npmrc"
    npm_config.write_text("", encoding="utf-8")
    run([node, dest / "npm/bin/npm-cli.js", "ci", "--ignore-scripts", "--no-fund",
         "--no-audit", "--registry=https://registry.npmjs.org", "--userconfig", npm_config,
         "--cache", dest / "npm-cache"], dest)
    run([sys.executable, "-m", "venv", dest / "python"], dest)
    python = dest / ("python/Scripts/python.exe" if os.name == "nt" else "python/bin/python")
    run([python, "-m", "pip", "--isolated", "install", "--disable-pip-version-check", "--no-cache-dir",
         "--index-url", "https://pypi.org/simple", "--only-binary=:all:",
         "--require-hashes", "-r", dest / "requirements.txt"], dest)
    run([python, "-m", "pip", "check"], dest)
    check_runtime_files(dest)
    (dest / "installed.json").write_text(
        json.dumps({"files": hashes, "node": version, "schema": 1}, indent=2), encoding="utf-8")
    (dest / "incomplete.json").unlink()
    print("READY " + str(dest), flush=True)


if __name__ == "__main__":
    try:
        main()
    except (InstallError, OSError, ValueError, subprocess.SubprocessError) as exc:
        raise SystemExit("도구 설치 중단. 기존 파일을 덮어쓰지 않음; 미완료 폴더는 진단용으로 유지: " + str(exc))
