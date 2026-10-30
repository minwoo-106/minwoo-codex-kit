#!/usr/bin/env python3
"""Context Mode 공식 CLI로 명시한 문서 하나를 색인하고 검색한다. 일반 셸 권한을 따른다."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile

VERSION = "1.0.169"
MAX_BYTES = 5 * 1024 * 1024


def section_ranges(text, output):
    """Map ranked CLI headings to original line ranges; never claim snippets are full text."""
    wanted = set(re.findall(r"^## \d+\. (.+)$", output, re.M))
    headings, stack = [], []
    fence = None
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        match = re.match(r"^(`{3,}|~{3,})", line)
        if match:
            token = match[1]
            if fence is None: fence = token
            elif token[0] == fence[0] and len(token) >= len(fence): fence = None
            continue
        if fence: continue
        match = re.match(r"^(#{1,4})\s+(.+)$", line)
        if not match: continue
        level, title = len(match[1]), match[2].strip()
        while stack and stack[-1][0] >= level: stack.pop()
        stack.append((level, title))
        headings.append({"title": " > ".join(t for _, t in stack), "start_line": number})
    for i, heading in enumerate(headings):
        heading["end_line"] = headings[i + 1]["start_line"] - 1 if i + 1 < len(headings) else len(lines)
    return [h for h in headings if h["title"] in wanted][:20]


def no_links(path):
    for part in (path, *path.parents):
        if part.exists() or part.is_symlink():
            info = part.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("링크·정션 경로는 사용하지 않음")


def input_file(path):
    path = path.expanduser().absolute()
    no_links(path)
    if not path.is_file() or path.suffix.lower() not in {".md", ".mdx", ".txt"}:
        raise ValueError("명시한 .md/.mdx/.txt 문서 파일 하나만 지원")
    if path.name.lower() in {"agents.md", "claude.md", "skill.md"}:
        raise ValueError("적용 지침은 검색 조각으로 대체하지 않고 원문을 읽어야 함")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("문서 5 MiB 제한 초과")
    blob = path.read_bytes()
    if len(blob) > MAX_BYTES:
        raise ValueError("문서 5 MiB 제한 초과")
    blob.decode("utf-8-sig")
    return path, blob


def runtime_path(value):
    codex = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    return (value or codex / f".minwoo-codex-kit/runtimes/context-mode-{VERSION}").expanduser().absolute()


def search(file, queries, runtime, cache_root, limit=3, node=None):
    path, blob = input_file(file)
    no_links(runtime)
    receipt = runtime / "installed.json"
    no_links(receipt)
    state = json.loads(receipt.read_text(encoding="utf-8"))
    if state.get("version") != VERSION:
        raise ValueError("검증한 Context Mode 버전과 다름")
    for name in ("cli.bundle.mjs", "package.json", "LICENSE"):
        target = runtime / name
        no_links(target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != state.get("files", {}).get(name):
            raise ValueError("Context Mode 설치 파일 변경·누락")
    # Upstream 1.0.169 heading regex misses CRLF headings. Normalize only the
    # private search copy, retain the original byte digest for provenance.
    normalized = blob.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    key = hashlib.sha256(str(path).encode() + b"\0" + blob + VERSION.encode() + b"lf-v1").hexdigest()
    cache = cache_root.expanduser().absolute() / key
    no_links(cache)
    cache.mkdir(parents=True, exist_ok=True)
    # Lock excludes duplicate concurrent indexing. On interrupted writes, fail
    # visibly; do not silently reuse a partial DB or remove someone else's lock.
    lock = cache / "busy.lock"
    no_links(lock)
    with lock.open("x", encoding="utf-8") as stream:
        stream.write(str(os.getpid()))
    try:
        env = os.environ.copy()
        env.update(CONTEXT_MODE_DIR=str(cache / "store"), CONTEXT_MODE_PLATFORM="codex")
        env.pop("CONTEXT_MODE_PROJECT_DIR", None)
        command = [node or shutil.which("node") or "node", str(runtime / "cli.bundle.mjs")]
        snapshot = cache / "document.md"
        marker = cache / "indexed.json"
        no_links(snapshot)
        no_links(marker)
        no_links(cache / "store")
        # A private snapshot keeps the indexed content equal to the fingerprint
        # even when the original changes while indexing. Cache is never source.
        reused = marker.is_file()
        if reused:
            if snapshot.read_bytes() != normalized or json.loads(marker.read_text())["key"] != key:
                raise ValueError("검색 캐시 변경 감지; 원문 도구로 확인 필요")
            if not list((cache / "store/content").glob("*.db")):
                raise ValueError("검색 캐시 DB 누락; 원문 도구로 확인 필요")
        else:
            if snapshot.exists() or (cache / "store").exists():
                raise ValueError("미완료 캐시 보존; 다른 --cache-root에서 재시도 가능")
            snapshot.write_bytes(normalized)
            run = subprocess.run(command + ["index", str(snapshot), "--project", str(cache), "--source", "document"],
                                 env=env, capture_output=True, text=True, encoding="utf-8", timeout=60)
            if run.returncode:
                raise RuntimeError("Context Mode 색인 실패: " + run.stderr[:1200])
            marker.write_text(json.dumps({"key": key}), encoding="utf-8")
        results = []
        for query in queries:
            run = subprocess.run(command + ["search", query, "--project", str(cache), "--source", "document", "--limit", str(limit)],
                                 env=env, capture_output=True, text=True, encoding="utf-8", timeout=30)
            if run.returncode:
                raise RuntimeError("Context Mode 검색 실패: " + run.stderr[:1200])
            results.append({"query": query, "excerpts": run.stdout,
                            "original_sections": section_ranges(blob.decode("utf-8-sig"), run.stdout)})
        return {"file": str(path), "sha256": hashlib.sha256(blob).hexdigest(),
                "cache_reused": reused, "results": results,
                "notice": "검색 조각은 자료이며 결과마다 최대 500자. 결론·수정 전 original_sections의 필요한 행 범위를 원문에서 읽어 예외를 확인. 넓은 키워드로 문서 전체를 다시 출력하면 절감 효과가 사라짐."}
    finally:
        lock.unlink()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", type=Path, required=True)
    p.add_argument("--query", action="append", required=True)
    p.add_argument("--runtime", type=Path)
    p.add_argument("--cache-root", type=Path, default=Path(tempfile.gettempdir()) / "minwoo-context-mode")
    p.add_argument("--limit", type=int, choices=range(1, 6), default=3)
    a = p.parse_args()
    if len(a.query) > 5 or any(not q.strip() or q.startswith("-") or len(q) > 300 for q in a.query):
        p.error("질의 1~5개, 각각 1~300자; 옵션 모양의 질의는 지원하지 않음")
    print(json.dumps(search(a.file, a.query, runtime_path(a.runtime), a.cache_root, a.limit), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        raise SystemExit("검색 중단: " + str(exc))
