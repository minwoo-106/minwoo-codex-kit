#!/usr/bin/env python3
"""선택형 Context Mode CLI만 설치. 규칙·설정·훅·npm 생명주기 스크립트는 변경하지 않는다."""
from __future__ import annotations
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request
from install import check_path, InstallError

VERSION = "1.0.169"
INTEGRITY = "94JIaFuLjF9SO2BsGTrbGtyT44K95+9OC8BdbaL/UT76xOkanJLfUR5CzmNw+GELXZQqH4nBrKg9wjBnSFkVnQ=="
URL = f"https://registry.npmjs.org/context-mode/-/context-mode-{VERSION}.tgz"
FILES = ("cli.bundle.mjs", "package.json", "LICENSE")
RUNTIME_NAME = "context-mode-" + VERSION


def probe_node(node):
    # Require the built-in backend: no native addon download/build fallback.
    code = "const {DatabaseSync}=require('node:sqlite');const d=new DatabaseSync(':memory:');d.exec('CREATE VIRTUAL TABLE t USING fts5(body)');d.close();if(+process.versions.node.split('.')[0]<24)process.exit(1)"
    subprocess.run([str(node), "-e", code], check=True, capture_output=True, timeout=20)


def selected_files(blob):
    if base64.b64encode(hashlib.sha512(blob).digest()).decode() != INTEGRITY:
        raise InstallError("Context Mode 배포 무결성 불일치")
    result = {}
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
        for name in FILES:
            matches = [m for m in archive.getmembers() if m.name == "package/" + name]
            if len(matches) != 1 or not matches[0].isfile():
                raise InstallError("배포 파일 누락·중복·링크: " + name)
            result[name] = archive.extractfile(matches[0]).read()
    if json.loads(result["package.json"])["version"] != VERSION:
        raise InstallError("배포 버전 불일치")
    return result


def verify(dest):
    check_path(dest)
    receipt = dest / "installed.json"
    check_path(receipt)
    state = json.loads(receipt.read_text(encoding="utf-8"))
    if state.get("version") != VERSION or state.get("integrity") != INTEGRITY or set(state.get("files", {})) != set(FILES):
        raise InstallError("미관리 또는 다른 버전의 설치 폴더")
    for name, digest in state["files"].items():
        target = dest / name
        check_path(target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise InstallError("설치 파일 로컬 변경: " + name)
    return state


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runtime-root", type=Path)
    p.add_argument("--node", default=shutil.which("node"))
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    if not a.node:
        p.error("Node.js 24+ 필요")
    probe_node(a.node)
    codex = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    root = (a.runtime_root or codex / ".minwoo-codex-kit/runtimes").expanduser().absolute()
    dest = root / RUNTIME_NAME
    check_path(dest)
    if dest.exists():
        verify(dest)
        print("UNCHANGED " + str(dest))
        return
    print(("PLAN " if a.dry_run else "INSTALL ") + str(dest), flush=True)
    if a.dry_run:
        return
    with urllib.request.urlopen(URL, timeout=90) as response:
        blob = response.read(20 * 1024 * 1024 + 1)
    if len(blob) > 20 * 1024 * 1024:
        raise InstallError("배포 다운로드 크기 초과")
    files = selected_files(blob)
    root.mkdir(parents=True, exist_ok=True)
    dest.mkdir()  # exclusive; partial installations are preserved, never overwritten
    for name, data in files.items():
        (dest / name).write_bytes(data)
    receipt = {"version": VERSION, "integrity": INTEGRITY,
               "files": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}}
    (dest / "installed.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    verify(dest)
    print("READY " + str(dest))


if __name__ == "__main__":
    try:
        main()
    except (InstallError, OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as exc:
        raise SystemExit("설치 중단; 기존 파일·미완료 폴더 보존: " + str(exc))
