"""지정한 두 영상만 제공하는 읽기 전용 로컬 컷 비교 서버."""
from __future__ import annotations

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import mimetypes
import os
from pathlib import Path
import re
import secrets
import stat
import sys
from urllib.parse import urlsplit

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MAX_JSON = 2_000_000


def checked(path: Path) -> Path:
    path = Path(os.path.abspath(path.expanduser()))
    for part in (path, *path.parents):
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("링크·정션 경로는 사용할 수 없음")
    if not path.is_file():
        raise ValueError("일반 파일이 필요함")
    return path


def stamp(path: Path) -> tuple:
    info = checked(path).stat()
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def read_json(path: Path) -> tuple[bytes, dict]:
    checked(path)
    with path.open("rb") as stream:
        raw = stream.read(MAX_JSON + 1)
    if len(raw) > MAX_JSON:
        raise ValueError("JSON 파일이 너무 큼")
    value = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("JSON 객체가 필요함")
    return raw, value


def text(value, label: str, limit=200) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{label} 문자열을 확인할 것")
    return value


def identifier(value) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", value):
        raise ValueError("ID는 영문·숫자·밑줄·하이픈으로 지정할 것")
    return value


def number(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


class Review:
    def __init__(self, path: Path):
        self.path = checked(path)
        before = stamp(self.path)
        raw, config = read_json(self.path)
        if type(config.get("schema")) is not int or config["schema"] != 1:
            raise ValueError("지원하는 설정 schema는 1")
        title = text(config.get("title"), "title")
        versions = config.get("versions")
        if not isinstance(versions, list) or len(versions) != 2:
            raise ValueError("비교할 영상 버전 두 개가 필요함")
        self.media = []
        view_versions = []
        ids = set()
        for version in versions:
            if not isinstance(version, dict):
                raise ValueError("잘못된 버전")
            vid = identifier(version.get("id"))
            if vid in ids:
                raise ValueError("버전 ID 중복")
            ids.add(vid)
            label = text(version.get("label"), "version label")
            filename = Path(text(version.get("file"), "file", 4096))
            video = checked(self.path.parent / filename)
            if video.suffix.lower() not in (".mp4", ".webm", ".ogv"):
                raise ValueError("MP4·WebM·OGV 파일만 지원함")
            original_stamp = stamp(video)
            if original_stamp[2] == 0:
                raise ValueError("빈 영상 파일")
            sha = digest(video)
            if stamp(video) != original_stamp:
                raise ValueError("해시 계산 중 영상이 변경됨")
            self.media.append((video, original_stamp))
            view_versions.append({"id": vid, "label": label, "sha256": sha,
                                  "url": f"media/{len(self.media) - 1}"})
        cuts = config.get("cuts")
        if not isinstance(cuts, list) or not 1 <= len(cuts) <= 200:
            raise ValueError("컷은 1~200개 필요함")
        seen = set()
        view_cuts = []
        for cut in cuts:
            if not isinstance(cut, dict):
                raise ValueError("잘못된 컷")
            cid = identifier(cut.get("id"))
            if cid in seen:
                raise ValueError("컷 ID 중복")
            seen.add(cid)
            ranges = cut.get("ranges")
            if not isinstance(ranges, dict) or set(ranges) != ids:
                raise ValueError("각 컷에 두 버전의 구간이 필요함")
            for times in ranges.values():
                if (not isinstance(times, list) or len(times) != 2 or
                        not all(number(n) for n in times) or not 0 <= times[0] < times[1]):
                    raise ValueError("컷 구간은 0 <= 시작 < 종료인 초 단위 숫자 두 개")
            view_cuts.append({"id": cid, "label": text(cut.get("label"), "cut label"), "ranges": ranges})
        if stamp(self.path) != before:
            raise ValueError("읽는 동안 설정이 변경됨")
        self.config_stamp = before
        self.identity = {"config_sha256": hashlib.sha256(raw).hexdigest(),
                         "videos": [{"id": v["id"], "sha256": v["sha256"]} for v in view_versions]}
        self.manifest = {"schema": 1, "title": title, "review": self.identity,
                         "versions": view_versions, "cuts": view_cuts}

    def unchanged(self):
        if stamp(self.path) != self.config_stamp:
            raise ValueError("설정이 변경됨. 서버를 재시작할 것")
        for path, original in self.media:
            if stamp(path) != original:
                raise ValueError("영상이 변경됨. 서버를 재시작할 것")

    def validate_notes(self, data: dict) -> int:
        if (type(data.get("schema")) is not int or data["schema"] != 1 or
                data.get("review") != self.identity):
            raise ValueError("메모의 설정·영상 해시가 현재 대상과 다름")
        notes = data.get("notes")
        if not isinstance(notes, list) or len(notes) > 500:
            raise ValueError("메모는 최대 500개")
        cuts = {c["id"]: c for c in self.manifest["cuts"]}
        for note in notes:
            if not isinstance(note, dict):
                raise ValueError("잘못된 메모")
            cut = cuts.get(note.get("cut_id"))
            vid = note.get("version_id")
            if cut is None or vid not in cut["ranges"]:
                raise ValueError("메모의 컷·버전이 대상에 없음")
            at = note.get("at_seconds")
            start, end = cut["ranges"][vid]
            if not number(at) or not start <= at <= end:
                raise ValueError("메모 시점이 컷 구간 밖임")
            if note.get("kind") not in ("technical", "visual", "judgment"):
                raise ValueError("메모 종류를 확인할 것")
            text(note.get("text"), "note text", 2000)
        return len(notes)


def byte_range(value: str | None, size: int) -> tuple[int, int, bool]:
    if value is None:
        return 0, size - 1, False
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", value)
    if not match or not any(match.groups()):
        raise ValueError("지원하지 않는 Range")
    first, last = match.groups()
    if first:
        start = int(first)
        end = min(int(last), size - 1) if last else size - 1
    else:
        suffix = int(last)
        if suffix == 0:
            raise ValueError("빈 Range")
        start, end = max(0, size - suffix), size - 1
    if start >= size or start > end:
        raise ValueError("범위 밖 Range")
    return start, end, True


def make_server(review: Review, port=0):
    token = secrets.token_urlsafe(24)
    prefix = "/" + token + "/"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # 접근 토큰이나 영상 경로를 로그에 남기지 않는다.

        def response(self, status, content=b"", kind="text/plain; charset=utf-8", extra=None, head=False):
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(content)))
            self.headers_common()
            for key, value in (extra or {}).items():
                self.send_header(key, value)
            self.end_headers()
            if not head:
                self.wfile.write(content)

        def headers_common(self):
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; script-src 'self'; style-src 'self'; "
                             "media-src 'self'; connect-src 'self'; object-src 'none'; "
                             "base-uri 'none'; frame-ancestors 'none'; form-action 'none'")

        def do_HEAD(self):
            self.get(head=True)

        def do_GET(self):
            self.get()

        def get(self, head=False):
            expected_host = f"127.0.0.1:{self.server.server_port}"
            if (self.headers.get("Host") != expected_host or
                    self.headers.get("Sec-Fetch-Site") == "cross-site"):
                return self.response(403, b"Forbidden", head=head)
            path = urlsplit(self.path).path
            if not path.startswith(prefix):
                return self.response(404, b"Not found", head=head)
            route = path[len(prefix):]
            try:
                review.unchanged()
                if route == "review.json":
                    body = json.dumps(review.manifest, ensure_ascii=False).encode("utf-8")
                    return self.response(200, body, "application/json; charset=utf-8", head=head)
                if route in ("", "app.js", "app.css"):
                    asset = ASSETS / (route or "index.html")
                    kind = {"": "text/html", "app.js": "text/javascript", "app.css": "text/css"}[route]
                    return self.response(200, asset.read_bytes(), kind + "; charset=utf-8", head=head)
                if route in ("media/0", "media/1"):
                    path, original = review.media[int(route[-1])]
                    size = original[2]
                    try:
                        start, end, partial = byte_range(self.headers.get("Range"), size)
                    except ValueError:
                        return self.response(416, extra={"Content-Range": f"bytes */{size}"}, head=head)
                    with path.open("rb") as stream:
                        review.unchanged()
                        self.send_response(206 if partial else 200)
                        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
                        self.send_header("Content-Length", str(end - start + 1))
                        self.send_header("Accept-Ranges", "bytes")
                        if partial:
                            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                        self.headers_common()
                        self.end_headers()
                        if not head:
                            stream.seek(start)
                            remaining = end - start + 1
                            while remaining:
                                data = stream.read(min(256 * 1024, remaining))
                                if not data:
                                    break
                                self.wfile.write(data)
                                remaining -= len(data)
                    return
                self.response(404, b"Not found", head=head)
            except (BrokenPipeError, ConnectionResetError):
                pass
            except (OSError, ValueError):
                self.response(409, "파일이 바뀌었거나 읽을 수 없음. 서버를 재시작하세요.".encode("utf-8"), head=head)

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    return server, f"http://127.0.0.1:{server.server_port}{prefix}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check-config", action="store_true")
    mode.add_argument("--check-notes", type=Path)
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    try:
        if not 0 <= args.port <= 65535:
            raise ValueError("포트 범위는 0~65535")
        review = Review(args.config)
        if args.check_config:
            print(json.dumps(review.manifest, ensure_ascii=False, indent=2))
        elif args.check_notes:
            _, notes = read_json(args.check_notes)
            print(f"메모 검증 통과: {review.validate_notes(notes)}개")
        else:
            server, url = make_server(review, args.port)
            print(url, flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"검토 실패: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
