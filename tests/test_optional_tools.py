import base64
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
spec = importlib.util.spec_from_file_location("kit_setup", REPO / "scripts/setup-tools.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
spec2 = importlib.util.spec_from_file_location("walkthrough", REPO / "skills/minwoo-diff-walkthrough/scripts/render_walkthrough.py")
walk = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(walk)
PATCH = "diff --git a/a.txt b/a.txt\nindex 7898192..6178079 100644\n--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n-a\n+b\n"


class ToolSetupTests(unittest.TestCase):
    def test_dry_run_does_not_create_destination(self):
        with tempfile.TemporaryDirectory() as parent:
            target = Path(parent) / "absent"
            with (
                patch.object(sys, "argv", ["setup-tools.py", "--runtime-root", str(target), "--dry-run"]),
                patch.object(setup.shutil, "which", return_value="node"),
                patch.object(setup.subprocess, "check_output", return_value="v24.22.1"),
            ):
                if sys.version_info < (3, 11):
                    with self.assertRaises(SystemExit) as exc:
                        setup.main()
                    self.assertEqual(exc.exception.code, 2)
                else:
                    setup.main()
            self.assertFalse(target.exists())

    def test_repeat_keeps_files_and_modification_is_rejected(self):
        with tempfile.TemporaryDirectory() as parent:
            dest=Path(parent)
            hashes=setup.file_hashes({"package.json":b"{}"})
            file=dest/"package.json"
            file.write_bytes(b"{}")
            (dest/"installed.json").write_text(json.dumps({"files":hashes}),encoding="utf-8")
            before=file.stat().st_mtime_ns
            setup.verify_existing(dest,hashes)
            self.assertEqual(before,file.stat().st_mtime_ns)
            file.write_bytes(b"changed")
            with self.assertRaises(setup.InstallError):
                setup.verify_existing(dest,hashes)

    def test_unmanaged_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as parent:
            with self.assertRaises(setup.InstallError):
                setup.verify_existing(Path(parent),{})

    def test_download_integrity_failure_writes_nothing(self):
        with tempfile.TemporaryDirectory() as parent:
            target=Path(parent)/"npm"
            with self.assertRaises(setup.InstallError):
                setup.extract_npm(b"invalid",target)
            self.assertFalse(target.exists())

    def test_archive_paths_and_links_are_rejected_before_extracting(self):
        for name, kind in [("package/../../escape",tarfile.REGTYPE),("package/link",tarfile.SYMTYPE)]:
            stream=io.BytesIO()
            with tarfile.open(fileobj=stream,mode="w:gz") as archive:
                member=tarfile.TarInfo(name); member.type=kind; member.linkname="../../escape"
                archive.addfile(member)
            blob=stream.getvalue()
            with (
                tempfile.TemporaryDirectory() as parent,
                patch.object(setup,"NPM_SHA512",base64.b64encode(hashlib.sha512(blob).digest()).decode()),
            ):
                target=Path(parent)/"npm"
                with self.assertRaises(setup.InstallError):
                    setup.extract_npm(blob,target)
                self.assertFalse(target.exists())


class WalkthroughTests(unittest.TestCase):
    def data(self):
        return {"title":"작은 변경", "steps":[{"message":"값 변경","files":["a.txt"],"diff":PATCH}],
                "explanations":["<p>내용</p>"],"reviews":[[]],"pr_meta":None}

    def test_original_patch_renders_and_script_text_is_escaped(self):
        data=self.data(); data["explanations"]=["</script><script>window.bad=1</script>"]
        html=walk.render(data,PATCH)
        self.assertIn("작은 변경",html)
        self.assertNotIn("</script><script>window.bad",html)
        self.assertIn("\\u003c",html)

    def test_fabricated_diff_is_rejected(self):
        data=self.data(); data["steps"][0]["diff"]=PATCH.replace("+b","+fabricated")
        with self.assertRaises(ValueError):
            walk.render(data,PATCH)

    def test_nonexistent_line_is_rejected(self):
        data=self.data()
        data["reviews"]=[[{"severity":"low","title":"확인","body":"설명","file":"a.txt","line":99,"side":"RIGHT"}]]
        with self.assertRaises(ValueError):
            walk.render(data,PATCH)


if __name__ == "__main__":
    unittest.main()
