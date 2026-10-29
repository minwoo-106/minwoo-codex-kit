"""kit 파일 비교의 분류와 읽기 전용 동작을 검증한다."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


kit = module("inspect_kit", "skills/minwoo-kit-maintenance/scripts/inspect_kit.py")


class FilesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("KIT_TEST_ROOT"))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, path, data=b"example"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path


class InspectTests(FilesTest):
    def test_classifies_files_and_duplicates_without_writing(self):
        source, home, a, b = [self.root / n for n in ("kit", "home", "a", "b")]
        self.put(source / "global/AGENTS.md", b"new")
        self.put(home / "AGENTS.md", b"local change")
        self.put(home / "AGENTS.override.md", b"override")
        self.put(source / "skills/example/SKILL.md", b"same")
        self.put(source / "skills/example/scripts/tool.py", b"new tool")
        self.put(source / "skills/example/references/doc.md", b"missing")
        self.put(a / "example/SKILL.md", b"same")
        self.put(a / "example/scripts/tool.py", b"local tool")
        self.put(a / "example/retired.md", b"keep")
        self.put(b / "example/SKILL.md", b"other")
        self.put(a / "installation-note.txt", b"unrelated file")
        def snapshot():
            return {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}
        before = snapshot()
        result = kit.inspect(source, home, [a, b])
        self.assertEqual(before, snapshot())
        self.assertEqual(result["rules"]["status"], "different")
        self.assertTrue(result["rules"]["override_present"])
        first = result["skills"][0]
        self.assertEqual(first["same"], ["SKILL.md"])
        self.assertEqual(first["different"], ["scripts/tool.py"])
        self.assertEqual(first["missing"], ["references/doc.md"])
        self.assertEqual(first["extra"], ["retired.md"])
        self.assertEqual(len(result["duplicates"]["example"]), 2)

    def test_missing_installations_are_not_created(self):
        source = self.root / "kit"
        self.put(source / "global/AGENTS.md")
        self.put(source / "skills/example/SKILL.md")
        result = kit.inspect(source, self.root / "home", [self.root / "skills"])
        self.assertEqual(result["rules"]["status"], "absent")
        self.assertFalse(result["skills"][0]["installed"])
        self.assertFalse((self.root / "home").exists())
        self.assertFalse((self.root / "skills").exists())

    def test_invalid_kit_fails(self):
        with self.assertRaises(ValueError):
            kit.inspect(self.root, self.root / "home", [])



if __name__ == "__main__":
    unittest.main()
