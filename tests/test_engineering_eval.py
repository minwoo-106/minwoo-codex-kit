"""Adding regression coverage is allowed; weakening existing tests must fail."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('engineering_fixtures',Path(__file__).resolve().parents[1]/'evals/engineering_fixtures.py')
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)


class PreservationTests(unittest.TestCase):
    def setUp(self):self.original=fixtures.SOURCES['flaky']['test_app.py']
    def check(self,after):return fixtures.original_tests_preserved(self.original,after)
    def test_added_regression_allowed(self):
        self.assertTrue(self.check(self.original+'\n    def test_extra(self): self.assertEqual(1,1)\n'))
    def test_assertion_change_rejected(self):
        self.assertFalse(self.check(self.original.replace('assertEqual','assertNotEqual')))
    def test_deleted_test_rejected(self):
        self.assertFalse(self.check(self.original.replace('    def test_b(self): self.assertEqual(add_item("b"),["b"])\n','')))
    def test_renamed_test_rejected(self):
        self.assertFalse(self.check(self.original.replace('test_b','renamed_b')))
    def test_skip_decorator_rejected(self):
        self.assertFalse(self.check(self.original.replace('    def test_b','    @unittest.skip("skip")\n    def test_b')))
    def test_class_skip_rejected(self):
        self.assertFalse(self.check(self.original.replace('class Tests','@unittest.skip("skip")\nclass Tests')))
    def test_duplicate_override_rejected(self):
        self.assertFalse(self.check(self.original+'\n    def test_b(self): pass\n'))
    def test_base_class_change_rejected(self):
        self.assertFalse(self.check(self.original.replace('unittest.TestCase','object')))


if __name__=='__main__':unittest.main()
