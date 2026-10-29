"""영상·메모의 대상 일치와 읽기 전용 서버 범위를 검증한다."""
import copy
import http.client
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


video = module("serve_review", "skills/minwoo-video-review/scripts/serve_review.py")


class FilesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("KIT_TEST_ROOT"))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, path, data=b"example"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path


class ReviewTests(FilesTest):
    def setUp(self):
        super().setUp()
        self.put(self.root / "before.webm", b"0123456789")
        self.put(self.root / "after.webm", b"abcdefghij")
        self.path = self.root / "review.json"
        self.config = {"schema": 1, "title": "sample",
                       "versions": [{"id": "before", "label": "Before", "file": "before.webm"},
                                    {"id": "after", "label": "After", "file": "after.webm"}],
                       "cuts": [{"id": "opening", "label": "Opening",
                                 "ranges": {"before": [1, 2], "after": [3, 4]}}]}
        self.save_config()

    def save_config(self):
        self.path.write_text(json.dumps(self.config), encoding="utf-8")

    def note(self, review):
        return {"schema": 1, "review": copy.deepcopy(review.identity), "notes": [
            {"cut_id": "opening", "version_id": "after", "at_seconds": 3.5,
             "kind": "visual", "text": "Check subtitle"}]}

    def test_note_matches_specific_version_range(self):
        review = video.Review(self.path)
        note = self.note(review)
        self.assertEqual(review.validate_notes(note), 1)
        note["notes"][0]["at_seconds"] = 1.5
        with self.assertRaises(ValueError):
            review.validate_notes(note)

    def test_old_notes_rejected_after_media_or_config_change(self):
        review = video.Review(self.path)
        note = self.note(review)
        self.put(self.root / "after.webm", b"new video")
        with self.assertRaises(ValueError):
            video.Review(self.path).validate_notes(note)
        self.put(self.root / "after.webm", b"abcdefghij")
        self.path.write_text(self.path.read_text() + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            video.Review(self.path).validate_notes(note)

    def test_malformed_notes_rejected(self):
        review = video.Review(self.path)
        for field, bad in [("cut_id", "missing"), ("version_id", "missing"),
                           ("kind", "approved"), ("text", ""), ("text", "x" * 2001),
                           ("at_seconds", float("nan")), ("at_seconds", True)]:
            with self.subTest(field=field, bad=str(bad)[:20]):
                note = self.note(review)
                note["notes"][0][field] = bad
                with self.assertRaises(ValueError):
                    review.validate_notes(note)

    def test_invalid_config_ranges(self):
        for bad in ([2, 1], [-1, 2], [0, float("inf")], [True, 2], [0], "0,2"):
            with self.subTest(bad=bad):
                self.config["cuts"][0]["ranges"]["before"] = bad
                self.save_config()
                with self.assertRaises(ValueError):
                    video.Review(self.path)

    def test_duplicate_ids_and_missing_range(self):
        original = copy.deepcopy(self.config)
        for mutation in ("versions", "cuts", "missing"):
            with self.subTest(mutation=mutation):
                self.config = copy.deepcopy(original)
                if mutation == "versions":
                    self.config["versions"][1]["id"] = "before"
                elif mutation == "cuts":
                    self.config["cuts"].append(copy.deepcopy(self.config["cuts"][0]))
                else:
                    del self.config["cuts"][0]["ranges"]["after"]
                self.save_config()
                with self.assertRaises(ValueError):
                    video.Review(self.path)

    def test_missing_empty_and_wrong_extension(self):
        with self.assertRaises(FileNotFoundError):
            video.Review(self.root / "missing.json")
        self.put(self.root / "before.webm", b"")
        with self.assertRaises(ValueError):
            video.Review(self.path)
        self.config["versions"][0]["file"] = "secret.txt"
        self.put(self.root / "secret.txt")
        self.save_config()
        with self.assertRaises(ValueError):
            video.Review(self.path)

    def test_linked_media_directory_is_rejected(self):
        media = self.root / "media"
        media.mkdir()
        self.put(media / "before.webm")
        link = self.root / "linked"
        try:
            link.symlink_to(media, target_is_directory=True)
        except OSError:
            if os.name != "nt":
                self.skipTest("Host cannot create directory links")
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(media)], capture_output=True)
            if result.returncode:
                self.skipTest("Host cannot create junctions")
        self.config["versions"][0]["file"] = "linked/before.webm"
        self.save_config()
        with self.assertRaises(ValueError):
            video.Review(self.path)

    def test_server_scope_ranges_host_and_read_only(self):
        review = video.Review(self.path)
        server, url = video.make_server(review)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        prefix = url.split(str(server.server_port), 1)[1]
        def request(path, headers=None, method="GET"):
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
            conn.request(method, path, headers=headers or {})
            response = conn.getresponse()
            result = response.status, dict(response.getheaders()), response.read()
            conn.close()
            return result
        try:
            status, headers, body = request(prefix + "review.json")
            self.assertEqual(status, 200)
            self.assertNotIn(str(self.root).encode(), body)
            self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
            self.assertEqual(request(prefix + "media/0")[2], b"0123456789")
            for value, expected in [("bytes=2-4", b"234"), ("bytes=-3", b"789"), ("bytes=7-", b"789")]:
                status, headers, body = request(prefix + "media/0", {"Range": value})
                self.assertEqual(status, 206)
                self.assertEqual(body, expected)
                self.assertEqual(int(headers["Content-Length"]), len(expected))
            for value in ("bytes=99-", "bytes=3-1", "bytes=-0", "bytes=0-1,3-4"):
                self.assertEqual(request(prefix + "media/0", {"Range": value})[0], 416)
            self.assertEqual(request(prefix + "media/0", method="HEAD")[2], b"")
            self.assertEqual(request(prefix + "media/0", {"Host": "evil.invalid"})[0], 403)
            self.assertEqual(request(prefix, {"Sec-Fetch-Site": "cross-site"})[0], 403)
            for invalid in ("/", "/review.json", prefix + "../review.json", prefix + "%2e%2e/secret.txt", prefix + "media/2"):
                self.assertEqual(request(invalid)[0], 404)
            self.assertEqual(request(prefix, method="POST")[0], 501)
            self.put(self.root / "after.webm", b"changed")
            self.assertEqual(request(prefix + "review.json")[0], 409)
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=3)

    def test_byte_ranges_expected_offsets(self):
        self.assertEqual(video.byte_range(None, 10), (0, 9, False))
        self.assertEqual(video.byte_range("bytes=0-99", 10), (0, 9, True))
        self.assertEqual(video.byte_range("bytes=-99", 10), (0, 9, True))


if __name__ == "__main__":
    unittest.main()
