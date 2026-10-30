import base64
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


setup = load("context_setup", ROOT / "scripts/setup-context-mode.py")
search = load("context_search_tests", ROOT / "skills/diagnosing-bugs/scripts/context_search.py")


class ContextModeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("KIT_TEST_ROOT"))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def runtime(self):
        dest = self.root / "runtime"
        dest.mkdir()
        files = {"cli.bundle.mjs": b"synthetic", "package.json": b"{}", "LICENSE": b"test"}
        for name, data in files.items(): (dest / name).write_bytes(data)
        state = {"version": setup.VERSION, "integrity": setup.INTEGRITY,
                 "files": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}}
        (dest / "installed.json").write_text(json.dumps(state))
        return dest

    def test_install_repeat_and_local_edit(self):
        dest = self.runtime()
        before = (dest / "cli.bundle.mjs").stat().st_mtime_ns
        setup.verify(dest)
        self.assertEqual(before, (dest / "cli.bundle.mjs").stat().st_mtime_ns)
        (dest / "cli.bundle.mjs").write_text("edited")
        with self.assertRaises(setup.InstallError): setup.verify(dest)

    def test_dry_run_does_not_download_or_write(self):
        with patch.object(sys, "argv", ["setup", "--runtime-root", str(self.root / "absent"), "--node", "node", "--dry-run"]), patch.object(setup, "probe_node"), patch.object(setup.urllib.request, "urlopen") as download:
            setup.main()
        download.assert_not_called()
        self.assertFalse((self.root / "absent").exists())

    def test_bad_archive_integrity(self):
        with self.assertRaises(setup.InstallError): setup.selected_files(b"wrong")

    def test_selected_archive_files_only_and_links_rejected(self):
        for link in (False, True):
            stream = io.BytesIO()
            with tarfile.open(fileobj=stream, mode="w:gz") as archive:
                for name in setup.FILES:
                    data = json.dumps({"version": setup.VERSION}).encode() if name == "package.json" else b"test"
                    member = tarfile.TarInfo("package/" + name)
                    member.size = len(data)
                    if link and name == "cli.bundle.mjs": member.type = tarfile.SYMTYPE; member.linkname = "../../outside"
                    archive.addfile(member, io.BytesIO(data))
                # Unselected files, including traversal, are never extracted.
                extra = tarfile.TarInfo("package/../../outside"); extra.size = 1
                archive.addfile(extra, io.BytesIO(b"x"))
            blob = stream.getvalue()
            with patch.object(setup, "INTEGRITY", base64.b64encode(hashlib.sha512(blob).digest()).decode()):
                if link:
                    with self.assertRaises(setup.InstallError): setup.selected_files(blob)
                else:
                    self.assertEqual(set(setup.selected_files(blob)), set(setup.FILES))
        self.assertFalse((self.root.parent / "outside").exists())

    def test_rule_and_non_document_refused(self):
        for name in ("AGENTS.md", "SKILL.md", "CLAUDE.md", ".env", "auth.json"):
            file = self.root / name; file.write_text("test")
            with self.assertRaises(ValueError): search.input_file(file)

    def test_size_cap(self):
        file = self.root / "large.md"; file.write_bytes(b"x" * 6)
        with patch.object(search, "MAX_BYTES", 5):
            with self.assertRaises(ValueError): search.input_file(file)

    def test_cache_repeat_crlf_refresh_and_no_execution_routes(self):
        runtime = self.runtime()
        file = self.root / "doc.md"; original = b"\xef\xbb\xbf# Header\r\n\r\nValue\r\n"
        file.write_bytes(original)
        calls = []
        def run(command, **kwargs):
            calls.append(command)
            self.assertIn(command[2], ("index", "search"))
            self.assertNotIn("shell", kwargs)
            if command[2] == "index":
                snap = Path(command[3]); self.assertNotIn(b"\r", snap.read_bytes())
                db = Path(kwargs["env"]["CONTEXT_MODE_DIR"]) / "content/a.db"
                db.parent.mkdir(parents=True); db.write_text("synthetic")
            return subprocess.CompletedProcess(command, 0, "result", "")
        with patch.object(search.subprocess, "run", side_effect=run):
            first = search.search(file, ["value"], runtime, self.root / "cache")
            again = search.search(file, ["value"], runtime, self.root / "cache")
            self.assertEqual(file.read_bytes(), original)
            file.write_bytes(b"# Header\nNew value\n")
            new = search.search(file, ["value"], runtime, self.root / "cache")
        self.assertFalse(first["cache_reused"])
        self.assertTrue(again["cache_reused"])
        self.assertFalse(new["cache_reused"])
        self.assertEqual(sum(c[2] == "index" for c in calls), 2)
        self.assertNotEqual(first["sha256"], new["sha256"])

    def test_failure_is_not_cached_or_reported_success(self):
        runtime = self.runtime(); file = self.root / "doc.md"; file.write_text("# Header\nValue")
        with patch.object(search.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "failure")):
            with self.assertRaises(RuntimeError): search.search(file, ["value"], runtime, self.root / "cache")
        self.assertFalse(list((self.root / "cache").rglob("indexed.json")))
        self.assertFalse(list((self.root / "cache").rglob("busy.lock")))
        with self.assertRaisesRegex(ValueError, "미완료"):
            search.search(file, ["value"], runtime, self.root / "cache")

    def test_new_runtime_only_has_reviewed_files(self):
        # The installer does not execute npm lifecycle scripts, hooks, or setup.
        self.assertEqual(set(setup.FILES), {"cli.bundle.mjs", "package.json", "LICENSE"})
        with patch.object(setup.subprocess, "run") as run:
            setup.probe_node("node")
        self.assertIn("fts5", run.call_args.args[0][2])

    def test_ranked_heading_maps_to_original_lines_and_ignores_fences(self):
        text = "# Manual\r\n## Policy\r\nrule\r\n```md\r\n## Fake\r\n```\r\n## Other\r\nend\r\n"
        value = search.section_ranges(text, "## 1. Manual > Policy\nSource: document\n")
        self.assertEqual(value, [{"title": "Manual > Policy", "start_line": 2, "end_line": 6}])
        self.assertEqual(search.section_ranges(text, "## 1. Manual > Fake\n"), [])


if __name__ == "__main__": unittest.main()
